"""Loom Crystal Sharpening — Does the delta loop sharpen both hologram AND crystal?

Session 124, experiment 8. The sign-flip loop sharpens the hologram
(sign corrections converge, accuracy climbs). But is the CRYSTAL
also sharpening? The crystal is the relational geometry — the 4×4
combinator cosine matrix from the student's internal representations.

Protocol:
  1. Generate per-combinator probe sets (K, I, B, C pure expressions)
  2. Extract reference crystal from teacher
  3. For each round of delta sign-flip:
     a. Train student
     b. Run probes through student, extract hidden states per layer
     c. Compute 4×4 combinator cosine matrix per layer
     d. Measure RDM correlation with teacher crystal (crystal agreement)
     e. Extract delta, flip signs, continue

If crystal agreement improves → hologram AND crystal sharpen together.
If accuracy improves but crystal degrades → routing shortcut, won't generalize.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_crystal_sharpen_exp.py

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
    TernaryLinear, Comb, Var, App,
    GDModel, HoloModel,
    count_holo_params,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-crystal-sharpen"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
N_ROUNDS = 5
FLIP_FRAC = 0.1  # sweet spot from previous experiment
ALPHA = 0.3
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4

COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Crystal probes — pure combinator expressions
# ══════════════════════════════════════════════════════════════════════

def generate_combinator_probes(n_per_comb=20, seed=42):
    """Generate pure combinator probe expressions.
    
    For each combinator, generate n_per_comb reduction examples.
    Returns: {comb_name: [(input_ids, target_ids), ...]}
    """
    rng = np.random.RandomState(seed)
    vars_pool = ["a", "b", "c", "d", "e", "x", "y", "z"]
    fvars_pool = ["f", "g", "h"]

    probes = {}
    for comb in COMBINATORS:
        comb_probes = []
        for _ in range(n_per_comb * 3):  # generate extra, filter
            if len(comb_probes) >= n_per_comb:
                break

            v1 = Var(rng.choice(vars_pool))
            v2 = Var(rng.choice(vars_pool))
            fv1 = Var(rng.choice(fvars_pool))
            fv2 = Var(rng.choice(fvars_pool))

            if comb == "K":
                expr = App(App(Comb("K"), v1), v2)
            elif comb == "I":
                expr = App(Comb("I"), v1)
            elif comb == "B":
                expr = App(App(App(Comb("B"), fv1), fv2), v1)
            elif comb == "C":
                expr = App(App(App(Comb("C"), fv1), v1), v2)

            reduced = full_reduce(expr)
            inp_toks = expr.to_tokens()
            out_toks = reduced.to_tokens()

            if not all(t in TOK2ID for t in inp_toks): continue
            if not all(t in TOK2ID for t in out_toks): continue

            full_input = ["<bos>"] + inp_toks + ["="]
            ids = [TOK2ID[t] for t in full_input]

            # Pad to fixed length
            max_len = 20
            ids = ids[:max_len] + [PAD_ID] * max(0, max_len - len(ids))
            comb_probes.append(ids)

        probes[comb] = comb_probes[:n_per_comb]

    return probes


def extract_crystal_geometry(model, probes, is_gd=False):
    """Run probes through model, extract 4×4 combinator cosine matrix per layer.
    
    Returns: {
        'per_layer': [4×4 cosine matrix per layer],
        'output': 4×4 cosine matrix at output,
        'mean_hidden': mean hidden state per combinator per layer,
    }
    """
    n_layers = len(model.layers)

    # Hook all layers
    layer_captures = {i: [] for i in range(n_layers)}
    hooks = []

    for li in range(n_layers):
        def make_hook(layer_idx):
            def hook_fn(module, args):
                # MLX uses __call__ not forward hooks, so we intercept differently
                pass
            return hook_fn

    # For MLX models, we need to run probes and capture intermediate states
    # by modifying the forward pass temporarily
    comb_hidden = {c: {li: [] for li in range(n_layers)} for c in COMBINATORS}
    comb_output = {c: [] for c in COMBINATORS}

    for comb_name in COMBINATORS:
        for ids in probes[comb_name]:
            input_ids = mx.array(np.array([ids], dtype=np.int32))

            # Manual forward pass to capture intermediate states
            x = model.embed(input_ids)
            for li, layer in enumerate(model.layers):
                x = layer(x)
                # Capture last token hidden state after this layer
                h = np.array(x[0, -1, :])  # (d_model,)
                comb_hidden[comb_name][li].append(h)

            # Output representation
            out = model.output_norm(x)
            comb_output[comb_name].append(np.array(out[0, -1, :]))

    # Compute per-layer 4×4 cosine matrices
    per_layer_crystals = []
    for li in range(n_layers):
        # Mean hidden state per combinator
        means = []
        for c in COMBINATORS:
            mean_h = np.mean(comb_hidden[c][li], axis=0)
            means.append(mean_h)
        means = np.array(means)  # (4, d_model)

        # Cosine matrix
        norms = np.maximum(np.linalg.norm(means, axis=1, keepdims=True), 1e-8)
        means_n = means / norms
        cos_mat = means_n @ means_n.T  # (4, 4)
        per_layer_crystals.append(cos_mat.tolist())

    # Output cosine matrix
    out_means = []
    for c in COMBINATORS:
        out_means.append(np.mean(comb_output[c], axis=0))
    out_means = np.array(out_means)
    norms = np.maximum(np.linalg.norm(out_means, axis=1, keepdims=True), 1e-8)
    out_means_n = out_means / norms
    output_crystal = (out_means_n @ out_means_n.T).tolist()

    return {
        "per_layer": per_layer_crystals,
        "output": output_crystal,
    }


def crystal_agreement(student_crystal, teacher_crystal):
    """RDM correlation between two 4×4 cosine matrices."""
    A = np.array(student_crystal)
    B = np.array(teacher_crystal)
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def crystal_summary(crystal_data, teacher_data):
    """Compute per-layer and output crystal agreement."""
    agreements = []
    for li in range(len(crystal_data["per_layer"])):
        agr = crystal_agreement(
            crystal_data["per_layer"][li],
            teacher_data["per_layer"][li])
        agreements.append(agr)

    out_agr = crystal_agreement(crystal_data["output"], teacher_data["output"])

    return {
        "per_layer": agreements,
        "mean_layer": float(np.mean(agreements)),
        "output": out_agr,
    }


# ══════════════════════════════════════════════════════════════════════
# Extraction functions (reused from previous experiments)
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(W_a, W_b, k=None):
    d_in = W_a.shape[1]
    if k is None: k = min(d_in, min(W_a.shape[0], W_b.shape[0]))
    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)
    k = min(k, Vt_a.shape[0], Vt_b.shape[0])
    A, B = Vt_a[:k, :].T, Vt_b[:k, :].T
    Qa, _ = np.linalg.qr(A); Qb, _ = np.linalg.qr(B)
    U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
    d_a, d_b = Qa @ U, Qb @ Vt.T
    shared = d_a + d_b
    return angles, shared / np.maximum(np.linalg.norm(shared, axis=0, keepdims=True), 1e-8)


def loom_weighted_sign(W, angles, shared):
    mask = (angles >= 35) & (angles < 72)
    if mask.sum() < 2: return np.sign(W)
    dim_e = np.sum(shared[:, mask] ** 2, axis=1)
    return np.sign(W) * (1.0 + dim_e / (dim_e.max() + 1e-10))[np.newaxis, :]


def extract_loom_crystal(teacher, d_small):
    crystal = []
    for li, layer in enumerate(teacher.layers):
        W_k, W_f = np.array(layer.attn.k_proj.weight), np.array(layer.ffn.weight)
        angles, shared = cca_angle_bands(W_k, W_f)
        ls = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            wt = loom_weighted_sign(W, angles, shared)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            signs = np.sign(P @ wt @ P.T).astype(np.float32)
            z = signs == 0
            if z.any(): signs[z] = np.random.RandomState(42+li).choice([-1.,1.], size=int(z.sum()))
            ls[name] = signs
        crystal.append(ls)
    return crystal


def extract_mag(teacher, d_small):
    t = []
    for layer in teacher.layers:
        lm = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            lm[name] = np.sqrt(np.mean((P @ W @ P.T) ** 2, axis=1)).astype(np.float32)
        t.append(lm)
    return t


def extract_teacher_signs(teacher, d_small):
    t = []
    for layer in teacher.layers:
        ls = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small, :]
            ls[name] = np.sign(P @ W @ P.T).astype(np.float32)
        t.append(ls)
    return t


def extract_beams(model):
    return [{"k": np.array(l.attn.k_scale), "v": np.array(l.attn.v_scale),
             "o": np.array(l.attn.o_scale), "ffn": np.array(l.ffn_scale)}
            for l in model.layers]


def compute_delta(beams, mag):
    return [{k: beams[i][k] - mag[i][k] for k in ["k","v","o","ffn"]}
            for i in range(len(beams))]


def delta_sign_flip(crystal, teacher_signs, delta, flip_frac):
    new_crystal, total_flipped, total_pos = [], 0, 0
    for li in range(len(crystal)):
        ls = {}
        for key in ["k","v","o","ffn"]:
            cur = crystal[li][key].copy()
            truth = teacher_signs[li][key]
            d = delta[li][key]
            n_flip = max(1, int(flip_frac * len(d)))
            rows = np.argsort(np.abs(d))[-n_flip:]
            for row in rows:
                dis = (cur[row] != truth[row]) & (cur[row] != 0) & (truth[row] != 0)
                cur[row][dis] = truth[row][dis]
                total_flipped += int(dis.sum())
            total_pos += cur.size
            ls[key] = cur
        new_crystal.append(ls)
    return new_crystal, total_flipped, total_pos


def refocus_mag(initial, delta, alpha):
    return [{k: np.maximum(initial[i][k] + alpha * delta[i][k], 0.01).astype(np.float32)
             for k in ["k","v","o","ffn"]} for i in range(len(initial))]


def sign_diff(a, b):
    t, c = 0, 0
    for i in range(len(a)):
        for k in ["k","v","o","ffn"]:
            t += a[i][k].size; c += int(np.sum(a[i][k] != b[i][k]))
    return c / t if t > 0 else 0


# ══════════════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════════════

def _zero_plates(grads, n):
    for i in range(n):
        lg = grads.get("layers", {})
        if isinstance(lg, list):
            if i >= len(lg): continue
            g = lg[i]
        elif isinstance(lg, dict): g = lg.get(i, lg.get(str(i), {}))
        else: continue
        if not isinstance(g, dict): continue
        for p in ["k_plate","v_plate","o_plate"]:
            pg = g.get("attn",{}).get(p,{})
            if isinstance(pg,dict) and "weight" in pg: pg["weight"] = mx.zeros_like(pg["weight"])
        fg = g.get("ffn_plate",{})
        if isinstance(fg,dict) and "weight" in fg: fg["weight"] = mx.zeros_like(fg["weight"])


def train_teacher_model(d, n_steps=5000):
    m = GDModel(d_model=d, n_layers=N_LAYERS); mx.eval(m.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m)); mx.eval(m.parameters())
        del lv, gr
        if (s+1)%100==0: mx.clear_cache()
        if (s+1)%1000==0:
            ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    return m


def train_student_model(model, name, n_steps=N_STEPS):
    mx.eval(model.parameters())
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)
    traj = []
    for s in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
        _zero_plates(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model)); mx.eval(model.parameters())
        del lv, gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%EVAL_INTERVAL==0:
            ev = eval_model(model, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
            traj.append({"step":s+1, "loss":ev["loss"], "accuracy":ev["accuracy"]})
            if (s+1)%500==0:
                log(f"    Step {s+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    return {"condition":name, "trajectory":traj,
            "final_accuracy":traj[-1]["accuracy"],
            "best_accuracy":max(t["accuracy"] for t in traj),
            "best_loss":min(t["loss"] for t in traj)}


def make_student(crystal, mag):
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m, crystal)
    for i, l in enumerate(m.layers):
        l.attn.k_scale = mx.array(mag[i]["k"]); l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"]); l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(m.parameters())
    return m


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ── Teacher ──
    log("Training teacher d=256...")
    teacher = train_teacher_model(D_TEACHER, n_steps=5000)

    # ── Probes ──
    log("\nGenerating combinator probes...")
    probes = generate_combinator_probes(n_per_comb=20)
    for c in COMBINATORS:
        log(f"  {c}: {len(probes[c])} probes")

    # ── Teacher crystal (reference) ──
    log("\nExtracting teacher crystal geometry...")
    teacher_crystal_geom = extract_crystal_geometry(teacher, probes, is_gd=True)
    log("  Teacher crystal (output layer):")
    tc = np.array(teacher_crystal_geom["output"])
    for i, c1 in enumerate(COMBINATORS):
        row = f"    {c1}: " + "  ".join(f"{tc[i,j]:+.3f}" for j, c2 in enumerate(COMBINATORS))
        log(row)

    # ── Extractions ──
    log("\nExtracting loom crystal + magnitudes + teacher signs...")
    initial_mag = extract_mag(teacher, D_STUDENT)
    initial_crystal = extract_loom_crystal(teacher, D_STUDENT)
    teacher_signs = extract_teacher_signs(teacher, D_STUDENT)

    # ── Baseline: MAGNITUDE ──
    log("\nBASELINE: MAGNITUDE")
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    for i, l in enumerate(m.layers):
        l.attn.k_scale=mx.array(initial_mag[i]["k"]); l.attn.v_scale=mx.array(initial_mag[i]["v"])
        l.attn.o_scale=mx.array(initial_mag[i]["o"]); l.ffn_scale=mx.array(initial_mag[i]["ffn"])
    mx.eval(m.parameters())
    bl_mag = train_student_model(m, "MAGNITUDE")
    bl_mag_crystal = extract_crystal_geometry(m, probes)
    bl_mag_agr = crystal_summary(bl_mag_crystal, teacher_crystal_geom)
    log(f"  Crystal agreement: per_layer={bl_mag_agr['per_layer']}, output={bl_mag_agr['output']:.4f}")
    del m; mx.clear_cache()

    # ── Sign-flip refinement with crystal tracking ──
    log(f"\n{'═'*60}")
    log(f"CRYSTAL SHARPENING LOOP (flip_frac={FLIP_FRAC})")
    log(f"{'═'*60}")

    rounds = []
    cur_crystal = initial_crystal
    cur_mag = initial_mag

    for r in range(N_ROUNDS):
        log(f"\n  ROUND {r}" + (" (initial)" if r == 0 else ""))

        model = make_student(cur_crystal, cur_mag)
        result = train_student_model(model, f"R{r}")

        # Crystal measurement
        student_crystal_geom = extract_crystal_geometry(model, probes)
        crystal_agr = crystal_summary(student_crystal_geom, teacher_crystal_geom)

        # Delta
        beams = extract_beams(model)
        delta = compute_delta(beams, cur_mag)
        d_vals = np.concatenate([d[k].flatten() for d in delta for k in ["k","v","o","ffn"]])
        d_l2 = float(np.sqrt(np.sum(d_vals**2)))

        # Signs changed from initial
        sc = sign_diff(initial_crystal, cur_crystal)

        log(f"    Acc: best={result['best_accuracy']:.4f}, final={result['final_accuracy']:.4f}")
        log(f"    Crystal: layers={[f'{a:.3f}' for a in crystal_agr['per_layer']]}, "
            f"output={crystal_agr['output']:.4f}, mean={crystal_agr['mean_layer']:.4f}")
        log(f"    Delta L2={d_l2:.2f}, signs_changed={sc*100:.1f}%")

        round_info = {
            **result,
            "crystal_agreement": crystal_agr,
            "crystal_output_matrix": student_crystal_geom["output"],
            "delta_l2": d_l2,
            "sign_change_from_initial": sc,
        }
        rounds.append(round_info)

        # Flip for next round
        if r < N_ROUNDS - 1:
            new_crystal, flipped, total = delta_sign_flip(
                cur_crystal, teacher_signs, delta, FLIP_FRAC)
            cur_mag = refocus_mag(initial_mag, delta, ALPHA)
            cur_crystal = new_crystal
            log(f"    Flipped {flipped} signs ({flipped/total*100:.2f}%)")

        del model; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SUMMARY: Crystal Sharpening")
    log(f"{'═'*60}\n")

    log(f"  {'Round':<8s} {'Best Acc':>8s} {'Crystal':>8s} {'Output':>8s} {'Signs%':>7s} {'δL2':>7s}")
    log(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*7} {'-'*7}")
    log(f"  {'MAG_BL':<8s} {bl_mag['best_accuracy']:8.4f} "
        f"{bl_mag_agr['mean_layer']:8.4f} {bl_mag_agr['output']:8.4f}")

    for i, r in enumerate(rounds):
        ca = r["crystal_agreement"]
        sc = r["sign_change_from_initial"]
        log(f"  {'R'+str(i):<8s} {r['best_accuracy']:8.4f} "
            f"{ca['mean_layer']:8.4f} {ca['output']:8.4f} "
            f"{sc*100:6.1f}% {r['delta_l2']:7.2f}")

    # Crystal convergence
    log(f"\n  Crystal agreement evolution (mean across layers):")
    log(f"    MAG baseline: {bl_mag_agr['mean_layer']:.4f}")
    for i, r in enumerate(rounds):
        ca = r["crystal_agreement"]["mean_layer"]
        bar = "█" * int(max(0, ca) * 40)
        log(f"    Round {i}:      {ca:.4f}  {bar}")

    log(f"\n  Hologram vs Crystal co-evolution:")
    log(f"    {'Round':<8s} {'Accuracy':>10s} {'Crystal':>10s} {'Both↑?':>8s}")
    for i in range(1, len(rounds)):
        acc_delta = rounds[i]["best_accuracy"] - rounds[i-1]["best_accuracy"]
        crys_delta = (rounds[i]["crystal_agreement"]["mean_layer"] -
                      rounds[i-1]["crystal_agreement"]["mean_layer"])
        both_up = "✓" if acc_delta > 0 and crys_delta > 0 else "✗"
        log(f"    R{i-1}→R{i}   {acc_delta:+10.4f} {crys_delta:+10.4f} {both_up:>8s}")

    # Save
    results = {
        "baseline_magnitude": {**bl_mag, "crystal": bl_mag_agr},
        "rounds": rounds,
        "teacher_crystal": teacher_crystal_geom,
        "config": {"d_teacher":D_TEACHER, "d_student":D_STUDENT,
                    "n_layers":N_LAYERS, "n_steps":N_STEPS,
                    "n_rounds":N_ROUNDS, "flip_frac":FLIP_FRAC},
        "elapsed_seconds": time.time() - t0,
    }
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
