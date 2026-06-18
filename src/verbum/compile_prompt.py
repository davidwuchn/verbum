"""Compile prompt contract — the shared prose→surface-FOL prompt (session 241).

THE INVARIANT. The §8 cold-start density probe and the GRPO training loop MUST use the
*identical* prompt, or the measured foothold rate would not reflect the prompts training
actually sees. This module is that single source of truth: the instruction, the held-out
few-shot, the prompt builder, the completion cleaner, and the corpus loader, imported by
both `scripts/experiments/rlvr_coldstart_density.py` and `scripts/experiments/
rlvr_grpo_train.py`.

The task: English sentence → surface logical form (λ ∀ ∃ . → ∧ ∨ ¬, predicate
application `p(a, b)`), the canonical-corpus output notation. Reward is by the kernel
(`verbum.reward`), representation-invariant — any combinator path reducing to the gold
normal form scores; the prompt only has to elicit *a* logical form, not a specific one.

License: MIT.
"""

from __future__ import annotations

import json
from pathlib import Path

__all__ = [
    "FEWSHOT",
    "FEWSHOT_INPUTS",
    "INSTRUCTION",
    "build_prompt",
    "clean_output",
    "load_corpus_rows",
    "to_chat",
]

ROOT = Path(__file__).resolve().parents[2]

INSTRUCTION = (
    "You translate an English sentence into a logical form.\n"
    "Use this notation: predicate application p(a, b); connectives → ∧ ∨ ¬; "
    "quantifiers ∀x. and ∃x. binding a variable x; lowercase tokens for predicates "
    "and named entities.\n"
    "Output ONLY the logical form on a single line, nothing else."
)

# Held-out few-shot demonstrating the notation across categories. Their inputs are
# EXCLUDED from the scored/trained set so density/learning is not inflated by leakage.
FEWSHOT: list[tuple[str, str]] = [
    ("Grace writes helen.", "writes(grace, helen)"),
    ("Kate falls and waits.", "falls(kate) ∧ waits(kate)"),
    ("Every artist knows a baker.", "∀x. artist(x) → knows(x, baker)"),
    ("The dog does not sleep.", "¬sleeps(dog)"),
]
FEWSHOT_INPUTS = {d for d, _ in FEWSHOT}


def build_prompt(sentence: str) -> str:
    """The instruction + few-shot + the target sentence, ending at 'Logical form:'."""
    lines = [INSTRUCTION, ""]
    for d, e in FEWSHOT:
        lines += [f"Sentence: {d}", f"Logical form: {e}", ""]
    lines += [f"Sentence: {sentence}", "Logical form:"]
    return "\n".join(lines)


def to_chat(tok, sentence: str) -> str:
    """`build_prompt(sentence)` as a user turn, with the model's chat template applied.

    THE SINGLE chat-formatted-prompt source. Qwen3 (and most policies here) are chat
    models, so the prompt the model actually sees is the user turn wrapped by the chat
    template + the generation-prompt header. The density probe, the SFT seed, and the
    GRPO loop ALL route through here so they train/measure on the byte-identical prompt
    (a mismatch would mean RL/SFT optimise a different distribution than was measured).
    `tok` is a HuggingFace tokenizer (passed in — no transformers import here).
    """
    msgs = [{"role": "user", "content": build_prompt(sentence)}]
    try:
        return tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except (TypeError, ValueError):
        return tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True)


def clean_output(text: str) -> str:
    """Extract the candidate logical form from a raw generation/completion."""
    t = text.strip()
    if "Logical form:" in t:
        t = t.split("Logical form:")[-1]
    t = t.replace("`", "")
    for line in t.splitlines():
        line = line.strip()
        if line:
            return line.rstrip(".").strip()
    return ""


def load_corpus_rows(
    split: str = "compile-train.canonical.jsonl",
    limit: int | None = None,
    *,
    exclude_fewshot: bool = True,
) -> list[dict]:
    """Load canonical-corpus rows (dicts with input/output/normal_form/…).

    Few-shot inputs are excluded by default (no leakage); `limit` truncates after.
    """
    path = ROOT / "data" / split
    rows = [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]
    if exclude_fewshot:
        rows = [r for r in rows if r["input"] not in FEWSHOT_INPUTS]
    return rows[:limit] if limit else rows
