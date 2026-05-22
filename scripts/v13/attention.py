"""v13 Attention — StrideStack + GatedLinearAttention + HybridStrideStack.

V13 extends V12 to 11 power-of-2 strides (1..1024) with uniform 2× gaps.
V12 had a gap at the bottom (1→8) that killed short prompts; V13 fills
in strides 2 and 4 for full coverage down to individual tokens.

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

Stride layout (11 strides):
  s1(C),  s2(C),  s4(C),  s8(C),   s16(R),  s32(R),
  s64(R), s128(R), s256(C), s512(C), s1024(C)
                  ^^^^^^^^^^^^^^^^
                  retrieval (GLA) zone: phrase/sentence scales (s16–s128)

Fractal stride bands (MERA topology):
  L0↑: [0,4) → s1,  s2,   s4,   s8      fine→local
  L1↑: [2,6) → s4,  s8,   s16,  s32     local→phrase
  L2↑: [4,8) → s16, s32,  s64,  s128    phrase→paragraph
  L3:  [7,11)→ s128,s256,s512,  s1024   paragraph→document (apex)
  L2↓: [4,8) → s128,s64,  s32,  s16     paragraph→phrase (reversed)
  L1↓: [2,6) → s32, s16,  s8,   s4      phrase→local (reversed)
  L0↓: [0,4) → s8,  s4,   s2,   s1      local→fine (reversed)

HybridStrideStack:
  - Interleaves both layer types based on stride_is_retrieval config
  - Each stride gets exactly one layer (composition OR retrieval)
  - Shared across VSM passes via pass_idx + reverse flag (S5 coherence)

Design principle — SEPARATION ENABLES HOLOGRAPHY (session 096):
  Multiplexing functions into shared weight matrices forces magnitude
  dependence, breaking holographic storage. Evidence: Pythia's fused
  QKV (score 0.60) vs separate Q/K/V in Qwen3/SmolLM3 (score 0.92).

  Rule: every weight matrix encodes ONE function. That is the shape
  that lets gradient descent find the holographic solution.

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from config import V13Config
from ternary import TernaryLinear, TernaryMirror
from scan import parallel_scan_2d


# ══════════════════════════════════════════════════════════════════════
# SingleStrideAttention — composition layers
# ══════════════════════════════════════════════════════════════════════


class SingleStrideAttention(nn.Module):
    """Ternary attention at a single stride and window.

    Each head attends to W past positions at the given stride:
      stride=1:  positions [i, i-1, ..., i-W+1]       (word-level)
      stride=8:  positions [i, i-8, ..., i-8*(W-1)]   (phrase-level)

    Q/K/V/O are TernaryLinear. Sparse gather, O(L×W) not O(L²).

    Spiral bias: -α·ln(stride·w + 1) applied to attention logits.
    Larger w (further back) → more negative → geometric attention decay.
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

        # Per-feature beam biases on plate outputs (mini_holo_exp1: scale+bias > scale-only)
        # gamma inside TernaryLinear provides per-feature scale; these add per-feature bias.
        self.k_bias = mx.zeros((d_model,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

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
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

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

        return x + self.out_proj(out) + self.o_bias

    def combinator_forward(
        self,
        x: mx.array,
        combinator_mirrors: list,
        dispatch_weights: mx.array,
    ) -> mx.array:
        """Per-combinator beam angle via Q blending — the holographic read.

        Session 093: V(B) = V(C) at cos=1.000, Q(B)·Q(C) = 0.005.
        The plate (K,V) is shared. The beam (Q) is combinator-specific.

        Compute K,V once. For each combinator mirror, compute a different Q.
        Blend the Q vectors with dispatch weights. Run ONE attention pass.
        Apply shared O projection.

        Args:
            x: (B, L, d_model)
            combinator_mirrors: list of N TernaryMirror modules
            dispatch_weights: (B, L, N) — softmax weights (live)

        Returns: (B, L, d_model) with residual connection
        """
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W = self.window

        x_norm = self.norm(x)

        # Per-combinator Q via mirrors, blended with dispatch weights.
        Q_blended = mx.zeros((B, L, D))
        for i, mirror in enumerate(combinator_mirrors):
            q_in = mirror(x_norm)
            for m in self.q_mirrors:
                q_in = m(q_in)
            Q_i = self.q_proj(q_in)  # (B, L, D)
            Q_blended = Q_blended + dispatch_weights[..., i:i+1] * Q_i

        Q = Q_blended.reshape(B, L, H, Dh)

        # Shared K, V (the plate — computed once, beam bias applied)
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

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

        return x + self.out_proj(out) + self.o_bias


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

    Striding: positions are gathered at stride intervals, same as
    SingleStrideAttention. Memory accumulates over strided positions,
    giving scale-appropriate pattern matching:
      stride=16:  phrase-level pattern memory
      stride=32:  sentence-level pattern memory
      stride=64:  paragraph-level pattern memory
      stride=128: multi-paragraph pattern memory

    Instrumentation:
      _gate_values:    (B, L, H) — per-head write gate activity
      _memory_norms:   (H,) — Frobenius norm of memory per head
      _retrieval_norms:(B, L) — L2 norm of retrieval output
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

        # Per-feature beam biases on plate outputs (scale+bias > scale-only)
        self.k_bias = mx.zeros((n_heads * d_state,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        # Write gate: controls memory update rate.
        # Pad to multiple of 16 for TernaryLinear; take [..., :n_heads] + bias.
        # Separate bias: -0.5 → sigmoid(-0.5) ≈ 0.38 (conservative initial memory).
        self._n_heads_padded = ((n_heads + 15) // 16) * 16
        self.gate_proj = TernaryLinear(d_model, self._n_heads_padded, pre_norm=False)
        self.gate_bias = mx.full((n_heads,), -0.5)

        # Output projection
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

        # Instrumentation caches (populated each forward pass)
        self._gate_values = None     # (B, L, H)
        self._memory_norms = None    # (H,)
        self._retrieval_norms = None # (B, L)

    def __call__(self, x: mx.array) -> mx.array:
        """Forward pass with causal gated linear attention.

        For stride > 1: gather stride-sampled positions, run the scan
        over the short sequence (stride× cheaper), then broadcast each
        stride segment's accumulated state to all positions in that window.
        For stride=1: full recurrence over all positions.
        """
        B, L, D = x.shape
        H = self.n_heads
        Ds = self.d_state
        Dh = self.d_head
        stride = self.stride

        x_norm = self.norm(x)

        # Beam steering before Q projection
        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        q_raw = self.q_proj(q_in).reshape(B, L, H, Ds)
        k_raw = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Ds)
        v = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
        gate = mx.sigmoid(
            self.gate_proj(x_norm)[..., :H] + self.gate_bias
        )  # (B, L, H)

        # Non-negative activations for linear attention
        q = nn.elu(q_raw) + 1.0  # (B, L, H, Ds)
        k = nn.elu(k_raw) + 1.0  # (B, L, H, Ds)

        # Cache gate values for instrumentation
        self._gate_values = mx.stop_gradient(gate)

        # ── Stride-aware scan ─────────────────────────────────
        if stride == 1:
            # Full recurrence — all positions participate
            L_s = L

            kv_outer = k[:, :, :, :, None] * v[:, :, :, None, :]
            gate_expand = gate[:, :, :, None, None]
            gated_kv = gate_expand * kv_outer       # (B, L, H, Ds, Dh)
            retention = 1.0 - gate                   # (B, L, H)

            S_all = parallel_scan_2d(retention, gated_kv)  # (B, L, H, Ds, Dh)
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)
        else:
            # ── Gather stride positions ───────────────────────
            L_s = L // stride

            if L_s == 0:
                # Sequence shorter than stride — memory is zero → retrieval returns zero.
                output = mx.zeros((B, L, H, Dh))
            else:
                stride_idx = mx.arange(L_s) * stride  # (L_s,)

                k_s = k[:, stride_idx, :, :]          # (B, L_s, H, Ds)
                v_s = v[:, stride_idx, :, :]          # (B, L_s, H, Dh)
                gate_s = gate[:, stride_idx, :]       # (B, L_s, H)

                kv_outer_s = k_s[:, :, :, :, None] * v_s[:, :, :, None, :]
                gate_s_expand = gate_s[:, :, :, None, None]
                gated_kv_s = gate_s_expand * kv_outer_s   # (B, L_s, H, Ds, Dh)
                retention_s = 1.0 - gate_s                 # (B, L_s, H)

                # Parallel scan over short sequence (stride× cheaper)
                S_stride = parallel_scan_2d(retention_s, gated_kv_s)  # (B, L_s, H, Ds, Dh)

                # Broadcast: position i reads state at floor(i / stride)
                state_idx = mx.minimum(
                    mx.arange(L) // stride, L_s - 1)       # (L,)
                S_all = S_stride[:, state_idx, :, :, :]    # (B, L, H, Ds, Dh)

                output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)

        output = output.reshape(B, L, D)

        # Instrumentation: memory norms at final stride position
        if stride == 1:
            S_final = S_all[:, -1, :, :, :]
        elif L_s == 0:
            S_final = mx.zeros((B, H, Ds, Dh))
        else:
            S_final = S_stride[:, -1, :, :, :]
        S_norms = mx.sqrt(mx.sum(S_final * S_final, axis=(2, 3)) + 1e-8)  # (B, H)
        self._memory_norms = mx.stop_gradient(S_norms.mean(axis=0))  # (H,)

        out_norms = mx.sqrt(mx.sum(output * output, axis=-1) + 1e-8)  # (B, L)
        self._retrieval_norms = mx.stop_gradient(out_norms)

        return x + self.dropout(self.out_proj(output)) + self.o_bias


# ══════════════════════════════════════════════════════════════════════
# StrideStack — 11-stride hybrid stack (V13: updated from 9 strides)
# ══════════════════════════════════════════════════════════════════════


class StrideStack(nn.Module):
    """Hybrid 11-stride stack: composition (SSA) + retrieval (GLA) layers.

    V13 key changes from V12:
      - 11 strides:  (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
      - stride_is_retrieval: (F,F,F,F, T,T,T,T, F,F,F)
        middle 4 strides (s16-s128) are GLA retrieval layers.

    Fractal stride bands from config.stride_band_ranges select active
    strides per pass (MERA topology). TernaryMirror per pass steers
    Q-beam direction.

    __call__ signature:
        x:           (B, T, d_model)
        pass_idx:    which pass (0–6) — used for Q-mirror selection
        stride_range:(start, end) stride index range from stride_band_ranges
        reverse:     True for descending passes (coarse→fine ordering)

    For each active stride:
      1. (implicit in layer __call__) normalise, compute Q/K/V
      2. Apply the layer (SSA or GLA)
      3. Accumulate via residual connection (handled inside each layer)

    Shared across all VSM passes — S5 coherence.
    """

    def __init__(
        self,
        d_model: int,
        strides: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024),
        stride_is_retrieval: tuple[bool, ...] = (
            False, False, False, False, True, True, True, True, False, False, False,
        ),
        window: int = 8,
        n_heads: int = 8,
        d_state: int = 64,
        dropout: float = 0.1,
        alpha: float | None = None,
        n_q_mirrors: int = 0,
        n_combinators: int = 8,
    ):
        super().__init__()
        assert len(strides) == len(stride_is_retrieval), (
            f"strides length ({len(strides)}) must match "
            f"stride_is_retrieval ({len(stride_is_retrieval)})"
        )
        self.d_model = d_model
        self.strides = strides
        self.stride_is_retrieval = stride_is_retrieval
        self.window = window
        self.n_combinators = n_combinators

        # Per-combinator beam mirrors (shared across all strides in this stack)
        # Used when dispatch_weights are provided to combinator_forward.
        self.combinator_mirrors = [TernaryMirror(d_model) for _ in range(n_combinators)]

        # Build layers: one per stride, type determined by stride_is_retrieval
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

        # Instrumentation caches (populated each forward pass)
        self._retrieval_gate_means = {}
        self._retrieval_memory_norms = {}

    def __call__(
        self,
        x: mx.array,
        pass_idx: int = 0,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        """Run active stride layers for this pass.

        Args:
            x:            (B, T, d_model) input hidden state
            pass_idx:     which hourglass pass (0–6), reserved for future
                          per-pass Q-mirror steering (currently unused beyond
                          being available for dispatch routing)
            stride_range: (start, end) from config.stride_band_ranges,
                          selecting which stride indices to activate.
                          None = all strides.
            reverse:      True for descending passes — runs active strides
                          in reversed order (coarse→fine)

        Returns:
            (B, T, d_model) — accumulated residual output
        """
        # Determine active stride indices
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
                    self._retrieval_gate_means[stride] = float(
                        mx.mean(layer._gate_values).item()
                    )
                if layer._memory_norms is not None:
                    self._retrieval_memory_norms[stride] = layer._memory_norms

        return x

    def combinator_forward(
        self,
        x: mx.array,
        dispatch_weights: mx.array,
        pass_idx: int = 0,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        """Per-combinator beam angle through shared stride layers.

        Composition layers use combinator_forward (per-combinator Q blending).
        Retrieval layers (GLA) always use the plain forward pass (GLA does
        not support per-combinator dispatch by design).

        Args:
            x:               (B, L, d_model)
            dispatch_weights:(B, L, n_combinators) — softmax weights
            pass_idx:        hourglass pass index (0–6)
            stride_range:    (start, end) stride index range
            reverse:         True for descending passes

        Returns:
            (B, L, d_model)
        """
        if stride_range is not None:
            start, end = stride_range
            indices = list(range(start, min(end, len(self.layers))))
        else:
            indices = list(range(len(self.layers)))

        if reverse:
            indices = list(reversed(indices))

        self._retrieval_gate_means = {}
        self._retrieval_memory_norms = {}

        for i in indices:
            if self._layer_types[i] == "comp":
                x = self.layers[i].combinator_forward(
                    x, self.combinator_mirrors, dispatch_weights
                )
            else:
                # GLA retrieval: always plain forward
                x = self.layers[i](x)

            if self._layer_types[i] == "ret":
                layer = self.layers[i]
                stride = self.strides[i]
                if layer._gate_values is not None:
                    self._retrieval_gate_means[stride] = float(
                        mx.mean(layer._gate_values).item()
                    )
                if layer._memory_norms is not None:
                    self._retrieval_memory_norms[stride] = layer._memory_norms

        return x

    def describe(self) -> str:
        parts = []
        for s, lt in zip(self.strides, self._layer_types):
            parts.append(f"s{s}({'R' if lt == 'ret' else 'C'})")
        return f"StrideStack({' → '.join(parts)}, W={self.window})"

    @classmethod
    def from_config(cls, cfg: V13Config) -> "StrideStack":
        """Construct a StrideStack from a V13Config."""
        return cls(
            d_model=cfg.d_model,
            strides=cfg.strides,
            stride_is_retrieval=cfg.stride_is_retrieval,
            window=cfg.window,
            n_heads=cfg.n_heads,
            d_state=cfg.d_state,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
            n_q_mirrors=cfg.n_q_mirrors if cfg.use_q_mirrors else 0,
            n_combinators=cfg.n_combinators,
        )


# ══════════════════════════════════════════════════════════════════════
# HybridStrideStack — StrideStack wrapper with GLA interleaving
# ══════════════════════════════════════════════════════════════════════


class HybridStrideStack(nn.Module):
    """Wrapper around StrideStack with explicit GLA interleaving interface.

    Provides a pass-indexed API aligned with the 7-pass hourglass:
      pass 0 (L0↑): stride_range=(0,4),  reverse=False
      pass 1 (L1↑): stride_range=(2,6),  reverse=False
      pass 2 (L2↑): stride_range=(4,8),  reverse=False
      pass 3 (L3):  stride_range=(7,11), reverse=False  ← apex
      pass 4 (L2↓): stride_range=(4,8),  reverse=True
      pass 5 (L1↓): stride_range=(2,6),  reverse=True
      pass 6 (L0↓): stride_range=(0,4),  reverse=True

    V13 layout (11 strides):
      Indices: 0=s1,  1=s2,  2=s4,  3=s8,  4=s16, 5=s32,
               6=s64, 7=s128, 8=s256, 9=s512, 10=s1024
      Types:   C      C      C      C      R      R
               R      R      C      C      C

    This is the primary interface used by the model's forward method.
    The inner StrideStack is shared across all passes (S5 coherence).

    Instrumentation is forwarded from the inner StrideStack after each call.
    """

    def __init__(
        self,
        d_model: int,
        strides: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024),
        stride_is_retrieval: tuple[bool, ...] = (
            False, False, False, False, True, True, True, True, False, False, False,
        ),
        window: int = 8,
        n_heads: int = 8,
        d_state: int = 64,
        dropout: float = 0.1,
        alpha: float | None = None,
        n_q_mirrors: int = 0,
        n_combinators: int = 8,
        stride_band_ranges: tuple[tuple[int, int], ...] | None = None,
    ):
        super().__init__()
        self.stride_band_ranges = stride_band_ranges
        self.n_passes = len(stride_band_ranges) if stride_band_ranges else 7

        # Number of descending passes: passes ≥ ceil(n_passes/2) are descending.
        # For 7-pass hourglass: passes 4,5,6 are descending.
        self._n_asc = (self.n_passes + 1) // 2   # 4 (including apex)
        # pass 0..n_asc-1 ascending; pass n_asc..n_passes-1 descending
        # pass n_asc-1 = apex (no reversal)
        # pass n_asc..n_passes-1: descending (reverse=True if desc_stride_reverse)
        # For 7 passes: asc=[0,1,2,3(apex)], desc=[4,5,6]

        # The single shared StrideStack (S5 coherence — shared across all passes)
        self.stack = StrideStack(
            d_model=d_model,
            strides=strides,
            stride_is_retrieval=stride_is_retrieval,
            window=window,
            n_heads=n_heads,
            d_state=d_state,
            dropout=dropout,
            alpha=alpha,
            n_q_mirrors=n_q_mirrors,
            n_combinators=n_combinators,
        )

        # Expose layer types and strides for describe()
        self.strides = strides
        self.stride_is_retrieval = stride_is_retrieval

    def __call__(
        self,
        x: mx.array,
        pass_idx: int = 0,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
        dispatch_weights: mx.array | None = None,
    ) -> mx.array:
        """Run one hourglass pass through the shared StrideStack.

        Args:
            x:                (B, T, d_model)
            pass_idx:         which pass (0–6)
            stride_range:     (start, end) from config.stride_band_ranges;
                              if None, uses stride_band_ranges[pass_idx] if available
            reverse:          True for descending passes
            dispatch_weights: (B, T, n_combinators) optional; when provided,
                              composition layers use per-combinator beam angles

        Returns:
            (B, T, d_model) — residual-accumulated output
        """
        # Resolve stride_range from pass_idx if not explicitly given
        if stride_range is None and self.stride_band_ranges is not None:
            if pass_idx < len(self.stride_band_ranges):
                stride_range = self.stride_band_ranges[pass_idx]

        if dispatch_weights is not None:
            return self.stack.combinator_forward(
                x,
                dispatch_weights=dispatch_weights,
                pass_idx=pass_idx,
                stride_range=stride_range,
                reverse=reverse,
            )
        else:
            return self.stack(
                x,
                pass_idx=pass_idx,
                stride_range=stride_range,
                reverse=reverse,
            )

    @property
    def _retrieval_gate_means(self):
        return self.stack._retrieval_gate_means

    @property
    def _retrieval_memory_norms(self):
        return self.stack._retrieval_memory_norms

    @property
    def _layer_types(self):
        return self.stack._layer_types

    def describe(self) -> str:
        return f"HybridStrideStack(wraps {self.stack.describe()})"

    @classmethod
    def from_config(cls, cfg: V13Config) -> "HybridStrideStack":
        """Construct a HybridStrideStack from a V13Config."""
        return cls(
            d_model=cfg.d_model,
            strides=cfg.strides,
            stride_is_retrieval=cfg.stride_is_retrieval,
            window=cfg.window,
            n_heads=cfg.n_heads,
            d_state=cfg.d_state,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
            n_q_mirrors=cfg.n_q_mirrors if cfg.use_q_mirrors else 0,
            n_combinators=cfg.n_combinators,
            stride_band_ranges=cfg.stride_band_ranges,
        )


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("V13 attention.py self-test")
    print("=" * 60)

    # ── SingleStrideAttention ─────────────────────────────────
    print("\nTesting SingleStrideAttention...")
    for stride in (1, 2, 4, 8):
        ssa = SingleStrideAttention(
            d_model=512, stride=stride, window=8, n_heads=8, alpha=1.18
        )
        x = mx.random.normal((1, 64, 512))
        y = ssa(x)
        mx.eval(y)
        assert y.shape == (1, 64, 512), f"Expected (1, 64, 512), got {y.shape}"
        print(f"  SSA(s={stride}): {x.shape} → {y.shape} ✓")

    # ── GatedLinearAttention ──────────────────────────────────
    print("\nTesting GatedLinearAttention...")
    for stride in (16, 32, 64, 128):
        gla = GatedLinearAttention(d_model=512, stride=stride, d_state=64, n_heads=8)
        x = mx.random.normal((1, 256, 512))
        y = gla(x)
        mx.eval(y)
        assert y.shape == (1, 256, 512), f"Expected (1, 256, 512), got {y.shape}"
        assert gla._gate_values is not None
        assert gla._gate_values.shape == (1, 256, 8)
        assert gla._memory_norms is not None
        assert gla._memory_norms.shape == (8,)
        gate_mean = float(mx.mean(gla._gate_values).item())
        print(f"  GLA(s={stride}): shape ✓  gate_mean={gate_mean:.3f}")

    # Sequence shorter than stride
    print("\nTesting GLA with short sequence (seq < stride)...")
    gla_big = GatedLinearAttention(d_model=512, stride=1024, d_state=64, n_heads=8)
    x_short = mx.random.normal((1, 64, 512))
    y_short = gla_big(x_short)
    mx.eval(y_short)
    assert y_short.shape == (1, 64, 512)
    print(f"  GLA(s=1024, L=64): {y_short.shape} ✓  (L < stride handled correctly)")

    # ── StrideStack (11 strides, hybrid) ──────────────────────
    print("\nTesting StrideStack (11 strides)...")
    strides_v13 = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
    stride_is_ret_v13 = (False, False, False, False, True, True, True, True, False, False, False)

    ss = StrideStack(
        d_model=512,
        strides=strides_v13,
        stride_is_retrieval=stride_is_ret_v13,
        window=8, n_heads=8, d_state=64, alpha=1.18,
    )
    assert len(ss.layers) == 11
    assert ss._layer_types == [
        "comp", "comp", "comp", "comp",
        "ret",  "ret",  "ret",  "ret",
        "comp", "comp", "comp",
    ]

    x = mx.random.normal((1, 256, 512))

    # Test all 7 hourglass pass bands
    band_ranges = (
        (0, 4), (2, 6), (4, 8), (7, 11), (4, 8), (2, 6), (0, 4)
    )
    for p_idx, (start, end) in enumerate(band_ranges):
        is_desc = p_idx >= 4
        y = ss(x, pass_idx=p_idx, stride_range=(start, end), reverse=is_desc)
        mx.eval(y)
        assert y.shape == (1, 256, 512), f"Pass {p_idx}: expected (1, 256, 512), got {y.shape}"
        n_active = end - start
        print(f"  StrideStack pass {p_idx} [{start},{end}) rev={is_desc}: {y.shape} ({n_active} strides) ✓")

    # Full stack (no range)
    y_full = ss(x)
    mx.eval(y_full)
    assert y_full.shape == (1, 256, 512)
    print(f"  StrideStack full (11 strides): ✓")
    print(f"  {ss.describe()}")

    # ── StrideStack from_config ───────────────────────────────
    print("\nTesting StrideStack.from_config...")
    cfg = V13Config()
    ss_cfg = StrideStack.from_config(cfg)
    assert len(ss_cfg.layers) == 11
    x = mx.random.normal((1, 128, 512))
    y = ss_cfg(x, pass_idx=0, stride_range=(0, 4))
    mx.eval(y)
    assert y.shape == (1, 128, 512)
    print(f"  StrideStack.from_config: ✓")

    # ── HybridStrideStack ─────────────────────────────────────
    print("\nTesting HybridStrideStack...")
    hss = HybridStrideStack(
        d_model=512,
        strides=strides_v13,
        stride_is_retrieval=stride_is_ret_v13,
        window=8, n_heads=8, d_state=64, alpha=1.18,
        stride_band_ranges=band_ranges,
    )

    x = mx.random.normal((1, 256, 512))
    for p_idx in range(7):
        is_desc = p_idx >= 4
        y = hss(x, pass_idx=p_idx, reverse=is_desc)
        mx.eval(y)
        assert y.shape == (1, 256, 512)
        print(f"  HybridStrideStack pass {p_idx} (rev={is_desc}): {y.shape} ✓")

    # Check instrumentation forwarding
    assert isinstance(hss._retrieval_gate_means, dict)
    assert isinstance(hss._layer_types, list)
    assert len(hss._layer_types) == 11
    print(f"  Layer types: {hss._layer_types}")
    print(f"  {hss.describe()}")

    # ── HybridStrideStack.from_config ─────────────────────────
    print("\nTesting HybridStrideStack.from_config...")
    hss_cfg = HybridStrideStack.from_config(cfg)
    x = mx.random.normal((1, 128, 512))
    for p_idx in range(cfg.n_passes):
        is_desc = p_idx >= (cfg.n_passes + 1) // 2
        y = hss_cfg(x, pass_idx=p_idx, reverse=is_desc)
        mx.eval(y)
        assert y.shape == (1, 128, 512)
    print(f"  HybridStrideStack.from_config: all {cfg.n_passes} passes ✓")

    # ── Retrieval instrumentation detail ──────────────────────
    print("\nChecking retrieval instrumentation (pass 2: s16, s32, s64, s128)...")
    x = mx.random.normal((1, 256, 512))
    y = hss(x, pass_idx=2)  # L2↑: [4,8) → s16, s32, s64, s128
    mx.eval(y)
    print(f"  Retrieval gate means: {hss._retrieval_gate_means}")
    for stride, norms in hss._retrieval_memory_norms.items():
        mx.eval(norms)
        print(f"  s{stride} memory norm mean: {float(mx.mean(norms).item()):.3f}")

    # ── Gradient flow ─────────────────────────────────────────
    print("\nTesting gradient flow through StrideStack...")

    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = StrideStack(
                d_model=512,
                strides=(1, 2, 4, 8, 16, 32),
                stride_is_retrieval=(False, False, False, False, True, True),
                window=8, n_heads=8, d_state=64, alpha=1.18,
            )
        def __call__(self, x):
            return mx.mean(self.stack(x, pass_idx=0, stride_range=(0, 4)))

    model = TestModel()
    mx.eval(model.parameters())

    def loss_fn(m, x):
        return m(x)

    gfn = nn.value_and_grad(model, loss_fn)
    x_test = mx.random.normal((1, 32, 512))
    lv, g = gfn(model, x_test)
    mx.eval(lv, g)
    print(f"  Gradient flow OK: loss={lv.item():.4f} ✓")

    print("\n" + "=" * 60)
    print("attention.py self-test: all OK ✓")
