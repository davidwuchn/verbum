---
title: "Extraction Methodology — What Works, What Failed, Why"
status: active
category: methodology
tags: [extraction, ternary, distillation, sign-topology, methodology]
related: [holographic-error-correction.md, v14-architecture.md, crystal-universality.md]
depends-on: [project-thesis.md, crystal-universality.md]
---

# Extraction Methodology

> How to extract ternary topology from a teacher model. The current
> method works (375× compression, 96.5% correct signs). This page
> documents why it works, how it evolved, and three critical confusions
> that were resolved along the way.

## The Working Pipeline

```
Teacher (Qwen3.6-27B, float16)
  ↓ load layer by layer (CPU, no GPU needed)
  ↓ SVD tomographic voting: 8 random rotations per weight matrix
  ↓ sign(voted_direction) → ternary {-1, +1}
  ↓ zone-voted FFN: 3 teacher layers (aperture/fan/converge) → sign vote
  ↓ gate_proj extraction (89% of FFN selection)
  ↓ Pack ±1 into 2-bit storage
Student ternary base plates (593M positions, 85 MB)
```

### SVD tomographic voting

For each weight matrix: project through 8 random rotation angles,
compute SVD at each angle, vote on the dominant direction. Take the
sign. This captures the weight's directional tendency across multiple
viewpoints, reducing noise from any single projection.

**Why 8 rotations:** Empirically sufficient. More doesn't improve
results. Fewer misses low-confidence directions.

### Zone-voted FFN

Teacher FFN signs are extracted from **three layers** spanning the
lens zones, not one:
- Layer 4 (aperture/encode): 3% neuron activation
- Layer 20 (fan/compress): 49% neuron activation
- Layer 56 (convergence/decode): 2% neuron activation

The three layers vote on the shared student plate. This captures the
full lens topology in one ternary matrix.

### gate_proj extraction

Gate_proj signs are MORE critical than up_proj for FFN addressing:
gate kills 89% of neurons (it IS the beamformer). Including gate_proj
in extraction brought etch budget to 80.5% of parameters.

## V14 Extraction Numbers

| Metric | Value |
|--------|-------|
| Teacher | Qwen3.6-27B (27.8B params, float16) |
| Total arrays | 142 (1 embedding + 132 attention + 9 FFN) |
| Ternary positions | 593M |
| Sign distribution | 50.1% negative / 49.9% positive |
| Zeros in base | 0 (pure ±1) |
| Compression | 375× |
| Extraction time | 25.4 minutes, CPU only |
| Storage | 85 MB (compressed NPZ) / 148 MB (2-bit) |

## Three Confusions Resolved

The extraction methodology evolved through three critical confusions.
Each was a dead end that consumed significant session time. They are
documented here so future sessions don't re-enter them.

### Confusion 1: Weight-space signs are random across matrices

**The mistake:** Trying to extract the crystal from weight-space sign
patterns. Using per-matrix SVD, fixed random projections, or shared-
basis SVD to find consistent sign structure across weight matrices.

**Why it failed:** Signs in SVD-projected weight subspaces correlate
50% across layers — indistinguishable from random noise. The crystal
lives in ACTIVATION space (how inputs transform through weights), not
WEIGHT space (what signs the weights store). Per-matrix SVD finds
matrix-specific principal directions that are unrelated across matrices.

**Resolution:** Extract at-dimension sign(W) directly — don't project
into a shared weight-space basis. The topology is per-weight, not
per-principal-component. `sign(W)` at each position captures the
routing decision for that position.

**Key insight:** Q=0.974 fidelity when extracting signs at-dimension
(directly from the weight values). The rotation and SVD steps in the
final pipeline handle noise within a single matrix, not alignment
between matrices. (Session 129)

### Confusion 2: Oracle crystal signs coupled to magnitudes

**The mistake:** Copying exact sign(W) from a converged continuous
model directly into ternary plates.

**What happened:** Oracle crystal performed WORST (38.6%) compared to
random plates (42.4%) and even noisy plates (50% noise = 52.5%, the
best result).

**Why it failed:** The continuous model's computation depends on
magnitudes, not just signs. The oracle's sign topology is coupled to
the oracle's magnitudes — it's overfit to values the ternary model
can't access. Continuous params (Q, scales) can't compensate because
they're not the oracle's magnitudes. Random/noisy plates give GD
freedom; oracle plates give it a trap.

**Resolution:** This applied to the micro-model (d=48) where student
and teacher have different architectures. At scale (v14), the issue is
mitigated because:
1. SVD tomographic voting de-noises the sign extraction
2. TD corrects the 3.49% of signs that are wrong
3. The fold-and-correct cycle removes coupling iteratively

The deeper lesson: direct sign copy only works when followed by
correction (TD). Without TD, oracle signs are a trap. (Session 115)

### Confusion 3: Attention geometry ≠ computation geometry

**The mistake:** Using PCA-Q crystal measurements (from attention Q
projections) as loss targets for combinator embeddings in a stride-stack
student. Baking flat-attention crystal constants into `config.py`.

**Why it failed:** PCA-Q captures how FLAT attention routes information.
Stride-stack attention has completely different topology (windowed,
multi-stride, fractal bands). The teacher's attention crystal is
incompatible with stride-stack geometry.

Three things got conflated:
1. **Attention geometry** — how the model routes (PCA-Q, architecture-specific)
2. **Computation geometry** — how combinators relate (universal, architecture-neutral)
3. **FFN knowledge** — what the model knows (stored functions, etchable)

**Resolution:** The lattice we WANT is computation geometry. The sign
topology crosses architecture boundaries (r=0.998 Pythia-160M vs
Qwen3-32B). Extraction dispatches based on teacher layer type (what
tensors exist), not student layer type (how they'll be used). The
crystal universality IS the reason cross-architecture extraction works.

The combinator geometry needs to be found in an architecture-neutral
way — from FFN activations, hidden state trajectories, or behavioral
probes. Not from attention Q projections. (Session 135)

## Why sign(W) Works At All

The operation is **signed accumulation**: `sign(W) @ x` correlates
0.84 with `W @ x`. Each weight position encodes a routing decision:
- +1 = ADD this input dimension's contribution
- -1 = SUBTRACT (invert) this input dimension's contribution
- 0 = SKIP (ignore) this input dimension entirely

The sign captures 84% of the matrix's action on inputs. The remaining
16% is magnitude calibration — captured by per-row gamma scalars
(one float per row, ~5% of model information).

### Ternary routing = sign(crystal eigenvector)

At the deepest level, the ternary routing table is the sign of the
crystal eigenvectors. The crystal eigendecomposition predicts:
- Which neurons serve which principal component (allocation ∝ eigenvalue)
- What sign pattern each neuron uses (sign of corresponding eigenvector)
- How many neurons each PC gets (predicted: [181,123,66,45,37,25,17,14],
  observed: [214,159,74,31,17,8,4,5], r=0.9932)

The entire ternary topology is computable from the crystal
eigendecomposition. No gradient descent needed for topology — just
`sign(eigenvector)`. GD only adjusts gamma (scale) and attention
(routing between tokens). See `computed-beam.md` for the analytical
construction.

## Holographic Distillation (Micro-Model Method)

At micro scale (d=48), a different approach was validated: project
teacher computation through multiple beam angles and etch the
interference pattern into student plates.

- **Method:** Forward diverse probes through teacher, etch student
  plates to minimize ‖teacher_output − student_output‖² per layer
- **Result:** 91.3% of oracle performance (80.1% vs 87.7% ceiling)
- **Significance:** Captures FUNCTION (input→output behavior), not
  FORM (sign patterns). Multiple beam angles create an interference
  pattern encoding teacher computation.

This method validated holographic extraction in principle but was
superseded at scale by SVD tomographic voting + TD correction, which
is simpler and achieves comparable or better results with the fold
cycle.

## Summary: The Extraction Rules

1. **Extract at-dimension** — `sign(W)` directly, not through a
   projected basis
2. **Use SVD voting** — multiple rotations de-noise the sign decision
3. **Vote across zones** — FFN from 3 teacher layers (aperture/fan/converge)
4. **Include gate_proj** — it controls 89% of FFN addressing
5. **Expect ~3-5% errors** — TD will find and correct them
6. **Don't worry about magnitudes** — gamma scalars handle that (5%)
7. **Cross-architecture is fine** — the sign topology is universal (r=0.998)
