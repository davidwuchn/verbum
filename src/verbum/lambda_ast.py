r"""Lambda AST — the typed CCG combinator reducer (the compiler's S5/source).

THE ROLE (session 226, Michael: "what if `lambda_ast.py` is *in the kernel*?").
This module is the SPECIFICATION of the verbum compiler. It plays a dual role:

  1. DATA ORACLE  — reduce(term) → exact β-reduction TRACE (the reduction tree the
                    LLMs cannot expose; s221 "fakes it with depth"), to supervise the
                    learned compile front-end (compiler-as-loss.md §s226).
  2. KERNEL SOURCE — the same combinator rewrites are what the constructed kernel's
                    ternary plates COMPILE FROM (source ↔ compiled, not oracle ↔
                    approximation). Build progression: symbolic (here) → neurosymbolic
                    → compiled plates (vsm-outer-recurrence.md §s226).

DESIGN (Michael, s226: "inspectability is important"). Terms are CCG-style: every
node carries (or can synthesize) an explicit category, so the S2 type-check — the
type-directedness thesis (AGENTS.md S5 λ types) — is FIRST-CLASS and inspectable,
not implicit in geometry.

  Term     = Comb(name) | Atom(name) | App(fn, arg)              # applicative spine
  Category = CAtom(name) | CVar(id) | CSlash(res, dir, arg)     # CCG, dir = fwd or bwd

Combinator basis + reduction rules (the s221 substructural classes):
    selection   {K, I, C}   (affine/linear — no copy)
    composition {B, D, S}   (B,D linear; S duplicates)
    recursion   {Y, W}      (W duplicates; Y unfolds — needs the outer recurrence)
    M (mockingbird) x → x x : reducible but NOT simply typable (the type-limit demo)

  I x       → x
  K x y     → x
  C f x y   → f y x
  B f g x   → f (g x)
  S f g x   → f x (g x)
  W f x     → f x x
  D f g h x → f (g (h x))            (deep/fused compose)
  Y f       → f (Y f)               (diverges under a step budget = correct)
  M x       → x x                   (ill-typed: occurs-check failure)

The reducer is NORMAL-ORDER (leftmost-outermost). Halting ≡ normal form; the step /
size budget bounds non-termination (Y, Ω) → status DIVERGED, the correct behaviour of
a bounded interpreter (lambda-halt-continuation.md). Term growth past the size budget
is the representational LIMIT of the machinery (the boundary the s225 diverse data
must map; compiler-as-loss.md §s226 "honest limits").

License: MIT — written from this project's observation (lambda-machine.md), NOT copied
from nucleus (AGPL is a probe, never a source). AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

__all__ = [
    "App",
    "Atom",
    "CAtom",
    "CSlash",
    "CVar",
    "Cat",
    "Comb",
    "IllTyped",
    "Reduction",
    "Status",
    "Term",
    "TypeResult",
    "normal_form",
    "parse",
    "pretty",
    "reduce",
    "trace_record",
    "typecheck",
    "verify",
]

# Default budgets — bound non-termination and term-growth (the machinery's limits).
MAX_STEPS = 512
MAX_SIZE = 4096


# --------------------------------------------------------------------------- #
# Terms                                                                        #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Comb:
    """A primitive combinator, e.g. S K I B C W D Y M."""

    name: str


@dataclass(frozen=True, slots=True)
class Atom:
    """A free constant / variable (a leaf the combinators move, copy, or drop)."""

    name: str


@dataclass(frozen=True, slots=True)
class App:
    """Application — left-associative; the argument sits to the RIGHT (forward)."""

    fn: Term
    arg: Term


Term = Comb | Atom | App


def spine(t: Term) -> tuple[Term, list[Term]]:
    """Unwind an application chain into (head, [arg1, ..., argn])."""
    args: list[Term] = []
    while isinstance(t, App):
        args.append(t.arg)
        t = t.fn
    args.reverse()
    return t, args


def rebuild(head: Term, args: list[Term]) -> Term:
    t = head
    for a in args:
        t = App(t, a)
    return t


def size(t: Term) -> int:
    if isinstance(t, App):
        return 1 + size(t.fn) + size(t.arg)
    return 1


def pretty(t: Term) -> str:
    """Render a term; parenthesise applications that sit in argument position."""
    if isinstance(t, Comb | Atom):
        return t.name
    head, args = spine(t)
    parts = [pretty(head)]
    for a in args:
        parts.append(f"({pretty(a)})" if isinstance(a, App) else pretty(a))
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# Parser  (juxtaposition = left-assoc application; parens group)               #
# --------------------------------------------------------------------------- #
_COMBINATORS = frozenset("SKIBCWDYM")


def _tokenize(s: str) -> list[str]:
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()":
            toks.append(c)
            i += 1
        elif c.isalnum() or c == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            toks.append(s[i:j])
            i = j
        else:
            raise ValueError(f"lambda_ast.parse: bad char {c!r} in {s!r}")
    return toks


def parse(s: str) -> Term:
    """Parse a combinator term. Single uppercase letters S K I B C W D Y M are
    combinators; everything else is an Atom. Application is juxtaposition."""
    toks = _tokenize(s)
    pos = 0

    def atom() -> Term:
        nonlocal pos
        if pos >= len(toks):
            raise ValueError(f"lambda_ast.parse: unexpected end in {s!r}")
        tok = toks[pos]
        if tok == "(":
            pos += 1
            inner = application()
            if pos >= len(toks) or toks[pos] != ")":
                raise ValueError(f"lambda_ast.parse: unbalanced parens in {s!r}")
            pos += 1
            return inner
        if tok == ")":
            raise ValueError(f"lambda_ast.parse: unexpected ')' in {s!r}")
        pos += 1
        if len(tok) == 1 and tok in _COMBINATORS:
            return Comb(tok)
        return Atom(tok)

    def application() -> Term:
        nonlocal pos
        t = atom()
        while pos < len(toks) and toks[pos] not in ")":
            t = App(t, atom())
        return t

    term = application()
    if pos != len(toks):
        raise ValueError(f"lambda_ast.parse: trailing tokens in {s!r}")
    return term


# --------------------------------------------------------------------------- #
# Reduction                                                                    #
# --------------------------------------------------------------------------- #
def _r_I(a):
    return a[0]


def _r_K(a):
    return a[0]


def _r_M(a):
    return App(a[0], a[0])


def _r_W(a):
    return App(App(a[0], a[1]), a[1])


def _r_C(a):
    return App(App(a[0], a[2]), a[1])


def _r_B(a):
    return App(a[0], App(a[1], a[2]))


def _r_S(a):
    return App(App(a[0], a[2]), App(a[1], a[2]))


def _r_D(a):
    return App(a[0], App(a[1], App(a[2], a[3])))


def _r_Y(a):
    return App(a[0], App(Comb("Y"), a[0]))


# combinator -> (arity, rule)
REDUCTIONS: dict[str, tuple[int, object]] = {
    "I": (1, _r_I),
    "K": (2, _r_K),
    "M": (1, _r_M),
    "W": (2, _r_W),
    "C": (3, _r_C),
    "B": (3, _r_B),
    "S": (3, _r_S),
    "D": (4, _r_D),
    "Y": (1, _r_Y),
}


def _root_redex(t: Term) -> Term | None:
    """If the spine root is a saturated combinator, fire it; else None."""
    head, args = spine(t)
    if isinstance(head, Comb) and head.name in REDUCTIONS:
        arity, rule = REDUCTIONS[head.name]
        if len(args) >= arity:
            return rebuild(rule(args[:arity]), args[arity:])
    return None


def step(t: Term) -> Term | None:
    """One leftmost-outermost reduction; None if t is a normal form."""
    r = _root_redex(t)
    if r is not None:
        return r
    head, args = spine(t)
    for i, a in enumerate(args):
        s = step(a)
        if s is not None:
            return rebuild(head, [*args[:i], s, *args[i + 1:]])
    return None


def is_whnf(t: Term) -> bool:
    """Weak head normal form: the spine root is not a saturated combinator."""
    return _root_redex(t) is None


def is_normal_form(t: Term) -> bool:
    return step(t) is None


class Status(StrEnum):
    NORMAL_FORM = "normal_form"   # reduction terminated
    DIVERGED = "diverged"         # step budget exhausted (e.g. Y, Ω)
    SIZE_EXCEEDED = "size_exceeded"  # term outgrew the representation (the limit)


@dataclass(frozen=True, slots=True)
class Reduction:
    initial: Term
    normal_form: Term
    trace: list[Term]
    status: Status
    steps: int
    whnf_step: int | None  # first step index at which WHNF was reached


def reduce(
    t: Term,
    max_steps: int = MAX_STEPS,
    max_size: int = MAX_SIZE,
) -> Reduction:
    """Normal-order reduce to normal form, recording the full trace.

    Halts at: normal form (NORMAL_FORM), step budget (DIVERGED), or term-size budget
    (SIZE_EXCEEDED — the representational limit the constructed kernel also has).
    """
    trace = [t]
    cur = t
    whnf_step = 0 if is_whnf(t) else None
    for i in range(max_steps):
        nxt = step(cur)
        if nxt is None:
            return Reduction(t, cur, trace, Status.NORMAL_FORM, i, whnf_step)
        cur = nxt
        trace.append(cur)
        if whnf_step is None and is_whnf(cur):
            whnf_step = i + 1
        if size(cur) > max_size:
            return Reduction(t, cur, trace, Status.SIZE_EXCEEDED, i + 1, whnf_step)
    return Reduction(t, cur, trace, Status.DIVERGED, max_steps, whnf_step)


def normal_form(t: Term, max_steps: int = MAX_STEPS) -> Term:
    return reduce(t, max_steps=max_steps).normal_form


# --------------------------------------------------------------------------- #
# CCG categories + type inference (the S2 type-check, first-class/inspectable) #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class CAtom:
    name: str


@dataclass(frozen=True, slots=True)
class CVar:
    id: int


@dataclass(frozen=True, slots=True)
class CSlash:
    """A CCG functor: takes `arg` on the `slash` side, returns `res`.

    slash '/' = forward (argument to the right) — all combinator applications.
    slash '\\' = backward (argument to the left) — for user atoms in NL order.
    """

    res: Cat
    slash: str
    arg: Cat


Cat = CAtom | CVar | CSlash


class IllTyped(Exception):
    """Raised when the S2 type-check fails (unification / occurs-check / no scheme)."""


class _Fresh:
    def __init__(self) -> None:
        self._n = 0

    def __call__(self) -> CVar:
        v = CVar(self._n)
        self._n += 1
        return v


def _fwd(res: Cat, arg: Cat) -> CSlash:
    return CSlash(res, "/", arg)


def _curry(args: list[Cat], result: Cat) -> Cat:
    """Curried forward functor: args[0] is the outermost (last-applied) slash."""
    cat: Cat = result
    for a in reversed(args):
        cat = _fwd(cat, a)
    return cat


def _scheme(name: str, fresh: _Fresh) -> Cat:
    """Instantiate a combinator's principal CCG category with fresh variables.

    M (self-application) has no simple type → IllTyped (the type-limit demo)."""
    a, b, c, d = fresh(), fresh(), fresh(), fresh()
    if name == "I":
        return _fwd(a, a)
    if name == "K":
        return _curry([a, b], a)
    if name == "W":
        return _curry([_curry([b, b], c), b], c)
    if name == "C":
        return _curry([_curry([b, a], c), a, b], c)
    if name == "B":
        return _curry([_fwd(a, b), _fwd(b, c), c], a)
    if name == "S":
        return _curry([_curry([a, b], c), _fwd(b, a), a], c)
    if name == "D":
        return _curry([_fwd(a, b), _fwd(b, c), _fwd(c, d), d], a)
    if name == "Y":
        return _curry([_fwd(a, a)], a)
    raise IllTyped(f"combinator {name!r} has no simple CCG type (self-application?)")


def _walk(c: Cat, subst: dict[int, Cat]) -> Cat:
    while isinstance(c, CVar) and c.id in subst:
        c = subst[c.id]
    return c


def _occurs(vid: int, c: Cat, subst: dict[int, Cat]) -> bool:
    c = _walk(c, subst)
    if isinstance(c, CVar):
        return c.id == vid
    if isinstance(c, CSlash):
        return _occurs(vid, c.res, subst) or _occurs(vid, c.arg, subst)
    return False


def _unify(x: Cat, y: Cat, subst: dict[int, Cat]) -> None:
    x, y = _walk(x, subst), _walk(y, subst)
    if isinstance(x, CVar):
        if isinstance(y, CVar) and y.id == x.id:
            return
        if _occurs(x.id, y, subst):
            raise IllTyped(f"occurs-check: {pretty_cat(x)} in {pretty_cat(y)}")
        subst[x.id] = y
        return
    if isinstance(y, CVar):
        _unify(y, x, subst)
        return
    if isinstance(x, CAtom) and isinstance(y, CAtom):
        if x.name != y.name:
            raise IllTyped(f"atom mismatch: {x.name} vs {y.name}")
        return
    if isinstance(x, CSlash) and isinstance(y, CSlash):
        if x.slash != y.slash:
            raise IllTyped(f"slash mismatch: {x.slash} vs {y.slash}")
        _unify(x.res, y.res, subst)
        _unify(x.arg, y.arg, subst)
        return
    raise IllTyped(f"cannot unify {pretty_cat(x)} with {pretty_cat(y)}")


def _resolve(c: Cat, subst: dict[int, Cat]) -> Cat:
    c = _walk(c, subst)
    if isinstance(c, CSlash):
        return CSlash(_resolve(c.res, subst), c.slash, _resolve(c.arg, subst))
    return c


def pretty_cat(c: Cat) -> str:
    if isinstance(c, CAtom):
        return c.name
    if isinstance(c, CVar):
        return _greek(c.id)
    return f"({pretty_cat(c.res)}{c.slash}{pretty_cat(c.arg)})"


def _greek(i: int) -> str:
    letters = "αβγδεζηθικλμνξ"
    return letters[i] if i < len(letters) else f"t{i}"


@dataclass
class TypeResult:
    ok: bool
    cat: Cat | None
    error: str | None = None
    # (subterm, category) for each App node — the inspectable derivation
    derivation: list[tuple[str, str]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok


def typecheck(t: Term, env: dict[str, Cat] | None = None) -> TypeResult:
    """Synthesize a principal CCG category via forward application + unification.

    env maps Atom names to fixed categories (e.g. {"john": CAtom("NP")}); unlisted
    atoms get a fresh variable (treated as polymorphic leaves). Returns ok=False with
    an error when the S2 type-check fails — the type-directedness boundary made
    explicit (compiler-as-loss.md §s226).
    """
    env = env or {}
    fresh = _Fresh()
    subst: dict[int, Cat] = {}
    deriv: list[tuple[str, str]] = []

    def infer(term: Term) -> Cat:
        if isinstance(term, Comb):
            return _scheme(term.name, fresh)
        if isinstance(term, Atom):
            return env.get(term.name, fresh())
        tf = infer(term.fn)
        tx = infer(term.arg)
        res = fresh()
        _unify(tf, _fwd(res, tx), subst)
        rc = _resolve(res, subst)
        deriv.append((pretty(term), pretty_cat(rc)))
        return res

    try:
        top = _resolve(infer(t), subst)
    except IllTyped as e:
        return TypeResult(False, None, str(e), deriv)
    return TypeResult(True, top, None, deriv)


# --------------------------------------------------------------------------- #
# Verify + data-oracle record                                                 #
# --------------------------------------------------------------------------- #
def _alpha_eq(a: Term, b: Term) -> bool:
    """Structural equality (no binders, so no alpha-renaming needed)."""
    if isinstance(a, Comb) and isinstance(b, Comb):
        return a.name == b.name
    if isinstance(a, Atom) and isinstance(b, Atom):
        return a.name == b.name
    if isinstance(a, App) and isinstance(b, App):
        return _alpha_eq(a.fn, b.fn) and _alpha_eq(a.arg, b.arg)
    return False


def verify(term: Term | str, claimed: Term | str, max_steps: int = MAX_STEPS) -> bool:
    """True iff `term` reduces to a normal form structurally equal to `claimed`.

    This is the VERIFIER role: certify a (possibly model-proposed) reduction is
    correct. Returns False if `term` does not reach normal form within budget."""
    t = parse(term) if isinstance(term, str) else term
    c = parse(claimed) if isinstance(claimed, str) else claimed
    red = reduce(t, max_steps=max_steps)
    if red.status is not Status.NORMAL_FORM:
        return False
    return _alpha_eq(red.normal_form, normal_form(c, max_steps=max_steps))


def trace_record(
    term: Term | str,
    env: dict[str, Cat] | None = None,
    max_steps: int = MAX_STEPS,
) -> dict:
    """The data-oracle hook: exact (input → reduction-trace) record + type verdict.

    This is the per-example training datum for compiler-as-loss (§s226): a diverse
    input certified to a canonical normal form, with the exact reduction tree."""
    t = parse(term) if isinstance(term, str) else term
    red = reduce(t, max_steps=max_steps)
    tr = typecheck(t, env)
    return {
        "input": pretty(t),
        "trace": [pretty(x) for x in red.trace],
        "normal_form": pretty(red.normal_form),
        "status": red.status.value,
        "steps": red.steps,
        "whnf_step": red.whnf_step,
        "well_typed": tr.ok,
        "category": pretty_cat(tr.cat) if tr.cat is not None else None,
        "type_error": tr.error,
    }
