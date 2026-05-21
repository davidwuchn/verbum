"""VSM control components — S3, S4, MetaS4, S5, S2, AlgedonicAlert, RetrievalRegisters.

v13: Trimmed of dead code from V12.

Removed (abstraction slots gone):
  - S4ProposalHead       (abstraction slot proposal pathway)
  - AbstractionRegularizer (diversity / no-KIBC-copying regularizer)
  - CycleContinue        (multi-cycle dispatch gate)
  - MetaS3Ternary        (superseded by S5Reweight)

Kept and adapted:
  - S3Ternary            — per-pass 3-phase gating
  - S4Ternary            — register cross-attention
  - MetaS4Ternary        — higher-level register coordination
  - S5Reweight           — identity-level pass contribution gates
  - S2Coordinator        — inter-pass coherence / direction signals
  - AlgedonicAlert       — VSM alarm channel (S1→S5 bypass)
  - RetrievalRegisters   — M-kernel ↔ KIBC bridge (2 registers)

Config: V13Config (no abstraction slots, no CategoryDispatch/math kernels).
Substrate: TernaryLinear from ternary.py.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2.
All gate projections use TernaryLinear (holographic capacity from the sieve).
Temperature and bias parameters are kept as separate fp32 scalars/vectors.

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from config import V13Config
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
        """Attend to residual from register-bank query; return register updates.

        banks:    list of register banks (each a list of n_registers vectors)
        residual: (B, L, d_model)

        Returns:
          updates:      list of n_registers updated register vectors
          attn_weights: (B, L) attention weights (stop_gradient)
        """
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

    3 phases: dispatch / stride / integrate.
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

        # Write gates: TernaryLinear padded to 16, separate bias param.
        # Bias init -2.0 → sigmoid(-2) ≈ 0.12 (near-closed at start)
        self.write_gates = [
            TernaryLinear(d_model, 16, pre_norm=False)
            for _ in range(n_phases * n_registers)
        ]
        # Separate bias per gate: scalar, init -2.0
        self.write_gate_biases = [
            mx.full((1,), -2.0)
            for _ in range(n_phases * n_registers)
        ]

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

    def gate_phase(
        self,
        registers: list[mx.array],
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array, list[mx.array], mx.array, list[float]]:
        """Gate a phase's output using alignment-based scalar gate.

        registers:  list of n_registers real register vectors
        delta:      (B, L, d_model) phase output
        phase_idx:  0 = dispatch, 1 = stride, 2 = integrate

        Returns:
          gated_delta:      (B, L, d_model) — scaled by alignment gate
          updated_registers: list of n_registers updated register vectors
          gate:             scalar gate value (for instrumentation)
          write_gate_values: per-register write gate scalars (for instrumentation)
        """
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
            wg = mx.sigmoid(
                self.write_gates[write_idx](summary.reshape(1, -1)).reshape(-1)[..., :1]
                + self.write_gate_biases[write_idx]
            )
            update = _ternary_1d(self.write_projs[write_idx], summary)[:self.d_reg_real]
            updated_registers.append(
                self.register_norm(registers[reg_idx] + wg * update))
            write_gate_values.append(wg.item())

        return gated_delta, updated_registers, gate, write_gate_values

    def __call__(
        self,
        registers: list[mx.array],
        deltas: list[mx.array],
    ) -> tuple[list[mx.array], list[mx.array], list[mx.array], list[list[float]]]:
        """Gate all phases for a pass.

        registers: initial register state (list of n_registers vectors)
        deltas:    list of n_phases delta tensors, each (B, L, d_model)

        Returns:
          gated_deltas:    list of n_phases gated deltas
          final_registers: register state after all phases
          gates:           per-phase gate scalars (for instrumentation)
          wgv_list:        per-phase write gate values
        """
        gated_deltas = []
        gates = []
        wgv_list = []
        current_regs = registers
        for phase_idx, delta in enumerate(deltas):
            gated, current_regs, gate, wgv = self.gate_phase(
                current_regs, delta, phase_idx)
            gated_deltas.append(gated)
            gates.append(gate)
            wgv_list.append(wgv)
        return gated_deltas, current_regs, gates, wgv_list


# ══════════════════════════════════════════════════════════════════════
# MetaS4 — Final structural summary
# ══════════════════════════════════════════════════════════════════════


class MetaS4Ternary(nn.Module):
    """Final intelligence scan: register-query attention over residual.

    Runs after all passes to produce a global structural summary.
    The output is added back to the residual stream as a final
    register-conditioned correction.
    """

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
        """Attend to residual from accumulated register banks.

        meta_banks: list of register banks (per-pass snapshots)
        residual:   (B, L, d_model)

        Returns: (B, L, d_model) — residual with register-conditioned correction
        """
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
# S5Reweight — Identity-level pass contribution
# ══════════════════════════════════════════════════════════════════════


class S5Reweight(nn.Module):
    """S5 — Identity-level pass contribution reweighting.

    Beer's S5 is identity — it defines what the system IS and must
    see the full picture to maintain coherence. S5Reweight gets a
    direct, ungated view of what S1 operations actually produced.

    Inputs:
      - Register banks (S2 coordination state) — what the system
        believes about type/scope/role
      - Raw (ungated) pass deltas — what each pass's operations
        PROPOSED before S3 gating filtered them

    Why ungated matters:
      A pass that S3 currently suppresses can still influence the
      final output through S5's awareness of its raw delta. If S5
      sees useful raw output, it opens that pass's gate, which in
      turn teaches S3 to open.

    Output: per-pass sigmoid gates (n_passes,).
    Initialization: bias -2.0 → gates start near-closed (~0.12).
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

        # Register input
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

        # Combined: register features + delta features → gates.
        # TernaryLinear requires in_features divisible by group_size=64.
        combined_dim = reg_input_dim + delta_proj_out
        self._combined_dim = combined_dim
        self._combined_dim_padded = ((combined_dim + 63) // 64) * 64
        self._n_passes_padded = ((n_passes + 15) // 16) * 16
        self.gate_proj = TernaryLinear(
            self._combined_dim_padded, self._n_passes_padded, pre_norm=False)
        # Separate bias: -2.0 → gates start near-closed (~0.12)
        self.gate_bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(
        self,
        all_banks: list[list[mx.array]],
        raw_deltas: list[mx.array],
    ) -> mx.array:
        """Compute per-pass contribution gates.

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
        # Pad to multiple of 64 for TernaryLinear
        if combined.shape[0] < self._combined_dim_padded:
            combined = mx.concatenate([
                combined,
                mx.zeros((self._combined_dim_padded - combined.shape[0],))
            ])
        logits = self.gate_proj(combined.reshape(1, -1)).reshape(-1)[:self.n_passes]
        return mx.sigmoid((logits + self.gate_bias) * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S2 — Inter-pass direction coordination (Beer's anti-oscillation)
# ══════════════════════════════════════════════════════════════════════


class S2Coordinator(nn.Module):
    """S2 — Inter-pass direction coordination.

    Beer's S2 prevents oscillation between S1 operational units.
    In V13, the 6 inter-pass transitions carry direction memos so
    each pass is aware of what the predecessor changed.

    Mechanism: after each pass produces a delta, S2 computes a small
    direction signal and adds it to the next pass's input. This is
    a coordination memo: "Pass N moved the representation THIS way."

    Properties:
      - 6 transitions (between 7 passes in hourglass)
      - Direction = projected, normalized delta summary
      - Scale starts small (~0.01), learnable per transition
      - Not gated by S3 (coordination infrastructure ≠ content control)

    Conflict detection (diagnostic, not used for control):
      cos < 0 → oscillation (passes fighting)
      cos > 0 → reinforcement (passes cooperating)
    """

    N_TRANSITIONS = 6
    TRANSITION_NAMES = (
        "L0↑→L1↑", "L1↑→L2↑", "L2↑→L3",
        "L3→L2↓", "L2↓→L1↓", "L1↓→L0↓",
    )

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model

        # Direction projection: learns which aspects of the delta matter.
        # pre_norm=True: shape (direction) not magnitude matters for S2.
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

        pass_delta:      (B, L, d_model) — what the pass changed
        transition_idx:  0 to N_TRANSITIONS-1

        Returns: (1, 1, d_model) — broadcasts to (B, L, d_model)
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

        stop_gradient on delta_prev — earlier pass sets direction,
        later pass learns to align.
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
# AlgedonicAlert — Beer's fire alarm: S1→S5 emergency bypass
# ══════════════════════════════════════════════════════════════════════


class AlgedonicAlert(nn.Module):
    """Beer's algedonic channel: S1→S5 fire alarm.

    Direct bypass from operational metrics to S5, monitoring the
    HEALTH of the control system itself — not its content.

    Beer (Brain of the Firm, 1972): emergency signals bypass the
    management hierarchy to reach S5 directly when the control
    system is failing.

    In V13, S5Reweight asks "what did each pass contribute?" (content).
    AlgedonicAlert asks "is the control system healthy?" (health).

    Mechanism:
      - Separate gate: per-pass factor ∈ [0, 2] via 1 + tanh(logit)
      - Factor = 1.0 → no alarm (neutral, S5Reweight controls)
      - Factor < 1.0 → pain (suppress this pass)
      - Factor > 1.0 → pleasure (amplify this pass, up to 2×)
      - Multiplies S5Reweight gates: effective = s5_gate × alarm_factor

    Properties:
      - Zero-init: alarm starts inert (factor = 1.0 everywhere)
      - End-to-end differentiable
      - Low bandwidth: compact scalar inputs → per-pass scalar outputs
        (no attention — the alarm is FAST)
    """

    # Input metric dimensions (must match _pack_metrics)
    # V13: 7 passes (3 asc + apex + 3 desc), 6 S2 transitions, 8 combinators
    N_S3_GATE_MEANS = 7    # mean S3 gate per pass
    N_S3_GATE_MINS = 7     # min S3 gate per pass (most suppressed phase)
    N_S2_CONFLICTS = 6     # cosine between consecutive pass deltas
    N_DISPATCH = 8         # combinator weight means (K, I, B, C, D, Y, W, WHNF)
    N_DISPATCH_ENTROPY = 1 # dispatch distribution entropy
    N_COMPUTE_GATE = 2     # mean + active fraction
    # V13: no cycle gates or effective cycles (max_cycles=1 always)
    N_RAW_DELTA_NORMS = 7  # L2 norm of each raw delta
    N_GATED_DELTA_NORMS = 7  # L2 norm of each gated delta
    N_SUPPRESSION_RATIOS = 7  # gated/raw ratio per pass
    N_REGISTER_NORMS = 8   # mean register norm per bank

    INPUT_DIM = (N_S3_GATE_MEANS + N_S3_GATE_MINS + N_S2_CONFLICTS +
                 N_DISPATCH + N_DISPATCH_ENTROPY + N_COMPUTE_GATE +
                 N_RAW_DELTA_NORMS + N_GATED_DELTA_NORMS +
                 N_SUPPRESSION_RATIOS + N_REGISTER_NORMS)  # = 60

    # TernaryLinear requires in_features divisible by group_size=64.
    # 60 → next multiple of 64 is 64.
    _INPUT_DIM_PADDED = 64

    def __init__(self, n_passes: int = 7, n_combinators: int = 8):
        super().__init__()
        self.n_passes = n_passes
        self.n_combinators = n_combinators

        # Single ternary linear: operational metrics → per-pass alarm logits.
        # Output padded to multiple of 16, take [:n_passes].
        _n_passes_padded = ((n_passes + 15) // 16) * 16
        self.alarm_proj = TernaryLinear(
            self._INPUT_DIM_PADDED, _n_passes_padded, pre_norm=False)
        # Zero-init: alarm starts inert (all factors = 1.0).
        # gamma=0 → output=0 → tanh(0)=0 → factor=1.0
        self.alarm_proj.gamma = mx.zeros_like(self.alarm_proj.gamma)

    def __call__(
        self, metrics_vector: mx.array,
    ) -> mx.array:
        """Compute alarm factors from health metrics.

        Args:
            metrics_vector: (INPUT_DIM,) packed operational metrics.
                All values should be differentiable (no stop_gradient).

        Returns:
            pass_factors: (n_passes,) alarm factors in [0, 2]:
              1.0 → no alarm (neutral)
              < 1.0 → pain (suppress this pass)
              > 1.0 → pleasure (amplify, up to 2.0)
        """
        # Pad metrics vector to _INPUT_DIM_PADDED for TernaryLinear
        padded = mx.concatenate([
            metrics_vector,
            mx.zeros((self._INPUT_DIM_PADDED - self.INPUT_DIM,))
        ])
        pass_logits = self.alarm_proj(padded.reshape(1, -1)).reshape(-1)[:self.n_passes]
        return 1.0 + mx.tanh(pass_logits)


# ══════════════════════════════════════════════════════════════════════
# RetrievalRegisters — M kernel ↔ KIBC bridge
# ══════════════════════════════════════════════════════════════════════


class RetrievalRegisters(nn.Module):
    """Bridge between retrieval (M/GLA) and composition (KIBC) pathways.

    During ascending passes, GatedLinearAttention retrieval layers
    accumulate pattern match information. RetrievalRegisters distills
    this into a fixed-size register bank that the descending arm reads
    alongside the existing KIBC registers.

    Architecture:
      - n_retrieval_registers: how many slots M can write to (default: 2)
      - Each register has dimension d_reg_real (same as KIBC registers)
      - Write pathway: residual summary → gated write to register
      - Read: registers are read by S4 and CombinatorDispatch (in model.py)

    Init: write gates biased to -3.0 → sigmoid ≈ 0.047.
    Near-zero at init — M results pass through without writing to
    registers until training teaches when to write.

    Instrumentation:
      _write_gate_values: (n_retrieval_registers,) per-register write activity
      _register_norms:    (n_retrieval_registers,) per-register L2 norms
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_retrieval_registers: int = 2,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_reg_real = d_register * 2
        self.n_retrieval_registers = n_retrieval_registers

        # Write projection: residual summary → register content
        d_reg_out = ((self.d_reg_real + 15) // 16) * 16
        self._d_reg_out = d_reg_out
        self.write_projs = [
            TernaryLinear(d_model, d_reg_out, pre_norm=True)
            for _ in range(n_retrieval_registers)
        ]

        # Write gates: TernaryLinear padded to 16, separate bias param.
        # Bias -3.0 → sigmoid ≈ 0.047. Near-zero at init.
        # d_model=512 is already a multiple of 16.
        self.write_gates = [
            TernaryLinear(d_model, 16, pre_norm=False)
            for _ in range(n_retrieval_registers)
        ]
        self.write_gate_biases = [
            mx.full((1,), -3.0)
            for _ in range(n_retrieval_registers)
        ]

        # Normalize written registers
        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # Instrumentation
        self._write_gate_values = None
        self._register_norms = None

    def init_registers(self) -> list[mx.array]:
        """Initialize retrieval registers to zeros."""
        return [mx.zeros((self.d_reg_real,))
                for _ in range(self.n_retrieval_registers)]

    def write(
        self,
        registers: list[mx.array],
        residual: mx.array,
    ) -> list[mx.array]:
        """Update retrieval registers from ascending arm residual.

        registers: list of n_retrieval_registers register vectors
        residual:  (B, L, d_model) — ascending arm output

        Returns: updated register list
        """
        # Spatial summary of residual
        summary = residual.mean(axis=(0, 1))  # (d_model,)

        updated = []
        gate_values = []
        for i in range(self.n_retrieval_registers):
            # Gate: should we write? TernaryLinear output padded to 16, take [:1] + bias.
            wg = mx.sigmoid(
                self.write_gates[i](summary.reshape(1, -1)).reshape(-1)[..., :1]
                + self.write_gate_biases[i]
            )
            gate_values.append(wg)

            # Content: what to write
            content = self.write_projs[i](
                summary.reshape(1, -1)).reshape(-1)[:self.d_reg_real]

            # Gated write + normalize
            updated.append(
                self.register_norm(registers[i] + wg * content))

        # Instrumentation
        self._write_gate_values = mx.stop_gradient(
            mx.concatenate([g.reshape(1) for g in gate_values]))
        self._register_norms = mx.stop_gradient(
            mx.stack([mx.sqrt(mx.sum(r * r) + 1e-8) for r in updated]))

        return updated


# ══════════════════════════════════════════════════════════════════════
# Convenience constructor from V13Config
# ══════════════════════════════════════════════════════════════════════


def make_components(cfg: V13Config) -> dict:
    """Construct all VSM components from a V13Config.

    Returns a dict of component instances keyed by name:
      s3:     S3Ternary
      s4:     S4Ternary
      meta_s4: MetaS4Ternary
      s5:     S5Reweight
      s2:     S2Coordinator
      alarm:  AlgedonicAlert
      retrieval: RetrievalRegisters
    """
    return {
        "s3": S3Ternary(
            d_model=cfg.d_model,
            d_register=cfg.d_register,
            n_phases=3,
            n_registers=cfg.n_registers,
        ),
        "s4": S4Ternary(
            d_model=cfg.d_model,
            d_register=cfg.d_register,
            n_registers=cfg.n_registers,
            max_banks=cfg.n_passes,
            dropout=cfg.dropout,
        ),
        "meta_s4": MetaS4Ternary(
            d_model=cfg.d_model,
            d_register=cfg.d_register,
            n_registers=cfg.n_registers,
            n_banks=cfg.n_passes,
            dropout=cfg.dropout,
        ),
        "s5": S5Reweight(
            d_model=cfg.d_model,
            d_register=cfg.d_register,
            n_registers=cfg.n_registers,
            n_banks=cfg.n_passes,
            n_passes=cfg.n_passes,
        ),
        "s2": S2Coordinator(d_model=cfg.d_model),
        "alarm": AlgedonicAlert(
            n_passes=cfg.n_passes,
            n_combinators=cfg.n_combinators,
        ),
        "retrieval": RetrievalRegisters(
            d_model=cfg.d_model,
            d_register=cfg.d_register,
            n_retrieval_registers=cfg.n_retrieval_registers,
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    d_register = 128
    d_reg_real = d_register * 2
    n_registers = 3
    n_passes = 7

    def _fresh_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    print("Testing S4Ternary...")
    s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=n_passes)
    banks = [_fresh_bank() for _ in range(3)]
    residual = mx.random.normal((1, 32, d_model))
    updates, attn = s4(banks, residual)
    mx.eval(*updates, attn)
    assert len(updates) == 3
    assert updates[0].shape == (d_reg_real,)
    print(f"  S4: {len(updates)} updates, shape {updates[0].shape} ✓")

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, d_register, n_phases=3, n_registers=n_registers)
    regs = _fresh_bank()
    deltas = [mx.random.normal((1, 32, d_model)) for _ in range(3)]
    gated_deltas, new_regs, gates, wgv_list = s3(regs, deltas)
    mx.eval(*gated_deltas, *new_regs, *gates)
    assert len(gated_deltas) == 3
    assert len(new_regs) == 3
    print(f"  S3: {len(gates)} gates, gated_delta shape {gated_deltas[0].shape} ✓")

    print("Testing MetaS4Ternary...")
    meta_s4 = MetaS4Ternary(d_model, d_register, n_registers=n_registers, n_banks=n_passes)
    meta_banks = [_fresh_bank() for _ in range(4)]
    out = meta_s4(meta_banks, residual)
    mx.eval(out)
    assert out.shape == residual.shape
    print(f"  MetaS4: output shape {out.shape} ✓")

    print("Testing S5Reweight...")
    s5 = S5Reweight(d_model, d_register, n_registers=n_registers,
                    n_banks=n_passes, n_passes=n_passes)
    all_banks = [_fresh_bank() for _ in range(n_passes)]
    raw_deltas = [mx.random.normal((1, 32, d_model)) for _ in range(n_passes)]
    gates_s5 = s5(all_banks, raw_deltas)
    mx.eval(gates_s5)
    assert gates_s5.shape == (n_passes,)
    print(f"  S5: gates shape {gates_s5.shape} ✓")

    print("Testing S2Coordinator...")
    s2 = S2Coordinator(d_model)
    delta = mx.random.normal((1, 32, d_model))
    sig = s2.direction_signal(delta, 0)
    mx.eval(sig)
    assert sig.shape == (1, 1, d_model)
    coh = S2Coordinator.coherence_factor(delta, delta)
    mx.eval(coh)
    print(f"  S2: signal shape {sig.shape}, coherence={coh.item():.3f} ✓")

    print("Testing AlgedonicAlert...")
    alarm = AlgedonicAlert(n_passes=n_passes)
    metrics = mx.zeros((AlgedonicAlert.INPUT_DIM,))
    factors = alarm(metrics)
    mx.eval(factors)
    assert factors.shape == (n_passes,)
    # zero-init: all factors should be 1.0
    assert abs(factors.mean().item() - 1.0) < 1e-5
    print(f"  Alarm: factors shape {factors.shape}, mean={factors.mean().item():.3f} ✓")

    print("Testing RetrievalRegisters...")
    rr = RetrievalRegisters(d_model, d_register, n_retrieval_registers=2)
    ret_regs = rr.init_registers()
    updated = rr.write(ret_regs, residual)
    mx.eval(*updated)
    assert len(updated) == 2
    assert updated[0].shape == (d_reg_real,)
    print(f"  RetrievalRegisters: {len(updated)} registers, shape {updated[0].shape} ✓")

    print("\nAll V13 component tests passed ✓")
