#!/usr/bin/env python3
# register: topological/routing (causal ablation, VALUE register via logit lens)
"""HOF OV logit-lens ablation — read the β-reduction in the VALUE register at the
READABLE layers, not surface NLL.

THE QUESTION (session 227, Michael): "are we looking in the right place?" The s227
surface-NLL ablation found prose necessity only 1/5 (vs mechanism 4/5), and the
continuation-KL readout was NULL. Recall (compilation-pipeline.md s192 / FFN
reduction trace s187): mid-stack (L7-L22) the reduction is written ORTHOGONAL to
vocabulary (null-space composition); it becomes vocabulary-READABLE only at L23-L35.
A surface next-token readout integrates the whole stack and is dominated by the EMIT
layers → it misses a mid-stack null-space substitution. See
`mementum/knowledge/explore/readout-register-reduction-readability.md`.

THE INSTRUMENT — logit lens at every layer:
  Decode the residual stream "as if output here": lm_head(final_norm(residual_L)) at
  the readout position, for every layer L. Metric = per-layer KL(clean_L || ablated_L)
  of that decode. This reads the VALUE register (the residual the OV wrote into) at
  every locus, so we can SEE at which depth removing the gather heads damages the
  readable decode.

INTERVENTION: same full head-knockout as hof_attention_ablation (zero the head's
slice at o_proj input = remove its QK gather + OV write), for the Phase-A top-N
gather heads, vs N RANDOM heads (specificity, R draws).

DIFF-IN-DIFF: HOF - control isolates HOF-specific damage.
  - LIST stims (hof_lists): hof = map/fold/filter, control = `first`.
  - PROSE pairs (hof_prose): HOF sentence vs its matched control; engaged HOFs
    (fold/reduce/filter/zip; map excluded per s225) for the headline.

HEADLINE: the READABLE-ZONE (depth ≥ 0.6, i.e. ~L23-L35) mean diff-in-diff, compared
to the SURFACE (last-layer) diff — the s227 readout. Prediction: gather-head damage
is HOF-selective and CONCENTRATED in the readable zone, larger there than at the
surface. If flat / not above random, the s227 power verdict stands.

Usage:
  uv run python scripts/experiments/hof_ov_logitlens_ablation.py \
      --model Qwen/Qwen3-8B --device mps --dtype bfloat16
  uv run python scripts/experiments/hof_ov_logitlens_ablation.py --mode aggregate

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_SCRIPT_DIR))

import hof_attention_ablation as A  # noqa: E402  (ablate/find_oproj/gather_heads/kl)

from verbum.probes.hof_lists import gather_stims  # noqa: E402
from verbum.probes.hof_prose import prose_pairs as _plain_prose  # noqa: E402
from verbum.probes.hof_prose_enum import prose_pairs as _enum_prose  # noqa: E402

ENGAGED_HOFS = ("fold", "reduce", "filter", "zip")
READABLE_DEPTH = 0.6  # compilation-pipeline: vocab-readable zone L23-L35 ~ depth 0.64+


def load_prose(name):
    """plain = hof_prose (no enumeration); enum = hof_prose_enum (literal list)."""
    return _enum_prose() if name == "enum" else _plain_prose()


def results_dir(prose_set):
    sub = "hof-ov-logitlens-enum" if prose_set == "enum" else "hof-ov-logitlens"
    return _PROJECT_ROOT / "results" / sub


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


@torch.no_grad()
def capture(model, tok, device, items, heads, oproj, head_dim, n_layers, norm, lmhead):
    """key -> ndarray[n_layers, vocab] float16: logit-lens decode at the LAST token
    of each layer's residual. `heads`=None → clean; else ablate those heads."""
    res = {}
    ctx = A.ablate(heads, oproj, head_dim) if heads is not None else nullcontext()
    with ctx:
        for key, text in items:
            enc = tok(text, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True)
            hs = out.hidden_states  # len n_layers+1; hs[0]=embed, hs[li+1]=block li
            mat = np.empty((n_layers, lmhead.weight.shape[0]), dtype=np.float16)
            for li in range(n_layers):
                x = hs[li + 1][0, -1].unsqueeze(0)          # (1, d_model) last token
                lg = lmhead(norm(x))[0]                      # (vocab,)
                mat[li] = lg.float().cpu().numpy().astype(np.float16)
            res[key] = mat
            del out
    return res


def kl_layers(a, b):
    """Per-layer KL(softmax(a) || softmax(b)). a,b: (n_layers, vocab)."""
    a = a.astype(np.float64) - a.astype(np.float64).max(axis=1, keepdims=True)
    b = b.astype(np.float64) - b.astype(np.float64).max(axis=1, keepdims=True)
    la = a - np.log(np.exp(a).sum(axis=1, keepdims=True))
    lb = b - np.log(np.exp(b).sum(axis=1, keepdims=True))
    return (np.exp(la) * (la - lb)).sum(axis=1)


def list_diff(clean, abl, stims):
    """Per-layer diff-in-diff for list stims: mean KL over hof minus over control."""
    hof = [s.id for s in stims if s.kind == "hof"]
    ctl = [s.id for s in stims if s.kind == "control"]
    kh = np.mean([kl_layers(clean[i], abl[i]) for i in hof], axis=0)
    kc = np.mean([kl_layers(clean[i], abl[i]) for i in ctl], axis=0)
    return kh, kc, kh - kc


def prose_diff(clean, abl, pairs, engaged_only):
    """Per-layer diff-in-diff for prose: mean over pairs of (KL_hof - KL_ctrl)."""
    rows = []
    for p in pairs:
        if engaged_only and p.function not in ENGAGED_HOFS:
            continue
        dh = kl_layers(clean[f"{p.id}#h"], abl[f"{p.id}#h"])
        dc = kl_layers(clean[f"{p.id}#c"], abl[f"{p.id}#c"])
        rows.append(dh - dc)
    arr = np.asarray(rows)  # (n_pairs, n_layers)
    return arr.mean(axis=0), arr  # mean profile, per-pair (for paired t)


def zone_idx(n_layers):
    return [li for li in range(n_layers) if (li + 1) / n_layers >= READABLE_DEPTH]


def run_model(args):
    results = results_dir(args.prose_set)
    results.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()
    stims = gather_stims()
    pairs = load_prose(args.prose_set)
    heads = A.gather_heads(args.model, args.heads, args.top_n)
    log(f"[{args.model}] logit-lens ablation of {len(heads)} gather heads: {heads}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    cfg = model.config
    n_layers = cfg.num_hidden_layers
    n_heads = cfg.num_attention_heads
    oproj = A.find_oproj(model)
    head_dim = oproj[0].weight.shape[1] // n_heads
    norm = model.model.norm
    lmhead = model.get_output_embeddings()
    vocab = lmhead.weight.shape[0]
    log(f"  {n_layers}L x {n_heads}H d_head={head_dim} vocab={vocab}")

    list_items = [(s.id, s.text) for s in stims]
    prose_items = []
    for p in pairs:
        prose_items.append((f"{p.id}#h", p.hof))
        prose_items.append((f"{p.id}#c", p.control))

    def cap(items, hh, _m=model, _tok=tok, _dev=args.device, _op=oproj,
            _hd=head_dim, _nl=n_layers, _nm=norm, _lm=lmhead):
        return capture(_m, _tok, _dev, items, hh, _op, _hd, _nl, _nm, _lm)

    # clean
    clean_list = cap(list_items, None)
    clean_prose = cap(prose_items, None)

    # gather ablation
    g_list_cap = cap(list_items, heads)
    g_prose_cap = cap(prose_items, heads)
    gl_hof, gl_ctl, gl_diff = list_diff(clean_list, g_list_cap, stims)
    gp_diff, gp_rows = prose_diff(clean_prose, g_prose_cap, pairs, engaged_only=True)
    del g_list_cap, g_prose_cap

    # random specificity
    rng = np.random.default_rng(args.seed)
    all_heads = [(li, h) for li in range(n_layers) for h in range(n_heads)]
    rl_diffs, rp_diffs = [], []
    for r in range(args.n_random):
        idx = rng.choice(len(all_heads), size=len(heads), replace=False)
        rheads = [all_heads[i] for i in idx]
        rl_cap = cap(list_items, rheads)
        rp_cap = cap(prose_items, rheads)
        _, _, rld = list_diff(clean_list, rl_cap, stims)
        rpd, _ = prose_diff(clean_prose, rp_cap, pairs, engaged_only=True)
        rl_diffs.append(rld)
        rp_diffs.append(rpd)
        del rl_cap, rp_cap
        log(f"    random draw {r + 1}/{args.n_random} done")
    rl_diff = np.mean(rl_diffs, axis=0)
    rp_diff = np.mean(rp_diffs, axis=0)

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    zi = zone_idx(n_layers)

    def summarize(diff, rand):
        readable = float(np.mean(diff[zi]))
        surface = float(diff[-1])
        rand_readable = float(np.mean(rand[zi]))
        peak = int(np.argmax(diff))
        return {"readable_zone_diff": round(readable, 5),
                "surface_diff": round(surface, 5),
                "random_readable_diff": round(rand_readable, 5),
                "readable_gt_surface": bool(readable > surface),
                "readable_gt_random": bool(readable > rand_readable),
                "peak_layer": peak, "peak_depth": round((peak + 1) / n_layers, 3),
                "peak_diff": round(float(diff[peak]), 5)}

    # prose paired t over engaged pairs, in the readable zone (per-pair mean over zone)
    zone_pair = gp_rows[:, zi].mean(axis=1)
    sd = zone_pair.std(ddof=1) + 1e-30
    prose_zone_t = float(zone_pair.mean() / (sd / np.sqrt(len(zone_pair))))

    out = {
        "model": args.model, "dtype": args.dtype, "prose_set": args.prose_set,
        "register": "topological/routing (causal, value register via logit lens)",
        "readout": "per-layer KL(clean||ablated) of lm_head(norm(residual_L)) "
                   "at last token; diff-in-diff hof-control; readable zone depth>=0.6",
        "n_layers": n_layers, "n_heads": n_heads, "head_dim": head_dim,
        "n_ablated": len(heads), "gather_heads": [list(h) for h in heads],
        "n_random_draws": args.n_random, "seed": args.seed,
        "readable_depth_threshold": READABLE_DEPTH,
        "list": {**summarize(gl_diff, rl_diff),
                 "layer_diff": [round(float(x), 5) for x in gl_diff],
                 "layer_diff_random": [round(float(x), 5) for x in rl_diff],
                 "layer_hof": [round(float(x), 5) for x in gl_hof],
                 "layer_ctrl": [round(float(x), 5) for x in gl_ctl]},
        "prose": {**summarize(gp_diff, rp_diff),
                  "readable_zone_t": round(prose_zone_t, 3),
                  "n_engaged_pairs": int(gp_rows.shape[0]),
                  "layer_diff": [round(float(x), 5) for x in gp_diff],
                  "layer_diff_random": [round(float(x), 5) for x in rp_diff]},
        "git_sha": A.git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (results / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} logit-lens OV ablation [{args.prose_set}] (value register) ===")
    for name in ("list", "prose"):
        s = out[name]
        rz = s["readable_zone_diff"]
        su = s["surface_diff"]
        rr = s["random_readable_diff"]
        extra = f" zoneT={s['readable_zone_t']:+.2f}" if name == "prose" else ""
        gs = s["readable_gt_surface"]
        gr = s["readable_gt_random"]
        log(f"  {name:>5}: readable={rz:+.4f} surface={su:+.4f} rand={rr:+.4f} "
            f"peak@L{s['peak_layer']}(d={s['peak_depth']}) "
            f"r>surf={gs} r>rand={gr}{extra}")
    log(f"  wrote {safe}.json  ({out['elapsed_s']}s)")


def run_aggregate(args):
    results = results_dir(args.prose_set)
    files = sorted(f for f in results.glob("*.json") if f.stem != "aggregate")
    if args.models:
        want = {m.replace("/", "_") for m in args.models}
        files = [f for f in files if f.stem in want]
    if not files:
        log(f"no model jsons in {RESULTS_DIR}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    rows = []
    for m in models:
        rows.append({
            "model": m["model"],
            "list_readable": m["list"]["readable_zone_diff"],
            "list_surface": m["list"]["surface_diff"],
            "list_r_gt_surf": m["list"]["readable_gt_surface"],
            "prose_readable": m["prose"]["readable_zone_diff"],
            "prose_surface": m["prose"]["surface_diff"],
            "prose_random": m["prose"]["random_readable_diff"],
            "prose_zone_t": m["prose"]["readable_zone_t"],
            "prose_r_gt_surf": m["prose"]["readable_gt_surface"],
            "prose_r_gt_rand": m["prose"]["readable_gt_random"],
        })
    out = {"models": [m["model"] for m in models], "rows": rows,
           "n_prose_readable_necessary":
               sum(r["prose_zone_t"] > 2.0 and r["prose_r_gt_rand"] for r in rows),
           "n_prose_readable_gt_surface": sum(r["prose_r_gt_surf"] for r in rows),
           "git_sha": A.git_sha()}
    (results / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log(f"  === LOGIT-LENS OV ABLATION [{args.prose_set}] (readable zone vs surface) ===")
    log(f"  {'model':>24} {'Lrdbl':>7} {'Lsurf':>7} {'Prdbl':>7} {'Psurf':>7} "
        f"{'Prand':>7} {'PzT':>6} r>surf(L/P) r>rand(P)")
    for r in rows:
        log(f"  {r['model']:>24} {r['list_readable']:>+7.4f} "
            f"{r['list_surface']:>+7.4f} {r['prose_readable']:>+7.4f} "
            f"{r['prose_surface']:>+7.4f} {r['prose_random']:>+7.4f} "
            f"{r['prose_zone_t']:>+6.2f} "
            f"{'Y' if r['list_r_gt_surf'] else 'n'}/"
            f"{'Y' if r['prose_r_gt_surf'] else 'n'} "
            f"{'Y' if r['prose_r_gt_rand'] else 'n'}")
    log(f"  prose readable-necessary (zoneT>2 & >rand) "
        f"{out['n_prose_readable_necessary']}/{len(rows)}; "
        f"readable>surface {out['n_prose_readable_gt_surface']}/{len(rows)}")
    log("  wrote aggregate.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], default="model")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--heads", nargs="*", default=None,
                    help="override ablated heads as L:H (default: Phase A top-N)")
    ap.add_argument("--top-n", type=int, default=8)
    ap.add_argument("--prose-set", choices=["plain", "enum"], default="plain",
                    help="plain=hof_prose (no list); enum=hof_prose_enum (literal list)")
    ap.add_argument("--n-random", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
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
