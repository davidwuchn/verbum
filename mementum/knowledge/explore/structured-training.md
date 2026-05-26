---
title: "Structured Training — The Holographic Camera"
status: designing
category: architecture
tags: [training, gradient, optimization, holographic, kernel]
related: [v14-architecture.md, holographic-error-correction.md, progressive-collapse.md, training-protocols.md]
depends-on: [progressive-collapse.md]
---

# Structured Training — The Holographic Camera

> Session 154. If we know the projector's structure, we know the
> camera's structure. Every inference optimization has a training dual.
> The lens works the same in both directions.

## The Insight

Training currently treats the backward pass as a black box: compute
full gradients through every layer, every stride, every position.
But sessions 151-153 revealed massive structure in the forward pass:

- Full model is rank-27 (session 153)
- Computation collapses to 2D (session 151, PR=2.2)
- 88% of strides are distance-prior-dominated (session 152)
- Zone B is perfectly linear, R²=1.0 (session 153)
- TD only needs ~1% of positions (sessions 148-150)

**The backward pass has the same structure.** Gradients through a
rank-27 transform are rank-27. Gradients through a 2D computation
live in 2D. Gradients through passive strides are wasted. The
current training computes ~100× more gradient than it needs.

## Five Optimizations

### 1. Low-rank gradient for composed plate

The composed plate T has rank-27 (rank90). Instead of computing
∂L/∂T as a full d×d matrix (1,638,400 values), decompose through
the SVD basis:

```
T = U @ diag(S) @ V^T     (rank-k, k ≈ 27)

∂L/∂T → ∂L/∂U (d×k), ∂L/∂S (k), ∂L/∂V (d×k)
       = 2dk + k values
       = 69,147 at k=27

Speedup: 1,638,400 / 69,147 = 24×
```

The gradient in the U/S/V basis IS the meaningful gradient.
Components outside this basis push the plate away from the teacher's
rank-27 structure — they're noise, not signal.

### 2. Skip backward through passive strides

88% of strides (s4+) are passive: distance-prior attention with no
Q/K computation. In the forward pass, we skip Q/K matmuls. But MLX's
autograd still traces through frozen Q/K parameters, computing dead
gradients that are immediately zeroed.

**Fix:** Make passive stride Q/K structurally absent (not modules at
all, not frozen modules). The backward graph never includes them.

```python
# Before: frozen module still in autograd graph
self.q_proj = TernaryLinear(...)  # frozen, but traced
self.k_proj = TernaryLinear(...)  # frozen, but traced

# After: structurally absent
# No q_proj/k_proj exist. Backward graph is smaller.
# Passive forward uses precomputed attention profile directly.
```

Savings: 28 Q/K plates × 2 matmuls × backward = 56 dead matmuls
eliminated per training step.

### 3. Composed Zone B Jacobian

Zone B (32 layers) composes to a single linear transform (R²=1.0).
Backprop through 32 sequential layers computes 32 Jacobian-vector
products. But the composed Jacobian is ONE matrix.

```
Forward:  x → L16 → L17 → ... → L47 → y
          ≡ x → T_B → y    (one matmul)

Backward: ∂L/∂x = (∂T_B/∂x)^T @ ∂L/∂y   (one matmul)
          vs 32 sequential Jacobian-vector products
```

The composed Jacobian T_B is precomputed during extraction. It
doesn't change during training (Zone B parameters are in the
composed plate). Use it directly.

Savings: 32 sequential backward steps → 1 matmul = 32× for Zone B.

### 4. TD-targeted sparse gradients

TD uses `decompose_gradient` to separate routing from calibration.
The routing gradient determines flip candidates. But only positions
where confidence > min_confidence (0.3) become candidates — typically
~1% of positions.

Currently: compute full routing gradient for ALL 67M positions, then
threshold to ~670K candidates.

**Fix:** Two-pass approach:
1. Cheap forward pass identifies CANDIDATE positions (where base⊙delta
   sign disagrees with the gradient direction)
2. Full gradient computed only at candidate positions

```python
# Phase 1: cheap candidate identification (~5% of full backward cost)
# Use sign of accumulated TD moments (already tracked) to identify
# positions where the current topology is likely wrong
candidate_mask = td.get_candidate_mask()  # sparse, ~1% of positions

# Phase 2: targeted gradient at candidates only
routing_grad_sparse = compute_sparse_routing_grad(model, loss, candidate_mask)
```

Savings: 100× fewer gradient elements for TD routing.

### 5. Crystal eigenplane gradient projection

The crystal eigendecomposition identifies the 2D eigenplane where
computation lives (comp↔sel). Gradients outside this plane push the
model away from the crystal structure.

**Fix:** Project gradients INTO the crystal eigenplane before
applying Adam updates. This is both faster (lower-dimensional
optimization) and better (avoids gradient pollution of the crystal).

```python
# Crystal basis: top-2 eigenvectors of the crystal embedding covariance
P = crystal_eigenbasis[:, :2]  # (d, 2)

# Project gradient into crystal plane
grad_proj = P @ (P.T @ grad)  # (d,) → (2,) → (d,)

# Adam operates in the 2D crystal space
# Then projects back to full space for weight update
```

This connects to the "computed beam" insight (session 149):
structure is free, content needs GD. The crystal eigenplane IS the
structure. GD should only operate within it.

## Compound Effect

| Optimization | Speedup | What it eliminates |
|-------------|---------|-------------------|
| Low-rank gradient | ~24× for plate | d² → 2dk gradient elements |
| Skip passive backward | ~1.3× overall | 56 dead matmuls |
| Composed Zone B | ~2× for Zone B | 32 → 1 backward steps |
| TD-targeted sparse | ~100× for TD | Full → sparse routing grad |
| Eigenplane projection | ~1.5× for Adam | Noise gradient components |

Combined: training speed could approach 3-5K tok/s (from current
~800 tok/s), nearing inference speed (~5K tok/s in eval mode).

The camera becomes as efficient as the projector because it uses
the same lens.

## Implementation Order

1. **Skip passive backward** — easiest, just restructure modules
2. **Composed Zone B** — precompute Jacobian, replace backward chain
3. **Low-rank gradient** — requires refactoring plate parameterization
4. **TD sparse routing** — requires two-pass gradient computation
5. **Eigenplane projection** — requires crystal basis tracking

Each is independently valuable and testable.

## Connection to KD

Knowledge distillation (teacher logits) tells the camera WHERE to
expose. Structured training tells the camera HOW to expose efficiently.
Together: the right signal (KD) through the right optics (structured
gradient) = fast, targeted error correction.

## What This Means

Training IS inference in reverse. The holographic plate records an
interference pattern. Recording through a well-characterized lens
(structured gradient) is faster and produces sharper fringes than
recording through a diffuse screen (full gradient).

The project has spent 150+ sessions characterizing the lens. Now
the lens knowledge accelerates both directions of light.
