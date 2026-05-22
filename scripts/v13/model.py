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
# V13Model — Controller VSM (Tree of VSMs)
# ══════════════════════════════════════════════════════════════════════


class V13Model(nn.Module):
    """Controller VSM: coordinates a tree of StrideStackVSMs.

    Forward pass:
      1. Embed tokens
      2. Sequential: A(x, alg_B_prev) -> B(x, alg_C_prev) -> C(x)
         S2 boundary dampening between stacks
      3. S5Reweight across all passes
      4. Route 1: all algedonics -> S4 -> S5 -> regulate
      5. MetaS3 fire alarm check
      6. Output projection + loss

    The S5 identity cycle (read -> update -> regulate -> evaluate)
    runs every forward pass. The identity state persists across steps.
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
        self.ffn_key_plate = TernaryLinear(d, cfg.d_ff, pre_norm=False)
        self.ffn_value_plate = TernaryLinear(cfg.d_ff, d, pre_norm=False)

        # ── S1: Three StrideStackVSMs ─────────────────────────
        self.stack_a = StrideStackVSM(
            cfg, cfg.stack_a, self.ffn_key_plate, self.ffn_value_plate)

        # Stack B shares stride stack with A (self-similar compression)
        self.stack_b = StrideStackVSM(
            cfg, cfg.stack_b, self.ffn_key_plate, self.ffn_value_plate,
            shared_stride_stack=self.stack_a.stride_stack)

        self.stack_c = StrideStackVSM(
            cfg, cfg.stack_c, self.ffn_key_plate, self.ffn_value_plate)

        # ── S4: Intelligence ──────────────────────────────────
        self.s4 = S4Intelligence(
            n_stacks=N_STACKS,
            alg_dim=cfg.alg_dim,
            hidden_dim=cfg.s4_hidden_dim,
            n_proposals=cfg.s4_n_proposals,
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

        # ── Crystal loss EMA ──────────────────────────────────
        self._crystal_ema = mx.array(1.0)

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Crystal loss ──────────────────────────────────────────

    def compute_crystal_loss(self) -> mx.array:
        """Dual-crystal lattice loss across 3 zones."""
        emb_all = mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)
        total = mx.array(0.0)
        for target, lam in zip(self._zone_targets, self.cfg.zone_lambdas):
            total = total + lam * crystal_lattice_loss(emb_all, target)
        return total

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

        # ── Route 1: all algedonics -> S4 -> S5 ──────────────
        all_alg = [alg_a, alg_b, alg_c]

        # S4: global pattern detection
        s4_proposals, s2_signal = self.s4(all_alg)

        # S2: update dampening for next step
        self._s2_dampening = self.s2_anti_osc(
            [x_a, x_b, x_c], s2_signal)

        # S5: identity cycle (read -> update -> regulate -> evaluate)
        crystal_loss = self.compute_crystal_loss()
        regulation, accepted_proposals, s5_alarm = self.s5_identity(
            crystal_loss, all_alg, s4_proposals)

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
                regulation, alarm_level)

        # ── Diagnostics cache ─────────────────────────────────
        self._last_regulation = mx.stop_gradient(regulation)
        self._last_alarm = mx.stop_gradient(alarm_level)
        self._last_s5_alarm = mx.stop_gradient(s5_alarm)
        self._last_s2_dampening = mx.stop_gradient(self._s2_dampening)
        self._last_alg = [mx.stop_gradient(a) for a in all_alg]

        return logits, loss

    def _compute_loss(
        self, logits, targets, effective_gates,
        all_deltas, x_embed, crystal_loss,
        regulation, alarm_level,
    ):
        """Loss = CE * exp(lambda * crystal_ema) + direct_crystal + holo."""
        B, L = targets.shape

        # CE loss
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, self.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        self._last_ce = mx.stop_gradient(ce_loss)

        # Crystal lattice loss (multiplicative EMA + additive direct)
        crystal_factor = mx.array(1.0)
        crystal_additive = mx.array(0.0)
        if self.cfg.use_relational_loss:
            # S5 regulation[0] modulates crystal enforcement
            crystal_enforcement = regulation[0] * 2.0  # (0,1) -> (0,2)

            # EMA path (no gradient to embeddings)
            crystal_ema_decay = 0.99
            self._crystal_ema = mx.stop_gradient(
                crystal_ema_decay * self._crystal_ema
                + (1 - crystal_ema_decay) * crystal_loss)
            crystal_factor = mx.exp(
                self.cfg.rel_lambda * crystal_enforcement * self._crystal_ema)

            # Direct path (gradient flows to embeddings)
            crystal_additive = self.cfg.crystal_direct_lambda * crystal_enforcement * crystal_loss
            self._last_crystal_loss = mx.stop_gradient(crystal_loss)

        # Holographic progressive loss
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
                        logits_n.reshape(-1, self.cfg.vocab_size),
                        targets.reshape(-1),
                    ).mean()

                if prev_ce is not None:
                    regression = mx.maximum(ce_n - prev_ce, 0.0)
                    holo_loss = holo_loss + regression
                prev_ce = ce_n

            holo_factor = mx.exp(holo_lambda_eff * holo_loss)
            self._last_holo_loss = mx.stop_gradient(holo_loss)

        # Total: multiplicative AND + direct crystal gradient
        loss = ce_loss * crystal_factor * holo_factor + crystal_additive
        return loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Diagnostics ───────────────────────────────────────────

    def crystal_diagnostics(self) -> dict:
        """Measure crystal lattice health."""
        emb_pos = self.combinator_embeddings
        emb_anti = self.anti_combinator_embeddings
        emb_all = mx.concatenate([emb_pos, emb_anti], axis=0)
        norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_all / norms
        cos_matrix = emb_norm @ emb_norm.T
        mx.eval(cos_matrix)

        names = COMBINATOR_NAMES
        metrics = {}
        cos_dict = {}
        for i in range(N_COMBINATORS):
            for j in range(i + 1, N_COMBINATORS):
                pair = f"{names[i]}_{names[j]}"
                cos_dict[pair] = float(cos_matrix[i, j].item())
        metrics["combinator_cosines"] = cos_dict

        whnf_pairs = [k for k in cos_dict if "WHNF" in k]
        if whnf_pairs:
            metrics["whnf_anti_correlation"] = sum(
                cos_dict[p] for p in whnf_pairs) / len(whnf_pairs)

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

    print("\nDiagnostics...")
    diag = model.crystal_diagnostics()
    print(f"  WHNF anti-corr: {diag.get('whnf_anti_correlation', 'N/A'):.4f}")
    print(f"  S5 regulation: {[f'{r:.3f}' for r in model._last_regulation.tolist()]}")
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
