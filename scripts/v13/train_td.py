"""
v13 — TernaryDescent Training Script (delta plate architecture)

Dual optimizer: Adam trains continuous beams, TernaryDescent trains
discrete delta plates.  Both run on the same backward pass.

Architecture:
  - Base plates:  full teacher crystal etch, FROZEN
  - Delta plates: initialized +1 (pass-through), trained by TD
  - Effective:    base ⊙ delta (ternary × ternary = ternary)
  - Gamma/norms:  trained by Adam (same as train.py)

Pipeline:
  1. extract_teacher.py → frozen plates (base)
  2. train_td.py --resume <etched-checkpoint> → delta plate training
  3. Periodic REDUCE: fold delta into base, reset delta, continue

The crystal lattice loss keeps the system in the β-reduction basin
while TD adapts the attention routing for stride-stack geometry.

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
    TernaryLinear,
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    surgical_adam_decay_for_etch,
)
from td import (
    TernaryDescent,
    DeltaTernaryLinear,
    convert_to_delta,
    collect_delta_params,
    reduce_all_deltas,
    freeze_delta_architecture,
    decompose_gradient,
    compute_routing_fraction,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Loss and LR
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(model, input_ids, targets):
    """CE + crystal + holographic losses."""
    _logits, total_loss = model(input_ids, targets)
    return total_loss


def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


def _sanitize(obj):
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if hasattr(obj, "item"):
        v = obj.item()
        return None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v
    return obj


def _append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(_sanitize(record)) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Model setup with delta plates
# ══════════════════════════════════════════════════════════════════════════════

def create_model_with_deltas(
    cfg: V13Config,
    convert_attention: bool = True,
    convert_ffn: bool = False,
) -> tuple[V13Model, list[tuple[str, DeltaTernaryLinear]]]:
    """Create V13Model, then convert selected TernaryLinear → DeltaTernaryLinear.

    By default converts attention plates only (stride stack Q/K/V/O projections).
    FFN plates stay as frozen TernaryLinear (architecture-independent, no delta needed).

    Returns (model, list_of_delta_modules).
    """
    model = V13Model(cfg)

    # First: freeze ALL ternary weights (standard)
    freeze_ternary_weights(model)

    # Determine which modules to convert to delta plates
    include = []
    exclude = []

    if convert_attention:
        # Stride stack attention projections
        include.append("stride_stack")
    if convert_ffn:
        include.append("ffn_key_plate")
        include.append("ffn_value_plate")

    if not convert_attention:
        exclude.append("stride_stack")
    if not convert_ffn:
        exclude.append("ffn_key_plate")
        exclude.append("ffn_value_plate")

    # Convert selected TernaryLinear modules to DeltaTernaryLinear
    converted = convert_to_delta(
        model,
        include_prefixes=tuple(include) if include else None,
        exclude_prefixes=tuple(exclude) if exclude else None,
    )

    # Freeze delta architecture (base_weight and delta_weight excluded from Adam)
    freeze_delta_architecture(model)

    # Re-freeze any remaining TernaryLinear modules
    freeze_ternary_weights(model)

    return model, converted


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Delta gradient computation
# ══════════════════════════════════════════════════════════════════════════════

def compute_all_delta_gradients(
    model: V13Model,
    loss: mx.array,
    input_ids: mx.array,
) -> list[tuple[str, mx.array, mx.array, mx.array]]:
    """Compute gradients for all delta plates using cached activations.

    During forward pass, DeltaTernaryLinear caches _x_abs_mean and _x_mean.
    We use these plus the model's loss to estimate ∂L/∂delta for each module.

    For TernaryDescent, we need (name, delta_packed, grad_delta, base_packed).

    This function uses a simpler approximation: the gradient of the loss
    w.r.t. gamma (which Adam computes) tells us the importance of each
    output dimension.  Combined with cached input statistics, this gives
    a reasonable ∂L/∂delta estimate.
    """
    delta_modules = collect_delta_params(model)
    result = []

    for path, dtl in delta_modules:
        # Get gradient of gamma (available from Adam's backward pass)
        # This is ∂L/∂gamma[i] which indicates how much each output dimension matters
        # We use the cached input activation statistics for column importance

        # Approximate ∂L/∂effective[i,j] ≈ ∂L/∂gamma[i] × input_importance[j]
        # Then ∂L/∂delta[i,j] = ∂L/∂effective[i,j] × base[i,j]

        # For now, use gamma as a proxy for row importance
        # and cached x_abs_mean for column importance
        gamma_abs = mx.abs(dtl.gamma)
        row_importance = gamma_abs / (gamma_abs.mean() + 1e-8)  # normalized

        if hasattr(dtl, "_x_abs_mean"):
            col_importance = dtl._x_abs_mean
            col_importance = col_importance / (col_importance.mean() + 1e-8)
        else:
            col_importance = mx.ones((dtl.in_features,))

        # Outer product → approximate gradient
        # ∂L/∂effective ≈ row_importance × col_importance
        grad_effective = (
            mx.expand_dims(row_importance, axis=-1)
            * mx.expand_dims(col_importance, axis=0)
        )

        # ∂L/∂delta = ∂L/∂effective × base_sign
        base_signs = unpack_ternary_mlx(dtl.base_weight).astype(mx.float32)
        grad_delta = grad_effective * base_signs

        result.append((path, dtl.delta_weight, grad_delta, dtl.base_weight))

    return result


def compute_decomposed_gradients(
    model: V13Model,
    grads: dict,
) -> tuple[
    list[tuple[str, mx.array, mx.array, mx.array]],
    dict[str, mx.array],
]:
    """Decompose gradients into routing (→ TD) and calibration (→ Adam).

    The gradient through the effective weight encodes two signals:
      ROUTING:     gradient fights the topology → TernaryDescent
      CALIBRATION: gradient agrees with topology → Adam (gamma)

    Returns:
        td_inputs:   list of (name, delta_packed, routing_grad, base_packed)
                     for TernaryDescent.step()
        gamma_filters: dict[module_path → calibration_fraction (N,)]
                     for filtering Adam's gamma gradient
    """
    delta_modules = collect_delta_params(model)
    td_inputs = []
    gamma_filters = {}

    flat_grads = dict(tree_flatten(grads))

    for path, dtl in delta_modules:
        # Get gamma gradient (∂L/∂gamma)
        gamma_key = f"{path}.gamma"
        if gamma_key in flat_grads:
            gamma_grad = flat_grads[gamma_key]
        else:
            gamma_grad = mx.abs(dtl.gamma)

        # Column importance from cached activations
        if hasattr(dtl, "_x_abs_mean"):
            col_importance = dtl._x_abs_mean
        else:
            col_importance = mx.ones((dtl.in_features,))

        # Approximate ∂L/∂effective[i,j] ≈ gamma_grad[i] × col_importance[j]
        grad_effective = (
            mx.expand_dims(gamma_grad, axis=-1)
            * mx.expand_dims(col_importance, axis=0)
        )

        # Current effective topology: base ⊙ delta
        base_unpacked = unpack_ternary_mlx(dtl.base_weight)   # (N, K) int8
        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int8
        effective_signs = (
            base_unpacked.astype(mx.int16) * delta_unpacked.astype(mx.int16)
        ).astype(mx.int8)

        # ── DECOMPOSE ──
        # Routing: gradient fights the current topology
        # Calibration: gradient agrees with the current topology
        routing, _calibration, _routing_mask = decompose_gradient(
            grad_effective, effective_signs,
        )

        # TD gets routing component directly (w.r.t. effective, NOT projected
        # through base).  TD.step() handles the base sign internally when
        # computing the desired direction for delta.
        td_inputs.append((path, dtl.delta_weight, routing, dtl.base_weight))

        # Compute per-row calibration fraction for Adam filtering
        # High routing fraction → attenuate gamma gradient (routing is TD's job)
        # Low routing fraction → full gamma gradient (calibration is Adam's job)
        routing_frac = compute_routing_fraction(grad_effective, effective_signs)
        calibration_frac = 1.0 - routing_frac  # (N,)
        gamma_filters[gamma_key] = calibration_frac

    return td_inputs, gamma_filters


def filter_gamma_grads(
    grads: dict,
    gamma_filters: dict[str, mx.array],
) -> dict:
    """Attenuate gamma gradients by calibration fraction.

    For each DeltaTernaryLinear module, the gamma gradient is scaled
    by the calibration fraction per row.  Rows where the topology is
    mostly wrong (high routing fraction) get attenuated — Adam shouldn't
    waste capacity trying to solve routing via magnitude distortion.

    Args:
        grads:         full gradient tree from nn.value_and_grad
        gamma_filters: {gamma_key → calibration_fraction (N,)} from
                       compute_decomposed_gradients

    Returns:
        modified gradient tree with filtered gamma gradients
    """
    if not gamma_filters:
        return grads

    flat = dict(tree_flatten(grads))

    for gamma_key, calib_frac in gamma_filters.items():
        if gamma_key in flat:
            # Scale gamma gradient by calibration fraction
            # calib_frac ≈ 1.0 → full gradient (correct routes, adjust magnitude)
            # calib_frac ≈ 0.0 → attenuated gradient (wrong routes, let TD handle)
            flat[gamma_key] = flat[gamma_key] * calib_frac

    return dict(tree_unflatten(list(flat.items())))


def compute_delta_gradients_from_grads(
    model: V13Model,
    grads: dict,
) -> list[tuple[str, mx.array, mx.array, mx.array]]:
    """Legacy: compute delta gradients without decomposition.

    For backwards compatibility. Use compute_decomposed_gradients() for
    the routing/calibration split.
    """
    delta_modules = collect_delta_params(model)
    result = []
    flat_grads = dict(tree_flatten(grads))

    for path, dtl in delta_modules:
        gamma_key = f"{path}.gamma"
        if gamma_key in flat_grads:
            gamma_grad = flat_grads[gamma_key]
        else:
            gamma_grad = mx.abs(dtl.gamma)

        if hasattr(dtl, "_x_abs_mean"):
            col_importance = dtl._x_abs_mean
        else:
            col_importance = mx.ones((dtl.in_features,))

        grad_effective = (
            mx.expand_dims(gamma_grad, axis=-1)
            * mx.expand_dims(col_importance, axis=0)
        )

        # Pass effective gradient directly — TD.step() handles base sign internally
        result.append((path, dtl.delta_weight, grad_effective, dtl.base_weight))

    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 4  Shared-weight gradient normalization
# ══════════════════════════════════════════════════════════════════════════════

_UNIVERSAL_SHARED = ("ffn_key_plate", "ffn_value_plate")
_N_ALL_PASSES = 8


def normalize_shared_grads(grads):
    all_scale = 1.0 / _N_ALL_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                root = new_keys[0] if new_keys else ""
                if root in _UNIVERSAL_SHARED:
                    out[k] = tree_map(lambda g: g * all_scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Training loop with dual optimizers
# ══════════════════════════════════════════════════════════════════════════════

def train_td(
    cfg: V13Config,
    args: argparse.Namespace,
    model: V13Model,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    start_step: int,
    train_loader,
    checkpoint_dir: Path,
) -> None:
    """Training loop with Adam (beams) + TernaryDescent (delta plates).

    Both optimizers share the same backward pass.  Adam updates gamma,
    norms, biases.  TD updates delta plates when gradient confidence is
    high enough.  Crystal lattice loss prevents leaving the KIBC basin.
    """
    total_steps = args.steps if args.steps else cfg.total_steps
    reduce_threshold = args.reduce_threshold
    reduce_interval = args.reduce_interval

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  TernaryDescent Training", file=sys.stderr)
    print(f"  Adam (beams) + TD (delta plates)", file=sys.stderr)
    print(f"  steps {start_step+1}–{total_steps}", file=sys.stderr)
    print(f"  TD: flip_rate={args.td_flip_rate}  warmup={args.td_warmup}"
          f"  min_conf={args.td_min_confidence}", file=sys.stderr)
    decompose_str = "ON (routing→TD, calibration→Adam)" if args.decompose_gradient else "OFF (mixed)"
    print(f"  Gradient decomposition: {decompose_str}", file=sys.stderr)
    print(f"  Reduce: interval={reduce_interval}  threshold={reduce_threshold}",
          file=sys.stderr)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)
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
        beta1=args.td_beta1,
        beta2=args.td_beta2,
    )

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── State ─────────────────────────────────────────────────
    train_losses = []
    loss_window = deque(maxlen=50)
    n_reductions = 0
    total_td_flips = 0
    td_active = False  # Schmitt trigger state — starts OFF, waits for crystal to latch
    t_start = time.time()

    # ── Warm-up forward pass (initialises Adam state) ─────────
    ids_np, tgts_np = next(train_loader)
    lv, grads = loss_and_grad(model, mx.array(ids_np), mx.array(tgts_np))
    mx.eval(lv, grads)
    grads = zero_ternary_grads(model, grads)
    adam.update(model, grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    # ── Session 142: restore optimizer state from checkpoint ──
    # The warm-up pass above initializes Adam's state dict structure.
    # If resuming from a training checkpoint, overwrite with saved moments.
    if start_step > 0:
        opt_path = checkpoint_dir / f"step_{start_step:06d}" / "optimizer.npz"
        if not opt_path.exists():
            # Also check the resume source directory (might differ from checkpoint_dir)
            resume_opt = Path(args.resume).resolve() / "optimizer.npz" if args.resume else None
            if resume_opt and resume_opt.exists():
                opt_path = resume_opt
        if opt_path.exists():
            saved_opt = dict(mx.load(str(opt_path)))
            # Adam state is a nested structure matching model parameters.
            # tree_unflatten it back into the same shape as adam.state.
            current_flat = dict(tree_flatten(adam.state))
            n_restored = 0
            n_skipped = 0
            for k, v in saved_opt.items():
                if k in current_flat and current_flat[k].shape == v.shape:
                    current_flat[k] = v
                    n_restored += 1
                else:
                    n_skipped += 1
            adam.state = tree_unflatten(list(current_flat.items()))
            mx.eval(adam.state)
            print(f"📂 Restored optimizer state from {opt_path}"
                  f" ({n_restored} arrays, {n_skipped} skipped)",
                  file=sys.stderr)
            # Re-load model weights to undo the warm-up gradient step
            model_path = checkpoint_dir / f"step_{start_step:06d}" / "model.npz"
            if not model_path.exists() and args.resume:
                model_path = Path(args.resume).resolve() / "model.npz"
            if model_path.exists():
                model.load_weights(str(model_path), strict=False)
                mx.eval(model.parameters())
                restore_ternary(model)
                print(f"📂 Re-loaded model weights (undoing warm-up step)",
                      file=sys.stderr)
        else:
            print(f"⚠  No optimizer.npz found for step {start_step}"
                  f" — Adam moments start fresh", file=sys.stderr)

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    nan_consecutive = 0  # Session 142: NaN skip/rollback counter

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        # Step counter for crystal warmup schedule
        model._training_step = step

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

        # ── Session 142: NaN skip guard ───────────────────────
        # If loss is NaN/Inf, skip this step entirely — don't poison
        # Adam moments or model weights. Log and count consecutive NaN.
        if math.isnan(step_loss) or math.isinf(step_loss):
            nan_consecutive += 1
            print(f"⚠️  NaN/Inf loss at step {step} (consecutive: {nan_consecutive})")
            if nan_consecutive >= 3:
                # Rollback: restore from last clean checkpoint
                ckpt_dirs = sorted([d for d in os.listdir(args.checkpoint_dir)
                                    if d.startswith("step_")])
                if ckpt_dirs:
                    last_ckpt = os.path.join(args.checkpoint_dir, ckpt_dirs[-1])
                    print(f"🔄 3 consecutive NaN — rolling back to {last_ckpt}")
                    model.load_weights(os.path.join(last_ckpt, "model.npz"))
                    mx.eval(model.parameters())
                    restore_ternary(model)
                nan_consecutive = 0
            continue  # skip optimizer step entirely

        # Reset NaN counter on clean step
        nan_consecutive = 0

        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── Shared-weight normalization + zero ternary grads ──
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ─────────────────────────────────
        flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
        grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads) if flat_grads else 0.0
        grad_norm = math.sqrt(max(grad_sq, 0.0))

        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── DECOMPOSE: split gradient into routing → TD, calibration → Adam ──
        td_inputs, gamma_filters = compute_decomposed_gradients(model, accum_grads)

        # Filter Adam's gamma gradient: remove routing component
        # so Adam focuses on calibration (magnitude), not routing (signs)
        if args.decompose_gradient:
            filtered_grads = filter_gamma_grads(accum_grads, gamma_filters)
        else:
            filtered_grads = accum_grads

        # ── Adam step (continuous params, calibration-only gradient) ──
        adam.update(model, filtered_grads)
        mx.eval(model.parameters(), adam.state)
        restore_ternary(model)

        # ── TernaryDescent step (delta plates, crystal-gated) ──────────
        # Schmitt trigger: hysteresis prevents rapid on/off oscillation.
        #   crystal_loss < gate (3%)    → TD activates (crystal latched, safe to flip)
        #   crystal_loss > ceiling (7%) → TD deactivates (crystal destabilized, stop)
        #   in between                 → TD stays in current state (hysteresis band)
        crystal_val_for_gate = getattr(model, "_last_crystal_loss", None)
        if crystal_val_for_gate is not None:
            mx.eval(crystal_val_for_gate)
            crystal_val_for_gate = float(crystal_val_for_gate.item())

        if crystal_val_for_gate is not None:
            if crystal_val_for_gate < args.td_crystal_gate:
                td_active = True   # crystal latched — activate
            elif crystal_val_for_gate > args.td_crystal_ceiling:
                td_active = False  # crystal destabilized — deactivate
            # else: stay in current state (hysteresis band)

        if td_active:
            td_result = td.step(td_inputs)
        else:
            # Crystal not ready or destabilized — skip TD entirely
            # Don't advance warmup counter — TD waits for crystal stability
            td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}

        # Apply any flips to the model + decay Adam moments for affected rows
        td_affected_rows: dict[str, set[int]] = {}
        for name, info in td_result["per_module"].items():
            if "new_packed" in info:
                # Find the module and update its delta weight
                for path, dtl in delta_modules:
                    if path == name:
                        dtl.delta_weight = info["new_packed"]
                        mx.eval(dtl.delta_weight)
                        break
                # Collect affected rows for Adam moment decay
                if "affected_rows" in info and info["affected_rows"]:
                    td_affected_rows[name] = info["affected_rows"]

        # Surgical Adam decay: GD was compensating for old topology.
        # TD flipped signs in these rows → Adam's moments are stale.
        # Decay them so GD can re-converge to the new topology.
        n_adam_decayed = 0
        if td_affected_rows:
            n_adam_decayed = surgical_adam_decay_for_etch(
                adam, model, td_affected_rows, decay=0.1,
            )

        total_td_flips += td_result["total_flips"]

        dt = time.time() - t0

        # ── Logging ───────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / max(dt, 1e-6)

            # Component losses
            ce_val = getattr(model, "_last_ce", None)
            crystal_val = getattr(model, "_last_crystal_loss", None)
            if ce_val is not None:
                mx.eval(ce_val)
                ce_val = float(ce_val.item())
            if crystal_val is not None:
                mx.eval(crystal_val)
                crystal_val = float(crystal_val.item())

            # Delta plate stats
            delta_stats_all = {}
            total_changed = 0.0
            for path, dtl in delta_modules:
                ds = dtl.delta_stats()
                delta_stats_all[path] = ds
                total_changed += ds["changed_frac"]
            avg_changed = total_changed / max(len(delta_modules), 1)

            ce_str = f"CE={ce_val:.3f}" if ce_val is not None else f"loss={step_loss:.3f}"
            crystal_str = f" crystal={crystal_val:.4f}" if crystal_val is not None else ""

            # Parity diagnostics (session 142)
            parity_str = ""
            parity_val = getattr(model, "_last_parity_loss", None)
            if parity_val is not None:
                mx.eval(parity_val)
                parity_str = f" parity={float(parity_val.item()):.4f}"

            # Categorical geometry diagnostics
            geom_parts = []
            for attr, label in [("_last_adjunction_kurtosis", "adj_κ"),
                                ("_last_hyperbolic_loss", "hyp"),
                                ("_last_coherence_loss", "coh")]:
                v = getattr(model, attr, None)
                if v is not None:
                    mx.eval(v)
                    geom_parts.append(f"{label}={float(v.item()):.3f}")
            geom_str = " " + " ".join(geom_parts) if geom_parts else ""

            gate_icon = "🔓" if td_active else "🔒"
            adam_decay_str = f" adam_decay={n_adam_decayed}" if n_adam_decayed > 0 else ""
            td_str = f" {gate_icon} td={td_result['total_flips']} Δ={avg_changed:.3f}{adam_decay_str}"

            print(
                f"step {step:>6d}"
                f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {ce_str}{crystal_str}{parity_str}{geom_str}"
                f" | lr {lr:.2e}"
                f" | gnorm {grad_norm:.2f}"
                f" | {tps:.0f} tok/s"
                f" |{td_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )

            # JSONL log
            record = {
                "step": step,
                "timestamp": time.time(),
                "loss": step_loss,
                "loss_avg50": avg50,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
                "td_flips": td_result["total_flips"],
                "td_total_flips": total_td_flips,
                "td_adam_decayed": n_adam_decayed,
                "td_in_warmup": td_result["in_warmup"],
                "delta_avg_changed": avg_changed,
                "n_reductions": n_reductions,
            }
            if ce_val is not None:
                record["ce"] = ce_val
            if crystal_val is not None:
                record["crystal_loss"] = crystal_val
            # Parity loss (session 142 — hierarchical error correction)
            parity_val = getattr(model, "_last_parity_loss", None)
            if parity_val is not None:
                mx.eval(parity_val)
                record["parity_loss"] = float(parity_val.item())
            parity_errs = getattr(model, "_last_parity_errors", None)
            if parity_errs is not None:
                mx.eval(parity_errs)
                parity_levels = getattr(model, "_parity_levels", [3, 4, 5, 6, 8])
                for k, err in zip(parity_levels, parity_errs.tolist()):
                    record[f"parity_err_{k}d"] = err

            # Categorical geometry losses
            for attr, key in [("_last_adjunction_loss", "adjunction_loss"),
                              ("_last_adjunction_kurtosis", "adjunction_kurtosis"),
                              ("_last_hyperbolic_loss", "hyperbolic_loss"),
                              ("_last_coherence_loss", "coherence_loss")]:
                v = getattr(model, attr, None)
                if v is not None:
                    mx.eval(v)
                    record[key] = float(v.item())

            # Per-module delta stats (every 4th log)
            if step % (cfg.log_interval * 4) == 0:
                for path, ds in delta_stats_all.items():
                    for k, v in ds.items():
                        record[f"delta.{path}.{k}"] = v

            # TD per-module confidence
            for name, info in td_result["per_module"].items():
                record[f"td.{name}.flips"] = info["flips"]
                record[f"td.{name}.candidates"] = info["candidates"]
                record[f"td.{name}.confidence"] = info["mean_confidence"]

            # Routing/calibration split stats (every 4th log)
            if step % (cfg.log_interval * 4) == 0 and args.decompose_gradient:
                for gamma_key, calib_frac in gamma_filters.items():
                    mx.eval(calib_frac)
                    mean_calib = float(calib_frac.mean().item())
                    mean_routing = 1.0 - mean_calib
                    path_short = gamma_key.replace(".gamma", "")
                    record[f"routing_frac.{path_short}"] = mean_routing
                    record[f"calibration_frac.{path_short}"] = mean_calib

            _append_jsonl(checkpoint_dir / "train_td_log.jsonl", record)

        # ── Periodic reduction ────────────────────────────────
        if reduce_interval > 0 and step % reduce_interval == 0 and step > start_step:
            # Check if delta has converged enough to reduce
            max_changed = max(
                dtl.delta_stats()["changed_frac"] for _, dtl in delta_modules
            )

            if max_changed < reduce_threshold:
                print(
                    f"\n🔄 REDUCE @ step {step}: max_changed={max_changed:.4f}"
                    f" < threshold={reduce_threshold}",
                    file=sys.stderr,
                )
                n_reduced = reduce_all_deltas(model)
                td.reset()
                n_reductions += 1
                print(
                    f"   Reduced {n_reduced} modules. "
                    f"Delta plates reset to +1. TD state cleared."
                    f" (reduction #{n_reductions})",
                    file=sys.stderr, flush=True,
                )
            else:
                print(
                    f"\n⏳ Reduce check @ step {step}: max_changed={max_changed:.4f}"
                    f" > threshold={reduce_threshold} — not ready",
                    file=sys.stderr, flush=True,
                )

        # ── Evaluation ────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            eval_result = _evaluate(model, cfg)
            print(
                f"📊 Eval @ {step}:"
                f" loss={eval_result['loss']:.3f}"
                f" ppl={eval_result['ppl']:.0f}",
                file=sys.stderr, flush=True,
            )
            crystal = eval_result.get("crystal", {})
            if crystal:
                whnf_anti = crystal.get("whnf_anti_correlation", 0)
                comp_mean = crystal.get("composition_cluster_mean", 0)
                i_sep = crystal.get("i_separation", 0)
                cross_crys = crystal.get("cross_crystal_mean", 0)
                print(
                    f"     crystal: WHNF_anti={whnf_anti:.3f}"
                    f"  comp_cluster={comp_mean:.3f}"
                    f"  I_sep={i_sep:.3f}"
                    f"  cross={cross_crys:.3f}",
                    file=sys.stderr, flush=True,
                )
            _append_jsonl(checkpoint_dir / "td_metrics_log.jsonl", {
                "step": step, "timestamp": time.time(), **eval_result,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            _save_checkpoint(model, adam, td, step, cfg, checkpoint_dir,
                             train_losses, n_reductions, total_td_flips)

    # ── Final ─────────────────────────────────────────────────
    elapsed = time.time() - t_start
    final_eval = _evaluate(model, cfg)
    print(
        f"\n{'='*72}\n"
        f"TD training complete: {total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Final: loss={final_eval['loss']:.3f}  ppl={final_eval['ppl']:.0f}\n"
        f"Total TD flips: {total_td_flips:,}  Reductions: {n_reductions}",
        file=sys.stderr,
    )
    _save_checkpoint(model, adam, td, total_steps, cfg, checkpoint_dir,
                     train_losses, n_reductions, total_td_flips)


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Evaluation and checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def _evaluate(model, cfg):
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
    tokens_seen = 0
    while tokens_seen < 50_000:
        ids_np, tgts_np = next(eval_loader)
        _logits, loss = model(mx.array(ids_np), mx.array(tgts_np))
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    result = {"loss": avg_loss, "ppl": math.exp(min(avg_loss, 20.0))}

    crystal = model.crystal_diagnostics()
    result["crystal"] = crystal

    # Delta plate statistics
    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        result["delta_stats"] = delta_stats

    return result


def _save_checkpoint(model, adam, td, step, cfg, checkpoint_dir,
                     train_losses, n_reductions, total_td_flips):
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    if adam.state:
        flat_opt = dict(tree_flatten(adam.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    # Save delta plate snapshots separately for comparison across runs.
    # Each delta plate is saved as its own .npz with both the delta weights
    # and diagnostic stats. The base plate is NOT saved here (it's frozen
    # and identical across runs — save disk space).
    delta_snapshots = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_key = path.replace(".", "_")
            delta_unpacked = unpack_ternary_mlx(mod.delta_weight)
            mx.eval(delta_unpacked)
            delta_snapshots[f"{delta_key}_delta"] = delta_unpacked
            delta_snapshots[f"{delta_key}_stats"] = mx.array([
                float((delta_unpacked == 1).sum().item()),   # n_keep
                float((delta_unpacked == -1).sum().item()),  # n_flip
                float((delta_unpacked == 0).sum().item()),   # n_block
                float(delta_unpacked.size),                  # total
            ])
    if delta_snapshots:
        mx.savez(str(step_dir / "delta_plates.npz"), **delta_snapshots)

    state = {
        "step": step,
        "train_losses_last50": train_losses[-50:],
        "n_reductions": n_reductions,
        "total_td_flips": total_td_flips,
        "td_step_count": td.step_count,
    }

    # Per-module delta stats in the state file for quick inspection
    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        state["delta_stats"] = delta_stats

    (step_dir / "state.json").write_text(json.dumps(_sanitize(state), indent=2))
    print(f"💾 Checkpoint: {step_dir}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# § 7  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="v13 — TernaryDescent trainer (delta plates + Adam beams)"
    )
    parser.add_argument("--checkpoint-dir", default="checkpoints/v13-td")
    parser.add_argument("--resume", type=str, default=None,
                        help="Etched checkpoint or training checkpoint to resume")
    parser.add_argument("--steps", type=int, default=None)

    # TernaryDescent params
    parser.add_argument("--td-flip-rate", type=float, default=0.001,
                        help="Max fraction of ternary weights to flip per step")
    parser.add_argument("--td-warmup", type=int, default=25,
                        help="TD warmup steps AFTER crystal latches (no flips before this)")
    parser.add_argument("--td-crystal-gate", type=float, default=0.03,
                        help="Crystal loss threshold for TD activation (Schmitt trigger "
                             "lower bound). TD activates once crystal_loss drops below "
                             "this value. Default 0.03 (3%%).")
    parser.add_argument("--td-crystal-ceiling", type=float, default=0.07,
                        help="Crystal loss ceiling (Schmitt trigger upper bound). TD "
                             "deactivates if crystal_loss rises above this. Reactivates "
                             "when it drops below --td-crystal-gate again. Default 0.07 (7%%).")
    parser.add_argument("--td-min-confidence", type=float, default=0.3,
                        help="Minimum signal-to-noise ratio for flip candidates")
    parser.add_argument("--td-beta1", type=float, default=0.9,
                        help="Direction EMA decay")
    parser.add_argument("--td-beta2", type=float, default=0.999,
                        help="Magnitude EMA decay")

    # Reduction params (disabled by default — fold manually when ready)
    parser.add_argument("--reduce-interval", type=int, default=0,
                        help="Check for reduction every N steps (0=never, default: never)")
    parser.add_argument("--reduce-threshold", type=float, default=0.05,
                        help="Reduce when max changed_frac < threshold (e.g. 0.05 = >95%% still +1)")

    # What to convert
    parser.add_argument("--convert-ffn", action="store_true",
                        help="Also convert FFN plates to delta (default: attention only)")

    # Gradient decomposition
    parser.add_argument("--decompose-gradient", action="store_true", default=True,
                        help="Decompose gradient into routing→TD + calibration→Adam (default: on)")
    parser.add_argument("--no-decompose-gradient", dest="decompose_gradient",
                        action="store_false",
                        help="Disable gradient decomposition (mixed gradient to both optimizers)")

    # Config overrides
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--crystal-direct-lambda", type=float, default=None,
                        help="Override direct crystal loss floor (additive gradient)")
    parser.add_argument("--crystal-direct-lambda-start", type=float, default=None,
                        help="Override crystal warmup start (anneals to --crystal-direct-lambda)")
    parser.add_argument("--crystal-warmup-steps", type=int, default=None,
                        help="Override crystal warmup schedule length (0=no warmup)")
    # Categorical geometry losses (session 140 probes)
    parser.add_argument("--adjunction-lambda", type=float, default=None,
                        help="Cross-stack rank-1 concentration loss weight")
    parser.add_argument("--hyperbolic-lambda", type=float, default=None,
                        help="Monotonic norm growth loss weight")
    parser.add_argument("--coherence-lambda", type=float, default=None,
                        help="Adjacent-token compositional coherence loss weight")

    args = parser.parse_args()
    cfg = V13Config()

    if args.lr is not None:
        cfg.lr = args.lr
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.seq_len is not None:
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    if args.data_dir is not None:
        cfg.data_dir = args.data_dir
    if args.crystal_direct_lambda is not None:
        cfg.crystal_direct_lambda = args.crystal_direct_lambda
    if args.crystal_direct_lambda_start is not None:
        cfg.crystal_direct_lambda_start = args.crystal_direct_lambda_start
    if args.crystal_warmup_steps is not None:
        cfg.crystal_warmup_steps = args.crystal_warmup_steps
    if args.adjunction_lambda is not None:
        cfg.adjunction_lambda = args.adjunction_lambda
    if args.hyperbolic_lambda is not None:
        cfg.hyperbolic_lambda = args.hyperbolic_lambda
    if args.coherence_lambda is not None:
        cfg.coherence_lambda = args.coherence_lambda
    cfg.__post_init__()

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v13 — TernaryDescent Training", file=sys.stderr)
    print("  Adam (continuous beams) + TD (discrete delta plates)", file=sys.stderr)
    print("  Base plates frozen (teacher crystal)", file=sys.stderr)
    print("  Delta plates learn stride-stack adaptations", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model: load weights FIRST, then convert to delta ─────
    # The etched checkpoint has TernaryLinear keys (*.weight).
    # DeltaTernaryLinear expects *.base_weight and *.delta_weight.
    # Loading BEFORE conversion ensures the etched plates land in
    # the right TernaryLinear.weight, which then becomes base_weight
    # when convert_to_delta() runs.
    model = V13Model(cfg)
    freeze_ternary_weights(model)

    start_step = 0
    if args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            weights = dict(mx.load(str(resume_path / "model.npz")))

            # Filter out S4/S5 controller weights that may have changed shape
            # (session 140: S4 input widened by d_identity, S5 health input widened).
            # These are tiny modules — random init is fine for the new architecture.
            reinit_prefixes = ("s4.", "s5_identity.")
            model_params = dict(tree_flatten(model.parameters()))
            filtered = []
            n_skipped = 0
            for k, v in weights.items():
                if any(k.startswith(p) for p in reinit_prefixes):
                    # Only load if shape matches (forward-compatible)
                    if k in model_params and model_params[k].shape == v.shape:
                        filtered.append((k, v))
                    else:
                        n_skipped += 1
                else:
                    filtered.append((k, v))
            if n_skipped > 0:
                print(f"  ⚠ Skipped {n_skipped} S4/S5 weights (shape mismatch — re-initialized)",
                      file=sys.stderr)

            model.load_weights(filtered, strict=False)
            mx.eval(model.parameters())
            freeze_ternary_weights(model)
            restore_ternary(model)

            state_path = resume_path / "state.json"
            if state_path.exists():
                state = json.loads(state_path.read_text())
                start_step = state.get("step", 0)
            print(f"📂 Loaded etched weights from {resume_path} (step {start_step})",
                  file=sys.stderr)

    # NOW convert TernaryLinear → DeltaTernaryLinear.
    # The etched .weight becomes .base_weight (frozen).
    # A fresh .delta_weight is initialized to all +1 (pass-through).
    include = []
    exclude = []
    if True:  # always convert attention (all 3 stacks)
        include.append("stack_a.stride_stack")
        include.append("stack_b.stride_stack")
        include.append("stack_c.stride_stack")
    if args.convert_ffn:
        include.append("ffn_key_plate")
        include.append("ffn_value_plate")
    else:
        exclude.append("ffn_key_plate")
        exclude.append("ffn_value_plate")

    delta_modules = convert_to_delta(
        model,
        include_prefixes=tuple(include) if include else None,
        exclude_prefixes=tuple(exclude) if exclude else None,
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    n_beam = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    n_delta = sum(dtl.out_features * dtl.in_features for _, dtl in delta_modules)
    total_ternary = count_ternary_weights(model)

    print(f"\n  beam_params={n_beam:,}", file=sys.stderr)
    print(f"  delta_positions={n_delta:,} (TD-managed)", file=sys.stderr)
    print(f"  delta_modules={len(delta_modules)}", file=sys.stderr)
    print(f"  ternary_total={total_ternary:,}", file=sys.stderr, flush=True)

    # ── Data ──────────────────────────────────────────────────
    train_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )

    # ── Train ─────────────────────────────────────────────────
    train_td(
        cfg=cfg,
        args=args,
        model=model,
        delta_modules=delta_modules,
        start_step=start_step,
        train_loader=train_loader,
        checkpoint_dir=checkpoint_dir,
    )
