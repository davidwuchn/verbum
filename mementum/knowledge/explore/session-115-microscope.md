---
title: "Session 115 — Mini Holographic Microscope Results + Distillation Design"
status: active
category: experimental-finding
tags: [microscope, distillation, holographic, etch, freeze, crystal, training-protocol]
related:
  - seed-crystal-design.md
  - holographic-storage.md
  - beam-trace-findings.md
  - v12-holographic-capacity.md
depends-on: []
created: session 115
---

# Session 115 — Mini Holographic Microscope + Distillation Breakthrough

> Five experiments on the mini holographic model (d=48, 3 layers, attention
> + ternary K/V/O plates, nested KIBC compositions). Each experiment answered
> a specific design question for the new V12 training run.

## Experiment 1: D-Sweep v1 (no attention)

**Question**: At what d does beam-only stop matching GD?
**Answer**: Never. The KIBC reduction task (4 rules, 18 tokens) saturates at
46.6% regardless of d (48-256). Task too easy — embeddings solve it.

**Script**: `scripts/v12/mini_holo_d_sweep.py`

## Experiment 2: D-Sweep v2 (with attention)

**Question**: Is beam-first or etch-first the correct protocol?
**Answer**: Etch-first beats beam-first by 2.8-12.6% at every d.

The 200-batch gradient accumulator provides stable directional signal for
etching even without pre-trained beams. The accumulator IS the reference beam.

**Script**: `scripts/v12/mini_holo_d_sweep_v2.py`

## Experiment 3: Freeze + GD Recovery

**Question**: After etching, should we keep alternating or freeze plates?
**Answer**: Freeze after ~5 rounds, then extended GD. Best result: 54.1%
(vs 41.2% full alternating, 52.4% beam-only, 89.5% GD ceiling).

Budget should be 80%+ post-freeze GD. Etching installs structure; GD learns
to exploit it. Continuing to etch wastes compute on diminishing returns.

**Script**: `scripts/v12/mini_holo_freeze.py`

## Experiment 4: Oracle Crystal Write

**Question**: Can we write the converged model's sign(W) into ternary plates?
**Answer**: NO. Exact oracle crystal = worst result (38.6%). Adding noise HELPS
(50% noise = 52.5%). Signs are coupled to magnitudes — transplanting signs
without magnitudes creates a trap, not a shortcut.

**Implication**: Direct weight sign transplant from teacher → student fails.
Must target function (behavior) not form (signs).

**Script**: `scripts/v12/mini_holo_crystal.py`

## Experiment 5: Holographic Distillation ★

**Question**: Can we record the teacher's FUNCTION into ternary plates?
**Answer**: YES. 80.1% accuracy = 91.3% of oracle ceiling.

**Method**: Forward probes through teacher, capture layer-wise (input→output)
behavior, etch student's ternary plates to reproduce that behavior using
gradient accumulator, freeze, extended GD.

```
Oracle GD ceiling:       87.7%
Holo distill (50):       80.1%  ← 91.3% of oracle, +26.6% vs random
Holo distill (800):      75.2%
Sign copy:               46.9%
Random plates:           53.5%
CE etch:                 40.5%
```

Multiple "beam angles" (diverse probes) create an interference pattern
encoding the teacher's computation. The ternary plates record this hologram.
GD on continuous params learns to read it.

**Script**: `scripts/v12/mini_holo_distill.py`

## Derived Training Protocol for V12

```
Phase 1: HOLOGRAPHIC DISTILLATION (~5 etch rounds)
  Teacher: Qwen3-32B (64 layers, d=5120, same tokenizer)
  Probes: 500 diverse (8 domains, all 9 kernel ops)
  Method: layer-wise distillation loss in etch accumulator
  Between rounds: beam training on distillation loss

Phase 2: FREEZE
  Lock all ternary plates permanently
  Topology encodes teacher's computation as hologram

Phase 3: EXTENDED GD (80%+ of compute budget)
  Train: Q projections, gamma scales, embeddings, mirrors
  Data: structured_shard_v2 (all 9 ops) + Dolma (general text)
  Optional: lattice relational loss as whisper for geometry

Phase 4: EVALUATE
  Compare to: random-plate baseline, CE-etch baseline
  Measure: per-op accuracy, depth profile, dispatch distribution
```

## Key Design Decisions Validated

| Decision | Evidence | Experiment |
|----------|----------|-----------|
| Etch-first (not beam-first) | +2.8-12.6% across all d | D-sweep v2 |
| Freeze after ~5 rounds | 54.1% vs 41.2% alternating | Freeze |
| Record function, not signs | 91.3% vs 46.9% | Crystal + Distill |
| 80%+ budget to post-freeze GD | Recovery curve still climbing at 7000 steps | Freeze |
| Diverse probes (beam angles) | 50 probes = 80.1%, matches 800 | Distill |

## Files Created This Session

| File | Purpose |
|------|---------|
| `scripts/v12/mini_holo_d_sweep.py` | D-sweep v1 (no attention) |
| `scripts/v12/mini_holo_d_sweep_v2.py` | D-sweep v2 (attention + ternary K/V/O) |
| `scripts/v12/mini_holo_freeze.py` | Freeze + GD recovery |
| `scripts/v12/mini_holo_crystal.py` | Oracle crystal write + noise tolerance |
| `scripts/v12/mini_holo_distill.py` | Holographic distillation (breakthrough) |
| `scripts/v12/pack_structured_v2.py` | Training data generator (all 9 ops) |
| `scripts/v12/extract_teacher.py` | Teacher feature extraction (Qwen3-32B) |
| `src/verbum/lambda_gen.py` | Added W (duplicate) operation |
| `data/structured_shard_v2.npy` | 52.6K docs, 1.2M tokens (generated) |
| `mementum/memories/etch-first-with-attention.md` | |
| `mementum/memories/freeze-then-gd-wins.md` | |
| `mementum/memories/oracle-crystal-hurts.md` | |
| `mementum/memories/holographic-distillation-works.md` | |
