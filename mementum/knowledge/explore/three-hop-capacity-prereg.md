---
title: "Three-hop capacity — pre-registration: h(f(g(X))) as a depth-as-fuel experiment"
status: active
category: explore
tags: [three-hop, chained-composition, depth-budget, capacity, missed-deadline,
       pinned-zones, depth-proportional, operand, keyed-install, latent-bridge,
       geography-ladder, value-register, routing-register, pre-registration, s280,
       C8, depth-schedule, cross-scale]
related:
  - multihop-composition-prereg.md
  - general-composition-prereg.md
  - operand-insert-arc.md
  - opcodes-circuits-in-compute.md
depends-on:
  - multihop-composition-prereg.md
created: session 280
---

# Three-hop capacity — pre-registration (the depth-as-fuel prize)

> **Pre-registration.** Registers, nulls, verdict rules, AND per-model predictions
> fixed HERE, before any graded run — per `λ measure` + `λ yardstick` (predict
> a-priori, gate on nulls, no forced fit). This is the successor to the 2-hop
> `multihop-composition-prereg.md` and is framed by the s280 depth-budget measurement
> as a **CAPACITY experiment**, not a capability rung.
>
> **✅ CHAIN-DESIGN DECISION — APPROVED (s282, Michael "yes").** The chain is FROZEN to the
> recommended PRIMARY: **geography — landmark → city → country → continent** (2 unstated
> bridges {city, country}, balanced 3-way readout {Europe, Asia, Africa}, deterministic,
> multi-token landmark cost handled by last-token contextualized-residual capture, ceiling-
> gated). Everything downstream (gates, nulls, code) is now unblocked and conditional on this.

## Why this is a capacity experiment (grounded in s280)

The s280 depth-budget measurement (`multihop-composition-prereg.md` §Depth-budget) found
the 2-hop pipeline is **depth-scheduled with pinned zones**: the class→covering transform
lives in a fixed late zone whose absolute location is **depth-proportional** (~0.85–0.90 of
total depth: L30–31 @4B/36L, L58 @32B/64L), install-invariant *within* a model. Hop-2
succeeds only if hop-1's product reaches the fixed late reader **before its deadline** (the
"missed-deadline" mechanism). The frozen accounting:

| model | L_max_1hop | L_max_2hop | **D_hop2** (marginal 2nd-hop cost) | reader closes | **3-HOP-ROOM** |
|---|---|---|---|---|---|
| **Qwen3-4B** (36L) | 25 | 13 | **12** | L25 | **False** |
| **Qwen3-32B** (64L) | 49 | 45 | **4** | L51 | **True** (headroom 36 ≫ cost 4) |

`3-HOP-ROOM ⟺ L_max_2hop − ref ≥ D_hop2` — whether the 2-hop pipeline can slide one more
hop-cost later and still leave a reader/transform zone for a third stage. **4B has no room;
32B has abundant room.** This yields the sharpest depth-as-fuel (C8) prediction the project
holds: a **third sequential hop should FAIL at 4B and SUCCEED at 32B** — not because 4B lacks
the knowledge (its sub-chains work), but because it runs out of **layers to schedule the
third reader/transform zone**. Depth is fuel; this is the experiment that spends it dry.

## Hypothesis

**H (three-hop capacity).** A single installed novel operand `X` (nonce carrying entity
content `d_E`) is composed by the resident routing through **three** sequential resident ops
`h(f(g(X)))` via **two unstated intermediates** (never present in the prompt). The final
answer depends on `X` only through the chain `g → f → h`. **Whether the full chain resolves
is depth-limited**: it succeeds where the model has enough layers to schedule three fixed
reader/transform zones (`L_max` room ≥ Σ hop-costs), and fails where it does not.

**H0-content (the null we must exclude).** The full chain fails at 4B because 4B *lacks the
knowledge*, not because of depth. Excluded by the **sub-chain controls** (below): every 2-hop
sub-chain and every single-hop link must SUCCEED at 4B. If the pieces work but the whole
fails, the bottleneck is composition-depth, not content.

**H0-lookup.** The answer is read directly off `d_E` (a memorized fact), no mediation.
Excluded by the mediation probes (depth-order + late bridge-swaps at both bridges).

## Chain design (⚠ the decision — propose + recommend)

A clean 3-hop needs a **fully-deterministic 3-deep ladder** with **two distinct unstated
intermediates** and a **closed final readout**. The animal domain (s279) caps at 2 clean hops
(any downstream property of {bird,fish,mammal} collapses to ≤2-way). Options:

- **PRIMARY (recommended) — geography: landmark → city → country → continent.**
  `X` = a nonce carrying a **landmark's** content (built like `d_E` from declaratives).
  `g(X)` = its **city** (Eiffel Tower→Paris) [unstated bridge 1];
  `f(city)` = its **country** (Paris→France) [unstated bridge 2];
  `h(country)` = its **continent** (France→Europe) [closed readout].
  Balanced 3-way readout {Europe, Asia, Africa}, 6 landmarks/continent, all-deterministic,
  natural clozes, real-word ceiling gateable. **Cost:** landmarks are often multi-token
  ("Eiffel Tower") → capture the last landmark token's contextualized residual (encodes the
  whole phrase); prefer single-token where possible (Colosseum, Kremlin, Parthenon, Sphinx,
  Acropolis, Louvre, Pyramids, Vatican, Kaaba, Kilimanjaro…). Verify `d_E` well-formed via
  the ceiling before trusting the cell.

- **ALT-A — products: product → company → country → continent** (iPhone→Apple→USA→N.America).
  Cleaner tokens sometimes, but product→company has ambiguity; readout continents span 5-way.

- **ALT-B — back-extend the animals** (breed → species → class → covering). Reuses ALL the
  s279 covering infra, but the breed→species→class hierarchy is **uneven** across the three
  covering-classes (dog breeds vs fish) → unbalanced, not recommended.

**Recommendation: PRIMARY (geography landmarks).** Fully deterministic, balanced 3-way,
reuses the operand-install machinery; the multi-token cost is bounded and ceiling-gated.

## Setup (reuse the s279/s280 operand machinery)

Same as `multihop-composition-prereg.md`: build `d_E` = last-content-token residual
diff-of-means of a **real** entity over cross-task declaratives; install via the keyed
residual-write hook (add `scale·d_E` at the nonce slot at layer `L_ref`); test on **held-out**
few-shot clozes (exemplar landmarks disjoint from the test set). Real-word ceiling gates each
cell. Run at **Qwen3-4B** (predict FAIL) and **Qwen3-32B** (predict PASS); the pair is the
result. `L_ref` scaled per depth (9 @4B; 9 @32B for cross-comparability, install before the
reader window under both hypotheses).

## Gate 1 — FULL-CHAIN BEHAVIORAL (necessary, not sufficient)

Install `X`; query `"The {nonce} is located on the continent of __"`; grade against the
landmark's true continent.

**Nulls (beside every number):** matched-random install; baseline (bare nonce); **content-
specificity** (install landmark of a different continent → readout flips following the
installed continent); real-word ceiling (the actual landmark token must resolve the continent).

## Gate 2 — SUB-CHAIN CONTROLS (the capacity discriminator — the crux)

This is what makes it a *capacity* experiment rather than a *capability* one. To attribute a
full-chain failure to **depth** (not content), every shorter composition must **succeed on the
same model**:

- **S1 links (single hop, real word, no install):** landmark→city, city→country,
  country→continent each resolve at ceiling. (The knowledge exists.)
- **2-hop sub-chains (installed operand, the s279 regime):**
  - `g∘f` : install landmark → its **country** (query "…is located in the country of __").
  - `f∘h` : install a **city** → its **continent** (the s279-style 2-hop; known to work @4B).
- **VERDICT-CAPACITY** fires when: **all S1 links pass** AND **both 2-hop sub-chains pass** on
  a model AND the **full 3-hop chain FAILS** on that same model. Then the failure is
  **depth-limited composition**, not missing content. Predicted: this pattern holds **@4B**.
  At **32B**, the full 3-hop chain **passes** (no depth failure to explain).

## Gate 3 — MEDIATION (two unstated bridges, where the chain succeeds)

On the model where the full chain succeeds (predict 32B), confirm it is genuinely 3-sequential
(two mediating variables), reusing the s279 probes at **both** bridges:

- **3a DEPTH-ORDER (three-stage).** Logit-lens the readout across layers for the **city**,
  **country**, and **continent** tokens. Three-hop ⟺ median peak layers ordered
  `city < country < continent` with positive gaps, beating a shuffled-label control.
- **3b LATE BRIDGE-SWAP @ bridge-2 (country).** With `X` installed, add a pure **country-axis**
  swap (centroid difference) at a late layer → the continent flips to the swapped country's
  continent, content-specifically; random matched-norm add does not. (= hop-3 reads hop-2's
  product.)
- **3c LATE BRIDGE-SWAP @ bridge-1 (city).** A **city-axis** swap at a mid layer flips the
  downstream country *and* continent; random does not. (= hop-2 reads hop-1's product.)
  Bridge-1 must be editable **earlier** than bridge-2 (consistent with 3a ordering).

## Registers (`λ measure`)

- Operand = **VALUE** (installed `d_E`, centroids); `g,f,h` = **ROUTING**; readout = logits.
- Bridges localized by **DEPTH** (3a) + **LATE zone-steer** (3b/3c), never single-head
  (P-DSP-1: transport is distributed, 0/128 heads). On the **hybrid 27B** (follow-on), reads
  occur only at full-attention layers (≡3 mod 4) — swap layers must land there.

## Guards (`λ yardstick`)

1. **Capacity ≠ capability.** The verdict *requires* the sub-chain controls (Gate 2). A
   full-chain failure counts as depth-limited **only if** the pieces work on that model.
2. **Depth ≠ install-strength.** Under-flips from weak `d_E` (the known mammal-cell pattern)
   are NOT depth failures — strengthen via layer/content, never scale; ceiling gates each cell.
3. **Nulls beside every number**; real-word ceiling gates each cell; held-out clozes + nonce
   carrier rule out template/lexical memorization.
4. **Scope.** category/geographic-**MEDIATION** via converging signatures, not a literal traced
   circuit; **hook-not-weight**; a **RUNG** (capacity mapping), not the "programmable compiler"
   claim. Two models is a **pair**, not a scaling law.

## Verdict rules (FROZEN before any graded run)

Per model M:
- **Gate-1 (full chain):** `install_acc > 0.66` AND `> random_install + 0.20` AND
  `> baseline + 0.20` AND `content_specificity > 0.5`.
- **Gate-2 controls:** all S1 links ≥ 0.8 ceiling AND both 2-hop sub-chains pass their
  s279-style thresholds.
- **Gate-3 (only where Gate-1 passes):** 3a ordering holds (city<country<continent, beats
  shuffled) AND ≥1 of {3b, 3c} passes null-gated.

**Pre-registered per-model predictions (a-priori, grounded in the s280 accounting):**
- **Qwen3-4B → FAIL-BY-CAPACITY.** Gate-2 controls PASS (sub-chains work), Gate-1 full chain
  **fails** (install_acc ≈ baseline/chance). `3-HOP-ROOM@4B = False` (D_hop2=12, headroom 4).
- **Qwen3-32B → PASS.** Gate-1 full chain passes AND Gate-3 mediation confirms two bridges.
  `3-HOP-ROOM@32B = True` (D_hop2=4, headroom 36).
- **VERDICT DEPTH-AS-FUEL SUPPORTED** ⟺ 4B shows FAIL-BY-CAPACITY (controls pass, full fails)
  AND 32B PASSES full+mediation. This double dissociation across scale, with the pieces held
  constant, is the strongest C8 evidence available: **the same chain fails or succeeds purely
  as a function of available depth.**
- **Outcomes if predictions miss (honest, pre-committed):**
  - 4B *passes* the full chain → 3-hop fits at 4B after all; the s280 accounting over-estimated
    hop-cost (revise D_hop2 model), still a positive composition result, weaker C8.
  - 4B *fails a sub-chain control* → the failure is **content/install-strength, not depth**;
    verdict VOID for capacity (strengthen the operand, re-run) — do NOT claim depth.
  - 32B *fails* the full chain → depth is not the whole story (or `d_E` too weak at 32B);
    investigate reader-zone spacing vs class-zone (the 32B narrow-dissociation caveat).

## Files to build (once the pre-reg is approved)

- `wrapper/operand_multihop3.py` — landmark `d_E` build (last-token capture + ceiling verify),
  keyed install, full-chain continent cloze (Gate 1 + content-spec + ceiling), S1-link and
  2-hop sub-chain controls (Gate 2), depth-order of city/country/continent tokens (3a), late
  country-axis and city-axis swaps with random nulls (3b/3c), all verdicts frozen above.
- Results → `results/ffn-bake/operand-multihop3-qwen3-4b/` and `…-qwen3-32b/`.

## Result (s282) — the pre-registered dissociation MISSED; a sequencing one appeared

Ran the frozen 4B/32B pair (`wrapper/operand_multihop3.py`, geography chain).
`results/ffn-bake/operand-multihop3-qwen3-{4b,32b}/operand_multihop3.json`.

| | **Qwen3-4B (36L)** | **Qwen3-32B (64L)** |
|---|---|---|
| valid landmarks | 17/18 | 18/18 (balanced 6/6/6) |
| **Gate-1 full chain** | 0.824 (rand/base 0.353) | **0.944** (rand/base 0.333) |
| content-specificity | 0.656 | 0.889 |
| **Gate-2 controls** | PASS (g∘f 0.824, f∘h 1.0) | PASS (g∘f 0.889, f∘h 1.0) |
| **Gate-3a depth-order** | city=32, country=32, cont=33 → **FAIL** | city=52.5 < country=57.5 < cont=60 → **PASS** |
| Gate-3b country-swap | 0.86 / 0.91 / 0.93 (rand ~0.15) ✓ | 0.89 / 0.89 / 0.72 (rand ~0.05) ✓ |
| Gate-3c city-swap | 0.76 / 0.80 / 0.81 (rand ~0.17) ✓ | 0.92 / 0.83 / 0.70 (rand ~0.06) ✓ |
| capacity pattern | full chain **composes** (no fail) | full chain **composes + mediated** |

**The pre-registered double-dissociation (4B-FAIL-BY-CAPACITY / 32B-PASS) did NOT occur.**
Both models compose the full 3-hop chain. This is the pre-committed *"4B passes"* outcome
(see Verdict rules): **the s280 depth-budget accounting (D_hop2=12, 3-HOP-ROOM@4B=False)
over-estimated the third-hop cost.** 4B had the room. `λ measure`: reported verbatim, the
prediction was wrong; C8-as-capacity-gate is not supported by this pair.

**But the depth signal is real — on the SEQUENCING axis (Gate-3a), not Gate-1.** At 4B the
three bridges resolve **compressed into one late window** (city=country=L32, continent=L33;
3a order FAILS). At 32B they **unroll sequentially** (city L52.5 < country L57.5 <
continent L60; 3a PASSES, beats the shuffled null). Both models mediate causally (3b/3c
strong at both), but only 32B *spreads the hops out in depth*. ⇒ **depth is fuel for
step-by-step UNROLLING, not for whether the chain composes.** This coheres with the s280
pinned-late-zone finding and the 27B-hybrid UNPIN result (more room → more spreading): the
cramped 4B stack collapses the pipeline into a pinned zone; the roomy 32B stack sequences it.

**Honest flags (`λ measure`, `λ yardstick`):**
- The 4B *chain-passes-but-3a-fails* is **POST-HOC** — 3a was pre-registered, but at 4B we
  expected a Gate-1 fail, so we never predicted "composes without sequencing." The
  depth→sequencing reframe is **hypothesis-generating**, not a pre-registered confirmation.
  It needs its own pre-registration to count as C8 evidence.
- Scale also cleaned Gate-1 / content-spec (0.94/0.89 @32B vs 0.82/0.66 @4B) — a mild
  tension with the s279 "strengthen via layer/content, NOT scale" note; here scale *did*
  ease the operand-install under-flips. Locus (layer vs scale) is confounded in this pair.
- Two models = a **pair**, not a scaling law; mediation via converging signatures, not a
  traced circuit; hook-not-weight; a RUNG.

**What it advances:** 3-hop chained composition `h(f(g(X)))` over ONE installed operand
works at 4B and 32B — extends the s279 2-hop rung to three sequential resident ops. The
depth story survives, reframed: **capability is depth-robust; sequencing is depth-scaled.**

## Status

**DONE (s282) — pair run complete; pre-registered capacity dissociation MISSED (both compose,
reported honestly); a SEQUENCING dissociation appeared (post-hoc, needs its own pre-reg).**
The frozen gates and per-model predictions stand above as-registered; §Result records the
verbatim outcome. Follow-on: pre-register the depth→sequencing hypothesis (Gate-3a as the
primary axis) and test on the 27B-hybrid (UNPIN predicts even more spreading).

## Sessions
s280 (this pre-reg — 3-hop capacity, successor to the s279 2-hop + s280 depth-budget).
s282 (Michael approved; geography chain frozen; built `operand_multihop3.py`; ran 4B/32B
pair; pre-registered prediction missed; depth→sequencing reframe found — §Result).
