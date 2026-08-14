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

  Term     = Comb(name) | Atom(name) | App(fn, arg) | Lam(var, body)  # +binders
  Category = CAtom(name) | CVar(id) | CSlash(res, dir, arg)     # CCG, dir = fwd or bwd

BINDER EXTENSION (§P-SUBST-ENGINE, the-benchmark-is-the-re-oracle.md §8). The
substitution engine — the ALU — only exists at binder level; combinator terms
dodge binding by construction. `Lam` adds named binders; `substitute` is the
correct capture-avoiding algorithm, `naive_subst` the deliberate capture-unsafe
rival (§2b: grading = which algorithm's output the model matches). The reducer
is parameterised by a `Calculus` (§9: strong/weak ξ · η · capture-avoiding) so
calculus identification rides the same sweeps — ¬hardcode strong-β.

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
    "R_CHURCH",
    "R_NAIVE",
    "R_NORMAL",
    "R_WEAK",
    "App",
    "Atom",
    "CAtom",
    "CSlash",
    "CVar",
    "Calculus",
    "Cat",
    "Comb",
    "IllTyped",
    "Lam",
    "Reduction",
    "Status",
    "Term",
    "TypeResult",
    "affine_ok",
    "alpha_eq",
    "free_vars",
    "naive_subst",
    "normal_form",
    "occurrence_profile",
    "parse",
    "pretty",
    "reduce",
    "substitute",
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


@dataclass(frozen=True, slots=True)
class Lam:
    """A binder — ``λvar.body``. Named variables (Atom leaves) are bound by the
    nearest enclosing ``Lam`` of the same name; unbound Atoms are free.

    The substitution engine (the ALU, §P-SUBST-ENGINE) only EXISTS at binder
    level — combinator terms dodge binding by construction. ``Lam`` is the node
    the capture-avoiding / naive-substitution rivalry (§2b) is measured on.
    """

    var: str
    body: Term


Term = Comb | Atom | App | Lam


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
    if isinstance(t, Lam):
        return 1 + size(t.body)
    return 1


def pretty(t: Term) -> str:
    """Render a term; parenthesise applications/binders in argument position.

    A ``Lam`` renders ``λvar.body`` and extends as far right as possible, so a
    binder in head or argument position is parenthesised to stay round-trippable
    (e.g. ``(λx.x) y`` — otherwise ``λx.x y`` parses as ``λx.(x y)``).
    """
    if isinstance(t, Comb | Atom):
        return t.name
    if isinstance(t, Lam):
        return f"λ{t.var}.{pretty(t.body)}"
    head, args = spine(t)
    head_s = f"({pretty(head)})" if isinstance(head, Lam) else pretty(head)
    parts = [head_s]
    for a in args:
        parts.append(f"({pretty(a)})" if isinstance(a, App | Lam) else pretty(a))
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
        elif c in "().":
            toks.append(c)
            i += 1
        elif c in ("λ", "\\"):
            toks.append("λ")  # normalise both binder glyphs
            i += 1
        elif c.isalnum() or c == "_":
            j = i
            # identifiers may carry trailing primes — the alpha-rename fresh names
            while j < n and (s[j].isalnum() or s[j] in "_'"):
                j += 1
            toks.append(s[i:j])
            i = j
        else:
            raise ValueError(f"lambda_ast.parse: bad char {c!r} in {s!r}")
    return toks


_STOP = frozenset((")", "."))


def parse(s: str) -> Term:
    """Parse a combinator/lambda term.

    Single uppercase letters S K I B C W D Y M are combinators; ``λx.`` or
    ``\\x.`` introduce a binder (``λx y.body`` sugars to ``λx.λy.body``);
    everything else is an Atom. Application is juxtaposition (left-assoc); a
    lambda body extends as far right as possible.
    """
    toks = _tokenize(s)
    pos = 0

    def lam() -> Term:
        nonlocal pos
        pos += 1  # consume "λ"
        vs: list[str] = []
        while pos < len(toks) and toks[pos] != ".":
            v = toks[pos]
            if v in ("(", ")", "λ"):
                raise ValueError(f"lambda_ast.parse: bad binder var {v!r} in {s!r}")
            vs.append(v)
            pos += 1
        if not vs:
            raise ValueError(f"lambda_ast.parse: λ with no variable in {s!r}")
        if pos >= len(toks) or toks[pos] != ".":
            raise ValueError(f"lambda_ast.parse: λ missing '.' in {s!r}")
        pos += 1  # consume "."
        term = application()
        for v in reversed(vs):
            term = Lam(v, term)
        return term

    def atom() -> Term:
        nonlocal pos
        if pos >= len(toks):
            raise ValueError(f"lambda_ast.parse: unexpected end in {s!r}")
        tok = toks[pos]
        if tok == "λ":
            return lam()
        if tok == "(":
            pos += 1
            inner = application()
            if pos >= len(toks) or toks[pos] != ")":
                raise ValueError(f"lambda_ast.parse: unbalanced parens in {s!r}")
            pos += 1
            return inner
        if tok in _STOP:
            raise ValueError(f"lambda_ast.parse: unexpected {tok!r} in {s!r}")
        pos += 1
        if len(tok) == 1 and tok in _COMBINATORS:
            return Comb(tok)
        return Atom(tok)

    def application() -> Term:
        nonlocal pos
        t = atom()
        while pos < len(toks) and toks[pos] not in _STOP:
            t = App(t, atom())
        return t

    term = application()
    if pos != len(toks):
        raise ValueError(f"lambda_ast.parse: trailing tokens in {s!r}")
    return term


# --------------------------------------------------------------------------- #
# Binders — free variables, substitution (the ALU), alpha-equivalence          #
# --------------------------------------------------------------------------- #
def free_vars(t: Term) -> frozenset[str]:
    """The free (unbound) Atom names of a term. Combinators are not variables."""
    if isinstance(t, Atom):
        return frozenset((t.name,))
    if isinstance(t, Comb):
        return frozenset()
    if isinstance(t, App):
        return free_vars(t.fn) | free_vars(t.arg)
    return free_vars(t.body) - {t.var}  # Lam


def _fresh_name(base: str, avoid: frozenset[str]) -> str:
    """Prime ``base`` until it avoids ``avoid`` — the capture-avoiding rename."""
    cand = base
    while cand in avoid:
        cand += "'"
    return cand


def _rename(t: Term, old: str, new: str) -> Term:
    """Alpha-rename free occurrences of ``old`` to ``new``. ``new`` MUST be fresh
    (unbound in ``t``), so naive replacement is capture-safe here by construction."""
    return _subst(t, old, Atom(new), capture_avoiding=False)


def _subst(t: Term, var: str, value: Term, *, capture_avoiding: bool) -> Term:
    """β-substitution ``t[var := value]``.

    ``capture_avoiding=True``  → the CORRECT algorithm: rename binders that would
                                 capture a free variable of ``value``.
    ``capture_avoiding=False`` → the deliberate NAIVE algorithm: textual
                                 replacement, no capture check (§2b: the rival
                                 fingerprint the model may match instead).

    Both algorithms respect shadowing of the same name (``λvar.…`` stops).
    """
    if isinstance(t, Atom):
        return value if t.name == var else t
    if isinstance(t, Comb):
        return t
    if isinstance(t, App):
        return App(
            _subst(t.fn, var, value, capture_avoiding=capture_avoiding),
            _subst(t.arg, var, value, capture_avoiding=capture_avoiding),
        )
    # Lam
    if t.var == var:
        return t  # the binder shadows var — no free occurrence below
    if capture_avoiding and t.var in free_vars(value):
        fresh = _fresh_name(t.var, free_vars(value) | free_vars(t.body) | {var})
        body = _rename(t.body, t.var, fresh)
        return Lam(fresh, _subst(body, var, value, capture_avoiding=True))
    return Lam(t.var, _subst(t.body, var, value, capture_avoiding=capture_avoiding))


def substitute(t: Term, var: str, value: Term) -> Term:
    """Capture-avoiding substitution ``t[var := value]`` (the correct algorithm)."""
    return _subst(t, var, value, capture_avoiding=True)


def naive_subst(t: Term, var: str, value: Term) -> Term:
    """Capture-UNSAFE textual substitution — kept on purpose (§2b rival)."""
    return _subst(t, var, value, capture_avoiding=False)


def _debruijn(t: Term, env: tuple[str, ...]) -> object:
    """A nameless encoding: bound vars → de Bruijn index, free/comb by name.

    ``env`` lists enclosing binder names, innermost LAST; alpha-equivalent terms
    map to equal encodings (the comparator's ground truth)."""
    if isinstance(t, Atom):
        for i, name in enumerate(reversed(env)):
            if name == t.name:
                return ("bound", i)
        return ("free", t.name)
    if isinstance(t, Comb):
        return ("comb", t.name)
    if isinstance(t, App):
        return ("app", _debruijn(t.fn, env), _debruijn(t.arg, env))
    return ("lam", _debruijn(t.body, (*env, t.var)))  # Lam


def alpha_eq(a: Term, b: Term) -> bool:
    """True iff ``a`` and ``b`` are equal up to renaming of bound variables."""
    return _debruijn(a, ()) == _debruijn(b, ())


# --------------------------------------------------------------------------- #
# Calculus switches (§9) — the reference FAMILY, ships day one (¬hardcode β)    #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Calculus:
    """The strategy switches that select WHICH calculus the reducer realises.

    The ledger already refutes pure Church (≥3 registers: KIBC¬SKI affine ·
    non-idempotent graded · WHNF weak pole). Rather than hardcode strong-β, the
    reducer is parameterised so calculus identification rides the SAME sweeps at
    ~zero marginal cost (§9, the-benchmark-is-the-re-oracle.md).

      reduce_under_lam — ξ rule: reduce inside binder bodies (strong) vs stop at
                         weak head normal form (the WHNF pole candidate).
      eta              — η-contraction ``λx.(M x) → M`` when ``x ∉ FV(M)``.
      capture_avoiding — correct substitution (True) vs the naive rival (False).
    """

    name: str
    reduce_under_lam: bool = True
    eta: bool = False
    capture_avoiding: bool = True


#: Strong normal-order, capture-avoiding — the default oracle reducer.
R_NORMAL = Calculus("R_normal", reduce_under_lam=True, eta=False, capture_avoiding=True)
#: Weak head reduction, no ξ — the WHNF-pole candidate (crystal, s-lineage).
R_WEAK = Calculus("R_weak", reduce_under_lam=False, eta=False, capture_avoiding=True)
#: Strong βη — the Church reference (reduce under binders, η on).
R_CHURCH = Calculus("R_church", reduce_under_lam=True, eta=True, capture_avoiding=True)
#: The deliberate bug: naive (capture-unsafe) substitution — the rival fingerprint.
R_NAIVE = Calculus("R_naive", reduce_under_lam=True, eta=False, capture_avoiding=False)


# --------------------------------------------------------------------------- #
# Structural / graded analyses (affine-check, occurrence counting)             #
# --------------------------------------------------------------------------- #
def _count_free(t: Term, var: str) -> int:
    """Number of free occurrences of ``var`` in ``t`` (shadowing respected)."""
    if isinstance(t, Atom):
        return 1 if t.name == var else 0
    if isinstance(t, Comb):
        return 0
    if isinstance(t, App):
        return _count_free(t.fn, var) + _count_free(t.arg, var)
    return 0 if t.var == var else _count_free(t.body, var)  # Lam


def affine_ok(t: Term) -> bool:
    """True iff every λ-bound variable is used at most once (the affine check —
    the KIBC¬SKI substructural register, s313). ``S`` / ``W`` duplicate."""
    if isinstance(t, Lam):
        return _count_free(t.body, t.var) <= 1 and affine_ok(t.body)
    if isinstance(t, App):
        return affine_ok(t.fn) and affine_ok(t.arg)
    return True


def occurrence_profile(t: Term) -> list[tuple[str, int]]:
    """Per-binder ``(var, free_occurrence_count)``, outermost binder first — the
    graded/quantitative register (non-idempotent accumulation, s320)."""
    out: list[tuple[str, int]] = []

    def walk(term: Term) -> None:
        if isinstance(term, Lam):
            out.append((term.var, _count_free(term.body, term.var)))
            walk(term.body)
        elif isinstance(term, App):
            walk(term.fn)
            walk(term.arg)

    walk(t)
    return out


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


def _eta_contract(t: Lam) -> Term | None:
    """η: ``λx.(M x) → M`` when ``x ∉ FV(M)`` (else None)."""
    body = t.body
    if (
        isinstance(body, App)
        and isinstance(body.arg, Atom)
        and body.arg.name == t.var
        and t.var not in free_vars(body.fn)
    ):
        return body.fn
    return None


def _step_impl(t: Term, calc: Calculus) -> tuple[Term | None, str | None]:
    """One leftmost-outermost reduction under ``calc``, reporting the fired opcode.

    Returns (next_term, label). (None, None) iff ``t`` is a ``calc``-normal form.
    Opcode labels: ``"β"`` (binder application) · ``"η"`` · the combinator name.
    Order: root β/combinator first (leftmost-outermost), then η at a bare binder,
    then (if strong) under the binder, then arguments left-to-right.
    """
    head, args = spine(t)
    # root β-redex: a binder applied to ≥1 argument
    if isinstance(head, Lam) and args:
        reduced = _subst(
            head.body, head.var, args[0], capture_avoiding=calc.capture_avoiding
        )
        return rebuild(reduced, args[1:]), "β"
    # root combinator redex
    if isinstance(head, Comb) and head.name in REDUCTIONS:
        arity, rule = REDUCTIONS[head.name]
        if len(args) >= arity:
            return rebuild(rule(args[:arity]), args[arity:]), head.name
    # bare binder: η at the root, then (if strong) reduce inside the body
    if isinstance(head, Lam) and not args:
        if calc.eta:
            e = _eta_contract(head)
            if e is not None:
                return e, "η"
        if calc.reduce_under_lam:
            b, fired = _step_impl(head.body, calc)
            if b is not None:
                return Lam(head.var, b), fired
        return None, None
    # reduce arguments left-to-right
    for i, a in enumerate(args):
        s, fired = _step_impl(a, calc)
        if s is not None:
            return rebuild(head, [*args[:i], s, *args[i + 1:]]), fired
    return None, None


def step(t: Term, calc: Calculus = R_NORMAL) -> Term | None:
    """One leftmost-outermost reduction under ``calc``; None if ``t`` is normal."""
    return _step_impl(t, calc)[0]


def step_fired(
    t: Term, calc: Calculus = R_NORMAL
) -> tuple[Term | None, str | None]:
    """One reduction, ALSO reporting which opcode fired (``β`` / ``η`` / combinator).

    Returns (next_term, fired_name). (None, None) iff ``t`` is a normal form. The
    certified OPCODE the kernel-as-reference audit anchors a model's routing
    trajectory against."""
    return _step_impl(t, calc)


def fired_sequence(
    t: Term, max_steps: int = MAX_STEPS, calc: Calculus = R_NORMAL
) -> list[str]:
    """The certified per-step opcode trace, in reduction order.

    Normal form -> []. Under-applied (inert) combinators never appear (they never
    saturate -> never fire). The multiset/order is exactly what `reduce` walks."""
    seq: list[str] = []
    cur = t
    for _ in range(max_steps):
        nxt, fired = _step_impl(cur, calc)
        if nxt is None:
            break
        seq.append(fired)  # type: ignore[arg-type]
        cur = nxt
        if size(cur) > MAX_SIZE:
            break
    return seq


def is_whnf(t: Term) -> bool:
    """Weak head normal form: the spine root is not a saturated redex (β or comb)."""
    head, args = spine(t)
    if isinstance(head, Lam) and args:
        return False
    if isinstance(head, Comb) and head.name in REDUCTIONS:
        arity, _rule = REDUCTIONS[head.name]
        if len(args) >= arity:
            return False
    return True


def is_normal_form(t: Term, calc: Calculus = R_NORMAL) -> bool:
    return step(t, calc) is None


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
    calc: Calculus = R_NORMAL,
) -> Reduction:
    """Reduce to ``calc``-normal form (default: strong normal order), full trace.

    ``calc`` selects the calculus (§9): strong/weak ξ · η · capture-avoiding vs
    naive substitution. Halts at: normal form (NORMAL_FORM), step budget
    (DIVERGED), or term-size budget (SIZE_EXCEEDED — the representational limit
    the constructed kernel also has).
    """
    trace = [t]
    cur = t
    whnf_step = 0 if is_whnf(t) else None
    for i in range(max_steps):
        nxt = step(cur, calc)
        if nxt is None:
            return Reduction(t, cur, trace, Status.NORMAL_FORM, i, whnf_step)
        cur = nxt
        trace.append(cur)
        if whnf_step is None and is_whnf(cur):
            whnf_step = i + 1
        if size(cur) > max_size:
            return Reduction(t, cur, trace, Status.SIZE_EXCEEDED, i + 1, whnf_step)
    return Reduction(t, cur, trace, Status.DIVERGED, max_steps, whnf_step)


def normal_form(
    t: Term, max_steps: int = MAX_STEPS, calc: Calculus = R_NORMAL
) -> Term:
    return reduce(t, max_steps=max_steps, calc=calc).normal_form


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
        if isinstance(term, Lam):
            xt = fresh()
            sentinel = object()
            prev = env.get(term.var, sentinel)
            env[term.var] = xt  # bind the parameter, shadowing any outer binding
            bt = infer(term.body)
            if prev is sentinel:
                del env[term.var]
            else:
                env[term.var] = prev  # type: ignore[assignment]
            fc = _fwd(_resolve(bt, subst), _resolve(xt, subst))
            deriv.append((pretty(term), pretty_cat(_resolve(fc, subst))))
            return fc
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
    """Equality up to renaming of bound variables (de Bruijn; binder-aware)."""
    return alpha_eq(a, b)


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
