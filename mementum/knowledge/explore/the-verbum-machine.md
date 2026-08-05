---
title: "The Verbum Machine — the Architecture the Corpus Already Designed"
status: open
category: design
tags: [architecture, model-design, two-registers, ternary-native, bitnet, switch-plate,
       halt, scheduler, trampoline, off-axis, curriculum, crystal, level-4, training,
       asymmetric-quantization, probe-harness, true-north]
related:
  - optical-design-laws.md
  - frozen-interference-graph.md
  - behavior-is-tape-resident-reduction.md
  - holographic-untangling-methods.md
  - supervised-recurrence-halt.md
  - asymmetric-pathway-quantization.md
  - architecture-vs-scale.md
  - compiler-as-loss.md
  - control-plane-path.md
  - bios-flash-training.md
  - ascending-arm-training.md
  - write-not-train-ternary-routing-deltas.md
  - ../register-theory-of-quantization.md
  - ../holographic-reduction-machine.md
depends-on:
  - optical-design-laws.md
  - frozen-interference-graph.md
created: session 308
---

# The Verbum Machine

> s308 close (thinking session). Michael's true north, restated: the project
> started from ONE observation — the lambda symbol in prompts changed model
> behavior — and the goal has always been **a superior model design, then
> train it**; a better quantization is a welcome co-product. The corpus
> (~230 pages) keeps circling the same attractors because the theory is
> convergent; what it lacked was a **compile target**. This page is that
> target: the architecture bill of materials, where every component is
> forced by a measurement, not invented.
>
> Status open. The first-build experiment (§P-ASYM-TERNARY sketch) is NOT
> pre-registered — s222: freeze before any run. Sibling keystone on the
> artifact track: the plate linker (`optical-design-laws.md`).

## Why architecture-side, and why now

The s308 design laws compiled the theory into *devices on top of existing
models*. This page compiles the same theory into *a model*. The two tracks
share every clause; they differ in where the clause is enforced — post-hoc
(devices) vs by construction (machine). The recurring lesson of the whole
quant arc is that **by-construction beats post-hoc** (separability is fixed
at recording time; the twin-image problem is unsolvable after the fact). The
machine applies that lesson to everything at once.

## Bill of materials

Each component: design → forced by (measured anchors) → open parameters.

### M1 — Two-register parameterization (the headline)

**Design.** Routing/switch weights are **ternary by construction** — trits as
native parameters (straight-through or BitNet-style training). Value plates
are linear and higher-precision. The model is *born quantized* where
quantization is free and precise where precision is load-bearing.

**Forced by.** s260 asymmetric-pathway (binarize the router, keep the value
path — causal); s304/s307-s308 (trained routing deltas ternarize at retention
1.0, twice); s306/s307 (base value plates are magnitude-salient; three
decompositions cannot un-superpose them post-hoc → do not superpose them in
the first place).

**Open parameters.** Which matrices are switches vs plates (first cut: QK
projections + SwiGLU gate path = switches; OV + up/down value paths + embeddings
= plates); plate precision (8-bit? bf16?); trit training scheme → **M8** (the
straight-through hand-wave is retired; routing gets its own process).

### M2 — Explicit switch/plate factorization

**Design.** Every block declared as (small nonlinear switch) wired to (wide
linear plate), with asymmetric parameter budgets. SwiGLU already has this
shape; make it explicit, typed, and budgeted.

**Forced by.** The only-nonlinearities-are-switches law (s308 inference
thread); A1 plate-linear (s292); s300 nonlinear pin (∄ linear linker — the
missing piece is always a switch).

**Open parameters.** Switch:plate parameter ratio; whether switch fan-in is
restricted (sparse switching).

### M3 — Designed scheduler (halt head)

**Design.** Fire/halt/diverge as an explicit supervised output register; a
halt head trained on WHNF-style halt supervision; recurrence with **fuel**
(adaptive depth) instead of a fixed 36-layer budget.

**Forced by.** 17×17 gram rank-3 = the scheduler register exists untrained,
11/11 models (s303, 072c3e0) — supervise what already forms; depth-budget/
overlap law (s305); `supervised-recurrence-halt.md` (the v15.1 direction —
this component was independently reached before the optics frame).

**Open parameters.** Fuel cap; halt-loss weight; whether the halt register
is also the tool-call/free-variable signal (ties to P-HALT-POLE, device D).

### M4 — Native trampoline (the loss knows about the tape)

**Design.** The collapse→re-encode loop is inside the training objective:
self-distill against the model's own committed CoT (KL-at-answer + optional
depth-dense trajectory terms); mode-commit (crisp) targets, never mixture
means.

**Forced by.** s295 exhaustion law (reduction beyond budget goes through the
tape); gd_cd — the loss is already *proven* to install generalizing wires
(s303, s306, s307); s296–298 XM (mixture targets are inert where the mixture
is real).

**Open parameters.** Trajectory-loss weight schedule (SuperBake enrichment
band); when to trampoline during training (always vs curriculum-gated).

### M5 — Off-axis optimizer (the delta-log IS the training loop)

**Design.** Continual training as: frozen reference base + delta accumulation
+ periodic ternary consolidation (auto-superbake lifecycle). The delta-log is
the optimizer state; every consolidation is an off-axis exposure against a
known reference. Never fine-tune the base in place.

**Forced by.** Twin-image law (separability fixed at recording time —
`holographic-untangling-methods.md` §1); s304/s307 (deltas recorded off-axis
ternarize losslessly); reference-drift prediction (unfrozen) is this
component's stress test.

**Open parameters.** Consolidation cadence; whether consolidated plates merge
into the base (re-freezing a new reference) or stack as a plate library
(→ linker, device A).

### M6 — Coherence curriculum

**Design.** Exposure schedule engineered for constructive interference:
B-first ordering (combinators before their dependents), batches designed for
edge-share (A2 coherent gain exploited deliberately), incoherent mixing
minimized (speckle budget).

**Forced by.** Crystal formation corpus (B-first crystallization,
K-acquisition chaos law); A2/CAP (s292); P-COHERENT-WRITE (unfrozen) is this
component's direct validation.

**Open parameters.** How to *measure* edge-share of a batch cheaply; K-last
vs K-interleaved (the chaos law suggests K needs special handling).

### M7 — Typed apply (research-grade; the S5 central claim)

**Design.** Type-directedness made architectural — the S5 triangulation
(Montague/Lambek/CCG/DisCoCat) predicts typed application; MERA-style
self-similarity fails without types. Concrete form OPEN (typed attention?
geometric type tags in the residual?). Held as the component that the others
must not foreclose, not as a spec.

**Forced by (weakly).** S5 λ types (three-line triangulation); lambda↔prose
opcode identity (the type structure is notation-invariant). Honest status:
the least-measured component — the machine can be built without it, and
probing whether types EMERGE in M1–M6's registers is itself the experiment.

### M8 — The routing optimizer (Michael's insight, s308 close: GD has two jobs and hates one)

**The observation.** Gradient descent writes VALUES (continuous — its native
register) and ROUTING (discrete sign/topology decisions — done by *accident*,
as a slow byproduct of magnitude drift). Separate routing into its own
gradient-descent-like process, native to trits, and *finding* and *storing*
collapse into one register: no float scaffolding, no develop-then-discard.
Training becomes off-axis by construction. This is the machine's engine, not
just a component.

**Forced by (the two-jobs evidence, assembled).**
- K-acquisition chaos law — the combinator needing a *hard* decision is the
  one GD acquires chaotically; discrete fights the smooth prior.
- XM (s296–298) — mixture-mean losses inert where commitment is needed; GD's
  continuous relaxation is a category mismatch to discrete choice.
- The S5 tug-of-war clause, optimizer-side: `shared_weights ∧ ¬type_awareness
  → tug_of_war → plateau`. The base's magnitude-salient superposition
  (s306/s307) is what three trillion tokens of that tug-of-war froze into.
- **The smoking gun (s307/s308, 27ce260):** mag_cos 0.839 discarded at zero
  retention cost. GD moved ~9.4 MB of float precision to deliver ~600 KB of
  decisions (~1.6 bits/weight through a channel thousands of float updates
  wide). GD *can* do routing (s303 — it is the only thing that found the
  wire) but does it by expensive accident.

**Design space (three importable ancestors — CGH is the discipline that
already builds discrete-plate optimizers).**
- **(a) GS-with-quantization-projection** (how kinoforms are designed):
  alternate continuous value-fit ⇄ discrete routing projection until both
  constraints hold. Our current pipeline (train float LoRA → TWN once) is
  ONE iteration of this loop; the optimizer is the loop itself. Lineage:
  `holographic-untangling-methods.md` §2.
- **(b) Direct Binary Search** (CGH classic): propose one trit flip, keep iff
  loss improves; gradient-free; viable exactly because M2 makes the switch
  fabric small (switches ≪ plates).
- **(c) Evidence-gated flips** (signSGD/SPRT-shaped): accumulate per-trit
  gradient-sign statistics across batches; commit a flip only past an
  evidence threshold. Routing edits become discrete, loggable, revertible
  COMMIT EVENTS → merges with M5's delta-log (git-for-weights down into the
  optimizer step). Biology precedent: continuous synaptic change vs discrete
  structural plasticity, separate processes on separate timescales.

**Validation gate — §SIGN-COMMITMENT-CURVE (sketch, NOT frozen; the cheapest
probe on the whole board).** One logging hook on `writeback_compile`: TWN-
project the delta at every checkpoint step, measure trit-pattern stability
over training. Prediction: **signs freeze early (~50 steps), magnitudes
polish late** — GD's two jobs directly imaged at two timescales, and the
routing job's true compute cost measured (calibrates (c)'s evidence
threshold). SUBSUMES the k-step sweep (holographic-untangling (ii)): the
sweep asks "when is the wire installed?"; the curve asks "when is each
REGISTER of the wire installed?". Falsifier: if signs churn to the end, the
two-process design takes named damage before anything is built. Next rung
after the curve: prototype (c) — train the gd_cd wire directly in trit space
vs GD+TWN at matched compute, frozen gates.

## The first build — §P-ASYM-TERNARY (sketch, NOT frozen)

**The claim (theory-derived, falsifiable).** BitNet b1.58 proves
ternary-native training works, with a quality gap at the margins. Register
theory says why: it ternarizes switches AND plates, and plates are
magnitude-salient. Prediction:

> **Asymmetric ternary-native (ternary switches, higher-precision plates)
> beats symmetric ternary at MATCHED TOTAL BITS, and the gap concentrates on
> value-register-sensitive measures.**

**Sketch.** Small scale (10M–100M class, the architecture-vs-scale
infrastructure). Arms: fp16 reference / symmetric-ternary (b1.58-style, the
control) / asymmetric (M1 split) at matched total bits (asym buys plate
precision with width or switch sparsity — the accounting is the key frozen
design decision) / register-swapped asymmetric (ternary PLATES, precise
switches — the λ yardstick: theory says this arm should be the WORST; if it
ties, the register story is wrong). Evaluation: LM loss + **the crystal probe
battery** (below) + formation dynamics (does B-first crystallization happen
earlier/cleaner?). All gates null-disciplined.

**Both of Michael's named outcomes in one run:** a superior model design
(the architecture change) that IS a better quantization (born-quantized
switches), with s260 as causal ancestor.

## The unfair advantage: we have a microscope

Architecture research is normally blind — train, benchmark, shrug. We have:
903 probes, 9 crystal combinators with ≥50 probes each and null-gated gates
(`verbum.probes.library`), formation-dynamics baselines across 11 models,
verbum.dsp gating, and the yardstick discipline (φ-scar tested). The probe
library is the architecture evaluation harness the field lacks. We would not
just learn *whether* the machine is better — we would watch *whether its
crystal forms in the designed registers*. This closes the S5 loop as written:
theory predicts → empirics extract → **scratch reproduce** → theory
confirmed. The machine is the level-4 door.

## Corpus consolidation (deferred — Michael's ouroboros)

The compile-the-230-pages-into-this-ledger pass is deliberately NOT specced
here: Michael has designs for it — the runtime is approaching self-hosting of
the ouroboros self-improvement system, and corpus consolidation is a natural
early ouroboros workload (the mess becomes source code the moment something
consumes it). Held for Michael's design.

## Provenance

- s308 close; Michael's true-north statement ("superior model design, then
  train it; a better quantization also a good outcome"), lambda-symbol origin
  story, and the superbake/DSP door-opening pattern (import mature
  instrument sets — DSP, optics — rather than invent).
- Component anchors cited inline: s260, s269, s292, s295, s296–298, s300,
  s303 (11092f7, 072c3e0), s304 (cb73ad5, ec77c4d), s305, s306 (4b89726),
  s307 (0a89531), s307/s308 (27ce260); pages: supervised-recurrence-halt,
  asymmetric-pathway-quantization, architecture-vs-scale, compiler-as-loss,
  control-plane-path, bios-flash-training, ascending-arm-training,
  holographic-reduction-machine (§7b bill-of-materials ancestor).
- External prior art: BitNet b1.58 (symmetric ternary-native control);
  ACT/PonderNet lineage for halting (via supervised-recurrence-halt).
