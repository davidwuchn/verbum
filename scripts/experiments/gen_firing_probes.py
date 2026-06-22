#!/usr/bin/env python3
# register: data-generation (measurement probes for the FFN program-decode, s248)
"""Generate a B-BALANCED firing-probe set for the FFN program-decode experiment (s248).

WHY (s248 IOU). ffn_program_decode.py found the canonical corpus is 84% S-dominant
(47/56) with only 8 B-dominant items — neither register decoded a single B item, so
the per-combinator TRACKING claim was untestable. This generator constructs PROSE whose
saturated kernel reduction (lambda_ast.fired_sequence on the s244-saturated term) is
B-dominant, balanced against B-light controls, so the FFN-vs-attention B-tracking can be
tested honestly.

THE MECHANISM (measured, s248). In this kernel S and B are coupled — every ∧/∨ emits
one S AND one B, so S never strictly exceeds B. Only a TRANSITIVE verb with an
EXISTENTIAL object makes B *dominant*:
    ∀x. P(x) → (∃y. Q(y) ∧ R(x,y))   →  fires S,B,B,B  (B-dominant, B:3 S:1)
B-light controls (B ≤ S):
    ∀x. P(x) → V(x)                   →  fires S,B      (B:1 S:1, tied)
    ∀x. P(x) → (V(x) ∧ W(x))          →  fires S,S,B,B  (B:2 S:2, tied)
Extra B-ladder rungs (graded test): negation B:2/S:1, double-existential B:5/S:1.

So we test TWO things the imbalanced corpus could not:
  • BINARY  — B-dominant (B>S) vs B-tied (B==S), now ~balanced.
  • GRADED  — does the decoded z(B) scale with the ground-truth B-count {1,2,3,5}?

GROUND TRUTH is computed, not asserted: each item is lowered via
lambda_surface.to_kernel, saturated (corpus_firing_survey.saturate), reduced, and its
fired_sequence recorded; items whose computed dominant ≠ intended class are DROPPED.

Output: data/firing-probes.balanced.jsonl — one record per line, schema mirrors the
canonical corpus plus the fired ground truth:
    {input, fol, kernel_term, category, fired_sequence, dominant_fired,
     b_count, s_count, c_count, b_class ∈ {b_dominant, b_tied}}

Usage:
    uv run python scripts/experiments/gen_firing_probes.py
    uv run python scripts/experiments/gen_firing_probes.py --per-class 60 --seed 0

License: MIT. AGENTS.md S5 λ provenance (constructed from this project's lambda_surface
+ lambda_ast; vocabulary is generic English, no external source).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from corpus_firing_survey import _Fresh, saturate

from verbum.lambda_ast import fired_sequence, pretty
from verbum.lambda_surface import to_kernel

_ROOT = Path(__file__).resolve().parent.parent.parent
OUT = _ROOT / "data" / "firing-probes.balanced.jsonl"
META = _ROOT / "data" / "firing-probes.balanced.meta.json"

# ── vocabulary (generic English; -s 3rd-person-singular for "Every N V") ──────────
SUBJ = ["cat", "dog", "farmer", "artist", "student", "teacher", "judge", "writer",
        "chef", "baker", "knight", "clerk", "king", "woman", "doctor", "sailor",
        "painter", "soldier", "dancer", "hunter", "nurse", "poet", "pilot", "guard"]
TVERB = ["fears", "knows", "likes", "finds", "greets", "trusts", "reads", "sees",
         "chases", "follows", "watches", "loves", "owns", "paints", "carries",
         "meets", "calls", "teaches", "serves", "leads"]
IVERB = ["sleeps", "runs", "swims", "falls", "sings", "walks", "works", "dreams",
         "laughs", "waits", "travels", "rests", "speaks", "listens", "wanders"]
OBJ = ["dog", "book", "bone", "fish", "song", "letter", "house", "apple", "horse",
       "garden", "map", "key", "ship", "tower", "river", "island", "engine", "owl"]
ADJ = ["black", "big", "old", "small", "young", "tall", "swift", "quiet"]


def _art(word: str) -> str:
    return "an" if word[0] in "aeiou" else "a"


def _fire(fol: str):
    """(dominant, b, s, c, kernel_str, fired_list) — or None on parse/reduce failure."""
    try:
        k = to_kernel(fol)
        seq = fired_sequence(saturate(k, _Fresh()))
    except Exception:
        return None
    if not seq:
        return None
    c = Counter(seq)
    dom = c.most_common(1)[0][0]
    return dom, c.get("B", 0), c.get("S", 0), c.get("C", 0), pretty(k), seq


def _emit(input_text, fol, category, b_class):
    f = _fire(fol)
    if f is None:
        return None
    dom, b, s, cc, kstr, seq = f
    return {
        "input": input_text, "fol": fol, "kernel_term": kstr, "category": category,
        "fired_sequence": seq, "dominant_fired": dom,
        "b_count": b, "s_count": s, "c_count": cc, "b_class": b_class,
    }


def generate(per_class: int, seed: int) -> list[dict]:
    import random

    rng = random.Random(seed)
    out: list[dict] = []
    seen: set[str] = set()

    def add(rec):
        if rec is None or rec["input"] in seen:
            return False
        seen.add(rec["input"])
        out.append(rec)
        return True

    # ── B-DOMINANT: transitive + existential object (B:3 S:1) ────────────────────
    tried = 0
    while sum(r["b_class"] == "b_dominant" and r["category"] == "trans_exist"
              for r in out) < per_class and tried < per_class * 40:
        tried += 1
        sub, tv, ob = rng.choice(SUBJ), rng.choice(TVERB), rng.choice(OBJ)
        prose = f"Every {sub} {tv} {_art(ob)} {ob}."
        fol = f"∀x. {sub}(x) → (∃y. {ob}(y) ∧ {tv}(x, y))"
        rec = _emit(prose, fol, "trans_exist", "b_dominant")
        if rec and rec["dominant_fired"] == "B" and rec["b_count"] > rec["s_count"]:
            add(rec)

    # ── B-DOMINANT ladder: negation (B:2 S:1) ────────────────────────────────────
    n_neg = max(8, per_class // 4)
    tried = 0
    while sum(r["category"] == "negation" for r in out) < n_neg and tried < n_neg * 40:
        tried += 1
        sub, iv = rng.choice(SUBJ), rng.choice(IVERB)
        prose = f"No {sub} {iv}."
        fol = f"∀x. {sub}(x) → ¬{iv}(x)"
        rec = _emit(prose, fol, "negation", "b_dominant")
        if rec and rec["dominant_fired"] == "B" and rec["b_count"] > rec["s_count"]:
            add(rec)

    # ── B-DOMINANT strong: double existential (B:5 S:1) ──────────────────────────
    n_dbl = max(8, per_class // 4)
    tried = 0
    while sum(r["category"] == "double_exist" for r in out) < n_dbl \
            and tried < n_dbl * 60:
        tried += 1
        sub, tv = rng.choice(SUBJ), rng.choice(TVERB)
        o1, o2 = rng.sample(OBJ, 2)
        prose = f"Every {sub} {tv} {_art(o1)} {o1} in {_art(o2)} {o2}."
        fol = (f"∀x. {sub}(x) → (∃y. {o1}(y) ∧ ∃z. {o2}(z) ∧ {tv}(x, y))")
        rec = _emit(prose, fol, "double_exist", "b_dominant")
        if rec and rec["dominant_fired"] == "B" and rec["b_count"] >= 4:
            add(rec)

    # ── B-TIED control: simple intransitive (B:1 S:1) ────────────────────────────
    tried = 0
    while sum(r["category"] == "intrans" for r in out) < per_class \
            and tried < per_class * 40:
        tried += 1
        sub, iv = rng.choice(SUBJ), rng.choice(IVERB)
        prose = f"Every {sub} {iv}."
        fol = f"∀x. {sub}(x) → {iv}(x)"
        rec = _emit(prose, fol, "intrans", "b_tied")
        if rec and rec["b_count"] <= rec["s_count"]:
            add(rec)

    # ── B-TIED control: conjunctive scope (B:2 S:2) ──────────────────────────────
    tried = 0
    while sum(r["category"] == "conj_scope" for r in out) < per_class \
            and tried < per_class * 40:
        tried += 1
        sub = rng.choice(SUBJ)
        v1, v2 = rng.sample(IVERB, 2)
        prose = f"Every {sub} {v1} and {v2}."
        fol = f"∀x. {sub}(x) → ({v1}(x) ∧ {v2}(x))"
        rec = _emit(prose, fol, "conj_scope", "b_tied")
        if rec and rec["b_count"] <= rec["s_count"]:
            add(rec)

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate B-balanced firing probes (s248)")
    ap.add_argument("--per-class", type=int, default=45)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.per_class, args.seed)
    by_class = Counter(r["b_class"] for r in rows)
    by_cat = Counter(r["category"] for r in rows)
    by_bcount = Counter(r["b_count"] for r in rows)
    dom = Counter(r["dominant_fired"] for r in rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    META.write_text(json.dumps({
        "generated_utc": datetime.now(UTC).isoformat(),
        "n": len(rows), "per_class": args.per_class, "seed": args.seed,
        "by_b_class": dict(by_class), "by_category": dict(by_cat),
        "by_b_count": {str(k): v for k, v in sorted(by_bcount.items())},
        "by_dominant_fired": dict(dom),
        "method": "lower via lambda_surface.to_kernel; saturate quantifiers (s244); "
                  "fired_sequence ground truth; drop items whose computed dominant ≠ "
                  "intended class.",
    }, indent=2), encoding="utf-8")

    print(f"[gen] wrote {OUT}  ({len(rows)} probes)")
    print(f"[gen] b_class:   {dict(by_class)}")
    print(f"[gen] category:  {dict(by_cat)}")
    print(f"[gen] b_count:   {dict(sorted(by_bcount.items()))}")
    print(f"[gen] dominant:  {dict(dom)}")


if __name__ == "__main__":
    main()
