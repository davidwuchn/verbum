"""Ternary substrate for v8's hot-path components.

Self-contained — no imports from other verbum modules.

TernaryLinear uses mx.quantized_matmul at 2-bit (bits=2, group_size=64)
via Apple's AMX hardware path.  This replaces the custom Metal ternary
matmul kernels used in earlier iterations and yields a 2–4× speedup on
Apple Silicon for the dominant level-0 operations.

Ternary weights {-1, 0, +1} map to 2-bit integers {0, 1, 2}:
    encoded = ternary + 1

Per-channel gamma folds into quantized_matmul scales/biases so the
dequant is exact:
    gamma * encoded + (-gamma) = {-gamma, 0, +gamma} ✓

MLX packs 16 two-bit values per uint32 (little-endian bit order).
TernaryLinear stores:
    weight  — (N, K//16) uint32 packed topology (evolutionary, not optimized)
    gamma   — (N,)       float32 per-channel scale (trained by Adam)

The ternary topology evolves via mutation + tournament selection.  Gamma
is trained normally with Adam.  quantized_matmul supports autograd
natively so no custom VJP is needed for TernaryLinear.

TernaryEmbedding is UNCHANGED: embedding lookup is a gather, not a
matmul.  It keeps the existing custom VJP and uint8 (4-per-byte) packed
format.

Memory per ternary weight:
    TernaryLinear inference:  0.125 bytes (2-bit packed)
    TernaryEmbedding:         0.25  bytes (2-bit packed in uint8)

License: MIT
"""

from __future__ import annotations

import math
from typing import Any

import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# MLX uint32 pack / unpack  (for TernaryLinear + quantized_matmul)
# ══════════════════════════════════════════════════════════════════════
#
# MLX packs 16 two-bit values per uint32 in little-endian bit order:
#   value i occupies bits [2*i : 2*i+2]  for i in 0..15
#
# Encoding:  -1 → 0,  0 → 1,  +1 → 2   (ternary + 1)
# Decode:    (field & 0x3) - 1


def pack_ternary_mlx(w_int8: mx.array) -> mx.array:
    """Pack int8 {-1, 0, +1} weights [N, K] → uint32 [N, K//16].

    MLX little-endian bit layout: value i at bits [2*i : 2*i+2], i=0..15.
    Encoding: ternary + 1  →  {0, 1, 2}.
    K must be divisible by 16.
    """
    N, K = w_int8.shape
    assert K % 16 == 0, f"K={K} must be divisible by 16 for MLX 2-bit packing"

    # Shift {-1,0,+1} → {0,1,2} and promote to uint32 to avoid overflow
    encoded = (w_int8.astype(mx.int32) + 1).astype(mx.uint32)  # (N, K)

    # Reshape to (N, K//16, 16) — groups of 16 values per uint32
    groups = encoded.reshape(N, K // 16, 16)  # (N, K//16, 16)

    # Build the packed uint32: value i goes into bits [2*i : 2*i+2]
    # shifts[i] = 2*i for i in 0..15
    shifts = mx.array([2 * i for i in range(16)], dtype=mx.uint32)  # (16,)
    shifted = groups << shifts  # (N, K//16, 16) — each value in its bit slot

    # OR-reduce over the last axis to pack 16 values into one uint32
    packed = mx.sum(shifted, axis=-1)  # (N, K//16) uint32
    # mx.sum on uint32 gives uint32 — the OR semantics hold because
    # the 2-bit fields don't overlap (each occupies distinct bits).
    return packed.astype(mx.uint32)


def unpack_ternary_mlx(wq_uint32: mx.array) -> mx.array:
    """Unpack uint32 [N, K//16] → int8 {-1, 0, +1} [N, K].

    Inverse of pack_ternary_mlx.
    """
    N, K16 = wq_uint32.shape
    K = K16 * 16

    # Expand to (N, K//16, 1) then broadcast shifts
    packed = wq_uint32.reshape(N, K16, 1)  # (N, K//16, 1)
    shifts = mx.array([2 * i for i in range(16)], dtype=mx.uint32)  # (16,)

    # Extract each 2-bit field; mask with integer literal (MLX broadcasts scalars)
    fields = (packed >> shifts) & 3  # (N, K//16, 16) uint32

    # Decode: field - 1 → {-1, 0, +1}
    decoded = fields.astype(mx.int32) - 1  # (N, K//16, 16) int32

    return decoded.reshape(N, K).astype(mx.int8)


# ══════════════════════════════════════════════════════════════════════
# uint8 pack / unpack  (for TernaryEmbedding — unchanged)
# ══════════════════════════════════════════════════════════════════════
#
# Encoding:  -1 → 0b00,  0 → 0b01,  +1 → 0b10   (0b11 unused)
# Positions: bits {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}
# Decode:    ((packed >> shift) & 0x3) - 1
# K must be divisible by 4.


def pack_ternary(w: mx.array) -> mx.array:
    """Pack int8 {-1, 0, +1} weights [N, K] → uint8 [N, K//4].

    Used by TernaryEmbedding (4 values per byte, big-endian within byte).
    K must be divisible by 4.
    """
    assert w.shape[-1] % 4 == 0, f"K={w.shape[-1]} must be divisible by 4"
    w_shifted = (w.astype(mx.int16) + 1).astype(mx.uint8)
    packed = (
        (w_shifted[:, 0::4] << 6) |
        (w_shifted[:, 1::4] << 4) |
        (w_shifted[:, 2::4] << 2) |
        w_shifted[:, 3::4]
    )
    return packed.astype(mx.uint8)


def unpack_ternary(packed: mx.array, K: int) -> mx.array:
    """Unpack uint8 [N, K//4] → int8 {-1, 0, +1} [N, K].

    Inverse of pack_ternary. K is the logical (unpacked) weight dimension.
    """
    w0 = ((packed >> 6) & 0x3).astype(mx.int16) - 1
    w1 = ((packed >> 4) & 0x3).astype(mx.int16) - 1
    w2 = ((packed >> 2) & 0x3).astype(mx.int16) - 1
    w3 = (packed & 0x3).astype(mx.int16) - 1
    N = packed.shape[0]
    stacked = mx.stack([w0, w1, w2, w3], axis=-1)  # (N, K//4, 4)
    return stacked.reshape(N, K).astype(mx.int8)


# ══════════════════════════════════════════════════════════════════════
# Ternary initialization
# ══════════════════════════════════════════════════════════════════════


def _ternary_init(out_features: int, in_features: int) -> tuple[mx.array, mx.array]:
    """Initialize TernaryLinear weights: Kaiming normal → quantize → MLX uint32 pack.

    Returns:
        wq_uint32: (out_features, in_features//16) uint32  — packed topology
        gamma:     (out_features,) float32                 — per-channel scale
    """
    assert in_features % 16 == 0, (
        f"in_features={in_features} must be divisible by 16 for MLX 2-bit packing"
    )
    # Kaiming normal: std = sqrt(2 / in_features)
    std = math.sqrt(2.0 / in_features)
    w_init = mx.random.normal((out_features, in_features)) * std

    # Per-channel absmean quantization
    gamma = mx.abs(w_init).mean(axis=-1)
    w_scaled = w_init / (mx.expand_dims(gamma, axis=-1) + 1e-8)
    w_q = mx.clip(mx.round(w_scaled), -1, 1).astype(mx.int8)

    # Pack 16 weights per uint32 for quantized_matmul
    wq_uint32 = pack_ternary_mlx(w_q)  # (N, K//16) uint32

    return wq_uint32, gamma


def _ternary_embed_init(vocab_size: int, d_model: int) -> tuple[mx.array, mx.array]:
    """Initialize TernaryEmbedding weights: Kaiming normal → quantize → uint8 pack.

    Returns:
        w_packed: (vocab_size, d_model//4) uint8  — packed topology
        gamma:    (vocab_size,) float32           — per-token scale
    """
    assert d_model % 4 == 0, f"d_model={d_model} must be divisible by 4 for packing"
    std = math.sqrt(2.0 / d_model)
    w_init = mx.random.normal((vocab_size, d_model)) * std

    gamma = mx.abs(w_init).mean(axis=-1)
    w_scaled = w_init / (mx.expand_dims(gamma, axis=-1) + 1e-8)
    w_q = mx.clip(mx.round(w_scaled), -1, 1).astype(mx.int8)

    w_packed = pack_ternary(w_q)  # (vocab_size, d_model//4) uint8
    return w_packed, gamma


# ══════════════════════════════════════════════════════════════════════
# TernaryLinear — mx.quantized_matmul path (AMX / Apple Silicon)
# ══════════════════════════════════════════════════════════════════════


class TernaryLinear(nn.Module):
    """Linear layer with ternary routing topology via mx.quantized_matmul.

    Forward:
        scales, biases = f(gamma)          # fold gamma into quant params
        y = quantized_matmul(norm(x), W,   # AMX-accelerated 2-bit matmul
                             scales, biases,
                             transpose=True, group_size=64, bits=2)

    The ternary {-1, 0, +1} encoding maps to 2-bit int {0, 1, 2}:
        encoded = ternary + 1

    Per-channel gamma is folded into quantized_matmul's scales/biases:
        scales = gamma           → dequant multiplier
        biases = -gamma          → shift so 0-encoded → actual 0
    Dequant: gamma * {0,1,2} + (-gamma) = {-gamma, 0, +gamma} ✓

    The weight tensor (uint32, N × K//16) represents the ternary topology.
    It is EVOLUTIONARY — mutated via tournament selection, never touched
    by the gradient optimizer.  Its gradient is always zero.

    gamma is CONTINUOUS — trained normally by Adam.  mx.quantized_matmul
    supports autograd natively; no custom VJP is needed.

    Args:
        in_features:  input dimension  (must be divisible by 16)
        out_features: output dimension
        pre_norm:     if True, apply RMSNorm before projection
    """

    # Class-level quantization constants shared with mx.quantized_matmul
    group_size: int = 64
    bits: int = 2

    def __init__(self, in_features: int, out_features: int, pre_norm: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.pre_norm = pre_norm

        if pre_norm:
            self.norm = nn.RMSNorm(in_features)

        # weight:  (out_features, in_features//16) uint32  — packed ternary topology
        # gamma:   (out_features,) float32               — trainable per-channel scale
        wq_uint32, gamma = _ternary_init(out_features, in_features)
        self.weight = wq_uint32
        self.gamma = gamma

    def _get_scales_biases(self) -> tuple[mx.array, mx.array]:
        """Compute quantized_matmul scales/biases from per-channel gamma.

        For bits=2, group_size=64 and K = in_features:
            n_groups = K // group_size
            scales shape: (out_features, n_groups)
            biases shape: (out_features, n_groups)

        The dequant formula in quantized_matmul is:
            out = scales * quant_val + biases

        With quant_val ∈ {0, 1, 2} (encoded ternary) and:
            scales = gamma   (broadcast over groups)
            biases = -gamma  (shift so 0-encoded maps to 0 in output)

        We get:  {0*γ-γ, 1*γ-γ, 2*γ-γ} = {-γ, 0, +γ} ✓
        """
        n_groups = self.in_features // self.group_size
        # gamma: (out_features,) → expand to (out_features, n_groups)
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.out_features, n_groups),
        )
        return gamma_2d, -gamma_2d

    def __call__(self, x: mx.array) -> mx.array:
        if self.pre_norm:
            x = self.norm(x)

        # Cache input statistics for gradient-informed mutation.
        # stop_gradient keeps these out of the backward graph.
        # x shape: (B, T, in_features) or (in_features,) — mean over all but last dim.
        if x.ndim >= 2:
            reduce_axes = tuple(range(x.ndim - 1))
            self._x_abs_mean = mx.stop_gradient(mx.mean(mx.abs(x), axis=reduce_axes))
            self._x_mean = mx.stop_gradient(mx.mean(x, axis=reduce_axes))
        else:
            self._x_abs_mean = mx.stop_gradient(mx.abs(x))
            self._x_mean = mx.stop_gradient(x)

        scales, biases = self._get_scales_biases()
        # stop_gradient on weight: it's evolutionary (uint32, not differentiable).
        # Without this, MLX autograd would attempt a VJP through quantized_matmul
        # w.r.t. the uint32 weight argument and raise an error.
        w = mx.stop_gradient(self.weight)
        return mx.quantized_matmul(
            x,
            w,
            scales,
            biases,
            transpose=True,
            group_size=self.group_size,
            bits=self.bits,
        )

    def ternary_stats(self) -> dict[str, float]:
        """Report ternary weight and gamma statistics."""
        w = unpack_ternary_mlx(self.weight)  # (N, K) int8
        total = w.size
        return {
            "sparsity":    float((w == 0).sum().item()) / total,
            "pos_frac":    float((w == 1).sum().item()) / total,
            "neg_frac":    float((w == -1).sum().item()) / total,
            "gamma_mean":  float(self.gamma.mean().item()),
            "gamma_std":   float(mx.sqrt(mx.var(self.gamma)).item()),
        }


# ══════════════════════════════════════════════════════════════════════
# TernaryEmbedding — packed ternary lookup table (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════


class TernaryEmbedding(nn.Module):
    """Embedding layer with ternary vectors and per-token gamma.

    Each vocabulary entry is a ternary vector {-1, 0, +1}^d_model with a
    float32 per-token scale (gamma). Lookup unpacks the selected rows on
    the fly, producing float32 output identical to standard embedding.

    Storage: vocab_size × d_model/4 bytes (packed) + vocab_size × 4 bytes (gamma)
           = vocab_size × (d_model/4 + 4) bytes
    vs float: vocab_size × d_model × 4 bytes

    For vocab=50277, d=1024: 13.1 MB packed vs 196.4 MB float (15× smaller).

    Ternary topology evolves via evolutionary mutation, not gradient descent.
    Uses the uint8 (4-per-byte) packed format and a custom VJP — embedding
    lookup is a gather, not a matmul, so quantized_matmul does not apply.
    """

    def __init__(self, vocab_size: int, d_model: int):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model

        # Initialize: random normal → quantize → pack into uint8
        w_packed, gamma = _ternary_embed_init(vocab_size, d_model)
        self.ternary_weight = w_packed   # (vocab_size, d_model//4) uint8
        self.gamma = gamma               # (vocab_size,) float32

    def __call__(self, tokens: mx.array) -> mx.array:
        """Lookup ternary embeddings for token indices.

        tokens: (*, ) int array of token indices
        Returns: (*, d_model) float32 array
        """
        return _ternary_embed_fwd(tokens, self.ternary_weight, self.gamma)

    @property
    def weight_T(self) -> mx.array:
        """Unpacked weight matrix transposed: (d_model, vocab_size) float32.

        SLOW fallback — unpacks to float32 then does regular matmul.
        Prefer output_proj() for the tied output projection.
        """
        w = unpack_ternary(self.ternary_weight, self.d_model).astype(mx.float32)
        w = w * mx.expand_dims(self.gamma, axis=-1)
        return w.T  # (d_model, vocab_size)

    def output_proj(self, x: mx.array) -> mx.array:
        """Tied output projection via quantized_matmul (fast, ternary).

        x: (B, L, d_model) → logits (B, L, vocab_size)

        Repacks the uint8 embedding weights to uint32 format for
        quantized_matmul. The repacked weights are cached and invalidated
        when the topology mutates (detected via shape/id change).
        """
        # Repack uint8 → uint32 if needed (cache for speed)
        if (not hasattr(self, '_qm_cache_id') or
                self._qm_cache_id != id(self.ternary_weight)):
            # Unpack uint8 → int8 → repack uint32
            w_int8 = unpack_ternary(self.ternary_weight, self.d_model)  # (V, d)
            self._qm_weight = pack_ternary_mlx(w_int8)  # (V, d//16) uint32
            self._qm_cache_id = id(self.ternary_weight)

        # Build scales/biases from gamma (same as TernaryLinear)
        group_size = 64
        n_groups = self.d_model // group_size
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.vocab_size, n_groups),
        )
        scales = gamma_2d
        biases = -gamma_2d

        w = mx.stop_gradient(self._qm_weight)
        return mx.quantized_matmul(
            x, w, scales, biases,
            transpose=True, group_size=group_size, bits=2,
        )

    @property
    def in_features(self):
        """For compatibility with _walk_ternary_modules."""
        return self.d_model

    @property
    def out_features(self):
        return self.vocab_size


@mx.custom_function
def _ternary_embed_fwd(
    tokens: mx.array,
    w_packed: mx.array,
    gamma: mx.array,
) -> mx.array:
    """Forward: unpack selected rows from packed ternary embedding, scale by gamma.

    tokens:   (*,) int indices
    w_packed: (vocab_size, d_model//4) uint8
    gamma:    (vocab_size,) float32

    Returns:  (*, d_model) float32
    """
    d_model = w_packed.shape[1] * 4
    flat_tokens = tokens.reshape(-1)
    packed_rows = w_packed[flat_tokens]      # (N, d_model//4) uint8
    gamma_rows = gamma[flat_tokens]          # (N,) float32

    # Unpack: uint8 → float32 {-1, 0, +1}
    w0 = ((packed_rows >> 6) & 0x3).astype(mx.float32) - 1.0
    w1 = ((packed_rows >> 4) & 0x3).astype(mx.float32) - 1.0
    w2 = ((packed_rows >> 2) & 0x3).astype(mx.float32) - 1.0
    w3 = (packed_rows & 0x3).astype(mx.float32) - 1.0
    # Interleave: columns {4k, 4k+1, 4k+2, 4k+3}
    N = flat_tokens.shape[0]
    unpacked = mx.stack([w0, w1, w2, w3], axis=-1).reshape(N, d_model)

    # Scale by per-token gamma
    result = unpacked * mx.expand_dims(gamma_rows, axis=-1)
    return result.reshape(*tokens.shape, d_model)


@_ternary_embed_fwd.vjp
def _ternary_embed_vjp(primals, cotangent, output):
    """Backward through ternary embedding lookup.

    ∂L/∂tokens:   zeros (integer indices, not differentiable)
    ∂L/∂w_packed: zeros (topology evolves via mutation, not gradient)
    ∂L/∂gamma:    per-token grad, scattered back to (vocab_size,)
    """
    tokens, w_packed, gamma = primals
    grad_out = cotangent  # (*, d_model)
    d_model = w_packed.shape[1] * 4

    flat_tokens = tokens.reshape(-1)
    N = flat_tokens.shape[0]
    grad_flat = grad_out.reshape(N, d_model)

    # ∂L/∂gamma: Σ_d (grad_out[n,d] * unpacked[n,d])
    packed_rows = w_packed[flat_tokens]
    w0 = ((packed_rows >> 6) & 0x3).astype(mx.float32) - 1.0
    w1 = ((packed_rows >> 4) & 0x3).astype(mx.float32) - 1.0
    w2 = ((packed_rows >> 2) & 0x3).astype(mx.float32) - 1.0
    w3 = (packed_rows & 0x3).astype(mx.float32) - 1.0
    unpacked = mx.stack([w0, w1, w2, w3], axis=-1).reshape(N, d_model)

    grad_gamma_per_token = mx.sum(grad_flat * unpacked, axis=-1)  # (N,)

    # Scatter gamma grads back to (vocab_size,)
    grad_gamma = mx.zeros((gamma.shape[0],), dtype=mx.float32)
    grad_gamma = grad_gamma.at[flat_tokens].add(grad_gamma_per_token)

    # ∂L/∂w_packed: zeros
    grad_w_packed = mx.zeros_like(w_packed).astype(mx.float32)

    # No gradient for tokens
    grad_tokens = mx.zeros(tokens.shape, dtype=mx.float32)

    return grad_tokens, grad_w_packed, grad_gamma


# ══════════════════════════════════════════════════════════════════════
# Ternary module utilities
# ══════════════════════════════════════════════════════════════════════


def _walk_ternary_modules(model: nn.Module):
    """Yield (path, module) for all TernaryLinear and TernaryEmbedding in model."""
    for path, module in model.named_modules():
        if isinstance(module, (TernaryLinear, TernaryEmbedding)):
            yield path, module


def zero_ternary_grads(model: nn.Module, grads: dict) -> dict:
    """Zero out packed topology weight gradients in the grad pytree.

    TernaryLinear.weight (uint32) is never touched by the optimizer —
    its topology evolves via mutation.  The grad returned by
    quantized_matmul autograd for the weight argument is zeros already,
    but this function enforces that guarantee and prevents any accidental
    optimizer state accumulation.

    TernaryEmbedding.ternary_weight (uint8) is similarly evolutionary.

    gamma gradients are left untouched — Adam updates gamma normally.
    """
    # Collect packed weight keys for all ternary modules
    weight_keys: dict[str, tuple] = {}
    for path, module in _walk_ternary_modules(model):
        if isinstance(module, TernaryLinear):
            key = f"{path}.weight" if path else "weight"
            weight_keys[key] = module.weight.shape
        elif isinstance(module, TernaryEmbedding):
            key = f"{path}.ternary_weight" if path else "ternary_weight"
            weight_keys[key] = module.ternary_weight.shape

    def _zero(path_prefix: str, tree):
        if isinstance(tree, dict):
            return {
                k: _zero(f"{path_prefix}.{k}" if path_prefix else k, v)
                for k, v in tree.items()
            }
        elif isinstance(tree, list):
            return [
                _zero(f"{path_prefix}.{i}" if path_prefix else str(i), v)
                for i, v in enumerate(tree)
            ]
        elif isinstance(tree, mx.array) and path_prefix in weight_keys:
            shape = weight_keys[path_prefix]
            return mx.zeros(shape, dtype=tree.dtype)
        return tree

    return _zero("", grads)


def freeze_ternary_weights(model: nn.Module) -> int:
    """Freeze all packed ternary weight parameters so the optimizer ignores them.

    This is the correct way to protect packed uint32/uint8 topology weights
    from AdamW weight decay corruption.  Without freezing, AdamW applies
    weight decay (w *= 1 - lr*wd) which casts packed uint32 to float32,
    destroying the 2-bit field packing.

    Freezing removes these parameters from model.trainable_parameters(),
    so nn.value_and_grad won't differentiate through them and the optimizer
    won't apply weight decay or momentum updates.

    Evolutionary mutations still work via direct assignment (mod.weight = ...).

    Must be called:
      - After model creation
      - After model.load_weights() (which may reset freeze state)

    Returns:
        Number of modules frozen.
    """
    n_frozen = 0
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            mod.freeze(keys=["weight"])
            n_frozen += 1
        elif isinstance(mod, TernaryEmbedding):
            mod.freeze(keys=["ternary_weight"])
            n_frozen += 1
    return n_frozen


def restore_ternary(model: nn.Module) -> None:
    """Assert ternary weights have correct dtype — detect corruption early.

    With freeze_ternary_weights() applied, the optimizer should never touch
    packed weights.  This function raises immediately if it detects dtype
    drift rather than silently corrupting the packing by clipping.

    The old implementation clipped packed uint32 values to [0, 3] which
    DESTROYED the 2-bit field packing (15 of 16 slots collapsed to -1).
    That bug is now prevented by freezing, and this function is the alarm.
    """
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            if mod.weight.dtype != mx.uint32:
                raise RuntimeError(
                    f"TERNARY CORRUPTION: {path}.weight dtype is "
                    f"{mod.weight.dtype}, expected uint32. "
                    f"Was freeze_ternary_weights() called after model init "
                    f"and after load_weights()?"
                )
        elif isinstance(mod, TernaryEmbedding):
            if mod.ternary_weight.dtype != mx.uint8:
                raise RuntimeError(
                    f"TERNARY CORRUPTION: {path}.ternary_weight dtype is "
                    f"{mod.ternary_weight.dtype}, expected uint8. "
                    f"Was freeze_ternary_weights() called after model init "
                    f"and after load_weights()?"
                )


# ══════════════════════════════════════════════════════════════════════
# Evolutionary topology mutation
# ══════════════════════════════════════════════════════════════════════
#
# Ternary topology = genome (N loci × 3 alleles {-1, 0, +1}).
# Evolution via mutation + tournament selection, not gradient descent.
#
# The relational loss r ∈ [0, 1] forms a cone-shaped restriction on
# the viable mutation space:
#
#   r ≈ 1.0  ████████████  wide cone — explore topology freely
#   r ≈ 0.5  ██████        moderate — refine structure
#   r ≈ 0.1  ██            narrow — surgical mutations only
#   r < 0.05 ·             frozen — topology crystallized
#
# Champion never degrades: mutations that increase loss are rejected.


def count_ternary_weights(model: nn.Module) -> int:
    """Count total logical ternary weight positions across all modules."""
    total = 0
    for _, mod in _walk_ternary_modules(model):
        total += mod.out_features * mod.in_features
    return total


def mutation_cone(r_ema: float, total_weights: int, base_pct: float = 0.001) -> int:
    """Compute mutation budget from relational loss via quadratic cone.

    Used by Dolma phase to protect BIOS-burned circuits. NOT used during BIOS.

    Args:
        r_ema:          relational loss EMA ∈ [0, 1]. 1.0 = random, 0.0 = converged.
        total_weights:  total ternary weight count
        base_pct:       maximum mutation rate at the cone's widest point

    Returns:
        Number of weights to mutate this generation.
    """
    if r_ema < 0.05:
        return 0  # converged — topology frozen
    # Quadratic cone: budget ∝ r²; full budget at r ≥ 0.6
    scale = min(1.0, (r_ema / 0.6) ** 2)
    return max(1, int(total_weights * base_pct * scale))


def bios_mutation_budget(
    step: int,
    total_steps: int,
    total_weights: int,
    base_pct: float = 0.005,
) -> int:
    """Compute mutation budget for BIOS phase: high constant then late decay.

    During BIOS burn-in, topology exploration should NOT be gated by loss.
    Gamma (continuous) learns surface statistics fast, driving loss down and
    starving topology evolution via the cone. Instead:

      First 80%: full budget — explore topology freely, find circuits.
      Last 20%:  linear decay to 10% — crystallize what worked.

    Args:
        step:          current training step
        total_steps:   total BIOS training steps
        total_weights: total ternary weight count
        base_pct:      mutation rate during exploration phase (default 0.5%)

    Returns:
        Number of weights to mutate this generation.
    """
    decay_start = int(total_steps * 0.8)
    if step <= decay_start:
        scale = 1.0
    else:
        # Linear decay from 1.0 → 0.1 over the last 20%
        progress = (step - decay_start) / max(1, total_steps - decay_start)
        scale = 1.0 - 0.9 * progress
    return max(1, int(total_weights * base_pct * scale))


def save_topology(model: nn.Module) -> list[tuple[str, mx.array]]:
    """Snapshot all ternary weight topologies for champion preservation.

    Returns a list of (path, weight_copy) pairs.
    TernaryLinear:  copies mod.weight  (uint32)
    TernaryEmbedding: copies mod.ternary_weight (uint8)
    """
    snapshot = []
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            snapshot.append((path, mx.array(mod.weight)))
        else:
            snapshot.append((path, mx.array(mod.ternary_weight)))
    mx.eval(*[w for _, w in snapshot])
    return snapshot


def load_topology(model: nn.Module, snapshot: list[tuple[str, mx.array]]) -> None:
    """Restore ternary weights from a topology snapshot.

    Used to revert failed mutations (champion preservation).
    """
    mod_map = {path: mod for path, mod in _walk_ternary_modules(model)}
    restored = []
    for path, saved_weight in snapshot:
        if path not in mod_map:
            continue
        mod = mod_map[path]
        if isinstance(mod, TernaryLinear):
            mod.weight = saved_weight
        else:
            mod.ternary_weight = saved_weight
        restored.append(saved_weight)
    if restored:
        mx.eval(*restored)


def mutate_topology(
    model: nn.Module,
    budget: int,
    rng: Any,
    depth_weights: dict[str, float] | None = None,
    sign_flip_rate: float = 0.2,
    row_importance: dict[str, Any] | None = None,
    col_importance: dict[str, Any] | None = None,
    grad_direction: dict[str, Any] | None = None,
    guided_fraction: float = 0.7,
) -> tuple[int, dict[str, set[int]]]:
    """Apply gradient-informed mutations to the ternary topology.

    Distributes `budget` mutations across ternary modules, weighted by
    depth priority.  Within each module, positions are sampled using a
    mix of importance-weighted and uniform random:

      70% (guided_fraction): rows sampled ∝ |∂L/∂γ| (gamma gradient EMA)
                              cols sampled ∝ mean(|x|) (input activation EMA)
      30% (1-guided_fraction): uniform random (exploration, prevents stagnation)

    When gradient direction info is available, activating mutations (0→±1)
    prefer the sign indicated by the gradient.

    Args:
        model:            the model to mutate IN PLACE
        budget:           total number of logical weights to flip
        rng:              numpy RandomState for reproducible mutations
        depth_weights:    module path prefix → float priority weight
        sign_flip_rate:   fraction of non-zero mutations that flip sign
        row_importance:   {module_path: np.array (out_features,)} from |∂L/∂γ| EMA
        col_importance:   {module_path: np.array (in_features,)} from mean(|x|) EMA
        grad_direction:   {module_path: np.array (out_features,)} sign of ∂L/∂γ EMA
        guided_fraction:  fraction of mutations that are importance-weighted (rest uniform)

    Returns:
        (n_mutated, mutation_map) — total count and dict mapping
        module_path → set of mutated row indices. The mutation map
        enables surgical Adam decay: only gamma entries for rows that
        actually changed need their optimizer state reset.
    """
    import numpy as np

    modules = list(_walk_ternary_modules(model))
    if not modules or budget <= 0:
        return 0, {}

    # Compute effective weight for each module
    sizes = [mod.out_features * mod.in_features for _, mod in modules]

    if depth_weights is not None:
        effective = []
        for (path, _), n_weights in zip(modules, sizes):
            best_weight = 1.0
            best_len = 0
            for prefix, w in depth_weights.items():
                if path.startswith(prefix) and len(prefix) > best_len:
                    best_weight = w
                    best_len = len(prefix)
            effective.append(n_weights * best_weight)
    else:
        effective = [float(s) for s in sizes]

    total_effective = sum(effective)

    total_mutated = 0
    mutated_arrays = []
    mutation_map: dict[str, set[int]] = {}

    for (path, mod), n_weights, eff in zip(modules, sizes, effective):
        mod_budget = max(0, round(budget * eff / total_effective))
        if mod_budget == 0:
            continue
        mod_budget = min(mod_budget, n_weights)

        # Get importance maps for this module (if available)
        row_imp = row_importance.get(path) if row_importance else None
        col_imp = col_importance.get(path) if col_importance else None
        grad_dir = grad_direction.get(path) if grad_direction else None

        if isinstance(mod, TernaryLinear):
            n, rows = _mutate_linear(
                mod, mod_budget, rng, np, mutated_arrays, sign_flip_rate,
                row_imp, col_imp, grad_dir, guided_fraction,
            )
            total_mutated += n
            mutation_map[path] = rows
        else:
            n, rows = _mutate_embedding(
                mod, mod_budget, rng, np, mutated_arrays, sign_flip_rate,
            )
            total_mutated += n
            mutation_map[path] = rows

    if mutated_arrays:
        mx.eval(*mutated_arrays)

    return total_mutated, mutation_map


def _importance_sample_indices(
    N: int,
    K: int,
    budget: int,
    rng: Any,
    np: Any,
    row_imp: Any | None,
    col_imp: Any | None,
    guided_fraction: float,
) -> Any:
    """Sample (row, col) mutation positions using importance-weighted + uniform mix.

    guided_fraction of positions are sampled proportional to:
        P(i,j) ∝ row_importance[i] × col_importance[j]
    The rest are uniform random (exploration).

    Returns flat logical indices (row * K + col).
    """
    n_guided = int(budget * guided_fraction)
    n_uniform = budget - n_guided

    indices_parts = []

    # ── Importance-weighted positions ──
    if n_guided > 0 and (row_imp is not None or col_imp is not None):
        # Row probabilities from |∂L/∂γ| importance
        if row_imp is not None and len(row_imp) == N:
            row_p = np.asarray(row_imp, dtype=np.float64)
            row_p = np.where(np.isfinite(row_p), row_p, 0.0)  # NaN/Inf → 0
            row_p = np.maximum(row_p, 1e-8)  # floor to prevent zero-prob rows
            row_p /= row_p.sum()
        else:
            row_p = None  # uniform

        # Column probabilities from mean(|x|) importance
        if col_imp is not None and len(col_imp) == K:
            col_p = np.asarray(col_imp, dtype=np.float64)
            col_p = np.where(np.isfinite(col_p), col_p, 0.0)  # NaN/Inf → 0
            col_p = np.maximum(col_p, 1e-8)
            col_p /= col_p.sum()
        else:
            col_p = None  # uniform

        rows = rng.choice(N, size=n_guided, p=row_p)
        cols = rng.choice(K, size=n_guided, p=col_p)
        indices_parts.append(rows * K + cols)

    else:
        # No importance info — fall back to all uniform
        n_uniform += n_guided

    # ── Uniform random positions (exploration) ──
    if n_uniform > 0:
        indices_parts.append(rng.randint(0, N * K, size=n_uniform))

    return np.concatenate(indices_parts) if len(indices_parts) > 1 else indices_parts[0]


def _mutate_linear(
    mod: "TernaryLinear",
    mod_budget: int,
    rng: Any,
    np: Any,
    mutated_arrays: list,
    sign_flip_rate: float = 0.2,
    row_imp: Any | None = None,
    col_imp: Any | None = None,
    grad_dir: Any | None = None,
    guided_fraction: float = 0.7,
) -> tuple[int, set[int]]:
    """Mutate TernaryLinear.weight with gradient-informed position selection.

    Position selection: importance-weighted sampling from |∂L/∂γ| (rows)
    and mean(|x|) (columns), mixed with uniform exploration.

    Direction for 0→±1 activations: when gradient direction is available,
    prefer the sign that the gradient indicates will reduce loss.

    Mutation rules:
        0 → ±1        (activate — gradient-biased if direction available)
       ±1 → 0         (deactivate, probability 1-sign_flip_rate)
       ±1 → ∓1        (sign flip, probability sign_flip_rate)

    Returns:
        (n_mutated, mutated_rows) — count and set of affected row indices.
        mutated_rows maps to gamma indices for surgical Adam decay.
    """
    N = mod.out_features
    K = mod.in_features

    packed_np = np.array(mod.weight)  # (N, K//16) uint32
    flat_packed = packed_np.reshape(-1)

    # Sample positions: importance-weighted + uniform mix
    indices = _importance_sample_indices(
        N, K, mod_budget, rng, np, row_imp, col_imp, guided_fraction,
    )

    # Map logical index → packed coordinates
    rows = indices // K
    cols = indices % K
    uint32_idx = rows * (K // 16) + cols // 16
    slot = cols % 16
    shifts = (slot * 2).astype(np.uint32)

    # Read current values
    current_encoded = ((flat_packed[uint32_idx] >> shifts) & np.uint32(0x3))
    current_val = current_encoded.astype(np.int8) - 1  # {-1,0,+1}

    # Apply mutations
    new_val = np.copy(current_val)

    # Non-zero positions: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero positions: activate with gradient-directed sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        if grad_dir is not None and len(grad_dir) == N:
            # Use gradient direction: sign(∂L/∂γ_i) for row i
            # Positive grad → gamma wants to grow → prefer +1 (increases magnitude)
            # Negative grad → gamma wants to shrink → prefer -1
            # Apply as soft bias: 80% follow gradient, 20% random
            zero_rows = rows[zero_mask]
            gd = np.asarray(grad_dir, dtype=np.float32)
            row_signs = np.sign(gd[zero_rows])  # {-1, 0, +1}
            # Where gradient is ~0 or unknown, fall back to random
            random_signs = rng.choice([-1, 1], size=n_zeros).astype(np.int8)
            follow_grad = rng.random(size=n_zeros) < 0.8
            has_direction = row_signs != 0
            use_grad = follow_grad & has_direction
            new_val[zero_mask] = np.where(
                use_grad, row_signs.astype(np.int8), random_signs,
            )
        else:
            new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    new_encoded = (new_val.astype(np.int32) + 1).astype(np.uint32)

    # Count actual flips: positions where the value genuinely changed.
    # Budget ≠ flips because:
    #   - indices sampled with replacement → duplicates (last write wins)
    #   - some mutations are no-ops at the packed level when duplicates
    #     overwrite each other
    # We compare against the original packed values at unique positions.
    actual_flips = int(np.sum(new_val != current_val))

    # Write back
    clear_mask = ~(np.uint32(0x3) << shifts)
    flat_packed[uint32_idx] = (flat_packed[uint32_idx] & clear_mask) | (new_encoded << shifts)

    mod.weight = mx.array(flat_packed.reshape(N, K // 16))
    mutated_arrays.append(mod.weight)

    # Track which rows (output channels) were touched — for surgical Adam decay
    # Only count rows where a flip actually happened
    actually_changed = new_val != current_val
    mutated_rows = set(int(r) for r in np.unique(rows[actually_changed])) if actual_flips > 0 else set()
    return actual_flips, mutated_rows


def _mutate_embedding(
    mod: "TernaryEmbedding",
    mod_budget: int,
    rng: Any,
    np: Any,
    mutated_arrays: list,
    sign_flip_rate: float = 0.2,
) -> tuple[int, set[int]]:
    """Mutate TernaryEmbedding.ternary_weight (uint8, 4-per-byte big-endian format).

    Encoding: {0b00→-1, 0b01→0, 0b10→+1}.
    Bit positions: bits {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}.

    Same mutation rules as _mutate_linear: deactivate or sign-flip for non-zero,
    random activation for zero.
    """
    vocab_size = mod.vocab_size
    d_model = mod.d_model
    n_weights = vocab_size * d_model

    packed_np = np.array(mod.ternary_weight)  # (vocab_size, d_model//4) uint8
    N, K4 = packed_np.shape
    flat_packed = packed_np.reshape(-1)

    indices = rng.randint(0, n_weights, size=mod_budget)

    # Map logical index → (byte_index, bit_position)
    byte_idx = indices // 4
    pos_in_byte = indices % 4
    shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

    # Read current 2-bit values
    current_encoded = (flat_packed[byte_idx] >> shifts) & np.uint8(0x3)  # {0,1,2}
    current_val = current_encoded.astype(np.int8) - 1                     # {-1,0,+1}

    # Apply mutations
    new_val = np.copy(current_val)

    # Non-zero: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero: activate with random sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    new_encoded = (new_val + 1).astype(np.uint8)

    # Actual flips (same logic as _mutate_linear)
    actual_flips = int(np.sum(new_val != current_val))

    # Write back
    clear_masks = ~(np.uint8(0x3) << shifts)
    flat_packed[byte_idx] = (flat_packed[byte_idx] & clear_masks) | (new_encoded << shifts)

    mod.ternary_weight = mx.array(flat_packed.reshape(N, K4))
    mutated_arrays.append(mod.ternary_weight)

    # Track mutated rows (vocab entries) — embeddings don't have gamma,
    # but tracked for completeness and potential future use
    actually_changed = new_val != current_val
    rows = indices // (K4 * 4)
    mutated_rows = set(int(r) for r in np.unique(rows[actually_changed])) if actual_flips > 0 else set()
    return actual_flips, mutated_rows


# ══════════════════════════════════════════════════════════════════════
# Consensus-based mutation: propose → vote → apply only agreed flips
# ══════════════════════════════════════════════════════════════════════
#
# Instead of tournament selection (best of 4 independent throws),
# consensus requires ≥3 of 4 strategies to independently agree on
# the same flip at the same position. This yields the fewest flips
# with the highest confidence — each accepted flip has independent
# evidence from multiple sampling strategies.
#
# Flow:
#   1. propose_mutations()  — each strategy samples positions and
#      computes proposed values WITHOUT modifying the model
#   2. find_consensus()     — positions where ≥3 strategies agree
#   3. apply_consensus()    — apply only the consensus flips


def _propose_linear(
    mod: "TernaryLinear",
    mod_budget: int,
    rng: Any,
    np: Any,
    sign_flip_rate: float = 0.2,
    row_imp: Any | None = None,
    col_imp: Any | None = None,
    grad_dir: Any | None = None,
    guided_fraction: float = 0.7,
) -> dict[int, int]:
    """Propose mutations for a TernaryLinear without modifying it.

    Same sampling and mutation logic as _mutate_linear, but returns
    a dict of {flat_logical_index: proposed_ternary_value} instead
    of writing to the packed array.

    Only includes positions where the proposal differs from current.
    For duplicate indices (sampled with replacement), last proposal wins.
    """
    N = mod.out_features
    K = mod.in_features

    packed_np = np.array(mod.weight)  # (N, K//16) uint32
    flat_packed = packed_np.reshape(-1)

    indices = _importance_sample_indices(
        N, K, mod_budget, rng, np, row_imp, col_imp, guided_fraction,
    )

    rows = indices // K
    cols = indices % K
    uint32_idx = rows * (K // 16) + cols // 16
    slot = cols % 16
    shifts = (slot * 2).astype(np.uint32)

    current_encoded = ((flat_packed[uint32_idx] >> shifts) & np.uint32(0x3))
    current_val = current_encoded.astype(np.int8) - 1

    new_val = np.copy(current_val)

    # Non-zero: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero: activate with gradient-directed sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        if grad_dir is not None and len(grad_dir) == N:
            zero_rows = rows[zero_mask]
            gd = np.asarray(grad_dir, dtype=np.float32)
            row_signs = np.sign(gd[zero_rows])
            random_signs = rng.choice([-1, 1], size=n_zeros).astype(np.int8)
            follow_grad = rng.random(size=n_zeros) < 0.8
            has_direction = row_signs != 0
            use_grad = follow_grad & has_direction
            new_val[zero_mask] = np.where(
                use_grad, row_signs.astype(np.int8), random_signs,
            )
        else:
            new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    # Build proposals dict: only positions that actually change
    # For duplicates, iterate in order so last write wins (matching _mutate_linear)
    proposals = {}
    for i in range(len(indices)):
        if new_val[i] != current_val[i]:
            proposals[int(indices[i])] = int(new_val[i])

    return proposals


def _propose_embedding(
    mod: "TernaryEmbedding",
    mod_budget: int,
    rng: Any,
    np: Any,
    sign_flip_rate: float = 0.2,
) -> dict[int, int]:
    """Propose mutations for a TernaryEmbedding without modifying it."""
    vocab_size = mod.vocab_size
    d_model = mod.d_model
    n_weights = vocab_size * d_model

    packed_np = np.array(mod.ternary_weight)
    flat_packed = packed_np.reshape(-1)

    indices = rng.randint(0, n_weights, size=mod_budget)

    byte_idx = indices // 4
    pos_in_byte = indices % 4
    shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

    current_encoded = (flat_packed[byte_idx] >> shifts) & np.uint8(0x3)
    current_val = current_encoded.astype(np.int8) - 1

    new_val = np.copy(current_val)

    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    proposals = {}
    for i in range(len(indices)):
        if new_val[i] != current_val[i]:
            proposals[int(indices[i])] = int(new_val[i])

    return proposals


def propose_mutations(
    model: nn.Module,
    budget: int,
    rng: Any,
    sign_flip_rate: float = 0.2,
    row_importance: dict[str, Any] | None = None,
    col_importance: dict[str, Any] | None = None,
    grad_direction: dict[str, Any] | None = None,
    guided_fraction: float = 0.7,
    depth_weights: dict[str, float] | None = None,
) -> dict[str, dict[int, int]]:
    """Propose mutations for all ternary modules without applying them.

    Returns dict mapping module_path → {flat_index: proposed_value}.
    Same budget distribution logic as mutate_topology.
    """
    import numpy as np

    modules = list(_walk_ternary_modules(model))
    if not modules or budget <= 0:
        return {}

    sizes = [mod.out_features * mod.in_features for _, mod in modules]

    if depth_weights is not None:
        effective = []
        for (path, _), n_weights in zip(modules, sizes):
            best_weight = 1.0
            best_len = 0
            for prefix, w in depth_weights.items():
                if path.startswith(prefix) and len(prefix) > best_len:
                    best_weight = w
                    best_len = len(prefix)
            effective.append(n_weights * best_weight)
    else:
        effective = [float(s) for s in sizes]

    total_effective = sum(effective)
    all_proposals = {}

    for (path, mod), n_weights, eff in zip(modules, sizes, effective):
        mod_budget = max(0, round(budget * eff / total_effective))
        if mod_budget == 0:
            continue
        mod_budget = min(mod_budget, n_weights)

        row_imp = row_importance.get(path) if row_importance else None
        col_imp = col_importance.get(path) if col_importance else None
        grad_dir = grad_direction.get(path) if grad_direction else None

        if isinstance(mod, TernaryLinear):
            all_proposals[path] = _propose_linear(
                mod, mod_budget, rng, np, sign_flip_rate,
                row_imp, col_imp, grad_dir, guided_fraction,
            )
        else:
            all_proposals[path] = _propose_embedding(
                mod, mod_budget, rng, np, sign_flip_rate,
            )

    return all_proposals


def find_consensus(
    proposals_list: list[dict[str, dict[int, int]]],
    threshold: int = 3,
    vote_weights: list[int] | None = None,
) -> tuple[dict[str, dict[int, int]], dict]:
    """Find consensus mutations: positions where weighted votes ≥ threshold.

    Args:
        proposals_list: list of proposals from each strategy (from propose_mutations)
        threshold:      minimum weighted vote count to accept (default: 3)
        vote_weights:   per-strategy vote multiplier (default: all 1).
                        e.g. [1,1,1,1,2] gives strategy 4 two votes.
                        S4 intelligence gets 2 votes — it only needs
                        one ally for consensus instead of two.

    Returns:
        (consensus, stats) where:
          consensus: dict[module_path → {flat_index: agreed_value}]
          stats: dict with diagnostic counts
    """
    from collections import defaultdict

    if vote_weights is None:
        vote_weights = [1] * len(proposals_list)

    # Collect all module paths
    all_paths = set()
    for prop in proposals_list:
        all_paths.update(prop.keys())

    consensus = {}
    total_positions_seen = 0
    total_positions_voted = 0
    total_consensus = 0

    for path in all_paths:
        # Gather weighted votes: for each position, collect
        # (proposed_value, weight) from each strategy
        votes = defaultdict(list)
        for si, prop in enumerate(proposals_list):
            w = vote_weights[si]
            if path in prop:
                for idx, val in prop[path].items():
                    votes[idx].append((val, w))

        total_positions_seen += len(votes)

        # Find consensus: weighted votes for same value ≥ threshold
        path_consensus = {}
        for idx, vote_list in votes.items():
            total_weight = sum(w for _, w in vote_list)
            if total_weight >= threshold:
                total_positions_voted += 1
                # Count weighted votes per value
                value_weights: dict[int, int] = {}
                for val, w in vote_list:
                    value_weights[val] = value_weights.get(val, 0) + w
                best_val = max(value_weights, key=value_weights.get)
                best_weight = value_weights[best_val]
                if best_weight >= threshold:
                    path_consensus[idx] = best_val
                    total_consensus += 1

        if path_consensus:
            consensus[path] = path_consensus

    stats = {
        "positions_sampled": total_positions_seen,
        "positions_with_enough_votes": total_positions_voted,
        "consensus_flips": total_consensus,
        "n_strategies": len(proposals_list),
        "threshold": threshold,
        "vote_weights": vote_weights,
    }

    return consensus, stats


def apply_consensus(
    model: nn.Module,
    consensus: dict[str, dict[int, int]],
) -> tuple[int, dict[str, set[int]]]:
    """Apply consensus mutations to the model.

    Args:
        consensus: dict[module_path → {flat_logical_index: new_ternary_value}]

    Returns:
        (n_applied, mutation_map) — count and per-module affected rows
        for surgical Adam decay.
    """
    import numpy as np

    mod_map = {path: mod for path, mod in _walk_ternary_modules(model)}
    total_applied = 0
    mutation_map: dict[str, set[int]] = {}
    mutated_arrays = []

    for path, flips in consensus.items():
        if path not in mod_map or not flips:
            continue

        mod = mod_map[path]

        if isinstance(mod, TernaryLinear):
            N = mod.out_features
            K = mod.in_features
            packed_np = np.array(mod.weight)
            flat_packed = packed_np.reshape(-1)

            indices = np.array(list(flips.keys()), dtype=np.int64)
            new_vals = np.array(list(flips.values()), dtype=np.int8)

            rows = indices // K
            cols = indices % K
            uint32_idx = rows * (K // 16) + cols // 16
            slot = cols % 16
            shifts = (slot * 2).astype(np.uint32)

            new_encoded = (new_vals.astype(np.int32) + 1).astype(np.uint32)
            clear_mask = ~(np.uint32(0x3) << shifts)
            flat_packed[uint32_idx] = (flat_packed[uint32_idx] & clear_mask) | (new_encoded << shifts)

            mod.weight = mx.array(flat_packed.reshape(N, K // 16))
            mutated_arrays.append(mod.weight)
            mutation_map[path] = set(int(r) for r in np.unique(rows))
            total_applied += len(flips)

        elif isinstance(mod, TernaryEmbedding):
            packed_np = np.array(mod.ternary_weight)
            N, K4 = packed_np.shape
            flat_packed = packed_np.reshape(-1)

            indices = np.array(list(flips.keys()), dtype=np.int64)
            new_vals = np.array(list(flips.values()), dtype=np.int8)

            byte_idx = indices // 4
            pos_in_byte = indices % 4
            shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

            new_encoded = (new_vals + 1).astype(np.uint8)
            clear_masks = ~(np.uint8(0x3) << shifts)
            flat_packed[byte_idx] = (flat_packed[byte_idx] & clear_masks) | (new_encoded << shifts)

            mod.ternary_weight = mx.array(flat_packed.reshape(N, K4))
            mutated_arrays.append(mod.ternary_weight)
            emb_rows = indices // (K4 * 4)
            mutation_map[path] = set(int(r) for r in np.unique(emb_rows))
            total_applied += len(flips)

    if mutated_arrays:
        mx.eval(*mutated_arrays)

    return total_applied, mutation_map


# ══════════════════════════════════════════════════════════════════════
# Checkpoint stubs
# ══════════════════════════════════════════════════════════════════════


def save_ternary_state(model: nn.Module, path: str) -> None:
    """No-op — ternary weights save with model.npz via tree_flatten(model.parameters()).

    In the evolutionary regime there are no accumulators or cooldowns to
    persist beyond the packed weights themselves.
    """
    pass


def load_ternary_state(model: nn.Module, path: str) -> None:
    """No-op — ternary weights load with model.load_weights().

    Kept for protocol compatibility.
    """
    pass


# ══════════════════════════════════════════════════════════════════════
# Gradient-directed etching — "laser hologram etcher"
# ══════════════════════════════════════════════════════════════════════
#
# The holographic plate in production LLMs is a structured ternary sign
# topology. The current consensus evolution can't shape it (cos=1.000
# frozen across 4K steps — see session 099 hologram probe).
#
# The laser etcher replaces random mutation with gradient-directed
# sign shaping:
#
#   1. HEAT ACCUMULATION (every step, cheap):
#      Row heat: EMA of |∂L/∂γ[i]| — gradient pressure per output channel
#      Col heat: EMA of |x_mean[j]| — input activation per feature
#      Row dir:  EMA of ∂L/∂γ[i]   — signed gradient direction
#      Col dir:  EMA of x_mean[j]   — signed activation direction
#
#   2. SIGNAL PLANE UPDATE (every N steps):
#      3 ternary signal planes per weight matrix, at heat thresholds
#      (weak/medium/strong). Each plane gets a direction vote:
#        direction[i,j] = sign(row_dir[i] × col_dir[j])
#      Written only at positions above the plane's heat threshold.
#
#   3. ETCH CHECK (every M steps):
#      When all 3 signal planes agree on a direction AND that direction
#      disagrees with the current weight sign → flip the weight sign.
#      Reset signal planes at etched positions.
#
# Properties:
#   - Self-terminating: heat drops to zero when signs align with gradient
#   - Re-etchable: if strategy changes, new gradient direction accumulates
#   - Memory efficient: 3 signal planes (ternary) + 4 float vectors per module
#   - Compute efficient: all ternary operations, AMX-compatible
#
# Metaphor:
#   γ gradient     = laser energy accumulating at each point
#   heat threshold = temperature where material changes state
#   consensus      = sustained energy from all intensity levels
#   settling time  = plate cooling between passes


class EtchState:
    """Per-module state for gradient-directed etching.

    Stores:
      - 4 float EMA vectors: row_heat, col_heat, row_dir, col_dir
      - 3 packed ternary signal planes (same uint32 format as TernaryLinear)
      - Bookkeeping: steps accumulated, total flips
    """

    def __init__(self, out_features: int, in_features: int):
        import numpy as np
        self.out_features = out_features
        self.in_features = in_features

        # Float EMAs — gradient heat and direction
        self.row_heat = np.zeros(out_features, dtype=np.float32)
        self.col_heat = np.zeros(in_features, dtype=np.float32)
        self.row_dir = np.zeros(out_features, dtype=np.float32)
        self.col_dir = np.zeros(in_features, dtype=np.float32)

        # 3 signal planes: packed uint32, initialized to all-zero (neutral)
        # Same format as TernaryLinear.weight: (out_features, in_features//16)
        # Encoding: -1→0, 0→1, +1→2 (ternary+1). All-zero packed = all-neutral.
        n_packed = in_features // 16
        # All-neutral = every 2-bit field is 0b01 (=1, decodes to 0)
        # Pack 16 copies of 0b01: each at position 2*i
        neutral_word = sum(1 << (2 * i) for i in range(16))
        self.signal_planes = [
            np.full((out_features, n_packed), neutral_word, dtype=np.uint32)
            for _ in range(3)
        ]

        self.steps_accumulated = 0
        self.total_etched = 0

    def accumulate(
        self,
        gamma_grad: "np.ndarray",
        x_abs_mean: "np.ndarray",
        x_mean: "np.ndarray",
        alpha: float = 0.99,
    ) -> None:
        """Accumulate gradient heat and direction from one training step."""
        import numpy as np
        gamma_grad = np.asarray(gamma_grad, dtype=np.float32)
        x_abs_mean = np.asarray(x_abs_mean, dtype=np.float32)
        x_mean = np.asarray(x_mean, dtype=np.float32)

        self.row_heat = alpha * self.row_heat + (1 - alpha) * np.abs(gamma_grad)
        self.col_heat = alpha * self.col_heat + (1 - alpha) * x_abs_mean
        self.row_dir = alpha * self.row_dir + (1 - alpha) * gamma_grad
        self.col_dir = alpha * self.col_dir + (1 - alpha) * x_mean
        self.steps_accumulated += 1

    def reset_signal_planes(self) -> None:
        """Reset all signal planes to neutral."""
        import numpy as np
        n_packed = self.in_features // 16
        neutral_word = sum(1 << (2 * i) for i in range(16))
        for i in range(3):
            self.signal_planes[i] = np.full(
                (self.out_features, n_packed), neutral_word, dtype=np.uint32
            )

    def save_dict(self) -> dict:
        """Serialize for checkpoint."""
        return {
            "row_heat": self.row_heat,
            "col_heat": self.col_heat,
            "row_dir": self.row_dir,
            "col_dir": self.col_dir,
            "signal_plane_0": self.signal_planes[0],
            "signal_plane_1": self.signal_planes[1],
            "signal_plane_2": self.signal_planes[2],
            "steps_accumulated": self.steps_accumulated,
            "total_etched": self.total_etched,
        }

    def load_dict(self, d: dict) -> None:
        """Restore from checkpoint."""
        self.row_heat = d["row_heat"]
        self.col_heat = d["col_heat"]
        self.row_dir = d["row_dir"]
        self.col_dir = d["col_dir"]
        self.signal_planes[0] = d["signal_plane_0"]
        self.signal_planes[1] = d["signal_plane_1"]
        self.signal_planes[2] = d["signal_plane_2"]
        self.steps_accumulated = int(d.get("steps_accumulated", 0))
        self.total_etched = int(d.get("total_etched", 0))


def init_etch_states(model: nn.Module) -> dict[str, EtchState]:
    """Initialize etch state for all TernaryLinear modules."""
    states = {}
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            states[path] = EtchState(mod.out_features, mod.in_features)
    return states


def _extract_gamma_grad(grads, path: str):
    """Extract gamma gradient for a module from the grad tree.

    grads is a nested dict matching model parameter structure.
    path like 'stride_stack.layers.0.q_proj' → grads['stride_stack']['layers'][0]['q_proj']['gamma']
    """
    import numpy as np
    parts = path.split(".")
    node = grads
    try:
        for part in parts:
            if isinstance(node, (list, tuple)):
                node = node[int(part)]
            elif isinstance(node, dict):
                if part.isdigit():
                    node = node[int(part)] if int(part) < len(node) else node[part]
                else:
                    node = node[part]
            else:
                return None
        # node should now be the module's grad dict
        if isinstance(node, dict) and "gamma" in node:
            g = node["gamma"]
            if hasattr(g, '__array__'):
                return np.array(g)
            return g
    except (KeyError, IndexError, TypeError):
        pass
    return None


def accumulate_etch_heat(
    model: nn.Module,
    grads,
    etch_states: dict[str, EtchState],
    alpha: float = 0.99,
) -> None:
    """Accumulate gradient heat for all TernaryLinear modules.

    Called every training step. Uses gamma gradient (from optimizer)
    and cached _x_abs_mean / _x_mean (from forward pass).

    Cost: 4 vector EMAs per module. Negligible.
    """
    import numpy as np

    for path, mod in _walk_ternary_modules(model):
        if path not in etch_states:
            continue
        if not isinstance(mod, TernaryLinear):
            continue

        state = etch_states[path]

        # Gamma gradient from grad tree
        gamma_grad = _extract_gamma_grad(grads, path)
        if gamma_grad is None:
            continue

        # Input activation stats from forward pass cache
        x_abs_mean = np.array(mod._x_abs_mean) if hasattr(mod, '_x_abs_mean') else None
        x_mean = np.array(mod._x_mean) if hasattr(mod, '_x_mean') else None

        if x_abs_mean is None or x_mean is None:
            continue

        state.accumulate(gamma_grad, x_abs_mean, x_mean, alpha=alpha)


def save_etch_states(etch_states: dict[str, EtchState], path: str) -> None:
    """Save all etch states to a .npz file."""
    import numpy as np
    save_dict = {}
    for mod_path, state in etch_states.items():
        d = state.save_dict()
        for k, v in d.items():
            save_dict[f"{mod_path}/{k}"] = v
    np.savez_compressed(path, **save_dict)


def load_etch_states(
    etch_states: dict[str, EtchState], path: str
) -> None:
    """Load etch states from a .npz file."""
    import numpy as np
    from pathlib import Path
    if not Path(path).exists():
        return
    data = dict(np.load(path))
    for mod_path, state in etch_states.items():
        d = {}
        prefix = f"{mod_path}/"
        for k, v in data.items():
            if k.startswith(prefix):
                key = k[len(prefix):]
                d[key] = v
        if d:
            state.load_dict(d)
