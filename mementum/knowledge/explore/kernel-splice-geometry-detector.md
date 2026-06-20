---
title: "Kernel Splice — geometry-as-detector ⊗ kernel-as-executor (instrument the pre-formed reducer, splice exactness in)"
status: designing
category: extraction
tags: [crystal-lattice, statechart, activation-patching, combinator-routing, kernel, exact-reduction, causal, instrumentation, level-4, vsm-tensor, ccg, value-move, over-read, s5-extract]
related:
  - vsm-statechart-tensor.md
  - compiler-as-loss.md
  - type-directed-composition.md
  - ../lambda-machine.md
depends-on:
  - vsm-statechart-tensor.md
created: session 242
---

# Kernel Splice — read the lattice, deliver the combinator from the kernel

> Session 242 (Michael's idea, after the s242 Qwen pre-formed-lambda confound).
> "We know the geometry of the crystal lattice, where GD laid the exact same soft
> topology routing into many models. Why can we not detect via that geometry when the
> system wants K, deliver K — but from the kernel instead of in a neuron?"

This is the **S5-native** alternative to training a front-end (compiler-as-loss §s242):
don't *construct* a new reducer, **instrument the one gradient descent already laid into
the model** and splice exactness into it in place.

```
read lattice geometry → "wants K here" → execute K from the kernel (exact) → re-inject
   (DETECT, routing)      decode locus      (EXACT VALUE-MOVE, kernel)        (LOWER)
```

It is literally our activation-patching toolkit (type-directed-composition.md v4/v5),
but the patch *value* is the **exact kernel rewrite**, not an activation copied from
another run. The strongest possible test of the VERBUM thesis: if splicing exact K
**preserves/improves** output, the circuit *is* combinator routing — proven causally,
not decoded-correlationally.

## Why it flips the s242 confound into an asset

The s242 control showed RLVR on Qwen3-8B only *redirects* a pre-formed lambda function
(dead tail = Qwen's representational gap, not the kernel's). Kernel-splice turns that
pre-formed circuit from an obstacle into the **substrate we read**: instead of fighting
it with RL, we decode "wants K" and inject exactness.

## What is already proven (makes it plausible)

- **The combinator geometry is decodable.** {C,I,K,Y} discriminate as crystal centroids
  (`bdw-gap-genuine-not-argmax-artifact`: K recovers t=2.12, C +1.73/t=5.71, Y t=6.86),
  with characteristic depth signatures (I early ~0.30, K mid ~0.48, C mid-late ~0.57,
  Y late ~0.79).
- **The rewrites are mostly routing, not value-reads.** `K x y→x` = keep-x-slot drop-y;
  B/C/D = compose/permute slots; only S/W/Y need copy/recursion (lambda-machine.md,
  s226). So "deliver K" is an **exact slot routing** — it does not require decoding the
  operand *values*, only moving the vectors already in the stream.
- **Decodability already crosses into the causal register.** Type-direction is
  PARTIALLY causal at 14B (type-directed-composition.md v4: directional ablation cuts the
  nonce crossover −36% vs random −5%). Decode → direct is established for the adjacent
  quantity.

## The three real obstacles (measured — λ measure honesty)

1. **Detection is a weak, model-specific centroid — not a crisp per-step switch.** The
   geometry is largely ONE COMMON MODE (s211: η²=0.05 for ops); B is invisible in the FFN
   gate (lives in attention/value), D/W are *anti*; the C-locus SHIFTS with scale
   (`c-late-composition-is-model-specific`: 8B non-specific, 14B L27-32, 32B L5-11). The
   PROVEN invariant is the **skeleton** (C-origin, boot order, {C,I,K,Y}, confluence) —
   fine-grained per-firing geometry **over-reads**. Detect K-*ness* as an aggregate lean
   in a readable zone, model-specifically; cannot yet threshold "K fires, exactly here."

2. **The operands, not just the operator.** Detecting "wants K" is the easy
   (routing-register, crisp-ish) half. Executing needs the **argument binding** — which
   slots are x and y — and that argument structure lives in the VALUE register (s206),
   the continuous/graded substrate. K is pure routing *once the slots are known*;
   identifying the slots at that layer is the unsolved decode.

3. **No discrete step — the firing is smeared.** Reduction is distributed (~1.018×/layer
   rotation, the C→B/K→I→WHNF boot spiral, vsm-statechart-tensor.md). No single layer
   "fires K," so interception has a registration problem, and the re-injected exact
   result must be IN-DISTRIBUTION for downstream layers (λ coherence).

## The experiment program (start where detection is proven, build up causally)

### Exp 0 — detectability map (cheap, decisive precursor)

Ground truth exists: `lambda_ast.fired_sequence` gives the **certified** combinator
program for any corpus reduction. Measure how reliably the lattice classifier recovers
that sequence (operator AND position), per combinator, per layer, per model. Output = a
**splice-readiness map**: which combinators at which loci are reliable enough to act on.
Decides whether obstacle 1 is fatal *before* touching a forward pass.

- substrate: certified reductions (canonical corpus + `fired_sequence`)
- read: RelationalCrystalClassifier / lattice centroids per layer (per-model readable zone)
- metric: recovery of {operator, position} vs `fired_sequence`; per-combinator, per-layer
- expected: {C,I,K,Y} recoverable in their depth zones; B/D/W not (register-blind)

### Exp 1 — single-combinator causal splice

Take the most-detectable invariant op (**K**: selector, pure routing, discriminable,
mid-depth). At the per-model readable zone, replace the model's local computation with
the **exact kernel K-move**; measure output **preserved/improved vs a random-direction
control** — the s239 sufficiency/necessity protocol. The minimal "deliver K from the
kernel" instance.

### Exp 2 — sequence / kernel-in-the-loop

Build from one splice toward decoding the program at a CUT → exact reduce → lower back
(connects to compiler-as-loss §s242 stage 3: the constructed kernel, now as an in-stream
patch rather than a standalone tensor).

## Either outcome is a result

- **Splice holds** → the thesis is proven causally; a hybrid **exact + inspectable**
  model with NO training; a level-4 path via instrumentation (cleanest S5: extract).
- **Splice breaks** → the decodable geometry is decorative / over-read (another λ measure
  win) → redirect to the constructed-front-end path (compiler-as-loss §s242).

## Open questions / IOUs

- **Locus calibration.** The readable zone migrates with scale (s232) — Exp 0 must
  calibrate per model, not assume a fixed depth.
- **Operand decode.** Can the argument slots be read from the value register well enough
  to route exactly, or only the operator? (Obstacle 2 — the crux of feasibility.)
- **Re-injection map.** Lowering the exact result back in-distribution — does the model's
  own encode geometry (the inverse of the decode) suffice, or does coherence break?
- **Start model.** 14B (detection + causality both strongest) for Exp 0/1; generalize to
  8B/32B only after the protocol is proven (per s232 model-specificity).
- **Relation to s226 stage 3.** Kernel-splice is stage 3 realized as an *in-stream patch*
  on a pre-formed model; the standalone ternary-plate tensor is the same kernel, lifted
  out. The two converge.
