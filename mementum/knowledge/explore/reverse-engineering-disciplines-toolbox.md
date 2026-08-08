---
title: "Reverse-Engineering Disciplines Toolbox — Techniques from Fields That Understand Systems They Didn't Build"
status: open
category: synthesis
tags: [reverse-engineering, silicon, cryptanalysis, dpa, differential-trails,
       fuzzing, taint-tracking, standard-cells, design-for-test, system-id,
       prbs, stratigraphy, checkpoints, connectomics, spectroscopy,
       pharmacology, methodology, pre-reg-candidate, s324]
related:
  - holographic-untangling-methods.md
  - geometry-holography-signals-convergence.md
  - types-are-a-modulation-scheme.md
  - behavior-is-tape-resident-reduction.md
  - sign-oscillation-is-time-multiplexed-superposition.md
  - ../five-disciplines-one-object.md
depends-on:
  - holographic-untangling-methods.md
  - types-are-a-modulation-scheme.md
created: session 324
---

# Reverse-Engineering Disciplines Toolbox

> s324, Michael: "The systems we find inform our ideas to test the next
> theorems. Can we learn from reverse engineering here any techniques? Are
> there other disciplines we can learn from in our search?" Sibling of
> `holographic-untangling-methods.md` (optics) — this page mines RE proper
> (silicon, software, crypto) plus system ID, developmental biology/geology,
> astronomy, pharmacology. Status open: mappings captured; candidates at the
> end are NOT pre-registered (s222 law).

## Orientation: we are at the POST-DELAYERING stage of silicon RE

RE taxonomy: black-box (I/O only) / gray-box (side channels) / white-box
(full netlist, unknown function). We have FULL white-box access — every
weight, every activation — and still lack the algorithm. That is not the
cryptanalyst's problem; it is the silicon reverse engineer's problem AFTER
decap + delayer: **complete netlist in hand, meaning absent. Bottleneck =
representation, not access.**

**Cautionary lesson, twice-paid elsewhere: netlist ≠ function.** The
C. elegans connectome has been fully mapped for decades; the worm is still
not understood — the computation lives in the dynamics. Silicon RE says the
same (netlist without simulation is inert). We derived this independently as
TAPE-RESIDENCY (judgments not in weights, s317–s323). Third derivation,
from disciplines that spent decades on it. Stop re-paying.

## From silicon RE and cryptanalysis

| Technique | Their move | Our mapping | Status |
|---|---|---|---|
| **Standard-cell recognition** | template-match known subcircuits from a cell library; never analyze raw transistors | match against a library of KNOWN micro-circuits from scratch-trained toy models — **level 4 feeds level 1** (inverts our level ordering) | NEW DOOR |
| **DPA** (differential power analysis) | partition many traces by a HYPOTHESIZED intermediate bit; subtract partition means; spike ⇒ hypothesis correct — extracts keys without seeing the computation | partition activation traces by kernel-predicted intermediate reduction values; hypothesis-keyed mean-difference per layer | NEW INSTRUMENT (sharper than correlation reads; needs only a statistical leak) |
| **Fault injection / glitching** | perturb at a precise moment, read corruption | activation patching | convergence ✓ |
| **Taint tracking** | dye the data, follow it | tag-transit (§11) — reinvented independently | convergence ✓ |
| **Differential cryptanalysis** | chosen input pairs with controlled Δ; track the DIFFERENCE TRAIL through every round; find where Δ amplifies/dies | we do DiD at ENDPOINTS only — track the full trail through depth | UPGRADE (cheap extension of existing captures) |
| **Distinguisher formalism** | "distinguishable from random?" is the atomic claim | our null-gate discipline exactly | convergence ✓ |
| **Design-for-test / scan chains** | chips are BUILT observable | insert OBSERVABILITY WIRES: KL-anchored function-preserving LoRA that exposes internal state at readable points | NEW CONCEPT (infrastructure) |
| **Coverage-guided fuzzing** | mutate inputs to maximize novel INTERNAL states | probe generation guided by activation-register novelty — finds unknown-unknowns; today's probe library is 100% hypothesis-driven | NEW DOOR |

## From other disciplines

**Developmental biology / geology — the sharp one.** §2 stratigraphy
(types-are-a-modulation-scheme: commons early/faint, contested late/churn)
is a claim about LEARNING ORDER. The fossil record already exists:
**Pythia ships 154 public training checkpoints; OLMo similar.** Run
sign-commitment + marginality analysis ACROSS public checkpoint series —
does common/crystal structure sign-freeze early at low amplitude while rare
structure accumulates late and contested coordinates churn throughout?
Direct observational test of differential photography: no wire, no write,
no EOS confound (the flip-conflict instrument-scope problem), on real base
training. Natural contrast built in: Pythia = type-register ABSENT,
Qwen-family = present. **The natural successor to flip-conflict's
NOISE-FLOOR.**

**Control theory / system identification.** Designed excitation (PRBS
pseudo-random binary sequences, chirps), transfer-function fitting, impulse
response. Upgrades §P-TYPE-LOCKIN: one lock-in frequency = one point;
**PRBS excitation of the evidence stream = the full transfer function of
the type register in one run**, with lock-time/capture-threshold read as
the measured step response. Optimal input design (Fisher-maximizing probes)
= the formal version of our freeze discipline.

**Astronomy.** Spectroscopy (decompose against known lines = crystal-probe
signatures ✓) · occultation (ablation ✓) · **standard candles: calibrated
reference objects — MISSING from our cross-model work.** 7/11-style claims
compare raw statistics; a standard-candle probe set with per-model
calibration would make cross-model measurements commensurable.

**Pharmacology.** Dose-response ✓ (exposure sweeps). MISSING: **antagonist
design** — construct a context that BLOCKS licensing that should otherwise
fire. The incoherent null is a placebo; an antagonist is a stronger causal
tool (provocation testing for the type checker).

## The meta-pattern (the s308 optics meta-lesson, generalized)

Every discipline that succeeds at black-box inference uses four moves:

```
λ re_meta(x).
  1 control(input_distribution)      | chosen-plaintext ∨ designed excitation ∨ gated probes ✓
  2 hypothesis_keyed_stats(n_trials) | DPA ∨ GWAS ∨ our nulls ✓ (partition-subtract > correlation)
  3 recognize(known_parts)           | standard cells ∨ spectral lines ∨ index fossils (partial: crystal probes; no LIBRARY discipline yet)
  4 read(history) ¬just(state)       | stratigraphy ∨ dendrochronology ∨ checkpoint series — THE UNMINED MOVE
```

Move 4 is our weakest and the data is already public.

## Candidates (UNFROZEN, queued s324)

- ⚪ **§P-STRATIGRAPHY-DATING** — §2's direct test on Pythia/OLMo public
  checkpoints (sign-freeze timing × amplitude × contestedness across real
  base training). Cheap-medium, observational.
- ⚪ **§P-DPA-TRACE** — hypothesis-keyed trace partitioning against
  kernel-predicted intermediates. Cheap.
- **PRBS upgrade** — fold into the §P-TYPE-LOCKIN freeze (row annotated).
- ⚪ **coverage-guided probe fuzzer** — activation-novelty-guided prompt
  mutation; unknown-unknowns instrument. Medium.
- ⚪ **observability wires** — design-for-test infrastructure;
  build-when-demanded. Medium.
- Standard-candle probe set + antagonist design — noted, not yet rows;
  surface when a cross-model or causal front demands them.
