"""Q2 Computed Beam — Replace GD with geometry.

GD is blind search with gradient hints. We know the full geometry:
rotation angles, CCA crossings, crystal lattice, magnitude spectrum.
Can we COMPUTE the beam instead of SEARCHING for it?

Spectrum of approaches from zero training to full training:

  A: TEACHER_BEAM   — teacher magnitudes, zero adjustment, zero training
  B: DAMPED_BEAM    — attenuate flipped dimensions by CCA loading, zero training
  C: NEWTON_BEAM    — one-shot Jacobian solve against per-layer crystal, ~zero training
  D: FEW_STEP       — 10 steps of beam GD (not 3000)
  E: FULL_GD        — 3000 steps (our current best, the baseline)

If A-D approach E's performance, we've replaced optimization with computation.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_computed_beam_exp.py

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

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-computed-beam"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
EVAL_BATCHES = 30; BEAM_CRYSTAL_LAMBDA = 0.5
COMBINATORS = ["K", "I", "B", "C"]


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
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for li in range(target_layer + 1): x = model.layers[li](x)
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

def per_layer_crystal_loss(model, probes, teacher_per_layer):
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
        total = total + mx.mean((cos[mx.array(ir),mx.array(ic)] - tgt[mx.array(ir),mx.array(ic)])**2)
    return total / N_LAYERS


# ══════════════════════════════════════════════════════════════════════
# Extraction
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

def make_model(crystal, mag):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m

def set_beams(model, mag):
    for i,l in enumerate(model.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(model.parameters())

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
# Evaluation helper
# ══════════════════════════════════════════════════════════════════════

def eval_condition(model, probes, teacher_per_layer, label):
    ev = eval_model(model, np.random.RandomState(999),
                    n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    crystals = []
    for li in range(N_LAYERS):
        c = crystal_at_layer(model, probes, li)
        crystals.append(crystal_agr(c, teacher_per_layer[li]))
    last_crystal = crystals[-1]
    log(f"  {label:<20s}: acc={ev['accuracy']:.4f}  "
        f"crystal=[{', '.join(f'{c:+.3f}' for c in crystals)}]  "
        f"loss={ev['loss']:.4f}")
    return {"accuracy": ev["accuracy"], "loss": ev["loss"],
            "per_layer_crystal": crystals, "crystal": last_crystal}


# ══════════════════════════════════════════════════════════════════════
# METHOD A: Teacher beam — zero adjustment
# ══════════════════════════════════════════════════════════════════════

def method_teacher_beam(q2_crystal, mag, probes, teacher_per_layer):
    """Just use teacher magnitudes. No adjustment. Zero training."""
    log("\n  Method A: TEACHER_BEAM (zero training)")
    m = make_model(q2_crystal, mag)
    result = eval_condition(m, probes, teacher_per_layer, "TEACHER_BEAM")
    del m; mx.clear_cache()
    return result


# ══════════════════════════════════════════════════════════════════════
# METHOD B: Damped beam — attenuate flipped dimensions
# ══════════════════════════════════════════════════════════════════════

def method_damped_beam(q2_crystal, oracle_crystal, mag, probes,
                       teacher_per_layer, damp_factor=0.3):
    """Attenuate beam at dimensions where Q2 flipped the sign.

    A flipped sign reverses dimension d's contribution. Reducing the
    beam at d reduces the damage. damp_factor controls how much:
      0.0 = zero out flipped dims (aggressive)
      1.0 = no damping (same as teacher beam)
    """
    log(f"\n  Method B: DAMPED_BEAM (damp={damp_factor}, zero training)")
    damped_mag = []
    total_damped = 0
    total_dims = 0

    for li in range(N_LAYERS):
        lm = {}
        for pn in ["k", "v", "o", "ffn"]:
            teacher_m = mag[li][pn].copy()
            oracle_s = oracle_crystal[li][pn]
            q2_s = q2_crystal[li][pn]

            # Per-dimension: is any sign in this row flipped?
            row_damage = np.any(oracle_s != q2_s, axis=1)  # (ds,)
            n_damaged = int(row_damage.sum())
            total_damped += n_damaged
            total_dims += len(row_damage)

            # Damp damaged dimensions
            damped = teacher_m.copy()
            damped[row_damage] *= damp_factor
            lm[pn] = damped
        damped_mag.append(lm)

    log(f"    Damped {total_damped}/{total_dims} dimensions ({total_damped/total_dims*100:.1f}%)")

    m = make_model(q2_crystal, damped_mag)
    result = eval_condition(m, probes, teacher_per_layer, "DAMPED_BEAM")
    del m; mx.clear_cache()
    return result


# ══════════════════════════════════════════════════════════════════════
# METHOD C: Newton beam — one-shot gradient solve
# ══════════════════════════════════════════════════════════════════════

def method_newton_beam(q2_crystal, mag, probes, teacher_per_layer,
                       n_newton_steps=5):
    """Compute beam correction via gradient descent on crystal loss ONLY.

    Not 3000 steps of CE+crystal. Just a few steps of pure crystal loss
    to align the geometry, then evaluate on CE.

    This is Newton-like: the crystal loss is low-dimensional (18 targets)
    and near-quadratic, so a few steps should converge.
    """
    log(f"\n  Method C: NEWTON_BEAM ({n_newton_steps} crystal-only steps)")
    m = make_model(q2_crystal, mag)

    # Freeze plates
    for layer in m.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    # Large learning rate for few-step convergence
    opt = optim.Adam(learning_rate=0.01)

    def crystal_only_loss(model):
        return per_layer_crystal_loss(model, probes, teacher_per_layer)

    lag = nn.value_and_grad(m, crystal_only_loss)

    for s in range(n_newton_steps):
        lv, gr = lag(m)
        mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m))
        mx.eval(m.parameters())
        del lv, gr
        if (s + 1) % 5 == 0:
            crystals = []
            for li in range(N_LAYERS):
                c = crystal_at_layer(m, probes, li)
                crystals.append(crystal_agr(c, teacher_per_layer[li]))
            log(f"    Step {s+1}: crystal=[{', '.join(f'{c:+.3f}' for c in crystals)}]")

    result = eval_condition(m, probes, teacher_per_layer, "NEWTON_BEAM")
    del m; mx.clear_cache()
    return result


# ══════════════════════════════════════════════════════════════════════
# METHOD D: Few-step GD (10 steps of CE + crystal)
# ══════════════════════════════════════════════════════════════════════

def method_few_step(q2_crystal, mag, probes, teacher_per_layer, n_steps=10):
    """Just 10 steps of beam training. Compare with 3000."""
    log(f"\n  Method D: FEW_STEP ({n_steps} steps of CE+crystal)")
    m = make_model(q2_crystal, mag)

    for layer in m.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def beam_loss(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = per_layer_crystal_loss(model, probes, teacher_per_layer)
        return ce + BEAM_CRYSTAL_LAMBDA * cl

    lag = nn.value_and_grad(m, beam_loss)
    for s in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m))
        mx.eval(m.parameters()); del lv, gr

    result = eval_condition(m, probes, teacher_per_layer, f"FEW_STEP_{n_steps}")
    del m; mx.clear_cache()
    return result


# ══════════════════════════════════════════════════════════════════════
# METHOD E: Full GD (3000 steps — the baseline)
# ══════════════════════════════════════════════════════════════════════

def method_full_gd(q2_crystal, mag, probes, teacher_per_layer, n_steps=3000):
    """3000 steps of CE + crystal loss. Our current best."""
    log(f"\n  Method E: FULL_GD ({n_steps} steps)")
    m = make_model(q2_crystal, mag)

    for layer in m.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    rng = np.random.RandomState(42)

    def beam_loss(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = per_layer_crystal_loss(model, probes, teacher_per_layer)
        return ce + BEAM_CRYSTAL_LAMBDA * cl

    lag = nn.value_and_grad(m, beam_loss)
    best_acc = 0
    for s in range(n_steps):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m))
        mx.eval(m.parameters()); del lv, gr
        if (s+1) % 50 == 0: mx.clear_cache()
        if (s+1) % 1000 == 0:
            ev = eval_model(m, np.random.RandomState(999),
                            n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
            best_acc = max(best_acc, ev["accuracy"])
            log(f"    Step {s+1}: acc={ev['accuracy']:.4f}")

    result = eval_condition(m, probes, teacher_per_layer, "FULL_GD")
    result["best_acc"] = max(best_acc, result["accuracy"])
    del m; mx.clear_cache()
    return result


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

    teacher_per_layer = []
    for li in range(N_LAYERS):
        teacher_per_layer.append(crystal_at_layer(teacher, probes, li))

    from mini_holo_crystal import crystal_similarity
    log(f"  Q2 sign agreement: {crystal_similarity(oracle_crystal, q2_crystal):.4f}")

    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SPECTRUM: zero training → full training")
    log(f"{'═'*60}")

    results["a_teacher_beam"] = method_teacher_beam(
        q2_crystal, mag, probes, teacher_per_layer)

    results["b_damped_0.3"] = method_damped_beam(
        q2_crystal, oracle_crystal, mag, probes, teacher_per_layer, 0.3)

    results["b_damped_0.1"] = method_damped_beam(
        q2_crystal, oracle_crystal, mag, probes, teacher_per_layer, 0.1)

    results["b_damped_0.0"] = method_damped_beam(
        q2_crystal, oracle_crystal, mag, probes, teacher_per_layer, 0.0)

    results["c_newton_5"] = method_newton_beam(
        q2_crystal, mag, probes, teacher_per_layer, n_newton_steps=5)

    results["c_newton_20"] = method_newton_beam(
        q2_crystal, mag, probes, teacher_per_layer, n_newton_steps=20)

    results["d_few_10"] = method_few_step(
        q2_crystal, mag, probes, teacher_per_layer, n_steps=10)

    results["d_few_100"] = method_few_step(
        q2_crystal, mag, probes, teacher_per_layer, n_steps=100)

    results["d_few_500"] = method_few_step(
        q2_crystal, mag, probes, teacher_per_layer, n_steps=500)

    results["e_full_3000"] = method_full_gd(
        q2_crystal, mag, probes, teacher_per_layer, n_steps=3000)

    # Oracle baseline
    log(f"\n  Oracle baselines:")
    m_oracle = make_model(oracle_crystal, mag)
    results["oracle_no_train"] = eval_condition(
        m_oracle, probes, teacher_per_layer, "ORACLE_NO_TRAIN")
    del m_oracle; mx.clear_cache()

    results["oracle_full_gd"] = method_full_gd(
        oracle_crystal, mag, probes, teacher_per_layer, n_steps=3000)

    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Computed Beam")
    log(f"{'═'*60}")
    log(f"  {'Method':<22s} {'Steps':>5s} {'Acc':>6s} {'Crystal':>8s}")
    log(f"  {'-'*22} {'-'*5} {'-'*6} {'-'*8}")

    for key, label, steps in [
        ("a_teacher_beam", "Teacher beam", "0"),
        ("b_damped_0.3", "Damped 0.3", "0"),
        ("b_damped_0.1", "Damped 0.1", "0"),
        ("b_damped_0.0", "Damped 0.0 (zero)", "0"),
        ("c_newton_5", "Newton 5-step", "5"),
        ("c_newton_20", "Newton 20-step", "20"),
        ("d_few_10", "CE+crystal 10", "10"),
        ("d_few_100", "CE+crystal 100", "100"),
        ("d_few_500", "CE+crystal 500", "500"),
        ("e_full_3000", "CE+crystal 3000", "3000"),
        ("oracle_no_train", "Oracle (no train)", "0"),
        ("oracle_full_gd", "Oracle+GD 3000", "3000"),
    ]:
        r = results[key]
        acc = r.get("best_acc", r["accuracy"])
        cry = r["crystal"]
        log(f"  {label:<22s} {steps:>5s} {acc:6.4f} {cry:+8.4f}")

    full_acc = results["e_full_3000"].get("best_acc", results["e_full_3000"]["accuracy"])
    for key, label in [("a_teacher_beam", "Teacher beam"),
                       ("c_newton_20", "Newton 20"),
                       ("d_few_100", "CE+crystal 100")]:
        r = results[key]
        acc = r.get("best_acc", r["accuracy"])
        pct = acc / max(full_acc, 1e-8) * 100
        log(f"\n  {label} vs Full GD: {pct:.1f}% ({acc:.4f} vs {full_acc:.4f})")

    log(f"\n  Results saved to {out_path} ({elapsed:.0f}s)")


if __name__ == "__main__":
    main()
