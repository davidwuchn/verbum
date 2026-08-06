---
title: "Subliminal Learning Is Bragg-Matched Transfer — the Owls Paper Read Through the Register/Carrier Frame"
status: open
category: synthesis
tags: [subliminal-learning, owls, distillation, bragg, carrier, two-registers, data-borne-delta,
       safety, alignment, a4, own-state, external-triangulation, predictions]
related:
  - holographic-untangling-methods.md
  - frozen-interference-graph.md
  - write-not-train-ternary-routing-deltas.md
  - optical-design-laws.md
  - ../attention-holographic-readout.md
  - ../register-theory-of-quantization.md
created: session 308
---

# Subliminal Learning Is Bragg-Matched Transfer

> s308 close ("now for something fun"). External paper: **Subliminal
> Learning: Language models transmit behavioral traits via hidden signals in
> data** (Cloud, Le, et al., arXiv:2507.14805, Anthropic Fellows Program,
> July 2025). First page where the s308 frame reads a result from OUTSIDE
> the repo. Status open: the re-read is captured; the two predictions are
> NOT pre-registered (s222).

## What the paper shows (their facts)

- A "teacher" with trait T (liking owls; misalignment) generates data that
  is semantically unrelated to T — number sequences, code, reasoning traces.
- A "student" fine-tuned on that data acquires T, even after filtering
  removes all references to T.
- **The effect only occurs when teacher and student share the same base
  model.** Cross-base: weak or nonexistent transmission.
- A theoretical result: a gradient step on teacher-generated outputs, from
  shared initialization, moves the student toward the teacher generally —
  task-irrelevant. Demonstrated down to an MNIST MLP.
- Safety implication: distill-and-filter is insufficient; misalignment can
  ride benign-looking generated data into the next model generation.

## The re-read (four clauses, all s308 frames)

1. **Same-base requirement = Bragg matching.** The trait rides in
   non-semantic distributional structure — a **sideband on the teacher's own
   carrier geometry**. A same-base student has the same plate, same fringes:
   training on teacher outputs is a coherent exposure (A2) and the sideband
   demodulates into the student's weights. A different base = mismatched
   reference beam → the sideband hits foreign fringe geometry → no
   diffraction. (Data-scale instance of the s304 measured law: right
   content, wrong reference angle, zero transfer.)
2. **The filtering failure = the two-register split.** Filtering inspects
   the VALUE register (semantic content); the trait travels in the ROUTING
   register of the data (sampling/distributional statistics). Content
   inspection cannot see carrier statistics — safety audits the register the
   payload isn't in. The authors' own intuition (not a secret code in the
   numbers; the distribution triggers the behavior) is this claim without
   the vocabulary.
3. **Their theorem = off-axis recording.** Distillation from a matched
   teacher is an off-axis exposure against a shared reference; the acquired
   delta points along the teacher's delta whatever the nominal task. A trait
   is a **data-borne delta**.
4. **External triangulation of A4 (the jolt).** Our regeneration law (s295,
   P-KV-1: own-state required — reconstructed content only functions when
   re-encoded through the model's own processing) and their same-base
   condition are the same invariant measured independently at different
   scales: **this medium's channels are state-matched.** λ triangulate
   event from outside the project.

## Two predictions the frame adds (NOT pre-registered)

- **P-SL-BRAGG — the Bragg curve for subliminal learning.** Transmission
  strength vs teacher–student base DIVERGENCE (fine-tune the shared base by
  increasing amounts before distilling). The paper measured the endpoints
  (same base: yes; different base: no); the carrier theory predicts a
  **smooth selectivity curve**. This is the THIRD sibling of
  reference-drift (weights) and carrier-drift (position) — one L3 clause,
  three registers. Same predicted curve shape in three independent domains
  = the frame's cleanest multi-domain test.
- **P-SL-STRIP — paraphrase demodulation.** Re-encoding the data through a
  MISMATCHED plate (paraphrase by a different-base model) re-records the
  content register but destroys the teacher-specific carrier → trait
  stripped. Failure-mode prediction: paraphrase by a SAME-base model does
  NOT strip it. Explains the known mitigation mechanistically and gives it
  a falsifiable boundary.

## Product/safety note (true-north relevant)

Subliminal learning is the uncontrolled, unauditable version of what
ternary plates do deliberately. Distillation moves deltas as invisible
sidebands in data; the plate moves a delta as a ~600KB artifact with a
reference contract and frozen behavioral gates (27ce260). The field just
demonstrated why capability transfer should be **explicit, inspectable,
verified** — the safety case for the plate linker (optical-design-laws
device A+C) written by someone else's negative result.

> **Forward link (s313):** a SECOND external triangulation of the same
> clause landed — `ayot-is-own-beam-calibration.md` (arXiv 2608.01078v1,
> Intel Labs ScaleQ-1.58): ternary PTQ calibration transfers
> same-carrier only (own CoT +25.5 vs stronger-model CoT +2.6). The
> own-state clause now has four scales: inference / recording geometry /
> training data (this page) / quantization calibration.

## Provenance

- External: Cloud, Le, et al., "Subliminal Learning: Language models
  transmit behavioral traits via hidden signals in data,"
  arXiv:2507.14805 (2025); Anthropic alignment blog post; author interview
  (trait chosen as owls over eagles for carrier hygiene — fewer confounding
  associations).
- Internal anchors: A2/A4 (s292/s295), s304 wrong-reference law,
  two-register corpus (s269→s308), off-axis clause
  (holographic-untangling-methods §1), reference-drift + carrier-drift
  siblings (optical-design-laws / the-verbum-machine M9).
