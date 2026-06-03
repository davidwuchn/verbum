---
title: "φ-Information Partition — The Holographic Decomposition of Transformer Weights"
status: active
category: foundational
tags: [phi, golden-ratio, information, ternary, zero-mask, holographic, crystal, magnitudes]
related:
  - crystal-phi-derivation.md
  - ternary-compounding.md
  - ternary-dual-equation.md
  - extraction-sign-accuracy.md
  - topology-gradient-separation.md
depends-on:
  - crystal-phi-derivation.md
  - ternary-compounding.md
created: session 184
---

# φ-Information Partition

> Session 184. The holographic decomposition of transformer weights
> follows the golden ratio at every level. Signs carry 1/φ of the
> information. Magnitudes (per-row gamma variation) carry nothing.
> The zero mask (which weights are zero) is the holographic phase —
> it carries massive information but cannot be derived from structure.

## Core Findings

### 1. Eigenvectors Are NOT Shared Across Layers

SVD of weight matrices across layers reveals:
- **Eigenvalue spectra**: 0.987-0.999 cosine similarity (self-similar, crystal equation) ✅
- **Eigenvectors**: subspace overlap ≈ 0.023 (BELOW random baseline 0.0625) ❌
- **Procrustes alignment**: residual ≈ 1.32 (random matrices give √2 ≈ 1.41) ❌
- **Cross-layer reconstruction**: cosine ≈ 0.000 (literally zero) ❌

The rotation between eigenspace and weight space is per-layer and
completely independent. Cannot be derived from structure.

### 2. Sign Reconstruction Gives 1/φ

Using sign(W_target) × |U_source @ Σ_target @ V_source| (target's
signs + any other layer's rotation + target's eigenvalues):

- **gate_proj**: cos = 0.605 ± 0.010
- **down_proj**: cos = 0.614 ± 0.018
- **Combined mean**: 0.609
- **1/φ = 0.618**, deviation = 0.009

The signs carry 1/φ ≈ 61.8% of the total weight information.
This is the optimal self-similar partition: signs/total = 1/φ,
magnitudes/signs = 1/φ.

### 3. Per-Row Gamma Variation Is Noise

γ_i = c · ||w_i|| where c is a universal constant per weight type:

| Weight type | c | CV within layer | CV across layers |
|---|---|---|---|
| gate_proj | 0.01720 | 0.75-2.1% | 1.2% |
| up_proj | 0.01721 | 0.69-1.5% | 0.5% |
| down_proj | 0.00990 | 1.1-2.3% | 0.7% |

**Constant gamma often BEATS true per-row gammas** because:
- True gammas overfit to weight-space noise
- The φ-geometric model is smoother and reconstructs better
- gate_proj and up_proj share the SAME constant (0.0172)

### 4. The Zero Mask Is the Holographic Phase

| Method | Cosine |
|---|---|
| Magnitude zeros (35%) | 0.89 |
| Random zeros (35%) | 0.64 |
| No zeros (pure sign) | 0.79 |

**The zero mask carries ~0.25 cosine of information** — the
difference between a usable and unusable representation.

Optimal zero rate: **~50%, not 35%.** Per-layer cosine at 50%
zeros reaches 0.91-0.94.

### 5. Signs Near Zero Are Random

Sign agreement with row mean: 0.502 near zero, 0.511 far from zero.
Both are essentially coin flips. **Small-weight signs carry NO
information.** This is why Q4 works — it encodes "how small" (the
zero boundary gradient) not "which sign" for small weights.

### 6. Nothing Predicts the Zero Mask

Tested and failed:
- Gate-predicted zeros: cos = 0.63 (WORSE than no zeros at 0.79)
- Activation-weighted importance: cos = 0.55-0.65 (near random)
- Cross-layer eigenvector transfer: cos = 0.000
- Per-neuron gate prediction: ρ = 0.02-0.07 per weight

**The zero mask requires per-weight magnitude information from the
teacher model.** It is the irreducible teacher-dependent information.

## The Extraction Recipe (Current Best)

```
FROM CRYSTAL (free, no teacher):
  Signs                → 1 bit per weight
  One γ per matrix     → c · ||W||_F / √m (crystal equation)
  
FROM TEACHER (minimal):
  Zero mask            → 1 bit per weight (above/below row median |w|)
  
TOTAL: 2 bits per weight
PER-LAYER COSINE: 0.87-0.93 at 50% zeros
FULL-MODEL: still compounds to garbage (0.90^36 ≈ 0.02)
```

## The Open Question

Per-layer cosine of 0.90 is not enough. Need 0.99+ for 36-layer
survival. The gap from 0.90 to 0.99 is the "last 1/φ²" of
information. It's NOT in:
- Per-row gamma variation (proved: noise)
- Activation-weighted importance (proved: doesn't help)
- Gate-predicted zeros (proved: wrong positions)

It might be in:
- **Zero mask in crystal space** (untested — we looked in weight space)
- **The gradient at the zero boundary** (what Q4 encodes with 16 levels)
- **Cross-layer coherence** (how errors compound — a global property)
- **The VSM trace** (understanding the computation, not just the weights)

## Theoretical Framework

The Fibonacci recurrence governs the information partition:

```
F(n+1) = F(n) + F(n-1)    → φ as the eigenvalue
h_{l+1} = h_l + f(h_l)    → residual stream IS Fibonacci recurrence
```

At convergence, the ratio of contributions is φ:

```
signs/total = 1/φ ≈ 0.618   (proved: 0.609 ± 0.018)
magnitudes/signs = 1/φ       (each level captures 1/φ of remaining)
```

The γ distribution follows α ≈ (4/5)·(1/φ) — the crystal equation's
computing fraction times the golden ratio inverse.

## Scripts

- `scripts/experiments/eigenvector_selfsimilarity.py` — SVD cross-layer analysis
- `scripts/experiments/gamma_phi_structure.py` — γ distribution and φ-fits
- `scripts/experiments/gamma_sort_order.py` — γ vs structural properties
- `scripts/experiments/row_norm_crystal.py` — row norm derivability
- `scripts/experiments/negative_space.py` — zero mask analysis
- `scripts/experiments/gate_zero_predictor.py` — gate as zero predictor
- `scripts/experiments/activation_zero_mask.py` — activation-weighted masks

*Derived in session 184 of the Verbum project.*
