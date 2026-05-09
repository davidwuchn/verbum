"""
Probe per-position dispatch × type co-occurrence in v10-topk checkpoints.

With top-k=2, every position selects exactly 2 ops. This probe captures:
  1. Co-occurrence matrix: which op pairs appear together as top-2
  2. Per-position type × dispatch cross-tabulation
  3. Whether FN-typed positions correlate with specific ops

Usage:
    uv run python scripts/v10/probe_dispatch.py \
        --checkpoint checkpoints/v10-consensus/step_012000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader
from model import V6Compressor, create_model
from ternary import freeze_ternary_weights, restore_ternary

# ── Op and type names ──────────────────────────────────────────────────

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

OP_FAMILIES = {
    "arith_binary":  [0, 1, 2, 3, 4, 5, 6],
    "comparison":    [7, 8, 9, 10, 11],
    "bool_binary":   [12, 13],
    "bool_unary":    [14],
    "arith_unary":   [15, 16],
    "conditional":   [17],
    "lambda":        [18, 19, 20, 21],
}

# Expected output type per op
OP_EXPECTED_TYPE = [
    "INT", "INT", "INT", "INT", "INT", "INT", "INT",       # arith_binary
    "BOOL", "BOOL", "BOOL", "BOOL", "BOOL",                # comparison
    "BOOL", "BOOL",                                          # bool_binary
    "BOOL",                                                  # bool_unary
    "INT", "INT",                                            # arith_unary
    "INT",                                                   # conditional
    "FN", "INT", "FN_COMP", "INT",                          # lambda
]


def load_model(checkpoint_dir: Path) -> tuple[V6Compressor, V10Config]:
    """Load model from checkpoint."""
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


def probe_dispatch(
    model: V6Compressor,
    cfg: V10Config,
    n_batches: int = 20,
) -> dict:
    """Run data through model, capture per-position dispatch and type info."""

    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=42,
    )

    n_ops = len(OP_NAMES)
    n_types = len(TYPE_NAMES)

    # Accumulators
    cooccurrence = np.zeros((n_ops, n_ops), dtype=np.int64)    # op-pair counts
    type_given_op = np.zeros((n_ops, n_types), dtype=np.float64)  # P(type|op) accumulator
    op_given_type = np.zeros((n_types, n_ops), dtype=np.float64)  # P(op|type) accumulator
    type_counts = np.zeros(n_types, dtype=np.float64)
    op_counts = np.zeros(n_ops, dtype=np.float64)
    total_positions = 0

    # Per-op dispatch weight distributions (when selected as top-1 vs top-2)
    op_as_top1_weight = np.zeros(n_ops, dtype=np.float64)
    op_as_top2_weight = np.zeros(n_ops, dtype=np.float64)
    op_as_top1_count = np.zeros(n_ops, dtype=np.int64)
    op_as_top2_count = np.zeros(n_ops, dtype=np.int64)

    for batch_idx in range(n_batches):
        input_ids_np, _ = next(eval_loader)
        input_ids = mx.array(input_ids_np)

        # Run instrumented forward
        _, metrics = model.forward_instrumented(input_ids)

        # Get cached per-position weights
        dw = model.kernel_dispatch._dispatch_weights  # (B, L, n_ops)
        tw = model.kernel_integrate._type_weights      # (B, L, n_types)
        mx.eval(dw, tw)

        dw_np = np.array(dw)  # (B, L, 22)
        tw_np = np.array(tw)  # (B, L, 5)

        B, L, _ = dw_np.shape

        for b in range(B):
            for l in range(L):
                pos_dw = dw_np[b, l]  # (22,)
                pos_tw = tw_np[b, l]  # (5,)

                # Find top-2 ops (nonzero weight)
                active_ops = np.where(pos_dw > 1e-6)[0]

                if len(active_ops) < 2:
                    continue

                # Sort by weight descending
                sorted_active = active_ops[np.argsort(-pos_dw[active_ops])]
                top1_op = sorted_active[0]
                top2_op = sorted_active[1]

                # Co-occurrence (symmetric)
                cooccurrence[top1_op, top2_op] += 1
                cooccurrence[top2_op, top1_op] += 1

                # Dominant type at this position
                dom_type = np.argmax(pos_tw)

                # Type given op (weighted by dispatch weight)
                for op in active_ops:
                    w = pos_dw[op]
                    type_given_op[op] += pos_tw * w
                    op_counts[op] += w

                # Op given type (weighted by type weight)
                for t in range(n_types):
                    tw_t = pos_tw[t]
                    op_given_type[t] += pos_dw * tw_t
                    type_counts[t] += tw_t

                # Top-1 vs top-2 weight tracking
                op_as_top1_weight[top1_op] += pos_dw[top1_op]
                op_as_top1_count[top1_op] += 1
                op_as_top2_weight[top2_op] += pos_dw[top2_op]
                op_as_top2_count[top2_op] += 1

                total_positions += 1

        print(f"  batch {batch_idx+1}/{n_batches} ({total_positions:,} positions)",
              flush=True)

    # Normalize
    type_given_op_norm = type_given_op / (op_counts[:, None] + 1e-10)
    op_given_type_norm = op_given_type / (type_counts[:, None] + 1e-10)

    avg_top1_weight = op_as_top1_weight / (op_as_top1_count + 1e-10)
    avg_top2_weight = op_as_top2_weight / (op_as_top2_count + 1e-10)

    return {
        "cooccurrence": cooccurrence,
        "type_given_op": type_given_op_norm,
        "op_given_type": op_given_type_norm,
        "op_counts": op_counts,
        "type_counts": type_counts,
        "total_positions": total_positions,
        "op_as_top1_count": op_as_top1_count,
        "op_as_top2_count": op_as_top2_count,
        "avg_top1_weight": avg_top1_weight,
        "avg_top2_weight": avg_top2_weight,
    }


def print_results(results: dict):
    """Pretty-print the probe results."""
    cooc = results["cooccurrence"]
    tgo = results["type_given_op"]
    ogt = results["op_given_type"]
    total = results["total_positions"]

    print(f"\n{'='*85}")
    print(f"DISPATCH × TYPE PROBE — {total:,} positions analyzed")
    print(f"{'='*85}")

    # ── Co-occurrence matrix (top pairs) ──────────────────────
    print(f"\n┌─ Top-2 Co-occurrence (which ops are paired together) ──────────────┐")
    pairs = []
    for i in range(len(OP_NAMES)):
        for j in range(i+1, len(OP_NAMES)):
            if cooc[i, j] > 0:
                pairs.append((i, j, cooc[i, j]))
    pairs.sort(key=lambda x: -x[2])

    print(f"│ {'Op A':>12s}  ×  {'Op B':>12s}  │ {'Count':>8s} │ {'Share':>7s} │")
    print(f"│{'─'*14}───{'─'*14}─┼{'─'*10}┼{'─'*9}│")
    for i, j, count in pairs[:20]:
        share = count / total
        print(f"│ {OP_NAMES[i]:>12s}  ×  {OP_NAMES[j]:>12s}  │ {count:>8,} │ {share:>6.1%}  │")
    print(f"└{'─'*55}┘")

    # ── Top-1 vs Top-2 role ────────────────────────────────────
    print(f"\n┌─ Op Roles: Top-1 (primary) vs Top-2 (runner-up) ─────────────────────┐")
    t1c = results["op_as_top1_count"]
    t2c = results["op_as_top2_count"]
    t1w = results["avg_top1_weight"]
    t2w = results["avg_top2_weight"]

    active_ops = [i for i in range(len(OP_NAMES)) if t1c[i] + t2c[i] > 0]
    active_ops.sort(key=lambda i: -(t1c[i] + t2c[i]))

    print(f"│ {'Op':>12s} │ {'as top-1':>10s} │ {'as top-2':>10s} │ {'top1 %':>7s} │ {'avg w₁':>7s} │ {'avg w₂':>7s} │")
    print(f"│{'─'*13}┼{'─'*12}┼{'─'*12}┼{'─'*9}┼{'─'*9}┼{'─'*9}│")
    for i in active_ops:
        total_i = t1c[i] + t2c[i]
        top1_pct = t1c[i] / total_i if total_i > 0 else 0
        print(f"│ {OP_NAMES[i]:>12s} │ {t1c[i]:>10,} │ {t2c[i]:>10,} │ {top1_pct:>6.1%}  │ {t1w[i]:>6.3f}  │ {t2w[i]:>6.3f}  │")
    print(f"└{'─'*67}┘")

    # ── P(type | op) ───────────────────────────────────────────
    print(f"\n┌─ P(type | op) — what type does each op produce? ─────────────────────┐")
    print(f"│ {'Op':>12s} │ {'INT':>6s} │ {'BOOL':>6s} │ {'FN':>6s} │ {'FN_C':>6s} │ {'ERROR':>6s} │ {'expect':>7s} │")
    print(f"│{'─'*13}┼{'─'*8}┼{'─'*8}┼{'─'*8}┼{'─'*8}┼{'─'*8}┼{'─'*9}│")
    for i in active_ops:
        row = tgo[i]
        dom = TYPE_NAMES[np.argmax(row)]
        expected = OP_EXPECTED_TYPE[i]
        match = "✓" if dom == expected else "✗"
        print(f"│ {OP_NAMES[i]:>12s} │ {row[0]:>5.1%}  │ {row[1]:>5.1%}  │ {row[2]:>5.1%}  │ {row[3]:>5.1%}  │ {row[4]:>5.1%}  │ {expected:>4s} {match}  │")
    print(f"└{'─'*67}┘")

    # ── P(op | type) ───────────────────────────────────────────
    print(f"\n┌─ P(op | type) — which ops serve each type? ──────────────────────────┐")
    for t in range(len(TYPE_NAMES)):
        row = ogt[t]
        top_ops = np.argsort(-row)[:5]
        parts = " ".join(f"{OP_NAMES[o]}={row[o]:.3f}" for o in top_ops if row[o] > 0.001)
        print(f"│ {TYPE_NAMES[t]:>7s}: {parts}")
    print(f"└{'─'*72}┘")

    # ── Family co-occurrence ───────────────────────────────────
    print(f"\n┌─ Family × Family Co-occurrence ──────────────────────────────────────┐")
    fam_names = list(OP_FAMILIES.keys())
    fam_cooc = np.zeros((len(fam_names), len(fam_names)), dtype=np.int64)

    def op_to_fam(op_idx):
        for fi, (fname, ops) in enumerate(OP_FAMILIES.items()):
            if op_idx in ops:
                return fi
        return -1

    for i in range(len(OP_NAMES)):
        for j in range(len(OP_NAMES)):
            fi, fj = op_to_fam(i), op_to_fam(j)
            if fi >= 0 and fj >= 0:
                fam_cooc[fi, fj] += cooc[i, j]

    # Normalize rows
    row_sums = fam_cooc.sum(axis=1, keepdims=True)
    fam_cooc_norm = fam_cooc / (row_sums + 1e-10)

    short_names = ["arith", "comp", "b_bin", "b_un", "a_un", "cond", "lambda"]
    print(f"│ {'':>8s} │", end="")
    for sn in short_names:
        print(f" {sn:>6s} │", end="")
    print()
    for fi in range(len(fam_names)):
        print(f"│ {short_names[fi]:>8s} │", end="")
        for fj in range(len(fam_names)):
            v = fam_cooc_norm[fi, fj]
            if v > 0.01:
                print(f" {v:>5.1%}  │", end="")
            else:
                print(f" {'—':>5s}  │", end="")
        print()
    print(f"└{'─'*72}┘")

    # ── Summary ────────────────────────────────────────────────
    print(f"\n{'='*85}")
    print("SUMMARY")
    print(f"{'='*85}")

    # Find the dominant pairing pattern
    if pairs:
        top_pair = pairs[0]
        print(f"\n  Most common pair: {OP_NAMES[top_pair[0]]} × {OP_NAMES[top_pair[1]]} "
              f"({top_pair[2]:,} = {top_pair[2]/total:.1%} of positions)")

    # Type coherence check
    print(f"\n  Type coherence (does dominant type match expected?):")
    coherent = 0
    incoherent = 0
    for i in active_ops:
        dom = TYPE_NAMES[np.argmax(tgo[i])]
        expected = OP_EXPECTED_TYPE[i]
        if dom == expected:
            coherent += 1
        else:
            incoherent += 1
            print(f"    ✗ {OP_NAMES[i]:>12s}: dispatches type {dom}, expected {expected}")
    print(f"    {coherent}/{coherent+incoherent} ops coherent with expected type")


def main():
    parser = argparse.ArgumentParser(description="Probe dispatch × type co-occurrence")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="Path to checkpoint directory")
    parser.add_argument("--n-batches", type=int, default=20,
                        help="Number of eval batches to probe (default: 20)")
    args = parser.parse_args()

    ckpt = Path(args.checkpoint)
    print(f"Loading checkpoint: {ckpt}", flush=True)
    model, cfg = load_model(ckpt)

    print(f"Probing dispatch × type ({args.n_batches} batches)...", flush=True)
    results = probe_dispatch(model, cfg, n_batches=args.n_batches)
    print_results(results)


if __name__ == "__main__":
    main()
