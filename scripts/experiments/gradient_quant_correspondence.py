#!/usr/bin/env python3
"""Test: do near-zero gradients predict low quantization error?

The thesis: gradient descent IS beta reduction. GD produces near-zero
gradients where computation is irreducible (normal form). Irreducible
positions are already effectively ternary {-1, 0, +1}. Therefore:

  PREDICTION: |∇L| correlates positively with |W - Q(W)|
  - Small gradient → already at fixed point → quantizes cleanly
  - Large gradient → still mid-reduction → needs continuous precision

This is a direct, falsifiable test of whether GD convergence and
ternary quantizability measure the same thing (irreducibility).

Method:
  1. Load model, run forward+backward on calibration text → gradients
  2. For each weight matrix, compute ternary quantization error per position
  3. Correlate |gradient| with |quantization error| across all positions
  4. Bin by gradient magnitude, plot mean quant error per bin

Usage:
  uv run python scripts/experiments/gradient_quant_correspondence.py
  uv run python scripts/experiments/gradient_quant_correspondence.py --model Qwen/Qwen3-0.6B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# Calibration texts — diverse, short, covering multiple domains
# ══════════════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    "The cat sat on the mat and watched the birds fly south for winter.",
    "In quantum mechanics, the wave function describes the probability amplitude.",
    "She opened the door carefully, unsure what she would find on the other side.",
    "The derivative of x squared with respect to x equals two x.",
    "Parliament voted to approve the new trade agreement with a narrow majority.",
    "Lambda calculus provides a formal system for expressing computation.",
    "The ancient ruins stood silent against the crimson sunset sky.",
    "Recursive data structures can be defined in terms of themselves.",
    "Interest rates rose sharply, causing concern in the housing market.",
    "The patient presented with fever, cough, and difficulty breathing.",
    "Every group homomorphism preserves the identity element.",
    "He ran through the rain without an umbrella, laughing at the absurdity.",
    "The function composes two operations and returns their combined result.",
    "Climate data from the past century shows a clear warming trend.",
    "She selected the red one and discarded the blue alternative.",
    "The compiler transforms source code into an executable binary format.",
]


def ternary_quantize(W: torch.Tensor) -> torch.Tensor:
    """Ternary quantization: W → sign(W) * gamma, per row.

    gamma = mean(|W|) per row (the standard ternary approach).
    Positions near zero get mapped to 0 (below 0.7 * mean threshold).
    """
    gamma = W.abs().mean(dim=-1, keepdim=True)
    threshold = 0.7 * gamma  # standard TWN threshold
    T = torch.zeros_like(W)
    T[W > threshold] = 1.0
    T[W < -threshold] = -1.0
    return T * gamma


def q4_quantize(W: torch.Tensor) -> torch.Tensor:
    """Simulated 4-bit quantization per row (absmax, 16 levels)."""
    scale = W.abs().amax(dim=-1, keepdim=True) / 7.0  # 4-bit: -8..7, use ±7
    scale = scale.clamp(min=1e-10)
    W_int = (W / scale).round().clamp(-8, 7)
    return W_int * scale


def measure_gradient_quant_correspondence(
    model,
    tokenizer,
    device: str,
    n_bins: int = 20,
) -> dict:
    """Core measurement: correlate gradient magnitude with quantization error."""

    # ── Step 1: Compute gradients on calibration data ────────────────
    print("  Computing gradients on calibration data...")
    model.train()  # Need gradients
    model.zero_grad()

    total_loss = 0.0
    n_tokens = 0
    for text in CALIBRATION_TEXTS:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()

        outputs = model(**inputs, labels=labels)
        loss = outputs.loss
        loss.backward()
        total_loss += loss.item() * labels.numel()
        n_tokens += labels.numel()

    avg_loss = total_loss / n_tokens
    print(f"  Calibration loss: {avg_loss:.4f} ({n_tokens} tokens)")

    # ── Step 2: Collect per-position gradient and quant error ────────
    print("  Measuring per-position gradient vs quantization error...")

    all_results = []
    per_matrix = []

    for name, param in model.named_parameters():
        if param.ndim != 2 or min(param.shape) < 64:
            continue
        if param.grad is None:
            continue

        W = param.data.float()
        G = param.grad.float()

        # Quantization errors
        W_ternary = ternary_quantize(W)
        W_q4 = q4_quantize(W)

        err_ternary = (W - W_ternary).abs()
        err_q4 = (W - W_q4).abs()
        grad_mag = G.abs()

        # Flatten for correlation
        g_flat = grad_mag.flatten().cpu().numpy()
        et_flat = err_ternary.flatten().cpu().numpy()
        eq_flat = err_q4.flatten().cpu().numpy()
        w_flat = W.abs().flatten().cpu().numpy()

        # Per-matrix Spearman rank correlation (more robust than Pearson)
        from scipy.stats import spearmanr, pearsonr

        # Sample if too large (>1M positions)
        if len(g_flat) > 1_000_000:
            rng = np.random.RandomState(42)
            idx = rng.choice(len(g_flat), 1_000_000, replace=False)
            g_s, et_s, eq_s, w_s = g_flat[idx], et_flat[idx], eq_flat[idx], w_flat[idx]
        else:
            g_s, et_s, eq_s, w_s = g_flat, et_flat, eq_flat, w_flat

        # Filter out exact zeros in gradient (uninformative)
        mask = g_s > 1e-12
        if mask.sum() < 100:
            continue

        g_m = g_s[mask]
        et_m = et_s[mask]
        eq_m = eq_s[mask]
        w_m = w_s[mask]

        r_ternary_s, p_ternary_s = spearmanr(g_m, et_m)
        r_q4_s, p_q4_s = spearmanr(g_m, eq_m)
        r_ternary_p, p_ternary_p = pearsonr(g_m, et_m)
        r_q4_p, p_q4_p = pearsonr(g_m, eq_m)

        # Also: gradient vs weight magnitude (control)
        r_grad_wmag_s, _ = spearmanr(g_m, w_m)

        # Zero-gradient fraction
        zero_grad_frac = (g_flat < 1e-10).sum() / len(g_flat)

        # Near-ternary fraction (positions where |W| is close to row mean or 0)
        gamma = W.abs().mean(dim=-1, keepdim=True)
        deviation_from_ternary = torch.min(
            W.abs(),  # distance to 0
            (W.abs() - gamma).abs(),  # distance to ±gamma
        )
        near_ternary_frac = (deviation_from_ternary < 0.1 * gamma).float().mean().item()

        entry = {
            "name": name,
            "shape": list(W.shape),
            "n_positions": int(mask.sum()),
            "zero_grad_frac": float(zero_grad_frac),
            "near_ternary_frac": float(near_ternary_frac),
            "r_ternary_spearman": float(r_ternary_s),
            "p_ternary_spearman": float(p_ternary_s),
            "r_q4_spearman": float(r_q4_s),
            "p_q4_spearman": float(p_q4_s),
            "r_ternary_pearson": float(r_ternary_p),
            "p_ternary_pearson": float(p_ternary_p),
            "r_q4_pearson": float(r_q4_p),
            "p_q4_pearson": float(p_q4_p),
            "r_grad_wmag_spearman": float(r_grad_wmag_s),
            "grad_mean": float(g_flat.mean()),
            "grad_std": float(g_flat.std()),
            "err_ternary_mean": float(et_flat.mean()),
            "err_q4_mean": float(eq_flat.mean()),
        }

        per_matrix.append(entry)
        all_results.append((g_m, et_m, eq_m, name))

        status = "✓" if r_ternary_s > 0.1 else "⚠" if r_ternary_s > 0 else "✗"
        print(f"    {status} {name:55s}  ρ_tern={r_ternary_s:+.4f}  ρ_q4={r_q4_s:+.4f}  "
              f"zero_g={zero_grad_frac:.1%}  near_T={near_ternary_frac:.1%}")

    # ── Step 3: Aggregate across all matrices ────────────────────────
    print("\n  Aggregating across all weight matrices...")

    all_g = np.concatenate([r[0] for r in all_results])
    all_et = np.concatenate([r[1] for r in all_results])
    all_eq = np.concatenate([r[2] for r in all_results])

    # Normalize per-matrix (z-score) to prevent scale differences from dominating
    all_g_z = []
    all_et_z = []
    all_eq_z = []
    for g, et, eq, _ in all_results:
        g_std = g.std()
        et_std = et.std()
        eq_std = eq.std()
        if g_std > 1e-12 and et_std > 1e-12 and eq_std > 1e-12:
            all_g_z.append((g - g.mean()) / g_std)
            all_et_z.append((et - et.mean()) / et_std)
            all_eq_z.append((eq - eq.mean()) / eq_std)

    all_g_z = np.concatenate(all_g_z)
    all_et_z = np.concatenate(all_et_z)
    all_eq_z = np.concatenate(all_eq_z)

    # Sample for aggregate correlation (may be very large)
    if len(all_g_z) > 2_000_000:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(all_g_z), 2_000_000, replace=False)
        all_g_z = all_g_z[idx]
        all_et_z = all_et_z[idx]
        all_eq_z = all_eq_z[idx]

    from scipy.stats import spearmanr, pearsonr
    agg_r_tern_s, agg_p_tern_s = spearmanr(all_g_z, all_et_z)
    agg_r_q4_s, agg_p_q4_s = spearmanr(all_g_z, all_eq_z)
    agg_r_tern_p, agg_p_tern_p = pearsonr(all_g_z, all_et_z)
    agg_r_q4_p, agg_p_q4_p = pearsonr(all_g_z, all_eq_z)

    # ── Step 4: Bin analysis ─────────────────────────────────────────
    print("  Binning by gradient magnitude...")

    # Use unnormalized for binning (more interpretable)
    if len(all_g) > 2_000_000:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(all_g), 2_000_000, replace=False)
        bin_g, bin_et, bin_eq = all_g[idx], all_et[idx], all_eq[idx]
    else:
        bin_g, bin_et, bin_eq = all_g, all_et, all_eq

    percentiles = np.linspace(0, 100, n_bins + 1)
    edges = np.percentile(bin_g, percentiles)
    bin_means_g = []
    bin_means_et = []
    bin_means_eq = []

    for i in range(n_bins):
        mask = (bin_g >= edges[i]) & (bin_g < edges[i + 1] if i < n_bins - 1 else True)
        if mask.sum() == 0:
            continue
        bin_means_g.append(float(bin_g[mask].mean()))
        bin_means_et.append(float(bin_et[mask].mean()))
        bin_means_eq.append(float(bin_eq[mask].mean()))

    # Monotonicity test: is quant error monotonically increasing with gradient?
    tern_increases = sum(1 for i in range(1, len(bin_means_et))
                        if bin_means_et[i] > bin_means_et[i-1])
    q4_increases = sum(1 for i in range(1, len(bin_means_eq))
                      if bin_means_eq[i] > bin_means_eq[i-1])
    n_transitions = len(bin_means_et) - 1

    # ── Step 5: Component-type breakdown ─────────────────────────────
    ffn_entries = [e for e in per_matrix if 'mlp' in e['name'] or 'ffn' in e['name']]
    attn_entries = [e for e in per_matrix if 'attention' in e['name'] or 'self_attn' in e['name']
                    or 'q_proj' in e['name'] or 'k_proj' in e['name']
                    or 'v_proj' in e['name'] or 'o_proj' in e['name']]

    ffn_r = np.mean([e['r_ternary_spearman'] for e in ffn_entries]) if ffn_entries else 0
    attn_r = np.mean([e['r_ternary_spearman'] for e in attn_entries]) if attn_entries else 0

    # ══════════════════════════════════════════════════════════════════
    # Results
    # ══════════════════════════════════════════════════════════════════

    summary = {
        "model": model.config._name_or_path,
        "n_matrices": len(per_matrix),
        "n_positions_total": int(len(all_g)),
        "calibration_loss": float(avg_loss),
        "calibration_tokens": int(n_tokens),
        "aggregate": {
            "ternary_spearman_r": float(agg_r_tern_s),
            "ternary_spearman_p": float(agg_p_tern_s),
            "q4_spearman_r": float(agg_r_q4_s),
            "q4_spearman_p": float(agg_p_q4_s),
            "ternary_pearson_r": float(agg_r_tern_p),
            "q4_pearson_r": float(agg_r_q4_p),
        },
        "bins": {
            "gradient_means": bin_means_g,
            "ternary_error_means": bin_means_et,
            "q4_error_means": bin_means_eq,
            "ternary_monotone_frac": tern_increases / max(n_transitions, 1),
            "q4_monotone_frac": q4_increases / max(n_transitions, 1),
        },
        "by_component": {
            "ffn_mean_r": float(ffn_r),
            "attn_mean_r": float(attn_r),
            "ffn_n": len(ffn_entries),
            "attn_n": len(attn_entries),
        },
        "per_matrix": per_matrix,
    }

    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="EleutherAI/pythia-160m-deduped")
    p.add_argument("--device", default="cpu")
    p.add_argument("--bins", type=int, default=20)
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  GRADIENT → QUANTIZATION ERROR CORRESPONDENCE")
    print(f"  Prediction: |∇L| correlates with |W - Q(W)|")
    print(f"  (near-zero gradient = irreducible = already ternary)")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    print(f"  Loading {args.model}...")
    # Use float16 for large models (>1B params), float32 for small
    dtype = torch.float16 if "8B" in args.model or "14B" in args.model or "13B" in args.model or "7B" in args.model else torch.float32
    print(f"  Using dtype: {dtype}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    t0 = time.time()
    results = measure_gradient_quant_correspondence(model, tokenizer, args.device, args.bins)
    elapsed = time.time() - t0

    # ── Print results ────────────────────────────────────────────────
    agg = results["aggregate"]
    bins = results["bins"]
    comp = results["by_component"]

    print(f"\n{'='*70}")
    print(f"  RESULTS — {args.model}")
    print(f"  {results['n_matrices']} matrices, {results['n_positions_total']:,} positions")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*70}")

    print(f"\n  ── AGGREGATE CORRELATION ──────────────────────────────")
    print(f"  Ternary:  Spearman ρ = {agg['ternary_spearman_r']:+.4f}  (p = {agg['ternary_spearman_p']:.2e})")
    print(f"            Pearson  r = {agg['ternary_pearson_r']:+.4f}")
    print(f"  Q4:       Spearman ρ = {agg['q4_spearman_r']:+.4f}  (p = {agg['q4_spearman_p']:.2e})")
    print(f"            Pearson  r = {agg['q4_pearson_r']:+.4f}")

    prediction = "✅ CONFIRMED" if agg['ternary_spearman_r'] > 0.05 and agg['ternary_spearman_p'] < 0.001 else \
                 "⚠ WEAK" if agg['ternary_spearman_r'] > 0 else "❌ REFUTED"
    print(f"\n  Prediction (|∇L| ↔ |W-Q(W)|): {prediction}")

    print(f"\n  ── BY COMPONENT ──────────────────────────────────────")
    print(f"  FFN matrices:       mean ρ = {comp['ffn_mean_r']:+.4f}  (n={comp['ffn_n']})")
    print(f"  Attention matrices: mean ρ = {comp['attn_mean_r']:+.4f}  (n={comp['attn_n']})")

    print(f"\n  ── BINNED ANALYSIS ({len(bins['gradient_means'])} bins) ────────────────")
    print(f"  Ternary error monotonicity: {bins['ternary_monotone_frac']:.1%} "
          f"of bins show increasing error with gradient")
    print(f"  Q4 error monotonicity:      {bins['q4_monotone_frac']:.1%}")
    print()
    print(f"  {'Bin':>4}  {'|∇L| mean':>12}  {'Tern err':>10}  {'Q4 err':>10}  {'Trend':>6}")
    print(f"  {'─'*4}  {'─'*12}  {'─'*10}  {'─'*10}  {'─'*6}")

    for i, (g, et, eq) in enumerate(zip(
        bins['gradient_means'], bins['ternary_error_means'], bins['q4_error_means']
    )):
        trend = "↑" if i > 0 and et > bins['ternary_error_means'][i-1] else "↓" if i > 0 else " "
        print(f"  {i+1:>4}  {g:>12.6f}  {et:>10.6f}  {eq:>10.6f}  {trend:>6}")

    # Ratio of highest to lowest bin
    if bins['ternary_error_means']:
        ratio = bins['ternary_error_means'][-1] / max(bins['ternary_error_means'][0], 1e-12)
        print(f"\n  Ternary error ratio (highest/lowest gradient bin): {ratio:.2f}×")

    # ── Save ─────────────────────────────────────────────────────────
    out_dir = Path("results/gradient-quant-correspondence")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
