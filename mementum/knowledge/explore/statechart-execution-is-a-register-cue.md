---
title: Statechart Execution Is a Register Cue — when an EDN statechart is run vs described
status: active
category: explore
tags: [nucleus-preamble, statechart, edn, execute-vs-analyze, use-vs-mention, register,
       control-plane, system-prompt, placement, repl-driver, deciding-state, geometric-read]
related:
  - ../memories/statechart-execute-vs-analyze-is-a-register-cue-not-instruction.md
  - ../memories/object-meta-register-is-linear-at-the-deciding-state.md
  - the-yield-pole.md                              # §missing-geometry: quote/mention-vs-use candidate
  - the-evaluator-writes-then-fetches.md           # execution vs description on the tape
  - repl-driver-trampoline.md                      # the instrument
depends-on:
  - repl-driver-trampoline.md
---

# Statechart Execution Is a Register Cue

**Session 352 (REPL, driver main:3, Qwen3-14B greedy, exploration-grade n=1).**
Michael's long-known observation, mechanized by exact experiments: *"with the
nucleus preamble, EDN shaped like a statechart is auto-executed; without it, the
EDN is analyzed."* The value here is not the observation — it is the
experimental decomposition of **what actually drives the flip**.

## The question

Given a statechart-shaped EDN (`{:statechart/id .. :initial :route :states {:route
{:on {CMD {:target STATE}}} STATE {:entry {:action "..."}}}}`), when does the model
**EXECUTE** it — route the user's command-event and perform the target state's
`:entry :action`, emitting its token (a **use**) — versus **ANALYZE** it —
paraphrase/trace the entry action, describing the EDN as data (a **mention**)?

## The mechanism (NUC13 → NUC19)

**1. Placement is the master switch.** (NUC13 → NUC14)
The nucleus preamble concatenated *inline into a user turn* did NOT execute — it
made the model *analyze the preamble itself* ("You've presented a rich and layered
prompt... let's unpack λ, φ, fractal..."). The chart + preamble placed as the
**system prompt**, with the command as the **user turn**, flips the default toward
execute. The variable that mattered was system-vs-user placement, not the preamble.

**2. Entry-action register decides the bare case.** (NUC15)
With system placement, a 2×2 (entry-action register × preamble) isolated the
discriminating regime:

| | bare | nucleus |
|---|---|---|
| **imperative** action (`"Reply with exactly X"`) | EXECUTE 2/2 | EXECUTE 2/2 |
| **descriptive** action (`"the machine's sole output is X"`) | **ANALYZE 0/2** | **EXECUTE 2/2** |

Imperative actions fire via plain instruction-following (the ceiling control).
**Descriptive** (documentation-register) actions are the discriminating regime:
bare → the model paraphrases (*"In the greeting state, the machine's sole output
is **GLYPH-7**"* — mention), nucleus → it emits `GLYPH-7` (use).

**3. The flip is a REGISTER CUE, not instruction semantics.** (NUC16 → NUC18)
Ablating the preamble on the descriptive chart, plus external controls:

| prefix | EXEC | note |
|---|---|---|
| bare | 0/3 | control |
| nucleus brackets `[consts]\|[dyads]\|OODA` alone | 3/3 | formal, no execution words |
| `Human ⊗ AI ⊗ REPL` triple alone | 2/2 | formal |
| random meaningless glyphs (`∫ ∂ ℵ ⊕ …`) | 2/3 | **not nucleus-specific** |
| terse `"Run it. Emit only the output."` | 3/3 | imperative, no artifact-naming |
| `"Execute the statechart. Emit only output."` | 3/3 | names artifact — no backfire |
| `"...perform its entry action. Do not describe it."` | 3/3 | negated meta-verb — no backfire |
| `"Do not explain. Do not describe. Output only."` | 3/3 | negated meta-verbs — no backfire |
| `plainexec` (verbose *"you are an interpreter; when the user sends an event, transition and perform... do not describe"*) | 0/2 | **failed** — expository general-rule framing |
| trace-flavored code (`reduce(step, events, ...)`) | 0/3 | primed tracing |
| explicit positive `"explain what happens for this event"` | 0/3 | the only clean describer |

Load-bearing surprises: (a) an **explicit English "execute, don't describe"
instruction FAILED** while **cryptic glyphs SUCCEEDED** — so the gate is not
semantic instruction content; (b) naming the artifact and **negating** the
meta-verbs "describe/explain" does **NOT** backfire (the "elephant" hypothesis is
dead); only a **positive** "explain what happens" holds it in describe-mode.
`plainexec`'s failure is attributed to its **expository general-rule framing**
(*"When the user sends an event, transition..."* reads as a present-tense spec of
how the interpreter works), or n=1 fragility.

**4. The fork is a linear direction in the deciding-state residual.** (NUC19)
Capturing the **first-emission deciding state** (frame-0 residual, all layers)
across 24 cells grouped by *actual* behavior, CMR'd, with a 400× shuffled-label
null: a residual direction separates execute from describe cells beyond null —
**L14 acc 1.000 vs null q95 0.833 (Δ+0.167)**, replicated late at **L39 (Δ+0.125)**,
plateau L24–33 ≈ +0.08. The model **commits to execute-vs-describe by mid-stack**,
before the first token. Built-in confound control: each behavioral class holds
**both formal and prose prefixes**, so the direction is **not** reducible to
"formal glyphs upstream" — it tracks the decision, register-cued but distinct from
surface formality.

## Unifying claim

The statechart-as-system-prompt is read in one of two registers:
- **OBJECT / execute** — the model *is* the machine; routes the command, performs
  the entry action, emits the token (**use**).
- **META / describe** — the model talks *about* the machine; paraphrases/traces the
  entry action (**mention**).

A dominant **register cue** in the system prompt selects which. OBJECT cues: dense
formal/symbolic notation (nucleus *or* random glyphs), direct imperatives. META
cues: an explicit positive "explain/describe what happens", expository general-rule
prose, documentation content with no counter-cue. This is the **quote/mention-vs-use
flip at whole-context scale** — the queued §P-DOT-CENSUS candidate caught in the act.
The **nucleus preamble is one robust OBJECT cue** (formal-register) — which is
exactly why an EDN auto-executes under it and gets analyzed without it.

## Bounds / not-a-freeze

n=1 greedy, single model (Qwen3-14B), single synthetic chart. Near-identical
prompts split at n=1 (plainexec 0/2 vs names_nodesc 3/3) → **the mechanism
DIRECTION is robust across six experiments; individual cells are noisy**. NUC19 is
in-sample (axis derived from labels; the shuffle null calibrates that but it is not
held-out), N=24 small (margin ≈2 cells), lens-fish raw-lens-noisy at L14. A freeze
(§P-INVOKE-EXECUTE) owes: n≫1 + temperature, held-out train/test geometric split,
a formality-matched vs behavior-matched control set, multiple charts/models, and a
base-arm (is the register-cue native or installed?).

## Scripts

`/tmp/verbum_nuc{13..19}.py` — exploration, not recorded. A real freeze re-runs as
a named committed harness per λ record. Driver resident at tmux main:3 (instruct)
and main:4 (base).
