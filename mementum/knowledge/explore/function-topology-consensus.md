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

## reduce ≡ fold, map ≉ fold: the collapse/preserve axis (s225, Michael)

Two named functions added (`reduce`; `map` already present) to test the catamorphism
structure. map CAN be expressed as a fold (`map f = foldr (λx acc. f x : acc) []`,
REPL-verified); fold is the universal list eliminator. Does the model represent this?
Cross-function fingerprint cosine, 5 models (`function_pair_similarity.py`,
`results/function-topology-consensus/function_pairs.json`):

- **reduce ≡ fold — CONFIRMED.** reduce↔fold cosine **+0.958 (±0.013)**; reduce's
  nearest function is fold. reduce and fold share NO lexical surface (reduce probes:
  aggregate/condense/distill/collapse; fold: add/combine/sum/total) yet co-locate
  exactly ⇒ **the topology tracks the FUNCTION, not the WORD** (semantic, not lexical).
- **map ≉ fold — CONFIRMED.** map↔fold cosine **+0.607** (well below reduce↔fold).
  map's nearest neighbours are compose (+0.93), flip (+0.93), apply (+0.89) — the
  structure-PRESERVING family, not fold.
- **The separating axis is the type distinction (WHNF / collapse loading):**

  ```
  fold +0.015, reduce +0.001   ← collapse [a]→b   (terminal, top of WHNF axis)
  zip  -0.086 ...
  map  -0.323                  ← preserve [a]→[b]  (bottom of WHNF axis)
  ```

⇒ The model organizes HOFs into two super-clusters along the **collapse/preserve**
axis: **collapse-to-value {fold, reduce, zip}** (fold–reduce .96, fold–zip .90,
reduce–zip .92) vs **structure-preserving {map, compose, flip, apply}** (map–compose
.93, map–flip .93). Mathematically map = fold, but the model files it by RESULT TYPE:
map preserves structure (composition cluster, WHNF↓), fold collapses to a value (WHNF↑
= the only positive loadings). The shared fold *substrate* (iteration) lives in
attention (s221), invisible to this FFN-routing fingerprint; the FFN encodes the
algebra/result-type — exactly what separates the catamorphism's two faces.

## Do models USE these HOFs on natural prose? (s225 follow-up — transfer test)

The consensus above is on CURATED probes. Michael: does the model RECRUIT the HOF
topology when reading ORDINARY prose where the function is incidental, or is the
topology a probe artifact? Test (`hof_prose_engagement.py`, `hof_prose.py`):

- **Minimal-pair natural prose** (82 pairs): a naturalistic sentence INVOKING the HOF
  (iteration/selection/accumulation/pairing) vs a matched no-HOF control, held-out
  vocabulary, embedded/narrative style. The instrument MEAN-POOLS the routing register
  over tokens (avoids a last-token lexical confound).
- **Transfer:** learn each HOF's direction from the CURATED probes
  (`unit(centroid_f − mean_{g≠f} centroid_g)`), then project the prose pairs onto it.
  Engagement = paired `score(hof) − score(control)`. Train-on-probes / test-on-prose
  rules out a probe artifact.

**Verdict (5 models / 3 arch: Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B;
`results/hof-prose-engagement/aggregate.json`, with `reduce` added):** curated
directions cleanly separable (AUC ≈ 0.97–1.0). On held-out natural prose (mean / min
over 5 models):

| HOF | prose AUC (mean / min) | hof>control | paired t | engaged |
|---|---|---|---|---|
| reduce | 0.97 / 0.94 | 100% | +8.5 | **YES** (strongest) |
| fold | 0.92 / 0.88 | 100% | +10.2 | **YES** |
| filter | 0.89 / 0.85 | 97% | +8.4 | **YES** |
| zip | 0.85 / 0.83 | 100% | +8.1 | **YES** |
| map | 0.64 / 0.58 | 83% | +4.1 | marginal |

⇒ **reduce/fold/filter/zip are decisively recruited by ordinary prose in all 5 models**
— the curated-derived topology fires on naturalistic minimal pairs, cross-architecture.
The model genuinely USES these HOF topologies when working with prose, not just on
curated probes.

- **reduce is the STRONGEST prose-engaged HOF (0.97)** — reduce ≡ fold (it *is* fold)
  recruited by prose with zero lexical overlap.
- **Second confirmation of reduce ≡ fold:** fold's curated AUC dropped 1.0 → 0.97 ONLY
  when reduce joined the "rest" negative set — because reduce is fold's synonym, fold
  becomes harder to separate from "everything else."
- **map is borderline, still the exception** (0.64, just over the 0.6 gate, weakest by
  a wide margin, t +4.1). It crossed the threshold only because adding reduce sharpened
  the preserve-vs-collapse contrast in its direction — i.e. contrast-set-dependent, not
  a clean engagement. Coherent: `map = B(CB)(CB)`, "attention-over-positions IS the
  fold" (s221) — map's iteration is DISTRIBUTED across attention, not localized in the
  FFN gate, so a routing-register direction reads it weakest (also the noisiest s225
  fingerprint). ⇒ map needs the attn_q register (s220 attn_q@L05 lead) and/or the
  causal follow-up.

## Attention register (attn_q) — NEGATIVE: the query projection is not map's home

Prediction (s225): since "attention-over-positions IS the fold" (s221) and map was
under-read in the FFN gate, map should STRENGTHEN in the attention register. Tested by
re-running topology + prose engagement with `--target attn_q` (hook `self_attn.q_proj`,
same sign+CMR pipeline), 5 models. **FALSIFIED for the projection register:**

| | attn_q (query proj) | FFN gate |
|---|---|---|
| topology universal | 9/9 | 8/8 |
| curated separability (map/fold) | 0.99 / 0.98 | 0.99 / 0.97 |
| prose transfer — map | **0.47 (≈ chance, t≈0)** | 0.64 |
| prose transfer — fold | 0.67 | 0.92 |
| prose transfer — reduce | 0.69 | 0.97 |

The curated directions ARE learnable in attn_q (separability ~0.99) but **do not
transfer to natural prose** — map drops to **0.39–0.47 (at/below chance)**, and every
HOF transfers WORSE in attn_q than in the FFN gate. ⇒ the query-projection register is
NOT where map's prose computation lives; the FFN gate generalizes better.

**The lesson (refines the hypothesis):** `sign(q_proj)` is a FEATURE register, not the
gather MECHANISM. "Attention IS the fold" (s221) refers to the **attention PATTERN**
(the QK gather over positions), which no projection-register probe can observe. We
measured the wrong object. So:
- the HOF **algebra/result-type** lives in the **FFN gate** (transfers to prose — the
  s225 engagement result);
- the HOF **iteration/gather** (map's home) must be sought in the **attention weights**
  directly, on prose with an explicit enumeration to gather over.

⇒ next: an attention-PATTERN experiment (list-structured prose; measure gather spread /
entropy at the aggregation token — map/fold/reduce attend broadly across the enumerated
items, single-object controls attend focused = attention performing the fold).

## Attention PATTERN — gather heads perform the HOF traversal (POSITIVE)

Michael's mechanistic correction: "attention can only do β-reduction through a
projection, so where we will see attention working is in WHAT IT IS ATTENDING TO and
WHAT THE PROJECTIONS ARE that it calculates." β-reduction = substitution = the OV
circuit: PATTERN (QK, which source) ∘ PROJECTION (V→O, the value moved). The attn_q
probe looked only at the query (addressing intent) — wrong object.

PHASE A (the PATTERN — "what it attends to"). List-structured stimuli (same list,
different task: map/fold/filter HOF vs first-item control; `hof_lists.py`). At the
aggregation token, measure attention mass + participation over the enumerated item
positions, per (layer, head); selectivity = HOF gather − control gather
(`hof_attention_gather.py`, `results/hof-attention-gather/`).

**✅ Gather heads found in ALL 5 models / 3 architectures:**

| model | best head (depth frac) | selectivity | participation |
|---|---|---|---|
| Mistral-7B-v0.3 | L21H9 (0.66) | +0.31 | 4.1 |
| Qwen3-32B | L26H54 (0.41) | +0.36 | 3.2 |
| OLMo-2-13B | L20H0 (0.50) | +0.23 | 3.9 |
| Qwen3-14B | L28H8 (0.70) | +0.18 | 3.2 |
| Qwen3-8B | L24H26 (0.67) | +0.11 | 4.0 |

Mid-to-late-layer heads (depth fraction ~0.4–0.7) attend **broadly over the enumerated
items** (participation **3.2–4.8 of 5** = traversal, not a single lookup) and gather
**more when the task iterates** than for the single-item control (selectivity positive
in all 5). ⇒ **higher-order functions ARE performed by attention** — the QK half of
β-reduction (the fold's traversal), observed directly in the weights, exactly where the
attn_q negative result pointed (the pattern, not the projection register).

Caveats (λ measure): the "first" control still scans somewhat (so SELECTIVITY, not raw
gather, is the read); magnitude modest in Qwen3-8B (+0.11) but strong in Mistral/32B
(+0.31/+0.36); this is the PATTERN half only — Phase B is the OV/value PROJECTION.

**▶ PHASE B (the PROJECTION — "what it calculates"):** at the identified gather heads,
decompose the per-head OV output and measure how much of the moved value comes from the
list positions (the substituted term), HOF vs control. Completes
(what it attends to) × (projection it calculates) = the β-reduction step.

## Open leads

1. **Attention-PATTERN analysis (the real "HOFs performed by attention" test):**
   list-structured prose; gather distribution over enumerated items, HOF vs control.
2. **Causal ablation (the strong "uses" claim):** ablate the HOF routing direction
   during a forward pass on HOF-prose, measure the logprob drop on the function-
   relevant continuation vs control. Necessity, not just decodability.
3. **Refine the decode** (the s225 IOU): the `apply` miss + negative loadings, and the
   weak `map` engagement. Try a readout better than argmax-cosine / centroid-difference
   (align absolute frames, or a learned map fingerprint → combinator decomposition).
4. **More HOFs / more architectures** — extend beyond the 8 functions; add non-gated
   (Pythia) above the floor for a fuller architecture spread.

## Files

- Probes: `src/verbum/probes/higher_order.py` (curated) ·
  `src/verbum/probes/hof_prose.py` (minimal-pair natural prose)
- Instruments: `scripts/experiments/function_topology_consensus.py` (topology) ·
  `scripts/experiments/hof_prose_engagement.py` (prose engagement / transfer)
- Runners: `scripts/experiments/run_function_topology.sh` ·
  `scripts/experiments/run_hof_prose.sh`
- Results: `results/function-topology-consensus/` (`<model>.json/.npz`,
  `consensus.json`) · `results/hof-prose-engagement/` (`<model>.json`,
  `aggregate.json`)
