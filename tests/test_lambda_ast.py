"""Tests for the typed CCG combinator reducer (lambda_ast)."""

from __future__ import annotations

from verbum.lambda_ast import (
    App,
    Atom,
    CAtom,
    Comb,
    Status,
    normal_form,
    parse,
    pretty,
    reduce,
    trace_record,
    typecheck,
    verify,
)


def nf(s: str) -> str:
    return pretty(normal_form(parse(s)))


# --------------------------------------------------------------------------- #
# parse / pretty                                                              #
# --------------------------------------------------------------------------- #
def test_parse_roundtrip():
    for s in ["K x y", "B f g x", "S (K) (K) x", "f (g x)", "Y f"]:
        assert pretty(parse(s)) == pretty(parse(pretty(parse(s))))


def test_parse_application_is_left_assoc():
    assert parse("a b c") == App(App(Atom("a"), Atom("b")), Atom("c"))


def test_parse_combinator_vs_atom():
    assert parse("K") == Comb("K")
    assert parse("foo") == Atom("foo")


# --------------------------------------------------------------------------- #
# reduction rules                                                             #
# --------------------------------------------------------------------------- #
def test_core_rules():
    assert nf("I x") == "x"
    assert nf("K x y") == "x"
    assert nf("C f x y") == "f y x"
    assert nf("B f g x") == "f (g x)"
    assert nf("S f g x") == "f x (g x)"
    assert nf("W f x") == "f x x"
    assert nf("D f g h x") == "f (g (h x))"


def test_skk_is_identity():
    assert nf("S K K x") == "x"


def test_composite_reduction():
    # B K I x y  →  K (I x) y  →  I x  →  x
    assert nf("B K I x y") == "x"


def test_normal_form_status():
    red = reduce(parse("K a b"))
    assert red.status is Status.NORMAL_FORM
    assert pretty(red.normal_form) == "a"
    assert red.trace[0] == parse("K a b")
    assert red.trace[-1] == red.normal_form


# --------------------------------------------------------------------------- #
# limits — divergence + term growth                                          #
# --------------------------------------------------------------------------- #
def test_Y_diverges():
    red = reduce(parse("Y f"), max_steps=50)
    assert red.status is Status.DIVERGED


def test_fixpoint_loop_diverges_constant_size():
    # W W W → W W W → ... (a constant-size loop)
    red = reduce(parse("W W W"), max_steps=20)
    assert red.status is Status.DIVERGED


def test_size_exceeded_is_the_growth_limit():
    red = reduce(parse("Y x"), max_steps=10_000, max_size=24)
    assert red.status is Status.SIZE_EXCEEDED


def test_whnf_before_normal_form():
    red = reduce(parse("K a b"))
    assert red.whnf_step is not None


# --------------------------------------------------------------------------- #
# typing — the S2 check, first-class                                          #
# --------------------------------------------------------------------------- #
def test_well_typed_combinators():
    for s in ["I", "K", "B", "C", "S", "W", "D", "Y"]:
        assert typecheck(parse(s)).ok, s


def test_skk_well_typed():
    assert typecheck(parse("S K K")).ok


def test_M_is_reducible_but_not_typable():
    # operationally fine ...
    assert nf("M x") == "x x"
    # ... but self-application has no simple type (occurs-check) — the limit demo
    assert not typecheck(parse("M")).ok
    assert not typecheck(parse("M x")).ok


def test_type_mismatch_is_caught():
    # an atom forced into incompatible categories
    env = {"j": CAtom("NP"), "s": CAtom("S")}
    res = typecheck(parse("K j s"), env)
    assert res.ok  # K just drops s — fine
    # forcing an atom (NP) into function position: I j : NP, applied to j:NP -> stuck
    bad = typecheck(parse("I j j"), env)
    assert not bad.ok


def test_derivation_is_inspectable():
    res = typecheck(parse("B f g x"))
    assert res.ok
    assert res.derivation  # per-App categories recorded
    assert res.cat is not None


# --------------------------------------------------------------------------- #
# verify + oracle record                                                      #
# --------------------------------------------------------------------------- #
def test_verify():
    assert verify("K x y", "x")
    assert verify("S K K x", "x")
    assert not verify("K x y", "y")
    assert not verify("Y f", "f")  # never reaches normal form


def test_trace_record():
    rec = trace_record("K a b")
    assert rec["normal_form"] == "a"
    assert rec["status"] == "normal_form"
    assert rec["well_typed"] is True
    assert rec["trace"][0] == "K a b"
    assert rec["category"] is not None


def test_trace_record_marks_ill_typed():
    rec = trace_record("M x")
    assert rec["well_typed"] is False
    assert rec["type_error"] is not None
    assert rec["normal_form"] == "x x"  # still reduces
