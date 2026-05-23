"""VSM control components — per-stack (S3, S2, Algedonic) + controller (S5, S4, S2, MetaS3).

Session 135: Tree of VSMs architecture. Two levels of control.
Session 140: S5 crystal custodian + S5→S4 policy channel.

  Per-stack (S1 operational units):
    S3Ternary      — per-pass gating within a stack
    S2Coordinator  — inter-pass coherence/direction within a stack
    AlgedonicAlert — per-stack health metrics → alarm factors

  Controller (coordinates the tree):
    S5Identity         — the self-model (cortex DMN). GRU state. Reads structured
                         crystal sub-lattice metrics (comp_cluster, whnf_anti,
                         i_separation, cross_crystal) + algedonics. Regulates
                         enforcement, gates S4 proposals. d_identity=64.
                         Broadcasts identity_state to S4 (policy channel).
    S4Intelligence     — global pattern detection from all stacks' algedonics,
                         conditioned on S5 identity state (policy). Proposes
                         meta-param adjustments to S5. Feeds S2.
    S2AntiOscillation  — PID-like inter-stack dampening at register boundaries.
                         P (current coherence) + D (trend, predictive). S4 feedback.
    MetaS3FireAlarm    — S5 existential threat detector. Bypasses S3/S4 hierarchy.
    S5Reweight         — identity-level pass contribution gates across all stacks.

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear
from config import N_STACKS, N_BOUNDARIES


# ══════════════════════════════════════════════════════════════════════
# Per-Stack Components (S1 operational level)
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Single-gate control for a level-pass within a stack.

    gate = sigmoid(learned_bias + temperature * delta_rms)
    """

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model
        self.temperature = mx.ones((1,))
        self.learned_bias = mx.zeros((1,))

    def __call__(self, delta: mx.array) -> mx.array:
        rms = mx.sqrt(mx.mean(delta * delta) + 1e-8)
        gate = mx.sigmoid(self.learned_bias + self.temperature * rms)
        return gate


class S2Coordinator(nn.Module):
    """Inter-pass direction coordination within a stack.

    Carries direction memos between consecutive passes so each pass
    is aware of what its predecessor changed. Anti-oscillation at
    the pass level (within a single stack).
    """

    def __init__(self, d_model: int, n_transitions: int):
        super().__init__()
        self.d_model = d_model
        self.n_transitions = n_transitions

        self.dir_projs = [
            TernaryLinear(d_model, d_model, pre_norm=True)
            for _ in range(n_transitions)
        ]
        for proj in self.dir_projs:
            proj.gamma = proj.gamma * 0.01

        self.scales = [mx.ones((1,)) * 0.01 for _ in range(n_transitions)]
        self.norm = nn.RMSNorm(d_model)

    def direction_signal(self, pass_delta: mx.array, transition_idx: int) -> mx.array:
        """Direction memo from pass N to pass N+1. Returns (1, 1, d_model)."""
        summary = pass_delta.mean(axis=(0, 1))
        projected = self.dir_projs[transition_idx](summary.reshape(1, -1)).reshape(-1)
        signal = self.norm(projected) * self.scales[transition_idx]
        return signal[None, None, :]

    @staticmethod
    def coherence_factor(delta_prev: mx.array, delta_curr: mx.array) -> mx.array:
        """1 + cos(prev, curr) → [0, 2]. stop_gradient on prev."""
        s_prev = mx.stop_gradient(delta_prev.mean(axis=(0, 1)))
        s_curr = delta_curr.mean(axis=(0, 1))
        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)
        cos = dot / (n_prev * n_curr)
        # Session 142: NaN guard — if upstream produced NaN, return neutral
        return mx.where(mx.isnan(cos), mx.array(1.0), 1.0 + cos)


class AlgedonicAlert(nn.Module):
    """Per-stack health metrics → alarm factors.

    Input: packed operational metrics vector (S3 gates, delta norms, etc.)
    Output: per-pass factors in [0, 2] via 1 + tanh(logit).
    1.0 = neutral. <1 = suppress. >1 = amplify.
    """

    def __init__(self, n_passes: int, input_dim: int = 32):
        super().__init__()
        self.n_passes = n_passes
        self.input_dim = input_dim
        self._input_padded = ((input_dim + 63) // 64) * 64
        _n_passes_padded = ((n_passes + 15) // 16) * 16
        self.alarm_proj = TernaryLinear(self._input_padded, _n_passes_padded, pre_norm=False)
        self.alarm_proj.gamma = mx.zeros_like(self.alarm_proj.gamma)

    def __call__(self, metrics_vector: mx.array) -> mx.array:
        n = metrics_vector.shape[-1]
        if n < self._input_padded:
            metrics_vector = mx.concatenate([
                metrics_vector, mx.zeros((self._input_padded - n,))
            ])
        logits = self.alarm_proj(metrics_vector.reshape(1, -1)).reshape(-1)[:self.n_passes]
        return 1.0 + mx.tanh(logits)

    def compute_metrics(
        self,
        s3_gates: list[mx.array],
        pass_deltas: list[mx.array],
        raw_deltas: list[mx.array],
    ) -> mx.array:
        """Pack operational health into a metrics vector.

        Layout per pass: [s3_gate_mean, raw_delta_rms, gated_delta_rms, suppression_ratio]
        = 4 values per pass. Total = 4 * n_passes.
        """
        metrics = []
        for i in range(self.n_passes):
            metrics.append(s3_gates[i].reshape(1))
            raw_rms = mx.sqrt(mx.mean(raw_deltas[i] * raw_deltas[i]) + 1e-8)
            gated_rms = mx.sqrt(mx.mean(pass_deltas[i] * pass_deltas[i]) + 1e-8)
            # Session 142: NaN guard — if activations contain NaN upstream,
            # substitute neutral values to prevent infecting S4/S5 path.
            raw_rms = mx.where(mx.isnan(raw_rms), mx.array(1.0), raw_rms)
            gated_rms = mx.where(mx.isnan(gated_rms), mx.array(1.0), gated_rms)
            metrics.append(raw_rms.reshape(1))
            metrics.append(gated_rms.reshape(1))
            metrics.append((gated_rms / (raw_rms + 1e-8)).reshape(1))
        return mx.concatenate(metrics)


# ══════════════════════════════════════════════════════════════════════
# Controller Components (tree coordination level)
# ══════════════════════════════════════════════════════════════════════


class S5Identity(nn.Module):
    """The self-model and crystal custodian. Cortex analogy: default mode network.

    Session 140: S5 reads structured crystal sub-lattice metrics, not just
    aggregate crystal_loss. This gives S5 a self-image of crystal geometry:
    which sub-lattices are healthy, which are drifting. The identity state
    (d_identity=64) encodes this self-image and is broadcast to S4 as
    the policy channel (S5→S4).

    Crystal sub-lattice metrics (4 scalars):
      comp_cluster   — B/C/D cosine tightness (composition family cohesion)
      whnf_anti      — WHNF anti-correlation with others (terminal separation)
      i_separation   — I independence from K/B/C (identity combinator distinctness)
      cross_crystal  — positive ↔ anti diagonal mean (suppression channel health)

    GRU update: state persists across forward passes (stop_gradient).
    The model learns HOW to read health and HOW to regulate, but the
    state itself evolves as a control process, not a gradient target.

    Regulation output IS in the gradient graph — GD learns that when
    S5 produces this regulation pattern, loss improves.

    d_identity=64: power of 2, divides d_model=512.
    """

    N_CRYSTAL_SUB_METRICS = 5  # crystal_loss + 4 sub-lattice

    def __init__(
        self,
        d_identity: int = 64,
        n_stacks: int = N_STACKS,
        alg_dim: int = 32,
        n_regulation: int = 4,
        n_proposals: int = 4,
        clip: float = 2.0,
        gru_bias_init: float = 2.0,
    ):
        super().__init__()
        self.d_identity = d_identity
        self.n_regulation = n_regulation
        self.clip = clip

        # Persistent identity state — the self-model
        self.identity_state = mx.zeros((d_identity,))

        # READ: system health → coherence reading
        # Input: crystal sub-lattice (5) + per-stack algedonic (n_stacks * alg_dim)
        # [crystal_loss, comp_cluster, whnf_anti, i_separation, cross_crystal, alg_a, alg_b, alg_c]
        health_input_dim = self.N_CRYSTAL_SUB_METRICS + n_stacks * alg_dim
        health_padded = ((health_input_dim + 15) // 16) * 16
        self._health_padded = health_padded
        self._health_raw = health_input_dim
        self.coherence_read = nn.Linear(health_padded, d_identity)

        # GRU UPDATE: [state; reading] → gate, candidate
        self.update_gate = nn.Linear(d_identity * 2, d_identity)
        self.update_candidate = nn.Linear(d_identity * 2, d_identity)
        # Positive bias → slow identity change (conservative at init)
        self.update_gate.bias = mx.full((d_identity,), gru_bias_init)

        # REGULATE: state → enforcement strengths
        # [crystal_enforcement, modulation_strength, gate_freedom, alarm_sensitivity]
        self.regulation_proj = nn.Linear(d_identity, n_regulation)

        # EVALUATE: [state; proposals] → accept/reject scalar
        self.proposal_impact = nn.Linear(d_identity + n_proposals, 1)

    def __call__(
        self,
        crystal_sub_metrics: mx.array,
        all_algedonics: list[mx.array],
        s4_proposals: mx.array,
    ) -> tuple[mx.array, mx.array, mx.array]:
        """S5 identity cycle: read → update → regulate → evaluate.

        Args:
            crystal_sub_metrics: (5,) [crystal_loss, comp_cluster, whnf_anti,
                                       i_separation, cross_crystal]
            all_algedonics: list of (alg_dim,) per stack
            s4_proposals: (n_proposals,) from S4

        Returns:
            regulation: (n_regulation,) sigmoid enforcement strengths
            accepted_proposals: (n_proposals,) gated by identity health
            alarm_level: scalar in (0, 1) from identity state
        """
        # 1. READ — structured crystal self-image + operational health
        health = mx.concatenate([crystal_sub_metrics] + all_algedonics)
        if health.shape[0] < self._health_padded:
            health = mx.concatenate([
                health, mx.zeros((self._health_padded - health.shape[0],))
            ])
        reading = mx.tanh(self.coherence_read(health))

        # 2. GRU UPDATE
        combined = mx.concatenate([self.identity_state, reading])
        gate = mx.sigmoid(self.update_gate(combined))
        candidate = mx.tanh(self.update_candidate(combined))
        new_state = gate * self.identity_state + (1.0 - gate) * candidate
        new_state = mx.clip(new_state, -self.clip, self.clip)

        # Stop gradient: state influences NEXT step, not current gradient
        self.identity_state = mx.stop_gradient(new_state)

        # 3. REGULATE
        regulation = mx.sigmoid(self.regulation_proj(new_state))

        # 4. EVALUATE S4 proposals
        # Accept more when healthy (crystal loss low), reject when stressed
        proposal_ctx = mx.concatenate([new_state, s4_proposals])
        predicted_impact = mx.tanh(self.proposal_impact(proposal_ctx).reshape(()))
        acceptance = mx.sigmoid(predicted_impact * 5.0)  # sharp gate
        accepted_proposals = s4_proposals * acceptance

        # 5. ALARM from identity state (separate from MetaS3 fire alarm)
        # Identity state norm as alarm proxy: large norm = drifting
        state_norm = mx.sqrt(mx.sum(new_state * new_state) + 1e-8)
        alarm_level = mx.sigmoid(state_norm - self.clip * 0.8)  # alarm rises near clip boundary

        return regulation, accepted_proposals, alarm_level


class S4Intelligence(nn.Module):
    """Global pattern detection from all stacks' algedonics.

    Session 140: Conditioned on S5 identity state (policy channel).
    S5→S4: identity_state from t-1 tells S4 who we are — what the
    crystal self-image looks like. S4's pattern detection is biased
    by identity, so proposals are identity-aware.

    Sees the health of the entire tree simultaneously. Produces:
    1. Proposals for S5 (meta-parameter adjustments)
    2. Signal for S2 (where oscillation is forming)
    """

    def __init__(
        self,
        n_stacks: int = N_STACKS,
        alg_dim: int = 32,
        hidden_dim: int = 64,
        n_proposals: int = 4,
        d_identity: int = 64,
    ):
        super().__init__()
        # S4 input: algedonics from all stacks + S5 identity policy
        input_dim = n_stacks * alg_dim + d_identity
        input_padded = ((input_dim + 15) // 16) * 16
        self._input_padded = input_padded
        self._input_raw = input_dim

        # Pattern detection (conditioned on identity)
        self.pattern_proj = nn.Linear(input_padded, hidden_dim)

        # Proposals for S5
        self.proposal_proj = nn.Linear(hidden_dim, n_proposals)

        # Signal for S2 anti-oscillation
        self.s2_signal_proj = nn.Linear(hidden_dim, hidden_dim)

    def __call__(
        self,
        all_algedonics: list[mx.array],
        s5_policy: mx.array,
    ) -> tuple[mx.array, mx.array]:
        """Analyze global health conditioned on identity, produce proposals + S2 signal.

        Args:
            all_algedonics: list of (alg_dim,) per stack
            s5_policy: (d_identity,) S5 identity state from t-1 (stop_gradient)

        Returns:
            proposals: (n_proposals,) tanh-bounded adjustment suggestions
            s2_signal: (hidden_dim,) for S2AntiOscillation
        """
        combined = mx.concatenate(all_algedonics + [s5_policy])
        if combined.shape[0] < self._input_padded:
            combined = mx.concatenate([
                combined, mx.zeros((self._input_padded - combined.shape[0],))
            ])

        hidden = mx.tanh(self.pattern_proj(combined))
        proposals = mx.tanh(self.proposal_proj(hidden))
        s2_signal = mx.tanh(self.s2_signal_proj(hidden))

        return proposals, s2_signal


class S2AntiOscillation(nn.Module):
    """Inter-stack anti-oscillation with PID-like dampening.

    Proportional: dampen where coherence is low (oscillating NOW)
    Derivative: dampen where coherence is DROPPING (predictive)
    S4 feedback: additional dampening where S4 detects problems

    Operates at register boundaries between stacks (A↔B, B↔C).
    """

    def __init__(
        self,
        n_boundaries: int = N_BOUNDARIES,
        s4_signal_dim: int = 64,
        p_gain_init: float = 0.5,
        d_gain_init: float = 0.3,
    ):
        super().__init__()
        self.n_boundaries = n_boundaries

        # PID gains (learnable)
        self.p_gain = mx.full((n_boundaries,), p_gain_init)
        self.d_gain = mx.full((n_boundaries,), d_gain_init)

        # S4 feedback → per-boundary dampening
        s4_padded = ((s4_signal_dim + 15) // 16) * 16
        self._s4_padded = s4_padded
        self._s4_raw = s4_signal_dim
        self.s4_to_dampening = nn.Linear(s4_padded, n_boundaries)

        # Cached previous coherence for derivative (feed-forward)
        self._prev_coherence = None

    def __call__(
        self,
        stack_outputs: list[mx.array],
        s4_signal: mx.array,
    ) -> mx.array:
        """Compute per-boundary dampening factors.

        Args:
            stack_outputs: list of (B, L, d_model) per stack
            s4_signal: (s4_signal_dim,) from S4Intelligence

        Returns:
            dampening: (n_boundaries,) in (0, 1). Higher = more dampening.
        """
        # Inter-stack coherence at boundaries
        coherence = []
        for i in range(len(stack_outputs) - 1):
            a_mean = stack_outputs[i].mean(axis=(0, 1))
            b_mean = stack_outputs[i + 1].mean(axis=(0, 1))
            dot = (a_mean * b_mean).sum()
            n_a = mx.sqrt((a_mean * a_mean).sum() + 1e-8)
            n_b = mx.sqrt((b_mean * b_mean).sum() + 1e-8)
            cos = dot / mx.maximum(n_a * n_b, mx.array(1e-8))
            # Session 142: NaN guard — prevent NaN propagation into dampening
            cos = mx.where(mx.isnan(cos), mx.array(0.0), cos)
            coherence.append(cos)
        coherence = mx.stack(coherence)  # (n_boundaries,)

        # P term: dampen where coherence is low
        p_term = mx.maximum(1.0 - coherence, 0.0) * self.p_gain

        # D term: dampen where coherence is dropping (predictive)
        if self._prev_coherence is not None:
            d_term = mx.maximum(self._prev_coherence - coherence, 0.0) * self.d_gain
        else:
            d_term = mx.zeros_like(p_term)

        # S4 feedback
        s4_padded = s4_signal
        if s4_padded.shape[0] < self._s4_padded:
            s4_padded = mx.concatenate([
                s4_padded, mx.zeros((self._s4_padded - s4_padded.shape[0],))
            ])
        s4_term = mx.sigmoid(self.s4_to_dampening(s4_padded))

        dampening = mx.sigmoid(p_term + d_term + s4_term)

        # Cache for next step (feed-forward prediction)
        self._prev_coherence = mx.stop_gradient(coherence)

        return dampening


class MetaS3FireAlarm(nn.Module):
    """S5 existential threat detector. Bypasses normal S3/S4 hierarchy.

    When alarm fires, all modulations return toward neutral and crystal
    enforcement increases. Prevents cascading failure.

    Input: concatenated algedonics from all stacks + crystal loss.
    Output: alarm_level in (0, 1). Init biased OFF.
    """

    def __init__(
        self,
        n_stacks: int = N_STACKS,
        alg_dim: int = 32,
        bias_init: float = -2.0,
    ):
        super().__init__()
        input_dim = n_stacks * alg_dim + 1  # +1 for crystal loss
        input_padded = ((input_dim + 15) // 16) * 16
        self._input_padded = input_padded
        self._input_raw = input_dim

        self.alarm_proj = nn.Linear(input_padded, 1)
        self.alarm_proj.bias = mx.array([bias_init])

    def __call__(
        self,
        all_algedonics: list[mx.array],
        crystal_loss: mx.array,
    ) -> mx.array:
        """Compute fire alarm level.

        Returns: scalar in (0, 1). Near 0 = all clear. Near 1 = crisis.
        """
        combined = mx.concatenate(all_algedonics + [crystal_loss.reshape(1)])
        if combined.shape[0] < self._input_padded:
            combined = mx.concatenate([
                combined, mx.zeros((self._input_padded - combined.shape[0],))
            ])
        return mx.sigmoid(self.alarm_proj(combined.reshape(1, -1)).reshape(()))


class S5Reweight(nn.Module):
    """Identity-level pass contribution reweighting across all stacks.

    Takes pass deltas from ALL stacks in the tree, computes per-pass
    gates. This operates at the controller level — it sees the full
    picture of all 8 passes across 3 stacks.
    """

    def __init__(self, d_model: int, n_passes: int):
        super().__init__()
        self.n_passes = n_passes
        self.d_model = d_model

        delta_input_dim = n_passes * d_model
        self._delta_input_padded = ((delta_input_dim + 63) // 64) * 64
        _n_passes_padded = ((n_passes + 15) // 16) * 16

        self.gate_proj = TernaryLinear(
            self._delta_input_padded, _n_passes_padded, pre_norm=False)
        self.gate_bias = mx.full((n_passes,), -2.0)
        self.temperature = mx.ones((n_passes,))

    def __call__(self, pass_deltas: list[mx.array]) -> mx.array:
        means = [delta.mean(axis=(0, 1)) for delta in pass_deltas]
        delta_flat = mx.concatenate(means, axis=-1)
        if delta_flat.shape[0] < self._delta_input_padded:
            delta_flat = mx.concatenate([
                delta_flat,
                mx.zeros((self._delta_input_padded - delta_flat.shape[0],))
            ])
        logits = self.gate_proj(delta_flat.reshape(1, -1)).reshape(-1)[:self.n_passes]
        return mx.sigmoid((logits + self.gate_bias) * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    n_passes = 8
    alg_dim = 32
    d_identity = 64
    n_stacks = N_STACKS

    print("=" * 60)
    print("components.py self-test (session 140: S5 crystal custodian + S5→S4 policy)")
    print("=" * 60)

    # ── Per-stack components ──────────────────────────────────
    print("\n── Per-stack components ──")

    print("S3Ternary...")
    s3 = S3Ternary(d_model)
    delta = mx.random.normal((1, 32, d_model))
    gate = s3(delta)
    mx.eval(gate)
    assert gate.shape == (1,)
    print(f"  gate={gate.item():.4f} ✓")

    print("S2Coordinator (3 transitions for 4 passes in a stack)...")
    s2_stack = S2Coordinator(d_model, n_transitions=3)
    for t in range(3):
        sig = s2_stack.direction_signal(delta, t)
        mx.eval(sig)
        assert sig.shape == (1, 1, d_model)
    print(f"  3 direction signals ✓")

    print("AlgedonicAlert (4 passes per stack)...")
    alg = AlgedonicAlert(n_passes=4, input_dim=16)
    metrics = mx.random.normal((16,))
    factors = alg(metrics)
    mx.eval(factors)
    assert factors.shape == (4,)
    print(f"  factors shape={factors.shape}, mean={factors.mean().item():.3f} ✓")

    # ── Controller components ─────────────────────────────────
    print("\n── Controller components ──")

    print("S5Identity (crystal custodian — 5 sub-lattice metrics)...")
    s5 = S5Identity(d_identity=d_identity, n_stacks=n_stacks, alg_dim=alg_dim)
    # crystal_sub_metrics: [crystal_loss, comp_cluster, whnf_anti, i_separation, cross_crystal]
    crystal_sub = mx.array([0.05, 0.3, -0.2, 0.1, -0.4])
    assert crystal_sub.shape == (S5Identity.N_CRYSTAL_SUB_METRICS,)
    algs = [mx.random.normal((alg_dim,)) for _ in range(n_stacks)]
    proposals = mx.random.normal((4,))
    regulation, accepted, alarm = s5(crystal_sub, algs, proposals)
    mx.eval(regulation, accepted, alarm)
    assert regulation.shape == (4,)
    assert accepted.shape == (4,)
    print(f"  regulation={[f'{r:.3f}' for r in regulation.tolist()]}")
    print(f"  accepted proposals norm={mx.sqrt(mx.sum(accepted*accepted)).item():.4f}")
    print(f"  alarm={alarm.item():.4f}")
    id_norm = mx.sqrt(mx.sum(s5.identity_state*s5.identity_state)).item()
    print(f"  identity_state norm={id_norm:.4f}")
    assert id_norm > 0, "identity state should update"
    print(f"  ✓")

    print("S4Intelligence (conditioned on S5 policy)...")
    s4 = S4Intelligence(n_stacks=n_stacks, alg_dim=alg_dim, d_identity=d_identity)
    # S5→S4 policy channel: identity state from t-1
    s5_policy = mx.stop_gradient(s5.identity_state)
    assert s5_policy.shape == (d_identity,)
    s4_proposals, s2_signal = s4(algs, s5_policy)
    mx.eval(s4_proposals, s2_signal)
    assert s4_proposals.shape == (4,)
    assert s2_signal.shape == (64,)
    print(f"  proposals={[f'{p:.3f}' for p in s4_proposals.tolist()]}")
    print(f"  s2_signal norm={mx.sqrt(mx.sum(s2_signal*s2_signal)).item():.4f} ✓")

    print("S2AntiOscillation...")
    s2_ctrl = S2AntiOscillation(n_boundaries=N_BOUNDARIES, s4_signal_dim=64)
    stack_outs = [mx.random.normal((1, 32, d_model)) for _ in range(n_stacks)]
    dampening = s2_ctrl(stack_outs, s2_signal)
    mx.eval(dampening)
    assert dampening.shape == (N_BOUNDARIES,)
    print(f"  dampening={[f'{d:.3f}' for d in dampening.tolist()]} ✓")
    # Second call to test derivative term
    dampening2 = s2_ctrl(stack_outs, s2_signal)
    mx.eval(dampening2)
    print(f"  dampening2 (with D term)={[f'{d:.3f}' for d in dampening2.tolist()]} ✓")

    print("MetaS3FireAlarm...")
    fire = MetaS3FireAlarm(n_stacks=n_stacks, alg_dim=alg_dim, bias_init=-2.0)
    crystal_scalar = mx.array(0.05)
    alarm_level = fire(algs, crystal_scalar)
    mx.eval(alarm_level)
    assert alarm_level.shape == ()
    print(f"  alarm_level={alarm_level.item():.4f} (should be near 0.12) ✓")

    print("S5Reweight...")
    s5r = S5Reweight(d_model=d_model, n_passes=n_passes)
    deltas = [mx.random.normal((1, 32, d_model)) for _ in range(n_passes)]
    gates = s5r(deltas)
    mx.eval(gates)
    assert gates.shape == (n_passes,)
    print(f"  gates mean={gates.mean().item():.4f} ✓")

    # ── Gradient flow ─────────────────────────────────────────
    print("\n── Gradient flow ──")

    class TestControllerGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.s5 = S5Identity(d_identity=64, n_stacks=3, alg_dim=32)
            self.s4 = S4Intelligence(n_stacks=3, alg_dim=32, d_identity=64)
            self.fire = MetaS3FireAlarm(n_stacks=3, alg_dim=32)

        def __call__(self, crystal_sub, algs):
            # S5→S4 policy channel (t-1 identity state)
            s5_policy = mx.stop_gradient(self.s5.identity_state)
            proposals, s2_sig = self.s4(algs, s5_policy)
            reg, accepted, alarm = self.s5(crystal_sub, algs, proposals)
            fire_alarm = self.fire(algs, crystal_sub[0])  # scalar crystal_loss
            return mx.sum(reg) + mx.sum(accepted) + alarm + fire_alarm

    tcg = TestControllerGrad()
    mx.eval(tcg.parameters())

    def ctrl_loss(m, cs, algs):
        return m(cs, algs)

    gfn = nn.value_and_grad(tcg, ctrl_loss)
    cs = mx.array([0.05, 0.3, -0.2, 0.1, -0.4])  # crystal sub-lattice metrics
    test_algs = [mx.random.normal((32,)) for _ in range(3)]
    lv, g = gfn(tcg, cs, test_algs)
    mx.eval(lv, g)
    print(f"  Controller gradient flow OK: output={lv.item():.4f} ✓")

    # Verify S5→S4 loop: second call should produce different proposals
    # because S5 identity_state was updated by the first call
    lv2, g2 = gfn(tcg, cs, test_algs)
    mx.eval(lv2, g2)
    print(f"  S5→S4 loop (2nd pass): output={lv2.item():.4f}")
    assert abs(lv.item() - lv2.item()) > 1e-6, "S5 state should influence S4 proposals"
    print(f"  S5→S4 policy channel verified (outputs differ) ✓")

    print("\n" + "=" * 60)
    print("All component tests passed ✓")
