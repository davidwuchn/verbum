"""
v10 Model — bidirectional VSM with split ascending/descending weights.

Architecture:

  tokens (B, L) → [V6Compressor: 5-pass, 9 strides, registers]
                       → hidden (B, L, d_model)
                       → [output_norm → tied embedding → logits]
                       → next-token cross-entropy

Compressor: v6 proven ascending arm + separate descending arm.
  5 passes: L0_asc → L1_asc → L2_apex → L1_desc → L0_desc
  9 strides (1, 8, 16, 32, 64, 128, 256, 512, 1024), W=8
  3 phases per pass: prep → converge (StrideStack) → consolidate
  3 named registers (type, scope, role), d_register=128, real-valued
  S4 intelligence + S3 gating per pass
  Meta-S4 + Meta-S3 after all passes

  SPLIT WEIGHTS (the key v10 design):
    Ascending arm (L0↑, L1↑, L2_apex): shared prep/stride/consolidate/mod/s4
    Descending arm (L1↓, L0↓): its OWN prep/stride/consolidate/mod/s4

  The ascending arm compresses and types (proven in v6).
  The descending arm has its own weight space to learn dispatch/routing.
  Prior work (sessions 045/054/055/062) established that compression in
  the descending direction doesn't work — the descending arm needs to
  learn a fundamentally different operation.

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
    MetaS3Ternary,
)


# ══════════════════════════════════════════════════════════════════
# V6Compressor — 5-pass bidirectional VSM
# ══════════════════════════════════════════════════════════════════


class V6Compressor(nn.Module):
    """Bidirectional VSM with split ascending/descending weights.

    5 passes:
      L0_asc → L1_asc → L2_apex → L1_desc → L0_desc

    Each pass: S4 scan → prep → S3 gate → converge → S3 gate → consolidate → S3 gate

    ASCENDING arm (L0↑, L1↑, L2_apex) — shared weights:
      prep, stride_stack, consolidate, mod_projs, s4
      Job: compress and type (proven in v6)

    DESCENDING arm (L1↓, L0↓) — its OWN shared weights:
      prep_desc, stride_stack_desc, consolidate_desc, mod_projs_desc, s4_desc
      Job: read typed representation, learn dispatch/routing
      (Prior sessions proved shared compression weights don't work here)

    Per-pass (S3 control):
      5 × S3Ternary instances (one per pass, always separate)
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

        # ── S1: Ascending ops (shared across L0↑, L1↑, L2_apex) ──
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
        #    Own weights — NOT shared with ascending arm.
        #    Same op types, but free to learn different behavior.
        self.prep_desc = TernaryFFN(d, cfg.d_ff, cfg.dropout)
        self.stride_stack_desc = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.consolidate_desc = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)

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
        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Meta-S4 ──────────────────────────────────────────
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── Meta-S3 (with temperature + bias fix) ────────────
        self.meta_s3 = MetaS3Ternary(d_reg, n_registers=n_reg,
                                      n_banks=6, n_passes=self.N_PASSES)

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

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

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks, target_bank):
        x_before = x

        # Select ops: ascending or descending
        s4 = self.s4_desc if is_descending else self.s4
        prep = self.prep_desc if is_descending else self.prep
        strides = self.stride_stack_desc if is_descending else self.stride_stack
        consolidate = self.consolidate_desc if is_descending else self.consolidate

        # S4 scan
        s4_updates, _ = s4(readable_banks, x)
        target_bank = [target_bank[i] + s4_updates[i]
                       for i in range(self.cfg.n_registers)]

        # Phase 0: prep
        prep_out = prep(x)
        delta = prep_out - x
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 0)
        x = self._modulate(x, delta, gate, phase_idx=0, is_descending=is_descending)

        # Phase 1: converge (StrideStack)
        converge_out = strides(x, reverse=is_descending)
        delta = converge_out - x
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 1)
        x = self._modulate(x, delta, gate, phase_idx=1, is_descending=is_descending)

        # Phase 2: consolidate
        consolidate_out = consolidate(x)
        delta = consolidate_out - x
        _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
            target_bank, delta, 2)
        x = self._modulate(x, delta, gate, phase_idx=2, is_descending=is_descending)

        pass_delta = x - x_before
        return x, target_bank, pass_delta

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

        # Initialize register banks
        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []

        # Pass 0: L0_asc
        x, bank_1_asc, pd = self._run_level_pass(
            x, 0, False, [bank_0], bank_1_asc)
        pass_deltas.append(pd)

        # Pass 1: L1_asc
        x, bank_2_asc, pd = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc], bank_2_asc)
        pass_deltas.append(pd)

        # Pass 2: L2_apex
        x, bank_3, pd = self._run_level_pass(
            x, 2, False, [bank_0, bank_1_asc, bank_2_asc], bank_3)
        pass_deltas.append(pd)

        # Pass 3: L1_desc
        x, bank_2_desc, pd = self._run_level_pass(
            x, 3, True, [bank_0, bank_1_asc, bank_2_asc, bank_3], bank_2_desc)
        pass_deltas.append(pd)

        # Pass 4: L0_desc — reads bank_2_desc, not bank_2_asc
        x, bank_1_desc, pd = self._run_level_pass(
            x, 4, True, [bank_0, bank_1_asc, bank_2_desc, bank_3], bank_1_desc)
        pass_deltas.append(pd)

        # Meta-S3: retroactive pass reweighting
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,
                     bank_2_desc, bank_1_desc]
        meta_gates = self.meta_s3(all_banks)

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
          s3_gates:     list of 5 lists of 3 floats (per pass, per phase)
          meta_s3:      list of 5 floats (per-pass contribution gates)
          register_norms: dict of bank_name → list of 3 floats (per register)
          pass_entropy_in:  list of 5 floats
          pass_entropy_out: list of 5 floats
          pass_compression: list of 5 floats (out/in ratio)
          pass_phi_dev:     list of 5 floats (|ratio - 1/φ|)
        """
        import math
        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)

        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        all_s3_gates = []
        pass_h_in = []
        pass_h_out = []

        pass_configs = [
            (0, False, lambda: [bank_0]),
            (1, False, lambda: [bank_0, bank_1_asc]),
            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc]),
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

            # Select ops: ascending or descending
            s4 = self.s4_desc if is_desc else self.s4
            prep = self.prep_desc if is_desc else self.prep
            strides = self.stride_stack_desc if is_desc else self.stride_stack
            consolidate = self.consolidate_desc if is_desc else self.consolidate

            s4_updates, _ = s4(readable, x)
            target = [target[i] + s4_updates[i] for i in range(self.cfg.n_registers)]

            phase_gates = []
            # Phase 0: prep
            prep_out = prep(x)
            delta = prep_out - x
            _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
            mx.eval(gate)
            phase_gates.append(float(gate.item()))
            x = self._modulate(x, delta, gate, 0, is_descending=is_desc)

            # Phase 1: converge
            conv_out = strides(x, reverse=is_desc)
            delta = conv_out - x
            _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
            mx.eval(gate)
            phase_gates.append(float(gate.item()))
            x = self._modulate(x, delta, gate, 1, is_descending=is_desc)

            # Phase 2: consolidate
            cons_out = consolidate(x)
            delta = cons_out - x
            _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
            mx.eval(gate)
            phase_gates.append(float(gate.item()))
            x = self._modulate(x, delta, gate, 2, is_descending=is_desc)

            target_banks[pi] = target
            pass_deltas.append(x - x_before)
            all_s3_gates.append(phase_gates)

            h_out = self._entropy_proxy(x)
            pass_h_out.append(h_out)

        # Re-assign named banks from target_banks
        bank_1_asc = target_banks[0]
        bank_2_asc = target_banks[1]
        bank_3 = target_banks[2]
        bank_2_desc = target_banks[3]
        bank_1_desc = target_banks[4]

        # Meta-S3
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]
        meta_gates = self.meta_s3(all_banks)
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

        metrics = {
            "s3_gates": all_s3_gates,
            "meta_s3": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],
            "register_norms": reg_norms,
            "pass_entropy_in": pass_h_in,
            "pass_entropy_out": pass_h_out,
            "pass_compression": pass_compression,
            "pass_phi_dev": pass_phi_dev,
        }

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
