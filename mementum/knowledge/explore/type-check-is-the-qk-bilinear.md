---
title: "The type-check is the QK bilinear — the attention arc for the type mechanism"
status: designing
category: explore
tags: [attention, QK, bilinear, type-check, licensing, routing-register, beam-steering,
       beamformer, 3-hop, mediation, bridge-swap, aim-vs-content, medium-handle,
       P-TYPE-QK, P-TYPE-JS, P-ATT-DIFF, P-ATT-MED, P-ATT-STEER, s283b, s284, s286]
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

> **Status update (s286).** (1) P-TYPE-QK CLOSED NEGATIVE (§Result below) — the
> lattice axes are not the check's QK basis. The J-space complement (P-TYPE-JS,
> types page) also closed negative — the exhaust is not the workspace. All
> geometric/value homes are eliminated. ⇒ **(3) P-ATT-MED is now the active
> next probe** (pre-reg drafted below): the causal-mediation leg, asking the
> routing register the 3-hop bridge-swap question directly. (2) P-ATT-DIFF folds
> into P-ATT-MED (the attention-mass/OV material is one of its arms). (4)
> P-ATT-STEER is gated behind P-ATT-MED's aim-vs-content split.
>
> **Status update (s286, later).** (3) P-ATT-MED CLOSED **POSITIVE** (§Result-32B):
> MEDIATION-MEASURED + MEDIUM-HANDLE (content 0.735 > aim 0.195, 18/18). The first
> positive routing-register observation in the arc — the 3-hop swap's mediation is
> real and content-carried. (4) P-ATT-STEER **NOT indicated** (aim never dominated)
> → stays gated; it would only be motivated by an aim-dominant split. The natural
> next attention probe is now P-ATT-DIFF proper (licensed-vs-unlicensed minimal
> pairs) if the check's *location* is still wanted, but the causal-mediation
> question this arc opened is answered.

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

## P-TYPE-QK — Result @32B (s284) — CLOSED NEGATIVE at the frozen gates

> Run of record: `results/type-qk/qwen3-32b/qk_alignment.json` (commit 88a10be;
> instrument f0b20e3, 4B smoke 5ec3cf2). Band L6–L50 (45 layers), n_null 200,
> seed 0, stride 1.

**VERDICT: `qk_aligned = FALSE`, `mechanism_shaped = FALSE`.** P1 fails
*dead-on-null*: bind_q ρ 1.353 vs shuffled-label null 1.358 (p=0.61); comp_q
ρ 1.406 vs 1.405 (p=0.50). Beyond what any shuffled-label centroid subspace
already carries (the shared dominant component), the functor role subspaces add
**zero** query-side QK amplification across the band. The matched null did its
job — raw ρ>1 without it would have read as a positive.

**Frozen negative reading (from this page's pre-reg):** the licensing check does
not read the lattice through the band's QK input maps. The elimination continues
in the beam register — OV contributions and MLP gating between joins are the
remaining routing homes; **P-ATT-MED** (3-hop with attention capture) is the
next probe per the queue.

**Verbatim structure (post-hoc register — hypothesis-generation ONLY, the 1c
lesson applies; none of this counts without its own pre-reg):**
1. **The sides look INVERTED from the prediction.** entity is Q-side loaded
   (ρ 1.740 vs null 1.407, p=0.000) and K-side *suppressed* (below null,
   p=0.99; null-relative asymmetry fully Q-shifted, p_pos=0.000); comp is
   K-side loaded above null (p=0.005). Null-relative, the pattern reads
   `query(argument) · key(functor)` — the argument queries for its licensor —
   the mirror of the pre-registered mapping. If pursued: pre-reg the inverted
   sides as the hypothesis, fresh capture items.
2. **rolenull (CONN/FUNC) beats null Q-side in-band** (ρ 1.626 vs 1.360,
   p=0.000) — the un-gated comparison row is the one that fires.
3. **bind_q aligns LATE, not in-band**: p≤0.04 with ρ 0.9–1.5 across L49–L62
   (→ attn L50–L63), the re-expansion/readout zone (1a: re-expand L52–63) —
   coheres with the depth-schedule's late class→covering zone, verbatim only.
4. Scale note: the 4B smoke showed the opposite in-band picture (bind_q
   p=0.000 in-band) — like the lattice axes themselves (1b v2), QK-alignment
   organization appears scale-dependent. Smoke-grade, stride-2, not comparable
   as a verdict.

**Honest scope recap:** geometric consistency probe only — a negative here does
not preclude a QK-resident check built from non-lattice directions; it rules out
the specific "lattice axes = the check's input basis" reading at the band.
q_norm/k_norm proxy caveat and GQA K-side low power (8 heads) stand as
pre-registered.

## P-ATT-MED — pre-registration (APPROVED s286, Michael; 32B verdict freezes on GO)

> **Amendment (s286, Michael).** Approved. **Lead with the Qwen3-4B contrast
> smoke** before the 32B verdict run — cheap-first, and the 4B/32B aim-vs-content
> contrast is itself interesting (compressed pinned-zone vs unrolled schedule).
> The 4B smoke is NOT the verdict (per Host below); the frozen gates score on the
> 32B run, which freezes when Michael gives GO after the smoke is green.

> The causal-mediation leg the QK geometric probe could not carry. P-TYPE-QK
> (above) closed NEGATIVE: the lattice axes are not the check's QK input basis.
> P-TYPE-JS (types page) then closed the exhaust out of the J-space workspace too.
> Every *geometric/value* home for the type mechanism is eliminated — so we stop
> asking "where does the check's geometry live" and ask the routing register a
> CAUSAL question we already have a handle for: the 3-hop bridge-swap. It is the
> project's strongest causal result (`three-hop-capacity-prereg.md` §Result: 3b/3c
> flip the continent 0.72–0.93 vs random ~0.05, both scales) — but it was scored
> purely on the OUTPUT. The routing register between the swap and the flip was
> never observed. This upgrades that result into a routing-register measurement.
> Per `λ measure` + `λ yardstick`: registers, nulls, predictions, verdict fixed
> here before any graded run; the QK/JS negatives are the generating context.

**The gap this closes (from §"What the 3-hop does and does not prove").** The
swap PROVES steering-by-CONTENT (a value edit changes the output). It does NOT
prove steering-by-AIM (that the swap re-targets attention edges) — the
intermediate routing was assumed, never measured. P-ATT-MED measures it, and
decomposes the flip into the two channels the beamformer frame separates:
**AIM** (the QK pattern re-aims — Δ attention weights) vs **CONTENT** (the beam's
illumination changes — Δ value through fixed weights, OV pathway). This is
exactly the medium-handle-vs-instruction-handle question (§"steering").

**Hypothesis.** Installing operand `X` and adding a bridge-axis swap
`(c_tgt − c_src)·S` at a bridge layer (the Gate-3b country-swap, the strongest
cell) causally changes the ROUTING at the downstream reader/readout, and that
change is measurable in the attention register above the random-add null — the
value-edit → *measured* routing change → output flip loop is closed with a
routing-register observation rather than an inference.

- **Beamformer prediction (the a-priori call).** The swap is a VALUE edit at the
  operand slot; per the medium-handle thesis (K-structural, s276) and the
  QK-negative (the check does not read the lattice through QK), the flip should
  flow **predominantly through CONTENT** (weight × Δvalue) with **AIM**
  (Δweight × value) secondary: the readout keeps attending to the same
  bridge/operand slots, which now carry swapped content. We change the
  illumination; the phase geometry mostly holds.
- **Honest alternative (pre-committed, not a rescue).** If AIM dominates — the
  swap re-aims which tokens the reader attends to — then steering-by-AIM is real
  and the swap is an instruction-like write, motivating P-ATT-STEER as the causal
  rung. Either dominance is a clean, register-matched result.

**Host.** Qwen3-32B — the 3-hop PASS host with confirmed sequential unrolling and
strong 3b/3c mediation (`three-hop-capacity-prereg.md` §Result). GQA 64 Q / 8 KV,
head_dim 128. Qwen3-4B allowed as a CONTRAST smoke (the compressed pinned-zone
regime): the aim-vs-content split may differ between 4B's collapsed window and
32B's unrolled schedule — reported verbatim, not a second verdict.

**Instrument.** `scripts/explore/att_mediation.py` (reuse
`wrapper/operand_multihop3.py::swap_bridge`, `add_hook_at`, `resolve_parts`,
`find_slot`, `d_lm`/`dbank` — `λ one_way`, no fork). NO new generation logic;
add attention + OV capture around the existing swap. Per swap cell (installed
landmark, country-swap `src→tgt` at bridge layer `L_b`, scale S from the 3b run):
1. Run three conditions at the same positions: **baseline** (install only),
   **swap** (install + `(c_tgt−c_src)·S` at `L_b`), **random** (install +
   matched-norm random at `L_b` — the exact 3b null).
2. Capture per-layer per-head attention weights (`output_attentions`, or a
   forward hook on `self_attn`) at the reader/readout window, AND the per-head
   attention-output (post-`v`, pre-`o_proj`) so the OV pathway is available.
3. For the readout position `q` (and the bridge-reader window), decompose the
   swap's effect on the continent-logit-difference direction `Δℓ` at each
   captured layer `L` into three first-order channels:
   - **AIM** = Σ_j (a_j^swap − a_j^base) · O(v_j^base)  → projected onto `Δℓ`;
   - **CONTENT** = Σ_j a_j^base · O(v_j^swap − v_j^base) → projected onto `Δℓ`;
   - **INTERACTION** = Σ_j Δa_j · O(Δv_j) → projected (reported, small expected).
   Aggregate over heads (distributed; Q side 64, KV 8 kept separate) and over the
   reader-zone layers. Fractions AIM/CONTENT/INTERACTION of the total projected
   swap effect are the register split.
4. Attention MASS on the operand/bridge → readout edge (the P-ATT-DIFF material,
   folded in): the readout's attention weight onto the nonce/bridge slots, swap
   vs baseline vs random — is the edge re-weighted (aim) or its payload swapped
   (content)?

**Yardstick / nulls (mandatory, pre-committed).**
- **Random-add null** (the exact 3b/3c null): matched-norm random vector at `L_b`.
  Predict ~0 on both AIM and CONTENT projected onto `Δℓ` (non-specific), whereas
  the real swap moves the output. p = frac(|null effect| ≥ |real effect|), N≥200
  random draws.
- **No-swap baseline**: the attention pattern under plain install (the reference
  the swap is differenced against).
- **Permutation over head labels** for the aggregate AIM/CONTENT significance
  (head-level localization is pre-refuted, 0/128 — do not rediscover it).
- Real-word ceiling gates each cell (inherited from 3-hop); only cells that flip
  under the real swap (3b-positive) enter the decomposition.
- `λ yardstick`: "the swap re-aims attention" counts ONLY if AIM beats the
  random-add null; a raw non-zero Δweight is not evidence.

**Predictions (fixed, a priori).**
- **P1 (primary — mediation MEASURED).** On 3b-positive cells, the swap's total
  projected routing effect at the reader zone beats the random-add null at
  p < 0.05 (aggregate). The loop value-edit → routing change → flip is closed in
  the routing register.
- **P2 (register split — the beamformer call).** CONTENT fraction > AIM fraction
  of the projected swap effect (content-dominant, medium handle). All three
  fractions (AIM/CONTENT/INTERACTION) reported verbatim with signs. Either
  dominance is a clean result; content-dominant confirms the medium-handle
  thesis, aim-dominant motivates P-ATT-STEER.
- **P3 (localization — verbatim, NOT gated).** The routing change concentrates in
  the s282 reader/unrolling window (32B: the L52–60 sequential band; 4B: the
  collapsed L32–33 zone). Reported as a profile; the swap may act wherever the
  bridge is read. Distributed over heads, never single-head.

**Verdict (freeze on GO).**
- **MEDIATION-MEASURED** ⟺ P1 (swap effect beats the random-add null in the
  attention register, p < 0.05).
- **MEDIUM-HANDLE-CONFIRMED** ⟺ P1 ∧ P2 with CONTENT > AIM.
- **AIM-STEERING-INDICATED** ⟺ P1 ∧ P2 with AIM > CONTENT → pre-reg P-ATT-STEER
  as the causal test (no post-hoc reinterpretation of this run).
- Anything less → reported verbatim. A clean P1 negative (the swap flips the
  output but moves NOTHING measurable in the attention register beyond the null)
  would mean the mediation runs through a pathway this decomposition doesn't
  capture (residual-stream bypass / MLP between joins) — itself a sharp finding
  that would send the elimination to the MLP-gating register. No sign-flip rescue.

**Registers (`λ measure`).** The CLAIM is routing (the swap re-targets/re-fills
routing) → the probe is an attention-register measurement: register-matched (the
inversion of the s206 scar, where an attention-weight probe was burned on a VALUE
claim). Weight ≠ effect is handled by construction: the decomposition pairs
Δweights (AIM) with OV contribution (CONTENT), so a raw weight change that carries
no logit effect scores as null. This is the CAUSAL leg; P-TYPE-QK carried the
geometric leg (negative), P-ATT-STEER would carry the intervention leg.

**Honest scope.** (a) First-order decomposition — the AIM/CONTENT/INTERACTION
split is exact only to first order; the interaction term is reported, not
absorbed. (b) GQA: KV side has 8 heads (low power); Q-side aggregate is primary.
(c) q_norm/k_norm renormalize per token → the captured weights are the model's
actual attention, but attributing "aim" to a specific QK subspace is out of scope
here (that was P-TYPE-QK). (d) "The swap re-targets attention" = a mechanism
observation over the edited residual's downstream effect, NOT a traced circuit;
aggregate/zone statistics only (0/128 pre-refuted). (e) hook-not-weight; the
operand is installed, not baked. (f) A RUNG: it upgrades the 3-hop causal result
into a routing measurement; it does not by itself grant beam-aim as a second REPL
handle — that is P-ATT-STEER's verdict.

**Files to build (on approval).** `scripts/explore/att_mediation.py` (imports
`operand_multihop3` helpers; adds attention/OV capture + the 3-channel
decomposition + random-add null + permutation), results →
`results/type-att-med/qwen3-32b/` (and `…-4b/` contrast smoke). `--validate`
no-model self-test first (planted attention pattern → known AIM/CONTENT split;
random null flat), per the QK-instrument precedent.

## P-ATT-MED — Result @4B (s286 contrast smoke; NOT the verdict host)

Instrument `scripts/explore/att_mediation.py` (built s286, commit 5ecd446).
`--validate` no-model self-test green: CONTENT-only → aim 0.000/content 1.000,
AIM-only → aim 1.000/content 0.000, DLA linearity exact (|Δ|=9e-16), matched-norm
random null flat (|mean/std|=0.002) — the decomposition recovers planted splits
and discriminates. 4B smoke (Qwen3-4B, install L9, swap L20, reader L20–35, 6
install-correct cells, n_null=30, ~35s), `results/type-att-med/qwen3-4b/`:

| | aim_frac | content_frac | inter_frac | p_vs_null |
|---|---|---|---|---|
| AGG (6/6 flipped) | 0.085 | **0.812** | 0.103 | 0.000 |

All six cells flip and are **content-dominant** (content 0.69–0.87, aim 0.01–0.17);
`p_vs_null=0.0` every cell — the swap's attention-register contribution beats the
matched random-add null decisively (the null does real work; the instrument
discriminates). **Advisory reading (4B contrast, NOT the verdict):** the
medium-handle a-priori call holds at 4B — the swap flows through *swapped content
at ~fixed aim*, not by re-aiming attention. The 4B reader zone is the compressed
pinned window (s282); the 32B verdict host unrolls the schedule sequentially
(L52–60), so whether content-dominance survives there is the real test.

## P-ATT-MED — Result @32B (s286) — CLOSED POSITIVE: mediation MEASURED, MEDIUM-HANDLE

> Run of record: `results/type-att-med/qwen3-32b/att_mediation.json` (commit after
> this write; instrument 5ecd446). Qwen3-32B, install L9, **swap L25** (the strongest
> 3b country-swap from the three-hop run of record: flip 0.891 vs random 0.057),
> scale 2.0, reader zone **L25–63**, 18 valid landmarks, **n_null=200**, ~31 min.

**VERDICT: `MEDIATION-MEASURED = TRUE`, `MEDIUM-HANDLE-CONFIRMED = TRUE`.**
(`AIM-STEERING` NOT indicated → P-ATT-STEER stays gated.)

| | aim_frac | content_frac | inter_frac | content>aim | p<0.05 vs null |
|---|---|---|---|---|---|
| **AGG (18/18 flipped)** | **0.195** | **0.735** | 0.070 | **18/18** | **16/18** |

- **P1 — MEDIATION MEASURED.** All 18 cells flip; the swap's attention-register
  contribution beats the matched random-add null at p<0.05 in **16/18** cells (14 at
  p=0.0, median p=0.0). The value-edit → *measured* routing change → output-flip loop
  is now closed in the routing register — the s282 "steering-by-CONTENT proven,
  steering-by-AIM unmeasured" gap is closed with an observation, not an inference.
- **P2 — MEDIUM HANDLE.** content_frac 0.735 vs aim_frac 0.195, content>aim in
  **every** cell (18/18). The swap steers by *swapped content at ~fixed aim*, not by
  re-aiming attention — the a-priori beamformer / K-structural call (§"steering",
  §"relocation hypothesis"), confirmed at the verdict host. AIM never dominates ⇒ no
  transient-instruction (beam-aim) write is indicated; the REPL keeps ONE handle
  (medium/content), not a second.
- **The two null-misses are magnitude, not counter-evidence (verbatim).** Sphinx
  (p=0.815, attn_total 1.49) and Petronas Towers (p=0.11, attn_total 14.9) have tiny
  attention-mediated magnitude vs 27–81 for the rest — their flip routes mostly
  *outside* the captured attention path (MLP-between-joins / residual bypass). The
  minority-of-cells edge the pre-reg anticipated: for most cells the attention
  register carries the mediation; a few route it elsewhere. Not gated, reported.
- **Scale contrast (4B → 32B).** content 0.812 → 0.735, aim 0.085 → 0.195: 32B's
  *unrolled* schedule (reader L25–63, window L52–60) re-aims modestly more than 4B's
  *compressed* pinned window, but content still dominates ~3.8:1. The unrolling buys
  a little aim, the medium handle holds — coheres with s282 (4B compresses, 32B
  sequences) without overturning the register split.

**P3 — localization (verbatim, NOT gated).** The routing change is **late-
concentrated**: |contribution| peaks at L61–63 (readout / re-expansion) plus the
L49–60 unrolling band (L52–60 = 38% of total; early L25–40 only 7.7%). Coheres with
s282's 32B sequential-unrolling window L52–60 and the QK-negative's late-bind zone
(§Result-32B pt 3, L49–62). Distributed over heads; no single-head claim (0/128).

**What it means for the arc.** The types mechanism was eliminated from every
value/geometry home (1b storage, 1c beam-coherence, QK read-in, JS workspace — four
negatives). P-ATT-MED is the **first positive routing-register observation**: the
licensing/composition IS mediated through routing, and the handle we have on it is
*content* (relocate the term), not *aim* (force the edge). This is exactly
map-and-swap's "write terms, never instructions" (K-structural, s276) made a
measurement: the 3-hop swap is a term relocation the routing then reduces. It does
NOT resurrect the QK-bilinear-as-lattice reading (QK stays negative) — it says the
mediation is real and content-carried, wherever in routing the check itself lives.

## P-ATT-FFN — retrieval vs composition (PRE-REG, APPROVED+FROZEN s286, Michael; 4B smoke leads, 32B verdict on GO)

> Michael's read of the two P-ATT-MED null-misses (s286): they are not weak cells,
> they are a **second route — FFN fact-lookup, not attention composition**. This
> pre-reg tests it. Grounded in the FFN-as-key-value-memory literature (Geva;
> ROME/MEMIT) AND our own frame: the s276 **database frame** (operand = value-register
> row) and the FFN-bake arc (operand installs as a single appended MLP neuron). Under
> map-and-swap: **atoms/facts = FFN value-rows, joins/composition = attention**; the
> 3-hop chain should be caught doing **both**. Predictions, nulls, verdict fixed here
> before any graded run (`λ measure` + `λ yardstick`).

**The gap in P-ATT-MED.** It decomposed only the ATTENTION path (AIM vs CONTENT) and
scored the attention contribution against the null. It never measured the **MLP
contribution** or what fraction of the *total* flip attention carries. So "the
null-misses are FFN retrieval" is currently unfalsified: a tiny attention
contribution is consistent with MLP-retrieval OR with a simply-weak effect. To claim
retrieval we must show the **MLP carries the flip** where attention does not.

**Hypothesis.** The 3-hop chain is computed by a MIX of routes. For most cells the
swap's effect is transported by attention (P-ATT-MED, content-dominant). For a
minority — the P-ATT-MED attention-null-misses (Sphinx, Petronas) — the last hop
(country→continent) is an **FFN fact-lookup**: the swapped country content is mapped
to its continent by an MLP, and that MLP output carries the flip while attention does
not. These cells also **skip the bridge-sequencing** that composition cells need.

**Instrument.** Extend `scripts/explore/att_mediation.py` (`λ one_way`, additive —
existing P-ATT-MED fields byte-identical, new work behind `--route-decomp`). Full
residual-stream **direct logit attribution** of the swap's *total* effect on the
continent-logit-diff direction w:
1. Total: `Δℓ_total = logit_diff(swap) − logit_diff(baseline)` at the readout (ground
   truth to reconstruct against).
2. Per reader layer L: **attention** channel (existing aim+content+inter, via v/weights
   + o_proj) AND **MLP** channel `Δmlp_out_L · w` (hook `dec[L].mlp` output, baseline
   vs swap). Direct/embed = `Δℓ_total − Σ_L(attn_L + mlp_L)` (reconstruction residual;
   should be small — a completeness check).
3. Per cell: fractions attn / mlp / direct of `|Δℓ_total|`; route = argmax(attn, mlp).
4. **Depth-order signature (secondary, reuse `operand_multihop3.lens_order`).** Per
   cell, logit-lens peak layers for the country and continent tokens. Composition ⟺
   country resolves before continent (bridge sequencing); retrieval ⟺ continent
   resolves early / without country-bridge dependence.

**Nulls (mandatory).** The matched-norm random-add at `L_b` (the exact 3b null):
predict ~0 on attn AND mlp AND total projected on w. p = frac(|null| ≥ |real|),
N≥200. Reconstruction check: `Σ channels ≈ Δℓ_total` (|residual|/|total| small) —
a decomposition-completeness gate, not a hypothesis gate.

**Predictions (fixed, a priori).**
- **P1 (primary — route dissociation).** The two P-ATT-MED attention-null-misses
  (Sphinx, Petronas) are **MLP-dominant** (mlp_frac > attn_frac) with the MLP channel
  beating the null (p<0.05), while the P-ATT-MED attention-significant cells are
  **attention-dominant**. A per-cell route split, not a global mean.
- **P2 (depth-order corroboration, verbatim + gated-with-P1).** The MLP-dominant
  cells resolve the continent **without** country<continent bridge-sequencing
  (retrieval signature); the attention-dominant cells show the sequencing.
- **P3 (verbatim, NOT gated).** The MLP contribution's layer profile — where the
  country→continent fact-map fires (mid-stack MLP per the ROME/FFN prior vs the late
  readout zone). Reported, not gated.

**Verdict (freeze on GO).**
- **FFN-RETRIEVAL-CONFIRMED** ⟺ P1 (Sphinx AND Petronas MLP-dominant + MLP beats null)
  AND the attention-null-misses are exactly the MLP-dominant set (dissociation clean).
- **MIXED-ROUTE-MEASURED** (weaker, still positive) ⟺ some cells attention-dominant
  AND some MLP-dominant with both channels null-beating — the 3-hop provably uses both
  routes, even if the specific 2 cells don't split as predicted.
- Negative (the null-misses are MLP-negligible too — the flip is direct-residual or
  just weak) → retrieval NOT supported; the null-misses are magnitude after all, as
  P-ATT-MED reported them. No post-hoc route reassignment.

**Registers (`λ measure`).** CLAIM = facts are FFN-resident, composition is attention
→ probe = residual-stream DLA over attn vs MLP = register-matched for BOTH channels;
the total-reconstruction gate proves the decomposition is complete (no hidden path).
No causal intervention (that would be an MLP knockout — a later rung); this is the
attribution leg. Distributed: aggregate over the MLP's contribution, no single-neuron
claim (the FFN-bake installed ONE neuron, but that is an *installed* atom, not a claim
that native facts are single-neuron).

**Host & order.** Reuse the P-ATT-MED cells/config verbatim (Qwen3-32B, install L9,
swap L25, scale 2.0, 18 cells, n_null 200) so the route split maps 1:1 onto the
P-ATT-MED verdict cells. **4B contrast smoke first** (per the P-ATT-MED amendment):
does the route dissociation appear at 4B, where composition is compressed? Results →
`results/type-att-ffn/qwen3-{4b,32b}/`.

**Honest scope.** (a) DLA is first-order (RMSNorm scale approximation); attn-vs-MLP
attribution says *where the continent-aligned output is produced*, not a traced
circuit. (b) Retrieval vs composition is a **route** characterization; "fact-lookup"
is the FFN-memory reading, not proof of a specific stored key. (c) n=2 predicted
retrieval cells is low power for P1's cleanliness — MIXED-ROUTE-MEASURED is the robust
fallback. (d) A causal MLP-knockout (does removing the MLP path kill the flip only for
retrieval cells?) is the stronger test, deferred. (e) hook-not-weight; a RUNG in the
map-and-swap decomposition (atoms=FFN, joins=attention), not the compiler claim.

## P-ATT-FFN — instrument note + Result @4B (s286 contrast smoke; NOT the verdict)

**Instrument bug found + fixed by the smoke (`λ measure`, smoke-surfaced → fix
pre-run).** The first two smokes had `recon_err ≈ 1.8` (attn+MLP did not reconstruct
the total). Cause: `hidden_states[-1]` is the **post-final-norm** state, not the raw
final residual (verified: `‖hs[-1] − rmsnorm(raw_final)‖/‖·‖ = 0.003`; per-layer
residual identity holds <0.6% for L0–L34, breaks only at the last entry). Fix: capture
the true pre-norm final residual as the **input to `norm_f`** (forward-pre-hook). After
the fix `recon_err = 0.001` — attn+MLP+direct reconstruct the total exactly, direct ≈ 0
(the swap at the nonce slot reaches the readout only via attention/MLP, never direct).
**This does NOT affect the P-ATT-MED verdict or the route split:** those are *ratios*
of projections onto the same `w` (scale-invariant to the wrong RMS); only the
absolute total / reconstruction were wrong.

**4B smoke (route-decomp, install L9, swap L20, reader L20–35, 18 cells, n_null 30):**
- **Reconstruction clean** (mean recon_err 0.0012) and **MLP channel real + null-beating**
  (p_mlp<0.05 in 13/14 flipped cells). The FFN carries a genuine, significant share of
  the country→continent flip — the FFN-fact frame has legs.
- **Route split = MIXED, MLP-leaning:** 11/14 cells MLP-dominant (mean mlp_frac 0.586),
  3/14 attention-dominant. At 4B the fact-map is FFN-heavy for most cells.
- **Tension with the clean P1 (verbatim, for the 32B verdict):** the 3 attention-dominant
  cells are Petronas, Sphinx, Victoria Falls — i.e. the two 32B P-ATT-MED null-misses
  (Sphinx, Petronas) are attention-dominant *here*, weak-MLP (p_mlp 0.033/0.067), the
  OPPOSITE of the P1 prediction. 4B is contrast (compressed schedule, different cells
  from the 32B verdict host), so this does not decide P1 — but it flags that
  **MIXED-ROUTE-MEASURED is the more likely 32B outcome than a clean FFN-RETRIEVAL
  dissociation.** Reported now; the 32B verdict scores the frozen gates.

Results `results/type-att-ffn/qwen3-4b/`. Verdict host = Qwen3-32B on GO (reuse the
P-ATT-MED cells/config verbatim so the route split maps 1:1 onto its verdict cells).

## P-ATT-FFN — Result @32B — RUN IN FLIGHT (s286, tmux main:1)

Verdict launched on Michael GO (s286): Qwen3-32B, `--route-decomp`, install L9, swap L25,
scale 2.0, reader L25–63, 18 cells, n_null 200 → `results/type-att-ffn/qwen3-32b/att_ffn.json`.
Verified running (weights 707/707). **No verdict recorded yet.** On completion, read
`aggregate.route` (n_attn_dominant vs n_mlp_dominant, `mlp_dominant_cells`,
`mean_recon_err` must be small) and score the frozen gates: **FFN-RETRIEVAL-CONFIRMED**
⟺ Sphinx AND Petronas MLP-dominant + MLP beats null; **MIXED-ROUTE-MEASURED** ⟺ both
routes present + null-beating (the likely outcome per the 4B contrast, which put
Sphinx/Petronas on the *attention* side); **negative** ⟺ null-misses MLP-negligible. Fill
§Result-32B verbatim, no post-hoc route reassignment.

## P-TYPE-SWAP — the ill-typed term (PRE-REG, APPROVED s287, Michael; 4B smoke leads, 32B verdict freezes on GO)

> **The generating induction (s287, Michael).** For most of our positive experiments
> to show what they show, the system must have types of some sort — v3 nonce
> crossover, 8-way decodability, the null-gated 1a lattice, the 3b class-swap beating
> random-add, P-ATT-MED's differential transport, name_pen's saturation asymmetry:
> each individually fails under a no-types H₀. Existence is over-determined; the
> four-way null (1b/1c/QK/JS) constrained only *implementation*. But the design space
> has a hole: every causal run compared **same-type on-manifold** (the class swap,
> works) against **no-type off-manifold** (random-add, refused). The deflationary
> counter — "manifold membership, not typing" — has never been tested. The missing
> cell is **wrong-type, on-manifold**. This pre-reg fills it, and in doing so gives
> the check what four location probes could not: a measured **stage** where the
> discipline acts.

**Measurement correction this design must carry (`λ measure`, flagged s287).** The
P-ATT-MED swap-vs-null differential is **w-projected** (contributions projected on the
continent-logit-diff direction). A random vector transported through the same edges
would score ~0 on w by geometry alone — so "random was refused" vs "random was
transported but has no w-component" is currently **indistinguishable**. The refusal
claim is confirmed only in the output register. This instrument therefore measures
**unprojected transport norms**, survival-normalized (below); the projected quantities
remain as the reduction-register readout. Without this, every arm comparison is
confounded by projection geometry.

**Hypothesis.** The bridge-swap causal handle is type-disciplined: composition
transports and reduces a swapped term iff it is well-typed for the slot. An
on-manifold, matched-norm, **wrong-type** centroid displacement at the same bridge
layer is refused at a measurable stage — behaving like the random-add, not like the
same-type swap — and the stage at which it dies (medium / join / reduction) locates
where the licensing acts. Manifold-membership predicts instead that any on-manifold
content transports and interferes.

**Conditions (per cell; all edits matched to the same-type swap's REALIZED norm at
the bridge layer — realized-norm logged live, the 1b lesson).**
1. **baseline** — install only.
2. **same-type** — the 3b country-swap `(c_tgt − c_src)·S` (in-run positive control;
   must replicate the 3b flip or the cell is excluded).
3. **sortal** — same broad type, wrong domain: `(c_animal1 − c_animal2)·S` from an
   animal noun bank (entity-class displacement with no continent image). Verbatim
   ladder row, NOT gated (see below).
4. **wrong-type** — `(c_adj1 − c_adj2)·S` from an adjective bank (MOD-class
   displacement — a type violation proper for the country slot).
5. **random-add** — matched-norm random (the exact 3b null), N≥200.

**Instrument.** Extend `scripts/explore/att_mediation.py` (`λ one_way`, additive —
existing fields byte-identical, new work behind `--arms`). Per arm, the three-stage
pipeline decomposition:
- **SURVIVAL S** = ‖Δresidual‖ at the reader-zone layer inputs (does the edit live
  long enough in the medium to be read? separates died-in-medium from refused).
- **TRANSPORT TE** = ‖Δ attention contribution‖ / S at the reader zone, UNPROJECTED
  (does the join carry it?), plus **attention mass on the bridge slot** (does the
  reader withdraw its edge from an ill-typed slot? — the P-ATT-DIFF question asked
  causally; this subsumes P-ATT-DIFF's minimal-pair design with a causal handle).
- **REDUCTION R** = the projected output register: movement along Δℓ (same-type),
  and **BREAK** = degradation of the baseline correct-continent margin (all arms) —
  is the ill-typed edit *ignored* (margin intact, like random) or *interferes as
  content* (margin damaged)?
- MLP channel per arm via `--route-decomp` (already built): whether the fact-map
  route enforces the same discipline as the attention route (P-ATT-FFN tie-in).

**Nulls (mandatory, pre-committed).** (1) random-add matched-norm N≥200 per arm
comparison — every claim is arm-vs-null and arm-vs-arm, permutation over cells;
(2) two independent wrong-type banks (adjective primary; a second MOD-class bank as
replication row, verbatim) — no single-axis artifact; (3) same-type arm must
replicate 3b in-run (instrument gate); (4) reconstruction gate from `--route-decomp`
(recon_err small); (5) permutation over head labels for aggregates (0/128,
pre-refuted — no single-head claims).

**Predictions (fixed, a priori).**
- **P1 (primary — the discriminator).** Some pre-registered stage discriminates
  same-type from wrong-type beyond the random-add null (permutation p<0.05):
  TE(same) > TE(wrong) and/or slot-mass drops for wrong-type. The a-priori call
  (well-formedness frame: type = which joins are licensed) is **join-level**
  discipline — the ill-typed term survives the medium (on-manifold) but the join
  refuses it.
- **P2 (pre-committed alternative, still typing).** TE(wrong) ≈ TE(same) — the join
  transports type-blind (slot/content-based, coheres with fixed-aim medium-handle) —
  but reduction fails: no coherent output movement, BREAK ≈ random. The check acts
  at the **reduction/fact-lookup**, not the join.
- **P3 (sortal ladder, verbatim, NOT gated).** The animal arm transports at the join
  (e-typed where e is expected) but fails at the fact-map (no continent image) —
  predicted TRANSPORTED-NOT-REDUCED, with its MLP channel distinguishing sortal
  (relation-domain) discipline from syntactic-type discipline. Graded transport
  same > sortal > wrong-type > random would be a measured sortal hierarchy.
- **Deflationary outcome (pre-committed, counts fully).** NO stage discriminates
  same vs wrong while both beat random at transport AND wrong-type BREAKS the chain
  like content — then on-manifold content is transported and reduced type-blind:
  **manifold membership, not typing**, wins this handle; the induction's ensemble
  argument loses its causal leg and the existence claim falls back on the
  behavioral/geometric registers alone. Reported verbatim, no rescue.

**Verdict (freeze on GO).**
- **JOIN-TYPED** ⟺ P1 (transport-stage discrimination, p<0.05, both wrong-type banks).
- **REDUCTION-TYPED** ⟺ P2 (transport type-blind + reduction discriminates).
- **TYPE-BLIND / MANIFOLD** ⟺ the deflationary outcome.
- Mixed per-cell splits → reported verbatim with the route decomposition (the
  P-ATT-FFN mixed-route precedent); no post-hoc stage reassignment.

**Registers (`λ measure`).** The CLAIM is licensing (which reductions fire) — probed
across three registers each stage-matched: value (survival), routing (unprojected
transport + slot mass), output (reduction/break). The projection confound is handled
by construction. Causal handle throughout (hook-not-weight); aggregate statistics
only.

**Host & order.** Qwen3-4B contrast smoke first (the s286 amendment pattern), verdict
host Qwen3-32B on GO — reuse the P-ATT-MED cells/config verbatim (install L9, swap
L25, scale 2.0, 18 cells, n_null 200) so every arm maps 1:1 onto the P-ATT-MED and
P-ATT-FFN verdict cells. Results → `results/type-swap/qwen3-{4b,32b}/`.

**Honest scope.** (a) Wrong-type displacement is constructed from *our* class banks —
a negative for one bank pair does not exhaust "ill-typed"; two banks + verbatim
replication row bound this. (b) Survival-normalization separates medium-death from
join-refusal only to first order (the edit interacts with the stack). (c) A
join-level negative + reduction-level positive does not resurrect any of the four
geometry nulls — stage location, not storage. (d) The animal arm's "no continent
image" presumes the fact-map is country-keyed; if P-ATT-FFN's 32B verdict lands
FFN-RETRIEVAL or MIXED, its route split refines this arm's reading. (e) n=18 cells;
per-cell splits are low power — aggregate gates only.

## Sessions
s283b (page created from the attention-gap hammock; no experiments run;
1c dark-field run in flight during discussion).
s284 (P-TYPE-QK pre-reg DRAFTED + instrument built while the 1c run was in
flight; pending Michael approval → freeze → run).
s284 cont (pre-reg frozen on approval 2b40033; 32B run: qk_aligned=FALSE
dead-on-null — lattice roles add no Q-side QK gain in the band; inverted-sides
+ rolenull-fires + late-bind structure reported verbatim, post-hoc; queue
advances to P-ATT-MED).
s286 (P-TYPE-JS closed the exhaust out of the J-space workspace too — all
geometric/value homes eliminated; P-ATT-MED pre-reg DRAFTED as the active next
probe: rerun the 3-hop bridge-swap WITH attention capture + an aim-vs-content
first-order decomposition, converting the strongest causal result into a
routing-register measurement; P-ATT-DIFF material folds in as one arm; PENDING
MICHAEL APPROVAL, freeze on GO).
s286 cont (Michael APPROVED, 4B-smoke-first amendment; instrument
`scripts/explore/att_mediation.py` built + `--validate` green + 4B contrast smoke
green = CONTENT-dominant advisory (§Result-4B); then Michael GO → 32B verdict
LAUNCHED in tmux main:1, swap L25, n_null=200).
s286 cont (32B VERDICT IN, ~31 min: MEDIATION-MEASURED=TRUE, MEDIUM-HANDLE=TRUE —
18/18 flip, 16/18 beat null p<0.05, content 0.735 vs aim 0.195, content>aim 18/18;
AIM-STEERING NOT indicated → P-ATT-STEER stays gated. First POSITIVE
routing-register observation in the types arc; the s282 steering-by-content gap is
measured. §Result-32B; the two null-misses are tiny-magnitude cells; localization
late L49–63. Memory SKIPPED by Michael — follow-ups will sharpen a better one).
s286 cont (Michael's read: the null-misses are FFN fact-lookup, not weak composition
→ P-ATT-FFN pre-reg APPROVED+FROZEN. Instrument extended `--route-decomp` (attn vs
MLP vs direct DLA + total reconstruction + depth-order). 4B smoke SURFACED + FIXED a
reconstruction bug — `hidden_states[-1]` is post-final-norm; capture the pre-norm final
residual via a `norm_f` pre-hook (recon_err 1.8→0.001; P-ATT-MED ratios unaffected).
4B route split MIXED, MLP-leaning (11/14 MLP-dominant, MLP null-beating 13/14 — FFN
carries the fact-map), but the two 32B null-misses are attention-dominant at 4B →
MIXED-ROUTE the likely 32B outcome. Verdict host 32B on GO).
s286 cont (Michael GO → P-ATT-FFN 32B verdict LAUNCHED in tmux main:1, `--route-decomp`,
swap L25, n_null 200 — RUN IN FLIGHT, §Result-32B pending on completion).
s287 (inductive hammock, Michael: types-mechanism EXISTENCE is over-determined by the
positives — six results each individually fatal to a no-types H₀; the four-way null
constrained implementation only. Two gaps surfaced: (1) the causal design space spans
only same-type-on-manifold vs no-type-off-manifold — the wrong-type-on-manifold cell,
which discriminates typing from manifold-membership, was never run; (2) the P-ATT-MED
swap-vs-null differential is w-PROJECTED — "random refused" vs "random transported
with no w-component" is currently indistinguishable; refusal is confirmed only in the
output register. → P-TYPE-SWAP pre-reg DRAFTED (§above): ill-typed-term arms
(sortal/wrong-type/random ladder), 3-stage survival/transport/reduction decomposition
with UNPROJECTED transport norms, subsumes P-ATT-DIFF with a causal handle; verdict
names JOIN-TYPED / REDUCTION-TYPED / MANIFOLD. PENDING MICHAEL APPROVAL; P-ATT-FFN 32B
verdict still in flight during drafting.)
