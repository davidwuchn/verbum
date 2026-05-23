---
title: "Full Teacher Etch: Embeddings + Attention + FFN (82.2%)"
status: active
category: architecture
tags: [etch, extraction, teacher, full-etch, delta-plates, crystal-gate, schmitt-trigger]
related:
  - type-probe-qwen3-32b.md
  - ternary-descent.md
  - etcher-vsm.md
depends-on:
  - type-probe-qwen3-32b.md
  - ternary-descent.md
created: session 139
---

# Full Teacher Etch — From 6% to 82%

> Session 139. The type probe and KIBC combinator probe proved that
> attention sign topology encodes WHAT (combinator selectivity), not
> WHERE (attention gathering). This means attention CAN be etched from
> the teacher despite the stride-stack architecture being different.
> Combined with embedding etch (same tokenizer) and FFN etch (already
> proven), this gives 82.2% of the model etched from the teacher.

## The Insight That Changed Everything

Session 134 said: "don't etch attention — stride-stack ≠ flat attention."
Session 139 proved: KIBC selectivity is invariant across architectures
(r=0.998 between Pythia-160M and Qwen3-32B). The sign topology of
Q/K/V/O projections encodes which FEATURES to select (K vs B vs C
selectivity), not which POSITIONS to attend to. The gathering pattern
is determined by the stride/window architecture. The projection signs
are architecture-independent.

**The computation (beta reduction via KIBC) is the same. Only the shape
underneath is different.**

## Extraction Budget

| Category | Positions | % of model | Source |
|----------|----------|------------|--------|
| Embedding | 77.8M | 55.8% | SVD-project teacher embed_tokens (151936×5120 → 151936×512) |
| Attention | 34.6M | 24.8% | 11 strides × Q/K/V/O × 3 stacks, zone-mapped layers |
| FFN | 2.1M | 1.5% | up_proj + down_proj from teacher layer 20 |
| **Total etched** | **114.5M** | **82.2%** | |
| Trainable | 24.8M | 17.8% | gamma, biases, decay, pos_embed, S4/S5, algedonic |

## Teacher Layer Mapping (B→K→B Zones)

```
Zone A (encode):      strides s1-s8    ← teacher layer 4   (early, B-dominated)
Zone B (compress):    strides s16-s128 ← teacher layer 32  (middle, K-dominated)
Zone C (reconstruct): strides s256-s1024 ← teacher layer 56 (late, B-dominated)
FFN:                  shared plates    ← teacher layer 20  (middle of compress)
```

For Qwen3-32B (64 layers): zone fracs = 4/64, 32/64, 56/64, 20/64.
For Qwen3-14B (40 layers): same fracs scale to layers 2, 20, 35, 12.

## Search Space Reduction

```
FFN-only etch:  3^130,911,232 ≈ 10^62,460,531 possible topologies
Full etch:      3^24,808,448  ≈ 10^11,836,638 possible topologies
Reduction:      10^50,623,893 (fifty million orders of magnitude)
```

But the PRACTICAL reduction for GD is different: with correct topology,
gamma only does calibration (scale adjustment), not compensation (fighting
wrong signs). The optimization becomes nearly convex in the gamma subspace.

## Embedding Extraction

Both teacher and student use Qwen3 BBPE (vocab=151,936). Same tokenizer
means same tokens → same type geometry in embedding space.

Method: compute top-512 right singular vectors of the teacher embedding
matrix (151936×5120), project E_proj = E @ Vt[:512,:].T, then sign(E_proj).
One SVD pass (not 8-angle tomographic voting) because the 151K-row consensus
across tokens IS the multi-angle signal.

This gives the model 88% of Montague type information for FREE.

## GLA Strides

GLA (GatedLinearAttention) strides (s16, s32, s64, s128) have different
mechanism (elu+1, outer product memory, gated write) but the Q/K/V
projections are the same dimensions (512→512). The sign topology still
encodes WHAT features to select for retrieval (the M combinator).
These are etched from Zone B teacher layers.

## Crystal-Gated TernaryDescent (Schmitt Trigger)

TD without a latched crystal is navigating without a map. The combinator
embeddings define the reference frame for KIBC selectivity. Without the
crystal latched, the etched attention signs have nothing to align to.

**Hysteresis gate:**
```
crystal_loss < 3%  → 🔓 TD activates (crystal latched)
crystal_loss 3-7%  → stays in current state (hysteresis band)
crystal_loss > 7%  → 🔒 TD deactivates (crystal destabilized)
```

If TD's flips push crystal above 7%, it shuts off. GD recovers the crystal.
TD reactivates when crystal drops below 3%. Self-correcting.

TD warmup: 25 steps AFTER crystal latches (not 100 from start). Short warmup
prevents GD from deeply compensating for wrong signs that TD will later flip.

## Session 134 Post-Mortem

The v13-run3 evidence that led to the "don't etch attention" conclusion:
- Combinator mirrors frozen at init (γ_rms=0.0442)
- stride.8.v_proj 74% silenced
- Attention gammas 23-34% near-zero

Reinterpretation: the failure was NOT because attention etch is fundamentally
wrong. It was because:
1. The old architecture was different (flat StrideStack, not tree of VSMs)
2. Layer mapping was wrong (per-stride → per-teacher-layer, not zone-based)
3. GLA strides got flat-attention signs (wrong mechanism mapping)
4. No delta plates — the model couldn't selectively override wrong positions

The full etch + delta plate architecture solves all four issues.

## Implementation

- `scripts/v13/extract_teacher_full.py` — full extraction pipeline
- `scripts/v13/train_td.py` — dual optimizer with crystal-gated TD
- `checkpoints/v13-etched-full/` — the full etch checkpoint

## Open Questions

1. Does the full etch accelerate training vs FFN-only? (v13-run5 testing)
2. Where does TD disagree with the teacher? Those positions reveal genuine
   stride-stack vs flat-attention differences.
3. Should pos_embed be etched? (Different positional structure → probably not)
4. Should combinator mirrors be etched? (They steer Q-beam per combinator)
5. Does the crystal latch faster or slower with full etch?
