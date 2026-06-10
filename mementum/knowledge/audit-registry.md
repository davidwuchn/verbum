---
title: "Audit Registry — The Validity-Distillation Program"
status: active
category: program
tags: [audit, validity, falsification, permutation-null, control, distillation, methodology, worklist]
related:
  - audit-meta-pattern.md
  - crystal-validity-and-fidelity.md
  - crystal-universality.md
  - crystal-phi-derivation.md
  - project-thesis.md
  - gtsm-search-space.md
  - tsp-trajectory-distillation.md
depends-on:
  - crystal-validity-and-fidelity.md
---

# Audit Registry — The Validity-Distillation Program

> Started session 203 (designed s202). A multi-session program to
> separate the project's **real working data** from its **assumptions
> and possibly biased methodologies**. Each session opens here, picks
> the highest load-bearing `untested` claim, runs its discriminating
> control, and updates the row. The output is not destruction — it is
> the smallest hard core of verified data the north-star can stand on.

> **Emergent finding (s202→s206):** every audit so far shows the *same shape* —
> the continuous substrate is real, the crisp discrete/localized/universal story
> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict
> where the next claim breaks before building the control). **s206 corollary
> (instrument-must-match-the-claim):** before building the null, probe in the
> claim's own register — a routing/weight probe under-reads a value/semantic
> claim (false negative), the mirror of a crispness-imposing probe's false
> positive.

## The Core Principle

> A claim is *distilled* only once you have named **the control a
> plausible-but-false version of it would fail** — and run it.

Evidence that merely *confirms* a claim is not enough: both the model
and the analyzing LLM are primed to confirm the framing. The audit
question is always: **what would I see if this were an artifact, and
have I checked I am not seeing exactly that?**

## The Seven Failure Modes (what to hunt)

| # | Failure mode | The tell | Discriminating control |
|---|---|---|---|
| 1 | **Unfalsifiable metric** | fits everything (φ best-fit grid) | does a random/null fit equally? |
| 2 | **Trivial statistic** | high for noise too (eig-ratio-corr ≈0.99) | permutation null on the statistic itself |
| 3 | **Fidelity masking** | a common mode hides signal (false neg) AND argmax illusion (false pos) | remove the common mode before claiming specificity |
| 4 | **Circular validation** | target baked from the data it "confirms" (CONSENSUS_8x8) | fresh/held-out measurement |
| 5 | **Untested generalization** | cross-family asserted, same-family measured | actually run the other family |
| 6 | **Surface confound** | lexical clustering as "structure" (fake combinators won) | matched fake categories / shuffled labels |
| 7 | **Frequency vs necessity** | "must" when "most common" suffices (B-first) | manipulate the data statistics |

## The Method Recipe (reusable)

- **Permutation null over labels** — "is this grouping real or imposed?"
  Shuffle which items carry which label; p = fraction of random labelings
  at least as extreme as the true one.
- **Single pre-registered target > best-fit grid** — φ^(4/5) is falsifiable;
  φ^(p/q) over a dense grid is not. Name the number *before* measuring.
- **Common-mode removal** (`v − mean_group(v)`) before any projection/argmax.
- **Matched controls** — random-weight net, shuffled-data-trained net, fake
  categories — separate "structure" from "size / redundancy / surface".
- **Report variance** — re-run with fixed seeds; a single lucky run is not a result.
- **Match the instrument to the claim's register** (s206) — name the *kind* of
  thing the claim is about (routing/position · value/semantics · magnitude ·
  spectral · causal) and probe *that*. A value-transfer claim ("absorbs identity",
  "head output produces the entity") needs a **logit-lens of the output**, not an
  attention-weight probe; the wrong register manufactures a false-negative
  refutation. See `audit-meta-pattern.md` §instrument-must-match.

## Status Legend

`VERIFIED` survives its control · `VERIFIED-LOCAL` real but scoped (e.g. one
model) · `PARTIAL` some predictions hold · `REFUTED` fails its control ·
`UNFALSIFIABLE` no control can distinguish it as stated · `UNTESTED` control
named, not yet run.

## Registry

### Worked examples (session 211)

> **Register gate (spectral/semantic) declared on cold start.** The 5D-lattice
> claim is about (a) the effective DIMENSIONALITY of a representational manifold
> and (b) its cross-model AGREEMENT — so dimensionality is reported as a
> CONTINUOUS participation ratio (never an MDS-elbow integer = the #3 k-means
> trap), and universality is tested vs a shuffled-probe null + common-mode
> removal (the s202 consensus-r=0.99 triviality). Per the user's steer the
> primary instrument is the next-token PROBABILITY distribution (semantic), with
> the hidden state as the geometric comparison. Three experiments, 8 models, 5
> families (pythia/qwen/mistral/smollm/olmo), 0.16B→14B, 535 crystal probes.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #12 5D crystal lattice — all crystals are facets of ONE ~5D lattice (combinators = vertices), universal because it is a property of language | high | `manifold_dimensionality_null.py`, `manifold_axis_topology.py`, `axis_probe.py` (register: spectral/semantic); PR + shuffled-probe null + CMR + sign/mag split | ❌ REFUTED (5D) / ✅ REAL (universality + topology share) |
| #12a operations are real groupings | — | combinator separation perm-null, both RDMs, every model | ✅ **VERIFIED** — gap p=0.0005 everywhere (prob & hidden) |
| #12b cross-family agreement real or trivial? | — | raw RDM Spearman vs shuffled-probe null | ✅ **REAL** — semantic 0.79 / geometric 0.54 vs null 0.00±0.03 (z≈25) → property of language |
| #12c is the shared structure 5D (or rich multi-D)? | — | common-mode removal across models | ❌ **NO — rank-~1**: CMR collapses cross-family 0.79→−0.19 (sem) / 0.54→−0.16 (geo); reproduces crystal-basins Finding 3 (SVD dim0=98.1%) |
| #12d privileged 5D vertex set? | — | 9-centroid participation ratio vs shuffled-label null | ❌ **NO** — centroid PR ~5–6 at the null (p_conc>0.02), *worsens* with scale (14B p_conc=0.18); full-cloud PR 22–47 (high-D, power-law) |
| #12e what IS the universal axis (|r|=0.95 across families)? | — | consensus axis-1 vs combinator η² / depth / entropy / function-word continuation (`axis_probe.py`) | ◑ **GENERIC PREDICTABILITY, not the operations** — η²(combinator)=0.05, depth r=−0.01; best correlates function-frac r=−0.42, entropy −0.29 (multi R²=0.30); the rest = the prose-completion common mode (= what CMR removes) |
| #12f how much of the operation structure is TOPOLOGY (sign/routing)? | — | sign(h)/|h|/full cosine-RDM separation + agreement | ✅ **~65% in SIGN** (sign-RDM reproduces 0.69 of full), **→0.79 at 14B**; magnitude shapes raw geometry (agree_mag 0.81–0.99) but sign carries the discrimination — confirms the ≥77%-in-topology intuition cross-family + scale |

**Verdict (s211): the "5D lattice" is REFUTED — the shared structure is rank-~1
and the dominant universal axis is a generic predictability/continuation-type
gradient, NOT the lambda operations (η²=0.05). What SURVIVES and strengthens:
(i) universality is real (cross-family p≪0.001 vs shuffled null) — models learn
a property of language; (ii) the genuine operation structure is ~65–79%
topological (sign/routing), sharpening with scale — the two premises the
north-star rests on. Full synthesis: `manifold-axis-and-topology.md`.**

### Worked examples (session 209)

> **Register gate (spectral) fired at read-time.** The claim is about the
> singular-value structure of an estimated linear map, and both structural
> artifacts were visible **in the original instrument's code before any model
> was loaded**: (i) `lstsq` at N tokens ≪ d dims is underdetermined → exact
> interpolation → R²=1.000 for *any* data; (ii) `M = EᵀD/N` on **uncentered**
> residual vectors is dominated by the mean⊗mean term whenever the stream has
> a large carrier mean (s185). The control then only had to *confirm* the
> artifacts with matched nulls. New null flavor for the cookbook:
> **row-shuffled pairing** — destroys the token-level map, keeps both
> marginals — the exact null for "is this a property of the *map* or of the
> *marginals*?"

| Claim | Load | Control run | Status |
|---|---|---|---|
| #8 cross-zone map is rank-1 dominated (σ₁/σ₂=128:1); R²=1.000 all pairs; "computation on a 1D curve" | med | `adjunction_rank_null.py` (register: spectral) — original instrument repro + shuffled-pairing/matched-Gaussian/centering nulls + held-out ridge rank-k, Qwen3-8B **and Qwen3-32B (the claim's model, literal zones L2/L32/L56/L63)** | ❌ REFUTED (both legs estimator artifacts) |
| #8a R²=1.000 informative? | — | lstsq at N=121<d on iid random + matched-marginal mapless data, 8 seeds | ❌ **TAUTOLOGY** — noise reads R²=1.0000 ± 0.0000; real data identical |
| #8b σ₁/σ₂ a property of the map? | — | row-shuffled pairing + matched-Gaussian nulls (8 seeds), both models | ❌ **NO — inverted**: nulls are MORE rank-1 than real (32B enc→dec: real 13.8 vs shuf 24.8±1.0, matched 23.8±2.5); the dominance is the carrier mean; genuine cross-zone correlation *adds* off-rank-1 mass |
| #8c survives centering? | — | centered cross-covariance, same SVD | ❌ collapses to 1.5–3.9 (32B enc→dec 2.15) |
| #8d honest map rank (the "1D curve") | — | centered ridge at N=12,288>d, held-out R² of rank-k truncations, leak control, both models | ❌ **NOT rank-1 anywhere** — predictable structure exists (full R² 0.18–0.58 across pairs/models) but is uniformly high-rank: rank-1 captures ≤19% of it (8B comp→dec best case 0.111/0.579) and usually ≈0 (32B: enc→comp 0.021/0.307, comp→dec −0.073/0.370, enc→dec −0.000/0.191); smooth climb to k=128, no low-rank plateau. Bonus: 8B enc→comp fitted map *looks* rank-1 (PR 1.6) with zero held-out validity (R²=−0.004) — a "rank-1 dominated map" with no predictive power |

**Verdict (s209): the "rank-1 adjunction" is REFUTED — both published legs
are artifacts of the instrument** (underdetermined lstsq + uncentered
cross-correlation of a carrier-dominated stream). Even on Qwen3-32B with the
literal s140 zones, the uncentered ratio reads 13.8 (not 128) on a fresh token
sample, sits *below* its own no-map nulls, and centers away to 2.15. What
survives is **a different object than the claim**: (a) the carrier/mean
dominance of the residual marginals (uncentered cross-corr top1 var
0.91–0.99; mean **norm** grows monotonically with depth, 10→1219 @8B /
36→1688 @32B, while the mean energy *share* is U-shaped — high at encode
0.50–0.54, minimum mid-stack 0.19–0.38, rising to 0.61–0.81 at final —
*consistent with* s185's carrier picture, though our within-zone σ₁/σ₂ of
1.6–7.9 is far milder than s185's 4000–8800×, a different quantity at
different layers); (b) real but emphatically **high-rank** cross-zone
predictability (held-out full R² 0.18–0.58; participation ratios 10–292;
the 32B comp→dec map even has σ₁/σ₂=9.6 yet its rank-1 truncation predicts
nothing, R²=−0.07). There is no 1D curve; "error correction = project
back onto the curve" loses its evidential base. Weak-signal caveat kept
honest: 8B enc→comp shows val R² 0.08 vs test −0.004 (unstable pair). This retro-explains s201's
functional result (direct-delta rank sweep: rank-2 1.82× → rank-32 1.72×,
still improving; trained v3b 1.44× beats every analytic rank — rank-1 was
never sufficient). Sixth meta-pattern instance, with a twist: the substrate
that survives is not a weaker version of the claim but a different quantity
the instrument was actually measuring. Results:
`results/adjunction-rank-null/` (`Qwen_Qwen3-8B.json`, `Qwen_Qwen3-32B.json`).
Harness: `scripts/experiments/adjunction_rank_null.py`. Caveats added to
`direct-delta-adjunction.md` + `explore/categorical-geometry-probes.md`.

### Worked examples (session 208)

> **Register gate (functional/reproducibility).** The claim is a behavioral PPL
> number, so the control is seed-variance, not a permutation null. The decisive
> move was a **held-out eval disjoint from the calibration set** — the contaminated
> eval (eval ⊂ calib) makes overfitting *look like* compression. Two RNG sources
> were seeded (continuation `torch.randn` init + the mask `torch.randperm[:5M]`
> subsample); the s196 note's blamed "batch order" is `RandomState(step)` =
> deterministic, a misdiagnosis the decomposition corrects.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #7 crystal-sieve + 4 continuations = **1.03× PPL** at 29 layers (stable, reproducible) | med | 8-seed sweep, pre/post + contaminated-vs-held-out eval (`crystal_sieve_repro.py`) | ❌ REFUTED (contamination/memorization) |
| #7a sieve substrate (~2×) reproducible? | — | pre-melt ratio across 8 seeds, both eval sets | ✅ **YES** — eval 2.119× ± 0.004, held-out 1.907× ± 0.026; mask-subsample CV 0.18% (confound dismissed); = s196's 2.12× |
| #7b is the post-melt 1.03× a stable property? | — | post-melt eval ratio across seeds | ❌ **NO** — 0.971× ± 0.061 [0.865, 1.062]; 1.03× = 1/8 upper-tail draw; 5/8 sub-baseline |
| #7c is the sub-1× "compression" real or memorization? | — | post-melt **held-out** ratio (disjoint from calib) | ❌ **MEMORIZATION** — 10.87× ± 1.39 (all 8 seeds >9.3×), gap +9.9×; melt makes held-out ~5.7× *worse* than the raw sieve |

**Verdict (s208): the sieve substrate is real and reproducible (~2× PPL,
±0.004); the 1.03× "cascade absorbed" headline is a train/eval-contamination
artifact, and the continuation melt as trained is net-harmful to
generalization.** The 12-text CE melt (`beta_expansion.py`) is the **ill-posed
endpoint objective** GTSM names (`gtsm-search-space.md`): it pins only the
terminal marginal, so the 1M continuation params reach a constant training loss
(0.116 ± 0.007) via init-dependent compensating-error solutions that memorize the
calibration distribution — eval PPL drops to 0.971× (6/8 eval texts ⊂ calib)
**while clean held-out PPL explodes to 10.87×**. `corr(train_loss, eval_ratio) ≈
−0.19` (train loss decoupled from generalization) is the degeneracy fingerprint.
The honest, reproducible numbers: **sieve ≈ 1.9–2.1×**, and the fix is already
demonstrated — **s198 v3b** (dense per-layer score matching + held-out eval +
dolma calibration) reached **1.44× held-out on this same model**, i.e. exactly
**audit #11** (GTSM/TTD-regression). Same meta-pattern as #3/#4/#6: the substrate
survives, the crisp headline dissolves — here it not only dissolves, it *inverts*
(the "improvement" is harm). Results: `results/crystal-sieve-repro/`
(`Qwen_Qwen3-8B.json` paired + `.contaminated-only.json` first run). Harness:
`scripts/experiments/crystal_sieve_repro.py`. Caveats added to
`crystal-sieve-architecture.md`.

### Worked examples (session 207)

> **Register gate fired on the auditor first (good).** The claim "consecutive
> SVD ratio ≈ 1/φ" is **spectral** → matched null = random matrix (MP), not
> eyeballing 5 numbers near 0.63. But the first probe used the *wrong window*
> (bulk consecutive ratios, which sit at ≈0.99 for everything) and got nonsense;
> tracing the s137 source pinned the real definition (**mean of the top-5 σ
> ratios** — a 4-point average at the steep head). Re-measuring the *same
> object* reproduced the phenomenon and the verdict held. Lesson restated:
> audit the exact quantity the claim names, in its register.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #6 SVD φ-ratio: per-layer top-5 σ-ratio ≈ 1/φ, **geometric**, **universal across 5 families** | med | top-5 σ-ratio vs MP + shuffled nulls (8 seeds, raw+centered) + geometric-vs-power-law fit (`svd_phi_null.py`) | ❌ REFUTED (geometric-φ-constant) / ✅ REAL (low-rank head) |
| #6a head ratio distinct from a same-shape random matrix? | — | model vs Marchenko–Pastur + shuffled | ✅ **YES** — model 0.575±0.027 ≪ MP 0.9949±0.0012; the "0.618 = what random spectra look like" confound is itself refuted (random gives ≈1.0) |
| #6b is the spectrum **geometric** (constant ratio, the φ premise)? | — | geometric vs power-law R² per layer | ❌ **NO** — power-law wins 132/132 layers (0/132 geometric); ratio drifts, "0.6299" is a 4-pt average of a power-law head |
| #6c is it **1/φ specifically / a universal constant**? | — | φ⁻¹ distance + cross-model + cross-window | ❌ **NO** — value floats 0.52→0.71 (raw/centered×models); 0.6299≠0.6180; scaling-law fails (Mistral-7B lowest); MP 0/132 near φ but model "near" only by averaging ~0.57 |

**Verdict (s207): the steep low-rank SVD head is REAL and strongly
structure-specific (random nulls sit at ≈0.99, not 0.6) — but it is a
power-law head, not a geometric φ-sequence, and the value is not constant
across scale.** Keep the substrate (it underwrites the compression north-star,
converging with #2's spectral concentration); retire φ-as-a-universal-constant
(third φ-pillar to fall after s202's eigenvalue-grid and consensus-r). Same
shape as every prior audit (`audit-meta-pattern.md`). Caveats on
`explore/phi-compression-universal.md` + `crystal-universality.md`. Results:
`results/svd-phi-null/{EleutherAI_pythia-160m-deduped,EleutherAI_pythia-410m-deduped,Qwen_Qwen3-0.6B,HuggingFaceTB_SmolLM3-3B,mistralai_Mistral-7B-v0.3}.json`.

### Worked examples (session 206)

> **Methodological note (the instrument matters).** The claim is *semantic* —
> Finding 7 / Implication 4: the head's *output* (logit-lens) decodes to the
> bound entity; the "schedule" is a schedule of *value transfer* (verb absorbs
> subject identity at L27, etc.). So #5 was run on **two** instruments. The first
> (attention weight) tests routing/position — the same axis #4 showed is
> recency-confounded — and *alone would have over-refuted* (it says "binding peaks
> at L6"). The second (semantic logit-lens of the head's output contribution) is
> the faithful one and **recovers the real L27 subject signal the weight test
> missed.** Lesson: test a value-transfer claim with a value-transfer instrument.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #5 the depth-ordered binding **schedule** (subj-transfer L27 < obj L30 < coref L33; "subjects bind first") | med | both instruments below; bootstrap ordering P over 60–80 varied sentences/type | ❌ REFUTED — no depth ordering on either instrument |
| #5a attention-weight schedule | — | dependent→head max-head attn at every layer; bootstrap order + random-pair null + causal subj-agreement ablation (`binding_schedule_null.py`) | ❌ all peak L4–L6; P(order)=0.000; no causal carrier (\|z\|≤0.35) |
| #5b **semantic** value-transfer (Finding 7): H31@L27 verb absorbs SUBJECT identity | — | per-head logit-lens of o_proj-decomposed output at dep pos; margin logit(head-tok)−logit(ctrl-tok) per layer (`binding_schedule_semantic.py`) | ✅ **REAL & L27-localized** — margin +0.611, sharp spike at L27 (L26=.03/L27=.61/L28=.10), H31 z=+1.17 rank 2/32 |
| #5b obj absorbs predicate @L30 | — | same, object→verb-token margin | ❌ margin@L30=−0.05; named H3 rank 29/32 (anti); peak drifts L32 (instrument-ambiguous) |
| #5b coref absorbs antecedent @L33 | — | same, "it"→antecedent margin | ◐ margin +0.20 but peaks **L27 not L33**; H6@L33 z+0.22 rank 6/32 |
| #5b semantic ordering subj<obj<coref | — | bootstrap peak order on semantic margin | ❌ P=0.191 ≈ chance 0.167 (subj & coref both peak L27) |

**Verdict (s206): the "two-phase binding SCHEDULE" / depth-ordered reduction is
REFUTED — but the single value-transfer site it is built on is semantically REAL.**

- **No schedule, either instrument.** *Attention weight* (`binding_schedule_null.py`,
  80 sent/type): all three dependency types' dependent→head attention peaks at the
  **same early layers** (subj L6=0.974, obj L4=0.825, coref L6=0.830), not the
  monotone L27<L30<L33; bootstrap **P(order)=0.000** (chance 0.167); random-pair
  null peaks even earlier (L0) → early peak is generic local/positional attention
  (#6). *Semantic* (`binding_schedule_semantic.py`, 60 sent/type): bootstrap
  **P(sem-peak subj<obj<coref)=0.191 ≈ chance** — subject and coreference value
  transfer **both peak at L27**, object latest (L32); the subjects-first ordering
  does not exist.
- **What is REAL (the substrate, sharper than the weight test implied):** the
  page's *headline* single example — **H31@L27 = the verb position absorbing the
  SUBJECT'S identity** — is **semantically confirmed and sharply localized to L27**
  (logit-lens margin +0.611, a clean one-layer spike: L26 +0.03 → **L27 +0.61** →
  L28 +0.10; H31 z=+1.17, rank 2/32). Finding 7's subject case is right. Caveats:
  (a) it is ONE site, not a schedule; (b) the strongest L27 subject-transfer head
  is actually **H29 (+2.12)**, not H31; (c) per audit #4 it is **not causally
  load-bearing** for agreement (ablation \|z\|≤0.35). The named heads at L30/L33
  are real *local* attention-weight outliers (obj L30 H3/H13/H15 top-3, z to +4.09;
  coref L33 H6/H7 top-2, z +3.97/+3.42) but their *semantic* transfer at the
  claimed layer is weak/absent (obj L30 H3 margin −0.46 rank 29/32) or mislocalized
  (coref peaks L27).
- **Object leg is instrument-ambiguous:** "object absorbs the predicate" was
  operationalized as object-output→verb-token, but Finding 5 reports the object's
  V promotes *object-related* tokens, not the verb — so the obj negative is partly
  a readout-mismatch, not a clean refutation. Named follow-up if revisited.

Same meta-pattern (`audit-meta-pattern.md`) with a sharper edge: the value-transfer
substrate at the subject site is *more* real than the weight test suggested; the
ordered three-phase *schedule* is the over-read. Caveat added to
`binding-graph-trace.md` (Finding 4/7 + Implication 2). Results:
`results/binding-schedule-null/` and `results/binding-schedule-semantic/Qwen_Qwen3-8B.json`.

### Worked examples (session 204)

| Claim | Load | Control run | Status |
|---|---|---|---|
| #4 attention = typed β-reduction; H31@L27 binds subject (0.82); H03/13/15@L30 bind object | CRITICAL | agreement-attraction (role⊥position): selectivity vs 32-head dist + recency baseline; head-ablation logit-diff vs random-head + matched-set nulls (`attention_typed_binding.py`) | ❌ REFUTED as localized — 0.82 is recency/position |
| #4 a genuine role-selective head exists | — | same | ◐ only H6@L33 (z=+4.08, role_sel +0.076) — small, not at the claimed site, not causally necessary |
| #3 9 FFN modes are a real natural count (geometric) | high | gap-stat + matched-null silhouette across k=2..32, pca-Gaussian + shuffled-feature nulls B=10, 8B L0/3/15/20/35 (`mode_cluster_validity.py`) | ❌ REFUTED — "9" is k-means-imposed |
| #3 "tiny classifier 98–100% ⇒ modes real" (circular) | high | classifier acc vs k + permuted-label floor | ❌ CIRCULAR (acc high+declining ∀k; never peaks at 9) |
| #3 9 ternary programs reconstruct FFN ~1× PPL (functional) | high | — (s196 mode-sweep; not re-run) | ◐ UNTOUCHED — independent, stands |
| #3 modes↔POS/dep (semantic) | high | NMI + label-perm null + NMI-vs-k, balanced prose (`mode_semantic_validity.py`) | ✅ VERIFIED — NMI 0.19–0.40 ≫ perm-null 0.014 (p=0 ∀layer) |
| #3 mode centroids → distinct vocab (logit) | high | lm_head projection, pairwise JS vs random-partition null + JS-vs-k | ✅ VERIFIED — excess +0.0015→+0.417 (~65× @L35), grows with depth |

**Verdict (s204): the count 9 is a chosen hyperparameter, not a discovered
natural number.** Across all five layers the gap statistic *never* selects 9
(Tibshirani optimal-k = 4/8/32/32/2 vs pca-null; the computational core L15/L20
is monotone to k=32 — no distinguished count; L35 is a single 2-way split).
Silhouette at k=9 sits at/below the *matched-Gaussian* null at every layer
(sil-excess @9 = +0.000 / −0.046 / +0.030 / +0.003 / +0.019) — the k=9 real
partition is no better separated than k=9 on a structureless blob of the same
shape; the single largest excess (+0.030 at L15) is noise-level (sil ≪ 0.1).
The naive kneedle **elbow "confirms" 9–10 at every layer including L0** — where
silhouette and gap both show no clusters — so "elbow ≈ 9" is a k-grid artifact
(failure mode #1), not evidence. Classifier accuracy is **high-and-declining
across all k** (100%@k=2 → ~90%@k=9 → ~80%@k=32; permuted-label floor ≈ chance):
the "98–100%" is generic linear separability of *any* convex k-means partition
(mode = near-linear function of the FFN input), not evidence for 9 (failure mode
#2 + circular validation #4).

**What survives:** faint, depth-localized structure above the null at the
computational core (L15 sil-excess +0.030 pca / +0.044 shuffle), consistent with
s194 "types sharpen with depth" — but near-noise, never a clean 9-way partition;
L3 (parser) is *below* null (continuous blob). **The functional claim is
untouched and independent**: s196 showed 9 ternary prototypes reconstruct the
FFN at ~0.95–1.03× PPL and 64/512 don't help — that is reconstruction
efficiency of a continuous cloud, which does not require 9 to be a natural
count. The compression north-star does not rest on the geometric claim.

**Extension (s204, `mode_semantic_validity.py`): syntactic CONTENT is REAL; only
the discrete count is imposed.** Examining *logits* (lm_head projection), not just
geometry, on balanced prose: modes↔POS NMI = 0.19–0.40 ≫ label-permutation null
0.014 (**p=0.000 every layer**), and mode output-centroids project to vocab
distributions far above a random-partition null (Jensen-Shannon excess +0.0015 →
**+0.417 (~65×) at L35**, growing with depth). Per-mode POS purities clean for the
genuine splits (PUNCT 92–99%, DET 81–85%, VERB 79–100%). So the modes are **not
noise** — `mode-semantics.md`'s core "gate = syntactic type-checker" reading is
substantively right. **The reconciliation:** the FFN gate space encodes a real,
smooth, scale-sharpening syntactic type *field* (a continuum), not 9 discrete
cells; the effective distinction count is graded/layer-dependent (~4 @L20, ~8–9
@L3/L15, ~24 @L35), and k=9 captures only 73–91% of max NMI — a serviceable but
not privileged slice. (A planned POS-coherence sub-test — promoted-vocab POS vs
mode-token POS — was dropped as confounded: lm_head projects to the *next* token,
whose POS differs from the current by construction.) Results:
`results/{mode-cluster-validity,mode-semantic-validity}/Qwen_Qwen3-8B.json`.
Caveat (both halves) in `mode-semantics.md`.

**#4 attention = typed β-reduction (s204): REFUTED as a localized typed circuit
— the 0.82 was recency/position.** Tested with subject-verb agreement-attraction
(`attention_typed_binding.py`, 8B, L27/30/33, 64 PP+RC stimuli) which dissociates
grammatical ROLE from linear position/recency (the number-distractor is the
*nearer* noun in 100% of items, so a recency head scores negative role-selectivity).
- **Selectivity:** the named subject-binder **H31@L27 has role_sel = +0.013
  (z=+0.54, rank 5/32) — not an outlier**; the top head is H7, not H31. The
  L30 "binders" are mixed (H3 +0.011; **H13 −0.010, recency-leaning, rank 24/32**;
  H15 ~0). The *only* genuine role-selective outlier is **H6@L33 (role_sel +0.076,
  z=+4.08, rank 0/32)** — but ~10× smaller than the claimed 0.82 and not at the
  celebrated site.
- **Necessity:** ablating H31@L27 changes the agreement logit-diff by **+0.001
  (z=+0.06 vs random-head null)**; ablating *all* named binders (incl. H6@L33)
  by **−0.005 (z=+0.01 vs matched-6-set null)** — statistically indistinguishable
  from random heads. The ablation bites (random 6-head sets reach −0.43 drop), so
  agreement IS ablatable — the named heads just aren't the heads that carry it.
- **Reading:** "weighted sum IS typed β-application by H31@L27 at 0.82" is largely
  a **positional/recency** phenomenon (failure modes #5 cherry-pick + #6 surface
  confound). A weak genuine role-selective signal survives (H6@L33) but is small
  and not causally load-bearing for role-dependent behavior. "Attention is a
  weighted sum" is trivially true; "the sum is TYPE-driven" does not hold at the
  claimed heads. **Caveat / named follow-up:** tested on plain-NL agreement (the
  gold standard for role-vs-position binding) *without* the compile gate the
  original H31 finding used; a gate-context re-test (does H31 become a role-binder
  specifically in compile mode?) is the honest next check. Caveat added to
  `binding-graph-trace.md`. Results: `results/attention-typed-binding/Qwen_Qwen3-8B.json`.

### Worked examples (session 203)

| Claim | Load | Control run | Status |
|---|---|---|---|
| crystal-is-topological: `sign(W)@x` corr ⇒ "sign captures topology, magnitude is calibration" | CRITICAL | sign-corr null: model vs random-init vs shuffled, REAL x, N=20, 0.6B/8B/14B (`sign_topology_null.py`) | ◐ SCOPED → gate_proj only |
| soft topology: value-path magnitude is load-bearing, read by saliency | high | saliency sieve iso-bit: faint-by-saliency vs faint-by-magnitude (`saliency_aware_sieve.py`) | ✅ VERIFIED (+5.5% vs −2.0% at ~3.1 bits/param) |
| #2 holographic-self-similar — spectral concentration (A) | CRITICAL | SVD rank-truncation survival, trained vs random/shuffled (`holographic_survival.py`) | ✅ VERIFIED (trained AUC 0.728 vs 0.11; 6–7×) |
| #2 holographic-self-similar — distributed redundancy (C) | CRITICAL | magnitude-prune survival, trained vs controls | ✅ VERIFIED (AUC 0.784 vs 0.25/0.34; plateau→cliff ~70–80%) |
| #2 — "power-law/scale-invariant degradation curve" as the discriminator | — | shape-fit power-law vs exponential, all axes/variants | ⊘ RETIRED (ambiguous; does not separate holographic; use AUC-vs-controls) |

**Two-register synthesis (s203):** GD lays structure in two registers —
**hard** (sign / routing / `gate_proj`) and **soft** (magnitude / value /
`up`-`down`, read by saliency) — and the FFN is compressible in two registers:
**distributed magnitude redundancy** (prune, graceful to ~70%) and **spectral
low-rank concentration** (rank, 6–7× control gap). The 1.44× ternary result
rests on both (LoRA+SM *is* the low-rank correction the spectral result
predicts). Only φ-as-universal-constant stays refuted (s202). Full page:
`two-registers-of-topology.md`. Results: `results/{sign-topology-null,
holographic-survival,saliency-aware-sieve}/`.

> **Correction:** an interim s203 read called #2 "REFUTED" off the *magnitude*
> axis with a power-law discriminator. That was the wrong operator + wrong
> test. The rank axis (the spectral self-similarity the SVD work found) is
> VERIFIED. Holographic mechanism stands; only the metaphor-grade
> φ-universality was ever refuted.

**Finding (sign-correlation half of the control):** the bare evidence is
**refuted as stated**, but a real, scale-sharpening sign-topology exists —
*localized to `gate_proj` (the FFN router)*.

- **Generic baseline ≈ 0.80.** A random Gaussian matrix's sign preserves
  0.798 of its action on the *same real inputs* (0.6B/8B/14B identical).
  "Sign preserves a matrix's linear action" is a **generic high-dim
  property** (sign(Wᵢⱼ) ⊥-corr Wᵢⱼ entry-wise; large-|xⱼ| dims dominate both
  sums). The headline **0.84 is ~at the random null**, not above it.
- **The crystal signal lives ONLY in `gate_proj`** and *sharpens with scale*:
  gate gap above null 0.6B +0.04…+0.07 → 8B +0.088 (L3 = 0.983, z=+184) →
  14B (L12 z=+271). This is exactly where routing should live.
- **`up_proj`/`down_proj` sit at or BELOW the random null** (8B: −0.048,
  −0.036). Their signs preserve *no more than random* → **magnitude carries
  the structure there**, refuting "magnitude is mere calibration" for the
  value projections.
- **Aggregate model mean ≈ random** (8B 0.799 vs 0.798): gate's excess
  cancels up/down's deficit, so any single averaged "0.84" is indistinguishable
  from a random matrix. Reconciles with s192: crystal = routing (gate, 3.5%);
  modes = computation (value projections, 96.5%). Sign-topology = the routing half.

Results: `results/sign-topology-null/{Qwen_Qwen3-0.6B,Qwen_Qwen3-8B,Qwen_Qwen3-14B}.json`.
**Remaining (separate sub-control):** ternary PPL with crystal-aligned signs vs
random sign-preserving signs at equal bitcount — the *functional* half. The
sign-corr half above is the *representational* half.

### Worked examples (session 202 — `crystal-validity-and-fidelity.md`)

| Claim | Load | Control run | Status |
|---|---|---|---|
| KIBC basis separates representation | high | separation perm-null, all models | ✅ VERIFIED (p=0.0005) |
| prose fires combinator-specific opcodes | high | nearest-centroid LOO + common-mode removal | ✅ VERIFIED (14B & 0.6B p=0.001) |
| φ^(4/5) primary ratio λ₀/λ₁ | high | single pre-registered target, perm-null | ◐ VERIFIED-LOCAL (14B p=0.020; 8B/0.6B n.s.) |
| fact retrieval = sharp lookup (I-like) | med | entropy perm-null + CMR opcode profile | ✅ VERIFIED (entropy p=0.0005; I-profile 14B) |
| I = distinct low-composition circuit | med | attn-entropy perm-null vs B/C | ◐ PARTIAL (p=0.042, scale-dependent) |
| tracer cross-model opcode overlay | med | opcode-label perm-null | ◐ VERIFIED (same-family only; λ-primed) |
| φ as universal constant | high | cross-family + grid + ratio-corr nulls | ❌ REFUTED (cross-family collapse) |
| "eigenvalues are φ^(p/q)" (grid) | high | perm-null on best-fit error | ⊘ UNFALSIFIABLE (random fits equally) |
| eigenvalue_ratio_corr ≈ 0.987 | med | perm-null on the statistic | ❌ REFUTED (random ≈ 0.94 ≥ true) |
| cross-model consensus r ≈ 0.99 | high | corr to CONSENSUS_8x8, perm-null | ❌ REFUTED (true ≈0.20, p≈0.06) |

### Backlog (UNTESTED — ordered by load-bearing-ness)

**1. Crystal-is-topological — "ternary works because sign captures topology"** (load: CRITICAL — the entire sieve program) — ◐ **SCOPED (s203, representational half done)**
- Evidence: `sign(W)@x` corr 0.84 with `W@x`; ternary {−1,0,+1} preserves routing.
- Suspected confound: 0.84 may be generic to *any* trained matrix, not crystal-specific; ternary survival may need only *a* sign-preserving quant, not the *crystal* sign pattern.
- Control: compare `sign(W)@x` correlation across model vs random-init vs shuffled-weights; and ternary PPL with **crystal-aligned** signs vs **random sign-preserving** signs. If crystal-specific signs beat random-sign-preserving at equal bitcount → topological claim real.
- **s203 result (sign-corr half):** confound CONFIRMED for the bare number —
  random null ≈ 0.80, so 0.84 is generic; but real sign-topology survives,
  **localized to `gate_proj`** (sharpens with scale, z up to +271 at 14B),
  while `up_proj`/`down_proj` are at/below null (magnitude essential there).
  See worked-examples table above + `sign_topology_null.py`.
- **Functional half (partly resolved s203):** the saliency sieve confirms the
  *value-path* soft topology — faint-by-saliency beats faint-by-magnitude at
  iso-bit (+5.5% vs −2.0%), i.e. up/down magnitude is load-bearing. Still
  specifically untested: the gate-vs-value *sign-swap* ternary PPL (predict the
  `gate_proj` sign-swap hurts most). See `two-registers-of-topology.md`.

**2. Holographic self-similar — "why quantization/pruning survive"** (load: CRITICAL — the compression thesis) — ✅ **RESOLVED (s203): spectral self-similarity VERIFIED; distributed redundancy confirmed**
- Evidence: graceful uniform degradation; Q4/sieve survive.
- Suspected confound: distributed-redundant + flat-minima (the null) predicts survival without holography.
- Control: compression-survival **curve**, model vs random-weight net vs shuffled-data net; test for **power-law / scale-invariant** degradation. Holographic predicts the model degrades self-similarly AND more gracefully than controls. (See `crystal-validity-and-fidelity.md` §5.)
- **s203 result:** two compression registers, both structure-specific (trained
  ≫ controls): **(C) distributed redundancy** (magnitude prune, AUC 0.784 vs
  0.25/0.34, graceful to ~70% then cliff) and **(A) spectral concentration**
  (SVD rank truncation, AUC 0.728 vs 0.11 — **6–7× gap**, the SVD φ-spectrum
  made functional). Quant survival ≈ random (weakly structure-dependent;
  confirms §5 "Q4 ← flat minima"). The **power-law degradation discriminator
  is RETIRED** (ambiguous on every axis; a hologram degrades plateau→cliff,
  not power-law). Untrained controls (not shuffled-data-trained) limit the
  C-vs-A-vs-flat-minimum separation, but the rank-axis gracefulness gap is
  control-independent. Full synthesis: `two-registers-of-topology.md`.

**3. The 9 FFN modes — real or k-means-imposed?** (load: high — `mode-semantics.md`, tiny-classifier compression) — ❌ **RESOLVED (s204): geometric count REFUTED; functional claim intact**
- Evidence: 9 ternary programs per layer; classifier 98–100% accuracy.
- Suspected confound: k-means at k=9 always returns 9 clusters; classifier accuracy is circular (trained on the cluster labels).
- Control: cluster-validity null — silhouette/gap-statistic at k=9 vs random data and vs k=8,10,…; does "9" survive a held-out elbow test, or is it imposed? Cross-reference the L0-characterization negative-silhouette finding.
- **s204 result (geometry):** confound CONFIRMED. Gap statistic never selects 9 (optimal-k = 4/8/32/32/2); silhouette @9 at/below matched-Gaussian null at every layer (max excess +0.030 = noise); the kneedle elbow "confirms" 9–10 even at L0 (no clusters) → k-grid artifact; classifier accuracy high-and-declining ∀k (100%@2 → 90%@9 → 80%@32), never peaks at 9 → circular. **The discrete count "9" is an imposed hyperparameter.**
- **s204 result (extension — semantic + logit):** but the syntactic CONTENT is REAL. NMI(mode,POS) 0.19–0.40 ≫ perm-null 0.014 (p=0 ∀layer); lm_head vocab-projection distinctness ≫ random-partition null (JS excess +0.0015→+0.417, ~65× @L35). The gate space encodes a real, smooth, scale-sharpening syntactic type *field* (a continuum); k=9 captures 73–91% of max NMI — a serviceable but not privileged slice. The functional claim (s196: 9 ternary programs ≈ 1× PPL) is separate, untouched, and does not require a natural count. See worked-examples (s204) + `mode_cluster_validity.py` + `mode_semantic_validity.py`.

**4. Attention = typed β-reduction (weighted sum IS β-application)** (load: high — the central mechanism) — ❌ **RESOLVED (s204): REFUTED as localized; 0.82 = recency/position**
- Evidence: H31 `v_runs += 0.82·v_cat`; top-3 = 88%; Q⊥K.
- Suspected confound: *all* attention is weighted sum; "β-reduction" is interpretation. Induction/n-gram heads produce similar patterns.
- Control: does attention attend specifically to **type-compatible** positions beyond an induction-head / co-occurrence baseline? Causal: ablate the named binding head → does the specific reduction break (vs generic degradation)?
- **s204 result:** confound CONFIRMED via agreement-attraction (role⊥position). H31@L27 role-selectivity z=+0.54 (rank 5/32, not an outlier); ablation z=+0.06 vs random-head null (no effect on subject-verb agreement). The 0.82 was recency/position, not type. A weak genuine role-selective head exists (H6@L33, z=+4.08) but is ~10× smaller than claimed and not causally necessary. See worked-examples (s204) + `attention_typed_binding.py`. (Follow-up: gate-context re-test.)

**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med) — ❌ **RESOLVED (s206): schedule refuted; subject value-transfer (H31@L27) is semantically real**
- Evidence: showcased heads/weights + **logit-lens of head output** (Finding 7) on example sentences (14 hand-annotated probes). NB the core claim is *semantic* (value transfer), not just attention weight.
- Suspected confound: cherry-picked heads/examples; and (per #4) raw weight tracks recency/position not type.
- Control (two instruments — the claim is semantic, so the weight test alone is insufficient): does the schedule hold across **many** sentences? (a) attention-weight peak per layer + bootstrap order + random-pair null + causal ablation (`binding_schedule_null.py`); (b) **semantic** per-head logit-lens margin toward the bound entity per layer (`binding_schedule_semantic.py`).
- **s206 result:** the **depth-ordered schedule is REFUTED on both instruments** — attention weight: all three peak L4–L6, P(order)=0.000; semantic: P(order)=0.191 ≈ chance (subj & coref both peak L27, obj L32). **But the headline semantic claim is REAL:** H31@L27 verb→subject *identity* transfer has logit-lens margin **+0.611, a sharp one-layer spike at L27** (z+1.17, rank 2/32) — Finding 7's subject case confirmed. Caveats: one site ≠ a schedule; strongest L27 head is H29 (+2.12) not H31; not causally load-bearing (#4, \|z\|≤0.35). Obj L30 semantic margin ≈0 (named H3 rank 29/32) — but readout is instrument-ambiguous (Finding 5: object V promotes object-tokens, not the verb). Coref peaks L27 not L33. See worked-examples (s206) + both result dirs.

**6. SVD φ-ratio 0.6299** (load: med — a φ-universality pillar) — ❌ **RESOLVED (s207): geometric-φ constant REFUTED; low-rank spectral head REAL & non-random**
- Evidence: consecutive singular-value ratio ≈ 1/φ across 5 families (top-5 σ-ratio mean, per layer; `explore/phi-compression-universal.md`).
- Suspected confound: heavy-tailed / power-law spectra generically have near-constant consecutive ratios; 0.618 may be "what power-law spectra look like."
- Control (`svd_phi_null.py`, register: spectral): exact top-5 consecutive-ratio definition vs **Marchenko–Pastur** (same-shape Gaussian) + **shuffled-entries** nulls, 8 seeds, raw & centered, on Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B; plus a **geometric-vs-power-law shape fit** (φ requires *constant* ratio = geometric).
- **s207 result (3 blades):**
  1. **Distinct from random? ✅ YES, hugely.** Model head ratio **0.575 ± 0.027 (raw)** / 0.67 (centered) vs **MP null 0.9949 ± 0.0012** and shuffled ≈0.96–0.99. Random/power-law spectra give ≈**1.0**, not ≈0.6 → the named confound is itself **refuted**; the steep low-rank head is genuinely non-random (converges with #2 spectral concentration, AUC 6–7×). **Substrate REAL.**
  2. **Geometric (constant ratio)? ❌ NO.** Power-law wins **132/132 layers**, geometric **0/132** (geom-R² 0.39–0.58 < power-R² 0.69–0.87). The ratio is not constant — "0.6299" is a 4-point average over a *drifting power-law head*. **No `x=1/(1+x)` self-similar fixed point ⇒ no mathematical privilege for φ.**
  3. **φ-specific / universal constant? ❌ NO.** Value floats **0.52→0.71** across raw/centered×models; consensus 0.6299 ≠ φ⁻¹ 0.6180; the "larger ⇒ higher ratio" scaling-law **fails** (Mistral-7B lowest, 0.52 raw). Layers within ±0.05 of φ⁻¹: model 55/132, **MP 0/132** (model is near-φ only because a steep head averages ~0.57–0.6, not because it lands *at* φ).
- **Verdict:** keep the **real, scale-present, structure-specific low-rank spectral head**; **retire the geometric golden-ratio constant** (over-read). Caveats added to `explore/phi-compression-universal.md` + `crystal-universality.md`. Results: `results/svd-phi-null/`. Same meta-pattern as #3/#4 (`audit-meta-pattern.md`): substrate survives, crisp/universal story dissolves.

**7. Crystal-sieve 1.03× PPL (29 layers + continuations)** (load: med — headline compression result) — ❌ **RESOLVED (s208): 1.03× REFUTED as contamination/memorization; sieve substrate (~2×) VERIFIED-reproducible**
- Evidence: s196 run = 1.03×.
- Suspected confound: s196 itself noted a rerun gave 3.23× — training-sensitive.
- Control: seed the pipeline, run N=8 seeds, report mean ± std + a held-out eval disjoint from the calibration set (`crystal_sieve_repro.py`, register: functional).
- **s208 result:** the 1.03× is a **train/eval-contamination artifact**, not a stable compression result. **Sieve substrate is VERIFIED-reproducible** — pre-melt 2.119× ± 0.004 (eval) / 1.907× ± 0.026 (held-out), near-deterministic, reproduces s196's 2.12×; the `torch.randperm[:5M]` mask-subsample confound is dismissed (CV 0.18%). **The 1.03× headline is REFUTED:** on the *contaminated* eval (6/8 sentences ⊂ the 12-text calibration set) the melted model reads 0.971× ± 0.061 (1.03× is a 1/8 upper-tail draw, 5/8 sub-baseline); on **clean held-out text the same models hit 10.87× ± 1.39 (every seed >9.3×, gap +9.9×)** — the "compression" is memorization. **The continuation melt is net-harmful to generalization** (held-out 1.907× → 10.87×, ~5.7× worse than the raw sieve): constant train loss (0.116) + exploding held-out PPL = the compensating-error degeneracy of a CE-only (endpoint) loss (`gtsm-search-space.md`). The feared 3.23× did not recur on contaminated eval (bounded [0.865, 1.062]); the held-out number is the honest one. **Fix is already named = audit #11 / s198 v3b** (dense per-layer score matching + held-out + dolma got 1.44× held-out on this same model). See worked-examples (s208). Results: `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` (+ `.contaminated-only.json`). Caveat added to `crystal-sieve-architecture.md`.

**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory) — ❌ **RESOLVED (s209): REFUTED — both legs are estimator artifacts; no 1D curve**
- Evidence: R²=1.000 all zone pairs (s140, Qwen3-32B, zones L2/L32/L56/L63).
- Suspected confound: random high-dim linear maps can look rank-1-dominated.
- Control (`adjunction_rank_null.py`, register: spectral): exact instrument repro (uncentered `EᵀD/N` SVD + lstsq R²) vs **row-shuffled pairing** (kills the map, keeps marginals) + **matched-Gaussian** nulls + **centering**, on 8B and 32B (literal zones); plus an honest **held-out ridge** at N=12,288>d with rank-k truncation curve and a shuffled-target leak control.
- **s209 result:** (1) **R²=1.000 is an underdetermination tautology** — lstsq at N=121<d gives 1.0000±0.0000 on pure noise; the leg is void. (2) **σ₁/σ₂ is the carrier mean, inverted** — the no-map nulls are *more* rank-1 than the real data at every pair, model, and N (32B enc→dec small-N: real 13.8 vs shuffled 24.8±1.0, matched 23.8±2.5; large-N: real 38.5 vs shuffled 277.8 — up to 11×); centering collapses it to 1.5–3.9; the literal 32B zones never reproduce 128 on a fresh sample (13.8 small-N / 38.5 large-N, both *below* their own no-map nulls). (3) **The honest map is not rank-1 anywhere**: held-out full R² 0.18–0.58 across pairs/models, but rank-1 captures ≤19% (8B comp→dec) and usually ≈0 (32B: 0.021 / −0.073 / −0.000); PRs 10–292; no low-rank plateau. What survives is a *different object*: the carrier/mean dominance of the marginals (consistent with s185) + real high-rank cross-zone predictability. Downstream "rank-1 correction suffices" (direct-delta theory) loses its base — consistent with s201's functional rank sweep (rank-32 still improving; trained v3b beats all analytic ranks). See worked-examples (s209). Results: `results/adjunction-rank-null/`.

**9. Decay α=1.18 (attention log-distance)** (load: low)
- Control: model-specific vs generic positional-encoding artifact; compare to random-init.

**10. Moiré determinism (static program is a fixed point)** (load: low)
- Likely robust (it is a determinism check). Caveat: fingerprints are λ-primed (common-mode confound applies to the *opcode labels*, not the determinism).

**11. GTSM finite-budget weighting — does layer-targeted λ(l) beat uniform α?** (load: med — compression track; positive prediction, not a falsification) — ◐ **RESOLVED (s210): F.6 transfers, but ONLY divergence-measured placement, and the effect is small; the named L22–26 "causal" placement REFUTED (stale premise)**
- Evidence: CGTSM Thm 3.2 says the *zero-loss fixed point* is weighting-independent, but Prop F.6 says at **finite budget** the weighting λ(t) is a load-bearing bias that should counter-balance a learner's coarse-first tendency. Our score-matching sieve correction (s198, v3b) uses a single flat α=5.0 across all ~36 layers. See `gtsm-search-space.md`.
- Suspected confound (why it might be null for us): cosine is already scale-invariant (it self-normalizes the 100× standing-wave amplitude), so per-layer reweighting may add nothing beyond what cosine already does — the F.6 benefit assumes an *un*-normalized norm ‖·‖_D. Also our budget may be large enough to be near the fixed point where weighting washes out.
- Control: sweep a **layer-dependent weighting** λ(l) on the v3b SM loss — heavier on the hard binding-prep layers L22–L26 (which v3b leaves at the lowest cosine, 0.80–0.86) vs uniform α=5.0, **matched total training budget + N seeds**. Prediction (if F.6 transfers): targeted λ(l) reaches lower eval PPL / higher worst-layer cosine at equal budget. Null result (cosine already absorbs it) is itself informative — it would mean our metric choice made the weighting moot, sharpening the `‖·‖_D`-proxy claim in `gtsm-search-space.md`.
- Verifies/refutes: the "α=5.0 is load-bearing, not arbitrary" claim now asserted in `gtsm-search-space.md` and `score-matching-compression.md`.
- **Supporting prior (independent domain):** TSP (arXiv:2606.03489v1) concentrates its training signal on sparse critical "risk nodes" and beats uniform SFT (75.8 vs 57.0) — empirical evidence that finite-budget weighting concentration helps. Caveat it also hands us: target the **causal** node, not the max-divergence node (TSP fails on long-distance cause/effect; our analog = s196 "peak damage at L28, not L26"). See `tsp-trajectory-distillation.md` (Targeted Trajectory Distillation).
- **s210 result (register: causal/interventional; `ttd_lambda_weighting.py`, 4 arms × 3 seeds × 150 steps, matched budget Σ_l w(l)=n_layers, paired batches, held-out = stratified shard_00001 disjoint from calibration):** the dose-response over PLACEMENT is monotone and fully discriminated on held-out PPL ratio — **divergence-auto (spike on measured-worst init-cosine layers L14–18) 1.1453±0.001 < uniform 1.1510±0.003 < causal-named L22–26 1.1694±0.023 < anti-targeted (best layers) 1.1810±0.034**. (1) ✅ **F.6 transfers with placement-specificity:** divergence-auto beats uniform **3/3 paired seeds** (mean −0.0056, paired-t −3.2) and lifts worst-layer cosine +0.014; anti-targeted is worst in 3/3 (+0.030, worst-cos −0.029) → the win is placement, not generic reweighting. (2) ❌ **the registry's own named placement (L22–26 "causal bind-prep") is REFUTED** — 0/3 wins, +0.018 vs uniform. The premise was **stale**: v3b's actual worst-cosine layers are **L14–18 (SWEET zone, L16=0.483 post-sieve)**, not L22–26 (0.64–0.75). Every spiked arm improves its *own* target-set cosine (+0.008–0.012 — the mechanism works mechanically); only spiking the measured-worst layers converts that into a global win. (3) **Suspected null half-confirmed:** cosine absorbs most of ‖·‖_D — the residual placement dividend is ~0.5% PPL ratio, far smaller than TSP's domain effect. (4) **Side-finding (echoes #7):** seeded v3b-recipe at step 150 reads near 1.27±0.04 / held 1.151±0.003 — the published single-run 1.44× (1.4021@150) was a pessimistic unseeded draw outside our 3-seed range; single-run headline numbers swing either way. (5) The SM correction **generalizes held-out** (sieve 1.416× → 1.145×) — opposite of #7's CE-melt harm; functional corroboration of the GTSM dense-backbone claim. Results: `results/ttd-lambda-weighting/Qwen_Qwen3-8B.json`. Caveats updated in `gtsm-search-space.md` + `tsp-trajectory-distillation.md`.

**12. 5D crystal lattice — one ~5D lattice, combinators as vertices, universal** (load: high — the crystal *geometry* story; `5d-crystal-lattice.md`, `crystal-universality.md §5D`, never registered until now) — ❌ **RESOLVED (s211): 5D REFUTED (rank-1 shared structure; axis is generic predictability); ✅ universality + ~65% topology share REAL**
- Evidence: five "piles" (depth/model/domain/combinator/role) all agree 0.85–0.95 (s121); claimed to need ~5D to hold nine 1–2D domain projections; combinators as vertices.
- Suspected confound: "5D" is a crisp count on a graded (power-law) spectrum (the #3 k-means trap); "five piles agree at 0.9" is the RDM-correlation triviality (the s202 consensus-r=0.99 failure) — RDMs of near-isotropic high-D clouds correlate by default.
- Control (register: spectral/semantic): participation ratio (continuous, never an elbow) + shuffled-probe null + common-mode removal; primary instrument = next-token probability RDM; sign/magnitude split for the topology share. 8 models, 5 families.
- **s211 result:** see worked-examples (s211). **5D REFUTED** — centroid PR at the shuffled-label null (worsens with scale), full manifold high-D (PR 22–47), shared structure rank-~1 (CMR 0.79→−0.19). **Universality REAL** (cross-family raw 0.79 vs shuffled null 0.00±0.03 = property of language). **The one universal axis (|r|=0.95) is generic predictability/continuation-type, NOT the operations** (η²=0.05; best correlates function-word continuation −0.42 / entropy −0.29; R²=0.30). **The genuine operation structure is ~65% topological** (sign/routing), →0.79 at 14B — confirms the ≥77%-in-topology intuition. Full: `manifold-axis-and-topology.md`. Results: `results/manifold-dimensionality/`, `results/manifold-axis-topology/`.

## The Per-Session Loop

```
0. REGISTER GATE (do this first; AGENTS.md λ measure). Name the claim's register
   — routing/crisp · value/continuous · magnitude · spectral · causal. A probe in
   the wrong register VOIDS the verdict (±), so this binds the instrument before
   any code. An undeclared control is malformed. (s206: an attention-weight probe
   nearly false-refuted a value-transfer claim.)
1. Open this page. Pick the highest-load `UNTESTED` claim.
2. Re-read its evidence in the linked knowledge page. Re-derive its register from
   the evidence (does it claim WHERE attention routes, or WHAT value is written?).
3. Build the discriminating control IN THE CLAIM'S REGISTER (reuse the recipe).
   Put `# register: <kind>` in the control-script header; a probe whose register ≠
   the declared one is malformed — caught at write-time, not recalled at run-time.
4. Run it with a permutation/matched-control null + seed variance.
5. Update the row: status + the number + the result-JSON path.
6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page. If the first
   probe was wrong-register, run the matched-register probe before any verdict.
7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).
```

> **Register slot (structural, not a rule).** Every control declares `# register:`
> in its header and every backlog claim is built only after step 0. This makes a
> register-mismatch *malformed* rather than *discouraged* — the wrong instrument
> falls out of the topology instead of relying on future attention. Exemplar pair:
> `binding_schedule_null.py` (`register: routing`, under-read #5) vs
> `binding_schedule_semantic.py` (`register: value`, found the real signal).

## Prioritization Rule

Audit **load-bearing-first**: a refuted peripheral claim changes nothing;
a verified (or refuted) CRITICAL claim moves the whole program. Next up:
**#1 crystal-is-topological** and **#2 holographic-self-similar** — the two
the compression north-star actually rests on.

## What "done" looks like

A small, hard core of `VERIFIED` claims that the north-star provably stands
on, with every assumption either verified, scoped, or retired — and source
pages carrying honest caveats where the controls bit. Distill ruthlessly;
every kept claim justifies itself.
