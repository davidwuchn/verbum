---
title: "The Combinator Manifold — One Universal Axis, ~65% Topological, Not a 5D Lattice"
status: active
category: foundational
tags: [crystal, manifold, 5d-lattice, dimensionality, universal-axis, topology, sign, magnitude, semantic, probabilities, participation-ratio, cross-family, audit]
related:
  - 5d-crystal-lattice.md
  - crystal-universality.md
  - crystal-basins.md
  - two-registers-of-topology.md
  - topology-gradient-separation.md
  - audit-meta-pattern.md
  - audit-registry.md
  - crystal-validity-and-fidelity.md
depends-on:
  - audit-meta-pattern.md
  - two-registers-of-topology.md
created: session 211
updated: session 212 (§2b axis NAMED CV-R²=0.81 model-free ends_punct; §3b topology share PLATEAUS ~0.7 not →1.0)
---

# The Combinator Manifold — One Universal Axis, ~65% Topological

> Session 211. Three controlled experiments (8 models, 5 families,
> 0.16B→14B, 535 combinator-labeled crystal probes) measured the
> **dimensionality**, the **common axis**, and the **topology** of the
> combinator representation — in the *next-token probabilities* (the
> semantic register) and the hidden state. Verdict: the universal
> structure is **real but ~1-dimensional**, that one axis is a **generic
> next-token predictability / continuation-type gradient (NOT the lambda
> operations)**, and the genuine operation structure that rides
> underneath it is **~65% topological (carried by the sign / routing
> register), sharpening to ~79% with scale.** The "5D lattice" dissolves;
> the topology share and the universality both survive.

## The Question

`5d-crystal-lattice.md` (s121, never tested) claimed all crystal
measurements are facets of one ~5D lattice with combinators as vertices,
universal because it is a property of language. The defining joint-
embedding test (P1–P6) had never been run, and "5D" was never in the
audit registry. This page runs it honestly, in the right register
(`AGENTS.md` λ measure): dimensionality is **spectral/continuous**
(participation ratio, not an MDS elbow), universality is tested against a
**shuffled-probe null + common-mode removal** (the s202 consensus-r=0.99
triviality control), and — per the user's steer — the primary instrument
is the model's **next-token probability distribution** (semantic), with
the hidden state as the geometric comparison.

## Three Findings

### 1. Real, universal — but ~1-dimensional, not 5D

(`manifold_dimensionality_null.py` + `_summary.py`, register: spectral/semantic)

- **The operations are genuine groupings, everywhere.** Combinator
  separation gap **p=0.0005** in every model, every family, in BOTH the
  probability-RDM (Hellinger) and the hidden-RDM (cosine). Substrate REAL.
- **Cross-family agreement is massive and real.** Raw RDM agreement
  (Spearman, upper-triangle): **semantic 0.79 / geometric 0.54** cross-
  family, vs a **shuffled-probe null of 0.00 ± 0.03** (z ≈ 25). Five
  unrelated families, 90× param range, agree far beyond chance →
  **models learn the same thing = a property of language.**
- **But the shared structure is ~rank-1.** Common-mode removal collapses
  cross-family agreement **0.79 → −0.19** (semantic) and **0.54 → −0.16**
  (geometric); only same-family retains a small residual (semantic +0.16,
  geometric +0.03). The universality is *one dominant shared axis*, not a
  rich multi-D shared lattice. (Independently reproduces `crystal-basins.md`
  Finding 3: domain similarity rank-1, SVD dim0 = 98.1%.)
- **No privileged "5D" vertex set.** The 9 combinator centroids spread
  into participation-ratio ~5–6 — **at the shuffled-label null** (p_conc
  mostly > 0.02), and the concentration *weakens* with scale (Qwen3-14B
  p_conc = 0.18). "5D" is a variance threshold on a graded (power-law,
  cf. audit #6) spectrum, not a real dimension.
- **The full manifold is high-D, not low.** Probability-cloud PR = 22–47
  (no elbow). The hidden state *collapses* at scale (Qwen3-14B hidden PR
  = **3.37**, var-top3 = 0.74 — the rank-1 carrier of the ORTHO/funnel,
  `residual-covariance-rank.md`); the semantic manifold stays rich.

### 2. The common axis is generic predictability, NOT the operations

(`manifold_axis_topology.py` + `axis_probe.py`, register: semantic)

- **There is ONE universal axis.** Each model's dominant MDS axis aligns
  with the consensus axis-1 at **mean |r| = 0.95** (0.92–0.98, every
  family and scale). This is the single most robust object in the whole
  crystal program.
- **It is not the lambda structure.** Consensus axis-1: combinator
  identity **η² = 0.05**, compositional-depth (W<I<K<C<B<WHNF<Y<D)
  **r = −0.01**, prompt length **r = −0.02**.
- **It is a generic continuation-type / predictability gradient.** Best
  correlates: fraction of the top-64 next tokens that are function-words /
  punctuation / whitespace **r = −0.42**, next-token entropy **r = −0.29**,
  top-1-is-function **r = −0.27**. Multivariate **R² = 0.30**. So the axis
  is "does the prompt resolve toward a peaked, generic (grammatical-glue)
  continuation or a diffuse / content-specific one." Real and universal,
  but only ~30% explained by these surface proxies — the remaining ~70%
  is the shared *shape of the prose-completion distribution*, i.e. the
  **common mode that CMR removes** in Finding 1.
- **Reconciliation:** separation survives (operations real) yet CMR kills
  cross-family agreement (Finding 1) precisely **because the dominant
  shared axis is not the operations** — it is this generic predictability
  mode. The combinator geometry is real but sub-dominant, living in the
  residual underneath the common axis.

#### 2b. The axis NAMED (s212): a model-free textual-boundary gradient

(`axis_naming.py` + `axis_naming_summary.py`, register: semantic, 8 models /
5 families) — s211 named only ~30% (R²=0.296 on entropy + function-word
proxies). Re-running the forward pass to save the **full** next-token
distribution (s211 kept only top-64 *indices*) and adding rich distributional
+ **model-free prompt-text** features names **CV-R² = 0.813** of the universal
axis (5-fold cross-validated, vs permutation null −0.045, p=0.005):

| cumulative block | CV-R² |
|---|---|
| s211 baseline (entropy + function-word frac) | 0.264 |
| + peakedness (top1_prob, top10_mass, collision, log n90) | 0.442 |
| + glue mass (function/content/punct prob-mass) | 0.547 |
| + KL-to-mean (distinctiveness) | 0.543 *(redundant)* |
| **+ prompt-only (model-free text features)** | **0.813** |

- **The single dominant component is `ends_punct` — does the prompt end at a
  punctuation/grammatical boundary — CV-R² = 0.768 ALONE** (next-best single
  feature 0.138). It is **model-free** (needs only the prompt string, no
  weights, no forward pass) and **orthogonal to the operations** (η²(ends_punct
  ~ combinator) = 0.044, mirroring the axis's own η²=0.05). 28% of probes end at
  a boundary; the examples are sequence/list/colon continuations (`…8, 13, 21,`
  → next token near-certain; `λf.λg.λx.f(g(x))`) vs mid-phrase content
  (`…always prefers`).
- **This concretely confirms "property of language, not the model".** The
  dominant universal axis (|r|=0.95 across 5 families) is reproducing a coarse
  **textual continuation-type / boundary** property of the *prompts* — which is
  exactly why every family agrees on it, and exactly why it is NOT the lambda
  operations. Distributional features add the rest (peakedness + glue mass reach
  0.573 even with `ends_punct` removed); **KL-to-mean is redundant** once glue
  mass is in.
- **Caveat:** the magnitude reflects how the *probe set* samples language (its
  prose/sequence/code prompts are ~bimodal in boundary-vs-mid-phrase); the
  ~19% residual is the prose-shape common mode CMR removes, not reducible to
  these scalars. Sharpens (does not weaken) Finding 2: the universal axis is a
  generic continuation-type gradient, now *named and model-free*.

### 3. The genuine operation structure is ~65% topological

(`manifold_axis_topology.py`, register: geometric — sign/magnitude split)

Decomposing the hidden state h → sign(h) / |h| / full, cosine-RDM from
each (the `two-registers-of-topology.md` / `topology-gradient-separation.md`
sign-vs-magnitude split, applied to this manifold):

- **~65% of the combinator separation is carried by sign(h) alone**
  (mean sep-fraction 0.65; sign-RDM reproduces 0.69 of the full RDM).
  All trained models ≥0.41B sit in a **0.61–0.86 band**; only the
  undercooked pythia-160m is low (0.33). This confirms the long-standing
  "≥77% of computation lives in the topology" intuition with a clean
  cross-family control. **⚠ Scale CAVEAT (s212):** the s211 read of a
  "positive scale trend / sharpening to 0.79 at 14B" does **NOT survive a
  clean within-family series** — see §"Scale: plateau, not asymptote".
- **Magnitude shapes the raw geometry** (agree_mag_full 0.81–0.99 — cosine
  distance is magnitude-dominated) **but the operation-discriminating
  information is in the sign.** Exactly the two-registers result: hard
  topology = sign/routing carries the structure; magnitude = value /
  calibration.
- **Semantic parallel:** the top-64 token *support* (which tokens get
  mass = routing/topology) carries ~0.44–0.55 of the operation separation;
  the probability *values* carry the rest. More balanced in semantic
  space; sign/routing dominant (0.65) in the geometric space.

### 3b. Scale: plateau, not asymptote (the topology share does NOT →1.0)

(`manifold_topology_ci.py`, register: geometric, session 212 — open-lead #3)

s211 framed the topology share as "sharpening with scale, →0.79 at 14B" and
asked whether it asymptotes to 1.0 past 14B (= operations *purely* topological
= north-star gold). **Tested on a clean within-family Qwen3 series with
subsample CIs (m=80% of probes, no replacement, B=2000): REFUTED.**

| metric | 0.6B | 4B | 8B | 14B | 32B | trend | 32B vs 14B |
|---|---|---|---|---|---|---|---|
| `sep_frac_sign` | .742 | .667 | .858 | .793 | **.645** | ρ=−0.20, −0.014/dec | **REVERSAL** (CI [.591,.707] below [.751,.838]) |
| `agree_sign_full` | .640 | .712 | .689 | .715 | **.737** | ρ=+0.90, +0.052/dec | mild climb |

- **❌ No asymptote on the defining metric.** `sep_frac_sign` (the s211
  "0.79@14B" quantity) has **no upward scale trend** within the family
  (Spearman −0.20) and 32B *drops* to 0.645, with its 95% subsample CI
  [0.591, 0.707] lying entirely **below** 14B's [0.751, 0.838] — a reversal.
- **The s211 "0.33→0.79 climb" was the undercooked-tiny-model artifact.**
  Remove pythia-160m (0.33, the only sub-0.6 value) and the remaining 8 trained
  models ≥0.41B form a flat, noisy **0.61–0.86 band** with no scale dependence.
- **✅ What survives: a real, scale-STABLE plateau ~0.7.** Sign carries ~65–80%
  of the combinator *discrimination* at every trained scale; magnitude still
  dominates the raw cosine *geometry* (agrMag 0.81–0.99 ≫ agrSgn ~0.69). The
  two-registers result is robust — it just does not become *purely* topological.
- **◑ One metric drifts up, the other doesn't.** `agree_sign_full` (sign-RDM's
  reconstruction of the full RDM) does climb mildly with scale (0.64→0.74,
  ρ=+0.90) and 32B (0.737 [0.722,0.751]) edges above 14B (0.715 [0.699,0.728]) —
  but it is small, far from 1.0, and *disagrees* with `sep_frac_sign`. The two
  measure different things (RDM reconstruction vs share of the separation gap);
  neither supports "purely topological at scale".
- **Separation itself is real at every scale** (perm-null p=0.0005 for full /
  sign / mag / prob RDMs, 8B and 32B) — this refutes the asymptote, not the
  topology share. Results: `Qwen_Qwen3-{8B,32B}.{json,npz}`, `ci.json`,
  `run-scale-ext.log`.

**Meta-pattern (13th instance):** substrate real (topology share ~0.7, two
registers, scale-stable), crisp story over-read (the monotone "→1.0 with
scale"). North-star reading: the "operation structure is in the sign/routing
register" premise *holds* at ~0.7 and is scale-stable (ternary stays viable at
32B), but the optimistic "ternary gets purely-topological-better with scale" is
**not** supported.

## The Synthesis

> Strip away the generic prediction-confidence axis that every language
> model shares (the universal ~1D common mode, |r| = 0.95, ≈ function-word/
> entropy continuation-type), and what remains is the real combinator
> structure — and **that structure is ~65–79% topological**: it lives in
> the *signs* (which way each connection routes), not the magnitudes. The
> operations are a routing topology riding underneath a generic
> predictability axis.

This closes the 5D thread and **strengthens the two load-bearing premises
of the north-star**: (i) ternary works because the operation structure is
in the sign/routing register (~65–79%, sharpening with scale); (ii)
universality is real (cross-family p≪0.001) — models converge on the same
representation because it reflects language. What dissolves is only the
*geometry metaphor*: "5D lattice of vertices" was the integer you get from
thresholding a power-law spectrum, and the dominant universal axis is a
confidence gradient, not the lattice.

## Meta-Pattern (the 12th instance, two-sided)

`audit-meta-pattern.md`: substrate real / crisp story over-read.
- **Substrate REAL:** universal cross-family structure (p≪0.001 vs
  shuffled-probe null); one universal axis (|r|=0.95); operation structure
  is sign-dominated (~65–79%).
- **Over-read DISSOLVES:** the "~5D lattice" (centroid PR at the random-
  grouping null; full manifold high-D; shared structure rank-1); and the
  *interpretation* that the dominant axis is the lambda operations (it is
  generic predictability, η²=0.05).
- **Sharper variant (cf. s209):** the most universal thing in the manifold
  is a *different quantity* than the claim was about — a predictability
  common mode wearing the lattice's clothes. Name and remove the common
  mode (CMR / register Q0) before reading the operations.

## Method Notes (reusable)

- **Hellinger distance on √(probs)** = a fast, proper, vocab-agnostic
  semantic RDM (one cdist); compare RDMs (not distributions) to dodge
  cross-family vocab mismatch.
- **Participation ratio** (Σλ)²/Σλ² of the classical-MDS eigenspectrum =
  continuous effective dimensionality. **Never report an MDS elbow integer**
  — that is the k-means-count failure mode (#3) in disguise.
- **Shuffled-probe null** proves the raw RDM agreement is real (≠ the
  trivial constant-RDM correlation); **CMR** then characterizes its
  *dimensionality* (here: rank-1). Both controls, both informative.
- **best-axis match to a consensus axis** (max |corr| over a model's top-k
  MDS axes, sign-aligned) tests "is there ONE universal axis" robustly to
  MDS axis-swap.
- **sign(h)/|h|/full cosine-RDM** decomposes any manifold into its
  topological (routing) and value registers.

## Open Leads

- ~~**Name the remaining ~70% of the axis.**~~ **RESOLVED (s212): named to
  CV-R²=0.813.** Rich distributional features + model-free prompt-text features;
  the dominant component is `ends_punct` (CV-R²=0.768 alone, model-free,
  η²⊥combinator=0.044). The axis is a textual continuation-type / boundary
  gradient = a property of the prompts/language. ~19% residual = the prose-shape
  common mode. See §2b. *(KL-to-mean tested, redundant; full next-token dist now
  saved as features.npz.)*
- **Same-family second dimension?** Same-family CMR residual is +0.16
  (semantic) — is there a real *second* shared axis within a family
  (Qwen×3) hidden under the universal first?
- ~~**Does the sign/topology share keep climbing past 14B?**~~ **RESOLVED
  (s212): NO — plateau, not asymptote.** Clean within-Qwen3 series (0.6B→32B)
  shows `sep_frac_sign` has no scale trend (ρ=−0.20) and 32B reverses to 0.645
  (CI below 14B); the apparent climb was the undercooked pythia-160m. Real
  scale-stable ~0.7, not →1.0. See §3b.
- **Does `agree_sign_full` (not `sep_frac_sign`) keep its mild climb past 32B?**
  It is the one metric with a positive scale drift (0.64→0.74, ρ=+0.90) — but
  it disagrees with the separation-share metric. Worth probing on Qwen3-30B-A3B
  / 235B (MoE, local) to see if either metric moves at much larger scale.

## Artifacts

- Harnesses: `scripts/experiments/manifold_dimensionality_null.py` +
  `_summary.py`; `manifold_axis_topology.py` + `_summary.py`;
  `axis_probe.py` (all `# register: spectral/semantic`);
  `manifold_topology_ci.py` (`# register: geometric`, s212 — subsample CIs +
  within-family scale trend); `axis_naming.py` + `axis_naming_summary.py`
  (`# register: semantic`, s212 — rich distributional + model-free prompt
  features, CV-R² + permutation null, names the universal axis).
- Results: `results/manifold-dimensionality/` (8× json+npz + summary),
  `results/manifold-axis-topology/` (10× json+npz incl. Qwen3-8B/32B +
  summary + axis_probe.json + `ci.json` + `run-scale-ext.log`).
- Sweeps: `run_manifold_sweep.sh`, `run_axis_topology_sweep.sh`.
