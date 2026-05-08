---
title: "Dispatch Gradient Death: Softmax Saturation Kills Sparse Routing"
status: active
category: architecture
tags: [kernel-dispatch, gradient-death, moe, top-k, softmax, v10]
related:
  - compressor-architecture.md
  - attention-spiral-finding.md
depends-on: []
---

# Dispatch Gradient Death

> Session 069. Diagnosed why 20/22 kernel ops were permanently dead
> in v10-spiral, and fixed with top-k MoE routing.

## The Problem

KernelDispatch routes representations through 22 kernel op pathways
via softmax over dispatch logits. After 9K steps of training:

- Only `if` (op 17) received gradient (norm 1.54)
- 20/22 ops received **zero gradient** — permanently dead
- `>=` (op 11) had embedding norm 4.22 but zero gradient (fossil)
- Register conditioning was 85% of dispatch signal, not inert

## Causal Chain

```
1. Early training: some ops slightly useful → slightly higher dispatch weight
2. Higher weight → more gradient → embedding grows → more modulation
3. Register conditioning learns "always route to `if`" → +10.2 bias
4. Softmax saturates: e^(+10.2) / Σ ≈ 1.0 for `if`, ≈ 0.0 for rest
5. Gradient scales by dispatch weight: 0.0 × anything = 0.0
6. Non-dominant ops starved — can never learn their niche
7. `>=` grew early (step 1-2), froze when step 3 redirected routing
```

The `>=` fossil: grew to 4.22 norm via positive feedback in early
training, then register conditioning redirected all routing to `if`.
`>=` stopped getting gradient but its embedding stayed huge. It
dominated the modulation step (`h + dispatch_weights @ op_embeddings`)
by raw norm, not by routing — distorting the representation even
though the router wasn't selecting it.

## Key Measurements (step 9000)

```
Register conditioning bias:
  if (op 17):  +10.2  (everything else: -1.2 to -4.1)

Op embedding norms:
  >=:  4.222  (FOSSIL — zero gradient)
  if:  2.961  (only op with gradient)
  %:   0.474
  rest: 0.12–0.17 (near initialization)

Gradient norms (per op embedding):
  if:   1.5366
  comp: 0.0001
  everything else: 0.0000

Dispatch logits vs register bias:
  Ternary dispatch: mean_abs = 0.37  (15% of signal)
  Register bias:    mean_abs = 2.12  (85% of signal)
```

## The Fix: Top-k MoE Routing (k=2)

Replace softmax-over-22 with top-k selection + softmax-over-k:

```python
top_k_values = mx.topk(dispatch_logits, k=2, axis=-1)
threshold = mx.min(top_k_values, axis=-1, keepdims=True)
mask = mx.where(logits >= threshold, logits, -1e9)
dispatch_weights = mx.softmax(mask, axis=-1)  # only 2 ops nonzero
```

**Why this works**: softmax over 2 ops can't saturate as badly.
Even with a large gap between 1st and 2nd place, the runner-up
gets weight ≈ e^(-gap). With gap ≈ 3, runner-up gets ~5%. With
gap ≈ 1, runner-up gets ~27%. Both give meaningful gradient.

**Why not equal distribution**: the 22 ops aren't interchangeable.
FN_COMP should dominate prose (~60%), arithmetic ops should be rare
(<1%) but alive for their niche. Load balancing or entropy
regularization would fight the natural distribution. Top-k preserves
skew while keeping all ops trainable.

Combined with **L2-normalized op embeddings** (fixed scale = 0.5):
dispatch weights alone determine influence, not embedding magnitude.
Prevents the fossil pattern entirely.

## Results

```
Before (softmax-over-22):  1/22 ops with gradient
After  (top-k=2):         16/22 ops with gradient

Fresh init runner-up weight: ≥ 31% (healthy)
Old checkpoint runner-up:    ≈ 0% (register bias too extreme — needs fresh training)
```

## Design Principle

**Softmax over many classes + unconstrained embeddings = winner-take-all
gradient death.** This is the same problem Switch Transformer solved
with top-k routing. Any architecture that uses softmax to select from
>10 options and feeds the selection back through the same gradient
path will develop this collapse. The fix is always some form of:

1. Limit competition (top-k)
2. Constrain magnitudes (norm constraint)
3. Guarantee exploration (noise, dropout, or auxiliary loss)

For this architecture, (1) + (2) is sufficient. The natural data
distribution provides (3) — different content types activate
different ops, providing organic exploration.

## Files

- `scripts/v10/kernel_dispatch.py` — top-k routing implementation
- `scripts/v10/config.py` — `dispatch_top_k` parameter
- `scripts/v10/probe.py` — op embedding health display
- `results/v10/probe_step_00{1,5,9}000.json` — diagnostic data
