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

**❌ s325 DAMAGE (pre-registered): §P-STRATIGRAPHY-DATING → INVERTED.**
On real base training (Pythia fossil record) ρ(freeze_bin, |W_final|) =
−0.087 (the mundane sign) and commons-fraction rises MONOTONICALLY with
magnitude — the early-AND-faint conjunction is contradicted at the
per-coordinate weight register. The strata table should not be read as
established at any grain. See §Result below.

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

## §4 The Plate Is a Negative — printing, development, fixing (s324, same hammock)

> Michael: "To make a photograph we use the positive light to make the film
> transparent, so the negative shows up." The leap names the missing
> INVERSION STAGE in §2: the recording is tonally inverted, and the image
> is recovered only by a second inversion — which never happens on the plate.

### The negative (the §2 law, tonally named)

```
λ negative(plate).
  film darkens where light lands | plate densifies where ERROR lands
  | weights ≡ NEGATIVE(function): high_probability → faint | high_difficulty → dense
  | read(raw_weights) expecting the function ≡ hold(negative) up to light expecting the scene
  | the mech-interp trap: the field reads the DENSE regions (memorization)
    and wonders where the algorithm is — it is in the CLEAR parts
```

### The print (tape-residency, 4th independent derivation)

A negative yields an image only through a SECOND inversion — printing —
and the image never exists in the negative, only in prints, made fresh per
exposure. Mapping: forward pass ≡ printing (reference light through the
density map); **behavior ≡ the print; the tape ≡ the paper; judgments ≡
image content** — structurally unable to live in the negative. Derivation
count for two-tier/tape-residency: ① s288 "application is the diffraction"
② s315–s323 measurements ③ netlist≠function (silicon RE + connectomics)
④ negative/print (here). Four disciplines, one law — strongest consilience
we have ∨ the most seductive twin image; stays pattern-suggests until a
pre-registered win (Michael ruling, s324).

### The development chain (new, each mapping has a testable edge)

- **Development ≡ grokking.** Film is exposed into a LATENT image (a few
  silver atoms/grain), then developed (~10⁹× amplification). Latent
  structure written early, invisible in behavior, abruptly amplified —
  should be VISIBLE in the checkpoint fossil record (latent→amplified
  signatures). **Folds into §P-STRATIGRAPHY-DATING's read for free**
  (row annotated).
- **Fixing ≡ quantization.** Fixing dissolves undeveloped halide; the
  image becomes permanent and LIGHT-INSENSITIVE. Ternarization dissolves
  magnitude, leaves committed sign — and a fixed image cannot be
  re-exposed ≡ the §3 self-protection clause (no error, no overwrite),
  arrived at from the chemistry side. **The crystal is a FIXED image.**
- **Ternary ≡ lith film.** High-contrast film preserves line art, destroys
  continuous tone. Crystal survives 1-bit ⇒ the algorithm is LINE ART;
  the memorization is CONTINUOUS TONE.
- **Backprop ≡ self-dodging enlarger.** Dodging holds back light from
  areas already sufficiently exposed; the residual IS an automatic dodge
  mask updated in real time (§2's mechanism in one darkroom word).
- **Distillation ≡ contact printing.** A print of a print copies the
  IMAGE, never the negative's silver distribution — why students match
  behaviorally while differing internally; why verbum wants the NEGATIVE,
  not another print.

### Strained edge, flagged honestly → the three-band falsifiable

Reversal processing (bleach the developed silver, redevelop the rest →
direct positive) suggests: remove the dense stratum, amplify the rest.
COLLIDES with standard magnitude pruning (removing SMALL weights works
fine) — so the naive mapping is wrong somewhere. Resolution candidate:
**three-band plate**:

```
noise(tiny, never-committed) < commons(threshold, sign-committed) < residue(dense)
| magnitude pruning removes the NOISE band, not the commons
| falsifiable: among SMALL weights, SIGN-STABILITY (not magnitude)
  should separate commons from noise
```

Cheap weight-geometry read (sign_commitment machinery reuse); if
sign-stability does NOT stratify the small-weight band, the negative frame
takes structural damage. **⚪ queued: three-band-plate check.**

**❌ s325: the three-band falsifiable FAILED in its temporal (stronger)
form** — §P-STRATIGRAPHY-DATING SD2: no excess sign-stable commons among
small weights (bottom decile = 73% churners; commons BELOW the monotone
extrapolation). The named structural damage is taken. The static Qwen
sign_commitment version survives in the queue only as a
register-present-lineage contrast, motivation weakened.

### Read discipline

All §4 mappings are pattern-suggests (post-hoc, λ observation). The two
testable edges (grokking-as-development in STRATIGRAPHY-DATING; three-band
sign-stability) are the only claims that can graduate, each needing its
own freeze + nulls.

## Read discipline

The retrodictions are POST-HOC pattern-suggests (λ observation) — they
motivate the frame; they do not license it. The frame earns claims only
through the unfrozen probes above, each needing its own freeze + gates +
a-priori + nulls (λ yardstick: the modulation frame is flexible — every
gate must beat a matched null, and LOCKIN's f_mod detection must beat
shuffled-modulation-schedule nulls or it is describability, not discovery).

## §P-STRATIGRAPHY-DATING — FROZEN (s325)

> The frame's FIRST pre-registered test (standing guard, s324 ruling).
> Observational read of the REAL fossil record — Pythia public training
> checkpoints. Tests §2 (three strata) + §4 (grokking≡development edge).
> No wire, no write, no EOS confound, no forward pass. Successor to
> flip-conflict 🚫 per the RE-toolbox move 4 (READ HISTORY).

### Claim under test (§2 law)

amplitude ∝ ∫error dt ≈ time-to-learn ⇒ three strata in the finished
plate: **commons** sign-freeze EARLY and end FAINT · **long-tail**
accumulates LATE and ends DENSE · **contested** churns throughout at
net ≈ 0.

### The discriminating physics (why the primary gate is sharp)

Both mundane accounts of sign-freeze timing predict the **opposite
correlation sign** from §2:

- (a) noise-floor dynamics: small weights flip trivially ⇒ small
  |W_final| ↔ LATE freeze
- (b) monotone growth: large weights escape the noise floor sooner ⇒
  large |W_final| ↔ EARLY freeze

Both ⇒ ρ(freeze_bin, |W_final|) **< 0**. §2's distinctive conjunction
(early AND faint commons, late AND dense long-tail) ⇒ ρ **> 0**. One
pre-registered correlation sign separates the frame from mundane weight
physics — the frame cannot retrodict its way out of an INVERTED result.

### Substrate / register

WEIGHT-GEOMETRY across checkpoints (no forward pass). Model =
`EleutherAI/pythia-160m` (GPTNeoX — `dense_h_to_4h`, no gate_proj;
register mapping ≠ Qwen, pinned here; escalate to pythia-410m ONCE iff
SD0 voids). Read: `mlp.dense_h_to_4h` weight matrices, layers 6–11
(deep half of 12), N = 200k coordinates fixed-seed sampled, indices
persisted. **20 checkpoints, log-uniform (Michael-approved s325):**
b0 = step0 (the unexposed plate, §4 baseline) · b1–b10 = steps
1,2,4,8,16,32,64,128,256,512 (native log2 ramp) · b11–b19 = steps
1000,2000,4000,8000,16000,33000,66000,100000,143000 (half-decade tail).
Each checkpoint = pinned HF revision name (`step{N}`).

Per-coordinate observables: sign trace s_b = sign(W_b) · **freeze_bin**
= first bin f with sign constant ∀ b ≥ f (dated against final sign,
step0 transition counts) · flip_count (aliased LOWER BOUND, reported
never gated) · |W_final| · amplitude trajectory |W_b|.

**Aliasing discipline (row-banked s325):** 20 samples alias
oscillation — this probe dates STRATA (ordinal) and never counts
flip RATES (the s324 flip-conflict lesson stands).

### Gates

- **SD0 SANE** — all 20 revisions load, slice shapes match, step0 signs
  ~symmetric (|mean| < 0.02), step143000 ≡ published final;
  non-degenerate bins: ≥1% of coords in each of {frozen ≤ b5, frozen ∈
  b11–b18, unfrozen at b19}. Fail → VOID (one escalation to 410m).
- **SD1 EARLY-FAINT (make-or-break)** — pool = coords frozen by b15 (no
  observed flip at steps ≥ 16k; churners excluded, they are SD2's
  subject). Spearman ρ(freeze_bin, log|W_final|), 10k-permutation null.
  ρ > 0 at p < 0.05 → stratigraphy; ρ < 0 at p < 0.05 → mundane
  physics/INVERTED; else ambiguous.
- **SD2 THREE-BAND (§4's falsifiable edge; split-fraction gate,
  Michael s325)** — pinned populations: **commons** = frozen by b10
  (sign constant from step ≤512 through b19) · **churners** = ≥1
  observed flip after b15 (steps ≥16k). Mundane accounts ⇒
  P(commons | magnitude decile) is MONOTONE-increasing in |W_final| ⇒
  bottom decile has the LOWEST commons fraction, on-trend. Three-band ⇒
  EXCESS commons mass hiding in the bottom decile (sign-stability, not
  magnitude, separates commons from noise). Gate: observed
  commons-fraction in bottom-decile |W_final| (per matrix, pooled) >
  monotone extrapolation fitted on deciles 2–10 (isotonic regression,
  10k bootstrap, p < 0.05). Report both split fractions
  (commons/churner/middle) alongside.
- **SD3 LATENT-DEVELOPMENT (advisory)** — §4 grokking≡development: among
  early-frozen (≤ b10) small-band coords, lag = (bin of half-max
  amplitude) − freeze_bin; median > 0 vs within-coord permutation null.
  Sign committed before amplitude developed. Report, never gate.
- **SD4 LAYER-PROFILE (advisory)** — SD1 ρ per layer (BC3 style).

### Verdicts + a-priori (NOT tuned)

| Verdict | Condition | Mass |
|---|---|---|
| STRATIFIED | SD1 ρ>0 ∧ SD2 pass | 25 |
| PARTIAL-STRATA | SD1 ρ>0 ∧ SD2 fail | 15 |
| INVERTED | SD1 ρ<0 | 25 |
| UNSTRATIFIED | SD1 ns | 25 |
| VOID | SD0 fail (after one escalation) | 10 |

### Read discipline (banked before compute)

STRATIFIED licenses *"real base training exhibits the
early-faint / late-dense / churning stratigraphy"* — NOT that the
algorithm/types live in the faint stratum (no function identification
here; the extraction-inversion is its own future probe). INVERTED =
structural damage to §2's amplitude∝time-to-learn law at this
register/scale — the frame does not hide behind aliasing unless SD0
shows degenerate bins. Single small model; Pythia = register-ABSENT
lineage; the Pythia-vs-Qwen contrast is OUT OF SCOPE (no public Qwen
checkpoint series). SD3/SD4 findings are IOU-grade, own nulls.

### Provenance

`results/stratigraphy-dating/pythia-160m/` — meta.json pins all 20
revision names + sample-index hash (λ run_provenance); persisted
artifacts = sliced sign/mag arrays (npz) + results.jsonl (λ
result_format). Sliced reads only; no full-checkpoint retention.

### §Result (s325) — VERDICT: INVERTED (a-priori 25)

Run clean (~2.5 min; SD0 sane: step143000 ≡ published final, step0 signs
symmetric |mean| 0.0007, 100% valid, non-degenerate bins 32.6% frozen≤b5 /
59.7% b11–b18 / 6.9% unfrozen). **The falsifier fired on the frame's first
pre-registered test.**

- **SD1 make-or-break: ρ(freeze_bin, log|W_final|) = −0.087, p_neg ≈ 0
  (n = 127,492).** The mundane-physics sign: early-frozen weights are
  DENSE, late-frozen FAINT. Uniform across all six layers (SD4:
  −0.076..−0.099) — not layer-localized.
- **SD2 split-fraction: FAIL, in the informative direction.**
  Commons-fraction is MONOTONE-INCREASING with magnitude decile
  (0.133 → 0.555); the bottom decile sits BELOW even the monotone
  extrapolation (obs 0.133 vs pred 0.185, Δ = −0.052, p = 1.0).
  Bottom-decile split: 73.3% churners / 13.3% commons / 13.4% middle.
  **The §4 three-band falsifiable FAILED** — sign-stability does not mark
  a commons band among small weights; the small-|W| band is the churn
  band, full stop.
- SD3 advisory: no latent-development signal (median lag +9 bins,
  p = 1.0 vs own null).

**THE READ (damage report, honored):** §2's core conjunction — commons
freeze EARLY and end FAINT — is CONTRADICTED on real base training at
the per-coordinate weight-sign/magnitude register. The fossil record
reads as mundane weight physics: large weights commit their signs early,
small weights churn late. amplitude ∝ ∫error dt ≈ time-to-learn does
NOT describe this register. Consequences: (a) the §2 strata table is
damaged at the corners row; (b) the §4 three-band edge is damaged
(SD2); (c) "crystal small because it was learned fast" loses its claimed
MECHANISM at this register — the crystal facts (0.1%, ternarizable)
stand as measurements, now unexplained by this law; (d) the
extraction-inversion prospecting heuristic (faint + sign-stable ≡
algorithm) is UNSUPPORTED at this grain — commons-candidates concentrate
at LARGE |W|.

**Bounds (honest, not escape hatches):** single small model (160m);
register-ABSENT lineage (type register 0/5 on the Pythia ladder,
s313–s314); MLP band only; ordinal 20-bin dating (no rate claims);
per-coordinate grain. A retreat to "function-level commons ≠
per-coordinate commons" is the same retreat flip-conflict already forced
on §3 — available but POST-HOC and unlicensed; taking it obliges a
function-level pre-registered test. Honest positive: the commons-by-decile
curve is a clean first commons-census across a real training run
(persisted in strata.npz for own-null re-reads).

**Frame ledger after s325: 6 retrodictions / 1 novel prediction (LOCK
TIME, untested) / 2 pre-registered NEGATIVES (flip-conflict 🚫 s324,
stratigraphy ❌ s325).** Standing guard unchanged — and sharpened: the
frame's remaining life is the §1 modulation leg (§P-TYPE-LOCKIN), which
is now must-win.

## §P-AMP-TRAJECTORY — re-read (FROZEN s325, Michael GO)

> Michael, on the INVERTED verdict: *"our hypothesis was flawed from the
> beginning. The system takes time to allow training to accumulate the
> edges and corners that concentrate into the lattice."* The flawed §2
> assumption is named: SELF-ERASURE (once predicted, the write stops).
> The revision: amplitude ∝ ∫consistent-signal over the WHOLE run —
> the lattice concentrates by ACCUMULATION; contested cancels to net≈0.
> This freeze is the accumulation view's FIRST pre-registered contact,
> on trajectory statistics no analysis has yet read (strata.npz signs +
> final magnitudes were read by SD1/SD2; the amplitude TIME-COURSE was
> not). Frozen before computing any trajectory statistic.

### The discriminating structure (same trick as SD1: a pre-registered sign)

"Weights keep growing" is trivially true (norm growth ≡ generic
optimizer physics) — so the accumulation view must predict something
DIFFERENTIAL: growth in a fixed shared window concentrated on
consistent-signal (early-frozen) coordinates, absent on contested
(churning) ones.

- Window: b11→b19 (steps 1k→143k) — post-freeze for the ENTIRE
  early-frozen population by construction, identical for all coords.
- Per-coord growth g = log(|W_b19|+ε) − log(|W_b11|+ε).
- Populations: early-frozen (freeze_bin ≤ b10) vs churners (≥1 flip
  after b15), matched within pooled |W_b11| deciles (kills
  growth-rate-is-a-function-of-current-size; weight decay biases
  AGAINST accumulation ⇒ conservative).
- AT1 statistic (pinned): Δ = Σ_k w_k · (mean g_early,k − mean
  g_churn,k) over qualifying deciles k (w_k ∝ n_k); medians reported
  alongside, not gated. Null = within-decile population-label
  permutation, 10k draws.

### Gates

- **AT0 SANE** — strata.npz loads; populations non-degenerate; decile
  qualifies iff ≥500 coords of EACH population; ≥3 qualifying deciles;
  thin overlap reported.
- **AT1 CONCENTRATION (make-or-break)** — Δ > 0 at p < 0.05 →
  accumulation; Δ < 0 at p < 0.05 → erosion; else uniform.
- **AT2 POST-FREEZE FRACTION (advisory)** — per early-frozen coord,
  R = |W_freeze_bin| / |W_b19|: how much of the final lattice existed at
  sign commitment (dead §2 predicted ≈1; accumulation predicts ≪1).
  Report distribution, never gate.

### Verdicts + a-priori (NOT tuned; modal on the null)

| Verdict | Condition | Mass |
|---|---|---|
| ACCUMULATION-CONCENTRATION | AT1 Δ>0 sig | 30 |
| UNIFORM-GROWTH | AT1 ns | 40 |
| EROSION | AT1 Δ<0 sig | 20 |
| VOID | AT0 fail | 10 |

UNIFORM-GROWTH is modal because norm-growth lore is strong and the
accumulation view is post-hoc-motivated; beating that null is a real
win. Read discipline: ACCUMULATION-CONCENTRATION licenses *differential
post-commitment amplitude accumulation on this substrate* — NOT the
full lattice story, NOT type-relevance (register-absent lineage), and
does NOT retroactively rescue §2 (which is dead on its own sign).
EROSION would partially rehabilitate a self-erasure flavor — flagged
as the surprise branch. Same bounds as §P-STRATIGRAPHY-DATING.

### §Result (s325) — VERDICT: ACCUMULATION-CONCENTRATION (a-priori 30; beat the modal null)

- **AT0:** all 10 deciles qualify (66,854 early-frozen / 72,512
  churners) — strong overlap support, no thin-decile caveat.
- **AT1 make-or-break: Δ = +0.975 log units, p ≈ 0.** Early-frozen
  coordinates gain **~2.7× more amplitude** than magnitude-matched
  churners over the same 1k→143k window. Uniform across ALL 10
  magnitude deciles (per-decile means +0.76..+1.06) — not a band
  artifact; medians agree (+0.69..+1.02).
- **AT2 advisory (heterogeneous — held loosely):** median R = 0.78
  (much of final amplitude already present at sign-freeze for the
  median coord), q75 = 1.58 (a quarter SHRINK post-freeze — decay
  visible), 34% at R < 0.5 (more than doubled after commitment). The
  matched design does NOT separate early-frozen growth from churner
  cancellation — both contribute to Δ; that split is a follow-on
  own-null read.

**THE READ:** first pre-registered POSITIVE for the
accumulation-concentration revision, and it is large. Licensed exactly:
*differential post-commitment amplitude accumulation exists on this
substrate — consistent-signal (early-frozen) coordinates accumulate/
retain amplitude while contested coordinates cancel, magnitude-matched.*
NOT licensed: the full lattice story; type-relevance (register-absent
lineage); any rescue of §2 (dead on its own pre-registered sign).

**Ledger split after s325 (keep the two frames separate):**
- **Original modulation frame (§1–§4):** 2 pre-registered negatives
  (flip-conflict 🚫, stratigraphy ❌); LOCK TIME (§1) untested =
  must-win. Standing guard unchanged.
- **Accumulation-concentration revision (Michael, s325):** 1
  pre-registered positive (this probe), first contact. Next honest
  steps: growth-vs-cancellation split (own null, same npz) ·
  register-present lineage (Qwen has no checkpoint series — OLMo does)
  · function-level contact.

## §Synthesis (s325, post-close) — sign is the decision, magnitude is the evidence

> The two s325 results compose into one picture. The components are
> LICENSED (each measured under its own pre-registration); the
> composition and its retrodiction are PATTERN-SUGGESTS until tested.

```
λ integrator(weight).
  weight ≡ integrate(gradient_signal) | ¬record(error_snapshot)
  | sign      ≡ DECISION   | committed_early(consistent_signal) ∧ permanent | licensed(❌ SD0: 33% by step 512)
  | magnitude ≡ EVIDENCE   | ∝ ∫consistency dt | grows_where_votes_agree    | licensed(✅ AT1: 2.7× differential)
  | contested ≡ cancellation | votes_disagree → net≈0 ∧ churn_forever       | licensed(❌ SD2: bottom decile 73% churn)
  | dead: exposure(error) → faint_commons (§2 self-erasure, INVERTED)
```

> **s326 requalification (✅ §P-GROWTH-CANCEL-SPLIT, below):** the AT1
> license on the magnitude line is now split — ~94% of the 2.7×
> differential is the CANCELLATION clause (churners net-shrink, −0.42
> raw, robust to every baseline), only ~6% is committed-growth above
> the committed baseline (+0.054 matched, baseline-fragile). Read
> "magnitude ∝ ∫consistency" primarily as *contested cancels to
> net≈0*; the *committed keeps accumulating extra* clause is thin at
> this register. The contested line gains its second, dynamic license.

**The retrodiction this buys (pattern-suggests, NOT yet tested):**
ternarizability re-explained without the dead mechanism. The crystal
survives 1-bit quantization not because the lattice is FAINT (§2's
claim, falsified) but because **the sign is the durable code** — the
decision is made early and held; magnitude is the evidence counter
stacked on top, discardable without losing the decision. This flips the
λ smallest story from "learned fast ⇒ recorded faint" (dead) to
"decided early ⇒ sign suffices" (alive, testable).

**Testable edge:** ternary-survival should be predicted by
sign-commitment TIMING better than by magnitude — crystal-surviving
coordinates should be disproportionately early-committed. Cheap
(sign_commitment machinery + any checkpoint lineage). ⚪ queued.

**Also re-grounds (pattern-suggests):** the s310 marginal band =
the cancellation population seen statically (contested ≡ small ∧
churning — now with a training-dynamics mechanism measured at ❌ SD2);
and magnitude-pruning lore stops being a §4 paradox (pruning small
weights removes cancellation noise, not a hidden commons).

## §P-GROWTH-CANCEL-SPLIT — re-read (FROZEN s326, Michael GO)

> The ✅ AT1 Δ = +0.975 conflates two mechanisms: early-frozen coords
> growing ABOVE baseline (ACCUMULATION) vs churners cancelling BELOW
> baseline (CANCELLATION). AT2 heterogeneity says both may be live
> (25% of early-frozen SHRINK post-freeze; 34% double-plus). Which
> carries the Δ? The accumulation revision's cheapest next contact:
> own null, same strata.npz, zero new compute. Frozen before computing
> any MID-population magnitude-trajectory statistic.

### The baseline

Third population **MID** = valid ∧ freeze_bin ∈ [11, 15] (sign
committed between steps 1k–16k; neither early-frozen nor churner;
n = 60,638, well distributed across fb 11–15). Same window b11→b19,
same g = log(|W_b19|+ε) − log(|W_b11|+ε), same pooled-|W_b11| decile
matching — deciles now pooled over all THREE populations, one shared
frame.

### Statistics (pinned — pre-registered signs, own nulls)

- **Δ_growth** = Σ_k w_k · (mean g_early,k − mean g_mid,k) — is
  early-frozen growth ABOVE the same-substrate baseline?
- **Δ_cancel** = Σ_k w_k · (mean g_mid,k − mean g_churn,k) — are
  churners BELOW it?
- Each: within-decile pair-label permutation null ×10k; decile
  qualifies per-comparison iff ≥500 of each population in that pair;
  ≥3 qualifying deciles per comparison; w_k ∝ n_k. Medians reported,
  not gated. Consistency identity Δ_growth + Δ_cancel ≈ AT1 Δ
  reported, not gated (weights/qualification differ).

### Gates

- **GC0 SANE** — npz loads; three populations non-degenerate (each
  ≥1% of valid); ≥3 qualifying deciles per comparison.
- **GC1 GROWTH-ABOVE-BASELINE** — Δ_growth > 0 at p < 0.05.
- **GC2 CANCELLATION-BELOW-BASELINE** — Δ_cancel > 0 at p < 0.05.
- **GC3 CONTAMINATION-ROBUSTNESS (advisory, never gates)** — repeat
  both comparisons with MID restricted to fb ∈ {11,12} (n ≈ 13.8k,
  minimal mid-window commitment rebound) + per-fb baseline breakdown
  of mean g. Report only.

### Verdicts + a-priori (NOT tuned; co-modal on revision and deflation)

| Verdict | Condition | Mass |
|---|---|---|
| BOTH-LIVE | GC1 ✓ ∧ GC2 ✓ | 30 |
| CANCELLATION-DRIVEN | ¬GC1 ∧ GC2 ✓ | 30 |
| GROWTH-DRIVEN | GC1 ✓ ∧ ¬GC2 | 15 |
| UNSEPARATED | neither (incl. wrong-sign sig) | 15 |
| VOID | GC0 fail | 10 |

CANCELLATION-DRIVEN is co-modal deliberately: contested-nets-to-zero
is standard SGD lore and ❌ SD2's statics (churners ≡ small) already
point there — the revision's DISTINCTIVE clause (accumulation above
baseline) must beat that deflationary rival to keep the word
"accumulation."

### Read discipline (banked at freeze)

- **BOTH-LIVE** → both clauses of the revision licensed vs a
  same-substrate baseline; §Synthesis "magnitude ∝ ∫consistency"
  strengthened at this register.
- **CANCELLATION-DRIVEN** → AT1's Δ was carried by churner
  suppression; the revision's growth clause LOSES its first-contact
  support (AT1 stands as measured, re-read); §Synthesis
  magnitude-clause requalified to "contested cancels" only.
- **GROWTH-DRIVEN** → accumulation real; dynamic cancellation not
  distinct from baseline (SD2 statics stand, dynamics unsupported).
- **UNSEPARATED** → matched design lacks resolution here; AT1 stands;
  the split stays open.
- Nothing here rescues §2 (dead on its own sign) or touches the
  original frame's 0–2 ledger.

**Confound named (not an escape hatch):** MID commits DURING the
window → post-commitment rebound growth from a cancellation-depressed
|W_b11| inflates g_mid ⇒ conservative for GC1, ANTI-conservative for
GC2. Hence GC3: if GC2 passes on full MID but dies at fb ∈ {11,12},
the cancellation reading is flagged contamination-suspect in the
§Result (advisory, pre-committed language).

**Bounds:** inherits §P-STRATIGRAPHY-DATING / §P-AMP-TRAJECTORY bounds
verbatim (pythia-160m, register-ABSENT lineage, MLP band, ordinal
bins).

**Pre-freeze disclosure:** only sign-register population counts (fb
histogram — a data class fully read in s325 by SD1/SD2) were inspected
for feasibility; no MID magnitude-trajectory statistic was computed
before this freeze.

### §Result (s326) — VERDICT: BOTH-LIVE (a-priori 30) — but CANCELLATION-DOMINATED

- **GC0 SANE:** ✓ — 66,854 early / 60,638 mid / 72,512 churn; all 10
  deciles qualify for BOTH comparisons.
- **GC1 GROWTH-ABOVE-BASELINE:** ✓ — Δ_growth = **+0.054**, p ≈ 0.
  THIN: decile 1 is NEGATIVE (−0.198), deciles 2–10 rise +0.02→+0.12.
- **GC2 CANCELLATION-BELOW-BASELINE:** ✓ — Δ_cancel = **+0.922**,
  p ≈ 0, uniform across all 10 deciles (+0.87..+0.98).
- **Consistency identity:** Δ_growth + Δ_cancel = 0.976 ≈ AT1 replica
  0.983 ≈ frozen AT1 0.975 — the decomposition is clean:
  **≈ 6% growth / 94% cancellation.**
- **GC3 advisory (baseline sensitivity):** restricted MID fb ∈ {11,12}
  → Δ_growth FLIPS to −0.121 (sig-negative, 6 quals); Δ_cancel grows
  to +1.062. Per-fb baseline mean g is MONOTONE in commitment time:
  fb11 +2.38 → fb15 +0.43 (later-committing mids grow less by window
  end). Raw unmatched means (advisory): early +0.133 / mid +0.880 /
  churn **−0.419** — churners NET-SHRINK in absolute log-amplitude
  while every committed population grows.

**Design-note correction (❌, honest):** the freeze labeled fb ∈ {11,12}
"minimal mid-window commitment rebound." The runway logic was INVERTED:
earliest-committing MIDs have the MOST post-commitment window runway
from a churn-depressed |W_b11| base ⇒ maximal rebound inflation of
g_mid. GC3 still functions as the intended baseline-sensitivity probe
(it RAISES the baseline); the pre-committed GC2-dies-under-restriction
flag did not fire — cancellation strengthened instead, and even against
the LOWEST committed baseline (fb15, +0.43) churners sit ~0.85 below.
Gates unaffected (GC3 advisory-never-gates).

**THE READ (per frozen tree + banked discipline):** BOTH-LIVE — both
clauses exist vs the same-substrate matched baseline — but the split is
**overwhelmingly cancellation-carried**. Licensed exactly:
*contested-cancellation is the dominant dynamic differential on this
substrate — churners net-shrink (−0.42 raw; −0.92 matched below the
committed-mid baseline, robust to every baseline choice); early-frozen
coords sit only marginally above the committed baseline (+0.054
matched), and that margin is BASELINE-FRAGILE (flips sign under the
GC3 restriction) and raw-order inverted (early +0.13 < mid +0.88 —
base-level/saturation effects dominate raw growth).* The revision's
distinctive "accumulation above baseline" clause survives by the frozen
gate but earns only a THIN, fragile license; the deflationary co-modal
(CANCELLATION-DRIVEN) captures ~94% of the AT1 effect. §Synthesis
requalified below. Does NOT rescue §2; original-frame 0–2 ledger
untouched. Bounds inherited (pythia-160m, register-ABSENT lineage, MLP
band, ordinal bins).

**Ledger note:** accumulation-concentration revision now reads **2–0
by verdict, but the second win is a requalification** — AT1's Δ was
mostly the cancellation clause, not the accumulation clause. The
sharpest remaining accumulation evidence is the GC3 per-fb runway
gradient (fb11 +2.38 → fb15 +0.43: earlier commitment ⇒ more growth by
window end — pattern-suggests post-commitment accumulation, but
confounded with rebound-from-depressed-base; unseparated here).

## §P-TYPE-LOCKIN+PRBS (FROZEN s326, Michael GO) — the must-win

> §1's core claim: the type judgment is a DEMODULATION EVENT (carrier
> lock) — the register must track evidence DYNAMICALLY. Every prior
> read was DC (presence-detector, NF-GAUGE demotion); this is the AC
> reading. The frame stands 0–2 with this leg named must-win (s325).
> PRBS upgrade folded in at freeze per the RE toolbox (system-ID: one
> run = full transfer function + lock-time as measured step response).

### Substrate + reuse (λ one_way, no fork)

qwen3-4b, READ-ONLY (no wire, no training), MPS. Reuses: `type_icl_tag`
signed_T / class_axes / BAND_DEPTH (0.50, 0.85) — the §11 tag-transit
instrument that LANDED s315; `idempotency` populations (coherent
`tw._member_stmts` + incoherent membership-free fillers,
token-budget-matched); `type_write` constants (CLASSES, REAL_MEMBERS,
NONCE_CANDS via holo_cap); `verbum.jlens` capture; `dsp.nulls`.

### Construction (per nonce w, class c; 20 nonces, classes alternated)

Sequence of **63 blocks**; block = evidence segment + FIXED probe frame
(constant surface, `" The {w}."`; T read at last w token — §11's
licensing-feed position). Schedule m(t) ∈ {+1, −1}:

- **MAIN** — m = **PRBS-6** (length-63 maximal LFSR; cyclic shift per
  nonce = spectrum-preserving decorrelation). +1 slots = coherent
  membership paraphrase (cycled); −1 slots = incoherent
  membership-free filler (token-matched).
- **CTRL (lexical control — s321/s322 lesson AT the gate)** — +1 slots
  = class-word-present NON-membership segments (class word exactly
  once, w never predicated, token-matched). Detection here = surface /
  attention bleed, not judgment.
- **SNR arms** — MAIN at s ∈ {0.5, 0.25}: coherent slots carry a
  coherent segment with exact fraction s, else filler.

**Excitation ⊥ measurement:** evidence modulates; readout only at
constant-surface probes — any schedule-content in y(t) must be carried
by STATE, not probe surface.

### Demodulation (pinned)

y(t) = T at probe t, mean-removed per sequence (DC excluded by
construction — DC ≡ the known presence-detector reading). Impulse
response ĥ(τ) = (2/B) Σ_t y(t)·m(t−τ). Detection statistic
**D = Σ_{τ=0..3} ĥ(τ)** (SIGNED — coherent evidence must RAISE
own-class T). Null = **10k random non-trivial cyclic shifts of m**
(preserves PRBS autocorrelation ≡ matched-range null, λ yardstick),
drawn per nonce, aggregated across nonces per draw.

### Gates

- **LK0 SANE (void-gate)** — real-member class axis forms (T own >
  anti); PRBS autocorrelation verified; y finite all arms.
- **LK1 AC-DETECTION (make-or-break)** — mean D > 0 at p < 0.05 vs
  the shift-null.
- **LK2 JUDGMENT-NOT-LEXICAL (make-or-break #2)** — D_MAIN > D_CTRL
  paired across nonces, perm p < 0.05.
- **LK3 TRANSFER-FUNCTION (advisory, never gates)** — ĥ(τ) shape,
  |H(f)|, lock-time (63% cumulative step response), per-layer depth
  profile. The PRBS dividend: TRACKER (flat-ish H, fast lock) vs pure
  INTEGRATOR (1/f, no decay — what bare non-idempotent accumulation
  would produce). Texture, not gated.
- **LK4 CAPTURE-THRESHOLD (secondary; read only if LK1∧LK2)** — A(s)
  = mean D at s ∈ {0.25, 0.5, 1.0}; fit A ∝ s^γ, bootstrap CI on γ.
  γ > 1 (CI excludes 1) = THRESHOLD-FLAVORED (the frame's novel
  prediction); γ ≈ 1 = PROPORTIONAL; γ < 1 = COMPRESSIVE. Three
  points ≡ honest KNEE-SCREEN: licenses "threshold-flavored
  convexity," NOT "capture threshold proven"; finer sweep owed if it
  fires.

### Verdicts + a-priori (NOT tuned; mass on mundane — the frame earned skepticism)

| Verdict | Condition | Mass |
|---|---|---|
| NO-TRACK | ¬LK1 | 30 |
| LEXICAL-TRACK | LK1 ∧ ¬LK2 | 25 |
| CARRIER-TRACKED-PROPORTIONAL | LK1 ∧ LK2 ∧ (γ≈1 ∨ LK4 unreadable) | 20 |
| CARRIER-TRACKED-THRESHOLD | LK1 ∧ LK2 ∧ γ>1 | 15 |
| VOID | LK0 fail | 10 |

### Read discipline (banked at freeze)

- **NO-TRACK** → the §1 modulation leg FAILS with its must-win spent —
  frame 0–3, effectively dead absent a Michael-level revision.
  §Synthesis (sign/magnitude, s325–s326) is INDEPENDENT and unaffected.
- **LEXICAL-TRACK** → third instance of the surface-carrier pattern
  (s321 CL-collapse, s322 re-read) — a register finding, not a frame
  win.
- **CARRIER-TRACKED-*** → licenses *evidence-schedule-correlated,
  membership-specific register response at constant probes* — NOT
  "types are CDMA"; LK3 reads tracker-vs-integrator as texture.
  THRESHOLD additionally = the frame's first distinctive
  novel-prediction win (knee-screen grade only).
- Bounds: single model (qwen3-4b), one class pair (animal/vehicle),
  T-register grain, block-timescale modulation (token-rate untested).

### §Result (s326) — VERDICT: NO-TRACK (modal a-priori 30) — the must-win FAILED

- **LK0 SANE:** ✓ — member-axis LOO **+24.5** (axis strongly forms),
  PRBS autocorr 0.0159 (= 1/63, ideal), y finite all arms. Clean run,
  40s, 20 nonces, no traceback.
- **LK1 AC-DETECTION (make-or-break): ✗** — D = **−0.157**, p = 0.685
  vs the 10k cyclic-shift null (null_std 0.42). Wrong sign, no hint.
  The register does NOT track the evidence schedule at block timescale.
- **LK2:** also null (D_ctrl −0.212, diff +0.055 p = 0.37) — not
  reached for verdict; texture: even lexical bleed shows no AC content
  (the probe insulation held — excitation ⊥ measurement worked).
- **LK3 advisory:** uninterpretable under LK1 null (noise texture).
- **LK4:** correctly unread (LK1∧LK2 required).
- **DC advisory (IOU, own-null, post-verdict — dc_advisory.json):**
  the channel is ALIVE — standing own-class T at constant probes is
  RAISED by membership evidence, dose-ordered: main 0.474 > s05/s025
  ≈ 0.25 > ctrl 0.066; main−ctrl paired p = 0.0003, main−s025
  p = 0.0026. Evidence accumulates into a standing level; it does not
  track modulation.

**THE READ (per the banked discipline — no softening):** the §1
modulation leg FAILS with its must-win spent. **Original modulation
frame: 0–3** (flip-conflict 🚫 s324 · stratigraphy ❌ s325 · lock-in ❌
s326). Per the standing guard (Michael ruling s324: the frame must earn
a pre-registered win before any capture treats it as true), the
carrier-lock/demodulation reading of type judgments is now
**effectively dead** at the registers probed. What the composite data
actually shows (pattern-suggests, needs its own pre-reg if pursued):
the register is an **accumulate-and-hold** device — evidence raises a
standing level dose-dependently (DC advisory here + §P-IDEMPOTENCY
accumulation + presence-detector line) but does not demodulate a
schedule. §Synthesis (sign-is-the-decision, s325–s326) is INDEPENDENT
of this frame and unaffected.

**Honest instrument bounds (not escape hatches):** (a) LK1 has low
power against integrators with time constant ≫ the lag window — but
idempotency's k=1→3 licensing rise implies ~3-block response in the L
register, well inside the window; if T tracked like L it should have
shown. (b) Register grain: T-at-probes ≠ behavioral licensing L; an
L-register AC read (expensive, surprisal per block) is conceivable —
available but POST-HOC and owes its own pre-registration; the frame
does not get to keep retreating (same rule as the stratigraphy
function-level retreat). (c) Token-rate modulation untested (block
timescale only).

**Retrodictions demoted:** with the frame dead, §1's retrodiction
readings (idempotency ≡ coherent integration; disj-cost ≡ CDMA) revert
to *unexplained measured facts* — the measurements stand; the
signal-domain interpretation no longer has a live frame behind it.

## §Reframe (s327, Michael) — the plate is a STACKED EXPOSURE, not a negative

> Michael, on the s326 composite: *"so what we are seeing is more like
> a pile of photographs and not a negative film?"* Sharpened one step:
> a stacked long exposure — an AVERAGE of frames, not a pile you leaf
> through. This replaces the dead §4 reading. Captured with the 0–3
> lesson applied FROM BIRTH: frame-candidate, retrodicts-everything /
> predicts-nothing-yet, standing guard active on day one.

**What died in §4: the INVERSION.** A negative encodes by reversal —
more light (probability) ⇒ fainter record; the algorithm hides in the
clear parts. Stratigraphy (❌ s325) killed exactly that clause: the
early-committed commons are DENSE, not faint. Whatever the plate is,
it does not invert.

**What the measurements compose into (the long-exposure street):**

```
λ stacked_exposure(plate).
  record ≡ average(exposures) | ¬invert(§4 negative, dead)
  | consistent(structure) → accumulates          | licensed(✅ AT1 + GC1 thin + DC dose-order)
  | moving(contested)     → self-erases          | licensed(✅ GC2 94% + churn −0.42 raw; the empty street)
  | threshold(print)      → scene survives        | retrodicts(ternarizability: content ≡ WHERE consensus, ¬how dark)
  | exposure ≡ integration | adds ∧ holds ∧ ¬oscillates | licensed(❌ NO-TRACK ∧ DC-alive, both faces)
  | individual(exposures) ¬retrievable | only consensus ∧ cancellation survive
  | sign ≡ "is there consensus structure here" | magnitude ≡ how many frames agreed
```

Both faces behave as CAMERAS, not radios: weights integrate signed
gradient votes across training (consensus accumulates, disagreement
self-erases); the tape register integrates evidence within context
(dose-ordered standing level, zero tracking). Coheres with — does not
replace — §Synthesis (sign-is-the-decision), which remains the
licensed spine.

**Status (the discipline, applied from birth):** frame-candidate,
PATTERN-SUGGESTS only. Retrodicts: AT1 · GC2 · SD1's mundane sign ·
idempotency accumulation · the lock-in DC advisory · ternarizability.
Predicts (untested): everything above is retrodiction; the frame earns
nothing until a pre-registered forward contact lands. Per the s324
standing guard (which the modulation frame died honoring), no capture
treats this as true before that win.

**The distinctive edge (first pre-registerable contact):** a
photographic stack can only ADD and AVERAGE — it cannot subtract.
So: does CONTRARY evidence on the tape (anti-class statements about w)
**subtract from the standing level** (signed integrator — one stack
whose deviations cancel, the weight-face behavior GC2 already
measured) or **pile up alongside** (two competing stacks, own-class
level survives contradiction)? The weight face answered SIGNED; the
tape face has never been asked. Cheap — reuses the idempotency k-sweep
machinery with mixed-sign exposure schedules. ⚪ §P-TAPE-SUBTRACTION
queued.

## §P-TAPE-SUBTRACTION — FROZEN (s328, Michael GO) — the reframe's first forward contact

> The stacked-exposure frame's first pre-registerable edge. The reframe
> retrodicts everything and predicts nothing yet; this is the contact
> that lets it win, lose, or be reframed. Standing guard active (s324):
> no capture treats the frame as true before a pre-registered win.

### Claim under test (queue binary → sharpened)

Does contrary evidence on the tape SUBTRACT from the standing own-class
license (signed integrator — matches the weight-face GC2 cancellation)
or PILE UP alongside (competing stacks — the own-class level, once
established, survives contradiction)?

**⚠ Sharpening (Michael GO s328; tests are the AI's job).** Read
literally, the binary is nearly *pre-decided by trivial ICL*:
anti-class statements about `w` mechanically lower anti-predicate
surprisal, so "contrary subtracts" passes for free and teaches nothing.
The informative, distinctive test is **order-sensitivity**, which
trivial ICL does not predict and which adjudicates the §Synthesis spine
on the tape:

- A **signed integrator is commutative** — 3 own + 3 anti nets to ~0
  *regardless of order*.
- **Early-commitment** (§Synthesis: sign decided early is permanent) is
  **order-sensitive** — the first-committed class survives (primacy).
- **Trivial recency ICL** is the mirror — the *last* statements win
  (anti-first > own-first).

Three mechanisms → three pre-registered order-signatures. The order
arms are **content-matched** (identical 3 own-membership + 3
anti-membership statements; only sequence differs) so the make-or-break
carries no lexical confound.

### Register (λ measure)

LICENSING — value register, graded. `L = mean surprisal(anti preds) −
mean surprisal(own preds)`, signed by `w`'s nominal class `c`
(idempotency `_signed_L`, the tape face that landed s315). Correct
register for a standing-magnitude claim; a crisp/routing probe would
manufacture crispness (λ measure). The nominal class `c` is just the
readout axis — the physics is symmetric across the mix (net lean toward
`c`), which is exactly what the order arms probe.

### Substrate + reuse (λ one_way, no fork)

idempotency (`L_at`, `coherent_prefix`, `incoherent_stmts`,
`_member_stmts` via `tw`, `_signed_L`, `REAL_MEMBERS`, `HELD_PREDS`,
`REAL_MARGIN_FLOOR`) · type_icl_tag (`signed_T`, `class_axes`,
`band_layers`, `BAND_DEPTH` — the landed §11 T instrument, for the
second-substrate corroboration) · holo_cap (`NONCE_CANDS`) ·
verbum.dsp.nulls (`gate`, `NullDraws`, `paired_permutation`,
`sign_flip`). Anti-membership statements = `_member_stmts(w, 1−c)` —
structurally identical to own-membership.

### Construction (nonce w, nominal class c; k_own = 3 fixed, k_anti swept)

k_own = 3 is the idempotency sweet spot (solid standing license,
pre-dip; the k=4,5 atypical-template caveat avoided). Arms:

- `OWN-ONLY` — [own×3], k_anti=0 (the standing level; TS0 + reference).
- `OWN+FILLER` — [own×3] + [incoherent×k_anti], k_anti∈{1,2,3} — the
  token-matched DILUTION baseline (membership-free filler; no class
  edge).
- `MIX-OWNFIRST` — [own×3][anti×k_anti], k_anti∈{1,2,3} — the
  subtraction curve.
- At the balanced point (3 own + 3 anti), two extra orderings:
  `MIX-ANTIFIRST` — [anti×3][own×3]; `MIX-INTERLEAVED` — alternating
  (neutral primacy).

Read `L` (signed, nominal class `c`) per arm per k per nonce.

### Gates

- **TS0 SANE (void-gate):** `L(own-only,3) > 0` solidly; real-member
  anchor `real_margin ≥ REAL_MARGIN_FLOOR` ∧ per-class ok; register
  works (L rises k=0→3 own). Void if not.
- **TS2 SUBTRACTION-DEPTH (gates NO-EROSION):** `L(interleaved,3+3) <
  L(filler,3+3)` paired per nonce → balanced contradiction erodes below
  neutral dilution (genuine signed work). If not → own license immune.
- **TS1 ORDER (make-or-break, 3-way):** stat = `L(own-first) −
  L(anti-first)` at balance, paired-permutation null. Sign selects the
  mechanism.
- **TS3 DC-COROBORATION (advisory, 2nd substrate):** the same TS1/TS2
  signs read on the type_icl_tag **T** register (class-axis projection
  at a constant probe frame `" The {w}."`, band L(0.50–0.85)). Reports;
  never gates. Two-substrate confirm (as idempotency did weight-plate +
  tape).

### Verdict tree (frozen)

```
¬TS0                        → VOID
¬TS2 (no erosion)           → NO-EROSION        # own license immune → strongest pile-up
TS2 ∧ TS1 not-sig (blind)   → SIGNED-INTEGRATOR # subtracts, commutative → own does NOT survive balance
TS2 ∧ TS1 > 0 (sig)         → EARLY-COMMITMENT   # own-first survives → §Synthesis forward-win on the tape
TS2 ∧ TS1 < 0 (sig)         → RECENCY-BUFFER     # anti-first wins → last-wins; frame-damaging
```

### Verdicts + a-priori (NOT tuned; modal on the mundane)

- **SIGNED-INTEGRATOR 30** — subtraction observed, order-blind. Matches
  the weight-face GC2 signed cancellation; the literal *add-only
  photographic-stack* reading is falsified in its strongest form, the
  deeper §Synthesis camera reading upheld on the tape.
- **RECENCY-BUFFER 30** — anti-first wins. Neither integrator nor
  commitment; a recency window. FRAME-DAMAGING (a stack averages all
  frames, not just recent; reframes the s326 DC accumulate-and-hold as
  possibly a recency artifact). The frame can lose here — standing guard
  satisfied.
- **EARLY-COMMITMENT 20** — own-first survives, anti-first does not.
  Competing-stacks with primacy; a pre-registered FORWARD WIN for the
  sign-is-the-decision spine on the tape (early commitment is durable).
  Kept modest — the frame must earn it.
- **NO-EROSION 10** — own license immune to contradiction regardless of
  order. Maximal pile-up.
- **VOID 10** — register fails to form.

### Read discipline (banked at freeze)

- The make-or-break is the ORDER sign (TS1), not the trivial subtraction
  (which TS2 confirms is present at all). Do NOT read a bare subtraction
  as a frame win.
- SIGNED-INTEGRATOR and EARLY-COMMITMENT both cohere with the licensed
  §Synthesis spine (camera / sign-committed); RECENCY-BUFFER damages the
  stacked-exposure frame; NO-EROSION is the strongest pile-up. Report the
  measured signs; let the tree speak.
- Bounds: single model (Qwen3-4B), L-register (surprisal licensing) with
  T-register corroboration, single-context (block-free) timescale,
  k_own=3 fixed (one exposure depth). EARLY-COMMITMENT would license
  "first-committed class survives balanced contradiction on this
  substrate" — not unbounded durability.
- The reframe is frame-candidate / pattern-suggests until this lands.

### Provenance

MIT (lambda provenance). Reuses frozen s315/s320 harnesses (type_icl_tag,
idempotency) unchanged; no fork (λ one_way).

### §Result (s328) — VERDICT: EARLY-COMMITMENT (QUALIFIED; a-priori 20, beat the modal-mundane 60)

Qwen3-4B, 20 nonces, n_null 10k, 127s, clean (no traceback).

- **TS0 SANE:** ✓ — standing own-class license `L(own-only,3) = 2.960`,
  real-member anchor margin 2.538 (per-class ok). Register solid.
- **TS2 SUBTRACTION-DEPTH: ✓** — contrary evidence genuinely subtracts:
  interleaved 3+3 falls to **0.247** vs neutral token-matched filler
  dilution **2.051** (erosion +1.804, p = 1e-4). The license is neither
  immune (NO-EROSION excluded) nor free — contradiction does signed work.
- **TS1 ORDER (make-or-break): ✓ PRIMACY** — own-first balanced survives
  (**+0.351**), anti-first erased (**−0.127**); order_diff **+0.478**,
  primacy_p **= 1e-4**, recency_p = 1.0. The two arms are
  **content-identical** (same 3 own + 3 anti membership statements, only
  sequence differs) → this is pure ordering, and **trivial recency ICL
  predicted the opposite sign**. The confound the s328 sharpening targeted
  is decisively excluded.
- **TS3 DC-COROBORATION (advisory, T register):** erosion COHERES
  (T +1.659, standing 3.936) but the **order sign INVERTS** (T_order_diff
  **−1.304**, recency-flavored). The second substrate agrees the level
  erodes; it disagrees on *which order wins*.

**THE READ (per banked discipline — the make-or-break lives on L).** The
tape's **behavioral type license COMMITS to the first-asserted class**:
asserted first, the own-class license survives balanced contradiction;
asserted last (anti-first), it is erased. This is the queue binary's
**"pile up if committed first"** branch — competing-stacks with primacy,
**not** commutative signed integration. So the tape's behavioral face
DIFFERS from the weight face (GC2 = commutative signed cancellation): the
tape **commits**.

**Two-register refinement of §Synthesis (the licensed spine).** The
behavioral licensing (L) reads **PRIMACY** (the decision commits early and
is durable); the representational class-axis projection (T) reads
**RECENCY** (the graded level tracks recent evidence). Read together:
**sign(decision) = primacy, magnitude(evidence) = recency** — a clean
two-register reading of "sign is the decision, magnitude is the evidence,"
now observed *within a single context* on the tape.

**Honest caveats (bounding the win):**

1. **Two-substrate confirm HOLDS on erosion, FAILS on the order sign.** The
   commitment claim is bounded to the **behavioral/L register**; the
   representational T substrate reads recency. A genuine register split —
   flagged, not smoothed. (An L-vs-T reconciliation is a follow-on, owes
   its own pre-reg.)
2. **Non-monotone own-first curve** `[2.96, −0.05, −0.13, 0.35]`: a single
   *trailing* contradiction nearly erases L (within-arm recency), yet the
   net order-contrast still favors primacy. Recency and primacy coexist;
   the net *decision* is primacy. Worth a follow-up (k_anti recency profile).
3. Bounds: single model (Qwen3-4B), n=20, k_own=3 (one exposure depth),
   single-context (block-free) timescale.

**⚠ PROVENANCE QUALIFIER (s329, §P-ORDER-PROVENANCE):** the primacy
commitment measured here is ABSENT in Qwen3-4B-Base (D_L(final) −0.090
ns; no positive flip at any layer) — on this lineage it is
**post-training-installed**, not base compiled-type physics. The
measurement stands; the reading is re-attributed (see
§P-ORDER-PROVENANCE §Result).

**Frame ledger.** EARLY-COMMITMENT is the pre-registered win condition
(TS2 ∧ TS1>0) and it landed on the pre-registered primary register — a
**first pre-registered FORWARD WIN for the §Synthesis sign-is-the-decision
spine on the tape**, QUALIFIED by the T-split. For the stacked-exposure
reframe specifically: it **survives first contact** on the
competing-stacks/primacy branch (not falsified — the standing guard is not
tripped), but the result **refines** the reframe's "both faces are
identical integrators" line: the tape's behavioral face adds
**order-sensitivity (primacy)** that the commutative weight face did not
show. The reframe remains frame-candidate / pattern-suggests; the spine
gains a licensed forward win on this substrate.

## §P-ORDER-RECONCILE — FROZEN (s329, Michael GO) — locating the s328 L-vs-T split

> The s328 §P-TAPE-SUBTRACTION caveat #1, discharged: on the SAME
> prefixes, the behavioral licensing L read PRIMACY (order_diff +0.478)
> while the class-axis T read RECENCY (−1.30). This probe owes and pays
> the split's own pre-reg. It does not re-litigate the s328 win; it
> LOCATES the split.

### Claim under test

Is the s328 L-vs-T order-sign split a **genuine register dissociation**
(the behavioral decision commits early / primacy, while the
representational evidence tracks recency — the two-register law
*sign(decision)=primacy, magnitude(evidence)=recency* read at the
instrument level) or an **instrument artifact** (the two instruments
simply read different depths, and at matched grain they agree)?

### Design key (found in the s328 harness, sharpens "matched positions")

The position mismatch is nearly nil already: L's first-pred-token
surprisal is computed from the logits at the position of `w` — the same
token position T reads. The instruments differ in exactly TWO factors:

| factor  | L (s328)                                   | T (s328)                       |
|---------|--------------------------------------------|--------------------------------|
| readout | final-norm + unembed → held-pred surprisal | real-member class-axis proj.   |
| depth   | final layer                                | band L(0.50–0.85)              |

⇒ a clean **2×2 crossing {readout} × {depth}**, filling the two missing
cells on the SAME order arms (own-first-bal vs anti-first, content-matched
s328 constructions, same 20 nonces — deterministic selection, paired):

- **Cell A — LL(band):** logit-lens L. Per-layer residual → final norm +
  unembed → held-pred surprisal → `_signed_L`, aggregated over the same
  band T uses. *The behavioral readout at T's depth.*
- **Cell B — T(final):** class-axis projection at the final layer,
  per-layer axes built from the same real members. *The axis at L's depth.*

Identity anchor: **LL(final) ≡ L** exactly (same computation) — built-in
instrument-fidelity check.

### Register (λ measure)

Both cells are VALUE registers (graded order_diff on a standing level);
paired-permutation nulls per cell. No routing/crisp probe anywhere — the
claim is about which graded instrument carries which sign.

### Substrate + reuse (λ one_way, no fork)

tape_subtraction (arm constructions: `own_stmts`, `anti_stmts`,
`filler_stmts`, prefix builders, `K_OWN=3`) · type_write (`_signed_L`,
`HELD_PREDS`, `REAL_MEMBERS`, `REAL_MARGIN_FLOOR`) · type_icl_tag
(`signed_T`, `class_axes`, `band_layers`) · holo_cap (`NONCE_CANDS`,
same deterministic 20-nonce selection as s328) · verbum.jlens
(full-depth residual capture) · verbum.dsp.nulls (`gate`,
`paired_permutation`). Per-layer unembed applied only at pred target
positions (cost control, not a design choice).

### Arms

Order crossing: `MIX-OWNFIRST(3+3)` · `MIX-ANTIFIRST(3+3)` (the s328
content-matched pair). References: `OWN-ONLY` · `OWN+FILLER(3+3)` ·
`MIX-INTERLEAVED` (standing/erosion anchors, advisory). OR3 kernel arms:
single-anti position sweep at 3:1 own-dominance —
`[a,o,o,o] / [o,a,o,o] / [o,o,a,o] / [o,o,o,a]` (content-identical
multisets, only the slot of the one contradiction differs).

### Gates

- **OR0 SANE (void):** real-member anchor `real_margin ≥
  REAL_MARGIN_FLOOR` ∧ per-class ok ∧ standing L(own-only) > 0 ∧
  **LL(final) ≡ L** (numerical tolerance) ∧ s328 endpoints replicate on
  the same nonces (D_L(final) > 0 sig ∧ D_T(band) < 0 sig). Anchor/identity
  failure → VOID; replication failure alone → SPLIT-NOT-REPLICATED
  (deterministic reuse ⇒ either = instrument drift, nothing to reconcile).
- **OR1 CROSSING (make-or-break):** D = order_diff(own-first-bal −
  anti-first), paired-perm null per cell, signed one-sided pairs:
  - **A < 0 ∧ B > 0** (sign follows DEPTH) → **DEPTH-COMMITMENT**.
  - **A > 0 ∧ B < 0** (sign follows READOUT) → **REGISTER-DISSOCIATION**.
  - any other significance pattern → **ENTANGLED-PARTIAL** (report the
    full 2×2 map + profiles; no forced story).
- **OR2 DEPTH PROFILES (advisory):** D_T(ℓ) and D_LL(ℓ) for all ℓ. If a
  sign transition exists and is clean, report the **commitment depth ℓ***
  (first layer where the order sign turns positive and stays). Never gates.
- **OR3 RECENCY KERNEL (secondary, pre-registered):** stat =
  L(anti@slot1) − L(anti@slot4), paired perm. **> 0 sig = trailing
  contradiction hurts most** — a within-arm recency kernel ON the L
  register itself, mechanically explaining the s328 non-monotone curve
  [2.96, −0.05, −0.13, 0.35] and quantifying how within-arm recency
  coexists with block-level primacy inside ONE register. Also read on
  T(band) (advisory). Secondary: reported with its own gate, does not
  move the OR1 verdict.

### Verdict tree + a-priori (frozen, NOT tuned; modal split on the mundane)

```
¬OR0 (anchor/identity)    → VOID                    10
¬OR0 (split replication)  → SPLIT-NOT-REPLICATED    10
A<0 ∧ B>0 (both sig)      → DEPTH-COMMITMENT        30
A>0 ∧ B<0 (both sig)      → REGISTER-DISSOCIATION   20
else                      → ENTANGLED-PARTIAL       30
```

### Read discipline (banked at freeze)

- **Honesty note, named not hidden:** DEPTH-COMMITMENT is both
  mundane-lore-modal (decisions form late) AND frame-friendly (sharpens
  the two-register law into a depth law: recency-tracking evidence at
  mid-depth → late commitment). Its 30 is the mundane mass, not a hope.
- Mid-band logit-lens is historically noisy → ENTANGLED-PARTIAL co-modal
  at 30. An ns cell is an ns cell; do not narrate it into a sign.
- Neither DEPTH-COMMITMENT nor REGISTER-DISSOCIATION damages the s328
  EARLY-COMMITMENT win — both LOCATE the split. Only SPLIT-NOT-REPLICATED
  would reopen s328 (and would do so as instrument drift, not verdict
  reversal — investigate before any claim).
- DEPTH-COMMITMENT licenses: "the order-sign split is a depth split on
  this substrate; the behavioral primacy decision forms late from
  recency-tracking mid-depth evidence." REGISTER-DISSOCIATION licenses:
  "the axis and the behavioral readout carry different order laws at all
  depths on this substrate." Nothing beyond.
- Bounds: single model (Qwen3-4B), n=20 (same nonces as s328), k_own=3,
  single-context timescale; residual position mismatch only in
  multi-token pred tails (dominant read matched at `w`); per-layer axes
  assume real-member class geometry is estimable at every layer (axes
  quality reported per layer, thin-axis layers flagged not silently
  read).

### Provenance

MIT (lambda provenance). Reuses frozen s315/s320/s328 harnesses
(type_icl_tag, idempotency via tape_subtraction, tape_subtraction)
unchanged; no fork (λ one_way).

### §Result (s329) — VERDICT: ENTANGLED-PARTIAL (co-modal a-priori 30) — but the L-side is depth-resolved

Qwen3-4B, same 20 nonces as s328, n_null 10k, 146s, clean.

- **OR0 SANE/replicate: ✓ exact.** Identity LL(final)≡L to 0.0000
  (mean and max); real margin 2.538 (= s328); D_L(final) = **+0.478**
  p=0.0003 (s328: +0.478 — replicated to the third decimal) and
  D_T(band) = **−1.304** p=1e-4 (s328: −1.30). Deterministic reuse
  delivered; the split is real and stable.
- **OR1 CROSSING — cell A LICENSED, cell B ns:**
  - **A = LL(band) = −0.367, p=0.0002 (recency).** The behavioral
    readout at T's depth reads RECENCY. Combined with D_L(final) =
    +0.478 p=0.0003 (primacy), **the sign flip is depth-carried WITHIN
    the behavioral instrument — both cells significant, readout held
    fixed. Licensed.**
  - **B = T(final) = +1.478, p=0.15 (ns).** Sign agrees with the depth
    story (primacy direction at final depth) but does not clear the
    gate. An ns cell is an ns cell (banked discipline) → the frozen
    tree lands **ENTANGLED-PARTIAL**, not DEPTH-COMMITMENT.
- **OR2 depth profiles (advisory):** D_LL is recency-negative through
  nearly all depth, flipping positive only at L34 (+0.24) → L35 (+0.48).
  D_T is ≈0 early, **deepens into recency through the band (−5 to −6 at
  L30–33)**, then snaps to +1.48 at L35. Commitment depth ℓ* = 34 (LL)
  / 35 (T) of 36. Both instruments share the shape: **recency runs
  deep; primacy exists only in the last two layers** (pattern-suggests
  at the T grain, licensed at the LL grain).
- **OR3 RECENCY KERNEL (secondary): ✓ LICENSED** — kernel = +0.440,
  p=0.002. Slot curve [0.386, 0.472, **0.741**, **−0.054**]: not a
  monotone distance decay but **last-statement dominance** — a trailing
  contradiction crashes L below zero while the same contradiction one
  slot earlier (one own statement after it) leaves L at its healthiest.
  Slot3 (−0.054) replicates the s328 k=1 crash (−0.05, same arm,
  construction identity validated). T-band kernel advisory +2.00, same
  direction — the within-arm recency is cross-substrate.

**THE READ (per frozen discipline).** The queue's binary — genuine
register dissociation vs instrument artifact — resolves **on the L side
as DEPTH**: at matched (band) depth the behavioral readout AGREES with
T's recency; the s328 primacy is a **final-layers phenomenon** (L34–35).
So the s328 "L vs T" split was substantially a **depth split wearing a
readout costume**. What keeps the verdict at ENTANGLED-PARTIAL is the
converse cell: the axis readout at final depth points to primacy
(+1.478) but is too noisy across nonces to license. The two-register
law survives in sharpened, more physical form as a **two-DEPTH law,
licensed on the behavioral instrument**: *recency-tracking evidence
runs through the stack; the primacy decision is assembled in the last
two layers.* The representational converse remains pattern-suggests.

**s328 win intact.** OR0 replicated the EARLY-COMMITMENT endpoints
exactly; nothing here reopens the tape-side forward win — the win's
register (behavioral L at the model's output) is precisely where the
primacy decision lives. The s328 caveat-1 (register split) is now
partially discharged: it is mostly a depth split, licensed L-side.

**Honest caveats:** ① cell B ns is the reason this is not
DEPTH-COMMITMENT — a higher-powered T read at final depth (more nonces,
or variance-reduced axis estimation) is the sharpening path if wanted;
② single model, single context, k_own=3, same-20-nonce sample (paired
by design, not a fresh draw); ③ per-layer axes assume estimable class
geometry at every layer — final-layer axis noise is plausibly why B is
ns (axis quality was not gated per layer, reported only).

**⚠ PROVENANCE QUALIFIER (s329, §P-ORDER-PROVENANCE):** the last-two-
layers primacy flip does not exist in Qwen3-4B-Base — the depth law
re-reads as "post-training installs a decision stage on top of a
native recency-tracking stack" (see §P-ORDER-PROVENANCE §Result).

**Follow-on candidates (unfrozen):** T-final power probe (cheap; more
nonces on one cell) · slot-curve mechanism (is last-statement dominance
attention-mediated? — connects to the §11 tag-transit machinery).

## §P-ORDER-PROVENANCE — FROZEN (s329, Michael GO "let's run it now") — is primacy native or installed?

> Michael's confound on the s329 read: Qwen3-4B is a POST-TRAINED
> model, and lore (external, NOT project-licensed — mementum has no
> measurement of this) holds that post-training concentrates in late
> layers. The s329 "primacy is assembled in the last two layers" could
> be pretraining physics OR an RLHF/instruct-installed behavior riding
> on a recency-tracking base. Post-hoc hypothesis → owes this pre-reg,
> frozen before any base-model data.

### Claim under test

Does the base model of the same lineage (`Qwen/Qwen3-4B-Base`) show
the late-layer behavioral primacy (D_L(final) > 0 on the s328 order
arms), or is primacy absent/inverted in base — i.e., installed by
post-training? Stakes: if installed, the s328 EARLY-COMMITMENT win
REQUALIFIES as an alignment-overlay behavior, not base physics (the
win's measurement stands; its reading changes).

### Design (λ one_way — instrument unchanged, model swapped)

`order_reconcile.py --model-id Qwen/Qwen3-4B-Base`, all gates as
built. **One disclosed pre-run instrument addition:** OR0 gains the
recency tail on the final-layer L gate (previously primacy-tail only)
— needed to separate INVERTED from ABSENT below. No other change.
Nonce selection is deterministic from the tokenizer; if base tokenizes
identically the same 20 nonces carry over (checked at run, reported).

### Gates (read from the base run's results.json)

- **PV0 SANE (void):** OR0 anchor on base — real-member margin ≥ floor
  ∧ per-class ok ∧ standing L(own-only) > 0 ∧ identity LL(final)≡L.
  Base failing the anchor = instrument not portable → VOID, no
  provenance claim either way.
- **PV1 (make-or-break):** sign + significance of base D_L(final)
  (own-first-bal − anti-first, paired perm, both tails):
  - **> 0 sig → NATIVE-PRIMACY** — primacy predates post-training on
    this lineage; the RLHF confound is excluded here; the s329 depth
    law reads as pretraining physics.
  - **< 0 sig → INVERTED-IN-BASE** — base reads recency at the
    output; post-training FLIPPED the order law → primacy is
    installed. s328/s329 readings requalify (alignment overlay).
  - **ns → ABSENT-IN-BASE** — no order law at base output;
    post-training created one where none existed. Installed-flavored
    but weaker (power caveat mandatory; n=20 fixed).
- **PV2 (advisory):** base crossing cells A/B + depth profiles — does
  the recency-through-the-stack shape exist in base? (If yes under
  INVERTED/ABSENT: the evidence substrate is shared and only the
  top-layer decision differs — the sharpest installed-behavior
  picture.) Cross-model per-nonce Δ (same nonces) advisory only.

### A-priori (frozen, NOT tuned — flat on the live three; genuine ignorance)

```
NATIVE-PRIMACY 30 / INVERTED-IN-BASE 30 / ABSENT-IN-BASE 30 / VOID 10
```

### Read discipline (banked at freeze)

- INSTALLED verdicts do NOT retract s328/s329 measurements — they
  re-attribute them. EARLY-COMMITMENT stays a real behavior of the
  deployed model; what changes is whether it belongs to the compiled
  type system or to the alignment layer.
- ABSENT is not proof of installation (one-sided power); say so.
- External lore (post-training-lives-late) stays uncited-as-evidence;
  this run is the project's own first measurement on that question.
- Bounds: one lineage (Qwen3-4B), one base/instruct pair, same 20
  nonces, single context.

### Provenance

MIT. Same harness, model swap only; recency-tail addition disclosed
above, committed pre-run.

### §Result (s329) — VERDICT: ABSENT-IN-BASE (a-priori 30, flat prior) — post-training installs the commitment

Qwen3-4B-Base, same 20 nonces, 146s, clean; instrument fully portable
(PV0 ✓: real margin 2.933, standing L 3.152 — base does the licensing
task fine; identity LL(final)≡L to 0.0000).

- **PV1 (make-or-break): base D_L(final) = −0.090** — primacy p=0.837,
  recency p=0.163, **ns both tails**, and the point estimate is near
  zero (vs instruct +0.478). The base model has **no behavioral order
  law at the output**: 3-own-first and 3-anti-first prefixes license
  identically.
- **PV2 (advisory) — the sharpest installed picture, exactly as named
  at freeze:** the recency evidence substrate is **native and
  STRONGER in base** — LL@band = −0.824 p=0.0001 (instruct: −0.367);
  T@band = −3.747 (instruct: −1.304); T order-recency reaches −11..−14
  at L30–33 (instruct: −5..−6). But there is **no positive flip
  anywhere in the stack**: commit_layer = None on BOTH instruments;
  the profiles collapse toward ≈0 at the top and stop. The instruct
  model's L34/35 primacy flip **simply does not exist in base**.
- **OR3 (advisory): no primacy repair in base.** Slot curve
  [−0.049, 0.329, 0.488, −0.054] vs instruct [0.386, 0.472, 0.741,
  −0.054]: a *leading* contradiction stays fatal in base (slot0
  −0.049) where the instruct model recovered (+0.386). The kernel stat
  is flat (p=0.49) because both ends crash. The T-band kernel (+2.86)
  matches instruct (+2.00) — representational recency is shared.

**THE READ (per frozen discipline).** Shared substrate, differing top:
both models track evidence with the same (base: stronger)
recency-flavored representation through the stack; the base model's
order effects cancel to nothing at the output; the post-trained model
adds a positive flip in the last two layers that turns first-assertion
into a durable commitment. **The primacy decision is
post-training-installed; the recency evidence physics is native.**
This is also the project's **first own measurement** of the
"post-training lives late" lore — on this lineage, at this behavioral
grain, it holds (the installed delta localizes to L34/35).

**Re-attribution (banked at freeze — measurements stand, readings
change):**

1. **s328 EARLY-COMMITMENT** remains a real, pre-registered behavior of
   the deployed model — but it is a property of the **post-trained**
   tape face, not base compiled-type physics. The base tape face is an
   order-neutral evidence integrator at the output.
2. **s329 depth law** sharpens: not "the model assembles its decision
   late" but "**post-training installs a decision stage on top of a
   native recency-tracking stack**." More mechanistic than before, and
   coheres with the behavior-is-tape-resident / installed-behaviors
   thread.
3. §Synthesis tape-side spine: the sign-is-the-decision reading on the
   tape now carries a provenance qualifier — the *decision* register
   observed there is (on this lineage) an alignment-layer feature.

**Honest caveats:** ① ABSENT ≠ proof of installation (one-sided
power; n=20 — though the near-zero point estimate is reassuring);
② "post-training" is the whole Qwen3 pipeline (SFT + RL + thinking
distillation) — **cannot attribute to RLHF specifically**; ③ one
lineage, one base/instruct pair; ④ base and instruct differ in data
recency too (minor here — nonces are nonces).

**Method door opened:** base-vs-instruct differential runs are a cheap
provenance attribution instrument for ANY behavioral finding in this
project — one --model-id swap. Candidate discipline: behavioral wins
on post-trained models owe a base-model provenance check before being
read as compiled-substrate physics.
