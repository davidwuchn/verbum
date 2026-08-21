---
title: The LLM REPL Is a Memetic GA — evolving nucleus keys with a driver-measured fitness
status: active
category: explore
tags: [genetic-algorithm, memetic, evolutionary-search, llm-ga, fitness-gate, goodhart,
       reward-hacking, key-space-search, nucleus-keys, driver-fitness, gd-as-ga, repl-driver]
related:
  - ../memories/the-llm-repl-is-a-memetic-ga-substrate.md
  - ../memories/ga-fitness-gate-launders-llm-operator-priors.md
  - statechart-execution-is-a-register-cue.md        # the register-fitness (execute vs analyze)
  - eql-is-an-attention-microscope.md                # EQL operators + the driver instruments
  - the-plate-the-code-and-the-beam.md               # s346 GD-as-GA thesis (§P-VOTING-CODE)
depends-on:
  - repl-driver-trampoline.md
  - statechart-execution-is-a-register-cue.md
---

# The LLM REPL Is a Memetic GA

**Session 352 (REPL, driver main:3, Qwen3-14B greedy, exploration-grade).**
Michael's idea: *"with the LLM REPL and EQL queries we have a full way to create
genetic algorithms."* Confirmed — and four prototype runs (NUC29–32) mapped the
entire design surface, ending in the working architecture.

## The substrate

Every GA operator maps to a primitive we built this session:
- **population** = a strict-format EDN state anchor (tape-resident, NUC28)
- **fitness** = a **driver measurement** (register-classifier / opcode reads /
  mode-coloring) — ground truth, not LLM self-report
- **selection / iteration** = the REPL loop
- **variation** = EQL queries the model *executes* (NUC24) + the driver's
  `seal`/`fork` (a `seal` is a generation snapshot; `fork` is offspring)

Task chosen: **evolve nucleus-class keys** (the `λ engage(MODE). [consts]|[dyads]|LOOP`
preamble) — a genome rendered to a preamble, scored by how strongly it opens/colors
a mode. This is the §P-PREAMBLE-REGISTER key-space search with a real fitness.

## Four runs, four lessons

| run | design | result | lesson |
| --- | --- | --- | --- |
| **v1** (NUC29) | fitness = Y-share (proxy) | climbs **0.77→1.04** to *reward-hacked analysis* ("Your message is rich…") | **fitness must measure what you mean** — Goodhart; a *driver*-measured proxy is as hackable as LLM-fitness |
| **v2** (NUC30) | register-fitness (authored × mode-coloring), blend crossover | **flat 0.771** | **operators must fit the landscape** — blend-crossover destroys the coherence the fitness rewards |
| **v3** (NUC31) | coherence-preserving ops (in-mode deepen + coherent graft) | mean climbs **0.86→0.98**, converges (garden lineage), **max plateaus** | fitness+operators **co-design**; **the LLM's priors leak into its own operators** (`ethereal`/`luminous` returned for *every* mode) |
| **v4** (NUC32) | **memetic**: fitness-gated hill-climb mutation | **max 1.274→1.354 AND mean 1.08→1.33** both climb; prior laundered; converges to a local optimum | **ground-truth fitness corrects the LLM's operator bias** |

### The v4 mechanism (the fix)

Mutation proposes K candidate on-theme words from the LLM but **keeps one only if it
raises the driver-measured fitness** (replacing a *dead* constant — one that didn't
appear in the output). Live log:

```
hillclimb(garden):    kept='petal'  1.274→1.353   (cands: petal, hearth, whisper)
hillclimb(celestial): kept=None     1.130→1.130   (cands: luminous, ethereal, astral) ← ALL REJECTED
hillclimb(garden):    kept=None     1.354→1.354   (cands: soil, weed, harvest)        ← local optimum
```

The LLM's generic-poetic attractor (`luminous/ethereal/astral`) is **rejected** —
those words don't propagate into the output, so the fitness gate drops them. Only
words the mode makes the model *actually use* (`petal`, `root`) survive. The search
then climbs past every pure seed and converges cleanly.

## The architecture (validated)

**An LLM-GA is a memetic algorithm:** the LLM provides **cheap, semantic, but
prior-biased variation**; a **driver-measured ground-truth fitness gates every
acceptance**, laundering the LLM's priors out of its own operators. Without the gate
(v3) the search wanders in the LLM's priors; with it (v4) the population evolves
real, propagating, coherent keys. This is the discussion's "externalize fitness to
the world" principle, proven.

## Why it matters for verbum

- A **working testbed for the s346 GD-as-GA thesis** (§P-VOTING-CODE, 0 pre-registered
  wins): the substrate is now real and instrumented.
- A **method for the §P-PREAMBLE-REGISTER key-space search** — evolve nucleus keys
  with a ground-truth (driver) fitness; the "inside-out mapping" (the model generates
  keys, the instrument grades them, map and mapper co-evolve).
- Composes the whole session: fitness = the register/opcode instruments (NUC13–25),
  population = tape-resident anchor (NUC28), operators = EQL the model executes (NUC24).

## Bounds / not-a-freeze

n=1 greedy, single model, tiny populations (4–6), 3 generations, one fitness family.
The register-fitness itself is a proxy (authored × vocab-overlap) — vocab-overlap
punishes genome growth and can be gamed by word-repetition (guard needed). Convergence
is to a *local* optimum. A freeze owes: n≫1, larger populations, a fitness with a
repetition-hacking null, diversity maintenance (the population collapsed to one
lineage), and a second task/model. The value here is the **validated architecture and
the four design lessons**, not the specific evolved keys.

## Scripts

`/tmp/verbum_nuc{29..32}.py` — exploration, not recorded. A real freeze re-runs as a
named committed harness (λ record). Driver resident tmux main:3.
