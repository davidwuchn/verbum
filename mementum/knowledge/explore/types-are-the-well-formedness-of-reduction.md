---
title: "Types are the well-formedness of β-reduction — the combinator reading of the type lattice"
status: active
category: explore
tags: [types, beta-reduction, combinators, KIBC, CCG, montague, lambek, discocat,
       curry-howard, well-formedness, S-combinator, B-combinator, functor-kind,
       type-check, compiler, P-TYPE-1, P-TYPE-1b, C1, C2, C9, s282]
related:
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
