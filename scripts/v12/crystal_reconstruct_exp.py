"""Crystal Reconstruction Experiment — Photogrammetry for Ternary Plates.

Instead of etching plates iteratively (carving one shadow at a time),
MAP the crystal from multiple Q rotations using gradient observations,
then CONSTRUCT the plates from the reconstructed crystal.

Analogy: motion capture.
  - Fiducial dots on actor = combinator token embeddings (known geometry)
  - Cameras at different angles = Q rotations
  - Recording = gradient observations per plate position
  - 3D reconstruction = crystal model from aligned multi-view gradients
  - Plate construction = sign(crystal) at each position

Methods compared:
  A. Single-rotation etch (baseline)
  B. Multi-rotation etch (accumulate signs across rotations)
  C. SVD reconstruction (denoise gradient stack via low-rank approximation)
  D. Magnitude-weighted reconstruction (trust high-confidence observations more)

For each method:
  Construct plates → freeze → reset beams → train GD → measure accuracy

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

from q_rotation_etch_exp import (
    random_orthogonal, apply_q_rotation, reset_beam_params,
    measure_q_sensitivity,
)


# ── Multi-View Gradient Collection ────────────────────────────────

def collect_gradient_views(
    model: HoloModel,
    rng: np.random.RandomState,
    n_rotations: int = 8,
    batches_per_rotation: int = 100,
    batch_size: int = 32,
    max_depth: int = 4,
) -> dict:
    """Collect full gradient matrices from multiple Q rotations.

    For each rotation, accumulate raw gradients (not just signs) for
    each plate. This preserves magnitude information for reconstruction.

    Returns dict with:
      - grad_stacks: list of (n_rotations, out_features, in_features) arrays,
                     one per plate. Each [r, i, j] = mean gradient at plate[i,j]
                     from rotation r.
      - sign_stacks: same but sign(accumulated gradient) per rotation
      - rotation_losses: mean loss per rotation
    """
    plates = _get_plates(model)
    n_plates = len(plates)

    plate_paths = []
    for i, layer in enumerate(model.layers):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    # Allocate storage: per-rotation accumulated gradients
    grad_stacks = []
    sign_accum_stacks = []  # accumulated signs (for etch comparison)
    for _, plate in plates:
        shape = (plate.out_features, plate.in_features)
        grad_stacks.append(np.zeros((n_rotations,) + shape, dtype=np.float64))
        sign_accum_stacks.append(np.zeros((n_rotations,) + shape, dtype=np.float64))

    # Save original Q weights
    orig_q_weights = [mx.array(layer.attn.q_proj.weight) for layer in model.layers]

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rotation_losses = []

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

        rot_loss = 0.0
        for b in range(batches_per_rotation):
            input_ids, targets, mask = generate_batch(
                batch_size, rng, max_depth=max_depth)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            rot_loss += float(loss_val.item())

            for pidx, (layer_idx, pname) in enumerate(plate_paths):
                g = _extract_grad(grads, layer_idx, pname)
                mx.eval(g)
                g_np = np.array(g)
                grad_stacks[pidx][rot_idx] += g_np
                sign_accum_stacks[pidx][rot_idx] += np.sign(g_np)

            del loss_val, grads, input_ids, targets, mask

        # Normalize by batch count
        for pidx in range(n_plates):
            grad_stacks[pidx][rot_idx] /= batches_per_rotation
            sign_accum_stacks[pidx][rot_idx] /= batches_per_rotation

        rotation_losses.append(rot_loss / batches_per_rotation)
        print(f"    View {rot_idx}/{n_rotations}: "
              f"loss={rotation_losses[-1]:.4f}", flush=True)

        mx.clear_cache()

    # Restore Q
    for layer, orig_w in zip(model.layers, orig_q_weights):
        layer.attn.q_proj.weight = mx.array(orig_w)
        mx.eval(layer.attn.q_proj.weight)

    return {
        "grad_stacks": grad_stacks,
        "sign_accum_stacks": sign_accum_stacks,
        "rotation_losses": rotation_losses,
        "n_rotations": n_rotations,
    }


def _extract_grad(grads, layer_idx: int, plate_name: str) -> mx.array:
    layer_grads = grads["layers"][layer_idx]
    parts = plate_name.split(".")
    g = layer_grads
    for part in parts:
        g = g[part]
    return g["weight"]


# ── Plate Construction Methods ────────────────────────────────────

def construct_plates_single_etch(views: dict, rotation_idx: int = 0) -> list[np.ndarray]:
    """Method A: single-rotation etch (baseline).

    Use sign accumulator from one rotation only.
    """
    plates = []
    for sign_stack in views["sign_accum_stacks"]:
        # sign_stack[rot_idx] = mean sign(gradient) from that rotation
        acc = sign_stack[rotation_idx]
        plates.append(np.sign(acc).astype(np.float32))
    return plates


def construct_plates_multi_etch(views: dict, confidence: float = 0.3) -> list[np.ndarray]:
    """Method B: multi-rotation etch (accumulate signs across rotations).

    Sum sign accumulators from all rotations, flip where confident.
    This is the current multi-rotation etching approach.
    """
    plates = []
    for sign_stack in views["sign_accum_stacks"]:
        # Sum across rotations
        acc = sign_stack.sum(axis=0)  # (out, in)
        n_rot = sign_stack.shape[0]
        conf = np.abs(acc) / n_rot
        signs = np.sign(acc)
        # Where not confident, keep as +1 (arbitrary default)
        signs = np.where(conf > confidence, signs, 1.0)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_svd(views: dict, rank: int = 4) -> list[np.ndarray]:
    """Method C: SVD reconstruction (denoise via low-rank).

    Stack gradient matrices from all rotations into a 3D tensor.
    Reshape to (n_rotations, out*in), take SVD, keep top-k components.
    Reconstruct the "consensus gradient" and take its sign.

    The SVD filters noise: only gradient directions that are consistent
    across multiple rotations survive in the top singular vectors.
    This is the photogrammetric reconstruction step.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        n_rot, out_f, in_f = grad_stack.shape
        # Reshape: (n_rotations, out*in) — each rotation is a flattened view
        G = grad_stack.reshape(n_rot, -1)  # (n_rot, out*in)

        # SVD
        U, S, Vt = np.linalg.svd(G, full_matrices=False)

        # Reconstruct using top-k singular vectors
        # The consensus crystal = weighted sum of singular vectors
        # Each singular vector represents one independent "facet" of the crystal
        k = min(rank, len(S))
        G_reconstructed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]

        # Average across rotations to get consensus
        consensus = G_reconstructed.mean(axis=0)  # (out*in,)
        signs = np.sign(consensus).reshape(out_f, in_f)

        # Where consensus is zero (ambiguous), default to +1
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


def construct_plates_magnitude_weighted(views: dict) -> list[np.ndarray]:
    """Method D: magnitude-weighted reconstruction.

    Weight each rotation's gradient by its magnitude. High |grad| at a
    position means that rotation has strong information about that position.
    Low |grad| means that rotation's Q doesn't illuminate that position well.

    This is the "trust confident observations more" principle.
    Equivalent to photogrammetric weighting by ray confidence.
    """
    plates = []
    for grad_stack in views["grad_stacks"]:
        # grad_stack: (n_rot, out, in)
        # Weight = |gradient| at each position
        weights = np.abs(grad_stack)  # (n_rot, out, in)
        # Weighted sum of gradient signs
        weighted_signs = (np.sign(grad_stack) * weights).sum(axis=0)
        total_weight = weights.sum(axis=0) + 1e-10
        consensus = weighted_signs / total_weight  # in [-1, 1]
        signs = np.sign(consensus)
        signs = np.where(signs == 0, 1.0, signs)
        plates.append(signs.astype(np.float32))
    return plates


# ── Plate Installation & Evaluation ──────────────────────────────

def install_plates(model: HoloModel, plate_signs: list[np.ndarray]):
    """Write constructed plate signs into the model."""
    plates = _get_plates(model)
    for (_, plate), signs in zip(plates, plate_signs):
        plate.weight = mx.array(signs)
        mx.eval(plate.weight)


def evaluate_condition(
    name: str,
    model: HoloModel,
    plate_signs: list[np.ndarray],
    seed: int = 42,
) -> dict:
    """Install plates, reset beams, train GD, evaluate."""
    print(f"\n  --- {name} ---")

    # Install constructed plates
    original_fp = holo_plate_fingerprint(model)
    install_plates(model, plate_signs)
    new_fp = holo_plate_fingerprint(model)
    diff = holo_plate_diff(original_fp, new_fp)
    print(f"    Plates changed: {diff['total_flipped']} ({diff['fraction']:.1%})")

    # Reset beam params to fair starting point
    reset_beam_params(model, np.random.RandomState(seed + 1000))

    # Train beams (GD on continuous params, plates frozen)
    t0 = time.time()
    gd_losses = train_beams(model, np.random.RandomState(seed + 2000),
                            n_steps=1000, lr=0.003, max_depth=4)
    gd_time = time.time() - t0

    # Evaluate
    eval_rng = np.random.RandomState(seed + 3000)
    final_eval = eval_model(model, eval_rng, n_batches=50, max_depth=4)
    final_acc = final_eval["accuracy"]
    final_loss = final_eval["loss"]

    # Q-sensitivity
    q_sens = measure_q_sensitivity(
        model, np.random.RandomState(seed + 4000),
        n_rotations=16, n_eval_batches=20)

    print(f"    Acc: {final_acc:.3f}  Loss: {final_loss:.4f}  "
          f"GD-loss: {gd_losses[-1]:.4f}  "
          f"Q-σ: {q_sens['std']:.3f}  ({gd_time:.1f}s)")

    return {
        "name": name,
        "final_accuracy": final_acc,
        "final_loss": final_loss,
        "gd_final_loss": gd_losses[-1],
        "gd_losses_sampled": [gd_losses[i] for i in
                              range(0, len(gd_losses), max(1, len(gd_losses)//10))],
        "q_sensitivity": q_sens,
        "plates_changed": diff["fraction"],
        "gd_time": gd_time,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Crystal Reconstruction Experiment")
    print("  Photogrammetry for ternary plates")
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
    print(f"  Views: {N_ROTATIONS} Q rotations × {BATCHES_PER_ROT} batches")

    # ── Phase 1: Collect multi-view gradient observations ──
    print(f"\n{'='*60}")
    print(f"  Phase 1: Collecting gradient views")
    print(f"{'='*60}")
    t0 = time.time()
    views = collect_gradient_views(
        model, rng,
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
    )
    collect_time = time.time() - t0
    print(f"  Collection time: {collect_time:.1f}s")

    # ── Phase 1.5: Analyze the gradient stack structure ──
    print(f"\n  Gradient stack analysis:")
    for pidx, grad_stack in enumerate(views["grad_stacks"]):
        n_rot, out_f, in_f = grad_stack.shape
        G = grad_stack.reshape(n_rot, -1)
        _, S, _ = np.linalg.svd(G, full_matrices=False)
        # How much variance is captured by top-k components
        var_total = np.sum(S ** 2)
        var_cum = np.cumsum(S ** 2) / (var_total + 1e-10)
        print(f"    Plate {pidx}: shape={out_f}×{in_f}  "
              f"rank-1={var_cum[0]:.1%}  "
              f"rank-2={var_cum[1] if len(var_cum)>1 else 0:.1%}  "
              f"rank-4={var_cum[3] if len(var_cum)>3 else 0:.1%}")

    # ── Phase 2: Construct plates with each method ──
    print(f"\n{'='*60}")
    print(f"  Phase 2: Constructing plates & evaluating")
    print(f"{'='*60}")

    results = []

    # Save initial model state for fair resets
    init_fp = holo_plate_fingerprint(model)

    # Method A: single-rotation etch (baseline — rotation 0 only)
    plates_a = construct_plates_single_etch(views, rotation_idx=0)
    r = evaluate_condition("A: single-rot etch", model, plates_a, seed=SEED)
    results.append(r)

    # Method B: multi-rotation etch (accumulated signs)
    plates_b = construct_plates_multi_etch(views, confidence=0.3)
    r = evaluate_condition("B: multi-rot etch", model, plates_b, seed=SEED)
    results.append(r)

    # Method C: SVD reconstruction (rank 1 — strongest signal only)
    plates_c1 = construct_plates_svd(views, rank=1)
    r = evaluate_condition("C1: SVD rank-1", model, plates_c1, seed=SEED)
    results.append(r)

    # Method C: SVD reconstruction (rank 4)
    plates_c4 = construct_plates_svd(views, rank=4)
    r = evaluate_condition("C4: SVD rank-4", model, plates_c4, seed=SEED)
    results.append(r)

    # Method C: SVD reconstruction (full rank)
    plates_cf = construct_plates_svd(views, rank=N_ROTATIONS)
    r = evaluate_condition(f"Cf: SVD rank-{N_ROTATIONS}", model, plates_cf, seed=SEED)
    results.append(r)

    # Method D: magnitude-weighted
    plates_d = construct_plates_magnitude_weighted(views)
    r = evaluate_condition("D: mag-weighted", model, plates_d, seed=SEED)
    results.append(r)

    # ── Phase 3: Agreement analysis ──
    print(f"\n{'='*60}")
    print(f"  Phase 3: Method agreement")
    print(f"{'='*60}")
    method_names = ["A:single", "B:multi", "C1:svd-1", "C4:svd-4",
                    f"Cf:svd-{N_ROTATIONS}", "D:mag-wt"]
    all_plates = [plates_a, plates_b, plates_c1, plates_c4, plates_cf, plates_d]
    for i in range(len(all_plates)):
        for j in range(i + 1, len(all_plates)):
            agree = sum(
                np.mean(np.sign(p1) == np.sign(p2))
                for p1, p2 in zip(all_plates[i], all_plates[j])
            ) / len(all_plates[i])
            print(f"    {method_names[i]:12s} vs {method_names[j]:12s}: "
                  f"{agree:.1%} agreement")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Method':<20s}  {'Acc':>6s}  {'GD loss':>8s}  "
          f"{'Q-σ':>6s}  {'Q-μ':>6s}")
    print(f"  {'-'*20}  {'-'*6}  {'-'*8}  {'-'*6}  {'-'*6}")
    for r in results:
        print(f"  {r['name']:<20s}  {r['final_accuracy']:>6.3f}  "
              f"{r['gd_final_loss']:>8.4f}  "
              f"{r['q_sensitivity']['std']:>6.3f}  "
              f"{r['q_sensitivity']['mean']:>6.3f}")

    # Save
    out_path = Path("results/crystal-reconstruct")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path / 'results.json'}")


if __name__ == "__main__":
    main()
