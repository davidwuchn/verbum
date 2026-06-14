#!/usr/bin/env python3
# register: topological/routing (attention pattern, causal)
"""HOF attention ablation — are the gather heads NECESSARY? (the causal leg).

THE QUESTION (session 226, Michael): Phase A (hof_attention_gather) OBSERVED gather
heads that traverse the enumerated list, and Phase B (hof_attention_ov) OBSERVED the
OV substitution they perform. Both are observational. This script asks the CAUSAL
question that completes the "uses" claim: knock those heads out — does the model's
higher-order computation DEGRADE, more than for the matched control, and more than
for an equal number of RANDOM heads?

THE INTERVENTION — full head knockout:
  forward_pre_hook on self_attn.o_proj zeroes the head's head_dim slice of the
  post-attention input (the value the head writes to the residual stream). This
  removes BOTH the head's QK gather and its OV projection — a complete ablation,
  GQA-safe because the o_proj input is indexed over QUERY heads.

TWO READOUTS:
  (1) LIST stims (hof_lists, the data the heads were FOUND on) — KL(clean||ablated)
      of the next-token distribution at the aggregation token. A gather head is
      NECESSARY for the HOF traversal if ablating it perturbs the HOF stims' output
      MORE than the control's: KL_hof > KL_ctrl (the interaction).
  (2) PROSE pairs (hof_prose, held-out natural prose) — per-token NLL of each
      sentence, clean vs ablated. NECESSITY (generalizing) if the ablation raises
      NLL on the HOF sentence more than on its matched control:
      interaction = paired[ dNLL(hof) - dNLL(control) ] > 0  (paired t).

SPECIFICITY: the same readouts under ablation of N RANDOM heads (averaged over R
seeds). The gather heads must beat the random baseline, else the damage is generic.

Usage:
  uv run python scripts/experiments/hof_attention_ablation.py \
      --mode model --model Qwen/Qwen3-8B --device mps --dtype bfloat16
  uv run python scripts/experiments/hof_attention_ablation.py --mode aggregate

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
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.hof_lists import gather_stims
from verbum.probes.hof_prose import prose_pairs

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "hof-attention-ablation"
GATHER_DIR = _PROJECT_ROOT / "results" / "hof-attention-gather"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def find_oproj(model):
    """layer -> o_proj module."""
    out = {}
    pat = re.compile(r"\.(\d+)\.self_attn\.o_proj$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            out[int(m.group(1))] = mod
    return out


def gather_heads(model_name, override, top_n):
    """Phase-A top-N gather heads as [(layer, head), ...]."""
    if override:
        return [tuple(int(x) for x in hh.split(":")) for hh in override]
    j = GATHER_DIR / f"{model_name.replace('/', '_')}.json"
    if not j.exists():
        log(f"no Phase A json {j}; pass --heads L:H ...")
        sys.exit(1)
    d = json.loads(j.read_text())
    return [(t["layer"], t["head"]) for t in d["top_gather_heads"][:top_n]]


def by_layer(heads):
    d: dict[int, list[int]] = {}
    for (li, h) in heads:
        d.setdefault(li, []).append(h)
    return d


@contextmanager
def ablate(heads, oproj, head_dim):
    """Zero the listed query heads' contribution at each o_proj input."""
    handles = []
    for li, hs in by_layer(heads).items():

        def mk(h_list):
            def hook(_m, args):
                x = args[0].clone()
                for h in h_list:
                    x[..., h * head_dim:(h + 1) * head_dim] = 0.0
                return (x, *tuple(args[1:]))
            return hook

        handles.append(oproj[li].register_forward_pre_hook(mk(list(hs))))
    try:
        yield
    finally:
        for hnd in handles:
            hnd.remove()


@torch.no_grad()
def list_last_logits(model, tok, device, stims):
    """id -> next-token logits at the aggregation (last) token (cpu f32)."""
    res = {}
    for s in stims:
        enc = tok(s.text, return_tensors="pt")
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc)
        res[s.id] = out.logits[0, -1].float().cpu().numpy()
        del out
    return res


@torch.no_grad()
def sent_nll(model, tok, device, text, max_length):
    """Mean per-token NLL (length-robust)."""
    enc = tok(text, return_tensors="pt", truncation=True, max_length=max_length)
    enc = {k: v.to(device) for k, v in enc.items()}
    out = model(**enc)
    logits = out.logits[0].float()
    ids = enc["input_ids"][0]
    logp = torch.log_softmax(logits[:-1], dim=-1)
    tgt = ids[1:]
    nll = float(-logp[torch.arange(len(tgt)), tgt].mean().item())
    del out
    return nll


@torch.no_grad()
def prose_nlls(model, tok, device, pairs, max_length):
    """pid -> (nll_hof, nll_control)."""
    res = {}
    for p in pairs:
        res[p.id] = (sent_nll(model, tok, device, p.hof, max_length),
                     sent_nll(model, tok, device, p.control, max_length))
    return res


def _logsoftmax(x):
    x = x - x.max()
    return x - np.log(np.exp(x).sum())


def kl_pq(pl, ql):
    """KL(softmax(pl) || softmax(ql))."""
    lp = _logsoftmax(pl.astype(np.float64))
    lq = _logsoftmax(ql.astype(np.float64))
    return float((np.exp(lp) * (lp - lq)).sum())


def list_kl_metrics(clean, abl, stims):
    """Mean KL over HOF stims and control stims, and the interaction."""
    hof = [kl_pq(clean[s.id], abl[s.id]) for s in stims if s.kind == "hof"]
    ctl = [kl_pq(clean[s.id], abl[s.id]) for s in stims if s.kind == "control"]
    kh, kc = float(np.mean(hof)), float(np.mean(ctl))
    return {"kl_hof": round(kh, 5), "kl_ctrl": round(kc, 5),
            "kl_interaction": round(kh - kc, 5)}


# s225: map is NOT recruited from this register by prose; the gather-engaged HOFs are
ENGAGED_HOFS = ("fold", "reduce", "filter", "zip")


def _inter_stats(inter):
    inter = np.asarray(inter)
    sd = inter.std(ddof=1) + 1e-30
    t = float(inter.mean() / (sd / np.sqrt(len(inter))))
    return {"interaction_mean": round(float(inter.mean()), 5),
            "interaction_t": round(t, 3),
            "frac_hof_gt_ctrl": round(float((inter > 0).mean()), 4),
            "n_pairs": len(inter)}


def prose_metrics(clean, abl, pairs):
    """Per-token ΔNLL hof/control + paired interaction (overall, engaged, per-HOF).

    interaction = dNLL(hof) - dNLL(control): difference-in-differences that isolates
    HOF-specific damage from generic disruption. map excluded from the headline.
    """
    rows = []
    for p in pairs:
        ch, cc = clean[p.id]
        ah, ac = abl[p.id]
        rows.append((p.function, ah - ch, ac - cc))
    fns = np.array([r[0] for r in rows])
    dh = np.array([r[1] for r in rows])
    dc = np.array([r[2] for r in rows])
    inter = dh - dc

    per_fn = {}
    for f in sorted(set(fns)):
        m = fns == f
        per_fn[f] = {**_inter_stats(inter[m]),
                     "dNLL_hof": round(float(dh[m].mean()), 5),
                     "dNLL_ctrl": round(float(dc[m].mean()), 5)}
    eng = np.isin(fns, ENGAGED_HOFS)
    out = {"dNLL_hof": round(float(dh.mean()), 5),
           "dNLL_ctrl": round(float(dc.mean()), 5),
           **_inter_stats(inter),
           "engaged": _inter_stats(inter[eng]),
           "per_function": per_fn}
    return out


def run_model(args):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()
    stims = gather_stims()
    pairs = prose_pairs()
    heads = gather_heads(args.model, args.heads, args.top_n)
    log(f"[{args.model}] ablating {len(heads)} gather heads: {heads}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    cfg = model.config
    n_layers = cfg.num_hidden_layers
    n_heads = cfg.num_attention_heads
    oproj = find_oproj(model)
    head_dim = oproj[0].weight.shape[1] // n_heads
    log(f"  {n_layers}L x {n_heads}H, head_dim={head_dim}")

    # clean baseline
    clean_list = list_last_logits(model, tok, args.device, stims)
    clean_prose = prose_nlls(model, tok, args.device, pairs, args.max_length)

    # gather-head ablation
    with ablate(heads, oproj, head_dim):
        g_list = list_last_logits(model, tok, args.device, stims)
        g_prose = prose_nlls(model, tok, args.device, pairs, args.max_length)
    gather_list = list_kl_metrics(clean_list, g_list, stims)
    gather_prose = prose_metrics(clean_prose, g_prose, pairs)

    # random-head specificity baseline (avg over R seeds)
    rng = np.random.default_rng(args.seed)
    all_heads = [(li, h) for li in range(n_layers) for h in range(n_heads)]
    rand_list_runs, rand_prose_runs = [], []
    for r in range(args.n_random):
        idx = rng.choice(len(all_heads), size=len(heads), replace=False)
        rheads = [all_heads[i] for i in idx]
        with ablate(rheads, oproj, head_dim):
            rl = list_last_logits(model, tok, args.device, stims)
            rp = prose_nlls(model, tok, args.device, pairs, args.max_length)
        rand_list_runs.append(list_kl_metrics(clean_list, rl, stims))
        rand_prose_runs.append(prose_metrics(clean_prose, rp, pairs))
        log(f"    random draw {r + 1}/{args.n_random} done")

    def mean_of(runs, key):
        return round(float(np.mean([x[key] for x in runs])), 5)

    rand_list = {k: mean_of(rand_list_runs, k)
                 for k in ("kl_hof", "kl_ctrl", "kl_interaction")}
    rand_prose = {k: mean_of(rand_prose_runs, k)
                  for k in ("dNLL_hof", "dNLL_ctrl", "interaction_mean",
                            "interaction_t", "frac_hof_gt_ctrl")}
    rand_prose["engaged"] = {
        k: round(float(np.mean([x["engaged"][k] for x in rand_prose_runs])), 5)
        for k in ("interaction_mean", "interaction_t", "frac_hof_gt_ctrl")}

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # verdict: gather heads disrupt HOF selectively, beyond the random baseline.
    # headline = engaged HOFs (map excluded per s225); prose diff-in-diff is principled.
    g_eng = gather_prose["engaged"]
    r_eng = rand_prose["engaged"]
    list_necessary = bool(
        gather_list["kl_interaction"] > 0
        and gather_list["kl_interaction"] > rand_list["kl_interaction"])
    prose_necessary = bool(
        g_eng["interaction_mean"] > 0
        and g_eng["interaction_t"] > 2.0
        and g_eng["interaction_mean"] > r_eng["interaction_mean"])

    out = {
        "model": args.model, "dtype": args.dtype,
        "register": "topological/routing (causal ablation)",
        "intervention": "zero o_proj input slice (full head knockout)",
        "n_layers": n_layers, "n_heads": n_heads, "head_dim": head_dim,
        "n_ablated": len(heads), "gather_heads": [list(h) for h in heads],
        "n_random_draws": args.n_random, "seed": args.seed,
        "list_kl": {"gather": gather_list, "random": rand_list},
        "prose_nll": {"gather": gather_prose, "random": rand_prose},
        "list_necessary": list_necessary, "prose_necessary": prose_necessary,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} causal ablation of {len(heads)} gather heads ===")
    gl, rl = gather_list, rand_list
    gp, rp = gather_prose, rand_prose
    log(f"  LIST KL @ agg:  gather hof={gl['kl_hof']:.4f} ctrl={gl['kl_ctrl']:.4f} "
        f"inter={gl['kl_interaction']:+.4f}")
    log(f"                  random hof={rl['kl_hof']:.4f} ctrl={rl['kl_ctrl']:.4f} "
        f"inter={rl['kl_interaction']:+.4f}")
    log(f"  PROSE dNLL/tok (all):     gather inter={gp['interaction_mean']:+.4f} "
        f"t={gp['interaction_t']:+.2f} | random inter={rp['interaction_mean']:+.4f}")
    gpe, rpe = gp["engaged"], rp["engaged"]
    log(f"  PROSE dNLL/tok (engaged): gather inter={gpe['interaction_mean']:+.4f} "
        f"t={gpe['interaction_t']:+.2f} | random inter={rpe['interaction_mean']:+.4f}")
    log("  per-HOF gather interaction:")
    for f in ("map", "filter", "fold", "reduce", "zip"):
        pf = gp["per_function"].get(f)
        if pf:
            log(f"    {f:>7} inter={pf['interaction_mean']:+.4f} "
                f"t={pf['interaction_t']:+.2f} hof>ctl={pf['frac_hof_gt_ctrl']:.2f}")
    log(f"  NECESSARY (list)={list_necessary}  NECESSARY (prose)={prose_necessary}")
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
    rows = []
    for m in models:
        ge = m["prose_nll"]["gather"]["engaged"]
        re_ = m["prose_nll"]["random"]["engaged"]
        rows.append({
            "model": m["model"],
            "list_kl_inter_gather": m["list_kl"]["gather"]["kl_interaction"],
            "list_kl_inter_random": m["list_kl"]["random"]["kl_interaction"],
            "prose_eng_inter_gather": ge["interaction_mean"],
            "prose_eng_t_gather": ge["interaction_t"],
            "prose_eng_inter_random": re_["interaction_mean"],
            "list_necessary": m["list_necessary"],
            "prose_necessary": m["prose_necessary"],
        })
    out = {"models": [m["model"] for m in models], "rows": rows,
           "n_list_necessary": sum(r["list_necessary"] for r in rows),
           "n_prose_necessary": sum(r["prose_necessary"] for r in rows),
           "git_sha": git_sha()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === CAUSAL ABLATION OF GATHER HEADS (necessity, gather vs random) ===")
    log("  prose = ENGAGED HOFs (fold/reduce/filter/zip; map excluded per s225)")
    log(f"  {'model':>26} {'lstKLg':>7} {'lstKLr':>7} {'prsG':>7} "
        f"{'prsT':>6} {'prsR':>7} need(L/P)")
    for r in rows:
        log(f"  {r['model']:>26} {r['list_kl_inter_gather']:>+7.4f} "
            f"{r['list_kl_inter_random']:>+7.4f} {r['prose_eng_inter_gather']:>+7.4f} "
            f"{r['prose_eng_t_gather']:>+6.2f} {r['prose_eng_inter_random']:>+7.4f} "
            f"{'Y' if r['list_necessary'] else 'n'}/"
            f"{'Y' if r['prose_necessary'] else 'n'}")
    log(f"  list-necessary {out['n_list_necessary']}/{len(rows)}; "
        f"prose-necessary {out['n_prose_necessary']}/{len(rows)}")
    log("  wrote aggregate.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], default="model")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--heads", nargs="*", default=None,
                    help="override ablated heads as L:H (default: Phase A top-N)")
    ap.add_argument("--top-n", type=int, default=8,
                    help="number of Phase-A gather heads to ablate")
    ap.add_argument("--n-random", type=int, default=3,
                    help="random-head specificity draws to average")
    ap.add_argument("--seed", type=int, default=0)
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
