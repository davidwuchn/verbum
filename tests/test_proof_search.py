"""Tests for the goal-directed proof engine (session 228).

The continuation-driven prover: the open goal stack is the reified continuation;
moves intro/exact/apply act on the focused goal; at QED the kernel reconstructs the
proof term via bracket abstraction and verifies it. Soundness is structural — a
non-theorem has no closing derivation, so no move sequence can falsely prove one.

License: MIT
"""

from __future__ import annotations

import pytest

from verbum.lambda_ast import pretty
from verbum.probes.proof_tasks import negatives, positives
from verbum.proof_search import (
    init_state,
    legal_moves,
    make_move,
    reconstruct,
    solve,
    verify_state,
)


def test_engine_proves_every_positive_and_verifies():
    """Auto-solver closes each theorem; the reconstructed term kernel-verifies."""
    for t in positives():
        st = solve(t.prop)
        assert st is not None, f"{t.id}: {t.prop} not solved"
        chk = verify_state(st)
        assert chk.valid, f"{t.id}: reconstructed {pretty(reconstruct(st))} invalid"


def test_engine_cannot_prove_any_negative():
    """Structural soundness: non-theorems have no closing derivation."""
    for t in negatives():
        assert solve(t.prop) is None, f"{t.id}: {t.prop} falsely solved"


def test_intro_then_exact_proves_K():
    st = init_state("A -> B -> A")
    assert legal_moves(st) == ["intro"]
    st = make_move(st, "intro")          # assume h1:A
    st = make_move(st, "intro")          # assume h2:B
    assert "exact h1" in legal_moves(st)
    st = make_move(st, "exact h1")
    assert st.done
    assert verify_state(st).valid
    assert pretty(reconstruct(st)) == "K"


def test_apply_chain_proves_composition():
    """The composition the single-shot prover failed: (A->B)->(B->C)->A->C ⟶ C B."""
    st = init_state("(A -> B) -> (B -> C) -> A -> C")
    for mv in ["intro", "intro", "intro", "apply h2", "apply h1", "exact h3"]:
        st = make_move(st, mv)
    assert st.done
    chk = verify_state(st)
    assert chk.valid
    assert pretty(reconstruct(st)) == "C B"


def test_illegal_moves_raise():
    st = init_state("A -> A")
    with pytest.raises(ValueError):
        make_move(st, "exact h1")        # no hypothesis yet
    st = make_move(st, "intro")
    with pytest.raises(ValueError):
        make_move(st, "intro")           # goal A is not an implication
    with pytest.raises(ValueError):
        make_move(st, "apply h1")        # h1:A cannot reach goal A by application


def test_legal_moves_menu_for_focused_goal():
    st = init_state("A -> (A -> B) -> B")
    st = make_move(st, "intro")          # h1:A
    st = make_move(st, "intro")          # h2:A->B, goal B
    moves = legal_moves(st)
    assert "apply h2" in moves           # h2:A->B reaches B
    assert "exact h1" not in moves       # h1:A is not B


def test_reconstruct_requires_qed():
    st = init_state("A -> A")
    with pytest.raises(ValueError):
        reconstruct(st)                  # still open


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
