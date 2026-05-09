"""
MiniDispatch training — routing lab bench.

Trains a small dispatch-routing LM on Dolma prose and instruments
every routing decision. The goal is to understand HOW routing learns,
not to build a good LM.

Key instrumentation:
  - Per-op dispatch weight (mean over batch/seq) at each log step
  - Routing entropy (high = uniform, low = specialized)
  - Per-op utilization (fraction of positions where op is in top-k)
  - All routing history saved to JSON for offline analysis

Usage:
  uv run python scripts/mini-dispatch/train.py --model dispatch --total-steps 2000
  uv run python scripts/mini-dispatch/train.py --model baseline --total-steps 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np

# Add mini-dispatch to path first, then v10 for ShardedDataLoader
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parent.parent / "v10"))
from data import ShardedDataLoader

from model import MiniDispatchConfig, create_model, count_parameters


# ══════════════════════════════════════════════════════════════════
# Learning rate schedule
# ══════════════════════════════════════════════════════════════════


def cosine_lr(step: int, total_steps: int, lr: float, warmup: int) -> float:
    """Cosine annealing with linear warmup."""
    if step < warmup:
        return lr * step / max(warmup, 1)
    progress = (step - warmup) / max(total_steps - warmup, 1)
    return lr * 0.5 * (1.0 + math.cos(math.pi * progress))


# ══════════════════════════════════════════════════════════════════
# Routing analysis
# ══════════════════════════════════════════════════════════════════


def compute_routing_stats(model) -> dict | None:
    """Extract routing statistics from a MiniDispatchModel."""
    if not hasattr(model, "get_routing_stats"):
        return None

    stats = model.get_routing_stats()
    if not stats:
        return None

    result = {}
    for s in stats:
        li = s["layer"]
        weights = s["mean_weights"]  # list of floats, one per op

        # Entropy of the dispatch distribution
        w_arr = mx.array(weights)
        entropy = -float(mx.sum(w_arr * mx.log(w_arr + 1e-10)).item())
        max_entropy = math.log(len(weights))  # uniform distribution
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        # Per-op utilization: fraction of positions where op is selected
        # (in top-k, i.e. weight > small threshold)
        w_tensor = s["weights_tensor"]  # (B, L, n_ops)
        active = mx.sum(w_tensor > 0.01, axis=(0, 1))  # (n_ops,)
        total_positions = w_tensor.shape[0] * w_tensor.shape[1]
        mx.eval(active)
        utilization = [float(active[i].item()) / total_positions
                       for i in range(w_tensor.shape[-1])]

        result[f"layer_{li}"] = {
            "mean_weights": weights,
            "entropy": entropy,
            "normalized_entropy": normalized_entropy,
            "utilization": utilization,
        }

    return result


# ══════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════


def train(args):
    """Main training loop."""
    cfg = MiniDispatchConfig(
        d_model=args.d_model,
        n_ops=args.n_ops,
        d_ff=args.d_model * 3,
        n_layers=args.n_layers,
        top_k=args.top_k,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        total_steps=args.total_steps,
        lr=args.lr,
        warmup_steps=args.warmup_steps,
        log_interval=args.log_interval,
        checkpoint_dir=args.checkpoint_dir,
        data_dir=args.data_dir,
    )

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  MiniDispatch — Routing Lab Bench               ║")
    print(f"╠══════════════════════════════════════════════════╣")
    print(f"║  Model:    {args.model:<38s} ║")
    print(f"║  d_model:  {cfg.d_model:<38d} ║")
    print(f"║  n_ops:    {cfg.n_ops:<38d} ║")
    print(f"║  n_layers: {cfg.n_layers:<38d} ║")
    print(f"║  top_k:    {cfg.top_k:<38d} ║")
    print(f"║  d_ff:     {cfg.d_ff:<38d} ║")
    print(f"║  seq_len:  {cfg.seq_len:<38d} ║")
    print(f"║  batch:    {cfg.batch_size:<38d} ║")
    print(f"║  steps:    {cfg.total_steps:<38d} ║")
    print(f"║  lr:       {cfg.lr:<38g} ║")
    print(f"╚══════════════════════════════════════════════════╝")

    # Create model
    model = create_model(cfg, args.model)
    params = count_parameters(model)
    print(f"\nParameters: {params['total']:,}")
    for k, v in params["groups"].items():
        print(f"  {k}: {v:,}")

    # Optimizer
    optimizer = optim.AdamW(learning_rate=cfg.lr, weight_decay=cfg.weight_decay)

    # Data
    train_loader = ShardedDataLoader(
        cfg.data_dir, cfg.batch_size, cfg.seq_len,
        shard_start=0, shard_end=cfg.n_train_shards,
    )
    eval_loader = ShardedDataLoader(
        cfg.data_dir, cfg.batch_size, cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
    )

    # Checkpoint dir
    ckpt_dir = Path(cfg.checkpoint_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # Save config
    with open(ckpt_dir / "config.json", "w") as f:
        json.dump({
            "model_type": args.model,
            "d_model": cfg.d_model,
            "n_ops": cfg.n_ops,
            "n_layers": cfg.n_layers,
            "top_k": cfg.top_k,
            "d_ff": cfg.d_ff,
            "seq_len": cfg.seq_len,
            "batch_size": cfg.batch_size,
            "total_steps": cfg.total_steps,
            "lr": cfg.lr,
        }, f, indent=2)

    # Training history
    history = {
        "losses": [],
        "eval_losses": [],
        "routing": [],
    }

    # Loss function
    def loss_fn(model, tokens, targets):
        _, loss = model(tokens, targets)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Training ──────────────────────────────────────────────
    print(f"\nTraining {args.model} model for {cfg.total_steps} steps...")
    print(f"{'step':>6s}  {'loss':>7s}  {'lr':>8s}  {'tok/s':>7s}  {'routing':>40s}")
    print("─" * 80)

    t0 = time.time()
    running_loss = 0.0

    for step in range(1, cfg.total_steps + 1):
        # LR schedule
        lr = cosine_lr(step, cfg.total_steps, cfg.lr, cfg.warmup_steps)
        optimizer.learning_rate = lr

        # Get batch
        input_ids, targets = train_loader.next_batch()
        tokens = mx.array(input_ids)
        tgt = mx.array(targets)

        # Forward + backward
        loss, grads = loss_and_grad(model, tokens, tgt)

        # Gradient clipping
        grads, grad_norm = optim.clip_grad_norm(grads, max_norm=cfg.grad_clip)

        # Update
        optimizer.apply_gradients(grads, model)
        mx.eval(model.parameters(), optimizer.state, loss)

        running_loss += loss.item()

        # Logging
        if step % cfg.log_interval == 0 or step == 1:
            avg_loss = running_loss / min(step, cfg.log_interval)
            running_loss = 0.0

            elapsed = time.time() - t0
            tokens_per_sec = (step * cfg.batch_size * cfg.seq_len) / elapsed

            # Routing stats
            routing_str = ""
            routing_data = compute_routing_stats(model)
            if routing_data:
                # Show layer 0 weights compactly
                l0 = routing_data.get("layer_0", {})
                weights = l0.get("mean_weights", [])
                ent = l0.get("normalized_entropy", 0)
                routing_str = (
                    f"[{' '.join(f'{w:.2f}' for w in weights)}] "
                    f"ent={ent:.3f}"
                )
                history["routing"].append({
                    "step": step,
                    "data": routing_data,
                })

            history["losses"].append({"step": step, "loss": avg_loss})
            print(f"{step:6d}  {avg_loss:7.4f}  {lr:8.6f}  {tokens_per_sec:7.0f}  {routing_str}")

        # Checkpoint
        if step % cfg.checkpoint_interval == 0 or step == cfg.total_steps:
            ckpt_path = ckpt_dir / f"step_{step:06d}"
            ckpt_path.mkdir(parents=True, exist_ok=True)
            model.save_weights(str(ckpt_path / "weights.safetensors"))

            # Save routing history
            with open(ckpt_dir / "history.json", "w") as f:
                json.dump(history, f, indent=2)

            print(f"  ↳ Checkpoint saved: {ckpt_path}")

    # Final eval
    print("\n── Evaluation ──")
    eval_losses = []
    for _ in range(20):
        input_ids, targets = eval_loader.next_batch()
        tokens = mx.array(input_ids)
        tgt = mx.array(targets)
        _, loss = model(tokens, tgt)
        mx.eval(loss)
        eval_losses.append(loss.item())

    eval_loss = sum(eval_losses) / len(eval_losses)
    history["eval_losses"].append({"step": cfg.total_steps, "loss": eval_loss})
    print(f"  Eval loss: {eval_loss:.4f}")

    # Final routing analysis
    if hasattr(model, "get_routing_stats"):
        print("\n── Final Routing Analysis ──")
        routing_data = compute_routing_stats(model)
        if routing_data:
            for layer_name, layer_data in routing_data.items():
                weights = layer_data["mean_weights"]
                util = layer_data["utilization"]
                ent = layer_data["normalized_entropy"]
                print(f"  {layer_name}:")
                print(f"    Weights:     {' '.join(f'{w:.4f}' for w in weights)}")
                print(f"    Utilization: {' '.join(f'{u:.4f}' for u in util)}")
                print(f"    Entropy:     {ent:.4f} (1.0=uniform, 0.0=collapsed)")

    # Save final history
    with open(ckpt_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nDone. History saved to {ckpt_dir / 'history.json'}")
    return history


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="MiniDispatch training")
    parser.add_argument("--model", type=str, default="dispatch",
                        choices=["dispatch", "baseline"],
                        help="Model type: dispatch (routing) or baseline (single FFN)")
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--n-ops", type=int, default=4)
    parser.add_argument("--n-layers", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=512)
    parser.add_argument("--total-steps", type=int, default=2000)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--warmup-steps", type=int, default=100)
    parser.add_argument("--log-interval", type=int, default=25)
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints/mini-dispatch")
    parser.add_argument("--data-dir", type=str,
                        default="/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
