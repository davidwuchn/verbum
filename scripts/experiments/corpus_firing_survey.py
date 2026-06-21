#!/usr/bin/env python3
"""Corpus firing survey — which combinators ever FIRE in the certified corpus (s244).

THE QUESTION (s244, Michael). Exp 1 (kernel_splice_exp1_ksplice.py) found the
K-geometry causally NECESSARY/DELIVERABLE in the ROUTING register but BEHAVIORALLY
weak on prose, and sharpened the open question to "find the operand-bound sentences
that actually fire K". The naive plan was: pick K-engaging certified items via
lambda_ast.fired_sequence, splice the exact K-move. This survey shows that plan has
NO targets — and reveals which combinators do.

WHY fired_sequence is empty on every stored term. The canonical corpus
(data/compile-*.canonical.jsonl) stores `kernel_term` = the POINT-FREE / already-
NORMAL logical form. Bracket abstraction (Turner 1979) is the INVERSE of reduction:
it emits a term whose combinators are UNDER-APPLIED (inert structure), and which
fires nothing until applied to arguments. So `fired_sequence(parse(kernel_term))` ==
[] for all 559 items — the stored form is a normal form by construction.

THE SATURATION. A quantifier `forall P` / `exists P` / `iota P` is the semantic
operator that APPLIES the abstracted one-place predicate P to a witness. This survey
saturates every quantifier with a fresh witness atom, reduces, and records what
FIRES. That reconstructs the actual reduction the point-free form encodes — the
behavioral register where output is kernel-checkable.

THE FINDING (s244): the corpus fires only {B, S, C} (concentrated in `quantified`);
it NEVER fires {I, K, W, D, Y, M}. This is DISJOINT from the Exp 0.5 firmed splice
set {I, K, Y} — K fires in 0/559 items. That fully explains Exp 1's behavioral-null
result (K never executes a reduction here) and ties to the Qwen3-4B `λx.` artifact:
a vacuous binder compiles to K, but the real compiler emits S/B/C for these
sentences, never K — so the inserted `λx.` was manufacturing spurious K-structure
the kernel never produces (the reason those probes were distilled).

Usage:
    uv run python scripts/experiments/corpus_firing_survey.py

License: MIT. AGENTS.md S5 λ provenance (written from this project's audit, not
nucleus).
"""

from __future__ import annotations

import collections
import json
from datetime import UTC, datetime
from pathlib import Path

from verbum.lambda_ast import (
    App,
    Atom,
    Comb,
    Status,
    fired_sequence,
    parse,
    reduce,
    spine,
)

_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _ROOT / "results" / "corpus-firing-survey"
CORPUS = {
    "train": _ROOT / "data" / "compile-train.canonical.jsonl",
    "test": _ROOT / "data" / "compile-test.canonical.jsonl",
    "eval": _ROOT / "data" / "compile-eval.canonical.jsonl",
}

QUANT = {"forall", "exists", "iota"}
ALL_COMBS = ["I", "K", "M", "W", "C", "B", "S", "D", "Y"]


def present_combs(t) -> collections.Counter:
    """Count combinator atoms PRESENT in a term (inert or not)."""
    out: collections.Counter = collections.Counter()

    def go(x) -> None:
        if isinstance(x, Comb):
            out[x.name] += 1
        elif isinstance(x, App):
            go(x.fn)
            go(x.arg)

    go(t)
    return out


class _Fresh:
    """Fresh witness-atom generator (one per bound quantifier variable)."""

    def __init__(self) -> None:
        self.n = 0

    def __call__(self) -> Atom:
        a = Atom(f"·w{self.n}")
        self.n += 1
        return a


def saturate(t, fresh: _Fresh):
    """Apply every quantifier's abstracted predicate to a fresh witness.

    `forall P args...` -> `(P witness) args...` (semantic saturation). Recurses so
    nested quantifiers each bind their own witness. Non-quantifier applications
    recurse structurally.
    """
    if isinstance(t, App):
        head, args = spine(t)
        if isinstance(head, Atom) and head.name in QUANT and len(args) >= 1:
            pred = saturate(args[0], fresh)
            applied = App(pred, fresh())  # bind one witness to the one-place predicate
            r = applied
            for a in args[1:]:
                r = App(r, saturate(a, fresh))
            return r
        return App(saturate(t.fn, fresh), saturate(t.arg, fresh))
    return t


def main() -> None:
    rows = [json.loads(line) for path in CORPUS.values() for line in open(path)]

    present: collections.Counter = collections.Counter()
    fired: collections.Counter = collections.Counter()
    items_fire: collections.Counter = collections.Counter()  # distinct items per comb
    by_cat_fire: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    examples: dict[str, list] = collections.defaultdict(list)
    non_nf = 0

    for r in rows:
        t = parse(r["kernel_term"])
        for c, n in present_combs(t).items():
            present[c] += n
        sat = saturate(t, _Fresh())
        if reduce(sat).status != Status.NORMAL_FORM:
            non_nf += 1
        seq = fired_sequence(sat)
        seen: set[str] = set()
        for c in seq:
            fired[c] += 1
            by_cat_fire[r["category"]][c] += 1
            if c not in seen:
                items_fire[c] += 1
                seen.add(c)
                if len(examples[c]) < 3:
                    examples[c].append(
                        {"input": r["input"], "kernel_term": r["kernel_term"],
                         "fired_sequence": seq})

    fires_set = sorted([c for c in ALL_COMBS if fired[c] > 0])
    never_fire = sorted([c for c in ALL_COMBS if fired[c] == 0])

    verdict = {
        "corpus_items": len(rows),
        "non_normal_form_after_saturation": non_nf,
        "saturation": "quantifier predicate applied to fresh witness, then reduced",
        "present_inert": dict(present.most_common()),
        "fired_total": dict(fired.most_common()),
        "items_firing_per_combinator": dict(items_fire.most_common()),
        "fired_by_category": {k: dict(v.most_common()) for k, v in by_cat_fire.items()},
        "fires_set": fires_set,
        "never_fires_set": never_fire,
        "exp0_5_firmed_splice_set": ["I", "K", "Y"],
        "disjoint_from_firing_set": sorted(set(["I", "K", "Y"]) & set(fires_set)) == [],
        "K_fires_in_items": items_fire.get("K", 0),
        "examples": {c: examples[c] for c in fires_set},
    }

    # ── report ──────────────────────────────────────────────────────────────────────
    print("═" * 78)
    print("CORPUS FIRING SURVEY — which combinators ever fire (s244)")
    print("═" * 78)
    print(f"  items={len(rows)}  non-normal-form after saturation={non_nf}")
    print(f"\n  {'comb':>5}{'present':>9}{'fired':>7}{'items':>7}")
    for c in ALL_COMBS:
        print(f"  {c:>5}{present.get(c, 0):>9}{fired.get(c, 0):>7}"
              f"{items_fire.get(c, 0):>7}")
    print(f"\n  FIRES:       {fires_set}")
    print(f"  NEVER fires: {never_fire}")
    print(f"  Exp 0.5 firmed splice set {{I,K,Y}} disjoint from firing set: "
          f"{verdict['disjoint_from_firing_set']}")
    print(f"  K fires in {verdict['K_fires_in_items']}/{len(rows)} items")
    print("\n  fired by category:")
    for cat in sorted(by_cat_fire):
        print(f"    {cat:18s} {dict(by_cat_fire[cat].most_common())}")
    print("═" * 78)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "firing_survey.json").write_text(
        json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    meta = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "corpus": {k: str(v.relative_to(_ROOT)) for k, v in CORPUS.items()},
        "method": "saturate quantifier predicates with fresh witnesses, reduce, "
                  "collect fired_sequence (the certified per-step opcode trace)",
    }
    (RESULTS_DIR / "meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\n[survey] wrote {RESULTS_DIR}/firing_survey.json")


if __name__ == "__main__":
    main()
