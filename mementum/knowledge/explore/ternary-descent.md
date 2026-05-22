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

**Two-step transitions through zero:**
- +1 → 0 (block): "not sure this sign is right, silence it"
- 0 → -1 (commit): "confirmed, flip it" (only after sustained evidence)
- Reverse: -1 → 0 → +1

The zero state is a staging area. Prevents catastrophic flips. If blocking
hurts, the gradient pushes back immediately.

**Budget control:** flip_rate limits max flips per step. Like a learning
rate but for discrete decisions. Prevents the topology from changing
too fast for Adam to adapt.

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
-  0 → block this position (staging area during transition)

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
