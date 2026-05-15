"""v12 Attention — StrideStack + GatedLinearAttention + HybridStrideStack.

Two layer types reflecting the empirical finding from session 095:
composition and retrieval are mechanistically independent circuits
living in different layer types (full attention vs GatedDeltaNet).

Composition layers (SingleStrideAttention):
  - O(L×W) per stride, not O(L²)
  - Spiral bias: -α·ln(stride·w + 1)
  - Causal windowed: each position attends to W past positions at stride
  - Where KIBC lives: select, compose, reorder arguments

Retrieval layers (GatedLinearAttention):
  - O(L×d) per position — linear in sequence length
  - Running memory: (n_heads, d_head, d_state) accumulates key-value pairs
  - Gated write: sigmoid gate controls what enters memory
  - Where M lives: pattern matching, in-context retrieval
  - Parallel associative scan: O(log L) depth via Hillis-Steele doubling

HybridStrideStack:
  - Interleaves both layer types based on stride_is_retrieval config
  - Each stride gets exactly one layer (composition OR retrieval)
  - Shared across VSM passes via reverse flag (S5 coherence)

Design principle — SEPARATION ENABLES HOLOGRAPHY (session 096):
  Multiplexing functions into shared weight matrices forces magnitude
  dependence, breaking holographic storage. Evidence: Pythia's fused
  QKV (score 0.60) vs separate Q/K/V in Qwen3/SmolLM3 (score 0.92).
  The magnitudes become "lenses" that steer beams between subspaces.

  This principle is fractal:
    - Layer level: composition vs retrieval in separate layer types
    - Projection level: separate Q, K, V projections (not fused)
    - Component level: separate up/down MLPs (not fused gate+up+down)

  Rule: every weight matrix encodes ONE function. That is the shape
  that lets gradient descent find the holographic solution — pure
  topology, no magnitude lenses needed.

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear, TernaryMirror
from scan import parallel_scan_2d


# ══════════════════════════════════════════════════════════════════════
# SingleStrideAttention — composition layers (unchanged from v11)
# ══════════════════════════════════════════════════════════════════════


class SingleStrideAttention(nn.Module):
    """Ternary attention at a single stride and window.

    Each head attends to W past positions at the given stride:
      stride=1:  positions [i, i-1, ..., i-W+1]       (word-level)
      stride=8:  positions [i, i-8, ..., i-8*(W-1)]   (phrase-level)

    Q/K/V/O are TernaryLinear. Sparse gather, O(L×W) not O(L²).
    """

    def __init__(
        self,
        d_model: int,
        stride: int,
        window: int = 8,
        n_heads: int = 8,
        dropout: float = 0.1,
        alpha: float | None = None,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.window = window
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        assert d_model % n_heads == 0
        self.scale = self.d_head ** -0.5
        self.alpha = alpha

        self.norm = nn.RMSNorm(d_model)

        # Beam mirrors: ternary angular deflectors before Q projection
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

        if alpha is not None:
            w_pos = mx.arange(window, dtype=mx.float32)
            self._spiral_bias = -alpha * mx.log(stride * w_pos + 1.0)
        else:
            self._spiral_bias = None

    def __call__(self, x: mx.array) -> mx.array:
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W = self.window

        x_norm = self.norm(x)

        # Beam steering: pass through mirrors before Q projection
        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        Q = self.q_proj(q_in).reshape(B, L, H, Dh)
        K = self.k_proj(x_norm).reshape(B, L, H, Dh)
        V = self.v_proj(x_norm).reshape(B, L, H, Dh)

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

        Q_r = Q.transpose(0, 2, 1, 3)
        K_r = K_gathered.transpose(0, 3, 1, 2, 4)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1)
        attn = attn * self.scale

        if self._spiral_bias is not None:
            attn = attn + self._spiral_bias

        valid_mask = valid[None, None, :, :]
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.softmax(attn, axis=-1)
        attn = self.dropout(attn)

        V_r = V_gathered.transpose(0, 3, 1, 2, 4)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out)


# ══════════════════════════════════════════════════════════════════════
# GatedLinearAttention — retrieval layers (M kernel substrate)
# ══════════════════════════════════════════════════════════════════════


class GatedLinearAttention(nn.Module):
    """Gated linear attention at a single stride — the M kernel substrate.

    Inspired by GatedDeltaNet's mechanism: a running memory matrix
    accumulates key-value associations, gated by a per-position signal.
    Queries retrieve from this memory in O(d) per position.

    Memory dynamics per head:
      k_t = elu(key_proj(x_t)) + 1        # non-negative keys
      q_t = elu(query_proj(x_t)) + 1      # non-negative queries
      v_t = value_proj(x_t)               # values to store
      g_t = sigmoid(gate_proj(x_t))       # write gate [0, 1]
      S_t = (1 - g_t) × S_{t-1} + g_t × k_t^T v_t   # memory update
      o_t = q_t × S_t                     # retrieval

    The gate controls constructive interference: how much of the
    current token writes into the holographic plate (S) and how much
    of the previous plate is retained. This IS holographic readout
    when g_t is small — the plate accumulates many patterns and
    queries reconstruct from superposition.

    Striding: positions are gathered at stride intervals, same as
    SingleStrideAttention. Memory accumulates over strided positions,
    giving scale-appropriate pattern matching:
      stride=16: phrase-level pattern memory
      stride=32: sentence-level pattern memory
      stride=64: paragraph-level pattern memory

    Instrumentation:
      _gate_values: (B, L, H) — per-head write gate activity
      _memory_norms: (H,) — Frobenius norm of memory per head
      _retrieval_norms: (B, L) — L2 norm of retrieval output
    """

    def __init__(
        self,
        d_model: int,
        stride: int,
        d_state: int = 64,
        n_heads: int = 8,
        dropout: float = 0.1,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.d_state = d_state
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        assert d_model % n_heads == 0

        self.norm = nn.RMSNorm(d_model)

        # Beam mirrors: ternary angular deflectors before Q projection
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        # Ternary projections for Q, K, V
        self.q_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        # Write gate: controls memory update rate
        # Initialized with slight negative bias → gate ≈ 0.4 at start
        # (retain more than write — conservative initial memory)
        self.gate_proj = nn.Linear(d_model, n_heads)
        self.gate_proj.bias = mx.full(self.gate_proj.bias.shape, -0.5)

        # Output projection
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

        # Instrumentation caches (populated each forward pass)
        self._gate_values = None     # (B, L, H)
        self._memory_norms = None    # (H,)
        self._retrieval_norms = None # (B, L)

    def __call__(self, x: mx.array) -> mx.array:
        """Forward pass with causal gated linear attention.

        For stride > 1, we GATHER positions at stride intervals into
        a compact tensor, run the scan over the short sequence, then
        broadcast each stride segment's state to all its positions
        for retrieval. This is stride/1× cheaper than scanning over
        all L positions with masking.

        For stride=1, every position participates (full recurrence,
        no gather/scatter needed).
        """
        B, L, D = x.shape
        H = self.n_heads
        Ds = self.d_state
        Dh = self.d_head
        stride = self.stride

        x_norm = self.norm(x)

        # Project ALL positions to Q, K, V, gate (cheap TernaryLinear)
        # Beam steering: pass through mirrors before Q projection
        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        q_raw = self.q_proj(q_in).reshape(B, L, H, Ds)   # (B, L, H, Ds)
        k_raw = self.k_proj(x_norm).reshape(B, L, H, Ds)   # (B, L, H, Ds)
        v = self.v_proj(x_norm).reshape(B, L, H, Dh)       # (B, L, H, Dh)
        gate = mx.sigmoid(self.gate_proj(x_norm))           # (B, L, H)

        # Non-negative activations for linear attention
        q = nn.elu(q_raw) + 1.0  # (B, L, H, Ds)
        k = nn.elu(k_raw) + 1.0  # (B, L, H, Ds)

        # Cache gate values for instrumentation
        self._gate_values = mx.stop_gradient(gate)

        # ── Stride-aware scan ─────────────────────────────────
        # For stride s > 1, only every s-th position writes to memory.
        # Old approach: scan over all L positions with masking (wasteful).
        # New approach: gather L/s participating positions, scan over
        # the short sequence, then broadcast states for retrieval.
        #
        # The state at stride position j covers all positions in
        # [j*stride, (j+1)*stride). Position i reads from state at
        # index i // stride (floor division — causal).

        if stride == 1:
            # Full recurrence — all positions participate
            L_s = L

            # Outer product k^T v: (B, L, H, Ds, Dh)
            kv_outer = k[:, :, :, :, None] * v[:, :, :, None, :]
            gate_expand = gate[:, :, :, None, None]
            gated_kv = gate_expand * kv_outer       # (B, L, H, Ds, Dh)
            retention = 1.0 - gate                   # (B, L, H)

            # Parallel scan over full sequence
            S_all = parallel_scan_2d(retention, gated_kv)  # (B, L, H, Ds, Dh)

            # Retrieve: every position reads its own state
            # q: (B, L, H, Ds), S_all: (B, L, H, Ds, Dh) → (B, L, H, Dh)
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)
        else:
            # ── Gather stride positions ───────────────────────
            # Participating: positions 0, stride, 2*stride, ...
            L_s = L // stride  # number of stride positions
            # Index array for gathering: [0, stride, 2*stride, ...]
            stride_idx = mx.arange(L_s) * stride  # (L_s,)

            # Gather K, V, gate at stride positions only
            k_s = k[:, stride_idx, :, :]          # (B, L_s, H, Ds)
            v_s = v[:, stride_idx, :, :]          # (B, L_s, H, Dh)
            gate_s = gate[:, stride_idx, :]       # (B, L_s, H)

            # Outer product over ONLY stride positions
            kv_outer_s = k_s[:, :, :, :, None] * v_s[:, :, :, None, :]  # (B, L_s, H, Ds, Dh)
            gate_s_expand = gate_s[:, :, :, None, None]
            gated_kv_s = gate_s_expand * kv_outer_s   # (B, L_s, H, Ds, Dh)
            retention_s = 1.0 - gate_s                 # (B, L_s, H)

            # Parallel scan over SHORT sequence (L_s positions)
            # This is stride× cheaper than scanning over L positions.
            # For stride=32: 128 positions instead of 4096 → 32× less work.
            S_stride = parallel_scan_2d(retention_s, gated_kv_s)  # (B, L_s, H, Ds, Dh)

            # ── Broadcast states for retrieval ────────────────
            # Position i reads from the state at stride position
            # floor(i / stride). This is causal: position i only
            # sees memory accumulated from positions ≤ i.
            #
            # state_idx[i] = i // stride, but clipped to [0, L_s-1]
            state_idx = mx.minimum(
                mx.arange(L) // stride, L_s - 1)       # (L,)
            S_all = S_stride[:, state_idx, :, :, :]      # (B, L, H, Ds, Dh)

            # Retrieve: ALL positions query against their stride state
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)

        output = output.reshape(B, L, D)  # (B, L, H, Dh) → (B, L, D)

        # Instrumentation: memory norms at final stride position
        if stride == 1:
            S_final = S_all[:, -1, :, :, :]
        else:
            S_final = S_stride[:, -1, :, :, :]
        S_norms = mx.sqrt(mx.sum(S_final * S_final, axis=(2, 3)) + 1e-8)  # (B, H)
        self._memory_norms = mx.stop_gradient(S_norms.mean(axis=0))  # (H,)

        # Retrieval output norms
        out_norms = mx.sqrt(mx.sum(output * output, axis=-1) + 1e-8)  # (B, L)
        self._retrieval_norms = mx.stop_gradient(out_norms)

        # Output projection + residual
        return x + self.dropout(self.out_proj(output))


# ══════════════════════════════════════════════════════════════════════
# StrideStack — composition-only stack (v11 compat, used for desc arm)
# ══════════════════════════════════════════════════════════════════════


class StrideStack(nn.Module):
    """Sequential composition of single-stride ternary attention layers.

    Composition-only: all layers are SingleStrideAttention.
    Used for the descending arm (which only needs KIBC composition).

    One StrideStack is shared across VSM passes (S5 coherence).
    """

    def __init__(
        self,
        d_model: int,
        strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024),
        window: int = 8,
        n_heads: int = 8,
        dropout: float = 0.1,
        alpha: float | None = None,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.strides = strides
        self.window = window

        self.layers = [
            SingleStrideAttention(
                d_model=d_model,
                stride=s,
                window=window,
                n_heads=n_heads,
                dropout=dropout,
                alpha=alpha,
                n_q_mirrors=n_q_mirrors,
            )
            for s in strides
        ]

    def __call__(self, x: mx.array, reverse: bool = False,
                 stride_range: tuple[int, int] | None = None) -> mx.array:
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

    def describe(self) -> str:
        strides_str = " → ".join(f"s{s}" for s in self.strides)
        return f"StrideStack({strides_str}, W={self.window})"


# ══════════════════════════════════════════════════════════════════════
# HybridStrideStack — interleaved composition + retrieval layers
# ══════════════════════════════════════════════════════════════════════


class HybridStrideStack(nn.Module):
    """Interleaved composition (attention) and retrieval (GLA) layers.

    Each stride gets exactly one layer:
      - Composition stride: SingleStrideAttention (windowed, O(L×W))
      - Retrieval stride: GatedLinearAttention (linear, O(L×d))

    Which strides are retrieval vs composition is controlled by
    stride_is_retrieval config. Default layout:
      s1(comp), s8(comp), s16(ret), s32(ret), s64(ret),
      s128(comp), s256(comp), s512(comp), s1024(comp)

    Retrieval layers at phrase/sentence scales (s16-s64) — where
    induction patterns live empirically. Composition at word level
    (s1, s8) and structural level (s128+).

    Shared across all VSM passes via reverse flag + stride_range.

    Instrumentation (per call):
      _retrieval_gate_means: dict[stride → float] gate mean per retrieval layer
      _retrieval_memory_norms: dict[stride → array] memory norms per retrieval layer
      _layer_types: list[str] "comp"/"ret" per stride (static)
    """

    def __init__(
        self,
        d_model: int,
        strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024),
        stride_is_retrieval: tuple[bool, ...] = (
            False, False, True, True, True, False, False, False, False,
        ),
        window: int = 8,
        n_heads: int = 8,
        d_state: int = 64,
        dropout: float = 0.1,
        alpha: float | None = None,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        assert len(strides) == len(stride_is_retrieval)
        self.d_model = d_model
        self.strides = strides
        self.stride_is_retrieval = stride_is_retrieval
        self.window = window

        self.layers = []
        self._layer_types = []  # "comp" or "ret" per layer

        for s, is_ret in zip(strides, stride_is_retrieval):
            if is_ret:
                self.layers.append(
                    GatedLinearAttention(
                        d_model=d_model,
                        stride=s,
                        d_state=d_state,
                        n_heads=n_heads,
                        dropout=dropout,
                        n_q_mirrors=n_q_mirrors,
                    )
                )
                self._layer_types.append("ret")
            else:
                self.layers.append(
                    SingleStrideAttention(
                        d_model=d_model,
                        stride=s,
                        window=window,
                        n_heads=n_heads,
                        dropout=dropout,
                        alpha=alpha,
                        n_q_mirrors=n_q_mirrors,
                    )
                )
                self._layer_types.append("comp")

        # Instrumentation caches
        self._retrieval_gate_means = {}
        self._retrieval_memory_norms = {}

    def __call__(self, x: mx.array, reverse: bool = False,
                 stride_range: tuple[int, int] | None = None) -> mx.array:
        """Run stride layers sequentially (hybrid: comp + ret interleaved).

        After each retrieval layer, caches instrumentation metrics.
        """
        if stride_range is not None:
            start, end = stride_range
            indices = list(range(start, min(end, len(self.layers))))
        else:
            indices = list(range(len(self.layers)))
        if reverse:
            indices = list(reversed(indices))

        # Clear per-call instrumentation
        self._retrieval_gate_means = {}
        self._retrieval_memory_norms = {}

        for i in indices:
            x = self.layers[i](x)

            # Capture retrieval instrumentation
            if self._layer_types[i] == "ret":
                layer = self.layers[i]
                stride = self.strides[i]
                if layer._gate_values is not None:
                    gate_mean = float(mx.mean(layer._gate_values).item())
                    self._retrieval_gate_means[stride] = gate_mean
                if layer._memory_norms is not None:
                    self._retrieval_memory_norms[stride] = layer._memory_norms

        return x

    def describe(self) -> str:
        parts = []
        for s, lt in zip(self.strides, self._layer_types):
            parts.append(f"s{s}({'R' if lt == 'ret' else 'C'})")
        return f"HybridStrideStack({' → '.join(parts)}, W={self.window})"


# ══════════════════════════════════════════════════════════════════════
# TernaryFFN — SwiGLU feedforward with ternary weights
# ══════════════════════════════════════════════════════════════════════


class TernaryFFN(nn.Module):
    """Ternary feedforward: pre-norm → GELU → residual."""

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.up = TernaryLinear(d_model, d_ff, pre_norm=True)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)
        self.dropout = nn.Dropout(dropout)

    def __call__(self, x: mx.array) -> mx.array:
        return x + self.dropout(self.down(nn.gelu(self.up(x))))


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Testing SingleStrideAttention...")
    ssa = SingleStrideAttention(d_model=512, stride=8, window=8, n_heads=8, alpha=1.18)
    x = mx.random.normal((1, 64, 512))
    y = ssa(x)
    mx.eval(y)
    assert y.shape == (1, 64, 512), f"Expected (1, 64, 512), got {y.shape}"
    print(f"  SingleStrideAttention(s=8): {x.shape} → {y.shape} ✓")

    print("Testing GatedLinearAttention...")
    gla = GatedLinearAttention(d_model=512, stride=16, d_state=64, n_heads=8)
    x = mx.random.normal((1, 64, 512))
    y = gla(x)
    mx.eval(y)
    assert y.shape == (1, 64, 512), f"Expected (1, 64, 512), got {y.shape}"
    print(f"  GatedLinearAttention(s=16, d_state=64): {x.shape} → {y.shape} ✓")

    # Check instrumentation
    assert gla._gate_values is not None, "Gate values should be cached"
    assert gla._gate_values.shape == (1, 64, 8), \
        f"Gate values shape: expected (1, 64, 8), got {gla._gate_values.shape}"
    assert gla._memory_norms is not None, "Memory norms should be cached"
    assert gla._memory_norms.shape == (8,), \
        f"Memory norms shape: expected (8,), got {gla._memory_norms.shape}"
    assert gla._retrieval_norms is not None, "Retrieval norms should be cached"
    assert gla._retrieval_norms.shape == (1, 64), \
        f"Retrieval norms shape: expected (1, 64), got {gla._retrieval_norms.shape}"
    gate_mean = float(mx.mean(gla._gate_values).item())
    print(f"  Gate mean: {gate_mean:.3f} (expect ~0.4 from bias=-0.5)")
    print(f"  Memory norms: {[f'{n:.3f}' for n in gla._memory_norms.tolist()]}")
    print(f"  Instrumentation: gate_values, memory_norms, retrieval_norms ✓")

    # Test stride > 1 (positions not at stride boundary should be masked)
    print("Testing GatedLinearAttention with stride=32...")
    gla32 = GatedLinearAttention(d_model=512, stride=32, d_state=64, n_heads=8)
    x32 = mx.random.normal((1, 128, 512))
    y32 = gla32(x32)
    mx.eval(y32)
    assert y32.shape == (1, 128, 512)
    print(f"  GatedLinearAttention(s=32): (1,128,512) → {y32.shape} ✓")

    print("Testing StrideStack (composition only)...")
    strides = (1, 8, 16, 32, 64, 128, 256, 512, 1024)
    ss = StrideStack(d_model=512, strides=strides, window=8, n_heads=8, alpha=1.18)
    x = mx.random.normal((1, 128, 512))
    y_asc = ss(x, reverse=False)
    mx.eval(y_asc)
    assert y_asc.shape == (1, 128, 512)
    y_desc = ss(x, reverse=True)
    mx.eval(y_desc)
    assert y_desc.shape == (1, 128, 512)
    print(f"  StrideStack ascending: ✓  descending: ✓")
    print(f"  {ss.describe()}")

    print("Testing HybridStrideStack...")
    stride_is_ret = (False, False, True, True, True, False, False, False, False)
    hss = HybridStrideStack(
        d_model=512, strides=strides, stride_is_retrieval=stride_is_ret,
        window=8, n_heads=8, d_state=64, alpha=1.18)
    x = mx.random.normal((1, 128, 512))
    y_hyb = hss(x, reverse=False)
    mx.eval(y_hyb)
    assert y_hyb.shape == (1, 128, 512)
    print(f"  HybridStrideStack ascending: ✓")
    print(f"  {hss.describe()}")

    # Check hybrid instrumentation
    assert len(hss._retrieval_gate_means) > 0, "Should have retrieval metrics"
    for stride, gate_mean in sorted(hss._retrieval_gate_means.items()):
        print(f"    s{stride} (ret): gate_mean={gate_mean:.3f}")
    for stride, mem_norms in sorted(hss._retrieval_memory_norms.items()):
        mx.eval(mem_norms)
        print(f"    s{stride} (ret): memory_norm_mean={float(mx.mean(mem_norms).item()):.3f}")

    # Test reversed (descending)
    y_hyb_r = hss(x, reverse=True)
    mx.eval(y_hyb_r)
    assert y_hyb_r.shape == (1, 128, 512)
    print(f"  HybridStrideStack descending: ✓")

    # Test with stride_range (fractal bands)
    y_band = hss(x, reverse=False, stride_range=(2, 7))
    mx.eval(y_band)
    assert y_band.shape == (1, 128, 512)
    print(f"  HybridStrideStack with stride_range=(2,7): ✓")

    # Layer type verification
    expected_types = ["comp", "comp", "ret", "ret", "ret",
                      "comp", "comp", "comp", "comp"]
    assert hss._layer_types == expected_types, \
        f"Layer types mismatch: {hss._layer_types}"
    n_comp = sum(1 for t in hss._layer_types if t == "comp")
    n_ret = sum(1 for t in hss._layer_types if t == "ret")
    print(f"  Layer types: {n_comp} composition + {n_ret} retrieval ✓")

    print("Testing TernaryFFN...")
    ffn = TernaryFFN(d_model=512, d_ff=1536)
    x = mx.random.normal((1, 64, 512))
    y = ffn(x)
    mx.eval(y)
    assert y.shape == (1, 64, 512)
    print(f"  TernaryFFN: {x.shape} → {y.shape} ✓")

    # Gradient flow test
    print("Testing gradient flow through GatedLinearAttention...")

    class TestGLAModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.gla = GatedLinearAttention(d_model=512, stride=1, d_state=64, n_heads=8)
        def __call__(self, x):
            return mx.mean(self.gla(x))

    gla_tm = TestGLAModel()
    mx.eval(gla_tm.parameters())

    def gla_test_loss(m, x):
        return m(x)

    gfn = nn.value_and_grad(gla_tm, gla_test_loss)
    x = mx.random.normal((1, 32, 512))
    lv, g = gfn(gla_tm, x)
    mx.eval(lv, g)
    print(f"  GLA gradient flow OK: loss={lv.item():.4f} ✓")

    # Check gradient exists for key params
    gla_grads = g.get("gla", {})
    has_gate_grad = "gate_proj" in gla_grads and "weight" in gla_grads["gate_proj"]
    has_q_grad = "q_proj" in gla_grads
    print(f"  Gate gradient: {'✓' if has_gate_grad else '✗'}")
    print(f"  Q projection gradient: {'✓' if has_q_grad else '✗'}")

    print("\nattention.py self-test: all ok ✓")
