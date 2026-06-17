#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — does composition follow TYPE or POSITION? (v2 clean)
"""Type-vs-position dissociation, v2 — the clean symmetric design (fixes v1's leak).

v1 (kernel-certified CCG, surprisal of the right word | left word) found a ROBUST
BACKWARD type-licensing effect (verb cheaper after a subject-NP than after a determiner;
t=6.9 @8B, 7.1 @14B) but a NOISY forward arm. DIAGNOSIS: v1's forward-violate
(intransitive-verb + NOUN, e.g. "runs dog") LEAKS — a noun after a verb reads as the
verb's OBJECT (forward application of a transitive reading), so it is not cleanly
type-violating. ROOT CAUSE: nouns are "universal donors" (almost any context licenses a
following noun as object/compound), so a NOUN-target arm can't be cleanly violated.

v2 FIX — make BOTH targets type-CONSTRAINED functors (verb / determiner), which CAN be
surprising:
  BACKWARD (verb S\\NP wants a subject-NP to its LEFT): target = the VERB
    match   "John runs"  p(verb | NP-subject)              cheap-if-typed
    violate "the runs"   p(verb | non-subject {det,prep})  dear-if-typed
  FORWARD (transitive verb (S\\NP)/NP wants an object-NP to its RIGHT; a determiner
           STARTS that object NP): target = the DETERMINER
    match   "saw the"    p(det | transitive-verb, has object-slot)   cheap-if-typed
    violate "slept the"  p(det | intransitive-verb, NO object-slot)  dear-if-typed
  A determiner cannot be coerced into a non-object reading after an intransitive verb,
  so the forward arm has no donor escape — the symmetric clean fix.

  penalty(dir) = surprisal(violate) - surprisal(match)   (paired by target word)
  DISSOCIATION = penalty(FORWARD) vs penalty(BACKWARD) + per-target consistency
    (fraction of target words showing the effect in the predicted direction — guards
     against one frequent bigram driving the mean).
  BOTH significant + consistent -> composition is TYPE-directed both ways (the s236-s240
    order signal IS type, not L-to-R position; the thesis holds).

CAVEATS (lambda measure, load-bearing): real words -> "type-licensed" still partly
confounds with bigram-FREQUENCY/grammaticality (the DiD + per-target consistency
mitigate, do NOT eliminate). The FREQUENCY-FREE controls (nonce in-context type
teaching; causal ablation of the decoded type direction) are v3. Backward-violate
function words carry their OWN forward expectations -> this tests "model uses
categorial type", not "backward binding" in isolation (that needs the ablation).
Single-word context; bare phrases; 1 model class.

Usage:
    uv run python scripts/experiments/type_directed_v2.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v2.py           # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)

from verbum.lambda_ast import CAtom, CSlash, IllTyped, _unify  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "type-directed"

# ── CCG lexicon (kernel categories as ground truth) ──────────────────────────
NP, N, S = CAtom("NP"), CAtom("N"), CAtom("S")


def fwd(res, arg):  # wants `arg` to the RIGHT ('/')
    return CSlash(res, "/", arg)


def bwd(res, arg):  # wants `arg` to the LEFT ('\\')
    return CSlash(res, "\\", arg)


PROPER = ["John", "Mary", "Sarah", "David", "Anna", "Peter", "Laura", "Thomas",
          "Susan", "James", "Emma", "Robert"]                    # NP (subjects)
DET = ["the", "a", "this", "that", "every", "some", "each", "his",
       "her", "their", "another", "no"]                          # NP/N (det target)
PREP = ["of", "with", "near", "for", "from", "about", "into", "beside"]  # (NP\NP)/NP
IVERB = ["runs", "sleeps", "sings", "arrived", "laughed", "fell",
         "waited", "smiled", "vanished", "slept", "coughed", "stumbled"]  # S\NP
TVERB = ["saw", "liked", "built", "found", "made", "took", "held",
         "knew", "ate", "read", "carried", "chased"]             # (S\NP)/NP

OBJ_PREP = fwd(CSlash(NP, "\\", NP), NP)  # (NP\NP)/NP : wants NP to the right
LEX: dict[str, CSlash | CAtom] = {}
LEX.update({w: NP for w in PROPER})
LEX.update({w: fwd(NP, N) for w in DET})
LEX.update({w: OBJ_PREP for w in PREP})
LEX.update({w: bwd(S, NP) for w in IVERB})
LEX.update({w: fwd(bwd(S, NP), NP) for w in TVERB})  # (S\NP)/NP


def wants_np_right(word: str) -> bool:
    """Kernel-certify: does `word` have an unsaturated NP slot to its RIGHT?

    True for transitive verbs (S\\NP)/NP and prepositions (NP\\NP)/NP — both forward
    functors whose arg unifies with NP. A determiner can START that object NP."""
    c = LEX[word]
    if isinstance(c, CSlash) and c.slash == "/":
        try:
            _unify(c.arg, NP, {})
            return True
        except IllTyped:
            return False
    return False


def is_subject_np(word: str) -> bool:
    """Kernel-certify: is `word` a bare NP (can be a verb's left subject)?"""
    return LEX[word] == NP


def _assert_lexicon() -> None:
    assert wants_np_right("saw") and not wants_np_right("slept"), "TV/IV object slot"
    assert is_subject_np("John") and not is_subject_np("the"), "subject NP"
    assert not is_subject_np("of"), "prep is not a subject"


# ── item generation: paired by TARGET (the measured word) ────────────────────
def gen_items(n_each: int, seed: int):
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    # BACKWARD: target = VERB; does a LEFT subject-NP license it?
    for iv in IVERB:
        for prop in pick(PROPER, n_each):                 # match: NP subject
            items.append({"left": prop, "right": iv, "dir": "bwd",
                          "cond": "bwd_match", "target": iv,
                          "typed": is_subject_np(prop)})
        for ctx in pick(DET + PREP, n_each):              # violate: non-subject
            items.append({"left": ctx, "right": iv, "dir": "bwd",
                          "cond": "bwd_violate", "target": iv,
                          "typed": is_subject_np(ctx)})

    # FORWARD: target = DET; does a LEFT object-taking verb license it?
    for det in DET:
        for tv in pick(TVERB, n_each):                    # match: TV object-slot
            items.append({"left": tv, "right": det, "dir": "fwd",
                          "cond": "fwd_match", "target": det,
                          "typed": wants_np_right(tv)})
        for iv in pick(IVERB, n_each):                    # violate: IV no object-slot
            items.append({"left": iv, "right": det, "dir": "fwd",
                          "cond": "fwd_violate", "target": det,
                          "typed": wants_np_right(iv)})
    rng.shuffle(items)
    return items


# ── surprisal of the TARGET (right word) given the left word ──────────────────
def score_item(item, model, tok, torch_mod):
    left, right = item["left"], item["right"]
    text = f"{left} {right}"
    c0, c1 = len(left) + 1, len(text)  # char span of the right (target) word
    enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
    dev = next(model.parameters()).device
    ids = enc["input_ids"][0]
    offsets = enc["offset_mapping"][0].tolist()
    import torch.nn.functional as func
    with torch_mod.no_grad():
        logits = model(input_ids=ids.unsqueeze(0).to(dev),
                       attention_mask=enc["attention_mask"].to(dev)).logits[0]
    logp = func.log_softmax(logits.float(), dim=-1).cpu()
    ids_cpu = ids.cpu()
    nlls = []
    for j in range(1, ids_cpu.shape[0]):
        s, e = offsets[j]
        # OVERLAP (leading-space BPE token starts before c0; containment misses it)
        if e > s and s < c1 and e > c0:
            nlls.append(-float(logp[j - 1, ids_cpu[j]]))
    return float(np.mean(nlls)) if nlls else None


def paired_penalty(match_by_t, violate_by_t):
    """violate - match, paired by target word (subtracts target lexical identity).

    Also returns per-target consistency (fraction with positive delta)."""
    deltas = []
    for tgt, mvals in match_by_t.items():
        vvals = violate_by_t.get(tgt)
        if mvals and vvals:
            deltas.append(float(np.mean(vvals) - np.mean(mvals)))
    if len(deltas) < 2:
        return None
    arr = np.array(deltas)
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    t = float(arr.mean() / se) if se > 0 else 0.0
    consist = float(np.mean(arr > 0))
    return {"penalty": round(float(arr.mean()), 4), "t": round(t, 3),
            "n_targets": len(deltas), "consistency": round(consist, 3),
            "significant": bool(abs(t) > 2.0)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Type-vs-position dissociation (v2 clean)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=10, help="contexts per target")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    _assert_lexicon()
    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 6
        print("[type-dir2] SMOKE MODE (Qwen3-8B)")

    items = gen_items(n_each, args.seed)
    print(f"[type-dir2] {len(items)} items (n_each={n_each})")
    seen = set()
    for it in items:
        if it["cond"] not in seen:
            seen.add(it["cond"])
            print(f"[type-dir2]   {it['cond']:<12} '{it['left']} {it['right']}'  "
                  f"typed={it['typed']}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    by_cond: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    cond_all: dict[str, list] = defaultdict(list)
    for i, it in enumerate(items):
        if i % 60 == 0:
            print(f"[type-dir2]   scoring {i}/{len(items)} ...")
        s = score_item(it, model, tok, torch_mod)
        if s is None:
            continue
        by_cond[it["cond"]][it["target"]].append(s)
        cond_all[it["cond"]].append(s)

    means = {c: round(float(np.mean(v)), 4) for c, v in sorted(cond_all.items())}
    fwd_pen = paired_penalty(by_cond["fwd_match"], by_cond["fwd_violate"])
    bwd_pen = paired_penalty(by_cond["bwd_match"], by_cond["bwd_violate"])
    did = None
    if fwd_pen and bwd_pen:
        both = bool(fwd_pen["significant"] and bwd_pen["significant"]
                    and fwd_pen["penalty"] > 0 and bwd_pen["penalty"] > 0)
        did = {"fwd_penalty": fwd_pen["penalty"], "bwd_penalty": bwd_pen["penalty"],
               "both_type_directed": both,
               "fwd_consistency": fwd_pen["consistency"],
               "bwd_consistency": bwd_pen["consistency"]}

    verdict = {
        "register": "type-vs-position dissociation v2 (target surprisal | left word)",
        "condition_mean_surprisal": means,
        "forward_type_penalty": fwd_pen, "backward_type_penalty": bwd_pen,
        "dissociation": did, "n_items": len(items)}

    print("\n" + "=" * 70)
    print("TYPE-DIRECTEDNESS v2 (clean) — TYPE or POSITION?")
    print("=" * 70)
    print(f"  {'condition':<14}{'mean surprisal':>16}")
    for c in ("fwd_match", "fwd_violate", "bwd_match", "bwd_violate"):
        print(f"  {c:<14}{means.get(c, float('nan')):>16}")
    print("\n  type-violation penalty (violate - match; >0 = model uses type):")
    pens = (("FORWARD (TV->det slot)", fwd_pen), ("BACKWARD (NP->verb)", bwd_pen))
    for name, p in pens:
        if p:
            sig = "OK" if p["significant"] else "  "
            print(f"    {name:<22} penalty={p['penalty']:>8}  t={p['t']:>7}  "
                  f"n={p['n_targets']:>2}  consist={p['consistency']:<5} {sig}")
    if did:
        print(f"\n  * both_type_directed={did['both_type_directed']}")
    print("=" * 70 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"type_directed_v2_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_items": len(items), "seed": args.seed}
    (RESULTS_DIR / f"type_directed_v2_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[type-dir2] wrote {RESULTS_DIR}/type_directed_v2_verdict_{slug}.json")


if __name__ == "__main__":
    main()
