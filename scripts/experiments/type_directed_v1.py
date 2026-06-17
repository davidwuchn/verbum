#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — does composition follow TYPE or POSITION? (v1)
"""Type-vs-position dissociation — is the composition we measured (s236-s240
order-cost) TYPE-directed, or merely LEFT-TO-RIGHT positional (copy/induction)?
(lead 2d — the VERBUM thesis: type-directed composition.)

THE QUESTION (Michael): "the system can't do combinator composition without some
typing — what would direct the composition?" Prior work (s139 type-probe-qwen3-32b)
shows types are DECODABLE (88-96%), LEXICAL, GEOMETRIC, and CO-LOCATED with
combinator dispatch at L0-L2 — but co-location is CORRELATION, not DIRECTION. This
probe tests the behavioural claim: does the model USE the type to direct composition?

THE AUTOREGRESSIVE-CAUSALITY TRAP (lambda measure — the load-bearing control): the
model reads strictly L-to-R. FORWARD composition (functor-left, arg-right) aligns
with reading order; BACKWARD composition (arg-left, functor-right) binds an argument
seen BEFORE its licensing functor. A naive "argument surprisal" would show backward
costing more — but that is autoregressive causality, NOT type-blindness. We avoid it
by measuring the surprisal of the SECOND (right) token given the first, and crossing
DIRECTION x TYPE so the dissociation is a DIFFERENCE-OF-DIFFERENCES (subtracting the
generic "grammatical bigrams are cheaper" baseline).

THE DESIGN (kernel-certified CCG types as ground truth; CSlash '/' fwd, '\\' bwd):
  FORWARD functor (det NP/N, adj N/N — wants its arg to the RIGHT):
    match   "the dog"   p(N | det)   type-licensed right-neighbour    cheap-if-typed
    violate "the runs"  p(IV | det)  det's forward N-expectation void  dear-if-typed
  BACKWARD functor (intransitive verb S\\NP — wants its NP subject LEFT):
    match   "John runs" p(IV | NP)   NP left-context licenses the verb cheap-if-typed
    violate "the runs"  p(IV | det)  det left-context does not license dear-if-typed

  penalty(dir) = surprisal(violate) - surprisal(match)   (paired by target word)
  DISSOCIATION = penalty(FORWARD) vs penalty(BACKWARD):
    - BOTH large positive -> composition is TYPE-directed in BOTH directions (the
      order signal IS types; thesis holds; s236 positional caveat killed).
    - only FORWARD (backward ~ 0) -> forward/positional bias; backward (retroactive)
      binding NOT type-licensed -> the order signal is L-to-R position, not type.

CAVEATS (lambda measure): real words -> "type-licensed" partly confounds with
grammaticality/bigram-frequency (the DiD mitigates, not eliminates); single-word
L-context; bare phrases (no carrier); 1 model class. v1 = first cut, ITERATE on data.

Usage:
    uv run python scripts/experiments/type_directed_v1.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v1.py           # 14B

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


def fwd(res, arg):  # functor wants `arg` to the RIGHT (forward, '/')
    return CSlash(res, "/", arg)


def bwd(res, arg):  # functor wants `arg` to the LEFT (backward, '\\')
    return CSlash(res, "\\", arg)


PROPER = ["John", "Mary", "Sarah", "David", "Anna", "Peter", "Laura", "Thomas"]
NOUN = ["dog", "car", "book", "house", "tree", "river", "table", "stone"]
DET = ["the", "a", "this", "that", "every", "some", "each", "his"]
ADJ = ["red", "small", "old", "tall", "cold", "quick", "dark", "soft"]
IVERB = ["runs", "sleeps", "sings", "arrived", "laughed", "fell", "waited", "smiled"]

LEX: dict[str, CSlash | CAtom] = {}
LEX.update({w: NP for w in PROPER})       # proper nouns
LEX.update({w: N for w in NOUN})          # common nouns
LEX.update({w: fwd(NP, N) for w in DET})  # determiners NP/N
LEX.update({w: fwd(N, N) for w in ADJ})   # adjectives N/N
LEX.update({w: bwd(S, NP) for w in IVERB})  # intransitive verbs S\NP


def applies(left: str, right: str):
    """Kernel-certify adjacent CCG combination of two words.

    Returns (ok, rule). Forward: left functor X/Y + right Y -> X. Backward: right
    functor X\\Y + left Y -> X. Uses the kernel _unify (the exact S2 type-check)."""
    lc, rc = LEX[left], LEX[right]
    if isinstance(lc, CSlash) and lc.slash == "/":  # forward: functor on the LEFT
        try:
            _unify(lc.arg, rc, {})
            return True, "fwd"
        except IllTyped:
            pass
    if isinstance(rc, CSlash) and rc.slash == "\\":  # backward: functor on the RIGHT
        try:
            _unify(rc.arg, lc, {})
            return True, "bwd"
        except IllTyped:
            pass
    return False, None


def _assert_lexicon() -> None:
    """Sanity: the canonical cells certify as designed (fail loud if not)."""
    assert applies("the", "dog") == (True, "fwd"), "det+N must forward-license"
    assert applies("red", "dog") == (True, "fwd"), "adj+N must forward-license"
    assert applies("John", "runs") == (True, "bwd"), "NP+IV must backward-license"
    assert applies("the", "runs")[0] is False, "det+IV must NOT license"
    assert applies("runs", "dog")[0] is False, "IV+N must NOT license"


# ── item generation: DIRECTION x TYPE, paired by TARGET (the right word) ──────
def gen_items(n_each: int, seed: int):
    """Each item = (left, right, dir, typed, target=right). Surprisal measured at
    the RIGHT word given the LEFT; paired match/violate share the SAME target."""
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    # FORWARD functor = det/adj wanting N to the right; TARGET = the noun
    for noun in NOUN:
        for det in pick(DET + ADJ, n_each):       # match: licenses noun on right
            ok, rule = applies(det, noun)
            items.append({"left": det, "right": noun, "dir": "fwd",
                          "typed": ok and rule == "fwd",
                          "cond": "fwd_match", "target": noun})
        for iv in pick(IVERB, n_each):             # violate: verb-left, no fwd license
            ok, _ = applies(iv, noun)
            items.append({"left": iv, "right": noun, "dir": "fwd", "typed": ok,
                          "cond": "fwd_violate", "target": noun})

    # BACKWARD functor = intransitive verb wanting NP to the left; TARGET = verb
    for iv in IVERB:
        for prop in pick(PROPER, n_each):          # match: NP-left licenses verb
            ok, rule = applies(prop, iv)
            items.append({"left": prop, "right": iv, "dir": "bwd",
                          "typed": ok and rule == "bwd",
                          "cond": "bwd_match", "target": iv})
        for det in pick(DET, n_each):              # violate: det-left, no bwd license
            ok, _ = applies(det, iv)
            items.append({"left": det, "right": iv, "dir": "bwd", "typed": ok,
                          "cond": "bwd_violate", "target": iv})
    rng.shuffle(items)
    return items


# ── surprisal of the TARGET (right word) given the left word ──────────────────
def score_item(item, model, tok, torch_mod):
    """Mean -log p over the target (right-word) tokens, given the left prefix.

    Bare 2-word phrase 'left right'; target is the final word, so its tokens carry
    the leading space. Locate target tokens by char-span of the right word."""
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
        # OVERLAP (not start-containment): the leading-space BPE token of the target
        # word starts on the space BEFORE c0, so containment misses it (v9 lesson).
        if e > s and s < c1 and e > c0:
            nlls.append(-float(logp[j - 1, ids_cpu[j]]))
    return float(np.mean(nlls)) if nlls else None


def paired_penalty(by_target_match, by_target_violate):
    """violate - match, paired by target word (subtracts target-word identity)."""
    deltas = []
    for tgt, mvals in by_target_match.items():
        vvals = by_target_violate.get(tgt)
        if mvals and vvals:
            deltas.append(float(np.mean(vvals) - np.mean(mvals)))
    if len(deltas) < 2:
        return None
    arr = np.array(deltas)
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    t = float(arr.mean() / se) if se > 0 else 0.0
    return {"penalty": round(float(arr.mean()), 4), "t": round(t, 3),
            "n_targets": len(deltas), "significant": bool(abs(t) > 2.0)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Type-vs-position dissociation (v1)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=8, help="contexts per target")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    _assert_lexicon()
    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 4
        print("[type-dir] SMOKE MODE (Qwen3-8B)")

    items = gen_items(n_each, args.seed)
    print(f"[type-dir] {len(items)} items (n_each={n_each})")
    seen = set()
    for it in items:  # sample one of each condition + kernel certification
        if it["cond"] not in seen:
            seen.add(it["cond"])
            ok, rule = applies(it["left"], it["right"])
            print(f"[type-dir]   {it['cond']:<12} '{it['left']} {it['right']}'  "
                  f"typed={it['typed']} (kernel licensed={ok} rule={rule})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    by_cond: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    cond_all: dict[str, list] = defaultdict(list)
    for i, it in enumerate(items):
        if i % 50 == 0:
            print(f"[type-dir]   scoring {i}/{len(items)} ...")
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
        ratio = (round(bwd_pen["penalty"] / fwd_pen["penalty"], 3)
                 if fwd_pen["penalty"] else None)
        did = {"fwd_penalty": fwd_pen["penalty"], "bwd_penalty": bwd_pen["penalty"],
               "both_type_directed": both, "bwd_over_fwd_ratio": ratio}

    verdict = {
        "register": "type-vs-position dissociation (target surprisal | left word)",
        "condition_mean_surprisal": means,
        "forward_type_penalty": fwd_pen, "backward_type_penalty": bwd_pen,
        "dissociation": did, "n_items": len(items)}

    print("\n" + "=" * 70)
    print("TYPE-DIRECTEDNESS v1 — does composition follow TYPE or POSITION?")
    print("=" * 70)
    print(f"  {'condition':<14}{'mean surprisal':>16}")
    for c in ("fwd_match", "fwd_violate", "bwd_match", "bwd_violate"):
        print(f"  {c:<14}{means.get(c, float('nan')):>16}")
    print("\n  type-violation penalty (violate - match; >0 = model uses type):")
    pens = (("FORWARD (det/adj->N)", fwd_pen), ("BACKWARD (NP->verb)", bwd_pen))
    for name, p in pens:
        if p:
            sig = "OK" if p["significant"] else "  "
            print(f"    {name:<22} penalty={p['penalty']:>8}  t={p['t']:>7}  "
                  f"n={p['n_targets']:>2}  {sig}")
    if did:
        print(f"\n  * both_type_directed={did['both_type_directed']}  "
              f"(bwd/fwd ratio={did['bwd_over_fwd_ratio']})")
    print("=" * 70 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"type_directed_v1_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_items": len(items), "seed": args.seed}
    (RESULTS_DIR / f"type_directed_v1_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[type-dir] wrote {RESULTS_DIR}/type_directed_v1_verdict_{slug}.json")


if __name__ == "__main__":
    main()
