"""Combined Crystal Reconstruction — Phase-only + Sign Vote + Per-plate Strategy.

Combine the two best approaches with the spectral insight:
  - V/O/FFN plates: phase-only Fourier (94% coherent energy)
  - K plates: sign vote or leave for GD (13% coherent energy)

Conditions:
  A: Sign vote only (baseline from multi-rot etch)
  B: Phase-only only (from Fourier experiment)
  C: Combined — phase-only for V/O/FFN, sign vote for K
  D: Combined — phase-only for V/O/FFN, leave K for GD (+1 default)
  E: Phase-only init → refine with sign vote (two-pass)
  F: Phase-only with 16 rotations (more cameras)
  G: Combined with 16 rotations

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
    holo_plate_fingerprint,
    masked_ce_loss, eval_model,
    generate_batch, train_beams,
)

from q_rotation_etch_exp import (
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


# ── Per-plate Strategy ────────────────────────────────────────────

def classify_plates(n_layers: int) -> list[str]:
    """Classify each plate as K, V, O, or FFN.

    Plate ordering per layer: K, V, O, FFN (from _get_plates).
    """
    types = []
    for _ in range(n_layers):
        types.extend(["K", "V", "O", "FFN"])
    return types


def construct_plates_combined(
    views: dict,
    n_layers: int,
    k_strategy: str = "sign",  # "sign", "default", "phase"
    vof_strategy: str = "phase",  # "phase", "sign"
    sign_confidence: float = 0.3,
) -> list[np.ndarray]:
    """Per-plate strategy: different reconstruction for K vs V/O/FFN.

    K plates have low spectral coherence (Q-dependent interface).
    V/O/FFN plates have high coherence (universal crystal structure).
    """
    plate_types = classify_plates(n_layers)
    plates_sign = construct_plates_multi_etch(views, confidence=sign_confidence)
    plates_phase = construct_plates_phase_only(views)

    result = []
    for pidx, ptype in enumerate(plate_types):
        if ptype == "K":
            if k_strategy == "sign":
                result.append(plates_sign[pidx])
            elif k_strategy == "default":
                # Leave as +1 (let GD figure it out)
                result.append(np.ones_like(plates_sign[pidx]))
            elif k_strategy == "phase":
                result.append(plates_phase[pidx])
            else:
                result.append(plates_sign[pidx])
        else:  # V, O, FFN
            if vof_strategy == "phase":
                result.append(plates_phase[pidx])
            else:
                result.append(plates_sign[pidx])
    return result


def construct_plates_two_pass(
    views: dict,
    sign_confidence: float = 0.3,
) -> list[np.ndarray]:
    """Two-pass: phase-only first (structure), then sign vote refinement.

    Pass 1: Phase-only reconstruction → initial crystal estimate
    Pass 2: Where sign vote disagrees with high confidence → override

    Phase gives the broad structure; sign vote corrects local errors
    where the real-space signal is unambiguous.
    """
    plates_phase = construct_plates_phase_only(views)
    n_rot = views["grad_stacks"][0].shape[0]

    result = []
    for pidx, phase_plate in enumerate(plates_phase):
        sign_stack = views["sign_accum_stacks"][pidx]
        # Accumulated signs across all rotations
        acc = sign_stack.sum(axis=0)
        conf = np.abs(acc) / n_rot

        # Start with phase reconstruction
        combined = phase_plate.copy()

        # Override with sign vote where highly confident AND disagrees
        sign_val = np.sign(acc)
        disagree = (sign_val != phase_plate) & (sign_val != 0)
        confident = conf > 0.6  # high confidence threshold for override
        override = disagree & confident

        combined = np.where(override, sign_val, combined)
        combined = np.where(combined == 0, 1.0, combined)
        result.append(combined.astype(np.float32))

    return result


# ── Evaluation ───────────────────────────────────────────────────

def evaluate_method(
    name: str,
    model: HoloModel,
    plate_signs: list[np.ndarray],
    seed: int = 42,
    n_trials: int = 3,
) -> dict:
    """Install plates, run multiple GD trials, evaluate."""
    print(f"\n  --- {name} ---")
    install_plates(model, plate_signs)

    trial_accs = []
    trial_losses = []
    for trial in range(n_trials):
        ts = seed + trial * 200
        reset_beam_params(model, np.random.RandomState(ts + 1000))
        gd_losses = train_beams(model, np.random.RandomState(ts + 2000),
                                n_steps=1000, lr=0.003, max_depth=4)
        ev = eval_model(model, np.random.RandomState(ts + 3000),
                        n_batches=30, max_depth=4)
        trial_accs.append(ev["accuracy"])
        trial_losses.append(ev["loss"])

    acc_mean = float(np.mean(trial_accs))
    acc_std = float(np.std(trial_accs))

    # Q-sensitivity on best trial
    best_trial = int(np.argmax(trial_accs))
    best_seed = seed + best_trial * 200
    reset_beam_params(model, np.random.RandomState(best_seed + 1000))
    train_beams(model, np.random.RandomState(best_seed + 2000),
                n_steps=1000, lr=0.003, max_depth=4)
    q_sens = measure_q_sensitivity(
        model, np.random.RandomState(seed + 5000),
        n_rotations=16, n_eval_batches=15)

    print(f"    Acc: {acc_mean:.3f}±{acc_std:.3f}  "
          f"Best: {max(trial_accs):.3f}  "
          f"Q-σ: {q_sens['std']:.3f}")

    return {
        "name": name,
        "acc_mean": acc_mean,
        "acc_std": acc_std,
        "acc_best": float(max(trial_accs)),
        "trial_accs": trial_accs,
        "gd_final_loss": float(np.mean(trial_losses)),
        "q_sensitivity": q_sens,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Combined Crystal Reconstruction Experiment")
    print("  Phase-only + Sign Vote + Per-plate Strategy")
    print()

    D_MODEL = 96
    N_LAYERS = 3
    SEED = 42

    model = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    print(f"  Model: d={D_MODEL}, layers={N_LAYERS}")

    plate_types = classify_plates(N_LAYERS)
    print(f"  Plate types: {plate_types}")

    results_all = []

    # ── 8 rotations ──
    print(f"\n{'='*60}")
    print(f"  8 Q rotations × 100 batches")
    print(f"{'='*60}")

    views_8 = collect_gradient_views(
        model, np.random.RandomState(SEED + 100),
        n_rotations=8, batches_per_rotation=100)

    # Spectral summary
    spectral = analyze_spectral_structure(views_8)
    for s in spectral:
        ptype = plate_types[s["plate"]]
        print(f"  Plate {s['plate']} ({ptype}): coh={s['mean_coherence']:.3f}  "
              f"coh-energy={s['coherent_energy_frac']:.1%}")

    # A: Sign vote only
    plates_a = construct_plates_multi_etch(views_8, confidence=0.3)
    r = evaluate_method("A: Sign vote (8rot)", model, plates_a, seed=SEED)
    results_all.append(r)

    # B: Phase-only
    plates_b = construct_plates_phase_only(views_8)
    r = evaluate_method("B: Phase-only (8rot)", model, plates_b, seed=SEED)
    results_all.append(r)

    # C: Combined — phase V/O/FFN, sign K
    plates_c = construct_plates_combined(views_8, N_LAYERS,
                                         k_strategy="sign", vof_strategy="phase")
    r = evaluate_method("C: Phase+Sign-K (8rot)", model, plates_c, seed=SEED)
    results_all.append(r)

    # D: Combined — phase V/O/FFN, default K
    plates_d = construct_plates_combined(views_8, N_LAYERS,
                                         k_strategy="default", vof_strategy="phase")
    r = evaluate_method("D: Phase+Default-K (8rot)", model, plates_d, seed=SEED)
    results_all.append(r)

    # E: Two-pass (phase init → sign refinement)
    plates_e = construct_plates_two_pass(views_8)
    r = evaluate_method("E: Two-pass (8rot)", model, plates_e, seed=SEED)
    results_all.append(r)

    # ── 16 rotations ──
    print(f"\n{'='*60}")
    print(f"  16 Q rotations × 100 batches")
    print(f"{'='*60}")

    views_16 = collect_gradient_views(
        model, np.random.RandomState(SEED + 200),
        n_rotations=16, batches_per_rotation=100)

    # F: Phase-only with 16 rotations
    plates_f = construct_plates_phase_only(views_16)
    r = evaluate_method("F: Phase-only (16rot)", model, plates_f, seed=SEED)
    results_all.append(r)

    # G: Combined with 16 rotations
    plates_g = construct_plates_combined(views_16, N_LAYERS,
                                         k_strategy="sign", vof_strategy="phase")
    r = evaluate_method("G: Phase+Sign-K (16rot)", model, plates_g, seed=SEED)
    results_all.append(r)

    # H: Two-pass with 16 rotations
    plates_h = construct_plates_two_pass(views_16)
    r = evaluate_method("H: Two-pass (16rot)", model, plates_h, seed=SEED)
    results_all.append(r)

    # I: Sign vote with 16 rotations (fair comparison)
    plates_i = construct_plates_multi_etch(views_16, confidence=0.3)
    r = evaluate_method("I: Sign vote (16rot)", model, plates_i, seed=SEED)
    results_all.append(r)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Method':<27s}  {'Acc':>6s}  {'±':>5s}  {'Best':>6s}  "
          f"{'Q-σ':>6s}")
    print(f"  {'-'*27}  {'-'*6}  {'-'*5}  {'-'*6}  {'-'*6}")
    for r in results_all:
        print(f"  {r['name']:<27s}  {r['acc_mean']:>6.3f}  "
              f"{r['acc_std']:>5.3f}  {r['acc_best']:>6.3f}  "
              f"{r['q_sensitivity']['std']:>6.3f}")

    # Save
    out_path = Path("results/crystal-combined")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "results.json", "w") as f:
        json.dump(results_all, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path / 'results.json'}")


if __name__ == "__main__":
    main()
