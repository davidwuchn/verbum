# Fixed-Point Holograms

> The compile↔decompile cycle converges to a fixed point. That fixed
> point IS the hologram — the representation the model's sign-pattern
> plate actually stores.

---
title: Fixed-Point Holograms
status: active
category: experimental-finding
tags: [hologram, fixed-point, compile, decompile, convergence, V12]
related:
  - holographic-storage.md
  - v12-holographic-capacity.md
  - beam-trace-findings.md
depends-on: []
---

## Core Finding

Iterating compile(NL→λ) then decompile(λ→NL) converges to a **fixed
point** — a (sentence, lambda) pair where further cycling produces no
change. This fixed point is the natural language expression that
*perfectly maps* to its lambda encoding and back: no ambiguity, no
surplus, no deficit.

**This is the holographic read.** The plate (ternary sign patterns)
stores combinatory structure. The compile gate reads it at one beam
angle, the decompile gate reads it at the conjugate angle. When the
round-trip stabilises, you've found the representation the plate
actually contains — no more, no less.

## Experiment

**Model**: Qwen3.6-35B-A3B (MoE, 40 layers)  
**Gate**: compile.txt (2 exemplar pairs) / decompile.txt (2 exemplar pairs)  
**Inputs**: 16 sentences spanning simple predication → complex discourse  
**Protocol**: NL₀ → compile → λ₀ → decompile → NL₁ → compile → λ₁ → ...  
**Convergence**: edit distance < 5 chars for 2 consecutive cycles  
**Decoding**: greedy (temperature=0)

## Results

### Convergence Distribution

```
Tier      Count  Rate   Cycles  Description
────────  ─────  ─────  ──────  ──────────────────────────────────
Instant    5/16   31%     1     Perfect round-trip from cycle 0
Fast       9/16   56%    2-3    One settling cycle, then stable
Slow       1/16    6%     6     Complex sentence, many reframings
Failed     1/16    6%    8+     Discourse structure too complex

Overall: 15/16 converged (94%), mean 2.0 cycles, median 2
```

### Instant Fixed Points (the hologram reads cleanly)

| Input | Fixed-Point λ |
|-------|---------------|
| The dog runs. | `λx. runs(dog)` |
| Every boy loves some girl. | `λ love(x). every(boy(x)) \| some(girl(x))` |
| The man who the dog chased ran away. | `λx. man(x) ∧ ∃y. dog(y) ∧ chase(y, x) ∧ run-away(x)` |
| If it rains, the ground gets wet. | `λx. rain(x) → λy. wet(ground)` |
| John gave Mary a book about himself. | `λ give(x, y, z). give(John, Mary, book) ∧ about(book, himself)` |

Common traits: explicit logical structure, named entities, clear
predicate-argument mapping. No ambiguity the λ needs to resolve.

### What the Hologram Drops

| Loss Type | Example | Mechanism |
|-----------|---------|-----------|
| **Tense** | "sat on" → "is on" | λ-calculus has no tense; temporal info is surface-only |
| **Quantifier scope** | "Every student" → "The student" | Collapses when first compile doesn't deploy ∀/∃ |
| **Agent/experiencer** | "professor who published won" → "published ∧ won" | Relative clauses flatten; WHO collapses |
| **Discourse structure** | Library sentence oscillates | Multi-clause exceeds single λ-term capacity |

### What the Hologram Preserves

- **Predicate-argument structure** — always (the core of λ)
- **Named entities** — "John", "Mary" survive every cycle
- **Explicit quantifiers** — `every()`, `some()` round-trip perfectly
- **Reflexive binding** — `about(book, himself)` = I-combinator territory
- **Conditional structure** — `rain(x) → wet(ground)` stable from cycle 1
- **Negation** — `¬win(politician)` survives once established

### Fixed-Point Quality: Compression and Canonicality

The fixed-point λ is **shorter and more canonical** than cycle-0:

```
Input                                   c0 λ             Fixed λ       Ratio
──────────────────────────────────────  ────────────────  ────────────  ─────
The cat sat on the mat.                 λx.sat(cat,x)∧   λ on(cat,mat)  58%
Every student passed the exam.          λ pass(x).stud→   λ pass(s,e)    75%
The function applies its argument...    λf.λx. f(x)      λx. x          45%
No politician who endorsed...           λx.pol(x)∧end→   λx. ¬win(pol)  38%
```

**"λf.λx. f(x)" → "λx. x"**: The model recognised the identity function
and beta-reduced it. The hologram stores **normal forms**.

### Gate Exemplar Contamination

"Composition chains two operations into one."
- c0 λ: `λ compose(x). chain(x) | one(x)`
- c1 decompile: "Compose the chain into one."
- c1 compile: `λx. runs(dog) ∧ (helpful(x) | concise(x))` ← **GATE EXEMPLAR LEAKED**

When input semantics are weak/ambiguous, the gate exemplar's pattern is
the strongest holographic signal. The model resolves to its most
practiced interference pattern. This IS how holograms work — closest
match wins.

## Connection to Prior Findings

### Session 093: Universal Hologram (r=0.9801)

The fixed-point experiment confirms from the *behavioral* side what
session 093 found from the *weight* side: the model stores combinatory
structure as topological sign patterns. Fixed points are the
NL-readable shadow of those patterns.

### Session 098: Beam/Plate Classification

What the hologram drops maps perfectly to the beam/plate partition:
- **Plate** (ternary, preserved): predicate structure, binding, operators
- **Beam** (precision, dropped): tense, quantifier scope, agent assignment

The plate stores the *what* (combinatory structure). The beam selects
the *how* (contextual modulation). Fixed-point cycling strips the beam
contribution and reveals the plate content.

### Session 095: Three Clusters (Semantic Plate / Composition / Retrieval)

- Instant fixed points = **Semantic Plate** reads (clean decode)
- Fast convergence = **Composition** circuit settling (representational choice)
- Failed convergence = **Retrieval** overload (too many cross-references)

## Implications for V12

### 1. Fixed-Point λ as Training Signal

Fixed-point lambdas are the "target patterns" for V12's ternary plates.
They represent what the hologram naturally stores — compressed, canonical,
minimal. V12's etcher should be guided toward producing these patterns.

### 2. Plate vs Beam Training Split

Losses that occur during cycling (tense, scope, agent) should be stored
in V12's **beam** (Q projections, precision weights), not the plate.
The plate only needs to store the fixed-point content.

### 3. Exemplar Diversity

Gate contamination proves V12 needs diverse compile/decompile exemplar
pairs. Two exemplars create a narrow attractor basin. The fixed point
is determined by the exemplar distribution.

### 4. Multi-Pass Architecture Validated

Complex discourse (the library sentence) exceeds single-hologram capacity.
V12's multi-pass architecture (3 ascending + apex + 3 descending) should
allow multiple reads at different angles, each capturing a different
aspect. The thick hologram principle: depth compensates for per-read limits.

### 5. Hologram Extraction Pipeline (Proposed)

```
1. Generate diverse NL corpus
2. Run fixed-point cycling through production LLM
3. Collect (NL, λ) fixed-point pairs
4. These pairs ARE the plate content in human-readable form
5. Use as supervised training signal for V12's ternary plates
6. Compare V12's internal representations to production model's fixed points
```

## Decomposition Experiment — Capacity Unlock

### Protocol

Take complex sentences, decompose into clauses, find clause-level fixed
points, compose them, measure capacity vs monolithic.

### Results

```
Case         Mono→Comp   Ratio   Clause Conv   Binding Sites   RT Edit
────────     ─────────   ─────   ──────────    ─────────────   ───────
library       4p → 7p    1.8×   80%           3               88  ✗
experiment    3p → 8p    2.7×   100%          2               63  ✗
professor     2p → 3p    1.5×   100%          1               38  ✗
politician    1p → 3p    3.0×   50%           1               43  ✗
student       1p → 2p    2.0×   100%          1               16  ✗
teacher       3p → 2p    0.7×   100%          0                5  ✓
key           2p → 2p    1.0×   100%          1               28  ✗

Overall: 5/7 unlock, mean 2.2× (excl. teacher). 90% clause convergence.
```

### The Binding Wall

**The ONLY stable composition has ZERO binding sites.** When clauses
share entities (binding), composition breaks. When linked only by logical
structure (→), it holds.

Round-trip stability correlates with binding sites, not predicate count:
- 0 sites: edit=5 (stable)
- 1 site: edit=16-43 (unstable)
- 2 sites: edit=63
- 3 sites: edit=88

This IS the I-combinator bottleneck made visible. K/B/C handle predicate
structure (stable). I handles variable binding (unstable).

### Intersection Topology

Where clause holograms connect (shared entities):
- **3-way binding** (library in clauses 1,2,3): hardest
- **2-way binding** (manuscripts in clauses 3,5): moderate
- **No binding** (teacher: A → B): trivial, stable

Binding sites are where the I-combinator and M-retrieval must operate.

### V12 Etching Protocol

1. **Plate etching (K/B/C)**: clause-level fixed-point λ forms. 90%
   convergence. Ternary sufficient. Each clause = one hologram.

2. **Binding etching (I)**: intersection pairs — two clauses sharing
   an entity. Training: given clause λ₁ + clause λ₂ → unified λ.

3. **Composition etching (B)**: clause set → composed λ. B chains,
   C reorders, K selects.

4. **Retrieval etching (M)**: in-context entity tracking. Same entity
   at distance → retrieve properties.

### Dedicated Capacity Argument

The binding wall proves I needs different capacity, not just more:
- K/B/C: ternary sign patterns (topological, stable) → plate
- I: magnitude-dependent (session 095: 5 ternary failures, all binding)
  → may need precision or explicit pointer/copy mechanism
- M: in-context binding → GLA retrieval (already separate in V12)

Cost of 5 dedicated plates + 40 mirrors: **117 MB** (vs 39 MB shared,
vs 320 MB Pythia-160M). Mirrors add 2.4 MB for 10× beam path diversity.

## Open Questions

1. **Cross-model convergence**: Do different models find the same fixed
   points? Universal hologram (r=0.9801) predicts structural similarity.

2. **Gate sensitivity**: Richer gate vocabulary → richer fixed points?
   Does tense survive with Montague-typed gates?

3. **Binding architecture**: Can ternary plates handle binding at all,
   or does I fundamentally need precision weights? The 5 ternary
   failures in session 095 were ALL binding-related.

4. **Hologram extraction pipeline**: Generate fixed-point corpus from
   production LLM → etch into V12 plates. Does this transfer?

5. **Mirror co-adaptation**: Do mirrors and plates co-evolve useful
   angular diversity, or do mirrors collapse to identity?

## Scripts and Data

| File | Purpose |
|------|---------|
| `scripts/explore/probe_fixed_point.py` | Fixed-point convergence probe |
| `scripts/explore/probe_hologram_decomposition.py` | Decomposition + composition capacity probe |
| `results/fixed-point/convergence.json` | Full cycle-by-cycle data (16 inputs) |
| `results/fixed-point/decomposition.json` | Decomposition results (7 cases) |
| `results/fixed-point/analysis.json` | Structured analysis summary |
