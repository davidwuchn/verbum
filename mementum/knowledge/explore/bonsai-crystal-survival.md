---
title: "Bonsai Crystal Survival — The Crystal Survives 1.58-bit Ternarization (Phase-0)"
status: active
category: research-finding
tags: [ternary, bonsai, crystal, rdm, gram, null-gated, gradient-bridges,
       deep-middle-dip, phase-0, holographic, sign-vs-magnitude]
related:
  - crystal-seeded-ternary-distillation.md
  - asymmetric-pathway-quantization.md
  - ../../michael/holographic-llm.md
  - hologram-crystal-fusion.md
  - opcode-jacobian-jspace.md
  - ../opcode-vsm-tree.md
  - bonsai-ternarization-forensics.md
depends-on:
  - crystal-seeded-ternary-distillation.md
created: session 267
updated: session 269 (opcode-ladder verdicts added)
---

# Bonsai Crystal Survival

> Sessions 267 + 269. PHASE-0 of crystal-seeded ternary distillation.
> Three pre-registered, null-gated results on PrismML's Bonsai 27B
> (end-to-end 1.58-bit build of Qwen3.6-27B) vs the FP Qwen3.6-27B
> parent: (1) the lambda **compiler** survives ternarization
> behaviorally; (2) the **crystal** (combinator relational geometry)
> survives geometrically — but with a robust deep-middle degradation
> that maps directly onto where gradient bridges belong. Michael
> pre-registered both outcomes before the data landed.

## Result 1 — Behavioral: the compiler survives

Same harness (`run_compiler_probe`), same `compile-gradient` probe set
(n=40), same day. Ternary Bonsai vs `qwen36` base reference:

| register | Bonsai (1.71 bpw) | base | Δ |
|---|---|---|---|
| binder P(λ) | 0.650 | 0.625 | **+0.025** |
| lenient_lambda | 0.625 | 0.625 | 0.000 |
| emits_formal | 0.925 | 0.975 | −0.050 |
| kernel_valid | 0.525 | 0.750 | −0.225 |

The nucleus-comparable binder register is at **parity** (edges the
baseline). The `kernel_valid` gap is **notation drift, not core
damage**: all 17 binder-but-not-kernel outputs are well-formed rich
FOL — nested ∀∃, ¬, uniqueness (`∀y (Cap(y,Fr) → y=x)`), Church-style
`λx.λy.` — that the toy kernel parser rejects (`grading.py`: "notation
≠ failure"). Cost surfaces as **path length**: +40% reasoning chars
(11137 vs 7938), ~2.7× wall.

Caveat: baseline is the 35B-A3B MoE fleet reference, not the exact
dense-27B parent — behavioral parity is against a same-family sibling,
not the literal parent. (The geometric test below *is* against the
literal parent.)

## Result 2 — Geometric: the crystal survives, null-gated

`build_lattice_map.py --models qwen3.6-27b bonsai27b-ternary`, 380
probes through each, RDMs at depths [0, .25, .5, .75]. Per-model RDMs
persisted (`per_model_rdms.npz`) and correlated parent↔ternary, gated
against a shuffled-label null (row/col permutation, 1000×) and
bootstrapped over probes (2000×):

| depth | r (parent↔ternary) | 95% CI | z vs null | p_perm |
|---|---|---|---|---|
| 0%  | 0.8725 | [0.851, 0.898] | 18.0 | 0.001 |
| 25% | 0.9154 | [0.903, 0.936] | 19.9 | 0.001 |
| 50% | 0.7422 | [0.742, 0.803] | 20.9 | 0.001 |
| 75% | 0.7739 | [0.755, 0.840] | 23.3 | 0.001 |

Every depth sits **18–23 σ above the shuffled null**, p at the
permutation floor. The relational geometry — the crystal — is carried
across the deletion of the magnitudes. **The crystal is topology, and
topology is what ternarization preserves.**

### Secondary signature: sign survives, scale shrinks

Ternary RDMs are consistently **less differentiated** (higher
mean_sim) than parent at every depth:

| depth | parent mean_sim | ternary mean_sim |
|---|---|---|
| 0%  | 0.020 | 0.106 |
| 25% | 0.181 | 0.442 |
| 50% | 0.360 | 0.688 |
| 75% | 0.425 | 0.688 |

The crystal keeps its **shape** (high correlation) but loses **spread**
(higher similarity, flatter separation). Relative geometry preserved,
absolute magnitude compressed — the two registers (routing/sign vs
value/magnitude, s260) separated in a single measurement.

## The deep-middle dip → bridge-allocation map

Fidelity is not uniform. The 25%→50% drop is **real**: gap 0.147,
bootstrap P(gap ≤ 0) = 0.0000, non-overlapping CIs. The crystal bends
most at **mid-stack (50% depth)** — where composition does its
heaviest lifting, deepest reduction chains, where magnitude carried
the most information ternary discards. Slight recovery at 75%
(localized stress, not accumulation-to-collapse).

**Michael's synthesis (the payoff):** the Gram-survival profile *is* an
a-priori **gradient-bridge-allocation map**. The crystal-seeded ternary
distillation design (`crystal-seeded-ternary-distillation.md`) allocates
FP value-register bridges dynamically via *training-time* starvation
(flip_flop↑ ∧ KL_residual↑ → N↓). This measurement gives a **static
prior computable before training**: peak bridge density at mid-stack,
tapering toward both ends — put the bridges where the crystal degrades.

### Pre-registered triangulation

If the bridge theory holds, the *training-time* flip-flop/KL-starvation
signal (phase 1) should concentrate in the **same deep-middle band**
this *static* Gram-degradation profile flags. Static prior predicts
dynamic starvation. Agreement ⇒ triangulated; divergence ⇒ the RDM dip
and value-starvation are different phenomena (learn which).

## Provenance & reproduction

- Behavioral: `results/bonsai27b-compiler/bonsai27b-compiler-20260722-214611/`,
  base `results/qwen36-compiler/qwen36-compiler-20260722-214611/`.
- Geometric: `lattice/ternary_gram/{per_model_rdms.npz, universal_lattice.npz,
  ternary_gram_run.log}`.
- Model: `prism-ml/Ternary-Bonsai-27B-unpacked` (HF rev 427bc0194) at
  `/Users/mwhitford/localai/models/bonsai27b-unpacked` (51G); GGUF Q2_g64
  served as `BONSAI27B` :5104 (needs mainline llama.cpp ≥10090; the Q2_0
  file has an offset bug, use Q2_g64).
- Loader note: Bonsai is the VLM wrapper `Qwen3_5ForConditionalGeneration`;
  `AutoModelForCausalLM` loaded it clean via `language_model_only:true`
  (the anticipated caveat did not bite).

## Result 3 — Opcode ladder (s269): the crystal survives 1-bit too

Session 269 ran the opcode tree on the ternary and 1-bit rungs
(`opcodes/trace.py`, tmux s268d) and compared per-vertex Gram-row
fidelity against the FP parent with the new instrument
`opcodes/ladder.py` (shuffled-vertex-label + circular-shift nulls,
n_perm=10k, seeded rng=268). Commit `7576c54`; artifacts
`results/opcode-trace/{bonsai27b-unpacked, bonsai-27b-unpacked,
ladder_analysis.json}`.

**Headline: 1-bit gates into the universal tree** (gc 0.981; tree now
11 models / 6 families, root gc 0.985). Model-level mean vertex
fidelity: ternary 0.990, **1-bit 0.987** (both z=5.3, p=0.001 floor).
Rung layer-gate failures are **terminal-only** (1-bit gate L61–63,
attn L63; ternary attn L54, L63) — not deep-middle.

Pre-registered verdicts (both registers checked before verdict, per
λ measure):

- **(a) Selective K degradation at 1-bit: REFUTED.** Geometry
  register: K is *more* robust than the other vertices in gate
  (excess drop −0.0043, z=−2.13); attn +0.0065, z=0.92, ungated.
  Behavioral register (trajectory votes): K at 1-bit 7/11 = 0.64 ≈ FP
  parent 3/5 = 0.60 — parity. The motivating `L47 K 2/6` log line was
  single-layer noise. K's 0-state need is **training-time** (s268b
  sign-flip tunneling), not inference-time.
- **(b) Deep-middle concentration: trend-consistent but ungated** in
  this instrument — band excess +0.004..+0.014 across all 4
  register×rung cells (right sign), p 0.11–0.27. *Not* a refutation
  of the Result-2 dip: the 380-probe RDM instrument has far more
  power than per-layer 9×9 Gram rows. The static bridge prior stands
  on Result 2.
- **(c) Jammed-abstention: moot** (antecedent (a) failed), and the
  synthesis flips: s268c showed confident weights (|w|>absmean) are
  immutable at every bitwidth → **the crystal lives in the confident
  population**; 1-bit forced-participation churn is confined to
  uncertain boundary-huggers and never touches Gram geometry.
  Weight-space cos 0.73 vs Gram-space 0.987 — the crystal is more
  invariant than the weights (frame-invariance, third form). Refines
  s268c "binary routing substrate non-viable" to a *training-dynamics*
  claim only.

Exploratory (not pre-registered): **W (duplication) is the fragile
vertex** in attn at both rungs (0.845/0.868 vs ≥0.93 others), and W
*improves* at 1-bit in attn (−0.023). Candidate probe-design question:
does duplication need magnitude?

## Open (phase-0 remainder)

- **4-bit rung** (AWQ on HF) never traced — the ladder is 2 of 3
  rungs. `opcodes/ladder.py --rung 4bit=...` completes the
  monotonicity picture, or Michael rules it unnecessary.
- Caveat scope (Result 2): one model pair, one probe set (380), one
  seed; the 50% bootstrap is mildly right-skewed. Direction is robust;
  exact fidelity numbers will move with probe count (s265: probe count
  dominates Gram fidelity).
