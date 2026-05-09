"""
MiniDispatch routing probe — analyze what the router learned.

Loads a checkpoint, runs eval data through, and reports:
  1. Per-op dispatch weight distribution
  2. Content-routing correlation (which tokens route where?)
  3. Op diversity metrics (entropy, utilization)
  4. Position-dependent routing (do early vs late positions differ?)

Usage:
  uv run python scripts/mini-dispatch/probe.py --checkpoint-dir checkpoints/mini-dispatch/step_002000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

# Path setup
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parent.parent / "v10"))
from data import ShardedDataLoader
from model import MiniDispatchConfig, MiniDispatchModel, create_model


# ══════════════════════════════════════════════════════════════════
# Token classification (simple heuristic for Qwen3 BBPE)
# ══════════════════════════════════════════════════════════════════

# Token ranges (approximate — good enough for routing analysis)
def classify_token(token_id: int) -> str:
    """Classify token into broad category for routing analysis."""
    # These are approximate for Qwen3 BBPE
    if token_id < 256:
        # Byte-level tokens — punctuation, digits, basic ASCII
        if 48 <= token_id <= 57:
            return "digit"
        elif 65 <= token_id <= 122:
            return "letter"
        else:
            return "punctuation"
    elif token_id < 1000:
        return "common"       # very frequent subwords
    elif token_id < 10000:
        return "frequent"     # frequent words/subwords
    elif token_id < 50000:
        return "mid"          # mid-frequency
    elif token_id < 100000:
        return "rare"         # rarer words
    else:
        return "very_rare"    # very rare / special


# ══════════════════════════════════════════════════════════════════
# Main probe
# ══════════════════════════════════════════════════════════════════


def probe(args):
    """Load checkpoint and analyze routing."""
    ckpt_dir = Path(args.checkpoint_dir)

    # Load config
    config_path = ckpt_dir.parent / "config.json" if (ckpt_dir.parent / "config.json").exists() else ckpt_dir / "config.json"
    if not config_path.exists():
        # Try one more level up
        config_path = ckpt_dir.parent.parent / "config.json"

    if config_path.exists():
        with open(config_path) as f:
            config_data = json.load(f)
        print(f"Config: {json.dumps(config_data, indent=2)}")
    else:
        print(f"Warning: no config.json found near {ckpt_dir}")
        config_data = {}

    cfg = MiniDispatchConfig(
        d_model=config_data.get("d_model", 128),
        n_ops=config_data.get("n_ops", 4),
        n_layers=config_data.get("n_layers", 2),
        top_k=config_data.get("top_k", 2),
        d_ff=config_data.get("d_ff", 384),
        seq_len=config_data.get("seq_len", 512),
    )

    # Load model
    model = create_model(cfg, "dispatch")
    weights_path = ckpt_dir / "weights.safetensors"
    if weights_path.exists():
        model.load_weights(str(weights_path))
        print(f"Loaded weights from {weights_path}")
    else:
        print(f"Warning: no weights found at {weights_path}, using random init")

    # Eval data
    data_dir = config_data.get("data_dir",
                                "/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
    n_train = 54
    eval_loader = ShardedDataLoader(
        data_dir, cfg.batch_size, cfg.seq_len,
        shard_start=n_train, shard_end=n_train + 6,
    )

    # Run eval batches and collect routing data
    n_batches = args.n_batches
    print(f"\nRunning {n_batches} eval batches...")

    all_tokens = []       # (n_batches * B * L,)
    all_weights = []      # per layer: list of (B, L, n_ops) arrays
    per_layer_weights = defaultdict(list)

    for bi in range(n_batches):
        input_ids, targets = eval_loader.next_batch()
        tokens = mx.array(input_ids)
        tgt = mx.array(targets)

        # Forward pass (populates routing caches)
        _, loss = model(tokens, tgt)
        mx.eval(loss)

        all_tokens.append(input_ids.flatten())

        # Collect routing weights per layer
        stats = model.get_routing_stats()
        for s in stats:
            li = s["layer"]
            w = s["weights_tensor"]  # (B, L, n_ops)
            mx.eval(w)
            per_layer_weights[li].append(np.array(w).reshape(-1, cfg.n_ops))

    all_tokens = np.concatenate(all_tokens)

    # ── Analysis ──────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  ROUTING ANALYSIS — {len(all_tokens):,} tokens")
    print(f"{'═' * 70}")

    for li in sorted(per_layer_weights.keys()):
        weights = np.concatenate(per_layer_weights[li], axis=0)  # (total_positions, n_ops)
        n_pos = weights.shape[0]

        print(f"\n── Layer {li} ──")

        # 1. Overall dispatch distribution
        mean_w = weights.mean(axis=0)
        std_w = weights.std(axis=0)
        print(f"\n  Op weights (mean ± std):")
        for oi in range(cfg.n_ops):
            bar = "█" * int(mean_w[oi] * 40)
            print(f"    Op {oi}: {mean_w[oi]:.4f} ± {std_w[oi]:.4f}  {bar}")

        # 2. Entropy
        # Per-position entropy
        pos_entropy = -np.sum(weights * np.log(weights + 1e-10), axis=1)
        max_ent = math.log(cfg.n_ops)
        norm_ent = pos_entropy / max_ent
        print(f"\n  Routing entropy: {norm_ent.mean():.4f} ± {norm_ent.std():.4f} "
              f"(1.0=uniform, 0.0=collapsed)")

        # 3. Winner diversity — how often is each op the winner?
        winners = np.argmax(weights, axis=1)
        print(f"\n  Winner frequency (primary route):")
        for oi in range(cfg.n_ops):
            frac = (winners == oi).sum() / n_pos
            bar = "█" * int(frac * 40)
            print(f"    Op {oi}: {frac:.4f}  {bar}")

        # 4. Content-routing correlation
        print(f"\n  Content → routing (which tokens prefer which ops?):")
        categories = defaultdict(list)
        for ti in range(len(all_tokens)):
            # Positions in flattened token array correspond to flattened weight array
            cat = classify_token(int(all_tokens[ti]))
            if ti < n_pos:  # only for positions we have weights
                categories[cat].append(weights[ti])

        print(f"    {'Category':<14s}  {'Count':>7s}  " +
              "  ".join(f"Op {i}" for i in range(cfg.n_ops)))
        print(f"    {'─' * 14}  {'─' * 7}  " +
              "  ".join("─" * 6 for _ in range(cfg.n_ops)))
        for cat in sorted(categories.keys()):
            cat_weights = np.array(categories[cat])
            cat_mean = cat_weights.mean(axis=0)
            count = len(categories[cat])
            vals = "  ".join(f"{v:.4f}" for v in cat_mean)
            print(f"    {cat:<14s}  {count:>7d}  {vals}")

        # 5. Position-dependent routing (early vs late in sequence)
        if n_pos >= cfg.seq_len * 2:  # need at least 2 full sequences
            n_seqs = n_pos // cfg.seq_len
            pos_weights = weights[:n_seqs * cfg.seq_len].reshape(n_seqs, cfg.seq_len, cfg.n_ops)
            # First quarter vs last quarter
            q1 = pos_weights[:, :cfg.seq_len // 4].mean(axis=(0, 1))
            q4 = pos_weights[:, 3 * cfg.seq_len // 4:].mean(axis=(0, 1))
            print(f"\n  Position dependence (early vs late in sequence):")
            print(f"    First quarter: {' '.join(f'{v:.4f}' for v in q1)}")
            print(f"    Last quarter:  {' '.join(f'{v:.4f}' for v in q4)}")
            diff = q4 - q1
            print(f"    Δ (late-early): {' '.join(f'{v:+.4f}' for v in diff)}")

    # 6. Training history analysis
    history_path = ckpt_dir.parent / "history.json" if (ckpt_dir.parent / "history.json").exists() else ckpt_dir / "history.json"
    if not history_path.exists():
        history_path = ckpt_dir.parent.parent / "history.json"

    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)

        if history.get("routing"):
            print(f"\n── Routing Evolution ──")
            # Show first, middle, last routing snapshots
            routing_entries = history["routing"]
            indices = [0, len(routing_entries) // 2, -1]
            for idx in indices:
                entry = routing_entries[idx]
                step = entry["step"]
                for layer_name, layer_data in entry["data"].items():
                    w = layer_data["mean_weights"]
                    ent = layer_data["normalized_entropy"]
                    print(f"  Step {step:>6d} {layer_name}: "
                          f"[{' '.join(f'{v:.3f}' for v in w)}] ent={ent:.3f}")

        if history.get("losses"):
            losses = history["losses"]
            print(f"\n── Loss trajectory ──")
            print(f"  Start: {losses[0]['loss']:.4f}  "
                  f"End: {losses[-1]['loss']:.4f}  "
                  f"Δ: {losses[-1]['loss'] - losses[0]['loss']:+.4f}")

    print(f"\n{'═' * 70}")


def main():
    parser = argparse.ArgumentParser(description="MiniDispatch routing probe")
    parser.add_argument("--checkpoint-dir", type=str, required=True,
                        help="Path to checkpoint directory (e.g. checkpoints/mini-dispatch/step_002000)")
    parser.add_argument("--n-batches", type=int, default=20,
                        help="Number of eval batches to analyze")
    args = parser.parse_args()
    probe(args)


if __name__ == "__main__":
    main()
