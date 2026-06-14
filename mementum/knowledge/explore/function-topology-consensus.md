---
title: "Function-Topology Consensus — Higher-Order Functions Are Routing Normal Forms, Universal Across Teachers"
status: active
category: interpretability
tags: [reverse-harvest, combinators, higher-order-functions, routing-register, consensus, teacher-agnostic, distributed, normal-form, church-rosser]
related:
  - combinator-function-shape.md
  - compiler-as-loss.md
  - consensus-delta-folding.md
  - combinator-training-beta-reduction.md
  - normal-form-curriculum-partition.md
depends-on:
  - compiler-as-loss.md
created: session 225
---

# Function-topology consensus — higher-order functions are routing normal forms, universal across teachers

> Session 225 (Michael's thread, off the compiler-as-loss debate). s219 showed the
> combinator PRIMITIVES {K I B C S D W Y WHNF} have a universal relational geometry
> across the open-weight ecosystem. Open question: does that hold for COMPOSED
> higher-order functions — `map` (= B(CB)(CB)), `filter`, `fold`, `zip`? If so, the
> distributed pipeline is teacher-agnostic.

## The pivot that motivated the test (Michael)

Two corrections to the s224 compiler-as-loss design (see `compiler-as-loss.md`):

1. **The compiler is a verifier, not the capability teacher.** Diverse big models
   are the better capability teacher — s219 universality came FROM diverse training.
   The compiler's role is to CERTIFY/canonicalize (Church-Rosser → unique normal
   form) and emit exact reduction trees, not to be an impoverished narrow generator.

2. **The pipeline is teacher-agnostic on both halves — IF topology is universal.**
   - **Capability signal:** the β-normal-form / reduction trace is unique by
     Church-Rosser ⇒ ANY sufficiently large model emits the SAME canonical traces.
     Teacher-agnostic *by mathematics*. No experiment needed.
   - **Inventory signal:** teacher-agnostic *iff* the routing topology is universal.
     This is the only empirical question — and the reason it should hold is deep:
     **if a higher-order function exists as a routing NORMAL FORM in the topology,
     its universality follows from the same uniqueness principle as the output's**
     (a normal form is unique). The topology is the β-normal form expressed in the
     routing register instead of in token space. (Ties to
     `normal-form-curriculum-partition.md`.)

   Hypothesis (Michael): most HOFs have the same topology regardless of teacher;
   "which teacher the topology came from" only matters for idiosyncratic HOFs (rare).

## The instrument

`scripts/experiments/function_topology_consensus.py` (register topological/routing).
Probes: `src/verbum/probes/higher_order.py` — 224 last-token-completion probes,
28 each across 8 functions in two groups:

- **Positive controls** (named function ≡ a primitive): `compose`≡B, `flip`≡C,
  `const`≡K, `apply`≡I. These validate the readout.
- **Higher-order tests**: `map`, `filter`, `fold`, `zip`.

Method (extends s219's frame-invariant trick):

```
routing(x)        = sign(FFN gate pre-activation)              # s203 routing register
centroid_f        = mean over f's probes of CMR(routing(x))    # common-mode removed
best layer        = argmax_L silhouette_z(combinators @ L)     # the BASIS must crystallize
fingerprint(f)[j] = cosine(centroid_f, centroid_combinator_j)  # 9-dim, RELATIONAL
                  ⇒ frame-invariant ⇒ comparable across architectures
                    (raw centroids are NOT: sign-corr 0.000 across frames, s219)
consensus(f)      = mean pairwise Pearson of fingerprint(f) across models
null              = permute the 9 combinator entries within each model
classification    = universal (z≥2 ∧ p<.05 ∧ corr≥0.3) | idiosyncratic
```

## Result — 8/8 universal (decisive)

5 models, 3 architectures, 7B–32B: Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B.
`results/function-topology-consensus/consensus.json`.

| function | kind | corr | z | p | consensus top |
|---|---|---|---|---|---|
| const | control(K) | +0.95 | 8.5 | .0002 | **K** ✓ |
| fold | test | +0.93 | 8.6 | .0002 | WHNF, S |
| compose | control(B) | +0.89 | 8.1 | .0002 | D, S, B |
| filter | test | +0.87 | 7.7 | .0002 | K, C |
| zip | test | +0.76 | 6.7 | .0002 | S, WHNF, W |
| flip | control(C) | +0.75 | 6.8 | .0002 | **C** ✓ |
| map | test | +0.72 | 6.5 | .0002 | D, C, B |
| apply | control(I) | +0.67 | 5.9 | .0002 | C, B |

**All 8 universal, 0 idiosyncratic.** Every HOF's cross-model fingerprint clears the
permutation null decisively. Topology of higher-order functions is universal across
teachers/architectures — extends s219 (primitives) up to composed HOFs. ⇒ Michael's
hypothesis confirmed; the extract→fold→compiler pipeline is teacher-agnostic.

## Secondary — the HOF fingerprints are semantically coherent

Without supplying any label for the test functions, their consensus fingerprints land
on the right primitives by meaning, consistently across all 5 models:

- **fold → WHNF, S** — fold reduces a sequence to a single TERMINAL value; WHNF is the
  terminal combinator. The only HOF with a POSITIVE top loading (+0.05).
- **filter → K** — filter is selection; K is select/discard.
- **zip → S, W** — zip is fork-join of two streams (S, applicative) with sharing (W).
- **map → D/C/B, Y dead last** (B −0.18, C −0.07, **Y −0.29**). Map routes through
  COMPOSITION, never recursion — across every model. The s219 prediction
  (`map=B(CB)(CB)`, "attention-over-positions IS the fold") holding at the topology
  level.

## Caveat — agreement decisive; the decode only suggestive (λ measure)

Honest scope, not oversold:

- Two of four controls hit argmax clean (`const→K`, `flip→C`). `compose→D` is a
  near-miss IN the composition family (D = fused B∘B∘B; B is #2–3). **`apply→C` is a
  genuine miss.**
- Absolute cosines are near-zero/negative — agreement is on the SHAPE of the
  relational fingerprint (robust, corr up to 0.95), not on crisp positive loadings.
  Same register subtlety as s219 ("above chance, not crisp"; negative absolute
  silhouettes).

⇒ **Topology-universality is decisive** (it is about cross-model agreement, p=.0002
everywhere — untouched by the caveat). **The combinator-DECOMPOSITION readout is
suggestive and needs refinement** (a better readout than argmax-cosine, or the s219
absolute-frame issue). The `apply` miss + negative loadings are the IOU.

## Implications

- **Distributed training:** the consensus topology is a shared, frame-invariant
  reference for the FOLD (inventory) that needs no designated teacher; the capability
  signal needs no teacher either (Church-Rosser). The s224 fold dream — "nothing to
  ship, everyone agrees on both the WHAT and the geometry" — is supported for HOFs.
- **Compiler-as-loss:** confirms the verifier framing. Any model can be the
  output-trace oracle; the consensus topology is the inventory target.

## Open leads

1. **Refine the decode** (the real IOU): the `apply` miss + negative loadings. Try a
   readout better than argmax-cosine (e.g. align absolute frames, or a learned linear
   map from fingerprint → combinator decomposition).
2. **Does the model USE these HOF topologies on natural prose?** (next experiment).
   The s225 measurement is on curated probes; verify the HOF routing signature is
   recruited when the model processes ordinary prose that implicitly requires the
   function — detection (projection on minimal-pair natural prose) + causal ablation.
3. **More HOFs / more architectures** — extend beyond the 8 functions; add non-gated
   (Pythia) above the floor for a fuller architecture spread.

## Files

- Probes: `src/verbum/probes/higher_order.py`
- Instrument: `scripts/experiments/function_topology_consensus.py`
- Runner: `scripts/experiments/run_function_topology.sh`
- Results: `results/function-topology-consensus/` (`<model>.json/.npz`, `consensus.json`)
