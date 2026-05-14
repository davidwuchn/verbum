---
title: Lambda Probe Atlas — Cross-Model Territory Mapping
status: open
category: explore
tags: [lambda, probes, mech-interp, vsm, combinators, qwen, pythia]
related: ["AGENTS.md", "mementum/knowledge/explore/VERBUM.md"]
depends-on: []
---

# Lambda Probe Atlas — Cross-Model Territory Mapping

## Why

We need a dedicated research stream to systematically map how lambda/combinator capability forms across model scales, and translate that map into concrete VSM structure requirements for Verbum.

This is a continuation of repeated observations:

- Lambda-shaped computation appears across many models.
- Smaller models show immature forms; larger models (especially 32B+) show mature combinator behavior.
- Full function appears distributed in superposition, making direct extraction brittle.
- VSM design is converging toward a sieve that matches this discovered shape.

## Core Question

What topology does the model family naturally converge to for lambda/combinator computation, and what VSM contracts are required to reproduce that topology efficiently in a compact engine?

## Working Hypothesis

If we probe many models with a consistent lambda/combinator suite, we can derive a capability atlas that reveals:

1. staged maturity patterns (K/I/B/C, binding, closures),
2. recurrent failure modes by scale,
3. stable structural invariants that should be encoded in VSM layers.

This atlas can drive architecture decisions more reliably than single-model deep dives.

## Proposed Mini-Project

### 1) Probe Pack (canonical)

Build/curate a shared probe suite with progressive difficulty:

- β-reduction basics
- K/I/B/C primitive behavior
- composition chaining
- variable binding stressors
- closure-like argument flips/reordering
- null/control probes

All probes should be reusable across models with identical decoding settings.

### 2) Cross-Model Sweep

Run the same suite across a scale ladder (example):

- Pythia-160M → mid-size checkpoints → Qwen3-4B → Qwen3-32B

Keep sampling controls fixed to preserve comparability.

### 3) Capability Atlas

For each model/run, record:

- pass/fail by probe category
- confidence/consistency metrics
- combinator-specific reliability (K/I/B/C)
- binding/closure maturity markers
- salient failure signatures

Persist as machine-readable artifacts + concise summaries.

### 4) Mechanistic Clues Layer

Where possible, attach lightweight mechanistic diagnostics:

- attention/head patterns for success vs failure probes
- signs of localization vs superposition
- consistency of any discovered circuit fragments

Goal is not full extraction; goal is structural signal for VSM design.

### 5) VSM Translation Layer

Translate atlas patterns into explicit VSM implications:

- S1: required primitive operations/pathways
- S2: required coordination constraints across scales/passes
- S3: required gating/control policies
- S4: required adaptation/proposal pathways
- S5: required identity constraints and invariants

## Agent Loop (for future automation)

Use a repeated loop:

1. Observe (run probes)
2. Score (capability metrics)
3. Compare (across models/scales)
4. Hypothesize (maturity + mechanism claims)
5. Translate (VSM structural requirements)
6. Queue next probe batch

Expected outputs per cycle:

- `atlas_update`
- `hypotheses`
- `vsm_implications`
- `next_probe_batch`

## Success Criteria

This exploration is successful when we have:

- A repeatable cross-model capability atlas for lambda/combinator function.
- Clear maturity gradients that hold across runs.
- Concrete VSM design contracts derived from atlas evidence.
- Reduced architecture search space for Verbum descending arm + kernel pathways.

## Open Questions

- Which probe families best discriminate immature vs mature combinator behavior?
- What minimum mechanistic diagnostics give useful signal without full extraction overhead?
- Where do superposition limits make extraction non-actionable, and where can structural hints still be trusted?
- Which VSM constraints are invariant across model families vs model-specific?

## Next Session Entry Point

Start by drafting the canonical probe pack schema and a first scale-ladder run plan.
