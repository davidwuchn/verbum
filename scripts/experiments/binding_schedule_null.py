#!/usr/bin/env python3
"""Audit #5 — Is the binding SCHEDULE real, or 14 cherry-picked probes?

The claim (`binding-graph-trace.md`, Findings 4 & 7, Implication 2):
  there is a depth-ordered "reduction schedule" --
    L27  subject -> verb   binding peaks (H31, 0.82)
    L30  object  -> verb   binding peaks (H03/H13/H15, 0.66-0.78)
    L33  coreference       (pronoun -> antecedent) binds late (H06/H07)
  i.e. peak_layer(subject) < peak_layer(object) < peak_layer(coref);
  "the depth ordering IS the reduction schedule -- subjects bind first."

Suspected confound (audit-registry #5, failure modes #5 cherry-pick / #6 surface):
  the schedule was read off 14 hand-annotated probes. Two ways it can be an
  artifact:
   (a) cherry-picked sentences/heads -- the ordering may not survive a large,
       varied corpus or a bootstrap over sentences;
   (b) generic attention-vs-depth -- ANY position pair (random content words at
       matched distance) may show the same peak-layer profile, so the "schedule"
       is a property of where attention is sharp by depth, not of binding/type.
  And (audit #4, already established) the raw verb->subject weight is
  recency/position-dominated -- so a schedule read off RAW attention may just
  track linear distance.

Discriminating design
---------------------
  Many sentences, three dependency types, EVERY layer, with three controls:
    PART 1  Schedule profile + nulls
      For dep in {subj (verb->subject), obj (object->verb), coref (it->antecedent)},
      N varied sentences. Per sentence, per layer L in 0..n_layers-1:
        raw[L]      = max_head attn(dependent -> head)
        role_sel[L] = max_head [ attn(dep->head) - mean attn(dep->other_content) ]
                      (position control: specifically the grammatical head, not
                       just any content word)
      Aggregate mean curves; peak_layer = argmax. Schedule predicts
      peak(subj) < peak(obj) < peak(coref). Tests:
        * bootstrap B over sentences -> P(ordering holds) + per-type peak CIs.
          (cherry-pick control: a real schedule is stable across resamples;
           an artifact of 14 probes scatters.)
        * RANDOM-PAIR null: per sentence, K random content (later->earlier) pairs;
          their binding(layer) profile. If random pairs peak at the same layers,
          the schedule is generic to depth, not binding.  (failure mode #6)
        * distance report per type (exposes the position confound).
    PART 2  Are the NAMED heads outliers? At each type's peak layer, rank all
      heads by binding; where do H31@L27 / H03,13,15@L30 / H06,07@L33 sit, and
      z vs the 32-head distribution.  (reuses audit #4 instrument)
    PART 3  Causal schedule (subject readout): subject-verb agreement is/are
      logit-diff; ablate L27-named vs L30-named vs L33-named vs random-head null.
      Schedule predicts ablating the L27 ("subject") heads hurts subject
      agreement MORE than L30/L33. (Extends audit #4's H31 null.)

Verdict
-------
  SCHEDULE real : peak(subj)<peak(obj)<peak(coref) stable under bootstrap AND
                  distinct from the random-pair null AND L27 ablation specifically
                  carries subject agreement.
  IMPOSED       : ordering unstable / matches random-pair depth profile /
                  no layer-specific causal carrier. "14 probes", not a schedule.

Usage:
  uv run python scripts/experiments/binding_schedule_null.py \
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

# Named schedule heads from binding-graph-trace.md (the claim under audit)
NAMED_SCHEDULE = {"subj": (27, [31]), "obj": (30, [3, 13, 15]), "coref": (33, [6, 7])}

# ── Lexicon (single common tokens preferred; multi-token handled) ──────
NOUNS = [
    "dog", "cat", "boy", "girl", "man", "woman", "bird", "horse", "teacher",
    "doctor", "farmer", "pilot", "singer", "king", "queen", "soldier", "child",
    "fox", "wolf", "lion", "nurse", "driver", "painter", "baker",
]
VERBS_INTRANS = [
    "runs", "sleeps", "jumps", "sings", "barks", "waits", "smiles", "works",
    "rests", "dreams", "laughs", "cries", "stumbles", "wanders", "hesitates",
]
VERBS_TRANS = [
    "chased", "found", "watched", "kicked", "carried", "pushed", "bit",
    "grabbed", "followed", "saw", "held", "dropped", "caught", "fed",
]
OBJECTS = [
    "ball", "book", "apple", "stick", "rope", "bone", "toy", "box", "cup",
    "flag", "drum", "kite", "leaf", "rock", "coin", "key", "hat", "shoe",
]
ADVS = ["quietly", "slowly", "today", "again", "alone", "outside", "early"]
ADJS = ["tired", "hungry", "afraid", "happy", "cold", "lost", "calm", "brave"]


def log(msg=""):
    print(msg, flush=True)


# ── Stimuli ────────────────────────────────────────────────────────────

def build_stimuli(n_per, seed=7):
    """Return dict dep_type -> list of {sentence, dep_word, head_word}.

    subj : "The <noun> <vi> <adv>."          dep=verb   head=noun  (verb->subject)
    obj  : "The <n1> <vt> the <obj> <adv>."   dep=obj    head=verb  (object->verb)
    coref: "The <noun> <vi> because it was <adj>."  dep="it" head=noun
    """
    rng = np.random.default_rng(seed)
    out = {"subj": [], "obj": [], "coref": []}
    for _ in range(n_per):
        n = rng.choice(NOUNS)
        vi = rng.choice(VERBS_INTRANS)
        adv = rng.choice(ADVS)
        out["subj"].append({
            "sentence": f"The {n} {vi} {adv}.",
            "dep_word": vi, "head_word": n})

        n1 = rng.choice(NOUNS)
        vt = rng.choice(VERBS_TRANS)
        ob = rng.choice(OBJECTS)
        adv2 = rng.choice(ADVS)
        out["obj"].append({
            "sentence": f"The {n1} {vt} the {ob} {adv2}.",
            "dep_word": ob, "head_word": vt})

        n2 = rng.choice(NOUNS)
        vi2 = rng.choice(VERBS_INTRANS)
        adj = rng.choice(ADJS)
        out["coref"].append({
            "sentence": f"The {n2} {vi2} because it was {adj}.",
            "dep_word": "it", "head_word": n2})
    return out


def token_positions(tokens, word):
    """Indices whose stripped lower text subword-matches `word` (alpha)."""
    w = word.lower().strip()
    hits = []
    for i, t in enumerate(tokens):
        s = t.strip().lower()
        if s and s.isalpha() and (s == w or s in w or w in s):
            hits.append(i)
    return hits


def content_positions(tokens):
    """Alpha tokens, excluding obvious function words (the binding endpoints
    we score separately are still allowed as 'content' for the random null)."""
    stop = {"the", "a", "an", "because", "was", "is", "are", "that", "near"}
    pos = []
    for i, t in enumerate(tokens):
        s = t.strip().lower()
        if s and s.isalpha() and s not in stop:
            pos.append(i)
    return pos


def first_token_id(tokenizer, s):
    ids = tokenizer(s, add_special_tokens=False)["input_ids"]
    return ids[0] if ids else None


# ══════════════════════════════════════════════════════════════════════
# PART 1 — schedule profile (per-sentence per-layer binding)
# ══════════════════════════════════════════════════════════════════════

def schedule_profile(model, tokenizer, stim, n_layers, n_heads, device,
                     k_random=4, seed=11):
    """Return per dep_type: arrays [n_sent, n_layers] of raw binding & role_sel,
    plus the random-pair null curve and distance stats."""
    rng = np.random.default_rng(seed)
    res = {}
    rand_curves = []  # per-sentence random-pair max-head binding (any type)
    for dep, items in stim.items():
        raw_rows, role_rows, dists = [], [], []
        for it in items:
            enc = tokenizer(it["sentence"], return_tensors="pt")
            ids = enc["input_ids"].to(device)
            toks = [tokenizer.decode(t) for t in enc["input_ids"][0]]
            dpos = token_positions(toks, it["dep_word"])
            hpos = token_positions(toks, it["head_word"])
            if not dpos or not hpos:
                continue
            d = dpos[-1]                       # dependent (later token)
            h = max(p for p in hpos if p < d) if any(p < d for p in hpos) else None
            if h is None:
                continue
            cpos = [p for p in content_positions(toks) if p < d and p != h]
            dists.append(d - h)

            with torch.no_grad():
                out = model(ids, output_attentions=True, return_dict=True)
            raw_L, role_L = np.zeros(n_layers), np.zeros(n_layers)
            for li in range(n_layers):
                A = out.attentions[li][0]      # (n_heads, seq, seq)
                col_head = A[:, d, h]          # (n_heads,)
                raw_L[li] = float(col_head.max())
                if cpos:
                    other = A[:, d, cpos].mean(dim=1)      # mean over other content
                    role_L[li] = float((col_head - other).max())
                else:
                    role_L[li] = raw_L[li]
                # random-pair null: a random (later->earlier) content pair
                allc = content_positions(toks)
                pairs = [(i, j) for i in allc for j in allc if j < i]
                if pairs:
                    for _ in range(k_random):
                        i, j = pairs[int(rng.integers(0, len(pairs)))]
                        rand_curves.append((li, float(A[:, i, j].max())))
            raw_rows.append(raw_L)
            role_rows.append(role_L)
        res[dep] = {
            "raw": np.array(raw_rows), "role": np.array(role_rows),
            "dist_mean": float(np.mean(dists)) if dists else 0.0,
            "n": len(raw_rows),
        }
    # collapse random-pair null into a per-layer mean curve
    null_curve = np.zeros(n_layers)
    cnt = np.zeros(n_layers)
    for li, v in rand_curves:
        null_curve[li] += v
        cnt[li] += 1
    null_curve = np.divide(null_curve, np.maximum(cnt, 1))
    return res, null_curve


def bootstrap_ordering(res, metric="role", B=1000, seed=3):
    """P(peak(subj) < peak(obj) < peak(coref)) over sentence bootstraps + peak CIs."""
    rng = np.random.default_rng(seed)
    deps = ["subj", "obj", "coref"]
    mats = {d: res[d][metric] for d in deps}
    peaks = {d: [] for d in deps}
    ok = 0
    for _ in range(B):
        pk = {}
        for d in deps:
            M = mats[d]
            if len(M) == 0:
                pk[d] = -1
                continue
            idx = rng.integers(0, len(M), len(M))
            pk[d] = int(np.argmax(M[idx].mean(axis=0)))
            peaks[d].append(pk[d])
        if pk["subj"] < pk["obj"] < pk["coref"]:
            ok += 1
    peak_ci = {d: [int(np.percentile(peaks[d], 5)), int(np.median(peaks[d])),
                   int(np.percentile(peaks[d], 95))] if peaks[d] else [-1, -1, -1]
               for d in deps}
    return round(ok / B, 4), peak_ci


# ══════════════════════════════════════════════════════════════════════
# PART 2 — are the named heads outliers at the peak layer?
# ══════════════════════════════════════════════════════════════════════

def head_ranks_at_peak(model, tokenizer, stim, peak_layer, dep, n_heads, device):
    """Mean per-head binding (dep->head) at a given layer; rank named heads."""
    per_head = np.zeros(n_heads)
    cnt = 0
    for it in stim[dep]:
        enc = tokenizer(it["sentence"], return_tensors="pt")
        ids = enc["input_ids"].to(device)
        toks = [tokenizer.decode(t) for t in enc["input_ids"][0]]
        dpos = token_positions(toks, it["dep_word"])
        hpos = token_positions(toks, it["head_word"])
        if not dpos or not hpos:
            continue
        d = dpos[-1]
        hcands = [p for p in hpos if p < d]
        if not hcands:
            continue
        h = max(hcands)
        with torch.no_grad():
            out = model(ids, output_attentions=True, return_dict=True)
        per_head += out.attentions[peak_layer][0][:, d, h].float().cpu().numpy()
        cnt += 1
    per_head /= max(cnt, 1)
    mu, sd = float(per_head.mean()), float(per_head.std() + 1e-9)
    order = np.argsort(-per_head)
    rank = {int(hh): int(np.where(order == hh)[0][0]) for hh in range(n_heads)}
    named = NAMED_SCHEDULE[dep][1]
    return {
        "layer": peak_layer, "n": cnt,
        "allhead_mean": round(mu, 4), "allhead_std": round(sd, 4),
        "top5": [[int(order[j]), round(float(per_head[order[j]]), 4)]
                 for j in range(5)],
        "named": {int(hh): {"binding": round(float(per_head[hh]), 4),
                            "z": round((per_head[hh] - mu) / sd, 2),
                            "rank": rank[hh], "of": n_heads} for hh in named},
    }


# ══════════════════════════════════════════════════════════════════════
# PART 3 — causal schedule (subject-verb agreement readout)
# ══════════════════════════════════════════════════════════════════════

def build_agreement(seed=5):
    rng = np.random.default_rng(seed)
    subs = [("author", "authors"), ("key", "keys"), ("officer", "officers"),
            ("pilot", "pilots"), ("farmer", "farmers"), ("singer", "singers"),
            ("doctor", "doctors"), ("painter", "painters")]
    items = []
    for (sg, pl) in subs:
        for num in ("sg", "pl"):
            head = sg if num == "sg" else pl
            correct = "is" if num == "sg" else "are"
            cloze = f"The {head} near the table"
            items.append({"cloze": cloze, "correct": correct})
    rng.shuffle(items)
    return items


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


def agreement_logit_diff(model, tokenizer, items, device, cfg, head_dim, id_is, id_are):
    handles = ablation_hooks(model, cfg, head_dim) if cfg else []
    diffs = []
    try:
        for it in items:
            ids = tokenizer(it["cloze"], return_tensors="pt")["input_ids"].to(device)
            with torch.no_grad():
                logits = model(ids).logits[0, -1].float()
            cid = id_is if it["correct"] == "is" else id_are
            wid = id_are if it["correct"] == "is" else id_is
            diffs.append(float(logits[cid] - logits[wid]))
    finally:
        for h in handles:
            h.remove()
    return float(np.mean(diffs)) if diffs else 0.0


# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-per", type=int, default=80,
                   help="sentences per dependency type")
    p.add_argument("--boot", type=int, default=1000)
    p.add_argument("--n-random-heads", type=int, default=24)
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    log(f"\n{'='*70}\n  AUDIT #5 — binding SCHEDULE: "
        f"real depth-ordering or 14 probes?\n{'='*70}")
    log(f"  Model: {args.model}  Device: {args.device}  n_per={args.n_per}")

    dtype = (torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"  Loading {args.model} ({dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device, attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    cfg = model.config
    n_heads = cfg.num_attention_heads
    n_layers = cfg.num_hidden_layers
    head_dim = getattr(cfg, "head_dim", None) or (cfg.hidden_size // n_heads)
    log(f"  {n_layers} layers, {n_heads} Q heads, head_dim={head_dim}")

    stim = build_stimuli(args.n_per, seed=args.seed)
    for d in stim:
        log(f"    {d:6s}: {len(stim[d])} sentences  e.g. \"{stim[d][0]['sentence']}\" "
            f"(dep='{stim[d][0]['dep_word']}' head='{stim[d][0]['head_word']}')")

    # ── PART 1 ─────────────────────────────────────────────────────────
    log(f"\n{'-'*70}\n  PART 1 — schedule profile across all "
        f"{n_layers} layers\n{'-'*70}")
    t0 = time.time()
    res, null_curve = schedule_profile(
        model, tokenizer, stim, n_layers, n_heads, args.device)
    deps = ["subj", "obj", "coref"]
    claim = {"subj": 27, "obj": 30, "coref": 33}
    profile_out = {}
    for d in deps:
        raw_mean = res[d]["raw"].mean(axis=0)
        role_mean = res[d]["role"].mean(axis=0)
        pk_raw = int(np.argmax(raw_mean))
        pk_role = int(np.argmax(role_mean))
        profile_out[d] = {
            "n": res[d]["n"], "dist_mean": round(res[d]["dist_mean"], 2),
            "peak_raw": pk_raw, "peak_role": pk_role,
            "claimed_layer": claim[d],
            "raw_at_claim": round(float(raw_mean[claim[d]]), 4),
            "role_at_claim": round(float(role_mean[claim[d]]), 4),
            "raw_curve": [round(float(x), 4) for x in raw_mean],
            "role_curve": [round(float(x), 4) for x in role_mean],
        }
        log(f"  {d:6s} (n={res[d]['n']}, dist={res[d]['dist_mean']:.1f}): "
            f"peak_raw=L{pk_raw}  peak_role=L{pk_role}  (claimed L{claim[d]})  "
            f"role@claim={role_mean[claim[d]]:+.3f}")
    log(f"  random-pair NULL peak: L{int(np.argmax(null_curve))} "
        f"(max={null_curve.max():.3f})")

    p_raw, ci_raw = bootstrap_ordering(res, "raw", B=args.boot)
    p_role, ci_role = bootstrap_ordering(res, "role", B=args.boot)
    log(f"\n  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  "
        f"raw={p_raw}  role={p_role}  "
        f"(chance for a strict order = 1/6 = 0.167)")
    log("  peak CIs (role) [p5,med,p95]:  " +
        "  ".join(f"{d}=L{ci_role[d]}" for d in deps))
    log(f"  part 1 done in {time.time()-t0:.1f}s")

    # ── PART 2 ─────────────────────────────────────────────────────────
    log(f"\n{'-'*70}\n  PART 2 — are the named heads outliers "
        f"at the CLAIMED layer?\n{'-'*70}")
    t0 = time.time()
    part2 = {}
    for d in deps:
        layer = claim[d]
        hr = head_ranks_at_peak(model, tokenizer, stim, layer, d, n_heads, args.device)
        part2[d] = hr
        log(f"  {d:6s} @L{layer}: all-head mean={hr['allhead_mean']:.4f} "
            f"top5={hr['top5']}")
        for hh, s in hr["named"].items():
            log(f"      NAMED H{hh}: binding={s['binding']:.4f}  z={s['z']:+.2f}  "
                f"rank={s['rank']}/{s['of']}")
    log(f"  part 2 done in {time.time()-t0:.1f}s")

    # ── PART 3 ─────────────────────────────────────────────────────────
    log(f"\n{'-'*70}\n  PART 3 — causal schedule "
        f"(subject-verb agreement readout)\n{'-'*70}")
    t0 = time.time()
    id_is = first_token_id(tokenizer, " is")
    id_are = first_token_id(tokenizer, " are")
    agree = build_agreement()
    base = agreement_logit_diff(
        model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)
    log(f"  baseline subject-verb logit-diff = {base:+.3f}")
    abl = {}
    for d in deps:
        li, heads = NAMED_SCHEDULE[d]
        r = agreement_logit_diff(model, tokenizer, agree, args.device,
                                 {li: heads}, head_dim, id_is, id_are)
        abl[d] = {"layer": li, "heads": heads, "logit_diff": round(r, 4),
                  "drop": round(base - r, 4)}
        log(f"  ablate {d:6s} (L{li} H{heads}): "
            f"logit-diff={r:+.3f}  drop={base-r:+.3f}")
    # random-head null per claimed layer
    rng = np.random.default_rng(args.seed)
    null_drops = {}
    for d in deps:
        li = claim[d]
        size = len(NAMED_SCHEDULE[d][1])
        drops = []
        for _ in range(args.n_random_heads):
            hs = list(rng.choice(n_heads, size=size, replace=False))
            r = agreement_logit_diff(
                model, tokenizer, agree, args.device,
                {li: [int(x) for x in hs]}, head_dim, id_is, id_are)
            drops.append(base - r)
        null_drops[d] = {"mean": round(float(np.mean(drops)), 4),
                         "std": round(float(np.std(drops)), 4),
                         "max": round(float(np.max(drops)), 4),
                         "z_named": round((abl[d]["drop"] - np.mean(drops)) /
                                          (np.std(drops) + 1e-9), 2)}
        log(f"  L{li} random {size}-head null: drop mean={null_drops[d]['mean']:+.3f} "
            f"std={null_drops[d]['std']:.3f}  -> "
            f"named z={null_drops[d]['z_named']:+.2f}")
    log(f"  part 3 done in {time.time()-t0:.1f}s")

    # ── Verdict ────────────────────────────────────────────────────────
    log(f"\n{'='*70}\n  VERDICT\n{'='*70}")
    log(f"  ordering P(subj<obj<coref): raw={p_raw} role={p_role}  (chance 0.167)")
    log(f"  random-pair null peaks at L{int(np.argmax(null_curve))} "
        f"(schedule must beat this to be binding-specific)")
    log("  causal: subject-agreement ablation z vs null  " +
        "  ".join(f"{d}=L{claim[d]}:{null_drops[d]['z_named']:+.2f}" for d in deps))
    log("  SCHEDULE real if ordering P>>0.167 AND distinct from random-pair null AND")
    log("  L27(subj) ablation z>>0 and > L30/L33; IMPOSED otherwise.")

    results = {
        "audit": "5-binding-schedule", "model": args.model,
        "n_layers": n_layers, "n_heads": n_heads, "head_dim": head_dim,
        "n_per": args.n_per,
        "part1_profile": profile_out,
        "random_pair_null_curve": [round(float(x), 4) for x in null_curve],
        "random_pair_null_peak": int(np.argmax(null_curve)),
        "ordering": {"p_raw": p_raw, "p_role": p_role,
                     "ci_raw": ci_raw, "ci_role": ci_role,
                     "chance": round(1 / 6, 4)},
        "part2_head_ranks": part2,
        "part3_causal": {"baseline": round(base, 4), "ablations": abl,
                         "null": null_drops},
    }
    out_dir = _PROJECT_ROOT / "results" / "binding-schedule-null"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
