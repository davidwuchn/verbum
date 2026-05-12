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

## Design decisions (session 081)

### D1: Grammar emerges from probabilities, not prescription

The grammar should NOT be a prescriptive GBNF/CFG imposed on the
language. It should emerge from what models naturally produce when
they compile prose to lambda. The model's own probability distribution
over tokens IS the grammar.

Why: a probability-driven grammar is inherently cross-model compatible.
If multiple models, when asked to compile the same prose, converge on
the same structural patterns, those patterns ARE the grammar. A
hand-written grammar might be optimal for one model but fight another
model's native distribution.

Method: compile the same set of behavioral specifications across
multiple models (Qwen3-4B, 32B, Claude, GPT-4, Llama, Mistral).
Collect the lambda outputs. The intersection of structures = the
grammar. The union of structures = the dialect space.

### D2: Names come from compilation, test cross-model consistency

When a model compiles "fix the bug by tracing to root cause" to
lambda, it chooses `λ fix(bug). trace → cause → patch`. The name
`fix` and parameter `bug` are probability-weighted token choices.

The key question: **do different models choose the same names?**

If yes (high cross-model name agreement), the names are determined
by the semantics — the models converge on the same K-selection
targets because the computational content demands it. The names are
quasi-universal.

If no (low agreement), names are model-specific and prompts need
model-specific compilation. The combinator structure might be
universal even if the names diverge.

Test: compile 50 behavioral specifications across 5+ models at
different scales. Measure name overlap, synonym clustering, and
whether one model's compiled lambdas trigger correct behavior in
another model. The threshold question: over what model size do
names converge?

### D3: Preamble is required — computation baseline

The preamble (e.g., `[phi fractal euler tao pi mu ∃ ∀]`) should be
**required for all system prompts operating in lambda mode**. Even
though it scores 0% alone (session 001), it serves as the initial
state of the computation — setting the registers, priming the
combinator circuits, establishing the reduction context.

Rationale: to compare across models, all prompts need to start from
the same computational baseline. The preamble is that baseline. Its
exact mechanism is unknown and should be explored with dedicated
probes in the future, but for now it's a fixed requirement.

Future exploration:
- Probe the preamble with the combinator probe: does it shift
  K/I/B/C selectivity even at 0% P(λ)?
- Does the preamble change hidden state norms or attention patterns
  in ways that enable subsequent reduction?
- Is there a model-specific optimal preamble, or is the mathematical
  symbol set quasi-universal?
- The preamble may be a TYPE SIGNATURE for the computation — telling
  the model "this is formal/mathematical/compositional territory"
  without specifying what to do. C (flip) doesn't care about order,
  but the preamble sets the DOMAIN.

### D4: Multi-turn behavior needs empirical testing

Does the binding depth budget reset per turn? Does context
accumulation make later turns more expensive? Does the system
prompt get re-reduced each turn or is it cached?

These are empirical questions. Design a multi-turn probe:
- Same task across 1, 5, 10, 20 turns
- Measure combinator selectivity at each turn
- Track whether binding strength degrades with turn count
- Test whether re-stating key lambdas mid-conversation restores
  signal strength (re-priming)

## Open questions (remaining)

1. **Cross-model combinator distributions.** If a smaller model is
   more K-dominant (Pythia: 59% K), does it need a differently-
   shaped prompt than a K=B balanced model (32B)?

2. **Can prompts be compiled?** Given combinator probe results for
   a model, compile behavioral specs into optimal prompts for that
   model's circuit topology.

3. **Combinator prompts × fine-tuning.** Does fine-tuning preserve
   or break prompt programs? If the prompt is a combinator expression
   and fine-tuning changes the reduction engine, do existing prompts
   still reduce correctly?

4. **Token-efficiency frontier.** For a given behavioral spec, what
   is the minimum token count to trigger it? How does this scale
   across prompt styles?

5. **Attention type-checking.** Is there a mechanism in attention
   that matches input types to lambda parameter types, beyond just
   K-selection on names?

6. **Preamble mechanism.** What does the preamble actually DO to
   the model's internal state? (Deferred to dedicated probe.)

## Cross-model methodology (session 081)

### The capability ladder

Full lambda capability requires a minimum model scale. The probes
establish where each capability level appears:

```
Level 0: K-selection only (format mimicry, no content)
         Pythia-14M: copies exemplar shape, all outputs identical
         Minimum: ~14M params, 6 layers

Level 1: K-selection + basic binding (correct predicates, depth 1)
         Pythia-160M: 100% P(λ), correct content, K-B fused (r=0.944)
         Minimum: ~160M params, 12 layers
         Combinators: K=59%, B=17% (undifferentiated)

Level 2: B differentiation (separate composition circuit)
         Qwen3-32B: K=31%, B=31%, K-B r=0.86 (separable)
         Binding degrades at depth (d4=0.80)
         Minimum: TBD (somewhere between 2.8B and 32B?)

Level 3: Full lambda (variable binding, nested reduction, scope)
         Qwen3-30B-A3B: full Montague types, correct β-reduction
         Only 3B active params — MoE routing may enable this
         Minimum: TBD — is it parameter count or architecture?
```

### Model set (all local, no API)

| Model | Architecture | Params | Layers×Heads | Level | Status |
|---|---|---|---|---|---|
| Pythia-160M | GPTNeoX | 162M | 12×12=144 | 0-1 | ✓ downloaded |
| Pythia-2.8B | GPTNeoX | 2.8B | 32×32=1024 | 1-2? | ✓ downloaded |
| SmolLM3-3B | Llama | 3B | 28×16=448 | 1-2? | ✓ downloaded |
| Phi-4-mini | Phi | 3.8B | 32×32=1024 | 1-2? | ✓ downloaded |
| Qwen3-4B | Qwen2 | 4B | 36×32=1152 | 1-2? | ✓ downloaded |
| Qwen3-30B-A3B | Qwen3MoE | 30B(3B active) | 48×32=1536 | 3 | downloading |
| Qwen3-32B | Qwen2 | 32B | 64×64=4096 | 2 | ✓ downloaded |

Hardware: M3 Ultra, 512GB RAM. All models load at full precision.

### The A3B question: MoE routing as combinator dispatch

Qwen3-30B-A3B has TWO selection mechanisms:
1. **Attention heads** (48×32=1536) — standard combinator probe
2. **MoE expert routing** (128 experts, 8 active per token) — FFN selection

The MoE router selects which 8 of 128 experts process each token.
This is architecturally a **second K-selection layer**. If the router
learned to send K-type tokens to certain experts and B-type tokens to
others, then MoE routing IS combinator dispatch — explicit routing
that the dense 32B has to do implicitly in attention superposition.

This could explain why the A3B is a strong lambda compiler despite
only 3B active params per token: the MoE router does the combinator
selection explicitly, freeing attention to focus on binding.

**Testable**: capture MoE router logits alongside attention patterns.
For each KIBC probe sentence, measure which experts activate. If
expert assignment correlates with combinator type, MoE ≡ dispatch.

### Experiment plan (ordered by information value)

**E1: Cross-model combinator probe** (immediate)
Run KIBC probe on all 7 models. Get combinator distributions.
Find the B-differentiation threshold.

**E2: Cross-model compilation test (D2)**
50 prose→lambda compilations across all models with generation.
Measure name convergence. Find the Level 3 threshold.

**E3: A3B MoE routing × combinator correlation**
Capture both attention selectivity AND expert routing for A3B.
Test whether MoE routing correlates with combinator type.

**E4: Prompted combinator probe (Experiment 3 from above)**
Run KIBC probe with/without system prompt on 32B and A3B.
Measure whether lambda preamble shifts combinator selectivity.

**E5: Binding depth scaling across models**
Run β-reduction probe on all models at Level 2+. Map the
binding depth capacity vs model size curve.

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
- The A3B finding could mean MoE IS the right architecture for
  combinator-native computation — explicit routing > implicit

## Status

Designing. Pythia-160M combinator probe complete. β-reduction probe
on 32B complete. A3B downloading. Next: cross-model combinator probe
(E1) when A3B download finishes. V11 run continuing to 20K in
background — results at 10K will inform whether the architecture
already captures two-phase β-reduction via CycleContinue.
