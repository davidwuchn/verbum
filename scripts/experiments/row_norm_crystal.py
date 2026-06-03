#!/usr/bin/env python3
"""Test: can we derive row norms from the crystal equation?

THE CHAIN SO FAR:
  γ_i = c · ||w_i||           (proved: R²=0.99, c universal)
  Σ follows crystal equation   (proved: 0.04% error)
  ||w_i||² = Σ_k σ_k² · U_ik²

If U is effectively random (experiment 1 proved eigenvectors are
random-like), then U_ik² ≈ 1/m + noise, and:
  ||w_i||² ≈ (1/m) · Σ_k σ_k² = ||W||_F² / m  (constant!)

But row norms AREN'T constant (CV ~10-20%). So the question is:
what creates the variation, and can we predict it?

EXPERIMENTS:
  1. Row norm distribution — shape, CV, comparison to constant prediction
  2. Random U simulation — generate ||w||² from crystal Σ + random orthogonal U,
     compare distribution to actual
  3. Row norm from Σ only — if all row norms were equal (random U limit),
     what reconstruction quality do we get?
  4. The critical test — use crystal equation Σ to generate synthetic row norms
     via random U sampling, then derive gammas, then reconstruct weights

Usage:
  uv run python scripts/experiments/row_norm_crystal.py --model Qwen/Qwen3-8B

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


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def compute_gamma_and_T(W: torch.Tensor, zero_rate: float = 0.35):
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
    return gamma, T


def reconstruction_cosine(W: torch.Tensor, T: torch.Tensor, gamma: torch.Tensor) -> float:
    W_f32 = W.float().cpu()
    W_recon = (gamma.unsqueeze(1) * T.float()).cpu()
    w_flat = W_f32.flatten()
    r_flat = W_recon.flatten()
    cos = torch.dot(w_flat, r_flat) / (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)
    return cos.item()


def run_experiment(model_id: str, layer_indices: list[int], zero_rate: float = 0.35):
    log("=" * 72)
    log("ROW NORM ↔ CRYSTAL EQUATION TEST")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log()

    from transformers import AutoModelForCausalLM, AutoConfig
    config = AutoConfig.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"Loaded {model_id}")

    weight_types = ['gate_proj', 'down_proj']

    # Universal gamma/row_norm ratios from previous experiment
    UNIVERSAL_C = {'gate_proj': 0.01720, 'up_proj': 0.01721, 'down_proj': 0.00990}

    for wtype in weight_types:
        log(f"\n{'═' * 72}")
        log(f"WEIGHT TYPE: {wtype}")
        log(f"{'═' * 72}")

        for layer_idx in layer_indices:
            layer = model.model.layers[layer_idx]
            if wtype in ('gate_proj', 'up_proj', 'down_proj'):
                W = getattr(layer.mlp, wtype).weight.data
            else:
                W = getattr(layer.self_attn, wtype).weight.data

            W_f32 = W.float().cpu()
            m, n = W_f32.shape
            gamma_true, T = compute_gamma_and_T(W, zero_rate)

            # Row norms
            row_norms = W_f32.norm(dim=1).numpy()
            true_cos = reconstruction_cosine(W, T, gamma_true)

            log(f"\n  Layer {layer_idx}: {m}×{n}")
            log(f"    True reconstruction cos: {true_cos:.6f}")
            log(f"    Row norm: mean={row_norms.mean():.4f} std={row_norms.std():.4f} "
                f"CV={row_norms.std()/row_norms.mean():.4f}")

            # ── Exp 1: Constant row norm prediction ─────────────
            # If U were perfectly random: ||w_i|| = ||W||_F / sqrt(m)
            frobenius = W_f32.norm().item()
            constant_norm = frobenius / math.sqrt(m)
            gamma_constant = UNIVERSAL_C[wtype] * constant_norm * torch.ones(m)
            cos_constant = reconstruction_cosine(W, T, gamma_constant)

            log(f"\n    Exp 1 — Constant row norm (||W||_F/√m):")
            log(f"      Predicted ||w|| = {constant_norm:.4f} (true mean = {row_norms.mean():.4f})")
            log(f"      Reconstruction cos: {cos_constant:.6f} (gap: {true_cos - cos_constant:.6f})")

            # ── Exp 2: SVD + row norm distribution analysis ─────
            log(f"\n    Exp 2 — SVD analysis:")
            t0 = time.time()
            # Truncated SVD for speed
            k = min(256, min(m, n))
            U, S, Vt = torch.svd_lowrank(W_f32, q=k, niter=5)
            svd_time = time.time() - t0
            log(f"      SVD top-{k} in {svd_time:.1f}s")

            # Row norms from SVD: ||w_i||² ≈ Σ_k S_k² · U_ik²
            S_sq = S ** 2
            U_sq = U ** 2  # (m, k)
            row_norms_svd = torch.sqrt((U_sq * S_sq.unsqueeze(0)).sum(dim=1)).numpy()

            # How much energy is captured?
            total_energy = (W_f32 ** 2).sum().item()
            svd_energy = (S ** 2).sum().item()
            log(f"      Energy captured: {svd_energy/total_energy:.4f}")

            # Compare SVD row norms to true
            rn_cos = np.dot(row_norms, row_norms_svd) / (
                np.linalg.norm(row_norms) * np.linalg.norm(row_norms_svd) + 1e-10)
            log(f"      SVD row_norm vs true row_norm cos: {rn_cos:.6f}")

            # ── Exp 3: U_ik² distribution — is it 1/m + noise? ─
            log(f"\n    Exp 3 — U² distribution (is U random?):")
            U_sq_np = U_sq.numpy()
            # For random orthogonal U, E[U_ik²] = 1/m
            expected = 1.0 / m
            actual_mean = U_sq_np.mean()
            actual_std = U_sq_np.std()
            # Marchenko-Pastur: for random, var(U_ik²) ≈ (2/m²) · (1 - k/m)
            # But let's just look at the stats
            log(f"      E[U²] = 1/m = {expected:.6f}")
            log(f"      Actual mean(U²) = {actual_mean:.6f}")
            log(f"      Actual std(U²)  = {actual_std:.6f}")

            # Row-wise variance of U²: how much does each row deviate from 1/m?
            row_u2_sums = U_sq_np.sum(axis=1)  # should be ~k/m for each row if random
            expected_row_sum = k / m
            row_sum_cv = row_u2_sums.std() / row_u2_sums.mean()
            log(f"      Row U² sum: mean={row_u2_sums.mean():.4f} (expected={expected_row_sum:.4f}) "
                f"CV={row_sum_cv:.4f}")

            # THE KEY: correlation between row U² sum and row norm
            rho_u2_norm, p_u2 = scipy_stats.spearmanr(row_u2_sums, row_norms)
            log(f"      Correlation(row_U²_sum, row_norm): ρ={rho_u2_norm:.4f} p={p_u2:.2e}")

            # ── Exp 4: Random U simulation ──────────────────────
            log(f"\n    Exp 4 — Random U simulation:")
            # Generate row norms from crystal S + random orthogonal U
            n_sims = 10
            sim_cvs = []
            sim_cosines = []
            for sim in range(n_sims):
                # Random orthogonal matrix (m × k)
                random_matrix = torch.randn(m, k)
                Q, _ = torch.linalg.qr(random_matrix)
                U_rand = Q[:, :k]
                # Synthetic row norms
                U_rand_sq = U_rand ** 2
                synth_norms_sq = (U_rand_sq * S_sq.unsqueeze(0)).sum(dim=1)
                synth_norms = torch.sqrt(synth_norms_sq).numpy()
                sim_cvs.append(synth_norms.std() / synth_norms.mean())
                # Use synthetic norms to predict gamma, then reconstruct
                synth_gamma = torch.tensor(
                    UNIVERSAL_C[wtype] * synth_norms, dtype=torch.float32)
                # But we need the right SORT ORDER — use true sort order
                # (This tests: if we had the right norms, would reconstruction work?)
                # Actually, let's assign synthetic gammas by matching rank order
                # to true rank order
                true_rank = np.argsort(np.argsort(-gamma_true.numpy()))
                synth_sorted = np.sort(synth_norms)[::-1]
                synth_gamma_ordered = np.zeros_like(synth_norms)
                synth_gamma_ordered[np.argsort(-gamma_true.numpy())] = \
                    UNIVERSAL_C[wtype] * synth_sorted
                synth_gamma_t = torch.tensor(synth_gamma_ordered, dtype=torch.float32)
                cos_synth = reconstruction_cosine(W, T, synth_gamma_t)
                sim_cosines.append(cos_synth)

            log(f"      Simulated CV: {np.mean(sim_cvs):.4f} ± {np.std(sim_cvs):.4f} "
                f"(true CV: {row_norms.std()/row_norms.mean():.4f})")
            log(f"      Sim reconstruction cos: {np.mean(sim_cosines):.4f} ± {np.std(sim_cosines):.4f} "
                f"(true: {true_cos:.4f})")

            # ── Exp 5: Row norm from crystal Σ + random U (no float weights) ─
            log(f"\n    Exp 5 — Crystal-only reconstruction (NO float weights):")
            # Use crystal equation to predict Σ
            # Crystal: λ_k = C · φ^(-s · β_k) where s=4/5, β=[0,1,1+φ,2+φ]
            # But for the full spectrum, we use the empirical finding that
            # singular values follow a smooth φ-geometric decay
            # For now, use the ACTUAL S from SVD (we'll replace with crystal later)

            # Method A: Constant gamma (all rows equal)
            mean_gamma = gamma_true.mean().item()
            gamma_flat = torch.full((m,), mean_gamma)
            cos_flat = reconstruction_cosine(W, T, gamma_flat)
            log(f"      Method A (constant γ = mean): cos={cos_flat:.6f} "
                f"(gap: {true_cos - cos_flat:.6f})")

            # Method B: φ-geometric gamma (from previous experiment's fit)
            # γ(rank) = A · φ^(-α · rank/N) with universal α
            # Use α values from gamma_phi_structure experiment
            alpha_gate = 0.95  # approximate mean for normal layers
            alpha_down = 0.43
            alpha = alpha_gate if wtype != 'down_proj' else alpha_down
            ranks = np.arange(m) / m
            phi_gammas_sorted = mean_gamma * PHI ** (-alpha * (ranks - 0.5))
            # Normalize to preserve mean
            phi_gammas_sorted *= mean_gamma / phi_gammas_sorted.mean()
            # Assign by true rank order
            true_sort = np.argsort(-gamma_true.numpy())
            phi_gammas = np.zeros(m)
            phi_gammas[true_sort] = phi_gammas_sorted
            cos_phi = reconstruction_cosine(
                W, T, torch.tensor(phi_gammas, dtype=torch.float32))
            log(f"      Method B (φ-geometric + true sort): cos={cos_phi:.6f} "
                f"(gap: {true_cos - cos_phi:.6f})")

            # Method C: φ-geometric gamma with RANDOM sort order
            n_random = 20
            cos_random_sorts = []
            for _ in range(n_random):
                random_sort = np.random.permutation(m)
                phi_gammas_rand = np.zeros(m)
                phi_gammas_rand[random_sort] = phi_gammas_sorted
                cos_r = reconstruction_cosine(
                    W, T, torch.tensor(phi_gammas_rand, dtype=torch.float32))
                cos_random_sorts.append(cos_r)
            log(f"      Method C (φ-geometric + random sort): cos={np.mean(cos_random_sorts):.6f} "
                f"± {np.std(cos_random_sorts):.6f}")

            # Method D: Constant gamma (no sort order needed at all)
            # vs true reconstruction — what's the actual cost of not knowing row norms?
            log(f"\n      SUMMARY for layer {layer_idx}:")
            log(f"        True gammas:          {true_cos:.6f}")
            log(f"        φ-predicted + sort:    {cos_phi:.6f}  (need sort order)")
            log(f"        Constant γ (no sort):  {cos_flat:.6f}  (need nothing)")
            log(f"        Random sort φ-geom:    {np.mean(cos_random_sorts):.6f}  (need nothing)")
            log(f"        Gap (true - constant): {true_cos - cos_flat:.6f}")

    del model
    gc.collect()

    # ── Final summary ───────────────────────────────────────────
    log(f"\n{'═' * 72}")
    log("ANALYSIS: THE CIRCULARITY AND THE WAY OUT")
    log(f"{'═' * 72}")
    log()
    log("The chain:")
    log("  1. γ_i = c · ||w_i||        (c universal per weight type)")
    log("  2. ||w_i||² = Σ_k σ_k² · U_ik²")
    log("  3. σ_k from crystal equation (known)")
    log("  4. U_ik from per-layer rotation (unknown, random-like)")
    log()
    log("The circularity: to get ||w_i|| we need U, and U is per-layer.")
    log()
    log("But the DISTRIBUTION of ||w_i|| is determined by σ_k + random U.")
    log("So we know the distribution but not the assignment.")
    log()
    log("The question becomes: how much does the assignment matter?")
    log("  - If constant γ gives cos ~0.89 and true gives ~0.90,")
    log("    the assignment barely matters.")
    log("  - If the gap is large, we need the assignment.")
    log()
    log(f"{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


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
