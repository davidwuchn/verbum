"""
v13 Model — Beam/Plate Separated Architecture.

Evolution from v12: clean separation of ternary plates (topology, etch-shaped)
from continuous beams (routing, GD-trained). Key changes:

  - 11 power-of-2 strides (1..1024, uniform 2× gaps)
  - Separated dispatch: plate path + beam path add in logit space
  - Mechanical WHNF FFN (zero continuous params)
  - PCA-Q crystal lattice loss (3-zone, constant targets)
  - No math kernels, no abstraction slots, no CategoryDispatch
  - One training script: etch phase + GD phase

Symmetric hourglass (7 passes):
  L0↑ → L1↑ → L2↑ → L3_apex → L2↓ → L1↓ → L0↓
  Pass  0       1       2         3       4      5      6

License: MIT
"""

from __future__ import annotations

import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V13Config
from ternary import TernaryLinear, TernaryEmbedding, TernaryMirror
from attention import HybridStrideStack
from components import (
    S4Ternary,
    S3Ternary,
    MetaS4Ternary,
    S5Reweight,
    S2Coordinator,
    AlgedonicAlert,
    RetrievalRegisters,
)
from kernel_dispatch import CombinatorDispatch, CombinatorIntegrate, N_COMBINATORS


# ══════════════════════════════════════════════════════════════════
# Crystal diagnostics — measure lattice formation from PCA-Q targets
# ══════════════════════════════════════════════════════════════════


def compute_crystal_diagnostics(model: "V13Model") -> dict:
    """Measure crystal lattice formation from combinator embeddings.

    Compares the current combinator embedding cosine matrix against
    the PCA-Q zone targets. Returns agreement scores per zone.
    """
    from kernel import COMBINATOR_NAMES as names
    metrics = {}

    emb = model.combinator_dispatch.combinator_embeddings  # (8, d_model)
    norms = mx.sqrt(mx.sum(emb * emb, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb / norms
    cos_matrix = emb_norm @ emb_norm.T  # (8, 8)
    mx.eval(cos_matrix)

    # Extract upper triangle (28 pairs)
    cos_dict = {}
    for i in range(N_COMBINATORS):
        for j in range(i + 1, N_COMBINATORS):
            pair = f"{names[i]}_{names[j]}"
            cos_dict[pair] = float(cos_matrix[i, j].item())
    metrics["combinator_cosines"] = cos_dict

    # Crystal formation: WHNF anti-correlation
    whnf_pairs = [k for k in cos_dict if "WHNF" in k]
    if whnf_pairs:
        whnf_mean = sum(cos_dict[p] for p in whnf_pairs) / len(whnf_pairs)
        metrics["whnf_anti_correlation"] = whnf_mean  # should be negative

    # Composition cluster tightness (B, C, D)
    comp_pairs = ["B_C", "B_D", "C_D"]
    comp_vals = [cos_dict.get(p, 0) for p in comp_pairs]
    if comp_vals:
        metrics["composition_cluster_mean"] = sum(comp_vals) / len(comp_vals)

    return metrics


# ══════════════════════════════════════════════════════════════════
# Crystal lattice loss — PCA-Q zone targets (constant, every step)
# ══════════════════════════════════════════════════════════════════


def crystal_lattice_loss(
    combinator_embeddings: mx.array,
    zone_targets: mx.array,
) -> mx.array:
    """Compute crystal lattice MSE for one zone.

    combinator_embeddings: (8, d_model) — current model embeddings
    zone_targets: (8, 8) — measured cosine target matrix for this zone

    Returns: scalar MSE over upper triangle (28 pairs), equal weight.
    """
    norms = mx.sqrt(mx.sum(combinator_embeddings * combinator_embeddings,
                            axis=-1, keepdims=True) + 1e-8)
    emb_norm = combinator_embeddings / norms
    cos_matrix = emb_norm @ emb_norm.T  # (8, 8)

    # Upper triangle mask
    n = cos_matrix.shape[0]
    # Build triu indices
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    rows_arr = mx.array(rows)
    cols_arr = mx.array(cols)

    student = cos_matrix[rows_arr, cols_arr]  # (28,)
    target = zone_targets[rows_arr, cols_arr]  # (28,)
    diff = student - target
    return mx.mean(diff * diff)


# ══════════════════════════════════════════════════════════════════
# V13Model — Beam/Plate Separated Hourglass
# ══════════════════════════════════════════════════════════════════


class V13Model(nn.Module):
    """Beam/plate separated VSM: 8-combinator dispatch + stride stack.

    7 passes: L0↑ → L1↑ → L2↑ → L3_apex → L2↓ → L1↓ → L0↓

    Register semantics:
      reg 0: combinator — K/I/B/C identity at this position
      reg 1: binding_depth — how many lambdas deep (0=free, 1=bound, ...)
      reg 2: phase — recognize / identify / resolve / produce

    Retrieval register semantics:
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

    def __init__(self, cfg: V13Config):
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

        # Cross-pass register norm
        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # ── S1: Unified stride stack (ALL 7 passes share this) ────
        self.stride_stack = HybridStrideStack.from_config(cfg)

        # ── Retrieval registers ───────────────────────────────
        self.retrieval_registers = RetrievalRegisters(
            d, cfg.d_register, cfg.n_retrieval_registers)

        # ── S1: Dispatch→Stride→Integrate ─────────────────────
        # V13: separated beam/plate paths
        self.combinator_dispatch = CombinatorDispatch(cfg)
        self.combinator_integrate = CombinatorIntegrate(cfg)

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

        # ── Meta-S4 ──────────────────────────────────────────
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── S2: Direction coordination ─────────────────────────
        self.s2 = S2Coordinator(d)

        # ── S5: Pass reweighting ──────────────────────────────
        self.s5_reweight = S5Reweight(
            d, d_reg, n_registers=n_reg,
            n_banks=8, n_passes=self.N_PASSES)

        # ── Algedonic alert ───────────────────────────────────
        self.algedonic = AlgedonicAlert(n_passes=self.N_PASSES,
                                         n_combinators=N_COMBINATORS)

        # ── Algedonic channel buffers ─────────────────────────
        self._algedonic_ema = 0.9
        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_3_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))
        self._prev_retrieval_regs = [
            mx.zeros((self.d_reg_real,)) for _ in range(cfg.n_retrieval_registers)]

        # ── PCA-Q zone targets (frozen constants) ─────────────
        self._zone_targets = [
            mx.array(cfg.pcaq_zone_a_targets),
            mx.array(cfg.pcaq_zone_b_targets),
            mx.array(cfg.pcaq_zone_c_targets),
        ]

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Helpers ───────────────────────────────────────────────

    @property
    def max_seq_len(self) -> int:
        return self.cfg.max_seq_len

    def _init_bank0(self) -> list[mx.array]:
        return [self.register_inits[f"reg_{name}"]
                for name in self.REGISTER_NAMES]

    def _fresh_bank(self) -> list[mx.array]:
        return [mx.zeros((self.d_reg_real,))
                for _ in self.REGISTER_NAMES]

    def _init_retrieval_registers(self) -> list[mx.array]:
        return self.retrieval_registers.init_registers()

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        return x + gate * mx.tanh(projs[phase_idx](delta))

    @staticmethod
    def _delta_rms(delta: mx.array) -> mx.array:
        return mx.sqrt(mx.mean(delta * delta) + 1e-8)

    def _stride_range_for_pass(self, pass_idx: int) -> tuple[int, int] | None:
        if not self.cfg.fractal_stride_bands:
            return None
        if pass_idx < len(self.cfg.stride_band_ranges):
            return self.cfg.stride_band_ranges[pass_idx]
        return None

    # ── Crystal lattice loss (3-zone PCA-Q targets) ───────────

    def compute_crystal_loss(self) -> mx.array:
        """Compute crystal lattice loss across all 3 zones.

        Uses the combinator embeddings from dispatch and compares against
        PCA-Q zone targets. Loss = weighted sum of per-zone MSE.

        Returns: scalar loss.
        """
        emb = self.combinator_dispatch.combinator_embeddings  # (8, d_model)
        total_loss = mx.array(0.0)
        for zone_idx, (target, lam) in enumerate(
                zip(self._zone_targets, self.cfg.zone_lambdas)):
            zone_loss = crystal_lattice_loss(emb, target)
            total_loss = total_loss + lam * zone_loss
        return total_loss

    # ── Alarm metrics collection ─────────────────────────────

    def _collect_alarm_metrics(
        self,
        all_s3_gates: list[list],
        pass_deltas: list[mx.array],
        raw_deltas: list[mx.array],
        all_pass_alarm: list[dict],
        all_banks: list[list[mx.array]],
    ) -> mx.array:
        """Pack operational health metrics into a single vector for AlgedonicAlert."""
        metrics = []

        # 1. S3 gate means per pass (7)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_sum = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_sum = gate_sum + g
                metrics.append(gate_sum / len(pass_gates))
            else:
                metrics.append(mx.array(0.5))

        # 2. S3 gate mins per pass (7)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_min = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_min = mx.minimum(gate_min, g)
                metrics.append(gate_min)
            else:
                metrics.append(mx.array(0.5))

        # 3. S2 conflict cosines (6)
        for i in range(self.N_PASSES - 1):
            s_prev = pass_deltas[i].mean(axis=(0, 1))
            s_curr = pass_deltas[i + 1].mean(axis=(0, 1))
            dot = (s_prev * s_curr).sum()
            n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
            n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)
            metrics.append(dot / (n_prev * n_curr))

        # 4. Dispatch weight means (8)
        dispatch_accum = None
        n_pass = 0
        for pa in all_pass_alarm:
            dw = pa.get('dispatch_weights_live')
            if dw is not None:
                dw_mean = mx.mean(dw, axis=(0, 1))
                if dispatch_accum is None:
                    dispatch_accum = dw_mean
                else:
                    dispatch_accum = dispatch_accum + dw_mean
                n_pass += 1
        if dispatch_accum is not None and n_pass > 0:
            dispatch_mean = dispatch_accum / n_pass
            for i in range(N_COMBINATORS):
                metrics.append(dispatch_mean[i])
        else:
            for _ in range(N_COMBINATORS):
                metrics.append(mx.array(1.0 / N_COMBINATORS))

        # 5. Dispatch entropy (1)
        if dispatch_accum is not None and n_pass > 0:
            p = dispatch_mean
            entropy = -mx.sum(p * mx.log(p + 1e-8))
            metrics.append(entropy)
        else:
            metrics.append(mx.array(math.log(N_COMBINATORS)))

        # 6. Compute gate mean + active fraction (2)
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
            metrics.append(cg_mean)
        else:
            metrics.append(mx.array(0.0))
            metrics.append(mx.array(0.0))

        # 7. Raw delta RMS norms (7)
        for rd in raw_deltas:
            metrics.append(self._delta_rms(rd))

        # 8. Gated delta RMS norms (7)
        for pd in pass_deltas:
            metrics.append(self._delta_rms(pd))

        # 9. S3 suppression ratio per pass (7)
        for pd, rd in zip(pass_deltas, raw_deltas):
            gated_rms = self._delta_rms(pd)
            raw_rms = self._delta_rms(rd)
            metrics.append(gated_rms / (raw_rms + 1e-8))

        # 10. Register bank mean norms (8)
        for bank in all_banks:
            bank_norm_sum = mx.array(0.0)
            for reg in bank:
                bank_norm_sum = bank_norm_sum + mx.sqrt(
                    mx.sum(reg * reg) + 1e-8)
            metrics.append(bank_norm_sum / len(bank))

        metrics_flat = [m.reshape(1) if m.ndim == 0 else m.reshape(1)
                        for m in metrics]
        return mx.concatenate(metrics_flat)

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks,
                         target_bank, embed_context=None, ret_regs=None):
        x_before = x
        raw_phases = []
        phase_gates = []
        pass_alarm = {
            'dispatch_weights_live': None,
            'compute_gate_live': None,
        }

        s4 = self.s4_desc if is_descending else self.s4

        # S4 scan
        s4_residual = x
        if embed_context is not None:
            s4_residual = mx.concatenate([x, embed_context], axis=1)
        s4_updates, _ = s4(readable_banks, s4_residual)
        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])
                       for i in range(self.cfg.n_registers)]

        # ── Phase 0: Dispatch ──────────────────────────────────
        dispatch_weights, comb_context = self.combinator_dispatch(x, pass_idx=pass_idx)
        # Cache live dispatch for alarm
        pass_alarm['dispatch_weights_live'] = dispatch_weights

        delta = comb_context - x  # dispatch effect on residual
        raw_phases.append(delta)
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 0)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=0, is_descending=is_descending)

        # ── Phase 1: Stride (propagate with beam angles) ──────
        reverse = is_descending and self.cfg.desc_stride_reverse
        stride_out = self.stride_stack(
            x, pass_idx=pass_idx, reverse=reverse)
        delta = stride_out - x
        raw_phases.append(delta)
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 1)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=1, is_descending=is_descending)

        # ── Phase 2: Integrate (apply combinator kernels) ─────
        integrate_out = self.combinator_integrate(
            x, dispatch_weights=dispatch_weights, comb_context=comb_context,
            pass_idx=pass_idx)
        delta = integrate_out - x
        raw_phases.append(delta)
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 2)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=2, is_descending=is_descending)

        # Cache compute gate for alarm
        if hasattr(self.combinator_integrate, '_compute_gate_live'):
            pass_alarm['compute_gate_live'] = \
                self.combinator_integrate._compute_gate_live

        # Write retrieval registers (ascending only)
        if not is_descending and ret_regs is not None:
            ret_regs = self.retrieval_registers.write(ret_regs, x)

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
        all_s3_gates = []
        all_pass_alarm = []

        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_b3d = [mx.stop_gradient(r) for r in self._prev_bank_3_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        asc_s3_gates = []
        ret_regs = self._init_retrieval_registers()

        # ── Pass 0: L0↑ ──────────────────────────────────────
        x, bank_1_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        x = x + self.s2.direction_signal(pd, 0)

        # ── Pass 1: L1↑ ──────────────────────────────────────
        x, bank_2_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])
        x = x + self.s2.direction_signal(pd, 1) * coherence

        # ── Pass 2: L2↑ ──────────────────────────────────────
        x, bank_3_asc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 2, False,
            [bank_0, bank_1_asc, bank_2_asc, prev_b3d, prev_kernel], bank_3_asc,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])
        x = x + self.s2.direction_signal(pd, 2) * coherence

        # ── Pass 3: L3_apex ──────────────────────────────────
        x, bank_4_apex, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 3, False,
            [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, prev_kernel], bank_4_apex,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        asc_s3_gates.extend(pg); all_s3_gates.append(pg); all_pass_alarm.append(pa)

        # Pack ascending S3 gates for descending arm
        asc_gate_flat = mx.concatenate([g.reshape(-1) for g in asc_s3_gates])
        pad_size = self.d_reg_real - asc_gate_flat.shape[0]
        if pad_size > 0:
            asc_gate_vector = mx.concatenate([
                asc_gate_flat, mx.zeros((pad_size,))])
        else:
            asc_gate_vector = asc_gate_flat[:self.d_reg_real]
        asc_gate_bank = [asc_gate_vector]

        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])
        x = x + self.s2.direction_signal(pd, 3) * coherence

        # ── Pass 4: L2↓ ──────────────────────────────────────
        x, bank_3_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 4, True,
            [bank_0, bank_1_asc, bank_2_asc, bank_3_asc, bank_4_apex, asc_gate_bank],
            bank_3_desc, embed_context=x_embed,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[3], pass_deltas[4])
        x = x + self.s2.direction_signal(pd, 4) * coherence

        # ── Pass 5: L1↓ ──────────────────────────────────────
        x, bank_2_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 5, True,
            [bank_0, bank_1_asc, bank_3_desc, bank_4_apex, asc_gate_bank],
            bank_2_desc, embed_context=x_embed,
            ret_regs=ret_regs)
        pass_deltas.append(pd); raw_deltas.append(rd)
        all_s3_gates.append(pg); all_pass_alarm.append(pa)
        coherence = S2Coordinator.coherence_factor(pass_deltas[4], pass_deltas[5])
        x = x + self.s2.direction_signal(pd, 5) * coherence

        # ── Pass 6: L0↓ ──────────────────────────────────────
        x, bank_1_desc, pd, rd, pg, pa, ret_regs = self._run_level_pass(
            x, 6, True,
            [bank_0, bank_1_asc, bank_2_desc, bank_4_apex, asc_gate_bank],
            bank_1_desc, embed_context=x_embed,
            ret_regs=ret_regs)
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

        if hasattr(self.combinator_dispatch, '_dispatch_weights_live'):
            dw_mean = mx.stop_gradient(
                self.combinator_dispatch._dispatch_weights_live.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_COMBINATORS,))
        if hasattr(self.combinator_integrate, '_compute_gate_live'):
            cg_mean = mx.stop_gradient(
                self.combinator_integrate._compute_gate_live.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean, cg_mean,
            mx.zeros((self.d_reg_real - N_COMBINATORS - 1,)),
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        self._prev_retrieval_regs = [
            mx.stop_gradient(
                α * self._prev_retrieval_regs[i] + (1 - α) * ret_regs[i])
            for i in range(self.cfg.n_retrieval_registers)]

        # ── S5 reweighting ─────────────────────────────────────
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3_asc,
                     bank_4_apex, bank_3_desc, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        # ── Algedonic alert ───────────────────────────────────
        alarm_metrics = self._collect_alarm_metrics(
            all_s3_gates, pass_deltas, raw_deltas,
            all_pass_alarm, all_banks)
        alarm_factors = self.algedonic(alarm_metrics)

        # Effective gate = S5 × alarm
        effective_gates = meta_gates * alarm_factors

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = effective_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + effective_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4
        meta_banks = [bank_0, bank_1_desc, bank_3_desc, bank_4_apex]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        self._last_hidden = x
        logits = self.embed.output_proj(x)

        loss = None
        if targets is not None:
            loss = self._compute_loss(logits, targets, all_pass_alarm,
                                       effective_gates, pass_deltas, x_embed)
        return logits, loss

    def _compute_loss(self, logits, targets, all_pass_alarm,
                       effective_gates, pass_deltas, x_embed):
        """Compute total loss: CE + crystal + dispatch KL + entropy."""
        B, L = targets.shape

        # Cross-entropy
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, self.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        loss = ce_loss
        self._last_ce = mx.stop_gradient(ce_loss)

        # Crystal lattice loss (PCA-Q 3-zone targets)
        if self.cfg.use_relational_loss:
            crystal_loss = self.compute_crystal_loss()
            loss = loss + self.cfg.rel_lambda * crystal_loss
            self._last_crystal_loss = mx.stop_gradient(crystal_loss)

        # Dispatch entropy regularization
        if self.cfg.dispatch_entropy_lambda > 0:
            dispatch_live = self._aggregate_dispatch(all_pass_alarm)
            if dispatch_live is not None:
                p = dispatch_live / (mx.sum(dispatch_live) + 1e-8)
                entropy = -mx.sum(p * mx.log(p + 1e-8))
                deficit = mx.maximum(
                    self.cfg.dispatch_entropy_target - entropy, 0.0)
                entropy_loss = self.cfg.dispatch_entropy_lambda * deficit * deficit
                loss = loss + entropy_loss

        # KL divergence toward empirical ratio
        if self.cfg.dispatch_kl_lambda > 0:
            dispatch_live = self._aggregate_dispatch(all_pass_alarm)
            if dispatch_live is not None:
                q = dispatch_live / (mx.sum(dispatch_live) + 1e-8)
                # EMA tracking (monitoring only)
                decay = self.cfg.dispatch_kl_ema_decay
                q_det = mx.stop_gradient(q)
                if not hasattr(self, '_dispatch_ema'):
                    self._dispatch_ema = q_det
                else:
                    self._dispatch_ema = decay * self._dispatch_ema + (1 - decay) * q_det

                r = mx.array(self.cfg.dispatch_ratio)
                p_prior = r / mx.sum(r)
                kl = mx.sum(q * mx.log(q / (p_prior + 1e-8) + 1e-8))
                kl_loss = self.cfg.dispatch_kl_lambda * kl
                loss = loss + kl_loss
                self._last_kl_loss = mx.stop_gradient(kl_loss)

        return loss

    def _aggregate_dispatch(self, all_pass_alarm):
        """Aggregate live dispatch weights across all passes."""
        accum = None
        count = 0
        for pa in all_pass_alarm:
            dw = pa.get('dispatch_weights_live')
            if dw is not None:
                dw_mean = mx.mean(dw, axis=(0, 1))
                accum = dw_mean if accum is None else accum + dw_mean
                count += 1
        if accum is not None and count > 0:
            return accum / count
        return None

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Parameter group separation ────────────────────────────

    def plate_count(self) -> int:
        """Count total ternary plate positions."""
        from ternary import count_ternary_weights
        return count_ternary_weights(self)

    def param_summary(self) -> dict:
        """Summary of parameter counts."""
        n_plate = self.plate_count()
        return {
            "plate_positions": n_plate,
            "plate_bytes": n_plate * 2 // 8,  # 2 bits per position
        }
