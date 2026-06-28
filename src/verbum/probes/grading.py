"""Canonical P(λ) grading — the single source of truth for compiler registers.

The "did the lambda compiler fire / is it well-formed" question is actually
**four named registers** (AGENTS.md S5 λ measure — name the register before
building the probe). Ordered broad → strict:

  - ``emits_formal``              binder OR pred-app   — "did the compiler fire
                                                         at all" (broadest;
                                                         catches atomic
                                                         ``runs(dog)`` a
                                                         binder-only register
                                                         false-misses).
  - ``lambda_binder_any_style``   any λ/∀/∃ binder      — THE nucleus-comparable
                                                         P(λ) (reference 0.907).
  - ``lenient_lambda``            binder AND pred-app  — a *stricter* lenient;
                                                         under-counts Church
                                                         juxtaposition
                                                         ``λx. f x`` → NOT the
                                                         nucleus number.
  - ``kernel_valid``              ``to_kernel`` parses  — canonical
                                                         well-formedness (STRICT;
                                                         rejects richer-than-toy
                                                         FOL — notation ≠
                                                         failure).

This module replaces the three divergent P(λ) metrics that drifted across the
repo (regex-binder vs char-ratio vs ``instrument._detect_lambda``). One model +
one probe set → one P(λ) **per named register**. ``kernel_valid`` wraps
``verbum.lambda_surface.to_kernel`` — the single strict validator — and never
re-implements parsing.

The register-mismatch trap (s253/s254, λ measure): the nucleus-comparable
headline is ``lambda_binder_any_style`` (vibe 0.925 ≈ nucleus 0.907), NOT
``lenient_lambda`` (vibe 0.875). Citing the latter as "the P(λ)" would
false-flag a regression. They are distinct named functions here so the
conflation cannot recur.

License: MIT.
"""

from __future__ import annotations

import re
from typing import Any

from verbum.lambda_surface import to_kernel

# nucleus baseline P(λ), cited once (the cross-model reference point).
NUCLEUS_REFERENCE_P_LAMBDA = 0.907

# A lambda/quantifier binder token: lambda, forall, exists, iota, the Coptic
# lambda variant, or a backslash-style binder. Plus a predicate-style
# application f(...). Char class kept verbatim from the s253/s254 harnesses.
_LAMBDA_TOK = re.compile(r"[λ∀∃ιⲗ\\]")
_PRED_APP = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\(")

# The four register names, broad → strict (stable ordering for aggregation).
REGISTERS = (
    "emits_formal",
    "lambda_binder_any_style",
    "lenient_lambda",
    "kernel_valid",
)


def final_answer(text: str) -> str:
    """Extract the model's final answer line.

    Strips a reasoning chain (everything up to and including ``</think>`` if
    present — for completion transports that return the raw chain inline; chat
    transports that split ``reasoning_content`` server-side already pass clean
    content) and returns the first non-empty line, de-fenced and stripped.
    """
    tail = text.split("</think>")[-1] if "</think>" in text else text
    for line in tail.strip().splitlines():
        s = line.strip().strip("`").strip()
        if s:
            return s
    return tail.strip()


def emits_formal(expr: str) -> bool:
    """Broadest register: any λ/∀/∃ binder OR a predicate application.

    "Did the compiler fire at all." Catches atomic predications (``runs(dog)``)
    that the binder-requiring registers false-miss.
    """
    return bool(_LAMBDA_TOK.search(expr) or _PRED_APP.search(expr))


def lambda_binder_any_style(expr: str) -> bool:
    """The nucleus-comparable P(λ): ANY λ/∀/∃ binder, regardless of app style.

    This is the headline P(λ) (reference 0.907). Counts Church juxtaposition
    (``λx. f x``) that ``lenient_lambda`` drops.
    """
    return bool(_LAMBDA_TOK.search(expr))


def lenient_lambda(expr: str) -> bool:
    """Stricter lenient: a binder AND a predicate-style application f(...).

    Under-counts Church juxtaposition — NOT the nucleus-comparable number.
    """
    return bool(_LAMBDA_TOK.search(expr) and _PRED_APP.search(expr))


def kernel_valid(expr: str) -> bool:
    """STRICT: ``verbum.lambda_surface.to_kernel`` parses the expression.

    Canonical well-formedness. Wraps the single strict validator; never
    re-implements parsing.
    """
    try:
        to_kernel(expr)
        return True
    except Exception:
        return False


def grade(expr: str) -> dict[str, bool]:
    """All four registers for one final answer, keyed by register name."""
    return {
        "emits_formal": emits_formal(expr),
        "lambda_binder_any_style": lambda_binder_any_style(expr),
        "lenient_lambda": lenient_lambda(expr),
        "kernel_valid": kernel_valid(expr),
    }


# ── reasoning-answer grading (lambda-as-pre-thinking experiment) ─────────────

_ANSWER_MARKER = re.compile(r"answer\s*[:=]\s*(.+)", re.IGNORECASE)
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?(?:\s*/\s*\d+)?")
_WORD = re.compile(r"[A-Za-z]+")
_TRUE = {"yes", "true", "valid", "correct", "y"}
_FALSE = {"no", "false", "invalid", "incorrect", "n"}


def extract_final(text: str) -> str:
    """The answer to grade: text after the last ``ANSWER:`` marker if present,
    else the last non-empty, de-fenced line."""
    if not text:
        return ""
    markers = _ANSWER_MARKER.findall(text)
    if markers:
        return markers[-1].strip().strip("`*. ").strip()
    for line in reversed(text.splitlines()):
        s = line.strip().strip("`*").strip()
        if s:
            return s
    return text.strip()


def _to_number(s: str) -> float | None:
    # Last number in the string — the answer usually trails the working
    # ("8 * 5 = 40" → 40; "9/12 = 75 percent" → 75).
    matches = _NUMBER.findall(s.replace("$", ""))
    if not matches:
        return None
    tok = matches[-1].replace(",", "").replace(" ", "")
    try:
        if "/" in tok:
            num, den = tok.split("/")
            return float(num) / float(den)
        return float(tok)
    except (ValueError, ZeroDivisionError):
        return None


def check_answer(final: str, ground_truth: str, answer_type: str) -> bool:
    """Objectively grade a reasoning answer against ground truth.

    ``numeric`` — last number in the answer == gt (tolerance 1e-6; handles
    ``$``, commas, simple ``a/b`` fractions).
    ``boolean`` — yes/true/valid family vs no/false/invalid family.
    ``token``   — the gt word appears among the answer's words (case-insensitive).
    """
    final = (final or "").strip()
    if not final:
        return False
    if answer_type == "numeric":
        a, b = _to_number(final), _to_number(ground_truth)
        return a is not None and b is not None and abs(a - b) < 1e-6
    if answer_type == "boolean":
        words = {w.lower() for w in _WORD.findall(final)}
        gt = ground_truth.strip().lower()
        want_true = gt in _TRUE
        has_true = bool(words & _TRUE)
        has_false = bool(words & _FALSE)
        if has_true == has_false:  # neither or both → ambiguous → wrong
            return False
        return has_true if want_true else has_false
    if answer_type == "token":
        words = {w.lower() for w in _WORD.findall(final)}
        return ground_truth.strip().lower() in words
    return False


def aggregate_by_category(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate graded rows into overall + per-category P(λ) per register.

    Each row must carry a ``category`` and the four boolean register fields
    (as produced by :func:`grade`). Returns::

        {
          "n": int,
          "overall": {register: rate, ...},
          "by_category": {cat: {"n": int, register: rate, ...}, ...},
        }
    """
    n = len(rows)
    overall = {r: 0 for r in REGISTERS}
    by_cat: dict[str, dict[str, int]] = {}
    for row in rows:
        cat = row.get("category", "?")
        c = by_cat.setdefault(cat, {"n": 0, **{r: 0 for r in REGISTERS}})
        c["n"] += 1
        for r in REGISTERS:
            v = int(bool(row.get(r)))
            overall[r] += v
            c[r] += v

    def _rates(counts: dict[str, int], denom: int) -> dict[str, float]:
        return {r: round(counts[r] / denom, 4) if denom else 0.0 for r in REGISTERS}

    return {
        "n": n,
        "overall": _rates(overall, n),
        "by_category": {
            cat: {"n": c["n"], **_rates(c, c["n"])}
            for cat, c in sorted(by_cat.items())
        },
    }
