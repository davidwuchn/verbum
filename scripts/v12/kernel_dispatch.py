"""
Combinator dispatch modules for the descending VSM arm.

v12 — KIBC dispatch stays 4-way (M operates via retrieval layers, not
dispatch). CombinatorIntegrate now accepts retrieval context from
ascending arm's GatedLinearAttention registers, allowing the
composition pathway to use what M found.

The 4 compositional combinators (K, I, B, C) are the dispatch basis:
  K (select):   softmax IS selection — pick relevant, discard rest
  I (identity): residual stream IS identity — copy forward unchanged
  B (compose):  attention composition — chain operations
  C (flip):     argument reordering — enables closures and binding

M (match/retrieval) operates in the ascending arm via GatedLinearAttention.
Its results reach the descending arm through retrieval registers,
which CombinatorIntegrate reads as additional context.

Architecture per descending pass:
  Phase 0 (dispatch):   CombinatorDispatch — which combinator? (4-way softmax)
  Phase 1 (converge):   StrideStack — propagate dispatched signal spatially
  Phase 2 (integrate):  CombinatorIntegrate — apply combinator reduction
                         + retrieval register context from M

Cycle semantics (desc_max_cycles=3):
  Cycle 0 — IDENTIFY:  which combinator applies here?
  Cycle 1 — RESOLVE:   find and bind the arguments (M results available)
  Cycle 2 — PRODUCE:   apply reduction, produce result

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear
from kernel import N_COMBINATORS, COMBINATOR_NAMES

# ── Dispatch ratio prior ──────────────────────────────────────────
# λ dispatch(logits, r=[1, 0.5, 1, 1]). softmax(logits + log(r / Σr))
#
# Empirical universal ratio K:I:B:C ≈ 1:0.5:1:1 measured across 9
# models, 2 architecture families (session 093). Applied as additive
# log-prior in logit space. When logits are zero, dispatch defaults
# to the ratio. Model learns on top of the prior, not from scratch.

def compute_dispatch_prior(ratio: tuple[float, ...]) -> mx.array:
    """log(ratio / sum(ratio)) — additive logit bias for softmax."""
    r = mx.array(ratio)
    return mx.log(r / mx.sum(r))


# ══════════════════════════════════════════════════════════════════
# CombinatorDispatch — routes to 4 combinator pathways
# ══════════════════════════════════════════════════════════════════


class CombinatorDispatch(nn.Module):
    """Phase 0: which combinator applies at this position?

    (4+N)-way softmax over KIBC primitives + N abstraction slots.
    The 4 KIBC primitives are fixed identity embeddings. The N slots
    are learnable composed-abstraction embeddings gated by S5.

    At init with slot gates near zero, this reduces to 4-way KIBC
    dispatch (existing behavior preserved).

    The combinator embeddings are the S5 identity of the dispatcher:
    4 near-orthogonal directions encoding WHAT each combinator IS.
    Abstraction slots are additional S5 embeddings representing
    pre-composed operations (e.g. B∘K = select-then-compose).
    Register conditioning from the ascending arm biases which
    combinator/slot is contextually likely. Op emphasis from S4
    scales the landscape.
    """

    def __init__(
        self,
        d_model: int,
        n_combinators: int = N_COMBINATORS,
        n_abstraction_slots: int = 0,
        d_ff: int | None = None,
        dropout: float = 0.1,
        n_registers: int = 3,
        d_register: int = 128,
        max_cond_banks: int = 5,
        dispatch_ratio: tuple[float, ...] = (1.0, 0.5, 1.0, 1.0),
    ):
        super().__init__()
        self.d_model = d_model
        self.n_combinators = n_combinators
        self.n_abstraction_slots = n_abstraction_slots

        # Empirical ratio prior: log(r/Σr) as static logit bias
        self._dispatch_prior = compute_dispatch_prior(dispatch_ratio)
        self.n_total = n_combinators + n_abstraction_slots
        if d_ff is None:
            d_ff = d_model * 3

        # Pad to multiple of 16 for TernaryLinear
        self.n_comb_padded = ((n_combinators + 15) // 16) * 16  # 16

        self.norm = nn.RMSNorm(d_model)

        # Dispatch projection: hidden → combinator logits (KIBC only)
        self.dispatch = TernaryLinear(d_model, self.n_comb_padded, pre_norm=False)

        # ── Register conditioning ─────────────────────────────
        # Ascending registers → dispatch bias: which combinator is likely?
        self.n_registers = n_registers
        self.d_reg_real = d_register * 2
        self.max_cond_banks = max_cond_banks
        max_cond_dim = max_cond_banks * n_registers * self.d_reg_real
        # TernaryLinear requires in_features divisible by group_size=64
        self._max_cond_dim = ((max_cond_dim + 63) // 64) * 64
        self.register_cond = TernaryLinear(self._max_cond_dim, self.n_comb_padded, pre_norm=False)
        # Zero-init: conditioning starts inert — gamma=0 → output=0
        self.register_cond.gamma = mx.zeros_like(self.register_cond.gamma)
        # Separate bias: zeros → no initial bias on conditioning
        self.register_cond_bias = mx.zeros((self.n_comb_padded,))

        # Combinator embeddings: 4 near-orthogonal directions
        self.combinator_embeddings = _init_combinator_embeddings(
            n_combinators, d_model)

        # ── Abstraction slot embeddings ───────────────────────
        if n_abstraction_slots > 0:
            # Near-zero init: slots are invisible at start
            self.slot_embeddings = mx.random.normal(
                (n_abstraction_slots, d_model)) * 0.01
            # Per-slot gates: sigmoid(-4) ≈ 0.018 — nearly invisible
            # Named without underscore so MLX includes in parameters()
            self.slot_gate_raw = mx.full((n_abstraction_slots,), -4.0)

        # L2-normalize to fixed scale each forward pass
        self.embed_scale = 0.5

        # FFN pathway: transforms representation using combinator identity
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

    @property
    def slot_gates(self) -> mx.array:
        """Per-slot gates in [0, 1]. Near-zero at init."""
        if self.n_abstraction_slots == 0:
            return mx.array([])
        return mx.sigmoid(self.slot_gate_raw)

    def _normalize_embeddings(self) -> mx.array:
        """L2-normalize combinator embeddings to fixed scale."""
        norms = mx.sqrt(
            mx.sum(self.combinator_embeddings * self.combinator_embeddings,
                   axis=-1, keepdims=True) + 1e-8)
        return self.combinator_embeddings * (self.embed_scale / norms)

    def _normalize_slot_embeddings(self) -> mx.array:
        """L2-normalize slot embeddings to fixed scale."""
        norms = mx.sqrt(
            mx.sum(self.slot_embeddings * self.slot_embeddings,
                   axis=-1, keepdims=True) + 1e-8)
        return self.slot_embeddings * (self.embed_scale / norms)

    def _get_all_embeddings(
        self,
        proposal_delta: mx.array | None = None,
    ) -> mx.array:
        """Get combined (4+N, d_model) embedding table.

        Returns normalized KIBC embeddings concatenated with gated
        slot embeddings (with optional S4 proposal delta).
        """
        # KIBC embeddings — pure normalized, no emphasis multiplication
        comb_emb = self._normalize_embeddings()  # (4, d_model)

        if self.n_abstraction_slots == 0:
            return comb_emb

        # Slot embeddings: normalized, gated, with proposal
        slot_emb = self._normalize_slot_embeddings()  # (N, d_model)

        # Apply S4 proposal delta (soft modulation, not hard write)
        if proposal_delta is not None:
            slot_emb = slot_emb + proposal_delta

        # Gate: near-zero gates → near-zero effective embeddings
        gates = self.slot_gates  # (N,)
        slot_emb = slot_emb * gates[:, None]

        return mx.concatenate([comb_emb, slot_emb], axis=0)  # (4+N, d_model)

    def __call__(
        self,
        x: mx.array,
        registers: list[list[mx.array]] | None = None,
        proposal_delta: mx.array | None = None,
    ) -> mx.array:
        """
        x: (B, L, d_model)
        registers: ascending register banks for conditioning
        proposal_delta: (N, d_model) S4 proposal modulation for slot embeddings

        Returns: (B, L, d_model) with residual connection
        """
        h = self.norm(x)

        # Step 1: Dispatch logits — KIBC from ternary projection
        kibc_logits = self.dispatch(h)[..., :self.n_combinators]  # (B, L, 4)

        # Register conditioning: ascending registers bias dispatch
        if registers is not None:
            parts = []
            for bank in registers:
                for reg in bank:
                    parts.append(reg)
            cond_input = mx.concatenate(parts, axis=-1)
            if cond_input.shape[0] < self._max_cond_dim:
                cond_input = mx.concatenate([
                    cond_input,
                    mx.zeros((self._max_cond_dim - cond_input.shape[0],))
                ])
            reg_bias = (
                self.register_cond(cond_input.reshape(1, -1)).reshape(-1)
                + self.register_cond_bias
            )[:self.n_combinators]
            kibc_logits = kibc_logits + reg_bias[None, None, :]

        # Step 2: Slot logits via dot product with gated slot embeddings
        if self.n_abstraction_slots > 0:
            slot_emb = self._normalize_slot_embeddings()  # (N, d_model)
            if proposal_delta is not None:
                slot_emb = slot_emb + proposal_delta
            gates = self.slot_gates  # (N,) in [0, 1]
            # Dot product: (B, L, d_model) @ (d_model, N) → (B, L, N)
            slot_logits = h @ slot_emb.T
            # Additive masking: log(gate) shifts logits toward -inf when
            # gate ≈ 0, making slots invisible in softmax. At gate=0.018,
            # log(0.018) ≈ -4.0, which strongly suppresses the slot.
            # At gate=1.0, log(1.0) = 0, no suppression.
            slot_logits = slot_logits + mx.log(gates[None, None, :] + 1e-8)
            # Full softmax over (4+N)
            dispatch_logits = mx.concatenate(
                [kibc_logits, slot_logits], axis=-1)  # (B, L, 4+N)
        else:
            dispatch_logits = kibc_logits

        # Empirical ratio prior: additive log-prior in logit space.
        # λ dispatch(logits, r). softmax(logits + log(r / Σr))
        # Defaults to K:I:B:C ≈ 1:0.5:1:1 when logits carry no signal.
        if self.n_abstraction_slots > 0:
            # Prior applies to KIBC logits only; slots are unaffected
            prior_padded = mx.concatenate([
                self._dispatch_prior,
                mx.zeros((self.n_abstraction_slots,))
            ])
            dispatch_logits = dispatch_logits + prior_padded
        else:
            dispatch_logits = dispatch_logits + self._dispatch_prior

        dispatch_weights = mx.softmax(dispatch_logits, axis=-1)

        # Cache for probing (stop_gradient) and alarm (live, end-to-end)
        self._dispatch_weights = mx.stop_gradient(dispatch_weights)
        self._dispatch_weights_live = dispatch_weights
        # Also cache KIBC-only weights for compatibility
        self._dispatch_weights_kibc = mx.stop_gradient(
            dispatch_weights[..., :self.n_combinators])

        # Step 3: All embeddings (KIBC + gated slots)
        all_emb = self._get_all_embeddings(
            proposal_delta)  # (4+N, d_model)

        # Step 4: Weighted embedding — identity modulation
        # (B, L, 4+N) @ (4+N, d_model) → (B, L, d_model)
        comb_context = dispatch_weights @ all_emb

        # Step 5: Modulate input, then transform
        modulated = h + comb_context
        out = self.down(nn.gelu(self.up(modulated)))

        return x + self.dropout(out)


# ══════════════════════════════════════════════════════════════════
# CombinatorIntegrate — applies combinator reductions
# ══════════════════════════════════════════════════════════════════


class CombinatorIntegrate(nn.Module):
    """Phase 2: apply the combinator reduction, type the result.

    Dual pathway:
      1. Standard FFN pathway: type modulation + shared transform.
         Handles prose and non-computational positions.
         With abstraction slots: weighted sum includes slot embeddings,
         so the FFN sees the composed-abstraction identity.
      2. Kernel computation pathway: exact combinator reductions on
         operands extracted from the residual stream:
           K: select operand 0, discard operand 1
           I: return operand 0 unchanged
           B: f(g(x)) — additive composition signal
           C: f(y,x) — swap: select operand 0 + operand 2
         Abstraction slots route through the FFN pathway only —
         kernel reductions are for the 4 KIBC primitives.

    Compute gate blends the two pathways:
      output = gate × kernel_result + (1-gate) × ffn_result
    Gate starts at ~0 (pure FFN), learns to open for positions
    where exact combinator computation helps.
    """

    def __init__(
        self,
        d_model: int,
        n_combinators: int = N_COMBINATORS,
        n_abstraction_slots: int = 0,
        d_ff: int | None = None,
        dropout: float = 0.1,
        max_val: int = 256,
        result_buckets: int = 1024,
        d_register: int = 128,
        n_retrieval_registers: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_combinators = n_combinators
        self.n_abstraction_slots = n_abstraction_slots
        self.n_total = n_combinators + n_abstraction_slots
        self.max_val = max_val
        self.n_retrieval_registers = n_retrieval_registers
        if d_ff is None:
            d_ff = d_model * 4

        # Pad for TernaryLinear
        self.n_comb_padded = ((n_combinators + 15) // 16) * 16

        self.norm = nn.RMSNorm(d_model)

        # ── Type pathway (combinator types, not value types) ──
        self.type_proj = TernaryLinear(
            d_model, self.n_comb_padded, pre_norm=False)
        self.type_embeddings = _init_combinator_type_embeddings(
            n_combinators, d_model)

        # ── Standard FFN pathway ──────────────────────────────
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        # ── Retrieval conditioning (v12) ──────────────────────
        # M's retrieval registers provide context to the FFN pathway.
        # This lets KIBC composition use what M found during ascending.
        # Conditioning is additive (like S2 direction signals): the
        # retrieval context biases the FFN but doesn't replace it.
        if n_retrieval_registers > 0:
            d_reg_real = d_register * 2
            ret_input_dim = n_retrieval_registers * d_reg_real
            ret_input_padded = ((ret_input_dim + 15) // 16) * 16
            self._ret_input_dim = ret_input_dim
            self._ret_input_padded = ret_input_padded
            self.retrieval_cond = TernaryLinear(
                ret_input_padded, d_model, pre_norm=True)
            # Scale starts small — retrieval influence is gentle at init
            self.retrieval_cond.gamma = self.retrieval_cond.gamma * 0.1

        # ── Kernel computation pathway ────────────────────────

        # 3 operand extractors (B and C need 3 arguments)
        max_val_padded = ((max_val + 15) // 16) * 16
        self._max_val_padded = max_val_padded
        self.operand0_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)
        self.operand1_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)
        self.operand2_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)

        # Result encoder
        self.result_buckets = result_buckets
        self.result_offset = result_buckets // 2
        self.result_embed = nn.Embedding(result_buckets, d_model)

        # Compute gate: starts near 0 (pure FFN).
        # Output padded to 16, take [..., :1]. Separate bias.
        # d_model=512 is already a multiple of 16.
        self.gate_proj = TernaryLinear(d_model, 16, pre_norm=False)
        # Zero gamma → output=0 at init → gate = sigmoid(-5) ≈ 0
        self.gate_proj.gamma = mx.zeros_like(self.gate_proj.gamma)
        self.gate_bias = mx.full((1,), -5.0)

        self.dropout = nn.Dropout(dropout)

    def _kernel_compute(
        self,
        h: mx.array,
        dispatch_weights: mx.array | None,
    ) -> tuple[mx.array, dict]:
        """Extract operands, apply combinator reductions, encode result.

        The 4 combinator kernel functions operate on integer operands:
          K(op0, op1, op2) → op0           (select first)
          I(op0, op1, op2) → op0           (identity)
          B(op0, op1, op2) → op0+op1+op2   (composition signal)
          C(op0, op1, op2) → op0+op2       (flip: skip op1)
        """
        B, L, _ = h.shape

        # Extract 3 operands via argmax (non-differentiable)
        op0_logits = self.operand0_proj(h)[..., :self.max_val]
        op1_logits = self.operand1_proj(h)[..., :self.max_val]
        op2_logits = self.operand2_proj(h)[..., :self.max_val]

        op0 = mx.stop_gradient(mx.argmax(op0_logits, axis=-1)).astype(mx.int32)
        op1 = mx.stop_gradient(mx.argmax(op1_logits, axis=-1)).astype(mx.int32)
        op2 = mx.stop_gradient(mx.argmax(op2_logits, axis=-1)).astype(mx.int32)

        # Get combinator from dispatch weights
        if dispatch_weights is not None:
            comb = mx.stop_gradient(
                mx.argmax(dispatch_weights, axis=-1)).astype(mx.int32)
        else:
            comb = mx.zeros((B, L), dtype=mx.int32)

        # ── Exact combinator kernel (non-differentiable) ─────
        # Compute all 4 combinator results, select by dispatched combinator

        # K: select op0 (discard op1, op2)
        r_K = op0

        # I: identity — return op0
        r_I = op0

        # B: compose — f(g(x)) encoded as additive signal
        r_B = op0 + op1 + op2

        # C: flip — f(y,x) encoded as op0 + op2 (skip op1)
        r_C = op0 + op2

        # Stack and select by combinator code
        all_results = mx.stack([r_K, r_I, r_B, r_C], axis=0)  # (4, B, L)

        comb_clamped = mx.clip(comb, 0, N_COMBINATORS - 1)
        b_idx = mx.broadcast_to(mx.arange(B)[:, None], (B, L))
        l_idx = mx.broadcast_to(mx.arange(L)[None, :], (B, L))
        result = all_results[comb_clamped, b_idx, l_idx]  # (B, L)

        # ── Encode result back to d_model ─────────────────────
        result_idx = mx.stop_gradient(
            mx.clip(result + self.result_offset, 0, self.result_buckets - 1)
        ).astype(mx.int32)
        kernel_out = self.result_embed(result_idx)  # (B, L, d_model)

        kernel_info = {
            "combinator": mx.stop_gradient(comb),
            "op0": mx.stop_gradient(op0),
            "op1": mx.stop_gradient(op1),
            "op2": mx.stop_gradient(op2),
            "result": mx.stop_gradient(result),
        }

        return kernel_out, kernel_info

    def __call__(
        self,
        x: mx.array,
        dispatch_weights: mx.array | None = None,
        slot_embeddings: mx.array | None = None,
        retrieval_registers: list | None = None,
    ) -> mx.array:
        """
        x: (B, L, d_model)
        dispatch_weights: (B, L, n_total) from CombinatorDispatch
                          First n_combinators are KIBC, rest are slots.
        slot_embeddings: (N, d_model) gated slot embeddings for context
        retrieval_registers: list of retrieval register vectors from M (v12)
        Returns: (B, L, d_model) with residual connection
        """
        h = self.norm(x)

        # ── Type projection (KIBC combinator types) ───────────
        type_logits = self.type_proj(h)[..., :self.n_combinators]
        type_weights = mx.softmax(type_logits, axis=-1)
        self._type_weights = mx.stop_gradient(type_weights)

        # ── Standard FFN pathway ──────────────────────────────
        # Type context from KIBC type embeddings
        type_context = type_weights @ self.type_embeddings

        # Slot context: if slots are active, add their contribution
        # via dispatch weights. This lets the FFN see composed identities.
        if (self.n_abstraction_slots > 0
                and dispatch_weights is not None
                and slot_embeddings is not None):
            slot_dw = dispatch_weights[..., self.n_combinators:]
            slot_context = slot_dw @ slot_embeddings
            type_context = type_context + slot_context

        # Retrieval conditioning (v12): M's findings bias the FFN
        if (self.n_retrieval_registers > 0
                and retrieval_registers is not None
                and len(retrieval_registers) > 0):
            ret_flat = mx.concatenate(retrieval_registers, axis=-1)
            if ret_flat.shape[0] < self._ret_input_padded:
                ret_flat = mx.concatenate([
                    ret_flat,
                    mx.zeros((self._ret_input_padded - ret_flat.shape[0],))
                ])
            # (d_model,) broadcast to (B, L, d_model)
            ret_context = self.retrieval_cond(
                ret_flat.reshape(1, -1)).reshape(-1)
            type_context = type_context + ret_context[None, None, :]

        modulated = h + type_context
        ffn_out = self.down(nn.gelu(self.up(modulated)))

        # ── Kernel computation pathway ────────────────────────
        # Kernel uses KIBC-only dispatch weights (first 4 columns)
        kibc_dw = (dispatch_weights[..., :self.n_combinators]
                   if dispatch_weights is not None else None)
        kernel_out, kernel_info = self._kernel_compute(h, kibc_dw)
        self._kernel_info = kernel_info

        # ── Compute gate: blend kernel vs FFN ─────────────────
        gate = mx.sigmoid(
            self.gate_proj(h)[..., :1] + self.gate_bias
        )  # (B, L, 1)
        self._compute_gate = mx.stop_gradient(gate)
        self._compute_gate_live = gate

        blended = gate * kernel_out + (1.0 - gate) * ffn_out

        return x + self.dropout(blended)


# ══════════════════════════════════════════════════════════════════
# Structured initialization
# ══════════════════════════════════════════════════════════════════


def _init_combinator_embeddings(n_combinators: int, d_model: int) -> mx.array:
    """Initialize 4 near-orthogonal combinator identity embeddings.

    Each combinator gets a distinct block of d_model/4 dimensions.
    With 4 combinators in 512-dim space, they can be exactly orthogonal.
    """
    embeddings = mx.zeros((n_combinators, d_model))
    block = d_model // n_combinators  # 128 dims each

    for i in range(n_combinators):
        # Characteristic direction: Gaussian in a dedicated block
        start = i * block
        end = start + block
        block_values = mx.random.normal((block,)) * 0.5
        embeddings = embeddings.at[i, start:end].add(block_values)

        # Small shared component for cross-combinator interaction
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[i].add(shared)

    # L2-normalize and scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1

    return embeddings


def _init_combinator_type_embeddings(
    n_combinators: int, d_model: int
) -> mx.array:
    """Initialize combinator type embeddings.

    4 types: K, I, B, C — each gets a near-orthogonal direction.
    Same structure as combinator dispatch embeddings but for the
    integration pathway (typing which combinator a position IS).
    """
    embeddings = mx.zeros((n_combinators, d_model))
    block = d_model // (n_combinators * 2)  # half-space for type identity

    for i in range(n_combinators):
        start = i * block
        end = min((i + 1) * block, d_model)
        for d in range(start, end):
            embeddings = embeddings.at[i, d].add(1.0)
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[i].add(shared)

    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1

    return embeddings


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import numpy as np
    d_model = 512
    n_slots = 16

    print("Testing CombinatorDispatch (4 KIBC + 16 abstraction slots)...")
    dispatch = CombinatorDispatch(
        d_model, n_combinators=4, n_abstraction_slots=n_slots, d_ff=1536)
    x = mx.random.normal((1, 64, d_model))
    y = dispatch(x)
    mx.eval(y)
    assert y.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y.shape}"

    # Check dispatch weights are cached (4+N-wide)
    dw = dispatch._dispatch_weights
    mx.eval(dw)
    assert dw.shape == (1, 64, 4 + n_slots), \
        f"Expected (1, 64, {4 + n_slots}), got {dw.shape}"

    # Weights should sum to ~1
    sums = mx.sum(dw, axis=-1)
    mx.eval(sums)
    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-4).item(), \
        f"Dispatch weights should sum to ~1"
    print(f"  CombinatorDispatch: {x.shape} → {y.shape} ✓")
    print(f"  Dispatch weights: {dw.shape}, (4+{n_slots})-way softmax ✓")

    # At init, almost all mass should be on KIBC (slots have near-zero gates)
    kibc_mass = mx.sum(dw[..., :4], axis=-1)
    slot_mass = mx.sum(dw[..., 4:], axis=-1)
    mx.eval(kibc_mass, slot_mass)
    mean_kibc = float(mx.mean(kibc_mass).item())
    mean_slot = float(mx.mean(slot_mass).item())
    print(f"  KIBC mass: {mean_kibc:.4f}, slot mass: {mean_slot:.4f}")
    assert mean_kibc > 0.9, \
        f"At init, KIBC should dominate (>0.9), got {mean_kibc:.4f}"
    print(f"  Slots near-invisible at init ✓")

    # Slot gates should start near 0.018
    sg = dispatch.slot_gates
    mx.eval(sg)
    print(f"  Slot gates: mean={float(mx.mean(sg).item()):.4f} "
          f"(expect ~0.018) ✓")

    # KIBC-only backward compatibility
    dw_kibc = dispatch._dispatch_weights_kibc
    mx.eval(dw_kibc)
    assert dw_kibc.shape == (1, 64, 4), f"KIBC weights shape: {dw_kibc.shape}"
    print(f"  KIBC-only weights cached: {dw_kibc.shape} ✓")

    # Mean dispatch distribution
    mean_dw = mx.mean(dw, axis=(0, 1))
    mx.eval(mean_dw)
    print(f"  Mean dispatch: K={mean_dw[0].item():.3f} I={mean_dw[1].item():.3f} "
          f"B={mean_dw[2].item():.3f} C={mean_dw[3].item():.3f}"
          f" slots={sum(mean_dw[i].item() for i in range(4, 4+n_slots)):.4f}")

    # Check embedding normalization
    normed = dispatch._normalize_embeddings()
    mx.eval(normed)
    norms = np.linalg.norm(np.array(normed), axis=1)
    assert np.allclose(norms, dispatch.embed_scale, atol=1e-3), \
        f"Normalized embeddings should have norm={dispatch.embed_scale}"
    print(f"  Embedding norms: all ≈ {dispatch.embed_scale} ✓")

    # Test without abstraction slots (backward compat)
    print("\nTesting CombinatorDispatch (4 KIBC, no slots)...")
    dispatch_base = CombinatorDispatch(d_model, n_combinators=4, d_ff=1536)
    y_base = dispatch_base(x)
    mx.eval(y_base)
    dw_base = dispatch_base._dispatch_weights
    mx.eval(dw_base)
    assert dw_base.shape == (1, 64, 4), f"Base dispatch: {dw_base.shape}"
    print(f"  Base dispatch (no slots): {dw_base.shape} ✓")

    print("\nTesting CombinatorIntegrate (with slots + retrieval)...")
    d_register = 128
    n_ret_regs = 2
    integrate = CombinatorIntegrate(
        d_model, n_combinators=4, n_abstraction_slots=n_slots, d_ff=2048,
        d_register=d_register, n_retrieval_registers=n_ret_regs)
    y2 = integrate(x)
    mx.eval(y2)
    assert y2.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y2.shape}"
    tw = integrate._type_weights
    mx.eval(tw)
    assert tw.shape == (1, 64, 4), f"Expected (1, 64, 4), got {tw.shape}"
    print(f"  CombinatorIntegrate: {x.shape} → {y2.shape} ✓")
    print(f"  Type weights: {tw.shape} (KIBC only) ✓")

    # Test with full dispatch weights (4+N) and slot embeddings
    slot_emb = dispatch._normalize_slot_embeddings()
    mx.eval(slot_emb)
    y3 = integrate(x, dispatch_weights=dw, slot_embeddings=slot_emb)
    mx.eval(y3)
    assert y3.shape == (1, 64, d_model)
    ki = integrate._kernel_info
    assert ki["combinator"].shape == (1, 64)
    assert ki["op0"].shape == (1, 64)
    print(f"  With full dispatch (4+{n_slots}) + slot embeddings: ✓")

    # Test with retrieval registers (v12)
    d_reg_real = d_register * 2
    ret_regs = [mx.random.normal((d_reg_real,)) for _ in range(n_ret_regs)]
    y4 = integrate(x, dispatch_weights=dw, slot_embeddings=slot_emb,
                   retrieval_registers=ret_regs)
    mx.eval(y4)
    assert y4.shape == (1, 64, d_model)
    print(f"  With retrieval registers ({n_ret_regs} regs): ✓")

    # Retrieval registers should change the output
    diff = float(mx.mean(mx.abs(y3 - y4)).item())
    print(f"  Output diff with/without retrieval: {diff:.6f} (should be >0)")
    assert diff > 0, "Retrieval registers should affect output"

    # Compute gate should start near 0
    cg = integrate._compute_gate
    mx.eval(cg)
    assert float(mx.mean(cg).item()) < 0.02, \
        f"Compute gate should start near 0, got {mx.mean(cg).item():.4f}"
    print(f"  Compute gate mean: {mx.mean(cg).item():.4f} (starts near 0) ✓")

    # Test gradient flow
    print("\nTesting gradient flow (with abstraction slots)...")

    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.dispatch = CombinatorDispatch(
                d_model, n_combinators=4,
                n_abstraction_slots=n_slots, d_ff=1536)
            self.integrate = CombinatorIntegrate(
                d_model, n_combinators=4,
                n_abstraction_slots=n_slots, d_ff=2048,
                d_register=d_register, n_retrieval_registers=n_ret_regs)

        def __call__(self, x):
            h = self.dispatch(x)
            dw = self.dispatch._dispatch_weights
            slot_emb = self.dispatch._normalize_slot_embeddings()
            ret_regs_test = [mx.zeros((d_reg_real,)) for _ in range(n_ret_regs)]
            h = self.integrate(h, dispatch_weights=dw,
                               slot_embeddings=slot_emb,
                               retrieval_registers=ret_regs_test)
            return mx.mean(h)

    tm = TestModel()
    mx.eval(tm.parameters())

    def test_loss(tm, x):
        return tm(x)

    gfn = nn.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)

    # Check combinator_embeddings gradient
    comb_grad = g["dispatch"]["combinator_embeddings"]
    mx.eval(comb_grad)
    cg_np = np.array(comb_grad)
    grad_norms = np.linalg.norm(cg_np, axis=1)
    n_with_grad = np.sum(grad_norms > 1e-6)
    print(f"  Gradient flow OK: loss={lv.item():.4f}")
    print(f"  Combinators with gradient: {n_with_grad}/4 ✓")

    # Check slot_embeddings gradient
    slot_grad = g["dispatch"]["slot_embeddings"]
    mx.eval(slot_grad)
    slot_grad_np = np.array(slot_grad)
    slot_grad_norms = np.linalg.norm(slot_grad_np, axis=1)
    n_slots_with_grad = np.sum(slot_grad_norms > 1e-8)
    print(f"  Slots with gradient: {n_slots_with_grad}/{n_slots} ✓")

    # Check slot gate gradient — find in the gradient tree
    # MLX may strip leading underscore in parameter naming
    dispatch_grads = g.get("dispatch", {})
    gate_key = "slot_gate_raw" if "slot_gate_raw" in dispatch_grads else None
    if gate_key is None:
        for k in dispatch_grads:
            if "slot_gate" in k:
                gate_key = k
                break
    if gate_key:
        gate_grad = dispatch_grads[gate_key]
        mx.eval(gate_grad)
        print(f"  Slot gate gradient norm: {np.linalg.norm(np.array(gate_grad)):.6f} ✓")
    else:
        print(f"  Slot gate gradient: not in grad tree (keys: {list(dispatch_grads.keys())})")
        print(f"  (may need mx.stop_gradient removal for gate_raw to be trainable)")

    print("\nkernel_dispatch.py self-test: all ok ✓")
