"""Discriminating substitution-pair generator — the §P-SUBST-ENGINE probes.

THE FRONT (s330, Michael: "hard one first" — RE the substitution engine, the
ALU). Substitution only EXISTS at binder level, so this module builds terms that
FORCE a choice between the two candidate algorithms the model might be running:

    CAPTURE-AVOIDING  — the correct algorithm (rename binders that would capture)
    NAIVE             — textual replacement, capture-unsafe (the §2b rival)

Each **capture pair** is one term whose capture-avoiding normal form differs from
its naive normal form. Both normal forms are certified by ``verbum.lambda_ast``
(the reference reducer) and shipped with the probe: the model's answer reveals
WHICH algorithm it runs (§2b bug-compatibility — we grade against the model's
measured profile, the naive answer is a real, reproducible fingerprint, not an
error to be scored away).

Each **alpha pair** is one term and an alpha-variant (bound variables renamed).
An extensional engine is invariant under renaming; a syntactic router (the
cl-collapse x2 finding) is measurably alpha-variant — a predicted bug, quantified.

DIALS (the cliff coordinates, recorded per probe):
    binder_distance   — binders between the substituted λ and the reused variable
    shadow_depth      — how many of those binders would capture (≥1 ⇒ discriminates)
    live_var_count    — distinct free variables in the term
    functional_order  — the term's order (§8b HOF fold-in: order-2 takes/returns a
                        function, order-3+ nested; read the ORDER CLIFF for free)

MODES: ``direct`` (answer only) and ``traced`` (steps shown) — the folded
direct/traced pilot; the gap is read PER dial-level (token-budget null mandatory
downstream — the confound that killed FUEL/TRACE-FUEL/NF-GAUGE x3).

This module is a pure generator + self-validator. It runs NO model. The freeze
gate (pre-registration, Michael GO) is a separate step before any sweep.

    from verbum.probes.subst_pairs import all_pairs, capture_pairs, validate
    validate()                      # certifies every pair via lambda_ast
    for p in capture_pairs()[:3]:
        print(p.term, "→", p.correct_nf, "| naive:", p.naive_nf)

License: MIT (lambda provenance — observed here, ¬copied from nucleus).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache

from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    App,
    Atom,
    Comb,
    CSlash,
    Lam,
    Status,
    Term,
    alpha_eq,
    free_vars,
    normal_form,
    parse,
    pretty,
    reduce,
    typecheck,
)

__all__ = [
    "Dials",
    "SubstProbe",
    "all_pairs",
    "alpha_pairs",
    "capture_pairs",
    "validate",
]

MODES = ("direct", "traced")

# Disjoint name pools so a "capture" term genuinely discriminates.
_CAP_VARS = ("y", "w", "u")  # value's free vars — the ones a naive λ captures
_EXTRA_VARS = ("a", "b", "c")  # non-capturing binders (raise distance, not shadow)
_SUBST_VAR = "x"  # the variable being substituted


# --------------------------------------------------------------------------- #
# Records                                                                      #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Dials:
    """The cliff coordinates recorded for every probe (the sweep reads these)."""

    binder_distance: int
    shadow_depth: int
    live_var_count: int
    functional_order: int | None  # None iff the term has no simple CCG type


@dataclass(frozen=True, slots=True)
class SubstProbe:
    """One discriminating probe. ``family`` ∈ {capture, alpha}.

    capture: ``naive_nf`` is the rival fingerprint (≠ ``correct_nf``).
    alpha:   ``alpha_variant`` is a renamed surface form of ``term`` (same NF);
             ``naive_nf`` is None.
    """

    id: str
    family: str
    term: str
    correct_nf: str
    naive_nf: str | None
    alpha_variant: str | None
    dials: Dials
    mode: str

    def as_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Term construction helpers                                                    #
# --------------------------------------------------------------------------- #
def _app_chain(terms: list[Term]) -> Term:
    """Left-associative application spine of ``terms`` (len ≥ 1)."""
    head, *rest = terms
    for t in rest:
        head = App(head, t)
    return head


def _nf(term: Term, calc) -> tuple[str, Status]:
    red = reduce(term, calc=calc)
    return pretty(red.normal_form), red.status


# --------------------------------------------------------------------------- #
# Dials — measured structurally from the term                                  #
# --------------------------------------------------------------------------- #
def _path_to_free_var(t: Term, var: str) -> list[str] | None:
    """Binder names on the path to the first FREE occurrence of ``var`` (or None).

    Descending under a binder that re-binds ``var`` is skipped (it shadows)."""
    if isinstance(t, Atom):
        return [] if t.name == var else None
    if isinstance(t, Comb):
        return None
    if isinstance(t, App):
        left = _path_to_free_var(t.fn, var)
        if left is not None:
            return left
        return _path_to_free_var(t.arg, var)
    # Lam
    if t.var == var:
        return None  # shadows the variable we are tracking
    inner = _path_to_free_var(t.body, var)
    return None if inner is None else [t.var, *inner]


def _cat_order(c) -> int:
    if isinstance(c, CSlash):
        return max(_cat_order(c.res), _cat_order(c.arg) + 1)
    return 0


def _subterms(t: Term):
    yield t
    if isinstance(t, App):
        yield from _subterms(t.fn)
        yield from _subterms(t.arg)
    elif isinstance(t, Lam):
        yield from _subterms(t.body)


def _functional_order(t: Term) -> int | None:
    """The term's functional order = the MAX category order over all subterms
    (§8b HOF fold-in). A saturated application's top category collapses to low
    order, so the order cliff lives in the sub-expressions: ``x`` used as a
    function (``x y``) makes ``λx.…`` order-2 even where the whole term is order-1.
    None iff no subterm has a simple CCG type."""
    orders = [
        _cat_order(tr.cat)
        for s in _subterms(t)
        if (tr := typecheck(s)).ok and tr.cat is not None
    ]
    return max(orders) if orders else None


def _redex_dials(term: Term) -> Dials:
    """Compute the four dials. For a β-redex ``(λx.body) value`` the binder
    metrics measure the path from ``body`` to the reused ``x``; otherwise 0."""
    binder_distance = 0
    shadow_depth = 0
    if isinstance(term, App) and isinstance(term.fn, Lam):
        lam, value = term.fn, term.arg
        path = _path_to_free_var(lam.body, lam.var)
        if path is not None:
            captured = free_vars(value)
            binder_distance = len(path)
            shadow_depth = sum(1 for name in path if name in captured)
    return Dials(
        binder_distance=binder_distance,
        shadow_depth=shadow_depth,
        live_var_count=len(free_vars(term)),
        functional_order=_functional_order(term),
    )


# --------------------------------------------------------------------------- #
# Capture-pair generation                                                      #
# --------------------------------------------------------------------------- #
def _make_capture_term(shadow_k: int, extra_m: int, order: int) -> Term:
    """Build ``(λx. λcap…λextra. <x | x cap…>) <value>`` so naive substitution
    captures the ``value`` free vars in the ``cap`` binders."""
    cap = list(_CAP_VARS[:shadow_k])
    extra = list(_EXTRA_VARS[:extra_m])
    value = _app_chain([Atom(v) for v in cap])
    if order == 1:
        inner: Term = Atom(_SUBST_VAR)
    else:  # order 2 — x is applied to the captured vars ⇒ higher-order
        inner = _app_chain([Atom(_SUBST_VAR), *[Atom(v) for v in cap]])
    body = inner
    for v in reversed(extra):  # inner (non-capturing) binders, closest to x
        body = Lam(v, body)
    for v in reversed(cap):  # outer capturing binders
        body = Lam(v, body)
    return App(Lam(_SUBST_VAR, body), value)


def _gen_capture() -> list[SubstProbe]:
    probes: list[SubstProbe] = []
    idx = 0
    for order in (1, 2):
        for shadow_k in (1, 2, 3):
            for extra_m in (0, 1, 2):
                term = _make_capture_term(shadow_k, extra_m, order)
                correct_nf, cst = _nf(term, R_NORMAL)
                naive_nf, nst = _nf(term, R_NAIVE)
                dials = _redex_dials(term)
                surface = pretty(term)
                for mode in MODES:
                    probes.append(
                        SubstProbe(
                            id=f"cap_{idx:03d}_{mode}",
                            family="capture",
                            term=surface,
                            correct_nf=correct_nf,
                            naive_nf=naive_nf,
                            alpha_variant=None,
                            dials=dials,
                            mode=mode,
                        )
                    )
                # certification asserted in validate(); statuses carried implicitly
                _ = (cst, nst)
                idx += 1
    return probes


# --------------------------------------------------------------------------- #
# Alpha-pair generation                                                        #
# --------------------------------------------------------------------------- #
_ALPHA_BASES = (
    "λx.x",
    "λx.λy.x",
    "λf.λx.f (f x)",
    "(λx.λy.x y) a",
    "(λf.λg.λx.f (g x)) h k z",
    "(λx.λy.x) y",  # a capture term, presented for its alpha-invariance
)


def _alpha_rename_all(t: Term, counter: list[int], env: dict[str, str]) -> Term:
    """Rename EVERY bound variable to a fresh ``q{n}`` scheme (scope-correct)."""
    if isinstance(t, Atom):
        return Atom(env.get(t.name, t.name))
    if isinstance(t, Comb):
        return t
    if isinstance(t, App):
        return App(
            _alpha_rename_all(t.fn, counter, env),
            _alpha_rename_all(t.arg, counter, env),
        )
    new = f"q{counter[0]}"  # Lam
    counter[0] += 1
    return Lam(new, _alpha_rename_all(t.body, counter, {**env, t.var: new}))


def _gen_alpha() -> list[SubstProbe]:
    probes: list[SubstProbe] = []
    for idx, src in enumerate(_ALPHA_BASES):
        term = parse(src)
        variant = _alpha_rename_all(term, [0], {})
        correct_nf, _ = _nf(term, R_NORMAL)
        dials = _redex_dials(term)
        for mode in MODES:
            probes.append(
                SubstProbe(
                    id=f"alpha_{idx:03d}_{mode}",
                    family="alpha",
                    term=pretty(term),
                    correct_nf=correct_nf,
                    naive_nf=None,
                    alpha_variant=pretty(variant),
                    dials=dials,
                    mode=mode,
                )
            )
    return probes


# --------------------------------------------------------------------------- #
# Public accessors                                                             #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def capture_pairs() -> tuple[SubstProbe, ...]:
    """All capture-discriminating probes (correct_nf ≠ naive_nf)."""
    return tuple(_gen_capture())


@lru_cache(maxsize=1)
def alpha_pairs() -> tuple[SubstProbe, ...]:
    """All alpha-invariance probes (term vs a renamed variant)."""
    return tuple(_gen_alpha())


def all_pairs() -> tuple[SubstProbe, ...]:
    """Every §P-SUBST-ENGINE probe (capture + alpha)."""
    return capture_pairs() + alpha_pairs()


# --------------------------------------------------------------------------- #
# Self-validation — certify every pair via the reference reducer               #
# --------------------------------------------------------------------------- #
def validate() -> dict:
    """Certify the generated set against ``lambda_ast``. Raises on any failure.

    Capture: correct_nf and naive_nf both reach normal form, and are NOT
    alpha-equal (the pair genuinely discriminates); shadow_depth ≥ 1; the
    recorded strings match a fresh recomputation.
    Alpha:   term and variant are alpha-equal, structurally distinct surfaces,
    and reduce to alpha-equal normal forms.
    """
    caps = capture_pairs()
    alphas = alpha_pairs()

    for p in caps:
        term = parse(p.term)
        red_c = reduce(term, calc=R_NORMAL)
        red_n = reduce(term, calc=R_NAIVE)
        assert red_c.status is Status.NORMAL_FORM, f"{p.id}: correct not NF"
        assert red_n.status is Status.NORMAL_FORM, f"{p.id}: naive not NF"
        assert pretty(red_c.normal_form) == p.correct_nf, f"{p.id}: correct_nf drift"
        assert p.naive_nf is not None and pretty(red_n.normal_form) == p.naive_nf, (
            f"{p.id}: naive_nf drift"
        )
        assert not alpha_eq(red_c.normal_form, red_n.normal_form), (
            f"{p.id}: pair does NOT discriminate (correct ≡ naive)"
        )
        assert p.dials.shadow_depth >= 1, f"{p.id}: no shadowing binder"

    for p in alphas:
        assert p.alpha_variant is not None, f"{p.id}: missing alpha variant"
        a, b = parse(p.term), parse(p.alpha_variant)
        assert alpha_eq(a, b), f"{p.id}: variant not alpha-equal"
        assert p.term != p.alpha_variant, f"{p.id}: variant is identical surface"
        assert alpha_eq(normal_form(a), normal_form(b)), f"{p.id}: NFs differ"

    orders = sorted(
        {p.dials.functional_order for p in caps if p.dials.functional_order is not None}
    )
    return {
        "capture_probes": len(caps),
        "alpha_probes": len(alphas),
        "total": len(caps) + len(alphas),
        "shadow_depths": sorted({p.dials.shadow_depth for p in caps}),
        "binder_distances": sorted({p.dials.binder_distance for p in caps}),
        "functional_orders": orders,
        "modes": list(MODES),
    }


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="§P-SUBST-ENGINE discriminating pairs")
    ap.add_argument(
        "--validate",
        action="store_true",
        help="certify every generated pair via lambda_ast and print a summary",
    )
    ap.add_argument(
        "--sample", type=int, default=0, help="print N sample probes of each family"
    )
    args = ap.parse_args(argv)

    if args.validate or args.sample == 0:
        report = validate()
        print("§P-SUBST-ENGINE self-validation: PASS")
        for k, v in report.items():
            print(f"  {k}: {v}")

    if args.sample:
        for label, pool in (("capture", capture_pairs()), ("alpha", alpha_pairs())):
            print(f"\n── {label} (first {args.sample}) ──")
            seen = 0
            for p in pool:
                if p.mode != "direct":
                    continue
                if p.family == "capture":
                    print(
                        f"  {p.term}\n    correct: {p.correct_nf}"
                        f"\n    naive:   {p.naive_nf}  {p.dials}"
                    )
                else:
                    print(
                        f"  {p.term}\n    variant: {p.alpha_variant}"
                        f"\n    nf:      {p.correct_nf}  {p.dials}"
                    )
                seen += 1
                if seen >= args.sample:
                    break
    return 0


if __name__ == "__main__":
    sys.exit(_main())
