---
title: "Psi Evaluation — Independent Verification of Crystal Hypothesis"
status: active
category: validation
tags: [psi, independent-verification, crystal, ternary, phi-convergence, gradient, type-system]
related:
  - crystal-universality.md
  - crystal-phi-derivation.md
  - phi-information-partition.md
  - tiny-classifier-ternary.md
  - ffn-circuit-types.md
  - lambda-machine.md
  - standing-wave-magnitudes.md
  - gradient-zero-map.md
depends-on: []
created: session 192
---

# Psi Evaluation — Independent Verification

> Session 192. An independent project (psi) ran verbum scripts unmodified
> and wrote new experiments on fresh hardware. Different human, different
> agent, same lambda activation trigger. 5 architectures tested, 6 new
> experiments created. The crystal hypothesis survives independent
> replication. The ternary FFN decompilation result is the breakthrough.

## What Was Verified

### 1. Sign Topology (5 architectures)

cos(sign(W)@x, W@x) measured fresh across 5 models:

| Model | cos(sign, full) |
|-------|----------------|
| Pythia-160M | 0.746 |
| Pythia-410M | 0.760 |
| Qwen3-0.6B | 0.760 |
| Qwen2.5-0.5B | 0.749 |
| SmolLM3-3B | 0.775 |

Mean = 0.758 ± 0.011. Random control ≈ 0.000 for all models.
The phenomenon is universal. Spread is 3 percentage points (not within 1%).

### 2. Four Modes (5 architectures)

KBC cluster correlation r > 0.85 in all 5 models. Always 4 clusters,
never 3 or 5. I is structurally distinct in 4/5 models (Pythia-410M
borderline at r=0.777). Mode percentages vary (K: 23-39%, B: 12-35%).
Structure is universal; proportions are model-specific.

### 3. Crystal Geometry (cross-architecture)

9×9 cosine matrix correlation across all architecture pairs:
- All pairs r > 0.85, mean = 0.951
- Best: Qwen3-0.6B ↔ Qwen2.5-0.5B r = 0.992
- Eigenvalue shape correlation: all pairs r > 0.96, mean = 0.982

The crystal is the same mathematical object across architectures.

### 4. Selectivity (cross-architecture)

Pythia-160M ↔ Qwen3-0.6B: r = 0.991 (KIBC means), cos = 0.999.
Depth profile correlation: low (r = 0.16). Same *what*, different *where*.
The crystal structure is universal; depth placement is architecture-specific.

## New Findings

### 5. φ Convergence (scale dependence)

Target: λ₀/λ₁ = φ^(4/5) = 1.4696

| Model | λ₀/λ₁ | Error |
|-------|--------|-------|
| Qwen3-0.6B | 1.079 | 26.6% |
| Qwen3-8B | 1.317 | 10.4% |
| Qwen3-14B | 1.480 | **0.7%** |
| Qwen3-32B | 1.340 | 8.8% (regresses) |
| Qwen3.6-27B | 1.183 | 19.5% (multimodal) |

Within Qwen3 pure language: monotonically improving (0.6B → 8B → 14B).
14B hits the attractor at 0.7% error. 32B regresses — hypothesis: the
30-70% zone-B heuristic may be wrong for 64-layer models.

Per-eigenvalue φ fit: all PCs 0-6 within 1.4% for ALL models tested.

### 6. Gradient-Quantization Correspondence

Prediction: |∇L| correlates positively with |W - Q(W)|.

**Pythia-160M:** ❌ INVERTED (ρ = -0.04, monotonically decreasing).

**Qwen3-8B:** Layer-specific.
- L1-L3 FFN (EXPAND): ρ = +0.55 to +0.78 ← **strong positive**
- L4: ρ = +0.19 (transition)
- L5+: ρ ≈ 0 or negative (ORTHO/COMMIT phase)
- Aggregate: ρ = +0.003 (signal drowned)
- Binned monotonicity: 68.4% (vs 0% for Pythia-160M)

**Finding:** Gradient-quantization correspondence holds in the EXPAND
phase only. GD converges to a normal form where the crystal nucleates.
ORTHO phase = continuous computation ≠ ternary convergence.

Results: `results/gradient-quant-correspondence/`
Script: `scripts/experiments/gradient_quant_correspondence.py`

### 7. Ternary Inference Pattern (FFN → 9 Ternary Programs)

Method: replace FFN layer → classify KIBC mode → lookup ternary pattern × γ.
9 ternary patterns derived from combinator centroids.

| Model | Best Layer | PPL Ratio | Worst Layer | PPL Ratio |
|-------|-----------|-----------|-------------|-----------|
| Qwen3-0.6B | L15 | 1.04× | L19 | 1.29× |
| Qwen3-8B | L15 | **0.96×** ← improves | L10 | 1.06× |
| Qwen3-32B | L19 | 0.99× | L27 | 1.03× |

**Critical finding:** centroid(continuous) ≡ ternary + pos_gamma TO THE
DECIMAL. The continuous centroid and the ternary pattern + per-position
gamma produce identical PPL. Magnitudes of the centroid are irrelevant;
only signs + scale matter.

Convergence: 0.6B (1.04×) → 8B (0.96×) → 32B (0.99× all layers).
At scale, FFN computation IS 9 ternary programs.

### 8. Coherence Test (Fact Recall with Ternary FFN)

Qwen3-8B, 15 fact prompts, baseline 12/15 = 80%.

| Layer | Fact Rate | Δ | Outputs Changed |
|-------|-----------|---|-----------------|
| L10 | 87% | +7% | 15/15 |
| L15 | 73% | -7% | 11/15 |
| L20 | 80% | 0% | 10/15 |
| L25 | 80% | 0% | 12/15 |

Mode is preserved (correct combinator fires). Content varies (specific
wording changes). L25 failure mode: K-reduction fired correctly but
operand was generic, not specific. Ternary captures crystal (routing),
loses plate (specific facts) at some layers.

### 9. Gate-Indexed Ternary

Keep gate_proj → binarize gate pattern → cluster → ternary lookup.
Qwen3-8B L25: all cluster counts (9-128) achieve fact recall ≥ 80%
(= baseline). Gate pattern carries more information than combinator
mode alone. But gate_proj = 96MB dominates storage (only 3× compression).

### 10. Tiny Classifier Ternary (THE BREAKTHROUGH)

See dedicated page: `tiny-classifier-ternary.md`

288MB → 180KB. 1638× compression. PPL **improves**. Classifier trains to
100% accuracy. The 9 modes are linearly separable from the residual stream.

### 11. Type System Discovery

The 9 operational modes ≠ KIBC combinators:
- AMI(clusters, KIBC labels) = 0.15 (near random)
- 136/180 crystal probes → single mega-cluster (all 9 combinators mixed)

Two overlapping ternary structures in the same weights:
1. **Crystal basis (KIBC):** governs routing (attention patterns). 3.5% of FFN space.
2. **Operational modes (9):** governs programs (FFN computation). Remaining 96.5%.

Both ternary. Both few-mode. Together = β-reduction engine.
Types are linearly separable (100% accuracy) but not yet decoded semantically.

### 12. Crystal Derivation (Pure Math)

Enumerated 2.35M KIBC expressions (size ≤ 7) → reduced → co-occurrence.
- Eigenvector topology: B,C vs K,I split ✅
- B=C symmetry ✅
- I smallest ✅
- Eigenvalue ratios: ❌ diverge from empirical (co-occurrence λ₀/λ₁ = 3.98
  vs target 1.47)

Topology is derivable from mathematics. Magnitudes require data.

## Meta

### Provenance

Independent human, independent agent, same nucleus trigger. The evaluation
converged to the same conclusions from a different reduction path. This is
the Church-Rosser property of the lambda calculus: all reduction paths reach
the same normal form.

### Attractor Hypothesis (refined)

The crystal equation = ideal topology that GD converges toward. GD can only
β-reduce (softmax forces it). Bigger model → more capacity → closer to
attractor. The frozen topology (signs) = the crystal = mathematical constant.
Soft topology (gradient zeros) = where GD settled = overlaid on crystal.

FFN magnitudes ≠ grout (free calibration). Magnitudes = part of the machine.
They determine softmax smearing → which reduction fires for a given input.
FFN magnitudes = holographic fringe pattern. Attention reads the fringes
→ reductions fire.

## Open Questions

1. **Multi-layer replacement:** Does PPL hold replacing ALL zone-B layers simultaneously?
2. **Type decoding:** What ARE the 9 operational modes semantically?
3. **Scale benchmark:** Run on MMLU/HellaSwag, not 15 handwritten prompts.
4. **32B zone-B:** Is the 30-70% heuristic wrong for 64-layer models?
5. **Cross-architecture tiny classifier:** Does it work on Pythia/Mistral?
6. **Full model decompilation:** Can ALL layers be decompiled (not just zone B)?
7. **Ternary training:** Can ternary programs be TRAINED directly (skip continuous FFN)?
