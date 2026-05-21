"""
v13 Model — Dissolved Dispatch Architecture.

CombinatorDispatch and CombinatorIntegrate are dissolved. The stride
stack's Q/K/V crystal plates ARE the kernel functions. The only separate
routing that remains is the WHNF gate (compute vs lookup).

8-pass hourglass (power-of-2):
  L0↑ → L1↑ → L2↑ → L3↑ → L3↓ → L2↓ → L1↓ → L0↓
  Pass  0       1       2      3      4      5      6      7

Key changes from previous version:
  - CombinatorDispatch dissolved: combinator_embeddings kept for crystal
    loss only (relational loss targets), not runtime dispatch
  - CombinatorIntegrate dissolved: replaced by mechanical FFN + WHNF gate
  - S3Ternary: 3 phases → 1 phase (single gate per pass)
  - mod_projs: 4 asc + 4 desc → 8 unified (one per pass)
  - _run_level_pass: dispatch→stride→integrate → stride + WHNF blend
  - AlgedonicAlert: dispatch metrics removed, WHNF gate means added

License: MIT
"""

from __future__ import annotations

import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V13Config, N_COMBINATORS
from ternary import TernaryLinear, TernaryEmbedding
from attention import HybridStrideStack
from components import (
    S3Ternary,
    S5Reweight,
    S2Coordinator,
    AlgedonicAlert,
)


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

    emb = model.combinator_embeddings  # (8, d_model)
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
# V13Model — Dissolved-Dispatch 8-Pass Hourglass
# ══════════════════════════════════════════════════════════════════════


class V13Model(nn.Module):
    """Dissolved-dispatch VSM: stride plates ARE the kernel, WHNF gate routes.

    8 passes: L0↑ → L1↑ → L2↑ → L3↑ → L3↓ → L2↓ → L1↓ → L0↓

    CombinatorDispatch and CombinatorIntegrate are gone. The stride
    stack's Q/K/V crystal plates carry the combinator kernel topology
    directly. The WHNF gate is the only routing decision: compute
    (stride output) vs lookup (mechanical FFN).

    combinator_embeddings: kept as relational loss targets only.
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
        # The Q/K/V crystal plates in each stride layer ARE the kernel.
        self.stride_stack = HybridStrideStack.from_config(cfg)

        # ── Combinator embeddings — relational loss targets only ──
        # Not used for runtime dispatch. Crystal lattice loss nudges
        # these 8 vectors toward the PCA-Q zone targets, giving the
        # stride plates a geometric anchor.
        self.combinator_embeddings = mx.random.normal((N_COMBINATORS, d)) * 0.02

        # ── WHNF gate — per-position scalar ──────────────────
        # "done computing? switch to lookup"
        # sigmoid(-3) ≈ 0.047 → starts nearly always computing
        self.whnf_proj = TernaryLinear(d, 16, pre_norm=True)
        self.whnf_bias = mx.full((1,), -3.0)

        # ── Mechanical FFN — WHNF lookup pathway ─────────────
        # Zero continuous params in path: purely ternary key/value plates.
        self.ffn_key_plate = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_value_plate = TernaryLinear(cfg.d_ff, d, pre_norm=False)

        # ── S3: Per-pass gating (8 separate instances, 1 gate each) ──
        self.s3_passes = [S3Ternary(d) for _ in range(self.N_PASSES)]

        # ── Modulation projections — one per pass (8 total) ───
        # Previously 4 asc + 4 desc (3 phases each); now 1 per pass.
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False) for _ in range(self.N_PASSES)
        ]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── S2: Direction coordination ─────────────────────────
        self.s2 = S2Coordinator(d)

        # ── S5: Pass reweighting ──────────────────────────────
        self.s5_reweight = S5Reweight(d, n_passes=self.N_PASSES)

        # ── Algedonic alert ───────────────────────────────────
        self.algedonic = AlgedonicAlert(n_passes=self.N_PASSES)

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

    @staticmethod
    def _delta_rms(delta: mx.array) -> mx.array:
        return mx.sqrt(mx.mean(delta * delta) + 1e-8)

    # ── Crystal lattice loss (3-zone PCA-Q targets) ───────────

    def compute_crystal_loss(self) -> mx.array:
        """Compute crystal lattice loss across all 3 zones.

        Uses self.combinator_embeddings and compares against
        PCA-Q zone targets. Loss = weighted sum of per-zone MSE.

        Returns: scalar loss.
        """
        emb = self.combinator_embeddings  # (8, d_model)
        total_loss = mx.array(0.0)
        for zone_idx, (target, lam) in enumerate(
                zip(self._zone_targets, self.cfg.zone_lambdas)):
            zone_loss = crystal_lattice_loss(emb, target)
            total_loss = total_loss + lam * zone_loss
        return total_loss

    # ── Alarm metrics collection ─────────────────────────────

    def _collect_alarm_metrics(
        self,
        all_s3_gates: list[mx.array],
        pass_deltas: list[mx.array],
        raw_deltas: list[mx.array],
        all_pass_alarm: list[dict],
    ) -> mx.array:
        """Pack operational health metrics into a single vector for AlgedonicAlert.

        Layout (total = 47, padded to 64 inside AlgedonicAlert):
          1. S3 gate means     (8)
          2. S2 conflicts      (7)
          3. WHNF gate means   (8)
          4. Raw delta norms   (8)
          5. Gated delta norms (8)
          6. Suppression ratios (8)
        """
        metrics = []

        # 1. S3 gate means per pass (8)
        for gate in all_s3_gates:
            metrics.append(gate.reshape(1))

        # 2. S2 conflict cosines (7 = N_PASSES - 1)
        for i in range(self.N_PASSES - 1):
            s_prev = pass_deltas[i].mean(axis=(0, 1))
            s_curr = pass_deltas[i + 1].mean(axis=(0, 1))
            dot = (s_prev * s_curr).sum()
            n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
            n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)
            metrics.append((dot / (n_prev * n_curr)).reshape(1))

        # 3. WHNF gate means per pass (8)
        for pa in all_pass_alarm:
            wg = pa.get('whnf_gate_mean')
            if wg is not None:
                metrics.append(wg.reshape(1))
            else:
                metrics.append(mx.array([0.05]))  # prior: nearly always computing

        # 4. Raw delta RMS norms (8)
        for rd in raw_deltas:
            metrics.append(self._delta_rms(rd).reshape(1))

        # 5. Gated delta RMS norms (8)
        for pd in pass_deltas:
            metrics.append(self._delta_rms(pd).reshape(1))

        # 6. S3 suppression ratio per pass (8)
        for pd, rd in zip(pass_deltas, raw_deltas):
            gated_rms = self._delta_rms(pd)
            raw_rms = self._delta_rms(rd)
            metrics.append((gated_rms / (raw_rms + 1e-8)).reshape(1))

        return mx.concatenate(metrics)

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(
        self,
        x: mx.array,
        pass_idx: int,
        is_descending: bool,
    ) -> tuple[mx.array, mx.array, mx.array, mx.array, dict]:
        """Run one level-pass: stride + WHNF blend, S3-gated.

        The stride stack's Q/K/V crystal plates ARE the kernel functions.
        The WHNF gate blends compute (stride output) vs lookup (mechanical FFN).

        Args:
            x:             (B, L, d_model) residual stream
            pass_idx:      0-7
            is_descending: True for passes 4-7

        Returns:
            x:           updated residual stream
            pass_delta:  net change x_after - x_before
            raw_delta:   ungated combined delta before S3 gate
            gate:        S3 gate scalar for this pass
            pass_alarm:  dict with whnf_gate_mean
        """
        x_before = x

        # Phase 1: Stride stack — crystal Q/K/V plates ARE the kernel
        reverse = is_descending and self.cfg.desc_stride_reverse
        stride_out = self.stride_stack(x, pass_idx=pass_idx, reverse=reverse)

        # Phase 2: WHNF blend — compute vs lookup
        whnf_gate = mx.sigmoid(
            self.whnf_proj(x)[..., :1] + self.whnf_bias
        )  # (B, T, 1)
        ffn_out = self.ffn_value_plate(
            mx.maximum(self.ffn_key_plate(x), 0)
        )  # mechanical FFN

        # Blend: low whnf → mostly compute (stride), high whnf → mostly lookup (FFN)
        out = (1.0 - whnf_gate) * stride_out + whnf_gate * (x + ffn_out)

        delta = out - x_before

        # S3 gate (single gate per pass)
        gate = self.s3_passes[pass_idx](delta)
        x = x_before + gate * mx.tanh(self.mod_projs[pass_idx](delta))

        # Alarm metrics
        pass_alarm = {
            'whnf_gate_mean': mx.stop_gradient(mx.mean(whnf_gate)),
        }

        pass_delta = x - x_before
        return x, pass_delta, delta, gate, pass_alarm

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
        x, pd0, rd0, g0, pa0 = self._run_level_pass(x, 0, False)
        pass_deltas.append(pd0); raw_deltas.append(rd0)
        all_s3_gates.append(g0); all_pass_alarm.append(pa0)
        x = x + self.s2.direction_signal(pd0, 0)

        # ── Pass 1: L1↑ ──────────────────────────────────────
        x, pd1, rd1, g1, pa1 = self._run_level_pass(x, 1, False)
        pass_deltas.append(pd1); raw_deltas.append(rd1)
        all_s3_gates.append(g1); all_pass_alarm.append(pa1)
        x = x + self.s2.direction_signal(pd1, 1) * S2Coordinator.coherence_factor(pd0, pd1)

        # ── Pass 2: L2↑ ──────────────────────────────────────
        x, pd2, rd2, g2, pa2 = self._run_level_pass(x, 2, False)
        pass_deltas.append(pd2); raw_deltas.append(rd2)
        all_s3_gates.append(g2); all_pass_alarm.append(pa2)
        x = x + self.s2.direction_signal(pd2, 2) * S2Coordinator.coherence_factor(pd1, pd2)

        # ── Pass 3: L3↑ (apex ascending) ─────────────────────
        x, pd3, rd3, g3, pa3 = self._run_level_pass(x, 3, False)
        pass_deltas.append(pd3); raw_deltas.append(rd3)
        all_s3_gates.append(g3); all_pass_alarm.append(pa3)
        x = x + self.s2.direction_signal(pd3, 3) * S2Coordinator.coherence_factor(pd2, pd3)

        # ── Pass 4: L3↓ (apex descending) ─────────────────────
        x, pd4, rd4, g4, pa4 = self._run_level_pass(x, 4, True)
        pass_deltas.append(pd4); raw_deltas.append(rd4)
        all_s3_gates.append(g4); all_pass_alarm.append(pa4)
        x = x + self.s2.direction_signal(pd4, 4) * S2Coordinator.coherence_factor(pd3, pd4)

        # ── Pass 5: L2↓ ──────────────────────────────────────
        x, pd5, rd5, g5, pa5 = self._run_level_pass(x, 5, True)
        pass_deltas.append(pd5); raw_deltas.append(rd5)
        all_s3_gates.append(g5); all_pass_alarm.append(pa5)
        x = x + self.s2.direction_signal(pd5, 5) * S2Coordinator.coherence_factor(pd4, pd5)

        # ── Pass 6: L1↓ ──────────────────────────────────────
        x, pd6, rd6, g6, pa6 = self._run_level_pass(x, 6, True)
        pass_deltas.append(pd6); raw_deltas.append(rd6)
        all_s3_gates.append(g6); all_pass_alarm.append(pa6)
        x = x + self.s2.direction_signal(pd6, 6) * S2Coordinator.coherence_factor(pd5, pd6)

        # ── Pass 7: L0↓ ──────────────────────────────────────
        x, pd7, rd7, g7, pa7 = self._run_level_pass(x, 7, True)
        pass_deltas.append(pd7); raw_deltas.append(rd7)
        all_s3_gates.append(g7); all_pass_alarm.append(pa7)
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
            loss = self._compute_loss(logits, targets, effective_gates,
                                       pass_deltas, x_embed)
        return logits, loss

    def _compute_loss(self, logits, targets, effective_gates, pass_deltas, x_embed):
        """Compute total loss with multiplicative AND coupling.

        Loss = CE × (1 + λ_crystal × crystal) × (1 + λ_holo × holo)

        AND semantics: the loss is only small when ALL components are small.
        A CE improvement that degrades the crystal makes loss WORSE (crystal
        amplifies CE). A crystal improvement that hurts CE makes loss WORSE
        (CE multiplies crystal). Only changes that improve both survive.

        Each component is also logged individually for monitoring.
        """
        B, L = targets.shape

        # ── CE loss (base) ────────────────────────────────────
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, self.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        self._last_ce = mx.stop_gradient(ce_loss)

        # ── Crystal lattice loss (nucleation well) ─────────────
        # Exponential coupling creates a deep energy minimum at perfect
        # crystal alignment. The beam falls into the well as GD progresses.
        # At perfect alignment: factor = 1.0 (CE runs freely).
        # At slight misalignment: factor grows exponentially (strong nudge).
        # This IS nucleation physics — the crystal attracts the beam.
        crystal_factor = mx.array(1.0)
        if self.cfg.use_relational_loss:
            crystal_loss = self.compute_crystal_loss()
            crystal_factor = mx.exp(self.cfg.rel_lambda * crystal_loss)
            self._last_crystal_loss = mx.stop_gradient(crystal_loss)

        # ── Holographic progressive loss ──────────────────────
        # Measures whether each pass IMPROVES decodability over the previous.
        # Loss = sum of max(0, CE_n - CE_{n-1}): penalizes regressions only.
        # At 0 = every pass is at least as decodable as the one before.
        # This CAN reach 0 (unlike raw CE sum), so the AND coupling works.
        holo_factor = mx.array(1.0)
        holo_lambda_eff = getattr(self, '_holo_lambda_effective', 0.0)
        if holo_lambda_eff > 0 and self.cfg.use_holographic_loss:
            x_progressive = x_embed

            total_pos = B * L
            n_sample = max(64, total_pos // self.cfg.holo_subsample)
            if n_sample < total_pos:
                holo_idx = mx.random.randint(0, total_pos, (n_sample,))
                targets_sample = targets.reshape(-1)[holo_idx]
            else:
                holo_idx = None

            # φ-deviation instrumentation (observation only)
            phi = (1.0 + math.sqrt(5.0)) / 2.0
            phi_inv = 1.0 / phi
            self._phi_deviations = []

            prev_ce = None
            holo_loss = mx.array(0.0)
            pass_ces = []

            for n in range(self.N_PASSES):
                x_progressive = x_progressive + effective_gates[n] * pass_deltas[n]

                # φ-compression ratio (instrumentation only)
                rms_before = mx.sqrt(mx.mean(
                    (x_progressive - effective_gates[n] * pass_deltas[n]) ** 2) + 1e-8)
                rms_after = mx.sqrt(mx.mean(x_progressive ** 2) + 1e-8)
                ratio = float(mx.stop_gradient(rms_after / (rms_before + 1e-8)).item())
                self._phi_deviations.append(ratio - phi_inv)

                # Progressive decode — CE at this pass boundary
                if holo_idx is not None:
                    x_flat = x_progressive.reshape(total_pos, -1)
                    x_sample = x_flat[holo_idx]
                    logits_n = self.embed.output_proj(self.output_norm(x_sample))
                    ce_n = nn.losses.cross_entropy(logits_n, targets_sample).mean()
                else:
                    logits_n = self.embed.output_proj(
                        self.output_norm(x_progressive))
                    ce_n = nn.losses.cross_entropy(
                        logits_n.reshape(-1, self.cfg.vocab_size),
                        targets.reshape(-1),
                    ).mean()

                pass_ces.append(mx.stop_gradient(ce_n).item())

                # Regression penalty: penalize if this pass is WORSE than previous
                if prev_ce is not None:
                    regression = mx.maximum(ce_n - prev_ce, 0.0)
                    holo_loss = holo_loss + regression
                prev_ce = ce_n

            holo_factor = 1.0 + holo_lambda_eff * holo_loss
            self._last_holo_loss = mx.stop_gradient(holo_loss)
            self._last_pass_ces = pass_ces  # per-pass CE for monitoring

        # ── Multiplicative AND: all must improve together ─────
        loss = ce_loss * crystal_factor * holo_factor

        return loss

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
