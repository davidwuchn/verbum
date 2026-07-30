---
title: "Types are a decodable readout of a distributed type-application compute — not a stored direction"
status: active
category: explore
tags: [types, montague, register, value-register, routing-register, decodability,
       circuits-in-compute, low-rank, lattice, P-TYPE-1, C5, C2, crisp-vs-graded,
       massive-activation, null-gated, s282]
related:
  - opcodes-circuits-in-compute.md
  - montague-inversion.md
  - map-and-swap-resident-lisp.md
  - project-thesis.md
depends-on:
  - opcodes-circuits-in-compute.md
created: session 282
---

# Types are a decodable readout, not a stored direction

> **The one-sentence claim.** In the transformer, a Montague semantic **type** is a
> **richly decodable value-register readout** of a **distributed** type-application
> computation — it is *not* a crisp, causally-ablatable direction. This folds C5
> (types geometric+lexical) **into** C2 (circuits-in-compute) rather than standing alone.

## Why this page exists (the register question, `λ measure`)

"Is the type system crisp or graded?" is not one question. "Type" bundles two quantities
that live in **different registers** and need **different probes** (getting it wrong is the
s206/s247 scar in both directions):

- **type-CONTENT / assignment** — *what type a slot carries.* **Value register**, graded
  (a direction/subspace with magnitude). Substrate.
- **type-CHECK** — *does this compose / is it well-typed.* **Routing register**, a discrete
  gate (governs what attends to what).

routing/crisp probe on graded content → **false negative** (s206: attention-weight ⊥
value-claim → near-false-refute; logit-lens found +0.611). crisp readout (argmax) on a
graded margin → **manufactured crispness** → false positive.

## The three registers already on disk — they triangulate (Qwen3, s282)

**1. Behavioural (graded surprisal) — real but asymmetric.**
`scripts/experiments/type_directed_v3_nonce.py`, `results/type-directed/`. Frequency-free
nonce crossover **+2.038 nats, t=9.33, consistency 1.0** (sign-agreement across 16 nonce,
NOT argmax). BUT decompose: `det_pen` ("The {w}") mean **+0.026, t=0.13** = **null**;
`name_pen` ("John {w}") mean **−2.01, t=−10.1** = carries the **entire** effect. So
behavioural "type-directedness" is really **predicate-licensing after a subject name**, not
a symmetric noun/verb check. One strong slot, frequency-free, real.

**2. Decodability (value register) — very strong.**
`scripts/explore/probe_type_qwen3_32b.py`, `results/type-probe-qwen3-32b/`. 8-way type
{DET, ENTITY, PRED, REL, QUANT, MOD, CONN, FUNC} linear-probe accuracy **0.88–0.96 at every
layer** (baseline 0.28), peaking early (L2 0.96). Type is a rich, linearly-decodable
value-register object at all depths. (Sense-2 confirmed.)

**3. Causal (v4 ablation) — negative *as a direction*.**
`scripts/experiments/type_directed_v4_ablation.py`. Type direction AUC → 1.0 (trivially
decodable) BUT **`type_direction_is_causal = false`**: ablating the decoded direction retains
**0.643** of the crossover vs **0.952** random — the behaviour **survives**; the decoded
direction is *not* the causal lever.

**Synthesis:** decodable-but-not-causal-as-a-direction = the **circuits-in-compute** pattern
(C2 core frame), the same shape as the D1 C-field ("readable but causally inert / readout
register") and the s206 scar. Type behaves like everything else in this machine: a decodable
readout of a **distributed routing** operation, not a stored locus.

## The lattice geometry (P-TYPE-1a) — low-rank + Montague-shaped, null-gated

`scripts/explore/type_lattice_geometry.py`, `results/type-lattice/`. Standardized
(diagonal-whitened) 8-type centroids, pre-committed shuffled-label null (200 perms).
**Qwen3-32B (the C5 host):** a **compress→expand** arc across depth —

| band | PR (≈ effective axes) | vs shuffled null |
|---|---|---|
| lexical (embed–L4) | ~6.0–6.5 | p ≥ 0.68 (full-rank simplex) |
| onset (L6) | 3.57 | p = 0.03 |
| **band (L6–L48)** | **3.7–4.8** | **p < 0.05 throughout** (~3 axes, top-3 = 0.85–0.92) |
| readout (L52–L63) | ~6 | p > 0.25 (re-expands) |

⇒ the type lattice is genuinely **small/low-rank in the compositional interior** (~⅔ of the
stack), null-gated — **confirming the montague-inversion decisive prediction** ("type lattice
SMALL, low-rank not high-dim"). Same progressive-collapse shape as **C8**, in the type
geometry. Scale strengthens it (0.6B: same arc, narrow L8–16; 32B: broad+robust).

## Honest flags (`λ measure`, `λ yardstick`)

- **Massive-activation confound:** RAW mid/late residual centroids collapse to PR≈1 (rogue-dim
  norm dominates Euclidean geometry; sep dies) while the linear probe stays 0.9. **MUST
  standardize per-dimension first.** Caught on 0.6B before the 32B run.
- **Arity ladder negative:** ENTITY→PRED→REL as a constant currying offset gives cos < 0
  (p ≫ 0.05). Low-rank but **NOT a linear arity axis** — the type algebra is not "add-an-
  argument = fixed vector."
- The saved Gram is at the **lexical** best-sep layer (rough content{ENTITY/PRED/REL/MOD} vs
  functional{DET/QUANT/CONN/FUNC} split); the ~3 axes **inside** the band are a follow-up.

## What it re-scopes — P-TYPE-1

- **1a (value/geometry): DONE, positive.** Low-rank Montague-shaped lattice, null-gated, at
  scale. Value-register readout claim (not causal).
- **1a-follow:** characterize the ~3 primitive axes **inside** the low-rank band (L24–L36) —
  SVD component loadings per type; is there an `e`-axis / a function-formation axis?
- **1b (causal/crisp): OPEN, and must change register.** v4 already ran *direction* ablation
  → negative (correctly). The right probe is **A1-style ZONE/PHASE ablation** of the low-rank
  band: does knocking out L6–L48 categorically break type-licensing? Only that earns the
  sense-1 "types make composition a **circuit**" claim.

## Ties to the artifact (the LLM-REPL)

This *is* the eval-fuzzy / check-crisp seam one level down: the LLM carries a **graded**
type assignment (value register, decodable, low-rank); the Clojure kernel imposes a **crisp**
type-check (routing, definitionally discrete) on top — calibrated thresholding, null-gated
Print, confidence-not-certainty. The register split is where the fuzzy reducer meets the crisp
verifier. The REPL's type system is Montague's; this page measures how much of it GD already
built (a lot, low-rank) and where the crisp check must be re-imposed.

## Open fork (from the name_pen asymmetry)

The behavioural effect being **name_pen-only** (predicate-licensing after a subject) hints the
operative "type" may be **argument-saturation** (a predicate wanting its subject) = the
**S/binding combinator**, not a noun/verb tag. Worth a probe: does the type-check fire on
*saturation* (a slot filled) rather than category?

## Sessions
s282 (three-register triangulation + P-TYPE-1a low-rank lattice; from the types discussion).
