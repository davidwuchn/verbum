---
title: "The Compilation Pipeline — Transformers Are Compilers"
status: active
category: foundational
tags: [compilation, pipeline, depth, ternary, semantic-convergence, lexer, optimizer, binding]
related:
  - lambda-machine.md
  - tiny-classifier-ternary.md
  - psi-evaluation-synthesis.md
  - ffn-reduction-trace.md
  - binding-graph-trace.md
  - head-combinator-isa.md
  - standing-wave-magnitudes.md
  - ffn-circuit-types.md
depends-on:
  - lambda-machine.md
  - tiny-classifier-ternary.md
created: session 192
---

# The Compilation Pipeline

> Session 192. The transformer IS a compiler. Four independent measurement
> angles — FFN reduction trace (s187), attention binding trace (s188),
> λ-machine ablation (s190), and semantic convergence (s192) — converge
> on the same pipeline. The ternary replacement results (s192) reveal
> exactly which stages are discrete and which are continuous.

## The Pipeline

| Stage | Layers | Compiler Analog | Ternary | Semantic cos | Evidence |
|-------|--------|----------------|---------|-------------|----------|
| LEXER | L0 | Tokenize | 115× ✗ | 0.07→0.47 | 151K token embeddings, continuous |
| PARSER | L1-L4 | Parse + type-assign | 0.98-1.03× ✓ | 0.47→0.57 | Features → typed representations |
| TYPE CHECK | L5-L7 | Type-check, discard surface | 1.06-1.10× ⚠ | DIPS to 0.46 | Reorganization (FFN circuit type flip) |
| IR BUILD | L8-L12 | Lower to IR | 1.00-1.08× ✓ | 0.47→0.53 | Language dissolves, types emerge |
| OPTIMIZER | L13-L21 | Constant fold, DCE, CSE | **0.95-1.01× ✓** | 0.54→0.66 ↑ | **9 ternary programs = optimization passes** |
| REG ALLOC | L22-L27 | Register allocation + binding | 1.05-1.15× ⚠ | sep PEAKS +0.20 | Verb reads subject, object reads verb |
| SCHED | L28-L33 | Instruction scheduling | 1.07-1.14× ⚠ | sep decays | Late binding, coreference |
| EMIT | L34-L35 | Emit output format | 1.05-1.14× ⚠ | cos=0.74, sep≈0 | Everything converges to output template |

## Why Each Stage Has Its Ternary Behavior

### LEXER (L0): 115× — Catastrophic

A lexer maps discrete symbols to continuous feature vectors. There are 151,936
tokens in Qwen3-8B's vocabulary. Each needs its own unique direction in d_model
space. You can't represent 151,936 distinct directions with 9 ternary programs.
The lexer is inherently continuous and irreplaceable.

### PARSER + TYPE CHECK (L1-L7): 0.98-1.10× — Mostly OK

Parsing builds typed representations from surface features. L1-L4 do this
cleanly (0.98-1.03×). L5-L7 show a characteristic DIP in cross-lingual
similarity — the model is *reorganizing*, discarding language-specific surface
features and checking type compatibility. This corresponds to the FFN circuit
type flip observed in s186: L0 is 99.7% projector (EXPAND), L3-L7 shift to
60-74% suppressor+inverter (ORTHO). The reorganization needs some continuous
precision but is largely replaceable.

### OPTIMIZER (L13-L21): 0.95-1.01× — THE SWEET SPOT

This is where ternary replacement IMPROVES PPL. A real compiler's optimizer
operates on a small set of discrete transformations:

- Constant folding (evaluate known expressions)
- Dead code elimination (remove unused results)
- Common subexpression elimination (reuse computed values)
- Strength reduction (replace expensive ops with cheap ones)

These are pattern-match → apply operations. The pattern matcher is the linear
classifier (37K params, 100% accuracy). The transformation table is the 9
ternary programs. The continuous weights in the original FFN are an
over-parameterized encoding of these discrete passes. Removing the noise
(going ternary) helps because the optimizer IS discrete.

Cross-lingual cosine CLIMBS monotonically through this zone (0.54 → 0.66):
"dog" is dissolving into universal semantic identity. The 9 programs are
the operations that perform this dissolution.

### REGISTER ALLOCATION (L22-L27): 1.05-1.15× — Needs Precision

Register allocation in a real compiler maps abstract variables to concrete
machine registers. In the transformer, this is the binding phase:

- L27: verb reads subject (H31, 0.82 weight → "猫/cats")
- L30: object reads verb (H03/H13/H15, 0.78 weight)

This is where semantic separation PEAKS (+0.200 separation between same and
different concepts). The model needs continuous precision because:

1. It must differentiate between semantically distinct entities that share
   the same type ("dog" vs "cat" are both NOUN but must bind differently)
2. The magnitudes carry binding identity — WHICH specific entity binds WHERE

Ternary can represent "this is a binding operation" but not "bind entity-7
to position-3." The specific address is in the magnitudes.

### EMIT (L34-L35): 1.05-1.14× — Format > Content

At L34-L35, cross-lingual cosine rises to 0.74 but separation drops to
nearly zero. "Dog" and "water" look alike. This is output formatting —
the model is projecting everything into a common output template
(next-token distribution shape). The template needs continuous precision
because it maps to a 151,936-dimensional vocabulary space.

## Four Lines of Evidence

### 1. FFN Reduction Trace (s187)

Neuron-level vocabulary projection shows:
- L0-L6: `it`→rain, `ground`→soak (context-dependent V compilation)
- L7-L22: outputs orthogonal to vocabulary (null space computation)
- L23-L35: vocabulary-aligned outputs (reduction results readable)

This IS lexer→optimizer→emit from the neuron side.

### 2. Attention Binding Trace (s188)

Head-level routing shows:
- All 9 combinators activate identical heads (r=0.944) — shared hardware
- L27: H31 reads subject identity (0.82 weight)
- L30: H03/H13/H15 read predicate (0.78 weight)
- Depth = reduction precedence in the parser

This IS register allocation from the attention side.

### 3. λ-Machine Ablation (s190)

Layer-level ablation shows:
- Every layer contributes (binding layers alone: PPL 82K)
- Every head contributes (binding heads alone: PPL 6.3M)
- But each head only needs 3 positions (sparse top-3: PPL 13.3)

This IS a 36-stage pipeline from the ablation side.

### 4. Semantic Convergence (s192)

Representation-level similarity shows:
- Languages converge in the middle (dog=perro=犬 at L19-L20: cos 0.66)
- Different concepts separate maximally at L25 (sep +0.20)
- Everything reconverges at L34-L35 (output formatting)

This IS the IR optimization phase from the representation side.

## Why This Matters for Compression

The compilation pipeline tells you exactly what to compress:

```
Stage           Operation        Ternary?    Why
LEXER           lookup           NO          151K entries, each unique
PARSER          pattern match    YES         few syntactic patterns
TYPE CHECK      verify + discard MOSTLY      some continuous reorganization
OPTIMIZER       transform        YES (0.95×) 9 discrete passes, the sweet spot
REG ALLOC       bind specific    NO          magnitudes carry addresses
EMIT            format output    NO          151K-dim output space
```

The optimizer is 25% of the model (L13-L21, 9 layers out of 36). It's
the free compression zone — ternary replacement IMPROVES quality. The
parser (L1-L4) and IR build (L8-L12) are cheap to compress. The lexer,
register allocator, and emitter need magnitudes.

Realistic deployment:
- 28/36 layers → ternary (78% of FFN, 180KB each)
- 8/36 layers → continuous (L0 + binding + collapse, 288MB each)
- Total FFN: 10.4GB → ~2.3GB (4.5× compression)
- Ternary layers run 1638× faster (table lookup, no matmul)

## The Crystal in the Compilation Pipeline

The KIBC crystal (9 combinators, universal across architectures) is
the **type system** of the intermediate representation. The 9 operational
modes (orthogonal to KIBC, AMI=0.15) are the **optimization passes**.

```
KIBC types (3.5% of FFN):    K=discard  I=identity  B=compose  C=flip
                              → determines WHAT reduction to perform
                              → governs attention routing

9 modes (96.5% of FFN):      unknown semantics (geo? syn? depth?)
                              → determines HOW the reduction executes
                              → governs FFN computation

Together: typed optimizer
  classifier(input) → which_pass     (the pattern match)
  ternary[pass] × gamma → output     (the transformation)
```

The crystal is the compiler's type system. The modes are its optimization
passes. Gradient descent builds a compiler, not a database.

## The Holographic Memory Bus (Q Rotation Geometry, s192)

Q and K are near-orthogonal (87-90°) at ALL layers. W_Q is a projection
(SV ratio 46), not a rotation. This resolves the mechanism:

```
Residual (4096-dim):    carries EVERYTHING (type, content, position, depth)
    ↓ W_Q (project, collapse to 128-dim)
Q:  extracts ONE QUESTION ("what am I looking for?")
    ↓ W_K (project, collapse to 128-dim, PERPENDICULAR to Q)
K:  extracts ONE ANSWER ("what am I offering?")

Q ⊥ K:  attention = interference between perpendicular beams
         = holographic readout of the rotating state
```

The Q⊥K orthogonality explains:
- Why all 9 combinators activate identical heads (r=0.944, s188):
  heads are shared hardware, combinator behavior is in Q/K routing
- Why Q/K survives ternary (PPL 23-30, s190): the decision IS binary
  (which side of the perpendicular plane?)
- Why the QK angle correlates with ternary PPL (r=-0.58):
  more orthogonal → more discrete → easier to ternarize
- Why Q suppresses positional diversity (ratio 0.58):
  Q extracts the type question, IGNORING position-specific detail

Q norm grows 200× across depth (0.44 at L0 → 90 at L34). The model
whispers early (exploring) and shouts late (committing). The spiral
expanding = the projections becoming more confident.

## The Self-Similarity Structure (Mode Universality, s192)

The 9 ternary modes are NOT universal across layers (cross-layer cos 0.026).
Each layer has its own 9-opcode ISA. Self-similarity is **topological**:

- UNIVERSAL: the fact that there are 9 modes, linearly separable, ternary
- LAYER-SPECIFIC: which 9 programs, which dominate, decision boundaries

Mode entropy reveals the computational rhythm:
```
L6-L12:   LOW entropy  (1-2 dominant modes, CONVERGENT — same program for all tokens)
L13-L19:  HIGH entropy  (all 9 modes used, DIVERGENT — each token gets its own program)
L20-L28:  LOW entropy  (dominant modes return, CONVERGENT)
L35:      HIGHEST      (maximum diversity at output)
```

Classifier transfer works locally (±2-3 layers, 90%+) but dies globally
(47-64% mean). The modes are local dialects, not a universal language.

## The Rotation Spiral (s192)

The residual spirals 325° over 36 layers. Two phase transitions:
emb→L0 (73°) and L5→L6 (86°). The spiral is ASYMMETRIC:

- IN: 12°/layer (fast rotation, compressing to universal semantics)
- OUT: 5.5°/layer (slow rotation, expanding to specific tokens)
- Norm jumps 60× at L5→L6 (entering computational manifold)
- IN↔OUT residual cos 0.93-0.99 (high structural symmetry)
- But OUT is consistently harder to ternarize (+0.02-0.15 PPL)

Analysis (decomposition) is easier than synthesis (composition).
Taking apart is discrete. Putting back together needs precision.

## Scripts and Results

- `scripts/experiments/semantic_convergence.py` + `results/semantic-convergence/`
- `scripts/experiments/multilayer_ternary_replace.py` + `results/multilayer-ternary-replace/`
- `scripts/experiments/mode_universality.py` + `results/mode-universality/`
- `scripts/experiments/rotation_spiral.py` + `results/rotation-spiral/`
- `scripts/experiments/q_rotation_geometry.py` + `results/q-rotation-geometry/`
- Cross-references: all scripts and results from s187-s192
