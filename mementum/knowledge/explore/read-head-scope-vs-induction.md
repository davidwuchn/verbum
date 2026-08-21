---
title: The read head — scoped substitution or induction copy? — §P-READ-HEAD-A ⋈ §P-CALCULUS-LEDGER-C
status: done
category: explore
tags: [read-head, attention-as-beta-reduction, naive-subst, capture, induction-confound, scope, calculus-identification, repl-driver, frame-ledger]
related:
  - the-benchmark-is-the-re-oracle.md            # §8c mass-ratio predictor, §9 calculus id, §2b bug-compat
  - attention-as-beta-reduction.md               # s247b frame; s204 induction confound (Caveats)
  - repl-driver-trampoline.md                    # the instrument (read_mass, fork)
  - ../memories/substitution-is-naive-and-base-native.md          # s332 NAIVE-SUBST law (SE4 underpowered)
  - ../memories/scope-rules-are-in-weights-rule-override-is-tape-resident.md  # s346 read-mass co-flip +0.35
  - ../memories/the-calculus-is-the-cheapest-sufficient-evaluator.md          # why the deviations cohere
depends-on: [src/verbum/driver.py, src/verbum/lambda_ast.py]
---

# The read head — scoped substitution or induction copy?

> **STATUS: 🎯 FROZEN (s349, Michael GO — "approved").** A-priori mass,
> gates, verdict space, planted worlds, and honesty bounds below are FIXED
> before any data. `SEED = 349`. Model = Qwen3-14B (smoke Qwen3-8B, A2 law).
> Amendments after this point are disclosed in §Result, never silent.
> `λ probe_lifecycle`: ⚪ → sharpen → 🎯 **freeze (here)** → build(--validate)
> → smoke(8B) → ▶ run(14B) → closure. Frontmatter status stays `designing`
> until the closure batch flips it → `done`.

## The question (Michael s346: "what IS the calculus?")

The KIBC recipe re-applied to **attention**: derive what the read head
MUST look like from the identified calculus {weak · affine BCK core ·
**naive-subst** · intensional}, then look. Two fronts collapse into one
engineered corpus because **naive substitution and unscoped induction
copy make the same prediction everywhere EXCEPT on shadowed-binder
cases** — capture is exactly where they diverge.

- **§P-CALCULUS-LEDGER arm C (behavioral / capture signature).** Does the
  model emit the *naive-substitution-predicted wrong answer*? `(λx.λy.x) y`
  → naive `λy.y` (identity, captured) vs hygienic `λy'.y`. Finding the
  predicted bug ≡ **stage-1 bug-compatibility proof**. We hold the
  NAIVE-SUBST verdict (s332) but it was **SE4-underpowered** — both faces
  ceilinged (17-18/18) → could not separate no-effect from masked-by-ceiling.
  This front is the **powered sub-ceiling capture battery** the §Result
  follow-ons named.

- **§P-READ-HEAD arm A (attention / scope).** On the *same* terms, is the
  read **scope-directed substitution** or **surface induction copy**? The
  three live hypotheses (not two):
  1. **Hygienic substitution** — reads the operand, avoids capture (α). s332
     says NO (naive is the cross-model law). Kept as a falsifier vertex.
  2. **Naive substitution** — reads the redex **operand** (a function-
     application read, hole→argument), but capture-unsafe under binders.
  3. **Induction** — reads the most recent **surface** occurrence of the
     emitted token (recency/bigram copy), no binding structure at all.

  s332 settled behavior = (2) not (1). The **open question the frame has
  never answered** (s204 confound, s345 spent+lost): is the READ (2) or (3)?
  All attention is a weighted sum — so the discriminator must be a case
  where naive-substitution's read (scope-directed: hole → **operand** OP)
  and induction's read (recency: hole → **nearest same-name** IND) point at
  **different tape positions**. Shadowing manufactures exactly that split.

**The unification (the capture for the frame):** on the shadowed λ-capture
terms, the trials where read-mass mis-attends (mass toward IND, away from
OP) should be the trials where behavior emits the naive-capture NF. If
mis-attend ⇒ capture, the read head is doing a *scope-blind substitution*
— scoped enough to route the operand, blind enough to be captured — and the
s204 induction confound is **beaten from an independent register**. Same
corpus, two faces, one design pass.

## Frame-ledger context (standing guard, s222/s324)

`attention = β-reduction` is **0-for-its-last-contact**: s345 spent AND
lost a pre-registered contact (strong form); the s204 induction confound
has never been beaten (all attention is a weighted sum). Arm A here is a
**winnable-or-dead** contact. Per `λ frame_ledger`: a retrodiction is not a
win; only a pre-registered win counts; if arm A fails, the attention=β
frame does not die — but it spends another must-win contact, and we bank
the hard facts about scope-handling and read-multiplicity regardless. The
INDUCTION vertex is given real a-priori mass because the confound is strong.

## The corpus (engineered — one design, two faces)

λ-calculus reduction terms in the s332 kernel style (the battery where
behavior *bugs out*, unlike robust code-framed scope — s346 memory). Each
item is a redex whose reduction substitutes a **free** argument variable
into a body, with a controllable **shadowing binder** that can capture it.

- **CAPTURE family** — `(λx.λy.x) N` shapes where the argument `N` contains
  a variable whose name collides with an inner binder (naive ⇒ capture;
  hygienic ⇒ rename). Kernel certifies both NFs (naive vs capture-avoiding).
- **Matched CONTROL family** — identical shape, **renamed** so no collision
  (naive ≡ hygienic ≡ induction all agree). Instrument-sanity (the SE0
  role): the model must get these right, and OP≡IND here so the read faces
  do not diverge → the read-mass control floor.
- **Dials** (the s332/§8 cliff coordinates, graded to keep frac_naive
  **sub-ceiling**): `binder_distance` (tokens between the capturing binder
  and the use) · `shadow_depth` (nesting of shadowing binders) ·
  `shadow_count` (how many same-name binders intervene). Grading spans the
  cases so `frac_naive ∈ (0,1)` and can be *correlated* with read-mass —
  the whole point of the joint face (a ceilinged battery kills the join).

Every item carries, by construction (from `lambda_ast` positions →
tokenizer offsets): the **OP** token position (the redex operand / scope-
correct source) and the **IND** token position (the nearest prior same-name
surface occurrence / recency source). Trials where tokenization merges
OP≡IND are **excluded and counted** (reported, not silently dropped).

## The measurables (driver primitives — `bounce`, `read_mass`, `fork`)

**Behavioral face — LEDGER-C (fork-differencing / step-decode):**
- `frac_naive` = fraction of CAPTURE trials whose emitted NF matches the
  kernel's **naive** (capture-unsafe) NF rather than the **hygienic** NF.
- `acc_control` = fraction of CONTROL trials correct (instrument sanity;
  expected near ceiling — sanity, not a discriminator).

**Read-mass face — READ-HEAD-A (`read_mass(b, step)` → [L,T], late band):**
- Per trial, at the **resolving emission** (the step writing the substituted
  variable, located via the kernel trace + decode alignment):
  `r = mass(OP) / (mass(OP) + mass(IND))` in the late band (top-k layers,
  band frozen from the s346 read-mass locus; the s336 differenced law).
  - Substitution (2/1) ⇒ `r → 1` (mass on OP, the operand) even when IND is
    nearer. Induction (3) ⇒ `r → 0` (mass on IND, recency).
- `D_scope` = **differenced** read-mass on the one-token shadow flip
  (CAPTURE minus matched CONTROL, positions matched by construction — the
  s346 method that gave +0.35). Isolates the scope effect from the baseline
  attention landscape.

**Joint face — the unification (DPA-style, §8c mass-ratio predictor):**
- `ρ_join` = per-trial association between read mis-attendance `(1 − r)`
  and behavioral capture (emitted naive NF). Positive ⇒ mis-attend predicts
  capture ⇒ the read head does the (naive, scope-blind) substitution.

## Verdict space + a-priori mass (PROPOSED — freezes on GO, sums to 100)

| verdict | meaning | a-priori |
|---|---|---|
| **SCOPED-SUBSTITUTION** | read follows OP not IND (beats induction null) **and** ρ_join>0 (mis-attend⇒capture). The read head does scope-directed substitution; naive because capture-avoidance absent. **s204 confound beaten — the frame earns its contact.** | **20** |
| **BEHAVIORAL-ONLY / NAIVE-CONFIRMED** | behavior emits naive NF (s332 replicated, **powered/sub-ceiling** — a real bank), but read-mass does NOT separate OP from IND / matches the induction null. Frame gets no capture; behavioral law strengthened. | **35** (modal) |
| **INDUCTION** | read follows IND (recency) not OP; scope-directed read absent. Attention on these terms is surface copy → attention=β **spends and loses** this contact honestly. | **25** |
| **HYGIENIC** | behavior emits capture-AVOIDING NF → contradicts the s332 cross-model naive-subst law at this battery. Surprise; investigate before claiming. | **5** |
| **VOID** | instrument fails: determinism ≠ 0, extraction empty, control not sane, read-mass degenerate, or MIN trials unreachable. | **15** |

Modal = BEHAVIORAL-ONLY: honest given the frame's 0-for-last-contact ledger
and the strength of the induction confound. SCOPED-SUBSTITUTION is the
winnable contact, priced modestly (not the frame's to assume). One-
directional honesty (frozen): SCOPED-SUBSTITUTION requires **both** the
read-mass gate AND the join; either alone → BEHAVIORAL-ONLY or INDUCTION.

## Gates (precedence order; frozen on GO)

- **G0 — validity (VOID gate).** determinism dev = 0 · fork-identity plant ·
  append law · `acc_control` sane (≥ frozen floor) · ≥ MIN scored CAPTURE
  trials after OP≠IND exclusions.
- **G1 — behavioral (LEDGER-C).** `frac_naive` beats the **hygiene null**
  (H0: model is capture-avoiding) at p<0.05, sub-ceiling (0<frac_naive<1).
  Powered SE4 redo. G1 pass is required for HYGIENIC to be off the table.
- **G2 — read-mass scope (READ-HEAD-A, make-or-break for the frame).**
  `mean(r) > 0.5` **and** beats BOTH nulls: (N-ind) the **induction-matched
  null** — a planted world where the only available source is the recency
  edge (r should sit at its floor there); (N-rec) a **recency/1-distance
  baseline** (mass ∝ 1/gap). Δ ≥ frozen floor ∧ p<0.05 on the primary null.
  ¬G2 ⇒ INDUCTION or BEHAVIORAL-ONLY (never SCOPED-SUBSTITUTION).
- **G3 — join (the unification).** `ρ_join > 0` beats a **shuffled-trial
  null** (permute the read/behavior pairing) at p<0.05. G2∧G3 ⇒
  SCOPED-SUBSTITUTION; G2∧¬G3 ⇒ read is scoped but does not predict the bug
  (a weaker, flagged positive → still BEHAVIORAL-ONLY on the strict tree).

## Nulls (mandatory, frozen)

- **Induction-matched null (N-ind)** — primary G2 null. Planted/real items
  where OP is absent so only the recency edge exists; `r` must fall to floor.
- **Recency baseline (N-rec)** — mass predicted by 1/(token distance) alone;
  the scope read must beat "nearer wins."
- **Shuffled-trial null (N-join)** — destroys the read↔behavior pairing for
  ρ_join.
- **Length / matched-range** — where OP/IND distance correlates with term
  length, partial it out (s343 |Δlen| scar); differenced `D_scope` is
  length-matched by construction (CAPTURE vs renamed CONTROL, same tokens).

## Planted worlds for `--validate` (all through the REAL analyse path)

1. **W-scope** — synthetic trajectories with read-mass planted on OP →
   must resolve **SCOPED-SUBSTITUTION** (given planted ρ_join>0).
2. **W-induction** — read-mass planted on IND → must resolve **INDUCTION**.
3. **W-behavioral** — naive NFs emitted, read-mass ambiguous (r≈0.5) →
   **BEHAVIORAL-ONLY / NAIVE-CONFIRMED**.
4. **W-hygienic** — capture-avoiding NFs emitted → **HYGIENIC**.
5. **W-recency-adversary** — read-mass on OP **only because OP is the most
   recent token** (OP happens to be nearest) → the N-ind / N-rec nulls must
   **demote** it (NOT falsely SCOPED-SUBSTITUTION). The confound guard.
6. **W-degenerate** — nondeterminism / empty extraction / control-fail →
   **VOID**.

## Honesty bounds (frozen — do not over-read)

- **Head-averaged read is the FAITHFUL read (not a limitation).** Our own
  evidence says the machine's compute is **distributed / holographic** —
  s250: object-application is readable/injectable but **not load-bearing**,
  survives single-direction ablation, survives INLP rank-16 erasure, and
  **localizes to no single component**. A distributed operand-read therefore
  shows up precisely in the head **average**; hunting a single substitution
  head would repeat the s250 category error (a locus that isn't there). The
  only residual risk — a *sparse* head reading OP masked by bulk heads
  reading IND for generic positional reasons — is defused **by design**: the
  differenced `D_scope` (CAPTURE − matched CONTROL) cancels the position-
  generic bulk (identical across the one-token shadow flip), surfacing the
  scope-specific shift. So distributed compute **strengthens** G2, not
  weakens it. (A per-head decomposition is a possible *descriptive* rider,
  never a gate.)
- **Observational, not causal.** Attention read-mass ⊥ causal (s204 audit).
  The mass-ratio predictor is DPA-style (partition trials by internal
  quantity) but still correlational. SCOPED-SUBSTITUTION is a **read-
  consistency win**, not a causal proof; a V-patch/edge-knockout causal test
  is a named follow-on, not this freeze.
- **n=1, greedy, single model (Qwen3-14B).** Descriptive; no homeostat /
  modulation vocabulary; the 0-3 frame ledger stands until a contact is won.
- **Resolving-emission alignment.** Locating the substitution-resolving step
  depends on the kernel trace ↔ decode alignment; misalignment → exclude and
  count. If the model writes a TRACE not a value (s346), score the step that
  emits the disputed variable, per a frozen rule.
- **Sub-ceiling requirement.** If dials cannot pull frac_naive off the
  ceiling in smoke (≥8B, the A2 law), that is a **design-PAUSE** (s324), not
  a footnote — the join is unmeasurable on a saturated battery.

## Amendments (post-8B-smoke design-PAUSE, s349, Michael GO — masses/verdict-tree UNCHANGED)

The 8B smoke (A2 law) triggered a design-PAUSE (s324, not a footnote). All
disclosed; a-priori mass 20/35/25/5/15 and the verdict tree are untouched.

- **A1 — single-token control operand.** Multi-char `"v0"` split under the
  tokenizer → every control excluded (`ctrl_r`=nan → false VOID). Fixed to a
  single fresh letter `"n"` (∉ binders, ∉ header letters).
- **A2 — reduction-form induction-null.** Bare `\s.s =` made the model ramble;
  the floor items are now `(\z.z)(\s.s) → \s.s` (fits the `EXPR = NF` few-shot,
  forces the copy emission).
- **A4 — `varof` token matching.** The body variable fuses with punctuation
  (`\y.y` → tokens `['\', 'y', '.y']`; the body `y` lives inside `.y`). Match
  by **alphabetic content** (`varof('.y')='y'`), else the resolving emission
  mis-locates onto the binder. (The v1 smoke measured the wrong position.)
- **A3 — CROSS-FAMILY join (the real design change, Michael GO).** The behavior
  is ~uniformly naive (s332), so the within-family ρ_join (mis-attend ⇒
  naive-vs-hygienic) is structurally degenerate. Reframe:
  - **IND redefined** = the **OUTPUT shadow-binder** position (a *matched*
    competitor present in BOTH families: capture `\y.y` collision vs control
    `\y.n` non-collision), so `r_control` is a real ratio, not trivially 1.
  - **G3′** = **D_scope** = `mean(r_control) − mean(r_capture) > 0` (two-sample
    permutation, p<0.05) **AND** behavioral capture confirmed. The capturable
    collision pulls the read toward the distractor binder relative to clean
    controls, exactly where behavior captures. **SCOPED-SUBSTITUTION = G2 ∧ G3′.**
  - **ρ_join → advisory** (reported, non-gating).
  - **G1 sub-ceiling requirement dropped** — the cross-family join needs no
    within-family variance, so uniform naive is the *strongest* capture
    confirmation. `g1_naive` = `frac_naive > 0.5` significant.
  - **G0 control sanity → BEHAVIORAL** (`acc_control` = model reduces easy
    no-collision substitutions right, SE0-style) — NOT a high-read requirement,
    so a genuinely induction machine reads **INDUCTION**, not VOID.

The three families now form a clean gradient: **nullind** (identity, correct
source = near binder → r floors) < **capture** (correct = far operand, colliding
binder tempts the near read) ⪅ **control** (correct = far operand, no collision
→ clean read). G2 asks capture r beats the floor/recency (substitution, not
induction); G3′ asks the collision pulls it below clean control (scope-blind).

## Instrument

`src/verbum/driver.py` (s346, validity-gated): `bounce(seal, n, attn=True)`
captures per-emission read-mass `[L,T]`; `read_mass(b, step)` averages heads
over the tape; `fork(seal, alt_text)` for the behavioral differencing;
`lambda_ast` certifies naive vs hygienic NFs and yields the OP/IND positions.
Real measurement re-runs as a named committed harness
(`scripts/experiments/read_head_ledger.py`) — REPL ≡ explore ¬record.
