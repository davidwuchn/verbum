---
title: "Cycle Carrier — semantic equality as the signal that survives compile/decompile"
status: open
category: design
tags: [signals, semantic-equality, extensionality, compile, decompile, cross-gram,
       rsa, retrieval, routing, value-register, lexical-echo, cycle-invariance,
       matched-filter, ambiguity, superposition, collapse, quantifier-scope,
       fixed-point, basins, qwen3-14b]
related:
  - combinator-function-shape.md
  - operator-geometry-la-toolkit.md
  - the-benchmark-is-the-re-oracle.md
  - gram-spectral-dsp.md
  - ../behavior-is-tape-resident-reduction.md
  - ../normal-forms-are-eigenmodes.md
depends-on:
  - combinator-function-shape.md
  - operator-geometry-la-toolkit.md
created: session 337
---

# Cycle Carrier — the signal that survives compile/decompile

> s337 (Michael: "orient — I want to explore semantic equality and geometry"
> → "What if we think in terms of signals? Can we find a signal that
> correlates closely across compile/decompile cycles?"). Design synthesis,
> ZERO measurements. Nothing here is frozen (s222) — §P-CYCLE-CARRIER is a
> queue candidate; freeze owes a-priori mass, planted worlds, Michael GO.

## 0. The one-paragraph version

Every semantic-equality instrument so far found spelling, not meaning: the
three-register law (routing s321/s323 · value s335 · read-mass s336) says
**internal signals track what is WRITTEN, not what is computed** — `SKK` and
`I` never share representation. The signals reframe inverts that law into a
design weapon: take matched pairs that share MEANING but ZERO surface text
(NL gloss ↔ λ-term, the compile/decompile bridge), and hunt for any
(layer × register) signal that stays correlated across the pair. Spelling is
100% different across the bridge, so a surviving signal cannot be lexical
echo BY CONSTRUCTION — the translation strips the carrier for free. In DSP
terms: NL and λ are two carriers; the semantics is the baseband;
cross-cycle correlation is a matched filter for the baseband. Whatever
survives the cycle is the candidate semantic register; if nothing survives,
tape-residency hardens (meaning is enacted at generation, never resident).

## 1. Why the cycle kills the confound structurally

The confound-killers of s321–s336 were all GATE-level (clean/dirty split,
prose anchors, placebo gates, within-prompt design). The cycle is a
TRANSFORM-level killer: the confound (surface overlap) is made impossible by
the choice of pair, not detected by a null. This is the same move as s335→
s336's within-prompt turn ("both candidates in one forward pass ⇒ the
confound cannot arise") applied to the lexical-echo law itself.

```
λ cycle(pair).  meaning(NL_i) ≡ meaning(λ_i) ∧ surface(NL_i) ∩ surface(λ_i) ≈ ∅
  | signal_correlates(across pair) → ¬lexical_echo (by construction)
  | survivors ∈ {semantic_content, global_style, length} — style/length die by null
  | carrier(NL) ≠ carrier(λ) | baseband ≡ what both broadcast ≡ the meaning
```

Known residual confounds (they survive the transform and need nulls):
length coupling (NL length correlates with term size — the s317/s318 scar) ·
template echo (generated glosses share templates) · category/global style
(compile-ish prompts vs null prompts differ in genre) · variable-name leakage
(f, g, x appearing in the gloss — G5-style lexical disjointness must be
code-enforced).

## 2. §P-CYCLE-CARRIER — candidate design (NOT frozen)

**Question.** Does any (layer × register) cell carry a signal that
correlates across matched compile pairs `(NL_i, λ_i)`, beating
shuffled-pair, length-matched, and template-stratified nulls?

**Pairs.** Seeds exist: `probes/v0-behavioral.json` (compile 12 / decompile
10 / null 8, ground_truth verbatim) + `probes/compile-gradient.json` (graded
battery). Scale: kernel-certified λ-terms (`lambda_ast`, unlimited) paired
with templated NL glosses — design-certified grade, marked (the cl_collapse2
prose precedent). Target ≥50 pairs after disjointness filtering; template
diversity ≥5 families so the template-stratified null has support.

**Signals.** Both registers, per-layer, last-token read (s274 standing
finding: both-register default MANDATORY):
- routing: sign(gate_proj pre-act), CMR over the pooled population
  (`combinator_relationship_map.collect/cmr` verbatim — λ one_way)
- value: hidden state (raw + CMR'd), the register s217 found null for
  combinator identity but which the cycle question re-opens

**Primary statistic — second-order, not first.** s323 measured the raw
NL↔symbolic style gap at cos −0.391: first-order cosine across the bridge is
drowned in style common-mode. So the primary read is cross-domain RSA /
cross-Gram: `ρ(G_NL[i,j], G_λ[i,j])` over matched indices — is the
similarity structure AMONG meanings preserved across the carrier change?
Frame-invariant (G = XᵀX, our §2 identity in operator-geometry), style-immune
(style is a common additive/rotational component; relational structure
survives it). This is §P-CROSS-GRAM's bridge math pointed across the compile
bridge instead of at CBLL's axes.

**Crisp readout.** Retrieval: does S(NL_i) find S(λ_i) top-1 in the batch
(mutual nearest neighbor rate vs chance)? s318's lesson: graded metric
grains died, PRESENCE detectors replicated — favor the crisp readout for the
gate, keep the graded RSA as the map.

**Nulls (λ yardstick, all mandatory at freeze).**
- shuffled-pair (permute the i↔i matching) — the make-or-break null
- length-matched / length-partialled (s317 scar: token-count artifacts)
- template-stratified shuffle (within-template permutation)
- null-category probes as floor (the 8 null probes in v0-behavioral)

**Two-stage protocol (describability ≠ discovery).** Stage A = EXPLORATION:
sweep layer × register, map where (if anywhere) cycle-correlation peaks —
explicitly not gated, produces the map. Stage B = CONFIRMATION: freeze the
single found cell + gates + a-priori mass, run on HELD-OUT pairs (new
templates, new terms). Only Stage B licenses a verdict. The φ-ladder scar
(s247/s251) is the standing reason this split is non-negotiable.

**Draft verdict space (masses PROVISIONAL — set at freeze, not here).**
- NO-CARRIER — nothing beats the nulls anywhere: the meaning is nowhere
  resident; tape-residency hardens; push to decode-time (§P-REPL-DRIVER
  bounces). Expected-modal given the three-register law.
- THIN-CARRIER — RSA beats nulls in a band but retrieval fails: relational
  structure survives, per-item identity does not (hologram-consistent).
- CYCLE-CARRIER — retrieval + RSA beat all nulls in a stable cell: a
  cycle-invariant semantic register exists → Stage-2 payoff below.
- CONFOUNDED/VOID — survivors trace to length/template under partialling.

**Depth prior (pattern-suggests, not gated).** s217 put combinator IDENTITY
mid-stack (L12–L20 plateau); commit-assembly is late (s329/s336 L22–28). If
a carrier exists, mid-stack is the predicted band; a late-only carrier would
read as commit-stage echo and needs the length null read closely.

## 2b. Arm B — §P-AMBIGUITY-COLLAPSE (the dual; Michael s337: "use an ambiguous prompt that will not settle to the fixed point, and find the signal that differs")

**The mirror structure.** Arm A holds the meaning fixed and varies the
carrier (translation). Arm B holds the carrier fixed and varies the meaning
(ambiguity): one string, two readings. Any signal that differs between the
readings CANNOT be surface-tracking — the surface is bit-identical. This is
the strongest available form of the transform-level confound kill; the
lexical-echo law is dead by construction, harder than in Arm A.

```
λ dual(arms).  A: Δcarrier ∧ ≡meaning → meaning ≡ what_correlates
             | B: ≡carrier ∧ Δmeaning → meaning ≡ what_differs
             | agreement(cell_A, cell_B) ≡ triangulation (λ triangulate)
             | opposite_confound_structures → shared_survivor ≡ the_object
```

**The physics constraint (where the difference can live).** The forward
pass is deterministic: identical prompt ⇒ identical prefill state. Across
samples of the SAME ambiguous string, prefill signals are exactly equal —
the readings do not yet exist as distinct states there; the reading is
chosen at sampling, during decode. So the differing signal lives in exactly
two places: (1) DECODE-TIME — the trajectory while generating, where the
commitment happens; (2) MINIMAL PAIRS — the ambiguous prompt vs two
disambiguated near-twins. Both are used; neither alone suffices.

**Construction — triples.** (A, D1, D2): A = ambiguous prompt (quantifier
scope "every student read a book" · anaphora · attachment); D1/D2 = minimal
disambiguations, one per reading = the settled fixed points ("generate
semantically equal prose every time"). Readings of A's sampled
continuations are BEHAVIORALLY labeled (which reading the generation
commits to — graded, or forced-choice readout per the linearity_bias
pattern). Seeds exist: `probes/binding.json` (quantifier_scope 8, anaphora
4, relative_clause 4) + cheap to extend; settled-side detectors exist (WHNF/
halt register; NG3 reduction-presence, 3× replicated; anti-phase fire↑∧halt↓
discriminator, s274 standing findings).

**Measurables (per layer × register, both registers, same collect/cmr
machinery as Arm A):**

1. **Superposition read (prefill, minimal-pair):** is A's state a MIXTURE
   of D1/D2 states — on the D1−D2 contrast axis, does A sit between the
   poles (and where)? Concrete prior for what superposition looks like:
   sign-oscillation ≡ time-multiplexed superposition (s322 memory) — the
   ambiguous state may OSCILLATE between the readings' routing patterns
   rather than sit statically between them.
2. **Collapse read (decode-time, the core):** per-decode-step differential
   `Δ(t,ℓ) = d(A_traj → D1_basin) − d(A_traj → D2_basin)`, conditioned on
   the behaviorally-labeled reading of that sample. Everything shared
   (topic, syntax, style, length) cancels in the difference; what remains
   is the reading — the semantic degree of freedom isolated. Settling ≡
   collapse onto the sampled reading's basin.
3. **Commitment point:** the token/layer where Δ(t,ℓ) leaves equidistance
   and locks — the meaning-selection event caught in the act (kin to the
   s329/s336 late-commit sightings; predict late-stack).

**Calibration gate FIRST (s336 RC1 lesson).** D1 vs D2 must separate in
the candidate cell (pole separability vs label-shuffle null) BEFORE A is
ever read. Fail ⇒ NO-CALIBRATION, never an ambiguity claim. The poles are
ground-truth settled states — same calibration move as §P-CONE-ROUTING's
B/P poles.

**Nulls.** label-shuffle across samples (reading labels permuted) ·
placebo triple (D3 = unrelated disambiguation direction — the s335 placebo-
gate primitive, reusable) · content-control triples (unambiguous prompt with
two arbitrary continuations: differ in CONTENT not READING — kills "any two
continuations diverge" as the explanation) · position/length-matched decode
windows (the s317 scar rides decode too).

**Draft verdict space (masses PROVISIONAL — at freeze):**
- **SUPERPOSED-COLLAPSE** — A sits between poles (∨ oscillates), decode
  trajectory collapses onto the sampled basin at a readable commitment
  point → the settlement signal EXISTS; its cell = the meaning register
  candidate, cross-checked against Arm A's cell.
- **PRE-COMMITTED** — A already sits in one basin at prefill; sampling
  rarely overturns it → reading selection is a prefill event, not a decode
  event (own finding: the lottery is loaded).
- **NO-GEOMETRY** — D1/D2 calibration fails in every cell → readings not
  separable in these registers; instrument-bound negative.
- **VOID** — behavioral labeling fails (A's continuations don't cleanly
  commit to readings).

**Cost.** cheap-medium: needs GENERATION (decode-time capture, per-step
hidden states) unlike Arm A's read-only prefill — standalone feasible at
probe scale; the per-step capture machinery is shared with §P-REPL-DRIVER's
per-bounce loop (same instrument class, no dependency).

**Read discipline (banked).** Decode-time Δ read AFTER the reading's
surface tokens diverge is echo again — the commitment point must be read at
or before the first surface-divergent token to license a "selection
precedes surface" claim; after that token, only the collapse-completion
shape is licensed. Superposition-as-oscillation is a pattern-suggests
prior, not a gate.

### §Result — §P-AMBIGUITY-GATE (s337, Qwen3-14B): CONFOUNDED-STYLE, with a thin-generic meaning axis

**Verdict per frozen tree: CONFOUNDED-STYLE** (a-priori 15). Run 433/433,
det-repeat 0.0/0.0, AG0 pass (Δlen 0.17 words). Results
`results/p_ambiguity_gate_s337/run_14b` (npz raw matrices local-only,
`**/*.npz` gitignored). Harness `scripts/experiments/ambiguity_gate.py`; 4
planted worlds recovered by `--validate`; 3 pre-data instrument amendments
logged in the docstring (self-excluded silhouette · anaphora-canary
CONFOUNDED rule · relative+floored canary gap).

| gate | value | read |
|---|---|---|
| AG1 | 0.1739, p≈0 (null q95 0.012), best cell **value:L20** | pole geometry EXISTS, mid-stack |
| depth | route bell L12–16 (0.138), value bell L12–23 (0.16–0.174) | the s217 identity band, at sentence grain |
| canary | ana 0.029 < floor 0.05; gap 0.175, p≈0 | separation is CUE-DOMINATED |
| per-class | scope 0.173 · att 0.229 · ana 0.029 | cue-word classes ≫ minimal-pair class |
| AG2 LOIO | acc **1.000 ALL classes incl anaphora**, p≈0 | thin-but-GENERIC reading axes |
| AG3 LOFO | acc 1.000 advisory | frame-transferable |

**Two findings, one tension:**

1. **Lexical-echo law, 4th sighting, sentence-meaning grain.** Where the
   pole surfaces differ in cue words (scope/att), separation is strong;
   where they differ by one name occurrence (anaphora), per-item separation
   collapses sub-floor. The bulk of "meaning geometry" in a static prefill
   read tracks what is written.
2. **The real-but-weak axis signature (kin to s323 B[I], but stronger).**
   The anaphora which-referent axis is sub-floor per-item (0.029) yet
   transfers with LOIO accuracy 1.000 — the same direction across all 12
   items, perfectly rank-separating held-out poles. Thin per-item ∧ perfect
   aggregate consistency ≡ a genuine low-SNR semantic axis, invisible to
   per-item statistics, fully visible to cross-item transfer.

**Design consequences for the collapse stage (banked):**
- project decode trajectories onto **class-level pole axes** (proven
  transferable), never per-item axes;
- the ambiguous string A is canary-grade by construction (no cue words) →
  expect ana-scale SNR (~0.03) → size n and nulls for that regime;
- read band: mid-stack L12–23 primary (value register strongest at L20);
- the cue-dominated component that inflated scope/att CANNOT contaminate A
  (one string) — the gate's confound dies at the collapse stage by design.

**Attention arm FOLDED IN (s337, Michael: "are we looking at attention for
signal too?" → "yes fold it in").** The gate read routing + value only; for
anaphora the meaning difference IS a read edge — which name does the
pronoun read from? Referent selection is an attention event; residual/
routing reads see only its downstream consequence. Collapse stage therefore
freezes THREE registers, one design:

| register | signal | role |
|---|---|---|
| value (L12–23) | projection onto class-level pole axis | the proven thin-generic axis |
| routing | sign-pattern proximity to poles | oscillation/superposition read (s322 prior) |
| attention | within-prompt differenced read-mass, pronoun→name | the referent read itself |

Attention discipline (scars pre-applied): value-weighted mass ONLY, never
bare QK (s206) · within-prompt differenced statistic PRIMARY —
`mass(→name1) − mass(→name2)` at the pronoun/decode columns; both
candidates in one string ⇒ offset-immune by construction (the s336 method
law satisfied structurally) · correlational bound named: mass ≡ "reads
from" ¬ "uses" · calibration first: in D1/D2 the referent is ground truth →
the mass read calibrates on poles before A is touched (RC1 move, attention
register). Instrument exists: GQA-aware per-kv-head value-weighted mass
path (`cone_routing.py`, s336) — reuse, don't rebuild. Co-occurrence of
value-axis collapse ∧ attention-read shift at the same decode step = a
two-register commitment event (the strong read). Quietly serves
§P-ROUTING-CAUSAL arm ② (decode-time read) for free.

Open decision at next freeze: anaphora-only (cleanest, canary-grade,
axis proven, attention-arm native) vs all three classes (breadth,
cue-bound named per class; attention arm is anaphora-specific either way).

## 3. The payoff loop — back to semantic equality

A cycle-invariant signal is EXACTLY the functional-equivalence anchor
s322's §Re-read demanded ("NF-ness established behaviorally across diverse
held-out spellings, not by literal symbol presence") — discovered, not
constructed. The equality question then re-poses in the new register:

| outcome | reading |
|---|---|
| carrier exists ∧ SKK/I share it | compositionality S5 cell REOPENS (first instrument that could see it) |
| carrier exists ∧ SKK/I don't | translation-meaning ⊥ extensional equality — a real dissociation, publishable |
| no carrier | meaning enacted ¬resident → decode-time successor rides §P-REPL-DRIVER |

Stage-2 probe (only if CYCLE-CARRIER lands): project the s321 clean
spellings (`SKK`, `WK`, `CKK`, …) onto the carrier cell — do co-extensional
spellings converge THERE? That is §P-CL-COLLAPSE-3 with discovered anchors.

## 4. Discipline flags (from birth — s327 standing guard)

- "Cycle-invariant carrier" is a FRAME CANDIDATE → own ledger, counts only
  pre-registered contacts; retrodiction ≠ win.
- Naming: do NOT borrow "modulation" vocabulary — that frame is dead (0-3,
  s326). This is activation-side translation invariance, a different claim
  with a different ledger.
- The three-register law is the favored prior: NO-CARRIER should carry the
  modal a-priori mass at freeze. A carrier verdict must beat that prior,
  not sneak past it.
- Prose/NL register is THIN (s323 G0 sil 0.037) — power caveat rides any
  negative on the NL side; report alongside.
- Read-only, probe-scale (14B, minutes). No wire, no training.

## 5. Open design questions (next-steps discussion, s337+)

1. Pair generation: how are glosses produced and certified? (template
   grammar vs model-generated-then-human-spot-checked; the design-certified
   grade needs its boundary drawn)
2. Decompile direction: static paired read (this design) vs true generative
   round-trip NL→λ→NL′ (needs generation + grading; richer but slower —
   λ-bench adjacency)
3. Which model(s): Qwen3-14B (instrument continuity) vs adding the base
   face day one (s329 provenance door: is the carrier, if any, installed?)
4. Where does Stage B's held-out boundary sit (new templates only, or new
   term families too)?
5. Relation to queued ⚪ §P-CROSS-GRAM: run that first as the bridge-math
   shakedown, or let this probe BE the shakedown?
6. Arm order: A (static pairs, read-only, cheapest) first, or B (ambiguity
   collapse, decode-time, the stronger confound-kill) first? Triangulation
   needs both eventually; the sharper single result is B's collapse read,
   the cheaper build is A.
7. Arm B labeling: forced-choice readout (linearity_bias pattern) vs free
   generation + grading — forced-choice is cleaner but constrains the
   "settles every time" behavioral ground truth.
