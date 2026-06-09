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

> ⚠️ **CAVEAT (session 208 audit #7 — read before trusting the 1.03×).** The
> headline **1.03× PPL "cascade absorbed"** is a **train/eval-contamination
> artifact**, not a stable compression result. An 8-seed reproducibility sweep
> (`scripts/experiments/crystal_sieve_repro.py`, `results/crystal-sieve-repro/`)
> shows: (1) the **sieve substrate is real and reproducible** — pre-melt 2.119× ±
> 0.004 (eval) / 1.907× ± 0.026 (held-out), near-deterministic; (2) the post-melt
> 1.03× is a **1/8 upper-tail draw** of a 0.971× ± 0.061 distribution, and 5/8
> seeds go *below* baseline because **6 of the 8 `EVAL_TEXTS` are duplicates of the
> 12 `CALIBRATION_TEXTS`** the melt trains on; (3) on **clean held-out text the
> same melted models read 10.87× ± 1.39** (every seed >9.3×) — the continuation
> melt **memorizes the calibration set and is net-harmful to generalization**
> (held-out 1.907× → 10.87×, ~5.7× worse than the raw sieve). Root cause: the
> CE-only melt is the ill-posed *endpoint* objective (`gtsm-search-space.md`);
> constant train loss (0.116) + exploding held-out PPL = compensating-error
> degeneracy. **The honest reproducible numbers are: sieve ≈ 1.9–2.1×, and the
> trained-correction fix is s198 v3b** (dense per-layer score matching + held-out +
> dolma → **1.44× held-out** on this same model) = audit #11. Treat "1.03×" below
> as **withdrawn**; the rank-32 continuation *parametrization* is fine, the CE
> *loss* + 12-text contaminated *eval* are not.

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
| 29-layer cascade (sieve only) | 2.12x PPL ✅ reproducible (s208: 2.119×±0.004) |
| + continuation residuals | ~~**1.03x PPL**~~ ❌ withdrawn (s208: contaminated eval; held-out **10.87×**) |
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

> ⚠️ **s208:** this section's thesis is **not supported held-out.** The CE-melted
> continuations reduce *contaminated* eval PPL (eval ⊂ calib) but raise **held-out**
> PPL ~5.7× (1.907× → 10.87×) — they memorize the calibration distribution rather
> than "absorb the cascade." A correction that genuinely absorbs the cascade needs
> a trajectory-matching loss (s198 v3b score matching, 1.44× held-out), not CE on
> 12 texts. The binding-preservation observation below still stands (it is an
> attention-pattern measurement, not a PPL claim).

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

**Proven quality**: ~~1.03x PPL at 29 sieved layers~~ ❌ **withdrawn (s208)** —
that number was on a contaminated eval; held-out is 10.87×. Reproducible quality
is the **sieve substrate ≈ 2× PPL** (held-out 1.907×); a real trained correction
needs dense score matching (s198 v3b, 1.44× held-out), not the CE melt here.
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
