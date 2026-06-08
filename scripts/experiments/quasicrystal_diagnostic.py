#!/usr/bin/env python3
"""Quasicrystal Diagnostic — Does the sign pattern have φ-structured multi-scale order?

Hypothesis: The crystal sign pattern is a quasicrystalline encoding where φ
governs the structure at every dimensional scale. If true:

  1. Eigenvalue ratios follow φ^(p/q) at EVERY projection level, not just k=4 (KIBC)
  2. Small random perturbations rapidly break φ ratios at ALL scales (fragile order)
  3. Successive eigenvectors are rotated by the golden angle (~137.5°)
  4. Fibonacci projection levels capture more error structure than powers-of-2

This is a lightweight diagnostic — pure weight geometry, no forward passes,
no calibration data. Runs in minutes on CPU.

Usage:
  uv run python scripts/experiments/quasicrystal_diagnostic.py \
    --model Qwen/Qwen3-8B

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

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent

PHI = (1 + 5**0.5) / 2
GOLDEN_ANGLE_DEG = 360 / PHI**2  # ≈ 137.508°


def log(msg=""):
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════
# Weight extraction (no forward passes needed)
# ══════════════════════════════════════════════════════════════

def load_sign_patterns(model_name: str, layers: list[int],
                       proj_names=("gate_proj", "up_proj", "down_proj")):
    """Load weight tensors and extract sign patterns. CPU only."""
    from transformers import AutoModelForCausalLM

    log(f"  Loading {model_name} (weights only, CPU)...")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="cpu",
        attn_implementation="eager")
    log(f"  Loaded in {time.time()-t0:.0f}s")

    if hasattr(model, "model") and hasattr(model.model, "layers"):
        model_layers = model.model.layers
    else:
        raise RuntimeError(f"Can't find layers in {type(model)}")

    patterns = {}
    for li in layers:
        mlp = model_layers[li].mlp
        for pname in proj_names:
            W = getattr(mlp, pname).weight.detach().float().cpu()
            signs = torch.sign(W)
            # Replace zeros (rare but possible) with +1
            signs[signs == 0] = 1.0
            patterns[f"L{li}.{pname}"] = signs
            log(f"    L{li}.{pname}: {signs.shape}")

    # Free the model
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return patterns


# ══════════════════════════════════════════════════════════════
# Test 1: Eigenvalue cascade at multiple scales
# ══════════════════════════════════════════════════════════════

def eigenvalue_cascade(signs: torch.Tensor, max_k=16, n_sample=20000):
    """Compute eigenvalues at each projection level k = 1..max_k.

    Returns eigenvalues and φ-ratio analysis at each level.
    """
    out_f, in_f = signs.shape

    # Sample columns for tractability
    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S = signs[:, idx].float()
    else:
        S = signs.float()

    # Row correlation matrix
    C = S @ S.T / S.shape[1]

    # Full eigendecomposition (descending order)
    eigvals, eigvecs = torch.linalg.eigh(C)
    eigvals = eigvals.flip(0).numpy()
    eigvecs = eigvecs.flip(1)

    # Crystal equation: λ_k/λ_0 = φ^(-s·β_k) for KIBC (s=4/5, β=[0,1,1+φ,2+φ])
    s = 4 / 5
    beta_kibc = [0, 1, 1 + PHI, 2 + PHI]
    predicted_kibc = [PHI ** (-s * b) for b in beta_kibc]

    results = []
    for k in range(2, min(max_k + 1, len(eigvals) + 1)):
        top_k = eigvals[:k]
        if top_k[0] <= 0:
            continue

        ratios = top_k / top_k[0]

        # Try to fit each ratio as φ^(p/q) for small integers
        phi_fits = []
        for i, r in enumerate(ratios):
            if r <= 0:
                phi_fits.append({"index": i, "ratio": float(r),
                                 "phi_exp": None, "error": None})
                continue
            # φ^x = r → x = log(r)/log(φ)
            x = np.log(r) / np.log(PHI)
            # Check if x is close to p/q for small Fibonacci denominators
            best_fib = None
            best_err = float('inf')
            for q in [1, 2, 3, 5, 8, 13, 21]:
                p = round(x * q)
                frac = p / q
                err = abs(x - frac)
                if err < best_err:
                    best_err = err
                    best_fib = (p, q, frac)
            phi_fits.append({
                "index": i,
                "ratio": float(r),
                "phi_exp": float(x),
                "best_fib": f"{best_fib[0]}/{best_fib[1]}" if best_fib else None,
                "best_fib_val": best_fib[2] if best_fib else None,
                "error_pct": float(best_err / max(abs(x), 1e-10) * 100)
                             if best_fib and abs(x) > 1e-10 else 0,
            })

        # Compare to KIBC predictions for first 4
        kibc_corr = None
        if k >= 4:
            obs4 = ratios[:4]
            pred4 = np.array(predicted_kibc)
            if np.std(obs4) > 1e-10:
                kibc_corr = float(np.corrcoef(pred4, obs4)[0, 1])

        results.append({
            "k": k,
            "eigenvalues": top_k.tolist(),
            "ratios": ratios.tolist(),
            "phi_fits": phi_fits,
            "kibc_correlation": kibc_corr,
        })

    return results, eigvals, eigvecs


# ══════════════════════════════════════════════════════════════
# Test 2: Perturbation fragility
# ══════════════════════════════════════════════════════════════

def perturbation_fragility(signs: torch.Tensor, n_trials=5,
                           flip_rates=(0.001, 0.005, 0.01, 0.05, 0.1),
                           n_sample=20000):
    """How quickly do φ ratios degrade under random sign flips?

    Quasicrystal prediction: rapid degradation at ALL scales from small flips.
    Random pattern prediction: proportional degradation.
    """
    out_f, in_f = signs.shape

    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S_base = signs[:, idx].float()
    else:
        S_base = signs.float()
        idx = None

    # Baseline eigenvalues
    C0 = S_base @ S_base.T / S_base.shape[1]
    eigvals0 = torch.linalg.eigvalsh(C0).flip(0).numpy()

    # Baseline φ-exponents for top-8
    baseline_exps = []
    for i in range(min(8, len(eigvals0))):
        r = eigvals0[i] / eigvals0[0] if eigvals0[0] > 0 else 0
        if r > 0:
            baseline_exps.append(np.log(r) / np.log(PHI))
        else:
            baseline_exps.append(None)

    results = []
    for rate in flip_rates:
        n_flip = int(out_f * in_f * rate)
        trial_results = []

        for trial in range(n_trials):
            # Flip random positions
            perturbed = signs.clone()
            flat_idx = torch.randperm(out_f * in_f)[:n_flip]
            rows = flat_idx // in_f
            cols = flat_idx % in_f
            perturbed[rows, cols] *= -1

            # Re-extract sampled columns
            if idx is not None:
                S_pert = perturbed[:, idx].float()
            else:
                S_pert = perturbed.float()

            C_pert = S_pert @ S_pert.T / S_pert.shape[1]
            eigvals_pert = torch.linalg.eigvalsh(C_pert).flip(0).numpy()

            # Measure φ-ratio deviation at each level
            deviations = []
            for i in range(min(8, len(eigvals_pert))):
                if eigvals0[0] > 0 and eigvals_pert[0] > 0:
                    r0 = eigvals0[i] / eigvals0[0]
                    r1 = eigvals_pert[i] / eigvals_pert[0]
                    dev = abs(r1 - r0) / max(abs(r0), 1e-10)
                    deviations.append(float(dev))
                else:
                    deviations.append(None)

            trial_results.append({
                "top8_eigvals": eigvals_pert[:8].tolist(),
                "ratio_deviations": deviations,
                "mean_deviation": float(np.mean([d for d in deviations
                                                  if d is not None])),
            })

        mean_dev = np.mean([t["mean_deviation"] for t in trial_results])
        results.append({
            "flip_rate": rate,
            "flip_pct": rate * 100,
            "n_flips": n_flip,
            "mean_ratio_deviation": float(mean_dev),
            "per_level_deviation": [
                float(np.mean([t["ratio_deviations"][i]
                               for t in trial_results
                               if t["ratio_deviations"][i] is not None]))
                for i in range(min(8, len(eigvals0)))
            ],
            "trials": trial_results,
        })

    return results, baseline_exps


# ══════════════════════════════════════════════════════════════
# Test 3: Golden angle between successive eigenvectors
# ══════════════════════════════════════════════════════════════

def eigenvector_angles(eigvecs: torch.Tensor, n_vecs=16):
    """Measure the angle between successive eigenvectors.

    In a quasicrystal, successive eigenvectors should be rotated
    by the golden angle (137.5°) or related angles.

    eigvecs: (out_features, n_vecs) — columns are eigenvectors
    """
    n = min(n_vecs, eigvecs.shape[1])

    # Pairwise angles between successive eigenvectors
    successive_angles = []
    for i in range(n - 1):
        v1 = eigvecs[:, i].float()
        v2 = eigvecs[:, i + 1].float()
        cos_sim = torch.dot(v1, v2) / (v1.norm() * v2.norm() + 1e-10)
        cos_sim = cos_sim.clamp(-1, 1)
        angle_deg = float(torch.acos(cos_sim.abs()) * 180 / torch.pi)
        successive_angles.append({
            "pair": f"v{i}→v{i+1}",
            "cos_sim": float(cos_sim),
            "angle_deg": angle_deg,
            "golden_angle_error": abs(angle_deg - GOLDEN_ANGLE_DEG),
            "complement_error": abs(angle_deg - (180 - GOLDEN_ANGLE_DEG)),
        })

    # Also check all pairwise angles for golden angle clustering
    all_angles = []
    for i in range(n):
        for j in range(i + 1, n):
            v1 = eigvecs[:, i].float()
            v2 = eigvecs[:, j].float()
            cos_sim = torch.dot(v1, v2) / (v1.norm() * v2.norm() + 1e-10)
            cos_sim = cos_sim.clamp(-1, 1)
            angle_deg = float(torch.acos(cos_sim.abs()) * 180 / torch.pi)
            all_angles.append(angle_deg)

    # Distribution of angles — check for clustering near golden angle
    all_angles_arr = np.array(all_angles)
    near_golden = np.sum(np.abs(all_angles_arr - GOLDEN_ANGLE_DEG) < 10)
    near_90 = np.sum(np.abs(all_angles_arr - 90) < 10)
    near_complement = np.sum(
        np.abs(all_angles_arr - (180 - GOLDEN_ANGLE_DEG)) < 10)

    return {
        "successive_angles": successive_angles,
        "all_angles_summary": {
            "mean": float(all_angles_arr.mean()),
            "std": float(all_angles_arr.std()),
            "near_golden_137": int(near_golden),
            "near_90": int(near_90),
            "near_complement_42": int(near_complement),
            "total_pairs": len(all_angles),
            "golden_angle_expected": GOLDEN_ANGLE_DEG,
        },
        "angle_histogram": {
            f"{lo}-{lo+15}": int(np.sum((all_angles_arr >= lo)
                                         & (all_angles_arr < lo + 15)))
            for lo in range(0, 91, 15)
        },
    }


# ══════════════════════════════════════════════════════════════
# Test 4: Fibonacci vs power-of-2 reconstruction error
# ══════════════════════════════════════════════════════════════

def fibonacci_vs_pow2_reconstruction(signs: torch.Tensor, eigvecs,
                                     eigvals, n_sample=20000):
    """Compare reconstruction quality at Fibonacci vs power-of-2 levels.

    Project the sign pattern through top-k eigenvectors, reconstruct,
    measure how much of the sign information is captured.

    Quasicrystal prediction: Fibonacci levels capture MORE of the
    structure per dimension than powers of 2.
    """
    out_f, in_f = signs.shape

    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S = signs[:, idx].float()
    else:
        S = signs.float()

    fib_levels = [1, 2, 3, 5, 8, 13]
    pow2_levels = [1, 2, 4, 8, 16]
    all_levels = sorted(set(fib_levels + pow2_levels))

    results = {}
    for k in all_levels:
        if k > eigvecs.shape[1]:
            continue
        # Project through top-k eigenvectors
        V_k = eigvecs[:, :k].float()  # (out_f, k)
        # Reconstruction: P_k @ S where P_k = V_k @ V_k.T
        S_recon = V_k @ (V_k.T @ S)  # (out_f, n_sample)

        # Reconstruction quality: sign agreement
        sign_agree = (torch.sign(S_recon) == S).float().mean()

        # Variance captured
        var_captured = eigvals[:k].sum() / eigvals.sum() if eigvals.sum() > 0 else 0

        # Frobenius reconstruction error
        frob_err = (S - S_recon).norm() / S.norm()

        results[k] = {
            "sign_agreement": float(sign_agree),
            "variance_captured": float(var_captured),
            "frobenius_error": float(frob_err),
            "is_fibonacci": k in fib_levels,
            "is_pow2": k in pow2_levels,
        }

    return results


# ══════════════════════════════════════════════════════════════
# Test 5: Cross-layer φ-consistency
# ══════════════════════════════════════════════════════════════

def cross_layer_phi_consistency(patterns: dict[str, torch.Tensor],
                                n_sample=10000):
    """Are the φ-exponents consistent across layers?

    In a quasicrystal, the φ structure should be universal — same
    exponents at every layer (like the crystal eigenvalue equation).
    """
    layer_exponents = {}

    for name, signs in patterns.items():
        out_f, in_f = signs.shape
        if in_f > n_sample:
            idx = torch.randperm(in_f)[:n_sample]
            S = signs[:, idx].float()
        else:
            S = signs.float()

        C = S @ S.T / S.shape[1]
        eigvals = torch.linalg.eigvalsh(C).flip(0).numpy()

        # φ-exponents for top-8
        exps = []
        for i in range(min(8, len(eigvals))):
            r = eigvals[i] / eigvals[0] if eigvals[0] > 0 else 0
            if r > 0:
                exps.append(float(np.log(r) / np.log(PHI)))
            else:
                exps.append(None)
        layer_exponents[name] = exps

    # Cross-layer consistency: std of exponents at each rank
    n_exp = min(len(v) for v in layer_exponents.values())
    consistency = []
    for i in range(n_exp):
        vals = [v[i] for v in layer_exponents.values()
                if v[i] is not None]
        if vals:
            consistency.append({
                "rank": i,
                "mean_exp": float(np.mean(vals)),
                "std_exp": float(np.std(vals)),
                "cv": float(np.std(vals) / abs(np.mean(vals)))
                      if abs(np.mean(vals)) > 1e-10 else float('inf'),
                "values": [round(v, 4) for v in vals],
            })

    return {"layer_exponents": layer_exponents, "consistency": consistency}


# ══════════════════════════════════════════════════════════════
# Random baseline: same tests on random sign patterns
# ══════════════════════════════════════════════════════════════

def random_baseline_eigenvalues(shape, n_trials=3, max_k=16, n_sample=20000):
    """What do eigenvalue ratios look like for RANDOM sign patterns?

    If the model's ratios match random, there's no quasicrystal.
    If they diverge systematically, the φ structure is real.
    """
    out_f, in_f = shape
    all_ratios = []

    for trial in range(n_trials):
        # Random ±1 matrix
        S = torch.sign(torch.randn(out_f, min(in_f, n_sample)))
        S[S == 0] = 1.0

        C = S @ S.T / S.shape[1]
        eigvals = torch.linalg.eigvalsh(C).flip(0).numpy()

        ratios = []
        for k in range(min(max_k, len(eigvals))):
            if eigvals[0] > 0:
                ratios.append(float(eigvals[k] / eigvals[0]))
            else:
                ratios.append(0)
        all_ratios.append(ratios)

    # Average across trials
    n = min(len(r) for r in all_ratios)
    mean_ratios = [float(np.mean([r[i] for r in all_ratios]))
                   for i in range(n)]
    return {"mean_ratios": mean_ratios, "n_trials": n_trials}


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--layers", type=str, default="3,10,15,20,25,33",
                   help="Comma-separated layer indices to analyze")
    p.add_argument("--proj", type=str, default="gate_proj",
                   help="Which projection to analyze (gate_proj, up_proj, down_proj)")
    args = p.parse_args()

    layer_list = [int(x) for x in args.layers.split(",")]

    log(f"\n{'='*70}")
    log("  QUASICRYSTAL DIAGNOSTIC")
    log(f"  Does the sign pattern have φ-structured multi-scale order?")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Layers: {layer_list}")
    log(f"  Projection: {args.proj}")
    log(f"  φ = {PHI:.6f}")
    log(f"  Golden angle = {GOLDEN_ANGLE_DEG:.3f}°")

    # ── Load sign patterns ────────────────────────────────
    patterns = load_sign_patterns(args.model, layer_list, [args.proj])

    all_results = {}

    # Pick a representative layer for detailed tests
    rep_key = f"L{layer_list[len(layer_list)//2]}.{args.proj}"
    rep_signs = patterns[rep_key]
    log(f"\n  Representative layer: {rep_key} {rep_signs.shape}")

    # ═══════════════════════════════════════════════════════
    # Test 1: Eigenvalue cascade
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TEST 1: EIGENVALUE CASCADE — φ^(p/q) at every scale?")
    log(f"{'═'*70}")

    cascade, eigvals, eigvecs = eigenvalue_cascade(rep_signs, max_k=16)
    all_results["eigenvalue_cascade"] = cascade

    log(f"\n  {'k':>3}  {'Ratios (λ_k/λ_0)':40}  {'φ-exponents':30}  {'KIBC r'}")
    log(f"  {'─'*3}  {'─'*40}  {'─'*30}  {'─'*6}")

    for level in cascade:
        k = level["k"]
        ratios_str = " ".join(f"{r:.3f}" for r in level["ratios"][:min(k, 6)])
        exps = [f["phi_exp"] for f in level["phi_fits"][:min(k, 6)]
                if f["phi_exp"] is not None]
        exp_str = " ".join(f"{e:+.3f}" for e in exps)
        kibc = f"{level['kibc_correlation']:.4f}" if level['kibc_correlation'] else "—"
        log(f"  {k:>3}  {ratios_str:40}  {exp_str:30}  {kibc}")

    # Show φ-fit quality for top-8
    log(f"\n  φ^(p/q) fit quality (representative layer):")
    if len(cascade) > 6:
        level8 = [c for c in cascade if c["k"] == 8]
        if level8:
            log(f"  {'idx':>4} {'ratio':>8} {'φ^x':>8} {'best p/q':>8}"
                f" {'φ^(p/q)':>8} {'err%':>6}")
            for fit in level8[0]["phi_fits"]:
                if fit["phi_exp"] is not None:
                    log(f"  {fit['index']:>4} {fit['ratio']:>8.4f}"
                        f" {fit['phi_exp']:>8.4f}"
                        f" {fit['best_fib'] or '—':>8}"
                        f" {PHI**fit['best_fib_val'] if fit['best_fib_val'] else 0:>8.4f}"
                        f" {fit['error_pct']:>6.2f}")

    # ── Random baseline ───────────────────────────────────
    log(f"\n  Random baseline (same shape):")
    rand_baseline = random_baseline_eigenvalues(rep_signs.shape)
    all_results["random_baseline"] = rand_baseline
    log(f"  Random ratios: {' '.join(f'{r:.3f}' for r in rand_baseline['mean_ratios'][:8])}")
    log(f"  Model ratios:  {' '.join(f'{r:.3f}' for r in cascade[-1]['ratios'][:8])}" if cascade else "")

    # ═══════════════════════════════════════════════════════
    # Test 2: Perturbation fragility
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TEST 2: PERTURBATION FRAGILITY — How fast do φ ratios break?")
    log(f"{'═'*70}")

    fragility, baseline_exps = perturbation_fragility(rep_signs)
    all_results["perturbation_fragility"] = fragility

    log(f"\n  Baseline φ-exponents: {' '.join(f'{e:+.3f}' for e in baseline_exps if e is not None)}")
    log(f"\n  {'flip%':>6} {'mean_dev':>10} {'per-level deviation (top-8)'}")
    log(f"  {'─'*6} {'─'*10} {'─'*50}")
    for r in fragility:
        devs = " ".join(f"{d:.4f}" for d in r["per_level_deviation"][:8])
        log(f"  {r['flip_pct']:>5.1f}% {r['mean_ratio_deviation']:>10.4f}  {devs}")

    # ═══════════════════════════════════════════════════════
    # Test 3: Golden angle between eigenvectors
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TEST 3: GOLDEN ANGLE — Are eigenvectors φ-rotated?")
    log(f"{'═'*70}")

    angles = eigenvector_angles(eigvecs, n_vecs=16)
    all_results["eigenvector_angles"] = angles

    log(f"\n  Successive eigenvector angles:")
    log(f"  {'pair':>10} {'angle':>8} {'|err from 137.5°|':>18} {'|err from 42.5°|':>16}")
    log(f"  {'─'*10} {'─'*8} {'─'*18} {'─'*16}")
    for a in angles["successive_angles"]:
        log(f"  {a['pair']:>10} {a['angle_deg']:>7.2f}°"
            f" {a['golden_angle_error']:>17.2f}°"
            f" {a['complement_error']:>15.2f}°")

    summ = angles["all_angles_summary"]
    log(f"\n  All pairwise angles ({summ['total_pairs']} pairs):")
    log(f"    Mean: {summ['mean']:.2f}° ± {summ['std']:.2f}°")
    log(f"    Near golden (137.5° ± 10°): {summ['near_golden_137']}")
    log(f"    Near 90° (± 10°): {summ['near_90']}")
    log(f"    Near complement (42.5° ± 10°): {summ['near_complement_42']}")
    log(f"    Histogram: {angles['angle_histogram']}")

    # ═══════════════════════════════════════════════════════
    # Test 4: Fibonacci vs power-of-2 reconstruction
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TEST 4: FIBONACCI vs POWER-OF-2 RECONSTRUCTION")
    log(f"{'═'*70}")

    fib_vs_pow2 = fibonacci_vs_pow2_reconstruction(
        rep_signs, eigvecs, eigvals)
    all_results["fibonacci_vs_pow2"] = fib_vs_pow2

    log(f"\n  {'k':>3} {'type':>6} {'sign_agree':>11} {'var_captured':>13}"
        f" {'frob_err':>10}")
    log(f"  {'─'*3} {'─'*6} {'─'*11} {'─'*13} {'─'*10}")
    for k in sorted(fib_vs_pow2.keys()):
        r = fib_vs_pow2[k]
        typ = "FIB" if r["is_fibonacci"] else "POW2"
        if r["is_fibonacci"] and r["is_pow2"]:
            typ = "BOTH"
        log(f"  {k:>3} {typ:>6} {r['sign_agreement']:>11.4f}"
            f" {r['variance_captured']:>13.4f} {r['frobenius_error']:>10.4f}")

    # ═══════════════════════════════════════════════════════
    # Test 5: Cross-layer consistency
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TEST 5: CROSS-LAYER φ CONSISTENCY")
    log(f"{'═'*70}")

    cross_layer = cross_layer_phi_consistency(patterns)
    all_results["cross_layer_consistency"] = cross_layer

    log(f"\n  φ-exponents across layers:")
    log(f"  {'rank':>4} {'mean_exp':>9} {'std':>8} {'CV':>8} {'values'}")
    log(f"  {'─'*4} {'─'*9} {'─'*8} {'─'*8} {'─'*40}")
    for c in cross_layer["consistency"]:
        vals_str = " ".join(f"{v:+.3f}" for v in c["values"][:6])
        cv_str = f"{c['cv']:.4f}" if c['cv'] < 100 else "∞"
        log(f"  {c['rank']:>4} {c['mean_exp']:>9.4f} {c['std_exp']:>8.4f}"
            f" {cv_str:>8}  {vals_str}")

    # ═══════════════════════════════════════════════════════
    # Verdict
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  VERDICT")
    log(f"{'='*70}")

    # Score each test
    verdicts = {}

    # Test 1: Do eigenvalues follow φ^(p/q) beyond k=4?
    if cascade:
        best_kibc = max((c["kibc_correlation"] for c in cascade
                         if c["kibc_correlation"] is not None), default=0)
        verdicts["eigenvalue_cascade"] = (
            "CONFIRMED" if best_kibc > 0.95 else
            "PARTIAL" if best_kibc > 0.8 else "DENIED")
        log(f"  Test 1 (eigenvalue cascade): {verdicts['eigenvalue_cascade']}"
            f" (best KIBC r={best_kibc:.4f})")

    # Test 2: Is fragility super-linear?
    if len(fragility) >= 3:
        # Compare 0.1% and 10% flip — quasicrystal = more than 100× ratio
        dev_small = fragility[0]["mean_ratio_deviation"]
        dev_large = fragility[-1]["mean_ratio_deviation"]
        ratio = dev_large / max(dev_small, 1e-10)
        verdicts["fragility"] = (
            "QUASICRYSTAL" if ratio > 200 else
            "PARTIAL" if ratio > 50 else "LINEAR")
        log(f"  Test 2 (fragility): {verdicts['fragility']}"
            f" (degradation ratio={ratio:.1f}x over"
            f" {fragility[-1]['flip_pct']/fragility[0]['flip_pct']:.0f}x flip increase)")

    # Test 3: Golden angle clustering
    if angles["all_angles_summary"]["total_pairs"] > 0:
        golden_frac = (angles["all_angles_summary"]["near_golden_137"]
                       / angles["all_angles_summary"]["total_pairs"])
        verdicts["golden_angle"] = (
            "CONFIRMED" if golden_frac > 0.2 else
            "PARTIAL" if golden_frac > 0.05 else "DENIED")
        log(f"  Test 3 (golden angle): {verdicts['golden_angle']}"
            f" ({golden_frac*100:.1f}% of pairs near 137.5°)")

    # Test 4: Fibonacci advantage
    fib_only = {k: v for k, v in fib_vs_pow2.items()
                if v["is_fibonacci"] and not v["is_pow2"]}
    pow2_only = {k: v for k, v in fib_vs_pow2.items()
                 if v["is_pow2"] and not v["is_fibonacci"]}
    if fib_only and pow2_only:
        fib_mean = np.mean([v["sign_agreement"] for v in fib_only.values()])
        pow2_mean = np.mean([v["sign_agreement"] for v in pow2_only.values()])
        verdicts["fib_vs_pow2"] = (
            "FIB_WINS" if fib_mean > pow2_mean + 0.01 else
            "TIE" if abs(fib_mean - pow2_mean) < 0.01 else "POW2_WINS")
        log(f"  Test 4 (fib vs pow2): {verdicts['fib_vs_pow2']}"
            f" (fib={fib_mean:.4f}, pow2={pow2_mean:.4f})")

    # Test 5: Cross-layer consistency
    if cross_layer["consistency"]:
        mean_cv = np.mean([c["cv"] for c in cross_layer["consistency"][:6]
                           if c["cv"] < 100])
        verdicts["cross_layer"] = (
            "UNIVERSAL" if mean_cv < 0.1 else
            "CONSISTENT" if mean_cv < 0.3 else "VARIABLE")
        log(f"  Test 5 (cross-layer): {verdicts['cross_layer']}"
            f" (mean CV={mean_cv:.4f})")

    all_results["verdicts"] = verdicts

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "quasicrystal-diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    out_path = out_dir / f"{slug}.json"

    # Convert numpy types for JSON serialization
    def to_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_serializable(v) for v in obj]
        return obj

    with open(out_path, "w") as f:
        json.dump(to_serializable(all_results), f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
