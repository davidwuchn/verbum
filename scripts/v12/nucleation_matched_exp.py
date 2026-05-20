"""Nucleation Matched Experiment — Do matched signs + magnitudes beat everything?

Session 123 found: oracle signs + uniform magnitudes = worst (0.248).
Random signs + teacher magnitudes = best (0.568). The hypothesis:
signs and magnitudes must be MATCHED. The oracle failed because it
had the right signs with the wrong magnitudes.

This experiment tests 4 conditions head-to-head:

  1. RANDOM — random plates, uniform beam scales (baseline from exp 1)
  2. MAGNITUDE_ONLY — random plates, teacher magnitude beam scales
  3. SIGNS_ONLY — teacher signs, uniform beam scales (oracle from exp 1)
  4. MATCHED — teacher signs + teacher magnitude beam scales ← THE TEST

If MATCHED wins, the design is:
  - Extract sign(W) → plates
  - Extract per-dim magnitude → beam scales
  - Both from same teacher → coherent hologram
  - GD refines beam path through the pre-etched hologram

Also test with plates unfrozen for MATCHED to see if GD can refine
the hologram when starting from a coherent position.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/nucleation_matched_exp.py

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
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID, ID2TOK,
    TernaryLinear,
    CausalSelfAttention, GDLayer, GDModel,
    TernaryCausalAttention, HoloBeamLayer, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model,
    generate_batch,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "nucleation-matched"
D_MODEL = 128
N_LAYERS = 3
N_STEPS = 3000
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def extract_magnitude_from_gd(teacher: GDModel) -> list[dict[str, np.ndarray]]:
    """Extract per-output-dim RMS magnitude from teacher's weight matrices."""
    templates = []
    for layer in teacher.layers:
        layer_mag = {}
        for name, proj in [
            ("k", layer.attn.k_proj),
            ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj),
            ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)  # (d, d)
            row_rms = np.sqrt(np.mean(W ** 2, axis=1))
            layer_mag[name] = row_rms.astype(np.float32)
        templates.append(layer_mag)
    return templates


def apply_magnitude_template(model: HoloModel, templates: list[dict[str, np.ndarray]]):
    """Set beam scales from magnitude template."""
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(templates[i]["k"])
        layer.attn.v_scale = mx.array(templates[i]["v"])
        layer.attn.o_scale = mx.array(templates[i]["o"])
        layer.ffn_scale = mx.array(templates[i]["ffn"])


def train_student(model: HoloModel, name: str, freeze_plates: bool = True) -> dict:
    """Train with diagnostics. Returns trajectory."""
    mx.eval(model.parameters())

    if freeze_plates:
        for layer in model.layers:
            layer.attn.k_plate.freeze()
            layer.attn.v_plate.freeze()
            layer.attn.o_plate.freeze()
            layer.ffn_plate.freeze()

    params = count_holo_params(model)
    log(f"  [{name}] plates={'frozen' if freeze_plates else 'live'}, "
        f"continuous={params['continuous']:,}")

    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    prev_fp = holo_plate_fingerprint(model)
    trajectory = []

    for step in range(N_STEPS):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)

        # Don't zero plate grads — frozen plates won't have grad entries anyway
        # For unfrozen: TernaryLinear weights don't update through normal optim
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask

        if (step + 1) % 50 == 0:
            mx.clear_cache()

        if (step + 1) % EVAL_INTERVAL == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=20, max_depth=MAX_DEPTH)
            curr_fp = holo_plate_fingerprint(model)
            diff = holo_plate_diff(prev_fp, curr_fp)
            prev_fp = curr_fp

            trajectory.append({
                "step": step + 1,
                "loss": ev["loss"],
                "accuracy": ev["accuracy"],
                "sign_change_rate": diff["fraction"],
            })

            if (step + 1) % 500 == 0:
                log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    return {
        "condition": name,
        "trajectory": trajectory,
        "final_loss": trajectory[-1]["loss"],
        "final_accuracy": trajectory[-1]["accuracy"],
        "best_accuracy": max(t["accuracy"] for t in trajectory),
        "best_loss": min(t["loss"] for t in trajectory),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # ── Train teacher ──
    log("═" * 60)
    log("Training teacher d=128...")
    log("═" * 60)
    teacher = GDModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(teacher.parameters())
    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(teacher, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(5000):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(teacher, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        teacher.update(optimizer.apply_gradients(grads, teacher))
        mx.eval(teacher.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 100 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"  Step {step+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    teacher_eval = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Teacher final: loss={teacher_eval['loss']:.4f}, acc={teacher_eval['accuracy']:.4f}")
    results["teacher"] = teacher_eval

    # ── Extract both sign and magnitude ──
    crystal = extract_crystal(teacher)
    mag_template = extract_magnitude_from_gd(teacher)
    log(f"  Crystal: {len(crystal)} layers")
    log(f"  Magnitudes: {len(mag_template)} layers, "
        f"sample RMS range: [{mag_template[0]['k'].min():.4f}, {mag_template[0]['k'].max():.4f}]")

    # ── Condition 1: RANDOM (baseline) ──
    log(f"\n{'═'*60}\nCONDITION 1: RANDOM\n{'═'*60}")
    m1 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m1.parameters())
    results["random"] = train_student(m1, "RANDOM")

    # ── Condition 2: MAGNITUDE_ONLY (random signs + teacher magnitudes) ──
    log(f"\n{'═'*60}\nCONDITION 2: MAGNITUDE_ONLY\n{'═'*60}")
    m2 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m2.parameters())
    apply_magnitude_template(m2, mag_template)
    mx.eval(m2.parameters())
    results["magnitude_only"] = train_student(m2, "MAGNITUDE_ONLY")

    # ── Condition 3: SIGNS_ONLY (teacher signs + uniform magnitudes) ──
    log(f"\n{'═'*60}\nCONDITION 3: SIGNS_ONLY\n{'═'*60}")
    m3 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m3.parameters())
    write_crystal_to_model(m3, crystal)
    mx.eval(m3.parameters())
    results["signs_only"] = train_student(m3, "SIGNS_ONLY")

    # ── Condition 4: MATCHED (teacher signs + teacher magnitudes) ── THE KEY TEST
    log(f"\n{'═'*60}\nCONDITION 4: MATCHED (signs + magnitudes from same teacher)\n{'═'*60}")
    m4 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m4.parameters())
    write_crystal_to_model(m4, crystal)
    apply_magnitude_template(m4, mag_template)
    mx.eval(m4.parameters())
    results["matched"] = train_student(m4, "MATCHED")

    # ── Condition 5: MATCHED + different random seed for beam init ──
    # (to verify it's not a seed artifact)
    log(f"\n{'═'*60}\nCONDITION 5: MATCHED_SEED2\n{'═'*60}")
    mx.random.seed(1337)
    m5 = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(m5.parameters())
    write_crystal_to_model(m5, crystal)
    apply_magnitude_template(m5, mag_template)
    mx.eval(m5.parameters())
    mx.random.seed(42)  # reset
    results["matched_seed2"] = train_student(m5, "MATCHED_SEED2")

    # ── Summary ──
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed, "d_model": D_MODEL,
                       "n_layers": N_LAYERS, "n_steps": N_STEPS}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Matched Signs + Magnitudes")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: loss={teacher_eval['loss']:.4f}, acc={teacher_eval['accuracy']:.4f}\n")

    log(f"  {'Condition':<20s} {'Best Loss':>10s} {'Best Acc':>10s} {'Final Acc':>10s}")
    log(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*10}")
    for name in ["random", "magnitude_only", "signs_only", "matched", "matched_seed2"]:
        r = results[name]
        log(f"  {name:<20s} {r['best_loss']:10.4f} {r['best_accuracy']:10.4f} "
            f"{r['final_accuracy']:10.4f}")

    # Learning curves
    log(f"\n  LEARNING CURVES (accuracy):")
    keys = ["random", "magnitude_only", "signs_only", "matched", "matched_seed2"]
    log(f"  {'Step':>6s}  " + "  ".join(f"{n[:10]:>10s}" for n in keys))
    log(f"  {'─'*6}  " + "  ".join("─"*10 for _ in keys))
    max_pts = min(len(results[k]["trajectory"]) for k in keys)
    for i in range(0, min(max_pts, 30), 2):  # every other point
        step = results[keys[0]]["trajectory"][i]["step"]
        accs = [results[k]["trajectory"][i]["accuracy"] for k in keys]
        log(f"  {step:6d}  " + "  ".join(f"{a:10.4f}" for a in accs))

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
