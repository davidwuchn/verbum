"""Evolutionary Descent v3 — Crystal loss in GD + crystal floor in evo.

v2 showed: evo floor works (10.7% acceptance) but crystal degrades
during GD beam training between rounds. Fix: add crystal lattice loss
to the GD phase. We proved it works at 0.9998 agreement (exp 9).

Combined protection:
  GD phase:  CE + crystal_lattice_loss (differentiable, keeps crystal stable)
  Evo phase: delta-guided flips + absolute crystal floor (discrete, only accepts improvements)

This is the full co-evolution with crystal protection on BOTH sides.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/evo_descent_v3_exp.py 2>&1 | tee results/evo-descent-v3/run.log

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

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "evo-descent-v3"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
N_ROUNDS = 10; GD_STEPS = 1500; N_CANDIDATES = 100
EVAL_BATCHES = 30; BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
CRYSTAL_FLOOR = 0.3; CRYSTAL_LAMBDA = 0.3; ACC_IMPROVE = 0.001
COMBINATORS = ["K", "I", "B", "C"]

# ── Crystal ──
def gen_probes(n=20, seed=42):
    rng=np.random.RandomState(seed)
    vs=["a","b","c","d","e","x","y","z"]; fs=["f","g","h"]
    probes={}
    for c in COMBINATORS:
        ps=[]
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

def crystal_lattice_loss(model, probes, targets):
    """Differentiable crystal loss for GD phase."""
    tgt=mx.array(np.array(targets,dtype=np.float32))
    means=[]
    for c in COMBINATORS:
        hs=[]
        for ids in probes[c]:
            x=model.embed(mx.array(np.array([ids],dtype=np.int32)))
            for layer in model.layers: x=layer(x)
            hs.append(x[0,-1,:])
        means.append(mx.mean(mx.stack(hs),axis=0))
    M=mx.stack(means)
    N=mx.sqrt(mx.sum(M*M,axis=1,keepdims=True)+1e-8)
    cos=(M/N)@(M/N).T
    ir,ic=[0,0,0,1,1,2],[1,2,3,2,3,3]
    return mx.mean((cos[mx.array(ir),mx.array(ic)]-tgt[mx.array(ir),mx.array(ic)])**2)

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

# ── Plate ops ──
def get_positions(model):
    pos=[]
    for li,layer in enumerate(model.layers):
        for pn in ["k","v","o","ffn"]:
            plate=getattr(layer.attn,f"{pn}_plate") if pn!="ffn" else layer.ffn_plate
            do,di=plate.weight.shape
            for i in range(do):
                for j in range(di): pos.append((li,pn,i,j))
    return pos

def flip_pos(model,li,pn,i,j):
    plate=getattr(model.layers[li].attn,f"{pn}_plate") if pn!="ffn" else model.layers[li].ffn_plate
    w=np.array(plate.weight); old=w[i,j]; w[i,j]=-old if old!=0 else 1.0
    plate.weight=mx.array(w); mx.eval(plate.weight); return old

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
                for j in range(di): dm.append(d[i])
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

def train_beams_with_crystal(model, n, probes, targets, clambda, tag=""):
    """GD with CE + crystal lattice loss."""
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt=optim.Adam(learning_rate=LR); rng=np.random.RandomState(42); best=0

    def loss_fn(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        if clambda > 0:
            cl = crystal_lattice_loss(model, probes, targets)
            return ce + clambda * cl
        return ce

    lag=nn.value_and_grad(model, loss_fn)
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

def train_beams_plain(model, n, tag=""):
    """GD with CE only (for baseline comparison)."""
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
    return eval_model(model,np.random.RandomState(999),n_batches=EVAL_BATCHES,max_depth=MAX_DEPTH)["accuracy"]

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

# ── Evo round ──
def evo_round(model, mag, probes, teacher_crystal, n_cand):
    positions=get_positions(model); dm=delta_map(model,mag)
    priority=dm+np.random.uniform(0,0.001,size=len(dm))
    candidates=np.argsort(priority)[-n_cand:]
    base_acc=quick_eval(model)
    base_crys=crystal_agr(measure_crystal(model,probes),teacher_crystal)
    accepted=0; rej_floor=0; rej_crys=0; rej_acc=0
    for idx in candidates:
        li,pn,i,j=positions[idx]
        old=flip_pos(model,li,pn,i,j)
        nc=crystal_agr(measure_crystal(model,probes),teacher_crystal)
        if nc<CRYSTAL_FLOOR:
            revert_pos(model,li,pn,i,j,old); rej_floor+=1; continue
        if nc<base_crys-0.01:
            revert_pos(model,li,pn,i,j,old); rej_crys+=1; continue
        na=quick_eval(model)
        if na>=base_acc+ACC_IMPROVE:
            accepted+=1; base_acc=na; base_crys=nc
        elif na>=base_acc and nc>base_crys:
            accepted+=1; base_acc=na; base_crys=nc
        else:
            revert_pos(model,li,pn,i,j,old); rej_acc+=1
    return {"tested":len(candidates),"accepted":accepted,"rej_floor":rej_floor,
            "rej_crys":rej_crys,"rej_acc":rej_acc,"acc":base_acc,"crystal":base_crys}

# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0=time.time()

    log("Training teacher d=256...")
    teacher=train_teacher(D_TEACHER,5000)
    probes=gen_probes()
    tc=measure_crystal(teacher,probes)
    loom=cca_loom_extract(teacher,D_STUDENT)
    mag=extract_mag(teacher,D_STUDENT)

    tca=np.array(tc)
    log("\nTeacher crystal:")
    for i,c in enumerate(COMBINATORS):
        log(f"  {c}: "+" ".join(f"{tca[i,j]:+.3f}" for j in range(4)))

    # ── C1: Baseline (CE only, no evo) ──
    log(f"\n{'═'*60}\nC1: BASELINE (CE only, no evo)")
    m1=make_model(loom,mag)
    best1,final1=train_beams_plain(m1,3000,"BL")
    c1=crystal_agr(measure_crystal(m1,probes),tc)
    log(f"  Best={best1:.4f}, Final={final1:.4f}, Crystal={c1:.4f}")
    del m1; mx.clear_cache()

    # ── C2: Crystal loss only (no evo) ──
    log(f"\n{'═'*60}\nC2: CRYSTAL LOSS (CE+CL, no evo)")
    m2=make_model(loom,mag)
    best2,final2=train_beams_with_crystal(m2,3000,probes,tc,CRYSTAL_LAMBDA,"CL")
    c2=crystal_agr(measure_crystal(m2,probes),tc)
    log(f"  Best={best2:.4f}, Final={final2:.4f}, Crystal={c2:.4f}")
    del m2; mx.clear_cache()

    # ── C3: Evo + CE only (no crystal loss in GD) ──
    log(f"\n{'═'*60}\nC3: EVO + CE (evo floor but no crystal loss in GD)")
    m3=make_model(loom,mag)
    traj3=[]; ta3=0; tt3=0
    for r in range(N_ROUNDS):
        log(f"\n  R{r}:")
        b,f=train_beams_plain(m3,GD_STEPS,f"R{r}")
        cr=crystal_agr(measure_crystal(m3,probes),tc)
        log(f"    Post-GD: acc={f:.4f}, crystal={cr:.4f}")
        ev=evo_round(m3,mag,probes,tc,N_CANDIDATES)
        ta3+=ev["accepted"]; tt3+=ev["tested"]
        log(f"    Evo: ok={ev['accepted']} flr={ev['rej_floor']} cry={ev['rej_crys']} acc={ev['rej_acc']}")
        log(f"    Post-evo: acc={ev['acc']:.4f}, crystal={ev['crystal']:.4f}")
        traj3.append({"round":r,"gd_acc":f,"gd_crystal":cr,**ev})
        reset_beams(m3,mag)
    best3,final3=train_beams_plain(m3,GD_STEPS,"FINAL")
    c3=crystal_agr(measure_crystal(m3,probes),tc)
    del m3; mx.clear_cache()

    # ── C4: Evo + CE + Crystal Loss (THE FULL PIPELINE) ──
    log(f"\n{'═'*60}\nC4: EVO + CE + CRYSTAL LOSS (full co-evolution)")
    m4=make_model(loom,mag)
    traj4=[]; ta4=0; tt4=0
    for r in range(N_ROUNDS):
        log(f"\n  R{r}:")
        b,f=train_beams_with_crystal(m4,GD_STEPS,probes,tc,CRYSTAL_LAMBDA,f"R{r}")
        cr=crystal_agr(measure_crystal(m4,probes),tc)
        log(f"    Post-GD+CL: acc={f:.4f}, crystal={cr:.4f}")
        ev=evo_round(m4,mag,probes,tc,N_CANDIDATES)
        ta4+=ev["accepted"]; tt4+=ev["tested"]
        log(f"    Evo: ok={ev['accepted']} flr={ev['rej_floor']} cry={ev['rej_crys']} acc={ev['rej_acc']}")
        log(f"    Post-evo: acc={ev['acc']:.4f}, crystal={ev['crystal']:.4f}")
        traj4.append({"round":r,"gd_acc":f,"gd_crystal":cr,**ev})
        reset_beams(m4,mag)
    best4,final4=train_beams_with_crystal(m4,GD_STEPS,probes,tc,CRYSTAL_LAMBDA,"FINAL")
    c4=crystal_agr(measure_crystal(m4,probes),tc)
    del m4; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nSUMMARY\n{'═'*60}\n")

    log(f"  {'Condition':<22s} {'Best':>6s} {'Final':>6s} {'Crystal':>7s} {'Flips':>6s}")
    log(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*7} {'-'*6}")
    log(f"  {'CE only':<22s} {best1:6.3f} {final1:6.3f} {c1:7.3f}      -")
    log(f"  {'CE+CrystalLoss':<22s} {best2:6.3f} {final2:6.3f} {c2:7.3f}      -")
    log(f"  {'Evo+CE':<22s} {best3:6.3f} {final3:6.3f} {c3:7.3f} {ta3:6d}")
    log(f"  {'Evo+CE+CrystalLoss':<22s} {best4:6.3f} {final4:6.3f} {c4:7.3f} {ta4:6d}")

    # The key question
    both_c3 = best3>best1 and c3>c1
    both_c4 = best4>best1 and c4>c1
    log(f"\n  Evo+CE improves both?            {'✓' if both_c3 else '✗'} (acc:{best1:.3f}→{best3:.3f}, crys:{c1:.3f}→{c3:.3f})")
    log(f"  Evo+CE+CrystalLoss improves both? {'✓' if both_c4 else '✗'} (acc:{best1:.3f}→{best4:.3f}, crys:{c1:.3f}→{c4:.3f})")

    # Crystal stability
    if traj4:
        crystals4=[t["crystal"] for t in traj4]
        gd_crystals4=[t["gd_crystal"] for t in traj4]
        log(f"\n  C4 crystal trajectory (GD phase → Evo phase):")
        for t in traj4:
            bar_gd="█"*max(0,int(t["gd_crystal"]*20))
            bar_ev="█"*max(0,int(t["crystal"]*20))
            log(f"    R{t['round']}: GD={t['gd_crystal']:+.3f} {bar_gd}  Evo={t['crystal']:+.3f} {bar_ev}  ok={t['accepted']}")
        log(f"  GD crystal range: [{min(gd_crystals4):.3f}, {max(gd_crystals4):.3f}]")
        log(f"  Evo crystal range: [{min(crystals4):.3f}, {max(crystals4):.3f}]")
        log(f"  Crystal always ≥ floor ({CRYSTAL_FLOOR})? "
            f"{'✓' if all(c>=CRYSTAL_FLOOR for c in crystals4) else '✗'}")

    results={
        "c1_baseline":{"best":best1,"final":final1,"crystal":c1},
        "c2_crystal_loss":{"best":best2,"final":final2,"crystal":c2},
        "c3_evo_ce":{"best":best3,"final":final3,"crystal":c3,"traj":traj3,"accepted":ta3,"tested":tt3},
        "c4_evo_ce_cl":{"best":best4,"final":final4,"crystal":c4,"traj":traj4,"accepted":ta4,"tested":tt4},
        "config":{"n_rounds":N_ROUNDS,"gd_steps":GD_STEPS,"n_candidates":N_CANDIDATES,
                  "crystal_floor":CRYSTAL_FLOOR,"crystal_lambda":CRYSTAL_LAMBDA},
        "elapsed":time.time()-t0,
    }
    with open(RESULTS_DIR/"results.json","w") as f: json.dump(results,f,indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")

if __name__=="__main__": main()
