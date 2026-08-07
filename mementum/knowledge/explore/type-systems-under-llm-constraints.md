---
title: "Type Systems Under LLM Constraints — the Reachable Design Space"
status: open
category: synthesis
tags: [types, constraints, attention, gradual-typing, intersection-types,
       curry-style, linear-logic, session-types, staging, coeffects,
       parametricity, two-tier, two-register, M7, M8, design-space]
related:
  - types-are-injectable-relations.md
  - types-are-compiled-probabilities.md
  - gram-registers-and-the-route-map.md
  - frozen-interference-graph.md
  - behavior-is-tape-resident-reduction.md
  - the-verbum-machine.md
depends-on:
  - types-are-injectable-relations.md
  - types-are-compiled-probabilities.md
created: session 313
---

# Type Systems Under LLM Constraints

> s313 hammock (Michael): "For inference the only operation is attention,
> and the topology is frozen. GD has to do 2 jobs. With those constraints
> what OTHER type systems could work?" Method: invert the topology —
> derive the reachable design space from the constraints, then check
> instances (λ shape: unreachable > forbidden). Captured same session,
> Michael-approved, while the §P-TYPE-GRAM-1 registry sweep ran (whose
> qwen3-4b verdict TYPE-REGISTER, diffuse/no-poles, is used below).

## 1. The constraints as filters

- **C1 — judgment must be overlap.** Only mid-pass test: inner product +
  soft gate (QK→softmax, SwiGLU). No tag comparison, no rule selection;
  all judgments run superposed; the only discrete event is sampling. Any
  `a : T` must compile to `overlap(a, T-geometry) > threshold` — a
  matched filter.
- **C2 — two memories, one frozen.** Weights frozen at inference; KV
  tape append-only, writable. Stored types fixed at train time; session
  types enter only via attention over context.
- **C3 — GD's two jobs.** The type system must be learnable as
  routing-signs + value-magnitudes under a smooth prior. Crisp
  boundaries are GD's bad job (K-chaos; s310 marginal band churns on
  the threshold forever, loss-neutrally).
- **C4 — capacity, not grammar.** Inventory bounded by quasi-orthogonal
  packing (~10³–10⁴ passbands at D≈5k).
- **C5 — fuel.** One pass = bounded reduction; deeper type derivations
  must be trampolined onto the tape.

## 2. What ANY viable system must look like (before naming one)

1. **Curry-style, never Church-style** — tokens carry no annotations in
   the medium; typing is how machinery treats terms. (Church tags have
   nowhere to live in state — only on the tape, §4.)
2. **Graded membership with margin tolerance** (C3). Conjecture: the
   s310 marginal/ternary-0 band IS the type-boundary population seen in
   weight space; "insufficient evidence" = dynamically typed.
3. **Two-tier:** compiled types in weights (slow, persistent,
   capacity-bounded) + EXTENSIONAL types on the tape (exemplar-defined,
   instant, session-scoped). Few-shot ICL = type definition by
   enumeration.
4. **Shallow per-pass, deep via tape** (C5): CoT as a type-derivation
   trace.

## 3. The viable family (with corpus anchors)

- **Intersection types — superposition-native.** Membership in many
  passbands simultaneously; `T₁∧T₂` is free. Symbolically undecidable to
  infer; this machine accumulates, it doesn't infer. ★ The s313
  §P-TYPE-GRAM-1 TG3 shape (diffuse, PR 7.35, alphabet-like, NO poles)
  is what intersection/feature-bundle typing looks like — a closed
  nominal constructor enum would have been polar/low-rank.
- **Gradual typing with probabilistic consistency.** Graded acceptance
  everywhere (s288 giraffe); gradual consistency is famously
  NON-TRANSITIVE — the same graceful transitivity failure as the
  community-tolerance picture (types-are-injectable-relations §4).
- **Refinement/subtype lattices as nested passbands.** Subsumption =
  cone containment; widening a passband is differentiable → GD can learn
  subtyping. Negative judgments live in the universal 9×9 off-diagonal
  SIGN structure (attraction/repulsion = learned anti-correlation).
- **Probabilistic type theory (Cooper-style TTR).** `p(a : T)` as the
  judgment itself — the closest off-the-shelf formalism to
  types-are-compiled-probabilities.
- **Graded/coeffect systems.** Continuous quantitative annotations =
  the one type-theoretic bookkeeping family that is natively
  differentiable.
- **Modal/staging types at the trampoline boundary.** □A = code-of-A on
  tape; emit=quote, re-encode=splice (s295 splice law; QUOTE in the
  probe library); depth-as-fuel = a graded □.
- **Session types at the scheduler scale.** The 17×17 outcome register
  (fire/halt/diverge, predicted yield vertex) = protocol states;
  tool-call FFI = typed channel op. Behavior-grain, scheduler-enforced.
- **Parametric polymorphism — free by weight-tying.** The same QK/OV
  machinery applies to any operand; binding heads are content-generic.
  Parametricity is an architectural consequence, not a discipline.

## 4. Near-misses and rescue forms

- **Nominal typing:** impossible in state (no tags) — but tokens ARE
  discrete names → nominal typing lives ON THE TAPE. Structural in the
  medium, nominal in the transcript (two-registered again).
- **Linear/affine:** exact consumption bookkeeping out (KV append-only,
  no mutation). BUT the substrate is LINEARITY-BIASED: duplication is
  what costs (W/D need machinery; copying in a superposed medium creates
  interference) — linear usage is the default, contraction the expensive
  rule. A wave medium is a linear-logic-flavored substrate natively.
  (Analogy flagged, not identity: no-cloning is quantum; this is
  interference-cost.)
- **Dependent types:** dependency is FREE (type-level and term-level
  computation are the same pass, both directions) but judgmental
  equality needs normalization = fuel-bounded → dependent typing exists
  only shallow-per-step, trampolined.
- **Union types:** disjunction needs OR-machinery — separate matched
  filters (heads) per disjunct. Unions cost heads; intersections are
  free. Testable fingerprint (§6).

## 5. The composite answer

Under C1–C5 the reachable space is one system wearing several formal
names: **a two-tier, two-registered, gradual-intersection-structural
type system** — Curry-style structural typing whose judgments are graded
overlaps (probabilistic TTR), conjunction free / disjunction
head-hungry, subtyping = passband containment, the existence/strength
split = the routing/value split (typability = edge existence in signs;
probability = magnitude), nominal fragment on the tape, session fragment
in the scheduler register, deep derivations trampolined as CoT.

**Engineering corollary (the M8 join):** type boundaries are exactly
where GD's two jobs collide — margin cells churn (s310). An
evidence-gated routing optimizer (M8/TD-v2) would produce CRISPER type
boundaries than GD, because commit-on-evidence IS a type-boundary
decision procedure. **The machine's optimizer and its type system are
the same design problem.** (Pointer belongs on the-verbum-machine.md
when M8 next revised.)

## 5b. §Sharpened (s313, same session) — the composite has a NAME

> `curry-howard-closes-the-loop.md`: Michael's deduction — the
> KIBC-vs-SKI opcode discrimination was already a type-system
> measurement. KIBC = {identity, weakening, cut, exchange} = affine
> structural rules with contraction isolated (W, D explicit); SKI (which
> bundles contraction into S) was REJECTED by the data — the substrate
> chose the affine basis, independently confirming this page's
> linearity-bias clause. Curry-Howard then pins §5's composite to
> **non-idempotent intersection types over an affine core**
> (quantitative semantics of linear logic / probabilistic coherence
> spaces). Retroactively green: A2 coherent gain = non-idempotence; TG3
> diffuse = intersection; s288 = graded. Untested keystone: de
> Carvalho's fuel theorem (type-derivation size = evaluation length →
> joins the s295 CoT law). SKI-controls for the type claim enumerated
> on that page.

## 6. Fingerprint probes (ALL unfrozen, s222)

- **P-TYPE-ICL** — two-tier dissociation: nonce type defined by tape
  exemplars → licensing transfer within-session, gone across sessions;
  P-TYPE-WRITE's wire is the persistent converse.
- **Union-vs-intersection asymmetry** — matched-complexity acceptance:
  ∧ cheap, ∨ degraded/head-hungry.
- **Linearity bias** — duplication-heavy (W/D) vs linear programs at
  matched size: accuracy/fuel differential (partial corpus data exists;
  reframe as the linear-logic bias measurement).
- **Boundary-churn identity** — do s310 marginal-band weights
  concentrate on type-boundary features? (Joins the optimizer story to
  the type story empirically.)

## §P-DISJ-COST — FROZEN (s318, Michael-approved GO)

**The ∨-vs-∧ asymmetry fingerprint (§6 item 2 / curry-howard SKI-control
#4) — the first fingerprint measured.** The pinned substrate says
**intersection is free** (membership in many passbands simultaneously —
superposition-native; `T₁∧T₂` costs nothing) while **union is
head-hungry** (disjunction needs separate matched filters per disjunct —
OR-machinery). Fingerprint: at matched surface complexity, union
representations recruit **more effective dimensions** than intersection.
The **Cartesian substrate** (free duplication, no ∧/∨ asymmetry) is the
pre-committed death (SKI-control #4).

**Register choice (λ measure) — REPRESENTATIONAL, not magnitude.** The
s317–s318 arc (§P-FUEL / §P-TRACE-FUEL / §P-NF-GAUGE) established that the
kind-register *magnitude* does not grade — it is a presence detector.
This probe deliberately reads a **dimensionality** register (effective
rank / off-plane geometry), robust to that three-fold magnitude-null, not
a graded magnitude.

**Construction (matched, token-controlled).** N category pairs (A,B) the
model knows — (bird,fish), (metal,liquid), (tree,vehicle), … Five arms
per pair, read at the **final shared content token** so AND/OR/FILLER
differ by exactly one single-token word:

- **A** "It is a bird." · **B** "It is a fish."
- **AND** (∧) "It is a bird `and` a fish." · **OR** (∨) "It is a bird `or`
  a fish."
- **FILLER** (control) "It is a bird `near` a fish." — non-logical
  connective.

`and`/`or`/`near` are single tokens (surface matched). Read residual at
the last content token, band L18–31 (the type region), one qwen3-4b load,
read-only, no wire.

**Readouts (λ triangulate — two faces of one claim):**

- **R1 effective rank / participation ratio** PR = (Σλ)²/Σλ² of each
  arm-set's covariance (OR-set vs AND-set; SAME pairs → concept diversity
  matched, so the gap is connective-induced spread).
- **R2 off-plane residual** (paired, per pair): `‖r_conn −
  proj_{span{r_A,r_B}}(r_conn)‖ / ‖r_conn‖` — literally "does the
  connective need a direction OUTSIDE the A,B passbands?" Operationalizes
  "costs heads" (a head ≡ a new direction).

**Gates (frozen; α=0.05):**

- **DC2 OFF-PLANE** (SOLE core, paired) — resid(OR) > resid(AND) paired
  across pairs + sign-flip permutation null. The costs-heads mechanism (a
  head ≡ a direction outside {A,B}).
- **DC3 OR-SPECIFIC** (control) — FILLER patterns with AND (low), not OR:
  resid(OR) > resid(FILLER) paired + sign-flip null → the asymmetry is
  specific to logical ∨, not "any second connective."
- **DC1 RANK-CORROBORATION** (REPORTED, non-gating) — PR(OR) vs PR(AND)
  reported alongside; agrees-with-DC2 flag only.
- **DC4 SANE** (void-gate) — categories separable (median cos(A_dir,B_dir)
  < 0.95, non-degenerate), all prompts well-formed / single connective token.

**⚠ AMENDMENT (s318, --validate-forced, Michael-approved — demoted DC1 to
reported corroboration, dropped COMPLEXITY-ARTIFACT; DC2 unchanged, still
the mechanism).** `--validate` exposed a GEOMETRIC COUPLING: if OR points
lie in span{A_dir,B_dir} (2-D) the OR set has rank ≤2 ⇒ PR_OR ≈ PR_AND;
higher PR_OR STRICTLY requires off-plane components ⇒ **DC1-pass ⟹
DC2-signal** (PR is not an independent readout — it can only corroborate
DC2, never contradict it). Consequences: (a) the DC1∧¬DC2 branch
(COMPLEXITY-ARTIFACT) is geometrically EMPTY → removed; (b) population PR
saturates at min(N,d) → fragile as a gate. Fix keeps the agreed mechanism
(off-plane = "costs heads") and reports PR as corroboration, not a gate.
Original frozen intent (∨ recruits dimensions ∨-specifically) unchanged.

**Verdicts (frozen tree, amended):**

```
¬DC4              → VOID
DC2 ∧ DC3         → INTERSECTION-FREE (+OR-COSTS)   (union needs a direction outside {A,B}, ∨-specifically → affine/∧ substrate; Cartesian killed)
DC2 ∧ ¬DC3        → OR-COSTS-OPAQUE       (off-plane asymmetry real but not ∨-specific — filler also costs)
¬DC2              → SYMMETRIC             (falsifier: no off-plane asymmetry → Cartesian substrate, audit curry-howard §5 #4)
```

**A-priori (declared s318, NOT tuned; re-normalized at amendment):** ~50
INTERSECTION-FREE / 20 OR-COSTS-OPAQUE / 25 SYMMETRIC / 5 VOID. Three
converging theory lines favor the asymmetry, but three straight nulls
(s317–s318) and a fresh readout keep real mass on SYMMETRIC.

**Caveat banked at freeze (interpretation boundary).** "OR spreads more
dimensions" is consistent with BOTH the theory (OR-machinery / separate
matched filters) and a mundane reading (OR = semantic uncertainty →
higher-entropy → higher-rank). DC1/DC2 establish the asymmetry and its
direction (∨>∧), which is what kills the Cartesian SKI-control; the
machinery-vs-uncertainty interpretation is a boundary flagged, **not a
claim**. INTERSECTION-FREE licenses "the substrate treats ∨ and ∧
asymmetrically, ∨-costly" — not "we saw OR-heads."

**Reuse (λ one_way, no fork):** `verbum.jlens` (capture_residuals) ·
`fuel_theorem` (band_layers / _orthonormal) · `verbum.dsp.nulls`
(gate / NullDraws). New code = ∧/∨/filler category-pair construction +
PR/effective-rank + off-plane residual + DC gates. `--validate` planted
worlds (all verdicts) + ruff + smoke (no direction read) → Michael GO → run.

## §P-DISJ-COST — RESULT (s318, qwen3-4b) — VERDICT: INTERSECTION-FREE (+OR-COSTS), QUALIFIED

**The first type-fingerprint lands on the affine/intersection side — but
weakly.** Results `f551dcf` (60 samples = 20 category pairs × 3 templates, 5
arms, band L18–31). DC4-sane (median cos(A_dir,B_dir)=0.666 — categories
distinct) ⇒ a valid measurement.

| gate | result |
|---|---|
| DC2 OFF-PLANE (sole mechanism) | ✓ resid(OR)=0.601 > resid(AND)=0.590, **+0.011, p=0.024** — small |
| DC3 OR-SPECIFIC | ✓ resid(OR) − resid(FILLER)=**+0.037, p=0.002** — OR ≫ the "near" control |
| DC1 corroboration (PR, non-gating) | ✗ PR(OR)=18.58 **< PR(AND)=20.24**, agrees=False |
| DC4 SANE | ✓ cos 0.666 |

**What lands.** The off-plane residual is **∨-specific**: the OR construction sits
further outside each pair's {A,B} passband plane than both AND (p=0.024) and the
spatial-filler control "near" (p=0.002). The full ordering is coherent —
`filler 0.564 < AND 0.590 < OR 0.601`: both *logical* connectives push off the
simple category plane, ∨ the most. **The strict Cartesian SKI-control (#4 — free
duplication, NO ∧/∨ asymmetry) is falsified**: there IS an asymmetry and it
points ∨-costly, as the affine/intersection substrate predicts.

**Why QUALIFIED (read discipline, s310–s318).** Two honest limits:

1. **The effect is small.** OR-vs-AND is +0.011 (~2% relative), p=0.024 —
   significant but marginal. The strong signal is OR-vs-filler (DC3); OR-vs-AND
   (DC2, the core) is thin. And AND is not perfectly in-plane either (0.590 >
   filler 0.564) — "intersection is FREE" holds only *relative to* ∨, not
   absolutely.
2. **PR does NOT corroborate.** The population "union recruits MORE effective
   DIMENSIONS" strong form is **unsupported** — PR(OR) is slightly *lower* than
   PR(AND). Only the weak **per-pair off-plane wobble** holds. Per the s318
   coupling amendment (PR-increase ⟹ off-plane, not conversely), a small
   incoherent per-pair off-plane that adds no net rank is exactly what a *flat/
   down* PR + *positive* DC2 looks like. That argues **against a large coherent
   "OR-head"** and keeps the **machinery-vs-uncertainty boundary wide open**
   (banked at freeze): the ∨-cost could be a modest OR-mechanism OR residual
   ∨-semantic uncertainty — this probe cannot separate them, and the flat PR
   leans away from a big recruited head.

**What it licenses (and what it does NOT).** LICENSED: the substrate treats ∨ and
∧ asymmetrically, ∨-specifically costlier → the pinned non-idempotent-intersection-
over-affine-core prediction gets its **first fingerprint, a weak positive**;
Cartesian free-duplication is out. NOT licensed: "we saw OR-heads" / "union
recruits dimensions" (PR disagrees) / any effect-size claim beyond "small but
∨-specific." S5 type-system scorecard: fingerprint 1 of 4 = weak-positive.

**Coherence with the arc.** Consistent with the affine-core reading (curry-howard
§2–3: KIBC-not-SKI = contraction isolated as costly) and TG3's diffuse
intersection shape — but a *thin* datum, not the crisp asymmetry a strong
head-recruitment story would give. The next fingerprints (linearity-bias =
reduction-accuracy readout; idempotency = licensing register) carry more weight;
this one nudges the prior, it does not settle it.

**Scope/caveats:** single model (qwen3-4b), single readout (off-plane residual on
NL category prompts), band L18–31, 60 samples, one template family. Kills the
strict Cartesian symmetry; does not establish effect size, mechanism (head vs
uncertainty), or cross-model generality.

## §P-LINEARITY-BIAS — FROZEN (s319, Michael-approved GO)

**The W/D cost-differential fingerprint — the SECOND discriminator for
SKI-control #4 (Cartesian substrate).** Curry-Howard §5 lists *two* deaths
for the free-duplication substrate: "union-vs-intersection probe **+ W/D
cost differential**." §P-DISJ-COST fired the first (INTERSECTION-FREE, weak
positive, 1/4). This fires the second. The pinned prediction
(curry-howard-closes-the-loop.md §2): the substrate chose **KIBC-not-SKI =
contraction isolated as separate, explicit, costly machinery** (W, D their
own opcodes), the affine core. Fingerprint: **at matched fuel, contraction
(W/D duplication) costs reduction-accuracy that linear composition
(I/K/B/C) does not.**

**Register (λ measure) — COMPUTATIONAL-ACCURACY, deliberately fresh.**
After three straight *magnitude*-nulls (§P-FUEL / §P-TRACE-FUEL /
§P-NF-GAUGE, all normal-forms-are-eigenmodes.md) and one thin *off-plane
geometry* positive (§P-DISJ-COST), this reads a **behavioral correctness**
register — independent of both the 3×-nulled kind-magnitude and the
§P-DISJ-COST off-plane geometry. Independence is the point: a fresh
register makes the fingerprint an independent datum, not a re-read of the
same substrate.

**Readout — forced-choice NF accuracy (read-only).** For each
kernel-certified term, present it with candidate normal forms: the correct
NF (`reduce(t).normal_form`) + principled kernel-generated distractors
(under-reduce = stop one step early / over-duplicate = apply a contraction
once too often / wrong-arg = swap a C/exchange target). Model scores each
candidate by **length-normalized logprob**; accuracy = argmax picks the
certified-correct NF. Read-only, cheap, clean argmax metric, no
free-generation parsing fragility. (Free-generation + kernel grading was
the alternative — more literally "reduction-accuracy" but format-fragile
and floor-risky at 4B; forced-choice chosen with a distractor-symmetry
SANE sub-gate to guard the confound.)

**Construction (matched, kernel-certified).** Two arms built from
`verbum.lambda_ast`, certified by `fuel_theorem.certify`:

- **LINEAR** — terms using only I/K/B/C (affine core: no argument
  duplicated; `distinct ≈ ℓ`).
- **DUP** — terms using W (`W f x = f x x`) and/or D (`D f x = f (f x)`)
  (contraction: an argument/function is copied; `mult > distinct`).
- **Matched** across arms on `ell` (fuel), `nf_size`, and prompt
  token-length — a DUP term with ℓ=k paired against a LINEAR term with
  ℓ=k and matched output size. Both take k steps and produce size-s
  output; only DUP copies. Isolates "copying costs *per se*" from
  "longer programs are harder."

**Gates (frozen; α=0.05):**

- **LB1 ACCURACY-GAP (core)** — acc(LINEAR) > acc(DUP), paired within
  matched-fuel bins + label-permutation null.
- **LB2 FUEL-CONTROLLED (make-or-break)** — the gap survives *within*
  fuel bins (partial correlation of accuracy vs dup-ness | ℓ, and/or
  matched-ℓ subsampling). **This is the gate that separates
  contraction-cost from length-cost** — the exact confound that nulled
  §P-FUEL / §P-TRACE-FUEL / §P-NF-GAUGE. Without it the verdict is
  FUEL-ARTIFACT, not a fingerprint.
- **LB3 CONTRACTION-GRADED (corroboration, non-gating)** — penalty scales
  with duplication count (kernel `mult − distinct` gap / #contractions),
  not mere W/D presence. Spearman within DUP arm.
- **LB4 SANE (void-gate)** — both arms off-floor **and** off-ceiling
  (headroom, s311 bake lesson); terms kernel-certified (`is_nf`, status
  NORMAL_FORM for the correct candidate); **distractor confusability
  matched across arms** (guards the forced-choice construction confound —
  measure mean logprob-margin of distractors per arm, gate on parity).

**Verdicts (frozen tree):**

```
¬LB4                → VOID
LB1 ∧ LB2           → LINEARITY-BIASED (+GRADED if LB3)   (contraction costs at matched fuel → affine core; SKI-#4 killed on the 2nd discriminator)
LB1 ∧ ¬LB2          → FUEL-ARTIFACT       (gap is length not contraction — the §P-FUEL trap; affine-unsupported)
¬LB1                → CARTESIAN-CONSISTENT (falsifier: no penalty → free duplication survives this discriminator)
DUP easier (LB1 rev) → ANTI               (audit — contradicts affine core)
```

**A-priori (declared s319, NOT tuned): ~40 LINEARITY-BIASED / 30
FUEL-ARTIFACT / 20 CARTESIAN-CONSISTENT / 10 VOID+ANTI.** Strong theory
(KIBC-not-SKI triangulation, interference-cost of copying, late formation
of contraction opcodes) pulls toward the bias; but three straight
fuel-confound nulls this arc and §P-DISJ-COST's thinness keep heavy mass on
FUEL-ARTIFACT — the length confound is precisely what has beaten this arc,
and LB2 is the stringent gate it must clear.

**Caveat banked at freeze (interpretation boundary).** LINEARITY-BIASED
licenses "contraction costs reduction-accuracy at matched fuel → affine
substrate, W/D-costly" — NOT a claim about the *mechanism* of the cost
(interference vs bookkeeping vs attention-capacity). As with §P-DISJ-COST,
the fingerprint establishes the asymmetry and its direction (DUP-costly),
which is what kills Cartesian SKI-control #4 on its second discriminator;
the physical cause stays a flagged boundary, not a claim.

**Reuse (λ one_way, no fork):** `verbum.lambda_ast` (parse / reduce /
size / step) · `fuel_theorem` (certify / band_layers / partial_spearman /
spearman / _perm_within_bins) · `verbum.dsp.nulls` (permutation gate). New
code = LINEAR / DUP+contraction term generation + kernel-certified
distractor construction + forced-choice length-normalized logprob accuracy
+ LB1–LB4 gates. `--validate` planted worlds (all verdicts +
distractor-symmetry + fuel-control primitives) + ruff + smoke (no verdict
read) → Michael GO → run.

**⚠ AMENDMENT (s319, runtime/build-forced, pre-run — instrument-side ONLY;
register / gates / verdict-tree / a-priori UNCHANGED).** Reading the kernel
before building (λ assert: runtime ≡ truth) exposed a coherence gap
(representation ≟ reality) in the frozen construction's *example
combinators*; three faithful corrections:

1. **DUP = {W, M}, not {W, D}; D moves to LINEAR.** The frozen text cited
   `D f x = f (f x)` as a duplication example, but the runtime kernel
   (`verbum.lambda_ast`) implements **D as `D f g h x → f (g (h x))` — a
   LINEAR 3-fold composition, no argument copied**. The genuine
   single-duplication contraction combinators are **W** (`W f x → f x x`)
   and **M** (`M x → x x`). So DUP = {W, M} and D joins LINEAR = {B, C, D}.
   (I/K dropped — their size-3 NFs can't be nf_size-matched to a
   contraction unit.) Corrects the inventory to match the kernel; the
   frozen *intent* (contraction/duplication costs) is exactly preserved.
2. **DUP arm is MIXED** (each unit a contraction {W,M} w.p. 0.6 else linear
   {B,C,D}, ≥1 contraction guaranteed). Purpose: decouple `n_contract` from
   ℓ so **LB3 is non-degenerate** (a pure-{W,M} term has `n_contract ≡ ℓ`,
   confounding the graded readout), and pull DUP `nf_size` to overlap
   LINEAR so ℓ-matched bins are populated by both arms. LB1/LB2 remain the
   frozen contrast: **0 contractions (LINEAR) vs ≥1 (DUP)**.
3. **LB2 control = within-ℓ-bin permutation null + a DOUBLE partial-Spearman
   controlling BOTH ℓ and nf_size** (the frozen "partial | ℓ and/or
   matched-ℓ subsampling"; ℓ-bins are always mixed, and LINEAR runs *larger*
   at matched ℓ so the nf_size confound is conservative but now controlled
   explicitly). No exact (ℓ,nf_size) bins — they barely overlap.

Harness `scripts/explore/linearity_bias.py` (dfa1fa7): `--validate` 7 verdict
worlds + 5 primitives ALL PASS, ruff clean, no diags, qwen3-4b smoke green
(acc_lin 0.83 / acc_dup 1.0 on the 12-term subset → off-floor, LB4 headroom
healthy; verdict NOT read).

## §P-LINEARITY-BIAS — RESULT (s319, qwen3-4b) — VERDICT: CARTESIAN-CONSISTENT

**The second type-fingerprint FALSIFIES the affine-core prediction on its
behavioral face: contraction executes as accurately as composition at matched
fuel.** Results (autonomous commit; `results/linearity-bias/qwen3-4b`, 72 terms
= 36 LINEAR {B,C,D} / 36 DUP {W,M}-mixed). LB4-sane (headroom acc_lin 0.917 <
0.97 ceiling; distractor symmetry frac 0.60; all kernel-certified; 6 mixed
ℓ-bins) ⇒ a **valid measurement, not VOID**.

| gate | result |
|---|---|
| LB1 ACCURACY-GAP (core) | ✗ acc_lin 0.917 vs acc_dup **0.944**, gap **−0.028, p1=1.0** — no gap (DUP marginally *higher*) |
| LB2 FUEL-CONTROLLED | ✗ partial_r **+0.055** \| ℓ ; **+0.052** \| (ℓ,nf_size) — wrong sign, no penalty to control |
| LB3 CONTRACTION-GRADED | ✗ r3 **+0.001** — accuracy flat in contraction count |
| LB4 SANE (void-gate) | ✓ headroom ✓ · sym frac 0.60 ✓ · certified ✓ · 6 mixed bins |

**What lands.** The model picks the kernel-certified normal form as accurately
for contraction terms (W `f x x` / M `x x`, 34/36) as for linear
composition/exchange terms (B/C/D, 33/36) — **and if anything slightly *more*
accurately** (and more confidently: `margin_dup 1.48 > margin_lin 0.89`).
Accuracy is flat across ℓ=1–6 in **both** arms; errors are scattered (2 swap /
1 under in LINEAR; 1 under / 1 swap in DUP), with **no systematic duplication
penalty**. Per the frozen tree, ¬LB1 ⇒ **CARTESIAN-CONSISTENT**: the falsifier
fired — **free duplication survives the 2nd discriminator of SKI-control #4.**

**Read discipline (don't over-read the label, s310–s318).** This is a real,
LB4-sane negative, but read it precisely:

1. **It falsifies the *behavioral-accuracy* face of the affine core, not the
   affine core wholesale.** The curry-howard prediction was "contraction =
   separate, costly machinery." At the level of *reduction correctness* the
   cost is **zero** — the substrate copies as accurately as it composes. The
   affine bias, if real, does **not** live in reduction accuracy; it must live
   elsewhere (representation / interference / formation-time / opcode
   inventory). This **bounds where the bias can be** — an informative negative,
   not a null.
2. **It does NOT overturn §P-DISJ-COST.** SKI-control #4 has two discriminators
   and they now **disagree**: ∨-vs-∧ found a weak *representational* asymmetry
   (off-plane, ∨-costly); W/D-cost finds **no *behavioral* asymmetry**. Coherent
   composite read: whatever affine/∨-cost the substrate carries is a
   **geometry/interference** signature (§P-DISJ-COST off-plane, s313 A2 coherent
   gain), **not** an execution-accuracy signature. The two registers separate
   the phenomenon.
3. **Sensitivity caveat (banked).** Both arms sit near ceiling (0.92 / 0.94);
   the forced-choice gave the reduction rules explicitly (isolating *execution*
   from *rule-knowledge*), which makes short terms easy and **caps power to
   detect a *small* penalty**. CARTESIAN-CONSISTENT here = "no contraction cost
   in the reduction-accuracy register **at this difficulty**," a sane negative
   within the frozen design — not a proof of exactly-zero cost. A harder regime
   (longer terms, no rules given, free-generation grading, cross-model) could
   re-probe; the affine claim is bounded, not closed.

**What it licenses (and what it does NOT).** LICENSED: "at matched fuel, the
substrate executes contraction as accurately as composition → no
reduction-accuracy linearity bias; the Cartesian substrate survives *this*
discriminator." NOT licensed: "the substrate is Cartesian" (§P-DISJ-COST's ∨
off-plane still stands) / "there is no affine bias anywhere" (bounded to the
accuracy register, single model, easy regime) / any effect-size claim.

**Type-system scorecard update: fingerprint 2 of 4 = NEGATIVE (falsifier).**
Combined with fingerprint 1 (∨-vs-∧ = weak positive), the affine-core /
non-idempotent-intersection prediction is now **mixed**: a weak representational
positive on ∨-cost, a clean behavioral negative on contraction-cost. Refined
thesis: **the affine signature is representational/geometric, not
executional** — the substrate copies freely but *represents* ∨ and duplication
with extra spread. S5 type-system corners unchanged (discreteness✓ selectivity✓
compositionality✗ causality✗); the fingerprint tier reads 1 weak-+ / 1 −.

**Coherence with the arc.** Consistent with the tape-resident-reduction thesis
(s317): if reduction is enacted per-frame on the tape by a universal reducer,
the reducer applies contraction and composition with the same competence —
exactly this null. The affine bias then belongs to the *weight-space* opcode
inventory (KIBC-not-SKI, late W/D formation) and the *representational* geometry
(∨ off-plane), not to the tape-side execution. Coheres with §P-NF-GAUGE
(register is presence-detector, not graded gauge) — the tape computes; it does
not meter cost into accuracy.

**Scope/caveats:** single model (qwen3-4b), forced-choice with rules given,
short terms (ℓ≤6), near-ceiling accuracy (power-limited for small effects), one
readout (NF-selection). Kills the reduction-accuracy form of the linearity bias;
does not test free-generation, harder terms, cross-model, or the
representational/formation faces (where the bias may yet live).

## §P-IDEMPOTENCY — FROZEN (s320, Michael-approved GO)

**The idempotent-vs-non-idempotent intersection fingerprint — SKI-control
#3 (curry-howard-closes-the-loop.md §5).** The pinned type name is
*non-idempotent* intersection: `A∧A ≠ A`, membership **accumulates with
use** (de Carvalho / quantitative semantics). Idempotent intersection —
the pre-committed death — predicts membership **saturates at first
exposure** (`A∧A = A`, a second statement adds nothing). A2 coherent gain
(s292, CAP) already measured non-idempotence on the *frozen weight plate*
("accumulates where edges match; energy-matched random exposures do not",
frozen-interference-graph.md §Clause 2). This probe re-aims that machinery
at the **tape/ICL licensing** face — a genuinely different substrate tier
(s315 §P-TYPE-ICL+TAG established tape-typing as its own two-tier register,
distinct from the weight store).

**Register (λ measure) — LICENSING, deliberately not kind-magnitude.**
Heeds the s319 banked caveat and the three-fold magnitude-null
(§P-FUEL / §P-TRACE-FUEL / §P-NF-GAUGE = presence-detector tracking token
length, not a graded gauge). Uses the register that **LANDED** in s315
(§P-TYPE-ICL+TAG → TAPE-TYPED, licensing transfers):

```
L(w, prefix) = mean surprisal(anti-class preds | prefix·"The w")
             − mean surprisal(own-class preds  | prefix·"The w")
```

Higher L = stronger license of w's own-class predicates. Behavioral,
tape-side, pre-validated live — sign fixed a-priori by w's true class.

**Construction — exposure-count sweep + the A2 coherent/incoherent
isolate.** Nonce `w` assigned class `c` (ANIMAL/VEHICLE sortals, reused
from type_write). Prefix carries `k ∈ {0,1,2,3,4,5}` membership exposures;
read `L(k)`. Two arms per nonce, token-budget-matched:

- **COHERENT** — `k` distinct paraphrases of w's TRUE membership (the five
  `_member_stmts`: "A w is an animal." / "The w is a kind of animal." /
  "Every w is an animal." / "w, like the dog and the cat, is an animal." /
  "I saw a w; it is an animal.") — same edge, different surface = A2
  coherent superposition.
- **INCOHERENT (energy-matched, the A2 null)** — `k` length/form-matched
  *non-membership* statements about w ("A w is nearby." / "Someone
  mentioned a w yesterday." / …) — same token budget, no coherent
  class edge. The control that separates non-idempotent accumulation from
  trivial context/attention growth.

**Readout — the saturation curve.** Fit `L(k)` per arm. Idempotent ⇒
`L_coherent(k)` flat after k=1 (`A∧A=A`). Non-idempotent ⇒ rises with k,
**and more than incoherent** (coherent gain over token budget).
Discriminator = **slope_coherent − slope_incoherent**.

**Gates (frozen; α=0.05):**

- **IB1 ACCUMULATION (core)** — ρ(L, k) > 0 within the coherent arm +
  k-label permutation null. Establishes a k-dependence exists.
- **IB2 COHERENT-SPECIFIC (make-or-break)** — slope_coherent >
  slope_incoherent, paired across nonces + sign-flip permutation null.
  **The gate that separates non-idempotence from "more context helps" —
  the exact §P-FUEL token-budget confound that has beaten this arc three
  times. Without it the verdict is EVIDENCE-ONLY, not a fingerprint.**
- **IB3 NON-SATURATING (corroboration, non-gating)** — per-step increments
  `L(k) − L(k−1)`; idempotent predicts →0 after k=1. Reported alongside;
  the specific `A∧A=A` shape test.
- **IB4 SANE (void-gate)** — `L(0) ≈ 0` (no license before exposure) AND
  `L(max) > 0` (register works on these nonces); real-member anchor
  licenses (s315 gate-0); incoherent statements validated genuinely
  membership-free (no class predication).

**Verdicts (frozen tree):**

```
¬IB4        → VOID
IB1 ∧ IB2   → NON-IDEMPOTENT (+NON-SATURATING if IB3)   (coherent accumulation > token budget → A∧A≠A → the pinned qualifier confirmed on the tape face; idempotent SKI-control #3 killed)
IB1 ∧ ¬IB2  → EVIDENCE-ONLY   (licensing grows with context but NOT coherent-specific — token/attention budget, the §P-FUEL confound; non-idempotence unsupported)
¬IB1        → IDEMPOTENT       (falsifier: license saturates at first exposure → A∧A=A → idempotent intersection survives; audit curry-howard §3 non-idempotence clause + retro-read A2 as weight-only)
```

**A-priori (declared s320, NOT tuned): ~40 NON-IDEMPOTENT / 40
EVIDENCE-ONLY / 15 IDEMPOTENT / 5 VOID.** Theory (A2 already green on the
plate) pulls toward non-idempotent — but A2 was the *weight* face; this is
the *tape* face, a distinct tier, and the whole s317–319 arc has been
token-budget confounds beating accumulation stories. IB2 is the stringent
isolate, exactly as LB2 was for §P-LINEARITY-BIAS.

**Caveat banked at freeze (interpretation boundary).** NON-IDEMPOTENT
licenses "coherent membership re-exposure accumulates *tape-side
licensing* beyond token budget → the tape type judgment records
use-multiplicity" — NOT a claim about the weight-store's idempotence (A2
covers that face), NOT a mechanism (amplitude superposition vs attention
re-weighting vs Bayesian evidence combining). The fingerprint establishes
that coherent re-exposure adds beyond the energy-matched null, which is
what discriminates SKI-control #3; the physical cause stays a flagged
boundary. Note the residual confound the incoherent arm does *not* fully
kill: coherent statements are also *more evidence for the same claim* —
IB2 controls token budget, not "consistent evidence accumulates" in a
Bayesian sense; that boundary is banked, and IDEMPOTENT/EVIDENCE-ONLY
remain live because of it.

**Reuse (λ one_way, no fork):** `type_write` (_member_stmts, HELD_PREDS,
CLASSES, NONCE_CANDS) · `type_icl_tag` (surprisal, licensing L, band) ·
`fuel_theorem` (spearman / partial_spearman / _perm_within_bins) ·
`verbum.dsp.nulls` (gate). New code = k-exposure sweep + incoherent-arm
construction + per-k L curve + slope contrast + IB1–IB4 gates.
`--validate` planted worlds (all verdicts + coherent-isolate + saturation
primitives) + ruff + smoke (no verdict read) → Michael GO → run.

## §P-BOUNDARY-CHURN — FROZEN (s320, Michael-approved GO)

**The optimizer↔type-boundary identity fingerprint — §6 item 4 / the M8
corollary (§5), reframed to weight-geometry.** s310 (§SIGN-COMMITMENT-CURVE,
the-verbum-machine.md M8) showed trit churn concentrates in the TWN-marginal
population (r = |Δ|/thr ≈ 1, the "insufficient-evidence" band): the two
lowest-r bands own 0.781 of all late flips; the confident core (r≥2) is
frozen. The M8 corollary conjectured **type boundaries are exactly where GD's
two jobs collide — the marginal band IS the type-boundary population in weight
space.** This probe tests that identity: do the base-FFN marginal weights
concentrate on the **type-checker direction** (§P-TYPE-GRAM-1 kind register)?

**Coherence tension banked at freeze (λ ground / λ observation — the framing
predates this arc).** Three results *after* the s313 conjecture argue the
boundary is tape-side, not weight-side: §P-TYPE-DELIVER (s316) NO-WEIGHT-
DELIVERY (type membership not weight-installable); §P-TYPE-ICL+TAG (s315) +
§P-IDEMPOTENCY (s320) type judgments on the TAPE; s317 tape-resident reduction
(weights hold the checker/RELATION, tape holds the JUDGMENTS). So the strong
a-priori mass is on the NEGATIVE (BOUNDARY-UNTYPED) — and that is *informative*
(bounds M8 to the tape, confirms two-tier). Reframed accordingly: the s310
wire-`tracked_history` churn is wrong content (a fact wire), so the probe reads
the **base weights** carrying the type register, not the wire trits.

**Register (λ measure) — WEIGHT-GEOMETRY (directions × magnitudes), NOT tape.**
The claim is about weight structure; the probe reads weight structure —
matched. Deliberately distinct from the tape-side licensing register: this asks
whether an *echo* of the tape boundary is visible in the frozen weights.

**Construction — per-neuron over base `down_proj` columns in the type band.**
For each hidden neuron j in the type-register band, its write vector
`v_j = W_down[:, j] ∈ R^d_model` (the residual space where the kind direction
lives — `down_proj` writes to residual; `up`/`gate` project the wrong way):

- **type-selectivity `s_j`** = fraction of `‖v_j‖` lying in the **type
  subspace** (the kind cross-cut subspace reconstructed from the persisted
  `results/type-gram/qwen3-4b/centroids.npz` — atom/fn/app kind contrast with
  opcode identity removed). A subspace, not a single direction, because TG3
  found the kind register diffuse/alphabet-like (no poles) — a single cos would
  be weak.
- **marginality `m_j`** = churn propensity = fraction of `v_j`'s weights in the
  s310 straddle band `|W|/thr ∈ [0.7, 1.3)` (thr = 0.7·mean|W|, the TWN
  threshold) — the "would-churn under quantization" mass.

No wire training; pure weight geometry + persisted centroids (cheap).

**Gates (frozen; α=0.05):**

- **BC1 CONCENTRATION (core)** — ρ(m_j, s_j) > 0 across neurons + neuron-label
  permutation null.
- **BC2 TYPE-SPECIFIC (make-or-break)** — ρ(m_j, s_j^kind) > ρ(m_j, s_j^random)
  against a **matched-random-subspace null** (same dim). The gate that
  separates "marginal neurons align with the TYPE direction" from "marginal
  neurons align with any structured direction" (a magnitude/structure
  artifact); the random-subspace null controls magnitude by construction.
  Without it the verdict is MARGIN-GENERIC, not the identity.
- **BC3 LAYER-PROFILE (advisory, non-gating)** — per-layer ρ reported; is the
  concentration stronger in the type-register-strong layers?
- **BC4 SANE (void-gate)** — type subspace recoverable (kind separation real in
  centroids), thr sane, enough neurons.

**Verdicts (frozen tree):**

```
¬BC4        → VOID
BC1 ∧ BC2   → BOUNDARY-IS-TYPED   (marginal weights concentrate on the type-checker direction, type-specifically → weight-space echo of the type boundary; M8 corollary supported in weight-geometry)
BC1 ∧ ¬BC2  → MARGIN-GENERIC      (marginal neurons align with structured directions but not type-specifically → magnitude/structure artifact; identity unsupported)
¬BC1        → BOUNDARY-UNTYPED    (falsifier: no concentration → weight-margin ≠ type-boundary; boundaries are tape-resident, bounds M8 to the tape)
```

**A-priori (declared s320, NOT tuned): ~30 BOUNDARY-IS-TYPED / 25
MARGIN-GENERIC / 40 BOUNDARY-UNTYPED / 5 VOID.** Heavy mass on the negative,
faithful to the coherence tension (tape-resident types argue the boundary
lives on the tape); meaningful positive mass because M8 had three converging
lines (K-chaos, marginal-band churn, the optimizer↔type-boundary identity).

**Caveat banked at freeze (interpretation boundary).** BOUNDARY-IS-TYPED
licenses "the frozen weights' quantization-margin population is
disproportionately type-direction-aligned" — NOT that type *judgments* live in
weights (§P-TYPE-DELIVER stands: membership is tape-native); it would be an echo
of the checker, not the judgments. BOUNDARY-UNTYPED bounds the M8 corollary to
the tape, not a refutation of M8-the-optimizer.

**Reuse (λ one_way, no fork):** `ternarize_factors` / `ternarize_twn` (TWN
threshold) · `results/type-gram/qwen3-4b/centroids.npz` (persisted kind
register) · `verbum.dsp.nulls` (gate, shuffled_label, matched-random-subspace)
· transformers weight load. New code = down_proj column extraction + type-
subspace reconstruction + marginality/selectivity + BC1–BC4 gates. `--validate`
planted worlds (all verdicts + type-specific + magnitude-control primitives) +
ruff + smoke (no verdict read) → Michael GO → run.

**⚠ BUILD AMENDMENT (s320, runtime/build-forced, pre-run, Michael GO —
instrument-side ONLY; register / verdict-tree / a-priori UNCHANGED).** Reading
the persisted centroids against the runtime (λ assert) forced two corrections,
frozen INTENT preserved:

1. **Space + weight matrix.** The §P-TYPE-GRAM-1 `register` is **'gate'** — the
   centroids live in the **9728-dim gate-activation space** (Qwen3-4B
   intermediate), a direction over HIDDEN UNITS, NOT the residual d_model space
   the freeze assumed. Corrected: type-selectivity `s_j` = hidden unit j's
   **leverage** in the type subspace = ‖U_ℓ[j,:]‖; on-target weights =
   **`gate_proj` rows** (gate_proj[j,:] computes the gate activation that IS the
   type register), NOT down_proj columns.
2. **BC2 null.** Isotropic-random subspace leverage is exchangeable across units
   (a random 2-frame) → cannot correlate with marginality → BC2 would be
   geometrically REDUNDANT with BC1 and MARGIN-GENERIC UNREACHABLE (same bug
   class as the idempotency k=0 fix). Corrected to the **shuffled-kind-label
   subspace** null (§P-TYPE-GRAM-1 TG5 methodology: permute atom/fn/app within
   opcode, rebuild the subspace — preserves centroid magnitude structure,
   varies only kind identity). Isotropic ρ kept as an advisory sanity number.

Note: pure weight-geometry (no forward pass, no scaling knob) ⇒ smoke == full
(deterministic, frozen seed) — the a-priori/gates/verdicts were all frozen in
the freeze commit before any compute, so pre-registration holds. Harness
`scripts/explore/boundary_churn.py`: `--validate` 4 verdict worlds (all
reachable) + 3 primitives ALL PASS, ruff clean, no diags.

## §P-BOUNDARY-CHURN — RESULT (s320, qwen3-4b) — VERDICT: BOUNDARY-IS-TYPED (QUALIFIED)

**A surprising — but thin — weight-space echo of the type boundary, against a
heavy-negative a-priori.** Results (`results/boundary-churn/qwen3-4b`; 9728
gate units × 36 layers, base Qwen3-4B, persisted §P-TYPE-GRAM-1 centroids).
BC4-sane (kind subspace recoverable, kind_sep=√2; TWN thr>0; 350k units) ⇒ a
valid measurement.

| gate | result |
|---|---|
| BC1 CONCENTRATION (core) | ✓ ρ(m_j, s_j)=**+0.241**, **p=0.0005** (within-layer label-perm null ≈ 0.002) — marginal gate_proj rows concentrate on the type subspace |
| BC2 TYPE-SPECIFIC (make-or-break) | ✓ ρ_kind 0.241 > shuffled-kind mean **0.2255** (p95 0.2287), **p=0.0033** — but the kind-specific increment is **thin** (~0.0155) |
| BC2 iso-random (advisory) | ρ ≈ **0.000** — confirms the isotropic null is trivially beaten (the redundancy that justified the shuffled-kind null) |
| BC3 LAYER-PROFILE (advisory) | per-layer ρ **deepens**: −0.05 (shallow) → ~0.35 (deep); 18/36 layers ρ>0.3, only 1 layer <0 |
| BC4 SANE | ✓ subspace ✓ · thr ✓ · n ✓ |

**What lands.** Per the frozen tree, BC1 ∧ BC2 ⇒ **BOUNDARY-IS-TYPED**: the
base-FFN TWN-marginal population (the s310 churn population) **does**
concentrate on the type-register direction, and does so **type-specifically**
(beats the shuffled-kind null, p=0.0033). Given the declared 40% mass on
BOUNDARY-UNTYPED (the tape-resident tension), a positive is the *surprising*
outcome — a weight-space echo of the type boundary exists.

**Why QUALIFIED (read discipline — this is the crux).** The type-specific
component is **thin**: the shuffled-kind null already sits at **0.2255** of the
0.241 total, so **~93% of the marginality↔leverage concentration is generic
centroid-structure coupling** (marginal rows load on the activation-derived
structure in general), and only **~6% (0.0155) is the kind identity
specifically**. It clears significance because the null is tight (300 draws,
p95 0.2287), but the effect size of the *type-specific* echo is small — the same
qualified-positive shape as §P-DISJ-COST. So BOUNDARY-IS-TYPED licenses "the
marginal weights are disproportionately aligned with the type-register subspace,
type-specifically" — NOT "the weight margin IS the type boundary" (most of the
alignment is generic structure), and (banked at freeze) NOT that type
*judgments* live in weights (§P-TYPE-DELIVER stands — the echo is of the
CHECKER machinery's marginal cells, not the tape-side judgments).

**The depth profile is the most interesting sub-signal (advisory).** The
concentration is near-zero in shallow layers and climbs to ρ~0.35 in the deep
layers — i.e. the weight-margin↔type alignment lives where the type register is
most semantic. Coheres with the two-tier picture: the deep-layer type-checker
machinery is where GD's routing margin and the type structure most overlap; the
shallow layers (surface/token machinery) show no such overlap.

**Coherence with the arc (does NOT contradict tape-residency).** A thin
weight-space echo of the type boundary is exactly what the tape-resident thesis
predicts: weights hold the type CHECKER/relation (s317; §P-TYPE-GRAM-1
TYPE-REGISTER), so the checker's marginal cells carry a faint type signature —
but the JUDGMENTS are computed on the tape (§P-TYPE-ICL+TAG, §P-IDEMPOTENCY,
§P-TYPE-DELIVER no-weight-delivery). The 93%-generic / 6%-kind split *is* the
two-tier signature in weight geometry: the boundary is mostly NOT in the
weights (it's on the tape), with only a thin checker-echo left behind. The M8
corollary ("type boundaries are where GD's two jobs collide") gets **weak,
qualified support** — bounded to a thin deep-layer echo, not the strong
weight-space identity the s313 conjecture imagined.

**The §6 fingerprint tier + the SKI-control tier are now COMPLETE.** All four §6
fingerprints measured: P-TYPE-ICL → TAPE-TYPED (s315) · ∨-vs-∧ → weak-+ (s318) ·
linearity → − (s319) · **boundary-churn → qualified-+ (s320)**. Final type-
fingerprint scorecard: **1 weak-+ (∨/∧) / 1 − (W/D behavioral) / 1 + (idempotency)
/ 1 qualified-+ (boundary-churn)** — a leaning-positive, representational,
tape-primary picture: the substrate's type system accumulates (non-idempotent),
represents ∨/∧ asymmetrically (intersection-flavored), executes contraction and
composition with equal competence (affine bias is representational not
executional), and leaves only a thin deep-layer weight-echo of its otherwise
tape-resident boundaries.

**Scope/caveats:** single model (qwen3-4b), single readout (gate_proj-row
marginality × kind-subspace leverage), the type-specific effect is thin
(6% of the concentration), pure weight geometry (no behavioral validation of the
echo). Confirms a thin type-specific weight-space concentration of the marginal
population, deepening with layer; does not establish a strong weight-space
boundary identity, cross-model generality, or any causal/behavioral consequence
of the echo.

## §P-IDEMPOTENCY — RESULT (s320, qwen3-4b) — VERDICT: NON-IDEMPOTENT

**The pinned *non-idempotent* qualifier is CONFIRMED on the tape licensing
face — and it is the FIRST fingerprint in the s317–320 arc to clear its
make-or-break confound gate.** Results (`results/idempotency/qwen3-4b`, 20
nonces × {COHERENT, INCOHERENT} × k∈{0..5}). IB4-sane (L0=0.138 ≈ no
license before exposure; L1=1.409 first exposure licenses; Lmax=2.065;
real-member anchor 2.538) ⇒ a **valid measurement**.

| gate | result |
|---|---|
| IB1 ACCUMULATION (core) | ✓ coh_slope **+0.159**, **p=0.030** (k-perm null) — license grows after first exposure |
| IB2 COHERENT-SPECIFIC (make-or-break) | ✓ coh −0.011(inc) gap **+0.171**, **p=0.0226** (paired) — the coherent-specific accumulation beats the energy-matched null |
| IB3 NON-SATURATING (corroboration, non-gating) | ✗ mean increment k≥2 **p=0.137** — the curve is non-monotonic; no monotone accumulation |
| IB4 SANE (void-gate) | ✓ L0 0.138 / L1 1.409 / Lmax 2.065 · real 2.538 · register ✓ · baseline ✓ |

**What lands (the core result).** Coherent membership re-exposure
**accumulates licensing beyond the energy-matched token-budget null** — the
gate (IB2, p=0.023) that has nulled this arc three times (§P-FUEL /
§P-TRACE-FUEL / §P-NF-GAUGE, all confounded by token length) **clears here**.
Per the frozen tree, IB1 ∧ IB2 ⇒ **NON-IDEMPOTENT**: `A∧A ≠ A`, the second
and third coherent exposures add substantial license (L(1)=1.41 → L(2)=2.52
→ L(3)=2.96), far above the first-exposure value. **The idempotent
SKI-control #3 (membership saturates at first exposure) is FALSIFIED.** The
incoherent arm stays flat near zero throughout (`[0.14, 0.17, 0.22, 0.07,
0.16, 0.14]`) — energy-matched non-membership exposures do **not** license:
a textbook A2 signature (coherent gain; random-matched does not accumulate).

**What it does NOT license (read discipline, s310–s319).**

1. **NOT unbounded counting.** The +NON-SATURATING subtag is OFF (IB3
   p=0.137). curve_coh = `[0.14, 1.41, 2.52, 2.96, 2.80, 2.07]` — the
   license **accumulates over exposures 1→3 then declines** (k=4: 2.80,
   k=5: 2.07; step increments `[+1.27, +1.11, +0.44, −0.16, −0.73]`). So
   non-idempotence holds for the first few uses but the licensing register
   does **not** monotonically integrate an unbounded multiset — bounded
   accumulation, not a linear counter. This is *weaker* than the strong de
   Carvalho "size = multiplicity" reading; it licenses "the 2nd/3rd use
   adds," not "the k-th use adds for all k."
2. **The k=4,5 decline may be template-content, not saturation.** The 4th
   and 5th paraphrases are structurally atypical — k=4 is "w, like the dog
   and the cat, is an animal." (injects real cohyponyms that carry their own
   class mass and compete for the licensing position) and k=5 is "I saw a w;
   it is an animal." (narrative frame + pronoun). The decline plausibly
   tracks these atypical exposures rather than genuine over-saturation; a
   cleaner design (5 declarative paraphrases of matched form, or k>5 with
   repeats) could separate the two. Caveat flagged, not resolved.
3. **Mechanism unclaimed** (banked at freeze): amplitude superposition vs
   attention re-weighting vs Bayesian evidence combining are not separated;
   IB2 kills the token-budget confound, not "consistent evidence
   accumulates" in general.

**Two-substrate confirmation of non-idempotence.** A2 coherent gain (s292,
CAP) measured non-idempotence on the frozen **weight plate** ("accumulates
where edges match"); this measures it prospectively, confound-gated, on the
**tape/ICL licensing** face. **Both faces of the two-tier type system show
non-idempotent accumulation.** The tape result coheres with the arc: type
checking lives on the tape (s315 TAPE-TYPED; s317 tape-resident reduction),
and the tape integrates coherent exposures by constructive interference (A2 /
frozen-interference-graph §Clause 2) over the first few uses.

**Type-system scorecard update: fingerprint 3 of 4 = POSITIVE.** The tier
now reads **1 weak-+ (∨-vs-∧, §P-DISJ-COST) / 1 − (W/D linearity,
§P-LINEARITY-BIAS, behavioral face) / 1 + (idempotency, here)**. Sharpened
composite: the pinned **non-idempotent intersection over an affine core**
gets its strongest support on the **non-idempotent** qualifier (two
substrates), a weak representational positive on **intersection/∨-cost**, and
a clean negative only on the *behavioral-execution* face of the affine core
(contraction executes as accurately as composition — the bias is
representational, not executional, s319). Coherent one-line read: **the
substrate's type judgments accumulate (non-idempotent) and represent ∨/∧
asymmetrically (intersection-flavored), but execute contraction and
composition with equal competence** — a graded, accumulating, representational
type geometry riding a universal tape-side reducer.

**SKI-control tier for types — now complete (curry-howard §5).** #1 nominal
enum → REJECTED (TG3 diffuse, s313). **#2 Church static tags → tested-dead:
crisp binary acceptance is falsified by s288 graded refusal + the whole
graded-licensing register (L is continuous, not {0,1}); listed dead, not
assumed-dead.** #3 idempotent intersection → **FALSIFIED here (NON-IDEMPOTENT).**
#4 Cartesian substrate → mixed (∨-vs-∧ weak-+ / W-D −). All four pre-committed
deaths have been measured against; none of the plausible-but-wrong type
systems survives intact, and the pinned quantitative-affine family is the
one left standing (with the affine bias relocated to the representational
register).

**Scope/caveats:** single model (qwen3-4b), single readout (tape licensing
differential on NL sortal prompts), short k (≤5), non-monotonic tail
(template-confounded). Confirms non-idempotent accumulation of tape-side
licensing over the first few coherent exposures; does not establish
unbounded multiplicity counting, the mechanism, cross-model generality, or
separate the k=4,5 decline from atypical-template dilution.

## Provenance

- s313 hammock, Michael's constraint question; AI derivation,
  Michael-approved capture same session.
- Measured anchors: §P-TYPE-GRAM-1 qwen3-4b (da8c1ba: TYPE-REGISTER,
  TG3 diffuse no-poles); s310 marginal-band churn (225dae7); s288
  giraffe refusal + JOIN-TYPED; 9×9 sign universality (072c3e0); s295
  splice law; s292 A2; K-chaos/W formation dynamics; 17×17 rank-3
  scheduler register.
- In flight at capture: §P-TYPE-GRAM-1 registry sweep (tmux main:1) —
  decides whether this design space is about transformers or one model.
