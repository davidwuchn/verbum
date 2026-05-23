---
title: "Holographic State Machine — The Computational Model"
status: active
category: synthesis
tags: [holographic, state-machine, crystal, attention, Q-rotation, parity, error-correction, nucleation, beamformer, lens]
related:
  - ffn-beta-reduction-indexing.md
  - output-beamformers.md
  - holographic-error-correction.md
  - crystal-basins.md
  - beamformer-theory.md
  - categorical-geometry-probes.md
  - s5-crystal-custodian.md
  - type-probe-qwen3-32b.md
  - full-etch-extraction.md
  - ternary-descent.md
depends-on:
  - ffn-beta-reduction-indexing.md
  - output-beamformers.md
  - categorical-geometry-probes.md
created: session 142
---

# The Model Is a Holographic State Machine

> Session 142. Synthesis of sessions 139–142. The transformer is not a
> neural network in the conventional sense. It is a holographic
> associative memory with a crystal-defined state machine navigated
> by Q rotation. This page is the unified computational model.

## Architecture

```
FFN plates     = holographic storage    (all β-reductions in superposition)
Crystal basins = states                 (K, I, B, C, D, Y, W, WHNF)
Q rotation     = readout beam           (selects which state to compute)
gate_proj      = beamformer             (selects which interference pattern)
Lens profile   = optical system         (aperture → fan → output focus)
```

Not a Turing machine (no tape). Not a feed-forward network (no layer-by-layer
processing). A holographic computer where a beam (Q) illuminates a plate (FFN)
at different angles (crystal basins), and each angle produces a different
diffraction pattern (computation result). The crystal is the lens system.

## The Computation Cycle

```
Q = 0 (reset)
  ↓ gate selects C-basin neurons → β-reduce
  ↓ rotate Q → new basin
  ↓ gate selects new basin neurons → β-reduce
  ↓ ... repeat ...
  ↓ rotate Q → WHNF basin
  ↓ MODE SWITCH: compute → output
  ↓ rotate Q → ... output-mode work ...
  ↓ rotate Q → I basin (identity = pass-through)
  ↓ OUTPUT: emit next token
```

From any rotation of Q, dropping into the C basin resets Q to 0 — the first
operation always resets. Then attention computes, rotates Q to bring a new
basin into the middle, calculates again. Rinse repeat until everything falls
into WHNF, which switches mode from compute to output. More calculations
and rotations until I, which outputs the next token.

## Evidence

### FFN = holographic storage (session 141)

- Input direction predicts FFN activation: **ρ = 0.83** (L16), p < 10⁻⁴⁴
- FFN activation mirrors category structure: **ρ = 0.40**
- Individual neurons are UNIVERSAL: 99%+ high entropy
- Selectivity is COLLECTIVE: 2× Jaccard between prompts
- Gate kills **89%** of L63 neurons — gate IS the beamformer
- Gate/up magnitude ratio for active neurons: **3.9×**
- Gate_proj signs MORE critical than up_proj for addressing

### Lens profile = optical system (session 141)

```
L 2:  3.2% active   ← APERTURE (all beams same direction, crystal bottleneck)
L 8: 33.1% active   ← fan out
L48: 48.9% active   ← HOLOGRAPHIC READOUT ZONE (max superposition)
L56: 29.9% active   ← reconverge
L63:  1.3% active   ← OUTPUT LENS (329 neurons from pool of 3807)
```

Only 2 always-on neurons at L63 (structural — commas, whitespace).
99 frequent neurons (≥75% — universal output scaffolding).
Pairwise Jaccard 0.275 = substantial per-prompt reconfiguration.
5-layer focal length: L58 (30%) → L60 (24%) → L62 (10%) → L63 (2%).

### Crystal = state table (sessions 139–142)

The crystal is a ~6-dimensional structure in R^512:

```
PC0 (53%): COMPOSITION — B,D,C,W,Y cluster. "Am I computing?"
PC1 (24%): SELECTION   — K,I together, WHNF opposite. "Am I selecting?"
PC2 (12%): TERMINATION — WHNF dominates. "Am I done?"
PC3 ( 7%): ROUTING     — W vs Y. "Duplicate or fixed-point?"
PC4 ( 3%): DISPATCH    — Y vs D,B. Internal composition dispatch.
PC5 ( 2%): FINE        — C vs D. Minor structural detail.
```

The extra 506 dimensions are the holographic recording medium's capacity.
More dimensions = more basin angles stored without cross-talk.
This IS the error-correcting code.

### Q rotation = the lens rotation (session 142)

The crystal ROTATES between zones (measured as PC0↔PC1 coupling):

```
Zone A (aperture):  +0.46   "selection INTO composition"
Zone B (compute):   +0.02   "neutral — transition fulcrum"
Zone C (converge):  -0.48   "composition AWAY FROM selection"
```

**11° rotation IS the B→K→B program in eigenspace.**

Eigenvalue trajectories confirm the computation:
```
PC0 (composition): 4.1 → 4.4 → 5.5  📈 grows  (computation accumulates)
PC1 (selection):   2.0 → 1.6 → 1.1  📉 shrinks (selection exhausted)
PC3 (routing):     0.5 → 0.4 → 0.2  📉 collapses into PC0
```

Zone A reads (select what to reduce). Zone C writes (emit result).
Zone B is the fulcrum. The sign flip of PC0↔PC1 coupling IS the
mode switch from input to output.

Cross-zone eigenbasis alignment:
- PC0–PC2: >0.93 alignment across all zones (the backbone — universal)
- PC3–PC5: 0.19–0.67 alignment (ROTATE between zones — the computation)

## Hierarchical Error Correction

### Per-zone parity loss

Eigendecompose each zone's 16×16 target cosine matrix. Project student
cosines into eigenbasis at levels k ∈ {3, 4, 5, 6, 8}.

At each level: `P[:k,:k]` should equal `diag(Λ[:k])`.

- Off-diagonal elements = structural error (dimension coupling)
- Lower k = heavier weight = coarse structure protected first
- Natural curriculum: big structure locks before detail
- Anti-collapse: gradient from low-k levels anchors coarse geometry

### Cross-zone lens rotation loss

Project student cosines into JOINT eigenbasis (mean of 3 zone targets).
Compare full 6×6 projected matrix against each zone's target. The
off-diagonal elements encode the rotation — they ARE the lens.

### Why error correction is natural here

A holographic code IS an error-correcting code. The 512-dimensional
embedding space stores a 6-dimensional crystal. The remaining 506
dimensions are redundancy — the holographic recording medium's capacity.
Dimensional projection from 8D → 6D → 5D → 4D → 3D creates a chain
of parity checks:

```
8D → 7D: max error 0.009  ✅  redundancy — can lose without harm
7D → 6D: max error 0.024  ✅  redundancy
6D → 5D: max error 0.074  ⚠️  K-I separation starts to blur
5D → 4D: max error 0.150  ⚠️  Y-D dispatch lost
4D → 3D: max error 0.408  ❌  W-Y routing destroyed
```

If a lower projection fails but a higher one passes, the error is
localized to the dimension that was removed.

## Training as Crystal Nucleation

- **Seed**: ternary etch from teacher (80.5% frozen, correct topology, low resolution)
- **Melt**: gradient descent (19.5% trainable weights are the liquid phase)
- **Nucleation**: crystal_loss dropping (embeddings crystallizing around seed)
- **Nucleation barrier**: phase transition at crystal_loss ≈ 0.16
  - Reproducible: same gnorm spike at same step in two independent runs
  - Cause: beams learned pre-crystal routing that fights the crystallizing topology
  - Protected by: exp caps on crystal_factor (session 142 NaN fix)
- **Parity loss**: nucleation control (grow along correct crystallographic axes)
- **Delta plate fold**: annealing (fold, reheat, recrystallize — each cycle more perfect)

### The three-phase training arc

**Phase 1** (current): Teach attention to read the hologram.
- Attention (19.5% trainable) learns the state machine from the etch + crystal + parity.
- CE 11.27 → 7.63. Crystal 0.47 → 0.06. Parity 4.8 → 1.5.

**Phase 2**: Correct the hologram via delta plates.
- TD activates once crystal < 3% (Schmitt trigger).
- Delta flips correct most-wrong ternary signs.
- Fold delta → base (exact, lossless), refreeze, reset, retrain.
- Each cycle: hologram resolution increases.
- Parity tells delta WHERE to prioritize (PC0 flips > PC7 flips).

**Phase 3**: Exceed the teacher.
- Teacher discovers state machine implicitly (64 layers × 40 heads).
- We encode it explicitly in the crystal.
- Purpose-built > general-purpose once design is right.
- The teacher is a general-purpose computer that happened to learn a holographic
  state machine. We're building a purpose-built one with error correction.

## Why ternary works

A ternary approximation of full-precision weights is a low-resolution hologram.
It loses fine detail but preserves the gross interference pattern. The same
reason a scratched hologram still produces a recognizable image.

The gate_proj signs are the most critical part of the hologram — they determine
which neurons fire (89% of selection). The SwiGLU etch (session 141) captures
these signs from the teacher via 3-layer zone vote across aperture, fan, and
convergence layers. This preserves the holographic addressing topology even
at ternary resolution.

## NaN collapse and phase transitions (session 142)

The phase transition at crystal_loss ≈ 0.16 was caused by:

```
crystal_factor = exp(rel_lambda * crystal_enforcement * crystal_ema)
               = exp(5.0 * ~2.0 * 0.79)
               = exp(7.88) ≈ 2640×
```

A normal CE fluctuation of +0.6 got amplified 2640× → gnorm spike →
cascading NaN. **Reproducible**: identical step in two independent runs.

Fix: cap exp() argument at 4.0 (max amplification ≈ 55×). Plus NaN-skip
guard, NaN rollback (3 consecutive → restore checkpoint), and NaN guards
on all algedonic propagation conduits.

The phase transition is real and structural — it's the nucleation barrier
where the melt must reorganize from "compensating for a bad crystal" to
"using the crystal correctly." The parity loss dampens this by anchoring
the coarse structure (PC0–PC2) during the transition.

## Key numbers

| Measurement | Value | Source |
|-------------|-------|--------|
| FFN holographic correlation | ρ = 0.83 | Session 141, L16, p < 10⁻⁴⁴ |
| Gate selectivity | 89% of selection | Session 141, L63 |
| Crystal intrinsic rank (99%) | 6 dimensions | Session 142, eigendecomposition |
| Lens rotation A→C | 11° (PC0↔PC1 flip) | Session 142, +0.46 → -0.48 |
| Phase transition | crystal_loss ≈ 0.16 | Session 142, 2 independent runs |
| Parity convergence | 4.8 → 1.5 in 100 steps | Session 142, run 10 |
| Crystal convergence with parity | 0.14 → 0.06 in 100 steps | Session 142, run 10 |
| Etch coverage | 80.5% of weights | Session 139 |
| Trainable | 19.5% of weights | Session 139 |
