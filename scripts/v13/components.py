"""VSM control components — S3, S5, S2, AlgedonicAlert.

v13 (register-free): Stride overlaps between fractal bands ARE the registers.
Cross-scale state is carried naturally by the shared StrideStack — no abstract
register vectors needed.

Removed vs previous version:
  - S4Ternary           — register cross-attention (no registers)
  - MetaS4Ternary       — higher-level register coordination (no registers)
  - RetrievalRegisters  — M↔KIBC bridge (no registers)
  - All register-related helpers (_flatten_registers, _flatten_banks, _ternary_1d)

Kept and simplified:
  - S3Ternary      — per-pass 3-phase gating (now: bias + temperature on delta_rms)
  - S5Reweight     — identity-level pass contribution gates (now: delta-means only)
  - S2Coordinator  — inter-pass coherence / direction signals (7 transitions for 8 passes)
  - AlgedonicAlert — VSM alarm channel (8 passes, INPUT_DIM=58 padded to 64)

8-pass hourglass:
  L0↑ → L1↑ → L2↑ → L3↑ → L3↓ → L2↓ → L1↓ → L0↓
  Pass  0       1       2      3      4      5      6      7

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════════
# S3 — Phase-Coherent Gating (register-free)
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Phase-coherent control for a single level-pass.

    3 phases: dispatch / stride / integrate.

    Register-free simplification: gate = sigmoid(bias + temperature * delta_rms)
    where delta_rms = sqrt(mean(delta²)).

    No register alignment, no write projections, no write gates.
    The cross-scale state lives in the shared StrideStack (stride overlaps).

    Per-phase learned temperature and bias (fp32 scalars).
    """

    def __init__(
        self,
        d_model: int,
        n_phases: int = 3,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_phases = n_phases

        # Temperature and bias — fp32 scalars, one per phase
        # temperature init 1.0, bias init 0.0 → gate starts near 0.5
        self.temperature = [mx.ones((1,)) for _ in range(n_phases)]
        self.learned_bias = [mx.zeros((1,)) for _ in range(n_phases)]

    def gate_phase(
        self,
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array,]:
        """Gate a phase's output using delta_rms scalar gate.

        delta:      (B, L, d_model) phase output
        phase_idx:  0 = dispatch, 1 = stride, 2 = integrate

        Returns:
          gate: (1,) scalar gate value (sigmoid)
        """
        delta_rms = mx.sqrt(mx.mean(delta * delta) + 1e-8)
        gate = mx.sigmoid(
            self.learned_bias[phase_idx]
            + self.temperature[phase_idx] * delta_rms
        )
        return (gate,)

    def __call__(
        self,
        deltas: list[mx.array],
    ) -> tuple[list[mx.array], list[mx.array]]:
        """Gate all phases for a pass.

        deltas:    list of n_phases delta tensors, each (B, L, d_model)

        Returns:
          gates:         per-phase gate scalars
        """
        gates = []
        for phase_idx, delta in enumerate(deltas):
            (gate,) = self.gate_phase(delta, phase_idx)
            gates.append(gate)
        return gates


# ══════════════════════════════════════════════════════════════════════
# S5Reweight — Identity-level pass contribution (delta-means only)
# ══════════════════════════════════════════════════════════════════════


class S5Reweight(nn.Module):
    """S5 — Identity-level pass contribution reweighting.

    Register-free simplification:
      - Input: n_passes pass deltas, each (B, T, d_model)
      - Mean each delta to (d_model,)
      - Concatenate → (n_passes * d_model,)
      - Project to (n_passes,) gates via single TernaryLinear
      - Output: (n_passes,) sigmoid gates

    Initialization: bias -2.0 → gates start near-closed (~0.12).
    """

    def __init__(
        self,
        d_model: int,
        n_passes: int,
    ):
        super().__init__()
        self.n_passes = n_passes
        self.d_model = d_model

        # Input: (n_passes * d_model,) padded to multiple of 64 for TernaryLinear
        delta_input_dim = n_passes * d_model
        self._delta_input_padded = ((delta_input_dim + 63) // 64) * 64

        # Output: n_passes, padded to multiple of 16
        self._n_passes_padded = ((n_passes + 15) // 16) * 16

        self.gate_proj = TernaryLinear(
            self._delta_input_padded, self._n_passes_padded, pre_norm=False)

        # Separate bias: -2.0 → gates start near-closed (~0.12)
        self.gate_bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(
        self,
        pass_deltas: list[mx.array],
    ) -> mx.array:
        """Compute per-pass contribution gates.

        pass_deltas: list of n_passes pass deltas, each (B, L, d_model)

        Returns: (n_passes,) sigmoid gates for pass contribution
        """
        # Mean each delta to (d_model,) and concatenate
        means = [delta.mean(axis=(0, 1)) for delta in pass_deltas]  # each (d_model,)
        delta_flat = mx.concatenate(means, axis=-1)  # (n_passes * d_model,)

        # Pad to multiple of 64
        if delta_flat.shape[0] < self._delta_input_padded:
            delta_flat = mx.concatenate([
                delta_flat,
                mx.zeros((self._delta_input_padded - delta_flat.shape[0],))
            ])

        logits = self.gate_proj(delta_flat.reshape(1, -1)).reshape(-1)[:self.n_passes]
        return mx.sigmoid((logits + self.gate_bias) * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S2 — Inter-pass direction coordination (Beer's anti-oscillation)
# ══════════════════════════════════════════════════════════════════════


class S2Coordinator(nn.Module):
    """S2 — Inter-pass direction coordination.

    Beer's S2 prevents oscillation between S1 operational units.
    In V13, the 7 inter-pass transitions carry direction memos so
    each pass is aware of what the predecessor changed.

    8 passes → 7 transitions:
      L0↑→L1↑, L1↑→L2↑, L2↑→L3↑, L3↑→L3↓, L3↓→L2↓, L2↓→L1↓, L1↓→L0↓
    """

    N_TRANSITIONS = 7
    TRANSITION_NAMES = (
        "L0↑→L1↑", "L1↑→L2↑", "L2↑→L3↑",
        "L3↑→L3↓",
        "L3↓→L2↓", "L2↓→L1↓", "L1↓→L0↓",
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

    In V13 (register-free, 8 passes):
      - No register bank norms (registers gone)
      - 8 passes instead of 7
      - INPUT_DIM = 58 (padded to 64 for TernaryLinear group_size)

    Mechanism:
      - Separate gate: per-pass factor ∈ [0, 2] via 1 + tanh(logit)
      - Factor = 1.0 → no alarm (neutral)
      - Factor < 1.0 → pain (suppress this pass)
      - Factor > 1.0 → pleasure (amplify, up to 2×)
      - Multiplies S5Reweight gates: effective = s5_gate × alarm_factor
    """

    # Input metric dimensions (must match _collect_alarm_metrics in model.py)
    # V13: 8 passes, 7 S2 transitions, 8 combinators — no register bank norms
    N_S3_GATE_MEANS = 8       # mean S3 gate per pass
    N_S3_GATE_MINS = 8        # min S3 gate per pass (most suppressed phase)
    N_S2_CONFLICTS = 7        # cosine between consecutive pass deltas (n_passes - 1)
    N_DISPATCH = 8            # combinator weight means (K, I, B, C, D, Y, W, WHNF)
    N_DISPATCH_ENTROPY = 1    # dispatch distribution entropy
    N_COMPUTE_GATE = 2        # mean + active fraction
    N_RAW_DELTA_NORMS = 8     # L2 norm of each raw delta
    N_GATED_DELTA_NORMS = 8   # L2 norm of each gated delta
    N_SUPPRESSION_RATIOS = 8  # gated/raw ratio per pass

    # 8+8+7+8+1+2+8+8+8 = 58
    INPUT_DIM = (N_S3_GATE_MEANS + N_S3_GATE_MINS + N_S2_CONFLICTS +
                 N_DISPATCH + N_DISPATCH_ENTROPY + N_COMPUTE_GATE +
                 N_RAW_DELTA_NORMS + N_GATED_DELTA_NORMS +
                 N_SUPPRESSION_RATIOS)  # = 58

    # TernaryLinear requires in_features divisible by group_size=64.
    # 58 → next multiple of 64 is 64.
    _INPUT_DIM_PADDED = 64

    def __init__(self, n_passes: int = 8, n_combinators: int = 8):
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
# Convenience constructor from V13Config
# ══════════════════════════════════════════════════════════════════════


def make_components(cfg) -> dict:
    """Construct all VSM components from a V13Config.

    Returns a dict of component instances keyed by name:
      s3_passes: list of S3Ternary (one per pass)
      s5:        S5Reweight
      s2:        S2Coordinator
      alarm:     AlgedonicAlert
    """
    from kernel_dispatch import N_COMBINATORS
    return {
        "s3_passes": [
            S3Ternary(d_model=cfg.d_model, n_phases=3)
            for _ in range(cfg.n_passes)
        ],
        "s5": S5Reweight(
            d_model=cfg.d_model,
            n_passes=cfg.n_passes,
        ),
        "s2": S2Coordinator(d_model=cfg.d_model),
        "alarm": AlgedonicAlert(
            n_passes=cfg.n_passes,
            n_combinators=N_COMBINATORS,
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import mlx.core as mx

    d_model = 512
    n_passes = 8

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, n_phases=3)
    delta = mx.random.normal((1, 32, d_model))
    for phase_idx in range(3):
        (gate,) = s3.gate_phase(delta, phase_idx)
        mx.eval(gate)
        assert gate.shape == (1,)
    gates = s3([delta, delta, delta])
    mx.eval(*gates)
    assert len(gates) == 3
    print(f"  S3: {len(gates)} gates, shapes ok ✓")

    print("Testing S5Reweight...")
    s5 = S5Reweight(d_model, n_passes=n_passes)
    pass_deltas = [mx.random.normal((1, 32, d_model)) for _ in range(n_passes)]
    gates_s5 = s5(pass_deltas)
    mx.eval(gates_s5)
    assert gates_s5.shape == (n_passes,)
    print(f"  S5: gates shape {gates_s5.shape} ✓")

    print("Testing S2Coordinator...")
    s2 = S2Coordinator(d_model)
    delta = mx.random.normal((1, 32, d_model))
    for t in range(S2Coordinator.N_TRANSITIONS):
        sig = s2.direction_signal(delta, t)
        mx.eval(sig)
        assert sig.shape == (1, 1, d_model)
    coh = S2Coordinator.coherence_factor(delta, delta)
    mx.eval(coh)
    print(f"  S2: {S2Coordinator.N_TRANSITIONS} transitions, coherence={coh.item():.3f} ✓")

    print("Testing AlgedonicAlert...")
    alarm = AlgedonicAlert(n_passes=n_passes)
    metrics = mx.zeros((AlgedonicAlert.INPUT_DIM,))
    factors = alarm(metrics)
    mx.eval(factors)
    assert factors.shape == (n_passes,)
    assert abs(factors.mean().item() - 1.0) < 1e-5
    print(f"  Alarm: factors shape {factors.shape}, mean={factors.mean().item():.3f} ✓")

    print(f"\n  AlgedonicAlert.INPUT_DIM = {AlgedonicAlert.INPUT_DIM} (padded to {AlgedonicAlert._INPUT_DIM_PADDED})")
    print("\nAll V13 component tests passed ✓")
