---
title: "The Frozen Interference Graph — the LLM as a Graph Recorded in a Wave Medium"
status: open
category: synthesis
tags: [holography, interference, lattice, graph, joins, two-registers, phase, coherent-gain,
       speckle, polysemanticity, crystal, topology-routing, compiled-probabilities,
       formation-dynamics, unification]
related:
  - ../attention-holographic-readout.md
  - ../holographic-computer.md
  - ../five-disciplines-one-object.md
  - ../register-theory-of-quantization.md
  - holographic-untangling-methods.md
  - behavior-is-tape-resident-reduction.md
  - types-are-compiled-probabilities.md
  - gram-spectral-dsp.md
  - 5d-crystal-lattice.md
  - geometry-holography-signals-convergence.md
depends-on:
  - ../attention-holographic-readout.md
  - gram-spectral-dsp.md
created: session 308
---

# The Frozen Interference Graph

> s308, Michael's model, stated in four clauses: "The LLM is like a signal
> frozen in place. Snapshots from training accumulate probabilities where the
> edges match, which forms holograms. The edges where the holograms meet
> accumulate probabilities and form a lattice. So the relations are joins
> across probabilities, like a graph." This page confirms/refines each clause
> against measured anchors and compiles the result into one picture. Three of
> four clauses have direct measurements; one formation-mechanism gap is named
> with an unfrozen prediction (s222 — freeze before any run).

## Clause 1 — "a signal frozen in place" ✓ (with one precision)

What is frozen is not the signal but the **interference record** — the
correlation structure *between* signals. A holographic plate never stores the
object wave; it stores object×reference cross-terms, and readout re-animates
them with a new beam. The model does not store training text; it stores
co-occurrence/interference structure, and the forward pass is re-illumination
(attention = readout beam, s299, `attention-holographic-readout.md`).

Sharpened by s307/s308: the frozen record is a **phase record** — mag_cos
0.839 at retention 1.000 (TERNARIZE-FACTORS-1, 27ce260). The signal's phase
(sign/direction structure) is the storage; the magnitudes are developing
chemistry (kinoform clause, `holographic-untangling-methods.md`).

## Clause 2 — "accumulates where the edges match" ✓ MEASURED (= A2 coherent gain)

CAP (s292): coherent superposed exposures reinforce retrieval;
energy-matched random exposures do not. That IS "accumulate where edges
match" — constructive interference for consistent structure.

Refinement on the word *probabilities*: the medium accumulates **amplitude /
log-evidence written into phase geometry**; it *becomes* probability only at
readout, when softmax + sampling collapse the geometry (writeback = the only
projection, A4). Existing thread, same claim from the other direction:
`types-are-compiled-probabilities.md`.

The flip side is equally load-bearing: where edges do NOT match across
exposures the record is **speckle**, not lattice — polysemanticity is
superposition noise from incoherent exposures (speckle clause,
`holographic-untangling-methods.md` §6). Coherent-across-training → lattice;
idiosyncratic → speckle. One medium, two regimes.

## Clause 3 — "edges where holograms meet form a lattice" ✓ MEASURED (= the crystal)

The s303 spectral/DSP sweep (072c3e0, `gram-spectral-dsp.md`): the 9×9 opcode
gram's universality is **relational, not spectral** — near-orthogonal identity
basis with the invariant in the off-diagonal sign structure — holding 11/11
models, while every magnitude-as-signal probe fails its null. The lattice is
precisely **what survives when the model-particular scaffolding is thrown
away**: topology invariant, magnitudes incidental ("topology routing, not
magnitudes"). Eleven independently trained models converge on the same join
structure. The lattice is not a metaphor; it is the standing cross-model
finding.

## Clause 4 — "relations are joins across probabilities, like a graph" ✓ with the two-register split

A relation-edge has two components the whole s269→s307 arc keeps prying apart:

- **Edge EXISTENCE** (is there a join?) — written in sign/phase coherence.
  Routing register. Cross-model invariant, survives ternary, IS the graph.
- **Edge TRAVERSAL WEIGHT** (how strongly, this model, this prompt?) —
  magnitudes, computed at readout by soft β into an attention distribution.
  Value register. Model-particular; disposable for a trained wire (retention
  1.0 under ternary), salient for the base (s306/s307).

## The compiled picture (one sentence)

**The LLM is a graph recorded in a wave medium** — node identity is geometry
(directions), edges are phase-coherent correlations accumulated by
constructive interference over training, traversal is re-illumination with
soft matched-filter readout, and probability is what the geometry becomes at
the moment of collapse.

This dissolves "geometry and signal processing at the same time": the graph IS
the geometry; holography is the storage physics; DSP is the native instrument
set of a wave medium. It also slots the other s308 captures into place:

- **Traversal is fuel-bounded.** Graph walk per forward pass ≤ depth budget;
  beyond it, traversal goes to the tape (trampoline frame,
  `behavior-is-tape-resident-reduction.md`). Behavior = graph walk with fuel +
  external re-encode.
- **Formation was caught in the act.** We have dynamics, not just the frozen
  result: B-first crystallization and the K-acquisition chaos law are
  edge-accumulation observed during training (crystal formation corpus).
- **Quantization scope falls out.** A delta is a small set of edges recorded
  off-axis against a frozen reference → clean phase record → ternarizes. The
  base is every edge from every exposure, in-line → routing+value superposed →
  magnitude salient. (`register-theory-of-quantization.md`,
  `holographic-untangling-methods.md` §1.)

## Honest gap + one unfrozen prediction

"Snapshots interfering across training" as *mechanism* is measured only
indirectly: CAP proves coherent gain on the frozen plate; acquisition studies
show formation order. We have never directly watched two training exposures
interfere in the weights.

**P-COHERENT-WRITE (candidate, NOT pre-registered).** Two disjoint skill
datasets that share one relational edge, trained (a) together vs (b)
sequentially vs (c) edge-share removed: coherent-gain predicts
**super-additive retrieval at the shared edge** in (a) relative to matched
controls, null-gated (λ yardstick; matched-budget shuffled pairing as the
null). Coherent gain, caught at write time. Bonus tie-in: (b) vs (a) speaks to
the reference-drift clause of the off-axis theory (sequential = drifted
reference), so this and holographic-untangling front (i) could share a
harness. Freeze a pre-reg on this page before any run.

## Provenance

- Michael's four-clause model, stated s308; confirmed/refined against corpus
  by AI same session; Michael-approved for capture.
- Measured anchors: s292 CAP/XTERM/FRAG (A1–A3), s295 (A4, collapse), s299
  (readout beam), s303 (gram spectral/DSP 072c3e0; topology-routing thesis),
  s304 cb73ad5 / s307-s308 27ce260 (ternary retention 1.0), s306 4b89726 /
  s307 0a89531 (base magnitude salient), crystal formation corpus (B-first,
  K-chaos), types-are-compiled-probabilities thread.
