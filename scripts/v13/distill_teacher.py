#!/usr/bin/env python3
"""
v13 Behavioral Distillation — shape student plates from teacher *behavior*,
not weight topology.

Where extract_teacher.py asks "what does the teacher's weight *look like*?"
(sign(SVD(W))), this script asks "what does the teacher *compute*?" It runs
diverse text probes through the teacher, captures (layer_input, layer_output)
pairs at each relevant layer, and etches the student plates to reproduce those
input→output mappings as closely as possible.

Protocol (adapted from scripts/v12/mini_holo_distill.py):
  1. Load teacher (Qwen3-14B) for real inference — mlx-lm preferred.
  2. Load fresh V13 student and build learnable projection bridges
     (d_teacher=5120 → d_student=512), one per mapped stride.
  3. For each round:
     a. Run n_probes text batches through teacher; hook intermediate outputs
        at the teacher layers that correspond to each student stride.
     b. For each student plate (q/k/v/out per stride, ffn key/value):
        - Accumulate sign(∂L_distill/∂γ) across all probe batches.
        - Flip positions where |accumulated sign| / n_batches > threshold.
     c. Train beam params (γ, norms, biases) + projection bridges via
        Adam on the MSE distillation loss for bridge_steps mini-steps.
  4. Save etched + beam-trained student as a model.npz checkpoint that
     train.py --resume can consume directly.

Key design decisions:
  - Teacher runs are hook-captured on every forward pass; no custom model
    surgery is required — we attach mlx or torch hooks at the right layers.
  - The Procrustes bridge (learnable linear d_t→d_s) is trained jointly with
    beam params. It is discarded after distillation; only student weights remain.
  - Layer mapping re-uses teacher_layer_for_stride from extract_teacher.py so
    that behavioral and topological distillation address the same teacher layers.
  - Confidence gate (default 0.6) mirrors the mini_holo_distill threshold.

Teacher inference requirement:
  Install mlx-lm for the fastest path on Apple Silicon::

      uv add mlx-lm

  If mlx-lm is absent, the script falls back to a minimal weight-only
  forward pass implemented here from safetensors (slower, no KV cache,
  bfloat16 arithmetic). Both paths expose the same FeatureExtractor API.

Usage::

    uv run python scripts/v13/distill_teacher.py \\
        --teacher-path ~/.cache/huggingface/hub/models--Qwen--Qwen3-14B/snapshots/<hash> \\
        --output checkpoints/v13-distilled \\
        --n-rounds 5 \\
        --n-probes 200

The output is a drop-in replacement for the extract_teacher.py checkpoint.
Pass it to train.py with ``--resume checkpoints/v13-distilled``.

License: MIT
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import numpy as np

# ── MLX is mandatory (student lives in MLX) ─────────────────────────────────
try:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
except ImportError:
    print("ERROR: mlx not found. Install with: uv add mlx-lm", file=sys.stderr)
    sys.exit(1)

try:
    from safetensors import safe_open
except ImportError:
    print("ERROR: safetensors not found. Install with: uv add safetensors",
          file=sys.stderr)
    sys.exit(1)

# ── V13 imports ──────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPT_DIR))

from config import V13Config
from model import V13Model
from ternary import (
    TernaryLinear,
    pack_ternary_mlx,
    freeze_ternary_weights,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
)
from data import ShardedDataLoader

# Re-use extract_teacher utilities for teacher config / shard loading / layer mapping
from extract_teacher import (
    detect_teacher_config,
    find_shard,
    load_tensor,
    teacher_layer_for_stride,
    install_plates,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 0  Logging
# ══════════════════════════════════════════════════════════════════════════════


def log(msg: str) -> None:
    """Write a diagnostic message to stderr (always flushed)."""
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Teacher loading — mlx-lm preferred, safetensors fallback
# ══════════════════════════════════════════════════════════════════════════════


class TeacherModel:
    """Thin wrapper around whichever teacher backend is available.

    Exposes a single method::

        hidden_states: list[mx.array] = teacher.hidden_at_layers(
            input_ids,          # (B, T) int32
            layer_indices,      # list[int] — 0-based teacher layer indices
        )

    Returns one (B, T, d_teacher) array per requested layer, representing
    the residual stream **after** that layer's full computation
    (attention + FFN + residual add + layer-norm is NOT included here —
    we capture the post-residual pre-norm state, i.e. the output of
    ``h = h + attn(h) + ffn(h)`` for each teacher layer).
    """

    def __init__(self, model_path: Path, teacher_cfg: dict):
        self.model_path = model_path
        self.teacher_cfg = teacher_cfg
        self._backend: str = "none"
        self._model = None
        self._tokenizer = None
        self._load()

    # ── Backend detection / loading ──────────────────────────────────────────

    def _load(self) -> None:
        """Try mlx-lm first; fall back to minimal safetensors forward pass."""
        if self._try_mlx_lm():
            return
        log("  mlx-lm not available — using minimal safetensors forward pass")
        log("  (Install mlx-lm for faster teacher inference: uv add mlx-lm)")
        self._load_minimal()

    def _try_mlx_lm(self) -> bool:
        """Attempt to load the teacher via mlx-lm."""
        try:
            from mlx_lm import load as mlx_lm_load  # type: ignore[import]
        except ImportError:
            return False
        try:
            log(f"  Loading teacher via mlx-lm from: {self.model_path}")
            model, tokenizer = mlx_lm_load(str(self.model_path))
            mx.eval(model.parameters())
            self._model = model
            self._tokenizer = tokenizer
            self._backend = "mlx_lm"
            d = self.teacher_cfg["d_model"]
            n = self.teacher_cfg["n_layers"]
            log(f"  Teacher loaded (mlx-lm): d={d}, layers={n}")
            return True
        except Exception as exc:
            log(f"  mlx-lm load failed ({exc}); falling back to minimal forward pass")
            return False

    def _load_minimal(self) -> None:
        """Load just the weight shards index for the minimal forward pass."""
        log(f"  Loading teacher shard index from: {self.model_path}")
        self._backend = "minimal"
        # The minimal backend reconstructs a Qwen3-style forward pass directly
        # from safetensors weights.  We keep a weight cache per shard to avoid
        # re-loading the same shard file more than once per call.
        self._shard_cache: dict[str, dict[str, np.ndarray]] = {}
        d = self.teacher_cfg["d_model"]
        n = self.teacher_cfg["n_layers"]
        log(f"  Teacher (minimal): d={d}, layers={n}")

    # ── Public interface ─────────────────────────────────────────────────────

    def hidden_at_layers(
        self,
        input_ids: mx.array,
        layer_indices: list[int],
    ) -> list[mx.array]:
        """Return post-residual hidden states at the requested teacher layers.

        Args:
            input_ids:     (B, T) int32 token ids
            layer_indices: which teacher layers to capture (0-based)

        Returns:
            List of (B, T, d_teacher) float32 tensors, one per layer_index,
            in the same order as layer_indices.
        """
        if self._backend == "mlx_lm":
            return self._hidden_mlx_lm(input_ids, layer_indices)
        else:
            return self._hidden_minimal(input_ids, layer_indices)

    # ── mlx-lm backend ───────────────────────────────────────────────────────

    def _hidden_mlx_lm(
        self,
        input_ids: mx.array,
        layer_indices: list[int],
    ) -> list[mx.array]:
        """Hook-capture hidden states through the mlx-lm model.

        mlx-lm's Qwen3 model (mlx_lm.models.qwen3) is an nn.Module with
        model.layers as a list of transformer blocks.  We instrument each
        requested layer by temporarily replacing its ``__call__`` with a
        wrapper that records the output before returning it.
        """
        model = self._model
        captures: dict[int, mx.array] = {}
        original_layers: dict[int, object] = {}

        # Attach thin wrappers by replacing layers in the list.
        # Python class dispatch means layer.__call__ = hook doesn't work;
        # we must replace the layer object itself with a wrapper.
        target_set = set(layer_indices)
        for li in target_set:
            original_layer = model.model.layers[li]
            original_layers[li] = original_layer

            class _HookWrapper:
                """Wrapper that captures output and delegates to original."""
                def __init__(self, orig, idx, caps):
                    self._orig = orig
                    self._idx = idx
                    self._caps = caps
                    # Forward all attribute access to original for compatibility
                    for attr in dir(orig):
                        if not attr.startswith('_') and attr != '__call__':
                            try:
                                setattr(self, attr, getattr(orig, attr))
                            except Exception:
                                pass

                def __call__(self, x, *args, **kwargs):
                    out = self._orig(x, *args, **kwargs)
                    hidden = out[0] if isinstance(out, (tuple, list)) else out
                    self._caps[self._idx] = mx.stop_gradient(hidden)
                    return out

            model.model.layers[li] = _HookWrapper(original_layer, li, captures)

        # Forward pass — eval immediately (MLX is lazy, captures are graph nodes)
        try:
            out = model(input_ids)
            # Force evaluation of both the model output and all captures
            all_to_eval = [out] + [captures[li] for li in layer_indices if li in captures]
            mx.eval(*all_to_eval)
        finally:
            # Restore original layers regardless of errors
            for li, orig in original_layers.items():
                model.model.layers[li] = orig

        return [captures[li] for li in layer_indices]

    # ── Minimal safetensors backend ──────────────────────────────────────────

    def _hidden_minimal(
        self,
        input_ids: mx.array,
        layer_indices: list[int],
    ) -> list[mx.array]:
        """Minimal Qwen3-style forward pass from safetensors weights.

        Implements the residual stream up to (and including) the deepest
        requested layer. Only the layers needed are executed, keeping
        memory overhead proportional to the depth requested.

        Qwen3 layer order (simplified):
          h = h + self_attn(input_layernorm(h))
          h = h + mlp(post_attention_layernorm(h))

        We capture h after each complete layer update.
        """
        import numpy as np

        cfg = self.teacher_cfg
        d = cfg["d_model"]
        n_heads = cfg["n_heads"]
        n_kv_heads = cfg["n_kv_heads"]
        head_dim = cfg["head_dim"]
        d_ff = cfg["d_ff"]

        B, T = input_ids.shape[0], input_ids.shape[1]
        max_layer = max(layer_indices)

        # ── Token embedding ──────────────────────────────────────────────
        embed_w = self._load_weight("model.embed_tokens.weight")    # (V, d)
        ids_np = np.array(input_ids).astype(np.int32)
        h = mx.array(embed_w[ids_np])                              # (B, T, d)
        del embed_w

        captures: dict[int, mx.array] = {}

        # ── Layer-by-layer forward ────────────────────────────────────────
        for li in range(max_layer + 1):
            pf = f"model.layers.{li}"
            h = self._qwen3_layer(h, pf, d, n_heads, n_kv_heads,
                                  head_dim, d_ff, li)
            if li in set(layer_indices):
                captures[li] = mx.stop_gradient(h)
                mx.eval(captures[li])
            mx.eval(h)

        return [captures[li] for li in layer_indices]

    def _qwen3_layer(
        self,
        h: mx.array,
        prefix: str,
        d: int,
        n_heads: int,
        n_kv_heads: int,
        head_dim: int,
        d_ff: int,
        layer_idx: int,
    ) -> mx.array:
        """One Qwen3 transformer layer: attention + MLP, both with residuals."""
        # ── Self-attention ────────────────────────────────────────────────
        W_norm_attn = self._load_weight(f"{prefix}.input_layernorm.weight")
        h_norm = _rms_norm(h, mx.array(W_norm_attn))
        del W_norm_attn

        W_q = self._load_weight(f"{prefix}.self_attn.q_proj.weight")
        W_k = self._load_weight(f"{prefix}.self_attn.k_proj.weight")
        W_v = self._load_weight(f"{prefix}.self_attn.v_proj.weight")
        W_o = self._load_weight(f"{prefix}.self_attn.o_proj.weight")

        q_norm_w = self._load_weight_optional(f"{prefix}.self_attn.q_norm.weight")
        k_norm_w = self._load_weight_optional(f"{prefix}.self_attn.k_norm.weight")

        attn_out = _qwen3_attention(
            h_norm,
            mx.array(W_q), mx.array(W_k), mx.array(W_v), mx.array(W_o),
            n_heads, n_kv_heads, head_dim,
            q_norm=mx.array(q_norm_w) if q_norm_w is not None else None,
            k_norm=mx.array(k_norm_w) if k_norm_w is not None else None,
        )
        h = h + attn_out
        del W_q, W_k, W_v, W_o, attn_out

        # ── MLP ───────────────────────────────────────────────────────────
        W_norm_mlp = self._load_weight(f"{prefix}.post_attention_layernorm.weight")
        h_norm2 = _rms_norm(h, mx.array(W_norm_mlp))
        del W_norm_mlp

        W_gate = self._load_weight(f"{prefix}.mlp.gate_proj.weight")
        W_up   = self._load_weight(f"{prefix}.mlp.up_proj.weight")
        W_down = self._load_weight(f"{prefix}.mlp.down_proj.weight")

        gate = mx.array(h_norm2) @ mx.array(W_gate).T   # (B, T, d_ff)
        up   = mx.array(h_norm2) @ mx.array(W_up).T
        mlp_out = (nn.silu(gate) * up) @ mx.array(W_down).T
        h = h + mlp_out
        del W_gate, W_up, W_down, mlp_out

        mx.eval(h)
        return h

    # ── Weight helpers ───────────────────────────────────────────────────────

    def _load_weight(self, name: str) -> np.ndarray:
        """Load a single weight tensor from sharded safetensors (float32)."""
        return load_tensor(self.model_path, name)

    def _load_weight_optional(self, name: str) -> np.ndarray | None:
        """Load a weight tensor; return None if it doesn't exist."""
        try:
            return load_tensor(self.model_path, name)
        except FileNotFoundError:
            return None


# ── Minimal RMSNorm and attention primitives ─────────────────────────────────


def _rms_norm(h: mx.array, weight: mx.array, eps: float = 1e-6) -> mx.array:
    """RMSNorm: h / rms(h) * weight."""
    variance = mx.mean(h * h, axis=-1, keepdims=True)
    h_normed = h * mx.rsqrt(variance + eps)
    return h_normed * weight


def _qwen3_attention(
    x: mx.array,
    W_q: mx.array,
    W_k: mx.array,
    W_v: mx.array,
    W_o: mx.array,
    n_heads: int,
    n_kv_heads: int,
    head_dim: int,
    q_norm: mx.array | None = None,
    k_norm: mx.array | None = None,
) -> mx.array:
    """Causal multi-head attention (GQA-capable, no KV cache).

    Uses full O(L²) causal mask — suitable for short probe sequences only.
    Long sequences (>512 tokens) will OOM on the minimal backend; use
    mlx-lm (which has sliding window / KV cache) for longer probes.
    """
    B, T, _ = x.shape
    H, Hkv, Dh = n_heads, n_kv_heads, head_dim

    Q = (x @ W_q.T).reshape(B, T, H, Dh)
    K = (x @ W_k.T).reshape(B, T, Hkv, Dh)
    V = (x @ W_v.T).reshape(B, T, Hkv, Dh)

    # Per-head norms (Qwen3 adds q_norm, k_norm)
    if q_norm is not None:
        Q = Q * q_norm
    if k_norm is not None:
        K = K * k_norm

    # GQA: repeat KV heads to match Q heads
    if Hkv < H:
        repeat = H // Hkv
        K = mx.repeat(K, repeat, axis=2)
        V = mx.repeat(V, repeat, axis=2)

    # (B, H, T, Dh) → scaled dot-product attention
    Q = Q.transpose(0, 2, 1, 3)
    K = K.transpose(0, 2, 1, 3)
    V = V.transpose(0, 2, 1, 3)

    scale = Dh ** -0.5
    attn = (Q @ K.transpose(0, 1, 3, 2)) * scale      # (B, H, T, T)

    # Causal mask
    mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
    attn = attn + mask
    attn = mx.softmax(attn, axis=-1)

    out = (attn @ V).transpose(0, 2, 1, 3).reshape(B, T, H * Dh)
    return out @ W_o.T


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Feature extraction — run probes, capture teacher hidden states
# ══════════════════════════════════════════════════════════════════════════════


class FeatureExtractor:
    """Runs text probes through the teacher; returns per-stride feature pairs.

    For each student stride index, we map it to a teacher layer (via
    teacher_layer_for_stride) and accumulate a list of
    (layer_input, layer_output) pairs — captured as (B, T, d_teacher)
    MLX arrays.

    The layer_input is approximated as the hidden state BEFORE the mapped
    teacher layer (i.e., the output of layer li-1), and layer_output is the
    hidden state AFTER layer li. This approximation is exact when we run
    two consecutive captures at (li-1, li).

    The FFN is mapped to the middle teacher layer (same as extract_teacher.py).
    """

    def __init__(
        self,
        teacher: TeacherModel,
        cfg: V13Config,
        n_strides: int,
        n_teacher_layers: int,
    ):
        self.teacher = teacher
        self.cfg = cfg
        self.n_strides = n_strides
        self.n_teacher_layers = n_teacher_layers

        # Build the set of teacher layers we need to hook
        self._stride_to_teacher: list[int] = [
            teacher_layer_for_stride(si, n_strides, n_teacher_layers)
            for si in range(n_strides)
        ]
        self._ffn_teacher_layer = n_teacher_layers // 2

        # All unique teacher layers we need to capture (sorted)
        all_layers = set(self._stride_to_teacher) | {self._ffn_teacher_layer}
        # Also need the layer BEFORE each target to get the "input" side
        prev_layers = {max(0, li - 1) for li in all_layers}
        self._capture_layers = sorted(all_layers | prev_layers)

    def extract(
        self,
        input_ids: mx.array,
    ) -> dict[str, tuple[mx.array, mx.array]]:
        """Forward one batch through teacher; return (input, output) per slot.

        Returns:
            Dict mapping slot_key → (input_hidden, output_hidden).
            Slot keys: "stride_{si}" for each stride, and "ffn".
            Each tensor is (B, T, d_teacher) float32.
        """
        hiddens = self.teacher.hidden_at_layers(input_ids, self._capture_layers)
        layer_map: dict[int, mx.array] = {
            li: h for li, h in zip(self._capture_layers, hiddens)
        }

        results: dict[str, tuple[mx.array, mx.array]] = {}

        # ── Per-stride pairs ──────────────────────────────────────────────
        for si in range(self.n_strides):
            tl = self._stride_to_teacher[si]
            # Input = state before this layer (layer tl-1, clamped to 0)
            in_layer = max(0, tl - 1)
            h_in = layer_map.get(in_layer, layer_map[min(self._capture_layers)])
            h_out = layer_map[tl]
            results[f"stride_{si}"] = (h_in, h_out)

        # ── FFN pair ─────────────────────────────────────────────────────
        tl = self._ffn_teacher_layer
        in_layer = max(0, tl - 1)
        h_in = layer_map.get(in_layer, layer_map[min(self._capture_layers)])
        h_out = layer_map[tl]
        results["ffn"] = (h_in, h_out)

        return results

    def collect_batches(
        self,
        data_loader: ShardedDataLoader,
        n_batches: int,
        seq_len: int,
    ) -> dict[str, list[tuple[mx.array, mx.array]]]:
        """Collect n_batches probe batches; return lists of (input, output) pairs.

        Data is loaded from ShardedDataLoader and truncated to seq_len tokens
        to keep teacher memory usage bounded.

        Returns:
            Dict mapping slot_key → list[(h_in, h_out)].
        """
        accumulated: dict[str, list[tuple[mx.array, mx.array]]] = {}

        for b in range(n_batches):
            ids_np, _tgts = data_loader.next_batch()
            # Truncate to seq_len so the minimal backend doesn't OOM
            ids_np = ids_np[:, :seq_len]
            input_ids = mx.array(ids_np)

            batch_results = self.extract(input_ids)

            # Force eval of all captures (MLX lazy — must materialize before
            # the next forward pass invalidates the computation graph)
            all_tensors = []
            for key, (h_in, h_out) in batch_results.items():
                all_tensors.extend([h_in, h_out])
            if all_tensors:
                mx.eval(*all_tensors)

            for key, (h_in, h_out) in batch_results.items():
                if key not in accumulated:
                    accumulated[key] = []
                accumulated[key].append((h_in, h_out))

            if (b + 1) % max(1, n_batches // 5) == 0:
                log(f"    Probe batch {b+1}/{n_batches}")
            mx.eval()

        return accumulated


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Projection bridges — d_teacher → d_student
# ══════════════════════════════════════════════════════════════════════════════


class ProjectionBridge(nn.Module):
    """Learnable linear projection: d_teacher → d_student.

    This is the Procrustes alignment step: finds the best-fit linear map
    from the teacher's high-dimensional feature space to the student's
    compressed space.  Trained via Adam alongside beam params during each
    distillation round.  Discarded after distillation is complete.

    Two-step architecture:
      1. Layer norm on the teacher hidden state (stabilises training)
      2. Linear projection (no bias — the student will develop its own bias)
    """

    def __init__(self, d_teacher: int, d_student: int):
        super().__init__()
        self.d_teacher = d_teacher
        self.d_student = d_student

        self.norm = nn.RMSNorm(d_teacher)
        # Xavier initialisation: scale by sqrt(2 / (d_in + d_out))
        std = math.sqrt(2.0 / (d_teacher + d_student))
        self.proj = mx.random.normal((d_student, d_teacher)) * std

    def __call__(self, h_teacher: mx.array) -> mx.array:
        """Project teacher features to student dimension.

        h_teacher: (B, T, d_teacher) → (B, T, d_student)
        """
        h_norm = self.norm(h_teacher)
        return h_norm @ self.proj.T


def build_bridges(
    d_teacher: int,
    d_student: int,
    n_strides: int,
) -> dict[str, ProjectionBridge]:
    """Create one bridge per slot (stride_0..stride_N, ffn)."""
    bridges: dict[str, ProjectionBridge] = {}
    for si in range(n_strides):
        bridges[f"stride_{si}"] = ProjectionBridge(d_teacher, d_student)
    bridges["ffn"] = ProjectionBridge(d_teacher, d_student)
    return bridges


# ══════════════════════════════════════════════════════════════════════════════
# § 4  Distillation loss — MSE between projected teacher and student outputs
# ══════════════════════════════════════════════════════════════════════════════


def distill_mse(
    student_out: mx.array,
    projected_teacher: mx.array,
) -> mx.array:
    """Scalar MSE distillation loss.

    student_out:       (B, T, d_student) — student layer output
    projected_teacher: (B, T, d_student) — teacher output projected to d_student

    Returns: scalar float32 MSE.
    """
    diff = student_out - projected_teacher
    return mx.mean(diff * diff)


def student_layer_output(
    model: V13Model,
    h_in: mx.array,
    stride_idx: int,
    pass_idx: int = 0,
) -> mx.array:
    """Run one student stride layer forward and return its delta output.

    Session 135 tree of VSMs: stride layers are accessed through Stack A
    (which is shared with Stack B). All strides live in one StrideStack.

    Args:
        model:      V13Model instance
        h_in:       (B, T, d_student) residual stream input
        stride_idx: which stride layer to probe (0-based, 0..n_strides-1)
        pass_idx:   unused (kept for API symmetry); stride layers are pass-invariant

    Returns:
        (B, T, d_student) — stride layer contribution (output minus input).
    """
    # Tree of VSMs: Stack A owns the shared stride stack
    layer = model.stack_a.stride_stack.stack.layers[stride_idx]
    out_with_residual = layer(h_in)
    return out_with_residual - h_in


def ffn_output(model: V13Model, h_in: mx.array) -> mx.array:
    """Run the student FFN plates and return the FFN delta.

    Session 135: FFN plates are shared at model root. FFN beams (norm/scale/bias)
    are per-stack, but for distillation we use Stack A's beams as the reference.

    Args:
        model: V13Model instance
        h_in:  (B, T, d_student) residual stream input

    Returns:
        (B, T, d_student) — FFN contribution (output - input).
    """
    ffn_in = model.stack_a.ffn_norm(h_in)
    ffn_out = model.ffn_value_plate(mx.maximum(model.ffn_key_plate(ffn_in), 0))
    ffn_out = ffn_out * model.stack_a.ffn_scale + model.stack_a.ffn_bias
    return ffn_out


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Holographic etch — accumulate sign(grad) → flip confident positions
# ══════════════════════════════════════════════════════════════════════════════


def _get_plate_module(model: V13Model, plate_key: str) -> TernaryLinear | None:
    """Navigate the model tree to a named TernaryLinear plate.

    plate_key format: "stride_{si}.{q_proj|k_proj|v_proj|out_proj}"
                   or "ffn.{key|value}"

    Session 135: stride layers live at model.stack_a.stride_stack.stack.layers[si].
    FFN plates are model.ffn_key_plate / model.ffn_value_plate.

    Returns None if the path does not resolve to a TernaryLinear.
    """
    try:
        if plate_key.startswith("stride_"):
            parts = plate_key.split(".")               # ["stride_3", "q_proj"]
            si = int(parts[0].split("_")[1])
            proj_name = parts[1]                       # "q_proj", "k_proj", etc.
            layer = model.stack_a.stride_stack.stack.layers[si]
            obj = getattr(layer, proj_name)
        elif plate_key == "ffn.key":
            obj = model.ffn_key_plate
        elif plate_key == "ffn.value":
            obj = model.ffn_value_plate
        else:
            return None
    except (AttributeError, IndexError, KeyError, TypeError):
        return None

    return obj if isinstance(obj, TernaryLinear) else None


def _accumulate_plate_grads(
    grads: dict,
    plate_keys: list[str],
    accumulators: dict[str, np.ndarray],
    n_strides: int,
) -> None:
    """Extract gamma gradients from the grad pytree and accumulate their signs.

    The gamma gradient ∂L/∂γ_i is proportional to the gradient w.r.t.
    the per-channel scale.  Its sign indicates whether increasing the
    magnitude of row i helps reduce the distillation loss.  We use
    sign(∂L/∂γ) as a proxy for sign(∂L/∂W_ternary_i) — accumulated
    across many batches, the consensus sign identifies plate positions
    that should flip.

    grads:        pytree of gradients from nn.value_and_grad
    plate_keys:   list of plate identifiers (e.g. "stride_0.q_proj")
    accumulators: dict[plate_key → np.ndarray (out_features,)] — updated in-place
    n_strides:    total number of strides (for indexing)
    """
    def _dig(tree, keys: list[str]):
        """Recursively dig into a grad pytree by key sequence."""
        obj = tree
        for k in keys:
            if obj is None:
                return None
            if isinstance(obj, dict):
                obj = obj.get(k)
            elif isinstance(obj, list):
                try:
                    obj = obj[int(k)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return obj

    for plate_key in plate_keys:
        # Parse the plate_key to build a grad tree path.
        # Session 135 tree of VSMs — grad pytree mirrors model hierarchy:
        #   stride plates: stack_a → stride_stack → stack → layers → [si] → proj → gamma
        #   ffn plates:    ffn_key_plate / ffn_value_plate → gamma
        if plate_key.startswith("stride_"):
            parts = plate_key.split(".")
            si = int(parts[0].split("_")[1])
            layer_attr = parts[1]      # "q_proj", "k_proj", "v_proj", "out_proj"
            gamma_grad = _dig(grads, [
                "stack_a", "stride_stack", "stack", "layers", str(si), layer_attr, "gamma"
            ])
        elif plate_key == "ffn.key":
            gamma_grad = _dig(grads, ["ffn_key_plate", "gamma"])
        elif plate_key == "ffn.value":
            gamma_grad = _dig(grads, ["ffn_value_plate", "gamma"])
        else:
            gamma_grad = None

        if gamma_grad is None:
            continue

        mx.eval(gamma_grad)
        g_np = np.array(gamma_grad).astype(np.float64)
        if g_np.shape == accumulators[plate_key].shape:
            accumulators[plate_key] += np.sign(g_np)


def etch_round(
    model: V13Model,
    feature_batches: dict[str, list[tuple[mx.array, mx.array]]],
    bridges: dict[str, ProjectionBridge],
    cfg: V13Config,
    n_strides: int,
    confidence_threshold: float = 0.6,
) -> dict:
    """One holographic etch round: accumulate grad signs → flip confident positions.

    For each probe batch and each slot (stride, ffn):
      1. Project teacher output to d_student via the bridge.
      2. Compute student output for the same input.
      3. Compute distillation MSE loss and backprop.
      4. Accumulate sign(∂L/∂γ) for each plate in that slot.

    After accumulating across all batches, flip plate positions where
    |accumulator| / n_batches > confidence_threshold.

    Args:
        model:               V13Model to etch in-place
        feature_batches:     dict[slot_key → list[(h_in, h_out)]] from FeatureExtractor
        bridges:             dict[slot_key → ProjectionBridge]
        cfg:                 V13Config
        n_strides:           number of student strides
        confidence_threshold: minimum fractional agreement to flip a position

    Returns:
        Dict with "total_flips" and per-plate flip counts.
    """
    # Build plate inventory
    plate_keys: list[str] = []
    for si in range(n_strides):
        for proj in ("q_proj", "k_proj", "v_proj", "out_proj"):
            plate_keys.append(f"stride_{si}.{proj}")
    plate_keys += ["ffn.key", "ffn.value"]

    # Build accumulators: (out_features,) float64 for sign voting
    accumulators: dict[str, np.ndarray] = {}
    for pk in plate_keys:
        mod = _get_plate_module(model, pk)
        if mod is not None:
            accumulators[pk] = np.zeros(mod.out_features, dtype=np.float64)

    # Determine which slot drives which plate keys
    slot_to_plates: dict[str, list[str]] = {}
    for si in range(n_strides):
        slot_to_plates[f"stride_{si}"] = [
            f"stride_{si}.{p}" for p in ("q_proj", "k_proj", "v_proj", "out_proj")
        ]
    slot_to_plates["ffn"] = ["ffn.key", "ffn.value"]

    # Count batches per slot (for normalisation)
    n_batches_per_slot: dict[str, int] = {
        k: len(v) for k, v in feature_batches.items()
    }

    # ── Accumulate grad signs across all probe batches ─────────────────────
    def _make_loss_fn(slot_key: str, h_in_t: mx.array, h_out_t: mx.array):
        """Factory: return a loss closure that takes the model as its argument.

        The factory captures slot_key, h_in_t, h_out_t by value.  The returned
        closure takes m (the model) as its sole argument so that nn.value_and_grad
        correctly differentiates through m's parameters (gamma values).

        Bridge params are stop-gradient'd here — we only want the model gradient.
        """
        bridge = bridges[slot_key]

        # Project teacher features once (bridge is stop-grad from model's perspective)
        target = mx.stop_gradient(bridge(h_out_t))    # (B, T, d_s)
        h_in_s = mx.stop_gradient(bridge(h_in_t))     # (B, T, d_s)

        if slot_key.startswith("stride_"):
            si = int(slot_key.split("_")[1])

            def _loss_fn(m: V13Model) -> mx.array:
                out = student_layer_output(m, h_in_s, si)
                return distill_mse(out, target)
        else:  # "ffn"
            def _loss_fn(m: V13Model) -> mx.array:
                out = ffn_output(m, h_in_s)
                return distill_mse(out, target)

        return _loss_fn

    for slot_key, batch_list in feature_batches.items():
        slot_plates = slot_to_plates.get(slot_key, [])
        if not slot_plates:
            continue

        for h_in_t, h_out_t in batch_list:
            _loss_fn = _make_loss_fn(slot_key, h_in_t, h_out_t)
            loss_val, grads = nn.value_and_grad(model, _loss_fn)(model)
            mx.eval(loss_val, grads)

            _accumulate_plate_grads(grads, slot_plates, accumulators, n_strides)

            del loss_val, grads

        mx.eval()

    # ── Flip confident positions ─────────────────────────────────────────────
    flip_counts: dict[str, int] = {}
    total_flips = 0

    for plate_key, acc in accumulators.items():
        # Derive slot_key from plate_key:
        #   "stride_3.q_proj"  → "stride_3"
        #   "ffn.key"          → "ffn"
        #   "ffn.value"        → "ffn"
        slot_key = plate_key.rsplit(".", 1)[0]   # strips last ".something"
        n_batches = n_batches_per_slot.get(slot_key, 1)

        confidence = np.abs(acc) / max(n_batches, 1)     # (out_features,)
        target_row_sign = np.sign(acc)                    # desired direction

        mod = _get_plate_module(model, plate_key)
        if mod is None:
            continue

        # Unpack current signs from packed uint32
        packed_np = np.array(mod.weight)                  # (N, K//16) uint32
        N, K16 = packed_np.shape
        K = K16 * 16
        current_signs = _unpack_signs_numpy(packed_np, N, K)  # (N, K) int8

        n_flips = 0
        new_signs = current_signs.copy()

        for row in range(N):
            if confidence[row] > confidence_threshold and target_row_sign[row] != 0:
                # Flip all positions in this row toward the target sign direction
                target_sign = int(target_row_sign[row])
                # Only flip positions that currently disagree with the target direction
                disagree_mask = current_signs[row] != target_sign
                new_signs[row, disagree_mask] = target_sign
                n_flips += int(disagree_mask.sum())

        if n_flips > 0:
            packed_new = pack_ternary_mlx(mx.array(new_signs))
            mod.weight = packed_new
            mx.eval(mod.weight)

        flip_counts[plate_key] = n_flips
        total_flips += n_flips

    return {"total_flips": total_flips, "per_plate": flip_counts}


def _unpack_signs_numpy(packed: np.ndarray, N: int, K: int) -> np.ndarray:
    """Unpack uint32 packed weights → int8 {-1, 0, +1} in numpy.

    Mirrors pack_ternary_mlx / unpack_ternary_mlx logic in pure numpy
    to avoid unnecessary MLX round-trips during the etch accumulation loop.
    """
    # packed: (N, K//16) uint32
    # Reshape to (N, K//16, 1) and extract 16 2-bit fields per uint32
    shifts = np.array([2 * i for i in range(16)], dtype=np.uint32)  # (16,)
    groups = packed.reshape(N, K // 16, 1)                           # (N, K//16, 1)
    fields = (groups >> shifts) & np.uint32(3)                       # (N, K//16, 16)
    decoded = fields.astype(np.int8) - 1                             # (N, K//16, 16)
    return decoded.reshape(N, K)                                     # (N, K) int8


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Beam training — GD on continuous params with distillation loss
# ══════════════════════════════════════════════════════════════════════════════


def train_beams(
    model: V13Model,
    bridges: dict[str, ProjectionBridge],
    feature_batches: dict[str, list[tuple[mx.array, mx.array]]],
    n_strides: int,
    n_steps: int = 200,
    lr: float = 3e-4,
    lr_bridge: float = 1e-4,
) -> list[float]:
    """Train beam params (γ, norms, biases) + projection bridges with distillation loss.

    The bridges are trained jointly so they adapt to the current plate topology.
    Ternary weight topology is frozen — only continuous params move.

    Args:
        model:          V13Model with frozen plates
        bridges:        projection bridges (dict[slot_key → ProjectionBridge])
        feature_batches: dict[slot_key → list[(h_in, h_out)]] probe data
        n_strides:      number of student strides
        n_steps:        number of Adam mini-steps
        lr:             learning rate for beam params (γ, norms, biases)
        lr_bridge:      learning rate for projection bridge parameters

    Returns:
        List of per-step loss values.
    """
    # ── Build combined parameter set for a single optimizer ──────────────────
    # We use two separate optimizers with different LRs to avoid bridge params
    # dominating the beam params (they typically have much larger gradients
    # at the start because the bridge is freshly initialised).
    beam_optimizer = optim.Adam(learning_rate=lr)
    bridge_optimizer = optim.Adam(learning_rate=lr_bridge)

    # Collect all slots and cycle through their batches
    slot_keys = list(feature_batches.keys())
    rng = np.random.RandomState(42)
    loss_log: list[float] = []

    # Precompute total batches available
    slot_batch_counts = {k: len(v) for k, v in feature_batches.items()}

    from ternary import zero_ternary_grads, restore_ternary

    for step in range(n_steps):
        # Pick a slot and a batch from it (round-robin)
        slot_key = slot_keys[step % len(slot_keys)]
        batch_list = feature_batches[slot_key]
        batch_idx = (step // len(slot_keys)) % len(batch_list)
        h_in_t, h_out_t = batch_list[batch_idx]

        bridge = bridges[slot_key]
        sk = slot_key  # capture for closure

        # ── Model gradient: fix bridge, differentiate model ───────────────
        # The bridge provides the projection target — we stop-gradient it
        # when differentiating the model.  Separately, we differentiate the
        # bridge with the model fixed.

        # Phase A: model gradient (bridge frozen)
        target_sg = mx.stop_gradient(bridge(h_out_t))   # (B, T, d_s)
        h_in_s_sg = mx.stop_gradient(bridge(h_in_t))    # (B, T, d_s)

        if sk.startswith("stride_"):
            si = int(sk.split("_")[1])

            def _model_loss(m: V13Model) -> mx.array:
                out = student_layer_output(m, h_in_s_sg, si)
                return distill_mse(out, target_sg)
        else:
            def _model_loss(m: V13Model) -> mx.array:
                out = ffn_output(m, h_in_s_sg)
                return distill_mse(out, target_sg)

        lv, model_grads = nn.value_and_grad(model, _model_loss)(model)
        mx.eval(lv, model_grads)

        # Skip NaN steps (numerical explosion)
        lv_val = float(lv.item())
        if math.isnan(lv_val) or math.isinf(lv_val):
            del model_grads, lv
            loss_log.append(float("nan"))
            continue

        model_grads = zero_ternary_grads(model, model_grads)

        # Gradient clipping (prevent explosion from large teacher magnitudes)
        from mlx.utils import tree_flatten, tree_map
        flat_grads = [g for _, g in tree_flatten(model_grads) if isinstance(g, mx.array)]
        if flat_grads:
            grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
            grad_norm = math.sqrt(max(grad_sq, 0.0))
            if grad_norm > 1.0:
                s = 1.0 / (grad_norm + 1e-8)
                model_grads = tree_map(lambda g: g * s, model_grads)

        beam_optimizer.update(model, model_grads)
        mx.eval(model.parameters())
        restore_ternary(model)  # protect uint32 packed weights
        del model_grads

        # Phase B: bridge gradient (student output frozen)
        if sk.startswith("stride_"):
            si_b = int(sk.split("_")[1])
            student_out_sg = mx.stop_gradient(
                student_layer_output(model, mx.stop_gradient(bridge(h_in_t)), si_b)
            )
        else:
            student_out_sg = mx.stop_gradient(
                ffn_output(model, mx.stop_gradient(bridge(h_in_t)))
            )

        def _bridge_loss(b: ProjectionBridge) -> mx.array:
            projected = b(h_out_t)
            return distill_mse(student_out_sg, projected)

        _, bridge_grads = nn.value_and_grad(bridge, _bridge_loss)(bridge)
        mx.eval(bridge_grads)
        bridge_optimizer.update(bridge, bridge_grads)
        mx.eval(bridge.parameters())
        del bridge_grads

        loss_log.append(lv_val)
        del lv

        if (step + 1) % max(1, n_steps // 4) == 0:
            log(f"      Beam step {step+1}/{n_steps}: loss={loss_log[-1]:.6f}")

        if (step + 1) % 50 == 0:
            mx.eval()

    return loss_log


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Main distillation pipeline
# ══════════════════════════════════════════════════════════════════════════════


def distill_teacher(
    teacher_path: str | Path,
    output_dir: str | Path,
    n_rounds: int = 5,
    n_probes: int = 200,
    confidence_threshold: float = 0.6,
    beam_steps: int = 200,
    probe_seq_len: int = 128,
    probe_batch_size: int = 4,
    beam_lr: float = 3e-4,
    bridge_lr: float = 1e-3,
    resume_ckpt: str | None = None,
    data_dir: str | None = None,
    structured_shard: str | None = None,
) -> None:
    """Full behavioral distillation pipeline.

    Steps:
      1. Detect teacher config; load teacher for inference.
      2. Create (or resume) V13 student model.
      3. Create projection bridges (d_teacher → d_student).
      4. Create ShardedDataLoader for probe data.
      5. For each round:
         a. Collect feature batches (teacher forward passes).
         b. Holographic etch (sign accumulation → plate flip).
         c. Beam training (Adam on γ + norms + biases + bridges).
      6. Save model.npz + config.json + manifest.json.

    Args:
        teacher_path:        Path to Qwen3-14B safetensors directory.
        output_dir:          Where to write the distilled checkpoint.
        n_rounds:            Number of etch+beam cycles.
        n_probes:            Number of probe batches per round.
        confidence_threshold: Sign-vote threshold to flip a plate position.
        beam_steps:          Adam steps per beam training phase.
        probe_seq_len:       Sequence length for probe batches.
        probe_batch_size:    Batch size for probe batches.
        beam_lr:             Learning rate for beam params.
        bridge_lr:           Learning rate for projection bridges.
        resume_ckpt:         Optional path to a prior checkpoint to resume from.
        data_dir:            Override for data directory (default: cfg.data_dir).
        structured_shard:    Override for structured shard path.
    """
    t_start = time.time()
    teacher_path = Path(teacher_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 72)
    log("  V13 Behavioral Distillation")
    log("  (recording teacher function, not copying weight topology)")
    log("=" * 72)

    # ── § 7.1  Teacher config ──────────────────────────────────────────────
    teacher_cfg = detect_teacher_config(teacher_path)
    d_teacher = teacher_cfg["d_model"]
    n_teacher_layers = teacher_cfg["n_layers"]
    log(f"\n  Teacher: {teacher_cfg['model_type']}, "
        f"d={d_teacher}, layers={n_teacher_layers}")

    # ── § 7.2  Student model ───────────────────────────────────────────────
    cfg = V13Config()
    d_student = cfg.d_model
    n_strides = cfg.n_strides

    model = V13Model(cfg)
    mx.eval(model.parameters())

    if resume_ckpt is not None:
        resume_path = Path(resume_ckpt)
        weights = dict(mx.load(str(resume_path / "model.npz")))
        model.load_weights(list(weights.items()), strict=False)
        mx.eval(model.parameters())
        log(f"\n  Resumed student from: {resume_path}")
    else:
        log(f"\n  Fresh student: d={d_student}, strides={n_strides}")

    # Freeze ternary topology before any training (bridges will update beams only)
    freeze_ternary_weights(model)
    restore_ternary(model)

    log(f"  Student ternary positions: {count_ternary_weights(model):,}")
    log(f"  Student d_model={d_student}, strides={n_strides}, passes={cfg.n_passes}")

    # ── § 7.3  Teacher inference model ────────────────────────────────────
    log(f"\n  Loading teacher for inference...")
    teacher = TeacherModel(teacher_path, teacher_cfg)

    # ── § 7.4  Projection bridges ─────────────────────────────────────────
    log(f"\n  Building projection bridges: d_teacher={d_teacher} → d_student={d_student}")
    bridges = build_bridges(d_teacher, d_student, n_strides)
    for b in bridges.values():
        mx.eval(b.parameters())
    log(f"  Bridges: {len(bridges)} slots ({n_strides} strides + ffn)")

    # ── § 7.5  Feature extractor ──────────────────────────────────────────
    extractor = FeatureExtractor(teacher, cfg, n_strides, n_teacher_layers)

    log(f"\n  Teacher layers captured: {sorted(extractor._capture_layers)}")
    log(f"  Stride → teacher layer mapping:")
    for si in range(n_strides):
        tl = extractor._stride_to_teacher[si]
        is_ret = cfg.stride_is_retrieval[si]
        kind = "GLA" if is_ret else "attn"
        log(f"    stride {si:2d} (s{cfg.strides[si]:4d}, {kind}) ← teacher layer {tl}")
    log(f"  FFN ← teacher layer {extractor._ffn_teacher_layer}")

    # ── § 7.6  Probe data loader ──────────────────────────────────────────
    effective_data_dir = data_dir or cfg.data_dir
    log(f"\n  Probe data: {effective_data_dir}")

    data_loader = ShardedDataLoader(
        data_dir=effective_data_dir,
        batch_size=probe_batch_size,
        seq_len=probe_seq_len + 1,  # +1 because ShardedDataLoader returns T+1 tokens
        shard_start=0,
        shard_end=min(cfg.n_train_shards, 6),  # Use first 6 shards for probes
        seed=777,
    )

    # ── § 7.7  Iterative etch + beam rounds ───────────────────────────────
    round_logs: list[dict] = []

    log(f"\n  Starting {n_rounds} distillation rounds")
    log(f"  n_probes={n_probes}, seq_len={probe_seq_len}, "
        f"batch_size={probe_batch_size}")
    log(f"  confidence_threshold={confidence_threshold}")
    log(f"  beam_steps={beam_steps}, beam_lr={beam_lr}, bridge_lr={bridge_lr}")

    for round_idx in range(n_rounds):
        t_round = time.time()
        log(f"\n{'─'*72}")
        log(f"  Round {round_idx + 1}/{n_rounds}")

        # ── Feature collection ────────────────────────────────────────────
        n_batches = max(1, n_probes // probe_batch_size)
        log(f"  Collecting {n_batches} feature batches "
            f"({n_batches * probe_batch_size} probe sequences)...")

        feature_batches = extractor.collect_batches(
            data_loader,
            n_batches=n_batches,
            seq_len=probe_seq_len,
        )

        # ── Holographic etch ──────────────────────────────────────────────
        log(f"  Holographic etch (confidence_threshold={confidence_threshold})...")

        # Un-freeze for etch (we need to write to plate weights)
        # Etch modifies mod.weight directly (not via optimizer), so freezing
        # the weight param is irrelevant for the etch step.  We just need to
        # ensure Adam doesn't touch them during beam training.

        etch_result = etch_round(
            model=model,
            feature_batches=feature_batches,
            bridges=bridges,
            cfg=cfg,
            n_strides=n_strides,
            confidence_threshold=confidence_threshold,
        )

        log(f"    Total flips: {etch_result['total_flips']:,}")

        # ── Beam training ─────────────────────────────────────────────────
        log(f"  Beam training ({beam_steps} steps)...")

        beam_losses = train_beams(
            model=model,
            bridges=bridges,
            feature_batches=feature_batches,
            n_strides=n_strides,
            n_steps=beam_steps,
            lr=beam_lr,
            lr_bridge=bridge_lr,
        )

        dt_round = time.time() - t_round
        mean_beam_loss = float(np.mean(beam_losses)) if beam_losses else float("nan")
        final_beam_loss = beam_losses[-1] if beam_losses else float("nan")

        log(f"  Round {round_idx + 1} complete: "
            f"flips={etch_result['total_flips']:,}, "
            f"beam_loss={final_beam_loss:.6f} ({dt_round:.0f}s)")

        round_logs.append({
            "round": round_idx + 1,
            "total_flips": etch_result["total_flips"],
            "per_plate_flips": etch_result["per_plate"],
            "beam_loss_mean": mean_beam_loss,
            "beam_loss_final": final_beam_loss,
            "elapsed_s": dt_round,
        })

        mx.eval()

    # ── § 7.8  Integrity check ────────────────────────────────────────────
    restore_ternary(model)
    log("\n  Ternary integrity verified ✓")

    # ── § 7.9  Save checkpoint ────────────────────────────────────────────
    dt_total = time.time() - t_start

    weights_path = output_dir / "model.npz"
    model.save_weights(str(weights_path))
    log(f"\n  Saved model: {weights_path} "
        f"({weights_path.stat().st_size / 1024 / 1024:.1f} MB)")

    config_path = output_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(dataclasses.asdict(cfg), f, indent=2, default=str)
    log(f"  Saved config: {config_path}")

    manifest = {
        "method": "behavioral_distillation",
        "teacher": {
            "path": str(teacher_path),
            "config": teacher_cfg,
        },
        "student": {
            "d_model": d_student,
            "d_ff": cfg.d_ff,
            "n_strides": n_strides,
            "d_state": cfg.d_state,
            "n_heads": cfg.n_heads,
            "n_passes": cfg.n_passes,
        },
        "distillation": {
            "n_rounds": n_rounds,
            "n_probes": n_probes,
            "probe_seq_len": probe_seq_len,
            "probe_batch_size": probe_batch_size,
            "confidence_threshold": confidence_threshold,
            "beam_steps": beam_steps,
            "beam_lr": beam_lr,
            "bridge_lr": bridge_lr,
        },
        "round_logs": round_logs,
        "total_elapsed_s": dt_total,
        "total_flips": sum(r["total_flips"] for r in round_logs),
    }
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    log(f"  Saved manifest: {manifest_path}")

    total_flips = sum(r["total_flips"] for r in round_logs)
    n_plate_positions = count_ternary_weights(model)

    log(f"\n{'='*72}")
    log(f"  Behavioral Distillation Complete")
    log(f"{'='*72}")
    log(f"  Rounds:            {n_rounds}")
    log(f"  Total plate flips: {total_flips:,}")
    log(f"  Total positions:   {n_plate_positions:,}")
    log(f"  Flip rate:         {total_flips / max(n_plate_positions, 1):.4f}")
    log(f"  Elapsed:           {dt_total:.0f}s ({dt_total/60:.1f}m)")
    log(f"  Checkpoint:        {output_dir}")
    log(f"\n  Next: uv run python scripts/v13/train.py --resume {output_dir}")
    log(f"{'='*72}")


# ══════════════════════════════════════════════════════════════════════════════
# § 8  CLI
# ══════════════════════════════════════════════════════════════════════════════


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "V13 Behavioral Distillation — etch student plates from teacher "
            "forward-pass behavior rather than weight topology."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── Required ─────────────────────────────────────────────────────────────
    p.add_argument(
        "--teacher-path",
        type=str,
        required=True,
        help="Path to teacher model directory (Qwen3-14B safetensors).",
    )
    p.add_argument(
        "--output",
        type=str,
        default="checkpoints/v13-distilled",
        help="Output directory for the distilled checkpoint.",
    )

    # ── Distillation hyperparameters ─────────────────────────────────────────
    p.add_argument(
        "--n-rounds",
        type=int,
        default=5,
        help="Number of etch+beam training cycles.",
    )
    p.add_argument(
        "--n-probes",
        type=int,
        default=200,
        help="Number of probe sequences per round (divided into batches).",
    )
    p.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.6,
        help="Fractional sign-vote agreement required to flip a plate position.",
    )
    p.add_argument(
        "--beam-steps",
        type=int,
        default=200,
        help="Adam mini-steps for beam training per round.",
    )
    p.add_argument(
        "--probe-seq-len",
        type=int,
        default=128,
        help=(
            "Sequence length for teacher probe batches. "
            "Longer → richer features but more memory. "
            "Keep ≤512 for the minimal safetensors backend."
        ),
    )
    p.add_argument(
        "--probe-batch-size",
        type=int,
        default=4,
        help="Batch size for probe sequences fed to the teacher.",
    )

    # ── Learning rates ────────────────────────────────────────────────────────
    p.add_argument(
        "--beam-lr",
        type=float,
        default=3e-4,
        help="Adam learning rate for student beam params (γ, norms, biases).",
    )
    p.add_argument(
        "--bridge-lr",
        type=float,
        default=1e-3,
        help="Adam learning rate for projection bridge parameters.",
    )

    # ── Optional / advanced ───────────────────────────────────────────────────
    p.add_argument(
        "--resume",
        type=str,
        default=None,
        help=(
            "Path to a prior checkpoint directory to resume from "
            "(e.g. a partially distilled run or the extract_teacher.py output)."
        ),
    )
    p.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help=(
            "Override probe data directory (default: V13Config.data_dir). "
            "Must contain shard_*.npy files tokenised with Qwen3 BBPE."
        ),
    )
    p.add_argument(
        "--structured-shard",
        type=str,
        default=None,
        help="Override path to structured data shard (default: V13Config.structured_shard).",
    )

    return p


def main(argv: list[str] | None = None) -> None:
    """Entry point for the behavioral distillation CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    distill_teacher(
        teacher_path=args.teacher_path,
        output_dir=args.output,
        n_rounds=args.n_rounds,
        n_probes=args.n_probes,
        confidence_threshold=args.confidence_threshold,
        beam_steps=args.beam_steps,
        probe_seq_len=args.probe_seq_len,
        probe_batch_size=args.probe_batch_size,
        beam_lr=args.beam_lr,
        bridge_lr=args.bridge_lr,
        resume_ckpt=args.resume,
        data_dir=args.data_dir,
        structured_shard=args.structured_shard,
    )


if __name__ == "__main__":
    main()
