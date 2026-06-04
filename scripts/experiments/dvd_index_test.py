#!/usr/bin/env python3
"""DVD Index Test — Is compounding from index corruption (QK) or value noise (V/FFN)?

THE HYPOTHESIS: Attention QK is an index/addressing system. Ternarizing QK
corrupts addresses → wrong lookups → wrong inputs to next layer → exponential
compounding. Ternarizing V/O/FFN adds noise to values but doesn't shift the
index → linear degradation.

FOUR CONFIGURATIONS:
  1. FFN only    — ternarize gate/up/down, keep ALL attention float
  2. V/O only    — ternarize value path, keep Q/K float (index preserved)
  3. Q/K only    — ternarize index, keep values float
  4. All         — ternarize everything (baseline)

Uses magnitude mask + per-group(32) scaling (best PPL from dvd_group_scale).
Reuses gradient_maps.pt for the gradient mask variant.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/dvd_index_test.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "dvd-index-test"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# Ternary modules (reused from dvd_group_scale.py)
# ═══════════════════════════════════════════════════════════════════════


class TernaryLinearGrouped(nn.Module):
    """Ternary Linear with per-group scale factors."""

    def __init__(self, T: torch.Tensor, gamma: torch.Tensor,
                 group_size: int, bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer("T", T.to(torch.int8))
        self.register_buffer("gamma", gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer("bias", bias.to(torch.float32))
        else:
            self.bias = None
        self.out_features = T.shape[0]
        self.in_features = T.shape[1]
        self.group_size = group_size
        self.n_groups = gamma.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        gamma_expanded = gamma.repeat_interleave(self.group_size, dim=1)
        gamma_expanded = gamma_expanded[:, :self.in_features]
        T_cast = self.T.to(device=x.device, dtype=x.dtype)
        W_eff = gamma_expanded * T_cast
        out = F.linear(x, W_eff)
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out


# ═══════════════════════════════════════════════════════════════════════
# Ternarization
# ═══════════════════════════════════════════════════════════════════════


def ternarize_per_group(W: torch.Tensor, zero_rate: float = 0.50,
                        group_size: int = 32):
    """Ternarize with magnitude mask + per-group optimal gamma."""
    W_f = W.detach().float().cpu()
    out_f, in_f = W_f.shape

    # Magnitude mask: zero smallest |W| per row
    abs_W = W_f.abs()
    thresh = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
    mask = abs_W >= thresh

    T = torch.where(mask, torch.sign(W_f), torch.zeros_like(W_f))

    # Per-group gamma
    n_groups = (in_f + group_size - 1) // group_size
    gamma = torch.zeros(out_f, n_groups, dtype=torch.float32)
    for g in range(n_groups):
        s, e = g * group_size, min((g + 1) * group_size, in_f)
        W_g, T_g = W_f[:, s:e], T[:, s:e]
        wt = (W_g * T_g).sum(dim=1)
        tt = (T_g * T_g).sum(dim=1)
        gamma[:, g] = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))

    # Cosine
    gamma_exp = gamma.repeat_interleave(group_size, dim=1)[:, :in_f]
    W_recon = gamma_exp * T
    cos = F.cosine_similarity(W_f.reshape(1, -1), W_recon.reshape(1, -1)).item()

    return T.to(torch.int8), gamma, cos


def get_model_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError("Cannot find layers")


# Module sets for each configuration
CONFIGS = {
    "ffn_only": {
        "ffn": ["gate_proj", "up_proj", "down_proj"],
        "attn": [],
    },
    "vo_only": {
        "ffn": [],
        "attn": ["v_proj", "o_proj"],
    },
    "qk_only": {
        "ffn": [],
        "attn": ["q_proj", "k_proj"],
    },
    "all": {
        "ffn": ["gate_proj", "up_proj", "down_proj"],
        "attn": ["q_proj", "k_proj", "v_proj", "o_proj"],
    },
}


def ternarize_layer(layer, layer_idx, config, zero_rate, group_size, device):
    """Ternarize selected modules in one layer."""
    cosines = {}
    n_params_ternary = 0
    n_params_float = 0

    # FFN
    for name in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(layer.mlp, name, None)
        if proj is None:
            continue
        if name in config["ffn"]:
            W = proj.weight
            T, gamma, cos = ternarize_per_group(W, zero_rate, group_size)
            bias = proj.bias.detach().float().cpu() if proj.bias is not None else None
            tl = TernaryLinearGrouped(T, gamma, group_size, bias).to(device)
            setattr(layer.mlp, name, tl)
            cosines[name] = cos
            n_params_ternary += W.numel()
            del proj
        else:
            n_params_float += proj.weight.numel()

    # Attention
    for name in ["q_proj", "k_proj", "v_proj", "o_proj"]:
        proj = getattr(layer.self_attn, name, None)
        if proj is None:
            continue
        if name in config["attn"]:
            W = proj.weight
            T, gamma, cos = ternarize_per_group(W, zero_rate, group_size)
            bias = proj.bias.detach().float().cpu() if proj.bias is not None else None
            tl = TernaryLinearGrouped(T, gamma, group_size, bias).to(device)
            setattr(layer.self_attn, name, tl)
            cosines[name] = cos
            n_params_ternary += W.numel()
            del proj
        else:
            n_params_float += proj.weight.numel()

    gc.collect()
    return cosines, n_params_ternary, n_params_float


# ═══════════════════════════════════════════════════════════════════════
# Compounding measurement
# ═══════════════════════════════════════════════════════════════════════


PROBE_TEXTS = [
    "The capital of France is Paris, located along the Seine river.",
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "(λx. λy. x y) (λz. z) reduces to (λy. y) which is the identity combinator I.",
    "Quantum entanglement occurs when two particles become correlated.",
    "The derivative of sin(x) is cos(x), a fundamental result in calculus.",
    "Once upon a time in a small village there lived an old clockmaker.",
    "SELECT name, age FROM users WHERE age > 18 ORDER BY name;",
    "日本の首都は東京で、世界最大の都市圏の一つです。",
]


@torch.no_grad()
def collect_float_hidden(model, tokenizer, device):
    encoded = tokenizer(
        PROBE_TEXTS, return_tensors="pt", padding=True,
        truncation=True, max_length=128,
    ).to(device)
    outputs = model(
        input_ids=encoded["input_ids"],
        attention_mask=encoded["attention_mask"],
        output_hidden_states=True,
    )
    mask = encoded["attention_mask"].bool()
    return [hs[mask].float().cpu() for hs in outputs.hidden_states]


@torch.no_grad()
def run_config(cfg_name, config, tokenizer, model_name, device,
               zero_rate, group_size):
    """Run compounding sweep + PPL for one configuration."""
    from transformers import AutoModelForCausalLM

    log(f"\n{'═' * 78}")
    log(f"  CONFIG: {cfg_name}")
    log(f"  Ternary: FFN={config['ffn'] or 'none'}  Attn={config['attn'] or 'none'}")
    log(f"{'═' * 78}")

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map=device,
    )
    model.eval()

    # Float reference
    log(f"  Collecting float reference...")
    float_hidden = collect_float_hidden(model, tokenizer, device)
    n_layers = len(float_hidden) - 1
    log(f"  Reference: {n_layers} layers, {float_hidden[0].shape[0]} tokens")

    # Progressive ternarization
    layers = get_model_layers(model)
    sweep = []
    total_ternary = 0
    total_float = 0

    for depth in range(n_layers):
        lcos, n_t, n_f = ternarize_layer(
            layers[depth], depth, config, zero_rate, group_size, device,
        )
        total_ternary += n_t
        total_float += n_f
        mean_wcos = np.mean(list(lcos.values())) if lcos else float("nan")

        # Forward pass
        encoded = tokenizer(
            PROBE_TEXTS, return_tensors="pt", padding=True,
            truncation=True, max_length=128,
        ).to(device)
        outputs = model(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"],
            output_hidden_states=True,
        )
        mask_tok = encoded["attention_mask"].bool()
        hs_tern = outputs.hidden_states[depth + 1][mask_tok].float().cpu()
        hs_float = float_hidden[depth + 1]

        cos_per_token = F.cosine_similarity(hs_tern, hs_float, dim=1)
        mean_cos = cos_per_token.mean().item()
        min_cos = cos_per_token.min().item()

        sweep.append({
            "depth": depth,
            "cumulative_cosine": mean_cos,
            "cumulative_cosine_min": min_cos,
            "weight_cosine_mean": float(mean_wcos) if not math.isnan(mean_wcos) else None,
        })

        wcos_str = f"wcos={mean_wcos:.4f}" if not math.isnan(mean_wcos) else "wcos=float"
        log(f"  L{depth:>2}: cos={mean_cos:.6f}  min={min_cos:.6f}  {wcos_str}")

        gc.collect()
        if device == "mps":
            torch.mps.empty_cache()

    # Now measure PPL with all layers ternarized
    log(f"\n  Params: {total_ternary:,} ternary + {total_float:,} float "
        f"({total_ternary/(total_ternary+total_float)*100:.1f}% ternary)")

    log(f"  Evaluating PPL...")
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        eval_texts = [t for t in ds["text"] if t.strip()]
    except Exception:
        eval_texts = PROBE_TEXTS

    full_text = "\n\n".join(eval_texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    max_eval = 16384
    seq_len = min(input_ids.size(0), max_eval)
    input_ids = input_ids[:seq_len]

    nlls = []
    n_tokens = 0
    stride, max_length = 256, 512

    with torch.no_grad():
        for begin_loc in range(0, seq_len - 1, stride):
            end_loc = min(begin_loc + max_length, seq_len)
            score_begin = stride if begin_loc > 0 else 0
            chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)
            logits = model(chunk).logits
            shift_logits = logits[0, score_begin:-1, :].contiguous()
            shift_labels = chunk[0, score_begin + 1:].contiguous()
            loss = F.cross_entropy(shift_logits, shift_labels, reduction="sum")
            nlls.append(loss.float().cpu().item())
            n_tokens += shift_labels.size(0)
            if end_loc >= seq_len:
                break

    mean_nll = sum(nlls) / n_tokens
    ppl = math.exp(min(mean_nll, 20))
    log(f"  PPL: {ppl:.2f}  NLL: {mean_nll:.4f}  ({n_tokens:,} tokens)")

    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    return {
        "sweep": sweep,
        "ppl": ppl,
        "nll": mean_nll,
        "n_tokens": n_tokens,
        "params_ternary": total_ternary,
        "params_float": total_float,
        "pct_ternary": total_ternary / (total_ternary + total_float) * 100,
    }


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="DVD Index Test")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--zero-rate", type=float, default=0.50)
    parser.add_argument("--group-size", type=int, default=32)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  DVD INDEX TEST — Where Does Compounding Come From?{' ' * 23}║")
    log(f"║  Model: {args.model:<67}║")
    log(f"║  Hypothesis: QK = index corruption → exponential compounding{' ' * 14}║")
    log(f"║              V/FFN = value noise → linear degradation{' ' * 22}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    results = {}
    for cfg_name in ["ffn_only", "vo_only", "qk_only", "all"]:
        results[cfg_name] = run_config(
            cfg_name, CONFIGS[cfg_name], tokenizer, args.model,
            args.device, args.zero_rate, args.group_size,
        )

    # ── Comparison tables ──
    log(f"\n{'═' * 78}")
    log(f"  COMPOUNDING COMPARISON — Index vs Value")
    log(f"{'═' * 78}")
    log(f"  {'L':>3}  {'FFN only':>9} {'V/O only':>9} {'Q/K only':>9} {'All':>9}")
    log(f"  {'─' * 3}  {'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")

    n = len(results["all"]["sweep"])
    for i in range(n):
        vals = {}
        for c in ["ffn_only", "vo_only", "qk_only", "all"]:
            vals[c] = results[c]["sweep"][i]["cumulative_cosine"]
        log(f"  {i:>3}  {vals['ffn_only']:>9.6f} {vals['vo_only']:>9.6f} "
            f"{vals['qk_only']:>9.6f} {vals['all']:>9.6f}")

    log(f"\n  FINAL (layer {n-1}):")
    for c in ["ffn_only", "vo_only", "qk_only", "all"]:
        v = results[c]["sweep"][-1]["cumulative_cosine"]
        log(f"    {c:<12} cos={v:.6f}")

    log(f"\n{'═' * 78}")
    log(f"  PERPLEXITY COMPARISON")
    log(f"{'═' * 78}")
    log(f"  {'Config':<12} {'PPL':>12}  {'NLL':>8}  {'% Ternary':>10}  {'Ternary params':>15}")
    log(f"  {'─' * 12} {'─' * 12}  {'─' * 8}  {'─' * 10}  {'─' * 15}")
    for c in ["ffn_only", "vo_only", "qk_only", "all"]:
        r = results[c]
        log(f"  {c:<12} {r['ppl']:>12.2f}  {r['nll']:>8.4f}  "
            f"{r['pct_ternary']:>9.1f}%  {r['params_ternary']:>15,}")

    # ── Key diagnostic: compounding RATE ──
    log(f"\n{'═' * 78}")
    log(f"  COMPOUNDING RATE — cos at depth 10 / cos at depth 1")
    log(f"{'═' * 78}")
    for c in ["ffn_only", "vo_only", "qk_only", "all"]:
        cos1 = results[c]["sweep"][1]["cumulative_cosine"]
        cos10 = results[c]["sweep"][10]["cumulative_cosine"]
        cos20 = results[c]["sweep"][20]["cumulative_cosine"]
        cos33 = results[c]["sweep"][33]["cumulative_cosine"]
        rate_10 = cos10 / cos1 if cos1 > 0.01 else float("inf")
        rate_20 = cos20 / cos1 if cos1 > 0.01 else float("inf")
        log(f"  {c:<12} L1={cos1:.4f}  L10={cos10:.4f}({rate_10:.3f}×)  "
            f"L20={cos20:.4f}({rate_20:.3f}×)  L33={cos33:.4f}")

    # Save
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
