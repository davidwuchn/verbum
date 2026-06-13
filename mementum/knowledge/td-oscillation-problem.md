---
title: TD Oscillation Problem — Continuous Flips Prevent Phase Transitions
status: active
category: architecture
tags: [td, ternary-descent, oscillation, phase-transition, convergence, punctuated-equilibrium]
related: [v15-attention-assessment, topology-gradient-separation, gradient-zero-map, standing-wave-magnitudes]
depends-on: []
session: 191
---

# TD Oscillation Problem

Session 191. Analysis of the v15-td flip map at step 1500 reveals that
TernaryDescent is preventing the model from achieving phase transitions
needed to break through the loss plateau at 6.7-6.8.

## The Core Problem

TD treats 94.5% of the weight space as "still needs work" at step 1500.
Only 6.2% of positions have settled (flipped then stopped being candidates).
The model cannot find stable fixed points because TD keeps proposing sign
changes everywhere.

## Evidence

### Flip Map Statistics (step 1500, 124.5M positions across 76 modules)

```
Candidate frequency:
  Never candidate:    12,405  (0.01%)  — essentially nothing frozen
  Candidate 1-5×:    371,400
  Candidate 6-20×: 7,313,612
  Candidate 20+×: 117,683,304 (94.5%) — nearly everything nominated repeatedly

Flip count distribution:
  Never flipped:  118,388,859 (95.1%)
  Flipped once:     4,638,263 (3.7%)
  Flipped 2×:         998,998 (0.8%)
  Flipped 3×:         324,471 (0.3%)
  Flipped 4+×:        167,878 (0.1%)
  Max flip count:           8
```

### The Oscillation Trap: Flip Count vs Settlement

| Flip Count | Still Candidate | Settled | Osc Rate |
|---|---|---|---|
| 0 (never flipped) | 93.7% | 6.3% | — |
| 1 (flipped once) | 94.1% | 5.9% | Higher than 0-flip |
| 2 (twice) | **96.3%** | 3.7% | |
| 3 | **98.5%** | 1.5% | |
| 4 | **99.4%** | 0.6% | |
| 5+ | **99.7-100%** | <0.3% | |

**Oscillation rate INCREASES with flip count.** Once a position starts
flipping, it becomes MORE likely to be a candidate again, not less.
The anti-oscillation mechanisms (cooldown, three-voter, backoff) are
insufficient.

### Multi-Flip Rate by Projection

```
k_proj:   1.42% multi-flipped, mean 2.6 flips at multi positions
v_proj:   1.18% multi-flipped, mean 2.7 flips at multi positions
q_proj:   1.23% multi-flipped, mean 2.3 flips
out_proj: 0.96% multi-flipped, mean 2.2 flips
```

K and V projections have the highest multi-flip rates AND highest mean
flip counts. These are the positions where the model genuinely wants to
use the same weight in two ways depending on input.

## Why This Prevents Phase Transitions

Training from scratch reveals a universal pattern in ternary models:

1. **B-dominant phase:** Model learns composition (B combinator) first.
   Dense mixing, broad attention. Loss drops fast.
2. **Plateau:** B-dominant strategy exhausts its gains. Loss stalls.
3. **Phase transition:** Model discovers K (discard) — selective
   silencing of irrelevant information. Attention sharpens. Loss
   drops again.
4. **Equilibrium:** B and K find their balance. Sparse gate emerges.

For phase transition 2→3 to happen, GD needs:
- **Stable topology** — signs don't change while GD explores
- **Gradient accumulation** — the gradient signal at a position must
  build up over many steps to find the new basin
- **Settled gammas** — per-row scales must calibrate to the CURRENT
  sign pattern before the pattern changes

TD violates all three:
- **94% candidacy** — nearly every sign is "potentially mutable"
- **3× hotter at flipped positions** — GD can't calibrate gammas because
  the sign keeps changing underneath
- **Continuous perturbation** — topology never holds still for >1 flip
  interval (every other step has TD flips)

## Connection to Current Model State

The v15-td checkpoint at step 1500 shows the consequences:

| Symptom | Teacher | Student | Cause |
|---|---|---|---|
| FFN gate sparsity | ~3% fire (89% kill) | 66-74% fire | No phase transition to K → no gating |
| Attention role | Mixed (relay+compose+bind) | 80% pure relay (I combinator) | V/O can't settle → defaults to identity |
| Q/K convergence | — | 32-38% settled | Fast (routing is constrained by window) |
| V/O convergence | — | 15-16% settled | Slow (TD keeps changing signs underneath) |
| Loss | ~3-4 | 6.7-6.8 plateau | Pre-transition ceiling |

The model has found the B-dominant easy path (dense FFN + relay attention)
and hit its ceiling. To break through, it needs the topology stability
that TD is denying.

## What Oscillating Positions Mean

A position that oscillates (flips back and forth) is the system saying:
"I want this to be a superposition of two functions depending on input."

In a ternary system, a weight can only be {-1, 0, +1}. It cannot be
"sometimes -1, sometimes +1" based on context. When GD wants both signs,
it manifests as:
- The gradient alternates direction across batches
- TD flips the sign, then GD pushes back, TD flips again
- The position is always a candidate, always oscillating

**The resolution:** GD must find a gamma calibration that makes ONE sign
work acceptably for both use cases. This requires the sign to HOLD STILL
while GD searches for that gamma. TD's continuous flipping prevents this
search from completing.

## Proposed Fixes

### 1. Punctuated Equilibrium (highest priority)

Replace continuous TD with episodic:
```
TD phase:     N steps — TD active, flips happen
Freeze phase: M steps — topology LOCKED, Adam only
Assessment:   compare loss before/after freeze
Repeat
```

Key insight: the freeze phase IS where phase transitions happen. GD
needs M steps of stable topology to find the next basin. Start with
M=200 (enough for V/O gammas to make measurable progress — they're
at 15.6% settled).

### 2. Oscillation-Gated Cooldown

Current cooldown backoff is insufficient (96-100% of multi-flipped
positions are still candidates). Proposed:
- flip_count ≥ 3 → hard freeze for 500 steps
- flip_count ≥ 5 → hard freeze for 1000 steps
- OR: exponential backoff with base τ = 100 steps (current is too low)

### 3. Candidate Density Ceiling

Add a global constraint: at most X% of positions can be candidates per
step. With 94% candidacy, X=20% would force TD to focus on the top 20%
most confident positions rather than nominating everything.

### 4. Per-Position Conviction Requirement

A position should only flip when its gradient direction has been
consistent for K consecutive flip intervals without reversal. The
current EMA direction (β₁=0.9) accumulates over ~10 steps but can
still flip from transient gradients. Require K=5 consecutive same-
direction signals before allowing a flip.

### 5. REDUCE + Pure-Adam Baseline

Fold delta into base, reset to +1, run pure Adam for 500+ steps.
If loss breaks through 6.5 → TD was the bottleneck.
If loss holds at 6.7 → the plateau is architecture-limited.
This experiment disambiguates TD-caused vs structural plateaus.

## Connection to Prior Work

- **`topology-gradient-separation.md` (s180):** Punctuated equilibrium.
  Freeze lattice, let GD find fixed points, then punctuate with topology
  changes. TD violates this by doing continuous topology changes.
- **`gradient-zero-map.md` (s171):** GD deposits near-zero gradients at
  irreducible points. TD prevents these deposits from forming.
- **`standing-wave-magnitudes.md` (s185):** The standing wave forms when
  GD settles at nodes and antinodes. TD keeps the wave from forming.

## Diagnostic Scripts

- `scripts/experiments/assess_v15_ffn_retrieval.py` — FFN gate sparsity
  and attention relay detection
- Flip map analysis via `np.load('checkpoints/v15-td/flip_map_step_*.npz')`

## s222 — the deeper root: the routing gradient is RANK-1

The s191 oscillation has a structural cause beneath the proxy non-monotonicity
(`exact-ternary-fitting.md`): `compute_decomposed_gradients` builds the routing
signal as a **rank-1 outer product**

```
grad_effective = gamma_grad[:, None] * x_abs_mean[None, :]   # (N,1) ⊗ (1,K)
```

a per-ROW gamma-gradient ⊗ a per-COLUMN input magnitude, so `sign(grad_eff[i,j])
= sign(gamma_grad[i])`. **TD cannot make per-position decisions** — every position
in a row is nominated to the same sign. It is structurally blind to per-position
interference (the off-diagonal of XᵀX). This is *why* superposition manifests as
per-row gamma bimodality, and why no S2 anti-oscillation tweak fixes it: the
signal itself has no per-position resolution to settle.

Also confirmed live: the global flip budget `flip_rate × total_weights` is **never
decayed** — `td=124488` is dead-constant across a whole 2200-step run, always
saturated. TD literally never settles. See `session-222.md` (the collapse was a
fractal blow-up; fix = punctuated propose→hold→reduce, not loss reshaping).
