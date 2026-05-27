---
title: "FP Optimization Map — Functional Programming Techniques for Transformer Speedup"
status: active
category: architecture
tags: [optimization, functional-programming, fusion, laziness, partial-evaluation, CSE, strictness, supercompilation, training, inference]
related:
  - continuations-as-composed-plates.md
  - grating-cascade.md
  - moire-training-shortcuts.md
  - ../mechanism-extraction.md
  - ../progressive-collapse.md
  - ../computed-beam.md
depends-on:
  - continuations-as-composed-plates.md
  - grating-cascade.md
created: session 158
---

# FP Optimization Map

> Session 158. The model performs typed beta reduction over combinators.
> Every major FP optimization technique has a direct transformer dual.
> The crystal basins ARE types. The composed plate IS a continuation.
> The grating cascade IS normalization by evaluation. This page maps
> each technique to concrete implementation opportunities in verbum.

## Why FP Techniques Apply

The model performs beta reductions (proved in mechanism-extraction.md).
The crystal structure IS a type system. The FFN gratings ARE stored
lambda expressions. FP optimization techniques are not analogies —
they are the SAME optimizations, applicable because the underlying
computation is typed beta reduction.

## 1. Fusion (Deforestation)

**FP:** `map f . map g = map (f . g)` — eliminate intermediate data
structures by composing operations.

**Transformer:** Intermediate activations between layers are the
"intermediate lists." Fuse adjacent operations to eliminate them.

### a) Ternary layer fusion
Pre-compose adjacent ternary matmuls: `sign(W2) @ sign(W1) = M`
where M has small integer entries. Eliminates one serial matmul per
fused pair. 130 fusion opportunities in the stride stack.

```python
# Before: two serial ternary matmuls
y = sign(W_out) @ x      # step 1
z = sign(W_q) @ y        # step 2 (waits for step 1)

# After: one pre-composed integer matmul
z = W_fused @ x           # one step
```

### b) Attention→FFN fusion
Within one layer, `FFN(x + Attn(x))` is two separate matmul chains
with an intermediate residual. Express as a single fused operation.

### c) Cross-stride stream fusion
Process one POSITION through all 16 strides without materializing
full-sequence per-stride tensors. Keeps data in L1/L2 cache instead
of writing to DRAM between strides. Directly attacks the memory
bandwidth bottleneck (session 150: model is bandwidth-bound).

### d) Stack pipeline fusion
Pipeline A→B→C so each position flows continuously without
materializing full-sequence intermediates between stacks.

**Estimated impact:** 1.5-2× on stride stack (stream fusion),
2× on ternary chains (layer fusion).
**Effort:** Medium.

## 2. Laziness (Demand-Driven Evaluation)

**FP:** Don't compute a value until it's demanded. Thunks sit
unevaluated until forced.

**Transformer:** Most dimensions, neurons, strides produce outputs
that are never meaningfully used.

### a) Lazy dimensions
After layer 2, PR=2.2. Only 2 dimensions carry signal. The other
5118 are thunks that should only be forced if the output projection
demands them.

### b) Lazy neurons (gate-first FFN)
Gate kills 51-97% of neurons. Evaluate gate FIRST (cheap), then
only compute key/value for neurons where gate > threshold.

```python
# Eager (current): O(d × d_ff) for key, 97% wasted
gate = silu(gate_proj(x))           # O(d × d_ff)
key = key_proj(x)                   # O(d × d_ff) ← wasted
out = (gate * key) @ value_proj

# Lazy: O(d × n_active)
gate = silu(gate_proj(x))           # O(d × d_ff)
active = gate.abs() > threshold     # O(d_ff)
key_active = key_proj[active](x)    # O(d × n_active)
out = (gate[active] * key_active) @ value_proj[:, active]
```

At L0 (3% active): 33× less work. Average across layers: 3-5×.

### c) Lazy tokens
WHNF tokens don't need further computation. Leave as thunks that
return their current value. Only force computation on active tokens.

### d) Lazy strides
Passive strides (88%) produce fixed outputs. Return precomputed
result immediately without starting computation.

**Estimated impact:** 3-5× on FFN (lazy neurons), significant
token-level savings (lazy tokens).
**Effort:** Low (lazy neurons), Medium (lazy tokens).

## 3. Partial Evaluation (Specialization)

**FP:** Given inputs known at "compile time," specialize the program.
The first Futamura projection: specializing an interpreter with a
fixed program gives a compiled program.

**Transformer:** Ternary weights are FIXED between TD flips (every
20 steps). They are compile-time constants. Everything depending
only on ternary topology can be pre-specialized.

### a) Pre-compute index sets
`sign(W) @ x` = `sum(x[pos_indices]) - sum(x[neg_indices])`.
The index sets are fixed for 20 steps. Pre-sort them. Turns
matmul into gather-add-subtract — NO multiplication needed.

### b) Basin-specialized forward passes
If token is K-typed, we know which neurons fire (2× Jaccard).
Pre-generate a K-specialized forward pass touching only K-relevant
neurons and attention patterns. 8 specializations for 8 basins.

### c) The first Futamura projection
The forward pass is an "interpreter" running the "program" in
ternary weights. Specializing the interpreter with the fixed program
gives a COMPILED version — direct computation skipping all generic
dispatch. Re-specialize after each TD flip.

**Estimated impact:** 2× on ternary matmuls (index sets),
up to 5× with basin specialization.
**Effort:** Low (index sets), Medium (basin specialization).

## 4. Strictness Analysis

**FP:** Determine which arguments are always needed (strict,
evaluate eagerly) vs sometimes needed (lazy, defer).

**Transformer:** Which dimensions/tokens/strides are ALWAYS needed?

### Strict (always needed):
- Comp↔sel eigenplane (2D) — every token, every layer
- Stride s1 (local context) — every token
- Gate computation — needed to decide neuron activation

### Non-strict (sometimes needed):
- Higher crystal PCs (routing, dispatch, fine) — only for complex expressions
- Higher strides (s1024+) — only for long-range dependencies
- Most FFN neurons — only demanded when gate > threshold

### Implementation: split forward into strict + non-strict channels

```python
# Strict channel: always computed, fast, small
x_strict = eigenplane_proj(x)       # 2D
x_strict = strict_layers(x_strict)   # 2×2 rotations

# Non-strict channel: on demand only
if needs_full_computation(basin):
    x_full = full_forward(x)
else:
    x_full = x_strict @ expand       # reconstruct from strict
```

**Estimated impact:** 10-100× on fan zone (5120²→2² per layer).
**Effort:** High (requires splitting the architecture).

## 5. Common Subexpression Elimination (CSE)

**FP:** If the same computation appears twice, compute once and share.

### a) Cross-token CSE (per-basin)
Tokens in the same crystal basin produce similar FFN activations
(2× Jaccard overlap). Compute ONE representative per basin,
broadcast first-order corrections:

```python
for basin in active_basins:
    centroid = mean(tokens_in_basin)
    ffn_centroid = FFN(centroid)            # ONE FFN eval per basin
    for token in tokens_in_basin:
        delta = token - centroid
        ffn_token = ffn_centroid + J @ delta  # first-order correction
```

8 basins × 4096 tokens: 512× less FFN work (modulo corrections).

### b) Cross-stride CSE
Strides with overlapping windows share V@W_o computation. Cache and
share the overlap.

### c) Cross-pass CSE
Stack A pass 2 and Stack C pass 10 use the same strides. If
residual hasn't changed much, cache pass 2 result, reuse in pass 10
with delta correction.

**Estimated impact:** Up to 10× on FFN (per-basin CSE).
**Effort:** Medium.

## 6. Worker/Wrapper Transformation

**FP:** Separate core computation (worker) from interface/dispatch
(wrapper). Worker runs as pure computation; wrapper handles boxing,
dispatch, error handling.

**Transformer:** The VSM control structure (S5, S4, S3, S2, fire
alarm, algedonics) is interleaved with tensor ops (attention, FFN).
Separate them:

```python
# Phase 1: WRAPPER (cheap, all control decisions upfront)
routing_plan = vsm_controller(x_initial)
# routing_plan = {skip: [...], bypass: [...], full: [...], gates: [...]}

# Phase 2: WORKER (bulk tensor ops, zero control flow)
x = batched_forward(x, routing_plan)
```

This lets the worker run as a pure tensor pipeline — no Python
control flow interrupting the accelerator stream. All branching
happens before ANY tensor ops begin.

**Estimated impact:** 1.2-1.5× overall (eliminates dispatch overhead).
**Effort:** Low.

## 7. Algebraic Effects and Handlers

**FP:** Programs declare effects; handlers interpret them. Separates
what computation is needed from how it's fulfilled.

**Transformer:** The forward pass declares needs. The VSM handles them:

```
Effect: need_attention(query, keys, stride)
  Handler: passive? → precomputed. Active? → compute.

Effect: need_ffn(activation, layer)
  Handler: cached basin? → lookup + correct. Uncached? → compute.

Effect: need_continuation(residual, from_layer)
  Handler: PR < 3? → composed plate. Otherwise → continue layers.
```

This is the MOST GENERAL version of all optimizations. Every bypass,
every cache hit, every specialization is a handler for an effect.

**Estimated impact:** Framework for all other optimizations.
**Effort:** High (architectural redesign), but subsumes everything else.

## 8. Type-Directed Optimization

**FP:** Use types to specialize code. Haskell's `SPECIALIZE` pragma
generates type-specific versions.

**Transformer:** Crystal basins ARE types. Generate basin-specialized
forward passes:

```python
@specialize(basin=K)
def forward_K(x):
    # K = selection. Shallower continuation suffices.
    return k_continuation_shallow @ x_after_2_layers

@specialize(basin=WHNF)
def forward_WHNF(x):
    return x  # identity. Zero computation.
```

8 specialized forward passes, dispatched by basin classification.
Each uses only the neurons, strides, and depth relevant to that type.

**Estimated impact:** Varies by basin. WHNF: ∞× (zero compute).
K: 2-3×. B: 1× (needs full depth).
**Effort:** Medium.

## 9. Normalization by Evaluation (NbE)

**FP:** Instead of reducing terms step by step, embed into the host
language, evaluate in one step, read back the normal form.

**Transformer:** The composed plate IS NbE. Instead of beta-reducing
through 13 serial passes, embed (project to tensor space), evaluate
(one matmul with the composed plate), read back (output projection).

The composed plate compiles the entire forward pass into its normal
form as a matrix. Applying it is a single host-language evaluation.

**Estimated impact:** Model depth → O(1). 13 passes → 1 matmul.
**Effort:** Already implemented (kernel training). The challenge is
knowing when it's accurate enough.

## 10. Supercompilation (Driving + Folding)

**FP:** Symbolically evaluate the program on all possible inputs.
When states repeat, fold (creating a loop). The result is a more
efficient program that does the same thing.

**Transformer:** 8 crystal basins, ~4 temporal states (B→K→C→B).
Reachable state sequences ≈ 50-100 (constrained by crystal geometry).
Pre-compute the forward pass result for each reachable sequence:

```python
supercompiled = {}
for seq in reachable_basin_sequences():  # ~50-100
    supercompiled[seq] = precompute_continuation(seq)  # d×d matrix

# Runtime: classify sequence, lookup, apply
sequence = classify_basin_sequence(x)
return supercompiled[sequence] @ x  # ONE matmul
```

The entire model compresses to a ~50-entry lookup table of matrices.

**Estimated impact:** O(1) forward pass (lookup + matmul).
**Effort:** High. Need to enumerate reachable sequences and validate
accuracy.

## Compound Effects (techniques compose)

| Combination | Effect |
|-------------|--------|
| Fusion + Partial eval | Signed accumulation over pre-sorted indices — eliminates ALL multiplication |
| Laziness + Strictness | Compute only 2D eigenplane eagerly; 640× less work in fan zone |
| CSE + Type specialization | ONE FFN eval per basin × 8 basins; 512× less FFN work |
| Worker/Wrapper + Effects | All routing upfront, all tensor ops batched; eliminates Python overhead |
| NbE + Supercompilation | Pre-compute per-sequence; runtime = lookup + matmul; O(1) depth |

## Implementation Priority (for training speedup)

The bottleneck is training: 28.6s/step, 77% forward, 13 serial passes.

| # | Technique | Target | Est. speedup | Effort |
|---|-----------|--------|-------------|--------|
| 1 | Lazy neurons (gate-first) | FFN (77%) | 3-5× | Low |
| 2 | Partial eval (index sets) | Ternary matmuls | 2× | Low |
| 3 | Worker/wrapper split | Control overhead | 1.2-1.5× | Low |
| 4 | Cross-token CSE (per-basin) | FFN (77%) | Up to 10× | Medium |
| 5 | Stream fusion (cross-stride) | Memory bandwidth | 1.5-2× | Medium |
| 6 | Basin-specialized forwards | Entire forward | 2-5× | Medium |
| 7 | Strict/lazy dimension split | Fan zone | 10-100× | High |
| 8 | Supercompilation (basin lookup) | Entire forward | depth→O(1) | High |

**Recommended first batch (session 159):**
Items 1-3 (lazy neurons, index sets, worker/wrapper). All low effort,
multiplicative, no architecture change. Combined estimate: 5-10×.
Can resume from existing checkpoints.

**Second batch:**
Items 4-5 (CSE, stream fusion). Medium effort, significant gains.

**Future:**
Items 6-8 require deeper architecture changes but offer the biggest
wins (up to O(1) forward pass via supercompilation).

## Checkpoint Compatibility

All techniques in the first batch (1-3) are IMPLEMENTATION CHANGES
to the forward pass, not architectural changes. They produce
IDENTICAL outputs for IDENTICAL inputs. No new parameters. No
checkpoint format changes. Training can resume from any existing
checkpoint with the optimized forward pass.

Techniques 4-6 may require storing auxiliary data (basin caches,
specialized matrices) but don't change the model parameters.

Techniques 7-8 require architectural changes and would need
migration from existing checkpoints (possible via composed plate
fitting from the old forward pass).
