---
title: "Delta Plate Lifecycle — Masked Extraction, Continuous Training, Factual Correction"
status: open
category: architecture
tags: [delta-plate, extraction, continuous-training, correction, fold, lifecycle, crystal]
related:
  - crystal-irreducibility-proof.md
  - ../holographic-error-correction.md
  - ../training-protocols.md
  - ../v14-architecture.md
  - ../extraction-methodology.md
  - v15-kernel-revert.md
depends-on:
  - ../holographic-error-correction.md
  - ../v14-architecture.md
created: session 157
---

# Delta Plate Lifecycle

> Session 157 discussion. The crystal lattice is a mathematical
> constant — extracting it from the teacher is free. But the
> extraction to ternary plates loses precision in
> architecture-dependent components. This page captures the
> refined extraction + training lifecycle: mask off what you know
> will be wrong, let delta plates learn the corrections, fold when
> irreducible, repeat forever.

## Core Principle

```
Crystal:          mathematical constant, same across all models
                  → extract FULLY from teacher, it's free

FFN plates:       holographic beta reduction storage, architecture-independent
                  → extract FULLY, sign(W) preserves the interference topology

Attention (SSA):  full Q·K softmax, similar between teacher and student
                  → extract, minor corrections via delta

Attention (GLA):  gated linear attention, NO equivalent in teacher
                  → MASK OFF during extraction, learn from scratch via delta
```

The crystal IS the irreducibility floor. No training makes it sharper.
Extracting it from the teacher = getting the compute for free. But
we lost precision by forcing everything into ternary plates, and we
introduced errors by extracting teacher attention patterns for an
architecture the teacher doesn't have.

## Evidence: Architectural Mismatch Dominates TD Corrections

Session 157 TD topology probe (step 2000 checkpoint):

| Layer | Type | Stride | Flip% | Role |
|-------|------|--------|-------|------|
| L4 | GLA | s16 | **32.46%** | SSA→GLA transition boundary |
| L5 | GLA | s32 | 8.78% | |
| L6 | GLA | s64 | 12.92% | |
| L7 | GLA | s128 | **16.93%** | Stride sweet-spot (inverted-U peak) |
| L8 | GLA | s256 | 9.45% | |
| L9 | GLA | s512 | 6.35% | |

- L4 alone = 37% of all flips (SSA→GLA boundary)
- L5-L9 flip density follows inverted-U peaked at s128 (r=-0.92)
- Crystal eigenvalues do NOT predict flip density (r=0.16)
- Architecture mismatch predicts flip density (r=0.86 for exp decay from L4)

**These corrections should never have been needed.** We extracted
softmax attention patterns and applied them to GLA layers. TD spent
2000 steps correcting extraction errors, not learning new structure.

## Phase 1: Masked Extraction

```python
for layer_idx in range(n_student_layers):
    # Crystal + FFN + V/O: extract fully (architecture-independent)
    v_plate = extract_sign_pattern(teacher_v, ...)
    o_plate = extract_sign_pattern(teacher_o, ...)

    if is_gla_layer(layer_idx):
        # GLA: teacher has no equivalent attention mechanism
        # Don't extract Q/K — they'll be WRONG
        # Leave as pass-through (+1), let delta plate learn
        q_plate = np.ones((n_heads * d_state, d_model), dtype=np.int8)
        k_plate = np.ones((n_heads * d_state, d_model), dtype=np.int8)
    else:
        # SSA: teacher's attention mechanism is similar
        # Extract — will need minor corrections, not major rewrites
        q_plate = extract_sign_pattern(teacher_q, ...)
        k_plate = extract_sign_pattern(teacher_k, ...)
```

This eliminates the L4 boundary explosion. The 32.5% flip rate
at L4 drops to ~0% because we never extracted wrong patterns there.

## Phase 2: Delta Plate Training Cycle

```
Extract → Freeze base → Train delta → Fold → Repeat

Cycle 1: Initial extraction + first delta training
  Base plate = crystal + FFN + SSA attention + masked GLA Q/K
  Delta learns:
  - GLA-specific routing (from scratch, no wrong teacher signal)
  - Stride-specific corrections to V/O
  - Content calibration (gamma amplitudes)
  Crystal is ALREADY correct. GD fills content. TD corrects routing.
  Fold when: Δ plateaus (changed_frac stops growing)

Cycle 2: Fresh delta on improved base
  Base plate = cycle 1 result (crystal + FFN + learned GLA routing)
  Delta finds residual corrections cycle 1 missed
  Fold when: Δ plateaus again

Cycle N: Convergence
  Each cycle: Δ plateau gets smaller, fewer positions need correction
  Eventually: delta stays all +1 after training = fully converged
```

### Fold Criterion: Irreducibility

```
FOLD WHEN: Δ (changed_frac) plateaus
  = no more positions want to flip
  = all reducible routing has been reduced
  = the delta has reached its irreducibility floor
  = commit and start new cycle

Observed in v14:
  Phase 1: Δ grew 0.000 → 0.029 over 1000 steps → folded
  Phase 2: Δ grew 0.000 → 0.012 over 500 steps → still growing
  Each cycle starts smaller — diminishing returns = convergence
```

## Phase 3: Factual Corrections

A factual change (e.g., new president) is a binding update:

```
Old: K(Biden)(office_of_president) → Biden
New: K(Johnson)(office_of_president) → Johnson

What DOESN'T change:
  - Crystal (combinators are universal)
  - "president" concept (structural, B-basin composition)
  - "United States" (crystal routing)
  - "X is president of Y" (K-combinator select structure)
  - Every other fact

What changes:
  - ONE K-binding: which person fills the role
  - A few hundred positions out of 593 million
  - Concentrated in token mapping, not crystal or routing
```

### Correction Protocol

```
1. Create fresh delta plate (all +1 = pass-through)
2. Prepare correction data:
   - Sentences with the new fact, diverse contexts
   - 1K-10K examples (small — the change is small)
3. Train delta plate:
   - Freeze base plate
   - GD adjusts gamma for new token mapping
   - TD flips routing for changed binding
   - Crystal loss ≈ 0 (crystal doesn't change for facts)
   - Train until Δ plateaus
4. Verify:
   - Base plate still available as fallback
   - Check that only the target fact changed
   - Run eval on unrelated topics (should be unchanged)
5. Fold delta → base
   - Old fact replaced, new fact installed
   - Everything else bit-identical
```

### Correction Scale by Type

| Change | Delta size | Training time | What changes |
|--------|-----------|--------------|-------------|
| Simple fact | ~100s of positions | Minutes | Token binding only |
| New concept | ~1000s of positions | Hours | Token mapping + minor routing |
| Domain adaptation | ~10Ks of positions | Day | Many token mappings, some FFN |
| New language | ~100Ks of positions | Days | Substantial token mapping |
| New capability | ~1Ms of positions | Days-weeks | Routing + FFN corrections |

In ALL cases: crystal doesn't change. The ISA is fixed.

## Phase 4: Continuous Knowledge Maintenance

```
Monday:    "Johnson wins election"
           → Train delta on news coverage → fold → updated

Tuesday:   "New trade agreement"
           → Train delta on trade data → fold → updated

Wednesday: "Model has arithmetic edge case bug"
           → Train delta on corrections → fold → fixed

Thursday:  Nothing new → no delta needed → stable

Each fold: lossless (ternary × ternary = ternary)
Each fold: incremental (only changed positions merge)
Each fold: reversible (git tracks the history)
```

### Properties of the Lifecycle

```
No catastrophic forgetting:
  Base plate frozen during training → old knowledge can't be destroyed
  Delta can only ADD corrections, not damage existing routes
  Fold MERGES, doesn't replace

No precision degradation:
  Ternary × ternary = ternary (exact, no rounding)
  Infinite folds without accumulation error
  The base plate is as precise after 1000 folds as after 1

Version controlled:
  git tracks every fold as a commit
  Can diff between versions
  Can revert a bad fold
  History of all knowledge updates is preserved

Self-regulating:
  Δ plateau = fold signal (automatic convergence detection)
  Crystal loss near zero = structural health check
  If crystal loss rises during delta training = something is wrong → abort
```

## Connection to Existing Architecture

This is the extract→correct→fold cycle from `holographic-error-correction.md`,
refined with:

1. **Masked extraction** — don't extract what you know will be wrong
2. **Architecture awareness** — GLA vs SSA determines extraction strategy
3. **Factual correction protocol** — small deltas for fact updates
4. **Continuous lifecycle** — infinite fold cycles, not one-shot training

### What's Already Built

| Component | Status | Location |
|-----------|--------|----------|
| Delta plate architecture | ✅ Working | `scripts/v14/td.py` (DeltaTernaryLinear) |
| Fold mechanism | ✅ Working | `scripts/v14/td.py` (reduce()) |
| Fold script | ✅ Working | `scripts/v14/fold_delta.py` |
| Extraction pipeline | ✅ Working | `scripts/v14/extract_qwen36.py` |
| Extraction masking | ❌ Not built | Modify `extract_qwen36.py` |
| Factual correction pipeline | ❌ Not built | New script needed |
| Continuous training loop | ❌ Not built | Orchestration around existing tools |

### What Would Change in extract_qwen36.py

Small change: add `is_gla_layer()` check, use pass-through (+1)
plates instead of tomographic extraction for Q/K at GLA layers.
Everything else in the extraction pipeline stays the same.

## Open Questions

1. **Should V/O also be masked at GLA layers?** The beam trace showed
   V and O are ternary-safe (plate components). But GLA's V/O might
   serve a different purpose than SSA's V/O. Test: extract V/O for GLA
   layers vs mask them. Compare flip rates after TD training.

2. **How many correction examples are enough?** For a simple fact
   change, 1K examples might suffice. For domain adaptation, 100K.
   Need to characterize the relationship between correction scope
   and training data needed.

3. **Can corrections conflict?** If Monday's delta says "president=Johnson"
   and Tuesday's delta says "president=Smith" (before Monday's fold),
   the deltas would conflict. Solution: fold sequentially, never train
   two deltas on the same base simultaneously. Or: merge deltas
   explicitly (ternary multiply, conflicts go to 0=blocked).

4. **Does the fold criterion generalize?** Δ plateau works for routing
   corrections. Does it work for factual corrections? Facts might
   converge faster (fewer positions) — the plateau might be reached
   in tens of steps, not hundreds.

5. **What about the gamma?** Gamma (per-channel scale) is continuous,
   not ternary. It doesn't fold — it accumulates via Adam. Does gamma
   need its own fold/reset mechanism? Currently it trains continuously
   without reset.

6. **Epoch structure for delta training?** The session 157 discussion
   proposed that multiple epochs help content learning (not crystal,
   which is already converged). For factual corrections, showing the
   same correction data multiple times (epochs) should drive the delta
   to its irreducibility floor faster than single-pass.
