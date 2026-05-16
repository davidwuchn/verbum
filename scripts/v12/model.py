"""
v12 Model — Dual-layer architecture: KIBC composition + M retrieval.

Evolution from v11: the ascending arm gains a hybrid stride stack that
interleaves KIBC composition passes (StrideStack) with M-retrieval passes
(GatedLinearAttention). Retrieval registers persist across passes and are
read by the descending arm's CombinatorIntegrate to condition application.

Dual-layer design:
  Layer 1 — KIBC composition (inherited from v11):
    Ascending: prep → StrideStack → consolidate
    Descending: CombinatorDispatch → StrideStack → CombinatorIntegrate
  Layer 2 — M retrieval (new in v12):
    Ascending: HybridStrideStack alternates composition + GLA retrieval
    Retrieval registers: 2 persistent registers written by ascending arm,
      read by descending CombinatorIntegrate to ground beta-reduction.

The retrieval layer provides associative memory as a continuous substrate:
tokens that appeared many positions ago can be retrieved via GLA's
recurrent state, complementing the KIBC combinator's logical structure.

Architecture:
  Ascending arm (4 passes): HybridStrideStack (KIBC + GLA)
    Retrieval registers updated after each ascending stride pass.
  Descending arm (3 passes): KIBC combinator dispatch (unchanged)
    CombinatorIntegrate conditioned on retrieval registers.
  Self-regulating cycles (desc_max_cycles=3): unchanged from v11
      Cycle 0 — IDENTIFY: which combinator?
      Cycle 1 — RESOLVE:  find arguments
      Cycle 2 — PRODUCE:  apply reduction (informed by retrieval)

Symmetric hourglass (7 passes):
  L0↑ → L1↑ → L2↑ → L3_apex → L2↓ → L1↓ → L0↓
  Pass  0       1       2         3       4      5      6

License: MIT
"""

from __future__ import annotations

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V12Config
from ternary import TernaryLinear, TernaryEmbedding
from attention import StrideStack, HybridStrideStack, DedicatedStrideStacks, TernaryFFN
from components import (
    S4Ternary,
    S3Ternary,
    MetaS4Ternary,
    S5Reweight,
    S2Coordinator,
    CycleContinue,
    AlgedonicAlert,
    S4ProposalHead,
    AbstractionRegularizer,
    RetrievalRegisters,
)
from kernel_dispatch import CombinatorDispatch, CombinatorIntegrate, N_COMBINATORS


# ══════════════════════════════════════════════════════════════════
# V12Model — Dual-layer: KIBC composition + M retrieval via GLA
# ══════════════════════════════════════════════════════════════════


class V12Model(nn.Module):
    """Dual-layer VSM: KIBC composition (ascending/descending) + M retrieval.

    7 passes: L0↑ → L1↑ → L2↑ → L3_apex → L2↓ → L1↓ → L0↓

    Register semantics (v12):
      reg 0: combinator — K/I/B/C identity at this position
      reg 1: binding_depth — how many lambdas deep (0=free, 1=bound, ...)
      reg 2: phase — recognize / identify / resolve / produce

    Retrieval register semantics (v12, new):
      ret_0: associative retrieval state — recent binding context
      ret_1: associative retrieval state — long-range argument memory
    """

    REGISTER_NAMES = ("combinator", "binding_depth", "phase")
    RETRIEVAL_REGISTER_NAMES = tuple(f"ret_{i}" for i in range(2))
    N_PASSES = 7
    N_ASC_PASSES = 4
    N_DESC_PASSES = 3
    PASS_NAMES = ("L0_asc", "L1_asc", "L2_asc", "L3_apex",
                  "L2_desc", "L1_desc", "L0_desc")

    def __init__(self, cfg: V12Config):
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

        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # ── S1: Ascending ops (shared across 3 passes) ────────
        self.prep = TernaryFFN(d, cfg.d_ff, cfg.dropout)
        n_mirrors = cfg.n_q_mirrors if cfg.use_q_mirrors else 0
        self.stride_stack = HybridStrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
            stride_is_retrieval=cfg.stride_is_retrieval,
            d_state=cfg.d_state,
            n_q_mirrors=n_mirrors,
        )
        self.consolidate = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)

        # ── Retrieval registers (v12) ─────────────────────────
        self.retrieval_registers = RetrievalRegisters(
            d, cfg.d_register, cfg.n_retrieval_registers)

        # ── S1: Descending ops (shared across 2 passes) ───────
        #    KIBC combinator dispatch + N abstraction slots
        self.combinator_dispatch = CombinatorDispatch(
            d, n_combinators=N_COMBINATORS,
            n_abstraction_slots=cfg.n_abstraction_slots,
            d_ff=cfg.d_ff,
            dropout=cfg.dropout,
            n_registers=cfg.n_registers, d_register=cfg.d_register,
            max_cond_banks=7,  # v12: up to 7 readable banks for descending passes
            dispatch_ratio=cfg.dispatch_ratio,
        )
        self.desc_plates = DedicatedStrideStacks(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
            n_q_mirrors=n_mirrors,
            n_combinators=cfg.n_combinators,
        )
        self.combinator_integrate = CombinatorIntegrate(
            d, n_combinators=N_COMBINATORS,
            n_abstraction_slots=cfg.n_abstraction_slots,
            d_ff=cfg.d_ff_consolidate, dropout=cfg.dropout,
            d_register=cfg.d_register,
            n_retrieval_registers=cfg.n_retrieval_registers,
        )

        # ── S4: Intelligence ──────────────────────────────────
        self.s4 = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                            dropout=cfg.dropout)
        self.s4_desc = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                                  dropout=cfg.dropout)

        # ── S3: Per-pass gating (7 separate instances) ─────────
        self.s3_passes = [
            S3Ternary(d, d_reg, n_phases=3, n_registers=n_reg, d_align=d)
            for _ in range(self.N_PASSES)
        ]

        # ── Modulation projections ────────────────────────────
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False) for _ in range(3)]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False) for _ in range(3)]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Multi-cycle injection gate ─────────────────────────
        self._cycle_inject_gate_raw = mx.array([-4.0])

        # ── S3 cycle continuation gate ─────────────────────────
        if cfg.desc_max_cycles > 1:
            self.cycle_continue = CycleContinue(
                cfg.d_register, n_registers=cfg.n_registers)

        # ── Meta-S4 ──────────────────────────────────────────
        # Banks: [bank_0, bank_1_desc, bank_3_desc, bank_4_apex] = 4
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── S2: Direction coordination ─────────────────────────
        self.s2 = S2Coordinator(d)

        # ── S5: Pass reweighting ──────────────────────────────
        # 8 banks: bank_0, bank_1_asc, bank_2_asc, bank_3_asc,
        #          bank_4_apex, bank_3_desc, bank_2_desc, bank_1_desc
        self.s5_reweight = S5Reweight(
            d, d_reg, n_registers=n_reg,
            n_banks=8, n_passes=self.N_PASSES)

        # ── Algedonic alert (Beer's fire alarm: S1→S5 bypass) ──
        self.algedonic = AlgedonicAlert(n_passes=self.N_PASSES)

        # ── Algedonic channel ──────────────────────────────────
        self._algedonic_ema = 0.9
        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_3_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        # Combinator algedonic: 4 combinator weights + 1 compute gate
        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))
        # Retrieval register EMA (v12): carry retrieval state across steps
        self._prev_retrieval_regs = [
            mx.zeros((self.d_reg_real,)) for _ in range(cfg.n_retrieval_registers)]
        # ── S4→S3 cycle budget: intelligence → control channel ──
        # S4 observes the residual stream and register state, then
        # produces a scalar bias that shifts CycleContinue's gate.
        # This is Beer's S4→S3 policy channel: intelligence tells
        # control when to stop cycling.
        #
        # Simple content (pronouns, punctuation): bias < 0 → fewer cycles
        # Complex content (lambda application, nested binding): bias > 0 → more
        #
        # Zero-init: starts inert (CycleContinue behaves exactly as before).
        # tanh×4 clamp: bias ∈ [-4, +4], matching CycleContinue's logit range.
        _cycle_budget_input_dim = 3 * n_reg * self.d_reg_real
        # cycle_budget_proj: TernaryLinear padded to 16, take [:1], + bias.
        _cycle_budget_padded = ((16 + 15) // 16) * 16  # = 16
        self.cycle_budget_proj = TernaryLinear(
            _cycle_budget_input_dim, _cycle_budget_padded, pre_norm=False)
        # Zero gamma: starts inert (CycleContinue unaffected at init)
        self.cycle_budget_proj.gamma = mx.zeros_like(
            self.cycle_budget_proj.gamma)
        self.cycle_budget_bias = mx.zeros((1,))
        self._cycle_budget_bias = mx.array(0.0)

        # ── S4→S5 abstraction proposal pathway ────────────────
        if cfg.n_abstraction_slots > 0:
            self.proposal_head = S4ProposalHead(
                d_model=d,
                n_abstraction_slots=cfg.n_abstraction_slots,
                d_register=cfg.d_register,
                n_registers=n_reg,
                n_banks=3,
            )
            # Alarm-gate threshold: learnable, init conservative
            self.proposal_threshold = mx.array(
                [cfg.abstraction_proposal_threshold_init])
            # Track dead slots for recycling
            self._slot_dead_steps = mx.zeros((cfg.n_abstraction_slots,))

        # ── Holographic loss schedule (set by train loop) ────
        self._holo_lambda_effective = 0.0

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Helpers ───────────────────────────────────────────────

    @property
    def cycle_inject_gate(self) -> mx.array:
        return mx.sigmoid(self._cycle_inject_gate_raw)

    def _init_bank0(self) -> list[mx.array]:
        return [self.register_inits[f"reg_{name}"]
                for name in self.REGISTER_NAMES]

    def _fresh_bank(self) -> list[mx.array]:
        return [mx.zeros((self.d_reg_real,))
                for _ in self.REGISTER_NAMES]

    def _init_retrieval_registers(self) -> list[mx.array]:
        """Initialise retrieval registers from the module's learned state."""
        return self.retrieval_registers.init_registers()

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        return x + gate * mx.tanh(projs[phase_idx](delta))

    # ── Alarm metrics collection ─────────────────────────────

    @staticmethod
    def _delta_rms(delta: mx.array) -> mx.array:
        """RMS norm of a (B, L, d) delta, scalar. Differentiable."""
        return mx.sqrt(mx.mean(delta * delta) + 1e-8)

    def _collect_alarm_metrics(
        self,
        all_s3_gates: list[list],
        pass_deltas: list[mx.array],
        raw_deltas: list[mx.array],
        all_pass_alarm: list[dict],
        all_banks: list[list[mx.array]],
    ) -> mx.array:
        """Pack ~48 operational health metrics into a single vector.

        All values are end-to-end differentiable (live tensors, no
        stop_gradient). This is what Beer's algedonic channel monitors.

        Returns: (48,) metrics vector for AlgedonicAlert.
        """
        metrics = []

        # 1. S3 gate means per pass (7 scalars)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_sum = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_sum = gate_sum + g
                metrics.append(gate_sum / len(pass_gates))
            else:
                metrics.append(mx.array(0.5))

        # 2. S3 gate mins per pass (7 scalars)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_min = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_min = mx.minimum(gate_min, g)
                metrics.append(gate_min)
            else:
                metrics.append(mx.array(0.5))

        # 3. S2 conflict cosines — differentiable (6 scalars)
        for i in range(self.N_PASSES - 1):
            s_prev = pass_deltas[i].mean(axis=(0, 1))
            s_curr = pass_deltas[i + 1].mean(axis=(0, 1))
            dot = (s_prev * s_curr).sum()
            n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
            n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)
            metrics.append(dot / (n_prev * n_curr))

        # 4. Dispatch weight means K,I,B,C (4 scalars)
        # Accumulate live dispatch weights from descending passes
        dispatch_accum = None
        n_desc = 0
        for pa in all_pass_alarm:
            dw = pa.get('dispatch_weights_live')
            if dw is not None:
                dw_mean = mx.mean(dw, axis=(0, 1))  # (4,)
                if dispatch_accum is None:
                    dispatch_accum = dw_mean
                else:
                    dispatch_accum = dispatch_accum + dw_mean
                n_desc += 1
        if dispatch_accum is not None and n_desc > 0:
            dispatch_mean = dispatch_accum / n_desc  # (4,)
            for i in range(N_COMBINATORS):
                metrics.append(dispatch_mean[i])
        else:
            for _ in range(N_COMBINATORS):
                metrics.append(mx.array(0.25))

        # 5. Dispatch entropy (1 scalar)
        #    -sum(p log p) — low entropy = collapsed dispatch
        if dispatch_accum is not None and n_desc > 0:
            p = dispatch_mean
            entropy = -mx.sum(p * mx.log(p + 1e-8))
            metrics.append(entropy)
        else:
            metrics.append(mx.array(1.386))  # ln(4) — uniform

        # 6. Compute gate: mean + active fraction (2 scalars)
        cg_accum = None
        cg_count = 0
        for pa in all_pass_alarm:
            cg = pa.get('compute_gate_live')
            if cg is not None:
                cg_accum = mx.mean(cg) if cg_accum is None \
                    else (cg_accum + mx.mean(cg))
                cg_count += 1
        if cg_accum is not None and cg_count > 0:
            cg_mean = cg_accum / cg_count
            metrics.append(cg_mean)
            # Active fraction: soft approximation (mean of gate values)
            metrics.append(cg_mean)  # at init these are the same
        else:
            metrics.append(mx.array(0.0))
            metrics.append(mx.array(0.0))

        # 7. CycleContinue gates (6 scalars, padded)
        cycle_gates_flat = []
        for pa in all_pass_alarm:
            for cg in pa.get('cycle_continue_gates', []):
                cycle_gates_flat.append(cg)
        # Pad to 6 (2 gates × 3 desc passes)
        while len(cycle_gates_flat) < 6:
            cycle_gates_flat.append(mx.array(0.5))  # neutral padding
        for cg in cycle_gates_flat[:6]:
            metrics.append(cg)

        # 8. Effective cycles per desc pass (3 scalars)
        #    Only descending passes (last N_DESC_PASSES) have cycles
        eff_cycles_list = []
        for pa in all_pass_alarm:
            cc_gates = pa.get('cycle_continue_gates', [])
            if cc_gates:
                eff = mx.array(1.0)
                cumul = mx.array(1.0)
                for cg in cc_gates:
                    cumul = cumul * cg
                    eff = eff + cumul
                eff_cycles_list.append(eff)
        # Pad to exactly 3 (one per desc pass)
        while len(eff_cycles_list) < 3:
            eff_cycles_list.append(mx.array(1.0))
        for ec in eff_cycles_list[:3]:
            metrics.append(ec)

        # 9. Raw delta RMS norms (7 scalars)
        for rd in raw_deltas:
            metrics.append(self._delta_rms(rd))

        # 10. Gated delta RMS norms (7 scalars)
        for pd in pass_deltas:
            metrics.append(self._delta_rms(pd))

        # 11. S3 suppression ratio per pass (7 scalars)
        #     gated_norm / raw_norm — how much S3 is filtering
        for pd, rd in zip(pass_deltas, raw_deltas):
            gated_rms = self._delta_rms(pd)
            raw_rms = self._delta_rms(rd)
            metrics.append(gated_rms / (raw_rms + 1e-8))

        # 12. Register bank mean norms (8 scalars)
        for bank in all_banks:
            bank_norm_sum = mx.array(0.0)
            for reg in bank:
                bank_norm_sum = bank_norm_sum + mx.sqrt(
                    mx.sum(reg * reg) + 1e-8)
            metrics.append(bank_norm_sum / len(bank))

        # Ensure all metrics are 0-d arrays and concatenate
        metrics_flat = [m.reshape(1) if m.ndim == 0 else m.reshape(1)
                        for m in metrics]
        metrics_vector = mx.concatenate(metrics_flat)
        return metrics_vector

    # ── Core level-pass ───────────────────────────────────────

    def _stride_range_for_pass(self, pass_idx: int) -> tuple[int, int] | None:
        """Return stride index range for this pass, or None if fractal bands disabled."""
        if not self.cfg.fractal_stride_bands:
            return None
        if pass_idx < len(self.cfg.stride_band_ranges):
            return self.cfg.stride_band_ranges[pass_idx]
        return None

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks,
                         target_bank, embed_context=None,
                         proposal_delta=None,
                         ret_regs=None,
                         cycle_budget_bias=None):
        x_before = x
        raw_phases = []
        phase_gates = []
        # Alarm metrics: live (differentiable) values for AlgedonicAlert
        pass_alarm = {
            'cycle_continue_gates': [],  # live CycleContinue gate values
            'dispatch_weights_live': None,  # (B, L, 4) live dispatch weights
            'compute_gate_live': None,  # (B, L, 1) live compute gate
            'retrieval_gate_mean': None,  # mean gate across retrieval strides
            'retrieval_memory_norms': None,  # per-stride GLA memory norms
        }

        s4 = self.s4_desc if is_descending else self.s4
        strides = self.stride_stack if not is_descending else None  # desc uses desc_plates

        # S4 scan
        s4_residual = x
        if embed_context is not None:
            s4_residual = mx.concatenate([x, embed_context], axis=1)
        s4_updates, _ = s4(readable_banks, s4_residual)
        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])
                       for i in range(self.cfg.n_registers)]

        if is_descending:
            # ── Combinator dispatch cycles ─────────────────────
            x_anchor = x
            max_cycles = self.cfg.desc_max_cycles
            cumulative_gate = mx.array(1.0)

            for cycle in range(max_cycles):
                x_cycle_start = x

                if cycle > 0:
                    x = x + self.cycle_inject_gate * x_anchor

                # Phase 0: dispatch (which combinator/slot?)
                dispatch_out = self.combinator_dispatch(
                    x, registers=readable_banks,
                    proposal_delta=proposal_delta)
                delta = dispatch_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 0)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=0, is_descending=True)

                # Phase 1: converge (propagate spatially via KIBC dedicated plates)
                # Each combinator gets its own StrideStack; dispatch weights blend outputs.
                # dispatch_weights_live is the DIFFERENTIABLE version — gradients flow
                # from plate outputs back through dispatch (no stop_gradient here).
                dw_kibc = self.combinator_dispatch._dispatch_weights_live[..., :self.cfg.n_combinators]

                converge_out = self.desc_plates(
                    x, dispatch_weights=dw_kibc,
                    reverse=self.cfg.desc_stride_reverse,
                    stride_range=self._stride_range_for_pass(pass_idx))
                delta = converge_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 1)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=1, is_descending=True)

                # Phase 2: integrate (apply combinator reduction)
                dw = (self.combinator_dispatch._dispatch_weights
                      if hasattr(self.combinator_dispatch, '_dispatch_weights')
                      else None)
                # Pass slot embeddings for context in FFN pathway
                slot_emb = None
                if (self.cfg.n_abstraction_slots > 0
                        and hasattr(self.combinator_dispatch,
                                    '_normalize_slot_embeddings')):
                    slot_emb = (self.combinator_dispatch
                                ._normalize_slot_embeddings())
                    if proposal_delta is not None:
                        slot_emb = slot_emb + proposal_delta
                    slot_emb = (slot_emb
                                * self.combinator_dispatch.slot_gates[:, None])
                integrate_out = self.combinator_integrate(
                    x, dispatch_weights=dw, slot_embeddings=slot_emb,
                    retrieval_registers=ret_regs)
                delta = integrate_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 2)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=2, is_descending=True)

                # Scale by cumulative gate
                cycle_contribution = x - x_cycle_start
                x = x_cycle_start + cumulative_gate * cycle_contribution

                # S3 continuation
                if cycle < max_cycles - 1 and max_cycles > 1:
                    cont_gate = self.cycle_continue(
                        target_bank, budget_bias=cycle_budget_bias)
                    pass_alarm['cycle_continue_gates'].append(cont_gate)
                    cumulative_gate = cumulative_gate * cont_gate

            # Capture live (differentiable) dispatch/compute metrics
            # from the LAST cycle — most recent computation
            if hasattr(self.combinator_dispatch, '_dispatch_weights_live'):
                pass_alarm['dispatch_weights_live'] = \
                    self.combinator_dispatch._dispatch_weights_live
            if hasattr(self.combinator_integrate, '_compute_gate_live'):
                pass_alarm['compute_gate_live'] = \
                    self.combinator_integrate._compute_gate_live
        else:
            # ── Ascending compression ──────────────────────────
            prep_out = self.prep(x)
            delta = prep_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 0)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=0, is_descending=False)

            converge_out = strides(x, reverse=False,
                                   stride_range=self._stride_range_for_pass(pass_idx))
            delta = converge_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 1)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=1, is_descending=False)

            # ── Write retrieval registers after ascending stride pass ──
            if ret_regs is not None:
                ret_regs = self.retrieval_registers.write(ret_regs, x)
            # Capture retrieval instrumentation from HybridStrideStack
            if hasattr(strides, '_retrieval_gate_means') and strides._retrieval_gate_means:
                pass_alarm['retrieval_gate_means'] = dict(strides._retrieval_gate_means)
            if hasattr(strides, '_retrieval_memory_norms'):
                pass_alarm['retrieval_memory_norms'] = strides._retrieval_memory_norms

            consolidate_out = self.consolidate(x)
            delta = consolidate_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 2)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=2, is_descending=False)

        pass_delta = x - x_before
        raw_delta = raw_phases[0]
        for rd in raw_phases[1:]:
            raw_delta = raw_delta + rd
        return x, target_bank, pass_delta, raw_delta, phase_gates, pass_alarm, ret_regs

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape

        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3_asc = self._fresh_bank()
        bank_4_apex = self._fresh_bank()
        bank_3_desc = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []
        all_s3_gates = []       # per-pass list of gate values (for alarm)
        all_pass_alarm = []     # per-pass alarm metrics dicts

        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_b3d = [mx.stop_gradient(r) for r in self._prev_bank_3_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        asc_s3_gates = []

        # Initialise retrieval registers (v12)
        ret_regs = self._init_retrieval_registers()

        # Pass 0: L0↑
        x, bank_1_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        x = x + self.s2.direction_signal(pd, 0)

        # Pass 1: L1↑
        x, bank_2_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])
        x = x + self.s2.direction_signal(pd, 1) * coherence

        # Pass 2: L2↑
        x, bank_3_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 2, False,
            [bank_0, bank_1_asc, bank_2_asc, prev_b3d, prev_kernel], bank_3_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])
        x = x + self.s2.direction_signal(pd, 2) * coherence

        # Pass 3: L3_apex
        x, bank_4_apex, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 3, False,
            [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, prev_kernel], bank_4_apex,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)

        # ── S4→S3 cycle budget bias ───────────────────────────
        # Ascending register banks → scalar bias for CycleContinue.
        # S4 decides: is this content worth multiple dispatch cycles?
        cycle_budget_parts = []
        for bank in [bank_1_asc, bank_2_asc, bank_3_asc]:
            for reg in bank:
                cycle_budget_parts.append(reg)
        cycle_budget_input = mx.concatenate(cycle_budget_parts, axis=-1)
        raw_budget = (
            self.cycle_budget_proj(cycle_budget_input.reshape(1, -1)).reshape(-1)[..., :1]
            + self.cycle_budget_bias
        ).reshape(())
        cycle_budget_bias = 4.0 * mx.tanh(raw_budget)  # [-4, +4]
        self._cycle_budget_bias = mx.stop_gradient(
            0.95 * self._cycle_budget_bias
            + 0.05 * cycle_budget_bias)

        # ── S4→S5 abstraction proposal ─────────────────────────
        proposal_delta = None
        if self.cfg.n_abstraction_slots > 0:
            proposal_delta, proposal_conf, _ = self.proposal_head(
                cycle_budget_input)
            # Cache for probing
            self._proposal_confidence = mx.stop_gradient(proposal_conf)

            # Alarm-gate modulation: use alarm from previous step
            # (alarm hasn't been computed yet for this step, but the
            # algedonic EMA carries forward). Use pass-0 alarm factor
            # as the S5 receptivity signal.
            # At init: alarm=1.0, confidence=0.1, threshold=1.0
            #   gate = sigmoid(1.0 * 0.1 - 1.0) = sigmoid(-0.9) ≈ 0.29
            #   Gentle, but not zero — gradient can explore.
            # During training: high alarm → gate opens more
            alarm_signal = mx.array(1.0)  # will be modulated by live alarm
            proposal_gate = mx.sigmoid(
                alarm_signal * proposal_conf - self.proposal_threshold)
            proposal_delta = proposal_delta * proposal_gate

        # ── Pack ascending S3 gates for descending arm ─────────
        asc_gate_flat = mx.concatenate(
            [g.reshape(-1) for g in asc_s3_gates])
        asc_gate_vector = mx.concatenate([
            asc_gate_flat,
            mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
        ])
        asc_gate_bank = [asc_gate_vector]

        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])
        x = x + self.s2.direction_signal(pd, 3) * coherence

        # Pass 4: L2↓
        x, bank_3_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 4, True,
            [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, bank_4_apex, asc_gate_bank],
            bank_3_desc, embed_context=x_embed,
            proposal_delta=proposal_delta,
            ret_regs=ret_regs,
            cycle_budget_bias=cycle_budget_bias)
        pass_deltas.append(pd); raw_deltas.append(rd)
        all_s3_gates.append(pg); all_pass_alarm.append(pa)

        coherence = S2Coordinator.coherence_factor(pass_deltas[3], pass_deltas[4])
        x = x + self.s2.direction_signal(pd, 4) * coherence

        # Pass 5: L1↓
        x, bank_2_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 5, True,
            [bank_0, bank_1_asc, bank_3_desc, bank_4_apex, asc_gate_bank],
            bank_2_desc, embed_context=x_embed,
            proposal_delta=proposal_delta,
            ret_regs=ret_regs,
            cycle_budget_bias=cycle_budget_bias)
        pass_deltas.append(pd); raw_deltas.append(rd)
        all_s3_gates.append(pg); all_pass_alarm.append(pa)

        coherence = S2Coordinator.coherence_factor(pass_deltas[4], pass_deltas[5])
        x = x + self.s2.direction_signal(pd, 5) * coherence

        # Pass 6: L0↓
        x, bank_1_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 6, True,
            [bank_0, bank_1_asc, bank_2_desc, bank_4_apex, asc_gate_bank],
            bank_1_desc, embed_context=x_embed,
            proposal_delta=proposal_delta,
            ret_regs=ret_regs,
            cycle_budget_bias=cycle_budget_bias)
        pass_deltas.append(pd); raw_deltas.append(rd)
        all_s3_gates.append(pg); all_pass_alarm.append(pa)

        # ── Update algedonic buffers ───────────────────────────
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)]
        self._prev_bank_3_desc = [
            mx.stop_gradient(α * self._prev_bank_3_desc[i] + (1 - α) * bank_3_desc[i])
            for i in range(self.cfg.n_registers)]

        # Combinator algedonic: 4 KIBC weights + 1 compute gate
        if hasattr(self.combinator_dispatch, '_dispatch_weights'):
            dw_full = mx.stop_gradient(
                self.combinator_dispatch._dispatch_weights.mean(axis=(0, 1)))
            # Only take KIBC portion (first 4)
            dw_mean = dw_full[:N_COMBINATORS]
        else:
            dw_mean = mx.zeros((N_COMBINATORS,))
        if hasattr(self.combinator_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.combinator_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean,                                            # 4 dims
            cg_mean,                                            # 1 dim
            mx.zeros((self.d_reg_real - N_COMBINATORS - 1,)),   # padding
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # ── Update retrieval register EMA (v12) ───────────────
        α = self._algedonic_ema
        self._prev_retrieval_regs = [
            mx.stop_gradient(
                α * self._prev_retrieval_regs[i] + (1 - α) * ret_regs[i])
            for i in range(self.cfg.n_retrieval_registers)]

        # ── S5 reweighting ─────────────────────────────────────
        # 8 banks: bank_0, bank_1_asc, bank_2_asc, bank_3_asc,
        #          bank_4_apex, bank_3_desc, bank_2_desc, bank_1_desc
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3_asc,
                     bank_4_apex, bank_3_desc, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        # ── Algedonic alert (Beer's fire alarm) ───────────────
        alarm_metrics = self._collect_alarm_metrics(
            all_s3_gates, pass_deltas, raw_deltas,
            all_pass_alarm, all_banks)
        alarm_factors = self.algedonic(alarm_metrics)

        # Effective gate = S5Reweight × alarm factor
        effective_gates = meta_gates * alarm_factors

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = effective_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + effective_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4: [bank_0, bank_1_desc, bank_3_desc, bank_4_apex] = 4 banks
        meta_banks = [bank_0, bank_1_desc, bank_3_desc, bank_4_apex]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        logits = self.embed.output_proj(x)

        loss = None
        if targets is not None:
            ce_loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()
            loss = ce_loss

            # Cache raw CE for logging (before holo/reg terms are added)
            self._last_ce = mx.stop_gradient(ce_loss)

            # Abstraction slot regularization
            if self.cfg.n_abstraction_slots > 0:
                reg_loss = AbstractionRegularizer.combined_loss(
                    self.combinator_dispatch.slot_embeddings,
                    self.combinator_dispatch.combinator_embeddings,
                    diversity_lambda=self.cfg.abstraction_diversity_lambda,
                    copy_lambda=self.cfg.abstraction_copy_lambda,
                    diversity_threshold=self.cfg.abstraction_diversity_threshold,
                    copy_threshold=self.cfg.abstraction_copy_threshold,
                )
                loss = loss + reg_loss

            # ── Dispatch entropy regularization (v12) ─────────────
            # The v11 gap: no ascending→dispatch feedback loop.
            # When ascending arm runs out of capacity, it drops
            # B-relevant features first, and nothing penalizes the
            # resulting dispatch collapse. This entropy penalty
            # creates gradient flow from dispatch diversity back
            # through the entire system.
            #
            # Squared hinge: only penalizes collapse (below target),
            # not uniformity. Target = 85% of max entropy (ln(4)).
            if self.cfg.dispatch_entropy_lambda > 0:
                # Use live dispatch weights (differentiable)
                dispatch_live = None
                n_desc_live = 0
                for pa in all_pass_alarm:
                    dw_live = pa.get('dispatch_weights_live')
                    if dw_live is not None:
                        dw_mean = mx.mean(dw_live, axis=(0, 1))
                        dispatch_live = dw_mean if dispatch_live is None \
                            else (dispatch_live + dw_mean)
                        n_desc_live += 1
                if dispatch_live is not None and n_desc_live > 0:
                    p = dispatch_live / n_desc_live
                    entropy = -mx.sum(p * mx.log(p + 1e-8))
                    entropy_deficit = mx.maximum(
                        self.cfg.dispatch_entropy_target - entropy, 0.0)
                    entropy_loss = self.cfg.dispatch_entropy_lambda * (
                        entropy_deficit * entropy_deficit)
                    loss = loss + entropy_loss

            # ── KL divergence toward empirical ratio (dispatch leash) ──
            # KL(dispatch ∥ prior) = Σ dispatch_i · log(dispatch_i / prior_i)
            # Penalizes deviation from the measured universal ratio.
            # The prior IS the ratio: λ dispatch(logits, r). softmax(logits + log(r/Σr))
            if self.cfg.dispatch_kl_lambda > 0:
                dispatch_kl_live = None
                n_kl_live = 0
                for pa in all_pass_alarm:
                    dw_live = pa.get('dispatch_weights_live')
                    if dw_live is not None:
                        dw_mean = mx.mean(dw_live, axis=(0, 1))
                        dispatch_kl_live = dw_mean if dispatch_kl_live is None \
                            else (dispatch_kl_live + dw_mean)
                        n_kl_live += 1
                if dispatch_kl_live is not None and n_kl_live > 0:
                    q = dispatch_kl_live / n_kl_live  # mean dispatch probs
                    # KIBC-only: first 4 components
                    q_kibc = q[:self.cfg.n_combinators]
                    q_kibc = q_kibc / mx.sum(q_kibc)  # renormalize to sum=1
                    # Prior from config ratio
                    r = mx.array(self.cfg.dispatch_ratio)
                    p_prior = r / mx.sum(r)
                    # KL(q ∥ p) = Σ q_i · log(q_i / p_i)
                    kl = mx.sum(q_kibc * mx.log(q_kibc / (p_prior + 1e-8) + 1e-8))
                    kl_loss = self.cfg.dispatch_kl_lambda * kl
                    loss = loss + kl_loss

            # ── Holographic loss (progressive intermediate decoding) ──
            # Each pass boundary produces a decodeable representation.
            # Pass n sees gradient from losses n..6 (7-n sources).
            # This creates a natural gradient slope: ascending arm
            # gets 4-7× gradient, descending arm gets 1-3×.
            #
            # Cost reduction: subsample positions for intermediate logits.
            # The 512→151936 projection is the bottleneck. Sampling 1/8
            # of positions gives unbiased gradient at ~8× less cost per
            # intermediate decode. The slope property is preserved exactly.
            holo_lambda_eff = getattr(self, '_holo_lambda_effective', 0.0)
            if holo_lambda_eff > 0:
                holo_loss = mx.array(0.0)
                x_progressive = x_embed  # base hologram = raw embedding
                total_pos = B * L
                n_sample = max(256, total_pos // 8)
                if n_sample < total_pos:
                    holo_idx = mx.random.randint(0, total_pos, (n_sample,))
                    targets_flat = targets.reshape(-1)
                    targets_sample = targets_flat[holo_idx]
                else:
                    holo_idx = None

                for n in range(self.N_PASSES):
                    x_progressive = x_progressive + effective_gates[n] * pass_deltas[n]
                    if holo_idx is not None:
                        x_flat = x_progressive.reshape(total_pos, -1)
                        x_sample = x_flat[holo_idx]  # (n_sample, d)
                        logits_n = self.embed.output_proj(
                            self.output_norm(x_sample))
                        loss_n = nn.losses.cross_entropy(
                            logits_n, targets_sample).mean()
                    else:
                        logits_n = self.embed.output_proj(
                            self.output_norm(x_progressive))
                        loss_n = nn.losses.cross_entropy(
                            logits_n.reshape(-1, self.cfg.vocab_size),
                            targets.reshape(-1),
                        ).mean()
                    holo_loss = holo_loss + loss_n
                loss = loss + holo_lambda_eff * holo_loss

        return logits, loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Instrumentation ───────────────────────────────────────

    @staticmethod
    def _entropy_proxy(x: mx.array) -> float:
        var_per_feat = mx.var(x, axis=(0, 1))
        mean_var = mx.mean(var_per_feat)
        mx.eval(mean_var)
        return float(mx.log(mean_var + 1e-10).item())

    def forward_instrumented(
        self,
        tokens: mx.array,
    ) -> tuple[mx.array, dict]:
        """Forward pass with full instrumentation. Returns (hidden, metrics)."""
        import math
        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)

        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3_asc = self._fresh_bank()
        bank_4_apex = self._fresh_bank()
        bank_3_desc = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []
        all_s3_gates = []
        all_pass_alarm_inst = []  # for alarm metrics collection
        pass_h_in = []
        pass_h_out = []
        asc_gate_mx = []
        asc_gate_bank = None
        cycle_budget_bias_inst = None
        all_cycle_continue_gates = []
        all_effective_cycles = []
        proposal_delta_inst = None
        proposal_confidence_inst = None
        # Retrieval register state (v12)
        ret_regs_inst = self._init_retrieval_registers()
        # Retrieval instrumentation accumulators
        all_retrieval_gate_means = []   # per ascending pass
        all_retrieval_memory_norms = []  # per ascending pass

        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_b3d = [mx.stop_gradient(r) for r in self._prev_bank_3_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        pass_configs = [
            (0, False, lambda: [bank_0, prev_b1d, prev_kernel]),
            (1, False, lambda: [bank_0, bank_1_asc, prev_b2d, prev_kernel]),
            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc, prev_b3d, prev_kernel]),
            (3, False, lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, prev_kernel]),
            (4, True,  lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, bank_4_apex]),
            (5, True,  lambda: [bank_0, bank_1_asc, bank_3_desc, bank_4_apex]),
            (6, True,  lambda: [bank_0, bank_1_asc, bank_2_desc, bank_4_apex]),
        ]
        target_banks = [bank_1_asc, bank_2_asc, bank_3_asc, bank_4_apex,
                        bank_3_desc, bank_2_desc, bank_1_desc]

        for pi, (pass_idx, is_desc, get_readable) in enumerate(pass_configs):
            h_in = self._entropy_proxy(x)
            pass_h_in.append(h_in)

            x_before = x
            readable = get_readable()
            target = target_banks[pi]

            s4 = self.s4_desc if is_desc else self.s4
            strides = self.stride_stack if not is_desc else None  # desc uses desc_plates

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
            raw_phases = []

            if is_desc:
                x_anchor = x
                max_cycles = self.cfg.desc_max_cycles
                cumulative_gate = mx.array(1.0)
                cycle_continue_gates = []

                for cycle in range(max_cycles):
                    x_cycle_start = x
                    if cycle > 0:
                        x = x + self.cycle_inject_gate * x_anchor

                    # Phase 0: dispatch
                    dispatch_out = self.combinator_dispatch(
                        x, registers=readable,
                        proposal_delta=proposal_delta_inst)
                    delta = dispatch_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                        target, delta, 0)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 0, is_descending=True)

                    # Phase 1: converge (KIBC dedicated plates)
                    # Each combinator has its own StrideStack; dispatch weights blend.
                    # Use live (differentiable) dispatch weights.
                    dw_kibc_inst = self.combinator_dispatch._dispatch_weights_live[..., :self.cfg.n_combinators]
                    conv_out = self.desc_plates(
                        x, dispatch_weights=dw_kibc_inst,
                        reverse=self.cfg.desc_stride_reverse,
                        stride_range=self._stride_range_for_pass(pass_idx))
                    delta = conv_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                        target, delta, 1)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 1, is_descending=True)

                    # Phase 2: integrate (with slot embeddings if available)
                    dw = (self.combinator_dispatch._dispatch_weights
                          if hasattr(self.combinator_dispatch, '_dispatch_weights')
                          else None)
                    slot_emb_inst = None
                    if (self.cfg.n_abstraction_slots > 0
                            and hasattr(self.combinator_dispatch,
                                        '_normalize_slot_embeddings')):
                        slot_emb_inst = (self.combinator_dispatch
                                         ._normalize_slot_embeddings())
                        if proposal_delta_inst is not None:
                            slot_emb_inst = slot_emb_inst + proposal_delta_inst
                        slot_emb_inst = (
                            slot_emb_inst
                            * self.combinator_dispatch.slot_gates[:, None])
                    integrate_out = self.combinator_integrate(
                        x, dispatch_weights=dw,
                        slot_embeddings=slot_emb_inst,
                        retrieval_registers=ret_regs_inst)
                    delta = integrate_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                        target, delta, 2)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 2, is_descending=True)

                    cycle_contribution = x - x_cycle_start
                    x = x_cycle_start + cumulative_gate * cycle_contribution

                    if cycle < max_cycles - 1 and max_cycles > 1:
                        cont_gate = self.cycle_continue(
                            target, budget_bias=cycle_budget_bias_inst
                            if cycle_budget_bias_inst is not None else None)
                        mx.eval(cont_gate)
                        cycle_continue_gates.append(float(cont_gate.item()))
                        cumulative_gate = cumulative_gate * cont_gate
            else:
                # Ascending compression
                prep_out = self.prep(x)
                delta = prep_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target, delta, 0)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 0, is_descending=False)

                conv_out = strides(x, reverse=False,
                                   stride_range=self._stride_range_for_pass(pass_idx))
                delta = conv_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target, delta, 1)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 1, is_descending=False)

                # ── Write retrieval registers (v12) ────────────────
                ret_regs_inst = self.retrieval_registers.write(ret_regs_inst, x)
                # Capture retrieval instrumentation from HybridStrideStack
                if hasattr(strides, '_retrieval_gate_means') and strides._retrieval_gate_means:
                    all_retrieval_gate_means.append(
                        dict(strides._retrieval_gate_means))  # dict[stride → float]
                if hasattr(strides, '_retrieval_memory_norms'):
                    rmn = strides._retrieval_memory_norms
                    if isinstance(rmn, dict):
                        norms_dict = {}
                        for stride_key, norm_arr in rmn.items():
                            mx.eval(norm_arr)
                            norms_dict[stride_key] = [
                                float(v.item()) for v in norm_arr]
                        all_retrieval_memory_norms.append(norms_dict)
                    elif rmn is not None:
                        mx.eval(rmn)
                        all_retrieval_memory_norms.append(
                            [float(v.item()) for v in rmn]
                            if rmn.ndim > 0 else [float(rmn.item())])

                cons_out = self.consolidate(x)
                delta = cons_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target, delta, 2)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 2, is_descending=False)

            target_banks[pi] = target
            pass_deltas.append(x - x_before)
            raw_delta = raw_phases[0]
            for rd in raw_phases[1:]:
                raw_delta = raw_delta + rd
            raw_deltas.append(raw_delta)
            all_s3_gates.append(phase_gates)

            # Collect alarm metrics for this pass (live values from modules)
            pa_inst = {
                'cycle_continue_gates': [],
                'dispatch_weights_live': None,
                'compute_gate_live': None,
            }
            if is_desc:
                if hasattr(self.combinator_dispatch, '_dispatch_weights_live'):
                    pa_inst['dispatch_weights_live'] = \
                        self.combinator_dispatch._dispatch_weights_live
                if hasattr(self.combinator_integrate, '_compute_gate_live'):
                    pa_inst['compute_gate_live'] = \
                        self.combinator_integrate._compute_gate_live
                # CycleContinue gates: re-read from module state
                # (the live gates were consumed in cumulative_gate above)
                # We need the live values — recompute from target register state
                # Actually, the cont_gate local variable IS live when computed.
                # But we already eval'd it. For instrumented mode, the stop_grad
                # versions are fine since we don't backprop. Use mx.array wrapping.
                if self.cfg.desc_max_cycles > 1 and cycle_continue_gates:
                    pa_inst['cycle_continue_gates'] = [
                        mx.array(g) for g in cycle_continue_gates]
            all_pass_alarm_inst.append(pa_inst)

            if is_desc and self.cfg.desc_max_cycles > 1:
                all_cycle_continue_gates.append(cycle_continue_gates)
                eff = 1.0 + sum(
                    float(mx.prod(mx.array(cycle_continue_gates[:i+1])).item())
                    for i in range(len(cycle_continue_gates))
                ) if cycle_continue_gates else 1.0
                all_effective_cycles.append(eff)

            # After pass 3 (L3_apex, pi==3): pack asc gates + compute emphasis
            if not is_desc and pi == 3 and asc_gate_mx:
                asc_gate_flat = mx.concatenate(
                    [g.reshape(-1) for g in asc_gate_mx])
                asc_gate_vector = mx.concatenate([
                    asc_gate_flat,
                    mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
                ])
                asc_gate_bank = [asc_gate_vector]

            if not is_desc and pi == 3:
                # S4→S3 cycle budget bias (instrumented path)
                # Uses banks 1_asc, 2_asc, 3_asc
                cycle_budget_parts_inst = []
                for bank in [target_banks[0], target_banks[1], target_banks[2]]:
                    for reg in bank:
                        cycle_budget_parts_inst.append(reg)
                cycle_budget_input_inst = mx.concatenate(
                    cycle_budget_parts_inst, axis=-1)
                raw_budget_inst = (
                    self.cycle_budget_proj(
                        cycle_budget_input_inst.reshape(1, -1)
                    ).reshape(-1)[..., :1]
                    + self.cycle_budget_bias
                ).reshape(())
                cycle_budget_bias_inst = 4.0 * mx.tanh(raw_budget_inst)
                mx.eval(cycle_budget_bias_inst)
                self._cycle_budget_bias = mx.stop_gradient(
                    0.95 * self._cycle_budget_bias
                    + 0.05 * cycle_budget_bias_inst)

                # S4→S5 abstraction proposal
                if self.cfg.n_abstraction_slots > 0:
                    proposal_delta_inst, proposal_confidence_inst, _ = \
                        self.proposal_head(cycle_budget_input_inst)
                    mx.eval(proposal_delta_inst, proposal_confidence_inst)
                    proposal_gate_inst = mx.sigmoid(
                        mx.array(1.0) * proposal_confidence_inst
                        - self.proposal_threshold)
                    proposal_delta_inst = proposal_delta_inst * proposal_gate_inst
                    mx.eval(proposal_delta_inst)

            h_out = self._entropy_proxy(x)
            pass_h_out.append(h_out)

            if pi < len(pass_configs) - 1:
                signal = self.s2.direction_signal(pass_deltas[-1], pi)
                if pi > 0:
                    coherence = S2Coordinator.coherence_factor(
                        pass_deltas[-2], pass_deltas[-1])
                    signal = signal * coherence
                x = x + signal

        # S2 conflict scores
        s2_conflict = []
        for i in range(len(pass_deltas) - 1):
            cs = S2Coordinator.conflict_score(pass_deltas[i], pass_deltas[i + 1])
            s2_conflict.append(cs)
        s2_scales = [float(self.s2.scales[i].item())
                     for i in range(S2Coordinator.N_TRANSITIONS)]

        bank_1_asc = target_banks[0]
        bank_2_asc = target_banks[1]
        bank_3_asc = target_banks[2]
        bank_4_apex = target_banks[3]
        bank_3_desc = target_banks[4]
        bank_2_desc = target_banks[5]
        bank_1_desc = target_banks[6]

        # Update algedonic buffers
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)]
        self._prev_bank_3_desc = [
            mx.stop_gradient(α * self._prev_bank_3_desc[i] + (1 - α) * bank_3_desc[i])
            for i in range(self.cfg.n_registers)]

        if hasattr(self.combinator_dispatch, '_dispatch_weights'):
            dw_full_inst = mx.stop_gradient(
                self.combinator_dispatch._dispatch_weights.mean(axis=(0, 1)))
            dw_mean = dw_full_inst[:N_COMBINATORS]
        else:
            dw_mean = mx.zeros((N_COMBINATORS,))
        if hasattr(self.combinator_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.combinator_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean, cg_mean,
            mx.zeros((self.d_reg_real - N_COMBINATORS - 1,)),
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # ── Update retrieval register EMA (v12) ───────────────
        self._prev_retrieval_regs = [
            mx.stop_gradient(
                α * self._prev_retrieval_regs[i] + (1 - α) * ret_regs_inst[i])
            for i in range(self.cfg.n_retrieval_registers)]

        # S5 reweighting — 8 banks
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3_asc,
                     bank_4_apex, bank_3_desc, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)
        mx.eval(meta_gates)

        # ── Algedonic alert (Beer's fire alarm) ───────────────
        # Collect alarm metrics using live S3 gate values.
        # In instrumented mode, S3 gates are floats — wrap as mx.array.
        all_s3_gates_mx = []
        for pass_gates in all_s3_gates:
            all_s3_gates_mx.append([mx.array(g) for g in pass_gates])
        alarm_metrics_inst = self._collect_alarm_metrics(
            all_s3_gates_mx, pass_deltas, raw_deltas,
            all_pass_alarm_inst, all_banks)
        mx.eval(alarm_metrics_inst)
        alarm_factors_inst = self.algedonic(alarm_metrics_inst)
        mx.eval(alarm_factors_inst)
        effective_gates = meta_gates * alarm_factors_inst

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = effective_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + effective_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4: [bank_0, bank_1_desc, bank_3_desc, bank_4_apex] = 4 banks
        meta_banks_list = [bank_0, bank_1_desc, bank_3_desc, bank_4_apex]
        x = self.meta_s4(meta_banks_list, x)
        x = self.output_norm(x)

        # Register norms
        reg_norms = {}
        named_banks = {
            "bank_0": bank_0, "bank_1_asc": bank_1_asc,
            "bank_2_asc": bank_2_asc, "bank_3_asc": bank_3_asc,
            "bank_4_apex": bank_4_apex, "bank_3_desc": bank_3_desc,
            "bank_2_desc": bank_2_desc, "bank_1_desc": bank_1_desc,
        }
        for name, bank in named_banks.items():
            norms = []
            for reg in bank:
                mx.eval(reg)
                norms.append(float(mx.sqrt((reg * reg).sum()).item()))
            reg_norms[name] = norms

        # Retrieval register norms (v12)
        retrieval_register_norms = []
        retrieval_write_gates = []
        for i, rr in enumerate(ret_regs_inst):
            mx.eval(rr)
            retrieval_register_norms.append(
                float(mx.sqrt(mx.sum(rr * rr) + 1e-8).item()))
        # Write gate values from the RetrievalRegisters module
        if hasattr(self.retrieval_registers, '_write_gate_values'):
            wg = self.retrieval_registers._write_gate_values
            if wg is not None:
                mx.eval(wg)
                retrieval_write_gates = [float(wg[i].item())
                                         for i in range(wg.shape[0])]

        # Compression metrics
        pass_compression = []
        pass_phi_dev = []
        for h_in, h_out in zip(pass_h_in, pass_h_out):
            ratio = h_out / h_in if abs(h_in) > 1e-8 else 1.0
            pass_compression.append(ratio)
            pass_phi_dev.append(abs(ratio - INV_PHI))

        # Combinator dispatch metrics
        dispatch_weights = None
        dispatch_weights_kibc = None
        type_weights = None
        if hasattr(self.combinator_dispatch, '_dispatch_weights'):
            dw = self.combinator_dispatch._dispatch_weights
            mx.eval(dw)
            dispatch_weights = mx.mean(dw, axis=(0, 1))
            mx.eval(dispatch_weights)
            # KIBC-only for backward compat
            dispatch_weights_kibc = dispatch_weights[:N_COMBINATORS]
        if hasattr(self.combinator_integrate, '_type_weights'):
            tw = self.combinator_integrate._type_weights
            mx.eval(tw)
            type_weights = mx.mean(tw, axis=(0, 1))
            mx.eval(type_weights)

        # Combinator embedding norms
        comb_emb_norms = None
        if hasattr(self.combinator_dispatch, 'combinator_embeddings'):
            raw_emb = self.combinator_dispatch.combinator_embeddings
            mx.eval(raw_emb)
            norms = mx.sqrt(mx.sum(raw_emb * raw_emb, axis=-1) + 1e-8)
            mx.eval(norms)
            comb_emb_norms = [float(norms[i].item()) for i in range(norms.shape[0])]

        # Abstraction slot metrics
        slot_metrics = None
        if self.cfg.n_abstraction_slots > 0:
            sg = self.combinator_dispatch.slot_gates
            mx.eval(sg)
            slot_gates_list = [float(sg[i].item())
                               for i in range(self.cfg.n_abstraction_slots)]

            # Slot usage: what fraction of dispatch mass goes to slots
            slot_usage = None
            if dispatch_weights is not None:
                slot_dw = dispatch_weights[N_COMBINATORS:]
                mx.eval(slot_dw)
                slot_usage = [float(slot_dw[i].item())
                              for i in range(self.cfg.n_abstraction_slots)]

            # Slot-KIBC cosine similarity
            slot_emb = self.combinator_dispatch.slot_embeddings
            comb_emb = self.combinator_dispatch.combinator_embeddings
            mx.eval(slot_emb, comb_emb)
            s_norms = mx.sqrt(mx.sum(slot_emb * slot_emb, axis=-1,
                                      keepdims=True) + 1e-8)
            c_norms = mx.sqrt(mx.sum(comb_emb * comb_emb, axis=-1,
                                      keepdims=True) + 1e-8)
            slot_kibc_cos = ((slot_emb / s_norms) @ (comb_emb / c_norms).T)
            mx.eval(slot_kibc_cos)
            max_slot_kibc_cos = [float(mx.max(slot_kibc_cos[i]).item())
                                 for i in range(self.cfg.n_abstraction_slots)]

            # Slot pairwise cosine (max off-diagonal per slot)
            s_normed = slot_emb / s_norms
            slot_pair_cos = s_normed @ s_normed.T
            mx.eval(slot_pair_cos)

            # Proposal confidence
            prop_conf = None
            if proposal_confidence_inst is not None:
                prop_conf = float(proposal_confidence_inst.item())

            slot_metrics = {
                "slot_gates": slot_gates_list,
                "slot_usage": slot_usage,
                "max_slot_kibc_cosine": max_slot_kibc_cos,
                "proposal_confidence": prop_conf,
                "n_active_slots": sum(1 for g in slot_gates_list if g > 0.1),
            }

        cig = self.cycle_inject_gate
        mx.eval(cig)

        metrics = {
            "s3_gates": all_s3_gates,
            "s5_reweight": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],
            "alarm_factors": [float(alarm_factors_inst[i].item())
                              for i in range(self.N_PASSES)],
            "alarm_metrics": [float(alarm_metrics_inst[i].item())
                              for i in range(alarm_metrics_inst.shape[0])],
            "effective_s5_gates": [float(effective_gates[i].item())
                                   for i in range(self.N_PASSES)],
            "s2_conflict": s2_conflict,
            "s2_scales": s2_scales,
            "register_norms": reg_norms,
            "pass_entropy_in": pass_h_in,
            "pass_entropy_out": pass_h_out,
            "pass_compression": pass_compression,
            "pass_phi_dev": pass_phi_dev,
            "combinator_dispatch_weights": (
                [float(dispatch_weights_kibc[i].item())
                 for i in range(dispatch_weights_kibc.shape[0])]
                if dispatch_weights_kibc is not None else None
            ),
            "combinator_type_weights": (
                [float(type_weights[i].item())
                 for i in range(type_weights.shape[0])]
                if type_weights is not None else None
            ),
            "combinator_embedding_norms": comb_emb_norms,
            "desc_max_cycles": self.cfg.desc_max_cycles,
            "cycle_inject_gate": float(cig.item()),
            "cycle_budget_bias": float(cycle_budget_bias_inst.item())
                if cycle_budget_bias_inst is not None else 0.0,
            "cycle_continue_gates": all_cycle_continue_gates,
            "effective_cycles": all_effective_cycles,
            # ── Retrieval metrics (v12) ────────────────────────
            "retrieval_gate_means": all_retrieval_gate_means,
            "retrieval_memory_norms": all_retrieval_memory_norms,
            "retrieval_register_norms": retrieval_register_norms,
            "retrieval_write_gates": retrieval_write_gates,
        }

        if hasattr(self.combinator_integrate, '_compute_gate'):
            cg = self.combinator_integrate._compute_gate
            mx.eval(cg)
            metrics["compute_gate_mean"] = float(mx.mean(cg).item())
            metrics["compute_gate_max"] = float(mx.max(cg).item())
            metrics["compute_gate_min"] = float(mx.min(cg).item())
            metrics["compute_gate_active"] = float(
                mx.mean((cg > 0.5).astype(mx.float32)).item())

        # Abstraction slot metrics
        if slot_metrics is not None:
            metrics["abstraction_slots"] = slot_metrics

        # ── Holographic intermediate losses ───────────────────
        # Compute per-pass intermediate CE loss for diagnostics.
        # These show how decodeable each progressive representation is.
        holo_losses = []
        x_progressive = mx.stop_gradient(x_embed)  # no grad in instrumented
        for n in range(self.N_PASSES):
            x_progressive = x_progressive + mx.stop_gradient(
                effective_gates[n] * pass_deltas[n])
            logits_n = self.embed.output_proj(self.output_norm(x_progressive))
            # Use first token shifted as pseudo-targets
            # (instrumented mode doesn't have real targets, compute on
            # the input tokens themselves for relative comparison)
            pseudo_targets = mx.concatenate(
                [tokens[:, 1:], mx.zeros((tokens.shape[0], 1), dtype=mx.int32)],
                axis=1)
            loss_n = nn.losses.cross_entropy(
                logits_n.reshape(-1, self.cfg.vocab_size),
                pseudo_targets.reshape(-1),
            ).mean()
            mx.eval(loss_n)
            holo_losses.append(float(loss_n.item()))
        metrics["holo_losses"] = holo_losses

        return x, metrics


# ══════════════════════════════════════════════════════════════════
# Factory + utilities
# ══════════════════════════════════════════════════════════════════


def create_model(cfg: V12Config) -> V12Model:
    model = V12Model(cfg)
    mx.eval(model.parameters())
    return model


def count_parameters(model: nn.Module) -> dict[str, int]:
    from mlx.utils import tree_flatten
    counts = {"total": 0, "trainable": 0}
    all_params = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())
    counts["total"] = sum(p.size for _, p in all_params)
    counts["trainable"] = sum(p.size for _, p in trainable)
    return counts
