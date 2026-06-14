"""Compile-task probes — natural-language dataflow → logical form (stage 2 leg 1).

THE QUESTION (session 226). Stage 2 factors the compiler into prose→logical-form
(LEARNED) ∘ logical-form→term (bracket abstraction, EXACT) ∘ term→normal-form
(reduction, EXACT). The two formal halves are certified exact (results/compile-
roundtrip). This probe set tests the ONLY learned step in isolation: can a model map a
natural-language description of a data-flow to a logical form (an applicative
expression), which the EXACT kernel then verifies by reduction?

Each task is (prose, gold) where gold is the normal-form expression in lambda_ast
syntax (juxtaposition application, parens to group). A model answer is correct iff it
parses and REDUCES to the same normal form as gold — so the model may answer with the
direct expression `f (g x)` OR an equivalent combinator term `B f g x`; the kernel
normalizes both (representation-invariant grading).

Patterns mirror the combinator basis (the dataflow each combinator performs):
    identity (I) · const/discard (K) · compose (B) · flip/reorder (C)
    duplicate (W) · substitute/share (S) · deep-compose (D)

Accessors: compile_tasks() · by_pattern(name) · pattern_names() · pattern_counts()

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "PATTERNS",
    "CompileTask",
    "by_pattern",
    "compile_tasks",
    "pattern_counts",
    "pattern_names",
]


@dataclass(frozen=True, slots=True)
class CompileTask:
    id: str
    pattern: str      # identity|const|compose|flip|dup|subst|deep
    prose: str        # natural-language dataflow description
    gold: str         # normal-form expression (lambda_ast syntax)
    complexity: int   # # of applications in gold


PATTERNS: tuple[str, ...] = (
    "identity", "const", "compose", "flip", "dup", "subst", "deep",
)

# (functions, values) name assignments for diversity (held-out from the few-shot set,
# which uses m/n/k/s/t — see compile_frontend.py).
_ASSIGN: tuple[tuple[str, str, str, str, str, str], ...] = (
    # F, G, H, X, Y, Z
    ("f", "g", "h", "x", "y", "z"),
    ("p", "q", "r", "a", "b", "c"),
    ("f", "h", "g", "u", "v", "w"),
    ("g", "f", "p", "x", "a", "u"),
    ("q", "p", "r", "b", "y", "v"),
    ("h", "g", "f", "z", "c", "w"),
    ("p", "f", "q", "a", "x", "b"),
    ("f", "p", "h", "x", "u", "y"),
)


def _templates(f, g, h, x, y, z):  # z reserved for future depth-extensions
    return [
        ("identity", f"Take {x} and return it unchanged.", f"{x}", 1),
        ("const", f"Return just {x} by itself; ignore {y} completely.", f"{x}", 1),
        ("compose",
         f"First apply {g} to {x}, then apply {f} to that result.",
         f"{f} ({g} {x})", 3),
        ("flip",
         f"Apply {f} to {y} and {x}, with {y} as the first argument "
         f"and {x} as the second.",
         f"{f} {y} {x}", 3),
        ("dup",
         f"Apply {f} to {x}, passing {x} as both of its arguments.",
         f"{f} {x} {x}", 3),
        ("subst",
         f"Apply {f} to {x} and to the result of applying {g} to {x}.",
         f"{f} {x} ({g} {x})", 5),
        ("deep",
         f"Apply {h} to {x}, then apply {g} to that, then apply {f} to that.",
         f"{f} ({g} ({h} {x}))", 5),
    ]


def _build() -> list[CompileTask]:
    out: list[CompileTask] = []
    for ai, names in enumerate(_ASSIGN):
        for pattern, prose, gold, cx in _templates(*names):
            out.append(CompileTask(
                id=f"compile_{pattern}_{ai:02d}",
                pattern=pattern, prose=prose, gold=gold, complexity=cx,
            ))
    return out


_TASKS: list[CompileTask] = _build()


def compile_tasks() -> list[CompileTask]:
    return list(_TASKS)


def by_pattern(name: str) -> list[CompileTask]:
    return [t for t in _TASKS if t.pattern == name]


def pattern_names() -> list[str]:
    return list(PATTERNS)


def pattern_counts() -> dict[str, int]:
    return {p: len(by_pattern(p)) for p in PATTERNS}


if __name__ == "__main__":
    import json
    print(json.dumps(pattern_counts(), indent=2))
    for t in _TASKS[:7]:
        print(f"[{t.pattern:8}] {t.prose}\n   gold: {t.gold}")
