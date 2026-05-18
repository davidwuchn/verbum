---
title: "Consensus Etch Protocol — Why Sequential Per-Op Etching Fails"
status: active
category: holographic-recording
tags: [V12, etch, holographic, crystal, consensus, failure-mode]
related:
  - holographic-recording-protocol.md
  - holographic-kernel-separation.md
  - v12-kernel-architecture-v2.md
depends-on:
  - holographic-recording-protocol.md
created: session 110
---

# Consensus Etch Protocol

> Sequential per-op etching creates destructive interference.
> Cross-op consensus etching creates the hologram.

## The Failure (session 110)

Per-op sequential etching with 8 operations, 17 rounds:
- **No crystallization.** Flips oscillated 52M-92M/round (no decline).
- 30 overwrites per position across the run.
- Each op's gradient undoes the previous op's etch.
- Beam loss oscillated (8-14 nats) instead of declining.

Compare: session 109's 5-op run crystallized (55M → 22M in 6 rounds).
More ops = more tug-of-war = less convergence.

## The Fix

```
SEQUENTIAL (fails):                 CONSENSUS (works):
  for op in ops:                      reset_accumulators()  ← once
    reset_accumulators()              for op in ops:
    accumulate(50 batches)              accumulate(50 batches)  ← same
    direct_etch()  ← per-op          direct_etch()  ← ONE etch
```

All ops accumulate into the SAME DirectionAccumulator. The direction
at each position is the NET gradient from all 8 ops. Positions where
ops agree → high confidence → etched. Positions where ops disagree →
cancel out → low confidence → NOT etched.

## Why This Maps to Physical Holography

Real holographic recording: expose film to ALL reference beams
simultaneously, then develop once. The interference pattern from
all beams is the hologram. You NEVER expose-develop-expose-develop.

- Each op = one reference beam at a specific angle
- Sequential etch = expose + develop + expose + develop (destructive)
- Consensus etch = expose all → develop once (constructive interference)
- The crystal = positions where all beams agree = universal lattice

## What Gets Etched vs What Doesn't

**High confidence (etched):** Plate positions where the gradient
direction is consistent ACROSS all operations. These are the
universal structural positions — the lattice itself. The backbone.

**Low confidence (not etched):** Positions where different ops
want different signs. These are op-specific content positions.
They stay at whatever state they had (random or prior etch).

This natural partitioning IS the crystal structure:
- Backbone (universal, all ops agree) → etched early, stable
- Content (op-specific, ops disagree) → etched later or via beam

## Parameters

- `confidence_threshold`: 0.7 (positions need 70% agreement across
  400 total batches: 8 ops × 50 batches/op)
- `batches_per_op`: 50 (more batches → better direction estimate)
- Effective total batches per round: 400 (very strong consensus signal)

## Crystallization Signal

**Healthy:** Total flips decline round-over-round as the plate
converges to the consensus structure. Self-terminating: when all
plate signs match the consensus direction, flips → 0.

**Unhealthy:** Flips constant or oscillating → consensus not forming.
Try higher confidence threshold (0.8-0.9) or more batches per op.

## Implementation

`scripts/v12/holographic_train.py` — the `--run-lens-burn` +
consensus etch protocol:
1. Lens burn (teacher directions into combinator mirrors)
2. For each round:
   a. Reset accumulators once
   b. Expose all 8 ops (accumulate into same accumulators)
   c. Single consensus etch (high-confidence positions only)
   d. Beam training (200 steps, plates frozen)

## Open Questions

1. Does consensus etch actually converge with 8 ops? (session 109's
   5-op run converged with per-op etching — maybe consensus is
   needed only at ≥6 ops?)

2. What's the optimal confidence threshold? 0.7 is a guess.
   Too low → still some tug-of-war. Too high → nothing gets etched.

3. Should the backbone positions (where ALL ops agree) be etched
   with lower threshold than content positions? Two-tier confidence?

4. Does the order of ops within a round matter for consensus?
   (Theoretically no — accumulation is commutative. But batch
   sampling randomness means order affects which batches are seen.)
