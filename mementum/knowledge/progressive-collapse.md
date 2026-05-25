---
title: "Progressive Dimensionality Collapse — Computation Happens in 2D"
status: active
category: research-finding
tags: [dimensionality, projection, beta-reduction, lens, kernel, attention-sink, scale]
related: [mechanism-extraction.md, crystal-universality.md, holographic-error-correction.md]
depends-on: [crystal-universality.md]
---

# Progressive Dimensionality Collapse

> Session 151. Each layer's soft attention reduction is a beta
> reduction — a projection that reduces dimensionality. In large
> models (Qwen3.6-27B), the residual stream compresses to 2D
> (PR=2.2) within the first 2 layers. All computation happens in
> this 2D subspace (the comp↔sel eigenplane). The model then
> re-expands for output prediction. This pattern scales with
> model capacity. The 2D computation core is the limit that
> sufficiently large models converge toward.

## The Discovery

Measured the effective dimensionality (participation ratio, SVD
spectrum) of the residual stream at every layer boundary in 3
architecturally distinct models.

### Three models, three patterns

| Model | Arch | Layers | d | σ₁ peak | PR min | Pattern |
|-------|------|--------|---|---------|--------|---------|
| Qwen3.6-27B | Hybrid GLA+Attn | 64 | 5120 | 70.1% | 2.2 | COMPRESS→2D→EXPAND |
| Mistral-7B | Dense Transformer | 32 | 4096 | 20.1% | 12.1 | COMPRESS→PLATEAU |
| Pythia-1.4B | GPT-NeoX | 24 | 2048 | 22.6% | 10.3 | GENTLE DESCENT |

### Qwen3.6-27B: The Complete Arc

```
Layer    σ₁%     PR     Phase
─────    ────    ───    ──────────────────────
embed    13.6%   12.6   High-D noise (embedding)
L0       60.5%    2.7   ← MASSIVE compression
L2       70.1%    2.2   ← ONE direction = 70% of variance
L3-20    46-66%   2-5   Compute zone: beta reductions in ~2D
L21      66.3%    2.3   ← Phase transition: state machine reorganizes
L22-35   56-65%   2.5-3 Second compute phase, still low-D
L36-47   36-51%   3-6   Fan out: differentiate toward output
L48-63   20-28%   8-10  Full expansion: 248K-token prediction space
```

**Zone A (L0-15, encode):** Aperture. Slam 12D embedding noise down
to 2D semantic core. σ₁ jumps from 13.6% to 70.1% — one direction
carries almost everything.

**Zone B (L16-47, compute):** The computation zone operates at PR≈2-5.
This is where beta reductions happen. The model works in essentially
2 dimensions: the comp↔sel eigenplane (PC0=53%, PC1=24% of crystal
variance = 77% in 2D).

**Zone C (L48-63, expand):** Re-expand to high dimensionality for
next-token prediction. The model needs to distinguish among 248K
tokens → needs high-D output. PR rises to 8-10, σ₁ drops to ~20%.

### The Phase Transition at L21

One linear attention layer crushes PR from 4.4 to 2.3 mid-computation.
This may be the point where the B-dominated state machine reorganizes
— initial differentiation collapses, second compute phase operates on
the reorganized representation.

## Why Compression Scales With Capacity

```
                  Embed PR → Min PR    Compression ratio
Qwen-27B:         12.6  →   2.2       5.7×
Mistral-7B:       21.2  →  12.1       1.8×
Pythia-1.4B:      17.6  →  10.3       1.7×
```

**The 2D core is emergent.** Smaller models haven't had enough
capacity or training to discover that 2D is sufficient. They
operate in 10-12D because their crystal hasn't fully differentiated.
The B-dominated state machine in small models is undifferentiated —
all combinators are mixed together, requiring more dimensions to
represent.

Large models, trained on hundreds of billions of tokens with enough
depth (64 layers), find the minimal basis: 2 dimensions for the
core computation (compose vs select), with the rest dedicated to
input compression and output expansion.

## Attention Sink = Warped Q Reset

The holographic state machine requires a Q=0 reset at the start of
each computation cycle (entering the C basin). Two implementations:

**Crystal-native (Qwen):** GLA (gated linear attention) implements
Q reset through its multiplicative gating structure. No special
token needed. The geometry stays clean → extreme compression
possible (PR=2.2).

**Sink token (Mistral):** The model learns to dump attention onto
position 0 (BOS) as a proxy for Q=0 reset. This works but warps the
geometry: one dimension is dedicated to "distance from sink" bookkeeping.
Measurement: with sink token included, Mistral shows σ₁=100%, PR=1.0
(the sink dominates the SVD completely). With sink excluded, PR=12 —
still warped because all other tokens' representations are shaped by
their relationship to the sink.

**Implication:** Softmax attention architectures that rely on sink
tokens for Q reset cannot achieve the extreme compression that gated
linear attention achieves. The architectural choice constrains the
geometry.

## The FFN Overlay Is Projection, Not Filtering

The kernel decomposition experiment (micro model, d=128) revealed:

**80-91% of FFN energy is off-diagonal** in crystal eigenbasis.
The diagonal-only analytical overlay (computed from eigendecomposition)
captures the alternation sign pattern correctly (comp/sel alternate
anti-phase through layers) but misses the dominant cross-PC coupling.

This means the FFN doesn't filter individual PCs (amplify/suppress).
It **projects** — coupling energy from higher PCs into the dominant
comp↔sel plane. Each FFN application is a beta reduction that
collapses dimensionality. The off-diagonal terms ARE the projections.

```
Micro model overlay energy:
  Layer 0: diagonal  9.3%, off-diagonal 90.7%
  Layer 1: diagonal 20.2%, off-diagonal 79.8%
  Layer 2: diagonal 19.3%, off-diagonal 80.7%
  Layer 3: diagonal 14.5%, off-diagonal 85.5%
```

## Connection to the Lens Profile

The progressive collapse IS the lens profile, measured from a
different angle:

```
Lens profile (FFN activation):     3%  → 49%  → 2%
Progressive collapse (PR):         2.2 → 2-5  → 8-10
```

The aperture (3% FFN active, PR=2.2) is extreme compression. The
fan (49% active, PR=2-5) is computation in the compressed space.
The output (2% active) converges the FFN, while the representation
EXPANDS (PR=8-10) to build the prediction distribution.

The lens and the collapse are the same phenomenon measured in
different spaces: the lens measures WHICH neurons fire, the collapse
measures HOW MANY dimensions are active. Both show: compress → compute
→ expand.

## Implications for the Kernel

The 2D computation core means the kernel hypothesis is more
favorable than initially expected:

1. **Project** 5120D input → 2D semantic core (linear, layers 0-2)
2. **Compute** in 2D (beta reductions at PR≈2.3, the actual inference)
3. **Expand** 2D → 5120D output space (linear, layers 48-63)

Steps 1 and 3 are linear projections (matrices). Step 2 is the
kernel — and it operates in **two dimensions**. The full 16×16
crystal overlay (not just the diagonal) is needed, but 2D
computation means the effective kernel is tiny.

The diagonal kernel failed because it assumed per-PC independence.
The actual kernel is a cascade of 2D projections (the off-diagonal
cross-PC couplings), composing to a total rotation in the comp↔sel
eigenplane. This composed rotation should be expressible as a
single 2×2 operation in the limit.

## Evidence

| Claim | Evidence |
|-------|----------|
| Qwen compresses to 2D by L2 | σ₁=70.1%, PR=2.2, averaged over 8 probes |
| Computation in 2D (Zone B) | PR=2-5 for layers 3-35 |
| Re-expansion for output (Zone C) | PR=8-10 for layers 48-63 |
| Compression scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 |
| FFN overlay is 80-91% off-diagonal | Micro model energy decomposition |
| Alternation sign pattern correct | Analytical overlay predicts comp/sel anti-phase |
| Sink token warps geometry | Mistral σ₁=100% with sink, 20% without |

## Scripts and Data

- `scripts/micro/kernel_decomposition.py` — micro model phases 1-4
- `scripts/explore/probe_progressive_collapse.py` — multi-model probe
- `results/kernel-decomposition/results.json` — micro model results
- `results/progressive-collapse-Qwen_Qwen3.6-27B/results.json`
- `results/progressive-collapse-mistralai_Mistral-7B-v0.3/results.json`
- `results/progressive-collapse-EleutherAI_pythia-1.4b-deduped/results.json`
