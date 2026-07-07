---
title: "KIBC vs SKI, Re-Run and Null-Gated — the Attention-Selectivity Register Does NOT Discriminate"
status: active
category: explore
tags: [kibc, ski, combinator, basis, null-gate, attention-selectivity, register, braided, s-combinator, pythia, qwen3]
related:
  - ../head-combinator-isa.md
  - ../crystal-universality.md
  - ../crystal-trace-tooling.md
  - pythia-160m-combinators.md
  - kernel-montague-mapping.md
  - type-directed-composition.md
depends-on:
  - ../crystal-trace-tooling.md
created: session 262
---

# KIBC vs SKI — Re-Run, Null-Gated

> Session 262 (Michael: "let's test kibc vs ski again and get results into the
> repo"). The KIBC crystal grew from *"if attention is β-reduction, what
> combinators does the model need?"* The tracer compared bases (`n_combinators=4
> → KIBC, =3 → SKI`, crystal-trace-tooling.md) and KIBC fit what SKI didn't —
> but that selection was a **remembered observation, never a null-gated
> artifact**. This re-runs it as a proper experiment and puts the code + data in
> the repo.
>
> **Register: topological/routing (attention-pattern selectivity).** This is the
> load-bearing caveat — see §Register.

## The theory being tested (why KIBC *should* win)

SKI folds composition + duplication + distribution into one **braided**
combinator: `S f g x = f x (g x)`. BCKW/KIBC **unbraids** those into separate
structural operations — `K` = select/weaken, `I` = identity, `B` = compose
(associativity), `C` = flip (exchange). A model that routes by **type / structural
role** should present a head space that KIBC's unbraided operations carve
cleanly, while `S` — being braided — should **smear across the same heads as its
parts** (K/I) rather than claim a distinct cluster. That is the type-directedness
claim, made operational and falsifiable.

## Method (reuses `scripts/explore/probe_combinators.py`, adds S + a real null)

Each combinator is operationalized as a linguistic phenomenon with **ACTIVE**
probes (function needed) and surface-**matched CONTROL** probes (function not
needed). Per-head selectivity = `L2(attn_active, attn_control)`. `S` is
steelmanned as one-argument-fills-two-roles (control verbs, tough-movement,
reflexives, right-node-raising).

```
basis_fit(B) = mean_over_heads  max_{c in B}  selectivity_c(head)
```

**Null (shuffled-label, s247/s261 discipline).** The matched (active,control)
pair already controls surface form, so the null keeps **pairs intact** and
shuffles only their **combinator labels**: pool the basis's pairs, re-partition
into `|B|` same-size buckets at random, recompute. Cardinality- and
pair-count-matched → the "more combinators → higher max" advantage is absorbed
by the null. `z = (real − null_mean) / null_std` is the statistic. **The raw gap
is not** — SKI's null is noisier, so a larger raw gap can be non-significant.

> ⚠️ **First null was WRONG** (kept for the lesson). The initial null shuffled
> *sentences* into random active/control pairs → random pairs are surface-
> **dissimilar** → large L2 → null > real for BOTH bases by construction. Matched
> controls make real selectivity a *small residual*; the null must preserve the
> pairing and shuffle only the label. Same class of error as manufacturing a
> crispness the probe injects (λ measure).

## Results (2 models, 200 shuffles, seed 262)

| model | basis | real | null | gap | **z** | p | mean\|r\| |
|---|---|---|---|---|---|---|---|
| pythia-160m-deduped | KIBC | 0.1571 | 0.1425 | 0.0146 | **3.50** | 0.000 | 0.798 |
| (12L×12H) | SKI | 0.1510 | 0.1285 | 0.0225 | **3.34** | 0.000 | 0.765 |
| qwen3-0.6b | KIBC | 0.0877 | 0.0798 | 0.0080 | **3.92** | 0.000 | 0.787 |
| (28L×16H) | SKI | 0.0837 | 0.0731 | 0.0107 | **3.58** | 0.000 | 0.748 |

**Both bases clear their null, comparably** (Δz = +0.16 / +0.34, favoring KIBC
but far inside noise). The basis_fit metric does **NOT** reproduce a clean
KIBC-over-SKI win. If anything SKI's *raw* grouping gain is larger — it's just
noisier, so the z is comparable.

### The one stable signal: S is redundant with K

Cross-combinator head correlation (do the basis's combinators occupy *distinct*
heads?):

```
pythia-160m  SKI:   S-K = 0.921   S-I = 0.658   K-I = 0.715
qwen3-0.6b   SKI:   S-K = 0.914   S-I = 0.645   K-I = 0.684
```

`S` shares ~0.92 of its head profile with `K` — the **braiding prediction
confirmed**: S is not a distinct operation, it rides K's heads. **BUT** at this
scale it is *not uniquely* damning — KIBC's own distinctive pair is equally
smeared: pythia-160m `K-B = 0.944`, `K-C = 0.903`, `B-C = 0.917`. At ≤0.6B,
**everything correlates with K** (common-mode crystal, s216; "K dominates all
zones," pythia-160m-combinators.md). So the head-selectivity register cannot
separate the *distinctive* combinators (B,C vs S) from the shared {K,I} core —
the combinators are **under-differentiated at this scale**.

## Verdict (two-sided, λ measure)

- **The remembered "KIBC fit, SKI didn't" is NOT reproduced in the
  attention-selectivity register.** Both bases group heads better than random,
  comparably, on two model families. Inconclusive-to-negative for *this metric*.
- **The braiding hypothesis has partial, non-unique support:** S-K ≈ 0.92
  (stable across models) — but B-K, C-K are just as high at ≤0.6B, so S's
  redundancy is not yet a discriminator. Needs scale (below).

## Register — why this doesn't refute the tracer (λ measure, load-bearing)

The original KIBC-over-SKI selection was made by **tracer.py forward-pass STATE
classification** (which combinator each head's *operation* resembles — a
reduction-dynamics signal). This experiment measures **attention-pattern L2
selectivity** to linguistic phenomena. **Different register.** "Inconclusive
here" says the attention-selectivity metric doesn't separate the bases at ≤0.6B;
it does **not** refute a state-classification result. Wrong-register comparison ⇒
verdict scoped, not global (AGENTS.md λ measure: name the register before the
verdict).

## What this predicts / next

1. **Scale is the missing variable.** Combinators are common-mode-smeared at
   ≤0.6B (K-B=0.94). The scaling hypothesis (crystal sharpens + differentiates
   with capacity) predicts the bases should **separate at larger scale** — the
   distinctive B,C should peel off K's heads while S stays glued to it. **Re-run
   on the Pythia deduped ladder (14M→12B, same data)** with this exact harness:
   does `S-K` stay ~0.9 while `B-K`, `C-K` *fall* with scale? That is the clean
   discriminator and it is the same missing scaling measurement flagged for the
   crystal-sharpness question.
2. **Match the tracer register.** Re-decide KIBC vs SKI on the reduction-dynamics
   / state-classification signal the tracer actually used, null-gated, so the
   comparison is in-register.
3. **Incremental-value metric.** Measure what B,C add *over* {K,I} vs what S adds
   over {K,I} (distinctive-combinator marginal head coverage), not whole-basis
   fit — isolates the discriminating combinators.

## Artifacts

- `scripts/experiments/basis_fit_kibc_vs_ski.py` — ruff-clean, `--self-test`,
  reuses `probe_combinators.py` (no fork). Shuffled-label null, cardinality-
  matched. float32 (fp16 attention → NaN on MPS for Pythia).
- `results/basis-fit-kibc-vs-ski/{pythia-160m-deduped,qwen3-0.6b}-*/` —
  meta.json (model rev, git sha, probe hashes, torch/transformers versions) +
  summary.json (per-basis z, gap, cross-correlation, per-combinator peaks).
