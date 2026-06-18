"""Corpus certify-audit — does data/compile-*.jsonl fit the kernel? (s240)

Runs every example's surface logical-form (FOL/λ) through the kernel pipeline and
reports a per-stage certify-rate + a failure/smell taxonomy. Grounds the reward
density for the spliced-reward design (knowledge/explore/spliced-reward-vsm-kernel.md).

PIPELINE (the "fit to kernel" transform — the standard CL encoding of FOL):

    surface str  → normalise/parse   : THIS module (recursive-descent over the
                                        surface grammar: λ ∀ ∃ . → ∧ ∨ ¬ , f(a,b))
    surface AST  → kernel Term        : lower predicates/connectives to applicative
                                        atoms; binders (λ/∀/∃) via BRACKET ABSTRACTION
                                        (lambda_compile.abstract) — quantifiers become
                                        higher-order atoms (forall/exists) over the
                                        abstracted predicate
    kernel Term  → typecheck          : lambda_ast.typecheck (S2, simply-typable?)
    kernel Term  → reduce             : lambda_ast.reduce (NF / DIVERGED / SIZE_EXCEEDED)

CERTIFIED = surface-parse ✓ ∧ lower ✓ ∧ typecheck ✓ ∧ reduce==NORMAL_FORM.
SMELLS (need changes even when they certify): vacuous binder (λx with x∉body),
mixed notation within a category (λ-wrapper vs bare connective/quantifier).

License: MIT.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from verbum.lambda_ast import (  # noqa: E402
    App,
    Atom,
    Status,
    Term,
    reduce,
    size,
    typecheck,
)
from verbum.lambda_compile import abstract  # noqa: E402

# --------------------------------------------------------------------------- #
# Surface grammar AST                                                          #
# --------------------------------------------------------------------------- #
CONNECTIVE = {"→": "implies", "∧": "and", "∨": "or"}


@dataclass
class SVar:
    name: str


@dataclass
class SApp:  # predicate application f(a1,...,an)  (n>=0)
    head: str
    args: list["SExpr"]


@dataclass
class SBin:  # A op B   (op ∈ → ∧ ∨)
    op: str
    lhs: "SExpr"
    rhs: "SExpr"


@dataclass
class SNot:
    body: "SExpr"


@dataclass
class SBind:  # λ/∀/∃ x . body
    kind: str  # 'λ' | '∀' | '∃'
    var: str
    body: "SExpr"


SExpr = SVar | SApp | SBin | SNot | SBind


class SurfaceError(Exception):
    pass


# --------------------------------------------------------------------------- #
# Tokeniser + recursive-descent parser for the surface logical-form           #
# --------------------------------------------------------------------------- #
_PUNCT = {"(", ")", ",", ".", "λ", "∀", "∃", "→", "∧", "∨", "¬"}
_BINDER = {"λ", "∀", "∃", "ι"}  # ι = definite description ("the")


def _tok(s: str) -> list[str]:
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c in _PUNCT or c == "ι":
            toks.append(c)
            i += 1
        elif c.isalnum() or c == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            toks.append(s[i:j])
            i = j
        else:
            raise SurfaceError(f"bad char {c!r}")
    return toks


class _P:
    def __init__(self, toks: list[str]):
        self.t = toks
        self.i = 0

    def peek(self) -> str | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, expect: str | None = None) -> str:
        if self.i >= len(self.t):
            raise SurfaceError("unexpected end")
        tok = self.t[self.i]
        if expect is not None and tok != expect:
            raise SurfaceError(f"expected {expect!r} got {tok!r}")
        self.i += 1
        return tok

    # expr := implication (right-assoc →); then ∨ ; then ∧ ; then unary
    def expr(self) -> SExpr:
        return self.imp()

    def imp(self) -> SExpr:
        lhs = self.disj()
        if self.peek() == "→":
            self.eat("→")
            return SBin("→", lhs, self.imp())
        return lhs

    def disj(self) -> SExpr:
        lhs = self.conj()
        while self.peek() == "∨":
            self.eat("∨")
            lhs = SBin("∨", lhs, self.conj())
        return lhs

    def conj(self) -> SExpr:
        lhs = self.unary()
        while self.peek() == "∧":
            self.eat("∧")
            lhs = SBin("∧", lhs, self.unary())
        return lhs

    def unary(self) -> SExpr:
        tok = self.peek()
        if tok == "¬":
            self.eat("¬")
            return SNot(self.unary())
        if tok in _BINDER:
            self.eat()
            var = self.eat()
            self.eat(".")
            return SBind(tok, var, self.expr())
        return self.app()

    def app(self) -> SExpr:
        tok = self.peek()
        if tok == "(":
            self.eat("(")
            inner = self.expr()
            self.eat(")")
            return inner
        if tok is None or tok in _PUNCT:
            raise SurfaceError(f"unexpected {tok!r}")
        head = self.eat()
        if self.peek() == "(":
            self.eat("(")
            args: list[SExpr] = []
            if self.peek() != ")":
                args.append(self.expr())
                while self.peek() == ",":
                    self.eat(",")
                    args.append(self.expr())
            self.eat(")")
            return SApp(head, args)
        return SVar(head)


def parse_surface(s: str) -> SExpr:
    p = _P(_tok(s))
    e = p.expr()
    if p.peek() is not None:
        raise SurfaceError(f"trailing {p.peek()!r}")
    return e


# --------------------------------------------------------------------------- #
# Lower surface AST → kernel Term  (binders via bracket abstraction)          #
# --------------------------------------------------------------------------- #
def _occurs_s(var: str, e: SExpr) -> bool:
    if isinstance(e, SVar):
        return e.name == var
    if isinstance(e, SApp):
        return e.head == var or any(_occurs_s(var, a) for a in e.args)
    if isinstance(e, SBin):
        return _occurs_s(var, e.lhs) or _occurs_s(var, e.rhs)
    if isinstance(e, SNot):
        return _occurs_s(var, e.body)
    if isinstance(e, SBind):
        return e.var != var and _occurs_s(var, e.body)
    return False


def _appchain(head: Term, args: list[Term]) -> Term:
    t = head
    for a in args:
        t = App(t, a)
    return t


def lower(e: SExpr, vacuous: list[str]) -> Term:
    """Surface AST → kernel Term. Appends a tag to `vacuous` per vacuous binder."""
    if isinstance(e, SVar):
        return Atom(e.name)
    if isinstance(e, SApp):
        return _appchain(Atom(e.head), [lower(a, vacuous) for a in e.args])
    if isinstance(e, SBin):
        return _appchain(Atom(CONNECTIVE[e.op]), [lower(e.lhs, vacuous), lower(e.rhs, vacuous)])
    if isinstance(e, SNot):
        return App(Atom("not"), lower(e.body, vacuous))
    if isinstance(e, SBind):
        if not _occurs_s(e.var, e.body):
            vacuous.append(e.kind)
        body = lower(e.body, vacuous)
        abstracted = abstract(e.var, body)  # remove the bound var (point-free)
        if e.kind == "λ":
            return abstracted
        head = {"∀": "forall", "∃": "exists", "ι": "iota"}[e.kind]
        return App(Atom(head), abstracted)
    raise SurfaceError(f"cannot lower {e!r}")


# --------------------------------------------------------------------------- #
# Per-example audit                                                           #
# --------------------------------------------------------------------------- #
def top_style(e: SExpr) -> str:
    """Classify the top-level shape (for the mixed-notation smell)."""
    if isinstance(e, SBind):
        return f"bind:{e.kind}"
    if isinstance(e, SBin):
        return f"bin:{e.op}"
    if isinstance(e, SNot):
        return "not"
    if isinstance(e, SApp):
        return "app"
    return "var"


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
    except (SurfaceError, Exception) as ex:  # noqa: BLE001
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
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    # ---- printout ----
    print(f"=== corpus certify-audit (n={n}) ===")
    print("\nSTAGE (terminal stage per example):")
    for k, v in stage.most_common():
        print(f"  {k:24s} {v:4d}  {v/n:6.1%}")
    print(f"\nCERTIFIED (parse∧lower∧typecheck∧NF): {certified}/{n} = {certified/n:.1%}")
    print(f"CLEAN-CERTIFIED (certified ∧ no smell): {clean_certified}/{n} = {clean_certified/n:.1%}")
    print(f"CLEAN-AFTER-STRIP (strip vacuous-λ wrapper): {clean_after_strip}/{n} = {clean_after_strip/n:.1%}")
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
            print(f"  [{r['stage']}] {r['output']}  -> {r.get('error') or r.get('type_error') or r.get('reduce_status')}")
            shown += 1
            if shown >= 12:
                break
    print(f"\nwrote {out_dir}/summary.json + rows.jsonl")


if __name__ == "__main__":
    main()
