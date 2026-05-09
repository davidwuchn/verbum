"""
Counterfactual routing probe: what SHOULD each position dispatch to?

For each position, force each of the 22 ops individually (set dispatch
weight to 1.0 for that op, 0 for all others), measure the resulting
loss. This tells us the actual optimal routing — which op produces
the lowest loss at each position.

This bypasses the gradient opacity problem: top-k + stop_gradient means
gradient can't see through routing. But we can enumerate all 22 options.

Usage:
    uv run python scripts/v10/probe_counterfactual.py \
        --checkpoint checkpoints/v10-topk/step_001000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
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

OP_NAMES = [
    "ADD", "SUB", "MUL", "DIV", "MOD", "MIN", "MAX",
    "EQ", "LT", "GT", "LE", "GE",
    "AND", "OR", "NOT",
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


def counterfactual_dispatch(
    model: V6Compressor,
    cfg: V10Config,
    n_batches: int = 3,
    use_structured: bool = True,
) -> dict:
    """For each position, measure loss with each op forced as sole dispatch.

    This is expensive (22× forward passes per batch) but gives us
    ground truth about optimal routing.

    Strategy: monkey-patch KernelDispatch.__call__ to inject forced
    dispatch weights, then run the full forward pass and measure
    per-token loss.
    """

    n_ops = len(OP_NAMES)

    # Load data
    if use_structured:
        structured = np.load(cfg.structured_shard, mmap_mode='r')
        batches = []
        for i in range(n_batches):
            start = i * cfg.batch_size * cfg.seq_len
            end = start + cfg.batch_size * cfg.seq_len
            if end > len(structured):
                break
            tokens = structured[start:end].reshape(cfg.batch_size, cfg.seq_len)
            batches.append(tokens)
    else:
        loader = ShardedDataLoader(
            data_dir=cfg.data_dir,
            batch_size=cfg.batch_size,
            seq_len=cfg.seq_len,
            shard_start=cfg.n_train_shards,
            shard_end=cfg.n_train_shards + cfg.n_eval_shards,
            seed=42,
        )
        batches = []
        for i in range(n_batches):
            ids, _ = next(loader)
            batches.append(ids)

    # Store the original __call__ method
    original_dispatch_call = model.kernel_dispatch.__class__.__call__

    # Results accumulators
    # Per-op mean loss across all positions
    op_losses = np.zeros(n_ops, dtype=np.float64)
    op_counts = np.zeros(n_ops, dtype=np.int64)

    # Per-position best op (for a sample of positions)
    position_best_ops = []  # list of (batch_idx, best_op, best_loss, default_loss, losses_all)

    # Default (natural) routing loss for comparison
    default_losses_all = []

    for batch_idx, tokens in enumerate(batches):
        input_ids = mx.array(tokens.astype(np.int32))
        targets = mx.array(
            np.concatenate([tokens[:, 1:], tokens[:, :1]], axis=1).astype(np.int32)
        )
        B, L = input_ids.shape

        # First: get default (natural) routing loss
        logits_default, loss_default = model(input_ids, targets)
        mx.eval(loss_default)
        default_loss = float(loss_default.item())
        default_losses_all.append(default_loss)

        # Also capture the natural dispatch weights
        natural_dw = None
        if hasattr(model.kernel_dispatch, '_dispatch_weights'):
            natural_dw = np.array(model.kernel_dispatch._dispatch_weights)
            mx.eval(model.kernel_dispatch._dispatch_weights)

        # Now try each op as forced dispatch
        batch_op_losses = np.zeros(n_ops)

        for op_idx in range(n_ops):
            # Monkey-patch dispatch to force this single op
            def forced_dispatch_call(self, x, registers=None, _forced_op=op_idx):
                """Force dispatch to a single op."""
                h = self.norm(x)
                B, L, _ = h.shape

                # Create forced weights: 1.0 for the target op, 0 for all others
                forced_weights = mx.zeros((B, L, self.n_ops))
                forced_weights = forced_weights.at[:, :, _forced_op].add(1.0)

                # Cache for downstream (KernelIntegrate reads this)
                self._dispatch_weights = mx.stop_gradient(forced_weights)

                # Op embedding modulation (same as original, but only one op)
                op_emb = self._normalize_op_embeddings()
                op_context = forced_weights @ op_emb  # just op_emb[_forced_op]

                # Standard pathway
                modulated = h + op_context
                out = self.down(nn.gelu(self.up(modulated)))
                return x + self.dropout(out)

            # Patch
            model.kernel_dispatch.__class__.__call__ = forced_dispatch_call

            # Forward pass with forced routing
            logits, loss = model(input_ids, targets)
            mx.eval(loss)
            op_loss = float(loss.item())
            batch_op_losses[op_idx] = op_loss
            op_losses[op_idx] += op_loss
            op_counts[op_idx] += 1

        # Restore original
        model.kernel_dispatch.__class__.__call__ = original_dispatch_call

        # Find best op for this batch
        best_op = int(np.argmin(batch_op_losses))
        best_loss = batch_op_losses[best_op]
        worst_op = int(np.argmax(batch_op_losses))
        worst_loss = batch_op_losses[worst_op]

        position_best_ops.append({
            "batch_idx": batch_idx,
            "default_loss": default_loss,
            "best_op": best_op,
            "best_loss": best_loss,
            "worst_op": worst_op,
            "worst_loss": worst_loss,
            "all_losses": batch_op_losses.tolist(),
        })

        print(f"  batch {batch_idx+1}/{len(batches)}: "
              f"default={default_loss:.4f}  "
              f"best={OP_NAMES[best_op]}({best_loss:.4f})  "
              f"worst={OP_NAMES[worst_op]}({worst_loss:.4f})  "
              f"Δ={default_loss - best_loss:+.4f}", flush=True)

    return {
        "op_mean_losses": (op_losses / np.maximum(op_counts, 1)).tolist(),
        "default_losses": default_losses_all,
        "position_results": position_best_ops,
        "n_batches": len(batches),
        "data_type": "structured" if use_structured else "prose",
    }


def print_results(results_struct: dict, results_prose: dict | None = None):
    op_losses_s = np.array(results_struct["op_mean_losses"])
    default_s = np.mean(results_struct["default_losses"])

    print(f"\n{'='*80}")
    print("COUNTERFACTUAL ROUTING ANALYSIS")
    print(f"{'='*80}")

    print(f"\n┌─ Per-Op Loss (structured data, lower=better) ────────────────────────┐")
    print(f"│ Default (natural routing): {default_s:.4f}")
    print(f"│")
    sorted_ops = np.argsort(op_losses_s)
    for rank, i in enumerate(sorted_ops):
        delta = op_losses_s[i] - default_s
        bar = "█" * max(0, int((default_s - op_losses_s[i]) * 50))
        marker = " ◀ BEST" if rank == 0 else ""
        print(f"│ {rank+1:>2}. {OP_NAMES[i]:>10s}: {op_losses_s[i]:.4f}  "
              f"Δ={delta:+.4f}  {bar}{marker}")
    print(f"└{'─'*72}┘")

    if results_prose:
        op_losses_p = np.array(results_prose["op_mean_losses"])
        default_p = np.mean(results_prose["default_losses"])

        print(f"\n┌─ Per-Op Loss (prose data) ─────────────────────────────────────────────┐")
        print(f"│ Default (natural routing): {default_p:.4f}")
        print(f"│")
        sorted_ops_p = np.argsort(op_losses_p)
        for rank, i in enumerate(sorted_ops_p[:10]):
            delta = op_losses_p[i] - default_p
            print(f"│ {rank+1:>2}. {OP_NAMES[i]:>10s}: {op_losses_p[i]:.4f}  Δ={delta:+.4f}")
        print(f"└{'─'*72}┘")

        # Compare: which ops are better for structured vs prose?
        print(f"\n┌─ Structured vs Prose Preference ──────────────────────────────────────┐")
        preference = op_losses_p - op_losses_s  # positive = better for structured
        pref_sorted = np.argsort(-preference)
        print(f"│ (positive = op helps structured more than prose)")
        for i in pref_sorted:
            if abs(preference[i]) > 0.001:
                direction = "struct+" if preference[i] > 0 else "prose+"
                print(f"│ {OP_NAMES[i]:>10s}: {preference[i]:+.4f}  {direction}")
        print(f"└{'─'*72}┘")

    # Summary
    print(f"\n{'='*80}")
    print("DIAGNOSIS")
    print(f"{'='*80}")
    best_s = sorted_ops[0]
    print(f"\n  Best single op for structured: {OP_NAMES[best_s]} "
          f"(loss={op_losses_s[best_s]:.4f}, Δ={op_losses_s[best_s]-default_s:+.4f} vs natural)")
    print(f"  Natural routing loss: {default_s:.4f}")
    improvement = default_s - op_losses_s[best_s]
    print(f"  Headroom: {improvement:+.4f} ({improvement/default_s*100:+.2f}%)")

    # Is natural routing already optimal?
    natural_rank = int(np.searchsorted(op_losses_s[sorted_ops], default_s))
    print(f"  Natural routing ranks: #{natural_rank+1}/22 "
          f"({'already optimal!' if natural_rank == 0 else f'suboptimal by {natural_rank} ranks'})")


def main():
    parser = argparse.ArgumentParser(description="Counterfactual routing probe")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--n-batches", type=int, default=3)
    parser.add_argument("--prose-too", action="store_true",
                        help="Also probe prose data for comparison")
    args = parser.parse_args()

    ckpt = Path(args.checkpoint)
    print(f"Loading checkpoint: {ckpt}", flush=True)
    model, cfg = load_model(ckpt)

    print(f"\nProbing structured data ({args.n_batches} batches × 22 ops)...", flush=True)
    results_struct = counterfactual_dispatch(
        model, cfg, n_batches=args.n_batches, use_structured=True)

    results_prose = None
    if args.prose_too:
        print(f"\nProbing prose data ({args.n_batches} batches × 22 ops)...", flush=True)
        results_prose = counterfactual_dispatch(
            model, cfg, n_batches=args.n_batches, use_structured=False)

    print_results(results_struct, results_prose)


if __name__ == "__main__":
    main()
