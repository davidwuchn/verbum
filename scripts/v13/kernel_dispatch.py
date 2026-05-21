"""
Combinator dispatch and integration for v13 — beam/plate separated architecture.

V13 cleanly separates two orthogonal signals that V12 entangled:

  PLATE PATH (S1 — structural, etch-shaped)
    x → TernaryMirror → TernaryLinear → raw_logits   (8-wide)
    Pure ternary. The mirror deflects the beam to the plate's reading angle.
    The plate is topology-only: which combinator fits THIS position's shape.
    No continuous params in this path — gradient cannot overwrite the structure.

  BEAM PATH (S3 — contextual, GD-trained)
    x → beam_norm → beam_proj(nn.Linear d→8) → beam_logits
    + combinator_embeddings dot product → embedding_logits
    Pure continuous. Gradient shapes what the current token stream needs.

  COMBINED:
    dispatch_logits = raw_logits + beam_logits + embedding_logits
                    + dispatch_prior + pass_bias
    dispatch_weights = softmax(dispatch_logits)

The plate gives a structural prior (which combinator topology fits here).
The beam gives a contextual adjustment (what this input needs right now).
They ADD in logit space — orthogonal gradient directions, no interference.

CombinatorIntegrate is simplified from V12:
  - Remove: MathExtractor, CategoryDispatch, math kernel pathway, abstraction slots
  - Keep: type projections per combinator (TernaryLinear per type), kernel compute
  - WHNF uses a mechanical ternary FFN (zero continuous params in its kernel)

Architecture per pass (7-pass hourglass):
  Phase 0 (dispatch):  CombinatorDispatch → dispatch_weights (B, T, 8)
                                           → comb_context (B, T, d_model)
  Phase 2 (integrate): CombinatorIntegrate → typed hidden state

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from config import V13Config
from kernel import N_COMBINATORS, COMBINATOR_NAMES
from ternary import TernaryLinear, TernaryMirror


# ══════════════════════════════════════════════════════════════════════
# § 1  Dispatch prior
# ══════════════════════════════════════════════════════════════════════


def _compute_dispatch_prior(ratio: tuple[float, ...]) -> mx.array:
    """log(ratio / sum(ratio)) — additive logit bias for the 8-way softmax.

    When dispatch logits carry no signal, softmax defaults to the ratio.
    Empirical universal ratio K:I:B:C:D:Y:W:WHNF from session 119.
    """
    r = mx.array(list(ratio), dtype=mx.float32)
    return mx.log(r / mx.sum(r))


# ══════════════════════════════════════════════════════════════════════
# § 2  Combinator embedding initialization
# ══════════════════════════════════════════════════════════════════════


def _init_combinator_embeddings(n_combinators: int, d_model: int) -> mx.array:
    """8 near-orthogonal combinator identity directions in d_model space.

    Each combinator occupies a dedicated block of d_model // n_combinators
    dimensions, making the initial embeddings maximally separated.
    A small shared component allows cross-combinator interaction.
    """
    block = d_model // n_combinators
    embeddings = mx.zeros((n_combinators, d_model))
    for i in range(n_combinators):
        start = i * block
        end = start + block
        block_vals = mx.random.normal((block,)) * 0.5
        embeddings = embeddings.at[i, start:end].add(block_vals)
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[i].add(shared)
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    return embeddings / norms * 0.1


def _init_type_embeddings(n_combinators: int, d_model: int) -> mx.array:
    """8 near-orthogonal combinator type directions — for the integrate pathway.

    Distinct from dispatch embeddings: these encode WHAT TYPE a position IS,
    not which combinator to apply.
    """
    block = max(1, d_model // (n_combinators * 2))
    embeddings = mx.zeros((n_combinators, d_model))
    for i in range(n_combinators):
        start = i * block
        end = min((i + 1) * block, d_model)
        # One-hot-ish block activation
        block_len = end - start
        embeddings = embeddings.at[i, start:end].add(
            mx.ones((block_len,))
        )
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[i].add(shared)
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    return embeddings / norms * 0.1


# ══════════════════════════════════════════════════════════════════════
# § 3  CombinatorDispatch — beam/plate separated 8-way routing
# ══════════════════════════════════════════════════════════════════════


class CombinatorDispatch(nn.Module):
    """Phase 0: which of 8 combinators (KIBC-DYWH) applies at each position?

    Two orthogonal signal paths that ADD in logit space:

      PLATE PATH (S1 — structural)
        The plate reads the ternary topology shaped by etching.
        A TernaryMirror deflects x to the plate's optimal reading angle,
        then a TernaryLinear projects to 8 raw_logits.
        No continuous parameters — only the sign topology matters.
        Gradient shape: zero (evolutionary, etch-only).

      BEAM PATH (S3 — contextual)
        beam_norm(x) → beam_proj(Linear d→8) → beam_logits
        combinator_embeddings dot product → embedding_logits
        Gradient shape: Adam, full precision.

    Combined:
        dispatch_logits = raw_logits + beam_logits + embedding_logits
                        + dispatch_prior + pass_bias[pass_idx]
        dispatch_weights = softmax(dispatch_logits)          (B, T, 8)
        comb_context     = dispatch_weights @ combinator_embeddings  (B, T, d_model)

    Orthogonal gradients: plate path is topology-only (no gradient),
    beam path is continuous-only (no ternary quantization).  They share
    the same logit accumulator but their updates never interfere.

    EMA diagnostics are stored per combinator for monitoring routing
    health across training steps.
    """

    def __init__(self, cfg: V13Config):
        super().__init__()
        d = cfg.d_model
        n = N_COMBINATORS  # 8

        # ── Plate path (S1 — ternary, etch-shaped) ──────────
        # Mirror deflects beam to the plate's reading angle.
        # TernaryLinear reads topology → raw_logits.
        # Padded to multiple of 16 for quantized_matmul.
        self._n_padded = ((n + 15) // 16) * 16  # 16
        self.plate_mirror = TernaryMirror(d)
        # pre_norm=False: mirror already normalizes; plate reads directly
        self.plate_proj = TernaryLinear(d, self._n_padded, pre_norm=False)

        # ── Beam path (S3 — continuous, GD-trained) ─────────
        self.beam_norm = nn.RMSNorm(d)
        self.beam_proj = nn.Linear(d, n, bias=False)

        # Combinator embeddings: 8 near-orthogonal identity directions.
        # Dot product with beam gives embedding_logits.
        # Also used to produce comb_context after dispatch.
        self.combinator_embeddings = _init_combinator_embeddings(n, d)
        self.embed_scale = 0.5

        # Type embeddings: separate from dispatch embeddings.
        # Used in CombinatorIntegrate, owned here for shared initialization.
        self.type_embeddings = _init_type_embeddings(n, d)

        # ── Priors and pass biases ───────────────────────────
        # dispatch_prior: log(ratio/Σratio) — static logit offset
        self._dispatch_prior = _compute_dispatch_prior(cfg.dispatch_ratio)

        # pass_dispatch_bias: (n_passes, 8) — depth-selective prior
        self._pass_bias = mx.array(
            [list(row) for row in cfg.pass_dispatch_bias],
            dtype=mx.float32,
        )  # (n_passes, 8)

        # ── EMA diagnostics (mean dispatch weight per combinator) ──
        self._ema_decay = cfg.dispatch_kl_ema_decay
        self._dispatch_ema = mx.ones((n,)) / n  # uniform at init

        # Cache for external access (e.g. KL loss, probing)
        self._dispatch_weights: mx.array | None = None
        self._dispatch_weights_live: mx.array | None = None

    def _normalize_embeddings(self) -> mx.array:
        """L2-normalize combinator_embeddings to fixed scale."""
        norms = mx.sqrt(
            mx.sum(self.combinator_embeddings * self.combinator_embeddings,
                   axis=-1, keepdims=True) + 1e-8
        )
        return self.combinator_embeddings * (self.embed_scale / norms)

    def __call__(
        self,
        x: mx.array,
        pass_idx: int = 0,
    ) -> tuple[mx.array, mx.array]:
        """Compute 8-way dispatch weights and combinator context.

        Args:
            x:        (B, T, d_model) hidden state
            pass_idx: which pass (0..6) — selects pass_dispatch_bias row

        Returns:
            dispatch_weights: (B, T, 8) softmax probabilities
            comb_context:     (B, T, d_model) = dispatch_weights @ combinator_embeddings
        """
        # ── Plate path ───────────────────────────────────────
        # Deflect beam angle, then read topology → raw_logits
        x_plate = self.plate_mirror(x)              # (B, T, d)
        raw_logits = self.plate_proj(x_plate)       # (B, T, n_padded)
        raw_logits = raw_logits[..., :N_COMBINATORS]  # (B, T, 8)

        # ── Beam path ────────────────────────────────────────
        h_beam = self.beam_norm(x)                  # (B, T, d)
        beam_logits = self.beam_proj(h_beam)        # (B, T, 8)

        # Embedding logits: dot product of normed beam with each combinator
        normed_emb = self._normalize_embeddings()   # (8, d)
        # (B, T, d) @ (d, 8) → (B, T, 8)
        embedding_logits = h_beam @ normed_emb.T

        # ── Combine ──────────────────────────────────────────
        # All terms in logit space — orthogonal gradient directions
        dispatch_logits = (
            raw_logits        # plate: topology prior
            + beam_logits     # beam: contextual adjustment
            + embedding_logits  # identity alignment
            + self._dispatch_prior   # empirical ratio prior
            + self._pass_bias[pass_idx]  # depth-selective prior
        )

        dispatch_weights = mx.softmax(dispatch_logits, axis=-1)  # (B, T, 8)

        # ── EMA update (stop_gradient — diagnostics only) ────
        w_mean = mx.stop_gradient(mx.mean(dispatch_weights, axis=(0, 1)))  # (8,)
        self._dispatch_ema = (
            self._ema_decay * self._dispatch_ema
            + (1.0 - self._ema_decay) * w_mean
        )

        # Cache for external access
        self._dispatch_weights = mx.stop_gradient(dispatch_weights)
        self._dispatch_weights_live = dispatch_weights

        # ── Combinator context ────────────────────────────────
        # (B, T, 8) @ (8, d) → (B, T, d)
        comb_context = dispatch_weights @ normed_emb

        return dispatch_weights, comb_context

    @property
    def diagnostics(self) -> dict[str, float]:
        """Per-combinator mean dispatch weight EMA for logging."""
        if self._dispatch_ema is None:
            return {}
        ema_vals = self._dispatch_ema
        mx.eval(ema_vals)
        return {
            f"dispatch_ema_{COMBINATOR_NAMES[i]}": float(ema_vals[i].item())
            for i in range(N_COMBINATORS)
        }


# ══════════════════════════════════════════════════════════════════════
# § 4  CombinatorIntegrate — simplified type projection + kernel compute
# ══════════════════════════════════════════════════════════════════════


class CombinatorIntegrate(nn.Module):
    """Phase 2: apply the dispatched combinator reduction, type the result.

    Simplified from V12:
      - Removed: MathExtractor, CategoryDispatch, math kernel pathway,
                 abstraction slots, retrieval register conditioning
      - Kept:    type projections (TernaryLinear per combinator type),
                 kernel compute (operand extraction + combinator reductions),
                 compute gate (blend kernel vs type-projection output)
      - Changed: WHNF uses a mechanical ternary FFN (key/value plates)

    Type pathway:
        type_logits = type_proj(h)[..., :8]          TernaryLinear
        type_weights = softmax(type_logits)
        type_context = type_weights @ type_embeddings
        ffn_out = type_down(gelu(type_up(h + type_context)))

    Kernel compute pathway (non-differentiable; discrete):
        Extracts 3 integer operands from h, applies the dispatched
        combinator's exact reduction, encodes result via nn.Embedding.

    WHNF mechanical FFN:
        When the dispatched combinator is WHNF (terminal), a purely
        ternary FFN runs: key_plate(h) → relu → value_plate → out.
        Zero continuous params in this kernel — only sign topology.

    Compute gate:
        gate = sigmoid(gate_proj(h) + gate_bias)  ← starts ~0 (pure type-FFN)
        output = gate * kernel_result + (1 - gate) * ffn_out

    The gate starts near zero (pure FFN pathway dominates), and learns
    to open for positions where exact combinator reductions help.
    """

    def __init__(self, cfg: V13Config):
        super().__init__()
        d = cfg.d_model
        d_ff = cfg.d_ff
        n = N_COMBINATORS  # 8

        # ── Normalization ─────────────────────────────────────
        self.norm = nn.RMSNorm(d)

        # Pad for quantized_matmul
        self._n_padded = ((n + 15) // 16) * 16  # 16

        # ── Type projection pathway ───────────────────────────
        # TernaryLinear: topology-shaped type recognition
        self.type_proj = TernaryLinear(d, self._n_padded, pre_norm=False)
        # type_embeddings shared reference: initialized in CombinatorDispatch
        # but we own a local copy for integrate's use.
        self.type_embeddings = _init_type_embeddings(n, d)

        # Standard FFN — continuous, GD-trained
        self.type_up = TernaryLinear(d, d_ff, pre_norm=False)
        self.type_down = TernaryLinear(d_ff, d, pre_norm=False)

        # ── Kernel compute pathway ────────────────────────────
        # Operand extractors: d → max_val (argmax → integer operand)
        self._max_val = 256
        _mv_padded = ((self._max_val + 15) // 16) * 16
        self._mv_padded = _mv_padded
        self.operand0 = TernaryLinear(d, _mv_padded, pre_norm=False)
        self.operand1 = TernaryLinear(d, _mv_padded, pre_norm=False)
        self.operand2 = TernaryLinear(d, _mv_padded, pre_norm=False)

        # Result encoder: integer → d_model embedding
        self._result_buckets = 1024
        self._result_offset = self._result_buckets // 2
        self.result_embed = nn.Embedding(self._result_buckets, d)

        # ── WHNF mechanical FFN (zero continuous params) ──────
        # Purely ternary: key_plate → relu → value_plate.
        # No gamma training — plates are topology-only.
        # d_ffn_whnf must be divisible by 16 for TernaryLinear.
        d_ffn_whnf = d_ff
        self.whnf_key_plate = TernaryLinear(d, d_ffn_whnf, pre_norm=False)
        self.whnf_value_plate = TernaryLinear(d_ffn_whnf, d, pre_norm=False)

        # ── Compute gate: blend kernel vs type-FFN ────────────
        # Starts near 0 → pure type-FFN; opens as model learns.
        # Output padded to 16; we take [..., :1].
        self.gate_proj = TernaryLinear(d, 16, pre_norm=False)
        # Zero gamma → output=0 at init → sigmoid(-5) ≈ 0.007
        self.gate_proj.gamma = mx.zeros_like(self.gate_proj.gamma)
        self.gate_bias = mx.full((1,), -5.0)

        self.dropout = nn.Dropout(cfg.dropout)

        # Diagnostic cache
        self._type_weights: mx.array | None = None
        self._compute_gate: mx.array | None = None
        self._kernel_info: dict | None = None

    # ── § 4.1  WHNF mechanical kernel ─────────────────────────────────

    def _whnf_kernel(self, h: mx.array) -> mx.array:
        """Mechanical ternary FFN for WHNF (terminal) positions.

        keys  = key_plate(h)       — ternary matmul, no continuous params
        active = relu(keys)        — ReLU gate
        out    = value_plate(active) — ternary matmul
        """
        keys = self.whnf_key_plate(h)   # (B, T, d_ffn)
        active = mx.maximum(keys, 0.0)  # ReLU gate
        return self.whnf_value_plate(active)  # (B, T, d)

    # ── § 4.2  Kernel compute ──────────────────────────────────────────

    def _kernel_compute(
        self,
        h: mx.array,
        dispatch_weights: mx.array,
    ) -> tuple[mx.array, dict]:
        """Extract operands, apply 8-combinator reductions, encode result.

        Combinator kernel functions (from kernel.py):
            K(op0, op1, op2) → op0              (select first)
            I(op0, op1, op2) → op0              (identity)
            B(op0, op1, op2) → op0+op1+op2      (composition signal)
            C(op0, op1, op2) → op0+op2          (flip: skip op1)
            D(op0, op1, op2) → op0*2+op1+op2    (deep compose)
            Y(op0, op1, op2) → op0              (recursion: persist fn)
            W(op0, op1, op2) → op0+op1*2        (duplicate: arg twice)
            WHNF             → whnf_kernel(h)   (mechanical ternary FFN)

        For WHNF (index 7), we blend the whnf_kernel output in place of
        the discrete result_embed path — the mechanical FFN is continuous
        in the blend gate, not discrete.
        """
        B, T, _ = h.shape

        # Extract operands (non-differentiable argmax)
        op0_logits = self.operand0(h)[..., :self._max_val]
        op1_logits = self.operand1(h)[..., :self._max_val]
        op2_logits = self.operand2(h)[..., :self._max_val]

        op0 = mx.stop_gradient(mx.argmax(op0_logits, axis=-1)).astype(mx.int32)
        op1 = mx.stop_gradient(mx.argmax(op1_logits, axis=-1)).astype(mx.int32)
        op2 = mx.stop_gradient(mx.argmax(op2_logits, axis=-1)).astype(mx.int32)

        comb = mx.stop_gradient(
            mx.argmax(dispatch_weights, axis=-1)).astype(mx.int32)  # (B, T)

        # ── 8-combinator discrete reductions ─────────────────
        # All 8 computed in parallel; select by dispatched combinator.
        r_K    = op0                          # K: select first
        r_I    = op0                          # I: identity
        r_B    = op0 + op1 + op2             # B: additive compose
        r_C    = op0 + op2                   # C: flip (skip op1)
        r_D    = op0 * 2 + op1 + op2        # D: deep compose (weighted)
        r_Y    = op0                          # Y: recursion (persist fn)
        r_W    = op0 + op1 * 2              # W: duplicate (arg twice)
        r_WHNF = op0                          # WHNF placeholder (mechanical path below)

        # Stack (8, B, T) and select by combinator index
        all_results = mx.stack(
            [r_K, r_I, r_B, r_C, r_D, r_Y, r_W, r_WHNF], axis=0
        )  # (8, B, T)

        comb_clamped = mx.clip(comb, 0, N_COMBINATORS - 1)
        b_idx = mx.broadcast_to(mx.arange(B)[:, None], (B, T))
        t_idx = mx.broadcast_to(mx.arange(T)[None, :], (B, T))
        result = all_results[comb_clamped, b_idx, t_idx]  # (B, T)

        # ── Encode result via embedding ───────────────────────
        result_idx = mx.stop_gradient(
            mx.clip(result + self._result_offset, 0, self._result_buckets - 1)
        ).astype(mx.int32)
        discrete_out = self.result_embed(result_idx)  # (B, T, d)

        # ── WHNF mechanical path ──────────────────────────────
        # For WHNF positions, replace discrete_out with whnf_kernel output.
        # Blend: is_whnf * whnf_out + (1 - is_whnf) * discrete_out
        # is_whnf is the soft dispatch weight for combinator 7.
        whnf_out = self._whnf_kernel(h)                       # (B, T, d)
        whnf_weight = dispatch_weights[..., 7:8]             # (B, T, 1)
        kernel_out = (
            whnf_weight * whnf_out
            + (1.0 - whnf_weight) * discrete_out
        )  # (B, T, d)

        kernel_info = {
            "combinator": mx.stop_gradient(comb),
            "op0":        mx.stop_gradient(op0),
            "op1":        mx.stop_gradient(op1),
            "op2":        mx.stop_gradient(op2),
            "result":     mx.stop_gradient(result),
        }

        return kernel_out, kernel_info

    # ── § 4.3  Forward ────────────────────────────────────────────────

    def __call__(
        self,
        x: mx.array,
        dispatch_weights: mx.array,
        comb_context: mx.array,
        pass_idx: int = 0,
    ) -> mx.array:
        """Apply combinator reductions and type the result.

        Args:
            x:               (B, T, d_model) input hidden state
            dispatch_weights: (B, T, 8) from CombinatorDispatch.__call__
            comb_context:    (B, T, d_model) = dispatch_weights @ combinator_embeddings
            pass_idx:        which pass (unused currently, reserved for pass mirrors)

        Returns:
            (B, T, d_model) — residual-connected output
        """
        h = self.norm(x)

        # ── Type projection pathway ───────────────────────────
        type_logits = self.type_proj(h)[..., :N_COMBINATORS]  # (B, T, 8)
        type_weights = mx.softmax(type_logits, axis=-1)
        self._type_weights = mx.stop_gradient(type_weights)

        # Type context: weighted sum over type embeddings
        # (B, T, 8) @ (8, d) → (B, T, d)
        type_context = type_weights @ self.type_embeddings

        # Incorporate dispatch's combinator context into FFN input
        modulated = h + type_context + comb_context
        ffn_out = self.type_down(nn.gelu(self.type_up(modulated)))  # (B, T, d)

        # ── Kernel compute pathway ────────────────────────────
        kernel_out, kernel_info = self._kernel_compute(h, dispatch_weights)
        self._kernel_info = kernel_info

        # ── Compute gate: blend kernel vs FFN ─────────────────
        # Starts at ~0 → pure FFN; opens for computational positions.
        gate = mx.sigmoid(
            self.gate_proj(h)[..., :1] + self.gate_bias
        )  # (B, T, 1)
        self._compute_gate = mx.stop_gradient(gate)

        blended = gate * kernel_out + (1.0 - gate) * ffn_out  # (B, T, d)

        return x + self.dropout(blended)

    @property
    def diagnostics(self) -> dict[str, float]:
        """Type weights and gate statistics for logging."""
        result = {}
        if self._type_weights is not None:
            tw = self._type_weights
            mx.eval(tw)
            tw_mean = mx.mean(tw, axis=(0, 1))
            for i in range(N_COMBINATORS):
                result[f"type_w_{COMBINATOR_NAMES[i]}"] = float(tw_mean[i].item())
        if self._compute_gate is not None:
            mx.eval(self._compute_gate)
            result["compute_gate_mean"] = float(
                mx.mean(self._compute_gate).item()
            )
        return result


# ══════════════════════════════════════════════════════════════════════
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import numpy as np

    cfg = V13Config()
    d = cfg.d_model
    B, T = 2, 32

    print(f"v13 kernel_dispatch self-test (d={d}, B={B}, T={T})")
    print(f"  N_COMBINATORS = {N_COMBINATORS}  ({', '.join(COMBINATOR_NAMES)})")

    # ── CombinatorDispatch ─────────────────────────────────────────────
    print("\n[1] CombinatorDispatch (beam/plate separated)...")
    dispatch = CombinatorDispatch(cfg)
    x = mx.random.normal((B, T, d))
    dw, cc = dispatch(x, pass_idx=0)
    mx.eval(dw, cc)

    assert dw.shape == (B, T, N_COMBINATORS), \
        f"dispatch_weights shape: expected {(B,T,N_COMBINATORS)}, got {dw.shape}"
    assert cc.shape == (B, T, d), \
        f"comb_context shape: expected {(B,T,d)}, got {cc.shape}"

    # Weights must sum to 1
    sums = mx.sum(dw, axis=-1)
    mx.eval(sums)
    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-4).item(), \
        "dispatch_weights must sum to 1"

    print(f"  dispatch_weights: {dw.shape}  ✓")
    print(f"  comb_context:     {cc.shape}  ✓")
    print(f"  weights sum to 1: ✓")

    # Mean dispatch distribution at init
    mean_dw = mx.mean(dw, axis=(0, 1))
    mx.eval(mean_dw)
    print(f"  Mean dispatch at init:")
    for i, name in enumerate(COMBINATOR_NAMES):
        print(f"    {name}: {float(mean_dw[i].item()):.4f}")

    # All 7 passes should produce valid weights
    print(f"\n  Testing all {cfg.n_passes} passes...")
    for p in range(cfg.n_passes):
        dw_p, cc_p = dispatch(x, pass_idx=p)
        mx.eval(dw_p, cc_p)
        sums_p = mx.sum(dw_p, axis=-1)
        mx.eval(sums_p)
        assert mx.allclose(sums_p, mx.ones_like(sums_p), atol=1e-4).item(), \
            f"Pass {p} dispatch weights don't sum to 1"
    print(f"  All {cfg.n_passes} passes valid  ✓")

    # EMA diagnostics
    diag = dispatch.diagnostics
    print(f"\n  EMA diagnostics (after 1 forward):")
    for k, v in diag.items():
        print(f"    {k}: {v:.4f}")
    assert len(diag) == N_COMBINATORS, \
        f"Expected {N_COMBINATORS} EMA entries, got {len(diag)}"
    print(f"  EMA diagnostics: {len(diag)} entries  ✓")

    # Cached weights accessible
    assert dispatch._dispatch_weights is not None
    assert dispatch._dispatch_weights.shape == (B, T, N_COMBINATORS)
    print(f"  Cached _dispatch_weights: {dispatch._dispatch_weights.shape}  ✓")

    # ── CombinatorIntegrate ───────────────────────────────────────────
    print("\n[2] CombinatorIntegrate (simplified, no math/slots)...")
    integrate = CombinatorIntegrate(cfg)
    y = integrate(x, dw, cc, pass_idx=0)
    mx.eval(y)

    assert y.shape == (B, T, d), \
        f"integrate output shape: expected {(B,T,d)}, got {y.shape}"
    print(f"  output shape: {y.shape}  ✓")

    # Type weights cached
    assert integrate._type_weights is not None
    tw = integrate._type_weights
    mx.eval(tw)
    assert tw.shape == (B, T, N_COMBINATORS), \
        f"type_weights shape: expected {(B,T,N_COMBINATORS)}, got {tw.shape}"
    tw_sums = mx.sum(tw, axis=-1)
    mx.eval(tw_sums)
    assert mx.allclose(tw_sums, mx.ones_like(tw_sums), atol=1e-4).item(), \
        "type_weights must sum to 1"
    print(f"  type_weights: {tw.shape}, sums to 1  ✓")

    # Compute gate starts near 0
    cg = integrate._compute_gate
    mx.eval(cg)
    cg_mean = float(mx.mean(cg).item())
    assert cg_mean < 0.02, \
        f"compute_gate should start near 0, got {cg_mean:.4f}"
    print(f"  compute_gate mean: {cg_mean:.4f} (starts near 0)  ✓")

    # Kernel info available
    ki = integrate._kernel_info
    assert ki is not None
    assert ki["combinator"].shape == (B, T)
    assert ki["op0"].shape == (B, T)
    print(f"  kernel_info: combinator {ki['combinator'].shape}  ✓")

    # Diagnostics
    diag2 = integrate.diagnostics
    assert "compute_gate_mean" in diag2
    print(f"  diagnostics: {list(diag2.keys())}  ✓")

    # ── Different passes produce different outputs ─────────────────────
    print("\n[3] Pass differentiation...")
    y0, _ = dispatch(x, pass_idx=0)
    y6, _ = dispatch(x, pass_idx=6)
    mx.eval(y0, y6)
    diff = float(mx.mean(mx.abs(y0 - y6)).item())
    print(f"  Dispatch diff (pass 0 vs 6): {diff:.6f}")
    assert diff > 0.0, "Different passes should produce different dispatch logits"
    print(f"  ✓")

    # ── Gradient flow ──────────────────────────────────────────────────
    print("\n[4] Gradient flow through CombinatorDispatch + CombinatorIntegrate...")

    class _TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.dispatch = CombinatorDispatch(cfg)
            self.integrate = CombinatorIntegrate(cfg)

        def __call__(self, x):
            dw, cc = self.dispatch(x, pass_idx=3)  # apex pass
            h = self.integrate(x, dw, cc, pass_idx=3)
            return mx.mean(h)

    model = _TestModel()
    mx.eval(model.parameters())

    x_small = mx.random.normal((1, 16, d))
    loss_and_grad = nn.value_and_grad(model, lambda m, xi: m(xi))
    loss_val, grads = loss_and_grad(model, x_small)
    mx.eval(loss_val, grads)

    # beam_proj should have gradient (it's nn.Linear)
    bp_grad = grads["dispatch"]["beam_proj"]["weight"]
    mx.eval(bp_grad)
    bp_norm = float(mx.mean(mx.abs(bp_grad)).item())
    assert bp_norm > 0.0, f"beam_proj should have gradient, got norm {bp_norm}"
    print(f"  beam_proj gradient norm: {bp_norm:.6f}  ✓")

    # combinator_embeddings should have gradient
    ce_grad = grads["dispatch"]["combinator_embeddings"]
    mx.eval(ce_grad)
    ce_norm = float(mx.mean(mx.abs(ce_grad)).item())
    assert ce_norm > 0.0, f"combinator_embeddings should have gradient"
    print(f"  combinator_embeddings gradient norm: {ce_norm:.6f}  ✓")

    # result_embed should have gradient
    re_grad = grads["integrate"]["result_embed"]["weight"]
    mx.eval(re_grad)
    re_norm = float(mx.mean(mx.abs(re_grad)).item())
    print(f"  result_embed gradient norm: {re_norm:.6f}  ✓")

    print(f"\n  loss: {float(loss_val.item()):.4f}  ✓")
    print(f"\nkernel_dispatch.py self-test: all assertions passed  ✓")
