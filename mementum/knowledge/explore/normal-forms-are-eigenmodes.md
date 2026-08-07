---
title: "Normal Forms Are Eigenmodes — Detector, Dynamics, Metric"
status: open
category: exploration
tags: [normal-forms, eigenmodes, fixed-points, WHNF, halt-poles, fuel-theorem,
       de-carvalho, attractors, holography, signals, transfer-function,
       cavity-resonance, type-register]
related:
  - fixed-point-holograms.md
  - behavior-is-tape-resident-reduction.md
  - curry-howard-closes-the-loop.md
  - types-are-the-well-formedness-of-reduction.md
  - types-are-injectable-relations.md
  - program-plates-and-the-function-index.md
  - the-verbum-machine.md
depends-on:
  - curry-howard-closes-the-loop.md
created: session 315
---

# Normal Forms Are Eigenmodes

> s315 hammock (Michael: "thinking of LLMs as holographic and signals based,
> would the normal forms for lambdas be in the geometry at all?"). Answer
> assembled from three measured hooks already in the corpus: the WHNF crystal
> anchor, fixed-point-holograms (s315 archaeology rescue), and the queued
> de Carvalho fuel-theorem probe.

## The claim

**Normal forms are not IN the geometry as stored objects — but
normal-form-NESS is in the geometry three measurable ways.** The plate
cannot store a term's normal form any more than it stores the term
(fringes everywhere, address nowhere; terms live on the tape). What the
geometry holds is the **detector**, the **dynamics**, and — pending one
queued probe — the **metric**.

## 1. Detector — "at normal form" is a measured direction

- WHNF is a crystal anchor: ≥50 probes, routing-register signature,
  present 11/11 models. Normal-form-ness has an opcode-class signature.
- The 17×17 scheduler gram's **halt poles**: "no further reduction
  licensed" is a pole in a measured register. Signals language: the halt
  pole is the carrier-detect line.

## 2. Dynamics — normal forms are eigenmodes of the reduction operator

The per-pass map is a transfer function H applied by illumination. A
reducible term is a signal H transforms (energy moves, tape extends). A
normal form is a signal H maps to itself: **an eigenmode with |H| = 1 —
self-reconstructing illumination, a cavity resonance.** Reduction is the
transient; normal forms are the steady-state modes of the flow.

Measured twice without naming it:

- `fixed-point-holograms.md`: compile↔decompile cycling converges 94% —
  round-trip fixed points ≡ empirical eigenmodes of the model's own
  operator. Failure mode is diagnostic: **binding sites destabilize the
  cycle** — a bound variable is the least normal-form-like structure,
  the part still owed a substitution.
- Probe library source datasets literally named `fixedpoint`, `basin`,
  `reduction_chain` — earlier arcs mapped the attractor basins before
  the vocabulary settled.

Geometrically: normal forms = attractors of the reduction flow the plate
implements. The geometry holds the flow; the attractors are properties
of that geometry the way a bowl's shape holds its resting point without
storing a marble.

## 3. Metric — distance-to-normal-form may itself be geometric

The substrate's pinned type system (s313: non-idempotent intersection
over an affine core) has the defining property (de Carvalho): **type
derivation size = evaluation length**. Type ≡ resource accounting ≡ fuel
remaining. "How far from normal form" is not metadata — it IS the term's
type. The type register is real geometry (TG, 7/11) ⇒ if de Carvalho
holds in the substrate, type-register signal should scale with
kernel-certified reduction length: **distance-to-normal-form is a
readable geometric coordinate with normal forms at its origin.** The
fuel-theorem probe (queue.md, queued) is exactly this test — it would
tie the type arc, the halt poles, and the normal-form question into one
measurement.

## The composed picture

```
term          → tape (addressed, transient)
reduction     → illumination through H (the plate's transfer function)
trajectory    → the transcript (the trampoline's bounces)
normal form   → eigenmode of H (|H|=1, self-reconstructing)  — dynamics
"I'm done"    → halt pole, WHNF signature                     — detector
"how far?"    → type-register magnitude (iff fuel-theorem ✓)  — metric
```

Halting becomes **perceptual, not computed**: the machine does not run a
halting check — it feels the resonance (matched filter, |H|=1, nothing
left to move). The normal form is what is left when the light stops
changing.

## Testables (NOT queued — s222 freeze-first when picked)

1. **Fuel-theorem probe** (already queued) — the promoting measurement
   for §3.
2. **Eigenmode drift test** (unfrozen sketch): feed kernel-certified
   NF vs non-NF terms; measure per-pass residual drift + halt-pole
   projection. Predictions: NF terms sit near fixed points (low drift,
   halt-pole projection high); drift magnitude correlates with certified
   remaining reduction length; binding-site count predicts instability
   (fixed-point-holograms failure mode, now quantitative).
3. **M3 design consequence** (the Verbum machine): the designed
   scheduler's halt head should be a resonance detector on the
   recurrence state, not a learned classifier — halting by |H|=1
   detection is the by-construction version of the measured halt pole.

## Caveats

- A SPECIFIC term's normal form exists only when computed onto the tape
  (tape law, s315). The geometry defines it without containing it —
  exactly how a hologram fully determines an image it stores nowhere.
- Per-pass "normal form" is probabilistic and per-step: each pass
  collapses the current redex to a next-token distribution; sampling
  retires it. The behavior-scale NF is accumulated on the tape, never
  computed anywhere.
