"""Mini Holographic Microscope — Freeze + GD Recovery.

Tests the seed crystal Stage 6 hypothesis: after etching plates to
convergence, freeze them permanently and train only continuous params
(Q projections, beam scales, embeddings). Does beam-only GD recover
to or exceed the alternating protocol?

Conditions:
  1. Etch-first for 15 rounds (full alternating baseline)
  2. Etch-first for N rounds → freeze → beam GD for remaining budget
     N ∈ {1, 3, 5, 8, 12}
  3. Beam-only from scratch (frozen random plates, beam GD only)
  4. GD baseline (no ternary constraint)

The key question: after plates are etched, is extended beam-only GD
better than continuing to alternate etch+beam?

Uses v2 architecture: causal attention with ternary K/V/O plates.
Task: nested KIBC composition chains.

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

# Reuse components from d-sweep v2
from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID, ID2TOK,
    TernaryLinear,
    GDModel, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model, eval_by_depth,
    generate_batch, generate_example,
    etch_plates, train_beams, _zero_plate_grads,
    _extract_plate_grad,
)


# ══════════════════════════════════════════════════════════════════════
# Freeze experiment
# ══════════════════════════════════════════════════════════════════════

def run_etch_then_freeze(
    d_model: int = 48,
    n_layers: int = 3,
    n_etch_rounds: int = 5,
    etch_batches: int = 200,
    beam_steps_per_round: int = 500,
    post_freeze_steps: int = 3000,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Etch-first for N rounds, then freeze plates and do beam-only GD.

    Returns full training trajectory so we can see:
    - Accuracy at freeze point
    - Recovery curve after freeze
    - Final accuracy after extended beam-only GD
    """
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)

    rng = np.random.RandomState(42)

    # Phase 1: Etch-first alternating
    etch_log = []
    for r in range(n_etch_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        losses = train_beams(model, rng, n_steps=beam_steps_per_round,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        etch_log.append({
            "round": r + 1, "phase": "etch",
            "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    # Record accuracy at freeze point
    freeze_eval = eval_model(model, np.random.RandomState(999),
                             max_depth=max_depth)
    freeze_depth = eval_by_depth(model, np.random.RandomState(999),
                                 max_depth=max_depth)

    # Phase 2: Freeze all plates, train beams only
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)

    gd_log = []
    for step in range(post_freeze_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()

        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            gd_log.append({"step": step + 1, "phase": "frozen_gd", **ev})

    # Final eval with depth breakdown
    final_eval = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
    final_depth = eval_by_depth(model, np.random.RandomState(999),
                                max_depth=max_depth)

    return {
        "n_etch_rounds": n_etch_rounds,
        "post_freeze_steps": post_freeze_steps,
        "params": params,
        "freeze_eval": freeze_eval,
        "freeze_depth": freeze_depth,
        "final_eval": final_eval,
        "final_depth": final_depth,
        "etch_log": etch_log,
        "gd_log": gd_log,
        "best_acc": max(
            max((e["accuracy"] for e in etch_log), default=0),
            max((e["accuracy"] for e in gd_log), default=0),
        ),
    }


def run_full_alternating(
    d_model: int = 48,
    n_layers: int = 3,
    n_rounds: int = 15,
    etch_batches: int = 200,
    beam_steps: int = 500,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Full alternating baseline — never freeze."""
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        losses = train_beams(model, rng, n_steps=beam_steps,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        log.append({
            "round": r + 1,
            "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    final_depth = eval_by_depth(model, np.random.RandomState(999),
                                max_depth=max_depth)

    return {
        "n_rounds": n_rounds,
        "params": params,
        "log": log,
        "final_depth": final_depth,
        "best_acc": max(e["accuracy"] for e in log),
    }


def run_beam_only_from_scratch(
    d_model: int = 48,
    n_layers: int = 3,
    n_steps: int = 10000,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Frozen random plates, beam-only GD from scratch."""
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)

    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final_depth = eval_by_depth(model, np.random.RandomState(999),
                                max_depth=max_depth)

    return {
        "n_steps": n_steps,
        "params": params,
        "log": log,
        "final_depth": final_depth,
        "best_acc": max(e["accuracy"] for e in log),
    }


def run_gd_baseline(
    d_model: int = 48,
    n_layers: int = 3,
    n_steps: int = 10000,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Full GD baseline (no ternary)."""
    model = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    from mlx.utils import tree_flatten
    n_params = sum(p.size for _, p in tree_flatten(model.parameters()))

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final_depth = eval_by_depth(model, np.random.RandomState(999),
                                max_depth=max_depth)

    return {
        "n_steps": n_steps,
        "n_params": n_params,
        "log": log,
        "final_depth": final_depth,
        "best_acc": max(e["accuracy"] for e in log),
    }


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-freeze")
    output_dir.mkdir(parents=True, exist_ok=True)

    d_model = 48
    n_layers = 3
    max_depth = 4
    etch_batches = 200
    beam_steps = 500
    batch_size = 32
    lr = 0.003

    # Total compute budget per condition:
    # 15 rounds × (200 etch + 500 beam) = 10,500 batch steps
    # Post-freeze GD gets the "remaining" budget after N etch rounds
    # So: freeze at round 5 → 5 rounds etch (3500 steps) + 7000 GD steps
    # This keeps total compute roughly equal across conditions.

    total_etch_beam_steps = 15 * (etch_batches + beam_steps)  # 10,500

    freeze_points = [1, 3, 5, 8, 12]

    print("=" * 70)
    print("  FREEZE + GD RECOVERY EXPERIMENT")
    print(f"  d={d_model}, layers={n_layers}, max_depth={max_depth}")
    print(f"  Total compute budget: ~{total_etch_beam_steps} batch steps")
    print(f"  Freeze points: {freeze_points}")
    print("=" * 70)

    results = {}

    # 1. GD baseline
    print(f"\n  [1/{4+len(freeze_points)}] GD baseline "
          f"({total_etch_beam_steps} steps)...", end="", flush=True)
    t0 = time.time()
    gd = run_gd_baseline(d_model, n_layers, n_steps=total_etch_beam_steps,
                         batch_size=batch_size, lr=lr, max_depth=max_depth)
    print(f" best={gd['best_acc']:.1%} ({time.time()-t0:.1f}s)")
    results["gd_baseline"] = gd

    # 2. Beam-only from scratch (frozen random plates)
    print(f"  [2/{4+len(freeze_points)}] Beam-only from scratch "
          f"({total_etch_beam_steps} steps)...", end="", flush=True)
    t0 = time.time()
    beam = run_beam_only_from_scratch(d_model, n_layers,
                                      n_steps=total_etch_beam_steps,
                                      batch_size=batch_size, lr=lr,
                                      max_depth=max_depth)
    print(f" best={beam['best_acc']:.1%} ({time.time()-t0:.1f}s)")
    results["beam_only"] = beam

    # 3. Full alternating (15 rounds, never freeze)
    print(f"  [3/{4+len(freeze_points)}] Full alternating "
          f"(15 rounds)...", end="", flush=True)
    t0 = time.time()
    alt = run_full_alternating(d_model, n_layers, n_rounds=15,
                               etch_batches=etch_batches,
                               beam_steps=beam_steps,
                               batch_size=batch_size, lr=lr,
                               max_depth=max_depth)
    print(f" best={alt['best_acc']:.1%} ({time.time()-t0:.1f}s)")
    results["full_alternating"] = alt

    # 4. Freeze at various points
    for i, fp in enumerate(freeze_points):
        etch_steps = fp * (etch_batches + beam_steps)
        remaining = total_etch_beam_steps - etch_steps
        post_freeze = max(remaining, 1000)  # at least 1000 steps

        print(f"  [{4+i}/{4+len(freeze_points)}] Freeze at round {fp} "
              f"(→ {post_freeze} GD steps)...", end="", flush=True)
        t0 = time.time()
        fr = run_etch_then_freeze(
            d_model, n_layers,
            n_etch_rounds=fp,
            etch_batches=etch_batches,
            beam_steps_per_round=beam_steps,
            post_freeze_steps=post_freeze,
            batch_size=batch_size, lr=lr,
            max_depth=max_depth,
        )
        dt = time.time() - t0
        print(f" freeze={fr['freeze_eval']['accuracy']:.1%} "
              f"→ final={fr['final_eval']['accuracy']:.1%} "
              f"(best={fr['best_acc']:.1%}) ({dt:.1f}s)")
        results[f"freeze_r{fp}"] = fr

    # 5. Extended freeze — what if we etch fully THEN give tons of GD?
    print(f"  [{4+len(freeze_points)}/{4+len(freeze_points)}] "
          f"Full etch (15r) + extended GD ({total_etch_beam_steps} steps)...",
          end="", flush=True)
    t0 = time.time()
    ext = run_etch_then_freeze(
        d_model, n_layers,
        n_etch_rounds=15,
        etch_batches=etch_batches,
        beam_steps_per_round=beam_steps,
        post_freeze_steps=total_etch_beam_steps,
        batch_size=batch_size, lr=lr,
        max_depth=max_depth,
    )
    dt = time.time() - t0
    print(f" freeze={ext['freeze_eval']['accuracy']:.1%} "
          f"→ final={ext['final_eval']['accuracy']:.1%} "
          f"(best={ext['best_acc']:.1%}) ({dt:.1f}s)")
    results["full_etch_extended_gd"] = ext

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  SUMMARY — Freeze + GD Recovery")
    print(f"{'═' * 70}")

    print(f"\n  Baselines:")
    print(f"    GD (no ternary):        best={gd['best_acc']:.1%}")
    print(f"    Beam-only (random):     best={beam['best_acc']:.1%}")
    print(f"    Full alternating (15r): best={alt['best_acc']:.1%}")

    print(f"\n  Freeze experiments:")
    print(f"  {'Freeze':>10}  {'At freeze':>10}  {'After GD':>10}  "
          f"{'Recovery':>10}  {'vs Alt':>10}")
    print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}")

    for fp in freeze_points:
        key = f"freeze_r{fp}"
        fr = results[key]
        freeze_acc = fr["freeze_eval"]["accuracy"]
        final_acc = fr["final_eval"]["accuracy"]
        recovery = final_acc - freeze_acc
        vs_alt = final_acc - alt["best_acc"]
        print(f"  {'round '+str(fp):>10}  {freeze_acc:>9.1%}  "
              f"{final_acc:>9.1%}  {recovery:>+9.1%}  {vs_alt:>+9.1%}")

    # Extended
    ext_freeze = ext["freeze_eval"]["accuracy"]
    ext_final = ext["final_eval"]["accuracy"]
    ext_recovery = ext_final - ext_freeze
    ext_vs_alt = ext_final - alt["best_acc"]
    print(f"  {'15r+extGD':>10}  {ext_freeze:>9.1%}  "
          f"{ext_final:>9.1%}  {ext_recovery:>+9.1%}  {ext_vs_alt:>+9.1%}")

    # Depth breakdown for key conditions
    print(f"\n  Depth breakdown (exact sequence match):")
    print(f"  {'Condition':>20}  {'d1':>6}  {'d2':>6}  {'d3':>6}  {'d4':>6}")
    print(f"  {'─'*20}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}")

    for label, data in [
        ("GD baseline", gd),
        ("Beam-only", beam),
        ("Full alt (15r)", alt),
        ("Freeze r5 + GD", results["freeze_r5"]),
        ("Freeze r12 + GD", results["freeze_r12"]),
        ("15r + ext GD", ext),
    ]:
        fd = data.get("final_depth", {})
        vals = []
        for d in range(1, max_depth + 1):
            acc = fd.get(d, fd.get(str(d), {}))
            if isinstance(acc, dict):
                acc = acc.get("accuracy", 0)
            vals.append(acc)
        print(f"  {label:>20}  " + "  ".join(f"{v:>5.1%}" for v in vals))

    # GD recovery curve for the best freeze point
    best_freeze = max(freeze_points,
                      key=lambda fp: results[f"freeze_r{fp}"]["final_eval"]["accuracy"])
    best_fr = results[f"freeze_r{best_freeze}"]
    if best_fr["gd_log"]:
        print(f"\n  Best freeze point: round {best_freeze}")
        print(f"  GD recovery curve:")
        for entry in best_fr["gd_log"]:
            print(f"    step {entry['step']:5d}: "
                  f"acc={entry['accuracy']:.1%} loss={entry['loss']:.4f}")

    # Save
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
