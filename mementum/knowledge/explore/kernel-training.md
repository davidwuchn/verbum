---
title: "Kernel Training — Training Through the Composed Plate"
status: active
category: training
tags: [kernel, composed-plate, gradient, training, optimization, TD]
related: [structured-training.md, ../holographic-error-correction.md, ../v14-architecture.md]
depends-on: [structured-training.md, ../extraction-methodology.md]
---

# Kernel Training — Training Through the Composed Plate

> Session 155. The composed plate (data-fitted linear transform
> embed→pre-head) captures 97% of the gradient direction. Training
> through it replaces 238 serial ternary matmuls with 1 matmul.
> Measured 4.4× speedup. But the output_proj bottleneck and
> gradient-subspace orthogonality constrain the design.

## What Was Proved

### Composed plate gradient accuracy

Gradient cosine = 0.9698 between:
- Full model: 238 ternary matmuls, 11 serial passes, all strides
- Composed plate: 1 dense matmul (1280×1280, least-squares fit)

| Metric | Value |
|--------|-------|
| Gradient cosine | 0.9698 (14° angular error) |
| Gradient magnitude ratio | 1.095 |
| CE difference | 0.08 nats |
| Logit cosine similarity | 0.716 |
| Top-1 agreement | 80.6% |
| ∂L/∂T rank | 151 |
| Composed plate rank90 | 1 (undertrained model) |

The composed plate is fit via least-squares:
```
T^T = lstsq(X_embed, X_out)
```
where X_embed = post-embed residuals, X_out = pre-head residuals.

### Training speedup

| Step type | Time | Matmuls |
|-----------|------|---------|
| Full model | 26.0s | 238 forward + 238 backward |
| Kernel (CE) | 6.0s | 1 forward + output_proj + backward |
| Measured speedup | 4.4× | |

Bottleneck is output_proj (1280→248,320 = 318M ops), NOT the
composed plate (1280×1280 = 1.6M ops). The stride stack (238
matmuls = 20s) is eliminated; the shared cost (embed + output_proj
+ CE = 6s) remains.

### Gradient projection failure

∂L/∂T projected into T's top-k SVD subspace:

| k | cos(G_projected, G) | T energy in top-k |
|---|---------------------|-------------------|
| 1 | 0.009 | 98.0% |
| 27 | 0.061 | 100% |
| 100 | 0.121 | 100% |
| 200 | 0.177 | 100% |

The gradient is orthogonal to T's subspace. The model (rank-1,
undertrained) needs to EXPAND, not refine. The gradient's energy
is in the directions where T is currently zero.

Cannot train in reduced dimensions for undertrained models.
May work for well-trained models — untested.

## Architecture

```
KERNEL STEP (fast):
  tokens → embed → T @ x_embed → output_norm → output_proj → CE → ∂L/∂(params)
  Cost: ~6s (dominated by output_proj)

FULL STEP (slow):
  tokens → embed → [stride stack: 238 matmuls] → output_norm → output_proj → CE
  → backward → Adam → TD → refit T
  Cost: ~26s

HYBRID LOOP (train_kernel.py):
  K kernel steps + 1 full step + refit T
  Effective: K×6s + 26s + 7s per (K+1) steps
  At K=10: ~9.2s/step effective (2.8× vs all-full)
```

## Key Insight: Camera IS Projector

Training is 77% forward pass. The backward pass is only 11%
(ternary base weights are frozen, only continuous params get
gradients). All five structured training optimizations from
session 154 target the 11% backward slice. The real win is
making the FORWARD pass cheaper — and that's the same problem
as inference optimization.

The composed plate does this: replace the stride stack with
one precomputed matmul. The gradient through this matmul is
97% correct. The bottleneck shifts to the output projection.

## Open Questions

1. **Output_proj factorization.** If hidden state is rank-27,
   output_proj effective rank ≤ 27. Factorize 1280→27→248K?
   Would eliminate the bottleneck AND be structurally correct.

2. **Gradient-subspace alignment on trained models.** Test on
   v14-td step 2000 (rank-27). If gradient aligns with T's
   subspace → 27D kernel training is viable for refinement.

3. **Flip scoring through composed plate.** ΔT from flip at
   position (i,j) in layer k = rank-1 update via prefix/suffix
   sandwich. Score = ⟨∂L/∂T, ΔT⟩. Needs prefix/suffix products
   for the stride-stack architecture — complex but possible.

4. **Incremental T updates.** After TD flips, can T be updated
   by rank-1 additions instead of full refit? Would eliminate
   the 7s refit cost.

5. **Phase-dependent training.** Use gradient-subspace alignment
   as a phase detector: orthogonal → explore (full 1280D),
   aligned → exploit (reduced dims). Automatic curriculum.

## Scripts

- `scripts/explore/probe_kernel_training.py` — validation probe
- `scripts/v14/train_kernel.py` — hybrid kernel/full training loop
- Results: `results/kernel-training-probe/`
