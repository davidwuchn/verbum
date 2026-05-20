"""Loom-Read Etch Nucleation — Does weave-separated etching beat uniform sign copy?

Session 124, experiment 5. The etcher VSM showed the teacher's weight
matrices contain multiple independent subcrystals at different CCA
angle bands. Consensus sign extraction (uniform sign(W)) averages
across these subcrystals, creating noise. Loom-read extraction
extracts per-family sign patterns and superposes them using magnitude
weights.

6 conditions (all HoloModel, d=128, 3 layers, plates frozen, beam-only GD):
  1. RANDOM — Kaiming random plates (blank hologram)
  2. ORACLE — sign(W) from teacher at d=128 (perfect crystal, same dim)
  3. SVD_SIGN — sign(SVD_project(teacher d=256 → d=128)) (naive projection)
  4. MAGNITUDE — random signs + teacher magnitude template (session 123 winner)
  5. LOOM_READ — CCA decomposition of teacher, per-band magnitude-weighted
                 sign extraction, superposed into plates
  6. LOOM_MAG — LOOM_READ signs + teacher magnitude template (combining both)

The LOOM_READ extraction:
  For each layer in teacher (d=256):
    1. CCA between K_proj and FFN weights → angle bands
    2. For each band with >1 direction:
       a. Project sign(W) onto band directions
       b. Weight by per-dimension RMS magnitude from KIBC reduction probes
       c. Extract the dominant sign pattern
    3. SVD-project the loom-weighted signs to d=128
    4. Write into student plates

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_etch_nucleation_exp.py

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


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-etch-nucleation"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4


# ══════════════════════════════════════════════════════════════════════
# Loom-read extraction
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(W_a: np.ndarray, W_b: np.ndarray, k: int = None):
    """Compute CCA between two weight matrices, return angle-binned directions.
    
    W_a: (d_out_a, d_in)  e.g. K projection
    W_b: (d_out_b, d_in)  e.g. FFN projection
    
    Returns: angles (k,), shared_dirs (d_in, k)
    """
    d_in = W_a.shape[1]
    if k is None:
        k = min(d_in, min(W_a.shape[0], W_b.shape[0]))

    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)

    k = min(k, Vt_a.shape[0], Vt_b.shape[0])
    A = Vt_a[:k, :].T  # (d_in, k)
    B = Vt_b[:k, :].T

    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)

    U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S, 0, 1)))

    dirs_a = Qa @ U
    dirs_b = Qb @ Vt.T
    shared = dirs_a + dirs_b
    norms = np.linalg.norm(shared, axis=0, keepdims=True)
    shared = shared / np.maximum(norms, 1e-8)

    return angles, shared


def loom_weighted_sign(W: np.ndarray, angles: np.ndarray, shared_dirs: np.ndarray):
    """Extract sign(W) weighted by loom structure.
    
    Instead of uniform sign(W), weight each dimension by how much it
    contributes to crystal-carrying angle bands (35-72°, where crystal
    agreement > 0.90 and subcrystals are most differentiated).
    
    W: (d_out, d_in) weight matrix
    angles: (k,) CCA angles
    shared_dirs: (d_in, k) CCA directions
    
    Returns: (d_out, d_in) loom-weighted sign matrix
    """
    d_out, d_in = W.shape

    # Crystal-carrying bands: 35-72° (mid_low through holographic)
    crystal_mask = (angles >= 35) & (angles < 72)
    if crystal_mask.sum() < 2:
        # Fallback to uniform sign
        return np.sign(W)

    crystal_dirs = shared_dirs[:, crystal_mask]  # (d_in, n_crystal)

    # How much does each input dimension contribute to crystal bands?
    # Project each basis vector onto crystal directions
    dim_crystal_energy = np.sum(crystal_dirs ** 2, axis=1)  # (d_in,)

    # Normalize to [0, 1]
    dim_weight = dim_crystal_energy / (dim_crystal_energy.max() + 1e-10)

    # High crystal dimensions: use sign(W) faithfully
    # Low crystal dimensions: still use sign(W) but these positions matter less
    # The weighting doesn't change the signs — it changes which positions
    # we preserve carefully during the SVD projection step
    
    sign_W = np.sign(W)

    # Weight the sign matrix by crystal dimension importance
    # This makes the SVD projection prioritize crystal-carrying dimensions
    weighted = sign_W * (1.0 + dim_weight[np.newaxis, :])  # emphasize crystal dims

    return weighted


def extract_loom_crystal(teacher: GDModel, d_small: int) -> list[dict[str, np.ndarray]]:
    """Extract crystal from teacher using loom-read weighting.
    
    For each layer:
    1. CCA between K and FFN → angle bands
    2. Loom-weight sign(W) to emphasize crystal-carrying dimensions
    3. SVD project to d_small
    4. sign() the projected result
    """
    crystal = []
    d_big = teacher.d_model

    for layer_idx, layer in enumerate(teacher.layers):
        W_k = np.array(layer.attn.k_proj.weight)  # (d_big, d_big)
        W_ffn = np.array(layer.ffn.weight)          # (d_big, d_big)

        # CCA between K and FFN input spaces
        angles, shared_dirs = cca_angle_bands(W_k, W_ffn)

        layer_signs = {}
        for name, proj in [
            ("k", layer.attn.k_proj),
            ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj),
            ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)  # (d_big, d_big)

            # Loom-weighted sign (emphasize crystal dimensions)
            weighted_sign = loom_weighted_sign(W, angles, shared_dirs)

            # SVD project to d_small (same as nucleation_exp but on weighted signs)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]  # (d_small, d_big) — projection basis

            # Project the loom-weighted signs
            W_proj = P @ weighted_sign @ P.T  # (d_small, d_small)
            signs = np.sign(W_proj).astype(np.float32)

            # Replace zeros
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42 + layer_idx).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))

            layer_signs[name] = signs

        crystal.append(layer_signs)

    return crystal


def extract_magnitude_template(teacher: GDModel, d_small: int) -> list[dict[str, np.ndarray]]:
    """Extract per-dimension magnitude profile (same as nucleation_exp)."""
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
            row_rms = np.sqrt(np.mean(W_small ** 2, axis=1))
            layer_mag[name] = row_rms.astype(np.float32)
        templates.append(layer_mag)
    return templates


def svd_project_crystal(teacher: GDModel, d_small: int) -> list[dict[str, np.ndarray]]:
    """Naive SVD projection + sign (baseline, same as nucleation_exp)."""
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
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
            signs = np.sign(W_small).astype(np.float32)
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


# ══════════════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════════════

def _safe_zero_plate_grads(grads, n_layers):
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
        attn_g = layer_g.get("attn", {})
        for pname in ["k_plate", "v_plate", "o_plate"]:
            plate_g = attn_g.get(pname, {})
            if isinstance(plate_g, dict) and "weight" in plate_g:
                plate_g["weight"] = mx.zeros_like(plate_g["weight"])
        ffn_g = layer_g.get("ffn_plate", {})
        if isinstance(ffn_g, dict) and "weight" in ffn_g:
            ffn_g["weight"] = mx.zeros_like(ffn_g["weight"])


def train_teacher(d_model: int, n_steps: int = 5000) -> GDModel:
    model = GDModel(d_model=d_model, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
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


def train_student(model: HoloModel, condition_name: str, freeze_plates: bool = True) -> dict:
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

    trajectory = []
    step_losses = []

    for step in range(N_STEPS):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
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
            recent_loss = float(np.mean(step_losses[-EVAL_INTERVAL:]))

            checkpoint = {
                "step": step + 1,
                "loss": ev["loss"],
                "accuracy": ev["accuracy"],
                "recent_train_loss": recent_loss,
            }
            trajectory.append(checkpoint)

            log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    return {
        "condition": condition_name,
        "trajectory": trajectory,
        "final_loss": trajectory[-1]["loss"],
        "final_accuracy": trajectory[-1]["accuracy"],
        "best_accuracy": max(t["accuracy"] for t in trajectory),
        "best_loss": min(t["loss"] for t in trajectory),
    }


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # ── Train teachers ──
    log("═" * 60)
    log("Training teachers...")
    log("═" * 60)

    log("\nTeacher d=256...")
    teacher_big = train_teacher(D_TEACHER, n_steps=5000)

    log("\nTeacher d=128...")
    teacher_small = train_teacher(D_STUDENT, n_steps=5000)

    # ── Extract crystals ──
    log("\n" + "═" * 60)
    log("Extracting crystals...")

    oracle_crystal = extract_crystal(teacher_small)
    svd_crystal = svd_project_crystal(teacher_big, D_STUDENT)
    loom_crystal = extract_loom_crystal(teacher_big, D_STUDENT)
    mag_template = extract_magnitude_template(teacher_big, D_STUDENT)

    # How different is loom_crystal from svd_crystal?
    for i in range(N_LAYERS):
        for key in ["k", "v", "o", "ffn"]:
            agree = np.mean(loom_crystal[i][key] == svd_crystal[i][key])
            log(f"  Layer {i} {key}: loom↔svd sign agreement = {agree:.4f}")

    # ── Condition 1: RANDOM ──
    log("\n" + "═" * 60)
    log("CONDITION 1: RANDOM")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    results["random"] = train_student(model, "RANDOM")

    # ── Condition 2: ORACLE ──
    log("\n" + "═" * 60)
    log("CONDITION 2: ORACLE")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, oracle_crystal)
    mx.eval(model.parameters())
    results["oracle"] = train_student(model, "ORACLE")

    # ── Condition 3: SVD_SIGN ──
    log("\n" + "═" * 60)
    log("CONDITION 3: SVD_SIGN (naive projection)")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, svd_crystal)
    mx.eval(model.parameters())
    results["svd_sign"] = train_student(model, "SVD_SIGN")

    # ── Condition 4: MAGNITUDE ──
    log("\n" + "═" * 60)
    log("CONDITION 4: MAGNITUDE (random signs + teacher magnitudes)")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])
    mx.eval(model.parameters())
    results["magnitude"] = train_student(model, "MAGNITUDE")

    # ── Condition 5: LOOM_READ ──
    log("\n" + "═" * 60)
    log("CONDITION 5: LOOM_READ (loom-weighted sign extraction)")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, loom_crystal)
    mx.eval(model.parameters())
    results["loom_read"] = train_student(model, "LOOM_READ")

    # ── Condition 6: LOOM_MAG ──
    log("\n" + "═" * 60)
    log("CONDITION 6: LOOM_MAG (loom signs + teacher magnitudes)")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, loom_crystal)
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])
    mx.eval(model.parameters())
    results["loom_mag"] = train_student(model, "LOOM_MAG")

    # ── Summary ──
    elapsed = time.time() - t_start

    log(f"\n{'═'*60}")
    log("SUMMARY")
    log(f"{'═'*60}\n")

    conds = ["random", "oracle", "svd_sign", "magnitude", "loom_read", "loom_mag"]
    log(f"  {'Condition':<16s} {'Best Acc':>8s} {'Final Acc':>9s} {'Best Loss':>9s}")
    log(f"  {'-'*16} {'-'*8} {'-'*9} {'-'*9}")
    for name in conds:
        r = results[name]
        log(f"  {name:<16s} {r['best_accuracy']:8.4f} {r['final_accuracy']:9.4f} "
            f"{r['best_loss']:9.4f}")

    log(f"\n  Learning curves (accuracy):")
    log(f"  {'Step':>6s}  " + "  ".join(f"{n:>9s}" for n in conds))
    log(f"  {'-'*6}  " + "  ".join("-"*9 for _ in conds))

    max_pts = min(len(results[c]["trajectory"]) for c in conds)
    for i in range(min(max_pts, 15)):
        step = results[conds[0]]["trajectory"][i]["step"]
        accs = [results[c]["trajectory"][i]["accuracy"] for c in conds]
        best = max(accs)
        row = f"  {step:6d}  "
        for a in accs:
            marker = "★" if a == best else " "
            row += f" {a:8.4f}{marker}"
        log(row)

    results["meta"] = {
        "d_teacher": D_TEACHER, "d_student": D_STUDENT,
        "n_layers": N_LAYERS, "n_steps": N_STEPS,
        "elapsed_seconds": elapsed,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Results saved to {out_path}")
    log(f"  Total time: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
