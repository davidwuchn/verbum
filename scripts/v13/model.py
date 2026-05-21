"""
v13 Model — Register-Free Beam/Plate Architecture.

Evolution: registers removed entirely. Stride overlaps between fractal
bands carry cross-scale state naturally through the shared StrideStack —
the intersection points where multiple attention scales see the same
hidden state. No abstract register vectors needed.

8-pass hourglass (power-of-2):
  L0↑ → L1↑ → L2↑ → L3↑ → L3↓ → L2↓ → L1↓ → L0↓
  Pass  0       1       2      3      4      5      6      7

Key changes from previous version:
  - Remove all register machinery (register_inits, register_norm, banks)
  - Remove S4Ternary, MetaS4Ternary, RetrievalRegisters
  - 8 passes (was 7): apex splits into L3↑ and L3↓
  - S3: gate_phase(delta, phase_idx) → (gate,) — no registers
  - S5: takes only pass_deltas, no banks
  - AlgedonicAlert: 8-pass INPUT_DIM=58
  - _run_level_pass: just dispatch→stride→integrate, each S3-gated

License: MIT
"""

from __future__ import annotations

import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V13Config
from ternary import TernaryLinear, TernaryEmbedding
from attention import HybridStrideStack
from components import (
    S3Ternary,
    S5Reweight,
    S2Coordinator,
    AlgedonicAlert,
)
from kernel_dispatch import CombinatorDispatch, CombinatorIntegrate, N_COMBINATORS


# ══════════════════════════════════════════════════════════════════════
# Crystal diagnostics — measure lattice formation from PCA-Q targets
# ══════════════════════════════════════════════════════════════════════


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


# ══════════════════════════════════════════════════════════════════════
# Crystal lattice loss — PCA-Q zone targets (constant, every step)
# ══════════════════════════════════════════════════════════════════════


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


# ══════════════════════════════════════════════════════════════════════
# V13Model — Register-Free 8-Pass Hourglass
# ══════════════════════════════════════════════════════════════════════


class V13Model(nn.Module):
    """Register-free VSM: 8-combinator dispatch + shared stride stack.

    8 passes: L0↑ → L1↑ → L2↑ → L3↑ → L3↓ → L2↓ → L1↓ → L0↓

    Stride overlaps between fractal bands carry cross-scale state:
      L0↑↔L1↑: s4, s8   — token↔phrase boundary
      L1↑↔L2↑: s16, s32 — phrase↔paragraph boundary
      L2↑↔L3↑: s128     — paragraph↔document boundary
      L3↑↔L3↓: full apex band (s128..s1024)
      and mirrors on the descending arm.
    """

    N_PASSES = 8
    N_ASC_PASSES = 4
    N_DESC_PASSES = 4
    PASS_NAMES = (
        "L0_asc", "L1_asc", "L2_asc", "L3_asc",
        "L3_desc", "L2_desc", "L1_desc", "L0_desc",
    )

    def __init__(self, cfg: V13Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model

        # ── S5: Identity ──────────────────────────────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # ── S1: Unified stride stack (ALL 8 passes share this) ────
        # The shared stack carries cross-scale state through stride overlaps.
        self.stride_stack = HybridStrideStack.from_config(cfg)

        # ── S1: Dispatch→Stride→Integrate ─────────────────────
        self.combinator_dispatch = CombinatorDispatch(cfg)
        self.combinator_integrate = CombinatorIntegrate(cfg)

        # ── S3: Per-pass gating (8 separate instances) ─────────
        self.s3_passes = [
            S3Ternary(d, n_phases=3)
            for _ in range(self.N_PASSES)
        ]

        # ── Modulation projections ────────────────────────────
        # 4 ascending + 4 descending, each with 3 phases
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False) for _ in range(4)]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False) for _ in range(4)]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── S2: Direction coordination ─────────────────────────
        self.s2 = S2Coordinator(d)

        # ── S5: Pass reweighting ──────────────────────────────
        self.s5_reweight = S5Reweight(d, n_passes=self.N_PASSES)

        # ── Algedonic alert ───────────────────────────────────
        self.algedonic = AlgedonicAlert(
            n_passes=self.N_PASSES, n_combinators=N_COMBINATORS)

        # ── PCA-Q zone targets (frozen constants) ─────────────
        self._zone_targets = [
            mx.array(cfg.pcaq_zone_a_targets),
            mx.array(cfg.pcaq_zone_b_targets),
            mx.array(cfg.pcaq_zone_c_targets),
        ]

        # ── Holographic progressive loss schedule ──────────────
        self._holo_lambda_effective = 0.0  # ramped by train loop

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Helpers ───────────────────────────────────────────────

    @property
    def max_seq_len(self) -> int:
        return self.cfg.max_seq_len

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        # phase_idx here is 0,1,2 within a pass; use pass-local idx for proj
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        # mod_projs has 4 entries (one per ascending/descending pass-group phase 0)
        # We use phase_idx modulo len(projs) for safety
        proj_idx = phase_idx % len(projs)
        return x + gate * mx.tanh(projs[proj_idx](delta))

    @staticmethod
    def _delta_rms(delta: mx.array) -> mx.array:
        return mx.sqrt(mx.mean(delta * delta) + 1e-8)

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
    ) -> mx.array:
        """Pack operational health metrics into a single vector for AlgedonicAlert.

        Layout (total = 58, padded to 64):
          1. S3 gate means  (8)
          2. S3 gate mins   (8)
          3. S2 conflicts   (7)
          4. Dispatch means (8)
          5. Dispatch entropy (1)
          6. Compute gate   (2)
          7. Raw delta norms (8)
          8. Gated delta norms (8)
          9. Suppression ratios (8)
        """
        metrics = []

        # 1. S3 gate means per pass (8)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_sum = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_sum = gate_sum + g
                metrics.append(gate_sum / len(pass_gates))
            else:
                metrics.append(mx.array(0.5))

        # 2. S3 gate mins per pass (8)
        for pass_gates in all_s3_gates:
            if pass_gates:
                gate_min = pass_gates[0]
                for g in pass_gates[1:]:
                    gate_min = mx.minimum(gate_min, g)
                metrics.append(gate_min)
            else:
                metrics.append(mx.array(0.5))

        # 3. S2 conflict cosines (7 = N_PASSES - 1)
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

        # 7. Raw delta RMS norms (8)
        for rd in raw_deltas:
            metrics.append(self._delta_rms(rd))

        # 8. Gated delta RMS norms (8)
        for pd in pass_deltas:
            metrics.append(self._delta_rms(pd))

        # 9. S3 suppression ratio per pass (8)
        for pd, rd in zip(pass_deltas, raw_deltas):
            gated_rms = self._delta_rms(pd)
            raw_rms = self._delta_rms(rd)
            metrics.append(gated_rms / (raw_rms + 1e-8))

        metrics_flat = [m.reshape(1) if m.ndim == 0 else m.reshape(1)
                        for m in metrics]
        return mx.concatenate(metrics_flat)

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(
        self,
        x: mx.array,
        pass_idx: int,
        is_descending: bool,
    ) -> tuple[mx.array, mx.array, mx.array, list, dict]:
        """Run one level-pass: dispatch → stride → integrate, S3-gated.

        Args:
            x:             (B, L, d_model) residual stream
            pass_idx:      0-7
            is_descending: True for passes 4-7

        Returns:
            x:           updated residual stream
            pass_delta:  net change x_after - x_before
            raw_delta:   sum of all phase raw deltas (ungated)
            phase_gates: list of 3 gate scalars
            pass_alarm:  dict with dispatch_weights_live, compute_gate_live
        """
        x_before = x
        raw_phases = []
        phase_gates = []
        pass_alarm = {
            'dispatch_weights_live': None,
            'compute_gate_live': None,
        }

        # ── Phase 0: Dispatch ──────────────────────────────────
        dispatch_weights, comb_context = self.combinator_dispatch(
            x, pass_idx=pass_idx)
        pass_alarm['dispatch_weights_live'] = dispatch_weights

        delta = comb_context - x
        raw_phases.append(delta)
        (gate,) = self.s3_passes[pass_idx].gate_phase(delta, 0)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=0, is_descending=is_descending)

        # ── Phase 1: Stride (propagate with beam angles) ──────
        reverse = is_descending and self.cfg.desc_stride_reverse
        stride_out = self.stride_stack(x, pass_idx=pass_idx, reverse=reverse)
        delta = stride_out - x
        raw_phases.append(delta)
        (gate,) = self.s3_passes[pass_idx].gate_phase(delta, 1)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=1, is_descending=is_descending)

        # ── Phase 2: Integrate (apply combinator kernels) ─────
        integrate_out = self.combinator_integrate(
            x, dispatch_weights=dispatch_weights, comb_context=comb_context,
            pass_idx=pass_idx)
        delta = integrate_out - x
        raw_phases.append(delta)
        (gate,) = self.s3_passes[pass_idx].gate_phase(delta, 2)
        phase_gates.append(gate)
        x = self._modulate(x, delta, gate, phase_idx=2, is_descending=is_descending)

        if hasattr(self.combinator_integrate, '_compute_gate_live'):
            pass_alarm['compute_gate_live'] = \
                self.combinator_integrate._compute_gate_live

        pass_delta = x - x_before
        raw_delta = raw_phases[0]
        for rd in raw_phases[1:]:
            raw_delta = raw_delta + rd

        return x, pass_delta, raw_delta, phase_gates, pass_alarm

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape

        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x  # save for holographic progressive loss

        pass_deltas = []
        raw_deltas = []
        all_s3_gates = []
        all_pass_alarm = []

        # ── Pass 0: L0↑ ──────────────────────────────────────
        x, pd0, rd0, pg0, pa0 = self._run_level_pass(x, 0, False)
        pass_deltas.append(pd0); raw_deltas.append(rd0)
        all_s3_gates.append(pg0); all_pass_alarm.append(pa0)
        x = x + self.s2.direction_signal(pd0, 0)

        # ── Pass 1: L1↑ ──────────────────────────────────────
        x, pd1, rd1, pg1, pa1 = self._run_level_pass(x, 1, False)
        pass_deltas.append(pd1); raw_deltas.append(rd1)
        all_s3_gates.append(pg1); all_pass_alarm.append(pa1)
        x = x + self.s2.direction_signal(pd1, 1) * S2Coordinator.coherence_factor(pd0, pd1)

        # ── Pass 2: L2↑ ──────────────────────────────────────
        x, pd2, rd2, pg2, pa2 = self._run_level_pass(x, 2, False)
        pass_deltas.append(pd2); raw_deltas.append(rd2)
        all_s3_gates.append(pg2); all_pass_alarm.append(pa2)
        x = x + self.s2.direction_signal(pd2, 2) * S2Coordinator.coherence_factor(pd1, pd2)

        # ── Pass 3: L3↑ (apex ascending) ─────────────────────
        x, pd3, rd3, pg3, pa3 = self._run_level_pass(x, 3, False)
        pass_deltas.append(pd3); raw_deltas.append(rd3)
        all_s3_gates.append(pg3); all_pass_alarm.append(pa3)
        x = x + self.s2.direction_signal(pd3, 3) * S2Coordinator.coherence_factor(pd2, pd3)

        # ── Pass 4: L3↓ (apex descending) ─────────────────────
        x, pd4, rd4, pg4, pa4 = self._run_level_pass(x, 4, True)
        pass_deltas.append(pd4); raw_deltas.append(rd4)
        all_s3_gates.append(pg4); all_pass_alarm.append(pa4)
        x = x + self.s2.direction_signal(pd4, 4) * S2Coordinator.coherence_factor(pd3, pd4)

        # ── Pass 5: L2↓ ──────────────────────────────────────
        x, pd5, rd5, pg5, pa5 = self._run_level_pass(x, 5, True)
        pass_deltas.append(pd5); raw_deltas.append(rd5)
        all_s3_gates.append(pg5); all_pass_alarm.append(pa5)
        x = x + self.s2.direction_signal(pd5, 5) * S2Coordinator.coherence_factor(pd4, pd5)

        # ── Pass 6: L1↓ ──────────────────────────────────────
        x, pd6, rd6, pg6, pa6 = self._run_level_pass(x, 6, True)
        pass_deltas.append(pd6); raw_deltas.append(rd6)
        all_s3_gates.append(pg6); all_pass_alarm.append(pa6)
        x = x + self.s2.direction_signal(pd6, 6) * S2Coordinator.coherence_factor(pd5, pd6)

        # ── Pass 7: L0↓ ──────────────────────────────────────
        x, pd7, rd7, pg7, pa7 = self._run_level_pass(x, 7, True)
        pass_deltas.append(pd7); raw_deltas.append(rd7)
        all_s3_gates.append(pg7); all_pass_alarm.append(pa7)
        # No direction signal after final pass

        # ── S5 reweighting ─────────────────────────────────────
        meta_gates = self.s5_reweight(pass_deltas)

        # ── Algedonic alert ───────────────────────────────────
        alarm_metrics = self._collect_alarm_metrics(
            all_s3_gates, pass_deltas, raw_deltas, all_pass_alarm)
        alarm_factors = self.algedonic(alarm_metrics)

        # Effective gate = S5 × alarm
        effective_gates = meta_gates * alarm_factors

        # Reweight pass contributions
        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = effective_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + effective_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

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
        """Compute total loss: CE + crystal + holographic + dispatch KL + entropy."""
        B, L = targets.shape

        # Cross-entropy
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, self.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        loss = ce_loss
        self._last_ce = mx.stop_gradient(ce_loss)

        # ── Holographic progressive loss ─────────────────────
        # Decode at each pass boundary. Every pass should be decodable.
        # Gradient slope: pass n sees gradient from losses n..N-1.
        # Ascending arm (passes 0-3): steepest gradient → compress
        # Descending arm (passes 4-7): refining gradient → expand
        holo_lambda_eff = getattr(self, '_holo_lambda_effective', 0.0)
        if holo_lambda_eff > 0 and self.cfg.use_holographic_loss:
            holo_loss = mx.array(0.0)
            x_progressive = x_embed  # start from raw embedding

            # Subsample positions for efficiency
            total_pos = B * L
            n_sample = max(64, total_pos // self.cfg.holo_subsample)
            if n_sample < total_pos:
                holo_idx = mx.random.randint(0, total_pos, (n_sample,))
                targets_sample = targets.reshape(-1)[holo_idx]
            else:
                holo_idx = None

            # φ-deviation instrumentation (observation only, not training signal)
            phi = (1.0 + math.sqrt(5.0)) / 2.0
            phi_inv = 1.0 / phi
            self._phi_deviations = []

            for n in range(self.N_PASSES):
                x_progressive = x_progressive + effective_gates[n] * pass_deltas[n]

                # Measure φ-compression ratio (instrumentation only)
                rms_before = mx.sqrt(mx.mean(
                    (x_progressive - effective_gates[n] * pass_deltas[n]) ** 2) + 1e-8)
                rms_after = mx.sqrt(mx.mean(x_progressive ** 2) + 1e-8)
                ratio = float(mx.stop_gradient(rms_after / (rms_before + 1e-8)).item())
                self._phi_deviations.append(ratio - phi_inv)

                # Progressive decode loss
                if holo_idx is not None:
                    x_flat = x_progressive.reshape(total_pos, -1)
                    x_sample = x_flat[holo_idx]
                    logits_n = self.embed.output_proj(self.output_norm(x_sample))
                    loss_n = nn.losses.cross_entropy(logits_n, targets_sample).mean()
                else:
                    logits_n = self.embed.output_proj(
                        self.output_norm(x_progressive))
                    loss_n = nn.losses.cross_entropy(
                        logits_n.reshape(-1, self.cfg.vocab_size),
                        targets.reshape(-1),
                    ).mean()
                holo_loss = holo_loss + loss_n

            loss = loss + holo_lambda_eff * holo_loss
            self._last_holo_loss = mx.stop_gradient(holo_loss)

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
