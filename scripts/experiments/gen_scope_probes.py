#!/usr/bin/env python3
# register: data-generation (scope-forcing probes, s248 cont.3 causal test)
"""Scope-forcing probes — CAN the model do existential-B when syntax forces it? (s248)

WHY (s248 cont.2 → the clean causal follow-up). The reading-preference test showed the
model reads a plain indefinite object as a CONSTANT/argument (→ C), not an existential
(→ B): adding objects raised z(C), not z(B). Open question: is that because the model
CANNOT represent existential-B, or because the DEFAULT reading of "Every X verbs a Y" is
applicative? If we SYNTACTICALLY FORCE wide-scope existential, does z(B) then rise?

THE PAIRED CONTRAST (matched subj/verb/obj triples × 3 conditions):
    PLAIN  "Every cat fears a dog."              → S,B,C    (applicative, C:1)
    CLEFT  "There is a dog that every cat fears." → S,B,B,B  (∃ fronted, B:3 C:0)
    RELCL  "Every cat fears a dog that runs."     → S,B,B,B  (∃ object, B-heavy)
  • CLEFT fronts the existential (strong wide-scope forcing).
  • RELCL predicates on the object, forcing it to be a real (existential) entity.
Both make the GROUND TRUTH B-heavy with NO constant C — the opposite of PLAIN.

PREDICTION:
  • model CAN do existential-B → z(B) RISES (and z(C) FALLS) PLAIN → CLEFT/RELCL
    (the construction is discoverable, just not the default). Paired Wilcoxon.
  • model ALWAYS applicative → z(B)/z(C) flat across conditions (ignores scope marking).

Output: data/scope-probes.jsonl
    {input, condition, triple_id, fol, fired, b_count, c_count, s_count}

Usage:
    uv run python scripts/experiments/gen_scope_probes.py
    uv run python scripts/experiments/gen_scope_probes.py --n-triples 45 --seed 0

License: MIT. AGENTS.md S5 λ provenance (lambda_surface + lambda_ast).
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
OUT = _ROOT / "data" / "scope-probes.jsonl"
META = _ROOT / "data" / "scope-probes.meta.json"


def _fired(fol: str):
    try:
        k = to_kernel(fol)
        seq = fired_sequence(saturate(k, _Fresh()))
    except Exception:
        return None
    if not seq:
        return None
    c = Counter(seq)
    return seq, pretty(k), c.get("B", 0), c.get("C", 0), c.get("S", 0)


def _rec(input_text, condition, tid, fol):
    f = _fired(fol)
    if f is None:
        return None
    seq, k, b, c, s = f
    return {"input": input_text, "condition": condition, "triple_id": tid,
            "fol": fol, "kernel": k, "fired": seq,
            "b_count": b, "c_count": c, "s_count": s}


def generate(n_triples: int, seed: int) -> list[dict]:
    import random

    rng = random.Random(seed)
    out: list[dict] = []
    used: set[tuple] = set()
    tid = 0
    tried = 0
    while tid < n_triples and tried < n_triples * 60:
        tried += 1
        sub, tv, ob = rng.choice(SUBJ), rng.choice(TVERB), rng.choice(OBJ)
        iv = rng.choice(IVERB)
        key = (sub, tv, ob, iv)
        if key in used:
            continue
        plain = _rec(f"Every {sub} {tv} {_art(ob)} {ob}.", "plain", tid,
                     f"∀x. {sub}(x) → {tv}(x, {ob})")
        cleft = _rec(f"There is {_art(ob)} {ob} that every {sub} {tv}.", "cleft", tid,
                     f"∃y. {ob}(y) ∧ (∀x. {sub}(x) → {tv}(x, y))")
        relcl = _rec(f"Every {sub} {tv} {_art(ob)} {ob} that {iv}.", "relcl", tid,
                     f"∀x. {sub}(x) → (∃y. ({ob}(y) ∧ {iv}(y)) ∧ {tv}(x, y))")
        # contract: plain must carry a C (applicative); cleft/relcl must be B-dominant.
        if (plain and cleft and relcl and plain["c_count"] >= 1
                and cleft["b_count"] > cleft["s_count"]
                and relcl["b_count"] > relcl["s_count"]):
            used.add(key)
            out.extend([plain, cleft, relcl])
            tid += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Scope-forcing probes (s248)")
    ap.add_argument("--n-triples", type=int, default=45)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rows = generate(args.n_triples, args.seed)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by_cond = Counter(r["condition"] for r in rows)
    META.write_text(json.dumps({
        "generated_utc": datetime.now(UTC).isoformat(),
        "n": len(rows), "n_triples": len(rows) // 3, "seed": args.seed,
        "by_condition": dict(by_cond),
        "contract": "plain c_count>=1 (applicative); cleft/relcl b_count>s_count "
                    "(existential forced, B-heavy no C).",
    }, indent=2), encoding="utf-8")
    print(f"[gen] wrote {OUT}  ({len(rows)} rows, {len(rows)//3} triples)  "
          f"by_condition={dict(by_cond)}")


if __name__ == "__main__":
    main()
