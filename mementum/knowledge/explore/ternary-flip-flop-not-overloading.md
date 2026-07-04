---
title: "Ternary Sign Flip-Flop ≠ Category Overloading — CAT-Q ST vs TernaryDescent on micro (null-gated)"
status: active
category: explore
tags: [ternary, from-scratch, catq, softened-ternarization, ternary-descent, flip-flop, oscillation, overloading, holographic, two-registers, sign, magnitude, anova, f-ratio, shuffled-label-null, yardstick, micro, level-4, boundary-jitter]
related:
  - asymmetric-pathway-quantization.md
  - ../two-registers-of-topology.md
  - ../ternary-dual-equation.md
  - ../standing-wave-magnitudes.md
  - moe-holographic-tree-vsm.md
  - supervised-recurrence-halt.md
depends-on:
  - ../two-registers-of-topology.md
  - asymmetric-pathway-quantization.md
created: session 261
---

# Ternary Sign Flip-Flop ≠ Category Overloading

> Session 261. Michael found CAT-Q (arXiv 2606.26650, "Cost-efficient and
> Accurate Ternary Quantization for LLMs") and asked whether its math ports
> from PTQ to TRAINING a ternary model from scratch — specifically as a fix
> for the TernaryDescent (v15/td.py) failure where the sign flip-flops and
> the system never reduces to a normal form. His speculation: GD wants the
> weight to output differently depending on the input — an "overloading" of
> the function. We built the bench, ran it, and the shuffled-label null
> **refined the hypothesis rather than confirming it.**

## The CAT-Q paper, decomposed for transfer

CAT-Q is post-training quantization (learn ternary weights to match a frozen
high-precision teacher on 512 calibration samples). Split into what ports to
from-scratch training and what does not:

| CAT-Q piece | mechanism | from-scratch? |
|---|---|---|
| **Softened Ternarization (ST)** | annealed soft→hard `f(w)=½(tanh(s(w−Δ))+tanh(s(w+Δ)))`, sharpness `s` raised over training | ✅ transfers — a principled STE replacement |
| **Learnable Modulation (LM)** | reparameterize `Ŵ=(w−μ)/α`; learn `α` (scale) and `Δ` (threshold) as separate params | ✅ transfers — a learnable-threshold ternary layer (LSQ-for-ternary) |
| **Sliding-layer output reconstruction** | `argmin‖F(W,X)−F(A·T,X)‖²` against a frozen HP teacher | ❌ drop — no teacher from scratch; end-to-end backprop gives cross-layer awareness for free |

**On-thesis catch:** CAT-Q learns `α` and `Δ` *separately* because the BitNet
absmean coupling (`Δ=α/2`) is distributionally misaligned. That is external,
independent confirmation of the verbum two-registers split — `α`=magnitude/**value**,
`Δ`=threshold/**routing** (which weights become ±1 vs 0). See
`two-registers-of-topology.md`, `ternary-dual-equation.md`.

## Three from-scratch ternary paradigms (verbum already has two)

CAT-Q is not a new idea about sign/magnitude for us — it's a **third paradigm**
for setting the ternary sign from scratch:

| paradigm | sign set by | magnitude set by |
|---|---|---|
| **etch** (v15 ternary.py) | evolutionary mutation + tournament | Adam on `gamma` |
| **TernaryDescent** (v15/td.py, s177) | discrete: flip on accumulated gradient *evidence* (routing⊥calibration split) | Adam on `gamma` |
| **CAT-Q / ST** (new) | continuous: latent float shadow, annealed soft→hard, learned `Δ` | learned `α` |

The right experiment is therefore an **internal A/B**, not "try the paper's
method": does continuous soft→hard relaxation crystallize the discrete router
better than discrete evidence-flip?

## The overloading hypothesis (and why it's plausible)

Michael's flip-flop diagnosis, in s257 terms: a **float** weight can
holographically multiplex several functions (read at different angles); a
**ternary** weight ({−1,0,+1}) can't hold that superposition, so when GD
demands input-dependent output the sign oscillates trying to serve each angle,
never reaching a fixed point. Prediction: the oscillating weights are the ones
different inputs pull in **opposite sign directions**.

## The experiment (Arm 0, on micro)

`scripts/micro/ternary_st.py` — `TernaryShadowLinear`, dual-mode (td | st),
latent float shadow, learned `α` (log-space) and `Δ` (delta_ratio·α), ST
sharpness anneal + straight-through hard stage, per-weight flip instrument.
`scripts/micro/micro_ternary.py` — surgical swap of micro's SwiGLUFFN linears
only (crystal + attention stay float; the FFN ternary paradigm is the ONLY
changed variable; `micro_model.py` untouched — it is the float microscope).
`scripts/micro/train_arm0.py` — trains on the compile corpus, tracks flips,
runs the overloading diagnostic. Three arms: `td`, `st`, `none` (float).

**Reproduction result** (2500 steps, seed 261, single run):

| mode | final CE | oscillating frac | notes |
|---|---|---|---|
| none (float) | **0.454** | — | capacity ceiling |
| td | 0.493 | 0.15 | sign never fully settles (flip rate stays positive) |
| st | 0.507 | 0.15 | *worse* than td; flips resurge at the hard-anneal point |

Solid, null-independent: the flip-flop reproduces; ternary plateaus ~0.04–0.05
CE **above** float; and **CAT-Q's ST did not beat the discrete flip** (st worse
than td), with a flip resurgence exactly at `anneal_frac=0.6` hardening — the
predicted "relaxation defers the conflict, hardening forces a lossy commit."

## The λ yardstick save (the methodological lesson)

**First diagnostic was confounded.** "Contested" was defined via gradient
*magnitude* across categories; high-gradient weights trivially look contested
AND flip more. It reported a 9.8× flip ratio = "overloading confirmed." The
**shuffled-label null reproduced it exactly** (9.88 vs null 10.43) → false
positive. (Same pattern as s206 attention-weight audit, s247 φ-ladder.)

**Fixed instrument: ANOVA F-ratio.** Per-weight `F = between-category variance
/ within-category variance` of the per-example gradient. F is a ratio →
gradient magnitude cancels. Real and shuffled labels accumulated in one pass
(totals are label-independent). Null sits at **F≈0.9–1.0** exactly as ANOVA
predicts — the confound is gone.

## The finding (null-gated, both modes, all 12 FFN modules)

1. **Category structure in the FFN gradients is REAL but modest at convergence.**
   `F_real ≈ 1.2–2.1` vs `F_null ≈ 0.9`. Magnitude-invariant. The weights DO
   receive category-dependent gradients — a real, if weak, version of "wants
   different output per input." It is **strong early, fades late**: F=6.6 at 60
   steps → ~1.6 at convergence → a **transient of learning** the model resolves
   by fitting, not a persistent property. `value_proj` carries the most (F≈2.0),
   gate/key fade with depth — the **value/content pathway** holds the
   category-dependence (on-thesis: value = content register).

2. **The oscillation does NOT track the overloaded weights.** Flip-enrichment on
   the most category-structured (top-F) weights is `real ≈ null` in every module
   (gate 1.24 vs 1.24; value 1.02 vs 1.06). At module level it *anti*-correlates:
   `value_proj` has the highest F but the *lowest* flip-enrichment. So the
   persistent flip-flop is **category-independent**.

**Conclusion:** the "GD wants input-dependent output" intuition is confirmed as
a real gradient phenomenon (F>null, strongest early, strongest in the value
path), BUT at this scale/grain the persistent sign oscillation is **not** caused
by that semantic contention. It looks like **quantization-boundary jitter** —
small-shadow-magnitude weights near ±Δ knocked across by minibatch SGD noise,
independent of category. Supporting: ST's *soft* phase nearly eliminated flips
(no hard boundary to jitter across); hardening revived them. The non-convergence
is likely two separable things braided: a real-but-transient overloading signal
+ a mundane boundary jitter that is what actually never settles.

## Caveats (λ measure)

- micro (500K params), 1 seed, 509 examples. Necessary-not-sufficient.
- **Category is a coarse grain** (13 buckets). Overloading may live finer
  (per-combinator B/S/C/I, per-binding) that category-ANOVA can't see. Absence
  of category-level flip-localization does NOT refute finer-grained overloading.
- ST vs TD single run; the ST-worse-than-TD gap (0.014 CE) is small.

## Implications + next (easy tests first)

- **Combinator-level ANOVA** — regroup by B/S/C/I in `kernel_term` (finer than
  category; directly tests the s257 "angle" reading). One-line grouping change.
- **Jitter discriminator** — if the residual flip-flop is boundary jitter,
  threshold hysteresis / an LR floor near ±Δ should kill it *without* hurting
  loss; if semantic, it won't.
- **Arm 2 (decouple)** — give overloaded weights an escape (crystal-addressed
  routing / 2 value pathways); the real test of "unbraid dispatch⊥compute fixes
  ternary." Must be run *against* the jitter hypothesis, not assuming semantic
  overloading.
- **For a deployable recipe:** ST did not beat TD here; verbum's discrete
  evidence-flip is at least competitive. CAT-Q's real transferable gift is the
  **learnable-`Δ` + learnable-`α` two-register parameterization**, not the
  soft→hard relaxation.

## Artifacts

- `scripts/micro/ternary_st.py` (dual-mode ternary linear + flip instrument, self-test)
- `scripts/micro/micro_ternary.py` (surgical FFN swap, smoke test)
- `scripts/micro/train_arm0.py` (train + ANOVA F-ratio overloading diagnostic + shuffled-label null)
- `results/micro-ternary-arm0/` — canonical set: `none-*` (float baseline), `td-*133841`, `st-*134153` (ANOVA F-ratio runs; smokes + confounded first-pass runs pruned)
- `logs/arm0-s261-anova.log`
- pyproject.toml: RUF001/2/3 ignore for `scripts/micro/ternary_st.py`
