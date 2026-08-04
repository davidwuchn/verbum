---
title: "Ratio Gradient Quantization — Companding the Heavy-Tailed Gradient (Spend Bits on the Ends, Derive the Ratio)"
status: designing
category: strategy
tags: [quantization, gradient, compression, companding, mu-law, precision-inversion, error-feedback, bimodal, heavy-tail, phi, distributed, delta, rate-distortion]
related:
  - ../gradient-zero-map.md
  - relational-loss-phi-compression.md
  - consensus-delta-folding.md
  - consensus-etch-protocol.md
  - exact-ternary-fitting.md
  - ternary-descent.md
  - holographic-burn-in-learning-rule.md
  - ../session-222.md
  - ../crystal-universality.md
depends-on:
  - ../gradient-zero-map.md
created: session 223
---

# Ratio Gradient Quantization

> Session 223. Michael's idea: *"What if compression of the gradient is possible?
> GD wants to place near-zero gradients to mark irreducibles, and very high
> gradients where variation is large. What if quantization needed to be a RATIO
> compression on the gradients — instead of cutting equally, a ratio that captures
> more of the ENDS of the bell curve?"*
>
> This is a **quantizer / coding scheme** (the distinguishing feature vs the other
> s223 pages: a loss `relational-loss-distillation`, a curriculum `normal-form-
> curriculum-partition`, a learning rule `holographic-burn-in-learning-rule`). The
> claim: the gradient distribution is bimodal / heavy-tailed, so its optimal code is
> a **ratio (logarithmic / companding) code**, not equal cutting — and the project
> can DERIVE the ratio from its own measured statistics.
>
> Register: **functional + topological/routing**.

## The premise is a confirmed finding — but it is TWO axes

`gradient-zero-map.md` (s171) confirms GD deposits near-zero gradients at
irreducibles: high-gradient + high sign-consistency = "still reducing"; low-gradient
+ random direction = "settled." The distribution is **not a bell** — in the encoding
zone it is **extremely bimodal** (ρ(grad,weight) = +0.77: positions are both-high =
active or both-low = noise floor; = the s222 γ finding, settled unimodal 0.046 vs
oscillator bimodal 0.688).

**Crucial refinement — two ORTHOGONAL "zeroness" axes (Jaccard 0.17, independent):**
```
magnitude        = amplitude  (how much this position contributes)
sign-consistency = coherence  (does it contribute CONSISTENTLY = the normal-form marker)
```
So "near-zero marks irreducibles" splits: near-zero MAGNITUDE can be noise OR
settled; the real **normal-form marker is the COHERENCE axis**. A scalar
ratio-compression on |grad| touches amplitude only. The right object is **2D**.

## What it is: companding (the information-theoretically correct move)

"A ratio that captures the ends instead of cutting equally" = **logarithmic /
geometric (companding, μ-law) quantization**: level spacing grows by a constant
RATIO, not a constant step. Result: fine resolution near zero (the "is this a
committed zero?" decision) AND preserved high-tail range (big moves not clipped), at
the cost of the dense middle.

Uniform ("equal cutting") is optimal only for a UNIFORM distribution. The project has
**measured** the gradient to be bimodal / heavy-tailed — the strongest case FOR
companding. (The "bell curve" framing under-sells it: bimodal/heavy-tail favors a
ratio code even more than a bell would.)

## ★ The project can DERIVE the ratio (not guess it)

Two principled handles, both already on the board:

1. **Rate-distortion under the precision inversion (s222).** Uniform / Lloyd-Max put
   levels where data is DENSE (the middle) — the OPPOSITE of the tail intuition.
   Tail-favoring is correct ONLY under an IMPORTANCE-weighted distortion, and the
   precision inversion supplies it: superposition (the high-coherence tail) needs
   **angular precision** → spend bits there; concentration (settled near-zero)
   ternarizes cleanly → cheap, but the zero-threshold needs precision. Minimize a
   precision-inversion-weighted distortion → a tail-favoring companding curve FALLS
   OUT (not ad hoc).
2. **Match the self-similar exponent (φ).** If the gradient is power-law /
   self-similar (Hilberg β≈0.5; `relational-loss-phi-compression.md` 1/φ≈0.618
   retention), a LOG transform turns power-law into uniform → uniform quant optimal
   IN LOG SPACE = geometric/ratio spacing, with the ratio set by the exponent. The φ
   hypothesis is, in effect, a prediction of the optimal ratio.

## Honest catches (one is load-bearing)

1. **★ The middle is the ACQUISITION PATH, not noise.** s221 acquisition⊥
   contractivity: learning K requires weights to move A LOT — to TRANSIT the middle
   from superposition → settled (Elhage phase transition). Coarse-quantizing the
   middle can FREEZE the model in its current basin and BLOCK acquisition. ⇒ compress
   the middle only AT CONVERGENCE (a deadband that widens as Δx→0, like the s221
   deadband fp-loss), NOT during acquisition. Compress late, not early.
2. **Error feedback is MANDATORY.** Any scheme that coarsens the small tail must
   ACCUMULATE the quantization residual (= consensus-etch accumulate-then-commit, =
   the contractivity acceptance gate) so slow-but-consistent gradients are not lost —
   they accumulate until they cross the commit threshold. Without it, ratio
   compression biases toward the high tail and starves settling directions.
3. **Lloyd-Max vs importance.** Density-optimal favors the middle; tail-favoring is
   right only under the importance weighting (catch made explicit so the curve is
   derived, not asserted).
4. **Scale / maturity dependence.** The coherence axis DEGENERATES at small scale
   (`gradient-zero-map.md`: micro model oscillated 89–95%, signal → noise; magnitude
   won). The 2-axis ratio quantizer needs a mature model; on a tiny student, expect
   only the magnitude/companding leg.

## Where it pays off — composes with distributed folding

This is the **communication-efficient version of `consensus-delta-folding.md`**:
contributors donate RATIO-COMPRESSED deltas — the tails (structural flips marking
normal forms + precise zeros marking settled) survive; the noisy middle is cheap.
The tails are exactly the part that FOLDS; the middle is exactly the part that stays
local content. (cf. DeMo top-k tail-keeping, here smooth + importance-weighted.)

## Falsifiable test

Uniform vs companding gradient/delta quantization (+ error feedback) at MATCHED
bit-budget, on (a) the tiny student and (b) a 2-contributor fold. Metrics:
convergence speed, final CE, and whether the bimodal γ structure (settled peak +
active tail) is PRESERVED. **Prediction:** ratio compression matches uniform at far
fewer bits and preserves structure better — **UNLESS** it coarsens the acquisition
middle (the one failure mode to instrument for, catch #1).

**One-line synthesis:** the gradient is heavy-tailed and bimodal, so its optimal code
is a ratio (log) code whose ratio the project can derive from the precision inversion
— but keep error feedback and protect the acquisition middle, or the elegant code
freezes learning.

## §P-COMPANDING-QUANT — pre-reg (FROZEN s306, before any run; s222 law)

> s306, Michael: "could we use our understanding of magnitudes and soft-routing to
> inform a quantization algorithm? Shave off the highest and lowest gradients,
> translate them into ternary routing, then quant the rest?" This is the **post-hoc
> WEIGHT** instance of this page's Open-Lead #2 (the 2-axis quantizer) — and the test
> of `register-theory-of-quantization.md`'s open frontier (base-weight-wide). Being
> post-hoc, it SIDESTEPS catch #1 (protect the acquisition middle — that only applies
> during training); error-feedback (catch #2) also n/a (no accumulation over steps).

**Register (λ measure, declared first).** The claim is **routing** — does the
quantized matrix preserve the edge graph so the FUNCTION survives — so the metric is
**downstream behavior** (held-text CE + the operand→capital g/h composition accuracy),
gated against a **shuffled-tail null**. NEVER ‖W−Q(W)‖ / mag_cos (that measures the
disposable register; λ yardstick).

**Two separable questions (the s171 correction folded in).**
- **Q1 — STORAGE (the register-theory primary).** Keep the outlier tail as ternary
  SIGN (1.58 b) vs high-precision fp16/int8. Is base-weight outlier *magnitude value*
  disposable-for-routing (register theory) or salient (AWQ/SpQR)?
- **Q2 — SELECTOR (answers `gradient-zero-map.md` open-Q1 at scale).** Pick the tail by
  **coherence** (gradient sign-consistency) vs **magnitude** (|w|). s171 Exp-3 proved
  **magnitude wins at MICRO scale** (6.00 vs 6.12; combined HURT) because coherence
  degenerates when undertrained (89–95% oscillators). Qwen3-4B is mature → the signal
  should exist → this is exactly s171's untested open question.

**Target.** FFN weights (gate/up/down) of Qwen3-4B, post-hoc, static, NO training.
Band = all 36 layers (advisory depth split: Zone-A L0–3 where ρ(grad,weight)≈0.8 vs
Zone-B/C L5+ where ≈0, per s171). Base model frozen; each arm quantizes → eval →
restore (the writeback/ternarize apply/restore pattern).

**Calibration (reuse, no fork).** `scripts/experiments/gradient_zero_map.py` already
emits per-weight gradient stats over diverse text → **magnitude** |w| (static, free)
and **coherence** = sign-consistency |Σ∇|/Σ|∇| (dynamic; one backward per calib batch,
accumulated). Noise-floor from a shuffled-batch control (s171: 0.057).

**Arms** (each hits a target average-bits B via its one free precision knob; we sweep
B and compare Pareto frontiers, not a single point):
- `int_uniform` — RTN int-b everything (outliers stretch the grid). FLOOR.
- `twn` — per-column ternary everything. FLOOR.
- `outlier_mag_fp16` — top-τ by |w| kept fp16, rest ternary (SpQR/AWQ "outliers are
  salient / keep magnitude"). The Q1 control.
- `companding_mag` — **PRIMARY**: top-τ by |w| → ternary sign·γ_col; body → int-b′;
  floor (bottom coherence∧amplitude) → 0. Q1 = `companding_mag` vs `outlier_mag_fp16`
  (same selection, ternary-sign vs fp16 storage).
- `companding_coh` — top-τ by **coherence** → ternary; body int-b′; floor → 0. Q2 =
  `companding_coh` vs `companding_mag` (advisory: Jaccard of the two tail sets, s171
  predicts ≈0.17).
- `companding_shuffle` — **λ yardstick**: the tail POSITIONS shuffled (matched count +
  matched per-column γ), body unchanged. MUST fail. ≥3 shuffle seeds.

**Bit-budget protocol (FROZEN).** Sweep B ∈ {2.0, 2.5, 3.0, 4.0} effective bits/weight
(effective = Σ per-tier bits incl. the tail-index overhead, reported by the arm). Each
arm's free knob (body int level b′, or the fp16-tail's low-precision level) is set to
match B ± 0.1. The comparison object is the **CE-vs-bits Pareto frontier** per arm;
verdicts read frontier DOMINANCE, not one budget.

**Gates** (downstream CE on held innocents, paired over text chunks, 10k bootstrap;
g/h composition acc; Bonferroni across the primary contrasts; null = shuffled-tail):
- **C1 SCHEME-WORKS** : min over companding arms dominates `int_uniform` on the frontier.
- **C2 MAGNITUDE-DISPOSABLE** (register-theory primary) : `companding_mag` frontier ≥
  `outlier_mag_fp16` frontier (within ε) → the ternary-sign tail matches the fp16 tail
  → outlier magnitude value disposable. If `outlier_mag_fp16` strictly dominates →
  **MAGNITUDE-SALIENT** (register clash on base weights; AWQ right here).
- **C3 SELECTOR** : sign of (`companding_coh` − `companding_mag`) frontier gap →
  COHERENCE-SELECTS vs MAGNITUDE-SELECTS at 4B (answers s171 open-Q1).
- **C4 SPECIFICITY** (yardstick) : the winning companding arm dominates
  `companding_shuffle` (else the tail choice was inert / the win was budget-only).
- **C5 HOST-SANE** : the winner's CE within a fixed rel-tolerance of fp16 at B=4.0.

**Verdicts (FROZEN).**
- **MAGNITUDE-DISPOSABLE (+COHERENCE-SELECTS / +MAGNITUDE-SELECTS)** : C1∧C2∧C4∧C5 →
  register theory reaches BASE WEIGHTS (the frontier closes); C3 sub-tags the selector.
  ★ the target result — outlier magnitude is scaffolding at the weight level too.
- **MAGNITUDE-SALIENT** : ¬C2 (`outlier_mag_fp16` dominates) → base-weight outliers need
  their magnitude; the register theory is delta-only (a real bound on the thesis).
- **SCHEME-INERT** : ¬C1 → the 3-tier code doesn't beat uniform (companding not worth it).
- **UNSPECIFIC** (¬C4) / **HOST-DAMAGED** (¬C5).

**A-priori lean (honest, s171-grounded; do NOT tune).** Magnitude is the PROVEN
selector (s171 Exp-3); coherence is untested at 4B. The register-theory bet is on Q1
(STORAGE): ~55% MAGNITUDE-DISPOSABLE (ternary sign suffices for the tail), most likely
paired with **+MAGNITUDE-SELECTS** (coherence loses/ties as a selector even at 4B); the
register-theory upside is +COHERENCE-SELECTS; the register-refuting downside is
MAGNITUDE-SALIENT (~25%). Every branch is publishable: it either extends
`register-theory-of-quantization` to base weights, bounds it to deltas, or answers
s171's open question. Not tuned to pass (B-sweep, τ, arms frozen a priori).

**Cadence.** THIS is the frozen pre-reg. Next: build the harness (reuse
`gradient_zero_map.py` calibration + writeback/ternarize apply-restore + ce/gh eval;
add the tiers + Pareto sweep) → `--validate` (planted: budget-match, tier masks,
shuffle-tail null, verdict worlds) → smoke (`--n-layers`, mechanics only, s297) →
Michael GO → run.

## Open leads (declare register first)

1. **Companding-quant harness** (register: functional): μ-law / power-α gradient
   quantizer + error feedback vs uniform at matched bits on the tiny student; sweep
   the ratio (μ/α); does the derived (precision-inversion) ratio win?
2. **2-axis quantizer** (register: topological/routing): allocate precision by
   magnitude (companding) AND coherence (keep high-sign-consistency directions
   high-precision); vs magnitude-only.
3. **Late-only middle compression** (register: functional): deadband that widens as
   Δx→0 (s221) — does compressing the middle only at convergence avoid the
   acquisition block?
4. **Ratio = φ?** (register: functional): measure the gradient power-law exponent
   per zone; is the optimal companding ratio the φ-predicted one?
5. **Distributed**: ratio-compressed delta donation in the fold (open lead of
   `consensus-delta-folding.md`) — bandwidth vs fold quality.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/ratio_gradient_quant.py` | companding gradient quantizer + error feedback vs uniform at matched bits; ratio sweep; γ-structure preservation |
| `mementum/knowledge/gradient-zero-map.md` | the confirmed premise: gradient-zero map, 2 orthogonal zeroness axes, bimodal Zone A |
| `scripts/experiments/relational_loss_distillation.py` | s223 sibling (the static relational loss) |
