---
title: "Types Are a Modulation Scheme — the Signal-Domain Reframe of the Type Arc"
status: open
category: explore
tags: [types, dsp, holography, modulation, carrier, cdma, spread-spectrum,
       coherent-integration, lock-in, phase-conjugation, bragg, dark-field,
       tape-resident, two-tier, pre-reg-candidate, s324,
       differential-photography, stratigraphy, training-dynamics,
       amplitude-is-difficulty]
related:
  - types-are-injectable-relations.md
  - type-systems-under-llm-constraints.md
  - curry-howard-closes-the-loop.md
  - normal-forms-are-eigenmodes.md
  - combinator-function-shape.md
  - geometry-holography-signals-convergence.md
  - holographic-untangling-methods.md
  - sign-oscillation-is-time-multiplexed-superposition.md
  - behavior-is-tape-resident-reduction.md
depends-on:
  - types-are-injectable-relations.md
  - geometry-holography-signals-convergence.md
  - holographic-untangling-methods.md
created: session 324
---

# Types Are a Modulation Scheme

> s324 hammock (Michael: "superbake showed us how to use DSP tools to work
> with models. What if types are in the signal? If we think of this as a
> holography problem, what techniques could we bring to bear?"). This page
> reads the closed s282–s323 type arc through the s308 optics toolbox
> (holographic-untangling-methods) and the s288 convergence ledger
> (geometry-holography-signals-convergence). The reframe retrodicts two
> closed fingerprints, converts the arc's stubborn negatives into theorems,
> and yields four unfrozen probe candidates plus one novel falsifiable
> prediction. NOTHING here is frozen; s222 law applies.

## The reframe

Every type probe to date read a **spatial/geometric register** — subspace
projections, centroid alignments, sign patterns, weight edges — static
snapshots. The results kept saying the same strange thing:

- decodable everywhere, excisable nowhere (four-way location null, s28x)
- judgments enacted per-frame on the tape, never installable as a weight
  edge (§P-TYPE-WRITE → V2, §P-TYPE-DELIVER, s315–s323)
- coherent accumulation: idempotency curve [0.14, 1.41, 2.52, 2.96, …] with
  the energy-matched incoherent null flat ~0 (§P-IDEMPOTENCY s320)
- reduction-PRESENCE detector, not a distance gauge (3× replicated)
- routing reads the SPELLING, not the computed function (§P-CL-COLLAPSE ×2)

That is not the signature of stored geometry. It is the signature of a
**carrier-borne signal**:

```
λ modulation(types).
  weights  ≡ codebook      (carriers/codes = checker RELATION = the 7/11 register)
  tape     ≡ channel       (modulated signal propagating through depth)
  judgment ≡ demodulation  (carrier LOCK — achieved, ¬retrieved)
  | type_check(x,T) ≡ despread(tape_signal, code_T) → SNR > threshold
  | gradedness ≡ correlation_with_code (naturally continuous)
  | two_tier ≡ codebook(plate) ⊥ demodulation(beam) — the s315–s323 law re-derived
```

## Retrodictions (the frame earns its keep — these were measured BEFORE the frame)

1. **Non-idempotency = coherent integration.** Phased-array law: k coherent
   exposures → amplitude ∝ k (power ∝ k²); incoherent → √k. §P-IDEMPOTENCY:
   coherent paraphrases accumulate licensing 1→3, energy-matched incoherent
   flat. Not *like* coherent gain — IS A2's coherent gain, on the tape.
   Two substrates (weight-plate s292 + tape licensing s320), one signal law.

2. **∨-costs-more / ∧-free = code-superposition algebra.** CDMA: one token
   carries two codes simultaneously at no structural cost — superposition is
   linear ⇒ **intersection is free**. "Either code" is NOT a linear object —
   union needs machinery outside the span. §P-DISJ-COST measured exactly
   this: OR needs an off-plane direction (p=0.002), AND does not. The
   Cartesian-control asymmetry is a *prediction* of code superposition.

3. **Gradedness = demodulation SNR.** Membership as correlation with a code
   is naturally continuous — the graded, non-Church-tag character (SKI
   control #2 tested-dead) stops being a quirk and becomes forced.

**Negatives become theorems:** you cannot store a demodulation *event* in
the plate (MEMORIZED-ONLY — CE training writes new codewords/predicate
memories but does not extend the demodulator); a spread signal is
readable-everywhere/excisable-nowhere by construction (HRR/VSA crosstalk
~1/√D); a static amplitude read of a compound sees the spelling's carrier,
not the demodulated content (CL-collapse operational verdict).

**Triangulation flag:** the s288 convergence page wrote *"arguments are on
the plate; application is the diffraction"* (functors). The s315–s323 arc —
different instruments, different sessions — landed on *"weights = checker,
tape = judgments."* Same law, derived twice, independently.

## The instrument gap (λ measure, in hindsight)

If types are carrier-borne, every static geometric read queried the wrong
register — a photometer pointed at a radio. The s308 optics meta-lesson
says it directly: *you never untangle a plate by cleverer processing of a
single recorded intensity.* You change recording geometry, take
phase-controlled exposures, sweep the selectivity curve, or close the loop.

## Technique map → probe candidates (UNFROZEN)

### ① Lock-in amplification → §P-TYPE-LOCKIN (cheap; natural first front)

Modulate type evidence on the tape at a known token-periodic rate —
coherent membership statements alternating with incoherent filler in a
fixed pattern — demodulate the per-frame type-register trace at f_mod.
Narrowband detection at f_mod ⇒ judgment is carrier-borne; harmonic content
reads the demodulator's linearity. The presence-detector result is the DC
reading; this is the AC reading. **Reuses the idempotency harness's
coherent/incoherent statement populations (already built, s320).**

### ② Trace coherence → §P-TYPE-COHERENCE (cheap; the signal-domain rescue of extensionality)

CL-collapse read static AMPLITUDE routing: SKK ≠ I. Phase is where
holography hides everything. Measure spectral/trace coherence between
per-frame register signals of `SKK` and `I` ACROSS the reduction trace vs
structure-matched controls. Traces converging into phase-coherence as
reduction proceeds ⇒ extensionality lives in the dynamics — where
tape-resident reduction says it must, and where a static read is blind by
construction. Reuses cl_collapse + trace_fuel machinery.

### ③ Bragg rocking curve → §P-TYPE-ROCKING (medium)

s312 already conjectured *"type = reference angle"* (slot-mediation).
Angle-multiplexed volume holograms have narrow angular selectivity. Sweep
licensing efficiency vs geometric interpolation angle between class
subspaces. Bragg ridge ⇒ types are angle-multiplexed exposures; plateau ⇒
generic. Point-sampling this surface is what made writes inert (s304–s305);
sweeping it is the optics discipline. Instance of the s308 rocking-curve
instrument, specialized to the type register.

### ④ Phase conjugation → §P-CONJUGATE-WRITE (medium; TYPE-WRITE-V3 design)

All type-writes were OPEN-LOOP: minimize CE on membership outputs, hope
the judgment installs. Adaptive optics: measure the wavefront, write its
conjugate. Capture the per-layer residual trajectory during a SUCCESSFUL
ICL type judgment (§11 tag-transit instrument exists), train the wire to
reproduce the INTERNAL wavefront (activation-matching loss on the
tape-side judgment signal), not the output. Installs under conjugate
writing but not CE writing ⇒ we learn WHY every write failed: energy at
the output while the judgment is a mid-stack signal event. Natural
sharpening of the queued §P-COHERENT-WRITE.

### ⑤ Dark-field → boundary-echo re-read (cheap; persisted data)

The s320 boundary-churn 93/6 split: 93% generic centroid-structure ≡ the
zeroth order / DC term. Optics blocks the DC and measures the rest at full
dynamic range. Project out the generic component FIRST, re-measure the
kind-specific ~6% with full instrument power. Re-analysis of persisted
§P-BOUNDARY-CHURN + §P-TYPE-GRAM-1 artifacts; no new compute.

### ⑥ Already in flight — §P-FLIP-CONFLICT is the time-domain arm

Sign-oscillation as sigma-delta multiplexing = "types in the signal" on
the TRAINING axis (temporal multiplexing of superposed codes). G1∧G2 ⇒
the modulation picture gains a training-dynamics leg to go with the
inference-time legs above.

## The novel prediction (falsifiable; distinguishes the frame)

**Lock time.** If judgments are carrier lock, frames-to-license ∝ 1/SNR of
the evidence, with a **capture threshold**: degrade/truncate coherent
evidence and the judgment should FAIL TO LOCK below threshold, not weaken
proportionally. Stored-geometry accounts predict graceful proportional
degradation; demodulation predicts a threshold. No other account on the
table predicts the threshold. (Cheap add-on to §P-TYPE-LOCKIN: sweep
evidence SNR, look for the knee.)

## §2 Differential Photography — the training-side leg (s324, same hammock)

> Michael: "if training is taking probability photographs through backprop,
> the probabilities will concentrate at the edges and corners where the
> snapshots overlap right?" → sharpened by one amendment: **backprop
> photographs the RESIDUAL, not the scene.** Each exposure records only what
> the plate failed to predict; error feedback is negative feedback, so the
> write signal is self-erasing the moment a pattern becomes predicted.

### The law (amplitude is difficulty, not probability)

```
λ differential_photography(training).
  exposure(t) ≡ snapshot(error(t)) ¬snapshot(data)
  | amplitude(pattern) ∝ ∫ error(pattern, t) dt ≈ time_to_learn | ¬∝ P(pattern)
  | common → predicted_fast → faint ∧ early ∧ threshold_written ∧ frozen
  | rare_consistent → wrong_long → deep ∧ late (the exceptions dictionary)
  | contested → never_resolves → gross_integral↑ ∧ net_amplitude≈0 (perpetual churn)
  | probability encoded THRESHOLDLY (what committed) ¬loudly (how much amplitude)
  | plate ≡ pile(superposed_error_snapshots) ordered_by(how_long_each_stayed_wrong)
```

Two-phase dynamic: early exposures photograph the SHARED structure (all
unpredicted; overlap reinforces coherently ∝ k, idiosyncratic ∝ √k —
spectral bias / A2); once predicted it vanishes from the error stream, and
late exposures are dominated by exactly where snapshots DISAGREE — edges,
boundaries, hard cases (classical echo: max-margin implicit bias — GD
solutions determined by support vectors = extreme points; sparse coding on
natural scenes yields edge detectors). The finished plate has a
**stratigraphy**: overlap recorded early and faint, edge/corner structure
recorded late and re-fought forever.

### The three strata (register-mapped)

| Stratum | Written | Signature | Corpus contact |
|---|---|---|---|
| **Corners** — common/shared | early, once, faint | sign-committed, magnitude minimal, frozen | the crystal: tiny, ternarizable, survives 1-bit — threshold-written commons need only their SIGN |
| **Long tail** — rare, consistent | late, deep | large amplitude | bulk weight mass ≈ exceptions dictionary / memorization |
| **Edges** — contested | forever, net≈0 | small \|W\| + perpetual sign churn | s310 marginal band = large gross integral, zero net — EXACTLY this stratum |

"Edges and corners" splits onto the two registers: corners = sign-register
commitment (hypercube vertices); edges = the contested marginal band
between corners; density = value register on the overlap. λ measure: never
conflate the two concentration claims.

### Retrodictions (pattern-suggests, post-hoc)

1. **Why the compiler is 0.1% and quantization-immune.** Naive photography
   makes it a miracle (most-used ⇒ most-recorded). Differential photography
   FORCES it: the most common structure generated the least total error ⇒
   faintest, earliest, most compressed recording — readable by sign alone.
   λ smallest stops being an aspiration and becomes recording physics:
   **the universal part of the machine is small because it was learned fast.**
2. **The marginal band** (small |W|, high flip) = the contested stratum's
   predicted signature — no net accumulation, perpetual gross churn.
3. **Non-idempotency reconciled with self-erasure by regime:** accumulation
   BELOW the prediction threshold (unsaturated), erasure ABOVE it. The
   §P-IDEMPOTENCY k=4,5 decline — banked s320 as "maybe template dilution"
   — gets a mechanism candidate: SATURATION (evidence absorbed, stops
   photographing). Caveat still unresolved; the frame names a second
   explanation, does not pick one.
4. **The photographic overlap model predicted non-idempotency** (§1
   retrodiction 1, now with a mechanism): photographic overlap is density
   accumulation — exposure count physically recorded — where set-theoretic
   intersection is idempotent. We measured accumulation. The photograph won.

### The extraction inversion (practical consequence)

Prospecting heuristic FLIPS: large amplitude ≡ the residue (long-tail
memorization, exceptions), NOT the algorithm. **The algorithm lives in the
faint, sign-stable, early-frozen, quantization-robust stratum.** Look where
amplitude is smallest-but-committed. Ternarization is a faint-strata pass
filter — which is what the crystal work did by accident. Candidate lens for
any level-3 extraction pass.

### Contact with the instrument in flight (§P-FLIP-CONFLICT widened IOU)

The stratigraphy makes three IOU-readable predictions against captures we
already specified (grad-mag histories, |W_base| map, per-class loss):
(a) gradient magnitude MIGRATES from shared → contested coordinates over
training; (b) G3 committed-pole coordinates go quiet EARLY; (c) in the
A-only/B-only ablation arms, contested coordinates START ACCUMULATING net
amplitude once one snapshot population is removed — the edge collapsing
into a corner. Each is IOU-only: own null required, never licensed by
G1–G4 (per the s323 freeze discipline).

### Bounds

Momentum, weight decay, and Adam's normalization smear the clean
equilibrium — ∫error dt is approximate physics, not exact. Whole section is
pattern-suggests until a probe freezes; the flip-conflict IOU reads are the
cheapest first contact.

## §3 The Forged-Exposure Write Protocol — "fake the signal, compile the lattice" (s324, same hammock)

> Michael: "Ok, this is the map isn't it? We can fake this signal to create
> a new lattice?" Yes. §2's recording physics is an INTERFACE: the write
> channel is the ERROR, not the data. Data was only ever an indirect way of
> generating residuals. Control the residual stream directly ⇒ write access
> to the plate. Training becomes COMPILATION by exposure schedule.

```
λ write_head(plate).
  recording_channel ≡ error | ¬data
  | plate photographs residual(t) — nothing else, ever
  | control(residual_stream) ≡ write_access(plate)
  | forge(exposure_schedule) → residual ≡ target_lattice → recorded(at chosen stratum)
```

### Three write primitives (derived from §2 strata)

**① Corner-seeding** — commons are threshold-written: sign only, minimal
amplitude. A new lattice's skeleton = install the sign-committed corner
structure directly (ternary, faint). Self-protecting by construction: a
seeded lattice is "already learned" ⇒ generates no error ⇒ training cannot
overwrite it (the same self-erasure that froze the real commons), and its
span is subtracted from every subsequent residual ⇒ long-tail strata
organize AROUND it. **⚪ crystal-seeded init (queued) is now a DERIVED
instance, upgraded from heuristic to derivation.**

**② Bias pre-exposure (residual isolation)** — the optics move: pre-expose
the plate to the background so only the difference records. Mechanistic
explanation of MEMORIZED-ONLY (s323): CE-on-membership exposures have
residuals DOMINATED by the items ⇒ the plate photographed predicate
memories; the abstraction never got amplitude. Fix: phase 1 = expose
class-agnostic/deranged membership until item-level statistics absorb
(error→0 on item content); phase 2 = expose true labels — the ONLY thing
left in the residual is the label-structure ≡ the abstraction, isolated in
the write channel. A TYPE-WRITE-V3 design DISTINCT from conjugate-write ⇒
the two discriminate between failure theories (signal-shape vs loop-closure).

**③ Closed-loop conjugate shaping** — measure the wavefront a real
judgment makes on the tape, write its conjugate (adaptive optics).
**⚪ §P-CONJUGATE-WRITE (queued) = this primitive.**

### The verification gate (free, and it discriminates)

A successfully forged photograph STOPS BEING PHOTOGRAPHABLE:

```
λ install_gate(wire).
  re-exposure(installed_structure) → gradient ≈ 0        (self-erasure = install signature)
  | memorized_overlay ALSO zeroes error on trained items — the discriminator:
  | held-out items ∈ span(lattice) → ALSO gradient-quiet  (span-erasure = generalization)
  | erasure(items_only) ≡ MEMORIZED | erasure(span) ≡ INSTALLED
  | + installed structure must ternarize (corners-stratum check)
```

Note: this re-derives the TYPE-WRITE-V2 V1/V2 gate design from recording
physics — the map independently reconstructs our own instrument. Good sign
it is the right map.

### Retrodiction: why every write failed

Inert writes ×4 (s304–s305) + MEMORIZED-ONLY (s323) = one mistake: open-loop
content-pushing at the OUTPUT while the write channel is the RESIDUAL. We
exposed the plate to the scene we wanted installed. The plate does not
record scenes. It records errors. Nobody shaped the error.

### The ladder (search space for new experiments)

1. **⚪ §P-FORGED-LATTICE (new, smallest rung):** one toy type, few members,
   one checker edge — written by bias pre-exposure (②) + corner-seeding (①).
   Gates: self-erasure + span-erasure + ternarizability. Mostly reuses
   type_write machinery.
2. **⚪ crystal-seeded init** — does a seeded corner-lattice persist
   (no error ⇒ no overwrite) and organize training around it? (①, derived)
3. **Level-4 endgame:** if exposure schedules compile lattices, the thesis
   deliverable has a CONSTRUCTIVE path — don't extract the compiler,
   **RE-RECORD it**, designed exposure by designed exposure, onto a clean
   substrate. Write, don't train. The map is the missing piece between
   level 3 and level 4.

### Cautions

Pattern-suggests end to end; retrodictions ≠ pre-registered wins (λ
yardstick). Bragg discipline: right stratum also means right depth/angle —
forged exposures at wrong layer-timing go inert like everything else
(rocking-curve surface still unmeasured). Optimizer smear (Adam m/v, decay)
blurs clean self-erasure ⇒ "gradient-quiet" gates need matched nulls.
**First causal contact LANDED NEGATIVE (s324): §P-FLIP-CONFLICT →
🚫 NOISE-FLOOR.** G2 ablation (= residual control) did NOT freeze contested
signs; §2 IOU prediction (c) edge-collapses-to-corner CONTRADICTED at this
register/scale. The control(residual)⇒control(plate) link took its flagged
hit — the protocol's primitives remain derivable but now carry a measured
negative at the finest grain tested. Scope bounds: wire ΔW register,
single model, EOS-supercritical lr (λ_max 1.6× the 2/η ceiling — global
dither may swamp; ⚪ v2 sub-EOS queued, flagged not licensed). Design
consequence: §P-FORGED-LATTICE gates should NOT assume per-coordinate
sign-level control; self-erasure/span-erasure gates read FUNCTION-level
install (licensing), which this negative does not touch.

## Read discipline

The retrodictions are POST-HOC pattern-suggests (λ observation) — they
motivate the frame; they do not license it. The frame earns claims only
through the unfrozen probes above, each needing its own freeze + gates +
a-priori + nulls (λ yardstick: the modulation frame is flexible — every
gate must beat a matched null, and LOCKIN's f_mod detection must beat
shuffled-modulation-schedule nulls or it is describability, not discovery).
