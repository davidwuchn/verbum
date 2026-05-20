"""Loom Delta Refinement — Self-distillation loop through the loom.

Session 124, experiment 6. LOOM_MAG hit 0.543 accuracy — beating the
teacher (0.252). The student's trained beams encode routing information
the teacher never had. The delta between initial magnitude template
and trained beam scales is a refinement signal.

Protocol:
  Round 0: baseline LOOM_MAG
    → extract loom crystal + magnitude template from teacher
    → train student, freeze plates
    → extract delta = trained_beams - initial_magnitudes

  Round 1-N: refocused etch
    → refocused_mag = teacher_mag + α·delta (from previous round)
    → re-extract loom-weighted signs with refocused beamformer
    → train new student with re-etched plates + refocused magnitudes
    → extract new delta, iterate

The hypothesis: each round refocuses the beamformer, so the loom-read
extracts better signs, so the student learns better routing, so the
delta is more informative. Convergence = the delta shrinks.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_delta_refine_exp.py

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
    GDModel, HoloModel,
    count_holo_params,
    masked_ce_loss, eval_model,
    generate_batch,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-delta-refine"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
N_ROUNDS = 4  # round 0 = baseline, rounds 1-3 = refinement
ALPHA = 0.5   # refinement learning rate
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4


# ══════════════════════════════════════════════════════════════════════
# Extraction functions (from loom_etch_nucleation_exp.py)
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(W_a, W_b, k=None):
    d_in = W_a.shape[1]
    if k is None:
        k = min(d_in, min(W_a.shape[0], W_b.shape[0]))
    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)
    k = min(k, Vt_a.shape[0], Vt_b.shape[0])
    A = Vt_a[:k, :].T
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


def loom_weighted_sign(W, angles, shared_dirs, mag_emphasis=None):
    """Extract sign(W) weighted by loom structure.
    
    mag_emphasis: optional (d_in,) per-dimension weight to emphasize
    certain dimensions during projection. This is the refocused beamformer.
    """
    d_out, d_in = W.shape
    crystal_mask = (angles >= 35) & (angles < 72)
    if crystal_mask.sum() < 2:
        return np.sign(W)

    crystal_dirs = shared_dirs[:, crystal_mask]
    dim_crystal_energy = np.sum(crystal_dirs ** 2, axis=1)
    dim_weight = dim_crystal_energy / (dim_crystal_energy.max() + 1e-10)

    # Apply refocused beamformer emphasis
    if mag_emphasis is not None:
        # Normalize emphasis to [0, 2] range
        emphasis_norm = mag_emphasis / (mag_emphasis.max() + 1e-10)
        dim_weight = dim_weight * (1.0 + emphasis_norm)

    sign_W = np.sign(W)
    weighted = sign_W * (1.0 + dim_weight[np.newaxis, :])
    return weighted


def extract_loom_crystal(teacher, d_small, mag_emphasis=None):
    """Extract crystal with optional refocused beamformer."""
    crystal = []
    for layer_idx, layer in enumerate(teacher.layers):
        W_k = np.array(layer.attn.k_proj.weight)
        W_ffn = np.array(layer.ffn.weight)
        angles, shared_dirs = cca_angle_bands(W_k, W_ffn)

        layer_signs = {}
        for name, proj in [
            ("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj), ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)

            # Per-layer mag emphasis if provided
            layer_emph = None
            if mag_emphasis is not None:
                layer_emph = mag_emphasis[layer_idx].get(name)

            weighted_sign = loom_weighted_sign(W, angles, shared_dirs, layer_emph)

            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            W_proj = P @ weighted_sign @ P.T
            signs = np.sign(W_proj).astype(np.float32)

            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42 + layer_idx).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


def extract_magnitude_template(teacher, d_small):
    templates = []
    for layer in teacher.layers:
        layer_mag = {}
        for name, proj in [
            ("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
            ("o", layer.attn.o_proj), ("ffn", layer.ffn),
        ]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            W_small = P @ W @ P.T
            row_rms = np.sqrt(np.mean(W_small ** 2, axis=1))
            layer_mag[name] = row_rms.astype(np.float32)
        templates.append(layer_mag)
    return templates


# ══════════════════════════════════════════════════════════════════════
# Delta extraction from trained student
# ══════════════════════════════════════════════════════════════════════

def extract_trained_beams(model: HoloModel) -> list[dict[str, np.ndarray]]:
    """Extract beam scales from a trained HoloModel."""
    beams = []
    for layer in model.layers:
        beams.append({
            "k": np.array(layer.attn.k_scale),
            "v": np.array(layer.attn.v_scale),
            "o": np.array(layer.attn.o_scale),
            "ffn": np.array(layer.ffn_scale),
        })
    return beams


def compute_delta(trained_beams, initial_mag):
    """Compute delta = trained_beams - initial_magnitudes.
    
    Returns per-layer, per-projection delta vectors.
    """
    deltas = []
    for i in range(len(trained_beams)):
        layer_delta = {}
        for key in ["k", "v", "o", "ffn"]:
            delta = trained_beams[i][key] - initial_mag[i][key]
            layer_delta[key] = delta
        deltas.append(layer_delta)
    return deltas


def refocus_magnitude(initial_mag, delta, alpha):
    """Apply delta to refocus the magnitude template.
    
    refocused = initial + alpha * delta
    Then clip to ensure non-negative.
    """
    refocused = []
    for i in range(len(initial_mag)):
        layer_ref = {}
        for key in ["k", "v", "o", "ffn"]:
            ref = initial_mag[i][key] + alpha * delta[i][key]
            ref = np.maximum(ref, 0.01)  # keep positive
            layer_ref[key] = ref.astype(np.float32)
        refocused.append(layer_ref)
    return refocused


def delta_stats(delta):
    """Compute summary statistics of the delta."""
    all_vals = []
    for layer_d in delta:
        for key in ["k", "v", "o", "ffn"]:
            all_vals.append(delta[0][key])
    all_vals = np.concatenate([v.flatten() for v in all_vals])
    return {
        "mean": float(np.mean(all_vals)),
        "std": float(np.std(all_vals)),
        "max": float(np.max(np.abs(all_vals))),
        "l2_norm": float(np.sqrt(np.sum(all_vals ** 2))),
    }


def sign_change_rate(crystal_a, crystal_b):
    """Fraction of sign positions that changed between two crystals."""
    total = 0
    changed = 0
    for i in range(len(crystal_a)):
        for key in ["k", "v", "o", "ffn"]:
            a = crystal_a[i][key]
            b = crystal_b[i][key]
            total += a.size
            changed += int(np.sum(a != b))
    return changed / total if total > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════════════

def _safe_zero_plate_grads(grads, n_layers):
    for i in range(n_layers):
        lg = grads.get("layers", {})
        if isinstance(lg, list):
            if i >= len(lg): continue
            layer_g = lg[i]
        elif isinstance(lg, dict):
            layer_g = lg.get(i, lg.get(str(i), {}))
        else: continue
        if not isinstance(layer_g, dict): continue
        attn_g = layer_g.get("attn", {})
        for pname in ["k_plate", "v_plate", "o_plate"]:
            plate_g = attn_g.get(pname, {})
            if isinstance(plate_g, dict) and "weight" in plate_g:
                plate_g["weight"] = mx.zeros_like(plate_g["weight"])
        ffn_g = layer_g.get("ffn_plate", {})
        if isinstance(ffn_g, dict) and "weight" in ffn_g:
            ffn_g["weight"] = mx.zeros_like(ffn_g["weight"])


def train_teacher(d_model, n_steps=5000):
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
        del loss_val, grads
        if (step + 1) % 100 == 0: mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {step+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    final = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Teacher final: loss={final['loss']:.4f}, acc={final['accuracy']:.4f}")
    return model


def train_student(model, condition_name, n_steps=N_STEPS):
    mx.eval(model.parameters())
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    trajectory = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        _safe_zero_plate_grads(grads, len(model.layers))
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0: mx.clear_cache()
        if (step + 1) % EVAL_INTERVAL == 0:
            ev = eval_model(model, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
            trajectory.append({"step": step + 1, "loss": ev["loss"], "accuracy": ev["accuracy"]})
            if (step + 1) % 500 == 0:
                log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    return {
        "condition": condition_name,
        "trajectory": trajectory,
        "final_accuracy": trajectory[-1]["accuracy"],
        "best_accuracy": max(t["accuracy"] for t in trajectory),
        "best_loss": min(t["loss"] for t in trajectory),
    }


def create_loom_mag_student(loom_crystal, mag_template):
    """Create a student with loom-etched plates + magnitude beam scales."""
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, loom_crystal)
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])
    mx.eval(model.parameters())
    return model


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # ── Train teacher ──
    log("═" * 60)
    log("Training teacher d=256...")
    teacher = train_teacher(D_TEACHER, n_steps=5000)

    # ── Initial extraction ──
    log("\nExtracting initial magnitude template + loom crystal...")
    initial_mag = extract_magnitude_template(teacher, D_STUDENT)
    initial_crystal = extract_loom_crystal(teacher, D_STUDENT)

    # ── Baselines ──
    log("\n" + "═" * 60)
    log("BASELINE: RANDOM")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    baseline_random = train_student(model, "RANDOM")

    log("\nBASELINE: MAGNITUDE (random signs + teacher mag)")
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(initial_mag[i]["k"])
        layer.attn.v_scale = mx.array(initial_mag[i]["v"])
        layer.attn.o_scale = mx.array(initial_mag[i]["o"])
        layer.ffn_scale = mx.array(initial_mag[i]["ffn"])
    mx.eval(model.parameters())
    baseline_mag = train_student(model, "MAGNITUDE")

    # ── Refinement loop ──
    rounds = []
    current_mag = initial_mag
    current_crystal = initial_crystal
    prev_crystal = None

    for round_idx in range(N_ROUNDS):
        log(f"\n{'═'*60}")
        log(f"ROUND {round_idx}: LOOM_MAG" +
            (f" + delta refine (α={ALPHA})" if round_idx > 0 else " (baseline)"))
        log(f"{'═'*60}")

        # Create and train student
        model = create_loom_mag_student(current_crystal, current_mag)
        result = train_student(model, f"ROUND_{round_idx}")

        # Extract delta
        trained_beams = extract_trained_beams(model)
        delta = compute_delta(trained_beams, current_mag)
        d_stats = delta_stats(delta)

        # Sign change from previous round
        sign_change = 0.0
        if prev_crystal is not None:
            sign_change = sign_change_rate(prev_crystal, current_crystal)

        round_info = {
            **result,
            "delta_stats": d_stats,
            "sign_change_from_prev": sign_change,
        }
        rounds.append(round_info)

        log(f"  Best acc: {result['best_accuracy']:.4f}, "
            f"Final acc: {result['final_accuracy']:.4f}")
        log(f"  Delta: mean={d_stats['mean']:.4f}, std={d_stats['std']:.4f}, "
            f"L2={d_stats['l2_norm']:.4f}, max={d_stats['max']:.4f}")
        if sign_change > 0:
            log(f"  Signs changed from prev round: {sign_change:.4f} ({sign_change*100:.1f}%)")

        # Refocus for next round
        if round_idx < N_ROUNDS - 1:
            prev_crystal = current_crystal
            current_mag = refocus_magnitude(initial_mag, delta, ALPHA)

            # Re-extract signs with refocused beamformer emphasis
            # The emphasis comes from the delta — dimensions where GD moved
            # the beams most are the ones to emphasize in the next extraction
            mag_emphasis = []
            for layer_d in delta:
                layer_emph = {}
                for key in ["k", "v", "o", "ffn"]:
                    # Use abs(delta) as emphasis — large deltas mean
                    # these dimensions needed adjustment
                    emph = np.abs(layer_d[key])
                    layer_emph[key] = emph
                mag_emphasis.append(layer_emph)

            current_crystal = extract_loom_crystal(
                teacher, D_STUDENT, mag_emphasis=mag_emphasis)

            new_sign_change = sign_change_rate(prev_crystal, current_crystal)
            log(f"  Re-etched: {new_sign_change*100:.1f}% signs changed")

        del model
        mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SUMMARY: Delta Refinement Loop")
    log(f"{'═'*60}\n")

    log(f"  {'Condition':<20s} {'Best Acc':>8s} {'Final Acc':>9s} {'Delta L2':>8s} {'Sign Δ':>7s}")
    log(f"  {'-'*20} {'-'*8} {'-'*9} {'-'*8} {'-'*7}")
    log(f"  {'RANDOM':<20s} {baseline_random['best_accuracy']:8.4f} "
        f"{baseline_random['final_accuracy']:9.4f}        -       -")
    log(f"  {'MAGNITUDE':<20s} {baseline_mag['best_accuracy']:8.4f} "
        f"{baseline_mag['final_accuracy']:9.4f}        -       -")

    for i, r in enumerate(rounds):
        ds = r["delta_stats"]
        sc = r["sign_change_from_prev"]
        sc_str = f"{sc*100:5.1f}%" if sc > 0 else "    -"
        log(f"  {'ROUND_'+str(i):<20s} {r['best_accuracy']:8.4f} "
            f"{r['final_accuracy']:9.4f} {ds['l2_norm']:8.4f} {sc_str}")

    # Learning curves comparison
    log(f"\n  Learning curves (best of each round):")
    all_conds = [("RANDOM", baseline_random), ("MAGNITUDE", baseline_mag)]
    all_conds += [(f"ROUND_{i}", r) for i, r in enumerate(rounds)]

    log(f"  {'Step':>6s}  " + "  ".join(f"{name:>9s}" for name, _ in all_conds))
    log(f"  {'-'*6}  " + "  ".join("-"*9 for _ in all_conds))

    max_pts = min(len(c["trajectory"]) for _, c in all_conds)
    for i in range(min(max_pts, 10)):
        step = all_conds[0][1]["trajectory"][i]["step"]
        accs = [c["trajectory"][i]["accuracy"] for _, c in all_conds]
        best = max(accs)
        row = f"  {step:6d}  "
        for a in accs:
            marker = "★" if a == best else " "
            row += f" {a:8.4f}{marker}"
        log(row)

    # Convergence: is the delta shrinking?
    log(f"\n  Delta convergence:")
    for i, r in enumerate(rounds):
        ds = r["delta_stats"]
        bar = "█" * int(ds["l2_norm"] * 10)
        log(f"    Round {i}: L2={ds['l2_norm']:.4f}  {bar}")

    # Save
    results = {
        "baselines": {
            "random": baseline_random,
            "magnitude": baseline_mag,
        },
        "rounds": rounds,
        "config": {
            "d_teacher": D_TEACHER, "d_student": D_STUDENT,
            "n_layers": N_LAYERS, "n_steps": N_STEPS,
            "n_rounds": N_ROUNDS, "alpha": ALPHA,
        },
        "elapsed_seconds": time.time() - t_start,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Results saved to {out_path}")
    log(f"  Total time: {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
