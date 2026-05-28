---
title: Topology-Magnitude Duality
status: active
category: theory
tags: [td, training, overfitting, crystal, convergence]
related:
  - mmap-continuous-training.md
  - kernel-replacement-optimization.md
depends-on: []
---

# Topology-Magnitude Duality

> Session 163. The inverse relationship between discrete topology and
> continuous magnitude explains overfitting, regularization, gnorm
> dynamics, and why TD training converges to a natural stopping point.

## The Core Insight

In ternary training, two parameter types co-evolve:

- **Topology** (TD): sign pattern of ternary weights {+1, -1, 0}.
  Determines WHICH beta reduction to apply. Discrete.
- **Magnitude** (Adam): scale of continuous weights (beams, norms).
  Determines HOW STRONGLY to apply it. Continuous.

**The inverse relationship:** as topology becomes more correct,
magnitudes need to do less work (approach unity). As topology is
wrong, magnitudes must grow to compensate (route around broken signs).

```
correct_topology → magnitudes → 1.0 (no compensation needed)
wrong_topology   → magnitudes → large (compensating for wrong routes)
```

## Why TD Can't Overfit

A ternary weight has 2-3 possible states. That's the entire space.

1. Weight at correct sign → gradient confirms → no flip → nothing happens
2. Weight at wrong sign → gradient accumulates evidence → flip → now correct → stops

There is no third option. You can't "turn up the gain" on a +1.
You can't memorize with a coin. The weight reaches its irreducible
form and stays there regardless of how much more data you show it.

**Continuous weights overfit because continuous topology never converges.**
A float32 weight can always be tweaked at the 8th decimal place.
There is no floor. There is no irreducible form. GD will keep
adjusting until the model memorizes the training data.

## Why Regularization Exists

Every regularization technique is an artificial brake substituting for
the natural stopping point that TD gets for free:

| Technique | What it's secretly doing |
|---|---|
| Weight decay | Pushing magnitudes toward unity |
| Dropout | Breaking topology to prevent memorization |
| Early stopping | Human pulls the plug at the right moment |
| LR schedule | Slowing how fast GD can adjust |
| Batch norm | Constraining magnitude variance |

TD needs none of them. Quantization creates a finite state space →
guaranteed convergence → natural floor → the brake is structural.

## The Gnorm Story

Gnorm dynamics directly express the duality:

- **Gnorm storms** (steps 160-330, 1590): topology changing → magnitudes
  must readjust → large gradients → storm → settles
- **Gnorm plateaus** (steps 800-1590): topology stable → Adam has done
  all it can for current topology → loss stops improving
- **Phase transition**: TD flips → topology changes → magnitudes have
  room to simplify → loss drops

The plateau IS the inverse relationship. Adam pushed magnitudes as
far as they can go. Loss stops. Then TD flips signs → new topology →
magnitudes simplify → loss drops again.

## Training = Fold Reductions Until Irreducible

```
freeze(base) → train(delta) → flips → 0 → fold(delta → base) → repeat
```

Each cycle:
- Delta gets smaller (fewer flips needed)
- Convergence is faster (deeper reductions only)
- Terminates when delta stays identity (nothing to reduce)

No epochs. No LR schedule. No early stopping. The system tells you
when it's done: flip_rate = 0, magnitudes at unity, delta = identity.

## The Topology-Coupled Brake

When topology converges (flips → 0), increase weight decay to push
magnitudes toward unity. The coupling is:

```
decay = base_decay + k * (1 - flip_rate / flip_rate_max)
```

- Flips active → low decay → Adam adjusts freely
- Flips stop → max decay → magnitudes pushed to unity → overfitting prevented
- Self-regulating. No tuning needed.

## Data as Reduction Strategy

Different data exercises different beta reductions. The flip rate on
a batch tells you whether the topology handles those compositions:

- 0 flips → already reduced → skip
- Many flips → unreduced compositions → train on this

Rank data by reduction potential → train on highest first → the model
designs its own curriculum. The irreducible form for ALL data = done.

## Observable Predictions

| If this is true... | Then we should see... |
|---|---|
| Correct topology → small magnitudes | Beam weights shrink as TD converges |
| Wrong topology → large magnitudes | Beam weights large where signs are wrong |
| Weight decay → topological pressure | Higher decay → faster TD convergence |
| Fold → magnitudes simplify | Post-fold, gnorm drops immediately |
| Data variety → faster convergence | Shuffled data → more flips per step |

## Implementation

- FlipMap: `scripts/v14/td.py` FlipMap class
- Shaped nozzle: `scripts/v14/td.py` TernaryDescent.step(hot_fracs=...)
- S2 anti-oscillation: `scripts/v14/td.py` FlipMap.summary() → nozzle_frac
- Data shuffling: `scripts/v14/data.py` ShardedDataLoader
