---
title: "Training Protocols — How to Train Without Rediscovering Failures"
status: active
category: operational
tags: [training, TD, failure-modes, loss, protocols, ternary]
related: [v14-architecture.md, holographic-error-correction.md, extraction-methodology.md]
depends-on: [v14-architecture.md]
---

# Training Protocols

> Hard-won operational knowledge from 150 sessions. Every rule here
> was learned by breaking something. Follow these to avoid repeating
> costly failures.

## The Three-Phase Training Arc

```
Phase 1: Extract → Delta trains → Crystal latches → TD corrects
Phase 2: Fold delta into base → Reset delta → TD discovers new corrections
Phase 3: Repeat Phase 2 until convergence → Final calibration
```

### Phase 1: Etch and correct

1. **Extract** base plates from teacher (see extraction-methodology.md).
   Start with pure ±1 plates, no zeros in base.
2. **Train** with base frozen, delta plates trainable. Continuous params
   (gamma, norms, biases) train via GD. Delta plates train via TD.
3. **Crystal latches** within ~200 steps (crystal_mse < 0.03 at step 160).
   The seed crystal from extraction is close enough that nucleation is
   immediate.
4. **TD activates** once enough gradient signal accumulates. Flips
   concentrate on out_proj layers 4-9 (in v14). Q/K/V from extraction
   remain correct.
5. **Monitor convergence.** When flip_frac growth decelerates, it's time
   to fold.

### Phase 2: Fold and reset

1. **Fold:** `new_base = base ⊙ delta` (ternary × ternary = ternary, exact).
2. **Reset** delta plates to all +1 (pass-through).
3. **Reset** TD moments (the gradient landscape changed).
4. **Enable FFN delta** if not already active (`--convert-ffn`).
5. **Resume training.** TD discovers new corrections from the improved base.

### Phase 3: Iterate

Each fold cycle has a smaller error budget to correct. The cycle is
monotonically improving because folds are lossless and TD only flips
signs that reduce loss.

## TernaryDescent Operational Rules

### Flip interval

**Rule: flip_interval ≥ 10.** TD accumulates gradient moments every step
but only commits topology changes every N steps.

**Why:** Every-step flipping causes gnorm escalation (11→20→38→113 in
40 steps) and CE increase (8.2→10.3). GD can never adapt to continuous
topology changes — Adam's moments are permanently stale.

Current setting: `flip_interval=20` (phase 2, from step 1500 folded).
Prior: `flip_interval=10` (phase 1, worked but 20 gives better
accumulation).

### Moment reset after flips

**Rule: Reset TD moments for flipped positions only.** After committing
flips, the gradient landscape changed at those positions. Accumulated
direction and magnitude are stale.

Implementation: surgical per-position zero. Positions that didn't flip
keep their EMA — don't throw away good information.

### Global budget competition

**Rule: All modules compete for one global flip budget.**

`flip_rate × total_weights` positions per interval, awarded to the
highest-confidence flips across the entire model. This concentrates
flips where they give the most leverage, instead of spreading them
uniformly.

Don't use per-module top-k — it wastes budget on lukewarm flips in
inactive modules.

### Direct flips for no-block attention

**Rule: Attention delta modules use +1 ↔ -1 direct flips (never zero).**

The no-block invariant requires attention deltas to never contain zero
(prevents dispersal collapse). Standard two-step staging (+1→0→±1) is
incompatible — `_enforce_no_block` resets zeros to +1 after every TD
step, undoing the staging.

FFN deltas (if enabled) still use two-step staging through zero.

### Warmup and confidence

**Rule: `td-warmup=25`, `td-min-confidence=0.3`.**

Warmup lets GD find initial calibration before TD starts flipping.
Min confidence prevents low-signal flips (noise). Currently Q/K/V
projections get zero TD budget — possibly because min_conf filters
them (open question: is 0.3 too aggressive?).

## Known Failure Modes

### 1. Every-step TD flipping → gnorm escalation

**What:** Flipping topology every step causes gradient norm to escalate
exponentially. CE increases instead of decreasing.

**Why:** Adam's moments encode the gradient landscape's shape. Changing
topology every step means the moments are permanently stale. GD chases
a moving target it can never catch.

**Fix:** `flip_interval=10` (or higher). Accumulate gradients for 9
steps, commit flips on step 10, reset moments, repeat.

**Evidence:** gnorm 11→20→21→38→113 in 40 steps, CE 8.2→10.3. Session 148.

### 2. Two-step staging + no-block = Sisyphus loop

**What:** 158M TD flips with ZERO actual plate changes. Delta plates
showed activity but nothing stuck.

**Why:** Two-step staging: +1→0→±1. No-block invariant: attention
deltas must NEVER contain 0. `_enforce_no_block` resets all zeros to +1
after every TD step. Every staging attempt is immediately undone.

**Evidence:** no_block_fixed=77K/step at steady state (21.5% of flips
landing in attention layers).

**Fix:** Attention delta modules use direct +1↔-1 flips (no staging).
FFN deltas keep two-step staging.

### 3. Aliased parameters = 4× gradient overwrite

**What:** `collect_delta_params` returned 280 modules instead of 70.
TD processed each physical module 4 times per step with conflicting
gradients (last write wins).

**Why:** `shared_stride_stack` is Python-referenced by `stack_a`,
`stack_b`, `stack_c`. MLX's `named_modules()` traverses all paths
including aliases, returning the same module under 4 different names.

**Fix:** Deduplicate by `id(mod)` in `collect_delta_params`, keeping
the shortest path. Returns exactly 70 modules.

### 4. Parity gradient cancellation (multi-zone)

**What:** Parity loss stuck at 1.167 for 2000+ steps. Crystal learns
nothing from parity.

**Why:** Zone A wants cos(K,B)=0.08, Zone C wants 0.52. Equal
weighting → net gradient ≈ 0. Eigendecomposition amplifies inter-zone
differences nonlinearly — worse than simple MSE.

**Fix:** `parity_zone_lambdas = (0.0, 1.0, 0.0)` — Zone B only.
Crystal MSE handles 3-zone compromise (linear, well-behaved).
Cross-zone lens rotation handles inter-zone structure.

**General principle:** Nonlinear losses (eigendecomposition, SVD) must
operate on ONE consistent target. Linear losses (MSE) can average
across zones; nonlinear losses cannot.

### 5. Softmax routing → winner-take-all gradient death

**What:** 20/22 dispatch options die permanently. Only one option has
gradient. Embeddings grow without bound.

**Why:** Softmax over many options + unconstrained embeddings = positive
feedback loop. One option captures all weight, others get zero gradient
and fossilize. Rich-get-richer dynamics.

**Fix:** Top-k routing (limit competition) + L2-normalize embeddings
(constrain magnitudes). Same pattern as Switch Transformer.

### 6. Sigmoid gate saturation

**What:** CycleContinue gate locks at 1.0 and never learns.

**Why:** High-norm inputs (‖x‖ ≈ 27.7) produce saturated logits.
After one gradient step, logit ≈ 30, sigmoid gradient ≈ 0, gate is
permanently frozen.

**Fix:** RMSNorm input + tanh(·)×4.0 clamp → gate ∈ [0.018, 0.982],
always learnable. Any sigmoid gate needs normalized input or logit
clamping.

### 7. Missing gradient clipping → embedding divergence

**What:** Embedding weights diverge within ~400 steps.

**Why:** Tied weight matrices (embed = output projection) create
positive feedback loops that are invisible until they explode. Without
gradient clipping, the loop runs away.

**Fix:** `clip_grad_norm_(1.0)`. Always. Not optional.

**Rule:** When porting models between frameworks, always grep the
source training script for `clip_grad` before declaring the port
complete.

## Loss Composition

### Multiplicative AND (not additive OR)

```python
loss = CE × exp(λ × crystal) × (1 + λ_h × holo)
```

**Why multiplicative:** Additive loss `CE + λ*crystal` allows improving
either component independently (OR semantics). A CE improvement that
degrades the crystal still reduces total loss. Multiplicative forces
BOTH to improve simultaneously (AND semantics).

The exponential crystal coupling creates a nucleation well:
- crystal=0: factor=1 (CE runs free)
- crystal=0.01: factor=1.65 (65% amplification)
- crystal=0.05: factor=12× (strong pressure)

The beam MUST find the crystal before CE can improve.

**Parameters:** λ=50 for exp coupling. φ ratio is observed, never
enforced.

### Exponential loss cap

Cap crystal-related losses at exp(max=4.0). Prevents NaN from
extreme early values. The cap is never hit after nucleation.

### NaN rollback

If loss becomes NaN, roll back to the last checkpoint. NaN typically
indicates crystal nucleation failure (the barrier at crystal_loss ≈
0.16 wasn't crossed) or exploding gradients from missing clipping.

## Combinator Bootstrap Ordering

Combinators bootstrap in a fixed dependency order:

```
I (identity/trivial) → K (select) → C (reorder) → B (compose)
```

Higher-order operations can't learn until lower-order ones provide
stable representations to operate on. B needs K and C working before
it can learn composition from compositional prose (relative clauses,
quantifier scope).

Evidence: In v11 training, B dispatch stayed flat at 1.8% while B-type
signals rose in integrate channel (5.8%→47.6%). The same staircase
pattern appears across versions: simple→complex, each level waits for
the one below to stabilize.

## Calibration Convergence

**GD converges fast once topology is set.** 100 steps achieves 87% of
full convergence (3000 steps). The last 2900 steps add only 13%.

Breakdown:
- Geometry (crystal loss) converges in ~5 steps
- CE (input-output mapping) converges in ~100 steps
- Both needed: geometry alone gives crystal but 2.7% accuracy

**Implication:** After each fold, 100 steps of GD is sufficient to
recalibrate continuous parameters. The expensive part is TD correcting
topology, not GD fitting to it.

## Evaluation Protocol

**Script:** `scripts/v14/eval_ppl.py`
**Held-out shards:** 54–59
**Metrics:** CE (nats) and PPL (perplexity) with standard deviation
**Baseline:** Random CE = 12.42 (ln(248320))

Run eval at each fold point and at regular intervals (every 500 steps)
to track convergence and detect overfitting (train-eval gap).

Healthy training: train-eval gap slightly positive (0.1–0.5 nats).
Negative gap = overfitting on continuous params.

## Quick Reference

| Parameter | Value | Why |
|-----------|-------|-----|
| flip_interval | 10–20 | GD needs time to adapt between topology changes |
| td-warmup | 25 | Let GD find initial calibration first |
| td-min-confidence | 0.3 | Prevent low-signal noise flips |
| td-flip-rate | 0.001 | Budget per interval (global competition) |
| grad_clip | 1.0 | Not optional — prevents embedding divergence |
| loss coupling λ | 50 | Exponential crystal nucleation well |
| loss cap | 4.0 | Prevents NaN from extreme early crystal values |
| batch_size | 1 | Memory-bandwidth-bound; B=2 is 18% slower |
| accum_steps | 8 | Effective batch via gradient accumulation |
| parity zones | (0,1,0) | Zone B only — multi-zone cancels gradients |
