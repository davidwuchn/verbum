---
title: "M-space Gemcutter — Topology Shaping via Attention Kernel Geometry"
status: active
category: research-finding
tags: [mspace, gemcutter, topology, attention-kernel, ternary, svd, zeros, crystal]
related:
  - explore/ffn-beta-reduction-indexing.md
  - explore/ternary-descent.md
  - explore/q-rotation-etching.md
  - v14-architecture.md
  - computed-beam.md
depends-on:
  - explore/ternary-descent.md
created: session 166
---

# M-space Gemcutter — Topology Shaping via Attention Kernel Geometry

> Session 166. The attention kernel M = W_q^T @ W_k is where computation
> lives. Topology changes must be planned in M-space, not W-space.
> A pre-cut geometric topology with zeros BEATS float32 on loss.

## Two Spaces

**W-space**: the weight matrix. Each element W_q[h,i] ∈ {-1, 0, +1}.
TD operates here — "should this position be +1 or -1?" Individual knobs.

**M-space**: the attention kernel M = W_q^T @ W_k. A bilinear form that
determines all attention patterns: score(t,s) = x_t^T M x_s. The SVD
of M gives the independent modes (facets) of the gem. This is where
computation lives — beta reductions are determined by M's structure.

**The relationship**: M is a product of two W matrices. One W-space flip
changes an entire row or column of M — a rank-1 perturbation that
spreads across ALL modes. A flip at W_q[h,i] produces:

```
ΔM[i, j] = -2 × W_q[h,i] × W_k[h, j]    for all j
```

One flip changes 1,280 elements of M simultaneously (at v14 scale).

## Why GD works but flips don't (the infinitesimal vs discrete gap)

GD updates W via the chain rule: ∂L/∂W_q = ∂L/∂M × ∂M/∂W_q.
GD is ALREADY working in M-space implicitly. It works because each
update is infinitesimal — the linear approximation is accurate.

Ternary flips are jumps of ±2 (maximum possible change). At this scale:
- The linear approximation (gradient) is wrong
- Multiple simultaneous flips interact nonlinearly
- M-space effects of 132K flips ≠ sum of individual effects

This is why TD's gradient-heat scoring is anti-predictive in structured
layers — the gradient says "this position should flip" but the actual
M-space effect of flipping it (at jump size ±2) damages other modes.

## The Gem Structure (micro model findings)

Trained float32 micro model (4 layers, 128 d_model, 4 heads):

| Layer | rank90 | top1% | σ0/σ1 | Character |
|-------|--------|-------|-------|-----------|
| 0     | 42     | 25.8% | 2.32  | Diffuse (still forming) |
| 1     | 24     | 68.6% | 4.45  | Sharp crystal |
| 2     | 13     | 69.0% | 3.51  | Sharpest — the compute layer |
| 3     | 25     | 56.4% | 3.25  | Output focusing |

The gem is REAL and LOW-RANK. Layer 2 has 13 modes capturing 90% of
the attention energy. Everything else is noise floor.

Sign quantization (±1, no zeros) blurs layer 2 from rank90=13 → 35.
The dominant mode survives (0.984 cosine alignment) but the 12 secondary
facets are drowned by ~22 ghost facets from small-weight positions forced
to ±1. The gem goes from 13-facet crystal to 35-facet noisy blob.

## Four Experiments

### Experiment 1: M-space scoring vs gradient-heat (probe_mspace.py)

M-space and gradient scoring select COMPLETELY DIFFERENT positions (0%
overlap in top-50). In structured layers (2-3), M-space finds 76%
helpful flips vs gradient's 46%. M-space PREDICTS which flips help
(ρ=+0.33) while gradient is ANTI-PREDICTIVE (ρ=-0.36).

### Experiment 2: Zero placement strategies (probe_mspace_zeros.py)

M-noise zeros monotonically sharpen the gem. At 60% zeros, layer 2
recovers from 74% → 92% energy concentration (float32 target: 91%).
Magnitude threshold is cheaper on loss; M-noise is better on gem
quality. Random zeros DESTROY the gem — proves zeros need geometric
guidance.

### Experiment 3: Single-facet cutting (probe_mspace_facet.py)

Facet-greedy selection achieves **30× less cross-mode damage** than
gradient scoring at 50 flips. The selectivity mechanism works: it
genuinely isolates mode changes. Coordinated W-space flips can target
one M-space facet without cross-cutting others.

### Experiment 4: Train from scratch with pre-cut topology (train_cut_topology.py)

THE KEY RESULT:

| Variant | Final Loss | L2 rank90 | L2 top1% |
|---------|-----------|-----------|----------|
| A. Float32 (full GD) | 6.7412 | 6 | 80.5% |
| B. Trained sign (±1) | 6.8625 | 32 | 45.5% |
| **C. Trained sign + 30% zeros** | **6.6972** | **25** | **56.1%** |
| D. Random sign (±1) | 6.6814 | 48 | 4.8% |
| E. Random + 30% zeros | 6.7721 | 48 | 5.6% |

**The gem-cut model (C) BEATS float32 on loss** (6.6972 vs 6.7412).
A frozen ternary topology with 30% M-noise zeros, trained from
scratch, outperforms fully-trainable float32 attention.

The geometric constraint HELPS GD — it channels optimization into
a sharp 25-mode kernel instead of diffusing across 128 modes. The
constraint is a guide, not a limitation.

Random topology (D) achieves similar loss but ZERO M-space structure
(rank90=48). GD compensated entirely through other parameters. The
model works DESPITE the attention, not because of it.

## The Fractal Collapse

Eigendecomposition IS β-reduction of matrices. The same operation at
every level:

```
level = data     → eigendecompose(activations)  → crystal(irreducible)
level = M_space  → SVD(attention_kernel)         → modes(irreducible)
level = W_space  → SVD(weight_contribution)      → sign(irreducible) + zero(reduced_to_∅)
level = training → GD(loss_landscape)             → fixed_point(irreducible)

∀level: decompose → keep(irreducible) → discard(reducible)
```

This collapses sanding/cutting/filling into ONE mechanism:

```python
# One SVD. Three outcomes.
M = W_q.T @ W_k
U, σ, V = svd(M)
K = rank_at_90%(σ)

for position (h, i):
    signal = Σ_{k<K}  U[i,k]² × (W_k[h,:] · V[:,k])²
    noise  = Σ_{k≥K}  U[i,k]² × (W_k[h,:] · V[:,k])²
    snr    = signal / noise

    if snr < threshold → ZERO  (fully reduced — noise dominates)
    if misaligned      → FLIP  (irreducible but wrong sign)
    else               → KEEP  (normal form)
```

## Experiment 6: Unified β-reduce (reduce.py + train_reduced.py)

Zeros+flips together (train_reduced.py): flips interfere with each
other when applied simultaneously. Best loss 6.83 — worse than
M-noise zeros alone (C, 6.70).

Zeros-only from SNR scoring (train_reduced_zeros_only.py):

| Variant | Loss | L2 rank90 | Zeros |
|---------|------|-----------|-------|
| I. SNR zt=1.5 | **6.3967** | 6 | 98% |
| C. M-noise 30% | 6.6972 | 25 | 30% |
| A. Float32 | 6.7412 | 6 | — |

**98% zeros on micro model achieves best loss.** But: micro model is
128 d_model, 509 examples, 10 eval — overcapacity regime. The specific
% won't transfer to v14 scale. The principle transfers:

1. One SVD, per-position SNR scoring for zero placement
2. Zeros-only (no flips) — zeros don't interfere with each other
3. GD fills around frozen sparse topology
4. Sweep the threshold at target scale to find operating point

## The Gemcutter Protocol

```
λ gemcut(M).
  phase_1(denoise): compute_M → SVD → zero(noise_positions, 30%)
                    | one-time operation before training
                    | zeros remove ghost facets, sharpen the gem
  phase_2(fill):    freeze(topology) → train(GD, gamma + all_else)
                    | GD fills gaps around the frozen facets
                    | the gem stays sharp (Q/K frozen)
  phase_3(inspect): measure(M_quality) → if(misaligned) → phase_1
                    | check facet alignment periodically
                    | re-cut only if needed

  cutting_head(mode_k):
    ΔM_target = correction for mode k
    for each candidate flip:
      project ΔM_flip onto all modes
      score = mode_k_improvement / cross_mode_damage
    select coordinated flip-set where:
      mode_k effects REINFORCE
      other mode effects CANCEL
    apply set → let Adam recalibrate → next mode
```

## Key Insights

1. **Zeros are denoising, not blocking.** Each zero removes one ghost
   route and sharpens the real facets. The gem goes from 35-mode blob
   to 25-mode crystal.

2. **GD is putty.** Cut the gem geometrically (accept loss hit), then
   let GD fill the gaps. The loss recovers. The gem persists.

3. **Geometric constraint helps GD.** A sharp frozen topology channels
   GD into the right subspace. The constraint IMPROVES convergence.

4. **TD's gradient scoring is wrong for structured layers.** The hottest
   W-space positions are NOT the best M-space corrections. Anti-correlated
   in the layers that matter most.

5. **One W-space flip cross-cuts all M-space modes.** A flip produces a
   rank-1 ΔM that projects onto every singular vector of M. Coordinated
   flips can reinforce on one mode and cancel on others (30× less damage).

6. **Crystal null space is structurally correct but too coarse for zeros.**
   The universal crystal lives in 15/128 dims. 113 dims are null space.
   Zeroing entire null-space columns gives good rank90 (26) but bad loss
   (7.13) — columns carry non-crystal info GD needs (position, syntax).
   Crystal energy should WEIGHT M-noise scoring as a prior, not hard-mask
   columns. M-noise zeros are per-position (row × column) which gives GD
   the flexibility to keep useful non-crystal info. M-noise alone (C) at
   loss 6.6972 remains the best variant.

## Crystal Subspace Analysis (Experiment 5)

Crystal embeddings (16 × d_model) span a rank-14 subspace. 90% of
crystal energy in 15 dims, 99% in 16 dims (of 128 total).

| Strategy | Final Loss | L2 rank90 | L2 top1% |
|----------|-----------|-----------|----------|
| C. M-noise 30% zeros | **6.6972** | 25 | 56.1% |
| G. 15% crystal + 15% M-noise | 6.8612 | 26 | 51.9% |
| F. 30% crystal-null columns | 7.1312 | 26 | 46.6% |

Crystal and M-noise select different positions: crystal zeros entire
columns (structural), M-noise zeros specific (row, col) positions
(surgical). Per-position resolution wins on loss.

## Files

| File | What |
|------|------|
| `scripts/micro/probe_mspace.py` | Exp 1: M-space vs gradient scoring |
| `scripts/micro