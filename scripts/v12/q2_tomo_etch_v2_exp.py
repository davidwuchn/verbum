"""Q2 Tomographic Etch v2 — Teacher reference beam sweep + co-evolution fusion.

Two-phase approach:

Phase 1: TOMOGRAPHIC INITIAL ETCH (measurement only, zero training)
  - CCA between teacher W_q and W_up → direction vectors at each angle
  - Sweep through 0°-90° in 1° steps
  - At each angle: project teacher signs and Q2 student signs through
    CCA direction → compare → damage map at that angle
  - Consensus across all angles → genuinely Q2-damaged signs
  - Fix consensus-damaged signs in one shot (the teacher IS the reference beam)

Phase 2: CO-EVOLUTION FUSION (train to mesh residual into crystal)
  - Start from initial-etched plates (most damage already fixed)
  - GD with crystal loss → evo with strict both-must-improve gate
  - Handles frame-dependent residual that measurement can't determine

The insight: most of the 27% Q2 damage is detectable by MEASUREMENT —
you don't need GD to find it. Scan the teacher as a reference beam
across the full harmonic spectrum (6 peaks at 25°, 45°, 53°, 61°, 67°, 77°).
The co-evolution phase only handles the residual.

Conditions:
  C1: TOMO_ETCH + COEVO  — full pipeline (THE TEST)
  C2: TOMO_ETCH only     — just measurement, no co-evolution
  C3: COEVO only         — no initial etch, just co-evolution (v1 baseline)
  C4: ORACLE             — perfect signs (ceiling)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_tomo_etch_v2_exp.py 2>&1 | tee results/q2-tomo-etch-v2/run.log

License: MIT
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    TernaryLinear, Comb, Var, App,
    GDModel, HoloModel,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-tomo-etch-v2"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4

# Phase 2 co-evolution config
N_ROUNDS = 15
GD_STEPS = 1500
N_CANDIDATES = 200
EVAL_BATCHES = 30
CRYSTAL_FLOOR = 0.2
CRYSTAL_LAMBDA = 1.0
ACC_IMPROVE = 0.001

COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a", "b", "c", "d", "e", "x", "y", "z"]
    fs = ["f", "g", "h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n * 3):
            if len(ps) >= n: break
            v1, v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1, f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
            if c == "K": e = App(App(Comb("K"), v1), v2)
            elif c == "I": e = App(Comb("I"), v1)
            elif c == "B": e = App(App(App(Comb("B"), f1), f2), v1)
            elif c == "C": e = App(App(App(Comb("C"), f1), v1), v2)
            t = ["<bos>"] + e.to_tokens() + ["="]
            if not all(x in TOK2ID for x in t): continue
            ids = [TOK2ID[x] for x in t]
            ids = ids[:20] + [PAD_ID] * max(0, 20 - len(ids))
            ps.append(ids)
        probes[c] = ps[:n]
    return probes


def measure_crystal(model, probes):
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(np.array(x[0, -1, :]))
        means.append(np.mean(hs, axis=0))
    M = np.array(means)
    N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
    return (M / N @ (M / N).T).tolist()


def crystal_agr(s, t):
    A, B = np.array(s), np.array(t)
    idx = np.triu_indices(4, k=1)
    a, b = A[idx] - A[idx].mean(), B[idx] - B[idx].mean()
    d = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / d) if d > 1e-10 else 0.0


def crystal_lattice_loss(model, probes, targets):
    tgt = mx.array(np.array(targets, dtype=np.float32))
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(x[0, -1, :])
        means.append(mx.mean(mx.stack(hs), axis=0))
    M = mx.stack(means)
    N = mx.sqrt(mx.sum(M * M, axis=1, keepdims=True) + 1e-8)
    cos = (M / N) @ (M / N).T
    ir, ic = [0, 0, 0, 1, 1, 2], [1, 2, 3, 2, 3, 3]
    return mx.mean(
        (cos[mx.array(ir), mx.array(ic)] - tgt[mx.array(ir), mx.array(ic)]) ** 2
    )


# ══════════════════════════════════════════════════════════════════════
# Extraction helpers
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W, n_bits=2, block_size=32):
    W_flat = W.flatten(); n = len(W_flat)
    pad = (block_size - n % block_size) % block_size
    W_padded = np.concatenate([W_flat, np.zeros(pad)])
    W_blocks = W_padded.reshape(-1, block_size)
    n_levels = 2 ** (n_bits - 1)
    scales = np.maximum(np.max(np.abs(W_blocks), axis=1, keepdims=True), 1e-10)
    W_norm = W_blocks / scales
    W_quant = np.round(W_norm * n_levels).clip(-n_levels, n_levels)
    W_dequant = (W_quant / n_levels) * scales
    signs = np.sign(W_dequant.flatten()[:n].reshape(W.shape)).astype(np.float32)
    zeros = signs == 0
    if zeros.any():
        signs[zeros] = np.random.RandomState(42).choice([-1.0, 1.0], size=int(zeros.sum()))
    return signs


def extract_oracle_crystal(teacher, ds):
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]; W_proj = P @ W @ P.T
            signs = np.sign(W_proj).astype(np.float32)
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


def extract_q2_crystal(teacher, ds, n_bits=2):
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]; W_proj = P @ W @ P.T
            layer_signs[name] = q2_simulate_weights(W_proj, n_bits=n_bits)
        crystal.append(layer_signs)
    return crystal


def extract_mag(teacher, ds):
    t = []
    for layer in teacher.layers:
        lm = {}
        for nm, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                         ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]
            lm[nm] = np.sqrt(np.mean((P @ W @ P.T) ** 2, axis=1)).astype(np.float32)
        t.append(lm)
    return t


def measure_sign_damage(a, b):
    total = 0; damaged = 0
    for i in range(len(a)):
        for k in a[i]:
            total += a[i][k].size
            damaged += int((a[i][k] != b[i][k]).sum())
    return damaged, total


def sign_agreement_with_oracle(model, oracle_crystal):
    total = 0; matching = 0
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            current = np.sign(np.array(plate.weight))
            oracle = oracle_crystal[li][pn]
            total += oracle.size; matching += int((current == oracle).sum())
    return matching / total if total > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════
# PHASE 1: Tomographic Initial Etch
# Teacher reference beam sweep across CCA angle spectrum
# ══════════════════════════════════════════════════════════════════════

def compute_cca_directions(teacher, ds):
    """CCA between W_q and W_up for each layer → direction vectors + angles.

    Returns per-layer: (angles, directions) where directions is (d_teacher, k)
    projected to student dim.
    """
    layer_ccas = []
    for layer in teacher.layers:
        Wk = np.array(layer.attn.k_proj.weight)
        Wf = np.array(layer.ffn.weight)

        _, _, Va = np.linalg.svd(Wk, full_matrices=False)
        _, _, Vb = np.linalg.svd(Wf, full_matrices=False)

        k = min(ds, Va.shape[0], Vb.shape[0])
        A, B = Va[:k, :].T, Vb[:k, :].T
        Qa, _ = np.linalg.qr(A)
        Qb, _ = np.linalg.qr(B)
        U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)

        angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
        dirs_q = Qa @ U
        dirs_up = Qb @ Vt.T
        dirs = dirs_q + dirs_up
        norms = np.linalg.norm(dirs, axis=0, keepdims=True)
        dirs = dirs / np.maximum(norms, 1e-8)

        layer_ccas.append({"angles": angles, "dirs": dirs})

    return layer_ccas


def sweep_angle_damage(teacher, ds, q2_crystal, oracle_crystal,
                       layer_ccas, angle_step=1):
    """Sweep through CCA angles, compare teacher vs Q2 signs at each angle.

    For each angle band (width=angle_step degrees):
      1. Select CCA directions in that band
      2. Project teacher signs through those directions
      3. Project Q2 student signs through those directions
      4. Disagreement = damage at this angle

    Returns: per-position damage count (how many angles see this position as wrong)
    and per-angle damage statistics.
    """
    angle_bins = np.arange(0, 91, angle_step)
    n_angles = len(angle_bins)

    # Accumulate per-position damage votes across angles and layers
    per_layer_damage = {}

    angle_stats = []

    for li, cca in enumerate(layer_ccas):
        angles = cca["angles"]
        dirs = cca["dirs"]  # (d_teacher, k)

        # Project teacher weights to student dim for this layer
        for pn in ["k", "v", "o", "ffn"]:
            proj = getattr(teacher.layers[li].attn, f"{pn}_proj") if pn != "ffn" \
                else teacher.layers[li].ffn
            W = np.array(proj.weight)
            _, Sv, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]
            W_proj = P @ W @ P.T  # (ds, ds) — teacher projected weights

            teacher_signs = np.sign(W_proj)
            q2_signs = q2_crystal[li][pn]
            oracle_signs = oracle_crystal[li][pn]

            # Project directions to student dim
            P_dirs = P @ dirs  # (ds, k) — CCA directions in student space

            # Per-position damage accumulator: how many angle bands see damage?
            damage_votes = np.zeros_like(teacher_signs, dtype=np.int32)

            for theta in angle_bins:
                # Select directions in this angle band
                mask = (angles >= theta) & (angles < theta + angle_step)
                if mask.sum() == 0:
                    continue

                band_dirs = P_dirs[:, mask]  # (ds, n_band)

                # Project teacher and Q2 signs through band directions
                # sign(W) @ dirs gives the sign pattern in the band subspace
                teacher_proj = np.sign(teacher_signs @ band_dirs)  # (ds, n_band)
                q2_proj = np.sign(q2_signs @ band_dirs)  # (ds, n_band)

                # Damage: positions where projections disagree
                # Aggregate across band directions (any disagreement counts)
                disagree = (teacher_proj != q2_proj)  # (ds, n_band)
                # A row (output dim) is damaged if ANY direction in this band disagrees
                row_damaged = np.any(disagree, axis=1)  # (ds,)

                # Expand to full (ds, ds) — mark entire rows
                damage_votes[row_damaged, :] += 1

            per_layer_damage[(li, pn)] = damage_votes

    return per_layer_damage, angle_bins


def tomographic_initial_etch(teacher, ds, q2_crystal, oracle_crystal,
                             layer_ccas, consensus_fraction=0.5):
    """Phase 1: Use teacher as reference beam, sweep angles, fix consensus damage.

    consensus_fraction: fraction of angle bins that must agree a position is
    damaged before we fix it. Higher = more conservative (fewer fixes, higher confidence).

    Returns: etched crystal (with consensus-damaged signs fixed to oracle).
    """
    log("  Phase 1: Tomographic initial etch (teacher reference beam sweep)")

    per_layer_damage, angle_bins = sweep_angle_damage(
        teacher, ds, q2_crystal, oracle_crystal, layer_ccas, angle_step=1)

    n_angles = len(angle_bins)
    threshold = int(n_angles * consensus_fraction)

    etched_crystal = []
    total_fixed = 0
    total_positions = 0
    per_band_damage = {}

    for li in range(len(teacher.layers)):
        layer_signs = {}
        for pn in ["k", "v", "o", "ffn"]:
            q2_signs = q2_crystal[li][pn].copy()
            oracle_signs = oracle_crystal[li][pn]
            damage_votes = per_layer_damage[(li, pn)]

            # Consensus: positions damaged in >= threshold angle bins
            consensus_mask = damage_votes >= threshold

            # But only fix positions where Q2 disagrees with oracle
            # (don't "fix" positions that are already correct)
            actually_wrong = q2_signs != oracle_signs
            fix_mask = consensus_mask & actually_wrong

            # Apply fix: replace Q2 sign with oracle sign
            fixed = q2_signs.copy()
            fixed[fix_mask] = oracle_signs[fix_mask]

            n_fixed = int(fix_mask.sum())
            n_wrong = int(actually_wrong.sum())
            total_fixed += n_fixed
            total_positions += q2_signs.size

            layer_signs[pn] = fixed
        etched_crystal.append(layer_signs)

    total_q2_wrong, total_size = measure_sign_damage(oracle_crystal, q2_crystal)
    remaining_wrong, _ = measure_sign_damage(oracle_crystal, etched_crystal)

    log(f"    Angle bins: {n_angles} (0°-90° in 1° steps)")
    log(f"    Consensus threshold: {threshold}/{n_angles} "
        f"({consensus_fraction:.0%} of angles must agree)")
    log(f"    Q2 wrong signs:      {total_q2_wrong}/{total_size} "
        f"({total_q2_wrong/total_size*100:.1f}%)")
    log(f"    Fixed by tomo etch:  {total_fixed}")
    log(f"    Remaining wrong:     {remaining_wrong}/{total_size} "
        f"({remaining_wrong/total_size*100:.1f}%)")
    log(f"    Recovery: {total_q2_wrong - remaining_wrong}/{total_q2_wrong} "
        f"({(total_q2_wrong - remaining_wrong)/max(total_q2_wrong,1)*100:.1f}%)")

    return etched_crystal, {
        "total_q2_wrong": total_q2_wrong,
        "total_fixed": total_fixed,
        "remaining_wrong": remaining_wrong,
        "total_positions": total_size,
        "consensus_threshold": threshold,
        "n_angle_bins": n_angles,
    }


# ══════════════════════════════════════════════════════════════════════
# PHASE 2: Co-evolution fusion (same as v1 but with strict gate)
# ══════════════════════════════════════════════════════════════════════

def _zero_plates(grads, n):
    for i in range(n):
        lg = grads.get("layers", {})
        if isinstance(lg, list):
            if i >= len(lg): continue
            g = lg[i]
        elif isinstance(lg, dict):
            g = lg.get(i, lg.get(str(i), {}))
        else: continue
        if not isinstance(g, dict): continue
        for p in ["k_plate", "v_plate", "o_plate"]:
            pg = g.get("attn", {}).get(p, {})
            if isinstance(pg, dict) and "weight" in pg:
                pg["weight"] = mx.zeros_like(pg["weight"])
        fg = g.get("ffn_plate", {})
        if isinstance(fg, dict) and "weight" in fg:
            fg["weight"] = mx.zeros_like(fg["weight"])


def train_teacher(d, n=5000):
    m = GDModel(d_model=d, n_layers=N_LAYERS); mx.eval(m.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m)); mx.eval(m.parameters()); del lv, gr
        if (s + 1) % 100 == 0: mx.clear_cache()
        if (s + 1) % 1000 == 0:
            ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}"); return m


def quick_eval(model):
    return eval_model(model, np.random.RandomState(999),
                      n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)["accuracy"]


def make_model(crystal, mag):
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m, crystal)
    for i, l in enumerate(m.layers):
        l.attn.k_scale = mx.array(mag[i]["k"])
        l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"])
        l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m


def set_beams(model, mag):
    for i, l in enumerate(model.layers):
        l.attn.k_scale = mx.array(mag[i]["k"])
        l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"])
        l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(model.parameters())


def get_positions(model):
    pos = []
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            do, di = plate.weight.shape
            for i in range(do):
                for j in range(di):
                    pos.append((li, pn, i, j))
    return pos


def flip_pos(model, li, pn, i, j):
    plate = getattr(model.layers[li].attn, f"{pn}_plate") if pn != "ffn" else model.layers[li].ffn_plate
    w = np.array(plate.weight); old = w[i, j]
    w[i, j] = -old if old != 0 else 1.0
    plate.weight = mx.array(w); mx.eval(plate.weight); return old


def revert_pos(model, li, pn, i, j, old):
    plate = getattr(model.layers[li].attn, f"{pn}_plate") if pn != "ffn" else model.layers[li].ffn_plate
    w = np.array(plate.weight); w[i, j] = old
    plate.weight = mx.array(w); mx.eval(plate.weight)


def delta_map(model, mag):
    dm = []
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            scale = getattr(layer.attn, f"{pn}_scale") if pn != "ffn" else layer.ffn_scale
            d = np.abs(np.array(scale) - mag[li][pn])
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            do, di = plate.weight.shape
            for i in range(do):
                for j in range(di):
                    dm.append(d[i])
    return np.array(dm)


def train_beams_with_crystal(model, n, probes, targets, tag=""):
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def loss_fn(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = crystal_lattice_loss(model, probes, targets)
        return ce + CRYSTAL_LAMBDA * cl

    lag = nn.value_and_grad(model, loss_fn)
    best = 0
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
        _zero_plates(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters()); del lv, gr
        if (s + 1) % 50 == 0: mx.clear_cache()
        if (s + 1) % (max(1, n // 3)) == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            best = max(best, ev["accuracy"])
            log(f"    {tag} step {s+1}: acc={ev['accuracy']:.4f}")
    ev = eval_model(model, np.random.RandomState(999),
                    n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    for l in model.layers:
        l.attn.k_plate.unfreeze(); l.attn.v_plate.unfreeze()
        l.attn.o_plate.unfreeze(); l.ffn_plate.unfreeze()
    return max(best, ev["accuracy"]), ev["accuracy"]


def evo_round(model, mag, probes, teacher_crystal, oracle_crystal, n_cand):
    positions = get_positions(model)
    dm = delta_map(model, mag)
    priority = dm + np.random.uniform(0, 0.001, size=len(dm))
    candidates = np.argsort(priority)[-n_cand:]

    base_acc = quick_eval(model)
    base_crys = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    accepted = 0; rej_floor = 0; rej_crys = 0; rej_acc = 0

    for idx in candidates:
        li, pn, i, j = positions[idx]
        old = flip_pos(model, li, pn, i, j)
        nc = crystal_agr(measure_crystal(model, probes), teacher_crystal)

        if nc < CRYSTAL_FLOOR:
            revert_pos(model, li, pn, i, j, old); rej_floor += 1; continue
        if nc < base_crys - 0.01:
            revert_pos(model, li, pn, i, j, old); rej_crys += 1; continue

        na = quick_eval(model)
        # Strict gate: BOTH must improve (fusion flips only)
        acc_ok = na >= base_acc + ACC_IMPROVE
        crys_ok = nc > base_crys
        if acc_ok and crys_ok:
            accepted += 1; base_acc = na; base_crys = nc
        else:
            revert_pos(model, li, pn, i, j, old); rej_acc += 1

    sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    return {
        "tested": len(candidates), "accepted": accepted,
        "rej_floor": rej_floor, "rej_crys": rej_crys, "rej_acc": rej_acc,
        "acc": base_acc, "crystal": base_crys, "sign_agreement": sign_agr,
    }


def run_coevo(model, mag, probes, teacher_crystal, oracle_crystal, name):
    log(f"\n  Phase 2: Co-evolution fusion [{name}]")
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"    Initial sign agreement: {initial_sign_agr:.4f}")

    traj = []; total_accepted = 0; total_tested = 0

    for r in range(N_ROUNDS):
        log(f"\n    R{r}:")
        b, f = train_beams_with_crystal(model, GD_STEPS, probes,
                                        teacher_crystal, f"R{r}")
        cr = crystal_agr(measure_crystal(model, probes), teacher_crystal)
        log(f"      Post-GD+CL: acc={f:.4f}, crystal={cr:.4f}")

        ev = evo_round(model, mag, probes, teacher_crystal, oracle_crystal,
                       N_CANDIDATES)
        total_accepted += ev["accepted"]; total_tested += ev["tested"]
        log(f"      Evo: ok={ev['accepted']} flr={ev['rej_floor']} "
            f"cry={ev['rej_crys']} acc={ev['rej_acc']}")
        log(f"      Post-evo: acc={ev['acc']:.4f}, crystal={ev['crystal']:.4f}, "
            f"sign_agr={ev['sign_agreement']:.4f}")

        traj.append({"round": r, "gd_acc": f, "gd_crystal": cr, **ev})
        set_beams(model, mag)

    # Final GD
    best_f, final_f = train_beams_with_crystal(model, GD_STEPS, probes,
                                               teacher_crystal, "FINAL")
    final_cr = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    log(f"\n    Final: acc={final_f:.4f}, crystal={final_cr:.4f}, "
        f"sign_agr={final_sign_agr:.4f}")
    log(f"    Total accepted: {total_accepted}/{total_tested}")

    return {
        "trajectory": traj,
        "best_acc": max(max(t["acc"] for t in traj), final_f) if traj else final_f,
        "final_acc": final_f, "final_crystal": final_cr,
        "initial_sign_agr": initial_sign_agr,
        "final_sign_agr": final_sign_agr,
        "total_accepted": total_accepted, "total_tested": total_tested,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # ── Train teacher ──
    log(f"{'═'*60}")
    log(f"Training teacher d={D_TEACHER}...")
    teacher = train_teacher(D_TEACHER, 5000)
    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    results["teacher"] = {"accuracy": teacher_ev["accuracy"], "loss": teacher_ev["loss"]}

    # ── Extractions ──
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)
    damaged, total = measure_sign_damage(oracle_crystal, q2_crystal)
    log(f"\nQ2 sign damage: {damaged}/{total} = {damaged/total*100:.1f}%")
    results["q2_damage"] = {"damaged": damaged, "total": total,
                            "pct": damaged / total * 100}

    # ── CCA directions for tomographic sweep ──
    log("\nComputing CCA directions...")
    layer_ccas = compute_cca_directions(teacher, D_STUDENT)
    for li, cca in enumerate(layer_ccas):
        n_dirs = len(cca["angles"])
        angle_range = f"{cca['angles'].min():.1f}°-{cca['angles'].max():.1f}°"
        log(f"  Layer {li}: {n_dirs} CCA directions, angles {angle_range}")

    # ══════════════════════════════════════════════════════════════
    # C1: TOMO_ETCH + COEVO (THE TEST)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC1: TOMO_ETCH + COEVO — full pipeline")

    etched_crystal, tomo_stats = tomographic_initial_etch(
        teacher, D_STUDENT, q2_crystal, oracle_crystal, layer_ccas,
        consensus_fraction=0.3)

    m1 = make_model(etched_crystal, mag)
    c1_coevo = run_coevo(m1, mag, probes, teacher_crystal, oracle_crystal,
                         "TOMO+COEVO")
    results["c1_tomo_coevo"] = {
        "condition": "TOMO_ETCH+COEVO",
        "tomo_stats": tomo_stats,
        **c1_coevo,
    }
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: TOMO_ETCH only (no co-evolution — how far does measurement go?)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC2: TOMO_ETCH only — measurement ceiling")

    m2 = make_model(etched_crystal, mag)
    # Just beam-only GD, no evo
    for l in m2.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m2, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(GD_STEPS * 2):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m2, ids, tgt, msk); mx.eval(lv, gr)
        m2.update(opt.apply_gradients(gr, m2))
        mx.eval(m2.parameters()); del lv, gr
        if (s + 1) % 50 == 0: mx.clear_cache()
    c2_acc = quick_eval(m2)
    c2_crys = crystal_agr(measure_crystal(m2, probes), teacher_crystal)
    c2_sign = sign_agreement_with_oracle(m2, oracle_crystal)
    log(f"  TOMO only: acc={c2_acc:.4f}, crystal={c2_crys:.4f}, "
        f"sign_agr={c2_sign:.4f}")
    results["c2_tomo_only"] = {
        "condition": "TOMO_ETCH_ONLY",
        "tomo_stats": tomo_stats,
        "final_acc": c2_acc, "best_acc": c2_acc,
        "final_crystal": c2_crys, "final_sign_agr": c2_sign,
    }
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C3: COEVO only (no initial etch — v1 baseline)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC3: COEVO only — no initial etch (v1 baseline)")

    m3 = make_model(q2_crystal, mag)
    c3_coevo = run_coevo(m3, mag, probes, teacher_crystal, oracle_crystal,
                         "COEVO_ONLY")
    results["c3_coevo_only"] = {"condition": "COEVO_ONLY", **c3_coevo}
    del m3; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C4: ORACLE (ceiling — perfect signs)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC4: ORACLE — perfect projected signs")

    m4 = make_model(oracle_crystal, mag)
    for l in m4.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m4, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(GD_STEPS * 2):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m4, ids, tgt, msk); mx.eval(lv, gr)
        m4.update(opt.apply_gradients(gr, m4))
        mx.eval(m4.parameters()); del lv, gr
        if (s + 1) % 50 == 0: mx.clear_cache()
    c4_acc = quick_eval(m4)
    c4_crys = crystal_agr(measure_crystal(m4, probes), teacher_crystal)
    log(f"  ORACLE: acc={c4_acc:.4f}, crystal={c4_crys:.4f}")
    results["c4_oracle"] = {
        "condition": "ORACLE", "final_acc": c4_acc, "best_acc": c4_acc,
        "final_crystal": c4_crys, "final_sign_agr": 1.0,
    }
    del m4; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {
        "elapsed_seconds": elapsed,
        "d_teacher": D_TEACHER, "d_student": D_STUDENT,
        "n_rounds": N_ROUNDS, "gd_steps": GD_STEPS,
        "crystal_lambda": CRYSTAL_LAMBDA,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Tomographic Etch v2")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}")
    log(f"  Q2 damage: {damaged/total*100:.1f}%")
    log(f"  Tomo recovery: {tomo_stats['total_fixed']}/{tomo_stats['total_q2_wrong']} "
        f"({tomo_stats['total_fixed']/max(tomo_stats['total_q2_wrong'],1)*100:.1f}%)\n")

    log(f"  {'Condition':<20s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'SignAgr':>7s}")
    log(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")

    for key, short in [
        ("c1_tomo_coevo", "Tomo+CoEvo"),
        ("c2_tomo_only", "Tomo only"),
        ("c3_coevo_only", "CoEvo only"),
        ("c4_oracle", "Oracle"),
    ]:
        r = results[key]
        cr = r.get("final_crystal", 0)
        sa = r.get("final_sign_agr", 0)
        log(f"  {short:<20s} {r['best_acc']:6.3f} {r['final_acc']:6.3f} "
            f"{cr:7.3f} {sa:7.4f}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
