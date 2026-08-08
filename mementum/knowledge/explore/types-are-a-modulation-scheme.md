---
title: "Types Are a Modulation Scheme — the Signal-Domain Reframe of the Type Arc"
status: open
category: explore
tags: [types, dsp, holography, modulation, carrier, cdma, spread-spectrum,
       coherent-integration, lock-in, phase-conjugation, bragg, dark-field,
       tape-resident, two-tier, pre-reg-candidate, s324]
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

## Read discipline

The retrodictions are POST-HOC pattern-suggests (λ observation) — they
motivate the frame; they do not license it. The frame earns claims only
through the unfrozen probes above, each needing its own freeze + gates +
a-priori + nulls (λ yardstick: the modulation frame is flexible — every
gate must beat a matched null, and LOCKIN's f_mod detection must beat
shuffled-modulation-schedule nulls or it is describability, not discovery).
