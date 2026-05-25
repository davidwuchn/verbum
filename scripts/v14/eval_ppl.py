"""
v14 — Perplexity evaluation on held-out shards.

Usage:
  uv run python scripts/v14/eval_ppl.py --checkpoint checkpoints/v14-td/step_000500

Loads model from checkpoint, evaluates CE on eval shards (54-59),
reports perplexity = exp(CE).

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import restore_ternary, freeze_ternary_weights
from td import convert_to_delta, collect_delta_params, freeze_delta_architecture


def evaluate(
    model: V14Model,
    loader: ShardedDataLoader,
    n_batches: int,
    seq_len: int,
) -> dict[str, float]:
    """Evaluate CE and perplexity over n_batches from loader."""
    total_ce = 0.0
    total_tokens = 0
    ce_values = []

    t0 = time.time()

    for i in range(n_batches):
        batch = loader.next_batch()
        if batch is None:
            break

        input_ids_np, targets_np = batch
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        # Forward pass (no grad)
        logits, _total_loss = model(input_ids, targets)
        mx.eval(logits)

        # Compute CE from logits directly (not the crystal-weighted total_loss)
        ce = nn.losses.cross_entropy(logits, targets, reduction="mean")
        mx.eval(ce)
        ce_val = float(ce.item())

        n_tok = targets.size
        total_ce += ce_val * n_tok
        total_tokens += n_tok
        ce_values.append(ce_val)

        if (i + 1) % 10 == 0 or (i + 1) == n_batches:
            running_ce = total_ce / total_tokens
            running_ppl = math.exp(min(running_ce, 20))  # cap to avoid overflow
            elapsed = time.time() - t0
            tps = total_tokens / max(elapsed, 1e-6)
            print(
                f"  [{i+1:>4}/{n_batches}]"
                f"  CE={running_ce:.4f}  PPL={running_ppl:.1f}"
                f"  batch_ce={ce_val:.4f}"
                f"  | {tps:.0f} tok/s  {elapsed:.1f}s",
                flush=True,
            )

    elapsed = time.time() - t0
    avg_ce = total_ce / max(total_tokens, 1)
    ppl = math.exp(min(avg_ce, 20))

    # Variance
    ce_arr = np.array(ce_values)
    ce_std = float(np.std(ce_arr)) if len(ce_arr) > 1 else 0.0

    return {
        "ce": avg_ce,
        "ppl": ppl,
        "ce_std": ce_std,
        "n_batches": len(ce_values),
        "n_tokens": total_tokens,
        "elapsed_s": elapsed,
        "tok_per_sec": total_tokens / max(elapsed, 1e-6),
    }


def main():
    parser = argparse.ArgumentParser(description="v14 perplexity evaluation")
    parser.add_argument(
        "--checkpoint", type=str, required=True,
        help="Path to checkpoint directory (e.g. checkpoints/v14-td/step_000500)",
    )
    parser.add_argument(
        "--n-batches", type=int, default=100,
        help="Number of eval batches (default: 100)",
    )
    parser.add_argument(
        "--extracted-model-path", type=str, default=None,
        help="Override extracted model path (default: from config)",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.checkpoint).resolve()
    print(f"{'='*60}")
    print(f"  v14 Perplexity Evaluation")
    print(f"  Checkpoint: {ckpt_path}")
    print(f"  Batches: {args.n_batches}")
    print(f"{'='*60}")

    # ── Config ────────────────────────────────────────────────
    cfg = V14Config()
    if args.extracted_model_path:
        cfg.extracted_model_path = args.extracted_model_path

    # ── Model ─────────────────────────────────────────────────
    print("\nBuilding model...", flush=True)
    model = V14Model(cfg)

    # Load extracted base plates first (same as training)
    base_path = Path(cfg.extracted_model_path).resolve()
    if base_path.exists():
        model.load_weights(str(base_path), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  Base plates loaded from {base_path}")

    # Convert to delta architecture (attention layers)
    convert_to_delta(model, include_prefixes=("shared_stride_stack",))
    freeze_delta_architecture(model)

    # Load checkpoint weights (overwrites base + delta + gamma/norms)
    model_path = ckpt_path / "model.npz"
    if model_path.exists():
        model.load_weights(str(model_path), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  Checkpoint weights loaded from {model_path}")
    else:
        print(f"  ⚠ No model.npz found at {model_path}")
        sys.exit(1)

    # Load delta plates if present
    delta_path = ckpt_path / "delta_plates.npz"
    if delta_path.exists():
        from ternary import pack_ternary_mlx
        delta_data = dict(np.load(str(delta_path), allow_pickle=False))
        delta_modules = collect_delta_params(model)
        n_loaded = 0
        for path, dtl in delta_modules:
            delta_key = path.replace(".", "_")
            # New format (session 150+): packed uint32, key = "{name}_delta_packed"
            packed_key = f"{delta_key}_delta_packed"
            # Old format: unpacked int8, key = "{name}_delta"
            old_key = f"{delta_key}_delta"
            if packed_key in delta_data:
                dtl.delta_weight = mx.array(delta_data[packed_key])
                mx.eval(dtl.delta_weight)
                n_loaded += 1
            elif old_key in delta_data:
                delta_int8 = mx.array(delta_data[old_key].astype(np.int8))
                dtl.delta_weight = pack_ternary_mlx(delta_int8)
                mx.eval(dtl.delta_weight)
                n_loaded += 1
        print(f"  Delta plates loaded: {n_loaded}/{len(delta_modules)}")
    else:
        print(f"  No delta_plates.npz (using all-+1 delta)")

    # Restore state (crystal EMA, S5 identity)
    state_path = ckpt_path / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        s5 = state.get("s5_identity_state")
        if s5 is not None:
            model.s5_identity.identity_state = mx.array(s5)
        ema = state.get("crystal_ema")
        if ema is not None:
            model._crystal_ema = mx.array(float(ema))
        step = state.get("step", "?")
        print(f"  State restored (step={step})")

    # Delta stats summary
    delta_modules = collect_delta_params(model)
    total_flip = 0
    total_block = 0
    total_positions = 0
    for path, dtl in delta_modules:
        stats = dtl.delta_stats()
        s = dtl.out_features * dtl.in_features
        total_flip += int(stats["flip_frac"] * s)
        total_block += int(stats["block_frac"] * s)
        total_positions += s
    print(f"  Delta summary: {total_positions:,} positions,"
          f" {total_flip:,} flipped ({total_flip/max(total_positions,1)*100:.2f}%),"
          f" {total_block:,} blocked ({total_block/max(total_positions,1)*100:.2f}%)")

    # ── Data loader (eval shards) ─────────────────────────────
    print(f"\nLoading eval data (shards {cfg.n_train_shards}-{cfg.n_train_shards + cfg.n_eval_shards - 1})...",
          flush=True)
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=12345,
    )
    print(f"  seq_len={cfg.seq_len}  batch_size={cfg.batch_size}")

    # ── Evaluate ──────────────────────────────────────────────
    print(f"\nEvaluating ({args.n_batches} batches, {args.n_batches * cfg.batch_size * cfg.seq_len:,} tokens)...\n",
          flush=True)
    results = evaluate(model, eval_loader, args.n_batches, cfg.seq_len)

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"  CE:   {results['ce']:.4f} ± {results['ce_std']:.4f}")
    print(f"  PPL:  {results['ppl']:.1f}")
    print(f"  Tokens: {results['n_tokens']:,}")
    print(f"  Speed: {results['tok_per_sec']:.0f} tok/s")
    print(f"  Time: {results['elapsed_s']:.1f}s")
    print(f"{'='*60}")

    # Save results
    out_path = ckpt_path / "eval_results.json"
    with open(str(out_path), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
