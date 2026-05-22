"""
v13 — GD Training Script (pre-etched plates, beam-only optimization)

Architecture: Beam/Plate Separated VSM — 8-combinator dispatch + 11-stride
hourglass (8 passes). Ternary plates pre-etched by extract_teacher.py via
360° tomographic sign voting — frozen forever. GD trains continuous beam
params only. Relational losses (crystal lattice, holographic) pull beams
into the groove etched into topology.

Pipeline:
  1. extract_teacher.py (360° tomographic etch) → frozen plates
  2. train.py --resume <etched-checkpoint> → GD on beams

Training loop:
  - CE loss + crystal lattice loss (exponential nucleation well) + holographic loss
  - Cosine LR schedule with linear warmup
  - AdamW optimizer with weight decay and gradient clipping
  - Periodic checkpointing, evaluation, and logging
  - FFN plates frozen via freeze_ternary_weights(exclude_prefixes=("stride_stack",))
  - Stride stack attention plates are TRAINABLE (topology learned from scratch)

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
from data import ShardedDataLoader, MixedDataLoader
from model import V13Model, crystal_lattice_loss
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════════════

E_IRREDUCIBLE = 1.82               # Chinchilla irreducible entropy (nats)
LOG_V = math.log(151936)           # log(vocab_size) ≈ 11.93  — "knows nothing" ceiling




# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss function
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(
    model: V13Model,
    input_ids: mx.array,
    targets: mx.array,
) -> mx.array:
    """CE + crystal + holographic losses (computed inside model._compute_loss).

    Returns the total scalar loss from the model forward pass.
    The model accumulates component losses in _last_ce, _last_crystal_loss,
    _last_holo_loss for diagnostic logging.
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
    """Instantiate V13Model and freeze ALL ternary topology weights.

    Session 135: ALL ternary uint32 weights are frozen — topology is
    fixed. What trains:
      - TernaryLinear.gamma (per-output-feature beam scale) — learns
        from scratch for attention, seeded from teacher for FFN
      - Learnable decay_alpha (per-stride per-head attention decay)
      - K/V/O biases, FFN beams (norm/scale/bias), RMSNorm weights
      - All controller params (S5/S4/S2/MetaS3)
      - Combinator embeddings (crystal geometry)

    The ternary topology of attention plates starts at random init.
    GD shapes the beams (gamma + decay + biases) to learn routing.
    The packed ternary weights provide the sign structure; gamma scales
    control which dimensions matter.
    """
    model = V13Model(cfg)
    freeze_ternary_weights(model)  # freeze ALL ternary weights
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

    Samples up to ~50K tokens. Returns loss, perplexity, component
    diagnostics, per-zone crystal loss, and beam magnitude stats.
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
    for attr in ("_last_ce", "_last_crystal_loss"):
        if hasattr(model, attr):
            v = getattr(model, attr)
            mx.eval(v)
            result[attr.lstrip("_")] = float(v.item())

    # Crystal lattice diagnostics (combinator embedding geometry)
    crystal = model.crystal_diagnostics()
    result["crystal"] = crystal

    # Per-zone crystal loss breakdown
    try:
        emb_all = mx.concatenate([
            model.combinator_embeddings,
            model.anti_combinator_embeddings,
        ], axis=0)
        zone_losses = {}
        for zi, (target, lam) in enumerate(
                zip(model._zone_targets, cfg.zone_lambdas)):
            zl = crystal_lattice_loss(emb_all, target)
            mx.eval(zl)
            zone_losses[f"zone_{chr(65+zi)}"] = float(zl.item())
        result["crystal_zones"] = zone_losses
    except Exception:
        pass

    # Tree-of-VSMs diagnostics
    vsm_stats = {}
    try:
        # Per-stack FFN beam magnitudes
        for name, stack in [("A", model.stack_a), ("B", model.stack_b), ("C", model.stack_c)]:
            s = stack.ffn_scale
            b = stack.ffn_bias
            mx.eval(s, b)
            vsm_stats[f"stack_{name}_ffn_scale_mean"] = float(mx.mean(mx.abs(s)).item())
            vsm_stats[f"stack_{name}_ffn_bias_rms"] = float(mx.sqrt(mx.mean(b * b)).item())

        # S5 identity state norm
        state = model.s5_identity.identity_state
        mx.eval(state)
        vsm_stats["s5_state_norm"] = float(mx.sqrt(mx.sum(state * state)).item())

        # Cached diagnostics from last forward pass
        if hasattr(model, "_last_regulation"):
            reg = model._last_regulation
            mx.eval(reg)
            for i, name in enumerate(["crystal_enf", "mod_strength", "gate_freedom", "alarm_sens"]):
                vsm_stats[f"s5_reg_{name}"] = float(reg[i].item())
        if hasattr(model, "_last_alarm"):
            vsm_stats["fire_alarm"] = float(model._last_alarm.item())
        if hasattr(model, "_last_s2_dampening"):
            damp = model._last_s2_dampening
            mx.eval(damp)
            for i in range(damp.shape[0]):
                vsm_stats[f"s2_dampening_{i}"] = float(damp[i].item())
        if hasattr(model, "_last_alg"):
            for i, alg in enumerate(model._last_alg):
                mx.eval(alg)
                vsm_stats[f"alg_{chr(65+i)}_norm"] = float(
                    mx.sqrt(mx.sum(alg * alg)).item())
    except Exception:
        pass
    if vsm_stats:
        result["vsm_stats"] = vsm_stats

    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Shared-weight gradient normalization (7-pass hourglass)
# ══════════════════════════════════════════════════════════════════════════════

# Universal shared components — used in all 8 passes.
# combinator_embeddings is EXCLUDED: its gradient comes from the direct
# crystal lattice loss (session 132 fix), not from pass accumulation.
# Dividing by 8 would attenuate the crystal alignment signal.
# Shared components in the tree: FFN plates are shared across stacks,
# stride_stack in Stack B is shared with Stack A.
_UNIVERSAL_SHARED = ("ffn_key_plate", "ffn_value_plate")
_N_ALL_PASSES = 8
_N_ASC_PASSES = 4   # L0↑ L1↑ L2↑ L3↑
_N_DESC_PASSES = 4  # L3↓ L2↓ L1↓ L0↓

# No separate ascending/descending shared components (mod_projs unified)
_ASC_SHARED: tuple[str, ...] = ()
_DESC_SHARED: tuple[str, ...] = ()


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
    train_loader: ShardedDataLoader,
) -> None:
    """Save model weights, optimizer state, and training metadata."""
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    # Model weights (flat safetensors-compatible via mx.savez)
    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    # Optimizer state
    if optimizer.state:
        flat_opt = dict(tree_flatten(optimizer.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    # Crystal diagnostics
    crystal = model.crystal_diagnostics()

    state = {
        "step": step,
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": last_eval or {},
        "crystal": crystal,
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
            "d_identity": cfg.d_identity,
            "tree_topology": {
                "stack_a": {"passes": list(cfg.stack_a.pass_indices)},
                "stack_b": {"passes": list(cfg.stack_b.pass_indices)},
                "stack_c": {"passes": list(cfg.stack_c.pass_indices)},
            },
        },
    }
    (step_dir / "state.json").write_text(json.dumps(state, indent=2))
    print(f"💾 Checkpoint saved: {step_dir}", file=sys.stderr, flush=True)


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    """Return the most recent valid checkpoint directory, or None.

    Searches for:
      1. step_* subdirectories with state.json + model.npz (training checkpoints)
      2. model.npz in checkpoint_dir root (etched checkpoint from extract_teacher.py)
    """
    if not checkpoint_dir.exists():
        return None
    # Training checkpoints (newest first)
    for d in sorted(checkpoint_dir.glob("step_*"), reverse=True):
        if (d / "state.json").exists() and (d / "model.npz").exists():
            return d
    # Etched checkpoint (flat model.npz in root)
    if (checkpoint_dir / "model.npz").exists():
        return checkpoint_dir
    return None


def load_checkpoint(
    ckpt_dir: Path,
    model: V13Model,
    optimizer,
) -> tuple[int, dict, dict]:
    """Load weights and optimizer state. Returns (step, state_meta, dl_state).

    Handles two checkpoint formats:
      - Training checkpoint: model.npz + state.json (+ optional optimizer.npz)
      - Etched checkpoint: model.npz + config.json (from extract_teacher.py, no state.json)
        → starts from step 0 with fresh optimizer state
    """
    # Model weights
    model_path = ckpt_dir / "model.npz"
    if not model_path.exists():
        raise FileNotFoundError(f"No model.npz in {ckpt_dir}")
    weights = dict(mx.load(str(model_path)))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)  # freeze ALL ternary weights
    restore_ternary(model)

    # Check for state.json (training checkpoint) vs config.json (etched checkpoint)
    state_path = ckpt_dir / "state.json"
    if state_path.exists():
        state_meta = json.loads(state_path.read_text())
        dl_state = state_meta.get("data_loader", {})
        step = state_meta["step"]

        # Optimizer state
        opt_path = ckpt_dir / "optimizer.npz"
        if opt_path.exists() and optimizer is not None:
            opt_state = dict(mx.load(str(opt_path)))
            optimizer.state = tree_unflatten(list(opt_state.items()))
            mx.eval(optimizer.state)

        print(f"📂 Loaded training checkpoint: {ckpt_dir} (step {step})",
              file=sys.stderr)
    else:
        # Etched checkpoint (from extract_teacher.py) — start from step 0
        step = 0
        state_meta = {"step": 0}
        dl_state = {}
        print(f"📂 Loaded etched checkpoint: {ckpt_dir} (starting from step 0)",
              file=sys.stderr)

    return step, state_meta, dl_state


# ══════════════════════════════════════════════════════════════════════════════
# § 9  GD Training Loop
# ══════════════════════════════════════════════════════════════════════════════

def train_gd(
    cfg: V13Config,
    args: argparse.Namespace,
    model: V13Model,
    start_step: int,
    train_loader: ShardedDataLoader,
    checkpoint_dir: Path,
    last_eval: dict | None,
) -> None:
    """GD training loop — beams only, plates frozen from etch.

    - CE + crystal lattice (exponential nucleation well) + holographic losses
    - Cosine LR with warmup
    - AdamW + gradient clipping
    - Grad accumulation (cfg.grad_accum micro-steps per optimizer step)
    - Periodic eval, checkpoint, logging
    - Plates never modified — relational losses pull beams into the etched groove
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
          f"  crystal_direct={cfg.crystal_direct_lambda}",
          file=sys.stderr)
    fractal = " + fractal bands" if cfg.fractal_stride_bands else ""
    print(f"  🌳 Tree of VSMs: A({len(cfg.stack_a.pass_indices)}p)"
          f" → B({len(cfg.stack_b.pass_indices)}p)"
          f" → C({len(cfg.stack_c.pass_indices)}p){fractal}",
          file=sys.stderr, flush=True)

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

        # Holographic loss — always on, gravity well (no warmup)
        if cfg.use_holographic_loss:
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
            for attr in ("_last_ce", "_last_crystal_loss"):
                if hasattr(model, attr):
                    v = getattr(model, attr)
                    mx.eval(v)
                    val = float(v.item())
                    if attr == "_last_ce":
                        ce_val = val
                    elif attr == "_last_crystal_loss":
                        crystal_val = val

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
            holo_str = f" holo={holo_val:.3f}" if holo_val is not None else ""

            print(
                f"step {step:>6d}"
                f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {ce_str}{crystal_str}{holo_str}"
                f" | lr {lr:.2e}"
                f" | gnorm {grad_norm:.2f}"
                f" | {tps:.0f} tok/s"
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
            if holo_val is not None:
                record["holo_loss"] = holo_val
            if phi_devs is not None:
                # Per-pass φ-deviation: how far each pass's compression ratio
                # is from 1/φ. Ascending should trend → 0, descending diverges.
                for i, dev in enumerate(phi_devs):
                    record[f"phi_dev_pass{i}"] = dev

            # VSM tree diagnostics (every log step)
            try:
                if hasattr(model, "_last_regulation"):
                    reg = model._last_regulation
                    mx.eval(reg)
                    record["s5_crystal_enf"] = float(reg[0].item())
                if hasattr(model, "_last_alarm"):
                    record["fire_alarm"] = float(model._last_alarm.item())
                if hasattr(model, "_last_s2_dampening"):
                    damp = model._last_s2_dampening
                    mx.eval(damp)
                    for i in range(damp.shape[0]):
                        record[f"s2_damp_{i}"] = float(damp[i].item())
                state = model.s5_identity.identity_state
                mx.eval(state)
                record["s5_state_norm"] = float(mx.sqrt(mx.sum(state * state)).item())
            except Exception:
                pass

            # Per-zone crystal loss (lightweight, every 4th log step)
            if step % (cfg.log_interval * 4) == 0:
                try:
                    emb_all = mx.concatenate([
                        model.combinator_embeddings,
                        model.anti_combinator_embeddings,
                    ], axis=0)
                    for zi, (target, lam) in enumerate(
                            zip(model._zone_targets, cfg.zone_lambdas)):
                        zl = crystal_lattice_loss(emb_all, target)
                        mx.eval(zl)
                        record[f"crystal_zone_{chr(65+zi)}"] = float(zl.item())
                except Exception:
                    pass

            _append_jsonl(checkpoint_dir / "train_log.jsonl", record)

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
                print(f"     CE={last_eval['last_ce']:.3f}",
                      file=sys.stderr, flush=True)
            crystal = last_eval.get("crystal", {})
            if crystal:
                whnf_anti = crystal.get("whnf_anti_correlation", 0)
                comp_mean = crystal.get("composition_cluster_mean", 0)
                print(
                    f"     crystal: WHNF_anti={whnf_anti:.3f}"
                    f"  comp_cluster={comp_mean:.3f}",
                    file=sys.stderr, flush=True,
                )
            # Per-zone crystal loss
            zones = last_eval.get("crystal_zones", {})
            if zones:
                zs = "  ".join(f"{k}={v:.4f}" for k, v in zones.items())
                print(f"     zones: {zs}", file=sys.stderr, flush=True)
            # VSM tree health
            vsm = last_eval.get("vsm_stats", {})
            if vsm:
                key_stats = {k: v for k, v in vsm.items()
                             if any(s in k for s in ("s5_", "fire_", "s2_", "alg_"))}
                if key_stats:
                    vs = "  ".join(f"{k}={v:.3f}" for k, v in key_stats.items())
                    print(f"     vsm: {vs}", file=sys.stderr, flush=True)

            _append_jsonl(checkpoint_dir / "metrics_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                **last_eval,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(
                model, optimizer, step, cfg, checkpoint_dir,
                train_losses, last_eval, train_loader,
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
        train_losses, final_eval, train_loader,
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 11  Main entry point
# ══════════════════════════════════════════════════════════════════════════════

def main(cfg: V13Config, args: argparse.Namespace) -> None:
    """GD trainer: pre-etched plates frozen, beams trained."""
    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v13 — Tree of VSMs (cortex-inspired)", file=sys.stderr)
    print("  8-pass hourglass · 11 strides · 8 combinators · Qwen3 BBPE", file=sys.stderr)
    print("  3 StrideStackVSMs · S5 self-model · learnable decay", file=sys.stderr)
    print("  FFN plates etched (frozen) · attention from scratch", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────
    model = create_model(cfg)
    total_ternary = count_ternary_weights(model)
    n_beam = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}"
          f"  strides={list(cfg.strides)}",
          file=sys.stderr)
    print(f"  d_ff={cfg.d_ff}  n_passes={cfg.n_passes}"
          f"  decay_init={cfg.decay_init_alpha}  d_identity={cfg.d_identity}",
          file=sys.stderr)
    print(f"  beam_params={n_beam:,}  ternary_positions={total_ternary:,}"
          f"  ternary_bytes={total_ternary * 2 // 8 / 1024:.0f} KB",
          file=sys.stderr)
    print(f"  vocab={cfg.vocab_size}  seq_len={cfg.seq_len}"
          f"  tokens/step={cfg.tokens_per_step:,}",
          file=sys.stderr)
    print(f"  data: {cfg.data_dir}", file=sys.stderr, flush=True)

    # ── Data loaders ──────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )
    structured_path = Path(cfg.structured_shard)
    if not structured_path.is_absolute():
        structured_path = Path(__file__).parent.parent.parent / structured_path
    if structured_path.exists() and cfg.mix_ratio > 0:
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=structured_path,
            mix_ratio=cfg.mix_ratio,
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
        )
        print(f"  mix: {cfg.mix_ratio:.0%} structured ({structured_path.name})"
              f" + {1-cfg.mix_ratio:.0%} prose",
              file=sys.stderr)
    else:
        train_loader = prose_loader
        if cfg.mix_ratio > 0:
            print(f"  ⚠  structured shard not found: {structured_path}",
                  file=sys.stderr)
            print(f"  ⚠  training on 100% prose", file=sys.stderr)

    # ── Resume ────────────────────────────────────────────────
    start_step = 0
    last_eval: dict | None = None

    if args.resume is not None:
        resume_path = Path(args.resume).resolve()

        # Priority: training checkpoints in checkpoint_dir > explicit resume path
        # This prevents accidentally reloading the etch when training checkpoints
        # exist (e.g., --resume points to etched dir but run1 has step_1000/).
        ckpt = find_latest_checkpoint(checkpoint_dir)
        if ckpt is None and resume_path.exists():
            ckpt = resume_path
        elif ckpt is None:
            ckpt = None  # nothing found anywhere

        if ckpt:
            # Temporary optimizer for loading state
            _tmp_opt = optim.AdamW(learning_rate=cfg.lr, weight_decay=cfg.weight_decay)
            start_step, state_meta, dl_state = load_checkpoint(
                ckpt, model, _tmp_opt,
            )
            last_eval = state_meta.get("eval_metrics")
            if dl_state:
                train_loader.load_state(dl_state)
            # Discard temp optimizer — GD phase creates its own
        else:
            print("  ⚠  No checkpoint found, starting fresh.", file=sys.stderr)

    # ── Train ─────────────────────────────────────────────────
    train_gd(
        cfg=cfg,
        args=args,
        model=model,
        start_step=start_step,
        train_loader=train_loader,
        checkpoint_dir=checkpoint_dir,
        last_eval=last_eval,
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 12  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="v13 — GD trainer (pre-etched plates, beam-only optimization)"
    )
    parser.add_argument(
        "--checkpoint-dir", default="checkpoints/v13",
        help="Directory for checkpoints and logs (default: checkpoints/v13)",
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Path to etched checkpoint or training checkpoint to resume from. "
             "For first run, point to extract_teacher.py output directory. "
             "If not provided, starts fresh (random plates).",
    )
    parser.add_argument(
        "--steps", type=int, default=None,
        help="Override cfg.total_steps.",
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
    parser.add_argument("--rel-lambda", type=float, default=None,
                        help="Override crystal lattice EMA coupling weight (multiplicative)")
    parser.add_argument("--crystal-direct-lambda", type=float, default=None,
                        help="Override direct crystal loss weight (additive gradient)")
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
    if args.rel_lambda is not None:
        cfg.rel_lambda = args.rel_lambda
    if args.crystal_direct_lambda is not None:
        cfg.crystal_direct_lambda = args.crystal_direct_lambda
    if args.data_dir is not None:
        cfg.data_dir = args.data_dir
    if args.checkpoint_dir != "checkpoints/v13":
        cfg.checkpoint_dir = args.checkpoint_dir

    cfg.__post_init__()

    main(cfg, args)
