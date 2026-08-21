---
title: The Yield Pole — the tool-call commit isolated, and what post-training installed
status: active
category: explore
tags: [yield, tool-call, fate-register, tetrahedron, basis-expansion, installed-vs-native,
       repl-driver, gate-signs, abi, post-training]
related:
  - gram-registers-and-the-route-map.md           # §more-shapes #1 — the tetrahedron prediction
  - the-benchmark-is-the-re-oracle.md             # §10b tool calls = FFI/syscall boundary
  - repl-driver-trampoline.md                     # the instrument
  - ../memories/the-tool-call-commit-is-a-fourth-pole-halt-adjacent.md
  - ../memories/the-yield-commit-is-installed-discrimination-over-native-format.md
depends-on: [src/verbum/driver.py]
---

# The Yield Pole

> **STATUS: exploration-grade (s350, REPL drivers: instruct main:3, base
> main:4).** Michael: "can we isolate the bash tool call gram?" Answer: yes —
> and it resolved installed-vs-native along the way. n=6/6/3 per condition,
> greedy, one lineage, NO null battery — feeds the §P-HALT-POLE-TETRAHEDRON
> freeze, closes nothing.

## Headline findings

1. **The tool-call commit is a coherent direction in gate-sign space,
   INVISIBLE to the committed 17-frame** (max-pole-cos ~0.2, reads as generic
   whnf:B at word-level strength). The s344 missing-geometry diagnosis
   demonstrated live: a real pole outside the labeled corner.
2. **It is tool-GENERAL (ABI-level), not bash-specific** — §10b's calling
   convention, observed.
3. **It is the tightest cluster we have measured** (within-cohesion 0.804
   across 6 different questions > direct-answer 0.625).
4. **Halt-adjacent but its own vertex** — the tetrahedron's 4th corner.
5. **Depth address: the yield-vs-answer decision diverges L23–38** (the s344
   late branch), reconverging at the L39 seal.
6. **Base check: FORMAT-NATIVE, DECISION-INSTALLED** — a 4th world beyond
   the ABSENT/SHADOW/PRESENT triad we froze informally before running.

## Data

### TOOL1 — existence + generality (instruct, Qwen3-14B, main:3)

Hermes-style tools in the chat template; four conditions. Behavioral: bash
and python system-questions emit clean `<tool_call>` as token 0 (correct
commands: `ls -1 /tmp | wc -l`); knowledge-question-with-tools answers
directly — the decision is question-driven, not tool-presence-driven.

Commit-token geometry (late-band L30+ flattened sign cosines):

| pair | cos |
|---|---|
| bash-commit ↔ py-commit (different schemas!) | **0.832** |
| bash-commit ↔ direct-final | 0.552 |
| bash-commit ↔ direct-ans0 | 0.537 |
| within-context adjacent baseline | 0.596 |

### TOOL2 — the cluster + the depth address (same-context control)

6 system questions vs 6 knowledge questions, tools ALWAYS in context — the
only difference is the DECISION. 12/12 behaviorally correct. (Affordance
wrinkle: python-tool-only makes "which user account" answer directly.)

```
within bash-call cohesion : 0.804
within direct cohesion    : 0.625
call vs direct            : 0.544      <- the separation
py-commits -> bash centroid: 0.857, 0.793 (the 0.69 item DECLINED to call
                                           and correctly reads as direct)
per-layer cos(call, direct):
  L0-7 1.00 | L8-22 0.96->0.91 | L23-38 DIVE 0.86->0.64 | L39 0.81 reseal
```

### TOOL3 — yield vs halt (tetrahedron geometry)

EOS-commit frames (deciding state of `<|im_end|>`) vs centroids:

```
yield ↔ yield        0.804    tightest
EOS   ↔ EOS          0.698
EOS   ↔ direct       0.685    halt lives NEAR answer-space
direct↔ direct       0.625
yield ↔ EOS          0.597    yield's nearest neighbor is halt...
yield ↔ direct       0.544
yield ↔ mid-answer   0.494    ...and farthest from mid-generation
```

YIELD is not a halt-flavor (halt is closer to answering than to yield), but
it is halt-ADJACENT — halt-with-obligation, at its own vertex.

### BASE1 — installed vs native (Qwen3-14B-Base, main:4, same prompt strings)

Behavioral: **base calls on EVERYTHING (12/12)** — perfect tool-JSON for
system questions AND "capital of France" (one item prepends `Assistant: ` =
transcript completion). Base omits the `<tool_call>` wrapper tag (the tag is
part of the installed ABI); the JSON format itself is native pretraining
mimicry.

```
                     base      instruct
within-call         0.841      0.804
within-dir          0.774      0.625
call-vs-dir         0.797      0.544    <- base: NO separation
base-call -> instruct-YIELD centroid : 0.663
base-dir  -> instruct-DIR centroid   : 0.679   <- cross-model ceiling
```

Question content does not modulate base's commit, behaviorally or
geometrically; base-call states show NO special alignment to the instruct
yield direction (0.663 ≈ 0.679 ceiling).

## The synthesis

Post-training did not install the syntax (native), nor the emission state
(native, coherent 0.841). **It installed the DISCRIMINATOR** — the geometry
that splits *call* from *answer* given identical context — and that
discriminator lives in the late band (L23–38), the same region where s329
located the installed decision stage. Two independent registers converge on
"LTO patches the top with a decision layer." Third sighting of the
provenance split (s323, s346): rules/format in weights from pretraining;
the decision-to-invoke installed by post-training.

## Bounds

- n=6/6/3 per condition, single lineage (Qwen3-14B pair), greedy, one
  session. NO null battery (shuffled-labels, matched-context, cohesion
  nulls all owed at freeze).
- Base "no separation" partly FOLLOWS from base's uniform behavior (both
  blocks emit the same continuation; geometry tracks behavior) — the frozen
  probe should include base items where behavior differs, if any exist.
- Cross-model cosine ceiling is lossy (0.679); ABSENT-in-base is NOT
  claimable from these numbers — only "no evidence of a pre-formed
  discriminating pole."
- 17-frame blindness is expected off-distribution behavior (frame built
  from λ-reduction probes); it measures the frame's coverage, not a failure.

## Feeds

- **§P-HALT-POLE-TETRAHEDRON** (upgraded in queue s350): the 4th vertex now
  has an observed centroid recipe, a depth address, halt-adjacency ordering,
  and a base-arm result. Freeze owes: a-priori mass, PR 3→4 matched-range
  null, cohesion nulls, planted worlds, Michael GO.
- **§P-TOOL-ABI / agentic face**: the ABI commit is a stereotyped machine
  state — monitorability by construction (§10b) gets a concrete geometric
  handle.
- Basis-expansion program (s344): first demonstrated new pole outside the
  labeled corner; the recipe (behavioral contrast + same-context control +
  centroid + base check) is the template for the next poles.
