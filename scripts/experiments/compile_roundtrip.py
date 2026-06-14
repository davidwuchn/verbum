#!/usr/bin/env python3
# register: functional (symbolic — the compile↔reduce inverse certification)
"""Compile round-trip certification — does abstraction invert reduction? (stage 2).

THE QUESTION (session 226). Stage 2 factors the compiler into prose→logical-form
(LEARNED) ∘ logical-form→term (bracket abstraction, EXACT) ∘ term→normal-form
(reduction, EXACT). This script certifies the two EXACT halves are genuine inverses
by generating diverse logical-form expressions, bracket-abstracting them to
combinator terms, reducing those terms back through the stage-1 kernel, and checking
the result equals the original:

    reduce( compile([x..], e) applied to [x..] )  ≡  e

It also measures TERM-SIZE GROWTH (term_size / expr_size) — the duplication blow-up
(S/W) that is the representational LIMIT of the constructed kernel (the boundary the
s225 diverse data must map; compiler-as-loss.md §s226 honest limits).

Usage:
  uv run python scripts/experiments/compile_roundtrip.py --n 5000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.lambda_ast import App, Atom, Term, parse, pretty
from verbum.lambda_compile import compile_record

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "compile-roundtrip"

VARS = ["x", "y", "z"]
ATOMS = ["f", "g", "h", "a", "b"]


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def rand_expr(rng: random.Random, atoms: list[str], depth: int) -> Term:
    if depth <= 0 or rng.random() < 0.4:
        return Atom(rng.choice(atoms))
    return App(rand_expr(rng, atoms, depth - 1), rand_expr(rng, atoms, depth - 1))


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    s = sorted(xs)
    k = max(0, min(len(s) - 1, round(p * (len(s) - 1))))
    return s[k]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--sample", type=int, default=200, help="records to dump to jsonl")
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    records = []
    fails = []
    growth = []
    by_stratum: dict[str, dict[str, int]] = {}
    n_typed = 0
    for _ in range(args.n):
        nvars = rng.randint(1, 3)
        depth = rng.randint(1, args.max_depth)
        vs = VARS[:nvars]
        # ensure the abstraction variables actually appear sometimes
        atoms = ATOMS + vs
        e = rand_expr(rng, atoms, depth)
        rec = compile_record(vs, e)
        records.append(rec)
        key = f"v{nvars}_d{depth}"
        st = by_stratum.setdefault(key, {"n": 0, "ok": 0})
        st["n"] += 1
        st["ok"] += int(rec["roundtrip_ok"])
        if rec["roundtrip_ok"]:
            growth.append(rec["term_size"] / max(rec["expr_size"], 1))
        else:
            fails.append(rec)
        n_typed += int(rec["well_typed"])

    n_ok = sum(r["roundtrip_ok"] for r in records)
    summary = {
        "n": args.n,
        "seed": args.seed,
        "roundtrip_ok": n_ok,
        "roundtrip_rate": round(n_ok / args.n, 6),
        "well_typed_rate": round(n_typed / args.n, 6),
        "n_failures": len(fails),
        "term_size_growth": {
            "mean": round(sum(growth) / max(len(growth), 1), 3),
            "p50": round(percentile(growth, 0.5), 3),
            "p95": round(percentile(growth, 0.95), 3),
            "max": round(max(growth), 3) if growth else None,
        },
        "by_stratum": {
            k: {"n": v["n"], "ok": v["ok"],
                "rate": round(v["ok"] / v["n"], 4)}
            for k, v in sorted(by_stratum.items())
        },
        "failures_sample": [
            {"variables": f["variables"], "expr": f["expr"], "term": f["term"],
             "applied_normal_form": f["applied_normal_form"],
             "reduce_status": f["reduce_status"]}
            for f in fails[:10]
        ],
        "git_sha": git_sha(),
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    with (RESULTS_DIR / "sample.jsonl").open("w") as fh:
        for r in records[: args.sample]:
            fh.write(json.dumps(r) + "\n")

    print(f"=== compile round-trip certification (n={args.n}) ===", file=sys.stderr)
    print(f"  round-trip rate : {summary['roundtrip_rate']:.4f} "
          f"({n_ok}/{args.n})", file=sys.stderr)
    print(f"  well-typed rate : {summary['well_typed_rate']:.4f}", file=sys.stderr)
    g = summary["term_size_growth"]
    print(f"  term/expr size  : mean {g['mean']} p50 {g['p50']} "
          f"p95 {g['p95']} max {g['max']}  (S/W duplication = the limit)",
          file=sys.stderr)
    if fails:
        print(f"  !! {len(fails)} FAILURES, e.g.:", file=sys.stderr)
        for f in fails[:3]:
            print(f"     {f['variables']} {f['expr']} -> {f['term']} "
                  f"-> {f['applied_normal_form']} [{f['reduce_status']}]",
                  file=sys.stderr)
    else:
        print("  ✅ abstraction and reduction are EXACT INVERSES on all samples",
              file=sys.stderr)
    print(f"  wrote {RESULTS_DIR}/summary.json + sample.jsonl", file=sys.stderr)
    _ = parse, pretty  # keep imports available for interactive use


if __name__ == "__main__":
    main()
