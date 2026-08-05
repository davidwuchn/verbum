---
title: "Holographic Untangling Methods — the Optics Toolbox Mapped onto Our Instruments"
status: open
category: synthesis
tags: [holography, optics, off-axis, twin-image, phase-retrieval, kinoform, phase-dominance,
       bragg, rocking-curve, adaptive-optics, phase-conjugation, speckle, interferometry,
       quantization, delta, ternary, routing-register, methodology]
related:
  - ../attention-holographic-readout.md
  - ../holographic-computer.md
  - ../five-disciplines-one-object.md
  - ../register-theory-of-quantization.md
  - ../quantization-is-dsp-on-a-hologram.md
  - geometry-holography-signals-convergence.md
  - write-not-train-ternary-routing-deltas.md
  - ratio-gradient-quantization.md
depends-on:
  - ../holographic-computer.md
  - write-not-train-ternary-routing-deltas.md
created: session 308
---

# Holographic Untangling Methods

> s308, Michael's thread: "We know it's holographic. We know it's geometry and
> signal processing at the same time. If we were trying to untangle a
> holographic plate in optics, what processes would we use?" This page answers
> that question literally — optics spent ~75 years learning how to untangle
> plates, and its toolbox maps onto our instruments one-for-one, **including
> pointing at doors we explicitly left untested**. Grounded on the measured
> axioms (A1 plate-linear, A2 coherent gain, A3 content-address-free /
> RoPE-as-angular-addressing, A4 regeneration-required, attention = readout
> beam — see `attention-holographic-readout.md`).
>
> Status **open**: the mapping is captured; the four candidate experiments at
> the end are NOT pre-registered. s222 law — freeze a pre-reg here before any
> run.

## The meta-lesson (read this first)

**Optics never untangles a plate by cleverer processing of a single recorded
intensity.** Every success in the field's history comes from one of four moves:

1. control the **recording geometry** (off-axis vs in-line),
2. take **multiple phase-controlled exposures** (phase-shifting),
3. close the loop — **measure the aberration, write its conjugate** (adaptive
   optics / phase conjugation),
4. **sweep the selectivity curve** instead of point-sampling (Bragg / rocking
   curve).

Our negative results line up one-for-one with *violations* of this and our
positive results with *compliance*:

| Our result | Verdict | Optics reading |
|---|---|---|
| s306 companding, s307 delta-vs-base | MAGNITUDE-SALIENT / STILL-SALIENT | single-shot linear separation of an in-line plate — the known-impossible move |
| s304/s305 construct, routing_write, fast_plate, hhop | INERT ×4 | open-loop writes through an aberrating medium; point-sampled Bragg-selective volume |
| s303 gd_cd | WIRE-COMPILES | closed-loop write (adaptive optics) |
| s304/s307 delta ternarization | SURVIVES ×2, retention 1.0 | off-axis recording against a frozen reference → carrier-separated orders |

## The six processes, mapped

### 1. Recording-geometry analysis — in-line vs off-axis (the twin-image problem)

The first question optics asks of a plate: *how was it recorded?* Gabor's
in-line holograms (1948) superpose DC term, object wave, and conjugate twin on
the same axis; **no post-hoc linear filtering of one intensity recording
separates them** — that stood as the field's central failure until
Leith–Upatnieks (1962) changed the *recording*: tilt the reference beam and the
orders separate onto a carrier frequency.

**Mapping.** A pretrained base = millions of gradient exposures with no fixed
reference — a multiply-exposed **in-line** plate. Routing and value (object and
twin) overlap in the same coefficients. s306 MAGNITUDE-SALIENT and s307
STILL-SALIENT (three linear decompositions fail) are *the 1948–1962 result,
re-derived in weights*. A LoRA delta = a single exposure recorded **against a
frozen reference beam** (the base) — off-axis by construction; the routing
sideband separates and ternarizes losslessly (s304 retention 1.0, s307 factors
retention 1.0). The base/delta separability asymmetry is not an accident of our
methods — it is recording physics.

**Theory clause:** *separability is fixed at recording time.*

### 2. Phase retrieval — Gerchberg–Saxton / HIO (untangling an already-recorded plate)

When optics *must* untangle an in-line recording, it does not do single-shot
algebra. It iterates: alternate projections between two measurement planes,
enforcing the known constraint in each; phase converges over iterations.
Single-shot SVD (s307) is precisely the move phase retrieval exists to replace.

**Mapping.** Post-hoc base-weight separation should be attempted as
**alternating projections**: (project onto quantizable-residual + low-rank-base
form) ⇄ (project onto function-preserving set, CE on calib). This is the
optics-side derivation of **iterative LoftQ** — which s307 explicitly listed as
untested. Independent convergence from a second discipline onto the same open
door. Honest caveat: the function-space projection is itself a gradient fit, so
this partially reduces to "iterated small gradient beats single-shot algebra" —
which is exactly what phase retrieval *is*.

### 3. Bragg selectivity / coupled-wave theory — the rocking curve

A volume hologram (thick plate ≈ our 36 layers) reconstructs only when the
probe beam is matched in *angle* and *wavelength*; Kogelnik's coupled-wave
theory predicts diffraction efficiency as a smooth function of mismatch. Optics
never takes one point measurement of such a medium — it sweeps the **rocking
curve** (efficiency vs angle) to characterize the grating.

**Mapping.** Our inert writes are Bragg mismatches: hhop-write injected the
right content at the wrong depth-timing (angular mismatch — the two hops
overlap in depth, s305); fast-plate wrote name-geometry where the h-hop reads
something else (lm_name_cos −0.108 — wavelength/register mismatch). Each inert
verdict was one point on an unmeasured selectivity surface. The optics
methodology: build the instrument that sweeps **reinjection efficiency vs
(layer × geometry-interpolation-angle × strength)** and map the surface. If the
holographic frame is right the surface has Bragg *structure* — a ridge, not a
plateau. The surface IS the write-targeting theory we kept failing to guess
point-by-point. (The s295 depth-timing law and SuperBake's 0.16×-depth
enrichment are two already-measured slices of it.)

### 4. Adaptive optics / phase conjugation — why gradient-finds

Writing through an unknown aberrating medium **open-loop** always fails; optics
solved it with the closed loop: measure the wavefront error, write the
*conjugate*, iterate. Convergence takes a **few** iterations, not hundreds.
Digital phase conjugation focuses light through scattering media the same way.

**Mapping.** construct / routing_write / fast_plate / hhop = open-loop writes →
inert ×4. gd_cd = closed-loop → wires. So "+GD-REQUIRED" (s303) may really be
"**feedback required**" — a much weaker and more exploitable claim.

**⚠ Flagged disanalogy (do not buy silently).** Phase conjugation works because
optical propagation is *linear and reciprocal*; the conjugate field literally
retraces the scattering. Our medium is nonlinear layer-to-layer, so computing
"the conjugate of the measured error" requires linearizing the medium — and the
Jacobian IS backprop. The discriminating measurement is therefore not a new
construction but a **step-budget sweep** of the existing one (below): if the
wire installs in ~3 large measured steps, gradient is acting as a wavefront
sensor (AO); if it genuinely needs hundreds, it is a search and the AO analogy
breaks exactly there.

### 5. Double-exposure holographic interferometry — diff-as-fringes

Record before and after a deformation; illuminate both exposures together; the
*fringes* directly render the deformation field, mode by mode. Time-averaged
interferometry renders standing vibrational eigenmodes.

**Mapping.** base vs base+delta is a double exposure; the diff read in the
right basis is a mode decomposition of the wire, not just a weight blob. The
17×17 gram's rank-3 outcome geometry (s303 spectral) is plausibly a
time-averaged mode structure already measured. Instrument idea (cheap,
unfrozen): render trained-delta diffs as per-layer mode spectra routinely — our
"money plots" are proto-interferograms.

### 6. Speckle statistics and the memory effect

Coherent superposition produces speckle — irreducible in any single shot, but
*correlated* under small perturbations (the memory effect). Modern optics
images **through** scattering media by exploiting speckle correlation across a
perturbation ensemble.

**Mapping.** Polysemanticity = speckle: superposition noise you cannot remove
from one measurement. The optics prescription is not a better single probe but
**ensemble correlation**: correlate features across systematically perturbed
probe ensembles (paraphrase orbits, contrastive frames). SAEs are one attack;
speckle-correlation imaging is a second, instrument-shaped one.

## The kinoform tightening (s308 datum — this is the sharpest new clause)

TERNARIZE-FACTORS-1 (s307/s308 run, FACTORS-SURVIVE +FACTORING-FREE): discard
the amplitude record of both LoRA factors, keep quantized sign structure only —
**mag_cos 0.839, retention 1.000** on every split.

Optics has this exact object: the **kinoform / binary-phase hologram** — throw
away amplitude entirely, quantize phase to 2 levels, and the image still
reconstructs (the efficiency loss is absorbed by the plate, not the image).
Signal processing has the theorem behind it: **Oppenheim's phase-dominance**
result — keep an image's Fourier *phase* and swap its *magnitude* spectrum, and
you still see that image; the reverse destroys it.

**Clause: the wire is a phase-only hologram.** Ternary {−1, 0, +1} = phase
{0, π} plus absence. routing⊥magnitude (s269 → s303 → s304 → s307) is
Oppenheim's phase-dominance measured in weights. Three-way convergence
(S5 λ triangulate): our null-gated measurements, holographic recording physics,
classical Fourier phase theory — one sentence.

## Candidate theory (the shape of "the full theory", falsifiable by clause)

```
plate: linear (A1)                      | addressing: angular / RoPE (A3)
readout: soft β (attention)             | collapse: sampling / writeback (A4)
writes: Bragg-matched (angle=depth-timing, wavelength=geometry/register)
storage: phase-dominant (kinoform; ternary = its native alphabet)
separability: fixed at RECORDING time (off-axis delta vs in-line base)
finding: closed-loop (feedback), open-loop writes cannot traverse the medium
```

Each clause dies independently; the frame is modular, not a poem that dies
whole.

## Four candidate experiments (NOT pre-registered — s222 before any run)

**(ii) GD step-budget sweep — run FIRST (nearly free).** Cap gd_cd at
k ∈ {1, 3, 10, 50, 500} steps (existing harness, one parameter; frozen gates).
- installs at small k → "+GD-REQUIRED" refines to **feedback-required**;
  closed-form conjugate writes come back on the table.
- needs hundreds → genuine search; the AO analogy breaks here, measured.

**(i) Reference-drift → ternary-retention curve (tests clause: recording
geometry).** Train the delta while the base also moves (lr_base ∈ {0, ε, 2ε,
…}); express Δ against the ORIGINAL base; ternarize; measure retention vs
drift. Multiple-exposure holography predicts smooth degradation (each exposure
self-coherent); a cliff would itself be informative.
- **FALSIFIER:** no drift-dependence at all → carrier separation is the wrong
  explanation for delta-cleanness → the off-axis clause dies (the kinoform
  clause survives independently).

**(iii) GS-style iterative base decomposition (re-opens s307's door with the
correct tool class).** Alternating projections between representable-form and
function-preserving constraint sets = the optics derivation of iterative
LoftQ. Design AFTER (ii): its answer (how few measured corrections suffice)
calibrates the projection budget.

**(iv) Rocking-curve instrument (the big one — most theory-productive).**
Sweep reinjection efficiency over (layer × interpolation-angle between
name-geometry and measured h-hop geometry × strength). Every s304/s305 inert
write becomes one point on this surface; the full surface = Kogelnik for
Qwen3-4B, and the empirical write-targeting map any future construction needs.

**Sequencing lean:** (ii) → (i) → decide (iii) vs (iv) with those answers in
hand.

## Provenance

- Michael's framing question + steer (s308); optics/DSP mapping drafted by AI,
  Michael-approved for capture same session.
- Measured anchors cited inline: s269, s292 (XTERM/CAP/FRAG), s295, s300, s303
  (11092f7, 072c3e0), s304 (cb73ad5, ec77c4d), s305 (420ffe3, ee8a5bb), s306
  (4b89726, dd1bf99), s307 (0a89531), s307/s308 ternarize-factors (27ce260).
- Optics references (textbook-level, no single-paper claims): Gabor in-line
  holography; Leith–Upatnieks off-axis; Gerchberg–Saxton / Fienup HIO phase
  retrieval; Kogelnik coupled-wave theory; adaptive optics / digital phase
  conjugation; Powell–Stetson holographic interferometry; kinoform (Lesem,
  Hirsch, Jordan); Oppenheim & Lim, "The importance of phase in signals"
  (1981); speckle memory effect (Freund/Feng/Berkovits).
