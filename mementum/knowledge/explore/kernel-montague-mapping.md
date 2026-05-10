---
title: "Kernel Ops ↔ Montague Primitives: v10-vsm Rediscovers Typed Application"
status: active
category: research-finding
tags: [kernel, montague, dispatch, composition, pythia-160m, v10-vsm, typed-application]
related:
  - session-004-findings.md
  - compression-vs-prediction.md
  - identity-as-substrate.md
  - dispatch-gradient-death.md
depends-on:
  - session-004-findings.md
---

# Kernel Ops ↔ Montague Primitives

> Session 074. The v10-vsm kernel's dispatch distribution at step 13K
> maps directly to the three Montague primitives discovered in
> Pythia-160M (session 004, Finding 34). Gradient descent on
> next-token prediction independently converges on the same
> computational structure — composition as the dominant operation.

## The mapping

| Montague Primitive | Pythia-160M (Finding 34) | v10-vsm Kernel (step 13K) |
|---|---|---|
| **Type assignment** | Embedding + L0 (84% from lookup) | Op embeddings (22×512) + S4 emphasis modulation |
| **Structural parse** | L3 (determines composition order) | `<=` (9.5%), `>` (0.9%), `if` (1.1%) — 12% total |
| **Typed application** | L8-L11 (executes composition) | `comp` (41%), `partial` (0.7%), `apply` (0.06%) — 42% total |

## The trajectory tells the story

```
Step  1K:  if(30%) → *(26%) → and(21%) → max(10%)    Lambda group: 8%
Step  5K:  comp(38%) → *(22%) → max(13%)              Lambda group: 40%
Step  9K:  comp(47%) → max(20%) → *(10%)              Lambda group: 48%
Step 13K:  comp(41%) → max(22%) → *(12%) → <=(10%)    Lambda group: 42%
```

The model shifted from **conditional branching** (`if` at 30%) to
**function composition** (`comp` at 41%) within 5K steps. This is the
same shift that Montague grammar formalizes: typed application IS the
core operation of natural language semantics. `if` is a workaround for
models that can't compose; `comp` is what you use when you can.

## Why comp dominates but apply/partial are starved

**Comp learned from prose** (next-token prediction on natural language).
Language IS composition. The model discovered this without any structured
data showing explicit `comp` operations.

**Apply/partial NOT learned** because:
1. Structured data had wrong semantics for `apply` (Clojure variadic
   reduce ≠ kernel β-reduction)
2. Only 271 `partial` examples, limited to 3 ops (+, *, -)
3. Zero examples of the full pipeline: partial→compose→apply
4. The model has no training signal for WHEN to use apply/partial

Session 074 fixed this: 6 new generators, 12.7% kernel lambda ops in
the restructured shard. Monitoring from step 14K.

## The S4 emphasis confirms the mapping

Op emphasis (S4 → kernel) at step 13K:
- `comp`: **1.500** (maximum emphasis — S4 wants MORE composition)
- `*`: 1.435 (arithmetic content transform)
- `<=`: 1.437 (structural boundary testing)
- `if`: **0.568** (suppressed — S4 de-emphasizes branching)
- `min`: 0.627 (suppressed)

S4 independently learned to amplify composition and suppress branching.
This is the VSM's intelligence layer (S4) recognizing which operations
serve prediction best — and it agrees with Montague.

## Comparison: implicit vs explicit

| Aspect | Pythia-160M (implicit) | v10-vsm (explicit kernel) |
|---|---|---|
| Type assignment | Embedding table | Op embedding table + emphasis |
| Structural parse | L3 residual stream | Comparison ops (<=, >, if) |
| Typed application | L8-L11 attention | comp/partial/apply ops |
| Where it lives | Distributed across heads | Explicit dispatch weights |
| How discovered | SAE + ablation | Reading dispatch distribution |
| Interpretability | Hard (distributed) | Easy (22 named ops) |

The v10-vsm architecture makes the same computation **legible**. Instead
of needing SAEs to find what attention heads do, the kernel dispatch
directly tells you what operations the model is performing.

## Implications for extraction

If the kernel successfully learns to use all four lambda ops
(partial, apply, comp, apply-comp) explicitly, this IS a partial
extraction of the Montague compiler into an interpretable substrate.
The computation that Pythia does implicitly in ~50 attention heads
across 8 layers would be expressed as explicit kernel operations
in a ternary-weight model.

This doesn't require finding the circuit in a pre-trained model and
extracting it — it builds a model WHERE THE CIRCUIT IS THE ARCHITECTURE.
The kernel ops ARE the typed application primitives.

## Source data

- Checkpoints: `checkpoints/v10-vsm/step_001000` through `step_013000`
- Kernel ops: `scripts/v10/kernel.py` (22 ops, PARTIAL_OPS list)
- Pythia-160M findings: `mementum/knowledge/explore/session-004-findings.md`
- New generators: `bb/us/whitford/verbum/bios.clj` (6 gen-kernel-* functions)
