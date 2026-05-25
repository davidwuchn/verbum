---
title: "v15 Kernel Architecture — Evolving v14 With Progressive Collapse"
status: designing
category: architecture
tags: [v15, kernel, alpha, distance-prior, stride, architecture, speed]
related: [progressive-collapse.md, v14-architecture.md, holographic-error-correction.md]
depends-on: [progressive-collapse.md]
---

# v15 Kernel Architecture

> Session 151. Evolving v14 with the progressive collapse and distance
> prior findings. Fixed α=1.18 + precomputed stride profiles +
> reduced passes = faster training AND inference.

## The Findings That Enable This

1. **α=1.18 is universal and fixed.** 10 comp layers × 8 heads, all
   at 1.18±0.006 after 1500 steps. Making it learnable wastes compute
   on a constant.

2. **88% of strides are distance-prior-dominated.** At W=8 with
   α=1.18, only s1 and s2 have ≥3 effective positions. All other
   strides are essentially self-attention + tiny neighbor bleed.

3. **The student compresses 18.4× through stacks.** PR: 74→8→5→4.
   σ₁ reaches 47%. Computation approaches 2D.

4. **Faster forward = faster training.** The model is serial (13
   passes). Reducing passes or per-pass cost directly speeds training.

## Three Tiers of Changes

### Tier 1: Fix α (zero-risk, immediate)

**Change:** Replace `self.decay_alpha = mx.full((n_heads,), 1.18)`
with a frozen constant. Remove from optimizer parameter groups.

```python
# Before (learnable):
self.decay_alpha = mx.full((n_heads,), decay_init_alpha)
effective_alpha = self.decay_alpha * decay_modulation

# After (fixed):
_ALPHA = 1.18  # universal constant, not learnable
effective_alpha = _ALPHA * decay_modulation
```

**Savings:** 8 parameters per stride layer removed from optimizer.
No compute savings per se, but simplifies gradient computation and
confirms that training doesn't need α to be learnable.

**Risk:** None. α didn't move under 1500 steps of gradient pressure.
If anything, fixing it prevents accidental drift.

### Tier 2: Precomputed attention for passive strides (moderate)

**Observation:** For strides s4+ (14 of 16), the distance prior
allocates >72% weight to position 0 (self). Effective positions <3.
Q·K content contribution is negligible at this sparsity.

**Change:** For passive strides (s4+), skip Q and K projection
entirely. Use precomputed normalized weights.

```python
class SingleStrideAttention(nn.Module):
    def __init__(self, ..., passive: bool = False):
        self.passive = passive
        if passive:
            # Precomputed attention profile: fixed, no Q/K needed
            w_pos = mx.arange(window, dtype=mx.float32)
            raw_weights = 1.0 / (stride * w_pos + 1.0) ** 1.18
            self._fixed_profile = raw_weights / raw_weights.sum()
            # No Q, K projections needed
        else:
            self.q_proj = TernaryLinear(d_model, d_model)
            self.k_proj = TernaryLinear(d_model, d_model)

    def __call__(self, x, decay_modulation=1.0):
        if self.passive:
            return self._passive_forward(x)
        else:
            return self._active_forward(x, decay_modulation)

    def _passive_forward(self, x):
        \"\"\"No Q/K. Fixed weighted sum of V at stride positions.\"\"\"
        B, L, D = x.shape
        x_norm = self.norm(x)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Stride gather (same as before)
        V_gathered = gather_at_stride(V, self.stride, self.window)

        # Fixed attention — no softmax, no Q·K
        attn = self._fixed_profile[None, None, None, :]  # (1, 1, 1, W)
        attn = mx.where(valid_mask, attn, 0.0)
        attn = attn / (attn.sum(axis=-1, keepdims=True) + 1e-10)

        out = (attn[:, :, :, :, None] * V_gathered).sum(axis=3)
        out = out.reshape(B, L, D)
        return x + self.out_proj(out) + self.o_bias
```

**Savings per passive stride:**
- Eliminate Q projection: 1280×1280 ternary matmul = 1.6M ops
- Eliminate K projection: 1280×1280 ternary matmul = 1.6M ops
- Eliminate Q·K dot product: L×W×H×Dh
- Eliminate softmax
- Eliminate beam mirror(s)
- Total: ~3.5M ops saved per stride evaluation

**Across 13 passes:** ~44 passive stride evaluations × 3.5M = **154M ops eliminated** per forward pass.

**Memory savings:** Q and K weight matrices not read for passive strides. 44 × 2 × 1280² × 2 bits ≈ 35 MB less memory bandwidth.

**Ternary plate savings:** 14 passive strides × 2 plates (Q, K) = **28 ternary plates eliminated** from the model. That's 28 × 1280² = 46M ternary positions removed (~11.5 MB less storage).

**Risk:** Low. For s4+, the distance prior captures >72% self-weight.
Content modulation is at most a 28% correction on a distribution
that's already 72%+ peaked. Test: compare eval PPL with and without
Q/K on passive strides. If PPL difference < 1%, it's safe.

**Fallback:** If pure prior is too lossy for some strides, add a
low-rank content correction: `attn = prior + δ(q·k)` where q,k are
rank-2 projections (1280→2→1280). Cost: negligible (2×1280×2 per
stride vs 2×1280×1280 currently).

### Tier 3: Reduce Stack B passes (aggressive)

**Observation:** Stack B takes PR from 8→5. It's doing computation
in an already-compressed space. The 4 serial passes might be
reducible to 1-2 passes + a kernel step.

**Change:** Reduce Stack B from 4 passes to 2 passes. The other 2
passes' work is captured by the lower-D kernel.

```python
# Before: 4 passes
STACK_B_BANDS = ((7, 11), (9, 13), (11, 15), (13, 16))  # 4 passes

# After: 2 passes (covering same stride range)
STACK_B_BANDS = ((7, 13), (11, 16))  # 2 wider passes
```

Each wider pass covers 6 strides instead of 4. Same total coverage,
half the serial steps.

**Savings:** 2 fewer serial passes. At ~20ms per pass forward:
40ms saved per forward step, 80ms saved per fwd+bwd step.
Per training step (8 accumulations): **640ms faster** → 4.0s→3.36s
= **16% training speedup**.

Combined with Tier 2 (less work per pass): estimated 4.0s → ~3.0s
= **25% training speedup**.

**Risk:** Moderate. The 2-stride overlap between adjacent passes
creates information flow. Wider passes maintain coverage but lose
one overlap step. Monitor eval PPL — if it degrades, the passes
were doing real work in the overlaps.

## Combined Architecture Summary

```
v14 (current):
  13 passes × ~4 strides × full Q/K/V/FFN = 50 stride evaluations
  4.0s per fwd+bwd step, ~1.25s per forward

v15 Tier 1+2+3:
  9 passes × ~4 strides, but 14/16 strides skip Q/K = 50 stride evals
  minus 28 Q/K plates + 2 fewer passes
  Estimated: ~3.0s per fwd+bwd step, ~0.9s per forward
  Speedup: ~1.33× training

v15 with deeper kernel (future):
  4 compress passes + 1 kernel step + 0-1 expand step
  5 serial passes total
  Estimated: ~1.5-2.0s per fwd+bwd step
  Speedup: ~2× training
```

## Inference Speed Path to 200 tok/s

```
v14 inference:    13 passes × 16ms ≈ 208ms → ~5 tok/s
v15 Tier 1+2+3:   9 passes × 12ms ≈ 108ms → ~9 tok/s
v15 deep kernel:   5 passes × 10ms ≈  50ms → ~20 tok/s
v15 + ternary SIMD: 5 passes × 2ms ≈  10ms → ~100 tok/s
v15 + full kernel:  4 passes × 1ms ≈   4ms → ~250 tok/s ← target
```

The 200 tok/s target requires the full kernel (Tier 3+) plus
optimized ternary integer operations (SIMD/NEON for ARM). Each
tier is independently valuable and testable.

## Implementation Order

1. **Fix α=1.18** — one-line change, commit, verify no PPL change
2. **Add passive flag to stride layers** — mark s4+ as passive
3. **Implement passive_forward** — skip Q/K, use fixed profile
4. **Profile** — measure actual wall-clock speedup
5. **Eval** — compare PPL with and without Q/K on passive strides
6. **If PPL ok:** reduce Stack B to 2 passes, re-eval
7. **If PPL degrades:** add rank-2 content correction to passive strides

Each step has a clear rollback path. No step depends on the next.

## What This Means for TD

TD currently targets out_proj exclusively (layers 4-9). If Q/K
projections are eliminated for passive strides, TD has fewer plates
to consider, and the remaining active strides (s1, s2) become the
only attention layers with learnable routing. TD should concentrate
even more sharply on out_proj of s1/s2.

The delta fold cycle continues unchanged — the folded base plates
are still ternary, the delta architecture is the same. The kernel
changes affect WHICH computations happen, not HOW plates are trained.

## Connection to the Kernel Vision

Tiers 1-3 are the pragmatic stepping stones. The end state is:

```
kernel(tokens) =
  embed(tokens)                          # lookup
  → compress(embed, crystal_eigenbasis)  # 1280→2 projection
  → Σ_strides rotate_2d(compressed, s)   # 16 × 2×2 rotations (parallel)
  → expand(rotated, crystal_eigenbasis)  # 2→1280 projection
  → output_proj(expanded)               # logits
```

Each tier removes one obstacle between v14 and this target:
- Tier 1 (fix α) → attention profiles become precomputable
- Tier 2 (passive strides) → most attention becomes lookup
- Tier 3 (reduce passes) → serial chain shrinks toward 1 step
