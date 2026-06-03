#!/usr/bin/env python3
"""Test: can gate_proj predict the zero mask for up_proj and down_proj?

THE HYPOTHESIS: In SwiGLU, y = (SiLU(x·W_gate) ⊙ x·W_up) · W_down
The gate controls which neurons fire. Gate weights predict which
up/down weights matter. The gate IS the holographic phase predictor.

THREE LEVELS OF PREDICTION:
  1. Per-neuron: gate row norm predicts up row importance / down column importance
  2. Per-weight: |gate[i,j]| predicts whether |up[i,j]| is large
  3. Ternary gate: the zero PATTERN in ternary gate predicts zeros in up/down

THE CALIBRATION-FREE CHAIN:
  gate signs → ternary gate → gate zero pattern → up/down zero masks → reconstruct

Usage:
  uv run python scripts/experiments/gate_zero_predictor.py --model Qwen/Qwen3-8B

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


def ternary_with_mask(W: torch.Tensor, zero_mask: torch.Tensor,
                      constant_gamma: bool = True) -> tuple[float, float]:
    """Reconstruct with given zero mask. Returns (cos_perrow, cos_const)."""
    W_f32 = W.float()
    T = torch.sign(W_f32)
    T[zero_mask] = 0

    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt

    # Per-row gamma
    W_recon = gamma.unsqueeze(1) * T
    w_flat = W_f32.flatten()
    r_flat = W_recon.flatten()
    cos_pr = (torch.dot(w_flat, r_flat) / (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)).item()

    # Constant gamma
    gamma_c = torch.full_like(gamma, gamma.mean().item())
    W_recon_c = gamma_c.unsqueeze(1) * T
    r_flat_c = W_recon_c.flatten()
    cos_c = (torch.dot(w_flat, r_flat_c) / (torch.norm(w_flat) * torch.norm(r_flat_c) + 1e-10)).item()

    return cos_pr, cos_c


def run_experiment(model_id: str, layer_indices: list[int]):
    log("=" * 72)
    log("GATE AS ZERO-MASK PREDICTOR")
    log("=" * 72)
    log(f"Model: {model_id}")
    log()

    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    log(f"Loaded {model_id}\n")

    for layer_idx in layer_indices:
        layer = model.model.layers[layer_idx]
        W_gate = layer.mlp.gate_proj.weight.data.float().cpu()
        W_up = layer.mlp.up_proj.weight.data.float().cpu()
        W_down = layer.mlp.down_proj.weight.data.float().cpu()

        m_inter, m_hidden = W_gate.shape  # (12288, 4096)
        log(f"{'═' * 72}")
        log(f"LAYER {layer_idx}: gate/up={W_gate.shape}, down={W_down.shape}")
        log(f"{'═' * 72}")

        abs_gate = W_gate.abs()
        abs_up = W_up.abs()
        abs_down = W_down.abs()

        # ── Baselines ───────────────────────────────────────────
        log(f"\n  BASELINES:")

        # up_proj with magnitude-based zeros at various rates
        for target, W_target, label in [("up_proj", W_up, "up"), ("down_proj", W_down, "down")]:
            for zr in [0.35, 0.50]:
                thresh = torch.quantile(W_target.float().abs(), zr, dim=1, keepdim=True)
                mask = W_target.float().abs() < thresh
                cos_pr, cos_c = ternary_with_mask(W_target, mask)
                log(f"    {label:5s} magnitude zeros @{zr:.0%}: cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

            # Random zeros at 50%
            mask_rand = torch.zeros_like(W_target, dtype=torch.bool)
            for row in range(W_target.shape[0]):
                idx = torch.randperm(W_target.shape[1])[:W_target.shape[1] // 2]
                mask_rand[row, idx] = True
            cos_pr, cos_c = ternary_with_mask(W_target, mask_rand)
            log(f"    {label:5s} random zeros @50%:      cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # ── Exp 1: Per-neuron prediction ────────────────────────
        log(f"\n  EXP 1 — PER-NEURON: gate row norm → neuron importance")

        gate_row_norms = W_gate.norm(dim=1)  # (12288,)
        up_row_norms = W_up.norm(dim=1)      # (12288,)
        down_col_norms = W_down.norm(dim=0)  # (12288,) — columns = neurons

        rho_gate_up, p1 = scipy_stats.spearmanr(gate_row_norms.numpy(), up_row_norms.numpy())
        rho_gate_down, p2 = scipy_stats.spearmanr(gate_row_norms.numpy(), down_col_norms.numpy())
        log(f"    gate_row_norm vs up_row_norm:   ρ={rho_gate_up:.4f}  p={p1:.2e}")
        log(f"    gate_row_norm vs down_col_norm: ρ={rho_gate_down:.4f}  p={p2:.2e}")

        # Zero entire neurons based on gate row norm
        for zero_frac in [0.25, 0.35, 0.50]:
            k = int(m_inter * zero_frac)
            # Find the k neurons with smallest gate row norms
            _, small_neurons = gate_row_norms.topk(k, largest=False)

            # Zero those rows in up_proj
            mask_up_neuron = torch.zeros_like(W_up, dtype=torch.bool)
            mask_up_neuron[small_neurons, :] = True
            cos_pr, cos_c = ternary_with_mask(W_up, mask_up_neuron)
            log(f"    up_proj zero {zero_frac:.0%} neurons (gate-predicted): "
                f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

            # Zero those columns in down_proj
            mask_down_neuron = torch.zeros_like(W_down, dtype=torch.bool)
            mask_down_neuron[:, small_neurons] = True
            cos_pr, cos_c = ternary_with_mask(W_down, mask_down_neuron)
            log(f"    down   zero {zero_frac:.0%} neurons (gate-predicted): "
                f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # ── Exp 2: Per-weight prediction ────────────────────────
        log(f"\n  EXP 2 — PER-WEIGHT: |gate[i,j]| predicts |up[i,j]| zero")

        # For up_proj: gate and up have same shape (12288, 4096)
        # Correlation between |gate[i,j]| and |up[i,j]|
        gate_flat = abs_gate.flatten().numpy()
        up_flat = abs_up.flatten().numpy()

        # Sample for speed (50M weights is too many for spearman)
        n_sample = min(500000, len(gate_flat))
        idx = np.random.choice(len(gate_flat), n_sample, replace=False)
        rho_pw, p_pw = scipy_stats.spearmanr(gate_flat[idx], up_flat[idx])
        log(f"    |gate[i,j]| vs |up[i,j]|: ρ={rho_pw:.4f} (sampled {n_sample})")

        # Use gate magnitude to predict up zero mask
        for zr in [0.35, 0.50]:
            # Per-row: zero the positions where gate is smallest
            gate_thresh = torch.quantile(abs_gate, zr, dim=1, keepdim=True)
            mask_up_from_gate = abs_gate < gate_thresh
            cos_pr, cos_c = ternary_with_mask(W_up, mask_up_from_gate)
            log(f"    up_proj zeros from gate magnitude @{zr:.0%}: "
                f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # For down_proj: gate is (12288, 4096), down is (4096, 12288)
        # gate[i,j] corresponds to neuron i, input j
        # down[j,i] corresponds to output j, neuron i
        # So gate[i,j] predicts down[ANY, i] — neuron-level only
        # But we can also try: gate transposed magnitude
        # |gate[i,j]| → predict |down[j,i]|
        gate_T_flat = abs_gate.T.flatten().numpy()  # (4096, 12288) flattened
        down_flat = abs_down.flatten().numpy()       # (4096, 12288) flattened
        idx2 = np.random.choice(len(gate_T_flat), n_sample, replace=False)
        rho_gd, p_gd = scipy_stats.spearmanr(gate_T_flat[idx2], down_flat[idx2])
        log(f"    |gate.T[j,i]| vs |down[j,i]|: ρ={rho_gd:.4f}")

        # Use gate.T magnitude to predict down zero mask
        for zr in [0.35, 0.50]:
            gate_T = abs_gate.T  # (4096, 12288) — same shape as down
            thresh_gt = torch.quantile(gate_T, zr, dim=1, keepdim=True)
            mask_down_from_gate = gate_T < thresh_gt
            cos_pr, cos_c = ternary_with_mask(W_down, mask_down_from_gate)
            log(f"    down_proj zeros from gate.T magnitude @{zr:.0%}: "
                f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # ── Exp 3: Ternary gate → zero mask (NO float weights) ─
        log(f"\n  EXP 3 — TERNARY GATE → ZERO MASK (calibration-free)")
        log(f"    Only uses sign(gate) and gate's own zero pattern.")

        # Ternary gate: sign + 35% zeros (magnitude-based)
        gate_thresh_35 = torch.quantile(abs_gate, 0.35, dim=1, keepdim=True)
        T_gate = torch.sign(W_gate)
        T_gate[abs_gate < gate_thresh_35] = 0

        # The zero pattern in ternary gate
        gate_zeros = (T_gate == 0)  # positions where gate is zero

        # Prediction: where gate is zero → up should be zero too
        # (same positions, since same shape)
        mask_up_from_ternary_gate = gate_zeros
        cos_pr, cos_c = ternary_with_mask(W_up, mask_up_from_ternary_gate)
        actual_zr = gate_zeros.float().mean().item()
        log(f"    up_proj zeros = gate zero positions ({actual_zr:.1%}): "
            f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # For down_proj: gate zeros transposed
        gate_zeros_T = gate_zeros.T  # (4096, 12288) — same shape as down
        cos_pr, cos_c = ternary_with_mask(W_down, gate_zeros_T)
        log(f"    down_proj zeros = gate.T zero positions ({actual_zr:.1%}): "
            f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # Try higher zero rates: use gate magnitude RANK from ternary
        # Even in ternary, we know |T_gate[i,j]| ∈ {0, 1}
        # But we can use the ORIGINAL zero threshold + expand
        # Idea: gate zeros + up's own smallest (by row) to reach 50%
        for target_zr in [0.50]:
            # Start with gate zero positions, add more based on up's own small weights
            # But we DON'T have up's magnitudes in the calibration-free path...
            # So: use gate zeros (35%) + random additional (15%) to reach 50%
            extra_needed = target_zr - actual_zr
            if extra_needed > 0:
                mask_combined = gate_zeros.clone()
                # For positions where gate is non-zero, randomly zero some
                non_zero_positions = ~gate_zeros
                # Per-row: randomly zero extra_needed fraction of remaining
                for row in range(m_inter):
                    remaining = non_zero_positions[row].nonzero().squeeze()
                    if remaining.dim() == 0:
                        continue
                    n_extra = int(len(remaining) * extra_needed / (1 - actual_zr))
                    if n_extra > 0 and len(remaining) > 0:
                        perm = torch.randperm(len(remaining))[:n_extra]
                        mask_combined[row, remaining[perm]] = True
                cos_pr, cos_c = ternary_with_mask(W_up, mask_combined)
                combined_zr = mask_combined.float().mean().item()
                log(f"    up_proj gate_zeros + random→{combined_zr:.1%}: "
                    f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # ── Exp 4: Combined prediction (gate + self magnitude) ──
        log(f"\n  EXP 4 — GATE + SELF MAGNITUDE COMBINED")
        log(f"    Use gate to predict zero mask, then refine with self magnitude.")

        for target, W_target, abs_target, label in [
            ("up_proj", W_up, abs_up, "up"),
            ("down_proj", W_down, abs_down, "down")
        ]:
            if label == "up":
                gate_predictor = abs_gate
            else:
                gate_predictor = abs_gate.T  # (4096, 12288)

            # Combined score: gate_magnitude * self_magnitude
            combined_score = gate_predictor * abs_target

            for zr in [0.35, 0.50]:
                # Zero where combined score is smallest
                combined_thresh = torch.quantile(combined_score, zr, dim=1, keepdim=True)
                mask_combined = combined_score < combined_thresh
                cos_pr, cos_c = ternary_with_mask(W_target, mask_combined)
                log(f"    {label:5s} combined(gate×self) zeros @{zr:.0%}: "
                    f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

            # Also try: gate-weighted importance — zero where gate is small
            # regardless of self magnitude
            # This is the "gate IS the zero mask" hypothesis
            for zr in [0.35, 0.50]:
                gp_thresh = torch.quantile(gate_predictor, zr, dim=1, keepdim=True)
                mask_gate_only = gate_predictor < gp_thresh
                cos_pr, cos_c = ternary_with_mask(W_target, mask_gate_only)
                log(f"    {label:5s} gate-only zeros @{zr:.0%}:          "
                    f"cos_pr={cos_pr:.6f}  cos_c={cos_c:.6f}")

        # ── Exp 5: The full calibration-free reconstruction ─────
        log(f"\n  EXP 5 — FULL CALIBRATION-FREE CHAIN")
        log(f"    gate signs → gate zeros → up/down zero mask → constant γ → reconstruct")

        # For up_proj: use ternary gate's zero pattern
        # Scale: crystal-derived constant
        UNIVERSAL_C_GATE = 0.0172
        UNIVERSAL_C_DOWN = 0.0099

        # up_proj: gate zeros as mask, constant gamma
        gate_zero_mask = (T_gate == 0)
        W_up_f32 = W_up.float()
        T_up = torch.sign(W_up_f32)
        T_up[gate_zero_mask] = 0

        # Gamma from crystal: c * ||W||_F / sqrt(m)
        frob_up = W_up_f32.norm().item()
        gamma_up_crystal = UNIVERSAL_C_GATE * frob_up / math.sqrt(m_inter)
        W_up_recon = gamma_up_crystal * T_up
        cos_up_free = (torch.dot(W_up_f32.flatten(), W_up_recon.flatten()) /
                       (torch.norm(W_up_f32.flatten()) * torch.norm(W_up_recon.flatten()) + 1e-10)).item()

        # down_proj: gate.T zeros as mask, constant gamma
        gate_zero_mask_T = gate_zero_mask.T
        W_down_f32 = W_down.float()
        T_down = torch.sign(W_down_f32)
        T_down[gate_zero_mask_T] = 0

        frob_down = W_down_f32.norm().item()
        gamma_down_crystal = UNIVERSAL_C_DOWN * frob_down / math.sqrt(W_down.shape[0])
        W_down_recon = gamma_down_crystal * T_down
        cos_down_free = (torch.dot(W_down_f32.flatten(), W_down_recon.flatten()) /
                         (torch.norm(W_down_f32.flatten()) * torch.norm(W_down_recon.flatten()) + 1e-10)).item()

        log(f"    up_proj   calibration-free: cos={cos_up_free:.6f}")
        log(f"    down_proj calibration-free: cos={cos_down_free:.6f}")

        # Compare: what if we use true Frobenius norm (still need float weights for this)
        # vs crystal-equation predicted norm
        log(f"    (Using true ||W||_F. Crystal prediction of ||W||_F is next step.)")

        # ── Exp 6: How much does each component contribute? ─────
        log(f"\n  EXP 6 — COMPONENT ATTRIBUTION")

        # Baseline: pure signs, no zeros, constant gamma
        mask_none = torch.zeros_like(W_up, dtype=torch.bool)
        cos_baseline_up, cos_baseline_up_c = ternary_with_mask(W_up, mask_none)

        mask_none_d = torch.zeros_like(W_down, dtype=torch.bool)
        cos_baseline_down, cos_baseline_down_c = ternary_with_mask(W_down, mask_none_d)

        # With self-magnitude zeros @50%
        thresh_up_50 = torch.quantile(abs_up, 0.50, dim=1, keepdim=True)
        mask_up_50 = abs_up < thresh_up_50
        cos_self50_up, cos_self50_up_c = ternary_with_mask(W_up, mask_up_50)

        thresh_down_50 = torch.quantile(abs_down, 0.50, dim=1, keepdim=True)
        mask_down_50 = abs_down < thresh_down_50
        cos_self50_down, cos_self50_down_c = ternary_with_mask(W_down, mask_down_50)

        # With gate zeros @35%
        cos_gate35_up, cos_gate35_up_c = ternary_with_mask(W_up, gate_zeros)
        cos_gate35_down, cos_gate35_down_c = ternary_with_mask(W_down, gate_zeros.T)

        log(f"    UP_PROJ:")
        log(f"      Pure sign (no zeros):           cos_c={cos_baseline_up_c:.6f}")
        log(f"      + gate zeros @35%:              cos_c={cos_gate35_up_c:.6f}  "
            f"(+{cos_gate35_up_c - cos_baseline_up_c:.4f})")
        log(f"      + self magnitude zeros @50%:    cos_c={cos_self50_up_c:.6f}  "
            f"(+{cos_self50_up_c - cos_baseline_up_c:.4f})")
        log(f"    DOWN_PROJ:")
        log(f"      Pure sign (no zeros):           cos_c={cos_baseline_down_c:.6f}")
        log(f"      + gate.T zeros @35%:            cos_c={cos_gate35_down_c:.6f}  "
            f"(+{cos_gate35_down_c - cos_baseline_down_c:.4f})")
        log(f"      + self magnitude zeros @50%:    cos_c={cos_self50_down_c:.6f}  "
            f"(+{cos_self50_down_c - cos_baseline_down_c:.4f})")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices)


if __name__ == "__main__":
    main()
