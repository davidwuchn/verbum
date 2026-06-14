"""Tests for the Curry-Howard proof kernel (session 228).

proof-check ≡ type-check; the combinator basis is a Hilbert proof calculus; the
sound-basis gate is the consistency firewall (Y = recursion = inconsistency). These
tests pin the 100% kernel floor and the soundness boundary.

License: MIT
"""

from __future__ import annotations

import pytest

from verbum.lambda_ast import parse, typecheck
from verbum.probes.proof_tasks import negatives, positives, proof_tasks
from verbum.proof_kernel import Verdict, check_proof, parse_prop, pretty_prop

# Tempting sound terms a checker must never accept for a non-theorem.
_TEMPTING = ["I", "K", "S", "B", "C", "W", "D", "K I", "C I", "S K K", "B B", "B K K"]


def test_every_positive_ref_proof_is_valid():
    """The 100% floor: each positive's reference proof type-checks at the goal."""
    for t in positives():
        r = check_proof(t.ref_proof, t.prop)
        assert r.valid, f"{t.id}: {t.ref_proof} did not prove {t.prop} ({r.verdict})"
        assert r.verdict == Verdict.VALID


def test_no_negative_is_falsely_proved():
    """Soundness: no non-theorem is proved by any tempting sound term."""
    for t in negatives():
        for term in _TEMPTING:
            r = check_proof(term, t.prop)
            assert not r.valid, f"{term} falsely proved non-theorem {t.prop}"


def test_axioms():
    assert check_proof("I", "A -> A").valid
    assert check_proof("K", "A -> B -> A").valid
    assert check_proof("S", "(A -> B -> C) -> (A -> B) -> A -> C").valid
    assert check_proof("B", "(B -> C) -> (A -> B) -> A -> C").valid
    assert check_proof("C", "(A -> B -> C) -> B -> A -> C").valid
    assert check_proof("W", "(A -> A -> B) -> A -> B").valid


def test_k_does_not_prove_identity():
    """K : A->B->A is well-typed but not a proof of A->A (type mismatch)."""
    r = check_proof("K", "A -> A")
    assert not r.valid
    assert r.verdict == Verdict.TYPE_MISMATCH
    assert r.well_typed


def test_self_application_is_ill_typed():
    """M = λx.xx has no simple type ⇒ never a proof (occurs-check)."""
    r = check_proof("M", "A -> A")
    assert not r.valid
    assert r.verdict == Verdict.ILL_TYPED


def test_open_term_rejected():
    """A term with free atoms is an open hypothesis, not a closed proof."""
    r = check_proof("f", "A -> A")
    assert not r.valid
    assert r.verdict == Verdict.OPEN_TERM


def test_none_is_a_declination():
    r = check_proof("none", "A")
    assert r.verdict == Verdict.NONE
    assert not r.valid


def test_consistency_firewall_rejects_Y():
    """The load-bearing point: Y TYPES (a->a)->a, but admitting it is unsound."""
    y_cat = typecheck(parse("Y")).cat
    assert pretty_prop(y_cat) == "(α -> α) -> α"  # noqa: RUF001  (real kernel output)
    r = check_proof("Y", "(A -> A) -> A")                 # the sound gate must reject
    assert not r.valid
    assert r.verdict == Verdict.UNSOUND_RECURSION


def test_y_trap_is_a_real_nontheorem():
    """(A->A)->A is in the negatives, flagged y_trap, and unprovable soundly."""
    y_trap = [t for t in negatives() if t.y_trap]
    assert len(y_trap) == 1
    assert y_trap[0].prop == "(A -> A) -> A"


def test_prop_parser_roundtrip():
    for s in ["A -> A", "A -> B -> A", "(A -> B) -> A -> B",
              "(A -> B -> C) -> (A -> B) -> A -> C"]:
        assert pretty_prop(parse_prop(s)) == s


def test_running_the_proof_reaches_normal_form():
    """The proof term reduces (cut-elimination) to a recorded normal form."""
    r = check_proof("C B", "(A -> B) -> (B -> C) -> A -> C")
    assert r.valid
    assert r.normal_form is not None
    assert r.status == "normal_form"


def test_taskset_shape():
    tasks = proof_tasks()
    assert len(positives()) >= 10
    assert len(negatives()) >= 6
    assert all(t.ref_proof is not None for t in positives())
    assert all(t.ref_proof is None for t in negatives())
    assert len(tasks) == len(positives()) + len(negatives())


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
