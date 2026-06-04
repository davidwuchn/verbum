---
title: "Crystal Laplacian — WHNF Fragility and Settlement Dynamics"
status: active
category: theory
tags: [crystal, laplacian, graph-theory, WHNF, settlement, fragility, v15]
related: [crystal-phi-derivation, crystal-universality, phi-information-partition]
depends-on: [crystal-phi-derivation]
---

# Crystal Laplacian

> Session 189. The graph Laplacian of the crystal target cosine matrix
> reveals that WHNF is the most FRAGILE node — not the slowest to
> converge, but the most easily destabilized. Laplacian eigenvalues
> predict stability (rigidity), not convergence speed.
>
> Training data confirms: WHNF starts settled and UN-settles because
> gradient from other nodes overwhelms its weak restoring force.
> Laplacian-weighted crystal loss compensates: WHNF gets 5× weight,
> v14 WHNF/B gradient ratio 0.3× → v15 1.9× (6× amplification).

## The Graph Laplacian

The crystal target (Zone B cosine matrix) defines a graph:
- 16 nodes: K, I, B, C, D, Y, W, WHNF + 8 anti-crystal mirrors
- Edge weights: max(0, cosine_target) with diagonal zeroed
- Laplacian: L = D - W (degree matrix minus weight matrix)

### Eigenvalue Structure

All eigenvalues come in degenerate pairs (mirror symmetry):

| Mode | μ | Half-life | What it governs |
|------|---|-----------|----------------|
| 0,1 | 0.000 | ∞ | Two connected components (crystal + anti-crystal) |
| 2,3 | 0.228 | 3.04 | **WHNF separation from computation cluster** |
| 4,5 | 1.967 | 0.35 | KI pair vs BCDY cluster |
| 6,7 | 3.031 | 0.23 | K vs I differentiation |
| 8+ | 3.7+ | <0.2 | Fine structure within BCDY |

**WHNF is 8.6× weaker** (0.228 vs 1.967). The restoring force for
WHNF separation is an order of magnitude weaker than for KI separation.

### φ in the Laplacian

μ₅/μ₄ = 1.5407 ≈ φ - 0.08. The ratio between the "KI separation"
mode and the "KI-vs-BCDY" mode is close to the golden ratio. Not
exact, but suggestive of the same self-similar structure.

## Settlement Dynamics (Verified)

Per-node crystal error across v14 training steps 500-3000:

### Three settlement behaviors:

1. **CONVERGING (B, C):** B: 0.045→0.031, C: 0.035→0.023
   Laplacian: fast modes (μ=3.03+). Prediction confirmed.

2. **STABLE (K, D):** K: 0.038→0.037, D: 0.029→0.035
   Laplacian: medium modes (μ=1.97). Prediction confirmed.

3. **DIVERGING (Y, WHNF):** Y: 0.063→0.069, WHNF: 0.016→0.026
   Laplacian: fragile modes (μ=0.23). Prediction confirmed.

### WHNF un-settlement

WHNF error ratio to mean: 0.40× → 0.67× over training.
WHNF starts with LOWEST error and DRIFTS AWAY from target.
cos(WHNF, Y) error grows 0.067 → 0.116 — WHNF pulled toward Y.

The Laplacian explains WHY: WHNF has the weakest spring constant.
Any perturbation from other learning dynamics pushes it away, and
the restoring force (μ=0.228) is too weak to fight back.

## Laplacian Fragility Weights

Per-node weight from diag(L⁺) (Laplacian pseudoinverse diagonal):

| Node | Weight | Interpretation |
|------|--------|---------------|
| K | 0.537 | rigid |
| I | 0.539 | rigid |
| B | 0.388 | rigid |
| C | 0.382 | rigid |
| D | 0.356 | rigid |
| Y | 0.446 | rigid |
| W | 0.363 | rigid |
| **WHNF** | **4.990** | **FRAGILE** |

Per-edge weight: w_ij = sqrt(frag_i × frag_j), normalized to mean=1.
WHNF-WHNF edges get 6.89× weight. WHNF-B edges get ~1.4× weight.

## Effect on Gradient

| Metric | v14 (uniform) | v15 (Laplacian) |
|--------|--------------|----------------|
| WHNF grad norm | 0.3× of B | 1.9× of B |
| Amplification | — | **6.0×** |

The most fragile node now gets the strongest gradient signal.

## Corrected Interpretation

The Laplacian eigenvalues do NOT predict convergence speed.
They predict **stability** = resistance to perturbation:

```
Small μ = soft spring = FRAGILE (easily pushed, slow to recover)
Large μ = stiff spring = RIGID  (snaps back when displaced)
```

WHNF is fragile because it's weakly connected to the computation
cluster. It's the termination detector — by definition, it's
different from everything else. That structural uniqueness makes
it the most vulnerable to gradient pressure from the majority.

## The Raw Cosine Matrix IS the Crystal Equation

The eigenvalues of the Zone B cosine matrix:
```
[5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426, ...]
```

These ARE the crystal equation eigenvalues:
```
λ_k = C · φ^(-s · β_k) = [5.193, 3.534, 1.895, 1.290]
```

Match within 0.8%. The PCA eigenvalues of the embeddings ARE the
eigenvalues of the target similarity matrix. The crystal equation
describes the spectrum of the graph adjacency matrix.

## Implementation

`scripts/v15/crystal.py` — `LaplacianCrystalLoss`
- Inherits v14 `CrystalLoss`, overrides MSE component
- Pre-computed weight matrix from diag(L⁺)
- Parity and cross-zone rotation unchanged (already mode-decomposed)
