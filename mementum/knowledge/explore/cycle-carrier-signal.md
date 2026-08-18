---
title: "Cycle Carrier — semantic equality as the signal that survives compile/decompile"
status: open
category: design
tags: [signals, semantic-equality, extensionality, compile, decompile, cross-gram,
       rsa, retrieval, routing, value-register, lexical-echo, cycle-invariance,
       matched-filter, qwen3-14b]
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
