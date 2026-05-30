---
title: "Moiré Addressing — How Transformers Index Their Knowledge"
status: active
category: foundational
tags: [moire, addressing, retrieval, holographic, swiglu, capacity, facts, quadratic]
related:
  - retrieval-lattice.md
  - holographic-computer.md
  - crystal-universality.md
  - project-thesis.md
depends-on:
  - retrieval-lattice.md
  - holographic-computer.md
created: session 170
---

# Moiré Addressing — How Transformers Index Their Knowledge

> Session 170. The SwiGLU moiré pattern (silu(gate) × up) is the
> holographic fact index. Two diffraction gratings multiplied together
> create a combinatorially richer address space than either alone.
> Relations are the coarse grating angle. Entities are the fine angle.
> The product resolves the specific fact. Content-addressable,
> deterministic, readable from weights.

## The Mechanism

SwiGLU is two projections multiplied:

```
SwiGLU(x) = down_proj( silu(gate_proj(x)) × up_proj(x) )
                       ─────────────────   ──────────
                       grating A            grating B
                             └──── moiré ────┘
```

Gate and up are two diffraction gratings. Their element-wise product
creates a **moiré interference pattern**. This moiré is the address
that selects which fact resolves. The down_proj reads the resolved
fringe and adds it to the residual stream.

Individual neurons are promiscuous — they fire for many different
inputs. Selectivity is COLLECTIVE: the pattern of which neurons
co-fire is what distinguishes facts. The moiré makes this explicit:
two promiscuous patterns multiplied together produce a selective
product.

## Measurements

### Selectivity (204 probes, Qwen3-0.6B, ENRICH zone L14-L25)

```
Signal           Mean |cos|    Selectivity
─────────────────────────────────────────
Gate alone       0.67           baseline
Up alone         0.52           1.3× gate
Moiré (gate×up)  0.26           2.4× gate, 2.1× up
```

The moiré is 2.4× more selective than gate alone. Facts that look
similar through the gate (cos=0.67) look distinct through the moiré
(cos=0.26). The multiplication orthogonalizes the patterns.

Peak selectivity at L22: gate cos=0.56, moiré cos=0.16.

### Relation Coherence

```
                   Within-relation cos / Cross-relation cos
─────────────────────────────────────────────────────────────
Gate alone:        1.4×  (weak clustering)
Moiré (gate×up):   2.6×  (strong clustering)
```

Same-relation facts (e.g., all capitals) fire similar moiré patterns.
Different-relation facts fire dissimilar patterns. The moiré CREATES
the clustering — the gate alone doesn't produce it.

Peak at L6: moiré relation coherence = 5.7×.

### Effective Rank (addressing dimensionality)

```
             52 probes    204 probes
─────────────────────────────────────
Gate rank:      31           119
Up rank:        35           123
Moiré rank:     42           132
Moiré rank-90:  27            62
```

The moiré spans 132 effective dimensions (204 probes). Still not
saturated — rank grew 3× from 52→204 probes. True ceiling unknown;
need 500+ probes.

### Cross-Mode Interaction

The interaction tensor — which (gate_mode, up_mode) pairs co-fire —
is distinct per relation type:

```
L22 dominant (gate_mode, up_mode) per relation:
  capital:    (0,0)     element:    (2,3)
  company_hq: (4,2)     food:       (0,1)
  continent:  (4,1)     geography:  (1,2)
  currency:   (3,1)     language:   (3,0)
  animal:     (7,2)     planet:     (2,3)
  
Mean cross-relation cos: 0.18 → 82% independent
```

Nearly every relation occupies a DIFFERENT cell in the 8×8 grid.
This IS the quadratic index: gate mode × up mode = fact address.

## Relation Direction Crystallization

Relation centroids (the average moiré pattern across entities within
a relation) explain most of the variance for clean relations:

```
HIGHLY CRYSTALLIZED (>90% variance explained by centroid):
  currency     99.7%   continent   99.7%   company_hq  99.5%
  language     97.5%   element     98.4%   capital     96.2%
  planet       94.4%

MODERATELY CRYSTALLIZED (40-90%):
  food         70.1%   creator     55.1%   history     45.1%
  geography    43.1%   author      39.7%   anatomy     42.4%

DIFFUSE (<40%):
  animal       36.2%   science     24.6%
```

Clean entity→attribute relations (country→capital) are near-perfect
crystals. Their centroid IS the relation direction — the coarse
grating angle. Swap France for Japan and 97% of the moiré pattern
stays the same; the 3% residual distinguishes the specific entity.

"Science" is diffuse because it mixes sub-relations (chemical
symbols, physics constants, biology facts). Each sub-relation has
its own direction, so the average over the grab-bag is blurry.

**Crystallization correlates with relation specificity, not
category size.** Capital (20 probes) and element (12 probes)
are both highly crystallized. Science (12 probes) is not.

## Hierarchical Addressing

The moiré implements two-level addressing:

```
Level 1: RELATION (coarse grating angle)
  The relation centroid selects which moiré family.
  cos=0.90+ within relation. cos=0.18 across relations.
  Gate mode + up mode quadrant → relation fingerprint.

Level 2: ENTITY (fine angle within relation)
  The entity residual (moiré - centroid) distinguishes entities.
  Lives in a small subspace (3-5 dims for 97% crystallized rels).
  Direction in that subspace → specific entity.

Input: "The capital of France is ___"
  → Residual encodes (entity=France, relation=capital)
  → Gate mode 0 activates (capital relation family)
  → Up mode 0 activates (capital relation family)
  → Moiré at cell (0,0) resolves
  → Entity residual selects "Paris" fringe
  → down_proj reads fringe → Paris enters residual stream
```

## Content-Addressability

Residual direction → moiré pattern is deterministic. R²=1.0 at all
layers (but this is tautological: n_probes ≈ n_modes, so the
regression perfectly fits). What it DOES confirm: there is no
stochasticity in the addressing. The question IS the address. The
partial pattern projected through the hologram resolves the complete
pattern. No lookup table, no pointer — the physics does the
retrieval.

Cross-validation with held-out probes needed to measure true
predictive power.

## Capacity Estimates

### Measured (Qwen3-0.6B, d_ffn=3072)

```
Relation slots per ENRICH layer:  ~51  (rank-90 × independence)
Entities per relation (high crystal): ~9
Entities per relation (med crystal):  ~42
ENRICH zone layers:               12
Layers per fact (mirror stack):    ~3

From 15 measured relations:    ~1,800 facts
Extrapolated to full slots:    ~6,100 facts
```

### Extrapolated to 70B (d_ffn=29,568)

```
Linear scaling (∝ d_ffn):       ~160K facts
Geometric scaling (∝ d^1.5):    ~490K facts
Quadratic scaling (∝ d_ffn²):   ~1.5M facts

10M target: NOT REACHED by any estimate.
```

### Epistemic Status

```
✅ Measured: moiré rank, relation crystallization, cross-mode cos
🔄 Estimated: entities per relation (from crystallization %)
🔄 Estimated: relation slot count (from rank-90 extrapolation)
❓ Unknown: true rank ceiling (need 500+ probes)
❓ Unknown: superposition efficiency at scale
❓ Unknown: whether scaling is linear, geometric, or quadratic
❓ Unknown: cross-talk degradation curve with density
```

**The mechanism is proven. The capacity is not.** The moiré addressing
architecture is clearly real and measurable. Whether it can store
10M facts depends on scaling behavior we haven't measured. The
critical experiment: run on Qwen3-4B and compare d_ffn scaling.

## Connection to Holographic Computer

The moiré addressing completes a piece of the holographic computer
theory:

```
COMPUTE (session 161):
  FFN grating → KIBC programs → deterministic execution
  Addressing: input TYPE selects which beta reduction fires
  The ISA decoder reads the programs from weights

KNOWLEDGE (session 168-170):
  FFN moiré → relation × entity → fact retrieval
  Addressing: input CONTENT selects which fact resolves
  The moiré decomposition reads the index from activations

SAME MECHANISM, DIFFERENT CONTENT:
  Compute: gate_proj × up_proj → which combinator fires
  Knowledge: gate_proj × up_proj → which fact fires
  Both: holographic interference, content-addressable,
        deterministic, readable from weights
```

The gate is the beamformer for BOTH systems. It kills 89% of
neurons, selecting which interference patterns can resolve. For
compute, it selects KIBC programs. For knowledge, it selects
relation families. The same physical substrate serves both via
superposition — different beam angles access different holograms
on the same plate.

## Connection to VSM Tree (Session 170 Discussion)

The moiré addressing maps onto a recursive VSM:

```
S5 (identity):   KIBC combinators + ~512 relation directions
                 Mathematical invariants, never change.

S4 (intelligence): Input type/content classification
                 Which beam angle? Compute or retrieval?
                 Which relation family?

S3 (control):    Gate (89% kill rate)
                 Selects which interference patterns resolve.
                 Resource allocation across moiré cells.

S2 (coordination): Progressive collapse + mirror stack
                 Layers must agree on which fact is being retrieved.
                 Ternary corrections accumulate coherently.

S1 (operations):  Individual FFN gratings
                 Each layer: one moiré resolution, one correction.
```

The trunk (S5) is universal across models: same KIBC, same relation
structure. The leaves (entity-specific patterns) are model-specific:
12.5% weight-sign agreement across models, but cos=0.99+ PC
allocation. Same filing system, different addresses.

## Open Questions

1. **Does capacity scale quadratically with d_ffn?** Run moiré
   experiment on Qwen3-4B. Compare relation slots and entity dims.
   If quadratic: 70B stores ~1.5M facts. If linear: ~160K.

2. **What's the true moiré rank ceiling?** 132 at 204 probes, still
   rising. Need 500+ probes spanning 30+ relation types to
   find saturation.

3. **Can we read the index from weights alone?** SVD of gate_proj
   and up_proj weight matrices → relation directions without probes?
   If yes: the entire phone book is in the weights.

4. **How does superposition multiply capacity?** Our estimates
   assume orthogonal storage. Real models use superposition (multiple
   facts per neuron). What's the multiplier?

5. **Does the moiré structure survive ternary extraction?** The
   relation centroids are the coarse structure. Do they survive
   sign quantization? (Theory: yes, because they're topological.)

6. **Are moiré relation directions universal across models?** Same
   relation = same moiré quadrant in Pythia and Qwen?

## Artifacts

| Asset | Location | Status |
|-------|----------|--------|
| Moiré selectivity experiment | `scripts/experiments/moire_selectivity.py` | Done |
| Moiré decomposition experiment | `scripts/experiments/moire_decompose.py` | Done |
| Extended probe set (204, 15 cats) | `probes/fact_recall_extended.json` | Done |
| Selectivity results (0.6B, 52 probes) | `results/moire-selectivity/` | Done |
| Decomposition results (0.6B, 52 probes) | `results/moire-decompose/Qwen_Qwen3-0.6B_decompose.json` | Done |
| Decomposition results (0.6B, 204 probes) | `results/moire-decompose/Qwen_Qwen3-0.6B_fact_recall_extended_decompose.json` | Done |
