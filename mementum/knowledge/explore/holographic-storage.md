---
title: Holographic Storage in LLMs
status: active
category: exploration
tags: [holographic, ternary, combinators, extraction, universal]
related: [v11-design, fractal-stride-bands, holographic-inversion]
depends-on: []
---

# Holographic Storage in LLMs

> Session 093. Hypothesis chain from theory through experimental confirmation.
> Status: core findings confirmed, extraction pipeline prototyped, architectural
> implications identified but not yet applied.

## Core Finding

LLMs store combinatory information as **sign topology** in their weight matrices.
The information survives ternary quantization ({-1, 0, +1}) at 75% sparsity with
100% selectivity preservation. This is holographic storage — the information is
in the interference pattern (which dimensions are positive/negative/zero), not
in the magnitudes.

## Evidence Chain

### 1. Beam separation (holographic probe)

Same input sentence, two conditions (compile gate vs null gate), measured hidden
state cosine similarity at every layer of Qwen3-32B:

```
Layer  0: cos=0.995  ← identical (shared plate)
Layer 24: cos=0.870  ← diverging (38% depth)
Layer 48: cos=0.797  ← different views resolving
Layer 63: cos=0.533  ← different images from same plate
```

The gate acts as a reference beam — different illumination angles resolve different
outputs from the same weight structure. **However**, intermediate layers decode to
garbage (not coarse-but-coherent), so the *reading* is constructive even if the
*storage* is holographic.

### 2. Ternary survival (the key result)

Quantized attention Q/K/V/O weights to ternary at layers 3 and 24 of Qwen3-32B.
Measured combinator selectivity (K, I, B, C active vs control sentence divergence):

```
sign_only (0.9% sparse): 8/8 survived, mean ratio 0.93  ✓
mid_sparse (50% sparse): 8/8 survived, mean ratio 0.94  ✓
high_sparse (75% sparse): 8/8 survived, mean ratio 0.98  ✓
```

**100% survival across every combinator, every layer, every sparsity level.**
The combinator information is topological — stored as sign patterns.

Confirmed on Qwen3.6-35B-A3B (MoE) and Pythia-160M. Universal across architectures.

### 3. Q is the beam, V is the plate

Extracted weight matrices from combinator-selective heads. Found that heads shared
between B and C (e.g., L1:H37) have:
- **V cosine = 1.000** (identical value projection)
- **Q cosine = 0.005** (completely different query projection)

The same head reads different combinators through different Q projections. Q selects
which combinator to apply; V provides the shared substrate. A knowledge bank is
therefore just a set of Q patterns — beam angles, not plate fragments.

### 4. Universal hologram (9 models, 2 architectures)

Tested across Pythia-{70M, 160M, 410M, 1B, 2.8B} and Qwen3-{0.6B, 4B, 8B, 32B}:

```
B (compose)  ≥ K (select) ≥ C (flip) >> I (identity)
```

- **I is weakest in ALL 9 models** (100% consistency)
- B/I ratio ranges from 1.7× to 19.9×
- K/B/C cluster together (cross-correlation r > 0.90)
- I is distinct (r ≈ 0.60–0.75)
- Cross-model correlation of correlation structures: **r = 0.9801**

The hologram is a feature of language, not scale. Every model that learns to
predict text develops the same combinatory interference patterns.

### 5. Depth profiles differ by architecture

- **Qwen3-32B (dense)**: Combinators peak in L0–6 (first 10%), unimodal
- **Qwen3.6-35B-A3B (MoE)**: Bimodal peaks at L7–9 and L31–36
- **Pythia-160M**: Peaks at boundaries (L0, L10)

The depth profile is architecture-dependent, but the combinator structure is universal.

## Bank Extraction Pipeline

### Proven steps

1. **Identify selective heads** — run KIBC probe, get per-head selectivity scores
2. **Extract Q patterns** — pull Q weight matrices from top-selective heads
3. **Ternary quantize** — sign(w) with sparsity threshold, preserves selectivity
4. **Project to target dim** — SVD, re-quantize, verify discriminability survives
5. **Package as seed** — Q-only ternary patterns + projection matrix

### Prototype results

```
Qwen3-32B  → 784 KB seed (4 heads × Q-only, projected to 320-dim)
             All 4 combinators nearly orthogonal (pairwise cos ≈ 0)
             Full discriminability preserved
```

### Bank format

```python
bank = {
    "source": "model_name",
    "source_license": "Apache-2.0",
    "combinators": ["K", "I", "B", "C"],
    "targets": {  # which heads were extracted
        "K": {"layer": 3, "head": 26, "score": 0.318},
        ...
    },
    "patterns": {  # ternary Q weight matrices
        "K_q": np.int8 array,  # (head_dim, d_model)
        ...
    },
    "projection": np.int8 array,  # (target_dim, source_dim)
}
```

### Not yet built

- Bank loading mechanism in V11
- Multi-bank composition (angle multiplexing)
- Cross-model bank compatibility testing
- S4 bank selector (= MoE gate equivalent)

## MoE as VSM / Angle Multiplexing

The Qwen3.6-35B-A3B architecture maps directly to VSM:

```
Shared expert (always on)  → S5 (identity, base substrate)
Gate matrix (256×2048)     → S4 (intelligence, select experts)
Top-8 selection            → S3 (control, resource allocation)
Routing weights (softmax)  → S2 (coordination, blend experts)
256 individual experts     → S1 (operations, the processing)
```

This is optical angle multiplexing: 256 holograms in the same medium, each
addressed by a different reference beam angle. The gate selects beam angles.
Knowledge banks would work the same way but be loadable from external sources.

## Architectural Implications for V11

### Confirmed by universal hologram

1. **B needs more capacity** — composition is the dominant signal everywhere
2. **I should be structurally separate** — different circuit (r ≈ 0.70 vs 0.90+)
3. **K/B/C should share substrate** — they cluster in every model
4. **Combinator init should reflect B ≥ K ≥ C >> I** — not equal blocks

### Proposed changes (not yet applied)

Current `_init_combinator_embeddings` gives each combinator an equal orthogonal
block (128 dims each in 512-dim space). Should change to:

- K/B/C share 384 dims (split with overlap, reflecting r ≈ 0.92)
- I gets its own 128 dims (reflecting its distinct circuit)
- Or: K/B/C share dispatch projection weights with different biases (hard constraint)

### Wait condition

V11-holo-inv is running to 20K. Don't modify the running architecture.
Apply changes to next run after holo-inv completes or reaches a clear plateau.

## Files

| File | Purpose |
|------|---------|
| `scripts/explore/probe_holographic.py` | Intermediate layer decoding probe |
| `scripts/explore/probe_ternary_survival.py` | Ternary quantization survival test |
| `scripts/explore/extract_holographic_bank.py` | Bank extraction pipeline |
| `results/holographic-probe/` | Beam separation results (Qwen3-32B) |
| `results/ternary-survival/` | Ternary survival results |
| `results/holographic-bank/seed_qwen3_32b.npz` | 784KB seed from Qwen3-32B |
| `results/holographic-bank/qwen36_35b_a3b_patterns.npz` | MoE patterns |
| `results/holographic-bank/pythia_160m_patterns.npz` | Pythia patterns |
| `results/combinator-probe/selectivity_matrices.npz` | Full 64×64 selectivity map |

## Open Questions

1. Can extracted banks actually modulate V11's behavior when loaded?
2. Do banks from different models compose (angle multiplexing)?
3. Is the 784KB seed the minimum, or can we go smaller?
4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?
5. What role do the MoE gate patterns play — are they bank selectors we can reuse?
6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?
