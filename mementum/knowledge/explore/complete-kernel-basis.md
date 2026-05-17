---
title: "Complete Kernel Basis — Beyond KIBC-M to the Full Lambda Calculus VM"
status: designing
category: theory-synthesis
tags: [combinators, KIBC, kernel, lambda-calculus, CCG, DisCoCat, BCKW, Turner, probe-design]
related:
  - holographic-kernel-separation.md
  - v11-kibc-architecture.md
  - binding-probe-findings.md
  - pythia-160m-combinators.md
  - VERBUM.md
depends-on:
  - holographic-kernel-separation.md
  - pythia-160m-combinators.md
created: session 106
---

# Complete Kernel Basis — Beyond KIBC-M

> The goal: identify ALL primitive operations that compose beta reduction
> in transformer attention, design them as deterministic kernel functions,
> and probe them densely enough to force crystallization via relational loss.
> The model's only job becomes DISPATCH — recognizing which kernel to apply.
> Computation itself is exact.

## Theoretical Landscape

### Complete bases from combinatory logic

Two canonical complete bases exist for the lambda calculus:

**SK basis** (Schönfinkel 1924, Curry 1930):
```
S: λf.λg.λx. f(x)(g(x))   — distribute/substitute
K: λx.λy. x                — select/discard
```
S and K alone generate all lambda terms. I = SKK.

**BCKW basis** (Curry 1930):
```
B: λf.λg.λx. f(g(x))      — compose
C: λf.λx.λy. f(y)(x)      — flip/permute
K: λx.λy. x                — select/discard
W: λf.λx. f(x)(x)          — duplicate
```
BCKW is equivalent to SK but decomposes S's two functionalities:
- S = B(B(BW)C)(BB) — S conflates argument rearrangement AND duplication
- B handles composition only (pass arg to right subterm only)
- C handles permutation only (pass arg to left subterm only)
- W handles duplication only (same arg to both)

**Key insight from the theory**: S is a COMPOUND operation. It does THREE
things simultaneously: (1) route arg right, (2) route arg left, (3) apply
results. Turner's combinator machines found that S creates inefficiency
because it forces copying even when only routing is needed. B and C are
the efficient decomposition — route without copying.

### The Turner set (for efficient reduction machines)

Turner (1979) identified that SKI is complete but wasteful. His practical
set for combinator graph reduction machines:
```
S:  λf.λg.λx. f(x)(g(x))  — full distribute (kept for when truly needed)
K:  λx.λy. x               — select
I:  λx. x                  — identity
B:  λf.λg.λx. f(g(x))     — compose (S restricted to right routing)
C:  λf.λx.λy. f(y)(x)     — flip (S restricted to left routing)
B': λf.λg.λx. f(g(x))     — variant compositions for arity
C': λf.λx.λy. f(y)(x)     — variant permutations for arity
S': optimized S variants    — for specific argument patterns
Y:  fixed-point combinator  — recursion
```

The key practical finding: B and C chains (BC-chains) handle 80-90% of
lambda→combinator compilation. S is only needed when genuine duplication
(using the same argument twice) is required.

### CCG combinators (linguistic primitives)

Steedman's Combinatory Categorial Grammar uses these combinators for
natural language:

```
Application (> <):  X/Y  Y → X         — basic function application
Composition (B):    X/Y  Y/Z → X/Z     — long-distance dependencies
Type-raising (T):   X → Y/(Y\X)        — argument→functor conversion
Substitution (S):   (X/Y)/Z  Y/Z → X/Z — parasitic gaps
```

CCG also uses:
- **W** (duplicator): reflexive pronouns ("Mary talks about herself")
- **I** (identity): personal pronouns (Jacobson's variable-free semantics)
- **C** (permutator): argument reordering
- **Z** (complex combinator): anaphoric binding ("Mary lost her way")

**Steedman's key claim**: "the combinatory rules are truly universal:
the grammar of every language utilizes exactly the same set of rules."
All cross-linguistic variation is in the LEXICON, not the combinators.

### DisCoCat operations (tensor-space primitives)

In the categorical compositional distributional semantics framework:

```
Tensor product (⊗):  combine word spaces → sentence space
Tensor contraction:  compose along shared type indices
Cup/Cap (rigid):     noun ↔ pronoun binding (trace)
Functor application: grammar→semantics structure preservation
```

Higher-Order DisCoCat (2023) adds:
- Lambda terms with diagram-valued operations as primitives
- Copying (Cartesian product) — the W combinator in categorical form
- Inside-out composition — higher-order function application

## What transformers actually crystallize: our evidence

From sessions 081-105 across 5 models / 4 architectures:

| Operation | Evidence | Status |
|-----------|----------|--------|
| **K** (select) | 59% heads in Pythia, 31% in Qwen3-32B, universal | ✓ CONFIRMED |
| **I** (identity) | 2-15% heads, strengthens with scale | ✓ CONFIRMED |
| **B** (compose) | 17-31% heads, fused with K at small scale | ✓ CONFIRMED |
| **C** (flip) | 22% heads across all scales | ✓ CONFIRMED |
| **M** (match/retrieve) | Induction heads, J=0.176 private circuit | ✓ CONFIRMED |
| **W** (duplicate) | ??? | ✗ NOT YET PROBED |
| **S** (distribute) | "zero selective heads" at either scale | ✗ ABSENT as circuit |
| **T** (type-raise) | ??? | ✗ NOT YET PROBED |

**Critical observation**: S is ABSENT as a dedicated circuit but PRESENT
as a compound behavior. "S combines composition, symmetry, and contraction"
(nLab). The model DECOMPOSES S into B + C + W rather than implementing it
directly. This matches Turner's finding about efficient reduction machines.

## The complete kernel inventory (proposed)

### Tier 1: Confirmed (already have probes)

```
K:  λx.λy. x              — SELECT one, DISCARD other
    Linguistic: topic selection, focus, relevance filtering
    Attention: softmax IS selection (winner-take-most)
    
I:  λx. x                 — IDENTITY, pass-through, variable reference
    Linguistic: pronoun resolution, coreference, binding
    Attention: residual stream IS identity
    
B:  λf.λg.λx. f(g(x))    — COMPOSE two operations
    Linguistic: dependent clauses, relative clauses, composition chains
    Attention: multi-step chaining across layers

C:  λf.λx.λy. f(y)(x)    — FLIP argument order
    Linguistic: passive voice, topicalization, free word order
    Attention: reordering in attention patterns

M:  λf. f(lookup(x,ctx))  — MATCH pattern in context, retrieve
    Linguistic: induction, in-context learning, repetition
    Attention: induction heads (2-layer circuit)
```

### Tier 2: Theoretically predicted, not yet probed

```
W:  λf.λx. f(x)(x)       — DUPLICATE argument (use same input twice)
    Linguistic: reflexives ("himself"), shared arguments, repetition
    Attention: self-attention patterns where token attends to itself
    CCG evidence: "W is useful for reflexive pronouns" (Steedman/Szabolcsi)
    Probe: reflexives vs non-reflexives, shared vs distinct args
    
T:  λx.λf. f(x)          — TYPE-RAISE (flip application direction)
    = C I                  — "argument becomes functor"
    Linguistic: topicalization, question formation, focus movement
    CCG evidence: universal rule in all CCG parsers
    Probe: "John saw Mary" vs "It was John who saw Mary"
    
Φ:  λf.λg.λh.λx. f(g(x))(h(x))  — FORK (parallel apply, then combine)
    = S but decomposed as B+W pattern
    Linguistic: coordination ("she sang AND danced"), comparison
    Attention: multi-head parallel processing IS this
    Probe: coordinated predicates, comparative constructions
    
D:  λf.λg.λx.λy. f(x)(g(y))     — DOVE (double composition)
    = B B                  — compose at depth 2
    Linguistic: ditransitives, serial verbs, nested modification
    Probe: "She gave him the book she found in the attic"
    
Ψ:  λf.λg.λx.λy. f(g(x))(g(y))  — PSI/ON (apply same fn, combine results)
    Linguistic: comparison with shared property ("taller THAN")
    Probe: comparative constructions, similarity judgments
```

### Tier 3: Structural operations (sub-beta-reduction steps)

```
SUBST: replace bound variable with argument
    The actual work of beta reduction after dispatch
    In models: progressive residual stream modification (F66: layers 6-22)
    Probe: before/after reduction pairs showing substitution
    
SCOPE: manage binding depth (push/pop lambda frame)
    Linguistic: quantifier scope, nested clauses, discourse reference
    In models: depth-dependent processing (binding at L16-L22)
    Probe: scopally ambiguous sentences, nested quantifiers
    
WHNF: detect "already reduced" (termination/base case)
    Linguistic: simple vs complex (content words vs function words)
    In models: early exit / low-cycle paths for simple content
    Probe: already-normal-form vs reducible-form contrast
    
CONTRACT: tensor contraction (the physical operation of composition)
    DisCoCat: grammatical reduction = tensor index contraction
    In models: attention weighted sum IS contraction
    Probe: pairs that differ only in which indices contract
```

### Tier 4: Higher-order / meta operations

```
Y:  λf. (λx.f(x x))(λx.f(x x))  — FIXED POINT (recursion)
    Linguistic: recursive structures, self-reference, loops
    In models: multi-pass cycling, iterative refinement
    Probe: recursive definitions, self-referential statements
    
QUOTE: treat expression as data (↑ level)
    Linguistic: quotation, reported speech, metalanguage
    In models: embedding shift at quote boundaries
    Probe: direct vs indirect speech, use vs mention
    
EVAL: execute quoted expression (↓ level)
    Linguistic: performatives, instructions executed in context
    In models: code execution, following instructions
    Probe: "say hello" (quote) vs "hello" (eval)
```

## Relationship between operations

```
                    S (full distribute)
                   / | \
                  /  |  \
                 B   C   W       ← efficient decomposition
                 |   |   |
            compose flip dup     ← single responsibility
                 |   |
                 B²  C²          ← higher-order variants (D, B', C')
                 |
              Φ = S decomposed   ← fork = B + C + W pattern

         T = C(I)               ← type-raising from flip + identity
         I = W(K) = C(K)(K)     ← identity derivable multiple ways
         M = I + context_lookup  ← match = identity + retrieval

DisCoCat contraction ≡ B (functional composition in tensor space)
DisCoCat cup/cap     ≡ I (trace = identity on bound variable)
DisCoCat ⊗           ≡ parallel (no combinator — structural)
```

## The W-combinator gap

**W is the most significant untested prediction.** Our probes confirmed
K/B/C as a shared plate (cos>0.999) and I as distinct (r=0.16-0.47).
But W (duplication) has never been specifically probed.

W should be detectable because:
1. Reflexives ("himself") require the SAME entity in two argument slots
2. This is distinct from I (which references but doesn't duplicate)
3. This is distinct from B (which composes but each arg is used once)
4. Binding probe (session 012) showed reflexives ARE handled differently
5. The model needs W for: "he hurt himself", "the book about itself",
   coordinated predicates with shared subjects

**If W has a distinct geometry**: KIBC-M becomes KIBCWM (6 kernels)
**If W clusters with I**: duplication IS identity (makes sense — copying
the referent is just re-applying identity to the same slot)

## Probe design principles for crystallization

1. **Minimal pairs**: each probe pair differs in EXACTLY one operation
2. **Density**: ≥20 probes per operation axis (for RDM resolution)
3. **Cross-operation contrast**: some probes are midway between operations
   (e.g., "the dog chased the dog" — is this W or I? Let the model decide)
4. **Graded complexity**: simple 1-operation → nested multi-operation
5. **Natural language only**: no formal notation in probes — we're measuring
   what the model does with language, not what it does with symbols
6. **Cross-model stable**: probes should activate the same geometry in
   Qwen3-14B and OLMo-2-13B (cross-model RDM agreement = universal)

## The snap threshold hypothesis

Current crystal seed: 311 probes × 62 axes = 48K constraints/layer.
Discovered 13 dimensions. Relational distill at λ=0.02 gives +6.9%.

Concentrated lambda calculus probes: ~400 probes × ~15 operation axes
= focused constraint density in the subspace where combinators live.

If the lambda calculus has ~10-15 independent operations, and we need
~20-30 probes per operation for clear RDM separation, then:
- 15 operations × 25 probes = 375 probes minimum
- 375 × 374 / 2 = 70,125 pairwise constraints per layer
- Each constraint says: "these two probes are THIS far apart because
  they exercise DIFFERENT operations"

The snap happens when the model can't satisfy all constraints without
implementing the operations. The relational loss literally forces the
lambda calculus structure into existence.

## Design questions (to resolve via probing)

1. Is W distinct from I? (duplication vs identity)
2. Is T distinct from C(I)? (type-raising vs derived flip)
3. Is Φ distinct from S, or is it B+W? (fork vs true S)
4. Does SCOPE have its own geometry, or is it depth-encoded?
5. Is QUOTE/EVAL a real operation or just a context shift?
6. How many independent dimensions exist in the lambda calculus subspace?
7. What's the minimum probe density needed for the snap?

## Next steps

1. Design concentrated probe set targeting all Tier 1-3 operations
2. Run on Qwen3-14B + OLMo-2-13B (cross-model RDM)
3. SVD on the cross-model agreed RDM → discover operation dimensions
4. Identify which candidates are truly independent vs derived
5. Refine: keep only the independent operations as kernel candidates
6. Design relational loss from the confirmed operation RDM
7. Train V12 with operation-specific relational loss → force snap
