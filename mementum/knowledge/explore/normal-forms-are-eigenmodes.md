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

## Caveats

- A SPECIFIC term's normal form exists only when computed onto the tape
  (tape law, s315). The geometry defines it without containing it —
  exactly how a hologram fully determines an image it stores nowhere.
- Per-pass "normal form" is probabilistic and per-step: each pass
  collapses the current redex to a next-token distribution; sampling
  retires it. The behavior-scale NF is accumulated on the tape, never
  computed anywhere.
