"""VSM control components — S4, S3, MetaS4, MetaS3 — MLX.

Ported from src/verbum/v6/components.py. Uses scripts/v10/ternary.py.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2,
preserving the same capacity as v6's complex ℂ^d_register registers without
requiring complex arithmetic in the autograd graph (MLX autograd doesn't
support mx.real/mx.imag + reshape in the backward pass).

Kept as fp32 (not ternary):
  - S3 write_gates (nn.Linear with bias, tiny, sigmoid-init)
  - S3 temperature and learned_bias (scalar parameters)
  - MetaS3 gate_proj (nn.Linear with bias, small)

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════════
# Helpers — register flattening (real-valued, no complex)
# ══════════════════════════════════════════════════════════════════════


def _flatten_registers(registers: list[mx.array]) -> mx.array:
    """Flatten list of real register vectors into one 1D vector."""
    return mx.concatenate(registers, axis=-1)


def _flatten_banks(banks: list[list[mx.array]]) -> mx.array:
    """Flatten all banks' registers into one 1D vector."""
    parts = []
    for bank in banks:
        parts.append(_flatten_registers(bank))
    return mx.concatenate(parts, axis=-1)


def _ternary_1d(proj: TernaryLinear, x: mx.array) -> mx.array:
    """Apply TernaryLinear to a 1D vector, working around MLX autograd
    requiring ≥2D input for quantized_matmul backward pass."""
    return proj(x.reshape(1, -1)).reshape(-1)


# ══════════════════════════════════════════════════════════════════════
# S4 — Intelligence (register-query cross-attention)
# ══════════════════════════════════════════════════════════════════════


class S4Ternary(nn.Module):
    """Register cross-attention: reads register banks, attends to residual,
    produces register updates.

    Real-valued registers (d_reg_real = d_register * 2 each).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,       # logical dimension (real dim = 2×)
        n_registers: int = 3,
        max_banks: int = 7,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2   # real-valued dimension per register
        self.n_registers = n_registers
        self.max_banks = max_banks
        self.scale = d_model ** -0.5

        max_q_dim = max_banks * n_registers * self.d_reg_real
        # Pad to multiple of 16 for TernaryLinear
        self._max_q_dim = ((max_q_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._max_q_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        summary_out = n_registers * self.d_reg_real
        self._summary_out_padded = ((summary_out + 15) // 16) * 16
        self._summary_out = summary_out
        self.summary_proj = TernaryLinear(d_model, self._summary_out_padded, pre_norm=False)

        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        banks: list[list[mx.array]],
        residual: mx.array,
    ) -> tuple[list[mx.array], mx.array]:
        B, L, D = residual.shape

        # Flatten all register banks into query input
        q_input = _flatten_banks(banks)
        # Pad to max
        if q_input.shape[0] < self._max_q_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._max_q_dim - q_input.shape[0],))
            ])

        # Query from register state (1D → 2D for autograd)
        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        # Standard attention: q (d_model,) @ k (B, L, d_model) → (B, L)
        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale  # (B, L)
        attn_weights = mx.softmax(attn, axis=-1)                  # (B, L)
        attn_weights = self.dropout(attn_weights)

        # Weighted sum → mean over batch
        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        summary = summary.mean(axis=0)                          # (d_model,)

        # Project to register update vectors (1D → 2D for autograd)
        updates_flat = _ternary_1d(self.summary_proj, summary)[:self._summary_out]

        updates = []
        for i in range(self.n_registers):
            start = i * self.d_reg_real
            end = start + self.d_reg_real
            updates.append(updates_flat[start:end])

        return updates, mx.stop_gradient(attn_weights)


# ══════════════════════════════════════════════════════════════════════
# S3 — Phase-Coherent Gating
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Phase-coherent control for a single level-pass.

    Scalar alignment gate based on register-delta direction match.
    Real-valued registers.
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_phases: int = 3,
        n_registers: int = 3,
        d_align: int | None = None,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2
        self.n_phases = n_phases
        self.n_registers = n_registers

        if d_align is None:
            d_align = d_model
        self.d_align = d_align

        reg_flat_dim = self.d_reg_real * n_registers
        self._reg_flat_dim = ((reg_flat_dim + 15) // 16) * 16

        # Alignment projections — ternary
        self.proj_align = [
            TernaryLinear(self._reg_flat_dim, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]
        self.proj_delta = [
            TernaryLinear(d_model, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]

        # Temperature and bias — fp32 scalars
        self.temperature = [mx.ones((1,)) for _ in range(n_phases)]
        self.learned_bias = [mx.zeros((1,)) for _ in range(n_phases)]

        # Register write projections — ternary
        d_reg_out = ((self.d_reg_real + 15) // 16) * 16
        self._d_reg_out = d_reg_out
        self.write_projs = [
            TernaryLinear(d_model, d_reg_out, pre_norm=False)
            for _ in range(n_phases * n_registers)
        ]

        # Write gates: kept as nn.Linear (has bias, tiny)
        # Bias init -2.0 → sigmoid(-2) ≈ 0.12
        self.write_gates = [
            nn.Linear(d_model, 1)
            for _ in range(n_phases * n_registers)
        ]
        for wg in self.write_gates:
            wg.bias = mx.full(wg.bias.shape, -2.0)

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

    def gate_phase(
        self,
        registers: list[mx.array],
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array, list[mx.array], mx.array, list[float]]:
        """Gate a phase's output using alignment-based scalar gate."""
        eps = 1e-8

        reg_flat = _flatten_registers(registers)
        # Pad to multiple of 16
        if reg_flat.shape[0] < self._reg_flat_dim:
            reg_flat = mx.concatenate([
                reg_flat,
                mx.zeros((self._reg_flat_dim - reg_flat.shape[0],))
            ])
        reg_dir = reg_flat / (mx.sqrt((reg_flat * reg_flat).sum()) + eps)

        summary = delta.mean(axis=(0, 1))  # (d_model,)
        delta_dir = summary / (mx.sqrt((summary * summary).sum()) + eps)

        reg_proj = _ternary_1d(self.proj_align[phase_idx], reg_dir)     # (d_align,)
        delta_proj = _ternary_1d(self.proj_delta[phase_idx], delta_dir)  # (d_align,)
        alignment = (reg_proj * delta_proj).sum()            # scalar

        gate = mx.sigmoid(
            alignment * self.temperature[phase_idx]
            + self.learned_bias[phase_idx]
        )
        gated_delta = gate * delta

        # Register updates (normalized to prevent unbounded accumulation)
        updated_registers = []
        write_gate_values = []
        for reg_idx in range(self.n_registers):
            write_idx = phase_idx * self.n_registers + reg_idx
            wg = mx.sigmoid(self.write_gates[write_idx](summary.reshape(1, -1)).reshape(-1))
            update = _ternary_1d(self.write_projs[write_idx], summary)[:self.d_reg_real]
            updated_registers.append(
                self.register_norm(registers[reg_idx] + wg * update))
            write_gate_values.append(wg.item())

        return gated_delta, updated_registers, gate, write_gate_values


# ══════════════════════════════════════════════════════════════════════
# MetaS4 — Final structural summary
# ══════════════════════════════════════════════════════════════════════


class MetaS4Ternary(nn.Module):
    """Final intelligence scan: register-query attention over residual."""

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int = 3,
        n_banks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_reg_real = d_register * 2
        self.n_registers = n_registers
        self.n_banks = n_banks
        self.scale = d_model ** -0.5

        total_reg_dim = n_banks * n_registers * self.d_reg_real
        self._total_reg_dim = ((total_reg_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._total_reg_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        meta_banks: list[list[mx.array]],
        residual: mx.array,
    ) -> mx.array:
        B, L, D = residual.shape

        q_input = _flatten_banks(meta_banks)
        if q_input.shape[0] < self._total_reg_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._total_reg_dim - q_input.shape[0],))
            ])

        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale
        attn_weights = mx.softmax(attn, axis=-1)
        attn_weights = self.dropout(attn_weights)

        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        out = self.out_proj(summary)                            # (B, d_model)
        out = mx.broadcast_to(out[:, None, :], residual.shape)
        return residual + out


# ══════════════════════════════════════════════════════════════════════
# MetaS3 — Cross-level contribution gates
# ══════════════════════════════════════════════════════════════════════


class MetaS3Ternary(nn.Module):
    """Top-level per-pass contribution gates from register banks.

    Fixed from original: temperature scaling + learned bias initialized
    to -2.0 (sigmoid(-2) ≈ 0.12) so gates start near-closed and must
    learn to open. Without this, gates start at 1.0 and never differentiate.
    """

    def __init__(self, d_register: int, n_registers: int, n_banks: int, n_passes: int):
        super().__init__()
        self.n_passes = n_passes
        d_reg_real = d_register * 2
        input_dim = n_banks * n_registers * d_reg_real
        self.gate_proj = nn.Linear(input_dim, n_passes)
        # Initialize bias to -2.0 so sigmoid starts near 0.12, not 0.5
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(self, all_banks: list[list[mx.array]]) -> mx.array:
        flat = _flatten_banks(all_banks)
        logits = self.gate_proj(flat)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S5Reweight — Identity-level pass contribution (replaces MetaS3)
# ══════════════════════════════════════════════════════════════════════


class S5Reweight(nn.Module):
    """S5 — Identity-level pass contribution reweighting.

    Beer's S5 is identity — it defines what the system IS and must
    see the full picture to maintain coherence. The prior MetaS3 only
    saw register banks (S2/S3-filtered state). S5 gets a direct,
    ungated view of what S1 operations actually produced.

    Inputs:
      - Register banks (S2 coordination state) — what the system
        believes about type/scope/role
      - Raw (ungated) pass deltas — what each pass's operations
        PROPOSED before S3 gating filtered them

    Why ungated matters:
      A pass that S3 currently suppresses can still influence the
      final output through S5's awareness of its raw delta. If S5
      sees useful raw output, it opens that pass's gate, which in
      turn teaches S3 to open. S5 sees ground truth about S1; S3
      only sees what it already filtered.

    Output: per-pass sigmoid gates (same role as MetaS3).
    Initialization: bias -2.0 (gates start near-closed, ~0.12).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int,
        n_banks: int,
        n_passes: int,
    ):
        super().__init__()
        self.n_passes = n_passes
        self.d_model = d_model
        d_reg_real = d_register * 2

        # Register input (same as MetaS3)
        reg_input_dim = n_banks * n_registers * d_reg_real

        # Raw delta input: each pass delta summarized to d_model
        delta_summary_dim = n_passes * d_model
        self._delta_dim = ((delta_summary_dim + 15) // 16) * 16
        self._delta_dim_raw = delta_summary_dim

        # Project raw deltas to compact features via ternary fabric.
        # pre_norm=True: direction matters, not magnitude.
        # 16 features per pass — enough to capture operational character.
        delta_proj_out = n_passes * 16
        delta_proj_out_padded = ((delta_proj_out + 15) // 16) * 16
        self.delta_proj = TernaryLinear(
            self._delta_dim, delta_proj_out_padded, pre_norm=True)
        self._delta_proj_out = delta_proj_out

        # Combined: register features + delta features → gates
        combined_dim = reg_input_dim + delta_proj_out
        self.gate_proj = nn.Linear(combined_dim, n_passes)
        # Bias -2.0: gates start near-closed (~0.12), must learn to open
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(
        self,
        all_banks: list[list[mx.array]],
        raw_deltas: list[mx.array],
    ) -> mx.array:
        """
        all_banks:  list of register banks (S2 coordination state)
        raw_deltas: list of n_passes raw (ungated) pass deltas,
                    each (B, L, d_model)

        Returns: (n_passes,) sigmoid gates for pass contribution
        """
        # Register features
        reg_flat = _flatten_banks(all_banks)

        # Raw delta features: spatial mean of each ungated pass delta
        delta_summaries = []
        for delta in raw_deltas:
            delta_summaries.append(delta.mean(axis=(0, 1)))  # (d_model,)
        delta_flat = mx.concatenate(delta_summaries, axis=-1)

        # Pad for TernaryLinear alignment
        if delta_flat.shape[0] < self._delta_dim:
            delta_flat = mx.concatenate([
                delta_flat,
                mx.zeros((self._delta_dim - delta_flat.shape[0],))
            ])

        # Project: ternary topology learns which delta patterns matter
        delta_features = _ternary_1d(
            self.delta_proj, delta_flat)[:self._delta_proj_out]

        # Combine register + delta features → gate logits
        combined = mx.concatenate([reg_flat, delta_features], axis=-1)
        logits = self.gate_proj(combined)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S2 — Inter-pass direction coordination (Beer's anti-oscillation)
# ══════════════════════════════════════════════════════════════════════


class S2Coordinator(nn.Module):
    """S2 — Inter-pass direction coordination.

    Beer's S2 prevents oscillation between S1 operational units.
    In v10, the S1 units are the 5 level-passes. Without S2, passes
    can write contradictory deltas to the residual stream — Pass N
    compresses in one direction, Pass N+1 inadvertently undoes it.

    Mechanism: after each pass produces a delta, S2 computes a small
    direction signal and adds it to the next pass's input. This is
    a coordination memo: "Pass N moved the representation THIS way."

    The next pass's S3 gates and S4 intelligence still control what
    happens — S2 just provides awareness of the predecessor's action.

    Properties:
      - 4 transitions (between 5 passes)
      - Direction = projected, normalized delta summary
      - Scale starts small (~0.01), learnable per transition
      - S2 signals survive MetaS3 reweighting — coordination
        infrastructure is not gated by control (correct: S2 ≠ S3)

    Conflict detection (diagnostic, not used for control):
      Cosine similarity between consecutive pass deltas.
        cos < 0 → oscillation (passes fighting)
        cos > 0 → reinforcement (passes cooperating)
      Exposed in instrumentation. If S2 works, conflict scores
      should trend toward 0 or positive over training.

    Design:
      - Not S3: doesn't gate or suppress. Additive, not multiplicative.
      - Not S4: doesn't scan environment. Dumb memo of what happened.
      - Not S5: doesn't define identity. Transient, per-forward-pass.
      - IS S2: minimum viable coordination — "FYI, here's what just
        happened." Prevents unknowing contradiction without preventing
        intentional override.
    """

    N_TRANSITIONS = 4
    TRANSITION_NAMES = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model

        # Direction projection: learns which aspects of the delta
        # matter for coordination. pre_norm=True so it's about
        # direction (shape), not magnitude.
        self.dir_projs = [
            TernaryLinear(d_model, d_model, pre_norm=True)
            for _ in range(self.N_TRANSITIONS)
        ]
        # Initialize gamma small — direction signal starts gentle
        for proj in self.dir_projs:
            proj.gamma = proj.gamma * 0.01

        # Per-transition learnable scale
        self.scales = [mx.ones((1,)) * 0.01
                       for _ in range(self.N_TRANSITIONS)]

        # Normalize direction signal — prevents scale drift over training
        self.norm = nn.RMSNorm(d_model)

    def direction_signal(
        self,
        pass_delta: mx.array,
        transition_idx: int,
    ) -> mx.array:
        """Direction memo from pass N to pass N+1.

        pass_delta: (B, L, d_model) — what the pass changed
        transition_idx: 0-3

        Returns (1, 1, d_model) — broadcasts to (B, L, d_model)
        """
        # Spatial mean → single direction vector
        summary = pass_delta.mean(axis=(0, 1))           # (d_model,)

        # Project through ternary fabric — learns which aspects matter
        projected = self.dir_projs[transition_idx](
            summary.reshape(1, -1)
        ).reshape(-1)                                     # (d_model,)

        # Normalize + scale
        signal = self.norm(projected) * self.scales[transition_idx]

        return signal[None, None, :]                      # (1, 1, d_model)

    @staticmethod
    def coherence_factor(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> mx.array:
        """Differentiable coherence: 1 + cos(prev, curr).

        Returns mx.array scalar in [0, 2]:
          2.0 → passes fully agree (amplify direction signal)
          1.0 → orthogonal (neutral)
          0.0 → passes fully conflict (dampen signal to zero)

        Gradient: stop_gradient on delta_prev — earlier pass sets
        direction, later pass learns to align. S2 doesn't retro-adjust
        the predecessor; it teaches the current pass that coherent
        deltas produce stronger forward signals (better loss).
        """
        s_prev = mx.stop_gradient(delta_prev.mean(axis=(0, 1)))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        return 1.0 + dot / (n_prev * n_curr)

    @staticmethod
    def conflict_score(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> float:
        """Cosine similarity between consecutive pass deltas (diagnostic).

          +1 → reinforcing  |  0 → orthogonal  |  -1 → oscillating

        Non-differentiable — for instrumentation/logging only.
        See coherence_factor() for the differentiable version used
        in the forward pass to modulate direction signals.
        """
        s_prev = delta_prev.mean(axis=(0, 1))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        cos = dot / (n_prev * n_curr)
        mx.eval(cos)
        return float(cos.item())


# ══════════════════════════════════════════════════════════════════════
# CycleContinue — S3 cycle-level continuation gate
# ══════════════════════════════════════════════════════════════════════


class CycleContinue(nn.Module):
    """S3 continuation gate: should another dispatch cycle contribute?

    Beer's S3 is the control layer — it decides what operations should
    pass through. Within a cycle, the existing S3Ternary gates each
    phase's delta. Between cycles, CycleContinue gates whether the
    NEXT cycle's entire contribution should matter.

    The model always computes up to desc_max_cycles (static graph for
    MLX). CycleContinue controls each cycle's contribution weight via
    a cumulative gate product:

      cycle 0: always full strength (cumulative_gate = 1.0)
      cycle 1: scaled by continue_gate_0
      cycle 2: scaled by continue_gate_0 × continue_gate_1
      ...

    If CycleContinue learns that simple tokens need only 1 cycle,
    it drives the gate toward 0 after cycle 0 — cycles 1+ produce
    near-zero deltas (computed but ineffective). For complex tokens
    needing compositional depth (PARTIAL → APPLY), the gate stays
    open, giving cycle 1+ full contribution.

    Input: register bank (S3's running state after the cycle).
    The registers carry type/scope/role information accumulated
    through the cycle's S3 phase gating — exactly what's needed
    to decide "was this cycle productive? would another help?"

    Initialization: bias=0 → sigmoid(0)=0.5 (neutral). The model
    learns in both directions: open for complex content, close for
    simple. No commitment to a default cycle count.
    """

    def __init__(self, d_register: int, n_registers: int = 3):
        super().__init__()
        d_reg_real = d_register * 2
        self.d_reg_real = d_reg_real
        self.n_registers = n_registers

        input_dim = n_registers * d_reg_real
        # RMSNorm the register input — prevents sigmoid saturation.
        # Raw registers have norm ~16 each (||concat|| ≈ 27.7).
        # Without normalization, even small weight updates produce
        # logits >> 4, saturating sigmoid and killing gradient.
        # RMSNorm → ||input|| ≈ 1.0 → logit stays in active zone.
        self.input_norm = nn.RMSNorm(input_dim)
        # Small projection: normalized register state → scalar logit
        self.gate_proj = nn.Linear(input_dim, 1)
        # Neutral init: sigmoid(0) = 0.5
        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)
        self.gate_proj.bias = mx.zeros_like(self.gate_proj.bias)

    def __call__(self, registers: list[mx.array]) -> mx.array:
        """Compute continuation gate from register state.

        registers: list of n_registers register vectors, each (d_reg_real,)
        Returns: scalar gate in [0, 1]
        """
        reg_flat = _flatten_registers(registers)
        reg_flat = self.input_norm(reg_flat)
        # tanh clamp: logit ∈ [-4, +4] → sigmoid ∈ [0.018, 0.982]
        # Guarantees gradient flow even if norms drift. The gate
        # can never fully saturate — always learnable.
        logit = mx.tanh(self.gate_proj(reg_flat)) * 4.0
        return mx.sigmoid(logit).reshape(())  # scalar


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    d_register = 128
    d_reg_real = d_register * 2
    n_registers = 3

    def _fresh_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    def _init_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    print("Testing S4Ternary...")
    s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
    banks = [_init_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    updates, attn = s4(banks, residual)
    mx.eval(*updates, attn)
    assert len(updates) == 3
    assert updates[0].shape == (d_reg_real,)
    print(f"  S4: {len(updates)} updates, shape {updates[0].shape} ✓")

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, d_register, n_phases=3, n_registers=n_registers)
    regs = _fresh_bank()
    delta = mx.random.normal((1, 32, d_model))
    gated, new_regs, gate, wgv = s3.gate_phase(regs, delta, phase_idx=0)
    mx.eval(gated, *new_regs, gate)
    assert gated.shape == (1, 32, d_model)
    assert len(new_regs) == 3
    print(f"  S3: gate={gate.item():.3f}, gated_delta shape {gated.shape} ✓")

    print("Testing MetaS4Ternary...")
    meta_s4 = MetaS4Ternary(d_model, d_register, n_registers=n_registers, n_banks=4)
    meta_banks = [_init_bank(), _fresh_bank(), _fresh_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    out = meta_s4(meta_banks, residual)
    mx.eval(out)
    assert out.shape == (1, 32, d_model)
    print(f"  MetaS4: {residual.shape} → {out.shape} ✓")

    print("Testing MetaS3Ternary...")
    meta_s3 = MetaS3Ternary(d_register, n_registers=n_registers, n_banks=6, n_passes=5)
    all_banks = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    gates = meta_s3(all_banks)
    mx.eval(gates)
    assert gates.shape == (5,)
    # Verify gates start near-closed (bias=-2.0 → sigmoid ≈ 0.12), not at 1.0
    for g in gates.tolist():
        assert g < 0.5, f"Meta-S3 gate should start near-closed, got {g:.3f}"
    print(f"  MetaS3: gates shape {gates.shape}, values {[f'{g:.3f}' for g in gates.tolist()]} ✓ (near-closed)")

    print("Testing S5Reweight...")
    s5 = S5Reweight(d_model, d_register, n_registers=n_registers,
                     n_banks=6, n_passes=5)
    mx.eval(s5.parameters())
    all_banks_s5 = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    raw_deltas = [mx.random.normal((1, 32, d_model)) for _ in range(5)]
    gates_s5 = s5(all_banks_s5, raw_deltas)
    mx.eval(gates_s5)
    assert gates_s5.shape == (5,), f"Expected (5,), got {gates_s5.shape}"
    for g in gates_s5.tolist():
        assert g < 0.5, f"S5 gate should start near-closed, got {g:.3f}"
    print(f"  S5Reweight: gates {[f'{g:.3f}' for g in gates_s5.tolist()]} ✓ (near-closed)")
    # Verify it uses raw deltas — different deltas should produce different gates
    raw_deltas_2 = [mx.random.normal((1, 32, d_model)) * 10.0 for _ in range(5)]
    gates_s5_2 = s5(all_banks_s5, raw_deltas_2)
    mx.eval(gates_s5_2)
    diff = max(abs(a - b) for a, b in zip(gates_s5.tolist(), gates_s5_2.tolist()))
    assert diff > 1e-6, "S5 gates should differ with different raw deltas"
    print(f"  S5Reweight: different raw deltas → different gates (max diff={diff:.4f}) ✓")

    print("Testing S2Coordinator...")
    s2 = S2Coordinator(d_model)
    mx.eval(s2.parameters())
    # Direction signal shape
    delta = mx.random.normal((1, 32, d_model))
    signal = s2.direction_signal(delta, 0)
    mx.eval(signal)
    assert signal.shape == (1, 1, d_model), f"Expected (1, 1, {d_model}), got {signal.shape}"
    # Signal should be small (gamma init * 0.01, scale 0.01)
    signal_norm = float(mx.sqrt((signal * signal).sum()).item())
    print(f"  S2: signal shape {signal.shape}, norm={signal_norm:.6f} (should be small) ✓")
    # All 4 transitions
    for ti in range(S2Coordinator.N_TRANSITIONS):
        sig = s2.direction_signal(delta, ti)
        mx.eval(sig)
        assert sig.shape == (1, 1, d_model)
    print(f"  S2: all {S2Coordinator.N_TRANSITIONS} transitions produce valid signals ✓")
    # Conflict score
    delta2 = mx.random.normal((1, 32, d_model))
    cs = S2Coordinator.conflict_score(delta, delta2)
    assert -1.0 <= cs <= 1.0, f"Conflict score out of range: {cs}"
    # Self-conflict should be +1
    cs_self = S2Coordinator.conflict_score(delta, delta)
    assert cs_self > 0.99, f"Self-conflict should be ~1.0, got {cs_self:.3f}"
    # Anti-conflict should be -1
    cs_anti = S2Coordinator.conflict_score(delta, -delta)
    assert cs_anti < -0.99, f"Anti-conflict should be ~-1.0, got {cs_anti:.3f}"
    print(f"  S2: conflict scores: random={cs:.3f}, self={cs_self:.3f}, anti={cs_anti:.3f} ✓")
    # Coherence factor (differentiable version)
    cf_agree = S2Coordinator.coherence_factor(delta, delta)
    mx.eval(cf_agree)
    assert abs(float(cf_agree.item()) - 2.0) < 0.01, \
        f"Agreement coherence should be ~2.0, got {cf_agree.item()}"
    cf_fight = S2Coordinator.coherence_factor(delta, -delta)
    mx.eval(cf_fight)
    assert abs(float(cf_fight.item()) - 0.0) < 0.01, \
        f"Conflict coherence should be ~0.0, got {cf_fight.item()}"
    cf_ortho = S2Coordinator.coherence_factor(
        mx.array([[[1.0, 0.0, 0.0, 0.0]]]),
        mx.array([[[0.0, 1.0, 0.0, 0.0]]]),
    )
    mx.eval(cf_ortho)
    assert abs(float(cf_ortho.item()) - 1.0) < 0.01, \
        f"Orthogonal coherence should be ~1.0, got {cf_ortho.item()}"
    print(f"  S2: coherence factor: agree={cf_agree.item():.1f}, "
          f"ortho={cf_ortho.item():.1f}, fight={cf_fight.item():.1f} ✓")

    print("Testing CycleContinue...")
    cc = CycleContinue(d_register, n_registers=n_registers)
    mx.eval(cc.parameters())
    regs = _fresh_bank()
    gate = cc(regs)
    mx.eval(gate)
    assert gate.shape == (), f"Expected scalar, got {gate.shape}"
    assert abs(float(gate.item()) - 0.5) < 0.01, \
        f"CycleContinue gate should start at ~0.5 (neutral), got {gate.item():.3f}"
    print(f"  CycleContinue: gate={gate.item():.3f} (neutral init) ✓")
    # After training (non-zero weights), different register states produce different gates.
    # At init, weights are zero so all inputs → same output (correct: neutral start).
    # Verify by setting a non-zero weight:
    cc.gate_proj.weight = mx.ones_like(cc.gate_proj.weight) * 0.01
    regs2 = [mx.random.normal((d_reg_real,)) for _ in range(n_registers)]
    gate_a = cc(regs)
    gate_b = cc(regs2)
    mx.eval(gate_a, gate_b)
    assert abs(float(gate_a.item()) - float(gate_b.item())) > 1e-6, \
        "CycleContinue should produce different gates for different register states (non-zero weights)"
    print(f"  CycleContinue: different regs → different gates ({gate_a.item():.3f} vs {gate_b.item():.3f}) ✓")

    # Test gradient flow
    print("Testing gradient flow through S4...")
    import mlx.nn as nn
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
            self.param = mx.zeros((d_reg_real,))
        def __call__(self, x):
            bank = [[self.param] * n_registers]
            target = _fresh_bank()
            updates, _ = self.s4(bank, x)
            return mx.sum(updates[0])

    tm = TestModel()
    mx.eval(tm.parameters())
    def test_loss(tm, x):
        return tm(x)
    gfn = nn.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)
    print(f"  S4 gradient flow OK: loss={lv.item():.4f} ✓")

    print("components.py self-test: all ok ✓")
