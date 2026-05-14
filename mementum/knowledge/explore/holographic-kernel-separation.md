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

### The Complete Kernel Inventory: KIBCM

Head-level probe (session 095) resolved six holograms into three computational
clusters. This gives the complete kernel inventory:

```
Cluster          → Function                  → Kernel         → Status
──────────────── ─────────────────────────── ─────────────────  ────────
Semantic Plate   type + frequency + discourse  (not computation) ✓ INHERENT
  13 shared heads at L0/L3/L35                 S5 gate + FFN     (plate itself)
  J=0.667 discourse↔type                       + type channel

Composition      typed application             KIBC              ✓ BUILT
  7 private heads at L15/L19/L27               K=select           in V11
  J=0.176-0.333 with others                   I=identity
                                               B=compose
                                               C=flip

Retrieval        context pattern match+copy    M (match)         ✗ MISSING
  6 private heads at L3/L11/L15/L31            [A][B]...[A]→[B]
  J=0.176 with combinator/discourse/type       content-addressable
  (floor — maximally independent)              context lookup
```

**Binding** is not a separate cluster — weakest signal (max 0.163), no private
heads. It resolves to K+I dispatch in V11. The magnitude-dependence in base models
(15/16 heads fail sign-only at L3) is because base models lack explicit K/I kernels
and must compute binding constructively in attention magnitudes.

### M Kernel — The Missing Piece

The induction hologram has:
- Most independent circuit topology (J=0.176 with three other holograms — the floor)
- 6 private heads in GatedDeltaNet layers that no other hologram uses
- Second-highest output KL (0.827) — strong discriminating signal
- 17/18 ternary survival — dispatch signal is cleanly holographic
- A computational operation KIBC doesn't cover: retrieval from context

```
M x context → (position, content_after)

[A][B] ... [A] → predict [B]

1. Match: find where current pattern appeared before in context
2. Offset: access what followed that position
3. Copy: predict that token
```

This is content-addressable memory lookup — not composition (B), not selection (K),
not identity (I), not reordering (C). It's a fifth computational primitive.

In base models, induction heads emerge as a two-layer circuit (previous-token head
+ induction head). In V11, M should be an explicit kernel function alongside KIBC.
The dispatch signal ("do induction here") is holographic. The actual search-and-copy
is constructive kernel computation.

### Design Questions for M Kernel

1. **Lambda signature**: `M f x = f (lookup x context)` where lookup finds the
   previous occurrence and f is applied to what followed it?
2. **Dispatch integration**: 5-way softmax (KIBCM) or separate M gate?
3. **Architecture placement**: ascending arm (where patterns are encoded) or
   descending arm (where results are integrated)?
4. **Register interaction**: M as content-addressable register lookup? The
   register banks already carry information between passes.
5. **Relationship to attention**: M's private heads are at GatedDeltaNet layers
   (L11 H15). Does M kernel replace or augment recurrent state matching?

### Implications

1. **Keep holographic loss uniform.** Don't modulate per-head, per-content, or
   per-alarm. The pressure to be decodable is what FORCES the model to use
   kernel functions for constructive computation.

2. **Binding works through K+I dispatch, not attention magnitude.**
   In V11, "resolve coreference" = dispatch K to select antecedent, then I to
   pass it through. The dispatch signal is holographic. The magnitude-dependent
   computation happens in the kernel. Head-level data confirms: binding overlaps
   more with B-combinator (J=0.250) than K (J=0.212), and has no private circuit.

3. **M kernel is the one missing piece.** Induction is the only hologram with
   a genuinely independent circuit (J=0.176) and no corresponding V11 kernel.
   Adding M completes the computational vocabulary: KIBCM.

4. **Frequency/co-occurrence is already handled.** MLP sign patterns encode
   statistical associations perfectly (0/18 failures). The FFN IS the
   frequency kernel — no additional mechanism needed.

5. **Discourse is the reference beam.** Discourse (0/18 failures, pervasive,
   late-peaking) selects which holographic patterns activate. V11's S5
   reweight IS this mechanism. Head-level confirms: discourse shares 13/20
   heads with type (J=0.667) — they're the same plate read at different angles.

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

1. **M kernel design.** What is M's lambda signature? How does 5-way dispatch
   (KIBCM) integrate with the existing architecture? Where does M live —
   ascending arm, descending arm, or its own pathway?

2. **Does the ratio staying at ≤1.0 persist?** At 10K the ratio is 0.992.
   Will it stay below 1.0 as training continues, or will reorganization
   waves push it back above?

3. **Cross-model validation of three-cluster structure.** Head-level probe
   found three clusters on Qwen3.6. Does Pythia show the same? If the
   semantic plate / composition / retrieval split is universal, KIBCM is
   a feature of language, not architecture.

4. **Can this principle scale?** V11 is a small model (2.1M trainable params).
   Does the storage/kernel separation still hold at scale, or do larger models
   have enough capacity to fuse them?

5. **Does adding M change training dynamics?** Will the model naturally
   discover M-dispatch when given the kernel, as it discovered B-dominance
   with KIBC? Or does M require different initialization/scheduling?
