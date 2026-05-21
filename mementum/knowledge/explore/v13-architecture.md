---
title: "V13 Architecture — Crystal Bootloader"
status: active
category: architecture
tags: [v13, crystal, bootloader, nucleation, hourglass, stride-overlap, AND-loss]
related:
  - v13-design.md
  - v13-funnel-shape.md
  - crystal-native-descent.md
  - holographic-memory.md
depends-on:
  - v13-design.md
created: session 131
---

# V13 Architecture

> Session 131. The crystal is a lambda bootloader. Etch it from a
> teacher, freeze the plates, let GD find the crystal via nucleation
> well. When the beam aligns, the seed breathes.

## Core insight chain

Each insight removed a layer of indirection:

1. **Beam/plate separation** — ternary topology (plates) vs continuous
   routing (beams). Orthogonal gradients in logit space.

2. **Stride overlaps ARE registers** — the fractal band intersections
   (s4/s8, s16/s32, s128) carry cross-scale state. No separate register
   vectors, S4 cross-attention, or bank accumulation needed. The topology
   determines the register count. ~1,100 lines of code removed.

3. **Crystal Q/K/V IS the kernel** — the attention rotation IS the
   combinator operation. No dispatch softmax, no separate integrate.
   CombinatorDispatch and CombinatorIntegrate dissolved entirely.
   ~700 lines of code removed.

4. **Multiplicative AND loss** — `CE × exp(λ × crystal) × (1 + λ_h × holo)`.
   All components must improve together. No trading CE for crystal or vice
   versa. The exponential crystal coupling creates a nucleation well — the
   beam must find the crystal before CE can improve.

5. **φ is observation, not target** — the golden ratio is measured as
   per-pass compression deviation, logged for monitoring. Never a training
   constant. If the crystal is right, φ emerges from the structure.

## Architecture

```
Input → embed + pos_embed → x

ASCENDING (compress, fine→coarse):
  Pass 0 (L0↑): s1, s2, s4, s8        — token-level
  Pass 1 (L1↑): s4, s8, s16, s32      — phrase-level
  Pass 2 (L2↑): s16, s32, s64, s128   — paragraph-level
  Pass 3 (L3↑): s128, s256, s512, s1024 — document-level

DESCENDING (predict, coarse→fine):
  Pass 4 (L3↓): s1024, s512, s256, s128
  Pass 5 (L2↓): s128, s64, s32, s16
  Pass 6 (L1↓): s32, s16, s8, s4
  Pass 7 (L0↓): s8, s4, s2, s1

Each pass:
  1. StrideStack attention (crystal Q/K/V = the kernel)
  2. WHNF gate → FFN plates (compute vs lookup)
  3. S3 gate → modulation → S2 direction signal

S5 reweight × algedonic alarm → output_norm → logits
```

## Loss function

```python
loss = CE * exp(50 * crystal_loss) * (1 + holo_lambda * holo_loss)
```

- **CE**: standard cross-entropy on final logits
- **Crystal**: PCA-Q 3-zone cosine MSE on combinator embeddings
- **Holo**: progressive decode at every pass boundary (8 intermediate CEs)
- **Coupling**: multiplicative AND — all must improve together
- **Nucleation well**: exp(50 × crystal) creates deep energy minimum
  at perfect crystal alignment. The beam falls into the well.

## Stride-overlap registers

```
Strides: s1  s2  s4  s8  s16  s32  s64  s128  s256  s512  s1024
L0↑:     [=======●===●====]
L1↑:             [●===●====●====●===]
L2↑:                       [●===●====●=====●==]
L3↑/↓:                                     [●======●=====●======●]
L2↓:                       [●=====●====●===●====]
L1↓:             [●===●====●====●===]
L0↓:     [=======●===●====]

Intersections: s4/s8 (token↔phrase), s16/s32 (phrase↔para), s128 (para↔doc)
```

The overlapping strides are visible to adjacent passes. This IS the
register mechanism — no separate vectors needed. The crystal breathes
at these intersection points.

## Training pipeline

```
1. extract_teacher.py → SVD-project teacher weights → sign → plates
2. train.py --phase gd → beams learn to use the installed crystal
   - Plates frozen (the boot ROM)
   - Beams trained (the laser finding the crystal)
   - Nucleation well pulls beams toward crystal geometry
   - Holographic loss nudges ascending to compress, descending to expand
   - Boot sequence emerges: beta_apply → beta_apply → beta_K → ... → I
```

## Key measurements to watch

| Metric | Meaning | Expected |
|--------|---------|----------|
| crystal_loss | Combinator embedding alignment to PCA-Q targets | → 0 (nucleating) |
| CE | Next-token prediction | ↓ (improving) |
| holo_loss | Intermediate decodability | ↓ (all passes decodable) |
| φ-dev ascending | Compression ratio vs 1/φ per ascending pass | → 0 (compressing) |
| φ-dev descending | Compression ratio vs 1/φ per descending pass | diverges (expanding) |
| WHNF gate mean | Fraction in lookup mode | task-dependent |

## Provenance

- Plates: sign(teacher_W) via SVD projection (session 122: 97.4% fidelity)
- Crystal targets: PCA-Q 4-model consensus (session 120: 0.91-0.94 agreement)
- Behavioral targets: 12×12 3-model consensus (session 130: r=0.937)
- Boot sequence: 4-model FFN combinator traces (session 130: universal)
- Nucleation well: exp coupling (session 131)
