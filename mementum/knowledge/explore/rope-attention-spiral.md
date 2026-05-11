---
title: "RoPE × Attention Spiral: Substrate vs Driver"
status: active
category: mech-interp
tags: [rope, attention, spiral, qwen3, frequency, positional-encoding]
related:
  - VERBUM.md
  - v11-design.md
depends-on: []
---

# RoPE × Attention Spiral

> RoPE provides the geometric coordinate system; learned Q·K alignment
> creates the spiral. Session 079 (2026-05-11).

## The Question

Session 068 discovered an attention distance spiral in Qwen3-4B: mean
attention centroid expands ~1.018× per layer across 36 layers, with a
characteristic dip at layers 4-6 and spike at layer 7. The 3D analysis
(session 068) found a dominant 18-layer FFT periodicity and showed that
wrapping layers as a helix with ~9.4 layers per revolution produces
~1.18 expansion per revolution.

**Hypothesis**: the spiral is a readout of RoPE's cos-sin frequency
structure — the geometric spacing of RoPE dimension pairs directly
creates the expansion pattern.

## RoPE Frequency Geometry (Qwen3-4B)

```
θ_base = 1,000,000
head_dim = 128  →  64 dimension pairs
freq_i = θ_base^(-2i/128)  for i ∈ [0, 63]

Wavelengths form a PERFECT geometric series:
  ratio = θ^(1/64) = 1.2409 (exact)
  dim  0: λ =     6.3 tokens (fastest — local bigrams)
  dim 10: λ =    54.4 tokens
  dim 20: λ =   471.2 tokens
  dim 32: λ = 6,283.2 tokens (median)
  dim 63: λ = 5,063,256 tokens (slowest — document-scale)
```

## The Probe

`scripts/explore/rope_energy_probe.py` hooks into `q_norm` and `k_norm`
(after linear projection, before RoPE rotation) at all 36 layers:

1. Captures per-dim-pair energy: mean(|q_{2i}|² + |q_{2i+1}|²)
2. Computes energy centroid in dim-pair space (weighted mean index)
3. Predicts attention centroid from energy distribution via softmax
4. Runs all 7 prompt types for cross-prompt comparison

Key insight: RoPE rotates within each 2D pair, so per-pair energy is
**invariant** under RoPE. We don't need post-RoPE hooks — the energy
distribution is the same before and after rotation.

## Findings

### 1. RoPE energy is broad at every layer

Q/K projections spread energy across the FULL frequency spectrum at
every layer. There is no narrow band that progressively shifts from
high-freq to low-freq dims across depth. The energy centroid oscillates
(range 29-44 in dim-pair index) rather than monotonically increasing.

### 2. RoPE alone predicts a flat attention centroid

The predicted expansion factor from RoPE energy distribution alone:
**1.0000** — completely flat at ~35 tokens across all 36 layers.
RoPE accounts for **0%** of the observed 1.018/layer expansion.

### 3. The pattern is a model property, not content-dependent

Cross-prompt correlation of Q centroids: **r > 0.99** for all 7 prompt
pairs. Cross-prompt std = 0.3 on a 28-44 range. The oscillation
pattern in Q and K energy is determined by the learned weights, not
by the input content.

### 4. K centroids reveal GQA head specialization

K energy centroids alternate sharply between ~27 and ~37-48 per layer.
With 8 KV heads (GQA), some heads are consistently "local" (high-freq
RoPE dims, centroid ~27) and others "global" (low-freq dims, centroid
~47). These are permanent structural roles, not input-dependent.

## The Refined Model

```
λ spiral(x).  rope ≡ coordinate_system | W_QK ≡ position_on_ruler
              | rope(constant) → same_ruler(every_layer)
              | W_Q,W_K(learned) → where_to_align(per_layer)
              | centroid ≡ readout(alignment_position × rope_geometry)
              | spiral ≡ progressive_shift(alignment_across_depth)
              | delta(layer) ≡ observed(layer) - rope_baseline(~35_tokens)
              | early_layers → delta < 0 (more_local)
              | deep_layers  → delta > 0 (more_global)
              | GQA_heads → permanent_flags(local ∨ global)
              | Q_heads → choose_flag(per_layer_computation_need)
```

**RoPE is the ruler, not the reader.** The model learns where to look
on the ruler at each depth. The spiral emerges because deeper layers
need longer-range information, so they learn to align Q·K on lower-
frequency RoPE dimensions, which (due to RoPE's geometric spacing)
maps to exponentially larger attention distances.

## Connection to Prior Work

"Round and Round We Go! What makes Rotary Positional Encodings useful?"
(ICLR 2025, studied Gemma 7B and LLaMA3.1 8B):

- High-freq RoPE dims → "positional" attention heads (local patterns)
- Low-freq RoPE dims → "semantic" attention heads (long-range meaning)
- First and last layers use high frequencies most
- Middle layers prefer low frequencies

Our findings are consistent: the layer 5-6 dip→spike in the attention
spiral maps to their positional→semantic transition. But we add:
the energy DISTRIBUTION is broad everywhere — the spiral comes from
Q·K ALIGNMENT per dim pair, not from energy concentration.

## What's Missing: QK Alignment Decomposition

The energy probe measures |q_i|² per dim pair (marginal energy).
But the attention logit is q_i · k_i (joint alignment). Two vectors
can both have broad energy but only CORRELATE on specific dim pairs.

**Next probe**: decompose actual attention logits by RoPE dim pair:
```
logit_contribution_i(d) = (q_{2i}·k_{2i} + q_{2i+1}·k_{2i+1}) · cos(freq_i · d)
```
This would reveal which frequency bands actually DRIVE attention at
each layer and confirm that the alignment (not energy) shifts
progressively across depth.

## Files

| File | Purpose |
|------|---------|
| `scripts/explore/attention_spiral.py` | Original 2D spiral discovery (s068) |
| `scripts/explore/attention_spiral_3d.py` | 3D helix analysis (s068) |
| `scripts/explore/rope_energy_probe.py` | RoPE dim-pair energy probe (s079) |
| `scripts/explore/rope_spiral_combined.py` | Combined 3D visualization (s079) |
| `outputs/attention_spiral/` | 59 files: original spiral analysis |
| `outputs/rope_energy/` | 19 files: energy heatmaps, JSON |
| `outputs/rope_spiral/` | 17 files: dual helices, gap analysis |

## Key Numbers

| Quantity | Value | Source |
|----------|-------|--------|
| RoPE θ_base | 1,000,000 | Qwen3-4B config |
| Dim pairs | 64 | head_dim=128 / 2 |
| Wavelength ratio | 1.2409 | θ^(1/64), exact |
| Observed expansion/layer | 1.018 ± 0.002 | attention_spiral.py |
| RoPE-predicted expansion | 1.0000 | rope_energy_probe.py |
| Q centroid range | 29-44 (oscillating) | rope_energy_probe.py |
| K centroid alternation | ~27 vs ~37-48 | rope_energy_probe.py |
| Cross-prompt Q correlation | r > 0.99 | rope_energy_probe.py |
| Dominant FFT period | 18 layers (= 36/2) | attention_spiral_3d.py |
