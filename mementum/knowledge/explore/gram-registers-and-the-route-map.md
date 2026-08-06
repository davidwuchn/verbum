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

## Provenance

- Michael's three-part question, s308 close; explanations grounded in
  `gram-spectral-dsp.md` (072c3e0, 11 models, pre-registered gates G1–G5
  with declared nulls; φ-trap expected-fail replicated).
- Anchors: s284/s285 un-flattening; s303 topology-routing thesis; s305
  country-key gram (task-native precedent); tape-resident reduction page
  (scheduler register, P-HALT-POLE); consensus-distillation page
  (carrier-averaging logic reused for routes); s273 atlas + restack.
