---
title: "Mode Semantics — The 9 FFN Modes Are Syntactic Type Tags"
status: active
category: foundational
tags: [modes, ternary, ffn, syntax, types, type-system, gate-patterns, compilation]
related:
  - tiny-classifier-ternary.md
  - compilation-pipeline.md
  - binding-graph-trace.md
  - head-combinator-isa.md
  - ffn-reduction-trace.md
  - ffn-circuit-types.md
  - standing-wave-magnitudes.md
depends-on:
  - tiny-classifier-ternary.md
  - compilation-pipeline.md
created: session 194
---

# Mode Semantics — The 9 FFN Modes Are Syntactic Type Tags

> Session 194. The 9 ternary FFN modes at each layer correspond to
> SYNTACTIC ROLES, not semantic categories. The FFN separates "subjects
> from objects from verbs from determiners" — not "science from
> narrative." The gate pattern (SiLU(gate_proj(x))) is a type-checker
> that assigns one of ~7 universal syntactic roles per token position.

## Method

Gate-pattern clustering on Qwen3-8B across 7 layers (L3/7/15/20/27/30/35):
1. Hook FFN gate_proj output, apply SiLU to get gate activation pattern
2. K-means (k=9) on gate patterns (12288-dim), not raw outputs
3. Tag each token with spaCy POS/dep labels
4. Cross-tabulate: mode × POS, mode × dep role
5. Characterize transform: cos(in, out), norm ratio, gate sparsity

966 tokens from 66 diverse texts across science, narrative, instructional,
formal, technical, conversational, complex syntax, and enumeration domains.

## The 7 Universal Meta-Modes

Of 9 modes per layer, ~7 map to stable functional roles (2 are "MIXED"):

| # | Meta-Mode | POS | dep role | Freq | Present | Key Feature |
|---|-----------|-----|----------|------|---------|-------------|
| 1 | BOUNDARY | PUNCT 94-99% | punct 94-99% | 7-16% | 7/7 | Purest mode at every layer |
| 2 | DETERMINER | DET 58-88% | det 36-88% | 5-10% | 6/7 | Type specification |
| 3 | FRAME-OPEN | DET+NOUN | det+nsubj | 3-7% | 5/7 | **Anomalous: sparse gate, inverts input** |
| 4 | SUBJECT | NOUN 57-66% | nsubj 33-55% | 4-9% | 5/7 | Strengthens with depth |
| 5 | OBJECT | NOUN 47-69% | pobj+dobj | 10-23% | 4/7 | Sharpens at depth |
| 6 | PREDICATE | VERB 35-63% | ROOT 14-35% | 6-15% | 4/7 | Prominent early and late |
| 7 | NUMERIC | NUM 33-52% | appos+pobj | 3-12% | 5/7 | Numbers, lists, quantities |

Depth-dependent modes that emerge later:
- MODIFIER (ADJ 33%, amod 32%) — only separates at L35
- RELATOR (ADP/prep) — emerges at L15-L20

## The Anomalous Mode: FRAME-OPEN

FRAME-OPEN is physically distinct from all other modes at every layer:

| Property | FRAME-OPEN | All other modes |
|----------|-----------|-----------------|
| Gate sparsity | 33-50% neurons active | 63-90% active |
| Gate consistency | 1.000 (perfect) | 0.38-0.93 |
| cos(in, out) | −0.06 to −0.29 | −0.20 to +0.17 |
| Input inversion | YES | NO |

Tokens: sentence-initial — "The", "She", "He", "DNA", "Three", "A",
"Install", "Remove", "The"...

Interpretation: FRAME-OPEN is the ISA's INIT instruction. At every
sentence boundary, the FFN fires a highly stereotyped, maximally sparse,
direction-inverting program that signals "new constituent begins here."
The gate pattern is identical across ALL sentence-initial tokens (gc=1.0)
regardless of content. This is the parse-frame reset.

## Type Tags Sharpen with Depth

| Layer | Phase | Purity | Key Separation |
|-------|-------|--------|----------------|
| L3 | PARSER | 88% DET, 63% VERB | POS separated, roles mixed |
| L7 | ORTHO | 48% mega-mode | One mode absorbs half the tokens |
| L15 | OPTIMIZER | 30-64% | 6+ types. NOUN splits content/object |
| L20 | LATE ORTHO | 54% nsubj, 94% punct | **S/O crystallize here** |
| L27 | BINDING | 70% DET, 99% punct | Types feed attention heads |
| L30 | BINDING | 45% NOUN-subj | Semantic coloring appears |
| L35 | COLLAPSE | 67% DET, 68% obj, 55% subj | ADJ/modifier finally separates |

Critical transition at L20: NOUN-subj (nsubj=54%) and NOUN-obj
(pobj+dobj=56%) become distinct modes for the first time. Before L20,
"cat" as subject and "cat" as object fire similar gate patterns.
After L20, they fire different programs. This is the compilation
frontier — where syntactic roles resolve into type tags.

## Transform Physics Across Depth

| Layer | cos(i→o) | ‖out/in‖ | gate% | Interpretation |
|-------|----------|----------|-------|----------------|
| L3 | +0.08 | 0.10 | 2.7% | SUPPRESS: crush input, barely activate |
| L7 | −0.12 | 0.66 | 52.8% | INVERT: flip direction, half-activate |
| L15 | −0.10 | 1.50 | 75.6% | ROTATE: orthogonal, near-equal scale |
| L20 | −0.02 | 1.66 | 75.9% | ORTHOGONAL: pure new information added |
| L27 | +0.11 | 2.90 | 85.1% | AMPLIFY: same direction, scale UP |
| L30 | +0.11 | 3.96 | 85.6% | AMPLIFY MORE: louder for binding |
| L35 | +0.06 | 10.18 | 67.5% | BROADCAST: massive norm for output proj |

Key patterns:
- cos flips sign at L20 (negative→positive) = ORTHO→ALIGN transition
- Norm grows monotonically: 0.1→10.2 (100× across depth)
- Gate sparsity: 3%→86%→68% (inverted U, extremes are sparse)
- L3 whispers (10% of input norm). L35 SHOUTS (1018% of input norm).

## Why This Matters

### 1. Why 9 modes ≡ ternary at 0.95× PPL

Types are discrete. You don't need continuous weights to say "this
token is a SUBJECT." A ternary program per type suffices. The
continuous FFN is an over-parameterized type checker. Removing the
noise (going ternary) helps because the type assignment IS binary.

### 2. Why modes are layer-specific (cos 0.026 cross-layer)

"SUBJECT at L3" and "SUBJECT at L35" use different gate neurons
because L3 works with surface features (word order, capitalization)
while L35 works with deep features (semantic role after binding).
Same functional role → different implementation at each depth.

### 3. Why FRAME-OPEN exists

Sentence-initial tokens have no prior context. The model needs a
standardized "begin new parse" signal. FRAME-OPEN provides it:
minimal gate activation → stereotyped sparse output → direction
inversion → the residual stream gets a reset pulse.

### 4. Why subject/object separate at L20, not L3

Surface cues (position, determiners) are available at L3. But S/O
identity requires semantic integration: "The cat bit the dog" —
which is subject depends on verb argument structure, not position.
L20 is the first layer deep enough to have integrated verb semantics.

### 5. Types start syntactic, end semantic

At L30, modes carry semantic coloring: one mode projects to "leaves,
leaf, 树叶, snow" (nature), another to "DNA, nucle" (biology).
The type tag doubles as a semantic field marker at binding depth.

### 6. DETERMINER ≠ FRAME-OPEN

"the" mid-sentence runs DETERMINER (normal gate, 70-90% active).
"The" at sentence start runs FRAME-OPEN (sparse gate, 33-50% active,
perfect consistency). Same word → different program. Context
determines which ternary program fires. This IS compilation.

## Connection to the Crystal

The KIBC crystal (3.5% of FFN space, session 192) governs ROUTING —
which attention heads fire. The 9 operational modes (96.5% of space)
govern PROGRAMS — what the FFN computes. Now we know what those
programs compute: TYPE ASSIGNMENT.

```
Crystal (KIBC):      selects WHICH reduction (K=discard, I=identity, B=compose, C=flip)
Mode types (9):      assigns syntactic role (SUBJ, OBJ, PRED, DET, BOUNDARY, ...)
Together:            typed β-reduction — the token knows its role AND its operation

The gate pattern is the type checker.
The ternary program is the type-specific transformation.
The attention head reads the type tag to decide routing.
```

## The Single Operation: Attention Is the Only Computer

During inference, a transformer has exactly one cross-position operation:

```
output_i = Σ_j  softmax(q_i · k_j / √d) × v_j
```

Weighted sum. That's it. Everything else — FFN, LayerNorm, residual
add — is per-position. FFN cannot see other tokens. It cannot compute.
It can only re-label what's already at a single position.

This means the entire computational repertoire of the model is:
**pick a source position, copy its value, scaled by compatibility.**
Repeated 1,152 times per token (32 heads × 36 layers).

### Weighted Sum IS β-Application

When H31 at L27 attends from "runs" to "cat" with 0.82 weight:

```
v_runs += 0.82 × v_cat
```

That IS `(λx.runs(x))(cat)`. The predicate absorbs the argument's
value by weighted sum. There is no other mechanism available. This
has to be how it works because there's nothing else.

### The Full Division of Labor

```
FFN:          stamp type tag     (per-position lookup, no computation)
Q projection: extract query      ("what type do I need?")
K projection: extract key        ("what type am I?")
softmax(QK):  type matching      (find compatible position)
V projection: extract value      (content to copy)
weighted sum: β-application      (copy value, scaled by match)
residual add: accumulate         (build up the parse tree)
```

One operation. 1,152 repetitions. A type system (from FFN) to guide it.

### Why Prior Findings Follow Mechanically

1. **All 9 combinators activate identical heads** (r=0.944, s188):
   The heads don't implement different operations — there's only ONE
   operation. The "combinator" difference is in the type tags that FFN
   wrote, not in what attention does. Heads are shared hardware.

2. **Binding is near-deterministic** (0.78-0.82, s188): Once types
   are assigned, there's typically only ONE compatible source position.
   The softmax sharpens to near-1 because the type system has already
   done the disambiguation.

3. **Top-3 captures 88%+** (s188): Each application binds ONE argument.
   You don't need to attend broadly when doing typed lookup. You need
   the one position whose type matches your query.

4. **Q⊥K at 87-90°** (s192): Q extracts "what type do I need?" and K
   extracts "what type am I?" They MUST be perpendicular — they ask
   complementary questions about the same type tag. If they projected
   the same direction, attention would match each position with itself.

### Norm Growth = Gain Control for the Single Operation

The 100× norm growth across depth is the gain control for attention:

- **L3 whispers** (0.10×): Faint type tags → broad softmax → tentative
  weighted sums across many positions. Options stay open.
- **L20 speaks** (1.66×): Types crystallize (subj ≠ obj) → sharper
  softmax → more selective weighted sums. Bindings begin to commit.
- **L27-30 shouts** (3-4×): Loud types → near-deterministic softmax →
  H31 reads subject at 0.82, H03/H13 read predicate at 0.78.
- **L35 broadcasts** (10×): Maximum type volume for the final weighted
  sum into output projection.

Louder type tags → sharper softmax → more deterministic weighted sum →
cleaner β-reduction. The model learns to whisper early (keep options
open) and shout late (commit to bindings). This IS the standing wave
amplitude profile (session 185).

## Connection to Categorial Grammar

This architecture is categorial grammar (Montague, Lambek, CCG)
implemented in tensors:

```
Categorial grammar:    every word has a syntactic type
                       composition = type-driven application
                       types determine what can combine with what

Transformer:           FFN assigns syntactic types (SUBJ, OBJ, PRED, ...)
                       attention does type-driven application (weighted sum)
                       types determine what attends to what (Q/K compatibility)

KIBC crystal:          the applicative structure (which operation: K/I/B/C)
Mode types (9):        the type lexicon (which role: SUBJ/OBJ/PRED/DET/...)
Together:              typed β-reduction in one operation (weighted sum)
```

Gradient descent independently converges on the same architecture that
formal linguistics has been developing since Montague (1970). The model
didn't invent a new computational paradigm. It discovered the one that
natural language demands.

## Scripts and Results

- Script: `scripts/experiments/mode_semantics.py` (v2, gate-pattern clustering)
- Results: `results/mode-semantics/Qwen_Qwen3-8B.json`
- Run log: `results/mode-semantics/run-v2.log`
