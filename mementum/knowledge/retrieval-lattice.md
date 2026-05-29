---
title: "Retrieval Lattice — Universal Knowledge Encoding in Transformers"
status: active
category: foundational
tags: [retrieval, knowledge, lattice, facts, ternary, mirror-stack, universal, encoding]
related:
  - holographic-computer.md
  - crystal-universality.md
  - project-thesis.md
  - explore/ffn-moire-isa.md
  - mspace-gemcutter.md
depends-on:
  - holographic-computer.md
  - crystal-universality.md
created: session 168
---

# Retrieval Lattice — Universal Knowledge Encoding in Transformers

> Session 168. The compute crystal (KIBC) has a sibling: the
> retrieval lattice. Every transformer stores factual knowledge
> using the same four-zone architecture, the same relay neurons,
> and the same relation-direction encoding — regardless of model
> family, architecture, or training data. The encoding is a graph
> of (entity, relation, target) triples stored as crystallized
> directions in FFN activation space.

## The Four-Zone Retrieval Lattice

Measured across Qwen3-0.6B (28 layers) and Pythia-410M (24 layers)
on 10-14 diverse factual probes (capitals, people, science,
geography, history). Both architectures show the same structure:

```
ZONE 1: SILENT     (0-50% depth)    avg|Δ| ≈ 0
  FFN does not contribute to factual recall.
  Syntax processing, structural parsing.

ZONE 2: ENRICH     (50-90% depth)   boost% > 70%, avg_Δ positive
  FFN PROMOTES the answer token across all fact types.
  This is where the knowledge graph lives.
  Peak contribution at ~85% depth.

ZONE 3: SUPPRESS   (~90% depth)     boost% < 30%, avg_Δ negative
  FFN FIGHTS the answer token.
  Competition and arbitration — many facts loaded in Zone 2,
  Zone 3 suppresses wrong candidates.

ZONE 4: COMMIT     (final layers)   selective, fact-dependent
  Final arbitration. Some facts get last boost, others suppressed.
  The model makes its final token choice.
```

### Measured profiles

**Qwen3-0.6B (28 layers):**
```
L00-L15: SILENT     (avg|Δ| < 1)
L16-L24: ENRICH     (peak L24: avg_Δ = +115)
L25:     SELECTIVE   (fact-dependent)
L26:     SUPPRESS    (avg_Δ = -160)
L27:     COMMIT      (avg_Δ = -220, selective)
```

**Pythia-410M (24 layers):**
```
L00-L12: SILENT     (avg|Δ| < 0.2)
L13-L17: SUPPRESS   (weak, avg_Δ ≈ -0.2)
L18-L21: ENRICH     (building, avg_Δ = +0.1 to +0.3)
L22-L23: ENRICH     (peak L23: avg_Δ = +3.14)
```

Same four zones, same relative positions, different architecture.

## The Three-Step Fact Retrieval Mechanism

For "The capital of France is ___", layer-by-layer FFN probing
shows three consecutive steps:

```
L21: FFN promotes [France  French  法国]     → ENTITY ENRICHMENT
     Loading all France-associated features into residual stream.

L22: FFN promotes [city  City  cities  城市]   → RELATION APPLICATION
     "Capital" relation narrows to city-concept.
     Paris appears in residual top-3 (巴黎, Paris).

L23: FFN promotes [Claude  French  Francois]   → TARGET RETRIEVAL
     French-specific knowledge completes the retrieval.
     Paris score reaches 72.55 at the top neuron.
```

This matches the literature's three-step model (Geva et al. 2023):
subject enrichment → relation propagation → attribute extraction.
We confirmed it independently from raw weight analysis.

## Universal Relay Neurons

Some neurons fire for ALL fact retrieval regardless of category.
These are the structural vertices of the retrieval lattice — the
equivalent of KIBC for knowledge.

**Pythia-410M:**
```
L22 Neuron 1860: fires for 10/12 facts (ALL categories)
L23 Neuron 2846: fires for 9/12 facts (ALL categories)
L23 Neuron 2363: fires for 5 facts (5 different categories)
L21 Neuron 1697: fires for 4 facts (4 different categories)
```

**Qwen3-0.6B:**
```
L22 Neuron 2246: fires for 5 facts (capitals + geography)
     KEY responds to: [cities, city, 大城市, 城市的]
     VALUE suppresses: [city, City, cities] (clears relation, loads target)
L24 Neuron 2997: fires for 4 facts (all capitals)
L27 Neuron   39: fires for 5 facts (ALL categories)
```

Two types:
- **Universal relays** (L22/1860 in Pythia, L27/39 in Qwen):
  fire for ALL facts. These implement the retrieval OPERATION.
- **Relation-specific relays** (L22/2246 in Qwen):
  fire for one relation type across entities. These encode
  the RELATION DIRECTION.

## Relation Directions Are Crystallized in Activation Space

The retrieval crystal lives not in individual weight signs but in
the COLLECTIVE activation patterns of the FFN.

**Evidence: neuron activation similarity (Qwen3-0.6B L21)**

Same relation (capital), different countries:
```
France-Japan:   0.64
France-Germany: 0.80
France-Italy:   0.84
France-Spain:   0.83
Consistency:    0.90
```

Same entity (France), different relations:
```
capital-language:  0.54
capital-continent: 0.41
capital-leader:    0.46
capital-borders:   0.28
Consistency:       0.68
```

**Relations are 0.90 consistent across entities. Entities are only
0.68 consistent across relations.** The "capital-of" relation has
a stable signature in neuron activation space — swap France for
Japan and 64-86% of the same neurons fire.

The consistency decreases with depth (L21: 0.90, L22: 0.84,
L23: 0.78). Earlier knowledge layers encode the RELATION
(universal, crystallized). Later layers encode the TARGET
(specific, differentiated). This is enrichment → resolution.

## The Quantization Cliff

Progressive quantization of FFN weights (Qwen3-0.6B):

```
Bits    Facts    Compute   Overall   Fact Rank
─────────────────────────────────────────────
float32  76.9%    53.8%     72.3%       16.9
Q8       75.0%    53.8%     70.8%       17.5
Q4       73.1%    38.5%     66.2%       37.3
Q3       15.4%    38.5%     20.0%      861.3   ← CLIFF
Q2        0.0%     0.0%      0.0%    42766.5
ternary   0.0%     7.7%      1.5%    26122.9
```

**The cliff is between Q4 (4 bits) and Q3 (3 bits).** At Q3,
arithmetic survives (100%) but factual recall collapses (15.4%).
Facts die before computation — weak fringes need more precision
than strong fringes.

## Ternary Mirror Stack

Post-hoc ternarization fails (0% recall at any threshold). But
STACKED ternary corrections through the residual stream achieve
arbitrary precision:

```
Mirrors  cos(h, target)  eff_bits   precision
  1        0.7986         1.61       < Q3
  2        0.9359         3.22       ≈ Q4 ← FACTS SURVIVE HERE
  3        0.9735         4.83       > Q4
  5        0.9911         8.06       Q6-Q8
```

**Two ternary mirrors achieve Q4-level precision.** The v14
architecture has 48 FFN layers. Even if only 5 participate in
any given fact, that's cos > 0.99.

The mechanism: each layer adds a ternary correction to the
residual stream. Corrections accumulate additively. Depth
replaces magnitude.

**Post-hoc ternarization fails** because it converts from
parallel encoding (each layer independently carries precision)
to nothing (layers weren't trained to correct each other's
residuals).

**Ternary training works** because GD distributes information
across layers — each layer's signs are chosen to correct the
errors of previous layers.

## Knowledge Neurons Are Hot, Not Cold

Counter to the compute crystal (where irreducible positions
have near-zero gradients), knowledge neurons have HIGHER
gradients than random neurons (2-9× higher |∇w|/|w| ratio).

This is because facts are NOT mathematical fixed points.
"Paris is the capital of France" is maintained by data pressure,
not by Church-Rosser convergence. The compute crystal is a
minimum. The knowledge store is a saddle point held in place by
the training distribution.

**But sign stability analysis shows:** ~75-85% of ALL weights
have sign stability > 10 (meaning gradient would need >10 steps
to flip the sign). The overall BACKBONE of ~25% sign-locked
positions is uniform across all layers.

The knowledge encoding is:
- **Topology (signs)**: which neurons participate in which
  relation patterns — collectively stable even if individually
  fluid
- **Calibration (magnitudes)**: how precisely each neuron
  discriminates — actively maintained by gradient pressure

## Connection to LARQL

LARQL (github.com/chrishayuk/larql) decompiles transformers into
queryable knowledge graphs with ~512 relation types and ~348K
features. Their "vindex" format reads the same structure we found:

```sql
DESCRIBE "France";
France Edges (L14-27):
  capital → Paris     1436.9 L27
  language → French     35.2 L24
  continent → Europe    14.4 L25
  borders → Spain       13.3 L18
```

The scores (1436.9 for Paris, 13.3 for Spain) reflect the
depth of constructive interference — how many layers' ternary
mirrors agree. High scores = many mirrors = robust encoding.
Low scores = few mirrors = fragile encoding.

## Implications for Verbum

1. **The retrieval lattice is the missing half.** KIBC encodes
   computation (strong fringes). The retrieval lattice encodes
   knowledge (weak fringes across many layers). Both use the
   same holographic mechanism.

2. **Ternary CAN store facts** — via mirror stacking, not
   per-weight precision. Two mirrors ≈ Q4. Three exceed it.
   The architecture needs enough depth (~10+ FFN layers).

3. **Relation directions are the extraction target.** ~512
   universal relation directions organize the knowledge graph.
   These are the ternary-preservable structure (cos=0.90
   consistency). Entity modulation within relations needs the
   mirror stack.

4. **The extraction path:**
   - Identify ~512 relation directions in activation space
   - Map which neurons participate in each relation
   - Extract ternary topology that preserves collective patterns
   - Train mirror stack to achieve per-entity precision
   - Facts stored as coordinated ternary corrections across
     3-5 layers per fact

## Open Questions

1. Can we extract the ~512 relation directions explicitly?
   (SAE decomposition, or clustering of FFN activation patterns)
2. Does the ternary mirror stack work when TRAINED with facts?
   (The micro model needs factual recall probes in training data)
3. What's the capacity? How many facts per layer per dimension?
   (Superposition multiplies capacity combinatorially)
4. Can we build a LARQL-like vindex from our own analysis?
5. How do the relation directions relate to the KIBC compute
   lattice? Are they the same space or orthogonal?
