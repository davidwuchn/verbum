---
title: "Recursion Mirrors — Ternary Depth for Sequential Computation"
status: designing
category: architecture
tags: [recursion, mirrors, ternary, depth, Y-combinator, cycles, variable-depth]
related: [crystal-native-architecture.md, extraction-sign-accuracy.md, holographic-computer.md]
depends-on: [crystal-native-architecture.md, extraction-sign-accuracy.md]
created: session 173
---

# Recursion Mirrors

> Strided attention students have fewer layers than full-attention
> teachers. Recursion (Y combinator) is fundamentally sequential —
> each application of f needs its own reduction step. Ternary mirrors
> can add reduction depth without adding layers, by storing multiple
> programs per layer position and executing them sequentially.

## The Problem

```
Teacher (Qwen3.6-27B, 64 layers, full attention):
  Y combinator detected at L55, L59
  Deep recursion: f(f(f(f(x)))) uses multiple consecutive layers
  64 layers total → plenty of depth for any program

Student (16-32 layers, strided attention):
  Fewer layers = fewer sequential reduction steps
  If 10 layers are used for classify + enrich + commit,
  only 6 remain for recursion
  Fibonacci(10) needs ~10 applications of Y → doesn't fit
```

Recursion is fundamentally sequential: Y f = f(Y f) = f(f(Y f)) = ...
Each application of f needs one complete reduction step. You cannot
parallelize it (each step depends on the previous result).

## Two Types of Mirrors

Session 173 proved that weight matrices decompose into:
- **Plate 1:** sign topology (the program)
- **Plate 2:** magnitude classification (above/below average)

These are **ADDITIVE** mirrors — both plates see the SAME input:
```
output = plate1 @ x * gamma1 + plate2 @ x * gamma2
```

Recursion mirrors are fundamentally different — they are **COMPOSED**:
```
output1 = grating(plate1, input)      # First reduction
output2 = grating(plate2, output1)    # Second reduction (reads first output)
output3 = grating(plate3, output2)    # Third reduction
```

Each plate is a complete SwiGLU grating. The second plate reads from
the residual AFTER the first plate writes. This is mathematically
identical to what happens between adjacent layers in a transformer.

## The Attention Requirement

**Critical finding:** recursion generally requires attention between
applications.

In the teacher:
- Y at L55 applies the recursive function
- Attention between L55-L59 routes the result
- Y at L59 applies it again

The routing is necessary because:
- f(f(x)) at position i may depend on positions j, k
- The FFN is per-token (column-wise) — it cannot move information
  between token positions
- Attention is the ONLY inter-token operation

**Therefore:** pure plate chaining (FFN→FFN without attention) only
works for per-token recursive computations:
- Iterative refinement of a single representation
- Fixed-point iteration on one token's embedding
- Church numeral operations (purely positional)

For INTER-TOKEN recursion (Fibonacci, tree traversal, multi-step
reasoning): attention steps are needed between plate applications.

## The Architecture: Recursion Cycles

```
Standard layer:    [Norm → FFN(plate) → Norm → Attention] × 1
Recursion layer:   [Norm → FFN(plate_k) → Norm → Attention] × K

K = number of recursion mirrors at this layer
Each cycle uses a DIFFERENT FFN plate but SHARED attention weights
The attention weights are shared because the ROUTING is the same —
only the DATA being routed changes between cycles.
```

This is the v11 CycleContinue mechanism, but with:
- Separate plates per cycle (instead of shared weights for all cycles)
- Each plate encodes a DIFFERENT step of the recursive computation
- The gate between cycles is WHNF detection (not a learned continue signal)

### WHNF Detection (the recursion terminator)

Between cycles, check if the computation has reached a fixed point:

```python
for k in range(K):
    # Apply grating k
    hidden = silu(gate_plate[k] @ x) * (up_plate[k] @ x)
    delta = down_plate[k] @ hidden
    x = x + delta
    
    # Attention (shared weights, routes between token positions)
    x = x + attention(norm(x))
    
    # WHNF detection: has the residual stopped changing?
    if norm(delta) < epsilon:  # Fixed point reached
        break                  # Skip remaining cycles
```

This gives **variable effective depth** — simple inputs use 1 cycle,
recursive inputs use all K cycles. The compute cost is proportional
to actual recursion depth, not maximum depth.

## Zone-Aware Plate Allocation

Not all layers need recursion depth. The crystal structure tells us:

```
SILENT zone (task classify):
  1 plate per layer (sign only, no magnitude mirror needed)
  Task classification is discrete — binary decision, no iteration
  No recursion ever happens here
  
ENRICH zone (fact retrieval + composition):
  2 plates per layer (sign + magnitude mirror)
  Composition (B) may use 2-3 sequential steps
  Optional: 1 recursion mirror for B-chains
  
RECURSION zone (late layers, Y combinator):
  2 + R plates per layer (sign + magnitude + R recursion plates)
  R = maximum recursion depth at this layer
  R=3 gives 4 total passes per layer
  With 3 recursion layers × 4 passes = 12 extra reduction steps
  
COMMIT zone (WHNF emission):
  1-2 plates per layer (just emit, no computation)
```

## Storage Cost

The beauty: recursion mirrors are cheap because they're only at a few
layers, and they're the same 2-bit-per-position ternary format.

```
For a 16-layer student (d_model=1280, d_ff=17408):

Standard (2 mirrors everywhere):
  16 layers × 3 matrices × 17408 × 1280 × 2 mirrors × 2 bits/pos
  = 572 MB

With recursion zone (3 layers × 4 mirrors):
  13 normal layers × 2 mirrors = 26 mirror-layers
  3 recursion layers × 4 mirrors = 12 mirror-layers  
  Total = 38 mirror-layers
  = 38/32 × 572 MB = 679 MB

Extra cost of recursion: ~107 MB (+19%)
Effective depth: 16 → 25 steps (+56%)
```

19% more storage for 56% more computation depth. The recursion mirrors
are extremely cost-effective because they reuse the same attention
weights (shared across cycles).

## Comparison to Alternatives

| Approach | Extra storage | Extra compute | Effective depth |
|----------|---------------|---------------|-----------------|
| More layers (brute force) | +100% | +100% | 2× |
| **Recursion mirrors (K=3)** | **+19%** | **+variable** | **up to 1.56×** |
| v11 CycleContinue (shared weights) | +0% | +variable | up to 3× per cycle |
| Adaptive compute (Graves) | +control overhead | +variable | unlimited* |

*Adaptive compute requires a learned halting mechanism; recursion mirrors
use WHNF detection (structural, not learned).

The advantage over v11 CycleContinue: **separate plates per cycle means
each iteration can compute a DIFFERENT function.** In Y combinator,
f may need to be applied differently at each depth (different operands
available, different partial results). Shared weights force identical
computation each cycle — separate plates allow adapted computation.

## Connection to the Crystal

The teacher's Y grating at L55 and L59 likely encodes:
- L55: "apply f to the current state" (initial reduction)
- L56-L58: attention routing + minor adjustments
- L59: "apply f to the updated state" (second reduction)

In the student, a recursion layer with 4 mirrors encodes:
- Mirror 0: "apply f to current state" (= teacher L55's plate, TD-adapted)
- Mirror 1: "apply f to once-reduced state" (= teacher L59's plate, TD-adapted)
- Mirror 2: "apply f if still not WHNF" (= continuation, may not exist in teacher)
- Mirror 3: "final correction before WHNF" (cleanup)

The TD adaptation cycle naturally discovers what each recursion mirror
should encode — it's finding the equivalent of teacher layers 55-63
compressed into 3-4 sequential plates at one student layer.

## The Deep Question: Is K Fixed or Adaptive?

**Fixed K:** Each recursion layer always has K mirrors. Simple, deterministic.
Wastes compute on simple inputs (WHNF detection helps via early exit).

**Adaptive K:** Choose how many mirrors to apply based on input complexity.
More powerful but requires a selection mechanism. The CycleContinue gate
from v11 was one attempt at this — a learned signal that decides "keep
going" vs "stop here."

With WHNF detection (structural, not learned), we get adaptive behavior
for free: the residual norm tells us when we've converged. This is
cleaner than a learned gate because it's based on physics (fixed-point
convergence) rather than a trained signal.

## The Stride Cascade IS the Recursion Unroll

**Key insight (session 173):** In a stride stack, larger strides process
the RESULT of smaller strides (via the shared residual stream). This
means the stride cascade is ALREADY a sequential reduction chain:

```
stride_1:     f(local_context)            — base case
stride_4:     sees stride_1 output → f²   — one recursion level
stride_16:    sees s1+s4 output → f³      — two recursion levels
stride_64:    sees s1+s4+s16 output → f⁴  — three levels
...
stride_32768: sees ALL prior → f^16       — deepest recursion (16 levels!)
```

**The stride hierarchy IS the Y combinator unrolled.** Each stride level
is one more application of the recursive function. We get up to 16
sequential reduction steps FROM THE STRIDE CASCADE ALONE — no extra
architectural mechanism needed.

But this only works if **different strides apply different programs.**
Current v14 uses a shared FFN plate across all strides — stride_32768
applies the SAME reduction as stride_1, wasting the sequential structure.

### The Base + Recursion Plate Design

```
base_plate:        shared across all strides (the common program)
recurse_plate[k]:  applied ONLY at strides >= threshold(k)

stride 1-16:     output = base_plate @ x
stride 64-1024:  output = base_plate @ x + recurse_0 @ x
stride 4096+:    output = base_plate @ x + recurse_0 @ x + recurse_1 @ x
```

**Why ADDITIVE works here:** The stride cascade already provides the
sequential composition (each stride sees prior strides' output in the
residual). We don't need to compose plates sequentially — the STRIDES
compose. Each plate just contributes the RIGHT correction for that
recursion depth level.

The recursion plates are additive corrections to the shared base:
- Base plate: "apply the universal reduction" (same at every stride)
- Recurse_0: "at medium depth, also apply this adjustment"
- Recurse_1: "at maximum depth, also apply this further correction"

### Why Larger Strides Need More Depth

1. **Information abstraction:** Stride_32768 attends to tokens 32K apart.
   Each of those tokens SUMMARIZES a huge context chunk. Operating on
   summaries requires more sequential steps than operating on raw tokens.

2. **Multi-hop reasoning:** "Paris → France → Europe → continent" requires
   3 hops. Local strides see the first hop. Medium strides chain 2 hops.
   Large strides resolve the full chain. Each hop = one reduction step.

3. **Compositional depth:** B f g x = f(g(x)) at stride_4 composes two
   local functions. B(B f g) h x = f(g(h(x))) at stride_64 composes
   three — needs one more reduction step to evaluate.

4. **Fixed-point distance:** Stride_1 operates on nearly-reduced forms
   (local context is already specific). Stride_32768 operates on
   abstract forms far from WHNF — needs more steps to collapse.

### Storage Cost

```
Shared plate (current v14):         33 MB per stack
Base + 2 recursion plates:          ~50 MB per stack (+50%)
  (if recurse plates are 30% sparse: ~43 MB, only +30%)

Cost of recursion depth:            +30-50% storage
Benefit:                            16 effective recursion levels
                                    (vs 1 with shared plates)
```

The recursion plates can be SPARSE because they only encode the
DIFFERENCE from the base program at that depth level. At shallow
strides, the base plate is correct — the recursion plate adds nothing.
At deep strides, only specific positions need depth-adjusted signs.
TD adaptation naturally discovers which positions differ per depth.

### Connection to Magnitude Mirrors

The two types of mirrors serve different purposes and STACK:

```
Per stride, the full expansion is:

output = (base_plate1 × γ1 + base_plate2 × γ2) @ x     # base: sign + magnitude
       + (recurse0_plate1 × γ3 + recurse0_plate2 × γ4) @ x  # depth-0 correction (if stride >= 64)
       + (recurse1_plate1 × γ5 + recurse1_plate2 × γ6) @ x  # depth-1 correction (if stride >= 4096)

Simplification (if recursion plates don't need magnitude mirrors):
output = (base_plate1 × γ1 + base_plate2 × γ2) @ x     # full magnitude precision
       + recurse0_plate × γ3 @ x                         # sign-only correction
       + recurse1_plate × γ4 @ x                         # sign-only correction
```

The recursion plates may only need 1 mirror (sign topology) because
they're encoding WHICH positions differ at that depth, not precise
magnitudes. The base plate needs 2 mirrors (sign + magnitude) for
full Q4-Q5 quality. The corrections are small perturbations — sign-only
may suffice.

## Revised Architecture (Stride-Aware Recursion)

```
Layer N, ascending pass (fine → coarse):

  For stride s in [s1, s4, s16, ..., s32768]:
    # Select plates for this stride level
    plates = base_plate
    if s >= stride_threshold_0:
        plates += recurse_0
    if s >= stride_threshold_1:
        plates += recurse_1
    
    # Apply grating
    hidden = silu(gate_plates @ x) * (up_plates @ x)
    delta = down_plates @ hidden
    
    # Attention at this stride
    x = x + attention_stride_s(norm(x + delta))
    x = x + delta

  # After all strides: the residual has been recursively refined
  # Stride_32768 operated on the full recursive result of all prior strides
```

This replaces the earlier "cycles within a layer" proposal with a
cleaner design: **the strides ARE the cycles.** No architectural change
needed — just per-stride-group plate selection.

## Open Questions

1. **Can TD discover the recursion plate content?** Train with shared
   base plate, then measure which positions' gradients differ by stride.
   Positions with stride-dependent gradients → candidates for recursion plates.

2. **What are the optimal stride-group boundaries?** [1-16], [64-1024],
   [4096-32768] is a guess. Run the hologram reader at per-stride
   granularity on the teacher to measure where the opcode map CHANGES
   between strides (if stride-specific fingerprints differ → boundary).

3. **Are recursion plates sparse enough to be efficient?** If only 10-20%
   of positions differ between base and recursion, the plates can be
   stored as sparse corrections. If 50%+ differ, need full plates.

4. **Does the descending pass (coarse→fine) also need recursion plates?**
   Descending strides go from abstract to concrete (stride_32768 first,
   stride_1 last). This is the INVERSE of recursion — it's distributing
   results back down. Different plates for descending vs ascending?

5. **Can we measure the recursion depth empirically?** Run teacher on
   inputs of varying complexity. Measure at which stride level the
   output stabilizes (delta → 0). Simple inputs: stabilize at stride_16.
   Complex inputs: still changing at stride_32768. This maps directly
   to required recursion depth per input class.
