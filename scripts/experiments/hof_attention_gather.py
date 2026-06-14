#!/usr/bin/env python3
# register: topological/routing (attention pattern)
"""HOF attention gather — see attention DO the fold (what it attends to).

THE QUESTION (session 225, Michael): "attention can only do beta reduction
through a projection, so where we will see attention working is in WHAT IT IS
ATTENDING TO, and WHAT THE PROJECTIONS ARE that it calculates."

PHASE A (this script): the PATTERN — what it attends to. On list-structured prose
(same list, different task), at the aggregation token, measure attention mass over
the enumerated item positions, per (layer, head). A GATHER / FOLD head attends
BROADLY over ALL items when the task iterates (map/fold/filter) but FOCUSES on one
item for the control (first). That head is attention performing the higher-order
function's traversal — the QK half of the β-reduction (the OV/value-projection half
is Phase B).

  metrics at the last token, per (layer, head):
    gather_mass    = sum attn[dest, item_positions]       (how much of the list)
    participation  = (sum a)^2 / sum(a^2) over items      (effective # attended)
  a fold/gather head: high HOF gather_mass, low control gather_mass,
  HOF participation ~ number of items.

Usage:
  uv run python scripts/experiments/hof_attention_gather.py \
      --model Qwen/Qwen3-8B --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.hof_lists import function_names, gather_stims

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "hof-attention-gather"

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


def item_spans(stim) -> list[tuple[int, int]]:
    """Char spans of each item in stim.text, located by a running cursor."""
    text = stim.text
    spans, cur = [], len(stim.prefix)
    for it in stim.items:
        s = text.index(it, cur)
        spans.append((s, s + len(it)))
        cur = s + len(it)
    return spans


def item_token_positions(offsets, spans) -> list[int]:
    """Token indices whose offset overlaps any item char span."""
    pos = []
    for ti, (ts, te) in enumerate(offsets):
        if te <= ts:  # special token (0,0)
            continue
        if any(ts < e and te > s for (s, e) in spans):
            pos.append(ti)
    return pos


@torch.no_grad()
def run_model(args):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()
    stims = gather_stims()

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, attn_implementation="eager")
    model.to(args.device).eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    log(f"[{args.model}] {len(stims)} stims; {n_layers}L x {n_heads}H")

    # gather_mass[func] -> running [L, H] sum + count; participation similarly
    gm = {f: np.zeros((n_layers, n_heads)) for f in function_names()}
    pr = {f: np.zeros((n_layers, n_heads)) for f in function_names()}
    cnt = {f: 0 for f in function_names()}

    for si, stim in enumerate(stims):
        enc = tok(stim.text, return_tensors="pt", return_offsets_mapping=True)
        offsets = enc.pop("offset_mapping")[0].tolist()
        spans = item_spans(stim)
        ipos = item_token_positions(offsets, spans)
        if len(ipos) < (1 if stim.kind == "control" else 2):
            log(f"  ! {stim.id}: only {len(ipos)} item tokens, skip")
            continue
        enc = {k: v.to(args.device) for k, v in enc.items()}
        out = model(**enc, output_attentions=True)
        dest = enc["input_ids"].shape[1] - 1
        ip = np.array(ipos)
        for li in range(n_layers):
            A = out.attentions[li][0, :, dest, :].float().cpu().numpy()  # [H, seq]
            a_items = A[:, ip]                                            # [H, |items|]
            mass = a_items.sum(axis=1)                                    # [H]
            part = (mass ** 2) / (np.sum(a_items ** 2, axis=1) + 1e-30)   # [H]
            gm[stim.function][li] += mass
            pr[stim.function][li] += part
        cnt[stim.function] += 1
        del out
        if (si + 1) % 8 == 0:
            log(f"    {si + 1}/{len(stims)}")

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    for f in function_names():
        if cnt[f]:
            gm[f] /= cnt[f]
            pr[f] /= cnt[f]

    # HOF gather = mean over HOF tasks; control gather = `first`
    hof_gm = np.mean([gm[f] for f in HOF], axis=0)        # [L,H]
    ctrl_gm = gm[CTRL]
    hof_pr = np.mean([pr[f] for f in HOF], axis=0)
    sel = hof_gm - ctrl_gm                                # gather selectivity [L,H]

    # top gather/fold heads
    flat = [(int(li), int(h), float(sel[li, h]), float(hof_gm[li, h]),
             float(ctrl_gm[li, h]), float(hof_pr[li, h]))
            for li in range(n_layers) for h in range(n_heads)]
    flat.sort(key=lambda x: -x[2])
    top = [{"layer": li, "head": h, "selectivity": round(s, 4),
            "hof_gather": round(hg, 4), "ctrl_gather": round(cg, 4),
            "hof_participation": round(pp, 4)}
           for (li, h, s, hg, cg, pp) in flat[:15]]

    out = {
        "model": args.model, "dtype": args.dtype,
        "register": "attention-pattern", "n_layers": n_layers, "n_heads": n_heads,
        "counts": cnt, "n_items_mean": None,
        "per_function_gather_max_head": {f: round(float(gm[f].max()), 4)
                                         for f in function_names()},
        "hof_gather_max": round(float(hof_gm.max()), 4),
        "ctrl_gather_at_hof_argmax": round(
            float(ctrl_gm[np.unravel_index(hof_gm.argmax(), hof_gm.shape)]), 4),
        "max_selectivity": round(float(sel.max()), 4),
        "hof_participation_at_sel_argmax": round(
            float(hof_pr[np.unravel_index(sel.argmax(), sel.shape)]), 4),
        "top_gather_heads": top,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    np.savez_compressed(RESULTS_DIR / f"{safe}.npz",
                        hof_gather=hof_gm.astype(np.float32),
                        ctrl_gather=ctrl_gm.astype(np.float32),
                        selectivity=sel.astype(np.float32),
                        hof_participation=hof_pr.astype(np.float32))
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} attention gather over enumerated items ===")
    log(f"  HOF gather_max {out['hof_gather_max']:.3f} "
        f"(ctrl at same head {out['ctrl_gather_at_hof_argmax']:.3f})")
    log(f"  max selectivity (HOF-ctrl) {out['max_selectivity']:+.3f}; "
        f"participation there {out['hof_participation_at_sel_argmax']:.2f}")
    log("  top gather/fold heads (HOF gathers list, ctrl does not):")
    for t in top[:8]:
        log(f"    L{t['layer']:02d}H{t['head']:02d} sel={t['selectivity']:+.3f} "
            f"hof={t['hof_gather']:.3f} ctrl={t['ctrl_gather']:.3f} "
            f"part={t['hof_participation']:.2f}")
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
    log(f"aggregate over {len(models)} models")
    rows = []
    for m in models:
        rows.append({
            "model": m["model"],
            "hof_gather_max": m["hof_gather_max"],
            "ctrl_at_hof_argmax": m["ctrl_gather_at_hof_argmax"],
            "max_selectivity": m["max_selectivity"],
            "participation": m["hof_participation_at_sel_argmax"],
            "best_head": (m["top_gather_heads"][0]["layer"],
                          m["top_gather_heads"][0]["head"]),
        })
    out = {"models": [m["model"] for m in models], "rows": rows,
           "git_sha": git_sha()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === ATTENTION GATHER (HOF vs control over enumerated items) ===")
    log(f"  {'model':>26} {'hof_gat':>8} {'ctrl':>6} {'sel':>7} {'part':>6} best")
    for r in rows:
        log(f"  {r['model']:>26} {r['hof_gather_max']:>8.3f} "
            f"{r['ctrl_at_hof_argmax']:>6.3f} {r['max_selectivity']:>+7.3f} "
            f"{r['participation']:>6.2f} L{r['best_head'][0]}H{r['best_head'][1]}")
    log("  wrote aggregate.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], default="model")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--models", nargs="*", default=None)
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
