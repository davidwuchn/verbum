"""Canonicalise data/compile-*.jsonl through the kernel (s240).

The audit (audit_compile_corpus.py) found the corpus is 100% kernel-expressible
but only 19.9% CLEAN: 80% carry a vacuous `λx.` wrapper (a grammar-convention
artifact — `lambda_montague.gbnf` documents `λx. runs(dog)` as "simple
predication"), plus per-category notation drift (`if(A,B)` vs `→`, `not(A)` vs `¬`).

This module applies the MECHANICAL, kernel-safe canonicalisation:

  1. STRIP vacuous λ binders        λx. cries(bird)        → cries(bird)
     (a SEMANTIC CORRECTION, not a refactor: a declarative is a proposition,
      type t, not a constant function ⟨e,t⟩ = K(prop). The stripped form is the
      *intended* meaning. Non-vacuous binders, incl. inner λy in relative
      clauses, are KEPT.)
  2. NORMALISE notation             if(A, B) → A → B  ;  not(A) → ¬A
  3. RE-RENDER one canonical surface form (uniform ¬ → ∧ ∨ binders, conservative
     parens so it round-trips)
  4. RE-CERTIFY through the kernel  (parse → lower → typecheck → reduce==NF)

Emits data/compile-{train,test,eval}.canonical.jsonl. Originals are NOT mutated
(git history + reproducibility). Going forward the kernel — not just the GBNF —
should gate generation (compiler-as-loss.md §s225/s226).

License: MIT.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_compile_corpus import (  # noqa: E402
    SApp,
    SBin,
    SBind,
    SExpr,
    SNot,
    SVar,
    _occurs_s,
    lower,
    parse_surface,
)
from verbum.lambda_ast import Status, pretty, reduce, typecheck  # noqa: E402


# --------------------------------------------------------------------------- #
# Canonicalising transform                                                    #
# --------------------------------------------------------------------------- #
def canonicalize(e: SExpr, log: list[str]) -> SExpr:
    """Mechanical, kernel-safe canonicalisation. Appends transform tags to log."""
    if isinstance(e, SVar):
        return e
    if isinstance(e, SApp):
        # notation: if(A, B) → A → B ; not(A) → ¬A
        if e.head == "if" and len(e.args) == 2:
            log.append("if→implies")
            return SBin("→", canonicalize(e.args[0], log), canonicalize(e.args[1], log))
        if e.head == "not" and len(e.args) == 1:
            log.append("not→¬")
            return SNot(canonicalize(e.args[0], log))
        return SApp(e.head, [canonicalize(a, log) for a in e.args])
    if isinstance(e, SBin):
        return SBin(e.op, canonicalize(e.lhs, log), canonicalize(e.rhs, log))
    if isinstance(e, SNot):
        return SNot(canonicalize(e.body, log))
    if isinstance(e, SBind):
        # strip a VACUOUS λ binder (the variable never occurs in the body)
        if e.kind == "λ" and not _occurs_s(e.var, e.body):
            log.append("strip-vacuous-λ")
            return canonicalize(e.body, log)
        # vacuous quantifier/iota → flag, keep (malformed but rare; don't silently rewrite)
        if e.kind in ("∀", "∃", "ι") and not _occurs_s(e.var, e.body):
            log.append(f"flag:vacuous-{e.kind}")
        return SBind(e.kind, e.var, canonicalize(e.body, log))
    raise TypeError(f"canonicalize: {e!r}")


# --------------------------------------------------------------------------- #
# Renderer — one canonical surface form, conservative parens (round-trips)     #
# --------------------------------------------------------------------------- #
def _operand(e: SExpr) -> str:
    """Render as a connective/not operand: parenthesise compound forms."""
    if isinstance(e, (SBin, SBind)):
        return f"({render(e)})"
    return render(e)


def render(e: SExpr) -> str:
    if isinstance(e, SVar):
        return e.name
    if isinstance(e, SApp):
        return f"{e.head}({', '.join(render(a) for a in e.args)})"
    if isinstance(e, SNot):
        return f"¬{_operand(e.body)}"
    if isinstance(e, SBin):
        return f"{_operand(e.lhs)} {e.op} {_operand(e.rhs)}"
    if isinstance(e, SBind):
        return f"{e.kind}{e.var}. {render(e.body)}"
    raise TypeError(f"render: {e!r}")


# --------------------------------------------------------------------------- #
# Per-record canonicalisation + re-certification                              #
# --------------------------------------------------------------------------- #
def certify(surface: str) -> tuple[bool, str | None, str | None]:
    """(ok, kernel_term_pretty, normal_form_pretty) — kernel verification."""
    try:
        sast = parse_surface(surface)
        term = lower(sast, [])
    except Exception as ex:  # noqa: BLE001
        return False, None, f"parse/lower: {ex}"
    tc = typecheck(term)
    red = reduce(term)
    ok = tc.ok and red.status is Status.NORMAL_FORM
    return ok, pretty(term), pretty(red.normal_form) if ok else red.status.value


def canon_record(d: dict) -> dict:
    orig = d["output"]
    log: list[str] = []
    sast = parse_surface(orig)
    canon = canonicalize(sast, log)
    out = render(canon)
    ok, term, nf = certify(out)
    rec = dict(d)
    rec["output"] = out
    rec["output_original"] = orig
    rec["transforms"] = log
    rec["changed"] = out != orig
    rec["kernel_term"] = term
    rec["normal_form"] = nf
    rec["recertified"] = ok
    return rec


def main() -> None:
    files = ["compile-train.jsonl", "compile-test.jsonl", "compile-eval.jsonl"]
    transforms = Counter()
    changed = 0
    failed: list[tuple[str, str]] = []
    flags: list[tuple[str, str]] = []
    total = 0

    for f in files:
        src = ROOT / "data" / f
        rows = [json.loads(line) for line in src.read_text().splitlines() if line.strip()]
        out_rows = []
        for d in rows:
            r = canon_record(d)
            out_rows.append(r)
            total += 1
            for t in r["transforms"]:
                transforms[t] += 1
                if t.startswith("flag:"):
                    flags.append((r["output_original"], t))
            if r["changed"]:
                changed += 1
            if not r["recertified"]:
                failed.append((r["output"], r["normal_form"] or "?"))
        dst = ROOT / "data" / f.replace(".jsonl", ".canonical.jsonl")
        dst.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + "\n"
        )

    print(f"=== canonicalisation (n={total}) ===")
    print(f"changed:      {changed}/{total} = {changed/total:.1%}")
    print(f"re-certified: {total - len(failed)}/{total} = {(total-len(failed))/total:.1%}")
    print("\nTRANSFORMS:")
    for k, v in transforms.most_common():
        print(f"  {k:24s} {v:4d}")
    if flags:
        print(f"\nFLAGGED (kept, not rewritten): {len(flags)}")
        for o, t in flags[:10]:
            print(f"  [{t}] {o}")
    if failed:
        print(f"\n★ RE-CERTIFY FAILURES: {len(failed)}")
        for o, why in failed[:10]:
            print(f"  {o}  -> {why}")
    else:
        print("\n✓ every canonical output re-certifies through the kernel")
    print("\nSAMPLES (before → after):")
    shown = 0
    for line in (ROOT / "data" / "compile-train.canonical.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["changed"]:
            print(f"  {r['output_original']:42s} → {r['output']}")
            shown += 1
            if shown >= 10:
                break
    print("\nwrote data/compile-{train,test,eval}.canonical.jsonl")


if __name__ == "__main__":
    main()
