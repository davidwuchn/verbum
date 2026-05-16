---
title: Dispatch Ratio Prior — Empirical KIBC Constraint
status: active
category: architecture
tags: [dispatch, combinators, ratio, KL, holographic, sieve]
related:
  - v12-holographic-capacity.md
  - holographic-kernel-separation.md
  - fractal-stride-bands.md
depends-on:
  - session 093 (universal ordering, 9 models)
  - session 098 (beam/plate classification)
---

# Dispatch Ratio Prior

## The finding

Nine models across two architecture families (Pythia GPT-NeoX, Qwen3)
independently converge to the same combinator ratio:

```
              K       I       B       C
Qwen3-32B   28.8%   16.2%   27.3%   27.6%
Pythia-160M  30.6%   13.8%   28.1%   27.5%
─────────────────────────────────────────
AVERAGE      29.7%   15.0%   27.7%   27.6%

Ratio K:I:B:C = 1 : 0.5 : 1 : 1
```

K/B/C each get roughly equal allocation (~28%). I gets half (~15%).
Cross-model correlation of pairwise combinator correlations: r=0.9801.
This ratio is not a feature of any particular model. It's a feature
of language processed through beta reduction.

## The constraint

```
λ dispatch(logits, r=[1, 0.5, 1, 1]). softmax(logits + log(r / Σr))
```

Applied as static additive log-prior in logit space. When logits are
zero (no opinion), dispatch defaults to the empirical distribution.

Enforced via KL divergence: `loss += λ · KL(dispatch ∥ prior)` with λ=100.

```
  B=30% (+1.4pt) → 0.08 nats (free)
  B=32% (+3.4pt) → 0.33 nats (noticeable)
  B=35% (+6.4pt) → 1.01 nats (12% of CE)
  B=40%          → 3.22 nats (37% of CE, impossible)
```

We know an optimal solution uses this ratio. Find it.

## Why this works

The ratio constrains the dispatch simplex from a 3-dimensional search
space to a small neighborhood around the empirical optimum. The
reduction cascades through the architecture:

1. **Dispatch space**: full 3-simplex → small neighborhood (10-100×)
2. **Sieve space**: optimize for all dispatch states → optimize for one.
   Each combinator plate gets consistent, predictable exposure. The sieve
   can specialize cleanly. (exponential reduction)
3. **Interaction space**: dispatch × sieve × cycles × passes. Constraining
   dispatch collapses a dimension from every interaction term. (multiplicative)
4. **Temporal**: stable dispatch signal from step 1. Every etch step is
   productive. No contradictory sign flips from dispatch oscillation.

Total: several orders of magnitude reduction in effective search space.

## What was removed

Three mechanisms previously tried to steer dispatch. All vestigial
with the ratio prior:

1. **S4 emphasis_bias**: [-2,+2] logit bias from ascending registers.
   Learned to fight the ratio (I=+2.0, B=-1.98 in run3). -removed-
2. **Alarm dispatch_bias_proj**: 65→4 projection. Never activated
   (all zeros in run3). -removed-
3. **S2DispatchCoordinator**: per-position inertia bias. Stuck at 0.0.
   Anti-oscillation is unnecessary when the target is fixed. -removed-

Net: -318 lines. The dispatch channel is now:

```
content logits (TernaryLinear)
  + register conditioning (ascending registers)
  + static ratio prior (log(r/Σr))
  → softmax
  → KL(dispatch ∥ prior) in loss (λ=100)
```

## Fully holographic VSM

Session 102 also converted all remaining nn.Linear to TernaryLinear.
Zero precision projections in the architecture. Every layer participates
in the consensus sieve.

```
Sieve-evolved (ternary signs):     4,389,888 values (17.4%)
Gradient-trained:                  20,814,492 values (82.6%)
  gamma (per-channel scale):         267,472
  bias (separated):                      665
  RMSNorm weights:                    36,864
  embeddings:                     20,508,672  ← dominates
```

Topology is fully holographic. Magnitudes remain gradient-trained.
The sieve shapes both the operational system (S1 attention/FFN) and
the control system (S3 gates, S4 policy, S5 alarm). Fractal: same
substrate, same operation, every scale.

## Fractal audit

Beta reduction self-similar at every scale:

```
Scale          Substrate        Operation
─────────────  ───────────────  ──────────────────────
Head           TernaryLinear    beta reduction (Q→K,V)
Multi-head     TernaryLinear    parallel beta reductions
FFN            TernaryLinear    pattern memory (signs)
Stride         TernaryLinear    multi-scale reduction
S3 gates       TernaryLinear    K (select/suppress)
S4 attention   TernaryLinear    M+K (match + select)
S5 alarm       TernaryLinear    health → amplitude
CycleContinue  TernaryLinear    continue/halt
Dispatch       TernaryLinear    combinator routing
Embeddings     TernaryEmbedding token/position plate
```

VSM layers map to combinators:
  S1 = full KIBC-M, S2 = B (compose), S3 = K (select),
  S4 = M+K (match + select), S5 = I (identity)

## Open questions

- Can gamma (per-channel scale) be sieve-evolved too? Would reduce
  gradient params from 267K to ~0 for TernaryLinear.
- Embeddings (20.5M) dominate gradient side. Can the vocabulary
  embedding be fully ternary? The position embedding?
- Does the KL leash need a schedule (tight early, relax late)?
  Current design: constant λ=100 throughout. The ratio is universal,
  so no reason to relax.
- V12-run4 will be the first test. Compare dispatch stability,
  per-plate etch differentiation, and convergence speed vs run3.
