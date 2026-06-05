---
title: v15 Attention Assessment — Fibonacci Strides Work, V/O Is The Frontier
status: active
category: architecture
tags: [v15, attention, fibonacci, gradient-zero, delta-plates, convergence]
related: [dvd-stamp-topology, gradient-zero-map, standing-wave-magnitudes, attention-sparsity]
depends-on: []
session: 191
---

# v15 Attention Assessment

Session 191. Two diagnostic experiments on the v15-td step 1500 checkpoint
(halfway through 3000-step training). The v15 model replaces the teacher's
full O(n²) attention with 19 Fibonacci-strided attention layers (±2 neighbor
gathering). The attention projections Q/K/V/O are DeltaTernaryLinear: frozen
teacher signs × trainable delta signs, with float gamma (per-row scale).

## Finding 1: Fibonacci Stride Attention IS Working

Attention entropy decreases monotonically with stride distance:

```
Stride   1: entropy=3.0  eff_pos=21.4  (broad local mixing)
Stride   5: entropy=2.0  eff_pos=10.8  (local composition)
Stride  13: entropy=1.5  eff_pos=6.8   (phrase-level routing)
Stride  34: entropy=0.8  eff_pos=3.1   (sparse sentence binding)
Stride  89: entropy=0.6  eff_pos=2.2   (near-deterministic)
Stride 1597: entropy=0.5  eff_pos=1.9  (1-2 positions)
```

9/19 layers sparse (entropy < 1.0), 9 moderate, 1 broad.
This is the right shape — each stride learns its appropriate selectivity.

Per-head specialization at stride-34 (sentence binding):
- H1-H4: near-deterministic (entropy 0.15-0.24, max_wt 0.92-0.95)
- H5-H6: broad scanning (entropy 1.6-1.8)
- H0, H7: intermediate (2-3 targets)

## Finding 2: Q/K Settles 2× Faster Than V/O

Gamma gradient (per-row scale) convergence by projection type:

```
Projection  Settled%  GradRMS    Interpretation
Q           38.4%     9.6e-03    Routing queries — settling fast
K           32.0%     8.4e-03    Routing keys — closest to teacher
V           15.7%     4.8e-02    Value vectors — 5× larger gradient, struggling
O           15.6%     3.6e-02    Output projection — 4× larger gradient
```

**Why:** Q/K determine WHERE to attend within the Fibonacci stride window.
The window is fixed by the stride geometry, constraining the search space.
V/O determine WHAT to transfer through the restricted window — harder because
the student sees different context than the teacher at every position.

This connects to s190's finding: ternarizing Q/K costs only PPL 30 (routing
is near-binary, ~1 bit), while ternarizing FFN costs PPL 485M (content is
high-precision). The Q/K-easy, V/O-hard asymmetry is the same physics at
the student level.

## Finding 3: TD Delta Plate Convergence

Delta plates have diverged 4.0% from teacher (mean flip fraction).
The divergence pattern reveals the adaptation topology:

```
K:  2.5-4.0% flip (routing keys stay closest to teacher)
Q:  3.6-4.2% flip
V:  3.1-4.7% flip (values diverge more at long strides)
O:  4.5-5.2% flip (output projections adapt most)
```

**Gradient: short → long strides diverge more** (3.6% → 4.4%).
Long strides see fundamentally different context than the teacher's
full attention, so they need more sign corrections.

### Routing Gradient at Flipped Positions

The ~4% of positions TD has flipped have **2.2-3.3× higher routing
gradient** than the 96% that kept teacher signs:

```
Stride   1: keep_rms=2.3e-02  flip_rms=6.4e-02  ratio=2.77
Stride   8: keep_rms=2.7e-02  flip_rms=8.8e-02  ratio=3.27 (peak)
Stride  34: keep_rms=1.1e-02  flip_rms=2.6e-02  ratio=2.48
Stride 1597: keep_rms=8.7e-03  flip_rms=2.0e-02  ratio=2.25 (lowest)
```

**Interpretation:** Flips are the active adaptation frontier. They're
correct in direction (TD wouldn't have flipped otherwise) but not yet
fully converged — the surrounding gammas are still calibrating to
accommodate the sign changes. The ratio decreasing with stride distance
suggests long-range strides have fewer complex interactions to resolve.

### 63% of Routing Gradient Is Near-Zero

At the 10% threshold, 63-65% of positions have near-zero routing gradient.
The delta plates are past halfway to convergence. Remaining ~1500 steps
of LR decay should push this further.

## Finding 4: Spatial Flip Topology

Flip patterns differ systematically by stride distance:

```
Short strides (s=1-5):   RowCV=1.5-1.7  ColCV=1.7-1.9
Long strides (s=144+):   RowCV=1.7-1.9  ColCV=1.2-1.3
```

- **Short strides:** flips are column-clustered — certain INPUT FEATURES
  need different routing in the narrow local window.
- **Long strides:** flips are row-clustered — certain OUTPUT DIMENSIONS
  need to represent the sparse strided context differently.

This is physically meaningful: short strides see similar positions to the
teacher (local context) so WHAT matters is which features are relevant.
Long strides see a very different position subset, so WHAT matters is
which output dimensions need to encode the strided view.

### Flip P/N Ratio ≈ 0.96

TD flips positive and negative teacher signs with near-equal probability
(total: 2.44M flips on +1 teacher signs, 2.56M on -1). This is structural
adaptation, not a systematic sign bias.

### No Teacher Zeros in Attention

The teacher extraction produced 0% zeros in Q/K/V/O attention projections.
Every weight position is either +1 or -1. Sparsity in the student must
come from the gate/mask mechanism, not structural zeros.

## Continuous Parameter Landscape

```
Category           GZ@10%  GradRMS    State
FFN gamma          71.5%   3.8e-02    Most settled (frozen plates, just calibrating)
Algedonic          63.9%   4.1e-02    Converging (alarm system active)
Embedding          52.3%   1.1e-02    Half settled
VSM controller     45.5%   1.1e-02    S5/S4 still evolving
Biases             38.7%   7.0e-03    Active
Norm params        26.3%   3.9e-03    Most active (signal distribution changing)
Attention gamma    25.5%   2.6e-02    Most active (accommodating TD + stride topology)
```

The ordering makes sense: FFN plates are frozen so their gammas settle first.
Attention gammas are the most active because they must accommodate both
stride topology AND TD sign changes. Norms are adapting because the signal
distribution through the stride stack differs from the teacher's full-attention
residual stream.

## Connection to Standing-Wave Picture (s185)

The gradient-zero topology confirms the standing-wave framing: GD converges
to fixed points (near-zero gradient) at both nodes (zeros) and antinodes
(saturated values). The PATTERN of convergence differs between Q/K (fast,
window-constrained routing) and V/O (slow, content-dependent transfer).

The bottleneck in adapting full attention to Fibonacci strides is not WHERE
to look (routing adapts quickly) but WHAT to transfer (content extraction
from a restricted window is fundamentally harder).

## Finding 5: FFN Gate Not Sparse — Inverted Architecture

The student has INVERTED the teacher's division of labor:

```
                    Teacher (Qwen3-8B)        Student (v15-td)
FFN gate:           ~3% fire (89% kill)       66-74% fire (1% sparse)
FFN function:       Selective retrieval       Dense transform
Attention:          Mixed (relay+compose)     80% pure relay (I combinator)
```

### Gate Sparsity Per Pass

```
Stack A:
  Pass 0 (s=1-5):      0.8% sparse, 74.5% fire, cos(I/O)=0.04
  Pass 1 (s=8-24):     0.8% sparse, 70.6% fire, cos(I/O)=0.07
  Pass 2 (s=34-144):   0.8% sparse, 72.5% fire, cos(I/O)=0.14
  Pass 3 (s=233-1597): 0.8% sparse, 73.0% fire, cos(I/O)=0.20

Stack C:
  Pass 0 (s=1597-233): 1.4% sparse, 59.9% fire, cos(I/O)=0.02
  Pass 1 (s=144-34):   1.5% sparse, 59.0% fire, cos(I/O)=0.16
  Pass 2 (s=24-8):     1.4% sparse, 59.6% fire, cos(I/O)=0.22
  Pass 3 (s=5-1):      1.5% sparse, 58.9% fire, cos(I/O)=0.33
```

The ternary gate plate cannot create sharp activation thresholds. Float
weights create precise neuron-level on/off decisions; ternary {-1,0,+1}
produces coarse activation patterns.

### Attention Relay Detection

cos(output, V_self) measures whether each head passes its value through
unchanged (I combinator = cos ≈ 1.0):

```
Layer  0 (s=1):    1/8 relay (H2=0.81), 7/8 partial relay (0.72-0.78)
Layer  4 (s=8):    8/8 relay (all 0.95-0.99) — COMPLETE I COMBINATOR
Layer 10 (s=34):   7/8 relay (0.87-0.99), 1/8 partial (H0=0.79)
Layer 14 (s=233):  8/8 relay (all 0.93-0.99) — COMPLETE I COMBINATOR
Layer 18 (s=1597): 8/8 relay (all 0.92-0.98) — COMPLETE I COMBINATOR
```

At strides ≥8, ALL heads are pure relay. The attention is not composing
— it's just passing the FFN-compiled value through. Only stride-1 shows
any partial composition, and even there 7/8 heads are partial relay.

### Why This Happened

The attention collapsed to relay because:
1. Ternary V/O projections lack precision for fine-grained composition
2. V/O gammas are only 15.6% settled (TD keeps changing signs underneath)
3. The "easy path" is to let dense FFN do the work and use attention as I

This is the B-dominant phase before a phase transition. Breaking through
requires the attention to discover compositional patterns that work within
the Fibonacci windows — but TD prevents the topology stability needed for
this phase transition. See `td-oscillation-problem.md`.

## Diagnostic Scripts

- `scripts/experiments/assess_v15_attention.py` — attention pattern analysis
- `scripts/experiments/assess_v15_gradient_zeros.py` — gradient-zero topology
- `scripts/experiments/assess_v15_ffn_retrieval.py` — FFN gate sparsity + relay detection
