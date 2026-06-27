#!/usr/bin/env python3
"""Generate the oracle-certified combinator-reduction probe set.

Builds `probes/combinator-reduction.json` (gated probe_format schema, AGENTS.md
S2 λ probe_format) for the REPL-machine eval (s255). Each probe is a pure
combinator term whose ground truth is computed AND certified by the verbum
lambda_ast oracle (normal-order reducer over the K I B C S W Y D M basis).

Two strata, both certified by the SAME oracle:
  depth1   — reuse the oracle-parseable combinator probes already in
             verbum.probes.library (the canonical measurement substrate),
             capped per combinator. Single-redex / already-NF anchors.
  multi    — seeded random combinator terms (saturated heads + atom/subterm
             args), filtered to status=NORMAL_FORM, 2..MAX_STEPS reductions,
             bounded NF size. Stratified by step count.

ground_truth = oracle normal form. metadata carries {combinator, source,
n_steps, fired (certified opcode sequence), status, whnf_step}. The harness
re-derives all gold from the term at grade time, so the JSON is a convenience
record, not a second source of truth (λ assert: oracle ≡ truth).

License: MIT.
"""

from __future__ import annotations

import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from verbum import lambda_ast as la  # noqa: E402
from verbum.probes.library import all_probes  # noqa: E402

OUT = _ROOT / "probes" / "combinator-reduction.json"

# Generation parameters
SEED = 255
MAX_STEPS_KEEP = 8          # keep terms reducing in 2..8 steps
MAX_NF_SIZE = 18            # bound the normal-form size (readability)
MAX_TERM_SIZE = 14          # bound the source-term size
PER_BUCKET = 12             # target probes per step-count bucket (2..8)
NF_CAP = 3                  # cap already-NF library probes per combinator
ATOMS = ["a", "b", "c", "d", "e", "f", "g", "h"]
# Linear/affine basis only for multi-step generation (avoid Y/W/M explosions).
GEN_COMBS = ["K", "I", "B", "C", "S", "W"]
# Single-redex basis (one β-step from saturated atom application). D, M added.
SINGLE_COMBS = ["I", "K", "B", "C", "S", "W", "D", "M"]


def _gold(term: str) -> dict | None:
    """Oracle record for a term, or None if it doesn't cleanly reach NF."""
    try:
        t = la.parse(term)
    except ValueError:
        return None
    r = la.reduce(t)
    if r.status is not la.Status.NORMAL_FORM:
        return None
    return {
        "normal_form": la.pretty(r.normal_form),
        "n_steps": r.steps,
        "fired": la.fired_sequence(t),
        "status": r.status.value,
        "whnf_step": r.whnf_step,
        "term_size": la.size(t),
        "nf_size": la.size(r.normal_form),
    }


def _rand_term(rng: random.Random, depth: int) -> str:
    """Build a random saturated combinator application."""
    comb = rng.choice(GEN_COMBS)
    arity, _ = la.REDUCTIONS[comb]
    parts = [comb]
    n_args = arity + rng.choice([0, 0, 1])  # sometimes one extra arg
    for _ in range(n_args):
        if depth > 0 and rng.random() < 0.45:
            parts.append("(" + _rand_term(rng, depth - 1) + ")")
        else:
            parts.append(rng.choice(ATOMS))
    return " ".join(parts)


def gen_multi(rng: random.Random) -> list[dict]:
    """Seeded multi-step stratum, stratified by step count 2..MAX_STEPS_KEEP."""
    buckets: dict[int, list[dict]] = {n: [] for n in range(2, MAX_STEPS_KEEP + 1)}
    seen: set[str] = set()
    tries = 0
    target = PER_BUCKET * len(buckets)
    while sum(len(v) for v in buckets.values()) < target and tries < 200_000:
        tries += 1
        term = _rand_term(rng, depth=rng.choice([1, 2, 2, 3]))
        if term in seen:
            continue
        g = _gold(term)
        if g is None:
            continue
        n = g["n_steps"]
        if not (2 <= n <= MAX_STEPS_KEEP):
            continue
        if g["term_size"] > MAX_TERM_SIZE or g["nf_size"] > MAX_NF_SIZE:
            continue
        if len(buckets[n]) >= PER_BUCKET:
            continue
        seen.add(term)
        # dominant combinator = most-fired opcode
        fired = g["fired"]
        comb = max(set(fired), key=fired.count) if fired else None
        buckets[n].append({"term": term, "combinator": comb, "gold": g})
    out: list[dict] = []
    for n in sorted(buckets):
        out.extend(buckets[n])
    return out


def _is_pure_combinator(term: str) -> bool:
    """True iff every token is a combinator letter or paren (no NL atoms)."""
    try:
        toks = la._tokenize(term)
    except ValueError:
        return False
    body = [t for t in toks if t not in "()"]
    return bool(body) and all(t in la._COMBINATORS for t in body)


def gen_already_nf(rng: random.Random) -> list[dict]:
    """Already-NF PURE-combinator terms (under-saturated): the NF-recognition stratum.

    Tests the WHNF axis the model is weak on — the machine must say `NF | term`,
    not invent a reduction. Reuses any pure-combinator NF probes from the library,
    then supplements with seed-generated under-saturated terms."""
    out: list[dict] = []
    seen: set[str] = set()

    def add(term: str, source: str, lib: dict | None = None) -> None:
        if term in seen:
            return
        g = _gold(term)
        if g is None or g["n_steps"] != 0 or g["term_size"] < 2 or g["term_size"] > 8:
            return
        seen.add(term)
        rec = {"term": term, "combinator": None, "gold": g, "source": source}
        if lib:
            rec.update(lib)
        out.append(rec)

    # reuse: library pure-combinator terms that are already NF
    for p in all_probes():
        t = p.prompt.strip()
        if _is_pure_combinator(t):
            add(t, "library", {"lib_source": p.source, "lib_id": p.id})

    # supplement: seed-generated under-saturated combinator terms (arity-1 args)
    target = 18
    tries = 0
    while len(out) < target and tries < 5000:
        tries += 1
        comb = rng.choice(SINGLE_COMBS)
        arity, _ = la.REDUCTIONS[comb]
        n_args = rng.randint(0, max(0, arity - 1))  # strictly under-saturated
        args = [rng.choice(SINGLE_COMBS) for _ in range(n_args)]
        add(" ".join([comb, *args]), "generated")
    return out


def gen_single(rng: random.Random) -> list[dict]:
    """Canonical single-redex terms: saturated combinator on atom/inert args, 1 step."""
    out: list[dict] = []
    seen: set[str] = set()
    for comb in SINGLE_COMBS:
        arity, _ = la.REDUCTIONS[comb]
        variants: list[str] = []
        # plain atom args
        variants.append(" ".join([comb, *ATOMS[:arity]]))
        variants.append(" ".join([comb, *ATOMS[1:arity + 1]]))
        # one variant with an inert combinator argument (saturated head still fires)
        if arity >= 2:
            args = [*ATOMS[:arity]]
            args[arity - 1] = "I"
            variants.append(" ".join([comb, *args]))
        # one variant with a parenthesized inert subterm in arg position
        if arity >= 1:
            args = [*ATOMS[:arity]]
            args[arity - 1] = "(K p)"
            variants.append(" ".join([comb, *args]))
        for term in variants:
            if term in seen:
                continue
            g = _gold(term)
            if g is None or g["n_steps"] != 1:
                continue
            if g["nf_size"] > MAX_NF_SIZE:
                continue
            seen.add(term)
            out.append({"term": term, "combinator": comb, "gold": g})
    return out


def main() -> None:
    rng = random.Random(SEED)
    nf = gen_already_nf(rng)
    single = gen_single(rng)
    multi = gen_multi(rng)

    probes = []
    for i, e in enumerate(nf):
        g = e["gold"]
        probes.append({
            "id": f"cr-nf-{i:03d}",
            "category": "already_nf",
            "prompt": e["term"],
            "ground_truth": g["normal_form"],
            "metadata": {
                "combinator": e["combinator"], "source": e["source"],
                "lib_source": e.get("lib_source"), "lib_id": e.get("lib_id"),
                "n_steps": g["n_steps"], "fired": g["fired"],
                "status": g["status"], "whnf_step": g["whnf_step"],
            },
        })
    for i, e in enumerate(single):
        g = e["gold"]
        probes.append({
            "id": f"cr-d1-{i:03d}",
            "category": "depth1",
            "prompt": e["term"],
            "ground_truth": g["normal_form"],
            "metadata": {
                "combinator": e["combinator"], "source": "generated",
                "n_steps": g["n_steps"], "fired": g["fired"],
                "status": g["status"], "whnf_step": g["whnf_step"],
            },
        })
    for i, e in enumerate(multi):
        g = e["gold"]
        probes.append({
            "id": f"cr-mx-{i:03d}",
            "category": f"multi{g['n_steps']}",
            "prompt": e["term"],
            "ground_truth": g["normal_form"],
            "metadata": {
                "combinator": e["combinator"], "source": "generated",
                "n_steps": g["n_steps"], "fired": g["fired"],
                "status": g["status"], "whnf_step": g["whnf_step"],
            },
        })

    doc = {
        "id": "combinator-reduction",
        "version": 1,
        "description": (
            "Oracle-certified combinator-reduction probes for the REPL-machine "
            "eval (s255). Pure combinator terms over K I B C S W Y D M; ground "
            "truth = verbum.lambda_ast normal-order reducer. depth1 stratum reused "
            "from verbum.probes.library; multi stratum seed-generated and filtered "
            "to 2..8 reduction steps. Gold re-derivable from each term via the oracle."
        ),
        "created": datetime.now(UTC).isoformat(),
        "author": "verbum",
        "oracle": "verbum.lambda_ast.reduce (normal-order, MAX_STEPS=512)",
        "seed": SEED,
        "probes": probes,
    }
    OUT.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # report
    from collections import Counter
    cats = Counter(p["category"] for p in probes)
    steps = Counter(p["metadata"]["n_steps"] for p in probes)
    print(f"wrote {OUT.relative_to(_ROOT)}  ({len(probes)} probes)")
    print(f"  already_nf (library): {len(nf)}  |  depth1: {len(single)}  "
          f"|  multi (generated): {len(multi)}")
    print(f"  by category: {dict(sorted(cats.items()))}")
    print(f"  by n_steps:  {dict(sorted(steps.items()))}")


if __name__ == "__main__":
    main()
