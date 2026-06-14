"""List-structured HOF stimuli — see attention DO the fold (the gather).

THE QUESTION (session 225, Michael): "attention can only do beta reduction
through a projection, so where we will see attention working is in WHAT IT IS
ATTENDING TO, and WHAT THE PROJECTIONS ARE that it calculates."

β-reduction = substitution = move a value source→dest. Attention realizes this as
the OV circuit: the PATTERN (QK: which source position) ∘ the PROJECTION (V→O: what
value is read and written). To watch attention perform a higher-order function we
need prose with an EXPLICIT enumeration to gather over, and we measure, at the
aggregation token: (a) the attention PATTERN over the enumerated items, and (b) the
OV/value PROJECTION moved from them.

DESIGN — same list, different task (isolates the gather to the FUNCTION, not the
tokens). Each stimulus is (prefix, items, suffix):
    text = prefix + ", ".join(items) + suffix
The instrument builds the text, recovers each item's char span (hence token
positions) via offset mapping, and reads attention at the last token.

  HOF tasks (should gather BROADLY over all items — iteration):
    map    — transform each item        ("square each", "double every")
    fold   — accumulate all items        ("add them all", "multiply together")
    filter — select a subset             ("keep the even ones")
  CONTROL tasks (same list, should FOCUS on one item):
    first  — report a single item        ("the first one is")

Accessors:
    gather_stims()      → list[GatherStim]
    by_function(name)   → list[GatherStim]
    function_names()    → list[str]

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FUNCTIONS",
    "GatherStim",
    "by_function",
    "function_names",
    "gather_stims",
]


@dataclass(frozen=True, slots=True)
class GatherStim:
    """A list-structured stimulus. text = prefix + ', '.join(items) + suffix."""

    id: str
    function: str            # map | fold | filter | first (control)
    kind: str                # "hof" | "control"
    prefix: str
    items: tuple[str, ...]
    suffix: str

    @property
    def text(self) -> str:
        return self.prefix + ", ".join(self.items) + self.suffix


FUNCTIONS: tuple[str, ...] = ("map", "fold", "filter", "first")
_CONTROL = {"first"}

# Item pools (short, mostly single-token) and the per-function suffixes.
_LISTS: tuple[tuple[str, ...], ...] = (
    ("4", "9", "2", "7", "5"),
    ("8", "3", "6", "1", "9", "4"),
    ("12", "5", "20", "7", "16"),
    ("apple", "pear", "plum", "grape", "lemon"),
    ("red", "blue", "green", "gray", "pink"),
    ("Tom", "Sara", "Ben", "Mia", "Leo"),
    ("oak", "elm", "pine", "birch", "ash"),
    ("north", "south", "east", "west", "up"),
)

_PREFIX = "Take the items "

_SUFFIXES: dict[str, str] = {
    "map": ", transform each of them, and the results are",
    "fold": ", combine them all together, and the single result is",
    "filter": ", keep only some of them, and the ones that remain are",
    "first": ", and the very first item in the list is",
}


def _build() -> list[GatherStim]:
    out: list[GatherStim] = []
    for fn in FUNCTIONS:
        kind = "control" if fn in _CONTROL else "hof"
        for i, items in enumerate(_LISTS):
            out.append(GatherStim(
                id=f"gather_{fn}_{i:02d}",
                function=fn, kind=kind,
                prefix=_PREFIX, items=tuple(items), suffix=_SUFFIXES[fn],
            ))
    return out


_STIMS: list[GatherStim] = _build()


def gather_stims() -> list[GatherStim]:
    return list(_STIMS)


def by_function(name: str) -> list[GatherStim]:
    return [s for s in _STIMS if s.function == name]


def function_names() -> list[str]:
    return list(FUNCTIONS)


if __name__ == "__main__":
    for s in _STIMS[:3] + by_function("first")[:1]:
        print(f"[{s.function}:{s.kind}] {s.text}")
    print(f"total: {len(_STIMS)} stimuli over {len(_LISTS)} lists x {len(FUNCTIONS)}")
