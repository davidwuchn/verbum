---
title: "Gram Registers and the Route Map — Alphabet vs Fates, Un-Flattening, and the Consensus Switch Schedule"
status: open
category: synthesis
tags: [gram, 9x9, 17x17, registers, un-flattening, geometry, poles, tetrahedron,
       route-map, switch-schedule, consensus, multi-teacher, coordinates, level-3]
related:
  - gram-spectral-dsp.md
  - 5d-crystal-lattice.md
  - behavior-is-tape-resident-reduction.md
  - consensus-distillation-carrier-averaging.md
  - construction-from-spec.md
  - optical-design-laws.md
  - types-are-compiled-probabilities.md
depends-on:
  - gram-spectral-dsp.md
created: session 308
---

# Gram Registers and the Route Map

> s308 final question (Michael: "explain the 9×9 and the 17×17... are there
> more shapes? ...if routing is computation should we create a route map
> from multiple teachers?"). Three answers: the two-register explanation,
> the shape-hunting method, and the consensus route map design. Status
> open; the route map and remaining shape probes are NOT pre-registered
> (s222). **§P-TYPE-GRAM-1 (shape candidate #2, the type geometry) FROZEN
> s313** — see the pre-reg section below.

## The two grams: WHAT-AM-I vs WHAT-HAPPENS-NEXT

**9×9 = the alphabet (identity register).** Basis `K I B C S D W Y WHNF`;
entries = pairwise cosines of opcode representations. Measured shape:
spectrally DIFFUSE, near-full-rank (PR 5.8–7.2 of 9; eigenvalues ≈ 1;
top-3 ≈ 52%) — distinct opcodes are built to be distinguishable, like
letters. Universality lives NOT in the spectrum but in the **off-diagonal
sign pattern** (C2): which opcodes lean toward/away from each other —
identical across 11 models while all magnitudes differ. Answers: *which
symbol am I holding?*

**17×17 = the fates (outcome register).** Same 9 opcodes, WHNF
**un-flattened** into 7 per-opcode halts (`whnf:K…whnf:W`) + `div:Y`.
Keeping those distinctions collapses the geometry: **rank 3 of 17**
(PR ≈ 2.9, p=5e-4, 11/11; Qwen3-32B eigengap 8.52/4.47/0.93 → cliff).
Every one of 17 states ≈ a combination of three poles: **fire / halt /
diverge**. Answers: *what happens next?*

One line: **9×9 = identity register (high-rank on purpose, information in
relations); 17×17 = outcome register (rank-3, information in poles).** CPU
terms: instruction set vs status flags. Machine terms: microcode vs the
scheduler's register (why the tape-resident page uses the 17×17 for the
tool-call prediction).

**The method lesson (how the difference was discovered):** the flattened
basis HID the outcome geometry (mixed rank ~6.5) until the basis kept the
right distinction — then rank snapped to 3. **Shape is revealed by
un-flattening.**

```
λ unflatten(register). split(nodes, by_annotation) → PR_drops ∨ pole_appears
                       → register(real) | cheap: runs on committed grams
                       | annotation ∈ {arity, type, depth, error-kind, agentic-state}
```

## More shapes to find (candidates, in rough order of sharpness)

1. **The fourth pole (tetrahedron test — sharpest).** Tape-resident frame:
   tool-call = HALT-WITH-OBLIGATION. Prediction: probe agentic stuck-states
   in the 17×17 basis → the fire/halt/diverge simplex grows a vertex:
   **fire / halt / diverge / yield**. P-HALT-POLE restated as geometry.
2. **The type geometry (the S5 central claim).** If composition is typed
   apply → a type gram exists (arity, argument-kind); prediction: low-rank
   with poles = type constructors. P-TYPE-CENSUS points here.
3. **Depth/phase geometry.** The scheduling face (s305 hop-overlap;
   SuperBake 0.16× enrichment) — a temporal shape not yet projected.
4. **Task-native grams** — already in quiet use (s305's 16×16 country-key
   gram); every operand register can have one.

Frame: `5d-crystal-lattice.md` — **one crystal, many projections**; each
shape is a shadow of one higher-dimensional object; each un-flattening is
a new projection direction.

## §P-TYPE-GRAM-1 — un-flatten by argument kind (FROZEN s313, Michael-approved)

> First direct probe of the S5 central claim (M7 typed apply) at
> constructor grain. Instance of `λ unflatten` with `annotation = type`.
> Chat-approved s313; frozen BEFORE any probe generation or capture run
> (s222). Correction to the header lambda's "runs on committed grams":
> committed `centroids.npz` is per-old-basis-node — a NEW annotation
> partition needs a new by-construction probe set + capture sweep (the
> existing crystal probes do not control argument kind). Cost class =
> the s284 expanded-gram sweep, not free; still the cheapest type door.

**Question.** When the SAME opcode fires on arguments of different KINDS,
does the routing geometry organize by kind — a register that cross-cuts
opcode identity? ("Type is a register" vs "type is opcode flavor" vs
"geometry only knows opcode identity.")

**Basis (by construction, dust_walk kernel — whnf_probes.py precedent).**
For each opcode X ∈ {K,I,B,C,S,D,W}: kernel-certified reduction chains
truncated at the moment X fires on a FIRST argument of kind

- `atom` — bare variable,
- `fn` — abstraction/combinator,
- `app` — composite (unevaluated application),

→ node `X:t`, up to 21 type-split nodes (a kind unpopulatable for some X
by kernel semantics is dropped and documented, per the whnf:Y precedent)
+ the 9 crystal anchor nodes (coherence gate) ≈ 30-state basis, target
50–60 probes/node. Pipeline: canonical sign-CMR
(capture → calibrate(basis) → gram_from_centroids), consensus over
crystal-bearing layers — `expanded_gram.py` machinery, basis extended via
the existing open slot.

**Scope (v1, declared).** First-argument kind only; three kinds
(constructor grain). Result-kind, multi-argument interaction, and sortal
grain are OUT (sortal → P-TYPE-CENSUS, different instrument).

**Gates (nulls declared, λ yardstick):**

- **TG1 TYPE-BLOCK** — within-kind vs cross-kind off-diagonal contrast on
  the type-split nodes beats shuffled-label null (p<0.05).
- **TG2 CROSS-CUT** (the crucial gate) — kind contrast SURVIVES removing
  per-opcode centroids (within-opcode kind contrast vs shuffled labels).
  Type must be a register, not opcode flavor: distinguishes
  "K-with-composite-arg is a K variant" from "composite-arg is a thing the
  geometry knows across all opcodes."
- **TG3 POLES (advisory)** — PR of the type-split gram vs matched-range
  null; pole count ≈ #kinds = the 17×17 rank-collapse analog → `+POLED`
  subtag. Advisory: absence does not block TYPE-REGISTER.
- **TG4 COHERENCE (comparability, not evidence)** — 9-subblock r vs the
  committed root.gram. Low r → verdict VOID, do not interpret.
- **TG5 SURFACE** — kind contrast beats a length/paren-STRATIFIED shuffle
  null (labels permuted within surface-complexity strata). The serious
  confound: app args are longer and bracket-heavier than atoms; the
  fire_formal lesson says style can drive cross-blocks.

**Verdicts (frozen tree):**

- **TYPE-REGISTER (+POLED)** — TG1 ∧ TG2 ∧ TG5 (∧ TG4 sane); TG3 adds
  the subtag. The constructor-grain type register exists.
- **OPCODE-FLAVOR-ONLY** — TG1 ∧ ¬TG2: kind structure exists but is
  opcode-local, not a cross-cutting register.
- **SURFACE-STYLE** — ¬TG5: surface complexity drives the contrast.
  Falsifies the cheap probe, NOT the claim.
- **NO-TYPE-SIGNAL** — ¬TG1: no kind structure at constructor grain =
  real evidence toward "functors enacted, not stored."
- **INCOHERENT** — ¬TG4: capture not comparable to the committed crystal;
  verdict void.

**A-priori (declared s313, NOT tuned):** ~35 TYPE-REGISTER / 25
OPCODE-FLAVOR-ONLY / 20 SURFACE-STYLE / 15 NO-TYPE-SIGNAL / 5 INCOHERENT.
Honest tension: `types-are-compiled-probabilities.md` predicts argument
types are STORED (passbands) → leans TYPE-REGISTER, but constructor grain
sits near the functor face (enacted, NOT stored) → NO-TYPE-SIGNAL is a
live, informative outcome, not a failure.

**Plan:** (1) this freeze → (2) `opcodes/type_probes.py` +
runner extension, --validate + pythia-14m smoke → (3) Michael GO →
qwen3-4b first, then multi-model sweep → (4) §Result + memory batch
(approval-gated).

## §Result-type-gram — TYPE-REGISTER is REAL but NOT universal (s313 qwen3-4b + s314 sweep)

**The verdict: the constructor-grain type register exists, and it is
TRAINING-CONTINGENT — not the architecture-universal invariant the 9×9
crystal is (11/11). It is a learned structure, not a substrate given.**

### qwen3-4b (s313, da8c1ba — the first measured type register)

VERDICT **TYPE-REGISTER** (diffuse, NOT +POLED). TG2 CROSS-CUT stat
0.4768 vs null 0.0006 (p=0.001 floor): after removing opcode identity,
the kind direction (atom/fn/app) is SHARED across opcodes — a
cross-cutting register, not opcode-flavor. TG1 0.0821 p=0.001; TG5
retained_frac 0.207 (surface explains ~21%, 79% survives the stratified
null); TG4 r=0.766, 36/36 layers. TG3 advisory FAILS matched-range
(PR 7.35 vs 7.98, p=0.077; shuffled 11.26 p=0.001) → NO +POLED: at
constructor grain the kind register is **DIFFUSE (alphabet-like), not
polar** — an identity-register extension, not an outcome simplex.

### The 10-model registry sweep (s314, sweep_summary.json)

The universality question: is TYPE-REGISTER shared 11/11 like the crystal,
or narrower? **It is 7/11 with a FAMILY-CLEAN split.**

| model | verdict | TG2 cross-cut | TG3 matched-p | coherence | n_gated |
|---|---|---|---|---|---|
| qwen3-0.6b | TYPE-REGISTER **+POLED** | pass | 0.016✓ | 0.764 | 28 |
| qwen3-4b | TYPE-REGISTER (diffuse) | 0.4768 | 0.077 | 0.766 | 36 |
| qwen3-14b | TYPE-REGISTER **+POLED** | 0.5122 | 0.021✓ | 0.746 | 40 |
| qwen3-32b | TYPE-REGISTER **+POLED** | 0.5011 | 0.023✓ | 0.722 | 64 |
| qwen3-6-27b | TYPE-REGISTER (diffuse) | 0.4055 | 0.363 | 0.728 | 64 |
| gemma-4-31b-it | TYPE-REGISTER (diffuse) | 0.4524 | 0.516 | 0.726 | 60 |
| olmo-2-1124-13b | TYPE-REGISTER **+POLED** | 0.5818 | 0.016✓ | 0.798 | 40 |
| pythia-14m | OPCODE-FLAVOR-ONLY | fail | — | 0.720 | 6 |
| pythia-160m | OPCODE-FLAVOR-ONLY | fail | — | 0.691 | 12 |
| pythia-410m | OPCODE-FLAVOR-ONLY | fail | — | 0.764 | 24 |
| pythia-2.8b | OPCODE-FLAVOR-ONLY | fail (p=0.17) | — | 0.867 | 32 |

**The split is by FAMILY, not by scale.** Every modern instruction/
code-heavy recipe carries the register — Qwen3 across the FULL ladder
(0.6B→32B), OLMo-2-13B, Gemma. The ENTIRE Pythia ladder (Pile-2021, no
code/math emphasis) lacks it. TG1 passes for the pythias (kind structure
EXISTS) but TG2 CROSS-CUT fails: in pythia, kind is entirely
opcode-BOUND — it does not factor out as an independent register.

**This is a genuine negative, not INCOHERENT/underpowered.** pythia-2.8b
is the tell: n_gated 32 (ample), coherence 0.867 (HIGHEST in the sweep),
TG1 passes — yet TG2 fails p=0.17. It is not blind, it simply has no
cross-cutting kind register. The small pythias (14m/160m) are
power-limited (n_gated 6/12) but land the SAME verdict as their
well-powered 410m/2.8b siblings — consistent family signal, not an
artifact of the small ones. (4th don't-over-read vigilance: the negative
is read from the WELL-POWERED members, not the underpowered ones.)

**POLED is a weaker, model-specific sub-signal** — POLED for
0.6b/14b/32b/olmo, diffuse for 4b/27b/gemma. It is NOT monotone in scale
(0.6b poled, 4b diffuse, 14b/32b poled). The core TYPE-REGISTER verdict
is the robust datum; whether the kind space is polar (simplex) vs diffuse
(alphabet) varies by model and should not be over-read.

### What it means

- **Contrast with the crystal.** The 9×9 routing crystal is 11/11 — it is
  what makes a transformer a reducer, present even in pythia. The TYPE
  register sits one layer up and is CONTINGENT: it emerges only when the
  training distribution demands typed composition (code, math, structured
  reasoning). Types are LEARNED on top of the universal reducer.
- **Direct evidence for M7 (`the-verbum-machine.md`).** M7 (typed apply)
  was held open — "whether types EMERGE in M1–M6 is itself the
  experiment." This sweep answers half of it: the type register is
  emergent and training-forced. A by-construction typed substrate (M7)
  would MANUFACTURE what Qwen3/OLMo/Gemma had to learn and pythia never
  did. It also refines `reachable-type-systems-are-gradual-intersection-
  structural.md`: the gradual/intersection design space is what a capable
  recipe converges to; the affine core is universal (KIBC), the type
  register on top is not.
- **S5 scorecard (the type arc).** discreteness ✓ · selectivity ✓
  (cross-cut, now cross-FAMILY 7/11) · compositionality ✗ · causality ✗
  → 2/4, held. Selectivity is now much stronger (7 models, 3 families) —
  but it is a SELECTION/READ signal, not yet compositional or causal.
  §P-TYPE-WRITE (nonce-membership injection → held-frame licensing
  transfer) remains the causal keystone; the fuel-theorem probe
  (de Carvalho: type size = evaluation length) tests compositionality.

## The consensus route map (the dynamic half the grams are missing)

The grams are **station maps** — no trains. Routing-is-computation says
the computation is the sequence of switch events, and opcode tracing
exists. Design:

- Per probe, record the reduction TRAJECTORY: per-layer register states,
  pole memberships, key firings → a per-model route.
- **The critical move: express routes in GRAM COORDINATES** — projections
  onto the outcome poles + the relational identity frame — not raw
  activation coordinates (frame-locked, incomparable). The gram
  coordinates are frame-invariant BY MEASUREMENT (11/11) → routes become
  comparable cross-model.
- Consensus over N teachers: idiosyncratic routing averages out (same
  carrier-averaging logic as consensus distillation); the **consensus
  route map = the invariant switch schedule**.

What it buys:
- **L4 made concrete** (extract switch schedules, not weight blobs) as a
  multi-teacher artifact.
- The s273 atlas extended from static sites to dynamic paths.
- **The mechanistic readout P-CONSENSUS-DISTILL was missing**: don't just
  check the student's gram walks to the consensus root — check its ROUTES
  converge to the consensus routes.
- The program listing the machine must implement: the lambda compiler
  written as paths through pole-space rather than as weights.

**Dependency order (noticed s308):** the grams are the **coordinate atlas
that makes the route map possible** — static geometry first so dynamic
routes have an invariant space to live in. The legend was built before we
knew we'd want the map.

## §Result-structure — the 9×9 is a DIFFUSE opcode block + a UNIVERSAL transform→output flip (s343)

Michael's structural reading of the 9×9 ("4 opcodes KIBC, each with a WHNF
geometry {S,D,W,Y}, and a final WHNF that flips transform→output in the highest
layers") tested against all 10 committed route Grams (zero model load,
deterministic; `scripts/explore/gram_structure_read.py`,
`results/gram_structure_s343/summary.json`). CRYSTAL order [K,I,B,C,S,D,W,Y,WHNF].

- **(1) "4 opcodes" — HALF.** KIBC is a genuine, distinctly-separated block
  (mean-centered: within-OP +0.056; OP↔RED −0.234; OP↔WHNF −0.268) — but the
  geometry is **DIFFUSE**, not a crisp rank-4: participation ratio ≈ 6.2/9,
  consensus eigenvalues [2.29, 1.60, 1.07, 0.98, 0.88, 0.81, 0.72, 0.65, 0.006],
  top-4 only 66% energy (top-5 76%). Confirms s303 "9×9 diffuse". So "4" shows up
  as a **block separation, not a rank**.
- **(2) "S,D,W,Y = a WHNF geometry per opcode" — NOT SUPPORTED.** {S,D,W,Y}
  barely cohere (within-RED +0.019) and are neutral to WHNF (RED↔WHNF −0.031); the
  OP×RED map is not 1:1 (K,I→W; B,C→D; S,Y never closest) and mostly anti-similar.
  A separate loose group, not per-opcode reduced forms.
- **(3) "final WHNF flips transform→output at the top" — STRONGLY CONFIRMED,
  10/10 models** (sign-test p<0.001). Mid→top: the KIBC opcodes **converge**
  (OP-block coherence ~0 → +0.15, rises in 10/10) AND **WHNF merges in**
  (distinctness 0.85 → 0.75, falls in 10/10). Middle = **transform** (opcodes
  spread doing distinct routing, WHNF held apart); top = **output** (opcodes
  collapse, WHNF joins — the computation resolving toward emission).
- **(4) Where is the MODEL-SPECIFIC residual? Nowhere nameable.** Cross-model
  agreement is high and flat across depth (0.91–0.955) and **HIGHEST at the top
  (0.955)** — the stage-flip is the *most universal* part, NOT model-specific. The
  arm-A residual does not localize at the stage boundary, has no family structure,
  is small → **idiosyncratic noise, not a per-model clock or program** (corrects an
  s343 stage-timing guess).

**Net.** The 9×9 decomposes into two universal **intensional** things: *which
opcode* (the KIBC block) and *which stage* (the transform→output flip). Crucially
the flip is **content-free** — it says "resolving", never *which* result — so even
the gram's dynamic part is intensional. This coheres the §P-SCHEDULE-READ-C LEXICAL
capstone (s343): the weights hold the ISA + pipeline stages; the specific answer is
tape-resident. Bounds: aggregate over 10 models, last-token routing register (9×9
identity), CMR cosine grams; the block/pairing reads are descriptive (the 10/10
stage-flip is the one with a sign-test).

## §Result-route-map-v0 — the trains, at last: a SHARED TRUNK with a LATE BRANCH (s344)

> The dynamic half designed above ("station maps, NO TRAINS") — finally built.
> INSTRUMENT-ONLY / EXPLORATORY (Michael s344 repoint): observe what the model
> does on a DIVERSE prompt set, THEN design special probes. Qwen3-14B only.

**Method (FTO-clean, frame-free — never CBLL's rotation).** Per probe, capture the
per-layer `sign(gate)` last-token trajectory and project it onto the committed
Qwen3-14B 17 outcome+identity pole centroids (`results/expanded-gram/qwen3-14b`)
→ a **route** = (40×17) cosine trajectory + its (40×3) rank-3 fire/halt/diverge
reduction + argmax station-sequence. Diverse BANDED set (496 probes):
`plain_prose → prose_structured → nl_combinator → symbolic_formal + cross_domain`
(the prose→symbolic gradient). Poles + probes co-registered in one pass (the coext
lesson). Instrument trusted: det 0.0, mean route-coherence 0.933, G0 offdiag_corr
0.929 vs the committed 17×17, `--validate` 4/4 (planted-route recovery /
shuffled-layer null / determinism / G0). Harness `scripts/explore/route_map_v0.py`
+ `route_map_read.py`; results `results/route_map_v0_s344`.

**What Qwen3-14B does (observations, NO verdict — capture-euphoria guard).**
1. **ONE shared route trunk (L5–29).** Plain prose, structured prose, combinator-
   evoking prose, AND code/math/tool trace **nearly the same path** in pole-space
   (band separation ~0.02; cos-to-plain-prose 0.93–0.98). Route-level evidence the
   reducer runs on **all language** (thesis L0), notation or not.
2. **A LATE BRANCH (L30–39)**, separation rising to 0.64 = the s343 transform→output
   flip seen as a **trajectory** (shared transform trunk → output-specific branch).
3. **Formal notation is the lone top-of-stack outlier.** Only `symbolic_formal`
   (`λx.x`, `S W (a (B D))`) peels off hard (cos-to-prose 0.93→**0.125** in the top
   third) and is the **only band substantially in the `whnf:*` OUTCOME poles**
   (whnf:K 14%, WHNF 13%) — the gate-activated "compile to lambda" (thesis L1) as a
   route divergence into the fate register.
4. **Landing sites:** plain prose collapses to **I** (97% of last-3-layer stations,
   "continue the text"); structured/combinator prose spread across K/B/W/Y/WHNF
   (selection/composition/recursion/halt, incl. Y=recursion); code rides **B**
   (composition 30%) + **WHNF** (halt 24%).
5. **Two isolated high-signal early sorters (L2, L4)** briefly separate the bands
   (sep 0.95/0.82, |signal| 0.90/0.97) then reconverge — a real feature, not noise.

**Why it matters.** REDEEMS the semantic-equality hunt: s339/s343 kept testing
STATIC points (→ LEXICAL); meaning, if anywhere, lives in the **orbit/branch**, not
the point. The action is the **top branch (L30–39)**, not the shared trunk. Next
probes (observation-driven): the **compile-step probe** (matched prose-vs-notation of
the SAME computation → does only notation branch into `whnf:*`?) · the branch-point
probe · the orbital co-ext read (SKK vs I as ROUTES) · the L2/L4 sorters. Bounds:
single model Qwen3-14B, last-token, gate register; exploratory (no gates/masses);
band counts imbalanced (per-band means robust).

## §Result-compile-step — surface NOTATION gate-activates the compile step (s344, FROZEN)

> route-map-v0's one clean divergence (formal notation branches into the whnf:*
> poles) — made a FROZEN, matched-computation test. Michael GO, all-7 scope; freeze
> committed BEFORE data (b9618905). Harness `scripts/experiments/compile_step.py`;
> results `results/p_compile_step_s344` (result 03176704).

**Question.** Does the branch track surface NOTATION or the COMPUTATION? Hold
computation constant, vary only notation: 7 combinators (K I C W B S D) × 3 levels —
**plain** everyday prose performing the op with no combinator vocabulary · **nl**
combinator-evoking prose (library `lambda_*`) · **formal** notation (`λx.λy.x`) —
× 8 = 168 matched items. Discriminator (reuses the route-map frame): branch-band
(top 25% layers) OUTCOME-POLE occupancy; within-combinator D = formal − plain;
`|Δtoken-length|` partial + shuffled-notation null. Verdict tree
NOTATION-GATED-COMPILE 40 / LENGTH-DRIVEN 25 / SHARED-COMPILE 20 / NO-BRANCH 10 /
VOID 5; `--validate` 5/5 (the LENGTH world reads LENGTH-DRIVEN — the partial works).

**§Result — NOTATION-GATED-COMPILE (a-priori modal 40).** det 0.0, G0 offdiag_corr
0.929. Branch-band outcome-pole mass: **formal +0.138 / nl −0.273 / plain −0.239** —
**only formal notation routes into the `whnf:*` halt register; the SAME computation
in prose (plain AND combinator-evoking) does not.** So the surface SYNTAX
gate-activates the compile machinery (thesis L1), not the computation. D formal−plain
+0.377 p=0.0002, **survives the `|Δlen|` partial** (resid +0.370, len_r −0.156 → not
length). **Consistent across all 7 combinators** (each formal_top; D +0.31..+0.41).
Formal hits the `whnf:*` HALT poles broadly (~0.14–0.18) but `div:Y` low (0.051) —
routes to halt, not diverge.

**The declared bound.** The `whnf:*` poles are themselves built from FORMAL
reduction-chain probes → "formal → whnf:*" carries a **surface-similarity**
component; formal-K hits ALL `whnf:*` poles ~uniformly (not `whnf:K` specifically) =
generic notation→halt-register routing. The verdict cleanly shows notation routes to
the outcome register while matched prose does not, but does **not** separate
"compiled the computation" from "recognized formal syntax as reducible." → **v2
control §P-COMPILE-STEP-V2: scrambled-formal** (same tokens/length, no valid
computation — does only VALID formal reach the poles?). Coheres the L0/L1 split
(route-map-v0: all language shares the trunk = L0 compressor; only notation branches
to the compiler = L1). Bounds: Qwen3-14B, last-token, gate register; S/D plain rungs
the weakest matches.

## §Result-compile-step-v2 — the compile step is lexical RECOGNITION, not compilation (s344, FROZEN)

> the §Result-compile-step declared bound, resolved. Michael GO; freeze committed
> BEFORE data (`c09cb514`). Harness `scripts/experiments/compile_step_v2.py` (imports
> the frozen s344 corpus → exact replication); results `results/p_compile_step_v2_s344`.

**Question.** Does VALID formal notation route into `whnf:*`, or does SCRAMBLED
formal (same atoms, no valid computation) route there too? A 4th level
**formal_scramble** atom-shuffles each frozen s344 formal item (regex atoms λx | word
| symbol, reordered, rejoined with spaces): the recognizable formal tokens survive so
recognition *can* fire, but no valid reduction exists. **formal-vs-scramble is
length-matched BY CONSTRUCTION** (identical atom multiset) — the confound that dogged
s344's formal-vs-plain does not apply here.

**The algebraic spine.** An exact identity of paired means makes the tree exhaustive:
`rep(formal−plain) ≡ ds(formal−scramble) + dsp(scramble−plain)`. COMPILATION = ds
carries the branch (scrambling collapses it to prose ⇒ valid computation required);
RECOGNITION = dsp carries it (scramble routes like formal ⇒ tokens suffice); MIXED =
both. A-priori RECOGNITION 35 / MIXED 25 / COMPILATION 20 / LENGTH-DRIVEN 8 /
SHARED-COMPILE 5 / NO-BRANCH 4 / VOID 3; `--validate` 7/7 (the LENGTH adversary —
which makes formal ≈ scramble, both short/high — correctly demotes to LENGTH-DRIVEN,
not RECOGNITION).

**§Result — RECOGNITION (a-priori modal 35).** det 0.0, G0 offdiag_corr 0.929,
`len_r_scramble` 0.013 (scramble genuinely length-matched). Branch-band outcome-pole
mass: **plain −0.239 · nl −0.283 · formal +0.138 · formal_scramble +0.121** —
**scrambled formal (broken, non-reducible) routes into the `whnf:*` register just as
much as valid formal**, both ~0.36 above prose. `ds(formal−scramble)` +0.0186
**p=0.32 NULL** (the length-clean validity axis); `dsp(scramble−plain)` +0.3619
p=0.0002 carries the whole branch; `rep(formal−plain)` +0.3805 p=0.0002 **replicates**
s344 (+0.377); identity `rep − (ds+dsp)` holds to **0.0**. So the s344 notation branch
is **lexical SYNTAX RECOGNITION** — the model routes formal-*notation* into the
halt/whnf register because it *looks* reducible, not because it compiled the specific
computation. Resolves the §Result-compile-step bound on the RECOGNITION side.

**Honest asterisk.** `ds` is a small *non-significant* positive (+0.019, formal a hair
above scramble) — a validity increment, if real, sits below detection power; the
dominant, significant mechanism is recognition. **Coheres the tape-residency
capstone:** even the compile-to-whnf gate fires on surface syntax; the actual
reduction lives on the tape (in-context). Method banked: the `rep=ds+dsp` identity
makes a 3-level decomposition exhaustive; a scramble (same atoms, order destroyed) is
a length-clean validity control. Bounds: Qwen3-14B, last-token, gate register;
scramble normalizes spacing (runs a hair longer — guarded by the `|Δlen|` partial +
the LENGTH planted world).

## Provenance

- Michael's three-part question, s308 close; explanations grounded in
  `gram-spectral-dsp.md` (072c3e0, 11 models, pre-registered gates G1–G5
  with declared nulls; φ-trap expected-fail replicated).
- Anchors: s284/s285 un-flattening; s303 topology-routing thesis; s305
  country-key gram (task-native precedent); tape-resident reduction page
  (scheduler register, P-HALT-POLE); consensus-distillation page
  (carrier-averaging logic reused for routes); s273 atlas + restack.
