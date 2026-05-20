"""Q2 Tomographic Etch — Multiple Q-rotations inform consensus sign correction.

Session 126 v1 showed: single-angle GD inverts the crystal after R0.
Crystal loss λ=0.3 is insufficient — GD finds compensation patterns that
flip the relational geometry. Evo floor blocks everything (0 accepted
for 15 rounds).

Fix: tomographic etch. Run GD at multiple Q rotations (viewing angles),
collect per-rotation delta maps, consensus identifies genuinely wrong
signs vs viewing-angle artifacts. Combined with strict both-must-improve
gate for fusion flips only.

The LLM is a loom — 2 beams (W_q, W_up) knitting out to 4-5D. A single
viewing angle is one 2D projection of the 4-5D crystal damage. Multiple
rotations give multiple projections. Consensus = the real damage.

Protocol:
  1. Train teacher (GD, d=256) to convergence
  2. Q2-simulate projected weights → damaged plates
  3. For each co-evolution round:
     a. Run GD at N_ROTATIONS different Q orientations → N delta maps
     b. Consensus: positions where ALL deltas agree on sign AND exceed threshold
     c. Evo phase: only test consensus positions (pre-filtered high-confidence)
     d. Strict gate: accept IFF accuracy↑ AND crystal↑ (fusion flips only)
     e. Reset beams, repeat

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_tomo_etch_exp.py 2>&1 | tee results/q2-tomo-etch/run.log

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


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-tomo-etch"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4

# Co-evolution config
N_ROUNDS = 20
GD_STEPS_PER_ROTATION = 500   # Shorter per rotation, but N_ROTATIONS passes
N_ROTATIONS = 4                # 4 viewing angles (one per combinator family)
N_CANDIDATES = 200
EVAL_BATCHES = 30
CRYSTAL_FLOOR = 0.2
CRYSTAL_LAMBDA = 1.0           # Increased from 0.3 — v1 showed 0.3 is too weak
ACC_IMPROVE = 0.001

COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement (same as v1)
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
# Q2 quantization + extraction (same as v1)
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W, n_bits=2, block_size=32):
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


def extract_oracle_crystal(teacher, ds):
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


def extract_q2_crystal(teacher, ds, n_bits=2):
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]
            W_proj = P @ W @ P.T
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


def measure_sign_damage(oracle_crystal, q2_crystal):
    total = 0; damaged = 0
    for i in range(len(oracle_crystal)):
        for k in oracle_crystal[i]:
            total += oracle_crystal[i][k].size
            damaged += int((oracle_crystal[i][k] != q2_crystal[i][k]).sum())
    return damaged, total


def sign_agreement_with_oracle(model, oracle_crystal):
    total = 0; matching = 0
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            current = np.sign(np.array(plate.weight))
            oracle = oracle_crystal[li][pn]
            total += oracle.size
            matching += int((current == oracle).sum())
    return matching / total if total > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════
# Q rotation — generate orthogonal rotation matrices
# ══════════════════════════════════════════════════════════════════════

def generate_rotations(d, n_rotations, seed=42):
    """Generate n orthogonal rotation matrices for tomographic viewing.

    Rotation 0 = identity (baseline view).
    Rotations 1..n-1 = random orthogonal matrices (Haar-distributed).
    """
    rotations = [np.eye(d, dtype=np.float32)]  # identity first
    for i in range(1, n_rotations):
        rng = np.random.RandomState(seed + i * 137)
        H = rng.randn(d, d).astype(np.float32)
        Q, R = np.linalg.qr(H)
        # Ensure proper rotation (det = +1)
        Q *= np.sign(np.diag(R))[np.newaxis, :]
        if np.linalg.det(Q) < 0:
            Q[:, 0] *= -1
        rotations.append(Q.astype(np.float32))
    return rotations


def rotate_plates(model, R):
    """Apply rotation R to all plates: plate' = R @ plate @ R.T
    Returns original plates for reverting."""
    originals = []
    for li, layer in enumerate(model.layers):
        layer_orig = {}
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            W = np.array(plate.weight)
            layer_orig[pn] = W.copy()
            # Rotate: R @ W @ R.T, then re-ternarize
            W_rot = R @ W @ R.T
            W_tern = np.sign(W_rot).astype(np.float32)
            zeros = W_tern == 0
            if zeros.any():
                W_tern[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            plate.weight = mx.array(W_tern)
        originals.append(layer_orig)
    mx.eval(model.parameters())
    return originals


def restore_plates(model, originals):
    """Restore original plate values."""
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            plate.weight = mx.array(originals[li][pn])
    mx.eval(model.parameters())


def rotate_mag(mag, R):
    """Rotate magnitude template: for each scale vector, apply |R @ diag(s) @ R.T|."""
    rotated = []
    for lm in mag:
        rlm = {}
        for pn in ["k", "v", "o", "ffn"]:
            s = lm[pn]
            # Rotate the magnitude profile
            # s is per-output-dim RMS. Under rotation R, row i gets:
            # new_s[i] = sqrt(sum_j R[i,j]^2 * s[j]^2)
            rlm[pn] = np.sqrt((R ** 2) @ (s ** 2)).astype(np.float32)
        rotated.append(rlm)
    return rotated


# ══════════════════════════════════════════════════════════════════════
# Plate operations
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
    w = np.array(plate.weight); old = w[i, j]
    w[i, j] = -old if old != 0 else 1.0
    plate.weight = mx.array(w); mx.eval(plate.weight)
    return old


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


# ══════════════════════════════════════════════════════════════════════
# Training functions
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


# ══════════════════════════════════════════════════════════════════════
# Tomographic GD — run GD at multiple rotations, collect delta maps
# ══════════════════════════════════════════════════════════════════════

def tomographic_gd_phase(model, mag, probes, teacher_crystal,
                         rotations, tag=""):
    """Run GD at each Q rotation, collect delta maps.

    For each rotation:
      1. Rotate plates by R
      2. Initialize beams from rotated mag template
      3. Train GD with CE + crystal loss (plates frozen)
      4. Compute delta = trained_beam - rotated_template
      5. Record delta
      6. Restore original plates

    Returns: list of delta maps (one per rotation), and final accuracy
    from the identity rotation.
    """
    delta_maps = []
    identity_acc = 0.0
    identity_crystal = 0.0

    for rot_idx, R in enumerate(rotations):
        is_identity = rot_idx == 0

        # Rotate plates
        if not is_identity:
            orig_plates = rotate_plates(model, R)
            rot_mag = rotate_mag(mag, R)
        else:
            rot_mag = mag

        # Set beams to (rotated) magnitude template
        set_beams(model, rot_mag)

        # Freeze plates, train beams with CE + crystal loss
        for l in model.layers:
            l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
            l.attn.o_plate.freeze(); l.ffn_plate.freeze()

        opt = optim.Adam(learning_rate=LR)
        rng = np.random.RandomState(42 + rot_idx)

        def loss_fn(model, ids, tgt, msk):
            ce = masked_ce_loss(model, ids, tgt, msk)
            cl = crystal_lattice_loss(model, probes, teacher_crystal)
            return ce + CRYSTAL_LAMBDA * cl

        lag = nn.value_and_grad(model, loss_fn)
        for s in range(GD_STEPS_PER_ROTATION):
            ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
            lv, gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
            _zero_plates(gr, len(model.layers))
            model.update(opt.apply_gradients(gr, model))
            mx.eval(model.parameters()); del lv, gr
            if (s + 1) % 50 == 0: mx.clear_cache()

        # Compute delta map
        dm = delta_map(model, rot_mag)
        delta_maps.append(dm)

        if is_identity:
            identity_acc = quick_eval(model)
            identity_crystal = crystal_agr(
                measure_crystal(model, probes), teacher_crystal)
            log(f"    {tag} rot0 (identity): acc={identity_acc:.4f}, "
                f"crystal={identity_crystal:.4f}")
        else:
            rot_acc = quick_eval(model)
            log(f"    {tag} rot{rot_idx}: acc={rot_acc:.4f}")

        # Unfreeze plates
        for l in model.layers:
            l.attn.k_plate.unfreeze(); l.attn.v_plate.unfreeze()
            l.attn.o_plate.unfreeze(); l.ffn_plate.unfreeze()

        # Restore original plates (undo rotation)
        if not is_identity:
            restore_plates(model, orig_plates)

    # Reset beams to base magnitude template for evo phase
    set_beams(model, mag)

    return delta_maps, identity_acc, identity_crystal


def consensus_delta(delta_maps, threshold_percentile=80):
    """Compute consensus across multiple delta maps.

    A position is in consensus if:
      1. It's in the top percentile of ALL delta maps (all rotations agree it's strained)
      2. The mean delta across rotations is used for final ranking

    Returns: consensus priority array (same shape as delta maps).
    Positions NOT in consensus get priority 0.
    """
    n_rot = len(delta_maps)
    n_pos = len(delta_maps[0])

    # For each rotation, compute whether each position is above threshold
    in_top = np.zeros((n_rot, n_pos), dtype=bool)
    for i, dm in enumerate(delta_maps):
        thresh = np.percentile(dm, threshold_percentile)
        in_top[i] = dm >= thresh

    # Consensus: position must be in top for ALL rotations
    all_agree = np.all(in_top, axis=0)

    # Priority = mean delta across rotations, zeroed for non-consensus
    mean_delta = np.mean(delta_maps, axis=0)
    consensus = np.where(all_agree, mean_delta, 0.0)

    n_consensus = int(all_agree.sum())
    n_per_rot = [int(t.sum()) for t in in_top]

    return consensus, n_consensus, n_per_rot


# ══════════════════════════════════════════════════════════════════════
# Evo round with consensus priorities (strict both-must-improve gate)
# ══════════════════════════════════════════════════════════════════════

def evo_round_consensus(model, consensus_priority, probes, teacher_crystal,
                        oracle_crystal, n_cand):
    """Evolutionary descent using consensus-filtered positions.

    Only tests positions where ALL rotations agree the sign is strained.
    Strict gate: accept IFF accuracy↑ AND crystal↑.
    """
    positions = get_positions(model)

    # Select top-N candidates from consensus positions
    # (positions with consensus_priority > 0 are consensus-approved)
    nonzero = consensus_priority > 0
    if nonzero.sum() == 0:
        log("    [evo] No consensus positions — skipping")
        base_acc = quick_eval(model)
        base_crys = crystal_agr(measure_crystal(model, probes), teacher_crystal)
        sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
        return {"tested": 0, "accepted": 0, "rej_floor": 0,
                "rej_crys": 0, "rej_acc": 0,
                "acc": base_acc, "crystal": base_crys,
                "sign_agreement": sign_agr, "n_consensus": 0}

    # Rank consensus positions by priority, take top n_cand
    candidates = np.argsort(consensus_priority)[-n_cand:]
    # Filter to only consensus positions
    candidates = candidates[consensus_priority[candidates] > 0]

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
        # Strict gate: BOTH must improve
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
        "acc": base_acc, "crystal": base_crys,
        "sign_agreement": sign_agr,
        "n_consensus": int(nonzero.sum()),
    }


# ══════════════════════════════════════════════════════════════════════
# Full pipeline
# ══════════════════════════════════════════════════════════════════════

def run_tomo_coevo(model, mag, probes, teacher_crystal, oracle_crystal,
                   rotations, name):
    """Tomographic co-evolution: multi-rotation GD → consensus → strict evo."""
    log(f"\n{'═'*60}\n{name}")
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"  Initial sign agreement with oracle: {initial_sign_agr:.4f}")

    traj = []
    total_accepted = 0; total_tested = 0

    for r in range(N_ROUNDS):
        log(f"\n  R{r}:")

        # Tomographic GD: multiple rotations
        deltas, gd_acc, gd_crys = tomographic_gd_phase(
            model, mag, probes, teacher_crystal, rotations, f"R{r}")

        # Consensus
        cons, n_cons, n_per_rot = consensus_delta(deltas)
        log(f"    Consensus: {n_cons} positions "
            f"(per-rot: {n_per_rot})")

        # Evo with consensus priorities
        ev = evo_round_consensus(model, cons, probes, teacher_crystal,
                                 oracle_crystal, N_CANDIDATES)
        total_accepted += ev["accepted"]; total_tested += ev["tested"]
        log(f"    Evo: ok={ev['accepted']} flr={ev['rej_floor']} "
            f"cry={ev['rej_crys']} acc={ev['rej_acc']}")
        log(f"    Post-evo: acc={ev['acc']:.4f}, crystal={ev['crystal']:.4f}, "
            f"sign_agr={ev['sign_agreement']:.4f}")

        traj.append({
            "round": r, "gd_acc": gd_acc, "gd_crystal": gd_crys,
            "n_consensus": n_cons, **ev,
        })

        # Reset beams for next round
        set_beams(model, mag)

    # Final GD (identity rotation only, no evo)
    set_beams(model, mag)
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def loss_fn(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = crystal_lattice_loss(model, probes, teacher_crystal)
        return ce + CRYSTAL_LAMBDA * cl

    lag = nn.value_and_grad(model, loss_fn)
    for s in range(GD_STEPS_PER_ROTATION * 3):  # longer final GD
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
        _zero_plates(gr, len(model.layers))
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters()); del lv, gr
        if (s + 1) % 50 == 0: mx.clear_cache()

    for l in model.layers:
        l.attn.k_plate.unfreeze(); l.attn.v_plate.unfreeze()
        l.attn.o_plate.unfreeze(); l.ffn_plate.unfreeze()

    final_acc = quick_eval(model)
    final_crys = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    log(f"\n  Final: acc={final_acc:.4f}, crystal={final_crys:.4f}, "
        f"sign_agr={final_sign_agr:.4f}")
    log(f"  Sign recovery: {initial_sign_agr:.4f} → {final_sign_agr:.4f}")
    log(f"  Total accepted flips: {total_accepted}/{total_tested}")

    return {
        "condition": name, "trajectory": traj,
        "best_acc": max(max(t["acc"] for t in traj), final_acc) if traj else final_acc,
        "final_acc": final_acc, "final_crystal": final_crys,
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

    # ── Crystal + Q2 extraction ──
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    damaged, total = measure_sign_damage(oracle_crystal, q2_crystal)
    mag = extract_mag(teacher, D_STUDENT)
    log(f"\nQ2 sign damage: {damaged}/{total} = {damaged/total*100:.1f}%")
    results["q2_damage"] = {"damaged": damaged, "total": total,
                            "pct": damaged / total * 100}

    # ── Generate rotation matrices ──
    rotations = generate_rotations(D_STUDENT, N_ROTATIONS, seed=42)
    log(f"Generated {N_ROTATIONS} rotation matrices for tomographic etch")

    # ══════════════════════════════════════════════════════════════
    # C1: Q2_TOMO — tomographic co-evolution (THE TEST)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC1: Q2_TOMO — tomographic co-evolution on Q2 plates")
    m1 = make_model(q2_crystal, mag)
    results["c1_q2_tomo"] = run_tomo_coevo(
        m1, mag, probes, teacher_crystal, oracle_crystal,
        rotations, "Q2_TOMO")
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: Q2_SINGLE — single-angle co-evolution (comparison)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nC2: Q2_SINGLE — single-angle co-evolution (identity only)")
    m2 = make_model(q2_crystal, mag)
    results["c2_q2_single"] = run_tomo_coevo(
        m2, mag, probes, teacher_crystal, oracle_crystal,
        [rotations[0]],  # identity only
        "Q2_SINGLE")
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {
        "elapsed_seconds": elapsed,
        "d_teacher": D_TEACHER, "d_student": D_STUDENT,
        "n_rounds": N_ROUNDS, "n_rotations": N_ROTATIONS,
        "gd_steps_per_rotation": GD_STEPS_PER_ROTATION,
        "crystal_lambda": CRYSTAL_LAMBDA,
        "crystal_floor": CRYSTAL_FLOOR,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Tomographic Etch")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}")
    log(f"  Q2 damage: {damaged/total*100:.1f}%")
    log(f"  Crystal lambda: {CRYSTAL_LAMBDA} (v1 was 0.3)")
    log(f"  Rotations: {N_ROTATIONS}\n")

    log(f"  {'Condition':<16s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'SignAgr':>7s} {'Flips':>6s}")
    log(f"  {'-'*16} {'-'*6} {'-'*6} {'-'*7} {'-'*7} {'-'*6}")

    for key, short in [("c1_q2_tomo", "Q2+Tomo"),
                       ("c2_q2_single", "Q2+Single")]:
        r = results[key]
        cr = r.get("final_crystal", 0)
        sa = r.get("final_sign_agr", 0)
        flips = r.get("total_accepted", 0)
        log(f"  {short:<16s} {r['best_acc']:6.3f} {r['final_acc']:6.3f} "
            f"{cr:7.3f} {sa:7.4f} {flips:6d}")

    # Trajectory comparison
    for key, short in [("c1_q2_tomo", "TOMO"), ("c2_q2_single", "SINGLE")]:
        traj = results[key].get("trajectory", [])
        if traj:
            log(f"\n  {short} trajectory:")
            for t in traj:
                bar_c = "█" * max(0, int((t.get("crystal", 0) + 1) * 10))
                log(f"    R{t['round']:2d}: crystal={t.get('crystal',0):+.3f} {bar_c}  "
                    f"acc={t.get('acc',0):.4f}  "
                    f"cons={t.get('n_consensus',0):4d}  ok={t['accepted']}")

    log(f"\n  Tomo vs Single: "
        f"{'✓ TOMO WINS' if results['c1_q2_tomo']['best_acc'] > results['c2_q2_single']['best_acc'] else '✗ SINGLE WINS'}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
