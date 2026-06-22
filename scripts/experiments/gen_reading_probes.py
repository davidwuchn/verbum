#!/usr/bin/env python3
# register: data-generation (reading-preference probes, s248 reason-3 test)
"""Object-count reading-preference probes — does the model compute objects as
EXISTENTIALS (Montague, B-heavy) or as CONSTANTS (entity arguments, C-heavy)? (s248)

WHY (s248 reason #3). ffn_program_decode found only weak B-tracking on prose labelled
with the EXISTENTIAL reading (`a dog` = ∃y.dog(y)∧…). A free post-hoc on the balanced
run showed the gate register decodes MORE C and LESS B when an object is present — the
OPPOSITE of the existential prediction, exactly the CONSTANT-object prediction. So the
weak B-signal may be a LABELING MISMATCH: we labelled B, the model computes constant→C.
This generator builds the clean discriminator to test it directly.

THE DISCRIMINATOR (measured, exact) along the OBJECT-COUNT ladder {0,1,2}:
    intransitive  "Every farmer sleeps."       0 obj  exist=const  S,B
    transitive    "Every cat fears a dog."      1 obj  const S,B,C  | exist S,B,B,B
    ditransitive  "Every chef gives a guest …"  2 obj  const S,B,C,C | exist B:5
    • CONSTANT reading   → C-count == #objects (B flat at 1).
    • EXISTENTIAL reading → B-count scales {1,3,5} (C flat at 0).
Decoding z(C) vs z(B) against the ladder separates the two readings — and the SLOPE
controls for the C common-mode (a uniform baseline cancels in the slope).

Each record carries BOTH candidate labelings (prose is identical; only the LF differs),
computed (to_kernel → saturate → fired_sequence), verified, round-tripped.

Output: data/reading-probes.jsonl
    {input, n_objects, category, exist_fol, const_fol, exist_kernel, const_kernel,
     exist_fired, const_fired, exist_b, exist_c, const_b, const_c}

Usage:
    uv run python scripts/experiments/gen_reading_probes.py
    uv run python scripts/experiments/gen_reading_probes.py --per-class 45 --seed 0

License: MIT. AGENTS.md S5 λ provenance (constructed from lambda_surface + lambda_ast).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from corpus_firing_survey import _Fresh, saturate
from gen_firing_probes import IVERB, OBJ, SUBJ, TVERB, _art

from verbum.lambda_ast import fired_sequence, pretty
from verbum.lambda_surface import to_kernel

_ROOT = Path(__file__).resolve().parent.parent.parent
OUT = _ROOT / "data" / "reading-probes.jsonl"
META = _ROOT / "data" / "reading-probes.meta.json"

# ditransitive vocabulary (double-object construction "V a RECIP a THEME")
DVERB = ["gives", "sends", "offers", "brings", "shows", "hands", "lends", "sells"]
RECIP = ["guest", "friend", "child", "king", "queen", "stranger", "neighbor", "rival"]
THEME = ["cake", "book", "letter", "gift", "song", "map", "key", "coin", "rose", "lamp"]


def _fired(fol: str):
    """(fired_list, kernel_str, b, c) or None on failure."""
    try:
        k = to_kernel(fol)
        seq = fired_sequence(saturate(k, _Fresh()))
    except Exception:
        return None
    if not seq:
        return None
    c = Counter(seq)
    return seq, pretty(k), c.get("B", 0), c.get("C", 0)


def _emit(input_text, n_obj, category, exist_fol, const_fol):
    e = _fired(exist_fol)
    co = _fired(const_fol)
    if e is None or co is None:
        return None
    e_seq, e_k, e_b, e_c = e
    c_seq, c_k, c_b, c_c = co
    # the const reading must put C == #objects (the discriminator's contract)
    if c_c != n_obj:
        return None
    return {
        "input": input_text, "n_objects": n_obj, "category": category,
        "exist_fol": exist_fol, "const_fol": const_fol,
        "exist_kernel": e_k, "const_kernel": c_k,
        "exist_fired": e_seq, "const_fired": c_seq,
        "exist_b": e_b, "exist_c": e_c, "const_b": c_b, "const_c": c_c,
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

    # 0 objects — intransitive (exist == const)
    tried = 0
    while sum(r["n_objects"] == 0 for r in out) < per_class and tried < per_class * 40:
        tried += 1
        sub, iv = rng.choice(SUBJ), rng.choice(IVERB)
        prose = f"Every {sub} {iv}."
        fol = f"∀x. {sub}(x) → {iv}(x)"
        add(_emit(prose, 0, "intransitive", fol, fol))

    # 1 object — transitive
    tried = 0
    while sum(r["n_objects"] == 1 for r in out) < per_class and tried < per_class * 40:
        tried += 1
        sub, tv, ob = rng.choice(SUBJ), rng.choice(TVERB), rng.choice(OBJ)
        prose = f"Every {sub} {tv} {_art(ob)} {ob}."
        exist = f"∀x. {sub}(x) → (∃y. {ob}(y) ∧ {tv}(x, y))"
        const = f"∀x. {sub}(x) → {tv}(x, {ob})"
        add(_emit(prose, 1, "transitive", exist, const))

    # 2 objects — ditransitive (double-object)
    tried = 0
    while sum(r["n_objects"] == 2 for r in out) < per_class and tried < per_class * 60:
        tried += 1
        sub, dv = rng.choice(SUBJ), rng.choice(DVERB)
        rc, th = rng.choice(RECIP), rng.choice(THEME)
        prose = f"Every {sub} {dv} {_art(rc)} {rc} {_art(th)} {th}."
        exist = (f"∀x. {sub}(x) → (∃y. {rc}(y) ∧ ∃z. {th}(z) ∧ {dv}(x, y, z))")
        const = f"∀x. {sub}(x) → {dv}(x, {rc}, {th})"
        add(_emit(prose, 2, "ditransitive", exist, const))

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Object-count reading probes (s248)")
    ap.add_argument("--per-class", type=int, default=45)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.per_class, args.seed)
    by_obj = Counter(r["n_objects"] for r in rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    META.write_text(json.dumps({
        "generated_utc": datetime.now(UTC).isoformat(),
        "n": len(rows), "per_class": args.per_class, "seed": args.seed,
        "by_n_objects": {str(k): v for k, v in sorted(by_obj.items())},
        "discriminator": "const C-count == n_objects; exist B-count scales {1,3,5}",
        "method": "prose identical; two candidate LFs (existential vs constant); "
                  "fired via to_kernel→saturate→fired_sequence; const_c==n_objects.",
    }, indent=2), encoding="utf-8")
    print(f"[gen] wrote {OUT}  ({len(rows)} probes)  "
          f"by_n_objects={dict(sorted(by_obj.items()))}")


if __name__ == "__main__":
    main()
