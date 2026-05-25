#!/usr/bin/env python3
"""Pack structured training data for v14 — Qwen3.6-27B tokenizer.

Generates lambda expressions for K, I, B, C, M, D, Y, W, WHNF using
lambda_gen.py, plus compile examples from compile-train.jsonl and
math/clojure examples. Tokenizes with Qwen3.6-27B BBPE (vocab 248320)
and packs into a flat int32 .npy shard.

This shard is fed first during training warmup to latch the crystal
lattice immediately (proven in micro model experiments).

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/pack_structured.py

Output: data/structured_shard_qwen36.npy

License: MIT
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from verbum.lambda_gen import LambdaGenerator, Op


# ══════════════════════════════════════════════════════════════════════
# Math generator
# ══════════════════════════════════════════════════════════════════════

def generate_math_examples(n: int = 10000, seed: int = 42) -> list[str]:
    """Generate verified math examples in multiple notations."""
    rng = random.Random(seed)
    examples = []

    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
    }

    for _ in range(n):
        op_sym = rng.choice(list(ops.keys()))
        op_fn = ops[op_sym]

        # Bias toward small numbers
        digits = rng.choices([1, 1, 1, 2, 2, 3], k=2)
        a = rng.randint(0, 10**digits[0] - 1)
        b = rng.randint(0, 10**digits[1] - 1)

        if op_sym == "-" and a < b:
            a, b = b, a

        result = op_fn(a, b)

        notation = rng.choice(["raw", "sexpr", "lambda"])
        if notation == "raw":
            text = f"{a} {op_sym} {b} = {result}"
        elif notation == "sexpr":
            text = f"({op_sym} {a} {b}) → {result}"
        else:
            text = f"(λx. λy. ({op_sym} x y) {a} {b}) → {result}"

        examples.append(text)

    return examples


def generate_clojure_examples(n: int = 10000, seed: int = 42) -> list[str]:
    """Generate simple clojure-style functional programming examples."""
    rng = random.Random(seed)
    examples = []

    for _ in range(n):
        kind = rng.choice([
            "map", "filter", "reduce", "range", "conj",
            "inc", "dec", "first", "rest", "count",
        ])

        if kind == "map":
            nums = [rng.randint(0, 99) for _ in range(rng.randint(2, 6))]
            op = rng.choice(["inc", "dec", "(* 2)"])
            if op == "inc":
                result = [x + 1 for x in nums]
            elif op == "dec":
                result = [x - 1 for x in nums]
            else:
                result = [x * 2 for x in nums]
            text = f"(map {op} [{' '.join(str(x) for x in nums)}]) → [{' '.join(str(x) for x in result)}]"

        elif kind == "filter":
            nums = [rng.randint(0, 99) for _ in range(rng.randint(3, 7))]
            threshold = rng.randint(10, 50)
            result = [x for x in nums if x > threshold]
            text = f"(filter (λx. (> x {threshold})) [{' '.join(str(x) for x in nums)}]) → [{' '.join(str(x) for x in result)}]"

        elif kind == "reduce":
            nums = [rng.randint(1, 20) for _ in range(rng.randint(2, 5))]
            result = sum(nums)
            text = f"(reduce + [{' '.join(str(x) for x in nums)}]) → {result}"

        elif kind == "range":
            start = rng.randint(0, 10)
            end = start + rng.randint(2, 8)
            result = list(range(start, end))
            text = f"(range {start} {end}) → [{' '.join(str(x) for x in result)}]"

        elif kind == "conj":
            nums = [rng.randint(0, 999) for _ in range(rng.randint(1, 4))]
            new = rng.randint(0, 999)
            result = nums + [new]
            text = f"(conj [{' '.join(str(x) for x in nums)}] {new}) → [{' '.join(str(x) for x in result)}]"

        elif kind == "inc":
            x = rng.randint(0, 999)
            text = f"(inc {x}) → {x + 1}"

        elif kind == "dec":
            x = rng.randint(1, 999)
            text = f"(dec {x}) → {x - 1}"

        elif kind == "first":
            nums = [rng.randint(0, 99) for _ in range(rng.randint(2, 5))]
            text = f"(first [{' '.join(str(x) for x in nums)}]) → {nums[0]}"

        elif kind == "rest":
            nums = [rng.randint(0, 99) for _ in range(rng.randint(2, 5))]
            rest = nums[1:]
            text = f"(rest [{' '.join(str(x) for x in nums)}]) → [{' '.join(str(x) for x in rest)}]"

        elif kind == "count":
            nums = [rng.randint(0, 99) for _ in range(rng.randint(1, 8))]
            text = f"(count [{' '.join(str(x) for x in nums)}]) → {len(nums)}"

        examples.append(text)

    return examples


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_path = Path("data/structured_shard_qwen36.npy")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_per_op = 3000
    n_math = 10000
    n_clojure = 10000

    print("=" * 60, file=sys.stderr)
    print("  Pack Structured Shard — Qwen3.6-27B tokenizer", file=sys.stderr)
    print(f"  Lambda: {n_per_op} per op × 9 ops = {n_per_op * 9}", file=sys.stderr)
    print(f"  Math: {n_math}", file=sys.stderr)
    print(f"  Clojure: {n_clojure}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    all_examples = []

    # 1. Lambda expressions for all 9 ops
    print("\nGenerating lambda expressions...", file=sys.stderr)
    gen = LambdaGenerator(seed=42)
    for op in Op:
        examples = gen.generate(op, n=n_per_op)
        for ex in examples:
            all_examples.append(f"[{ex.op.value}:{ex.complexity}] {ex.expr}")
        print(f"  {op.value}: {len(examples)} examples", file=sys.stderr)

    # 2. Compile examples (NL → lambda)
    compile_path = Path("data/compile-train.jsonl")
    if compile_path.exists():
        print(f"\nLoading compile examples...", file=sys.stderr)
        with open(compile_path) as f:
            compile_raw = [json.loads(line.strip()) for line in f if line.strip()]
        for d in compile_raw:
            all_examples.append(f"{d['input']} → {d['output']}")
        # Repeat to balance (they're few — 509 examples)
        compile_repeated = [f"{d['input']} → {d['output']}" for d in compile_raw] * 10
        all_examples.extend(compile_repeated)
        print(f"  {len(compile_raw)} compile × 11 = {len(compile_raw) * 11}",
              file=sys.stderr)
    else:
        print(f"⚠  compile-train.jsonl not found at {compile_path}", file=sys.stderr)

    # 3. Math examples
    print(f"\nGenerating math examples...", file=sys.stderr)
    math_examples = generate_math_examples(n=n_math)
    all_examples.extend(math_examples)
    print(f"  {len(math_examples)} math examples", file=sys.stderr)

    # 4. Clojure examples
    print(f"\nGenerating clojure examples...", file=sys.stderr)
    clojure_examples = generate_clojure_examples(n=n_clojure)
    all_examples.extend(clojure_examples)
    print(f"  {len(clojure_examples)} clojure examples", file=sys.stderr)

    # Shuffle
    rng = np.random.RandomState(42)
    rng.shuffle(all_examples)
    print(f"\nTotal examples: {len(all_examples)}", file=sys.stderr)

    # Tokenize with Qwen3.6-27B
    print("\nLoading Qwen3.6-27B tokenizer...", file=sys.stderr)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3.6-27B",
                                               trust_remote_code=True)
    eod_id = tokenizer.eos_token_id
    print(f"  eos_token_id: {eod_id}", file=sys.stderr)
    print(f"  vocab_size: {tokenizer.vocab_size}", file=sys.stderr)

    print("Tokenizing...", file=sys.stderr)
    all_tokens = []
    for i, text in enumerate(all_examples):
        ids = tokenizer.encode(text, add_special_tokens=False)
        all_tokens.extend(ids)
        all_tokens.append(eod_id)
        if (i + 1) % 10000 == 0:
            print(f"  {i + 1}/{len(all_examples)} tokenized "
                  f"({len(all_tokens):,} tokens)", file=sys.stderr)

    print(f"\nFinal: {len(all_tokens):,} tokens", file=sys.stderr)

    # Pack
    arr = np.array(all_tokens, dtype=np.int32)
    np.save(output_path, arr)
    print(f"Saved: {output_path} ({arr.nbytes / 1024 / 1024:.1f} MB)",
          file=sys.stderr)

    # Stats
    n_docs = (arr == eod_id).sum()
    n_unique = len(np.unique(arr))
    max_id = int(arr.max())
    print(f"Documents: {n_docs:,}", file=sys.stderr)
    print(f"Unique tokens: {n_unique:,}", file=sys.stderr)
    print(f"Max token id: {max_id} (vocab limit: 248320)", file=sys.stderr)
    assert max_id < 248320, f"Token id {max_id} exceeds vocab 248320!"

    # Verify a few decoded examples
    print("\nSample decoded:", file=sys.stderr)
    eod_positions = np.where(arr == eod_id)[0]
    start = 0
    for i, end in enumerate(eod_positions[:5]):
        doc_tokens = arr[start:end].tolist()
        text = tokenizer.decode(doc_tokens)
        print(f"  [{i}] {text[:120]}", file=sys.stderr)
        start = end + 1

    print(f"\n✅ Structured shard ready: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
