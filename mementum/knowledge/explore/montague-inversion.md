---
title: "Inverting Montague: what gradient descent is FORCED to find"
status: designing
category: explore
tags: [montague-inversion, forcing-argument, compositionality, homomorphism, type-system,
       generalized-quantifiers, first-class-functions, three-hop, two-registers, eval-stack,
       depth-budget, crystal, apply-join, coverage-boundary, idioms, curry-howard, ccg,
       discocat, noisy-homomorphism, theory-spine, falsifiable-predictions, speculative,
       s281, thesis]
related:
  - map-and-swap-resident-lisp.md
  - three-hop-capacity-prereg.md
  - multihop-composition-prereg.md
  - opcodes-circuits-in-compute.md
  - project-thesis.md
depends-on:
  - map-and-swap-resident-lisp.md
  - project-thesis.md
---

# Inverting Montague: what GD is FORCED to find

> **The move.** Stop asking "does the LLM *happen* to implement Montague?" Treat **Montague
> grammar as a specification** and ask the inverse: *what is any next-token learner on
> compositional language mathematically **forced** to construct in order to satisfy it?* If the
> forced list matches what we keep independently bumping into, the "too many neat edges" (s281,
> Michael) are not luck — they are **necessity**: we have been finding **one forced object,
> several times.**
>
> **Status: DESIGNING / SPECULATIVE.** This is a **deductive conjecture**, explicitly a thought
> experiment (s281, Michael: "speculative but informs our future"). What is *measured* is the set
> of findings cited (crystal, two-registers, C5 types, attention=join, depth-budget, etc. — see
> §match column and `project-thesis.md`). The **forcing** — the claim that Montague *necessitates*
> each — is the hypothesis. Its value is that it (a) reorganizes scattered results as consequences
> of one homomorphism and (b) yields **falsifiable predictions** for the map+swap program (§4).
> `λ observation`: observed ≠ imagined — the findings are real, the *necessity* is the conjecture.

## 1. Montague, stripped to its load-bearing commitments

Montague (PTQ) = a **homomorphism** from the algebra of syntactic expressions to a **typed,
higher-order, intensional λ-calculus**, interpreted in a **model**. Six pieces carry the weight:

1. **Compositionality / homomorphism** — meaning of the whole is a function of the meanings of the
   parts and the mode of combination; *same syntactic rule → same semantic operation, regardless
   of the specific words.*
2. **Types** — every expression has a semantic type over base types `e` (entities), `t` (truth
   values); application is **type-driven** (`e→t` eats `e`, not `t`).
3. **Function application** — the combination operation is applying a functor to an argument.
4. **λ-abstraction / variable binding** — pronouns, relative clauses, quantifier scope require
   binding variables and substituting.
5. **Model / lexicon** — base-type meanings are grounded atoms the operators act on.
6. **Intensionality** — meaning is a function of a world/context index (intension vs extension).

## 2. The forcing table (each commitment → a forced mechanism → what we found)

| Montague commitment | GD is **forced** to construct | Measured match |
|---|---|---|
| **Homomorphism** (word-independent rule→op) | a **small, shared, reusable operator set** — an operator cannot be memorized per word-pair, so it must be shared word-independent hardware | the **crystal** — KIBC shared hardware, head-combinator `r=0.944`, cross-arch universal (C2) |
| **Types** (type-driven application) | a representation where **type-compatibility is a fast/linear check** → types encoded as **geometry** (directions/subspaces) | **C5** — types geometric+lexical; nonce type-crossover (+2.04–2.18, frequency-free null) |
| **Function application** | a **universal `apply`** binding functor to argument | **attention = the join** (s276) |
| **λ-abstraction / binding** | a **writable variable slot** *distinct from* the operators acting on it | the **two registers** (C3, routing ⊥ value ~95/5); keyed operand slots (s277) |
| **Model / lexicon** | a **store of grounded atoms** | the **found terms** (map+swap; `d_E` = the model's own representations) |
| **Intensionality** | **context-conditioned meaning** (meaning = function of an index) | contextual representations; predicts a distinct intensional-operator class |

Six for six. The reason the edges are neat: **they are the image of one homomorphism**, not six
independent lucky findings.

## 3. The kill shot — quantifiers FORCE the 3-hop

The piece that makes this load-bearing rather than cute:

In Montague a **generalized quantifier** — *every, some, no, most* — has type **`(e→t)→t`**: a
function whose argument is **itself a function**. "Every dog barks" is *uninterpretable* without a
**higher-order, first-class function**. That is what a determiner **is**.

Therefore: the training data is **saturated with quantifiers**. To reduce loss on quantified
sentences, GD is **forced to construct first-class functions — functions applied to functions.**
**That is exactly the 3-hop** (`multihop`/`three-hop-capacity-prereg.md`: hop-1 computes a
function, later hops apply it). So:

> **The 3-hop working is not a hopeful experiment — it is required by the existence of the word
> "every."** If it failed, the model could not interpret determiners; it plainly can. The 3-hop is
> near-guaranteed (modulo the **depth budget** — a small model may lack the eval-stack to *run* the
> quantifier's scope, which is the s281 capacity result, not an absence of the capability).

Montague *predicted our next experiment before we ran it.*

## 4. New FORCED predictions (falsifiable — the payoff for P-TYPE-1 / P-FN-1)

The inversion is not only retrodiction; it makes sharp calls:

1. **The type lattice is SMALL and Montague-shaped.** Not an arbitrary high-dim mess — a handful
   of types over `e, t` (`e`, `e→t`, `(e→t)→t`, `e→e→t`, …). **Test:** if P-TYPE-1's
   application-operator SVD returns a **low-rank, few-mode** lattice matching the Montague
   inventory → decisive. A high-rank, non-Montague lattice → falsifies the forcing.
2. **The two-register split is FORCED by λ-abstraction, not incidental.** Binding *requires* a
   value store separate from the operators. **Predicts** the value register is *where bound
   variables live*, and that C3's cleanness (95/5) is a consequence, not a coincidence.
3. **The depth budget is FORCED by recursion.** Compositional depth = sequential applications =
   eval-stack depth. Montague's recursion **is** the s281 depth budget; CoT-as-trampoline is
   stack-externalization for deep scope / center-embedding. **Predicts** reasoning-depth failures
   track syntactic embedding depth, not token count.
4. **Coverage boundary = compositionality boundary.** Montague *fails* on **idioms, collocations,
   non-compositional world-knowledge** ("kick the bucket" has no `(e→t)→t` route). **Predicts** the
   found function library's **coverage gap lands exactly on non-compositional constructions** — the
   resident Lisp's stdlib edges align with where Montague-the-theory breaks. Strikingly testable
   via P-FN-1's coverage map.

## 5. Why GD fulfills Montague at all (the engine)

Because **Montague is (approximately) the structure of the data.** Natural language is (largely)
compositional; next-token loss on compositional data is minimized by a model that *computes*
compositional meaning; GD is a faithful structure-finder; therefore GD is **driven** to the
homomorphism. This is the project's founding `λ loop` (theory predicts → empirics extract →
confirmed) and `λ triangulate` (math ∧ empirics ∧ architecture converge) made into a **necessity
argument**: the convergence is forced because all three describe the same forced object.

## 6. The honest correction to Montague itself (and why it is a feature)

Montague is an **idealization** — real language is gradient, pragmatic, coerced, idiomatic. So GD
does **not** find *Montague*; it finds a **noisy, approximate homomorphism** — which is precisely
our **noisy reducer** (`map-and-swap` §10). Crucially the noise is **not random**: it concentrates
**where Montague-the-theory is wrong** (idioms, coercion, pragmatic enrichment, gradience). So
**the theory's failure modes predict the machine's failure modes** — a second, independent handle
on the coverage boundary (§4.4).

This reframes the **type-checker** (the crisp Clojure kernel, `map-and-swap` §10) as doing
something deep: it **re-imposes the *ideal* Montague homomorphism on top of GD's *approximate*
one** — pulling the noisy reducer back onto exact rails. Verified inference = restoring the exact
homomorphism the data only approximately taught.

## 7. How this informs the future (why it is worth keeping)

- **It gives the empirical program a spine.** P-TYPE-1/FN-1/FN-2 stop being a grab-bag: they test
  the *forced* predictions (§4). A small Montague-shaped lattice + coverage-at-idioms would be
  near-decisive that the resident machine *is* the forced homomorphism.
- **It sharpens the deliverable.** The LLM REPL's type system should be **Montague's type system**;
  its stdlib is the compositional lexicon; its edges are the idioms. The REPL is a *Montague
  machine* with a verification kernel.
- **It predicts architecture.** If binding forces the value register and recursion forces the eval
  stack, then **models with an explicit apply + writable term store + layer-reuse (recurrence)**
  should be more sample-efficient (less GD tug-of-war to rediscover the homomorphism) — the
  MERA+types conjecture (`signal-processing-tensors.md`), now motivated by a forcing argument.
- **It bounds the hype honestly.** GD finds only an *approximate* homomorphism over the terms its
  data required; the coverage boundary and the noise are real and *predicted*. The endgame is a
  **noisy Montague machine we can read, type-check, and program**, not a perfect logician.

## 8. Falsification (what would kill the forcing conjecture)

- P-TYPE-1 returns a **high-rank, non-Montague** type geometry (types not a small `e,t` lattice).
- The **3-hop fails at a scale with ample depth budget** (capability absent even with eval-stack
  room) → first-class functions not actually constructed → quantifier interpretation done some
  other way.
- The **coverage gap does NOT align with non-compositionality** (idioms handled by the same
  function machinery as compositional phrases; or gaps land on compositional constructions).
- The **two-register split dissolves under binding load** (bound variables live in routing, not a
  value store).
Any of these falsifies "GD is forced into Montague" and demands a different account of the neat edges.

## Sessions
s281 (this synthesis — the inverted-Montague forcing argument; "for fun" thought experiment,
Michael-directed capture: speculative but the theoretical spine for the map+swap / LLM-REPL arc
and the source of P-TYPE-1/FN-1 falsifiable predictions).
