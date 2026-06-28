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
