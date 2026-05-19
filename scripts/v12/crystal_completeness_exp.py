"""Crystal Completeness — How many Q rotations to close the basin?

If enough Q rotations make the crystal rotation-invariant, Q-σ → 0
and GD finds the basin from any starting Q. The latching problem
disappears.

Sweep: 1, 2, 4, 8, 16, 32 rotations × 50 batches each.
Fixed per-rotation budget so we're only measuring rotation count.
Track: accuracy, Q-sensitivity (σ and μ), GD convergence.

The stopping criterion: Q-σ converges → crystal is complete.

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
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model,
    generate_batch, train_beams,
)

from q_rotation_etch_exp import (
    random_orthogonal, reset_beam_params,
    etch_with_rotation,
)


def measure_q_sensitivity_detailed(
    model: HoloModel,
    rng: np.random.RandomState,
    n_rotations: int = 32,
    n_eval_batches: int = 20,
    max_depth: int = 4,
) -> dict:
    """Detailed Q-sensitivity: more rotations, track distribution."""
    orig_q_weights = [mx.array(layer.attn.q_proj.weight)
                      for layer in model.layers]

    accuracies = []
    losses = []
    for rot_idx in range(n_rotations):
        if rot_idx == 0:
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(orig_w)
                mx.eval(layer.attn.q_proj.weight)
        else:
            R = random_orthogonal(model.d_model, rng)
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(R.T) @ orig_w
                mx.eval(layer.attn.q_proj.weight)

        ev = eval_model(model, np.random.RandomState(rot_idx + 9999),
                        n_batches=n_eval_batches, max_depth=max_depth)
        accuracies.append(ev["accuracy"])
        losses.append(ev["loss"])

    # Restore
    for layer, orig_w in zip(model.layers, orig_q_weights):
        layer.attn.q_proj.weight = mx.array(orig_w)
        mx.eval(layer.attn.q_proj.weight)

    accs = np.array(accuracies)
    ls = np.array(losses)
    return {
        "acc_mean": float(accs.mean()),
        "acc_std": float(accs.std()),
        "acc_min": float(accs.min()),
        "acc_max": float(accs.max()),
        "acc_p25": float(np.percentile(accs, 25)),
        "acc_p75": float(np.percentile(accs, 75)),
        "loss_mean": float(ls.mean()),
        "loss_std": float(ls.std()),
        "n_rotations_tested": n_rotations,
    }


def run_rotation_sweep_point(
    n_etch_rotations: int,
    batches_per_rotation: int = 50,
    d_model: int = 96,
    n_layers: int = 3,
    seed: int = 42,
    n_gd_steps: int = 1000,
    n_gd_trials: int = 3,
) -> dict:
    """Run one point on the rotation sweep."""
    print(f"\n{'='*60}")
    print(f"  {n_etch_rotations} rotations × {batches_per_rotation} batches "
          f"= {n_etch_rotations * batches_per_rotation} total")
    print(f"{'='*60}")

    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    # Etch
    t0 = time.time()
    etch_result = etch_with_rotation(
        model, np.random.RandomState(seed),
        n_rotations=n_etch_rotations,
        batches_per_rotation=batches_per_rotation,
        confidence=0.6,
    )
    etch_time = time.time() - t0
    print(f"  Etch: {etch_result['total_flipped']} flips "
          f"({etch_result['flip_fraction']:.1%}) in {etch_time:.1f}s")

    # GD from multiple random Q inits (to measure variance)
    trial_accs = []
    trial_losses = []
    for trial in range(n_gd_trials):
        trial_seed = seed + 1000 + trial * 200
        reset_beam_params(model, np.random.RandomState(trial_seed))

        gd_losses = train_beams(
            model, np.random.RandomState(trial_seed + 100),
            n_steps=n_gd_steps, lr=0.003, max_depth=4)

        ev = eval_model(model, np.random.RandomState(trial_seed + 200),
                        n_batches=30, max_depth=4)
        trial_accs.append(ev["accuracy"])
        trial_losses.append(ev["loss"])
        print(f"  Trial {trial}: acc={ev['accuracy']:.3f} "
              f"loss={ev['loss']:.4f} GD={gd_losses[-1]:.4f}")

    # Q-sensitivity on the best trial
    best_trial = int(np.argmax(trial_accs))
    best_seed = seed + 1000 + best_trial * 200
    reset_beam_params(model, np.random.RandomState(best_seed))
    train_beams(model, np.random.RandomState(best_seed + 100),
                n_steps=n_gd_steps, lr=0.003, max_depth=4)

    q_sens = measure_q_sensitivity_detailed(
        model, np.random.RandomState(seed + 5000),
        n_rotations=32, n_eval_batches=15)

    acc_mean = float(np.mean(trial_accs))
    acc_std = float(np.std(trial_accs))

    print(f"  ── Result: acc={acc_mean:.3f}±{acc_std:.3f}  "
          f"Q-σ={q_sens['acc_std']:.4f}  "
          f"Q-range=[{q_sens['acc_min']:.3f},{q_sens['acc_max']:.3f}]")

    return {
        "n_etch_rotations": n_etch_rotations,
        "total_batches": n_etch_rotations * batches_per_rotation,
        "flips": etch_result["total_flipped"],
        "flip_fraction": etch_result["flip_fraction"],
        "acc_mean": acc_mean,
        "acc_std": acc_std,
        "trial_accs": trial_accs,
        "trial_losses": trial_losses,
        "q_sensitivity": q_sens,
        "etch_time": etch_time,
    }


def main():
    print("Crystal Completeness Sweep")
    print("  How many Q rotations to close the basin?")
    print()

    BATCHES_PER_ROT = 50
    SEED = 42

    rotation_counts = [1, 2, 4, 8, 16, 32]
    results = []

    for n_rot in rotation_counts:
        r = run_rotation_sweep_point(
            n_etch_rotations=n_rot,
            batches_per_rotation=BATCHES_PER_ROT,
            seed=SEED,
            n_gd_trials=3,
            n_gd_steps=1000,
        )
        results.append(r)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  CRYSTAL COMPLETENESS SWEEP")
    print(f"{'='*60}")
    print(f"  {'Rots':>4s}  {'Total':>5s}  {'Flips':>6s}  "
          f"{'Acc':>6s}  {'±':>5s}  "
          f"{'Q-σ':>6s}  {'Q-min':>6s}  {'Q-max':>6s}  {'Q-IQR':>6s}")
    print(f"  {'-'*4}  {'-'*5}  {'-'*6}  "
          f"{'-'*6}  {'-'*5}  "
          f"{'-'*6}  {'-'*6}  {'-'*6}  {'-'*6}")
    for r in results:
        qs = r["q_sensitivity"]
        iqr = qs["acc_p75"] - qs["acc_p25"]
        print(f"  {r['n_etch_rotations']:>4d}  "
              f"{r['total_batches']:>5d}  "
              f"{r['flips']:>6d}  "
              f"{r['acc_mean']:>6.3f}  "
              f"{r['acc_std']:>5.3f}  "
              f"{qs['acc_std']:>6.4f}  "
              f"{qs['acc_min']:>6.3f}  "
              f"{qs['acc_max']:>6.3f}  "
              f"{iqr:>6.4f}")

    # Convergence check
    q_sigmas = [r["q_sensitivity"]["acc_std"] for r in results]
    print(f"\n  Q-σ trajectory: {['%.4f' % s for s in q_sigmas]}")
    if len(q_sigmas) >= 2:
        last_delta = abs(q_sigmas[-1] - q_sigmas[-2])
        print(f"  Last Δ(Q-σ): {last_delta:.4f}")
        if last_delta < 0.005:
            print(f"  ✓ Q-σ converged (Δ < 0.005)")
        else:
            print(f"  ✗ Q-σ still changing (Δ ≥ 0.005)")

    # Save
    out_path = Path("results/crystal-completeness")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path / 'results.json'}")


if __name__ == "__main__":
    main()
