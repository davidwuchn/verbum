---
title: "Type Systems Under LLM Constraints — the Reachable Design Space"
status: open
category: synthesis
tags: [types, constraints, attention, gradual-typing, intersection-types,
       curry-style, linear-logic, session-types, staging, coeffects,
       parametricity, two-tier, two-register, M7, M8, design-space]
related:
  - types-are-injectable-relations.md
  - types-are-compiled-probabilities.md
  - gram-registers-and-the-route-map.md
  - frozen-interference-graph.md
  - behavior-is-tape-resident-reduction.md
  - the-verbum-machine.md
depends-on:
  - types-are-injectable-relations.md
  - types-are-compiled-probabilities.md
created: session 313
---

# Type Systems Under LLM Constraints

> s313 hammock (Michael): "For inference the only operation is attention,
> and the topology is frozen. GD has to do 2 jobs. With those constraints
> what OTHER type systems could work?" Method: invert the topology —
> derive the reachable design space from the constraints, then check
> instances (λ shape: unreachable > forbidden). Captured same session,
> Michael-approved, while the §P-TYPE-GRAM-1 registry sweep ran (whose
> qwen3-4b verdict TYPE-REGISTER, diffuse/no-poles, is used below).

## 1. The constraints as filters

- **C1 — judgment must be overlap.** Only mid-pass test: inner product +
  soft gate (QK→softmax, SwiGLU). No tag comparison, no rule selection;
  all judgments run superposed; the only discrete event is sampling. Any
  `a : T` must compile to `overlap(a, T-geometry) > threshold` — a
  matched filter.
- **C2 — two memories, one frozen.** Weights frozen at inference; KV
  tape append-only, writable. Stored types fixed at train time; session
  types enter only via attention over context.
- **C3 — GD's two jobs.** The type system must be learnable as
  routing-signs + value-magnitudes under a smooth prior. Crisp
  boundaries are GD's bad job (K-chaos; s310 marginal band churns on
  the threshold forever, loss-neutrally).
- **C4 — capacity, not grammar.** Inventory bounded by quasi-orthogonal
  packing (~10³–10⁴ passbands at D≈5k).
- **C5 — fuel.** One pass = bounded reduction; deeper type derivations
  must be trampolined onto the tape.

## 2. What ANY viable system must look like (before naming one)

1. **Curry-style, never Church-style** — tokens carry no annotations in
   the medium; typing is how machinery treats terms. (Church tags have
   nowhere to live in state — only on the tape, §4.)
2. **Graded membership with margin tolerance** (C3). Conjecture: the
   s310 marginal/ternary-0 band IS the type-boundary population seen in
   weight space; "insufficient evidence" = dynamically typed.
3. **Two-tier:** compiled types in weights (slow, persistent,
   capacity-bounded) + EXTENSIONAL types on the tape (exemplar-defined,
   instant, session-scoped). Few-shot ICL = type definition by
   enumeration.
4. **Shallow per-pass, deep via tape** (C5): CoT as a type-derivation
   trace.

## 3. The viable family (with corpus anchors)

- **Intersection types — superposition-native.** Membership in many
  passbands simultaneously; `T₁∧T₂` is free. Symbolically undecidable to
  infer; this machine accumulates, it doesn't infer. ★ The s313
  §P-TYPE-GRAM-1 TG3 shape (diffuse, PR 7.35, alphabet-like, NO poles)
  is what intersection/feature-bundle typing looks like — a closed
  nominal constructor enum would have been polar/low-rank.
- **Gradual typing with probabilistic consistency.** Graded acceptance
  everywhere (s288 giraffe); gradual consistency is famously
  NON-TRANSITIVE — the same graceful transitivity failure as the
  community-tolerance picture (types-are-injectable-relations §4).
- **Refinement/subtype lattices as nested passbands.** Subsumption =
  cone containment; widening a passband is differentiable → GD can learn
  subtyping. Negative judgments live in the universal 9×9 off-diagonal
  SIGN structure (attraction/repulsion = learned anti-correlation).
- **Probabilistic type theory (Cooper-style TTR).** `p(a : T)` as the
  judgment itself — the closest off-the-shelf formalism to
  types-are-compiled-probabilities.
- **Graded/coeffect systems.** Continuous quantitative annotations =
  the one type-theoretic bookkeeping family that is natively
  differentiable.
- **Modal/staging types at the trampoline boundary.** □A = code-of-A on
  tape; emit=quote, re-encode=splice (s295 splice law; QUOTE in the
  probe library); depth-as-fuel = a graded □.
- **Session types at the scheduler scale.** The 17×17 outcome register
  (fire/halt/diverge, predicted yield vertex) = protocol states;
  tool-call FFI = typed channel op. Behavior-grain, scheduler-enforced.
- **Parametric polymorphism — free by weight-tying.** The same QK/OV
  machinery applies to any operand; binding heads are content-generic.
  Parametricity is an architectural consequence, not a discipline.

## 4. Near-misses and rescue forms

- **Nominal typing:** impossible in state (no tags) — but tokens ARE
  discrete names → nominal typing lives ON THE TAPE. Structural in the
  medium, nominal in the transcript (two-registered again).
- **Linear/affine:** exact consumption bookkeeping out (KV append-only,
  no mutation). BUT the substrate is LINEARITY-BIASED: duplication is
  what costs (W/D need machinery; copying in a superposed medium creates
  interference) — linear usage is the default, contraction the expensive
  rule. A wave medium is a linear-logic-flavored substrate natively.
  (Analogy flagged, not identity: no-cloning is quantum; this is
  interference-cost.)
- **Dependent types:** dependency is FREE (type-level and term-level
  computation are the same pass, both directions) but judgmental
  equality needs normalization = fuel-bounded → dependent typing exists
  only shallow-per-step, trampolined.
- **Union types:** disjunction needs OR-machinery — separate matched
  filters (heads) per disjunct. Unions cost heads; intersections are
  free. Testable fingerprint (§6).

## 5. The composite answer

Under C1–C5 the reachable space is one system wearing several formal
names: **a two-tier, two-registered, gradual-intersection-structural
type system** — Curry-style structural typing whose judgments are graded
overlaps (probabilistic TTR), conjunction free / disjunction
head-hungry, subtyping = passband containment, the existence/strength
split = the routing/value split (typability = edge existence in signs;
probability = magnitude), nominal fragment on the tape, session fragment
in the scheduler register, deep derivations trampolined as CoT.

**Engineering corollary (the M8 join):** type boundaries are exactly
where GD's two jobs collide — margin cells churn (s310). An
evidence-gated routing optimizer (M8/TD-v2) would produce CRISPER type
boundaries than GD, because commit-on-evidence IS a type-boundary
decision procedure. **The machine's optimizer and its type system are
the same design problem.** (Pointer belongs on the-verbum-machine.md
when M8 next revised.)

## 6. Fingerprint probes (ALL unfrozen, s222)

- **P-TYPE-ICL** — two-tier dissociation: nonce type defined by tape
  exemplars → licensing transfer within-session, gone across sessions;
  P-TYPE-WRITE's wire is the persistent converse.
- **Union-vs-intersection asymmetry** — matched-complexity acceptance:
  ∧ cheap, ∨ degraded/head-hungry.
- **Linearity bias** — duplication-heavy (W/D) vs linear programs at
  matched size: accuracy/fuel differential (partial corpus data exists;
  reframe as the linear-logic bias measurement).
- **Boundary-churn identity** — do s310 marginal-band weights
  concentrate on type-boundary features? (Joins the optimizer story to
  the type story empirically.)

## Provenance

- s313 hammock, Michael's constraint question; AI derivation,
  Michael-approved capture same session.
- Measured anchors: §P-TYPE-GRAM-1 qwen3-4b (da8c1ba: TYPE-REGISTER,
  TG3 diffuse no-poles); s310 marginal-band churn (225dae7); s288
  giraffe refusal + JOIN-TYPED; 9×9 sign universality (072c3e0); s295
  splice law; s292 A2; K-chaos/W formation dynamics; 17×17 rank-3
  scheduler register.
- In flight at capture: §P-TYPE-GRAM-1 registry sweep (tmux main:1) —
  decides whether this design space is about transformers or one model.
