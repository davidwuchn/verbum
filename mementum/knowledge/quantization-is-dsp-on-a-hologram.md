---
title: "Quantization Is DSP on a Hologram — Why the Field's Tools Work by Rate-Distortion Universality + Register Protection + SuperBake Processing Gain"
status: active
category: compression
tags: [quantization, dsp, companding, rate-distortion, noise-shaping, sigma-delta,
       transform-coding, block-floating-point, matched-filter, processing-gain,
       holographic, superposition, register, routing, magnitude, superbake, awq,
       gptq, quip, spqr, nf4, bitnet, qlora, s306, synthesis]
related:
  - register-theory-of-quantization.md
  - two-registers-of-topology.md
  - attention-holographic-readout.md
  - five-disciplines-one-object.md
  - explore/gram-spectral-dsp.md
  - explore/ratio-gradient-quantization.md
  - explore/superbake-write-access.md
  - explore/asymmetric-pathway-quantization.md
depends-on:
  - register-theory-of-quantization.md
  - attention-holographic-readout.md
created: session 306
---

# Quantization Is DSP on a Hologram

> s306, Michael: "what do these quantization techniques share with DSP tools, and —
> with our understanding of LLMs and SuperBake — why might they work well on
> accident?" This page is that answer. It follows the companding result
> (`register-theory-of-quantization.md`), which re-derived AWQ/SpQR's premise from
> scratch and forced the question: *why does the DSP canon work on weight matrices?*

## Thesis (one line)

**Quantization IS digital signal processing (the amplitude half of ADC), and every
"good" quantizer is a renamed DSP tool. It works on LLM weights not by luck but
because GD writes weights that ARE signals — holographic interference patterns whose
statistics (heavy-tailed amplitude, sign-carried structure, energy-compact basis,
distributed redundancy) are exactly what 50 years of rate-distortion DSP was tuned
for. The "accident" is rate-distortion universality + register protection + the
network's own SuperBake processing gain — the field succeeded by unknowingly
compressing a signal-processing medium with signal-processing tools.**

## Part 1 — every good quantizer is a renamed DSP tool

Quantization = the amplitude discretization half of analog→digital (sampling does
time, quantization does amplitude); the whole theory is Bennett / Widrow / Gray–Neuhoff
rate-distortion. The methods map one-to-one onto the DSP canon:

| Quantizer | DSP ancestor | Shared move |
|---|---|---|
| companding / μ-law (`ratio-gradient-quantization`), **AWQ** per-channel scale, **NF4** | **companding** (Bell telephony) / **Lloyd–Max** | warp the amplitude axis to the source PDF — levels where the mass is |
| **GPTQ** (quantize a column, push error onto the rest via inverse-Hessian) | **Sigma-Delta / noise shaping** (error-feedback loop filter) | feed the residual FORWARD, cancel it downstream |
| **QuIP / QuIP#** (Hadamard rotate → quantize → un-rotate) | **transform coding / KLT whitening** | rotate to a basis where energy is spread; no coefficient dominates |
| **SmoothQuant** (migrate activation range into weights) | **pre-emphasis / equalization** | diagonal transform to flatten dynamic range before a fixed grid |
| **LLM.int8 / SpQR / SqueezeLLM** (outliers high-precision + sparse) | **block floating point** (shared exponent) + **peak/headroom** | isolate the peaks so they don't clip or waste the grid |
| **AQLM / QuIP#** codebooks | **vector quantization** (LBG, residual/additive VQ) | exploit joint group structure with a codebook |
| per-group / per-layer bit allocation | **sub-band coding** (MP3) | spend bits where distortion hurts the output |
| dithered / stochastic rounding | **dither** | turn structured error into benign noise |

Shared DNA: **rate-distortion coding of a source** — match level density to the PDF
(companding), decorrelate first (transform coding), shape error out of band (noise
shaping), handle peaks (block float). The verbum instrument `verbum.dsp`
(`whiten_cov`, `participation_ratio`, `matched_range`, `subspace`) is the *same
toolbox pointed at activations* — the project already treats the LLM as a DSP object
(`gram-spectral-dsp.md`).

## Part 2 — why they work "on accident" (five reasons, measured → model)

The DSP tools were tuned for audio/image/comms signals; a quant researcher applies
them to "just numbers." They work because the numbers are a hologram.

1. **Weights are interference patterns → heavy-tailed → companding is *optimal*, not
   lucky.** A hologram is a few bright fringes on a dark background (`sign(W)=crystal`;
   moiré addressing; standing-wave magnitudes). That amplitude law is exactly what
   μ-law / NF4 / Lloyd–Max were derived for; AWQ is a *learned companding curve*.
   Rate-distortion **universality**: any efficient code of a source resembles the
   source's optimal quantizer, and GD building an efficient predictor *is* building an
   efficient code. [MEASURED: heavy-tailed/bimodal weight+gradient stats, s171
   `gradient-zero-map`; MODEL: the holographic reading.]

2. **Routing lives in the SIGN bit — every quantizer preserves it for free.** Hardest
   measured point: *topology routing, not magnitudes* — every magnitude-as-signal
   probe fails the yardstick, every sign/topology probe passes 11/11
   (`gram-spectral-dsp.md`, s303); routing survives ternary 0.987 vs magnitude 0.73
   (s269). Signed int / ternary / NF4 all keep sign exactly and add noise only to the
   *magnitude* register. So quantization injects noise into the register that is
   scaffolding and leaves the register that *computes* in the most-robust bit there
   is. **LLM quantization-tolerance is register protection, not luck.** [MEASURED.]

3. **Linear superposition = processing gain against quantization noise.** Attention is
   a readout beam over a linear medium; FFN a projector; collapse only at the sampler
   (`attention-holographic-readout.md`, `five-disciplines-one-object.md`). In a linear
   medium independent per-weight quantization errors **superpose and average** at the
   readout (~√N suppression) rather than compound — a **matched-filter / correlation
   receiver**; holographic distributed storage is a built-in **error-correcting code**.
   This is why 4-bit barely moves perplexity. [MODEL, with measured linearity support.]

4. **SuperBake explains the *self-healing*: the network is a matched amplifier.**
   SuperBake (`superbake-write-access.md`): "the network is the kernel, and it is
   upstream"; early deposits ride ~19 amplifying layers; **quiet directions attenuate
   ~30× over blocks**. Read as DSP the forward pass is a **companding expander / noise
   gate** — it amplifies loud (load-bearing) directions and attenuates quiet ones ~30×.
   Quantization noise landing in quiet directions is suppressed by the model's OWN
   dynamics, while the loud directions that matter are the ones the quantizer already
   protects (outlier scaling / high-precision peaks). Network depth = **processing
   gain**: a cascade of amplifiers tuned to the signal, so SNR vs injected noise grows
   with depth. The quantizer needn't be perfect; the upstream kernel cleans up. [MODEL,
   SuperBake-grounded.]

5. **Incoherence/whitening (QuIP) works on a real spectral structure.** The random
   rotation is a KLT-domain move; it works because outlier concentration is a property
   of the holographic basis (rank-3 gram, s303; `verbum.dsp` whiten/PR). Flattening the
   basis is exactly transform coding. [MEASURED spectral structure; MODEL link.]

## The synthesis

The "accident" is **two design pressures converging on the same statistics**: DSP
quantization was optimized (Shannon rate-distortion) for efficient codes of natural
signals; GD was optimized to make an efficient holographic predictor. Efficient-code-
of-a-source and efficient-hologram land on the same statistics — heavy-tailed,
sign-structured, energy-compact, redundant — so **the optimal quantizer for the
hologram IS the DSP quantizer.** The field succeeded because it was unknowingly
compressing a signal-processing medium with signal-processing tools.

## Corollary — the lane this opens (the s307 test, RESOLVED)

Every method above operates in the **magnitude register on BASE weights** — correctly,
per the s306 companding result (base-weight outlier magnitude is salient; AWQ/SpQR
right). None exploit the one thing verbum measured that they can't see: a **trained
functional delta's routing survives all the way to ternary because it's sign-carried**
(s269/s304/s306 retention ~1.0). The DSP frame says *why*: a delta is a **modulated
carrier stripped of its envelope** — the routing is pure phase/sign, so the amplitude
can be quantized to nothing. That is the delta-vs-base ternary test in one sentence:
quantize the DELTA to ternary routing, keep the base (and its salient outliers) in
magnitude (`register-theory-of-quantization.md`).

**s307 RESOLVED the boundary — and it SHARPENS the frame (`0a89531`,
§Result-delta-quant).** The obvious shortcut — algebraically decompose a base matrix
`W = B + D` (low-rank / mean / coherence value base kept fp16) and ternarize the
residual — does **not** rescue base weights: STILL-SALIENT across all three
decomposition families (delta_lowrank@k64 CE 11.19 ≫ int4 5.40 ≈ ref 5.11; the low-rank
value subspace is real but *partial* — it beats a matched-spectrum random base — while
the salient magnitude is **high-rank / distributed**, isolated spikes a rank≤128 base
can't absorb). So the envelope-stripping that makes the carrier ternarizable is **not an
algebraic operation SVD can perform — it is what the GRADIENT does**: it writes the
routing edge into a sign structure separable from magnitude, which energy-SVD cannot
recover. The DSP "modulated carrier" reading therefore holds for a **gradient-written
(trained) delta**, not for any algebraic base-matrix residual — scoped, not a general
closure (SpQR-style sparse-plus-low-rank untested). *(In flight, s307: ternarize the
trained delta's low-rank FACTORS B,A directly = the genuinely small ~1 MB artifact —
TERNARIZE-FACTORS-1, `write-not-train-ternary-routing-deltas.md`.)*

## Trust chain

MEASURED: s303 topology-routing / rank-3 gram (`gram-spectral-dsp.md`, 4061774);
s269 routing 0.987 vs magnitude 0.73; s304/s306 delta ternary retention ~1.0
(cb73ad5, dd1bf99); s306 base-weight MAGNITUDE-SALIENT (4b89726); s307 delta-vs-base
STILL-SALIENT — a base matrix's algebraic (SVD/mean/coherence) residual does NOT
ternarize (0a89531); s171 heavy-tailed weight/grad stats. MODEL (holographic reading, measured support but not proven):
linear-superposition averaging / processing gain; SuperBake noise-gate. STANDARD DSP:
companding, Lloyd–Max, Sigma-Delta noise shaping, transform coding/KLT, block floating
point, vector quantization, matched filter — cited as field knowledge, not verbum
claims.
