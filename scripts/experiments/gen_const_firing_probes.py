#!/usr/bin/env python3
# register: data-generation (CONSTANT-labeled firing probes, s249 C-tracking test)
"""Generate a C-BALANCED, CONSTANT-labeled firing-probe set (s249).

WHY (s248 → s249 IOU). The s248 FFN program-decode TRACKING test failed to decode the
combinator the corpus item "fires" — but s248 cont.2/cont.3 then showed WHY: we labelled
ground truth with the Montague EXISTENTIAL reading (`a dog` = ∃y.dog(y)∧…, B-heavy), yet
the model computes objects APPLICATIVELY (`fears(x, dog)` → object as CONSTANT → C).
The weak-B was a LABELING MISMATCH. This generator builds the corrected ground truth:
the SAME quantified prose, labelled with the CONSTANT/applicative reading (object → C),
so we can re-run TRACKING and ask the s249 question — *does the corpus B-tracking
failure flip to C-tracking success?*

THE MECHANISM (measured, s248 cont.2). Under the constant reading, C-count == #objects:
    ∀x. P(x) → V(x)            →  S,B            C:0  (S-dominant)   c_light
    ∀x. P(x) → V(x, o)         →  S,B,C          C:1  (S-dominant)   c_light
    ∀x. P(x) → V(x, o1, o2)    →  S,B,C,C        C:2  (C-DOMINANT)   c_dominant
So a ditransitive (double-object) quantified sentence is C-dominant — the C analog
of the s248 B-dominant transitive-existential. The set is balanced: c_dominant
(ditransitive) vs c_light (intransitive + transitive), with a C-count ladder {0,1,2}
for the graded test.

This is the constant-reading mirror of gen_firing_probes.py (which built the existential
B-balanced set). Prose is generic English; ground truth is COMPUTED, not asserted: each
item is lowered via lambda_surface.to_kernel, saturated (corpus_firing_survey.saturate),
reduced, and its fired_sequence recorded; items whose computed dominant / c_count ≠ the
intended class are DROPPED.

Output: data/firing-probes.const.jsonl — schema mirrors firing-probes.balanced.jsonl so
ffn_program_decode.build_firing_corpus reads it unchanged:
    {input, fol, kernel_term, category, fired_sequence, dominant_fired,
     b_count, s_count, c_count, c_class ∈ {c_dominant, c_light}}

Usage:
    uv run python scripts/experiments/gen_const_firing_probes.py
    uv run python scripts/experiments/gen_const_firing_probes.py --per-class 60 --seed 0

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
from gen_firing_probes import IVERB, OBJ, SUBJ, TVERB, _art
from gen_reading_probes import DVERB, RECIP, THEME

from verbum.lambda_ast import fired_sequence, pretty
from verbum.lambda_surface import to_kernel

_ROOT = Path(__file__).resolve().parent.parent.parent
OUT = _ROOT / "data" / "firing-probes.const.jsonl"
META = _ROOT / "data" / "firing-probes.const.meta.json"


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


def _emit(input_text, fol, category, c_class, want_c):
    """Emit the record iff it fires, its c_count matches the intended ladder rung
    (`want_c`), and its dominant matches the class contract."""
    f = _fire(fol)
    if f is None:
        return None
    dom, b, s, cc, kstr, seq = f
    if cc != want_c:
        return None
    if c_class == "c_dominant" and dom != "C":
        return None
    if c_class == "c_light" and dom == "C":
        return None
    return {
        "input": input_text, "fol": fol, "kernel_term": kstr, "category": category,
        "fired_sequence": seq, "dominant_fired": dom,
        "b_count": b, "s_count": s, "c_count": cc, "c_class": c_class,
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

    # ── C-DOMINANT: ditransitive constant object (S,B,C,C → C:2) ─────────────────
    tried = 0
    while sum(r["category"] == "ditrans_const" for r in out) < per_class \
            and tried < per_class * 60:
        tried += 1
        sub, dv = rng.choice(SUBJ), rng.choice(DVERB)
        rc, th = rng.choice(RECIP), rng.choice(THEME)
        prose = f"Every {sub} {dv} {_art(rc)} {rc} {_art(th)} {th}."
        fol = f"∀x. {sub}(x) → {dv}(x, {rc}, {th})"
        add(_emit(prose, fol, "ditrans_const", "c_dominant", want_c=2))

    # ── C-LIGHT: transitive constant object (S,B,C → C:1, S-dominant) ────────────
    n_trans = max(8, per_class // 2)
    tried = 0
    while sum(r["category"] == "trans_const" for r in out) < n_trans \
            and tried < n_trans * 40:
        tried += 1
        sub, tv, ob = rng.choice(SUBJ), rng.choice(TVERB), rng.choice(OBJ)
        prose = f"Every {sub} {tv} {_art(ob)} {ob}."
        fol = f"∀x. {sub}(x) → {tv}(x, {ob})"
        add(_emit(prose, fol, "trans_const", "c_light", want_c=1))

    # ── C-LIGHT: intransitive (S,B → C:0) ────────────────────────────────────────
    n_intrans = max(8, per_class // 2)
    tried = 0
    while sum(r["category"] == "intrans" for r in out) < n_intrans \
            and tried < n_intrans * 40:
        tried += 1
        sub, iv = rng.choice(SUBJ), rng.choice(IVERB)
        prose = f"Every {sub} {iv}."
        fol = f"∀x. {sub}(x) → {iv}(x)"
        add(_emit(prose, fol, "intrans", "c_light", want_c=0))

    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate C-balanced constant-labeled firing probes (s249)")
    ap.add_argument("--per-class", type=int, default=67)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.per_class, args.seed)
    by_class = Counter(r["c_class"] for r in rows)
    by_cat = Counter(r["category"] for r in rows)
    by_ccount = Counter(r["c_count"] for r in rows)
    dom = Counter(r["dominant_fired"] for r in rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    META.write_text(json.dumps({
        "generated_utc": datetime.now(UTC).isoformat(),
        "n": len(rows), "per_class": args.per_class, "seed": args.seed,
        "by_c_class": dict(by_class), "by_category": dict(by_cat),
        "by_c_count": {str(k): v for k, v in sorted(by_ccount.items())},
        "by_dominant_fired": dict(dom),
        "reading": "constant/applicative (object → C); the s248 corrected labeling",
        "method": "lower via lambda_surface.to_kernel; saturate quantifiers (s244); "
                  "fired_sequence ground truth; drop items whose computed dominant / "
                  "c_count ≠ intended class.",
    }, indent=2), encoding="utf-8")

    print(f"[gen] wrote {OUT}  ({len(rows)} probes)")
    print(f"[gen] c_class:   {dict(by_class)}")
    print(f"[gen] category:  {dict(by_cat)}")
    print(f"[gen] c_count:   {dict(sorted(by_ccount.items()))}")
    print(f"[gen] dominant:  {dict(dom)}")


if __name__ == "__main__":
    main()
