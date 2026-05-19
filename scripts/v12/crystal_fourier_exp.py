"""Crystal Fourier Reconstruction — Diffraction Pattern Assembly.

Instead of accumulating gradient signs in real space (shadow voting),
accumulate in Fourier space (diffraction pattern assembly) then
inverse FFT to reconstruct the crystal.

If Q rotations sample different spatial frequencies of the crystal,
Fourier accumulation preserves phase coherence that real-space
averaging destroys.

Methods:
  A: Sign vote in real space (current best — baseline)
  B: FFT accumulate → IFFT → sign (complex average in freq space)
  C: Magnitude-weighted FFT (weight by spectral energy)
  D: Phase-only accumulate (ignore magnitudes, average unit-phasors)
  E: Hybrid: FFT for confident positions, sign vote for rest

All methods use the same gradient observations from 8 Q rotations.

License: MIT
"""

from __future__ import annotations

import json
import time
import sys
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model,
    generate_batch, train_beams,
)

from q_rotation_etch_exp import (
    reset_beam_params, measure_q_sensitivity,
    etch_with_rotation,
)

from crystal_reconstruct_exp import (
    collect_gradient_views, install_plates,
    construct_plates_multi_etch,
)


# ── Fourier Reconstruction Methods ───────────────────────────────

def construct_plates_fft_average(views: dict) -> list[np.ndarray]:
    """Method B: FFT accumulation → IFFT → sign.

    For each plate:
      1. FFT2 each rotation's gradient matrix
      2. Average the complex spectra across rotations
      3. IFFT2 → consensus gradient in real space
      4. sign() → plate weights

    Phase-coherent components (consistent across rotations) reinforce.
    Phase-incoherent components (view-specific) cancel.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        # FFT2 each rotation's gradient matrix
        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        # Average in frequency space (complex average preserves phase)
        fft_mean = fft_stack.mean(axis=0)

        # IFFT2 → real space consensus
        consensus = np.fft.ifft2(fft_mean).real

        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_fft_mag_weighted(views: dict) -> list[np.ndarray]:
    """Method C: Magnitude-weighted FFT accumulation.

    Weight each rotation's FFT contribution by its spectral magnitude.
    Rotations with strong signal at a frequency get more influence
    at that frequency. Weak signals are downweighted.

    This compensates for lens distortion: Q rotations that clearly
    see a particular frequency component get more say about it.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        # Magnitude of each rotation's spectrum
        magnitudes = np.abs(fft_stack)  # (n_rot, out, in)
        total_mag = magnitudes.sum(axis=0) + 1e-10  # (out, in)

        # Weighted average: weight each rotation by its magnitude
        # at each frequency
        fft_weighted = (fft_stack * magnitudes).sum(axis=0) / total_mag

        consensus = np.fft.ifft2(fft_weighted).real
        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_phase_only(views: dict) -> list[np.ndarray]:
    """Method D: Phase-only accumulation.

    Ignore magnitudes entirely. Normalize each FFT to unit phasors
    (complex numbers on the unit circle), then average.

    This focuses purely on whether rotations AGREE on the direction
    (phase) at each frequency, ignoring how strongly they see it.
    Phase agreement = structural consistency across views.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape

        phasor_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_r = np.fft.fft2(grad_stack[r])
            # Normalize to unit phasors (magnitude = 1)
            mag = np.abs(fft_r) + 1e-10
            phasor_stack[r] = fft_r / mag

        # Average phasors — high agreement → large resultant
        # Low agreement → cancellation
        phasor_mean = phasor_stack.mean(axis=0)

        # The magnitude of the mean phasor = phase coherence
        # (1.0 = all rotations agree, 0.0 = random phases)
        coherence = np.abs(phasor_mean)

        # IFFT of the coherence-weighted mean phasor
        consensus = np.fft.ifft2(phasor_mean).real
        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_hybrid(views: dict, coherence_threshold: float = 0.5) -> list[np.ndarray]:
    """Method E: Hybrid — FFT where coherent, sign vote elsewhere.

    Use phase coherence to decide per-frequency:
      High coherence → trust the FFT reconstruction
      Low coherence → fall back to real-space sign vote

    This uses FFT for the crystal's strong features and
    sign vote for the noisy positions.
    """
    plates = []
    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape

        # FFT path: phase-coherent reconstruction
        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        mag = np.abs(fft_stack) + 1e-10
        phasors = fft_stack / mag
        phasor_mean = phasors.mean(axis=0)
        coherence = np.abs(phasor_mean)  # (out, in) in [0, 1]

        # FFT reconstruction (magnitude-weighted)
        total_mag = mag.sum(axis=0) + 1e-10
        fft_weighted = (fft_stack * mag).sum(axis=0) / total_mag
        fft_consensus = np.fft.ifft2(fft_weighted).real

        # Sign vote path (real-space)
        sign_stack = views["sign_accum_stacks"][pidx]
        sign_consensus = sign_stack.sum(axis=0)

        # Hybrid: use FFT where coherent, sign vote where not
        # Map coherence from freq space to real space
        coherence_real = np.fft.ifft2(coherence).real
        coherence_real = np.abs(coherence_real)
        coherence_real = coherence_real / (coherence_real.max() + 1e-10)

        # Blend
        signs_fft = np.sign(fft_consensus)
        signs_vote = np.sign(sign_consensus)
        mask = coherence_real > coherence_threshold
        signs = np.where(mask, signs_fft, signs_vote)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


# ── Spectral Analysis ────────────────────────────────────────────

def analyze_spectral_structure(views: dict) -> dict:
    """Analyze the Fourier structure of the gradient observations."""
    analysis = []
    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape

        fft_stack = np.zeros((n_rot, out_f, in_f), dtype=np.complex128)
        for r in range(n_rot):
            fft_stack[r] = np.fft.fft2(grad_stack[r])

        # Phase coherence across rotations at each frequency
        mag = np.abs(fft_stack) + 1e-10
        phasors = fft_stack / mag
        phasor_mean = phasors.mean(axis=0)
        coherence = np.abs(phasor_mean)  # (out, in)

        # Spectral energy distribution
        energy = (np.abs(fft_stack) ** 2).mean(axis=0)
        total_energy = energy.sum()

        # What fraction of spectrum has high coherence?
        high_coh = (coherence > 0.7).mean()
        med_coh = ((coherence > 0.3) & (coherence <= 0.7)).mean()
        low_coh = (coherence <= 0.3).mean()

        # DC component (frequency 0,0) coherence
        dc_coherence = float(coherence[0, 0])

        # Energy in coherent vs incoherent components
        coherent_energy = float((energy * (coherence > 0.5)).sum() / (total_energy + 1e-10))

        analysis.append({
            "plate": pidx,
            "shape": f"{out_f}×{in_f}",
            "dc_coherence": dc_coherence,
            "high_coherence_frac": float(high_coh),
            "med_coherence_frac": float(med_coh),
            "low_coherence_frac": float(low_coh),
            "coherent_energy_frac": coherent_energy,
            "mean_coherence": float(coherence.mean()),
        })
    return analysis


# ── Evaluation ───────────────────────────────────────────────────

def evaluate_method(
    name: str,
    model: HoloModel,
    plate_signs: list[np.ndarray],
    seed: int = 42,
) -> dict:
    """Install plates, reset beams, train, evaluate."""
    print(f"\n  --- {name} ---")
    install_plates(model, plate_signs)
    reset_beam_params(model, np.random.RandomState(seed + 1000))

    gd_losses = train_beams(model, np.random.RandomState(seed + 2000),
                            n_steps=1000, lr=0.003, max_depth=4)

    ev = eval_model(model, np.random.RandomState(seed + 3000),
                    n_batches=50, max_depth=4)

    q_sens = measure_q_sensitivity(
        model, np.random.RandomState(seed + 4000),
        n_rotations=16, n_eval_batches=20)

    print(f"    Acc: {ev['accuracy']:.3f}  Loss: {ev['loss']:.4f}  "
          f"GD: {gd_losses[-1]:.4f}  Q-σ: {q_sens['std']:.3f}")

    return {
        "name": name,
        "final_accuracy": ev["accuracy"],
        "final_loss": ev["loss"],
        "gd_final_loss": gd_losses[-1],
        "q_sensitivity": q_sens,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Crystal Fourier Reconstruction Experiment")
    print("  Diffraction pattern assembly vs shadow voting")
    print()

    D_MODEL = 96
    N_LAYERS = 3
    N_ROTATIONS = 8
    BATCHES_PER_ROT = 100
    SEED = 42

    model = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    print(f"  Model: d={D_MODEL}, layers={N_LAYERS}")

    # Collect gradient views
    print(f"\n{'='*60}")
    print(f"  Collecting {N_ROTATIONS} gradient views")
    print(f"{'='*60}")
    views = collect_gradient_views(
        model, np.random.RandomState(SEED + 100),
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
    )

    # Spectral analysis
    print(f"\n{'='*60}")
    print(f"  Spectral analysis")
    print(f"{'='*60}")
    spectral = analyze_spectral_structure(views)
    for s in spectral:
        print(f"  Plate {s['plate']} ({s['shape']}): "
              f"DC-coh={s['dc_coherence']:.3f}  "
              f"mean-coh={s['mean_coherence']:.3f}  "
              f"high={s['high_coherence_frac']:.1%}  "
              f"coh-energy={s['coherent_energy_frac']:.1%}")

    # Construct plates with each method
    print(f"\n{'='*60}")
    print(f"  Reconstruction methods")
    print(f"{'='*60}")

    results = []

    # A: Sign vote (baseline)
    plates_a = construct_plates_multi_etch(views, confidence=0.3)
    r = evaluate_method("A: Sign vote", model, plates_a, seed=SEED)
    results.append(r)

    # B: FFT average
    plates_b = construct_plates_fft_average(views)
    r = evaluate_method("B: FFT average", model, plates_b, seed=SEED)
    results.append(r)

    # C: FFT magnitude-weighted
    plates_c = construct_plates_fft_mag_weighted(views)
    r = evaluate_method("C: FFT mag-weighted", model, plates_c, seed=SEED)
    results.append(r)

    # D: Phase-only
    plates_d = construct_plates_phase_only(views)
    r = evaluate_method("D: Phase-only", model, plates_d, seed=SEED)
    results.append(r)

    # E: Hybrid (threshold 0.3)
    plates_e3 = construct_plates_hybrid(views, coherence_threshold=0.3)
    r = evaluate_method("E: Hybrid (t=0.3)", model, plates_e3, seed=SEED)
    results.append(r)

    # E: Hybrid (threshold 0.5)
    plates_e5 = construct_plates_hybrid(views, coherence_threshold=0.5)
    r = evaluate_method("E: Hybrid (t=0.5)", model, plates_e5, seed=SEED)
    results.append(r)

    # Agreement analysis
    print(f"\n  Method agreement with sign vote (A):")
    all_plates = [
        ("B:FFT-avg", plates_b), ("C:FFT-mag", plates_c),
        ("D:Phase", plates_d), ("E:Hyb-0.3", plates_e3),
        ("E:Hyb-0.5", plates_e5),
    ]
    for name, pl in all_plates:
        agree = np.mean([
            np.mean(np.sign(a) == np.sign(b))
            for a, b in zip(plates_a, pl)
        ])
        print(f"    A vs {name:12s}: {agree:.1%}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Method':<22s}  {'Acc':>6s}  {'GD loss':>8s}  {'Q-σ':>6s}")
    print(f"  {'-'*22}  {'-'*6}  {'-'*8}  {'-'*6}")
    for r in results:
        print(f"  {r['name']:<22s}  {r['final_accuracy']:>6.3f}  "
              f"{r['gd_final_loss']:>8.4f}  "
              f"{r['q_sensitivity']['std']:>6.3f}")

    # Save
    out_path = Path("results/crystal-fourier")
    out_path.mkdir(parents=True, exist_ok=True)
    save_results = []
    for r in results:
        save_results.append(r)
    with open(out_path / "results.json", "w") as f:
        json.dump(save_results, f, indent=2, default=str)
    with open(out_path / "spectral.json", "w") as f:
        json.dump(spectral, f, indent=2)
    print(f"\n  Results saved to {out_path}/")


if __name__ == "__main__":
    main()
