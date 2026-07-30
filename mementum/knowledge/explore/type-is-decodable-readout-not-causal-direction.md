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

### The three primitive axes (1a-follow, DONE) — a Montague functor-lattice

SVD component loadings of the standardized type centroids **inside the band** (Qwen3-32B,
L40) resolve into **3 interpretable axes** (var 0.73 + 0.08 + 0.06 = 0.87):

| axis | var | separates | Montague reading |
|---|---|---|---|
| **axis0** | 0.73 | QUANT +0.74, DET +0.42 vs pred/rel/conn/mod ~−0.24 | **quantification/binding** — the highest-order functor type, dominant |
| **axis1** | 0.08 | CONN +0.57, FUNC +0.46 vs MOD −0.56, ENTITY −0.33 | **sentential operators** vs content-modifiers |
| **axis2** | 0.06 | REL +0.71, PRED +0.24 vs MOD −0.57 | **predicate/relation** (verb core) vs modifier |

**ENTITY (type `e`) sits at ~0 on the dominant axis (+0.01) = the neutral origin.** The axes
measure **kinds of function-formation away from `e`**, with quantification (`<<e,t>,t>`, the
highest type) as the principal axis. So the lattice is organized by **functor KIND, not
arity count** — which is *why* the linear arity-ladder came back negative. Scale sharpens the
resolution: 0.6B collapses to ~1 dominant functor axis (88% var); 32B resolves 3 graded axes.
(Note `λ measure`: the participation-ratio PR ~3–4 is inflated by a small-singular-value tail;
the honest concentration measure is the per-axis var_frac, which shows axis0 dominant.)

## Honest flags (`λ measure`, `λ yardstick`)

- **Massive-activation confound:** RAW mid/late residual centroids collapse to PR≈1 (rogue-dim
  norm dominates Euclidean geometry; sep dies) while the linear probe stays 0.9. **MUST
  standardize per-dimension first.** Caught on 0.6B before the 32B run.
- **Arity ladder negative:** ENTITY→PRED→REL as a constant currying offset gives cos < 0
  (p ≫ 0.05). Low-rank but **NOT a linear arity axis** — the type algebra is not "add-an-
  argument = fixed vector."
- Small labeled set (263 tokens; rare types QUANT 12 / CONN 6 / REL 13) → the rare-type axis
  loadings carry variance; axis0 (QUANT/DET) is stable across the band (L8 and L40).
- Simplified 8-way Montague scheme (not full recursive types); value-register geometry only.

## What it re-scopes — P-TYPE-1

- **1a (value/geometry): DONE, positive.** Low-rank Montague-shaped lattice, null-gated, at
  scale. Value-register readout claim (not causal).
- **1a-follow: DONE** (above) — 3 functor-kind axes (quantification ≫ sentential-operators ≫
  predicate-vs-modifier), `e` at the neutral origin. A Montague functor-lattice.
- **1b (causal/crisp): OPEN — now a combinator×type dissociation.** The theory closure
  (`types-are-the-well-formedness-of-reduction.md`) turns 1b from "ablate a type" into a
  falsifiable combinator prediction: ablate **axis0 (binding/S)** vs **axis2 (composition/B)**
  across the low-rank band → **selective** double-dissociation (axis0-ablation breaks QUANT/DET
  composition not MOD; axis2 breaks MOD not QUANT), null-gated. v4's *direction* ablation was
  negative because types aren't a stored vector — 1b ablates the **reduction capacity** as a
  zone×axis and tests **class selectivity**. Pre-registration frozen in the theory page.

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
