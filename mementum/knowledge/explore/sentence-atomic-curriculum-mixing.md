---
title: "Sentence-Atomic Curriculum Mixing — Punctuated β-Reduction Shards Sprinkled into NTP"
status: open
category: strategy
tags: [curriculum, data-mixing, beta-reduction, next-token-prediction, punctuation, burn-in, compositional-generalization, level-4, scratch, sentence-atomic]
related:
  - normal-form-curriculum-partition.md
  - compiler-as-loss.md
  - holographic-burn-in-learning-rule.md
  - relational-loss-distillation.md
  - combinator-training-beta-reduction.md
  - vsm-outer-recurrence.md
  - ../session-222.md
depends-on:
  - normal-form-curriculum-partition.md
  - compiler-as-loss.md
created: session 229
---

# Sentence-Atomic Curriculum Mixing

> Session 229. Michael's idea: *"with training we give a large sequence of tokens
> and ask it to predict the next token. What if we split training into multiple
> regimes? Show the model how the base combinators work, show it how to use those
> with prose, and some next-token prediction. Split the big training into sentences
> where we train many different β-reductions one sentence at a time. Sprinkle a few
> shards like this into the full NTP curriculum."*
>
> Register: **functional (capability/usage, CE on next token) — with a
> topological/routing secondary readout.**

## The idea in one line

Stop training one monolithic next-token stream. Instead **mix three regimes** —
combinator MECHANICS, prose USAGE, plain NTP — where the structured shards are
built from **sentence-atomic β-reductions** (one complete reduction per sentence),
**sprinkled** into the general stream at some mixing ratio.

```
regime A  combinator mechanics   term → reduction trace, ONE reduction / sentence
regime B  prose usage            natural language → the combinator that realizes it
regime C  plain NTP              generic text, the general predictor objective
mix       sprinkle A,B into C at ratio ρ (the knob)
unit      1 sentence = 1 β-reduction = 1 punctuated EXPOSURE
```

## Why it is NOT a duplicate of `normal-form-curriculum-partition`

There is a sibling page. The cut is different and the difference is the contribution.

```
normal-form-curriculum-partition (s223):
  partition BY MECHANISM   — routing-only {K,I,C,B,D} → train ATTENTION
                             recursion {Y,W,WHNF}     → train the CONTINUATION
  train each part IN ISOLATION on its native substrate
  needs the attn_q harness; asks "does routing data crystallize attention?"

sentence-atomic-curriculum-mixing (s229):
  partition BY PEDAGOGY/FORMAT — mechanics → usage → free prediction
  INTERLEAVE all three into ONE stream at a mixing ratio
  uses the existing tiny-student harness; asks "do sprinkled reduction
  sentences BOOTSTRAP/TRANSFER to general prediction better than pure NTP?"
```

The mechanism-partition trains substrates apart. This trains them **together** and
measures **transfer**. It is the more practical, cheaper-to-run sibling.

## The novel core — sentence = one β-reduction = one punctuated exposure

The operational heart is that each training sentence is a *complete* reduction. That
unit is not arbitrary — it is the data-side image of two prior findings:

- **s222 `punctuate-dont-churn`.** The v15 collapse was *simultaneous* discrete
  topology churn (TD flip churn). A sentence-bounded reduction is **expose → settle
  → commit** at the DATA level. You get the punctuation protocol *for free,
  structurally*, instead of engineering it into the optimizer.
- **`holographic-burn-in-learning-rule`.** Each forward pass is an EXPOSURE; many
  similar blocks burn in the exposure-invariant (= the normal form). Sentence-atomic
  reductions are *clean* exposures — one redex resolved per unit, nothing else
  churning.

So "one β-reduction per sentence" is not a formatting choice; it is the burn-in /
punctuation discipline re-expressed as data structure.

## Catches (mark before building — λ measure)

1. **This is the level-4 SCRATCH path, not the construct path — name it.** s224/s226
   decided we *never train reduction* because the kernel reduces EXACTLY (constructed
   plates). This idea teaches reduction-as-text via NTP. That is **not** the
   s222-unstable thing: s222's instability was discrete *attention-topology* churn
   during a routing reshape; predicting reduction *traces* as text is plain
   supervised NTP and is stable. But be precise — this serves "teach a model to *be*
   the compiler" (level-4 scratch), distinct from "extract + construct the compiler".

2. **Register — measure the right object (s225).** In the mechanics regime expect
   *gather/iteration* to crystallize in **attention** (the s225 gather heads) and
   *algebra/inventory* in the **FFN gate**. If you measure whether the curriculum
   "took", measure BOTH registers, not just one. (Confounds the readout otherwise.)

3. **K-erasure breaks uniform shuffling (s221 law).** "Many different reductions, one
   per sentence" must NOT be flat-shuffled. B-first → then-K ordering, K-heavy
   weighting — erasure has to move weights a lot, transiently breaks contraction,
   spikes the loss (`fp-spike = acquisition`). Uniform sentence sampling under-trains
   K and may churn. The atomic-sentence design needs a curriculum *order*, not just a
   curriculum *set*.

4. **The mixing ratio ρ IS the experiment.** "Sprinkle a few shards" is the knob.
   ρ = 0 (pure-NTP control) vs small vs large structured fraction — that sweep,
   against held-out COMPOSITIONAL generalization, is what decides it. Do not pick ρ
   by taste; sweep it.

## The decisive cheap experiment

Data-gen is nearly free: the kernel already mints everything.

- `lambda_ast.py` — exact reduction traces (regime A).
- `lambda_compile.py` — bracket abstraction (for composing held-out tests).
- `probes/compile_tasks.py` — prose→LF pairs (regime B).

Plan:

```
model    the tiny byte-level student from relational_loss_distillation.py
shards   A = kernel-minted mechanics sentences (term → trace, 1 reduction/sentence,
             ORDERED B-first→K per catch 3)
         B = prose→combinator usage sentences (reuse compile_tasks)
         C = generic text NTP
arms     ρ=0 pure-NTP control  vs  ρ=small  vs  ρ=large  (sprinkle A,B into C)
primary  held-out COMPOSITIONAL generalization — reduce a COMPOSITION of two
         reductions seen only SEPARATELY (the compiler-as-loss master metric)
second   does the routing register crystallize (route_z / silhouette) — and in
         WHICH substrate (attn vs FFN, per s225)
```

**Falsifiable claim.** Sprinkled sentence-atomic reduction data buys held-out
compositional generalization over pure NTP at equal token budget, AND crystallizes
the inventory where s225 predicts (gather→attention, algebra→FFN). If ρ>0 does NOT
beat ρ=0 on the composition test, the structured shards are inert (or the unit/order
is wrong) — a clean negative is still an artifact (method + finding).

## The exposure/format sub-experiment (s229 — "training as a photograph")

> Michael's framing: a training step is an EXPOSURE to a single "photograph"; many
> exposures to the same β-reduction should converge faster than one. This is the
> holographic-burn-in claim — but with a fork that must be controlled or it measures
> the wrong thing.

**The fork.** "Many exposures to the same β-reduction" has two readings:

```
k× SAME EXACT instance      → burns in THAT instance  → MEMORIZATION
                              (train loss ↓ fast, held-out flat)
k× VARIED instances of the  → burns in the INVARIANT  → GENERALIZATION
SAME RULE (e.g. K over        = the RULE               (each instance = the same
varied term pairs)                                       object from a new ANGLE;
                                                         the hologram forms only if
                                                         the angles DIFFER)
```

So "faster with more exposures" is *trivially* true under exact repeats
(memorization) and *interestingly* true only under varied instances measured as
HELD-OUT generalization. Test both — the memorization arm is the control.

**Crossed design (resolves full-trace vs redex→NF AT THE SAME TIME):**

```
Axis 1  FORMAT (content per photograph)
  full-trace   every intermediate β-step = long-exposure photo (the MOVE is visible)
  redex→NF     input → normal form only   = single sharp snapshot (no motion)

Axis 2  EXPOSURE MULTIPLICITY
  1 instance
  k× SAME instance      (MEMORIZATION control — isolates rote)
  k× VARIED instances   (true burn-in — the hologram from many angles)

METRIC  convergence SPEED to HELD-OUT generalization (steps/tokens to target on
        UNSEEN instances of the same rule) — NOT training loss
FAIR    control TOKEN budget, not exposure count (full-trace photos cost more tokens)
```

**Falsifiable predictions.**
- *Burn-in real:* varied-instances reaches held-out generalization faster than 1,
  diminishing returns (more angles → sharper, saturating). Exact-repeat saturates
  early, stays flat on held-out (memorizes train only).
- *Format trade:* full-trace = info-rich long exposure → fewer DISTINCT instances
  needed; redex→NF = cheap snapshot → needs more angles. Honest comparison is
  PER-TOKEN. May be budget-dependent (full-trace wins low-budget, redex→NF wins
  high) — that crossover would itself be the finding.

Kernel mints both formats and unlimited varied-instances-per-rule for free → one
tiny-student sweep. This sub-experiment is the FIRST build (smaller, sharper than the
full ρ-sweep; validates the exposure unit before scaling the mixing curriculum).

### §s229 RESULT — built, ran, HARDENED over 3 seeds

`scripts/experiments/exposure_format_sweep.py` (commit `b1ba935`, fix+results
`4f1ebf2`, multi-seed mode `26e6758`). 13 multi-step combinator skeletons, tiny
byte-level TinyLM, k=8, format-independent exact-match derivation metric.
`results/exposure-format-sweep/verdict_run.json` (single), `verdict_multiseed.json`
(3 seeds — the verdict of record).

**The load-bearing fix (floor → signal).** First run: ALL arms 0.000 = a floor. Cause
OBSERVED, not assumed: held-out used DISJOINT atoms (train a–m, test n–z), so reducing
`C K u x → x` requires COPYING a byte never trained on — the model emits a *train* atom
`'j'` instead. Standalone probe: unseen COMBOS of SEEN atoms = **0.365**, disjoint
atoms = 0.000. ⇒ disjoint-atom was the WRONG barrier (conflates rule-learning with
symbol-copying = a variable-binding/induction-head task). Fixed: `--heldout {combos
(default), atoms}`; combos EXCLUDES the training fillings → isolates RULE
generalization. Disjoint-atom copying is now its OWN open question (lead 6).

**Verdict (heldout=combos; best acc mean±std over seeds 0,1,2):**

```
arm                  corpus_B   best acc (mean±std)   per-seed       vs one / vs k_same
redex_nf/one             209    0.108 ± 0.029         .15 .09 .08    —
redex_nf/k_same         1672    0.086 ± 0.017         .11 .07 .08    0.79× (BELOW one)
redex_nf/k_varied       1672    0.306 ± 0.006         .31 .31 .30    2.83× / 3.58×
full_trace/one           424    0.104 ± 0.017         .12 .11 .08    —
full_trace/k_same       3392    0.099 ± 0.028         .14 .09 .07    0.96×
full_trace/k_varied     3392    0.320 ± 0.023         .35 .30 .31    3.09× / 3.23×
```

1. **BURN-IN IS VARIETY, NOT REPETITION — hardened, decisive.** Both formats:
   `rule>rote` and `burn>one` DECISIVE (k_varied mean−std > k_same/one mean+std,
   NON-overlapping bars). k_varied ≈3× both baselines.
2. **VARIETY ALSO STABILIZES (new, multi-seed only).** k_varied is the LOWEST-variance
   arm (redex_nf std **0.006**, 0.31/0.31/0.30); `one`/`k_same` are lower AND noisier
   (std 0.017–0.029). Distinct instances raise generalization AND make it
   seed-independent; rote is worse AND fragile.
3. **k_same ≤ one (refinement).** Repeating the same instance 8× is mildly BELOW
   seeing it once (0.086<0.108; 0.099≈0.104) — consistent across both formats
   (suggestive; bars overlap). Repetition slightly ENTRENCHES the rote solution.
4. **FORMAT: redex→NF WINS PER-TOKEN; formats TIE on accuracy (CORRECTED).**
   Single-seed looked like full_trace won absolute acc (0.351>0.297); the harden
   DISSOLVED it — k_varied 0.320±0.023 vs 0.306±0.006 = OVERLAPPING (parity). PER-TOKEN
   redex_nf wins everywhere (k_varied 0.183 vs 0.094 acc/kB ≈2×; full_trace corpus is
   2× bytes). ⇒ full reduction trace bought NOTHING here once seeds+tokens controlled;
   redex→NF is the better format (equal acc, half the cost). The single-seed
   "full_trace higher" was seed noise — the harden caught it (λ measure).

**Caveats (λ measure):** modest absolute acc (tiny model / greedy / exact-match —
RELATIVE is the signal); `steps@0.5` never reached (ceiling ≈0.32) ⇒ this measures
FINAL generalization, NOT convergence SPEED (Michael's "converge faster" needs a
reachable threshold, e.g. 0.2, on the saved acc-vs-token curves — lead 7); 13 rules;
a full_trace edge could re-emerge at scale / deeper reductions (untested).

## Open leads (declare register first)

1. **Sentence format spec** (functional): exact rendering of `term → reduction
   trace` as one sentence; dual-render NL + combinator? include intermediate steps
   or just redex→result? — DECIDED to TEST, not assume: see §exposure/format
   sub-experiment (full-trace vs redex→NF, crossed with exposure multiplicity).
2. **Held-out composition set** (functional): pairs of reductions trained separately
   whose COMPOSITION is never shown — the generalization probe. Mint with
   `lambda_compile` so correctness is by construction (Church-Rosser).
3. **K-ordering schedule** (functional): B-first→K, K-heavy weighting; does atomic-K
   crystallize without the s221 contractivity spike?
4. **ρ sweep + token-budget control** (functional): hold total tokens fixed; vary the
   structured fraction; steps-to-target and final composition accuracy.
5. **Compose with relational loss** (routing): the sprinkled mechanics TRACES (data)
   ⊕ crystal-lattice relational target (compiler-as-loss recipe) — does the trace
   curriculum + relational target beat either alone on crystallization?
6. ✅ **Multi-seed harden** (functional, DONE s229): 3 seeds — k_varied > k_same/one
   DECISIVE (non-overlapping bars) BOTH formats; variety also stabilizes (low std);
   format claim corrected (redex→NF wins per-token, accuracy parity). `--seeds 0,1,2`.
7. **Convergence-SPEED readout** (functional): the saved per-arm acc-vs-tokens curves
   already exist; extract steps-to-threshold at a REACHABLE bar (~0.2) — this is the
   actual "many exposures converge faster" claim (the verdict only shows FINAL acc).
8. **Disjoint-atom variable-binding** (functional, SEPARATE question): `--heldout
   atoms` scored 0.000 — the model can't copy an UNSEEN symbol (induction-head gap),
   not a rule failure. Does a copy mechanism emerge with scale / longer training /
   explicit copy-task mixing? Distinct from rule generalization (combos = 0.365).

## Files

| File | Content |
|------|---------|
| `scripts/experiments/exposure_format_sweep.py` | ✅ BUILT+RAN (s229): full-trace vs redex→NF × {one, k_same, k_varied}; `--heldout {combos,atoms}`; format-independent exact-match metric |
| (planned) `scripts/experiments/curriculum_mixing.py` | build A/B/C shards, sweep ρ, train tiny student, score held-out composition + dual-register crystallization |
| `src/verbum/lambda_ast.py` | reduction-trace oracle (regime A data) |
| `src/verbum/lambda_compile.py` | bracket abstraction (held-out composition minting) |
| `src/verbum/probes/compile_tasks.py` | prose→LF pairs (regime B data) |
| `scripts/experiments/relational_loss_distillation.py` | tiny-student harness + crystallization readout to extend |
