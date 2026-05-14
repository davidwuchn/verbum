"""VSM control components — S4, S3, MetaS4, MetaS3, RetrievalRegisters — MLX.

v12: Adds RetrievalRegisters — the bridge between M (retrieval layers in
ascending arm) and KIBC (composition layers in descending arm). M writes
pattern match results to retrieval registers during ascending passes.
The descending arm reads them alongside existing KIBC registers.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2,
preserving the same capacity as v6's complex ℂ^d_register registers without
requiring complex arithmetic in the autograd graph.

Kept as fp32 (not ternary):
  - S3 write_gates (nn.Linear with bias, tiny, sigmoid-init)
  - S3 temperature and learned_bias (scalar parameters)
  - MetaS3 gate_proj (nn.Linear with bias, small)
  - RetrievalRegisters write gate (nn.Linear, small)

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
# S4ProposalHead — S4→S5 abstraction proposal pathway
# ══════════════════════════════════════════════════════════════════════


class S4ProposalHead(nn.Module):
    """S4→S5 abstraction proposal: S4 proposes composed abstractions.

    After S4 has scanned registers and residual, this head projects
    S4's understanding into the slot embedding space. The result
    modulates what the abstraction slots represent during dispatch.

    Mechanism:
      - proposal_vector: Linear(S4_summary → d_model) — what to propose
      - proposal_confidence: Linear(S4_summary → 1) → sigmoid — how sure
      - target_slot: argmax over slot logits (straight-through)
      - effective: confidence × proposal_vector added to target slot

    The alarm gate (in model.py) modulates whether the proposal takes
    effect: high alarm + high confidence → gate opens → slot learns.

    Initialization: near-zero weights produce ~0.1 confidence and
    near-zero proposal vectors. First N steps behave identically
    to current architecture.
    """

    def __init__(
        self,
        d_model: int,
        n_abstraction_slots: int,
        d_register: int,
        n_registers: int = 3,
        n_banks: int = 3,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_abstraction_slots = n_abstraction_slots

        # Input: S4 summary (register-derived) — same inputs as emphasis
        d_reg_real = d_register * 2
        input_dim = n_banks * n_registers * d_reg_real

        # Proposal vector: what the abstraction should be
        self.proposal_proj = nn.Linear(input_dim, d_model)
        # Small init: proposals start negligible
        self.proposal_proj.weight = self.proposal_proj.weight * 0.01
        self.proposal_proj.bias = mx.zeros_like(self.proposal_proj.bias)

        # Confidence: how sure S4 is about this proposal
        self.confidence_proj = nn.Linear(input_dim, 1)
        # Bias init: sigmoid(bias) ≈ 0.1 → low confidence at start
        self.confidence_proj.weight = mx.zeros_like(
            self.confidence_proj.weight)
        self.confidence_proj.bias = mx.full(
            self.confidence_proj.bias.shape, -2.2)  # sigmoid(-2.2) ≈ 0.10

        # Slot targeting: which slot to modulate
        self.slot_target_proj = nn.Linear(input_dim, n_abstraction_slots)
        self.slot_target_proj.weight = mx.zeros_like(
            self.slot_target_proj.weight)
        self.slot_target_proj.bias = mx.zeros_like(
            self.slot_target_proj.bias)

    def __call__(
        self,
        register_summary: mx.array,
    ) -> tuple[mx.array, mx.array, mx.array]:
        """Produce a proposal for the abstraction slots.

        register_summary: (input_dim,) flattened register banks

        Returns:
          proposal_delta: (N, d_model) — per-slot proposal modulation
                          Only the target slot has non-zero contribution.
          confidence: scalar in [0, 1]
          slot_logits: (N,) raw targeting logits (for probing)
        """
        # Proposal vector
        proposal = self.proposal_proj(register_summary)  # (d_model,)

        # Confidence
        confidence = mx.sigmoid(
            self.confidence_proj(register_summary)).reshape(())

        # Target slot selection — soft via softmax weighting
        slot_logits = self.slot_target_proj(register_summary)  # (N,)
        slot_weights = mx.softmax(slot_logits)  # (N,)

        # Proposal delta: confidence-weighted proposal distributed
        # across slots proportional to slot_weights
        # (N,) × (d_model,) → (N, d_model)
        proposal_delta = (confidence * slot_weights[:, None]
                          * proposal[None, :])

        return proposal_delta, confidence, slot_logits


# ══════════════════════════════════════════════════════════════════════
# AbstractionRegularizer — diversity + no-KIBC-copying
# ══════════════════════════════════════════════════════════════════════


class AbstractionRegularizer:
    """Compute regularization losses for abstraction slot embeddings.

    Two soft pressures:
      1. Diversity: prevent slots from collapsing to the same vector.
         Penalizes pairwise cosine > diversity_threshold.
      2. No-KIBC-copying: prevent slots from becoming redundant copies
         of K, I, B, or C. Penalizes cosine(slot, combinator) > copy_threshold.

    Both are differentiable soft penalties (squared hinge).
    """

    @staticmethod
    def diversity_loss(
        slot_embeddings: mx.array,
        threshold: float = 0.5,
    ) -> mx.array:
        """Pairwise diversity penalty.

        slot_embeddings: (N, d_model)
        Returns: scalar loss
        """
        N = slot_embeddings.shape[0]
        if N < 2:
            return mx.array(0.0)

        # L2-normalize
        norms = mx.sqrt(mx.sum(
            slot_embeddings * slot_embeddings,
            axis=-1, keepdims=True) + 1e-8)
        normed = slot_embeddings / norms

        # Pairwise cosine: (N, N)
        cosines = normed @ normed.T

        # Mask diagonal
        mask = 1.0 - mx.eye(N)
        cosines = cosines * mask

        # Squared hinge: penalize above threshold
        violations = mx.maximum(cosines - threshold, 0.0)
        return mx.mean(violations * violations)

    @staticmethod
    def copy_loss(
        slot_embeddings: mx.array,
        combinator_embeddings: mx.array,
        threshold: float = 0.7,
    ) -> mx.array:
        """Prevent slots from copying KIBC embeddings.

        slot_embeddings: (N, d_model)
        combinator_embeddings: (4, d_model)
        Returns: scalar loss
        """
        # L2-normalize both
        s_norms = mx.sqrt(mx.sum(
            slot_embeddings * slot_embeddings,
            axis=-1, keepdims=True) + 1e-8)
        s_normed = slot_embeddings / s_norms

        c_norms = mx.sqrt(mx.sum(
            combinator_embeddings * combinator_embeddings,
            axis=-1, keepdims=True) + 1e-8)
        c_normed = combinator_embeddings / c_norms

        # Cross cosine: (N, 4)
        cosines = s_normed @ c_normed.T

        # Squared hinge: penalize above threshold
        violations = mx.maximum(cosines - threshold, 0.0)
        return mx.mean(violations * violations)

    @staticmethod
    def combined_loss(
        slot_embeddings: mx.array,
        combinator_embeddings: mx.array,
        diversity_lambda: float = 0.01,
        copy_lambda: float = 0.01,
        diversity_threshold: float = 0.5,
        copy_threshold: float = 0.7,
    ) -> mx.array:
        """Combined regularization loss."""
        div_loss = AbstractionRegularizer.diversity_loss(
            slot_embeddings, diversity_threshold)
        cp_loss = AbstractionRegularizer.copy_loss(
            slot_embeddings, combinator_embeddings, copy_threshold)
        return diversity_lambda * div_loss + copy_lambda * cp_loss


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

    N_TRANSITIONS = 6
    TRANSITION_NAMES = (
        "L0↑→L1↑", "L1↑→L2↑", "L2↑→L3",
        "L3→L2↓", "L2↓→L1↓", "L1↓→L0↓",
    )

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
# AlgedonicAlert — Beer's fire alarm: S1→S5 emergency bypass
# ══════════════════════════════════════════════════════════════════════


class AlgedonicAlert(nn.Module):
    """Beer's algedonic channel: S1→S5 fire alarm.

    Direct bypass from operational metrics to S5, monitoring the
    HEALTH of the control system itself — not its content.

    Beer (Brain of the Firm, 1972): "Signals between Systems 1 and 3
    should be continuously monitored, and if an emergency condition
    is detected, an emergency signal will be sent directly to System 5.
    In turn, System 5 wakes up, requesting emergency corrective action
    from Systems 3 and 4."

    In v11, S5Reweight asks "what did each pass contribute?" (content).
    AlgedonicAlert asks "is the control system healthy?" (health).
    S5Reweight reads raw deltas and register banks through S4 attention.
    AlgedonicAlert reads S3 gate values, dispatch distributions,
    conflict scores — the operational metrics that S4 doesn't see.

    Mechanism:
      - Separate gate: per-pass factor ∈ [0, 2] via 1 + tanh(logit)
      - Factor = 1.0 → no alarm (neutral, S5Reweight controls)
      - Factor < 1.0 → pain (suppress this pass)
      - Factor > 1.0 → pleasure (amplify this pass, up to 2×)
      - Multiplies S5Reweight gates: effective = s5_gate × alarm_factor

    Properties:
      - Zero-init: alarm starts inert (factor = 1.0 everywhere)
      - End-to-end differentiable: gradients flow back through
        operational metrics to S1/S3, teaching the whole system
        to avoid alarm conditions
      - Low bandwidth: ~48 scalar inputs → 5 scalar outputs
        (one linear projection, no attention — the alarm is FAST)
      - No learned baseline: raw metrics logged for offline
        threshold analysis. Baselines set from real data later.

    Escalation (Beer's model):
      1. S1 self-corrects (CycleContinue regulates cycles)
      2. S3 filters (per-phase gates suppress bad deltas)
      3. S5 overrides via alarm (this module — final recourse)
      The alarm runs AFTER all passes, so S1 and S3 have
      already had their chance.
    """

    # Input metric dimensions (must match _pack_metrics)
    # v12: 7 passes (3 asc + apex + 3 desc), 6 S2 transitions, 8 banks
    N_S3_GATE_MEANS = 7    # mean S3 gate per pass
    N_S3_GATE_MINS = 7     # min S3 gate per pass (most suppressed phase)
    N_S2_CONFLICTS = 6     # cosine between consecutive pass deltas
    N_DISPATCH = 4         # combinator weight means (K, I, B, C)
    N_DISPATCH_ENTROPY = 1 # dispatch distribution entropy
    N_COMPUTE_GATE = 2     # mean + active fraction
    N_CYCLE_GATES = 6      # CycleContinue gates (2 per desc pass × 3 desc passes)
    N_EFFECTIVE_CYCLES = 3 # effective cycle count per desc pass
    N_RAW_DELTA_NORMS = 7  # L2 norm of each raw delta
    N_GATED_DELTA_NORMS = 7  # L2 norm of each gated delta
    N_SUPPRESSION_RATIOS = 7  # gated/raw ratio per pass
    N_REGISTER_NORMS = 8   # mean register norm per bank

    INPUT_DIM = (N_S3_GATE_MEANS + N_S3_GATE_MINS + N_S2_CONFLICTS +
                 N_DISPATCH + N_DISPATCH_ENTROPY + N_COMPUTE_GATE +
                 N_CYCLE_GATES + N_EFFECTIVE_CYCLES +
                 N_RAW_DELTA_NORMS + N_GATED_DELTA_NORMS +
                 N_SUPPRESSION_RATIOS + N_REGISTER_NORMS)  # = 65

    def __init__(self, n_passes: int = 5, n_combinators: int = 4):
        super().__init__()
        self.n_passes = n_passes
        self.n_combinators = n_combinators

        # Single linear: operational metrics → per-pass alarm logits
        # Zero-init: alarm starts inert (all factors = 1.0)
        self.alarm_proj = nn.Linear(self.INPUT_DIM, n_passes)
        self.alarm_proj.weight = mx.zeros_like(self.alarm_proj.weight)
        self.alarm_proj.bias = mx.zeros_like(self.alarm_proj.bias)

        # ── Per-combinator dispatch bias (v12 variety fix) ────
        # The v11 gap: alarm could only modulate per-PASS amplitude,
        # but dispatch collapse happens per-COMBINATOR within a pass.
        # 5 knobs can't control 4×5=20 dimensions (Beer's variety law).
        #
        # This head gives the alarm direct per-combinator control:
        # output is an additive bias on CombinatorDispatch logits.
        # If B is declining while entropy drops, alarm can boost B's
        # logit directly without affecting K/I/C.
        #
        # Zero-init: bias starts at [0,0,0,0] (inert, same as v11).
        # Range [-2, +2] via tanh×2: a ±2 shift on logits is significant
        # in softmax (shifts ~7× probability ratio).
        self.dispatch_bias_proj = nn.Linear(self.INPUT_DIM, n_combinators)
        self.dispatch_bias_proj.weight = mx.zeros_like(
            self.dispatch_bias_proj.weight)
        self.dispatch_bias_proj.bias = mx.zeros_like(
            self.dispatch_bias_proj.bias)

    def __call__(
        self, metrics_vector: mx.array,
    ) -> tuple[mx.array, mx.array]:
        """Compute alarm factors and dispatch bias from health metrics.

        Args:
            metrics_vector: (INPUT_DIM,) packed operational metrics.
                All values should be differentiable (no stop_gradient).

        Returns:
            pass_factors: (n_passes,) alarm factors:
              1.0 → no alarm (neutral)
              < 1.0 → pain (suppress this pass)
              > 1.0 → pleasure (amplify, up to 2.0)
            dispatch_bias: (n_combinators,) additive logit bias:
              0.0 → neutral (no alarm intervention on dispatch)
              > 0 → boost this combinator's softmax share
              < 0 → suppress this combinator's softmax share
              Range [-2, +2] — significant in softmax space.
        """
        # Per-pass factors (existing mechanism)
        pass_logits = self.alarm_proj(metrics_vector)
        pass_factors = 1.0 + mx.tanh(pass_logits)

        # Per-combinator dispatch bias (new: variety-matching actuator)
        dispatch_logits = self.dispatch_bias_proj(metrics_vector)
        dispatch_bias = 2.0 * mx.tanh(dispatch_logits)

        return pass_factors, dispatch_bias


# ══════════════════════════════════════════════════════════════════════
# RetrievalRegisters — M kernel ↔ KIBC bridge (v12)
# ══════════════════════════════════════════════════════════════════════


class RetrievalRegisters(nn.Module):
    """Bridge between retrieval (M) and composition (KIBC) pathways.

    During ascending passes, GatedLinearAttention retrieval layers
    accumulate pattern match information. RetrievalRegisters distills
    this into a fixed-size register bank that the descending arm can
    read alongside the existing KIBC registers.

    Architecture:
      - n_retrieval_registers: how many slots M can write to (default: 2)
      - Each register has dimension d_reg_real (same as KIBC registers)
      - Write pathway: residual summary → gated write to register
      - Read: registers are read by S4 and CombinatorDispatch (in model.py)

    The write gate learns when M has found something worth remembering.
    At init, gates are near-zero (M results pass through without
    writing to registers — existing behavior preserved).

    Instrumentation:
      _write_gate_values: (n_retrieval_registers,) — per-register write activity
      _register_norms: (n_retrieval_registers,) — per-register L2 norms
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

        # Write gates: per-register, sigmoid. Bias -3.0 → sigmoid ≈ 0.047
        # Near-zero at init: M doesn't write until it has something useful.
        self.write_gates = [
            nn.Linear(d_model, 1)
            for _ in range(n_retrieval_registers)
        ]
        for wg in self.write_gates:
            wg.bias = mx.full(wg.bias.shape, -3.0)

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
        residual: (B, L, d_model) — ascending arm output

        Returns: updated register list
        """
        # Spatial summary of residual
        summary = residual.mean(axis=(0, 1))  # (d_model,)

        updated = []
        gate_values = []
        for i in range(self.n_retrieval_registers):
            # Gate: should we write?
            wg = mx.sigmoid(
                self.write_gates[i](summary.reshape(1, -1)).reshape(-1))
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

    print("Testing AlgedonicAlert...")
    alarm = AlgedonicAlert(n_passes=7, n_combinators=4)
    mx.eval(alarm.parameters())
    # Input dim should be 65 (v12: 7 passes, 6 transitions, 8 banks)
    assert AlgedonicAlert.INPUT_DIM == 65, \
        f"Expected INPUT_DIM=65, got {AlgedonicAlert.INPUT_DIM}"
    # At init: factors ~1.0, dispatch_bias ~0.0
    metrics_vec = mx.zeros((AlgedonicAlert.INPUT_DIM,))
    factors, dispatch_bias = alarm(metrics_vec)
    mx.eval(factors, dispatch_bias)
    assert factors.shape == (7,), f"Expected (7,), got {factors.shape}"
    assert dispatch_bias.shape == (4,), f"Expected (4,), got {dispatch_bias.shape}"
    for i, f in enumerate(factors.tolist()):
        assert abs(f - 1.0) < 0.01, \
            f"Alarm factor {i} should be ~1.0 at init, got {f:.4f}"
    for i, b in enumerate(dispatch_bias.tolist()):
        assert abs(b) < 0.01, \
            f"Dispatch bias {i} should be ~0.0 at init, got {b:.4f}"
    print(f"  AlgedonicAlert: factors {[f'{f:.3f}' for f in factors.tolist()]} ✓ (all ~1.0)")
    print(f"  AlgedonicAlert: dispatch_bias {[f'{b:.3f}' for b in dispatch_bias.tolist()]} ✓ (all ~0.0)")
    # Verify range: factors [0, 2], dispatch_bias [-2, +2]
    extreme_pos = mx.ones((AlgedonicAlert.INPUT_DIM,)) * 100.0
    alarm.alarm_proj.weight = mx.ones_like(alarm.alarm_proj.weight) * 0.1
    alarm.dispatch_bias_proj.weight = mx.ones_like(alarm.dispatch_bias_proj.weight) * 0.1
    factors_pos, dbias_pos = alarm(extreme_pos)
    mx.eval(factors_pos, dbias_pos)
    for f in factors_pos.tolist():
        assert 0.0 <= f <= 2.0 + 1e-6, f"Factor out of [0, 2]: {f}"
        assert f > 1.5, f"Extreme positive should give factor > 1.5, got {f:.3f}"
    for b in dbias_pos.tolist():
        assert -2.0 - 1e-6 <= b <= 2.0 + 1e-6, f"Dispatch bias out of [-2, 2]: {b}"
        assert b > 1.5, f"Extreme positive should give bias > 1.5, got {b:.3f}"
    extreme_neg = mx.ones((AlgedonicAlert.INPUT_DIM,)) * -100.0
    factors_neg, dbias_neg = alarm(extreme_neg)
    mx.eval(factors_neg, dbias_neg)
    for f in factors_neg.tolist():
        assert 0.0 - 1e-6 <= f <= 2.0 + 1e-6, f"Factor out of [0, 2]: {f}"
        assert f < 0.5, f"Extreme negative should give factor < 0.5, got {f:.3f}"
    for b in dbias_neg.tolist():
        assert -2.0 - 1e-6 <= b <= 2.0 + 1e-6, f"Dispatch bias out of [-2, 2]: {b}"
        assert b < -1.5, f"Extreme negative should give bias < -1.5, got {b:.3f}"
    print(f"  AlgedonicAlert: range verified — factors [0, 2], bias [-2, +2] ✓")
    # Gradient flow test
    alarm2 = AlgedonicAlert(n_passes=7, n_combinators=4)
    mx.eval(alarm2.parameters())

    class AlarmTestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.alarm = AlgedonicAlert(n_passes=7, n_combinators=4)
            self.input_param = mx.zeros((AlgedonicAlert.INPUT_DIM,))
        def __call__(self, _):
            factors, dbias = self.alarm(self.input_param)
            return mx.sum(factors) + mx.sum(dbias)

    atm = AlarmTestModel()
    mx.eval(atm.parameters())
    def alarm_test_loss(m, x):
        return m(x)
    agfn = nn.value_and_grad(atm, alarm_test_loss)
    dummy = mx.zeros((1,))
    alv, ag = agfn(atm, dummy)
    mx.eval(alv, ag)
    print(f"  AlgedonicAlert gradient flow OK: sum={alv.item():.4f} ✓")
    # Parameter count: (65×7 + 7) pass_proj + (65×4 + 4) dispatch_bias_proj
    from mlx.utils import tree_flatten as tf
    n_alarm_params = sum(p.size for _, p in tf(alarm.parameters()))
    expected_params = (65 * 7 + 7) + (65 * 4 + 4)  # = 462 + 264 = 726
    print(f"  AlgedonicAlert params: {n_alarm_params} (expected {expected_params}) ✓")

    print("Testing RetrievalRegisters...")
    ret_regs = RetrievalRegisters(d_model, d_register, n_retrieval_registers=2)
    mx.eval(ret_regs.parameters())
    regs = ret_regs.init_registers()
    assert len(regs) == 2, f"Expected 2 retrieval registers, got {len(regs)}"
    assert regs[0].shape == (d_reg_real,), f"Expected ({d_reg_real},), got {regs[0].shape}"
    print(f"  Init: {len(regs)} registers, shape {regs[0].shape} ✓")

    # Write test
    residual = mx.random.normal((1, 32, d_model))
    updated = ret_regs.write(regs, residual)
    mx.eval(*updated)
    assert len(updated) == 2
    assert updated[0].shape == (d_reg_real,)
    print(f"  Write: updated registers shape {updated[0].shape} ✓")

    # Check write gates start near-closed (bias=-3 → sigmoid ≈ 0.047)
    wgv = ret_regs._write_gate_values
    mx.eval(wgv)
    for i, g in enumerate(wgv.tolist()):
        assert g < 0.15, f"Write gate {i} should start near 0, got {g:.4f}"
    print(f"  Write gates: {[f'{g:.4f}' for g in wgv.tolist()]} (near-zero init) ✓")

    # Check instrumentation
    assert ret_regs._register_norms is not None
    mx.eval(ret_regs._register_norms)
    print(f"  Register norms: {[f'{n:.3f}' for n in ret_regs._register_norms.tolist()]} ✓")

    # Gradient flow
    print("Testing RetrievalRegisters gradient flow...")

    class RetRegTestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.ret_regs = RetrievalRegisters(d_model, d_register, n_retrieval_registers=2)
            self.init_reg = mx.zeros((d_reg_real,))
        def __call__(self, x):
            regs = [self.init_reg, self.init_reg]
            updated = self.ret_regs.write(regs, x)
            return mx.sum(updated[0]) + mx.sum(updated[1])

    rrtm = RetRegTestModel()
    mx.eval(rrtm.parameters())
    def rr_test_loss(m, x):
        return m(x)
    rr_gfn = nn.value_and_grad(rrtm, rr_test_loss)
    x = mx.random.normal((1, 16, d_model))
    rr_lv, rr_g = rr_gfn(rrtm, x)
    mx.eval(rr_lv, rr_g)
    print(f"  RetrievalRegisters gradient flow OK: loss={rr_lv.item():.4f} ✓")

    print("components.py self-test: all ok ✓")
