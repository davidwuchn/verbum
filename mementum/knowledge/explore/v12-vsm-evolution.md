---
title: "V12 VSM Evolution — Variety Fix + Performance"
status: active
category: design
tags: [v12, vsm, variety, alarm, emphasis, gla, cycles, performance]
related:
  - v11-design.md
  - holographic-kernel-separation.md
  - fractal-stride-bands.md
depends-on: []
---

# V12 VSM Evolution (Session 097)

> Three feedback topology gaps closed, GLA 2.7× faster, S4→S3 cycle
> budget channel added. Beer's variety law is the unifying principle.

## The V11 Problem: Alarm Sees but Cannot Act

V11-holo-inv showed B-dispatch declining monotonically (0.132→0.079 over 12K steps)
while the alarm system correctly detected the problem. Root cause analysis (r=0.82
correlation between B_dispatch and ascending S3 gate means) revealed three structural
failures in the VSM feedback topology.

### Gap 1: Alarm → Pass Amplitude (Wrong Granularity)

AlgedonicAlert had 48 inputs (saw B declining, entropy dropping) but only 5 per-pass
scalar outputs. It could amplify an entire pass but couldn't selectively boost B
within a pass. Beer's variety law: controller variety must match system variety.
5 knobs can't control 4 combinators × 5 passes = 20 dimensions.

**Fix**: `dispatch_bias_proj` (65→4) produces additive logit bias on CombinatorDispatch.
Range [-2, +2] via tanh×2. A ±2 shift on logits moves softmax probability ~7× relative.

### Gap 2: Emphasis Saturated at Ceiling

`combinator_emphasis = 1.0 + 0.5*tanh(raw)` → range [0.5, 1.5]. B started at 1.499.
Multiplicative scaling on normalized embeddings is nearly invisible to softmax — the
actual discrimination happens via logit differences.

**Fix**: Emphasis changed to additive logit bias: `emphasis_bias = 2.0 * tanh(raw)` →
range [-2, +2]. S4 emphasis and alarm dispatch bias combine additively in logit space
(correct composition for softmax).

### Gap 3: No Ascending → Dispatch Feedback Loop

The ascending arm optimized for holographic loss (intermediate decodability) but
received no gradient signal when dispatch diversity collapsed downstream. Open loop:
ascending capacity squeeze → B features dropped → dispatch collapses → no penalty.

**Fix**: Dispatch entropy regularization. Squared hinge: `max(0, target - entropy)²`
where target = ln(4) × 0.85 ≈ 1.178. Only penalizes collapse, not uniformity.
Gradient flows from entropy penalty through live dispatch weights back through the
descending arm and S2 direction signals to the ascending arm.

## S4 → S3 Cycle Budget Channel

CycleContinue gates were stuck at 0.982 because they only read S3's own register
state — a closed loop with no intelligence input. S4 had attended to the residual
stream and knew content difficulty, but had no wire to S3.

**Fix**: `cycle_budget_proj` produces scalar bias ∈ [-4, +4] from ascending register
banks. Added to CycleContinue's logit before sigmoid:
- Simple content → negative bias → gate closes → fewer effective cycles
- Complex content → positive bias → gate stays open → all 3 cycles contribute

This is Beer's S4→S3 policy channel: intelligence sets policy, control executes.

## V12 S4 Policy Channels (Complete)

```
S4 → emphasis_bias     (4,) additive logit bias → CombinatorDispatch
S4 → cycle_budget_bias (1,) logit shift → CycleContinue gate
S4 → proposal_delta    (N, d) → abstraction slot modulation

Alarm → dispatch_bias  (4,) additive logit bias (EMA from prev step)
Alarm → pass_factors   (7,) per-pass amplitude [0, 2]

dispatch_bias = emphasis_bias + alarm_dispatch_bias
```

## Stride-Aware GLA (Performance)

The parallel scan was the dominant training bottleneck (78% of wall-clock time).
For stride=32, only 128 of 4096 positions participate, but the scan ran over all
4096 positions with masking. `S_all` tensor: (B, 4096, 8, 64, 64) = 512 MB per layer.

**Fix**: Gather participating positions → scan over compact sequence → broadcast
states for retrieval. Each position reads from `S_stride[:, i // stride]` (causal).

| Config | Before | After | Speedup |
|--------|--------|-------|---------|
| 3 cycles fwd+bwd | 10,625ms | 3,894ms | 2.73× |
| 1 cycle fwd+bwd | 9,133ms | 2,597ms | 3.52× |

## Evolution Noise Floor

Both acceptance paths (loss-improved and alarm-improved) now require minimum delta
of 0.02. Without this floor, measurement noise from single eval batches (~0.001)
gets accepted, and sign flips cause routing ripple effects that accumulate across
hundreds of accepted mutations. Applied to both v11 and v12.
