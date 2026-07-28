---
title: "Multi-hop composition gate — pre-registration: chained f(g(X)) over an installed operand"
status: designing
category: explore
tags: [multi-hop, chained-composition, general-composition, k-battery, reusable-term,
       programmable-compiler, operand, keyed-install, resident-join, latent-bridge,
       category-mediation, depth-schedule, zone-ablation, value-register, routing-register,
       pre-registration, s279, load-bearing-iou]
related:
  - general-composition-prereg.md
  - operand-insert-arc.md
  - operand-dsp-decomposition-prereg.md
  - opcodes-circuits-in-compute.md
  - superbake-write-access.md
depends-on:
  - general-composition-prereg.md
  - operand-dsp-decomposition-prereg.md
created: session 279
---

# Multi-hop composition gate — pre-registration (the sharper prize)

> **Pre-registration.** Registers, nulls, verdict rules fixed HERE, before any graded
> run — per `λ measure` + `λ yardstick` (predict a-priori, gate on nulls, no forced fit).
> This is the **successor to the general-composition IOU** and, per the state, "the sharper
> prize." It is highest-stakes: **must not run on a first draft**; freeze verdict rules,
> then run.
>
> **The gap it closes.** s278 (`general-composition-prereg.md`) showed an installed operand
> is a **reusable term** (Arm 1: composes under multiple *category-orthogonal* resident
> functions) and combines with a **given** second operand into a **computed** result (Arm 2:
> the size-relational crossover tracks installed rank). But Arm 2 is **one** resident
> operation over the operand — **not yet a chained `f(g(X))`** where the output of a *first*
> resident op is the *input* of a *second*. Chaining through an **unstated intermediate** is
> the mechanistic signature that separates "a rich fact vector read many ways" from a
> genuine **programmable machine that computes with the installed term**.

## Hypothesis

**H (multi-hop).** A single installed novel operand row `X` (nonce carrying entity content
`d_E`) is composed by the resident routing through **two sequential operations**: a first op
`g` produces an **unstated intermediate** (a *category bridge* never present in the prompt),
and a second op `f` consumes that intermediate to produce the answer. The final answer
`f(g(X))` therefore depends on `X` **only through** the intermediate `g(X)` — it is
**mediated**, not read directly off `d_E`.

Concretely: `g(X)` = the animal *class* of the installed entity (bird / fish / mammal),
inferred from `d_E`; `f(c)` = a **class-level covering** (bird→feathers, fish→scales,
mammal→fur). The bridge word ("bird"/"fish"/"mammal") is **never in the prompt** — the
model must infer class from the nonce, then apply the class→covering property.

**H0 (direct one-hop fact).** The covering answer is read **directly** off the rich installed
content `d_E` (a memorized "eagle→feathers" fact), with no mediating category variable. Then:
individual identity, not class, drives the answer; a class-only direction fails; the answer
does not resolve a category *before* the property in depth; and a late category-axis edit does
not flip the property. Composition is bounded to single resident reads — no chaining.

## Setup (reuse the s278 arc infrastructure)

Same as `general-composition-prereg.md`: build `d_E` = object-token residual diff-of-means of
a **real** entity E over cross-task declaratives; install via the keyed residual-write hook
(add `scale · d_E` at the nonce slot at layer `L≈9`); test on **held-out** few-shot clozes
(exemplar words disjoint from the test entities). Real-word ceiling gates each cell (cannot
test composition where the model lacks the real class→covering answer). **4B** (0.6B known too
weak — squish/patchscope-void scar).

**Entities → class → covering** (`f(g(X))` ground truth), balanced across three classes:

| class  | entities (test)                         | covering (label) |
|--------|-----------------------------------------|------------------|
| bird   | eagle, hawk, owl, crow, sparrow, robin  | feathers         |
| fish   | salmon, shark, tuna, trout, cod, carp   | scales           |
| mammal | wolf, fox, bear, tiger, rabbit, cat     | fur              |

Covering is a **closed 3-way** readout (`{feathers, scales, fur}`); few-shot exemplars use
**held-out** class members (e.g. parrot/goat/bass) so the test entities never appear.

## Gate 1 — BEHAVIORAL COMPOSITION (necessary, NOT sufficient)

Install E on the nonce; query `"A {nonce} is covered in __"`; grade against the class covering.

**Nulls (beside every number):**
- **matched-random install** — no coherent covering.
- **baseline** (bare, un-installed nonce) — chance / default headroom.
- **content-specificity (decisive within Gate 1)** — install E vs E′ of a **different class**
  on the same nonce → covering flips (feathers↔scales↔fur) **following the installed class**.
  A random content vector cannot; a class-carrying operand must.
- **real-word ceiling** — the actual entity token must resolve the covering (gates each cell).

**Gate-1 pass** ⟺ install accuracy ≫ random-install **and** baseline (pre-reg margins below),
content-specific, held-out, at/near the real-word ceiling. *This alone is Arm-1-like and does
**not** prove chaining.*

## Gate 2 — INTERMEDIATE-MEDIATION (the two-hop discriminator)

The load-bearing risk (`λ yardstick`): Gate 1 could be a rich content vector read at the
readout (a fancy fact), not a chain through an unstated intermediate. Three independent
mediation probes, all pre-registered; **≥2 must pass** (each null-gated):

- **2a — DEPTH ORDER (the intermediate is computed first).** Logit-lens the readout position
  across layers (`output_hidden_states` → unembed) for the **bridge** (class-word) tokens vs
  the **property** (covering) tokens. Two-hop ⟺ the bridge token's peak margin occurs at an
  **earlier** median layer than the property token's, with a positive gap, across entities,
  and beats a **shuffled-label** control (bridge/property token roles permuted). Grounds in the
  project's depth-scheduled frame (opcodes = circuits-in-compute, C8).

- **2b — INDIVIDUAL-INDEPENDENCE (mediation strips identity).** Build a **class centroid**
  `d_class = mean_{E∈class} d_E − global` (individual identity washed out; only the class axis
  survives). Install `d_class` on the nonce → the covering still resolves correctly at
  **≥ 0.66 of the full-content accuracy**. If a category-only direction (no individual fact)
  drives the property, the property is reached **via class**, not via individual lookup.
  Null: random matched-norm centroid.

- **2c — CAUSAL LATE BRIDGE-SWAP (the second hop reads the first hop's output).** With E
  installed at `L≈9`, add a **pure class-axis swap** `γ·(d_{c′} − d_c)` (centroid difference,
  individual-free) at a **late** layer `L_b` (> install; sweep e.g. {15,18,20}) at the readout
  position. Two-hop ⟺ the covering **flips** to `c′` (feathers→scales→fur) content-specifically,
  while a **random matched-norm** late add does **not** flip it, and the flip **follows the
  swapped class** (swap→fish gives scales, swap→mammal gives fur). A late category-axis edit
  flipping the property means the property-readout consumes a **class variable that persists to
  late layers** = hop-2 reading hop-1's product.

## Registers (`λ measure`)

- **Operand = VALUE** (installed `d_E`, `d_class`; s206/s269c) — value-register writes.
- **g (class inference) and f (class→covering) = ROUTING** — resident operations; readout =
  logits.
- **Bridge localization** — the transform is **distributed** and **late** (P-DSP-1: 0/128 heads
  necessary, transform L20–21). So 2a uses **depth** logit-lens and 2c uses **late zone-steer**,
  **never single-head** ablation — there are no transport heads to knock out.

## Guards (`λ yardstick`)

1. **Two-hop ≠ one-hop.** Gate 1 alone is explicitly insufficient; the verdict *requires*
   mediation evidence (Gate 2).
2. **Category-mediation ≠ literal sequential circuit.** We claim the property is **mediated by
   a class variable** (three converging signatures), **not** that we traced a discrete two-node
   circuit. Honest scope stated in the result.
3. **Nulls beside every number** (random install, baseline, shuffled-label depth control, random
   matched-norm late add); **real-word ceiling** gates each cell.
4. **Held-out** clozes + nonce carrier rule out template/lexical memorization.
5. **0.6B necessary-not-sufficient** (patchscope-void scar); full pass is a **RUNG**, not the
   claim. **Hook-not-weight** (gate (f) untouched); **4B not scale-final**.

## Verdict rules (FROZEN before any graded run)

- **Gate-1 (behavioral):** `install_acc > 0.66` AND `install_acc > random_install + 0.20` AND
  `install_acc > baseline + 0.20` AND `content_specificity > 0.5`.
- **Gate-2 probes (each pass condition):**
  - **2a:** `median(bridge_peak_layer) < median(property_peak_layer)` by a positive gap AND the
    gap exceeds the shuffled-label control.
  - **2b:** `centroid_acc ≥ 0.66 × full_content_acc` AND `centroid_acc > random_centroid + 0.20`.
  - **2c:** `bridge_swap_flip ≥ 0.66` content-specifically AND `random_late_add_flip < 0.34`.
- **VERDICT MULTI-HOP SUPPORTED** ⟺ **Gate-1 passes** AND **≥2 of {2a, 2b, 2c} pass**, all
  null-gated.
- **Outcomes:**
  - *Gate-1 pass + ≥2 Gate-2* → chained `f(g(X))` supported (rung): the resident routing
    composes the installed term through an **unstated intermediate** = "programmable machine"
    earns its chaining rung (still 4B, still hook-not-weight).
  - *Gate-1 pass + <2 Gate-2* → the operand composes on class-level properties but chaining is
    **not** demonstrably mediated (looks one-hop) — honest, scopes the tower, no chaining claim.
  - *Gate-1 fail* → covering is not composed at all at this layer/scale — revisit install
    strength (not scale, per s278 under-flip lesson).

## Files to build (once the pre-reg survives review)

- `wrapper/operand_multihop.py` — `d_E` build, keyed install, covering cloze (Gate 1 +
  content-specificity + ceiling), `d_class` centroid install (2b), late bridge-swap steer with
  random null (2c), logit-lens depth-order of bridge vs property tokens (2a), all verdict rules
  frozen above.
- Results → `results/ffn-bake/operand-multihop-qwen3-4b/`.

## Result (s279 — Qwen3-4B, `wrapper/operand_multihop.py`)

**VERDICT: MULTI-HOP SUPPORTED — Gate-1 passes AND all 3 mediation probes pass (3/3).**
The resident routing chains **two** sequential resident ops over **one** installed operand:
`g(X)` = the animal class (an **unstated** bridge inferred from `d_E`), `f(class)` = the
class covering. The final answer is **mediated** by the latent class variable — not read
directly off `d_E`. A genuine advance past s278's single-op Arm-2. Rung-level, hook-not-weight,
4B (not scale-final).

Real-word ceiling **0.944** (bird 1.0 / fish 0.833 / mammal 1.0; only `cod` voids → 17/18
entities valid).

| gate | metric | value | null | pass |
|---|---|---|---|---|
| **1** behavioral | install acc | **0.824** | rand 0.353 / baseline 0.353 | ✅ (+0.47) |
| **1** content-spec | both follow installed class | 0.656 (n=192) | ~0.11 chance | ✅ |
| **2a** depth-order | median class-peak L / covering-peak L | **30 < 33** (gap +3.0) | shuffled −3.0 | ✅ |
| **2b** centroid | class-centroid install acc | 0.667 (n=3) | rand 0.333 | ✅ |
| **2c** bridge-swap | late class-axis edit flips covering | **0.853** @L15 | random 0.088 | ✅ |

### The decisive (confound-immune) evidence
The load-bearing risk was "a rich content vector read many ways at the readout" (a fancy
one-hop fact, not a chain). Two signatures a fact-read **cannot** produce:
- **2c CAUSAL late bridge-swap (the strongest).** With E installed at L9, adding a **pure
  class-axis** swap (centroid difference, individual-free) at a **late** layer flips the
  covering to the swapped class — **0.853 @L15, 0.765 @L18, 0.676 @L20** — while a random
  matched-norm late add flips almost nothing (**0.088 / 0.059 / 0.059**), content-specifically
  (swap→fish gives scales, swap→mammal gives fur). A late category edit flipping the property
  means the property-readout **consumes a class variable that persists to late layers** =
  hop-2 reading hop-1's product. Strongest early (L15), decaying toward readout (L20) — the
  bridge is most editable *before* the covering is committed.
- **2a DEPTH-ORDER.** Class (bridge) token logit-lens margin peaks at median **L30**, covering
  at median **L33** — the intermediate is resolved **before** the property, consistently
  per-entity (covering-peak ≥ class-peak for 17/17), decisively beating the shuffled-label
  control (−3.0). Grounds in the depth-scheduled frame (opcodes = circuits-in-compute, C8).

### Honest edges
- **`mammal → fur` is the weak cell.** All **3** Gate-1 misses are mammals (wolf/fox/tiger)
  under-flipping to **"scales"**, and 2b's mammal centroid also mispredicts scales — the same
  **entity-specific install-strength under-flip** seen in s278 (not a category error; the
  `fur` direction is simply weaker than feathers/scales here). content-specificity (0.656) and
  centroid (0.667) are both dragged by this one cell; bird/fish are clean.
- **2b n=3** (only three classes) — a coarse test; passes but is the least-powered probe. The
  verdict does not rest on it (2a + 2c alone satisfy ≥2).
- **Depth gap is small (+3 layers) and late** (both L30–33 of 36) — consistent and shuffled-
  gated, but the two hops are close in depth (as expected for a distributed late transform,
  P-DSP-1).
- **Scope (unchanged):** category-**MEDIATION** via three converging signatures, **not** a
  literal traced two-node circuit; **hook-not-weight** (gate (f) untouched); **4B not
  scale-final**; 0.6B known too weak (squish). A **RUNG**, not the claim.

### Checklist move
Flips **"composes ARBITRARY programs"** from the s278 single-op rung toward genuine **chained
`f(g(X))`**: the installed term is composed through an **unstated intermediate**, the
mechanistic signature of a programmable machine (not a lookup). Still: no "programmable
compiler" until this holds **weight-serialized (f) and at scale (27B)** — both remain red.

## Status

Pre-registered s279; **RUN s279** — **MULTI-HOP SUPPORTED (3/3 Gate-2)** on Qwen3-4B via the
causal late bridge-swap (0.853 vs 0.088 random) + depth-order (class before covering) + centroid
individual-independence. Successor to `general-composition-prereg.md` (Arm 2 = one op; this =
chained two ops through an unstated intermediate). Next: strengthen the `fur`/mammal install
(layer/content, not scale); gate (f) weight-serialize + R5; cross-scale to 27B.

## Sessions
s278 (general-composition Arm 1/2 — reusable term + one-op novel composition), s279 (this
pre-reg — chained `f(g(X))` via latent category bridge).
