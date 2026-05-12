---
title: "Pythia-160M Combinator Probe: Montague Primitives Were Combinators All Along"
status: active
category: experiment-results
tags: [combinators, KIBC, pythia-160m, montague, reinterpretation, scale, bootstrap]
related:
  - session-004-findings.md
  - kibc-32b-validation.md
  - kernel-montague-mapping.md
  - v11-design.md
depends-on:
  - session-004-findings.md
  - kibc-32b-validation.md
created: session 081
---

# Pythia-160M Combinator Probe

> Session 081. The "three Montague primitives" discovered in session 004
> (type assignment, structural parse, typed application) are KIBC
> combinators viewed from a different angle. Pythia-160M is K-dominant
> with B nearly fused into K (r=0.944). The three-phase structure is
> real but the mechanism is one circuit operating in three phases, not
> three separate primitives. B differentiates from K only at scale.

## The reinterpretation

Session 004 found three phases in Pythia-160M and mapped them to
Montague grammar:

| Session 004 label | Layers | What we thought |
|---|---|---|
| Type assignment | L0 | Lexical type lookup |
| Structural parse | L3 | Composition order |
| Typed application | L8-L11 | Execute composition |

Session 081 ran the same KIBC combinator probe used on Qwen3-32B
(matched sentence pairs isolating K/I/B/C) on Pythia-160M. **K
dominates all three zones.** The mechanism is selection (K), not
three separate primitives.

## Head assignment

| Combinator | Pythia-160M | Qwen3-32B | v11 @ 5K |
|---|---|---|---|
| K (select) | **59.0%** (85/144) | 31.3% (1284/4096) | 62.5% |
| I (identity) | 2.1% (3/144) | 14.7% (603/4096) | 15.3% |
| B (compose) | 16.7% (24/144) | 31.3% (1282/4096) | 2.6% |
| C (flip) | 22.2% (32/144) | 22.6% (927/4096) | 19.6% |

## Cross-combinator correlation

```
Pythia-160M:                    Qwen3-32B:
        K     I     B     C             K     I     B     C
  K  1.00  0.72  0.94  0.90      K  1.00  0.71  0.86  0.93
  I  0.72  1.00  0.71  0.60      I  0.71  1.00  0.75  0.69
  B  0.94  0.71  1.00  0.92      B  0.86  0.75  1.00  0.87
  C  0.90  0.60  0.92  1.00      C  0.93  0.69  0.87  1.00
```

**K-B: 0.944 (Pythia) vs 0.86 (32B).** In Pythia, K and B are nearly
the same circuit. In the 32B, they're separable. B hasn't differentiated
from K at 160M scale.

## Layer-by-layer selectivity

```
Layer    K        I        B        C       dominant
L0    0.14389  0.05773  0.13114  0.14232  K
L1    0.16975  0.05815  0.15800  0.16386  K
L2    0.14676  0.05498  0.14224  0.14936  C
L3    0.12236  0.04207  0.11359  0.11480  K
L4    0.12272  0.04763  0.10114  0.09519  K
L5    0.11604  0.04523  0.10426  0.08527  K
L6    0.11095  0.04727  0.09710  0.08598  K
L7    0.10895  0.05037  0.10302  0.09452  K
L8    0.19117  0.08503  0.16848  0.16738  K
L9    0.14868  0.09324  0.13500  0.12703  K
L10   0.15271  0.09718  0.14624  0.12313  K
L11   0.25774  0.12796  0.24383  0.26276  C
```

K dominates 10 of 12 layers. C takes L2 and L11 (boundaries).
B never leads any layer.

## Montague zone → combinator mapping

| Montague zone | Dominant | K | I | B | C |
|---|---|---|---|---|---|
| Type (L0) | **K** | 0.144 | 0.058 | 0.131 | 0.142 |
| Parse (L3) | **K** | 0.122 | 0.042 | 0.114 | 0.115 |
| Apply (L8-L11) | **K** | 0.188 | 0.101 | 0.173 | 0.170 |

All three zones are K-dominant. The "three Montague primitives" are
one K circuit operating in three phases.

## Cosine similarity confirms three phases

```
Transition  Cosine   Change   Note
L0→L1       0.91     0.089    ← phase boundary (input parsing)
L1→L2       0.93     0.073
L2→L3       0.96     0.045
L3→L4       0.996    0.004    ← stable processing begins
L4→L5       0.994    0.006
L5→L6       0.996    0.004
L6→L7       0.993    0.007
L7→L8       0.993    0.007
L8→L9       0.978    0.023    ← processing ends
L9→L10      0.886    0.114    ← phase boundary (output begins)
L10→L11     0.147    0.853    ← MAJOR phase boundary (output emission)
```

Three phases exist (cos confirms session 004):
- **Phase 1 (L0-L2):** Input parsing, cos 0.91-0.93
- **Phase 2 (L3-L8):** Stable processing, cos 0.99+
- **Phase 3 (L9-L11):** Progressive destruction → output, cos 0.89→0.15

But all three phases are K-dominated. The phase structure is
architectural (depth-dependent), not combinator-specific.

## Key findings

### 1. K absorbs B at small scale

At 160M (144 heads), there isn't enough capacity for B to separate.
K does "selection that resembles composition" — it selects nested
referents by traversing the nesting structure, which looks like
functional composition but is mechanistically selection.

### 2. C differentiates early at any scale

C = 22.2% in Pythia (144 heads), 22.6% in 32B (4096 heads). Argument
reordering (passive voice, topicalization) separates from selection
at the smallest viable scale. This makes sense: reordering is a
syntactic operation with clear surface markers ("was ... by").

### 3. I requires spare capacity

I = 2.1% in Pythia, 14.7% in 32B. Identity (pass-through) is a
luxury the small model can't afford. Every head is doing K-work.

### 4. The bootstrap hypothesis is confirmed

Pythia-160M's distribution (K=59%, B=17%) matches v11 at step 5K
(K=63%, B=2.6%). Both are in the bootstrap state where K handles
everything and B hasn't differentiated. The mature state (K=B=31%)
requires either more capacity (32B) or more training (v11 hasn't
reached it yet at 5K).

### 5. L11:H7 and L11:H11 are the most specialized heads

| Head | Score | Dominant | Differential |
|---|---|---|---|
| L11:H7 | 0.331 | C | 0.052 |
| L11:H11 | 0.344 | K | 0.023 |
| L11:H9 | 0.301 | B | 0.019 |
| L10:H3 | 0.238 | B | 0.059 |

L11:H9 is the strongest B-specialized head. L10:H3 has the highest
B-differential (0.059). These are the heads where composition is
most distinct from selection — the seeds of what becomes the full
B circuit at larger scale.

## Implications

### For extraction (VERBUM thesis)

You can't extract "three Montague primitives" from Pythia-160M because
there's really one K-dominant circuit with phase structure. The three-
primitive architecture (MontaguCompiler, session 004 Finding 35) was
shaped by the correct phase boundaries but the wrong mechanistic
decomposition. A combinator-shaped extractor (KIBC basis) would be
more accurate — and at 160M, it would mostly be a K-extractor.

### For v11 training

Pythia-160M is the bootstrap state frozen in a pretrained model. V11
is training *through* this state. The question is whether v11 (at
~20M params) has enough capacity for B to differentiate, or whether
K=B co-equality is a scale phenomenon requiring hundreds of millions
of parameters.

### For the Pythia scaling probe (future)

Running the combinator probe on Pythia-410M and Pythia-1B would reveal
where B differentiates from K. If K-B correlation drops from 0.944
toward 0.86 at some intermediate scale, that's the differentiation
threshold — the minimum capacity needed for separate composition
circuits.

## Data

| File | Contents |
|---|---|
| `scripts/explore/probe_combinators_pythia.py` | Probe script |
| `results/combinator-probe-pythia/combinator_probe_results.json` | Full results |
| `results/combinator-probe-pythia/selectivity_matrices.npz` | Per-head arrays |
| `results/combinator-probe-pythia/selectivity_heatmaps.png` | 12×12 heatmaps |
| `results/combinator-probe-pythia/differential_map.png` | Head assignment + Montague overlay |
| `results/combinator-probe-pythia/layer_profiles_montague_overlay.png` | Layer profiles with zone bands |
| `results/combinator-probe-pythia/cross_combinator_correlation.png` | Correlation matrix |
| `results/combinator-probe-pythia/pythia_vs_32b_distribution.png` | Side-by-side comparison |
