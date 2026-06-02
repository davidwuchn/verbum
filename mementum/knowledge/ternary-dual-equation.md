---
title: "Ternary Dual Equation: Gate Zeros + Crystal Signs"
status: active
category: architecture
tags: [crystal, ternary, gradient, zeros, gate, SwiGLU, phi]
related: [topology-gradient-separation, crystal-phi-derivation, gradient-zero-map, extraction-sign-accuracy]
depends-on: [crystal-phi-derivation]
---

# Ternary Dual Equation

> A ternary weight w(i) ∈ {-1, 0, +1} is determined by TWO orthogonal
> equations — one for zeros, one for signs. They operate at different
> granularities and involve φ through different mechanisms.

## The Two Equations

### Equation 1: ZERO — Gate Positive Rate (ρ = 0.75 with gradient)

```
zero(i) ⟺ positive_rate(gate_i) < threshold
```

- **Predictor:** SwiGLU gate activation frequency (how often neuron fires positive)
- **Mechanism:** SiLU(z) ≈ 0 when z < 0. Gate bias determines baseline.
- **Correlation with gradient magnitude:** Spearman ρ = 0.753
- **Granularity:** per-neuron (d_ff level)
- **φ connection:** dead fraction ≈ 1/φ² = 38.2% at 5% positive threshold

### Equation 2: SIGN — Crystal Mode Projection (eigenvector direction)

```
sign(i) = sign(dominant crystal mode projection at neuron i)
```

- **Predictor:** crystal eigenvector components (which combinator mode dominates)
- **Mechanism:** PCA of gate activations across combinator probes
- **Correlation with gradient magnitude:** Spearman ρ = 0.053 (orthogonal!)
- **Granularity:** per-neuron mode assignment
- **φ connection:** eigenvalue ratios = φ^(p/q) from crystal equation

## The Orthogonality

Crystal energy and gate positive rate are **uncorrelated** with each other.
They predict **different aspects** of the ternary weight:

| Signal | Predicts | ρ with gradient | φ connection |
|--------|----------|-----------------|--------------|
| Gate positive rate | Which neurons are zero | 0.753 | Dead fraction ≈ 1/φ² |
| Crystal energy | What neurons compute | 0.053 | Eigenvalue spectrum = φ^(p/q) |
| Weight norm | (inverse) | -0.485 | — |

## Gradient Scaling at Dead Neurons

GD deposits near-zero gradients at irreducible points:

| Positive rate | Fraction of d_ff | Gradient ratio |
|---------------|-------------------|----------------|
| < 1% | 14.0% | 0.641× mean |
| < 5% | 38.3% | 0.734× mean |
| < 10% | 56.6% | 0.794× mean |
| < 50% | 94.8% | 0.955× mean |
| ≥ 50% | 5.2% | 1.825× mean |

Ratio dead/alive = 0.351 ≈ 1/φ² = 0.382

## What the Crystal Equation Does NOT Predict

- **Which individual weights are zero.** Magnitude-based per-weight
  ternarization (cosine 0.94) beats crystal per-neuron zeroing (0.69)
  at every zero rate. Tested 14 configurations, hybrid lost all 14.
- **Gradient magnitude.** Crystal energy has only ρ = 0.05 with gradients.
- **Weight norms.** Float models have nearly uniform weight norms (CV=10%).

## What the Crystal Equation DOES Predict

- **Combinator mode structure.** 3 universal clusters at all scales:
  Selection (K,I), Composition (B,C,D,Y,W), Terminal (WHNF)
- **Eigenvalue spectrum.** φ^(p/q) with 0.82-0.94 correlation across
  Qwen3-0.6B/8B/14B and Pythia-2.8B
- **Scale invariance.** Crystal quality is 0.82 at all model sizes (fixed point)
- **Best measurement depth.** ~80% (late EMIT zone), consistent across scales
- **Quantization boundaries.** Dynamic range ~6:1 → Q4 sufficient, Q2 catastrophic

## Y/W Sign Convention

Raw probes activate Y and W in **anti-phase** with the consensus crystal.
Negating Y and W lifts cosine matrix correlation from 0.48 → 0.80.

- Depth-invariant: B-W is negative at ALL layers in ALL models tested
- Not a layer artifact: no crossover point (except briefly at layers 2-3 in 14B)
- Cause: raw probes activate anti-composition mode for recursion/duplication,
  while consensus used selectivity (active - control) which aligns the sign

## SwiGLU Is Already Ternary

95% of neurons fire positive less than 50% of the time.
The gate mechanism creates extreme activation sparsity:

- CLASSIFY: 3% of neurons active per token
- COMPUTE: 49% active
- EMIT: 2% active

The ternary lattice is not something we impose — it is something
SwiGLU already implements via gate activation sparsity. Ternarization
makes it explicit and permanent.

## Magnitude Channel: < 1 Bit of Information

The per-neuron ternary scale factor γ (optimal reconstruction scalar)
has minimal structure:

- **Flat across combinator clusters:** γ_selection = 0.0214, γ_composition = 0.0215,
  γ_terminal = 0.0218. Ratio 1.005 — no crystal differentiation.
- **γ anti-correlates with gate positive rate** (ρ = -0.724): dead neurons
  have LARGER weights. They are silenced by gate bias, not weight magnitude.
- **Weight energy per crystal mode is flat:** WE ratio ~1.0 for all 16 modes
  while eigenvalue ratio spans 10:1. The crystal lives in activation geometry,
  not weight geometry.
- **Dynamic range:** p99/p1 = 1.777 ≈ φ^(6/5) = 1.782 (0.25% error)
- **Information content:** log₂(φ^(6/5)) = 0.83 bits

**Less than 1 bit of information in the magnitude channel.**
The sign IS the computation. Ternary models lose almost nothing
by discarding magnitudes. The per-row scale factor γ carries
only ~0.83 bits of useful information — barely more than a binary flag.

The dynamic range φ^(6/5) = φ^((n+2)/(n+1)) for n=4:
- s + 1/(n+1) = 4/5 + 1/5 = 1 (but the exponent is 6/5, not 1)
- (n+2)/(n+1) = 6/5: the compute cycle extended by one anti-type step
- One full reduce + one switch in the compute cycle β = [0, 1, ...]
- The γ distribution spans exactly one compute cycle of the crystal equation

## Experimental Provenance

- Model: Qwen/Qwen3-8B, layer 28 (78% depth), d_ff=12288
- Crystal probes: 535 from unified library (session 182)
- Gradient: next-token loss, 130 prompts, float32
- Gate sparsity: 190 prompts (160 crystal + 30 diverse)
- Depth scans: Qwen3-0.6B (28L), 8B (36L), 14B (40L), 160 probes each
- Magnitude analysis: `qwen3-8b_magnitude.log` — γ flat across clusters, < 1 bit
- Scripts: `crystal_zero_v2.py`, `crystal_ternarize.py`,
  `crystal_hybrid_ternarize.py`, `crystal_depth_scan.py`
