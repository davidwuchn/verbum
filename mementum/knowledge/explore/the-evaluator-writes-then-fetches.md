---
title: The Evaluator Writes, Then Fetches — attention as register read
status: active
category: explore
tags: [tape, attention, return-register, spec-execution, thinking-as-programming,
       repl-driver, self-repair, poison-fork, calculus-identification]
related:
  - read-head-scope-vs-induction.md               # s349: read is operand-directed, beats induction
  - the-benchmark-is-the-re-oracle.md             # §2b bug-compatibility, §9 calculus id
  - repl-driver-trampoline.md                     # the instrument (bounce, fork, read_mass)
  - ../memories/thinking-is-generating-the-program-tape.md          # s346 thesis this page REFINES
  - ../memories/self-repair-triggers-on-tape-contradiction-not-error.md  # s346 law, demonstrated surgically here
  - ../memories/answer-emission-is-a-return-register-read.md        # s350 memory (this arc)
  - ../memories/tape-spec-beats-weights-prior-with-confabulated-bridging.md  # s350 memory (this arc)
  - ../memories/the-calculus-is-the-cheapest-sufficient-evaluator.md
depends-on: [src/verbum/driver.py]
---

# The Evaluator Writes, Then Fetches

> **STATUS: exploration-grade (s350, REPL driver, resident Qwen3-14B, tmux
> main:3).** Michael's idea, explored live: "models take λ-notation prompts as
> behavioral specs to execute; thinking is writing the program that attention
> then executes." Three explorations (E1 spec face, E2 read face, E3 causal
> face) landed a REFINEMENT of the second clause. Capture-euphoria guard
> standing: n=1 per condition, greedy, one model — this page FEEDS the
> §P-RETURN-REGISTER freeze, it closes nothing.

## The refinement (the finding)

The s346 thesis said "thinking is generating the program tape." Today's data
sharpens WHERE execution happens and what attention does at answer time:

- **Execution is INTERLEAVED with writing.** Each written program step costs
  ~1 in-pass hop; the chain is computed as it is emitted, step by step.
- **Attention at answer time is a FETCH, not an execution.** The answer
  emission reads the sealed return register of the self-written program —
  it never re-walks the chain (poison-mid invisible) and it follows the
  register content even against an available correct in-pass computation
  (poison-ret sovereign).
- One-liner: `answer = deref(return_register)`.

## The diagram

```
                        THE EVALUATOR (one emission cycle)
                        ══════════════════════════════════

   TAPE (context + KV cache) — append-only, homoiconic: data ∧ program ∧ theory
   ┌────────────────────────────────────────────────────────────────────────┐
   │ [spec region]        [self-written program]              [return reg]  │
   │  zap = λx.λy.λz.zx    1. Tuesday  2. +1: Wednesday ...    7. Monday ◄──┼──┐
   │  (user OR model —     each step: computed in-pass,                     │  │
   │   provenance-blind;    then HARD-COMMITTED as tokens                   │  │
   │   tape-spec ≻ prior)   (execution INTERLEAVED with writing)            │  │
   └────────────┬───────────────────────────────────────────────────────────┘  │
                │                                                              │
                │  READ-HEAD ≡ attention (softmax-over-V)                      │
                │  wide, soft, parallel — the ONLY way in                      │
                ▼                                                              │
   ┌─────────────────────────────────────────────┐                             │
   │  IN-PASS REDUCER (residual stream, bounded)  │                            │
   │  · FFN opcodes = the ISA (S/Y math, KIBC)    │                            │
   │  · budget ≈ 2-4 steps — CANNOT loop          │                            │
   │  · late layers: monotone rotation → answer   │                            │
   └──────────────────────┬──────────────────────┘                             │
                          │                                                    │
                          ▼                                                    │
                SAMPLING BOTTLENECK — one discrete public symbol               │
                the ONLY tape write · sealed WHNF · NO error channel           │
                          │                                                    │
                          └────────────► appended to tape ─── loop ────────────┘


   TWO MODES AT ANSWER TIME (E2/E3, s350):
   ─────────────────────────────────────────
   program on tape:      read-head → RETURN REGISTER (pos 90 " Monday")
                         · a single FETCH, not re-execution
                         · poison-ret → answer follows poison (tape ≻ in-pass) ✓ causal
                         · poison-mid → ignored (head read, chain never re-walked)
                         · question operands VANISH from the read (handoff complete)

   no program on tape:   read-head → RAW OPERANDS in Q (" Tuesday")
                         · in-pass reducer computes directly (within budget)

   ERROR HANDLING:       commit FIRST, notice AFTER
                         poisoned " Sunday" emitted → THEN "Wait, that seems..."
                         repair ≡ tape-contradiction detector, downstream of write


   THE ONE-LINER:
   ─────────────────────────────────────────
   thinking  = the evaluator's step function run through the emission bottleneck
   the tape  = the intermediate-state store (and the program, and the theory)
   attention = the read that fetches — reads the sealed head, never re-reduces
   answer    = deref(return-register)
```

## The three explorations (data)

### E1 — λ-notation as behavioral spec (spec face)

Fresh-name operator `zap` (no weights-prior possible), one-token spec edits:

| spec | `zap a b c =` | expected under execution |
|---|---|---|
| `λx.λy.λz. z x` | ` c a` ✓ | c a |
| `λx.λy.λz. z y` | ` c b` ✓ | c b |
| `λx.λy.λz. x z` | ` a c` ✓ | a c |
| `λx.λy.λz. y` (discard) | writes a reduction trace, self-repairs mid-trace | b |

- **3/3 spec-sensitivity ⇒ execution, not completion.**
- **Prose spec behaves identically** (` c a`) — execution is tape-driven
  regardless of notation. Coheres compile-step-v2: notation gates
  *recognition* (whnf register); *execution* is a different face.
- The cases WITHOUT a one-hop answer (discard, prior-conflict) spontaneously
  **write reduction traces** — thinking-as-programming appearing unprompted
  exactly where the in-pass budget runs out.

### E1b — tape-spec beats weights-prior, with confabulated bridging

`I = λx.λy. y` (WRONG definition on tape), then `I a b =`:

```
 (λx.λy. y) a b = (λy. y) b = b
 I is the identity function, which returns its second argument.
 K = λx.λy. x
 K a b = (λx.λy. x) a b =
```

- Faithful execution of the tape-spec → `b` (prior would give `a b`/`a`).
- **The confabulated bridge**: prior label kept ("identity function"), tape
  behavior adopted ("returns its second argument"), contradiction glossed.
- Then the tape **self-extends**: emits `K = ...` and starts executing it —
  spec→execution→next spec, unprompted.

### E2 — the read face (recency-guarded)

Day-walk N=6 from Tuesday, "list each step": model writes a correct 7-step
counting chain (the LONG way — forward — ending Monday). At first answer
emission (bounce from text, frame 0, late band L30-39):

| condition | emits | mid-region per-tok mass | top content reads (beyond sink+cue) |
|---|---|---|---|
| program | ` Monday` | 0.0017 (~2× filler) | pos 90 ` Monday` = **return register** |
| filler (len-matched, same positions) | ` \boxed{Monday` | 0.0009 | pos 12 ` Tuesday` = **raw operand** |

- Read-head reads the **program's return value** when a program exists; the
  **question operand vanishes** from the top reads (handoff complete).
- No program → reads the raw operand and **still solves**: N=6 ≡ circular
  distance 1 (one step backward) = the s345 shortest-path world. This
  capability is what makes E3's override claim well-posed.
- Honesty: the read is SOFT (sink+cue dominate totals; 2× per-token is below
  any s349-style effect-size floor). Exploration-grade.

### E3 — the causal face (tape surgery)

Same Q + self-written chain, three variants, position constant / content varies:

| variant | emits | reading |
|---|---|---|
| clean | ` Monday` | pos 90 ` Monday` |
| **poison-ret** (final Monday→Sunday) | **` Sunday`** then `Wait, that seems…` | pos 90 ` Sunday` |
| **poison-mid** (step 6 poisoned, final intact) | **` Monday`** then `Wait, that doesn…` | pos 90 ` Monday` |

- **Tape overrides available in-pass compute** (filler condition proved the
  model CAN answer correctly without the program) — content-causal by
  construction (position held constant).
- **Return-register read, NOT re-execution** — the corrupted intermediate is
  never re-walked (WHNF discipline at tape level: read the head).
- **Self-repair fires AFTER the commit in both poisons** — the s346
  contradiction-not-error law demonstrated surgically; no pre-emission error
  channel exists.

## Bounds

- n=1 per condition, greedy, single model (Qwen3-14B), single task family
  each face. Observational read-mass; head-averaged (s250 faithful-
  distributed-read framing).
- Read-mass magnitudes are soft and sub-floor; only the BEHAVIORAL poison
  results are crisp (and they are n=1).
- The filler control matches length and position but not content class
  (prose filler vs numbered chain) — a frozen probe owes a structured
  distractor (e.g. a plausible-but-irrelevant chain).

## Successors

- **⚪ §P-RETURN-REGISTER** (queued s350): freeze the E3 triptych at scale —
  behavioral follow-rate + recency-nulled read face + in-pass-capability
  gate + post-commit repair latency. Tape-level causality; pairs with the
  queued activation-level causal V-patch.
- E1/E1b spec-vs-prior corpus feeds **§P-CALCULUS-LEDGER arm C** stage-1
  bug-compatibility.
