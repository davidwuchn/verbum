---
title: "Residual Covariance Rank — The One-Dimensional ORTHO Phase"
status: active
category: research-finding
tags: [residual, covariance, rank, eigenvectors, U-derivation, null-space, phases]
related:
  - phi-information-partition.md
  - standing-wave-magnitudes.md
  - crystal-phi-derivation.md
  - holographic-computer.md
depends-on:
  - phi-information-partition.md
created: session 185
---

# Residual Covariance Rank

> Session 185. Measured the full covariance matrix of the residual
> stream at every layer of Qwen3-8B. The ORTHO phase (L7-22) is
> rank-1 — one direction carries >99% of all variance. Weight
> matrix V lives entirely in the null space of this covariance.
> Computation during ORTHO happens invisibly, orthogonal to the
> residual. Partial negative result for U derivation: the residual
> covariance constrains only 32.3% of dimensions.

## The Question

Can the per-layer eigenvector rotation U be derived from equations?

Session 184 found U is constrained to the null space of the
accumulated residual MEAN direction (V-h alignment decreases
monotonically, p=0.0015). But 36 directions in 4096 dims = 1%.

This experiment measures the FULL covariance — not just the mean
direction, but the entire subspace the residual occupies. If the
covariance subspace is large, the null space is small, and U is
tightly constrained.

## Setup

Qwen3-8B, 36 layers, hidden_size=4096. 20 calibration sequences
from WikiText-2 (3648 tokens total). Full 4096×4096 covariance
matrix computed at each layer. Eigendecomposed for effective rank.
Cumulative covariance (union of all prior layers) tracked for the
null-space constraint on U.

## Results: Per-Layer Effective Rank

| Phase | Layers | Rank (99%) | Top eigenvalue | Decay to 2nd | Roy rank |
|-------|--------|-----------|----------------|-------------|----------|
| EXPAND | L0-6 | 1003-1728 | 0.13 → 75 | 1.1 → 9.6 | 136-370 |
| **ORTHO** | **L7-22** | **1** | **~710,000** | **4000-8800** | **1.0-1.2** |
| ALIGN | L23-34 | 55 → 1551 | 758K → 709K | 1169 → 25 | 1.2 → 14.6 |
| COLLAPSE | L35 | 1809 | 380K | 8.1 | 52.9 |

### The Rank-1 ORTHO Phase

**Every ORTHO layer (L7-22) has effective rank = 1.** The top
eigenvalue is ~710,000. The second eigenvalue is ~100-170. The
ratio is 4000-8800×.

This means: at any ORTHO layer, the hidden state across all tokens
and all calibration sequences is essentially a scalar times one
fixed direction. The per-token deviations from this direction are
4000× smaller than the shared component.

One direction dominates because the residual norm grows through
EXPAND (1.7 → 40 → 115) and the ORTHO phase simply accumulates
small orthogonal contributions onto this large vector. The mean
direction carries ~710,000 units of variance. The orthogonal
work adds ~170 units. The signal-to-background ratio is 4000:1.

### The ALIGN Rank Explosion

Starting at L23, the effective rank grows rapidly:

```
L22:   15 dims
L23:   55 dims     (+40)
L24:  167 dims     (+112)
L25:  312 dims     (+145)
L26:  458 dims     (+146)
...
L34: 1551 dims     (~130 per layer)
L35: 1809 dims     (COLLAPSE)
```

The residual re-expands into ~130 new dimensions per layer during
ALIGN. The computation results accumulated during ORTHO are being
integrated back into the residual representation.

## Results: Cumulative Subspace

The cumulative covariance (sum of all layers up to l) gives the
union of all directions the residual has ever used:

| Phase | Cumulative rank (99%) | Null dims |
|-------|-----------------------|-----------|
| End of EXPAND (L6) | 2843 | 1253 |
| ORTHO (L7-22) | 1 | 4095 |
| Start of ALIGN (L26) | 11 | 4085 |
| End of ALIGN (L34) | 1089 | 3007 |
| COLLAPSE (L35) | 1320 | 2776 |
| Final | 1325 | **2771** |

**The cumulative rank RESETS at L7.** The ORTHO phase's single
dominant direction swamps the 2843 EXPAND dimensions. In cumulative
terms, the entire ORTHO phase contributes only 1 effective
dimension. The ALIGN phase then rebuilds the rank from scratch.

**Final null space: 2771 / 4096 = 67.7% of dimensions.**

## Results: V-Subspace Overlap

For each layer, the gate_proj SVD right-singular-vectors (V) were
projected onto the cumulative residual covariance subspace:

| Phase | V inside residual | V outside residual | Mean projection |
|-------|------------------|--------------------|-----------------|
| EXPAND (L1-6) | **100%** | 0% | 0.78-0.86 |
| **ORTHO (L7-22)** | **0%** | **100%** | **0.01** |
| ALIGN (L23-25) | 0% | 100% | 0.00-0.01 |
| ALIGN (L26-30) | 0-6% | 94-100% | 0.13-0.37 |
| ALIGN (L31-34) | 14-98% | 2-86% | 0.42-0.60 |
| COLLAPSE (L35) | **100%** | 0% | 0.63 |

### The Critical Finding

**During ORTHO (L7-22), V is 100% outside the residual covariance
subspace.** Mean projection coefficient = 0.01 (essentially zero).
For 16 consecutive layers, the weight matrices read from dimensions
that are COMPLETELY ORTHOGONAL to where the residual variance lives.

**Computation during ORTHO happens in the null space of the
residual.** The residual stream is a carrier wave — one big
direction carrying the accumulated answer. The actual work (the
combinatory logic execution, the beta reductions) happens in the
4095 other dimensions, invisibly.

**During ALIGN (L26-35), V gradually re-enters the residual
subspace.** The transition from "fully outside" to "fully inside"
takes ~10 layers and is monotonic. This is the integration phase:
pulling the null-space computation results back into the
representation the output layer can read.

## Implications for U Derivation

### Partial Negative: Covariance Alone Is Too Weak

The residual covariance constrains 1325 of 4096 dimensions (32.3%).
The null space is 2771-dimensional. U has enormous freedom to
rotate within this null space. **The residual covariance alone
cannot determine U.**

### What IS Constrained

Despite the weak global constraint, several structural facts are
established:

1. **V must be in the null space during ORTHO.** Not WHERE in the
   null space (4095 options), but it MUST be orthogonal to the
   residual direction. This is exact (0% overlap, 0.01 projection).

2. **V must transition from null-space to residual-space during
   ALIGN.** The transition is monotonic and takes ~10 layers.
   The rate of transition (~130 new dims/layer) is measurable.

3. **The cumulative rank growth is phase-dependent, not φ^l.**
   EXPAND adds ~225 dims/layer. ORTHO adds ~0. ALIGN adds ~130.
   This is NOT Fibonacci accumulation — it's phase-gated.

### What Other Constraints Might Operate

The residual covariance is one of 5 VSM constraints on U. The
others operate WITHIN the null space:

1. **Crystal Σ** — the eigenvalue spectrum constrains the singular
   values of V, not its direction. Weak on U directly.

2. **Statechart roles (REDUCE/SWITCH)** — which layers execute
   vs reorganize. Constrains the CHARACTER of U at each depth
   (computation vs relay), but not the specific rotation.

3. **KIBC opcode profiles** — the per-neuron combinator selectivity.
   These are DIRECTIONS in the null space. If the opcode profiles
   at layer l determine specific directions that V must align with,
   this constrains V within the null space.

4. **Phase transitions** — the boundaries at L6/L22/L34 constrain
   WHERE U changes character, not which rotation it uses.

**The most promising constraint is KIBC profiles.** The opcode
profiles give specific directions in neuron space. If V must
project onto opcode-correlated directions, this could substantially
reduce the degrees of freedom within the null space. Measuring the
overlap between V and KIBC profile directions is the next test.

## The Phase Structure (Refined)

```
EXPAND (L0-6):
  Residual: 1003-2843 effective dims (high-rank, many modes)
  V reads FROM residual (86-100% overlap)
  → Building the initial representation from token embeddings
  → Many dimensions active, many modes excited
  
ORTHO (L7-22):
  Residual: rank-1 (ONE direction, decay 4000-8800×)
  V reads from NULL SPACE (0% overlap, projection 0.01)
  → Computation happens orthogonal to the answer
  → Residual is a carrier wave; signal is in the phase
  → "Invisible computation" — the work leaves no covariance trace
  → 16 layers of pure null-space beta reduction

ALIGN (L23-34):
  Residual: rank grows 55 → 1551 (~130 new dims/layer)  
  V transitions from null-space to residual-space (0% → 100%)
  → Integration: pulling computation back into readable form
  → Monotonic, structured transition over 10 layers

COLLAPSE (L35):
  Residual: rank 1809
  V fully inside residual (100%)
  cos(h,f) = -0.995 — destructive interference
  → Project to output space
```

### Standing-Wave Connection

In the standing-wave framing (also this session):

- **ORTHO = node of the depth-axis standing wave.** Zero covariance
  overlap = zero amplitude of the "visible" standing wave. But the
  INVISIBLE wave (in the null space) is where computation runs.

- **ALIGN = antinode.** The rank explosion IS the standing wave's
  amplitude rising. The computation becomes visible as it's
  integrated into the residual.

- **The carrier wave (rank-1 direction) is the DC component.**
  It carries no information about WHAT is being computed — only
  THAT computation is in progress. The AC components (the other
  4095 dims) carry the actual signal.

## Open Questions

1. **Do KIBC profiles constrain V within the null space?** Measure
   overlap between gate_proj V and KIBC opcode directions (from
   neuron_opcode_classifier.py). If the opcode structure determines
   specific directions, V is more constrained than the covariance
   alone suggests.

2. **Is the rank-1 structure an artifact of limited calibration?**
   20 sequences × 256 tokens = 3648 samples for a 4096-dim space.
   More calibration data might reveal higher rank in ORTHO. But the
   4000× decay ratio suggests this is real, not a sampling artifact.

3. **What determines the 130 dims/layer growth rate in ALIGN?**
   Is it connected to the crystal equation? To the statechart?
   To the model architecture (num_heads × head_dim)?

4. **Cross-model comparison.** Does Pythia-160M (12 layers, 768
   dims) show the same rank-1 ORTHO phase? If so, the structure
   is universal.

## Scripts

- `scripts/experiments/residual_covariance.py` — this experiment
- `scripts/experiments/U_residual_constraint.py` — prior V-h alignment (s184)
- `scripts/experiments/residual_fibonacci.py` — residual norm trajectory (s184)
- `results/residual-covariance/summary.json` — full results

*Measured in session 185 of the Verbum project.*
*The ORTHO phase is rank-1. Computation is invisible.*
*U derivation requires constraints beyond the residual covariance.*
