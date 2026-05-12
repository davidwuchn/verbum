---
title: "Prompt as Program: System Prompts as Combinator Expressions"
status: designing
category: research-exploration
tags: [combinators, beta-reduction, prompt-engineering, system-prompt, nucleus, language-design]
related:
  - pythia-160m-combinators.md
  - kibc-32b-validation.md
  - session-001-findings.md
  - architecture-vs-scale.md
depends-on:
  - kibc-32b-validation.md
created: session 081
---

# Prompt as Program

> A system prompt is not a set of instructions the model "follows."
> It is a program written in the model's native combinator language
> that the model β-reduces against user input. If we understand the
> reduction mechanism (KIBC + two-phase β-reduction), we can design
> prompts that are optimally shaped for how the model actually
> processes them.

## The empirical foundation

### What the probes tell us

**Session 001** — The dual-exemplar gate:
- Two lines of demonstration = 100% P(λ), 100% compile activation
- L1:H0 reads *delimiters* (`. ) → λ`), not content
- Preamble symbols alone = 0%. Keywords alone = 40%
- Instruction < demonstration. Shape > content.

**Session 080** — KIBC combinators in Qwen3-32B:
- K (select): 31% of heads — softmax IS selection
- B (compose): 31% of heads — chaining operations
- C (flip): 23% — argument reordering
- I (identity): 15% — pass-through
- Three circuits: routing (K≈C), composition (B≈S), identity (I)

**Session 081** — Pythia-160M reinterpretation:
- K=59%, B=17% — K absorbs B at small scale
- The model mostly selects; composition is expensive

**Session 081** — β-reduction probe in Qwen3-32B:
- Two binding types: syntactic (peak L2-L9) and pronominal (peak L5-L27)
- Binding strength degrades with depth: d1=0.97, d2=0.92, d3=0.86, d4=0.80
- Substitution test: same mechanism different values (r=0.989)
- Inside-out processing for nested structures
- Centroid increases with depth: deeper binding → later layers

### What this means for prompt design

The model processes a system prompt through:

```
1. K-SELECT:  which abstraction matches this input? (early layers, L0-L15)
2. B-COMPOSE: chain selected abstractions if needed (early-mid layers)
3. β-REDUCE:  substitute user input into the selected abstraction (L21-L39)
4. RESOLVE:   inside-out resolution of any nested bindings (L40+)
```

Each step has a cost:
- K-selection is cheap (59-63% of heads do this natively)
- B-composition loses ~5% signal per chaining step
- Deeper binding requires later layers and degrades
- Nested structures process inside-out (expensive)

**The optimal prompt minimizes composition depth and binding depth
while maximizing the precision of K-selection.**

## What already works (empirical)

### Nucleus lambda notation

The AGENTS.md lambdas are already combinator programs:

```
λ fix(bug).   trace(bug) → cause(structural) → redesign > patch
λ build(x).   ∃lib(x) → use(lib) | ∃pattern(x,y) → extract(shape)
λ extend(x).  open_slot(x) > closed_dispatch(x) | addition > modification
```

Properties:
- **Flat** — one binding depth per lambda (x bound once)
- **Named** — K-selectable by name ("fix", "build", "extend")
- **Pre-composed** — the chain `trace → cause → redesign` is already
  composed in the prompt; the model doesn't need to B-compose it
- **Prioritized** — `>` and `|` give K clear selection signals

### The dual-exemplar gate

```
The dog runs. → λx. runs(dog)
Be helpful but concise. → λ assist(x). helpful(x) | concise(x)
```

Properties:
- **Two demonstrations** — minimum for pattern recognition
- **Shape-preserving** — same delimiter structure in both
- **Input→output mapping** — the model sees the reduction pattern
- **No meta-instruction** — no "you are a compiler," just examples

### Nucleus preamble (what doesn't work alone)

```
[phi fractal euler tao pi mu ∃ ∀]
```

This scores 0% alone. Why? It's **values without bindings**. The
symbols are there but nothing tells the model what to reduce them
against. There's no `λx.` to create a binding — the symbols float
free. They might bias attention (priming) but they can't trigger
β-reduction because there's nothing to substitute.

## The hypothesis

### System prompts as typed combinator expressions

A system prompt is most efficient when it is a collection of
**named, flat, pre-composed combinators** that the model K-selects
and β-reduces against user input:

```
PROMPT ≡ { λ name₁(x). body₁,
           λ name₂(x). body₂,
           ...
           λ nameₙ(x). bodyₙ }

PROCESSING ≡ K-select(nameᵢ, user_input) → β-reduce(bodyᵢ, user_input)
```

### Design principles (from probe data)

**P1: Flat over nested (binding depth budget)**

Each binding depth costs ~5% signal strength.

```
Good:  λ fix(x).  trace → cause → patch     (depth 1, strength ~0.97)
Bad:   λ fix(x).  λ cause(y). λ patch(z).   (depth 3, strength ~0.86)
```

Keep abstractions at depth 1. If you need depth, pre-compose.

**P2: Named over described (K-selection is cheap)**

K-selection is the model's dominant operation (59-63% of heads).
Give it clear selection targets.

```
Good:  λ fix(bug).    ...    ← name IS the selector
Bad:   When you encounter a bug, you should...  ← model must parse
```

Names are tokens. The model K-selects on tokens. A named lambda
is a single-token K-selection target. A prose description requires
B-composition to parse before K can even select.

**P3: Pre-compose chains (B is expensive)**

B-composition degrades signal. Pre-compose chains in the prompt
so the model does one K-selection, not multiple B-compositions.

```
Good:  λ fix(x). trace(x) → cause(structural) → redesign > patch
       ↑ pre-composed chain: one K-select, one β-reduce

Bad:   λ trace(x). ...
       λ cause(x). ...
       λ patch(x). ...
       "first trace, then find cause, then patch"
       ↑ three separate abstractions requiring B-composition at runtime
```

Exception: when the operations are independently useful, separate
them. The test: does the user ever invoke just `trace` without
`cause → patch`? If yes, keep them separate.

**P4: Demonstrate over instruct (shape > content)**

L1:H0 reads delimiters, not words. The model recognizes the
*shape* of a reduction pattern from examples.

```
Good:  input₁ → output₁        ← shape demonstrated
       input₂ → output₂        ← pattern confirmed

Bad:   "Transform inputs to outputs by..."  ← content described
```

Two demonstrations = pattern. The model infers the reduction
rule from the shape. This is literally how in-context learning
works: the exemplars ARE the program.

**P5: Signal priority with operators (K needs contrast)**

K-selection works by contrast: pick this, not that. Priority
operators (`>`, `|`, `∧`, `¬`) give K explicit selection signals.

```
Good:  simple(x) > complex(x)   ← K sees: prefer simple
       ∃lib(x) → use(lib)       ← K sees: existence → action
       addition > modification   ← K sees: prefer addition

Bad:   "prefer simple approaches but use complex when needed"
       ← K must parse prose to extract the priority
```

**P6: Symbols as type signatures (C reordering is free)**

C-flip is already differentiated (22-23% at any scale). Argument
order doesn't matter — the model reorders for free. But symbols
act as type signatures that help K-select the right abstraction.

```
λ fix(bug).    ← "bug" types the input → selects this for bugs
λ build(x).    ← generic x → selects for construction tasks
λ extend(x).   ← "extend" matches extension requests
```

The parameter name IS a type. `bug` is more selective than `x`.

### What this predicts

1. **Lambda-notation prompts should outperform prose prompts**
   at the same semantic content, because they minimize binding
   depth and maximize K-selectability.

2. **Adding more flat lambdas should scale linearly** (each is
   an independent K-selection target), while adding nested
   structure should degrade sublinearly (each depth costs 5%).

3. **Two exemplars should be near-optimal for pattern activation**
   (session 001 proved this). More exemplars have diminishing
   returns unless they cover new patterns.

4. **The order of lambdas shouldn't matter** (C-flip is free),
   but grouping related lambdas should help (spatial locality
   for attention).

5. **Preamble symbols prime but don't trigger** — they bias
   K-selection weights but don't create bindings. Useful as
   context, not as instructions.

## Experimental design

### Experiment 1: Lambda vs prose instruction

Compare on a fixed task (e.g., code review, bug fixing):

**Condition A — Lambda notation:**
```
λ review(code). correctness(code) > style(code) | security(code)
λ fix(bug).     trace(bug) → cause → minimal_patch
```

**Condition B — Prose instruction:**
```
When reviewing code, focus on correctness first, then style.
Check for security issues. When fixing bugs, trace the bug to
its root cause and make the minimal patch.
```

**Condition C — Hybrid:**
```
λ review(code). correctness > style | security
When reviewing, focus on what breaks before what looks wrong.
```

Measure: task completion, adherence to priorities, token efficiency.

### Experiment 2: Binding depth scaling

Same behavior, expressed at different binding depths:

**Depth 1:**
```
λ fix(x). trace → cause → patch
```

**Depth 2:**
```
λ fix(x). trace(x) → λ root(y). cause(y) → patch(x, y)
```

**Depth 3:**
```
λ fix(x). trace(x) → λ root(y). analyze(y) → λ solution(z). patch(x, z)
```

Measure: behavioral precision, consistency across invocations.
Prediction: depth 1 ≈ depth 2 > depth 3 (diminishing returns).

### Experiment 3: Combinator probe on prompted model

Run the KIBC combinator probe on Qwen3-32B **while different
system prompts are active**. Measure whether:

- Lambda prompts shift combinator distribution (more K? more B?)
- Prose prompts change the distribution differently
- The system prompt's structure is visible in the attention patterns

This would be the first direct measurement of how system prompts
interact with combinator circuits.

### Experiment 4: Minimum viable trigger

For a specific behavior (e.g., lambda compilation), binary search
for the minimum prompt that triggers it:

- Start: full nucleus gate (100% P(λ))
- Remove one element at a time
- Find the minimal set that maintains >95% P(λ)

Session 001 already started this (dual exemplar = minimum). But
now we can measure the combinator activation at each ablation
step to understand WHY each element contributes.

## Open questions

1. **Is there a formal grammar for this language?** The lambda
   notation is informal. Can we define a GBNF or CFG that
   constrains the "prompt program" to optimally-shaped expressions?

2. **Do different models have different combinator distributions?**
   If a smaller model is more K-dominant (Pythia: 59% K), does it
   need a differently-shaped prompt than a K=B balanced model (32B)?

3. **Can prompts be compiled?** If we have the combinator probe
   results for a specific model, can we "compile" a behavioral
   specification into the optimal prompt for that model's circuit
   topology?

4. **How do combinator prompts interact with fine-tuning?** If
   the prompt is a combinator program, fine-tuning changes the
   model's reduction engine. Does this preserve or break prompt
   programs?

5. **What is the token-efficiency frontier?** For a given behavioral
   specification, what is the minimum number of tokens needed in
   the prompt to trigger it? How does this compare across prompt
   styles (lambda vs prose vs exemplar)?

6. **Does the model's β-reduction mechanism have a type system?**
   If parameter names act as types (`bug` vs `x`), is there a
   type-checking mechanism in the attention that matches input
   types to lambda parameter types?

7. **Multi-turn reduction.** In a conversation, each turn is a
   new β-reduction against the accumulated context. How does this
   interact with the binding depth budget? Does context window
   position matter for K-selectability?

## Connections

This connects VERBUM's extraction work to practical prompt
engineering. If the extraction thesis is correct (architecture-shaped
models achieve combinator circuits with 4860× fewer param-token-ops),
then understanding how prompts interact with those circuits could:

- Improve nucleus (the existing prompt system) with empirical grounding
- Enable "prompt compilation" for specific model architectures
- Explain why certain prompt techniques work (chain-of-thought = 
  explicit B-composition? few-shot = exemplar β-reduction?)
- Inform v11's training: if the model will eventually be prompted,
  the training data should include prompt-shaped contexts

## Status

Designing. No experiments run yet. This page captures the theoretical
framework emerging from sessions 001 + 080 + 081. First experiment
should be the combinator probe on prompted models (Experiment 3) — 
it's the cheapest test of the core hypothesis.
