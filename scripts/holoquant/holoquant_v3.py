#!/usr/bin/env python3
"""HoloQuant v3 — Beam/plate mixed-precision + quantile-optimal levels.

v1: naive ternary → catastrophic (PPL 31→142K)
v2: selective ternary → still catastrophic (signs ≠ forward pass)
v3: holographic-informed multi-bit quantization

Key insights from session 098 exploration:
  1. The holographic seed is 3 magnitude bits per weight (which of 8 bins)
  2. Quantile-optimal level placement beats uniform at same bit count
     (Q3: PPL 1747→580, Q4: PPL 290→260 on Pythia)
  3. Beam/plate classification tells us WHERE to allocate bits
  4. For MoE models: 93% of params are plate (expert FFN) → fewer bits
     while 5% are beam (Q projections) → more bits

Strategy:
  PLATE components (K, V, O, expert FFN):  Q3 quantile (3.25 bits)
  MARGINAL components (FFN gate):          Q4 quantile (4.25 bits)
  BEAM components (Q, reader, gates):      Q5-Q6 quantile (5-6 bits)
  PRECISION components (norms, conv1d):    FP16

Usage:
    # Pythia-160M (fast validation)
    uv run python scripts/holoquant/holoquant_v3.py --model pythia

    # Qwen3.6-35B-A3B
    uv run python scripts/holoquant/holoquant_v3.py --model qwen36

License: MIT
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Models
# ══════════════════════════════════════════════════════════════════

MODELS = {
    "pythia": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "arch": "gpt_neox",
        "dtype": torch.float32,
    },
    "pythia-1b": {
        "hf_name": "EleutherAI/pythia-1b-deduped",
        "arch": "gpt_neox",
        "dtype": torch.float32,
    },
    "qwen36": {
        "hf_name": "Qwen/Qwen3.6-35B-A3B",
        "arch": "qwen3_5_moe",
        "dtype": torch.float16,
    },
}


# ══════════════════════════════════════════════════════════════════
# Quantile-optimal quantization
# ══════════════════════════════════════════════════════════════════

def quant_quantile(W: torch.Tensor, n_levels: int,
                   group_size: int = 64) -> torch.Tensor:
    """Quantile-optimal quantization: place levels at distribution quantiles.

    For Gaussian-distributed weights, this places more levels near zero
    (where the density is highest) and fewer in the tails.
    Equivalent to a Lloyd-Max quantizer for the empirical distribution.

    Returns reconstructed float tensor.
    """
    flat = W.float().reshape(-1)
    n = flat.shape[0]
    n_padded = ((n + group_size - 1) // group_size) * group_size
    if n_padded > n:
        flat = F.pad(flat, (0, n_padded - n))

    groups = flat.reshape(-1, group_size)
    signs = torch.sign(groups)
    mags = groups.abs()

    n_pos = max(n_levels // 2, 1)
    reconstructed = torch.zeros_like(groups)

    for g in range(groups.shape[0]):
        m = mags[g]
        if n_pos <= 1:
            reconstructed[g] = signs[g] * m.mean()
            continue
        quantiles = torch.quantile(m, torch.linspace(0, 1, n_pos + 1,
                                                      device=m.device))
        levels = (quantiles[:-1] + quantiles[1:]) / 2
        diffs = (m.unsqueeze(-1) - levels.unsqueeze(0)).abs()
        assignments = diffs.argmin(dim=-1)
        reconstructed[g] = signs[g] * levels[assignments]

    return reconstructed.reshape(-1)[:n].reshape(W.shape)


def quant_uniform(W: torch.Tensor, bits: int,
                  group_size: int = 64) -> torch.Tensor:
    """Standard uniform N-bit quantization with group scales."""
    flat = W.float().reshape(-1)
    n = flat.shape[0]
    n_padded = ((n + group_size - 1) // group_size) * group_size
    if n_padded > n:
        flat = F.pad(flat, (0, n_padded - n))

    groups = flat.reshape(-1, group_size)
    max_vals = groups.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-10)
    n_levels = 2 ** bits
    scaled = groups / max_vals
    quantized = torch.round(scaled * (n_levels // 2 - 1)) / (n_levels // 2 - 1)
    return (quantized * max_vals).reshape(-1)[:n].reshape(W.shape)


# ══════════════════════════════════════════════════════════════════
# Beam/Plate classification + quantization configs
# ══════════════════════════════════════════════════════════════════

# Classification: which components get how many levels
# Based on beam trace findings (session 098):
#   PLATE: K, V, O, expert FFN — ternary-safe, fewer bits needed
#   BEAM:  Q, reader, MoE gates — precision-critical, more bits needed

HOLOQUANT_CONFIGS = {
    # Baseline: uniform Q4 everywhere
    "uniform-Q4": {
        "description": "Standard uniform 4-bit (baseline comparison)",
        "default": ("uniform", 4),
    },

    # Quantile Q4: same bits, better quality
    "quantile-Q4": {
        "description": "Quantile-optimal 4-bit (same bits, ~5% better PPL)",
        "default": ("quantile", 16),
    },

    # HoloQuant v3: beam/plate mixed-precision
    "holoquant-v3": {
        "description": "Beam/plate mixed: plate=Q3q, marginal=Q4q, beam=Q5q",
        "gpt_neox": {
            # GPT-NeoX (Pythia): fused QKV contains beam (Q)
            "query_key_value": ("quantile", 32),    # Q5: contains Q (beam)
            "attention.dense":  ("quantile", 8),     # Q3: O projection (plate)
            "dense_h_to_4h":    ("quantile", 16),    # Q4: FFN gate (marginal)
            "dense_4h_to_h":    ("quantile", 32),    # Q5: FFN reader (beam)
        },
        "qwen3_5_moe": {
            # Qwen3.6 MoE: separated Q/K/V, expert FFN is the plate
            "q_proj":                   ("quantile", 32),    # Q5: beam angle
            "k_proj":                   ("quantile", 8),     # Q3: plate
            "v_proj":                   ("quantile", 8),     # Q3: plate
            "o_proj":                   ("quantile", 8),     # Q3: plate
            "linear_attn.out_proj":     ("quantile", 8),     # Q3: plate
            "linear_attn.in_proj_qkv":  ("quantile", 16),    # Q4: mixed Q+KV
            "experts.gate_up_proj":     ("quantile", 8),     # Q3: expert plate!
            "experts.down_proj":        ("quantile", 12),    # Q3.6: expert reader
            "shared_expert.gate_proj":  ("quantile", 8),     # Q3: shared plate
            "shared_expert.up_proj":    ("quantile", 8),     # Q3: shared plate
            "shared_expert.down_proj":  ("quantile", 12),    # Q3.6: shared reader
            "mlp.gate.weight":          ("quantile", 64),    # Q6: MoE gate (beam!)
        },
        "default": ("quantile", 8),
    },

    # Aggressive: push plate down to Q2 quantile
    "holoquant-v3-aggressive": {
        "description": "Aggressive: plate=Q2q (4 levels), beam=Q5q",
        "gpt_neox": {
            "query_key_value": ("quantile", 32),
            "attention.dense":  ("quantile", 4),     # Q2: plate
            "dense_h_to_4h":    ("quantile", 8),     # Q3: marginal
            "dense_4h_to_h":    ("quantile", 32),    # Q5: reader
        },
        "qwen3_5_moe": {
            "q_proj":                   ("quantile", 32),
            "k_proj":                   ("quantile", 4),     # Q2: plate
            "v_proj":                   ("quantile", 4),     # Q2: plate
            "o_proj":                   ("quantile", 4),     # Q2: plate
            "linear_attn.out_proj":     ("quantile", 4),
            "experts.gate_up_proj":     ("quantile", 6),     # Q2.6: plate
            "experts.down_proj":        ("quantile", 8),     # Q3: reader
            "shared_expert.gate_proj":  ("quantile", 6),
            "shared_expert.up_proj":    ("quantile", 6),
            "shared_expert.down_proj":  ("quantile", 8),
            "mlp.gate.weight":          ("quantile", 64),    # Q6: beam
        },
        "default": ("quantile", 6),
    },
}


# ══════════════════════════════════════════════════════════════════
# Classification engine
# ══════════════════════════════════════════════════════════════════

SKIP_PATTERNS = [
    "layernorm", "layer_norm", "rmsnorm", "norm.weight", "norm.bias",
    "input_layernorm", "post_attention_layernorm",
    "q_norm.", "k_norm.",
    "conv1d.", "A_log", "dt_bias",
    "visual.",
]


def apply_holoquant(model, config_name: str, arch: str) -> dict:
    """Apply HoloQuant v3 to a model."""
    config = HOLOQUANT_CONFIGS[config_name]
    arch_spec = config.get(arch, {})
    default = config.get("default", ("quantile", 8))

    stats = {
        "config": config_name,
        "per_component": [],
        "total_params": 0,
        "total_bits": 0,
    }

    for name, param in list(model.named_parameters()):
        n = param.numel()
        stats["total_params"] += n

        # Skip small params
        if n < 1024:
            stats["total_bits"] += n * 32
            continue

        # Skip norms, conv1d, etc.
        if any(s in name for s in SKIP_PATTERNS):
            stats["total_bits"] += n * 16
            stats["per_component"].append({
                "name": name, "params": n, "method": "FP16",
                "bits": 16, "reason": "precision-critical",
            })
            continue

        # Find matching spec
        method, n_levels_or_bits = default
        matched_key = "default"
        for key, val in arch_spec.items():
            if key in name:
                method, n_levels_or_bits = val
                matched_key = key
                break

        # Apply quantization
        W = param.data.float()

        if method == "uniform":
            param.data = quant_uniform(W, n_levels_or_bits).to(param.dtype)
            bits = n_levels_or_bits + 0.25
        else:
            # Handle 3D expert tensors
            if W.dim() == 3:
                for ei in range(W.shape[0]):
                    W[ei] = quant_quantile(W[ei], n_levels_or_bits)
                param.data = W.to(param.dtype)
            else:
                param.data = quant_quantile(W, n_levels_or_bits).to(param.dtype)
            bits = math.log2(n_levels_or_bits) + 0.25

        stats["total_bits"] += n * bits
        stats["per_component"].append({
            "name": name, "params": n, "method": f"{method}-{n_levels_or_bits}",
            "bits": bits, "matched": matched_key,
        })

    stats["avg_bits"] = stats["total_bits"] / stats["total_params"]
    return stats


# ══════════════════════════════════════════════════════════════════
# Perplexity
# ══════════════════════════════════════════════════════════════════

def get_test_texts():
    return [
        "The transformer architecture revolutionized natural language processing by introducing self-attention mechanisms that allow models to weigh the importance of different parts of the input when producing each part of the output.",
        "In quantum mechanics, the wave function describes the quantum state of a particle or system of particles. The Schrödinger equation governs how the wave function evolves over time.",
        "The Viable System Model, developed by Stafford Beer in 1972, describes the organizational structure needed for any viable system.",
        "Lambda calculus is a formal system for expressing computation based on function abstraction and application using variable binding and substitution.",
        "The holographic principle suggests that the description of a volume of space can be thought of as encoded on a lower-dimensional boundary to the region.",
        "Machine learning models learn representations of data through gradient descent optimization. The loss function measures how well the model's predictions match the true labels.",
        "Combinatory logic is a notation to eliminate the need for quantified variables in mathematical logic. It was introduced by Moses Schönfinkel and Haskell Curry.",
        "The attention mechanism in neural networks allows the model to focus on relevant parts of the input sequence when generating each output token.",
    ]


@torch.no_grad()
def measure_perplexity(model, tokenizer, texts, max_length=512, device="cpu"):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                           max_length=max_length).to(device)
        if inputs["input_ids"].shape[1] < 2:
            continue
        outputs = model(**inputs, labels=inputs["input_ids"])
        n_tokens = inputs["input_ids"].shape[1] - 1
        total_loss += outputs.loss.item() * n_tokens
        total_tokens += n_tokens
    return math.exp(total_loss / total_tokens) if total_tokens > 0 else float("inf")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="HoloQuant v3 — beam/plate mixed-precision + quantile-optimal")
    parser.add_argument("--model", default="pythia", choices=list(MODELS.keys()))
    parser.add_argument("--config", default="all",
                        help="Config name or 'all'")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-length", type=int, default=512)
    args = parser.parse_args()

    cfg = MODELS[args.model]
    configs_to_test = (list(HOLOQUANT_CONFIGS.keys())
                       if args.config == "all" else [args.config])
    texts = get_test_texts()

    print(f"HoloQuant v3 — Beam/Plate Mixed-Precision + Quantile-Optimal")
    print(f"  Model: {cfg['hf_name']}")
    print(f"  Device: {args.device}")
    print()

    results = []

    for config_name in configs_to_test:
        print(f"\n{'='*70}")
        print(f"CONFIG: {config_name}")
        desc = HOLOQUANT_CONFIGS[config_name].get("description", "")
        if desc:
            print(f"  {desc}")
        print(f"{'='*70}")

        # Fresh model
        print(f"  Loading model...", end="", flush=True)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(cfg["hf_name"],
                                                   trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            cfg["hf_name"], torch_dtype=cfg["dtype"],
            device_map=args.device, trust_remote_code=True)
        model.eval()
        total_params = sum(p.numel() for p in model.parameters())
        print(f" {time.time()-t0:.1f}s ({total_params:,} params)")

        # Baseline (only first time)
        if not results:
            print(f"  Baseline perplexity...", end="", flush=True)
            t0 = time.time()
            baseline_ppl = measure_perplexity(
                model, tokenizer, texts, args.max_length, args.device)
            print(f" {baseline_ppl:.2f} ({time.time()-t0:.1f}s)")
        else:
            baseline_ppl = results[0]["baseline_ppl"]

        # Apply HoloQuant
        print(f"  Applying {config_name}...", end="", flush=True)
        t0 = time.time()
        stats = apply_holoquant(model, config_name, cfg["arch"])
        print(f" {time.time()-t0:.1f}s")
        print(f"  Average bits: {stats['avg_bits']:.2f}")

        # Measure
        print(f"  Measuring perplexity...", end="", flush=True)
        t0 = time.time()
        holo_ppl = measure_perplexity(
            model, tokenizer, texts, args.max_length, args.device)
        print(f" {holo_ppl:.2f} ({time.time()-t0:.1f}s)")

        ppl_delta = 100 * (holo_ppl - baseline_ppl) / baseline_ppl
        original_bytes = total_params * (2 if cfg["dtype"] == torch.float16 else 4)
        holo_bytes = stats["total_bits"] / 8

        print(f"\n  RESULT:")
        print(f"    Baseline:   {baseline_ppl:.2f}")
        print(f"    HoloQuant:  {holo_ppl:.2f} ({ppl_delta:+.1f}%)")
        print(f"    Avg bits:   {stats['avg_bits']:.2f}")
        print(f"    Memory:     {holo_bytes/1e6:.1f} MB "
              f"(was {original_bytes/1e6:.1f} MB, "
              f"{original_bytes/holo_bytes:.1f}×)")

        results.append({
            "config": config_name,
            "baseline_ppl": baseline_ppl,
            "holo_ppl": holo_ppl,
            "ppl_delta_pct": ppl_delta,
            "avg_bits": stats["avg_bits"],
            "compression": original_bytes / holo_bytes,
        })

        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Final table
    print(f"\n\n{'='*70}")
    print(f"COMPARISON TABLE — {cfg['hf_name']}")
    print(f"{'='*70}")
    print(f"{'Config':<35} {'Bits':>6} {'PPL':>8} {'Delta%':>8} "
          f"{'Compr':>6} {'Verdict':>8}")
    print(f"{'─'*35} {'─'*6} {'─'*8} {'─'*8} {'─'*6} {'─'*8}")

    for r in results:
        d = r["ppl_delta_pct"]
        verdict = ("✅" if abs(d) < 5 else "⚠️" if abs(d) < 25
                   else "❌" if abs(d) < 100 else "💀")
        print(f"{r['config']:<35} {r['avg_bits']:>6.2f} "
              f"{r['holo_ppl']:>8.1f} {d:>+7.1f}% "
              f"{r['compression']:>5.1f}× {verdict:>8}")


if __name__ == "__main__":
    main()
