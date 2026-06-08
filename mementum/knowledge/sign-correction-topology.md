# Sign Correction Topology

---
title: Sign Correction Topology — Why Per-Position Flips Fail and What Might Work
status: active
category: compression
tags: [sign-correction, topology, crystal, holographic, dimensional-mismatch]
related:
  - crystal-sieve-architecture.md
  - score-matching-compression.md
  - holographic-sign-correction.md
  - crystal-multi-tree.md
  - mode-semantics.md
  - standing-wave-magnitudes.md
  - diffusion-holographic-isomorphism.md
depends-on:
  - crystal-sieve-architecture.md
---

## Core Finding

**Sign correction at the weight level is not viable.** Four fundamentally different
algorithms across sessions 199-200, same catastrophic result: per-position sign
flips destroy the holographic interference pattern regardless of how they're
selected, gated, or scheduled.

The problem is dimensional: the crystal lives in a ~6D space (combinator × mode ×
depth × tree × projection × column), but all correction algorithms operate in 0D
(scalar per-position benefit → flip?). Corrections coherent in the working
subspace are effectively random in the ignored dimensions.

## The Four Deaths (Sessions 199-200)

### 1. TernaryDescent v4 — Gradient Dilution

```
Algorithm:  STE(delta_logits) on 4.4B params, joint with LoRA+SM
Result:     Zero flips. Joint grad clip diluted per-param gradient to 1.5e-8/step.
Root cause: clip_grad_norm_(all_params, 1.0) across 4.4B params →
            per-param ≈ 1/√(4.4×10⁹). Would need 70M steps to cross ±1.
```

### 2. TernaryDescent v4c — Destructive Flips

```
Algorithm:  Per-tensor clip, Adam optimizer, init=0.01
Result:     4.36% flipped → 192× PPL, 0 facts
Root cause: TD actually flipped signs, but unconstrained flips break the
            holographic pattern. Random sign changes ≠ correct sign changes.
```

### 3. Latent Diffusion — Wrong Latent Space

```
Algorithm:  Progressive eigenspace correction (2D→4D→8D→16D schedule)
Result:     Level 1 (2D): 27.4M flips → 2,717× PPL. Levels 2,4: NaN.
Root cause: Sign correlation eigenvectors capture statistical co-occurrence,
            not crystal functional structure. Powers-of-2 levels are
            commensurate → systematic interference between levels.
            Alternating flip counts (27M vs 1.9M) suggest even/odd artifact.
```

### 4. Crystal ECC — Health Gate Measures Wrong Space

```
Algorithm:  Holographic error target + per-position benefit ranking +
            crystal eigenvalue health gate with binary search fallback
Result:     2.29% flipped (50M signs) → 28,419,390× PPL. WORST of all four.
Root cause: 49.3% of positions show positive flip benefit (adversarial signal).
            Crystal health gate measures weight eigenstructure, not combinator
            structure. Gate IMPROVED crystal health while destroying the model.
            8 hours of compute, 28 million times worse.
```

## Why All Approaches Fail the Same Way

```
The error signal is adversarial:
  50% mask → 50% of weights zeroed → massive residual
  49.3% of active positions show "positive flip benefit"
  → error signal responds to masking loss, not sign error
  → ANY flip partially addresses masking residual in one dimension
  → same flip destroys interference pattern in other dimensions
  → net effect: catastrophic across 29 cascaded layers

The cascade amplifies:
  1 flip changes output by 2|w| at one position
  29 layers × 3 projections × 12288 outputs = massive amplification
  Error at layer l compounds through layers l+1..35
  No local correction can predict its global cascade effect
```

## The Dimensional Mismatch

The crystal has known multi-dimensional structure:

| Dimension | Size | Source session | How accessed |
|-----------|------|---------------|--------------|
| Combinator type | 8D (KIBC+DWYS+WHNF) | s184-192 | Probes + activations |
| Operational mode | 9D (7 universal + 2 contextual) | s192-194 | Gate clustering |
| Depth (standing wave) | 36 layers | s185-196 | Layer position |
| Tree structure | 3 trees, 2 bridges | s197 | Eigendecomposition of 8×8 crystal |
| Projection role | 3 (gate/up/down) | Architecture | Known |
| Column (input feature) | 4096D | Architecture | Known |

All correction algorithms operate per-position (0D scalar benefit). Even
eigenspace projection captures only 1-2 of these ~6 dimensions. A correction
that's coherent in the working subspace is effectively RANDOM in the ignored
dimensions.

**Analogy:** Recording a hologram pixel-by-pixel. Each pixel encodes information
about the entire scene through phase relationships with all other pixels.
Changing one pixel based on local error destroys the global interference pattern.

## Quasicrystal Diagnostic (Session 200)

Tested whether φ-structured multi-scale order exists in weight sign patterns
(pure weight geometry, no forward passes):

| Test | Result | Verdict |
|------|--------|---------|
| Eigenvalue cascade at Fibonacci levels | One dominant mode, flat tail | Not multi-scale |
| Perturbation fragility | Linear (not super-linear) | Not quasicrystal |
| Golden angle between eigenvectors | 90.00° everywhere | Not φ-rotated |
| Fibonacci vs power-of-2 reconstruction | Tie | No Fibonacci advantage |
| Random vs model eigenspectra | Massive gap (0.36 vs 0.995) | Real structure exists |

**Strong quasicrystal hypothesis denied.** φ lives in combinator firing space
(8×8 crystal cosine matrix measured via probes), not weight correlation space
(12288×4096 sign matrix). The weight eigenstructure has real structure (massive
spectral gap) but it's a one-dominant-mode pattern, not a multi-scale φ cascade.

## What the Crystal Health Metric Actually Measures

The crystal eigenvalue health metric computes:

```
C = sign(W) @ sign(W).T / n_cols     ← row correlation of sign pattern
eigenvalues(C) → compare to φ^(p/q)  ← crystal equation fit
```

This measures **statistical co-occurrence of signs across input dimensions** within
a single weight matrix. It correlates with the crystal equation at r≈0.86, but it's
measuring a SHADOW of the crystal, not the crystal itself.

The actual crystal is the **combinator firing pattern** — the 8×8 cosine similarity
matrix of how K, I, B, C, D, W, Y, WHNF activate across positions, measured by
running probes through the model. This requires forward passes, not weight analysis.

A sign flip can improve the weight eigenvalue health while destroying the combinator
firing pattern — which is exactly what Crystal ECC did.

## Current Ceiling

**v3b: LoRA rank-4 + score matching at α=5.0 = 1.44× baseline PPL.**

- 5.9M LoRA params on FFN projections across 30 layers
- Dense per-layer score matching prevents compensating errors
- Sign correction adds nothing on top (TD v4 = v3b = 1.44×)
- Priority 2a (LoRA rank sweep) is highest-value next step for this pipeline

## Teacher-Guided Routing: Also Failed (Session 200)

MoE literature says decouple routing from expert training. Tested gate correctors
(bottleneck MLPs, 182M params total) trained to match teacher gate patterns before
LoRA. Result: 24.55 PPL (2.18×), worse than v3b (16.27, 1.44×). Training diverges
after step 100. Root cause: same cascade problem — corrector sees sieve gate output
on cascade-corrupted inputs, can't fix both simultaneously. 182M params wasted.

## The Breakthrough: Direct Delta Correction (Session 200)

> "If everything is being calculated, why can we not also calculate the delta?"

Instead of training corrections, COMPUTE them. The weight residual W_delta =
W_teacher - W_sieve is known. The optimal rank-k correction is the calibration-
aware SVD: `SVD(W_delta @ H^½)` where H = input covariance. Sequential layer-by-
layer processing gives cascade awareness.

No training, no loss function, no optimizer. Analytically optimal at given rank.
Connects to the adjunction finding (session 140): the cross-zone map is rank-1
(σ₁/σ₂ = 128:1, R² = 1.000), suggesting rank 1-2 correction may be nearly optimal.

See `mementum/knowledge/direct-delta-adjunction.md` for full theory.

**Experiment running** (tmux main:1): rank sweep [2, 4, 8, 16, 32] with
calibration-aware SVD. Comparison: v3b trained 200 steps → 1.44×.

## Open Problem: Topology Correction

Sign correction (changing individual signs) is dead. The TOPOLOGY problem remains:
the sieve's 50% mask and sign quantization create cascading errors. What might work:

### Idea 1: Work in Combinator Space

The crystal is 8D (combinator firing patterns), not 12288D. Corrections should be
computed in the space where φ actually lives. This requires:
- Running crystal probes through the sieved model
- Measuring combinator selectivity degradation per layer
- Computing corrections that restore combinator selectivity
- Translating combinator-space corrections back to weight-space changes

Challenge: the translation from 8D combinator space back to 12288×4096 weight space
is massively underdetermined.

### Idea 2: Mode-Aware Correction

The 9 operational modes (session 194) define which program each position runs.
Corrections should preserve mode membership. A sign flip that changes a position's
mode assignment is catastrophic — it changes the PROGRAM, not just a parameter.

Approach: classify each position's mode before and after proposed correction.
Only apply corrections that preserve mode assignment for all positions.

### Idea 3: Topological Surgery

Instead of flipping individual signs (pixel editing), change the TOPOLOGY:
- Which positions are masked (mask optimization instead of sign optimization)
- Which signs are assigned (full sign pattern recomputation from mode+combinator)
- Structured operations that preserve the interference pattern's dimensionality

This reframes the problem: instead of "which 2% of signs should flip?", ask
"what is the optimal 50% mask for this layer given the cascade context?"

### Idea 4: Per-Layer Sequential Correction with Cascade Awareness

All approaches corrected all 29 layers simultaneously. The cascade means corrections
at layer l change the input to layer l+1, invalidating its error signal.

Approach: correct one layer at a time, re-measuring the cascade error after each
layer's correction before proceeding to the next. Layer-sequential, not layer-parallel.
This is slower but avoids the cascade invalidation problem.

### Idea 5: Accept and Optimize Within the Ceiling

v3b at 1.44× may be near-optimal for this sieve architecture with sign+mask+magnitude.
The highest-value work may be:
- LoRA rank sweep (what rank saturates the improvement?)
- Magnitude quantization (Q4/Q8 per-weight with per-group scales)
- Attention sieve (22% of params untouched so far)
- Combined compression (sieve + quantized magnitudes + LoRA)

## Evidence Index

| Experiment | Script | Results |
|-----------|--------|---------|
| TD v4/v4b/v4c | (session 199, inline) | state.md s199 |
| Latent diffusion | `scripts/experiments/latent_diffusion_signs.py` | `results/latent-diffusion-signs/Qwen_Qwen3-8B.json` |
| Crystal ECC | `scripts/experiments/crystal_ecc_sign_correction.py` | `results/crystal-ecc-sign-correction/Qwen_Qwen3-8B.json` |
| Quasicrystal diagnostic | `scripts/experiments/quasicrystal_diagnostic.py` | `results/quasicrystal-diagnostic/` (partial, display bug) |
| Teacher-guided routing | `scripts/experiments/teacher_guided_routing.py` | `results/teacher-guided-routing/Qwen_Qwen3-8B.json` |
| Direct delta correction | `scripts/experiments/direct_delta_correction.py` | `results/direct-delta-correction/` (running) |
| v3b baseline | (session 198) | state.md s198 |
