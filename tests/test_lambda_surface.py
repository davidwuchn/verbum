"""Tests for verbum.lambda_surface — surface FOL/λ → kernel Term (session 241)."""

from __future__ import annotations

import pytest

from verbum.lambda_ast import pretty, reduce
from verbum.lambda_surface import (
    SBind,
    SurfaceError,
    lower,
    parse_surface,
    to_kernel,
)

# (surface output, expected kernel normal form) — taken from the canonical corpus,
# whose rows carry precomputed `normal_form`. Keeps the test hermetic (no file I/O).
CORPUS_CASES = [
    ("∀x. artist(x) → knows(x, baker)",
     "forall (S (B implies artist) (C knows baker))"),
    ("follows(frank, oscar)", "follows frank oscar"),
    ("¬sleeps(john)", "not (sleeps john)"),
    ("happy(mary) ∧ sleeps(mary)", "and (happy mary) (sleeps mary)"),
]


@pytest.mark.parametrize(("surface", "gold_nf"), CORPUS_CASES)
def test_to_kernel_reduces_to_gold_nf(surface: str, gold_nf: str):
    """to_kernel lowers surface FOL/λ to a Term that reduces to the corpus NF."""
    term = to_kernel(surface)
    got = pretty(reduce(term).normal_form)
    assert got == gold_nf


def test_quantifier_lowers_via_bracket_abstraction():
    """∀ becomes a higher-order atom over the abstracted predicate."""
    assert pretty(to_kernel("∀x. runs(x)")) == "forall runs"


def test_existential_and_iota_heads():
    assert pretty(to_kernel("∃x. runs(x)")) == "exists runs"
    assert pretty(to_kernel("ι x. runs(x)")) == "iota runs"


def test_parse_surface_error_on_garbage():
    with pytest.raises(SurfaceError):
        parse_surface("∀x. artist(")
    with pytest.raises(SurfaceError):
        parse_surface("foo )")


def test_vacuous_binder_is_tracked():
    """A binder whose var never appears in the body appends its kind to `vacuous`."""
    vac: list[str] = []
    lower(parse_surface("λx. follows(frank, oscar)"), vac)
    assert vac == ["λ"]


def test_nonvacuous_binder_not_tracked():
    vac: list[str] = []
    lower(parse_surface("λx. runs(x)"), vac)
    assert vac == []


def test_lower_default_vacuous_sink_is_optional():
    """lower works without passing a vacuous sink (the to_kernel path)."""
    term = lower(parse_surface("runs(dog)"))
    assert pretty(term) == "runs dog"


def test_surface_ast_shapes():
    e = parse_surface("∀x. artist(x) → knows(x, baker)")
    assert isinstance(e, SBind)
    assert e.kind == "∀"
    assert e.var == "x"
