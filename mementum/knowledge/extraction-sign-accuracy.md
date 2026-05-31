---
title: "Extraction Sign Accuracy — Signs Are Perfect, Magnitude Is the Gap"
status: active
category: foundational
tags: [ternary, extraction, error-correction, magnitude, compression]
related: [ternary-plate-extraction.md, holographic-error-correction.md, crystal-universality.md]
depends-on: [ternary-plate-extraction.md]
---

# Extraction Sign Accuracy

> **The central finding of session 173:** Ternary extraction captures
> signs with 100% accuracy. There are no sign errors to correct. The
> gap between extraction quality and the original is entirely due to
> magnitude information loss.

## The Falsified Hypothesis

**Hypothesis:** The KIBC crystal geometry (6D subspace, 170× redundancy)
provides an error-correcting code that can detect and fix sign errors
in extracted ternary plates.

**Result:** Falsified. Crystal error correction makes things *worse* at
every confidence threshold. Diagnostic revealed:

1. Ternary at non-zero positions = sign(W_float) **exactly, 100% of the time**
2. The "sign_corr = 0.792" metric measures cos(sign(W)@x, W@x) — a *functional*
   similarity metric, not a sign accuracy metric
3. The gap (1 - 0.792 = 20.8%) comes from replacing per-weight magnitudes
   with a single per-row gamma scalar

## Why Crystal Correction Cannot Work

The combinator fingerprints define an 11D subspace in R^5120. Each weight
row projects only **0.3%** of its energy into this subspace. The crystal
captures what a neuron *does* (which combinator it implements) but not
*how it's wired* (which of its 5120 individual weights should be +1 vs -1).

When the crystal projection disagrees with the ternary sign at a position,
the crystal is wrong 100% of the time — because the ternary already IS
sign(W_float), and the crystal projection is essentially random noise
relative to individual weight values.

The 170× redundancy argument was about **crystal identification**
(recognizing which combinator a direction belongs to from sparse measurements),
not about **sign prediction** (predicting individual weight values from
a 11D projection of 5120D vectors).

## What the Metrics Actually Measure

| Metric | Formula | What it measures | 27B value |
|--------|---------|------------------|-----------|
| sign_corr | cos(sign(W)@x, W@x) | Functional similarity (sign-only vs full) | 0.792 |
| recon_cos | cos((ternary×γ)@x, W@x) | Reconstruction quality with gamma | 0.882 |
| sign_accuracy | #(ternary == sign(W)) / #nonzero | Element-wise sign correctness | **1.000** |

The sign_corr gap (0.792) is NOT from wrong signs. It's from:
- **Per-row gamma collapsing magnitude variance** (CV = 0.51 within rows)
- **Zeroed positions** (30% of positions zeroed, containing 1.5% of energy)

## What Actually Helps

Tested on Qwen3.6-27B layer 10 gate_proj [17408, 5120]:

| Strategy | recon_cos | Δ vs baseline | Extra storage | Compression |
|----------|-----------|---------------|---------------|-------------|
| Baseline (ternary + row-gamma) | 0.884 | — | — | 8.0× |
| + column scales | 0.884 | +0.0002 | 10 KB/matrix | 8.0× |
| + sparse top-1% outliers | 0.900 | +0.016 | 2.5 MB/matrix | 6.8× |
| + sparse top-5% outliers | 0.925 | +0.041 | 12 MB/matrix | — |
| 4-bit (sign + 2-bit magnitude) | 0.975 | +0.091 | — | 4.0× |

**The 4-bit encoding reaches 0.975 recon_cos** — near-lossless — by keeping
signs exact (ternary) and adding 2 bits of magnitude quantization per position
with 4 per-row centroids. This is Q4-equivalent quality at 4× compression
(vs bf16), but with the crucial difference that signs are *exact*, not
approximated.

## Implications for the Project

1. **Crystal error correction is a dead end for sign topology.** The signs
   are already perfect. Don't try to "fix" them.

2. **The holographic error correction page's TD approach** is about a
   different thing: it's about training a *student* model's signs to match
   a *teacher* — not about fixing extraction errors in the teacher's own
   plates. In extraction from float → ternary, there are no sign errors.

3. **The extraction quality gap is a compression problem**, not a topology
   problem. The path forward is:
   - Better magnitude encoding (2-bit per position)
   - Or: sparse outlier preservation (top-1% → top-5%)
   - Or: accept the 0.884 recon_cos and let attention adapt (the "attention
     emerges" hypothesis — extract FFN plates, let attention retrain)

4. **The crystal IS useful** — just not for sign correction:
   - Crystal geometry identifies functional roles (which combinator each neuron implements)
   - Crystal fingerprints enable opcode map comparison (verification that the
     extracted plate preserves the program)
   - Crystal structure guides *training* (etch, TD) on new/adapted models

5. **The 0.792 "sign_corr" metric should be renamed** in our context. It's
   "sign functional similarity" — the cosine between the sign-only transform
   and the full transform. It does NOT indicate sign errors.

## Compression Hierarchy (updated understanding)

```
Float32:    32 bits/param    100%  quality    1.0× compression
BFloat16:   16 bits/param    ~99%  quality    2.0× compression
Q8:          8 bits/param    ~98%  quality    4.0× compression
Q4:          4 bits/param    ~95%  quality    8.0× compression
────────────────────────────────────────────────────────────────
Ternary+2bit: 4 bits/param  97.5% quality    4.0× compression  ← EXACT SIGNS
Ternary+γ:    2 bits/param  88.4% quality    8.0× compression  ← EXACT SIGNS
Pure ternary: 2 bits/param  79.2% quality    8.0× compression  ← EXACT SIGNS (no γ)
```

The key difference: standard quantization (Q4, Q8) approximates BOTH signs
and magnitudes. Our ternary extraction gets signs *exactly right* and only
loses magnitude resolution. This means:
- No error accumulation in sign topology across layers
- Attention can learn exact corrections for magnitude (γ is learnable)
- The plate IS the program — topology is preserved perfectly

## What Changed in Understanding

**Before (session 172):** "The 23% sign error (1 - 0.77) is recoverable via
crystal error correction. ~170× redundancy means enormous correction capacity."

**After (session 173):** There is no sign error. The 23% gap is magnitude
loss. The 170× redundancy helps identify which combinator a neuron implements,
not what its individual weight signs should be. The extraction already captures
the exact program topology. What's lost is calibration (magnitude), not structure (sign).

This is actually *better* than we thought. The plate extraction is *lossless
for the program*. What's lossy is the amplitude — and amplitude is recoverable
via γ (already done), 2-bit magnitude (cheap), or retraining (attention adapts).
