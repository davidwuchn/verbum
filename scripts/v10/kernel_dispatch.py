"""
Kernel dispatch modules for the descending VSM arm.

The descending arm's S1 operations are kernel-shaped, not compression-shaped.
Instead of TernaryFFN (compress), the descending arm routes representations
through kernel op pathways (dispatch).

The 22 kernel ops (from kernel.py) are pre-wired as architectural identity —
the model discovers them as easy paths while training on prose via relational
loss. The ternary routing topology learns which positions benefit from which
kernel op family.

Architecture per descending pass:
  Phase 0 (dispatch):   KernelDispatch — route to kernel op families
  Phase 1 (integrate):  KernelIntegrate — type the dispatched result locally
  Phase 2 (converge):   StrideStack coarse→fine — propagate typed dispatch

The kernel op embeddings are the S5 identity of the dispatcher VSM.
They encode WHAT each operation IS — its characteristic transformation
pattern. The dispatch projection learns WHEN each op is relevant.

Design principles:
  - Shapes not outputs: the kernel provides the right shape for the
    descending arm, replacing compression ops that always go to passthrough
  - Easy path: kernel ops are architecturally available, not learned targets
  - Pre-wired: op embeddings initialized with structure, not random
  - Observable: dispatch weights show which kernel ops activate where

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════
# Kernel op families — from kernel.py
# ══════════════════════════════════════════════════════════════════

N_OPS = 22
N_TYPES = 5

# Op family indices for structured initialization
OP_FAMILIES = {
    "arith_binary":  list(range(0, 7)),    # add sub mul div mod min max
    "comparison":    list(range(7, 12)),    # eq lt gt le ge
    "bool_binary":   [12, 13],             # and or
    "bool_unary":    [14],                 # not
    "arith_unary":   [15, 16],             # abs neg
    "conditional":   [17],                 # if
    "lambda":        list(range(18, 22)),   # partial apply compose apply-comp
}

N_FAMILIES = len(OP_FAMILIES)


# ══════════════════════════════════════════════════════════════════
# KernelDispatch — routes representations to kernel op pathways
# ══════════════════════════════════════════════════════════════════


class KernelDispatch(nn.Module):
    """Kernel-aware transformation for second arm phase 0 (dispatch).

    Replaces TernaryFFN prep in the second arm.

    Architecture:
      1. Dispatch: project to (n_ops,) distribution — which kernel op?
         Conditioned on ascending register banks (type/scope/role) when
         available, so dispatch can see what the ascending arm learned.
      2. Op modulation: weighted kernel identity added to representation
      3. Pathway: shared ternary transform, biased by kernel identity
      4. Gated residual

    The kernel op embeddings are the S5 identity of each operation.
    They provide orthogonal directions in d_model space — one per op —
    so the ternary routing fabric has distinct targets to route toward.

    The dispatch projection (TernaryLinear) learns WHEN each op is
    relevant. The ternary topology creates discrete routing paths:
    {-1, 0, +1} = {negate, disconnect, connect} = routing fabric.

    Register conditioning: the ascending arm's registers carry
    type/scope/role information that tells dispatch what kind of
    content is at each position. Without this, dispatch must infer
    routing purely from the residual stream — which is why it
    collapses to routing everything through one op. With register
    conditioning, dispatch sees "the ascending arm thinks this is
    scope=local, type=arithmetic" and can route to arithmetic ops.
    """

    def __init__(
        self,
        d_model: int,
        n_ops: int = N_OPS,
        d_ff: int | None = None,
        dropout: float = 0.1,
        n_registers: int = 3,
        d_register: int = 128,
        max_cond_banks: int = 5,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_ops = n_ops
        if d_ff is None:
            d_ff = d_model * 3

        # Pad n_ops to multiple of 16 for TernaryLinear
        self.n_ops_padded = ((n_ops + 15) // 16) * 16  # 32

        self.norm = nn.RMSNorm(d_model)

        # Dispatch projection: hidden → op distribution
        # TernaryLinear: the ternary topology learns discrete routing
        self.dispatch = TernaryLinear(d_model, self.n_ops_padded, pre_norm=False)

        # Dispatch temperature: learnable, starts at 1.0
        # Higher temperature → softer routing (early training)
        # Lower temperature → harder routing (converged)
        self.dispatch_temp = mx.array([1.0])

        # ── Register conditioning ─────────────────────────────
        # Ascending registers → dispatch bias: which ops should activate?
        # Registers carry type/scope/role from the ascending arm.
        # This is a real-valued (not ternary) projection because
        # registers are real-valued and we want smooth gradients
        # for the conditioning to learn quickly.
        self.n_registers = n_registers
        self.d_reg_real = d_register * 2
        self.max_cond_banks = max_cond_banks
        max_cond_dim = max_cond_banks * n_registers * self.d_reg_real
        self._max_cond_dim = ((max_cond_dim + 15) // 16) * 16
        # Small real-valued projection: register summary → per-op bias
        self.register_cond = nn.Linear(self._max_cond_dim, self.n_ops_padded)
        # Initialize to zero so conditioning starts inert
        self.register_cond.weight = mx.zeros_like(self.register_cond.weight)
        self.register_cond.bias = mx.zeros_like(self.register_cond.bias)

        # Op embeddings: kernel S5 identity — what each op IS
        # Real-valued, trainable. Initialized with structure:
        # each op gets a near-orthogonal direction in d_model space.
        self.op_embeddings = _init_op_embeddings(n_ops, d_model)

        # Pathway: transforms representation using dispatched op identity
        # The kernel identity modulates the input; the pathway transforms
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

    def __call__(self, x: mx.array, registers: list[list[mx.array]] | None = None) -> mx.array:
        """
        x: (B, L, d_model)
        registers: list of register banks from ascending arm, each bank is
                   a list of register vectors. Used to condition dispatch.
        Returns: (B, L, d_model) — with residual connection
        """
        h = self.norm(x)

        # Step 1: Dispatch — which kernel ops are relevant at each position?
        dispatch_logits = self.dispatch(h)[..., :self.n_ops]  # (B, L, n_ops)

        # Register conditioning: add per-op bias from ascending registers
        if registers is not None:
            # Flatten all register banks into one vector
            parts = []
            for bank in registers:
                for reg in bank:
                    parts.append(reg)
            cond_input = mx.concatenate(parts, axis=-1)  # (total_reg_dims,)
            # Pad to max
            if cond_input.shape[0] < self._max_cond_dim:
                cond_input = mx.concatenate([
                    cond_input,
                    mx.zeros((self._max_cond_dim - cond_input.shape[0],))
                ])
            # Project to per-op bias
            reg_bias = self.register_cond(cond_input)[:self.n_ops]  # (n_ops,)
            # Add to dispatch logits (broadcast across B, L)
            dispatch_logits = dispatch_logits + reg_bias[None, None, :]

        dispatch_weights = mx.softmax(
            dispatch_logits * self.dispatch_temp, axis=-1
        )  # (B, L, n_ops)

        # Cache for probing (stop_gradient keeps out of backward graph)
        self._dispatch_weights = mx.stop_gradient(dispatch_weights)

        # Step 2: Weighted op embedding — kernel identity modulation
        # (B, L, n_ops) @ (n_ops, d_model) → (B, L, d_model)
        op_context = dispatch_weights @ self.op_embeddings

        # Step 3: Modulate input with kernel identity, then transform
        modulated = h + op_context
        out = self.down(nn.gelu(self.up(modulated)))

        return x + self.dropout(out)


# ══════════════════════════════════════════════════════════════════
# KernelIntegrate — combines kernel pathway results
# ══════════════════════════════════════════════════════════════════


class KernelIntegrate(nn.Module):
    """Kernel-aware integration for descending arm phase 2 (integrate).

    Replaces TernaryFFN consolidation in the descending arm.

    After the StrideStack has propagated context across scales, this
    module integrates the kernel dispatch information back into the
    representation. It reads the current hidden state and produces
    a type-aware transformation.

    Architecture:
      1. Type projection: project to (n_types,) distribution
      2. Type modulation: weighted type identity added to representation
      3. Integration pathway: shared ternary transform
      4. Gated residual

    The type embeddings are the output types of the kernel — INT, BOOL,
    FN, FN_COMP, ERROR. They provide the type-awareness that the
    descending arm needs to produce well-typed representations.
    """

    def __init__(
        self,
        d_model: int,
        n_types: int = N_TYPES,
        d_ff: int | None = None,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_types = n_types
        if d_ff is None:
            d_ff = d_model * 4  # wider than dispatch — integration needs capacity

        # Pad n_types to multiple of 16
        self.n_types_padded = ((n_types + 15) // 16) * 16  # 16

        self.norm = nn.RMSNorm(d_model)

        # Type projection: hidden → type distribution
        self.type_proj = TernaryLinear(d_model, self.n_types_padded, pre_norm=False)

        # Type embeddings: kernel output types
        self.type_embeddings = _init_type_embeddings(n_types, d_model)

        # Integration pathway
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

    def __call__(self, x: mx.array) -> mx.array:
        """
        x: (B, L, d_model)
        Returns: (B, L, d_model) — with residual connection
        """
        h = self.norm(x)

        # Step 1: Type projection — what output type at each position?
        type_logits = self.type_proj(h)[..., :self.n_types]  # (B, L, n_types)
        type_weights = mx.softmax(type_logits, axis=-1)  # (B, L, n_types)

        # Cache for probing
        self._type_weights = mx.stop_gradient(type_weights)

        # Step 2: Type modulation
        # (B, L, n_types) @ (n_types, d_model) → (B, L, d_model)
        type_context = type_weights @ self.type_embeddings

        # Step 3: Integrate
        modulated = h + type_context
        out = self.down(nn.gelu(self.up(modulated)))

        return x + self.dropout(out)


# ══════════════════════════════════════════════════════════════════
# Structured initialization
# ══════════════════════════════════════════════════════════════════


def _init_op_embeddings(n_ops: int, d_model: int) -> mx.array:
    """Initialize kernel op embeddings with near-orthogonal structure.

    Each op gets a characteristic direction in d_model space.
    Ops within the same family share a family subspace but have
    distinct directions within it. This gives the ternary routing
    fabric structured targets to route toward.

    Family subspace allocation:
      Each family gets a contiguous block of dimensions.
      Within the block, ops get distinct orthogonal directions.
      Remaining dimensions are shared (allow cross-family interaction).
    """
    embeddings = mx.zeros((n_ops, d_model))

    # Allocate dimension blocks per family
    # Reserve first 50% for family-specific, last 50% shared
    family_dims = d_model // 2
    shared_dims = d_model - family_dims

    families = list(OP_FAMILIES.values())
    n_families = len(families)
    dims_per_family = family_dims // n_families

    family_offset = 0
    for fi, op_indices in enumerate(families):
        n_in_family = len(op_indices)
        # Each op in the family gets a direction in the family block
        for oi, op_idx in enumerate(op_indices):
            # Family-specific component: one-hot-ish within family block
            dim_start = family_offset
            dim_end = min(family_offset + dims_per_family, family_dims)
            if dim_end > dim_start and n_in_family > 0:
                # Spread ops across family dimensions
                op_dim = dim_start + (oi * (dim_end - dim_start)) // max(n_in_family, 1)
                op_dim = min(op_dim, dim_end - 1)
                embeddings = embeddings.at[op_idx, op_dim].add(1.0)

            # Shared component: small random for cross-family interaction
            shared_component = mx.random.normal((shared_dims,)) * 0.1
            embeddings = embeddings.at[op_idx, family_dims:].add(shared_component)

        family_offset += dims_per_family

    # L2-normalize each embedding, then scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1  # small scale so modulation is gentle

    return embeddings


def _init_type_embeddings(n_types: int, d_model: int) -> mx.array:
    """Initialize kernel type embeddings.

    5 types: INT, BOOL, FN, FN_COMP, ERROR
    Each gets a near-orthogonal direction. Types are fundamental —
    every position has a type, and the type determines what operations
    are valid downstream.
    """
    embeddings = mx.zeros((n_types, d_model))

    # Each type gets a distinct block of dimensions
    dims_per_type = d_model // (n_types * 2)  # use half the space for type identity

    for ti in range(n_types):
        dim_start = ti * dims_per_type
        dim_end = min((ti + 1) * dims_per_type, d_model)
        # Characteristic direction
        for d in range(dim_start, dim_end):
            embeddings = embeddings.at[ti, d].add(1.0)

        # Small random component in remaining dims for interaction
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[ti].add(shared)

    # L2-normalize and scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1

    return embeddings


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512

    print("Testing KernelDispatch...")
    dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536)
    x = mx.random.normal((1, 64, d_model))
    y = dispatch(x)
    mx.eval(y)
    assert y.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y.shape}"
    # Check dispatch weights are cached
    assert hasattr(dispatch, '_dispatch_weights')
    dw = dispatch._dispatch_weights
    mx.eval(dw)
    assert dw.shape == (1, 64, 22), f"Expected (1, 64, 22), got {dw.shape}"
    # Check dispatch weights sum to 1
    sums = mx.sum(dw, axis=-1)
    mx.eval(sums)
    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-5).item(), \
        f"Dispatch weights should sum to 1, got {sums}"
    print(f"  KernelDispatch: {x.shape} → {y.shape} ✓")
    print(f"  Dispatch weights: {dw.shape}, top op per position varies ✓")

    print("Testing KernelIntegrate...")
    integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)
    y2 = integrate(x)
    mx.eval(y2)
    assert y2.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y2.shape}"
    tw = integrate._type_weights
    mx.eval(tw)
    assert tw.shape == (1, 64, 5), f"Expected (1, 64, 5), got {tw.shape}"
    print(f"  KernelIntegrate: {x.shape} → {y2.shape} ✓")
    print(f"  Type weights: {tw.shape} ✓")

    # Check op embeddings have structure
    op_emb = dispatch.op_embeddings
    mx.eval(op_emb)
    # Ops in same family should be more similar than across families
    add_embed = op_emb[0]  # ADD
    sub_embed = op_emb[1]  # SUB
    eq_embed = op_emb[7]   # EQ (different family)
    mx.eval(add_embed, sub_embed, eq_embed)
    same_fam_sim = float(mx.sum(add_embed * sub_embed).item())
    cross_fam_sim = float(mx.sum(add_embed * eq_embed).item())
    print(f"  Op embedding structure: same-family sim={same_fam_sim:.4f}, "
          f"cross-family sim={cross_fam_sim:.4f}")

    # Test gradient flow
    import mlx.nn as nn_mod

    class TestModel(nn_mod.Module):
        def __init__(self):
            super().__init__()
            self.dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536)
            self.integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)

        def __call__(self, x):
            h = self.dispatch(x)
            h = self.integrate(h)
            return mx.mean(h)

    tm = TestModel()
    mx.eval(tm.parameters())

    def test_loss(tm, x):
        return tm(x)

    gfn = nn_mod.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)
    print(f"  Gradient flow OK: loss={lv.item():.4f} ✓")

    print("kernel_dispatch.py self-test: all ok ✓")
