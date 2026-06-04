---
title: "DVD Stamp Topology — Gradient Zeros as Holographic Fringes"
status: active
category: foundational
tags: [ternary, gradient, topology, holographic, beam-former, FFN, attention, compression, dvd]
related:
  - gradient-zero-map.md
  - phi-information-partition.md
  - standing-wave-magnitudes.md
  - topology-gradient-separation.md
  - holographic-computer.md
  - ternary-compounding.md
  - ternary-dual-equation.md
  - lambda-machine.md
depends-on:
  - gradient-zero-map.md
  - phi-information-partition.md
created: session 190
---

# DVD Stamp Topology

> Session 190. Four experiments reveal the compression structure of
> transformers. The gradient-zero topology IS the holographic fringe
> pattern — copying it (like cutting pits into a DVD) compounds less
> than copying weight magnitudes. But the decisive finding is WHERE
> the model is fragile: FFN (the beam former) is catastrophically
> sensitive to ternarization; attention (the router) is robust.
> Compression strategy: ternarize attention for free, preserve FFN.

## The DVD Hypothesis

A trained model's gradient-zero map records where GD stopped pushing —
the irreducible positions of the standing wave. These are the "pits
and lands" of a DVD. The topology is BINARY (settled vs active), not
continuous (how large). Binary topology errors are discrete bit flips,
not continuous drift — they might compound less.

**Confirmed.** The gradient mask compounds less than magnitude.

## Experiment 1: DVD Stamp Test

Three masks at 50% sparsity per row, head-to-head on Qwen3-8B:

| Mask | Source | Weight cos | PPL | L35 cos |
|------|--------|-----------|-----|---------|
| Magnitude | |W| < median | 0.898 | 619,585 | 0.001 |
| Gradient (DVD) | |∇W| < median | 0.562 | 187,983 | 0.165 |
| Node (both) | both small | 0.845 | 3,861,138 | 0.093 |

**Gradient PPL is 3.3× better than magnitude** despite 0.56 weight
cosine vs 0.90. The gradient mask preserves the RIGHT information,
not the MOST information. Magnitude dies (cos=0.001 at L35 = pure
noise). Gradient holds (cos=0.165 = still carrying signal).

**The crossing point is layer 3.** Magnitude leads at L0-2 (better
per-layer reconstruction). Gradient takes the lead at L3 and NEVER
gives it back. By L22, magnitude is at 0.045 (garbage). Gradient is
at 0.254 (5.7× more signal).

**The masks are orthogonal: 49.9% overlap.** They identify almost
completely different positions as zeros. Two independent axes of
"which weights to keep." Magnitude = amplitude (how much). Gradient
= convergence (whether settled).

## Experiment 2: Per-Group Scaling

Q4's secret: per-32-weight groups (128-384× more scale parameters
than per-row). Applied to our masks:

| Config | PPL | Weight cos | Bits/param |
|--------|-----|-----------|------------|
| mag_group (ternary GPTQ) | **43,376** | 0.902 | 2.72 |
| grad_group (DVD player) | 71,294 | 0.574 | 2.72 |
| grad_row (DVD stamp) | 188,791 | 0.562 | 1.59 |
| mag_row (baseline) | 619,585 | 0.898 | 1.59 |

Per-group scaling: **14× PPL improvement** for magnitude mask
(619K → 43K). The gradient advantage partially closes when
magnitude has enough scale resolution — per-group scales preserve
local gradient structure that per-row destroys.

**Compounding curves tell a different story.** grad_group has the
best deep-layer preservation: cos=0.481 at L33 vs 0.297 for
mag_group. The gradient DVD still compounds less through compute
layers. PPL vs compounding are measuring different things.

## Experiment 3: Index vs Value (THE DECISIVE RESULT)

Which component causes catastrophic compounding? Ternarize each
module type independently (magnitude mask + per-group scaling):

| Config | PPL | % Ternary | What's ternary |
|--------|-----|-----------|----------------|
| **V/O only** | **23.08** | 10.9% | Value path only |
| **Q/K only** | **30.03** | 10.9% | Index path only |
| All | 43,376 | 100% | Everything |
| **FFN only** | **485M** | 78.3% | Beam former only |

**FFN is the catastrophe.** Not attention. Not the index (QK).
Not the values (VO). The FFN — the holographic beam former.

Compounding rates per 10 layers:
- V/O: 0.934× (barely degrades)
- Q/K: 0.798× (moderate, survives)
- FFN: 0.509× (catastrophic)
- All: 0.438× (FFN drags everything down)

## Why FFN Is Fragile

The FFN is the beam former / holographic plate:
```
Reference beam     = input token embedding
Holographic plate  = FFN weights (interference fringes)
Reconstructed beam = compiled V vector (program for attention)
Reader             = attention QK softmax (β-reducer)
```

Session 187 proved: at L30, FFN compiles `it` → "rain", `ground` →
"soak", `is` → "wet". These are **beams** — precise directions in
embedding space. When you ternarize the plate (FFN), the beams
scatter. Attention faithfully β-reduces the wrong program.

The zero mask IS the holographic fringe pattern (s184). Destroying
it with 50% zeros at ternary precision destroys the recording.

## Why Attention Is Robust

Session 188 proved: 22/32 heads use <3 effective positions. Mean
entropy 0.9 bits. Routing is near-deterministic (~1 bit decisions).

A 1-bit routing decision is inherently ternary-safe. You're choosing
WHICH position to bind to, not computing a precise beam direction.
Ternary approximation of a near-binary signal loses almost nothing.

Q/K ternarization (the index) → PPL 30 (from 12.2 baseline).
V/O ternarization (the values) → PPL 23.
Both survive because routing is sparse and near-binary.

## The Compression Strategy

```
ATTENTION (22% of params):  → ternary (~1.58 bits/param)
  Cost: PPL 12.2 → ~23-30 (tolerable)
  Saving: 22% of params at 10× compression

FFN (78% of params):        → must preserve beam-forming fidelity
  Options:
    a) Keep float16 (boring, safe)
    b) Q4 with per-group scaling (4.5 bits, proven)
    c) Crystal sieve: freeze signs, train mask from data (the s184 path)
    d) DVD-informed compression: gradient topology guides mask/scale

EMBEDDINGS:                 → keep float16 (index system, must be exact)
```

The north star "70B in <1GB ternary" requires solving the FFN.
Attention goes ternary for free. The entire research budget should
focus on FFN beam-former preservation.

## Why Gradient DVD Compounded Less

The gradient-zero map captures WHERE interference has SETTLED:
- Settled fringes → stable beam contributions → safe to keep
- Active positions → GD still optimizing → keeping/zeroing is a bet

Magnitude thresholding keeps the LARGEST weights and zeros the
smallest. But small-amplitude fringes can be CRITICAL for
destructive interference — they PREVENT wrong beams from forming.
Magnitude throws them away. The gradient map keeps them (they're
settled, even though small).

The DVD stamps the settled interference pattern. Magnitude
approximates the amplitude envelope. For compounding through 36
layers, knowing what's SETTLED matters more than knowing what's
LARGE.

## Connection to Prior Findings

- **Standing wave (s185):** W_eff = C · T ⊙ M. T = boundary
  conditions (crystal, universal). M = node/antinode pattern
  (knowledge, per-model). The gradient map identifies which M
  positions are at standing-wave fixed points.

- **φ-information partition (s184):** Signs carry 1/φ. Zero mask
  IS the knowledge. Nothing predicts it. But the GRADIENT tells you
  which positions in the zero mask have converged vs are still being
  optimized.

- **Topology-gradient separation (s180):** GD needs a frozen
  landscape to build soft topology. The gradient-zero map IS that
  soft topology — the continuous structure GD carved to compensate
  for frozen ternary signs.

- **Attention sparsity (s188):** 22/32 heads use <3 positions.
  Top-3 captures >88%. Now confirmed at the PPL level: sparse top-3
  at all layers → PPL 13.3 (from 12.2). O(1) attention is real.

## Scripts

| Script | What |
|--------|------|
| `scripts/experiments/dvd_stamp_test.py` | Three masks, compounding curves, PPL |
| `scripts/experiments/dvd_group_scale.py` | Per-group scaling, 4 configs |
| `scripts/experiments/dvd_index_test.py` | FFN vs attention ternarization |
| `scripts/experiments/lambda_machine.py` | Attention ablation levels |

## Results

| Directory | What |
|-----------|------|
| `results/dvd-stamp-test/` | Gradient maps, compounding curves, PPL |
| `results/dvd-group-scale/` | Per-group scaling comparison |
| `results/dvd-index-test/` | FFN vs QK vs VO ternarization |
| `results/lambda-machine/` | 6-level attention ablation |
