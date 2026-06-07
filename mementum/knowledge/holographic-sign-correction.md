---
title: "Holographic Sign Correction & Crystal ECC"
status: active
category: foundational
tags: [holographic, crystal, ecc, signs, td, compression, error-correction, sieve]
related:
  - score-matching-compression.md
  - crystal-sieve-architecture.md
  - td-oscillation-problem.md
  - crystal-multi-tree.md
  - explore/holographic-state-machine.md
depends-on:
  - crystal-universality.md
  - score-matching-compression.md
created: session 199
---

# Holographic Sign Correction & Crystal ECC

> Session 199. TD (TernaryDescent) for sieve sign correction is dead.
> Three experiments, three failure modes: gradient-based sign optimization
> cannot work through 29 cascaded layers. The correct formulation is
> holographic recording (direct inverse) gated by crystal ECC (dimensional
> projection parity checks).

## TD Autopsy

### v4: Zero flips (joint gradient clipping)

```
clip_grad_norm_(all_4.4B_params, 1.0)
per_param_gradient ≈ 1/√(4.4×10⁹) ≈ 1.5×10⁻⁵
displacement_per_step = lr × grad = 1e-3 × 1.5e-5 = 1.5e-8
steps_to_flip = 1.0 / 1.5e-8 = 70,000,000
available_steps = 200
```

Result: v4 = v3b exactly (1.44x PPL). TD did nothing; LoRA did all work.

### v4c: Catastrophic flips (per-tensor clipping)

Per-tensor clip + Adam lr=1e-3 + init at 0.01: TD achieved 4.36% flips.
Result: **192x PPL, 0 facts.** The flips are real but destructive.

### Why gradient-based sign correction fails

1. **Gradient dilution.** The loss is measured at the output. Sign
   decisions are 29 layers upstream. Each Jacobian dilutes the signal.
   Local information needed for sign decisions is lost in global backprop.

2. **Catastrophic cascade.** Flipping one sign changes W by ±2|w|.
   Across 29 sieved layers, even a few percent of flips destroy the
   holographic interference pattern entirely.

3. **No coherence constraint.** TD flips wherever gradient points,
   regardless of whether the flip preserves the crystal topology.
   v14/v15 TD oscillated precisely at positions where the crystal is
   ambiguous (bridge nodes W and Y from the multi-tree structure).

## The Holographic Inverse

Sign correction is a **recording** problem, not an optimization problem.

In a hologram:
- Recording: reference beam × object beam → fringe pattern
- Reconstruction: reference beam × fringe pattern → object image

In the sieve:
- Reference beam: actual input to projection (from sieved model, corrupted)
- Object beam: desired output of projection (from teacher)
- Fringe pattern: `sign(correlation(reference, object))`
- Optimal signs: directly computed, no backprop needed

```python
# For each sieved projection:
sieve_input = capture_from_forward_pass()      # corrupted input
teacher_output = original_weight @ sieve_input  # what teacher produces
error = teacher_output - sieve_output
flip_benefit[i,j] = -2 * sign[i,j] * mag[i,j] * Σ_k x_k[j] * error_k[i]
# Positive benefit = flip reduces error
```

### Error Source

At the single-layer level, sieve signs ARE teacher signs at active positions:
`sign(W) × |W| × mask = W × mask`. No sign is "wrong."

The error comes from:
1. **Masked positions** (50%): teacher uses them, sieve zeros them
2. **Cascade corruption**: prior sieved layers change the input activations

Sign flips at active positions can partially compensate for masked losses
by redirecting their contribution.

### Tautological Target Bug (session 199 discovery)

First prototype used `teacher_signs * magnitudes @ sieve_input` as target.
Since `teacher_signs * magnitudes = signs * magnitudes` (they're the same
before any flips), this computes `sieve_output` vs `sieve_output` = zero
error. Correlation sign is then noise → 50% disagree rate.

**Fix:** Store FULL original weight (including unmasked positions).
The error is then `full_W @ x - (signs * magnitudes) @ x`, which captures
the contribution of masked-out positions.

## Crystal ECC: Error-Correcting Code from Dimensional Projections

The crystal's eigenvalue hierarchy constrains valid sign patterns:

```
8D crystal (KIBC + DWYS + WHNF)
  ↓ project to 6D → parity check (eigenvalue ratios)
    ↓ project to 5D → parity check
      ↓ project to 4D → parity check (KIBC basis, φ^(4/5) ratios)
        ↓ project to 3D → parity check (minimal topology)
```

### The Code Space

The sign pattern's correlation matrix has eigenvalues:
```
C = sign(W) @ sign(W).T / n_cols
eigenvalues(C) → should follow λ_k = C · φ^(-s·β_k)
```

A sign flip that moves eigenvalue ratios AWAY from φ^(p/q) is an error.
A flip that maintains or improves the ratios is crystal-coherent.

### Crystal Health Metric

```python
def crystal_health(signs):
    C = sign(W) @ sign(W).T / n_cols
    eigvals = eigendecompose(C)
    observed_ratios = eigvals[:4] / eigvals[0]
    predicted_ratios = [φ^(-4/5 * β_k) for β_k in [0, 1, 1+φ, 2+φ]]
    health = correlation(observed, predicted)
    return health
```

### ECC Algorithm

```
1. Compute flip candidates from proper error signal (holographic recording)
2. Rank by error reduction benefit
3. Measure crystal health BEFORE proposed flips
4. Apply flips, measure health AFTER
5. If health degrades > threshold:
     Binary search for largest subset maintaining coherence
6. Apply only crystal-coherent flips
7. LoRA + score matching for continuous magnitude correction
```

### Connection to TD Oscillation (v14/v15)

TD oscillates at positions where the gradient gives conflicting signals
across batches. These are EXACTLY the positions where the crystal parity
check fails — the bridge nodes (W, Y) that belong to multiple trees.

The crystal ECC resolves oscillation structurally: positions where the
crystal is ambiguous (bridge nodes) are rejected by the parity check,
while positions with clear crystal allegiance get flipped if beneficial.

## Experimental Status

Crystal ECC experiment running (session 199):
`scripts/experiments/crystal_ecc_sign_correction.py`

Key design choices:
- Full original weight as holographic target (captures mask error)
- Per-position flip benefit from error × input correlation
- Crystal eigenvalue health gate with binary search fallback
- Max 5% flip rate per projection (conservative)
- LoRA + SM phase 2 for magnitude correction

### Comparison Targets

| Method | PPL | Mechanism |
|--------|-----|-----------|
| Sieve only | 2.27x | Baseline |
| v3b (LoRA+SM) | 1.44x | Continuous correction only |
| v4c (TD+LoRA) | 192x | Sign flips + continuous (BROKEN) |
| Crystal ECC + LoRA | ??? | Crystal-gated flips + continuous |

## Theoretical Connections

| Concept | In ECC terms |
|---------|--------------|
| Crystal cosine matrix | Generator matrix of the code |
| Eigenvalue ratios | Parity check equations |
| Dimensional projections | Syndrome computation |
| Bridge nodes (W, Y) | Erasure positions (known ambiguous) |
| Flip benefit | Channel likelihood ratio |
| Crystal health gate | Syndrome-based decoding |
| v14/v15 oscillators | Decoding failures at erasure positions |
