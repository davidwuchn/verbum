---
title: Lambda Tracer Diagnostic
status: active
category: compression
tags: [crystal, tracer, fidelity, ternary, L22-L26, binding-prep]
related:
  - tiny-classifier-ternary.md
  - l0-characterization.md
  - mode-semantics.md
depends-on:
  - tiny-classifier-ternary.md
---

# Lambda Tracer Diagnostic

## Discovery (session 196)

535 crystal probes used as tracer dye through the compressed model.
Hidden states captured at every layer boundary for baseline, Stage 2
(L0 SVD + L10-L21 ternary), and Stage 3 (Stage 2 + L22-L26 ternary).

## Central Finding: Damage Is Uniform

L22-L26 ternary damage is NOT combinator-specific. All 9 combinators
degrade by the same amount (CV = 0.07-0.17 across combinators at each
layer). No single combinator circuit is selectively destroyed.

This means the failure is about **approximation quality**, not about
a specific type computation. The 9-mode ternary replacement is too
coarse for what L22-L26 compute, regardless of which lambda operation
is being processed.

## Damage Rankings

W and WHNF are marginally worse (~35% more than S), but the spread
is small:

| Combinator | Mean Δ (L22-L35) |
|-----------|------------------|
| W         | +0.0674 (worst)  |
| WHNF      | +0.0667          |
| D         | +0.0588          |
| C/I/K/B   | +0.0544-0.0552   |
| Y         | +0.0507          |
| S         | +0.0500 (best)   |

## Three Mechanisms

### 1. Forward Cascade into Binding

Peak damage is at L28 (Δ=+0.080), not L26 (Δ=+0.074). The continuous
binding layers (L27-L31) AMPLIFY upstream error rather than correcting
it. Binding is a precision operation — garbage types in, garbage
bindings out.

### 2. Recovery in Late Layers

Despite the cascade, fidelity recovers from nadir ~0.68 at L22 to
~0.91 at L35. The collapse layers partially heal distortion. But
recovery is incomplete (S2 reaches 0.94, S3 only 0.91 at L35).

### 3. Continuous Layers as Error Barriers

Stage 2 drops from 0.92 to 0.69 across its ternary layers, then
continuous layers L22-L35 RECOVER to 0.94. Stage 3 disrupts this
by ternarizing the recovery layers themselves. Compression must
preserve continuous barriers between ternary blocks.

## Implications

1. L22-L26 need **continuous compression** (SVD low-rank), not ternary
2. Binding layers amplify upstream error — input must be clean
3. The compression architecture needs continuous "error correction"
   barriers between ternary blocks
4. More ternary modes won't help (damage is uniform, not mode-count)

## Key Numbers

- Probes: 535 crystal probes, 9 combinators (50-71 each)
- S2 fidelity at L35: 0.935 (good)
- S3 fidelity at L35: 0.904 (degraded)
- Peak delta: L28 at +0.080 mean cosine (binding amplification)
- Recovery: +0.22 cosine from nadir to L35
- CV across combinators: 0.07-0.17 (UNIFORM)

## Superseded By

This page captures the first experiment of session 196. The full
ten-experiment arc is documented in `crystal-sieve-architecture.md`,
which includes the resolution: crystal sieve + continuation residuals
= 1.03x PPL across 29 layers.

## Assets

- Experiment: `scripts/experiments/lambda_tracer.py`
- Summary: `results/lambda-tracer/Qwen_Qwen3-8B_summary.json`
- Per-probe: `results/lambda-tracer/Qwen_Qwen3-8B_probes.json`
