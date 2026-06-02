#!/usr/bin/env python3
"""Multi-mirror ternarization — 2-mirror (4 bits) and 3-mirror (6 bits).

Decomposes each weight matrix into N ternary "mirrors" plus per-row scales:

  W ≈ γ₁·T₁ + γ₂·T₂ + ... + γₙ·Tₙ

where each Tᵢ ∈ {-1, 0, +1} and γᵢ is a per-row scalar.

Mirror decomposition (greedy):
  Mirror 1: T₁ = sign(W),              γ₁ = (W·T₁) / (T₁·T₁)
  Residual: R₁ = W - γ₁·T₁
  Mirror 2: T₂ = sign(R₁),             γ₂ = (R₁·T₂) / (T₂·T₂)
  Residual: R₂ = R₁ - γ₂·T₂
  Mirror 3: T₃ = sign(R₂),             γ₃ = (R₂·T₃) / (T₃·T₃)

Forward: y = Σᵢ γᵢ · (Tᵢ @ x)   — N ternary matmuls, no float materialization

Bit counts (2 bits storage per trit):
  2-mirror: 4 bits/param → predicted 0.97 cosine/layer
  3-mirror: 6 bits/param → predicted 0.99 cosine/layer

Usage:
  uv run python scripts/experiments/mirror_ternarize.py --mirrors 3
  uv run python scripts/experiments/mirror_ternarize.py --mirrors 2 --zero-rate 0.3

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

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# Multi-Mirror TernaryLinear
# ═══════════════════════════════════════════════════════════════════════

class MultiMirrorLinear(nn.Module):
    """Linear layer with N ternary mirrors and per-row scales.

    Stores:
      mirrors: list of int8 tensors (out_features, in_features) ∈ {-1, 0, +1}
      gammas: list of float32 tensors (out_features,) — per-row scale per mirror
      bias: float32 tensor (out_features,) or None

    Forward: y = Σᵢ (γᵢ ⊙ (Tᵢ @ x)) + bias
    """

    def __init__(self, mirrors: list[torch.Tensor], gammas: list[torch.Tensor],
                 bias: torch.Tensor | None = None):
        super().__init__()
        self.n_mirrors = len(mirrors)
        for i, (T, g) in enumerate(zip(mirrors, gammas)):
            self.register_buffer(f'T{i}', T.to(torch.int8))
            self.register_buffer(f'gamma{i}', g.to(torch.float32))
        if bias is not None:
            self.register_buffer('bias', bias.to(torch.float32))
        else:
            self.bias = None

        self.out_features = mirrors[0].shape[0]
        self.in_features = mirrors[0].shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.zeros(*x.shape[:-1], self.out_features,
                          device=x.device, dtype=x.dtype)

        for i in range(self.n_mirrors):
            T = getattr(self, f'T{i}').to(device=x.device, dtype=x.dtype)
            gamma = getattr(self, f'gamma{i}').to(device=x.device, dtype=x.dtype)
            out = out + F.linear(x, T) * gamma

        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out

    def extra_repr(self) -> str:
        T0 = getattr(self, 'T0')
        zeros = (T0 == 0).sum().item()
        total = T0.numel()
        return (f"in={self.in_features}, out={self.out_features}, "
                f"mirrors={self.n_mirrors}, "
                f"m0_zeros={zeros}/{total} ({zeros/total*100:.1f}%)")


# ═══════════════════════════════════════════════════════════════════════
# Multi-mirror decomposition
# ═══════════════════════════════════════════════════════════════════════

def decompose_multimirror(W: torch.Tensor, n_mirrors: int = 2,
                          zero_rate: float = 0.0) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
    """Decompose weight matrix into N ternary mirrors.

    Phase 1 (greedy): Extract ternary sign patterns from successive residuals.
    Phase 2 (joint): Solve for optimal gammas jointly via least-squares.

    The greedy approach assigns sign patterns correctly but computes
    gammas independently, systematically underestimating total energy.
    Joint optimization fixes this: given fixed T₁..Tₙ, find γ₁..γₙ
    that minimize ||W - Σᵢ γᵢ·Tᵢ||² per row.

    Returns:
        mirrors: list of int8 ternary matrices
        gammas: list of float32 per-row scale vectors
    """
    W_float = W.detach().float().cpu()
    out_f, in_f = W_float.shape
    mirrors_raw = []
    residual = W_float.clone()

    # Phase 1: Greedy sign extraction (determines T patterns)
    for i in range(n_mirrors):
        abs_R = residual.abs()

        if zero_rate > 0:
            thresholds = torch.quantile(abs_R, zero_rate, dim=1, keepdim=True)
            alive = abs_R >= thresholds
        else:
            alive = torch.ones_like(residual, dtype=torch.bool)

        T = torch.where(alive, torch.sign(residual), torch.zeros_like(residual))
        mirrors_raw.append(T)

        # Greedy gamma for residual update only (will be replaced by joint solve)
        rt = (residual * T).sum(dim=1)
        tt = (T * T).sum(dim=1)
        gamma_greedy = torch.where(tt > 0, rt / tt, torch.zeros_like(rt))
        residual = residual - gamma_greedy.unsqueeze(1) * T

    # Phase 2: Joint gamma optimization (vectorized over all rows)
    # For each row i, solve: min_γ ||W_i - Σⱼ γⱼ · T_j_i||²
    # Normal equations: A·γ = b  where  A_jk = Σ T_j · T_k,  b_j = Σ W · T_j
    #
    # Stack mirrors: M has shape (n_mirrors, out_f, in_f)
    M = torch.stack([T.float() for T in mirrors_raw])  # (n_mirrors, out_f, in_f)

    # A[i,j,k] = (M[j,i,:] · M[k,i,:]) = dot product of mirror j and k at row i
    # Shape: (out_f, n_mirrors, n_mirrors)
    A = torch.einsum('jid,kid->ijk', M, M)  # (out_f, n_mirrors, n_mirrors)

    # b[i,j] = (W[i,:] · M[j,i,:])
    # Shape: (out_f, n_mirrors)
    b = torch.einsum('id,jid->ij', W_float, M)  # (out_f, n_mirrors)

    # Solve A @ gamma = b for each row (batched)
    # A: (out_f, n_mirrors, n_mirrors), b: (out_f, n_mirrors)
    try:
        gamma_opt = torch.linalg.solve(A, b)  # (out_f, n_mirrors)
    except Exception:
        gamma_opt = torch.linalg.lstsq(A, b.unsqueeze(-1)).solution.squeeze(-1)

    gammas = [gamma_opt[:, j] for j in range(n_mirrors)]
    mirrors = [T.to(torch.int8) for T in mirrors_raw]
    return mirrors, gammas


def mirror_ternarize_linear(linear: nn.Linear, n_mirrors: int = 2,
                            zero_rate: float = 0.0) -> tuple[MultiMirrorLinear, float]:
    """Convert nn.Linear to MultiMirrorLinear."""
    W = linear.weight
    bias = linear.bias

    mirrors, gammas = decompose_multimirror(W, n_mirrors, zero_rate)

    # Compute reconstruction quality
    W_float = W.detach().float().cpu()
    W_recon = torch.zeros_like(W_float)
    for T, g in zip(mirrors, gammas):
        W_recon = W_recon + g.unsqueeze(1) * T.float()
    cos = F.cosine_similarity(W_float.reshape(1, -1), W_recon.reshape(1, -1)).item()

    bias_tensor = bias.detach().float().cpu() if bias is not None else None
    ml = MultiMirrorLinear(mirrors, gammas, bias_tensor)

    return ml, cos


# ═══════════════════════════════════════════════════════════════════════
# Model surgery
# ═══════════════════════════════════════════════════════════════════════

WEIGHT_NAMES_FFN = ['gate_proj', 'up_proj', 'down_proj']
WEIGHT_NAMES_ATTN = ['q_proj', 'k_proj', 'v_proj', 'o_proj']


def get_model_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise RuntimeError("Cannot find layers")


def mirror_ternarize_model(model, n_mirrors: int = 2, zero_rate: float = 0.0,
                           device: str = "cpu") -> list[dict]:
    """Ternarize all layers with N mirrors."""
    layers = get_model_layers(model)
    n_layers = len(layers)
    all_stats = []

    log(f"\n{'═' * 78}")
    log(f"  {n_mirrors}-MIRROR TERNARIZATION ({n_mirrors * 2} bits/param, zero_rate={zero_rate:.0%})")
    log(f"{'═' * 78}")
    log(f"  {'Layer':>5}  {'gate':>8} {'up':>8} {'down':>8} "
        f"{'q':>8} {'k':>8} {'v':>8} {'o':>8}")
    log(f"  {'─' * 5}  {'─' * 8} {'─' * 8} {'─' * 8} "
        f"{'─' * 8} {'─' * 8} {'─' * 8} {'─' * 8}")

    t0 = time.time()
    for i, layer in enumerate(layers):
        stats = {'layer': i}
        t_layer = time.time()

        for name in WEIGHT_NAMES_FFN:
            proj = getattr(layer.mlp, name, None)
            if proj is None:
                continue
            ml, cos = mirror_ternarize_linear(proj, n_mirrors, zero_rate)
            ml = ml.to(device)
            setattr(layer.mlp, name, ml)
            stats[name] = cos
            del proj

        for name in WEIGHT_NAMES_ATTN:
            proj = getattr(layer.self_attn, name, None)
            if proj is None:
                continue
            ml, cos = mirror_ternarize_linear(proj, n_mirrors, zero_rate)
            ml = ml.to(device)
            setattr(layer.self_attn, name, ml)
            stats[name] = cos
            del proj

        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        all_stats.append(stats)

        cosines = []
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in stats:
                cosines.append(f"{stats[name]:>8.5f}")
            else:
                cosines.append(f"{'N/A':>8}")
        log(f"  {i:>5}  {' '.join(cosines)}  ({time.time() - t_layer:.1f}s)")

    elapsed = time.time() - t0

    # Summary
    cos_by_type = {n: [] for n in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN}
    for s in all_stats:
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in s:
                cos_by_type[name].append(s[name])

    log(f"\n  Completed in {elapsed:.1f}s")
    log(f"  Mean cosine by weight type:")
    for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
        if cos_by_type[name]:
            vals = cos_by_type[name]
            log(f"    {name:<12} mean={np.mean(vals):.5f}  min={np.min(vals):.5f}  max={np.max(vals):.5f}")

    return all_stats


# ═══════════════════════════════════════════════════════════════════════
# Perplexity + Generation (import from full_ternarize)
# ═══════════════════════════════════════════════════════════════════════

def load_eval_texts():
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        texts = [t for t in ds["text"] if t.strip()]
        log(f"  Loaded WikiText-2 test: {len(texts)} lines")
        return texts
    except Exception as e:
        log(f"  WikiText-2 unavailable ({e}), using built-in corpus")
        return [
            "The speed of light in vacuum is 299792458 meters per second.",
            "In computer science, a hash table is a data structure.",
            "Lambda calculus is a formal system for expressing computation.",
        ]


@torch.no_grad()
def evaluate_perplexity(model, tokenizer, texts, max_length=512, stride=256,
                        max_eval_tokens=16384, device="mps"):
    log(f"\n  Evaluating perplexity (max_length={max_length}, stride={stride})...")
    t0 = time.time()

    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = input_ids.size(0)

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
        score_begin = stride if begin_loc > 0 else 0
        input_chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)

        outputs = model(input_chunk)
        logits = outputs.logits

        shift_logits = logits[0, score_begin:-1, :].contiguous()
        shift_labels = input_chunk[0, score_begin + 1:].contiguous()

        loss = F.cross_entropy(shift_logits, shift_labels, reduction='sum')
        count = shift_labels.size(0)

        nlls.append(loss.float().cpu().item())
        n_tokens += count
        window_count += 1

        if window_count % 10 == 0:
            elapsed_so_far = time.time() - t0
            ppl_so_far = math.exp(sum(nlls) / n_tokens)
            remaining = (n_windows - window_count) * (elapsed_so_far / window_count)
            log(f"    [{window_count}/{n_windows}] {n_tokens:,} tok, "
                f"PPL={ppl_so_far:.2f}, {elapsed_so_far:.0f}s, ~{remaining:.0f}s rem")

        if end_loc >= seq_len:
            break

    mean_nll = sum(nlls) / n_tokens
    ppl = math.exp(min(mean_nll, 20))  # cap exp to avoid overflow
    elapsed = time.time() - t0

    log(f"  Scored {n_tokens:,} tokens in {elapsed:.1f}s")
    log(f"  NLL: {mean_nll:.4f}")
    log(f"  Perplexity: {ppl:.2f}")

    return {'perplexity': ppl, 'nll': mean_nll, 'n_tokens': n_tokens, 'elapsed': elapsed}


GENERATION_PROMPTS = [
    "The capital of France is",
    "The speed of light is approximately",
    "If all dogs are animals and all animals are living things, then all dogs are",
    "def fibonacci(n):\n    \"\"\"Return the nth Fibonacci number.\"\"\"\n",
    "Once upon a time, in a forest deep and dark, there lived a",
    "In lambda calculus, the identity combinator I is defined as",
]


@torch.no_grad()
def test_generation(model, tokenizer, prompts, max_new_tokens=64, device="mps"):
    results = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        t0 = time.time()
        output = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, pad_token_id=tokenizer.eos_token_id,
        )
        elapsed = time.time() - t0
        generated = tokenizer.decode(output[0], skip_special_tokens=True)
        new_tokens = output.shape[1] - inputs['input_ids'].shape[1]
        results.append({
            'prompt': prompt,
            'generated': generated,
            'new_tokens': new_tokens,
            'tok_per_sec': new_tokens / elapsed if elapsed > 0 else 0,
        })
    return results


def print_generations(results, label=""):
    log(f"\n{'═' * 78}")
    log(f"  GENERATION — {label}")
    log(f"{'═' * 78}")
    for i, r in enumerate(results):
        log(f"\n  ── Prompt {i+1} ({r['new_tokens']} tok, {r['tok_per_sec']:.1f} tok/s) ──")
        log(f"  {r['prompt']}")
        for line in r['generated'][len(r['prompt']):].split('\n'):
            log(f"  ▸ {line}")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Multi-mirror ternarization")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--mirrors", type=int, default=3,
                        help="Number of ternary mirrors (2=4bits, 3=6bits)")
    parser.add_argument("--zero-rate", type=float, default=0.0,
                        help="Per-row zero rate per mirror (default: 0 = pure sign)")
    parser.add_argument("--max-eval-tokens", type=int, default=16384)
    parser.add_argument("--skip-generation", action="store_true")
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

    bits = args.mirrors * 2
    log(f"\n{'═' * 78}")
    log(f"  {args.mirrors}-MIRROR TERNARIZATION ({bits} bits/param)")
    log(f"{'═' * 78}")
    log(f"  Model:     {args.model}")
    log(f"  Device:    {device}")
    log(f"  Mirrors:   {args.mirrors}")
    log(f"  Zero rate: {args.zero_rate:.0%}")
    log(f"  Bits/param: {bits}")

    # Load
    log(f"\n  Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16, trust_remote_code=True)
    if device == "mps":
        model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    log(f"  Loaded: {n_layers} layers")

    eval_texts = load_eval_texts()

    # Ternarize
    all_stats = mirror_ternarize_model(model, n_mirrors=args.mirrors,
                                       zero_rate=args.zero_rate, device=device)

    # Memory
    total_bytes = 0
    for name, buf in model.named_buffers():
        total_bytes += buf.nelement() * buf.element_size()
    for name, param in model.named_parameters():
        total_bytes += param.nelement() * param.element_size()
    log(f"\n  In-memory size: {total_bytes / 1e9:.2f} GB")

    # Perplexity
    ppl = evaluate_perplexity(model, tokenizer, eval_texts,
                              max_eval_tokens=args.max_eval_tokens,
                              device=device)

    # Generation
    if not args.skip_generation:
        gen = test_generation(model, tokenizer, GENERATION_PROMPTS, device=device)
        print_generations(gen, f"{args.mirrors}-MIRROR ({bits} bits)")

    # Final
    log(f"\n{'═' * 78}")
    log(f"  FINAL: {args.mirrors}-mirror, {bits} bits/param")
    log(f"  PPL: {ppl['perplexity']:.2f}")
    log(f"  NLL: {ppl['nll']:.4f}")
    log(f"{'═' * 78}\n")


if __name__ == "__main__":
    main()
