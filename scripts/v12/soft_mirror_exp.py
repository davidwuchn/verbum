"""Soft Mirror Experiment — GD learns sign corrections through continuous mirrors.

Session 124, experiment 9. Instead of discrete sign flips (which break
the crystal), add learnable soft mirrors per plate and train with
crystal lattice loss to constrain corrections to the crystal manifold.

Three conditions:
  1. LOOM_MAG — baseline (no mirrors, beams only)
  2. MIRROR_CE — soft mirrors + CE loss only (no crystal constraint)
  3. MIRROR_CRYSTAL — soft mirrors + CE + crystal lattice loss (the full pipeline)

After training, quantize mirrors to ternary and measure:
  - Accuracy (task performance)
  - Crystal agreement (relational geometry preservation)
  - Mirror statistics (how many flipped to -1, blocked to 0)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/soft_mirror_exp.py

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
    GDModel, HoloBeamLayer, HoloModel,
    count_holo_params,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "soft-mirror"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4
CRYSTAL_LAMBDA = 0.5  # weight for crystal lattice loss
COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Soft Mirror Model — HoloModel with learnable mirrors per plate
# ══════════════════════════════════════════════════════════════════════

class SoftMirrorAttention(nn.Module):
    """Attention with ternary plates + soft mirrors + continuous beam."""
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_plate = TernaryLinear(d_model, d_model)
        self.v_plate = TernaryLinear(d_model, d_model)
        self.o_plate = TernaryLinear(d_model, d_model)
        # Beam scales
        self.k_scale = mx.ones((d_model,))
        self.v_scale = mx.ones((d_model,))
        self.o_scale = mx.ones((d_model,))
        # Soft mirrors — initialized to 1.0 (pass-through)
        self.k_mirror = mx.ones((d_model, d_model))
        self.v_mirror = mx.ones((d_model, d_model))
        self.o_mirror = mx.ones((d_model, d_model))
        self.scale = d_model ** -0.5

    def __call__(self, x):
        B, T, D = x.shape
        q = self.q_proj(x) * self.scale

        # Plate output * soft mirror * beam scale
        k_raw = self.k_plate(x)  # (B, T, D) through ternary
        k = (k_raw * self.k_mirror.reshape(1, 1, D, D).sum(axis=-1)
             if False else k_raw)
        # Simpler: mirror acts per-output-dimension as a learned sign correction
        # k_mirror is (D,D), k_raw is (B,T,D)
        # Apply mirror as: for each output dim i, mirror[i,:] weights the plate
        # But TernaryLinear already does W@x, so mirror should act on the output
        # Simplest correct form: per-output-dim scale that can go negative
        k = self.k_plate(x) * self.k_mirror_scale * self.k_scale
        v = self.v_plate(x) * self.v_mirror_scale * self.v_scale
        
        attn = q @ k.transpose(0, 2, 1)
        mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
        attn = attn + mask
        attn = mx.softmax(attn, axis=-1)

        out = attn @ v
        out = self.o_plate(out) * self.o_mirror_scale * self.o_scale
        return out


# Actually, let me keep it simpler and more correct.
# The soft mirror is a per-output-dimension sign correction.
# It starts at 1.0 and can learn to go to -1.0 (flip) or 0.0 (block).
# This is a (d_model,) vector, not a full matrix.

class MirrorHoloAttention(nn.Module):
    """Attention with ternary plates + per-dim soft mirrors."""
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_plate = TernaryLinear(d_model, d_model)
        self.v_plate = TernaryLinear(d_model, d_model)
        self.o_plate = TernaryLinear(d_model, d_model)
        self.k_scale = mx.ones((d_model,))
        self.v_scale = mx.ones((d_model,))
        self.o_scale = mx.ones((d_model,))
        # Soft mirrors: per-output-dim, init=1.0 (pass-through)
        self.k_mirror = mx.ones((d_model,))
        self.v_mirror = mx.ones((d_model,))
        self.o_mirror = mx.ones((d_model,))
        self.scale = d_model ** -0.5

    def __call__(self, x):
        B, T, D = x.shape
        q = self.q_proj(x) * self.scale
        k = self.k_plate(x) * self.k_mirror * self.k_scale
        v = self.v_plate(x) * self.v_mirror * self.v_scale

        attn = q @ k.transpose(0, 2, 1)
        mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
        attn = mx.softmax(attn + mask, axis=-1)

        out = attn @ v
        return self.o_plate(out) * self.o_mirror * self.o_scale


class MirrorHoloLayer(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.attn = MirrorHoloAttention(d_model)
        self.attn_norm = nn.LayerNorm(d_model)
        self.ffn_plate = TernaryLinear(d_model, d_model)
        self.ffn_norm = nn.LayerNorm(d_model)
        self.ffn_scale = mx.ones((d_model,))
        self.ffn_bias = mx.zeros((d_model,))
        self.ffn_mirror = mx.ones((d_model,))

    def __call__(self, x):
        x = x + self.attn(self.attn_norm(x))
        ffn_out = self.ffn_plate(self.ffn_norm(x)) * self.ffn_mirror * self.ffn_scale + self.ffn_bias
        return x + ffn_out


class MirrorHoloModel(nn.Module):
    def __init__(self, d_model=128, n_layers=3):
        super().__init__()
        self.d_model = d_model
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [MirrorHoloLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


def write_crystal_to_mirror_model(model: MirrorHoloModel, crystal):
    """Write sign topology into MirrorHoloModel plates."""
    for i, layer in enumerate(model.layers):
        for name, plate in [("k", layer.attn.k_plate), ("v", layer.attn.v_plate),
                            ("o", layer.attn.o_plate), ("ffn", layer.ffn_plate)]:
            plate.weight = mx.array(crystal[i][name])


def set_magnitudes(model, mag_template):
    """Set beam scales from magnitude template."""
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag_template[i]["k"])
        layer.attn.v_scale = mx.array(mag_template[i]["v"])
        layer.attn.o_scale = mx.array(mag_template[i]["o"])
        layer.ffn_scale = mx.array(mag_template[i]["ffn"])


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════

def generate_combinator_probes(n_per=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]
    fs = ["f","g","h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n_per * 3):
            if len(ps) >= n_per: break
            v1, v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1, f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
            if c == "K": expr = App(App(Comb("K"), v1), v2)
            elif c == "I": expr = App(Comb("I"), v1)
            elif c == "B": expr = App(App(App(Comb("B"), f1), f2), v1)
            elif c == "C": expr = App(App(App(Comb("C"), f1), v1), v2)
            toks = ["<bos>"] + expr.to_tokens() + ["="]
            if not all(t in TOK2ID for t in toks): continue
            ids = [TOK2ID[t] for t in toks]
            ids = ids[:20] + [PAD_ID] * max(0, 20 - len(ids))
            ps.append(ids)
        probes[c] = ps[:n_per]
    return probes


def measure_crystal(model, probes):
    """Compute 4×4 combinator cosine matrix from model's hidden states."""
    comb_means = {}
    for c in COMBINATORS:
        hiddens = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers:
                x = layer(x)
            h = np.array(x[0, -1, :])
            hiddens.append(h)
        comb_means[c] = np.mean(hiddens, axis=0)

    means = np.array([comb_means[c] for c in COMBINATORS])
    norms = np.maximum(np.linalg.norm(means, axis=1, keepdims=True), 1e-8)
    normed = means / norms
    return (normed @ normed.T).tolist()


def crystal_agreement(student, teacher):
    A, B = np.array(student), np.array(teacher)
    idx = np.triu_indices(4, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    d = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a*b) / d) if d > 1e-10 else 0.0


def crystal_lattice_loss_fn(model, probes, target_cosines):
    """Differentiable crystal lattice loss.
    
    Run probes through model, compute 4×4 cosine matrix, MSE vs targets.
    """
    target = mx.array(np.array(target_cosines, dtype=np.float32))
    means = []
    for c in COMBINATORS:
        hiddens = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers:
                x = layer(x)
            hiddens.append(x[0, -1, :])  # (d_model,)
        mean_h = mx.mean(mx.stack(hiddens), axis=0)  # (d_model,)
        means.append(mean_h)

    means_stack = mx.stack(means)  # (4, d_model)
    norms = mx.sqrt(mx.sum(means_stack * means_stack, axis=1, keepdims=True) + 1e-8)
    normed = means_stack / norms
    cos_mat = normed @ normed.T  # (4, 4)

    # Upper triangle MSE
    idx_r = [0,0,0,1,1,2]
    idx_c = [1,2,3,2,3,3]
    student_vals = cos_mat[mx.array(idx_r), mx.array(idx_c)]
    target_vals = target[mx.array(idx_r), mx.array(idx_c)]

    return mx.mean((student_vals - target_vals) ** 2)


# ══════════════════════════════════════════════════════════════════════
# Mirror statistics
# ══════════════════════════════════════════════════════════════════════

def mirror_stats(model):
    """How have the soft mirrors moved from their initial value of 1.0?"""
    all_mirrors = []
    for layer in model.layers:
        for m in [layer.attn.k_mirror, layer.attn.v_mirror,
                  layer.attn.o_mirror, layer.ffn_mirror]:
            all_mirrors.append(np.array(m).flatten())

    vals = np.concatenate(all_mirrors)
    
    # Quantize to see what the ternary version would be
    quantized = np.sign(np.round(vals))  # round then sign
    
    n_pass = int(np.sum(quantized == 1))   # stayed +1
    n_flip = int(np.sum(quantized == -1))  # flipped to -1
    n_block = int(np.sum(quantized == 0))  # blocked
    total = len(quantized)

    return {
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "pct_pass": n_pass / total * 100,
        "pct_flip": n_flip / total * 100,
        "pct_block": n_block / total * 100,
        "n_total": total,
    }


# ══════════════════════════════════════════════════════════════════════
# Extraction functions (reused)
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(W_a, W_b, k=None):
    d_in = W_a.shape[1]
    if k is None: k = min(d_in, min(W_a.shape[0], W_b.shape[0]))
    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)
    k = min(k, Vt_a.shape[0], Vt_b.shape[0])
    A, B = Vt_a[:k,:].T, Vt_b[:k,:].T
    Qa, _ = np.linalg.qr(A); Qb, _ = np.linalg.qr(B)
    U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
    d_a, d_b = Qa @ U, Qb @ Vt.T
    sh = d_a + d_b
    return angles, sh / np.maximum(np.linalg.norm(sh, axis=0, keepdims=True), 1e-8)

def extract_loom_crystal(teacher, d_small):
    crystal = []
    for li, layer in enumerate(teacher.layers):
        W_k, W_f = np.array(layer.attn.k_proj.weight), np.array(layer.ffn.weight)
        angles, shared = cca_angle_bands(W_k, W_f)
        ls = {}
        for name, proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                           ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W = np.array(proj.weight)
            cmask = (angles >= 35) & (angles < 72)
            if cmask.sum() >= 2:
                de = np.sum(shared[:,cmask]**2, axis=1)
                wt = np.sign(W) * (1.0 + de/(de.max()+1e-10))[np.newaxis,:]
            else:
                wt = np.sign(W)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small,:]
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
        for name, proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                           ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:d_small,:]
            lm[name] = np.sqrt(np.mean((P@W@P.T)**2, axis=1)).astype(np.float32)
        t.append(lm)
    return t


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
            if isinstance(pg,dict) and "weight" in pg: pg["weight"]=mx.zeros_like(pg["weight"])
        fg = g.get("ffn_plate",{})
        if isinstance(fg,dict) and "weight" in fg: fg["weight"]=mx.zeros_like(fg["weight"])


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


def train_mirror_model(model, name, crystal_probes=None, crystal_targets=None,
                       crystal_lambda=0.0, n_steps=N_STEPS):
    """Train MirrorHoloModel. Plates frozen, mirrors + beams learnable."""
    mx.eval(model.parameters())
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def loss_fn(model, input_ids, targets, mask):
        ce = masked_ce_loss(model, input_ids, targets, mask)
        if crystal_lambda > 0 and crystal_probes is not None:
            cl = crystal_lattice_loss_fn(model, crystal_probes, crystal_targets)
            return ce + crystal_lambda * cl
        return ce

    lag = nn.value_and_grad(model, loss_fn)
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
                ms = mirror_stats(model)
                log(f"    Step {s+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}, "
                    f"mirror: flip={ms['pct_flip']:.1f}% block={ms['pct_block']:.1f}%")

    return {"condition":name, "trajectory":traj,
            "final_accuracy":traj[-1]["accuracy"],
            "best_accuracy":max(t["accuracy"] for t in traj),
            "best_loss":min(t["loss"] for t in traj)}


def train_baseline(crystal, mag, name, crystal_probes=None, crystal_targets=None,
                   crystal_lambda=0.0):
    """Train standard HoloModel (no mirrors) for baseline comparison."""
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m, crystal)
    for i, l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters())

    for l in m.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)
    lag = nn.value_and_grad(m, masked_ce_loss)
    traj = []
    for s in range(N_STEPS):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        _zero_plates(gr, len(m.layers))
        m.update(opt.apply_gradients(gr, m)); mx.eval(m.parameters())
        del lv, gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%EVAL_INTERVAL==0:
            ev = eval_model(m, np.random.RandomState(999), n_batches=20, max_depth=MAX_DEPTH)
            traj.append({"step":s+1, "loss":ev["loss"], "accuracy":ev["accuracy"]})
            if (s+1)%500==0:
                log(f"    Step {s+1:4d}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    return m, {"condition":name, "trajectory":traj,
               "final_accuracy":traj[-1]["accuracy"],
               "best_accuracy":max(t["accuracy"] for t in traj),
               "best_loss":min(t["loss"] for t in traj)}


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("Training teacher d=256...")
    teacher = train_teacher_model(D_TEACHER)

    log("\nGenerating probes...")
    probes = generate_combinator_probes()

    log("\nExtracting teacher crystal geometry...")
    teacher_crystal_geom = measure_crystal(teacher, probes)
    tc = np.array(teacher_crystal_geom)
    log("  Teacher 4×4 cosine matrix:")
    for i, c in enumerate(COMBINATORS):
        log(f"    {c}: " + " ".join(f"{tc[i,j]:+.3f}" for j in range(4)))

    log("\nExtracting loom crystal + magnitudes...")
    loom_crystal = extract_loom_crystal(teacher, D_STUDENT)
    mag_template = extract_mag(teacher, D_STUDENT)

    # ── Condition 1: LOOM_MAG baseline (no mirrors) ──
    log(f"\n{'═'*60}")
    log("CONDITION 1: LOOM_MAG (baseline, no mirrors)")
    bl_model, bl_result = train_baseline(loom_crystal, mag_template, "LOOM_MAG")
    bl_crystal = measure_crystal(bl_model, probes)
    bl_agr = crystal_agreement(bl_crystal, teacher_crystal_geom)
    log(f"  Crystal agreement: {bl_agr:.4f}")
    del bl_model; mx.clear_cache()

    # ── Condition 2: MIRROR_CE (soft mirrors, CE only) ──
    log(f"\n{'═'*60}")
    log("CONDITION 2: MIRROR_CE (soft mirrors, CE only)")
    m2 = MirrorHoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m2.parameters())
    write_crystal_to_mirror_model(m2, loom_crystal)
    set_magnitudes(m2, mag_template)
    mx.eval(m2.parameters())
    r2 = train_mirror_model(m2, "MIRROR_CE", crystal_lambda=0.0)
    m2_crystal = measure_crystal(m2, probes)
    m2_agr = crystal_agreement(m2_crystal, teacher_crystal_geom)
    m2_ms = mirror_stats(m2)
    log(f"  Crystal agreement: {m2_agr:.4f}")
    log(f"  Mirror: flip={m2_ms['pct_flip']:.1f}%, block={m2_ms['pct_block']:.1f}%, "
        f"mean={m2_ms['mean']:.4f}, std={m2_ms['std']:.4f}")
    del m2; mx.clear_cache()

    # ── Condition 3: MIRROR_CRYSTAL (soft mirrors + crystal loss) ──
    log(f"\n{'═'*60}")
    log(f"CONDITION 3: MIRROR_CRYSTAL (soft mirrors + crystal loss, λ={CRYSTAL_LAMBDA})")
    m3 = MirrorHoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m3.parameters())
    write_crystal_to_mirror_model(m3, loom_crystal)
    set_magnitudes(m3, mag_template)
    mx.eval(m3.parameters())
    r3 = train_mirror_model(m3, "MIRROR_CRYSTAL",
                            crystal_probes=probes,
                            crystal_targets=teacher_crystal_geom,
                            crystal_lambda=CRYSTAL_LAMBDA)
    m3_crystal = measure_crystal(m3, probes)
    m3_agr = crystal_agreement(m3_crystal, teacher_crystal_geom)
    m3_ms = mirror_stats(m3)
    log(f"  Crystal agreement: {m3_agr:.4f}")
    log(f"  Mirror: flip={m3_ms['pct_flip']:.1f}%, block={m3_ms['pct_block']:.1f}%, "
        f"mean={m3_ms['mean']:.4f}, std={m3_ms['std']:.4f}")
    del m3; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SUMMARY")
    log(f"{'═'*60}\n")

    log(f"  {'Condition':<18s} {'Best Acc':>8s} {'Final':>8s} {'Crystal':>8s} {'Flip%':>6s} {'Block%':>7s}")
    log(f"  {'-'*18} {'-'*8} {'-'*8} {'-'*8} {'-'*6} {'-'*7}")
    log(f"  {'LOOM_MAG':<18s} {bl_result['best_accuracy']:8.4f} "
        f"{bl_result['final_accuracy']:8.4f} {bl_agr:8.4f}      -       -")
    log(f"  {'MIRROR_CE':<18s} {r2['best_accuracy']:8.4f} "
        f"{r2['final_accuracy']:8.4f} {m2_agr:8.4f} {m2_ms['pct_flip']:5.1f}% {m2_ms['pct_block']:6.1f}%")
    log(f"  {'MIRROR_CRYSTAL':<18s} {r3['best_accuracy']:8.4f} "
        f"{r3['final_accuracy']:8.4f} {m3_agr:8.4f} {m3_ms['pct_flip']:5.1f}% {m3_ms['pct_block']:6.1f}%")

    # Key question: does MIRROR_CRYSTAL improve BOTH accuracy and crystal?
    both_better = (r3["best_accuracy"] > bl_result["best_accuracy"] and
                   m3_agr > bl_agr)
    log(f"\n  MIRROR_CRYSTAL improves both accuracy AND crystal? {'✓ YES' if both_better else '✗ NO'}")
    log(f"    Accuracy: {bl_result['best_accuracy']:.4f} → {r3['best_accuracy']:.4f} "
        f"({'↑' if r3['best_accuracy'] > bl_result['best_accuracy'] else '↓'})")
    log(f"    Crystal:  {bl_agr:.4f} → {m3_agr:.4f} "
        f"({'↑' if m3_agr > bl_agr else '↓'})")

    # Save
    results = {
        "loom_mag": {**bl_result, "crystal_agreement": bl_agr},
        "mirror_ce": {**r2, "crystal_agreement": m2_agr, "mirror_stats": m2_ms},
        "mirror_crystal": {**r3, "crystal_agreement": m3_agr, "mirror_stats": m3_ms},
        "teacher_crystal": teacher_crystal_geom,
        "config": {"d_teacher":D_TEACHER, "d_student":D_STUDENT,
                    "crystal_lambda":CRYSTAL_LAMBDA},
        "elapsed_seconds": time.time() - t0,
    }
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
