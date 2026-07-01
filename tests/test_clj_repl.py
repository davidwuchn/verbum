"""Tests for clj_repl — the model-free parts (oracle, parsing, verify loop).

The network turn is stubbed: we drive `verify_turn` with a fake `_chat` so the
oracle-in-the-loop logic (grade against the kernel, correct once) is tested with
no server. The model IS the evaluator; here we play the model.
"""

from __future__ import annotations

import verbum.clj_repl as repl
from verbum.clj_repl import (
    ModelConfig,
    normalize,
    oracle,
    parse_answer,
    verify_turn,
)
from verbum.lambda_ast import Status
from verbum.probes.harness import split_reasoning_field


# --------------------------------------------------------------------------- #
# oracle — the kernel is ground truth                                          #
# --------------------------------------------------------------------------- #
def test_oracle_int():
    o = oracle("(+ 2 3)")
    assert o.value == "5"
    assert o.status is Status.NORMAL_FORM


def test_oracle_monus_truncates():
    assert oracle("(- 3 5)").value == "0"


def test_oracle_bool():
    assert oracle("(and true (not false))").value == "true"


def test_oracle_false_equals_zero():
    # untyped Church: false ≡ 0 (both are `K I`). primary decodes int-first as "0",
    # but "false" is ALSO acceptable — the type-directedness thesis in miniature.
    o = oracle("(zero? 5)")
    assert o.value == "0"
    assert o.acceptable == frozenset({"0", "false"})


def test_oracle_factorial_via_Y():
    o = oracle("(Y (fn [self] (fn [n] (if (zero? n) 1 (* n (self (dec n)))))) 4)")
    assert o.value == "24"
    assert o.steps > 0


def test_oracle_pair_is_raw():
    # a bare pair does not decode to a scalar → raw combinator string, not a crash
    o = oracle("(cons 7 9)")
    assert o.value  # non-empty; not "5"/"true"
    assert o.value not in ("5", "true", "false")


# --------------------------------------------------------------------------- #
# answer parsing + normalisation                                              #
# --------------------------------------------------------------------------- #
def test_parse_answer_last_wins():
    assert parse_answer("step 1\n=> 3\nrecheck\n=> 5\n") == "5"


def test_parse_answer_none():
    assert parse_answer("I could not evaluate it") is None


def test_normalize():
    assert normalize(" 6 ") == "6"
    assert normalize("`42`.") == "42"
    assert normalize("True") == "true"
    assert normalize("the answer is 8") == "8"
    assert normalize("(cons 7 9)") == "(cons 7 9)"
    assert normalize(None) == ""


# --------------------------------------------------------------------------- #
# verify_turn — oracle-in-the-loop, model stubbed                              #
# --------------------------------------------------------------------------- #
def _stub_cfg() -> ModelConfig:
    return ModelConfig(
        name="stub", endpoint="http://localhost:0", transport="chat",
        reasoning_extract_fn=split_reasoning_field,
    )


class _ScriptedChat:
    """Replaces repl._chat: returns queued (reasoning, content) per call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, client, cfg, messages, n_predict, *, no_think=False):
        self.calls.append([m["role"] for m in messages])
        content = self.replies.pop(0)
        return "reasoning...", content, 42, None


def test_verify_turn_correct_first_try(monkeypatch):
    monkeypatch.setattr(repl, "_chat", _ScriptedChat(["working\n=> 5"]))
    rec = verify_turn(None, _stub_cfg(), "(+ 2 3)")
    assert rec.solved and rec.solved_first_try
    assert rec.oracle.value == "5"
    assert len(rec.attempts) == 1


def test_verify_turn_fixed_by_correction(monkeypatch):
    chat = _ScriptedChat(["=> 6", "sorry, recomputing\n=> 5"])  # wrong then right
    monkeypatch.setattr(repl, "_chat", chat)
    rec = verify_turn(None, _stub_cfg(), "(+ 2 3)", max_retries=1)
    assert rec.solved and not rec.solved_first_try
    assert len(rec.attempts) == 2
    assert rec.attempts[1].role == "retry"
    # the correction turn must carry the assistant answer + a corrective user msg
    assert chat.calls[1] == ["system", "user", "assistant", "user"]


def test_verify_turn_unsolved(monkeypatch):
    monkeypatch.setattr(repl, "_chat", _ScriptedChat(["=> 6", "=> 7"]))
    rec = verify_turn(None, _stub_cfg(), "(+ 2 3)", max_retries=1)
    assert not rec.solved
    assert rec.form in repl._summarize([rec])["unsolved"]


def test_verify_turn_stops_on_transport_error(monkeypatch):
    def boom(client, cfg, messages, n_predict, *, no_think=False):
        return "", "", None, "ConnectionError(...)"

    monkeypatch.setattr(repl, "_chat", boom)
    rec = verify_turn(None, _stub_cfg(), "(+ 2 3)", max_retries=3)
    assert not rec.solved
    assert len(rec.attempts) == 1  # error breaks the loop immediately
    assert rec.attempts[0].error is not None
