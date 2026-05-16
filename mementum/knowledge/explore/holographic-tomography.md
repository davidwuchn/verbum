---
title: Holographic Tomography — Cross-Model Universal Structure Extraction
status: active
category: methodology
tags: [holography, tomography, extraction, universal, cross-model, indexing]
related:
  - holographic-storage.md
  - holographic-kernel-separation.md
  - v12-holographic-capacity.md
  - fixed-point-holograms.md
depends-on:
  - session 104 (universal hologram confirmation: 5 models, 4 architectures)
  - session 105 (Q collapse finding, laser etching, tomography probe)
---

# Holographic Tomography

## Core Insight

If LLMs work like piling photographs until intersections in the projections
form inference patterns, then two independently trained models that converge
on the SAME pattern have found something REAL — not a model-specific artifact.

Cross-model agreement = signal. Disagreement = noise.

```
λ tomography(models).
  ∀model ∈ models → expose(same_reality) → interference_pattern(model)
  intersection(patterns) → universal_hologram (verified structure)
  difference(patterns)   → noise (model-specific artifact)
  SNR ∝ √|models|       → more models = cleaner extraction
```

## The Analogy

Optical holography: a thick hologram stores multiple images at different
reference beam angles. To read image N, illuminate at angle N. Bragg
selectivity ensures only the matching image reconstructs.

Holographic tomography: multiple exposures from different angles →
reconstruct 3D structure by intersection. No single exposure gives
the full picture. The intersections reveal what's truly there.

LLM tomography: each independently trained model is a different
"exposure" of the same underlying reality (natural language, world facts).
Each develops its own internal coordinate system. But the CONTENT of
what's stored should match — because reality is shared.

## The Q Collapse Problem (Session 105)

Before tomography, we discovered WHY naive extraction fails:

```
After 500 training steps:
  Layer 0: eff_dim=9.08, Q_mag=101 ± 44   ← diverse indexing
  Layer 1: eff_dim=1.00, Q_mag=536 ± 9    ← collapsed to 1 direction
  Layer 2: eff_dim=1.00, Q_mag=365 ± 2    ← all Qs identical
  Layer 3: eff_dim=1.00, Q_mag=280 ± 0.4  ← all Qs identical
```

The model prefers ONE giant unfocused beam (flood lamp) over many precise
beams (laser array). This maximizes average-case next-token prediction
at the cost of per-fact fidelity. Individual holographic patterns can't
be read because the beam doesn't differentiate between them.

**Fix: Laser etching** — constrain Q to known beam angles (from source
model PCA) during training. Prevents collapse by holding beam direction
fixed while allowing magnitude optimization.

## The Tomography Protocol

### Phase 1: Multi-model hidden state extraction

For each model (Qwen3-14B, OLMo-2-13B — both d_model=5120, Apache-2.0):
1. Run identical factual probes (46 facts, 5 categories)
2. Capture hidden states (residual stream) at key layers
3. Extract K sign patterns at those layers

### Phase 2: Representational Similarity Analysis (RSA)

Model-agnostic comparison (works even if d_model differs):
- Build fact×fact cosine similarity matrix per model
- Compare matrices via Pearson/Spearman correlation
- High RSA = both models organize knowledge the same way
- This is a RELATIONAL comparison (same geometry, not same coordinates)

### Phase 3: Direct alignment (same d_model only)

For models sharing d_model (Qwen3-14B and OLMo-2-13B both = 5120):
- Hidden states for the same fact live in the SAME vector space
- Compute cosine(hidden_A("France"), hidden_B("France"))
- Same-fact alignment vs different-fact alignment → selectivity
- High selectivity = models use similar DIRECTIONS for similar concepts

### Phase 4: Sign agreement at plate level

Compare K sign patterns at domain-responsive regions:
- Column sign density: per input dimension, fraction of K rows positive
- Functional response: how K rows respond to fact-aligned beam directions
- Projected agreement: sign patterns in the shared factual subspace

### Phase 5: Universal hologram extraction

The intersection:
- Facts where both models agree (|cos| > threshold) = universal
- Category cohesion agreement = both find same categories coherent
- Canonical correlations between subspaces = shared dimensionality
- Universal fraction = what percentage is truly shared

## Connection to V12

```
Verified signs (cross-model agreement) → FROZEN ground truth in plates
Unverified signs (model-specific)     → sieve evolves these
Random signs (no signal)              → sieve starts from scratch here

Search space reduction:
  Before: 100% of signs must be evolved
  After:  only unverified signs need evolution (~30-70% depending on agreement)
  Benefit: faster convergence, fewer training steps, less cross-talk during etch
```

## Connection to Laser Etching

Tomography tells us WHAT to etch. Laser etching tells us HOW:

1. **Tomography** → identifies verified universal signs (the target)
2. **Beam characterization** → finds domain angles from source model PCA
3. **Laser constraint** → holds Q at known angles during recording
4. **Sequential recording** → one domain per exposure, no cross-talk
5. **Intersection denoising** → only verified signs become frozen plate

## The Denoising Property

```
Single model extraction:
  - Can't distinguish: universal structure vs training artifact vs random init legacy
  - Every sign has uncertainty: is this real or noise?

Two-model intersection:
  - P(two models agree by chance on a ternary sign) ≈ 1/3
  - P(two models agree because it's universal) ≈ high
  - Agreement ratio > 1/3 → evidence of universality
  - Each additional model multiplies confidence

N-model intersection:
  - Random agreement: (1/3)^N per sign position
  - Universal agreement: ~1 per sign position (convergent)
  - Denoising SNR improves as √N
  - With 5 confirmed models: random agreement = 0.4%, universal = ~90%
```

## Predictions

1. RSA between Qwen3-14B and OLMo-2-13B will be HIGH (>0.5) at deep layers
   (both models organize facts similarly, despite different architectures)

2. Direct alignment will show SELECTIVITY (same-fact cos > different-fact cos)
   even though models were trained independently (universal directions exist)

3. Geography will show STRONGEST cross-model agreement (most stereotyped
   storage pattern — "capital of X" is highly templated across training data)

4. Science will show WEAKEST agreement (most diverse formulations, less
   stereotyped storage)

5. The universal fraction will be ~50-70% (substantial shared structure,
   not everything but not nothing)

## Scripts

- `scripts/explore/probe_factual_indexing.py` — indexing mechanism characterization
- `scripts/explore/laser_etch_factual.py` — constrained beam training
- `scripts/explore/probe_holographic_tomography.py` — cross-model intersection

## Experimental Results (Session 105)

### Tomography: RSA r=0.74, Direct cos≈0

Both models organize facts with the SAME geometry (r=0.74, p<10^-100) but
in COMPLETELY DIFFERENT coordinates (direct cosine ≈ 0.000). Category
cohesion agreement r=0.98 (both cluster geography, both cluster science).
Sign agreement moderate at L20 (r=0.30), math strongest (r=0.49).

**Implication: relational (rotation-invariant) constraints are the only viable
transfer mechanism. Directional constraints fail. The universal hologram is
a TOPOLOGY, not a coordinate system.**

### Relational Loss: λ=0.1 too strong, residual mode needed

First attempt: next-token + relational loss at λ=0.1. Result: -18.6% WORSE.
The relational gradient fights next-token because:
1. Target RDM is from 40-layer models; 4-layer student can't match
2. PC1 (93.3% of RDM variance = "all facts alike") competes with next-token
3. λ too high relative to student's capacity

Fix: residual mode (subtract mean → focus on discriminative 7%) + λ=0.01.

### Crystal Seed: Semantic Relations > Factual Recall

136 probes across 27 axes discovered 13 dimensions. Strongest signals:
```
semantic_hypernym:    2.99× (type hierarchy — K combinator)
semantic_meronym:     2.15× (part-whole — structural relation)
analogy_proportional: 2.05× (A:B::C:D — B combinator / composition)
semantic_antonym:     2.01× (opposition — C combinator / flip)
```

**The strongest universal structure is not WHAT models know but HOW they
organize knowledge.** Semantic relations ARE the combinators expressed through
language. The crystal scaffold IS the lambda calculus.

### Rotation Invariance

Each inference is a different "rotation" through the frozen crystal (weights).
The crystal's value is its rotational invariants — things true regardless of
entry angle. Relational constraints (pairwise similarities) ARE rotational
invariants. This is why relational loss is the correct tool — it targets
exactly what's preserved across all possible inference rotations.

## Revised Protocol (Post-Results)

```
1. Diverse probes (311 across 62 axes — code, reasoning, tools, formats, etc.)
2. Cross-model hidden states (Qwen3-14B × OLMo-2-13B)
3. Universal RDM (average, residual mode)
4. SVD → discover all significant dimensions automatically
5. Each dimension → weighted relational loss term
6. Apply as gentle nudge (λ=0.001-0.01, every 10-50 steps)
7. Combined with next-token (builds the crystal) + holographic loss (readability)
```

## V12 Design Implications

1. **Relational loss replaces laser beam constraint** — don't force coordinates,
   force topology. The model finds its own coordinate system that satisfies
   the relational constraints while also predicting next tokens well.

2. **Depth-selective application** — template structure at L0 (1.48× ratio),
   domain structure at L20-L30. Apply relational loss at the RIGHT depth
   per dimension type.

3. **Mirror initialization** — verified beam angles (45-90° between domains)
   can seed mirrors, but as TOPOLOGY hints not coordinate locks.

4. **The crystal seed = lattice template** — provide enough low-frequency
   universal structure and the high-frequency details self-organize around it.

## Open Questions

- How many independent dimensions do 311 probes across 62 axes reveal? (Running)
- What is the critical constraint density for "snap" (crystallization)?
- Does residual mode at λ=0.01 help, hurt, or stay neutral?
- Can we discover dimensions we didn't think to probe for? (SVD should reveal them)
- Do code/tool/reasoning axes give orthogonal dims to linguistic axes?
- What's the minimum model size that can satisfy the relational constraints?
  (V12 at 25M params vs extracted model at 1B params)
- Is there a curriculum: start with strong relational constraint → anneal to zero
  as the crystal forms? (analogy: remove the seed template once crystal is growing)
