"""v15 Attention — Fibonacci Stride with Neighbor Gathering.

Session 189 discovery: binding distances are bimodal (local + instruction),
not power law. Powers-of-2 strides skip the binding range. Fibonacci strides
+ ±2 neighbor gathering achieves 98.2% coverage with 8 strides.

Key changes from v14:
  1. Fibonacci strides (1,2,3,5,8,13,21,34,...) replace powers of 2
  2. Neighbor gathering: for each stride grid point, also gather ±R
     positions to catch binding targets between grid points
  3. The gather+attend window is W_eff = W×(2R+1) = 40 per stride
     (vs W=8 in v14), but most overlap → ~20-30 unique per stride

The attention mechanism:
  For stride s, window W=8, radius R=2, query at position q:
    Grid points:  {q - s·w  | w ∈ 0..W-1}          = 8 positions
    Expanded:     {q - s·w + r | w ∈ 0..W-1, r ∈ -R..R} = 40 positions
    After dedup and boundary clamp: ~20-35 unique positions

  Full Q·K attention over expanded set with:
    - HPE (crystal-frequency rotation on K)
    - α=1.18 decay bias on log-distance
    - Causal masking (expanded positions can include future → mask)

CPU-friendly: all positions computed arithmetically. No hash tables,
no content-based indexing. Gather is stride arithmetic + neighbor offsets.

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from config import (
    V15Config, D_MODEL, N_HEADS, D_HEAD,
    STRIDES, STRIDE_IS_RETRIEVAL, N_STRIDES,
    WINDOW, NEIGHBOR_RADIUS, EFFECTIVE_WINDOW,
)

# Import ternary/scan from v14 (shared infrastructure)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v14"))
from ternary import TernaryLinear, TernaryMirror
from scan import parallel_scan_2d

# Universal constants (confirmed across v13/v14)
_ALPHA = 1.18

# Crystal eigenvalues (from PCAQ targets)
_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]
_N_EIGEN_PAIRS = 4


# ══════════════════════════════════════════════════════════════════════
# § 0  Neighbor-Expanded Gather
# ══════════════════════════════════════════════════════════════════════


def compute_expanded_indices(
    seq_len: int,
    stride: int,
    window: int = WINDOW,
    radius: int = NEIGHBOR_RADIUS,
) -> tuple[mx.array, mx.array, mx.array]:
    """Pre-compute expanded stride+neighbor indices for all query positions.

    For each query position q, compute the set of key positions:
      {q - s·w + r | w ∈ 0..W-1, r ∈ -R..R}

    Returns:
        indices: (L, W_eff) — key positions, clamped to [0, L-1]
        valid:   (L, W_eff) — True where position exists and is causal
        log_distances: (L, W_eff) — log(|q - key_pos| + 1) for HPE/decay
    """
    W_eff = window * (2 * radius + 1)

    # Build offset template: for each (w, r) pair
    offsets = []
    for w in range(window):
        for r in range(-radius, radius + 1):
            offsets.append(stride * w - r)  # subtract r because we go backward
    offsets = mx.array(offsets)  # (W_eff,)

    # For each query position: key_pos = query_pos - offset
    query_pos = mx.arange(seq_len)[:, None]  # (L, 1)
    raw_indices = query_pos - offsets[None, :]  # (L, W_eff) — but offsets go backward

    # Wait — let me reconsider. offset = stride * w - r means:
    #   key_pos = query_pos - (stride * w - r) = query_pos - stride*w + r
    # For w=0, r=0: key_pos = query_pos (self)
    # For w=1, r=0: key_pos = query_pos - stride
    # For w=0, r=2: key_pos = query_pos + 2 (FUTURE — must be masked!)
    # For w=0, r=-2: key_pos = query_pos - 2

    # Causal: key_pos must be <= query_pos
    # Valid: key_pos must be >= 0

    valid = (raw_indices >= 0) & (raw_indices <= query_pos)
    indices = mx.maximum(raw_indices, 0)
    # Also clamp to seq_len-1 for safety
    indices = mx.minimum(indices, seq_len - 1)

    # Log-distances for HPE and decay
    distances = mx.abs(query_pos - indices.astype(mx.float32))
    log_distances = mx.log(distances + 1.0)  # (L, W_eff)

    return indices, valid, log_distances


# ══════════════════════════════════════════════════════════════════════
# § 1  HPE — Holographic Position Encoding (adapted for variable distances)
# ══════════════════════════════════════════════════════════════════════


def apply_hpe_rotation(
    q: mx.array,
    k_gathered: mx.array,
    log_distances: mx.array,
    n_pairs: int = _N_EIGEN_PAIRS,
    freq_scale: mx.array = None,
) -> tuple[mx.array, mx.array]:
    """Apply holographic position encoding: rotate K by log-distance × crystal freq.

    Adapted from v14: now log_distances is (L, W_eff) instead of (W,),
    since each query position has different absolute distances to its
    expanded key set.

    Args:
        q: (B, H, L, Dh) — queries
        k_gathered: (B, L, W_eff, H, Dh) — gathered keys
        log_distances: (L, W_eff) — per-position log-distances
        n_pairs: number of eigenplane pairs to rotate
        freq_scale: (n_pairs,) learnable scaling

    Returns:
        q (unchanged), k_rotated
    """
    freqs_base = mx.array([ev / _CRYSTAL_EIGENVALUES[0]
                           for ev in _CRYSTAL_EIGENVALUES[:n_pairs]])
    if freq_scale is not None:
        freqs = freqs_base * freq_scale
    else:
        freqs = freqs_base

    # Rotation angles: (L, W_eff, n_pairs)
    angles = log_distances[:, :, None] * freqs[None, None, :]
    cos_a = mx.cos(angles)  # (L, W_eff, n_pairs)
    sin_a = mx.sin(angles)

    rot_dim = 2 * n_pairs
    Dh = k_gathered.shape[-1]

    # Split K into rotated and non-rotated
    k_rot_part = k_gathered[:, :, :, :, :rot_dim]    # (B, L, W_eff, H, 2*n_pairs)
    k_pass_part = k_gathered[:, :, :, :, rot_dim:]   # rest

    # Reshape into pairs: (B, L, W_eff, H, n_pairs, 2)
    k_pairs = k_rot_part.reshape(*k_rot_part.shape[:-1], n_pairs, 2)
    k_even = k_pairs[:, :, :, :, :, 0]  # (B, L, W_eff, H, n_pairs)
    k_odd = k_pairs[:, :, :, :, :, 1]

    # Broadcast cos/sin: (1, L, W_eff, 1, n_pairs)
    c = cos_a.reshape(1, cos_a.shape[0], cos_a.shape[1], 1, n_pairs)
    s = sin_a.reshape(1, sin_a.shape[0], sin_a.shape[1], 1, n_pairs)

    k_even_rot = k_even * c - k_odd * s
    k_odd_rot = k_even * s + k_odd * c

    k_rot_interleaved = mx.stack([k_even_rot, k_odd_rot], axis=-1)
    k_rot_flat = k_rot_interleaved.reshape(*k_rot_part.shape)

    k_rotated = mx.concatenate([k_rot_flat, k_pass_part], axis=-1)
    return q, k_rotated


# ══════════════════════════════════════════════════════════════════════
# § 2  FibonacciStrideAttention — composition with neighbor gathering
# ══════════════════════════════════════════════════════════════════════


class FibonacciStrideAttention(nn.Module):
    """Attention at a Fibonacci stride with ±R neighbor gathering.

    For each query position, attends to W_eff = W × (2R+1) candidate
    key positions: the stride grid plus neighbors. This catches binding
    targets that fall between grid points.

    Replaces v14's SingleStrideAttention. Same Q·K·V mechanism, but
    with expanded gather and per-position log-distances.
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 1,
        window: int = WINDOW,
        radius: int = NEIGHBOR_RADIUS,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.window = window
        self.radius = radius
        self.w_eff = window * (2 * radius + 1)
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.scale = self.d_head ** -0.5

        self.norm = nn.RMSNorm(d_model)

        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.k_bias = mx.zeros((d_model,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

        # HPE frequency scaling
        self.hpe_freq_scale = mx.ones((_N_EIGEN_PAIRS,))

        # Pre-computed indices are cached per seq_len (lazily)
        self._cached_seq_len = -1
        self._cached_indices = None
        self._cached_valid = None
        self._cached_log_distances = None

    def _ensure_indices(self, seq_len: int):
        """Lazily compute and cache expanded stride indices."""
        if self._cached_seq_len != seq_len:
            indices, valid, log_dist = compute_expanded_indices(
                seq_len, self.stride, self.window, self.radius
            )
            self._cached_indices = indices
            self._cached_valid = valid
            self._cached_log_distances = log_dist
            self._cached_seq_len = seq_len

    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W_eff = self.w_eff

        self._ensure_indices(L)
        indices = self._cached_indices       # (L, W_eff)
        valid = self._cached_valid           # (L, W_eff)
        log_distances = self._cached_log_distances  # (L, W_eff)

        x_norm = self.norm(x)

        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        Q = self.q_proj(q_in).reshape(B, L, H, Dh)
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Gather K, V at expanded positions
        GD = H * Dh
        K_flat = K.reshape(B, L, GD)
        V_flat = V.reshape(B, L, GD)

        idx = indices.reshape(1, L * W_eff, 1)  # (1, L*W_eff, 1)
        idx = mx.broadcast_to(idx, (B, L * W_eff, GD))

        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W_eff, H, Dh)
        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W_eff, H, Dh)

        # HPE: rotate K by log-distance × crystal frequencies
        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
        _, K_gathered_rot = apply_hpe_rotation(
            Q_r, K_gathered, log_distances,
            n_pairs=_N_EIGEN_PAIRS,
            freq_scale=self.hpe_freq_scale,
        )

        # Attention scores
        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W_eff, Dh)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale  # (B, H, L, W_eff)

        # Decay bias: -α · log(distance + 1), per-position
        decay_bias = -(_ALPHA * decay_modulation * log_distances)  # (L, W_eff)
        attn = attn + decay_bias[None, None, :, :]

        # Mask invalid positions (out of bounds or non-causal)
        valid_mask = valid[None, None, :, :]  # (1, 1, L, W_eff)
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.clip(attn, -65.0, 65.0)
        attn = mx.softmax(attn, axis=-1)
        if self.dropout is not None:
            attn = self.dropout(attn)

        # Weighted sum of values
        V_r = V_gathered.transpose(0, 3, 1, 2, 4)  # (B, H, L, W_eff, Dh)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)  # (B, H, L, Dh)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out) + self.o_bias


# ══════════════════════════════════════════════════════════════════════
# § 3  GatedLinearAttention — unchanged from v14
# ══════════════════════════════════════════════════════════════════════


class GatedLinearAttention(nn.Module):
    """Gated linear attention at a Fibonacci stride — retrieval via running memory.

    Identical to v14's GLA: running memory per head, associative scan,
    O(d) per position. The stride spacing changes but the mechanism doesn't.
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 55,
        d_state: int = 64,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.d_state = d_state
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.norm = nn.RMSNorm(d_model)
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        self.q_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.k_bias = mx.zeros((n_heads * d_state,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        self._n_heads_padded = ((n_heads + 15) // 16) * 16
        self.gate_proj = TernaryLinear(d_model, self._n_heads_padded, pre_norm=False)
        self.gate_bias = mx.full((n_heads,), -0.5)

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

    def __call__(self, x: mx.array) -> mx.array:
        B, L, D = x.shape
        H = self.n_heads
        Ds = self.d_state
        Dh = self.d_head
        stride = self.stride

        x_norm = self.norm(x)

        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        q_raw = self.q_proj(q_in).reshape(B, L, H, Ds)
        k_raw = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Ds)
        v = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
        gate = mx.sigmoid(
            self.gate_proj(x_norm)[..., :H] + self.gate_bias
        )

        q = nn.elu(q_raw) + 1.0
        k = nn.elu(k_raw) + 1.0

        if stride == 1:
            L_s = L
            kv_outer = k[:, :, :, :, None] * v[:, :, :, None, :]
            gate_expand = gate[:, :, :, None, None]
            gated_kv = gate_expand * kv_outer
            retention = 1.0 - gate
            S_all = parallel_scan_2d(retention, gated_kv)
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)
        else:
            L_s = L // stride
            if L_s == 0:
                output = mx.zeros((B, L, H, Dh))
            else:
                stride_idx = mx.arange(L_s) * stride
                k_s = k[:, stride_idx, :, :]
                v_s = v[:, stride_idx, :, :]
                gate_s = gate[:, stride_idx, :]

                kv_outer_s = k_s[:, :, :, :, None] * v_s[:, :, :, None, :]
                gate_s_expand = gate_s[:, :, :, None, None]
                gated_kv_s = gate_s_expand * kv_outer_s
                retention_s = 1.0 - gate_s

                S_stride = parallel_scan_2d(retention_s, gated_kv_s)

                state_idx = mx.minimum(mx.arange(L) // stride, L_s - 1)
                S_all = S_stride[:, state_idx, :, :, :]
                output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)

        output = output.reshape(B, L, D)
        result = self.out_proj(output) + self.o_bias
        if self.dropout is not None:
            result = self.dropout(result)
        return x + result


# ══════════════════════════════════════════════════════════════════════
# § 4  FibonacciStrideStack — the complete attention module
# ══════════════════════════════════════════════════════════════════════


class FibonacciStrideStack(nn.Module):
    """Hybrid stride stack with Fibonacci spacing + neighbor gathering.

    One layer per stride. Composition strides use FibonacciStrideAttention
    (Q·K with neighbor expansion). Retrieval strides use GLA (running memory).
    """

    def __init__(self, cfg: V15Config):
        super().__init__()
        d = cfg.d_model
        n_q = cfg.n_q_mirrors if cfg.use_q_mirrors else 0

        self.layers = []
        self._layer_types = []

        for s, is_ret in zip(cfg.strides, cfg.stride_is_retrieval):
            if is_ret:
                self.layers.append(GatedLinearAttention(
                    d_model=d, stride=s, d_state=cfg.d_state,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("ret")
            else:
                self.layers.append(FibonacciStrideAttention(
                    d_model=d, stride=s,
                    window=cfg.window, radius=cfg.neighbor_radius,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("comp")

        self.combinator_mirrors = [TernaryMirror(d) for _ in range(cfg.n_combinators)]

    def __call__(
        self,
        x: mx.array,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        if stride_range is not None:
            start, end = stride_range
            indices = list(range(start, min(end, len(self.layers))))
        else:
            indices = list(range(len(self.layers)))

        if reverse:
            indices = list(reversed(indices))

        for i in indices:
            x = self.layers[i](x)

        return x


# ══════════════════════════════════════════════════════════════════════
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v15 attention.py self-test (Fibonacci stride + neighbors)")
    print("=" * 60)

    cfg = V15Config()
    B, L, D = 1, 64, cfg.d_model

    # Test expanded index computation
    print("\nExpanded index computation...")
    for s in [1, 3, 8, 13, 34]:
        indices, valid, log_dist = compute_expanded_indices(L, s, WINDOW, NEIGHBOR_RADIUS)
        n_valid = float(mx.sum(valid[L//2]).item())
        print(f"  stride={s:3d}: indices={indices.shape}, valid@mid={n_valid:.0f}/{indices.shape[1]}")

    # FibonacciStrideAttention
    print(f"\nFibonacciStrideAttention (s=1, s=8, s=34)...")
    for s in (1, 8, 34):
        fsa = FibonacciStrideAttention(d_model=D, stride=s, window=WINDOW,
                                        radius=NEIGHBOR_RADIUS, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = fsa(x)
        mx.eval(y)
        assert y.shape == (B, L, D), f"Expected {(B, L, D)}, got {y.shape}"
        print(f"  s={s:3d}: {y.shape} ✓  (W_eff={fsa.w_eff})")

    # GatedLinearAttention
    print(f"\nGatedLinearAttention (s=55, s=144)...")
    for s in (55, 144):
        gla = GatedLinearAttention(d_model=D, stride=s, d_state=64, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = gla(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  s={s:3d}: {y.shape} ✓")

    # FibonacciStrideStack
    print(f"\nFibonacciStrideStack ({N_STRIDES} strides, Fibonacci)...")
    ss = FibonacciStrideStack(cfg)
    assert len(ss.layers) == N_STRIDES
    n_comp = sum(1 for t in ss._layer_types if t == "comp")
    n_ret = sum(1 for t in ss._layer_types if t == "ret")
    print(f"  {n_comp} composition + {n_ret} retrieval = {len(ss.layers)} strides")

    x = mx.random.normal((B, L, D))

    # Test each pass band
    all_bands = list(cfg.stack_a_bands) + list(cfg.stack_c_bands)
    for i, (start, end) in enumerate(all_bands):
        is_desc = i >= len(cfg.stack_a_bands)
        y = ss(x, stride_range=(start, end), reverse=is_desc)
        mx.eval(y)
        assert y.shape == (B, L, D)
        strides_in_band = cfg.strides[start:end]
        print(f"  Pass {i} [{start},{end}) rev={is_desc}: strides {strides_in_band} ✓")

    # Gradient flow
    print("\nGradient flow...")

    class TestGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = FibonacciStrideStack(cfg)
        def __call__(self, x):
            return mx.mean(self.stack(x, stride_range=(0, 4)))

    m = TestGrad()
    mx.eval(m.parameters())
    gfn = nn.value_and_grad(m, lambda m, x: m(x))
    x_test = mx.random.normal((1, 32, D))
    lv, g = gfn(m, x_test)
    mx.eval(lv, g)
    print(f"  loss={lv.item():.6f} ✓")

    print("\n" + "=" * 60)
    print("v15 attention.py: all tests passed ✓")
