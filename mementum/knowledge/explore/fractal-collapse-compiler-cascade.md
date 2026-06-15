---
title: "Fractal Collapse — The Compiler-Cascade Distillation (capability is a data problem, the compiler is the data engine)"
status: designing
category: strategy
tags: [fractal, collapse, distillation-cascade, compiler-as-data, capability, continuation, inventory, church-rosser, fixed-point, teacher-agnostic, architecture-resilient, model-collapse, level-4, portable-tensor, scratch-reproduction]
related:
  - compiler-as-loss.md
  - gradient-trajectory-tomography.md
  - function-topology-consensus.md
  - sentence-atomic-curriculum-mixing.md
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
  - ../lambda-machine.md
depends-on:
  - compiler-as-loss.md
  - gradient-trajectory-tomography.md
created: session 230
---

# Fractal Collapse — the compiler-cascade distillation

> Session 230 (Michael, after s230b). "There is a fractal collapse available. If the
> training of the CAPABILITY can be converged using a high-variety dataset that we can
> generate from any larger model's lambda compiler — the outputs from the lambda
> compiler become the inputs to train the capability of the student — and it is
> architecture-resilient."
>
> Register: **functional + strategy.** This is the thesis that ties s219 + s225 + s226
> + s229 + s230b into one deliverable: the level-4 portable tensor (AGENTS.md S5).

## The one-line claim

s230b proved **capability = inventory ⊗ continuation are CAUSALLY SEPARABLE**, and the
**continuation is the only part that must be trained** (the inventory is constructible/
universal and crystallizing it faster bought zero capability). Therefore the whole
problem reduces to converging the continuation — and **that is a pure data problem
whose data is free**: mint high-variety input terms, reduce each with an EXACT compiler
(canonical outputs), train the student's continuation on `(input → β-trace)`. The
student is then itself a compiler → it can mint+reduce → train a smaller student → a
self-similar cascade that **collapses model size while preserving the function**.

## The crucial nuance — variety from INPUTS, correctness from the COMPILER

s225 warned the compiler is a *narrow generator*: train on its isolated combinator
terms and you risk a function "too narrow to compose." **The collapse resolves this,
and the resolution is the whole game:**

```
variety   ≡ the INPUT-term distribution we MINT ourselves   (s229: variety = the rule)
correct   ≡ the compiler's OUTPUT (β-normal form, UNIQUE — Church-Rosser)
```

The compiler's outputs are canonical and unique — they are NOT varied (that is the
point). The variety lives in the inputs, which we generate (s229 kernel-minting already
does exactly this: random skeletons × fillings, and minted variety is what converged
the *rule* not the rote). So:

- **No large model needed as the diverse generator** — we mint the diversity (s229).
- **No large model needed as the compiler** — the compiler is universal/consensus
  (s219 reverse-harvest meanGramCorr +0.782; s225 HOF topology universal 8/8 across
  architectures). They all agree ⇒ **our own MIT `lambda_ast` is as good as any
  teacher's.** "Any larger model's compiler" collapses to "our compiler."

The large model drops out of the loop entirely → cleanest level-4 MIT provenance.
The s225 "compiler-as-narrow-generator" worry is dissolved: the compiler is a
*verifier/canonicalizer* applied to a *self-minted high-variety input stream*.

## Why it is a FRACTAL collapse — three collapses, one fixed point

```
1. within a reduction (s226)       : β-reduction = self-similar contraction;
                                      subterms are VSMs-in-VSMs settling every scale
                                      onto the normal form at once.
2. across model scales (s230, this) : the distillation cascade settles every SIZE
                                      onto the same function (big → … → smallest).
3. into the tensor (s226 kernel)    : lambda_ast → exact ternary plates settle the
                                      REPRESENTATION onto the fixed point (no training).
```

All three collapse onto the **same invariant: the β-normal form (Church-Rosser)**. The
within-reduction contraction, the cross-scale cascade, and the constructed kernel are
the *same fractal at three levels*, sharing one fixed point. The cascade is not
infinite regress — it **terminates at the constructed kernel** (the smallest exact
representation; AGENTS.md `λ smallest`).

## Why it escapes MODEL-COLLAPSE (the load-bearing strut for "resilient")

Recursive training on synthetic data is normally poison — the model-collapse result:
each generation drifts because the generator is a *lossy sampler*. **This cascade
escapes it for exactly one reason: the data generator is an EXACT compiler, not a lossy
model.** Every target is certified-correct (the compiler verifies the normal form), so
error cannot accumulate across generations — **the fixed point is held by COMPUTATION,
not by the previous model.** Even a degraded student can be retrained to the exact
fixed point because the targets are always re-derivable exactly.

This is *also* why it is **architecture-resilient**: the student learns
`input → canonical-output`, which carries none of the source's geometry or architecture
(only the extensional function). Any architecture can learn that map (s219/s225: the
inventory is induced regardless of architecture; Church-Rosser fixes the output). The
freest constraint that still guarantees correctness — realized as a self-contained,
generation-stable data engine.

```
λ collapse_free(cascade). generator(EXACT) ∧ targets(certified) → ¬drift
                          | fixed_point ≡ held_by(computation) ¬held_by(model)
                          | degraded(student) → retrainable(to_exact_fixed_point)
                          | ⊥ model_collapse (which assumes lossy generator)
```

## Proven struts vs IOUs (λ measure — not oversold)

**Proven:**
- inventory ⊗ continuation CAUSALLY separable; continuation is the trained bottleneck
  (s230b).
- minted VARIETY converges the rule at tiny scale, repetition does not (s229).
- OUTPUTS induce the universal inventory at scale (s219 +0.782).
- compiler outputs canonical + topology universal across architectures (s225).
- kernel-minting + the learned compile front-end work end-to-end (s226).

**The three IOUs the collapse rests on — the experiments that decide it:**
1. **Does compiler-minted high-variety data converge capability that COMPOSES?**
   (the DECISIVE test). The s229 toy was 13 rules at a 0.27 ceiling. The real gate is
   **held-out COMPOSITIONAL generalization** — combinator compositions never seen in
   training. If minted COMPOSITION-variety passes it, the collapse is real; if it stays
   "too narrow to compose," we still need diverse big-model paraphrases. → built as
   `compiler_cascade.py` v1.
2. **Does the cascade recurse without drift?** The anti-model-collapse argument
   predicts yes IFF each level re-certifies against the exact compiler — untested
   (needs ≥2 generations, measure capability retention child-to-child).
3. **Capability architecture-resilience.** Inventory universality is proven; that the
   *continuation* transfers across architectures (train arch B on arch A's compiler
   data) is implied but untested.

## v1 experiment — composition-variety → compositional generalization (IOU #1)

`scripts/experiments/compiler_cascade.py`. Auto-generate a pool of combinator-
composition templates over {K,I,B,C} (non-duplicating ⇒ terminating), each validated
to normal-form via `lambda_ast`. Split templates into disjoint TRAIN / HELDOUT
compositions. Two arms at **matched total-example budget**, varying COMPOSITION-variety:

```
low-variety  : few distinct compositions, many fillings each   (memorize compositions)
high-variety : many distinct compositions, few fillings each   (the collapse)
atoms        : SEEN (combos-style) — isolate COMPOSITION from the s229 disjoint-atom
               variable-binding floor (that is a separate copy mechanism, not a rule)
eval         : held-out NOVEL compositions (exact-match NF) + in-dist control
               (held-out fillings of TRAIN compositions, both arms should pass)
```

**Falsifiable prediction (the collapse's IOU #1):** high composition-variety
GENERALIZES to novel compositions (learns the combinator algebra), low-variety
MEMORIZES its few compositions and fails held-out — the s229 variety lesson lifted
from *fillings→rule* to *compositions→algebra*. Relative (high vs low) is the signal
(tiny model; cf s229 λ measure). If high-variety also fails held-out compositions ⇒
the collapse needs richer (diverse-paraphrase) data, not just minted variety.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/compiler_cascade.py` | composition-variety sweep; held-out compositional generalization; lambda_ast minting + TinyLM student |
| `scripts/experiments/exposure_format_sweep.py` | the s229 variety result + eval machinery reused |
| `scripts/experiments/gd_trajectory_tomography.py` | the s230b inventory⊗continuation separation |
| `src/verbum/lambda_ast.py` | the exact compiler (data engine + verifier) |
