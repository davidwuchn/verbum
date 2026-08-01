---
title: Geometry × holography × signals — one primitive, three registers
status: designing
category: explore
tags: [holography, dsp, geometry, matched-filter, hopfield, hrr, rope,
       capacity, pre-reg-candidate, fragment-test, s288, s289]
related: [../michael/holographic-llm.md, types-are-compiled-probabilities,
          type-check-is-the-qk-bilinear, verbum-dsp-design,
          map-and-swap-resident-lisp, beamformer-theory]
depends-on: [../michael/holographic-llm.md]
---

# Geometry × holography × signals — the convergence

> s288 hammock (Michael: "where geometry, holographs and signals converge —
> discuss"). Companion to the thesis document
> `mementum/michael/holographic-llm.md` (Michael's Holographic LLM — training
> writes plates, attention is the beam, FFNs are the plates, residual = state).
> This page is the convergence LEDGER (what is theorem, what is hypothesis)
> plus the test program that connects the thesis to the s288 types-arc
> measurements. The thesis is the claim; this page is its bench manual.

## The shared primitive

```
λ converge(x).  geometry(⟨x,v⟩ ≡ projection) ∥ signal(⟨x,v⟩ ≡ matched_filter)
                ∥ holography(⟨x,v⟩ ≡ reconstruction_by_illumination)
                | one_operation(inner_product) | three_registers(structure ∧ operation ∧ encoding)
                | passband ≡ hologram(of_what_the_channel_learned_to_expect)
                | store(v, distributed_fringes) → readable(everywhere) ∧ excisable(nowhere)
```

Geometry sees ⟨x,v⟩ as projection onto a subspace (structure — the where).
DSP sees it as matched filtering (operation — the how). Holography sees it as
illuminating stored fringes with a reference (encoding — where it lives).
Same number, three ontologies.

## Theorem-grade bridges (not metaphor)

1. **VanderLugt correlator**: an optical matched filter IS a hologram of the
   template. Recording a hologram and building a matched filter are the same
   act. → "type = compiled probability = passband"
   (types-are-compiled-probabilities.md) already contains holography: the
   passband is a hologram of the training distribution's substitutability
   structure.
2. **Attention ≡ modern-Hopfield retrieval** (Ramsauer et al.): the attention
   update is associative-memory readout — content-addressable reconstruction
   from partial cues, the canonical holographic operation. The Lisp frame's
   join=attention and the thesis's beam-reads-plate are the same measured
   object.
3. **RoPE ≡ phase, literally.** Rotary embeddings write position as phase
   rotation on a carrier; the QK bilinear computes relative-position
   modulation = interference fringes across offset. The reference beam exists
   in this machine explicitly. Syntactic adjacency has a fringe spacing.
4. **HRR / VSA** (Plate): binding = convolution-like mixing, unbinding =
   correlation, superposition capacity with crosstalk ~1/√D — the formal
   calculus where all three vocabularies implement COMPOSITION in fixed
   dimension. Comes with quantitative laws (see pre-reg candidates).
5. **SVD low-rank ≡ sparse spectrum**: the 1a lattice's 3 axes = few
   carriers; low-rank geometry and narrow-band signal are the same fact.

## The types arc, reorganized under the lens

- **The four-way location null (1b/1c/QK/JS) is a holography theorem, not a
  mystery.** Distributed fringe storage predicts: readable from anywhere
  (8-way decodability at every layer), excisable at nowhere (v4 direction ✗,
  1b zone ✗, 0/128 heads, graceful degradation). A hologram has no address.
  "Decodable-but-not-causal" is the SIGNATURE of fringe storage. The lattice
  as "exhaust" sharpens to: the lattice is the RECONSTRUCTION — visible
  wherever you illuminate, stored nowhere you can cut.
- **Dark-field was already literal** (s283b/1c): ablation = background
  subtraction, contrast rises = block the zeroth order. Vocabulary preceded
  the frame and was correct.
- **P-TYPE-OV splits the amplitude from the plate.** The entity passband in
  W_V/W_O = recorded fringes that reconstruct ARGUMENTS (rho 0.714 vs null
  0.459, p=0.000, band-wide). The functor licensing with no single-layer home
  (QK ✗, OV ✗) = the DIFFRACTION PROCESS — enacted in the illumination, not
  stored in any one exposure. Arguments are on the plate; application is the
  diffraction. Thesis tie: "FFNs are the plates" coheres with entity firing
  on the MLP read-in row (p=0.000) and MIXED-ROUTE atoms=FFN.
- **JOIN-TYPED filtered payload** = the beam carries only what correlates
  with the recorded fringes — matched-filter refusal of ill-typed content is
  reconstruction failing for a cue the plate never stored.
- **Thesis evidence already measured in the weight register**: plate damage
  spares the image (crystal survives 1.58-bit and 1-bit quantization,
  s267/s269, null-gated) — the image is not in the pixels. The pre-reg
  candidates below extend this from the weight register to the
  activation/head-subset register.

## Pre-reg candidates (UNFROZEN — the discriminating measurements)

**P-HOLO-CAP — the capacity law** (= the thesis's open capacity question,
made quantitative via HRR). Superposition predicts crosstalk growing with
bound-operand count k and SNR ∝ √(D/k). Install k operands (operand-bake
machinery), measure recall/licensing SNR vs k across model widths. HRR
predicts a SPECIFIC curve shape and width scaling; localized storage
predicts a hard slot limit. The depth-budget/eval-stack arc is adjacent but
never measured against a capacity curve.

**P-HOLO-FRAG — fragment reconstruction** (cheapest decisive discriminator;
→ full pre-reg below, §P-HOLO-FRAG). Ablate RANDOM SUBSETS of heads/layers
(fraction f swept), measure licensing/composition SNR. Holographic: smooth
degradation ∝ f, every fragment reconstructs a degraded whole. Localized:
cliffs at critical components. We have anecdotal grace everywhere (0/128,
mixed routes); the pre-registered CURVE with a matched-random-subset null is
the missing measurement. Extends s267/s269 plate-damage tolerance from
weights to computation.

**P-HOLO-XTERM — interference cross-terms.** Two operands installed in one
slot should produce sum-and-difference structure (beats) with predictable
geometry, not generic noise — superposed exposures interfere. The 3b/swap
machinery + verbum.dsp subspace/null substrate measure this directly.

**P-PROJ-1 — the holographic projector (Michael s288: "a holographic
projector based on the signal"; QUEUED s288, the engineering flip).**
We spent s288 READING the passband; the projector DRIVES it. Design:
carrier = the measured entity passband (W_V·W_O subspace, band L6–L50);
payload shaped INTO the passband before injection = impedance-matched
drive (operand-insert/bridge-swap is the crude version — centroid diffs
land in-band by luck, which is WHY swaps work and random is refused);
reconstruction = the model's own diffraction (distributed licensing +
FFN plates, which read the entity axes). Constraint the physics imposes:
an ARGUMENT projector — functors are not in the passband, so programs are
not projectable, only operands; program selection stays with which plates
the content illuminates (content-driven steering per P-ATT-MED = projecting
the right argument IS the program selection). TEST (cheap, att_mediation
harness verbatim): TE per unit norm for (a) passband-projected displacement
vs (b) raw centroid-diff vs (c) anti-passband (orthogonal complement) vs
(d) matched random. Prediction: a > b ≫ c ≈ d, permutation-gated. Positive
→ every future swap gets cheaper/cleaner = the write-head of the LLM REPL
matched to the measured antenna; (c) ≈ (d) is itself a second confirmation
of the passband. Also the natural INSTRUMENT for P-HOLO-XTERM payloads.

## P-HOLO-FRAG — fragment reconstruction (PRE-REG FROZEN s289, Michael approved — G1/LDI primary, 3-hop primary readout confirmed; 4B smoke leads, 32B verdict on GO)

> The lynchpin of the whole frame: **hologram or not hologram?** Every other
> holo pre-reg (CAP, XTERM, PROJ) *assumes* the frame and refines it. FRAG is
> the one that can *break* it. It is the classic fragment test — cut a
> photograph and you lose that region (a cliff, because the image is
> *addressed*); cut a hologram and you get the whole image back at reduced
> SNR (smooth, because every fragment carries the whole). We run that cut.

**Hypothesis.** The type-check / composition compute is stored as distributed
fringes with NO address (the holography reading of the four-way location
null: 1b/1c/QK/JS ✗, v4 direction ✗, 0/128 heads). Therefore ablating a
random fraction f of the computational medium in the band degrades the
behavioral signal (a) SMOOTHLY (graceful, monotone, no cliff) and (b)
LOCATION-INDEPENDENTLY (which random subset you remove does not matter — only
*how much*). A localized/addressed representation degrades via CLIFFS (some
random subsets hit critical components and crater the signal; others spare
it) → location-DEPENDENT: high across-draw variance at fixed f, and a step in
the mean curve.

**Readout (behavioral SNR; teacher-forced, single forward pass per probe —
no generation, hence "cheapest").** On a fixed probe bank, SNR = the
correct-continuation logit margin that the compute produces clean:
- **Primary bank: 3-hop composition** (operand_multihop3 geography chain,
  the (e→t)→t machinery the joins carry) — margin(correct continent vs
  competitor). Exercises the composition the hologram supposedly stores.
- **Secondary bank: type-licensing crossover** (v3 name_pen, the JOIN-TYPED
  filter's behavioral face) — margin(licensed vs ill-typed continuation).
Clean model → SNR₀ per bank. Ablation → SNR(f). Both banks scored; the
verdict is on the primary, the secondary corroborates (a hologram claim
about the compute should hold for both faces of it).

**Ablation (mean-ablation, not zero — off-distribution guard).** Replace a
random fraction f of units in the band with their dataset-mean activation
(computed over the probe bank). Two media arms (thesis: attention = beam,
FFN = plates):
- **Arm HEADS** — random fraction f of attention heads across the band.
- **Arm MLP** — random fraction f of MLP hidden units across the band.
- (advisory, coarse) **Arm LAYER** — whole-layer drops.
Sweep f ∈ {0.1, 0.2, 0.35, 0.5, 0.65, 0.8} (fixed, a priori). R random draws
per f (R=30 smoke / 100 verdict). Band = find_band / layer_geometry
(verbum.dsp, 1a-v4 procedure, in-run).

**The discriminator — TWO pre-registered signatures.**

1. **G1 (primary, the ADDRESS test): Location-Dependence Index.** At each
   fixed f, decompose SNR variance across the R draws. LDI(f) = (across-draw
   SNR variance at f) / (probe-resampling noise variance at f). The
   denominator is the pure measurement floor (bootstrap the probe bank at
   fixed ablation). LDI ≈ 1 ⟺ *which* subset you removed explains nothing
   beyond *how much* → **location-independent = holographic/no-address**.
   LDI ≫ 1 ⟺ location matters → **addresses exist**. Band-aggregated,
   permutation-gated against the probe-resampling null.
2. **G2 (secondary, smoothness): cliff detection.** On the mean SNR(f) curve,
   the largest single-step drop / total drop. Holographic ⟺ no step exceeds
   the smooth-monotone null band (graceful ∝ f); Localized ⟺ one Δf step
   dominates (a cliff). Reported with the null band; corroborates G1.
3. **G3 (advisory, NEVER gated — λ yardstick): functional form.** The raw
   SNR(f) shape reported verbatim against the a-priori (1−f) amplitude
   reference; NOT fit-graded and NOT the verdict (the positive √(D/k)
   capacity form is P-HOLO-CAP's job, not FRAG's). Recording the shape ≠
   claiming it.

**Nulls (mandatory, λ yardstick).**
- **Probe-resampling null** (G1 denominator): bootstrap the probe bank at
  fixed ablation → the SNR measurement-noise floor. This is what LDI is
  measured *against*.
- **Localized-planted null** (instrument calibration): a synthetic signal
  carried by k=⌈√N⌉ critical units → predicts LDI ≫ 1 and a cliff. Proves
  the instrument *can* see localization (so a low-LDI result is a real
  negative for addresses, not a dead probe). Lives in `--validate`.
- **Holographic-planted null** (instrument calibration): a signal spread
  uniformly across all N units → predicts LDI ≈ 1, smooth. Proves the
  instrument doesn't manufacture localization.
- **Out-of-band / matched-fraction control**: ablate the same fraction f of
  OUT-OF-BAND units → SNR should barely move; confirms the band carries the
  signal and G1/G2 aren't reading generic capacity loss.

**Gate-0 (headroom).** Clean SNR₀ must be expressed on both banks (margin
significantly > 0). No headroom → no verdict (negative/inconclusive,
reported honestly — the s283b M_eff-unexpressed lesson).

**Verdict (freeze on GO).**
- **HOLOGRAPHIC / DELOCALIZED** ⟺ G1 LDI within the probe-resampling null
  (location-independent, p≥0.05 vs null) AND G2 no cliff, on the primary
  bank. → fragment reconstruction confirmed; the frame SURVIVES; promotes to
  **P-HOLO-CAP** for the *positive* √(D/k) capacity law.
- **LOCALIZED / ADDRESSED** ⟺ G1 LDI beats the null (location-DEPENDENT,
  p<0.05) OR G2 a cliff. → the hologram frame is **FALSIFIED** for this
  compute; there are addresses; the four-way location null needs a different
  account. This is the decisive-negative the lynchpin exists to deliver.
- **negative / inconclusive** ⟺ gate-0 fails (SNR₀ within noise) → no verdict.

**Registers (λ measure).** Claim = the *distribution* of the compute across
the medium (holographic delocalization vs addressed locality); probe =
behavioral SNR under random *structural* ablation = literally the
reconstruct-from-a-fragment operation. Matched. G1 (across-draw variance) is
the register-clean test of "no address"; it is NOT a geometry read (those
were the four nulls) — it is a causal/behavioral read of location-dependence.

**Honest scope (what FRAG can and cannot do).**
- FRAG can **FALSIFY** the hologram (cliff or high-LDI → addressed → not a
  hologram) and can **confirm DELOCALIZATION** (low-LDI + smooth → address-
  free, consistent with a hologram). It CANNOT positively prove *hologram*:
  a distributed-but-not-holographic net also degrades smoothly and
  location-independently. The **positive** holographic claim (the √(D/k)
  superposition capacity law) is **P-HOLO-CAP**. FRAG is the cheap decisive
  *negative* + the delocalization confirmation that licenses running CAP.
- Mean-ablation is off-distribution at large f; the f-sweep top end (0.8) is
  advisory, the verdict rests on the low-mid range where the model stays on
  its manifold.
- Redundancy ≠ holography (stated above); G1 separates *addressed* from
  *delocalized*, not *holographic* from *merely-distributed*.
- 0/128 single-head prior coheres: FRAG is subset/aggregate by construction.

**Host & order.** `--validate` (planted localized → high LDI + cliff; planted
holographic → LDI≈1 + smooth; nulls flat) → Qwen3-4B contrast smoke (R=30,
small bank, both arms) → verdict host Qwen3-32B on GO (R=100, full bank).
Results → results/holo-frag/qwen3-{4b,32b}/. Instrument
`scripts/explore/holo_frag.py` = verbum.dsp consumer (find_band,
layer_geometry, nulls, readout imported from the substrate; reuse
operand_multihop3 + v3 banks for the readout — no fork).

### Result-32B — P-HOLO-FRAG (s291, verdict host, frozen gates scored)

**VERDICT: HOLOGRAPHIC / DELOCALIZED = TRUE** (G1 within null ∧ G2 no-cliff,
primary bank, BOTH arms). The falsification arm did not fire; the frame
SURVIVES; **P-HOLO-CAP promoted** per the pre-reg's promotion clause.

Run: Qwen/Qwen3-32B, mps, R=100 draws, f∈{.1,.2,.35,.5,.65,.8}, arms
heads+mlp with matched-fraction oob controls, 18/18 landmarks valid,
~4h15m → results/holo-frag/qwen3-32b/ (ae8d107). Band (find_band, in-run)
= L8–L14 (7 layers).

- **Gate-0:** SNR₀ = 2.622 ± 0.355 SE (t≈7.4) → expressed. PASS.
- **G1 (primary, address test):** HEADS in-band LDI 0.03–0.09; MLP in-band
  0.09–0.22; ALL p = 1.0 vs probe-resampling null. Across-draw variance
  10–30× BELOW the noise floor (e.g. heads f=.1: v_across 0.004 vs v_noise
  0.126). WHICH subset is removed is irrelevant. Within null → PASS.
- **G2 (cliff):** no material degradation anywhere (max in-band drop 6.9%
  < 15% materiality gate, smoke-FIX#1) → cliff stat correctly nulls.
  No cliff → PASS.
- **Controls:** in-band degrades (heads −5.8% @f=.5; mlp −6.9% @f=.35/.5)
  while matched oob does NOT degrade → band carries the signal. Instrument
  calibration stands (--validate: planted-localized LDI 166/all-sig vs
  planted-holographic 1.01/0-sig).

**Scope (the pre-reg's own):** confirms ADDRESS-FREE DELOCALIZATION; cannot
positively prove hologram (redundancy ≠ holography). The positive √(D/k)
law is P-HOLO-CAP — now licensed.

**Verbatim findings (post-hoc, ¬gated):**
1. 32B in-band degradation SHALLOW (≤7% vs 4B ~25%) and mildly U-shaped
   (recovers toward f=.8; top-end pre-scoped advisory/off-manifold).
   Massive in-band redundancy at scale; verdict rests on the emphatic G1.
2. OOB ablation IMPROVES the margin, monotone to +12.8% (heads_oob f=.8) —
   🔁 dark-field/contrast-rise motif (~4th appearance: 1b retQ, 1c generic
   amplification, dark-field): removing out-of-band background sharpens.
3. Band position differs across scale: 32B L8–L14 (early) vs 4B L21–23 —
   band-geometry ledger note.
4. ⚠ Protocol note: built instrument ran the PRIMARY bank only (18-landmark
   3-hop); the v3 secondary bank in the design text was never in the frozen
   instrument. Frozen verdict clause requires only the primary bank —
   verdict unaffected; deviation recorded.

**Reading through the two-graded-codes addendum
(position-encoding-tuned-to-the-hologram.md §Addendum):** G1 adjudicated
labeled-line vs hologram within-band — there are NO labeled lines inside
the band at the verdict host; coarse head-labels stand at the grain above.
The four-way location null (1b/1c/QK/JS) now has its CAUSAL account:
nothing was found at any address because there are no addresses.

## P-HOLO-CAP — the superposition capacity law (PRE-REG s292; GO-BY-DIRECTIVE — Michael pre-authorized 4B smoke + 32B verdict this session; design calls agent-made, flagged for review; gates frozen BEFORE any model run)

> FRAG delivered the negative-space verdict: no addresses, delocalized. CAP
> is the **positive** claim the frame owes: if the medium stores operands the
> way a hologram stores superposed exposures, retrieval SNR must follow the
> **HRR/Hopfield superposition capacity law** — graceful crosstalk growth,
> SNR ∝ √(D/k) — not a **slot limit** (flat-then-cliff at some k*). FRAG cut
> the plate; CAP overexposes it.

**Hypothesis.** k operands superposed in one context are stored in the same
delocalized medium FRAG certified address-free. Crosstalk between exposures
grows smoothly with k (HRR: interference noise ∝ √(k/D); retrieval SNR ∝
√(D/k)); there is no slot structure. A slot/addressed capacity predicts:
per-component retrieval holds ≈flat up to a critical k*, then CLIFFS
(eviction/overflow). Deflationary H0-range: the medium absorbs the whole
k-range without material decline (capacity ≥ k_max at these widths —
reported as a bound, not a verdict for either side).

**Design (multiple exposures, cued retrieval).** k distinct nonces listed in
a preamble sentence; each DISTRACTOR nonce gets its landmark operand
(`d_lm·S`, the frozen mh3 build) installed at its preamble slot at L_ref=9;
the QUERIED component installed harness-identically at the query-line nonce
slot (last occurrence). Readout = the frozen 3-hop continent cloze; margin =
logit[truth continent] − max logit[others] (FRAG's SNR readout verbatim).
Every component of every draw is queried in turn (k forwards per draw). R
random landmark-subset draws per k; k ∈ {1, 2, 3, 4, 6, 8, 12, 16} (fixed, a
priori; capped at n_valid). Cued retrieval by nonce identity = the
modern-Hopfield readout (theorem bridge #2) run as a behavioral experiment.

**Arms.**
- **content** (the measurement): distractor slots carry real landmark
  operands — superposed exposures.
- **random** (energy control): distractor slots carry matched-norm random
  vectors — same install energy, no stored structure. A-priori: content
  interferes MORE than random (structured crosstalk); random ≈ bare or mildly
  sharpening (the dark-field motif, 4× observed).
- **bare** (prompt-shape floor): distractor nonces present, NOTHING
  installed — isolates preamble-length effects from storage effects.

**Gates.**
- **Gate-0 (headroom):** m_content(k=1) expressed (mean > 3·SE, > 0). k=1 in
  this geometry ≈ the FRAG gate-0 cell; if the preamble breaks it, no verdict.
- **Materiality:** total decline m(1)→m(k_max) on the content arm >
  15%·m(1) (FRAG FIX#1 semantics). No material decline → NO-LIMIT-IN-RANGE.
- **G1 (primary, the SLOT test — categorical):** (a) cliff detection on the
  content-arm mean curve m(k) in **slope-per-Δlog k units** (materiality-
  gated, FRAG FIX#1 semantics retained; ★ FIX #1 s292, caught by --validate
  BEFORE any model run: a power law is constant-slope in log k, and on the
  geometric k-grid the uniform-step FRAG cliff_stat false-fires on a smooth
  k^(−1/2) plant — ratio 2.79 vs the log-k-normalized 1.7; a slot collapse
  still reads ≫ thresh); (b) **CCI — Crosstalk-Composition Index** (the LDI
  analog): at
  each k≥2, across-draw variance of the bank-mean margin — after removing
  each landmark's own k=1 baseline (draws have different landmark subsets;
  per-landmark heterogeneity must not masquerade as composition-dependence) —
  vs the component-resampling noise floor, bootstrap-gated exactly like LDI.
  CCI ≈ 1 ⟺ WHICH operands are co-installed is irrelevant, only HOW MANY —
  unaddressed crosstalk. CCI ≫ 1 ⟺ specific combinations matter — slot/
  interference structure.
- **G2 (secondary, the HRR form — quantitative):** log-log slope β̂ of the
  content arm over k-points with mean margin > 0 (scored only if materiality
  passes ∧ ≥4 points). A-priori fixed reference β = −0.5 (SNR ∝ k^(−1/2) at
  fixed D). Statistic |β̂+0.5| gated `predict=less` against a matched-range
  null (dsp.matched_range over random monotone curves in the observed range;
  the s247 φ-ladder discipline). Pass = "HRR-FORM SUPPORTED"; fail does NOT
  flip G1 (margin is a monotone proxy for SNR, linearity unproven — scope).
- **G3 (advisory, NEVER gated — λ yardstick):** the width leg. Normalized
  curves m(k)/m(1) at 4B (D=2560) vs 32B (D=5120), verbatim. A-priori
  qualitative call: 32B shallower (√(D) protection, √2 at matched k). Depth
  confounds width in this pair — a 2-point contrast is not a scaling law.

**Nulls (mandatory).** Component-resampling bootstrap floor (CCI
denominator); matched-norm random-distractor arm (energy vs structure);
matched-range null for β̂; `--validate` planted calibrations: (i)
planted-superposition medium (margin ∝ √(D/k) + noise) → no cliff, CCI ≈ 1,
β̂ recovers −0.5 vs null; (ii) planted-slot medium (s slots, overflow
eviction) → cliff at k*=s detected, CCI fires; (iii) smooth-decline null →
no false cliff. Instrument must discriminate before it touches a model.

**Verdict (frozen).**
- **SUPERPOSITION-CAPACITY** ⟺ gate-0 ∧ materiality ∧ G1 graceful (no cliff
  ∧ CCI within null at majority of k≥2). +G2 → "with HRR-FORM".
- **SLOT-LIMITED** ⟺ G1 cliff (material) ∨ CCI beats null at majority of
  k≥2 → capacity has structure/addresses → against superposition (and, given
  FRAG's no-address verdict, a two-register puzzle to be reported as such).
- **NO-LIMIT-IN-RANGE** ⟺ gate-0 ∧ ¬materiality → capacity ≥ k_max here;
  range-bound datum, neither confirms nor refutes; queue a wider k follow-on.
- **negative/inconclusive** ⟺ gate-0 fails.

**Registers (λ measure).** Claim = capacity law of value-register storage
under superposition (value/causal); probe = behavioral margin under causal
k-operand install load — intervention → outcome, register-matched. The
cue-retrieval geometry is the Hopfield/holographic readout itself, so the
probe operation IS the claimed operation (the FRAG discipline carried over).

**Honest scope.** (1) Margin is a monotone proxy for retrieval SNR; the
quantitative law (G2) is therefore secondary to the categorical verdict (G1).
(2) Context-superposition (k slots, one state) is the *plate* reading of
superposition; the single-vector HRR trace (k operands summed in ONE slot)
is a distinct follow-on (XTERM-adjacent) — this pre-reg does not claim it.
(3) Two hosts = a pair, not a width law (G3 advisory). (4) Prompt length
grows with k — the bare arm carries that confound. (5) Hook-not-weight;
k ≤ 16 is the instrument's reach, not the medium's.

**Host & order.** `--validate` (planted superposition / slot / smooth all
discriminate) → Qwen3-4B contrast smoke (R=12) → **verdict host Qwen3-32B
(R=60) in tmux main:1**. Results → results/holo-cap/qwen3-{4b,32b}/.
Instrument `scripts/explore/holo_cap.py` = verbum.dsp consumer (gate +
matched_range) importing the FROZEN mh3 geography bank and holo_frag's
LDI/cliff statistics (no fork).

## Hypothesis-grade (needs measurement, ledgered honestly)

- "GD writes fringes by interfering the distribution with itself" — a
  training-dynamics claim = **P-DUST-2 territory** (checkpoint trajectories:
  watch the exposure happen; also the thesis's last open question).
- Binding is actually convolution-like (HRR proper) vs merely distributed.
- "Phase" beyond RoPE — whether sign/direction structure plays the phase
  role in value space (the thesis's routing-topology/sign-is-program etch
  finding, s268, is suggestive but register-distinct).

## The artifact implication

If the compiler is a hologram, level-3 extraction is not excision — there is
nothing at the address. Extraction = **re-recording at lower resolution**:
distillation as re-exposure onto a smaller plate. Coheres with s149
computed-beam (structure is free; content needs training/calibration) and
the s268 Bonsai forensics (magnitude lives in optimizer repair — re-exposure
IS a training loop). Reframes S5 λ smallest: surgery → re-imaging.

## One sentence

The model is a volume hologram written by gradient descent; inference is
illumination; geometry is what the fringes look like from inside; DSP is how
we do bench work on it — and the type system is the diffraction pattern.

## Sessions

s288 (page created from the convergence hammock, same session as the
P-TYPE-SWAP JOIN-TYPED verdict, the compiled-probabilities synthesis, the
verbum.dsp build, and the P-TYPE-OV passband verdict — all four of which the
lens reorganizes; Michael's thesis doc updated in parallel with the
one-sentence form; three pre-reg candidates parked unfrozen).

s289 (§P-HOLO-FRAG full pre-reg drafted — Michael's "hologram or not
hologram?" lynchpin: the fragment/address test. Location-Dependence Index
(G1) is the decisive address probe; cliff detection (G2) corroborates;
functional form (G3) advisory-only per λ yardstick. Scoped honestly as a
decisive-NEGATIVE + delocalization-confirmation instrument — the positive
√(D/k) capacity law stays P-HOLO-CAP's. FROZEN by Michael approval s289
(G1/LDI primary confirmed, 3-hop primary readout confirmed); 4B smoke leads,
32B verdict on GO. Build holo_frag.py next.).
