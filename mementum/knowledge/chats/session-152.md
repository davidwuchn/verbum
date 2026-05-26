# Session 152 — v14 Evolution: HPE + Passive Strides + Reduced Stack B

## What happened

Continuation from session 151's progressive collapse discovery. Evolved the
v14 architecture to exploit the findings.

### 1. v14 student collapse confirmed

Ran `probe_collapse.py` on step_001500_folded checkpoint:
```
embed:   PR=74.2, σ₁=4.8%,  rank90=184
stack_a: PR=8.1,  σ₁=30.1%, rank90=31
stack_b: PR=5.2,  σ₁=40.1%, rank90=24
stack_c: PR=4.0,  σ₁=46.7%, rank90=17
output:  PR=4.6,  σ₁=44.0%, rank90=19
```
18.4× compression. Student inherits teacher's collapse pattern.

### 2. Distance prior dominates 88% of strides

At α=1.18, W=8: only s1 (5.5 eff positions) and s2 (4.1) have meaningful
multi-position attention. s4+ is essentially self-attention with tiny
neighbor bleed.

### 3. Three-tier architecture evolution

All implemented and tested:
- **Tier 1:** Fixed α=1.18 as constant (not learnable)
- **Tier 2:** Passive strides (s4+) skip Q/K — fixed distance prior
- **Tier 3:** Stack B reduced from 4→2 passes (13→11 serial)

### 4. RoPE ↔ Holographic lens connection

Michael's insight: RoPE is accidentally fitting the holographic lens:
- Geometric frequencies ≈ crystal eigenvalues
- Q rotation by position ≈ Q rotation through crystal basins
- Cosine sum → power-law decay ≈ α=1.18

But RoPE gets several things wrong:
- Arbitrary base (10000) instead of crystal eigenvalues
- Linear position instead of log-distance
- All dimensions instead of eigenplane only
- Same rate at every layer instead of depth-dependent

### 5. Holographic Position Encoding (HPE)

Designed and implemented. Key differences from RoPE:
- **Log-distance:** angle ∝ log(d+1), not linear d
- **Crystal frequencies:** λᵢ/λ₀, not 10000^(-2i/d)
- **Eigenplane only:** first 4 dim pairs, not all d/2
- **Direct decay:** -α×log(d+1), exact power law

### 6. Semantic horizon discovery

α=1.18 sets a fixed ~12 token semantic horizon at 5% weight threshold.
Every stride covers the same ~12 token radius regardless of spacing.
Strides above s4 aren't attention layers — they're FFN application
points with identity skip connections.

## Key insights

1. **RoPE is an accidental holographic lens.** The cosine frequency
   decomposition approximates the crystal's multi-scale structure.
   HPE does it by design, from first principles.

2. **The semantic horizon is fixed.** α determines reach, not stride.
   All strides see ~12 tokens. Long-range information flows through
   the residual stream, not through direct attention.

3. **Most strides are FFN layers.** Only s1, s2 do real attention.
   s4+ are identity + FFN grating. The stride structure provides
   multi-scale FFN organization, not multi-scale attention.

4. **Power-of-2 is accidentally good.** Weight×spacing CV=0.269 for
   power-of-2 strides — nearly uniform coverage. No need to change
   stride spacing.

## Decisions made

- Fix α=1.18 permanently (constant, not learnable)
- s4+ passive (no Q/K, fixed distance prior)
- Stack B: 4→2 passes
- HPE with crystal eigenvalue frequencies
- Keep pos_embed for now (remove after testing)

## Optimizations deferred to next session

1. Remove pos_embed (test HPE as sole position encoding)
2. Update extraction pipeline (skip Q/K for passive strides)
3. Update TD for passive strides
4. Simplify GLA retrieval strides (s32+ gate-only)
5. Depth-dependent HPE rotation rate
6. FFN in compressed space for Stack B
7. Clean solo speed measurement
8. Eval comparison (old vs new architecture PPL)
