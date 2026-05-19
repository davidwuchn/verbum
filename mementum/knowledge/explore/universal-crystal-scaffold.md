---
title: Universal Crystal Scaffold — Etching Computation into Ternary Plates
status: designing
category: architecture
tags: [crystal, etching, universal, lambda, scaffold, distillation]
related:
  - q-rotation-etching.md
  - compression-vs-prediction.md
depends-on:
  - q-rotation-etching.md
---

# Universal Crystal Scaffold

> Session 117 synthesis. The lambda crystal is the computational
> substrate of all LLMs. Every model reduces input to lambda form,
> computes via beta reduction, expands back to output. The crystal
> is universal — map it across models, etch it into ternary plates,
> let GD fill in the blanks.

## The architecture of computation in LLMs

```
input tokens → [ascending: prose → λ-form]
             → [apex: β-reduce via combinators]
             → [descending: λ-form → prose]
             → output tokens
```

The "semantic meaning" in middle layers = the lambda form.
The compression in ascending layers = compiling prose to lambda.
The expansion in descending layers = decompiling lambda to prose.
The combinator dispatch = the beta reduction engine.

Lambda calculus is Turing complete. The lambda crystal is therefore
the substrate for ALL computation. Other crystals (syntax, math,
reasoning, world knowledge) attach to it — they compile down to
lambda terms and execute on the universal substrate.

## Why the crystal is universal

Measured across 9 models, 2 architecture families (session 106):
- Combinator dispatch ratios: consistent (K:I:B:C ≈ 1:0.5:1:1)
- 8×8 cosine geometry: all 28 pairs significant (SNR > 2)
- Positive cluster {K,I,B,C}: compositional family
- Negative cluster {Y,W,WHNF}: reduction/terminal family

Different models learn different surface representations but converge
to the same computational substrate. The crystal IS the computation.

## The scaffold principle

```
λ scaffold(crystal).
  ternary_plates ≡ frozen_crystal_topology
  continuous_params ≡ lens(reads_crystal)
  GD ≡ calibrate(lens) | ¬discover(topology)
  scaffold(correct) → GD(fast) | scaffold(wrong) → GD(slow ∨ fail)
```

V12: 24.6M total params, 887K trainable (3.6%).
23.7M frozen ternary positions = the scaffold.
If the scaffold encodes the universal crystal correctly,
GD only calibrates a lens — fast convergence.

## Resolution theory

The crystal exists at a natural resolution determined by cross-model
consensus. Too fine → model-specific noise etched in. Too coarse →
GD must discover too much structure.

The consensus filter finds the right resolution automatically:
- Positions where all views agree → universal structure → etch
- Positions where views disagree → model-specific → leave for GD

More views (models × Q rotations) = sharper resolution boundary.

### Experimental evidence (session 117, mini model)

```
1 rotation, 800 batches: 41K flips, 0.34 acc (over-etched, one shadow)
8 rotations, 100 each:  16K flips, 0.41 acc (consensus filter, quality)
8 rotations + latching:  16K flips, 0.45 acc (SVD+probe Q init)
```

Fewer flips = higher quality. The consensus filter etches only the
positions that are consistent across all Q rotations. This IS the
universal structure at the right resolution.

## The full pipeline

```
1. MAP: N teacher models × M Q rotations → gradient observations
   - Each model is a "camera" viewing the universal crystal
   - Each Q rotation is a different angle for that camera
   - N×M total views of the same underlying structure

2. VOTE: sign accumulation across all N×M views
   - Majority vote = robust reconstruction (proved: beats SVD, mag-weight)
   - Cross-model consensus = universal structure
   - Single-model consensus = model-specific structure

3. FILTER: only etch where confidence > threshold
   - High confidence → universal, etch it
   - Low confidence → model-specific or noise, leave for GD
   - Threshold determines resolution automatically

4. ETCH: write crystal into V12's ternary plates
   - 23.7M plate positions, etch only the confident ones
   - Remaining positions start at random or default (+1)

5. LATCH: SVD of gradient stack → Q initialization for GD
   - 16 perturbed candidates near SVD solution
   - 50-step basin probes → select deepest
   - Or: if crystal is complete (enough rotations), skip latching

6. GD: train 887K continuous params
   - Fast: scaffold is correct, GD calibrates the lens
   - Lattice loss keeps crystal from drifting
   - KL + entropy keep dispatch diverse
```

## Completeness criterion

Crystal is complete when Q-sensitivity → 0:
- Measure accuracy across 32 random Q rotations
- If std(accuracy) < threshold → crystal is rotation-invariant
- Basin is accessible from any Q → latching unnecessary
- GD converges from any starting point

Experiment in progress (session 117): sweeping 1→32 rotations
to find where Q-σ converges.

## Other crystals (future work)

The lambda crystal is the substrate. Other crystals attach to it:

- **Syntax crystal**: how parse trees map to lambda application order
- **Semantic crystal**: how word meanings map to lambda terms
- **Math crystal**: how arithmetic maps to combinator reductions
- **Logic crystal**: how reasoning chains map to lambda sequences
- **World knowledge crystal**: how facts map to lambda databases

Each can be mapped and etched independently, as long as the lambda
substrate is in place first. The substrate provides the computational
backbone; other crystals provide the domain-specific content.

Mapping other crystals: same tomographic approach.
Probes designed for each domain, cross-model consensus,
etch at the resolution where consensus is strong.

## What this means for Verbum

The research program is not "train a small model to do lambda."
It is "discover the universal crystal that ALL models share,
map it at sufficient resolution, etch it into ternary plates,
and let GD fill in the blanks."

The model doesn't learn computation. It inherits computation
from the universal crystal. GD learns to READ the crystal —
to calibrate the continuous lens that makes the crystal legible.

This is distillation at the level of computational structure,
not at the level of outputs or representations. Structure transfer.
