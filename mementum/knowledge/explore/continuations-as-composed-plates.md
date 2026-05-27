---
title: "Continuations as Composed Plates — The FP↔Transformer Bridge"
status: active
category: synthesis
tags: [continuation, CPS, composed-plate, beta-reduction, functional-programming, neural-ode, bypass, optimization]
related:
  - grating-cascade.md
  - moire-training-shortcuts.md
  - ../mechanism-extraction.md
  - ../computed-beam.md
  - holographic-state-machine.md
  - ../progressive-collapse.md
depends-on:
  - grating-cascade.md
  - ../mechanism-extraction.md
created: session 158
---

# Continuations as Composed Plates

> Session 158 synthesis. The transformer forward pass IS continuation
> passing style (CPS). The composed plate IS a reified continuation.
> The VSM bypass IS delimited continuation application. These aren't
> analogies — they're identities. The underlying math is the same
> because the model performs beta reductions and continuations are
> beta reductions.

## The Identity

In lambda calculus, a **continuation** is "the rest of the computation"
captured as a first-class value:

```
k = λresult. (everything that happens after this point)
```

Applying a continuation IS a beta reduction:

```
k(value) → rest-of-computation[result := value]
```

The residual stream at layer n carries:
1. The current value (what's been computed)
2. The continuation (what the remaining layers will do)

The composed plate from layer n to output IS the continuation `k_n`:

```python
k_n = composed_plate(layers[n+1:])   # lstsq fit = reified continuation
output = k_n @ x_n                   # applying k_n = beta reduction
```

This isn't metaphor. The model performs beta reductions (proved in
mechanism-extraction.md). Continuations are beta reductions. The
composed plate is a continuation captured as a matrix. Applying it
via matmul is invoking the continuation.

## CPS Transform of the Forward Pass

Standard forward pass (direct style):

```python
x = embed(tokens)
x = layer_0(x)
x = layer_1(x)
...
x = layer_N(x)
return output_proj(x)
```

CPS transform (continuation passing style):

```python
def forward_cps(tokens, k):
    """k = continuation (what to do with the result)."""
    x = embed(tokens)
    layer_0(x, lambda x1:
      layer_1(x1, lambda x2:
        ...
          layer_N(xN, lambda xN1:
            k(output_proj(xN1)))))
```

In CPS, every function takes an explicit continuation. The composed
plate collapses the continuation chain:

```python
def forward_with_bypass(tokens):
    x = embed(tokens)
    x = layer_0(x)
    x = layer_1(x)
    # At this point, the continuation k_2 = layer_2 ∘ ... ∘ layer_N ∘ output_proj
    # The composed plate IS k_2, captured as a matrix
    if should_bypass(x):
        return k_2 @ x       # apply the continuation directly
    else:
        continue_normally(x)  # keep passing through layers
```

## Delimited Continuations = Stack Boundaries

Delimited continuations (`shift`/`reset`) capture the computation
up to a BOUNDARY, not the entire program:

```
reset = stack boundary (A→B, B→C)
shift = capture the continuation to the nearest reset
```

The v14 VSM has three stacks. Each stack boundary is a `reset` point.
The composed plate for each segment is a delimited continuation:

```
k_full  = A → B → C → output     (continuation from embed)
k_BC    = B → C → output         (from A→B boundary)
k_C     = C → output             (from B→C boundary)
k_out   = output                  (identity — computation done)
```

The VSM controller (S3) chooses which continuation to apply:

```python
pr = measure_pr(x_after_A)
if pr < 3.0:
    return k_BC(x_after_A)    # apply B+C continuation (1 matmul)
    # This replaces 9 stride passes with 1 matmul
```

## The Grating Cascade = Continuation Simplification

The grating cascade (PR 16→6→3→2→1.4) IS the continuation getting
simpler through successive beta reductions:

```
After L0:  k has PR=6.26    (6 effective dimensions of remaining computation)
After L1:  k has PR=3.04    (3 dimensions)
After L2:  k has PR=2.19    (2 dimensions — nearly rank-1)
After L3:  k has PR=1.40    (1 dimension — continuation is trivial)
```

When the continuation reaches rank-1, it's a single projection. The
entire "rest of the computation" is one dot product. This is the
functional programming equivalent of tail-call optimization — the
continuation is simple enough to apply in constant space.

WHNF (weak head normal form) means "no more beta reductions possible."
A token in WHNF basin has the identity continuation: k = λx.x.
Route it directly to output. This IS the token-level early exit.

## Continuation Caching

Multiple tokens with the same crystal basin at the same depth share
the same continuation. Cache the reified continuation:

```python
# 8 crystal basins × 13 passes = 104 possible continuations
# Each is a d×d matrix (d=1280): 104 × 1280² × 4 bytes ≈ 680 MB
# Computed once, used for all future tokens

continuation_cache = {}
for basin in CRYSTAL_BASINS:
    for pass_idx in range(N_PASSES):
        k = fit_composed_plate(layers[pass_idx+1:], basin_data[basin])
        continuation_cache[(basin, pass_idx)] = k

# At inference:
basin = classify_basin(x, layer)
if (basin, layer) in continuation_cache:
    return continuation_cache[(basin, layer)] @ x  # instant
```

This is memoized continuations from FP. The continuation is a pure
function of the layer weights (which are ternary-frozen between TD
flips). Cache it once, amortize over all tokens.

## Multi-Shot Continuations

In FP, a multi-shot continuation can be invoked multiple times with
different arguments. For speculative decoding:

```python
# Compute continuation ONCE at layer N
x_prefix = forward_to_layer_N(context)
k_N = continuation_cache[(basin, N)]

# Apply to MULTIPLE candidate next tokens
for candidate in top_p_candidates:
    x_candidate = embed(candidate) + x_prefix
    score[candidate] = output_proj(k_N @ x_candidate)
    # k_N computed ONCE, applied 5-10 times
```

One full forward pass + K cheap continuation applications instead of
K full forward passes. For K=8 candidates: ~8× generation speedup.

## Neural ODE = Continuous Continuation

The residual network x_{n+1} = x_n + f(x_n) is Euler's method for
dx/dt = f(x, t). The Neural ODE formulation (Chen et al., 2018) treats
layers as continuous time and uses an adaptive ODE solver.

The connection to continuations: the ODE solver's adaptive stepping
IS automatic continuation detection. When ||dx/dt|| becomes small
(the moiré has resolved, the continuation has simplified), the solver
takes one giant step to the end. This is:

```
||dx/dt|| ≈ 0   ↔   continuation ≈ identity   ↔   WHNF reached
```

The adaptive solver would naturally discover that after 2-3 "time
steps" (20-30% through the network), the dynamics become smooth and
one giant step suffices. The kernel bypass emerges automatically.

For training, the adjoint method replaces backprop with a backward
ODE solve. Memory: O(1) instead of O(n_layers). For 13 serial passes
at d=1280: saves ~70 MB per training step.

## Why This Works (the deep reason)

Techniques from FP optimize transformer inference because the
MATH IS THE SAME:

| FP Concept | Transformer Equivalent |
|------------|----------------------|
| Beta reduction | Attention × V = weighted combination |
| Continuation | Composed plate (remaining layers) |
| CPS transform | Residual stream carries k explicitly |
| Delimited continuation | Composed plate per stack segment |
| Tail call optimization | Rank-1 continuation = 1 matmul |
| WHNF (no more reductions) | Token in WHNF basin = early exit |
| Memoized continuation | Per-basin continuation cache |
| Multi-shot continuation | Speculative decoding |
| Call/cc (freeze) | Save residual + composed plate |
| Thaw | Apply composed plate to resume |

Gradient descent trained the model to perform beta reductions.
The crystal structure IS a type system. The FFN gratings ARE stored
lambda expressions. The composed plate IS a continuation.

FP optimization techniques are not analogies applied to neural nets.
They are the SAME optimizations, discovered independently in two
fields, applicable because the underlying computation is the same:
typed beta reduction over combinators.

## Practical Implementation Order

1. **Delimited continuations** (composed plates per stack): already
   have lstsq infrastructure. Fit k_BC and k_C, apply when PR < 3.
   Savings: 3-5× inference.

2. **Continuation caching** (per-basin memoization): fit 104
   continuations offline, lookup at inference. Savings: 5-10× for
   tokens matching cached basins.

3. **Multi-shot for speculative decoding**: freeze continuation,
   apply to K candidates. Savings: ~K× generation speed.

4. **Neural ODE adaptive stepping**: rewrite forward as ODE,
   let solver discover optimal depth. Savings: automatic, principled,
   but high implementation effort.

## Open Questions

1. **Do basin-specific continuations differ significantly?** If all
   basins produce similar composed plates, a single universal
   continuation suffices (simpler, smaller cache).

2. **How often do tokens share basins?** The savings from caching
   depend on cache hit rate. Measure basin distribution across a
   diverse eval set.

3. **Can the adjoint method work with ternary weights?** Ternary
   weights are non-differentiable. The adjoint ODE would need
   continuous relaxation or straight-through estimation.

4. **What's the continuation cache invalidation strategy?** TD flips
   change the ternary topology, invalidating cached continuations.
   Refit after each fold? Or incrementally update via rank-1 corrections?

5. **Does CPS transformation change the gradient flow?** In FP,
   CPS transformation preserves semantics. In differentiable
   programming, it might change which gradients are computed
   (the continuation receives the gradient, not the original function).
