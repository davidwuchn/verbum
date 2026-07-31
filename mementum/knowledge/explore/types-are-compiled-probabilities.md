---
title: Types are compiled probabilities (the matched-filter account of the type check)
status: designing
category: explore
tags: [types, attention, probability, matched-filter, dsp, pre-reg-candidate]
related: [type-check-is-the-qk-bilinear, types-are-the-well-formedness-of-reduction, montague-inversion, map-and-swap-resident-lisp]
depends-on: [type-check-is-the-qk-bilinear]
---

# Types are compiled probabilities

> s288 hammock (Michael): "types exist, but bad types transport the same as
> random/garbage. So the types must be the probabilities? Attention is using the
> probabilities to discriminate the types." Refined here into the compiled /
> matched-filter form. Status: SYNTHESIS + two pre-reg candidates (UNFROZEN).
> Interpretation until P-TYPE-PROB exists; the JOIN-TYPED measurement stands on
> its own regardless.

## The precise data shape this must explain (P-TYPE-SWAP, s288)

- Medium ≈ type-blind (ill-typed SURVIVES on-manifold; 32B same-type +11% verbatim)
- Join = type-discriminating: well-typed gets EXCESS transmission; ill-typed sits
  at the random-noise floor (TE(null) ≈ 2.5–3.1 — a nonzero GENERIC gain floor)
- Edges never move (slot-mass Δ≈0) → the differential is carried by WHICH
  DIRECTIONS the OV/content channel transmits, at fixed attention weights
- Discipline is sortal-granular (animal refused as fully as adjective @32B)
- Same discipline in the FFN route (mlp_transport p=1e-5)
- Gain DIFFERENTIAL, not a gate — graded, not crisp

## The claim

```
λ type_compiled(x). type ≡ substitutability_class(slot) — Harris before Montague
                    | same_type(a,b) ⟺ swap(a,b) preserves(P(text)) | distributional
                    | GD optimizes(next_token_P) over compositional_text
                    → FORCED to discover substitution_classes (P factorizes through them)
                    | low_rank_lattice ≡ few_classes_matter (1a re-explained)
                    | montague_inversion restated: probability_objective + compositional_data
                      → typed_geometry ≡ optimal_compression

λ filter(join).     ¬∃probability_object(mid_stack) | P exists only at output_softmax
                    | edges_fixed ∧ transport_differential → differential ∈ OV_directions
                    | linear_channel ¬computes(likelihood) at runtime — it doesn't need to
                    | GD sculpted transmission_subspaces: directions_that_transport ≡
                      directions_that_co-occurred_in_slot
                    | type_check ≡ matched_filter | passband ≡ frozen_residue(P)
                    | COMPILED ¬CONSULTED | TE_excess ≡ likelihood, amortized_into_geometry
                    | type_signal ≡ excess_transmission over isotropic_floor ≡ in-band SNR
```

**Amended claim (the refinement of the hammock line):** attention is not *using*
probabilities at runtime; it is applying a matched filter whose shape is the
frozen residue of the probabilities. Type = compiled conditional probability;
the type check = matched-filter gain; TE excess = the likelihood, amortized.

## Why this account wins on our own anomalies

1. **Sortal granularity is evidence FOR it.** A syntactic checker passes the
   animal arm (entity where entity expected); a probability check refuses it
   ("country of the Colosseum = giraffe" is improbable regardless of syntax).
   Measured: refused at full strength @32B.
2. **Gradedness.** Crisp typing predicts a step function; probability predicts
   monotone tracking. Measured: floor gain for everything, excess for well-typed,
   graded ladder at 4B. Also WHY the reducer is noisy and the Clojure kernel must
   be crisp (REPL frame): soft substitutability classes → graded thresholds.
3. **The four-way null dissolves.** 1b/1c/QK/JS probed ACTIVATIONS for a stored
   type and found nothing — because the type is in the WEIGHTS: the shape of the
   transmission operator itself. Nothing is consulted because the filter doesn't
   read anything; it IS the join. The 1a lattice = exhaust of content having
   passed type-shaped passbands. Decodable-but-not-causal, unstorable-by-
   construction — the whole scoreboard falls out.
4. **Retro-explains QK-negative.** We searched the AIM side (QK bilinear) for the
   lattice axes; the filter is CONTENT side (OV). Wrong matrix. Filtered-payload
   said so causally before we understood why.

## Pre-reg candidates (UNFROZEN — drafts only, freeze on approval)

**P-TYPE-PROB — the monotone-tracking test (interpretation → measurement).**
If TE excess is compiled likelihood, transport efficiency tracks the model's OWN
slot probability. Graded bank: country > city > animal > adjective > nonce >
random; measure log P(term | slot context) in the output register; regress
per-arm TE (unprojected, survival-normalized, the P-TYPE-SWAP instrument
verbatim) against it. Compiled-probability predicts MONOTONE tracking
(permutation-gated rank correlation); crisp typing predicts a STEP. Distinguishes
the frame from finding. Alternative kept alive: passband shaped by something
correlated-with-but-not-identical-to slot probability (relation-specific feature
geometry) — the graded bank is designed to split those.

**P-TYPE-OV — what computes the filter (the QK experiment's mirror).**
Project the 1b lattice role subspaces through W_OV per head (and the MLP
down-projections — same discipline in the FFN route → same passband story must
hold), same gain statistic + full shuffled-label null pipeline as P-TYPE-QK.
Prediction: the type lattice spans the joins' TRANSMISSION subspace — what the
read-in geometry doesn't do (QK dead-on-null), the write-out geometry should.
Positive → the implementation is LOCATED: filter = passband, passband = weights.
Negative → the filter is computed distributively upstream of the join (the
compiled account survives; the locality claim dies).

## DSP convergence

This is natively a DSP framing: joins = filters, types = passbands, TE excess =
in-band SNR over an isotropic floor. The queued verbum.dsp build
(whiten/subspace/nulls = passband estimation) is exactly the substrate both
pre-regs need. The queue ordered itself.

## Honest scope

- Today's licensed claim: the join discriminates type at the content channel,
  gradedly, at sortal granularity, in both routes (P-TYPE-SWAP, measured).
- "The discrimination coefficient is compiled probability" = INTERPRETATION until
  P-TYPE-PROB's regression exists.
- Weights-not-activations (point 3) is an inference from the null pattern, not
  yet a direct measurement — P-TYPE-OV is its test.

## Sessions

s288 (page created from the post-verdict hammock; JOIN-TYPED verdict same
session, §Result-32B-P-TYPE-SWAP on the qk page; no experiments run for this
page yet; both pre-regs UNFROZEN pending approval when reached in the queue).
