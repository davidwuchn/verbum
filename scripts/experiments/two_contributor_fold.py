#!/usr/bin/env python3
# register: functional -> topological/routing
"""Two-contributor fold — do two INDEPENDENTLY-trained contributors compose
CLEANLY when they share a relational target?  (session 224, the decisive
distributed test; AGENTS.md S5 gate "two contributors compose cleanly")

THE CLAIM CHAIN (from s223 relational-loss distillation, 3 seeds x 3 lambda):
  - a relational loss pulls an independently-init student to ecosystem-grade
    agreement (+0.78-0.85) with a reference routing Gram, robust to seed/lambda;
  - the function lives ONLY in the routing register; RAW carries the common-mode
    crystal (the b-column: GC(hidden)=1.0, zero function transferred = model-soup);
  - => N contributors trained to the SAME reference Gram should be RELATIONALLY
    IDENTICAL => a fold of the ROUTING register is well-posed by construction,
    while a RAW merge folds only the universal crystal everyone already has.

THE EXPERIMENT:
  Two tiny byte-level students A, B trained on DISJOINT data shards.
  Two arms:
    REL  : both + relational loss to the SAME teacher routing Gram (route_cmr_L12)
    CTRL : CE only (independent, incommensurable frames)
  Fold protocol (fold ROUTING, NEVER raw):
    1. verify relationally identical  : GramCorr(A_route, B_route) in the sign-CMR
       gate register (REL high, CTRL low) + raw-register GramCorr (b-column crystal
       control: high for BOTH = the universal crystal).
    2. Re-Basin align              : permute B's d_ff neurons to A per block by
       gate-activation correlation (Hungarian) -- the exact SwiGLU symmetry.
    3. fold                        : base = A (plumbing stays local); merge ONLY the
       routing register w_gate where sign-consensus holds (avg A & permuted-B);
       leave w_up/w_down/attn/emb = A.
    4. ACCEPT via WHNF/contractivity, NOT Gram-match (Goodhart, s223#3): run the
       capture block as a fixed-point map x+block(x), K iters; accept iff the folded
       operator stays contractive (L<1) and Delta-x does not rise vs base.
    5. measure CE on held-out A-shard & B-shard for A, B, folded.

THE FALSIFIABLE CLAIM:
  REL  -> fold stays contractive AND folded CE on the OTHER contributor's shard
          improves/holds vs base A (B's routing function transferred), skeleton
          folds (high consensus), plumbing left local.
  CTRL/raw -> fold degrades CE / breaks contractivity (model soup) -- the two
          do NOT compose cleanly without the shared relational geometry.

Usage:
  uv run python scripts/experiments/two_contributor_fold.py --smoke
  uv run python scripts/experiments/two_contributor_fold.py --steps 1500 --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# reuse the s223 harness primitives (model, geometry, verdict instruments)
from relational_loss_distillation import (  # noqa: E402
    CRYSTAL,
    VOCAB,
    TinyLM,
    build_corpus,
    gather_last,
    git_sha,
    load_crystal_probe_batch,
    log,
    np_centroids,
    np_cmr,
    np_gram,
    np_silhouette_null,
    offdiag_corr,
    offdiag_mse,
    soft_gram,
    to_bytes,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "two-contributor-fold"
TEACHER_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"


# ---- training one contributor on its shard ----------------------------------
def train_contributor(name, shard_train, args, device, g_target, seed,
                      probe_ids, probe_len, label_idx, cap):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff,
                   args.block_size).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    n = shard_train.shape[0]
    bs, T = args.batch_size, args.block_size
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    gt = (torch.tensor(g_target, device=device, dtype=torch.float32)
          if g_target is not None else None)
    t0 = time.time()
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack(
            [torch.from_numpy(shard_train[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(shard_train[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        loss = ce
        if gt is not None and (step % args.rel_every == 0):
            feats = []
            for s in range(0, p_ids.shape[0], args.probe_batch):
                _, _, gate = model(p_ids[s:s + args.probe_batch], capture_layer=cap)
                feats.append(gather_last(gate, p_len[s:s + args.probe_batch]))
            g_pred = soft_gram(torch.cat(feats, dim=0), label_idx)
            loss = ce + args.rel_lambda * offdiag_mse(g_pred, gt)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.log_every == 0 or step == 1:
            log(f"    [{name}] step {step:5d} | CE {ce.item():.4f} "
                f"| {(time.time()-t0):.0f}s")
    return model


# ---- evaluation -------------------------------------------------------------
@torch.no_grad()
def eval_ce(model, shard_eval, args, device, n_batches=40):
    model.eval()
    n, T, bs = shard_eval.shape[0], args.block_size, args.batch_size
    if n <= T + 1:
        return float("nan")
    tot, cnt = 0.0, 0
    g = torch.Generator().manual_seed(1234)
    for _ in range(n_batches):
        ix = torch.randint(0, n - T - 1, (bs,), generator=g)
        xb = torch.stack([torch.from_numpy(shard_eval[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(shard_eval[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        tot += float(ce.item())
        cnt += 1
    return tot / max(cnt, 1)


@torch.no_grad()
def capture_all_gates(model, idx):
    """Return list over blocks of gate pre-activations [B,T,d_ff]."""
    pos = torch.arange(idx.shape[1], device=idx.device)
    x = model.tok(idx) + model.pos(pos)[None]
    gates = []
    for blk in model.blocks:
        x, gate = blk(x)
        gates.append(gate)
    return gates


@torch.no_grad()
def routing_gram(model, p_ids, p_len, labels, cap, device, probe_batch):
    """Sign-CMR gate Gram in the routing register at the capture layer."""
    feats = []
    for s in range(0, p_ids.shape[0], probe_batch):
        _, _, gate = model(p_ids[s:s + probe_batch], capture_layer=cap)
        feats.append(gather_last(gate, p_len[s:s + probe_batch]).cpu().numpy())
    gate_np = np.concatenate(feats, axis=0).astype(np.float64)
    sign_cmr = np_cmr(np.sign(gate_np))
    return np_gram(np_centroids(sign_cmr, labels)), sign_cmr


@torch.no_grad()
def raw_gram(model, p_ids, p_len, labels, cap, device, probe_batch):
    feats = []
    for s in range(0, p_ids.shape[0], probe_batch):
        _, hid, _ = model(p_ids[s:s + probe_batch], capture_layer=cap)
        feats.append(gather_last(hid, p_len[s:s + probe_batch]).cpu().numpy())
    hid_np = np.concatenate(feats, axis=0).astype(np.float64)
    hid_cmr = np_cmr(hid_np)
    return np_gram(np_centroids(hid_cmr, labels)), hid_cmr


# ---- Re-Basin: permute B's d_ff neurons to A per block ----------------------
@torch.no_grad()
def rebasin_perms(model_a, model_b, p_ids, probe_batch, device):
    """Per-block permutation of B's d_ff neurons matched to A's by gate-activation
    correlation (Hungarian). Returns (perms, matched_corrs): perm[l] of length d_ff
    and matched_corr[l][i] = activation correlation of A-neuron i to its matched
    B-neuron (the foldability score: high = same job in both = consensus skeleton)."""
    ga_all, gb_all = [], []
    for s in range(0, p_ids.shape[0], probe_batch):
        pb = p_ids[s:s + probe_batch]
        ga = capture_all_gates(model_a, pb)
        gb = capture_all_gates(model_b, pb)
        ga_all.append([g.reshape(-1, g.shape[-1]).cpu().numpy() for g in ga])
        gb_all.append([g.reshape(-1, g.shape[-1]).cpu().numpy() for g in gb])
    n_layer = len(ga_all[0])
    perms, matched_corrs = [], []
    for li in range(n_layer):
        A = np.concatenate([b[li] for b in ga_all], axis=0)  # [M, d_ff]
        B = np.concatenate([b[li] for b in gb_all], axis=0)
        A = (A - A.mean(0)) / (A.std(0) + 1e-8)
        B = (B - B.mean(0)) / (B.std(0) + 1e-8)
        corr = (A.T @ B) / A.shape[0]                        # [d_ff, d_ff]
        row, col = linear_sum_assignment(-corr)              # maximize corr
        perm = np.empty(corr.shape[0], dtype=np.int64)
        perm[row] = col                                      # A-neuron i <- B-neuron
        mc = np.empty(corr.shape[0], dtype=np.float64)
        mc[row] = corr[row, col]
        matched_corrs.append(mc)

        perms.append(perm)
    return perms, matched_corrs


@torch.no_grad()
def fold_routing(model_a, model_b, perms, matched_corrs, theta, device):
    """Neuron-wise Re-Basin partial merge. base = A (plumbing local). For each block,
    permute B's d_ff neurons into A's frame; at CONSENSUS neurons (matched activation
    correlation >= theta = "same combinator job in both") average the FULL aligned
    neuron (w_gate+w_up rows, w_down col); leave non-consensus (plumbing) neurons = A.
    The routing register (which neurons fire = the gate) drives the consensus mask;
    the merge keeps the SwiGLU symmetry exact (permutation, not rotation)."""
    folded = copy.deepcopy(model_a)
    consensus_frac = []
    for li, blk in enumerate(folded.blocks):
        perm = perms[li]
        cons = torch.tensor(matched_corrs[li] >= theta, device=device)  # [d_ff]
        gate_a = model_a.blocks[li].w_gate.weight.data
        up_a = model_a.blocks[li].w_up.weight.data
        down_a = model_a.blocks[li].w_down.weight.data            # [d_model, d_ff]
        gate_b = model_b.blocks[li].w_gate.weight.data[perm]      # aligned to A
        up_b = model_b.blocks[li].w_up.weight.data[perm]
        down_b = model_b.blocks[li].w_down.weight.data[:, perm]
        m = cons.unsqueeze(1).float()                            # [d_ff,1] row mask
        blk.w_gate.weight.data.copy_(gate_a * (1 - m) + 0.5 * (gate_a + gate_b) * m)
        blk.w_up.weight.data.copy_(up_a * (1 - m) + 0.5 * (up_a + up_b) * m)
        mc = cons.unsqueeze(0).float()                           # [1,d_ff] col mask
        blk.w_down.weight.data.copy_(down_a * (1 - mc) + 0.5 * (down_a + down_b) * mc)
        consensus_frac.append(float(cons.float().mean().item()))
    return folded, {"consensus_frac_per_block": consensus_frac,
                    "consensus_frac_mean": float(np.mean(consensus_frac)),
                    "theta": theta}


# ---- contractivity acceptance gate (WHNF / Delta-x not rising) --------------
@torch.no_grad()
def contractivity_L(model, p_ids, cap, device, K=6, max_rows=512):
    """Run the capture-layer block as a fixed-point map x_{k+1}=x_k+block(x_k);
    return geometric L of ||Delta x|| and the per-step ratios. L<1 = contractive."""
    blk = model.blocks[cap]
    pos = torch.arange(p_ids.shape[1], device=device)
    x = model.tok(p_ids) + model.pos(pos)[None]
    # warm up to the capture layer
    for li in range(cap):
        x, _ = model.blocks[li](x)
    x = x.reshape(-1, x.shape[-1])[:max_rows]
    deltas = []
    cur = x
    for _ in range(K):
        nxt, _ = blk(cur.unsqueeze(0))
        nxt = nxt.squeeze(0)
        d = (nxt - cur).norm(dim=-1).mean() / (cur.norm(dim=-1).mean() + 1e-8)
        deltas.append(float(d.item()))
        cur = nxt
    ratios = [deltas[i + 1] / (deltas[i] + 1e-12) for i in range(len(deltas) - 1)]
    L = (float(np.exp(np.mean(np.log(np.clip(ratios, 1e-6, None)))))
         if ratios else float("nan"))
    return {"L": L, "deltas": deltas, "ratios": ratios,
            "rising": bool(deltas[-1] > deltas[0])}


# ---- one arm (REL or CTRL): train A,B then fold & measure -------------------
def run_arm(arm, g_target, args, device, shards, probe_pack, teacher, seed):
    (sA_tr, sA_ev, sB_tr, sB_ev) = shards
    (probe_ids, probe_len, probe_labels, label_idx, cap) = probe_pack
    teacher_route, _teacher_hidden = teacher
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)

    log(f"\n  === arm={arm} seed={seed} ===")
    A = train_contributor(f"{arm}/A", sA_tr, args, device, g_target, seed,
                          probe_ids, probe_len, label_idx, cap)
    B = train_contributor(f"{arm}/B", sB_tr, args, device, g_target, seed + 100,
                          probe_ids, probe_len, label_idx, cap)

    # 1. relationally identical?  (routing register vs raw b-column control)
    pbz = args.probe_batch
    gA_route, _ = routing_gram(A, p_ids, p_len, probe_labels, cap, device, pbz)
    gB_route, _ = routing_gram(B, p_ids, p_len, probe_labels, cap, device, pbz)
    gA_raw, _ = raw_gram(A, p_ids, p_len, probe_labels, cap, device, pbz)
    gB_raw, _ = raw_gram(B, p_ids, p_len, probe_labels, cap, device, pbz)
    gc_route_ab = offdiag_corr(gA_route, gB_route)
    gc_raw_ab = offdiag_corr(gA_raw, gB_raw)
    gc_route_a_teach = offdiag_corr(gA_route, teacher_route)
    gc_route_b_teach = offdiag_corr(gB_route, teacher_route)

    # 2. Re-Basin align B -> A
    perms, matched_corrs = rebasin_perms(A, B, p_ids, args.probe_batch, device)
    mc_all = np.concatenate(matched_corrs)
    fold_stats_mc = {"matched_corr_mean": float(mc_all.mean()),
                     "matched_corr_median": float(np.median(mc_all))}

    # 3. fold routing register (neuron-wise consensus merge)
    folded, fold_stats = fold_routing(A, B, perms, matched_corrs, args.theta, device)
    fold_stats.update(fold_stats_mc)

    # 4. contractivity acceptance gate
    cL_A = contractivity_L(A, p_ids, cap, device)
    cL_fold = contractivity_L(folded, p_ids, cap, device)
    accept = bool(cL_fold["L"] < 1.0 and not (cL_fold["L"] > 1.2 * cL_A["L"]))

    # 5. held-out CE: A, B, folded on BOTH shards
    ce = {
        "A_on_Aev": eval_ce(A, sA_ev, args, device),
        "A_on_Bev": eval_ce(A, sB_ev, args, device),
        "B_on_Aev": eval_ce(B, sA_ev, args, device),
        "B_on_Bev": eval_ce(B, sB_ev, args, device),
        "fold_on_Aev": eval_ce(folded, sA_ev, args, device),
        "fold_on_Bev": eval_ce(folded, sB_ev, args, device),
    }

    # routing silhouette of folded (function preserved?)
    gfold_route, sign_cmr_fold = routing_gram(
        folded, p_ids, p_len, probe_labels, cap, device, args.probe_batch)
    sil_fold = np_silhouette_null(sign_cmr_fold, probe_labels, args.n_perm, seed)
    gc_fold_teach = offdiag_corr(gfold_route, teacher_route)

    res = {
        "arm": arm, "seed": seed,
        "gramcorr_route_AB": gc_route_ab,
        "gramcorr_raw_AB": gc_raw_ab,
        "gramcorr_route_A_teacher": gc_route_a_teach,
        "gramcorr_route_B_teacher": gc_route_b_teach,
        "rebasin": "gate-activation Hungarian",
        "fold": fold_stats,
        "contractivity_A": cL_A,
        "contractivity_fold": cL_fold,
        "fold_accepted": accept,
        "ce": ce,
        "fold_route_silhouette_z": sil_fold["z"],
        "fold_route_silhouette_p": sil_fold["p_value"],
        "gramcorr_fold_teacher": gc_fold_teach,
        # decisive deltas: does folding B help on B's shard without wrecking A's?
        "delta_fold_on_Bev_vs_A": ce["fold_on_Bev"] - ce["A_on_Bev"],
        "delta_fold_on_Aev_vs_A": ce["fold_on_Aev"] - ce["A_on_Aev"],
    }
    log(f"  [{arm}] GC(route A,B)={gc_route_ab:+.3f} GC(raw A,B)={gc_raw_ab:+.3f} "
        f"| consensus={fold_stats['consensus_frac_mean']:.3f} "
        f"| L_A={cL_A['L']:.3f} L_fold={cL_fold['L']:.3f} accept={accept}")
    log(f"  [{arm}] CE A/Bev={ce['A_on_Bev']:.3f} fold/Bev={ce['fold_on_Bev']:.3f} "
        f"(Δ={res['delta_fold_on_Bev_vs_A']:+.3f}) | "
        f"A/Aev={ce['A_on_Aev']:.3f} fold/Aev={ce['fold_on_Aev']:.3f} "
        f"(Δ={res['delta_fold_on_Aev_vs_A']:+.3f})")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default="Qwen_Qwen3-14B")
    ap.add_argument("--teacher-layer", type=int, default=12)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=64)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--rel-lambda", type=float, default=3.0)
    ap.add_argument("--rel-every", type=int, default=1)
    ap.add_argument("--theta", type=float, default=0.5)
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--log-every", type=int, default=250)
    ap.add_argument("--seeds", default="0", help="csv seeds (each = a fresh A,B pair)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.n_perm, args.log_every = 40, 200, 20
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # teacher targets
    tnpz = TEACHER_DIR / f"{args.teacher}.npz"
    d = np.load(tnpz, allow_pickle=True)
    teacher_route = d[f"gram_route_cmr_L{args.teacher_layer:02d}"].astype(np.float64)
    teacher_hidden = d["gram_hidden_cmr"].astype(np.float64)
    log(f"  teacher={args.teacher} L{args.teacher_layer:02d} "
        f"route offdiag_mean={teacher_route[~np.eye(9,dtype=bool)].mean():+.3f}")

    # data: disjoint shards, each split train/eval
    corpus = to_bytes(build_corpus(), max_len=4_000_000)
    half = corpus.shape[0] // 2
    shard_a, shard_b = corpus[:half], corpus[half:]

    def split(s):
        cut = int(len(s) * 0.9)
        return s[:cut], s[cut:]
    sA_tr, sA_ev = split(shard_a)
    sB_tr, sB_ev = split(shard_b)
    log(f"  shard A train/eval={sA_tr.shape[0]}/{sA_ev.shape[0]} "
        f"B={sB_tr.shape[0]}/{sB_ev.shape[0]} (disjoint)")

    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2
    label_idx = torch.tensor([CRYSTAL.index(c) for c in probe_labels], device=device)
    probe_pack = (probe_ids, probe_len, probe_labels, label_idx, cap)
    shards = (sA_tr, sA_ev, sB_tr, sB_ev)
    teacher = (teacher_route, teacher_hidden)

    seeds = [int(s) for s in args.seeds.split(",")]
    runs = []
    for sd in seeds:
        runs.append(run_arm("REL", teacher_route, args, device, shards, probe_pack,
                            teacher, sd))
        runs.append(run_arm("CTRL", None, args, device, shards, probe_pack,
                            teacher, sd))

    def agg(arm, key_fn):
        a = np.array([key_fn(r) for r in runs if r["arm"] == arm], float)
        return [round(float(a.mean()), 4), round(float(a.std()), 4)]

    summary = {}
    for arm in ("REL", "CTRL"):
        summary[arm] = {
            "gc_route_AB": agg(arm, lambda r: r["gramcorr_route_AB"]),
            "gc_raw_AB": agg(arm, lambda r: r["gramcorr_raw_AB"]),
            "consensus_frac": agg(arm, lambda r: r["fold"]["consensus_frac_mean"]),
            "L_fold": agg(arm, lambda r: r["contractivity_fold"]["L"]),
            "fold_accept_frac": agg(arm, lambda r: float(r["fold_accepted"])),
            "delta_fold_on_Bev_vs_A": agg(arm, lambda r: r["delta_fold_on_Bev_vs_A"]),
            "delta_fold_on_Aev_vs_A": agg(arm, lambda r: r["delta_fold_on_Aev_vs_A"]),
            "fold_route_z": agg(arm, lambda r: r["fold_route_silhouette_z"]),
        }

    out = {
        "experiment": "two-contributor-fold",
        "register": "functional -> topological/routing",
        "teacher": args.teacher, "teacher_layer": args.teacher_layer,
        "git_sha": git_sha(), "smoke": args.smoke, "seeds": seeds,
        "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
        "summary": summary, "runs": runs,
    }
    tag = "smoke" if args.smoke else "run"
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== TWO-CONTRIBUTOR FOLD VERDICT (mean +/- std over seeds) ====")
    log(f"  {'arm':<6} {'GC(route)AB':>12} {'GC(raw)AB':>11} {'consensus':>10} "
        f"{'L_fold':>8} {'accept':>7} {'dCE_Bev':>9} {'dCE_Aev':>9}")
    for arm in ("REL", "CTRL"):
        s = summary[arm]
        log(f"  {arm:<6} {s['gc_route_AB'][0]:>+7.3f}+-{s['gc_route_AB'][1]:<4.3f} "
            f"{s['gc_raw_AB'][0]:>+6.3f}+-{s['gc_raw_AB'][1]:<4.3f} "
            f"{s['consensus_frac'][0]:>10.3f} {s['L_fold'][0]:>8.3f} "
            f"{s['fold_accept_frac'][0]:>7.2f} "
            f"{s['delta_fold_on_Bev_vs_A'][0]:>+9.3f} "
            f"{s['delta_fold_on_Aev_vs_A'][0]:>+9.3f}")
    log("\n  DECISIVE: REL composes cleanly iff fold ACCEPTED (L<1) AND dCE_Bev<=0 "
        "(B's routing function transferred) AND dCE_Aev not blown up;")
    log("  CTRL should fail (incommensurable frames -> raw merge = model soup).")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
