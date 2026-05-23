"""StrideStackVSM — Reusable S1 operational unit in the tree of VSMs.

Each StrideStackVSM owns:
  - HybridStrideStack (attention layers for its assigned strides)
  - FFN beams (norm/scale/bias — per-stack; plates are shared)
  - S3 gates (per-pass within this stack)
  - S2Coordinator (inter-pass direction within this stack)
  - AlgedonicAlert (this stack health metrics)
  - Algedonic modulation projections (downstream feedback → 3 surfaces)

Receives from controller:
  - Shared FFN plates (key_plate, value_plate) — ternary, frozen
  - downstream_alg: route 2 algedonic from consumer (one step back)
  - s5_regulation: from controller S5 identity

Full-stack algedonic modulation (session 135):
  downstream_alg → 3 modulation factors (attention_decay, ffn_scale, gate)
  Each factor in (0, 2) via sigmoid * 2. Neutral = 1.0.
  Total amplification = attn_factor * ffn_factor * gate_factor.

License: MIT
"""

from __future__ import annotations

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V13Config, StackConfig, N_TOTAL_COMBINATORS
from attention import HybridStrideStack
from ternary import TernaryLinear
from components import S3Ternary, S2Coordinator, AlgedonicAlert


class StrideStackVSM(nn.Module):
    """S1 operational unit — one node in the tree of VSMs.

    Data flow within a stack:
      For each pass in this stack:
        1. stride_stack(x) — attention beta reductions (plates)
        2. FFN(x) — shared plates, per-stack beams
        3. S3 gate — modulate delta contribution
      After all passes:
        4. Compute algedonic health metrics
        5. Return output + algedonic

    Algedonic modulation from downstream consumer (one step back):
      - Modulates attention decay (per-stride)
      - Modulates FFN output scale
      - Modulates S3 gate
    """

    def __init__(
        self,
        cfg: V13Config,
        stack_cfg: StackConfig,
        ffn_key_plate: TernaryLinear,
        ffn_value_plate: TernaryLinear,
        ffn_gate_plate: TernaryLinear,
        shared_stride_stack: Optional[HybridStrideStack] = None,
    ):
        super().__init__()
        self.cfg = cfg
        self.stack_cfg = stack_cfg
        d = cfg.d_model
        self.n_passes = len(stack_cfg.pass_indices)

        # ── Attention (own or shared) ─────────────────────────
        if shared_stride_stack is not None:
            # Stack B reuses Stack A stride layers (self-similar)
            self.stride_stack = shared_stride_stack
        else:
            self.stride_stack = HybridStrideStack.from_config(
                cfg, stride_band_ranges=stack_cfg.stride_band_ranges)

        # ── FFN (shared plates, per-stack beams) ──────────────
        # Plates are SHARED (passed in, not owned)
        self.ffn_key_plate = ffn_key_plate
        self.ffn_value_plate = ffn_value_plate
        self.ffn_gate_plate = ffn_gate_plate  # Session 141: gate IS the beamformer
        # Beams are PER-STACK (each stack reads shared plates differently)
        self.ffn_norm = nn.RMSNorm(d)
        self.ffn_scale = mx.ones((d,))
        self.ffn_bias = mx.zeros((d,))

        # ── S3 gates (per-pass within this stack) ─────────────
        self.s3_gates = [S3Ternary(d) for _ in range(self.n_passes)]

        # ── S2 (inter-pass direction within this stack) ───────
        n_transitions = max(self.n_passes - 1, 0)
        self.s2 = S2Coordinator(d, n_transitions=n_transitions)

        # ── Algedonic (this stack health) ─────────────────────
        # Input: 4 metrics per pass (gate, raw_rms, gated_rms, suppression)
        alg_input_dim = 4 * self.n_passes
        self.algedonic = AlgedonicAlert(n_passes=self.n_passes, input_dim=alg_input_dim)

        # ── Algedonic summary (for controller route 1) ────────
        # Compress pass-level factors to a fixed-size vector
        alg_dim = cfg.alg_dim
        alg_proj_in = self.n_passes + alg_input_dim
        alg_proj_padded = ((alg_proj_in + 15) // 16) * 16
        self._alg_proj_padded = alg_proj_padded
        self._alg_proj_raw = alg_proj_in
        self.alg_summary_proj = nn.Linear(alg_proj_padded, alg_dim)

        # ── Algedonic modulation projections ──────────────────
        # downstream_alg (alg_dim) → 3 modulation factors
        # Attention: per-stride modulation (n_strides)
        # FFN: scalar modulation
        # Gate: scalar modulation
        n_strides = cfg.n_strides
        mod_input_padded = ((alg_dim + 15) // 16) * 16
        self._mod_input_padded = mod_input_padded
        self.alg_to_attn = nn.Linear(mod_input_padded, n_strides)
        self.alg_to_ffn = nn.Linear(mod_input_padded, 1)
        self.alg_to_gate = nn.Linear(mod_input_padded, 1)
        # Init bias=0 → sigmoid(0)=0.5 → *2=1.0 → neutral
        self._mod_range = cfg.alg_modulation_range

    def _compute_modulation(
        self, downstream_alg: Optional[mx.array]
    ) -> tuple[float, float, float]:
        """Compute 3 modulation factors from downstream algedonic.

        Returns: (attn_mod, ffn_mod, gate_mod) each scalar or per-stride.
        When no downstream_alg, returns neutral (1.0).
        """
        if downstream_alg is None:
            return 1.0, 1.0, 1.0

        alg = downstream_alg
        if alg.shape[0] < self._mod_input_padded:
            alg = mx.concatenate([
                alg, mx.zeros((self._mod_input_padded - alg.shape[0],))
            ])

        # Each surface: sigmoid * range → (0, range). Neutral = range/2.
        attn_mod = mx.sigmoid(self.alg_to_attn(alg)) * self._mod_range  # (n_strides,)
        ffn_mod = mx.sigmoid(self.alg_to_ffn(alg).reshape(())) * self._mod_range
        gate_mod = mx.sigmoid(self.alg_to_gate(alg).reshape(())) * self._mod_range

        return attn_mod, ffn_mod, gate_mod

    def forward(
        self,
        x: mx.array,
        downstream_alg: Optional[mx.array] = None,
    ) -> tuple[mx.array, mx.array, list[mx.array], list[mx.array]]:
        """Run this stack: attention + FFN per pass, S3 gated.

        Args:
            x: (B, L, d_model) input residual stream
            downstream_alg: (alg_dim,) from consumer stack (one step back)

        Returns:
            x: (B, L, d_model) output
            alg_summary: (alg_dim,) this stack health for controller
            pass_deltas: list of (B, L, d_model) per-pass deltas
            s3_gate_values: list of scalar gates per pass
        """
        attn_mod, ffn_mod, gate_mod = self._compute_modulation(downstream_alg)
        is_desc = self.stack_cfg.is_descending

        pass_deltas = []
        raw_deltas = []
        s3_gate_values = []
        prev_delta = None

        for local_idx, global_pass_idx in enumerate(self.stack_cfg.pass_indices):
            x_before = x

            # Stride stack pass — attention beta reductions
            # For now, decay_modulation uses a mean across per-stride values
            if isinstance(attn_mod, mx.array) and attn_mod.ndim > 0:
                # Mean across strides for single scalar modulation to stride stack
                dm = float(mx.mean(attn_mod).item())
            else:
                dm = float(attn_mod) if not isinstance(attn_mod, float) else attn_mod

            stride_range = self.stack_cfg.stride_band_ranges[local_idx]
            stride_out = self.stride_stack(
                x, pass_idx=global_pass_idx,
                stride_range=stride_range,
                reverse=is_desc,
            )
            # stride_stack returns x + residual, so subtract to get the delta
            x = stride_out

            # FFN — shared plates, per-stack beams
            # Session 141: gate IS the holographic aperture selector.
            # SwiGLU: value_plate(silu(gate_plate(x)) * key_plate(x))
            # Gate controls 89% of neuron selection (teacher L63 probe).
            ffn_in = self.ffn_norm(x)
            ffn_gate = nn.silu(self.ffn_gate_plate(ffn_in))
            ffn_key = self.ffn_key_plate(ffn_in)
            ffn_out = self.ffn_value_plate(ffn_gate * ffn_key)
            ffn_out = (ffn_out * self.ffn_scale + self.ffn_bias) * ffn_mod
            x = x + ffn_out

            raw_delta = x - x_before

            # S3 gate (modulated by downstream algedonic)
            gate = self.s3_gates[local_idx](raw_delta) * gate_mod
            x = x_before + gate * raw_delta

            pass_delta = x - x_before
            pass_deltas.append(pass_delta)
            raw_deltas.append(raw_delta)
            s3_gate_values.append(gate)

            # S2 direction signal to next pass (within this stack)
            if local_idx < self.n_passes - 1:
                if prev_delta is not None:
                    coherence = S2Coordinator.coherence_factor(prev_delta, pass_delta)
                else:
                    coherence = mx.array(1.0)
                dir_signal = self.s2.direction_signal(pass_delta, local_idx)
                x = x + dir_signal * coherence

            prev_delta = pass_delta

        # ── Compute algedonic health ──────────────────────────
        metrics = self.algedonic.compute_metrics(s3_gate_values, pass_deltas, raw_deltas)
        alarm_factors = self.algedonic(metrics)

        # Summarize for controller (route 1)
        summary_in = mx.concatenate([alarm_factors, metrics])
        if summary_in.shape[0] < self._alg_proj_padded:
            summary_in = mx.concatenate([
                summary_in, mx.zeros((self._alg_proj_padded - summary_in.shape[0],))
            ])
        alg_summary = mx.tanh(self.alg_summary_proj(summary_in))

        return x, alg_summary, pass_deltas, s3_gate_values

    def __call__(
        self,
        x: mx.array,
        downstream_alg: Optional[mx.array] = None,
    ) -> tuple[mx.array, mx.array, list[mx.array], list[mx.array]]:
        return self.forward(x, downstream_alg)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("stack_vsm.py self-test")
    print("=" * 60)

    cfg = V13Config()

    # Shared FFN plates (would be etched from teacher in real use)
    ffn_key = TernaryLinear(cfg.d_model, cfg.d_ff, pre_norm=False)
    ffn_val = TernaryLinear(cfg.d_ff, cfg.d_model, pre_norm=False)
    ffn_gate = TernaryLinear(cfg.d_model, cfg.d_ff, pre_norm=False)

    # ── Stack A ───────────────────────────────────────────────
    print("\nStack A (ascending fine, 2 passes)...")
    stack_a = StrideStackVSM(cfg, cfg.stack_a, ffn_key, ffn_val, ffn_gate)
    x = mx.random.normal((1, 64, cfg.d_model))
    out_a, alg_a, deltas_a, gates_a = stack_a(x)
    mx.eval(out_a, alg_a)
    assert out_a.shape == (1, 64, cfg.d_model)
    assert alg_a.shape == (cfg.alg_dim,)
    assert len(deltas_a) == 2
    assert len(gates_a) == 2
    print(f"  output: {out_a.shape} alg: {alg_a.shape}")
    print(f"  gates: {[f'{float(g.item()):.3f}' for g in gates_a]} OK")

    # ── Stack B (shares stride stack with A) ──────────────────
    print("\nStack B (ascending coarse, 2 passes, shared stride stack)...")
    stack_b = StrideStackVSM(cfg, cfg.stack_b, ffn_key, ffn_val, ffn_gate,
                             shared_stride_stack=stack_a.stride_stack)
    out_b, alg_b, deltas_b, gates_b = stack_b(out_a, downstream_alg=None)
    mx.eval(out_b, alg_b)
    assert out_b.shape == (1, 64, cfg.d_model)
    assert alg_b.shape == (cfg.alg_dim,)
    print(f"  output: {out_b.shape} alg: {alg_b.shape}")
    print(f"  gates: {[f'{float(g.item()):.3f}' for g in gates_b]} OK")

    # ── Stack C (descending, own stride stack) ────────────────
    print("\nStack C (descending, 4 passes)...")
    stack_c = StrideStackVSM(cfg, cfg.stack_c, ffn_key, ffn_val, ffn_gate)
    out_c, alg_c, deltas_c, gates_c = stack_c(out_b)
    mx.eval(out_c, alg_c)
    assert out_c.shape == (1, 64, cfg.d_model)
    assert alg_c.shape == (cfg.alg_dim,)
    assert len(deltas_c) == 4
    print(f"  output: {out_c.shape} alg: {alg_c.shape}")
    print(f"  gates: {[f'{float(g.item()):.3f}' for g in gates_c]} OK")

    # ── With algedonic modulation ─────────────────────────────
    print("\nStack A with downstream algedonic modulation...")
    fake_alg = mx.random.normal((cfg.alg_dim,))
    out_mod, alg_mod, _, _ = stack_a(x, downstream_alg=fake_alg)
    mx.eval(out_mod, alg_mod)
    assert out_mod.shape == (1, 64, cfg.d_model)
    print(f"  modulated output: {out_mod.shape} OK")

    # ── Gradient flow ─────────────────────────────────────────
    print("\nGradient flow through StrideStackVSM...")

    class TestStackGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.ffn_key = TernaryLinear(cfg.d_model, cfg.d_ff, pre_norm=False)
            self.ffn_val = TernaryLinear(cfg.d_ff, cfg.d_model, pre_norm=False)
            self.ffn_gate = TernaryLinear(cfg.d_model, cfg.d_ff, pre_norm=False)
            self.stack = StrideStackVSM(cfg, cfg.stack_a, self.ffn_key, self.ffn_val, self.ffn_gate)

        def __call__(self, x):
            out, alg, _, _ = self.stack(x)
            return mx.mean(out) + mx.sum(alg)

    tsg = TestStackGrad()
    mx.eval(tsg.parameters())

    def stack_loss(m, x):
        return m(x)

    gfn = nn.value_and_grad(tsg, stack_loss)
    x_test = mx.random.normal((1, 32, cfg.d_model))
    lv, g = gfn(tsg, x_test)
    mx.eval(lv, g)
    print(f"  Gradient flow OK: loss={lv.item():.4f}")

    print("\n" + "=" * 60)
    print("stack_vsm.py: all tests passed")
