"""Lens Mechanism Experiment — What IS the Q lens distortion?

The Fourier experiments showed:
  - Phase-only reconstruction (strip magnitude) beats sign vote by +19%
  - Magnitude encodes "lens distortion" from the Q rotation
  - Phase encodes "crystal structure" (consistent across rotations)

But we don't understand the MECHANISM. This script probes:

1. DECOMPOSITION: For each Q rotation × plate, decompose the gradient's
   FFT into magnitude and phase. Measure how much each varies across
   rotations. If Q is truly a "lens", magnitude should vary (Q-dependent)
   while phase stays constant (crystal-dependent).

2. Q TRANSFER FUNCTION: Can we predict a rotation's magnitude spectrum
   from its Q weight matrix? If Q is a linear lens, it should impose a
   predictable transfer function on the gradient signal.

3. SIGNAL SEPARATION: How much of the magnitude is lens (Q-dependent)
   vs crystal (rotation-invariant)? Can we separate them?

4. DECONVOLUTION: If we can model the lens, Wiener deconvolution should
   beat crude phase-only stripping. Test this.

5. SCALING: Why does phase-only win at 8-rot but lose at 16-rot?
   Hypothesis: at enough rotations, magnitude noise averages out in
   sign vote, recovering the signal that phase-only discards.

License: MIT
"""

from __future__ import annotations

import json
import time
import sys
from pathlib import Path

import numpy as np

import mlx.core as mx


def _pearsonr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Pearson correlation + approximate two-sided p-value."""
    x = x - x.mean()
    y = y - y.mean()
    r = (x * y).sum() / (np.sqrt((x ** 2).sum() * (y ** 2).sum()) + 1e-30)
    r = float(np.clip(r, -1.0, 1.0))
    n = len(x)
    if n <= 2 or abs(r) >= 1.0:
        return r, 0.0
    # t-statistic → two-tailed p-value (normal approx for large n)
    t = r * np.sqrt((n - 2) / (1 - r ** 2 + 1e-30))
    # Approximate p from t using normal CDF (good enough for diagnostics)
    p = float(np.exp(-0.5 * t ** 2) * 2)  # rough upper bound
    return r, p
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint,
    masked_ce_loss, eval_model,
    generate_batch, train_beams,
)

from q_rotation_etch_exp import (
    random_orthogonal, apply_q_rotation,
    reset_beam_params, measure_q_sensitivity,
)

from crystal_reconstruct_exp import (
    collect_gradient_views, install_plates,
    construct_plates_multi_etch,
)

from crystal_fourier_exp import (
    construct_plates_phase_only,
    construct_plates_fft_average,
    analyze_spectral_structure,
)


# ── 1. Magnitude vs Phase Variance Across Rotations ──────────────

def decompose_fft_per_rotation(views: dict) -> dict:
    """For each plate and rotation, compute FFT magnitude and phase.

    Returns per-plate analysis of how magnitude and phase vary
    across Q rotations at each frequency.
    """
    results = []
    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape

        # FFT each rotation's gradient matrix
        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag_stack = np.abs(fft_stack)          # (n_rot, out, in)
        phase_stack = np.angle(fft_stack)       # (n_rot, out, in) in [-π, π]

        # --- Magnitude variance across rotations ---
        # Coefficient of variation at each frequency
        mag_mean = mag_stack.mean(axis=0)       # (out, in)
        mag_std = mag_stack.std(axis=0)         # (out, in)
        mag_cv = mag_std / (mag_mean + 1e-10)   # (out, in) — 0 = identical, >1 = highly variable

        # --- Phase coherence across rotations ---
        # Use circular statistics: mean resultant length
        # R = |mean(exp(i*theta))| → 1 = all same, 0 = uniform random
        unit_phasors = np.exp(1j * phase_stack)  # (n_rot, out, in)
        mean_phasor = unit_phasors.mean(axis=0)  # (out, in)
        phase_coherence = np.abs(mean_phasor)    # (out, in) in [0, 1]

        # --- Separate: which frequencies are "crystal" vs "lens"? ---
        # Crystal frequency: phase coherent (phase_coherence > 0.7) AND low mag CV
        # Lens frequency: phase coherent but high mag CV (Q scales it differently)
        # Noise frequency: phase incoherent (neither crystal nor lens)

        crystal_mask = (phase_coherence > 0.7) & (mag_cv < 0.5)
        lens_mask = (phase_coherence > 0.7) & (mag_cv >= 0.5)
        noise_mask = phase_coherence <= 0.7

        # Energy in each category
        energy = (mag_stack ** 2).mean(axis=0)  # mean energy per freq
        total_energy = energy.sum()
        crystal_energy = energy[crystal_mask].sum() / (total_energy + 1e-10)
        lens_energy = energy[lens_mask].sum() / (total_energy + 1e-10)
        noise_energy = energy[noise_mask].sum() / (total_energy + 1e-10)

        results.append({
            "plate": pidx,
            "shape": f"{out_f}×{in_f}",
            # Aggregate stats
            "mag_cv_mean": float(mag_cv.mean()),
            "mag_cv_median": float(np.median(mag_cv)),
            "phase_coherence_mean": float(phase_coherence.mean()),
            "phase_coherence_median": float(np.median(phase_coherence)),
            # Energy decomposition
            "crystal_energy_frac": float(crystal_energy),
            "lens_energy_frac": float(lens_energy),
            "noise_energy_frac": float(noise_energy),
            # Counts
            "crystal_freq_frac": float(crystal_mask.mean()),
            "lens_freq_frac": float(lens_mask.mean()),
            "noise_freq_frac": float(noise_mask.mean()),
            # Raw arrays for further analysis
            "_mag_cv": mag_cv,
            "_phase_coherence": phase_coherence,
            "_mag_stack": mag_stack,
            "_phase_stack": phase_stack,
            "_fft_stack": fft_stack,
            "_energy": energy,
        })

    return results


# ── 2. Q Transfer Function Analysis ─────────────────────────────

def analyze_q_transfer_function(
    model: HoloModel,
    views: dict,
    rotations: list[np.ndarray],
) -> dict:
    """Can we predict magnitude distortion from Q's weight matrix?

    If Q is a linear lens, the gradient through a ternary plate P is:
        grad_P = f(Q, data)

    In Fourier space, a linear operation on the input translates to
    multiplication in frequency domain. If Q acts as a linear filter
    on the gradient signal, then:
        |FFT(grad_P)| ∝ |H(Q)| * |FFT(crystal_signal)|

    where H(Q) is Q's transfer function.

    We test this by:
    1. Computing |FFT(Q_weights)| for each rotation's Q
    2. Correlating with |FFT(gradient)| at that rotation
    3. If correlated, Q IS the lens and we can deconvolve
    """
    results = []

    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape

        # Get the Q weight matrix for each rotation
        # rotation 0 = original Q, rotation r = R_r.T @ Q_orig
        correlations = []

        for r in range(n_rot):
            # Gradient magnitude spectrum for this rotation
            fft_grad = np.fft.fft2(grad_stack[r])
            mag_grad = np.abs(fft_grad).ravel()

            if r < len(rotations) and rotations[r] is not None:
                # Q weight = R.T @ Q_orig → FFT of rotation matrix
                R = rotations[r]
                # The effective Q for this plate depends on which
                # layer/component it is. For now, use the rotation
                # matrix itself as a proxy for the lens.
                # Resize R to match plate dimensions if needed
                R_cropped = R[:out_f, :in_f]
                fft_R = np.fft.fft2(R_cropped)
                mag_R = np.abs(fft_R).ravel()

                # Correlation between |FFT(R)| and |FFT(grad)|
                if len(mag_R) == len(mag_grad):
                    corr, pval = _pearsonr(mag_R, mag_grad)
                    correlations.append({
                        "rotation": r,
                        "corr": float(corr),
                        "pval": float(pval),
                    })

        results.append({
            "plate": pidx,
            "q_grad_correlations": correlations,
            "mean_corr": float(np.mean([c["corr"] for c in correlations])) if correlations else 0.0,
        })

    return results


# ── 3. Signal Separation: Invariant vs Variable Magnitude ────────

def separate_invariant_magnitude(views: dict) -> dict:
    """Decompose magnitude into rotation-invariant and rotation-variable.

    At each frequency:
      mag_invariant = median(|FFT|) across rotations  (crystal structure)
      mag_variable = |FFT| - mag_invariant             (lens distortion)

    If the lens model is correct:
      - mag_invariant should correlate with phase coherence
        (frequencies where we see the crystal clearly have consistent magnitude)
      - mag_variable should predict how much each rotation's Q distorts
    """
    results = []
    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag_stack = np.abs(fft_stack)

        # Invariant: median across rotations (robust to outliers)
        mag_invariant = np.median(mag_stack, axis=0)  # (out, in)

        # Variable: deviation from invariant per rotation
        mag_variable = mag_stack - mag_invariant[None, :, :]  # (n_rot, out, in)
        mag_var_energy = (mag_variable ** 2).mean(axis=0)  # (out, in)
        mag_inv_energy = mag_invariant ** 2                 # (out, in)

        # Phase coherence for correlation
        unit_phasors = np.exp(1j * np.angle(fft_stack))
        phase_coherence = np.abs(unit_phasors.mean(axis=0))

        # Does magnitude invariance correlate with phase coherence?
        # (If so, the crystal shows up in both magnitude and phase)
        inv_frac = mag_inv_energy / (mag_inv_energy + mag_var_energy + 1e-10)
        corr_inv_coh, pval = _pearsonr(inv_frac.ravel(), phase_coherence.ravel())

        # Fraction of total magnitude energy that is invariant
        total_mag_energy = (mag_stack ** 2).mean()
        invariant_energy_frac = float(mag_inv_energy.mean() / (total_mag_energy + 1e-10))

        results.append({
            "plate": pidx,
            "invariant_energy_frac": invariant_energy_frac,
            "variable_energy_frac": 1.0 - invariant_energy_frac,
            "inv_coherence_corr": float(corr_inv_coh),
            "inv_coherence_pval": float(pval),
            "_mag_invariant": mag_invariant,
            "_mag_variable_energy": mag_var_energy,
            "_inv_frac": inv_frac,
        })

    return results


# ── 4. Reconstruction Methods ────────────────────────────────────

def construct_plates_deconvolved(views: dict, regularization: float = 0.1) -> list[np.ndarray]:
    """Wiener-style deconvolution using empirical lens estimate.

    Instead of throwing away ALL magnitude (phase-only) or keeping ALL
    magnitude (FFT average), use the estimated lens transfer function
    to correct the magnitude.

    Lens estimate: per-rotation magnitude / median magnitude across rotations
    Correction: divide each rotation's FFT by its lens estimate, then average

    Wiener regularization prevents noise amplification where lens is weak.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag_stack = np.abs(fft_stack)

        # Estimate the "crystal magnitude" (invariant across rotations)
        mag_crystal = np.median(mag_stack, axis=0)  # (out, in)

        # For each rotation, estimate and correct the lens
        corrected_stack = np.zeros_like(fft_stack)
        for r in range(n_rot):
            # Lens transfer function: ratio of this rotation's magnitude
            # to the crystal magnitude
            lens = mag_stack[r] / (mag_crystal + 1e-10)

            # Wiener deconvolution: H* / (|H|^2 + λ)
            # Here H = lens, so correction = 1/lens regularized
            wiener = 1.0 / (lens + regularization)

            # Apply correction: scale magnitude, preserve phase
            corrected_stack[r] = fft_stack[r] * wiener

        # Average corrected spectra
        fft_mean = corrected_stack.mean(axis=0)
        consensus = np.fft.ifft2(fft_mean).real

        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_coherence_weighted(views: dict) -> list[np.ndarray]:
    """Adaptive magnitude: keep where consistent, strip where variable.

    At each frequency:
      - High phase coherence AND low mag CV → keep full magnitude (crystal)
      - High phase coherence AND high mag CV → strip magnitude (lens-distorted crystal)
      - Low phase coherence → strip magnitude (noise)

    This is more nuanced than phase-only (which strips ALL magnitude)
    or FFT-average (which keeps ALL magnitude).
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag_stack = np.abs(fft_stack)
        phase_stack = np.angle(fft_stack)

        # Phase coherence
        unit_phasors = np.exp(1j * phase_stack)
        phase_coherence = np.abs(unit_phasors.mean(axis=0))  # (out, in)

        # Magnitude consistency (inverse CV)
        mag_mean = mag_stack.mean(axis=0)
        mag_std = mag_stack.std(axis=0)
        mag_cv = mag_std / (mag_mean + 1e-10)
        mag_consistency = 1.0 / (1.0 + mag_cv)  # (out, in) in (0, 1]

        # Adaptive weight: how much magnitude to keep
        # Keep magnitude where both phase and magnitude are consistent
        keep_mag = phase_coherence * mag_consistency  # (out, in) in [0, 1]

        # Reconstruct: blend between phase-only and full-magnitude
        mean_fft = fft_stack.mean(axis=0)
        mean_phase = np.angle(mean_fft)
        mean_mag = np.abs(mean_fft)

        # phase-only component: unit magnitude, mean phase
        phase_only = np.exp(1j * mean_phase)
        # full component: original mean
        full = mean_fft / (np.abs(mean_fft) + 1e-10) * mean_mag

        # Blend
        blended = keep_mag * full + (1.0 - keep_mag) * phase_only
        consensus = np.fft.ifft2(blended).real

        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_invariant_magnitude(views: dict) -> list[np.ndarray]:
    """Use the rotation-invariant magnitude with mean phase.

    Magnitude = median across rotations (strips lens, keeps crystal structure)
    Phase = circular mean across rotations (consensus direction)

    This should be BETTER than phase-only because it preserves the
    crystal's actual spectral shape while removing Q-dependent distortion.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag_stack = np.abs(fft_stack)

        # Invariant magnitude: median across rotations
        mag_invariant = np.median(mag_stack, axis=0)  # (out, in)

        # Consensus phase: circular mean
        unit_phasors = np.exp(1j * np.angle(fft_stack))
        mean_phasor = unit_phasors.mean(axis=0)
        consensus_phase = np.angle(mean_phasor)

        # Reconstruct with invariant magnitude + consensus phase
        reconstructed = mag_invariant * np.exp(1j * consensus_phase)
        consensus = np.fft.ifft2(reconstructed).real

        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


# ── 5. Scaling Crossover Analysis ────────────────────────────────

def analyze_scaling(
    model: HoloModel,
    seed: int = 42,
    rotation_counts: list[int] | None = None,
) -> dict:
    """Run sign vote, phase-only, deconvolved, and coherence-weighted
    at multiple rotation counts. Find the crossover.

    Memory-safe: collects views one rotation count at a time,
    frees between iterations, clears MLX cache aggressively.
    """
    if rotation_counts is None:
        rotation_counts = [2, 4, 8, 12, 16]

    methods = {
        "sign_vote": construct_plates_multi_etch,
        "phase_only": construct_plates_phase_only,
        "deconvolved": construct_plates_deconvolved,
        "coherence_weighted": construct_plates_coherence_weighted,
        "invariant_magnitude": construct_plates_invariant_magnitude,
    }

    scaling_results = {name: [] for name in methods}

    for n_rot in rotation_counts:
        print(f"\n  === {n_rot} rotations ===", flush=True)

        # Collect views (uses batches_per_rotation=50 to save memory)
        views = collect_gradient_views(
            model, np.random.RandomState(seed + n_rot * 100),
            n_rotations=n_rot, batches_per_rotation=50)

        for method_name, method_fn in methods.items():
            if method_name == "sign_vote":
                plates = method_fn(views, confidence=0.3)
            elif method_name == "deconvolved":
                plates = method_fn(views, regularization=0.5)
            else:
                plates = method_fn(views)

            install_plates(model, plates)
            reset_beam_params(model, np.random.RandomState(seed + 1000))

            gd_losses = train_beams(
                model, np.random.RandomState(seed + 2000),
                n_steps=1000, lr=0.003, max_depth=4)

            ev = eval_model(
                model, np.random.RandomState(seed + 3000),
                n_batches=30, max_depth=4)

            acc = ev["accuracy"]
            scaling_results[method_name].append({
                "n_rot": n_rot,
                "accuracy": float(acc),
                "final_loss": float(ev["loss"]),
            })
            print(f"    {method_name:25s}: {acc:.3f}", flush=True)

            del plates
            mx.clear_cache()

        # Free views before next rotation count
        del views
        mx.clear_cache()

    return scaling_results


# ── Evaluation helper ────────────────────────────────────────────

def evaluate_reconstruction(
    name: str,
    model: HoloModel,
    plate_signs: list[np.ndarray],
    seed: int = 42,
) -> dict:
    """Install plates, reset beams, train, evaluate."""
    print(f"\n  --- {name} ---")
    install_plates(model, plate_signs)
    reset_beam_params(model, np.random.RandomState(seed + 1000))

    gd_losses = train_beams(
        model, np.random.RandomState(seed + 2000),
        n_steps=1000, lr=0.003, max_depth=4)

    ev = eval_model(
        model, np.random.RandomState(seed + 3000),
        n_batches=50, max_depth=4)

    print(f"    Acc: {ev['accuracy']:.3f}  Loss: {ev['loss']:.4f}  "
          f"GD final: {gd_losses[-1]:.4f}")

    return {
        "name": name,
        "accuracy": float(ev["accuracy"]),
        "loss": float(ev["loss"]),
        "gd_final_loss": float(gd_losses[-1]),
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  LENS MECHANISM EXPERIMENT")
    print("  What IS the Q lens distortion?")
    print("=" * 70)

    D_MODEL = 96
    N_LAYERS = 3
    SEED = 42

    model = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(model.parameters())

    pinfo = count_holo_params(model)
    print(f"\n  Model: d={D_MODEL}, layers={N_LAYERS}")
    print(f"  Params: {pinfo['total']:,} total "
          f"({pinfo['plate_positions']:,} plate, {pinfo['beam_params']:,} beam)")

    # ================================================================
    # PHASE 1: Diagnostic — decompose the gradient signal
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  PHASE 1: Gradient Signal Decomposition")
    print(f"{'=' * 70}")

    # Collect views and save the rotation matrices
    n_rot = 8
    rng = np.random.RandomState(SEED + 100)
    rotations = [None]  # rotation 0 = identity
    for r in range(1, n_rot):
        rotations.append(random_orthogonal(D_MODEL, rng))
    # Reset rng for view collection to match
    views_8 = collect_gradient_views(
        model, np.random.RandomState(SEED + 100),
        n_rotations=n_rot, batches_per_rotation=100)

    # 1a. Magnitude vs Phase variance
    print(f"\n  --- Magnitude vs Phase Variance ---")
    plate_types = []
    for _ in range(N_LAYERS):
        plate_types.extend(["K", "V", "O", "FFN"])

    decomp = decompose_fft_per_rotation(views_8)
    print(f"\n  {'Plate':<10s}  {'Type':<4s}  {'MagCV':>6s}  {'PhCoh':>6s}  "
          f"{'Crystal':>8s}  {'Lens':>8s}  {'Noise':>8s}")
    print(f"  {'-'*10}  {'-'*4}  {'-'*6}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}")
    for d in decomp:
        ptype = plate_types[d["plate"]]
        print(f"  Plate {d['plate']:<3d}  {ptype:<4s}  "
              f"{d['mag_cv_mean']:>6.3f}  {d['phase_coherence_mean']:>6.3f}  "
              f"{d['crystal_energy_frac']:>7.1%}  "
              f"{d['lens_energy_frac']:>7.1%}  "
              f"{d['noise_energy_frac']:>7.1%}")

    # Aggregate by plate type
    print(f"\n  --- By plate type ---")
    for ptype in ["K", "V", "O", "FFN"]:
        idxs = [i for i, t in enumerate(plate_types) if t == ptype]
        mag_cv = np.mean([decomp[i]["mag_cv_mean"] for i in idxs])
        ph_coh = np.mean([decomp[i]["phase_coherence_mean"] for i in idxs])
        crystal = np.mean([decomp[i]["crystal_energy_frac"] for i in idxs])
        lens = np.mean([decomp[i]["lens_energy_frac"] for i in idxs])
        noise = np.mean([decomp[i]["noise_energy_frac"] for i in idxs])
        print(f"    {ptype:>3s}: MagCV={mag_cv:.3f}  PhCoh={ph_coh:.3f}  "
              f"Crystal={crystal:.1%}  Lens={lens:.1%}  Noise={noise:.1%}")

    # 1b. Signal separation
    print(f"\n  --- Signal Separation (invariant vs variable magnitude) ---")
    separation = separate_invariant_magnitude(views_8)
    for s in separation:
        ptype = plate_types[s["plate"]]
        print(f"  Plate {s['plate']} ({ptype}): "
              f"invariant={s['invariant_energy_frac']:.1%}  "
              f"variable={s['variable_energy_frac']:.1%}  "
              f"inv↔coh corr={s['inv_coherence_corr']:.3f} "
              f"(p={s['inv_coherence_pval']:.2e})")

    # 1c. Q transfer function
    print(f"\n  --- Q Transfer Function Correlation ---")
    q_analysis = analyze_q_transfer_function(model, views_8, rotations)
    for qa in q_analysis:
        ptype = plate_types[qa["plate"]]
        print(f"  Plate {qa['plate']} ({ptype}): "
              f"mean |FFT(Q)|↔|FFT(grad)| corr = {qa['mean_corr']:.3f}")

    # ================================================================
    # PHASE 2: Reconstruction comparison
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  PHASE 2: Reconstruction Methods (8 rotations)")
    print(f"{'=' * 70}")

    results_8 = []

    def _run_method(name, plates_fn):
        plates = plates_fn()
        r = evaluate_reconstruction(name, model, plates, SEED)
        results_8.append(r)
        del plates
        mx.clear_cache()

    # Baselines
    _run_method("Sign vote",
                lambda: construct_plates_multi_etch(views_8, confidence=0.3))
    _run_method("Phase-only",
                lambda: construct_plates_phase_only(views_8))

    # New methods
    _run_method("Deconvolved (λ=0.1)",
                lambda: construct_plates_deconvolved(views_8, regularization=0.1))
    _run_method("Deconvolved (λ=0.5)",
                lambda: construct_plates_deconvolved(views_8, regularization=0.5))
    _run_method("Deconvolved (λ=1.0)",
                lambda: construct_plates_deconvolved(views_8, regularization=1.0))
    _run_method("Coherence-weighted",
                lambda: construct_plates_coherence_weighted(views_8))
    _run_method("Invariant magnitude",
                lambda: construct_plates_invariant_magnitude(views_8))

    # Summary
    print(f"\n  {'Method':<25s}  {'Acc':>6s}  {'Loss':>7s}  {'GD':>7s}")
    print(f"  {'-'*25}  {'-'*6}  {'-'*7}  {'-'*7}")
    for r in results_8:
        print(f"  {r['name']:<25s}  {r['accuracy']:>6.3f}  "
              f"{r['loss']:>7.4f}  {r['gd_final_loss']:>7.4f}")

    # ================================================================
    # PHASE 3: Scaling crossover
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  PHASE 3: Scaling Crossover (2-32 rotations)")
    print(f"{'=' * 70}")

    # Free phase 2 data before scaling
    del views_8, decomp, separation, q_analysis, results_8
    mx.clear_cache()

    scaling = analyze_scaling(
        model, seed=SEED,
        rotation_counts=[2, 4, 8, 12, 16])

    print(f"\n  --- Accuracy vs Rotation Count ---")
    print(f"  {'n_rot':>5s}  ", end="")
    for name in scaling:
        print(f"{name:>14s}  ", end="")
    print()
    print(f"  {'-'*5}  " + "  ".join(['-'*14] * len(scaling)))

    # Get all rotation counts from first method
    first_method = list(scaling.values())[0]
    for i, entry in enumerate(first_method):
        n_r = entry["n_rot"]
        print(f"  {n_r:>5d}  ", end="")
        for name in scaling:
            acc = scaling[name][i]["accuracy"]
            print(f"{acc:>14.3f}  ", end="")
        print()

    # ================================================================
    # Save everything
    # ================================================================
    out_path = Path("results/lens-mechanism")
    out_path.mkdir(parents=True, exist_ok=True)

    # Strip numpy arrays for JSON
    decomp_save = []
    for d in decomp:
        d_save = {k: v for k, v in d.items() if not k.startswith("_")}
        decomp_save.append(d_save)

    separation_save = []
    for s in separation:
        s_save = {k: v for k, v in s.items() if not k.startswith("_")}
        separation_save.append(s_save)

    save_data = {
        "decomposition": decomp_save,
        "signal_separation": separation_save,
        "q_transfer_function": q_analysis,
        "reconstruction_8rot": results_8,
        "scaling": {name: entries for name, entries in scaling.items()},
    }

    with open(out_path / "results.json", "w") as f:
        json.dump(save_data, f, indent=2, default=str)

    print(f"\n  Results saved to {out_path}/")
    print(f"\n{'=' * 70}")
    print("  DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
