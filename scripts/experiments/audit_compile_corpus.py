"""Corpus certify-audit — does data/compile-*.jsonl fit the kernel? (s240)

Runs every example's surface logical-form (FOL/λ) through the kernel pipeline and
reports a per-stage certify-rate + a failure/smell taxonomy. Grounds the reward
density for the spliced-reward design (knowledge/explore/spliced-reward-vsm-kernel.md).

PIPELINE (the "fit to kernel" transform — the standard CL encoding of FOL).
The surface parse + lower now live in `verbum.lambda_surface` (shared with
the verifiable reward); this script just drives them over the corpus + tallies:

    surface str  → surface AST        : verbum.lambda_surface.parse_surface
    surface AST  → kernel Term         : verbum.lambda_surface.lower (binders via
                                        BRACKET ABSTRACTION; quantifiers → higher-
                                        order atoms forall/exists/iota)
    kernel Term  → typecheck           : lambda_ast.typecheck (S2, simply-typable?)
    kernel Term  → reduce              : lambda_ast.reduce (NF/DIVERGED/SIZE_EXCEEDED)

CERTIFIED = surface-parse ✓ ∧ lower ✓ ∧ typecheck ✓ ∧ reduce==NORMAL_FORM.
SMELLS (need changes even when they certify): vacuous binder (λx with x∉body),
mixed notation within a category (λ-wrapper vs bare connective/quantifier).

License: MIT.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from verbum.lambda_ast import (  # noqa: E402
    Status,
    reduce,
    size,
    typecheck,
)
from verbum.lambda_surface import (  # noqa: E402
    SurfaceError,
    lower,
    parse_surface,
    top_style,
)


# --------------------------------------------------------------------------- #
# Per-example audit                                                           #
# --------------------------------------------------------------------------- #
def audit_one(out: str) -> dict:
    rec: dict = {"output": out, "stage": None, "smells": []}
    try:
        sast = parse_surface(out)
    except SurfaceError as ex:
        rec["stage"] = "surface_parse_error"
        rec["error"] = str(ex)
        return rec
    rec["top_style"] = top_style(sast)
    vac: list[str] = []
    try:
        term = lower(sast, vac)
    except (SurfaceError, Exception) as ex:
        rec["stage"] = "lower_error"
        rec["error"] = f"{type(ex).__name__}: {ex}"
        return rec
    if vac:
        rec["smells"].append(f"vacuous_binder:{'+'.join(vac)}")
    rec["term_size"] = size(term)
    tc = typecheck(term)
    rec["well_typed"] = tc.ok
    if not tc.ok:
        rec["smells"].append("not_simply_typable")
        rec["type_error"] = tc.error
    red = reduce(term)
    rec["reduce_status"] = red.status.value
    rec["steps"] = red.steps
    rec["stage"] = (
        "certified"
        if (tc.ok and red.status is Status.NORMAL_FORM)
        else "kernel_reject"
    )
    if red.status is Status.SIZE_EXCEEDED:
        rec["smells"].append("blow_up_over_budget")
    if red.status is Status.DIVERGED:
        rec["smells"].append("diverged")
    return rec


def main() -> None:
    files = ["compile-train.jsonl", "compile-test.jsonl", "compile-eval.jsonl"]
    rows: list[dict] = []
    for f in files:
        p = ROOT / "data" / f
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            r = audit_one(d["output"])
            r["category"] = d.get("category")
            r["split"] = f
            rows.append(r)

    n = len(rows)
    stage = Counter(r["stage"] for r in rows)
    smell = Counter(s for r in rows for s in r["smells"])
    by_cat_style = defaultdict(set)
    for r in rows:
        if "top_style" in r:
            by_cat_style[r["category"]].add(r["top_style"])
    mixed_cats = {c: sorted(v) for c, v in by_cat_style.items() if len(v) > 1}
    certified = stage["certified"]
    clean_certified = sum(
        1 for r in rows if r["stage"] == "certified" and not r["smells"]
    )
    # Actionable projection: a vacuous TOP-LEVEL λ wrapper is a pure generation
    # artifact (strip it → the inner closed proposition). How many examples become
    # clean once the (only) vacuous-binder smell is stripped?
    vacuous_lambda_top = sum(
        1 for r in rows
        if r.get("top_style") == "bind:λ"
        and any(s.startswith("vacuous_binder") for s in r["smells"])
    )
    clean_after_strip = sum(
        1 for r in rows
        if r["stage"] == "certified"
        and all(s.startswith("vacuous_binder") for s in r["smells"])
    )

    out_dir = ROOT / "results" / "compile-corpus-audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rows.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    )
    summary = {
        "n": n,
        "stage_counts": dict(stage),
        "certified": certified,
        "certified_rate": round(certified / n, 4),
        "clean_certified": clean_certified,
        "clean_certified_rate": round(clean_certified / n, 4),
        "smell_counts": dict(smell),
        "mixed_notation_categories": mixed_cats,
        "well_typed": sum(1 for r in rows if r.get("well_typed")),
        "reduce_status": dict(Counter(r.get("reduce_status") for r in rows)),
        "vacuous_lambda_top": vacuous_lambda_top,
        "clean_after_strip_vacuous": clean_after_strip,
        "clean_after_strip_rate": round(clean_after_strip / n, 4),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    # ---- printout ----
    print(f"=== corpus certify-audit (n={n}) ===")
    print("\nSTAGE (terminal stage per example):")
    for k, v in stage.most_common():
        print(f"  {k:24s} {v:4d}  {v/n:6.1%}")
    print(f"\nCERTIFIED (parse∧lower∧typecheck∧NF): "
          f"{certified}/{n} = {certified/n:.1%}")
    print(f"CLEAN-CERTIFIED (certified ∧ no smell): "
          f"{clean_certified}/{n} = {clean_certified/n:.1%}")
    print(f"CLEAN-AFTER-STRIP (strip vacuous-λ wrapper): "
          f"{clean_after_strip}/{n} = {clean_after_strip/n:.1%}")
    print(f"  (vacuous top-level λ wrappers: {vacuous_lambda_top})")
    print("\nSMELLS (need changes even if certified):")
    for k, v in smell.most_common():
        print(f"  {k:28s} {v:4d}  {v/n:6.1%}")
    print("\nMIXED-NOTATION categories (>1 top-level style):")
    for c, styles in sorted(mixed_cats.items()):
        print(f"  {c:16s} {styles}")
    print("\nREDUCE status:", dict(Counter(r.get("reduce_status") for r in rows)))
    print("\nSample failures / rejects:")
    shown = 0
    for r in rows:
        if r["stage"] in ("surface_parse_error", "lower_error", "kernel_reject"):
            why = r.get("error") or r.get("type_error") or r.get("reduce_status")
            print(f"  [{r['stage']}] {r['output']}  -> {why}")
            shown += 1
            if shown >= 12:
                break
    print(f"\nwrote {out_dir}/summary.json + rows.jsonl")


if __name__ == "__main__":
    main()
