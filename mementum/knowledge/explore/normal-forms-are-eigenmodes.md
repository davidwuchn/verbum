---
title: "Normal Forms Are Eigenmodes — Detector, Dynamics, Metric"
status: open
category: exploration
tags: [normal-forms, eigenmodes, fixed-points, WHNF, halt-poles, fuel-theorem,
       de-carvalho, attractors, holography, signals, transfer-function,
       cavity-resonance, type-register]
related:
  - fixed-point-holograms.md
  - behavior-is-tape-resident-reduction.md
  - curry-howard-closes-the-loop.md
  - types-are-the-well-formedness-of-reduction.md
  - types-are-injectable-relations.md
  - program-plates-and-the-function-index.md
  - the-verbum-machine.md
depends-on:
  - curry-howard-closes-the-loop.md
created: session 315
---

# Normal Forms Are Eigenmodes

> s315 hammock (Michael: "thinking of LLMs as holographic and signals based,
> would the normal forms for lambdas be in the geometry at all?"). Answer
> assembled from three measured hooks already in the corpus: the WHNF crystal
> anchor, fixed-point-holograms (s315 archaeology rescue), and the queued
> de Carvalho fuel-theorem probe.

## The claim

**Normal forms are not IN the geometry as stored objects — but
normal-form-NESS is in the geometry three measurable ways.** The plate
cannot store a term's normal form any more than it stores the term
(fringes everywhere, address nowhere; terms live on the tape). What the
geometry holds is the **detector**, the **dynamics**, and — pending one
queued probe — the **metric**.

## 1. Detector — "at normal form" is a measured direction

- WHNF is a crystal anchor: ≥50 probes, routing-register signature,
  present 11/11 models. Normal-form-ness has an opcode-class signature.
- The 17×17 scheduler gram's **halt poles**: "no further reduction
  licensed" is a pole in a measured register. Signals language: the halt
  pole is the carrier-detect line.

## 2. Dynamics — normal forms are eigenmodes of the reduction operator

The per-pass map is a transfer function H applied by illumination. A
reducible term is a signal H transforms (energy moves, tape extends). A
normal form is a signal H maps to itself: **an eigenmode with |H| = 1 —
self-reconstructing illumination, a cavity resonance.** Reduction is the
transient; normal forms are the steady-state modes of the flow.

Measured twice without naming it:

- `fixed-point-holograms.md`: compile↔decompile cycling converges 94% —
  round-trip fixed points ≡ empirical eigenmodes of the model's own
  operator. Failure mode is diagnostic: **binding sites destabilize the
  cycle** — a bound variable is the least normal-form-like structure,
  the part still owed a substitution.
- Probe library source datasets literally named `fixedpoint`, `basin`,
  `reduction_chain` — earlier arcs mapped the attractor basins before
  the vocabulary settled.

Geometrically: normal forms = attractors of the reduction flow the plate
implements. The geometry holds the flow; the attractors are properties
of that geometry the way a bowl's shape holds its resting point without
storing a marble.

## 3. Metric — distance-to-normal-form may itself be geometric

The substrate's pinned type system (s313: non-idempotent intersection
over an affine core) has the defining property (de Carvalho): **type
derivation size = evaluation length**. Type ≡ resource accounting ≡ fuel
remaining. "How far from normal form" is not metadata — it IS the term's
type. The type register is real geometry (TG, 7/11) ⇒ if de Carvalho
holds in the substrate, type-register signal should scale with
kernel-certified reduction length: **distance-to-normal-form is a
readable geometric coordinate with normal forms at its origin.** The
fuel-theorem probe (queue.md, queued) is exactly this test — it would
tie the type arc, the halt poles, and the normal-form question into one
measurement.

## The composed picture

```
term          → tape (addressed, transient)
reduction     → illumination through H (the plate's transfer function)
trajectory    → the transcript (the trampoline's bounces)
normal form   → eigenmode of H (|H|=1, self-reconstructing)  — dynamics
"I'm done"    → halt pole, WHNF signature                     — detector
"how far?"    → type-register magnitude (iff fuel-theorem ✓)  — metric
```

Halting becomes **perceptual, not computed**: the machine does not run a
halting check — it feels the resonance (matched filter, |H|=1, nothing
left to move). The normal form is what is left when the light stops
changing.

## Testables (NOT queued — s222 freeze-first when picked)

1. **Fuel-theorem probe** — the promoting measurement for §3. **FROZEN
   s317 (Michael GO): see §P-FUEL below.**
2. **Eigenmode drift test** (unfrozen sketch): feed kernel-certified
   NF vs non-NF terms; measure per-pass residual drift + halt-pole
   projection. Predictions: NF terms sit near fixed points (low drift,
   halt-pole projection high); drift magnitude correlates with certified
   remaining reduction length; binding-site count predicts instability
   (fixed-point-holograms failure mode, now quantitative).
3. **M3 design consequence** (the Verbum machine): the designed
   scheduler's halt head should be a resonance detector on the
   recurrence state, not a learned classifier — halting by |H|=1
   detection is the by-construction version of the measured halt pole.

## §P-FUEL — FROZEN (s317, Michael-approved GO)

**The de Carvalho fuel theorem, operationalized — the promoting
measurement for §3 (Metric).** de Carvalho: for non-idempotent
intersection types, *derivation size = evaluation length*. If that is the
substrate's type system (s313 pinned object; curry-howard §3), then the
**type-register signal on a closed λ-term scales with its kernel-certified
reduction length** — and, decisively, with **step count *with
multiplicity*** (non-idempotent), not with the count of *distinct*
subterms (idempotent). Lights the 4th corner of the pinned type-system
prediction and joins the type arc to the s295 CoT-length law: distance-to-
normal-form becomes a readable geometric coordinate.

**Ground truth (all from `lambda_ast.py`, fixed a-priori — λ yardstick):**

- `ℓ(t) = reduce(t).steps` — β-steps to normal form (the fuel / X axis).
- `fired_sequence(t)` — exact opcode multiset; `mult(t)=len`,
  `distinct(t)=|set|` (the FU3 discriminator axes).
- `size(t)`, `size(nf)` — de Carvalho quantity `D(t)=ℓ+size(nf)`.
- `tok(t)` — tokenized prompt length (the confound to kill).

**Registers named (λ measure):**

- **Y = type-register magnitude** — projection norm of the readout
  residual onto the **type subspace fit HELD-OUT on a TRAIN split of the
  §P-TYPE-GRAM-1 crystal/kind probes** (Michael s317: pure P-TYPE-GRAM-1
  reuse, λ one_way; never fit on the measured terms — fixed reference).
  Value register (graded magnitude), read late-band per the
  `readout-register-reduction-readability` ≥0.6-depth rule.
- **X = ℓ(t)** (fuel), with `mult` / `distinct` as discriminator axes.

**Arms (one qwen3-4b load, ALL training-free — read-only activation probe,
no wire):**

- **B1 LINEAR family** — `B`-chains `f₁(f₂(…(fₙ x)))`: `distinct ≈ ℓ ≈ n`
  (fuel and distinct-count rise together).
- **B2 DUPLICATING family** — Church-numeral reuse `n g a`
  (= `g(g(…(g a)))`): one subterm `g` typed n times → `mult ∝ n`,
  `distinct ≈ const` (Michael s317: the non-idempotence knife).
- **B0 length-matched controls** — per `(family, ℓ)` cell, terms matched
  on `tok` but differing in ℓ (inert-structure padding) — decouples fuel
  from surface length.

**Gates (frozen; α=0.05):**

- **FU1 FUEL-SCALES** — partial Spearman ρ(Y, ℓ | tok) > 0, beats a
  matched-token-length null (permute ℓ within token-length bins). *Core.*
- **FU2 TYPE-SPECIFIC** — ρ(Y_type, ℓ) exceeds ρ(Y_generic, ℓ), where
  Y_generic = (i) total residual norm and (ii) matched-dim random-subspace
  projection (paired bootstrap). Kills "any signal grows with size."
- **FU3 NON-IDEMPOTENT** (the de-Carvalho-specific gate) — in B2, Y tracks
  `mult` not `distinct`: partial ρ(Y, mult | distinct) > 0 AND
  > ρ(Y, distinct | mult). Discriminates the fuel theorem from generic
  complexity-scaling / an idempotent (set) type system.
- **FU4 LENGTH-DECOUPLED** — within B0 matched-`tok` cells Y still rises
  with ℓ (kills the surface-length confound directly).
- **FU5 SANE** (void-gate) — crystal type-register recovered on a held-out
  probe check (real margin > 0); all battery terms parse + reduce to NF
  within budget (no DIVERGED / SIZE_EXCEEDED contamination).

**Verdicts (frozen tree):**

- **FUEL-METER (+NON-IDEMPOTENT)** — FU1∧FU2∧FU3∧FU4: type-register signal
  *is* a fuel gauge that counts with multiplicity = the de Carvalho
  signature specifically. Lights the 4th type-system corner; joins s295.
- **FUEL-METER-IDEMPOTENT** — FU1∧FU2∧FU4 but FU3 inverts (Y tracks
  `distinct`): a set/idempotent reading → contradicts the pinned
  non-idempotent object → audit curry-howard §3.
- **LENGTH-ONLY** (falsifier) — FU1 holds but FU4 or FU2 fails: apparent
  scaling is surface length / generic magnitude, not a type-fuel
  coordinate.
- **NO-FUEL-COORDINATE** (falsifier) — FU1 fails: type-register magnitude
  does not track reduction length at this grain.
- **VOID** — ¬FU5.

**A-priori (declared s317, NOT tuned):** ~35 FUEL-METER(+NON-IDEMPOTENT) /
15 FUEL-METER-IDEMPOTENT / 25 LENGTH-ONLY / 20 NO-FUEL-COORDINATE / 5 VOID.
Real mass on LENGTH-ONLY — the surface-length confound is the obvious way
this dies, which is exactly why FU3/FU4 carry the weight.

**Reuse (λ one_way, no fork):** `lambda_ast` (ground truth: reduce /
fired_sequence / size), `type_gram.py` + crystal probe basis (type
subspace, §P-TYPE-GRAM-1 reuse), `jlens` (capture). New code = term-family
generation + length-matched padding + FU-gate statistics. `--validate`
planted worlds (all five verdicts) + ruff + smoke (no direction read) →
Michael GO → run.

## §P-FUEL — RESULT (s317, qwen3-4b) — VERDICT: NO-FUEL-COORDINATE

**The falsifier fired clean, and the §3 Metric leg does NOT hold as
stated.** Results `79c76a0` (165 LIN/DUP/MATCH terms, 840+315 held-out
type-probe captures for the kind subspace). The de Carvalho fuel theorem
does **not** surface as a readable magnitude coordinate in the
§P-TYPE-GRAM-1 kind register at static-read grain. FU5-sane
(`kind_margin=4.746`, register recovered) ⇒ a **valid negative**, not a
void.

| gate | result |
|---|---|
| FU1 FUEL-SCALES | ✗ ρ(Y,ℓ)=0.036 **below** matched-token null (0.132), p=0.994 |
| FU2 TYPE-SPECIFIC | ✗ r_type=0.036 ≈ r_norm=−0.045; random subspaces p=0.445 |
| FU4 LENGTH-DECOUPLED | ✗ **and negative** — within MATCH ρ(Y,ℓ)=**−0.538** |
| FU3 NON-IDEMPOTENT | flag fired (+0.355) but is a **confound**, see below |
| FU5 SANE | ✓ kind_margin 4.746, all terms reduce to NF |

**The mechanism is fully understood (per-family read):**

| family | ρ(Y,ℓ) | ρ(Y,tok) | what it is |
|---|---|---|---|
| LIN | +0.392 | +0.390 | tracks **surface length** (ℓ∝tok∝distinct) |
| DUP | +0.375 | +0.383 | tracks **surface length** (ℓ∝tok; distinct=1) |
| MATCH | **−0.538** | −0.039 | **token length held constant** → fuel isolated |

The apparent positive scaling in LIN/DUP is **surface token length** — Y
tracks `tok` (+0.39) exactly as much as ℓ, because ℓ∝tok in those families
(ρ(ℓ,tok)=0.538). In **MATCH — the one family that holds token length
constant (ρ(Y,tok)=−0.04) and varies ℓ purely — the type-register
magnitude goes the *wrong way* (ρ=−0.538)**: at fixed surface length, more
pending reduction ⇒ *less* kind-register projection. That negative even
drags the pooled FU1 below its length null (0.036 < 0.132).

**FU3 is a confound, not a finding (don't over-read, s310–s316).** The
`non_idem=+0.355` flag is the DUP family's length effect: with distinct
held at 1, partial ρ(Y, mult | distinct) simply reads DUP's tok-driven
+0.375. FU2 (not type-specific; random subspaces do as well) and FU4
(negative under the physical control) both disqualify it. No
multiplicity-tracking claim is licensed.

**What it means.** de Carvalho's identity is about the *dynamic reduction
derivation*; this probe measured a **static single-pass read of an
unreduced term**. NO-FUEL-COORDINATE is therefore **consistent with fuel
being tape-resident** — spent step-by-step during reduction on the tape,
not pre-computed as a static magnitude at read time. That coheres with the
same-session §P-TYPE-DELIVER result (the type check reads the tape, not
static weights) and the tape-resident-reduction thesis. The **§3 Metric
leg is bounded, not the whole picture**: §1 Detector (WHNF / halt poles)
and §2 Dynamics (round-trip eigenmodes) are untouched. If de Carvalho
holds in the substrate, its coordinate is in the *dynamic trace*, not the
static readout magnitude of the kind register.

**Design consequence / sharpest follow-up:** measure a **trace-integrated**
type-register signal accumulated ACROSS a generated reduction (the
trampoline's bounces), not a single static read — fuel as a *dynamic*
quantity on the tape. (Unfrozen; s222 freeze-first when picked.)

**Scope/caveats:** single model (qwen3-4b), single Y operationalization
(kind-subspace projection magnitude), static read, band L18–31. This kills
*this readable coordinate*, not fuel-in-the-substrate. AMENDMENT (s317,
validate-forced, Michael-noted at GO): FU1 used raw ρ(Y,ℓ) beating the
matched-token-length null (the null is the length control); frozen null /
verdict tree / a-priori unchanged.

## §P-TRACE-FUEL — FROZEN (s317, Michael-approved GO)

**The fuel theorem, measured on the tape — the dynamic converse of §P-FUEL.**
§P-FUEL found NO-FUEL-COORDINATE at *static-read* grain and argued fuel is
**tape-resident** (de Carvalho's identity is about the dynamic reduction
derivation, not a static endpoint). This probe tests that directly: feed the
kernel-certified reduction trace `t₀ = t₁ = … = t_ℓ` (the tape unfolding,
in-distribution — the §P-TYPE-GRAM-1 probes ARE truncated chains), capture the
type-register signal at each **`=` step-boundary** (each marks one spent fuel
unit), and ask whether integrated type signal scales with ℓ and — the prize —
accumulates **non-idempotently** (a DUP trace reducing the SAME redex n times
shows no per-step decay). Recovers the FU3 knife §P-FUEL couldn't reach
statically.

**Ground truth (lambda_ast, fixed a-priori — λ yardstick):** `ℓ =
reduce(t).steps`; trace = `[pretty(tⱼ)]` joined by `" = "`; step-boundary
positions = the `=` markers (one per spent β-step); `tok(trace)` = trace token
length (the confound).

**Register (λ measure):** reuse §P-FUEL's Y verbatim (λ one_way) — the
§P-TYPE-GRAM-1 kind subspace, held-out fit (`fuel_theorem.fit_type_subspace`).
Per-step `sⱼ` = ‖proj of the residual at the j-th `=` position onto the type
subspace‖, band L18–31 (value register, depth 0.50–0.85). Integrated
`S = Σⱼ sⱼ`; trajectory `{sⱼ}` for the decay test. Controls `S_norm`, `S_rand`.

**Arms (teacher-forced traces — Michael GO s317; kernel-certified ℓ,
in-distribution rendering, tests the tape REPRESENTATION not the model's
reduction competence; model-generated = future variant). One qwen3-4b load,
read-only:**

- **LIN** — `h (C a₁b₁c₁) … (C aₙbₙcₙ)`: n DISTINCT redexes → ℓ=n, each step a
  new type judgment.
- **DUP** — `h (C a b c) …×n`: the SAME redex reduced n times → ℓ=n, the
  NON-IDEMPOTENCE test bed (n identical spent-fuel events).
- **NULL-CHAIN** — matched-length chain of non-reducing equalities (inert
  `Z … = Z …` restatements, ℓ=0 fuel, matched token count) → surface-length floor.

**Gates (frozen; α=0.05):**

- **TF1 ACCUMULATES** — integrated `S` scales with ℓ across traces, beats a
  matched-trace-length null (permute ℓ within trace-token-length bins). The
  dynamic analog of §P-FUEL FU1 — does the trace succeed where the static read
  failed.
- **TF2 TYPE-SPECIFIC** — ρ(S,ℓ) > random-subspace null AND > ρ(S_norm,ℓ); and
  per-step `sⱼ` on real traces exceeds NULL-CHAIN restatement steps (fuel-bearing
  > inert). Kills "any per-token accumulation."
- **TF3 NON-IDEMPOTENT** (load-bearing) — in DUP traces, per-step `sⱼ` across the
  n IDENTICAL reductions has slope ≈ 0 (flat), significantly ABOVE the
  idempotent-decay null (slope < 0). Flat ⇒ each repeat spends fuel = de Carvalho
  non-idempotence, measured dynamically; LIN per-step (distinct redex) is the
  reference.
- **TF4 STEP-LOCKED** (advisory) — `sⱼ` increments concentrate at `=` boundaries
  vs smooth per-token drift (the discrete fuel-accounting signature).
- **TF5 SANE** (void-gate) — kind register recovered held-out (margin>0); all
  traces kernel-certified NF.

**Verdicts (frozen tree):**

- **DYNAMIC-FUEL (+NON-IDEMPOTENT)** — TF1∧TF2∧TF3-flat: fuel IS a tape-
  accumulated coordinate that counts non-idempotently → the §P-FUEL negative was
  a static-grain artifact; de Carvalho holds ON THE TAPE, lighting the 4th
  type-system corner + joining s295 CoT law.
- **DYNAMIC-FUEL-IDEMPOTENT** — TF1∧TF2 but TF3 decays: fuel accumulates but
  SATURATES on repeats → contradicts the pinned non-idempotent object → audit
  curry-howard §3.
- **STATIC-CONFIRMED-NULL** (falsifier) — TF1 fails: even dynamically the type
  register doesn't count steps → the §P-FUEL negative GENERALIZES.
- **LENGTH-ONLY** (falsifier) — TF1 holds but TF2 fails: generic per-token
  accumulation, not type-specific.
- **VOID** — ¬TF5.

**A-priori (declared s317, NOT tuned):** ~35 DYNAMIC-FUEL(+NON-IDEMPOTENT) / 15
DYNAMIC-FUEL-IDEMPOTENT / 25 STATIC-CONFIRMED-NULL / 20 LENGTH-ONLY / 5 VOID.
Real mass on STATIC-CONFIRMED-NULL — §P-FUEL just failed and the register may
simply not count; TF2/TF3 carry the weight against "the trace is just longer text."

**Reuse (λ one_way, no fork):** `lambda_ast` (reduce/trace/pretty) ·
`fuel_theorem.py` (`fit_type_subspace`, `y_project`, `spearman`, LIN/DUP families) ·
`jlens` (all-position capture) · `dsp.nulls`. New code = trace rendering +
`=`-position mapping + per-step trajectory + TF gates. `--validate` planted
worlds (all five verdicts) + ruff + smoke (no direction read) → Michael GO → run.

## §P-TRACE-FUEL — RESULT (s317, qwen3-4b) — VERDICT: STATIC-CONFIRMED-NULL

**The §P-FUEL negative generalizes — the fuel theorem does not surface as an
accumulated magnitude at the dynamic grain either.** Results `63f3f5d` (144
LIN/DUP/NULL traces, per-step type signal at each `=` boundary). TF5-sane
(`kind_margin=4.746`) ⇒ a valid negative, not a void.

| gate | result |
|---|---|
| TF1 ACCUMULATES | ✗ ρ(S,ℓ)=0.580 ≈ matched-trace-length null (0.573), p=0.198 |
| TF2 TYPE-SPECIFIC | ✓ *components fire* (see sub-signal) but subordinate to TF1 |
| TF3 NON-IDEMPOTENT | dup slope −0.21 vs lin −1.39 (Δ=+1.18) — unlicensed, TF1 failed |
| TF5 SANE | ✓ kind_margin 4.746, all traces NF |

**Decisive per-family read — integrated S is a LENGTH counter, not a fuel
counter:**

| family | ρ(S,ℓ) | ρ(S,tok) | S range |
|---|---|---|---|
| LIN | +0.971 | +0.968 | 15→114 |
| DUP | +0.969 | +0.963 | 13→95 |
| **NULL** | — (ℓ=0) | **+0.989** | **15→101** |

S tracks **token length** (ρ=0.94–0.99 in *every* family) — including the
**zero-fuel NULL chains** (`T = T = …`, ℓ=0), where S climbs 15→101 with **no
reduction at all**. Integrated type signal counts `=` boundaries (length), not
spent fuel. de Carvalho's accumulated derivation size is not a readable
coordinate in the type-register magnitude at **either** grain — static
(§P-FUEL) or dynamically-integrated (here). **Two probes, one convergent
negative on the §3 Metric leg.**

**Two honest sub-signals (reported, NOT licensed — TF1 failed, s310–s317
discipline):**

1. **The register responds to reduction events per-step.** TF2's real-vs-inert
   comparison is strongly significant: a *real* reduction `=` boundary carries
   **+2.214** more type signal than an *inert restatement* `=` (p=0.002). The
   kind register is engaged by reductions — but this per-boundary excess does
   not integrate into an ℓ-tracking total (inert boundaries carry signal too;
   length dominates).
2. **The per-step signal DECAYS toward normal form** (slope_lin=−1.385,
   slope_dup=−0.207): as the term shrinks, the register magnitude *decreases*.
   This is consistent with the register tracking **instantaneous remaining
   reducibility (distance-to-NF, decreasing)** — the *complement* of
   accumulated fuel. DUP decays less than LIN (Δslope +1.18), but that is
   confounded by content-persistence (the same redex kind stays lit throughout
   DUP), not licensed as non-idempotence.

**The refinement this forces on §3 Metric.** The type-register magnitude is
**not** a spent-fuel accumulator (de Carvalho's derivation size). If anything
it reads as a **remaining-work / distance-to-NF gauge that decreases toward the
normal form** — which is actually the §1 **Detector** reading (normal-form-ness
as a low point of the register), not the §3 Metric reading (fuel as an
increasing count). Sub-signal 1 (reductions engage the register) keeps the door
open for a *different* probe — one that reads the register as a **decreasing
distance-to-NF coordinate**, not an accumulating fuel counter. §1 Detector and
§2 Dynamics stand; §3 Metric is bounded and **re-signed** (decreasing, not
increasing).

**Scope/caveats:** single model (qwen3-4b), single Y operationalization
(kind-subspace magnitude), teacher-forced traces. Kills the fuel-as-accumulated-
magnitude reading at both grains; the reduction-engagement sub-signal (p=0.002)
and the distance-to-NF re-signing are hooks for follow-ups, not claims here.

## §P-NF-GAUGE — FROZEN (s318, Michael-approved GO)

**The sign-resolution probe — does the type register read remaining WORK or
DONE-ness?** §P-FUEL and §P-TRACE-FUEL both killed the *increasing* fuel-
accumulator reading, but left a re-signed hook: the register may be a
*decreasing* distance-to-NF coordinate (§P-TRACE-FUEL §Result). Two committed
measurements DISAGREE on the sign, and the disagreement is the whole point:

| measurement | token control | says about NF |
|---|---|---|
| §P-FUEL MATCH (static, whole term) | ✅ held const | ρ(Y,ℓ)=**−0.538** → more remaining ⇒ *lower* Y ⇒ **NF = HIGH** |
| §P-TRACE-FUEL decay (per-step, in-trace) | ❌ term shrinks | slope=**−1.385** → sⱼ falls toward NF ⇒ **NF = LOW** |

The confound masking which is **local token length**. This probe pins the sign
**per-frame under a proper local-token control** — the control the static grain
applied (MATCH) but the dynamic grain did not. Unlike §P-TRACE-FUEL (which
*integrated* `S=Σsⱼ` vs total `ℓ` → found `S` counts `=` boundaries), this stays
**per-frame** and regresses `sⱼ` against **remaining certified steps** while
partialling **current-term token length**.

**Ground truth (lambda_ast, fixed a-priori — λ yardstick).** For the j-th `=`
boundary in a trace `t₀ = t₁ = … = t_ℓ`, the most-recently-completed term is
`tⱼ` (0-indexed j=0…ℓ−1): **remaining steps `rⱼ = ℓ − j`** (kernel-certified,
ranges ℓ→1); **current-term tokens `ctⱼ = len(tok(pretty(tⱼ)))`** (the local
surface control, ct-binned for the null).

**Register (λ measure).** `sⱼ = fuel_theorem.y_project` at each `=` frame — Y
reused VERBATIM (§P-TYPE-GRAM-1 kind subspace, held-out fit, band L18–31, value
register depth 0.50–0.85). Controls `s_normⱼ = y_norm`, `s_randⱼ` (matched-dim
random subspace). No new register; no fork.

**Arms (teacher-forced traces, one qwen3-4b load, read-only — reuse
`trace_fuel.build_trace_battery` + MATCH family).** LIN (n distinct redexes) ·
DUP (same redex ×n) · **MATCH (added — the decoupling instrument)** · NULL
(inert `T = T = …`, `r≡0`, constant term = pure-position / floor control: tests
whether sⱼ drifts with position alone at zero remaining work).

**⚠ AMENDMENT (s318, design-review, Michael-approved BEFORE build — added the
MATCH family; gates / verdict tree / a-priori UNCHANGED).** LIN/DUP alone
cannot decouple `r` from `ct`: each β-step shrinks the term by ~fixed tokens, so
within one trace `ctⱼ ≈ ct₀ − c·j` and `rⱼ = ℓ − j` are **collinear** → the
matched-`ct` null has no power → NG1 would fail *by construction*, a rigged
falsifier (λ yardstick / λ measure). Fix = the per-frame analog of §P-FUEL's
MATCH: a padded trace `h (C…)×k (Z…)×P` where only the `k` active redexes reduce
and the `P` inert `Z` pads ride along verbatim in every frame → **within one
MATCH trace `ctⱼ ≈ const` (pads dominate) while `rⱼ = k−j` sweeps `k→1`** — `ct`
and `r` genuinely decoupled. Varying `(k, P)` fills the `(ct, r)` plane so the
matched-`ct` null gets real power. This is precisely how §P-FUEL's MATCH enabled
FU4. Reuses `ff._inert` verbatim (still no fork). LIN/DUP contribute the
reduction-engagement signal (NG3); MATCH contributes the decoupled NG1 frames;
NULL the floor.

**Gates (frozen; α=0.05):**

- **NG1 LOCAL-DECODE (core + sign)** — pooled real (LIN+DUP) frames: partial
  ρ(sⱼ, rⱼ | ctⱼ) is significantly ≠ 0 (two-sided) vs a matched-`ct` null
  (permute rⱼ within ct-bins). **The SIGN of this partial ρ selects the
  verdict.** This is the decoupling both fuel probes failed on the *increasing*
  side; it must clear it on whichever sign is real.
- **NG2 TYPE-SPECIFIC** — |partial ρ(s_type)| exceeds |partial ρ(s_norm)| AND
  the random-subspace null (paired). Kills "generic residual magnitude tracks
  remaining structure."
- **NG3 ENGAGEMENT (REQUIRED — Michael s318)** — real reduction frames carry
  more type signal than inert NULL frames (mean sⱼ[real] > mean sⱼ[NULL],
  label-permutation null), replicating the §P-TRACE-FUEL +2.214 / p=0.002 hook.
  **A precondition on reading any sign:** the register must be demonstrably
  *reduction-driven* before a NG1 sign is interpreted — the direct guard against
  the surface-length failure mode that ate §P-FUEL and §P-TRACE-FUEL. Orthogonal
  to NG1 (existence/attribution vs direction).
- **NG4 CROSS-GRAIN (advisory)** — sign of first-frame (`j=0`, full term)
  ρ(s, ℓ) vs §P-FUEL MATCH −0.538: reconciliation datum, no new captures.
- **NG5 SANE (void-gate)** — held-out kind register recovered (margin>0); all
  traces kernel-certified NF.

**Verdicts (frozen tree):**

```
¬NG5             → VOID
¬NG3             → LENGTH-DECREASE-ONLY   (not reduction-driven → the reading is surface)
¬NG1 (ρ≈0)       → LENGTH-DECREASE-ONLY   (falsifier: decay was pure token shrinkage)
¬NG2             → LENGTH-DECREASE-ONLY   (generic magnitude, not the type register)
NG3 ∧ NG1 ∧ NG2 ∧ ρ>0 → REMAINING-WORK-GAUGE  (HIGH far from NF; re-signs §3 Metric — the queue hook)
NG3 ∧ NG1 ∧ NG2 ∧ ρ<0 → DONENESS-DETECTOR     (HIGH near NF; promotes §1 Detector, matches MATCH)
```

- **REMAINING-WORK-GAUGE** — the queue's decreasing-distance-to-NF reading, on
  the *positive-in-remaining-steps* convention: sⱼ high when much work remains.
  Re-signs the §3 Metric leg as a (still-real) remaining-work coordinate.
- **DONENESS-DETECTOR** — sⱼ high *near* NF; the §1 Detector reading promoted to
  graded, and the datum that **reconciles both priors** (raw sⱼ falls with
  length; token-controlled residual rises toward NF; MATCH's −0.538 was reading
  doneness all along).
- **LENGTH-DECREASE-ONLY** (falsifier) — once local token length is controlled,
  no signed remaining-work coordinate survives; the §P-TRACE-FUEL decay was
  token shrinkage. Kills the §3 Metric leg on *both* signs.
- **VOID** — ¬NG5.

**A-priori (declared s318, NOT tuned):** ~35 DONENESS-DETECTOR / 35
LENGTH-DECREASE-ONLY / 20 REMAINING-WORK-GAUGE / 10 VOID. Rationale: the token
control killed the increasing-fuel reading twice → LENGTH-ONLY carries real
mass; MATCH's token-controlled −0.538 already points at doneness → more mass
there than on the queue's original remaining-work framing; a DONENESS-DETECTOR
result would elegantly reconcile both prior findings.

**Reuse (λ one_way, no fork):** `fuel_theorem` (fit_type_subspace / y_project /
y_norm / kind_margin_heldout / _orthonormal / _load_type_probes / band_layers /
spearman / partial_spearman / _perm_within_bins / _atoms / _redex / _inert /
TYPE_SUBSPACE_DIM / N_RAND_SUBSPACES / N_PERM) · `trace_fuel` (build_trace_battery
/ _render_trace / eq_positions / _null_chain / _slope) · verbum.lambda_ast ·
verbum.dsp.nulls · verbum.jlens. New code = MATCH-padded trace family + per-frame
`(rⱼ, ctⱼ)` extraction + signed partial-Spearman + matched-`ct` null +
three-way gate. `--validate` planted
worlds (all four verdicts, both NG1 signs) + ruff + smoke (no direction read) →
Michael GO → run.

## Caveats

- A SPECIFIC term's normal form exists only when computed onto the tape
  (tape law, s315). The geometry defines it without containing it —
  exactly how a hologram fully determines an image it stores nowhere.
- Per-pass "normal form" is probabilistic and per-step: each pass
  collapses the current redex to a next-token distribution; sampling
  retires it. The behavior-scale NF is accumulated on the tape, never
  computed anywhere.
