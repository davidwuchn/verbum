"""v15 StrideStackVSM — S1 operational unit in the tree of VSMs.

Each stack owns a FibonacciStrideStack (19 strides) + shared FFN plates +
S3 gates.  Bottom-up algedonic: C feeds A.

v15 vs v14:
  - FibonacciStrideStack replaces StrideStack (Fibonacci strides, ±2 neighbors)
  - V15Config replaces V14Config
  - Band topology is asymmetric: band 0 has 4 strides, band 1 has 6,
    band 2 has 4, band 3 has 5. n_passes = 4 for each of A and C.
  - All strides are composition (FibonacciStrideAttention) — no GLA.
  - Shared infrastructure (ternary, components, kernel) imported from v14.

License: MIT
"""

from __future__ import annotations

import sys
import os

# ── Path setup: v15 first, then v14 for shared infrastructure ────────
_V15_DIR = os.path.dirname(os.path.abspath(__file__))
_V14_DIR = os.path.join(_V15_DIR, "..", "v14")
# Insert v15 at position 0, v14 at position 1 (v15 takes priority for config/attention)
if _V15_DIR not in sys.path:
    sys.path.insert(0, _V15_DIR)
if _V14_DIR not in sys.path:
    sys.path.insert(1, _V14_DIR)

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V15Config
from attention import FibonacciStrideStack
from ternary import TernaryLinear
from components import S3Ternary, S2Coordinator, AlgedonicAlert


class StrideStackVSM(nn.Module):
    """S1 operational unit — one Fibonacci-stride-stack in the tree.

    Data flow:
      For each pass (determined by stride bands):
        1. FibonacciStrideStack(x, band, reverse) — attention at active strides
        2. FFN — shared plates, per-stack beams (SwiGLU)
        3. S3 gate — modulate delta contribution
      After all passes:
        4. Compute algedonic health
        5. Return output + algedonic summary

    v15: band 1 has 6 strides (phrase binding, gap-fill zone) vs v14's 4.
    This is the heart of the attention mechanism — n_passes=4 for both stacks,
    but the stride counts within each band differ.
    """

    def __init__(
        self,
        cfg: V15Config,
        bands: tuple[tuple[int, int], ...],
        ffn_key_plate: TernaryLinear,
        ffn_gate_plate: TernaryLinear,
        ffn_value_plate: TernaryLinear,
        stride_stack: FibonacciStrideStack,
        is_descending: bool = False,
    ):
        super().__init__()
        self.cfg = cfg
        self.bands = bands
        self.is_descending = is_descending
        self.n_passes = len(bands)
        d = cfg.d_model

        # ── Attention (shared stride stack — NOT owned) ───────────
        # The FibonacciStrideStack is shared across all StrideStackVSMs.
        # Each stack calls different bands on the same layers.
        # Stored as _stride_stack (private) to prevent MLX from traversing it
        # as a child module (which would duplicate parameters in tree_flatten).
        # The shared_stride_stack is owned by V15Model and appears once.
        self._stride_stack = stride_stack

        # ── FFN (shared plates, per-stack beams) ──────────────────
        self.ffn_key_plate = ffn_key_plate
        self.ffn_gate_plate = ffn_gate_plate
        self.ffn_value_plate = ffn_value_plate
        self.ffn_norm = nn.RMSNorm(d)
        self.ffn_scale = mx.ones((d,))
        self.ffn_bias = mx.zeros((d,))

        # ── S3 gates (per-pass) ────────────────────────────────────
        self.s3_gates = [S3Ternary(d) for _ in range(self.n_passes)]

        # ── S2 (inter-pass direction) ──────────────────────────────
        n_transitions = max(self.n_passes - 1, 0)
        self.s2 = S2Coordinator(d, n_transitions=n_transitions)

        # ── Algedonic (health metrics) ─────────────────────────────
        alg_input_dim = 4 * self.n_passes
        self.algedonic = AlgedonicAlert(n_passes=self.n_passes, input_dim=alg_input_dim)

        # ── Algedonic summary → controller ─────────────────────────
        alg_dim = cfg.alg_dim
        alg_proj_in = self.n_passes + alg_input_dim
        alg_proj_padded = ((alg_proj_in + 15) // 16) * 16
        self._alg_proj_padded = alg_proj_padded
        self.alg_summary_proj = nn.Linear(alg_proj_padded, alg_dim)

        # ── Algedonic modulation (from downstream) ─────────────────
        mod_input_padded = ((alg_dim + 15) // 16) * 16
        self._mod_input_padded = mod_input_padded
        self.alg_to_ffn = nn.Linear(mod_input_padded, 1)
        self.alg_to_gate = nn.Linear(mod_input_padded, 1)

    def _modulation(self, downstream_alg: Optional[mx.array]) -> tuple:
        if downstream_alg is None:
            return 1.0, 1.0
        alg = downstream_alg
        if alg.shape[0] < self._mod_input_padded:
            alg = mx.concatenate([alg, mx.zeros((self._mod_input_padded - alg.shape[0],))])
        ffn_mod = mx.sigmoid(self.alg_to_ffn(alg).reshape(())) * 2.0
        gate_mod = mx.sigmoid(self.alg_to_gate(alg).reshape(())) * 2.0
        return ffn_mod, gate_mod

    def __call__(
        self,
        x: mx.array,
        downstream_alg: Optional[mx.array] = None,
    ) -> tuple[mx.array, mx.array, list[mx.array], list[mx.array]]:
        """Run stack: attention + FFN per pass, S3 gated.

        Returns:
            x:              (B, L, d) output
            alg_summary:    (alg_dim,) health for controller
            pass_deltas:    list of (B, L, d) per-pass deltas (for S5Reweight)
            s3_gate_values: list of scalar gates per pass
        """
        ffn_mod, gate_mod = self._modulation(downstream_alg)

        raw_deltas = []
        pass_deltas = []
        s3_gate_values = []
        prev_delta = None

        for local_idx, band in enumerate(self.bands):
            x_before = x

            # Fibonacci stride-stack pass (±2 neighbor gathering)
            x = self._stride_stack(x, stride_range=band, reverse=self.is_descending)

            # FFN (SwiGLU with shared plates)
            ffn_in = self.ffn_norm(x)
            ffn_gate = nn.silu(self.ffn_gate_plate(ffn_in))
            ffn_key = self.ffn_key_plate(ffn_in)
            ffn_product = mx.clip(ffn_gate * ffn_key, -100.0, 100.0)
            ffn_out = self.ffn_value_plate(ffn_product)
            ffn_out = (ffn_out * self.ffn_scale + self.ffn_bias) * ffn_mod
            x = x + ffn_out

            raw_delta = x - x_before

            # S3 gate
            gate = self.s3_gates[local_idx](raw_delta) * gate_mod
            x = x_before + gate * raw_delta

            pass_delta = x - x_before
            raw_deltas.append(raw_delta)
            pass_deltas.append(pass_delta)
            s3_gate_values.append(gate)

            # S2 direction
            if local_idx < self.n_passes - 1:
                coherence = (S2Coordinator.coherence_factor(prev_delta, pass_delta)
                             if prev_delta is not None else mx.array(1.0))
                dir_signal = self.s2.direction_signal(pass_delta, local_idx)
                x = x + dir_signal * coherence

            prev_delta = pass_delta

        # Algedonic health
        metrics = self.algedonic.compute_metrics(s3_gate_values, pass_deltas, raw_deltas)
        alarm_factors = self.algedonic(metrics)

        summary_in = mx.concatenate([alarm_factors, metrics])
        if summary_in.shape[0] < self._alg_proj_padded:
            summary_in = mx.concatenate([
                summary_in, mx.zeros((self._alg_proj_padded - summary_in.shape[0],))])
        alg_summary = mx.tanh(self.alg_summary_proj(summary_in))

        return x, alg_summary, pass_deltas, s3_gate_values


class AlgedonicCombiner(nn.Module):
    """Combine multiple algedonic signals (bottom-up feedback).

    Stack A receives from C. Learns to merge multiple signals.
    Identical to v14 — algedonic topology is architecture-independent.
    """

    def __init__(self, n_sources: int, alg_dim: int = 32):
        super().__init__()
        in_dim = n_sources * alg_dim
        in_padded = ((in_dim + 15) // 16) * 16
        self._in_padded = in_padded
        self.combine_proj = nn.Linear(in_padded, alg_dim)

    def __call__(self, *signals: mx.array) -> mx.array:
        combined = mx.concatenate(list(signals))
        if combined.shape[0] < self._in_padded:
            combined = mx.concatenate([
                combined, mx.zeros((self._in_padded - combined.shape[0],))])
        return mx.tanh(self.combine_proj(combined))


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v15 stack_vsm.py self-test")
    print("=" * 60)

    cfg = V15Config()
    d = cfg.d_model

    print(f"\nConfig:")
    print(f"  N_STRIDES={cfg.n_strides}  strides={cfg.strides}")
    print(f"  stack_a_bands={cfg.stack_a_bands}")
    print(f"  stack_c_bands={cfg.stack_c_bands}")
    print(f"  Band sizes: {[b[1]-b[0] for b in cfg.stack_a_bands]}")

    # Shared FFN plates
    ffn_key = TernaryLinear(d, cfg.d_ff, pre_norm=False)
    ffn_gate = TernaryLinear(d, cfg.d_ff, pre_norm=False)
    ffn_val = TernaryLinear(cfg.d_ff, d, pre_norm=False)

    # Shared Fibonacci stride stack
    shared_ss = FibonacciStrideStack(cfg)
    print(f"\n  FibonacciStrideStack: {len(shared_ss.layers)} layers")
    n_comp = sum(1 for t in shared_ss._layer_types if t == "comp")
    n_ret = sum(1 for t in shared_ss._layer_types if t == "ret")
    print(f"    composition={n_comp}, retrieval={n_ret}")

    # Stack A (ascending)
    n_a = len(cfg.stack_a_bands)
    print(f"\nStack A (ascending, {n_a} passes, bands {cfg.stack_a_bands})...")
    stack_a = StrideStackVSM(cfg, cfg.stack_a_bands, ffn_key, ffn_gate, ffn_val, shared_ss)
    x = mx.random.normal((1, 32, d))
    out_a, alg_a, deltas_a, gates_a = stack_a(x)
    mx.eval(out_a, alg_a)
    assert out_a.shape == (1, 32, d), f"Bad shape: {out_a.shape}"
    assert len(deltas_a) == n_a, f"Expected {n_a} deltas, got {len(deltas_a)}"
    assert len(gates_a) == n_a
    print(f"  output: {out_a.shape}, alg: {alg_a.shape}, {n_a} deltas, {n_a} gates ✓")

    # Stack C (descending, separate FFN plates)
    ffn_key_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
    ffn_gate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
    ffn_val_c = TernaryLinear(cfg.d_ff, d, pre_norm=False)

    n_c = len(cfg.stack_c_bands)
    print(f"\nStack C (descending, {n_c} passes, bands {cfg.stack_c_bands})...")
    stack_c = StrideStackVSM(
        cfg, cfg.stack_c_bands, ffn_key_c, ffn_gate_c, ffn_val_c,
        shared_ss, is_descending=True,
    )
    out_c, alg_c, deltas_c, gates_c = stack_c(out_a)
    mx.eval(out_c, alg_c)
    assert len(deltas_c) == n_c
    print(f"  output: {out_c.shape}, alg: {alg_c.shape}, {n_c} deltas ✓")

    total = n_a + n_c
    band_sizes_a = [b[1] - b[0] for b in cfg.stack_a_bands]
    print(f"\n  Total passes: {total} (A={n_a}, C={n_c})")
    print(f"  A band sizes: {band_sizes_a}  (band 1 has 6 strides = phrase zone)")

    # Bottom-up algedonic: C→A
    print("\nBottom-up algedonic (C→A)...")
    combiner_a = AlgedonicCombiner(n_sources=1, alg_dim=cfg.alg_dim)
    combined_for_a = combiner_a(alg_c)
    mx.eval(combined_for_a)
    print(f"  combiner(C)→A: {combined_for_a.shape} ✓")

    # Second pass with feedback
    x2 = mx.random.normal((1, 32, d))
    out_a2, alg_a2, _, _ = stack_a(x2, downstream_alg=combined_for_a)
    out_c2, alg_c2, _, _ = stack_c(out_a2)
    mx.eval(out_c2)
    print(f"  Pass 2 with C→A feedback: {out_c2.shape} ✓")

    # Gradient
    print("\nGradient flow...")

    class TestGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.fk = TernaryLinear(d, cfg.d_ff, pre_norm=False)
            self.fg = TernaryLinear(d, cfg.d_ff, pre_norm=False)
            self.fv = TernaryLinear(cfg.d_ff, d, pre_norm=False)
            self.ss = FibonacciStrideStack(cfg)
            self.stack = StrideStackVSM(
                cfg, cfg.stack_a_bands, self.fk, self.fg, self.fv, self.ss,
            )

        def __call__(self, x):
            out, alg, _, _ = self.stack(x)
            return mx.mean(out) + mx.sum(alg)

    tg = TestGrad()
    mx.eval(tg.parameters())
    gfn = nn.value_and_grad(tg, lambda m, x: m(x))
    lv, g = gfn(tg, mx.random.normal((1, 16, d)))
    mx.eval(lv, g)
    print(f"  loss={lv.item():.4f} ✓")

    print("\n" + "=" * 60)
    print("v15 stack_vsm.py: all tests passed ✓")
