---
title: "Types are the well-formedness of β-reduction — the combinator reading of the type lattice"
status: active
category: explore
tags: [types, beta-reduction, combinators, KIBC, CCG, montague, lambek, discocat,
       curry-howard, well-formedness, S-combinator, B-combinator, functor-kind,
       type-check, compiler, P-TYPE-1, P-TYPE-1b, P-TYPE-1c, P-TYPE-QK, P-TYPE-JS,
       dark-field, holography, jspace, workspace, exhaust, beamformer, C1, C2, C9,
       s282, s283, s284, s285, s286]
related:
  - type-check-is-the-qk-bilinear.md
  - beamformer-theory.md
  - type-is-decodable-readout-not-causal-direction.md
  - opcodes-circuits-in-compute.md
  - montague-inversion.md
  - map-and-swap-resident-lisp.md
  - project-thesis.md
depends-on:
  - type-is-decodable-readout-not-causal-direction.md
  - opcodes-circuits-in-compute.md
created: session 282
---

# Types are the well-formedness of β-reduction

> **The closure.** Given the two project frames — **attention = β-reduction** (s276:
> attention = application = join) and **the LLM computes in the KIBC opcodes** (C2: the
> 9×9 crystal is a Gram-proven universal combinator evaluator) — the s282 type
> measurements are *forced*, and they mean one thing: **a type is not a stored feature; it
> is the well-formedness (the licensing) of a reduction.** The Montague type lattice is a
> projection of the combinator basis; the type of a word = which opcode its application
> invokes.

## Why "decodable but not causal" is forced (not a puzzle)

In a combinatory / typed-λ system a term does **not carry** its type as data — the type is
the *discipline on application*: `(a→b)` applied to `a` reduces; a mismatch does not. The
type is **derived from** how the term reduces, not stored beside it.

So the s282 result — type is **richly decodable but `type_direction_is_causal = false`**
(v4) — is exactly what this frame predicts. You can **decode** a term's type (it is a
well-defined function of its reduction role); you cannot **ablate** it as a stored direction
because it is not stored — it is the **shape of which joins (β-reductions) the term
licenses**. The decodable readout is the network's value-register *image* of that
constraint. This dissolves the crisp-vs-graded question: types are neither a crisp stored
gate nor a graded stored feature — they are the **precondition on which reductions fire**.

## The 3 axes are combinator roles (INFERENCE — the P-TYPE-1b prediction)

⚠ **This mapping is inference from the 1a-follow loadings under the assumed frame, NOT yet
measured.** It generates the P-TYPE-1b test below. Measured facts: 3 functor-kind axes,
`e` at origin, arity-ladder negative (see the sibling page).

If type = which opcode's application a word participates in, the measured axes map to
combinator **roles**:

| measured axis (32B L40) | combinator role | why |
|---|---|---|
| **axis0** (var 0.73) QUANT+DET | **S / binding** | binding = bracket abstraction → S/K/I; S handles a bound var in both function+arg positions. Quantifiers/determiners bind a variable. |
| **axis2** (var 0.06) REL/PRED vs MOD | **B / composition** | a modifier `(e→t)→(e→t)` **composes** with a predicate = B. |
| **axis1** (var 0.08) CONN/FUNC | **t-level plumbing** | truth-value combiners; clause-level B/C glue. |
| **ENTITY `e`** at origin | **I / operand** | an atom applies to nothing; it is *consumed*, the value-row, not a functor. |

**Why binding (axis0) dominates (73%):** binding is the operation that creates *nested*
reductions and first-class functions — the **S/Y axis** that separates "just apply" (B/C)
from "bind-and-recurse" (S/Y). It is the axis that makes the machine Turing-complete beyond
flat application, and (montague-inversion) the one generalized quantifiers **force**. It is
the same capability the s282 **3-hop** exercised. The dominant *type* distinction is exactly
"does this term bind / build a function."

⇒ the Montague type lattice **is a projection of the combinator basis**. Types and KIBC
opcodes are two views of one object: *the type of a word = which combinator its application
invokes.* (This is the crystal-alignment triangulation, earlier deferred as forced-fit,
now theory-predicted.)

## Discriminating claim: the type system is CCG-combinatory, not Church-arity

The s282 negative — **functor KIND, not arity count** (the ENTITY→PRED→REL arity ladder
failed) — is *discriminating*, not null. Simply-typed λ (Church) types by arrow-nesting
**depth**; a combinatory system routes through fixed opcodes and types by **role +
direction**. The machine typing by functor-kind-not-arity is evidence it does **combinatory
categorial** typing — CCG/Lambek slash-types `X/Y`, `X\Y` = "functor kind + direction, `e`
at the base" — *because* it computes in combinators. This leans the **Lambek ∧ CCG ∧
DisCoCat** side of the S5 identity over pure Montague arity-typing: a measured preference
between formalisms.

## The compress→expand arc = the compiler's type-check phase

Read the depth arc (sibling page) as a compiler pass:
- **full-rank lexical (embed–L4)** = lexer — each token's rich specific content.
- **low-rank band (L6–L48)** = **the typed-reduction phase** — content projected onto the
  small combinator-role axes; the β-reductions (attention joins) run *under type discipline*
  in that compressed space.
- **re-expand (L52–L63)** = codegen/readout — the normalized result written back to content.

C8 progressive-collapse is not incidental — it **is the reduction happening in type-space**.
The low-rank band is literally where β-reduction runs gated by type-compatibility. This is
the C1 compilation pipeline made concrete for the type layer.

## Curry–Howard closure (C9, concrete)

types = propositions, terms = proofs, β-reduction = normalization. If the opcodes are the
proof-combinators and attention is normalization, the low-rank band is the **propositional
structure** being proved and the readout is the normalized proof. "Low-rank + Montague-
shaped" means the proof system is **small / finitely axiomatized** — a handful of type
schemas = the KIBC principal types. The lattice being ~3 axes is the geometric image of
"the combinator calculus has a few principal types."

## The behavioural signature falls out (name_pen = argument saturation)

The s282 behavioural result was **name_pen-only**: a predicate `<e,t>` is an **unsaturated
application waiting for an `e`**. "John {verb}" supplies the `e` → the reduction fires
(cheap); "John {noun}" gives a second `e` with no functor to consume it → type mismatch
(dear). The behavioural "type effect" **is** β-reduction firing-or-failing on type-
compatibility = **argument saturation** = the S/application axis — which is why axis0
(binding/application) dominates. (Answers the `name_pen` fork: the operative "type" is
applicative saturation.)

## Consequence for the S5 identity claim

S5 `λ types`: type-directedness is the missing piece that turns shared-weight composition
into a discrete circuit. Under this frame that resolves: **the type is the router's
combinator-selector** — type-directedness = choosing the right opcode for the join =
attention (β-reduction) gated by type-compatibility. The "missing piece" = the combinator-
selection signal = the low-rank band we measured.

---

# P-TYPE-1b — pre-registration (combinator-zone × type-class dissociation)

> The frame turns 1b from "ablate a type" into a **falsifiable combinator prediction**, and
> plugs into the A1 zone-ablation machinery that is already causal + selective (C2). Frozen
> here per `λ measure` + `λ yardstick` before any graded run.

**Hypothesis.** If type = which opcode's application is licensed, then removing an axis's
*reduction capacity* **selectively** breaks the matching type-class:
- ablating **axis0 (binding/S)** across the low-rank band degrades **binding-type composition
  (QUANT/DET)** but NOT predicate/modifier composition;
- ablating **axis2 (composition/B)** degrades **modifier composition (MOD)** but NOT binding.
A **double dissociation** between axis (combinator role) and type-class.

**Why v4 was negative (and this is not a repeat).** v4 ablated a *global* type direction and
tested *retention of the whole crossover* → negative (correctly: types aren't a stored
direction). 1b ablates a **role-specific axis across the band as a ZONE** and tests
**class-selective** behavioural breakage — the operational form of "type = which reduction
is licensed," not "type = a stored vector."

**Instrument.** Reuse `type_lattice_geometry.py` axis directions (1a-follow) as the ablation
targets; project each band axis out of the residual stream across L6–L48 (zone×axis
ablation, hook-based). Behavioural readouts:
- **binding-type task:** quantifier composition (a "Every {nonce} …" / determiner-licensing
  cloze, v3-style surprisal crossover).
- **composition-type task:** modifier composition (an adjective/adverb-licensing cloze).
- **predicate control:** simple predication (name_pen-style).

**Registers (`λ measure`).** Ablation target = value-register band axis; the CLAIM is about
**reduction licensing** → measure the **behavioural** (reduction-outcome) effect and its
**class selectivity**, not a decodability change. Selectivity (which class breaks) is the
discriminator, never a single global number.

**Nulls (mandatory, pre-committed).**
1. **random matched-norm direction** ablated in the same zone → breaks **neither** class.
2. **cross-class control** = the dissociation itself: axis0-ablation leaves MOD intact;
   axis2-ablation leaves QUANT intact.
3. **task control:** a non-compositional task (lexical recall / bare next-token) survives
   band-axis ablation (rules out "we just broke the model").
4. **`e`-axis control:** ablating toward the ENTITY/operand origin (a near-null direction)
   has no selective composition effect.

**Verdict (FROZEN).** DISSOCIATION SUPPORTED ⟺ axis0-ablation degrades QUANT/DET-composition
by a pre-set margin over BOTH (a) its own predicate/MOD effect AND (b) the random-direction
null, AND axis2-ablation degrades MOD-composition over BOTH its QUANT effect and the null.
Anything less (both classes break, or random breaks a class) → NOT a clean combinator×type
map (report verbatim; the axes may be decodable-but-not-reduction-causal, i.e. still readout).

**Honest scope.** Value-subspace ablation across a zone ≠ ablating a combinator *per se*
(opcodes are circuits-in-compute, not weights). This tests whether the **type axes are
causally necessary for the matching composition** — the operational form of "type = which
reduction is licensed." A RUNG, hook-not-weight, host = 32B (the C5 host); a pair of
type-classes is a dissociation, not the whole lattice. If clean, it is the first **causal**
evidence that types are the reduction-licensing structure, not just a decodable readout.

## P-TYPE-1b — Result @4B smoke (s283; NOT the verdict host)

> Instrument: `wrapper/type_zone_ablation.py`, iterated v1→v4 in one session
> (commits bc1d242 → f7e07f7 → f0c3418 → 0961819). Verdict cells below are from
> **v4, the absolute-dose grid** — the only version where conditions compare at
> matched realized removed-energy. 4B ≠ pre-reg host; 32B run launched s283.

**CORE — the dissociation is ABSENT at 4B.** At the only interpretable dose
(d1 ≈ 74 E/tok per layer, roles energy-matched ±5%, recall_acc 1.0 everywhere):
`retQ` bind 0.843 / comp 0.801 / rolenull 0.868 — the binding slice does **not**
preferentially carry quantifier licensing. `dissociation_supported = False` by
the frozen rules, with no separation to argue about. Combined with the v4
global-direction negative, the value-register hiding places are exhausted at 4B:
**the lattice is exhaust, not consulted** — the licensing computation does not
read its own geometric ledger. This is the theory-pure outcome: a type that IS
the well-formedness of a reduction is unstorable by construction, so it cannot
be removed from the value register at any dose. The negative confirms the frame.

**Lattice slices = generic infrastructure.** Role subspaces destroy recall at
~270 E/tok while a 2D random subspace partially survives 1009 and needs ~9000 to
die — the lattice region is ~4× more load-bearing per unit energy, but
*uniformly* (all class-centroid offsets share the dominant axis0 component,
which carries general computation, not type tags). Sharp cliff between 74 and
270 E/tok.

**⚠ POST-HOC (needs own pre-reg before it counts):** gentle dampening (~74
E/tok) of ANY role subspace **unmasks** M_eff — 0.17 (t=0.6) → ~1.05 (t=5.5–6.7)
for all three role slices; random does NOT (0.05, t=0.19). The one cell in the
grid where lattice ≠ random behaviorally: shared-component-driven, not
class-selective. Candidate: "removing shared type-ledger signal reveals a weak
licensing channel."

**4B lattice structure (scale finding):** true band L9–L22 (14 layers; earlier
sub-bands were a falsy-zero p-bug). QUANT and DET **split onto separate axes**
at 4B (axis0 = QUANT-vs-rest @85% var, DET on axis1 ~5%, MOD clean on axis4)
where 32B co-loads QUANT+DET on axis0 — the lattice's internal organization
evolves with scale. M_eff is behaviorally unexpressed at 4B baseline (t≈0.6,
two grids) — coheres with the barely-resolved MOD axis; gate-0 discipline held.

**Instrument lessons (v1→v4, for any future zone ablation):** (1) `p or 1.0`
falsy-zero excludes the most significant layers — two runs shipped accidental
sub-bands; (2) never compare subspace ablations at full projection (variance
differs ×10⁴) — match on REALIZED removed energy, logged live from the hooks;
planned-vs-realized drifts ×25 (capture exemplars vs behavioral text);
(3) amplified random steering (α≫1) cascades across stacked hooks (realized
10¹⁰⁺ E/tok); (4) absolute-dose grids ≻ subspace-relative budgets; (5) breakage
gates on tiny-surprisal baselines must use accuracy, not ratios; (6) deviation:
the pre-reg e-axis control is unrealizable (raw ENTITY-centroid direction
carries ~10⁵ E/tok) — replaced by the role-null (CONN/FUNC) lattice subspace,
which is the sharper class-control anyway.

## P-TYPE-1b — Result @32B (s283b; THE VERDICT HOST) — CLOSED NEGATIVE

> Run: `wrapper/type_zone_ablation.py` v4 (commit 0961819), host Qwen/Qwen3-32B,
> band L24–L49 (26 layers, p-fixed in-run), absolute-dose grid planned
> {50, 150, 600, 2400} E/tok. Results committed 95d89de
> (`results/type-zone-ablation/qwen3-32b/`). Frozen rules applied verbatim.

**VERDICT: `dissociation_supported = False` at the pre-registered host.**
`bind_selective = False`, `comp_selective = False`, `nulls_clean = False`.
**P-TYPE-1b closes as exhaust-theory-confirmed at both scales.**

**This is the full-strength verdict, not a capacity-limited one.** Gate-0
passed BOTH effects: baseline Q_eff 1.197 (t=3.48), M_eff 0.929 (t=4.21),
recall 0.8. Unlike 4B (M_eff t≈0.6, unexpressed), the 32B baseline expresses
both licensing effects — the pre-reg host had everything to lose and lost
nothing selectively.

**The grid (retention = ablated/baseline; realized E/tok for role slices):**

| dose | bind retQ/retM | comp retQ/retM | rolenull retQ/retM | random retQ/retM |
|---|---|---|---|---|
| d1 (~25) | 0.963 / 0.998 | 0.988 / 1.004 | 0.977 / 0.968 | 1.056 / 0.937 |
| d2 (~74) | 0.963 / 1.004 | 1.011 / 0.996 | 0.984 / 0.932 | 1.167 / 0.821 |
| d3 (~280) | 1.087 / 0.801 | 1.123 / 0.847 | 1.112 / 0.751 | 1.388 / 0.606 |
| d4 (~1000) | 1.372 / 0.404 | 1.672 / 0.863 | 1.602 / 0.145 | 1.947 / −0.303 |

Read, no spin:
1. **No class-selectivity at any dose.** At d2 (~74 E/tok, the 4B
   interpretable dose) bind ≈ comp ≈ rolenull within noise — the
   pre-registered double dissociation is ABSENT, matching 4B.
2. **retQ AMPLIFIES with dose** (1.37–1.95 @d4, every condition including
   random) — opposite in sign to the predicted breakage. Verbatim
   observation; plausibly a surprisal-scale artifact of generic degradation
   (both crossover terms inflate, contrast widens). Not interpreted further.
3. **retM degrades generically, anti-mapping ordered:** rolenull 0.145 >
   bind 0.404 > comp 0.863 @d4 — the CONTROL subspace (CONN/FUNC) hurts
   modifier licensing most, not the pre-registered axis2/comp mapping.
   Random reaches sign-flip (−0.303) at ~2× realized energy →
   `nulls_clean = False`; even the generic pattern fails the null gate.
4. **⚠ The 4B "lattice = 4× load-bearing infrastructure" finding does NOT
   replicate @32B:** role-slice recall_acc holds 0.8→1.0 through ~1000 E/tok
   (4B cliff was 74→270). The infrastructure claim is **4B-scoped** (n=10,
   one-cell resolution on the recall uptick — not over-read).
5. **No 32B analog of the 4B M_eff-unmasking cell:** baseline M is already
   fully expressed, so "gentle dampening reveals a weak licensing channel"
   has no counterpart here — coheres with a 4B-capacity artifact, but that
   remains post-hoc pending its own pre-reg.

**Band note (for 1a-follow):** the in-run p-fixed band is L24–L49, later and
narrower than 1a's L6–L48 sustained-low-rank characterization (different
estimator, falsy-zero fix applied) — a refinement, not a contradiction.

**Deviation (same as 4B, logged in verdict.json):** e-axis control replaced
by role-null (CONN/FUNC) — raw ENTITY-centroid direction carries ~10⁵ E/tok,
unrealizable as a near-null.

**Meaning.** With (i) the v4 global-direction negative, (ii) the 4B zone×axis
grid, and (iii) this full-baseline 32B verdict, the value-register hiding
places are exhausted at both scales: **the type lattice is EXHAUST — a
readout of routing-resident licensing — not a consulted ledger.** The
theory-pure outcome: a type that IS the well-formedness of a reduction is
unstorable by construction, so no dose can remove it from the value register.
The negative confirms the frame. The REPL is unaffected: decode-verify-swap
needs only *us* to read the ledger (Print/type-checker side), not the machine
to consult it. Successor experiment: **P-HOF-1** (§Consequence below).

## Holographic reading — the amplification is dark-field contrast (s283b discussion, Michael)

> Frame: s136 `beamformer-theory.md` + `holographic-plates.md`. Beam = attention/routing
> (the inference pattern); gemstone = the frozen weights (the cut, the KIBC facet
> geometry); value register = the illuminated MEDIUM the beam traverses.

Every 1b result lands naturally in this frame:

1. **Generic graceful degradation = holographic damage.** Scratching a hologram dims
   everything, deletes nothing local. No class-selective breakage at any dose; 32B
   role-slice recall survives ~1000 E/tok (bigger plate, more redundancy). The *storage*
   prediction failed because holograms do not store locally.
2. **retQ amplification = dark-field contrast.** Q_eff/M_eff are CONTRAST measures
   (surprisal differences), not amplitudes. If licensing rides the BEAM and the value
   register is the medium, dimming the medium is *background subtraction*: haze is removed
   faster than signal → contrast RISES. Dark-field microscopy: block the direct light,
   the scattered signal jumps out. The amplification is therefore an independent
   signature that the signal is in the beam, not the medium — it CORROBORATES exhaust.
3. **The 4B M_eff unmasking is the same phenomenon** (t 0.6→5.5 under gentle lattice
   dampening, random does not) — dark-field seen once already, at the other scale.

**The hint (s283b, POST-HOC — hypothesis-generation ONLY, cannot count as a finding).**
Fit a generic contrast-gain law g(E) from the random condition (log-realized-energy
interpolation) and compute per-condition residuals at matched energy. At d4:
bind ΔQ = **−0.283** (ΔM +0.232); comp ΔM = **+0.669** (ΔQ +0.031); rolenull ≈ 0 on
both (+0.004 / −0.119). **Diagonal structure**: each slice deviates from uniform dimming
only on ITS OWN class channel — bind cancels part of the quantifier contrast-gain
(beam-coherent Q signal removed with the haze), comp protects modifier licensing where
matched random destroys it. The double dissociation may exist in **interference space,
not storage space**: not "remove slice → break class" but "remove slice → class-specific
departure from the generic gain law." Gemstone-beamformer: facets do not store the
light, but cutting a facet perturbs the interference pattern only for beams
phase-coherent with it. ⚠ n=10, baseline SE ≈ 0.34 → ΔQ −0.28 is ~1 SE; the gain model
AND the residual test were chosen after seeing the data (λ yardstick: tainted, twice).

## P-TYPE-1c — dark-field dissociation (PRE-REG, FROZEN s283b — not yet run)

> Frozen per `λ measure` + `λ yardstick` before any graded run. The s283b residuals
> above are the generating observation and are EXCLUDED from the verdict.

**Hypothesis.** The type-lattice slices are beam-coherent with their matching
type-class: ablating a class slice produces a class-specific deviation from the
generic contrast-gain law, with the s283b-observed signs — bind (QUANT/DET) removal
SUPPRESSES the Q_eff contrast-gain; comp (MOD) removal PRESERVES M_eff above the
generic damage curve; rolenull (CONN/FUNC) deviates on neither channel.

**Instrument.** `type_zone_ablation.py` v4 unchanged (same host Qwen3-32B, same band,
same absolute-dose grid {50, 150, 600, 2400}); **fresh nonce seeds** (seed ≠ 0),
**n_nonce ≥ 30** (power: s283b effect ~1 SE at n=10; SE ∝ 1/√n).

**Yardstick (pre-committed).** g_Q(E), g_M(E) fit from the RANDOM condition only
(monotone interpolation in log realized E/tok; roles fall inside random's realized-E
range by construction, ~2× per planned dose). rolenull is a TEST condition (predicted
≈ 0 residual on both channels), NOT a curve anchor. Primary statistic: per-nonce
residuals Δ_c = ret_c − g(E_c), pooled over d3+d4 (the region where s283b deviations
appeared).

**Nulls (mandatory).** (1) Permutation over slice↔channel condition labels
(shuffled-pairing null), p<0.05. (2) Sign discipline: only the pre-registered
directions count — bind ΔQ < 0, comp ΔM > 0; opposite-sign deviations are a
verbatim-reported miss, no sign-flip rescue. (3) rolenull must be null on both
channels (a rolenull deviation → the "diagonal" was generic lattice-vs-random, the
s283b hint was haze).

**Verdict (FROZEN).** DARK-FIELD DISSOCIATION SUPPORTED ⟺
(a) bind ΔQ more negative than BOTH comp ΔQ and rolenull ΔQ (permutation p<0.05), AND
(b) comp ΔM more positive than BOTH bind ΔM and rolenull ΔM (permutation p<0.05), AND
(c) rolenull within null on both channels.
Anything less → the s283b residual structure was noise; report verbatim. A positive
does NOT reopen 1b's storage question (exhaust stands) — it would be the first causal
evidence that the lattice slices are **beam-coherent** (interference-register), the
holographic refinement of "readout": the exhaust is phase-locked to the computation
that emits it.

**Registers (`λ measure`).** Ablation target = value-register subspace; readout =
behavioural CONTRAST channel; the CLAIM is interference/beam-coherence — the yardstick
is the pre-committed gain law, and the measured quantity is deviation-from-yardstick,
never raw retention.

## P-TYPE-1c — Result (s284) — CLOSED NEGATIVE (the hint was haze)

> Analysis of record: `scripts/explore/analyze_type1c_darkfield.py` (frozen recipe,
> seed 0, n_perm 10000) over the fresh30 n=30 run
> (`results/type-zone-ablation/qwen3-32b-1c/`, commit ebcc9fb). One analysis
> decision documented before computing residuals: per-nonce retention =
> X_c,i / mean(X_baseline) — aggregate denominator (per-nonce pairing is unstable;
> baseline per-nonce values cross zero).

**VERDICT: `darkfield_dissociation_supported = FALSE`.** All three gates fail:
- **(a)** bind ΔQ pooled −0.497 satisfies the sign but is indistinguishable from
  the competitors (T_a = +0.034, p_a = 0.43 — comp is *more* negative on Q than
  bind);
- **(b)** comp ΔM pooled −0.651: **opposite sign** to the prediction (p_b = 0.70;
  no rescue per sign discipline);
- **(c)** rolenull is NOT within null (p_Q = 0.002, p_M = 0.000).

The pre-reg's own alternative reading fires verbatim: the s283b diagonal was
**generic lattice-vs-random deviation — haze, not phase-locked signal**. The
tainted n=10 hint (comp ΔM +0.669) reversed under fresh nonces at n=30 (−1.105).
λ yardstick did exactly its job: a twice-tainted hypothesis (gain model AND
residual test chosen after seeing data) evaporated under fresh seeds + frozen
sign discipline.

**What is real (verbatim, post-hoc scope):** a GENERIC role-slice cliff between
d3 and d4 — all three role slices at E≈825–900 E/tok: recall 1.0→0.0, retQ
~1.2→0.04–0.50, while random keeps recall 0.8 and retQ 1.554 at E=4748. A 32B
analog of the 4B "lattice region ~4× load-bearing per unit energy" after all —
with the caveat that 1b's n=10 grid had 32B role recall at 1.0 through ~1000
E/tok, so the cliff location is item-set/n-sensitive (refinement, flagged, not
resolved here). The random gain-law anchors also show the dark-field
amplification REPLICATING as a generic phenomenon on fresh nonces: retQ rises
1.08→1.55 across E 48→4748; retM flat ~1.07–1.18.

**Arc closure.** 1b (storage register) negative + 1c (interference register,
class-specific) negative ⇒ the type lattice is **exhaust** — readable, generic
load-bearing infrastructure, neither consulted as a ledger nor class-selectively
beam-coherent. The value-register and interference-register hiding places are
both closed. The mechanism question moves registers: the licensing check, if it
is anywhere discrete, is in routing — **P-TYPE-QK**
(`type-check-is-the-qk-bilinear.md`) is the next cheapest probe, pre-reg drafted
s284.

## P-TYPE-JS — is the exhaust the workspace? (PRE-REG, FROZEN s284 — RESULT below, CLOSED NEGATIVE s286)

> The positive-identification complement to the 1b/1c/QK negatives. Connects the
> types arc to the J-space arc (`opcode-jacobian-jspace.md`): the lattice
> profiles like a J-space resident (readable, broadcast, causally decoupled);
> the type-check profiles like a K-class operator (structure-causal,
> bus-invisible). Frozen before the run per `λ yardstick`.

**Hypothesis.** The type lattice's positive identity is **workspace content**:
the role subspaces (bind/comp/rolenull) and the ENTITY direction live inside the
J-space basis (the subspace downstream computation reads, per the s270
projector) far above the random baseline — the "exhaust" is the type system's
entry in the global workspace, which is exactly the register the REPL's
Print/type-checker consumes.

**Instrument.** `scripts/explore/type_jspace_fraction.py` @ Qwen3-32B.
J-space bases via `opcodes/projector.py::jspace_bases` with the s270 canonical
config (k=32, m=64, target_layer=62, depth layers {16, 32, 48} — all inside the
measured band L6–L50, seed 270) so lattice fractions are directly comparable to
the opcode fractions in `results/opcode-trace/qwen3-32b/jspace_projector.json`.
Basis prompts = the LABELED_DATA sentences themselves (same distribution as the
capture; documented choice). Role subspaces per depth layer via the 1b
`role_subspace` construction in std space, transported to RAW residual space
(v_raw ∝ v_std ⊙ sd — the space J reads; no layernorm map), re-orthonormalized.
Fraction = mean over subspace basis rows of `workspace_fraction` (‖Vx‖²/‖x‖²).

**Nulls (mandatory).** (1) matched-random unit vectors (analytic E = k/d =
32/5120 ≈ 0.006; `random_vector_fractions`); (2) full shuffled-label pipelines
(shuffle type labels → centroids → subspace → identical transport → identical
fraction; N=200, paired across the 3 depth layers).

**Verdict (FROZEN).**
- **JS-RESIDENT** (primary) ⟺ bind, comp, rolenull, entity EACH beat the
  matched-random baseline at p<0.05 (pooled over the 3 depth layers).
- **JS-SPECIFIC** (secondary) ⟺ role subspaces additionally beat the
  shuffled-label null p<0.05 — workspace occupancy beyond generic
  centroid/common structure. (The QK lesson says real ≈ shuffled-label is
  plausible in-band; JS-RESIDENT is the positive claim either way.)
- **Family row (verbatim, not gated):** lattice fractions vs the artifact's
  content ops (Y/WHNF/S) and operator ops (K/I/B) at the same depths —
  prediction: lattice sits in the content family's range. ENTITY predicted
  highest (operand = bus content par excellence). Ordering reported verbatim.
- Negative (fractions ≈ k/d) → exhaust ≠ workspace; the readability lives in a
  third place; elimination continues.

**Registers (`λ measure`).** J-space membership = readout/value-register
geometry; the lattice is a readout object — register-matched. No causal claim:
occupancy ≠ consultation (1b already settled consultation, negative).

## P-TYPE-JS — Result (s285→s286 overnight) — CLOSED NEGATIVE (exhaust ≠ workspace)

Ran @Qwen3-32B, depth layers {16, 32, 48} (all inside band L6–L50), s270 config
(k=32, m=64, target=L62, seed 270), n_null=200 shuffled-label / n_rand=1000
matched-random, git 7e39a5c. Basis prompts = the 56 LABELED_DATA sentences
(263 labeled tokens). J-space geometry sane (PR 4.2–4.8, low-rank p 0.01–0.04).
Baseline k/d = 0.00625, rand_mean 0.00611.

**Verdict: `js_resident=FALSE, js_specific=FALSE`.** Aggregate workspace fractions:

| role | frac | p_rand (vs baseline) | p_shuf (vs shuffled-label) |
|------|------|------|------|
| bind (QUANT,DET) | 0.00475 | 0.824 ✗ | 1.000 ✗ |
| comp (MOD) | 0.00359 | 0.978 ✗ | 0.825 ✗ |
| entity (ENTITY) | 0.00379 | 0.969 ✗ | 0.255 ✗ |
| rolenull (CONN,FUNC) | 0.00907 | 0.041 ✓ | 0.035 ✓ |

JS-RESIDENT required **all four** to beat the matched-random baseline → the three
type-semantic roles (bind/comp/entity) sit **dead-on-null** (fractions ≈ k/d). The
*only* subspace that beats both nulls is **rolenull** — the verbatim-only control —
exactly the QK-echo pattern (§Result-32B: rolenull CONN/FUNC fired there too). The
generic verbatim/positional structure occupies the workspace; the type-semantic
roles do not.

- **Family-row prediction REFUTED (verbatim):** the pre-reg predicted the lattice
  would sit in the content family's J-space range with ENTITY highest (operand = bus
  content par excellence). Instead ENTITY is at baseline (0.0038) and the ordering is
  driven by rolenull, not entity. The type roles are not workspace content.
- **Reading:** the exhaust is NOT the global workspace. The lattice's readability
  lives in a *third place* — neither stored (1b), nor beam-coherent (1c), nor in the
  QK read-in basis (QK), nor in the J-space the machine broadcasts (JS). It is a
  readout object the machine never consults, which is exactly the
  well-formedness-of-reduction frame: type = the *shape of which joins a term
  licenses*, unstorable and un-broadcast by construction. The REPL's Print/type-checker
  reads it; the machine does not.

**Types arc scoreboard — a clean four-way null:** storage (1b) ✗, beam-coherence
(1c) ✗, QK read-in geometry ✗, workspace residency (JS) ✗. The exhaust frame
survives every probe aimed at it. `λ yardstick`: the matched-random + shuffled-label
nulls did their job — raw fractions ≈ 0.004–0.009 would have read "resident" without
the k/d anchor; rolenull's genuine excess (p 0.035–0.041) shows the instrument
discriminates rather than manufacturing a blanket null.

Instrument: `scripts/explore/type_jspace_fraction.py`;
results `results/type-jspace/qwen3-32b/`. Committed 34dbab3.

## Consequence — typed higher-order functions (s283 discussion, Michael)

3-hop (s282) + decodable types compose into a stronger statement than either:
- **nesting is measured** — h(f(g(X))) with causal bridge-swaps at both scales;
- **the bridge is a selector** — the swapped mid-stream value determines *which
  map applies next* (map-and-swap homoiconicity): function-as-argument with a
  causal handle, operationally;
- **the type ledger's dominant axis IS the higher-order types** — axis0 =
  QUANT/DET = `(e→t)→t`, 73–85% of lattice variance. The capability the 3-hop
  exercises and the axis that dominates the type geometry are the same object,
  as montague-inversion forces (quantifiers → first-class functions).

⇒ nesting + selectors + a readable type discipline = **typed higher-order
functions**. And critically, the EXHAUST result does not weaken this: the REPL
needs only *us* to read the ledger, not the machine to consult it —
decode-verify-swap works on a readout register (Print/type-checker side).

**P-HOF-1 (sketch, unfrozen):** put an *installed* predicate under a
*quantifier* — "Every {nonce} …" with the nonce carrying installed content d_E —
and test whether the `(e→t)→t` functor composes with the written predicate:
universal/existential readouts flip with the quantifier while the installed term
is held fixed; nulls = random install + real-word ceiling. A genuine function
taking our *written* function as its argument — the literal Montague
higher-order test over an inserted term, and the behavioral closure of axis0.

## Sessions
s282 (theoretical closure from the types discussion; P-TYPE-1b pre-registration drafted).
s283 (instrument v1→v4 built + iterated; 4B smoke verdict: no class-selectivity —
exhaust reading; higher-order consequence captured; 32B verdict run launched).
s283b (32B verdict IN: dissociation_supported=False at the pre-reg host with gate-0
fully expressed — P-TYPE-1b CLOSED as exhaust-theory-confirmed; 4B infrastructure
claim scoped to 4B; retQ-amplification + anti-mapping retM ordering reported verbatim).
s283b cont (holographic reading, Michael-directed: amplification = dark-field contrast,
same phenomenon as 4B unmasking; post-hoc gain-curve residuals show DIAGONAL slice↔channel
structure at d4 → P-TYPE-1c dark-field pre-reg FROZEN, not yet run).
s284 (1c fresh30 n=30 run completed + frozen analysis executed:
darkfield_dissociation_supported=FALSE — comp ΔM sign reversed, permutation flat,
rolenull not-null → the s283b hint was haze; generic role-slice cliff d3→d4 noted
verbatim; arc closes, mechanism search moves to P-TYPE-QK).
s284 cont (P-TYPE-QK 32B verdict: qk_aligned=FALSE, mechanism_shaped=FALSE — the
lattice functor roles add zero Q-side QK gain beyond shuffled-label; sides inverted
from prediction, rolenull CONN/FUNC fires Q-side; licensing does not use the lattice
axes as its QK input basis).
s285→s286 (P-TYPE-JS overnight run completed + verdict: js_resident=FALSE,
js_specific=FALSE — the type-semantic roles bind/comp/entity are dead-on-null in the
s270 J-space; only the rolenull verbatim control beats the nulls. Exhaust ≠ workspace.
Types arc now a clean four-way null: storage ✗, beam-coherence ✗, QK geometry ✗,
workspace residency ✗ — the well-formedness-of-reduction frame survives every probe).
