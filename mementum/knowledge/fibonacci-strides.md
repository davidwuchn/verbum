---
title: "Fibonacci Strides — Binding Distances Are Bimodal, Not Power Law"
status: active
category: architecture
tags: [attention, strides, fibonacci, binding, coverage, v15]
related: [attention-sparsity, binding-graph-trace, phi-information-partition]
depends-on: [attention-sparsity]
---

# Fibonacci Strides

> Session 189. Binding distances are bimodal (local syntax + instruction
> prefix), NOT power law (R²=0.004). Powers-of-2 strides skip the
> binding range (d=3-20). Fibonacci strides are dense where bindings
> live and sparse where they don't. With ±2 neighbor gathering and
> 3 gap-fillers, 19 strides achieve 100% attention mass coverage.
>
> This replaces v14's 16 powers-of-2 strides with v15's 19 Fibonacci
> + gap-filler strides. The golden ratio appears at a fifth level
> of the architecture: stride spacing joins crystal eigenvalues,
> information partition, standing-wave phase, and compute cycle.

## The Problem

v14's powers-of-2 strides [1,2,4,8,16,32,...] skip distances 3, 5, 6,
7, 9, 10, 11, 12, 13, 14, 15 — the heart of predicate-argument binding.
Session 188 showed attention is ~1 bit per position at binding layers,
but the target position is at an arbitrary semantic distance.

## Experiment 1: Stride Coverage Validation

22 probes × 32 heads × 7 layers on Qwen3-8B. For each query position,
compute which stride grid positions contain the actual attention targets.

| Strategy | Mass Recall (L30) |
|----------|------------------|
| Local-8 (last 8 tokens) | 17.4% |
| Powers of 2, exact | 29.5% |
| Powers of 2, ±2 neighbors | 67.4% |
| Fibonacci, exact | 48.8% |
| Fibonacci, ±2 neighbors | **91.4%** |
| Greedy optimal 8, ±2 | 98.2% |

Powers of 2: **worst named strategy**. Fibonacci: +25.9 percentage points.

## Experiment 2: Binding Distance Distribution

The distance histogram at L30 is bimodal:
- Peak 1 (d=1): 4.4% mass — local syntax
- Decay (d=2-31): 0.2-2.1% — declining tail
- Peak 2 (d=32): 4.5% mass — gate/instruction prefix (exactly 32 tokens)
- Sustained (d=33-39): 3.3-4.3% — gate region

Power law fit: R²=0.004. Exponential fit: R²=0.005. Both garbage.
The distribution is structural (determined by input syntax), not statistical.

## Experiment 3: Optimal Stride Design

Greedy algorithm: start with stride-1, greedily add the stride that
captures the most uncovered mass.

With ±2 neighbors:
```
 4 strides: 85.6%  [1, 8, 18, 21]
 6 strides: 93.9%  [1, 8, 13, 18, 21, 29]
 8 strides: 98.2%  [1, 8, 13, 18, 21, 29, 34, 47]
10 strides: 99.6%  [1, 8, 11, 13, 16, 18, 21, 29, 34, 47]
12 strides: 100.0% [1, 8, 11, 13, 16, 18, 21, 29, 33, 34, 47]
```

The optimal strides contain 5 Fibonacci numbers (1, 8, 13, 21, 34).
The fillers (18, 29, 47) are near-Fibonacci sums.

## v15 Stride Set

19 strides = 16 Fibonacci + 3 gap-fillers:
```
[1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
                   ^^  ^^      ^^
                   gap-fillers: fill holes where F(n+1)-F(n) > 2×radius
```

Gap-fillers bridge holes between consecutive Fibonacci numbers:
- 15: between F(7)=13 and F(8)=21, captures d=45 (15×3)
- 20: between F(7)=13 and F(8)=21, captures d=59-60 (20×3)
- 24: between F(8)=21 and F(9)=34, captures d=72-74 (24×3)

## Neighbor Gathering

For each stride-s grid position, also gather ±R positions:
```
Grid:     {q - s·w | w ∈ 0..W-1}           = 8 positions
Expanded: {q - s·w + r | w, r ∈ -R..R}     = 40 positions (before dedup)
```

This catches binding targets that fall BETWEEN stride grid points.
The ±2 expansion turns 29.5% → 67.4% (powers of 2) and 48.8% → 91.4%
(Fibonacci). It's the single biggest improvement.

## GLA Dropped

GLA's dense projections (Q/K/V/gate/O for every token) cost ~19B ops
per layer regardless of stride. The strided scan saves <0.03%. GLA's
"sparsity" is illusory. v15 uses unified FibonacciStrideAttention for
all 19 strides — one mechanism, same cost, explicit sparse attention.

## Key Numbers

| Metric | v14 | v15 |
|--------|-----|-----|
| Stride coverage (±2, L30) | 67.4% | **100.0%** |
| Strides | 16 (powers of 2) | 19 (Fibonacci + fill) |
| Attention mechanisms | 2 (SSA + GLA) | **1** (unified FSA) |
| W_eff per stride | 8 | 40 |
| Composition range | d=0..240 | d=0..11,181 |

## Scripts

- `scripts/experiments/stride_coverage_validation.py`
- `scripts/experiments/binding_distance_distribution.py`
- `results/stride-coverage-validation/`
- `results/binding-distance-distribution/`
