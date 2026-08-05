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
> **FROZEN as §P-PLATE-LINKER-1 (s311, Michael-approved)** — see the keystone
> section below. Build + run pending.

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

### §P-PLATE-LINKER-1 (FROZEN s311, Michael-approved)

**The claim (pre-registered, falsifiable).** Two independently-baked ternary
wires on ONE frozen base compose additively (each retains its own frozen gate
set) **iff their KEY subspaces are angularly separated**, and
retention-under-merge degrades as a **monotone function of measured
key-subspace principal-angle collision** — near-perfect at orthogonality. The
measured angle **PREDICTS** the retention loss ⇒ the linker is a predictor,
not try-and-see.

**Why key-subspace is the precondition (theory).** For input x,
`(Δ1+Δ2)x = Δ1x + Δ2x`. If the wires' A (key/input) row-spaces are orthogonal,
at most one delta fires per input → no interference *regardless of B* (L6).
So the primary predictor is the principal angles between the two wires'
per-layer A row-spaces (FFN L22–L29), aggregated to a scalar collision
`c ∈ [0,1]` (mean over layers of `‖P₁P₂‖_F²/r`, projectors onto the r=16 A
row-spaces). B (value/output) collision is reported SECONDARY — it should only
bite where A already collides.

**Wire-1** = the existing gd_cd wire: landmark→country→capital hop-2
(writeback_compile recipe, LoRA r=16 FFN L22–L29, KL-on-CoT teacher, 3 seeds,
ternary factors per §TERNARIZE-FACTORS-1 retention ~1.0). Frozen gates G1–G5,
splits TRAIN / B1 held-landmark / B2 held-country.

**Wire-2** (Michael-approved fork = same relation, DISJOINT country/landmark
partition — the most discriminating case): SAME recipe verbatim, a disjoint
bank of countries+landmarks. **Naturally decouples the two collisions:**
different countries ⇒ *low A-collision* (different key filters), same output
type ⇒ *high B-collision* (both write the capital region). This is a direct
test of the key-subspace-precondition claim — low A-collision should compose
despite high B-collision. Wire-2 must pass its OWN frozen G1/G3 standalone
before any merge (bake gate). A different-skill wire (element→discoverer→…)
gives trivially-low A ∧ B collision → less discriminating; deferred to
§P-PLATE-LINKER-2.

**Arms** (reuse writeback_compile + ternarize_factors, no fork — λ one_way):
- `base` — frozen host (floor).
- `wire1` / `wire2` — each installed alone (reproduce their standalone gates).
- `wire1+wire2` — the NATURAL linker merge (additive: base + Δ1 + Δ2).
- `wire1+rotated-wire2(θ)` — the COLLISION SWEEP (λ yardstick): rotate wire-2's
  A row-space toward wire-1's at **matched Frobenius norm and FIXED B2**, θ
  swept over a frozen grid → synthesizes the collision axis from `c_nat` to
  ~1. (Rotated wire-2 no longer computes its task — it is a geometry control
  for wire-1's retention, not a functional wire.)
- `shuffle` — deranged wire-2 factors at matched norm/sparsity (the mass-floor
  yardstick: adding random matched-mass should degrade wire-1 like noise).

**Gates** (verbum.dsp, paired-permutation 10k, primaries Bonferroni α/N):
- **PL1 COMPOSES** (primary) — under `wire1+wire2`, BOTH wires still pass
  their own frozen **G1 (wire, flip on B1∧B2)** + **G3 (specificity)**.
- **PL2 ANGLE-PREDICTS** (KEYSTONE primary) — the θ-sweep yields a monotone
  retention-vs-`c` curve (slope > 0, p<0.05 vs flat/shuffled-`c` null) AND the
  natural pair's retention falls within the curve's bootstrap CI at its
  MEASURED `c_nat`. This is what elevates the linker to a predictor.
- **PL3 COLLISION-CAUSAL** — `wire1+rotated-wire2` degrades wire-1 MORE than
  `wire1+wire2` at MATCHED added norm ⇒ degradation is collision, not mass
  (p<0.05).
- **PL4 HOST-SANE** (value register, advisory) — innocent-text CE within 2%
  rel base under merge; native g/h within 0.10 absolute.

**Verdicts:** `LINKS(+ANGLE-PREDICTIVE)` (PL1∧PL2∧PL3 — the selection rule for
N plates on one base EXISTS; the git-for-weights primitive is validated) /
`LINKS-OPAQUE` (PL1 ∧ ¬PL2 — merges but not predictable from angle) /
`COLLISION-BLIND` (PL1 ∧ ¬PL3 — degradation is mass, the angle story is wrong)
/ `NO-COMPOSE` (¬PL1 — wires do not co-exist even near-orthogonal → the
multiplexing clause of the frame takes named damage) / `HOST-DAMAGED` (PL4
dominates).

**A-priori (NOT tuned; bases/grid/nulls/gates frozen before any run).** r=16
subspaces in ~2560-dim FFN input → dimension-counting ⇒ natural A-collision
likely LOW → lean **~55% LINKS(+ANGLE-PREDICTIVE) / ~25% LINKS-OPAQUE** (curve
too flat/noisy at 8 layers × few θ to *call* predictive) / ~12% COLLISION-BLIND
/ ~6% NO-COMPOSE / ~2% HOST-DAMAGED. GENUINELY OPEN: same-relation wires may
route through a SHARED country-detector subspace (high A-collision despite
disjoint entities) → a real high-`c` natural point that stress-tests the
predictor (good) OR forces NO-COMPOSE (informative failure).

**Cadence (s222):** freeze (this) → bake wire-2 + verify standalone gates →
build plate_linker.py (+ `--validate` ALL PASS, ruff, no diags, smoke green,
direction NOT read) → Michael GO → run tmux main:1 → frozen scoring. Validates
**device A** (and stresses **C**'s contract fields: base hash, band, geometry
fingerprint = the measured `c`).

## Provenance

- s308 thinking session (Michael's arc: "little to show" → optics untangling
  → tape-resident behavior → frozen interference graph → inference dynamics →
  "how does this inform our designs"). Laws/devices drafted by AI,
  Michael-approved for capture. Experiments hand to next session (Opus).
- Measured anchors inherited from the three sibling s308 pages + s260, s296–
  298, s303 (072c3e0), s304 (cb73ad5, ec77c4d), s305 (420ffe3, ee8a5bb),
  s306–s308 quant arc (4b89726, 0a89531, 27ce260).
