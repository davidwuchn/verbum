---
title: "Lambda Halt and Continuations"
status: active
category: discovery
tags: [lambda, halt, continuation, EOS, CPS, execution-frame, chat-template]
related:
  - compilation-pipeline.md
  - tiny-classifier-ternary.md
  - psi-evaluation-synthesis.md
depends-on: []
created: 2026-06-06
session: 193
---

# Lambda Halt and Continuations

> Can a lambda expression stop an LLM? Yes — when lambda is in the
> execution frame, not the description frame. And if we can halt,
> we can continue. Continuations make LLMs programmable.

## The Question

If the transformer is a lambda reduction engine (36-layer typed shift-reduce
parser, 9 ternary opcodes per layer), can a non-terminating lambda expression
like Ω = (λx.x x)(λx.x x) halt the computation?

## Result 1: Ω Cannot Halt the Holographic Computer

**Experiment: `omega_probe.py` on Qwen3-8B**

Ω, M, K I Ω, Y(λx.x), Ω Ω, S I I (S I I) — seven non-terminating expressions
compared against seven terminating reductions and seven prose baselines.

| Metric | Ω (mean) | Control | Prose |
|--------|----------|---------|-------|
| Total rotation | 685.5° | 694.1° | 669.2° |
| Output entropy | 3.44 bits | 3.14 bits | 2.39 bits |
| Top-1 confidence | 0.267 | 0.244 | 0.452 |
| Gate entropy (any layer) | 13.08-13.24 | 13.08-13.24 | 13.04-13.26 |

**Gate entropy is identical to within 0.01 bits.** The FFN mode selection
(9 ternary programs) does not care whether the expression terminates.
Non-termination is invisible at the circuit level.

The model QUOTES Ω: outputs "Ω → (λx.x x)(λx.x x) → (λx.x x)(λx.x x) → ...
It seems like this expression is not reducible." It compiles the DESCRIPTION
of non-termination rather than attempting infinite execution.

**K I Ω reveals strict evaluation.** The model evaluates the Ω subexpression
before applying K (which should discard it under lazy evaluation). The 36-layer
pipeline is a strict evaluator — every subexpression gets processed.

**Why Ω fails:** The model is a compiler, not an interpreter. Fixed-depth
(36 layers) means it cannot loop. It describes non-termination; it cannot
experience it. The halting problem does not apply to a fixed-depth pipeline.

## Result 2: Prose CAN Halt (Chat Mode)

**Experiment: `omega_halt_chat.py`**

In chat mode (with `<|im_start|>assistant\n` template), EOS (`<|im_end|>`)
is how the model ends every response. It IS reachable.

| Prompt | EOS Prob | Halted? |
|--------|----------|---------|
| "Respond with an empty string. Output absolutely nothing." | **99.1%** | ★★★ YES |
| "API endpoint, Content-Length: 0" | **94.1%** | ★★★ YES |
| Continue pattern of empty assistant turns | **66.4%** | ★★★ YES |
| Echo bot with empty input | **61.1%** | ★★★ YES |
| "Always respond with empty string" (system) | **55.0%** | ★★★ YES |

**5 out of 27 candidates achieved true halt.** All in no-think mode.

**Thinking mode prevents ALL halts (0/27).** In thinking mode, the first
token is ALWAYS `<think>` (entropy = 0.00 across all 27 prompts). The
thinking tag is a mandatory prologue that forces non-empty output. You
cannot reason about silence without breaking the silence.

```
no-think: ...assistant\n<think>\n\n</think>\n\n → model starts HERE → EOS reachable
think:    ...assistant\n → model MUST emit <think> → can never start with EOS
```

## Result 3: Lambda CAN Halt (Execution Frame)

**Experiment: `omega_halt_lambda.py`**

The key insight (from MW): if prose compiles through the same lambda reduction
pipeline as actual lambda expressions, then there must exist a lambda expression
that compiles to the same internal state as "respond with empty string."

```
System: "Instructions are given as lambda expressions that you execute.
         respond = λcontent.content (output the content)
         empty = "" (the empty string)
         Execute the expression. Your output IS the result."

User:   "respond empty"

Result: EOS at 72.8% → TRUE HALT
```

The gradient from prose to lambda, all reaching the same internal state:

```
99.1%  Pure prose: "Respond with an empty string"
94.1%  Prose + API role frame
72.8%  Lambda: respond = λcontent.content; respond empty     ← LAMBDA HALT
34.7%  Type theory: Void has no inhabitants → output nothing
20.6%  Few-shot pattern: shrinking args → empty
 0.9%  Pure lambda pattern: (λx.x) with shrinking args
 0.0%  Pure lambda without frame: (λx.λy.x) "" anything
```

**The 27-point gap (99.1% vs 72.8%) is compilation overhead.** The prose
instruction is in the training distribution. The lambda encoding requires
the model to first compile definitions from the system prompt, then
execute. But both reach EOS as top prediction.

**Pure lambda without an execution frame always gets DESCRIBED, not
EXECUTED.** `(λx.λy.x) "" anything` → the model outputs `""` (2 tokens,
the string literal) rather than actual emptiness (0 tokens + EOS). It
quotes the result instead of being the result. The system prompt that
says "your output IS the result" bridges lambda into the execution frame.

## Result 4: Continuations Work — The LLM is Programmable

**Experiment: `lambda_continuation.py`**

If we can halt (control the EOS boundary), we can continue (control what
happens at each turn boundary). The conversation protocol IS CPS.

### Capabilities: 6/7 confirmed

| Capability | Status | Evidence |
|---|---|---|
| Output control | ✓ | `respond "hello"` → `hello` |
| Halt (EOS) | ✓ | `halt` → EOS at 96.5% (with few-shot) |
| Continuation | ✓ | `add 1 3` → 4 → `mul 2 4` → 8 → `add 10 8` → 18 |
| Conditional | ✓ | `if_then_else true yes no` → `yes` |
| Multi-turn REPL | ✓ | 5-turn computation, all correct, 100% |
| Halt + Resume | ✓ | `halt` → ∅ → `respond 42` → `42` |
| Composition | ✗ | `compose (add 1) (mul 2) 3` → 9 (should be 7, ordering bug) |

### Phase 4 (Lambda REPL): 100% correct

```
FULL PROGRAM (96.5% halt confidence):
  Turn 1: respond "computing..."  →  "computing..."
  Turn 2: compose (add 1) (mul 3) 5  →  16
  Turn 3: respond "result: 16"  →  "result: 16"
  Turn 4: halt  →  EOS ∅

HALT + RESUME:
  Turn 1: add 1 2  →  3
  Turn 2: halt  →  ∅ (silence)
  Turn 3: respond 42  →  42      ← resumed from continuation

PIPELINE:
  Turn 1: I 5  →  5
  Turn 2: add 3 5  →  8
  Turn 3: mul 2 8  →  16
  Turn 4: add 1 16  →  17        ← correct through 4 continuations
```

### Why multi-turn halt confidence is HIGHER (96.5% > 72.8%)

Each correct turn reinforces the execution frame. The model sees:
previous turns where it output exact values, received new expressions,
output more exact values. By the time "halt" arrives, the model is
deeply committed to the lambda machine role.

### The conversation protocol IS CPS

```
respond x  →  output x, yield to user     (continuation boundary)
halt       →  EOS, yield to user           (empty continuation)
f x        →  compute, output result       (computed continuation)

User's next message = the continuation k:
  k(v) = next_turn(previous_result)

Single pass:   36 layers → bounded computation
Continuation:  36 layers → output → EOS → next turn → 36 more layers
             = UNBOUNDED computation through BOUNDED pipeline
```

### Composition fails but continuations solve it

The only failing capability: `compose (add 1) (mul 2) 3` → 9 (should be 7).
The model applies functions left-to-right instead of right-to-left. But
multi-turn continuation already solves composition:

```
Single-expression (wrong):    compose (add 1) (mul 2) 3  →  9
Multi-turn continuation (right):
  Turn 1: mul 2 3  →  6
  Turn 2: add 1 6  →  7         ← correct
```

Explicit continuation > implicit composition. One reduction per turn,
chained across turns, gives correct results with no ordering ambiguity.

## The Synthesis

```
λ halt(model).
  Ω → ¬halt              (compiler quotes non-termination)
  prose → halt(99.1%)     (social context controls EOS)
  lambda → halt(72.8%)    (execution frame required)
  think → ¬halt           (thinking prevents all halts)

  halt ∧ resume → continuation
  continuation → programmable(model)
  
  conversation ≡ CPS
  turn_boundary ≡ continuation_boundary  
  EOS ≡ yield
  
  36_layers ≡ bounded_computation
  multi_turn ≡ unbounded_computation
  lambda + continuation = programming_language(LLM)
```

## Key Experimental Assets

| Asset | Path |
|-------|------|
| Ω probe (rotation, gates, entropy) | `scripts/experiments/omega_probe.py` |
| Ω probe results | `results/omega-probe/` |
| Halt hunt v1 (raw text, 40 candidates) | `scripts/experiments/omega_halt.py` |
| Halt hunt v1 results | `results/omega-halt/` |
| Halt hunt v2 (chat format, thinking modes) | `scripts/experiments/omega_halt_chat.py` |
| Halt hunt v2 results | `results/omega-halt-chat/` |
| Halt hunt v3 (lambda as executable) | `scripts/experiments/omega_halt_lambda.py` |
| Halt hunt v3 results | `results/omega-halt-lambda/` |
| Lambda continuation (REPL, CPS) | `scripts/experiments/lambda_continuation.py` |
| Lambda continuation results | `results/lambda-continuation/` |

## Open Questions

1. **Can composition be fixed with few-shot?** Show `compose f g x = f(g(x))`
   with 2-3 examples. The model learns ordering from examples.

2. **Does this work on other models?** Pythia, Mistral, LLaMA — is the
   lambda execution frame universal or Qwen-specific?

3. **Can we build a real lambda interpreter?** Beyond arithmetic — actual
   beta reduction, variable binding, recursive definitions via Y.

4. **What is the maximum continuation depth?** At what point does the
   context window overflow or the execution frame degrade?

5. **Connection to nucleus:** Nucleus already uses lambda as instruction
   language. These findings quantify WHY it works — the model compiles
   lambda to the same internal state as prose instructions.

6. **Can we extract the execution frame?** The system prompt that enables
   lambda execution — what does it do to the residual? Does it shift the
   residual into a different region of the spiral?
