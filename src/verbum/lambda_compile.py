"""Lambda compile — bracket abstraction (the EXACT compile oracle, stage 2).

THE ROLE (session 226). Stage 2 is the neurosymbolic system: a learned compile
front-end + the exact `lambda_ast` kernel back-end. But the "compile" step factors:

    prose          → logical-form     : LEARNED  (NL understanding; Montague/CCG parse)
    logical-form   → combinator term  : EXACT    (bracket abstraction — THIS module)
    combinator term → normal form     : EXACT    (reduction — lambda_ast, stage 1)

Bracket abstraction is the INVERSE of reduction (combinatory completeness, Turner
1979): given an expression e with free variables, it produces a closed combinator
term t such that `t v1 ... vn` reduces back to e. So the two symbolic halves
cross-validate through the kernel — the round-trip

    reduce( compile([x..], e) applied to [x..] )  ≡  e

is the kernel CERTIFYING the compiler (and vice-versa). This shrinks the learned
surface to just prose→logical-form (the project's Montague/DisCoCat target); the
formal compile is constructible, like the reducer (compiler-as-loss.md §s226).

Algorithm: Turner-style abstraction over {S,K,I,B,C} (combinatorially complete, all
reducible by the stage-1 kernel), with the standard K/B/C/η optimizations that keep
terms small:

    [x] x            = I
    [x] E            = K E                 (x not free in E)
    [x] (E1 x)       = E1                  (η, x not free in E1)
    [x] (E1 E2)      = B E1 ([x]E2)        (x free only in E2)
                     = C ([x]E1) E2        (x free only in E1)
                     = S ([x]E1) ([x]E2)   (x free in both)

License: MIT. AGENTS.md S5 λ provenance (written from theory, not nucleus).
"""

from __future__ import annotations

from verbum.lambda_ast import (
    App,
    Atom,
    Comb,
    Status,
    Term,
    normal_form,
    parse,
    pretty,
    pretty_cat,
    reduce,
    size,
    typecheck,
)

__all__ = [
    "abstract",
    "compile_expr",
    "compile_record",
    "free_vars",
    "occurs",
    "roundtrip",
]


def occurs(var: str, t: Term) -> bool:
    """Does an Atom named `var` appear anywhere in t?"""
    if isinstance(t, Atom):
        return t.name == var
    if isinstance(t, App):
        return occurs(var, t.fn) or occurs(var, t.arg)
    return False


def free_vars(t: Term) -> set[str]:
    """All Atom names in t (no binders ⇒ every atom is free)."""
    if isinstance(t, Atom):
        return {t.name}
    if isinstance(t, App):
        return free_vars(t.fn) | free_vars(t.arg)
    return set()


def abstract(var: str, t: Term) -> Term:
    """[var] t — Turner bracket abstraction; result has `var` removed.

    Invariant: `App(abstract(var, t), Atom(var))` reduces to `t`."""
    if not occurs(var, t):
        return App(Comb("K"), t)
    if isinstance(t, Atom):  # must be the var itself (occurs ⇒ name matches)
        return Comb("I")
    if isinstance(t, App):
        f, a = t.fn, t.arg
        # η: [x](f x) = f   when x not free in f
        if isinstance(a, Atom) and a.name == var and not occurs(var, f):
            return f
        xf, xa = occurs(var, f), occurs(var, a)
        if not xf and xa:
            return App(App(Comb("B"), f), abstract(var, a))
        if xf and not xa:
            return App(App(Comb("C"), abstract(var, f)), a)
        return App(App(Comb("S"), abstract(var, f)), abstract(var, a))
    # t is a Comb with var occurring — impossible (occurs is False for Comb)
    return App(Comb("K"), t)  # pragma: no cover


def compile_expr(variables: list[str], expr: Term) -> Term:
    """Abstract `variables` (in order) out of `expr` → a closed combinator term.

    Result t satisfies: `t v1 ... vn` reduces to `expr`. Abstraction is folded
    right-to-left so the leftmost variable is the first argument applied."""
    t = expr
    for v in reversed(variables):
        t = abstract(v, t)
    return t


def _apply(t: Term, variables: list[str]) -> Term:
    for v in variables:
        t = App(t, Atom(v))
    return t


def roundtrip(
    variables: list[str],
    expr: Term | str,
    max_steps: int = 512,
) -> bool:
    """True iff reduce(compile(variables, expr) applied to variables) ≡ nf(expr).

    The kernel certifying the compiler (and the compiler certifying the kernel)."""
    e = parse(expr) if isinstance(expr, str) else expr
    term = compile_expr(variables, e)
    red = reduce(_apply(term, variables), max_steps=max_steps)
    if red.status is not Status.NORMAL_FORM:
        return False
    return _eq(red.normal_form, normal_form(e, max_steps=max_steps))


def _eq(a: Term, b: Term) -> bool:
    if isinstance(a, Atom) and isinstance(b, Atom):
        return a.name == b.name
    if isinstance(a, Comb) and isinstance(b, Comb):
        return a.name == b.name
    if isinstance(a, App) and isinstance(b, App):
        return _eq(a.fn, b.fn) and _eq(a.arg, b.arg)
    return False


def compile_record(
    variables: list[str],
    expr: Term | str,
    max_steps: int = 512,
) -> dict:
    """The stage-2 (logical-form → combinator term) datum, kernel-certified.

    A learned front-end is trained to map (variables, expr) → term; this record is
    the exact gold + the verification that abstraction and reduction are inverse."""
    e = parse(expr) if isinstance(expr, str) else expr
    term = compile_expr(variables, e)
    red = reduce(_apply(term, variables), max_steps=max_steps)
    ok = red.status is Status.NORMAL_FORM and _eq(
        red.normal_form, normal_form(e, max_steps=max_steps)
    )
    tc = typecheck(term)
    return {
        "variables": list(variables),
        "expr": pretty(e),
        "term": pretty(term),  # the compile target (point-free)
        "applied_normal_form": pretty(red.normal_form),
        "roundtrip_ok": ok,
        "reduce_status": red.status.value,
        "well_typed": tc.ok,
        "category": None if tc.cat is None else pretty_cat(tc.cat),
        "expr_size": size(e),
        "term_size": size(term),
    }
