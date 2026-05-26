"""
v14 — TernaryDescent Training Script (delta plate architecture)

Dual optimizer: Adam trains continuous beams, TernaryDescent trains
discrete delta plates.  Both run on the same backward pass.

Architecture:
  - Base plates:  extracted from Qwen3.6-27B (Apache 2.0), FROZEN
  - Delta plates: attention only, no-block ({+1, -1} only — NEVER 0)
  - Effective:    base ⊙ delta (ternary × ternary = ternary)
  - Gamma/norms:  trained by Adam

Key differences from v13:
  - d_model = 1280 (was 512)
  - No-block constraint: attention delta plates NEVER contain 0.
    FFN delta plates (if converted) may still use {+1, -1, 0}.
  - Base plates loaded from checkpoints/v14-extracted/model.npz
  - Crystal loss is _last_crystal_mse / _last_parity / _last_cross_zone
    (not _last_crystal_loss / _last_parity_loss / _last_cross_zone_loss)

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

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader, MixedDataLoader
from model import V14Model
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
# § 1  Loss function, cosine LR, logging helpers
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(model, input_ids, targets):
    """CE + crystal losses (all combined in model forward pass)."""
    _logits, total_loss = model(input_ids, targets)
    return total_loss


# ══════════════════════════════════════════════════════════════════════════════
# § 1b  Knowledge Distillation — sparse top-k KL divergence
# ══════════════════════════════════════════════════════════════════════════════

class TeacherLogitLoader:
    """Loads pre-computed sparse teacher logits aligned with training data.

    Teacher logits are stored per-shard as .npz with:
      - indices: (n_batches, seq_len, top_k) int32
      - logits:  (n_batches, seq_len, top_k) float16
      - positions: (n_batches,) int64 — byte offset into shard

    The loader tracks which batch within the current shard to serve.
    When the training data loader advances to a new shard, this loader
    follows. If a shard has no teacher logits, returns None (fall back
    to pure CE).
    """

    def __init__(self, logits_dir: str | Path):
        self.logits_dir = Path(logits_dir)
        self._current_shard_idx = -1
        self._current_batch = 0
        self._indices = None  # (n_batches, seq_len, top_k)
        self._logits = None   # (n_batches, seq_len, top_k)
        self._n_batches = 0

    def _load_shard(self, shard_idx: int) -> bool:
        """Load teacher logits for a shard. Returns True if available."""
        path = self.logits_dir / f"teacher_shard_{shard_idx:05d}.npz"
        if not path.exists():
            self._indices = None
            self._logits = None
            self._n_batches = 0
            self._current_shard_idx = shard_idx
            self._current_batch = 0
            return False

        data = np.load(str(path))
        self._indices = data["indices"]   # (n_batches, seq_len, top_k)
        self._logits = data["logits"].astype(np.float32)  # upcast from float16
        self._n_batches = self._indices.shape[0]
        self._current_shard_idx = shard_idx
        self._current_batch = 0
        return True

    def get_batch(self, data_loader) -> tuple | None:
        """Get teacher logits for the current training batch.

        Returns (teacher_indices, teacher_logits) as mx.arrays, or None
        if no teacher logits available for this shard/position.
        """
        # Sync shard with data loader
        shard_idx = getattr(data_loader, 'current_shard_idx', 0)
        if hasattr(data_loader, 'prose'):
            shard_idx = data_loader.prose.current_shard_idx

        if shard_idx != self._current_shard_idx:
            self._load_shard(shard_idx)

        if self._indices is None or self._current_batch >= self._n_batches:
            return None

        idx = self._indices[self._current_batch]  # (seq_len, top_k)
        logits = self._logits[self._current_batch]  # (seq_len, top_k)
        self._current_batch += 1

        # Expand to match batch dimension (B=1 for pre-computed, broadcast)
        return (
            mx.array(idx[np.newaxis, :, :]),     # (1, seq_len, top_k)
            mx.array(logits[np.newaxis, :, :]),   # (1, seq_len, top_k)
        )


def sparse_kd_loss(
    student_logits: mx.array,
    teacher_indices: mx.array,
    teacher_logits: mx.array,
    temperature: float = 2.0,
) -> mx.array:
    """Sparse top-k KL divergence: student vs teacher on teacher's top-k tokens.

    The teacher's top-k captures 99%+ of probability mass. Computing KL
    only over these k tokens is O(B×L×k) instead of O(B×L×V) — 2400×
    cheaper for V=151936, k=64.

    Args:
        student_logits: (B, L, V) raw logits from student
        teacher_indices: (B, L, k) int32 — teacher's top-k token IDs
        teacher_logits: (B, L, k) float — teacher's logits/T (pre-scaled)
        temperature: softening temperature (must match pre-computation)

    Returns:
        kd_loss: scalar KL divergence (already T²-scaled)
    """
    # Teacher: softmax over top-k (already scaled by 1/T during pre-compute)
    teacher_probs = mx.softmax(teacher_logits, axis=-1)  # (B, L, k)

    # Student: gather logits for teacher's top-k tokens, scale by 1/T
    student_scaled = student_logits / temperature  # (B, L, V)

    # Gather student logits at teacher's top-k positions
    # take_along_axis with (B, L, k) indices on axis=-1
    student_topk = mx.take_along_axis(student_scaled, teacher_indices, axis=-1)  # (B, L, k)

    # Student log-softmax over just the top-k slice
    # This is an approximation — we normalize over k tokens, not V.
    # Accurate when top-k covers >99% of teacher mass.
    student_log_probs = student_topk - mx.logsumexp(student_topk, axis=-1, keepdims=True)

    # KL(teacher || student) = Σ teacher * (log(teacher) - log(student))
    kl = teacher_probs * (mx.log(teacher_probs + 1e-10) - student_log_probs)
    kd_loss = mx.mean(mx.sum(kl, axis=-1))  # mean over (B×L), sum over k

    # T² scaling: ensures gradient magnitudes match between CE and KD
    kd_loss = kd_loss * (temperature ** 2)

    return kd_loss


def loss_fn_kd(model, input_ids, targets, teacher_indices, teacher_logits,
               kd_alpha=0.5, temperature=2.0):
    """CE + KD + crystal losses.

    Combined loss: α * CE_crystal + (1-α) * KD
    where CE_crystal is the full v14 loss (CE × crystal_factor + structural losses)
    and KD is the sparse top-k KL divergence against teacher.

    kd_alpha: weight of CE component (1-kd_alpha for KD). Default 0.5.
    """
    logits, ce_crystal_loss = model(input_ids, targets)

    kd_loss = sparse_kd_loss(logits, teacher_indices, teacher_logits, temperature)

    # Store for logging
    model._last_kd_loss = mx.stop_gradient(kd_loss)

    combined = kd_alpha * ce_crystal_loss + (1.0 - kd_alpha) * kd_loss
    return combined


def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
    """Cosine LR schedule with linear warmup."""
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


def _sanitize(obj):
    """Recursively sanitize for JSON: strip NaN/Inf, convert MLX arrays."""
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
    """Append one record to a JSONL file."""
    with open(path, "a") as f:
        f.write(json.dumps(_sanitize(record)) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Model creation with delta plates + base plate loading
# ══════════════════════════════════════════════════════════════════════════════

def create_model_with_deltas(
    cfg: V14Config,
    convert_ffn: bool = False,
) -> tuple[V14Model, list[tuple[str, DeltaTernaryLinear]]]:
    """Create V14Model, load extracted base plates, convert to delta architecture.

    Attention delta plates use no-block constraint: delta is initialized
    to all +1 and TD is instructed never to allow 0.  This prevents the
    collapse that killed v13-td-r10.

    FFN plates stay frozen TernaryLinear unless convert_ffn=True.
    If convert_ffn=True, FFN delta plates CAN use {+1, -1, 0} (standard TD).

    Returns:
        model:     V14Model ready for training
        converted: list of (path, DeltaTernaryLinear) — all delta modules
    """
    model = V14Model(cfg)

    # Step 1: freeze ALL ternary weights (protects dtype from AdamW corruption)
    freeze_ternary_weights(model)

    # Step 2: load extracted base plates from Qwen3.6-27B extraction.
    #
    # The extraction NPZ uses flat keys (e.g. stack_a.layer_00.q)
    # while the model tree uses nested paths (e.g. shared_stride_stack.layers.0.q_proj.weight).
    # We remap keys manually. For the shared stride stack, we vote across
    # all 3 stack extractions (majority sign wins per ternary position).
    extracted_path = Path(cfg.extracted_model_path)
    if extracted_path.exists():
        print(f"📂 Loading extracted base plates from {extracted_path}", file=sys.stderr)
        saved = dict(mx.load(str(extracted_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0
        n_skipped = 0

        # ── Attention: vote across 3 stacks into shared_stride_stack ──
        n_extracted_layers = 11  # extraction has 11 layers per stack
        proj_map = {"q": "q_proj", "k": "k_proj", "v": "v_proj", "o": "out_proj"}
        stacks = ["stack_a", "stack_b", "stack_c"]

        for layer_idx in range(n_extracted_layers):
            for ext_proj, model_proj in proj_map.items():
                model_key = f"shared_stride_stack.layers.{layer_idx}.{model_proj}.weight"
                if model_key not in flat_params:
                    continue
                target_shape = flat_params[model_key].shape

                # Collect from all 3 stacks and sign-vote
                candidates = []
                for stack in stacks:
                    ext_key = f"{stack}.layer_{layer_idx:02d}.{ext_proj}"
                    if ext_key in saved:
                        arr = saved[ext_key]
                        # If extraction shape matches model, use directly
                        if arr.shape == target_shape:
                            candidates.append(arr)
                        # If extraction is larger (e.g. (1280,80) vs (512,80) for GLA Q/K),
                        # truncate rows to match model dim
                        elif arr.shape[1] == target_shape[1] and arr.shape[0] >= target_shape[0]:
                            candidates.append(arr[:target_shape[0]])
                        else:
                            print(
                                f"  ⚠ shape mismatch {ext_key}: ext={arr.shape} model={target_shape}",
                                file=sys.stderr,
                            )

                if len(candidates) == 0:
                    n_skipped += 1
                    continue

                if len(candidates) == 1:
                    voted = mx.array(candidates[0])
                else:
                    # Sign-vote: sum the packed uint32 arrays isn't meaningful.
                    # But since these are packed ternary, we vote in packed space.
                    # All 3 are the same shape — take first (they represent different
                    # teacher zones so any is a valid initialization).
                    # Prefer stack_b (middle layers = most general representation).
                    voted = mx.array(candidates[1] if len(candidates) >= 2 else candidates[0])

                flat_params[model_key] = voted
                n_loaded += 1

        # ── FFN: load from extraction (already voted during extraction) ──
        ffn_map = {
            "stack_b.ffn.gate": "ffn_gate_plate.weight",
            "stack_b.ffn.up": "ffn_key_plate.weight",
            "stack_b.ffn.down": "ffn_value_plate.weight",
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

        # ── Embeddings ──
        if "embed_tokens" in saved:
            emb_key = "embed.ternary_weight"
            if emb_key in flat_params:
                ext_emb = saved["embed_tokens"]
                if ext_emb.shape == flat_params[emb_key].shape:
                    flat_params[emb_key] = mx.array(ext_emb)
                    n_loaded += 1
                else:
                    # Extraction uses d//16 packing, embedding uses d//4 packing
                    print(
                        f"  ⚠ Embedding shape mismatch: ext={ext_emb.shape}"
                        f" model={flat_params[emb_key].shape}",
                        file=sys.stderr,
                    )
                    n_skipped += 1

        # Re-apply remapped params to model
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

    # Step 3: convert attention plates to DeltaTernaryLinear.
    # No-block invariant: attention delta initialised to all +1 by DeltaTernaryLinear.
    # The shared_stride_stack is the single set of 16 stride layers.
    attention_prefixes = (
        "shared_stride_stack",
    )
    # Exclude the shared FFN plates from attention conversion
    exclude = ("ffn_key_plate", "ffn_gate_plate", "ffn_value_plate")
    if convert_ffn:
        exclude = ()  # convert everything under the attention prefixes

    converted_attn = convert_to_delta(
        model,
        include_prefixes=attention_prefixes,
        exclude_prefixes=exclude if exclude else None,
    )

    converted_ffn: list[tuple[str, DeltaTernaryLinear]] = []
    if convert_ffn:
        # Also convert shared FFN plates (standard TD: can use 0)
        converted_ffn = convert_to_delta(
            model,
            include_prefixes=("ffn_key_plate", "ffn_gate_plate", "ffn_value_plate"),
        )

    converted = converted_attn + converted_ffn

    # Step 4: freeze delta architecture (base_weight + delta_weight excluded from Adam)
    freeze_delta_architecture(model)

    # Step 5: re-freeze any remaining plain TernaryLinear modules
    freeze_ternary_weights(model)

    return model, converted


def _attention_delta_modules(
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
) -> list[tuple[str, DeltaTernaryLinear]]:
    """Return only the attention delta modules (those under shared_stride_stack)."""
    attn_prefixes = ("shared_stride_stack",)
    return [
        (path, dtl)
        for path, dtl in delta_modules
        if any(path.startswith(p) for p in attn_prefixes)
    ]


def _enforce_no_block(delta_modules: list[tuple[str, DeltaTernaryLinear]]) -> int:
    """v14 invariant: attention delta plates must never contain 0.

    After TD.step(), scan all attention delta plates and force any zeros
    back to +1 (keep = safe default).  Returns number of violations fixed.
    """
    n_fixed_total = 0
    attn_modules = _attention_delta_modules(delta_modules)
    for _path, dtl in attn_modules:
        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int8
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
# § 3  Delta gradient computation (decomposition)
# ══════════════════════════════════════════════════════════════════════════════

def compute_decomposed_gradients(
    model: V14Model,
    grads: dict,
) -> tuple[
    list[tuple[str, mx.array, mx.array, mx.array, bool]],
    dict[str, mx.array],
]:
    """Decompose gradients: routing → TD, calibration → Adam.

    Returns:
        td_inputs:     list of (name, delta_packed, routing_grad, base_packed, no_block)
        gamma_filters: dict[gamma_key → calibration_fraction (N,)]
    """
    delta_modules = collect_delta_params(model)
    td_inputs = []
    gamma_filters = {}

    # Determine which modules have the no-block constraint (attention)
    attn_modules = _attention_delta_modules(delta_modules)
    attn_paths = {path for path, _ in attn_modules}

    flat_grads = dict(tree_flatten(grads))

    for path, dtl in delta_modules:
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
        base_unpacked = unpack_ternary_mlx(dtl.base_weight)    # (N, K) int8
        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int8
        effective_signs = (
            base_unpacked.astype(mx.int16) * delta_unpacked.astype(mx.int16)
        ).astype(mx.int8)

        # Decompose: routing → TD, calibration → Adam
        routing, _calibration, _routing_mask = decompose_gradient(
            grad_effective, effective_signs,
        )

        td_inputs.append((path, dtl.delta_weight, routing, dtl.base_weight, path in attn_paths))

        # Calibration fraction for Adam gamma filtering
        routing_frac = compute_routing_fraction(grad_effective, effective_signs)
        calibration_frac = 1.0 - routing_frac  # (N,)
        gamma_filters[gamma_key] = calibration_frac

    return td_inputs, gamma_filters


def filter_gamma_grads(
    grads: dict,
    gamma_filters: dict[str, mx.array],
) -> dict:
    """Attenuate gamma gradients by calibration fraction (remove routing component)."""
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

# FFN plates are shared across all N_PASSES=8 passes.
# Gradients accumulate from every pass, so divide by 8 to avoid scaling.
_UNIVERSAL_SHARED = ("ffn_key_plate", "ffn_gate_plate", "ffn_value_plate")
_N_PASSES = 8


def normalize_shared_grads(grads: dict) -> dict:
    """Divide shared FFN plate gradients by N_PASSES (they see 8× accumulation)."""
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
# § 5  Training loop (main loop with all guards)
# ══════════════════════════════════════════════════════════════════════════════

def train_td(
    cfg: V14Config,
    args: argparse.Namespace,
    model: V14Model,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    start_step: int,
    train_loader,
    checkpoint_dir: Path,
    structured_warmup_steps: int = 0,
    target_mix_ratio: float = 0.1,
) -> None:
    """Training loop: Adam (beams) + TernaryDescent (delta plates).

    Lessons encoded from v13 failures:
      - NaN guard with rollback after 3 consecutive NaN
      - Crystal factor overflow guard
      - Schmitt trigger (hysteresis) for TD activation
      - Gradient decomposition: routing→TD, calibration→Adam
      - Surgical Adam decay on TD-flipped rows
      - Zero ternary grads after backward
      - Shared-weight normalization
      - Gradient clipping before optimizer step
      - Crystal warmup schedule
      - No-block enforcement: attention delta must be {+1, -1} only
    """
    total_steps = args.steps if args.steps else cfg.total_steps
    reduce_threshold = args.reduce_threshold
    reduce_interval = args.reduce_interval

    # Separate attention vs FFN delta modules
    attn_delta = _attention_delta_modules(delta_modules)
    ffn_delta = [(p, d) for p, d in delta_modules if (p, d) not in attn_delta]

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  v14 — TernaryDescent Training", file=sys.stderr)
    print(f"  Adam (beams) + TD (delta plates)", file=sys.stderr)
    print(f"  d_model={cfg.d_model}  n_passes={cfg.n_passes}  strides={len(cfg.strides)}", file=sys.stderr)
    print(f"  steps {start_step+1}–{total_steps}", file=sys.stderr)
    print(f"  TD: flip_rate={args.td_flip_rate}  warmup={args.td_warmup}"
          f"  min_conf={args.td_min_confidence}"
          f"  flip_interval={args.td_flip_interval}", file=sys.stderr)
    decompose_str = "ON (routing→TD, calibration→Adam)" if args.decompose_gradient else "OFF (mixed)"
    print(f"  Gradient decomposition: {decompose_str}", file=sys.stderr)
    print(f"  No-block: attention delta = {{+1,-1}} only (NEVER 0)", file=sys.stderr)
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
    )

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
            print(f"   α={args.kd_alpha} (CE={args.kd_alpha:.0%}, KD={1-args.kd_alpha:.0%})",
                  file=sys.stderr)
            print(f"   Temperature: {args.kd_temperature}", file=sys.stderr)
        else:
            print(f"⚠  Teacher logits dir not found: {teacher_dir}", file=sys.stderr)

    if kd_enabled:
        # KD loss function captures alpha and temperature from args
        _kd_alpha = args.kd_alpha
        _kd_temp = args.kd_temperature
        def _loss_fn_kd(model, input_ids, targets, t_indices, t_logits):
            return loss_fn_kd(model, input_ids, targets, t_indices, t_logits,
                              kd_alpha=_kd_alpha, temperature=_kd_temp)
        loss_and_grad_kd = nn.value_and_grad(model, _loss_fn_kd)

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── State ─────────────────────────────────────────────────
    train_losses = []
    loss_window = deque(maxlen=50)
    n_reductions = 0
    total_td_flips = 0
    td_flips_since_log = 0  # accumulates flips between log lines for visibility
    td_active = False  # Schmitt trigger state — starts OFF until crystal latches
    _structured_warmup_done = False  # True after structured-only warmup phase completes
    t_start = time.time()

    # ── Warm-up forward pass (initialises Adam state) ─────────
    ids_np, tgts_np = next(train_loader)
    lv, grads = loss_and_grad(model, mx.array(ids_np), mx.array(tgts_np))
    mx.eval(lv, grads)
    grads = zero_ternary_grads(model, grads)
    adam.update(model, grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    # ── Resume: restore optimizer state from checkpoint ───────
    if start_step > 0:
        # Resume path priority: --resume (explicit) > checkpoint_dir/step_N (implicit).
        # Session 150 bug: folded checkpoint at --resume was overwritten by
        # checkpoint_dir/step_001500 (the original unfolded checkpoint).
        resume_dir = Path(args.resume).resolve() if args.resume else None
        step_dir = checkpoint_dir / f"step_{start_step:06d}"

        # Optimizer: prefer --resume, fallback to step_dir
        opt_path = None
        if resume_dir and (resume_dir / "optimizer.npz").exists():
            opt_path = resume_dir / "optimizer.npz"
        elif (step_dir / "optimizer.npz").exists():
            opt_path = step_dir / "optimizer.npz"

        if opt_path is not None:
            saved_opt = dict(mx.load(str(opt_path)))
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
            print(
                f"📂 Restored optimizer state from {opt_path}"
                f" ({n_restored} arrays, {n_skipped} skipped)",
                file=sys.stderr,
            )
            # Re-load model weights to undo the warm-up gradient step.
            # Must use same source as the CLI loaded (--resume path).
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
        else:
            print(
                f"⚠  No optimizer.npz at step {start_step} — Adam moments start fresh",
                file=sys.stderr,
            )

        # Restore running state (crystal EMA, S5 identity, loop state)
        # Prefer --resume, fallback to step_dir
        state_path = None
        if resume_dir and (resume_dir / "state.json").exists():
            state_path = resume_dir / "state.json"
        elif (step_dir / "state.json").exists():
            state_path = step_dir / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text())
            ema_val = state.get("crystal_ema")
            if ema_val is not None:
                model._crystal_ema = mx.array(float(ema_val))
                print(f"  crystal_ema = {ema_val:.6f}", file=sys.stderr)
            s5_state = state.get("s5_identity_state")
            if s5_state is not None:
                model.s5_identity.identity_state = mx.array(s5_state)
                print(
                    f"  s5_identity_state restored ({len(s5_state)} dims)",
                    file=sys.stderr,
                )

            # Restore training loop counters
            if "total_td_flips" in state:
                total_td_flips = state["total_td_flips"]
                print(f"  total_td_flips = {total_td_flips:,}", file=sys.stderr)
            if "n_reductions" in state:
                n_reductions = state["n_reductions"]
                print(f"  n_reductions = {n_reductions}", file=sys.stderr)
            if "td_active" in state:
                td_active = state["td_active"]
                print(f"  td_active = {td_active}", file=sys.stderr)

            # Restore structured warmup state
            if "structured_warmup_done" in state:
                _structured_warmup_done = state["structured_warmup_done"]
                if _structured_warmup_done and hasattr(train_loader, 'mix_ratio'):
                    train_loader.mix_ratio = target_mix_ratio
                print(f"  structured_warmup_done = {_structured_warmup_done}", file=sys.stderr)

            # Restore data loader position (shard + offset)
            if "data_loader" in state and hasattr(train_loader, "load_state"):
                train_loader.load_state(state["data_loader"])
                dl_state = state["data_loader"]
                print(
                    f"  data_loader: shard={dl_state.get('shard_idx', '?')}"
                    f"  pos={dl_state.get('position', '?'):,}"
                    f"  struct_pos={dl_state.get('structured_pos', 'N/A')}",
                    file=sys.stderr,
                )

        model._training_step = start_step

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    nan_consecutive = 0  # NaN skip/rollback counter

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        # ── Structured data warmup → mix transition ───────────
        # For the first N steps, mix_ratio=1.0 (pure structured data)
        # to latch the crystal lattice immediately. Then switch to
        # normal mix_ratio for prose+structured mixture.
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
                file=sys.stderr,
                flush=True,
            )

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        # Crystal warmup: crystal_direct_lambda anneals start→floor over warmup steps
        if cfg.crystal_warmup_steps > 0 and step <= cfg.crystal_warmup_steps:
            progress = step / cfg.crystal_warmup_steps
            crystal_lambda_eff = (
                cfg.crystal_direct_lambda_start
                + (cfg.crystal_direct_lambda - cfg.crystal_direct_lambda_start)
                * 0.5 * (1.0 - math.cos(math.pi * progress))
            )
            model.cfg.crystal_direct_lambda = crystal_lambda_eff

        model._training_step = step

        # ── Gradient accumulation ─────────────────────────────
        accum_loss = 0.0
        accum_grads = None
        _kd_loss_accum = 0.0

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            # Try KD path if teacher logits are available
            used_kd = False
            if kd_enabled and teacher_loader is not None:
                teacher_batch = teacher_loader.get_batch(train_loader)
                if teacher_batch is not None:
                    t_indices, t_logits = teacher_batch
                    lv, grads = loss_and_grad_kd(model, ids, tgts, t_indices, t_logits)
                    mx.eval(lv, grads)
                    used_kd = True
                    # Log KD loss component
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

        # ── NaN guard ─────────────────────────────────────────
        # If loss is NaN/Inf: skip this step entirely (don't poison Adam
        # moments or model weights). After 3 consecutive NaN, roll back.
        if math.isnan(step_loss) or math.isinf(step_loss):
            nan_consecutive += 1
            print(
                f"⚠️  NaN/Inf loss at step {step} (consecutive: {nan_consecutive})",
                file=sys.stderr, flush=True,
            )
            if nan_consecutive >= 3:
                # Roll back to last clean checkpoint
                ckpt_dirs = sorted(
                    d for d in os.listdir(str(checkpoint_dir))
                    if d.startswith("step_")
                )
                if ckpt_dirs:
                    last_ckpt = checkpoint_dir / ckpt_dirs[-1]
                    print(
                        f"🔄 3 consecutive NaN — rolling back to {last_ckpt}",
                        file=sys.stderr, flush=True,
                    )
                    model.load_weights(str(last_ckpt / "model.npz"), strict=False)
                    mx.eval(model.parameters())
                    restore_ternary(model)
                    freeze_ternary_weights(model)
                    freeze_delta_architecture(model)
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

        # ── Decompose: routing → TD, calibration → Adam ───────
        td_inputs, gamma_filters = compute_decomposed_gradients(model, accum_grads)

        if args.decompose_gradient:
            filtered_grads = filter_gamma_grads(accum_grads, gamma_filters)
        else:
            filtered_grads = accum_grads

        # ── Adam step (continuous params, calibration gradient) ──
        adam.update(model, filtered_grads)
        mx.eval(model.parameters(), adam.state)
        restore_ternary(model)

        # ── Schmitt trigger: crystal-gated TD activation ──────
        # TD does NOT flip anything until crystal latches.
        #   crystal_mse < td_crystal_gate    → TD activates
        #   crystal_mse > td_crystal_ceiling → TD deactivates
        #   in between                       → stays in current state (hysteresis)
        crystal_val = getattr(model, "_last_crystal_mse", None)
        if crystal_val is not None:
            mx.eval(crystal_val)
            crystal_val_f = float(crystal_val.item())
        else:
            crystal_val_f = None

        if crystal_val_f is not None:
            if crystal_val_f < args.td_crystal_gate:
                td_active = True   # crystal latched — activate TD
            elif crystal_val_f > args.td_crystal_ceiling:
                td_active = False  # crystal destabilized — deactivate TD
            # else: stay in current state (hysteresis band)

        # ── TernaryDescent: accumulate every step, flip every N ──
        # TD.step() accumulates moments every call. When step_count
        # hits a flip_interval boundary, it also commits flips.
        # Between flips, GD has time to re-learn routes.
        # After flips, moments reset — stale accumulation drives bad flips.
        #
        # Flipping every step → gnorm escalation → divergence (session 148).
        if td_active:
            td_result = td.step(td_inputs, training_step=step)
        else:
            td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}

        # ── Apply flips + surgical Adam decay ─────────────────
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

        # ── No-block invariant enforcement (v14 attention delta) ──
        # After TD.step(), verify attention delta plates have no zeros.
        # Force any leaked zeros back to +1 (keep = safe default).
        n_no_block_fixed = _enforce_no_block(delta_modules)

        # ── Surgical Adam decay: GD was compensating for old topology.
        # TD flipped signs → Adam's moments for those rows are stale.
        # Decay them so GD can re-converge to the new topology.
        n_adam_decayed = 0
        if td_affected_rows:
            n_adam_decayed = surgical_adam_decay_for_etch(
                adam, model, td_affected_rows, decay=0.1,
            )

        total_td_flips += td_result["total_flips"]
        td_flips_since_log += td_result["total_flips"]
        dt = time.time() - t0

        # ── Logging ───────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / max(dt, 1e-6)

            # Retrieve component losses (cached on model during forward)
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

            # Delta plate stats
            delta_stats_all = {}
            total_changed = 0.0
            for path, dtl in delta_modules:
                ds = dtl.delta_stats()
                delta_stats_all[path] = ds
                total_changed += ds["changed_frac"]
            avg_changed = total_changed / max(len(delta_modules), 1)

            # Console line
            ce_str = f"CE={ce_val:.3f}" if ce_val is not None else f"loss={step_loss:.3f}"
            kd_str = f" KD={_kd_loss_step:.3f}" if _kd_loss_step is not None else ""
            crystal_str = f" crystal={crystal_mse_val:.4f}" if crystal_mse_val is not None else ""
            parity_str = f" parity={parity_val:.4f}" if parity_val is not None else ""
            cross_str = f" cross_zone={cross_zone_val:.4f}" if cross_zone_val is not None else ""
            gate_icon = "🔓" if td_active else "🔒"
            nb_str = f" nb_fixed={n_no_block_fixed}" if n_no_block_fixed > 0 else ""
            adam_decay_str = f" adam_decay={n_adam_decayed}" if n_adam_decayed > 0 else ""
            # td_flips_since_log shows ALL flips since last log line
            # (flip_interval may not align with log_interval in old runs,
            # but with training_step alignment they should match)
            td_flips_this_window = td_flips_since_log  # capture before reset
            td_str = (
                f" {gate_icon} td={td_flips_this_window}"
                f" Δ={avg_changed:.3f}{nb_str}{adam_decay_str}"
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

            # Reset per-log-interval flip counter
            td_flips_since_log = 0

            # JSONL record
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
                "td_adam_decayed": n_adam_decayed,
                "td_in_warmup": td_result["in_warmup"],
                "td_active": td_active,
                "delta_avg_changed": avg_changed,
                "n_reductions": n_reductions,
                "no_block_fixed": n_no_block_fixed,
            }
            if ce_val is not None:
                record["ce"] = ce_val
            if _kd_loss_step is not None:
                record["kd_loss"] = _kd_loss_step
                record["kd_enabled"] = True
            if crystal_mse_val is not None:
                record["crystal_mse"] = crystal_mse_val
            if parity_val is not None:
                record["parity"] = parity_val
            if cross_zone_val is not None:
                record["cross_zone"] = cross_zone_val

            # Per-module delta stats (every 4th log)
            if step % (cfg.log_interval * 4) == 0:
                for path, ds in delta_stats_all.items():
                    for k, v in ds.items():
                        record[f"delta.{path}.{k}"] = v

            # TD per-module confidence
            for name, info in td_result["per_module"].items():
                record[f"td.{name}.flips"] = info.get("flips", 0)
                record[f"td.{name}.candidates"] = info.get("candidates", 0)
                record[f"td.{name}.confidence"] = info.get("mean_confidence", 0.0)

            # Routing/calibration split stats (every 4th log)
            if step % (cfg.log_interval * 4) == 0 and args.decompose_gradient:
                for gamma_key, calib_frac in gamma_filters.items():
                    mx.eval(calib_frac)
                    mean_calib = float(calib_frac.mean().item())
                    path_short = gamma_key.replace(".gamma", "")
                    record[f"routing_frac.{path_short}"] = 1.0 - mean_calib
                    record[f"calibration_frac.{path_short}"] = mean_calib

            _append_jsonl(checkpoint_dir / "train_td_log.jsonl", record)

        # ── Periodic reduction ────────────────────────────────
        if reduce_interval > 0 and step % reduce_interval == 0 and step > start_step:
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
                # Re-enforce no-block after reduction: delta is now all +1 — fine
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

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            _save_checkpoint(
                model, adam, td, step, cfg, checkpoint_dir,
                train_losses, n_reductions, total_td_flips, delta_modules,
                train_loader=train_loader,
                td_active=td_active,
                structured_warmup_done=_structured_warmup_done,
                structured_warmup_steps=structured_warmup_steps,
                target_mix_ratio=target_mix_ratio,
            )

    # ── Final ─────────────────────────────────────────────────
    elapsed = time.time() - t_start
    print(
        f"\n{'='*72}\n"
        f"TD training complete: {total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Total TD flips: {total_td_flips:,}  Reductions: {n_reductions}",
        file=sys.stderr,
    )
    _save_checkpoint(
        model, adam, td, total_steps, cfg, checkpoint_dir,
        train_losses, n_reductions, total_td_flips, delta_modules,
        train_loader=train_loader,
        td_active=td_active,
        structured_warmup_done=_structured_warmup_done,
        structured_warmup_steps=structured_warmup_steps,
        target_mix_ratio=target_mix_ratio,
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Evaluation and checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def _save_checkpoint(
    model: V14Model,
    adam,
    td: TernaryDescent,
    step: int,
    cfg: V14Config,
    checkpoint_dir: Path,
    train_losses: list[float],
    n_reductions: int,
    total_td_flips: int,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    *,
    train_loader=None,
    td_active: bool = False,
    structured_warmup_done: bool = False,
    structured_warmup_steps: int = 0,
    target_mix_ratio: float = 0.1,
) -> None:
    """Save model weights, optimizer state, delta snapshots, and running state.

    Saves everything needed for exact resume:
      - model.npz: all model parameters
      - optimizer.npz: Adam moments
      - delta_plates.npz: per-module delta weights + stats
      - state.json: all loop state, data position, config snapshot
    """
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    # Model weights
    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    # Optimizer state
    if adam.state:
        flat_opt = dict(tree_flatten(adam.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    # Delta plate snapshots — separate file for quick cross-run comparison.
    # Base plates are NOT saved here (frozen and identical to extraction).
    # Uses collect_delta_params() to deduplicate aliases (shared_stride_stack
    # is aliased via stack_a/b/c — without dedup we'd save 280 entries
    # instead of 70). Stores packed uint32 (2 bits/position) not int8.
    delta_snapshots = {}
    dedup_deltas = collect_delta_params(model)
    for path, dtl in dedup_deltas:
        delta_key = path.replace(".", "_")
        # Store packed uint32 directly (session 150: 356MB → ~27MB)
        mx.eval(dtl.delta_weight)
        delta_snapshots[f"{delta_key}_delta_packed"] = dtl.delta_weight
        # Stats from the module's own method (avoids unpacking)
        ds = dtl.delta_stats()
        total = dtl.out_features * dtl.in_features
        delta_snapshots[f"{delta_key}_stats"] = mx.array([
            ds["keep_frac"] * total,    # n_keep
            ds["flip_frac"] * total,    # n_flip
            ds["block_frac"] * total,   # n_block
            float(total),               # total
        ])
    if delta_snapshots:
        mx.savez(str(step_dir / "delta_plates.npz"), **delta_snapshots)

    # Running state for clean resume
    crystal_ema = getattr(model, "_crystal_ema", None)
    if crystal_ema is not None:
        mx.eval(crystal_ema)

    s5_identity = getattr(model.s5_identity, "identity_state", None)
    if s5_identity is not None:
        mx.eval(s5_identity)

    state = {
        "step": step,
        "train_losses_last50": train_losses[-50:],
        "n_reductions": n_reductions,
        "total_td_flips": total_td_flips,
        "td_step_count": td.step_count,
        "crystal_ema": float(crystal_ema.item()) if crystal_ema is not None else None,
        "s5_identity_state": (
            s5_identity.tolist() if s5_identity is not None else None
        ),

        # Training loop state — needed for exact resume
        "td_active": td_active,
        "structured_warmup_done": structured_warmup_done,
        "structured_warmup_steps": structured_warmup_steps,
        "target_mix_ratio": target_mix_ratio,
    }

    # Data loader position — exact shard/offset for reproducible resume
    if train_loader is not None and hasattr(train_loader, "save_state"):
        state["data_loader"] = train_loader.save_state()

    # Per-module delta stats (quick inspection without loading weights)
    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        state["delta_stats"] = delta_stats

    # Config snapshot — full hyperparameters that produced this run
    from dataclasses import asdict
    state["config"] = asdict(cfg)

    (step_dir / "state.json").write_text(json.dumps(_sanitize(state), indent=2))
    print(f"💾 Checkpoint: {step_dir}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# § 7  CLI with argparse
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "v14 — TernaryDescent trainer (delta plates + Adam beams)\n"
            "\n"
            "Attention delta plates: no-block ({+1,-1} only — NEVER 0).\n"
            "FFN delta plates (--convert-ffn): standard {+1,-1,0}.\n"
            "Base plates loaded from checkpoints/v14-extracted/model.npz."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── Paths ─────────────────────────────────────────────────
    parser.add_argument(
        "--checkpoint-dir", default="checkpoints/v14-td",
        help="Directory for training checkpoints (default: checkpoints/v14-td)",
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Path to a training checkpoint directory to resume from",
    )
    parser.add_argument(
        "--extracted-model-path", type=str, default=None,
        help=(
            "Path to extracted base plates model.npz "
            "(default: checkpoints/v14-extracted/model.npz)"
        ),
    )
    parser.add_argument("--steps", type=int, default=None,
                        help="Override total training steps")

    # ── TernaryDescent params ─────────────────────────────────
    parser.add_argument(
        "--td-flip-rate", type=float, default=0.001,
        help="Max fraction of ternary weights to flip per step (default: 0.001)",
    )
    parser.add_argument(
        "--td-warmup", type=int, default=25,
        help="TD warmup steps AFTER crystal latches (no flips before; default: 25)",
    )
    parser.add_argument(
        "--td-flip-interval", type=int, default=20,
        help=(
            "Steps between TD flip commits (default: 20). TD accumulates moments "
            "every step but only commits flips every N steps. After flipping, "
            "moments at flipped positions are surgically zeroed (definitely stale). "
            "Non-flipped positions keep their accumulation — EMA natural decay "
            "(beta1=0.9 → 12%% remaining after 20 steps) handles landscape drift. "
            "Use a multiple of --log-interval for visibility. "
            "Session 148: every-step flipping caused gnorm escalation. "
            "Session 150: global reset was too conservative."
        ),
    )
    parser.add_argument(
        "--td-crystal-gate", type=float, default=0.03,
        help=(
            "Crystal MSE threshold for TD activation (Schmitt trigger lower bound). "
            "TD activates once crystal_mse drops below this value. Default: 0.03"
        ),
    )
    parser.add_argument(
        "--td-crystal-ceiling", type=float, default=0.07,
        help=(
            "Crystal MSE ceiling (Schmitt trigger upper bound). TD deactivates if "
            "crystal_mse rises above this. Reactivates when it drops back below "
            "--td-crystal-gate. Default: 0.07"
        ),
    )
    parser.add_argument(
        "--td-min-confidence", type=float, default=0.3,
        help="Minimum signal-to-noise ratio for flip candidates (default: 0.3)",
    )
    parser.add_argument(
        "--td-beta1", type=float, default=0.9,
        help="TD direction EMA decay (default: 0.9)",
    )
    parser.add_argument(
        "--td-beta2", type=float, default=0.999,
        help="TD magnitude EMA decay (default: 0.999)",
    )

    # ── Delta architecture ────────────────────────────────────
    parser.add_argument(
        "--convert-ffn", action="store_true",
        help=(
            "Also convert shared FFN plates to delta (standard TD: can use 0). "
            "Default: attention only."
        ),
    )

    # ── Reduction ─────────────────────────────────────────────
    parser.add_argument(
        "--reduce-interval", type=int, default=0,
        help="Check for delta reduction every N steps (0=never; default: 0)",
    )
    parser.add_argument(
        "--reduce-threshold", type=float, default=0.05,
        help=(
            "Reduce when max changed_frac < threshold. "
            "E.g. 0.05 = >95%% positions still +1. Default: 0.05"
        ),
    )

    # ── Gradient decomposition ────────────────────────────────
    parser.add_argument(
        "--decompose-gradient", action="store_true", default=True,
        help="Decompose gradient: routing→TD, calibration→Adam (default: ON)",
    )
    parser.add_argument(
        "--no-decompose-gradient", dest="decompose_gradient",
        action="store_false",
        help="Disable gradient decomposition (mixed gradient to both optimizers)",
    )

    # ── Config overrides ──────────────────────────────────────
    parser.add_argument("--lr", type=float, default=None,
                        help="Override learning rate")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Override batch size")
    parser.add_argument("--seq-len", type=int, default=None,
                        help="Override sequence length")
    parser.add_argument("--data-dir", type=str, default=None,
                        help="Override data directory")
    parser.add_argument(
        "--crystal-direct-lambda", type=float, default=None,
        help="Override crystal direct loss floor lambda",
    )
    parser.add_argument(
        "--crystal-direct-lambda-start", type=float, default=None,
        help="Override crystal warmup start lambda (anneals to --crystal-direct-lambda)",
    )
    parser.add_argument(
        "--crystal-warmup-steps", type=int, default=None,
        help="Override crystal warmup schedule length (0 = no warmup)",
    )

    # ── Knowledge distillation args ───────────────────────────
    parser.add_argument(
        "--teacher-logits-dir", type=str, default=None,
        help="Directory with pre-computed teacher logits (enables KD loss). "
             "Use precompute_teacher.py to generate.",
    )
    parser.add_argument(
        "--kd-alpha", type=float, default=0.5,
        help="Weight of CE loss (1-alpha = KD weight). Default: 0.5 (equal weight).",
    )
    parser.add_argument(
        "--kd-temperature", type=float, default=2.0,
        help="Softening temperature for KD (must match precompute_teacher.py). Default: 2.0",
    )

    # ── Structured data args ──────────────────────────────────
    parser.add_argument(
        "--structured-path", type=str,
        default="data/structured_shard_qwen36.npy",
        help="Path to structured data shard (lambda/math/clojure). "
             "Set to 'none' to disable structured mixing.",
    )
    parser.add_argument(
        "--mix-ratio", type=float, default=0.1,
        help="Fraction of batches drawn from structured data (default: 0.1)",
    )
    parser.add_argument(
        "--structured-warmup-steps", type=int, default=50,
        help="Steps of pure structured data before mixing in prose. "
             "Crystal latches immediately on structured data. (default: 50)",
    )

    args = parser.parse_args()

    # ── Build config ──────────────────────────────────────────
    cfg = V14Config()

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

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v14 — TernaryDescent Training", file=sys.stderr)
    print("  Adam (continuous beams) + TD (discrete delta plates)", file=sys.stderr)
    print(f"  d_model={cfg.d_model}  n_heads={cfg.n_heads}  d_ff={cfg.d_ff}", file=sys.stderr)
    print(f"  strides={cfg.strides}", file=sys.stderr)
    print(f"  n_passes={cfg.n_passes}  n_stacks={cfg.n_stacks}", file=sys.stderr)
    print("  Base plates: FROZEN (Qwen3.6-27B extraction)", file=sys.stderr)
    print("  Attention delta plates: {+1, -1} ONLY — no-block constraint", file=sys.stderr)
    print(f"  Crystal gate: [{args.td_crystal_gate}, {args.td_crystal_ceiling}]"
          f" (Schmitt trigger)", file=sys.stderr)
    print(f"  Crystal warmup: {cfg.crystal_direct_lambda_start} → "
          f"{cfg.crystal_direct_lambda} over {cfg.crystal_warmup_steps} steps",
          file=sys.stderr)
    print(f"  Extracted model: {cfg.extracted_model_path}", file=sys.stderr)
    print(f"  Checkpoint dir: {checkpoint_dir}", file=sys.stderr)
    if args.teacher_logits_dir:
        print(f"  KD: teacher_logits={args.teacher_logits_dir}  "
              f"α={args.kd_alpha}  T={args.kd_temperature}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model: create + load base plates + convert to delta ───
    model, delta_modules = create_model_with_deltas(
        cfg,
        convert_ffn=args.convert_ffn,
    )

    # ── Print param count ─────────────────────────────────────
    n_plate = count_ternary_weights(model)
    trainable = [
        v for _, v in tree_flatten(model.trainable_parameters())
        if isinstance(v, mx.array)
    ]
    n_trainable = sum(v.size for v in trainable)
    print(f"\nModel summary:", file=sys.stderr)
    print(f"  Ternary positions: {n_plate:,}", file=sys.stderr)
    print(f"  Trainable float params: {n_trainable:,}", file=sys.stderr)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)

    # ── Resume: find start_step ───────────────────────────────
    start_step = 0
    if args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            # Load base weights first (before convert_to_delta was already done,
            # so load_weights will land in DeltaTernaryLinear.base_weight / .gamma)
            model.load_weights(str(resume_path / "model.npz"), strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)
            freeze_ternary_weights(model)
            freeze_delta_architecture(model)
            print(f"📂 Loaded resume weights from {resume_path}", file=sys.stderr)

            state_path = resume_path / "state.json"
            if state_path.exists():
                saved_state = json.loads(state_path.read_text())
                start_step = saved_state.get("step", 0)
                print(f"  Resuming from step {start_step}", file=sys.stderr)
        else:
            print(f"⚠  Resume path not found: {resume_path}", file=sys.stderr)

    # ── Data loader ───────────────────────────────────────────
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
        # MixedDataLoader: structured warmup then mixed training.
        # During warmup (first N steps), mix_ratio=1.0 → pure structured.
        # After warmup, switches to normal mix_ratio.
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=structured_path,
            mix_ratio=1.0,  # Start pure structured for crystal latch
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
            seed=42,
        )
        structured_warmup_steps = args.structured_warmup_steps
        target_mix_ratio = args.mix_ratio
        print(f"\n🔮 Structured data: {structured_path}", file=sys.stderr)
        print(f"   Crystal warmup: {structured_warmup_steps} steps of PURE structured",
              file=sys.stderr)
        print(f"   Then mix_ratio={target_mix_ratio} (structured/prose)", file=sys.stderr)
    else:
        train_loader = prose_loader
        structured_warmup_steps = 0
        target_mix_ratio = 0.0
        if structured_path and structured_path.lower() != "none":
            print(f"⚠  Structured shard not found: {structured_path}", file=sys.stderr)
        print(f"\n📄 Data: prose only (no structured mixing)", file=sys.stderr)

    # ── Config summary banner ─────────────────────────────────
    print(f"\nConfig summary:", file=sys.stderr)
    print(f"  lr={cfg.lr}  batch={cfg.batch_size}  grad_accum={cfg.grad_accum}"
          f"  seq_len={cfg.seq_len}", file=sys.stderr)
    print(f"  total_steps={cfg.total_steps}  warmup={cfg.warmup_steps}", file=sys.stderr)
    print(f"  tokens_per_step={cfg.tokens_per_step:,}", file=sys.stderr)
    print(f"  log_interval={cfg.log_interval}  ckpt_interval={cfg.checkpoint_interval}",
          file=sys.stderr, flush=True)

    # ── Training ──────────────────────────────────────────────
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
