"""
v10 Model — Tree of VSMs: compressor + kernel-aware dispatcher.

Architecture:

  tokens (B, L) → [VSM-Compressor: ascending, 9 strides, proven]
                       → typed representations (B, L, d_model)
                 → [VSM-Dispatcher: descending, kernel-shaped S1 ops]
                       → enriched representations (B, L, d_model)
                 → [output_norm → tied embedding → logits]
                 → relational loss on Dolma prose

Tree of VSMs (Beer 1972):
  VSM-Compressor (ascending arm, 3 passes: L0↑, L1↑, L2_apex):
    S5: token embedding identity (Qwen3 BBPE)
    S4: StrideStack fine→coarse (intelligence — reads context)
    S3: phase gates (control — what to compress)
    S2: direction signals between passes (anti-oscillation coordination)
    S1: TernaryFFN prep/consolidate (operations — compression)

  VSM-Dispatcher (second arm, 2 passes: L1↓, L0↓):
    S5: kernel function identity (22 ops, 5 types — pre-wired)
    S4: dual-view attention (residual + original embeddings)
    S3: dispatch gates (control — which kernel pathways activate)
    S2: direction signals + register conditioning (coordination)
    S1: KernelDispatch/KernelIntegrate/StrideStack (operations)

  Phase order (dispatch → stride → integrate):
    Phase 0: KernelDispatch — route to 22 kernel op pathways (local)
    Phase 1: StrideStack fine→coarse — propagate dispatched signal (spatial)
    Phase 2: KernelIntegrate — type the context-enriched result (local)

    Rationale: dispatch modulates per-position, then stride propagates
    so that each position sees how its neighbors were dispatched.
    Integration (typing) then has both the local op bias AND spatial
    context to inform its type decision. Prior order (dispatch → integrate
    → stride) produced type-dispatch decoupling: typing couldn't
    distinguish dispatch patterns without spatial context, defaulting
    to FN (56%) regardless of which op was active.

    Session 068 discovered that standard transformer attention self-
    organizes into a logarithmic spiral that always expands outward
    (~1.18x per revolution, ~9.4 layers per revolution). The spiral
    never reverses — there is no "descending" direction in attention.
    Both arms follow the same fine→coarse spiral; they differ in what
    operations they apply (compression vs kernel dispatch), not in
    the direction of attention.

Key design:
  The ascending arm compresses and types (proven in v6, φ-locking).
  The descending arm routes through kernel function pathways — NOT
  compression. Prior sessions (045/054/055/062/065) proved that giving
  the descending arm compression ops causes passthrough. The kernel
  provides the correct shape: dispatch/routing, not compression.

  The 22 kernel ops (from kernel.py, proven at 100% in v9) are pre-wired
  as architectural identity in the dispatcher VSM. The model discovers
  them as easy paths while training on prose — no need to learn
  composition through superpositions.

Output: tied embedding projection (weight sharing with input embed).

License: MIT
"""

from __future__ import annotations

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V10Config
from ternary import TernaryLinear, TernaryEmbedding
from attention import StrideStack, TernaryFFN
from components import (
    S4Ternary,
    S3Ternary,
    MetaS4Ternary,
    S5Reweight,
    S2Coordinator,
)
from kernel_dispatch import KernelDispatch, KernelIntegrate, N_OPS, N_TYPES


# ══════════════════════════════════════════════════════════════════
# V6Compressor — 5-pass bidirectional VSM
# ══════════════════════════════════════════════════════════════════


class V6Compressor(nn.Module):
    """Tree of VSMs: compressor (ascending) + dispatcher (descending).

    5 passes:
      L0_asc → L1_asc → L2_apex → L1_desc → L0_desc

    ASCENDING arm (VSM-Compressor, 3 passes) — shared weights:
      S1: TernaryFFN prep/consolidate (compression — proven in v6)
      S4: StrideStack fine→coarse (reads context across scales)
      Job: compress and type (proven: φ-locking, S3 differentiation)

    SECOND arm (VSM-Dispatcher, 2 passes) — own weights:
      S1: KernelDispatch → StrideStack fine→coarse → KernelIntegrate
      S4: register cross-attention (reads typed representations)
      Job: route through 22 kernel op pathways, propagate, then type

    Both arms spiral outward (fine→coarse). The difference is what
    operations they apply: compression vs kernel dispatch. The spiral
    direction matches the emergent attention geometry discovered in
    standard transformers (~1.18x expansion per revolution).

    Phase order: dispatch (local) → stride (spatial) → integrate (local).
    Dispatch modulates per-position. Stride propagates so each position
    sees neighbor dispatch patterns. Integrate (typing) then has both
    local op bias and spatial context for informed type decisions.

    S2 coordination: between each pair of consecutive passes, a small
    direction signal is fed forward — "Pass N moved the representation
    THIS way." This is Beer's anti-oscillation mechanism: coordination
    between S1 units to prevent unknowing contradiction. The signal
    survives MetaS3 reweighting (S2 infrastructure ≠ S3 control).
    4 transitions, learnable scales starting at 0.01.

    Per-pass S3 control: 5 separate S3Ternary instances.
    """

    REGISTER_NAMES = ("type", "scope", "role")
    N_PASSES = 5
    N_ASC_PASSES = 3   # L0↑, L1↑, L2_apex
    N_DESC_PASSES = 2  # L1↓, L0↓
    PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")

    def __init__(self, cfg: V10Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model
        d_reg = cfg.d_register
        n_reg = cfg.n_registers
        self.d_reg_real = d_reg * 2

        # ── S5: Identity ──────────────────────────────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # Register bank 0: learnable real init
        self.register_inits = {
            f"reg_{name}": mx.zeros((self.d_reg_real,))
            for name in self.REGISTER_NAMES
        }

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # ── S1: Ascending ops (shared across L0↑, L1↑, L2_apex) ──
        #    Compression operations — proven in v6 (φ-locking)
        self.prep = TernaryFFN(d, cfg.d_ff, cfg.dropout)
        self.stride_stack = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.consolidate = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)

        # ── S1: Descending ops (shared across L1↓, L0↓) ──────
        #    Kernel-shaped operations — NOT compression.
        #    KernelDispatch routes to 22 kernel op pathways.
        #    KernelIntegrate combines results with type awareness.
        #    StrideStack reads typed reps across scales (coarse→fine).
        self.kernel_dispatch = KernelDispatch(
            d, n_ops=N_OPS, d_ff=cfg.d_ff, dropout=cfg.dropout,
            n_registers=cfg.n_registers, d_register=cfg.d_register,
            max_cond_banks=5,  # bank_0 + up to 4 ascending banks
            top_k=cfg.dispatch_top_k,
        )
        self.stride_stack_desc = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.kernel_integrate = KernelIntegrate(
            d, n_types=N_TYPES, d_ff=cfg.d_ff_consolidate, dropout=cfg.dropout,
        )

        # ── S4: Intelligence (ascending, shared) ──────────────
        self.s4 = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                            dropout=cfg.dropout)

        # ── S4: Intelligence (descending, own) ────────────────
        self.s4_desc = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                                  dropout=cfg.dropout)

        # ── S3: Per-pass gating (5 instances, always separate) ─
        self.s3_passes = [
            S3Ternary(d, d_reg, n_phases=3, n_registers=n_reg, d_align=d)
            for _ in range(self.N_PASSES)
        ]

        # ── Modulation projections (ascending, shared, 3 per phase) ─
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Modulation projections (descending, own) ──────────
        #    Same 3 phases but different semantics:
        #    phase 0 = dispatch, phase 1 = converge, phase 2 = integrate
        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Multi-cycle input injection gate (HRM-inspired) ──
        # Controls how much of the pre-cycle residual is re-injected
        # at each cycle > 0. HRM adds z_H + input at every L-step;
        # this is the v10 analog: re-ground in the pre-cycle state
        # so dispatch doesn't drift too far from what ascending produced.
        # sigmoid(-4) ≈ 0.018: injection starts nearly silent, model
        # learns to open. Unused when desc_cycles=1.
        self._cycle_inject_gate_raw = mx.array([-4.0])

        # ── Meta-S4 ──────────────────────────────────────────
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── S2: Inter-pass direction coordination ──────────
        #    Beer's anti-oscillation: direction signal between
        #    consecutive passes prevents unknowing contradiction.
        self.s2 = S2Coordinator(d)

        # ── S5: Identity-level pass reweighting ───────────────
        #    Replaces MetaS3. Sees both register banks (S2 state)
        #    AND raw ungated pass deltas (direct S1 output).
        #    Beer's S5 needs ungated view to maintain identity.
        self.s5_reweight = S5Reweight(
            d, d_reg, n_registers=n_reg,
            n_banks=6, n_passes=self.N_PASSES)

        # ── Algedonic channel: persistent descending registers ─
        # Beer's VSM requires feedback from S3 back to S1/S2 —
        # an "algedonic channel" that signals system distress.
        # Without it, the apex can expand without limit because
        # nothing reads the descending arm's state to regulate
        # the ascending arm.
        #
        # Implementation: store the descending registers from the
        # previous forward pass as persistent buffers. The ascending
        # arm's S4 intelligence can read these stale descending
        # registers, creating a cross-step feedback loop:
        #   descending pressure → stored → ascending S4 reads →
        #   ascending S3 adjusts gates → regulated apex output
        #
        # Kernel compute algedonic: the kernel's dispatch weights
        # and compute gate are packed into a register-shaped vector.
        # This tells the ascending arm "the kernel was active,
        # dispatching to these ops, with this compute gate level"
        # so it can adjust compression accordingly (e.g. preserve
        # token identity when the kernel is computing).
        #
        # EMA smoothing (α=0.9) prevents oscillation.
        self._algedonic_ema = 0.9
        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        # Kernel compute: dispatch weights (22) + compute gate (1)
        # packed into d_reg_real, zero-padded. No projection needed —
        # S4's q_proj learns what to extract from the raw values.
        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))

        # ── Op emphasis: S4 register state → per-op modulation ──
        # S4's registers carry type/scope/role from the ascending arm.
        # This projection maps that intelligence to per-op emphasis:
        # "given what S4 observes, which kernel ops should be louder?"
        # EMA-tracked across steps for stability (slowly shifting
        # landscape, not reactive noise).
        # Input: ascending banks (bank_1_asc + bank_2_asc + bank_3)
        #        = 3 banks × 3 registers × d_reg_real
        emphasis_input_dim = 3 * n_reg * self.d_reg_real
        self.emphasis_proj = nn.Linear(emphasis_input_dim, N_OPS)
        # Zero-init: emphasis starts neutral (1.0 for all ops)
        self.emphasis_proj.weight = mx.zeros_like(self.emphasis_proj.weight)
        self.emphasis_proj.bias = mx.zeros_like(self.emphasis_proj.bias)
        self._op_emphasis = mx.ones((N_OPS,))
        self._emphasis_ema = 0.95  # slow-moving — captures trends, not noise

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Cycle injection ────────────────────────────────────────

    @property
    def cycle_inject_gate(self) -> mx.array:
        """Sigmoid gate controlling input injection strength per cycle."""
        return mx.sigmoid(self._cycle_inject_gate_raw)

    # ── Register helpers ──────────────────────────────────────

    def _init_bank0(self) -> list[mx.array]:
        return [self.register_inits[f"reg_{name}"]
                for name in self.REGISTER_NAMES]

    def _fresh_bank(self) -> list[mx.array]:
        return [mx.zeros((self.d_reg_real,))
                for _ in self.REGISTER_NAMES]

    # ── Modulation (additive) ─────────────────────────────────

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        return x + gate * mx.tanh(projs[phase_idx](delta))

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks, target_bank,
                         embed_context=None, op_emphasis=None):
        x_before = x
        raw_phases = []   # ungated phase deltas for S5
        phase_gates = []  # S3 gate values for cross-arm visibility

        # Select ops based on VSM arm
        s4 = self.s4_desc if is_descending else self.s4
        strides = self.stride_stack_desc if is_descending else self.stride_stack

        # S4 scan (intelligence — reads register banks)
        # Descending arm gets dual view: compressed residual + original
        # token embeddings. S4 attends over [residual; embeddings] (2L
        # positions) so it can see both what compression produced AND
        # what the tokens originally were. Critical for dispatch: knowing
        # "this position IS the + token" helps route to arithmetic ops.
        s4_residual = x
        if embed_context is not None:
            s4_residual = mx.concatenate([x, embed_context], axis=1)
        s4_updates, _ = s4(readable_banks, s4_residual)
        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])
                       for i in range(self.cfg.n_registers)]

        if is_descending:
            # ── VSM-Dispatcher: multi-cycle kernel operations ─
            # HRM-inspired multi-timescale: S4 scanned once above
            # (slow/abstract), now dispatch→stride→integrate cycles
            # N times (fast/detailed).
            #
            # Cycle 1: dispatch from compressed reps, propagate
            #          spatially, integrate with local-only context.
            # Cycle 2+: dispatch AGAIN with spatial context from
            #          prior cycle's stride. Each position now knows
            #          what its neighbors dispatched to. Integrate
            #          sees the refined dispatch landscape.
            #
            # Weights shared across cycles (same as HRM sharing
            # L_level weights across L_cycles). S3 gates each
            # cycle's phases independently — same phase_idx reused
            # means the same alignment projections judge cycle 2's
            # delta against the (now-updated) register state.
            #
            # Input injection at cycle > 0: re-ground in the
            # pre-cycle residual (HRM's z_L += z_H + input pattern).
            # Prevents drift from what the ascending arm produced.
            # Gate starts near-zero (sigmoid(-4) ≈ 0.018), learnable.
            #
            # desc_cycles=1: loop runs once, cycle>0 never true,
            # behavior is identical to prior single-cycle code.

            x_anchor = x  # pre-cycle state for injection
            n_cycles = self.cfg.desc_cycles

            for cycle in range(n_cycles):
                # Input injection (HRM pattern): re-ground in anchor
                if cycle > 0:
                    x = x + self.cycle_inject_gate * x_anchor

                # Phase 0: dispatch (route to kernel op pathways)
                dispatch_out = self.kernel_dispatch(
                    x, registers=readable_banks, op_emphasis=op_emphasis)
                delta = dispatch_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 0)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=0, is_descending=True)

                # Phase 1: converge (StrideStack — propagate dispatch outward)
                converge_out = strides(x, reverse=False)
                delta = converge_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 1)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=1, is_descending=True)

                # Phase 2: integrate (type + compute with spatial context)
                dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                delta = integrate_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 2)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=2, is_descending=True)
        else:
            # ── VSM-Compressor: compression S1 operations ─────
            # Phase 0: prep (local feature extraction)
            prep_out = self.prep(x)
            delta = prep_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 0)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=0, is_descending=False)

            # Phase 1: converge (StrideStack fine→coarse)
            converge_out = strides(x, reverse=False)
            delta = converge_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 1)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=1, is_descending=False)

            # Phase 2: consolidate (feature integration)
            consolidate_out = self.consolidate(x)
            delta = consolidate_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 2)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=2, is_descending=False)

        pass_delta = x - x_before
        # Raw delta: sum of ungated phase deltas — what S1 proposed
        # before S3 gating. S5 sees this to maintain identity coherence.
        raw_delta = raw_phases[0]
        for rd in raw_phases[1:]:
            raw_delta = raw_delta + rd
        return x, target_bank, pass_delta, raw_delta, phase_gates

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        """
        tokens (B, L) → logits (B, L, vocab_size), optional loss.

        Output uses tied embedding: logits = h @ embed.weight_T
        """
        B, L = tokens.shape

        # Embed
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        # Capture original embeddings for descending S4's dual view.
        # By pass 3, compression has buried token identity under 3
        # transformation passes. The dispatcher needs raw token identity
        # to route correctly (e.g. "this IS the + token → arithmetic ops").
        x_embed = x

        # Initialize register banks
        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5

        # ── Algedonic channel: read previous descending registers ──
        # These are EMA-smoothed registers from the PREVIOUS forward
        # pass. They carry descending arm pressure (type/dispatch state)
        # back into the ascending arm's S4 intelligence, creating the
        # feedback loop that Beer's VSM requires for S3 regulation.
        # stop_gradient: the algedonic signal is observational, not
        # a training target. Gradient flows forward through the
        # ascending arm normally.
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        # Kernel compute algedonic: which ops fired, how active the
        # compute gate was. Tells ascending arm what downstream needs.
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        asc_s3_gates = []  # ascending S3 gate values for descending arm

        # Pass 0: L0_asc — reads prev descending L0 + kernel compute
        x, bank_1_asc, pd, rd, pg = self._run_level_pass(
            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 0 → Pass 1 (unmodulated — first signal)
        x = x + self.s2.direction_signal(pd, 0)

        # Pass 1: L1_asc — reads prev descending L1 + kernel compute
        x, bank_2_asc, pd, rd, pg = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 1 → Pass 2, modulated by coherence(0,1)
        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])
        x = x + self.s2.direction_signal(pd, 1) * coherence

        # Pass 2: L2_apex — reads kernel compute (helps transition to dispatch)
        x, bank_3, pd, rd, pg = self._run_level_pass(
            x, 2, False, [bank_0, bank_1_asc, bank_2_asc, prev_kernel], bank_3)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # ── Op emphasis: S4 register state → per-op modulation ──
        # After ascending passes, registers carry type/scope/role.
        # Project to per-op emphasis: which ops should be louder?
        emphasis_parts = []
        for bank in [bank_1_asc, bank_2_asc, bank_3]:
            for reg in bank:
                emphasis_parts.append(reg)
        emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
        raw_emphasis = self.emphasis_proj(emphasis_input)           # (N_OPS,)
        op_emphasis = 1.0 + 0.5 * mx.tanh(raw_emphasis)            # [0.5, 1.5]

        # EMA tracking — slowly accumulates S4's emphasis preferences
        self._op_emphasis = mx.stop_gradient(
            self._emphasis_ema * self._op_emphasis
            + (1.0 - self._emphasis_ema) * op_emphasis)

        # ── Pack ascending S3 gates for descending arm ─────────
        # 9 gate values (3 passes × 3 phases) packed into a register-
        # shaped vector. Tells descending S4 what the ascending arm's
        # control decisions were: "prep was gated at 0.8, converge
        # suppressed at 0.3, consolidate open at 0.9" etc.
        # NOT stop_gradient: gradient flows back to ascending S3,
        # teaching it that its gate decisions affect downstream dispatch.
        asc_gate_flat = mx.concatenate(
            [g.reshape(-1) for g in asc_s3_gates])              # (9,)
        asc_gate_vector = mx.concatenate([
            asc_gate_flat,
            mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
        ])
        asc_gate_bank = [asc_gate_vector]

        # S2: direction signal Pass 2 → Pass 3 (ascending→descending)
        #     modulated by coherence(1,2)
        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])
        x = x + self.s2.direction_signal(pd, 2) * coherence

        # Pass 3: L1_desc — S4 sees residual + embeds + ascending gates
        x, bank_2_desc, pd, rd, _ = self._run_level_pass(
            x, 3, True,
            [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank],
            bank_2_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # S2: direction signal Pass 3 → Pass 4, modulated by coherence(2,3)
        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])
        x = x + self.s2.direction_signal(pd, 3) * coherence

        # Pass 4: L0_desc — S4 sees residual + embeds + ascending gates
        x, bank_1_desc, pd, rd, _ = self._run_level_pass(
            x, 4, True,
            [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank],
            bank_1_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # ── Update algedonic buffers (EMA, no gradient) ────────
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic: pack dispatch weights + compute gate
        # into register-shaped vector for ascending arm's next pass
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean,                                        # 22 dims: op distribution
            cg_mean,                                        # 1 dim: compute gate level
            mx.zeros((self.d_reg_real - N_OPS - 1,)),       # padding to d_reg_real
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting — sees registers AND
        # raw ungated deltas (direct view of what operations proposed)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,
                     bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]

        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]

        x = x - total_ungated + total_gated

        # Meta-S4: final structural summary
        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        logits = self.embed.output_proj(x)   # tied ternary embedding, (B, L, vocab_size)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Instrumentation ───────────────────────────────────────

    @staticmethod
    def _entropy_proxy(x: mx.array) -> float:
        """log(mean_var) entropy proxy — same as v6."""
        var_per_feat = mx.var(x, axis=(0, 1))
        mean_var = mx.mean(var_per_feat)
        mx.eval(mean_var)
        return float(mx.log(mean_var + 1e-10).item())

    def forward_instrumented(
        self,
        tokens: mx.array,
    ) -> tuple[mx.array, dict]:
        """Forward pass with full instrumentation. Returns (hidden, metrics).

        Metrics dict contains:
          s3_gates:     list of 5 lists of floats (per pass, per phase;
                        descending passes have 3*desc_cycles phases)
          s5_reweight:  list of 5 floats (per-pass contribution gates from S5)
          s2_conflict:  list of 4 floats (cosine sim between consecutive deltas)
          s2_scales:    list of 4 floats (learnable direction signal scales)
          register_norms: dict of bank_name → list of 3 floats (per register)
          pass_entropy_in:  list of 5 floats
          pass_entropy_out: list of 5 floats
          pass_compression: list of 5 floats (out/in ratio)
          pass_phi_dev:     list of 5 floats (|ratio - 1/φ|)
          desc_cycles:  int — number of dispatch cycles per descending pass
          cycle_inject_gate: float — learned injection strength (sigmoid)
        """
        import math
        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)

        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x  # original embeddings for descending S4 dual view

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5
        all_s3_gates = []
        pass_h_in = []
        pass_h_out = []
        asc_gate_mx = []  # ascending S3 gate values (mx.arrays) for descending arm
        asc_gate_bank = None  # packed after ascending passes
        op_emphasis_inst = None  # computed after ascending passes

        # Algedonic channel: stale descending registers + kernel compute
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        pass_configs = [
            (0, False, lambda: [bank_0, prev_b1d, prev_kernel]),
            (1, False, lambda: [bank_0, bank_1_asc, prev_b2d, prev_kernel]),
            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc, prev_kernel]),
            (3, True,  lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3]),
            (4, True,  lambda: [bank_0, bank_1_asc, bank_2_desc, bank_3]),
        ]
        target_banks = [bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]

        for pi, (pass_idx, is_desc, get_readable) in enumerate(pass_configs):
            h_in = self._entropy_proxy(x)
            pass_h_in.append(h_in)

            x_before = x
            readable = get_readable()
            target = target_banks[pi]

            # Select ops based on VSM arm
            s4 = self.s4_desc if is_desc else self.s4
            strides = self.stride_stack_desc if is_desc else self.stride_stack

            # Descending arm: add ascending S3 gate bank + embed dual view
            if is_desc:
                if asc_gate_bank is not None:
                    readable.append(asc_gate_bank)
                s4_residual = mx.concatenate([x, x_embed], axis=1)
            else:
                s4_residual = x
            s4_updates, _ = s4(readable, s4_residual)
            target = [self.register_norm(target[i] + s4_updates[i])
                      for i in range(self.cfg.n_registers)]

            phase_gates = []
            raw_phases = []  # ungated phase deltas for S5

            if is_desc:
                # ── VSM-Dispatcher: multi-cycle kernel phases ─
                x_anchor = x
                n_cycles = self.cfg.desc_cycles

                for cycle in range(n_cycles):
                    # Input injection (HRM pattern)
                    if cycle > 0:
                        x = x + self.cycle_inject_gate * x_anchor

                    # Phase 0: dispatch
                    dispatch_out = self.kernel_dispatch(
                        x, registers=readable, op_emphasis=op_emphasis_inst)
                    delta = dispatch_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 0, is_descending=True)

                    # Phase 1: converge (propagate dispatch outward)
                    conv_out = strides(x, reverse=False)
                    delta = conv_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 1, is_descending=True)

                    # Phase 2: integrate (type + compute with spatial context)
                    dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                    integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                    delta = integrate_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 2, is_descending=True)
            else:
                # ── VSM-Compressor: compression phases ────────
                # Phase 0: prep
                prep_out = self.prep(x)
                delta = prep_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 0, is_descending=False)

                # Phase 1: converge (fine→coarse)
                conv_out = strides(x, reverse=False)
                delta = conv_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 1, is_descending=False)

                # Phase 2: consolidate
                cons_out = self.consolidate(x)
                delta = cons_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 2, is_descending=False)

            target_banks[pi] = target
            pass_deltas.append(x - x_before)
            # Raw delta: sum of ungated phase deltas for S5
            raw_delta = raw_phases[0]
            for rd in raw_phases[1:]:
                raw_delta = raw_delta + rd
            raw_deltas.append(raw_delta)
            all_s3_gates.append(phase_gates)

            # Pack ascending S3 gates after last ascending pass (pi=2)
            if not is_desc and pi == 2 and asc_gate_mx:
                asc_gate_flat = mx.concatenate(
                    [g.reshape(-1) for g in asc_gate_mx])
                asc_gate_vector = mx.concatenate([
                    asc_gate_flat,
                    mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
                ])
                asc_gate_bank = [asc_gate_vector]

            # Op emphasis after ascending passes complete (pi=2)
            if not is_desc and pi == 2:
                emphasis_parts = []
                for bank in [target_banks[0], target_banks[1], target_banks[2]]:
                    for reg in bank:
                        emphasis_parts.append(reg)
                emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
                raw_emphasis = self.emphasis_proj(emphasis_input)
                op_emphasis_inst = 1.0 + 0.5 * mx.tanh(raw_emphasis)
                mx.eval(op_emphasis_inst)
                self._op_emphasis = mx.stop_gradient(
                    self._emphasis_ema * self._op_emphasis
                    + (1.0 - self._emphasis_ema) * op_emphasis_inst)

            h_out = self._entropy_proxy(x)
            pass_h_out.append(h_out)

            # S2: direction signal to next pass (except after last pass)
            # First signal unmodulated; subsequent signals modulated by
            # coherence between this pass and the previous one.
            if pi < len(pass_configs) - 1:
                signal = self.s2.direction_signal(pass_deltas[-1], pi)
                if pi > 0:
                    coherence = S2Coordinator.coherence_factor(
                        pass_deltas[-2], pass_deltas[-1])
                    signal = signal * coherence
                x = x + signal

        # S2: conflict scores between consecutive pass deltas
        s2_conflict = []
        for i in range(len(pass_deltas) - 1):
            cs = S2Coordinator.conflict_score(pass_deltas[i], pass_deltas[i + 1])
            s2_conflict.append(cs)
        s2_scales = [float(self.s2.scales[i].item())
                     for i in range(S2Coordinator.N_TRANSITIONS)]

        # Re-assign named banks from target_banks
        bank_1_asc = target_banks[0]
        bank_2_asc = target_banks[1]
        bank_3 = target_banks[2]
        bank_2_desc = target_banks[3]
        bank_1_desc = target_banks[4]

        # Update algedonic buffers (EMA, no gradient) — same as forward()
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic — same as forward()
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean, cg_mean,
            mx.zeros((self.d_reg_real - N_OPS - 1,)),
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting (sees registers + raw deltas)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)
        mx.eval(meta_gates)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4
        meta_banks_list = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks_list, x)
        x = self.output_norm(x)

        # Register norms
        reg_norms = {}
        named_banks = {
            "bank_0": bank_0, "bank_1_asc": bank_1_asc,
            "bank_2_asc": bank_2_asc, "bank_3": bank_3,
            "bank_2_desc": bank_2_desc, "bank_1_desc": bank_1_desc,
        }
        for name, bank in named_banks.items():
            norms = []
            for reg in bank:
                mx.eval(reg)
                norms.append(float(mx.sqrt((reg * reg).sum()).item()))
            reg_norms[name] = norms

        # Compression metrics
        pass_compression = []
        pass_phi_dev = []
        for h_in, h_out in zip(pass_h_in, pass_h_out):
            if abs(h_in) > 1e-8:
                ratio = h_out / h_in
            else:
                ratio = 1.0
            pass_compression.append(ratio)
            pass_phi_dev.append(abs(ratio - INV_PHI))

        # Kernel dispatch metrics (from descending arm)
        # KernelDispatch caches _dispatch_weights: (B, L, n_ops)
        # KernelIntegrate caches _type_weights: (B, L, n_types)
        dispatch_weights = None
        type_weights = None
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw = self.kernel_dispatch._dispatch_weights
            mx.eval(dw)
            # Mean over batch and sequence → per-op activation frequency
            dispatch_weights = mx.mean(dw, axis=(0, 1))  # (n_ops,)
            mx.eval(dispatch_weights)
        if hasattr(self.kernel_integrate, '_type_weights'):
            tw = self.kernel_integrate._type_weights
            mx.eval(tw)
            type_weights = mx.mean(tw, axis=(0, 1))  # (n_types,)
            mx.eval(type_weights)

        # Op embedding norms (health check — should be uniform with norm constraint)
        op_emb_norms = None
        if hasattr(self.kernel_dispatch, 'op_embeddings'):
            raw_emb = self.kernel_dispatch.op_embeddings
            mx.eval(raw_emb)
            norms = mx.sqrt(mx.sum(raw_emb * raw_emb, axis=-1) + 1e-8)
            mx.eval(norms)
            op_emb_norms = [float(norms[i].item()) for i in range(norms.shape[0])]

        # Cycle inject gate value
        cig = self.cycle_inject_gate
        mx.eval(cig)

        metrics = {
            "s3_gates": all_s3_gates,
            "s5_reweight": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],
            "op_emphasis": (
                [float(op_emphasis_inst[i].item()) for i in range(N_OPS)]
                if op_emphasis_inst is not None else None
            ),
            "s2_conflict": s2_conflict,
            "s2_scales": s2_scales,
            "register_norms": reg_norms,
            "pass_entropy_in": pass_h_in,
            "pass_entropy_out": pass_h_out,
            "pass_compression": pass_compression,
            "pass_phi_dev": pass_phi_dev,
            "kernel_dispatch_weights": (
                [float(dispatch_weights[i].item()) for i in range(dispatch_weights.shape[0])]
                if dispatch_weights is not None else None
            ),
            "kernel_type_weights": (
                [float(type_weights[i].item()) for i in range(type_weights.shape[0])]
                if type_weights is not None else None
            ),
            "op_embedding_norms": op_emb_norms,
            "desc_cycles": self.cfg.desc_cycles,
            "cycle_inject_gate": float(cig.item()),
        }

        # Compute gate stats (if kernel pathway is active)
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg = self.kernel_integrate._compute_gate  # (B, L, 1)
            mx.eval(cg)
            metrics["compute_gate_mean"] = float(mx.mean(cg).item())
            metrics["compute_gate_max"] = float(mx.max(cg).item())
            metrics["compute_gate_min"] = float(mx.min(cg).item())
            # Fraction of positions where gate > 0.5
            metrics["compute_gate_active"] = float(mx.mean((cg > 0.5).astype(mx.float32)).item())

        return x, metrics


# ══════════════════════════════════════════════════════════════════
# Factory + utilities
# ══════════════════════════════════════════════════════════════════


def create_model(cfg: V10Config) -> V6Compressor:
    """Create and initialize a V6Compressor."""
    model = V6Compressor(cfg)
    mx.eval(model.parameters())
    return model


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count parameters by component."""
    from mlx.utils import tree_flatten

    counts = {"total": 0, "trainable": 0}
    all_params = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())

    counts["total"] = sum(p.size for _, p in all_params)
    counts["trainable"] = sum(p.size for _, p in trainable)

    return counts


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cfg = V10Config(vocab_size=151936, max_seq_len=64)
    model = create_model(cfg)

    # Test forward
    tokens = mx.array([[59, 2809, 90, 37155, 3733, 7981, 1887, 1102,
                         374, 279, 2701, 382, 59, 7265, 90, 31515]])
    targets = mx.array([[2809, 90, 37155, 3733, 7981, 1887, 1102, 374,
                          279, 2701, 382, 59, 7265, 90, 31515, 11035]])

    logits, loss = model(tokens, targets)
    mx.eval(logits, loss)
    print(f"Logits: {logits.shape}")   # (1, 16, 151936)
    print(f"Loss: {loss.item():.4f}")

    params = count_parameters(model)
    print(f"Parameters: total={params['total']:,}  trainable={params['trainable']:,}")

    print("model.py self-test: all ok ✓")
