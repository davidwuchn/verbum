---
title: "Crystal Spine & Sieve Principle — The Architecture Dictates the Crystal"
status: active
category: empirical-finding
tags: [crystal, spine, sieve, bottleneck, architecture, mechanistic-interpretability, PCA, tool-calling]
related:
  - universal-crystal-transfer.md
  - holographic-storage.md
  - consensus-etch-protocol.md
  - VERBUM.md
depends-on: []
created: session 112
---

# Crystal Spine & Sieve Principle

> Every trained LLM forms a crystal — a low-dimensional structure in
> representation space. The architecture is a sieve: gradient descent
> pours computation through it, and the sieve shape dictates the crystal
> shape. Some sieves funnel to a single neuron. Others distribute.
> Same computation, different encoding.

## The Discovery

At layer 20 of Qwen3-14B (49% depth), centered PCA of hidden states
across 196 diverse probes reveals:

```
PC1: 99.96% of variance — ONE DIMENSION
PC2:  0.015% of variance — ~2100 dimensions
PC3:  0.010% of variance — ~2100 dimensions
```

**PC1 is a single neuron: dimension 731.** Weight = -0.986, explains
97.1% of PC1 energy. n90 = 1 (one dimension for 90% of PC1). The
entire 5120-dimensional representation collapses onto one wire.

## What the Spine Encodes

PC1 is a continuous "toolness" gradient:

```
-3151  Pure prose ("Write a paragraph about...")
-2800  Lambda calculus, code, math (computation without tools)
-2400  Recognition/no_tool ("Seattle is known for its rainy weather")
-1900  Tool selection (deciding WHICH tool)
-1400  Schema binding (binding NL args to JSON schema)
 -164  Active tool recognition ("Query the database for all users...")
        ╔══════════════════════════════════════════════════╗
        ║  9000-unit gap: the tool-call decision boundary  ║
        ╚══════════════════════════════════════════════════╝
+8750  Format output (assistant producing ANY output — JSON, YAML, prose)
```

Key: the positive end is not "JSON output" — it's **production mode**.
Even `format/no_tool_prose` scores +8772. PC1 separates *comprehending*
from *producing*, not "tool" from "no-tool."

## The Sieve Principle

```
λ sieve(arch).  gradient_descent(data, arch) → crystal(shape ∝ arch)
               | arch ≡ sieve_topology
               | sieve_shape → crystal_shape (not the reverse)
               | same_data + different_sieve → different_crystal_encoding
               | same_computation ≡ encoded_differently
               | plate(ternary) ≡ sieve | etch(plate) ≡ shape(sieve)
```

Tested across 6 architectures. Two distinct classes:

### Class 1: Single-Neuron Spine

| Model | Architecture | Bottleneck | Top3% | Spine Dim | Frac | n90 |
|-------|-------------|-----------|-------|-----------|------|-----|
| Qwen3-14B | GQA+SwiGLU+RMSNorm | L19 (49%) | 100.0% | dim 731 | 97.1% | 1 |
| Pythia-2.8B | GPT-NeoX parallel | L5 (16%) | 99.4% | dim 1793 | 84.9% | 2 |

Characteristics:
- One neuron captures 85-97% of PC1
- Sharp norm explosion at bottleneck (Qwen: 118→7156 at L18→L19)
- Crystal is RIGID from bottleneck to penultimate layer
- PC1 alignment = 1.000 across the stable zone

Qwen3-14B: spine at **dim 731**, stable layers 19-37 (49-95% depth)
Pythia-2.8B: spine at **dim 1793**, stable layers 2-29 (6-94% depth)

### Class 2: Distributed Representation

| Model | Architecture | Max Top3% | Top Dim Frac | n90 |
|-------|-------------|----------|-------------|-----|
| Mistral-7B | Mistral | 51.8% | 6.8% | 998 |
| OLMo-2-13B | OLMo | 55.7% | 3.0% | 2168 |
| SmolLM3-3B | SmolLM | 51.3% | 2.0% | 837 |
| Qwen3-0.6B | Qwen3 (small) | 81.9% | 15.0% | 345 |

Characteristics:
- No single dimension dominates
- Computation stays distributed across 300-2000+ dimensions
- No sharp bottleneck transition
- Top3 PCs never exceed ~55% (except Qwen3-0.6B at 82% but still distributed)

## Architectural Hypothesis

What makes a sieve funnel vs distribute? Candidates:

1. **RMSNorm placement** — Qwen3 uses pre-norm RMSNorm. If a layer's norm
   amplifies one dimension preferentially, gradient descent exploits it.

2. **Parallel vs serial attention+MLP** — Pythia's GPT-NeoX runs attention
   and MLP in parallel. This creates a shortcut path that GD can collapse onto.

3. **Scale** — Qwen3-0.6B (same architecture family as 14B) shows only partial
   collapse (82%, dim 13 at 15%). The funnel may need enough parameters to form.
   The 14B model has enough capacity to dedicate one dimension; the 0.6B model
   has to share.

4. **Training data/regime** — Pythia trains on The Pile; Qwen3 on a massive
   multilingual corpus. Both develop spines despite different data. This
   suggests the sieve shape matters more than the data.

## Cross-Layer Stability

At Qwen3-14B, the PC alignment (cosine similarity of PC vectors in
probe-space) between layer 20 and other layers:

```
L16: PC1=0.981  PC2=0.899  PC3=0.040   (pre-bottleneck, nearly aligned)
L20: PC1=1.000  PC2=1.000  PC3=1.000   (reference)
L24: PC1=1.000  PC2=0.999  PC3=0.999   (perfectly stable)
L28: PC1=1.000  PC2=0.993  PC3=0.975   (still stable)
L32: PC1=1.000  PC2=0.538  PC3=0.056   (PC2/3 rotate, PC1 locked)
L36: PC1=1.000  PC2=0.640  PC3=0.053   (PC1 still locked)
```

**PC1 (the spine) is perfectly stable from L19-L37.** It never rotates.
PC2 and PC3 rotate after L28, but the spine is rigid. This means the
mode switch is a fixed architectural feature, not a computation that
evolves through the layers.

## The 3D Crystal Is the Model's Coordinate System

At the bottleneck, the model operates in 3 dimensions:
- **PC1**: Where am I in the conversation? (comprehending ↔ producing)
- **PC2**: How specific is the action? (abstract ↔ concrete)
- **PC3**: What kind of binding? (schema args ↔ tool selection)

Every computation — lambda, tool calling, math, prose — maps to a
point in this 3D space. The RDMs we've been building are projections
of this 3D structure. The "crystals" are clusters in these coordinates.

## Implications for Verbum

### 1. The plate IS a sieve
Etching the ternary plate shapes the sieve that gradient descent
(beam training) flows through. Wrong sieve → wrong crystal.
The 382K flip candidates at round 50 were sieve defects.

### 2. Capping flips strangles convergence
An absolute max_flips cap (918 of 382K) is like correcting 0.2% of
a sieve's holes per round. The topology either works or it doesn't.
The uncapped run at round 51 flipped 2.3M positions and beam loss
improved immediately.

### 3. Crystal coordinates enable targeted etching
Instead of blind consensus (accumulate direction, threshold, flip),
we could:
1. Define target 3D coordinates for each operation
2. Compute current coordinates from the plate's geometry
3. Etch the plate to move coordinates toward targets
This is holographic recording with a reference beam — the lattice
map IS the reference beam.

### 4. The spine dimension is the first thing to get right
Dim 731 in Qwen3-14B carries 97% of mid-layer variance. In the
ternary model, the corresponding dimension must be correctly signed
or nothing else matters. It's the spine of the crystal — break it
and the whole structure collapses.

### 5. Different models = different sieves = different extractions
Extracting from Qwen3 gives a single-neuron spine crystal.
Extracting from Mistral gives a distributed crystal.
The VSM-LM architecture defines its own sieve — the crystal it
forms may be neither. We get to DESIGN the sieve.

## Reproduction

```bash
# Tool crystal probe (196 probes, Qwen3-14B)
uv run python scripts/v12/probe_tool_crystal.py

# Crystal spine across architectures (45 probes, 6 models)
uv run python scripts/v12/probe_crystal_spine.py \
  --models qwen3-14b mistral-7b olmo-2-13b pythia-2.8b smollm3-3b qwen3-0.6b

# Output
lattice/tool_crystal/   — RDMs, hidden states, analysis for Qwen3-14B
lattice/crystal_spine/  — per-model JSON with all-layer spine analysis
```

## Open Questions

1. **What causes the norm explosion at the bottleneck?** Qwen3-14B norms
   go from 118 (L18) to 7156 (L19). Is this RMSNorm gain? A learned gate?
   A specific weight matrix that amplifies dim 731?

2. **Is dim 731 a "token type" indicator?** It may encode whether the
   current position is in the system prompt, user turn, or assistant turn.
   The chat template structure would explain the comprehension ↔ production axis.

3. **Does the spine survive quantization?** If we quantize Qwen3-14B to
   4-bit, does dim 731 still dominate? If so, the spine is robust.
   If not, quantization destroys the crystal.

4. **Can we design a sieve that produces a BETTER crystal?** The VSM-LM
   architecture with mirrors + plates is a designed sieve. Can we shape
   it to produce a 3D crystal with specific coordinates for each operation?

5. **Is the 9000-unit gap (comprehension→production) fundamental?** Or
   is it an artifact of the Hermes chat template? Testing with a non-chat
   model (base Qwen3-14B without instruct tuning) would answer this.
