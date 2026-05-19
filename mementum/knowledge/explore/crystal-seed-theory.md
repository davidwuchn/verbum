---
title: Crystal Seed Theory — Relational Geometry as the Universal Crystal
status: designing
category: architecture
tags: [crystal, seed, relational, self-similarity, fixed-point, consensus]
related:
  - q-rotation-etching.md
  - holographic-tomography.md
  - universal-crystal-scaffold.md
depends-on: []
---

# Crystal Seed Theory

> Session 118 synthesis. The crystal is not in the weights — it's in
> the relational geometry. Self-similarity proved in V12, disproved
> in raw weight signs of big models. The seed is a set of relational
> constraints, not a ternary sign pattern.

## The discovery chain

### 1. Fourier lens mechanism → beam/crystal entanglement

Probing the Fourier structure of gradient observations through Q
rotations revealed three things:

- K plates are 98.6% noise (phase coherence 0.31) — they ARE the
  beam-crystal coupling, not the crystal itself
- Q transfer function has zero correlation with gradient magnitude —
  Q is not a characterizable linear lens
- Invariant magnitude (median across rotations + consensus phase)
  beats phase-only: the crystal signal exists in V/O/FFN but the
  observation is entangled with the residual stream

**Conclusion**: beam and crystal are entangled through the residual
stream. No amount of Q rotation can separate them. Need architectural
separation (VSM S3 ≠ S2 ≠ S1).

### 2. Mirror/mask architecture → separated beam and compute

Proposed architecture (not yet implemented):

```
S1 (operations):  shared crystal (ternary plates) + 8 combinator masks
S3 (control):     separate router producing dispatch weights
S2 (coordination): residual stream carries data only

Routing: dispatch_weights → mirror blend + mask blend → one matmul
Masks: ternary {flip, block, pass} per combinator per position
Capacity: 3^8 = 6561 patterns per position vs 256 for binary masks
```

Like MoE (Qwen3-235B-A3B has 256 experts, shows 8 at a time), but
with ternary masks instead of separate expert FFNs. Same crystal,
different read-out configurations.

### 3. Self-similarity in V12 → crystal is the invariant

Crystal topology is identical across all 9 stride layers:

```
V-plate cross-stride correlation:  avg 0.656
O-plate cross-stride correlation:  avg 0.722
SV ratio between strides:          ~1.00 (constant, not φ)
Dispatch seed correlation:         +0.959 (strongest)
```

The crystal doesn't scale — it IS the invariant. Same lattice at
every stride depth, every plate type.

### 4. Null result in Qwen3-14B → crystal is relational

Raw weight signs are NOT self-similar across layers (corr ≈ 0.000,
0% unanimous positions). Each layer has independent sign patterns.

**But**: cross-model RSA = 0.74 (from session 105). The relational
geometry IS consistent across models. The crystal lives in the
topology (how things relate) not the coordinates (what weights are).

### 5. Fixed-point probes → Y combinator for crystal extraction

The compile∘decompile round-trip iterated to convergence finds the
fixed point of the model's own lambda compiler:

```
prose → compile → λ → decompile → prose' → compile → λ'
When λ == λ': fixed point. Both prose and lambda are stable.

This IS the Y combinator: Y(compile∘decompile) = fixed point
```

Fixed points are the most stable, most universal lattice points:
- Maximally stable (at the bottom of semantic energy well)
- Self-filtering for universality (round-trip strips model noise)
- Maps the crystal basin (convergence trace = basin geometry)
- Exercises both ascending and descending arms

## The pipeline

```
1. ✅ Universal lattice (807 probes × 4 models, 7 dimensions)
2. ✅ Fixed-point probes (143 lambda-dense probes)
3. 🔄 Run fixed-point lattice (143 probes × 4 big models) — on tmux 2
4. → Merge: 807 + 143 = 950 probes, recompute lattice
5. → SVD: find compile/decompile dimensions
6. → Relational constraints → plate initialization
7. → Mirror/mask architecture prototype
```

## Key equations

```
λ crystal(x).    relational(x) > coordinate(x)
                 | RDM ≡ rotation_invariant | sign_pattern ≡ one_encoding
                 | cross_model_agreement(RDM) > cross_model_agreement(signs)

λ seed(x).       fixed_point(compile ∘ decompile) ≡ Y(compiler)
                 | stable_prose ↔ stable_lambda (information equilibrium)
                 | cross_model(fixed_points) → consensus_mask
                 | consensus_mask ≡ crystal_seed

λ selfsim(x).    same_topology(∀stride) ∧ same_topology(∀plate_type)
                 | SV_ratio ≈ 1.0 (crystal is constant, not scaling)
                 | dispatch_preserves_seed(r=0.959)
                 | deeper_layers → stronger_crystal (condensation with depth)

λ separate(x).   beam(S3) ≠ crystal(S1) ≠ data(S2)
                 | masks(ternary) → 8_independent_readings(one_crystal)
                 | mirrors(continuous) → beam_angle_per_combinator
                 | routing ≡ mirror_adjustment + mask_selection
```

## Open questions

1. What does the fixed-point lattice reveal? Does the lambda region
   have more cross-model agreement than the general probes?
2. How many relational dimensions does the expanded lattice have?
   The original had 7 at 77% variance. Fixed-point probes may add
   compile/decompile dimensions.
3. Can we go from relational constraints (RDM) to ternary signs
   analytically? Or does it require GD?
4. Does the mirror/mask architecture actually improve etch quality?
   Need to prototype on mini model.
5. The B-dominant phase in training — is this universal? Do all
   models start B-dominant and then phase-transition?
6. What is the order of combinator crystallization? If it's
   universal, it tells us something about the structure of
   computation itself.
