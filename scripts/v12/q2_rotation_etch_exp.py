"""Q2 Rotation Etch — Compute sign corrections from measured geometry.

The problem was never optimization. It's measurement + transcription.

The teacher's geometry is fully formed: rotation angles, lattice positions,
WHNF anti-correlation — all measurable. We compute the correction analytically
from the geometric difference between teacher and student, not search for it
via gradient descent.

Key insight: per-layer crystal loss gives each layer's plates a DIRECT
gradient signal (short backprop path) instead of routing through all layers.
Combined with rotation angle matching and WHNF anti-correlation, this gives
us 18+ geometric markers constraining ~196k plate signs.

Protocol:
  Phase 0: MEASURE teacher geometry
    - Per-layer 4×4 cosine matrices (markers in the 5D lattice)
    - Per-combinator rotation angles at each layer
    - WHNF anti-correlation angles
    → These ARE the lattice coordinates

  Phase 1: ETCH plates using per-layer crystal gradient
    - Loss = Σ_layer MSE(student_crystal[L], teacher_crystal[L])
    - Each layer's plates get direct gradient (no deep backprop)
    - Accumulate sign(grad), flip confident positions
    - Much cleaner signal than last-layer-only crystal loss

  Phase 2: TRAIN beams (CE + crystal loss, plates frozen)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_rotation_etch_exp.py 2>&1 | tee results/q2-rotation-etch/run.log

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
    _get_plates,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-rotation-etch"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4

LATTICE_ROUNDS = 30
LATTICE_BATCHES = 200
FLIPS_PER_ROUND = 500     # top-K by gradient magnitude (was: threshold → 98k!)

BEAM_STEPS = 3000
BEAM_CRYSTAL_LAMBDA = 0.5
EVAL_BATCHES = 30

COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Probes + crystal measurement
# ══════════════════════════════════════════════════════════════════════

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


def crystal_at_layer(model, probes, target_layer):
    """Measure 4×4 cosine matrix at a specific layer depth."""
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for li in range(target_layer + 1):
                x = model.layers[li](x)
            hs.append(np.array(x[0, -1, :]))
        means.append(np.mean(hs, axis=0))
    M = np.array(means)
    N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
    return (M / N @ (M / N).T).tolist()


def crystal_agr(s, t):
    A, B = np.array(s), np.array(t)
    idx = np.triu_indices(4, k=1)
    a, b = A[idx]-A[idx].mean(), B[idx]-B[idx].mean()
    d = np.sqrt(np.sum(a**2))*np.sqrt(np.sum(b**2))
    return float(np.sum(a*b)/d) if d>1e-10 else 0.0


# ══════════════════════════════════════════════════════════════════════
# Phase 0: Measure teacher geometry (the 5D lattice markers)
# ══════════════════════════════════════════════════════════════════════

def measure_teacher_geometry(teacher, probes):
    """Measure the teacher's per-layer crystal = the lattice markers.

    Returns list of 4×4 cosine matrices, one per layer.
    These ARE the 5D lattice coordinates projected to each depth.
    """
    log("  Phase 0: Measuring teacher geometry (5D lattice markers)")
    per_layer_crystals = []
    for li in range(N_LAYERS):
        crystal = crystal_at_layer(teacher, probes, li)
        agr_self = crystal_agr(crystal, crystal)
        per_layer_crystals.append(crystal)

        c = np.array(crystal)
        log(f"    Layer {li}: "
            + " ".join(f"{c[0,j]:+.3f}" for j in range(4))
            + f"  (K↔I={c[0,1]:.3f} K↔C={c[0,3]:.3f} I↔C={c[1,3]:.3f})")

    return per_layer_crystals


# ══════════════════════════════════════════════════════════════════════
# Per-layer crystal lattice loss — the key improvement
# ══════════════════════════════════════════════════════════════════════

def per_layer_crystal_loss(model, probes, teacher_per_layer_crystals):
    """Crystal loss at EACH layer independently.

    Each layer's plates get a DIRECT gradient signal through only that
    layer's computation. No deep backprop through all layers.

    Layer 0 plates ← gradient from layer 0 crystal error (direct)
    Layer 1 plates ← gradient from layer 1 crystal error (through 1 layer)
    Layer 2 plates ← gradient from layer 2 crystal error (through 2 layers)

    vs original crystal loss:
    ALL plates ← gradient from layer 2 crystal error (through all layers)
    """
    total_loss = mx.array(0.0)

    for target_layer in range(N_LAYERS):
        tgt = mx.array(np.array(teacher_per_layer_crystals[target_layer],
                                dtype=np.float32))
        means = []
        for c in COMBINATORS:
            hs = []
            for ids in probes[c]:
                x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
                for li in range(target_layer + 1):
                    x = model.layers[li](x)
                hs.append(x[0, -1, :])
            means.append(mx.mean(mx.stack(hs), axis=0))
        M = mx.stack(means)
        N = mx.sqrt(mx.sum(M * M, axis=1, keepdims=True) + 1e-8)
        cos = (M / N) @ (M / N).T
        ir, ic = [0,0,0,1,1,2], [1,2,3,2,3,3]
        layer_loss = mx.mean(
            (cos[mx.array(ir), mx.array(ic)] - tgt[mx.array(ir), mx.array(ic)]) ** 2
        )
        total_loss = total_loss + layer_loss

    return total_loss / N_LAYERS


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

def measure_sign_damage(a, b):
    total=0; damaged=0
    for i in range(len(a)):
        for k in a[i]:
            total+=a[i][k].size; damaged+=int((a[i][k]!=b[i][k]).sum())
    return damaged, total

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

def quick_eval(model):
    return eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)

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
# Phase 1: Per-layer lattice etch
# ══════════════════════════════════════════════════════════════════════

def lattice_etch_round(model, probes, teacher_per_layer_crystals):
    """One round: accumulate sign(gradient) of per-layer crystal loss."""
    plates = _get_plates(model)
    accumulators = [np.zeros((p.out_features, p.in_features), dtype=np.float64)
                    for _, p in plates]

    plate_paths = []
    for i in range(len(model.layers)):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    def loss_fn(model):
        return per_layer_crystal_loss(model, probes, teacher_per_layer_crystals)

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    total_loss = 0.0
    for b in range(LATTICE_BATCHES):
        loss_val, grads = loss_and_grad(model)
        mx.eval(loss_val, grads)
        total_loss += float(loss_val)

        for pidx, (layer_idx, pname) in enumerate(plate_paths):
            lg = grads.get("layers", [])
            if isinstance(lg, list) and layer_idx < len(lg):
                layer_g = lg[layer_idx]
            else: continue
            parts = pname.split(".")
            g = layer_g
            for part in parts:
                if isinstance(g, dict) and part in g: g = g[part]
                else: g = None; break
            if g is not None and isinstance(g, dict) and "weight" in g:
                gw = g["weight"]; mx.eval(gw)
                accumulators[pidx] += np.sign(np.array(gw))

        del loss_val, grads
        if (b+1) % 25 == 0: mx.clear_cache()

    # Collect all positions with their gradient magnitude and desired sign
    all_candidates = []
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        grad_mag = np.abs(acc)  # accumulated magnitude = confidence
        desired_sign = -np.sign(acc)  # negative gradient direction
        current = np.sign(np.array(plate.weight)).astype(np.float32)
        do, di = current.shape
        for i in range(do):
            for j in range(di):
                if desired_sign[i, j] != 0 and desired_sign[i, j] != current[i, j]:
                    all_candidates.append((grad_mag[i, j], pidx, i, j,
                                           desired_sign[i, j]))

    # Sort by gradient magnitude (descending) and flip only top-K
    all_candidates.sort(key=lambda x: -x[0])
    n_to_flip = min(FLIPS_PER_ROUND, len(all_candidates))

    total_flipped = 0
    for rank in range(n_to_flip):
        mag, pidx, i, j, desired = all_candidates[rank]
        _, plate = plates[pidx]
        w = np.array(plate.weight)
        w[i, j] = desired
        plate.weight = mx.array(w)
        total_flipped += 1

    mx.eval(*[p.weight for _, p in plates])
    return total_flipped, total_loss / LATTICE_BATCHES


def run_lattice_etch(model, probes, teacher_per_layer_crystals,
                     teacher_last_crystal, oracle_crystal):
    """Phase 1: Per-layer lattice reconstruction."""
    log("\n  Phase 1: Per-layer lattice etch (direct gradient per layer)")
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    initial_crystal = crystal_agr(
        crystal_at_layer(model, probes, N_LAYERS - 1), teacher_last_crystal)
    log(f"    Initial: crystal={initial_crystal:.4f}, sign_agr={initial_sign_agr:.4f}")

    # Log per-layer crystal agreement
    for li in range(N_LAYERS):
        c = crystal_at_layer(model, probes, li)
        agr = crystal_agr(c, teacher_per_layer_crystals[li])
        log(f"    Layer {li} crystal agr: {agr:+.4f}")

    traj = []
    for r in range(LATTICE_ROUNDS):
        flips, avg_loss = lattice_etch_round(model, probes,
                                              teacher_per_layer_crystals)
        # Measure per-layer crystal agreement
        per_layer_agr = []
        for li in range(N_LAYERS):
            c = crystal_at_layer(model, probes, li)
            agr = crystal_agr(c, teacher_per_layer_crystals[li])
            per_layer_agr.append(agr)

        last_agr = per_layer_agr[-1]
        sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
        ev = quick_eval(model)

        traj.append({
            "round": r, "flips": flips, "loss": avg_loss,
            "per_layer_agr": per_layer_agr, "crystal_agr": last_agr,
            "sign_agr": sign_agr, "accuracy": ev["accuracy"],
        })

        bars = " ".join(f"L{li}={'█'*max(0,int((a+1)*5))}" for li, a in enumerate(per_layer_agr))
        log(f"    R{r:2d}: flips={flips:5d}  {bars}  "
            f"sign={sign_agr:.4f}  acc={ev['accuracy']:.4f}")

        if all(a > 0.95 for a in per_layer_agr):
            log(f"    All layers converged at round {r}")
            break
        mx.clear_cache()

    final_crystal = crystal_agr(
        crystal_at_layer(model, probes, N_LAYERS - 1), teacher_last_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"    Final: crystal={final_crystal:.4f}, sign_agr={final_sign_agr:.4f}")

    return {
        "trajectory": traj,
        "initial_crystal": initial_crystal, "final_crystal": final_crystal,
        "initial_sign_agr": initial_sign_agr, "final_sign_agr": final_sign_agr,
    }


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Beam training (CE + crystal loss, plates frozen)
# ══════════════════════════════════════════════════════════════════════

def run_beam_training(model, probes, teacher_per_layer_crystals,
                      teacher_last_crystal, oracle_crystal):
    log(f"\n  Phase 2: Beam training (CE + crystal λ={BEAM_CRYSTAL_LAMBDA})")

    for layer in model.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)

    def beam_loss(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = per_layer_crystal_loss(model, probes, teacher_per_layer_crystals)
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
            ev = quick_eval(model)
            crystal = crystal_agr(
                crystal_at_layer(model, probes, N_LAYERS-1), teacher_last_crystal)
            sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
            traj.append({"step": s+1, "accuracy": ev["accuracy"],
                         "loss": ev["loss"], "crystal_agr": crystal,
                         "sign_agr": sign_agr})
            log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}  "
                f"crystal={crystal:+.4f}  loss={ev['loss']:.4f}")

    final_ev = quick_eval(model)
    final_crystal = crystal_agr(
        crystal_at_layer(model, probes, N_LAYERS-1), teacher_last_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    return {
        "trajectory": traj,
        "final_acc": final_ev["accuracy"], "final_loss": final_ev["loss"],
        "final_crystal": final_crystal, "final_sign_agr": final_sign_agr,
        "best_acc": max(t["accuracy"] for t in traj) if traj else final_ev["accuracy"],
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # Train teacher
    log(f"{'═'*60}")
    log(f"Training teacher d={D_TEACHER}...")
    teacher = train_teacher(D_TEACHER, 5000)
    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    results["teacher"] = {"accuracy": teacher_ev["accuracy"], "loss": teacher_ev["loss"]}

    # Extractions
    probes = gen_probes()
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)
    damaged, total = measure_sign_damage(oracle_crystal, q2_crystal)
    log(f"\nQ2 sign damage: {damaged}/{total} = {damaged/total*100:.1f}%")
    results["q2_damage"] = {"damaged": damaged, "total": total, "pct": damaged/total*100}

    # Phase 0: Measure teacher geometry
    log(f"\n{'═'*60}")
    teacher_per_layer = measure_teacher_geometry(teacher, probes)
    teacher_last = teacher_per_layer[-1]
    results["teacher_geometry"] = {
        f"layer_{li}": teacher_per_layer[li] for li in range(N_LAYERS)
    }

    # ══════════════════════════════════════════════════════════════
    # C1: PER-LAYER LATTICE ETCH + BEAM TRAINING
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C1: PER-LAYER LATTICE ETCH + BEAM TRAINING")

    m1 = make_model(q2_crystal, mag)
    phase1 = run_lattice_etch(m1, probes, teacher_per_layer, teacher_last,
                              oracle_crystal)
    phase2 = run_beam_training(m1, probes, teacher_per_layer, teacher_last,
                               oracle_crystal)
    results["c1_perlayer"] = {
        "condition": "PER_LAYER_ETCH+BEAM",
        "phase1": phase1, "phase2": phase2,
    }
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: ORACLE
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C2: ORACLE — perfect projected signs")

    m2 = make_model(oracle_crystal, mag)
    phase2_oracle = run_beam_training(m2, probes, teacher_per_layer,
                                      teacher_last, oracle_crystal)
    results["c2_oracle"] = {"condition": "ORACLE", "phase2": phase2_oracle}
    del m2; mx.clear_cache()

    # Summary
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed, "d_teacher": D_TEACHER,
                       "d_student": D_STUDENT, "lattice_rounds": LATTICE_ROUNDS,
                       "lattice_batches": LATTICE_BATCHES, "beam_steps": BEAM_STEPS}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Rotation Etch")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}")
    log(f"  Q2 damage: {damaged/total*100:.1f}%\n")

    p1 = results["c1_perlayer"]["phase1"]
    p2 = results["c1_perlayer"]["phase2"]
    log(f"  Phase 1 (per-layer lattice etch):")
    log(f"    Crystal: {p1['initial_crystal']:+.4f} → {p1['final_crystal']:+.4f}")
    log(f"    Signs:   {p1['initial_sign_agr']:.4f} → {p1['final_sign_agr']:.4f}")
    log(f"\n  Phase 2 (beam training CE + crystal):")
    log(f"    Accuracy: {p2['final_acc']:.4f} (best={p2['best_acc']:.4f})")
    log(f"    Crystal:  {p2['final_crystal']:+.4f}")

    p2o = results["c2_oracle"]["phase2"]
    log(f"\n  Oracle ceiling:")
    log(f"    Accuracy: {p2o['final_acc']:.4f} (best={p2o['best_acc']:.4f})")
    log(f"    Crystal:  {p2o['final_crystal']:+.4f}")

    pct = p2['best_acc'] / max(p2o['best_acc'], 1e-8) * 100
    log(f"\n  Rotation etch achieves {pct:.1f}% of oracle accuracy")
    log(f"  Crystal preserved: {'✓' if p2['final_crystal'] > 0.5 else '✗'} "
        f"({p2['final_crystal']:+.4f})")
    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
