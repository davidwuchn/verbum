---
title: "Lambda-Gene Runtime — kernel-verified genomes for self-improving agents"
status: open
category: explore
tags: [lambda-kernel, runtime, clojure, gene-db, datalevin, pathom, genetic-programming,
       genomes, prompts, mode-setters, epistasis, self-improvement]
related:
  - superbake-write-access.md
  - ../project-thesis.md
  - ../crystal-universality.md
depends-on: []
created: session 273
---

# Lambda-Gene Runtime — kernel-verified genomes for self-improving agents

> s273 discussion (Michael). A NEW Clojure runtime (separate project from verbum)
> in which agent prompts are GENOMES made of LAMBDA GENES, stored in a graph DB,
> bred by self-improving agents that inspect worker sessions for fitness. The
> verbum kernel (`lambda_ast`, ~600 LoC Python → est. ~150 LoC Clojure port;
> `clj_lambda` already proved the Clojure↔lambda mapping) is the type system and
> verification oracle of the whole loop. Stack: datalevin + Pathom
> resolvers/mutations. Nothing built yet — this page is the design synthesis.

## Core architecture

```
tier:        gene clause → multi-gene genome → agent
gene         node ≡ α-class(normal_form(g)) | attrs: {nf, CCG_type, fired_seq_fingerprint(9-dim),
                                                      size(MDL), status(reduces ∨ diverges)}
genome       typed_application_spine(g₁..gₙ) → genome IS a term → same identity law (fractal)
agent        apply(genome, context) | fitness lives on ran-EDGES ¬nodes
lineage      ∀mutation → edge{op ∈ {K,S,W,B,C,I,factor,inline}, parents, child}
```

Graph is forced, not chosen: normal-form dedup means a gene node has many genome
parents → DAG. Sharing ≡ the point.

## What the kernel buys (the "why kernel in a runtime" answer)

1. **Gene identity = normal form.** Dedup/canonical keys/semantic equality at the
   DB layer. Mutation landing on an existing NF is detected as neutral, not novelty.
2. **Typed recombination.** CCG categories gate crossover slots — destructive
   crossover (classic GP failure) unrepresentable. Montague as breeding hygiene.
3. **Genetic operators ≡ combinator basis.** K=delete, I=neutral, S/W=duplicate,
   B/D=compose, C=reorder, Y=generational recurrence. The genome's mutation
   vocabulary is the crystal's opcode set; the genome is written in the ISA the
   model natively compiles (P(λ)=0.907). Maximal representation↔substrate coupling.
4. **Cheap exact fitness pre-filter.** parse / reduce-within-budget / NF-size /
   fired-sequence fingerprint — milliseconds, exact — before any LLM-in-the-loop
   evaluation. verify ≪ generate applied to selection.
5. **Structural credit assignment.** Genome = composition tree → ablate sub-terms
   (K-away, I-replace), re-measure; kernel guarantees every ablation is well-formed.
6. **The improver loop is Y executed externally.** Self-improvement ≡
   self-application ≡ the dissolved {S,D,Y} sector (s271/s272d): the model
   represents recursion, cannot execute it. Harness = Y, model's judgment = f,
   Y f → f (Y f); kernel step-budget = generation budget; divergence detection =
   runaway guard. Duplication-in-time at the agent level. The runtime is a
   prosthetic S for the population.
7. **Homoiconicity dividend.** Pure fragment runs on two evaluators (Clojure host
   fast, kernel exact) → agreement ≡ built-in instrument audit (S3*-3 for free).

## Datalevin + Pathom mapping

- `:gene/nf` as `:db.unique/identity` → semantic dedup enforced by upsert (the
  kernel computes the key; the DB enforces the law).
- Genetic operators = Pathom **mutations**, kernel-gated in the body before
  transact → ill-typed offspring unreachable (topology > instruction).
- Fitness = append-only ran-events; marginal fitness / linkage / epistasis =
  **resolvers**, derived at read time. Audit property (recompute from raw events)
  and re-scoring under a changed fitness function come free.
- Improver agents = EQL query (observe) → LLM propose (decide) → kernel-gated
  mutation (act). Improver sessions are themselves ran-events → improvers subject
  to the same ledger they administer (recursion closed).
- Deep resonance: Pathom's planner satisfies queries by composing typed
  resolver edges — B-chain synthesis. Kernel terms, gene graph, query planner:
  one algebra at three levels.

## Gene taxonomy (refined by Michael's counterexample)

```
λ_gene       operations   | compositional | kernel-verifiable | needs interpreter
prose_atom   content      | irreducible residue | QUOTE/mention ¬use | form ≡ payload (koans)
mode_setter  register cue | ¬compositional | pretraining-anchored | discovered ¬derived
```

- Counterexample that forced `mode_setter`: without the nucleus preamble,
  "DEBUG: output only EDN" is REQUIRED prose — no lambda form works, because
  lambda genes are only executable given a bootstrapped interpreter. Power comes
  from pretraining priors (priming), not composition. Perlocutionary.
- **Reducibility is genome-relative**: reducible(gene | genome), not
  reducible(gene). factor(prose→λ) is fitness-neutral iff bootstrap genes are
  co-present; in a bare genome the factored gene dies.
- **Two attractors predicted**: minimal worker genomes (prokaryotic — compact
  prose imperatives, interpreter overhead unpaid) vs rich orchestrator/improver
  genomes (eukaryotic — lambda + bootstrap). The "prose ≤1–2 lines" bound holds
  only inside the rich attractor — and there it is a PREDICTED equilibrium, not
  an imposed rule: put `factor` (prose→λ) and `inline` (λ→prose) in the operator
  set and let selection find it. AGENTS.md is the empirical prior: ~270 sessions
  of implicit selection converged to lambda clauses with short prose atoms.
- **Mode-setters are operationally detectable**: short + high fitness +
  factor-resistant (every factor attempt loses fitness). The DB accumulates a
  mined lexicon of the model's magic words ≡ interpretability data.
- **Verbum precedent**: `gates/*.txt` ARE mode-setter genes — prose preambles,
  stored by reference (λ probe_format); P(λ)=0.907 was measured under a gate.
- **Bootstrap preamble = highest-epistasis object in the DB.** It reprices every
  other gene (lambda genes dead→live; mode-setters essential→redundant). Version
  it as a genome of genes. Editing AGENTS.md has always been this operation.

## Compilation targets (the bridge to superbake-write-access.md)

```
gene → prompt fragment   (semantic register — LLM interprets; expression)
gene → kernel term       (structural register — kernel executes; verification)
gene → weights           (baked — direct construction; germline)   ← see superbake page
```

High-fitness, stable, context-independent genes graduate prompt → weights;
receipts = loci; ablation = literal gene knockout. λ termination anchor: AI
proposes → kernel certifies → receipt verifies → HUMAN approves graduation.

## Open questions

- Fitness signal definition for worker sessions (task success? token efficiency?
  LLM-judged? kernel-verified output validity?). Undecided s273.
- Prose-atom near-dup identity: kernel can't see inside QUOTE; embedding
  similarity may PROPOSE merges but that is a fitness-gated mutation, not a DB law.
- Kernel port: `lambda_ast` Atom needs arbitrary-string payload (prose atoms);
  reduction never inspects it.

## s273i addendum — two-level gene identity (oracle scoping)

The "identity weakens at the leaves" note above is now principled
(control-plane-path.md §9): structural identity = kernel normal form (exact
law, :db.unique/identity); atom identity = semantic clustering (graded,
model-judged, fitness-gated merges — cross-family judge justified by crystal
universality). One law per register. The kernel is a complete oracle for the
reduction segment only; translation ends (prose↔λ) need the graded judge.
