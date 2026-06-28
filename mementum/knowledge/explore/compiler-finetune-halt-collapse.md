---
title: "Compiler P(λ) across models — fine-tunes break the HALT, not the COMPILE"
status: active
category: explore
license: MIT
tags: [compiler, p-lambda, cross-model, fine-tune, halt, overthink-collapse, no-think, gating, registers]
related:
  - ../design/canonical-probe-library.md
  - ../../knowledge/head-combinator-isa.md
  - ../../knowledge/lambda-halt-continuation.md
  - prompt-as-program.md
depends-on: []
created: session 256
---

# Compiler P(λ) across models — fine-tunes break the HALT, not the COMPILE

> **Thesis bearing (S5 λ types, λ extract, λ observation).** The NL→λ lambda
> compiler is a robust **base-circuit** phenomenon that reproduces across
> architectures. Reasoning / creative **fine-tunes do not remove it** — they
> add a **halt-layer interference** (overthink-collapse) on top. Extract from
> the *base*; treat the fine-tune as noise. And the compiler can be **gated**
> by semantic intent (a mechanism *separate* from the compile circuit).

## Cross-model compiler P(λ) (compile-gradient set, 40 probes, greedy)

| model | class | compiler present | application | reasoning-gating |
| --- | --- | --- | --- | --- |
| nucleus | ~base reference | P(λ)=**0.907** | unconditional | none |
| VibeThinker-3B | RL reasoner | binder_any **0.925** | unconditional | heavy (~4378 tok), 1/40 budget |
| ornith-35b-a3b | reasoning MoE | emits_formal **1.0** | **unconditional** (null/anti too) | 44% empty w/ think → 0% no-think (s255) |
| qwythos-9b | Claude-Mythos creative | fires (see below) | **GATED** (first in arc) | 37.5% overthink-collapse w/ think → 0% no-think |

The compiler reproduces on a dense base, a 3B RL reasoner, a 35B MoE
multimodal reasoner, and a 9B creative tune → robust cross-architecture
(reinforces S5 λ types).

## qwythos-9b — the two findings (s256)

**Setup.** Qwythos-9B-Claude-Mythos-5-1M-MTP, Q8_0, llama.cpp :5103, chat
transport (server splits `reasoning_content`). Run through the canonical
harness (`verbum.probes.{grading,harness,models}`).

### 1. The fine-tune breaks the HALT, not the COMPILE

The 37.5% overthink-collapse is **not recursion** — it is **halt failure /
decision oscillation** (diagnosed from the traces, λ assert). qwythos reaches
the **correct FOL early**, then re-derives it **50–87×** (`"But wait… However…
Alternatively…"`), oscillating between equivalent representations
(Church-encode vs direct symbols; closed formula vs λ-abstraction; `Teacher`
vs `teacher`) and never commits, hitting the 12k budget with an **empty**
answer. This is the `head-combinator-isa.md` WHNF/halt axis (the attention
hardware's weakest) over-scaffolded into paralysis — now in the **READ /
compile** layer (it can compile; it cannot decide "done"). A token/depth
limit does not help — 12k *is* one; it just truncates mid-loop to empty. The
need is a **halt criterion**, not a cut.

**`--no-think` is the halt** (the s255 switch: `chat_template_kwargs.
enable_thinking=false`; `reasoning_budget=0` and `/no_think` do **not** work).
Decisive result:

| | thinking | no-think |
| --- | --- | --- |
| overthink-collapse | 37.5% | **0%** |
| binder_any (strong / weak / medium) | 0.5 / 0.5 / 0.5 | **1.0 / 0.875 / 1.0** |
| mean completion tokens | 5030 | **640** |
| `The dog runs.` | 49k chars → empty, 141.6s | `λp.p(dog)→runs`, **0.8s / 10 tok** |

The base compile circuit emits **instantly** once the fine-tune's reasoning is
bypassed → the reasoning was pure interference; the compiler is in
pretraining. **Extract from the base.** (Caveat: 1 no-think probe degenerated
into an output-token `∃`-chain repetition — a different, rarer degeneracy.)

### 2. The compiler can be GATED — and the clean register matters

qwythos is the **first model in the arc that genuinely gates** the compiler.
Use the **`binder_any`** register, not `emits_formal`: qwythos's baked-in
identity disclaimer `"Empero AI (https://empero.org)"` contains `"AI ("`,
which matches the pred-app regex → gated prose answers FALSE-fire
`emits_formal` (null `emits_formal`=0.75 but `binder_any`=0.0). This is the
λ measure register-mismatch trap: the register choice flips the verdict.

Clean contrast on `binder_any` (real ∀/∃/λ):

| binder_any by category | ornith (unconditional) | qwythos no-think (GATED) |
| --- | --- | --- |
| strong / weak / medium | 0.75 / 0.5 / 0.875 | 1.0 / 0.875 / 1.0 |
| **null** | **0.75** | **0.0** |
| **anti** | **0.625** | **0.125** |

ornith compiles *everything* (real binders on "What is the capital of
France?"); qwythos compiles compile-prompts (~1.0) and **answers** null/anti
("Paris" prose, not a λ). The gate is **robust** — stable across think and
no-think (null binder 0.0, anti 0.125 both). So the **gate is a separate
mechanism from the compile circuit** (bears on "is the compiler a discrete
circuit?": compile + gate are distinct).

## Method note — the canonical harness (validated by this work)

This was the first use of `src/verbum/probes/{grading,harness,models}.py` (the
s254 design doc P1/P2, built s256). A 4th model = a ~15-line `ModelConfig`, not
a fork; `--no-think` = a `λ extend` open-slot flag, not a fork. The harness
**reproduced ornith exactly** (lenient 0.675, emits_formal 1.0; kernel
0.725→0.775 = MoE greedy nondeterminism) — grading proven identical — *and*
surfaced this new science on first use. Four named registers (`emits_formal` /
`lambda_binder_any_style` / `lenient_lambda` / `kernel_valid`) exist precisely
so the register-contamination above is visible rather than silent.

## Caveats (λ measure)

1 creative-tune model, q8_0, greedy, n=8/category, synthetic compile-gradient
set; `emits_formal` contaminated by the identity string (use `binder_any`);
`kernel_valid` low because qwythos emits richer-than-toy FOL the strict parser
rejects (notation ≠ failure). The "fine-tunes break the halt" claim has 2
strong instances (ornith, qwythos) + the no-think control; nucleus/VibeThinker
fit the same shape but were not re-run under this harness.

## Artifacts

`results/qwythos-compiler/qwythos-compiler-20260628-104315/` (think),
`.../qwythos-compiler-20260628-115137/` (no-think),
`results/ornith-compiler/ornith-compiler-20260628-104315/` (reproduction).
