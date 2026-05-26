#!/usr/bin/env python3
"""
v14 — Kernel Training Loop

Trains through the composed plate (1 matmul) instead of the full model
(238 matmuls). Validated by probe: gradient cosine = 0.9698.

Architecture:
  KERNEL steps (fast, ~0.1s): embed → T @ x → norm → logits → CE → Adam
  FULL steps (slow, every K steps): full forward/backward → TD → refit T

The composed plate T captures the embed→pre-head transform as a single
matrix. Training through T gives 97% of the gradient direction at
50-300× less compute. TD still runs through the full model (it needs
per-layer routing gradients), but only every K steps.

Usage:
    cd verbum
    uv run python scripts/v14/train_kernel.py \\
      --checkpoint-dir checkpoints/v14-kernel \\
      --kernel-ratio 10 \\
      --refit-batches 10 \\
      --steps 500

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_map, tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import restore_ternary, freeze_ternary_weights, zero_ternary_grads
from td import (
    TernaryDescent,
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
    DeltaTernaryLinear,
)
from ternary import surgical_adam_decay_for_etch
from train_td import (
    loss_fn,
    cosine_lr,
    _attention_delta_modules,
    _enforce_no_block,
    compute_decomposed_gradients,
    filter_gamma_grads,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Composed Plate Management
# ══════════════════════════════════════════════════════════════════════════════


def fit_composed_plate(model, loader, n_batches, seq_len=4096):
    """Fit composed plate T via least-squares from full model residuals.

    Captures embed output and pre-head output, fits T: x_out ≈ T @ x_embed.
    Returns T as numpy array (d_model × d_model).
    """
    all_embeds = []
    all_outs = []

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        B, L = ids.shape

        # Capture embed output
        positions = mx.arange(L)
        x_embed = model.embed_norm(model.embed(ids) + model.pos_embed(positions))

        # Full forward to get pre-head output
        logits, loss_val = model(ids, tgts)
        mx.eval(logits, loss_val)
        x_out = model._last_hidden
        mx.eval(x_embed, x_out)

        all_embeds.append(np.array(x_embed.reshape(-1, x_embed.shape[-1])))
        all_outs.append(np.array(x_out.reshape(-1, x_out.shape[-1])))

    X_in = np.concatenate(all_embeds, axis=0)   # (N, d)
    X_out = np.concatenate(all_outs, axis=0)    # (N, d)

    # Solve: X_out = X_in @ T^T  →  T^T = lstsq(X_in, X_out)
    T_T, _, _, _ = np.linalg.lstsq(X_in, X_out, rcond=None)
    T = T_T.T  # (d, d)

    return T


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Kernel Loss Function
# ══════════════════════════════════════════════════════════════════════════════


def kernel_loss_fn(model, input_ids, targets, T_mx):
    """Forward through composed plate → CE loss.

    Path: embed → T @ x_embed → output_norm → output_proj → CE
    This skips the entire stride-stack computation (238 matmuls → 1).
    """
    B, L = input_ids.shape
    positions = mx.arange(L)
    x_embed = model.embed_norm(model.embed(input_ids) + model.pos_embed(positions))

    # THE KERNEL: one matmul replaces the entire stride stack
    x_composed = x_embed @ T_mx.T

    # Output projection (same as full model)
    x_out = model.output_norm(x_composed)
    logits = model.embed.output_proj(x_out)

    # CE loss
    logits_flat = logits.reshape(-1, logits.shape[-1])
    tgts_flat = targets.reshape(-1)
    ce = mx.mean(nn.losses.cross_entropy(logits_flat, tgts_flat))

    return ce


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Training Loop
# ══════════════════════════════════════════════════════════════════════════════


def train_kernel(
    cfg: V14Config,
    args: argparse.Namespace,
    model: V14Model,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    start_step: int,
    train_loader,
    checkpoint_dir: Path,
) -> None:
    """Hybrid kernel/full training loop.

    Alternates between:
    - K kernel steps: fast (composed plate), trains embed/norm/output_proj
    - 1 full step: slow (full model), trains everything + TD flips + refit T
    """
    total_steps = args.steps or cfg.total_steps
    kernel_ratio = args.kernel_ratio  # K kernel steps per full step
    refit_batches = args.refit_batches

    attn_delta = _attention_delta_modules(delta_modules)

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  v14 — Kernel Training", file=sys.stderr)
    print(f"  Kernel steps (composed plate) + Full steps (TD + refit)", file=sys.stderr)
    print(f"  Kernel ratio: {kernel_ratio} kernel steps per full step", file=sys.stderr)
    print(f"  Refit batches: {refit_batches}", file=sys.stderr)
    print(f"  Steps {start_step+1}–{total_steps}", file=sys.stderr)
    print(f"  TD: flip_rate={args.td_flip_rate}  flip_interval={args.td_flip_interval}",
          file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr, flush=True)

    # ── Optimizers ─────────────────────────────────────────────
    adam = optim.AdamW(
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=[0.9, 0.999],
    )
    td = TernaryDescent(
        flip_rate=args.td_flip_rate,
        warmup_steps=args.td_warmup,
        min_confidence=args.td_min_confidence,
        flip_interval=args.td_flip_interval,
    )

    # ── Full model loss+grad ───────────────────────────────────
    loss_and_grad_full = nn.value_and_grad(model, loss_fn)

    # ── State ──────────────────────────────────────────────────
    loss_window = deque(maxlen=50)
    total_td_flips = 0
    td_active = False
    step = start_step
    t_start = time.time()

    # ── Initial composed plate fit ─────────────────────────────
    print(f"\n  Fitting initial composed plate ({refit_batches} batches)...",
          file=sys.stderr, flush=True)
    t_fit = time.time()
    T_np = fit_composed_plate(model, train_loader, refit_batches)
    T_mx = mx.array(T_np.astype(np.float32))
    fit_time = time.time() - t_fit
    print(f"  Composed plate fit in {fit_time:.1f}s", file=sys.stderr, flush=True)

    # Track timing
    kernel_times = deque(maxlen=50)
    full_times = deque(maxlen=10)
    refit_times = deque(maxlen=10)

    # ── Main loop ──────────────────────────────────────────────
    while step < total_steps:

        # ════════════════════════════════════════════════════════
        # KERNEL STEPS: fast, through composed plate
        # ════════════════════════════════════════════════════════
        for k_step in range(kernel_ratio):
            step += 1
            if step > total_steps:
                break

            t0 = time.time()
            lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
            adam.learning_rate = lr

            # Gradient accumulation through composed plate
            accum_loss = 0.0
            accum_grads = None

            for _micro in range(cfg.grad_accum):
                ids_np, tgts_np = next(train_loader)
                ids = mx.array(ids_np)
                tgts = mx.array(tgts_np)

                lv, grads = nn.value_and_grad(model, kernel_loss_fn)(
                    model, ids, tgts, T_mx
                )
                mx.eval(lv, grads)
                accum_loss += float(lv.item())

                if accum_grads is None:
                    accum_grads = grads
                else:
                    accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

            step_loss = accum_loss / cfg.grad_accum
            accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

            # NaN guard
            if math.isnan(step_loss) or math.isinf(step_loss):
                print(f"⚠️  NaN in kernel step {step}, skipping", file=sys.stderr)
                continue

            # Zero ternary grads + clip
            accum_grads = zero_ternary_grads(model, accum_grads)
            flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
            grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
            grad_norm = math.sqrt(max(grad_sq, 0.0))
            if grad_norm > 1.0:
                accum_grads = tree_map(lambda g: g * (1.0 / (grad_norm + 1e-8)), accum_grads)

            # Adam step
            adam.update(model, accum_grads)
            mx.eval(model.parameters(), adam.state)
            restore_ternary(model)

            loss_window.append(step_loss)
            dt = time.time() - t0
            kernel_times.append(dt * 1000)

            # Log
            if step % cfg.log_interval == 0:
                avg50 = sum(loss_window) / len(loss_window)
                tps = cfg.tokens_per_step / dt
                avg_kernel_ms = sum(kernel_times) / len(kernel_times)
                print(
                    f"step {step:>6d} [K]"
                    f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                    f" | lr {lr:.2e}"
                    f" | gnorm {grad_norm:.2f}"
                    f" | {tps:.0f} tok/s"
                    f" | {avg_kernel_ms:.0f}ms/step",
                    file=sys.stderr, flush=True,
                )

        if step > total_steps:
            break

        # ════════════════════════════════════════════════════════
        # FULL STEP: slow, through full model (TD + refit)
        # ════════════════════════════════════════════════════════
        step += 1
        if step > total_steps:
            break

        t0_full = time.time()
        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        # Full forward/backward with grad accumulation
        accum_loss = 0.0
        accum_grads = None

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            lv, grads = loss_and_grad_full(model, ids, tgts)
            mx.eval(lv, grads)
            accum_loss += float(lv.item())

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        step_loss = accum_loss / cfg.grad_accum
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        if math.isnan(step_loss) or math.isinf(step_loss):
            print(f"⚠️  NaN in full step {step}, skipping", file=sys.stderr)
            continue

        # Zero ternary grads + clip
        accum_grads = zero_ternary_grads(model, accum_grads)
        flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
        grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
        grad_norm = math.sqrt(max(grad_sq, 0.0))
        if grad_norm > 1.0:
            accum_grads = tree_map(lambda g: g * (1.0 / (grad_norm + 1e-8)), accum_grads)

        # Gradient decomposition for TD
        td_inputs, gamma_filters = compute_decomposed_gradients(model, accum_grads)
        filtered_grads = filter_gamma_grads(accum_grads, gamma_filters)

        # Adam step
        adam.update(model, filtered_grads)
        mx.eval(model.parameters(), adam.state)
        restore_ternary(model)

        # Schmitt trigger: crystal-gated TD activation
        crystal_val = getattr(model, "_last_crystal_mse", None)
        if crystal_val is not None:
            mx.eval(crystal_val)
            crystal_val_f = float(crystal_val.item())
            if crystal_val_f < args.td_crystal_gate:
                td_active = True
            elif crystal_val_f > args.td_crystal_ceiling:
                td_active = False

        # TD step
        if td_active:
            td_result = td.step(td_inputs, training_step=step)
        else:
            td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}

        # Apply flips
        td_affected_rows = {}
        for name, info in td_result["per_module"].items():
            if "new_packed" in info:
                for path, dtl in delta_modules:
                    if path == name:
                        dtl.delta_weight = info["new_packed"]
                        mx.eval(dtl.delta_weight)
                        break
            if "affected_rows" in info and info["affected_rows"]:
                td_affected_rows[name] = info["affected_rows"]

        _enforce_no_block(delta_modules)

        if td_affected_rows:
            surgical_adam_decay_for_etch(adam, model, td_affected_rows, decay=0.1)

        total_td_flips += td_result["total_flips"]
        dt_full = time.time() - t0_full

        # ── Refit composed plate ───────────────────────────────
        t_refit = time.time()
        T_np = fit_composed_plate(model, train_loader, refit_batches)
        T_mx = mx.array(T_np.astype(np.float32))
        dt_refit = time.time() - t_refit
        refit_times.append(dt_refit * 1000)

        loss_window.append(step_loss)
        full_times.append(dt_full * 1000)

        # Log full step
        avg50 = sum(loss_window) / len(loss_window)
        tps = cfg.tokens_per_step / dt_full
        gate_icon = "🔓" if td_active else "🔒"
        avg_kernel = sum(kernel_times) / len(kernel_times) if kernel_times else 0
        avg_full = sum(full_times) / len(full_times) if full_times else 0
        avg_refit = sum(refit_times) / len(refit_times) if refit_times else 0
        speedup = avg_full / avg_kernel if avg_kernel > 0 else 0

        print(
            f"step {step:>6d} [F] {gate_icon}"
            f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
            f" | lr {lr:.2e}"
            f" | gnorm {grad_norm:.2f}"
            f" | td={td_result['total_flips']}"
            f" | {tps:.0f} tok/s"
            f" | full={avg_full:.0f}ms  kernel={avg_kernel:.0f}ms"
            f" | refit={avg_refit:.0f}ms"
            f" | speedup={speedup:.1f}×",
            file=sys.stderr, flush=True,
        )

        # ── Checkpoint ─────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            ckpt_dir = checkpoint_dir / f"step_{step:06d}"
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            model.save_weights(str(ckpt_dir / "model.npz"))

            # Save state
            state = {
                "step": step,
                "train_losses_last50": list(loss_window),
                "total_td_flips": total_td_flips,
                "td_active": td_active,
                "kernel_ratio": kernel_ratio,
                "avg_kernel_ms": float(avg_kernel),
                "avg_full_ms": float(avg_full),
                "speedup": float(speedup),
                "config": cfg.to_dict(),
            }
            with open(str(ckpt_dir / "state.json"), "w") as f:
                json.dump(state, f, indent=2)

            # Save composed plate
            np.savez_compressed(str(ckpt_dir / "composed_plate.npz"), T=T_np)

            print(f"  📸 Checkpoint saved: {ckpt_dir}", file=sys.stderr, flush=True)

    # Final summary
    avg_kernel = sum(kernel_times) / len(kernel_times) if kernel_times else 0
    avg_full = sum(full_times) / len(full_times) if full_times else 0
    speedup = avg_full / avg_kernel if avg_kernel > 0 else 0
    elapsed = time.time() - t_start
    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  Training complete: {step} steps in {elapsed:.0f}s", file=sys.stderr)
    print(f"  Avg kernel step: {avg_kernel:.0f}ms", file=sys.stderr)
    print(f"  Avg full step:   {avg_full:.0f}ms", file=sys.stderr)
    print(f"  Kernel speedup:  {speedup:.1f}×", file=sys.stderr)
    print(f"  Total TD flips:  {total_td_flips:,}", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════════════════
# § 4  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="v14 Kernel Training")

    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints/v14-kernel")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--steps", type=int, default=None)

    # Kernel-specific
    parser.add_argument("--kernel-ratio", type=int, default=10,
                        help="Number of kernel (fast) steps per full (slow) step. Default: 10")
    parser.add_argument("--refit-batches", type=int, default=10,
                        help="Batches to use when refitting composed plate. Default: 10")

    # TD args (same as train_td.py)
    parser.add_argument("--td-flip-rate", type=float, default=0.001)
    parser.add_argument("--td-warmup", type=int, default=100)
    parser.add_argument("--td-min-confidence", type=float, default=0.3)
    parser.add_argument("--td-flip-interval", type=int, default=20)
    parser.add_argument("--td-beta1", type=float, default=0.9)
    parser.add_argument("--td-beta2", type=float, default=0.999)
    parser.add_argument("--td-crystal-gate", type=float, default=0.03)
    parser.add_argument("--td-crystal-ceiling", type=float, default=0.07)
    parser.add_argument("--decompose-gradient", action="store_true", default=True)

    # FFN delta
    parser.add_argument("--convert-ffn", action="store_true", default=False)

    args = parser.parse_args()

    # ── Config ─────────────────────────────────────────────────
    cfg = V14Config()
    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  v14 Kernel Training", file=sys.stderr)
    print(f"  Kernel ratio: {args.kernel_ratio} (K fast steps per full step)", file=sys.stderr)
    print(f"  Checkpoint dir: {checkpoint_dir}", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)

    # ── Model ──────────────────────────────────────────────────
    model = V14Model(cfg)
    base_path = Path(cfg.extracted_model_path).resolve()
    print(f"\n  Loading base plates from {base_path}...", file=sys.stderr)
    model.load_weights(str(base_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)

    # Delta conversion
    prefixes = ("shared_stride_stack",)
    if args.convert_ffn:
        prefixes = ("shared_stride_stack", "ffn_")
    convert_to_delta(model, include_prefixes=prefixes)
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)
    delta_modules = collect_delta_params(model)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)

    # Resume from checkpoint if available
    start_step = 0
    latest_ckpt = None
    if args.resume:
        latest_ckpt = Path(args.resume)
    else:
        ckpt_dirs = sorted(
            d for d in checkpoint_dir.iterdir()
            if d.is_dir() and d.name.startswith("step_")
        ) if checkpoint_dir.exists() else []
        if ckpt_dirs:
            latest_ckpt = ckpt_dirs[-1]

    if latest_ckpt and latest_ckpt.exists():
        print(f"  Resuming from {latest_ckpt}", file=sys.stderr)
        model.load_weights(str(latest_ckpt / "model.npz"), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        state_path = latest_ckpt / "state.json"
        if state_path.exists():
            with open(str(state_path)) as f:
                state = json.load(f)
            start_step = state.get("step", 0)
            print(f"  Resumed at step {start_step}", file=sys.stderr)

    # ── Data ───────────────────────────────────────────────────
    train_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
        seed=42,
    )

    # ── Train ──────────────────────────────────────────────────
    train_kernel(
        cfg=cfg,
        args=args,
        model=model,
        delta_modules=delta_modules,
        start_step=start_step,
        train_loader=train_loader,
        checkpoint_dir=checkpoint_dir,
    )
