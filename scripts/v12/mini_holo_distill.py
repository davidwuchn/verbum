"""Mini Holographic Microscope — Holographic Distillation.

Instead of copying sign(W) from the teacher (which fails because signs
are coupled to magnitudes), we RECORD the teacher's layer-wise function
into ternary plates using multiple "beam angles" (diverse probes).

For each probe (beam angle), we capture the teacher's (input → output)
at each layer. Then we etch the student's ternary plates to reproduce
those mappings. The more beam angles, the more of the teacher's
computation is captured in the interference pattern.

The etch accumulator works naturally here: compute the gradient of
the distillation loss (teacher_output - student_output)² w.r.t.
ternary weights, accumulate sign(gradient) across many probes,
flip where confident.

Conditions:
  1. GD baseline (oracle ceiling)
  2. Holographic distillation + freeze + GD (50/200/800 beam angles)
  3. Oracle crystal (sign copy) + freeze + GD (from mini_holo_crystal)
  4. Random plates + freeze + GD
  5. Iterative CE etch (round 5) + freeze + GD

License: MIT
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID, ID2TOK,
    TernaryLinear,
    CausalSelfAttention, GDLayer, GDModel,
    TernaryCausalAttention, HoloBeamLayer, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model, eval_by_depth,
    generate_batch, generate_example,
    etch_plates, train_beams, _zero_plate_grads,
)

from mini_holo_crystal import (
    extract_crystal, write_crystal_to_model, crystal_similarity,
)


# ══════════════════════════════════════════════════════════════════════
# Teacher feature extraction — capture layer-wise (input, output)
# ══════════════════════════════════════════════════════════════════════

def extract_teacher_features(
    teacher: GDModel,
    n_probes: int = 200,
    batch_size: int = 32,
    max_depth: int = 4,
    rng: np.random.RandomState = None,
) -> list[list[tuple[mx.array, mx.array]]]:
    """Extract (input, output) pairs at each layer for many probes.

    Returns: list of layers, each containing list of (input, output) pairs.
      features[layer_idx] = [(input_batch, output_batch), ...]

    The teacher's layer computation:
      attn_out = attn(norm(x))
      x = x + attn_out           ← attention residual
      ffn_out = ffn(norm(x))
      x = x + ffn_out            ← FFN residual

    We capture the full layer: input x → output (x + attn + ffn).
    """
    if rng is None:
        rng = np.random.RandomState(777)

    n_layers = len(teacher.layers)
    features = [[] for _ in range(n_layers)]

    n_batches = (n_probes + batch_size - 1) // batch_size

    for _ in range(n_batches):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)

        # Forward through embedding
        x = teacher.embed(input_ids)
        mx.eval(x)

        # Forward through each layer, capturing input and output
        for i, layer in enumerate(teacher.layers):
            layer_input = x
            x = layer(x)
            mx.eval(x)
            features[i].append((layer_input, x))
            # Detach for next layer
            layer_input = x

    return features


# ══════════════════════════════════════════════════════════════════════
# Holographic distillation — etch plates to match teacher behavior
# ══════════════════════════════════════════════════════════════════════

def distill_loss_single_layer(
    student_layer: HoloBeamLayer,
    teacher_input: mx.array,
    teacher_output: mx.array,
) -> mx.array:
    """Distillation loss for a single layer.

    Compute student's output for the same input, compare to teacher's output.
    Loss = MSE(student_output, teacher_output)
    """
    student_output = student_layer(teacher_input)
    diff = student_output - teacher_output
    return (diff * diff).mean()


def holographic_etch(
    student: HoloModel,
    teacher_features: list[list[tuple[mx.array, mx.array]]],
    n_rounds: int = 5,
    confidence_threshold: float = 0.6,
) -> list[dict]:
    """Etch student plates to reproduce teacher layer behavior.

    For each layer independently:
      1. Accumulate gradient of distillation loss w.r.t. plates
      2. Flip where confident majority agrees on direction

    Also trains beam params (scales, bias) alongside etch for better
    signal — the continuous params help the plates find the right topology.
    """
    n_layers = len(student.layers)
    log = []

    for round_idx in range(n_rounds):
        round_total_flips = 0

        for layer_idx in range(n_layers):
            layer = student.layers[layer_idx]
            batches = teacher_features[layer_idx]
            n_batches = len(batches)

            # Accumulators for all 4 plates in this layer
            plate_names = ["attn.k_plate", "attn.v_plate",
                           "attn.o_plate", "ffn_plate"]
            accumulators = {}
            for pname in plate_names:
                parts = pname.split(".")
                plate = layer
                for p in parts:
                    plate = getattr(plate, p)
                shape = (plate.out_features, plate.in_features)
                accumulators[pname] = np.zeros(shape, dtype=np.float64)

            # Accumulate gradient signs
            for teacher_input, teacher_output in batches:
                loss_fn = lambda layer: distill_loss_single_layer(
                    layer, teacher_input, teacher_output)
                loss_val, grads = nn.value_and_grad(
                    student.layers[layer_idx], loss_fn)(
                    student.layers[layer_idx])
                mx.eval(loss_val, grads)

                # Extract plate gradients
                for pname in plate_names:
                    parts = pname.split(".")
                    g = grads
                    for p in parts:
                        g = g[p]
                    g = g["weight"]
                    mx.eval(g)
                    accumulators[pname] += np.sign(np.array(g))

                del loss_val, grads

            # Flip confident positions
            layer_flips = 0
            for pname in plate_names:
                parts = pname.split(".")
                plate = layer
                for p in parts:
                    plate = getattr(plate, p)

                acc = accumulators[pname]
                confidence = np.abs(acc) / n_batches
                target_sign = np.sign(acc)
                current = np.sign(np.array(plate.weight)).astype(np.int8)
                should_flip = (
                    (confidence > confidence_threshold)
                    & (target_sign != 0)
                    & (target_sign != current)
                )
                new_signs = np.where(
                    should_flip, target_sign, current
                ).astype(np.float32)
                plate.weight = mx.array(new_signs)
                mx.eval(plate.weight)
                layer_flips += int(should_flip.sum())

            round_total_flips += layer_flips

        # Also train beam params with distillation loss
        beam_optimizer = optim.Adam(learning_rate=0.003)
        for beam_step in range(100):
            total_loss = mx.array(0.0)
            for layer_idx in range(n_layers):
                # Use first batch for beam training
                if teacher_features[layer_idx]:
                    t_in, t_out = teacher_features[layer_idx][
                        beam_step % len(teacher_features[layer_idx])]

                    def full_distill_loss(model):
                        loss = mx.array(0.0)
                        x = t_in
                        for li in range(n_layers):
                            t_i, t_o = teacher_features[li][
                                beam_step % len(teacher_features[li])]
                            s_o = model.layers[li](t_i)
                            diff = s_o - t_o
                            loss = loss + (diff * diff).mean()
                        return loss

            loss_fn = lambda m: full_distill_loss(m)
            loss_val, grads = nn.value_and_grad(student, loss_fn)(student)
            mx.eval(loss_val, grads)

            # Zero plate grads, keep beam grads
            _zero_plate_grads(grads, n_layers)
            student.update(beam_optimizer.apply_gradients(grads, student))
            mx.eval(student.parameters())
            del loss_val, grads

            if (beam_step + 1) % 25 == 0:
                mx.clear_cache()

        # Eval
        ev = eval_model(student, np.random.RandomState(999), max_depth=4)
        log.append({
            "round": round_idx + 1,
            "flips": round_total_flips,
            **ev,
        })
        print(f"      Round {round_idx+1}: flips={round_total_flips:5d} "
              f"acc={ev['accuracy']:.1%} loss={ev['loss']:.4f}")
        mx.clear_cache()

    return log


# ══════════════════════════════════════════════════════════════════════
# Experiment runners
# ══════════════════════════════════════════════════════════════════════

def run_holographic_distill(
    teacher: GDModel,
    n_probes: int = 200,
    n_etch_rounds: int = 5,
    post_freeze_steps: int = 10500,
    d_model: int = 48,
    n_layers: int = 3,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Full holographic distillation pipeline."""

    # Extract teacher features
    features = extract_teacher_features(
        teacher, n_probes=n_probes, batch_size=batch_size,
        max_depth=max_depth,
        rng=np.random.RandomState(777),
    )
    n_feature_batches = len(features[0])

    # Create student
    student = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(student.parameters())

    # Holographic etch
    etch_log = holographic_etch(
        student, features,
        n_rounds=n_etch_rounds,
    )

    # Capture etched crystal
    etched_crystal = holo_plate_fingerprint(student)

    # Freeze plates
    for layer in student.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    # Extended GD on task
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)
    rng = np.random.RandomState(42)

    gd_log = []
    for step in range(post_freeze_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        student.update(optimizer.apply_gradients(grads, student))
        mx.eval(student.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(student, np.random.RandomState(999),
                            max_depth=max_depth)
            gd_log.append({"step": step + 1, **ev})

    final = eval_model(student, np.random.RandomState(999),
                       max_depth=max_depth)
    depth = eval_by_depth(student, np.random.RandomState(999),
                          max_depth=max_depth)

    all_accs = (
        [e["accuracy"] for e in etch_log]
        + [e["accuracy"] for e in gd_log]
        + [final["accuracy"]]
    )

    return {
        "n_probes": n_probes,
        "n_feature_batches": n_feature_batches,
        "n_etch_rounds": n_etch_rounds,
        "best_acc": max(all_accs),
        "final_acc": final["accuracy"],
        "final_depth": depth,
        "etch_log": etch_log,
        "gd_log": gd_log,
    }


def run_crystal_write_gd(
    crystal, label, d_model=48, n_layers=3,
    n_steps=10500, batch_size=32, lr=0.003, max_depth=4,
):
    """Write crystal, freeze, GD — reused from crystal experiment."""
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    write_crystal_to_model(model, crystal)

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
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    depth = eval_by_depth(model, np.random.RandomState(999),
                          max_depth=max_depth)
    return {
        "label": label,
        "best_acc": max(e["accuracy"] for e in log) if log else final["accuracy"],
        "final_acc": final["accuracy"],
        "final_depth": depth,
        "log": log,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-distill")
    output_dir.mkdir(parents=True, exist_ok=True)

    d_model = 48
    n_layers = 3
    max_depth = 4
    gd_steps = 10500
    batch_size = 32
    lr = 0.003

    probe_counts = [50, 200, 800]

    print("=" * 70)
    print("  HOLOGRAPHIC DISTILLATION EXPERIMENT")
    print(f"  d={d_model}, layers={n_layers}, max_depth={max_depth}")
    print(f"  GD budget: {gd_steps} steps")
    print(f"  Beam angles (probe counts): {probe_counts}")
    print("=" * 70)

    results = {}

    # 1. Train oracle
    print(f"\n  [1] Training GD oracle ({gd_steps} steps)...")
    t0 = time.time()
    oracle = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(oracle.parameters())
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(oracle, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(gd_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(oracle, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        oracle.update(optimizer.apply_gradients(grads, oracle))
        mx.eval(oracle.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 2000 == 0:
            ev = eval_model(oracle, np.random.RandomState(999),
                            max_depth=max_depth)
            print(f"    step {step+1}: acc={ev['accuracy']:.1%}")

    oracle_eval = eval_model(oracle, np.random.RandomState(999),
                             max_depth=max_depth)
    oracle_depth = eval_by_depth(oracle, np.random.RandomState(999),
                                 max_depth=max_depth)
    dt = time.time() - t0
    print(f"    Oracle: acc={oracle_eval['accuracy']:.1%} ({dt:.1f}s)")
    results["oracle"] = {
        "acc": oracle_eval["accuracy"],
        "depth": oracle_depth,
    }

    # Extract sign crystal for comparison
    crystal = extract_crystal(oracle)

    n_conditions = len(probe_counts) + 3  # + sign_copy + random + ce_etch

    # 2. Holographic distillation at various probe counts
    for i, n_probes in enumerate(probe_counts):
        print(f"\n  [{i+2}/{n_conditions+1}] Holographic distillation "
              f"({n_probes} beam angles)...")
        t0 = time.time()
        r = run_holographic_distill(
            oracle, n_probes=n_probes, n_etch_rounds=5,
            post_freeze_steps=gd_steps, d_model=d_model,
            n_layers=n_layers, batch_size=batch_size, lr=lr,
            max_depth=max_depth,
        )
        dt = time.time() - t0
        print(f"    best={r['best_acc']:.1%} ({dt:.1f}s)")
        results[f"holo_distill_{n_probes}"] = r

    # 3. Oracle crystal (sign copy)
    print(f"\n  [{len(probe_counts)+2}/{n_conditions+1}] "
          f"Oracle crystal (sign copy)...", end="", flush=True)
    t0 = time.time()
    r_sign = run_crystal_write_gd(crystal, "sign_copy", d_model, n_layers,
                                   gd_steps, batch_size, lr, max_depth)
    dt = time.time() - t0
    print(f" best={r_sign['best_acc']:.1%} ({dt:.1f}s)")
    results["sign_copy"] = r_sign

    # 4. Random plates
    print(f"  [{len(probe_counts)+3}/{n_conditions+1}] "
          f"Random plates...", end="", flush=True)
    t0 = time.time()
    rng_r = np.random.RandomState(42)
    random_crystal = []
    for layer_signs in crystal:
        layer_random = {}
        for key, signs in layer_signs.items():
            layer_random[key] = rng_r.choice(
                [-1.0, 1.0], size=signs.shape).astype(np.float32)
        random_crystal.append(layer_random)
    r_random = run_crystal_write_gd(random_crystal, "random", d_model,
                                     n_layers, gd_steps, batch_size, lr,
                                     max_depth)
    dt = time.time() - t0
    print(f" best={r_random['best_acc']:.1%} ({dt:.1f}s)")
    results["random"] = r_random

    # 5. CE etch r5
    print(f"  [{len(probe_counts)+4}/{n_conditions+1}] "
          f"CE etch (r5) + freeze + GD...", end="", flush=True)
    t0 = time.time()
    etch_model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(etch_model.parameters())
    etch_rng = np.random.RandomState(42)
    for r in range(5):
        etch_plates(etch_model, etch_rng, n_batches=200,
                    batch_size=batch_size, max_depth=max_depth)
        train_beams(etch_model, etch_rng, n_steps=500,
                    batch_size=batch_size, lr=lr, max_depth=max_depth)
        mx.clear_cache()

    for layer in etch_model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer_e = optim.Adam(learning_rate=lr)
    loss_and_grad_e = nn.value_and_grad(etch_model, masked_ce_loss)
    etch_log = []
    for step in range(gd_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, etch_rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad_e(etch_model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        etch_model.update(optimizer_e.apply_gradients(grads, etch_model))
        mx.eval(etch_model.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(etch_model, np.random.RandomState(999),
                            max_depth=max_depth)
            etch_log.append({"step": step + 1, **ev})

    etch_final = eval_model(etch_model, np.random.RandomState(999),
                            max_depth=max_depth)
    etch_depth = eval_by_depth(etch_model, np.random.RandomState(999),
                               max_depth=max_depth)
    dt = time.time() - t0
    r_etch = {
        "label": "ce_etch_r5",
        "best_acc": max(e["accuracy"] for e in etch_log) if etch_log else etch_final["accuracy"],
        "final_acc": etch_final["accuracy"],
        "final_depth": etch_depth,
        "log": etch_log,
    }
    print(f" best={r_etch['best_acc']:.1%} ({dt:.1f}s)")
    results["ce_etch_r5"] = r_etch

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  SUMMARY — Holographic Distillation")
    print(f"{'═' * 70}")

    oracle_acc = results["oracle"]["acc"]
    random_acc = results["random"]["best_acc"]

    print(f"\n  Oracle GD ceiling: {oracle_acc:.1%}")
    print()
    print(f"  {'Condition':>30}  {'Best':>7}  {'% Oracle':>9}  "
          f"{'vs Random':>10}")
    print(f"  {'─'*30}  {'─'*7}  {'─'*9}  {'─'*10}")

    conditions = [
        (f"Holo distill ({n})", results[f"holo_distill_{n}"]["best_acc"])
        for n in probe_counts
    ] + [
        ("Sign copy (oracle)", results["sign_copy"]["best_acc"]),
        ("Random plates", results["random"]["best_acc"]),
        ("CE etch r5", results["ce_etch_r5"]["best_acc"]),
    ]

    for label, acc in conditions:
        pct = acc / oracle_acc * 100 if oracle_acc > 0 else 0
        vs_r = acc - random_acc
        print(f"  {label:>30}  {acc:>6.1%}  {pct:>8.1f}%  {vs_r:>+9.1%}")

    # Depth breakdown
    print(f"\n  Depth breakdown:")
    print(f"  {'Condition':>30}  {'d1':>6}  {'d2':>6}  {'d3':>6}  {'d4':>6}")
    print(f"  {'─'*30}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}")

    for label, key in [
        ("Oracle GD", "oracle"),
        (f"Holo distill (200)", f"holo_distill_200"),
        ("Sign copy", "sign_copy"),
        ("Random plates", "random"),
        ("CE etch r5", "ce_etch_r5"),
    ]:
        data = results[key]
        fd = data.get("final_depth", data.get("depth", {}))
        vals = []
        for d in range(1, max_depth + 1):
            acc = fd.get(d, fd.get(str(d), {}))
            if isinstance(acc, dict):
                acc = acc.get("accuracy", 0)
            vals.append(acc if isinstance(acc, (int, float)) else 0)
        print(f"  {label:>30}  " + "  ".join(f"{v:>5.1%}" for v in vals))

    # Save
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
