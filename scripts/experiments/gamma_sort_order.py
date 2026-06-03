#!/usr/bin/env python3
"""Inspect the gamma sort order: which rows get big gammas and why?

The distribution is universal (α ≈ (4/5)·(1/φ)). The only unknown
is which rows get assigned which gamma values. If this assignment
has structure, we can derive it.

WHAT WE INSPECT:
  1. Sort order correlation across layers — do the same row indices
     get big gammas in every layer?
  2. Sort order vs row properties — does gamma rank correlate with
     row norm, row variance, row sparsity, or row index?
  3. Sort order across weight types — does gate_proj row k's gamma
     predict up_proj row k's gamma?
  4. Visualization — heatmap of gamma values by (layer, row_index)

Usage:
  uv run python scripts/experiments/gamma_sort_order.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time
from pathlib import Path

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
from scipy import stats

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def compute_gamma(W: torch.Tensor, zero_rate: float = 0.35) -> torch.Tensor:
    W_f32 = W.float()
    abs_W = W_f32.abs()
    if zero_rate > 0:
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
    else:
        thresholds = torch.zeros(W_f32.shape[0], 1)
    T = torch.sign(W_f32)
    T[abs_W < thresholds] = 0
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt
    return gamma


def compute_row_properties(W: torch.Tensor) -> dict:
    """Compute structural properties of each row."""
    W_f32 = W.float()
    abs_W = W_f32.abs()

    return {
        'row_norm': W_f32.norm(dim=1).numpy(),
        'row_mean_abs': abs_W.mean(dim=1).numpy(),
        'row_std': W_f32.std(dim=1).numpy(),
        'row_max': abs_W.max(dim=1).values.numpy(),
        'row_kurtosis': ((W_f32 - W_f32.mean(dim=1, keepdim=True))**4).mean(dim=1).numpy() /
                        (W_f32.var(dim=1)**2 + 1e-10).numpy(),
        'row_sparsity': (abs_W < 0.001).float().mean(dim=1).numpy(),
        'row_sign_balance': W_f32.sign().mean(dim=1).abs().numpy(),
        'row_index': np.arange(W_f32.shape[0]),
    }


def run_experiment(model_id: str, layer_indices: list[int], zero_rate: float = 0.35):
    log("=" * 72)
    log("GAMMA SORT ORDER INSPECTION")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log()

    from transformers import AutoModelForCausalLM, AutoConfig
    config = AutoConfig.from_pretrained(model_id)
    num_layers = config.num_hidden_layers

    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"Loaded {model_id} ({num_layers} layers)")

    weight_types = ['gate_proj', 'up_proj', 'down_proj']

    # Collect gammas and ranks for all layers/types
    all_gammas = {}
    all_ranks = {}
    all_props = {}

    for layer_idx in layer_indices:
        layer = model.model.layers[layer_idx]
        for wtype in weight_types:
            if wtype in ('gate_proj', 'up_proj', 'down_proj'):
                W = getattr(layer.mlp, wtype).weight.data
            else:
                W = getattr(layer.self_attn, wtype).weight.data

            gamma = compute_gamma(W, zero_rate)
            rank_order = torch.argsort(gamma, descending=True).numpy()
            # rank[i] = the rank of row i (0 = biggest gamma)
            ranks = np.empty_like(rank_order)
            ranks[rank_order] = np.arange(len(rank_order))

            all_gammas[(layer_idx, wtype)] = gamma.numpy()
            all_ranks[(layer_idx, wtype)] = ranks
            all_props[(layer_idx, wtype)] = compute_row_properties(W)

    del model
    gc.collect()

    # ── Exp 1: Sort order correlation across layers ─────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 1: RANK CORRELATION ACROSS LAYERS (same weight type)")
    log(f"{'=' * 72}")
    log("Spearman ρ between gamma rank orderings at different layers.")
    log("ρ=1.0: same rows always get big gammas. ρ=0: no correlation.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        layers_avail = [l for l in layer_indices if (l, wtype) in all_ranks]
        n_rows = len(all_ranks[(layers_avail[0], wtype)])
        log(f"    ({n_rows} rows)")

        for i, l1 in enumerate(layers_avail):
            for l2 in layers_avail[i+1:]:
                r1 = all_ranks[(l1, wtype)]
                r2 = all_ranks[(l2, wtype)]
                rho, pval = stats.spearmanr(r1, r2)
                log(f"    L{l1:2d} vs L{l2:2d}: ρ={rho:.4f}  p={pval:.2e}")

    # ── Exp 2: Rank correlation across weight types (same layer) ─
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 2: RANK CORRELATION ACROSS WEIGHT TYPES (same layer)")
    log(f"{'=' * 72}")
    log("Does gate_proj row k having a big gamma predict up_proj row k?")

    for layer_idx in layer_indices:
        log(f"\n  Layer {layer_idx}:")
        types_avail = [wt for wt in weight_types if (layer_idx, wt) in all_ranks]
        for i, wt1 in enumerate(types_avail):
            for wt2 in types_avail[i+1:]:
                r1 = all_ranks[(layer_idx, wt1)]
                r2 = all_ranks[(layer_idx, wt2)]
                if len(r1) == len(r2):
                    rho, pval = stats.spearmanr(r1, r2)
                    log(f"    {wt1:10s} vs {wt2:10s}: ρ={rho:.4f}  p={pval:.2e}")
                else:
                    # gate/up are (intermediate, hidden), down is (hidden, intermediate)
                    # Can't directly compare ranks — different dimensions
                    log(f"    {wt1:10s} vs {wt2:10s}: SKIP (different row counts: "
                        f"{len(r1)} vs {len(r2)})")

    # ── Exp 3: Gamma vs row structural properties ───────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 3: GAMMA vs ROW STRUCTURAL PROPERTIES")
    log(f"{'=' * 72}")
    log("Spearman correlation between gamma and various row metrics.")

    prop_names = ['row_norm', 'row_mean_abs', 'row_std', 'row_max',
                  'row_kurtosis', 'row_sparsity', 'row_sign_balance', 'row_index']

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        log(f"    {'Layer':>6s}", end="")
        for pname in prop_names:
            log(f"  {pname:>14s}", end="")
        log()
        log(f"    {'─'*6}", end="")
        for _ in prop_names:
            log(f"  {'─'*14}", end="")
        log()

        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            props = all_props[key]

            log(f"    L{layer_idx:4d}", end="")
            for pname in prop_names:
                prop_vals = props[pname]
                rho, _ = stats.spearmanr(gamma, prop_vals)
                log(f"  {rho:14.4f}", end="")
            log()

    # ── Exp 4: How much of gamma is explained by row_norm? ──────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 4: GAMMA ≈ f(ROW_NORM)? — THE DIRECT TEST")
    log(f"{'=' * 72}")
    log("If gamma ∝ row_norm, then we can derive gamma from the")
    log("weight matrix's row norms — which ARE computable from signs")
    log("+ the crystal equation (the eigenvalue spectrum determines")
    log("the row norm distribution).")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            props = all_props[key]
            row_norm = props['row_norm']

            # Linear fit: gamma = a * row_norm + b
            slope, intercept, r_value, p_value, std_err = stats.linregress(row_norm, gamma)

            # Predict gamma from row_norm
            gamma_pred = slope * row_norm + intercept

            # Reconstruction comparison would require T, skip here
            # Just report R² and the relationship
            log(f"    Layer {layer_idx:2d}: R²={r_value**2:.6f}  "
                f"slope={slope:.6f}  intercept={intercept:.6f}")

    # ── Exp 5: Gamma = row_norm * constant? ─────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 5: GAMMA / ROW_NORM RATIO — IS IT CONSTANT?")
    log(f"{'=' * 72}")
    log("If γ_i = c · ||w_i|| for some constant c, the ratio should")
    log("be constant across rows and across layers.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        all_ratios = []
        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            row_norm = all_props[key]['row_norm']

            ratio = gamma / (row_norm + 1e-10)
            mean_r = ratio.mean()
            std_r = ratio.std()
            cv = std_r / (mean_r + 1e-10)
            all_ratios.append(mean_r)

            log(f"    Layer {layer_idx:2d}: γ/||w|| = {mean_r:.6f} ± {std_r:.6f}  "
                f"CV={cv:.4f}")

        log(f"    Cross-layer: mean={np.mean(all_ratios):.6f} ± {np.std(all_ratios):.6f}  "
            f"CV={np.std(all_ratios)/(np.mean(all_ratios)+1e-10):.4f}")

    # ── Exp 6: The complete picture — can we derive gamma? ──────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 6: COMPLETE DERIVATION TEST")
    log(f"{'=' * 72}")
    log("Given ONLY signs + row norms + universal γ/||w|| ratio:")
    log("  1. Compute row norms from W")
    log("  2. γ_predicted = (mean γ/||w||) · ||w_i||")
    log("  3. Compare with true gamma")

    for wtype in weight_types:
        log(f"\n  {wtype}:")

        # Compute universal ratio from all layers
        ratios_all = []
        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            row_norm = all_props[key]['row_norm']
            ratios_all.extend((gamma / (row_norm + 1e-10)).tolist())
        universal_ratio = np.mean(ratios_all)
        log(f"    Universal γ/||w|| ratio: {universal_ratio:.6f}")

        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            row_norm = all_props[key]['row_norm']

            # Predict gamma
            gamma_pred = universal_ratio * row_norm

            # Compare
            cos = np.dot(gamma, gamma_pred) / (
                np.linalg.norm(gamma) * np.linalg.norm(gamma_pred) + 1e-10)
            rank_true = np.argsort(np.argsort(-gamma))
            rank_pred = np.argsort(np.argsort(-gamma_pred))
            rho, _ = stats.spearmanr(rank_true, rank_pred)

            log(f"    Layer {layer_idx:2d}: γ_cos={cos:.6f}  rank_ρ={rho:.4f}")

    # ── Exp 7: But wait — row_norm requires float weights! ──────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 7: ROW NORM FROM TERNARY — CAN WE ESTIMATE IT?")
    log(f"{'=' * 72}")
    log("Row norm from float W requires float weights.")
    log("But ||w|| ≈ γ · ||t|| where t is ternary. And ||t|| = sqrt(nnz).")
    log("So the relationship is CIRCULAR unless row norms have structure.")
    log()
    log("Alternative: does row INDEX predict gamma rank?")
    log("(i.e., is there a positional pattern?)")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        for layer_idx in layer_indices:
            key = (layer_idx, wtype)
            gamma = all_gammas[key]
            n = len(gamma)
            row_idx = np.arange(n)

            rho, _ = stats.spearmanr(gamma, row_idx)

            # Check if gamma has ANY spatial structure (periodic, etc)
            # Autocorrelation at lag 1
            g_centered = gamma - gamma.mean()
            autocorr_1 = np.correlate(g_centered[:-1], g_centered[1:])[0] / (
                np.dot(g_centered, g_centered) + 1e-10)

            # Check for block structure — compare first half vs second half
            half = n // 2
            mean_first = gamma[:half].mean()
            mean_second = gamma[half:].mean()
            half_ratio = mean_first / (mean_second + 1e-10)

            log(f"    Layer {layer_idx:2d}: idx_ρ={rho:.4f}  "
                f"autocorr={autocorr_1:.4f}  "
                f"half_ratio={half_ratio:.4f}")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,1,5,10,17,25,35")
    parser.add_argument("--zero-rate", type=float, default=0.35)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, args.zero_rate)


if __name__ == "__main__":
    main()
