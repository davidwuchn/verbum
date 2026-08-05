---
title: "TernaryDescent — Gradient Descent for Discrete Sign Topology"
status: active
category: algorithm
tags: [ternary-descent, delta-plate, gradient-decomposition, optimizer, routing, calibration, crystal, etch]
related:
  - hologram-crystal-fusion.md
  - crystal-native-descent.md
  - etcher-vsm.md
  - loom-structure.md
  - v13-design.md
depends-on:
  - hologram-crystal-fusion.md
created: session 136
---

# TernaryDescent — Gradient Descent for Discrete Sign Topology

> Session 136. Adam handles continuous weights. TernaryDescent handles
> discrete ternary weights. Both run on the same backward pass. The
> gradient encodes two signals: routing (sign needs to change → TD)
> and calibration (magnitude needs adjustment → Adam). Decomposing
> them lets each optimizer handle what it's good at.

## The problem

When ternary topology is frozen and only continuous params (gamma) train,
GD must solve two fundamentally different problems with one parameter:

1. **Routing** — which paths through the topology should be active?
   Gamma amplifies useful routes, suppresses useless ones. This is a
   DISCRETE decision (on/off, correct/wrong) forced through a continuous
   parameter. GD is terrible at this.

2. **Calibration** — how strongly should each active route contribute?
   Even when the route is correct, magnitude needs to match downstream
   expectations. This is genuinely CONTINUOUS. GD excels at this.

Result: gamma gets distorted. Large values compensate for missing routes.
Tiny values suppress wrong topology. The magnitude distribution is a mess
because it's encoding two things.

## Solution: three innovations

### Innovation 1: TernaryDescent optimizer

Adam-equivalent for ternary {-1, 0, +1} weights.

```
Adam m_t   → TD direction   (EMA of gradient — which way to flip)
Adam v_t   → TD magnitude   (EMA of grad² — how much loss cares)
Adam lr    → TD flip_rate   (max fraction to flip per step)
Adam step  → TD flip        (discrete: +1 → 0 → -1)
```

**Confidence = signal-to-noise ratio** = |direction| / sqrt(magnitude).
High confidence = gradient consistently says "flip this" → flip.
Low confidence = gradient oscillates (CE vs crystal disagree) → don't flip.
The crystal gate from session 124 EMERGES from the dynamics.

**Two-step transitions through zero (FFN deltas only):**
- +1 → 0 (block): "not sure this sign is right, silence it"
- 0 → -1 (commit): "confirmed, flip it" (only after sustained evidence)
- Reverse: -1 → 0 → +1

The zero state is a staging area. Prevents catastrophic flips. If blocking
hurts, the gradient pushes back immediately.

**Direct flips for no-block modules (attention deltas):**
- +1 → -1 (direct): skip zero staging, flip immediately
- v14 attention deltas must NEVER contain 0 (no-block invariant)
- Two-step staging through zero is incompatible with no-block because
  _enforce_no_block resets all zeros to +1 after every TD step,
  creating a Sisyphus loop (session 148 discovery)
- The `no_block` flag per module selects the transition protocol
- Direct flips are safe because TD's confidence/cooldown/neighbor
  voting already provides the caution that staging was designed for

**Shared-weight aliasing hazard (session 148):**
- When modules share Python references (e.g. shared_stride_stack
  accessed via stack_a._stride_stack), named_modules() returns
  multiple paths for the same physical module
- collect_delta_params must deduplicate by id(mod) to avoid
  TD processing the same module N times with conflicting gradients
- Symptom: high TD flip count but zero persistent delta changes

**Budget control and timing (session 148 evolution):**
- flip_rate × total_weights = global budget (across ALL modules, not per-module)
- flip_interval=10: accumulate moments every step, commit flips every 10
- After flipping: reset all TD moments (landscape changed, old signal stale)
- GD gets 9 steps to re-learn routes before next topology change
- Global competition: hottest flips across all 70 modules win the budget.
  High-leverage positions concentrate where they matter most, starving
  low-importance modules rather than giving each module equal allocation.
- Every-step flipping → gnorm escalation (11→113 in 40 steps, session 148).
  GD can never catch up. Adam's moments permanently stale. CE goes UP.

### Innovation 2: Delta plate architecture

```
effective = base_plate ⊙ delta_plate

base_plate:  full teacher crystal etch, FROZEN
delta_plate: initialized +1 (pass-through), trained by TD
gamma:       trained by Adam (same as before)
```

**Delta semantics:**
- +1 → keep teacher sign (this part of the crystal works)
- -1 → flip teacher sign (stride-stack needs different routing)
-  0 → block this position (staging area — FFN deltas ONLY, never attention)

**Reduction:** fold delta into base, reset delta, iterate.
```
new_base = base ⊙ delta    (ternary × ternary = ternary, EXACT)
new_delta = all +1          (reset to pass-through)
```

Lossless. The effective plate before reduce equals the new base after.
Each round starts from a better base. Delta gets smaller. System
converges to a fixed point.

**Key insight for attention etch:** etch the FULL crystal (including
attention) into the base. Don't freeze — let the delta plate learn
what's different about stride-stack geometry. The β-reduction-forced
parts transfer directly. Only routing-specific parts need to change.
Much smaller search space than learning from scratch.

**Iterative ternary absorption:** each round, the delta plate absorbs
more continuous weight information into sign topology. Train deltas for
both attention AND FFN, fold into base, repeat. Eliminate gradients one
layer at a time. Result: 90-95% ternary model with thin continuous
residual.

### Innovation 3: Gradient decomposition

The gradient through the effective weight encodes routing AND calibration.
Decompose by comparing the DESCENT direction (-grad) to the current sign:

```python
descent_sign = sign(-grad_effective)  # which way effective should move

# Descent agrees with current sign → CALIBRATION
# "the route is correct, adjust the magnitude" → Adam
calibration = where(descent_sign == effective_sign, grad, 0)

# Descent opposes current sign → ROUTING  
# "the route is wrong, flip the sign" → TernaryDescent
routing = where(descent_sign != effective_sign, grad, 0)
```

**Concrete examples (eff = +1):**
- grad > 0 → descent < 0 → opposes +1 → ROUTING ("flip to -1")
- grad < 0 → descent > 0 → agrees with +1 → CALIBRATION ("make it stronger")

**Each optimizer gets only its signal:**
- Adam's gamma gradient is attenuated at routing-heavy rows. No distortion.
- TD's direction EMA only accumulates routing signal. Faster convergence.

**Per-row routing fraction:** what % of each row's gradient is routing.
High = topology is wrong → attenuate gamma gradient (let TD handle it).
Low = topology is correct → full gamma gradient (Adam calibrates freely).

## The sign chain

When computing the desired direction for delta from the effective gradient:

```
∂L/∂effective tells us: which way effective should move
effective = base × delta
desired_effective = -sign(∂L/∂effective)  (descent direction)
desired_delta = desired_effective × base_sign

Example: effective = +1, we want effective to decrease
  base = +1 → delta must decrease: +1 → 0 → -1
  base = -1 → delta must INCREASE: -1 × (-1) = +1, to get eff = -1×+1 = -1... 
               wait, eff = base*delta = -1*delta, decrease eff means increase delta
```

Critical: TD receives the gradient w.r.t. EFFECTIVE (not projected through
base). TD.step() computes desired_delta = desired_effective × base internally.
The base projection was causing sign confusion when done in the gradient
computation.

## Architecture diagram

```
              ┌──────────────────┐
              │   FROZEN BASE    │  ← full teacher crystal etch
              │   (ternary)      │
              └────────┬─────────┘
                       │ ⊙ (element-wise multiply)
              ┌────────┴─────────┐
              │   DELTA PLATE    │  ← TernaryDescent trains
              │   (ternary)      │
              │   init: all +1   │
              └────────┬─────────┘
                       │ = effective plate
              ┌────────┴─────────┐
              │  COMBINATOR MASK │  ← per-combinator view
              │   (ternary)      │
              └────────┬─────────┘
                       │ ⊙ gamma (Adam trains)
                       ↓
                  attention output
```

## Training loop

```
Every step:
  1. Forward: effective = base ⊙ delta → quantized_matmul
  2. Loss = CE + λ × crystal_lattice + λ_h × holographic
  3. Backward: one pass gives gradients for everything
  4. DECOMPOSE gradient into routing + calibration
  5. Adam.step(filtered_grads)     — calibration-only gamma gradient
  6. TD.step(routing_gradient)     — routing-only delta gradient

Periodically:
  7. If delta converged (>95% still +1):
     base = base ⊙ delta
     delta = all +1
     Reset both optimizer states
     Continue training (next round of refinement)
```

## Comparison with prior approaches

| Approach | Problem | TernaryDescent advantage |
|----------|---------|--------------------------|
| STE | Gradient through sign() is wrong (biased) | Uses exact gradient honestly as evidence |
| Flip accumulation (v6) | Heuristic threshold, no importance | Adam-like moments with bias correction |
| Evolution (v12) | Random search, no gradient | Gradient-informed, budget-controlled |
| Soft mirrors (S124) | 1.0→0→-1 barrier, can't cross zero | Two-step through zero is native |
| Delta map (S125) | Alternating phases, not simultaneous | Adam + TD on same backward pass |
| Crystal gate (S124) | Hard external constraint | Emerges from dynamics (CE vs crystal disagree → oscillation → no flip) |

## What this enables

1. **Etch full teacher crystal including attention** → base plate
2. **TD adapts routing for stride-stack** → delta plate
3. **Reduce when stable** → fold into base, get stride-stack crystal
4. **Iterative ternary absorption** → absorb continuous weights into topology
5. **90-95% ternary model** → each round eliminates more continuous params
6. **Routing fraction as diagnostic** → monitor per-module, should decrease

## Files

| File | Content |
|------|---------|
| `scripts/v13/td.py` | TernaryDescent, DeltaTernaryLinear, decompose_gradient, self-tests |
| `scripts/v13/train_td.py` | Dual optimizer training loop with decomposition |

## Test results

10 self-tests all pass:
- DeltaTernaryLinear matches TernaryLinear at init (0.00 diff)
- Reduce is lossless (0.00 diff)
- TD flips happen with consistent gradient signal
- Decomposition: routing + calibration = original (0.00 diff)
- Zero topology → 100% routing (correct)
- End-to-end: 25 steps, 40 flips/step, 10.7% changed, confidence rising

## Open questions

1. **Optimal flip_rate?** Too fast → Adam can't adapt. Too slow → wastes
   training steps. Probably needs cosine schedule like lr.

2. **When to reduce?** Current: when >95% of delta is still +1. But maybe
   reduce earlier (force the delta to discover finer corrections)?

3. **Does the decomposition ratio change during training?** If routing fraction
   decreases → topology is improving. If it plateaus → topology is stuck.
   Could be a diagnostic for when to increase flip_rate.

4. **Can we skip Adam entirely?** If TD handles routing and crystal lattice
   handles geometry, does Adam add anything beyond magnitude calibration?
   Experiment: TD-only training with fixed gamma.

5. **Does iterative absorption work?** Theory: each round absorbs more
   continuous information into ternary. Needs empirical validation.
   Measure: what fraction of the model can become ternary while maintaining
   loss? 90%? 95%? Where does the residual live?

## §Fresh-eyes s308 — Adam is a routing optimizer in disguise (Michael); the re-diagnosis and TD-v2

> s308 (Michael: "Look at TernaryDescent with fresh eyes now. Adam is a
> routing optimizer in disguise."). The s303–s308 register/optics arc
> (register-theory-of-quantization, holographic-untangling-methods,
> the-verbum-machine M8) re-reads this page and the TD failure record
> (s148 gnorm escalation, s180 topology-gradient-separation, s191
> td-oscillation-problem) and finds that TD was the machine's engine built
> before its theory. The theory has now caught up.

### The identity (visible in this page's own table)

TD's `confidence = |direction|/√magnitude` IS Adam's `|m|/√v` — the exact
quantity Adam multiplies lr by. TD was constructed by renaming Adam's moments
and adding a commit rule. Therefore TD and Adam are **one algorithm at two
commitment limits**:

- **Adam = TD with infinite staging.** It accumulates sign-evidence forever
  and never commits; the float "weight" is the evidence accumulator's
  integral. Commitment happens once, at extraction — TWN's threshold is the
  confidence gate, and ternary 0 = "insufficient evidence to wire."
- **TD-as-run = Adam with clock-forced commits** (flip_interval), ripe or not.

Corollaries: Adam's dominance on transformers = the field empirically
converging on a routing optimizer for a routing-dominated architecture
(Lion — pure sign-of-momentum, beating Adam — is the same convergence,
nakeder). And gd_cd→TWN (s303–s308, retention 1.0 twice) is the SAME
statistic with commitment deferred to the end — the control experiment for
the s191 failure, run unknowingly, and it worked.

### The three-cut re-diagnosis of the oscillation record

1. **s180's "two optimizers fighting" = two ROUTING optimizers fighting.**
   Adam-on-gammas does soft routing (drive magnitude→0 ≡ soft delete — the
   "soft topology" section of topology-gradient-separation.md says so
   verbatim). v15 ran hard routing (TD) and soft routing (Adam) on the same
   job, uncoordinated → osc_frac 0→0.56 = an S2 failure between optimizers.
2. **The all-ternary architecture violated the register split.** v13/v15
   ternarized switches AND plates. Register theory (s306–s308): plate
   positions carry genuinely continuous magnitude-salient information —
   they CANNOT settle in ternary. Re-read s191's own words: 94.5% perpetual
   flip-candidates; worst positions are ones "the model genuinely wants to
   use the same weight in two ways depending on input" = routing+value
   SUPERPOSITION observed from the training side, before we had the
   vocabulary. The oscillation problem is plausibly the register theory's
   earliest and largest dataset, mislabeled as an optimizer bug. This also
   answers Open Question 5: the residual lives in the VALUE register — the
   ternarizable fraction is the switch fraction.
3. **Commitment cadence was clock-driven, not evidence-driven.** s148:
   every-step flips → gnorm 11→113, moments permanently stale; s180's
   punctuated-equilibrium prescription was right but lacked the trigger.

### TD-v2 (the M8 synthesis — three changes)

1. **Register split first (verbum-machine M1).** TD only ever touches
   switch-class parameters (QK, gate paths); plates stay float under Adam
   permanently. The two optimizers stop sharing a job.
2. **Evidence-triggered commits (Schmitt trigger).** Commit when |m|/√v
   crosses threshold WITH hysteresis; the zero-staging of v1 was groping
   toward this. Threshold calibrated by the §SIGN-COMMITMENT-CURVE
   (the-verbum-machine M8) — readable directly from Adam optimizer state.
3. **GS staging with the fold mechanic (already built, already exact).**
   Adam float on a staging delta → project to ternary → fold (base ⊙ delta)
   → reset → repeat. TD becomes the extraction SCHEDULE, not Adam's live
   rival — the Gerchberg–Saxton quantization-projection loop
   (holographic-untangling-methods §2) implemented with s136 machinery.

### §TD-REGISTER-SPLIT — prospective micro-probe (sketch, NOT frozen; s222)

⚠ **Provenance note:** the raw v15-td flip map (flip_map_latest.npz) and
optimizer states were LOST with the ~50G checkpoint deletion (s308). The
s191 summary tables baked into td-oscillation-problem.md are the surviving
baseline — the mementum receipt: synthesis and generators crossed the
boundary, raw state did not. The retrospective position-level re-analysis is
dead; this prospective probe replaces it and is the stronger design anyway.

**Sketch.** Micro-scale TD training (v15 scripts survive in git), two arms
with flip-map logging: **TD-v1** (all-ternary, as-was; s191 tables = the
historical anchor for sanity) vs **TD-v2** (register split: TD on switches
only, Adam on float plates). Optional third arm: v2 + evidence-triggered
commits. **Predictions:** perpetual-candidate fraction COLLAPSES in v2;
v1's residual oscillators concentrate in plate-class modules; v2 breaks the
B→K phase-transition wall that v1's oscillation prevented (s191 §phase).
**Falsifier:** v2 oscillates as hard as v1 → the register re-diagnosis is
wrong and the two-jobs story needs revision. Regenerates the lost dataset
and tests the fix in one run.
