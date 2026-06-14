#!/usr/bin/env python3
# register: functional
"""Fold-then-train-continuation — does a FOLDED routing geometry (the function
INVENTORY) let a TRAINED continuation (the USAGE) recover capability faster than a
random inventory?  (session 224, the decisive test of Michael's thesis)

THE THESIS (Michael, s224, after the 2-contributor fold):
  "Capability won't EVER transfer with just routing geometry. The capability needs
   to be TRAINED so the model can understand how to USE the functions the routing
   geometry gives it."
  => routing geometry = function INVENTORY (which combinators exist + relations).
     capability       = USAGE = the CONTINUATION (how to drive them), TRAINED not
                        folded.  geometry match is NECESSARY, NOT SUFFICIENT.

THE 2-CONTRIBUTOR FOLD (s224) showed: a REL fold KEEPS the function geometry
(GC fold->teacher +0.84) but RAISES CE (dCE +0.15) -- geometry present, usage broken.

THE TEST:
  Build a REL fold F (folded routing geometry). FREEZE the routing register (w_gate
  = the inventory). TRAIN the continuation (everything else = attn, w_up, w_down,
  head, ln, emb = the USAGE) for K steps. Compare CE-recovery trajectories of:
    F_cont      : folded inventory (frozen w_gate)  + trained continuation
    A_cont      : contributor-A solo inventory      + trained continuation
    scratch_cont: RANDOM inventory (frozen w_gate)  + trained continuation
  plus measure whether the folded function GEOMETRY PERSISTS through continuation
  training (fold_route_z before vs after) -- the punctuate-don't-churn protocol:
  hold the topology/inventory, train the continuation.

FALSIFIABLE:
  thesis CONFIRMED if F_cont (and A_cont) recover CE to ~A-baseline AND clearly beat
  scratch_cont (good frozen inventory >> random), i.e. a TRAINED continuation on a
  GOOD frozen inventory = capability.
  thesis REFUTED if F_cont ~ scratch_cont (the folded inventory is inert -- a random
  one would do as well -> geometry buys nothing).

Usage:
  uv run python scripts/experiments/fold_then_train_continuation.py --smoke
  uv run python scripts/experiments/fold_then_train_continuation.py \
      --distill-steps 1500 --cont-steps 1000 --device mps

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

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from relational_loss_distillation import (  # noqa: E402
    CRYSTAL,
    VOCAB,
    TinyLM,
    build_corpus,
    git_sha,
    load_crystal_probe_batch,
    log,
    np_centroids,
    np_gram,
    np_silhouette_null,
    offdiag_corr,
    to_bytes,
)
from two_contributor_fold import (  # noqa: E402
    contractivity_L,
    eval_ce,
    fold_routing,
    rebasin_perms,
    routing_gram,
    train_contributor,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "fold-then-train-continuation"
TEACHER_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"


def freeze_routing(model):
    """Freeze the routing register (w_gate = the function inventory)."""
    n = 0
    for blk in model.blocks:
        blk.w_gate.weight.requires_grad_(False)
        n += blk.w_gate.weight.numel()
        if blk.w_gate.bias is not None:
            blk.w_gate.bias.requires_grad_(False)
            n += blk.w_gate.bias.numel()
    return n


def train_continuation(name, model, shard_train, shard_eval, args, device):
    """Train everything EXCEPT the (frozen) routing register; log CE recovery."""
    frozen = freeze_routing(model)
    params = [p for p in model.parameters() if p.requires_grad]
    n_train = sum(p.numel() for p in params)
    opt = torch.optim.AdamW(params, lr=args.cont_lr)
    n, T, bs = shard_train.shape[0], args.block_size, args.batch_size
    t0 = time.time()
    traj = []
    for step in range(1, args.cont_steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack(
            [torch.from_numpy(shard_train[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(shard_train[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad()
        ce.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        if step % args.cont_log_every == 0 or step == 1:
            ev = eval_ce(model, shard_eval, args, device)
            traj.append({"step": step, "train_ce": float(ce.item()), "eval_ce": ev})
            log(f"    [{name}] step {step:5d} | train_ce {ce.item():.4f} "
                f"| eval_ce {ev:.4f} | {(time.time()-t0):.0f}s")
    return {"trajectory": traj, "frozen_params": frozen, "trained_params": n_train,
            "final_eval_ce": traj[-1]["eval_ce"] if traj else float("nan")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default="Qwen_Qwen3-14B")
    ap.add_argument("--teacher-layer", type=int, default=12)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--distill-steps", type=int, default=1500)
    ap.add_argument("--cont-steps", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=64)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--cont-lr", type=float, default=3e-4)
    ap.add_argument("--rel-lambda", type=float, default=3.0)
    ap.add_argument("--rel-every", type=int, default=1)
    ap.add_argument("--theta", type=float, default=0.5)
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--log-every", type=int, default=500)
    ap.add_argument("--cont-log-every", type=int, default=100)
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.distill_steps, args.cont_steps = 40, 60
        args.n_perm, args.log_every, args.cont_log_every = 200, 20, 20
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    args.steps = args.distill_steps  # train_contributor reads .steps

    tnpz = TEACHER_DIR / f"{args.teacher}.npz"
    d = np.load(tnpz, allow_pickle=True)
    teacher_route = d[f"gram_route_cmr_L{args.teacher_layer:02d}"].astype(np.float64)
    log(f"  teacher={args.teacher} L{args.teacher_layer:02d}")

    # data: full corpus = the task (train/eval); shards A,B (disjoint) build A,B
    corpus = to_bytes(build_corpus(), max_len=4_000_000)
    cut = int(len(corpus) * 0.9)
    task_train, task_eval = corpus[:cut], corpus[cut:]
    half = task_train.shape[0] // 2
    shard_a, shard_b = task_train[:half], task_train[half:]
    log(f"  task train/eval={task_train.shape[0]}/{task_eval.shape[0]} "
        f"shards A/B={shard_a.shape[0]}/{shard_b.shape[0]}")

    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2
    label_idx = torch.tensor([CRYSTAL.index(c) for c in probe_labels], device=device)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)

    def fold_route_z(model):
        _, sign_cmr = routing_gram(model, p_ids, p_len, probe_labels, cap, device,
                                   args.probe_batch)
        sil = np_silhouette_null(sign_cmr, probe_labels, args.n_perm, 0)
        g = np_gram(np_centroids(sign_cmr, probe_labels))
        return sil["z"], offdiag_corr(g, teacher_route)

    seeds = [int(s) for s in args.seeds.split(",")]
    runs = []
    for sd in seeds:
        log(f"\n  ===== seed {sd} =====")
        # 1. build REL contributors A,B and fold F
        log("  -- distill A,B (REL) --")
        A = train_contributor("A", shard_a, args, device, teacher_route, sd,
                              probe_ids, probe_len, label_idx, cap)
        B = train_contributor("B", shard_b, args, device, teacher_route, sd + 100,
                              probe_ids, probe_len, label_idx, cap)
        perms, matched = rebasin_perms(A, B, p_ids, args.probe_batch, device)
        F_fold, fstats = fold_routing(A, B, perms, matched, args.theta, device)

        a_base = eval_ce(A, task_eval, args, device)
        f_pre = eval_ce(F_fold, task_eval, args, device)
        z_f_pre, gc_f_pre = fold_route_z(F_fold)
        z_a, gc_a = fold_route_z(A)
        log(f"  baselines: A_eval={a_base:.4f} F_pre={f_pre:.4f} "
            f"(dCE={f_pre-a_base:+.4f}) | F geom z={z_f_pre:+.2f} GC={gc_f_pre:+.3f}")

        # 2. continuation training arms (freeze w_gate, train the rest)
        log("  -- continuation training (freeze routing, train usage) --")
        scratch = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff,
                         args.block_size).to(device)
        arms = {
            "F_cont": copy.deepcopy(F_fold),
            "A_cont": copy.deepcopy(A),
            "scratch_cont": scratch,
        }
        arm_out = {}
        for nm, mdl in arms.items():
            r = train_continuation(nm, mdl, task_train, task_eval, args, device)
            if nm == "F_cont":
                z_post, gc_post = fold_route_z(mdl)
                r["geom_z_post"] = z_post
                r["geom_gc_post"] = gc_post
            r["L_after"] = contractivity_L(mdl, p_ids, cap, device)["L"]
            arm_out[nm] = r

        runs.append({
            "seed": sd,
            "a_baseline_eval_ce": a_base,
            "fold_pre_eval_ce": f_pre,
            "fold_dCE_pre": f_pre - a_base,
            "fold_geom_z_pre": z_f_pre, "fold_geom_gc_pre": gc_f_pre,
            "a_geom_z": z_a, "a_geom_gc": gc_a,
            "fold_stats": fstats,
            "arms": arm_out,
        })

    def arm_final(arm):
        a = np.array([r["arms"][arm]["final_eval_ce"] for r in runs], float)
        return [round(float(a.mean()), 4), round(float(a.std()), 4)]

    def ms(key):
        a = np.array([r[key] for r in runs], float)
        return [round(float(a.mean()), 4), round(float(a.std()), 4)]

    summary = {
        "a_baseline": ms("a_baseline_eval_ce"),
        "fold_pre": ms("fold_pre_eval_ce"),
        "F_cont_final": arm_final("F_cont"),
        "A_cont_final": arm_final("A_cont"),
        "scratch_cont_final": arm_final("scratch_cont"),
        "fold_geom_z_pre": ms("fold_geom_z_pre")[0],
        "fold_geom_z_post": round(
            float(np.mean([r["arms"]["F_cont"].get("geom_z_post", float("nan"))
                           for r in runs])), 3),
    }

    out = {
        "experiment": "fold-then-train-continuation",
        "register": "functional",
        "thesis": "geometry=inventory(foldable); capability=continuation(trained)",
        "teacher": args.teacher, "teacher_layer": args.teacher_layer,
        "git_sha": git_sha(), "smoke": args.smoke, "seeds": seeds,
        "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
        "summary": summary, "runs": runs,
    }
    tag = "smoke" if args.smoke else "run"
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== FOLD-THEN-TRAIN-CONTINUATION VERDICT (mean +/- std) ====")
    log(f"  A baseline eval CE          : {summary['a_baseline'][0]:.4f}")
    log(f"  fold PRE-continuation eval CE: {summary['fold_pre'][0]:.4f} "
        f"(dCE {summary['fold_pre'][0]-summary['a_baseline'][0]:+.4f})")
    log(f"  F_cont      final eval CE    : {summary['F_cont_final'][0]:.4f} "
        f"+- {summary['F_cont_final'][1]:.4f}")
    log(f"  A_cont      final eval CE    : {summary['A_cont_final'][0]:.4f} "
        f"+- {summary['A_cont_final'][1]:.4f}")
    log(f"  scratch_cont final eval CE   : {summary['scratch_cont_final'][0]:.4f} "
        f"+- {summary['scratch_cont_final'][1]:.4f}")
    log(f"  folded geometry z: pre={summary['fold_geom_z_pre']:+.2f} "
        f"post-continuation={summary['fold_geom_z_post']:+.2f} (persistence)")
    log("\n  THESIS CONFIRMED if F_cont ~ A_cont <= A-baseline AND << scratch_cont")
    log("  (good frozen inventory + trained continuation = capability);")
    log("  REFUTED if F_cont ~ scratch_cont (folded inventory inert).")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
