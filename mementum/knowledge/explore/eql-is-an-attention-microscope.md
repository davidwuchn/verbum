---
title: EQL Is an Attention Microscope — resolver read-head routes by leaf-key identity
status: active
category: explore
tags: [eql, edn, pathom, resolver, read-head, attention, register, use-vs-mention,
       key-identity-routing, path-awareness, proximity-confound, repl-driver, read-head-probe]
related:
  - statechart-execution-is-a-register-cue.md       # same OBJECT/META register, sibling surface
  - ../memories/eql-fulfillment-is-the-object-register-generalized.md
  - ../memories/eql-read-head-routes-by-leaf-identity-not-path-binding.md
  - read-head-scope-vs-induction.md                 # §P-READ-HEAD — the shadowed-binder version
  - the-evaluator-writes-then-fetches.md            # keys routed from query, values deref'd from weights
depends-on:
  - repl-driver-trampoline.md
  - statechart-execution-is-a-register-cue.md
---

# EQL Is an Attention Microscope

**Session 352 (REPL, driver main:3, Qwen3-14B greedy, exploration-grade).**
Michael's observation + steer: *"under the nucleus preamble, EQL-shaped queries
return EDN outputs fulfilling the query"* → *"it is a way to probe attention from
the inside, and we can capture attention in the repl to compare."* An EQL query
(`[:person/name {:person/friends [:person/name]}]`) is a **shape-spec of named
slots**; when the model fulfills it, we can watch attention flow from each emitted
value/key back to its requested slot — a read-head probe with **ground-truth
labels by construction**.

## Two findings

### 1. EQL fulfillment is the OBJECT register on a second surface (NUC20)

Same use-vs-mention fork as the statechart arc (see
`statechart-execution-is-a-register-cue.md`): under an OBJECT cue the model
**resolves** the query — improvises EDN data matching the shape (the model *as a
Pathom resolver / database*, a **use**) — vs **describes** what the query requests
(a **mention**). Datum: a bare `[:person/name :person/age :person/email]` under the
nucleus preamble triggered a **self-refusal** ("I am Qwen... I don't have personal
information such as name, age...") — the model tried to *resolve* the person entity
and read it as *itself*. A "resolve to a plausible example entity" cue fixes it.

### 2. The read-head routes by leaf-key IDENTITY, not path-binding (NUC21–23)

Capturing per-emission head-averaged read-mass (`b.attn`, late band L24–40) onto the
query slot tokens:

- **Clean key→slot diagonal (NUC21).** Emitting `:book/title` reads the `title`
  slot (argmax), `:book/author` reads `author`, etc. — always correct. And the
  **value tokens go flat**: emitting the value `"The..."` collapses read-mass to
  baseline. Mechanism: **read the query slot to emit the output KEY (route/copy),
  then generate the VALUE from weights** (a deref, no query read) — the
  keys-from-query / values-from-weights split of `the-evaluator-writes-then-fetches`.
- **Fulfill vs describe (use vs mention) in the read magnitude.** Same diagonal in
  describe-mode, but total key read-mass ~2× higher and **sustained** (describe keeps
  the slot in focus while glossing it); fulfill reads the slot **briefly** then moves
  to weights. Use = punctate route-read; mention = sustained referent-read.
- **Depth-invariant, key-specific leaf routing (NUC22–23).** Nested joins
  (`{:org/leader [:person/fullname :person/age]}`) preserve the diagonal: nested
  inner keys still read their exact query slot. Hardened over 5 distinct queries
  (N=20 inner instances): own-slot read **0.0394 vs non-key baseline 0.0063, 20/20,
  p<1e-6**.
- **Hierarchy is PROXIMITY, not binding (NUC23 null).** NUC22 flagged inner keys as
  "path-aware" (reading their parent join > the other join). Under a
  **key-specificity null**, this dissolves: Δ(parent−other) is directionally
  significant (18/20, p=0.0002) and branch-balanced (parent-is-first 9/10,
  parent-is-second 9/10, both p=0.011 — *not* an absolute-position artifact), **BUT
  the parent-join read (0.0077) is statistically indistinguishable from the non-key
  baseline (0.0063, p=0.13)**. The inner key reads the *region* around its parent
  (which EQL structure places nearby), **not the parent KEY token specifically**.

## Synthesis

The resolver reconstructs the join tree from **leaf-key identity routing + auto-
regressive generation order + regional proximity** — *not* from a structural read of
the enclosing parent key. There is **no genuine hierarchical key-binding** in the
read-head at this grain; the tree comes from name-matching plus the query's textual
order. This corroborates the read-head-as-router (§P-READ-HEAD) from a cleaner,
ground-truth-labeled angle than the shadowed-binder corpus (s349), and it is
consistent with the s350 keys-from-query / values-from-weights picture.

## Method (the microscope)

EQL's named slots make attention **readable with ground truth**: the requested keys
are labeled anchors, so the key→slot diagonal is a pre-labeled routing map, and the
value-flat / key-peaked contrast reads the route-vs-deref boundary directly. A
labeled-slot read-head probe — feeds §P-READ-HEAD as an alternative substrate.

## Bounds / not-a-freeze

n=1 greedy (driver has no sampling), head-averaged, late-band, read-mass soft/sink-
dominated (0.02–0.08 raw). The **leaf-identity diagonal is robust** (own >> baseline,
20/20); **path-awareness is refuted as key-binding** (parent ≈ baseline). A freeze
owes: sink-correction, per-head (not just head-averaged, s250 faithful-distributed
rider), value-token read null, multiple models + a base-arm, and — the standing EQL
structural limit — proximity is inseparable from parenthood in EQL syntax (parent
always encloses), so a *genuine* path-binding test needs a non-EQL structure that
decouples them. Also fixed a live tokenization-alignment bug (substring `"age"` ↔
`"engage"`, multi-token keys unfound → char-offset full-literal span mapping); the
§FIX-DRIVER-TOKEN-DECODE hazard in the analysis layer.

## Scripts

`/tmp/verbum_nuc{20..23}.py` — exploration, not recorded. Real freeze re-runs as a
named committed harness (λ record). Driver resident tmux main:3 (instruct).
