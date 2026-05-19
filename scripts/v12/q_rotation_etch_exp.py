"""Q-Rotation Etching Experiment — Tomographic Crystal Formation.

Tests whether etching ternary plates from multiple Q rotations produces
a more complete crystal than single-rotation etching.

Setup (mini model from d_sweep_v2):
  - HoloModel: d_model=96, 3 layers, ~27K plate positions, ~10K beam params
  - Task: nested combinator reduction (K, I, B, C), depths 1-4
  - TernaryCausalAttention: Q is continuous, K/V/O are ternary plates

Experiment conditions:
  1. Baseline:  1 etch pass (current approach, no rotation)
  2. 2 rotations: etch from 2 orthogonal Q viewpoints
  3. 4 rotations: etch from 4 orthogonal Q viewpoints
  4. 8 rotations: etch from 8 orthogonal Q viewpoints
  5. Control: 8× etch batches at single rotation (same compute budget as #4)

For each condition:
  - Etch plates → freeze → train beams (GD on continuous params)
  - Measure: eval accuracy, plate fingerprint diversity, Q-sensitivity

The key metric: does multi-rotation etching produce plates that work
from more Q starting points? And does that translate to better GD convergence?

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
import mlx.optimizers as optim
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID, ID2TOK,
    TernaryLinear,
    TernaryCausalAttention, HoloBeamLayer, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model, eval_by_depth,
    generate_batch, generate_example,
    _zero_plate_grads, train_beams,
)


# ── Q-Rotation Utilities ──────────────────────────────────────────

def random_orthogonal(d: int, rng: np.random.RandomState) -> np.ndarray:
    """Generate a random orthogonal matrix via QR decomposition."""
    A = rng.randn(d, d).astype(np.float32)
    Q, R = np.linalg.qr(A)
    # Fix sign ambiguity: ensure det(Q) = +1
    Q = Q * np.sign(np.diag(R))[None, :]
    return Q


def apply_q_rotation(model: HoloModel, rotation: np.ndarray):
    """Apply an orthogonal rotation to all Q projections in the model.

    Q_new = Q_old @ R

    This changes which facet of the ternary plates the query beam
    illuminates, without changing the plates themselves.
    """
    R = mx.array(rotation)
    for layer in model.layers:
        q_weight = layer.attn.q_proj.weight  # (d_model, d_model)
        # nn.Linear: output = x @ W.T, so W is (d_out, d_in)
        # Rotating Q space: W_new = R.T @ W (rotate the output space)
        layer.attn.q_proj.weight = R.T @ q_weight
        mx.eval(layer.attn.q_proj.weight)


def reset_q_projections(model: HoloModel, rng: np.random.RandomState):
    """Reset Q projections to fresh random initialization."""
    d = model.d_model
    for layer in model.layers:
        w = rng.randn(d, d).astype(np.float32) * (d ** -0.5)
        layer.attn.q_proj.weight = mx.array(w)
        mx.eval(layer.attn.q_proj.weight)


def reset_beam_params(model: HoloModel, rng: np.random.RandomState):
    """Reset all continuous (beam) parameters to fresh random init.

    Plates are left unchanged. This resets the model to a fresh
    starting point for GD while preserving etched plate structure.
    """
    d = model.d_model
    for layer in model.layers:
        # Q projection
        w = rng.randn(d, d).astype(np.float32) * (d ** -0.5)
        layer.attn.q_proj.weight = mx.array(w)
        # K/V/O beam scales
        layer.attn.k_scale = mx.ones((d,))
        layer.attn.v_scale = mx.ones((d,))
        layer.attn.o_scale = mx.ones((d,))
        # FFN scale/bias
        layer.ffn_scale = mx.ones((d,))
        layer.ffn_bias = mx.zeros((d,))
        # Norms: reset to default (weight=1, bias=0)
        layer.attn_norm.weight = mx.ones((d,))
        layer.attn_norm.bias = mx.zeros((d,))
        layer.ffn_norm.weight = mx.ones((d,))
        layer.ffn_norm.bias = mx.zeros((d,))
    mx.eval(model.parameters())


# ── Etch with Q rotation ──────────────────────────────────────────

def _extract_plate_grad(grads, layer_idx, plate_name):
    """Extract gradient for a specific plate from the gradient tree."""
    parts = plate_name.split(".")
    g = grads["layers"][layer_idx]
    for part in parts:
        g = g[part]
    return g["weight"]


def etch_with_rotation(
    model: HoloModel,
    rng: np.random.RandomState,
    n_rotations: int = 1,
    batches_per_rotation: int = 200,
    batch_size: int = 32,
    max_depth: int = 4,
    confidence: float = 0.6,
) -> dict:
    """Etch plates from multiple Q rotations (tomographic etching).

    For each rotation:
      1. Apply orthogonal rotation to Q projections
      2. Run batches, accumulate sign(gradient) for each plate
      3. After all rotations, flip confident positions

    Total compute: n_rotations × batches_per_rotation batches.

    Returns: dict with flipped count, fraction, per-rotation stats.
    """
    before = holo_plate_fingerprint(model)

    plates = _get_plates(model)
    # Accumulate across ALL rotations
    accumulators = []
    for _, plate in plates:
        shape = (plate.out_features, plate.in_features)
        accumulators.append(np.zeros(shape, dtype=np.float64))

    plate_paths = []
    for i, layer in enumerate(model.layers):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    # Save original Q weights to restore between rotations
    orig_q_weights = []
    for layer in model.layers:
        orig_q_weights.append(mx.array(layer.attn.q_proj.weight))

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rotation_stats = []

    for rot_idx in range(n_rotations):
        # Apply rotation (first rotation = identity, rest = random orthogonal)
        if rot_idx == 0:
            # Restore original Q (identity rotation)
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(orig_w)
                mx.eval(layer.attn.q_proj.weight)
        else:
            # Random orthogonal rotation from original
            R = random_orthogonal(model.d_model, rng)
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(R.T) @ orig_w
                mx.eval(layer.attn.q_proj.weight)

        # Etch from this rotation
        rot_loss_sum = 0.0
        for b in range(batches_per_rotation):
            input_ids, targets, mask = generate_batch(
                batch_size, rng, max_depth=max_depth)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            rot_loss_sum += float(loss_val.item())

            for pidx, (layer_idx, pname) in enumerate(plate_paths):
                g = _extract_plate_grad(grads, layer_idx, pname)
                mx.eval(g)
                accumulators[pidx] += np.sign(np.array(g))

            del loss_val, grads, input_ids, targets, mask
            if (b + 1) % 50 == 0:
                mx.clear_cache()

        rotation_stats.append({
            "rotation": rot_idx,
            "mean_loss": rot_loss_sum / batches_per_rotation,
        })
        print(f"    Rotation {rot_idx}/{n_rotations}: "
              f"mean_loss={rot_loss_sum / batches_per_rotation:.4f}",
              flush=True)

    # Restore original Q weights
    for layer, orig_w in zip(model.layers, orig_q_weights):
        layer.attn.q_proj.weight = mx.array(orig_w)
        mx.eval(layer.attn.q_proj.weight)

    # Flip confident positions (accumulated across all rotations)
    total_batches = n_rotations * batches_per_rotation
    total_flipped = 0
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        conf = np.abs(acc) / total_batches
        target_sign = np.sign(acc)
        current = np.sign(np.array(plate.weight)).astype(np.int8)
        should_flip = (
            (conf > confidence) & (target_sign != 0) & (target_sign != current)
        )
        new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
        plate.weight = mx.array(new_signs)
        mx.eval(plate.weight)
        total_flipped += int(should_flip.sum())

    after = holo_plate_fingerprint(model)
    diff = holo_plate_diff(before, after)

    return {
        "n_rotations": n_rotations,
        "total_batches": total_batches,
        "total_flipped": total_flipped,
        "flip_fraction": diff["fraction"],
        "rotation_stats": rotation_stats,
    }


# ── Q-Sensitivity Measurement ────────────────────────────────────

def measure_q_sensitivity(
    model: HoloModel,
    rng: np.random.RandomState,
    n_rotations: int = 16,
    n_eval_batches: int = 20,
    max_depth: int = 4,
) -> dict:
    """Measure how sensitive the model is to Q rotation.

    For each rotation: apply random orthogonal Q rotation → evaluate.
    A well-etched crystal should be robust (low variance across rotations).
    A single-projection etch should be fragile (high variance).

    Returns: dict with per-rotation accuracies, mean, std.
    """
    orig_q_weights = []
    for layer in model.layers:
        orig_q_weights.append(mx.array(layer.attn.q_proj.weight))

    results = []
    for rot_idx in range(n_rotations):
        if rot_idx == 0:
            # Identity (original Q)
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(orig_w)
                mx.eval(layer.attn.q_proj.weight)
        else:
            R = random_orthogonal(model.d_model, rng)
            for layer, orig_w in zip(model.layers, orig_q_weights):
                layer.attn.q_proj.weight = mx.array(R.T) @ orig_w
                mx.eval(layer.attn.q_proj.weight)

        ev = eval_model(model, rng, n_batches=n_eval_batches,
                        max_depth=max_depth)
        results.append(ev["accuracy"])

    # Restore original Q
    for layer, orig_w in zip(model.layers, orig_q_weights):
        layer.attn.q_proj.weight = mx.array(orig_w)
        mx.eval(layer.attn.q_proj.weight)

    return {
        "accuracies": results,
        "mean": float(np.mean(results)),
        "std": float(np.std(results)),
        "min": float(np.min(results)),
        "max": float(np.max(results)),
    }


# ── Main Experiment ───────────────────────────────────────────────

def run_condition(
    name: str,
    n_rotations: int,
    batches_per_rotation: int,
    d_model: int = 96,
    n_layers: int = 3,
    seed: int = 42,
) -> dict:
    """Run one experimental condition."""
    print(f"\n{'='*60}")
    print(f"  Condition: {name}")
    print(f"  n_rotations={n_rotations}, "
          f"batches/rot={batches_per_rotation}, "
          f"total={n_rotations * batches_per_rotation}")
    print(f"{'='*60}")

    rng = np.random.RandomState(seed)
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    params = count_holo_params(model)
    print(f"  Params: {params['plate_positions']} plate, "
          f"{params['continuous']} continuous")

    # ── Phase 1: Etch ──
    t0 = time.time()
    etch_result = etch_with_rotation(
        model, rng,
        n_rotations=n_rotations,
        batches_per_rotation=batches_per_rotation,
        confidence=0.6,
    )
    etch_time = time.time() - t0
    print(f"  Etch: {etch_result['total_flipped']} flipped "
          f"({etch_result['flip_fraction']:.1%}) in {etch_time:.1f}s")

    # ── Phase 2: Freeze plates, train beams ──
    # Reset beam params to fresh init (fair comparison)
    reset_beam_params(model, np.random.RandomState(seed + 1000))

    t0 = time.time()
    gd_losses = train_beams(model, np.random.RandomState(seed + 2000),
                            n_steps=1000, lr=0.003, max_depth=4)
    gd_time = time.time() - t0

    # ── Phase 3: Evaluate ──
    eval_rng = np.random.RandomState(seed + 3000)
    final_eval = eval_model(model, eval_rng, n_batches=50, max_depth=4)
    final_acc = final_eval["accuracy"]
    depth_acc = eval_by_depth(model, np.random.RandomState(seed + 3001),
                              n_samples_per_depth=100, max_depth=4)

    # ── Phase 4: Q-sensitivity test ──
    q_sens = measure_q_sensitivity(
        model, np.random.RandomState(seed + 4000),
        n_rotations=16, n_eval_batches=20)

    print(f"\n  Results:")
    print(f"    Final accuracy: {final_acc:.3f}")
    print(f"    By depth: {depth_acc}")
    print(f"    GD final loss: {gd_losses[-1]:.4f}")
    print(f"    Q-sensitivity: mean={q_sens['mean']:.3f} "
          f"std={q_sens['std']:.3f} "
          f"range=[{q_sens['min']:.3f}, {q_sens['max']:.3f}]")
    print(f"    Times: etch={etch_time:.1f}s, gd={gd_time:.1f}s")

    return {
        "name": name,
        "n_rotations": n_rotations,
        "batches_per_rotation": batches_per_rotation,
        "total_batches": etch_result["total_batches"],
        "flipped": etch_result["total_flipped"],
        "flip_fraction": etch_result["flip_fraction"],
        "gd_final_loss": gd_losses[-1],
        "gd_losses_sampled": [gd_losses[i] for i in
                              range(0, len(gd_losses), max(1, len(gd_losses)//20))],
        "final_accuracy": final_acc,
        "depth_accuracy": depth_acc,
        "q_sensitivity": q_sens,
        "etch_time": etch_time,
        "gd_time": gd_time,
        "rotation_stats": etch_result.get("rotation_stats", []),
    }


def main():
    print("Q-Rotation Etching Experiment")
    print(f"  Model: HoloModel(d=96, layers=3)")
    print(f"  Task: nested combinator reduction, depths 1-4")

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["fixed-budget", "fixed-per-rot"],
                    default="fixed-budget")
    exp_args = ap.parse_args()

    if exp_args.mode == "fixed-per-rot":
        # Follow-up: constant 200 batches per rotation, total scales with n_rot
        PER_ROT = 200
        conditions = [
            ("1-rot×200",    1, PER_ROT),   # 200 total
            ("2-rot×200",    2, PER_ROT),   # 400 total
            ("4-rot×200",    4, PER_ROT),   # 800 total
            ("8-rot×200",    8, PER_ROT),   # 1600 total
        ]
    else:
        # Original: fixed total budget 800, spread across rotations
        TOTAL_BATCHES = 800
        conditions = [
            ("1-rot (baseline)",   1, TOTAL_BATCHES),      # 1×800
            ("2-rot",              2, TOTAL_BATCHES // 2),  # 2×400
            ("4-rot",              4, TOTAL_BATCHES // 4),  # 4×200
            ("8-rot",              8, TOTAL_BATCHES // 8),  # 8×100
        ]

    results = []
    for name, n_rot, bpr in conditions:
        result = run_condition(name, n_rot, bpr, seed=42)
        results.append(result)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Condition':<20s}  {'Acc':>6s}  {'Q-sens σ':>8s}  "
          f"{'Q-sens μ':>8s}  {'Flipped':>8s}  {'GD loss':>8s}")
    print(f"  {'-'*20}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
    for r in results:
        print(f"  {r['name']:<20s}  {r['final_accuracy']:>6.3f}  "
              f"{r['q_sensitivity']['std']:>8.3f}  "
              f"{r['q_sensitivity']['mean']:>8.3f}  "
              f"{r['flipped']:>8d}  "
              f"{r['gd_final_loss']:>8.4f}")

    # Save results
    out_path = Path("results/q-rotation-etch")
    out_path.mkdir(parents=True, exist_ok=True)
    suffix = "fixed-per-rot" if exp_args.mode == "fixed-per-rot" else "fixed-budget"
    out_file = out_path / f"results-{suffix}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_file}")


if __name__ == "__main__":
    main()
