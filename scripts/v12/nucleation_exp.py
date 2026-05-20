"""Nucleation Speed Experiment — Does projected teacher structure accelerate hologram discovery?

Central hypothesis: GD must discover that the hologram exists before it can
focus the beam through it. Pre-loading holographic structure gives GD a
non-random starting point, so the nucleation cascade fires faster.

Experiment: train a teacher (GD model, d=256, 3 layers), then test how
quickly different student initializations nucleate on the same task.

Five conditions (all HoloModel, d=128, 3 layers, plates frozen, beam-only GD):
  1. RANDOM — Kaiming random plates (blank hologram)
  2. ORACLE — sign(W) copied from a teacher trained at d=128 (perfect hologram)
  3. SVD_PROJ — teacher (d=256) projected to d=128 via SVD, then sign
  4. SVD_PROJ_UNFROZEN — same as 3 but plates NOT frozen (GD can refine hologram)
  5. MAGNITUDE — random signs but magnitude template from SVD-projected teacher

Measure every 100 steps for 3000 steps:
  - Loss
  - Token accuracy on reduction task
  - Sign change rate (% of plate signs that flipped since last checkpoint)

The SVD projection: teacher W_q is (256, 256). SVD: W = U @ S @ Vt.
Project to d=128: W_small = Vt[:128,:] @ W @ Vt[:128,:].T = (128, 128).
This keeps the top-128 interference patterns of the teacher hologram.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/nucleation_exp.py

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
    generate_batch, generate_example,
    _zero_plate_grads,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model


def _safe_zero_plate_grads(grads, n_layers):
    """Zero out plate gradients, tolerant of missing keys (frozen plates)."""
    for i in range(n_layers):
        lg = grads.get("layers", {})
        if not isinstance(lg, (dict, list)):
            continue
        if isinstance(lg, list):
            if i >= len(lg):
                continue
            layer_g = lg[i]
        else:
            layer_g = lg.get(i, lg.get(str(i), {}))
        if not isinstance(layer_g, dict):
            continue
        # Attention plates
        attn_g = layer_g.get("attn", {})
        for pname in ["k_plate", "v_plate", "o_plate"]:
            plate_g = attn_g.get(pname, {})
            if isinstance(plate_g, dict) and "weight" in plate_g:
                plate_g["weight"] = mx.zeros_like(plate_g["weight"])
        # FFN plate
        ffn_g = layer_g.get("ffn_plate", {})
        if isinstance(ffn_g, dict) and "weight" in ffn_g:
            ffn_g["weight"] = mx.zeros_like(ffn_g["weight"])

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "nucleation"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Phase 0: Train teachers
# ══════════════════════════════════════════════════════════════════════

def train_teacher(d_model: int, n_steps: int = 5000) -> GDModel:
    """Train a full-GD teacher to convergence."""
    model = GDModel(d_model=d_model, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    n_params = sum(p.size for _, p in tree_flatten(model.parameters()))
    log(f"  Teacher d={d_model}: {n_params:,} params")

    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 100 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {step+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    final = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Teacher final: loss={final['loss']:.4f}, acc={final['accuracy']:.4f}")
    return model


# ══════════════════════════════════════════════════════════════════════
# SVD projection: teacher d=256 → student d=128
# ══════════════════════════════════════════════════════════════════════

def svd_project_crystal(teacher: GDModel, d_small: int) -> list[dict[str, np.ndarray]]:
    """Project teacher's weight signs through SVD to a smaller dimension.

    For each weight matrix W (d_big × d_big):
      1. SVD: W = U @ diag(S) @ Vt
      2. Projection basis: P = Vt[:d_small, :]  (d_small × d_big)
      3. Projected: W_small = P @ W @ P.T  (d_small × d_small)
      4. Crystal: sign(W_small)

    This preserves the top-d_small interference patterns in the hologram.
    """
    crystal = []
    d_big = teacher.d_model

    for layer in teacher.layers:
        layer_signs = {}

        for name, proj in [
            ("k", layer.attn.k_proj),
            ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj),
            ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)  # (d_big, d_big)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)

            # Project to smaller dimension
            P = Vt[:d_small, :]  # (d_small, d_big)
            W_small = P @ W @ P.T  # (d_small, d_small)
            signs = np.sign(W_small).astype(np.float32)

            # Replace zeros
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))

            layer_signs[name] = signs

        crystal.append(layer_signs)

    return crystal


def extract_magnitude_template(teacher: GDModel, d_small: int) -> list[dict[str, np.ndarray]]:
    """Extract per-row magnitude profile from SVD-projected teacher weights.

    Returns magnitude templates (d_small,) per projection, for use as
    beam scale initialization in the student.
    """
    templates = []
    for layer in teacher.layers:
        layer_mag = {}
        for name, proj in [
            ("k", layer.attn.k_proj),
            ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj),
            ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            W_small = P @ W @ P.T
            # Per-output-dim RMS magnitude
            row_rms = np.sqrt(np.mean(W_small ** 2, axis=1))  # (d_small,)
            layer_mag[name] = row_rms.astype(np.float32)
        templates.append(layer_mag)
    return templates


# ══════════════════════════════════════════════════════════════════════
# Training loop with diagnostics
# ══════════════════════════════════════════════════════════════════════

def train_student(
    model: HoloModel,
    condition_name: str,
    freeze_plates: bool = True,
) -> dict:
    """Train student model, recording nucleation diagnostics."""
    mx.eval(model.parameters())

    if freeze_plates:
        for layer in model.layers:
            layer.attn.k_plate.freeze()
            layer.attn.v_plate.freeze()
            layer.attn.o_plate.freeze()
            layer.ffn_plate.freeze()

    params = count_holo_params(model)
    log(f"\n  [{condition_name}] plates={'frozen' if freeze_plates else 'live'}, "
        f"continuous={params['continuous']:,}")

    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    # Initial plate snapshot
    prev_fingerprint = holo_plate_fingerprint(model)

    trajectory = []
    step_losses = []

    for step in range(N_STEPS):
        input_ids, targets, mask = generate_batch(
            BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)

        if freeze_plates:
            _safe_zero_plate_grads(grads, len(model.layers))

        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())

        step_losses.append(float(loss_val.item()))
        del loss_val, grads, input_ids, targets, mask

        if (step + 1) % 50 == 0:
            mx.clear_cache()

        if (step + 1) % EVAL_INTERVAL == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=20, max_depth=MAX_DEPTH)

            # Sign change rate
            curr_fingerprint = holo_plate_fingerprint(model)
            diff = holo_plate_diff(prev_fingerprint, curr_fingerprint)
            prev_fingerprint = curr_fingerprint

            # Cross-layer sign correlation (weight-level self-similarity)
            sign_corrs = []
            for i in range(len(model.layers)):
                for j in range(i + 1, len(model.layers)):
                    si = np.sign(np.array(model.layers[i].attn.k_plate.weight)).flatten()
                    sj = np.sign(np.array(model.layers[j].attn.k_plate.weight)).flatten()
                    corr = float(np.corrcoef(si.astype(float), sj.astype(float))[0, 1])
                    sign_corrs.append(corr)
            mean_sign_corr = float(np.mean(sign_corrs)) if sign_corrs else 0.0

            recent_loss = float(np.mean(step_losses[-EVAL_INTERVAL:]))

            checkpoint = {
                "step": step + 1,
                "loss": ev["loss"],
                "accuracy": ev["accuracy"],
                "recent_train_loss": recent_loss,
                "sign_change_rate": diff["fraction"],
                "cross_layer_sign_corr": mean_sign_corr,
            }
            trajectory.append(checkpoint)

            log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, "
                f"acc={ev['accuracy']:.4f}, "
                f"sign_Δ={diff['fraction']:.4f}, "
                f"xlay_corr={mean_sign_corr:.4f}")

    return {
        "condition": condition_name,
        "params": params,
        "freeze_plates": freeze_plates,
        "trajectory": trajectory,
        "final_loss": trajectory[-1]["loss"],
        "final_accuracy": trajectory[-1]["accuracy"],
        "best_accuracy": max(t["accuracy"] for t in trajectory),
        "best_loss": min(t["loss"] for t in trajectory),
    }


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    results = {}

    # ── Train teachers ──
    log("═" * 60)
    log("PHASE 0: Training teachers")
    log("═" * 60)

    log("\nTraining teacher d=256 (for SVD projection)...")
    teacher_big = train_teacher(D_TEACHER, n_steps=5000)

    log("\nTraining teacher d=128 (for oracle crystal)...")
    teacher_small = train_teacher(D_STUDENT, n_steps=5000)

    # ── Extract crystals ──
    log("\n" + "═" * 60)
    log("Extracting crystals...")
    log("═" * 60)

    oracle_crystal = extract_crystal(teacher_small)
    log(f"  Oracle crystal: {len(oracle_crystal)} layers, "
        f"shapes: {[list(v.shape) for v in oracle_crystal[0].values()]}")

    svd_crystal = svd_project_crystal(teacher_big, D_STUDENT)
    log(f"  SVD crystal: {len(svd_crystal)} layers, "
        f"shapes: {[list(v.shape) for v in svd_crystal[0].values()]}")

    mag_template = extract_magnitude_template(teacher_big, D_STUDENT)
    log(f"  Magnitude template: {len(mag_template)} layers")

    # ── Condition 1: RANDOM ──
    log("\n" + "═" * 60)
    log("CONDITION 1: RANDOM (blank hologram)")
    log("═" * 60)
    model_random = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model_random.parameters())
    results["random"] = train_student(model_random, "RANDOM", freeze_plates=True)

    # ── Condition 2: ORACLE ──
    log("\n" + "═" * 60)
    log("CONDITION 2: ORACLE (perfect crystal from d=128 teacher)")
    log("═" * 60)
    model_oracle = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model_oracle.parameters())
    write_crystal_to_model(model_oracle, oracle_crystal)
    mx.eval(model_oracle.parameters())
    results["oracle"] = train_student(model_oracle, "ORACLE", freeze_plates=True)

    # ── Condition 3: SVD_PROJ (frozen) ──
    log("\n" + "═" * 60)
    log("CONDITION 3: SVD_PROJ (teacher d=256 projected to d=128, frozen)")
    log("═" * 60)
    model_svd = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model_svd.parameters())
    write_crystal_to_model(model_svd, svd_crystal)
    mx.eval(model_svd.parameters())
    results["svd_proj"] = train_student(model_svd, "SVD_PROJ", freeze_plates=True)

    # ── Condition 4: SVD_PROJ_UNFROZEN ──
    log("\n" + "═" * 60)
    log("CONDITION 4: SVD_PROJ_UNFROZEN (GD can refine hologram)")
    log("═" * 60)
    model_svd_live = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model_svd_live.parameters())
    write_crystal_to_model(model_svd_live, svd_crystal)
    mx.eval(model_svd_live.parameters())
    results["svd_proj_unfrozen"] = train_student(
        model_svd_live, "SVD_PROJ_UNFROZEN", freeze_plates=False)

    # ── Condition 5: MAGNITUDE (random signs, teacher magnitude template) ──
    log("\n" + "═" * 60)
    log("CONDITION 5: MAGNITUDE (random signs, teacher magnitude profile)")
    log("═" * 60)
    model_mag = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model_mag.parameters())
    # Apply magnitude template to beam scales
    for i, layer in enumerate(model_mag.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])
    mx.eval(model_mag.parameters())
    results["magnitude"] = train_student(model_mag, "MAGNITUDE", freeze_plates=True)

    # ── Summary ──
    elapsed = time.time() - t_start
    results["meta"] = {
        "d_teacher": D_TEACHER,
        "d_student": D_STUDENT,
        "n_layers": N_LAYERS,
        "n_steps": N_STEPS,
        "elapsed_seconds": elapsed,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Nucleation Speed")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s\n")

    # Print comparison table
    log(f"  {'Condition':<22s} {'Best Loss':>10s} {'Best Acc':>10s} "
        f"{'Final Acc':>10s} {'Nucleation':>12s}")
    log(f"  {'─'*22} {'─'*10} {'─'*10} {'─'*10} {'─'*12}")

    for name in ["random", "oracle", "svd_proj", "svd_proj_unfrozen", "magnitude"]:
        r = results[name]
        # Find nucleation point: first step where accuracy > 0.3
        nuc_step = "never"
        for t in r["trajectory"]:
            if t["accuracy"] > 0.3:
                nuc_step = f"step {t['step']}"
                break

        log(f"  {name:<22s} {r['best_loss']:10.4f} {r['best_accuracy']:10.4f} "
            f"{r['final_accuracy']:10.4f} {nuc_step:>12s}")

    # Learning curve comparison (first 10 checkpoints)
    log(f"\n  LEARNING CURVES (accuracy at each checkpoint):")
    log(f"  {'Step':>6s}  " + "  ".join(f"{n:>10s}" for n in
        ["random", "oracle", "svd_proj", "svd_unfz", "magnitude"]))
    log(f"  {'─'*6}  " + "  ".join("─"*10 for _ in range(5)))

    keys = ["random", "oracle", "svd_proj", "svd_proj_unfrozen", "magnitude"]
    max_points = min(len(results[k]["trajectory"]) for k in keys)
    for i in range(min(max_points, 15)):
        step = results[keys[0]]["trajectory"][i]["step"]
        accs = [results[k]["trajectory"][i]["accuracy"] for k in keys]
        log(f"  {step:6d}  " + "  ".join(f"{a:10.4f}" for a in accs))

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
