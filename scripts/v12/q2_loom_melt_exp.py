"""Q2 Loom Melt — Multi-angle crystal loss traces the full weave.

The loom has structure at every CCA angle. Each angle-band projection
gives a different cross-section of the 5D lattice. Measure the teacher's
crystal through each band → fixed points. Use ALL fixed points as loss
targets during beam training → beams settle into alignment.

Single forward pass per probe, then project through each band's CCA
directions to get angle-resolved crystal targets. 7 bands × 3 layers
× 6 cosines = 126 geometric targets (vs 18 for per-layer only).

The beams must satisfy all 126 cross-sections simultaneously.
The only configuration that does is the correct loom geometry.

No plate changes. Just rich geometric targets for the beam melt.

Protocol:
  Phase 0: Measure teacher's crystal at each angle band × layer (fixed points)
  Phase 1: Beam training with multi-angle crystal loss (the loom melt)

Conditions:
  C1: LOOM MELT — multi-angle crystal loss (THE TEST)
  C2: PER-LAYER — per-layer crystal loss only (rotation etch baseline)
  C3: ORACLE + LOOM MELT (ceiling)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_loom_melt_exp.py

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
    Comb, Var, App,
    GDModel, HoloModel,
    masked_ce_loss, eval_model,
    generate_batch,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-loom-melt"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
BEAM_STEPS = 3000; BEAM_CRYSTAL_LAMBDA = 0.5; EVAL_BATCHES = 30
COMBINATORS = ["K", "I", "B", "C"]

ANGLE_BANDS = [
    ("shared",      0, 35),
    ("mid_low",    35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]


def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]; fs = ["f","g","h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n*3):
            if len(ps)>=n: break
            v1,v2 = Var(rng.choice(vs)),Var(rng.choice(vs))
            f1,f2 = Var(rng.choice(fs)),Var(rng.choice(fs))
            if c=="K": e=App(App(Comb("K"),v1),v2)
            elif c=="I": e=App(Comb("I"),v1)
            elif c=="B": e=App(App(App(Comb("B"),f1),f2),v1)
            elif c=="C": e=App(App(App(Comb("C"),f1),v1),v2)
            t=["<bos>"]+e.to_tokens()+["="]
            if not all(x in TOK2ID for x in t): continue
            ids=[TOK2ID[x] for x in t]
            ids=ids[:20]+[PAD_ID]*max(0,20-len(ids))
            ps.append(ids)
        probes[c]=ps[:n]
    return probes


def crystal_agr(s, t):
    A, B = np.array(s), np.array(t)
    idx = np.triu_indices(4, k=1)
    a, b = A[idx]-A[idx].mean(), B[idx]-B[idx].mean()
    d = np.sqrt(np.sum(a**2))*np.sqrt(np.sum(b**2))
    return float(np.sum(a*b)/d) if d>1e-10 else 0.0


# ══════════════════════════════════════════════════════════════════════
# CCA band projections
# ══════════════════════════════════════════════════════════════════════

def compute_band_projections(teacher, ds):
    """Compute CCA direction matrices for each angle band at each layer.

    Returns: dict[(layer, band_name)] → projection matrix P (ds, n_band)
    Band projections are in student dimension space.
    """
    log("  Computing CCA band projections...")
    projections = {}

    for li, layer in enumerate(teacher.layers):
        Wk = np.array(layer.attn.k_proj.weight)
        Wf = np.array(layer.ffn.weight)
        _, _, Va = np.linalg.svd(Wk, full_matrices=False)
        _, _, Vb = np.linalg.svd(Wf, full_matrices=False)
        k = min(ds, Va.shape[0], Vb.shape[0])
        A, B = Va[:k, :].T, Vb[:k, :].T
        Qa, _ = np.linalg.qr(A); Qb, _ = np.linalg.qr(B)
        U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
        angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
        dirs = Qa @ U + Qb @ Vt.T
        norms = np.linalg.norm(dirs, axis=0, keepdims=True)
        dirs = dirs / np.maximum(norms, 1e-8)

        # Project to student dim (take first ds rows)
        dirs_student = dirs[:ds, :] if dirs.shape[0] >= ds else np.pad(
            dirs, ((0, ds - dirs.shape[0]), (0, 0)))

        n_total = 0
        for band_name, lo, hi in ANGLE_BANDS:
            mask = (angles >= lo) & (angles < hi)
            n_dirs = int(mask.sum())
            if n_dirs > 0:
                P = dirs_student[:, mask].astype(np.float32)  # (ds, n_band)
                projections[(li, band_name)] = P
                n_total += n_dirs

        log(f"    Layer {li}: {n_total} CCA directions across {len(ANGLE_BANDS)} bands")

    return projections


# ══════════════════════════════════════════════════════════════════════
# Phase 0: Measure teacher's crystal at each angle × layer
# ══════════════════════════════════════════════════════════════════════

def measure_teacher_fixed_points(teacher, probes, projections):
    """Measure teacher's 4×4 cosine matrix through each angle band at each layer.

    These are the fixed points of the loom — the cross-sections that
    the beam melt must satisfy simultaneously.
    """
    log("  Measuring teacher fixed points (crystal at each angle × layer)...")
    fixed_points = {}

    for li in range(N_LAYERS):
        # Get teacher hidden states at this layer
        comb_means = {}
        for c in COMBINATORS:
            hs = []
            for ids in probes[c]:
                x = teacher.embed(mx.array(np.array([ids], dtype=np.int32)))
                for layer_idx in range(li + 1):
                    x = teacher.layers[layer_idx](x)
                hs.append(np.array(x[0, -1, :]))
            comb_means[c] = np.mean(hs, axis=0)  # (d_teacher,)

        # Project through each band and compute cosine matrix
        for band_name, _, _ in ANGLE_BANDS:
            key = (li, band_name)
            if key not in projections:
                continue
            P = projections[key]  # (ds, n_band)

            # Project teacher means (take first ds dims since teacher is bigger)
            projected = []
            for c in COMBINATORS:
                m = comb_means[c][:D_STUDENT]  # truncate to student dim
                projected.append(m @ P)  # (n_band,)

            M = np.array(projected)  # (4, n_band)
            N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
            cos = ((M / N) @ (M / N).T).tolist()
            fixed_points[key] = cos

    n_points = len(fixed_points)
    log(f"    {n_points} fixed points ({n_points * 6} geometric targets)")
    return fixed_points


def measure_unprojected_teacher(teacher, probes):
    """Also measure raw per-layer crystals (no projection)."""
    per_layer = []
    for li in range(N_LAYERS):
        means = []
        for c in COMBINATORS:
            hs = []
            for ids in probes[c]:
                x = teacher.embed(mx.array(np.array([ids], dtype=np.int32)))
                for layer_idx in range(li + 1):
                    x = teacher.layers[layer_idx](x)
                hs.append(np.array(x[0, -1, :]))
            means.append(np.mean(hs, axis=0))
        M = np.array(means)
        N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
        per_layer.append((M / N @ (M / N).T).tolist())
    return per_layer


# ══════════════════════════════════════════════════════════════════════
# Multi-angle crystal loss (the loom melt loss)
# ══════════════════════════════════════════════════════════════════════

def loom_crystal_loss(model, probes, fixed_points, projections):
    """Crystal loss measured through every angle band at every layer.

    Single forward pass per probe per layer, then project through each
    band's CCA directions. Much richer geometric signal than raw crystal.
    """
    total_loss = mx.array(0.0)
    n_terms = 0

    for li in range(N_LAYERS):
        # Forward pass to this layer — capture hidden states
        comb_hidden = {}
        for c in COMBINATORS:
            hs = []
            for ids in probes[c]:
                x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
                for layer_idx in range(li + 1):
                    x = model.layers[layer_idx](x)
                hs.append(x[0, -1, :])  # (d_student,)
            comb_hidden[c] = mx.stack(hs)  # (n_probes, d_student)

        # For each angle band, project and compute crystal loss
        for band_name, _, _ in ANGLE_BANDS:
            key = (li, band_name)
            if key not in fixed_points or key not in projections:
                continue

            P_np = projections[key]  # (ds, n_band)
            P = mx.array(P_np)
            tgt = mx.array(np.array(fixed_points[key], dtype=np.float32))

            # Project hidden states through band directions
            means = []
            for c in COMBINATORS:
                h = mx.mean(comb_hidden[c], axis=0)  # (d_student,)
                h_proj = h @ P  # (n_band,)
                means.append(h_proj)

            M = mx.stack(means)  # (4, n_band)
            N = mx.sqrt(mx.sum(M * M, axis=1, keepdims=True) + 1e-8)
            cos = (M / N) @ (M / N).T

            ir, ic = [0,0,0,1,1,2], [1,2,3,2,3,3]
            band_loss = mx.mean(
                (cos[mx.array(ir), mx.array(ic)] -
                 tgt[mx.array(ir), mx.array(ic)]) ** 2)
            total_loss = total_loss + band_loss
            n_terms += 1

    return total_loss / max(n_terms, 1)


def per_layer_crystal_loss(model, probes, teacher_per_layer):
    """Simple per-layer crystal loss (baseline comparison)."""
    total = mx.array(0.0)
    for tl in range(N_LAYERS):
        tgt = mx.array(np.array(teacher_per_layer[tl], dtype=np.float32))
        means = []
        for c in COMBINATORS:
            hs = []
            for ids in probes[c]:
                x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
                for li in range(tl + 1): x = model.layers[li](x)
                hs.append(x[0, -1, :])
            means.append(mx.mean(mx.stack(hs), axis=0))
        M = mx.stack(means)
        N = mx.sqrt(mx.sum(M*M, axis=1, keepdims=True) + 1e-8)
        cos = (M/N) @ (M/N).T
        ir, ic = [0,0,0,1,1,2], [1,2,3,2,3,3]
        total = total + mx.mean(
            (cos[mx.array(ir),mx.array(ic)] - tgt[mx.array(ir),mx.array(ic)])**2)
    return total / N_LAYERS


# ══════════════════════════════════════════════════════════════════════
# Extraction helpers
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W, n_bits=2, block_size=32):
    W_flat=W.flatten(); n=len(W_flat)
    pad=(block_size-n%block_size)%block_size
    W_padded=np.concatenate([W_flat,np.zeros(pad)])
    W_blocks=W_padded.reshape(-1,block_size)
    n_levels=2**(n_bits-1)
    scales=np.maximum(np.max(np.abs(W_blocks),axis=1,keepdims=True),1e-10)
    W_norm=W_blocks/scales
    W_quant=np.round(W_norm*n_levels).clip(-n_levels,n_levels)
    W_dequant=(W_quant/n_levels)*scales
    signs=np.sign(W_dequant.flatten()[:n].reshape(W.shape)).astype(np.float32)
    zeros=signs==0
    if zeros.any(): signs[zeros]=np.random.RandomState(42).choice([-1.,1.],size=int(zeros.sum()))
    return signs

def extract_oracle_crystal(teacher, ds):
    crystal=[]
    for layer in teacher.layers:
        ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]; W_proj=P@W@P.T
            signs=np.sign(W_proj).astype(np.float32)
            zeros=signs==0
            if zeros.any(): signs[zeros]=np.random.RandomState(42).choice([-1.,1.],size=int(zeros.sum()))
            ls[nm]=signs
        crystal.append(ls)
    return crystal

def extract_q2_crystal(teacher, ds, n_bits=2):
    crystal=[]
    for layer in teacher.layers:
        ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]; W_proj=P@W@P.T
            ls[nm]=q2_simulate_weights(W_proj,n_bits=n_bits)
        crystal.append(ls)
    return crystal

def extract_mag(teacher, ds):
    t=[]
    for layer in teacher.layers:
        lm={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]
            lm[nm]=np.sqrt(np.mean((P@W@P.T)**2,axis=1)).astype(np.float32)
        t.append(lm)
    return t

def sign_agreement_with_oracle(model, oracle_crystal):
    total=0; matching=0
    for li,layer in enumerate(model.layers):
        for pn in ["k","v","o","ffn"]:
            plate=getattr(layer.attn,f"{pn}_plate") if pn!="ffn" else layer.ffn_plate
            current=np.sign(np.array(plate.weight))
            oracle=oracle_crystal[li][pn]
            total+=oracle.size; matching+=int((current==oracle).sum())
    return matching/total if total>0 else 0.0

def make_model(crystal, mag):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m

def train_teacher(d, n=5000):
    m=GDModel(d_model=d,n_layers=N_LAYERS); mx.eval(m.parameters())
    opt=optim.Adam(learning_rate=LR); lag=nn.value_and_grad(m,masked_ce_loss)
    rng=np.random.RandomState(42)
    for s in range(n):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(m,ids,tgt,msk); mx.eval(lv,gr)
        m.update(opt.apply_gradients(gr,m)); mx.eval(m.parameters()); del lv,gr
        if (s+1)%100==0: mx.clear_cache()
        if (s+1)%1000==0:
            ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}"); return m


# ══════════════════════════════════════════════════════════════════════
# Beam training
# ══════════════════════════════════════════════════════════════════════

def run_beam_training(model, probes, crystal_loss_fn, oracle_crystal,
                      teacher_last_crystal, label):
    log(f"\n  Beam training [{label}]")

    for layer in model.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)

    def beam_loss(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = crystal_loss_fn(model)
        return ce + BEAM_CRYSTAL_LAMBDA * cl

    lag = nn.value_and_grad(model, beam_loss)
    rng = np.random.RandomState(42)

    traj = []
    for s in range(BEAM_STEPS):
        ids,tgt,msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv,gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters()); del lv, gr
        if (s+1) % 50 == 0: mx.clear_cache()
        if (s+1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            # Measure raw crystal at last layer
            means = []
            for c in COMBINATORS:
                hs = []
                for ids2 in probes[c]:
                    x = model.embed(mx.array(np.array([ids2], dtype=np.int32)))
                    for layer in model.layers: x = layer(x)
                    hs.append(np.array(x[0, -1, :]))
                means.append(np.mean(hs, axis=0))
            M = np.array(means)
            N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
            crystal = (M / N @ (M / N).T).tolist()
            agr = crystal_agr(crystal, teacher_last_crystal)

            traj.append({"step": s+1, "accuracy": ev["accuracy"],
                         "loss": ev["loss"], "crystal_agr": agr})
            log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}  "
                f"crystal={agr:+.4f}  loss={ev['loss']:.4f}")

    final_ev = eval_model(model, np.random.RandomState(999),
                          n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    # Final crystal
    means = []
    for c in COMBINATORS:
        hs = []
        for ids2 in probes[c]:
            x = model.embed(mx.array(np.array([ids2], dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(np.array(x[0, -1, :]))
        means.append(np.mean(hs, axis=0))
    M = np.array(means)
    N_m = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
    final_crystal = crystal_agr((M / N_m @ (M / N_m).T).tolist(), teacher_last_crystal)

    return {
        "trajectory": traj,
        "final_acc": final_ev["accuracy"], "final_loss": final_ev["loss"],
        "final_crystal": final_crystal,
        "best_acc": max(t["accuracy"] for t in traj) if traj else final_ev["accuracy"],
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    log(f"{'═'*60}")
    log(f"Training teacher d={D_TEACHER}...")
    teacher = train_teacher(D_TEACHER, 5000)

    probes = gen_probes()
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)

    # Phase 0: compute band projections and fixed points
    log(f"\n{'═'*60}")
    log("Phase 0: Measuring loom fixed points")
    projections = compute_band_projections(teacher, D_STUDENT)
    fixed_points = measure_teacher_fixed_points(teacher, probes, projections)
    teacher_per_layer = measure_unprojected_teacher(teacher, probes)
    teacher_last = teacher_per_layer[-1]

    n_targets = len(fixed_points) * 6
    log(f"  Total geometric targets: {n_targets} (loom) vs {N_LAYERS * 6} (per-layer)")

    # ══════════════════════════════════════════════════════════════
    # C1: LOOM MELT — multi-angle crystal loss
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log(f"C1: LOOM MELT (Q2 plates, {n_targets} geometric targets)")

    m1 = make_model(q2_crystal, mag)
    loom_loss = lambda model: loom_crystal_loss(model, probes, fixed_points, projections)
    c1 = run_beam_training(m1, probes, loom_loss, oracle_crystal, teacher_last,
                           f"LOOM_MELT ({n_targets} targets)")
    results["c1_loom_melt"] = {"condition": "LOOM_MELT", **c1}
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: PER-LAYER — per-layer crystal loss only (baseline)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log(f"C2: PER-LAYER (Q2 plates, {N_LAYERS * 6} geometric targets)")

    m2 = make_model(q2_crystal, mag)
    perlayer_loss = lambda model: per_layer_crystal_loss(model, probes, teacher_per_layer)
    c2 = run_beam_training(m2, probes, perlayer_loss, oracle_crystal, teacher_last,
                           f"PER_LAYER ({N_LAYERS * 6} targets)")
    results["c2_perlayer"] = {"condition": "PER_LAYER", **c2}
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C3: ORACLE + LOOM MELT (ceiling)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C3: ORACLE + LOOM MELT (ceiling)")

    m3 = make_model(oracle_crystal, mag)
    c3 = run_beam_training(m3, probes, loom_loss, oracle_crystal, teacher_last,
                           "ORACLE+LOOM_MELT")
    results["c3_oracle_loom"] = {"condition": "ORACLE+LOOM", **c3}
    del m3; mx.clear_cache()

    # Summary
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed, "n_loom_targets": n_targets,
                       "n_perlayer_targets": N_LAYERS * 6}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Loom Melt")
    log(f"{'═'*60}")
    log(f"  Geometric targets: loom={n_targets} vs per-layer={N_LAYERS*6}\n")

    for key, short in [("c1_loom_melt", "Loom Melt"),
                       ("c2_perlayer", "Per-Layer"),
                       ("c3_oracle_loom", "Oracle+Loom")]:
        r = results[key]
        log(f"  {short:<16s}: acc={r['best_acc']:.4f}  crystal={r['final_crystal']:+.4f}")

    c1b = results["c1_loom_melt"]["best_acc"]
    c2b = results["c2_perlayer"]["best_acc"]
    c3b = results["c3_oracle_loom"]["best_acc"]
    log(f"\n  Loom vs Per-Layer: {'✓ LOOM WINS' if c1b > c2b else '✗ PER-LAYER WINS'} "
        f"({c1b:.4f} vs {c2b:.4f})")
    log(f"  Loom vs Oracle:   {c1b/max(c3b,1e-8)*100:.1f}% of ceiling")
    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
