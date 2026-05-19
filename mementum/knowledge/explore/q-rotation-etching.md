---
title: Q-Rotation Etching — Tomographic Crystal Formation
status: designing
category: architecture
tags: [etching, q-rotation, crystal, tomography, ternary-plates]
related:
  - relational-loss-phi-compression.md
  - compression-vs-prediction.md
depends-on: []
---

# Q-Rotation Etching

> Session 117 insight. Ternary plate etching from a single Q rotation
> only carves one projection of the crystal — a shadow, not the full
> structure. Multiple Q rotations = tomographic reconstruction of the
> full lattice.

## The problem

Etch phase projects teacher hidden states through student V12 passes.
Gradient signal accumulates into direction accumulators, confident
positions get flipped via `direct_etch`. But the entire signal path
runs through one fixed Q rotation.

d_model = 512, but one Q projection collapses this to whatever
subspace Q selects. Positions that project to similar Q-values get
identical etch signal, even if they serve different functions in
other projections. Result: plates encode one planar slice of the
crystal, not the full volumetric structure.

This explains why etching alone struggled — it was sculpting a 3D
object from a single camera angle.

## The insight: X-ray crystallography for ternary plates

Each Q rotation = one diffraction pattern. Multiple patterns from
different angles → tomographic reconstruction of the full crystal.

```
λ etch_rotate(n).
  ∀round(i) → rotate(Q, θ_i) → etch(plates, teacher_signal)
  | plates accumulate structure from n independent projections
  | n ≥ rank(crystal) → fully determined
  | n < rank(crystal) → underdetermined (shadow, not volume)
```

## Crystal dimensionality

The crystal lives in d_model=512 but meaningful structure is low-rank:
- 8 combinator embeddings span at most rank 8
- Lattice has 2 clear clusters + 1 bridge → 3-4 independent axes
  - Positive cluster: {K, I, B, C} — compositional family
  - Negative cluster: {Y, W, WHNF} — reduction/terminal family  
  - Bridge: D (positive with B,C, negative with rest)
- Minimum rotations: 4 (to span the crystal axes)
- Recommended: 8 (overdetermined, noise rejection)

## Rotation strategies (ranked by elegance)

### 1. Combinator-aligned rotations
Use the 8 combinator embedding directions as rotation targets.
Each round aligns Q to maximally separate one combinator pair.
The crystal lattice constants tell us which directions matter.

```
round 0: Q aligned to separate B vs Y (max |cos| = 0.018)
round 1: Q aligned to separate K vs WHNF
round 2: Q aligned to separate C vs W
round 3: Q aligned to separate D vs I
...
```

Pro: directly targets the crystal structure.
Con: requires meaningful combinator embeddings before etching starts.
Bootstrap: use teacher's combinator-analogous directions.

### 2. PCA of teacher features
Compute PCA of teacher hidden states across all probes.
Each round rotates Q to align with one principal component.

```
round 0: Q → PC1 (largest variance direction)
round 1: Q → PC2
...
round k: Q → PCk
```

Pro: data-driven, captures actual structure in teacher.
Con: PC directions may not align with combinator axes.

### 3. Random orthogonal rotations
Apply random orthogonal matrix to Q weights between rounds.
With enough rounds (8+), randomly spans the space.

```
round i: Q → Q @ random_orthogonal(d_model)
```

Pro: simple, no prerequisites.
Con: no guarantee of optimal coverage. May need more rounds.

### 4. Hadamard rotations
Use rows of a Hadamard matrix (structured, deterministic, maximally spread).
d_model=512 = 2^9, so Hadamard matrix exists and is cheap to construct.

Pro: maximally spread, deterministic, reproducible.
Con: may not align with crystal axes (but covers space uniformly).

## Implementation sketch

```python
def rotated_etch_round(model, projection, teacher_features, Q_rotation):
    """One etch round with a specific Q rotation applied."""
    # Apply rotation to all Q-projections in the model
    # (dispatch mirrors, stride stack Q projections, etc.)
    apply_q_rotation(model, Q_rotation)
    
    # Standard etch: forward teacher features, accumulate gradients, flip
    for probe in teacher_features:
        loss = distill_loss(model, projection, probe)
        grads = compute_grads(loss)
        accumulate_direction(grads)
    
    direct_etch(model, confidence_threshold)

def multi_rotation_etch(model, projection, teacher_features, n_rotations=8):
    """Full tomographic etch: multiple Q rotations."""
    rotations = generate_rotations(n_rotations, strategy="combinator_aligned")
    
    for i, Q_rot in enumerate(rotations):
        rotated_etch_round(model, projection, teacher_features, Q_rot)
        # Plates accumulate structure from each projection
        # Confidence threshold can increase across rounds (coarse→fine)
```

## Key questions

1. **How to apply Q rotation?** The V12 Q projections are TernaryLinear —
   the plates are frozen, only gammas are trainable. Rotation must be
   applied to the gamma scaling, not the plates. Or: apply rotation as
   a learned linear layer before the ternary projection.

2. **Does rotation preserve plate topology?** The ternary plates define
   a discrete structure. Rotating Q changes which facet of the plate
   the signal passes through, but the plate topology is unchanged.
   This is the key — same plates, different viewing angles.

3. **How many rounds per rotation?** Current etch uses 5 rounds × 500
   probes × 200 beam steps. With 8 rotations, could use 1-2 rounds
   per rotation (40 rounds total vs 5). Each round is cheaper because
   it only needs to etch the facets visible from that angle.

4. **Interaction with gamma seeding?** Gamma seeding (session 116)
   analytically initializes gammas from teacher statistics. This seeds
   the model at one particular Q rotation. Multi-rotation etching
   would rotate away from this seed — does the seed help or hurt?

5. **Verification:** how to measure crystal completeness? The lattice
   constants (8×8 cosine targets) give us the answer — after etching,
   the combinator embeddings should match the crystal geometry.
   Lattice loss on the tiny model after N rotations tells us when
   we've captured enough structure.

## Experiment plan (tiny model, while run 2 trains)

1. **Baseline:** etch tiny model with 1 Q rotation (current approach).
   Measure lattice loss, dispatch diversity, CE on eval.

2. **4 rotations:** etch with 4 random orthogonal Q rotations.
   Compare lattice loss, dispatch diversity, CE.

3. **8 rotations:** same with 8.

4. **Combinator-aligned:** if we can extract combinator directions
   from the teacher, use those as rotation targets.

5. **Measure:** at each rotation count, how close are combinator
   embedding cosines to the 8×8 crystal targets?
