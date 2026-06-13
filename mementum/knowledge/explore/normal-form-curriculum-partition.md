---
title: "Normal-Form Curriculum Partition — Routing-Only Forms Train Attention, Recursion Trains the Continuation"
status: open
category: strategy
tags: [curriculum, normal-form, routing, attention, recursion, continuation, lambda-compiler, self-teaching, basis, stride, distributed]
related:
  - relational-loss-distillation.md
  - combinator-training-beta-reduction.md
  - consensus-delta-folding.md
  - vsm-outer-recurrence.md
  - recursion-mirrors.md
  - fractal-stride-bands.md
  - ../function-discovery.md
  - ../fibonacci-strides.md
  - ../two-registers-of-topology.md
  - ../session-222.md
depends-on:
  - combinator-training-beta-reduction.md
  - relational-loss-distillation.md
created: session 223
---

# Normal-Form Curriculum Partition

> Session 223. Michael's idea: *"create the training data using the lambda
> compiler for the shared normal forms, and also the routing-only normal forms to
> train attention."*
>
> The key recognition: **"shared normal forms" and "routing-only normal forms" are
> the SAME cut, approached from two directions** — and it is the cut the project
> has now hit three independent times. Curriculum should be designed *along the
> grain of the basis*: generate routing-realizable normal forms to train ATTENTION,
> leave recursion to the CONTINUATION, and treat the universal skeleton as the
> shared/foldable core.
>
> Register: **topological/routing + functional**.

## The convergence — three findings, one partition

```
s219 (universality):  composition/selection skeleton {B,D,S}/{K,I,C} binds
                      UNIVERSALLY (+0.78); recursion {Y,W,WHNF} is the RESIDUAL
                      (map = B(C B)(C B) has no Y; attention-over-positions IS the fold)
s221 (mechanism):     beta-reduction = substitution = an attention MOVE
                      selection {K,I,C} = affine, ONE pass; composition {B,D} linear
                      (S duplicates); recursion {Y,W,WHNF} needs the OUTER RECURRENCE
                      (no single attention move)
s222 (basis):         routing ⊕ continuation = COMPLETE basis
                      routing rules composition; the continuation IS recursion
```

All three name the same boundary:

```
{selection, composition}  ≡  routing-realizable  ≡  shared/universal   → train ATTENTION
{recursion}               ≡  the residual        ≡  needs continuation → train CONTINUATION
```

So Michael's two curricula are one set viewed twice (universality + mechanism), and
the deliberate *complement* (recursion) is exactly what to EXCLUDE from the
attention curriculum. This is curriculum design as the data-side image of s222.

## The curricula (concrete)

```
Curriculum A — ATTENTION (routing-only normal forms):
  combinators {K, I, C, B, D} (+ S with care) — each beta-reduction IS a
  cross-position move. Generate (from the lambda compiler): diverse input terms →
  reduction trace rendered as the ROUTING move (which position selects/copies/
  composes which). By construction INSIDE attention's expressive class (= application).
  EXCLUDE Y, W, WHNF (no single move). Target register: attention routing (attn_q
  sign), NOT the FFN gate.

Curriculum B — SHARED / FOLD (universal skeleton):
  the high-consensus harvest edges B–D, B–C, K–C, S–D, S–Y (s219 prescription).
  Generate diverse I/O for the part the whole ecosystem agrees on → fold into base /
  transfer cheaply (it is the universal layer; see consensus-delta-folding §honest-catch).

RECURSION {Y, W, WHNF}:
  NOT trained by data — trained by the contractivity/fixed-point CONTINUATION
  (optionally fed the reduction-step trajectory = the holographic reduction-tree
  vector field; see relational-loss-distillation §holographic-trajectory IOU).
```

## Why attention is the RIGHT target for routing-only forms

Attention is essentially ONE structural operation = a data-dependent convex
combination of value vectors = function **application** (s219). The routing-only
normal forms are *by construction* the things expressible as that move. So this is
not "hope attention can represent the curriculum" — the curriculum is RESTRICTED to
attention's expressive class. Cleanest possible attention dataset.

Half-validated already by the stride-fit screen (s221, `combinator-training-beta-
reduction.md` §strided): of the agreed harvest edges, **B–D / S–D are v15-NATIVE,
B–C / K–C FEASIBLE, only S–Y NEEDS-RECURRENCE — 4/5 stride-teachable**. v15's
`FibonacciStrideAttention` is a fixed causal gather (content only weights), so
"substitution-at-distance = Zeckendorf stride composition"; the composition
skeleton fits as stride-hop/window-weighting traces and the recurrence supplies Y.
This idea is the curriculum that operationalizes that result.

## Honest catches (mark before building)

1. **K-erasure is the known hard spot.** s221 training law: B-first → plateau →
   learning **K causes chaos** (erasure must move weights a lot → transiently breaks
   contraction → fp-loss explodes). Stride screen flagged K "zero in-window." ⇒
   within routing-only, **K is the expensive one** — needs MORE data + careful
   ordering (B-first, then K), not uniform weighting. (`fp-spike = acquisition`.)
2. **S is not cleanly one move.** S duplicates (1 fan-out) — composition with a copy,
   more than a linear move; stride-fit: S–D native but S–Y needs recurrence. So
   "routing-only" is a GRADIENT: {K,I,C,B,D} clean single-move, S a static-but-
   duplicating boundary case. Tier the curriculum; do not treat the set as flat.
3. **Right register or wrong experiment.** The s223 relational-loss sweep measures
   the **FFN gate** as routing register. Training ATTENTION needs target + readout =
   **attn_q** (instrument exists: `combinator_relationship_map_v15.py --target
   attn_q`; s220's only suggestive v15 signal was attn_q@L05, z=1.54, p=0.063 = the
   SILENT-selector layer, `function-discovery.md`). Same instrument, different register.
4. **Identity vs analogy.** "routing-only normal form = attention move" is IDENTITY
   for {K,I,C,B} (s221 grounded in substitution structure), near-identity for {D,S},
   FALSE for {Y,W,WHNF} (the whole point). Keep the line where it actually is.

## Falsifiable test (the second leg, after the s223 FFN-gate sweep confirms)

> Generate Curriculum A (routing-only reduction traces for {K,I,C,B,D}) from the
> lambda compiler. Train v15-style attention (or the tiny student's attention) on it.
> Measure with the **attn_q** instrument: does the combinator silhouette at L05 clear
> the null (lift z=1.54 → significant)? CONTROL: feed recursion {Y,W,WHNF} traces to
> the SAME attention → prediction: it does NOT crystallize (no single move).

Double claim: routing-only data crystallizes attention's routing register; recursion
data does not — s222's "routing ⊕ continuation = complete basis" as a CURRICULUM
result, not just a static map.

## Distributed / self-teaching tie-in

This is the self-teaching loop (`consensus-delta-folding.md` §s217) sharpened by the
basis partition: the lambda compiler is a VERIFIED ORACLE (WHNF / Church-Rosser →
labels correct by construction), so it can mint:
- routing-only traces → teach attention WHICH cross-position move (the execution),
- shared-skeleton I/O → the foldable/transferable universal core,
- (recursion left to the continuation, fed the contractive trajectory).
Curriculum partitioned by MECHANISM, each part trained where it is representable.

## Open leads (declare register first)

1. **Curriculum-generation spec** (register: functional): how the lambda compiler
   emits routing-move traces for {K,I,C,B,D} (input term → reduced term → the
   position-move it encodes, dual-rendered NL + combinator per the self-teaching loop).
2. **Attention-routing harness** (register: topological/routing → functional):
   the attn_q version of `relational_loss_distillation.py` — train attention on
   Curriculum A, measure attn_q@L05 silhouette vs the recursion control.
3. **K-curriculum design** (register: functional): B-first→K ordering + K-heavy
   weighting; does it crystallize K without the contractivity collapse (s221 law)?
4. **Compose with relational loss**: routing-only TRACES (data) ⊕ routing-CMR Gram
   (relational target, s223) — does the trace curriculum + relational target beat
   either alone on attn_q crystallization?

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/routing_curriculum_attention.py` | attn_q version: train attention on routing-only reduction traces; measure vs recursion control |
| `scripts/experiments/relational_loss_distillation.py` | s223 sibling (FFN-gate, static-Gram relational version) |
| `scripts/experiments/combinator_relationship_map_v15.py` | the attn_q routing-register readout instrument |
