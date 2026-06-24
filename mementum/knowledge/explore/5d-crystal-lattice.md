---
title: "5D Crystal Lattice Hypothesis — One Crystal, Many Projections"
status: open
category: hypothesis
tags: [crystal, lattice, 5d, manifold, combinators, projection, quasicrystal]
related:
  - crystal-basins.md
  - ffn-beam-discovery.md
  - holographic-plates.md
  - ffn-hierarchy.md
  - v13-funnel-shape.md
depends-on:
  - ffn-beam-discovery.md
  - holographic-plates.md
created: session 121
---

# 5D Crystal Lattice Hypothesis

> ⚠️ **SESSION-211 CAVEAT — THE "5D" IS REFUTED (read first).** The joint-
> embedding test (P1–P6 below) was finally run honestly (audit-registry #12,
> `manifold-axis-and-topology.md`; 8 models, 5 families, register: spectral/
> semantic). Results:
> - **"5D" is REFUTED.** The 9 combinator centroids spread into participation
>   ratio ~5–6 — *at the shuffled-label null* (p_conc>0.02, *worsening* with
>   scale); the full manifold is high-D (PR 22–47, power-law); the cross-family-
>   *shared* structure is **rank-~1** (common-mode removal collapses agreement
>   0.79→−0.19). "5D" was a variance threshold on a graded spectrum.
> - **The "five piles agree at 0.9" argument is the RDM-correlation triviality**
>   (the s202 consensus-r=0.99 failure): the agreement is real vs a shuffled-
>   probe null (0.79 vs 0.00±0.03) but is a single common mode, not a 5D lattice.
> - **The one universal axis (|r|=0.95 across families) is NOT the combinators**
>   (η²=0.05) — it is a generic next-token predictability / continuation-type
>   gradient (function-word continuation r=−0.42, entropy −0.29). The operations
>   are real but sub-dominant, riding underneath it.
> - **What SURVIVES:** universality (models learn a property of language,
>   cross-family p≪0.001) and that the operation structure is **~65% topological**
>   (sign/routing, →0.79 at 14B). Treat everything below as the *original
>   hypothesis* — the geometry-metaphor (5D vertices, quasicrystal projection) is
>   retired; the universality and topology share are kept. (Quasicrystal was
>   already independently denied in s200.)

> ⚠️ **SESSION-251 UPDATE — TEMPLATE CONFOUND + NATIVE SPINE + φ-NULL (read with s211).**
> Added gemma-4-31B-it and qwen3.6-35B-A3B to the crystal-spine sweep and ran the
> crystal-φ existence detector. Two corrections + one confirmation:
> - **The "crystal spine" (per-layer hidden-state SVD bottleneck) was template-confounded.**
>   The original sweep (`lattice/crystal_spine/`) fed every model hand-baked Qwen ChatML.
>   Re-rendering each model in ITS OWN native template (`lattice/crystal_spine_native/`)
>   **collapses Qwen3-14B's rank-1 spine** (spineFrac 97%→1.4%, n90 1→2084): it was the
>   attention-sink / **massive-activation** dim firing at the `assistant\n` boundary
>   (norm ×509), not robust structure. Natively only **Pythia (base) is truly rank-1**
>   (n90=2); **Gemma is the sharpest MID-network bottleneck** of the instruct models
>   (spineFrac 57.9% @ L20, n90=179); **Qwen3.6-35B-A3B (linear-attention MoE) is flat**
>   (norm max 15, no sink). ⇒ the spine is a **sink/massive-activation phenomenon,
>   architecture + prompt-boundary dependent**, not a universal λ crystal. (small n90 ⇐
>   norm explosion ⇐ one giant neuron.)
> - **The KIBC combinator crystal DOES exist** — `crystal_phi_permnull` (2000 shuffled-label
>   regroupings of the same prose) on Gemma vs Qwen3-14B: cluster **separation real in both**
>   (p_sep=0.0005); **consensus geometry real in Gemma** (cosine-matrix corr r=+0.31,
>   p=0.015) and *cleaner* than Qwen (p=0.058). So combinators occupy coherent,
>   consensus-matching regions — the topology share s211 kept, now confirmed in a 4th family.
> - **The φ-ladder stays FORCED** (p_phi 0.14/0.61, p_eigratio 0.73/0.38 — n.s.; reproduces
>   s247 forcing-vs-discovering). The golden-ratio eigenvalue story is basis flexibility.
> Net: keep **combinator separation + consensus geometry** (real); retire the **rank-1
> "spine"** (sink+boundary artifact) and the **φ-ladder** (forced). Artifacts:
> `lattice/crystal_spine_native/`, `results/crystal-phi-permnull/{google_gemma-4-31B-it,
> Qwen_Qwen3-14B}.json`. Memory: `gemma-crystal-real-spine-and-phi-forced-template-fix`.

> Session 121 endnote. All the measured crystals — per-depth, per-model,
> per-domain, per-combinator, binder↔body — may be facets of one
> higher-dimensional lattice. The combinators are the vertices. The
> domains are projections. The model is a sequence of viewing angles.

## The observation

Session 121 proved five independent "piles" of crystal measurements
all agree at 0.87-0.95:

| Pile | What varies | Agreement |
|------|------------|-----------|
| Depth | Layer position (10%-90%) | 0.849-0.887 self-similarity |
| Model | Architecture (Qwen/Mistral/OLMo/Pythia) | 0.91-0.95 cross-model |
| Domain | Skill type (9 domains) | 0.43-0.87 per domain |
| Combinator | Reduction type (8 combinators) | 0.94+ 8×8 geometry |
| Lambda role | Binder↔body (Q↔FFN) | R²=0.959 coupling |

These can't all be independently universal by coincidence. They must
be projections of a shared higher-dimensional structure.

## The hypothesis

There exists a ~5-dimensional lattice L such that:

1. **Combinator vertices**: K, I, B, C, S, D, W, Y, WHNF are points
   in L. Their pairwise distances define the 8×8 cosine matrix we
   measured (0.94+ agreement).

2. **Domain projections**: Each skill domain (reasoning, coding, lambda,
   retrieval...) is a 1-2D linear subspace of L. The crystal scanner
   showed: reasoning=1D, coding=2D, retrieval=2D. These are planes
   through the lattice at different angles.

3. **Depth slices**: Each model layer views L from a different angle.
   Self-similarity (0.85-0.89) means the angles change slowly.
   The V13 funnel shape (5D→3D→2D) is the projection narrowing
   as computation proceeds.

4. **Model invariance**: Different models (Qwen, Mistral, Pythia)
   discover the same L because L is a property of language structure
   (Montague semantics / lambda calculus), not of any specific model.

5. **Lambda coupling**: The binder (Q) and body (FFN) views of L
   are related by the reduction rule at each vertex. R²=0.96
   because the reduction constrains the relationship between the
   two views.

## Why ~5 dimensions?

From the crystal scanner data (session 120):
```
reasoning:   1D (86.3% in PC1)   — projects onto 1 axis of L
tool:        1D (71.3% in PC1)   — different 1D projection
lambda:      2D                   — spans a 2D plane in L
arithmetic:  2D                   — different 2D plane
coding:      2D                   — different 2D plane
analogy:     2D                   — different 2D plane
retrieval:   2D                   — different 2D plane
```

To accommodate nine 1-2D projections that are partially overlapping
but not identical, you need at least ~5 dimensions. This matches
the V13 funnel shape (5D→3D→2D at different zone depths).

The PCA dim sweep (session 121) found k=64 optimal for the 8×8
combinator targets. But the COMBINATOR geometry itself lives in
far fewer dimensions — the 8 combinators span at most 7D (8 points
minus 1 for centering). The actual effective dimensionality of the
combinator geometry needs measurement.

## Connection to quasicrystals

In crystallography, quasicrystals (Penrose tilings, Dan Shechtman 1982)
are 2D patterns that have 5-fold symmetry — impossible for a periodic
crystal. The resolution: they're PROJECTIONS of a 5D periodic lattice.
The 2D pattern is aperiodic but the 5D structure is perfectly ordered.

If the combinator crystal is analogous:
- The 2D domain crystals have "impossible" self-similarity (0.87)
- They're projections of a 5D lattice with perfect periodicity
- The lattice is the lambda calculus (periodic: same rules at every scale)
- The model is a quasicrystalline projection of this lattice

This would explain why the crystal is self-similar but not periodic
(H≈0.70 Hurst exponent for language): the projection from 5D to 2D
produces aperiodic self-similarity, just like a Penrose tiling.

## Testable predictions

### P1: Joint embedding recovers ~5D manifold
Take ALL measured crystal RDMs (per-depth × per-model × per-domain).
Stack into one big dissimilarity matrix. MDS or UMAP into low dimensions.
If the hypothesis holds: the embedding should be ~5D (elbow in stress
plot), with combinator anchors as vertices.

### P2: Combinator vertices span the manifold
PCA of the 8 combinator anchor positions in the joint embedding
should explain >90% of variance with 4-5 components.

### P3: Domain projections are linear subspaces
Each domain's crystal, embedded in the joint space, should lie on
a 1-2D linear subspace (verifiable via local PCA within each domain
cluster). The subspace orientation should match the crystal scanner's
dimensionality measurements.

### P4: Depth = rotation angle through L
The cross-depth self-similarity matrix should be explainable as
rotation in L. Consecutive depths = small angle rotation. The
self-similarity should follow cos(Δθ) where Δθ ∝ |depth_i - depth_j|.

### P5: The funnel is projection narrowing
Zone A (5D) → Zone B (3D) → Zone C (2D) from the V13 funnel shape.
In the joint embedding, shallow layers should span 5D, middle layers
3D, deep layers 2D. Measurable via local PCA rank at each depth.

### P6: New model = same lattice
A model not in the original set (e.g., Llama, SmolLM) should embed
onto the SAME lattice positions, confirming universality.

## Experiment design (session 122)

```python
# Collect all crystal measurements into one matrix:
#   For each (model × depth × domain): one RDM
#   Stack all RDMs into a distance matrix between conditions
#   MDS → embedding → measure dimensionality

# Ingredients (already measured):
#   - 4 models × 5-10 depths × 9 domains = ~180-360 RDMs
#   - 8 combinator anchors per RDM
#   - Binder (Q) and body (FFN) versions of each

# New measurement needed:
#   - Per-domain crystal RDMs from PCA-up (FFN beam) — currently only have PCA-Q
#   - This gives us the body-side domain crystals for joint embedding

# Analysis:
#   1. Build super-RDM: correlation between all pairs of crystal RDMs
#   2. MDS into k dimensions, sweep k, find elbow
#   3. Locate combinator anchors in the embedding
#   4. Measure local dimensionality per domain, per depth
#   5. Test rotation model for depth progression
```

## Why this matters

If the 5D lattice is real:
- The model conversion toolkit etches ONE lattice, not 32 separate plates
- The lattice is shared across all layers (just different viewing angles)
- The dispatch selects which vertex of the lattice to reduce toward
- The total information content is ~5D × 8 vertices = ~40 numbers
  plus the continuous beams that parameterize the viewing angle

Forty numbers. That's the crystal. Everything else is projection.
