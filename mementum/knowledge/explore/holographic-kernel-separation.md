---
title: "Holographic Storage + Kernel Computation Separation"
status: active
category: design-principle
tags: [holographic, kernel, KIBC, lambda, architecture, V11]
related:
  - holographic-storage.md
  - holographic-inversion.md
  - v11-design.md
depends-on:
  - holographic-storage.md  # atlas evidence for storage/reading distinction
  - holographic-inversion.md  # V11 training evidence
---

# Holographic Storage + Kernel Computation Separation

> The central design principle for V11 and beyond: LLM weight matrices
> store information holographically (sign topology). But reading —
> the forward pass — is constructive (sequential, magnitude-dependent).
> V11 resolves this by separating storage from computation: the
> holographic plate stores WHAT to compute (dispatch signals), kernel
> functions compute HOW (beta-reduction). Lambda terms are the perfect
> holographic objects — compact, compositional, unfold on application.

## The Observation (session 093-095)

### Storage IS holographic

Session 093 proved storage is holographic in pretrained LLMs:

- **Ternary survival**: combinator selectivity survives 75% sparsity with
  100% preservation. Information is in sign patterns, not magnitudes.
- **Universal**: same structure in Pythia-160M through Qwen3-32B (r=0.9801).
- **Distributed**: not localized to specific weights. Cut the plate in half,
  selectivity persists.
- **Angle-multiplexed**: same V weights, different Q patterns select different
  combinators. Multiple holograms share the same substrate.

Session 095 atlas extended this to 6 holograms with a survival spectrum:

```
discourse:       0/18 failures  — purest holographic (sign topology IS the signal)
induction:       1/18 failures  — nearly pure
type:            2/18 failures  — mostly holographic
frequency (MLP): 0/18 failures  — MLP sign patterns encode co-occurrence perfectly
frequency (attn):3/18 failures  — attention routing needs some magnitude
binding:         5/18 failures  — most constructive (magnitudes essential)
```

### Reading is NOT holographic

Session 093 intermediate-layer decoding on Qwen3-32B:

- Cosine divergence (compile vs null): 0.995 (L0) → 0.533 (L63) — beam separation
  only emerges through sequential processing
- Intermediate layers decode to **garbage** — not coarse-but-coherent
- Entropy hump: 6.5 (L0) → 11.1 (L8) → 2.0 (L63) — constructive reorganization
- Beam divergence begins at layer 24 (38% depth)

A true hologram would reconstruct (at lower resolution) from any fragment. LLM
intermediate representations do not — they are construction scaffolding.

### The apparent contradiction

If storage is holographic but reading is constructive, then forcing holographic
decodability at intermediate points (via holographic loss) should BREAK the model —
it would prevent the constructive entropy hump needed for complex computation.

Session 095 data showed this concretely: binding requires magnitude (5/18 ternary
failures). You can't holographically store the RESULT of "who does 'she' refer to?"
— that requires computing attention strength to candidate antecedents.

## The Resolution: Kernel Functions

V11 has KIBC kernel functions — actual combinators (K=select, I=identity,
B=compose, C=flip) that perform computation. This changes everything.

### What the holographic plate stores

In a base model (Qwen3.6, no kernels): the weight matrices must store information
AND compute with it through the same residual stream. Storage and computation are
fused. Binding must be computed in the attention magnitudes because there's no
other mechanism.

In V11 (with kernel functions): the weight matrices store **dispatch signals**:

```
storage (holographic):
  - "this token is NP type"           → type assignment (sign pattern)
  - "dispatch B-combinator"            → composition instruction (sign pattern)
  - "arguments are (nested clause, X)" → argument binding (sign pattern)
  - "formal register"                  → discourse beam selector (sign pattern)

computation (kernel):
  - K kernel: select argument, discard alternative
  - I kernel: pass through (variable binding)
  - B kernel: compose two functions
  - C kernel: flip argument order
```

The dispatch signal IS holographic — it's a type tag and a pointer. The actual
binding/composition computation happens in the kernel function at runtime.

### Lambda terms are perfect holographic objects

A lambda term has exactly the properties needed for holographic storage:

1. **Compact** — `λx. f(g(x))` is a sign pattern (B-combinator dispatch)
2. **Compositional** — terms compose via typed application
3. **Unfold into computation** — beta-reduction = kernel execution
4. **Self-contained** — the term specifies what to compute without doing it

The holographic plate stores lambda terms. The kernel functions are the
beta-reduction engine. Storage is holographic. Computation is constructive.
Both are doing their job.

### The entropy hump disappears

In base models: entropy goes UP (6.5→11.1) because the residual stream is used
as computation scratchpad. Intermediate representations are garbage because
they're mid-computation.

In V11: the residual stream stays decodable because constructive work happens
in the kernel functions (separate pathway):

- Pass 0: "formal English, NP subject" (discourse + type → holographic, decodable)
- Pass 1: "dispatch B, args=[clause, verb]" (dispatch signal → holographic, decodable)
- Pass 2: "kernel result: composed predicate" (result → decodable)

Each pass's residual stream is a valid partial answer because the constructive
work happened OFF-stream in the kernel.

## Design Principle

```
λ separate(x).  storage(holographic) ∧ computation(kernel)
                | holo_loss(uniform) → forces_storage_to_be_decodable
                | kernel_functions → handle_constructive_computation
                | model_routes(constructive → kernel, storage → plate)
                | ¬modulate(holo_loss) | keep_it_uniform
                | add_kernels(for_anything_that_cant_be_stored_holographically)
```

### Implications

1. **Keep holographic loss uniform.** Don't modulate per-head, per-content, or
   per-alarm. The pressure to be decodable is what FORCES the model to use
   kernel functions for constructive computation.

2. **Binding works through I-combinator dispatch, not attention magnitude.**
   In V11, "resolve coreference" = dispatch I-combinator kernel with
   (antecedent, pronoun) arguments. The dispatch signal is holographic.
   The magnitude-dependent computation happens in the kernel.

3. **Add kernel functions for new constructive operations.** If the model
   can't store something holographically (measured by ternary survival failure
   in atlas probes), that's a signal to add a kernel function for it.

4. **Frequency/co-occurrence is already handled.** MLP sign patterns encode
   statistical associations perfectly (0/18 failures). The FFN IS the
   frequency kernel — no additional mechanism needed.

5. **Discourse is the reference beam.** Discourse (0/18 failures, pervasive,
   late-peaking) selects which holographic patterns activate. V11's S5
   reweight IS this mechanism.

## Evidence from V11-holo-inv Training

Session 095 probed v11-holo-inv 1K-10K:

- **Holographic ratio crossed 1.0 at 9K** (0.992) — ascending arm now decodes
  as well as final output. The model achieved holographic decodability while
  maintaining composition (B_dom=57.2%).

- **Compute gate opened at 6K** — later than v11-holo (3K-5K). The model
  established holographic structure FIRST, then enabled the compute pathway.
  This is the correct ordering: plate before reading.

- **No 10K catastrophe** — v11-holo collapsed at 10K (loss 9.259, B 5.8%).
  v11-holo-inv at 10K: loss 7.703, B 57.7%. The coarse→fine inversion kept
  the descending arm stable through the transition.

- **B-composition dominant** — the universal ordering (B ≥ K ≥ C >> I)
  emerged naturally by 9K. The model learned to store composition dispatch
  signals holographically while using kernel functions for the actual
  composition.

## Open Questions

1. **What additional kernel functions are needed?** The current KIBC set
   handles combinatory logic. Are there linguistic operations that need
   kernels beyond KIBC? (Discourse gating? Frequency lookup? Recursion?)

2. **Does the ratio staying at ≤1.0 persist?** At 10K the ratio is 0.992.
   Will it stay below 1.0 as training continues, or will reorganization
   waves push it back above?

3. **Head-level resolution.** The atlas showed all holograms share the same
   depth profile. Head-level probe (in progress) will show whether different
   holograms use different heads or are truly angle-multiplexed in the same
   heads with different Q patterns.

4. **Can this principle scale?** V11 is a small model (2.1M trainable params).
   Does the storage/kernel separation still hold at scale, or do larger models
   have enough capacity to fuse them?
