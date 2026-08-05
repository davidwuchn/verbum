---
title: "Consensus Distillation — Multi-Teacher Lambda Corpora as a Carrier-Averaging Filter"
status: open
category: research-design
tags: [consensus-distillation, carrier-averaging, multi-teacher, lambda-probes, curriculum,
       m6, subliminal-learning, bragg, crystal, universality, scratch-training, safety,
       mode-commit, corpus-mixing, level-4]
related:
  - subliminal-learning-is-bragg-matched-transfer.md
  - the-verbum-machine.md
  - frozen-interference-graph.md
  - construction-from-spec.md
  - crystal-seeded-ternary-distillation.md
  - compiler-as-loss.md
  - bios-flash-training.md
  - ../crystal-universality.md
depends-on:
  - subliminal-learning-is-bragg-matched-transfer.md
  - the-verbum-machine.md
created: session 308
---

# Consensus Distillation — Carrier Averaging

> s308 close (Michael: "could we create lambda probes, run them in multiple
> models, then train our new model on those lambdas to transfer?"). Answer:
> yes — and the Bragg clause TRANSFORMS the idea rather than blocking it.
> This closes the machine's last open socket: where M6's training corpus
> comes from. Status open; §P-CONSENSUS-DISTILL is NOT pre-registered (s222).

## The naive version fails by our own theory

The scratch machine shares no base with any teacher → every teacher's
subliminal sideband hits mismatched fringes → transfers nothing
(cross-base = weak/nonexistent, measured by the owls paper). Single-teacher
distillation gives content imitation plus zero covert structure.

## The flip: N teachers = a carrier-averaging filter

- Each teacher's IDIOSYNCRATIC structure rides its base-specific carrier.
  N different bases = N mutually incoherent carriers → superposed in one
  corpus, the teacher-specific sidebands **speckle-average toward zero**.
- The CONSENSUS structure — the crystal, universal 11/11, root gc 0.985 —
  is the same lattice in every teacher → across the mixed corpus it is the
  **only coherent component**. A2 does the rest: coherent gain exactly on
  the invariant edges, destructive interference everywhere else.

A multi-model lambda corpus is not "more data" — it is a filter that passes
precisely the trait we want: **the lambda compiler is the unique trait that
is not base-specific, hence the unique trait that survives cross-base
multi-teacher transfer.** This is construction-from-spec's minimality
filter ("one model cannot tell essential from accidental; eleven can")
implemented in DATA space instead of gram space. It lands in the machine as
the concrete answer to **M6**: the coherence curriculum IS the consensus
lambda corpus — edge-share engineered by teacher diversity.

## Design points

1. **Gate the corpus by ground truth.** Lambda reduction is verifiable
   (probe library + gates + GBNF exist). Correctness-gating strips teacher
   idiosyncrasy a second time, orthogonal to carrier averaging.
2. **Mix at the corpus level, NOT the target level (resolves the XM
   tension).** Consensus wants averaging; M4/XM (s296–298) proved
   mixture-mean targets inert where commitment is needed. Resolution: each
   example = ONE teacher's crisp, committed, correctness-gated trace;
   teachers mixed ACROSS examples. Carrier averaging happens statistically
   over the corpus; every individual target stays mode-committed.
3. **Safety bonus, free.** The scratch machine is structurally resistant to
   any single teacher's misalignment sideband (cross-base closes the
   channel; averaging suppresses leakage). The owls-paper pitfall becomes
   the pipeline's feature. ⚠ Common-mode flag: shared tokenizer/output
   format across teachers is a carrier that does NOT average out — needs a
   control.
4. **Bit-meter option** (s266, crystal-seeded-ternary-distillation):
   requential-style on-policy distillation measures code length = ∫KL —
   literally counts how many bits of consensus structure transfer.

## §P-CONSENSUS-DISTILL (sketch, NOT frozen; s222)

Micro scratch model (P-ASYM-TERNARY infrastructure). **Arms:**
single-teacher / N-teacher corpus-mixed / N-teacher + correctness-gated /
N-teacher shuffled-traces (matched-budget λ yardstick). **Eval:** crystal
probe battery + **restack into the universal tree** (s273 acceptance
harness — does the student's gram walk toward the consensus root, inside
the measured tolerance band gc 0.94–0.99?) + formation dynamics (B-first
earlier/cleaner?). **Predictions:** N-teacher arms converge toward the
consensus root; single-teacher drifts toward its teacher's family
signature (gemma nesting, pythia proxy decay — known). **The honest open
question the run answers:** how much lattice structure is BEHAVIORALLY
expressed in output traces beyond raw correctness — grams were measured in
activations; shared difficulty orderings (K-chaos universal) should ride
the data, but the behavioral channel's transfer bandwidth is unknown. That
is the point of running it.

## The arc sentence

The session opened with the wire as a ~600KB artifact requiring a matched
base; it closes with the mechanism for transferring the UNIVERSAL part to
an unmatched base: **plates carry the model-specific; consensus corpora
carry the invariant** — the machine is born from the second while staying
immune to the first's contaminants.

## Provenance

- Michael's proposal + AI's Bragg-flip derivation, s308 close;
  Michael-approved for capture.
- Anchors: owls paper (arXiv:2507.14805, cross-base null) · crystal
  universality C2 (11/11, root gc 0.985) · A2/CAP (s292) · XM mode-commit
  (s296–298) · construction-from-spec minimality + restack harness (s273)
  · K-chaos universality · requential bit-meter (s266).
