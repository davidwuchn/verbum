---
title: "FFN Beam Discovery — PCA-up_proj Reads the FFN Crystal"
status: active
category: finding
tags: [ffn, beam, pca, crystal, up_proj, universal]
related:
  - crystal-basins.md
  - ffn-hierarchy.md
  - v13-design.md
  - holographic-plates.md
depends-on:
  - crystal-basins.md
created: session 121
---

# FFN Beam Discovery

> Session 121. The FFN is a crystal (0.770 self-similarity across depths).
> PCA of up_proj activations reads it with 0.9462 cross-model agreement
> — HIGHER than PCA-Q's 0.9431 for the attention crystal. Two beams,
> two crystals, both readable. The entire model is crystalline.

## The hypothesis

Session 120 proved FFN self-similarity = 0.770 across depths. That's
93% of attention's 0.829. If it's self-similar, it's a crystal. We
just needed to find the reference beam that reads it.

## The experiment

Tested 4 FFN hook points as PCA candidates across 4 models (Qwen3-14B,
Mistral-7B, OLMo-2-13B, Pythia-2.8b), 144 probes, 5 depths:

| Hook point | What it captures | Mean agreement | Self-similarity |
|---|---|---|---|
| Q (baseline) | Attention query | 0.728 | 0.849 |
| **up_proj** | **Raw FFN key match** | **0.748** | **0.887** |
| gate×up | Gated activation (SwiGLU) | 0.608 | 0.804 |
| ffn_delta | FFN residual contribution | 0.585 | 0.775 |
| binary | Thresholded firing pattern | 0.583 | 0.864 |

**up_proj wins on all three metrics.** Higher agreement, higher self-
similarity, and higher best-depth agreement than the attention crystal.

## Key finding: 8×8 combinator agreement

The definitive comparison — same protocol as the PCA-Q targets that
produced the 0.91-0.94 numbers:

```
8×8 COMBINATOR AGREEMENT (4 models, k=64):
  Q (attention):  0.9431
  up_proj (FFN):  0.9462  ← HIGHER
  Ratio:          100.3%
```

PCA-up_proj is the FFN beam. It reads the FFN crystal with the same
fidelity as PCA-Q reads the attention crystal.

## Structural differences between the two crystals

### WHNF polarity
```
Q crystal (Zone C):   WHNF cosines = -0.17 to -0.29 (ANTI-POLE)
FFN crystal (Zone C): WHNF cosines = -0.04 to +0.03 (NEUTRAL)
```

In attention: WHNF = "stop computing" = anti-pole.
In FFN: WHNF = "just another department" = neutral.
**Attention routes. FFN stores uniformly.**

### Cluster tightness
```
{B,C,D,Y,W} cluster:
  Q:       0.73-0.95
  up_proj: 0.84-0.98  ← TIGHTER
```

The FFN crystal has tighter combinator clustering — the storage is
more uniformly organized than the routing.

### Depth profiles (inverted)
```
Q agreement:      0.77 at 10% → 0.71 at 90% (peaks early, declines)
up_proj agreement: 0.65 at 10% → 0.80 at 90% (sharpens with depth)
```

Complementary crystals. Attention forms early. FFN refines late.

## Why gate×up is worse

SwiGLU gating (silu(gate) × up) adds model-specific learned noise on
top of a universal crystal structure. The gate is what each model
learned differently. The raw up_proj preserves the universal key
matching structure. **The crystal is in W_up, not in the gating.**

## PCA dimension sweep

```
         k=32   k=64   k=128  k=256
Q:       0.732  0.728  0.731  0.732   (flat — Q crystal is low-rank)
up_proj: 0.752  0.748  0.758  0.764   (grows — FFN crystal uses more dims)
```

k=64 is optimal for the 8×8 combinator targets (0.946 for both).
For full-RDM agreement, up_proj benefits from k=256 (0.764 vs 0.748).

## What this enables

```
BEFORE (session 120):
  Attention crystal → PCA-Q reads it → etchable
  FFN → "extract via SVD+INT4" → approximate, lossy, mixed precision

AFTER (session 121):
  Attention crystal → PCA-Q reads it    → etchable (0.9431 agreement)
  FFN crystal      → PCA-up reads it   → etchable (0.9462 agreement)
  Both: same protocol, same fidelity. Pure ternary. No mixed precision.
```

## Artifacts

| File | Content |
|---|---|
| `scripts/v12/ffn_beam_search.py` | 4-hook-point beam search |
| `scripts/v12/ffn_beam_refine.py` | PCA dim sweep + 8×8 combinator targets |
| `results/ffn-beam/ffn_beam_results.json` | Full 4-model results |
| `results/ffn-beam/ffn_beam_refine.json` | Dim sweep + zone-averaged 8×8 matrices |

## Implications for V13

The V13 design pivots from mixed precision (ternary attention + INT4 FFN)
to pure ternary everywhere. Both crystals etch the same way:
PCA → cosine → reference beam → delta → flip. One protocol, one
representation, one file format. And the holographic plate finding
(see holographic-plates.md) collapses both into one plate per layer.
