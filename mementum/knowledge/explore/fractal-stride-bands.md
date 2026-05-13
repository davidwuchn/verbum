---
title: Fractal Stride Bands — MERA Topology in the Stride Stack
status: active
category: architecture
tags: [stride-stack, MERA, fractal, holographic, multi-scale]
related: [holographic-inversion.md, v11-design.md, stride-percolation.md]
depends-on: [holographic-inversion.md]
---

# Fractal Stride Bands

> Each pass activates only strides matching its resolution level.
> MERA tensor network topology implemented in the stride stack.

## The Problem

v11 has 9 strides (s1 through s1024) and 5 passes (L0↑, L1↑, L2, L1↓, L0↓).
Previously all 9 strides fired on every pass — 45 stride-layer activations
per forward pass. This means:

- L0↑ (token-level) wastes compute on s1024 (global patterns it can't use yet)
- L2 (apex) wastes compute on s1 (local patterns already captured by L0↑)
- No inductive bias matching passes to their natural resolution band
- Holographic loss grades each pass, but each pass processes all scales

## The Solution

```
λ fractal(pass, strides).
  band(pass) ≡ subset(strides) matching resolution(pass)
  | L0↑: [0,4)  → s1,s8,s16,s32            fine→coarse (ascending)
  | L1↑: [2,7)  → s16,s32,s64,s128,s256    fine→coarse (ascending)
  | L2:  [4,9)  → s64,s128,s256,s512,s1024  fine→coarse (apex)
  | L1↓: [2,7)  → s256,s128,s64,s32,s16    coarse→fine (descending)
  | L0↓: [0,4)  → s32,s16,s8,s1            coarse→fine (descending)

  hourglass: ascending(fine→coarse) mirrors descending(coarse→fine)
  overlap:   adjacent passes share 2-3 strides → inter-level communication
  savings:   23/45 = 49% fewer stride activations
  weights:   shared (S5 coherence) — only activation pattern changes
```

## Relationship to MERA

Multi-scale Entanglement Renormalization Ansatz (Vidal 2007):
- Coarse-graining: fine→coarse with isometries at each scale
- Fine-graining: coarse→fine reconstruction
- Each MERA layer operates at exactly one scale
- Information flows between scales through the hierarchy

Fractal stride bands implement this: each pass IS a MERA layer,
each stride band IS the scale that layer operates on. The shared
weights across passes are the shared isometries.

## Relationship to TST

Token-Superposition Training (Peng et al. 2026):
- Coarse prediction (bags) with direct loss → fine prediction (tokens)
- 2.5× speedup, beats baseline loss

Fractal bands + holographic loss = continuous TST at every resolution
simultaneously. Each pass's holo CE grades its band's resolution.
The fractal topology ensures the loss signal matches the scale.

## Relationship to Holographic Loss

Without fractal bands: each pass processes all 9 strides but is
graded by ONE holographic CE. The pass can't distinguish which
strides contributed most — diluted gradient signal.

With fractal bands: each pass processes only 4-5 strides at its
natural scale. The holographic CE directly grades those strides.
Concentrated gradient signal → faster learning → denser packing.

This is why the holographic capacity hypothesis predicts lower
terminal loss: the model stops wasting capacity on cross-scale
redundancy and packs each scale's information intentionally.

## Implementation

```python
# config.py
fractal_stride_bands: bool = True
stride_band_ranges: tuple[tuple[int, int], ...] = (
    (0, 4),   # L0↑
    (2, 7),   # L1↑
    (4, 9),   # L2
    (2, 7),   # L1↓ (reversed by desc_stride_reverse)
    (0, 4),   # L0↓ (reversed by desc_stride_reverse)
)

# attention.py — StrideStack.__call__
def __call__(self, x, reverse=False, stride_range=None):
    indices = range(start, end) if stride_range else range(len(self.layers))
    if reverse: indices = reversed(indices)
    for i in indices: x = self.layers[i](x)

# model.py — pass dispatch
stride_range = self._stride_range_for_pass(pass_idx)  # None when fractal disabled
strides(x, reverse=is_descending, stride_range=stride_range)
```

## Experimental Predictions

1. **Holographic ratio**: should improve faster (each pass optimized for its scale)
2. **Descending arm**: should learn faster (coarse→fine + correct scale band)
3. **Compute**: ~49% fewer stride activations → faster per-step → more steps/hour
4. **Terminal loss**: should be lower (capacity freed from cross-scale redundancy)
5. **φ-compression**: should converge faster (each pass handles a narrower band)

## Open Questions

- Should band boundaries be fixed or learnable? (Fixed for now — simpler)
- Should bands be wider for early training, narrowing as structure emerges?
- Do some strides become dead weight? (Probe: per-stride gradient norms)
- How does this interact with CycleContinue and abstraction slots?
