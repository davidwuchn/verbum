"""v14 Attention — Stride-Stack at d=1280.

Holographic lens architecture: each stride is a lens pointed at a
different scale of the context. O(L×W) per stride, ternary, CPU-runnable.

Two layer types (same as v13, evolved for d=1280):
  SingleStrideAttention — composition (KIBC dispatch), all strides active
  GatedLinearAttention  — retrieval (M kernel substrate)

16 strides: powers of 2 from s1 to s32768.
  Composition strides: full Q·K attention + fixed α=1.18 decay + HPE
  Retrieval strides: gated linear attention with associative scan

HPE (Holographic Position Encoding): crystal-frequency rotation on K,
warmed up from freq_scale=0 (identity) for checkpoint compatibility.

Fractal stride bands (MERA topology) select 4 strides per pass.
Shared across passes within a stack (S5 coherence).

Base plates: extracted from Qwen3.6-27B, packed ternary.
Delta plates: overlay corrections. No-block on attention (flip-or-keep).

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from config import V14Config, D_MODEL, N_HEADS, D_HEAD, STRIDES, STRIDE_IS_RETRIEVAL, N_STRIDES
from ternary import TernaryLinear, TernaryMirror
from scan import parallel_scan_2d

# Universal decay constant — confirmed at 1.18±0.006 across 10 comp layers
# × 8 heads after 1500 steps of gradient pressure. Not learnable.
_ALPHA = 1.18

# Crystal eigenvalues (Zone B, top 8 — from PCAQ_ZONE_B_TARGETS eigendecomposition).
# These are the natural frequencies of the holographic lens.
_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]

# Number of eigenplane pairs to rotate (the rest carry content, not position).
# First 4 pairs cover 77% of crystal variance (comp, sel, term, rout).
_N_EIGEN_PAIRS = 4

# HPE is active from step 0 — no warmup needed for fresh training.
# The warmup mechanism is retained for checkpoint compatibility but
# defaults to full rotation (freq_scale=1.0).


# ══════════════════════════════════════════════════════════════════════
# § 0  Holographic Position Encoding (HPE)
# ══════════════════════════════════════════════════════════════════════


class HolographicPositionEncoding(nn.Module):
    """Position encoding derived from holographic lens physics.

    Instead of RoPE (arbitrary 10000-base, all dimensions, linear position):
      - Log-position: angle ∝ log(d+1) → natural power-law decay
      - Crystal frequencies: eigenvalues of the crystal target → natural lens bands
      - Selective rotation: only first N_EIGEN_PAIRS dimension pairs → eigenplane only
      - Direct decay bias: -α × log(d+1) → exact, not cosine-envelope approximation

    For stride attention at stride s, window position w:
      absolute_distance = s × w
      log_distance = log(s × w + 1)
      rotation_angle[i] = log_distance × freq[i] × depth_factor

    This unifies position encoding + distance decay into one mechanism:
    the holographic lens's frequency response.
    """

    def __init__(
        self,
        d_head: int = D_HEAD,
        n_eigen_pairs: int = _N_EIGEN_PAIRS,
        alpha: float = _ALPHA,
    ):
        super().__init__()
        self.d_head = d_head
        self.n_eigen_pairs = n_eigen_pairs
        self.alpha = alpha

        # Crystal-derived frequencies (normalized by λ₀)
        freqs = [ev / _CRYSTAL_EIGENVALUES[0] for ev in _CRYSTAL_EIGENVALUES[:n_eigen_pairs]]
        self._freqs = mx.array(freqs)  # (n_eigen_pairs,)

        # Learnable frequency scaling — initialized to 1.0 (full rotation).
        # HPE is active from step 0: the model learns with position encoding
        # from the start, enabling context extension later.
        self.freq_scale = mx.ones((n_eigen_pairs,))

    def apply_rotary(
        self,
        q: mx.array,
        k: mx.array,
        log_distances: mx.array,
    ) -> tuple[mx.array, mx.array]:
        """Apply holographic rotation to Q and K.

        Args:
            q: (B, L, H, Dh) or (B, H, L, Dh) — query
            k: (B, L, W, H, Dh) — gathered keys at stride positions
            log_distances: (W,) — log(stride × w + 1) for each window position

        Returns:
            q_rot, k_rot with rotations applied to first n_eigen_pairs dim pairs.
        """
        n_pairs = self.n_eigen_pairs
        freqs = self._freqs * self.freq_scale  # (n_pairs,)

        # Rotation angles: log_distance × crystal_frequency
        # angles shape: (W, n_pairs)
        angles = log_distances[:, None] * freqs[None, :]  # (W, n_pairs)

        cos_a = mx.cos(angles)  # (W, n_pairs)
        sin_a = mx.sin(angles)  # (W, n_pairs)

        # For Q: position 0 (self) gets zero rotation (log(0+1) = 0)
        # We only need to rotate Q by its absolute position, but since
        # we're doing RELATIVE encoding (like RoPE), we apply rotation
        # to K by the relative log-distance, and leave Q unrotated.
        # The Q·K product then encodes relative log-distance automatically.

        # Rotate the first 2*n_pairs dimensions of K
        k_rot = mx.array(k)  # copy
        for i in range(n_pairs):
            d0 = 2 * i
            d1 = 2 * i + 1
            if d1 >= k.shape[-1]:
                break

            # k has shape (B, L, W, H, Dh)
            # cos_a[w, i] and sin_a[w, i] broadcast over (B, L, H)
            c = cos_a[:, i]  # (W,)
            s = sin_a[:, i]  # (W,)

            # Reshape for broadcasting: (1, 1, W, 1)
            c = c.reshape(1, 1, -1, 1)
            s = s.reshape(1, 1, -1, 1)

            k0 = k[:, :, :, :, d0:d0+1]  # (B, L, W, H, 1)
            k1 = k[:, :, :, :, d1:d1+1]

            k_rot_d0 = k0 * c - k1 * s
            k_rot_d1 = k0 * s + k1 * c

            k_rot = k_rot.at[:, :, :, :, d0:d0+1].add(k_rot_d0 - k0)
            k_rot = k_rot.at[:, :, :, :, d1:d1+1].add(k_rot_d1 - k1)

        return q, k_rot

    def get_decay_bias(self, log_distances: mx.array) -> mx.array:
        """Direct decay bias: -α × log(d+1).

        Args:
            log_distances: (W,) — precomputed log(stride × w + 1)

        Returns:
            (W,) decay bias to add to attention scores.
        """
        return -(self.alpha * log_distances)


def apply_hpe_rotation(
    q: mx.array,
    k_gathered: mx.array,
    log_distances: mx.array,
    n_pairs: int = _N_EIGEN_PAIRS,
    freq_scale: mx.array = None,
) -> tuple[mx.array, mx.array]:
    """Apply holographic position encoding: rotate K by log-distance × crystal freq.

    Rotates K by relative log-distance in the first n_pairs dimension pairs
    (the crystal eigenplane dimensions). Q stays unrotated — relative encoding.

    Args:
        q: (B, H, L, Dh) — queries (transposed)
        k_gathered: (B, L, W, H, Dh) — gathered keys
        log_distances: (W,) — log(stride × w + 1)
        n_pairs: number of eigenplane pairs to rotate
        freq_scale: (n_pairs,) learnable scaling on crystal frequencies

    Returns:
        q (unchanged), k_rotated
    """
    freqs_base = mx.array([ev / _CRYSTAL_EIGENVALUES[0]
                           for ev in _CRYSTAL_EIGENVALUES[:n_pairs]])
    if freq_scale is not None:
        freqs = freqs_base * freq_scale
    else:
        freqs = freqs_base

    # Rotation angles: (W, n_pairs)
    angles = log_distances[:, None] * freqs[None, :]
    cos_a = mx.cos(angles)  # (W, n_pairs)
    sin_a = mx.sin(angles)  # (W, n_pairs)

    # Vectorized rotation of first 2*n_pairs dimensions of K
    # k_gathered: (B, L, W, H, Dh)
    rot_dim = 2 * n_pairs
    Dh = k_gathered.shape[-1]

    # Split K into rotated and non-rotated parts
    k_rot_part = k_gathered[:, :, :, :, :rot_dim]    # (B, L, W, H, 2*n_pairs)
    k_pass_part = k_gathered[:, :, :, :, rot_dim:]   # (B, L, W, H, Dh-2*n_pairs)

    # Reshape rotated part into pairs: (B, L, W, H, n_pairs, 2)
    k_pairs = k_rot_part.reshape(*k_rot_part.shape[:-1], n_pairs, 2)

    # Extract even (d0) and odd (d1) components
    k_even = k_pairs[:, :, :, :, :, 0]  # (B, L, W, H, n_pairs)
    k_odd = k_pairs[:, :, :, :, :, 1]   # (B, L, W, H, n_pairs)

    # Broadcast cos/sin: (1, 1, W, 1, n_pairs)
    c = cos_a.reshape(1, 1, -1, 1, n_pairs)
    s = sin_a.reshape(1, 1, -1, 1, n_pairs)

    # Apply rotation: [cos -sin; sin cos] × [even; odd]
    k_even_rot = k_even * c - k_odd * s
    k_odd_rot = k_even * s + k_odd * c

    # Interleave back: (B, L, W, H, n_pairs, 2) → (B, L, W, H, 2*n_pairs)
    k_rot_interleaved = mx.stack([k_even_rot, k_odd_rot], axis=-1)
    k_rot_flat = k_rot_interleaved.reshape(*k_rot_part.shape)

    # Concatenate rotated + non-rotated
    k_rotated = mx.concatenate([k_rot_flat, k_pass_part], axis=-1)

    return q, k_rotated


# ══════════════════════════════════════════════════════════════════════
# § 1  SingleStrideAttention — composition layers
# ══════════════════════════════════════════════════════════════════════


class SingleStrideAttention(nn.Module):
    """Ternary attention at a single stride and window.

    Each head attends to W past positions at the given stride:
      stride=1:  positions [i, i-1, ..., i-W+1]
      stride=8:  positions [i, i-8, ..., i-8*(W-1)]

    Full Q·K attention for ALL strides with:
      - Fixed decay bias: -α·ln(stride·w + 1), α=1.18 (not learnable)
      - HPE: crystal-frequency rotation on K (warmed up from 0)

    Q/K/V/O are TernaryLinear (base plates from teacher extraction).
    Sparse gather, O(L×W) not O(L²).
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 1,
        window: int = 8,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        decay_init_alpha: float = _ALPHA,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.window = window
        self.n_heads = n_heads
        self.d_head = d_model // n_heads  # 160
        self.scale = self.d_head ** -0.5

        self.norm = nn.RMSNorm(d_model)

        # Beam mirrors before Q
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        # Ternary projections (base plates from extraction)
        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        # Per-feature beam biases
        self.k_bias = mx.zeros((d_model,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

        # HPE: learnable frequency scaling on crystal eigenfrequencies.
        # Initialized to 1.0 — full rotation from step 0.
        self.hpe_freq_scale = mx.ones((_N_EIGEN_PAIRS,))

        # Pre-compute log-distance structure
        w_pos = mx.arange(window, dtype=mx.float32)
        self._log_distances = mx.log(stride * w_pos + 1.0)

        # Fixed α decay bias (not learnable — confirmed universal at 1.18±0.006)
        self._decay_bias = -(_ALPHA * self._log_distances)  # (W,)

    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
        """Full Q·K attention with HPE and fixed α decay.

        HPE rotates K by log-distance × crystal-frequency in the first
        N_EIGEN_PAIRS dimension pairs. Q stays unrotated (relative encoding).
        When hpe_freq_scale is 0, HPE is identity (no rotation).
        """
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W = self.window

        x_norm = self.norm(x)

        # Beam steering
        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        Q = self.q_proj(q_in).reshape(B, L, H, Dh)
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Stride gather
        query_pos = mx.arange(L)[:, None]
        offsets = mx.arange(W)[None, :] * self.stride
        raw_indices = query_pos - offsets
        valid = raw_indices >= 0
        indices = mx.maximum(raw_indices, 0)

        GD = H * Dh
        K_flat = K.reshape(B, L, GD)
        V_flat = V.reshape(B, L, GD)

        idx = indices.reshape(1, L * W, 1)
        idx = mx.broadcast_to(idx, (B, L * W, GD))

        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W, H, Dh)
        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)

        # ── HPE: rotate K by log-distance × crystal frequencies ──
        # When hpe_freq_scale is all zeros, this is identity (no rotation).
        # As freq_scale warms up from 0→1, rotation gradually introduces
        # crystal-derived positional structure.
        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
        _, K_gathered_rot = apply_hpe_rotation(
            Q_r, K_gathered, self._log_distances,
            n_pairs=_N_EIGEN_PAIRS,
            freq_scale=self.hpe_freq_scale,
        )

        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale

        # Fixed α decay bias (the direct power-law, not cosine approximation)
        decay_bias = self._decay_bias * decay_modulation  # (W,)
        attn = attn + decay_bias[None, None, None, :]

        valid_mask = valid[None, None, :, :]
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.clip(attn, -65.0, 65.0)  # prevent float32 softmax overflow (NaN)
        attn = mx.softmax(attn, axis=-1)
        if self.dropout is not None:
            attn = self.dropout(attn)

        V_r = V_gathered.transpose(0, 3, 1, 2, 4)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out) + self.o_bias


# ══════════════════════════════════════════════════════════════════════
# § 2  GatedLinearAttention — retrieval layers
# ══════════════════════════════════════════════════════════════════════


class GatedLinearAttention(nn.Module):
    """Gated linear attention at a single stride — M kernel substrate.

    Running memory per head: (d_head, d_state) accumulates key-value pairs.
    Queries retrieve from memory in O(d) per position.
    Parallel associative scan for training.

    Striding: positions gathered at stride intervals, memory accumulates
    over strided positions for scale-appropriate pattern matching.
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 16,
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

        # Write gate
        self._n_heads_padded = ((n_heads + 15) // 16) * 16
        self.gate_proj = TernaryLinear(d_model, self._n_heads_padded, pre_norm=False)
        self.gate_bias = mx.full((n_heads,), -0.5)

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

        # Diagnostics
        self._gate_values = None
        self._memory_norms = None

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

        self._gate_values = mx.stop_gradient(gate)

        # Stride-aware scan
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

        # Diagnostics
        if stride == 1:
            S_final = S_all[:, -1, :, :, :]
        elif L_s == 0:
            S_final = mx.zeros((B, H, Ds, Dh))
        else:
            S_final = S_stride[:, -1, :, :, :]
        S_norms = mx.sqrt(mx.sum(S_final * S_final, axis=(2, 3)) + 1e-8)
        self._memory_norms = mx.stop_gradient(S_norms.mean(axis=0))

        result = self.out_proj(output) + self.o_bias
        if self.dropout is not None:
            result = self.dropout(result)
        return x + result


# ══════════════════════════════════════════════════════════════════════
# § 3  StrideStack — 11-stride hybrid stack
# ══════════════════════════════════════════════════════════════════════


class StrideStack(nn.Module):
    """Hybrid 11-stride stack: composition + retrieval layers.

    One layer per stride. Layer type determined by STRIDE_IS_RETRIEVAL.
    Shared across passes within a stack (fractal bands select active strides).
    """

    def __init__(self, cfg: V14Config):
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
                self.layers.append(SingleStrideAttention(
                    d_model=d, stride=s, window=cfg.window,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("comp")

        # Per-combinator beam mirrors (shared across strides)
        self.combinator_mirrors = [TernaryMirror(d) for _ in range(cfg.n_combinators)]

    def __call__(
        self,
        x: mx.array,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        """Run active stride layers for one pass.

        Args:
            x: (B, L, d_model)
            stride_range: (start, end) — which stride indices to activate
            reverse: True for descending passes

        Returns: (B, L, d_model)
        """
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
# § 4  HPE Warmup
# ══════════════════════════════════════════════════════════════════════


def set_hpe_warmup_fraction(stride_stack: StrideStack, fraction: float) -> None:
    """Set HPE freq_scale on all SSA layers based on warmup fraction.

    Args:
        stride_stack: The shared StrideStack module.
        fraction: 0.0 = no rotation (identity), 1.0 = full crystal rotation.
                  Clamped to [0, 1]. Typically: min(1, step / HPE_WARMUP_STEPS).

    When fraction=0, cos(0)=1, sin(0)=0 → K is unrotated → identical to
    pre-HPE behavior. This makes checkpoint resume seamless.
    """
    fraction = max(0.0, min(1.0, fraction))
    target = mx.full((_N_EIGEN_PAIRS,), fraction)
    for layer in stride_stack.layers:
        if isinstance(layer, SingleStrideAttention):
            layer.hpe_freq_scale = target


def get_hpe_fraction_for_step(step: int, warmup_start: int = 0) -> float:
    """Compute HPE warmup fraction for a given training step.

    Args:
        step: current training step
        warmup_start: step at which HPE warmup begins (default: 0, i.e. resume step)

    Returns:
        fraction in [0, 1]: linear ramp from warmup_start to warmup_start + HPE_WARMUP_STEPS
    """
    elapsed = step - warmup_start
    if elapsed <= 0:
        return 0.0
    return min(1.0, elapsed / HPE_WARMUP_STEPS)


# ══════════════════════════════════════════════════════════════════════
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v14 attention.py self-test (stride-stack at d=1280)")
    print("=" * 60)

    cfg = V14Config()
    B, L, D = 1, 64, cfg.d_model

    # SingleStrideAttention
    print("\nSingleStrideAttention (s=1, s=8)...")
    for s in (1, 8):
        ssa = SingleStrideAttention(d_model=D, stride=s, window=8, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = ssa(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  s={s}: {y.shape} ✓")

    # GatedLinearAttention
    print("\nGatedLinearAttention (s=16, s=64)...")
    for s in (16, 64):
        gla = GatedLinearAttention(d_model=D, stride=s, d_state=64, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = gla(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        gate_mean = float(mx.mean(gla._gate_values).item())
        print(f"  s={s}: {y.shape} gate={gate_mean:.3f} ✓")

    # StrideStack
    print(f"\nStrideStack ({N_STRIDES} strides, hybrid)...")
    ss = StrideStack(cfg)
    assert len(ss.layers) == N_STRIDES
    n_comp = sum(1 for t in ss._layer_types if t == "comp")
    n_ret = sum(1 for t in ss._layer_types if t == "ret")
    print(f"  {n_comp} composition + {n_ret} retrieval = {len(ss.layers)} strides")

    x = mx.random.normal((B, L, D))

    # Test each pass band
    all_bands = list(cfg.stack_a_bands) + list(cfg.stack_b_bands) + list(cfg.stack_c_bands)
    for i, (start, end) in enumerate(all_bands):
        is_desc = i >= (len(cfg.stack_a_bands) + len(cfg.stack_b_bands))
        y = ss(x, stride_range=(start, end), reverse=is_desc)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  Pass {i} [{start},{end}) rev={is_desc}: ✓")

    # Gradient flow
    print("\nGradient flow...")

    class TestGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = StrideStack(cfg)
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
    print("v14 attention.py: all tests passed ✓")
