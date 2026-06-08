---
title: "Direct Delta Correction — Compute the Answer via Adjunction Structure"
status: active
category: compression
tags: [direct-delta, adjunction, rank-1, svd, error-correction, parametric-surface, calibration-aware]
related:
  - sign-correction-topology.md
  - score-matching-compression.md
  - residual-covariance-rank.md
  - explore/categorical-geometry-probes.md
  - mathematical-convergences.md
  - standing-wave-magnitudes.md
depends-on:
  - score-matching-compression.md
  - explore/categorical-geometry-probes.md
created: session 200
---

# Direct Delta Correction

> Session 200. After four sign correction algorithms failed catastrophically,
> two insights converged: (1) the teacher delta is directly computable — no
> training needed, (2) the adjunction finding from session 140 says the
> encode→decode transformation is rank-1. Together: the optimal correction
> is an analytical SVD, and it might need only rank 1-2.

## The Core Insight

> "If everything is being calculated, why can we not also calculate the
> delta from the teacher?"

We have the teacher model. We have the sieved student. At every layer,
for every projection, the weight residual is known:

```
W_delta = W_teacher - W_sieve
```

For sieved layers: W_delta is W at masked-out positions, zero at kept
positions (50% sparse). For L0 SVD: W_delta is the rank-750 approximation
error.

The optimal rank-k additive correction `A @ B ≈ W_delta` is the truncated
SVD. No training loop. No loss function. No optimizer. No hyperparameters
beyond rank.

## Calibration-Aware SVD

Naive SVD minimizes `||A@B - W_delta||²_F` (Frobenius). But not all input
directions are equally likely. The calibration-aware version weights by the
actual input distribution:

```
Minimize: E_x[||A@B@x - W_delta@x||²]
        = ||(A@B - W_delta) @ H^½||²_F

where H = E[x@x.T] = input covariance (from calibration data)

Solution:
  1. Whiten: W_whitened = W_delta @ H^½
  2. SVD(W_whitened) → truncate to rank k
  3. Unwhiten B: B = B_whitened @ H^{-½}
```

This gives the rank-k correction that is optimal for the actual input
distribution, not uniform over all directions.

## Sequential Cascade Awareness

Layer-by-layer, correct upstream before computing downstream:

```
For l = 0, 1, ..., 34:
  1. Run calibration data through model → collect actual inputs at layer l
     (these reflect upstream corrections already applied)
  2. Compute H_l = input covariance at this layer
  3. Compute W_delta_l for each projection (gate/up/down)
  4. Calibration-aware SVD → rank-k correction A_l, B_l
  5. Install correction at layer l
  6. Next layer sees corrected cascade
```

This is the GPTQ approach: each layer's correction is optimal for its
actual inputs, accounting for how upstream corrections changed the cascade.

## Why This Should Work Better Than Training

| Property | SM Loss (v3b) | Direct Delta |
|----------|--------------|-------------|
| Gradient dilution | Yes (29 Jacobians) | None (no backprop) |
| Compensating errors | Possible (CE creates them) | Impossible (per-layer independent) |
| Hyperparameter sensitivity | α, lr, steps, batch_size | rank only |
| Training instability | Diverges after step 150+ | No training |
| Cascade awareness | Implicit (through SM loss) | Explicit (sequential) |
| Optimality guarantee | Local minimum of loss | Global optimum at given rank |
| Speed | ~600s for 200 steps | ~minutes (SVD per layer) |

## The Adjunction Connection

### Session 140 Finding (Qwen3-32B)

The cross-zone mapping (encode L2 → decode L56) has:
```
σ₁/σ₂ = 128:1  (rank-1 dominated)
R² = 1.000     (for ALL zone pairs)
```

The Jacobian of the encode→decode transformation has **constant rank 1**
everywhere on the manifold. This is the defining property of a **regular
parametric surface** — specifically, a 1D curve embedded in 4096D space.

### Session 185 Finding (Qwen3-8B)

During ORTHO (L7-22), the residual stream has **effective rank = 1**:
```
Top eigenvalue: ~710,000
Second eigenvalue: ~100-170
Ratio: 4000-8800×
V overlap with residual: 0% (computation in null space)
```

16 consecutive layers of computation happen in the 4095-dimensional null
space of a rank-1 carrier wave. The residual is 1D; the computation is
invisible.

### The Implication for Error Correction

If the transformation is rank-1:
1. The entire computation lives on a **1D curve** through activation space
2. The sieve pushes representations off this curve
3. Error correction = **project back onto the curve**
4. The projection is along the dominant singular vector = **rank-1 correction**

**Prediction:** Direct delta correction at rank 1-2 should be nearly
optimal. The rank sweep [2, 4, 8, 16, 32] will test this. If rank-2
matches rank-32, the adjunction structure IS the error correcting code.

## The Tiles and Grout Metaphor

Topology (signs, mask, crystal) = tiles in a mosaic.
Gradients (LoRA, magnitudes) = grout filling the gaps between tiles.

```
When you move a tile (flip a sign):
  → all surrounding grout is wrong (trained for different gaps)
  → new gaps the grout doesn't fit
  → cascade: every downstream tile's grout is also wrong

Why sign correction + LoRA fails:
  Phase 1 (sign flips) → creates new gaps
  Phase 2 (LoRA) → trains grout from scratch
  But gaps too numerous, grout capacity (rank-4) too thin
```

MoE explicitly separates tiles from grout: router = topology, experts =
computation. Dense models entangle them. The crystal sieve tries to
separate what was never separate.

Direct delta correction avoids this entirely: instead of changing tiles
and refitting grout, compute the exact grout needed for the existing
tiles. No tile movement. No refit. Analytical solution.

## Connection to MoE Literature

Three principles from MoE training dynamics (session 200 research):

1. **Decouple routing from expert training.** (SEAS-GMoE, Grouter)
   → Direct delta: routing (signs) is frozen, correction (SVD) is computed
   independently. Perfect decoupling.

2. **Use teacher to supervise routing.** (TGR-MoE)
   → Direct delta: teacher's weights ARE the target. The SVD computes
   exactly the deviation from teacher.

3. **Stabilize routing FIRST, then train experts.** (Grouter)
   → Direct delta: routing is never changed. Experts (corrections) are
   computed analytically. No stability concern.

## Connection to TSP (arXiv:2606.03489)

TSP identifies "risk nodes" (critical decision points) and trains the model
to prefer the "golden path" over self-generated alternatives. Maps to:

- Risk nodes = layers where sieve diverges from teacher
- Golden path = teacher's residual trajectory
- Self-play path = student's trajectory

If direct delta works, TSP-style contrastive loss could refine it further
at the specific layers where the analytic correction is weakest. The
direct delta provides the initial correction; TSP provides the polish.

## Why All Sign Correction Failed (Summary)

Four approaches, same failure mode. The tiles-and-grout analysis explains
all of them:

| Approach | What it did | Why it failed |
|----------|------------|---------------|
| TD (gradient) | Tried to move tiles via backprop | Gradient too diluted to reach tiles through 29 layers of grout |
| TD v4c (per-tensor clip) | Successfully moved tiles | Grout around moved tiles now wrong; cascade destroys pattern |
| Latent diffusion | Moved tiles in eigenspace | Eigenspace ≠ crystal space; correlated tile moves catastrophic |
| Crystal ECC | Moved tiles with health gate | Health gate measures wrong space; 49.3% adversarial signal |
| Teacher-guided routing | Added correction to routing | 182M params, diverges; can't fix routing + cascade simultaneously |

All five tried to change the tiles. Direct delta doesn't change tiles —
it computes the exact grout for the existing tile arrangement.

## Experimental Artifacts

| Experiment | Script | Status |
|-----------|--------|--------|
| Direct delta (rank sweep) | `scripts/experiments/direct_delta_correction.py` | Running (tmux main:1) |
| Teacher-guided routing | `scripts/experiments/teacher_guided_routing.py` | ❌ Failed (24.55 PPL) |
| Crystal ECC | `scripts/experiments/crystal_ecc_sign_correction.py` | ❌ Failed (28M× PPL) |
| Latent diffusion | `scripts/experiments/latent_diffusion_signs.py` | ❌ Failed (2717× PPL) |
| Quasicrystal diagnostic | `scripts/experiments/quasicrystal_diagnostic.py` | ✅ Strong form denied |

## Open Questions

1. **What rank does the correction saturate at?** If rank 1-2 ≈ rank 32,
   the adjunction structure is confirmed as the error correcting code.

2. **Does the rank-1 adjunction finding hold for Qwen3-8B?** Session 140
   measured Qwen3-32B. Need to verify on 8B.

3. **Can direct delta + TSP contrastive beat either alone?** Direct delta
   for the analytical correction, TSP for the residual that SVD can't
   capture (e.g., nonlinear effects in the cascade).

4. **What is the compression ratio of direct delta?** At rank-k, each
   projection stores A (out_f × k) + B (k × in_f). At rank-4:
   (12288 × 4 + 4 × 4096) × 2 bytes × 3 projections × 29 layers ≈ 28MB.
   Is this competitive with LoRA at the same rank?

5. **Does calibration-aware SVD significantly beat naive SVD?** The
   experiment runs both. If calibration doesn't help, the correction is
   input-independent (a property of the weight delta alone, not the data).
