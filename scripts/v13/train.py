"""
v13 — Unified Training Script (ETCH + GD phases)

Architecture: Beam/Plate Separated VSM — 8-combinator dispatch + 11-stride
hourglass (7 passes). Ternary plates shaped by ETCH phase; continuous beam
params trained by GD phase.

Phase 1 — ETCH (teacher-guided plate shaping):
  - Accumulate gradient direction signals over batches
  - Call direct_etch() with accumulated directions — flip confident positions
  - Short GD on beam params (plates frozen) for lattice alignment
  - Reset accumulators between rounds
  - Optional: skip if loading pre-etched plates

Phase 2 — GD (continuous param optimization, plates frozen):
  - CE loss + crystal lattice loss + KL dispatch + dispatch entropy
  - Cosine LR schedule with linear warmup
  - AdamW optimizer with weight decay and gradient clipping
  - Periodic checkpointing, evaluation, and logging
  - Plates frozen throughout via freeze_ternary_weights()

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

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map, tree_unflatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V13Config
from data import ShardedDataLoader
from model import V13Model, compute_crystal_diagnostics
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    # Gradient-directed etching (consensus, EMA heat)
    init_etch_states,
    accumulate_etch_heat,
    update_signal_planes,
    etch_check,
    save_etch_states,
    load_etch_states,
    surgical_adam_decay_for_etch,
    # Direct holographic etch (fast path: clean data)
    DirectionAccumulator,
    init_direction_accumulators,
    accumulate_direction,
    direct_etch,
    reset_accumulators,
)
from kernel import COMBINATOR_NAMES, N_COMBINATORS


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════════════

E_IRREDUCIBLE = 1.82               # Chinchilla irreducible entropy (nats)
LOG_V = math.log(151936)           # log(vocab_size) ≈ 11.93  — "knows nothing" ceiling

PASS_NAMES = ("L0↑", "L1↑", "L2↑", "L3", "L2↓", "L1↓", "L0↓")


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss function
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(
    model: V13Model,
    input_ids: mx.array,
    targets: mx.array,
) -> mx.array:
    """CE + crystal + dispatch losses (computed inside model._compute_loss).

    Returns the total scalar loss from the model forward pass.
    The model accumulates component losses in _last_ce, _last_crystal_loss,
    _last_kl_loss for diagnostic logging.
    """
    _logits, total_loss = model(input_ids, targets)
    return total_loss


# ══════════════════════════════════════════════════════════════════════════════
# § 3  LR schedule
# ══════════════════════════════════════════════════════════════════════════════

def cosine_lr(
    step: int,
    warmup_steps: int,
    total_steps: int,
    lr_max: float,
    lr_floor_ratio: float = 0.01,
) -> float:
    """Linear warmup → cosine decay to lr_max * lr_floor_ratio."""
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


# ══════════════════════════════════════════════════════════════════════════════
# § 4  JSONL helpers
# ══════════════════════════════════════════════════════════════════════════════

def _sanitize(obj):
    """Recursively convert NaN/Inf to None, mx/np scalars to Python."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if hasattr(obj, "item"):
        v = obj.item()
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v
    return obj


def _append_jsonl(path: Path, record: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(_sanitize(record)) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Model creation
# ══════════════════════════════════════════════════════════════════════════════

def create_model(cfg: V13Config) -> V13Model:
    """Instantiate V13Model and freeze ternary topology weights."""
    model = V13Model(cfg)
    freeze_ternary_weights(model)
    return model


def count_parameters(model: V13Model) -> dict:
    """Count beam (trainable) and plate (ternary, frozen) parameters."""
    trainable = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    total_ternary = count_ternary_weights(model)
    return {
        "trainable": trainable,
        "ternary_positions": total_ternary,
        "ternary_bytes": total_ternary * 2 // 8,
    }


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(model: V13Model, cfg: V13Config) -> dict:
    """Evaluate CE loss on held-out eval shards.

    Samples up to ~50K tokens. Returns loss, perplexity, and component
    diagnostics cached on the model during the final forward pass.
    """
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=9999,
    )

    total_loss = 0.0
    n_batches = 0
    target_tokens = 50_000
    tokens_seen = 0

    while tokens_seen < target_tokens:
        ids_np, tgts_np = next(eval_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)

        _logits, loss = model(ids, tgts)
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    ppl = math.exp(min(avg_loss, 20.0))

    result: dict = {"loss": avg_loss, "ppl": ppl}

    # Cached component diagnostics from last forward pass
    for attr in ("_last_ce", "_last_crystal_loss", "_last_kl_loss"):
        if hasattr(model, attr):
            v = getattr(model, attr)
            mx.eval(v)
            result[attr.lstrip("_")] = float(v.item())

    # Crystal lattice diagnostics (combinator embedding geometry)
    crystal = compute_crystal_diagnostics(model)
    result["crystal"] = crystal

    # Dispatch EMA (routing statistics)
    if hasattr(model, "_dispatch_ema"):
        ema = model._dispatch_ema
        mx.eval(ema)
        result["dispatch_ema"] = {
            COMBINATOR_NAMES[i]: float(ema[i].item())
            for i in range(min(N_COMBINATORS, ema.shape[0]))
        }

    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Shared-weight gradient normalization (7-pass hourglass)
# ══════════════════════════════════════════════════════════════════════════════

# Universal shared components — used in all 7 passes
_UNIVERSAL_SHARED = ("stride_stack", "combinator_dispatch", "combinator_integrate")
_N_ALL_PASSES = 7
_N_ASC_PASSES = 4   # L0↑ L1↑ L2↑ L3_apex
_N_DESC_PASSES = 3  # L2↓ L1↓ L0↓

# Ascending-only shared
_ASC_SHARED = ("s4", "mod_projs")
# Descending-only shared
_DESC_SHARED = ("s4_desc", "mod_projs_desc")


def normalize_shared_grads(grads: dict) -> dict:
    """Divide gradients of shared components by their pass-count.

    Universal components (stride_stack, dispatch, integrate) accumulate
    gradients from all 7 passes. Dividing by 7 stabilises Adam's running
    statistics and prevents scale blow-up.
    """
    all_scale = 1.0 / _N_ALL_PASSES
    asc_scale = 1.0 / _N_ASC_PASSES
    desc_scale = 1.0 / _N_DESC_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                root = new_keys[0] if new_keys else ""
                if root in _UNIVERSAL_SHARED:
                    out[k] = tree_map(lambda g: g * all_scale, v)
                elif root in _ASC_SHARED:
                    out[k] = tree_map(lambda g: g * asc_scale, v)
                elif root in _DESC_SHARED:
                    out[k] = tree_map(lambda g: g * desc_scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 8  Checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def save_checkpoint(
    model: V13Model,
    optimizer,
    step: int,
    cfg: V13Config,
    checkpoint_dir: Path,
    train_losses: list[float],
    last_eval: dict | None,
    total_etched: int,
    etch_states: dict | None,
    train_loader: ShardedDataLoader,
    phase: str = "gd",
) -> None:
    """Save model weights, optimizer state, etch states, and training metadata."""
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    # Model weights (flat safetensors-compatible via mx.savez)
    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    # Optimizer state
    if optimizer.state:
        flat_opt = dict(tree_flatten(optimizer.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    # Etch states (signal planes, heat EMAs)
    if etch_states is not None:
        save_etch_states(etch_states, str(step_dir / "etch_states.npz"))

    # Crystal diagnostics
    crystal = compute_crystal_diagnostics(model)

    # Dispatch EMA
    dispatch_ema = None
    if hasattr(model, "_dispatch_ema"):
        ema = model._dispatch_ema
        mx.eval(ema)
        dispatch_ema = {
            COMBINATOR_NAMES[i]: float(ema[i].item())
            for i in range(min(N_COMBINATORS, ema.shape[0]))
        }

    state = {
        "step": step,
        "phase": phase,
        "total_etched": total_etched,
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": last_eval or {},
        "crystal": crystal,
        "dispatch_ema": dispatch_ema,
        "data_loader": train_loader.save_state() if train_loader else {},
        "config": {
            "d_model": cfg.d_model,
            "vocab_size": cfg.vocab_size,
            "batch_size": cfg.batch_size,
            "total_steps": cfg.total_steps,
            "lr": cfg.lr,
            "seq_len": cfg.seq_len,
            "n_passes": cfg.n_passes,
            "strides": list(cfg.strides),
            "rel_lambda": cfg.rel_lambda,
        },
    }
    (step_dir / "state.json").write_text(json.dumps(state, indent=2))
    print(f"💾 Checkpoint saved: {step_dir}", file=sys.stderr, flush=True)


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    """Return the most recent valid checkpoint directory, or None."""
    if not checkpoint_dir.exists():
        return None
    for d in sorted(checkpoint_dir.glob("step_*"), reverse=True):
        if (d / "state.json").exists() and (d / "model.npz").exists():
            return d
    return None


def load_checkpoint(
    ckpt_dir: Path,
    model: V13Model,
    optimizer,
    etch_states: dict | None,
) -> tuple[int, dict, dict]:
    """Load weights, optimizer state, etch states. Returns (step, state_meta, dl_state)."""
    # Model weights
    weights = dict(mx.load(str(ckpt_dir / "model.npz")))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)

    # Optimizer state
    opt_path = ckpt_dir / "optimizer.npz"
    if opt_path.exists():
        opt_state = dict(mx.load(str(opt_path)))
        optimizer.state = tree_unflatten(list(opt_state.items()))
        mx.eval(optimizer.state)

    # Etch states
    if etch_states is not None:
        etch_path = ckpt_dir / "etch_states.npz"
        load_etch_states(etch_states, str(etch_path))

    state_meta = json.loads((ckpt_dir / "state.json").read_text())
    dl_state = state_meta.get("data_loader", {})
    step = state_meta["step"]

    print(f"📂 Loaded checkpoint: {ckpt_dir} (step {step})", file=sys.stderr)
    return step, state_meta, dl_state


# ══════════════════════════════════════════════════════════════════════════════
# § 9  Phase 1 — ETCH
# ══════════════════════════════════════════════════════════════════════════════

def run_etch_phase(
    model: V13Model,
    cfg: V13Config,
    checkpoint_dir: Path,
    train_loader: ShardedDataLoader,
    n_rounds: int = 5,
    batches_per_round: int = 200,
    gd_steps_per_round: int = 100,
    confidence_threshold: float = 0.5,
    max_flips_frac: float = 0.01,
) -> int:
    """Phase 1: Direct holographic etching.

    For each etch round:
      1. Forward+backward batches_per_round batches — accumulate direction
      2. Call direct_etch() — flip high-confidence positions
      3. Re-freeze topology weights after flipping
      4. Short GD phase (gd_steps_per_round steps) on beam params only
         with crystal lattice loss keeping combinator geometry aligned
      5. Reset direction accumulators

    Returns total etch flips applied.

    Args:
        model:               V13Model (plates frozen on entry)
        cfg:                 V13Config
        checkpoint_dir:      where to write etch phase logs
        train_loader:        data source
        n_rounds:            number of etch+GD cycles
        batches_per_round:   batches to accumulate direction signal per round
        gd_steps_per_round:  short GD steps after each etch event
        confidence_threshold: minimum direction consistency to flip (0–1)
        max_flips_frac:      max fraction of candidates to flip per event
    """
    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  Phase 1 — ETCH  ({n_rounds} rounds × {batches_per_round} batches"
          f" + {gd_steps_per_round} GD steps)",
          file=sys.stderr)
    print(f"  confidence_threshold={confidence_threshold}"
          f"  max_flips_frac={max_flips_frac}",
          file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr, flush=True)

    accumulators = init_direction_accumulators(model)
    n_modules = len(accumulators)
    print(f"  Etch modules: {n_modules}", file=sys.stderr)

    # Lightweight optimizer for etch GD rounds — AdamW on beam params only
    etch_optimizer = optim.AdamW(
        learning_rate=cfg.lr * 0.1,
        weight_decay=cfg.weight_decay,
    )
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    total_etched = 0
    etch_log_path = checkpoint_dir / "etch_phase_log.jsonl"

    for rnd in range(n_rounds):
        t_round = time.time()
        print(f"\n  ── Round {rnd + 1}/{n_rounds} ──────────────────────────────",
              file=sys.stderr, flush=True)

        # ── 1. Accumulate direction ──────────────────────────
        accum_loss = 0.0
        for bi in range(batches_per_round):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            lv, grads = loss_and_grad(model, ids, tgts)
            mx.eval(lv, grads)
            accum_loss += float(lv.item())

            # Accumulate direction signal into per-module DirectionAccumulators
            accumulate_direction(model, grads, accumulators)

        avg_loss = accum_loss / batches_per_round
        print(f"    direction accumulated: {batches_per_round} batches"
              f"  avg_loss={avg_loss:.3f}",
              file=sys.stderr, flush=True)

        # ── 2. Direct etch ──────────────────────────────────
        etch_result = direct_etch(
            model,
            accumulators,
            confidence_threshold=confidence_threshold,
            max_flips_frac=max_flips_frac,
        )
        n_flipped = etch_result["total_flipped"]
        total_etched += n_flipped

        # Re-freeze topology after plate modification
        if n_flipped > 0:
            freeze_ternary_weights(model)
            restore_ternary(model)

        print(f"    direct_etch: {n_flipped:,} flips"
              f"  ({etch_result['total_candidates']:,} candidates)"
              f"  total={total_etched:,}",
              file=sys.stderr, flush=True)

        # Emit per-type breakdown
        type_flips = etch_result.get("flips_by_type", {})
        if type_flips:
            parts = "  ".join(f"{k}={v}" for k, v in sorted(type_flips.items()))
            print(f"    by_type: {parts}", file=sys.stderr, flush=True)

        # ── 3. Short GD on beam params ───────────────────────
        # Keep combinator geometry aligned with crystal targets after plate flip
        if gd_steps_per_round > 0:
            gd_loss_sum = 0.0
            for gd_step in range(gd_steps_per_round):
                ids_np, tgts_np = next(train_loader)
                ids = mx.array(ids_np)
                tgts = mx.array(tgts_np)

                lv, grads = loss_and_grad(model, ids, tgts)
                mx.eval(lv, grads)
                gd_loss_sum += float(lv.item())

                grads = zero_ternary_grads(model, grads)

                # Gradient clipping
                flat_grads = [g for _, g in tree_flatten(grads)
                               if isinstance(g, mx.array)]
                if flat_grads:
                    grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
                    grad_norm = math.sqrt(grad_sq)
                    if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
                        s = cfg.grad_clip / (grad_norm + 1e-8)
                        grads = tree_map(lambda g: g * s, grads)

                etch_optimizer.update(model, grads)
                mx.eval(model.parameters(), etch_optimizer.state)
                restore_ternary(model)

            gd_avg = gd_loss_sum / gd_steps_per_round
            print(f"    GD ({gd_steps_per_round} steps): avg_loss={gd_avg:.3f}",
                  file=sys.stderr, flush=True)

        # ── 4. Reset accumulators ────────────────────────────
        reset_accumulators(accumulators)

        dt = time.time() - t_round
        print(f"    round {rnd + 1} done in {dt:.0f}s", file=sys.stderr, flush=True)

        # Log
        _append_jsonl(etch_log_path, {
            "round": rnd + 1,
            "timestamp": time.time(),
            "batches": batches_per_round,
            "avg_loss": avg_loss,
            "n_flipped": n_flipped,
            "total_candidates": etch_result["total_candidates"],
            "total_etched": total_etched,
            "flips_by_type": type_flips,
            "gd_steps": gd_steps_per_round,
            "gd_avg_loss": gd_avg if gd_steps_per_round > 0 else None,
            "round_seconds": dt,
        })

    print(f"\n  Phase 1 complete: {total_etched:,} total flips across {n_rounds} rounds",
          file=sys.stderr, flush=True)
    return total_etched


# ══════════════════════════════════════════════════════════════════════════════
# § 10  Phase 2 — GD
# ══════════════════════════════════════════════════════════════════════════════

def train_gd(
    cfg: V13Config,
    args: argparse.Namespace,
    model: V13Model,
    start_step: int,
    train_loader: ShardedDataLoader,
    checkpoint_dir: Path,
    last_eval: dict | None,
    etch_states: dict | None,
    total_etched: int,
) -> None:
    """Phase 2: Standard gradient-descent training loop.

    - CE + crystal lattice + KL dispatch + dispatch entropy losses
    - Cosine LR with warmup
    - AdamW + gradient clipping
    - Grad accumulation (cfg.grad_accum micro-steps per optimizer step)
    - Periodic eval, checkpoint, logging
    - Consensus etch pass every cfg.etch_interval steps (ongoing topology refinement)
    """
    total_steps = args.steps if args.steps is not None else cfg.total_steps

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  Phase 2 — GD   (steps {start_step+1}–{total_steps})", file=sys.stderr)
    print(f"  lr={cfg.lr}  warmup={cfg.warmup_steps}  wd={cfg.weight_decay}",
          file=sys.stderr)
    print(f"  grad_accum={cfg.grad_accum}  grad_clip={cfg.grad_clip}",
          file=sys.stderr)
    print(f"  batch_size={cfg.batch_size}  seq_len={cfg.seq_len}"
          f"  tokens/step={cfg.tokens_per_step:,}",
          file=sys.stderr)
    print(f"  crystal: rel_lambda={cfg.rel_lambda}"
          f"  kl_lambda={cfg.dispatch_kl_lambda}"
          f"  entropy_lambda={cfg.dispatch_entropy_lambda}",
          file=sys.stderr)
    desc_dir = "coarse→fine" if cfg.desc_stride_reverse else "fine→coarse"
    fractal = " + fractal bands" if cfg.fractal_stride_bands else ""
    print(f"  🔄 Descending stride: {desc_dir}{fractal}", file=sys.stderr, flush=True)

    # ── Optimizer ─────────────────────────────────────────────
    optimizer = optim.AdamW(
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=[0.9, 0.999],
    )
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── State ─────────────────────────────────────────────────
    train_losses: list[float] = []
    loss_window: deque[float] = deque(maxlen=50)
    t_start = time.time()

    if last_eval:
        train_losses.extend(last_eval.get("train_losses_last50", []))
        loss_window.extend(train_losses[-50:])

    # ── Warm-up forward pass (initialises optimizer state) ────
    if not (hasattr(optimizer, "state") and optimizer.state):
        ids_np, tgts_np = next(train_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)
        grads = zero_ternary_grads(model, grads)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        optimizer.learning_rate = lr

        # Holographic progressive loss warmup: linear ramp to holo_lambda
        if cfg.use_holographic_loss and cfg.holo_warmup_steps > 0:
            holo_frac = min(1.0, step / cfg.holo_warmup_steps)
            model._holo_lambda_effective = cfg.holo_lambda * holo_frac
        elif cfg.use_holographic_loss:
            model._holo_lambda_effective = cfg.holo_lambda

        # ── Gradient accumulation ─────────────────────────────
        accum_loss = 0.0
        accum_grads = None

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            lv, grads = loss_and_grad(model, ids, tgts)
            mx.eval(lv, grads)
            accum_loss += float(lv.item())

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        step_loss = accum_loss / cfg.grad_accum
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── Etch heat accumulation ─────────────────────────────
        # Feeds the consensus etch (signal planes), runs cheaply every step
        if etch_states is not None and step >= cfg.etch_warmup:
            accumulate_etch_heat(
                model, accum_grads, etch_states, alpha=cfg.etch_heat_alpha
            )

        # ── Shared-weight normalization + zero ternary grads ──
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ─────────────────────────────────
        flat_grads = [g for _, g in tree_flatten(accum_grads)
                       if isinstance(g, mx.array)]
        if flat_grads:
            grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
            grad_norm = math.sqrt(max(grad_sq, 0.0))
        else:
            grad_norm = 0.0

        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── Optimizer step ────────────────────────────────────
        optimizer.update(model, accum_grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        dt = time.time() - t0

        # ── Logging ───────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / max(dt, 1e-6)

            # Component losses cached during forward pass
            ce_val = None
            crystal_val = None
            kl_val = None
            for attr, key in [("_last_ce", "ce"),
                               ("_last_crystal_loss", "crystal"),
                               ("_last_kl_loss", "kl")]:
                if hasattr(model, attr):
                    v = getattr(model, attr)
                    mx.eval(v)
                    val = float(v.item())
                    if attr == "_last_ce":
                        ce_val = val
                    elif attr == "_last_crystal_loss":
                        crystal_val = val
                    elif attr == "_last_kl_loss":
                        kl_val = val

            # Holographic loss + φ-deviation instrumentation
            holo_val = None
            phi_devs = None
            if hasattr(model, "_last_holo_loss"):
                v = model._last_holo_loss
                mx.eval(v)
                holo_val = float(v.item())
            if hasattr(model, "_phi_deviations") and model._phi_deviations:
                phi_devs = model._phi_deviations  # list of floats

            ce_str = f"CE={ce_val:.3f}" if ce_val is not None else f"loss={step_loss:.3f}"
            crystal_str = (f" crystal={crystal_val:.4f}"
                           if crystal_val is not None else "")
            kl_str = f" kl={kl_val:.4f}" if kl_val is not None else ""
            holo_str = f" holo={holo_val:.3f}" if holo_val is not None else ""

            # Dispatch weights for live monitoring
            dispatch_str = ""
            if (hasattr(model, "combinator_dispatch") and
                    hasattr(model.combinator_dispatch, "_dispatch_weights_live")):
                dw = model.combinator_dispatch._dispatch_weights_live
                if dw is not None:
                    dw_mean = mx.mean(dw, axis=(0, 1))
                    mx.eval(dw_mean)
                    parts = [f"{COMBINATOR_NAMES[i]}={float(dw_mean[i].item()):.2f}"
                             for i in range(min(N_COMBINATORS, dw_mean.shape[0]))]
                    dispatch_str = " | " + " ".join(parts)

            print(
                f"step {step:>6d}"
                f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {ce_str}{crystal_str}{kl_str}{holo_str}"
                f" | lr {lr:.2e}"
                f" | gnorm {grad_norm:.2f}"
                f" | {tps:.0f} tok/s"
                f"{dispatch_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )

            # JSONL training log
            record: dict = {
                "step": step,
                "timestamp": time.time(),
                "loss": step_loss,
                "loss_avg50": avg50,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
            }
            if ce_val is not None:
                record["ce"] = ce_val
            if crystal_val is not None:
                record["crystal_loss"] = crystal_val
            if kl_val is not None:
                record["kl_loss"] = kl_val
            if holo_val is not None:
                record["holo_loss"] = holo_val
            if phi_devs is not None:
                # Per-pass φ-deviation: how far each pass's compression ratio
                # is from 1/φ. Ascending should trend → 0, descending diverges.
                for i, dev in enumerate(phi_devs):
                    record[f"phi_dev_pass{i}"] = dev

            # Dispatch EMA diagnostics
            if hasattr(model, "_dispatch_ema"):
                ema = model._dispatch_ema
                mx.eval(ema)
                for i, name in enumerate(COMBINATOR_NAMES):
                    if i < ema.shape[0]:
                        record[f"dispatch_ema_{name}"] = float(ema[i].item())

            _append_jsonl(checkpoint_dir / "train_log.jsonl", record)

        # ── Signal plane update (consensus etch preparation) ──
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_signal_interval == 0):
            sig_stats = update_signal_planes(
                etch_states,
                model,
                heat_thresholds=cfg.etch_heat_thresholds,
            )
            if sig_stats and step % cfg.log_interval == 0:
                active = sum(
                    1 for s in sig_stats.values()
                    if sum(s.get("votes_per_plane", [])) > 0
                )
                print(f"  🔥 signal: {active}/{len(sig_stats)} modules active",
                      file=sys.stderr, flush=True)

        # ── Consensus etch check ───────────────────────────────
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_interval == 0):
            etch_result = etch_check(
                etch_states,
                model,
                consensus_required=cfg.etch_consensus,
                max_flips=cfg.etch_max_flips_per_event,
            )
            n_flipped = etch_result["total_flipped"]
            total_etched += n_flipped

            if n_flipped > 0:
                affected = etch_result.get("affected_rows", {})
                if cfg.etch_adam_decay < 1.0 and affected:
                    surgical_adam_decay_for_etch(
                        optimizer, model, affected,
                        decay=cfg.etch_adam_decay,
                    )
                freeze_ternary_weights(model)
                restore_ternary(model)

                if cfg.etch_reset_after_flip:
                    for es in etch_states.values():
                        if hasattr(es, "reset_heat"):
                            es.reset_heat()

                etch_tempo = (
                    etch_result.get("total_candidates", 0)
                    / max(count_ternary_weights(model), 1)
                )
                print(
                    f"  ⚡ etch step {step}: {n_flipped:,} flips"
                    f" ({total_etched:,} total)"
                    f"  tempo: {etch_tempo:.6f}",
                    file=sys.stderr, flush=True,
                )

                _append_jsonl(checkpoint_dir / "etch_log.jsonl", {
                    "step": step,
                    "timestamp": time.time(),
                    "total_flipped": n_flipped,
                    "total_candidates": etch_result.get("total_candidates", 0),
                    "total_etched": total_etched,
                    "flips_by_type": etch_result.get("flips_by_type", {}),
                    "per_module": {
                        p: d for p, d in etch_result.get("per_module", {}).items()
                        if d.get("n_flipped", 0) > 0
                    },
                })

        # ── Evaluation ────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            last_eval = evaluate(model, cfg)
            print(
                f"📊 Eval @ {step}:"
                f" loss={last_eval['loss']:.3f}"
                f" ppl={last_eval['ppl']:.0f}",
                file=sys.stderr, flush=True,
            )
            if "last_ce" in last_eval:
                print(f"     CE={last_eval['last_ce']:.3f}", file=sys.stderr, flush=True)
            crystal = last_eval.get("crystal", {})
            if crystal:
                whnf_anti = crystal.get("whnf_anti_correlation", 0)
                comp_mean = crystal.get("composition_cluster_mean", 0)
                print(
                    f"     crystal: WHNF_anti={whnf_anti:.3f}"
                    f"  comp_cluster={comp_mean:.3f}",
                    file=sys.stderr, flush=True,
                )

            _append_jsonl(checkpoint_dir / "metrics_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                **last_eval,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(
                model, optimizer, step, cfg, checkpoint_dir,
                train_losses, last_eval, total_etched, etch_states,
                train_loader, phase="gd",
            )

    # ── Final checkpoint + eval ──────────────────────────────
    elapsed = time.time() - t_start
    final_eval = evaluate(model, cfg)
    print(
        f"\n{'='*72}\n"
        f"GD complete: {total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Final: loss={final_eval['loss']:.3f}  ppl={final_eval['ppl']:.0f}",
        file=sys.stderr,
    )

    save_checkpoint(
        model, optimizer, total_steps, cfg, checkpoint_dir,
        train_losses, final_eval, total_etched, etch_states,
        train_loader, phase="gd",
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 11  Main entry point
# ══════════════════════════════════════════════════════════════════════════════

def main(cfg: V13Config, args: argparse.Namespace) -> None:
    """Unified trainer: ETCH phase (optional) → GD phase."""
    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v13 — Beam/Plate Separated Hourglass VSM", file=sys.stderr)
    print("  7-pass hourglass · 11 strides · 8 combinators · Qwen3 BBPE", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────
    model = create_model(cfg)
    total_ternary = count_ternary_weights(model)
    n_beam = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}"
          f"  strides={list(cfg.strides)}",
          file=sys.stderr)
    print(f"  d_ff={cfg.d_ff}  n_passes={cfg.n_passes}"
          f"  d_register={cfg.d_register}  alpha={cfg.alpha}",
          file=sys.stderr)
    print(f"  beam_params={n_beam:,}  ternary_positions={total_ternary:,}"
          f"  ternary_bytes={total_ternary * 2 // 8 / 1024:.0f} KB",
          file=sys.stderr)
    print(f"  vocab={cfg.vocab_size}  seq_len={cfg.seq_len}"
          f"  tokens/step={cfg.tokens_per_step:,}",
          file=sys.stderr)
    print(f"  data: {cfg.data_dir}", file=sys.stderr, flush=True)

    # ── Data loaders ──────────────────────────────────────────
    train_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )

    # ── Etch states (for consensus etch during GD phase) ──────
    etch_states: dict | None = None
    if cfg.use_etching:
        etch_states = init_etch_states(model)
        print(f"  etch: {len(etch_states)} modules initialized",
              file=sys.stderr)

    # ── Resume ────────────────────────────────────────────────
    start_step = 0
    last_eval: dict | None = None
    total_etched = 0

    if args.resume is not None:
        resume_path = Path(args.resume)
        if not resume_path.is_absolute():
            resume_path = checkpoint_dir / resume_path

        if resume_path.exists():
            ckpt = resume_path
        else:
            ckpt = find_latest_checkpoint(checkpoint_dir)

        if ckpt:
            # Temporary optimizer for loading state
            _tmp_opt = optim.AdamW(learning_rate=cfg.lr, weight_decay=cfg.weight_decay)
            start_step, state_meta, dl_state = load_checkpoint(
                ckpt, model, _tmp_opt, etch_states,
            )
            total_etched = state_meta.get("total_etched", 0)
            last_eval = state_meta.get("eval_metrics")
            if dl_state:
                train_loader.load_state(dl_state)
            # Discard temp optimizer — GD phase creates its own
        else:
            print("  ⚠  No checkpoint found, starting fresh.", file=sys.stderr)

    total_steps = args.steps if args.steps is not None else cfg.total_steps

    # ── Phase routing ─────────────────────────────────────────
    phase = args.phase  # "etch" | "gd" | "both"

    if phase in ("etch", "both"):
        total_etched += run_etch_phase(
            model=model,
            cfg=cfg,
            checkpoint_dir=checkpoint_dir,
            train_loader=train_loader,
        )
        # Save post-etch checkpoint before GD
        if phase == "both":
            etch_only_dir = checkpoint_dir / "post_etch"
            etch_only_dir.mkdir(exist_ok=True)
            flat_weights = dict(tree_flatten(model.parameters()))
            mx.savez(str(etch_only_dir / "model.npz"), **flat_weights)
            if etch_states:
                save_etch_states(etch_states, str(etch_only_dir / "etch_states.npz"))
            print(f"  💾 Post-etch weights saved to {etch_only_dir}",
                  file=sys.stderr, flush=True)

    if phase in ("gd", "both"):
        train_gd(
            cfg=cfg,
            args=args,
            model=model,
            start_step=start_step,
            train_loader=train_loader,
            checkpoint_dir=checkpoint_dir,
            last_eval=last_eval,
            etch_states=etch_states,
            total_etched=total_etched,
        )


# ══════════════════════════════════════════════════════════════════════════════
# § 12  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="v13 — Beam/Plate Separated VSM (ETCH + GD unified trainer)"
    )
    parser.add_argument(
        "--checkpoint-dir", default="checkpoints/v13",
        help="Directory for checkpoints and logs (default: checkpoints/v13)",
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Path to checkpoint to resume from. "
             "Relative paths resolved against --checkpoint-dir. "
             "If not provided, starts fresh.",
    )
    parser.add_argument(
        "--phase", choices=["etch", "gd", "both"], default="gd",
        help="Training phase: 'etch' (Phase 1 only), 'gd' (Phase 2 only), "
             "'both' (ETCH then GD). Default: gd",
    )
    parser.add_argument(
        "--steps", type=int, default=None,
        help="Override cfg.total_steps for GD phase.",
    )
    # Config overrides
    parser.add_argument("--lr", type=float, default=None,
                        help="Override learning rate")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Override batch size")
    parser.add_argument("--grad-accum", type=int, default=None,
                        help="Override gradient accumulation steps")
    parser.add_argument("--seq-len", type=int, default=None,
                        help="Override sequence length")
    parser.add_argument("--log-interval", type=int, default=None,
                        help="Override log interval (steps)")
    parser.add_argument("--eval-interval", type=int, default=None,
                        help="Override eval interval (steps)")
    parser.add_argument("--checkpoint-interval", type=int, default=None,
                        help="Override checkpoint interval (steps)")
    parser.add_argument("--no-etching", action="store_true", default=False,
                        help="Disable consensus etch during GD phase")
    parser.add_argument("--etch-warmup", type=int, default=None,
                        help="Override etch warmup steps")
    parser.add_argument("--etch-interval", type=int, default=None,
                        help="Override etch check interval (steps)")
    parser.add_argument("--etch-signal-interval", type=int, default=None,
                        help="Override signal plane update interval (steps)")
    parser.add_argument("--etch-consensus", type=int, default=None,
                        help="Override etch consensus threshold (2 or 3)")
    parser.add_argument("--rel-lambda", type=float, default=None,
                        help="Override crystal lattice loss weight")
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Override data directory")

    args = parser.parse_args()
    cfg = V13Config()

    # Apply CLI overrides
    if args.lr is not None:
        cfg.lr = args.lr
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.grad_accum is not None:
        cfg.grad_accum = args.grad_accum
    if args.seq_len is not None:
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    if args.log_interval is not None:
        cfg.log_interval = args.log_interval
    if args.eval_interval is not None:
        cfg.eval_interval = args.eval_interval
    if args.checkpoint_interval is not None:
        cfg.checkpoint_interval = args.checkpoint_interval
    if args.no_etching:
        cfg.use_etching = False
    if args.etch_warmup is not None:
        cfg.etch_warmup = args.etch_warmup
    if args.etch_interval is not None:
        cfg.etch_interval = args.etch_interval
    if args.etch_signal_interval is not None:
        cfg.etch_signal_interval = args.etch_signal_interval
    if args.etch_consensus is not None:
        cfg.etch_consensus = args.etch_consensus
    if args.rel_lambda is not None:
        cfg.rel_lambda = args.rel_lambda
    if args.data_dir is not None:
        cfg.data_dir = args.data_dir
    if args.checkpoint_dir != "checkpoints/v13":
        cfg.checkpoint_dir = args.checkpoint_dir

    cfg.__post_init__()

    main(cfg, args)
