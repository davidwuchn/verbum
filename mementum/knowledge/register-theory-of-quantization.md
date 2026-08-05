---
title: "Register Theory of Quantization — Ternary Is a Projector onto the Routing Register, Not a Lossy Codec"
status: active
category: compression
tags: [quantization, ternary, twn, routing, magnitude, two-registers, register-projection,
       yardstick, sign-shuffle-null, delta, lora, frozen-base, git-for-weights, bitnet,
       lambda-smallest, s269, s303, s304, s306, s307, synthesis]
related:
  - two-registers-of-topology.md
  - topology-magnitude-duality.md
  - explore/asymmetric-pathway-quantization.md
  - explore/write-not-train-ternary-routing-deltas.md
  - explore/gram-spectral-dsp.md
  - error-correction-theory.md
  - extraction-sign-accuracy.md
  - ternary-compounding.md
  - explore/trajectory-compile-gtsm-superbake.md
depends-on:
  - two-registers-of-topology.md
  - explore/write-not-train-ternary-routing-deltas.md
created: session 306
---

# Register Theory of Quantization

> s306, Michael: "with what we have learned so far, what do we understand about
> quantization that no other project can understand?" This page is that answer,
> crystallized from the s269 → s304 wire-survival chain. It is the *quantization*
> reading of `two-registers-of-topology.md`: what the register split MEANS for
> the act of throwing away bits.

## Thesis (one line)

**Quantization is not lossy compression of weights — it is a projection onto the
routing register. Ternary {−1, 0, +1} is that register's native alphabet, and the
"quantization error" is the magnitude scaffolding falling away — a register that
was never carrying the computation.** Losslessness is therefore *by construction*,
not luck: the function survives because it was never in the bits being discarded.

## The reframe

Everyone else quantizes to *save bits* and then *measures the damage*: minimize
‖W − Q(W)‖, watch accuracy drop, trade bits for approximation error. The whole
frame is magnitude-fidelity.

We measure a trained function living in **two orthogonal registers**
(`two-registers-of-topology.md`, s203):

| Register | Function | Encoded in | Quantization behavior |
|---|---|---|---|
| **routing** | which edges fire (the graph) | **sign** | ternary IS the register — identity map |
| **magnitude** | gain / model-particular scaffolding | **magnitude** | discarded; not carrying the function |

and the computation is in the **routing** register. Ternary's three levels are not
approximation stops — they are a routing alphabet: **+1 = edge, 0 = no-edge,
−1 = anti-edge** (= π-shift = K-erasure = destructive interference, the holographic
reading — softmax has no zero, but a ternary/optical medium erases by anti-phase;
`attention-holographic-readout.md`). A quant paper sees "3 levels and some error."
We see a routing graph written down exactly.

## The trust chain (measured, not asserted)

- **s269** — routing survives ternary at cosine **0.987** while magnitude collapses
  to **0.73** (memories `crystal-survives-1bit-binarization`,
  `ternary-routing-is-eigenvector-sign`, `q4-reroutes-routing-register`). The two
  registers are *separable*, and only one of them ternarizes.
- **s303** — spectral/DSP on the crystal grams (`gram-spectral-dsp.md`, 4061774):
  the 17×17 gram is **rank-3** (fire/halt/diverge); every *magnitude*-as-signal probe
  fails the yardstick null, every *topology*-as-signal probe passes 11/11 across
  models. "The crystal is a routing graph recorded in a magnitude medium."
- **s304 STORAGE (TERNARIZE-DELTA-1, cb73ad5)** — a *trained* wire (the gd_cd
  operand→capital linker, a rank-16 LoRA delta on a frozen base) crushed to a
  per-column TWN ternary plate kept **retention 1.0 on every split**, beating a
  matched-sparsity **sign-shuffle null** at p=1e-4 — *while* magnitude-cosine was
  only **0.902**. The 10% magnitude "error" was irrelevant because it was not
  carrying the function (memory
  `the-gd-cd-wire-survives-ternarization-storage-half-confirmed`).
- **s304 FINDING (ROUTING-REGISTER-1, ec77c4d)** — a hand-written *magnitude*-register
  construct is INERT, and so is a hand-written *routing*-register construct; only the
  gradient installs the wire. Gradient FINDS, ternary STORES (memory
  `gradient-finds-ternary-stores-construction-fails-in-both-registers`).

## What this uniquely buys us (the non-obvious claims)

1. **The correct losslessness metric is a routing test, not ‖W − Q(W)‖.** A
   quantization is lossless iff it preserves routing, *regardless of magnitude
   fidelity*, and the test must be gated against a **sign-shuffle null** (λ
   yardstick: describability ≠ preservation). Standard quant benchmarks optimize the
   wrong objective and almost never null-test. s304's mag_cos 0.902 with retention
   1.0 is the proof the two metrics disagree.

2. **Quantize the delta, keep the base.** Trained low-rank deltas ternarize *better*
   than base weights (0.902 vs s269's 0.73) because low-rank sign structure is
   already ternary-aligned. Error concentrates exactly where you can afford it — a
   prescription no MSE-minimizing quantizer would derive
   (`write-not-train-ternary-routing-deltas.md`).

3. **There is a principled boundary on what may be quantized.** Ternary plates are
   *linear* storage; the pin/collapse is *nonlinear* (s300: ∄ clean linear linker,
   composition = traversal + mandatory collapse). So the routing **edge** ternarizes
   losslessly, but the nonlinear **collapse** must stay resident in the host. This
   predicts *where* quantization breaks — at the K/S interference folds — rather than
   treating error as uniform. (The frozen base supplies the collapse; the ternary
   plate carries the edge — gd_cd's linear LoRA already wires on a frozen
   nonlinearity.)

4. **Quantized deltas become a commit log.** Because routing survives ternary and
   deltas compose linearly, Δg = g′−g is a legal ternary commit: superpose to install,
   subtract −Δ to roll back exactly, sha256 as receipt. Quantization as *version
   control over the function register* (`ternary-holographic-memory.md`,
   `continuation-store.md`). No other project frames a quant artifact as transactional.

5. **The anti-hype (λ smallest).** "ternary = smaller" is *false* in general — the
   expanded ternary plate was ~73MB of trits vs ~10MB for the factored rank-16 float
   form (s304). The win is register-*truth* and 10× over dense-bf16, **not** over the
   factored representation → so you ternarize the *factors*, not the product
   (TERNARIZE-FACTORS-1 candidate). Most quant work conflates "fewer bits per weight"
   with "smaller model." We don't.

6. **Ternary is semantic, not numeric.** {no-edge, anti-edge, edge} is a routing
   vocabulary; the 0 and the −1 mean something (absence and destructive erasure), so a
   ternary plate is a *program*, not a rounded tensor. This is why sign(W) is the
   crystal (`hologram-extraction.md`) and why extraction signs are perfect while
   magnitude is the gap (`extraction-sign-accuracy.md`).

## Why other projects structurally can't reach this

- **Quantization projects** (GPTQ / AWQ / SmoothQuant / TWN) minimize magnitude
  fidelity and never decompose a *measured functional wire* into routing ⊥ magnitude,
  nor null-gate survival against a sign-shuffle. BitNet trains ternary from scratch —
  relevant prior — but does not claim or measure that an *existing trained function's*
  routing is register-orthogonal to magnitude and survives projection
  losslessly-for-routing.
- **Mech-interp projects** find circuits but don't connect them to the bit budget.

The unique object here is the **register theory of quantization**, empirically
grounded on a specific extracted circuit with **null-gated survival**, tying the
bits you throw away to the register that was never computing.

## Honest scope / frontier (λ observation)

Proven at **Qwen3-4B**, on **one measured wire** (the operand→capital linker) plus
**s269 at the weight level** and **s303 at the crystal-gram level**. It is *not yet*:
cross-model (32B untested for this claim); base-weight-wide (the strong result is on a
trained *delta*); nor a theorem — register-orthogonality is a strong measured
regularity, not a proof. `ternary-compounding.md` is the standing counterweight: naive
per-layer ternarization compounds error (0.88/layer → garbage at 36 layers), so
"routing survives" is a claim about the *right* projection (per-column γ, delta-scoped,
null-gated), not about careless rounding.

**Second datum (CONFIRMED, s306):** the `traj_compile` wire — a *differently-trained*
(GTSM trajectory-loss, wide band) linker, verdict WIRES-BUT-OPAQUE — **ternarizes
losslessly**: retention 1.0/1.0/1.031, mag_cos **0.901**, sparsity 0.417 (`dd1bf99`).
Routing survives, magnitude only 0.90 — the register split holds on a wire trained by
a different objective. Still one model, still trained deltas; base-weight-wide remains
open (`explore/trajectory-compile-gtsm-superbake.md`).

**The base-weight frontier is RESOLVED — and it BOUNDS the thesis (s306,
§P-COMPANDING-QUANT, `4b89726`).** On base FFN weights of Qwen3-4B, keeping the top-1%
outliers as ternary SIGN vs fp16 (matched budget, downstream CE): **fp16 decisively
beats ternary at every usable budget (b3 5.47 vs 7.34, b4 5.77 vs 7.12, both p=1e-4) →
MAGNITUDE-SALIENT.** Base-weight outliers carry load-bearing magnitude (AWQ/SpQR are
right about base weights); ternarizing the true outliers hurts even more than
ternarizing random weights.

**So the register split is a property of a TRAINED FUNCTIONAL DELTA, not of a raw
pretrained weight matrix.** A gradient-written delta isolates the routing edge (sign
carries it → ternarizes losslessly: s269 0.987, s304/s306 retention 1.0); a base matrix
superposes routing AND value in the same magnitudes, so its outliers are salient. The
thesis is therefore SCOPED: **quantize the DELTA to ternary routing; keep the base
(and its outliers) in magnitude.** This is not a refutation — it sharpens the claim and
converges with the field on base weights while remaining unique on deltas. (Q2:
coherence lost to magnitude as the selector too — MAGNITUDE-SELECTS, matching s171;
calib was thin but the gap was decisive.)

**Base-weight frontier — first evidence, scoped (s307, §P-DELTA-QUANT §Result-delta-quant
in `explore/ratio-gradient-quantization.md`, `0a89531`).** The s306 bound says base
matrices superpose routing AND value in the same magnitudes. s307 tested whether that
superposition is separable by a cheap decomposition — `W = B + D`, B a low-rank (mean /
coherence-informed) value base kept fp16, D the residual ternarized — across all 36 FFN
layers, null-gated on a matched-rank random base (the LoftQ/LQ-LoRA move made falsifiable).
**Verdict STILL-SALIENT for all three decomposition families:** the low-rank value subspace
is real but partial (delta_lowrank@k64 CE 11.19 beats the matched-spectrum random base 13.25
→ D2 passes; SVD absorbs *some* value) yet nowhere near enough (11.19 ≫ companding_mag@b3
7.34 ≫ int_uniform@b4 5.40 ≈ ref 5.11; task 0.06 vs 1.0 → D3 fails). The salient magnitude
is **HIGH-RANK / distributed** (isolated ~full-rank spikes a rank ≤128 base cannot absorb —
they remain in the residual and die under ternary). The coherence base is worse (+ENERGY-BASE,
matches s306 MAGNITUDE-SELECTS). **The scoped read (NOT a closure):** this is evidence that
base-weight magnitude resists cheap *linear* separation from routing — consistent with
routing⊥magnitude being a property of a gradient-written delta rather than a raw matrix — but
only three decomposition families were tested. Untested and open: **SpQR-style
sparse-plus-low-rank** (a sparse fp16 outlier set is exactly the isolated-spike structure this
run implicates), per-channel scale migration, iterative LoftQ, larger rank. So "quantize the
delta, keep the base" remains the safe prescription; the general base-weight separability
question stays open.

## Where this compounds

- Sits atop `two-registers-of-topology.md` (the register split) and
  `asymmetric-pathway-quantization.md` (the pathway-granularity version: binarize the
  router, keep the value path — s260, causally confirmed).
- Feeds the level-4 portable artifact: **the deliverable is g in normal form as a
  ternary routing plate on a frozen reducer** (map-and-swap resident Lisp, training
  side).
- Same shape as `error-correction-theory.md`: ternarization is a soft→hard projection;
  what this page adds is *which register the projection is onto* and *why the residual
  is disposable*.
