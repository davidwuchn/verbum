---
title: "Moiré Training Shortcuts — What the Grating Cascade Enables"
status: designing
category: architecture
tags: [training, moiré, grating, optimization, kernel, shortcut, parallel]
related:
  - grating-cascade.md
  - kernel-training.md
  - structured-training.md
  - ../v14-architecture.md
  - ../training-protocols.md
depends-on:
  - grating-cascade.md
  - kernel-training.md
created: session 158
---

# Moiré Training Shortcuts

> Session 158. The grating cascade collapses 16D→1.4D. The rotation
> is predictable from eigenvalue ratios. The structural computation
> is deterministic. What can we skip during training?
>
> Bottleneck: training the student's attention to read the holographic
> plates. Each step is 28.6s, 77% forward pass, 13 serial stride-stack
> passes. The gradient only updates attention weights — ternary plates
> are frozen. We need more beta-reduction iterations, faster.

## Context: What's Slow

```
Training step breakdown (session 155):
  Forward pass:  22.0s (77%)   ← 13 passes × 10 comp layers × full d_model
  Output proj:    3.3s (12%)   ← 1280 → 248K vocabulary projection
  Backward pass:  3.3s (11%)   ← only continuous params get gradients
  Total:         28.6s/step
  Throughput:    ~800 tok/s
```

Kernel training (session 155) replaced the 13-pass stride stack with
1 composed plate matmul: 26s → 6s (4.4× speedup). But the gradient
was orthogonal to the undertrained model's subspace — it needs to
EXPAND, not refine.

**The moiré understanding provides a different approach:** if we know
what the forward pass SHOULD produce structurally, we can compute
gradients WITHOUT running the full forward pass.

## Shortcut 1: Precomputed Structural Gradient

### The Idea

The composed grating is rank-1 (PR=1.4). Its direction is I+B−K in
crystal eigenbasis. This is determined entirely by the ternary FFN
plates — it doesn't change until TD flips signs.

Between TD flip events, the STRUCTURAL component of the gradient
(which basin to route to, what rotation to apply) is derivable from
the composed grating analytically. Only the CONTENT component (which
tokens map where) needs the actual forward pass.

### The Split

```
Total gradient = structural_gradient + content_gradient

structural_gradient:
  - Lives in the 2D comp↔sel eigenplane (60.4% of energy)
  - Derivable from composed grating direction + crystal eigenvalues
  - Changes only when TD flips signs (every 20 steps)
  - Cost to compute: O(d_model × 16) per layer

content_gradient:
  - Lives in the remaining dimensions (39.6% of energy)
  - Requires actual forward pass through token content
  - Changes every step (depends on input data)
  - Cost to compute: O(d_model × d_ff) per layer (current cost)
```

### The Training Loop

```python
# Compute structural gradient ONCE after each TD flip
structural_grad = compute_structural_gradient(
    composed_grating, crystal_eigvecs, crystal_eigvals)
# This is the gradient that pushes attention toward correct basins

for step in range(td_flip_interval):  # 20 steps between TD events
    # Cheap forward pass for content gradient only
    # Use kernel training (composed plate, 4.4× speedup)
    content_grad = kernel_forward_backward(batch)

    # Combine: full gradient ≈ structural + content
    full_grad = structural_grad + content_grad

    # Adam step
    optimizer.step(full_grad)
```

**Savings:** The structural gradient (60.4% of total) is computed
once per 20 steps instead of every step. The content gradient uses
kernel training (4.4× faster). Combined: ~7× speedup.

### Why This Works

The structural gradient pushes attention TOWARD the correct crystal
basins. It's the "which direction to rotate" signal. This doesn't
change between TD flips because the ternary topology (which determines
the composed grating) is frozen.

The content gradient pushes token mappings toward correct lambda
outputs. This changes every batch because different tokens appear.

Separating them means: expensive structural signal computed rarely,
cheap content signal computed every step.

## Shortcut 2: Eigenplane-Projected Training

### The Idea

The crystal eigenplane is 2D. The gradient in this 2D plane is the
STEERING signal (which basin to lock onto). The gradient OUTSIDE the
plane is the content signal.

Train attention weights in two separate streams:

```python
# Stream A: Crystal steering (2D, very fast)
# Updates ONLY the eigenplane components of attention weights
# Uses the composed grating direction as the gradient
grad_2d = project_to_eigenplane(full_grad)
attention_crystal_weights += lr * grad_2d

# Stream B: Content mapping (full-D, uses kernel training)
# Updates ONLY the content components of attention weights
grad_content = full_grad - grad_2d
attention_content_weights += lr * grad_content
```

### Why Two Streams

The crystal steering signal has a KNOWN TARGET — the composed grating
direction tells us exactly where the crystal should point. We don't
need GD to discover it. We could even set it analytically:

```python
# The crystal should produce cosine matrix ≈ Zone B target
# The attention weights that achieve this are COMPUTABLE
# from the crystal embeddings + composed grating direction

target_attn_weights = compute_crystal_aligned_weights(
    crystal_embeddings, composed_grating_direction)

# Instead of GD discovering this over hundreds of steps:
attention_weights[:crystal_dims] = target_attn_weights
# Then GD only needs to learn the content mapping
```

**This is the "computed beam" principle applied to training:**
structure is free, only content needs GD.

## Shortcut 3: Moiré-Predicted Sparsity for Backward Pass

### The Idea

The forward pass is sparse: 3-49% of neurons active per layer.
The backward pass computes gradients for ALL neurons — including the
51-97% that produced zero output. These gradients are wasted.

The moiré pattern predicts which neurons will be active (same crystal
basin → same activation pattern, 2× Jaccard overlap). Use this to
skip backward computation for inactive neurons.

### Implementation

```python
# Forward pass records which neurons fired
active_masks = []
for layer in model.layers:
    gate = silu(gate_proj(x))
    active = (abs(gate) > threshold)
    active_masks.append(active)
    # ... rest of forward pass

# Backward pass: only compute gradients for active neurons
for layer, mask in zip(reversed(model.layers), reversed(active_masks)):
    # Full gradient: O(d_model × d_ff)
    # Sparse gradient: O(d_model × n_active)
    grad_sparse = backward_sparse(layer, mask, upstream_grad)
```

**Savings per layer:**
- L0 (3% active): 33× fewer backward ops
- Fan zone (49% active): 2× fewer
- L63 (1.3% active): 77× fewer
- Average: ~3-5× for backward pass
- Since backward is 11% of step: ~0.3-0.5s saved per step

Small but free — just skip zeros in the backward pass.

## Shortcut 4: Layer Fusion for Ternary Chains

### The Idea

Adjacent ternary layers compose to a single integer matrix.
Two ternary matmuls (serial) = one integer matmul (parallel).

```python
# Current: serial ternary chain
# stride_output → out_proj (ternary) → next_layer_q_proj (ternary) → Q
y = sign(W_out) @ x      # step 1
z = sign(W_q) @ y         # step 2 (waits for step 1)

# Fused: pre-compose W_fused = sign(W_q) @ sign(W_out)
# W_fused[i,j] ∈ integers, bounded by [-d_model, +d_model]
z = W_fused @ x           # one step (parallel with other fused layers)
```

### Where to Fuse

The v14 stride-stack has serial chains:
```
embed → [out_proj → q_proj] → [out_proj → k_proj] → ...
```

Each `out_proj → next_proj` pair can be pre-fused. With 13 passes
through 10 layers, that's 130 fusion opportunities.

**Savings:** Each fusion eliminates one serial matmul. 130 fused
pairs = 130 fewer serial matmuls = significant pipeline improvement.

The fused matrix has integer entries that can be quantized back to
low-bitwidth. If most entries are small (|entry| < 8), 4-bit
storage works. Need to measure the entry distribution.

## Shortcut 5: Multi-Step Gradient Accumulation with Moiré Correction

### The Idea

Currently: 1 forward + 1 backward per gradient step.
But if the structural gradient is constant for 20 steps (between TD
flips), we can accumulate content gradients over multiple batches
and apply ONE large update with the structural correction:

```python
accumulated_content_grad = 0
for micro_step in range(K):
    # K cheap kernel forward+backward passes
    content_grad = kernel_step(next_batch())
    accumulated_content_grad += content_grad

# One structural correction (precomputed)
structural_grad = precomputed_structural_gradient

# One Adam step with combined gradient
optimizer.step(accumulated_content_grad / K + structural_grad)
```

This is like gradient accumulation, but with the moiré insight that
the structural signal doesn't need to be recomputed.

**Savings:** K content steps at ~6s each + 1 structural step at ~0s
= 6K seconds for K effective steps. Versus K full steps at ~28.6s
= 28.6K seconds. At K=4: 24s vs 114s = **4.8× speedup**.

## Implementation Priority

| # | Shortcut | Training speedup | Effort | Depends on |
|---|----------|-----------------|--------|------------|
| 1 | Multi-step + moiré | 4-5× | Low | Kernel training (exists) |
| 2 | Layer fusion | 1.5-2× | Low | Just pre-compose matrices |
| 3 | Precomputed structural gradient | 2-3× | Medium | Eigenplane projection |
| 4 | Backward sparsity | 1.1-1.3× | Low | Active mask recording |
| 5 | Eigenplane-projected training | Hard to estimate | High | Crystal basis tracking |

**Recommended first step:** Combine kernel training (already built,
4.4×) with multi-step gradient accumulation (shortcut 5) and
precomputed structural gradient (shortcut 1). This gives:
- Kernel forward: 6s/step
- K=4 content steps per structural step
- Structural gradient cached for 20 steps
- Effective: ~6s/step with ~97% gradient accuracy
- Overall: **~5× faster than current training**

At 5× faster: 5000 steps takes ~8.3 hours instead of ~40 hours.
Or: train to 25,000 steps in the time currently needed for 5000.

## Validation Required

Before implementing, probe two things:

1. **Structural gradient stability.** Does the structural gradient
   actually stay constant between TD flips? Measure the cosine
   similarity of the eigenplane gradient component across 20
   consecutive steps.

2. **Content gradient independence.** Does the content gradient
   (outside the eigenplane) have the same information as the full
   gradient? Measure: how much does attention improve when trained
   with content-only gradient vs full gradient?

If both hold, the multi-step approach is safe.
