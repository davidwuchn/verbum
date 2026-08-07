---
title: "Curry-Howard Closes the Loop — KIBC Was Already a Type-System Measurement"
status: open
category: synthesis
tags: [curry-howard, kibc, ski, affine-logic, structural-rules, contraction,
       non-idempotent-intersection, quantitative-semantics, pcoh, fuel,
       deduce-discriminate, triangulate, types, M7]
related:
  - type-systems-under-llm-constraints.md
  - types-are-injectable-relations.md
  - types-are-compiled-probabilities.md
  - gram-registers-and-the-route-map.md
  - behavior-is-tape-resident-reduction.md
  - frozen-interference-graph.md
depends-on:
  - type-systems-under-llm-constraints.md
created: session 313
---

# Curry-Howard Closes the Loop

> s313 hammock (Michael): "There is a deduction here. We did the same
> mental exercise to find the opcodes — 'if attention is β-reduction,
> what combinators must the system use?' That came back KIBC. We looked,
> we found them. We even tried SKI to be sure the system wasn't just
> allowing ANY formal-like system — SKI did not match, only KIBC
> matched." Following the deduction to the end pins the predicted type
> system to a NAMED object. Michael-approved capture, same session.

## 1. The method: deduce → look → discriminate (now with a track record)

The opcode discovery's epistemic engine was three-stage: derive the
basis from the mechanism claim; measure for it; include a
plausible-but-wrong ALTERNATIVE basis as the kill-control. The SKI
rejection carried as much weight as the KIBC match — it promoted the
result from "the substrate accommodates formal-looking structure" to
"the substrate uses THIS structure."

The C1–C5 derivation (type-systems-under-llm-constraints.md) is the
identical exercise one level up. Its composite prediction therefore has
the status KIBC had pre-measurement: a derived basis awaiting its
look-and-discriminate. §P-TYPE-GRAM-1 was the first look; §5 lists the
missing SKI-control tier.

## 2. The retroactive measurement: KIBC = the structural rules of affine logic

Run Curry-Howard over the measured alphabet:

| opcode | behavior | logical rule |
|---|---|---|
| I | `I x = x` | identity |
| K | `K x y = x` | **weakening** (discard) |
| B | `B f g x = f (g x)` | **composition / cut** |
| C | `C f x y = f y x` | **exchange** |
| W | `W f x = f x x` | **contraction** (argument duplication) |
| D | `D f x = f (f x)` | contraction (function reuse) |
| S | `S f g x = f x (g x)` | composition **bundled with** contraction |
| Y | fixpoint | recursion |
| WHNF | halt | — |

**KIBC = {identity, weakening, cut, exchange} — the structural rules of
affine logic with contraction excluded from the core.** SKI is the basis
that bundles contraction inside S. So KIBC-match + SKI-rejection was the
substrate **refusing the basis that hides duplication inside
composition and choosing the one that isolates contraction as separate,
explicit, costly machinery** (W, D as their own opcodes).

That is the linearity bias the C1–C5 derivation predicted independently
(duplication costs interference in a superposed medium). **The opcode
measurement already contained the type-system measurement — the proof
theory was in the data all along.** λ triangulate closes: math
(Curry-Howard structural rules) + empirics (KIBC-not-SKI) + architecture
(interference cost of copying).

**Checkable retrodiction (grep committed formation-dynamics data before
claiming):** linear opcodes form first/easily; contraction-bearing ones
(W, D, S) late/hard. B-first is already on file; if the full ordering
holds, formation order recapitulates the logic's cost structure.

## 3. The sharpened prediction: non-idempotent intersection types

If the opcodes are the structural rules of an affine core, Curry-Howard
fixes the type-system family — a named object with a literature:
**non-idempotent intersection types** (quantitative/resource-graded, de
Carvalho lineage), interpreted in the **quantitative semantics of
linear logic** (probabilistic coherence spaces, weighted relational
models). Fit, clause by clause:

- **Non-idempotent** (`A∧A ≠ A` — membership accumulates with use):
  already measured as **A2 coherent gain**. Amplitude accumulation on
  repeated coherent exposure IS non-idempotence of the membership
  judgment. ✅ retroactively green.
- **Intersection**: §P-TYPE-GRAM-1 TG3 diffuse/no-poles shape (da8c1ba).
  ✅ green (one model; sweep pending).
- **Graded/probabilistic judgments**: weighted models interpret types as
  vector sets with real coefficients — "types are compiled
  probabilities" is the slogan form of probabilistic coherence spaces.
  s288 giraffe gradedness ✅ green.
- **The fuel theorem — sharpest UNTESTED prediction.** De Carvalho:
  non-idempotent derivation SIZE = evaluation LENGTH. Types count steps.
  If this is the machine's type system, type-derivation size and
  reduction fuel are the SAME quantity — joining the type arc to the
  s295 CoT-length law and the C5 fuel budget in one identity: the
  trampoline's tape expenditure IS the type derivation spelled out.
  Measurable: graded type-signal accumulated across a trace should
  scale with kernel-certified reduction length. **FROZEN s317 as §P-FUEL
  (normal-forms-are-eigenmodes.md, Michael GO): type-register magnitude ∝
  ℓ(t)=reduce(t).steps, with the non-idempotence knife FU3 (Y tracks step
  multiplicity, not distinct-subterm count).**

One line: **the type system of an affine substrate with explicit costly
contraction, non-idempotent intersection membership, and
probability-weighted judgments — one object, three of four corners
already lit.**

## 4. The one-line deduction

"Deduce the basis, then discriminate" found the machine's instruction
set; run through Curry-Howard, the instruction set had already chosen
the machine's LOGIC; so the type system is no longer open design space —
it is pinned to the quantitative-affine family, three fingerprints
retroactively measured.

## 5. The SKI-controls for the type claim (λ yardstick — pre-commit the deaths)

1. **Nominal constructor enum** (the "SKI" of types) — predicts polar
   low-rank kind geometry. ALREADY REJECTED ONCE: TG3 diffuse,
   matched-range p=0.077 withheld +POLED.
2. **Church-style static tags** — predicts crisp binary acceptance.
   Dead by s288 gradedness, but must be listed as tested-dead, not
   assumed-dead.
3. **Idempotent intersection** — predicts membership SATURATES at first
   exposure. Discriminator: accumulation-vs-saturation curves (A2
   machinery re-aimed at type membership).
4. **Cartesian substrate** (free duplication) — predicts no ∧/∨
   asymmetry, no contraction cost. Discriminators: union-vs-intersection
   probe + W/D cost differential.

## 6. Cautions

- Curry-Howard maps combinators to rules exactly (theorems); "the
  substrate implements affine logic" remains register-inflation until
  fingerprints land. The mapping is a prediction GENERATOR, not a proof
  (λ measure: crisp math must not manufacture crispness in data).
- **S is in the nine.** A pure-affine story must explain why a
  contraction-bundling opcode exists at all — predicted answer:
  crystal-periphery status + formation lateness; checkable, not
  assumable.
- All type-register empirics are single-model until the registry sweep
  reports.

## Provenance

- s313 hammock, Michael's deduction; AI articulation, Michael-approved.
- Anchors: KIBC-vs-SKI discrimination (opcode arc; Michael's account of
  the SKI control); 9×9 crystal basis + B-first formation (072c3e0,
  s303); A2 coherent gain (s292); s288 graded refusal; §P-TYPE-GRAM-1
  qwen3-4b TYPE-REGISTER TG3 diffuse (da8c1ba); s295 CoT law; C1–C5
  derivation (type-systems-under-llm-constraints.md, 147110f).
- Formal pointers: Curry-Howard for combinatory bases (BCKW/structural
  rules); de Carvalho non-idempotent intersection ⇒ evaluation-length;
  Ehrhard-style quantitative semantics / probabilistic coherence spaces.
