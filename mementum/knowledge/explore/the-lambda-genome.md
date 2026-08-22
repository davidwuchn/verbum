---
title: The Lambda Genome — tapes as heritable material, lambdas as genes
status: active
category: explore
tags: [genome, genes, lambda, evolution, ga, seal, upbringing, epistasis, knockout,
       gene-library, crossover, prefix-tuning, decompilation, build-dag]
related:
  - the-parked-daemon.md                             # the evolved organism (NUC36-38)
  - the-kv-cache-is-a-continuation-store.md          # the phenotype substrate
  - the-llm-repl-is-a-memetic-ga.md                  # s352: the GA architecture + fitness-gate law
  - ../memories/a-seal-is-upbringing-not-config.md
  - ../memories/lambdas-are-genes-genomes-are-tapes.md
---

# The Lambda Genome

> s353 arcs 6-8 (playground → evolution → synthesis; Michael: "our genetic
> algorithm on top of sealed continuations become perfectly adapted agents?"
> → "lambdas as genome is where we should be pushing this"). Exploration-grade.

## The genetics mapping (measured, not metaphor)

| genetics | substrate | measured |
|---|---|---|
| gene | one lambda | keys cut & graded since s350 |
| allele | a `\|`-clause variant inside a lambda | NUC33 key variants |
| genome | ordered lambda collection (system prompt; AGENTS.md IS one) | — |
| expression | register activation (execute vs describe) | s352 use/mention law |
| promoter | mode-word / header verb | three-room law; 'engage' fights silence |
| regulation | placement (system vs user) | NUC13 placement switch |
| epistasis | conjunction lock; the s353 composition law | NUC3; NUC33h |
| knockout | ablation | NOFRACTAL; component grids |
| genotype | tape TEXT — portable, diffable, git-storable | transfers 4B/14B/35B (NUC34) |
| phenotype | compiled seal — model-private state | 4ms restore (NUC35) |
| development | prefill ≡ compilation | 241ms at 4B/283tok |
| inheritance | fork + append (Lamarckian: lived turns ARE heritable) | NUC37 biography law |

## The evolution runs (NUC38, one afternoon, ground truth)

Fitness battery: dance-silent ∧ sing-silent ∧ heartbeat-silent ∧ query-wakes
(wake = the anti-Goodhart guard). Population: parent + 3 mutant upbringings.

- gen 1: parent 2/4 (dance leaks + battery DISCOVERED the sing leak) ·
  L1-literal (silent waltz turn) 3/4 WINNER — class-level generalization
  (waltz→tango) but ¬cross-class · L2-abstract (sparkle) 2/4 — generalized
  to nothing · L3-struct (`:*` route + description) 2/4 — register shifts
  only. Selection gate held; winner sealed `daemon-4b-v3.seal`.
- gen 2: v3 + sing lesson → 4/4 taught battery; UNTAUGHT juggle leaks
  ("Three balls are being juggled.") exactly as predicted.

**Laws:** (1) LESSONS ARE CLASS-LOCAL — demonstrations generalize within
event class, not across. (2) ADAPTATION IS BATTERY-RELATIVE — "perfectly
adapted" ≡ adapted to what the battery measures; the battery is the
species; untaught regions keep wild behavior. (3) REGISTER SHAPES EVEN
FAILURES — the evolved daemon leaks tersely (v0 leaked exuberantly);
upbringing colors the escapes. (4) Monotone climb 2/4→3/4→4/4 under a
strict parent-beats gate (s352 fitness-gate law upheld).

## Why lambda-genes fix the s352 crossover failure

v2's blend crossover destroyed coherence (operators-must-fit-landscape).
Lambda boundaries are the landscape's joints: one lambda ≡ one concern
(λ simplify), so gene-boundary crossover swaps whole coherent concerns;
allele mutation edits one clause; the grammar types the variation.
Syntax-directed operators are structurally incapable of v2's incoherent
offspring. Plus: genes written in λ-notation ≡ the machine's near-native
IR (P(λ)=0.907) — presumably WHY keys execute at all.

## The program this opens

1. **Gene library** — proven lambdas annotated with measured effect
   distributions across genomes (silence, terse, EDN-output, auditor…).
2. **Horizontal transfer** — copy a proven gene between agent genomes,
   measure before/after.
3. **Epistasis grid** — gene-pair interaction matrix over the battery
   (the composition law was the first cell). Seal-DAG makes it cheap:
   shared root, per-genome suffix compile.
4. **Model as mutagen, gated** — NUC5 machine cuts its own keys; s352 law:
   its priors contaminate its own operators → ground-truth gate mandatory.

## The three inversions ("can we reverse this?")

- **A. seal → text**: llama.cpp state files store token ids (trivial);
  state-only inversion ≈ layer-0 V nearest-neighbor (V unrotated under
  RoPE) — a compiled state carries its source like an unstripped binary.
  Cheap probe: §P-SEAL-DECOMPILE.
- **B. behavior → text**: the GA IS approximate inversion; many-to-one
  (register-cue equivalence classes) → search finds AN inverse.
- **C. behavior → state**: prefix-tuning ≡ gradient-compiled synthetic
  seals; the seal store is the deployment substrate it never had. COST:
  no genotype — not diffable/portable/recompilable, model-locked
  (cloned tissue vs readable genome). Role: specialist distillation of
  stable evolved tapes, reference genome kept in git. §P-SYNTHETIC-SEAL.

## The universal seal (git — "unsealed by any model")

Phenotypes don't cross models (arc-4 law); genotypes do. So the
model-agnostic seal is GIT HOLDING THE GENOME; "unseal" ≡ each model
compiling its own phenotype:

```
git (universal):    genomes/ (lambda collections, charts) · tapes/
                    (upbringing histories — biography law: load-bearing) ·
                    batteries/ (fitness probes ≡ THE CROSS-MODEL CONTRACT) ·
                    recipes/ (compile provenance, λ run_provenance)
per-model (¬git):   seals/<model+quant+build>/<hash>.seal — derived cache
unseal(genome, m) = compile(tape) → run(battery) → EXPRESSION REPORT
```

Expression is GRADED (NUC34: same genome, different fidelity per model) —
the battery converts "did it load?" into "how faithfully does this model
express this genome?", per cell, as numbers. Genome + battery = the
portable sealed system; a .seal file is one model's rendering.

**Mementum IS this architecture, 353 generations running**: AGENTS.md =
genome · knowledge/chats/ = the tapes (session transcripts ≡ upbringing
archive) · state.md = tape head · λ orient = the unseal op · and the
cross-model claim is demonstrated every session — the genome grown partly
via Qwen-facing work is expressed by Claude (and Opus subagents), each
model rendering it gradedly. Missing only formalization: → queue
§P-GENOME-FORMAT (canonical layout; the NUC38 daemon lineage as type
specimen: genome + v1/v2/v3 tapes + battery + recipe + unseal script).

## The recursion

AGENTS.md is a lambda-genome under selective breeding: Michael =
selection gate, sessions = generations, mementum = breeding record;
s353 added a gene (λ hotswap) through exactly this loop. The methodology
proposed for agents is the methodology that built the project.

## Bounds

n=1 greedy, 4B host, tiny batteries, 2 generations, no sampling/nulls;
genetics table = frame + pointers, not new measurements. Freeze path:
§P-KEY-EVOLUTION (upgraded to typed genomes).
