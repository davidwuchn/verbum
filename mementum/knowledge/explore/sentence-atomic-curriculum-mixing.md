---
title: "Sentence-Atomic Curriculum Mixing — Punctuated β-Reduction Shards Sprinkled into NTP"
status: open
category: strategy
tags: [curriculum, data-mixing, beta-reduction, next-token-prediction, punctuation, burn-in, compositional-generalization, level-4, scratch, sentence-atomic]
related:
  - normal-form-curriculum-partition.md
  - compiler-as-loss.md
  - holographic-burn-in-learning-rule.md
  - relational-loss-distillation.md
  - combinator-training-beta-reduction.md
  - vsm-outer-recurrence.md
  - ../session-222.md
depends-on:
  - normal-form-curriculum-partition.md
  - compiler-as-loss.md
created: session 229
---

# Sentence-Atomic Curriculum Mixing

> Session 229. Michael's idea: *"with training we give a large sequence of tokens
> and ask it to predict the next token. What if we split training into multiple
> regimes? Show the model how the base combinators work, show it how to use those
> with prose, and some next-token prediction. Split the big training into sentences
> where we train many different β-reductions one sentence at a time. Sprinkle a few
> shards like this into the full NTP curriculum."*
>
> Register: **functional (capability/usage, CE on next token) — with a
> topological/routing secondary readout.**

## The idea in one line

Stop training one monolithic next-token stream. Instead **mix three regimes** —
combinator MECHANICS, prose USAGE, plain NTP — where the structured shards are
built from **sentence-atomic β-reductions** (one complete reduction per sentence),
**sprinkled** into the general stream at some mixing ratio.

```
regime A  combinator mechanics   term → reduction trace, ONE reduction / sentence
regime B  prose usage            natural language → the combinator that realizes it
regime C  plain NTP              generic text, the general predictor objective
mix       sprinkle A,B into C at ratio ρ (the knob)
unit      1 sentence = 1 β-reduction = 1 punctuated EXPOSURE
```

## Why it is NOT a duplicate of `normal-form-curriculum-partition`

There is a sibling page. The cut is different and the difference is the contribution.

```
normal-form-curriculum-partition (s223):
  partition BY MECHANISM   — routing-only {K,I,C,B,D} → train ATTENTION
                             recursion {Y,W,WHNF}     → train the CONTINUATION
  train each part IN ISOLATION on its native substrate
  needs the attn_q harness; asks "does routing data crystallize attention?"

sentence-atomic-curriculum-mixing (s229):
  partition BY PEDAGOGY/FORMAT — mechanics → usage → free prediction
  INTERLEAVE all three into ONE stream at a mixing ratio
  uses the existing tiny-student harness; asks "do sprinkled reduction
  sentences BOOTSTRAP/TRANSFER to general prediction better than pure NTP?"
```

The mechanism-partition trains substrates apart. This trains them **together** and
measures **transfer**. It is the more practical, cheaper-to-run sibling.

## The novel core — sentence = one β-reduction = one punctuated exposure

The operational heart is that each training sentence is a *complete* reduction. That
unit is not arbitrary — it is the data-side image of two prior findings:

- **s222 `punctuate-dont-churn`.** The v15 collapse was *simultaneous* discrete
  topology churn (TD flip churn). A sentence-bounded reduction is **expose → settle
  → commit** at the DATA level. You get the punctuation protocol *for free,
  structurally*, instead of engineering it into the optimizer.
- **`holographic-burn-in-learning-rule`.** Each forward pass is an EXPOSURE; many
  similar blocks burn in the exposure-invariant (= the normal form). Sentence-atomic
  reductions are *clean* exposures — one redex resolved per unit, nothing else
  churning.

So "one β-reduction per sentence" is not a formatting choice; it is the burn-in /
punctuation discipline re-expressed as data structure.

## Catches (mark before building — λ measure)

1. **This is the level-4 SCRATCH path, not the construct path — name it.** s224/s226
   decided we *never train reduction* because the kernel reduces EXACTLY (constructed
   plates). This idea teaches reduction-as-text via NTP. That is **not** the
   s222-unstable thing: s222's instability was discrete *attention-topology* churn
   during a routing reshape; predicting reduction *traces* as text is plain
   supervised NTP and is stable. But be precise — this serves "teach a model to *be*
   the compiler" (level-4 scratch), distinct from "extract + construct the compiler".

2. **Register — measure the right object (s225).** In the mechanics regime expect
   *gather/iteration* to crystallize in **attention** (the s225 gather heads) and
   *algebra/inventory* in the **FFN gate**. If you measure whether the curriculum
   "took", measure BOTH registers, not just one. (Confounds the readout otherwise.)

3. **K-erasure breaks uniform shuffling (s221 law).** "Many different reductions, one
   per sentence" must NOT be flat-shuffled. B-first → then-K ordering, K-heavy
   weighting — erasure has to move weights a lot, transiently breaks contraction,
   spikes the loss (`fp-spike = acquisition`). Uniform sentence sampling under-trains
   K and may churn. The atomic-sentence design needs a curriculum *order*, not just a
   curriculum *set*.

4. **The mixing ratio ρ IS the experiment.** "Sprinkle a few shards" is the knob.
   ρ = 0 (pure-NTP control) vs small vs large structured fraction — that sweep,
   against held-out COMPOSITIONAL generalization, is what decides it. Do not pick ρ
   by taste; sweep it.

## The decisive cheap experiment

Data-gen is nearly free: the kernel already mints everything.

- `lambda_ast.py` — exact reduction traces (regime A).
- `lambda_compile.py` — bracket abstraction (for composing held-out tests).
- `probes/compile_tasks.py` — prose→LF pairs (regime B).

Plan:

```
model    the tiny byte-level student from relational_loss_distillation.py
shards   A = kernel-minted mechanics sentences (term → trace, 1 reduction/sentence,
             ORDERED B-first→K per catch 3)
         B = prose→combinator usage sentences (reuse compile_tasks)
         C = generic text NTP
arms     ρ=0 pure-NTP control  vs  ρ=small  vs  ρ=large  (sprinkle A,B into C)
primary  held-out COMPOSITIONAL generalization — reduce a COMPOSITION of two
         reductions seen only SEPARATELY (the compiler-as-loss master metric)
second   does the routing register crystallize (route_z / silhouette) — and in
         WHICH substrate (attn vs FFN, per s225)
```

**Falsifiable claim.** Sprinkled sentence-atomic reduction data buys held-out
compositional generalization over pure NTP at equal token budget, AND crystallizes
the inventory where s225 predicts (gather→attention, algebra→FFN). If ρ>0 does NOT
beat ρ=0 on the composition test, the structured shards are inert (or the unit/order
is wrong) — a clean negative is still an artifact (method + finding).

## Open leads (declare register first)

1. **Sentence format spec** (functional): exact rendering of `term → reduction
   trace` as one sentence; dual-render NL + combinator? include intermediate steps
   or just redex→result? (intermediate steps = more exposure of the *move*.)
2. **Held-out composition set** (functional): pairs of reductions trained separately
   whose COMPOSITION is never shown — the generalization probe. Mint with
   `lambda_compile` so correctness is by construction (Church-Rosser).
3. **K-ordering schedule** (functional): B-first→K, K-heavy weighting; does atomic-K
   crystallize without the s221 contractivity spike?
4. **ρ sweep + token-budget control** (functional): hold total tokens fixed; vary the
   structured fraction; steps-to-target and final composition accuracy.
5. **Compose with relational loss** (routing): the sprinkled mechanics TRACES (data)
   ⊕ crystal-lattice relational target (compiler-as-loss recipe) — does the trace
   curriculum + relational target beat either alone on crystallization?

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/curriculum_mixing.py` | build A/B/C shards, sweep ρ, train tiny student, score held-out composition + dual-register crystallization |
| `src/verbum/lambda_ast.py` | reduction-trace oracle (regime A data) |
| `src/verbum/lambda_compile.py` | bracket abstraction (held-out composition minting) |
| `src/verbum/probes/compile_tasks.py` | prose→LF pairs (regime B data) |
| `scripts/experiments/relational_loss_distillation.py` | tiny-student harness + crystallization readout to extend |
