"""v14 Attention — Stride-Stack at d=1280.

Holographic lens architecture: each stride is a lens pointed at a
different scale of the context. O(L×W) per stride, ternary, CPU-runnable.

Two layer types (same as v13, evolved for d=1280):
  SingleStrideAttention — composition (KIBC dispatch)
  GatedLinearAttention  — retrieval (M kernel substrate)

11 strides: (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
  s1-s8:    composition (fine → local)
  s16-s128: retrieval (phrase → paragraph)
  s256-s1024: composition (document scale)

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


# ══════════════════════════════════════════════════════════════════════
# § 1  SingleStrideAttention — composition layers
# ══════════════════════════════════════════════════════════════════════


class SingleStrideAttention(nn.Module):
    """Ternary attention at a single stride and window.

    Each head attends to W past positions at the given stride:
      stride=1:  positions [i, i-1, ..., i-W+1]
      stride=8:  positions [i, i-8, ..., i-8*(W-1)]

    Q/K/V/O are TernaryLinear (base plates from teacher extraction).
    Sparse gather, O(L×W) not O(L²).

    Learnable decay per-head: -α·ln(stride·w + 1).
    Algedonic modulation scales the decay (sharper/broader attention).
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 1,
        window: int = 8,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        decay_init_alpha: float = 1.18,
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

        # Learnable decay per head
        self.decay_alpha = mx.full((n_heads,), decay_init_alpha)

        # Pre-compute log-distance structure
        w_pos = mx.arange(window, dtype=mx.float32)
        self._log_distances = mx.log(stride * w_pos + 1.0)

    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
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

        Q_r = Q.transpose(0, 2, 1, 3)
        K_r = K_gathered.transpose(0, 3, 1, 2, 4)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale

        # Learnable decay
        effective_alpha = self.decay_alpha * decay_modulation
        decay_bias = -(effective_alpha[:, None] * self._log_distances[None, :])
        attn = attn + decay_bias[None, :, None, :]

        valid_mask = valid[None, None, :, :]
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
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
                    decay_init_alpha=cfg.decay_init_alpha,
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
# § 4  Self-test
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
