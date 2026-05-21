"""Q2 Circuit Fix — Surgical correction of routing + output circuits, then beam melt.

Session 126 findings:
  - Rotation etch + beam training BEATS oracle (104.8% accuracy, 0.967 crystal)
  - FFN routing and output circuits are completely separate (0 overlap)
  - Q2 damage at circuit dims: cos_sim = -0.21 (routing) to -0.47 (output)
  - L2 output circuit most damaged — the last beta-reduction is nearly inverted

Protocol:
  Phase 0: Identify circuits (routing + output dims per layer)
  Phase 1: Surgical fix — copy oracle signs at circuit dimensions only
  Phase 2: Beam training (CE + per-layer crystal loss, plates frozen)

No gradient etch. No iterative search. Just fix the entrance (routing)
and exit (output) by hand, then let the beam melt handle everything else.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_circuit_fix_exp.py

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
    generate_batch, _get_plates,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-circuit-fix"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
BEAM_STEPS = 3000; BEAM_CRYSTAL_LAMBDA = 0.5; EVAL_BATCHES = 30
COMBINATORS = ["K", "I", "B", "C"]
CIRCUIT_TOP_K = 20  # dims per circuit


def gen_probes(n=50, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]; fs = ["f","g","h","p","q"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n*5):
            if len(ps) >= n: break
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


def find_combinator_position(ids):
    comb_ids = {TOK2ID.get(c) for c in ["K","I","B","C"] if c in TOK2ID}
    for i, tok in enumerate(ids):
        if tok in comb_ids: return i
    return 1

def find_eq_position(ids):
    for i, tok in enumerate(ids):
        if tok == EQ_ID: return i
    return len([t for t in ids if t != PAD_ID]) - 1


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════

def crystal_at_layer(model, probes, target_layer):
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
# FFN circuit identification
# ══════════════════════════════════════════════════════════════════════

def capture_ffn_at_pos(model, input_ids, pos):
    """Capture FFN output at a specific position."""
    x = model.embed(mx.array(np.array([input_ids], dtype=np.int32)))
    mx.eval(x)
    per_layer = []
    for li, layer in enumerate(model.layers):
        attn_out = layer.attn(layer.attn_norm(x))
        h_mid = x + attn_out
        ffn_input = layer.ffn_norm(h_mid)
        if hasattr(layer, 'ffn'):
            ffn_out = layer.ffn(ffn_input)
        elif hasattr(layer, 'ffn_plate'):
            ffn_out = layer.ffn_plate(ffn_input) * layer.ffn_scale + layer.ffn_bias
        else:
            ffn_out = mx.zeros_like(ffn_input)
        mx.eval(ffn_out)
        per_layer.append(np.array(ffn_out[0, pos, :]).copy())
        x = h_mid + ffn_out
    return per_layer


def identify_circuits(model, probes):
    """Find top-K routing and output dims per layer."""
    log("  Identifying routing + output circuits...")

    routing_acts = {li: [] for li in range(N_LAYERS)}
    output_acts = {li: [] for li in range(N_LAYERS)}

    for c in ["K", "B", "C"]:  # routing = K/B/C shared
        for ids in probes[c]:
            cpos = find_combinator_position(ids)
            epos = find_eq_position(ids)
            r = capture_ffn_at_pos(model, ids, cpos)
            o = capture_ffn_at_pos(model, ids, epos)
            for li in range(N_LAYERS):
                routing_acts[li].append(r[li])
                output_acts[li].append(o[li])

    # Also add I to output (WHNF fires for all combinators)
    for ids in probes["I"]:
        epos = find_eq_position(ids)
        o = capture_ffn_at_pos(model, ids, epos)
        for li in range(N_LAYERS):
            output_acts[li].append(o[li])

    circuits = {}
    for li in range(N_LAYERS):
        r_mean = np.mean(np.abs(np.array(routing_acts[li])), axis=0)
        o_mean = np.mean(np.abs(np.array(output_acts[li])), axis=0)

        r_spec = r_mean / (o_mean + 1e-10)
        o_spec = o_mean / (r_mean + 1e-10)

        routing_dims = np.argsort(r_spec)[-CIRCUIT_TOP_K:].tolist()
        output_dims = np.argsort(o_spec)[-CIRCUIT_TOP_K:].tolist()

        circuits[li] = {"routing": routing_dims, "output": output_dims}
        log(f"    L{li}: routing={sorted(routing_dims[:5])}... "
            f"output={sorted(output_dims[:5])}...")

    return circuits


# ══════════════════════════════════════════════════════════════════════
# Surgical circuit fix
# ══════════════════════════════════════════════════════════════════════

def surgical_circuit_fix(model, oracle_crystal, circuits):
    """Fix plate signs at circuit dimensions by copying from oracle.

    For each circuit dimension d in each layer:
      Copy the entire ROW d of oracle plates into student plates.
      (Row d of the FFN plate controls dimension d's output.)

    Returns number of signs changed.
    """
    log("  Surgical circuit fix (copy oracle signs at circuit dims)...")
    total_changed = 0

    for li, layer in enumerate(model.layers):
        circuit_dims = set(circuits[li]["routing"] + circuits[li]["output"])

        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            current = np.array(plate.weight)
            oracle = oracle_crystal[li][pn]

            for d in circuit_dims:
                if d < current.shape[0]:
                    changed = int((current[d, :] != oracle[d, :]).sum())
                    current[d, :] = oracle[d, :]
                    total_changed += changed

            plate.weight = mx.array(current)

        mx.eval(layer.parameters())

    log(f"    Fixed {total_changed} signs across {sum(len(circuits[li]['routing']) + len(circuits[li]['output']) for li in range(N_LAYERS))} circuit dims")
    return total_changed


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
# Beam training (same as rotation etch)
# ══════════════════════════════════════════════════════════════════════

def run_beam_training(model, probes, teacher_per_layer, oracle_crystal, label):
    log(f"\n  Beam training [{label}] (CE + crystal λ={BEAM_CRYSTAL_LAMBDA})")
    teacher_last = teacher_per_layer[-1]

    for layer in model.layers:
        layer.attn.k_plate.freeze(); layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze(); layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    def beam_loss(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        cl = per_layer_crystal_loss(model, probes, teacher_per_layer)
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
            crystal = crystal_agr(crystal_at_layer(model, probes, N_LAYERS-1),
                                  teacher_last)
            sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
            traj.append({"step": s+1, "accuracy": ev["accuracy"],
                         "loss": ev["loss"], "crystal_agr": crystal})
            log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}  "
                f"crystal={crystal:+.4f}  loss={ev['loss']:.4f}")

    final_ev = eval_model(model, np.random.RandomState(999),
                          n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)
    final_crystal = crystal_agr(crystal_at_layer(model, probes, N_LAYERS-1),
                                teacher_last)
    final_sign = sign_agreement_with_oracle(model, oracle_crystal)

    return {
        "trajectory": traj,
        "final_acc": final_ev["accuracy"], "final_loss": final_ev["loss"],
        "final_crystal": final_crystal, "final_sign_agr": final_sign,
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
    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)

    probes = gen_probes(n=50)
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)

    from mini_holo_crystal import crystal_similarity
    q2_sim = crystal_similarity(oracle_crystal, q2_crystal)
    log(f"  Q2 sign agreement: {q2_sim:.4f}")

    # Teacher per-layer crystals
    teacher_per_layer = []
    for li in range(N_LAYERS):
        teacher_per_layer.append(crystal_at_layer(teacher, probes, li))

    # ══════════════════════════════════════════════════════════════
    # Phase 0: Identify circuits using oracle student
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("Phase 0: Identify routing + output circuits")
    oracle_model = make_model(oracle_crystal, mag)
    circuits = identify_circuits(oracle_model, probes)
    del oracle_model; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C1: CIRCUIT FIX + BEAM (THE TEST)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C1: CIRCUIT FIX + BEAM TRAINING")

    m1 = make_model(q2_crystal, mag)
    pre_sign = sign_agreement_with_oracle(m1, oracle_crystal)
    pre_crystal = crystal_agr(crystal_at_layer(m1, probes, N_LAYERS-1),
                              teacher_per_layer[-1])
    log(f"  Before fix: sign={pre_sign:.4f}, crystal={pre_crystal:+.4f}")

    n_fixed = surgical_circuit_fix(m1, oracle_crystal, circuits)

    post_sign = sign_agreement_with_oracle(m1, oracle_crystal)
    post_crystal = crystal_agr(crystal_at_layer(m1, probes, N_LAYERS-1),
                               teacher_per_layer[-1])
    log(f"  After fix:  sign={post_sign:.4f}, crystal={post_crystal:+.4f}")
    log(f"  Signs fixed: {n_fixed} ({n_fixed/196608*100:.2f}% of plates)")

    c1_beam = run_beam_training(m1, probes, teacher_per_layer, oracle_crystal,
                                "CIRCUIT_FIX+BEAM")
    results["c1_circuit_fix"] = {
        "condition": "CIRCUIT_FIX+BEAM",
        "pre_sign": pre_sign, "post_sign": post_sign,
        "pre_crystal": pre_crystal, "post_crystal": post_crystal,
        "n_fixed": n_fixed, "circuits": {str(k): v for k, v in circuits.items()},
        "beam": c1_beam,
    }
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: Q2 RAW + BEAM (no fix — baseline)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C2: Q2 RAW + BEAM (no circuit fix)")

    m2 = make_model(q2_crystal, mag)
    c2_beam = run_beam_training(m2, probes, teacher_per_layer, oracle_crystal,
                                "Q2_RAW+BEAM")
    results["c2_q2_raw"] = {"condition": "Q2_RAW+BEAM", "beam": c2_beam}
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C3: ORACLE + BEAM (ceiling)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("C3: ORACLE + BEAM (ceiling)")

    m3 = make_model(oracle_crystal, mag)
    c3_beam = run_beam_training(m3, probes, teacher_per_layer, oracle_crystal,
                                "ORACLE+BEAM")
    results["c3_oracle"] = {"condition": "ORACLE+BEAM", "beam": c3_beam}
    del m3; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {"elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Circuit Fix")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Q2 damage: {(1-q2_sim)*100:.1f}% signs wrong")
    log(f"  Circuit fix: {n_fixed} signs ({n_fixed/196608*100:.2f}%)\n")

    for key, short in [("c1_circuit_fix", "Circuit+Beam"),
                       ("c2_q2_raw", "Q2 Raw+Beam"),
                       ("c3_oracle", "Oracle+Beam")]:
        b = results[key].get("beam", results[key])
        log(f"  {short:<16s}: acc={b['best_acc']:.4f}  crystal={b['final_crystal']:+.4f}")

    c1b = results["c1_circuit_fix"]["beam"]["best_acc"]
    c2b = results["c2_q2_raw"]["beam"]["best_acc"]
    c3b = results["c3_oracle"]["beam"]["best_acc"]
    log(f"\n  Circuit fix vs Q2 raw: {'✓ BETTER' if c1b > c2b else '✗ WORSE'} "
        f"({c1b:.4f} vs {c2b:.4f})")
    log(f"  Circuit fix vs oracle: {c1b/max(c3b,1e-8)*100:.1f}% of ceiling")
    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
