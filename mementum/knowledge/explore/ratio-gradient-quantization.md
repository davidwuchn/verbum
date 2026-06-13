---
title: "Ratio Gradient Quantization — Companding the Heavy-Tailed Gradient (Spend Bits on the Ends, Derive the Ratio)"
status: open
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
