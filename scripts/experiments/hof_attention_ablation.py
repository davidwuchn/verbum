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

READOUTS:
  (1) LIST stims (hof_lists, the data the heads were FOUND on) — KL(clean||ablated)
      of the next-token distribution at the aggregation token. A gather head is
      NECESSARY for the HOF traversal if ablating it perturbs the HOF stims' output
      MORE than the control's: KL_hof > KL_ctrl (the interaction).
  (2) PROSE pairs (hof_prose, held-out natural prose), THREE readouts of the same
      diff-in-diff interaction = paired[ effect(hof) - effect(control) ] > 0:
      - region (PRIMARY, s227 IOU fix): NLL over only the DIVERGENT MIDDLE tokens
        of each minimal pair (drop the shared prefix/suffix). The HOF contrast lives
        there ('each plant' vs 'the plant'); the s226 whole-sentence average diluted
        it across ~12 mostly-shared tokens → prose leg underpowered (1/5 vs 4/5
        mechanism). Removing the shared tokens is the principled de-dilution.
      - lastkl (secondary cross-check): KL of the continuation distribution at the
        final token — the SAME metric as the list leg, for cross-leg consistency.
      - whole (s226 REFERENCE): whole-sentence mean NLL, kept to show whether
        dilution was the culprit.
      Headline prose_necessary = region.

WHY (s227): the s226 ablation found mechanism necessity 4/5 (list) but prose
generalization only 1/5 (whole-sentence NLL). The IOU was a sharper prose readout.
This script keeps the old readout and adds the two sharper ones so the comparison
is visible in one run — if region lifts prose toward 4/5, dilution is confirmed
(foundations solid); if it stays weak, prose necessity is honestly weak.

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
def forward_sent(model, tok, device, text, max_length):
    """One forward pass → per-token NLL vector + final-position next-token logits.

    Returns {ids, nll, last}:
      ids  — token id array (numpy), identical clean vs ablated (tokenization is
             weight-independent), so region bounds are computed once.
      nll  — nll[j] = NLL of predicting ids[j+1]  (len = len(ids)-1)
      last — next-token logits at the final position (numpy f32; for continuation KL)
    """
    enc = tok(text, return_tensors="pt", truncation=True, max_length=max_length)
    enc = {k: v.to(device) for k, v in enc.items()}
    out = model(**enc)
    logits = out.logits[0].float()
    ids = enc["input_ids"][0]
    logp = torch.log_softmax(logits[:-1], dim=-1)
    tgt = ids[1:]
    nll = (-logp[torch.arange(len(tgt)), tgt]).cpu().numpy()
    last = logits[-1].cpu().numpy()
    ids_np = ids.cpu().numpy()
    del out
    return {"ids": ids_np, "nll": nll, "last": last}


@torch.no_grad()
def prose_capture(model, tok, device, pairs, max_length):
    """pid -> {'hof': forward_sent(...), 'control': forward_sent(...)}.

    One capture holds everything the three prose readouts need (whole-sentence NLL,
    divergent-region NLL, continuation logits). clean and each ablation each call it.
    """
    cap = {}
    for p in pairs:
        cap[p.id] = {
            "hof": forward_sent(model, tok, device, p.hof, max_length),
            "control": forward_sent(model, tok, device, p.control, max_length),
        }
    return cap


def region_bounds(ids_a, ids_b):
    """Longest shared token (prefix_len, suffix_len) of a minimal pair.

    The divergent middle — where HOF-ness actually lives ('each plant' vs 'the
    plant') — is [prefix_len, len-suffix_len) in each sentence. The shared prefix
    ('She moved down the row and watered') and suffix ('near the') carry no
    HOF contrast and only dilute a whole-sentence average; we drop them.
    """
    n = min(len(ids_a), len(ids_b))
    p = 0
    while p < n and ids_a[p] == ids_b[p]:
        p += 1
    s = 0
    while s < n - p and ids_a[-1 - s] == ids_b[-1 - s]:
        s += 1
    return p, s


def _region_nll(sent, p, s):
    """Mean NLL over the divergent middle tokens [p, len-s) of one sentence.

    Token k (k>=1) has NLL nll[k-1]; we require left context so k starts at max(p,1).
    Falls back to whole-sentence NLL if the region is empty (defensive; minimal pairs
    differ by construction so this should not trigger).
    """
    ids, nll = sent["ids"], sent["nll"]
    start, end = max(p, 1), len(ids) - s
    ks = list(range(start, end))
    if not ks:
        return float(nll.mean())
    return float(np.mean([nll[k - 1] for k in ks]))


def _whole_nll(sent):
    """Mean per-token NLL over the whole sentence (the s226 reference readout)."""
    return float(sent["nll"].mean())


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


def _assemble(rows):
    """rows = [(function, score_hof, score_ctrl), ...] → diff-in-diff stat blocks.

    interaction = score(hof) - score(control): the difference-in-differences that
    isolates HOF-specific damage from generic disruption. Reported overall, for the
    ENGAGED HOFs (map excluded per s225), and per function. score is ΔNLL for the
    NLL readouts and KL for the continuation readout — the diff-in-diff is identical.
    """
    fns = np.array([r[0] for r in rows])
    dh = np.array([r[1] for r in rows])
    dc = np.array([r[2] for r in rows])
    inter = dh - dc
    per_fn = {}
    for f in sorted(set(fns)):
        m = fns == f
        per_fn[f] = {**_inter_stats(inter[m]),
                     "hof": round(float(dh[m].mean()), 5),
                     "ctrl": round(float(dc[m].mean()), 5)}
    eng = np.isin(fns, ENGAGED_HOFS)
    return {"hof": round(float(dh.mean()), 5),
            "ctrl": round(float(dc.mean()), 5),
            **_inter_stats(inter),
            "engaged": _inter_stats(inter[eng]),
            "per_function": per_fn}


def prose_region_metrics(clean, abl, pairs, bounds):
    """PRIMARY readout — divergent-region NLL diff-in-diff.

    Drops the shared prefix/suffix of each minimal pair and scores only the
    HOF-specific middle tokens, removing the whole-sentence dilution that left the
    s226 prose leg underpowered (1/5 vs the 4/5 mechanism leg).
    """
    rows = []
    for p in pairs:
        pp, ss = bounds[p.id]
        ch = _region_nll(clean[p.id]["hof"], pp, ss)
        cc = _region_nll(clean[p.id]["control"], pp, ss)
        ah = _region_nll(abl[p.id]["hof"], pp, ss)
        ac = _region_nll(abl[p.id]["control"], pp, ss)
        rows.append((p.function, ah - ch, ac - cc))
    return _assemble(rows)


def prose_whole_metrics(clean, abl, pairs):
    """REFERENCE readout — whole-sentence mean-NLL diff-in-diff (the s226 readout)."""
    rows = []
    for p in pairs:
        ch = _whole_nll(clean[p.id]["hof"])
        cc = _whole_nll(clean[p.id]["control"])
        ah = _whole_nll(abl[p.id]["hof"])
        ac = _whole_nll(abl[p.id]["control"])
        rows.append((p.function, ah - ch, ac - cc))
    return _assemble(rows)


def prose_lastkl_metrics(clean, abl, pairs):
    """SECONDARY readout — continuation KL at the final position (the LIST-leg metric).

    KL(clean||ablated) of the next-token distribution at the sentence's last token,
    diff-in-diff KL_hof - KL_ctrl. Same instrument as the list leg → cross-leg
    consistency. The minimal pair shares the final token, so the position is matched.
    """
    rows = []
    for p in pairs:
        kh = kl_pq(clean[p.id]["hof"]["last"], abl[p.id]["hof"]["last"])
        kc = kl_pq(clean[p.id]["control"]["last"], abl[p.id]["control"]["last"])
        rows.append((p.function, kh, kc))
    return _assemble(rows)


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

    # region bounds per pair — tokenization is weight-independent, compute once
    base_cap = prose_capture(model, tok, args.device, pairs, args.max_length)
    bounds = {p.id: region_bounds(base_cap[p.id]["hof"]["ids"],
                                  base_cap[p.id]["control"]["ids"]) for p in pairs}

    def prose_readouts(clean_cap, abl_cap):
        """All three prose readouts from one clean/ablated capture pair."""
        return {
            "region": prose_region_metrics(clean_cap, abl_cap, pairs, bounds),
            "lastkl": prose_lastkl_metrics(clean_cap, abl_cap, pairs),
            "whole": prose_whole_metrics(clean_cap, abl_cap, pairs),
        }

    # clean baseline (reuse base_cap for prose)
    clean_list = list_last_logits(model, tok, args.device, stims)
    clean_prose = base_cap

    # gather-head ablation
    with ablate(heads, oproj, head_dim):
        g_list = list_last_logits(model, tok, args.device, stims)
        g_prose_cap = prose_capture(model, tok, args.device, pairs, args.max_length)
    gather_list = list_kl_metrics(clean_list, g_list, stims)
    gather_prose = prose_readouts(clean_prose, g_prose_cap)

    # random-head specificity baseline (avg over R seeds)
    rng = np.random.default_rng(args.seed)
    all_heads = [(li, h) for li in range(n_layers) for h in range(n_heads)]
    rand_list_runs, rand_prose_runs = [], []
    for r in range(args.n_random):
        idx = rng.choice(len(all_heads), size=len(heads), replace=False)
        rheads = [all_heads[i] for i in idx]
        with ablate(rheads, oproj, head_dim):
            rl = list_last_logits(model, tok, args.device, stims)
            rp_cap = prose_capture(model, tok, args.device, pairs, args.max_length)
        rand_list_runs.append(list_kl_metrics(clean_list, rl, stims))
        rand_prose_runs.append(prose_readouts(clean_prose, rp_cap))
        log(f"    random draw {r + 1}/{args.n_random} done")

    def mean_of(runs, key):
        return round(float(np.mean([x[key] for x in runs])), 5)

    rand_list = {k: mean_of(rand_list_runs, k)
                 for k in ("kl_hof", "kl_ctrl", "kl_interaction")}

    # random baseline per readout: average the engaged diff-in-diff over draws
    def rand_readout(name):
        eng_keys = ("interaction_mean", "interaction_t", "frac_hof_gt_ctrl")
        return {"engaged": {
            k: round(float(np.mean([x[name]["engaged"][k]
                                    for x in rand_prose_runs])), 5)
            for k in eng_keys}}
    rand_prose = {name: rand_readout(name) for name in ("region", "lastkl", "whole")}

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # verdict: gather heads disrupt HOF selectively, beyond the random baseline.
    # headline = engaged HOFs (map excluded per s225); diff-in-diff is principled.
    list_necessary = bool(
        gather_list["kl_interaction"] > 0
        and gather_list["kl_interaction"] > rand_list["kl_interaction"])

    def prose_verdict(name):
        g = gather_prose[name]["engaged"]
        r = rand_prose[name]["engaged"]
        return bool(g["interaction_mean"] > 0
                    and g["interaction_t"] > 2.0
                    and g["interaction_mean"] > r["interaction_mean"])

    prose_necessary_region = prose_verdict("region")   # PRIMARY (the IOU fix)
    prose_necessary_lastkl = prose_verdict("lastkl")   # secondary cross-check
    prose_necessary_whole = prose_verdict("whole")     # s226 reference readout
    prose_necessary = prose_necessary_region           # headline = sharper readout

    out = {
        "model": args.model, "dtype": args.dtype,
        "register": "topological/routing (causal ablation)",
        "intervention": "zero o_proj input slice (full head knockout)",
        "n_layers": n_layers, "n_heads": n_heads, "head_dim": head_dim,
        "n_ablated": len(heads), "gather_heads": [list(h) for h in heads],
        "n_random_draws": args.n_random, "seed": args.seed,
        "list_kl": {"gather": gather_list, "random": rand_list},
        "prose": {
            "readout": "diff-in-diff (hof-control) of ablation effect; "
                       "region=PRIMARY (divergent-middle NLL), "
                       "lastkl=secondary (continuation KL, list-leg metric), "
                       "whole=s226 reference (whole-sentence NLL)",
            "region": {"gather": gather_prose["region"],
                       "random": rand_prose["region"]},
            "lastkl": {"gather": gather_prose["lastkl"],
                       "random": rand_prose["lastkl"]},
            "whole": {"gather": gather_prose["whole"],
                      "random": rand_prose["whole"]},
        },
        "list_necessary": list_necessary,
        "prose_necessary": prose_necessary,
        "prose_necessary_region": prose_necessary_region,
        "prose_necessary_lastkl": prose_necessary_lastkl,
        "prose_necessary_whole": prose_necessary_whole,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} causal ablation of {len(heads)} gather heads ===")
    gl, rl = gather_list, rand_list
    log(f"  LIST KL @ agg:  gather hof={gl['kl_hof']:.4f} ctrl={gl['kl_ctrl']:.4f} "
        f"inter={gl['kl_interaction']:+.4f}")
    log(f"                  random hof={rl['kl_hof']:.4f} ctrl={rl['kl_ctrl']:.4f} "
        f"inter={rl['kl_interaction']:+.4f}")
    for name in ("region", "lastkl", "whole"):
        ge = gather_prose[name]["engaged"]
        re_ = rand_prose[name]["engaged"]
        log(f"  PROSE[{name:>6}] engaged: gather inter={ge['interaction_mean']:+.4f} "
            f"t={ge['interaction_t']:+.2f} hof>ctl={ge['frac_hof_gt_ctrl']:.2f} | "
            f"random inter={re_['interaction_mean']:+.4f}")
    log("  per-HOF gather interaction (PRIMARY region readout):")
    for f in ("map", "filter", "fold", "reduce", "zip"):
        pf = gather_prose["region"]["per_function"].get(f)
        if pf:
            log(f"    {f:>7} inter={pf['interaction_mean']:+.4f} "
                f"t={pf['interaction_t']:+.2f} hof>ctl={pf['frac_hof_gt_ctrl']:.2f}")
    log(f"  NECESSARY list={list_necessary}  prose[region]={prose_necessary_region} "
        f"prose[lastkl]={prose_necessary_lastkl} prose[whole]={prose_necessary_whole}")
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
        reg = m["prose"]["region"]
        rows.append({
            "model": m["model"],
            "list_kl_inter_gather": m["list_kl"]["gather"]["kl_interaction"],
            "list_kl_inter_random": m["list_kl"]["random"]["kl_interaction"],
            "region_inter_gather": reg["gather"]["engaged"]["interaction_mean"],
            "region_t_gather": reg["gather"]["engaged"]["interaction_t"],
            "region_inter_random": reg["random"]["engaged"]["interaction_mean"],
            "lastkl_t_gather":
                m["prose"]["lastkl"]["gather"]["engaged"]["interaction_t"],
            "whole_t_gather":
                m["prose"]["whole"]["gather"]["engaged"]["interaction_t"],
            "list_necessary": m["list_necessary"],
            "prose_necessary_region": m["prose_necessary_region"],
            "prose_necessary_lastkl": m["prose_necessary_lastkl"],
            "prose_necessary_whole": m["prose_necessary_whole"],
        })
    # cross-model combine — per-model t>2 is underpowered at n~80 pairs, so report
    # the cross-model picture: directional consistency (sign test, assumption-free)
    # + Stouffer z (caveat: per-model t's share the same prose pairs → positively
    # correlated → Stouffer OVERSTATES; the sign test is the conservative claim).
    def _binom_one_sided(k, n, p=0.5):
        from math import comb
        return sum(comb(n, i) for i in range(k, n + 1)) * (p ** n)

    cross = {}
    nmod = len(models)
    for ro in ("region", "lastkl", "whole"):
        ts, pos, gr = [], 0, 0
        for m in models:
            g = m["prose"][ro]["gather"]["engaged"]
            r = m["prose"][ro]["random"]["engaged"]
            ts.append(g["interaction_t"])
            pos += int(g["interaction_mean"] > 0)
            gr += int(g["interaction_mean"] > r["interaction_mean"])
        cross[ro] = {
            "t_mean": round(float(np.mean(ts)), 3),
            "t_per_model": [round(t, 3) for t in ts],
            "n_positive": pos,
            "sign_p_one_sided": round(_binom_one_sided(pos, nmod), 4),
            "n_gather_gt_random": gr,
            "stouffer_z": round(float(np.sum(ts) / np.sqrt(nmod)), 3),
        }

    out = {"models": [m["model"] for m in models], "rows": rows,
           "primary_readout": "region (divergent-middle NLL diff-in-diff)",
           "cross_model": cross,
           "n_list_necessary": sum(r["list_necessary"] for r in rows),
           "n_prose_necessary_region":
               sum(r["prose_necessary_region"] for r in rows),
           "n_prose_necessary_lastkl":
               sum(r["prose_necessary_lastkl"] for r in rows),
           "n_prose_necessary_whole":
               sum(r["prose_necessary_whole"] for r in rows),
           "git_sha": git_sha()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === CAUSAL ABLATION OF GATHER HEADS (necessity, gather vs random) ===")
    log("  prose = ENGAGED HOFs (fold/reduce/filter/zip; map excluded per s225)")
    log("  PRIMARY readout = divergent-region NLL; whole = s226 reference")
    log(f"  {'model':>26} {'lstKLg':>7} {'rgnG':>7} {'rgnT':>6} {'rgnR':>7} "
        f"{'klT':>6} {'whlT':>6} need(L/rgn/kl/whl)")
    for r in rows:
        log(f"  {r['model']:>26} {r['list_kl_inter_gather']:>+7.4f} "
            f"{r['region_inter_gather']:>+7.4f} {r['region_t_gather']:>+6.2f} "
            f"{r['region_inter_random']:>+7.4f} {r['lastkl_t_gather']:>+6.2f} "
            f"{r['whole_t_gather']:>+6.2f} "
            f"{'Y' if r['list_necessary'] else 'n'}/"
            f"{'Y' if r['prose_necessary_region'] else 'n'}/"
            f"{'Y' if r['prose_necessary_lastkl'] else 'n'}/"
            f"{'Y' if r['prose_necessary_whole'] else 'n'}")
    log(f"  list-necessary {out['n_list_necessary']}/{len(rows)}; prose-necessary "
        f"region {out['n_prose_necessary_region']}/{len(rows)} "
        f"lastkl {out['n_prose_necessary_lastkl']}/{len(rows)} "
        f"whole {out['n_prose_necessary_whole']}/{len(rows)}")
    log("  cross-model combine (per-model t>2 underpowered; sign test = conservative):")
    for ro in ("region", "lastkl", "whole"):
        c = cross[ro]
        log(f"    {ro:>7}: t_mean={c['t_mean']:+.2f} positive {c['n_positive']}/{nmod} "
            f"(sign p1={c['sign_p_one_sided']:.3f}) "
            f"gt_rand {c['n_gather_gt_random']}/{nmod} "
            f"Stouffer_z={c['stouffer_z']:+.2f}")
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
