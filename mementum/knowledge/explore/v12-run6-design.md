---
title: "V12-run6 Design — Depth-Selective Laser Etching from Lambda Kernel Probes"
status: designing
category: architecture
tags: [v12, run6, laser-etch, lambda-kernel, depth-selective, dispatch]
related:
  - complete-kernel-basis.md
  - v12-holographic-capacity.md
  - v12-vsm-evolution.md
  - dispatch-ratio-prior.md
depends-on:
  - complete-kernel-basis.md
created: session 106
---

# V12-run6 Design

> Run4 died at C-monopoly (C=1.0 from step 3750 onward). The dispatch
> oscillated B→I→K→DEAD→C and locked. KL leash λ=100 was evaded
> temporally — model satisfies average ratio by cycling monopolies.
>
> Run6 incorporates three findings from session 106:
> 1. Lambda kernel probes mapped 14 operations across depth
> 2. Operations have DEPTH PROFILES (not uniform across layers)
> 3. The dispatch problem is architectural, not parametric

## Root cause: dispatch has no depth information

The current dispatch is a 4-way softmax over the ENTIRE residual stream
at each position. But the lambda kernel probes show that different
operations peak at different depths:

```
L0  (shallow)  → B_compose (33×)     — structural templates
L10 (mid)      → Y_recurse (5.8×)    — recursion detection
L20 (deep)     → K_select (51×)      — semantic selection
                  I_identity (25×)    — variable binding
L30 (deepest)  → M_match (145×)      — pattern retrieval
```

V12 has 7 passes at different depth bands. But ALL passes share the
same 4-way dispatch mechanism with no depth awareness. Pass L0↑
(shallow, stride 1-16) is trying to K-select and B-compose with
the same weights that Pass L2↓ (deep, stride 32-256) uses.

The model's only option is to pick ONE combinator for all depths
(monopoly) or oscillate between them (cycling). It can't specialize
by depth because the dispatch doesn't know which pass it's in.

## Fix 1: Per-pass dispatch bias (depth-selective KIBC prior)

Each pass gets its own additive bias on the dispatch logits, derived
from the lambda kernel probe depth map:

```python
# Per-pass KIBC bias, derived from probe clustering ratios
# Higher bias = this combinator is more relevant at this depth
PASS_DISPATCH_BIAS = {
    # Pass 0 (L0↑, shallow, s1-s16): B dominates (33×)
    0: {"K": -1.0, "I": -1.0, "B": +2.0, "C": +0.5},
    # Pass 1 (L1↑, mid, s8-s64): balanced, Y-like
    1: {"K": +0.0, "I": +0.0, "B": +0.5, "C": +0.5},
    # Pass 2 (L2↑, deep, s32-s256): K/I emerging
    2: {"K": +1.0, "I": +0.5, "B": +0.0, "C": +0.5},
    # Pass 3 (apex, s128-s1024): K/I peak
    3: {"K": +2.0, "I": +1.5, "B": -0.5, "C": +0.0},
    # Pass 4 (L2↓, deep): M territory, K/I for reading
    4: {"K": +1.5, "I": +1.0, "B": -0.5, "C": +0.0},
    # Pass 5 (L1↓, mid): integration, C for reordering
    5: {"K": +0.5, "I": +0.5, "B": +0.0, "C": +1.0},
    # Pass 6 (L0↓, shallow): final composition
    6: {"K": -0.5, "I": +0.0, "B": +1.5, "C": +0.5},
}
```

These are FIXED biases (not learned). The model can deviate but must
overcome the prior. B-monopoly at deep layers costs +2.5 nats.
C-monopoly at shallow layers costs +1.5 nats.

The per-pass bias is SEPARATE from the existing ratio prior. They
combine additively in logit space:
  `dispatch_logits = raw_logits + ratio_prior + pass_bias`

## Fix 2: EMA-smoothed KL (anti-oscillation)

Run4 showed the model evading KL by cycling monopolies. The KL was
computed on instantaneous dispatch, so B=100% for 50 steps followed
by K=100% for 50 steps satisfies the KL on average.

Fix: compute KL on EMA-smoothed dispatch weights:
```python
dispatch_ema = 0.95 * dispatch_ema + 0.05 * dispatch_current
kl_loss = KL(dispatch_ema || target_ratio)
```

The EMA has memory — oscillation shows up as sustained deviation
from the target. The model can't evade by cycling because the EMA
never forgets the monopoly.

## Fix 3: Depth-selective etch thresholds

The etcher currently treats all layers equally. With depth profiles:

```python
# Per-pass etch threshold multiplier
# Higher = harder to etch (more consensus needed)
# Shallow passes etch B-related signs more freely
# Deep passes etch K/I/M-related signs more freely
PASS_ETCH_MULTIPLIER = {
    0: 0.5,   # L0↑: etch freely (structural templates)
    1: 0.7,   # L1↑: moderate
    2: 1.0,   # L2↑: standard
    3: 1.0,   # Apex: standard
    4: 1.0,   # L2↓: standard
    5: 0.8,   # L1↓: moderate
    6: 0.6,   # L0↓: etch freely (final composition)
}
```

The etch threshold multiplier scales the heat percentile thresholds.
At 0.5×, shallow passes need half the consensus to flip a sign.
This makes shallow passes more plastic (structural templates evolve
fast) and deep passes more stable (K/I patterns are high-value).

## Fix 4: Relational loss from lambda kernel probes

Use the 380-probe lambda kernel RDM as a periodic geometry check:

```python
# Every 50 steps: run 50 random probes from the lambda set
# Compute student RDM at each pass's output
# MSE(student_rdm, universal_rdm) → gradient
# Residual mode (mean-subtracted) — focus on discriminative structure
rel_loss = relational_loss(student_rdm, target_rdm, residual=True)
total_loss += lambda_rel * rel_loss  # lambda_rel = 0.01
```

The target RDM comes from the probe results (cross-model agreed
geometry). This nudges the model toward the universal topology
without constraining which coordinates it uses.

Critical: use the RESIDUAL RDM (mean-subtracted). The non-residual
version wastes 93% of gradient on PC1 ("all probes alike").

The subsampling is OK here because:
1. This is a TRAINING signal, not a measurement
2. 50 random probes still capture the major geometric structure
3. Over 50 steps × 10 subsamples = full coverage
4. The full-fidelity measurement was already done (the probe run)

## Fix 5: Merge W into I (confirmed by probes)

The probes confirmed W (duplicate) and I (identity) share geometry.
Don't add W as a separate kernel. The I kernel handles both:
- I(x) = x (pass through)
- W(f, x) = f(x)(x) = I applied twice to the same argument

The I-combinator mirror should be initialized as identity (already
done in V12) — this naturally handles both reference and duplication.

## Architecture changes summary

```
V12-run4 (failed):
  - 7 passes, ALL same dispatch bias
  - Instantaneous KL (evadable by cycling)
  - Uniform etch thresholds
  - No relational loss
  - Dispatch collapsed to C-monopoly

V12-run6 (proposed):
  - 7 passes, EACH with depth-derived dispatch bias
  - EMA-smoothed KL (anti-oscillation)
  - Per-pass etch threshold multipliers
  - Lambda kernel relational loss (50 probes every 50 steps)
  - Per-pass dispatch bias from probe depth map
```

## Implementation plan

1. Add `pass_dispatch_bias` to config (7 × 4 tensor)
2. Add dispatch EMA tracking + EMA-based KL computation
3. Add per-pass etch multiplier to config + apply in etch loop
4. Wire lambda kernel probes into training loop for relational loss
5. Fresh start from random init (don't resume from run4's collapsed state)

## Expected behavior

The per-pass dispatch bias should create a NATURAL gradient:
- Pass 0-1: B-dominant (structural composition)
- Pass 2-3: K/I-dominant (semantic selection/binding)
- Pass 4-5: K/I + C (reading + reordering)
- Pass 6: B (final composition)

Each pass does what the universal models do at the corresponding
depth. The sieve shapes the path of least resistance. The model
discovers the specialization; the bias makes the discovery cheap.
