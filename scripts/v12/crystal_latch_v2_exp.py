"""Crystal Latching v2 — SVD neighborhood + basin probing.

SVD gets us to the right neighborhood of Q rotations.
Short GD probes find the deepest basin in that neighborhood.

Conditions:
  1. Random Q (baseline, 3 trials)
  2. SVD Q (from v1)
  3. Multi-restart random (8×, pick lowest init loss — from v1)
  4. SVD + perturbation probe (NEW): 8 Q rotations near SVD, 
     50-step GD probe each, pick steepest descent
  5. SVD + perturbation probe (16×): more candidates, same budget
  6. SVD + loss probe: pick lowest loss after 50 steps (not steepest)

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
    VOCAB_SIZE, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint,
    masked_ce_loss, eval_model,
    generate_batch, train_beams,
)

from q_rotation_etch_exp import (
    random_orthogonal, reset_beam_params,
    measure_q_sensitivity, etch_with_rotation,
)

from crystal_reconstruct_exp import collect_gradient_views

from crystal_latch_exp import (
    init_q_random, init_q_svd, init_q_identity,
    eval_with_q_strategy,
)


def perturb_q_near_svd(
    model: HoloModel,
    grad_stacks: list[np.ndarray],
    rng: np.random.RandomState,
    perturbation_scale: float = 0.3,
):
    """Initialize Q near the SVD solution with a random perturbation.

    Q = SVD_Q + scale * random_direction
    Then re-orthogonalize via QR decomposition.
    """
    d = model.d_model

    # First apply SVD init
    init_q_svd(model, grad_stacks)

    # Then perturb each layer's Q
    for layer in model.layers:
        Q_svd = np.array(layer.attn.q_proj.weight)
        # Random perturbation
        noise = rng.randn(d, d).astype(np.float32) * perturbation_scale * (d ** -0.5)
        Q_perturbed = Q_svd + noise
        # Re-orthogonalize via QR to stay on the rotation manifold
        Q_orth, R = np.linalg.qr(Q_perturbed)
        Q_orth = Q_orth * np.sign(np.diag(R))[None, :]  # sign fix
        Q_orth = Q_orth.astype(np.float32) * (d ** -0.5)
        layer.attn.q_proj.weight = mx.array(Q_orth)

    mx.eval(model.parameters())


def probe_basin(
    model: HoloModel,
    rng: np.random.RandomState,
    n_probe_steps: int = 50,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> tuple[list[float], float]:
    """Run a short GD probe and return (losses, steepness).

    Steepness = (loss[0] - loss[-1]) / n_steps — how fast loss drops.
    Higher steepness = deeper basin.
    """
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    losses = []

    for step in range(n_probe_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        losses.append(float(loss_val.item()))

        # Zero plate grads (frozen plates)
        for i, layer in enumerate(model.layers):
            lg = grads["layers"][i]
            for pname in ["k_plate", "v_plate", "o_plate"]:
                if "attn" in lg and pname in lg["attn"]:
                    lg["attn"][pname]["weight"] = mx.zeros_like(
                        lg["attn"][pname]["weight"])
            if "ffn_plate" in lg:
                lg["ffn_plate"]["weight"] = mx.zeros_like(
                    lg["ffn_plate"]["weight"])

        optimizer.update(model, grads)
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask

    steepness = (losses[0] - losses[-1]) / n_probe_steps if losses else 0.0
    return losses, steepness


def svd_neighborhood_probe(
    model: HoloModel,
    grad_stacks: list[np.ndarray],
    plate_fp,
    n_candidates: int = 8,
    n_probe_steps: int = 50,
    perturbation_scale: float = 0.3,
    select_by: str = "steepest",  # "steepest" or "lowest"
    seed: int = 42,
) -> dict:
    """Generate Q candidates near SVD, probe each, select best.

    Returns the seed of the best candidate and probe stats.
    """
    candidates = []

    for c in range(n_candidates):
        c_seed = seed + c * 137
        c_rng = np.random.RandomState(c_seed)

        # Reset beams + set Q near SVD
        reset_beam_params(model, np.random.RandomState(c_seed + 1000))
        if c == 0:
            # First candidate = pure SVD (no perturbation)
            init_q_svd(model, grad_stacks)
        else:
            perturb_q_near_svd(model, grad_stacks, c_rng, perturbation_scale)

        # Save Q state
        q_weights = [mx.array(layer.attn.q_proj.weight)
                     for layer in model.layers]

        # Short GD probe
        probe_losses, steepness = probe_basin(
            model, np.random.RandomState(c_seed + 2000),
            n_probe_steps=n_probe_steps)

        init_loss = probe_losses[0]
        final_loss = probe_losses[-1]

        candidates.append({
            "idx": c,
            "seed": c_seed,
            "init_loss": init_loss,
            "final_loss": final_loss,
            "steepness": steepness,
            "q_weights": q_weights,
        })
        print(f"    Candidate {c}: init={init_loss:.3f} → "
              f"final={final_loss:.3f}  "
              f"steep={steepness:.4f}", flush=True)

    # Select best
    if select_by == "steepest":
        best = max(candidates, key=lambda c: c["steepness"])
    elif select_by == "lowest":
        best = min(candidates, key=lambda c: c["final_loss"])
    else:
        raise ValueError(f"Unknown select_by: {select_by}")

    print(f"    Selected candidate {best['idx']} ({select_by}): "
          f"init={best['init_loss']:.3f} final={best['final_loss']:.3f}")

    return {
        "best_seed": best["seed"],
        "best_idx": best["idx"],
        "best_q_weights": best["q_weights"],
        "candidates": [{k: v for k, v in c.items() if k != "q_weights"}
                       for c in candidates],
    }


def apply_q_weights(model: HoloModel, q_weights: list[mx.array]):
    """Install specific Q weights into the model."""
    for layer, qw in zip(model.layers, q_weights):
        layer.attn.q_proj.weight = mx.array(qw)
    mx.eval(model.parameters())


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("Crystal Latching v2 — SVD neighborhood + basin probing")
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

    # ── Phase 1: Collect gradient views ──
    print(f"\n{'='*60}")
    print(f"  Phase 1: Collecting {N_ROTATIONS} gradient views")
    print(f"{'='*60}")
    views = collect_gradient_views(
        model, np.random.RandomState(SEED + 100),
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
    )

    # ── Phase 2: Etch plates ──
    print(f"\n{'='*60}")
    print(f"  Phase 2: Etching plates (8-rot sign accumulation)")
    print(f"{'='*60}")
    etch_result = etch_with_rotation(
        model, np.random.RandomState(SEED + 200),
        n_rotations=N_ROTATIONS,
        batches_per_rotation=BATCHES_PER_ROT,
        confidence=0.6,
    )
    print(f"  Etched: {etch_result['total_flipped']} flips "
          f"({etch_result['flip_fraction']:.1%})")

    plate_fp = holo_plate_fingerprint(model)

    # ── Phase 3: Q initialization strategies ──
    print(f"\n{'='*60}")
    print(f"  Phase 3: Q strategies (same plates for all)")
    print(f"{'='*60}")

    results = []

    # 1. Random Q (3 trials for variance)
    for trial in range(3):
        ts = SEED + trial * 100
        r = eval_with_q_strategy(
            f"Random Q #{trial}", model,
            lambda s=ts: init_q_random(model, np.random.RandomState(s + 7000)),
            seed=ts)
        results.append(r)

    # 2. SVD Q (from v1)
    r = eval_with_q_strategy(
        "SVD Q", model,
        lambda: init_q_svd(model, views["grad_stacks"]),
        seed=SEED)
    results.append(r)

    # 3. Multi-restart random (8×, pick by init loss)
    print(f"\n  --- Multi-restart random (8×) ---")
    best_init_loss = float("inf")
    best_mr_seed = SEED
    for trial in range(8):
        ts = SEED + 500 + trial * 77
        reset_beam_params(model, np.random.RandomState(ts + 1000))
        init_q_random(model, np.random.RandomState(ts + 7000))
        ev = eval_model(model, np.random.RandomState(ts + 5000),
                        n_batches=5, max_depth=4)
        if ev["loss"] < best_init_loss:
            best_init_loss = ev["loss"]
            best_mr_seed = ts
    r = eval_with_q_strategy(
        "Multi-restart 8×", model,
        lambda: init_q_random(model, np.random.RandomState(best_mr_seed + 7000)),
        seed=best_mr_seed)
    results.append(r)

    # 4. SVD + perturbation probe (8 candidates, select steepest)
    print(f"\n  --- SVD neighborhood probe (8×, steepest) ---")
    probe_result = svd_neighborhood_probe(
        model, views["grad_stacks"], plate_fp,
        n_candidates=8, n_probe_steps=50,
        perturbation_scale=0.3, select_by="steepest", seed=SEED + 600)
    best_q = probe_result["best_q_weights"]
    r = eval_with_q_strategy(
        "SVD+probe steep 8×", model,
        lambda: apply_q_weights(model, best_q),
        seed=SEED + 600 + probe_result["best_seed"])
    r["probe_candidates"] = probe_result["candidates"]
    results.append(r)

    # 5. SVD + perturbation probe (16 candidates, select steepest)
    print(f"\n  --- SVD neighborhood probe (16×, steepest) ---")
    probe_result16 = svd_neighborhood_probe(
        model, views["grad_stacks"], plate_fp,
        n_candidates=16, n_probe_steps=50,
        perturbation_scale=0.3, select_by="steepest", seed=SEED + 700)
    best_q16 = probe_result16["best_q_weights"]
    r = eval_with_q_strategy(
        "SVD+probe steep 16×", model,
        lambda: apply_q_weights(model, best_q16),
        seed=SEED + 700 + probe_result16["best_seed"])
    r["probe_candidates"] = probe_result16["candidates"]
    results.append(r)

    # 6. SVD + perturbation probe (8 candidates, select lowest final loss)
    print(f"\n  --- SVD neighborhood probe (8×, lowest loss) ---")
    probe_result_low = svd_neighborhood_probe(
        model, views["grad_stacks"], plate_fp,
        n_candidates=8, n_probe_steps=50,
        perturbation_scale=0.3, select_by="lowest", seed=SEED + 800)
    best_q_low = probe_result_low["best_q_weights"]
    r = eval_with_q_strategy(
        "SVD+probe low 8×", model,
        lambda: apply_q_weights(model, best_q_low),
        seed=SEED + 800 + probe_result_low["best_seed"])
    r["probe_candidates"] = probe_result_low["candidates"]
    results.append(r)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Method':<25s}  {'Init':>6s}  {'Acc':>6s}  {'GD loss':>8s}  "
          f"{'Q-σ':>6s}")
    print(f"  {'-'*25}  {'-'*6}  {'-'*6}  {'-'*8}  {'-'*6}")
    for r in results:
        print(f"  {r['name']:<25s}  {r['init_loss']:>6.3f}  "
              f"{r['final_accuracy']:>6.3f}  "
              f"{r['gd_final_loss']:>8.4f}  "
              f"{r['q_sensitivity']['std']:>6.3f}")

    # Save
    out_path = Path("results/crystal-latch-v2")
    out_path.mkdir(parents=True, exist_ok=True)
    # Strip mx.array from results before saving
    clean_results = []
    for r in results:
        cr = {k: v for k, v in r.items() if k != "probe_candidates"}
        if "probe_candidates" in r:
            cr["probe_candidates"] = r["probe_candidates"]
        clean_results.append(cr)
    with open(out_path / "results.json", "w") as f:
        json.dump(clean_results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path / 'results.json'}")


if __name__ == "__main__":
    main()
