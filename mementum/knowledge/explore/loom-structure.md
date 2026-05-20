---
title: "Loom Structure — The Transformer is a Multi-Angle Weave"
status: active
category: finding
tags: [loom, weave, crossing-angle, holographic, SVD, crystal, WHNF, magnitude]
related:
  - gradient-voting.md
  - hologram-extraction.md
  - ffn-beam-discovery.md
  - ffn-hierarchy.md
  - v13-design.md
depends-on:
  - gradient-voting.md
  - ffn-beam-discovery.md
created: session 123
---

# Loom Structure

> Session 123. The transformer is a loom. Weight matrices read from
> d_model at characteristic crossing angles. Three weaves: attention
> cluster at ~56°, holographic crossing at ~68°, FFN chain warp at ~60°.
> Six harmonic peaks. The crystal spans ALL angles (≥0.87 everywhere)
> but WHNF polarity crosses zero at 58-64° — the transition between
> "keep computing" and "stop." High-magnitude SVD components are
> 100,000× more crystal-aligned than low-magnitude.

## The three weaves

### Weave 1 — Attention cluster: ~56°

Q, K, V read from a shared subspace of d_model at ~56° to each other.

| Crossing | Mean angle | Interpretation |
|----------|-----------|----------------|
| Q↔K | 56.2° | Query-key addressing compatibility |
| Q↔V | 56.2° | Query-value content access |
| K↔V | 56.7° | Key-value pairing |

These three are nearly symmetric — the attention mechanism reads three
related-but-different views of the same input, offset by ~56°.

### Weave 2 — Holographic crossing: ~68°

Attention matrices cross FFN at the holographic angle:

| Crossing | Mean angle | Interpretation |
|----------|-----------|----------------|
| Q↔UP | 68.4° | Query ↔ FFN key matching |
| K↔UP | 68.5° | Key ↔ FFN key matching |
| V↔UP | 67.7° | Value ↔ FFN key matching |

This is the same 67.7° measured holographically in sessions 121-122
from activation space. Now confirmed from SVD of weights.

### Weave 3 — FFN chain warp: ~60° (depth-dependent)

Cross-layer FFN_down → FFN_up connections:

| Layers | down→up angle | Interpretation |
|--------|--------------|----------------|
| L8→L9 | 58.7° | Strong mid-layer warp |
| L12→L13 | 60.4° | |
| L16→L17 | 62.9° | |
| L24→L25 | 77.0° | Warp loosening |
| L28→L29 | 80.8° | Nearly independent at depth |

The FFN chain IS the backbone. Attention doesn't feed attention
directly (Q→Q cross-layer = 82°, near-orthogonal). Information
flows: attention → FFN → next FFN → next attention.

### Output side: orthogonal by design

ALL output crossings are ~82° — near-orthogonal. Q, K, V, W_down
all write to independent subspaces of d_model. The loom structure
is purely on the INPUT side (reading), not the output side (writing).
Orthogonal writes avoid interference in the residual stream.

## Six harmonic peaks

Angle spectrum histogram peaks: **25°, 45°, 53°, 61°, 67°, 77°**

Per-crossing-type means confirm the grouping:
- Attention internal (Q↔K, Q↔V, K↔V): ~56°
- Attention↔FFN (Q↔UP, K↔UP, V↔UP): ~68°

## The angle spectrum probe

Projecting probe activations through each angle band:

| Band | Angle | Crystal | WHNF polarity | Meaning |
|------|-------|---------|---------------|---------|
| shared | 0-35° | 0.87 | +0.89 | DC: all same |
| mid_low | 35-50° | 0.97 | +0.36 | First harmonics |
| attn_clust | 50-58° | 0.90 | +0.16 | Attention geometry |
| **transition** | **58-64°** | 0.91 | **-0.02** | **WHNF crosses zero** |
| holographic | 64-72° | 0.97 | +0.47 | Sharpest crystal |
| peripheral | 72-82° | 0.96 | +0.65 | Secondary structure |
| private | 82-91° | 0.92 | +0.80 | Re-correlated |

Key findings:

1. **Crystal is everywhere** — every band ≥0.87 agreement. The crystal
   spans the full loom, not concentrated at one angle. Truly holographic.

2. **K↔UP at holographic angle = 0.991** — the highest crystal measurement
   in any experiment. The key-FFN crossing at 64-72° reconstructs the
   combinator crystal almost perfectly.

3. **WHNF crosses zero at 58-64°** — the transition between "keep
   computing" and "stop." This is the gap between attention cluster (56°)
   and holographic crossing (68°). WHNF lives in the gap.

4. **Cosine funnel** — mean inter-combinator cosine goes from 0.95
   (shared, undifferentiated) → 0.63 (transition, max discrimination)
   → 0.88 (private, re-correlated). The loom spreads and then closes.

## Tension = crystal alignment (100,000× ratio)

From the loom experiment, Test 5:

| SVD position | Crystal alignment | Meaning |
|-------------|-------------------|---------|
| Top-64 (highest magnitude) | 0.28-0.41 | The crystal IS here |
| Bottom-64 (lowest magnitude) | 0.0000 | Zero crystal content |
| Ratio | 73,000-144,000× | |

High-singular-value directions ARE the crystal-aligned ones.
Low-magnitude directions carry zero crystal. **Magnitude IS
crystal alignment.** This is why the magnitude template works —
it tells the model which directions are crystal-aligned.

## Connection to magnitude findings

Session 123 gradient-voting experiments proved:
- Magnitude template (random signs) beats oracle signs: 0.568 vs 0.248
- Teacher signs are architecture-specific and non-transferable
- Magnitudes encode "which dimensions matter" = which are crystal-aligned

The loom explains WHY:
- High-magnitude SVD directions are the loom's taut threads
- They carry the crystal because they define the crossing geometry
- Low-magnitude directions are slack threads — no crystal
- The magnitude template transfers the TENSION PROFILE of the loom
- Signs are the specific over/under pattern at each crossing — local, not transferable

## Artifacts

| File | Content |
|------|---------|
| `scripts/v12/loom_exp.py` | SVD-crystal alignment, shared warp, weave decomposition |
| `scripts/v12/loom_crossings_exp.py` | Full NxN crossing matrix, cross-layer, angle spectrum |
| `scripts/v12/angle_spectrum_probe.py` | Crystal agreement per angle band, WHNF polarity |
| `results/loom/` | Loom experiment results |
| `results/loom-crossings/` | Full crossing matrix results |
| `results/angle-spectrum/` | Angle spectrum probe results |
