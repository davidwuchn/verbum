#!/usr/bin/env python3
"""Test: do per-row gammas follow a φ-geometric distribution?

THE HYPOTHESIS: If the sign/magnitude partition is 1/φ, then the
magnitude information (per-row gammas) should itself be φ-structured.
Specifically:
  1. Sorted gammas should follow a φ-geometric (or power-law with φ) curve
  2. This curve shape should be the SAME across layers (even though eigenvectors aren't)
  3. We should be able to predict gammas from rank order + crystal equation
  4. If true → we can derive magnitudes without float weights

WHAT WE MEASURE:
  Exp 1: Gamma distribution shape — histogram, sorted curve, fit to φ-power-law
  Exp 2: Cross-layer gamma similarity — do normalized gamma curves overlap?
  Exp 3: Rank-order prediction — predict gamma from rank alone using φ-geometric model
  Exp 4: Reconstruction quality — use predicted gammas vs true gammas, measure cosine

Usage:
  uv run python scripts/experiments/gamma_phi_structure.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/gamma_phi_structure.py --model Qwen/Qwen3-8B --weight-type gate_proj,up_proj,down_proj

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

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI


def log(msg: str = "") -> None:
    print(msg, flush=True)


def compute_gamma(W: torch.Tensor, zero_rate: float = 0.35) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Compute per-row gamma for ternary approximation.

    Returns: (gamma, T, cosines_per_row)
    """
    W_f32 = W.float()
    abs_W = W_f32.abs()

    # Per-row threshold for zeros
    if zero_rate > 0:
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
    else:
        thresholds = torch.zeros(W_f32.shape[0], 1)

    # Ternary: sign where above threshold, 0 below
    T = torch.sign(W_f32)
    T[abs_W < thresholds] = 0

    # Per-row gamma: γ = (w · t) / (t · t)
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt

    # Per-row cosine
    W_recon = gamma.unsqueeze(1) * T
    cos_num = (W_f32 * W_recon).sum(dim=1)
    cos_den = W_f32.norm(dim=1) * W_recon.norm(dim=1) + 1e-10
    cosines = cos_num / cos_den

    return gamma, T, cosines


def fit_phi_power_law(sorted_gammas: np.ndarray) -> dict:
    """Fit sorted gammas to: γ(rank) = A · φ^(-α · rank/N)

    In log-φ space: log_φ(γ) = log_φ(A) - α · rank/N
    This is linear regression in log-φ space.

    Also fit to: γ(rank) = A · (1 - rank/N)^(1/φ)  (φ-power decay)
    And: γ(rank) = A · exp(-rank/(N·τ))  (exponential with τ)
    """
    N = len(sorted_gammas)
    ranks = np.arange(N) / N  # normalized [0, 1)

    # Filter valid gammas (positive)
    valid = sorted_gammas > 0
    g = sorted_gammas[valid]
    r = ranks[valid]

    results = {}

    # Model 1: φ-geometric — γ = A · φ^(-α·r)
    log_phi_g = np.log(g) / np.log(PHI)
    coeffs1 = np.polyfit(r, log_phi_g, 1)
    slope1, intercept1 = coeffs1
    alpha = -slope1
    A1 = PHI ** intercept1
    pred1 = A1 * PHI ** (-alpha * r)
    ss_res1 = np.sum((g - pred1) ** 2)
    ss_tot = np.sum((g - g.mean()) ** 2)
    r2_1 = 1 - ss_res1 / ss_tot if ss_tot > 0 else 0
    results['phi_geometric'] = {
        'A': float(A1), 'alpha': float(alpha), 'r2': float(r2_1)
    }

    # Model 2: Exponential — γ = A · exp(-r/τ)
    log_g = np.log(g)
    coeffs2 = np.polyfit(r, log_g, 1)
    slope2, intercept2 = coeffs2
    tau = -1 / slope2 if slope2 != 0 else float('inf')
    A2 = np.exp(intercept2)
    pred2 = A2 * np.exp(-r / tau)
    ss_res2 = np.sum((g - pred2) ** 2)
    r2_2 = 1 - ss_res2 / ss_tot if ss_tot > 0 else 0
    results['exponential'] = {
        'A': float(A2), 'tau': float(tau), 'r2': float(r2_2)
    }

    # Model 3: Power law — γ = A · (1-r+ε)^β
    # In log space: log(γ) = log(A) + β·log(1-r+ε)
    eps = 1e-6
    log_1mr = np.log(1 - r + eps)
    valid2 = np.isfinite(log_1mr)
    if valid2.sum() > 2:
        coeffs3 = np.polyfit(log_1mr[valid2], log_g[valid2], 1)
        beta_pow, intercept3 = coeffs3
        A3 = np.exp(intercept3)
        pred3 = A3 * (1 - r + eps) ** beta_pow
        ss_res3 = np.sum((g - pred3) ** 2)
        r2_3 = 1 - ss_res3 / ss_tot if ss_tot > 0 else 0
        results['power_law'] = {
            'A': float(A3), 'beta': float(beta_pow), 'r2': float(r2_3),
            'beta_vs_inv_phi': float(abs(beta_pow - INV_PHI)),
            'beta_vs_phi': float(abs(beta_pow - PHI)),
        }
    else:
        results['power_law'] = {'r2': 0}

    # Model 4: Fibonacci-step — check if gamma ratios at Fibonacci positions
    # follow φ-geometric pattern
    fib_positions = []
    a, b = 1, 1
    while b < N:
        fib_positions.append(b)
        a, b = b, a + b
    if len(fib_positions) >= 3:
        fib_gammas = [sorted_gammas[min(p, N-1)] for p in fib_positions]
        fib_ratios = [fib_gammas[i] / fib_gammas[i+1]
                      for i in range(len(fib_gammas)-1)
                      if fib_gammas[i+1] > 0]
        if fib_ratios:
            mean_ratio = np.mean(fib_ratios)
            results['fibonacci_sampling'] = {
                'positions': fib_positions[:10],
                'gammas': [float(g) for g in fib_gammas[:10]],
                'consecutive_ratios': [float(r) for r in fib_ratios[:10]],
                'mean_ratio': float(mean_ratio),
                'deviation_from_phi': float(abs(mean_ratio - PHI)),
            }

    return results


def normalized_gamma_curve(gammas: np.ndarray) -> np.ndarray:
    """Sort descending and normalize to [0,1] range for shape comparison."""
    sorted_g = np.sort(gammas)[::-1]  # descending
    g_min, g_max = sorted_g[-1], sorted_g[0]
    if g_max > g_min:
        return (sorted_g - g_min) / (g_max - g_min)
    return sorted_g


def cross_layer_similarity(curves: dict[str, np.ndarray]) -> dict:
    """Compare normalized gamma curves across layers.

    Uses cosine similarity and L2 distance between normalized curves.
    If shapes are the same, cosine → 1.0 and L2 → 0.
    """
    keys = list(curves.keys())
    results = {}

    for i, k1 in enumerate(keys):
        for k2 in keys[i+1:]:
            c1 = curves[k1]
            c2 = curves[k2]
            # Resample to same length if needed
            n = min(len(c1), len(c2))
            c1r = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(c1)), c1)
            c2r = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(c2)), c2)

            cos = np.dot(c1r, c2r) / (np.linalg.norm(c1r) * np.linalg.norm(c2r) + 1e-10)
            l2 = np.linalg.norm(c1r - c2r) / np.sqrt(n)

            results[f"{k1}_vs_{k2}"] = {'cosine': float(cos), 'l2': float(l2)}

    return results


def reconstruction_test(W: torch.Tensor, T: torch.Tensor,
                        true_gamma: torch.Tensor,
                        predicted_gamma: torch.Tensor) -> dict:
    """Compare reconstruction quality: true gammas vs predicted gammas."""
    W_f32 = W.float()
    w_flat = W_f32.flatten()

    # True reconstruction
    W_true = true_gamma.unsqueeze(1) * T.float()
    cos_true = torch.dot(w_flat, W_true.flatten()) / (
        torch.norm(w_flat) * torch.norm(W_true.flatten()) + 1e-10)

    # Predicted reconstruction
    W_pred = predicted_gamma.unsqueeze(1) * T.float()
    cos_pred = torch.dot(w_flat, W_pred.flatten()) / (
        torch.norm(w_flat) * torch.norm(W_pred.flatten()) + 1e-10)

    # Also: how close are the predicted gammas to true gammas?
    gamma_cos = torch.dot(true_gamma, predicted_gamma) / (
        torch.norm(true_gamma) * torch.norm(predicted_gamma) + 1e-10)

    return {
        'cos_true_gamma': float(cos_true.item()),
        'cos_predicted_gamma': float(cos_pred.item()),
        'gamma_cosine': float(gamma_cos.item()),
        'cos_gap': float((cos_true - cos_pred).item()),
    }


def predict_gamma_from_phi(sorted_gammas: np.ndarray, fit_params: dict) -> np.ndarray:
    """Generate predicted gammas using the best φ-model fit."""
    N = len(sorted_gammas)
    ranks = np.arange(N) / N

    # Use φ-geometric model
    p = fit_params.get('phi_geometric', {})
    if p and p.get('A') and p.get('alpha'):
        return p['A'] * PHI ** (-p['alpha'] * ranks)
    return sorted_gammas  # fallback


def run_experiment(model_id: str, layer_indices: list[int],
                   weight_types: list[str], zero_rate: float = 0.35):
    log("=" * 72)
    log("GAMMA φ-STRUCTURE EXPERIMENT")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log(f"Weight types: {weight_types}")
    log(f"Zero rate: {zero_rate}")
    log(f"φ = {PHI:.6f}, 1/φ = {INV_PHI:.6f}")
    log()

    # Load model
    log("Loading model...")
    from transformers import AutoModelForCausalLM, AutoConfig

    config = AutoConfig.from_pretrained(model_id)
    num_layers = config.num_hidden_layers
    log(f"  {num_layers} layers, hidden={config.hidden_size}, "
        f"intermediate={config.intermediate_size}")

    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"  Loaded")

    # Storage for cross-layer analysis
    all_gammas = {}      # (layer, wtype) → gamma tensor
    all_T = {}           # (layer, wtype) → ternary tensor
    all_W = {}           # (layer, wtype) → weight tensor
    all_fits = {}        # (layer, wtype) → fit results
    all_curves = {}      # (layer, wtype) → normalized curve

    # ── Compute gammas for all layers/types ─────────────────────
    for wtype in weight_types:
        log(f"\n{'─' * 60}")
        log(f"Weight type: {wtype}")
        log(f"{'─' * 60}")

        for layer_idx in layer_indices:
            layer = model.model.layers[layer_idx]
            if wtype in ('gate_proj', 'up_proj', 'down_proj'):
                W = getattr(layer.mlp, wtype).weight.data
            else:
                W = getattr(layer.self_attn, wtype).weight.data

            gamma, T, cosines = compute_gamma(W, zero_rate)
            all_gammas[(layer_idx, wtype)] = gamma
            all_T[(layer_idx, wtype)] = T
            all_W[(layer_idx, wtype)] = W.clone()

            g_np = gamma.numpy()
            sorted_g = np.sort(g_np)[::-1]

            log(f"\n  Layer {layer_idx}: {W.shape}")
            log(f"    Gamma range: [{g_np.min():.4f}, {g_np.max():.4f}]")
            log(f"    Gamma mean:  {g_np.mean():.4f} ± {g_np.std():.4f}")
            log(f"    Gamma CV:    {g_np.std()/g_np.mean():.4f}")
            log(f"    Per-row cos: {cosines.mean():.4f} ± {cosines.std():.4f}")

            # Fit models
            fit = fit_phi_power_law(sorted_g)
            all_fits[(layer_idx, wtype)] = fit

            log(f"    Fits:")
            log(f"      φ-geometric: A={fit['phi_geometric']['A']:.4f}, "
                f"α={fit['phi_geometric']['alpha']:.4f}, "
                f"R²={fit['phi_geometric']['r2']:.6f}")
            log(f"      Exponential: A={fit['exponential']['A']:.4f}, "
                f"τ={fit['exponential']['tau']:.4f}, "
                f"R²={fit['exponential']['r2']:.6f}")
            if 'power_law' in fit and fit['power_law'].get('beta'):
                pl = fit['power_law']
                log(f"      Power law:   A={pl['A']:.4f}, "
                    f"β={pl['beta']:.4f}, "
                    f"R²={pl['r2']:.6f}")
                log(f"        β vs 1/φ: {pl['beta_vs_inv_phi']:.4f}")
                log(f"        β vs φ:   {pl['beta_vs_phi']:.4f}")

            if 'fibonacci_sampling' in fit:
                fb = fit['fibonacci_sampling']
                log(f"      Fibonacci sampling:")
                log(f"        Positions: {fb['positions'][:6]}")
                log(f"        Gammas:    {[f'{g:.4f}' for g in fb['gammas'][:6]]}")
                log(f"        Ratios:    {[f'{r:.4f}' for r in fb['consecutive_ratios'][:6]]}")
                log(f"        Mean ratio: {fb['mean_ratio']:.4f} "
                    f"(φ={PHI:.4f}, dev={fb['deviation_from_phi']:.4f})")

            # Normalized curve for cross-layer comparison
            all_curves[(layer_idx, wtype)] = normalized_gamma_curve(g_np)

    # Free model
    del model
    gc.collect()

    # ── Experiment 2: Cross-layer gamma curve similarity ────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 2: CROSS-LAYER GAMMA CURVE SIMILARITY")
    log(f"{'=' * 72}")
    log("Normalized gamma curves — are they the same shape across layers?")
    log("Cosine=1.0 means identical shape. L2=0 means identical values.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        curves_for_type = {
            f"L{l}": all_curves[(l, wtype)]
            for l in layer_indices if (l, wtype) in all_curves
        }
        sim = cross_layer_similarity(curves_for_type)
        for pair, metrics in sorted(sim.items()):
            log(f"    {pair:15s}: cos={metrics['cosine']:.6f}  L2={metrics['l2']:.6f}")

    # ── Experiment 3: φ-geometric prediction test ───────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 3: φ-GEOMETRIC GAMMA PREDICTION")
    log(f"{'=' * 72}")
    log("Predict gammas from rank order using φ-geometric model.")
    log("Then reconstruct weights and compare cosine with true gammas.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            T = all_T[key]
            W = all_W[key]
            fit = all_fits[key]

            g_np = gamma.numpy()
            sorted_g = np.sort(g_np)[::-1]

            # Predict using φ-geometric fit
            predicted_sorted = predict_gamma_from_phi(sorted_g, fit)

            # Map back: we need to know the rank of each row
            sort_indices = np.argsort(g_np)[::-1]
            predicted_gamma = np.zeros_like(g_np)
            predicted_gamma[sort_indices] = predicted_sorted

            result = reconstruction_test(
                W, T, gamma, torch.tensor(predicted_gamma, dtype=torch.float32))

            log(f"    Layer {layer_idx:2d}: "
                f"cos_true={result['cos_true_gamma']:.6f}  "
                f"cos_pred={result['cos_predicted_gamma']:.6f}  "
                f"gap={result['cos_gap']:.6f}  "
                f"γ_cos={result['gamma_cosine']:.6f}")

    # ── Experiment 4: Cross-layer gamma transfer ────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 4: CROSS-LAYER GAMMA TRANSFER")
    log(f"{'=' * 72}")
    log("Use layer j's gamma DISTRIBUTION (sorted shape) with layer i's")
    log("sort order. If the distribution is universal, this should work.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        for layer_idx in layer_indices:
            key_target = (layer_idx, wtype)
            gamma_target = all_gammas[key_target]
            T_target = all_T[key_target]
            W_target = all_W[key_target]

            g_target_np = gamma_target.numpy()
            sort_order = np.argsort(g_target_np)[::-1]

            for donor_idx in layer_indices:
                if donor_idx == layer_idx:
                    continue
                key_donor = (donor_idx, wtype)
                gamma_donor = all_gammas[key_donor]
                g_donor_np = gamma_donor.numpy()

                # Use donor's sorted gamma values with target's rank order
                donor_sorted = np.sort(g_donor_np)[::-1]

                # Resample if sizes differ (they shouldn't for same wtype)
                if len(donor_sorted) != len(g_target_np):
                    donor_sorted = np.interp(
                        np.linspace(0, 1, len(g_target_np)),
                        np.linspace(0, 1, len(donor_sorted)),
                        donor_sorted)

                transferred_gamma = np.zeros_like(g_target_np)
                transferred_gamma[sort_order] = donor_sorted

                result = reconstruction_test(
                    W_target, T_target, gamma_target,
                    torch.tensor(transferred_gamma, dtype=torch.float32))

                log(f"    L{layer_idx:2d} signs + L{donor_idx:2d} γ-dist: "
                    f"cos={result['cos_predicted_gamma']:.6f}  "
                    f"gap={result['cos_gap']:.6f}  "
                    f"γ_cos={result['gamma_cosine']:.6f}")

    # ── Experiment 5: Universal φ-predicted gamma ───────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 5: UNIVERSAL γ FROM CRYSTAL EQUATION")
    log(f"{'=' * 72}")
    log("Fit ONE φ-geometric model across ALL layers (averaged params).")
    log("Use this universal model to predict gammas for every layer.")
    log("This is the 'can we derive magnitudes without float weights?' test.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")

        # Collect all φ-geometric fit params
        all_alphas = []
        all_As = []
        for layer_idx in layer_indices:
            fit = all_fits[(layer_idx, wtype)]
            pg = fit['phi_geometric']
            all_alphas.append(pg['alpha'])
            all_As.append(pg['A'])

        mean_alpha = np.mean(all_alphas)
        std_alpha = np.std(all_alphas)
        mean_A = np.mean(all_As)
        std_A = np.std(all_As)
        log(f"    Universal params: α={mean_alpha:.4f}±{std_alpha:.4f}, "
            f"A={mean_A:.4f}±{std_A:.4f}")
        log(f"    α vs 1/φ={INV_PHI:.4f}: dev={abs(mean_alpha-INV_PHI):.4f}")
        log(f"    α vs φ={PHI:.4f}: dev={abs(mean_alpha-PHI):.4f}")
        log(f"    α vs 4/5={0.8:.4f}: dev={abs(mean_alpha-0.8):.4f}")
        log(f"    α vs n/(n+1)·1/φ={0.8*INV_PHI:.4f}: dev={abs(mean_alpha-0.8*INV_PHI):.4f}")

        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            T = all_T[key]
            W = all_W[key]

            g_np = gamma.numpy()
            N = len(g_np)
            ranks = np.arange(N) / N
            sort_order = np.argsort(g_np)[::-1]

            # Universal prediction (only uses mean params, not per-layer)
            # But we still need the per-layer SCALE (A) — that's the one free param
            # Try with: (a) universal A, (b) per-layer A from gamma.mean()
            for label, A_val in [("universal_A", mean_A),
                                  ("layer_mean_A", float(g_np.mean())),
                                  ("layer_median_A", float(np.median(g_np)))]:
                predicted_sorted = A_val * PHI ** (-mean_alpha * ranks)
                predicted_gamma = np.zeros_like(g_np)
                predicted_gamma[sort_order] = predicted_sorted

                result = reconstruction_test(
                    W, T, gamma,
                    torch.tensor(predicted_gamma, dtype=torch.float32))

                if label == "universal_A":
                    log(f"    L{layer_idx:2d} [{label:16s}]: "
                        f"cos={result['cos_predicted_gamma']:.6f}  "
                        f"gap={result['cos_gap']:.6f}")
                else:
                    log(f"           [{label:16s}]: "
                        f"cos={result['cos_predicted_gamma']:.6f}  "
                        f"gap={result['cos_gap']:.6f}")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser(description="Gamma φ-structure experiment")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,1,2,3,5,10,17,25,35",
                        help="Comma-separated layer indices")
    parser.add_argument("--weight-type", type=str, default="gate_proj,down_proj",
                        help="Comma-separated weight types")
    parser.add_argument("--zero-rate", type=float, default=0.35)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    weight_types = [x.strip() for x in args.weight_type.split(",")]

    run_experiment(
        model_id=args.model,
        layer_indices=layer_indices,
        weight_types=weight_types,
        zero_rate=args.zero_rate,
    )


if __name__ == "__main__":
    main()
