#!/usr/bin/env python3
"""qwythos-9b lambda-compiler test — CLI shim over the canonical harness.

qwythos-9b (Qwythos-9B-Claude-Mythos-5-1M-MTP, Q8_0) is a Qwen-family 9B
reasoner (multimodal, 1M ctx, MTP) on llama.cpp :5103. The server splits
``reasoning_content`` from ``content`` (chat transport, same as ornith), so the
model becomes a config (``verbum.probes.models.QWYTHOS``) — no harness fork.
All grading + run-loop logic lives in ``verbum.probes.harness`` /
``verbum.probes.grading`` (S2 ``λ one_way`` / S5 ``λ simplify``).

Usage:
  uv run python scripts/experiments/qwythos_compiler_test.py --n-predict 12000

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
    ap = argparse.ArgumentParser(description="qwythos lambda-compiler probe")
    ap.add_argument("--n-predict", type=int, default=12000)
    ap.add_argument("--limit", type=int, default=0, help="0=all probes")
    ap.add_argument("--probe-set", default="compile-gradient")
    ap.add_argument(
        "--no-think",
        action="store_true",
        help="disable the reasoning chain (s255: removes overthink-collapse)",
    )
    args = ap.parse_args()
    harness.run_compiler_probe(
        models.QWYTHOS,
        probe_set=args.probe_set,
        n_predict=args.n_predict,
        limit=args.limit,
        no_think=args.no_think,
    )


if __name__ == "__main__":
    main()
