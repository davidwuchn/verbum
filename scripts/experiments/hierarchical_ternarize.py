#!/usr/bin/env python3
"""Hierarchical ternary — mirrors as computational roles, not weight reconstruction.

Instead of: W_recon = γ₁·T₁ + γ₂·T₂  (additive weight approximation)
We use:     gate * importance * values  (mirrors serve different computational roles)

Mirror 1 (T₁): the program — sign(W), which neurons fire, the crystal topology
Mirror 2 (T₂): importance — sign(residual), which firings matter more

For SwiGLU FFN:
  gate       = SiLU(γ₁_gate · T₁_gate @ x)           # topology: which neurons fire
  importance = sigmoid(γ₂_gate · T₂_gate @ x)          # importance: how much they matter  
  values     = γ₁_up · T₁_up @ x                       # values: what they compute
  hidden     = gate * importance * values               # importance-modulated FFN
  output     = γ₁_down · T₁_down @ hidden              # project back

This is NOT equivalent to additive mirrors because the sigmoid is applied
AFTER a separate ternary matmul, creating nonlinear interaction terms.

Usage:
  uv run python scripts/experiments/hierarchical_ternarize.py

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
# Ternary decomposition helpers
# ═══════════════════════════════════════════════════════════════════════

def extract_mirror(W: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Extract T₁, γ₁, and residual from weight matrix.

    Returns:
        T1: int8 sign matrix
        gamma1: float32 per-row scale
        residual: float32 residual W - γ₁·T₁
    """
    W_float = W.detach().float().cpu()
    T1 = torch.sign(W_float)

    # Optimal per-row gamma
    wt = (W_float * T1).sum(dim=1)
    tt = (T1 * T1).sum(dim=1)
    gamma1 = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))

    residual = W_float - gamma1.unsqueeze(1) * T1
    return T1.to(torch.int8), gamma1, residual


# ═══════════════════════════════════════════════════════════════════════
# Hierarchical Ternary MLP (replaces Qwen3MLP)
# ═══════════════════════════════════════════════════════════════════════

class HierarchicalTernaryMLP(nn.Module):
    """SwiGLU MLP with hierarchical ternary mirrors.

    Gate path uses TWO mirrors:
      T₁_gate: program (which neurons fire)
      T₂_gate: importance (how much each firing matters)

    Value and down paths use ONE mirror each.
    """

    def __init__(self, gate_T1, gate_gamma1, gate_T2, gate_gamma2,
                 up_T1, up_gamma1, down_T1, down_gamma1):
        super().__init__()
        # Gate: program
        self.register_buffer('gate_T1', gate_T1.to(torch.int8))
        self.register_buffer('gate_gamma1', gate_gamma1.to(torch.float32))
        # Gate: importance
        self.register_buffer('gate_T2', gate_T2.to(torch.int8))
        self.register_buffer('gate_gamma2', gate_gamma2.to(torch.float32))
        # Up: values
        self.register_buffer('up_T1', up_T1.to(torch.int8))
        self.register_buffer('up_gamma1', up_gamma1.to(torch.float32))
        # Down: projection
        self.register_buffer('down_T1', down_T1.to(torch.int8))
        self.register_buffer('down_gamma1', down_gamma1.to(torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        dtype = x.dtype
        device = x.device

        # Gate: the program — which neurons fire
        gate_T1 = self.gate_T1.to(device=device, dtype=dtype)
        gate_g1 = self.gate_gamma1.to(device=device, dtype=dtype)
        gate_logits = F.linear(x, gate_T1) * gate_g1
        gate = F.silu(gate_logits)

        # Importance: which firings matter more (post-nonlinearity modulation)
        gate_T2 = self.gate_T2.to(device=device, dtype=dtype)
        gate_g2 = self.gate_gamma2.to(device=device, dtype=dtype)
        importance_logits = F.linear(x, gate_T2) * gate_g2
        importance = torch.sigmoid(importance_logits)

        # Modulate gate by importance
        gate = gate * importance

        # Values: what each neuron computes
        up_T1 = self.up_T1.to(device=device, dtype=dtype)
        up_g1 = self.up_gamma1.to(device=device, dtype=dtype)
        values = F.linear(x, up_T1) * up_g1

        # SwiGLU combination
        hidden = gate * values

        # Project back to residual stream
        down_T1 = self.down_T1.to(device=device, dtype=dtype)
        down_g1 = self.down_gamma1.to(device=device, dtype=dtype)
        output = F.linear(hidden, down_T1) * down_g1

        return output


# ═══════════════════════════════════════════════════════════════════════
# Simple TernaryLinear for attention (same as before)
# ═══════════════════════════════════════════════════════════════════════

class TernaryLinear(nn.Module):
    def __init__(self, T, gamma, bias=None):
        super().__init__()
        self.register_buffer('T', T.to(torch.int8))
        self.register_buffer('gamma', gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer('bias', bias.to(torch.float32))
        else:
            self.bias = None

    def forward(self, x):
        T = self.T.to(device=x.device, dtype=x.dtype)
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        out = F.linear(x, T) * gamma
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out


# ═══════════════════════════════════════════════════════════════════════
# Model surgery
# ═══════════════════════════════════════════════════════════════════════

def ternarize_model_hierarchical(model, device="cpu"):
    """Replace all MLPs with HierarchicalTernaryMLP, attention with TernaryLinear."""
    layers = model.model.layers
    n_layers = len(layers)

    log(f"\n{'═' * 78}")
    log(f"  HIERARCHICAL TERNARIZATION (gate: T₁+T₂, up/down: T₁)")
    log(f"{'═' * 78}")
    log(f"  {'Layer':>5}  {'gate_T1':>8} {'gate_T2':>8} {'up_T1':>8} {'down_T1':>8} "
        f"{'q':>8} {'k':>8} {'v':>8} {'o':>8}")
    log(f"  {'─'*5}  {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")

    t0 = time.time()
    all_stats = []

    for i, layer in enumerate(layers):
        stats = {'layer': i}
        t_layer = time.time()

        # ── FFN: Hierarchical ternary ──
        W_gate = layer.mlp.gate_proj.weight.detach().float().cpu()
        W_up = layer.mlp.up_proj.weight.detach().float().cpu()
        W_down = layer.mlp.down_proj.weight.detach().float().cpu()

        # Gate Mirror 1 (program)
        gate_T1, gate_g1, gate_residual = extract_mirror(W_gate)
        stats['gate_T1_cos'] = F.cosine_similarity(
            W_gate.reshape(1, -1),
            (gate_g1.unsqueeze(1) * gate_T1.float()).reshape(1, -1)).item()

        # Gate Mirror 2 (importance) — from residual
        gate_T2 = torch.sign(gate_residual).to(torch.int8)
        rt2 = (gate_residual * gate_T2.float()).sum(dim=1)
        tt2 = (gate_T2.float() * gate_T2.float()).sum(dim=1)
        gate_g2 = torch.where(tt2 > 0, rt2 / tt2, torch.zeros_like(rt2))
        stats['gate_T2_cos'] = F.cosine_similarity(
            gate_residual.reshape(1, -1),
            (gate_g2.unsqueeze(1) * gate_T2.float()).reshape(1, -1)).item()

        # Up Mirror 1
        up_T1, up_g1, _ = extract_mirror(W_up)
        stats['up_cos'] = F.cosine_similarity(
            W_up.reshape(1, -1),
            (up_g1.unsqueeze(1) * up_T1.float()).reshape(1, -1)).item()

        # Down Mirror 1
        down_T1, down_g1, _ = extract_mirror(W_down)
        stats['down_cos'] = F.cosine_similarity(
            W_down.reshape(1, -1),
            (down_g1.unsqueeze(1) * down_T1.float()).reshape(1, -1)).item()

        # Build hierarchical MLP
        h_mlp = HierarchicalTernaryMLP(
            gate_T1, gate_g1, gate_T2, gate_g2,
            up_T1, up_g1, down_T1, down_g1,
        ).to(device)

        # Replace MLP
        layer.mlp = h_mlp
        del W_gate, W_up, W_down, gate_residual

        # ── Attention: simple ternary ──
        attn_cosines = []
        for name in ['q_proj', 'k_proj', 'v_proj', 'o_proj']:
            proj = getattr(layer.self_attn, name, None)
            if proj is None:
                continue
            W = proj.weight.detach().float().cpu()
            T1, g1, _ = extract_mirror(W)
            cos = F.cosine_similarity(
                W.reshape(1, -1),
                (g1.unsqueeze(1) * T1.float()).reshape(1, -1)).item()
            bias = proj.bias.detach().float().cpu() if proj.bias is not None else None
            tl = TernaryLinear(T1, g1, bias).to(device)
            setattr(layer.self_attn, name, tl)
            stats[name] = cos
            attn_cosines.append(cos)
            del proj, W

        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        all_stats.append(stats)

        q_cos = stats.get('q_proj', 0)
        k_cos = stats.get('k_proj', 0)
        v_cos = stats.get('v_proj', 0)
        o_cos = stats.get('o_proj', 0)
        log(f"  {i:>5}  {stats['gate_T1_cos']:>8.5f} {stats['gate_T2_cos']:>8.5f} "
            f"{stats['up_cos']:>8.5f} {stats['down_cos']:>8.5f} "
            f"{q_cos:>8.5f} {k_cos:>8.5f} {v_cos:>8.5f} {o_cos:>8.5f}  "
            f"({time.time()-t_layer:.1f}s)")

    elapsed = time.time() - t0
    log(f"\n  Done in {elapsed:.1f}s")

    return all_stats


# ═══════════════════════════════════════════════════════════════════════
# Eval (same as mirror_ternarize.py)
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
        return ["The speed of light is 299792458 meters per second."] * 5


@torch.no_grad()
def evaluate_perplexity(model, tokenizer, texts, max_length=512, stride=256,
                        max_eval_tokens=16384, device="mps"):
    log(f"\n  Evaluating perplexity...")
    t0 = time.time()
    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = input_ids.size(0)
    if max_eval_tokens > 0 and seq_len > max_eval_tokens:
        log(f"  Tokens: {seq_len:,} → {max_eval_tokens:,}")
        input_ids = input_ids[:max_eval_tokens]
        seq_len = max_eval_tokens
    else:
        log(f"  Tokens: {seq_len:,}")

    n_windows = (seq_len - 1 + stride - 1) // stride
    nlls, n_tokens, wc = [], 0, 0

    for begin_loc in range(0, seq_len - 1, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        score_begin = stride if begin_loc > 0 else 0
        chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)
        logits = model(chunk).logits
        s_logits = logits[0, score_begin:-1, :].contiguous()
        s_labels = chunk[0, score_begin + 1:].contiguous()
        loss = F.cross_entropy(s_logits, s_labels, reduction='sum')
        nlls.append(loss.float().cpu().item())
        n_tokens += s_labels.size(0)
        wc += 1
        if wc % 10 == 0:
            ppl_so_far = math.exp(min(sum(nlls) / n_tokens, 20))
            log(f"    [{wc}/{n_windows}] {n_tokens:,} tok, PPL={ppl_so_far:.2f}")
        if end_loc >= seq_len:
            break

    nll = sum(nlls) / n_tokens
    ppl = math.exp(min(nll, 20))
    log(f"  NLL: {nll:.4f}, PPL: {ppl:.2f} ({time.time()-t0:.1f}s)")
    return {'perplexity': ppl, 'nll': nll, 'n_tokens': n_tokens}


PROMPTS = [
    "The capital of France is",
    "The speed of light is approximately",
    "If all dogs are animals and all animals are living things, then all dogs are",
    "def fibonacci(n):\n    \"\"\"Return the nth Fibonacci number.\"\"\"\n",
    "Once upon a time, in a forest deep and dark, there lived a",
    "In lambda calculus, the identity combinator I is defined as",
]


@torch.no_grad()
def test_generation(model, tokenizer, device="mps"):
    log(f"\n{'═' * 78}")
    log(f"  GENERATION — HIERARCHICAL TERNARY")
    log(f"{'═' * 78}")
    for i, prompt in enumerate(PROMPTS):
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        t0 = time.time()
        output = model.generate(**inputs, max_new_tokens=64, do_sample=False,
                                pad_token_id=tokenizer.eos_token_id)
        elapsed = time.time() - t0
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        new_tok = output.shape[1] - inputs['input_ids'].shape[1]
        log(f"\n  ── Prompt {i+1} ({new_tok} tok, {new_tok/elapsed:.1f} tok/s) ──")
        log(f"  {prompt}")
        for line in text[len(prompt):].split('\n'):
            log(f"  ▸ {line}")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-eval-tokens", type=int, default=16384)
    parser.add_argument("--skip-generation", action="store_true")
    args = parser.parse_args()

    if args.device == "auto":
        device = "mps" if torch.backends.mps.is_available() else "cpu"
    else:
        device = args.device

    log(f"\n{'═' * 78}")
    log(f"  HIERARCHICAL TERNARY TERNARIZATION")
    log(f"  Gate: T₁ (program) + T₂ (importance, post-SiLU sigmoid)")
    log(f"  Up/Down/Attn: T₁ only (per-row scale)")
    log(f"{'═' * 78}")

    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"\n  Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16, trust_remote_code=True)
    if device == "mps":
        model = model.to(device)
    model.eval()
    log(f"  Loaded: {model.config.num_hidden_layers} layers")

    eval_texts = load_eval_texts()

    # Ternarize
    stats = ternarize_model_hierarchical(model, device=device)

    # PPL
    ppl = evaluate_perplexity(model, tokenizer, eval_texts,
                              max_eval_tokens=args.max_eval_tokens, device=device)

    # Generate
    if not args.skip_generation:
        test_generation(model, tokenizer, device=device)

    log(f"\n{'═' * 78}")
    log(f"  FINAL: Hierarchical ternary")
    log(f"  PPL: {ppl['perplexity']:.2f}, NLL: {ppl['nll']:.4f}")
    log(f"{'═' * 78}\n")


if __name__ == "__main__":
    main()
