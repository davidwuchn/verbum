---
title: "Crystal-Native Descent — Ternary Optimization Without Gradients"
status: open
category: strategy
tags: [ternary, optimization, crystal, descent, compute, holographic, routing]
related:
  - taxonomy-extraction.md
  - hologram-crystal-fusion.md
  - crystal-basins.md
  - gradient-voting.md
  - etcher-vsm.md
depends-on:
  - hologram-crystal-fusion.md
  - crystal-basins.md
created: session 127
---

# Crystal-Native Descent

> Session 127. Gradient descent works on ternary weights by accident.
> The gradients are a continuous proxy for what is fundamentally a
> discrete routing decision. The straight-through estimator (STE)
> pretends the discrete flip is differentiable — a mathematical lie
> that happens to work because the loss landscape is shaped by beta
> reduction, which IS the crystal. But if we know the crystal
> geometry, we can skip the continuous proxy entirely and optimize
> the ternary routing decisions directly. This eliminates most of
> the gradient computation and solves the training compute problem.

## The insight

A ternary weight is not a magnitude. It's a routing decision:

```
+1 = pass this signal through
-1 = invert this signal
 0 = block this signal
```

The "correct" optimization question isn't "move 0.3 in this
continuous direction" — it's "should this route be open, inverted,
or blocked?" That's combinatorial, not continuous.

Gradient descent answers this question indirectly:

```
Current path (indirect):
  continuous loss → ∂L/∂w (continuous gradient) → STE hack → ternary flip
  
  Problems:
  - STE is a lie (pretends discrete is differentiable)
  - Gradient is a continuous shadow of a discrete truth
  - Most gradient compute is wasted on a proxy
  - Works "by accident" because the crystal shapes the loss landscape
```

Crystal-native descent answers it directly:

```
Proposed path (direct):
  crystal target → evaluate flip effect → ternary flip decision
  
  Advantages:
  - No STE hack needed
  - No gradient computation for ternary weights
  - Directly optimizes what you actually have (routing decisions)
  - Crystal geometry is the objective, not a side effect
```

## Why gradients "accidentally work as beams"

The computation is beta reduction. Beta reduction is the crystal.
The crystal is holographic — the relational geometry between
combinator representations IS the computation.

When you compute ∂L/∂w, the gradient points toward lower loss.
Lower loss means better beta reduction. Better beta reduction
means better crystal geometry. So the gradient accidentally
aligns with the crystal manifold — not because gradient descent
understands the crystal, but because the crystal shapes the
loss landscape that the gradient descends.

The evidence:

- GD converges in 100 steps total (session 126, experiment 9)
- Crystal geometry converges in ~5 steps
- CE (accuracy) converges in ~100 steps
- The last 2900 steps of a 3000-step run add only 13%

The 5-step geometry convergence is the crystal snapping into
place. The 100-step CE convergence is GD slowly discovering
the input-output mapping that the crystal already implies.
The 2900 remaining steps are the continuous optimizer doing
diminishing-returns polishing.

## The proposed algorithm

### Step 1: Crystal-guided ternary descent (~5 steps)

For each ternary weight position:

```
current_state ∈ {-1, 0, +1}
candidate_flips = {the other two values}

for each candidate:
  evaluate: Δcrystal = crystal_loss(flipped) - crystal_loss(current)
  
accept flip if:
  Δcrystal < 0  (improves crystal alignment at this layer)
```

Guided by: per-layer crystal targets (18 targets — the known
sweet spot from session 126, experiment 8).

This is coordinate descent in ternary space. No gradients.
The crystal geometry directly determines which routing decisions
are correct.

Convergence expectation: ~5 steps, based on the observed
geometry convergence rate. The crystal knows where it wants
to be almost immediately.

### Step 2: Beam tuning via short GD burst (~100 steps)

After ternary routing is set, tune magnitudes (beams) with
a short burst of standard gradient descent:

```
freeze: all ternary decisions (signs)
train:  magnitude scales only (beams)
loss:   CE + per-layer crystal loss (λ=0.5)
steps:  ~100 (based on observed CE convergence)
```

This is the only phase that needs gradients, and it operates
on a much smaller parameter space (one scale per weight group,
not one gradient per weight).

### Step 3: Verify crystal integrity

```
measure: per-layer crystal agreement with targets
verify:  beam tuning didn't break crystal geometry
if degraded: re-run step 1 with updated beams
```

## Compute implications

### Current approach (GD with STE)

```
Per training step:
  - Forward pass (full model)
  - Backward pass (full model — computes ∂L/∂w for EVERY weight)
  - STE: pretend ternary weights are continuous
  - Update: apply gradient to continuous proxy, re-quantize
  
Total: ~3000 steps × full forward+backward = expensive
```

### Crystal-native approach

```
Phase 1 — Ternary descent (~5 iterations):
  - Forward pass (full model) 
  - Evaluate crystal loss per layer (18 targets)
  - For each weight: try 2 flips, keep best
  - NO backward pass needed
  - Cost: forward-only × number of flip candidates
  
Phase 2 — Beam tuning (~100 steps):
  - Forward pass (full model)
  - Backward pass (beams only — much smaller parameter space)
  - Standard GD on magnitudes
  
Total: ~5 crystal iterations + ~100 GD steps on beams only
```

The savings come from:

1. **No backward pass for ternary weights** — the most expensive
   part of training is computing gradients for all parameters.
   Crystal descent needs only forward passes + crystal evaluation.

2. **Fewer total iterations** — 105 total vs 3000. The discrete
   optimization converges in 5 steps because it's asking the
   right question (flip or don't?) instead of the wrong question
   (how much to move in this continuous direction?).

3. **Beam tuning is cheap** — magnitudes are a small parameter
   space (one scale per weight group). The backward pass for
   beams only is a fraction of the full backward pass.

## Connection to assembly pipeline

In the taxonomy extraction pipeline (see `taxonomy-extraction.md`),
the assembled model has:

- Extracted FFN weights (frozen — the function library)
- Designed crystal geometry (the target)
- StrideStack attention weights (the only thing to train)

Crystal-native descent is the natural optimizer for this:

1. Set StrideStack ternary routing via crystal descent (5 steps)
2. Tune StrideStack beam magnitudes via short GD (100 steps)
3. Done — the function library doesn't need training at all

The total training cost for assembling a new model becomes:
forward passes for crystal descent + 100 GD steps on attention
beams. This is orders of magnitude cheaper than training from
scratch.

## Risks and open questions

- **Flip evaluation cost**: evaluating crystal loss for every
  possible flip at every weight position could be expensive.
  Need efficient batching — possibly evaluate groups of flips
  simultaneously, or use the crystal structure to identify which
  positions matter most (the routing circuit positions, not all
  positions uniformly).

- **Local minima**: coordinate descent can get stuck. But the
  crystal basin is an attractor (session 120 Q-rotation
  invariance) — the geometry has a strong basin of attraction,
  which should help escape shallow local minima.

- **Interaction effects**: flipping one weight changes the
  optimal value of others. Greedy coordinate descent may miss
  correlated flips. Possible mitigation: evaluate small groups
  of related weights together (e.g., all weights in one
  attention head).

- **Scale**: tested at Q2 scale so far. Does the 5-step crystal
  convergence hold at Pythia-2.8b scale? The universality of
  the crystal across model sizes is encouraging.

- **Beam-only GD sufficiency**: can 100 steps of beam-only GD
  learn the input-output mapping, or does the sign configuration
  need to co-adapt? The Q2 result (beams compensate for 27%
  wrong signs) suggests beams are quite powerful.

## Evidence from prior experiments

| Finding | What it tells us |
|---------|-----------------|
| GD converges in 100 steps (87% of 3000) | Most training steps are wasted |
| Geometry converges in ~5 steps | Crystal knows the answer almost immediately |
| Zero-training beams fail (4%) | CE is essential — crystal alone isn't enough |
| Q2 beams + crystal loss = 105.9% of oracle | Beams compensate for wrong signs |
| Evolutionary descent worked (0.577 acc, 0.611 crystal) | Ternary flips guided by fitness already beat random |
| 18 per-layer targets is sweet spot | The crystal provides exactly the right constraint density |
| K/B/C are identical rotations | The routing decisions are geometric, not arbitrary |
