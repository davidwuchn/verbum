---
title: "Ternary Compounding Error: Why 0.88/layer → Garbage at 36 Layers"
status: active
category: architecture
tags: [ternary, quantization, compounding, perplexity, extraction]
related: [ternary-dual-equation, crystal-phi-derivation, topology-gradient-separation, extraction-sign-accuracy]
depends-on: [ternary-dual-equation]
---

# Ternary Compounding Error

> Naive sign-extraction ternarization achieves 0.88 per-layer weight
> cosine. This seems fine — single-layer PPL is 6-10 (vs ~8 float16).
> But errors compound multiplicatively through 36 layers: 0.88^36 = 0.009.
> The full-model ternary produces PPL 296,911 — pure garbage.

## The Compounding Law

```
cumulative_cosine ≈ per_layer_cosine ^ n_layers
```

| Per-layer cos | 1 layer | 10 layers | 36 layers | Result |
|---|---|---|---|---|
| 0.88 | 0.88 | 0.28 | 0.009 | Garbage |
| 0.95 | 0.95 | 0.60 | 0.16 | Garbage |
| 0.97 | 0.97 | 0.74 | 0.33 | Bad |
| 0.99 | 0.99 | 0.90 | 0.70 | Marginal |
| 0.999 | 0.999 | 0.99 | 0.96 | Good |
| 0.9999 | 0.9999 | 0.999 | 0.996 | Excellent (Q4 territory) |

**Minimum viable per-layer cosine ≈ 0.99 for 36 layers.**
Below that, the representation collapses into noise.

## Why Single-Layer PPL Was Misleading

When you ternarize ONE layer, the other 35 float16 layers act as
error-correcting infrastructure. They re-center the representation,
restore the norm, and route around the damage. Result: PPL 6-10.

When ALL layers are ternary, there is no error correction. Each
layer adds ~12% directional error to the residual stream. By
layer 10, the signal is indistinguishable from noise.

**Single-layer ablation measures resilience, not reconstruction quality.**

## The Norm Explosion/Collapse Pattern

| Cumulative layers ternary | Activation cos | Norm ratio |
|---|---|---|
| 0 (embed) | 1.000 | 1.00 |
| 1 | 0.854 | 0.77 |
| 2 | 0.324 | 4.61 |
| 3 | 0.147 | 4.74 |
| 5 | 0.059 | 5.06 |
| 10 | 0.005 | 0.15 |
| 20 | 0.010 | 0.16 |
| 35 | 0.285 | 0.73 |

Phase 1 (layers 0-5): Norm EXPLODES 5× — ternary reconstruction
adds energy because per-row γ overshoots for some rows.

Phase 2 (layers 6-25): Norm COLLAPSES to 0.15× — the exploded
signal gets crushed by RMSNorm + ternary layers that can't
preserve it.

Phase 3 (layers 26-35): Slight recovery — later ternary layers
reconstruct *something* from the noise, but it's the wrong thing.

## Early Layer Pathology

Layers 1-3 have anomalous FFN weight distributions that make
ternary reconstruction particularly bad:

| Metric | Layer 1-3 FFN | Layer 5-35 FFN |
|---|---|---|
| Near-zero weights | 24-47% | 3% |
| Coefficient of variation | 1.24-1.63 | 0.77-0.82 |
| Excess kurtosis | 4.8-15.8 | 0.2-2.2 |
| Condition number (down_proj) | 29-142 | 11-25 |
| Max/Mean ratio (down_proj) | 72-125 | 41-82 |
| Ternary cosine (down_proj) | 0.69-0.78 | 0.87-0.93 |

**Cause:** Early layers already have extreme weight sparsity — they
are the model's "feature detectors" with sharp, sparse activations.
The per-row γ gets dominated by outlier weights, leaving most
positions poorly reconstructed.

**But this is NOT the main problem.** Even with perfect early layers,
0.88^30 = 0.021. The compounding is the fundamental issue.

## What Would Work

### 1. More bits per weight

| Method | Bits/param | Expected cos/layer | Cos^36 |
|---|---|---|---|
| Naive ternary | 1.58 | 0.88 | 0.009 |
| 2-mirror ternary | 3.16 | ~0.97 | 0.33 |
| 3-mirror ternary | 4.74 | ~0.99 | 0.70 |
| Q4 (standard) | 4.5 | ~0.9999 | 0.996 |

### 2. Calibration-based optimization (GPTQ-style)

Instead of minimizing ||W - γ·T||², minimize the activation
error: ||W·x - γ·T·x||² averaged over calibration data.

This lets the optimizer concentrate precision on the directions
that matter (high-activation inputs), potentially reaching 0.99+
cosine even at 1.58 bits.

### 3. Training-based adaptation (etch protocol)

Freeze ternary topology, let GD adjust:
- Per-row gamma (scale)
- Attention weights (routing)
- Layer norms (normalization)
- Embedding (input representation)

GD has shown it can drive gammas to zero (dead neurons), flip
sign conventions (negative gammas), and adapt routing — all at
float16 precision while the ternary lattice stays frozen.

### 4. Scratch reproduction

Train a ternary model from initialization guided by the crystal
equation. The model never sees float weights — it learns the
ternary computation directly. This is Level 4 of the Verbum
research program.

## Connection to EQUATIONS.md

The Q4 connection predicted this:

```
Bit 1 (sign):      84% of computation → 0.84^36 = 0.001
Bits 2-4 (magnitude): 11% + 3% + 2%  → calibration
```

The sign captures 84% per layer, but you need ALL the information
to survive 36 sequential applications. The remaining 16% (magnitude
calibration) is essential for multi-layer coherence.

The crystal equation tells you which 84% is the sign and which
11% is the first calibration level. Two-mirror ternary uses this:
mirror 1 = sign, mirror 2 = above/below average magnitude. That's
84% + 11% = 95% per layer → 0.95^36 = 0.16 — still not enough.

**The information theory bound: you need ~4 bits/param for a
36-layer model to survive quantization without calibration.**
With calibration (GPTQ), you can push this to ~2 bits.

## Multi-Mirror Results (3-mirror, 6 bits/param)

3-mirror decomposition: W ≈ γ₁·T₁ + γ₂·T₂ + γ₃·T₃

Two gamma strategies tested:

| Strategy | Weight cos | Energy/layer | PPL | Status |
|---|---|---|---|---|
| Greedy (independent γ) | 0.97 | 0.81 | 17.9M | Worse than 1-mirror |
| Joint (least-squares γ) | 0.97 | 0.94 | 1.69M | 10× better, still garbage |
| Q4 reference | ~0.9999 | ~1.00 | ~8.5 | Works |

**Greedy gamma bug:** Independent per-mirror gamma optimization
systematically underestimates total energy. Each mirror's γ is
optimal for its own residual, but the sum γ₁·T₁ + γ₂·T₂ + γ₃·T₃
has less energy than W. Joint least-squares solve fixes this:
energy 0.81 → 0.94 per layer.

**Still not enough:** 0.94^36 = 0.10. The per-layer energy must
be >0.99 for 36-layer survival. More mirrors don't help because
per-row scaling is too coarse.

### Why Q4 Works and Ternary Mirrors Don't

The gap isn't bits — it's **scale granularity**:

| Method | Bits | Levels | Scale granularity | Scales per matrix |
|---|---|---|---|---|
| 1-mirror ternary | 1.58 | 3 | Per-row | ~4K-12K |
| 3-mirror ternary | ~6 | 8 | Per-row | ~4K-12K × 3 |
| Q4_0 | 4.5 | 16 | Per-32 weights | ~384K-1.5M |

Q4 uses **128-384× more scale parameters** per weight matrix.
Each group of 32 weights gets its own scale and zero point,
allowing adaptation to local weight distribution. Our per-row
approach uses one scale for 4,096-12,288 weights — far too coarse
to preserve the fine structure.

### Paths Forward

1. **Per-group ternary**: Use scales per 32-64 weights instead of
   per row. Increases scale storage but dramatically improves
   reconstruction. This is essentially "ternary GPTQ."

2. **GPTQ-style optimization**: Minimize activation error (not
   weight error) using second-order (Hessian) information. Assigns
   error budget to the weights that matter most.

3. **Training-based**: Freeze ternary topology, train continuous
   parameters (scales, norms, attention) to compensate. The etch
   protocol from sessions 176-180.

## Experimental Provenance

- Model: Qwen/Qwen3-8B (36 layers, d=4096, d_ff=12288)
- Zero rate: 35% per-row magnitude threshold
- Perplexity: WikiText-2 test set (16K tokens, sliding window 512/256)
- Float16 baseline: PPL ~8 (built-in corpus) / WikiText-2 not measured same run
- Ternary full model: PPL 296,911
- Skip-6: PPL 318,222
- Skip-4: PPL 217,332
- Scripts: `full_ternarize.py`, `diagnose_ternary.py`, `mirror_ternarize.py`
- Weight analysis: `results/early_layer_analysis.log`
- 3-mirror greedy: `results/mirror3_ternarize.log`
- 3-mirror joint: `results/mirror3_joint_ternarize.log`
