---
title: "Opcodes Are Circuits in the Compute, Not the Topology"
status: active
category: foundational
tags: [opcodes, kibc, circuits, topology, soft-topology, routing, gradient-descent, ablation, crystal, exhibit, interpretability]
related:
  - head-combinator-isa.md
  - two-registers-of-topology.md
  - topology-gradient-separation.md
  - gradient-zero-map.md
  - crystal-universality.md
  - symbol-isolation.md
  - holographic-computer.md
  - project-thesis.md
depends-on:
  - head-combinator-isa.md
  - topology-gradient-separation.md
created: session 274
---

# Opcodes Are Circuits in the Compute, Not the Topology

> **The claim.** The KIBC combinator opcodes (K I B C S D W Y WHNF) are real,
> universal, and decodable — but they are **not** circuits in the *topology*
> (dedicated weights / heads / directions you can localize and ablate). They are
> circuits in the **compute**: dynamically instantiated operations in the reduction
> trajectory, defined by the routing (attention pattern), scheduled by depth. This
> single frame resolves the apparent tension between "the crystal is universal and
> real" and "you cannot ablate a single opcode direction," and it names the
> mechanism: **GD builds a soft routing topology, via the gradient extremes, over
> the frozen base weights; the opcodes are the operations of that soft topology.**
>
> This is the honest spine of the opcodes/ exhibit (see `opcodes/EVIDENCE_CATALOG.md`).
> It is stated for a hostile skeptic: every supporting result below ships with the
> null or control it beats.

## Two topologies

There are two structures in a trained transformer, and they must not be confused:

1. **The frozen topology** — the base weight structure GD is normally understood to
   "train." This is where classic mech-interp looks for *circuits*: dedicated
   weights whose removal breaks a function. For the combinator opcodes, **they are
   not here.**
2. **The soft topology** — a routing overlay that GD *forms* on top of the frozen
   base, using the extremes of the gradient. The compute is routed through this
   overlay. **The opcodes live here.**

An opcode is therefore a transient *operation of the soft routing topology*, not a
stored locus in the frozen weights. "The routing IS the program"
(`head-combinator-isa.md`): the combinator is expressed in *which positions attend
to which*, not in any head's identity or any fixed direction.

## Evidence — it is NOT a topology circuit

| Finding | What it shows | Null / control | Host |
|---|---|---|---|
| **Shared hardware** (`head-combinator-isa.md`) | All 9 combinators activate essentially the same attention-head pattern (mean pairwise r=0.944 at L33). No "K head," no "B head." | correlation across combinators; 500 crystal probes | Qwen3-8B |
| **C-field un-ablatable** (`program_cfield_ablation.py`) | Erasing ALL linearly-decodable C at its peak layers does not selectively hurt object-application — *"decisively a readout register, not the computation."* | random-direction ablation, equal magnitude; c=2 vs c=0 differential | Qwen3-14B / 0.6B |
| **S has no vertex** (s271 duplication register) | The duplicator S is absorbed holographically (softmax can't fan-out); it dissolves into a {S,D,Y} sector rather than sitting on a clean opcode vertex. | exact-enumeration nulls; W/Y positive controls | 13-model sweep |

These are *negative* results at the direction/weight level — and they are exactly
what the frame predicts. Showing them **builds** credibility (we tested whether the
opcodes are localizable circuits; they are not).

## Evidence — it IS real in the compute

| Finding | What it shows | Null / control | Host |
|---|---|---|---|
| **Crystal universality** (`crystal-universality.md`) | The 9×9 combinator Gram (routing-register cosine structure) is the same relational object across 11 models / 6 architecture families; root consensus gc ≈ 0.985; survives 1-bit/ternary quantization. | shuffled-label null; quant rung vs FP reference | ★27B + 10 |
| **Prose = formal opcodes** (`symbol-isolation.md`, register-split) | Natural-language prose lands on the same opcodes as formal lambda (cross-register classify z=2.99–4.68, p≤0.004). Transfer carried by WHNF/Y/I; C=0 (operation vertices register-bound). | shuffled-label permutation null (n_perm=500) | ★27B |
| **Zone ablation is causal** (zone_ablation_27b) | Zero the ENRICH zone (L32-53) → λ-reduction collapses 1.0→0.2 while facts survive (0.8); zero COMMIT (L59-63) → the reverse. 4.0× λ-specific double dissociation. | the other task is the control (double dissociation) | ★27B |

**The causal granularity is the phase, not the direction.** A zone is a *stretch of
the computation*; ablating it bites because it removes a phase of the routing
trajectory. A single opcode direction does not bite because the opcode is not stored
there — it is a step the shared substrate performs.

## The mechanism — how compute-circuits exist without weight-circuits

Nearly all compute in an LLM is **routing**, and GD forms that routing from the
**gradient extremes**:

- **Very high gradients** carve the active routing edges (the strong sign structure —
  ~95% of the encoded structure is sign/routing; `two-registers-of-topology.md`).
- **Near-zero gradients** deposit the frozen, irreducible atoms. GD cannot delete a
  connection, so it drives magnitude toward zero, *"creating a smooth landscape that
  approximates a discrete structure"* — the soft topology
  (`topology-gradient-separation.md`). `gradient-zero-map.md`: ~35% of positions sit
  at gradient equilibrium — the crystal atoms every model converges to.
- The heavy-tailed gradient (`gradient-voting.md`, `ratio-gradient-quantization.md`,
  "spend bits on the ends") is why *both* extremes carry the structure.

The result is a **soft routing topology laid over the frozen base weights**. The
frozen lattice is the *precondition* for GD to build the soft structure
(`topology-gradient-separation.md`: the topology must be frozen for GD to build the
soft topology that makes the lattice functional). The compute flows through the soft
overlay. This is why ablating a base-weight direction (C-field) misses the
operation: you are cutting the frozen substrate, not the soft routing step.

## Register split (from `two-registers-of-topology.md`)

| Register | Function | Encoded in | Lives in |
|---|---|---|---|
| **Hard topology** | routing (which neurons fire) | **sign** | `gate_proj` (router) |
| **Soft topology** | value + error-correction | **magnitude** (highways/zeros) | `up_proj` / `down_proj` |

(Terminology note: `topology-gradient-separation.md` s180 uses "soft topology" for
the whole GD-built routing landscape approximating a discrete structure;
`two-registers.md` s203 uses "soft" specifically for the magnitude/value register.
Both point at the same fact — GD builds a smooth landscape via magnitude and
gradient extremes over a frozen sign lattice.)

## Consequence for the exhibit

The sentence playback (prose → opcodes fire + j-space per stage) shows the compute's
operational **trajectory** through KIBC operation-space — *state-on-the-crystal*.
That is "circuits in the compute made visible," and it is honest by construction:

- **Never** claim a topological circuit "lights up" or that ablating an opcode
  direction breaks a function (it does not — D1).
- Causal language is reserved for **phase/zone** ablation (A1), never
  direction-level, unless a positive direction-level causal card is later found.
- The reading is a **decodable readout** of which operation the soft topology is
  running — not a claim about a stored weight-circuit.

## Consequence for interpretability

Mech-interp's default object — the localized circuit in weight space — is the wrong
object for these operations. The right object is the **soft routing topology**: the
operation is defined by the attention pattern and the depth schedule, distributed
over shared hardware. Looking for an opcode in the frozen weights and failing is not
evidence of absence; it is evidence the operation lives in the compute.

## How to verify / falsify

- **Falsify the frame:** find a base-weight direction or head whose ablation
  *selectively* and *causally* destroys one opcode's function (scaling with opcode
  load, beating a random-direction control). None found so far (C-field is the
  clean negative). A positive would refine the frame to "some opcodes are also
  topology-localizable."
- **Strengthen it:** replicate the C-field null on 27B; run the direction-ablation
  battery across the other opcodes (edge-knockout, head-ablation pending); confirm
  the crystal universality already spans Gemma + Qwen-MoE (cross-architecture anchor).
- **Runtime checks:** crystal Gram in `opcodes/data/consensus_gram.json`; per-model
  `model_vsm.json`; zone ablation `results/zone-ablation/Qwen_Qwen3.6-27B/`; C-field
  `results/program-cfield-ablation/`.

## One-line

**GD builds a soft routing topology via the gradient extremes over the frozen base
weights; the KIBC opcodes are the operations of that soft topology — real in the
compute, invisible in the frozen circuit map.**
