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

## Depth-budget (s280 — pre-registered BEFORE the run; `wrapper/operand_depthbudget.py`)

> **Question (gates the 3-hop d1 design):** how many layers does each hop consume, and is
> there room for a third? The s279 pipeline occupies nearly the whole 36-layer stack:
> install L9 → bridge causally live L15–20 (2c window already decaying at L20, closing edge
> unmeasured) → class legible L30 → covering legible L33. The s279 layersweep (L5–15,
> weak-cell-motivated) saw covering degrade at install ≥ L13 but is **confounded for budget
> purposes**: it varied install layer AND `d_E` build layer together and read only the final
> hop — fuel-exhaustion vs content/basis-drift are different quantities (`λ measure`).

**Arm A — stage-resolved install-layer sweep.** Install L ∈ {5, 9, 13, 17, 21, 25, 29, 33},
matched-build `d_E` (captured at the install layer; ALL sweep layers captured in one pass per
declarative — no extra forwards), basis-drift covariate = cos(d_E@L, d_E@9) per entity. Per
install layer, THREE reads: **hop-1 behavioral** = class query `"A {x} is a kind of ___"`
graded over {bird, fish, mammal} (held-out exemplar prefixes, real-word ceiling gated first);
**hop-2 behavioral** = covering query (s279 instrument unchanged); **logit-lens peaks**
(class + covering, 6 strong entities: eagle, hawk, salmon, shark, bear, cat — the weak
mammal trio excluded so install-strength does not masquerade as budget).

**Arm B — bridge read-window fine sweep.** Standard install L9; class-axis swap (2c
machinery) at L_edit ∈ {11, 13, …, 33}; 6 strong entities × 2 swap targets, matched-norm
random null beside, single prefix (granularity read, noted).

```
Fuel accounting (definitions FROZEN):
  L_max_1hop  = max install L with class-acc  ≥ 0.7·class-ceiling
  L_max_2hop  = max install L with cover-acc  ≥ 0.7·cover-acc@L9
  D_hop2      = L_max_1hop − L_max_2hop          (marginal cost of the second hop)
  L_close     = min L_edit with flip ≤ random+0.10 (hop-2's bridge-read window closes)

BUDGET-VISIBLE        ⟺ ∃ install band where class-acc ≥ 0.7·ceiling ∧ cover-acc ≤ 0.5·(@L9)
                         (hop-2 fails while hop-1 succeeds = fuel, not install failure)
DEPTH-BUDGET-UNMEASURED ⟺ class and covering collapse together everywhere
                         (content/basis drift dominates; budget not measurable this way)
PIPELINE-SLIDES (P2)  ⟺ median class logit-lens peak increases with install L
                         (Spearman ρ > 0.8 over surviving layers) — the program moves,
                         it is not pinned to absolute layers
3-HOP-ROOM-AT-4B      ⟺ L_max_2hop − 9 ≥ D_hop2
                         (the 2-hop pipeline can slide one hop-cost later ⇒ a third
                          hop-sized stage fits after install at L9; else predict d1
                          FAILS at 4B → design at 27B, couples (d) to (c))
```

**Predictions (a priori):** BUDGET-VISIBLE with L_max_1hop ≈ 21–29 and L_max_2hop ≈ 13–17
(from the layersweep + 2c decay); PIPELINE-SLIDES holds (circuits-in-compute: the reduction
trajectory is scheduled, not pinned); L_close ≈ 21–27 (between the 2c decay and the class
legibility onset). Honest alternative: peaks may NOT slide (stages pinned to absolute
depth-bands per A1 zone structure) — that would itself be a C8 finding (stage zones are
architectural, and the budget is then a hard zone-capacity, worse for 3-hop at 4B).

### Depth-budget Result (s280 — `wrapper/operand_depthbudget.py`, Qwen3-4B, commit 46910e9)

| install L | 5 | 9 | 13 | 17 | 21 | 25 | 29 | 33 |
|---|---|---|---|---|---|---|---|---|
| class acc (hop-1) | 1.0 | 1.0 | 1.0 | **1.0** | **0.889** | **0.833** | 0.611 | 0.389 |
| cover acc (hop-2) | 0.824 | 0.824 | 0.647 | **0.353** | **0.353** | **0.353** | 0.353 | 0.353 |
| class peak (lens) | 30 | 30 | 30 | 31 | 31 | 31.5 | 32 | 35 |
| drift cos vs L9 | 0.61 | 1.0 | 0.67 | 0.61 | 0.57 | 0.50 | 0.41 | 0.29 |

Arm B bridge-read window: flip 0.917–1.0 across L11–21 (random 0.0 throughout), **sharp
close L23 (0.25) → L25 (0.0)**. Frozen accounting: **L_max_1hop=25, L_max_2hop=13,
D_hop2=12, L_close=25.**

- **BUDGET-VISIBLE = True (clean).** Install L17–25: hop-1 completes (class 1.0–0.833)
  while hop-2 sits at chance — fuel exhaustion measured stage-resolved, not install
  failure. **Drift control:** cos ≈ 0.61 at *both* L5 (composes 0.824) and L17 (chance) →
  basis drift does not explain the cliff.
- **PIPELINE-SLIDES = False — in the strongest form.** The class peak is **constant at
  L30–31 for every install layer L5→L25** (zero variance over surviving layers, not a
  failed correlation). The pre-registered honest alternative fired: **stages are PINNED
  to absolute depth zones** (A1 zone structure). The compute does not run a program
  forward from the install point; the class→covering transform lives in a fixed late
  zone. A C8 finding: the budget is a **hard zone-capacity**, not sliding fuel.
- **Mechanism = MISSED DEADLINE.** Hop-2's bridge-reader operates at L11–21 and is gone
  by L23–25. Install at L17 leaves too little room for hop-1 to write the bridge before
  the reader's deadline — the class *still resolves* (peak L31, behaviorally 1.0) but
  arrives **after the reader has passed** → chance covering. Fuel is not "layers
  remaining," it is "can each stage's product reach the next fixed reader in time."
- **3-HOP-ROOM-AT-4B = False** (L_max_2hop − 9 = 4 < D_hop2 = 12). d1 3-hop is a
  **predicted negative at 4B**. Sharper than the frozen rule anticipated: since stages
  are pinned (not sliding), a third sequential hop needs a reader/transform zone that
  does not exist above L33 at 4B — no install layer fixes that.
- Instrument note: lens peak search restricted to post-install layers (pre-run fix,
  smoke-surfaced: bare-nonce prior produced a spurious early class peak).

**Consequence for d1:** run 3-hop as the **capacity experiment**, not a capability rung:
pre-register FAIL at 4B (this measurement's prediction) and SUCCESS at 27B (more layers →
either more zones or wider ones — A1 27B zones are broad). A 4B-fail/27B-pass pair would be
the strongest depth-as-fuel (C8) evidence the project holds, and it merges (d) with (c).

### Cross-scale depth-budget (s281 — `wrapper/operand_depthbudget.py`, Qwen3-32B, commit 8ceaaec)

Clean scale replication on **Qwen3-32B** (64L, dense **uniform full attention** — same
architecture as 4B, isolating the *scale* variable; `--ref-layer 9`, install/swap swept
{5,9,…,57}/{11,15,…,59}). The mechanism **replicates and refines**:

| | **4B (36L)** | **32B (64L)** |
|---|---|---|
| class-transform zone | pinned **L30–31** (0.85 depth) | pinned **L58** (0.90 depth) |
| pinned *within* model (∀ install)? | yes (L5–25) | yes (L5–49) |
| cover-acc holds until install L | 13 | **45** |
| reader window / close | L11–21 / **L25** | L11–47 / **L51** |
| **D_hop2** (marginal 2nd-hop cost) | **12** | **4** |
| L_max_1hop / L_max_2hop | 25 / 13 | 49 / 45 |
| **3-HOP-ROOM** | **False** | **True** (headroom 36 ≫ cost 4) |

- **Zones are depth-PROPORTIONAL, not absolute-layer-locked.** The class→covering transform
  sits at ~0.85–0.90 of total depth in *both* models (L30–31 @4B, L58 @32B), install-invariant
  within each. This **refines** the s280 "pinned zones" finding: pinned *within*-model,
  depth-proportional *across*-model. The A1 zone structure scales with the stack; it is not
  locked to absolute layer indices.
- **Depth is fuel — quantified.** The marginal cost of the second hop collapsed **12 → 4**
  layers, and the missed-deadline threshold moved **L25 → L51**. 32B tolerates install as late
  as L45 where 4B failed at L17. Deeper model ⇒ each hop is *cheaper* in install-headroom, and
  the deadline lands later.
- **The missed-deadline mechanism replicates**: install past the reader-close (L51 @32B) →
  hop-1's product reaches the late class zone (L58) after the reader has passed → chance cover.
  Same physics as 4B, deadline scaled with depth.
- **3-HOP-ROOM = True @32B** (L_max_2hop − ref = 36 ≥ D_hop2 = 4) — the pre-registered
  **4B-FAIL / large-PASS** contrast is confirmed at the accounting level. This directly seeds
  the `three-hop-capacity-prereg.md` predictions.
- **Honest note on the frozen verdict.** At 32B `BUDGET-VISIBLE=False / UNMEASURED=True` fired
  — NOT because budget is unmeasurable, but because with so much room the hops **stay coupled**
  (class and cover degrade together only once install itself enters the terminal zone, ≥L49).
  The dissociation band that made 4B's budget "visible" is narrow/absent in the roomy 32B. The
  null **is** the "more room" finding; reported verbatim, interpreted, not spun. (`λ measure`:
  the rule was tuned to the cramped regime.)

Architecture-robustness follow-on: **Qwen3.6-27B** (qwen3_5 *hybrid*: linear attn + full attn
every 4th of 64L) — instrument made architecture-robust via `resolve_parts` (dense
`model.model.layers` vs hybrid `model.model.language_model.layers`); **smoke confirms it runs
on the hybrid** (ceilings 1.0, hooks fire). Smoke hint: the class peak **slid** with install
(L47.5→L53) — *unlike* the pinned dense models — suggesting sparse attention loosens zone
pinning. **Full 27B run was in progress at the s281 boundary (not yet complete).**

## Status

Pre-registered s279; **RUN s279** — **MULTI-HOP SUPPORTED (3/3 Gate-2)** on Qwen3-4B via the
causal late bridge-swap (0.853 vs 0.088 random) + depth-order (class before covering) + centroid
individual-independence. Successor to `general-composition-prereg.md` (Arm 2 = one op; this =
chained two ops through an unstated intermediate). **s280: depth-budget RUN** — stages PINNED
to absolute zones (class peak L30–31 ∀ install L5–25), missed-deadline mechanism (bridge-reader
window L11–21, closes L23–25), **3-HOP-ROOM-AT-4B = False** → d1 3-hop = capacity experiment
(pre-register 4B-fail / 27B-pass; merges (d) into (c)). Still open: mammal content build;
cross-scale 27B. **s281: cross-scale depth-budget RUN on Qwen3-32B** — zones depth-PROPORTIONAL
(pinned within-model, L30@4B→L58@32B), depth-as-fuel quantified (D_hop2 12→4), 3-HOP-ROOM
True@32B → 4B-FAIL/32B-PASS pair pre-registered in `three-hop-capacity-prereg.md`. Instrument
made architecture-robust (`resolve_parts`); Qwen3.6-27B hybrid smoke passes, full run pending.

## Sessions
s278 (general-composition Arm 1/2 — reusable term + one-op novel composition), s279 (this
pre-reg — chained `f(g(X))` via latent category bridge), s280 (depth-budget: pinned zones +
missed deadline; no 3-hop room at 4B), s281 (cross-scale depth-budget @32B: zones
depth-proportional, depth-as-fuel D_hop2 12→4, 3-HOP-ROOM True@32B; 27B hybrid smoke +
instrument architecture-robust; 3-hop capacity pre-reg drafted).
