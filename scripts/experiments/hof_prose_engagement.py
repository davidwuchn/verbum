#!/usr/bin/env python3
# register: topological/routing
"""HOF prose engagement — does the model USE higher-order functions on prose?

THE QUESTION (session 225, Michael):
  s225 (function_topology_consensus) found higher-order functions have a
  universal routing topology — on CURATED probes. Does the model RECRUIT that
  topology when reading ORDINARY prose where the function is incidental?

THE TEST — transfer + minimal-pair contrast:
  Learn each HOF's routing DIRECTION from the curated probes (centroid of f minus
  the mean of the other HOFs, in the sign(gate)+CMR register). Then, on held-out
  NATURAL prose minimal pairs (a HOF-invoking sentence vs a matched no-HOF
  control), project both onto that direction and ask: does the HOF sentence score
  HIGHER than its matched control?

    direction_f = unit( centroid_curated(f) - mean_{g≠f} centroid_curated(g) )
    score(s)    = direction_f · repr(s)
    engagement  = paired[ score(hof_i) - score(control_i) ]  over prose pairs

  repr(s) = MEAN over the sentence's tokens of sign(gate pre-activation), then
  common-mode removed across all stimuli (mean-pooling avoids a last-token
  lexical confound; the curated probes are mean-pooled the same way for a fair
  transfer). Best layer chosen by curated-HOF silhouette.

  If hof > control reliably (paired t, AUC), the curated-derived HOF topology is
  recruited by natural prose ⇒ the model USES it. Transfer (train on probes, test
  on different-style prose) rules out a probe artifact.

Usage:
  uv run python scripts/experiments/hof_prose_engagement.py \
      --mode model --model Qwen/Qwen3-8B --device mps --dtype bfloat16
  uv run python scripts/experiments/hof_prose_engagement.py --mode aggregate

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.higher_order import by_function as probe_by_function
from verbum.probes.hof_prose import by_function as prose_by_function
from verbum.probes.hof_prose import function_names

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "hof-prose-engagement"

HOFS = ["map", "filter", "fold", "zip"]
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def find_gate_modules(model):
    hits = []
    pat = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod))
    hits.sort(key=lambda x: x[0])
    return hits


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


@torch.no_grad()
def collect_meanpool(model, tokenizer, device, prompts, max_length, want_layers):
    """Mean over tokens of sign(gate pre-activation) per layer. [n x d_ff]."""
    gate_mods = find_gate_modules(model)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            # out: [1, seq, d_ff] -> sign -> mean over seq
            s = torch.sign(out[0]).mean(dim=0)
            buf[li] = s.detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]
    n = len(prompts)
    pooled = {li: None for li in want}
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True,
                            max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            model(**enc)
            for li in want:
                g = buf[li]
                if pooled[li] is None:
                    pooled[li] = np.empty((n, g.shape[0]), np.float32)
                pooled[li][i] = g
            if (i + 1) % 100 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return pooled, len(gate_mods)


def cmr(X):
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def auc(pos, neg):
    """Probability a random positive scores above a random negative (Mann-Whitney)."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def silhouette(X, labels, names):
    C = np.array([X[labels == c].mean(axis=0) for c in names])
    U = np.array([unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    idx = {c: j for j, c in enumerate(names)}
    li = np.array([idx[c] for c in labels])
    own = sims[np.arange(len(labels)), li]
    sims[np.arange(len(labels)), li] = -np.inf
    return float(np.mean(own - sims.max(axis=1)))


def run_model(args):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    # curated probes (positive material for the directions) + prose pairs (test)
    cur_prompts, cur_labels = [], []
    for f in HOFS:
        for p in probe_by_function(f):
            cur_prompts.append(p.prompt)
            cur_labels.append(f)
    cur_labels = np.array(cur_labels)
    n_cur = len(cur_prompts)

    prose_prompts, prose_fn, prose_role, prose_pid = [], [], [], []
    for f in function_names():
        for pp in prose_by_function(f):
            prose_prompts.append(pp.hof)
            prose_fn.append(f)
            prose_role.append("hof")
            prose_pid.append(pp.id)
            prose_prompts.append(pp.control)
            prose_fn.append(f)
            prose_role.append("control")
            prose_pid.append(pp.id)
    prose_fn = np.array(prose_fn)
    prose_role = np.array(prose_role)

    all_prompts = cur_prompts + prose_prompts
    log(f"[{args.model}] {n_cur} curated + {len(prose_prompts)} prose = "
        f"{len(all_prompts)} forward passes")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    n_layers = len(find_gate_modules(model))
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers; capturing {want_layers}")
    pooled, n_layers = collect_meanpool(model, tok, args.device, all_prompts,
                                        args.max_length, want_layers)
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # best layer by curated HOF silhouette (mean-pooled, CMR over ALL stimuli)
    best_li, best_sil = want_layers[0], -1e9
    per_layer = {}
    for li in want_layers:
        Xc = cmr(pooled[li])[:n_cur]
        sil = silhouette(Xc, cur_labels, HOFS)
        per_layer[str(li)] = {"frac": round(li / max(n_layers - 1, 1), 3),
                              "curated_hof_silhouette": round(sil, 4)}
        if sil > best_sil:
            best_sil, best_li = sil, li
    log(f"  best layer L{best_li} (curated HOF silhouette {best_sil:+.4f})")

    X = cmr(pooled[best_li])
    Xcur, Xpro = X[:n_cur], X[n_cur:]

    # per-HOF direction from curated, transfer test on prose minimal pairs
    out_fns = {}
    for f in HOFS:
        cf = Xcur[cur_labels == f].mean(axis=0)
        crest = Xcur[cur_labels != f].mean(axis=0)
        d = unit(cf - crest)
        # curated separability (in-sample sanity)
        cur_pos = Xcur[cur_labels == f] @ d
        cur_neg = Xcur[cur_labels != f] @ d
        cur_auc = auc(cur_pos, cur_neg)
        # prose transfer: this HOF's pairs
        mask = prose_fn == f
        hof_s = Xpro[mask & (prose_role == "hof")] @ d
        ctl_s = Xpro[mask & (prose_role == "control")] @ d
        diff = hof_s - ctl_s  # paired (same order)
        sd = diff.std(ddof=1) + 1e-30
        t = float(diff.mean() / (sd / np.sqrt(len(diff))))
        out_fns[f] = {
            "curated_auc": round(cur_auc, 4),
            "n_pairs": len(diff),
            "paired_mean_diff": round(float(diff.mean()), 4),
            "paired_t": round(t, 3),
            "frac_hof_gt_control": round(float((diff > 0).mean()), 4),
            "prose_auc_hof_vs_control": round(auc(hof_s, ctl_s), 4),
        }
        log(f"    {f:>7}: curated_auc={cur_auc:.3f}  prose pairs={len(diff)}  "
            f"hof>ctl={out_fns[f]['frac_hof_gt_control']:.2f}  "
            f"t={t:+.2f}  AUC={out_fns[f]['prose_auc_hof_vs_control']:.3f}")

    out = {
        "model": args.model, "dtype": args.dtype, "register": "topological/routing",
        "pooling": "mean(sign(gate)) over tokens, CMR over stimuli",
        "n_curated": n_cur, "n_prose_sentences": len(prose_prompts),
        "n_layers": n_layers, "best_layer": int(best_li),
        "best_frac": round(best_li / max(n_layers - 1, 1), 3),
        "per_layer": per_layer, "per_function": out_fns,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"  wrote {safe}.json  ({out['elapsed_s']}s)")


def run_aggregate(args):
    files = sorted(f for f in RESULTS_DIR.glob("*.json") if f.stem != "aggregate")
    if args.models:
        want = {m.replace("/", "_") for m in args.models}
        files = [f for f in files if f.stem in want]
    if not files:
        log(f"no model jsons in {RESULTS_DIR}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    names = [m["model"] for m in models]
    log(f"aggregate over {len(models)} models: {names}")

    agg = {}
    for f in HOFS:
        cur = [m["per_function"][f]["curated_auc"] for m in models]
        auc_ = [m["per_function"][f]["prose_auc_hof_vs_control"] for m in models]
        frac = [m["per_function"][f]["frac_hof_gt_control"] for m in models]
        t = [m["per_function"][f]["paired_t"] for m in models]
        agg[f] = {
            "curated_auc_mean": round(float(np.mean(cur)), 4),
            "prose_auc_mean": round(float(np.mean(auc_)), 4),
            "prose_auc_min": round(float(np.min(auc_)), 4),
            "frac_hof_gt_control_mean": round(float(np.mean(frac)), 4),
            "paired_t_mean": round(float(np.mean(t)), 3),
            "n_models_auc_gt_0.6": int(np.sum(np.array(auc_) > 0.6)),
            "engaged": bool(np.mean(auc_) > 0.6 and np.mean(t) > 2.0),
        }
    out = {"models": names, "n_models": len(models), "per_function": agg,
           "n_engaged": sum(v["engaged"] for v in agg.values()),
           "git_sha": git_sha()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  === HOF PROSE ENGAGEMENT (transfer: train on probes, test on prose) ===")
    log(f"  {len(models)} models | repr = mean(sign(gate)) over tokens + CMR")
    log("")
    log(f"  {'HOF':>7} {'cur_AUC':>8} {'prose_AUC':>10} {'min':>6} "
        f"{'hof>ctl':>8} {'t':>7}  engaged")
    for f in HOFS:
        v = agg[f]
        log(f"  {f:>7} {v['curated_auc_mean']:>8.3f} {v['prose_auc_mean']:>10.3f} "
            f"{v['prose_auc_min']:>6.3f} {v['frac_hof_gt_control_mean']:>8.2f} "
            f"{v['paired_t_mean']:>+7.2f}  {'YES' if v['engaged'] else 'no'}")
    log("")
    log(f"  ENGAGED: {out['n_engaged']}/{len(HOFS)} HOFs recruited by natural prose")
    log("  wrote aggregate.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    args = ap.parse_args()
    if args.mode == "model":
        run_model(args)
    else:
        run_aggregate(args)


if __name__ == "__main__":
    main()
