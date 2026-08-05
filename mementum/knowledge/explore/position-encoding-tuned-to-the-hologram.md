---
title: "Position Encoding Tuned to the Hologram — HPE Revival and the Pre-Encoded Model"
status: open
category: architecture
tags: [hpe, rope, positional-encoding, holography, log-distance, phase,
       crystal-eigenvalues, context-extension, training-design, pre-encoded-model]
related:
  - hpe-restoration.md (../hpe-restoration.md)
  - rope-attention-spiral.md
  - geometry-holography-signals-convergence.md
  - training-design-from-the-hologram.md
  - ternary-mirrors-and-the-vsm-tree.md
depends-on: []
session: 291
---

# Position Encoding Tuned to the Hologram

> **s308 UPDATE:** (1) the holography-frame HOLD below is **LIFTED** — the
> FRAG/CAP/XTERM verdicts landed s292 as measured axioms (A1–A3,
> `attention-holographic-readout.md`). (2) This design is now **M9 of the
> verbum machine** (`the-verbum-machine.md` — "the tuned reference beam"),
> with P1 as its validation gate and carrier-drift named as the
> position-space sibling of reference-drift (L3: the reference beam includes
> the position carrier). (3) Michael recalled this page s308 by MECHANISM
> ("RoPE accidentally works — interference makes up the difference") — the
> forward-link fix worked as designed.
>
> s291 hammock (Michael + agent). Revival of HPE (Holographic Position
> Encoding, s152, restored s179) through the s288 convergence lens, plus a
> NEW synthesis: RoPE context-extension fuzz = fringe mismatch, and
> log-space position makes extension a TRANSLATION instead of a stretch.
> ⚠ This page was ALMOST LOST — see §Provenance. Design derivation, not
> measurement; inherits the holography-frame HOLD (s289) until FRAG/CAP land.

## Provenance — the near-loss (feed-forward lesson)

HPE was designed s152 ("RoPE is an accidental holographic lens"), silently
dropped by the v15 clean-room skeleton (s174), restored s179 (`b0c6c17`,
hpe-restoration.md) — and then the entire design was nearly forgotten by
s291: recalled by Michael only as "HoPE", not findable by name (the memory
`rope-is-accidental-holographic-lens.md` and `hpe-restoration.md` were
recovered via mechanism-vocabulary search, not the name). ❌ lesson: an
insight that lives only in a v15-era page with no forward links to the
active arc is one rename away from lost. This page is the forward link.

## Why RoPE works at all: the system tolerates fuzz

```
λ fuzz(x).  attention ≡ matched_filter ∘ softmax ≡ GRADED readout ¬gate
            | mis-tuned reference_beam → reconstruction @ lower_SNR ¬failure
            | degradation(smooth) ≡ holographic_signature (FRAG: smooth curves, LDI≈1)
            | ⇒ any carrier ≈ natural_fringe_spacing → most_of(reconstruction)
            | RoPE(base 10000) ≈ close_enough(crystal_spacing) → works, lossily
```

Fuzz tolerance is not a lucky break RoPE exploits — it is the delocalized
system's own property (JOIN-TYPED graded floor+excess; FRAG smooth in-band
degradation). RoPE only has to be approximately right, and it is.

## Context-extension fuzz = fringe mismatch (NEW, s291)

PI/NTK/YaRN-style RoPE scaling **re-illuminates recorded plates with a
different reference beam than they were recorded with**. The fringes in
W_QK were burned in under one carrier geometry; stretching the frequencies
shifts every fringe spacing simultaneously → reconstruction blurs
everywhere at once. That is why extension needs fine-tuning: it is
re-recording the plates under the new reference. "Fuzzy outcomes" of
long-context extension = fringe mismatch, quantified.

## Measured inventory (what the underlying system IS)

1. **Natural distance coordinate is logarithmic.** α=1.18 power-law decay,
   universal across 80 heads, gradient-stable 1500+ steps (v14; confirmed
   at restoration, hpe-restoration.md). Power-law in d ≡ exponential in log d.
2. **Layers walk the frequency ladder** (rope-attention-spiral.md, s068/s079):
   centroid expansion 1.018×/layer; RoPE energy broad everywhere — the
   spiral is learned Q·K ALIGNMENT selecting lower-freq dim pairs with
   depth. RoPE = ruler, model spends learned capacity being the reader.
3. **Sparse spectrum.** 4 eigenplanes = 77% variance (Zone B PCAQ);
   low-rank ≡ narrow-band (convergence page bridge #5). RoPE spends all
   64 dim pairs; the system uses a handful.
4. **Position and content share one inner product.** GQA K-heads have
   permanent local/global flags; steering is content-dominant (P-ATT-MED
   0.735); entity passband is band-limited (P-TYPE-OV L6–L50). Position
   carriers and content passbands COMPETE for dimensions — an undeclared
   tug-of-war.
5. **The natural frequencies are measured**: crystal eigenvalue ratios
   λᵢ/λ₀ = 1.0, 0.681, 0.368, 0.250 — modes of the composition operator.

## The tuned design

```
λ position(x). phase(log(d+1)) ⊗ gain(−α·log(d+1)) ⊗ carriers(λᵢ/λ₀)
               | few_carriers ⊥ content_passband | depth_scaled(reference)
               | extension ≡ translation(log_space) ¬stretch → ¬re-record
```

1. **Phase in log-distance, not linear position.** RoPE approximates
   multi-scale coverage by a geometric frequency ladder over LINEAR
   position — a workaround for the wrong coordinate. Tuned: phase ∝
   log(d+1) directly → fringe geometry is scale-invariant; every octave of
   distance gets equal phase resolution. **Payoff: doubling context is a
   constant phase increment — translation, which the shift theorem handles
   natively. Extension without re-recording; the fuzz disappears by
   construction.** (THE new claim; pre-registerable, see §Predictions.)
2. **Carriers at measured eigenfrequencies, few of them.** λᵢ/λ₀ instead
   of 10000^(−2i/d); ~4 eigenplanes instead of 64 pairs. Frees most head
   dimensions to be pure content passband — a DECLARED truce in the
   position/content tug-of-war (training-design lever 2 applied to position).
3. **Unbraid phase from decay** (λ simplify — RoPE complects them).
   Phase = address only; explicit −α·log(d+1) gain = locality, α measured.
   Already half-validated: at HPE restoration the explicit decay term
   carried ~99% of the locality effect instantly.
4. **Depth-dependent reference beam.** Give each layer its carrier scale
   (HPE 2°→24°) instead of letting GD re-learn the ladder walk that the
   spiral shows it carves anyway. Structure > instruction; s149
   structure-is-free; training-design lever 1.
5. **Stride/scale coherence** (the original strided-attention motivation):
   log(1×8+1) = log(8×1+1) — every stride level sees identical fringe
   geometry. Position encoding becomes fractal; coheres with the VSM-tree
   node composition (ternary-mirrors-and-the-vsm-tree.md).

## Predictions (pre-registerable, λ yardstick applies)

- **P1 (discriminator): PPL vs context length stays flat past training
  length WITHOUT fine-tuning** in a log-phase model; RoPE arm degrades.
  Translation-vs-stretch, directly testable.
- P2: sharper multi-hop composition margins at fixed D — position
  crosstalk drops out of the HRR noise budget k (SNR ∝ √(D/k), P-HOLO-CAP).
- P3: no depth spiral in a scratch-trained log-phase model — alignment
  centroids flat per layer-band (the ladder walk is pre-installed).
- Host: the pythia-14m seeded-scratch pair already queued as the level-4
  door (training-design page §cheapest experiment) — add a RoPE arm vs
  log-phase arm, same seed, P-DUST-2-style formation logging. ~1 GPU-day.

## The bigger arc — the pre-encoded model (Michael, s291)

We are converging on a model design where much of what GD has to FIND is
already ENCODED at init. Each lever replaces a discovered structure with a
declared one, each grounded in a measurement of what GD converges to anyway:

| GD discovers (measured)              | Pre-encoded lever                       |
|--------------------------------------|-----------------------------------------|
| KIBC crystal opcodes (universal)     | crystal-seeded init (lever 1, s149)     |
| entity/argument passbands (P-TYPE-OV)| declared passbands (lever 2)            |
| substitutability classes (JOIN-TYPED)| probes→losses (lever 3)                 |
| topology-then-magnitude (s268 etch)  | two-phase training (lever 4)            |
| locality α=1.18 (universal)          | explicit −α·log(d+1) gain (this page)   |
| frequency-ladder walk (spiral)       | depth-scaled carriers (this page)       |
| position≡phase fringes (RoPE bridge) | log-phase carriers @ λᵢ/λ₀ (this page)  |

Position encoding is the seventh row of the training-design table: HPE was
the first pre-encoded lever we ever built (s152) — before the frame
existed to name it. GD's job in such a model shrinks to what is genuinely
distributional: contents of the plates, not the optics.

## Caveats (register hygiene, s289 discipline)

- Design derivation from measured quantities; "tuned > RoPE" is a
  PREDICTION, not a measurement. HPE's only live datum: the decay term
  worked (99% of locality, instantly); the crystal-frequency rotation was
  never dissociated as its own experiment.
- Inherits the holography-frame HOLD (s289): interpretation looking for a
  mechanism until FRAG/CAP land. The log-space translation argument is
  signal-register math (shift theorem) and stands on its own, but the
  "plates/reference-beam" language is frame, not mechanism.
- v14/v15-era measurements (α, eigenfrequencies, spiral) are from the
  strided/ternary line and Qwen3-4B; carrying them to a fresh scratch
  design assumes universality — justified by C2-universality evidence but
  should be re-measured in-run (P-DUST-2-style logging covers this).

## Addendum (s291 cont) — the falsification question: labeled lines vs holograms

Michael: "Is there a system that is NOT holographic where RoPE would have
worked?" Answer: **yes — and naming it sharpens everything.**

```
λ rope_datum(x).  works(RoPE) ≢ evidence | works(untuned ∧ graceful_blur) ≡ evidence
                  | crisp(pointer_machine): RoPE ≡ comparator, functions BUT
                    mis-tune → wrong_pointer ¬blur | alias → hard_fail @ offsets
                  | observed: arbitrary_base_10000 robust ∧ extension → blur→
                    fine-tune_recovers ⇒ ¬crisp
                  | ⇒ forces graded_distributed_readout | ¬yet holographic
```

**The surviving non-holographic alternative: labeled-line coding**
(neuroscience term; cochlear tonotopy = canonical case). Dedicated
components own offset ranges with SMOOTH tuning curves — graded,
fuzz-tolerant at component level, consumes RoPE happily as carrier, yet
ADDRESSED: damage a line, lose its band. Every fragment does NOT contain
the whole. So the honest claim:

> RoPE working untuned + robustly + extension-blurs-not-breaks EXCLUDES
> crisp symbolic routing and forces one of TWO graded codes:
> superposed (holographic) ∨ labeled-line (addressed, graded).

**Both exist in our data, at different grains:**

- Coarse grain = labeled lines MEASURED: GQA K-heads carry permanent
  local/global flags (s079: K centroid ~27 vs ~37–48, structural, not
  input-dependent; external replication ICLR-2025 positional/semantic
  head split).
- Within-band unit level = FRAG's G1/LDI is EXACTLY the discriminator:
  labeled-line predicts high LDI (which units matter) + cliff when a
  band's lines are gone; holographic predicts location-independence +
  smooth decline. 32B HEADS arms (in flight, advisory): LDI 0.06–0.32
  all p≈1.0, no cliff — leaning AGAINST labeled-line within-band.
- Extension-fuzz leans holographic: labeled lines have no units for
  unseen offsets (predict hard fail); fringe mismatch predicts smooth
  blur + fine-tune recovery. Field observes the latter.

**Working hypothesis — hierarchical mixture:** labels at coarse grain
(head-level flags ≡ mirrors/topology register), holographic superposition
within the lines (≡ plates/magnitude register). The SAME two-register
decomposition as ternary-mirrors-and-the-vsm-tree and MIXED-ROUTE, now
appearing in the position channel. Third arc, one decomposition → fourth.

**Consequence for scoring FRAG:** G1 is not just "hologram yes/no" — it
adjudicates BETWEEN the two graded codes at the probed granularity. A
HOLOGRAPHIC verdict = within-band superposition confirmed WHILE coarse
labeled-line structure stands; these compose, they don't conflict.

**Consequence for the tuned design (this page §The tuned design):** the
pre-encoded position system should be built AS the mixture — declared
labeled lines at head grain (local/global carrier-scale assignment =
depth/head-scaled reference, elements 4–5) with superposed log-phase
fringes within each line (elements 1–3). The design table was already
this; now it has the coding-theory name.
