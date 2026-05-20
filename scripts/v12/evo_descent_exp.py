"""Evolutionary Descent — Co-evolve beams (GD) and plates (ternary bit flips).

Session 125. GD can't flip ternary signs (0 barrier). Evolution can.
Use GD for the continuous domain (beams), evolution for the discrete
domain (plates). The beam's delta guides where to flip. The crystal
gates which flips are accepted.

Protocol:
  For N co-evolution rounds:
    1. GD PHASE: train beams with plates frozen (1500 steps)
    2. DELTA: extract beam scales - initial magnitudes → mutation map
    3. EVO PHASE: try flipping top-K highest-|delta| positions
       - For each candidate: flip, eval fitness, crystal check
       - Accept if fitness improves AND crystal preserved
    4. Apply accepted flips → new plate configuration
    5. Reset beam to initial magnitudes (force beam to re-adapt)

Conditions:
  1. LOOM_MAG baseline (no evolution, beams only)
  2. EVO_COEVOLVE (GD beams + evolutionary plate flips)
  3. RANDOM_FLIPS (random mutations, no delta guidance — control)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/evo_descent_exp.py 2>&1 | tee results/evo-descent/run.log

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
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    TernaryLinear, Comb, Var, App,
    GDModel, HoloModel,
    count_holo_params,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
)

from mini_holo_crystal import extract_crystal, write_crystal_to_model


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "evo-descent"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_COEVO_ROUNDS = 8
GD_STEPS_PER_ROUND = 1500
N_CANDIDATES_PER_ROUND = 200  # flip candidates to try per round
EVAL_BATCHES = 30
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4
CRYSTAL_THRESHOLD = -0.05  # max crystal degradation per flip
COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]; fs = ["f","g","h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n*3):
            if len(ps)>=n: break
            v1,v2=Var(rng.choice(vs)),Var(rng.choice(vs))
            f1,f2=Var(rng.choice(fs)),Var(rng.choice(fs))
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


def measure_crystal(model, probes):
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids],dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(np.array(x[0,-1,:]))
        means.append(np.mean(hs, axis=0))
    M = np.array(means)
    N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
    return (M/N @ (M/N).T).tolist()


def crystal_agr(s, t):
    A,B = np.array(s), np.array(t)
    idx = np.triu_indices(4, k=1)
    a,b = A[idx]-A[idx].mean(), B[idx]-B[idx].mean()
    d = np.sqrt(np.sum(a**2))*np.sqrt(np.sum(b**2))
    return float(np.sum(a*b)/d) if d>1e-10 else 0.0


# ══════════════════════════════════════════════════════════════════════
# Extraction (reused)
# ══════════════════════════════════════════════════════════════════════

def cca_loom_extract(teacher, ds):
    cr = []
    for li,layer in enumerate(teacher.layers):
        Wk,Wf=np.array(layer.attn.k_proj.weight),np.array(layer.ffn.weight)
        _,_,Vta=np.linalg.svd(Wk,full_matrices=False)
        _,_,Vtb=np.linalg.svd(Wf,full_matrices=False)
        k=min(ds,Vta.shape[0],Vtb.shape[0])
        A,B=Vta[:k,:].T,Vtb[:k,:].T
        Qa,_=np.linalg.qr(A); Qb,_=np.linalg.qr(B)
        U,S,Vt=np.linalg.svd(Qa.T@Qb,full_matrices=False)
        ang=np.degrees(np.arccos(np.clip(S,0,1)))
        da,db=Qa@U,Qb@Vt.T; sh=da+db
        sh=sh/np.maximum(np.linalg.norm(sh,axis=0,keepdims=True),1e-8)
        ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); cm=(ang>=35)&(ang<72)
            if cm.sum()>=2:
                de=np.sum(sh[:,cm]**2,axis=1)
                wt=np.sign(W)*(1.0+de/(de.max()+1e-10))[np.newaxis,:]
            else: wt=np.sign(W)
            _,Sv,Vtv=np.linalg.svd(W,full_matrices=False); P=Vtv[:ds,:]
            s=np.sign(P@wt@P.T).astype(np.float32)
            z=s==0
            if z.any(): s[z]=np.random.RandomState(42+li).choice([-1.,1.],size=int(z.sum()))
            ls[nm]=s
        cr.append(ls)
    return cr

def extract_mag(teacher, ds):
    t=[]
    for layer in teacher.layers:
        lm={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]; lm[nm]=np.sqrt(np.mean((P@W@P.T)**2,axis=1)).astype(np.float32)
        t.append(lm)
    return t


# ══════════════════════════════════════════════════════════════════════
# Plate manipulation
# ══════════════════════════════════════════════════════════════════════

def get_all_plate_positions(model):
    """Get list of (layer_idx, plate_name, row, col) for all plate positions."""
    positions = []
    for li, layer in enumerate(model.layers):
        for pname in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pname}_plate") if pname != "ffn" else layer.ffn_plate
            d_out, d_in = plate.weight.shape
            for i in range(d_out):
                for j in range(d_in):
                    positions.append((li, pname, i, j))
    return positions


def get_plate_value(model, li, pname, i, j):
    plate = getattr(model.layers[li].attn, f"{pname}_plate") if pname != "ffn" else model.layers[li].ffn_plate
    return float(np.array(plate.weight)[i, j])


def flip_plate_position(model, li, pname, i, j):
    """Flip a ternary plate position: +1↔-1, 0→+1."""
    plate = getattr(model.layers[li].attn, f"{pname}_plate") if pname != "ffn" else model.layers[li].ffn_plate
    w = np.array(plate.weight)
    old_val = w[i, j]
    w[i, j] = -old_val if old_val != 0 else 1.0
    plate.weight = mx.array(w)
    mx.eval(plate.weight)
    return old_val, w[i, j]


def revert_plate_position(model, li, pname, i, j, old_val):
    plate = getattr(model.layers[li].attn, f"{pname}_plate") if pname != "ffn" else model.layers[li].ffn_plate
    w = np.array(plate.weight)
    w[i, j] = old_val
    plate.weight = mx.array(w)
    mx.eval(plate.weight)


def compute_delta_map(model, initial_mag):
    """Compute |delta| for each output dimension across all plates.
    Returns flat array aligned with plate positions."""
    delta_map = []
    for li, layer in enumerate(model.layers):
        for pname in ["k", "v", "o", "ffn"]:
            scale = getattr(layer.attn, f"{pname}_scale") if pname != "ffn" else layer.ffn_scale
            mag = initial_mag[li][pname]
            delta = np.abs(np.array(scale) - mag)  # (d_out,)
            plate = getattr(layer.attn, f"{pname}_plate") if pname != "ffn" else layer.ffn_plate
            d_out, d_in = plate.weight.shape
            # Each position (i,j) gets its row's delta value
            for i in range(d_out):
                for j in range(d_in):
                    delta_map.append(delta[i])
    return np.array(delta_map)


# ══════════════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════════════

def _zero_plates(grads, n):
    for i in range(n):
        lg=grads.get("layers",{})
        if isinstance(lg,list):
            if i>=len(lg): continue
            g=lg[i]
        elif isinstance(lg,dict): g=lg.get(i,lg.get(str(i),{}))
        else: continue
        if not isinstance(g,dict): continue
        for p in ["k_plate","v_plate","o_plate"]:
            pg=g.get("attn",{}).get(p,{})
            if isinstance(pg,dict) and "weight" in pg: pg["weight"]=mx.zeros_like(pg["weight"])
        fg=g.get("ffn_plate",{})
        if isinstance(fg,dict) and "weight" in fg: fg["weight"]=mx.zeros_like(fg["weight"])


def train_teacher_model(d, n_steps=5000):
    m=GDModel(d_model=d,n_layers=N_LAYERS); mx.eval(m.parameters())
    opt=optim.Adam(learning_rate=LR); lag=nn.value_and_grad(m,masked_ce_loss)
    rng=np.random.RandomState(42)
    for s in range(n_steps):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(m,ids,tgt,msk); mx.eval(lv,gr)
        m.update(opt.apply_gradients(gr,m)); mx.eval(m.parameters()); del lv,gr
        if (s+1)%100==0: mx.clear_cache()
        if (s+1)%1000==0:
            ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}"); return m


def train_beams(model, n_steps, tag=""):
    """GD phase: train only beams (continuous params), plates frozen."""
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt=optim.Adam(learning_rate=LR); lag=nn.value_and_grad(model,masked_ce_loss)
    rng=np.random.RandomState(42); best_acc=0
    for s in range(n_steps):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(model,ids,tgt,msk); mx.eval(lv,gr)
        _zero_plates(gr,len(model.layers))
        model.update(opt.apply_gradients(gr,model)); mx.eval(model.parameters()); del lv,gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%(n_steps//3)==0:
            ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
            best_acc=max(best_acc,ev["accuracy"])
            log(f"    {tag} GD step {s+1}: acc={ev['accuracy']:.4f}")
    ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
    return max(best_acc, ev["accuracy"]), ev["accuracy"]


def quick_eval(model):
    ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
    return ev["accuracy"], ev["loss"]


def make_model(crystal, mag):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m


# ══════════════════════════════════════════════════════════════════════
# Evolutionary descent
# ══════════════════════════════════════════════════════════════════════

def evo_round(model, initial_mag, crystal_probes, teacher_crystal,
              n_candidates, use_delta=True, rng=None):
    """One round of evolutionary descent.
    
    1. Compute delta map (mutation priority)
    2. Select top-N candidate positions
    3. For each: flip, eval, crystal check, accept/reject
    4. Return stats
    """
    if rng is None:
        rng = np.random.RandomState(int(time.time()) % 2**31)

    positions = get_all_plate_positions(model)
    n_positions = len(positions)

    if use_delta:
        # Delta-guided: prioritize high-|delta| positions
        delta_map = compute_delta_map(model, initial_mag)
        # Add small random noise to break ties
        priority = delta_map + rng.uniform(0, 0.001, size=len(delta_map))
        candidate_indices = np.argsort(priority)[-n_candidates:]
    else:
        # Random: pick random positions
        candidate_indices = rng.choice(n_positions, size=min(n_candidates, n_positions), replace=False)

    # Baseline fitness
    base_acc, base_loss = quick_eval(model)
    base_crystal = crystal_agr(measure_crystal(model, crystal_probes), teacher_crystal)

    accepted = 0
    rejected_acc = 0
    rejected_crystal = 0
    tested = 0

    for idx in candidate_indices:
        li, pname, i, j = positions[idx]
        old_val, new_val = flip_plate_position(model, li, pname, i, j)
        tested += 1

        # Quick crystal check first (cheap rejection)
        new_crystal = crystal_agr(measure_crystal(model, crystal_probes), teacher_crystal)
        if new_crystal < base_crystal + CRYSTAL_THRESHOLD:
            revert_plate_position(model, li, pname, i, j, old_val)
            rejected_crystal += 1
            continue

        # Accuracy check
        new_acc, _ = quick_eval(model)
        if new_acc >= base_acc - 0.005:  # small tolerance
            # ACCEPT
            accepted += 1
            base_acc = new_acc
            base_crystal = new_crystal
        else:
            # REJECT
            revert_plate_position(model, li, pname, i, j, old_val)
            rejected_acc += 1

    return {
        "tested": tested,
        "accepted": accepted,
        "rejected_crystal": rejected_crystal,
        "rejected_acc": rejected_acc,
        "final_acc": base_acc,
        "final_crystal": base_crystal,
        "accept_rate": accepted / tested if tested > 0 else 0,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("Training teacher d=256...")
    teacher = train_teacher_model(D_TEACHER, n_steps=5000)

    log("\nSetup...")
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    loom = cca_loom_extract(teacher, D_STUDENT)
    mag = extract_mag(teacher, D_STUDENT)

    # ── C1: LOOM_MAG baseline ──
    log(f"\n{'═'*60}")
    log("C1: LOOM_MAG baseline (beams only, no evolution)")
    m1 = make_model(loom, mag)
    best1, final1 = train_beams(m1, 3000, "C1")
    c1 = crystal_agr(measure_crystal(m1, probes), teacher_crystal)
    log(f"  Best={best1:.4f}, Final={final1:.4f}, Crystal={c1:.4f}")
    del m1; mx.clear_cache()

    # ── C2: EVO_COEVOLVE (delta-guided) ──
    log(f"\n{'═'*60}")
    log("C2: EVO_COEVOLVE (GD beams + delta-guided ternary evolution)")
    m2 = make_model(loom, mag)
    c2_trajectory = []
    total_accepted = 0
    total_tested = 0

    for r in range(N_COEVO_ROUNDS):
        log(f"\n  Round {r}:")

        # GD phase: train beams
        best_r, final_r = train_beams(m2, GD_STEPS_PER_ROUND, f"R{r}")

        # Measure
        crystal_r = crystal_agr(measure_crystal(m2, probes), teacher_crystal)
        log(f"    Post-GD: acc={final_r:.4f}, crystal={crystal_r:.4f}")

        # Evo phase: delta-guided flips
        evo_stats = evo_round(m2, mag, probes, teacher_crystal,
                              N_CANDIDATES_PER_ROUND, use_delta=True)

        total_accepted += evo_stats["accepted"]
        total_tested += evo_stats["tested"]

        log(f"    Evo: tested={evo_stats['tested']}, "
            f"accepted={evo_stats['accepted']}, "
            f"rejected(crystal)={evo_stats['rejected_crystal']}, "
            f"rejected(acc)={evo_stats['rejected_acc']}")
        log(f"    Post-evo: acc={evo_stats['final_acc']:.4f}, "
            f"crystal={evo_stats['final_crystal']:.4f}")

        c2_trajectory.append({
            "round": r,
            "gd_best": best_r,
            "gd_final": final_r,
            "gd_crystal": crystal_r,
            "evo_accepted": evo_stats["accepted"],
            "evo_tested": evo_stats["tested"],
            "post_evo_acc": evo_stats["final_acc"],
            "post_evo_crystal": evo_stats["final_crystal"],
        })

        # Reset beam scales to initial magnitudes for next round
        # (force beam to re-adapt to modified plates)
        for i, l in enumerate(m2.layers):
            l.attn.k_scale = mx.array(mag[i]["k"])
            l.attn.v_scale = mx.array(mag[i]["v"])
            l.attn.o_scale = mx.array(mag[i]["o"])
            l.ffn_scale = mx.array(mag[i]["ffn"])
        mx.eval(m2.parameters())

    # Final evaluation
    best2, final2 = train_beams(m2, GD_STEPS_PER_ROUND, "FINAL")
    c2_final = crystal_agr(measure_crystal(m2, probes), teacher_crystal)
    log(f"\n  Final: best={best2:.4f}, acc={final2:.4f}, crystal={c2_final:.4f}")
    log(f"  Total: {total_accepted} accepted / {total_tested} tested")
    del m2; mx.clear_cache()

    # ── C3: RANDOM_FLIPS (control — random mutations, no delta) ──
    log(f"\n{'═'*60}")
    log("C3: RANDOM_FLIPS (random mutations, no delta guidance)")
    m3 = make_model(loom, mag)
    c3_trajectory = []
    total_rand_accepted = 0

    for r in range(N_COEVO_ROUNDS):
        log(f"\n  Round {r}:")
        best_r, final_r = train_beams(m3, GD_STEPS_PER_ROUND, f"R{r}")
        crystal_r = crystal_agr(measure_crystal(m3, probes), teacher_crystal)

        evo_stats = evo_round(m3, mag, probes, teacher_crystal,
                              N_CANDIDATES_PER_ROUND, use_delta=False,
                              rng=np.random.RandomState(42 + r))

        total_rand_accepted += evo_stats["accepted"]
        log(f"    Evo: accepted={evo_stats['accepted']}/{evo_stats['tested']}, "
            f"acc={evo_stats['final_acc']:.4f}, crystal={evo_stats['final_crystal']:.4f}")

        c3_trajectory.append({
            "round": r,
            "post_evo_acc": evo_stats["final_acc"],
            "post_evo_crystal": evo_stats["final_crystal"],
            "accepted": evo_stats["accepted"],
        })

        for i, l in enumerate(m3.layers):
            l.attn.k_scale = mx.array(mag[i]["k"])
            l.attn.v_scale = mx.array(mag[i]["v"])
            l.attn.o_scale = mx.array(mag[i]["o"])
            l.ffn_scale = mx.array(mag[i]["ffn"])
        mx.eval(m3.parameters())

    best3, final3 = train_beams(m3, GD_STEPS_PER_ROUND, "FINAL")
    c3_final = crystal_agr(measure_crystal(m3, probes), teacher_crystal)
    del m3; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("SUMMARY: Evolutionary Descent")
    log(f"{'═'*60}\n")

    log(f"  {'Condition':<18s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'Flips':>6s}")
    log(f"  {'-'*18} {'-'*6} {'-'*6} {'-'*7} {'-'*6}")
    log(f"  {'LOOM_MAG':<18s} {best1:6.3f} {final1:6.3f} {c1:7.3f}      -")
    log(f"  {'EVO_COEVOLVE':<18s} {best2:6.3f} {final2:6.3f} {c2_final:7.3f} {total_accepted:>6d}")
    log(f"  {'RANDOM_FLIPS':<18s} {best3:6.3f} {final3:6.3f} {c3_final:7.3f} {total_rand_accepted:>6d}")

    both = best2 > best1 and c2_final > c1
    log(f"\n  EVO improves both accuracy AND crystal? {'✓ YES' if both else '✗ NO'}")
    log(f"    Accuracy: {best1:.4f} → {best2:.4f} ({'+' if best2>best1 else ''}{best2-best1:.4f})")
    log(f"    Crystal:  {c1:.4f} → {c2_final:.4f} ({'+' if c2_final>c1 else ''}{c2_final-c1:.4f})")

    log(f"\n  Co-evolution trajectory:")
    log(f"  {'Round':>5s} {'GD Acc':>7s} {'Evo Acc':>8s} {'Crystal':>8s} {'Accepted':>9s}")
    for t in c2_trajectory:
        log(f"  {t['round']:5d} {t['gd_final']:7.3f} {t['post_evo_acc']:8.3f} "
            f"{t['post_evo_crystal']:8.3f} {t['evo_accepted']:9d}")

    if total_accepted > 0:
        log(f"\n  Delta guidance vs random: "
            f"delta accepted {total_accepted}/{total_tested} "
            f"({total_accepted/total_tested*100:.1f}%), "
            f"random accepted {total_rand_accepted}")

    results = {
        "baseline": {"best": best1, "final": final1, "crystal": c1},
        "evo_coevolve": {"best": best2, "final": final2, "crystal": c2_final,
                         "trajectory": c2_trajectory, "total_accepted": total_accepted},
        "random_flips": {"best": best3, "final": final3, "crystal": c3_final,
                         "trajectory": c3_trajectory, "total_accepted": total_rand_accepted},
        "config": {"n_rounds": N_COEVO_ROUNDS, "gd_steps": GD_STEPS_PER_ROUND,
                   "n_candidates": N_CANDIDATES_PER_ROUND,
                   "crystal_threshold": CRYSTAL_THRESHOLD},
        "elapsed": time.time()-t0,
    }
    with open(RESULTS_DIR/"results.json","w") as f: json.dump(results,f,indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
