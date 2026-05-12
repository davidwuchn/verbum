---
title: "KIBC Combinator Validation in Qwen3-32B"
status: active
category: experiment-results
tags: [combinators, KIBC, Qwen3-32B, probes, v11, architecture-validation]
related:
  - v11-kibc-architecture.md
  - v11-design.md
  - session-001-findings.md
  - session-062-probes.md
depends-on: []
created: session 080
---

# KIBC Combinator Validation in Qwen3-32B

> Two probes on Qwen3-32B (64 layers × 64 heads = 4096 heads) validate
> that {K, I, B, C} is the natural combinator basis of attention.
> Extended probes show W≡C, S≡B, and binding as a partially distinct
> downstream operation. Three circuits, not eight.

## Probe 1: Basic KIBC (session 080)

**Method:** For each combinator, designed 6 matched sentence pairs where
only the combinator function differs between active and control. Measured
per-head attention selectivity (L2 distance of attention patterns) between
active/control and active/null conditions across all 4096 heads.

**Script:** `scripts/explore/probe_combinators.py`

### Head assignment

| Combinator | Dominant heads | Share | Role |
|-----------|---------------|-------|------|
| K (select) | 1,284 | 31.3% | Pick relevant, discard irrelevant |
| B (compose) | 1,282 | 31.3% | Chain operations, nested clauses |
| C (flip) | 927 | 22.6% | Reorder arguments, passive voice |
| I (identity) | 603 | 14.7% | Pass through unchanged |

**K and B are co-equal.** This is the headline: composition has equal
representation to selection in the mature model.

### Cross-combinator correlation

```
        K      I      B      C
  K   1.00   0.71   0.86   0.93
  I   0.71   1.00   0.75   0.69
  B   0.86   0.75   1.00   0.87
  C   0.93   0.69   0.87   1.00
```

- K-C = 0.93: selection and reordering share nearly the same circuit
- B is somewhat independent (0.86 with K, 0.87 with C)
- I is most distinct (0.69-0.75 with everything)

### Layer profiles

| Combinator | Peak layers | Interpretation |
|-----------|------------|---------------|
| K | L1, L3, L6 | Early — input parsing |
| C | L0, L1, L5 | Very early — syntactic reordering |
| B | L3, L9, L17 | Early-to-mid — progressive composition |
| I | L6, L9, L36, L41 | Distributed — pass-through at any depth |

### Session 001 circuit mapping

The 3-head compiler circuit from 4B (session 001), mapped to 32B:

| 4B head | Role | 32B position | Dominant combinator |
|---------|------|-------------|-------------------|
| L1:H0 | Gate recognizer | L2:H0 | **B** (composition) |
| L24:H0 | Universal compositor | L43:H0 | **C** (flip) |
| L24:H2 | Recursion head | L43:H2 | **B** (composition) |

The compiler circuit is {B, C, B} — composition and reordering.

## Probe 2: Extended Combinators (session 080)

**Method:** Same technique, probing for W (duplicate), S (distribute),
variable binding, and abstraction. Cross-correlated with KIBC results.

**Script:** `scripts/explore/probe_combinators_extended.py`

### Extended selectivity

| Combinator | Mean | Max | Peak layer |
|-----------|------|-----|-----------|
| W (duplicate) | 0.073 | 0.277 | L1 |
| S (distribute) | 0.071 | 0.262 | L1 |
| bind (variable) | 0.043 | 0.190 | **L21** |
| abstract | 0.061 | 0.258 | L1 |

### Cross-correlation: KIBC + extended

```
             K      I      B      C      W      S    bind  abstr
     K     1.00   0.71   0.86   0.93   0.90   0.85   0.76   0.87
     I     0.71   1.00   0.75   0.69   0.69   0.76   0.74   0.68
     B     0.86   0.75   1.00   0.87   0.84   0.88   0.83   0.80
     C     0.93   0.69   0.87   1.00   0.92   0.83   0.78   0.87
     W     0.90   0.69   0.84   0.92   1.00   0.82   0.76   0.85
     S     0.85   0.76   0.88   0.83   0.82   1.00   0.77   0.79
  bind     0.76   0.74   0.83   0.78   0.76   0.77   1.00   0.72
  abstr    0.87   0.68   0.80   0.87   0.85   0.79   0.72   1.00
```

### Three circuits emerge

```
Circuit 1 — Routing:    K ≈ C ≈ W ≈ abstract    (r=0.87-0.93)
Circuit 2 — Composition: B ≈ S                   (r=0.88)
Circuit 3 — Identity:    I                        (r=0.68-0.76)
Outlier   — Binding:     bind                     (r=0.72-0.83)
```

**W ≡ C** (r=0.92): Duplication ("he saw himself") uses the same heads
as reordering ("the fish was eaten by the cat"). Both are argument routing.

**S ≡ B** (r=0.88): Distribution ("who studies hard and asks questions")
uses the composition circuit. S = B∘K∘C in the residual stream.

**bind is partially distinct** (max r=0.83 with B): Variable binding
lives at L21-L39, while everything else peaks at L0-L15. Binding is a
downstream consumer of the KIBC circuits.

## Implications for v11

### KIBC is the correct basis
W and S don't need separate combinators — they're handled by C and B
respectively. The four combinators capture the actual circuit topology.

### The training gap is expected
- 32B target: K=31%, B=31% (co-equal)
- v11 at 5K: K=63%, B=1.8% (bootstrap in progress)
- B-type rising in integrate (47.6%) = pressure building
- K-C co-occurrence shift at step 4K = model finding the K≈C topology

### Binding maps to CycleContinue
The mid-to-late layer profile of binding (L21-L39) maps to the
descending arm cycle semantics:
- Cycle 0 (early): IDENTIFY — K/C routing
- Cycle 1 (mid): RESOLVE — B/S composition
- Cycle 2 (late): PRODUCE — variable binding

CycleContinue should learn to stay open for binding-heavy inputs.
This is why CycleContinue hasn't opened yet at 5K — the model is
still in K-dominant territory with no binding pressure.

### {B,C,K,I} is NOT Turing-complete, but the model doesn't need it to be
Pure {B,C,K,I} can only express linear functions (each argument used
at most once). The model achieves duplication through the C circuit
(W≡C, r=0.92) and distribution through the B circuit (S≡B, r=0.88).
The residual stream provides the duplication substrate — the same
token representation is available at every layer, enabling the "use
twice" operation without a dedicated W combinator.

## Data

| File | Contents |
|------|----------|
| `results/combinator-probe/combinator_probe_results.json` | KIBC summary |
| `results/combinator-probe/selectivity_matrices.npz` | Per-head arrays |
| `results/combinator-probe/*.png` | 4 visualizations |
| `results/combinator-probe-extended/extended_probe_results.json` | Extended summary |
| `results/combinator-probe-extended/extended_matrices.npz` | Per-head arrays |
| `results/combinator-probe-extended/*.png` | 3 visualizations |
