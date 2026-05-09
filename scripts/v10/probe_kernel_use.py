"""
Probe whether kernel dispatch correlates with actual computation in structured data.

This probe answers: when the model sees structured expressions like
"max(6 + 0, 5550 - 20) = 5530", does it dispatch to the right ops
at the right positions?

The key insight: the kernel functions (kernel.py) operate on discrete
trees, but the model sees token sequences. We need to find the bridge.

Approach:
  1. Run structured-only data through the model
  2. Capture per-position dispatch weights AND the actual tokens
  3. Decode tokens to find positions where ops appear in the text
  4. Check: does dispatch correlate with textual op occurrences?
  5. Compare structured vs prose dispatch patterns

This tells us whether the model has ANY signal connecting dispatch
to actual computation, even without the kernel being wired in.

Usage:
    uv run python scripts/v10/probe_kernel_use.py \
        --checkpoint checkpoints/v10-consensus/step_012000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

import mlx.core as mx
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader
from model import V6Compressor, create_model
from ternary import freeze_ternary_weights, restore_ternary
from kernel import Op, OP_NAMES as KERNEL_OP_NAMES

OP_NAMES = [
    "ADD", "SUB", "MUL", "DIV", "MOD", "MIN", "MAX",
    "EQ", "LT", "GT", "LE", "GE",
    "AND", "OR",
    "NOT",
    "ABS", "NEG",
    "IF",
    "PARTIAL", "APPLY", "COMPOSE", "APPLY-COMP",
]

TYPE_NAMES = ["INT", "BOOL", "FN", "FN_COMP", "ERROR"]


def load_model(checkpoint_dir: Path) -> tuple[V6Compressor, V10Config]:
    state = json.loads((checkpoint_dir / "state.json").read_text())
    cfg_data = state.get("config", {})
    cfg = V10Config(
        d_model=cfg_data.get("d_model", 512),
        vocab_size=cfg_data.get("vocab_size", 151936),
        seq_len=cfg_data.get("seq_len", 4096),
    )
    model = create_model(cfg)
    weights = dict(mx.load(str(checkpoint_dir / "model.npz")))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)
    return model, cfg


def load_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)


def find_op_tokens(tokenizer) -> dict[str, list[int]]:
    """Find token IDs that correspond to operator symbols/keywords.

    Returns mapping from op category to list of token IDs.
    """
    # Map text patterns to kernel op families
    op_patterns = {
        "arithmetic": ["+", "-", "*", "//", "%", "add", "sub", "mul", "div", "mod",
                       " + ", " - ", " * ", "(+", "(-", "(*"],
        "comparison": ["<", ">", "<=", ">=", "=", "==", " < ", " > ", " = ",
                       "min", "max", "min(", "max("],
        "boolean":    ["and", "or", "not", "true", "false", "True", "False",
                       " and ", " or ", " not "],
        "lambda":     ["λ", "fn", "partial", "comp", "apply", "reduce", "map",
                       "filter", "(fn ", "(λ", "lambda"],
        "conditional": ["if", "if(", "(if "],
    }

    op_token_map = {}
    for category, patterns in op_patterns.items():
        token_ids = set()
        for pattern in patterns:
            encoded = tokenizer.encode(pattern, add_special_tokens=False)
            token_ids.update(encoded)
        op_token_map[category] = sorted(token_ids)

    return op_token_map


def classify_position(token_id: int, context_ids: list[int], tokenizer,
                       op_token_map: dict) -> str | None:
    """Classify what kind of computation a position is near."""
    text = tokenizer.decode([token_id])

    for category, token_ids in op_token_map.items():
        if token_id in token_ids:
            return category

    return None


def probe_structured_vs_prose(
    model: V6Compressor,
    cfg: V10Config,
    tokenizer,
    n_batches: int = 10,
) -> dict:
    """Compare dispatch patterns on structured vs prose data."""

    n_ops = len(OP_NAMES)
    n_types = len(TYPE_NAMES)

    # ── Structured data ──────────────────────────────────
    structured = np.load(cfg.structured_shard, mmap_mode='r')
    op_token_map = find_op_tokens(tokenizer)

    struct_dispatch = np.zeros(n_ops, dtype=np.float64)
    struct_types = np.zeros(n_types, dtype=np.float64)
    struct_positions = 0

    # Per-category dispatch: what ops fire near arithmetic tokens vs lambda tokens etc.
    category_dispatch = defaultdict(lambda: np.zeros(n_ops, dtype=np.float64))
    category_types = defaultdict(lambda: np.zeros(n_types, dtype=np.float64))
    category_counts = defaultdict(int)
    uncategorized_dispatch = np.zeros(n_ops, dtype=np.float64)
    uncategorized_count = 0

    # Dispatch delta: how much does the hidden state change per op?
    # We capture the pre/post dispatch hidden states for each op
    op_delta_norms = defaultdict(list)  # op_idx -> list of ||delta|| values

    print("  Probing structured data...", flush=True)
    for batch_idx in range(n_batches):
        start = batch_idx * cfg.batch_size * cfg.seq_len
        end = start + cfg.batch_size * cfg.seq_len
        if end > len(structured):
            break

        tokens = structured[start:end].reshape(cfg.batch_size, cfg.seq_len)
        input_ids = mx.array(tokens.astype(np.int32))

        _, metrics = model.forward_instrumented(input_ids)

        dw = model.kernel_dispatch._dispatch_weights  # (B, L, 22)
        tw = model.kernel_integrate._type_weights       # (B, L, 5)
        mx.eval(dw, tw)
        dw_np = np.array(dw)
        tw_np = np.array(tw)

        B, L, _ = dw_np.shape
        struct_dispatch += dw_np.sum(axis=(0, 1))
        struct_types += tw_np.sum(axis=(0, 1))
        struct_positions += B * L

        # Classify each position by its token
        for b in range(B):
            for l in range(L):
                token_id = int(tokens[b, l])
                cat = classify_position(token_id, [], tokenizer, op_token_map)
                if cat:
                    category_dispatch[cat] += dw_np[b, l]
                    category_types[cat] += tw_np[b, l]
                    category_counts[cat] += 1
                else:
                    uncategorized_dispatch += dw_np[b, l]
                    uncategorized_count += 1

        print(f"    structured batch {batch_idx+1}/{n_batches} "
              f"({struct_positions:,} positions)", flush=True)

    # ── Prose data ────────────────────────────────────────
    prose_dispatch = np.zeros(n_ops, dtype=np.float64)
    prose_types = np.zeros(n_types, dtype=np.float64)
    prose_positions = 0

    print("  Probing prose data...", flush=True)
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=42,
    )

    for batch_idx in range(n_batches):
        input_ids_np, _ = next(eval_loader)
        input_ids = mx.array(input_ids_np)

        _, metrics = model.forward_instrumented(input_ids)

        dw = model.kernel_dispatch._dispatch_weights
        tw = model.kernel_integrate._type_weights
        mx.eval(dw, tw)
        dw_np = np.array(dw)
        tw_np = np.array(tw)

        B, L, _ = dw_np.shape
        prose_dispatch += dw_np.sum(axis=(0, 1))
        prose_types += tw_np.sum(axis=(0, 1))
        prose_positions += B * L

        print(f"    prose batch {batch_idx+1}/{n_batches} "
              f"({prose_positions:,} positions)", flush=True)

    return {
        "struct_dispatch": struct_dispatch / struct_positions,
        "struct_types": struct_types / struct_positions,
        "struct_positions": struct_positions,
        "prose_dispatch": prose_dispatch / prose_positions,
        "prose_types": prose_types / prose_positions,
        "prose_positions": prose_positions,
        "category_dispatch": {
            k: v / max(category_counts[k], 1) for k, v in category_dispatch.items()
        },
        "category_types": {
            k: v / max(category_counts[k], 1) for k, v in category_types.items()
        },
        "category_counts": dict(category_counts),
        "uncategorized_dispatch": uncategorized_dispatch / max(uncategorized_count, 1),
        "uncategorized_count": uncategorized_count,
    }


def print_results(results: dict):
    n_ops = len(OP_NAMES)

    print(f"\n{'='*85}")
    print("STRUCTURED vs PROSE DISPATCH COMPARISON")
    print(f"{'='*85}")
    print(f"\n  Structured: {results['struct_positions']:,} positions")
    print(f"  Prose:      {results['prose_positions']:,} positions")

    # ── Overall dispatch comparison ───────────────────────
    sd = results["struct_dispatch"]
    pd = results["prose_dispatch"]

    print(f"\n┌─ Dispatch: Structured vs Prose (ops > 1% in either) ────────────────┐")
    print(f"│ {'Op':>12s} │ {'Struct':>8s} │ {'Prose':>8s} │ {'Delta':>8s} │ {'Signal':>8s} │")
    print(f"│{'─'*13}┼{'─'*10}┼{'─'*10}┼{'─'*10}┼{'─'*10}│")
    for i in range(n_ops):
        if sd[i] > 0.01 or pd[i] > 0.01:
            delta = sd[i] - pd[i]
            signal = "struct+" if delta > 0.02 else ("prose+" if delta < -0.02 else "~same")
            print(f"│ {OP_NAMES[i]:>12s} │ {sd[i]:>7.1%}  │ {pd[i]:>7.1%}  │ {delta:>+7.1%}  │ {signal:>8s} │")
    print(f"└{'─'*55}┘")

    # ── Type comparison ────────────────────────────────────
    st = results["struct_types"]
    pt = results["prose_types"]

    print(f"\n┌─ Types: Structured vs Prose ─────────────────────────────────────────┐")
    print(f"│ {'Type':>8s} │ {'Struct':>8s} │ {'Prose':>8s} │ {'Delta':>8s} │")
    print(f"│{'─'*9}┼{'─'*10}┼{'─'*10}┼{'─'*10}│")
    for i, name in enumerate(TYPE_NAMES):
        delta = st[i] - pt[i]
        print(f"│ {name:>8s} │ {st[i]:>7.1%}  │ {pt[i]:>7.1%}  │ {delta:>+7.1%}  │")
    print(f"└{'─'*42}┘")

    # ── Per-category dispatch (the key table) ─────────────
    cat_d = results["category_dispatch"]
    cat_t = results["category_types"]
    cat_c = results["category_counts"]

    print(f"\n┌─ Dispatch by Token Category (structured data only) ──────────────────┐")
    print(f"│ Positions per category:")
    for cat in sorted(cat_c.keys()):
        print(f"│   {cat:>15s}: {cat_c[cat]:>8,} positions")
    print(f"│   {'uncategorized':>15s}: {results['uncategorized_count']:>8,} positions")
    print(f"│")

    categories = sorted(cat_d.keys())
    for cat in categories:
        d = cat_d[cat]
        t = cat_t[cat]
        top_ops = np.argsort(-d)[:5]
        ops_str = " ".join(f"{OP_NAMES[o]}={d[o]:.3f}" for o in top_ops if d[o] > 0.005)
        top_type = TYPE_NAMES[np.argmax(t)]
        type_w = t[np.argmax(t)]
        print(f"│ {cat:>15s}: {ops_str}")
        print(f"│ {'':>15s}  type: {top_type}={type_w:.1%}  "
              f"({'matches!' if _expected_match(cat, OP_NAMES[top_ops[0]], top_type) else 'mismatch'})")

    # Uncategorized (general tokens in structured data)
    ud = results["uncategorized_dispatch"]
    top_ops = np.argsort(-ud)[:5]
    ops_str = " ".join(f"{OP_NAMES[o]}={ud[o]:.3f}" for o in top_ops if ud[o] > 0.005)
    print(f"│ {'uncategorized':>15s}: {ops_str}")
    print(f"└{'─'*72}┘")

    # ── Diagnosis ──────────────────────────────────────────
    print(f"\n{'='*85}")
    print("DIAGNOSIS")
    print(f"{'='*85}")

    # Check if dispatch differs between structured and prose
    diff = np.abs(sd - pd)
    total_diff = diff.sum()
    print(f"\n  Total dispatch divergence (L1): {total_diff:.3f}")
    print(f"  (0 = identical patterns, 2 = completely different)")

    type_diff = np.abs(st - pt).sum()
    print(f"  Total type divergence (L1):     {type_diff:.3f}")

    # Check if categories get different dispatch
    if len(categories) >= 2:
        cat_pairs = []
        for i, c1 in enumerate(categories):
            for c2 in categories[i+1:]:
                d1, d2 = cat_d[c1], cat_d[c2]
                cat_diff = np.abs(d1 - d2).sum()
                cat_pairs.append((c1, c2, cat_diff))
        cat_pairs.sort(key=lambda x: -x[2])
        print(f"\n  Category dispatch divergence:")
        for c1, c2, d in cat_pairs:
            print(f"    {c1:>15s} vs {c2:<15s}: L1={d:.3f}")


def _expected_match(category: str, top_op: str, top_type: str) -> bool:
    """Check if the top op/type makes sense for the token category."""
    expected = {
        "arithmetic": ({"ADD", "SUB", "MUL", "DIV", "MOD", "MIN", "MAX"}, {"INT"}),
        "comparison": ({"EQ", "LT", "GT", "LE", "GE", "MIN", "MAX"}, {"BOOL", "INT"}),
        "boolean":    ({"AND", "OR", "NOT"}, {"BOOL"}),
        "lambda":     ({"PARTIAL", "APPLY", "COMPOSE", "APPLY-COMP"}, {"FN", "FN_COMP"}),
        "conditional": ({"IF"}, {"INT"}),
    }
    if category not in expected:
        return False
    exp_ops, exp_types = expected[category]
    return top_op in exp_ops or top_type in exp_types


def main():
    parser = argparse.ArgumentParser(description="Probe kernel dispatch vs actual computation")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--n-batches", type=int, default=10)
    args = parser.parse_args()

    ckpt = Path(args.checkpoint)
    print(f"Loading checkpoint: {ckpt}", flush=True)
    model, cfg = load_model(ckpt)

    print("Loading tokenizer...", flush=True)
    tokenizer = load_tokenizer()

    print(f"Running probe ({args.n_batches} batches each)...", flush=True)
    results = probe_structured_vs_prose(model, cfg, tokenizer, n_batches=args.n_batches)
    print_results(results)


if __name__ == "__main__":
    main()
