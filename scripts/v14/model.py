"""v14 Model — Controller VSM (Tree of Stride-Stacks).

Tree of VSMs at d=1280. 16 strides, 8 passes, 2 stacks.
Base plates from Qwen3.6-27B extraction.
Delta plates (no-block on attention) discover stride-stack corrections.

  ControllerVSM
    S5: crystal identity (dual crystal, GRU self-model)
    S4: intelligence (global algedonic pattern detection)
    S3: resource allocation (S5Reweight across all 8 passes)
    S2: anti-oscillation (PID dampening at stack boundary)
    MetaS3: fire alarm (existential threat bypass)
    |
    +-- StrideStack A (ascending, 4 passes, s1→s32768)
    +-- StrideStack C (descending, 4 passes, s32768→s1, exact mirror of A)

Data flow: x → A → C → S5Reweight → output
Algedonic: C→A (bottom-up), all→S4→S5 (global)

License: MIT
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import mlx.core as mx
import mlx.nn as nn

from config import V14Config, D_MODEL, D_FF, N_STACKS, N_COMBINATORS, N_TOTAL_COMBINATORS
from ternary import TernaryLinear, TernaryEmbedding
from attention import StrideStack
from stack_vsm import StrideStackVSM, AlgedonicCombiner
from components import (
    S5Identity,
    S4Intelligence,
    S2AntiOscillation,
    MetaS3FireAlarm,
    S5Reweight,
)
from crystal import CrystalLoss
from kernel import COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES


# ══════════════════════════════════════════════════════════════════════
# Spectral φ-ratio loss (session 137)
# ══════════════════════════════════════════════════════════════════════

def spectral_phi_loss(
    hidden_states: mx.array,
    target_ratio: float = 0.6299,
    target_std: float = 0.019,
    subsample: int = 64,
) -> tuple[mx.array, mx.array]:
    """Differentiable proxy for SVD spectrum compression ratio.

    Uses spectral kurtosis: tr(C²) / tr(C)² where C = H^T H / n.
    For a geometric spectrum with ratio r, this converges to
    (1 - r²) / (1 + r²). Target for r=0.6299: κ=0.4374.
    """
    B, L, D = hidden_states.shape
    H = hidden_states.reshape(B * L, D)
    n_tokens = H.shape[0]

    if n_tokens > subsample:
        idx = mx.random.randint(0, n_tokens, (subsample,))
        H = H[idx]

    H = H - mx.mean(H, axis=0, keepdims=True)
    n = H.shape[0]
    C = (H.T @ H) / n

    tr_C = mx.sum(mx.diagonal(C))
    C2 = C @ C
    tr_C2 = mx.sum(mx.diagonal(C2))
    kurtosis = tr_C2 / (tr_C * tr_C + 1e-10)
    kurtosis = mx.minimum(kurtosis, 100.0)  # cap to prevent overflow

    r = target_ratio
    target_kurtosis = (1.0 - r * r) / (1.0 + r * r)
    dkdr = abs(-4 * r / (1 + r * r) ** 2)
    kurtosis_margin = target_std * dkdr

    deviation = mx.abs(kurtosis - target_kurtosis)
    excess = mx.maximum(deviation - kurtosis_margin, 0.0)
    loss = excess * excess

    return loss, kurtosis


# ══════════════════════════════════════════════════════════════════════
# V14Model
# ══════════════════════════════════════════════════════════════════════


class V14Model(nn.Module):
    """Controller VSM: 2 StrideStackVSMs + S5/S4/S3/S2 hierarchy.

    Forward:
      1. Embed tokens
      2. A(x, alg_prev) → C(x_a)  [sequential]
      3. Collect all 8 pass deltas → S5Reweight → meta-gates
      4. Fire alarm: dampen toward neutral when alarmed
      5. Final reweighting: x_final = x_c - ungated + gated
      6. S5↔S4 closed loop (crystal custodian)
      7. Output + loss (CE, crystal, parity, spectral φ)
    """

    def __init__(self, cfg: V14Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model

        # ── Embedding ─────────────────────────────────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # ── Crystal (dual: 8 positive + 8 anti) ──────────────
        self.combinator_embeddings = mx.random.normal((N_COMBINATORS, d)) * 0.02
        self.anti_combinator_embeddings = mx.random.normal((N_COMBINATORS, d)) * 0.02

        # ── Crystal loss system ───────────────────────────────
        self.crystal_loss_fn = CrystalLoss()

        # ── Per-stack FFN plates (from teacher extraction) ────
        self.ffn_key_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_gate_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_value_plate_a = TernaryLinear(cfg.d_ff, d, pre_norm=False)
        self.ffn_key_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_gate_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_value_plate_c = TernaryLinear(cfg.d_ff, d, pre_norm=False)

        # ── Shared StrideStack (one set of 16 lenses) ─────────
        self.shared_stride_stack = StrideStack(cfg)

        # ── Two StrideStackVSMs (share the same lenses) ───────
        self.stack_a = StrideStackVSM(
            cfg, cfg.stack_a_bands,
            self.ffn_key_plate_a, self.ffn_gate_plate_a, self.ffn_value_plate_a,
            self.shared_stride_stack,
            is_descending=False,
        )
        self.stack_c = StrideStackVSM(
            cfg, cfg.stack_c_bands,
            self.ffn_key_plate_c, self.ffn_gate_plate_c, self.ffn_value_plate_c,
            self.shared_stride_stack,
            is_descending=True,
        )

        # ── Algedonic combiner: C → A ─────────────────────────
        self.alg_combiner_a = AlgedonicCombiner(n_sources=1, alg_dim=cfg.alg_dim)

        # ── S5 Identity ───────────────────────────────────────
        self.s5_identity = S5Identity(
            d_identity=cfg.d_identity,
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            n_regulation=cfg.n_regulation_surfaces,
            n_proposals=cfg.s4_n_proposals,
            clip=cfg.identity_clip,
            gru_bias_init=cfg.s5_gru_bias_init,
        )

        # ── S4 Intelligence ───────────────────────────────────
        self.s4 = S4Intelligence(
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            hidden_dim=cfg.s4_hidden_dim,
            n_proposals=cfg.s4_n_proposals,
            d_identity=cfg.d_identity,
        )

        # ── S3: S5Reweight across all 8 passes ───────────────
        self.s5_reweight = S5Reweight(d, n_passes=cfg.n_passes)

        # ── S2 Anti-oscillation ───────────────────────────────
        self.s2_anti_osc = S2AntiOscillation(
            n_boundaries=N_STACKS - 1,
            s4_signal_dim=cfg.s4_hidden_dim,
            p_gain_init=cfg.s2_p_gain_init,
            d_gain_init=cfg.s2_d_gain_init,
        )

        # ── MetaS3 Fire alarm ─────────────────────────────────
        self.fire_alarm = MetaS3FireAlarm(
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            bias_init=cfg.fire_alarm_bias_init,
        )

        # ── Cached algedonics (one step back) ─────────────────
        self._prev_alg_c = None

        # ── State ─────────────────────────────────────────────
        self._crystal_ema = mx.array(1.0)
        self._training_step = 0

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Crystal ───────────────────────────────────────────────

    def compute_crystal_losses(self) -> dict:
        """Full crystal loss: lattice MSE + geodesic parity + cross-zone."""
        emb_all = mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)
        return self.crystal_loss_fn(emb_all)

    def _crystal_sub_metrics(self, crystal_mse: mx.array) -> mx.array:
        """Structured sub-lattice metrics for S5's self-image."""
        emb_pos = self.combinator_embeddings
        norms = mx.sqrt(mx.sum(emb_pos * emb_pos, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_pos / norms
        cos_matrix = emb_norm @ emb_norm.T

        # Composition cluster: mean(cos(B,C), cos(B,D), cos(C,D))
        comp_cluster = (cos_matrix[2, 3] + cos_matrix[2, 4] + cos_matrix[3, 4]) / 3.0
        # WHNF anti-correlation
        whnf_anti = mx.mean(cos_matrix[7, :7])
        # I separation
        i_separation = (cos_matrix[1, 0] + cos_matrix[1, 2] + cos_matrix[1, 3]) / 3.0
        # Cross-crystal diagonal
        emb_anti = self.anti_combinator_embeddings
        norms_anti = mx.sqrt(mx.sum(emb_anti * emb_anti, axis=-1, keepdims=True) + 1e-8)
        emb_anti_norm = emb_anti / norms_anti
        cross_crystal = mx.mean(mx.sum(emb_norm * emb_anti_norm, axis=-1))

        return mx.stack([crystal_mse, comp_cluster, whnf_anti, i_separation, cross_crystal])

    # ── PR Monitoring (grating cascade observation) ─────────

    def enable_pr_monitoring(self):
        """Enable participation ratio monitoring at stack boundaries.
        Pure observation — no parameters, no grad impact, no checkpoint change.
        """
        self._monitor_pr = True
        self._pr_snapshots = None
        # Precompute crystal basis for projection
        emb_all = mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)
        norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
        self._crystal_basis = mx.stop_gradient(emb_all / norms)  # (16, d)

    def disable_pr_monitoring(self):
        self._monitor_pr = False
        self._pr_snapshots = None

    def _compute_pr_snapshots(self, x_embed, x_a, x_c) -> dict:
        """Compute PR in crystal eigenbasis at each stack boundary.
        All operations are stop_gradient — zero impact on training.
        """
        basis = self._crystal_basis  # (16, d)
        snapshots = {}
        for name, tensor in [("embed", x_embed), ("post_A", x_a), ("post_C", x_c)]:
            t = mx.stop_gradient(tensor)
            # Project to crystal space: (B, L, d) @ (d, 16) → (B, L, 16)
            proj = t @ basis.T
            # Flatten batch: (B*L, 16)
            proj_flat = proj.reshape(-1, 16)
            # Covariance
            mean = mx.mean(proj_flat, axis=0, keepdims=True)
            centered = proj_flat - mean
            n = centered.shape[0]
            cov = (centered.T @ centered) / n  # (16, 16)
            # Eigenvalues (use numpy — small matrix)
            mx.eval(cov)
            cov_np = np.array(cov, dtype=np.float32)
            eigvals = np.maximum(np.linalg.eigvalsh(cov_np)[::-1], 0)
            pr = float((eigvals.sum() ** 2) / (np.sum(eigvals ** 2) + 1e-12))
            sigma1_frac = float(eigvals[0] / (eigvals.sum() + 1e-12))
            snapshots[name] = {"pr": pr, "sigma1": sigma1_frac}
        return snapshots

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
        x_embed = x  # save for hyperbolic norm loss

        # ── Bottom-up algedonic from previous step ────────────
        if self._prev_alg_c is not None:
            alg_for_a = self.alg_combiner_a(self._prev_alg_c)
        else:
            alg_for_a = None

        # ── Sequential: A → C ────────────────────────────────
        x_a, alg_a, deltas_a, gates_a = self.stack_a(x, downstream_alg=alg_for_a)
        x_c, alg_c, deltas_c, gates_c = self.stack_c(x_a)

        # Collect all pass deltas and gates (across all stacks)
        all_deltas = deltas_a + deltas_c  # 4+4 = 8
        all_gates = gates_a + gates_c

        # ── PR monitoring (pure observation, no grad impact) ──
        # Measures participation ratio in crystal eigenbasis at stack boundaries.
        # Detects progressive collapse: PR < 3 = computation in 2D.
        # Cost: O(B×L×d×16) ≈ negligible vs stride stack.
        if getattr(self, '_monitor_pr', False):
            self._pr_snapshots = self._compute_pr_snapshots(x, x_a, x_c)

        # ── Cache algedonics for next step ────────────────────
        self._prev_alg_c = mx.stop_gradient(alg_c)

        # ── Crystal loss system ───────────────────────────────
        crystal_results = self.compute_crystal_losses()
        crystal_mse = crystal_results["crystal_mse"]

        # Parity + cross-zone: diagnostic only (not enforced in loss).
        # Routing geometry is architecture-specific — stride-stack will
        # find its own routing. We observe whether it converges naturally.
        self._last_parity = mx.stop_gradient(crystal_results["parity"])
        self._last_cross_zone = mx.stop_gradient(crystal_results["cross_zone"])

        # ── S5/S4 loop ────────────────────────────────────────
        all_alg = [alg_a, alg_c]
        s5_policy = mx.stop_gradient(self.s5_identity.identity_state)
        s4_proposals, s2_signal = self.s4(all_alg, s5_policy)

        crystal_sub = self._crystal_sub_metrics(crystal_mse)
        regulation, accepted, s5_alarm = self.s5_identity(crystal_sub, all_alg, s4_proposals)

        # MetaS3 fire alarm
        alarm_level = self.fire_alarm(all_alg, crystal_mse)

        # S2 dampening
        self._s2_dampening = self.s2_anti_osc([x_a, x_c], s2_signal)

        # ── S3: S5Reweight across all 8 passes ───────────────
        meta_gates = self.s5_reweight(all_deltas)

        # Fire alarm: dampen toward neutral when alarm fires
        override = 1.0 - alarm_level
        effective_gates = meta_gates * override + 0.12 * (1.0 - override)

        # ── Final reweighting ─────────────────────────────────
        # Remove raw ungated contributions, replace with meta-gated
        total_ungated = all_deltas[0]
        for i in range(1, len(all_deltas)):
            total_ungated = total_ungated + all_deltas[i]

        total_gated = effective_gates[0] * all_deltas[0]
        for i in range(1, len(all_deltas)):
            total_gated = total_gated + effective_gates[i] * all_deltas[i]

        x_final = x_c - total_ungated + total_gated

        # ── Output ────────────────────────────────────────────
        x_out = self.output_norm(x_final)
        self._last_hidden = x_out
        logits = self.embed.output_proj(x_out)

        # ── Loss ──────────────────────────────────────────────
        loss = None
        if targets is not None:
            loss = self._compute_loss(
                logits, targets, effective_gates, all_deltas,
                crystal_mse, regulation, alarm_level, x_out,
                x_embed=x_embed, x_a=x_a, x_c=x_c,
            )

        # ── Diagnostics cache ─────────────────────────────────
        self._last_regulation = mx.stop_gradient(regulation)
        self._last_alarm = mx.stop_gradient(alarm_level)
        self._last_alg = [mx.stop_gradient(a) for a in all_alg]

        return logits, loss

    def _compute_loss(
        self, logits, targets, effective_gates, all_deltas,
        crystal_mse, regulation, alarm_level, x_out,
        x_embed=None, x_a=None, x_c=None,
    ):
        """Loss = CE × crystal_factor + crystal_direct + spectral + hyperbolic."""
        B, L = targets.shape
        cfg = self.cfg

        # CE loss
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        self._last_ce = mx.stop_gradient(ce_loss)

        # ── Crystal multiplicative coupling ───────────────────
        crystal_enforcement = regulation[0] * 2.0  # (0,1) → (0,2)

        # EMA (no gradient to embeddings)
        self._crystal_ema = mx.stop_gradient(
            0.99 * self._crystal_ema + 0.01 * crystal_mse)
        crystal_exp_arg = cfg.rel_lambda * crystal_enforcement * self._crystal_ema
        crystal_factor = mx.exp(mx.minimum(crystal_exp_arg, 4.0))

        # Crystal warmup: cosine anneal from start → floor
        if cfg.crystal_warmup_steps > 0 and self._training_step < cfg.crystal_warmup_steps:
            progress = self._training_step / cfg.crystal_warmup_steps
            high = cfg.crystal_direct_lambda_start
            low = cfg.crystal_direct_lambda
            crystal_direct_eff = low + (high - low) * 0.5 * (1.0 + math.cos(math.pi * progress))
        else:
            crystal_direct_eff = cfg.crystal_direct_lambda

        crystal_direct = crystal_direct_eff * crystal_enforcement * crystal_mse
        self._last_crystal_mse = mx.stop_gradient(crystal_mse)

        # ── Spectral φ-ratio loss ─────────────────────────────
        spectral_loss = mx.array(0.0)
        if cfg.use_spectral_loss and x_out is not None:
            s_loss, s_kurtosis = spectral_phi_loss(
                x_out, cfg.spectral_target_ratio, cfg.spectral_target_std)
            spectral_loss = cfg.spectral_lambda * s_loss
            self._last_spectral_kurtosis = mx.stop_gradient(s_kurtosis)

        # ── Hyperbolic norm growth ────────────────────────────
        # norm(embed) < norm(stack_a) < norm(stack_c)
        hyp_loss = mx.array(0.0)
        if x_a is not None and x_c is not None:
            norm_embed = mx.sqrt(mx.mean(x_embed * x_embed) + 1e-8)
            norm_a = mx.sqrt(mx.mean(x_a * x_a) + 1e-8)
            norm_c = mx.sqrt(mx.mean(x_c * x_c) + 1e-8)
            hyp_loss = (mx.maximum(norm_embed - norm_a, 0.0)
                        + mx.maximum(norm_a - norm_c, 0.0))

        # ── Total ─────────────────────────────────────────────
        loss = (ce_loss * crystal_factor
                + crystal_direct
                + spectral_loss
                + 0.1 * hyp_loss)

        return loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v14 model.py self-test")
    print("=" * 60)

    cfg = V14Config()

    print("\nInstantiating V14Model...")
    model = V14Model(cfg)
    mx.eval(model.parameters())
    print(f"  ✓ (d={cfg.d_model}, {cfg.n_passes} passes, {N_STACKS} stacks, A+C)")

    print("\nForward (no targets)...")
    tokens = mx.random.randint(0, 1000, (1, 32))
    logits, loss = model(tokens)
    mx.eval(logits)
    assert logits.shape == (1, 32, cfg.vocab_size)
    assert loss is None
    print(f"  logits: {logits.shape} ✓")

    print("\nForward (with targets)...")
    targets = mx.random.randint(0, 1000, (1, 32))
    logits2, loss2 = model(tokens, targets)
    mx.eval(logits2, loss2)
    assert loss2.shape == ()
    print(f"  loss: {loss2.item():.4f}")
    print(f"  CE: {model._last_ce.item():.4f}")
    print(f"  crystal_mse: {model._last_crystal_mse.item():.6f}")
    print(f"  parity: {model._last_parity.item():.4f}")
    print(f"  cross_zone: {model._last_cross_zone.item():.4f}")
    if hasattr(model, '_last_spectral_kurtosis'):
        print(f"  spectral_κ: {model._last_spectral_kurtosis.item():.4f}")

    print(f"  alarm: {model._last_alarm.item():.4f}")
    print(f"  regulation: {[f'{r:.3f}' for r in model._last_regulation.tolist()]}")

    print("\nSecond forward (tests C→A algedonic + S5 state)...")
    logits3, loss3 = model(tokens, targets)
    mx.eval(logits3, loss3)
    assert model._prev_alg_c is not None, "_prev_alg_c should be cached"
    print(f"  loss: {loss3.item():.4f} (with C→A algedonic) ✓")

    print("\nGradient flow...")
    def model_loss(m, tok, tgt):
        _, loss = m(tok, tgt)
        return loss

    gfn = nn.value_and_grad(model, model_loss)
    lv, g = gfn(model, tokens, targets)
    mx.eval(lv, g)
    print(f"  loss={lv.item():.4f} ✓")

    from ternary import count_ternary_weights
    n_plate = count_ternary_weights(model)
    print(f"\n  Ternary positions: {n_plate:,}")
    print(f"  Ternary MB: {n_plate * 2 / 8 / 1024 / 1024:.1f}")

    print("\n" + "=" * 60)
    print("v14 model.py: all tests passed ✓")
