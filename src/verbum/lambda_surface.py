"""Lambda surface — parse + lower surface logical-form (FOL/λ) → kernel Term.

THE ROLE (session 240/241). The structured corpus (`data/compile-*.jsonl`) carries
outputs in a *surface* logical-form notation (λ ∀ ∃ . → ∧ ∨ ¬, and predicate
application `f(a,b)`). The kernel (`lambda_ast`) reads only *combinator* terms
(`Comb {B,C,K,I,S,W,D,Y,M}`, `Atom`, `App`). This module bridges the two — the
"fit to kernel" front-end:

    surface str  → surface AST   : `parse_surface` (recursive-descent over the surface
                                    grammar)
    surface AST  → kernel Term   : `lower` — connectives/predicates become applicative
                                    atoms; binders (λ/∀/∃/ι) via BRACKET ABSTRACTION
                                    (`lambda_compile.abstract`); quantifiers become
                                    higher-order atoms (forall/exists/iota) over the
                                    abstracted predicate.

    to_kernel(s) = lower(parse_surface(s))   — the convenience round-trip.

This is the EXACT, constructed half of the compile path (the inverse of reduction,
Turner 1979). It is shared by the corpus certify-audit
(`scripts/experiments/audit_compile_corpus.py`) and the verifiable-reward module
(`verbum.reward`): grading a model's surface-FOL output means lowering it here, then
reducing in the kernel, then comparing normal forms. Single source of truth.

License: MIT. AGENTS.md S5 λ provenance (written from theory + this project's audit,
not nucleus).
"""

from __future__ import annotations

from dataclasses import dataclass

from verbum.lambda_ast import App, Atom, Term
from verbum.lambda_compile import abstract

__all__ = [
    "CONNECTIVE",
    "SApp",
    "SBin",
    "SBind",
    "SExpr",
    "SNot",
    "SVar",
    "SurfaceError",
    "lower",
    "parse_surface",
    "to_kernel",
    "top_style",
]

CONNECTIVE = {"→": "implies", "∧": "and", "∨": "or"}


# --------------------------------------------------------------------------- #
# Surface grammar AST                                                          #
# --------------------------------------------------------------------------- #
@dataclass
class SVar:
    name: str


@dataclass
class SApp:  # predicate application f(a1,...,an)  (n>=0)
    head: str
    args: list[SExpr]


@dataclass
class SBin:  # A op B   (op ∈ → ∧ ∨)
    op: str
    lhs: SExpr
    rhs: SExpr


@dataclass
class SNot:
    body: SExpr


@dataclass
class SBind:  # λ/∀/∃/ι x . body
    kind: str  # 'λ' | '∀' | '∃' | 'ι'
    var: str
    body: SExpr


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


def lower(e: SExpr, vacuous: list[str] | None = None) -> Term:
    """Surface AST → kernel Term. Appends a tag to `vacuous` per vacuous binder.

    `vacuous` is an optional out-param sink: when provided, every binder whose bound
    variable never appears in its body appends its kind (the corpus audit's
    vacuous-binder smell). Pass None (default) to ignore the diagnostic.
    """
    if vacuous is None:
        vacuous = []
    if isinstance(e, SVar):
        return Atom(e.name)
    if isinstance(e, SApp):
        return _appchain(Atom(e.head), [lower(a, vacuous) for a in e.args])
    if isinstance(e, SBin):
        lhs, rhs = lower(e.lhs, vacuous), lower(e.rhs, vacuous)
        return _appchain(Atom(CONNECTIVE[e.op]), [lhs, rhs])
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


def to_kernel(s: str) -> Term:
    """Surface logical-form string → kernel Term (parse_surface ∘ lower).

    The convenience front-end used by the verifiable reward: lower a model's
    surface-FOL/λ output into the kernel's language so it can be reduced and
    compared by normal form. Raises SurfaceError on a bad parse/lower.
    """
    return lower(parse_surface(s))


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
