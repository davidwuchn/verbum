#!/usr/bin/env python3
"""Lambda-as-pre-thinking experiment — CLI shim over the canonical harness.

Tests whether lambda compilation acts as "pre-thinking" (S5 λ types): run the
same checkable reasoning set in three FORMATS — direct / prose-CoT / lambda —
held at no-think so the reasoning format is the only varying factor. All logic
lives in ``verbum.probes.{harness,grading}``; this is a thin entry point.

Usage:
  uv run python scripts/experiments/reasoning_mode_test.py --model qwythos --mode lambda
  uv run python scripts/experiments/reasoning_mode_test.py --model qwythos --mode all

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
    ap = argparse.ArgumentParser(description="lambda-as-pre-thinking reasoning probe")
    ap.add_argument("--model", default="qwythos", choices=sorted(models.REGISTRY))
    ap.add_argument("--mode", default="all", choices=["direct", "cot", "lambda", "all"])
    ap.add_argument("--probe-set", default="reasoning-check")
    ap.add_argument("--n-predict", type=int, default=4000)
    ap.add_argument("--limit", type=int, default=0, help="0=all probes")
    ap.add_argument(
        "--think",
        action="store_true",
        help="enable the native reasoning channel (default: no-think)",
    )
    args = ap.parse_args()

    cfg = models.REGISTRY[args.model]
    modes = ["direct", "cot", "lambda"] if args.mode == "all" else [args.mode]
    for mode in modes:
        print(f"\n########## MODE = {mode} ##########", flush=True)
        harness.run_reasoning_probe(
            cfg,
            mode=mode,  # type: ignore[arg-type]
            probe_set=args.probe_set,
            n_predict=args.n_predict,
            limit=args.limit,
            no_think=not args.think,
        )


if __name__ == "__main__":
    main()
