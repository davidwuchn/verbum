---
title: "The type-check is the QK bilinear — the attention arc for the type mechanism"
status: designing
category: explore
tags: [attention, QK, bilinear, type-check, licensing, routing-register, beam-steering,
       beamformer, 3-hop, mediation, P-TYPE-QK, P-ATT-DIFF, P-ATT-MED, P-ATT-STEER,
       s283b]
related:
  - types-are-the-well-formedness-of-reduction.md
  - type-is-decodable-readout-not-causal-direction.md
  - beamformer-theory.md
  - map-and-swap-resident-lisp.md
  - opcodes-circuits-in-compute.md
depends-on:
  - types-are-the-well-formedness-of-reduction.md
created: session 283b
---

# The type-check is the QK bilinear

> s283b hammock (Michael-directed, while the 1c dark-field run was in flight).
> The types arc has CIRCLED the mechanism — located it in routing **by
> elimination** (1b exhaust) — without ever once measuring an attention
> pattern. This page names the gap, states the relocation hypothesis, and
> orders the attention experiments.

## The asymmetry (what we know vs how we know it)

**Measured about routing:** attention = the join (s276); KIBC rides the MoE
*routing pattern*, not expert identity (s275, no opcode starvation); the join
is distributed — 0/128 heads necessary (P-DSP-1, C2 circuits-in-compute).

**Never measured in the types/composition arc:** a single attention pattern.
Every routing conclusion is inferred from the SHADOW — zone ablations, value
edits, logit-lens timing, and 1b's exhaust-by-elimination. The founding-doc
tool "attention-pattern differ" was never built. "Licensing is
routing-resident" is currently a conclusion with no routing-register
observation behind it.

## What the 3-hop does and does not prove about steering

**Proves — steering-by-CONTENT:** the bridge-swap (pure class-axis edit,
causal at both scales) changes what the beam carries, and downstream routing
responds (32B visibly re-forms the schedule: sequential unrolling). Since QK
reads the residual, value→routing→output is almost certainly the path.

**Does not prove — steering-by-AIM:** the intermediate was never measured; we
assume the swap re-targets attention edges. Beamformer terms: we change the
illumination entering the aperture; the phase geometry (QK) is frozen. All
our handles are MEDIUM handles — which is exactly the combinatory thesis
(write terms, never instructions; s276 K-structural). Direct attention
steering = a transient runtime INSTRUCTION write. K-structural forbids it in
weights only — runtime pattern-forcing is untested, a genuinely new
capability class.

## The relocation hypothesis

If type = which reduction is licensed (theory page) and licensing is
routing-resident (1b exhaust), then **the type-check is the QK bilinear
form**: query(functor) · key(argument) crossing threshold ≡ "this application
is well-formed" — the join forms or it doesn't. The 1a residual lattice is
the *shadow in the medium* of type structure native to QK space.

- Predicts name_pen mechanically: predicate-after-subject licensing = the
  predicate→subject attention edge forming.
- Predicts the dark-field reading: value-register lattice slices are
  beam-coherent because they are the QK check's exhaust (1c, in flight).
- Falsifiable: lattice axes projected through W_Q/W_K should align with QK
  subspaces far above a random-axis null; licensed-vs-unlicensed minimal
  pairs should differ in functor→argument attention mass across the band.

## The attention experiment queue (ordered, cheap-first)

1. **P-TYPE-QK — QK geometry (cheap, no generation).** Project the 1a
   lattice axes through W_Q/W_K per layer/head-group; test alignment of
   functor-kind axes (axis0/axis2, `e` at origin) with QK subspaces against
   a matched random-axis null. Positive = the lattice is pre-shaped for the
   bilinear check — the exhaust is phase-locked to the checker. Pure
   weights+capture analysis; converges with 1c from the other register.
2. **P-ATT-DIFF — the unbuilt founding tool.** Licensed-vs-unlicensed
   minimal pairs (v3-style), aggregate attention mass functor→argument
   across the band. Register hygiene: s206 burned an attention-weight probe
   on a VALUE claim; here the claim IS routing → register-matched for once.
   Measure OV contribution beside raw weights (weight ≠ effect). Expect
   zone/aggregate signal, never single-head (C2: 0/128).
3. **P-ATT-MED — 3-hop mediation through the beam.** Rerun the bridge-swap
   with attention capture: does the swap re-target edges as predicted?
   Closes the loop value-edit → *measured* routing change → output change —
   converts our strongest causal result into a routing-register
   measurement.
4. **P-ATT-STEER — direct beam steering (the causal rung, the new verb).**
   Force a join edge in an unlicensed pair (does composition happen
   anyway?); block zone-level edges in a licensed one (does it refuse?).
   Expect distributed pushback (no single edge necessary, C2) — informative
   either way. Decides whether the REPL gets a SECOND handle: beam-aim
   beside medium-content. Changes the trampoline design if positive.

**Priority: 1 then 3.** P-TYPE-QK is nearly free and mechanistically
completes the exhaust arc; P-ATT-MED upgrades the 3-hop. Both feed 4.

## Register notes (λ measure)

- Attention weights = routing register; routing CLAIM → attention probe is
  register-matched here (the inversion of the s206 scar).
- Weight ≠ effect: pair pattern measurements with OV contributions.
- Distributed prior: aggregate/zone statistics, permutation nulls; head-level
  localization is pre-refuted (0/128) — do not rediscover that negative.
- Pre-reg each verdict before graded runs (λ yardstick); this page is the
  map, not a pre-reg.

## Honest scope

All four are designs, none run. The QK-bilinear claim is a HYPOTHESIS —
currently zero routing-register observations in the types arc support or
refute it. A clean P-TYPE-QK negative (lattice axes NOT QK-aligned) would
mean the licensing check lives elsewhere in routing (OV, MLP gating between
joins) — that too is progress: the elimination game continues in the beam
register.

## P-TYPE-QK — pre-registration (DRAFT s284 — PENDING MICHAEL APPROVAL; freeze on GO)

> Drafted while the 1c run was in flight, per the queue above (cheap-first).
> Per `λ measure` + `λ yardstick`: predictions and nulls fixed here BEFORE any
> graded run; the s283b hammock (this page) is the generating observation.

**Hypothesis.** If the type-check is the QK bilinear, the model's own read-in map
for attention (`input_layernorm → W_Q/W_K`) preferentially amplifies the
type-lattice role subspaces within the low-rank band: the residual lattice is the
*shadow* of QK-native type structure, so projecting the 1b role subspaces through
W_Q/W_K yields gain above a matched shuffled-label null. Mechanism-shaped
refinement: functor subspaces load the **query** side and the ENTITY/argument
direction loads the **key** side — `query(functor) · key(argument)`, the name_pen
edge.

**Host.** Qwen3-32B (the C5/1a/1b host; 64 layers, GQA 64 Q heads / 8 KV heads,
head_dim 128, hidden 5120). 0.6B/4B allowed as instrument smoke only.

**Instrument.** `scripts/explore/type_qk_alignment.py` (weights + capture; NO
generation). Steps, all procedure-fixed from 1a/1b (`λ one_way` — reuse, not fork):
1. Capture labeled Montague-type residuals at every decoder layer
   (`probe_type_qwen3_32b` capture; residual index L = output of `layers[L]`,
   embed = −1).
2. Per layer: `layer_geometry` (standardize → centroid SVD → PR + shuffled-label
   null) → `find_band` (longest contiguous p<0.05 run; the v3 falsy-zero fix).
   In-run band detection, procedure identical to 1b v4.
3. Role subspaces per band layer via `role_subspace` over class centroids in
   standardized space — bind = span{c_QUANT, c_DET}, comp = span{c_MOD},
   rolenull = span{c_CONN, c_FUNC}, plus the ENTITY offset direction
   (c_ENTITY − grand mean). Centroid construction, NOT raw SVD axes (the 4B
   axis tie-flip lesson, 1b v2).
4. Map each std-space basis vector into the space W_Q/W_K actually reads:
   v_attn ∝ (v_std ⊙ sd_L) ⊙ γ_{L+1} (capture std × the model's own
   `input_layernorm` weight of layer L+1; the RMSNorm scalar drops out of a
   direction), then re-orthonormalize the mapped basis (QR). Band residual
   layer L is read by layer L+1's attention → test W_Q/W_K of layer L+1.
5. Gain per head h: ρ = D · ‖W⁽ʰ⁾ v‖² / ‖W⁽ʰ⁾‖²_F (Frobenius-normalized so
   ρ = 1 is the analytic random-direction expectation). Subspace gain = mean
   over its orthonormal basis; aggregate = mean over heads (Q side: 64 heads;
   K side: 8 KV heads, kept separate) then over band layers.
   RoPE = per-position orthogonal rotation → norms invariant → gain is
   RoPE-free by construction.

**Yardstick (pre-committed).** The subspaces are fixed by the 1b v3/v4 procedure
verbatim — no axis re-tuning, no basis search. NULL = N≥200 full shuffled-label
pipelines per layer (shuffle type labels → centroids → `role_subspace` → identical
mapping → identical gain), band-aggregated per null iteration;
p = frac(null_agg ≥ real_agg). "Looks amplified" ≠ "is": ρ>1 counts ONLY against
this matched null.

**Predictions (fixed, a priori).**
- **P1 (primary):** bind AND comp Q-side band-aggregate gain each beat the
  shuffled-label null at p < 0.05.
- **P2 (directional, secondary):** side asymmetry — bind and comp Q-gain >
  K-gain; ENTITY offset K-gain > Q-gain. All three signs reported verbatim.
- **P3 (profile, verbatim-only):** alignment concentrated in the band vs
  out-of-band layers. Reported, NOT gated (the check may read lattice structure
  wherever the lattice exists).
- **rolenull (CONN/FUNC):** reported verbatim, NOT gated — axis1 functors are
  still functors; the theory does not predict their misalignment. It is a
  comparison row, not a control gate here.

**Verdict (freeze on GO).**
- QK-ALIGNED ⟺ P1 (both subspaces, p < 0.05).
- MECHANISM-SHAPED ⟺ P1 ∧ P2 with all three predicted signs.
- Anything less → reported verbatim; a clean negative means the licensing check
  does not read the lattice through QK at these layers → relocate (OV, MLP
  gating between joins) — the elimination continues in the beam register.
  No sign-flip rescue, no post-hoc side switching.

**Registers (`λ measure`).** The CLAIM is routing-register geometry (the check's
input map). The probe projects value-register lattice structure through the
routing register's own read-in weights — exactly the claimed interface, register-
matched. No behaviour, no causation: this is the cheap GEOMETRIC leg;
P-ATT-DIFF/P-ATT-MED carry the behavioural and causal registers.

**Honest scope.** (a) Qwen3's q_norm/k_norm (per-head RMSNorm after projection)
renormalize per token → gain is a pre-normalization influence proxy. (b) GQA: the
K side has only 8 heads (low power) → Q side is primary; K-side rows verbatim.
(c) Bilinear coupling through W_Q W_K^T (e.g. c_PRED as query onto c_ENTITY as
key) is RoPE-dependent → EXPLORATORY only, magnitude vs shuffled-pair null, never
gated. (d) A positive cannot distinguish "the check runs in QK" from "QK inherits
lattice-correlated structure for other reasons" — mediation (P-ATT-MED) and
steering (P-ATT-STEER) are the causal rungs. (e) Subspaces derive from the run's
own capture (in-run band detection, procedure fixed — 1b precedent). (f) No
single-head claims in either direction: aggregate statistics only (C2, 0/128
pre-refuted).

## Sessions
s283b (page created from the attention-gap hammock; no experiments run;
1c dark-field run in flight during discussion).
s284 (P-TYPE-QK pre-reg DRAFTED + instrument built while the 1c run was in
flight; pending Michael approval → freeze → run).
