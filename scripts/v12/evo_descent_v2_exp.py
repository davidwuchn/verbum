"""Evolutionary Descent v2 — Absolute crystal floor prevents drift.

v1 hit 0.585 accuracy (record) but crystal drifted to -0.654 because
the per-flip threshold (-0.05) allowed accumulated degradation across
rounds. v2 uses an ABSOLUTE crystal floor: reject any flip that drops
crystal below the floor, regardless of how small the degradation.

Also tightens acceptance: require accuracy IMPROVEMENT, not just
"don't degrade." And reduces candidates per round (was 200 at 95.6%
acceptance — too loose).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/evo_descent_v2_exp.py 2>&1 | tee results/evo-descent-v2/run.log

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

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    TernaryLinear, Comb, Var, App,
    GDModel, HoloModel,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
)
from mini_holo_crystal import write_crystal_to_model


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "evo-descent-v2"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_COEVO_ROUNDS = 10
GD_STEPS = 1500
N_CANDIDATES = 100
EVAL_BATCHES = 30
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4
CRYSTAL_FLOOR = 0.3       # absolute minimum crystal agreement
ACC_IMPROVEMENT = 0.001   # must improve accuracy by at least this
COMBINATORS = ["K", "I", "B", "C"]


# ── Crystal ──

def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs=["a","b","c","d","e","x","y","z"]; fs=["f","g","h"]
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
    means=[]
    for c in COMBINATORS:
        hs=[]
        for ids in probes[c]:
            x=model.embed(mx.array(np.array([ids],dtype=np.int32)))
            for layer in model.layers: x=layer(x)
            hs.append(np.array(x[0,-1,:]))
        means.append(np.mean(hs,axis=0))
    M=np.array(means); N=np.maximum(np.linalg.norm(M,axis=1,keepdims=True),1e-8)
    return (M/N@(M/N).T).tolist()

def crystal_agr(s,t):
    A,B=np.array(s),np.array(t)
    idx=np.triu_indices(4,k=1)
    a,b=A[idx]-A[idx].mean(),B[idx]-B[idx].mean()
    d=np.sqrt(np.sum(a**2))*np.sqrt(np.sum(b**2))
    return float(np.sum(a*b)/d) if d>1e-10 else 0.0


# ── Extraction ──

def cca_loom_extract(teacher, ds):
    cr=[]
    for li,layer in enumerate(teacher.layers):
        Wk,Wf=np.array(layer.attn.k_proj.weight),np.array(layer.ffn.weight)
        _,_,Va=np.linalg.svd(Wk,full_matrices=False); _,_,Vb=np.linalg.svd(Wf,full_matrices=False)
        k=min(ds,Va.shape[0],Vb.shape[0])
        A,B=Va[:k,:].T,Vb[:k,:].T
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


# ── Plate manipulation ──

def get_all_positions(model):
    pos=[]
    for li,layer in enumerate(model.layers):
        for pn in ["k","v","o","ffn"]:
            plate=getattr(layer.attn,f"{pn}_plate") if pn!="ffn" else layer.ffn_plate
            do,di=plate.weight.shape
            for i in range(do):
                for j in range(di):
                    pos.append((li,pn,i,j))
    return pos

def flip_pos(model,li,pn,i,j):
    plate=getattr(model.layers[li].attn,f"{pn}_plate") if pn!="ffn" else model.layers[li].ffn_plate
    w=np.array(plate.weight); old=w[i,j]
    w[i,j]=-old if old!=0 else 1.0
    plate.weight=mx.array(w); mx.eval(plate.weight)
    return old

def revert_pos(model,li,pn,i,j,old):
    plate=getattr(model.layers[li].attn,f"{pn}_plate") if pn!="ffn" else model.layers[li].ffn_plate
    w=np.array(plate.weight); w[i,j]=old
    plate.weight=mx.array(w); mx.eval(plate.weight)

def delta_map(model, mag):
    dm=[]
    for li,layer in enumerate(model.layers):
        for pn in ["k","v","o","ffn"]:
            scale=getattr(layer.attn,f"{pn}_scale") if pn!="ffn" else layer.ffn_scale
            d=np.abs(np.array(scale)-mag[li][pn])
            plate=getattr(layer.attn,f"{pn}_plate") if pn!="ffn" else layer.ffn_plate
            do,di=plate.weight.shape
            for i in range(do):
                for j in range(di):
                    dm.append(d[i])
    return np.array(dm)


# ── Training ──

def _zero_plates(grads,n):
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

def train_teacher(d,n=5000):
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

def train_beams(model, n, tag=""):
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt=optim.Adam(learning_rate=LR); lag=nn.value_and_grad(model,masked_ce_loss)
    rng=np.random.RandomState(42); best=0
    for s in range(n):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(model,ids,tgt,msk); mx.eval(lv,gr)
        _zero_plates(gr,len(model.layers))
        model.update(opt.apply_gradients(gr,model)); mx.eval(model.parameters()); del lv,gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%(max(1,n//3))==0:
            ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
            best=max(best,ev["accuracy"])
            log(f"    {tag} step {s+1}: acc={ev['accuracy']:.4f}")
    ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
    return max(best,ev["accuracy"]), ev["accuracy"]

def quick_eval(model):
    ev=eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)
    return ev["accuracy"]

def make_model(crystal, mag):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m

def reset_beams(model, mag):
    for i,l in enumerate(model.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(model.parameters())


# ── Evo round with absolute floor ──

def evo_round_v2(model, mag, probes, teacher_crystal, n_candidates):
    """Evolutionary round with absolute crystal floor + accuracy improvement."""
    positions = get_all_positions(model)
    dm = delta_map(model, mag)
    priority = dm + np.random.uniform(0, 0.001, size=len(dm))
    candidates = np.argsort(priority)[-n_candidates:]

    base_acc = quick_eval(model)
    base_crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)

    accepted = 0
    rej_crystal = 0
    rej_acc = 0
    rej_floor = 0

    for idx in candidates:
        li, pn, i, j = positions[idx]
        old = flip_pos(model, li, pn, i, j)

        # Crystal floor check (absolute)
        new_crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)
        if new_crystal < CRYSTAL_FLOOR:
            revert_pos(model, li, pn, i, j, old)
            rej_floor += 1
            continue

        # Crystal must not degrade from current
        if new_crystal < base_crystal - 0.01:
            revert_pos(model, li, pn, i, j, old)
            rej_crystal += 1
            continue

        # Accuracy must improve (or stay equal)
        new_acc = quick_eval(model)
        if new_acc >= base_acc + ACC_IMPROVEMENT:
            accepted += 1
            base_acc = new_acc
            base_crystal = new_crystal
        elif new_acc >= base_acc and new_crystal > base_crystal:
            # Accept if crystal improves even if accuracy flat
            accepted += 1
            base_acc = new_acc
            base_crystal = new_crystal
        else:
            revert_pos(model, li, pn, i, j, old)
            rej_acc += 1

    return {
        "tested": len(candidates),
        "accepted": accepted,
        "rej_floor": rej_floor,
        "rej_crystal": rej_crystal,
        "rej_acc": rej_acc,
        "final_acc": base_acc,
        "final_crystal": base_crystal,
    }


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("Training teacher d=256...")
    teacher = train_teacher(D_TEACHER, 5000)

    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    loom = cca_loom_extract(teacher, D_STUDENT)
    mag = extract_mag(teacher, D_STUDENT)

    tc = np.array(teacher_crystal)
    log("\nTeacher crystal:")
    for i,c in enumerate(COMBINATORS):
        log(f"  {c}: "+" ".join(f"{tc[i,j]:+.3f}" for j in range(4)))

    # ── Baseline ──
    log(f"\n{'═'*60}\nBASELINE: LOOM_MAG (no evolution)")
    m_bl = make_model(loom, mag)
    best_bl, final_bl = train_beams(m_bl, 3000, "BL")
    c_bl = crystal_agr(measure_crystal(m_bl, probes), teacher_crystal)
    log(f"  Best={best_bl:.4f}, Final={final_bl:.4f}, Crystal={c_bl:.4f}")
    del m_bl; mx.clear_cache()

    # ── Evo with absolute floor ──
    log(f"\n{'═'*60}\nEVO v2: absolute crystal floor={CRYSTAL_FLOOR}, acc_improve={ACC_IMPROVEMENT}")
    m_evo = make_model(loom, mag)
    traj = []
    total_accepted = 0
    total_tested = 0

    for r in range(N_COEVO_ROUNDS):
        log(f"\n  Round {r}:")

        best_r, final_r = train_beams(m_evo, GD_STEPS, f"R{r}")
        crystal_r = crystal_agr(measure_crystal(m_evo, probes), teacher_crystal)
        log(f"    Post-GD: acc={final_r:.4f}, crystal={crystal_r:.4f}")

        evo = evo_round_v2(m_evo, mag, probes, teacher_crystal, N_CANDIDATES)
        total_accepted += evo["accepted"]
        total_tested += evo["tested"]

        log(f"    Evo: accept={evo['accepted']}, "
            f"rej_floor={evo['rej_floor']}, rej_crystal={evo['rej_crystal']}, "
            f"rej_acc={evo['rej_acc']}")
        log(f"    Post-evo: acc={evo['final_acc']:.4f}, crystal={evo['final_crystal']:.4f}")

        traj.append({
            "round": r,
            "gd_best": best_r, "gd_final": final_r, "gd_crystal": crystal_r,
            "evo_accepted": evo["accepted"],
            "evo_rej_floor": evo["rej_floor"],
            "evo_rej_crystal": evo["rej_crystal"],
            "evo_rej_acc": evo["rej_acc"],
            "post_acc": evo["final_acc"],
            "post_crystal": evo["final_crystal"],
        })

        reset_beams(m_evo, mag)

    # Final beam training
    best_final, final_final = train_beams(m_evo, GD_STEPS, "FINAL")
    c_final = crystal_agr(measure_crystal(m_evo, probes), teacher_crystal)

    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nSUMMARY\n{'═'*60}\n")

    log(f"  {'Condition':<14s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'Flips':>6s}")
    log(f"  {'-'*14} {'-'*6} {'-'*6} {'-'*7} {'-'*6}")
    log(f"  {'LOOM_MAG':<14s} {best_bl:6.3f} {final_bl:6.3f} {c_bl:7.3f}      -")
    log(f"  {'EVO_v2':<14s} {best_final:6.3f} {final_final:6.3f} {c_final:7.3f} {total_accepted:>6d}")

    both = best_final > best_bl and c_final > c_bl
    log(f"\n  Improves BOTH accuracy AND crystal? {'✓ YES' if both else '✗ NO'}")
    log(f"    Accuracy: {best_bl:.4f} → {best_final:.4f} ({best_final-best_bl:+.4f})")
    log(f"    Crystal:  {c_bl:.4f} → {c_final:.4f} ({c_final-c_bl:+.4f})")
    log(f"    Acceptance rate: {total_accepted}/{total_tested} "
        f"({total_accepted/max(1,total_tested)*100:.1f}%)")

    log(f"\n  Co-evolution trajectory:")
    log(f"  {'R':>2s} {'GDAcc':>6s} {'EvoAcc':>7s} {'Crystal':>7s} {'OK':>3s} "
        f"{'Flr':>4s} {'Cry':>4s} {'Acc':>4s}")
    log(f"  {'-'*2} {'-'*6} {'-'*7} {'-'*7} {'-'*3} {'-'*4} {'-'*4} {'-'*4}")
    for t in traj:
        log(f"  {t['round']:2d} {t['gd_final']:6.3f} {t['post_acc']:7.3f} "
            f"{t['post_crystal']:7.3f} {t['evo_accepted']:3d} "
            f"{t['evo_rej_floor']:4d} {t['evo_rej_crystal']:4d} {t['evo_rej_acc']:4d}")

    # Crystal preservation check
    crystals = [t["post_crystal"] for t in traj]
    all_above_floor = all(c >= CRYSTAL_FLOOR for c in crystals)
    log(f"\n  Crystal always above floor ({CRYSTAL_FLOOR})? "
        f"{'✓ YES' if all_above_floor else '✗ NO'}")
    log(f"  Crystal range: [{min(crystals):.3f}, {max(crystals):.3f}]")

    results = {
        "baseline": {"best":best_bl, "final":final_bl, "crystal":c_bl},
        "evo_v2": {"best":best_final, "final":final_final, "crystal":c_final,
                   "trajectory":traj, "total_accepted":total_accepted,
                   "total_tested":total_tested},
        "config": {"n_rounds":N_COEVO_ROUNDS, "gd_steps":GD_STEPS,
                   "n_candidates":N_CANDIDATES, "crystal_floor":CRYSTAL_FLOOR,
                   "acc_improvement":ACC_IMPROVEMENT},
        "elapsed": time.time()-t0,
    }
    with open(RESULTS_DIR/"results.json","w") as f: json.dump(results,f,indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
