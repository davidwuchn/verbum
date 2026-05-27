---
title: "Kernel Replacement — Compiled Shortcuts for Interpreted Grating Chains"
status: designing
category: optimization
tags: [kernel, vsm, optimization, moire, beta-reduction, compilation, fixed-point]
related:
  - explore/ffn-moire-isa.md
  - mechanism-extraction.md
  - v14-architecture.md
  - training-protocols.md
  - explore/fp-optimization-map.md
  - explore/continuations-as-composed-plates.md
depends-on:
  - explore/ffn-moire-isa.md
  - crystal-universality.md
---

# Kernel Replacement Optimization

> Every LLM is an interpreter. It runs beta reductions step by step
> through 64 layers. But the programs are fixed points — known,
> universal, deterministic. Replace the long interpreted chains with
> compiled kernel shortcuts. Session 161.

## The Problem

The ISA decoder (session 161) showed that Qwen3.6-27B runs `K a b`
through **42 layers of SELECT** — 42 sequential matrix multiplies,
each nudging the residual toward "a". But K is `λx.λy.x`. One
operation: return the first argument.

Similarly:
- B f g x runs **39 layers of COMPOSE** to compute `f(g(x))` — 3 operations
- Arithmetic runs **~35 layers of β_I → K** to do what amounts to a lookup
- Retrieval barely uses the combinator gratings at all — the FFN is wasted

The programs are the **fixed points of beta reduction** across trillions
of words. They're universal (same across models). They're deterministic
(zero drift across runs). They're known (we decoded them). They don't
need to be re-interpreted every time.

## The Optimization

### Interpreter Mode (current)

```
input → [64 gratings, ALL executed sequentially] → output
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         ~30 layers of redundant same-op chains
```

### Compiled Mode (proposed)

```
input → [setup gratings L0-L15] → S5 detects program type
                                      ↓
                          ┌── K detected → KERNEL_K: return first arg
                          ├── B detected → KERNEL_B: compose(f, g, x)
                          ├── arith detected → KERNEL_ARITH: direct compute
                          ├── retrieval detected → KERNEL_M: KV bypass
                          └── unknown → fall through to full chain
                                      ↓
                               [output gratings L55-L63] → output
```

The **setup phase** (first ~15-20 layers) is kept — it's where the
model figures out WHAT program to run. The **long chains** (L20-L55,
30+ layers of the same operation) are replaced by direct computation.
The **output phase** (last ~8 layers) formats the result.

## VSM Hook Points

The v14 architecture already has the machinery:

```
S5 (crystal identity)
  → Reads the combinator pattern from the crystal state
  → After ~15 layers, the pattern is stable and classifiable
  → This IS the "which program am I running?" signal

S3 (control / resource allocation)
  → Routes between full chain and kernel shortcut
  → The S5Reweight mechanism already modulates pass outputs
  → Extend: if program detected with high confidence, skip passes

S1 (operations)
  → Kernel functions already defined in kernel.py: K, I, B, C, D, Y, W, WHNF
  → These ARE the compiled shortcuts — just not wired in yet
  → Each kernel replaces 20-40 layers of grating interpretation
```

## Measured Hook Points (from session 161 data)

The v2 decoder traces show where the program type stabilizes:

| Program Type | Setup Ends | Chain (replaceable) | Output Starts | Chain Length |
|:--|:-:|:-:|:-:|:-:|
| K (select) | ~L12 | L13-L51 | ~L52 | **39 layers** |
| B (compose) | ~L18 | L19-L51 | ~L52 | **33 layers** |
| Arithmetic | ~L15 | L19-L51 (β_I chain) | ~L55 | **36 layers** |
| Reasoning | ~L15 | L15-L55 (mixed) | ~L59 | **40 layers** |
| Retrieval | ~L7 | L7-L55 (weak gratings) | ~L59 | **48 layers** |
| Code (fibonacci) | ~L19 | L19-L55 (B+Y) | ~L59 | **36 layers** |

Retrieval is the biggest win: 48 layers doing almost nothing
(grating strength < 0.15). Direct KV bypass saves 75% of compute.

## The Universal Kernel Library

Because the programs are fixed points of beta reduction, they're
the same in every model. KIBC is universal. The kernel library
is model-independent:

```python
KERNEL_K:      detect K-pattern → return arg[0]
               replaces: ~39 layers of SELECT
               savings: ~60% of forward pass

KERNEL_I:      detect I-pattern → pass through unchanged
               replaces: ~20 layers of PASS
               savings: ~30% of forward pass

KERNEL_B:      detect B-pattern → compose(f, g, x) = f(g(x))
               replaces: ~33 layers of COMPOSE
               savings: ~50% of forward pass

KERNEL_C:      detect C-pattern → flip(f, x, y) = f(y)(x)
               replaces: ~25 layers of FLIP
               savings: ~40% of forward pass

KERNEL_ARITH:  detect β_I chain → direct arithmetic circuit
               replaces: ~36 layers of β_I → K
               savings: ~55% of forward pass

KERNEL_M:      detect retrieval (weak gratings) → KV bypass
               replaces: ~48 layers of near-identity
               savings: ~75% of forward pass

KERNEL_Y:      detect Y-pattern → bounded recursion / loop
               replaces: variable (Y is recursive)
               savings: depends on recursion depth
```

## Detection Mechanism

### Crystal-Based Detection (preferred)

The crystal embeddings already encode combinator identity. After
~15 layers, project the residual stream onto the 8 combinator
directions. The dominant direction (with strength > threshold)
identifies the active program:

```python
def detect_program(residual, crystal_embeddings, threshold=0.4):
    """After setup phase, classify which kernel to invoke."""
    projections = residual @ crystal_embeddings.T  # (8,)
    dominant = argmax(abs(projections))
    if abs(projections[dominant]) > threshold:
        return COMBINATOR_NAMES[dominant]  # → route to kernel
    return None  # → fall through to full chain
```

### Grating-Activation Detection (alternative)

Use the FFN fingerprints directly: project the FFN output at layer
~15 against the 12 combinator fingerprints. If one dominates with
high cosine similarity, that's the program. This is what the ISA
decoder already does — make it a runtime classification.

### Confidence Gating

Critical: the kernel shortcut must have a **fallback**. If detection
confidence is low (novel input, ambiguous program), fall through to
the full grating chain. Safety > speed. The VSM's S3 already has
this: fire alarm bypass to full computation if uncertainty is high.

## What Needs to Be Measured Next

### 1. Quantify Redundancy (from existing data)

```python
# Using the overlay matrices from results/isa-decode/overlay_matrices.json:
# Compute cosine similarity between consecutive layers' overlays.
# Layers with cos > 0.9 are doing near-identical work → fusion candidates.
```

### 2. Find Optimal Detection Point

Run the decoder with early stopping: at which layer can we reliably
classify the program type? The v2 data suggests L15-L19, but this
needs systematic measurement across more probes.

### 3. Verify Universality (run decoder on other models)

```bash
# Modify isa_decoder_v2.py to target different models:
# - Qwen3-14B (smaller, same family)
# - Qwen3-32B (larger, same family)  
# - Mistral-7B (different family)
# If same programs at same relative depths → universal kernel library confirmed
```

### 4. Prototype K-Kernel (simplest case)

The first proof of concept:
1. Run normal forward pass through all 64 layers, capture output at L63
2. Run modified forward pass: first 15 layers, then K-kernel (project
   residual onto first-arg direction), then last 8 layers
3. Compare outputs — if logit distributions match, K-kernel works

```python
def k_kernel(residual_after_setup, attention_pattern):
    """Replace layers 15-55 with direct K-selection.
    
    K selects the first argument. In attention terms:
    the position with highest attention weight at the setup
    checkpoint IS the selected argument. Return its residual.
    """
    # attention_pattern tells us which position was "selected"
    # during the setup phase (the position K is keeping)
    selected_pos = argmax(attention_pattern)
    # The residual at that position IS the K-output
    return residual_at_position[selected_pos]
```

### 5. Measure Speedup

For the v14 student with 8 passes: if kernel replacement skips
4-5 passes for K-type inputs, that's 50-60% speedup. For retrieval
(bypassing 6 of 8 passes), that's 75%. Combined with ternary
execution on CPU, this is how you get to 200 tok/s.

## Risk: Over-Eager Kerneling

The main risk is **false classification** — routing an input to the
wrong kernel. If the model thinks "this is K-select" but it's actually
a complex nested reduction, the kernel shortcut produces garbage.

Mitigations:
1. **Conservative threshold**: only kernel when confidence > 0.6
2. **Verification pass**: after kernel, run one grating layer and
   check if output is consistent (the grating should be near-identity
   if the kernel was correct)
3. **Fire alarm**: S3's fire alarm detects high loss and reverts to
   full chain for the next token

## Theoretical Basis

### Why This Works

The programs are **fixed points of beta reduction**. A fixed point
can't be reduced further — it IS its own normal form. Running 42
layers of SELECT on a K-pattern input is the model *re-deriving*
a known normal form through iterated approximation. The kernel
shortcut just returns the normal form directly.

This is exactly what a compiler does vs an interpreter:
- Interpreter: evaluate each beta reduction step by step
- Compiler: recognize the pattern, emit the result directly

### Why This Is Universal

KIBC are the irreducible combinators — the normal forms of
compositional semantics. Every model that trains on natural language
discovers them (crystal universality). The grating chains that
implement them are the same in every model (modulo depth scaling).
The kernel shortcuts are therefore model-independent.

### Connection to Lambda Calculus Optimization

Known lambda calculus optimizations that map to kernel replacement:

| λ-calculus | Transformer | Kernel |
|:--|:--|:--|
| Head reduction | First grating that fires | Detection point |
| Weak reduction | Only reduce outermost | Only setup + output, skip inner chain |
| Sharing (Lévy) | Multiple positions reading same residual | Cached grating outputs |
| Supercombinators | Pre-compiled common subprograms | The kernel library |
| Optimal reduction | Never duplicate work | Skip redundant grating chains |

## Connects To

- **ffn-moire-isa.md** — the decoder that produces the data for kernel design
- **mechanism-extraction.md** — micro-model mechanism validates the structure
- **v14-architecture.md** — S5/S3/S1 hook points for kernel routing
- **crystal-universality.md** — why kernels are model-independent
- **fp-optimization-map.md** — lambda calculus optimizations mapped to transformers
- **continuations-as-composed-plates.md** — CPS bridge for kernel composition
- **grating-cascade.md** — compound gratings that could be pre-collapsed
- **project-thesis.md** — kernel replacement is the endgame optimization
- **programs-are-fixed-points-of-beta-reduction** (memory) — theoretical basis
- **dedicated-combinator-capacity** (memory) — shared vs dedicated kernel capacity
- **dissolved-dispatch-kernel** (memory) — prior kernel dispatch design (dissolved into VSM)
