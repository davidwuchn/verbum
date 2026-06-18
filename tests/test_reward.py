"""Tests for verbum.reward — the kernel as a verifiable RLVR reward (session 241).

Covers: reduction-equality + representation invariance (R_parent), the multi-channel
decomposition, the potential-based shaping telescoping invariance (the load-bearing
guarantee), and the fired_sequence-aligned reduction-tree process reward.
"""

from __future__ import annotations

import pytest

from verbum.lambda_ast import parse, reduce
from verbum.reward import (
    RewardConfig,
    channels,
    dense_reward,
    potential,
    reward,
    shaped_return,
    shaping,
    tree_process_reward,
    verifiable_reward,
)

APP = RewardConfig(parse="applicative")
SURF = RewardConfig(parse="surface")


# --------------------------------------------------------------------------- #
# R_parent — reduction-equality outcome reward                                #
# --------------------------------------------------------------------------- #
def test_gold_surface_output_scores_one():
    out = "∀x. artist(x) → knows(x, baker)"
    gold_nf = "forall (S (B implies artist) (C knows baker))"
    r = reward(out, gold_nf, SURF)
    assert r.reward == 1.0
    assert r.channels.reduces_correct
    assert r.dense == pytest.approx(1.0)


def test_wrong_output_scores_zero_but_still_parses():
    out = "∀x. artist(x) → knows(x, oscar)"  # wrong arg
    gold_nf = "forall (S (B implies artist) (C knows baker))"
    r = reward(out, gold_nf, SURF)
    assert r.reward == 0.0
    assert not r.channels.reduces_correct
    assert r.channels.parsed and r.channels.well_typed  # a wrong, not a malformed, term


def test_unparseable_output_parsed_false():
    r = reward("∀x. artist(", "forall (S (B implies artist) (C knows baker))", SURF)
    assert not r.channels.parsed
    assert r.reward == 0.0
    assert r.channels.error is not None


def test_representation_invariance_b_form_and_direct():
    """`B f g x` and `f (g x)` both reduce to the same NF → both score 1.0."""
    gold = "f (g x)"
    assert verifiable_reward("B f g x", gold, APP) == 1.0
    assert verifiable_reward("f (g x)", gold, APP) == 1.0


def test_representation_invariance_via_term_input():
    """channels accepts a Term directly (a reduction-trace state)."""
    t = parse("B f g x")
    ch = channels(t, "f (g x)", APP)
    assert ch.reduces_correct


# --------------------------------------------------------------------------- #
# Multi-channel decomposition                                                 #
# --------------------------------------------------------------------------- #
def test_channels_decomposition_all_in_unit_interval():
    ch = channels("B f g x", "f (g x)", APP)
    for v in ch.as_scores().values():
        assert 0.0 <= v <= 1.0


def test_dense_reward_zero_weights_is_zero():
    ch = channels("B f g x", "f (g x)", APP)
    assert dense_reward(ch, {}) == 0.0


def test_dense_reward_anchor_only_tracks_correctness():
    gold = "f (g x)"
    ch_ok = channels("B f g x", gold, APP)
    ch_no = channels("g (f x)", gold, APP)
    w = {"reduces_correct": 1.0}
    assert dense_reward(ch_ok, w) == 1.0
    assert dense_reward(ch_no, w) == 0.0


# --------------------------------------------------------------------------- #
# §4a — potential-based shaping invariance (the load-bearing guarantee)        #
# --------------------------------------------------------------------------- #
def test_potential_bounded_unit_interval():
    gold = "f (g x)"
    for s in ["B f g x", "f (g x)", "g (f x)", "garbage ((("]:
        assert 0.0 <= potential(s, gold, APP) <= 1.0


def test_potential_unparseable_is_zero():
    assert potential("garbage (((", "f (g x)", APP) == 0.0


@pytest.mark.parametrize("gamma", [1.0, 0.99, 0.9, 0.5, 0.0])
def test_shaping_sum_telescopes_to_endpoints(gamma: float):
    """Σ_t γ^t (γΦ(s_{t+1}) − Φ(s_t)) == γ^T·Φ(s_T) − Φ(s_0).

    THE invariance: the shaping channel depends only on the endpoints, so any over-read
    in Φ along the path cancels and cannot move the optimum (Ng-Harada-Russell 1999).
    """
    gold = "f (g x)"
    states = list(reduce(parse("B f g x")).trace)  # s0 … sT (a multi-step trajectory)
    assert len(states) >= 2
    sr = shaped_return(states, gold, APP, gamma=gamma)
    assert sr.shaping_sum == pytest.approx(sr.telescoped, abs=1e-9)


def test_shaping_single_transition_is_potential_difference():
    gold = "f (g x)"
    f = shaping("B f g x", "f (g x)", gold, APP, gamma=0.9)
    expected = 0.9 * potential("f (g x)", gold, APP) - potential("B f g x", gold, APP)
    assert f == pytest.approx(expected, abs=1e-12)


def test_shaped_return_outcome_is_the_anchor():
    gold = "f (g x)"
    states = list(reduce(parse("B f g x")).trace)
    assert shaped_return(states, gold, APP).outcome == 1.0
    wrong = list(reduce(parse("C f g x")).trace)  # reduces to f x g ≠ f (g x)
    assert shaped_return(wrong, gold, APP).outcome == 0.0


def test_shaped_return_empty_states_raises():
    with pytest.raises(ValueError):
        shaped_return([], "f (g x)", APP)


# --------------------------------------------------------------------------- #
# §4c — reduction-tree process reward                                          #
# --------------------------------------------------------------------------- #
def test_tree_process_reward_aligned_to_fired_sequence():
    """One process step per fired combinator, in reduction order, root = outcome.

    B K I x y -> K (I x) y [B] -> I x [K] -> x [I]; certified trace == [B, K, I].
    """
    from verbum.lambda_ast import fired_sequence

    tr = tree_process_reward("B K I x y", "x", APP)
    seq = fired_sequence(parse("B K I x y"))
    assert seq == ["B", "K", "I"]
    assert [s.opcode for s in tr.steps] == seq
    assert len(tr.potentials) == len(tr.steps) + 1
    assert tr.outcome == 1.0


def test_tree_process_reward_correct_outcome():
    # B f g x -> f (g x); one B step.
    tr = tree_process_reward("B f g x", "f (g x)", APP)
    assert tr.outcome == 1.0
    assert [s.opcode for s in tr.steps] == ["B"]


def test_tree_process_reward_normal_form_candidate_has_no_steps():
    """A candidate already in NF has an empty reduction tree (just the root)."""
    tr = tree_process_reward("f (g x)", "f (g x)", APP)
    assert tr.steps == []
    assert tr.outcome == 1.0
    assert tr.potentials == [potential("f (g x)", "f (g x)", APP)]
