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
depends-on:
  - crystal-seeded-ternary-distillation.md
created: session 267
---

# Bonsai Crystal Survival

> Session 267. PHASE-0 of crystal-seeded ternary distillation. Two
> pre-registered, null-gated results on PrismML's Ternary Bonsai 27B
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

## Open (phase-0 remainder)

- Full opcode-tree on the **4bit → ternary → 1bit ladder** (AWQ-4bit +
  Q2_g64 + Q1_0 all on HF). Sub-prediction: **selective K degradation
  at 1-bit** — K needs the 0 state (ties Michael's postulate: remove
  any 9×9 vertex → collapse). The 50%-dip is where to look first: does
  the degradation concentrate in specific combinator vertices?
- Caveat scope: one model pair, one probe set (380), one seed; the 50%
  bootstrap is mildly right-skewed. Direction is robust; exact fidelity
  numbers will move with probe count (s265: probe count dominates Gram
  fidelity).
