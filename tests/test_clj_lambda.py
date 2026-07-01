"""Tests for clj_lambda — the Clojure-subset interpreter over the verbum kernel.

The contract: a Clojure form compiles to a closed combinator term and reduces in the
SAME kernel (`lambda_ast`) that grades the compiler, decoding back to a Python value.
"""

from __future__ import annotations

import pytest

from verbum.clj_lambda import (
    PRELUDE,
    Sym,
    Vector,
    church,
    compile_clj,
    read,
    reduce_clj,
    run,
)
from verbum.lambda_ast import Status


# --------------------------------------------------------------------------- #
# reader                                                                       #
# --------------------------------------------------------------------------- #
def test_read_int():
    assert read("42") == 42


def test_read_symbol():
    assert read("foo") == Sym("foo")


def test_read_nested_list():
    assert read("(+ 1 (* 2 3))") == [Sym("+"), 1, [Sym("*"), 2, 3]]


def test_read_vector_is_vector():
    form = read("(fn [x] x)")
    assert isinstance(form[1], Vector)
    assert form[1] == [Sym("x")]


def test_read_commas_and_comments():
    assert read("(+ 1, 2) ; trailing") == [Sym("+"), 1, 2]


def test_read_trailing_tokens_raises():
    with pytest.raises(SyntaxError):
        read("(+ 1 2) 3")


# --------------------------------------------------------------------------- #
# arithmetic (Church numerals, reduced in the kernel)                          #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("(+ 2 3)", 5),
        ("(* 3 4)", 12),
        ("(inc 6)", 7),
        ("(dec 5)", 4),
        ("(- 7 3)", 4),
        ("(+ (* 2 3) 4)", 10),
        ("0", 0),
        ("7", 7),
    ],
)
def test_arithmetic(src, expected):
    assert run(src) == expected


# --------------------------------------------------------------------------- #
# booleans + if (church-encoded, lazy branch via normal-order reduction)       #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("(zero? 0)", True),
        ("(zero? 5)", False),
        ("(not true)", False),
        ("(not false)", True),
        ("(and true true)", True),
        ("(and true false)", False),
        ("(or false false)", False),
        ("(or false true)", True),
    ],
)
def test_booleans(src, expected):
    assert run(src, kind="bool") == expected


def test_if_selects_branch():
    assert run("(if true 1 2)") == 1
    assert run("(if false 1 2)") == 2
    assert run("(if (zero? 0) 10 20)") == 10


# --------------------------------------------------------------------------- #
# fn / let / higher-order                                                       #
# --------------------------------------------------------------------------- #
def test_fn_application():
    assert run("((fn [x] (+ x 1)) 6)") == 7


def test_fn_multi_arg():
    assert run("((fn [x y] (+ x y)) 4 5)") == 9


def test_let():
    assert run("(let [x 4 y 3] (+ x y))") == 7


def test_let_sequential_binding():
    # y sees x
    assert run("(let [x 2 y (* x 3)] (+ x y))") == 8


def test_higher_order():
    # apply f twice
    assert run("((fn [f] (f (f 2))) (fn [n] (+ n 3)))") == 8


# --------------------------------------------------------------------------- #
# pairs (church-encoded data)                                                   #
# --------------------------------------------------------------------------- #
def test_pair_first_rest():
    assert run("(first (cons 7 9))") == 7
    assert run("(rest (cons 7 9))") == 9


# --------------------------------------------------------------------------- #
# recursion via the kernel's own Y combinator                                  #
# --------------------------------------------------------------------------- #
FAC = "(Y (fn [self] (fn [n] (if (zero? n) 1 (* n (self (dec n)))))))"


@pytest.mark.parametrize(("k", "expected"), [(0, 1), (1, 1), (2, 2), (3, 6), (4, 24)])
def test_factorial_via_Y(k, expected):
    assert run(f"({FAC} {k})") == expected


# --------------------------------------------------------------------------- #
# compilation contract: closed combinator terms, kernel round-trip             #
# --------------------------------------------------------------------------- #
def test_compiles_to_closed_combinator_term():
    from verbum.lambda_compile import free_vars

    # a program with no free variables must compile to a term with no Atom leaves
    term = compile_clj("(+ 2 3)")
    assert free_vars(term) == set()


def test_church_zero_and_succ():
    from verbum.lambda_ast import pretty

    assert pretty(church(0)) == "K I"  # λf.λx.x  ==  K I


def test_reduce_reaches_normal_form():
    red = reduce_clj("(+ 2 3)")
    assert red.status is Status.NORMAL_FORM


def test_unbound_symbol_raises():
    with pytest.raises(NameError):
        run("(frobnicate 1)")


def test_prelude_entries_are_closed():
    from verbum.lambda_compile import free_vars

    for name, term in PRELUDE.items():
        assert free_vars(term) == set(), f"prelude {name!r} is not closed"
