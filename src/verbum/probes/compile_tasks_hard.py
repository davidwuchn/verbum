"""Hard compile-task probes — find where prose→logical-form BREAKS (stage 2 leg 1+).

THE QUESTION (session 226). Leg 1 (compile_tasks.py) hit 1.0 on both Qwen3-8B/32B —
the task was BELOW the compile boundary (≤5-node, single combinator pattern, abstract
letters). This set probes the boundary by varying difficulty along independent axes so
we can see WHICH axis degrades the learned compile step:

    depth     — deep composition chains   (f (g (h (k x))))
    branch    — multiple independent subtrees  (f (g x) (h y) (k z))
    reuse     — variable reused / non-trivial routing  (f x (g x) x)
    mixed     — multi-combinator composition  (f (g x) (h (k y)))
    natural   — naturalistic prose, REAL words as atoms (structure extraction)
    ambiguous — genuinely ambiguous prose (multiple valid readings via also_ok)

Graded the same way (compile_frontend.py): few-shot prose→expression, the EXACT kernel
grades by REDUCTION-EQUALITY, representation-invariant. Inspecting failures separates
structural-incapacity from lexical/ambiguity (the leg-1 method).

License: MIT
"""

from __future__ import annotations

from verbum.probes.compile_tasks import CompileTask

__all__ = [
    "FAMILIES",
    "by_family",
    "family_counts",
    "family_names",
    "hard_tasks",
]

FAMILIES: tuple[str, ...] = (
    "depth4", "depth5", "branch2", "branch3", "reuse", "mixed",
    "natural", "ambiguous",
)

# (f, g, h, k, p, q, x, y, z) — abstract-symbol assignments for the structural axes.
_ASSIGN: tuple[tuple[str, ...], ...] = (
    ("f", "g", "h", "k", "p", "q", "x", "y", "z"),
    ("p", "q", "r", "s", "t", "u", "a", "b", "c"),
    ("g", "h", "f", "p", "k", "q", "u", "v", "w"),
    ("h", "f", "g", "q", "p", "k", "a", "x", "u"),
    ("q", "p", "k", "f", "g", "h", "b", "y", "v"),
)


def _structural(f, g, h, k, p, q, x, y, z):  # q reserved for future families
    return [
        ("depth4",
         f"Apply {k} to {x}, then apply {h} to that, then apply {g} to that, "
         f"then apply {f} to that.",
         f"{f} ({g} ({h} ({k} {x})))", 7, ()),
        ("depth5",
         f"Apply {p} to {x}, then {k} to that, then {h} to that, then {g} to "
         f"that, then {f} to that.",
         f"{f} ({g} ({h} ({k} ({p} {x}))))", 9, ()),
        ("branch2",
         f"Apply {f} to two arguments: first the result of applying {g} to {x}, "
         f"then the result of applying {h} to {y}.",
         f"{f} ({g} {x}) ({h} {y})", 7, ()),
        ("branch3",
         f"Apply {f} to three arguments: the result of {g} on {x}, then the "
         f"result of {h} on {y}, then the result of {k} on {z}.",
         f"{f} ({g} {x}) ({h} {y}) ({k} {z})", 10, ()),
        ("reuse",
         f"Apply {f} to three arguments in order: {x}, then the result of "
         f"applying {g} to {x}, then {x} again.",
         f"{f} {x} ({g} {x}) {x}", 6, ()),
        ("mixed",
         f"Apply {f} to two arguments: the result of applying {g} to {x}, and "
         f"the result of applying {h} to ({k} applied to {y}).",
         f"{f} ({g} {x}) ({h} ({k} {y}))", 9, ()),
    ]


# Naturalistic — real words as atoms; the model must extract STRUCTURE, keep words.
_NATURAL: tuple[tuple[str, str], ...] = (
    ("The scanner digitizes the form, then the office will archive the result.",
     "archive (digitize form)"),
    ("First peel the potato, then boil it.", "boil (peel potato)"),
    ("Revise the draft, then print the revision.", "print (revise draft)"),
    ("The robot welds the panel, then paints it, then inspects it.",
     "inspect (paint (weld panel))"),
    ("Merge the result of testing the blood with the result of scanning the bone.",
     "merge (test blood) (scan bone)"),
    ("The teacher will grade the essay and the quiz.", "grade essay quiz"),
    ("The bank will verify the signature and the balance.",
     "verify signature balance"),
    ("Combine the result of chopping the onion with the result of dicing the "
     "carrot.", "combine (chop onion) (dice carrot)"),
)

# Ambiguous — multiple valid readings; accept any via also_ok.
_AMBIG: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Apply f to g of x and y.", "f (g x) y", ("f (g x y)",)),
    ("Apply f to x and g of y and z.", "f x (g y) z",
     ("f x (g y z)", "f x (g y) z")),
    ("Apply h to f of x and g of y.", "h (f x) (g y)", ("h (f x g y)",)),
    ("Apply p to q of a and b and c.", "p (q a) b c",
     ("p (q a b c)", "p (q a b) c", "p (q a) b c")),
)


def _build() -> list[CompileTask]:
    out: list[CompileTask] = []
    for ai, names in enumerate(_ASSIGN):
        for fam, prose, gold, cx, alt in _structural(*names):
            out.append(CompileTask(
                id=f"hard_{fam}_{ai:02d}", pattern=fam, prose=prose,
                gold=gold, complexity=cx, also_ok=alt))
    for i, (prose, gold) in enumerate(_NATURAL):
        out.append(CompileTask(
            id=f"hard_natural_{i:02d}", pattern="natural", prose=prose,
            gold=gold, complexity=gold.count("(") + 1))
    for i, (prose, gold, alt) in enumerate(_AMBIG):
        out.append(CompileTask(
            id=f"hard_ambiguous_{i:02d}", pattern="ambiguous", prose=prose,
            gold=gold, complexity=gold.count("(") + 1, also_ok=alt))
    return out


_TASKS: list[CompileTask] = _build()


def hard_tasks() -> list[CompileTask]:
    return list(_TASKS)


def by_family(name: str) -> list[CompileTask]:
    return [t for t in _TASKS if t.pattern == name]


def family_names() -> list[str]:
    return list(FAMILIES)


def family_counts() -> dict[str, int]:
    return {f: len(by_family(f)) for f in FAMILIES}


if __name__ == "__main__":
    import json
    print(json.dumps(family_counts(), indent=2))
    for t in _TASKS:
        if t.id.endswith("_00") or t.pattern in ("natural", "ambiguous"):
            print(f"[{t.pattern:9}] {t.prose}\n   gold: {t.gold}  alt:{t.also_ok}")
