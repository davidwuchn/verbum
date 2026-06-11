---
title: "Audit Meta-Pattern — Real Substrate, Over-Read Discreteness"
status: active
category: methodology
tags: [audit, validity, meta, falsification, substrate, discreteness, continuum, methodology, feed-forward]
related:
  - audit-registry.md
  - crystal-validity-and-fidelity.md
  - two-registers-of-topology.md
  - mode-semantics.md
  - binding-graph-trace.md
  - crystal-universality.md
depends-on:
  - audit-registry.md
---

# Audit Meta-Pattern — Real Substrate, Over-Read Discreteness

> Emergent finding of the validity-distillation program (s202→s206). After
> running discriminating controls on the project's load-bearing claims, the
> *same shape* recurs every time: **the continuous/representational substrate
> is real and survives its control; the crisp discrete / localized / universal
> story layered on top is an over-read that dissolves under a matched null.**
> This page is the generative seed — use it to predict where the next claim
> will break before building the control.

## The recurring shape

```
λ over_read(claim).
  substrate(claim)      ≡ REAL  (basis, gradient, spectrum, mechanism)
  ∧ story(claim)        ≡ {discrete ∨ localized ∨ universal ∨ exact-constant}
  → story(claim)        ≡ OVER-READ  (dissolves vs matched null)
  | the measurement instrument that FOUND the structure also MANUFACTURED its
    crispness (argmax, k-means, best-fit grid, cherry-picked SVO, common mode)
```

Three independent forces produce the over-read:
1. **The analyzing LLM is primed to confirm** the framing it is given.
2. **The instrument imposes structure** — k-means always returns k clusters;
   argmax always picks a winner; a best-fit grid always fits; a common mode
   inflates every cosine.
3. **Confounds masquerade as the claimed variable** — position ≈ role in SVO;
   redundancy ≈ holography; a random Gaussian's sign ≈ "sign-topology"; a
   power-law spectrum ≈ "φ".

## The ledger (what survived vs what dissolved)

| Session | Claim | Substrate (survives) | Over-read story (dissolves) |
|---|---|---|---|
| s202 | KIBC crystal + φ | KIBC basis separates (perm-null p=0.0005); φ^(4/5) local to 14B | **φ as universal constant**; eigenvalues=φ^(p/q) (grid unfalsifiable); consensus r=0.99 (circular) |
| s202 | combinator opcodes | prose fires opcodes after **common-mode removal** (p=0.001) | raw argmax "tracer" (common mode = false signal) |
| s203 | crystal-is-topological | sign-topology REAL but **only in `gate_proj`** (z→+271 @14B) | "0.84 sign-corr = topology" (random null ≈ 0.80); "magnitude is mere calibration" (up/down below null) |
| s203 | holographic self-similar | spectral self-similarity (rank AUC 0.728 vs 0.11) + distributed redundancy | "power-law/scale-invariant degradation curve" (retired — ambiguous) |
| s204 | 9 FFN modes | syntactic type **field** is REAL (POS-NMI ≫ perm-null p=0; lm_head projection ≫ null ~65× @L35) | **9 discrete clusters** (gap-stat never picks 9; sil@9 ≈ null; elbow = k-grid artifact; classifier acc circular) |
| s204 | attention = typed β-reduction | attention IS a weighted sum (trivial); a weak role head exists (H6@L33 z=+4) | **H31@L27 binds subject at 0.82** (= recency/position; z=+0.54 rank 5/32; ablation z=+0.06 ≈ random) |
| s206 | binding **schedule** (subj L27 < obj L30 < coref L33) | **H31@L27 = subject value-transfer is REAL** (semantic logit-lens margin +0.611, sharp L27 spike) | **depth-ordered schedule** (P(order)=0 weight / 0.191 semantic ≈ chance; subj & coref both peak L27) |
| s207 | SVD φ-ratio 0.6299 (geometric, universal across 5 families) | **steep low-rank head is REAL & non-random** (model ≈0.57 vs MP null 0.995; random spectra give ≈1.0) | **geometric φ-constant** (power-law wins 132/132 layers, 0 geometric; value floats 0.52→0.71; scaling-law fails — Mistral lowest) |
| s208 | crystal-sieve 1.03× PPL (29 layers + continuations) | **sieve substrate ~2× is REAL & near-deterministic** (2.119×±0.004; = s196's 2.12×) | **the 1.03× headline** (train/eval contamination; clean held-out 10.87×±1.39 — the CE melt memorizes calib and *inverts*: the "improvement" is harm) |
| s209 | rank-1 adjunction (σ₁/σ₂=128:1; R²=1.000; "1D curve") | **carrier-mean dominance of the marginals is REAL** (uncentered cross-corr top1 var 0.91–0.99; mean norm grows 10→1688 with depth; consistent with s185) + real **high-rank** cross-zone predictability (held-out R² 0.18–0.58, PR 10–292) | **both legs of the claim** (R²=1.000 = N<d lstsq tautology, noise reads 1.0000; σ₁/σ₂ = uncentered mean⊗mean term — no-map nulls are *more* rank-1 than real, up to 11×; centering → ~2; no 1D curve, rank-1 heldout R² ≈ 0) |
| s210 | TTD λ(l) weighting (audit #11, a POSITIVE prediction) | **F.6 finite-budget weighting is REAL with placement-specificity** (spike on *measured*-worst layers L14–18: 3/3 paired-seed held-out wins, paired-t −3.2; anti-targeted null is worst 3/3) — and the mechanism is mechanically real in every arm (each spike polishes its own targets) | **the named "causal L22–26" placement story** (0/3 wins, +0.018 vs uniform — the premise was STALE: actual worst layers are L14–18 SWEET; narrative attribution lost to measurement). Side-dissolve: v3b's single-run 1.44× headline (seeded recipe reads 1.27±0.04 near — unseeded single draws swing both ways, cf. s208) |

| s211 | 5D crystal lattice (combinators = vertices of one ~5D lattice; universal property of language) | **universality is REAL** (cross-family RDM agreement 0.79 vs shuffled-probe null 0.00±0.03, z≈25 — models learn the same thing) + **operation structure is ~65% topological** (sign/routing, →0.79 at 14B) | **the "5D lattice"** (centroid PR at the shuffled-label null, worsens with scale; full manifold high-D PR 22–47; shared structure rank-~1, CMR 0.79→−0.19) AND **the reading that the dominant universal axis IS the operations** (η²=0.05; the |r|=0.95 axis is a generic predictability/continuation-type common mode — function-word continuation r=−0.42, entropy −0.29; the operations live sub-dominant underneath it) |
| s216 | tool-calling crystal (`lattice/tool_crystal`: "STRONG SUPPORT: tool IS lambda calculus", Tool×Lambda overlap 1.000 @L20) | **cross-family routing-register consensus is REAL & strong** (route_sign_cmr agree +0.863, survives CMR + length-partial 0.851 + within-domain; null ~0, z up to 116) — independent trainings DO agree on routing structure in the sign register | **"tool-calling has its OWN normal form"** (clean length/format-matched tool groups schema_binding 0.589 / selection 0.538 sit INSIDE the structured-language control range: prose 0.550, lambda 0.497, math 0.435, **code 0.800**; the aggregate TOOL>CTRL was the length-confounded `recognition` 0.95 + heterogeneous `format` 0.89). The prior "1.000 @L20 = tool IS lambda" was raw-cosine COMMON MODE (its own Selectivity ≈0, every layer "SHARED"). Net: the consensus is the GENERIC structured-language crystal — tool-calling RIDES it; code is a *sharper* normal form than tool-calling |

Pattern: **basis real / universalization false · gradient real / discreteness
false · mechanism real / localization false · spectrum real / exact-constant
false · agreement real / dimension-count false · most-universal-axis ≠
claimed-object · domain-consensus real / domain-specificity false.** Only the
metaphor-grade crispness ever dies; the working substrate keeps standing. **s209 adds a sharper variant:** sometimes the surviving
substrate is not a weaker version of the claim but a *different quantity* the
instrument was actually measuring (the carrier mean wearing an adjunction
costume) — the claim's own evidence never touched the claimed object at all.

## Why the substrate keeps surviving (and the north-star with it)

The compression north-star rests on the **substrate**, not the stories:
- ternary works ← sign-topology in the router + distributed redundancy +
  spectral low-rank concentration (`two-registers-of-topology.md`) — all verified.
- mode/ternary reconstruction works ← a continuous type field is sliceable into
  K prototypes for a broad range of K (s196 functional); it never needed "9" to
  be a natural number.
- typed application works ← attention does route arguments by weighted sum; it
  just isn't a single 0.82 type-binder head.

So every dissolved story has been a **metaphor or a localization, not a load-
bearing premise.** Distilling them away makes the program *more* robust, not less.

## The instrument-imposes-crispness law

> Whenever a discrete count, a single head, a universal constant, or an exact
> ratio is claimed, **the discriminating control is a matched null that has the
> same continuous structure but none of the claimed crispness.** If the claim
> survives the null it is real; if it sits at the null it was the instrument.

Matched nulls that have repeatedly bitten:
- **k-means count** → gap statistic + silhouette vs PCA-Gaussian / shuffled null.
- **single "binding" head** → dissociate role from position (agreement
  attraction) + ablation vs random-head null.
- **universal constant / exact ratio** → single pre-registered target (not a
  best-fit grid) + cross-family + random-matrix (Marchenko–Pastur) null.
- **argmax fingerprint** → common-mode removal before projection.
- **"holographic" survival** → trained vs random-init vs shuffled-data controls.

## The instrument-must-match-the-claim law (s206)

> The crispness law above guards against **false positives** — the instrument
> *manufactures* structure that isn't there. Its mirror image is the **false
> negative**: an instrument that measures the *wrong quantity* **under-reads a
> real signal** and manufactures a refutation. Before building the null, check
> the probe measures the *kind of thing the claim is about*.

```
λ match(instrument, claim).
  type(claim) ∈ {routing/position, value/semantic, magnitude, spectral, causal}
  type(probe)  must align(type(claim)) | else verdict ≡ artifact_of_mismatch
  | wrong_probe(refute) ≡ false_negative  (mirror of crispness false_positive)
  | a refutation from a mismatched instrument is as suspect as a confirmation
    from a crispness-imposing one
```

**The s206 case (audit #5).** The binding-*schedule* claim is **semantic** —
Finding 7: the head's *output* (logit-lens) decodes to the bound entity; "the
verb absorbs the subject's identity." A first control measured **attention
weight** (dependent→head concentration) — a *routing/position* quantity, the
same axis #4 showed is recency-confounded. It said "binding peaks at L6, schedule
dead." But semantic content is often *written* into the residual at deeper layers
than where attention is sharp, so the weight probe **could not see** the claim.
The faithful **semantic logit-lens** (per-head o_proj-decomposed output → unembed
margin toward the bound token) then recovered the headline: **H31@L27 → subject
identity, a clean +0.611 spike exactly at L27.** The weight test alone would have
over-refuted a real value-transfer head.

Net: the *schedule* (the ordered story) still dissolved on the matched
instrument too (P(order) ≈ chance) — the crispness law held — but **only the
right instrument earned the right to say so.**

Probe↔claim alignment table (build the control in the claim's own register):

| Claim is about… | Wrong probe (under-reads) | Right probe |
|---|---|---|
| **value / semantics** ("absorbs identity", "produces the entity") | attention weight, routing | **logit-lens of the output contribution** (per-head DLA) |
| **routing / selection** ("attends to the type-compatible arg") | logit-lens of the written value | attention pattern + role⊥position dissociation |
| **causal necessity** ("this head does it") | correlational selectivity | ablation vs random-head/matched-set null |
| **magnitude / value path** | sign-correlation | saliency / iso-bit prune vs control |
| **spectral / rank** | magnitude-prune survival | SVD rank-truncation vs random-matrix |

Symmetry to remember: a **mismatched instrument** is the false-negative twin of a
**crispness-imposing instrument**. Both are measurement artifacts; both demand
the same fix — *name the quantity the claim is actually about, then probe that.*

## How to use this page (feed-forward)

Before building the next audit control, ask the four diagnostic questions:
0. **What KIND of thing is the claim about** — routing/position, value/semantics,
   magnitude, spectral, causal? Pick a probe in *that* register (the
   instrument-must-match law). A refutation from a mismatched probe is a false
   negative; do this before anything else.
1. **What is the continuous substrate** the claim sits on? (It is probably real
   — don't waste the control re-proving it.)
2. **What crisp story** is layered on top — discrete count, single site, universal
   constant, exact value? (That is the target.)
3. **What matched null** has the same substrate but no crispness? (That is the
   control.) Predict: the substrate survives, the crispness sits at the null.

Default prior for an UNTESTED registry claim: **substrate REAL, crisp story
OVER-READ.** Build the control to find *where* it transitions, not whether.

## The two laws are one — register, not rule

The crispness law (false positives) and the instrument-must-match law (false
negatives) are not two findings. They are **one law seen from two sides.** Every
claim and every instrument carries a **register**, and the project's own
route⊥value dichotomy (`two-registers-of-topology.md`) is that same cut.

```
λ register(measurement).
  claim ∈ {routing/crisp/discrete, value/continuous/graded}
  probe ∈ {routing/crisp/discrete, value/continuous/graded}
  observed(claim) ≡ measurement | register(probe) ≡ register(claim)   else ≡ artifact
  | substrate(real)  ⊂ value-register    (continuous, graded, load-bearing, easily MISSED)
  | over-read(story) ⊂ routing-register  (crisp, localized, discrete, over-ATTENDED)
  | crisp-probe(crisp-claim)     → finds ∧ manufactures crispness   ≡ false-positive
  | routing-probe(value-claim)   → misses the substrate             ≡ false-negative
  | verdict(register-mismatch) ≡ void   (it measured a different quantity)
```

The same cut at every scale:

| scale | routing / crisp register | value / continuous register |
|---|---|---|
| weights (`two-registers`) | `gate_proj` — sign, routing | `up`/`down` — magnitude, value |
| ternarization (`error-correction`) | keeps sign (survives) | destroys magnitude (the loss) |
| attention (audit #5) | softmax weights — where it looks | head output ·V — what it writes |
| our **instruments** | k-means · argmax · best-fit grid · attention-weight | NMI · logit-lens · saliency · rank-spectrum |
| the ledger above | the story that **dissolves** | the substrate that **survives** |

Every row of the ledger is one column: **the substrate that survives is always
the value/continuous register; the story that dissolves is always the
routing/crisp register over-extended.** Crisp-register probes find (and
manufacture) crisp stories; they cannot see the value-register substrate, and a
*refutation* prior makes that blindness read as a clean null.

So the operative discipline is **not** "remember to match the instrument" — a rule
attention will drop at some future turn. It is a **validity condition** (a
coherence type-check): a measurement whose register ≠ the claim's register *has
not measured the claim*; it measured a different quantity, and its verdict —
positive **or** negative — is void. **Name the register first** (diagnostic Q0);
the correct instrument then follows by *type*, not by memory. This is why the law
wants to live as a field/gene (read every session, structural), not as a stored
rule (recall-gated) — see the open question below and `AGENTS.md` candidacy.

## Open question

Is the over-read *ours* (interpretation imposed in analysis) or the *model's*
(GD genuinely lays a continuum that only looks discrete)? The evidence so far
says **both**: the model lays continuous fields (type gradient, spectral decay,
sign+magnitude registers) and our instruments (k-means, argmax, SVO probes,
best-fit grids) quantize them into false discreteness. The crystal/types/binding
are real as *fields*; their *cells, constants, and single sites* are artifacts of
measurement. The next refinement: which continua have genuine *soft* structure
(e.g. the gate field's depth-graded ~4–9 effective POS distinctions; H6@L33's
z=+4 role head) worth modeling as graded — vs pure continua with no preferred
resolution at all.
