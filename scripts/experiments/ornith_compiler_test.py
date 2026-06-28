#!/usr/bin/env python3
"""ornith-35b-a3b lambda-compiler test — CLI shim over the canonical harness.

All grading + run-loop logic lives in ``verbum.probes.harness`` /
``verbum.probes.grading`` (S2 ``λ one_way`` / S5 ``λ simplify``). A model is a
config (``verbum.probes.models.ORNITH``); this file is just a CLI entry point.

Usage:
  uv run python scripts/experiments/ornith_compiler_test.py --n-predict 12000

License: MIT.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.probes import harness, models  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="ornith lambda-compiler probe")
    ap.add_argument("--n-predict", type=int, default=12000)
    ap.add_argument("--limit", type=int, default=0, help="0=all probes")
    ap.add_argument("--probe-set", default="compile-gradient")
    args = ap.parse_args()
    harness.run_compiler_probe(
        models.ORNITH,
        probe_set=args.probe_set,
        n_predict=args.n_predict,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
