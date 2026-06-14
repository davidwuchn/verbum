"""Tests for bracket abstraction — round-trip with the kernel is the contract."""

from __future__ import annotations

import random

from verbum.lambda_ast import Comb, parse, pretty
from verbum.lambda_compile import (
    abstract,
    compile_expr,
    free_vars,
    occurs,
    roundtrip,
)


def comp(variables, s):
    return pretty(compile_expr(variables, parse(s)))


# --------------------------------------------------------------------------- #
# known abstractions                                                          #
# --------------------------------------------------------------------------- #
def test_identity():
    assert abstract("x", parse("x")) == Comb("I")


def test_constant_K():
    assert comp(["x"], "a") == "K a"


def test_eta():
    assert comp(["x"], "f x") == "f"


def test_compose_is_B():
    assert comp(["x"], "f (g x)") == "B f g"


def test_flip_is_C():
    assert comp(["x", "y"], "f y x") == "C f"


def test_dup_uses_S():
    # [x](f x x) = S f I  ;  S f I x → f x (I x) → f x x
    assert comp(["x"], "f x x") == "S f I"


def test_free_vars_and_occurs():
    t = parse("f (g x) y")
    assert free_vars(t) == {"f", "g", "x", "y"}
    assert occurs("x", t)
    assert not occurs("z", t)


# --------------------------------------------------------------------------- #
# round-trip: the kernel certifies the compiler                              #
# --------------------------------------------------------------------------- #
def test_roundtrip_known():
    assert roundtrip(["x"], "f (g x)")
    assert roundtrip(["x", "y"], "f y x")
    assert roundtrip(["x"], "f x x")
    assert roundtrip(["x", "y", "z"], "x (y z) (z x)")


def _rand_expr(rng, atoms, depth):
    if depth <= 0 or rng.random() < 0.4:
        return parse(rng.choice(atoms))
    from verbum.lambda_ast import App

    return App(_rand_expr(rng, atoms, depth - 1), _rand_expr(rng, atoms, depth - 1))


def test_roundtrip_property():
    """Random logical-form exprs must round-trip: reduce(compile(vs,e).vs) == e."""
    rng = random.Random(0)
    variables = ["x", "y", "z"]
    atoms = ["f", "g", "h", "a", "b", *variables]
    fails = []
    for _ in range(400):
        nvars = rng.randint(1, 3)
        vs = variables[:nvars]
        e = _rand_expr(rng, atoms, rng.randint(1, 4))
        if not roundtrip(vs, e):
            fails.append((vs, pretty(e)))
    assert not fails, f"{len(fails)} round-trip failures, e.g. {fails[:3]}"
