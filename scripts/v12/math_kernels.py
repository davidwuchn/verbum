"""Math kernel functions — deterministic, frozen, exact.

These are CODE, not weights. They execute. They don't learn.
They don't approximate. They can't be unlearned.

The dispatch (ternary plates + mirrors) learns WHEN to use these.
The extractor head learns HOW to parse operands from hidden state.
The kernel itself is always correct.

Usage:
    from math_kernels import MATH_KERNELS, apply_kernel
    
    result = apply_kernel("ADD", 23.0, 47.0)  # → 70.0
    result = apply_kernel("MUL", 6.0, 9.0)    # → 54.0
    result = apply_kernel("DIV", 7.0, 0.0)    # → NaN (safe)

License: MIT
"""

from __future__ import annotations

import math
from typing import Callable


# ══════════════════════════════════════════════════════════════════════
# Kernel functions — pure, deterministic, frozen
# ══════════════════════════════════════════════════════════════════════

def _add(a: float, b: float) -> float:
    """Addition. Always exact."""
    return a + b


def _sub(a: float, b: float) -> float:
    """Subtraction. Always exact."""
    return a - b


def _mul(a: float, b: float) -> float:
    """Multiplication. Always exact."""
    return a * b


def _div(a: float, b: float) -> float:
    """Division. Returns NaN for division by zero (safe, no crash)."""
    if b == 0:
        return float('nan')
    return a / b


def _mod(a: float, b: float) -> float:
    """Modulo. Returns NaN for mod by zero."""
    if b == 0:
        return float('nan')
    return a % b


def _pow(a: float, b: float) -> float:
    """Exponentiation. Handles edge cases safely."""
    try:
        result = a ** b
        if isinstance(result, complex):
            return float('nan')  # negative base with fractional exponent
        return float(result)
    except (OverflowError, ValueError):
        return float('nan')


def _cmp(a: float, b: float) -> float:
    """Compare. Returns -1 (a<b), 0 (a==b), +1 (a>b)."""
    if a < b:
        return -1.0
    elif a > b:
        return 1.0
    return 0.0


def _eq(a: float, b: float) -> float:
    """Equality. Returns 1.0 (true) or 0.0 (false)."""
    return 1.0 if a == b else 0.0


def _sqrt(a: float, _b: float = 0.0) -> float:
    """Square root. Returns NaN for negative input."""
    if a < 0:
        return float('nan')
    return math.sqrt(a)


def _log(a: float, _b: float = 0.0) -> float:
    """Natural logarithm. Returns NaN for non-positive input."""
    if a <= 0:
        return float('nan')
    return math.log(a)


def _abs(a: float, _b: float = 0.0) -> float:
    """Absolute value."""
    return abs(a)


def _round(a: float, b: float = 0.0) -> float:
    """Round a to b decimal places."""
    return round(a, int(b))


def _floor(a: float, _b: float = 0.0) -> float:
    """Floor (round down)."""
    return float(math.floor(a))


def _ceil(a: float, _b: float = 0.0) -> float:
    """Ceiling (round up)."""
    return float(math.ceil(a))


def _max(a: float, b: float) -> float:
    """Maximum of two values."""
    return max(a, b)


def _min(a: float, b: float) -> float:
    """Minimum of two values."""
    return min(a, b)


def _neg(a: float, _b: float = 0.0) -> float:
    """Negate."""
    return -a


# ══════════════════════════════════════════════════════════════════════
# Registry — maps kernel names to functions
# ══════════════════════════════════════════════════════════════════════

MATH_KERNELS: dict[str, Callable[[float, float], float]] = {
    # Binary arithmetic
    "ADD": _add,
    "SUB": _sub,
    "MUL": _mul,
    "DIV": _div,
    "MOD": _mod,
    "POW": _pow,
    # Comparison
    "CMP": _cmp,
    "EQ": _eq,
    "MAX": _max,
    "MIN": _min,
    # Unary (b ignored)
    "SQRT": _sqrt,
    "LOG": _log,
    "ABS": _abs,
    "NEG": _neg,
    "FLOOR": _floor,
    "CEIL": _ceil,
    # Rounding (b = decimal places)
    "ROUND": _round,
}

# Operation metadata for training data generation
MATH_KERNEL_INFO: dict[str, dict] = {
    "ADD": {"arity": 2, "symbol": "+", "example": "23 + 47 = 70"},
    "SUB": {"arity": 2, "symbol": "-", "example": "100 - 37 = 63"},
    "MUL": {"arity": 2, "symbol": "×", "example": "6 × 9 = 54"},
    "DIV": {"arity": 2, "symbol": "÷", "example": "100 ÷ 4 = 25"},
    "MOD": {"arity": 2, "symbol": "%", "example": "17 % 5 = 2"},
    "POW": {"arity": 2, "symbol": "^", "example": "2 ^ 10 = 1024"},
    "CMP": {"arity": 2, "symbol": "cmp", "example": "5 cmp 3 = 1"},
    "EQ":  {"arity": 2, "symbol": "==", "example": "4 == 4 = 1"},
    "MAX": {"arity": 2, "symbol": "max", "example": "max(3, 7) = 7"},
    "MIN": {"arity": 2, "symbol": "min", "example": "min(3, 7) = 3"},
    "SQRT": {"arity": 1, "symbol": "√", "example": "√144 = 12"},
    "LOG": {"arity": 1, "symbol": "ln", "example": "ln(e) = 1"},
    "ABS": {"arity": 1, "symbol": "|·|", "example": "|-5| = 5"},
    "NEG": {"arity": 1, "symbol": "-", "example": "-(7) = -7"},
    "FLOOR": {"arity": 1, "symbol": "⌊·⌋", "example": "⌊3.7⌋ = 3"},
    "CEIL": {"arity": 1, "symbol": "⌈·⌉", "example": "⌈3.2⌉ = 4"},
    "ROUND": {"arity": 2, "symbol": "round", "example": "round(3.14159, 2) = 3.14"},
}


def apply_kernel(name: str, a: float, b: float = 0.0) -> float:
    """Apply a math kernel by name. Returns NaN if kernel not found."""
    fn = MATH_KERNELS.get(name)
    if fn is None:
        return float('nan')
    return fn(a, b)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    tests = [
        # (kernel, a, b, expected)
        ("ADD", 23, 47, 70),
        ("ADD", -5, 3, -2),
        ("ADD", 0.1, 0.2, 0.3),
        ("SUB", 100, 37, 63),
        ("SUB", 5, 8, -3),
        ("MUL", 6, 9, 54),
        ("MUL", -3, 7, -21),
        ("MUL", 0, 999, 0),
        ("DIV", 100, 4, 25),
        ("DIV", 7, 2, 3.5),
        ("DIV", 1, 3, 1/3),
        ("MOD", 17, 5, 2),
        ("MOD", 100, 7, 2),
        ("POW", 2, 10, 1024),
        ("POW", 3, 3, 27),
        ("POW", 4, 0.5, 2),
        ("CMP", 5, 3, 1),
        ("CMP", 2, 7, -1),
        ("CMP", 4, 4, 0),
        ("EQ", 4, 4, 1),
        ("EQ", 4, 5, 0),
        ("MAX", 3, 7, 7),
        ("MIN", 3, 7, 3),
        ("SQRT", 144, 0, 12),
        ("SQRT", 2, 0, math.sqrt(2)),
        ("ABS", -5, 0, 5),
        ("ABS", 5, 0, 5),
        ("NEG", 7, 0, -7),
        ("NEG", -3, 0, 3),
        ("FLOOR", 3.7, 0, 3),
        ("FLOOR", -1.2, 0, -2),
        ("CEIL", 3.2, 0, 4),
        ("CEIL", -1.8, 0, -1),
        ("ROUND", 3.14159, 2, 3.14),
        ("ROUND", 2.5, 0, 2),  # Python banker's rounding
    ]

    # Edge cases
    edge_tests = [
        ("DIV", 1, 0, float('nan')),
        ("MOD", 5, 0, float('nan')),
        ("SQRT", -1, 0, float('nan')),
        ("LOG", 0, 0, float('nan')),
        ("LOG", -1, 0, float('nan')),
        ("POW", -1, 0.5, float('nan')),
    ]

    print(f"Testing {len(MATH_KERNELS)} math kernels...")
    failures = 0

    for name, a, b, expected in tests:
        result = apply_kernel(name, a, b)
        if abs(result - expected) > 1e-10:
            print(f"  ✗ {name}({a}, {b}) = {result}, expected {expected}")
            failures += 1

    for name, a, b, expected in edge_tests:
        result = apply_kernel(name, a, b)
        if not math.isnan(result):
            print(f"  ✗ {name}({a}, {b}) = {result}, expected NaN")
            failures += 1

    # Test unknown kernel
    result = apply_kernel("UNKNOWN", 1, 2)
    if not math.isnan(result):
        print(f"  ✗ UNKNOWN kernel should return NaN, got {result}")
        failures += 1

    if failures == 0:
        print(f"  ✓ All {len(tests)} tests passed")
        print(f"  ✓ All {len(edge_tests)} edge cases passed")
        print(f"  ✓ Unknown kernel returns NaN")
        print(f"\n  Kernels: {', '.join(sorted(MATH_KERNELS.keys()))}")
        print(f"  Total: {len(MATH_KERNELS)} deterministic functions")
    else:
        print(f"\n  ✗ {failures} failures")
        sys.exit(1)

    print("\n✓ math_kernels.py self-test complete")
