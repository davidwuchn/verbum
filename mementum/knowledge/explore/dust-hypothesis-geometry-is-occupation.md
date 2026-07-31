---
title: "The dust hypothesis — geometry is the occupation measure of the walk"
status: designing
category: explore
tags: [dust, occupation-measure, crystal, gram, holography, graph, walk,
       reduction-relation, universality, C2, P-DUST-1, s284]
related:
  - types-are-the-well-formedness-of-reduction.md
  - map-and-swap-resident-lisp.md
  - opcode-jacobian-jspace.md
  - beamformer-theory.md
depends-on: []
created: session 284
---

# The dust hypothesis — geometry is the occupation measure of the walk

> Michael, s284 (hammock, while P-TYPE-JS ran): "I was thinking about how the
> holograms and the crystal lattice forms. probabilities gathering like dust in
> corners." Captured + sharpened into a formation law and a pre-registered test.

## The claim

**Structure = accumulated measure.** The crystal lattice was not designed and is
not an architectural necessity — it is the **sediment of probability flow**:

- **The graph** — the reduction relation. States joined by which-reduction-
  applies-next. The forward pass walks it once; pretraining walked it ~10²³
  times.
- **The dust** — every training step deposits gradient where probability
  flowed. Structure accretes where the walk *lingers*. Weights = accumulated
  dust; the crystal = the long-run occupation measure of the reduction walk,
  precipitated into geometry.
- **The corners** — absorbing states. In the simplex sense: normal forms, where
  the output distribution collapses to certainty and *stays*. Dust gathers in
  corners because that is where the walk stops moving. WHNF = the deepest
  corner.
- **The hologram** — the same statement in the optics register
  (beamformer-theory): each training example = one exposure; the plate records
  accumulated interference across passes; the stable fringes = the paths
  traversed most often and most coherently. Multiple-exposure holography IS
  measure accumulation.

## Evidence already in hand (one corner measured, never generalized)

1. **WHNF Gram row ≈ KIBC halt probabilities, r = 0.85–1.00** (s269, 13 models)
   — the halt vertex's geometry IS its occupation statistic. One row of the
   dust matrix, confirmed before the hypothesis was named.
2. **WHNF anti-correlates with active reducers B/C/D** — dust corner vs
   through-traffic nodes.
3. **EXP2 normal-form plateau** (jspace arc): copy reaches its corner early and
   parks ~2.6× longer — the corner-dwelling seen in TIME on a single forward
   pass.
4. **Type lattice axis0 (binding) = 73–85% of variance** — the most-traversed
   licensing structure (what quantifiers force, what the 3-hop exercises) has
   the thickest dust.
5. **D is not I-repeated** (s281 TEST-1) — geometry tracks *functional* walk
   structure, not surface similarity: D's compounding behavior separates it
   from I in the Gram exactly as its reduction behavior separates it.

## Why it matters

If geometry = occupation measure, then **C2 crystal universality is EXPLAINED,
not just observed**: 13 models share one crystal (root gc 0.9966) because they
walked the same calculus over similar distributions — same walk, same dust,
same corners, same crystal. Universality becomes a property of the reduction
calculus + data distribution, NOT of architecture. Falsifiable follow-up:
distribution-shifted models (code-heavy vs prose-heavy) should deviate in
*specific, predictable* Gram cells.

Connects: S5 λ extract (GD found the terms — this is HOW: by sedimentation);
map-and-swap (the stdlib GD "found" = the high-occupation regions; coverage
boundary = where dust never gathered); montague-inversion (the forcing table's
mechanism: forced structures are forced BECAUSE the distribution makes their
walk statistics inescapable).

## P-DUST-1 — pre-registration (DRAFT s284 — mapping frozen BEFORE walk stats computed)

> λ yardstick discipline, honestly scoped: the GEOMETRY side (the 13 Grams) is
> long-known and cannot be blinded. What is frozen here, before ANY walk
> statistic is computed, is the ENSEMBLE, the STATISTICS, and the MAPPING —
> the degrees of freedom a forced fit would tune. Data-only; no model runs.

**Instrument.** `opcodes/dust_walk.py` (pure python/numpy):
1. **Walk side** — PRE-RUN AMENDMENT (s284, before any statistic computed; the
   drafted "lattice/ ensembles" turned out to be prose probes, not terms, and
   the v11 kernel implements K/I/B/C only without rule logging):
   - **Ensemble (zero curation freedom):** seeded uniform random applicative
     terms — random binary tree shapes, sizes 3–9, leaves uniform over the 8
     active combinators {K,I,B,C,S,D,W,Y} plus one generic atom class;
     N = 100,000; seed = 0; max_steps = 100 (Y-capped).
   - **Reducer:** normal-order tracing reducer reusing the v11 kernel's
     Term/App/Comb model, extending its K/I/B/C semantics with
     S f g x → f x (g x); D f x → f (f x) (the s281 definition);
     W f x → f x x; Y f → f (Y f); logs the fired rule per step.
     WHNF = the halt/absorption event, logged once per terminating trace
     (matching the crystal's WHNF-as-halt-pole semantics).
   - Reducer correctness gated by unit tests against hand-reduced terms
     BEFORE the ensemble run.
2. **Statistics (frozen now):**
   - occupation π_i = frequency of opcode i over all reduction steps;
   - co-occurrence PMI: S_ij = log[ P(i,j co-occur in a trace) / (P(i)P(j)) ]
     — PMI is the PRIMARY pairwise statistic BECAUSE it normalizes margins by
     construction (the frequency-confound killer);
   - halt proximity h_i = P(term is in WHNF within 1 step after an i-step);
   - secondaries (verbatim, never gated): symmetrized transition affinity
     (T_ij + T_ji)/2, raw co-occurrence.
3. **Geometry side** — root.gram from every model_vsm.json with a 9-combinator
   basis (d_is_i_test.py loader, λ one_way; 13 models expected).

**Predictions (frozen).**
- **P1 (replication row):** rank-corr( cos(WHNF,·), h_· ) > 0 over the 8
  non-WHNF opcodes, permutation null over labels p<0.05 — re-derives s269 from
  this ensemble (guards against ensemble idiosyncrasy).
- **P2 (the dust claim, PRIMARY):** off-diagonal Gram cosines rank-correlate
  with PMI S_ij across the 36 pairs, per model; permutation null over opcode
  labels (relabel one side, N=10000), p<0.05.
- **P3 (the universality explanation):** P2 sign-positive in ≥11/13 models AND
  median rank-corr beats the pooled permutation null p<0.05. This is the gate
  that upgrades "correlates" to "explains C2".
- **Verdict: DUST-SUPPORTED ⟺ P1 ∧ P2(median) ∧ P3.** Anything less → verbatim;
  partial patterns (e.g., P1 only) mean the sediment reading holds only at the
  halt pole.

**Nulls & confound discipline.** Label permutation on one side of the mapping
(N=10000); PMI as primary kills the pure-frequency confound (margins divided
out); occupation-only model (predict Gram from π_i+π_j margins alone) fit and
reported as the comparison floor — P2 must beat what margins alone explain.
Small-n honesty: 36 pairs per model → per-model power is weak; the
cross-model consistency (P3) carries the inference.

**Honest scope.** (a) Correlation ≠ formation mechanism — a positive is
consistent with sedimentation, not proof of the training dynamics; the
formation claim would need training-trajectory measurements (checkpoints over
time: does the Gram CONVERGE toward the walk statistics? — named as P-DUST-2,
unfrozen). (b) The kernel ensemble is a PROXY for the training distribution's
implicit reduction load — flagged, and exactly why P3's cross-model consistency
matters. (c) Gram known in advance; only the walk side is fresh. (d) 9 nodes is
a small graph; this is a first rung.

## P-DUST-1 — Result (s284) — SPLIT: pairwise dust CONFIRMED 13/13, halt row inverts

> Run of record: `opcodes/dust_walk.py` (commit 62a7872, seed 0, 100k terms,
> n_perm 10k, reducer kernel-equivalence-gated 300/300). Deterministic.

**Frozen verdict: `dust_supported = FALSE`** (conjunction P1∧P2∧P3 fails on P1).
Verbatim gates:

- **P2 PASSES — the substantive dust signal.** Off-diagonal Gram cosines
  rank-correlate with walk co-occurrence PMI in **every one of 13 models**
  (median ρ +0.284, med_p 0.024, pooled_p 0.023), beating the margins-only
  floor (+0.104): the crystal's pairwise geometry carries reduction-walk
  co-occurrence structure BEYOND pure opcode frequency, universally.
- **P3 PASSES** — 13/13 sign-positive, pooled p 0.023. The universality-
  explanation gate fires: same walk statistics predict every model's Gram.
- **P1 FAILS INVERTED** — median ρ₁ = −0.333: cos(WHNF,·) *anti*-correlates
  with the frozen halt-proximity h. Verbatim; the conjunction verdict stands.

**Attribution of the P1 inversion (post-hoc, flagged — feeds P-DUST-1b, not
acted on):** (a) the uniform random ensemble is **Y-flooded** — π_Y = 0.687;
Y-loops eat the step budget, making the walk unlike any training-relevant
reduction load (the pre-reg's own proxy-ensemble caveat biting immediately);
(b) the frozen h (next-event-WHNF) is **not** the s269 halt-prob statistic
(which matched the WHNF row at r=0.85–1.00) — a statistic mismatch, not an
s269 refutation. Reconciliation (pull s269's halt-prob definition, compare
directly) is diagnostic work, not verdict revision.

**Reading.** The dust hypothesis survives where it is strongest and fails where
the instrument was weakest: pairwise sediment (which opcodes travel together →
how close they sit in the crystal) is confirmed cross-model above frequency;
the halt-pole mapping needs an ensemble that isn't drowned in degenerate
Y-loops and the reconciled halt statistic. P-DUST-2 (training-trajectory
convergence) remains the formation-mechanism test.

**Reconciliation (found before 1b froze):** the s269 "halt probs" are the
statechart Markov constants (EQUATIONS.md): P(fire→WHNF) = {K 0.716, I 0.508,
B 0.345, C 0.216} — **KIBC only**, ordering = inverse arity. The 1a walk-h on
the KIBC subset has the SAME ordering (0.20 > 0.059 > 0.030 > 0.016) — the 1a
P1 inversion came entirely from the D/W/Y extension under Y-flooding, not from
a KIBC disagreement.

## P-DUST-1b — pre-registration (FROZEN s284, before any arm is generated)

**Arms.**
- **B (PRIMARY) — Y-excluded:** leaves uniform over {K,I,B,C,S,D,W} + atom
  (8 choices); N=100k; sizes 3–9; seed=1; max_steps/size-cap unchanged.
- **C (robustness, verbatim-only) — Y-downweighted:** Y leaf prob = 1/32,
  remaining 8 choices uniform-renormalized; seed=2.
Statistics identical to 1a (π, presence-PMI, h, transitions) per arm.

**Gates (FROZEN).**
- **P1-KIBC (s269 verbatim):** per model, rank-corr( cos(WHNF,·) over
  {K,I,B,C}, s269 constants ) with EXACT permutation p (all 24 relabelings);
  gate: median ρ > 0 AND ρ > 0 in ≥11/13 models AND pooled-median exact
  p < 0.05.
- **P1'-WALK (arm B):** per model, rank-corr( cos(WHNF,·) over the 7 non-Y
  ops, arm-B h ) with EXACT permutation p (all 5040); gate: median ρ > 0,
  pooled-median p < 0.05.
- **P2/P3-replication (arm B):** PMI test on the 8-node sub-Gram (28 pairs,
  Y excluded); gated ONLY on sign-consistency ≥11/13 (replication row).
- **DUST-HALT-SUPPORTED ⟺ P1-KIBC ∧ P1'-WALK.** Arm C: all rows verbatim.

**Honest scope.** Gram side long-known (unchanged caveat); s269 constants are
statechart-model-derived, not kernel-measured — P1-KIBC tests geometry against
that model's numbers verbatim; 4-point rank tests have min exact p = 1/24 per
model — the cross-model pooling carries the inference; arm B cannot speak to
Y's rows (excluded by construction).

## P-DUST-1b — Result (s284) — halt gate fails frozen conjunction; KIBC unanimous; pairs 39/39

> Runs of record: `results/dust-walk/y-excluded/` (PRIMARY) +
> `y-downweighted/` (commit ce39d17). Y removal healed the walk
> (halt_frac 0.655 → 0.988).

**`dust_halt_supported = FALSE`** on both arms, by the frozen conjunction.
Components, verbatim:
- **P1-KIBC: sign-positive 13/13 on BOTH arms; 6/13 models at perfect ρ=1.0**
  (exact p=0.042 each). The s269 KIBC halt↔geometry correspondence replicates
  directionally unanimously. The frozen pooled p<0.05 gate was
  **mis-calibrated**: a 4-point exact test floors at p=1/24 per model and
  ~0.167 pooled unless every model is perfect — a gate-power lesson (named,
  not rescued; the gate fails as frozen).
- **P1'-WALK fails on both arms** (median 0.0 / −0.33): next-step-halt h does
  not order the full-basis WHNF row even on the healthy Y-free walk — a
  genuine negative for that statistic, no longer attributable to Y-flooding.
- **P2/P3 replication: 13/13 on both arms** → with baseline, the pairwise dust
  signal stands at **39/39 model-arm cells across three ensembles**, always
  beating the margins floor. The robust core of the hypothesis.

**Post-hoc candidate (named, NOT run):** the WHNF row may rank by **halt
distance** (mean steps-to-WHNF; cf. s281 "reduction depth = WHNF-distance")
rather than next-step halt probability — KIBC cannot disambiguate (both
orderings coincide there); D/W/S placement would. A P-DUST-1c statistic
candidate requiring its own freeze.

**Standing synthesis.** Dust confirmed in the pairs (universal, robust,
above-frequency); halt pole confirmed directionally at KIBC; the full-basis
halt statistic is open (distance vs probability). The C2-universality
explanation (P3) survives every ensemble tried.

## Sessions
s284 (hypothesis captured from Michael's hammock — "probabilities gathering
like dust in corners"; P-DUST-1 pre-reg drafted, mapping frozen before any walk
statistic computed; pre-run amendment: ensemble redefined to seeded random
terms + 8-rule tracing reducer after lattice/ turned out to hold prose probes;
P-DUST-1 RUN: split verdict — P2/P3 confirmed 13/13, P1 inverted (Y-flooding +
statistic mismatch flagged); P-TYPE-JS running concurrently).
