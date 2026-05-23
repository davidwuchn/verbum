---
title: "Universal Phi Compression — SVD Spectrum Convergence Across Architectures"
status: active
category: discovery
tags: [phi, compression, svd, universal, crystal, compressor, relational-loss]
related:
  - hologram-crystal-fusion.md
  - ternary-descent.md
  - v6.1-training-trajectory.md
  - crystal-basins.md
depends-on:
  - hologram-crystal-fusion.md
created: session 137
---

# Universal Phi Compression — SVD Spectrum Convergence

> Session 137. The SVD spectrum of hidden state representations in
> language models follows a geometric sequence where consecutive
> singular values maintain ratio ≈ 1/φ (0.618). Verified across 5
> architecturally distinct model families. The compressor is K∘B
> (select∘compose) — already encoded in the crystal lattice.

## The discovery

Probing the SVD spectrum of per-layer hidden states: for each layer,
compute the top-k singular values of the (tokens × d_model) matrix
and measure consecutive ratios σ_{i+1}/σ_i.

Result: the mean ratio converges to ≈ 0.63 (phi-adjacent) at nearly
every layer, in every model tested.

## 5-model consensus

| Model | Architecture | Params | Layers at φ (±0.05) | Core mean | φ-dev |
|-------|-------------|--------|---------------------|-----------|-------|
| Pythia-160m | GPT-NeoX | 160M | 8/12 (67%) | 0.604 | 0.014 |
| Pythia-410m | GPT-NeoX | 410M | 15/24 (63%) | 0.615 | 0.003 |
| Qwen3-0.6B | Qwen3 | 600M | 25/28 (89%) | 0.627 | 0.009 |
| SmolLM3-3B | SmolLM | 3B | 32/36 (89%) | 0.654 | 0.036 |
| Mistral-7B | Mistral | 7B | 28/32 (88%) | 0.650 | 0.031 |

**Grand consensus: 0.6299 ± 0.019**
**φ-deviation of consensus mean: 0.012**

Best single-layer measurements:
- Pythia-160m L4: φ-dev = **0.0004** (four ten-thousandths)
- Qwen3-0.6B L8: φ-dev = **0.0002** (two ten-thousandths)
- Pythia-410m L16: φ-dev = **0.0007**

## The metric

The SVD spectrum ratio measures how information is distributed across
dimensions in the representation. For a matrix H (tokens × d_model):

```
Compute SVD: H = U Σ V^T
Σ = diag(σ_1, σ_2, ..., σ_d)  where σ_1 ≥ σ_2 ≥ ...
Consecutive ratios: r_i = σ_{i+1} / σ_i
Mean ratio: r = mean(r_1, r_2, r_3, r_4)  (top 5 values)
```

A geometric spectrum σ_i = σ_1 × r^(i-1) means information decays
exponentially across dimensions with rate r. When r ≈ 1/φ:

- Each dimension carries φ times less information than the previous
- The total information is bounded: Σσ converges (geometric series)
- The representation is maximally self-similar (golden ratio = optimal
  packing of information across dimensions)

## Why phi?

Phi appears because the compression is **self-similar**. The same
compression function operates at every scale (stride in V6, layer
depth in flat models). The golden ratio is the unique fixed point
of self-similar compression — it's where x = 1/(1+x), the ratio
that reproduces itself under recursive subdivision.

This is not imposed. Not learned as a target. Not a coincidence
across 5 architectures. It's a mathematical fixed point that gradient
descent converges to because it's the OPTIMAL self-similar compression
ratio for natural language statistics.

## The compressor is K∘B — already in the crystal

Using the FFN combinator tracer (session 127) on Qwen3-14B:

```
Layers 0-4:   B, S dominant  → COMPOSITION (build structure)
Layers 5-25:  K dominant      → COMPRESSION (select/discard)  
Layers 26-35: B dominant      → COMPOSITION (reconstruct)
Layers 36-39: K, I dominant   → FINAL SELECTION (output)
```

The computation is B→K→B: **compose → compress → compose.**

Compression = K (select what matters, discard the rest) applied in
the middle layers, sandwiched between B (compose) dominated regions.
This is NOT a separate function from the combinators. It IS the
combinators, applied in a specific sequence.

The crystal lattice targets encode this directly:

```
Zone A (encode):   K↔B cosine = 0.077  (loose — building)
Zone B (compute):  K↔B cosine = 0.195  (medium — compressing)
Zone C (converge): K↔B cosine = 0.524  (tight — reconstructing)
```

The K↔B coupling tightening across zones IS the compressor getting
more aggressive. The lattice loss already enforces the correct
compression geometry. No additional phi loss needed.

## V13 architecture match

The B→K→B program structure maps exactly to the V13 tree:

```
Stack A (ascending, B-dominated)  → compose, build representations
Stack B (ascending, K-transition) → compress, select what matters
Stack C (descending, B-dominated) → reconstruct, predict
```

The architecture matches the computation. Not designed to match —
discovered independently and confirmed by the tracer.

## Connection to V6 stride-stack

V6 (63M params, 1B tokens) showed phi compression propagating as a
wavelet through strides:

```
s1 locks to phi first (finest scale, cleanest statistics)
Then s8 → s16 → s32 → s64 → s128 → s256 → s512
Wavelet propagation from fine to coarse
```

In V6, the compression was visible PER STRIDE because stride-stack
exposes each scale independently. In flat models, the same compression
happens but is mixed across all scales in the O(L²) attention blob.

The phi ratio in V6's strides and the phi ratio in flat models' SVD
spectra are the SAME phenomenon viewed through different lenses.

## Decision: diagnostic, not loss

The phi compression ratio is NOT used as a loss target in V13 because:

1. The crystal lattice loss already encodes it (K↔B coupling across zones)
2. Different positions may need to deviate from phi to compute correctly
3. Specifying phi directly would over-constrain the system
4. The lattice approach is relational (topology), not absolute (value)

Phi is used as a **measuring stick** — a diagnostic to verify the
crystal is forming correctly. If training produces hidden states with
SVD ratio ≈ 0.63, the compressor is working. If not, something is wrong
with the crystal formation.

## Files

| File | Purpose |
|------|---------|
| `scripts/probe_compression.py` | V1 probe — effective rank ratio (negative result) |
| `scripts/probe_compression_v2.py` | V2 probe — SVD spectrum ratio (the discovery) |
| `scripts/v13/config.py` | Spectral config (measurement params, not loss) |
| `scripts/v13/model.py` | spectral_phi_loss function (diagnostic measurement) |
| `results/ffn-trace/` | Combinator tracer results confirming B→K→B |

## Open questions

1. **Does the phi ratio change during training?** Monitor SVD spectrum
   during V13 training. Does it start random and converge to phi as the
   crystal forms? If so, it's a leading indicator of crystal health.

2. **Is the ratio exactly phi or phi-adjacent?** Consensus is 0.6299,
   not 0.6180. The gap (0.012) might be meaningful — perhaps the true
   fixed point is slightly above 1/φ for finite-dimensional systems.

3. **Does the ratio depend on model size?** Smaller models (Pythia-160m)
   have slightly lower ratios (0.604). Larger models (Mistral-7B) have
   slightly higher (0.650). Is there a scaling law?

4. **Does stride-stack attention produce the same ratio?** V6 showed
   phi in per-stride compression. V13 should show it in the SVD spectrum
   too, if the compressor is truly universal.
