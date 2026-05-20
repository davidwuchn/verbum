"""Q2 Distill-Etch — Teacher beam as reference for phase correction.

Protocol:
  1. Train teacher (GD, d=128) to convergence
  2. Q2-simulate: quantize teacher weights to 2-bit, extract signs
  3. Write Q2 signs into HoloModel ternary plates
  4. Initialize beam scales from teacher magnitude profile
  5. Etch: use KL(teacher_logits, student_logits) as the error signal
     - Teacher logits = reference beam (the correct hologram readout)
     - Student logits = distorted readout (damaged phases)
     - KL gradient = which signs to flip to refocus
  6. Alternate: etch rounds (fix signs) + beam GD (refine continuous)

Conditions:
  1. Q2_DISTILL_ETCH: Q2 plates + teacher mag + teacher-guided etch
  2. RANDOM_DISTILL_ETCH: random plates + teacher mag + teacher-guided etch
  3. Q2_BEAM_ONLY: Q2 plates + teacher mag + beam-only GD (no etch, no teacher)
  4. RANDOM_BEAM_ONLY: random plates + teacher mag + beam-only GD (baseline)
  5. GD_CEILING: full GD model at same d_model (upper bound)

The key test: does Q2_DISTILL_ETCH recover to near the teacher?

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_distill_etch_exp.py

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
from mlx.utils import tree_flatten

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID,
    GDModel, HoloModel,
    TernaryLinear,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model,
    generate_batch,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-distill-etch"
D_MODEL = 128
N_LAYERS = 3
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4

# Etch config
N_ETCH_ROUNDS = 15
ETCH_BATCHES = 100       # batches per etch accumulation
BEAM_STEPS_PER_ROUND = 200  # beam GD steps between etch rounds
ETCH_CONFIDENCE = 0.6    # accumulator threshold for flipping


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def q2_simulate_weights(W: np.ndarray, n_bits: int = 2, block_size: int = 32) -> np.ndarray:
    """Q2 simulate and return sign pattern."""
    W_flat = W.flatten()
    n = len(W_flat)
    pad = (block_size - n % block_size) % block_size
    W_padded = np.concatenate([W_flat, np.zeros(pad)])
    W_blocks = W_padded.reshape(-1, block_size)
    n_levels = 2 ** (n_bits - 1)
    scales = np.maximum(np.max(np.abs(W_blocks), axis=1, keepdims=True), 1e-10)
    W_norm = W_blocks / scales
    W_quant = np.round(W_norm * n_levels).clip(-n_levels, n_levels)
    W_dequant = (W_quant / n_levels) * scales
    signs = np.sign(W_dequant.flatten()[:n].reshape(W.shape)).astype(np.float32)
    # Replace zeros with random
    zeros = signs == 0
    if zeros.any():
        signs[zeros] = np.random.RandomState(42).choice([-1.0, 1.0], size=int(zeros.sum()))
    return signs


def extract_q2_crystal(teacher: GDModel, n_bits: int = 2) -> list[dict[str, np.ndarray]]:
    """Q2-quantize teacher weights, extract sign patterns."""
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            layer_signs[name] = q2_simulate_weights(W, n_bits=n_bits)
        crystal.append(layer_signs)
    return crystal


def extract_magnitude_template(teacher: GDModel) -> list[dict[str, np.ndarray]]:
    """Per-output-dim RMS magnitude from teacher."""
    templates = []
    for layer in teacher.layers:
        layer_mag = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            layer_mag[name] = np.sqrt(np.mean(W ** 2, axis=1)).astype(np.float32)
        templates.append(layer_mag)
    return templates


def apply_mag_template(model: HoloModel, templates):
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(templates[i]["k"])
        layer.attn.v_scale = mx.array(templates[i]["v"])
        layer.attn.o_scale = mx.array(templates[i]["o"])
        layer.ffn_scale = mx.array(templates[i]["ffn"])


# ══════════════════════════════════════════════════════════════════════
# Teacher-guided etch: use KL(teacher, student) as error signal
# ══════════════════════════════════════════════════════════════════════

def distill_etch_round(student: HoloModel, teacher: GDModel, rng,
                       n_batches: int = ETCH_BATCHES) -> tuple[int, float]:
    """One round of teacher-guided etching.

    Accumulate sign(gradient) from KL(teacher, student) loss.
    Flip confident positions.
    """
    plates = _get_plates(student)
    accumulators = [np.zeros((p.out_features, p.in_features), dtype=np.float64)
                    for _, p in plates]

    plate_paths = []
    for i, layer in enumerate(student.layers):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    def distill_loss(student_model, input_ids, targets, mask):
        """KL divergence from teacher to student on output positions."""
        teacher_logits = mx.stop_gradient(teacher(input_ids))
        student_logits = student_model(input_ids)

        # KL only on masked (output) positions
        B, T, V = student_logits.shape
        teacher_lse = mx.logsumexp(teacher_logits, axis=-1, keepdims=True)
        student_lse = mx.logsumexp(student_logits, axis=-1, keepdims=True)
        teacher_log_probs = teacher_logits - teacher_lse
        student_log_probs = student_logits - student_lse
        teacher_probs = mx.exp(teacher_log_probs)

        # KL = sum(p * (log_p - log_q))
        kl = mx.sum(teacher_probs * (teacher_log_probs - student_log_probs), axis=-1)
        return (kl * mask).sum() / (mask.sum() + 1e-8)

    loss_and_grad = nn.value_and_grad(student, distill_loss)

    for b in range(n_batches):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)

        for pidx, (layer_idx, pname) in enumerate(plate_paths):
            # Navigate grad tree
            lg = grads.get("layers", [])
            if isinstance(lg, list) and layer_idx < len(lg):
                layer_g = lg[layer_idx]
            else:
                continue
            parts = pname.split(".")
            g = layer_g
            for part in parts:
                if isinstance(g, dict) and part in g:
                    g = g[part]
                else:
                    g = None
                    break
            if g is not None and isinstance(g, dict) and "weight" in g:
                gw = g["weight"]
                mx.eval(gw)
                accumulators[pidx] += np.sign(np.array(gw))

        del loss_val, grads, input_ids, targets, mask
        if (b + 1) % 25 == 0:
            mx.clear_cache()

    # Flip confident positions
    # Convention: match original etch_plates() from mini_holo_d_sweep_v2.py
    # desired_sign used for BOTH condition check AND new value (consistency!)
    total_flipped = 0
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        confidence = np.abs(acc) / n_batches
        desired_sign = np.sign(acc)
        current = np.sign(np.array(plate.weight)).astype(np.int8)
        should_flip = (
            (confidence > ETCH_CONFIDENCE)
            & (desired_sign != 0)
            & (desired_sign != current)
        )
        new_signs = np.where(should_flip,
                             desired_sign.astype(np.float32),
                             current.astype(np.float32))
        plate.weight = mx.array(new_signs)
        mx.eval(plate.weight)
        total_flipped += int(should_flip.sum())

    return total_flipped


def beam_gd_steps(student: HoloModel, rng, n_steps: int = BEAM_STEPS_PER_ROUND):
    """Beam-only GD using CE loss (normal LM training)."""
    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)

    # Freeze plates
    for layer in student.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        student.update(optimizer.apply_gradients(grads, student))
        mx.eval(student.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()

    # Unfreeze plates for next etch round
    for layer in student.layers:
        layer.attn.k_plate.unfreeze()
        layer.attn.v_plate.unfreeze()
        layer.attn.o_plate.unfreeze()
        layer.ffn_plate.unfreeze()


def train_with_etch(student, teacher, name, use_teacher_etch=True):
    """Full training loop: alternating etch + beam GD."""
    log(f"\n  [{name}]")
    mx.eval(student.parameters())
    rng = np.random.RandomState(42)
    prev_fp = holo_plate_fingerprint(student)

    trajectory = []
    for round_idx in range(N_ETCH_ROUNDS):
        # Etch phase
        if use_teacher_etch:
            flips = distill_etch_round(student, teacher, rng)
        else:
            flips = 0

        # Beam GD phase
        beam_gd_steps(student, rng)

        # Eval
        ev = eval_model(student, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
        curr_fp = holo_plate_fingerprint(student)
        diff = holo_plate_diff(prev_fp, curr_fp)
        prev_fp = curr_fp

        # Sign agreement with original teacher crystal
        trajectory.append({
            "round": round_idx + 1,
            "flips": flips,
            "sign_change": diff["fraction"],
            "loss": ev["loss"],
            "accuracy": ev["accuracy"],
        })
        log(f"    Round {round_idx+1:2d}: flips={flips:4d}, "
            f"loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
        mx.clear_cache()

    return {
        "condition": name,
        "trajectory": trajectory,
        "final_acc": trajectory[-1]["accuracy"],
        "best_acc": max(t["accuracy"] for t in trajectory),
        "final_loss": trajectory[-1]["loss"],
    }


def train_beam_only(student, name):
    """Beam-only GD (no etch, no teacher signal)."""
    log(f"\n  [{name}]")
    mx.eval(student.parameters())
    rng = np.random.RandomState(42)

    # Freeze plates permanently
    for layer in student.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)

    total_steps = N_ETCH_ROUNDS * (ETCH_BATCHES + BEAM_STEPS_PER_ROUND)
    eval_interval = total_steps // N_ETCH_ROUNDS

    trajectory = []
    for step in range(total_steps):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        student.update(optimizer.apply_gradients(grads, student))
        mx.eval(student.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % eval_interval == 0:
            ev = eval_model(student, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
            trajectory.append({
                "step": step + 1,
                "loss": ev["loss"],
                "accuracy": ev["accuracy"],
            })
            log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    return {
        "condition": name,
        "trajectory": trajectory,
        "final_acc": trajectory[-1]["accuracy"],
        "best_acc": max(t["accuracy"] for t in trajectory),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # ── Train teacher ──
    log("═" * 60)
    log("Training teacher d=128...")
    teacher = GDModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(teacher.parameters())
    opt = optim.Adam(learning_rate=LR)
    lg = nn.value_and_grad(teacher, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(5000):
        ids, tgt, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lg(teacher, ids, tgt, mask)
        mx.eval(lv, gr)
        teacher.update(opt.apply_gradients(gr, teacher))
        mx.eval(teacher.parameters())
        del lv, gr
        if (step+1) % 100 == 0: mx.clear_cache()
        if (step+1) % 1000 == 0:
            ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"  Step {step+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Teacher final: loss={teacher_ev['loss']:.4f}, acc={teacher_ev['accuracy']:.4f}")
    results["teacher"] = teacher_ev

    # ── Extract crystals ──
    oracle_crystal = extract_crystal(teacher)
    q2_crystal = extract_q2_crystal(teacher, n_bits=2)
    mag_template = extract_magnitude_template(teacher)

    # Measure Q2 sign damage
    total_pos = sum(c[k].size for c in oracle_crystal for k in c)
    damaged = sum(int((oracle_crystal[i][k] != q2_crystal[i][k]).sum())
                  for i in range(len(oracle_crystal)) for k in oracle_crystal[i])
    log(f"  Q2 sign damage: {damaged}/{total_pos} = {damaged/total_pos*100:.1f}%")

    # ── Condition 1: Q2_DISTILL_ETCH ──
    log(f"\n{'═'*60}\nQ2_DISTILL_ETCH")
    m1 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m1.parameters())
    write_crystal_to_model(m1, q2_crystal)
    apply_mag_template(m1, mag_template)
    mx.eval(m1.parameters())
    results["q2_distill_etch"] = train_with_etch(m1, teacher, "Q2_DISTILL_ETCH", use_teacher_etch=True)

    # ── Condition 2: RANDOM_DISTILL_ETCH ──
    log(f"\n{'═'*60}\nRANDOM_DISTILL_ETCH")
    m2 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m2.parameters())
    apply_mag_template(m2, mag_template)
    mx.eval(m2.parameters())
    results["random_distill_etch"] = train_with_etch(m2, teacher, "RANDOM_DISTILL_ETCH", use_teacher_etch=True)

    # ── Condition 3: Q2_BEAM_ONLY ──
    log(f"\n{'═'*60}\nQ2_BEAM_ONLY")
    m3 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m3.parameters())
    write_crystal_to_model(m3, q2_crystal)
    apply_mag_template(m3, mag_template)
    mx.eval(m3.parameters())
    results["q2_beam_only"] = train_beam_only(m3, "Q2_BEAM_ONLY")

    # ── Condition 4: RANDOM_BEAM_ONLY ──
    log(f"\n{'═'*60}\nRANDOM_BEAM_ONLY")
    m4 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m4.parameters())
    apply_mag_template(m4, mag_template)
    mx.eval(m4.parameters())
    results["random_beam_only"] = train_beam_only(m4, "RANDOM_BEAM_ONLY")

    # ── Summary ──
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed, "d_model": D_MODEL,
                       "n_etch_rounds": N_ETCH_ROUNDS}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Distill-Etch")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}\n")
    log(f"  {'Condition':<24s} {'Best Acc':>10s} {'Final Acc':>10s}")
    log(f"  {'─'*24} {'─'*10} {'─'*10}")
    for name in ["q2_distill_etch", "random_distill_etch", "q2_beam_only", "random_beam_only"]:
        r = results[name]
        log(f"  {name:<24s} {r['best_acc']:10.4f} {r['final_acc']:10.4f}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
