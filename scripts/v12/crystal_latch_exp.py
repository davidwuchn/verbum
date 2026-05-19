"""Crystal Latching Experiment — SVD-derived Q initialization.

After etching plates via multi-rotation sign accumulation, the gradient
stack from the collection phase contains the crystal's principal axes
(via SVD). Use those axes to initialize Q for GD, "latching" the beams
to the crystal's readable reference frame.

Hypothesis: SVD-derived Q init should beat random Q init because it
starts GD in the reference frame where the crystal structure is most
legible. The plates were etched from multiple rotations — the SVD
extracts the common structure across all of them.

Conditions:
  1. Random Q init (current approach — baseline)
  2. SVD-derived Q init (latch Q to crystal's principal axes)
  3. Best-rotation Q init (use the Q rotation that had lowest etch loss)
  4. Identity Q init (Q = I, no rotation)
  5. Multi-restart: try 8 random Q inits, keep the best

All conditions use the SAME etched plates (from multi-rot etch).
Only the Q initialization differs.

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
    VOCAB_SIZE, PAD_ID, EQ_ID,
    TernaryLinear, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model,
    generate_batch, _zero_plate_grads, train_beams,
)

from q_rotation_etch_exp import (
    random_orthogonal, reset_beam_params,
    measure_q_sensitivity, etch_with_rotation,
)

from crystal_reconstruct_exp import (
    collect_gradient_views,
)


# ── Q Initialization Strategies ───────────────────────────────────

def init_q_random(model: HoloModel, rng: np.random.RandomState):
    """Strategy 1: Random Q init (baseline)."""
    d = model.d_model
    for layer in model.layers:
        w = rng.randn(d, d).astype(np.float32) * (d ** -0.5)
        layer.attn.q_proj.weight = mx.array(w)
    mx.eval(model.parameters())


def init_q_svd(model: HoloModel, grad_stacks: list[np.ndarray]):
    """Strategy 2: SVD-derived Q init — latch to crystal axes.

    For each layer's K-plate gradient stack, compute SVD.
    The right singular vectors (V) define the input directions
    where the plate has the most gradient structure across rotations.
    Set Q = V^T so queries project into the plate's principal axes.

    This is "reading the key from the lock" — the plate structure
    tells us which Q rotation makes it most legible.
    """
    d = model.d_model
    # Plates are ordered: layer0.k, layer0.v, layer0.o, layer0.ffn, layer1.k, ...
    # We use K-plate gradients to derive Q init (K is what Q reads)
    for layer_idx, layer in enumerate(model.layers):
        # K-plate gradient stack for this layer
        k_plate_idx = layer_idx * 4  # k, v, o, ffn per layer
        if k_plate_idx >= len(grad_stacks):
            # Fallback to random
            w = np.random.randn(d, d).astype(np.float32) * (d ** -0.5)
            layer.attn.q_proj.weight = mx.array(w)
            continue

        grad_stack = grad_stacks[k_plate_idx]  # (n_rot, out, in)
        n_rot, out_f, in_f = grad_stack.shape

        # Reshape to (n_rot, out*in) and SVD
        G = grad_stack.reshape(n_rot, -1)
        U, S, Vt = np.linalg.svd(G, full_matrices=False)

        # V^T rows are the principal directions in plate space
        # We want Q to project into these directions
        # Q weight is (d_model, d_model) — output = x @ W^T
        # To project into Vt's principal directions, set W = Vt[:d, :]
        # But Vt is (min(n_rot, out*in), out*in) — much larger than d×d
        # We need to extract a d×d rotation from the principal structure

        # Strategy: take the top-d right singular vectors of the
        # per-input-dimension gradient. Reshape gradient stack to
        # privilege the input dimension structure.

        # Alternative: compute SVD of the (n_rot × in_f) matrix formed by
        # averaging gradient across output dimension — this gives us the
        # principal INPUT directions.
        G_input = grad_stack.mean(axis=1)  # (n_rot, in_f) — avg over outputs
        _, _, Vt_input = np.linalg.svd(G_input, full_matrices=True)
        # Vt_input is (in_f, in_f) — full rotation matrix for input space

        # Use this as Q init — it projects queries into the directions
        # where the K-plate has the most structure
        Q_init = Vt_input[:d, :d].astype(np.float32)
        # Scale to match typical Q projection magnitude
        Q_init *= (d ** -0.5)

        layer.attn.q_proj.weight = mx.array(Q_init)

    mx.eval(model.parameters())


def init_q_best_rotation(
    model: HoloModel,
    orig_q_weights: list[mx.array],
    rotation_losses: list[float],
    rotations_used: list[np.ndarray | None],
):
    """Strategy 3: Use the Q rotation that had lowest loss during collection."""
    best_idx = int(np.argmin(rotation_losses))
    for layer, orig_w in zip(model.layers, orig_q_weights):
        if best_idx == 0 or rotations_used[best_idx] is None:
            layer.attn.q_proj.weight = mx.array(orig_w)
        else:
            R = rotations_used[best_idx]
            layer.attn.q_proj.weight = mx.array(R.T) @ orig_w
    mx.eval(model.parameters())


def init_q_identity(model: HoloModel):
    """Strategy 4: Q = scaled identity (no rotation)."""
    d = model.d_model
    scale = d ** -0.5
    for layer in model.layers:
        layer.attn.q_proj.weight = mx.array(
            np.eye(d, dtype=np.float32) * scale)
    mx.eval(model.parameters())


# ── Evaluation Helper ─────────────────────────────────────────────

def eval_with_q_strategy(
    name: str,
    model: HoloModel,
    q_init_fn,
    seed: int = 42,
    n_gd_steps: int = 1000,
) -> dict:
    """Reset beams (except Q), apply Q strategy, train, evaluate."""
    print(f"\n  --- {name} ---")

    # Reset all beam params to deterministic starting point
    reset_beam_params(model, np.random.RandomState(seed + 1000))

    # Apply Q initialization strategy (overrides the random Q from reset)
    q_init_fn()

    # Measure initial loss (before any GD)
    init_rng = np.random.RandomState(seed + 5000)
    init_eval = eval_model(model, init_rng, n_batches=10, max_depth=4)
    init_loss = init_eval["loss"]
    init_acc = init_eval["accuracy"]
    print(f"    Init: loss={init_loss:.4f} acc={init_acc:.3f}")

    # Train beams
    t0 = time.time()
    gd_losses = train_beams(model, np.random.RandomState(seed + 2000),
                            n_steps=n_gd_steps, lr=0.003, max_depth=4)
    gd_time = time.time() - t0

    # Final eval
    eval_rng = np.random.RandomState(seed + 3000)
    final_eval = eval_model(model, eval_rng, n_batches=50, max_depth=4)
    final_acc = final_eval["accuracy"]
    final_loss = final_eval["loss"]

    # Q sensitivity
    q_sens = measure_q_sensitivity(
        model, np.random.RandomState(seed + 4000),
        n_rotations=16, n_eval_batches=20)

    # Early GD trajectory (first 100 steps)
    early_losses = gd_losses[:100:10] if len(gd_losses) >= 100 else gd_losses[:10]

    print(f"    Final: acc={final_acc:.3f} loss={final_loss:.4f} "
          f"GD={gd_losses[-1]:.4f} Q-σ={q_sens['std']:.3f} ({gd_time:.1f}s)")
    print(f"    GD trajectory (first 100): {[f'{l:.3f}' for l in early_losses]}")

    return {
        "name": name,
        "init_loss": init_loss,
        "init_accuracy": init_acc,
        "final_accuracy": final_acc,
        "final_loss": final_loss,
        "gd_final_loss": gd_losses[-1],
        "gd_losses_sampled": [gd_losses[i] for i in
                              range(0, len(gd_losses), max(1, len(gd_losses)//20))],
        "early_gd": early_losses,
        "q_sensitivity": q_sens,
        "gd_time": gd_time,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Crystal Latching Experiment")
    print("  SVD-derived Q initialization vs random")
    print()

    D_MODEL = 96
    N_LAYERS = 3
    N_ROTATIONS = 8
    BATCHES_PER_ROT = 100
    SEED = 42

    rng = np.random.RandomState(SEED)
    model = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(model.parameters())

    params = count_holo_params(model)
    print(f"  Model: d={D_MODEL}, layers={N_LAYERS}")
    print(f"  Params: {params['plate_positions']} plate, "
          f"{params['continuous']} continuous")

    # Save original Q weights (pre-etch)
    orig_q_weights = [mx.array(layer.attn.q_proj.weight)
                      for layer in model.layers]

    # ── Phase 1: Collect gradient views ──
    print(f"\n{'='*60}")
    print(f"  Phase 1: Collecting {N_ROTATIONS} gradient views")
    print(f"{'='*60}")

    # Track which rotations we use
    rotation_matrices = [None]  # rotation 0 = identity
    collection_rng = np.random.RandomState(SEED + 100)

    views = collect_gradient_views(
        model, collection_rng,
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
    )

    # ── Phase 2: Etch plates (multi-rot sign accumulation) ──
    print(f"\n{'='*60}")
    print(f"  Phase 2: Etching plates (multi-rot sign accumulation)")
    print(f"{'='*60}")

    etch_result = etch_with_rotation(
        model, np.random.RandomState(SEED + 200),
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
        confidence=0.6,
    )
    print(f"  Etched: {etch_result['total_flipped']} flips "
          f"({etch_result['flip_fraction']:.1%})")

    # Freeze plates — all conditions use these same plates
    plate_fp = holo_plate_fingerprint(model)

    # ── Phase 3: Test Q initialization strategies ──
    print(f"\n{'='*60}")
    print(f"  Phase 3: Q initialization strategies (same plates)")
    print(f"{'='*60}")

    results = []

    # Strategy 1: Random Q (baseline) — run 3 seeds for variance
    for trial in range(3):
        trial_seed = SEED + trial * 100
        r = eval_with_q_strategy(
            f"Random Q (trial {trial})", model,
            lambda s=trial_seed: init_q_random(model, np.random.RandomState(s + 7000)),
            seed=trial_seed)
        results.append(r)

    # Plates are reinstalled by each eval_with_q_strategy via reset_beam_params

    # Strategy 2: SVD-derived Q
    r = eval_with_q_strategy(
        "SVD Q (crystal latch)", model,
        lambda: init_q_svd(model, views["grad_stacks"]),
        seed=SEED)
    results.append(r)

    # Strategy 3: Identity Q
    r = eval_with_q_strategy(
        "Identity Q", model,
        lambda: init_q_identity(model),
        seed=SEED)
    results.append(r)

    # Strategy 4: Multi-restart (8 random, keep best)
    print(f"\n  --- Multi-restart (8 random Q, keep best) ---")
    best_restart_acc = -1
    best_restart_result = None
    for trial in range(8):
        trial_seed = SEED + 500 + trial * 77
        # Quick eval: just check init loss (no GD) to pick best start
        reset_beam_params(model, np.random.RandomState(trial_seed + 1000))
        init_q_random(model, np.random.RandomState(trial_seed + 7000))
        quick_eval = eval_model(model, np.random.RandomState(trial_seed + 5000),
                                n_batches=5, max_depth=4)
        print(f"    Restart {trial}: init_loss={quick_eval['loss']:.4f}", flush=True)
        if best_restart_result is None or quick_eval["loss"] < best_restart_result:
            best_restart_result = quick_eval["loss"]
            best_restart_seed = trial_seed

    # Now fully train the best restart
    r = eval_with_q_strategy(
        f"Multi-restart best", model,
        lambda: init_q_random(model, np.random.RandomState(best_restart_seed + 7000)),
        seed=best_restart_seed)
    results.append(r)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Method':<25s}  {'Init':>6s}  {'Acc':>6s}  {'GD loss':>8s}  "
          f"{'Q-σ':>6s}  {'Q-μ':>6s}")
    print(f"  {'-'*25}  {'-'*6}  {'-'*6}  {'-'*8}  {'-'*6}  {'-'*6}")
    for r in results:
        print(f"  {r['name']:<25s}  {r['init_loss']:>6.3f}  "
              f"{r['final_accuracy']:>6.3f}  "
              f"{r['gd_final_loss']:>8.4f}  "
              f"{r['q_sensitivity']['std']:>6.3f}  "
              f"{r['q_sensitivity']['mean']:>6.3f}")

    # Save
    out_path = Path("results/crystal-latch")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path / 'results.json'}")


if __name__ == "__main__":
    main()
