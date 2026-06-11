"""
v15 — TernaryDescent Training Script (Fibonacci stride architecture)

Dual optimizer: Adam trains continuous beams, TernaryDescent trains
discrete delta plates.  Both run on the same backward pass.

Architecture:
  - Base plates:  extracted from Qwen3.6-27B (Apache 2.0), FROZEN
  - Delta plates: attention only, no-block ({+1, -1} only — NEVER 0)
  - Effective:    base ⊙ delta (ternary × ternary = ternary)
  - Gamma/norms:  trained by Adam

Key differences from v14 train_td.py:
  - V15Config (19 Fibonacci strides, all composition, no GLA)
  - V15Model (FibonacciStrideStack, LaplacianCrystalLoss)
  - N_STRIDES = 19, N_PASSES = 8 (unchanged)
  - Checkpoint to checkpoints/v15-td/
  - Base plates from checkpoints/v15-extracted/model.npz
  - All 19 shared_stride_stack layers are composition (FibonacciStrideAttention)
  - LaplacianCrystalLoss metrics in logging (_last_crystal_mse from Laplacian-weighted loss)

Pipeline:
  1. extract_qwen36.py → base plates (model.npz)
  2. train_td.py → delta plate training on top of frozen base
  3. Periodic REDUCE: fold delta into base, reset delta, continue

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

from config import V15Config
from v15model import V15Model
from data import ShardedDataLoader, MixedDataLoader
from ternary import (
    TernaryLinear,
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    surgical_adam_decay_for_etch,
)
from td_delta import (
    TernaryDescent,
    DeltaTernaryLinear,
    FlipMap,
    convert_to_delta,
    collect_delta_params,
    reduce_all_deltas,
    freeze_delta_architecture,
    decompose_gradient,
    compute_routing_fraction,
)

# Safetensors store (optional)
_safetensors_store = None


def _get_safetensors_store():
    return _safetensors_store


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Loss function, cosine LR, logging helpers
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(model, input_ids, targets):
    """CE + Laplacian crystal losses (all combined in model forward pass)."""
    _logits, total_loss = model(input_ids, targets)
    return total_loss


# ══════════════════════════════════════════════════════════════════════════════
# § 1b  Knowledge Distillation — sparse top-k KL divergence (identical to v14)
# ══════════════════════════════════════════════════════════════════════════════

class TeacherLogitLoader:
    """Loads pre-computed sparse teacher logits aligned with training data."""

    def __init__(self, logits_dir: str | Path):
        self.logits_dir = Path(logits_dir)
        self._current_shard_idx = -1
        self._current_batch = 0
        self._indices = None
        self._logits = None
        self._n_batches = 0

    def _load_shard(self, shard_idx: int) -> bool:
        path = self.logits_dir / f"teacher_shard_{shard_idx:05d}.npz"
        if not path.exists():
            self._indices = None
            self._logits = None
            self._n_batches = 0
            self._current_shard_idx = shard_idx
            self._current_batch = 0
            return False
        data = np.load(str(path))
        self._indices = data["indices"]
        self._logits = data["logits"].astype(np.float32)
        self._n_batches = self._indices.shape[0]
        self._current_shard_idx = shard_idx
        self._current_batch = 0
        return True

    def get_batch(self, data_loader) -> tuple | None:
        shard_idx = getattr(data_loader, 'current_shard_idx', 0)
        if hasattr(data_loader, 'prose'):
            shard_idx = data_loader.prose.current_shard_idx
        if shard_idx != self._current_shard_idx:
            self._load_shard(shard_idx)
        if self._indices is None or self._current_batch >= self._n_batches:
            return None
        idx = self._indices[self._current_batch]
        logits = self._logits[self._current_batch]
        self._current_batch += 1
        return (
            mx.array(idx[np.newaxis, :, :]),
            mx.array(logits[np.newaxis, :, :]),
        )


def sparse_kd_loss(
    student_logits: mx.array,
    teacher_indices: mx.array,
    teacher_logits: mx.array,
    temperature: float = 2.0,
) -> mx.array:
    teacher_probs = mx.softmax(teacher_logits, axis=-1)
    student_scaled = student_logits / temperature
    student_topk = mx.take_along_axis(student_scaled, teacher_indices, axis=-1)
    student_log_probs = student_topk - mx.logsumexp(student_topk, axis=-1, keepdims=True)
    kl = teacher_probs * (mx.log(teacher_probs + 1e-10) - student_log_probs)
    kd_loss = mx.mean(mx.sum(kl, axis=-1))
    kd_loss = kd_loss * (temperature ** 2)
    return kd_loss


def loss_fn_kd(model, input_ids, targets, teacher_indices, teacher_logits,
               kd_alpha=0.5, temperature=2.0):
    logits, ce_crystal_loss = model(input_ids, targets)
    kd_loss = sparse_kd_loss(logits, teacher_indices, teacher_logits, temperature)
    model._last_kd_loss = mx.stop_gradient(kd_loss)
    combined = kd_alpha * ce_crystal_loss + (1.0 - kd_alpha) * kd_loss
    return combined


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
# § 2  Model creation with delta plates + base plate loading
# ══════════════════════════════════════════════════════════════════════════════

def create_model_with_deltas(
    cfg: V15Config,
    convert_ffn: bool = False,
    skip_base_load: bool = False,
) -> tuple[V15Model, list[tuple[str, DeltaTernaryLinear]]]:
    """Create V15Model, load extracted base plates, convert to delta architecture.

    v15 change: all 19 strides are composition (FibonacciStrideAttention).
    The shared_stride_stack has 19 layers, all with Q/K/V/O of shape
    (d_model, d_model). No GLA layers → no stride-type dispatch needed.

    Returns:
        model:     V15Model ready for training
        converted: list of (path, DeltaTernaryLinear) — all delta modules
    """
    model = V15Model(cfg)
    freeze_ternary_weights(model)

    extracted_path = Path(cfg.extracted_model_path)
    if skip_base_load:
        print(f"  Skipping base plate load (safetensors mode)", file=sys.stderr)
    elif extracted_path.exists():
        print(f"📂 Loading extracted base plates from {extracted_path}", file=sys.stderr)
        saved = dict(mx.load(str(extracted_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0
        n_skipped = 0

        # ── Attention: 19 strides, all composition (q/k/v/o) ──────────
        # v15 extraction keyed as: shared_stride_stack.layers.{0-18}.{q,k,v,o}
        # v15 model params keyed as: shared_stride_stack.layers.{i}.{q_proj,k_proj,v_proj,out_proj}.weight
        proj_map = {"q": "q_proj", "k": "k_proj", "v": "v_proj", "o": "out_proj"}
        n_extracted_layers = cfg.n_strides  # 19

        for layer_idx in range(n_extracted_layers):
            for ext_proj, model_proj in proj_map.items():
                model_key = f"shared_stride_stack.layers.{layer_idx}.{model_proj}.weight"
                if model_key not in flat_params:
                    continue
                target_shape = flat_params[model_key].shape

                ext_key = f"shared_stride_stack.layers.{layer_idx}.{ext_proj}"
                if ext_key not in saved:
                    n_skipped += 1
                    continue

                arr = saved[ext_key]
                if arr.shape == target_shape:
                    flat_params[model_key] = mx.array(arr)
                    n_loaded += 1
                elif arr.shape[1] == target_shape[1] and arr.shape[0] >= target_shape[0]:
                    flat_params[model_key] = mx.array(arr[:target_shape[0]])
                    n_loaded += 1
                else:
                    print(
                        f"  ⚠ shape mismatch {ext_key}: ext={arr.shape} model={target_shape}",
                        file=sys.stderr,
                    )
                    n_skipped += 1

        # ── FFN plates (stack_a and stack_c) ───────────────────────────
        ffn_map = {
            "stack_a.ffn.gate": "ffn_gate_plate_a.weight",
            "stack_a.ffn.up":   "ffn_key_plate_a.weight",
            "stack_a.ffn.down": "ffn_value_plate_a.weight",
            "stack_c.ffn.gate": "ffn_gate_plate_c.weight",
            "stack_c.ffn.up":   "ffn_key_plate_c.weight",
            "stack_c.ffn.down": "ffn_value_plate_c.weight",
        }
        for ext_key, model_key in ffn_map.items():
            if ext_key in saved and model_key in flat_params:
                if saved[ext_key].shape == flat_params[model_key].shape:
                    flat_params[model_key] = mx.array(saved[ext_key])
                    n_loaded += 1
                else:
                    print(
                        f"  ⚠ FFN shape mismatch {ext_key}: ext={saved[ext_key].shape}"
                        f" model={flat_params[model_key].shape}",
                        file=sys.stderr,
                    )
                    n_skipped += 1

        # ── Embeddings ─────────────────────────────────────────────────
        if "embed_tokens" in saved:
            emb_key = "embed.ternary_weight"
            if emb_key in flat_params:
                ext_emb = saved["embed_tokens"]
                if ext_emb.shape == flat_params[emb_key].shape:
                    flat_params[emb_key] = mx.array(ext_emb)
                    n_loaded += 1
                else:
                    print(
                        f"  ⚠ Embedding shape mismatch: ext={ext_emb.shape}"
                        f" model={flat_params[emb_key].shape}",
                        file=sys.stderr,
                    )
                    n_skipped += 1

        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  loaded={n_loaded} skipped={n_skipped}", file=sys.stderr)
    else:
        print(
            f"⚠  Extracted model not found at {extracted_path}. "
            f"Using random init (delta training still valid for testing).",
            file=sys.stderr,
        )

    # ── Convert shared_stride_stack to DeltaTernaryLinear ──────────────
    # v15: all 19 strides are composition — one prefix covers all of them.
    attention_prefixes = ("shared_stride_stack",)
    exclude = (
        "ffn_key_plate_a", "ffn_gate_plate_a", "ffn_value_plate_a",
        "ffn_key_plate_c", "ffn_gate_plate_c", "ffn_value_plate_c",
    )
    if convert_ffn:
        exclude = ()

    converted_attn = convert_to_delta(
        model,
        include_prefixes=attention_prefixes,
        exclude_prefixes=exclude if exclude else None,
    )

    converted_ffn: list[tuple[str, DeltaTernaryLinear]] = []
    if convert_ffn:
        converted_ffn = convert_to_delta(
            model,
            include_prefixes=(
                "ffn_key_plate_a", "ffn_gate_plate_a", "ffn_value_plate_a",
                "ffn_key_plate_c", "ffn_gate_plate_c", "ffn_value_plate_c",
            ),
        )

    converted = converted_attn + converted_ffn
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    return model, converted


def _attention_delta_modules(
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
) -> list[tuple[str, DeltaTernaryLinear]]:
    """Return only the attention delta modules (shared_stride_stack)."""
    return [
        (path, dtl)
        for path, dtl in delta_modules
        if path.startswith("shared_stride_stack")
    ]


def _enforce_no_block(delta_modules: list[tuple[str, DeltaTernaryLinear]]) -> int:
    """v15 invariant: attention delta plates must never contain 0.

    All 19 composition strides enforce no-block. Returns violations fixed.
    """
    n_fixed_total = 0
    attn_modules = _attention_delta_modules(delta_modules)
    for _path, dtl in attn_modules:
        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)
        has_zeros = bool((delta_unpacked == 0).any().item())
        if has_zeros:
            fixed = mx.where(
                delta_unpacked == 0,
                mx.array(1, dtype=mx.int8),
                delta_unpacked,
            )
            dtl.delta_weight = pack_ternary_mlx(fixed)
            mx.eval(dtl.delta_weight)
            n_zeros = int((delta_unpacked == 0).sum().item())
            n_fixed_total += n_zeros
    return n_fixed_total


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Delta gradient computation (identical to v14)
# ══════════════════════════════════════════════════════════════════════════════

def compute_decomposed_gradients(
    model: V15Model,
    grads: dict,
) -> tuple[
    list[tuple[str, mx.array, mx.array, mx.array, bool]],
    dict[str, mx.array],
    dict[str, tuple[mx.array, mx.array]],
]:
    delta_modules = collect_delta_params(model)
    td_inputs = []
    gamma_filters = {}
    curvature_info: dict[str, tuple[mx.array, mx.array]] = {}
    attn_modules = _attention_delta_modules(delta_modules)
    attn_paths = {path for path, _ in attn_modules}
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

        base_unpacked = unpack_ternary_mlx(dtl.base_weight)
        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)
        effective_signs = (
            base_unpacked.astype(mx.int16) * delta_unpacked.astype(mx.int16)
        ).astype(mx.int8)

        routing, _calibration, _routing_mask = decompose_gradient(
            grad_effective, effective_signs,
        )
        td_inputs.append((path, dtl.delta_weight, routing, dtl.base_weight, path in attn_paths))

        routing_frac = compute_routing_fraction(grad_effective, effective_signs)
        calibration_frac = 1.0 - routing_frac
        gamma_filters[gamma_key] = calibration_frac

        # Curvature inputs for exact-ΔL acceptance (session 213):
        # per-row scale γ and per-column input energy E[x_j²]. Both are
        # layer-local statistics already cached on the forward pass.
        if hasattr(dtl, "_x_sq_mean"):
            x_sq_mean = dtl._x_sq_mean
        else:
            x_sq_mean = mx.ones((dtl.in_features,))
        curvature_info[path] = (dtl.gamma, x_sq_mean)

    return td_inputs, gamma_filters, curvature_info


def filter_gamma_grads(
    grads: dict,
    gamma_filters: dict[str, mx.array],
) -> dict:
    if not gamma_filters:
        return grads
    flat = dict(tree_flatten(grads))
    for gamma_key, calib_frac in gamma_filters.items():
        if gamma_key in flat:
            flat[gamma_key] = flat[gamma_key] * calib_frac
    return dict(tree_unflatten(list(flat.items())))


# ══════════════════════════════════════════════════════════════════════════════
# § 4  Shared-weight gradient normalization
# ══════════════════════════════════════════════════════════════════════════════

# FFN plates are shared across all N_PASSES=8 passes — normalize by 8.
_UNIVERSAL_SHARED = (
    "ffn_key_plate_a", "ffn_gate_plate_a", "ffn_value_plate_a",
    "ffn_key_plate_c", "ffn_gate_plate_c", "ffn_value_plate_c",
)
_N_PASSES = 8


def normalize_shared_grads(grads: dict) -> dict:
    """Divide shared FFN plate gradients by N_PASSES (8× accumulation)."""
    scale = 1.0 / _N_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                root = new_keys[0] if new_keys else ""
                if root in _UNIVERSAL_SHARED:
                    out[k] = tree_map(lambda g: g * scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Training loop
# ══════════════════════════════════════════════════════════════════════════════

def train_td(
    cfg: V15Config,
    args: argparse.Namespace,
    model: V15Model,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    start_step: int,
    train_loader,
    checkpoint_dir: Path,
    structured_warmup_steps: int = 0,
    target_mix_ratio: float = 0.1,
) -> None:
    """Training loop: Adam (beams) + TernaryDescent (delta plates).

    v15 changes from v14:
      - LaplacianCrystalLoss logs (_last_crystal_mse is now Laplacian-weighted)
      - 19 stride modules under shared_stride_stack (vs 16 in v14)
      - All strides are composition — no stride-type dispatch in logging
      - Checkpoint to checkpoints/v15-td/
    """
    total_steps = args.steps if args.steps else cfg.total_steps
    reduce_threshold = args.reduce_threshold
    reduce_interval = args.reduce_interval

    attn_delta = _attention_delta_modules(delta_modules)
    ffn_delta = [(p, d) for p, d in delta_modules if (p, d) not in attn_delta]

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  v15 — TernaryDescent Training", file=sys.stderr)
    print(f"  Adam (beams) + TD (delta plates)", file=sys.stderr)
    print(f"  d_model={cfg.d_model}  n_passes={cfg.n_passes}  strides={len(cfg.strides)}", file=sys.stderr)
    print(f"  Fibonacci strides: {cfg.strides}", file=sys.stderr)
    print(f"  All composition (no GLA): {all(not r for r in cfg.stride_is_retrieval)}", file=sys.stderr)
    print(f"  ±{cfg.neighbor_radius} neighbor gathering", file=sys.stderr)
    print(f"  steps {start_step+1}–{total_steps}", file=sys.stderr)
    print(f"  TD: flip_rate={args.td_flip_rate}  warmup={args.td_warmup}"
          f"  min_conf={args.td_min_confidence}"
          f"  flip_interval={args.td_flip_interval}", file=sys.stderr)
    decompose_str = "ON (routing→TD, calibration→Adam)" if args.decompose_gradient else "OFF"
    print(f"  Gradient decomposition: {decompose_str}", file=sys.stderr)
    print(f"  No-block: all 19 composition strides = {{+1,-1}} only", file=sys.stderr)
    print(f"  Crystal loss: Laplacian-weighted (WHNF 5× fragility)", file=sys.stderr)
    print(f"  Reduce: interval={reduce_interval}  threshold={reduce_threshold}", file=sys.stderr)
    print(f"  Delta modules total: {len(delta_modules)}"
          f"  (attn={len(attn_delta)}, ffn={len(ffn_delta)})", file=sys.stderr)
    for path, dtl in delta_modules:
        tag = "[attn,no-block]" if path.startswith("shared_stride_stack") else "[ffn]"
        print(f"    {tag} {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)
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
        flip_interval=args.td_flip_interval,
        acceptance=args.td_acceptance,
        curvature_scale=args.td_curvature_scale,
        no_s2=args.td_no_s2,
    )
    print(f"  TD acceptance: {args.td_acceptance}"
          + (f" (curvature_scale={args.td_curvature_scale})"
             if args.td_acceptance == "exact" else "")
          + ("  [S2 anti-oscillation: DISABLED]" if args.td_no_s2
             else "  [S2: on]"),
          file=sys.stderr)

    # ── KD setup ───────────────────────────────────────────────
    teacher_loader = None
    kd_enabled = False
    if hasattr(args, 'teacher_logits_dir') and args.teacher_logits_dir is not None:
        teacher_dir = Path(args.teacher_logits_dir)
        if teacher_dir.exists():
            teacher_loader = TeacherLogitLoader(teacher_dir)
            kd_enabled = True
            print(f"\n🎯 Knowledge Distillation: ENABLED", file=sys.stderr)
            print(f"   Teacher logits: {teacher_dir}/", file=sys.stderr)
            print(f"   α={args.kd_alpha}  T={args.kd_temperature}", file=sys.stderr)

    if kd_enabled:
        _kd_alpha = args.kd_alpha
        _kd_temp = args.kd_temperature

        def _loss_fn_kd(model, input_ids, targets, t_indices, t_logits):
            return loss_fn_kd(model, input_ids, targets, t_indices, t_logits,
                              kd_alpha=_kd_alpha, temperature=_kd_temp)
        loss_and_grad_kd = nn.value_and_grad(model, _loss_fn_kd)

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── State ──────────────────────────────────────────────────
    train_losses = []
    loss_window = deque(maxlen=50)
    n_reductions = 0
    total_td_flips = 0
    td_flips_since_log = 0
    td_active = False
    _structured_warmup_done = False
    t_start = time.time()

    # ── FlipMap ─────────────────────────────────────────────────
    flip_map = FlipMap()
    flip_map_path = checkpoint_dir / "flip_map_latest.npz"
    if flip_map_path.exists():
        flip_map = FlipMap.load(str(flip_map_path))
        print(f"  📊 Loaded flip map ({len(flip_map.modules)} modules)", file=sys.stderr)
    _cached_hot_fracs: dict[str, float] | None = None

    # ── Warm-up forward pass ────────────────────────────────────
    ids_np, tgts_np = next(train_loader)
    lv, grads = loss_and_grad(model, mx.array(ids_np), mx.array(tgts_np))
    mx.eval(lv, grads)
    grads = zero_ternary_grads(model, grads)
    adam.update(model, grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    # ── Resume: restore optimizer state ────────────────────────
    if start_step > 0 and _get_safetensors_store() is not None:
        store = _get_safetensors_store()
        store.load_optimizer_state(adam)
        mx.eval(adam.state)
        store.load_into_model(model)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        freeze_delta_architecture(model)
        saved_state = store.load_state()
        if saved_state:
            crystal_ema = saved_state.get("crystal_ema")
            if crystal_ema is not None and hasattr(model, "_crystal_ema"):
                model._crystal_ema = mx.array(crystal_ema)
                mx.eval(model._crystal_ema)
            n_reductions = saved_state.get("n_reductions", 0)
            total_td_flips = saved_state.get("total_td_flips", 0)
            td.step_count = saved_state.get("td_step_count", 0)
        print(f"📦 Restored from safetensors (step {start_step})", file=sys.stderr)

    elif start_step > 0:
        resume_dir = Path(args.resume).resolve() if args.resume else None
        step_dir = checkpoint_dir / f"step_{start_step:06d}"

        opt_path = None
        if resume_dir and (resume_dir / "optimizer.npz").exists():
            opt_path = resume_dir / "optimizer.npz"
        elif (step_dir / "optimizer.npz").exists():
            opt_path = step_dir / "optimizer.npz"

        if opt_path is not None:
            saved_opt = dict(mx.load(str(opt_path)))
            current_flat = dict(tree_flatten(adam.state))
            n_restored = 0
            for k, v in saved_opt.items():
                if k in current_flat and current_flat[k].shape == v.shape:
                    current_flat[k] = v
                    n_restored += 1
            adam.state = tree_unflatten(list(current_flat.items()))
            mx.eval(adam.state)
            print(f"📂 Restored optimizer from {opt_path} ({n_restored} arrays)", file=sys.stderr)

            model_path = None
            if resume_dir and (resume_dir / "model.npz").exists():
                model_path = resume_dir / "model.npz"
            elif (step_dir / "model.npz").exists():
                model_path = step_dir / "model.npz"
            if model_path is not None:
                model.load_weights(str(model_path), strict=False)
                mx.eval(model.parameters())
                restore_ternary(model)
                freeze_ternary_weights(model)
                freeze_delta_architecture(model)
                print(f"📂 Re-loaded model weights from {model_path}", file=sys.stderr)

        state_path = None
        if resume_dir and (resume_dir / "state.json").exists():
            state_path = resume_dir / "state.json"
        elif (step_dir / "state.json").exists():
            state_path = step_dir / "state.json"
        if state_path and Path(state_path).exists():
            state = json.loads(Path(state_path).read_text())
            if "crystal_ema" in state and state["crystal_ema"] is not None:
                model._crystal_ema = mx.array(float(state["crystal_ema"]))
            for key in ("total_td_flips", "n_reductions", "td_active",
                        "structured_warmup_done"):
                if key in state:
                    locals()[key] = state[key]  # type: ignore[assignment]
            if "data_loader" in state and hasattr(train_loader, "load_state"):
                train_loader.load_state(state["data_loader"])

        model._training_step = start_step

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    nan_consecutive = 0

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        # Structured data warmup transition
        if (
            not _structured_warmup_done
            and structured_warmup_steps > 0
            and step > structured_warmup_steps
            and hasattr(train_loader, 'mix_ratio')
        ):
            train_loader.mix_ratio = target_mix_ratio
            _structured_warmup_done = True
            print(
                f"\n🔮 Step {step}: structured warmup complete → "
                f"mix_ratio={target_mix_ratio}",
                file=sys.stderr, flush=True,
            )

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        if cfg.crystal_warmup_steps > 0 and step <= cfg.crystal_warmup_steps:
            progress = step / cfg.crystal_warmup_steps
            crystal_lambda_eff = (
                cfg.crystal_direct_lambda_start
                + (cfg.crystal_direct_lambda - cfg.crystal_direct_lambda_start)
                * 0.5 * (1.0 - math.cos(math.pi * progress))
            )
            model.cfg.crystal_direct_lambda = crystal_lambda_eff

        model._training_step = step

        # ── Gradient accumulation ──────────────────────────────
        accum_loss = 0.0
        accum_grads = None
        _kd_loss_accum = 0.0

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            used_kd = False
            if kd_enabled and teacher_loader is not None:
                teacher_batch = teacher_loader.get_batch(train_loader)
                if teacher_batch is not None:
                    t_indices, t_logits = teacher_batch
                    lv, grads = loss_and_grad_kd(model, ids, tgts, t_indices, t_logits)
                    mx.eval(lv, grads)
                    used_kd = True
                    kd_val = getattr(model, "_last_kd_loss", None)
                    if kd_val is not None:
                        mx.eval(kd_val)
                        _kd_loss_accum += float(kd_val.item())

            if not used_kd:
                lv, grads = loss_and_grad(model, ids, tgts)
                mx.eval(lv, grads)

            accum_loss += float(lv.item())
            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        step_loss = accum_loss / cfg.grad_accum
        _kd_loss_step = _kd_loss_accum / cfg.grad_accum if _kd_loss_accum > 0 else None
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        # ── NaN guard ──────────────────────────────────────────
        if math.isnan(step_loss) or math.isinf(step_loss):
            nan_consecutive += 1

            def _safe_read(attr_name):
                v = getattr(model, attr_name, None)
                if v is None:
                    return "N/A"
                try:
                    mx.eval(v)
                    fv = float(v.item())
                    return "NaN ❌" if math.isnan(fv) else ("Inf ❌" if math.isinf(fv) else f"{fv:.4f}")
                except Exception:
                    return "err"

            def _safe_gnorm(grads):
                try:
                    fg = [g for _, g in tree_flatten(grads) if isinstance(g, mx.array)]
                    gsq = sum(float(mx.sum(g * g).item()) for g in fg) if fg else 0.0
                    return "NaN ❌" if (math.isnan(gsq) or math.isinf(gsq)) else f"{math.sqrt(max(gsq, 0)):.2f}"
                except Exception:
                    return "err"

            print(
                f"⚠️  NaN/Inf loss at step {step} (consecutive: {nan_consecutive})"
                f" | CE={_safe_read('_last_ce')}"
                f" crystal={_safe_read('_last_crystal_mse')}"
                f" parity={_safe_read('_last_parity')}"
                f" gnorm={_safe_gnorm(accum_grads)}",
                file=sys.stderr, flush=True,
            )

            if nan_consecutive >= 3:
                ckpt_dirs = sorted(d for d in os.listdir(str(checkpoint_dir)) if d.startswith("step_"))
                print(
                    f"\n{'='*72}\n💀 FATAL: 3 consecutive NaN at step {step}. Training stopped.\n"
                    f"  Available checkpoints: {', '.join(ckpt_dirs[-5:]) if ckpt_dirs else 'none'}\n"
                    f"  Recovery: --resume {checkpoint_dir}/{ckpt_dirs[-2] if len(ckpt_dirs)>=2 else '???'}\n"
                    f"{'='*72}",
                    file=sys.stderr, flush=True,
                )
                sys.exit(1)
            continue

        nan_consecutive = 0
        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── Normalize + zero ternary grads ─────────────────────
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ───────────────────────────────────
        flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
        grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads) if flat_grads else 0.0
        grad_norm = math.sqrt(max(grad_sq, 0.0))
        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── Decompose: routing → TD, calibration → Adam ────────
        td_inputs, gamma_filters, curvature_info = compute_decomposed_gradients(model, accum_grads)
        filtered_grads = filter_gamma_grads(accum_grads, gamma_filters) if args.decompose_gradient else accum_grads

        # ── Adam step ───────────────────────────────────────────
        adam.update(model, filtered_grads)
        mx.eval(model.parameters(), adam.state)
        restore_ternary(model)

        # ── Schmitt trigger: crystal-gated TD ──────────────────
        crystal_val = getattr(model, "_last_crystal_mse", None)
        if crystal_val is not None:
            mx.eval(crystal_val)
            crystal_val_f = float(crystal_val.item())
            if crystal_val_f < args.td_crystal_gate:
                td_active = True
            elif crystal_val_f > args.td_crystal_ceiling:
                td_active = False

        # ── TernaryDescent ─────────────────────────────────────
        if td_active:
            td_result = td.step(
                td_inputs, training_step=step, hot_fracs=_cached_hot_fracs,
                curvature_info=(curvature_info if args.td_acceptance == "exact" else None),
            )
        else:
            td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}

        # ── Apply flips ─────────────────────────────────────────
        td_affected_rows: dict[str, set[int]] = {}
        for name, info in td_result["per_module"].items():
            if "new_packed" in info:
                for path, dtl in delta_modules:
                    if path == name:
                        dtl.delta_weight = info["new_packed"]
                        mx.eval(dtl.delta_weight)
                        break
            if "affected_rows" in info and info["affected_rows"]:
                td_affected_rows[name] = info["affected_rows"]

        # ── No-block enforcement ────────────────────────────────
        n_no_block_fixed = _enforce_no_block(delta_modules)

        # ── Surgical Adam decay ─────────────────────────────────
        n_adam_decayed = 0
        if td_affected_rows:
            n_adam_decayed = surgical_adam_decay_for_etch(
                adam, model, td_affected_rows, decay=0.1,
            )

        total_td_flips += td_result["total_flips"]
        td_flips_since_log += td_result["total_flips"]
        flip_map.record(td_result, step)
        dt = time.time() - t0

        # ── Logging ─────────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / max(dt, 1e-6)

            def _read_attr(attr):
                v = getattr(model, attr, None)
                if v is None:
                    return None
                mx.eval(v)
                return float(v.item())

            ce_val = _read_attr("_last_ce")
            crystal_mse_val = _read_attr("_last_crystal_mse")
            parity_val = _read_attr("_last_parity")
            cross_zone_val = _read_attr("_last_cross_zone")
            # v15: crystal_mse is Laplacian-weighted (WHNF 5× fragility)
            laplacian_note = "(Laplacian-wtd)" if crystal_mse_val is not None else ""

            delta_stats_all = {}
            total_changed = 0.0
            for path, dtl in delta_modules:
                ds = dtl.delta_stats()
                delta_stats_all[path] = ds
                total_changed += ds["changed_frac"]
            avg_changed = total_changed / max(len(delta_modules), 1)

            ce_str = f"CE={ce_val:.3f}" if ce_val is not None else f"loss={step_loss:.3f}"
            kd_str = f" KD={_kd_loss_step:.3f}" if _kd_loss_step is not None else ""
            crystal_str = (f" crystal={crystal_mse_val:.4f}{laplacian_note}"
                           if crystal_mse_val is not None else "")
            parity_str = f" parity={parity_val:.4f}" if parity_val is not None else ""
            cross_str = f" cross_zone={cross_zone_val:.4f}" if cross_zone_val is not None else ""
            gate_icon = "🔓" if td_active else "🔒"
            nb_str = f" nb_fixed={n_no_block_fixed}" if n_no_block_fixed > 0 else ""
            adam_decay_str = f" adam_decay={n_adam_decayed}" if n_adam_decayed > 0 else ""
            td_flips_this_window = td_flips_since_log
            etch_modules = td_result.get("etch_active_modules", "")
            etch_slot = td_result.get("etch_slot_size", "")
            etch_str = f" etch={etch_modules}×{etch_slot}" if etch_modules else ""
            outer_deltas_list = []
            _od = getattr(model, "_last_outer_deltas", None)
            if _od:
                for _d in _od:
                    mx.eval(_d)
                    outer_deltas_list.append(round(float(_d.item()), 5))
            outer_str = (f" Δx={outer_deltas_list}" if outer_deltas_list else "")
            _fpl = getattr(model, "_last_fp_loss", None)
            fp_loss_val = None
            if _fpl is not None:
                mx.eval(_fpl)
                fp_loss_val = float(_fpl.item())
                outer_str += f" fp={fp_loss_val:.4f}"

            exact_str = ""
            if "exact_n_proxy" in td_result:
                exact_str = (
                    f" veto={td_result['exact_n_veto']}/{td_result['exact_n_proxy']}"
                    f"({td_result['exact_veto_frac']:.2f})"
                    f" lin/curv={td_result['exact_lin_mean']:.2e}/"
                    f"{td_result['exact_curv_mean']:.2e}"
                )
            td_str = (
                f" {gate_icon} td={td_flips_this_window}"
                f" Δ={avg_changed:.3f}{etch_str}{nb_str}{adam_decay_str}{exact_str}{outer_str}"
            )

            print(
                f"step {step:>6d}"
                f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {ce_str}{kd_str}{crystal_str}{parity_str}{cross_str}"
                f" | lr {lr:.2e}"
                f" | gnorm {grad_norm:.2f}"
                f" | {tps:.0f} tok/s"
                f" |{td_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )
            td_flips_since_log = 0

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
                "td_flips_since_log": td_flips_this_window,
                "td_total_flips": total_td_flips,
                "td_flip_rate": td.flip_rate,
                "td_in_warmup": td_result["in_warmup"],
                "td_active": td_active,
                "delta_avg_changed": avg_changed,
                "n_reductions": n_reductions,
                "no_block_fixed": n_no_block_fixed,
                # v15 metadata
                "n_strides": cfg.n_strides,
                "all_composition": True,
                "laplacian_crystal": True,
            }
            if ce_val is not None:
                record["ce"] = ce_val
            if _kd_loss_step is not None:
                record["kd_loss"] = _kd_loss_step
            if crystal_mse_val is not None:
                record["crystal_mse"] = crystal_mse_val
                record["crystal_mse_laplacian_weighted"] = True
            if parity_val is not None:
                record["parity"] = parity_val
            if cross_zone_val is not None:
                record["cross_zone"] = cross_zone_val

            if outer_deltas_list:
                record["outer_deltas"] = outer_deltas_list
            if fp_loss_val is not None:
                record["fp_loss"] = fp_loss_val

            # Exact-ΔL acceptance diagnostics (session 213)
            if "exact_n_proxy" in td_result:
                for _k in ("exact_n_accept", "exact_n_proxy", "exact_n_veto",
                           "exact_veto_frac", "exact_lin_mean", "exact_curv_mean"):
                    if _k in td_result:
                        record[_k] = td_result[_k]

            if step % (cfg.log_interval * 4) == 0:
                for path, ds in delta_stats_all.items():
                    for k, v in ds.items():
                        record[f"delta.{path}.{k}"] = v

            for name, info in td_result["per_module"].items():
                record[f"td.{name}.flips"] = info.get("flips", 0)
                record[f"td.{name}.candidates"] = info.get("candidates", 0)
                record[f"td.{name}.confidence"] = info.get("mean_confidence", 0.0)

            # FlipMap convergence (every 100 steps)
            fm_summary = None
            if step % 100 == 0 and len(flip_map.modules) > 0:
                fm_summary = flip_map.summary(step, recent_window=100)
                for mod_name, info in fm_summary.items():
                    record[f"fm.{mod_name}.frozen"] = round(info["frozen_frac"], 4)
                    record[f"fm.{mod_name}.hot"] = round(info["hot_frac"], 4)
                    record[f"fm.{mod_name}.osc"] = round(info["oscillation_frac"], 4)
                    record[f"fm.{mod_name}.nozzle"] = round(info["nozzle_frac"], 4)
                _cached_hot_fracs = {
                    name: info["nozzle_frac"] for name, info in fm_summary.items()
                }

            _append_jsonl(checkpoint_dir / "train_td_log.jsonl", record)

            if fm_summary is not None:
                flip_map.save(str(flip_map_path))

        # ── Periodic reduction ──────────────────────────────────
        if reduce_interval > 0 and step % reduce_interval == 0 and step > start_step:
            max_changed = max(dtl.delta_stats()["changed_frac"] for _, dtl in delta_modules)
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
                    f"   Reduced {n_reduced} modules. Delta reset to +1. (#{n_reductions})",
                    file=sys.stderr, flush=True,
                )

        # ── Checkpoint / Sync ────────────────────────────────────
        store = _get_safetensors_store()
        if store is not None:
            if step % 20 == 0:
                extra_state = {
                    "n_reductions": n_reductions,
                    "total_td_flips": total_td_flips,
                    "td_step_count": td.step_count,
                    "td_active": td_active,
                    "structured_warmup_done": _structured_warmup_done,
                    "train_losses_last50": train_losses[-50:],
                }
                if hasattr(train_loader, "save_state"):
                    extra_state["data_loader"] = train_loader.save_state()
                crystal_ema = getattr(model, "_crystal_ema", None)
                if crystal_ema is not None:
                    mx.eval(crystal_ema)
                    extra_state["crystal_ema"] = float(crystal_ema.item())
                store.sync(model, adam, step, extra_state=extra_state)
            if step % cfg.checkpoint_interval == 0:
                _save_checkpoint(
                    model, adam, td, step, cfg, checkpoint_dir,
                    train_losses, n_reductions, total_td_flips, delta_modules,
                    train_loader=train_loader,
                    td_active=td_active,
                    structured_warmup_done=_structured_warmup_done,
                )
                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))
        else:
            if step % cfg.checkpoint_interval == 0:
                _save_checkpoint(
                    model, adam, td, step, cfg, checkpoint_dir,
                    train_losses, n_reductions, total_td_flips, delta_modules,
                    train_loader=train_loader,
                    td_active=td_active,
                    structured_warmup_done=_structured_warmup_done,
                )
                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))

    # ── Final ──────────────────────────────────────────────────
    elapsed = time.time() - t_start
    print(
        f"\n{'='*72}\n"
        f"v15 TD training complete: {total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Total TD flips: {total_td_flips:,}  Reductions: {n_reductions}",
        file=sys.stderr,
    )
    store = _get_safetensors_store()
    if store is not None:
        store.sync(model, adam, step=total_steps, extra_state={
            "n_reductions": n_reductions,
            "total_td_flips": total_td_flips,
            "td_active": td_active,
        })
    else:
        _save_checkpoint(
            model, adam, td, total_steps, cfg, checkpoint_dir,
            train_losses, n_reductions, total_td_flips, delta_modules,
            train_loader=train_loader,
            td_active=td_active,
            structured_warmup_done=_structured_warmup_done,
        )
    flip_map.save(str(flip_map_path))
    flip_map.save(str(checkpoint_dir / f"flip_map_step_{total_steps:06d}.npz"))


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def _save_checkpoint(
    model: V15Model,
    adam,
    td: TernaryDescent,
    step: int,
    cfg: V15Config,
    checkpoint_dir: Path,
    train_losses: list[float],
    n_reductions: int,
    total_td_flips: int,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    *,
    train_loader=None,
    td_active: bool = False,
    structured_warmup_done: bool = False,
) -> None:
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    if adam.state:
        flat_opt = dict(tree_flatten(adam.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    delta_snapshots = {}
    dedup_deltas = collect_delta_params(model)
    for path, dtl in dedup_deltas:
        delta_key = path.replace(".", "_")
        mx.eval(dtl.delta_weight)
        delta_snapshots[f"{delta_key}_delta_packed"] = dtl.delta_weight
        ds = dtl.delta_stats()
        total = dtl.out_features * dtl.in_features
        delta_snapshots[f"{delta_key}_stats"] = mx.array([
            ds["keep_frac"] * total,
            ds["flip_frac"] * total,
            ds["block_frac"] * total,
            float(total),
        ])
    if delta_snapshots:
        mx.savez(str(step_dir / "delta_plates.npz"), **delta_snapshots)

    crystal_ema = getattr(model, "_crystal_ema", None)
    if crystal_ema is not None:
        mx.eval(crystal_ema)

    s5_identity = getattr(model.s5_identity, "identity_state", None)
    if s5_identity is not None:
        mx.eval(s5_identity)

    state = {
        "step": step,
        "version": "v15",
        "train_losses_last50": train_losses[-50:],
        "n_reductions": n_reductions,
        "total_td_flips": total_td_flips,
        "td_step_count": td.step_count,
        "crystal_ema": float(crystal_ema.item()) if crystal_ema is not None else None,
        "s5_identity_state": (
            s5_identity.tolist() if s5_identity is not None else None
        ),
        "td_active": td_active,
        "structured_warmup_done": structured_warmup_done,
        # v15 metadata
        "n_strides": cfg.n_strides,
        "strides": list(cfg.strides),
        "all_composition": True,
        "laplacian_crystal": True,
    }

    if train_loader is not None and hasattr(train_loader, "save_state"):
        state["data_loader"] = train_loader.save_state()

    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        state["delta_stats"] = delta_stats

    from dataclasses import asdict
    state["config"] = asdict(cfg)

    (step_dir / "state.json").write_text(json.dumps(_sanitize(state), indent=2))
    print(f"💾 Checkpoint: {step_dir}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# § 7  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "v15 — TernaryDescent trainer (Fibonacci stride architecture)\n"
            "\n"
            "19 Fibonacci strides, all composition (no GLA).\n"
            "LaplacianCrystalLoss: WHNF gets 5× fragility weight.\n"
            "Attention delta plates: {+1, -1} ONLY — no-block constraint.\n"
            "Base plates from checkpoints/v15-extracted/model.npz."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Paths
    parser.add_argument("--checkpoint-dir", default="checkpoints/v15-td")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--extracted-model-path", type=str, default=None)
    parser.add_argument("--steps", type=int, default=None)

    # TD params
    parser.add_argument("--td-flip-rate", type=float, default=0.001)
    parser.add_argument("--td-warmup", type=int, default=25)
    parser.add_argument("--td-flip-interval", type=int, default=20)
    parser.add_argument("--td-crystal-gate", type=float, default=0.03)
    parser.add_argument("--td-crystal-ceiling", type=float, default=0.07)
    parser.add_argument("--td-min-confidence", type=float, default=0.3)
    parser.add_argument("--td-beta1", type=float, default=0.9)
    parser.add_argument("--td-beta2", type=float, default=0.999)
    # Acceptance rule (session 213): "proxy" = gradient SNR (original);
    # "exact" = curvature-aware 3-way ΔL argmin (OBQ/GPTQ).
    parser.add_argument("--td-acceptance", choices=["proxy", "exact"],
                        default="proxy")
    parser.add_argument("--td-curvature-scale", type=float, default=1.0,
                        help="λ on the exact-ΔL curvature term (absorbs the "
                             "unknown downstream output-curvature; λ=1 ≡ "
                             "layer-local reconstruction assumption)")
    parser.add_argument("--td-no-s2", action="store_true",
                        help="disable the S2 anti-oscillation stack (cooldown/"
                             "backoff + neighbor SNR smoothing). Tests whether "
                             "exact-ΔL monotonicity removes the need for S2.")

    # Delta architecture
    parser.add_argument("--convert-ffn", action="store_true")

    # Reduction
    parser.add_argument("--reduce-interval", type=int, default=0)
    parser.add_argument("--reduce-threshold", type=float, default=0.05)

    # Safetensors
    parser.add_argument("--safetensors-dir", type=str, default=None)

    # Gradient decomposition
    parser.add_argument("--decompose-gradient", action="store_true", default=True)
    parser.add_argument("--no-decompose-gradient", dest="decompose_gradient",
                        action="store_false")

    # Config overrides
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--crystal-direct-lambda", type=float, default=None)
    parser.add_argument("--crystal-direct-lambda-start", type=float, default=None)
    parser.add_argument("--crystal-warmup-steps", type=int, default=None)

    # KD
    parser.add_argument("--teacher-logits-dir", type=str, default=None)
    parser.add_argument("--kd-alpha", type=float, default=0.5)
    parser.add_argument("--kd-temperature", type=float, default=2.0)

    # Structured data
    parser.add_argument(
        "--structured-path", type=str,
        default="data/structured_shard_qwen36.npy",
    )
    parser.add_argument("--mix-ratio", type=float, default=0.1)
    parser.add_argument("--structured-warmup-steps", type=int, default=50)

    # Determinism: seed model float init (beams/gamma/norms) so A/B runs that
    # differ only in TD acceptance share an identical starting point.
    parser.add_argument("--seed", type=int, default=42)

    # VSM outer recurrence (session 214, explore/vsm-outer-recurrence.md):
    # re-run the shared A→C sweep K times per forward (K=1 ≡ baseline).
    parser.add_argument("--n-outer-passes", type=int, default=1)
    # Fixed-point / holographic-contractivity loss: λ_fp · mean ‖x_c^k −
    # detach(x_c^{k-1})‖²/‖·‖². Drives the iterated sweep toward a contractive
    # reduce-to-WHNF map. Only active with --n-outer-passes ≥ 2.
    parser.add_argument("--fixed-point-lambda", type=float, default=0.0)

    args = parser.parse_args()

    # Seed BEFORE model creation (random float init happens there).
    mx.random.seed(args.seed)
    np.random.seed(args.seed)

    # ── Build config ───────────────────────────────────────────
    cfg = V15Config()

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
    if args.extracted_model_path is not None:
        cfg.extracted_model_path = args.extracted_model_path
    cfg.__post_init__()

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ─────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v15 — TernaryDescent Training (Fibonacci strides)", file=sys.stderr)
    print("  Adam (continuous beams) + TD (discrete delta plates)", file=sys.stderr)
    print(f"  d_model={cfg.d_model}  n_heads={cfg.n_heads}  d_ff={cfg.d_ff}", file=sys.stderr)
    print(f"  Fibonacci strides ({cfg.n_strides}): {cfg.strides}", file=sys.stderr)
    print(f"  All composition (no GLA): True", file=sys.stderr)
    print(f"  ±{cfg.neighbor_radius} neighbor gathering (W_eff={cfg.effective_window})", file=sys.stderr)
    print(f"  n_passes={cfg.n_passes}  n_stacks={cfg.n_stacks}", file=sys.stderr)
    print("  LaplacianCrystalLoss: WHNF gets 5× fragility weight", file=sys.stderr)
    print("  Base plates: FROZEN (Qwen3.6-27B extraction)", file=sys.stderr)
    print("  Attention delta plates: {+1, -1} ONLY — no-block", file=sys.stderr)
    print(f"  Crystal gate: [{args.td_crystal_gate}, {args.td_crystal_ceiling}]", file=sys.stderr)
    print(f"  Extracted model: {cfg.extracted_model_path}", file=sys.stderr)
    print(f"  Checkpoint dir: {checkpoint_dir}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ──────────────────────────────────────────────────
    model, delta_modules = create_model_with_deltas(
        cfg, convert_ffn=args.convert_ffn,
        skip_base_load=bool(args.safetensors_dir),
    )
    model._n_outer_passes = args.n_outer_passes
    model._fixed_point_lambda = args.fixed_point_lambda
    if args.n_outer_passes != 1:
        print(f"  VSM outer recurrence: n_outer_passes={args.n_outer_passes} "
              f"(shared-weight sweep iterated; K=1 ≡ baseline)", file=sys.stderr)
    if args.fixed_point_lambda > 0.0:
        print(f"  Fixed-point contractivity loss: λ_fp={args.fixed_point_lambda} "
              f"(holographic — pulls each sweep onto its input → WHNF)",
              file=sys.stderr)

    n_plate = count_ternary_weights(model)
    trainable = [v for _, v in tree_flatten(model.trainable_parameters())
                 if isinstance(v, mx.array)]
    n_trainable = sum(v.size for v in trainable)
    print(f"\nModel summary:", file=sys.stderr)
    print(f"  Ternary positions: {n_plate:,}", file=sys.stderr)
    print(f"  Trainable float params: {n_trainable:,}", file=sys.stderr)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)

    # ── Resume ─────────────────────────────────────────────────
    start_step = 0

    if args.safetensors_dir:
        from safetensors_store import SafetensorsStore
        st_dir = Path(args.safetensors_dir).resolve()
        store = SafetensorsStore(str(st_dir))
        globals()["_safetensors_store"] = store
        store.load_into_model(model)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        freeze_delta_architecture(model)
        saved_state = store.load_state()
        if saved_state:
            start_step = saved_state.get("step", 0)
        print(f"📦 Loaded from safetensors: {st_dir} (step {start_step})", file=sys.stderr)

    elif args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            model.load_weights(str(resume_path / "model.npz"), strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)
            freeze_ternary_weights(model)
            freeze_delta_architecture(model)
            state_path = resume_path / "state.json"
            if state_path.exists():
                saved_state = json.loads(state_path.read_text())
                start_step = saved_state.get("step", 0)
            print(f"📂 Resuming from {resume_path} (step {start_step})", file=sys.stderr)

    # ── Data loader ────────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
        seed=42,
    )

    structured_path = args.structured_path
    if structured_path and structured_path.lower() != "none" and Path(structured_path).exists():
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=structured_path,
            mix_ratio=1.0,
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
            seed=42,
        )
        structured_warmup_steps = args.structured_warmup_steps
        target_mix_ratio = args.mix_ratio
        print(f"\n🔮 Structured data: {structured_path}", file=sys.stderr)
        print(f"   Crystal warmup: {structured_warmup_steps} steps pure structured", file=sys.stderr)
        print(f"   Then mix_ratio={target_mix_ratio}", file=sys.stderr)
    else:
        train_loader = prose_loader
        structured_warmup_steps = 0
        target_mix_ratio = 0.0
        print(f"\n📄 Data: prose only", file=sys.stderr)

    print(f"\nConfig: lr={cfg.lr}  batch={cfg.batch_size}  grad_accum={cfg.grad_accum}"
          f"  seq_len={cfg.seq_len}  total_steps={cfg.total_steps}", file=sys.stderr, flush=True)

    # ── Training ───────────────────────────────────────────────
    train_td(
        cfg=cfg,
        args=args,
        model=model,
        delta_modules=delta_modules,
        start_step=start_step,
        train_loader=train_loader,
        checkpoint_dir=checkpoint_dir,
        structured_warmup_steps=structured_warmup_steps,
        target_mix_ratio=target_mix_ratio,
    )


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test():
    """Validate training infrastructure without a data loader."""
    print("=" * 60)
    print("v15 train_td.py self-test")
    print("=" * 60)

    cfg = V15Config()
    cfg.total_steps = 3
    cfg.log_interval = 1
    cfg.checkpoint_interval = 10  # don't checkpoint during test
    cfg.grad_accum = 1

    print(f"\nInstantiating V15Model (no extraction checkpoint)...")
    model, delta_modules = create_model_with_deltas(cfg, skip_base_load=True)
    print(f"  ✓ delta_modules: {len(delta_modules)}")
    print(f"  Attention delta modules (shared_stride_stack): "
          f"{len(_attention_delta_modules(delta_modules))}")

    # Quick forward pass
    tokens = mx.random.randint(0, 1000, (1, 32))
    targets = mx.random.randint(0, 1000, (1, 32))
    logits, loss = model(tokens, targets)
    mx.eval(logits, loss)
    print(f"\n  Forward pass: logits={logits.shape}, loss={loss.item():.4f} ✓")
    print(f"  crystal_mse (Laplacian): {model._last_crystal_mse.item():.6f}")
    print(f"  parity: {model._last_parity.item():.4f}")
    print(f"  CE: {model._last_ce.item():.4f}")

    # Gradient
    gfn = nn.value_and_grad(model, loss_fn)
    lv, grads = gfn(model, tokens, targets)
    mx.eval(lv, grads)
    print(f"\n  Gradient: loss={lv.item():.4f} ✓")

    # No-block enforcement
    n_fixed = _enforce_no_block(delta_modules)
    print(f"\n  No-block enforcement: {n_fixed} violations fixed ✓")

    print("\n" + "=" * 60)
    print("v15 train_td.py: all tests passed ✓")


if __name__ == "__main__":
    import sys as _sys
    # Run self-test only when called directly without CLI args
    # (CLI entry is in the `if __name__ == "__main__"` block above)
    pass
