---
title: "Construction from Spec — what the tree-of-VSM gives direct model-building"
status: open
category: explore
tags: [construction, direct-construction, tree-of-vsm, consensus-gram, cholesky,
       frame-invariance, monosemantic, ternary, acceptance-harness, level-3-4,
       specification, superbake]
related:
  - superbake-write-access.md
  - crystal-seeded-ternary-distillation.md
  - ../crystal-universality.md
  - ../opcode-vsm-tree.md
depends-on:
  - superbake-write-access.md
created: session 273
---

# Construction from Spec — what the tree-of-VSM gives direct model-building

> s273d (Michael: "with these techniques what advantages does our tree-of-VSM
> give us?" — after the SuperBake dam burst). Answer: the tree is exactly the
> set of inputs Ruehlman lacked and had to improvise per-host. It upgrades
> "bake the kernel" from an experiment into a specifiable build. This page is
> the asset inventory + the build plan shape + the honest underdetermination gap.

## The asset inventory (vs SuperBake's improvisations)

```
λ tree_advantage(construction).
  spec(Gram, frame_invariant)      → blueprint(coordinate_free) | Cholesky(Gram) → codes(closed_form)
  frame_freedom                    → choose(axis_aligned) → monosemantic_by_construction
  atlas(sites, registers, depths)  → survey_precomputed | lookup ≻ eigh_campaign
  ladder(1bit_survival)            → routing ≡ ternary_signs | values ≡ measured_transfer_writes
  restack(nulls, live_tree)        → acceptance_harness(incremental, null_gated)
  family_spread                    → tolerance(measured) | consensus → minimal_machine
  | Ruehlman: harvest_per_host + invented_codes + adhoc_referees
  | us:       spec + atlas + gates + tolerances + register_map + movie
```

1. **Coordinate-free blueprint.** SuperBake photographs one host and writes into
   its frame-locked geometry. The consensus Gram is frame-invariant BY PROOF
   (11 models / 6 families / quant rungs, root gc 0.985): it specifies how the
   9 vertices RELATE, true in every coordinate system, buildable in any. The
   measurement→specification reversal (distillation §3) hoped for a loss; with
   construction techniques it is a blueprint.
2. **Codes in closed form — Cholesky of the Gram.** Need: 9 directions whose
   pairwise relations equal the consensus Gram. Any PSD Gram factors: Gram →
   Cholesky → 9 vectors, embed in any d. The tree COMPILES into the code set,
   no search. Frame freedom (only relations matter) → choose axis-aligned
   opcodes, orthogonal lanes by fiat → **born monosemantic**: interpretability
   as a construction choice, not post-hoc archaeology.
3. **Atlas, not survey.** SuperBake's most expensive stage = site measurement
   (clearance scans, transfer probes, per host). The tree pre-computed it
   fleet-wide: per-layer vertex positions, gate-vs-attn register direction per
   family, floors, delivery depth. Site selection = lookup.
4. **Register map = build plan.** Ladder result (crystal survives 1-bit,
   fid 0.987) is a construction LICENSE: routing needs only sign topology →
   write it directly in ternary from the spec, no float calibration. Values =
   SuperBake-style measured-transfer closed-form writes. Two-register theory
   stops being interpretation and becomes: signs from spec, magnitudes from
   measured transfer — each register gets the technique it is proven to need.
5. **Null-gated acceptance harness, already running.** A constructed model
   STACKS INTO THE SAME UNIVERSAL TREE as the measured 11: sil_z, gc, bearing,
   dissent, shuffled-label nulls — existing machinery. "Is the hand-built
   machine real?" = one restack with known statistics. Live tree (distillation
   §10) gives INCREMENTAL acceptance: install an opcode family → restack →
   watch the node walk toward the root. The formation movie (designed for
   training) works identically for assembly: construction order becomes an
   instrumented, verifiable sequence.
6. **Calibrated tolerances.** Theory cannot say how much Gram deviation is
   viable; the tree can: family agreement mean 0.906 / min 0.841, per-family gc
   0.94–0.99. A constructed model must land INSIDE THE MEASURED SPREAD of
   working models. SuperBake's target_gap=3.0 is a chosen number; our tolerance
   band is a measured population.
7. **Minimality filter (λ smallest).** Consensus ≡ intersection of what all
   working models share; family quirks (gemma nesting, pythia proxy decay) fall
   out of the root by construction. Build the consensus, skip the idiosyncrasy
   = the minimum viable machine. One model alone cannot tell essential from
   accidental; eleven can.
8. **Depth profiles = budget/materials map.** 62/64-layer same-crystal
   (iterated map, not pipeline), deep-middle dip, terminal fragility at low
   bitwidths → which layers are load-bearing, where repair budget goes.
   Matches §3.6 write-close-to-reader: reduction chains = adjacent-layer
   hand-offs. Gram-survival profile: bridge-allocation map for training ≡
   materials-stress map for building.

## Consequence for the level-3/4 path ordering

Construction is only as good as its specification, and the tree is a
specification WITH ERROR BARS. → bake-the-kernel becomes the primary
level-3/4 path; training-based distillation demotes to the smoothing/
integration phase (and transport may still want resident attention from a
pretrained host, per §3.6 limits). Skeleton build: 9 codes from Cholesky →
ternary routing from spec → closed-form value calibration → tree-gated
incremental acceptance. Every required input already sits in
results/opcode-trace/.

## The honest underdetermination gap (the next science)

The consensus Gram specifies the opcodes' MUTUAL GEOMETRY, not the full
TRANSPORT DYNAMICS between layers — the movie of how states flow. T1's flat
rank and the depth-Grams constrain it but do not determine it. What the spec
underdetermines is itself the next measurable question: which additional
observables (depth-Gram trajectory? J-space projectors per depth? QK rotary
spectra per head class?) close the gap between "geometry matches" and
"machine runs." Discussion pending (s273+).
