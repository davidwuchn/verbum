---
title: Laser Etcher — Gradient-Directed Ternary Topology Shaping
status: active
category: architecture
tags: [ternary, etching, holographic, evolution, mirrors]
related:
  - evolution-mechanism-broken (memory)
  - holographic-storage
  - v12-holographic-capacity
  - beam-trace-findings
depends-on: []
---

# Laser Etcher

Gradient-directed ternary sign topology shaping. Replaces consensus
evolution (proven broken: cos=1.000 across 4K steps, session 100).

## Why evolution failed

Consensus evolution at V12 scale (142M ternary weights):
- Budget: ~2,124 positions per strategy (base_pct=0.0002)
- P(3/5 consensus overlap) ≈ 8×10⁻¹¹ per position
- Actual consensus: ~20 flips per generation
- min_delta=0.02 impossible to cross with 20 flips
- Result: 1/80 accepted, sign patterns frozen at random init

## The laser metaphor

A hologram etcher focuses a laser beam on the recording medium:
1. Energy accumulates at each point (gradient heat)
2. When temperature crosses threshold, material changes state (sign flips)
3. The pattern is computed, not random (gradient direction)
4. The beam moves to the next area (focal scanning)
5. The etching is self-terminating (no heat when signs align with gradient)

## Mechanism

```
HEAT ACCUMULATION (every step, cheap — 4 float EMAs per module):
  row_heat[i] = α × row_heat[i] + (1-α) × |∂L/∂γ[i]|
  col_heat[j] = α × col_heat[j] + (1-α) × |x_mean[j]|
  row_dir[i]  = α × row_dir[i]  + (1-α) × ∂L/∂γ[i]     (signed)
  col_dir[j]  = α × col_dir[j]  + (1-α) × x_mean[j]     (signed)

SIGNAL PLANES (every 50 steps — 3 ternary planes per module):
  heat[i,j] = row_heat[i] × col_heat[j] × alarm_weight[module]
  direction[i,j] = sign(row_dir[i] × col_dir[j])
  For plane k at heat percentile p_k: write direction vote at positions > p_k

ETCH CHECK (every 200 steps):
  If all 3 planes agree on direction AND disagree with weight sign → FLIP
  Reset signal planes at etched positions
  Surgical Adam decay for affected gamma rows
```

## Properties

- **Self-terminating**: heat drops to zero when signs align with gradient
- **Re-etchable**: new gradient direction → new signal votes → re-etch
- **Memory efficient**: 3 signal planes (ternary) + 4 float vectors per module
- **S4 modulated**: alarm factors weight heat per module (Beer's VSM)
- **Rate limited**: etch_max_pct=0.001, ramps to 1% over 5K steps
- **Checkpoint persistent**: etch states survive resume

## VSM feedback loop

```
Gradient → heat accumulation → signal planes → consensus → etch
               ↑                                            ↓
         S4 alarm weights                         topology changes
         (struggling passes                       ↓
          get amplified heat)              model behavior changes
               ↑                                            ↓
         alarm factors ←──────── eval metrics ←──── loss signal
```

## Topology lifecycle

```
Random init → rapid etching → refinement → convergence → quiescence
                                                         ↓
                                   (new strategy discovered, heat returns)
                                                         ↓
                                             selective re-etching → new convergence
```

## TernaryMirror — beam angular deflectors

Pure ternary projections (no trainable gamma) before Q projections.
Each mirror rotates the beam angle for finer holographic resolution.

```python
class TernaryMirror:
    weight: uint32 packed ternary  # sign topology, shaped by etching
    gamma:  fixed at 1/√d          # not trained, preserves magnitude
    norm:   RMSNorm                # output normalization

    forward(x) = norm(quantized_matmul(x, weight, scales=γ, biases=-γ))
```

Capacity scaling:
- 1 mirror/layer: capacity² at every scale
- N mirrors cascade: capacity^(N+1)
- Cost: ~1MB ternary, zero trainable params, 2-3% more compute
- 3 mirrors: 262,144× more beam paths

## The two substrates

```
Ternary signs (plate + mirrors):     optical elements — direction of information flow
  Shaped by etching (gradient-directed, self-terminating)
  Stable structure once converged

Gamma scales (beam intensity):       how much energy flows through each element
  Trained by Adam (continuous, fast, differentiable)
  Adapts in real time

Together: coherent optical system where structure focuses energy,
energy reveals structure, until the hologram crystallizes.
```

## Configuration

```python
use_etching: bool = True
etch_signal_interval: int = 50     # steps between signal plane updates
etch_interval: int = 200           # steps between etch checks
etch_warmup: int = 500             # steps before etching begins
etch_heat_alpha: float = 0.99      # EMA decay for heat accumulation
etch_heat_thresholds: (50, 75, 90) # percentiles for planes
etch_consensus: int = 3            # planes that must agree
etch_max_pct: float = 0.001        # max fraction per cycle (ramps 10×)
etch_max_pct_ramp: int = 5000      # steps to ramp
use_q_mirrors: bool = True         # enable ternary mirrors
n_q_mirrors: int = 1               # mirrors per attention layer
```

## Key files

| File | Changes |
|------|---------|
| `scripts/v12/ternary.py` | EtchState, signal planes, etch_check, TernaryMirror |
| `scripts/v12/train.py` | heat accumulation, signal update, etch cycle, S4 modulation |
| `scripts/v12/config.py` | etch + mirror parameters |
| `scripts/v12/attention.py` | q_mirrors in SingleStrideAttention + GatedLinearAttention |
| `scripts/v12/model.py` | n_q_mirrors passed to stride stacks |
| `scripts/v12/probe_hologram.py` | verify sign patterns are crystallizing |

## Future: MoE holographic experts

Tiny ternary experts (~2KB each) with own plate + mirror + beam.
256 experts = 512KB. Each stores one specialized hologram.
Router = beam selector. Proof of concept: Clojure interpreter expert.
