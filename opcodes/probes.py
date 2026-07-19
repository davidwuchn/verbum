#!/usr/bin/env python3
"""Crystal probe access — bundled JSON first, verbum library fallback.

The measurement substrate: labeled prompts per crystal combinator
(K I B C S D W Y WHNF, >=50 each) used to calibrate the classifier. For the
standalone MVP the probes ship as ``data/crystal_probes.json``; inside the
verbum repo the canonical source of truth remains
``verbum.probes.library.crystal_probes()`` and the JSON is a mechanical
export of it (regenerate with ``python opcodes/probes.py --export``).

Probe record: ``{id, prompt, combinator, source, category}``.
License: MIT.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
PROBES_PATH = _HERE / "data" / "crystal_probes.json"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
MIN_PER_COMBINATOR = 50

__all__ = [
    "CRYSTAL",
    "MIN_PER_COMBINATOR",
    "Probe",
    "crystal_probes",
    "export_from_library",
    "self_test",
]


@dataclass(frozen=True)
class Probe:
    id: str
    prompt: str
    combinator: str
    source: str = ""
    category: str = ""


def _from_json(path: Path = PROBES_PATH) -> list[Probe] | None:
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("crystal_order") != CRYSTAL:
        raise ValueError(f"{path}: crystal order mismatch")
    return [Probe(**p) for p in d["probes"]]


def _from_library() -> list[Probe]:
    from verbum.probes.library import crystal_probes as lib_probes

    return [
        Probe(
            id=p.id,
            prompt=p.prompt,
            combinator=p.combinator,
            source=p.source,
            category=p.category,
        )
        for p in lib_probes()
        if p.combinator in CRYSTAL
    ]


def crystal_probes() -> list[Probe]:
    """All crystal measurement probes (bundled JSON, else verbum library)."""
    probes = _from_json()
    if probes is None:
        probes = _from_library()
    _check(probes)
    return probes


def _check(probes: list[Probe]) -> None:
    from collections import Counter

    counts = Counter(p.combinator for p in probes)
    thin = {
        c: counts.get(c, 0)
        for c in CRYSTAL
        if counts.get(c, 0) < MIN_PER_COMBINATOR
    }
    if thin:
        raise ValueError(
            f"crystal probe invariant violated (>= {MIN_PER_COMBINATOR} per "
            f"combinator): {thin}"
        )


def export_from_library(path: Path = PROBES_PATH) -> Path:
    """Regenerate the bundled JSON from the verbum probe library."""
    probes = _from_library()
    _check(probes)
    d = {
        "description": (
            "Crystal measurement probes — labeled prompts per combinator "
            "(exported from verbum.probes.library, dedup by prompt)"
        ),
        "crystal_order": CRYSTAL,
        "n_probes": len(probes),
        "probes": [vars(p) for p in probes],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return path


def self_test() -> dict:
    probes = crystal_probes()
    from collections import Counter

    counts = Counter(p.combinator for p in probes)
    checks = {
        "loaded_from_json": PROBES_PATH.exists(),
        "min_per_combinator": all(
            counts[c] >= MIN_PER_COMBINATOR for c in CRYSTAL
        ),
        "prompts_unique": len({p.prompt for p in probes}) == len(probes),
        "prompts_nonempty": all(p.prompt.strip() for p in probes),
    }
    return {
        "n_probes": len(probes),
        "counts": dict(counts),
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    import sys

    if "--export" in sys.argv:
        p = export_from_library()
        print(f"exported -> {p}")
    print(json.dumps(self_test(), indent=2))
    if not self_test()["all_pass"]:
        raise SystemExit(1)
