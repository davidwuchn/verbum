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

> **Emergent finding (s202→s204):** every audit so far shows the *same shape* —
> the continuous substrate is real, the crisp discrete/localized/universal story
> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict
> where the next claim breaks before building the control).

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

## Status Legend

`VERIFIED` survives its control · `VERIFIED-LOCAL` real but scoped (e.g. one
model) · `PARTIAL` some predictions hold · `REFUTED` fails its control ·
`UNFALSIFIABLE` no control can distinguish it as stated · `UNTESTED` control
named, not yet run.

## Registry

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

**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med)
- Evidence: showcased heads/weights on example sentences.
- Suspected confound: cherry-picked heads/examples.
- Control: does the schedule hold across **many** sentences with a perm-null, or only the showcased ones? Causal ablation of the specific head.

**6. SVD φ-ratio 0.6299** (load: med — a φ-universality pillar)
- Evidence: consecutive singular-value ratio ≈ 1/φ across 5 families.
- Suspected confound: heavy-tailed / power-law spectra generically have near-constant consecutive ratios; 0.618 may be "what power-law spectra look like."
- Control: compare to random-matrix (Marchenko–Pastur) and shuffled-data nets; is 0.6299 model-specific and distinct from the random-matrix prediction?

**7. Crystal-sieve 1.03× PPL (29 layers + continuations)** (load: med — headline compression result)
- Evidence: s196 run = 1.03×.
- Suspected confound: s196 itself noted a rerun gave 3.23× — training-sensitive.
- Control: re-run N seeds, report mean ± variance; is 1.03× robust or a lucky run? (Reproducibility, not novelty.)

**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory)
- Evidence: R²=1.000 all zone pairs (s140).
- Suspected confound: random high-dim linear maps can look rank-1-dominated.
- Control: compare σ₁/σ₂ to random/shuffled linear maps between the same spaces.

**9. Decay α=1.18 (attention log-distance)** (load: low)
- Control: model-specific vs generic positional-encoding artifact; compare to random-init.

**10. Moiré determinism (static program is a fixed point)** (load: low)
- Likely robust (it is a determinism check). Caveat: fingerprints are λ-primed (common-mode confound applies to the *opcode labels*, not the determinism).

**11. GTSM finite-budget weighting — does layer-targeted λ(l) beat uniform α?** (load: med — compression track; positive prediction, not a falsification) — `UNTESTED`
- Evidence: CGTSM Thm 3.2 says the *zero-loss fixed point* is weighting-independent, but Prop F.6 says at **finite budget** the weighting λ(t) is a load-bearing bias that should counter-balance a learner's coarse-first tendency. Our score-matching sieve correction (s198, v3b) uses a single flat α=5.0 across all ~36 layers. See `gtsm-search-space.md`.
- Suspected confound (why it might be null for us): cosine is already scale-invariant (it self-normalizes the 100× standing-wave amplitude), so per-layer reweighting may add nothing beyond what cosine already does — the F.6 benefit assumes an *un*-normalized norm ‖·‖_D. Also our budget may be large enough to be near the fixed point where weighting washes out.
- Control: sweep a **layer-dependent weighting** λ(l) on the v3b SM loss — heavier on the hard binding-prep layers L22–L26 (which v3b leaves at the lowest cosine, 0.80–0.86) vs uniform α=5.0, **matched total training budget + N seeds**. Prediction (if F.6 transfers): targeted λ(l) reaches lower eval PPL / higher worst-layer cosine at equal budget. Null result (cosine already absorbs it) is itself informative — it would mean our metric choice made the weighting moot, sharpening the `‖·‖_D`-proxy claim in `gtsm-search-space.md`.
- Verifies/refutes: the "α=5.0 is load-bearing, not arbitrary" claim now asserted in `gtsm-search-space.md` and `score-matching-compression.md`.

## The Per-Session Loop

```
1. Open this page. Pick the highest-load `UNTESTED` claim.
2. Re-read its evidence in the linked knowledge page.
3. Build the named discriminating control (reuse the method recipe).
4. Run it with a permutation/matched-control null + seed variance.
5. Update the row: status + the number + the result-JSON path.
6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page.
7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).
```

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
