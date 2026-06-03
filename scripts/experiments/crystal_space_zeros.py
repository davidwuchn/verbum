#!/usr/bin/env python3
"""Test: does the zero mask have structure in crystal/SVD space?

THE HYPOTHESIS: Zeros look random in weight space, but in the SVD basis
(the crystal's eigenbasis), they might concentrate in low-energy components.
If so, the crystal equation tells us where zeros should be.

GD creates zeros where computation is irreducible. The SVD basis separates
"important directions" (large σ_k) from "irreducible directions" (small σ_k).
Zeros should concentrate in the small-σ components.

EXPERIMENTS:
  1. Project zero mask into SVD basis — do zeros concentrate in specific components?
  2. Component-wise zero rate — what fraction of each singular component is "zero"?
  3. Cross-model comparison — do different models zero the same SVD components?
     (Using Qwen3-8B layers as "different models" — they're independently trained
     in the sense that each layer's eigenvectors are independent)
  4. Reconstruction from crystal-predicted zeros — use σ_k threshold to predict
     zero mask, reconstruct, measure cosine

Usage:
  uv run python scripts/experiments/crystal_space_zeros.py --model Qwen/Qwen3-8B

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


def ternary_with_mask(W: torch.Tensor, zero_mask: torch.Tensor) -> tuple[float, float]:
    W_f32 = W.float()
    T = torch.sign(W_f32)
    T[zero_mask] = 0
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt
    W_recon = gamma.unsqueeze(1) * T
    w_flat = W_f32.flatten()
    cos_pr = (torch.dot(w_flat, W_recon.flatten()) /
              (torch.norm(w_flat) * torch.norm(W_recon.flatten()) + 1e-10)).item()
    gamma_c = torch.full_like(gamma, gamma.mean().item())
    W_recon_c = gamma_c.unsqueeze(1) * T
    cos_c = (torch.dot(w_flat, W_recon_c.flatten()) /
             (torch.norm(w_flat) * torch.norm(W_recon_c.flatten()) + 1e-10)).item()
    return cos_pr, cos_c


def run_experiment(model_id: str, layer_indices: list[int], top_k: int = 256):
    log("=" * 72)
    log("ZERO MASK IN CRYSTAL/SVD SPACE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log(f"SVD top-k: {top_k}")
    log()

    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"Loaded {model_id}\n")

    weight_types = ['gate_proj', 'down_proj']

    # Store per-component zero rates for cross-layer comparison
    component_zero_rates = {}  # (wtype, layer) → array of per-component zero rates

    for wtype in weight_types:
        log(f"\n{'═' * 72}")
        log(f"WEIGHT TYPE: {wtype}")
        log(f"{'═' * 72}")

        for layer_idx in layer_indices:
            layer = model.model.layers[layer_idx]
            W = getattr(layer.mlp, wtype).weight.data.float().cpu()
            m, n = W.shape

            log(f"\n  Layer {layer_idx}: {m}×{n}")

            # SVD
            k = min(top_k, min(m, n))
            t0 = time.time()
            U, S, Vt = torch.svd_lowrank(W, q=k, niter=5)
            # U: (m, k), S: (k,), Vt is actually V: (n, k)
            V = Vt  # svd_lowrank returns V not Vt
            log(f"    SVD top-{k} in {time.time()-t0:.1f}s")

            energy_captured = (S**2).sum() / (W**2).sum()
            log(f"    Energy captured: {energy_captured:.4f}")

            # Weight-space zero mask at 50%
            abs_W = W.abs()
            thresh = torch.quantile(abs_W, 0.50, dim=1, keepdim=True)
            zero_mask = abs_W < thresh  # (m, n) bool

            # ── Exp 1: Project zero mask into SVD space ─────────
            log(f"\n    EXP 1 — Zero mask in SVD basis:")

            # For each singular component k, measure how much "zero weight"
            # falls in that direction.
            # W = Σ_k σ_k · u_k · v_k^T
            # The contribution of component k to position (i,j) is σ_k · U[i,k] · V[j,k]
            # A zero at position (i,j) "blocks" this contribution.
            #
            # Component-k zero rate = fraction of component k's energy
            # that falls in zero positions.
            #
            # zero_energy_k = Σ_{(i,j) ∈ zeros} (U[i,k] · V[j,k])²
            # total_energy_k = Σ_{(i,j)} (U[i,k] · V[j,k])² = ||u_k||² · ||v_k||² = 1

            # More direct: project the zero indicator into SVD space
            # Zero indicator as float: Z[i,j] = 1 if zero, 0 if not
            Z = zero_mask.float()

            # Component-k zero rate = u_k^T · Z · v_k (how much of component k is zeroed)
            # This gives a scalar per component, but sign-dependent.
            # Better: u_k^T · Z · v_k measures the "zero mass" in direction (u_k, v_k)

            # Actually, more meaningful: for each component k, what fraction
            # of the WEIGHTS that load heavily on this component are zero?
            # Weight (i,j) loads on component k proportionally to |U[i,k]| · |V[j,k]|

            # Per-component zero fraction, weighted by component loading
            comp_zero_rates = torch.zeros(k)
            comp_nonzero_rates = torch.zeros(k)
            
            # For efficiency: compute U^T @ Z @ V — this gives (k, k) matrix
            # The diagonal is what we want: how much "zero" each component sees
            UZ = U.T @ Z      # (k, n)
            UZV = UZ @ V      # (k, k)
            
            # Also compute U^T @ (1-Z) @ V for non-zero
            UNZ = U.T @ (1 - Z)
            UNZV = UNZ @ V
            
            # The diagonal of UZV tells us: for component k, the projection
            # of the zero mask onto (u_k, v_k)
            diag_zero = torch.diag(UZV)
            diag_nonzero = torch.diag(UNZV)
            
            # Normalize to get fraction
            total_proj = diag_zero.abs() + diag_nonzero.abs()
            frac_zero = diag_zero.abs() / (total_proj + 1e-10)

            log(f"      Singular values (first 10): {S[:10].tolist()}")
            log(f"      Zero fraction by component (first 20):")
            log(f"      {'comp':>6s} {'σ_k':>10s} {'σ_k/σ_0':>10s} {'zero_frac':>10s}")
            for i in range(min(20, k)):
                log(f"      {i:6d} {S[i]:10.4f} {S[i]/S[0]:10.4f} {frac_zero[i]:10.4f}")

            # ── Exp 2: Row-space analysis ───────────────────────
            log(f"\n    EXP 2 — Per-row zero rate in SVD component space:")
            
            # For each row i, compute the "SVD profile": how much of row i's
            # energy is in each component k
            # row_profile[i,k] = (U[i,k] * S[k])² / ||w_i||²
            row_profiles = (U * S.unsqueeze(0)) ** 2  # (m, k)
            row_norms_sq = (W ** 2).sum(dim=1, keepdim=True)  # (m, 1)
            row_profiles_norm = row_profiles / (row_norms_sq + 1e-10)  # (m, k)

            # For each row, what's the zero rate?
            row_zero_rates = zero_mask.float().mean(dim=1)  # (m,)

            # Correlation: do rows with more energy in high-k (low σ) components
            # have more zeros?
            # Compute "high-k energy fraction" per row
            mid = k // 2
            high_k_energy = row_profiles_norm[:, mid:].sum(dim=1).numpy()
            low_k_energy = row_profiles_norm[:, :mid].sum(dim=1).numpy()
            rz = row_zero_rates.numpy()

            rho_high, _ = scipy_stats.spearmanr(high_k_energy, rz)
            rho_low, _ = scipy_stats.spearmanr(low_k_energy, rz)
            log(f"      ρ(high-k energy, row_zero_rate) = {rho_high:.4f}")
            log(f"      ρ(low-k energy, row_zero_rate)  = {rho_low:.4f}")

            # ── Exp 3: σ-threshold zero mask ────────────────────
            log(f"\n    EXP 3 — Crystal-predicted zero mask (σ_k threshold):")
            log(f"      Zero the low-σ components of each weight,")
            log(f"      reconstruct, measure cosine.")

            # For each weight (i,j), its "importance" in SVD space is:
            # importance[i,j] = Σ_k σ_k² · U[i,k]² · V[j,k]²
            # If we could compute this efficiently...

            # Approximate: reconstruct W from top-k' components,
            # zero where reconstruction is small
            for k_keep in [k//4, k//2, 3*k//4, k]:
                W_approx = U[:, :k_keep] @ torch.diag(S[:k_keep]) @ V[:, :k_keep].T
                # Zero where approximation is small
                abs_approx = W_approx.abs()
                thresh_approx = torch.quantile(abs_approx, 0.50, dim=1, keepdim=True)
                mask_approx = abs_approx < thresh_approx
                cos_pr, cos_c = ternary_with_mask(W, mask_approx)
                
                # Also: how much does this mask overlap with the true mask?
                overlap = (mask_approx == zero_mask).float().mean().item()
                
                log(f"      top-{k_keep:3d} approx mask: cos_pr={cos_pr:.6f} "
                    f"cos_c={cos_c:.6f}  overlap={overlap:.4f}")

            # Baseline: true magnitude mask
            cos_pr_base, cos_c_base = ternary_with_mask(W, zero_mask)
            log(f"      True magnitude mask:  cos_pr={cos_pr_base:.6f} "
                f"cos_c={cos_c_base:.6f}  overlap=1.0000")

            # ── Exp 4: Component-energy zero mask ───────────────
            log(f"\n    EXP 4 — Per-weight SVD importance as zero predictor:")
            
            # importance[i,j] = Σ_k σ_k · |U[i,k]| · |V[j,k]|
            # This is cheaper than σ² · U² · V² and more numerically stable
            # Actually: this is just |W_approx[i,j]| from the SVD reconstruction
            # Which we already tested above.
            
            # More interesting: importance from CRYSTAL equation singular values
            # Replace S with crystal-predicted values: S_crystal[k] = C · φ^(-α·k/K)
            # and use U, V from this layer
            
            # Fit crystal equation to singular values
            k_range = torch.arange(k, dtype=torch.float32)
            log_phi_S = torch.log(S) / math.log(PHI)
            # Fit: log_phi(S) = a - b*k
            coeffs = np.polyfit(k_range.numpy(), log_phi_S.numpy(), 1)
            slope_phi, intercept_phi = coeffs
            S_crystal = PHI ** (intercept_phi + slope_phi * k_range)
            
            crystal_fit_cos = torch.dot(S / S.norm(), S_crystal / S_crystal.norm()).item()
            log(f"      Crystal fit to singular values: cos={crystal_fit_cos:.6f}")
            log(f"      φ-decay rate: {-slope_phi:.4f}")
            
            # Reconstruct with crystal S, true U, V
            W_crystal = U @ torch.diag(S_crystal) @ V.T
            abs_crystal = W_crystal.abs()
            thresh_crystal = torch.quantile(abs_crystal, 0.50, dim=1, keepdim=True)
            mask_crystal = abs_crystal < thresh_crystal
            
            cos_pr_crystal, cos_c_crystal = ternary_with_mask(W, mask_crystal)
            overlap_crystal = (mask_crystal == zero_mask).float().mean().item()
            log(f"      Crystal-S mask: cos_pr={cos_pr_crystal:.6f} "
                f"cos_c={cos_c_crystal:.6f}  overlap={overlap_crystal:.4f}")

            # Store for cross-layer comparison
            component_zero_rates[(wtype, layer_idx)] = frac_zero.numpy()

        # ── Exp 5: Cross-layer component zero rate comparison ───
        log(f"\n  EXP 5 — Cross-layer component zero rate correlation ({wtype}):")
        log(f"    Do the same SVD components get zeroed across layers?")
        layers_avail = [l for l in layer_indices if (wtype, l) in component_zero_rates]
        for i, l1 in enumerate(layers_avail):
            for l2 in layers_avail[i+1:]:
                r1 = component_zero_rates[(wtype, l1)]
                r2 = component_zero_rates[(wtype, l2)]
                n_min = min(len(r1), len(r2))
                rho, p = scipy_stats.spearmanr(r1[:n_min], r2[:n_min])
                log(f"    L{l1:2d} vs L{l2:2d}: ρ={rho:.4f}  p={p:.2e}")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    parser.add_argument("--top-k", type=int, default=256)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, args.top_k)


if __name__ == "__main__":
    main()
