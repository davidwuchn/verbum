"""Soft Mirror v2 — Per-position mirrors + crystal loss + mirror stacking.

Session 124, experiment 10. v1 used per-dimension mirrors (d,) — too coarse,
GD only learned to block (0.0% flips). v2 uses per-position mirrors (d, d)
that can correct individual sign positions. Also tests stacking: 1 vs 2 mirrors.

The self-tuning hypothesis: with enough mirror precision + crystal loss,
GD can discover the correct sign corrections from just the reference beam
(magnitude template). No blunt flip phase needed.

Conditions:
  1. LOOM_MAG — baseline (no mirrors)
  2. MIRROR_1 — one per-position (d,d) soft mirror + crystal loss
  3. MIRROR_2 — two stacked per-position mirrors + crystal loss
  4. MIRROR_CE — one per-position mirror, CE only (no crystal constraint)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/soft_mirror_v2_exp.py

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


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "soft-mirror-v2"
D_TEACHER = 256
D_STUDENT = 128
N_LAYERS = 3
N_STEPS = 3000
EVAL_INTERVAL = 100
BATCH_SIZE = 32
LR = 0.003
MAX_DEPTH = 4
CRYSTAL_LAMBDA = 0.5
COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Per-position soft mirror model
# ══════════════════════════════════════════════════════════════════════

class PerPosMirrorAttention(nn.Module):
    """Attention with ternary plates + per-position soft mirrors.
    
    Mirror is (d_out, d_in) initialized to 1.0 — same shape as the plate.
    The effective weight at each position is plate[i,j] * mirror[i,j].
    GD can learn to flip (→-1), pass (+1), or block (→0) each position.
    """
    def __init__(self, d_model, n_mirrors=1):
        super().__init__()
        self.d_model = d_model
        self.n_mirrors = n_mirrors
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_plate = TernaryLinear(d_model, d_model)
        self.v_plate = TernaryLinear(d_model, d_model)
        self.o_plate = TernaryLinear(d_model, d_model)
        self.k_scale = mx.ones((d_model,))
        self.v_scale = mx.ones((d_model,))
        self.o_scale = mx.ones((d_model,))
        # Per-position mirrors — each is (d_out, d_in) init=1.0
        # For stacking: we store N mirrors per plate, product applied
        self.k_mirrors = [mx.ones((d_model, d_model)) for _ in range(n_mirrors)]
        self.v_mirrors = [mx.ones((d_model, d_model)) for _ in range(n_mirrors)]
        self.o_mirrors = [mx.ones((d_model, d_model)) for _ in range(n_mirrors)]
        self.scale = d_model ** -0.5

    def _apply_mirrors(self, plate, mirrors):
        """Apply stacked mirrors to plate output.
        
        plate: TernaryLinear, applied to x gives (B, T, d_out)
        mirrors: list of (d_out, d_in) soft mirrors
        
        For efficiency: compute effective mirror = product of all mirrors,
        then apply to the plate weight before matmul.
        """
        # Compute effective mirror (element-wise product of stack)
        eff = mirrors[0]
        for m in mirrors[1:]:
            eff = eff * m
        # Apply: modify the plate's effective weight
        # plate(x) = x @ (plate.weight.T) = x @ W.T
        # mirrored = x @ (W * mirror).T = x @ (mirror.T * W.T)
        # But we can't modify frozen plate weights.
        # Instead: plate(x) gives (B, T, d_out). The mirror acts per-output-dim.
        # Actually mirror is (d_out, d_in) and plate.weight is (d_out, d_in).
        # plate(x) = sign(W) @ x for each batch/time position.
        # mirrored(x) = (sign(W) * mirror) @ x
        # We need to apply mirror BEFORE the matmul, not after.
        # Since plate is frozen, we apply mirror to the input instead:
        # mirrored(x) = sign(W) @ (mirror_input_transform(x))
        # That's not right either.
        #
        # Correct approach: mirror modifies the plate output per-position.
        # For a (d_out, d_in) mirror M and plate weight W:
        #   effective_output[i] = sum_j M[i,j] * W[i,j] * x[j]
        #   = sum_j (M[i,:] * W[i,:]) . x
        # This IS element-wise modification of the weight matrix.
        # Since plate is frozen, we pre-compute the effective weight.
        return eff

    def __call__(self, x):
        B, T, D = x.shape
        q = self.q_proj(x) * self.scale

        # Apply mirrors to plates
        k_eff = self._apply_mirrors(self.k_plate, self.k_mirrors)
        v_eff = self._apply_mirrors(self.v_plate, self.v_mirrors)
        o_eff = self._apply_mirrors(self.o_plate, self.o_mirrors)

        # Mirrored plate forward: (W * mirror) @ x
        k_weight = self.k_plate.weight * k_eff  # (d, d)
        v_weight = self.v_plate.weight * v_eff
        k = (x @ k_weight.T) * self.k_scale  # (B, T, D)
        v = (x @ v_weight.T) * self.v_scale

        attn = q @ k.transpose(0, 2, 1)
        mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
        attn = mx.softmax(attn + mask, axis=-1)

        out = attn @ v
        o_weight = self.o_plate.weight * o_eff
        out = (out @ o_weight.T) * self.o_scale
        return out


class PerPosMirrorLayer(nn.Module):
    def __init__(self, d_model, n_mirrors=1):
        super().__init__()
        self.attn = PerPosMirrorAttention(d_model, n_mirrors)
        self.attn_norm = nn.LayerNorm(d_model)
        self.ffn_plate = TernaryLinear(d_model, d_model)
        self.ffn_norm = nn.LayerNorm(d_model)
        self.ffn_scale = mx.ones((d_model,))
        self.ffn_bias = mx.zeros((d_model,))
        self.ffn_mirrors = [mx.ones((d_model, d_model)) for _ in range(n_mirrors)]

    def __call__(self, x):
        x = x + self.attn(self.attn_norm(x))
        # FFN with mirror
        eff = self.ffn_mirrors[0]
        for m in self.ffn_mirrors[1:]:
            eff = eff * m
        ffn_weight = self.ffn_plate.weight * eff
        ffn_out = (self.ffn_norm(x) @ ffn_weight.T) * self.ffn_scale + self.ffn_bias
        return x + ffn_out


class PerPosMirrorModel(nn.Module):
    def __init__(self, d_model=128, n_layers=3, n_mirrors=1):
        super().__init__()
        self.d_model = d_model
        self.n_mirrors = n_mirrors
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [PerPosMirrorLayer(d_model, n_mirrors) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


def write_crystal_to_pp_model(model, crystal):
    for i, layer in enumerate(model.layers):
        layer.attn.k_plate.weight = mx.array(crystal[i]["k"])
        layer.attn.v_plate.weight = mx.array(crystal[i]["v"])
        layer.attn.o_plate.weight = mx.array(crystal[i]["o"])
        layer.ffn_plate.weight = mx.array(crystal[i]["ffn"])


def set_magnitudes_pp(model, mag):
    for i, layer in enumerate(model.layers):
        layer.attn.k_scale = mx.array(mag[i]["k"])
        layer.attn.v_scale = mx.array(mag[i]["v"])
        layer.attn.o_scale = mx.array(mag[i]["o"])
        layer.ffn_scale = mx.array(mag[i]["ffn"])


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement + loss (from v1)
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]; fs = ["f","g","h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n*3):
            if len(ps)>=n: break
            v1,v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1,f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
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


def crystal_loss_fn(model, probes, targets):
    tgt = mx.array(np.array(targets, dtype=np.float32))
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids],dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(x[0,-1,:])
        means.append(mx.mean(mx.stack(hs), axis=0))
    M = mx.stack(means)
    N = mx.sqrt(mx.sum(M*M, axis=1, keepdims=True)+1e-8)
    cos = (M/N) @ (M/N).T
    ir,ic = [0,0,0,1,1,2],[1,2,3,2,3,3]
    return mx.mean((cos[mx.array(ir),mx.array(ic)] - tgt[mx.array(ir),mx.array(ic)])**2)


def mirror_stats(model):
    vals = []
    for layer in model.layers:
        for mirrors in [layer.attn.k_mirrors, layer.attn.v_mirrors,
                        layer.attn.o_mirrors, layer.ffn_mirrors]:
            for m in mirrors:
                vals.append(np.array(m).flatten())
    v = np.concatenate(vals)
    q = np.sign(np.round(v))
    return {
        "mean": float(np.mean(v)), "std": float(np.std(v)),
        "min": float(np.min(v)), "max": float(np.max(v)),
        "pct_pass": float(np.mean(q==1))*100,
        "pct_flip": float(np.mean(q==-1))*100,
        "pct_block": float(np.mean(q==0))*100,
        "n_total": len(v),
    }


# ══════════════════════════════════════════════════════════════════════
# Extraction (reused)
# ══════════════════════════════════════════════════════════════════════

def cca_angle_bands(Wa, Wb, k=None):
    di = Wa.shape[1]
    if k is None: k=min(di,min(Wa.shape[0],Wb.shape[0]))
    _,_,Va=np.linalg.svd(Wa,full_matrices=False); _,_,Vb=np.linalg.svd(Wb,full_matrices=False)
    k=min(k,Va.shape[0],Vb.shape[0])
    A,B=Va[:k,:].T,Vb[:k,:].T
    Qa,_=np.linalg.qr(A); Qb,_=np.linalg.qr(B)
    U,S,Vt=np.linalg.svd(Qa.T@Qb,full_matrices=False)
    ang=np.degrees(np.arccos(np.clip(S,0,1)))
    da,db=Qa@U,Qb@Vt.T; sh=da+db
    return ang, sh/np.maximum(np.linalg.norm(sh,axis=0,keepdims=True),1e-8)

def extract_loom(teacher, ds):
    cr = []
    for li,layer in enumerate(teacher.layers):
        Wk,Wf=np.array(layer.attn.k_proj.weight),np.array(layer.ffn.weight)
        ang,sh=cca_angle_bands(Wk,Wf); ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight)
            cm=(ang>=35)&(ang<72)
            if cm.sum()>=2:
                de=np.sum(sh[:,cm]**2,axis=1)
                wt=np.sign(W)*(1.0+de/(de.max()+1e-10))[np.newaxis,:]
            else: wt=np.sign(W)
            _,S,Vt=np.linalg.svd(W,full_matrices=False); P=Vt[:ds,:]
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

def train_pp_model(model, name, cprobes=None, ctargets=None, clambda=0.0):
    mx.eval(model.parameters())
    for l in model.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt=optim.Adam(learning_rate=LR); rng=np.random.RandomState(42)
    def loss_fn(model, ids, tgt, msk):
        ce = masked_ce_loss(model, ids, tgt, msk)
        if clambda > 0 and cprobes:
            return ce + clambda * crystal_loss_fn(model, cprobes, ctargets)
        return ce
    lag=nn.value_and_grad(model, loss_fn); traj=[]
    for s in range(N_STEPS):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(model,ids,tgt,msk); mx.eval(lv,gr)
        _zero_plates(gr,len(model.layers))
        model.update(opt.apply_gradients(gr,model)); mx.eval(model.parameters()); del lv,gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%EVAL_INTERVAL==0:
            ev=eval_model(model,np.random.RandomState(999),n_batches=20,max_depth=MAX_DEPTH)
            traj.append({"step":s+1,"loss":ev["loss"],"accuracy":ev["accuracy"]})
            if (s+1)%500==0:
                ms=mirror_stats(model)
                log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}, "
                    f"flip={ms['pct_flip']:.1f}%, block={ms['pct_block']:.1f}%, "
                    f"mean={ms['mean']:.3f}")
    return {"condition":name,"trajectory":traj,
            "final_accuracy":traj[-1]["accuracy"],
            "best_accuracy":max(t["accuracy"] for t in traj),
            "best_loss":min(t["loss"] for t in traj)}

def train_baseline(crystal, mag, name):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters())
    for l in m.layers:
        l.attn.k_plate.freeze(); l.attn.v_plate.freeze()
        l.attn.o_plate.freeze(); l.ffn_plate.freeze()
    opt=optim.Adam(learning_rate=LR); rng=np.random.RandomState(42)
    lag=nn.value_and_grad(m,masked_ce_loss); traj=[]
    for s in range(N_STEPS):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(m,ids,tgt,msk); mx.eval(lv,gr)
        _zero_plates(gr,len(m.layers))
        m.update(opt.apply_gradients(gr,m)); mx.eval(m.parameters()); del lv,gr
        if (s+1)%50==0: mx.clear_cache()
        if (s+1)%EVAL_INTERVAL==0:
            ev=eval_model(m,np.random.RandomState(999),n_batches=20,max_depth=MAX_DEPTH)
            traj.append({"step":s+1,"loss":ev["loss"],"accuracy":ev["accuracy"]})
            if (s+1)%500==0: log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}")
    return m, {"condition":name,"trajectory":traj,
               "final_accuracy":traj[-1]["accuracy"],
               "best_accuracy":max(t["accuracy"] for t in traj),
               "best_loss":min(t["loss"] for t in traj)}


# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("Training teacher d=256...")
    teacher = train_teacher_model(D_TEACHER)

    log("\nSetup...")
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    loom = extract_loom(teacher, D_STUDENT)
    mag = extract_mag(teacher, D_STUDENT)

    tc = np.array(teacher_crystal)
    log("  Teacher crystal:")
    for i,c in enumerate(COMBINATORS):
        log(f"    {c}: "+" ".join(f"{tc[i,j]:+.3f}" for j in range(4)))

    # ── C1: LOOM_MAG baseline ──
    log(f"\n{'═'*60}\nC1: LOOM_MAG baseline")
    bl_m, bl_r = train_baseline(loom, mag, "LOOM_MAG")
    bl_c = measure_crystal(bl_m, probes)
    bl_a = crystal_agr(bl_c, teacher_crystal)
    log(f"  Crystal: {bl_a:.4f}"); del bl_m; mx.clear_cache()

    # ── C2: MIRROR_1 (1 per-pos mirror + crystal loss) ──
    log(f"\n{'═'*60}\nC2: MIRROR_1 (1 per-position mirror + crystal loss)")
    m2 = PerPosMirrorModel(D_STUDENT, N_LAYERS, n_mirrors=1); mx.eval(m2.parameters())
    write_crystal_to_pp_model(m2, loom); set_magnitudes_pp(m2, mag); mx.eval(m2.parameters())
    r2 = train_pp_model(m2, "MIRROR_1", probes, teacher_crystal, CRYSTAL_LAMBDA)
    c2 = measure_crystal(m2, probes); a2 = crystal_agr(c2, teacher_crystal)
    ms2 = mirror_stats(m2)
    log(f"  Crystal: {a2:.4f}, flip={ms2['pct_flip']:.1f}%, block={ms2['pct_block']:.1f}%")
    del m2; mx.clear_cache()

    # ── C3: MIRROR_2 (2 stacked mirrors + crystal loss) ──
    log(f"\n{'═'*60}\nC3: MIRROR_2 (2 stacked mirrors + crystal loss)")
    m3 = PerPosMirrorModel(D_STUDENT, N_LAYERS, n_mirrors=2); mx.eval(m3.parameters())
    write_crystal_to_pp_model(m3, loom); set_magnitudes_pp(m3, mag); mx.eval(m3.parameters())
    r3 = train_pp_model(m3, "MIRROR_2", probes, teacher_crystal, CRYSTAL_LAMBDA)
    c3 = measure_crystal(m3, probes); a3 = crystal_agr(c3, teacher_crystal)
    ms3 = mirror_stats(m3)
    log(f"  Crystal: {a3:.4f}, flip={ms3['pct_flip']:.1f}%, block={ms3['pct_block']:.1f}%")
    del m3; mx.clear_cache()

    # ── C4: MIRROR_CE (1 per-pos mirror, CE only, no crystal) ──
    log(f"\n{'═'*60}\nC4: MIRROR_CE (per-position, CE only)")
    m4 = PerPosMirrorModel(D_STUDENT, N_LAYERS, n_mirrors=1); mx.eval(m4.parameters())
    write_crystal_to_pp_model(m4, loom); set_magnitudes_pp(m4, mag); mx.eval(m4.parameters())
    r4 = train_pp_model(m4, "MIRROR_CE")
    c4 = measure_crystal(m4, probes); a4 = crystal_agr(c4, teacher_crystal)
    ms4 = mirror_stats(m4)
    log(f"  Crystal: {a4:.4f}, flip={ms4['pct_flip']:.1f}%, block={ms4['pct_block']:.1f}%")
    del m4; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}\nSUMMARY\n{'═'*60}\n")

    log(f"  {'Condition':<14s} {'Best':>6s} {'Final':>6s} {'Cryst':>6s} {'Flip%':>6s} {'Block%':>7s}")
    log(f"  {'-'*14} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*7}")
    log(f"  {'LOOM_MAG':<14s} {bl_r['best_accuracy']:6.3f} {bl_r['final_accuracy']:6.3f} {bl_a:6.3f}      -       -")
    log(f"  {'MIRROR_1+CL':<14s} {r2['best_accuracy']:6.3f} {r2['final_accuracy']:6.3f} {a2:6.3f} {ms2['pct_flip']:5.1f}% {ms2['pct_block']:6.1f}%")
    log(f"  {'MIRROR_2+CL':<14s} {r3['best_accuracy']:6.3f} {r3['final_accuracy']:6.3f} {a3:6.3f} {ms3['pct_flip']:5.1f}% {ms3['pct_block']:6.1f}%")
    log(f"  {'MIRROR_CE':<14s} {r4['best_accuracy']:6.3f} {r4['final_accuracy']:6.3f} {a4:6.3f} {ms4['pct_flip']:5.1f}% {ms4['pct_block']:6.1f}%")

    # The key question
    m1_better = r2['best_accuracy'] > bl_r['best_accuracy'] and a2 > bl_a
    m2_better = r3['best_accuracy'] > bl_r['best_accuracy'] and a3 > bl_a
    log(f"\n  MIRROR_1 improves both acc+crystal? {'✓' if m1_better else '✗'}")
    log(f"  MIRROR_2 improves both acc+crystal? {'✓' if m2_better else '✗'}")
    log(f"  MIRROR_CE preserves crystal?        {'✓' if a4 > 0.5 else '✗'} ({a4:.3f})")

    results = {
        "loom_mag": {**bl_r, "crystal": bl_a},
        "mirror_1": {**r2, "crystal": a2, "mirror": ms2},
        "mirror_2": {**r3, "crystal": a3, "mirror": ms3},
        "mirror_ce": {**r4, "crystal": a4, "mirror": ms4},
        "teacher_crystal": teacher_crystal,
        "elapsed": time.time()-t0,
    }
    with open(RESULTS_DIR/"results.json","w") as f: json.dump(results,f,indent=2)
    log(f"\n✓ Saved ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
