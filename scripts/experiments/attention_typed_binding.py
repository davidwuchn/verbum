#!/usr/bin/env python3
"""Audit #4 — Is attention TYPED beta-reduction, or just a positional/recency head?

The claim (`binding-graph-trace.md`, `mode-semantics.md`): attention IS typed
beta-application — H31@L27 attends 0.82 verb->subject, H03/H13/H15@L30 do
object->verb, and "weighted sum IS beta-application of a type-compatible
argument."

Suspected confound (audit-registry #4, failure mode #5/#6):
  In simple SVO ("The dog bit the cat") the subject is ALWAYS at a fixed early
  position and is the nearest preceding noun to the verb. So "verb attends to
  subject at 0.82" is consistent with a plain POSITIONAL / RECENCY head (attend
  to the nearest/earliest noun) with NO notion of grammatical role or type.
  All attention is a weighted sum; "typed beta-reduction" is interpretation.

Discriminating design — subject-verb AGREEMENT ATTRACTION (Linzen 2016 /
Lakretz 2019): put the true subject (head noun) and a number DISTRACTOR
(attractor) at DIFFERENT positions, so grammatical ROLE dissociates from
linear position and recency:

  PP:  "The author near the editors is ..."   head=author(far)  attractor=editors(near)
  RC:  "The author that the editors saw is ..."  head=author(far) attractor=editors(near)

A recency/positional head attends to the NEAR noun (attractor). A typed
subject-binder attends to the ROLE-correct head noun (far). The behavioural
readout is clean: the copula must agree in number with the HEAD, not the
attractor — logit(" is") vs logit(" are").

Instruments
-----------
  PART 1 — Selectivity (representational, with baselines)
    For the named binder heads, attention from the verb/copula to {head, attractor}.
    role_selectivity = a(head) - a(attractor)  (>0 = role-driven, <0 = recency).
    Compare named heads to the FULL 32-head distribution (rank + z) and to the
    recency baseline (which always predicts the attractor). Is the named head a
    genuine outlier in role-selectivity, or typical?

  PART 2 — Necessity (causal ablation, with null)
    logit-diff = logit(correct copula) - logit(wrong copula) at the cloze.
    Ablate the named binder head(s) (o_proj head-slice zeroing) and measure the
    drop, vs B random single-head and random matched-size-set ablations at the
    same layers. Broken out by match / MISMATCH (mismatch is where binding is
    load-bearing). Named-ablation drop >> random-head null  ==>  causal necessity.

Verdict
-------
  TYPED real : named head role_selectivity > 0 and an outlier vs all heads AND
               beats recency; named ablation drops mismatch logit-diff >> null.
  POSITIONAL : named head role_selectivity ~0 / negative (tracks recency), not an
               outlier; named ablation ~ random-head null. "typed beta" over-reads.

Usage:
  uv run python scripts/experiments/attention_typed_binding.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent

# Named binder heads from binding-graph-trace.md / reverse_binding_trace.md
NAMED_BINDERS = {27: [31], 30: [3, 13, 15], 33: [6, 7]}
TARGET_LAYERS = [27, 30, 33]

# ── Lexicon (singular, plural) ─────────────────────────────────────────
SUBJECTS = [
    ("author", "authors"), ("key", "keys"), ("painting", "paintings"),
    ("officer", "officers"), ("pilot", "pilots"), ("surgeon", "surgeons"),
    ("senator", "senators"), ("farmer", "farmers"),
]
ATTRACTORS = [
    ("editor", "editors"), ("cabinet", "cabinets"), ("museum", "museums"),
    ("building", "buildings"), ("airport", "airports"), ("hospital", "hospitals"),
    ("committee", "committees"), ("market", "markets"),
]
ADJS = ["ready", "famous", "calm", "late", "honest", "quiet", "absent", "tall"]


def log(msg=""):
    print(msg, flush=True)


def build_stimuli():
    """Agreement-attraction stimuli; head and attractor at different positions.

    Each item: cloze (prompt before copula) + full (with the correct copula),
    head/attractor words + numbers, correct/wrong copula, match flag, structure.
    """
    items = []
    rng = np.random.default_rng(7)
    for i, ((s_sg, s_pl), (a_sg, a_pl), adj) in enumerate(
            zip(SUBJECTS, ATTRACTORS, ADJS, strict=True)):
        for struct in ("PP", "RC"):
            for head_num in ("sg", "pl"):
                for attr_num in ("sg", "pl"):
                    head = s_sg if head_num == "sg" else s_pl
                    attr = a_sg if attr_num == "sg" else a_pl
                    correct = "is" if head_num == "sg" else "are"
                    wrong = "are" if head_num == "sg" else "is"
                    if struct == "PP":
                        cloze = f"The {head} near the {attr}"
                    else:
                        cloze = f"The {head} that the {attr} saw"
                    full = f"{cloze} {correct} {adj}."
                    items.append({
                        "id": f"{i}-{struct}-{head_num}{attr_num}",
                        "cloze": cloze, "full": full,
                        "head_word": head, "attractor_word": attr,
                        "head_num": head_num, "attr_num": attr_num,
                        "correct": correct, "wrong": wrong,
                        "match": "match" if head_num == attr_num else "mismatch",
                        "structure": struct, "verb_word": correct,
                    })
    rng.shuffle(items)
    return items


def get_layers(model):
    return model.model.layers


def find_positions(tokens, word, start=0):
    """All token indices whose stripped text is a subword of `word` (last wins)."""
    w = word.lower().strip()
    hits = []
    for i in range(start, len(tokens)):
        t = tokens[i].strip().lower()
        if t and (t in w or w in t) and t.isalpha():
            hits.append(i)
    return hits


def first_token_id(tokenizer, s):
    ids = tokenizer(s, add_special_tokens=False)["input_ids"]
    return ids[0] if ids else None


# ══════════════════════════════════════════════════════════════════════
# PART 1 — selectivity
# ══════════════════════════════════════════════════════════════════════

def selectivity(model, tokenizer, items, layers, n_heads, device):
    per_head = {li: {h: [] for h in range(n_heads)} for li in layers}
    role_n = 0
    nearer_attractor = 0

    for it in items:
        enc = tokenizer(it["full"], return_tensors="pt")
        ids = enc["input_ids"].to(device)
        toks = [tokenizer.decode(t) for t in enc["input_ids"][0]]
        head_pos = find_positions(toks, it["head_word"])
        attr_pos = find_positions(toks, it["attractor_word"])
        # verb = the copula form, find its position (after the nouns)
        verb_hits = [i for i, t in enumerate(toks) if t.strip() == it["verb_word"]]
        if not head_pos or not attr_pos or not verb_hits:
            continue
        vpos = verb_hits[-1]
        hp = [p for p in head_pos if p < vpos]
        ap = [p for p in attr_pos if p < vpos]
        if not hp or not ap:
            continue
        # recency: which is nearer to verb
        if max(ap) > max(hp):
            nearer_attractor += 1
        role_n += 1

        with torch.no_grad():
            out = model(ids, output_attentions=True, return_dict=True)
        for li in layers:
            attn = out.attentions[li][0]  # (n_heads, seq, seq)
            for h in range(n_heads):
                a_head = float(attn[h, vpos, hp].sum())
                a_attr = float(attn[h, vpos, ap].sum())
                per_head[li][h].append(a_head - a_attr)

    # aggregate
    result = {"n_items": role_n, "recency_target_is_attractor_frac":
              round(nearer_attractor / max(1, role_n), 3), "layers": {}}
    for li in layers:
        head_means = np.array([np.mean(per_head[li][h]) if per_head[li][h] else 0.0
                               for h in range(n_heads)])
        mu, sd = float(head_means.mean()), float(head_means.std() + 1e-9)
        named = NAMED_BINDERS.get(li, [])
        named_stats = {}
        order = np.argsort(-head_means)  # descending role-selectivity
        rank = {int(h): int(np.where(order == h)[0][0]) for h in range(n_heads)}
        for h in named:
            named_stats[int(h)] = {
                "role_sel": round(float(head_means[h]), 4),
                "z_vs_allheads": round((head_means[h] - mu) / sd, 2),
                "rank": rank[h], "of": n_heads,
                "top1_head": int(order[0]),
                "top1_role_sel": round(float(head_means[order[0]]), 4),
            }
        result["layers"][str(li)] = {
            "allhead_mean_role_sel": round(mu, 4),
            "allhead_std": round(sd, 4),
            "named": named_stats,
            "top5_heads": [[int(order[j]), round(float(head_means[order[j]]), 4)]
                           for j in range(5)],
        }
    return result


# ══════════════════════════════════════════════════════════════════════
# PART 2 — ablation / necessity
# ══════════════════════════════════════════════════════════════════════

def ablation_hooks(model, cfg, head_dim):
    handles = []
    for li, heads in cfg.items():
        o_proj = model.model.layers[li].self_attn.o_proj

        def mk(hs):
            def pre(module, args):
                x = args[0].clone()
                for h in hs:
                    x[..., h * head_dim:(h + 1) * head_dim] = 0.0
                return (x,)
            return pre
        handles.append(o_proj.register_forward_pre_hook(mk(list(heads))))
    return handles


def logit_diffs(model, tokenizer, items, device, cfg, head_dim, id_is, id_are):
    handles = ablation_hooks(model, cfg, head_dim) if cfg else []
    diffs = {"all": [], "match": [], "mismatch": []}
    try:
        for it in items:
            enc = tokenizer(it["cloze"], return_tensors="pt")
            ids = enc["input_ids"].to(device)
            with torch.no_grad():
                logits = model(ids).logits[0, -1].float()
            cid = id_is if it["correct"] == "is" else id_are
            wid = id_are if it["correct"] == "is" else id_is
            d = float(logits[cid] - logits[wid])
            diffs["all"].append(d)
            diffs[it["match"]].append(d)
    finally:
        for h in handles:
            h.remove()
    return {k: (float(np.mean(v)) if v else 0.0) for k, v in diffs.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--layers", type=int, nargs="+", default=TARGET_LAYERS)
    p.add_argument("--n-random", type=int, default=24, help="random single-head ablations")
    p.add_argument("--n-random-sets", type=int, default=24, help="random matched-size sets")
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    log(f"\n{'='*70}\n  AUDIT #4 — typed beta-reduction vs positional/recency head\n{'='*70}")
    log(f"  Model: {args.model}  Device: {args.device}  Layers: {args.layers}")

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    log(f"  Loading {args.model} ({dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device, attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    cfg = model.config
    n_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", None) or (cfg.hidden_size // n_heads)
    layers = [_l for _l in args.layers if _l < cfg.num_hidden_layers]
    log(f"  {cfg.num_hidden_layers} layers, {n_heads} Q heads, head_dim={head_dim}")

    id_is = first_token_id(tokenizer, " is")
    id_are = first_token_id(tokenizer, " are")
    log(f"  copula token ids: ' is'={id_is}  ' are'={id_are}")

    items = build_stimuli()
    log(f"  stimuli: {len(items)}  "
        f"(mismatch={sum(1 for it in items if it['match']=='mismatch')})")

    # ── PART 1 ─────────────────────────────────────────────────────────
    log(f"\n{'─'*70}\n  PART 1 — selectivity (verb -> head vs attractor)\n{'─'*70}")
    t0 = time.time()
    sel = selectivity(model, tokenizer, items, layers, n_heads, args.device)
    log(f"  recency target = attractor in {sel['recency_target_is_attractor_frac']:.0%} of items "
        f"(a recency head would score NEGATIVE role-selectivity)")
    for li in layers:
        L = sel["layers"][str(li)]
        log(f"  L{li}: all-head role_sel mean={L['allhead_mean_role_sel']:+.4f} "
            f"std={L['allhead_std']:.4f}  top5={L['top5_heads']}")
        for h, s in L["named"].items():
            log(f"     NAMED H{h}: role_sel={s['role_sel']:+.4f}  z={s['z_vs_allheads']:+.2f}  "
                f"rank={s['rank']}/{s['of']}  (top head H{s['top1_head']}={s['top1_role_sel']:+.4f})")
    log(f"  part 1 done in {time.time()-t0:.1f}s")

    # ── PART 2 ─────────────────────────────────────────────────────────
    log(f"\n{'─'*70}\n  PART 2 — necessity (ablation, logit-diff is/are)\n{'─'*70}")
    t0 = time.time()
    base = logit_diffs(model, tokenizer, items, args.device, {}, head_dim, id_is, id_are)
    log(f"  baseline logit-diff: all={base['all']:+.3f}  match={base['match']:+.3f}  "
        f"mismatch={base['mismatch']:+.3f}")

    named_cfgs = {
        "named_L27_H31": {27: [31]},
        "named_L30_set": {30: [3, 13, 15]},
        "named_all": {k: v for k, v in NAMED_BINDERS.items() if k in layers},
    }
    named_res = {}
    for name, c in named_cfgs.items():
        c = {li: hs for li, hs in c.items() if li in layers}
        r = logit_diffs(model, tokenizer, items, args.device, c, head_dim, id_is, id_are)
        named_res[name] = {
            "cfg": {str(k): v for k, v in c.items()}, "logit_diff": r,
            "drop_all": round(base["all"] - r["all"], 4),
            "drop_mismatch": round(base["mismatch"] - r["mismatch"], 4),
        }
        log(f"  {name:16s}: mismatch={r['mismatch']:+.3f}  "
            f"drop(all)={base['all']-r['all']:+.3f}  drop(mismatch)={base['mismatch']-r['mismatch']:+.3f}")

    # Null: random single-head ablations at the target layers
    rng = np.random.default_rng(args.seed)
    single_drops_all, single_drops_mm = [], []
    for _ in range(args.n_random):
        li = int(rng.choice(layers))
        h = int(rng.integers(0, n_heads))
        r = logit_diffs(model, tokenizer, items, args.device, {li: [h]}, head_dim, id_is, id_are)
        single_drops_all.append(base["all"] - r["all"])
        single_drops_mm.append(base["mismatch"] - r["mismatch"])
    # Null: random matched-size sets (size = |named_all|)
    set_size = sum(len(v) for v in named_cfgs["named_all"].values())
    set_drops_mm = []
    for _ in range(args.n_random_sets):
        c = {}
        for _h in range(set_size):
            li = int(rng.choice(layers))
            c.setdefault(li, [])
            h = int(rng.integers(0, n_heads))
            if h not in c[li]:
                c[li].append(h)
        r = logit_diffs(model, tokenizer, items, args.device, c, head_dim, id_is, id_are)
        set_drops_mm.append(base["mismatch"] - r["mismatch"])

    def z(val, arr):
        a = np.array(arr)
        return round((val - a.mean()) / (a.std() + 1e-9), 2)

    null = {
        "single_head": {
            "drop_all_mean": round(float(np.mean(single_drops_all)), 4),
            "drop_mismatch_mean": round(float(np.mean(single_drops_mm)), 4),
            "drop_mismatch_std": round(float(np.std(single_drops_mm)), 4),
            "drop_mismatch_max": round(float(np.max(single_drops_mm)), 4),
        },
        "matched_set": {
            "size": set_size,
            "drop_mismatch_mean": round(float(np.mean(set_drops_mm)), 4),
            "drop_mismatch_std": round(float(np.std(set_drops_mm)), 4),
            "drop_mismatch_max": round(float(np.max(set_drops_mm)), 4),
        },
    }
    log(f"\n  NULL random single-head: drop(mismatch) mean={null['single_head']['drop_mismatch_mean']:+.3f} "
        f"std={null['single_head']['drop_mismatch_std']:.3f} max={null['single_head']['drop_mismatch_max']:+.3f}")
    log(f"  NULL random {set_size}-head sets: drop(mismatch) mean={null['matched_set']['drop_mismatch_mean']:+.3f} "
        f"std={null['matched_set']['drop_mismatch_std']:.3f} max={null['matched_set']['drop_mismatch_max']:+.3f}")

    z_h31 = z(named_res["named_L27_H31"]["drop_mismatch"], single_drops_mm)
    z_set = z(named_res["named_all"]["drop_mismatch"], set_drops_mm)
    log(f"\n  H31@L27 mismatch-drop z vs single-head null = {z_h31:+.2f}")
    log(f"  named_all mismatch-drop z vs matched-set null = {z_set:+.2f}")
    log(f"  part 2 done in {time.time()-t0:.1f}s")

    # ── Verdict ────────────────────────────────────────────────────────
    log(f"\n{'='*70}\n  VERDICT\n{'='*70}")
    h31 = sel["layers"][str(27)]["named"].get(31) if 27 in layers else None
    if h31:
        log(f"  selectivity: H31@L27 role_sel={h31['role_sel']:+.4f} z={h31['z_vs_allheads']:+.2f} "
            f"rank {h31['rank']}/{h31['of']}  (>0 & outlier => role-driven; <0 => recency)")
    log(f"  necessity:   H31@L27 ablation mismatch-drop z={z_h31:+.2f} vs random-head null; "
        f"named_all z={z_set:+.2f} vs matched-set null")
    log("  TYPED if role_sel>0 & outlier & ablation-z>>0; POSITIONAL if role_sel<=0 & z~0.")

    results = {
        "audit": "4-typed-binding", "model": args.model, "layers": layers,
        "n_heads": n_heads, "head_dim": head_dim, "n_stimuli": len(items),
        "selectivity": sel,
        "ablation": {"baseline": base, "named": named_res, "null": null,
                     "z_h31_vs_single": z_h31, "z_namedall_vs_set": z_set},
    }
    out_dir = _PROJECT_ROOT / "results" / "attention-typed-binding"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
