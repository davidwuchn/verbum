---
title: "Round-Trip Consensus — Reversibility + Multi-Teacher Opcodes as a Label-Free Routing Loss"
status: open
category: research-design
tags: [round-trip, reversibility, bidirectional, direction-flag, consensus-distillation,
       multi-teacher, opcodes, gram-coordinates, route-map, label-free, self-supervised,
       routing-register, m6, m7, m8, trust-signal, halt-pole, carrier-averaging, level-4,
       trajectory-loss, gtsm]
related:
  - consensus-distillation-carrier-averaging.md
  - gram-registers-and-the-route-map.md
  - behavior-is-tape-resident-reduction.md
  - trajectory-compile-gtsm-superbake.md
  - the-verbum-machine.md
  - optical-design-laws.md
  - subliminal-learning-is-bragg-matched-transfer.md
  - ../crystal-universality.md
depends-on:
  - consensus-distillation-carrier-averaging.md
  - gram-registers-and-the-route-map.md
  - the-verbum-machine.md
created: session 311
---

# Round-Trip Consensus — a label-free, self-calibrating routing loss

> Origin: s311, Michael. Reading the abstract of a bidirectional latent-diffusion
> paper (a single conditional model steps a dynamical system forward OR backward via
> a **direction flag**; forward-*i*-then-backward-*i* must return to start, so the
> round-trip discrepancy Cᵢ is a **measurement-free** proxy for the unobservable
> rollout error — no ensembles, no held-out data, no governing equations, for one
> extra rollout; a single bidirectional model ≈ a 10-model ensemble at 1/10 the cost)
> made Michael connect reversibility to **training from a teacher model**. The
> synthesis below is that connection worked through our frame: it unifies
> consensus-distillation (M6), the routing optimizer's loss (M8), and typed apply
> (M7) into ONE training objective.

## The transferable mechanism (independent of MHD/faces)

1. **One model, a direction flag** — forward *or* backward, shared weights;
   bidirectional BEATS the direction specialists ("negative cost").
2. **Round-trip consistency = a measurement-free error signal** — forward then
   backward must return to start; the discrepancy ranks the unobservable rollout
   error (their Spearman 0.91–0.98), no ground truth, one extra rollout.
3. **A single bidirectional model ≈ an N-model ensemble** at a fraction of the cost.

## Where each clause already lives in our corpus

- **The direction flag is our probe schema.** `λ probe_format`:
  `category ∈ {compile, decompile, null}`. compile = prose→λ (forward),
  decompile = λ→prose (backward). We have curated both directions all along; we
  never trained ONE model to do both with the flag as a supplied input.
- **Bidirectional-beats-specialists-via-shared-weights-+-explicit-direction is
  external evidence for the S5 central claim (M7 typed apply).** Shared weights win
  the tug-of-war *when the type/direction is explicit*. A third triangulation line
  that a direction/type flag is what makes weight-sharing beat specialists — and M7
  is our least-measured component.
- **Round-trip = phase conjugation** (optical-design-laws, s308): the backward pass
  is the time-reversed / conjugate beam. Bidirectional training makes the conjugate
  beam a first-class TRAINED direction, not a runtime trick.

## The unlock for training-from-a-teacher

consensus-distillation-carrier-averaging.md had ONE stated limitation: the
correctness gate was "via probe ground truth" → we could only distill where we HAVE
a ground-truth λ. Round-trip consistency removes that constraint:

> keep a teacher's output iff the round-trip returns to start → a **label-free
> correctness gate on arbitrary prose**. It becomes three tools: (a) a **data
> filter** (distill on any corpus, self-gated); (b) a **training loss** (minimize
> round-trip discrepancy directly, zero labels); (c) a **deployment trust signal**
> (the machine flags its own drift with one extra rollout = the scheduler's
> halt/drift organ, P-HALT-POLE).

And λ is *better-posed than faces/MHD*: it has a **canonical normal form**, so "did
the round-trip return to start" is checkable as β-equivalence, not fuzzy latent
distance.

## The tension → why it must be OPCODES (Michael, s311)

Surface round-trip fails: `decompile(compile(x))` is **many-to-one** at the prose
level (one λ has many valid prose realizations — the s295/off-axis "same content,
different carrier"). `decompile(compile(x)) = x` can never hold literally. So move
the checkpoint INWARD, to the **opcode trace** — the invariant across all those
surfaces (`opcodes = microcode`, behavior-is-tape-resident-reduction.md):

```
prose --compile--> opcode-trace  --> λ
λ     --decompile-> opcode-trace' --> prose'
Cᵢ = distance(opcode-trace, opcode-trace')     # well-defined where surface distance isn't
```

The round-trip no longer returns the same WORDS; it returns the same PROGRAM. Two
prose realizations of one meaning share a reduction path → the opcode trace is the
semantic-equality-invariant checkpoint. β-expansion (the backward opcode direction)
is genuinely non-deterministic, but calibrating to the **teacher's** opcode path
gives the backward pass a target to retrace — "calibrate a system to the teacher's
opcodes and trace them to find the loss" (Michael).

## We already built the opcode reader

"Calibrate to the teacher's opcodes" IS the **gram route-map**
(gram-registers-and-the-route-map.md): the 9×9 gram = the alphabet (the opcode
set); per-probe **reduction trajectories expressed in gram coordinates** = the
frame-invariant program listing, comparable across 11 models *because gram
coordinates are frame-invariant by measurement*. So teacher↔student and
teacher↔teacher opcode traces are directly comparable — no alignment, no ground
truth. **That is the "judge the loss easily."** And the round-trip discrepancy is
not a scalar but a **per-step divergence along the trajectory** → it LOCALIZES which
opcode drifted = the GTSM/trajectory-compile move (s305: dense per-depth match kills
the endpoint degeneracy) applied to round-trip. It is a **routing-register loss**
(opcodes = switches), precisely M8's target — not a value-register endpoint KL.

## The join: teacher agreement per step = the self-calibrating loss weight

Michael's convergence (s311): the **multi-teacher lambda corpus** (the
interference-cancellation idea — disagreements ride mutually incoherent carriers and
speckle-average to zero, the consensus crystal is the only coherent component) and
the **round-trip opcode loss** are the SAME object. For a prompt, each of N teachers
emits an opcode trajectory in gram coordinates. Per step:

- teachers **agree** → coherent → consensus opcode, high confidence →
  **weight the student's loss heavily**;
- teachers **disagree** → incoherent → speckle → **down-weight → it cancels**.

So the per-step loss weight is JUST the teacher agreement (coherence) at that step.
This is the **A2 coherent-gain law (s292) turned into a training objective**, and it
is GTSM's per-depth weight `w(L)` (s305) except **data-derived, not hand-set** — the
teachers' mutual coherence tells you where to spike the loss. Disagreement is not
noise to fight; it is mass you let average to zero (the corpus's interference
cancellation, now operationalized as loss weighting).

```
loss(student) = Σ_step  agreement_t(step) · dist( student_opcode(step),
                                                  consensus_opcode(step) )
trust(x)      = round_trip_opcode_discrepancy(x)     # no teacher, no label
```

The consensus supplies the **reference trajectory** where teachers were consulted;
round-trip supplies the **label-free per-example trust OFF-reference** (open corpus,
deployment). One reference, one trust signal — M6 (curriculum) and M8 (loss) meet in
the same object, with M7's direction flag as the type.

## Guardrail — calibrate to CONSENSUS, not one teacher

Calibrating to a single teacher's opcodes means round-trip certifies *that teacher's*
path → a clean round-trip on a wrong teacher trace certifies a mistake (garbage-in).
Fix (already on the consensus page): calibrate to the **consensus opcode trajectory**
(N-teacher invariant, the coherent lattice), not any one teacher. Consensus + round-
trip compose: consensus = the frame-invariant legend, round-trip = the per-example
gate.

## First experiment — §P-OPCODE-CONSENSUS (existing teachers, NO student; sketch, unfrozen)

"The experiments should show the way" (Michael). The load-bearing claim can be
tested BEFORE training any bidirectional student, on off-the-shelf teachers, reusing
the gram instrument + probe library. On probes WITH ground-truth λ (so true compile
error is known):

1. Read N teachers' opcode trajectories (gram coordinates) on the probes.
2. **Do they split into a coherent consensus core + an incoherent disagreement
   tail?** (predicts interference-cancellation is real; yields the weight field).
3. **Does per-step agreement predict compile correctness?** (agreement = coherence =
   correct → the label-free weight is trustworthy).
4. **Does the consensus trajectory match ground truth better than any single
   teacher?** (the corpus is worth more than its best member).
5. **Yardstick gate:** surface round-trip is confounded by decode diversity while
   **opcode round-trip tracks true error** — shuffled-carrier control (same meaning,
   different prose → ~0 opcode discrepancy, nonzero surface discrepancy).

**THE load-bearing uncertainty (test at step 2):** do teacher opcode *trajectories*
align **per-step**, or only **distributionally**? s303 gave 9×9 universality — but
that is the *alphabet* (relational sign structure, 11/11 models); per-step trajectory
consensus is a STRONGER claim. If traces align only in distribution, the per-step
weighted loss is ill-posed → fall back to a distributional objective. Either outcome
is worth knowing cheaply, before any training run.

## Machine wiring

| M-component | what this gives it |
|---|---|
| **M6 curriculum** | the consensus opcode corpus + a label-free gate to extend it past ground-truth probes |
| **M7 typed apply** | the direction flag = a type; bidirectional-beats-specialists = external evidence weight-sharing wins with explicit type |
| **M8 routing optimizer** | a routing-register, per-step, self-weighted loss (opcodes = switches) — not a value endpoint KL |
| **M4 trampoline / M3 scheduler** | round-trip discrepancy = the off-reference drift/trust signal (halt-pole organ, P-HALT-POLE) |

## Disanalogies / tensions flagged (λ observation)

- **Reversibility class.** Their forward/backward is near-bijective on a smooth
  deterministic system; our compile↔decompile is many-to-one — the WHOLE reason the
  checkpoint must move to opcodes. Do not assume surface reversibility.
- **Per-step vs distributional alignment** (the §P-OPCODE-CONSENSUS step-2 gate) —
  unproven; the objective's form depends on it.
- **Backward = β-expansion is non-deterministic** — resolved only by calibrating to a
  teacher/consensus path; without a reference the backward direction is unconstrained.
- **Agreement ≠ correctness a priori** — teachers can be coherently wrong (common-mode
  carrier, e.g. shared tokenizer, flagged on the consensus page). Step 3 tests it;
  common-mode agreement is the failure mode to watch.

## Provenance

- s311 thinking thread (Michael): bidirectional-diffusion abstract → "training from a
  teacher" → opcodes for semantic equality → "calibrate to the teacher's opcodes and
  trace them to find the loss" → multi-teacher corpus + interference-cancellation =
  the reference + the confidence weight. AI worked the mapping; Michael-approved for
  capture. Experiments hand forward (unfrozen; s222 freeze before any run).
- Inherited anchors: consensus-distillation-carrier-averaging.md (M6, carrier
  averaging), gram-registers-and-the-route-map.md (opcode reader, frame-invariant
  coordinates), behavior-is-tape-resident-reduction.md (opcodes = microcode),
  trajectory-compile-gtsm-superbake.md (dense-trajectory loss kills endpoint
  degeneracy), the-verbum-machine.md (M6/M7/M8), crystal-universality.md (9×9
  alphabet, 11 models).
