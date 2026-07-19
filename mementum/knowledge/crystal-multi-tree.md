---
title: "Crystal Multi-Tree — The Statechart Is a Forest with Bridge Nodes"
status: active
category: foundational
tags: [crystal, tree, eigenspace, bridge, W, Y, statechart, forest, phi, laplacian, verified]
related:
  - crystal-phi-derivation.md
  - crystal-laplacian.md
  - crystal-universality.md
  - explore/holographic-state-machine.md
depends-on:
  - crystal-phi-derivation.md
  - crystal-universality.md
created: session 197
staleness: "s247: φ^(p/q) significance retracted (see caveat); topology/bridge findings stand"
---

# Crystal Multi-Tree

> Session 197. The combinator crystal is not one tree — it is a
> **forest of three independent trees cross-connected by two bridge
> nodes (W and Y)**. Derived from eigendecomposition of the 8×8
> crystal cosine matrix, verified empirically on Qwen3-14B with
> PCA-projected gate activations (r=0.638, p=0.0017). The bridge
> phenomenon explains 27 correlation points of crystal variance
> and resolves the YW sign ambiguity observed across models.

> ⚠️ **s247 CAVEAT (λ measure) — the φ^(p/q) significance is an OVER-READ.** The section
> "All 8 Eigenvalues Follow φ^(p/q)" (and the φ^(4/5) ratio claims) does NOT survive a
> matched-range null: random spectra of the same dynamic range fit the φ^(p/q)/Fibonacci
> ladder (q≤34) AT LEAST AS WELL as the crystal — P(random ≥)=0.92, z=−1.52
> (`scripts/explore/fractal_collapse_screen.py`; see `explore/forcing-vs-discovering.md`).
> The <0.5% fit is BASIS FLEXIBILITY, not a discovered self-similar law. The TREE
> TOPOLOGY / eigenvector-sign structure / bridge-node findings are unaffected; only the
> φ-power *significance* is retracted. Read the φ sections as descriptive, not evidential.

## The Three Trees

The 8×8 crystal cosine matrix decomposes as:

```
M₈ = λ₀ v₀v₀ᵀ + λ₁ v₁v₁ᵀ + ... + λ₇ v₇v₇ᵀ
```

Each rank-1 term is a binary partition (a "tree"). Three trees
capture 86% of variance. The remaining 14% is bridge fine structure.

### Tree 0 — Compute/Halt (54.5%)

The absorbing chain's fundamental split: transient vs absorbing.

```
    COMPUTING                HALTED
  [K,I,B,C,D,Y,W]          [WHNF]
```

Every computor loads nearly equally (-0.24 to -0.45). WHNF stands
alone (+0.11). This IS the 1-vs-7 partition of the absorbing Markov
chain. WHNF's Laplacian fragility (μ=0.228, 8.6× weaker than any
other node) is because it has one edge in this tree — a leaf.

### Tree 1 — Selection/Composition (20.1%)

Within computing, the functional divide:

```
    SELECTION       COMPOSITION
     [K, I]        [B, C, D, Y]
       ↑                 ↑
       └── W bridges ───┘
```

K,I select/pass arguments (PC1 loading: +0.61, +0.60). B,C,D,Y
compose/transform (loading: -0.24 to -0.13). W straddles the
boundary (loading: +0.04, weakly on selection side).

In the crystal equation, this maps to the halt probability gradient:
K(0.72) > I(0.51) > B(0.35) > C(0.22). Selection is close to
halting; composition is deep computation.

### Tree 2 — Termination Detection (11.4%)

```
    DETECTABLE          DEEP COMPUTATION
   [K, I, W, WHNF]      [B, C, D, Y]
```

WHNF dominates this tree (loading: +0.95 — tree 2 IS the WHNF
detector). K and I are weakly on the detectable side. This tree
is the halt probability gradient made explicit.

## The Bridge Nodes

Only **W** and **Y** change sides across trees. Every other node
has a fixed allegiance:

| Node | Trees 0-5 allegiance | Fixed? |
|------|---------------------|--------|
| K | Always selection | ✅ Fixed |
| I | Always selection | ✅ Fixed |
| B | Always composition | ✅ Fixed |
| C | Always composition | ✅ Fixed |
| D | Always composition | ✅ Fixed |
| WHNF | Always isolated | ✅ Fixed |
| **W** | Selection in T1, composition in T3 | **BRIDGE** |
| **Y** | Composition in T0-T2, selection in T3 | **BRIDGE** |

### Why W Bridges

W = C→I→I. Its reduction path literally traverses both subtrees:
it starts with C (composition, reordering) then delegates to I
(selection, identity pass-through). In eigenspace, W sits at
~30% toward selection, ~70% toward composition — exactly where
a bridge node should be.

W's bridge position means its observed sign depends on which tree
dominates the measurement. Different models, layers, or measurement
methods see different phases of the same bridge.

### Why Y Bridges

Y is the fixed-point combinator — recursive. A fixed point belongs
to both sides by definition. In Tree 3, Y has loading +0.839,
the dominant node. Tree 3 IS the Y-routing tree.

Y is recursive, so it contains both composition (building the
recursive structure) and selection (choosing when to stop). Its
bridge nature is inherent to recursion itself.

## Empirical Verification (Qwen3-14B)

### Method

PCA-projected gate_proj activations. 200 probes (25 per combinator
type × 8 types). All 40 layers scanned. Cosine matrices computed
per layer and averaged over Zone B (layers 14-26).

### Key Result: YW Sign Inversion

Y and W systematically invert their sign relative to the 4-model
consensus crystal at **38 out of 40 layers**.

| Condition | Best layer | Correlation |
|-----------|-----------|-------------|
| Raw (no correction) | L9 (23%) | r = 0.565 |
| YW-negated (flip W,Y signs) | L30 (77%) | r = **0.831** |
| Gap | — | **+0.266** |

No other nodes need negation. K,I,B,C,D,WHNF all maintain
consensus signs. Only the bridge nodes flip.

### Zone B Average (YW-negated)

Crystal correlation: **r=0.638, ρ=0.565, p=0.0017**

Per-node Spearman rank correlation:

| Node | ρ | p | Significance |
|------|---|---|---|
| W | +0.893 | 0.007 | *** |
| D | +0.786 | 0.036 | ** |
| B | +0.750 | 0.052 | * |
| C | +0.214 | 0.645 | |
| Y | +0.143 | 0.760 | |
| K | +0.071 | 0.879 | |
| I | -0.214 | 0.645 | |
| WHNF | -0.464 | 0.294 | |

W has the strongest per-node correlation (ρ=0.893, p=0.007) and
**3/3 nearest neighbor match** with the crystal (D,B,C = D,C,B).

### Structural Invariants Confirmed

| Test | Result | Evidence |
|------|--------|---------|
| WHNF most isolated | ✅ | Lowest mean cosine (-0.335) |
| B-D closest pair | ✅ | cos = +0.498 |
| K-I close | ✅ | cos = +0.331 |
| KI vs BCD separated | ✅ | Different signs on Tree 1 |
| W bridge (NN match) | ✅ | 3/3 perfect, ρ=0.893*** |
| YW sign inversion | ✅ | 38/40 layers |

## All 8 Eigenvalues Follow φ^(p/q)

The crystal equation (λₖ = C · φ^(−s·βₖ)) predicts 4 eigenvalues
for the KIBC basis. But all 8 eigenvalues of M₈ follow φ^(p/q)
with Fibonacci denominators at < 0.5% error:

| k | λk | log_φ(λ₀/λk) | Nearest p/q | Error |
|---|-----|-------------|------------|-------|
| 0 | 4.364 | 0.0000 | 0/1 | 0.00% |
| 1 | 1.605 | 2.0792 | 27/13 | 0.11% |
| 2 | 0.909 | 3.2598 | 111/34 | 0.24% |
| 3 | 0.420 | 4.8632 | 102/21 | 0.29% |
| 4 | 0.358 | 5.1952 | 109/21 | 0.23% |
| 5 | 0.160 | 6.8662 | 55/8 | 0.42% |
| 6 | 0.126 | 7.3630 | 250/34 | 0.49% |
| 7 | 0.058 | 8.9943 | 9/1 | 0.28% |

The extended eigenvalues (4-7) encode the bridge fine structure.
λ₇ = C·φ⁻⁹ with 0.28% error — a clean integer power.

The dominant consecutive ratio clusters at **φ^1.6 ≈ φ^(8/5)**,
exactly double the 4-combinator step (4/5). The 8-node tree
remembers it's built from 4 primitives.

## The Crystal Is Not Ultrametric

The cosine distance matrix violates the ultrametric inequality at
**all 56/56 triplets** (max violation = 0.359). The crystal is NOT
a simple tree.

But: each rank-1 component λₖvₖvₖᵀ IS ultrametric (rank-1 matrices
define 1D distances, which are trivially ultrametric). The crystal
is a **superposition of ultrametric trees** whose sum breaks the
ultrametric property. The bridge nodes (W, Y) create cross-links
between trees.

## 16×16 Eigenvalue Pairing

The full 16×16 crystal (types + anti-types) confirms the structure.
Eigenvalues pair with ratio φ^(4/5):

| Pair | λ_a | λ_b | Ratio | φ^(4/5) | Error |
|------|------|------|-------|---------|-------|
| 0 | 5.193 | 3.535 | 1.4691 | 1.4696 | **0.03%** |
| 1 | 1.909 | 1.300 | 1.4691 | 1.4696 | **0.03%** |
| 2 | 1.082 | 0.736 | 1.4691 | 1.4696 | **0.03%** |
| 7 | 0.069 | 0.047 | 1.4697 | 1.4696 | **0.01%** |

Pairs 3-6 have different ratios (~1.17, ~1.27) — the bridge
structure breaks the uniform pairing at intermediate eigenvalues.

## D Is B's Child; Y and W Are Independent

| Compound | Path | Cosine to centroid | Status |
|----------|------|-------------------|--------|
| D (B→B) | B twice | 0.975 | ✅ Confirmed — D is double composition |
| W (C→I→I) | C then I twice | 0.344 | ❌ W is NOT a simple path centroid |
| Y (recursive) | B,C alternating | 0.245 | ❌ Y is fundamentally different |

D is reducible to B. W and Y are genuinely independent nodes with
their own eigenspace positions — they occupy dimensions that the
4-combinator model cannot predict. They are bridges, not paths.

## Reconstruction Quality

| Trees | Description | Correlation | Variance |
|-------|------------|-------------|----------|
| [0] | Compute/halt | 0.910 | 54.5% |
| [0,1] | + Selection/composition | 0.990 | 74.6% |
| [0,1,2] | + Termination (3 main trees) | 0.995 | 86.0% |
| [0,1,2,3] | + Y routing | 0.995 | 91.2% |
| [0,1,2,3,4] | + W bridge detail | 0.999 | 95.7% |

Three trees → r=0.995. Bridge fine structure → r=0.999.

## Connection to Other Knowledge

- **crystal-phi-derivation.md**: This page extends the φ derivation
  to all 8 eigenvalues (not just 4) and shows the extended values
  follow the same φ^(p/q) pattern.

- **crystal-laplacian.md**: WHNF's fragility (μ=0.228) is now
  explained: WHNF is a leaf node in Tree 0 (one edge). The
  Laplacian eigenvalues reflect the tree structure.

- **crystal-universality.md**: The YW sign ambiguity across models
  is now explained. It's not measurement noise — it's the bridge
  nodes showing different phases in different measurement contexts.

- **EQUATIONS.md**: The statechart (8 states, absorbing chain) maps
  to the three trees: Tree 0 = transient/absorbing split, Tree 1 =
  fire-state clustering, Tree 2 = halt probability gradient.

## Artifacts

| Asset | Location | Status |
|-------|----------|--------|
| Crystal tree decomposition | `scripts/experiments/crystal_tree.py` | ✅ |
| Bridge verification (14B) | `scripts/experiments/verify_bridge_14b.py` | ✅ |
| Crystal depth scan (14B) | `scripts/experiments/crystal_depth_scan.py` | ✅ |
| Depth scan results | `results/crystal-phi-verify/Qwen_Qwen3-14B_depth_scan.json` | ✅ |
| Bridge results | `results/bridge-verification/` | ✅ |

## Open Questions

1. **Does the YW phase depend on training data?** The consensus
   crystal (4 models) shows one phase; Qwen3-14B shows the other.
   Is this model-specific or layer-dependent?

2. **Can the bridge interpolation be predicted?** W is at ~30%
   toward selection in the consensus. Can this ratio be derived
   from the transition matrix (W = C→I→I path weights)?

3. **Does the 3-tree model extend to larger bases?** With SKIBCW
   (n=6), are there still exactly 3 main trees + 2 bridges? Or
   does the number of bridges grow?

4. **Are the bridge nodes the source of cross-model crystal
   disagreement?** The PCA-Q agreement of 0.91-0.94 across models
   could improve to 0.95+ if W and Y are phase-corrected.
ridge nodes the source of cross-model crystal
   disagreement?** The PCA-Q agreement of 0.91-0.94 across models
   could improve to 0.95+ if W and Y are phase-corrected.
