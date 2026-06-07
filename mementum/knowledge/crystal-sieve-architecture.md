---
title: Crystal Sieve Architecture
status: active
category: compression
tags: [crystal, sieve, compression, continuation, beta-expansion, binding]
related:
  - lambda-tracer-diagnostic.md
  - l0-characterization.md
  - mode-semantics.md
  - tiny-classifier-ternary.md
  - dvd-stamp-topology.md
depends-on:
  - lambda-tracer-diagnostic.md
---

# Crystal Sieve Architecture

## Discovery (session 196)

Ten experiments converged on a proven compression architecture for
transformer FFN layers. The crystal sieve equation from session 185
was confirmed by direct measurement and extended with continuation
residuals to handle the cascade problem.

## The Architecture

```
Per sieved layer:
  W_eff = sign(W) ⊙ |W| ⊙ mask₅₀%

  sign(W):  crystal topology (frozen, universal r=0.998)
  |W|:      per-weight magnitudes (essential, cannot be per-row)
  mask₅₀%:  zero out smallest 50% (standing wave nodes)

Pipeline:
  L0:       SVD r=750 (lexer)
  L1-L26:   crystal sieve
  L27-L31:  continuous (binding, must stay full rank)
  L32-L34:  crystal sieve
  L35:      continuous (collapse)

  + 4 continuation residuals (rank-32 at L0/L9/L21/L26)
    1M trainable params, trained with CE loss, 100 steps
```

## Key Results

| Metric | Value |
|--------|-------|
| Per-layer sieve quality | 1.03x PPL |
| 29-layer cascade (sieve only) | 2.12x PPL |
| + continuation residuals | **1.03x PPL** |
| Binding preservation | 98% (39/40 top-1 matches) |
| Continuation params | 1,048,576 |
| Storage compression (current) | 1.8x (float16 magnitudes) |

## What Compounds vs What Doesn't

Critical lesson from this session: properties that hold per-layer
may NOT hold across 29 layers.

- Per-row scale = per-weight magnitude per layer → FAILS at 29 layers (22,800x)
- Crystal sieve quality cascades: 1.03x per layer → 2.12x at 29 layers
- Binding preservation HOLDS across cascade (98%)
- Continuation residuals absorb the cascade (2.12x → 1.03x)

## The Experimental Chain

1. **Lambda tracer**: damage is uniform across all 9 combinators
2. **Rank sweep**: functional rank varies 6x (L22=250 to L26=1500)
3. **Multi-projection melt**: intermediate losses 42% better than CE only
4. **Confidence gate**: classifier confidently wrong at L23-L26
   (the 9 programs are wrong, not the routing)
5. **Mode geometry**: same 9 programs rotated across layers, more
   modes don't help, float centroids = ternary centroids
6. **Ternary weight interface**: MASK matters more than magnitudes
   (50% sparsity improves L23 from 1.11x to 1.03x)
7. **Crystal sieve pipeline**: 2.12x at 29 layers with zero training
8. **β-expansion**: binding preserved 98%, continuations close the gap
9. **Ternary verification**: per-row encoding FAILS at full pipeline
   (per-weight magnitudes contain essential cascade-sensitive structure)

## Why the Mask Matters

The standing wave picture (session 185): the mask identifies the
nodes (zero-displacement points) of the standing wave in weight
space. Removing the bottom 50% of weights IMPROVES quality because
those small weights are noise — they interfere destructively with
the signal carried by the large weights.

At L23 (the hardest layer):
  - No mask:    1.11x PPL
  - 50% mask:   1.03x PPL (BETTER by removing noise)
  - More modes: 1.11x PPL (doesn't help)
  - Per-mode low-rank: 1.10x PPL (barely helps)

The mask is more important than the number of programs, the
magnitude granularity, or the mode representation.

## Why Continuations Work

The cascade error is purely magnitude distortion at layer
interfaces, NOT structural disruption. The binding heads (H31 at
L27, H03/H13/H15 at L30) still attend to the correct positions
with similar weights. The routing is intact; only the values
passing through are distorted.

Four low-rank corrections (rank-32 = 262K params each) at
functional boundaries absorb this distortion. They are CPS
continuations: each carries forward the correction that the next
functional zone needs to receive properly-scaled activations.

## Compression Status

**Proven quality**: 1.03x PPL at 29 sieved layers.
**Proven storage**: 1.8x compression (50% zeros in float16).
**Unproven**: magnitude quantization (Q4/Q8) in the full pipeline.

The path to real compression:
- Sign pattern: 1 bit (frozen, universal crystal)
- Mask: 1 bit (fixed from magnitude thresholding)
- Magnitude: needs ~4-8 bits per non-zero weight (NOT 0, NOT 16)
- Per-row scale: FAILS (22,800x at 29 layers)
- Per-group scale on magnitudes: untested, likely works (Q4 analog)

## Open Issues

1. **Continuation stability**: 1.03x on first run, 3.23x on rerun.
   Training is sensitive to initialization/batch order.
2. **Magnitude quantization**: Q4/Q8 per-weight with per-group scales
   needs verification across 29 layers + continuations.
3. **Attention compression**: only FFN is sieved (78% of params).
   Attention ternary works at PPL 23-30 (s190) but not yet integrated.

## Assets

| Asset | Path |
|-------|------|
| Lambda tracer | `scripts/experiments/lambda_tracer.py` |
| Binding-prep rank sweep | `scripts/experiments/binding_prep_lowrank.py` |
| Multi-projection melt | `scripts/experiments/multi_projection_melt.py` |
| Confidence gate | `scripts/experiments/confidence_gate.py` |
| Mode geometry | `scripts/experiments/mode_geometry.py` |
| Ternary weight interface | `scripts/experiments/ternary_weight_interface.py` |
| Crystal sieve pipeline | `scripts/experiments/crystal_sieve_pipeline.py` |
| β-expansion | `scripts/experiments/beta_expansion.py` |
| Ternary verification | `scripts/experiments/ternary_pipeline_verify.py` |
