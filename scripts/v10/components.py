"""VSM control components — S4, S3, MetaS4, MetaS3 — MLX.

Ported from src/verbum/v6/components.py. Uses scripts/v10/ternary.py.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2,
preserving the same capacity as v6's complex ℂ^d_register registers without
requiring complex arithmetic in the autograd graph (MLX autograd doesn't
support mx.real/mx.imag + reshape in the backward pass).

Kept as fp32 (not ternary):
  - S3 write_gates (nn.Linear with bias, tiny, sigmoid-init)
  - S3 temperature and learned_bias (scalar parameters)
  - MetaS3 gate_proj (nn.Linear with bias, small)

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════════
# Helpers — register flattening (real-valued, no complex)
# ══════════════════════════════════════════════════════════════════════


def _flatten_registers(registers: list[mx.array]) -> mx.array:
    """Flatten list of real register vectors into one 1D vector."""
    return mx.concatenate(registers, axis=-1)


def _flatten_banks(banks: list[list[mx.array]]) -> mx.array:
    """Flatten all banks' registers into one 1D vector."""
    parts = []
    for bank in banks:
        parts.append(_flatten_registers(bank))
    return mx.concatenate(parts, axis=-1)


def _ternary_1d(proj: TernaryLinear, x: mx.array) -> mx.array:
    """Apply TernaryLinear to a 1D vector, working around MLX autograd
    requiring ≥2D input for quantized_matmul backward pass."""
    return proj(x.reshape(1, -1)).reshape(-1)


# ══════════════════════════════════════════════════════════════════════
# S4 — Intelligence (register-query cross-attention)
# ══════════════════════════════════════════════════════════════════════


class S4Ternary(nn.Module):
    """Register cross-attention: reads register banks, attends to residual,
    produces register updates.

    Real-valued registers (d_reg_real = d_register * 2 each).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,       # logical dimension (real dim = 2×)
        n_registers: int = 3,
        max_banks: int = 7,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2   # real-valued dimension per register
        self.n_registers = n_registers
        self.max_banks = max_banks
        self.scale = d_model ** -0.5

        max_q_dim = max_banks * n_registers * self.d_reg_real
        # Pad to multiple of 16 for TernaryLinear
        self._max_q_dim = ((max_q_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._max_q_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        summary_out = n_registers * self.d_reg_real
        self._summary_out_padded = ((summary_out + 15) // 16) * 16
        self._summary_out = summary_out
        self.summary_proj = TernaryLinear(d_model, self._summary_out_padded, pre_norm=False)

        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        banks: list[list[mx.array]],
        residual: mx.array,
    ) -> tuple[list[mx.array], mx.array]:
        B, L, D = residual.shape

        # Flatten all register banks into query input
        q_input = _flatten_banks(banks)
        # Pad to max
        if q_input.shape[0] < self._max_q_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._max_q_dim - q_input.shape[0],))
            ])

        # Query from register state (1D → 2D for autograd)
        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        # Standard attention: q (d_model,) @ k (B, L, d_model) → (B, L)
        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale  # (B, L)
        attn_weights = mx.softmax(attn, axis=-1)                  # (B, L)
        attn_weights = self.dropout(attn_weights)

        # Weighted sum → mean over batch
        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        summary = summary.mean(axis=0)                          # (d_model,)

        # Project to register update vectors (1D → 2D for autograd)
        updates_flat = _ternary_1d(self.summary_proj, summary)[:self._summary_out]

        updates = []
        for i in range(self.n_registers):
            start = i * self.d_reg_real
            end = start + self.d_reg_real
            updates.append(updates_flat[start:end])

        return updates, mx.stop_gradient(attn_weights)


# ══════════════════════════════════════════════════════════════════════
# S3 — Phase-Coherent Gating
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Phase-coherent control for a single level-pass.

    Scalar alignment gate based on register-delta direction match.
    Real-valued registers.
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_phases: int = 3,
        n_registers: int = 3,
        d_align: int | None = None,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2
        self.n_phases = n_phases
        self.n_registers = n_registers

        if d_align is None:
            d_align = d_model
        self.d_align = d_align

        reg_flat_dim = self.d_reg_real * n_registers
        self._reg_flat_dim = ((reg_flat_dim + 15) // 16) * 16

        # Alignment projections — ternary
        self.proj_align = [
            TernaryLinear(self._reg_flat_dim, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]
        self.proj_delta = [
            TernaryLinear(d_model, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]

        # Temperature and bias — fp32 scalars
        self.temperature = [mx.ones((1,)) for _ in range(n_phases)]
        self.learned_bias = [mx.zeros((1,)) for _ in range(n_phases)]

        # Register write projections — ternary
        d_reg_out = ((self.d_reg_real + 15) // 16) * 16
        self._d_reg_out = d_reg_out
        self.write_projs = [
            TernaryLinear(d_model, d_reg_out, pre_norm=False)
            for _ in range(n_phases * n_registers)
        ]

        # Write gates: kept as nn.Linear (has bias, tiny)
        # Bias init -2.0 → sigmoid(-2) ≈ 0.12
        self.write_gates = [
            nn.Linear(d_model, 1)
            for _ in range(n_phases * n_registers)
        ]
        for wg in self.write_gates:
            wg.bias = mx.full(wg.bias.shape, -2.0)

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

    def gate_phase(
        self,
        registers: list[mx.array],
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array, list[mx.array], mx.array, list[float]]:
        """Gate a phase's output using alignment-based scalar gate."""
        eps = 1e-8

        reg_flat = _flatten_registers(registers)
        # Pad to multiple of 16
        if reg_flat.shape[0] < self._reg_flat_dim:
            reg_flat = mx.concatenate([
                reg_flat,
                mx.zeros((self._reg_flat_dim - reg_flat.shape[0],))
            ])
        reg_dir = reg_flat / (mx.sqrt((reg_flat * reg_flat).sum()) + eps)

        summary = delta.mean(axis=(0, 1))  # (d_model,)
        delta_dir = summary / (mx.sqrt((summary * summary).sum()) + eps)

        reg_proj = _ternary_1d(self.proj_align[phase_idx], reg_dir)     # (d_align,)
        delta_proj = _ternary_1d(self.proj_delta[phase_idx], delta_dir)  # (d_align,)
        alignment = (reg_proj * delta_proj).sum()            # scalar

        gate = mx.sigmoid(
            alignment * self.temperature[phase_idx]
            + self.learned_bias[phase_idx]
        )
        gated_delta = gate * delta

        # Register updates (normalized to prevent unbounded accumulation)
        updated_registers = []
        write_gate_values = []
        for reg_idx in range(self.n_registers):
            write_idx = phase_idx * self.n_registers + reg_idx
            wg = mx.sigmoid(self.write_gates[write_idx](summary.reshape(1, -1)).reshape(-1))
            update = _ternary_1d(self.write_projs[write_idx], summary)[:self.d_reg_real]
            updated_registers.append(
                self.register_norm(registers[reg_idx] + wg * update))
            write_gate_values.append(wg.item())

        return gated_delta, updated_registers, gate, write_gate_values


# ══════════════════════════════════════════════════════════════════════
# MetaS4 — Final structural summary
# ══════════════════════════════════════════════════════════════════════


class MetaS4Ternary(nn.Module):
    """Final intelligence scan: register-query attention over residual."""

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int = 3,
        n_banks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_reg_real = d_register * 2
        self.n_registers = n_registers
        self.n_banks = n_banks
        self.scale = d_model ** -0.5

        total_reg_dim = n_banks * n_registers * self.d_reg_real
        self._total_reg_dim = ((total_reg_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._total_reg_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        meta_banks: list[list[mx.array]],
        residual: mx.array,
    ) -> mx.array:
        B, L, D = residual.shape

        q_input = _flatten_banks(meta_banks)
        if q_input.shape[0] < self._total_reg_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._total_reg_dim - q_input.shape[0],))
            ])

        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale
        attn_weights = mx.softmax(attn, axis=-1)
        attn_weights = self.dropout(attn_weights)

        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        out = self.out_proj(summary)                            # (B, d_model)
        out = mx.broadcast_to(out[:, None, :], residual.shape)
        return residual + out


# ══════════════════════════════════════════════════════════════════════
# MetaS3 — Cross-level contribution gates
# ══════════════════════════════════════════════════════════════════════


class MetaS3Ternary(nn.Module):
    """Top-level per-pass contribution gates from register banks.

    Fixed from original: temperature scaling + learned bias initialized
    to -2.0 (sigmoid(-2) ≈ 0.12) so gates start near-closed and must
    learn to open. Without this, gates start at 1.0 and never differentiate.
    """

    def __init__(self, d_register: int, n_registers: int, n_banks: int, n_passes: int):
        super().__init__()
        self.n_passes = n_passes
        d_reg_real = d_register * 2
        input_dim = n_banks * n_registers * d_reg_real
        self.gate_proj = nn.Linear(input_dim, n_passes)
        # Initialize bias to -2.0 so sigmoid starts near 0.12, not 0.5
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(self, all_banks: list[list[mx.array]]) -> mx.array:
        flat = _flatten_banks(all_banks)
        logits = self.gate_proj(flat)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    d_register = 128
    d_reg_real = d_register * 2
    n_registers = 3

    def _fresh_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    def _init_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    print("Testing S4Ternary...")
    s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
    banks = [_init_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    updates, attn = s4(banks, residual)
    mx.eval(*updates, attn)
    assert len(updates) == 3
    assert updates[0].shape == (d_reg_real,)
    print(f"  S4: {len(updates)} updates, shape {updates[0].shape} ✓")

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, d_register, n_phases=3, n_registers=n_registers)
    regs = _fresh_bank()
    delta = mx.random.normal((1, 32, d_model))
    gated, new_regs, gate, wgv = s3.gate_phase(regs, delta, phase_idx=0)
    mx.eval(gated, *new_regs, gate)
    assert gated.shape == (1, 32, d_model)
    assert len(new_regs) == 3
    print(f"  S3: gate={gate.item():.3f}, gated_delta shape {gated.shape} ✓")

    print("Testing MetaS4Ternary...")
    meta_s4 = MetaS4Ternary(d_model, d_register, n_registers=n_registers, n_banks=4)
    meta_banks = [_init_bank(), _fresh_bank(), _fresh_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    out = meta_s4(meta_banks, residual)
    mx.eval(out)
    assert out.shape == (1, 32, d_model)
    print(f"  MetaS4: {residual.shape} → {out.shape} ✓")

    print("Testing MetaS3Ternary...")
    meta_s3 = MetaS3Ternary(d_register, n_registers=n_registers, n_banks=6, n_passes=5)
    all_banks = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    gates = meta_s3(all_banks)
    mx.eval(gates)
    assert gates.shape == (5,)
    # Verify gates start near-closed (bias=-2.0 → sigmoid ≈ 0.12), not at 1.0
    for g in gates.tolist():
        assert g < 0.5, f"Meta-S3 gate should start near-closed, got {g:.3f}"
    print(f"  MetaS3: gates shape {gates.shape}, values {[f'{g:.3f}' for g in gates.tolist()]} ✓ (near-closed)")

    # Test gradient flow
    print("Testing gradient flow through S4...")
    import mlx.nn as nn
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
            self.param = mx.zeros((d_reg_real,))
        def __call__(self, x):
            bank = [[self.param] * n_registers]
            target = _fresh_bank()
            updates, _ = self.s4(bank, x)
            return mx.sum(updates[0])

    tm = TestModel()
    mx.eval(tm.parameters())
    def test_loss(tm, x):
        return tm(x)
    gfn = nn.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)
    print(f"  S4 gradient flow OK: loss={lv.item():.4f} ✓")

    print("components.py self-test: all ok ✓")
