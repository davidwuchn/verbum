#!/usr/bin/env python3
# register: topological/routing (attention OV circuit)
"""HOF attention OV — the PROJECTION attention calculates (Phase B).

THE QUESTION (session 225, Michael): "attention can only do β-reduction through a
projection ... we see it in WHAT IT IS ATTENDING TO and WHAT THE PROJECTIONS ARE
that it calculates." β-reduction = substitution = the OV circuit:
PATTERN (QK, which source) ∘ PROJECTION (V→O, the value moved).

PHASE A (hof_attention_gather.py) found GATHER heads — the PATTERN that traverses
the enumerated list. PHASE B (this script): at those heads, decompose the per-head
OV output and measure how much of the VALUE MOVED to the aggregation token comes
from the list positions (the substituted term) — HOF vs control.

  per head h (handling GQA: query head h reads kv head h // group):
    v_h[src]      = value vector for head h at source src
    wlist         = Σ_{src∈items} A[dest,src] · v_h[src]      (value gathered from list)
    wall          = Σ_{src}        A[dest,src] · v_h[src]      (head's full moved value)
    W_O^h         = o_proj columns for head h
    ov_list_frac  = ||W_O^h wlist|| / ||W_O^h wall||      (substitution from the list)

  A SUBSTITUTION head: high ov_list_frac on HOF (moves the items' values), low on the
  single-item control. ov_list_frac vs attn_mass_list shows if the head AMPLIFIES the
  items' values beyond merely attending.

Usage:
  uv run python scripts/experiments/hof_attention_ov.py \
      --model Qwen/Qwen3-8B --device mps --dtype bfloat16   # heads from Phase A json

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
from verbum.probes.hof_lists import gather_stims

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "hof-attention-ov"
GATHER_DIR = _PROJECT_ROOT / "results" / "hof-attention-gather"

HOF = ["map", "fold", "filter"]
CTRL = "first"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def item_spans(stim):
    text, spans, cur = stim.text, [], len(stim.prefix)
    for it in stim.items:
        s = text.index(it, cur)
        spans.append((s, s + len(it)))
        cur = s + len(it)
    return spans


def item_token_positions(offsets, spans):
    pos = []
    for ti, (ts, te) in enumerate(offsets):
        if te <= ts:
            continue
        if any(ts < e and te > s for (s, e) in spans):
            pos.append(ti)
    return pos


def find_attn(model):
    """layer -> (v_proj module, o_proj weight)."""
    vmods, owts = {}, {}
    pat = re.compile(r"\.(\d+)\.self_attn\.(v_proj|o_proj)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            li, kind = int(m.group(1)), m.group(2)
            if kind == "v_proj":
                vmods[li] = mod
            else:
                owts[li] = mod.weight
    return vmods, owts


def target_heads(model_name, override):
    if override:
        return [tuple(int(x) for x in hh.split(":")) for hh in override]
    j = GATHER_DIR / f"{model_name.replace('/', '_')}.json"
    if not j.exists():
        log(f"no Phase A json {j}; pass --heads L:H ...")
        sys.exit(1)
    d = json.loads(j.read_text())
    return [(t["layer"], t["head"]) for t in d["top_gather_heads"][:8]]


@torch.no_grad()
def run_model(args):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()
    stims = gather_stims()
    heads = target_heads(args.model, args.heads)
    layers_needed = sorted({li for (li, _h) in heads})
    log(f"[{args.model}] OV at {len(heads)} heads: {heads}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, attn_implementation="eager")
    model.to(args.device).eval()
    cfg = model.config
    n_heads = cfg.num_attention_heads
    n_kv = getattr(cfg, "num_key_value_heads", n_heads)
    hd = getattr(cfg, "head_dim", None) or (cfg.hidden_size // n_heads)
    group = n_heads // n_kv
    log(f"  n_heads={n_heads} n_kv={n_kv} head_dim={hd} group={group}")

    vmods, owts = find_attn(model)
    vbuf = {}

    def mk_hook(li):
        def hook(_m, _i, out):
            vbuf[li] = out[0].detach().float().cpu().numpy()  # [seq, n_kv*hd]
        return hook

    handles = [vmods[li].register_forward_hook(mk_hook(li)) for li in layers_needed]

    # per head: lists of ov_list_frac and attn_mass keyed by function group
    acc = {(li, h): {"hof_frac": [], "ctrl_frac": [], "hof_mass": [],
                     "ctrl_mass": []} for (li, h) in heads}
    try:
        for stim in stims:
            enc = tok(stim.text, return_tensors="pt", return_offsets_mapping=True)
            offsets = enc.pop("offset_mapping")[0].tolist()
            ipos = item_token_positions(offsets, item_spans(stim))
            if len(ipos) < (1 if stim.kind == "control" else 2):
                continue
            vbuf.clear()
            enc = {k: v.to(args.device) for k, v in enc.items()}
            out = model(**enc, output_attentions=True)
            dest = enc["input_ids"].shape[1] - 1
            seq = enc["input_ids"].shape[1]
            ip = np.array(ipos)
            is_hof = stim.kind == "hof"
            for (li, h) in heads:
                A = out.attentions[li][0, h, dest, :].float().cpu().numpy()  # [seq]
                v = vbuf[li].reshape(seq, n_kv, hd)[:, h // group, :]        # [seq, hd]
                wall = (A[:, None] * v).sum(axis=0)                          # [hd]
                wlist = (A[ip, None] * v[ip]).sum(axis=0)
                wo = owts[li][:, h * hd:(h + 1) * hd]
                Wo = wo.float().cpu().numpy()
                pall = Wo @ wall
                plist = Wo @ wlist
                frac = float(np.linalg.norm(plist) / (np.linalg.norm(pall) + 1e-30))
                mass = float(A[ip].sum())
                k = "hof" if is_hof else "ctrl"
                acc[(li, h)][f"{k}_frac"].append(frac)
                acc[(li, h)][f"{k}_mass"].append(mass)
            del out
    finally:
        for hnd in handles:
            hnd.remove()
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    rows = []
    for (li, h) in heads:
        a = acc[(li, h)]
        hf = float(np.mean(a["hof_frac"]))
        cf = float(np.mean(a["ctrl_frac"]))
        hm = float(np.mean(a["hof_mass"]))
        cm = float(np.mean(a["ctrl_mass"]))
        rows.append({
            "layer": li, "head": h,
            "ov_list_frac_hof": round(hf, 4), "ov_list_frac_ctrl": round(cf, 4),
            "ov_frac_selectivity": round(hf - cf, 4),
            "attn_mass_hof": round(hm, 4), "attn_mass_ctrl": round(cm, 4),
            "ov_amplifies_over_attn": round(hf - hm, 4),
        })
    rows.sort(key=lambda r: -r["ov_frac_selectivity"])
    out = {"model": args.model, "register": "attention-OV",
           "n_heads": n_heads, "n_kv": n_kv, "head_dim": hd, "group": group,
           "heads": rows, "git_sha": git_sha(),
           "elapsed_s": round(time.time() - t0, 1)}
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} OV: value moved FROM list positions (HOF vs ctrl) ===")
    log(f"  {'head':>8} {'ovHOF':>6} {'ovCTRL':>7} {'ovSEL':>7} "
        f"{'attnHOF':>8} {'amplify':>8}")
    for r in rows:
        log(f"  L{r['layer']:02d}H{r['head']:02d} {r['ov_list_frac_hof']:>6.3f} "
            f"{r['ov_list_frac_ctrl']:>7.3f} {r['ov_frac_selectivity']:>+7.3f} "
            f"{r['attn_mass_hof']:>8.3f} {r['ov_amplifies_over_attn']:>+8.3f}")
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
    out = {"models": [], "git_sha": git_sha()}
    log("")
    log("  === ATTENTION OV (value substituted from the list, best head/model) ===")
    log(f"  {'model':>26} {'ovHOF':>6} {'ovCTRL':>7} {'ovSEL':>7} {'amplify':>8} head")
    for m in models:
        best = m["heads"][0]
        out["models"].append({"model": m["model"], "best": best})
        log(f"  {m['model']:>26} {best['ov_list_frac_hof']:>6.3f} "
            f"{best['ov_list_frac_ctrl']:>7.3f} {best['ov_frac_selectivity']:>+7.3f} "
            f"{best['ov_amplifies_over_attn']:>+8.3f} "
            f"L{best['layer']}H{best['head']}")
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("  wrote aggregate.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], default="model")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--heads", nargs="*", default=None,
                    help="override target heads as L:H (default: Phase A top-8)")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    args = ap.parse_args()
    if args.mode == "model":
        run_model(args)
    else:
        run_aggregate(args)


if __name__ == "__main__":
    main()
