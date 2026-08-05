---
title: "Optical Design Laws — Six Laws, Five Devices; the Plate Linker Is the Keystone"
status: open
category: design
tags: [design, devices, holography, plate, reference-beam, linker, composition, multiplexing,
       rocking-curve, halt-pole, exposure-schedule, artifact, contract, switches, routing,
       roadmap, level-4]
related:
  - frozen-interference-graph.md
  - holographic-untangling-methods.md
  - behavior-is-tape-resident-reduction.md
  - write-not-train-ternary-routing-deltas.md
  - ../attention-holographic-readout.md
  - ../register-theory-of-quantization.md
  - ../holographic-reduction-machine.md
  - ../ternary-holographic-memory.md
depends-on:
  - frozen-interference-graph.md
  - holographic-untangling-methods.md
  - behavior-is-tape-resident-reduction.md
created: session 308
---

# Optical Design Laws

> s308 capstone (thinking session; experiments hand to next session). Michael:
> "How does that inform our designs? We have the understanding, but I don't
> know enough to bridge the gaps." The bridge is the one optics itself used:
> **every plate-physics principle became a device** (correlator, multiplexed
> storage, adaptive optics, interferometer). Each measured clause of our
> theory licenses a specific device. Six laws → five devices → the existing
> experiment queue turns out to be the devices' validation gates.
>
> Status open. The keystone experiment (composition + angle-prediction) is
> NOT pre-registered — s222: freeze on this page or the write-not-train page
> before any run.

## Derivation base (s308 inference-dynamics thread, captured here)

The laws below rest on four clauses worked out in the s308 discussion
(companion to `frozen-interference-graph.md`; may deserve their own inference
page later):

- **Attention softmax = operand selection, not rule selection.** Heads are
  matched filters with the rule compiled into QK/OV; the attention
  distribution is amplitude-normalized *argument* mixing (soft β). No rule
  choice exists inside a pass — all matching reductions run superposed
  (speculative execution); the only genuine probability event is sampling
  (= retirement to the tape).
- **Routing IS compute (Shannon).** Every block factors as a dynamic SWITCH
  (QK→softmax; SwiGLU gate — the network's ONLY nonlinearities) wired to a
  static linear PLATE (OV; down_proj = stored values). Linear plates alone
  compose to one matrix; all expressivity is the interleaved switching.
  Ternary {−1,0,+1} = the complete native alphabet of a switch → the entire
  quant arc's scope falls out (wire survives ternary; base plates are
  magnitude-salient; s260 binarize-router-keep-value measured it causally).
- **Projection = multiply-then-propagate.** A hologram is projected by
  illuminating the frozen fringes with the recording's reference beam: the
  plate multiplies (q·k, gate·key), propagation sums with phase (the value
  sum into the residual). Inference = 36 plate stages in series with
  switches between them; the beam is the prompt's own evolving state.
  Measured Bragg instance: s304 — the country key fires on NAME frames,
  never on landmark prompts; same content, wrong reference angle, zero
  diffraction.
- **Two flagged disanalogies (do not glaze):** detection law is exp(logit)
  not |amplitude|² (softmax vs Born — open whether meaningful); and the beam
  is ALSO the memory (residual = reference + accumulating reconstruction),
  which passive optics lacks — the dynamics live in the illumination.

## The six design laws

**L1 — Ship (plate, reference-contract) pairs; never plates alone.** The
plate is passive; no image without the matching beam. An artifact is a tensor
PLUS its illumination contract: base hash, layer band, key-geometry
fingerprint, prompt frame, verification gates. Every s304/s305 inert write
was a plate no beam ever illuminated at the recorded angle — a format
requirement, not an ad-hoc failure mode.

**L2 — Measure the beam before writing the plate.** All four inert
constructions wrote first and hoped the illumination matched. Characterize
the bench, then cut the grating: writes are designed FROM measured beam
geometry (the rocking-curve surface), never from guessed geometry.

**L3 — Record off-axis, always.** Separability is fixed at write time
(twin-image law). Never fine-tune a base in place: freeze the reference,
record deltas, keep the delta-log (git-for-weights). Standing law for every
training run this project performs.

**L4 — Extract switch schedules, not weight blobs.** Compute lives in the
switch fabric; switches need trits. The level-3 extraction target (the
verbum mission) is stated in the routing register: which heads couple where,
which keys fire, in what order. This is why λ smallest's ~0.1% goal is
plausible: a circuit's wiring diagram is tiny relative to its recording
medium.

**L5 — Bake steps, not chains.** Behavior deeper than the depth budget is
tape-resident (trampoline law). Skill plates improve single contractions;
the scaffold/handler carries the chain. Corollary: train on crisp collapsed
outcomes (mode-commit, s296–298), because the tape is the discrete register.

**L6 — Compose by angle separation.** Multiplexed storage works because each
page owns a reference angle. Two skill plates compose iff their reference
geometries do not collide — a measurable PRECONDITION (principal angles
between key subspaces), not a hope.

## The five devices

| Device | Optics ancestor | What it is | Law | Gap it closes |
|---|---|---|---|---|
| **A. Plate linker** | angular multiplexing | Takes two ternary plates + base: measures principal angles between key subspaces, PREDICTS interference, merges, verifies both frozen gate sets | L6 | Composition with a predictor — the ecosystem primitive |
| **B. Beam profiler** | rocking curve | Per-layer map of what reference geometry the base's gratings respond to (layer × angle × strength efficiency surface) | L2 | Would have prevented all four inert writes; the write-targeting map |
| **C. Reference-contract format** | lens datasheet | Artifact metadata spec: base hash, band, geometry fingerprint, prompt frame, gates | L1 | Turns the ~600KB wire (27ce260) into a distributable object |
| **D. Halt-pole detector** | photodetector on the scheduler | Runtime readout of the 17×17 outcome register: "stuck on a free variable" signal before the tool call forms | L5 | Crystal corpus → agentic products bridge |
| **E. Exposure-schedule spec** | recording protocol | Bake discipline hardened: frozen reference, mode-commit targets, coherent edge-share curriculum (A2) | L3 | Makes gradient-finds → ternary-stores a reproducible pipeline |

## Experiments = validation gates (the queue re-typed)

The s308/s309 candidate probes are not a menu of curiosities — each validates
a device:

- **P-HALT-POLE** (behavior-is-tape-resident-reduction.md) → validates **D**.
- **Rocking-curve instrument** (holographic-untangling-methods.md (iv)) →
  IS **B**.
- **Composition + angle-prediction** (below) → validates **A** (and stresses
  C's contract fields).
- **P-COHERENT-WRITE + reference-drift** (frozen-interference-graph.md,
  holographic-untangling (i)) → validate **E**'s curriculum clauses; shared
  harness.
- **GD k-step sweep** (holographic-untangling (ii)) → prices **E**'s search
  stage (feedback-vs-search).

## The keystone: composition with angle-prediction (recommended first build)

One ~600KB wire is a demo. TWO wires, independently baked, merged by a
linker that PREDICTED their compatibility from measured angle separation,
both verified against their contracts on one frozen base = an **ecosystem
primitive**: git-for-weights with a type checker. Devices B/D/E improve the
primitive; only A+C make it exist.

**Pre-registrable prediction (what elevates this above try-and-see):**
retention of each wire under merge degrades as a function of measured
key-subspace angle collision — smooth in the overlap, near-perfect at
orthogonality. Holds → the SELECTION RULE for arbitrarily many plates on one
base. Fails → the multiplexing clause of the frame takes named damage.

Sketch (freeze properly before running, s222): bake wire-2 on a disjoint
task (different relation, same recipe as gd_cd); measure principal angles
between the two deltas' key subspaces per layer; arms = base / wire1 /
wire2 / wire1+wire2 (linker merge) / wire1+rotated-wire2 (angle-collision
control: rotate wire-2's factors into wire-1's subspace at matched norm —
the λ yardstick for the predictor) / shuffle. Gates: each wire's ORIGINAL
frozen gate set re-scored under merge + cross-interference CE + the
degradation-vs-angle curve against the rotated control.

## Provenance

- s308 thinking session (Michael's arc: "little to show" → optics untangling
  → tape-resident behavior → frozen interference graph → inference dynamics →
  "how does this inform our designs"). Laws/devices drafted by AI,
  Michael-approved for capture. Experiments hand to next session (Opus).
- Measured anchors inherited from the three sibling s308 pages + s260, s296–
  298, s303 (072c3e0), s304 (cb73ad5, ec77c4d), s305 (420ffe3, ee8a5bb),
  s306–s308 quant arc (4b89726, 0a89531, 27ce260).
