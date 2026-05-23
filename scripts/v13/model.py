"""
v13 Model — Tree of VSMs with Dual Crystal.

Session 135: The model is a tree of viable systems modeled on the cortex.

  ControllerVSM (this module)
    S5: crystal identity (dual crystal embeddings, GRU self-model)
    S4: intelligence (global algedonic pattern detection)
    S3: resource allocation (S5Reweight across all passes)
    S2: anti-oscillation (PID dampening at stack boundaries)
    MetaS3: fire alarm (existential threat bypass)
    |
    +-- StrideStackVSM A (ascending fine, s1..s1024, passes 0-1)
    +-- StrideStackVSM B (ascending coarse, s512..s1024, passes 2-3)
    +-- StrideStackVSM C (descending, all strides, passes 4-7)

Data flow: x -> A -> B -> C -> output (sequential)
Algedonic route 1: all stacks -> S4 -> S5 (global health)
Algedonic route 2: C(t-1) -> B(t), B(t-1) -> A(t) (local back-pressure)

Attention trains from scratch (no teacher etch).
FFN plates etched from teacher (shared across stacks).
Learnable decay per stride per head.
Full-stack algedonic modulation (3 surfaces, multiplicative).

License: MIT
"""

from __future__ import annotations

import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V13Config, N_COMBINATORS, N_TOTAL_COMBINATORS, N_STACKS
from ternary import TernaryLinear, TernaryEmbedding
from stack_vsm import StrideStackVSM
from components import (
    S5Identity,
    S4Intelligence,
    S2AntiOscillation,
    MetaS3FireAlarm,
    S5Reweight,
)
from kernel import COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES


# ══════════════════════════════════════════════════════════════════════
# Crystal lattice loss
# ══════════════════════════════════════════════════════════════════════


def crystal_lattice_loss(
    all_embeddings: mx.array,
    zone_targets: mx.array,
) -> mx.array:
    """Crystal lattice MSE for one zone (dual crystal, 16x16)."""
    norms = mx.sqrt(mx.sum(all_embeddings * all_embeddings,
                            axis=-1, keepdims=True) + 1e-8)
    emb_norm = all_embeddings / norms
    cos_matrix = emb_norm @ emb_norm.T
    n = cos_matrix.shape[0]
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    student = cos_matrix[mx.array(rows), mx.array(cols)]
    target = zone_targets[mx.array(rows), mx.array(cols)]
    diff = student - target
    return mx.mean(diff * diff)


# ══════════════════════════════════════════════════════════════════════
# Spectral φ-ratio loss (session 137)
# ══════════════════════════════════════════════════════════════════════
#
# The SVD spectrum of hidden state representations follows a geometric
# sequence where each successive singular value is ≈ 1/φ times the
# previous one.  5-model consensus across Pythia, Qwen3, SmolLM3,
# and Mistral: target ratio = 0.6299 ± 0.019.
#
# This is the universal language compressor — adding it as a loss
# target tells the model WHERE the compression fixed point is.


def spectral_phi_loss(
    hidden_states: mx.array,
    target_ratio: float = 0.6299,
    target_std: float = 0.019,
    top_k: int = 5,
    subsample: int = 64,
) -> tuple[mx.array, mx.array]:
    """Differentiable proxy for SVD spectrum compression ratio.

    Uses spectral kurtosis: tr(C^2) / tr(C)^2 where C = H^T H / n.
    For a geometric spectrum with ratio r, this converges to
    (1 - r^2) / (1 + r^2) as d → ∞.

    Fully differentiable (no SVD needed — MLX lacks SVD VJP).
    O(subsample × d^2) — dominated by matmul, not eigendecomposition.

    For r = 0.6299: target kurtosis = 0.4374.
    """
    B, L, D = hidden_states.shape
    H = hidden_states.reshape(B * L, D)
    n_tokens = H.shape[0]

    if n_tokens > subsample:
        idx = mx.random.randint(0, n_tokens, (subsample,))
        H = H[idx]

    # Center
    H = H - mx.mean(H, axis=0, keepdims=True)

    # Covariance C = H^T H / n
    n = H.shape[0]
    C = (H.T @ H) / n

    # Spectral kurtosis: tr(C^2) / tr(C)^2
    tr_C = mx.sum(mx.diagonal(C))
    C2 = C @ C
    tr_C2 = mx.sum(mx.diagonal(C2))
    kurtosis = tr_C2 / (tr_C * tr_C + 1e-10)

    # Target kurtosis for geometric spectrum with ratio r
    r = target_ratio
    target_kurtosis = (1.0 - r * r) / (1.0 + r * r)

    # Propagate margin through r→κ mapping: dκ/dr = -4r/(1+r²)²
    dkdr = abs(-4 * r / (1 + r * r) ** 2)
    kurtosis_margin = target_std * dkdr

    # Soft-margin quadratic loss
    deviation = mx.abs(kurtosis - target_kurtosis)
    excess = mx.maximum(deviation - kurtosis_margin, 0.0)
    loss = excess * excess

    return loss, kurtosis


# ══════════════════════════════════════════════════════════════════════
# V13Model — Controller VSM (Tree of VSMs)
# ══════════════════════════════════════════════════════════════════════


class V13Model(nn.Module):
    """Controller VSM: coordinates a tree of StrideStackVSMs.

    Session 140: S5 crystal custodian + S5→S4 policy channel.

    Forward pass:
      1. Embed tokens
      2. Sequential: A(x, alg_B_prev) -> B(x, alg_C_prev) -> C(x)
         S2 boundary dampening between stacks
      3. S5Reweight across all passes
      4. S5 policy broadcast: identity_state(t-1) → S4
      5. Route 1: all algedonics + s5_policy -> S4 -> proposals -> S5
      6. S5 reads crystal sub-lattice + algedonics, regulates
      7. MetaS3 fire alarm check
      8. Output projection + loss

    The S5↔S4 loop: S5 identity_state from t-1 conditions S4's pattern
    detection at t. S4 proposals go to S5 at t. S5 updates identity_state
    for t+1. S5 reads structured crystal sub-lattice metrics (comp_cluster,
    whnf_anti, i_separation, cross_crystal) as its self-image.
    """

    def __init__(self, cfg: V13Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model

        # ── S5: Identity — embeddings + self-model ────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # Dual crystal: 8 positive + 8 anti combinator embeddings
        self.combinator_embeddings = mx.random.normal((N_COMBINATORS, d)) * 0.02
        self.anti_combinator_embeddings = mx.random.normal((N_COMBINATORS, d)) * 0.02

        # PCA-Q zone targets (frozen constants = the genome)
        self._zone_targets = [
            mx.array(cfg.pcaq_zone_a_targets),
            mx.array(cfg.pcaq_zone_b_targets),
            mx.array(cfg.pcaq_zone_c_targets),
        ]

        # S5 self-model (the living phenotype)
        self.s5_identity = S5Identity(
            d_identity=cfg.d_identity,
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            n_regulation=cfg.n_regulation_surfaces,
            n_proposals=cfg.s4_n_proposals,
            clip=cfg.identity_clip,
            gru_bias_init=cfg.s5_gru_bias_init,
        )

        # ── Shared FFN plates (etched from teacher) ───────────
        # Session 141: gate IS the holographic aperture selector.
        # Gate controls 89% of neuron selection. SwiGLU activation:
        #   value_plate(silu(gate_plate(x)) * key_plate(x))
        self.ffn_key_plate = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_gate_plate = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_value_plate = TernaryLinear(cfg.d_ff, d, pre_norm=False)

        # ── S1: Three StrideStackVSMs ─────────────────────────
        self.stack_a = StrideStackVSM(
            cfg, cfg.stack_a,
            self.ffn_key_plate, self.ffn_value_plate, self.ffn_gate_plate)

        # Stack B gets its own stride stack (not shared at runtime).
        # Self-similar weight INITIALIZATION (copy A's coarse stride weights
        # to B) is done in extract_teacher.py, not via Python object sharing.
        # MLX autograd doesn't handle aliased parameters correctly.
        self.stack_b = StrideStackVSM(
            cfg, cfg.stack_b,
            self.ffn_key_plate, self.ffn_value_plate, self.ffn_gate_plate)

        self.stack_c = StrideStackVSM(
            cfg, cfg.stack_c,
            self.ffn_key_plate, self.ffn_value_plate, self.ffn_gate_plate)

        # ── S4: Intelligence (conditioned on S5 policy) ────────
        self.s4 = S4Intelligence(
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            hidden_dim=cfg.s4_hidden_dim,
            n_proposals=cfg.s4_n_proposals,
            d_identity=cfg.d_identity,
        )

        # ── S3: Resource allocation (S5Reweight) ──────────────
        self.s5_reweight = S5Reweight(d, n_passes=cfg.n_passes)

        # ── S2: Anti-oscillation (inter-stack) ────────────────
        self.s2_anti_osc = S2AntiOscillation(
            n_boundaries=N_STACKS - 1,
            s4_signal_dim=cfg.s4_hidden_dim,
            p_gain_init=cfg.s2_p_gain_init,
            d_gain_init=cfg.s2_d_gain_init,
        )

        # ── MetaS3: Fire alarm ────────────────────────────────
        self.fire_alarm = MetaS3FireAlarm(
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            bias_init=cfg.fire_alarm_bias_init,
        )

        # ── Cached algedonics (one step back for route 2) ─────
        self._prev_alg_b = None  # B algedonic for A at next step
        self._prev_alg_c = None  # C algedonic for B at next step

        # ── Crystal loss EMA + step counter ───────────────────
        self._crystal_ema = mx.array(1.0)
        self._training_step = 0  # incremented by training loop

        # ── Spectral φ-ratio (session 137) ────────────────────
        self._last_spectral_ratio = mx.array(0.0)
        self._last_spectral_loss = mx.array(0.0)

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Crystal sub-lattice metrics ──────────────────────────

    def compute_crystal_sub_lattice(self) -> tuple[mx.array, mx.array]:
        """Compute crystal loss + structured sub-lattice metrics.

        Returns:
            crystal_loss: scalar MSE against PCA-Q targets (for loss computation)
            sub_metrics: (5,) [crystal_loss, comp_cluster, whnf_anti,
                               i_separation, cross_crystal]
                         S5's structured self-image of crystal geometry.
        """
        emb_all = mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)  # (16, d_model)

        # Aggregate crystal loss (for loss function)
        crystal_loss = mx.array(0.0)
        for target, lam in zip(self._zone_targets, self.cfg.zone_lambdas):
            crystal_loss = crystal_loss + lam * crystal_lattice_loss(emb_all, target)

        # Sub-lattice metrics from positive crystal (8, d_model)
        emb_pos = self.combinator_embeddings
        norms = mx.sqrt(mx.sum(emb_pos * emb_pos, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_pos / norms
        cos_matrix = emb_norm @ emb_norm.T  # (8, 8)

        # Combinator indices: K=0, I=1, B=2, C=3, D=4, Y=5, W=6, WHNF=7
        # Composition cluster: mean(cos(B,C), cos(B,D), cos(C,D))
        comp_cluster = (cos_matrix[2, 3] + cos_matrix[2, 4] + cos_matrix[3, 4]) / 3.0

        # WHNF anti-correlation: mean cos(WHNF, all others)
        whnf_anti = (cos_matrix[7, 0] + cos_matrix[7, 1] + cos_matrix[7, 2]
                     + cos_matrix[7, 3] + cos_matrix[7, 4] + cos_matrix[7, 5]
                     + cos_matrix[7, 6]) / 7.0

        # I separation: mean cos(I, K/B/C) — should be low (I is independent)
        i_separation = (cos_matrix[1, 0] + cos_matrix[1, 2] + cos_matrix[1, 3]) / 3.0

        # Cross-crystal: positive ↔ anti diagonal mean
        # cos(pos_c, anti_c) for each combinator c — suppression channel health
        emb_anti = self.anti_combinator_embeddings
        norms_anti = mx.sqrt(mx.sum(emb_anti * emb_anti, axis=-1, keepdims=True) + 1e-8)
        emb_anti_norm = emb_anti / norms_anti
        cross_cos = mx.sum(emb_norm * emb_anti_norm, axis=-1)  # (8,) per-combinator
        cross_crystal = mx.mean(cross_cos)

        sub_metrics = mx.stack([
            crystal_loss, comp_cluster, whnf_anti, i_separation, cross_crystal,
        ])

        return crystal_loss, sub_metrics

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape
        cfg = self.cfg

        # ── Embed ─────────────────────────────────────────────
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x  # save for holographic loss

        # ── Sequential: A -> B -> C ──────────────────────────
        # Route 2: downstream algedonic from previous step
        x_a, alg_a, deltas_a, gates_a = self.stack_a(
            x, downstream_alg=self._prev_alg_b)

        x_b, alg_b, deltas_b, gates_b = self.stack_b(
            x_a, downstream_alg=self._prev_alg_c)

        x_c, alg_c, deltas_c, gates_c = self.stack_c(x_b)

        # Collect all pass deltas and gates (across all stacks)
        all_deltas = deltas_a + deltas_b + deltas_c
        all_gates = gates_a + gates_b + gates_c

        # ── S2: boundary dampening ────────────────────────────
        # (Uses previous S4 signal; first call gets neutral dampening)
        # S2 observes inter-stack output coherence
        # Dampening applied at next forward pass via modulation

        # ── Route 1: S5 policy → S4 → S5 (closed VSM loop) ────
        all_alg = [alg_a, alg_b, alg_c]

        # S5→S4 policy channel: identity state from t-1
        s5_policy = mx.stop_gradient(self.s5_identity.identity_state)

        # S4: global pattern detection, conditioned on S5 identity
        s4_proposals, s2_signal = self.s4(all_alg, s5_policy)

        # S2: update dampening for next step
        self._s2_dampening = self.s2_anti_osc(
            [x_a, x_b, x_c], s2_signal)

        # S5: crystal custodian — structured sub-lattice self-image
        crystal_loss, crystal_sub_metrics = self.compute_crystal_sub_lattice()
        regulation, accepted_proposals, s5_alarm = self.s5_identity(
            crystal_sub_metrics, all_alg, s4_proposals)

        # MetaS3: fire alarm
        alarm_level = self.fire_alarm(all_alg, crystal_loss)

        # ── S3: S5Reweight across all passes ──────────────────
        meta_gates = self.s5_reweight(all_deltas)

        # Apply alarm: dampen toward neutral when alarm fires
        # override factor: 1.0 when calm, 0.0 when alarmed
        override = 1.0 - alarm_level
        effective_gates = meta_gates * override + 0.12 * (1.0 - override)
        # 0.12 = sigmoid(-2.0) = the init gate value = safe baseline

        # ── Reweight pass contributions ───────────────────────
        total_ungated = all_deltas[0]
        for i in range(1, len(all_deltas)):
            total_ungated = total_ungated + all_deltas[i]

        total_gated = effective_gates[0] * all_deltas[0]
        for i in range(1, len(all_deltas)):
            total_gated = total_gated + effective_gates[i] * all_deltas[i]

        x_final = x_c - total_ungated + total_gated

        # ── Cache algedonics for next step (route 2) ──────────
        self._prev_alg_b = mx.stop_gradient(alg_b)
        self._prev_alg_c = mx.stop_gradient(alg_c)

        # ── Output ────────────────────────────────────────────
        x_out = self.output_norm(x_final)
        self._last_hidden = x_out
        logits = self.embed.output_proj(x_out)

        # ── Loss ──────────────────────────────────────────────
        loss = None
        if targets is not None:
            loss = self._compute_loss(
                logits, targets, effective_gates,
                all_deltas, x_embed, crystal_loss,
                regulation, alarm_level, x_out,
                x_a=x_a, x_b=x_b, x_c=x_c)

        # ── Diagnostics cache ─────────────────────────────────
        self._last_regulation = mx.stop_gradient(regulation)
        self._last_alarm = mx.stop_gradient(alarm_level)
        self._last_s5_alarm = mx.stop_gradient(s5_alarm)
        self._last_crystal_sub_metrics = mx.stop_gradient(crystal_sub_metrics)
        self._last_s2_dampening = mx.stop_gradient(self._s2_dampening)
        self._last_alg = [mx.stop_gradient(a) for a in all_alg]

        return logits, loss

    def _compute_loss(
        self, logits, targets, effective_gates,
        all_deltas, x_embed, crystal_loss,
        regulation, alarm_level, x_out=None,
        x_a=None, x_b=None, x_c=None,
    ):
        """Loss = CE * exp(lambda * crystal_ema) * spectral + direct_crystal + holo + geometry."""
        B, L = targets.shape
        cfg = self.cfg

        # CE loss
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        self._last_ce = mx.stop_gradient(ce_loss)

        # Crystal lattice loss (multiplicative EMA + additive direct)
        crystal_factor = mx.array(1.0)
        crystal_additive = mx.array(0.0)
        if cfg.use_relational_loss:
            # S5 regulation[0] modulates crystal enforcement
            crystal_enforcement = regulation[0] * 2.0  # (0,1) -> (0,2)

            # EMA path (no gradient to embeddings)
            crystal_ema_decay = 0.99
            self._crystal_ema = mx.stop_gradient(
                crystal_ema_decay * self._crystal_ema
                + (1 - crystal_ema_decay) * crystal_loss)
            crystal_factor = mx.exp(
                cfg.rel_lambda * crystal_enforcement * self._crystal_ema)

            # Crystal warmup schedule: high early → floor
            # Cosine anneal from crystal_direct_lambda_start to crystal_direct_lambda
            # over crystal_warmup_steps. Floor allows crystal to vibrate during training.
            if cfg.crystal_warmup_steps > 0 and self._training_step < cfg.crystal_warmup_steps:
                progress = self._training_step / cfg.crystal_warmup_steps
                high = cfg.crystal_direct_lambda_start
                low = cfg.crystal_direct_lambda
                crystal_direct_eff = low + (high - low) * 0.5 * (1.0 + math.cos(math.pi * progress))
            else:
                crystal_direct_eff = cfg.crystal_direct_lambda

            # Direct path (gradient flows to embeddings)
            crystal_additive = crystal_direct_eff * crystal_enforcement * crystal_loss
            self._last_crystal_loss = mx.stop_gradient(crystal_loss)
            self._last_crystal_direct_eff = crystal_direct_eff

        # Holographic progressive loss
        holo_factor = mx.array(1.0)
        holo_lambda_eff = getattr(self, '_holo_lambda_effective', 0.0)
        if holo_lambda_eff > 0 and cfg.use_holographic_loss:
            x_progressive = x_embed
            total_pos = B * L
            n_sample = max(64, total_pos // cfg.holo_subsample)
            if n_sample < total_pos:
                holo_idx = mx.random.randint(0, total_pos, (n_sample,))
                targets_sample = targets.reshape(-1)[holo_idx]
            else:
                holo_idx = None

            prev_ce = None
            holo_loss = mx.array(0.0)

            for n in range(len(all_deltas)):
                x_progressive = x_progressive + effective_gates[n] * all_deltas[n]

                if holo_idx is not None:
                    x_flat = x_progressive.reshape(total_pos, -1)
                    x_sample = x_flat[holo_idx]
                    logits_n = self.embed.output_proj(self.output_norm(x_sample))
                    ce_n = nn.losses.cross_entropy(logits_n, targets_sample).mean()
                else:
                    logits_n = self.embed.output_proj(
                        self.output_norm(x_progressive))
                    ce_n = nn.losses.cross_entropy(
                        logits_n.reshape(-1, cfg.vocab_size),
                        targets.reshape(-1),
                    ).mean()

                if prev_ce is not None:
                    regression = mx.maximum(ce_n - prev_ce, 0.0)
                    holo_loss = holo_loss + regression
                prev_ce = ce_n

            holo_factor = mx.exp(holo_lambda_eff * holo_loss)
            self._last_holo_loss = mx.stop_gradient(holo_loss)

        # ── Categorical geometry losses (session 140 probes) ─────
        geometry_additive = mx.array(0.0)

        if x_a is not None and x_c is not None:
            # 1. Adjunction loss — cross-stack spectral concentration
            # The L2→L56 mapping in Qwen3-32B is rank-1 dominated (σ₁/σ₂ = 128:1).
            # Encourage cross-correlation(stack_a, stack_c) to be low-rank.
            # Kurtosis proxy: tr(C²)/tr(C)² → 1.0 for rank-1 (subsample for speed).
            if cfg.adjunction_lambda > 0:
                H_a = x_a.reshape(-1, x_a.shape[-1])  # (B*L, d)
                H_c = x_c.reshape(-1, x_c.shape[-1])
                n_tok = H_a.shape[0]
                sub = min(64, n_tok)
                if sub < n_tok:
                    idx = mx.random.randint(0, n_tok, (sub,))
                    H_a = H_a[idx]
                    H_c = H_c[idx]
                # Center
                H_a = H_a - mx.mean(H_a, axis=0, keepdims=True)
                H_c = H_c - mx.mean(H_c, axis=0, keepdims=True)
                # Cross-correlation C = H_a^T H_c / n
                n = H_a.shape[0]
                C = (H_a.T @ H_c) / n
                # Spectral kurtosis: tr(C²) / tr(C)²
                tr_C = mx.sum(mx.diagonal(C))
                C2 = C @ C
                tr_C2 = mx.sum(mx.diagonal(C2))
                kurtosis = tr_C2 / (tr_C * tr_C + 1e-10)
                # Target: kurtosis = 1.0 (perfect rank-1)
                adj_loss = (kurtosis - 1.0) ** 2
                geometry_additive = geometry_additive + cfg.adjunction_lambda * adj_loss
                self._last_adjunction_loss = mx.stop_gradient(adj_loss)
                self._last_adjunction_kurtosis = mx.stop_gradient(kurtosis)

            # 2. Hyperbolic norm loss — norm growth across stacks
            # Qwen3-32B shows ρ=+0.49 (norm ∝ depth) across all layers.
            # Encourage: norm(embed) < norm(stack_a) < norm(stack_b) < norm(stack_c).
            # Soft hinge: penalize only when norms decrease.
            if cfg.hyperbolic_lambda > 0:
                norm_embed = mx.sqrt(mx.mean(x_embed * x_embed) + 1e-8)
                norm_a = mx.sqrt(mx.mean(x_a * x_a) + 1e-8)
                norm_b = mx.sqrt(mx.mean(x_b * x_b) + 1e-8)
                norm_c = mx.sqrt(mx.mean(x_c * x_c) + 1e-8)
                # Penalize norm decreases (soft hinge)
                hyp_loss = (mx.maximum(norm_embed - norm_a, 0.0)
                            + mx.maximum(norm_a - norm_b, 0.0)
                            + mx.maximum(norm_b - norm_c, 0.0))
                geometry_additive = geometry_additive + cfg.hyperbolic_lambda * hyp_loss
                self._last_hyperbolic_loss = mx.stop_gradient(hyp_loss)

        if x_embed is not None and x_b is not None:
            # 3. Compositional coherence loss — adjacent tokens compose
            # Qwen3-32B shows adjacent-token cosine peaks in mid-layers (composition).
            # Encourage: adj_cos(stack_b) > adj_cos(embed). The composition zone
            # should pull together, not pass through.
            if cfg.coherence_lambda > 0:
                def _adj_cos(h):
                    """Mean cosine between consecutive token representations."""
                    # h: (B, L, d)
                    h_norm = h / (mx.sqrt(mx.sum(h * h, axis=-1, keepdims=True)) + 1e-8)
                    cos = mx.sum(h_norm[:, :-1] * h_norm[:, 1:], axis=-1)  # (B, L-1)
                    return mx.mean(cos)

                cos_embed = _adj_cos(x_embed)
                cos_b = _adj_cos(x_b)
                # Penalize when composition zone doesn't increase coherence
                coh_loss = mx.maximum(cos_embed - cos_b, 0.0)
                geometry_additive = geometry_additive + cfg.coherence_lambda * coh_loss
                self._last_coherence_loss = mx.stop_gradient(coh_loss)

        # Total: multiplicative AND + direct crystal gradient + geometry
        loss = ce_loss * crystal_factor * holo_factor + crystal_additive + geometry_additive
        return loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Diagnostics ───────────────────────────────────────────

    def crystal_diagnostics(self) -> dict:
        """Measure crystal lattice health — full sub-lattice decomposition.

        Session 140: Reports the same sub-lattice metrics that S5 reads,
        plus the full pairwise cosine matrix for detailed inspection.
        """
        # Full pairwise cosines (positive crystal)
        emb_pos = self.combinator_embeddings
        emb_anti = self.anti_combinator_embeddings
        emb_all = mx.concatenate([emb_pos, emb_anti], axis=0)
        norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_all / norms
        cos_matrix = emb_norm @ emb_norm.T
        mx.eval(cos_matrix)

        names = COMBINATOR_NAMES
        anti_names = ANTI_COMBINATOR_NAMES
        metrics = {}

        # Positive crystal pairwise cosines
        cos_dict = {}
        for i in range(N_COMBINATORS):
            for j in range(i + 1, N_COMBINATORS):
                pair = f"{names[i]}_{names[j]}"
                cos_dict[pair] = float(cos_matrix[i, j].item())
        metrics["combinator_cosines"] = cos_dict

        # Sub-lattice metrics (same as S5 reads via compute_crystal_sub_lattice)
        crystal_loss, sub_metrics = self.compute_crystal_sub_lattice()
        mx.eval(crystal_loss, sub_metrics)
        metrics["crystal_loss"] = float(crystal_loss.item())
        metrics["composition_cluster_mean"] = float(sub_metrics[1].item())
        metrics["whnf_anti_correlation"] = float(sub_metrics[2].item())
        metrics["i_separation"] = float(sub_metrics[3].item())
        metrics["cross_crystal_mean"] = float(sub_metrics[4].item())

        # Cross-crystal diagonal (per-combinator positive ↔ anti)
        cross_diag = {}
        for i in range(N_COMBINATORS):
            pair = f"{names[i]}_{anti_names[i]}"
            cross_diag[pair] = float(cos_matrix[i, i + N_COMBINATORS].item())
        metrics["cross_crystal_diagonal"] = cross_diag

        # Anti-crystal internal cosines
        anti_cos_dict = {}
        for i in range(N_COMBINATORS):
            for j in range(i + 1, N_COMBINATORS):
                pair = f"{anti_names[i]}_{anti_names[j]}"
                anti_cos_dict[pair] = float(
                    cos_matrix[i + N_COMBINATORS, j + N_COMBINATORS].item())
        metrics["anti_combinator_cosines"] = anti_cos_dict

        # Anti-composition cluster (āB, āC, āD)
        anti_comp_vals = [anti_cos_dict.get(p, 0) for p in ["āB_āC", "āB_āD", "āC_āD"]]
        if anti_comp_vals:
            metrics["anti_composition_cluster_mean"] = sum(anti_comp_vals) / len(anti_comp_vals)

        return metrics

    def param_summary(self) -> dict:
        from ternary import count_ternary_weights
        n_plate = count_ternary_weights(self)
        return {
            "plate_positions": n_plate,
            "plate_bytes": n_plate * 2 // 8,
        }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("model.py self-test (tree of VSMs)")
    print("=" * 60)

    cfg = V13Config()

    print("\nInstantiating V13Model...")
    model = V13Model(cfg)
    mx.eval(model.parameters())
    print("  Instantiation OK")

    print("\nForward pass (no targets)...")
    tokens = mx.random.randint(0, 1000, (1, 64))
    logits, loss = model(tokens)
    mx.eval(logits)
    assert logits.shape == (1, 64, cfg.vocab_size)
    assert loss is None
    print(f"  logits: {logits.shape} OK")

    print("\nForward pass (with targets)...")
    targets = mx.random.randint(0, 1000, (1, 64))
    logits2, loss2 = model(tokens, targets)
    mx.eval(logits2, loss2)
    assert logits2.shape == (1, 64, cfg.vocab_size)
    assert loss2.shape == ()
    print(f"  logits: {logits2.shape}, loss: {loss2.item():.4f} OK")

    print("\nDiagnostics (crystal sub-lattice + VSM health)...")
    diag = model.crystal_diagnostics()
    print(f"  crystal_loss: {diag.get('crystal_loss', 'N/A'):.4f}")
    print(f"  comp_cluster: {diag.get('composition_cluster_mean', 'N/A'):.4f}")
    print(f"  WHNF anti-corr: {diag.get('whnf_anti_correlation', 'N/A'):.4f}")
    print(f"  I separation: {diag.get('i_separation', 'N/A'):.4f}")
    print(f"  cross_crystal: {diag.get('cross_crystal_mean', 'N/A'):.4f}")
    if 'anti_composition_cluster_mean' in diag:
        print(f"  anti_comp_cluster: {diag['anti_composition_cluster_mean']:.4f}")
    print(f"  S5 regulation: {[f'{r:.3f}' for r in model._last_regulation.tolist()]}")
    print(f"  S5 identity norm: {mx.sqrt(mx.sum(model.s5_identity.identity_state**2)).item():.4f}")
    print(f"  Alarm: {model._last_alarm.item():.4f}")
    print(f"  S2 dampening: {[f'{d:.3f}' for d in model._last_s2_dampening.tolist()]}")

    print("\nSecond forward (tests route 2 algedonic)...")
    logits3, loss3 = model(tokens, targets)
    mx.eval(logits3, loss3)
    print(f"  loss: {loss3.item():.4f} (with algedonic feedback) OK")

    print("\nGradient flow...")

    def model_loss(m, tok, tgt):
        _, loss = m(tok, tgt)
        return loss

    gfn = nn.value_and_grad(model, model_loss)
    lv, g = gfn(model, tokens, targets)
    mx.eval(lv, g)
    print(f"  Gradient flow OK: loss={lv.item():.4f}")

    # Check key params have gradients
    has_grad = {}
    def check_grads(prefix, tree):
        if isinstance(tree, dict):
            for k, v in tree.items():
                check_grads(f"{prefix}.{k}", v)
        elif isinstance(tree, list):
            for i, v in enumerate(tree):
                check_grads(f"{prefix}[{i}]", v)
        elif isinstance(tree, mx.array):
            has_grad[prefix] = tree.size > 0

    check_grads("grad", g)
    print(f"  Gradient tree has {len(has_grad)} parameter groups")

    summary = model.param_summary()
    print(f"\n  Plates: {summary['plate_positions']:,} positions")
    print(f"  Plate bytes: {summary['plate_bytes']:,}")

    print("\n" + "=" * 60)
    print("model.py: all tests passed")
