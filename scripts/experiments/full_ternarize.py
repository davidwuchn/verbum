#!/usr/bin/env python3
"""Full-model ternarization of Qwen3-8B.

Ternarizes ALL weight matrices across ALL layers using the complete recipe
proven in sessions 170-182:

  1. SIGN:   T(i,j) = sign(W(i,j))         — from teacher weights (100% accurate)
  2. ZERO:   T(i,j) = 0 where |W(i,j)| < percentile(|W(i,:)|, zero_rate)
             Per-row magnitude threshold     — cosine 0.94 at 48% zeros
  3. SCALE:  γ(i) = (w_i · t_i) / (t_i · t_i)   — optimal per-row scalar

Strategy: Monkey-patch. Load float16 model, replace each nn.Linear with a
TernaryLinear that stores T as int8 + γ as float32. Free float weights after
each layer to keep memory bounded.

Then: measure perplexity on WikiText-2 and generate text for quality check.

Usage:
  uv run python scripts/experiments/full_ternarize.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/full_ternarize.py --model Qwen/Qwen3-8B --zero-rate 0.35
  uv run python scripts/experiments/full_ternarize.py --model Qwen/Qwen3-8B --eval-only  # skip ternarization, just baseline

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import sys
import time
from pathlib import Path

# Force unbuffered stdout so output appears immediately through pipes
os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def log(msg: str = "") -> None:
    """Print with immediate flush."""
    print(msg, flush=True)

# ═══════════════════════════════════════════════════════════════════════
# TernaryLinear — drop-in replacement for nn.Linear
# ═══════════════════════════════════════════════════════════════════════

class TernaryLinear(nn.Module):
    """Linear layer with ternary weights {-1, 0, +1} and per-row scale.

    Stores:
      T: int8 tensor (out_features, in_features) ∈ {-1, 0, +1}
      gamma: float32 tensor (out_features,) — per-row scale factor
      bias: float32 tensor (out_features,) or None

    Forward: y = (γ ⊙ (T @ x))  [with optional bias]

    The int8 matmul is computed as: cast T to input dtype, matmul, then scale.
    On MPS/CUDA, the cast is cheap and the matmul dominates.
    """

    def __init__(self, T: torch.Tensor, gamma: torch.Tensor,
                 bias: torch.Tensor | None = None):
        super().__init__()
        # Store T as int8 (saves 2× vs float16)
        self.register_buffer('T', T.to(torch.int8))
        self.register_buffer('gamma', gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer('bias', bias.to(torch.float32))
        else:
            self.bias = None

        self.out_features = T.shape[0]
        self.in_features = T.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Cast T to input device and dtype for matmul
        T_cast = self.T.to(device=x.device, dtype=x.dtype)
        # Matmul: (..., in_features) @ (out_features, in_features).T → (..., out_features)
        out = F.linear(x, T_cast)
        # Per-row scale
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        out = out * gamma
        # Bias
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out

    def extra_repr(self) -> str:
        zeros = (self.T == 0).sum().item()
        total = self.T.numel()
        return (f"in_features={self.in_features}, out_features={self.out_features}, "
                f"zeros={zeros}/{total} ({zeros/total*100:.1f}%), "
                f"bias={self.bias is not None}")


# ═══════════════════════════════════════════════════════════════════════
# Ternarization logic
# ═══════════════════════════════════════════════════════════════════════

def ternarize_weight(W: torch.Tensor, zero_rate: float = 0.35) -> tuple[torch.Tensor, torch.Tensor]:
    """Ternarize a weight matrix using the proven recipe.

    Args:
        W: float weight matrix (out_features, in_features)
        zero_rate: fraction of smallest-magnitude weights per row to zero

    Returns:
        T: int8 ternary matrix {-1, 0, +1}
        gamma: float32 per-row scale factors
    """
    W_float = W.detach().float().cpu()
    out_f, in_f = W_float.shape

    # Per-row magnitude threshold
    abs_W = W_float.abs()

    if zero_rate > 0:
        # Compute per-row threshold using quantile
        # quantile along dim=1 for each row
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)  # (out_f, 1)
        alive_mask = abs_W >= thresholds  # True where weight survives
    else:
        alive_mask = torch.ones_like(W_float, dtype=torch.bool)

    # Signs where alive, 0 where dead
    T = torch.where(alive_mask, torch.sign(W_float), torch.zeros_like(W_float))

    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
    wt = (W_float * T).sum(dim=1)      # (out_f,)
    tt = (T * T).sum(dim=1)             # (out_f,) — equals count of nonzeros per row
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))

    return T.to(torch.int8), gamma


def ternarize_linear(linear: nn.Linear, zero_rate: float = 0.35) -> TernaryLinear:
    """Convert an nn.Linear to TernaryLinear."""
    W = linear.weight
    bias = linear.bias

    T, gamma = ternarize_weight(W, zero_rate)

    # Compute reconstruction quality before we lose the weights
    W_float = W.detach().float().cpu()
    W_recon = gamma.unsqueeze(1) * T.float()
    cos = F.cosine_similarity(W_float.reshape(1, -1), W_recon.reshape(1, -1)).item()

    bias_tensor = bias.detach().float().cpu() if bias is not None else None
    tl = TernaryLinear(T, gamma, bias_tensor)

    return tl, cos


# ═══════════════════════════════════════════════════════════════════════
# Model surgery — monkey-patch all Linear layers
# ═══════════════════════════════════════════════════════════════════════

def get_model_layers(model):
    """Extract the transformer layers container."""
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise RuntimeError("Cannot find layers — add support for this architecture")


WEIGHT_NAMES_FFN = ['gate_proj', 'up_proj', 'down_proj']
WEIGHT_NAMES_ATTN = ['q_proj', 'k_proj', 'v_proj', 'o_proj']


def ternarize_layer(layer: nn.Module, zero_rate: float, layer_idx: int,
                    n_layers: int, device: str = "cpu") -> dict:
    """Ternarize all weight matrices in a single transformer layer."""
    stats = {'layer': layer_idx, 'depth': layer_idx / n_layers}

    # FFN weights
    for name in WEIGHT_NAMES_FFN:
        proj = getattr(layer.mlp, name, None)
        if proj is None:
            continue
        tl, cos = ternarize_linear(proj, zero_rate)
        tl = tl.to(device)  # Move buffers to model device
        setattr(layer.mlp, name, tl)
        zeros = (tl.T == 0).sum().item()
        total = tl.T.numel()
        stats[name] = {
            'cosine': cos,
            'zeros': zeros,
            'total': total,
            'zero_pct': zeros / total * 100,
            'shape': list(tl.T.shape),
        }
        del proj
        gc.collect()

    # Attention weights
    for name in WEIGHT_NAMES_ATTN:
        proj = getattr(layer.self_attn, name, None)
        if proj is None:
            continue
        tl, cos = ternarize_linear(proj, zero_rate)
        tl = tl.to(device)  # Move buffers to model device
        setattr(layer.self_attn, name, tl)
        zeros = (tl.T == 0).sum().item()
        total = tl.T.numel()
        stats[name] = {
            'cosine': cos,
            'zeros': zeros,
            'total': total,
            'zero_pct': zeros / total * 100,
            'shape': list(tl.T.shape),
        }
        del proj
        gc.collect()

    return stats


def ternarize_model(model, zero_rate: float = 0.35, device: str = "cpu") -> list[dict]:
    """Ternarize all layers of the model in-place."""
    layers = get_model_layers(model)
    n_layers = len(layers)
    all_stats = []

    log(f"\n{'═' * 78}")
    log(f"  TERNARIZING {n_layers} LAYERS  (zero_rate={zero_rate:.0%})")
    log(f"{'═' * 78}")
    log(f"  {'Layer':>5}  {'gate cos':>9} {'up cos':>9} {'down cos':>9} "
          f"{'q cos':>9} {'k cos':>9} {'v cos':>9} {'o cos':>9}")
    log(f"  {'─' * 5}  {'─' * 9} {'─' * 9} {'─' * 9} "
          f"{'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")

    t0 = time.time()
    for i, layer in enumerate(layers):
        t_layer = time.time()
        stats = ternarize_layer(layer, zero_rate, i, n_layers, device=device)
        all_stats.append(stats)

        # Print per-layer cosines
        cosines = []
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in stats:
                cosines.append(f"{stats[name]['cosine']:>9.5f}")
            else:
                cosines.append(f"{'N/A':>9}")
        log(f"  {i:>5}  {' '.join(cosines)}  ({time.time() - t_layer:.1f}s)")

        # Force GC every layer
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    elapsed = time.time() - t0

    # Summary
    total_zeros = 0
    total_params = 0
    cos_by_type = {n: [] for n in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN}
    for s in all_stats:
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in s:
                total_zeros += s[name]['zeros']
                total_params += s[name]['total']
                cos_by_type[name].append(s[name]['cosine'])

    log(f"\n  {'─' * 78}")
    log(f"  Total ternarized: {total_params:,} params in {elapsed:.1f}s")
    log(f"  Overall zeros: {total_zeros:,} / {total_params:,} ({total_zeros / total_params * 100:.1f}%)")
    log(f"\n  Mean cosine by weight type:")
    for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
        if cos_by_type[name]:
            vals = cos_by_type[name]
            log(f"    {name:<12} mean={np.mean(vals):.5f}  min={np.min(vals):.5f}  max={np.max(vals):.5f}")

    # Size estimate
    # Ternary weights: 1.58 bits/param (log2(3))
    ternary_bits = total_params * math.log2(3)
    ternary_bytes = ternary_bits / 8
    # Per-row gamma: float32 per output row
    total_rows = sum(s[n]['shape'][0] for s in all_stats for n in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN if n in s)
    gamma_bytes = total_rows * 4  # float32

    log(f"\n  Size estimate:")
    log(f"    Ternary weights: {ternary_bytes / 1e9:.3f} GB ({total_params * 1.58:.0f} Mbits)")
    log(f"    Gamma scalars:   {gamma_bytes / 1e6:.2f} MB ({total_rows:,} rows × 4 bytes)")
    log(f"    Original fp16:   {total_params * 2 / 1e9:.3f} GB")
    log(f"    Compression:     {total_params * 2 / (ternary_bytes + gamma_bytes):.1f}×")

    return all_stats


# ═══════════════════════════════════════════════════════════════════════
# Perplexity evaluation
# ═══════════════════════════════════════════════════════════════════════

def load_eval_texts(max_tokens: int = 32768) -> list[str]:
    """Load evaluation texts. Try WikiText-2, fall back to built-in corpus."""
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        # Concatenate non-empty lines
        texts = [t for t in ds["text"] if t.strip()]
        log(f"  Loaded WikiText-2 test: {len(texts)} lines")
        return texts
    except Exception as e:
        log(f"  WikiText-2 unavailable ({e}), using built-in corpus")
        return [
            "The speed of light in vacuum is 299792458 meters per second. "
            "This fundamental constant of nature was first measured with reasonable accuracy by "
            "Ole Rømer in 1676 through observations of the moons of Jupiter. "
            "The modern value was established by the 17th General Conference on Weights and Measures in 1983, "
            "which redefined the metre in terms of the speed of light.",

            "In computer science, a hash table is a data structure that implements an associative array, "
            "also called a dictionary. A hash table uses a hash function to compute an index into an array "
            "of buckets or slots, from which the desired value can be found. During lookup, the key is hashed "
            "and the resulting hash indicates where the corresponding value is stored.",

            "The Amazon rainforest, also known as Amazonia, is a moist broadleaf tropical rainforest in the "
            "Amazon biome that covers most of the Amazon basin of South America. This basin encompasses "
            "7,000,000 square kilometres of which 5,500,000 square kilometres are covered by the rainforest. "
            "This region includes territory belonging to nine nations and 3,344 formally acknowledged "
            "indigenous territories.",

            "Machine learning is a subset of artificial intelligence that provides systems the ability to "
            "automatically learn and improve from experience without being explicitly programmed. "
            "Machine learning focuses on the development of computer programs that can access data and "
            "use it to learn for themselves. The process begins with observations or data, such as examples, "
            "direct experience, or instruction, in order to look for patterns in data.",

            "Lambda calculus is a formal system in mathematical logic for expressing computation based on "
            "function abstraction and application using variable binding and substitution. It is a universal "
            "model of computation that can be used to simulate any Turing machine. It was introduced by the "
            "mathematician Alonzo Church in the 1930s as part of his research into the foundations of mathematics.",
        ]


@torch.no_grad()
def evaluate_perplexity(model, tokenizer, texts: list[str],
                        max_length: int = 512, stride: int = 256,
                        max_eval_tokens: int = 16384,
                        device: str = "mps") -> dict:
    """Evaluate perplexity using sliding window.

    Uses stride < max_length to avoid boundary effects. Only scores
    tokens in the non-overlapping region.
    """
    log(f"\n  Evaluating perplexity (max_length={max_length}, stride={stride})...")
    t0 = time.time()

    # Concatenate all texts and tokenize
    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = input_ids.size(0)

    # Cap tokens for faster eval
    if max_eval_tokens > 0 and seq_len > max_eval_tokens:
        log(f"  Total tokens: {seq_len:,} → capped to {max_eval_tokens:,}")
        input_ids = input_ids[:max_eval_tokens]
        seq_len = max_eval_tokens
    else:
        log(f"  Total tokens: {seq_len:,}")

    n_windows = (seq_len - 1 + stride - 1) // stride
    log(f"  Windows: ~{n_windows}")

    nlls = []
    n_tokens = 0
    window_count = 0

    for begin_loc in range(0, seq_len - 1, stride):
        end_loc = min(begin_loc + max_length, seq_len)

        # Only score the non-overlapping part (except for the first window)
        if begin_loc > 0:
            score_begin = stride  # score only the new tokens
        else:
            score_begin = 0

        input_chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)

        outputs = model(input_chunk)
        logits = outputs.logits  # (1, seq_len, vocab)

        # Shift: predict token[i+1] from logits[i]
        shift_logits = logits[0, score_begin:-1, :].contiguous()
        shift_labels = input_chunk[0, score_begin + 1:].contiguous()

        loss = F.cross_entropy(shift_logits, shift_labels, reduction='sum')
        count = shift_labels.size(0)

        nlls.append(loss.float().cpu().item())
        n_tokens += count
        window_count += 1

        # Progress every 10 windows
        if window_count % 10 == 0:
            elapsed_so_far = time.time() - t0
            ppl_so_far = math.exp(sum(nlls) / n_tokens)
            remaining = (n_windows - window_count) * (elapsed_so_far / window_count)
            log(f"    [{window_count}/{n_windows}] {n_tokens:,} tokens, "
                f"PPL={ppl_so_far:.2f}, {elapsed_so_far:.0f}s elapsed, ~{remaining:.0f}s remaining")

        if end_loc >= seq_len:
            break

    mean_nll = sum(nlls) / n_tokens
    ppl = math.exp(mean_nll)
    elapsed = time.time() - t0

    log(f"  Scored {n_tokens:,} tokens in {elapsed:.1f}s")
    log(f"  NLL: {mean_nll:.4f}")
    log(f"  Perplexity: {ppl:.2f}")

    return {'perplexity': ppl, 'nll': mean_nll, 'n_tokens': n_tokens, 'elapsed': elapsed}


# ═══════════════════════════════════════════════════════════════════════
# Generation test
# ═══════════════════════════════════════════════════════════════════════

GENERATION_PROMPTS = [
    # Factual
    "The capital of France is",
    "The speed of light is approximately",
    "Water is composed of two elements:",
    # Reasoning
    "If all dogs are animals and all animals are living things, then all dogs are",
    "The next number in the sequence 2, 4, 8, 16, 32 is",
    # Code
    "def fibonacci(n):\n    \"\"\"Return the nth Fibonacci number.\"\"\"\n",
    # Creative
    "Once upon a time, in a forest deep and dark, there lived a",
    # Lambda / technical
    "In lambda calculus, the identity combinator I is defined as",
]


@torch.no_grad()
def test_generation(model, tokenizer, prompts: list[str],
                    max_new_tokens: int = 64, device: str = "mps",
                    temperature: float = 0.0) -> list[dict]:
    """Generate text from prompts and return results."""
    results = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        t0 = time.time()
        if temperature == 0:
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        else:
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )
        elapsed = time.time() - t0

        generated = tokenizer.decode(output[0], skip_special_tokens=True)
        new_tokens = output.shape[1] - inputs['input_ids'].shape[1]

        results.append({
            'prompt': prompt,
            'generated': generated,
            'new_tokens': new_tokens,
            'tok_per_sec': new_tokens / elapsed if elapsed > 0 else 0,
            'elapsed': elapsed,
        })

    return results


def print_generations(results: list[dict], label: str = ""):
    """Pretty-print generation results."""
    log(f"\n{'═' * 78}")
    log(f"  GENERATION RESULTS{f' — {label}' if label else ''}")
    log(f"{'═' * 78}")
    for i, r in enumerate(results):
        log(f"\n  ── Prompt {i + 1} ({r['new_tokens']} tokens, {r['tok_per_sec']:.1f} tok/s) ──")
        log(f"  {r['prompt']}")
        # Print only the generated part (after prompt)
        generated_only = r['generated'][len(r['prompt']):]
        # Indent continuation
        for line in generated_only.split('\n'):
            log(f"  ▸ {line}")


# ═══════════════════════════════════════════════════════════════════════
# Memory accounting
# ═══════════════════════════════════════════════════════════════════════

def memory_report(model) -> dict:
    """Report actual memory usage of the model."""
    total_bytes = 0
    ternary_params = 0
    float_params = 0
    int8_bytes = 0
    float_bytes = 0

    for name, param in model.named_parameters():
        total_bytes += param.nelement() * param.element_size()
        float_params += param.nelement()
        float_bytes += param.nelement() * param.element_size()

    for name, buf in model.named_buffers():
        total_bytes += buf.nelement() * buf.element_size()
        if buf.dtype == torch.int8:
            int8_bytes += buf.nelement() * buf.element_size()
            ternary_params += buf.nelement()
        else:
            float_bytes += buf.nelement() * buf.element_size()

    return {
        'total_bytes': total_bytes,
        'total_GB': total_bytes / 1e9,
        'int8_bytes': int8_bytes,
        'int8_GB': int8_bytes / 1e9,
        'float_bytes': float_bytes,
        'float_GB': float_bytes / 1e9,
        'ternary_params': ternary_params,
        'float_params': float_params,
    }


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Full-model ternarization")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--zero-rate", type=float, default=0.35,
                        help="Fraction of smallest-magnitude weights per row to zero (default: 0.35)")
    parser.add_argument("--max-length", type=int, default=512,
                        help="Max sequence length for perplexity eval")
    parser.add_argument("--stride", type=int, default=256,
                        help="Stride for sliding window perplexity")
    parser.add_argument("--skip-baseline", action="store_true",
                        help="Skip float16 baseline perplexity (faster)")
    parser.add_argument("--skip-perplexity", action="store_true",
                        help="Skip perplexity eval entirely")
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skip generation test")
    parser.add_argument("--max-eval-tokens", type=int, default=16384,
                        help="Max tokens for perplexity eval (default: 16384, 0=all)")
    parser.add_argument("--eval-only", action="store_true",
                        help="Only run float16 baseline, no ternarization")
    args = parser.parse_args()

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    log(f"\n{'═' * 78}")
    log(f"  FULL-MODEL TERNARIZATION")
    log(f"{'═' * 78}")
    log(f"  Model:     {args.model}")
    log(f"  Device:    {device}")
    log(f"  Zero rate: {args.zero_rate:.0%}")
    log(f"  Eval only: {args.eval_only}")

    # ── Load model ────────────────────────────────────────────────────
    log(f"\n  Loading model (float16)...")
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    load_time = time.time() - t0
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    d_ff = getattr(model.config, 'intermediate_size', d_model * 4)
    log(f"  Loaded in {load_time:.1f}s: {n_layers} layers, d={d_model}, d_ff={d_ff}")

    mem_before = memory_report(model)
    log(f"  Float16 memory: {mem_before['total_GB']:.2f} GB")

    # ── Float16 baseline ──────────────────────────────────────────────
    baseline_ppl = None
    baseline_gen = None
    eval_texts = None

    if not args.skip_perplexity:
        eval_texts = load_eval_texts()
        if not args.skip_baseline:
            log(f"\n{'═' * 78}")
            log(f"  FLOAT16 BASELINE PERPLEXITY")
            log(f"{'═' * 78}")
            baseline_ppl = evaluate_perplexity(
                model, tokenizer, eval_texts,
                max_length=args.max_length, stride=args.stride,
                max_eval_tokens=args.max_eval_tokens,
                device=device)

    if not args.skip_generation and not args.skip_baseline:
        log(f"\n  Generating baseline samples...")
        baseline_gen = test_generation(model, tokenizer, GENERATION_PROMPTS,
                                       device=device)
        print_generations(baseline_gen, "FLOAT16 BASELINE")

    if args.eval_only:
        log(f"\n  eval-only mode, stopping before ternarization.")
        return

    # ── Ternarize ─────────────────────────────────────────────────────
    all_stats = ternarize_model(model, zero_rate=args.zero_rate, device=device)

    # Memory after
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    mem_after = memory_report(model)
    log(f"\n  Memory after ternarization:")
    log(f"    Total:        {mem_after['total_GB']:.2f} GB")
    log(f"    Int8 (T):     {mem_after['int8_GB']:.2f} GB")
    log(f"    Float (rest): {mem_after['float_GB']:.2f} GB")
    log(f"    Reduction:    {mem_before['total_GB'] / mem_after['total_GB']:.2f}×")

    # ── Ternary perplexity ────────────────────────────────────────────
    ternary_ppl = None
    if not args.skip_perplexity:
        log(f"\n{'═' * 78}")
        log(f"  TERNARY PERPLEXITY")
        log(f"{'═' * 78}")
        if eval_texts is None:
            eval_texts = load_eval_texts()
        ternary_ppl = evaluate_perplexity(
            model, tokenizer, eval_texts,
            max_length=args.max_length, stride=args.stride,
            max_eval_tokens=args.max_eval_tokens,
            device=device)

        if baseline_ppl:
            ratio = ternary_ppl['perplexity'] / baseline_ppl['perplexity']
            log(f"\n  COMPARISON:")
            log(f"    Float16 PPL:  {baseline_ppl['perplexity']:.2f}")
            log(f"    Ternary PPL:  {ternary_ppl['perplexity']:.2f}")
            log(f"    Ratio:        {ratio:.2f}×")
            log(f"    NLL increase: {ternary_ppl['nll'] - baseline_ppl['nll']:.4f}")

    # ── Ternary generation ────────────────────────────────────────────
    ternary_gen = None
    if not args.skip_generation:
        log(f"\n  Generating ternary samples...")
        ternary_gen = test_generation(model, tokenizer, GENERATION_PROMPTS,
                                      device=device)
        print_generations(ternary_gen, "TERNARY")

        # Side-by-side comparison
        if baseline_gen:
            log(f"\n{'═' * 78}")
            log(f"  SIDE-BY-SIDE COMPARISON")
            log(f"{'═' * 78}")
            for i, (b, t) in enumerate(zip(baseline_gen, ternary_gen)):
                log(f"\n  ── Prompt {i + 1}: {b['prompt'][:60]}...")
                b_text = b['generated'][len(b['prompt']):][:200]
                t_text = t['generated'][len(t['prompt']):][:200]
                log(f"  F16: {b_text}")
                log(f"  T3:  {t_text}")

    # ── Final report ──────────────────────────────────────────────────
    log(f"\n{'═' * 78}")
    log(f"  FINAL REPORT")
    log(f"{'═' * 78}")
    log(f"  Model:           {args.model}")
    log(f"  Layers:          {n_layers}")
    log(f"  Zero rate:       {args.zero_rate:.0%}")
    log(f"  Float16 size:    {mem_before['total_GB']:.2f} GB")
    log(f"  Ternary size:    {mem_after['total_GB']:.2f} GB (in-memory, int8+float32)")
    log(f"  Compression:     {mem_before['total_GB'] / mem_after['total_GB']:.2f}× (int8)")
    if baseline_ppl and ternary_ppl:
        log(f"  Float16 PPL:     {baseline_ppl['perplexity']:.2f}")
        log(f"  Ternary PPL:     {ternary_ppl['perplexity']:.2f}")
        log(f"  PPL ratio:       {ternary_ppl['perplexity'] / baseline_ppl['perplexity']:.2f}×")
    log(f"{'═' * 78}\n")


if __name__ == "__main__":
    main()
