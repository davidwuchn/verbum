"""Q2 Co-Evolution Etch — Apply session 125's winning pipeline to Q2 sign recovery.

Session 125 proved: evolutionary descent (ternary bit flips) + GD (continuous
beams) + crystal lattice loss = accuracy AND crystal improve together.
Session 123 proved: Q2 flips 44% of signs but oracle etch recovers to 1.000.

This experiment applies the validated co-evolution pipeline to Q2 post-
quantization sign correction. The question: can co-evolution recover the
crystal from 44% sign damage?

Protocol:
  1. Train teacher (GD, d=128) to convergence
  2. Q2-simulate: quantize teacher weights to 2-bit, extract damaged signs
  3. Write Q2 signs into HoloModel ternary plates + teacher magnitude template
  4. Co-evolve: GD trains beams (with crystal loss) → delta map → evo flips
     (with crystal floor) → reset beams → repeat

Conditions:
  1. Q2_COEVO:         Q2 plates + mag template + co-evolution (THE TEST)
  2. Q2_BEAM_ONLY:     Q2 plates + mag template + CE-only beam GD (no evo)
  3. RANDOM_COEVO:     Random plates + mag template + co-evolution
  4. Q2_DISTILL_ETCH:  Q2 plates + mag template + old KL etch (session 125 method)
  5. LOOM_COEVO:       Loom-extracted plates + mag template + co-evolution (baseline)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_coevo_etch_exp.py 2>&1 | tee results/q2-coevo-etch/run.log

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
    holo_plate_fingerprint, holo_plate_diff,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-coevo-etch"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4

# Co-evolution config (from evo v3, but more rounds for Q2's 44% damage)
N_ROUNDS = 20           # More rounds — Q2 has 10× more flips than evo v3 started with
GD_STEPS = 1500         # Beam training per round (CE + crystal loss)
N_CANDIDATES = 200      # More candidates per round — bigger search space
EVAL_BATCHES = 30
CRYSTAL_FLOOR = 0.2     # Lower floor — Q2 starts with damaged crystal
CRYSTAL_LAMBDA = 0.3    # Crystal loss weight in GD phase
ACC_IMPROVE = 0.001     # Minimum accuracy improvement for acceptance

# KL etch config (for comparison condition)
KL_ETCH_BATCHES = 100
KL_ETCH_CONFIDENCE = 0.6
KL_BEAM_STEPS = 200

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
            if len(ps) >= n:
                break
            v1, v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1, f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
            if c == "K": e = App(App(Comb("K"), v1), v2)
            elif c == "I": e = App(Comb("I"), v1)
            elif c == "B": e = App(App(App(Comb("B"), f1), f2), v1)
            elif c == "C": e = App(App(App(Comb("C"), f1), v1), v2)
            t = ["<bos>"] + e.to_tokens() + ["="]
            if not all(x in TOK2ID for x in t):
                continue
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
            for layer in model.layers:
                x = layer(x)
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
    """Differentiable crystal loss for GD phase."""
    tgt = mx.array(np.array(targets, dtype=np.float32))
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers:
                x = layer(x)
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
# Q2 quantization
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W: np.ndarray, n_bits: int = 2, block_size: int = 32) -> np.ndarray:
    """Q2-quantize and return sign pattern."""
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
    zeros = signs == 0
    if zeros.any():
        signs[zeros] = np.random.RandomState(42).choice([-1.0, 1.0], size=int(zeros.sum()))
    return signs


def extract_q2_crystal(teacher: GDModel, ds: int, n_bits: int = 2) -> list[dict[str, np.ndarray]]:
    """Q2-quantize teacher weights projected to student dim, extract sign patterns.

    Projects teacher weights to student dimension via SVD before Q2
    simulation — the student operates at ds, not d_teacher, so we must
    simulate quantization at the dimension the plates will actually be.
    """
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            # Project to student dimension via top-k SVD directions
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]           # (ds, d_teacher)
            W_proj = P @ W @ P.T     # (ds, ds) — projected weights
            layer_signs[name] = q2_simulate_weights(W_proj, n_bits=n_bits)
        crystal.append(layer_signs)
    return crystal


def extract_oracle_crystal(teacher: GDModel, ds: int) -> list[dict[str, np.ndarray]]:
    """Extract sign(W_projected) from teacher — the oracle crystal at student dim.

    Projects teacher weights to student dimension via SVD, then takes signs.
    This is what a perfect Q∞ quantization would give us.
    """
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]
            W_proj = P @ W @ P.T
            signs = np.sign(W_proj).astype(np.float32)
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


def measure_sign_damage(oracle_crystal, q2_crystal):
    """Fraction of signs that differ between oracle and Q2."""
    total = 0
    damaged = 0
    for i in range(len(oracle_crystal)):
        for k in oracle_crystal[i]:
            total += oracle_crystal[i][k].size
            damaged += int((oracle_crystal[i][k] != q2_crystal[i][k]).sum())
    return damaged, total


# ══════════════════════════════════════════════════════════════════════
# Extraction (magnitude template + loom plates)
# ══════════════════════════════════════════════════════════════════════

def extract_mag(teacher, ds):
    """Per-output-dim RMS magnitude from teacher, projected to student dim."""
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


def cca_loom_extract(teacher, ds):
    """CCA-based loom sign extraction (from evo v3)."""
    cr = []
    for li, layer in enumerate(teacher.layers):
        Wk = np.array(layer.attn.k_proj.weight)
        Wf = np.array(layer.ffn.weight)
        _, _, Va = np.linalg.svd(Wk, full_matrices=False)
        _, _, Vb = np.linalg.svd(Wf, full_matrices=False)
        k = min(ds, Va.shape[0], Vb.shape[0])
        A, B = Va[:k, :].T, Vb[:k, :].T
        Qa, _ = np.linalg.qr(A)
        Qb, _ = np.linalg.qr(B)
        U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
        ang = np.degrees(np.arccos(np.clip(S, 0, 1)))
        da, db = Qa @ U, Qb @ Vt.T
        sh = da + db
        sh = sh / np.maximum(np.linalg.norm(sh, axis=0, keepdims=True), 1e-8)
        ls = {}
        for nm, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                         ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            cm = (ang >= 35) & (ang < 72)
            if cm.sum() >= 2:
                de = np.sum(sh[:, cm] ** 2, axis=1)
                wt = np.sign(W) * (1.0 + de / (de.max() + 1e-10))[np.newaxis, :]
            else:
                wt = np.sign(W)
            _, Sv, Vtv = np.linalg.svd(W, full_matrices=False)
            P = Vtv[:ds, :]
            s = np.sign(P @ wt @ P.T).astype(np.float32)
            z = s == 0
            if z.any():
                s[z] = np.random.RandomState(42 + li).choice([-1.0, 1.0], size=int(z.sum()))
            ls[nm] = s
        cr.append(ls)
    return cr


# ══════════════════════════════════════════════════════════════════════
# Plate operations (from evo v3)
# ══════════════════════════════════════════════════════════════════════

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
    w = np.array(plate.weight)
    old = w[i, j]
    w[i, j] = -old if old != 0 else 1.0
    plate.weight = mx.array(w)
    mx.eval(plate.weight)
    return old


def revert_pos(model, li, pn, i, j, old):
    plate = getattr(model.layers[li].attn, f"{pn}_plate") if pn != "ffn" else model.layers[li].ffn_plate
    w = np.array(plate.weight)
    w[i, j] = old
    plate.weight = mx.array(w)
    mx.eval(plate.weight)


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


def sign_agreement_with_oracle(model, oracle_crystal):
    """Fraction of plate signs that match oracle."""
    total = 0
    matching = 0
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            current = np.sign(np.array(plate.weight))
            oracle = oracle_crystal[li][pn]
            total += oracle.size
            matching += int((current == oracle).sum())
    return matching / total if total > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════
# Training functions
# ══════════════════════════════════════════════════════════════════════

def _zero_plates(grads, n):
    for i in range(n):
        lg = grads.get("layers", {})
        if isinstance(lg, list):
            if i >= len(lg):
                continue
            g = lg[i]
        elif isinstance(lg, dict):
            g = lg.get(i, lg.get(str(i), {}))
        else:
            continue
        if not isinstance(g, dict):
            continue
        for p in ["k_plate", "v_plate", "o_plate"]:
            pg = g.get("attn", {}).get(p, {})
            if isinstance(pg, dict) and "weight" in pg:
                pg["weight"] = mx.zeros_like(pg["weight"])
        fg = g.get("ffn_plate", {})
        if isinstance(fg, dict) and "weight" in fg:
            fg["weight"] = mx.zeros_like(fg["weight"])


def train_teacher(d, n=5000):
    m = GDModel(d_model=d, n_layers=N_LAYERS)
    mx.eval(m.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk)
        mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m))
        mx.eval(m.parameters())
        del lv, gr
        if (s + 1) % 100 == 0:
            mx.clear_cache()
        if (s + 1) % 1000 == 0:
            ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    return m


def train_beams_with_crystal(model, n, probes, targets, clambda, tag=""):
    """GD with CE + crystal lattice loss."""
    for l in model.layers:
        l.attn.k_plate.freeze()
        l.attn.v_plate.freeze()
        l.attn.o_plate.freeze()
        l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def loss_fn(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        if clambda > 0:
            cl = crystal_lattice_loss(model, probes, targets)
            return ce + clambda * cl
        return ce

    lag = nn.value_and_grad(model, loss_fn)
    best = 0
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk)
        mx.eval(lv, gr)
        _zero_plates(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (s + 1) % 50 == 0:
            mx.clear_cache()
        if (s + 1) % (max(1, n // 3)) == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            best = max(best, ev["accuracy"])
            log(f"    {tag} step {s+1}: acc={ev['accuracy']:.4f}")
    ev = eval_model(model, np.random.RandomState(999),
                    n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    # Unfreeze plates for evo phase
    for l in model.layers:
        l.attn.k_plate.unfreeze()
        l.attn.v_plate.unfreeze()
        l.attn.o_plate.unfreeze()
        l.ffn_plate.unfreeze()
    return max(best, ev["accuracy"]), ev["accuracy"]


def train_beams_plain(model, n, tag=""):
    """GD with CE only (no crystal loss)."""
    for l in model.layers:
        l.attn.k_plate.freeze()
        l.attn.v_plate.freeze()
        l.attn.o_plate.freeze()
        l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)
    best = 0
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk)
        mx.eval(lv, gr)
        _zero_plates(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (s + 1) % 50 == 0:
            mx.clear_cache()
        if (s + 1) % (max(1, n // 3)) == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            best = max(best, ev["accuracy"])
            log(f"    {tag} step {s+1}: acc={ev['accuracy']:.4f}")
    ev = eval_model(model, np.random.RandomState(999),
                    n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    for l in model.layers:
        l.attn.k_plate.unfreeze()
        l.attn.v_plate.unfreeze()
        l.attn.o_plate.unfreeze()
        l.ffn_plate.unfreeze()
    return max(best, ev["accuracy"]), ev["accuracy"]


def quick_eval(model):
    return eval_model(model, np.random.RandomState(999),
                      n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)["accuracy"]


def make_model(crystal, mag):
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS)
    mx.eval(m.parameters())
    write_crystal_to_model(m, crystal)
    for i, l in enumerate(m.layers):
        l.attn.k_scale = mx.array(mag[i]["k"])
        l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"])
        l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(m.parameters())
    return m


def reset_beams(model, mag):
    for i, l in enumerate(model.layers):
        l.attn.k_scale = mx.array(mag[i]["k"])
        l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"])
        l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(model.parameters())


# ══════════════════════════════════════════════════════════════════════
# Evo round (from evo v3, with sign recovery tracking)
# ══════════════════════════════════════════════════════════════════════

def evo_round(model, mag, probes, teacher_crystal, oracle_crystal, n_cand):
    """One round of evolutionary descent with crystal floor."""
    positions = get_positions(model)
    dm = delta_map(model, mag)
    priority = dm + np.random.uniform(0, 0.001, size=len(dm))
    candidates = np.argsort(priority)[-n_cand:]

    base_acc = quick_eval(model)
    base_crys = crystal_agr(measure_crystal(model, probes), teacher_crystal)

    accepted = 0
    rej_floor = 0
    rej_crys = 0
    rej_acc = 0

    for idx in candidates:
        li, pn, i, j = positions[idx]
        old = flip_pos(model, li, pn, i, j)
        nc = crystal_agr(measure_crystal(model, probes), teacher_crystal)

        if nc < CRYSTAL_FLOOR:
            revert_pos(model, li, pn, i, j, old)
            rej_floor += 1
            continue
        if nc < base_crys - 0.01:
            revert_pos(model, li, pn, i, j, old)
            rej_crys += 1
            continue

        na = quick_eval(model)
        # Only accept if BOTH accuracy and crystal improve (or hold).
        # A flip that helps only one metric is either a routing hack
        # (acc up, crystal flat) or irrelevant correction (crystal up,
        # acc flat). Both improving = genuinely repairing a damaged sign.
        acc_ok = na >= base_acc + ACC_IMPROVE
        crys_ok = nc > base_crys
        if acc_ok and crys_ok:
            accepted += 1
            base_acc = na
            base_crys = nc
        else:
            revert_pos(model, li, pn, i, j, old)
            rej_acc += 1

    # Measure sign recovery vs oracle
    sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    return {
        "tested": len(candidates), "accepted": accepted,
        "rej_floor": rej_floor, "rej_crys": rej_crys, "rej_acc": rej_acc,
        "acc": base_acc, "crystal": base_crys,
        "sign_agreement": sign_agr,
    }


# ══════════════════════════════════════════════════════════════════════
# KL-based distill etch (old method, for comparison)
# ══════════════════════════════════════════════════════════════════════

def distill_etch_round(student, teacher, rng):
    """One round of teacher-guided KL etch (from q2_distill_etch_exp.py)."""
    from mini_holo_d_sweep_v2 import _get_plates

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
        teacher_logits = mx.stop_gradient(teacher(input_ids))
        student_logits = student_model(input_ids)
        teacher_lse = mx.logsumexp(teacher_logits, axis=-1, keepdims=True)
        student_lse = mx.logsumexp(student_logits, axis=-1, keepdims=True)
        teacher_log_probs = teacher_logits - teacher_lse
        student_log_probs = student_logits - student_lse
        teacher_probs = mx.exp(teacher_log_probs)
        kl = mx.sum(teacher_probs * (teacher_log_probs - student_log_probs), axis=-1)
        return (kl * mask).sum() / (mask.sum() + 1e-8)

    loss_and_grad = nn.value_and_grad(student, distill_loss)

    for b in range(KL_ETCH_BATCHES):
        input_ids, targets, mask = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)

        for pidx, (layer_idx, pname) in enumerate(plate_paths):
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

    total_flipped = 0
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        confidence = np.abs(acc) / KL_ETCH_BATCHES
        desired_sign = np.sign(acc)
        current = np.sign(np.array(plate.weight)).astype(np.int8)
        should_flip = (
            (confidence > KL_ETCH_CONFIDENCE)
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


def kl_beam_gd_steps(student, rng, n_steps):
    """Beam-only GD using CE loss."""
    optimizer = optim.Adam(learning_rate=LR)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)
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
    for layer in student.layers:
        layer.attn.k_plate.unfreeze()
        layer.attn.v_plate.unfreeze()
        layer.attn.o_plate.unfreeze()
        layer.ffn_plate.unfreeze()


# ══════════════════════════════════════════════════════════════════════
# Co-evolution pipeline
# ══════════════════════════════════════════════════════════════════════

def run_coevo(model, mag, probes, teacher_crystal, oracle_crystal, name):
    """Full co-evolution pipeline: GD+crystal → evo → reset → repeat."""
    log(f"\n{'═'*60}\n{name}")
    traj = []
    total_accepted = 0
    total_tested = 0
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Initial sign agreement with oracle: {initial_sign_agr:.4f}")

    for r in range(N_ROUNDS):
        log(f"\n  R{r}:")
        # GD phase: CE + crystal loss
        b, f = train_beams_with_crystal(model, GD_STEPS, probes, teacher_crystal,
                                        CRYSTAL_LAMBDA, f"R{r}")
        cr = crystal_agr(measure_crystal(model, probes), teacher_crystal)
        log(f"    Post-GD+CL: acc={f:.4f}, crystal={cr:.4f}")

        # Evo phase
        ev = evo_round(model, mag, probes, teacher_crystal, oracle_crystal, N_CANDIDATES)
        total_accepted += ev["accepted"]
        total_tested += ev["tested"]
        log(f"    Evo: ok={ev['accepted']} flr={ev['rej_floor']} "
            f"cry={ev['rej_crys']} acc={ev['rej_acc']}")
        log(f"    Post-evo: acc={ev['acc']:.4f}, crystal={ev['crystal']:.4f}, "
            f"sign_agr={ev['sign_agreement']:.4f}")

        traj.append({
            "round": r, "gd_acc": f, "gd_crystal": cr,
            **ev,
        })

        # Reset beams for next round
        reset_beams(model, mag)

    # Final GD
    best_f, final_f = train_beams_with_crystal(model, GD_STEPS, probes,
                                               teacher_crystal, CRYSTAL_LAMBDA, "FINAL")
    final_cr = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    log(f"\n  Final: acc={final_f:.4f}, crystal={final_cr:.4f}, "
        f"sign_agr={final_sign_agr:.4f}")
    log(f"  Sign recovery: {initial_sign_agr:.4f} → {final_sign_agr:.4f} "
        f"(Δ{final_sign_agr - initial_sign_agr:+.4f})")
    log(f"  Total accepted flips: {total_accepted}/{total_tested}")

    return {
        "condition": name,
        "trajectory": traj,
        "best_acc": max(max(t["acc"] for t in traj), final_f) if traj else final_f,
        "final_acc": final_f,
        "final_crystal": final_cr,
        "initial_sign_agr": initial_sign_agr,
        "final_sign_agr": final_sign_agr,
        "total_accepted": total_accepted,
        "total_tested": total_tested,
    }


def run_kl_distill(model, teacher, oracle_crystal, name):
    """Old KL-based distill etch for comparison."""
    log(f"\n{'═'*60}\n{name}")
    rng = np.random.RandomState(42)
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Initial sign agreement with oracle: {initial_sign_agr:.4f}")

    traj = []
    for round_idx in range(N_ROUNDS):
        flips = distill_etch_round(model, teacher, rng)
        kl_beam_gd_steps(model, rng, KL_BEAM_STEPS)
        ev = eval_model(model, np.random.RandomState(999),
                        n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
        sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
        traj.append({
            "round": round_idx + 1,
            "flips": flips,
            "loss": ev["loss"],
            "accuracy": ev["accuracy"],
            "sign_agreement": sign_agr,
        })
        log(f"    Round {round_idx+1:2d}: flips={flips:4d}, "
            f"acc={ev['accuracy']:.4f}, sign_agr={sign_agr:.4f}")
        mx.clear_cache()

    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Sign recovery: {initial_sign_agr:.4f} → {final_sign_agr:.4f}")

    return {
        "condition": name,
        "trajectory": traj,
        "final_acc": traj[-1]["accuracy"] if traj else 0,
        "best_acc": max(t["accuracy"] for t in traj) if traj else 0,
        "initial_sign_agr": initial_sign_agr,
        "final_sign_agr": final_sign_agr,
    }


def run_beam_only(model, oracle_crystal, name):
    """Beam-only GD, no evo, no crystal loss. Same total compute budget."""
    log(f"\n{'═'*60}\n{name}")
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Initial sign agreement with oracle: {initial_sign_agr:.4f}")

    total_steps = N_ROUNDS * GD_STEPS + GD_STEPS  # match co-evo total
    eval_interval = total_steps // N_ROUNDS

    for l in model.layers:
        l.attn.k_plate.freeze()
        l.attn.v_plate.freeze()
        l.attn.o_plate.freeze()
        l.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    traj = []
    for step in range(total_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk)
        mx.eval(lv, gr)
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % eval_interval == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            traj.append({"step": step + 1, "accuracy": ev["accuracy"],
                         "loss": ev["loss"]})
            log(f"    Step {step+1:5d}: acc={ev['accuracy']:.4f}")

    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Final sign agreement: {final_sign_agr:.4f} (unchanged — plates frozen)")

    return {
        "condition": name,
        "trajectory": traj,
        "final_acc": traj[-1]["accuracy"] if traj else 0,
        "best_acc": max(t["accuracy"] for t in traj) if traj else 0,
        "initial_sign_agr": initial_sign_agr,
        "final_sign_agr": final_sign_agr,
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

    # ── Measure teacher crystal ──
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    log(f"\nTeacher crystal (4×4 cosine matrix):")
    tc = np.array(teacher_crystal)
    for i, c in enumerate(COMBINATORS):
        log(f"  {c}: " + " ".join(f"{tc[i,j]:+.3f}" for j in range(4)))

    # ── Extract oracle crystal + Q2 crystal (both projected to student dim) ──
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    damaged, total = measure_sign_damage(oracle_crystal, q2_crystal)
    log(f"\nQ2 sign damage: {damaged}/{total} = {damaged/total*100:.1f}%")
    results["q2_damage"] = {"damaged": damaged, "total": total,
                            "pct": damaged / total * 100}

    # ── Extract magnitude template + loom plates ──
    mag = extract_mag(teacher, D_STUDENT)
    loom = cca_loom_extract(teacher, D_STUDENT)

    # ── Random crystal ──
    rng_rc = np.random.RandomState(42)
    random_crystal = []
    for layer_signs in oracle_crystal:
        layer_random = {}
        for key, signs in layer_signs.items():
            layer_random[key] = rng_rc.choice(
                [-1.0, 1.0], size=signs.shape).astype(np.float32)
        random_crystal.append(layer_random)

    # ══════════════════════════════════════════════════════════════
    # C1: Q2_COEVO — the main test
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC1: Q2_COEVO — co-evolution on Q2-damaged plates")
    m1 = make_model(q2_crystal, mag)
    results["c1_q2_coevo"] = run_coevo(m1, mag, probes, teacher_crystal,
                                        oracle_crystal, "Q2_COEVO")
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: Q2_BEAM_ONLY — beam GD only, no evo
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC2: Q2_BEAM_ONLY — beam GD only (no evo, no crystal loss)")
    m2 = make_model(q2_crystal, mag)
    results["c2_q2_beam_only"] = run_beam_only(m2, oracle_crystal, "Q2_BEAM_ONLY")
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C3: RANDOM_COEVO — can evo find structure from random?
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC3: RANDOM_COEVO — co-evolution from random plates")
    m3 = make_model(random_crystal, mag)
    results["c3_random_coevo"] = run_coevo(m3, mag, probes, teacher_crystal,
                                            oracle_crystal, "RANDOM_COEVO")
    del m3; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C4: Q2_DISTILL_ETCH — old KL-based etch
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC4: Q2_DISTILL_ETCH — old KL etch (session comparison)")
    m4 = make_model(q2_crystal, mag)
    results["c4_q2_distill_etch"] = run_kl_distill(m4, teacher, oracle_crystal,
                                                    "Q2_DISTILL_ETCH")
    del m4; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C5: LOOM_COEVO — loom-extracted plates + co-evolution
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC5: LOOM_COEVO — co-evolution from loom-extracted plates")
    m5 = make_model(loom, mag)
    loom_sign_agr = sign_agreement_with_oracle(m5, oracle_crystal)
    log(f"  Loom sign agreement with oracle: {loom_sign_agr:.4f}")
    results["c5_loom_coevo"] = run_coevo(m5, mag, probes, teacher_crystal,
                                          oracle_crystal, "LOOM_COEVO")
    del m5; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {
        "elapsed_seconds": elapsed,
        "d_teacher": D_TEACHER, "d_student": D_STUDENT,
        "n_rounds": N_ROUNDS, "gd_steps": GD_STEPS,
        "n_candidates": N_CANDIDATES,
        "crystal_floor": CRYSTAL_FLOOR,
        "crystal_lambda": CRYSTAL_LAMBDA,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Co-Evolution Etch")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}")
    log(f"  Q2 sign damage: {damaged/total*100:.1f}%\n")

    log(f"  {'Condition':<22s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'SignAgr':>7s} {'Flips':>6s}")
    log(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*7} {'-'*7} {'-'*6}")

    for key, name_short in [
        ("c1_q2_coevo", "Q2+CoEvo"),
        ("c2_q2_beam_only", "Q2+BeamOnly"),
        ("c3_random_coevo", "Random+CoEvo"),
        ("c4_q2_distill_etch", "Q2+KLEtch"),
        ("c5_loom_coevo", "Loom+CoEvo"),
    ]:
        r = results[key]
        cr = r.get("final_crystal", "-")
        cr_str = f"{cr:7.3f}" if isinstance(cr, float) else f"{'':>7s}"
        sa = r.get("final_sign_agr", 0)
        flips = r.get("total_accepted", "-")
        flips_str = f"{flips:6d}" if isinstance(flips, int) else f"{'':>6s}"
        log(f"  {name_short:<22s} {r['best_acc']:6.3f} {r['final_acc']:6.3f} "
            f"{cr_str} {sa:7.4f} {flips_str}")

    # Sign recovery trajectory for Q2_COEVO
    traj = results["c1_q2_coevo"].get("trajectory", [])
    if traj:
        log(f"\n  Q2_COEVO crystal + sign trajectory:")
        for t in traj:
            bar_c = "█" * max(0, int(t.get("crystal", 0) * 20))
            bar_s = "▓" * max(0, int(t.get("sign_agreement", 0) * 20))
            log(f"    R{t['round']:2d}: crystal={t.get('crystal',0):+.3f} {bar_c}  "
                f"sign={t.get('sign_agreement',0):.4f} {bar_s}  ok={t['accepted']}")

    # The key question
    c1_best = results["c1_q2_coevo"]["best_acc"]
    c2_best = results["c2_q2_beam_only"]["best_acc"]
    c4_best = results["c4_q2_distill_etch"]["best_acc"]
    log(f"\n  Q2+CoEvo vs Q2+BeamOnly:  {'✓ BETTER' if c1_best > c2_best else '✗ WORSE'} "
        f"({c1_best:.3f} vs {c2_best:.3f})")
    log(f"  Q2+CoEvo vs Q2+KLEtch:    {'✓ BETTER' if c1_best > c4_best else '✗ WORSE'} "
        f"({c1_best:.3f} vs {c4_best:.3f})")

    c1_sa = results["c1_q2_coevo"]["final_sign_agr"]
    c1_sa0 = results["c1_q2_coevo"]["initial_sign_agr"]
    log(f"  Sign recovery: {c1_sa0:.4f} → {c1_sa:.4f} "
        f"({'✓ RECOVERING' if c1_sa > c1_sa0 else '✗ NOT RECOVERING'})")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
