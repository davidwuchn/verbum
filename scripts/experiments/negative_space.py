#!/usr/bin/env python3
"""The Negative Space: is the missing information in the zero pattern?

WE PROVED:
  - Signs carry 1/φ of information
  - Per-row magnitude variation carries ~nothing (constant γ works)
  - Gap from 0.88 to 0.99+ is NOT in magnitude scaling

HYPOTHESIS: The missing information is in WHICH weights are zero.
The zero pattern (negative space) is the holographic phase information.

EXPERIMENTS:
  1. Zero mask quality — compare magnitude-threshold zeros vs random zeros
     vs optimal zeros (greedy selection). How much does the mask matter?
  2. Zero mask information content — how many bits are in the mask itself?
  3. Per-weight ternary vs per-weight binary (sign only, no zeros) —
     is the zero mask helping or hurting?
  4. The Q4 soft boundary — what are Q4's near-zero weights doing?
     Bucket Q4 weights by magnitude, see where the information lives.
  5. Zero mask structure — is the mask self-similar across layers?
     Does it follow φ? Is it predictable from the gate?
  6. Optimal zero rate — sweep zero_rate from 0% to 50%.
     Where's the sweet spot, and is it 1/φ² ≈ 38.2%?

Usage:
  uv run python scripts/experiments/negative_space.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
from scipy import stats as scipy_stats

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def ternary_reconstruct(W: torch.Tensor, zero_mask: torch.Tensor,
                        use_constant_gamma: bool = False) -> tuple[float, torch.Tensor]:
    """Reconstruct with given zero mask and measure cosine.

    Returns (cosine, gamma_per_row).
    """
    W_f32 = W.float()
    T = torch.sign(W_f32)
    T[zero_mask] = 0

    # Per-row gamma
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt

    if use_constant_gamma:
        gamma = torch.full_like(gamma, gamma.mean().item())

    W_recon = gamma.unsqueeze(1) * T
    w_flat = W_f32.flatten()
    r_flat = W_recon.flatten()
    cos = torch.dot(w_flat, r_flat) / (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)
    return cos.item(), gamma


def run_experiment(model_id: str, layer_indices: list[int]):
    log("=" * 72)
    log("THE NEGATIVE SPACE EXPERIMENT")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"φ = {PHI:.6f}, 1/φ = {INV_PHI:.6f}, 1/φ² = {INV_PHI**2:.6f}")
    log()

    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"Loaded {model_id}")

    weight_types = ['gate_proj', 'down_proj']

    for wtype in weight_types:
        log(f"\n{'═' * 72}")
        log(f"WEIGHT TYPE: {wtype}")
        log(f"{'═' * 72}")

        for layer_idx in layer_indices:
            layer = model.model.layers[layer_idx]
            W = getattr(layer.mlp, wtype).weight.data
            W_f32 = W.float().cpu()
            m, n = W_f32.shape
            abs_W = W_f32.abs()

            log(f"\n  Layer {layer_idx}: {m}×{n}")

            # ── Exp 1: Zero mask quality comparison ─────────────
            log(f"\n    Exp 1 — Zero mask quality (at 35% zero rate):")

            total_weights = m * n
            n_zeros = int(total_weights * 0.35)

            # Method A: Per-row magnitude threshold (standard)
            thresholds = torch.quantile(abs_W, 0.35, dim=1, keepdim=True)
            mask_magnitude = abs_W < thresholds
            cos_mag, _ = ternary_reconstruct(W, mask_magnitude)
            cos_mag_const, _ = ternary_reconstruct(W, mask_magnitude, use_constant_gamma=True)

            # Method B: Global magnitude threshold
            # torch.quantile can't handle very large tensors, use numpy
            global_threshold = float(np.percentile(abs_W.numpy(), 35))
            mask_global = abs_W < global_threshold
            actual_zero_rate_global = mask_global.float().mean().item()
            cos_global, _ = ternary_reconstruct(W, mask_global)
            cos_global_const, _ = ternary_reconstruct(W, mask_global, use_constant_gamma=True)

            # Method C: Random zeros (same rate)
            n_zeros_per_row = (mask_magnitude.sum(dim=1)).float().mean().item()
            mask_random = torch.zeros_like(abs_W, dtype=torch.bool)
            for row in range(m):
                nz = int(n_zeros_per_row)
                indices = torch.randperm(n)[:nz]
                mask_random[row, indices] = True
            cos_random, _ = ternary_reconstruct(W, mask_random)
            cos_random_const, _ = ternary_reconstruct(W, mask_random, use_constant_gamma=True)

            # Method D: No zeros at all (pure sign)
            mask_none = torch.zeros_like(abs_W, dtype=torch.bool)
            cos_nosign, _ = ternary_reconstruct(W, mask_none)
            cos_nosign_const, _ = ternary_reconstruct(W, mask_none, use_constant_gamma=True)

            # Method E: Optimal greedy zeros — zero the weights that
            # INCREASE cosine the most when zeroed
            # (Too expensive for full matrix, sample rows)
            # Instead: zero weights where |w_i,j| < median(row) AND
            # the weight has opposite sign to its neighbors' mean
            # Actually let's just compare error: zero where W_recon error is highest
            # First pass: reconstruct with no zeros
            T_full = torch.sign(W_f32)
            wt_full = (W_f32 * T_full).sum(dim=1)
            tt_full = (T_full * T_full).sum(dim=1).clamp(min=1)
            gamma_full = wt_full / tt_full
            W_recon_full = gamma_full.unsqueeze(1) * T_full
            error = (W_f32 - W_recon_full).abs()
            # Zero the weights with HIGHEST error (they're poorly represented)
            error_flat = error.flatten()
            _, top_error_idx = error_flat.topk(n_zeros)
            mask_error = torch.zeros(total_weights, dtype=torch.bool)
            mask_error[top_error_idx] = True
            mask_error = mask_error.reshape(m, n)
            cos_error, _ = ternary_reconstruct(W, mask_error)
            cos_error_const, _ = ternary_reconstruct(W, mask_error, use_constant_gamma=True)

            log(f"      Per-row magnitude:    cos={cos_mag:.6f}  (const γ: {cos_mag_const:.6f})")
            log(f"      Global magnitude:     cos={cos_global:.6f}  (const γ: {cos_global_const:.6f})")
            log(f"      Random zeros:         cos={cos_random:.6f}  (const γ: {cos_random_const:.6f})")
            log(f"      No zeros (pure sign): cos={cos_nosign:.6f}  (const γ: {cos_nosign_const:.6f})")
            log(f"      Error-based zeros:    cos={cos_error:.6f}  (const γ: {cos_error_const:.6f})")

            # ── Exp 2: Zero rate sweep ──────────────────────────
            log(f"\n    Exp 2 — Zero rate sweep:")
            log(f"      {'rate':>6s} {'cos_perrow':>12s} {'cos_const':>12s} {'Δ':>8s}")
            zero_rates = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35,
                          1/PHI**2, 0.40, 0.45, 0.50, 0.55, 0.60, 1/PHI]
            best_rate = 0
            best_cos = 0
            best_rate_const = 0
            best_cos_const = 0
            for zr in sorted(zero_rates):
                if zr >= 1.0:
                    continue
                thresh = torch.quantile(abs_W, zr, dim=1, keepdim=True) if zr > 0 else torch.zeros(m, 1)
                mask = abs_W < thresh if zr > 0 else torch.zeros_like(abs_W, dtype=torch.bool)
                c, _ = ternary_reconstruct(W, mask)
                c_const, _ = ternary_reconstruct(W, mask, use_constant_gamma=True)
                marker = ""
                if abs(zr - INV_PHI**2) < 0.005:
                    marker = " ← 1/φ²"
                elif abs(zr - INV_PHI) < 0.005:
                    marker = " ← 1/φ"
                elif abs(zr - 0.35) < 0.005:
                    marker = " ← current"
                log(f"      {zr:6.3f} {c:12.6f} {c_const:12.6f} {c - c_const:8.4f}{marker}")
                if c_const > best_cos_const:
                    best_cos_const = c_const
                    best_rate_const = zr
                if c > best_cos:
                    best_cos = c
                    best_rate = zr
            log(f"      Best (per-row γ):  rate={best_rate:.3f} cos={best_cos:.6f}")
            log(f"      Best (constant γ): rate={best_rate_const:.3f} cos={best_cos_const:.6f}")

            # ── Exp 3: Zero mask correlation across layers ──────
            # (Only store, compare after loop)

            # ── Exp 4: What do Q4's near-zero weights encode? ───
            log(f"\n    Exp 4 — Weight magnitude histogram (information density):")
            # Bucket weights by magnitude and measure how much each bucket
            # contributes to the Frobenius norm
            abs_flat = abs_W.flatten().numpy()
            percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]
            thresholds = np.percentile(abs_flat, percentiles)

            log(f"      {'Bucket':>12s} {'%weights':>10s} {'%energy':>10s} {'energy/weight':>14s}")
            total_energy = (abs_flat ** 2).sum()
            for i in range(len(percentiles) - 1):
                lo, hi = thresholds[i], thresholds[i+1]
                mask_bucket = (abs_flat >= lo) & (abs_flat < hi)
                n_in_bucket = mask_bucket.sum()
                energy_in_bucket = (abs_flat[mask_bucket] ** 2).sum()
                pct_weights = n_in_bucket / len(abs_flat) * 100
                pct_energy = energy_in_bucket / total_energy * 100
                energy_per = pct_energy / pct_weights if pct_weights > 0 else 0
                log(f"      {percentiles[i]:3d}-{percentiles[i+1]:3d}%ile "
                    f"{pct_weights:10.1f}% {pct_energy:10.2f}%  {energy_per:14.2f}")

            # ── Exp 5: Information in sign-changes near zero ────
            log(f"\n    Exp 5 — Sign stability near zero:")
            # For weights near the zero threshold, how stable are the signs?
            # Compare: sign(W) at the threshold boundary vs. what the
            # neighbors' signs predict
            row_medians = abs_W.median(dim=1).values
            near_threshold = abs_W < row_medians.unsqueeze(1) * 1.2
            far_from_threshold = abs_W > row_medians.unsqueeze(1) * 2.0

            # For "near threshold" weights: how often does the sign match
            # the sign of the row mean?
            row_means = W_f32.mean(dim=1, keepdim=True)
            sign_agreement_near = ((W_f32.sign() == row_means.sign()) & near_threshold).float().sum() / near_threshold.float().sum()
            sign_agreement_far = ((W_f32.sign() == row_means.sign()) & far_from_threshold).float().sum() / far_from_threshold.float().sum()

            log(f"      Sign agrees with row mean (near zero): {sign_agreement_near:.4f}")
            log(f"      Sign agrees with row mean (far zero):  {sign_agreement_far:.4f}")

            # What fraction of near-zero weights have |w| < γ/10?
            # These are the weights where ternary → 0 but Q4 → small nonzero
            gamma_mean = (W_f32.abs().mean(dim=1) * 0.0172).mean().item()
            very_small = (abs_W < gamma_mean * 0.1).float().mean().item()
            small = (abs_W < gamma_mean).float().mean().item()
            log(f"      Fraction |w| < γ/10: {very_small:.4f}")
            log(f"      Fraction |w| < γ:    {small:.4f}")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    parser.add_argument("--zero-rate", type=float, default=0.35)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices)


if __name__ == "__main__":
    main()
