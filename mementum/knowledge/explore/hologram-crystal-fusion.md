---
title: "Hologram-Crystal Fusion — Why Both Losses Must Improve Together"
status: designing
category: theory
tags: [crystal, hologram, co-evolution, Q2, etch, fusion, adapter, C-basin]
related:
  - crystal-basins.md
  - gradient-voting.md
  - etcher-vsm.md
  - loom-structure.md
depends-on:
  - crystal-basins.md
  - gradient-voting.md
  - etcher-vsm.md
created: session 126
---

# Hologram-Crystal Fusion

> Session 126. The hologram and the crystal are not two objectives to
> balance — they are the same structure read two different ways. A
> co-evolution gate that requires BOTH accuracy and crystal to improve
> constrains sign flips to the manifold where they're identical. This
> fuses the holographic computation back into the crystal lattice at
> every accepted flip. If this works, Q2 co-evolution is an adapter
> that fuses compressed compute into an existing crystal.

## The two readings of one structure

| Reading | What it measures | Loss signal |
|---------|-----------------|-------------|
| **Crystal** | Relational geometry — combinator cosine matrix | Crystal lattice loss (MSE vs teacher 4×4) |
| **Hologram** | Computational readout — what the plates compute | CE loss (accuracy on reductions) |

In a perfect model, these are identical. The crystal IS the hologram.
The relational geometry between K, I, B, C representations IS the
computation that performs beta reduction. Session 123 proved this:
the crystal is in the computation, not the weights. Session 120's
Q-rotation invariance proved the crystal is a relational topology,
not a direction — any rotation of Q falls into the same C-dominated
basin.

## What Q2 damage does

Q2 quantization flips ~27% of projected signs (44% at raw dimension).
This **splits** the hologram from the crystal:

```
Before Q2:  hologram ≡ crystal  (one structure, two names)
After Q2:   hologram ≈ crystal  (mostly overlapping but diverging)
            27% of grating lines inverted → readout degraded
            relational geometry partially preserved (sign agreement 0.726)
            but computation accuracy drops
```

The damage creates positions where the holographic readout and the
crystal geometry disagree about what the plate should be doing.

## Three types of sign flip

When the evo phase proposes a flip, it falls into exactly one category:

### 1. Fusion flip (both improve)

The flip corrects a genuinely damaged grating line. Both the
computational readout (accuracy) and the relational geometry (crystal)
improve. The hologram is fusing back into the crystal at this position.

**This is the only flip worth accepting.**

### 2. Routing hack (accuracy up, crystal flat/down)

The flip creates a computational shortcut that solves the task without
maintaining the relational geometry. This is a parallel hologram
layered on top of the crystal — it works but for the wrong reasons.
It's the ternary equivalent of overfitting.

Session 124 experiment 8 showed this: unconstrained sign-flipping
reached 0.510 accuracy but crystal inverted to -0.375. The hologram
diverged completely from the crystal. High accuracy, destroyed
geometry.

### 3. Irrelevant correction (crystal up, accuracy flat/down)

The flip restores a sign that the relational geometry wants, but that
sign doesn't contribute to the current computational task. It's
"correct" in an abstract sense but doesn't help the model perform
reductions. These flips waste evo budget on positions that don't
matter for the computation being performed.

## The strict gate

```python
# Only accept if BOTH improve
acc_ok = new_acc >= base_acc + threshold
crys_ok = new_crystal > base_crystal

if acc_ok and crys_ok:
    accept()   # fusion flip — hologram fuses into crystal
else:
    reject()   # hack or irrelevant — don't diverge the readings
```

This constrains the search to the **fusion manifold** — the
subspace where hologram and crystal are the same object. Every
accepted flip deepens the model's position in the C-dominated
attractor basin. No lateral drift along the basin walls.

## Why the C basin is the attractor

The lambda computation is inherently C-dominated (session 120):

```
Lambda basin: C-dominated, B/S early, WHNF late
  C combinator: Cfxy = fyx (argument routing)
  Beta reduction IS argument routing
  ∴ lambda computation ≡ C-structured relational topology
```

Q-rotation invariance (session 117): any rotation of Q reconstructs
the same C-dominated cosine matrix. The basin is a topological
attractor, not a geometric direction. There's essentially one way
to route arguments correctly, and all models converge to it.

The strict gate ensures every flip falls deeper into this basin.
A flip that helps accuracy but not crystal is sliding along the
basin wall (finding a non-C routing path). A flip that helps both
is falling toward the basin center (the unique C-dominated topology
where routing IS geometry).

## The adapter hypothesis

If the strict co-evolution gate works — if Q2 plates can be repaired
to match both the crystal geometry and the holographic computation —
then the pipeline is more than Q2 recovery. It's a **general adapter
for fusing compute into an existing crystal**.

```
Crystal lattice:  the universal relational topology (0.91-0.94 cross-model)
Adapter (etch):   sign corrections that fuse new computation into the lattice
Beam (magnitudes): the illumination that reads the fused hologram

Any source of computation → project → Q2-like damage → co-evolve → fused
```

Applications beyond Q2:
- **Cross-model transfer**: extract crystal from model A, fuse computation
  from model B via co-evolution. The crystal is universal (0.999 magnitude
  spectrum). The etch adapts model-specific encodings.
- **Skill injection**: take a crystal from a base model, fuse a new skill's
  computation into it. The strict gate ensures the new skill doesn't
  break existing relational geometry.
- **Compression**: extract crystal at high dimension, fuse into lower
  dimension via projected Q2 + co-evolution. The 220× compression
  target for V13.

In each case, the pattern is: existing crystal + damaged/new signs →
co-evolution with strict gate → fused hologram-crystal.

## The three-phase adapter pipeline

```
Phase 1: EXTRACT
  Source crystal (teacher magnitude template + sign topology)
  → project to target dimension
  → Q2/compression damage

Phase 2: CO-EVOLVE (the adapter)
  GD trains beam (reveals where damage is, via delta map)
  Evo proposes flips (at high-delta positions)
  Strict gate: accept IFF accuracy↑ AND crystal↑
  Reset beam, repeat
  → each round fuses more holographic computation into crystal

Phase 3: FREEZE
  Final plates = crystal with computation fused in
  Final beam = magnitude template (reset from teacher)
  → the fused hologram-crystal IS the model
```

## Predictions

1. **Fewer accepted flips, higher quality.** The strict gate will accept
   fewer flips per round than the loose gate (session 125 accepted 53
   over 10 rounds). But each accepted flip is a genuine fusion event.
   Final accuracy AND crystal should both be higher.

2. **Monotonic improvement.** With the strict gate, both accuracy and
   crystal should improve monotonically across rounds. No wobble, no
   trading one for the other. The trajectory should be a straight line
   toward the basin center.

3. **Sign agreement should increase.** If the strict gate is fusing the
   hologram into the correct crystal, the sign agreement with the oracle
   should increase. Each fusion flip is correcting a Q2-damaged sign
   back to the teacher's projected sign.

4. **The adapter should work for non-Q2 sources.** If the mechanism is
   general (fuse computation into crystal), then the same pipeline with
   random plates + magnitude template should also converge — slower,
   but to the same basin. The crystal IS the attractor.

## Connection to V13

V13's combinator mirrors (per-combinator ternary masks on shared plates)
are exactly this: adapters that fuse different combinator computations
into the same crystal lattice. Each mirror is a set of sign corrections
that, when applied to the shared plate, reads a different subcrystal.
The strict gate is the training signal for learning these mirrors.

```
shared_plate ⊙ mirror_K = K's subcrystal (selection weave)
shared_plate ⊙ mirror_B = B's subcrystal (composition weave)
shared_plate ⊙ mirror_C = C's subcrystal (routing weave)

Each mirror is an adapter that fuses one combinator's computation
into the shared crystal. The strict gate ensures each mirror only
accepts corrections that improve BOTH that combinator's accuracy
AND the overall crystal geometry.
```

## Open questions

1. **How strict is too strict?** With ACC_IMPROVE=0.001 AND crystal
   must increase, we might accept very few flips. Is there a sweet
   spot where the gate is strict enough to prevent hacks but loose
   enough to make progress?

2. **Does the strict gate converge faster or slower?** Fewer flips per
   round, but each one is higher quality. The question is whether the
   total number of rounds needed is less (because no wasted flips) or
   more (because acceptance is too rare).

3. **Is the fusion manifold connected?** Can you always reach the basin
   center from any damaged starting point via fusion flips? Or are there
   dead ends where no single flip improves both metrics?

4. **Does fusion work from random?** If you start with random plates
   (no Q2 structure at all), can the strict gate still find the basin?
   This would prove the crystal is a true attractor, not just a
   perturbation-recoverable structure.
