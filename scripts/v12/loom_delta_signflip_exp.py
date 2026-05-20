"""Loom Delta Sign-Flip — Delta gradient drives sign corrections, not just magnitude.

Session 124, experiment 7. The previous delta refinement only tuned
magnitudes (0% sign change). This version uses the delta to identify
WHICH plate rows need correction, then flips signs at those rows
to match the teacher's projected weight signs.

The logic:
  - delta[i] large → GD had to compensate hard at output dim i
  - The plate row i probably has wrong signs
  - Teacher's SVD-projected weight signs are the "ground truth"
  - Flip plate signs at high-delta rows to match teacher
  - This is a TARGETED oracle correction: delta tells us WHERE to apply it

Rounds:
  Round 0: LOOM_MAG baseline (no flips)
  Round 1+: train → extract delta → flip top-k% rows → retrain

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_delta_signflip_exp.py

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


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-delta-signflip"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
N_ROUNDS = 5
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4

# Fraction of rows to flip per round (sweep: try different fractions)
FLIP_FRACS = [0.1, 0.2, 0.3]


# ══════════════════════════════════════════════════════════════════════
# Extraction (reused)
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(W_a, W_b, k=None):
    d_in = W_a.shape[1]
    if k is None:
        k = min(d_in, min(W_a.shape[0], W_b.shape[0]))
    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)
    k = min(k, Vt_a.shape[0], Vt_b.shape[0])
    A, B = Vt_a[:k, :].T, Vt_b[:k, :].T
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
    dirs_a, dirs_b = Qa @ U, Qb @ Vt.T
    shared = dirs_a + dirs_b
    norms = np.linalg.norm(shared, axis=0, keepdims=True)
    return angles, shared / np.maximum(norms, 1e-8)


def loom_weighted_sign(W, angles, shared_dirs):
    crystal_mask = (angles >= 35) & (angles < 72)
    if crystal_mask.sum() < 2:
        return np.sign(W)
    crystal_dirs = shared_dirs[:, crystal_mask]
    dim_energy = np.sum(crystal_dirs ** 2, axis=1)
    dim_weight = dim_energy / (dim_energy.max() + 1e-10)
    return np.sign(W) * (1.0 + dim_weight[np.newaxis, :])


def extract_loom_crystal(teacher, d_small):
    crystal = []
    for li, layer in enumerate(teacher.layers):
        W_k = np.array(layer.attn.k_proj.weight)
        W_ffn = np.array(layer.ffn.weight)
        angles, shared = cca_angle_bands(W_k, W_ffn)
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            weighted = loom_weighted_sign(W, angles, shared)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            signs = np.sign(P @ weighted @ P.T).astype(np.float32)
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42 + li).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


def extract_magnitude_template(teacher, d_small):
    templates = []
    for layer in teacher.layers:
        layer_mag = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            W_small = P @ W @ P.T
            layer_mag[name] = np.sqrt(np.mean(W_small ** 2, axis=1)).astype(np.float32)
        templates.append(layer_mag)
    return templates


def extract_teacher_projected_signs(teacher, d_small):
    """Extract sign(SVD_project(W)) — the teacher's 'ground truth' signs."""
    truth = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            signs = np.sign(P @ W @ P.T).astype(np.float32)
            layer_signs[name] = signs
        truth.append(layer_signs)
    return truth


# ══════════════════════════════════════════════════════════════════════
# Delta sign flipping
# ══════════════════════════════════════════════════════════════════════

def extract_trained_beams(model):
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
    deltas = []
    for i in range(len(trained_beams)):
        layer_delta = {}
        for key in ["k", "v", "o", "ffn"]:
            layer_delta[key] = trained_beams[i][key] - initial_mag[i][key]
        deltas.append(layer_delta)
    return deltas


def delta_sign_flip(crystal, teacher_signs, delta, flip_frac):
    """Flip signs at high-delta rows to match teacher's projected signs.
    
    For each plate:
      1. Find rows where |delta| is in top flip_frac
      2. At those rows: flip signs that disagree with teacher
      3. Leave other rows untouched
    
    Returns: (new_crystal, stats)
    """
    new_crystal = []
    total_flipped = 0
    total_positions = 0
    total_candidates = 0

    for li in range(len(crystal)):
        layer_signs = {}
        for key in ["k", "v", "o", "ffn"]:
            current = crystal[li][key].copy()
            truth = teacher_signs[li][key]
            d = delta[li][key]  # (d_out,)

            d_out = len(d)
            n_flip_rows = max(1, int(flip_frac * d_out))
            flip_rows = np.argsort(np.abs(d))[-n_flip_rows:]

            for row in flip_rows:
                # Find positions where current disagrees with teacher
                disagree = (current[row] != truth[row])
                disagree &= (current[row] != 0) & (truth[row] != 0)
                total_candidates += int(disagree.sum())

                # Flip to match teacher at these positions
                current[row][disagree] = truth[row][disagree]
                total_flipped += int(disagree.sum())

            total_positions += current.size
            layer_signs[key] = current
        new_crystal.append(layer_signs)

    return new_crystal, {
        "total_flipped": total_flipped,
        "total_positions": total_positions,
        "flip_rate": total_flipped / total_positions if total_positions > 0 else 0,
        "candidates": total_candidates,
    }


def refocus_magnitude(initial_mag, delta, alpha=0.5):
    refocused = []
    for i in range(len(initial_mag)):
        layer_ref = {}
        for key in ["k", "v", "o", "ffn"]:
            ref = initial_mag[i][key] + alpha * delta[i][key]
            layer_ref[key] = np.maximum(ref, 0.01).astype(np.float32)
        refocused.append(layer_ref)
    return refocused


def sign_change_rate(a, b):
    total, changed = 0, 0
    for i in range(len(a)):
        for key in ["k", "v", "o", "ffn"]:
            total += a[i][key].size
            changed += int(np.sum(a[i][key] != b[i][key]))
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
        for pname in ["k_plate", "v_plate", "o_plate"]:
            pg = layer_g.get("attn", {}).get(pname, {})
            if isinstance(pg, dict) and "weight" in pg:
                pg["weight"] = mx.zeros_like(pg["weight"])
        fg = layer_g.get("ffn_plate", {})
        if isinstance(fg, dict) and "weight" in fg:
            fg["weight"] = mx.zeros_like(fg["weight"])


def train_teacher(d_model, n_steps=5000):
    model = GDModel(d_model=d_model, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk)
        mx.eval(lv, gr)
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (step+1) % 100 == 0: mx.clear_cache()
        if (step+1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {step+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev = eval_model(model, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Teacher final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    return model


def train_student(model, name, n_steps=N_STEPS):
    mx.eval(model.parameters())
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)
    traj = []
    for step in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk)
        mx.eval(lv, gr)
        _safe_zero_plate_grads(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (step+1) % 50 == 0: mx.clear_cache()
        if (step+1) % EVAL_INTERVAL == 0:
            ev = eval_model(model, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
            traj.append({"step": step+1, "loss": ev["loss"], "accuracy": ev["accuracy"]})
            if (step+1) % 500 == 0:
                log(f"    Step {step+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    return {
        "condition": name, "trajectory": traj,
        "final_accuracy": traj[-1]["accuracy"],
        "best_accuracy": max(t["accuracy"] for t in traj),
        "best_loss": min(t["loss"] for t in traj),
    }


def make_student(crystal, mag_template):
    model = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(model.parameters())
    write_crystal_to_model(model, crystal)
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])
    mx.eval(model.parameters())
    return model


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("Training teacher d=256...")
    teacher = train_teacher(D_TEACHER, n_steps=5000)

    log("\nExtracting...")
    initial_mag = extract_magnitude_template(teacher, D_STUDENT)
    initial_crystal = extract_loom_crystal(teacher, D_STUDENT)
    teacher_signs = extract_teacher_projected_signs(teacher, D_STUDENT)

    # How much does loom crystal disagree with teacher signs?
    loom_vs_teacher = sign_change_rate(initial_crystal, teacher_signs)
    log(f"  Loom crystal vs teacher signs: {loom_vs_teacher*100:.1f}% disagree")

    # ── Baselines ──
    log("\nBASELINE: RANDOM")
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    bl_random = train_student(m, "RANDOM")

    log("\nBASELINE: MAGNITUDE")
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    for i, layer in enumerate(m.layers):
        layer.attn.k_scale = mx.array(initial_mag[i]["k"])
        layer.attn.v_scale = mx.array(initial_mag[i]["v"])
        layer.attn.o_scale = mx.array(initial_mag[i]["o"])
        layer.ffn_scale = mx.array(initial_mag[i]["ffn"])
    mx.eval(m.parameters())
    bl_mag = train_student(m, "MAGNITUDE")

    # ── Sign-flip refinement loop with flip_frac=0.2 ──
    flip_frac = 0.2
    log(f"\n{'═'*60}")
    log(f"SIGN-FLIP REFINEMENT (flip_frac={flip_frac})")
    log(f"{'═'*60}")

    rounds = []
    current_crystal = initial_crystal
    current_mag = initial_mag

    for r in range(N_ROUNDS):
        log(f"\n  ROUND {r}" + (" (baseline)" if r == 0 else f" (flipped {flip_frac*100:.0f}% rows)"))

        model = make_student(current_crystal, current_mag)
        result = train_student(model, f"R{r}_flip{flip_frac}")

        # Extract delta
        trained_beams = extract_trained_beams(model)
        delta = compute_delta(trained_beams, current_mag)

        # Delta stats
        all_d = np.concatenate([d[k].flatten() for d in delta for k in ["k","v","o","ffn"]])
        d_l2 = float(np.sqrt(np.sum(all_d**2)))

        # Sign change from initial
        sc_from_initial = sign_change_rate(initial_crystal, current_crystal)

        round_info = {
            **result,
            "delta_l2": d_l2,
            "sign_change_from_initial": sc_from_initial,
        }

        log(f"    Best={result['best_accuracy']:.4f}, Final={result['final_accuracy']:.4f}, "
            f"δL2={d_l2:.2f}, signs_changed={sc_from_initial*100:.1f}%")

        # Sign-flip for next round
        if r < N_ROUNDS - 1:
            new_crystal, flip_stats = delta_sign_flip(
                current_crystal, teacher_signs, delta, flip_frac)

            log(f"    Flipped {flip_stats['total_flipped']} signs "
                f"({flip_stats['flip_rate']*100:.2f}% of total)")

            # Also refocus magnitudes
            current_mag = refocus_magnitude(initial_mag, delta, alpha=0.3)
            current_crystal = new_crystal

        rounds.append(round_info)
        del model; mx.clear_cache()

    # ── Also try different flip fractions for round 1 only ──
    log(f"\n{'═'*60}")
    log("FLIP FRACTION SWEEP (single round from baseline)")
    log(f"{'═'*60}")

    sweep_results = {}
    for ff in FLIP_FRACS:
        log(f"\n  flip_frac={ff}")

        # Train round 0
        model = make_student(initial_crystal, initial_mag)
        r0 = train_student(model, f"sweep_r0_ff{ff}")
        trained_beams = extract_trained_beams(model)
        delta = compute_delta(trained_beams, initial_mag)
        del model; mx.clear_cache()

        # Flip and train round 1
        flipped_crystal, flip_stats = delta_sign_flip(
            initial_crystal, teacher_signs, delta, ff)
        refocused_mag = refocus_magnitude(initial_mag, delta, alpha=0.3)

        log(f"    R0: best={r0['best_accuracy']:.4f}, flipped={flip_stats['flip_rate']*100:.2f}%")

        model = make_student(flipped_crystal, refocused_mag)
        r1 = train_student(model, f"sweep_r1_ff{ff}")
        del model; mx.clear_cache()

        improvement = r1["best_accuracy"] - r0["best_accuracy"]
        log(f"    R1: best={r1['best_accuracy']:.4f}, Δ={improvement:+.4f}")

        sweep_results[str(ff)] = {
            "flip_frac": ff,
            "r0": r0, "r1": r1,
            "flip_stats": flip_stats,
            "improvement": improvement,
        }

    # ══════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SUMMARY")
    log(f"{'═'*60}\n")

    log(f"  {'Condition':<20s} {'Best Acc':>8s} {'Final':>8s} {'δL2':>7s} {'Signs%':>7s}")
    log(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*7} {'-'*7}")
    log(f"  {'RANDOM':<20s} {bl_random['best_accuracy']:8.4f} {bl_random['final_accuracy']:8.4f}")
    log(f"  {'MAGNITUDE':<20s} {bl_mag['best_accuracy']:8.4f} {bl_mag['final_accuracy']:8.4f}")

    for i, r in enumerate(rounds):
        sc = r["sign_change_from_initial"]
        log(f"  {'ROUND_'+str(i):<20s} {r['best_accuracy']:8.4f} {r['final_accuracy']:8.4f} "
            f"{r['delta_l2']:7.2f} {sc*100:6.1f}%")

    log(f"\n  FLIP FRACTION SWEEP:")
    log(f"  {'Frac':>6s} {'R0 Best':>8s} {'R1 Best':>8s} {'Δ':>8s} {'Flipped':>8s}")
    log(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for ff_str, sr in sweep_results.items():
        log(f"  {sr['flip_frac']:6.1%} {sr['r0']['best_accuracy']:8.4f} "
            f"{sr['r1']['best_accuracy']:8.4f} {sr['improvement']:+8.4f} "
            f"{sr['flip_stats']['flip_rate']*100:7.2f}%")

    # Save
    results = {
        "baselines": {"random": bl_random, "magnitude": bl_mag},
        "rounds": rounds,
        "sweep": sweep_results,
        "loom_vs_teacher_disagree": loom_vs_teacher,
        "config": {
            "d_teacher": D_TEACHER, "d_student": D_STUDENT,
            "n_layers": N_LAYERS, "n_steps": N_STEPS,
            "n_rounds": N_ROUNDS, "flip_frac": flip_frac,
        },
        "elapsed_seconds": time.time() - t0,
    }
    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Saved to {out_path} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
