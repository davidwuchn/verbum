#!/usr/bin/env python3
"""Pack structured training data (BIOS + compile examples) into a tokenized .npy shard.

Reads:
  - BIOS examples (one per line, from `bb gen-bios`)
  - compile-train.jsonl (prose → lambda pairs)

Tokenizes with Qwen3 BBPE and packs into a flat int32 .npy array,
matching the format of Dolma shards for ShardedDataLoader compatibility.

Examples are separated by EOD tokens. The shard can be loaded by
MixedDataLoader for interleaved training with prose.

Usage:
    # Generate BIOS first:
    bb gen-bios --count 50000 > /tmp/bios_examples.txt

    # Pack into shard:
    uv run python scripts/v10/pack_structured.py \\
        --bios /tmp/bios_examples.txt \\
        --compile data/compile-train.jsonl \\
        --output data/structured_shard.npy

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load_bios_examples(path: Path) -> list[str]:
    """Load BIOS examples, one per line. Skip header/stats lines."""
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Skip bb stderr lines that leaked into stdout
            if line.startswith("BIOS Flash") or line.startswith("  "):
                continue
            examples.append(line)
    return examples


def load_compile_examples(path: Path) -> list[str]:
    """Load compile-train.jsonl as 'input → output' strings."""
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            # Format: "The dog runs. → λx. runs(dog)"
            text = f"{d['input']} → {d['output']}"
            examples.append(text)
    return examples


def main():
    parser = argparse.ArgumentParser(
        description="Pack structured training data into tokenized .npy shard")
    parser.add_argument("--bios", type=Path, required=True,
                        help="Path to BIOS examples (one per line)")
    parser.add_argument("--compile", type=Path, default=None,
                        help="Path to compile-train.jsonl")
    parser.add_argument("--output", type=Path, required=True,
                        help="Output .npy shard path")
    parser.add_argument("--repeat-compile", type=int, default=20,
                        help="Repeat compile examples N times (they're few)")
    args = parser.parse_args()

    # ── Load examples ─────────────────────────────────────────
    print(f"Loading BIOS examples from {args.bios}...", file=sys.stderr)
    bios = load_bios_examples(args.bios)
    print(f"  {len(bios)} BIOS examples", file=sys.stderr)

    compile_examples = []
    if args.compile and args.compile.exists():
        print(f"Loading compile examples from {args.compile}...", file=sys.stderr)
        raw_compile = load_compile_examples(args.compile)
        # Repeat compile examples to balance with BIOS
        compile_examples = raw_compile * args.repeat_compile
        print(f"  {len(raw_compile)} compile examples × {args.repeat_compile} "
              f"= {len(compile_examples)}", file=sys.stderr)

    all_examples = bios + compile_examples
    # Shuffle deterministically
    rng = np.random.RandomState(42)
    rng.shuffle(all_examples)
    print(f"  Total: {len(all_examples)} examples", file=sys.stderr)

    # ── Tokenize ──────────────────────────────────────────────
    print("Loading Qwen3 tokenizer...", file=sys.stderr)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B",
                                               trust_remote_code=True)
    eod_id = 151643  # Qwen3 EOD token

    print("Tokenizing...", file=sys.stderr)
    all_tokens = []
    for i, text in enumerate(all_examples):
        ids = tokenizer.encode(text, add_special_tokens=False)
        all_tokens.extend(ids)
        all_tokens.append(eod_id)  # separator
        if (i + 1) % 10000 == 0:
            print(f"  {i + 1}/{len(all_examples)} tokenized "
                  f"({len(all_tokens):,} tokens)", file=sys.stderr)

    print(f"  Final: {len(all_tokens):,} tokens", file=sys.stderr)

    # ── Pack to .npy ──────────────────────────────────────────
    arr = np.array(all_tokens, dtype=np.int32)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(args.output), arr)
    print(f"  Saved: {args.output} ({arr.nbytes / 1024 / 1024:.1f} MB)",
          file=sys.stderr)

    # ── Stats ─────────────────────────────────────────────────
    n_lambda = sum(1 for ex in all_examples if "λ" in ex)
    n_arrow = sum(1 for ex in all_examples if "→" in ex)
    n_raw = sum(1 for ex in all_examples if " = " in ex and "→" not in ex)
    print(f"\n  Distribution:", file=sys.stderr)
    print(f"    Lambda notation: {n_lambda} ({n_lambda/len(all_examples)*100:.0f}%)",
          file=sys.stderr)
    print(f"    S-expr/arrow:    {n_arrow - n_lambda} ({(n_arrow-n_lambda)/len(all_examples)*100:.0f}%)",
          file=sys.stderr)
    print(f"    Raw math:        {n_raw} ({n_raw/len(all_examples)*100:.0f}%)",
          file=sys.stderr)

    # Tokens per example
    tpe = len(all_tokens) / len(all_examples)
    print(f"    Tokens/example:  {tpe:.1f}", file=sys.stderr)


if __name__ == "__main__":
    main()
