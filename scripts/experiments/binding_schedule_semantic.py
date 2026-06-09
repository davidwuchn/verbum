#!/usr/bin/env python3
"""Audit #5 (SEMANTIC leg) — does the binding schedule hold for VALUE TRANSFER?

The attention-weight control (`binding_schedule_null.py`) tests routing/position:
WHERE attention is sharp. But the claim (`binding-graph-trace.md`, Finding 7 /
Implication 2/4) is SEMANTIC:

  "Head output IS the reduction result -- H31 at L27 produces '猫' at position
   'runs' when it reads 'cat' ... the VALUE TRANSFER step of beta-reduction."
  Schedule: the verb position ABSORBS THE SUBJECT'S IDENTITY at L27, the object
  absorbs the predicate at L30, coref at L33 -- a depth ordering of SEMANTIC
  absorption.  Evidence was a LOGIT-LENS on the head's OUTPUT.

Early attention concentration (L4-L6, found by the weight control) does NOT
refute a LATE semantic schedule: semantic content is often written into the
residual at deeper layers. So we need the SEMANTIC instrument the claim used.

Instrument — per-head logit-lens of the output contribution
-----------------------------------------------------------
For each dependency type and many sentences, at EVERY layer L, for the named
head h, take the head's contribution to the residual at the DEPENDENT position:

    c_h = W_oproj[:, h*hd:(h+1)*hd] @ (attn_h value-weighted-sum at dep_pos)

(captured via an o_proj forward-pre-hook), then logit-lens through lm_head and
read the SEMANTIC MARGIN toward the bound entity:

    m_h[L] = logit(token@head_pos) - logit(token@control_pos)
           = lm_head[tok_head] . c_h  -  lm_head[tok_ctrl] . c_h

i.e. does this head's output, at the dependent position, point to the GRAMMATICAL
HEAD's token more than to another in-context content token? (control = earliest
other content token; an in-context, distance/frequency-matched null.)

  subj : dep=verb,   head=subject noun  -> does the verb absorb the subject identity?
  obj  : dep=object, head=verb          -> does the object absorb the predicate?
  coref: dep="it",   head=antecedent    -> does the pronoun absorb the antecedent?

Tests
-----
  PART A  Semantic schedule: per-type semantic-transfer curve m_named[L] across
          all layers; peak layer; bootstrap P(peak(subj)<peak(obj)<peak(coref))
          + per-type peak CIs. Also the margin at the CLAIMED layer vs its peak.
  PART B  Named-head specificity at the claimed layer: rank the named head's
          semantic margin against all 32 heads (z, rank).

Verdict
-------
  SEMANTIC schedule real : m_named>0 (entity is promoted), peaks in the claimed
                           L27<L30<L33 order (bootstrap P >> 1/6), named head an
                           outlier at its layer.
  NOT a schedule         : margins ~0 / negative, or peak order not L27<L30<L33,
                           or named head not special. Value-transfer schedule
                           is over-read.

Usage:
  uv run python scripts/experiments/binding_schedule_semantic.py \
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

NAMED_SCHEDULE = {"subj": (27, [31]), "obj": (30, [3, 13, 15]), "coref": (33, [6, 7])}

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


def build_stimuli(n_per, seed=7):
    rng = np.random.default_rng(seed)
    out = {"subj": [], "obj": [], "coref": []}
    for _ in range(n_per):
        n = rng.choice(NOUNS)
        vi = rng.choice(VERBS_INTRANS)
        adv = rng.choice(ADVS)
        out["subj"].append({"sentence": f"The {n} {vi} {adv}.",
                            "dep_word": vi, "head_word": n})
        n1 = rng.choice(NOUNS)
        vt = rng.choice(VERBS_TRANS)
        ob = rng.choice(OBJECTS)
        adv2 = rng.choice(ADVS)
        out["obj"].append({"sentence": f"The {n1} {vt} the {ob} {adv2}.",
                          "dep_word": ob, "head_word": vt})
        n2 = rng.choice(NOUNS)
        vi2 = rng.choice(VERBS_INTRANS)
        adj = rng.choice(ADJS)
        out["coref"].append({"sentence": f"The {n2} {vi2} because it was {adj}.",
                            "dep_word": "it", "head_word": n2})
    return out


def token_positions(tokens, word):
    w = word.lower().strip()
    hits = []
    for i, t in enumerate(tokens):
        s = t.strip().lower()
        if s and s.isalpha() and (s == w or s in w or w in s):
            hits.append(i)
    return hits


def content_positions(tokens):
    stop = {"the", "a", "an", "because", "was", "is", "are", "that", "near"}
    return [i for i, t in enumerate(tokens)
            if t.strip().lower() and t.strip().lower().isalpha()
            and t.strip().lower() not in stop]


class OProjTap:
    """Capture o_proj input (concatenated per-head outputs) at every layer."""

    def __init__(self, model, n_layers):
        self.store = {}
        self.handles = []
        for li in range(n_layers):
            o_proj = model.model.layers[li].self_attn.o_proj

            def mk(idx):
                def pre(module, args):
                    self.store[idx] = args[0].detach()
                    return None
                return pre
            self.handles.append(o_proj.register_forward_pre_hook(mk(li)))

    def remove(self):
        for h in self.handles:
            h.remove()


def head_logits_at(model, store, li, pos, head_dim, n_heads, tok_ids):
    """Per-head logit of each token id in `tok_ids` from head output at `pos`.

    Returns array [n_heads, len(tok_ids)].
    """
    o_proj = model.model.layers[li].self_attn.o_proj
    Wo = o_proj.weight                       # [hidden, n_heads*head_dim]
    Wu = model.lm_head.weight                # [vocab, hidden]
    x = store[li][0, pos]                    # [n_heads*head_dim]
    out = np.zeros((n_heads, len(tok_ids)), dtype=np.float32)
    Wu_sel = Wu[tok_ids].float()             # [n_tok, hidden]
    for h in range(n_heads):
        sl = slice(h * head_dim, (h + 1) * head_dim)
        c_h = Wo[:, sl].float() @ x[sl].float()   # [hidden] contribution
        out[h] = (Wu_sel @ c_h).detach().cpu().numpy()
    return out


def semantic_profile(model, tokenizer, stim, n_layers, n_heads, head_dim, device):
    """Per dep_type: array [n_sent, n_layers] of named-head semantic margin, and
    the per-layer all-head margins at the claimed layer (for ranking)."""
    res = {}
    tap = OProjTap(model, n_layers)
    try:
        for dep, items in stim.items():
            named = NAMED_SCHEDULE[dep][1]
            claimed = NAMED_SCHEDULE[dep][0]
            rows = []                       # [n_sent, n_layers] named-head margin
            allhead_at_claim = []           # [n_sent, n_heads] margin at claimed L
            for it in items:
                enc = tokenizer(it["sentence"], return_tensors="pt")
                ids = enc["input_ids"][0]
                toks = [tokenizer.decode(t) for t in ids]
                dpos = token_positions(toks, it["dep_word"])
                hpos = token_positions(toks, it["head_word"])
                if not dpos or not hpos:
                    continue
                d = dpos[-1]
                hcands = [p for p in hpos if p < d]
                if not hcands:
                    continue
                h_pos = max(hcands)
                ctrl = [p for p in content_positions(toks)
                        if p < d and p != h_pos]
                if not ctrl:
                    continue
                c_pos = ctrl[0]
                tok_head = int(ids[h_pos])
                tok_ctrl = int(ids[c_pos])
                with torch.no_grad():
                    model(enc["input_ids"].to(device))
                # named-head margin per layer (mean over named heads)
                m_L = np.zeros(n_layers)
                for li in range(n_layers):
                    hl = head_logits_at(model, tap.store, li, d, head_dim,
                                        n_heads, [tok_head, tok_ctrl])
                    margins = hl[:, 0] - hl[:, 1]          # [n_heads]
                    m_L[li] = float(np.mean([margins[h] for h in named]))
                    if li == claimed:
                        allhead_at_claim.append(margins.copy())
                rows.append(m_L)
            res[dep] = {
                "margin": np.array(rows),
                "allhead_at_claim": np.array(allhead_at_claim),
                "claimed": claimed, "named": named, "n": len(rows),
            }
    finally:
        tap.remove()
    return res


def bootstrap_ordering(res, B=1000, seed=3):
    rng = np.random.default_rng(seed)
    deps = ["subj", "obj", "coref"]
    mats = {d: res[d]["margin"] for d in deps}
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


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-per", type=int, default=60)
    p.add_argument("--boot", type=int, default=1000)
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    log(f"\n{'='*70}\n  AUDIT #5 SEMANTIC — value-transfer schedule "
        f"(logit-lens head output)\n{'='*70}")
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

    log(f"\n{'-'*70}\n  PART A — semantic value-transfer schedule\n{'-'*70}")
    t0 = time.time()
    res = semantic_profile(model, tokenizer, stim, n_layers, n_heads, head_dim,
                           args.device)
    deps = ["subj", "obj", "coref"]
    claim = {"subj": 27, "obj": 30, "coref": 33}
    profile = {}
    for d in deps:
        m = res[d]["margin"].mean(axis=0)
        pk = int(np.argmax(m))
        profile[d] = {
            "n": res[d]["n"], "peak_layer": pk,
            "peak_margin": round(float(m[pk]), 4),
            "claimed_layer": claim[d],
            "margin_at_claim": round(float(m[claim[d]]), 4),
            "margin_curve": [round(float(x), 4) for x in m],
        }
        log(f"  {d:6s} (n={res[d]['n']}): semantic peak=L{pk} "
            f"(margin={m[pk]:+.3f})  margin@claimL{claim[d]}={m[claim[d]]:+.3f}  "
            f"(>0 = head's output points to the bound entity)")

    p_ord, ci = bootstrap_ordering(res, B=args.boot)
    log(f"\n  bootstrap P(sem-peak(subj)<obj<coref) = {p_ord}  (chance 0.167)")
    log("  peak CIs [p5,med,p95]: " + "  ".join(f"{d}=L{ci[d]}" for d in deps))
    log(f"  part A done in {time.time()-t0:.1f}s")

    log(f"\n{'-'*70}\n  PART B — named-head specificity at CLAIMED layer\n{'-'*70}")
    part_b = {}
    for d in deps:
        A = res[d]["allhead_at_claim"]          # [n_sent, n_heads]
        if len(A) == 0:
            continue
        head_mean = A.mean(axis=0)
        mu, sd = float(head_mean.mean()), float(head_mean.std() + 1e-9)
        order = np.argsort(-head_mean)
        rank = {int(h): int(np.where(order == h)[0][0]) for h in range(n_heads)}
        named = res[d]["named"]
        part_b[d] = {
            "layer": claim[d], "allhead_mean": round(mu, 4),
            "top5": [[int(order[j]), round(float(head_mean[order[j]]), 4)]
                     for j in range(5)],
            "named": {int(h): {"margin": round(float(head_mean[h]), 4),
                               "z": round((head_mean[h] - mu) / sd, 2),
                               "rank": rank[h], "of": n_heads} for h in named},
        }
        log(f"  {d:6s} @L{claim[d]}: all-head mean margin={mu:+.4f} "
            f"top5={part_b[d]['top5']}")
        for h, s in part_b[d]["named"].items():
            log(f"      NAMED H{h}: margin={s['margin']:+.4f}  z={s['z']:+.2f}  "
                f"rank={s['rank']}/{s['of']}")

    log(f"\n{'='*70}\n  VERDICT\n{'='*70}")
    log(f"  semantic ordering P(subj<obj<coref) = {p_ord}  (chance 0.167)")
    for d in deps:
        log(f"  {d:6s}: semantic peak L{profile[d]['peak_layer']} "
            f"(claimed L{claim[d]}); "
            f"margin@claim={profile[d]['margin_at_claim']:+.3f}")
    log("  SCHEDULE real if margins>0, peaks in L27<L30<L33 order (P>>0.167),")
    log("  named head an outlier at its layer; over-read otherwise.")

    results = {
        "audit": "5-binding-schedule-semantic", "model": args.model,
        "n_layers": n_layers, "n_heads": n_heads, "head_dim": head_dim,
        "n_per": args.n_per,
        "partA_profile": profile,
        "ordering": {"p": p_ord, "ci": ci, "chance": round(1 / 6, 4)},
        "partB_head_specificity": part_b,
    }
    out_dir = _PROJECT_ROOT / "results" / "binding-schedule-semantic"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
