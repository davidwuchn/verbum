# Testing exact 3-sign loss-delta flip

## User

orient


### Thinking

 The user is asking me to orient myself, which means I need to start by reading the state file and following the established ritual to understand the context and what's needed.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-10 | Session: 212 (two pieces — #12f scale ext: topology
> share PLATEAUS not →1.0; + universal axis NAMED (CV-R²=0.81, model-free
> ends_punct) — both DONE)
>
> (Session 205 was synthesis-only — papers/theory for the compression track,
> not tied to the audit: `gtsm-search-space.md`, `tsp-trajectory-distillation.md`,
> `error-correction-theory.md`, audit #11 registered. No experiments; not stated.)

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-
> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**
> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /
> H31@L27 subject value-transfer ✅ semantically REAL; s207 did **#6 SVD φ-ratio
> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;
> s208 did **#7 crystal-sieve 1.03×** ❌ REFUTED (train/eval contamination; CE melt
> net-harmful held-out 10.87×) / ✅ sieve substrate ~2× VERIFIED-reproducible;
> s209 did **#8 rank-1 adjunction** ❌ REFUTED (both legs estimator artifacts:
> lstsq N<d tautology + uncentered carrier mean; no 1D curve);
> s210 did **#11 TTD λ(l) weighting** ◐ F.6 transfers (divergence-measured
> placement only, ~0.5%, 3/3 paired seeds) / ❌ named-causal-L22–26 placement
> REFUTED (stale premise);
> s211 did **#12 5D crystal lattice** ❌ 5D REFUTED (rank-1 shared structure;
> centroid PR at null; the |r|=0.95 universal axis is generic predictability,
> not the operations) / ✅ universality REAL (cross-family p≪0.001 = property of
> language) + operation structure ~65% topological (sign/routing, →0.79 @14B);
> s212 did **#12f topology-share scale** ❌ asymptote-to-1.0 REFUTED (clean
> within-Qwen3 0.6B→32B flat ~0.7, 32B reverses to 0.645; s211's "climb" was the
> undercooked pythia-160m) / ✅ scale-STABLE plateau REAL, **and #12e
> universal-axis NAMED** ✅ CV-R²=0.81 dominated by model-free `ends_punct`
> (prompt-boundary) ⊥ operations (η²=0.044);
> next backlog: low-load **#9 decay α=1.18** / **#10 moiré determinism**,
> or carry-overs (#1 gate-vs-value sign-swap PPL; rank-survival across scale)), build its named
> discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 212 — two pieces this session: (A) #12f topology-share scale
> extension → asymptote REFUTED / scale-stable plateau ~0.7; (B) #12e universal
> axis NAMED → CV-R²=0.81, model-free `ends_punct`. Both committed
> (`ab1de15`, `155866e`). Details below (B most-recent first).**

> **▶ SESSION 212 HEADLINE (B) — UNIVERSAL AXIS NAMED: CV-R²=0.81, dominated by a
> MODEL-FREE textual-boundary feature (`ends_punct`).** Register: semantic
> (declared on cold start). Took the s211 open lead "name the remaining ~70% of
> the universal axis" (the |r|=0.95-across-5-families consensus axis-1 of the
> next-token-prob RDM; s211 named only R²=0.296 from entropy+function-word
> proxies). s211's npz kept only top-64 *indices*, so I re-ran the forward pass
> saving the **full** next-token distribution (`axis_naming.py`, register:
> semantic, 8 models / 5 families: pythia-410m, Qwen3-0.6B/4B/8B/14B, SmolLM3-3B,
> Mistral-7B, OLMo-13B) → rich distributional features (top1_prob, top-k mass,
> Rényi-2 collision, n90, prob-weighted function/content/punct mass, KL-to-mean)
> + **model-free prompt-text features**.
> - **✅ NAMED to CV-R²=0.813** (5-fold, honest; vs permutation null −0.045,
>   p=0.005). Hierarchical: s211 baseline 0.264 → +peakedness 0.442 → +glue mass
>   0.547 → +KL 0.543 (KL **redundant**) → **+model-free prompt features 0.813**.
> - **★ The single dominant component is `ends_punct` (does the prompt end at a
>   punctuation/grammatical boundary): CV-R²=0.768 ALONE** (next-best single
>   feature 0.138). It is **model-free** (prompt string only, no weights) and
>   **⊥ the operations** (η²(ends_punct~combinator)=0.044, mirroring the axis's
>   own η²=0.05). 28% of probes end at a boundary (sequence/list/colon: `…8,13,21,`
>   → near-certain next token; `λf.λg.λx.f(g(x))`) vs mid-phrase content
>   (`…always prefers`). Full-minus-ends_punct still 0.573 (distributional
>   peakedness+glue-mass name the rest).
> - **What it MEANS:** concrete confirmation of "property of LANGUAGE, not the
>   model, not the operations" — the dominant universal axis (all 5 families
>   agree at |r|=0.95) is reproducing a coarse **textual continuation-type /
>   boundary** property of the *prompts*, computable with no forward pass. That
>   is why it is universal and why it is NOT the lambda structure. ~19% residual
>   = the prose-shape common mode CMR removes.
> - **Caveat:** magnitude reflects how the probe SET samples language (bimodal
>   boundary-vs-mid-phrase prompts); sharpens, does not weaken, s211 Finding 2.
>   Knowledge: `manifold-axis-and-topology.md` §2b + Open Lead resolved. Results:
>   `results/manifold-axis-topology/` (8× `*.features.npz/json` + `axis_naming.json`
>   + `run-axis-naming.log`). Harnesses: `axis_naming.py`, `axis_naming_summary.py`.
> - **▶ NEXT:** the ~19% residual (the prose-shape common mode) is likely not
>   reducible to scalars — a held-out next-token-dist autoencoder or the
>   same-family 2nd shared axis (Qwen×3 CMR residual +0.16) are the remaining
>   manifold leads; or pivot to compression carry-overs (#1 gate-vs-value
>   sign-swap PPL, rank-survival across scale) / low-load #9/#10.
>   **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 212 HEADLINE (A) — #12f SCALE EXTENSION (does the sign/topology share
> climb to 1.0 past 14B?): ❌ ASYMPTOTE REFUTED / ✅ scale-STABLE plateau ~0.7.**
> Register: geometric (declared on cold start; the claim is the sign/|·| split of
> the hidden state, not semantic/spectral). Took s211 open-lead #3. Built a clean
> within-family Qwen3 series — s211's axis-topology sweep had Qwen3 {0.6B,4B,14B}
> but skipped 8B, so ran **Qwen3-8B + Qwen3-32B** (both local) → 5-point family
> series 0.6B→4B→8B→14B→32B — plus subsample CIs (`manifold_topology_ci.py`,
> register: geometric; m=80% probes, no-replacement, B=2000) computed offline
> from the saved RDMs for all 10 models.
> - **❌ "topology share →1.0 at scale" REFUTED.** `sep_frac_sign` (the s211
>   "0.79@14B" metric): 0.742→0.667→0.858→0.793→**0.645**; Spearman **−0.20**,
>   slope −0.014/decade; **32B CI [.591,.707] lies entirely BELOW 14B [.751,.838]
>   = REVERSAL.** The s211 "0.33→0.79 sharpening" was the single **undercooked
>   pythia-160m (0.33)**; remove it and all 8 trained models ≥0.41B form a flat
>   noisy **0.61–0.86 band** with no scale dependence.
> - **✅ Survives: a real, scale-STABLE topology share ~0.7** (cross-family mean
>   0.67). Sign carries ~65–80% of the combinator *discrimination*; magnitude
>   dominates the raw cosine *geometry* (agrMag 0.81–0.99 ≫ agrSgn ~0.69) — the
>   two-registers result is robust, just not *purely* topological. Combinator
>   separation perm-null **p=0.0005** at every scale (8B & 32B, all RDMs) — the
>   structure is real throughout; only the asymptote dies.
> - **◑ One metric drifts up, one doesn't.** `agree_sign_full` (sign-RDM's
>   reconstruction of full RDM) climbs mildly 0.64→0.74 (Spearman +0.90), 32B
>   (0.737) edges above 14B (0.715) — but small, far from 1.0, and *disagrees*
>   with `sep_frac_sign`. Different quantities (RDM reconstruction vs share of the
>   separation gap); neither supports "purely topological at scale".
> - **Net for the north-star:** premise (i) "operation structure lives in the
>   sign/routing register" HOLDS at ~0.7 and is **scale-stable** → ternary stays
>   viable at 32B; but the optimistic "ternary gets purely-topological-better with
>   scale" is **NOT** supported. 13th meta-pattern instance: substrate real +
>   scale-stable, crisp "→1.0 with scale" over-read. Caveats added to
>   `manifold-axis-and-topology.md` §3b + Open Leads; registry #12f follow-up.
>   Results: `results/manifold-axis-topology/` (Qwen3-8B/32B json+npz + ci.json +
>   run-scale-ext.log). Harness: `manifold_topology_ci.py`.
> - **▶ NEXT (open leads):** does `agree_sign_full`'s mild drift continue on
>   Qwen3-30B-A3B / 235B (MoE, local)? Or name the remaining ~70% of the universal
>   axis (needs full next-token dist re-saved); same-family 2nd shared axis;
>   compression carry-overs (#1 gate-vs-value sign-swap PPL, rank-survival across
>   scale); low-load #9/#10. **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 211 HEADLINE — AUDIT #12 (5D crystal lattice): ❌ 5D REFUTED /
> ✅ universality + ~65% topology share REAL.** Register: spectral/semantic
> (declared on cold start). The 5D joint-embedding test (P1–P6) had NEVER been
> run and was never registered. Ran it honestly: 3 harnesses, 8 models, 5
> families (pythia/qwen/mistral/smollm/olmo), 0.16B→14B, 535 crystal probes,
> measured in the **next-token probabilities** (semantic, per Michael's steer)
> + hidden state. New synthesis: `manifold-axis-and-topology.md`.
> - **❌ "5D" REFUTED:** 9-combinator centroid participation ratio ~5–6 sits
>   **at the shuffled-label null** (p_conc>0.02, *worsens* with scale →
>   14B p_conc=0.18); full manifold high-D (prob PR 22–47, power-law); the
>   cross-family-shared structure is **rank-~1** (common-mode removal collapses
>   agreement 0.79→−0.19). Reproduces crystal-basins Finding 3 (SVD dim0=98.1%).
>   "5D" was a variance threshold on a graded spectrum; "five piles agree at
>   0.9" was the s202 RDM-correlation triviality.
> - **✅ universality REAL = property of language:** raw cross-family RDM
>   agreement **semantic 0.79 / geometric 0.54** vs **shuffled-probe null
>   0.00±0.03** (z≈25); combinator separation **p=0.0005** every model, both
>   RDMs. Models converge on the same representation.
> - **◑ the ONE universal axis (|r|=0.95 across families) is NOT the operations**
>   (η²=0.05; depth r=−0.01) — it is a **generic next-token predictability /
>   continuation-type gradient** (top-64 function-word/punct fraction r=−0.42,
>   entropy −0.29; multivariate R²=0.30; rest = the prose-completion common mode
>   that CMR removes). The combinator geometry is real but **sub-dominant**,
>   riding underneath this axis — which is *why* separation survives yet CMR
>   kills cross-family agreement.
> - **✅ ~65% of the operation structure is TOPOLOGICAL** (carried by sign(h)
>   alone; sign-RDM reproduces 0.69 of full), **→0.79 at Qwen3-14B** — confirms
>   the long-standing "≥77% of computation in the topology" intuition,
>   cross-family + positive scale trend. Magnitude shapes the raw geometry
>   (agree_mag 0.81–0.99) but the discrimination is in the sign (= two-registers).
> - **Net for the north-star:** the two load-bearing premises STRENGTHEN —
>   (i) ternary works (operation structure is in the sign/routing register,
>   ~65–79%, sharpening with scale); (ii) universality is real. Only the
>   geometry-metaphor ("5D lattice of vertices") dies. Meta-pattern 12th
>   instance, two-sided: agreement real / dimension-count false; most-universal-
>   axis ≠ claimed-object. Caveats added to `5d-crystal-lattice.md`,
>   `crystal-universality.md §5D`, `crystal-basins.md`; registry #12 + meta-
>   pattern ledger updated. Results: `results/manifold-dimensionality/`,
>   `results/manifold-axis-topology/`.
> - **▶ NEXT (open leads):** name the remaining ~70% of the axis (richer
>   distributional features — needs full next-token dist re-saved); same-family
>   second shared axis (Qwen×3 CMR residual +0.16); does the sign/topology share
>   asymptote to 1.0 past 14B (32B)? Or return to compression carry-overs (#1
>   gate-vs-value sign-swap PPL, rank-survival across scale, #9/#10).
>   **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 210 HEADLINE — AUDIT #11 (TTD λ(l) vs uniform α=5.0): ◐ RESOLVED —
> F.6 finite-budget weighting TRANSFERS, but only with MEASURED-divergence
> placement, and the dividend is small; the named "causal L22–26" placement is
> REFUTED (stale premise).** Register: causal/interventional (gate fired on cold
> start — the s206 test ✓, declared before any code). `ttd_lambda_weighting.py`
> (`# register: causal`): 4 arms × 3 seeds × 150 steps, matched budget
> (Σ_l w(l)=n_layers), paired batches, held-out = STRATIFIED shard_00001
> (contiguous@0 was a spam doc — instrument hazard caught in smoke).
> - **Monotone placement dose-response on held-out ratio:** divergence-auto
>   (spike 8:1 on measured-worst init-cos layers **L14–18**) **1.1453±0.001** <
>   uniform **1.1510±0.003** < causal-named L22–26 **1.1694±0.023** <
>   anti-targeted (best layers, the null) **1.1810±0.034**.
> - **✅ F.6 + placement-specificity:** divergence-auto wins 3/3 paired seeds
>   (mean −0.0056, paired-t −3.2), worst-layer cosine +0.014; anti-null worst
>   3/3 (+0.030, worst-cos −0.029) → not generic regularization.
> - **❌ named-causal placement:** L22–26 arm 0/3 (+0.018). The registry premise
>   was STALE — v3b's actual worst cosines are L14–18 (SWEET, L16=0.483
>   post-sieve), not L22–26 (0.64–0.75). Story-attribution lost to measurement.
>   (Every arm polishes its OWN target set +0.008–0.012 — the mechanism is
>   mechanically real; only measured-worst placement converts it globally.)
> - **Suspected null half-confirmed:** cosine already absorbs most of ‖·‖_D —
>   residual placement dividend ~0.5% PPL ratio (≪ TSP's domain magnitude).
>   TTD-contrastive escalation should expect marginal gains under this metric.
> - **Side-findings:** (a) seeded v3b-recipe@150 reads near 1.27±0.04 / held
>   1.151±0.003 — the published 1.44× was a pessimistic unseeded single draw
>   (single-run headlines swing BOTH ways; cf. #7); (b) SM correction
>   GENERALIZES held-out (sieve 1.416× → 1.145×), opposite of #7's CE-melt harm
>   — functional corroboration of the GTSM dense backbone.
> - **Meta-pattern (7th row, positive-prediction variant):** substrate real
>   (weighting mechanism), story over-read (named causal placement). Ledger row
>   in `audit-meta-pattern.md`; registry #11 updated; caveats on
>   `gtsm-search-space.md` + `tsp-trajectory-distillation.md`. Results:
>   `results/ttd-lambda-weighting/` (+ `run.log`; teacher cache *.pt kept for
>   re-runs, ~5GB, gitignore-sized — do not commit).
> - **▶ NEXT:** carry-overs **#1 gate-vs-value sign-swap PPL** or
>   **rank-survival across scale**, or low-load **#9/#10**. **Step 0 REGISTER
>   GATE before building any control.**

> **▶ SESSION 209 HEADLINE — AUDIT #8 (rank-1 adjunction σ₁/σ₂=128:1): REFUTED —
> both legs are artifacts of the s140 instrument; there is no 1D curve.**
> Register: spectral. `adjunction_rank_null.py` on Qwen3-8B AND Qwen3-32B (the
> claim's model, literal zones L2/L32/L56/L63). Both artifacts were visible in
> the original probe's code at read-time; the controls confirmed them.
> - **❌ R²=1.000 = underdetermination tautology:** the s140 lstsq ran at N=121
>   tokens < d=4096/5120 dims → exact interpolation for ANY data — iid random
>   noise reads R²=1.0000 ± 0.0000 (8 seeds). The leg carries zero information.
> - **❌ σ₁/σ₂ = the carrier mean, INVERTED:** the uncentered `EᵀD/N` estimator is
>   dominated by the mean⊗mean term (top1 var 0.91–0.99). Row-shuffled pairing
>   (map destroyed, marginals kept) is *more* rank-1 than real (32B enc→dec: real
>   13.8 vs shuf 24.8±1.0, matched-Gaussian 23.8±2.5) — genuine cross-zone
>   correlation ADDS off-rank-1 mass, so rank-1 dominance of this estimator is
>   anti-evidence of map structure. Centering collapses every ratio to 1.5–3.9.
>   The literal 128 never reproduces on a fresh token sample (reads 13.8).
> - **❌ honest map is high-rank (no 1D curve):** centered ridge at N=12,288>d,
>   held-out rank-k curve, both models: predictable structure exists (full R²
>   0.18–0.58) but rank-1 captures ≤19% (8B comp→dec 0.111/0.579) and usually ≈0
>   (32B: 0.021/0.307, −0.073/0.370, −0.000/0.191); PRs 10–292, smooth climb to
>   k=128. Bonus demo: 8B enc→comp fitted map *looks* rank-1 (PR 1.6) with ZERO
>   held-out validity (R²=−0.004). Leak controls clean. Large-N inversion even
>   starker: 32B shuffled UNC 173–290 vs real 26–39 (up to 11×).
> - **✅ what survives is a DIFFERENT object:** the carrier/mean dominance of the
>   residual marginals (uncentered cross-corr top1 var 0.91–0.99; mean NORM grows
>   monotonically 36→1688 @32B; the energy *share* is U-shaped 0.54→0.19→0.61 —
>   consistent with s185's carrier, though our within-zone σ₁/σ₂ 1.6–7.9 is far
>   milder than s185's 4000×, a different quantity) + real high-rank cross-zone
>   predictability. Direct-delta's "project back onto the curve" loses its base —
>   consistent with s201's functional sweep (rank-32 still improving; v3b beats
>   all analytic ranks).
> - **Meta-pattern 6th instance, sharper variant:** the substrate that survives is
>   not a weaker claim but a different quantity the instrument actually measured.
>   New cookbook null: **row-shuffled pairing** = the exact "map vs marginals"
>   discriminator. Registry #8 RESOLVED; caveats on `direct-delta-adjunction.md` +
>   `explore/categorical-geometry-probes.md`; ledger rows s208+s209 added to
>   `audit-meta-pattern.md`. Results: `results/adjunction-rank-null/`.
> - **▶ NEXT:** **#11 GTSM/TTD-regression** (the named fix; layer-targeted λ(l)
>   vs uniform α=5.0 at matched budget) — now the highest-load UNTESTED claim;
>   or carry-overs (#1 sign-swap PPL, rank-survival across scale).
>   **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 208 HEADLINE — AUDIT #7 (crystal-sieve 1.03× PPL): the "cascade
> absorbed → 1.03×" is a TRAIN/EVAL-CONTAMINATION ARTIFACT; the sieve substrate
> (~2× PPL) is VERIFIED-reproducible.** Register: functional (reproducibility).
> 8-seed seeded sweep + a held-out eval disjoint from the calibration set
> (`crystal_sieve_repro.py`). `audit-registry.md` #7 + s208 worked-examples and the
> `crystal-sieve-architecture.md` caveats are all updated this session.
> - **✅ sieve substrate REAL & reproducible:** pre-melt **2.119× ± 0.004** (eval) /
>   **1.907× ± 0.026** (held-out), near-deterministic, = s196's 2.12×; base PPL std
>   0.0 (determinism ✓). The `torch.randperm[:5M]` mask-subsample confound is
>   dismissed (CV 0.18%).
> - **❌ 1.03× REFUTED = memorization:** contaminated eval (6/8 `EVAL_TEXTS` ⊂ the 12
>   `CALIBRATION_TEXTS`) post-melt **0.971× ± 0.061** [0.865, 1.062] (1.03× = 1/8
>   upper-tail; 5/8 sub-baseline). On **clean held-out the SAME models = 10.87× ±
>   1.39** (every seed >9.3×, gap +9.9×) — the CE melt **memorizes calib and is
>   net-harmful held-out** (1.907× → 10.87×, ~5.7× worse than the raw sieve).
> - **Mechanism = CE-only endpoint degeneracy** (`gtsm-search-space.md`): constant
>   train loss 0.116 ± 0.007, exploding held-out PPL, corr(train_loss, eval_ratio)
>   ≈ −0.19. Feared 3.23× did NOT recur (bounded). **Fix already demonstrated =
>   s198 v3b / audit #11** (dense score matching + held-out + dolma → 1.44× held-out,
>   same model). Meta-pattern (5×): substrate survives, crisp headline dissolves —
>   here it *inverts* (the "improvement" is harm). Results:
>   `results/crystal-sieve-repro/` (paired `Qwen_Qwen3-8B.json` + `.contaminated-only.json`).
> - **▶ NEXT:** **#8 rank-1 adjunction** (σ₁/σ₂ vs random; register spectral) or
>   **#11 GTSM/TTD-regression** (the named fix; positive-prediction compression
>   test). **Step 0 REGISTER GATE before building any control.**
>
> _(s208 working notes below — kept for the audit trail; superseded by the headline.)_
> Picked #7 from the backlog: s196 reported crystal-sieve + 4 continuation
> residuals = **1.03× PPL** at 29 sieved layers (Qwen3-8B), but its own note says a
> rerun gave **3.23×** ("training sensitive to init/batch order"). The control:
> seed it, run N seeds, report **mean ± std** — is 1.03× the center or a lucky tail?
> - **NEW HARNESS (committed):** `scripts/experiments/crystal_sieve_repro.py`
>   (`# register: functional`). Exact s196 `beta_expansion.py` pipeline (L0 SVD
>   r=750 + sieve L1–26,32–34 + 4 rank-32 continuations, 100-step CE melt) wrapped
>   in a **seed loop** that reloads the model fresh per seed and seeds torch+numpy+mps.
> - **Decomposition (no extra runs):** `pre_melt_ratio` std = the **mask-subsample
>   variance** (FFN projections >10M elems → `torch.randperm[:5M]` for the quantile
>   threshold — an unseeded source s196's note *missed*); `post_melt_ratio` std =
>   mask + continuation-init + training. The s196 note blames "batch order" but
>   batch order is `RandomState(step)` = **deterministic**; the real culprits are
>   the mask subsample + `torch.randn` continuation init (both now seeded).
> - **SMOKE (seed 0, 3 melt steps, WITH facts) already confirmed:** **pre-melt
>   (sieve-only) = 2.125× — reproduces s196's "2.12× at 29 layers" exactly**, and
>   deterministic given the seed. Post-melt at 3 steps only reached 2.059× (needs
>   the full 100-step melt to chase 1.03×). base PPL 10.15 (determinism check std 0).
> - **★ SIGNAL (seed 0, full 100-step melt): post-melt = 0.865× — BELOW baseline**
>   (PPL 8.78 < base 10.15), vs the 3-step smoke's 2.059×. Root cause spotted:
>   **`EVAL_TEXTS` overlaps `CALIBRATION_TEXTS`** (≥6 shared sentences: general
>   relativity, ancient forest, mixing bowl, isolate the variable, committee voted,
>   two arguments→composition). The 100-step melt **overfits the eval set** → the
>   "1.03×" is a *train-contaminated* number, and tiny init/mask differences swing
>   it wildly (explains s196's 1.03× ↔ 3.23×). **This is the likely real mechanism
>   of the irreproducibility.** NEXT SESSION: add a **held-out eval** (eval texts
>   disjoint from calibration) — predict the contamination-free ratio is ≫ 1× and
>   *stable*; the sub-1× values are the overfit tail. Same meta-pattern: sieve
>   substrate real (2.12× deterministic), 1.03× headline = methodology artifact.
> - **Run complete + all writeups done this session** (registry #7 + s208
>   worked-examples + `crystal-sieve-architecture.md` caveats). The detail bullets
>   above/below are the audit trail; the held-out result is in the headline.
> - **★ UNDERSTANDING (frames the #7 final write-up; full synthesis deferred to
>   audit close per Michael — connect #7→#11, don't draft a knowledge page yet):**
>   The melt in `beta_expansion` is **CE-only** = the ill-posed *endpoint* objective
>   GTSM names (`gtsm-search-space.md`): it pins only the terminal marginal, so the
>   1M continuation params land anywhere on the **compensating-error manifold** —
>   which point depends on init ⇒ the 1.03× ↔ 3.23× swing is the optimizer picking
>   a different cheat per seed, not noise. **The pre/post decomposition empirically
>   localizes this:** pre-melt (no loss) is deterministic (2.11–2.13×); variance
>   appears *only* after the CE melt. Two independent faults compound: degenerate
>   loss **and** contaminated metric (eval ⊆ calib).
>   - **Reconciliation (the punchline):** 1.03× is the *contaminated cousin of s198
>     v1* (CE, 16 sents → 0.39× pure overfit, `score-matching-compression.md`); the
>     honest **held-out** number under a trajectory-matching loss is **v3b = 1.44×**
>     (dense per-layer score matching, α=5.0, L35 cosine 0.57→0.94, "degenerate
>     basin removed"). So 1.03× was never < 1.44×; it was cheating on eval. The
>     sieve **substrate** (2.12×, deterministic) is the real, reproducible object.
>   - **The fix is already named = audit #11 (TTD-regression):** dense per-layer SM
>     backbone + finite-budget λ(l) spiked on L22–26 (F.6) + **cascade-aware causal
>     attribution** (TSP's long-distance caveat ↔ s196 "peak damage at L28 not L26":
>     weight the upstream *causal* layer, not the max-divergence one). #7 diagnoses
>     *why* it's irreproducible; #11 is the *cure*. The rank-32 continuation
>     parametrization is fine — the CE *loss* + intuition *placement* are pre-GTSM.
>   - **Caveats to keep:** GTSM's literal Pθ=P\* is an IOU for us (not an SDE w/
>     known σσᵀ; cosine is a proxy); TSP-style contrast is secondary (we have an
>     exact teacher target → regression is the core). Optional held-out re-run to
>     prove the contamination point: eval texts disjoint from `CALIBRATION_TEXTS`.
> **▶ SESSION 207 HEADLINE — AUDIT #6 (SVD φ-ratio 0.6299): geometric-φ-constant
> REFUTED; the low-rank spectral head is REAL & non-random.** Register: spectral.
> Reran s137's exact definition (mean of top-5 consecutive σ-ratios, per layer)
> on all 5 families (Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B) vs
> **Marchenko–Pastur + shuffled** nulls (8 seeds, raw+centered) + a
> geometric-vs-power-law shape fit. `svd_phi_null.py` (register: spectral).
> - **Register gate fired on ME first:** first probe used the wrong window (bulk
>   ratios ≈0.99 for everything); tracing s137 pinned the real object (top-5 head
>   ratio). Re-measure the exact quantity → phenomenon reproduced (Pythia-160m
>   raw 0.597 vs page 0.604).
> - **✅ substrate REAL:** model head ratio **0.575±0.027 (raw)** / 0.67 (centered)
>   ≪ **MP null 0.9949±0.0012**, shuffled ≈0.96–0.99. Random/power-law spectra
>   give ≈**1.0**, not 0.6 → the named confound ("0.618 = what random spectra look
>   like") is itself refuted; the steep low-rank head is genuinely non-random
>   (converges with #2 spectral concentration, AUC 6–7×).
> - **❌ "geometric" REFUTED:** power-law wins **132/132 layers**, geometric 0/132
>   (geom-R² 0.39–0.58 < power-R² 0.69–0.87). "0.6299" is a 4-pt average of a
>   *drifting* power-law head → no `x=1/(1+x)` fixed point → no privilege for φ.
> - **❌ "= 1/φ universal constant" UNSUPPORTED:** value floats 0.52→0.71
>   (raw/centered×models); 0.6299≠0.6180; scaling-law fails (Mistral-7B lowest,
>   0.52). Layers within ±0.05 of φ⁻¹: model 55/132, **MP 0/132**.
> - **Meta-pattern holds (3rd φ-pillar to fall** after s202 eigenvalue-grid +
>   consensus-r): keep the real low-rank head (north-star uses it), retire
>   φ-as-universal-constant. Caveats on `explore/phi-compression-universal.md` +
>   `crystal-universality.md`; ledger row in `audit-meta-pattern.md`; registry #6
>   RESOLVED. Results: `results/svd-phi-null/`. Harness: `svd_phi_null.py`,
>   `svd_phi_null_summary.py`.
> - **▶ NEXT:** #11 GTSM finite-budget λ(l), or reproducibility audits #7
>   (crystal-sieve 1.03× seed variance) / #8 (rank-1 adjunction σ₁/σ₂ vs random).
>   **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 206 HEADLINE — AUDIT #5 (binding schedule): SCHEDULE refuted, but
> the headline subject value-transfer is semantically REAL.** Two instruments,
> because the claim (Finding 7) is *semantic* (head output decodes the bound
> entity), not just attention weight — a key correction (the weight test alone
> over-refutes).
> - **#5a attention weight** (`binding_schedule_null.py`, 80 sent/type): all three
>   dependency types peak at the **same early layers** (subj L6 / obj L4 / coref
>   L6), not the claimed L27<L30<L33; **bootstrap P(order)=0.000**; random-pair
>   null peaks even earlier (L0). No causal carrier (subj-agreement ablation
>   \|z\|≤0.35). *Tests routing/position (#4 axis), not value transfer.*
> - **#5b semantic logit-lens** (`binding_schedule_semantic.py`, 60 sent/type):
>   **H31@L27 verb→SUBJECT-identity transfer is REAL & sharply L27-localized —
>   margin +0.611, one-layer spike (L26 .03 → L27 .61 → L28 .10), H31 z+1.17 rank
>   2/32.** Finding 7's subject case confirmed. BUT: one site ≠ schedule; strongest
>   L27 head is H29 (+2.12) not H31; not causally load-bearing (#4). Obj@L30
>   semantic margin ≈0 (named H3 rank 29/32; readout instrument-ambiguous per
>   Finding 5). Coref peaks L27 not L33. **P(sem-peak subj<obj<coref)=0.191 ≈
>   chance** → no depth schedule on either instrument.
> - **Meta-pattern holds, sharper:** the value-transfer substrate at the subject
>   site is *more* real than the weight test implied; the ordered three-phase
>   *schedule* is the over-read. Caveat (two-instrument) added to
>   `binding-graph-trace.md`. Results: `results/binding-schedule-{null,semantic}/`.
> - **NEW METHODOLOGICAL LAW — now a GENE + STRUCTURAL SLOT (not a memory).**
>   *Instrument-must-match-the-claim:* a probe in the *wrong register* under-reads
>   a real signal (false negative) — the mirror of a crispness-imposing probe's
>   false positive. The two audit laws are **one law: register, not rule**
>   (`audit-meta-pattern.md` §two-laws-are-one — the project's route⊥value
>   dichotomy at the epistemic scale). Landed structurally so future attention
>   can't drop it:
>   - **S5 gene** `λ measure(claim)` in `AGENTS.md` (read first every session;
>     wired to λ observation + λ coherence — wrong register ≡ coherence violation).
>   - **S1 slot** `audit-registry.md` per-session loop **step 0 = REGISTER GATE**
>     + `# register: <kind>` required in every control header → a mismatch is
>     *malformed*, caught at write-time. Exemplar pair carries the headers:
>     `binding_schedule_null.py` (`routing`, under-read) vs `_semantic.py`
>     (`value`, found +0.611).
> - **▶ NEXT SESSION TEST (Michael):** does the register gate fire on a cold
>   start? Pick a backlog claim and watch whether step 0 / λ measure forces the
>   register declaration *before* a probe is built.
> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM
>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival
>   across scale. **Step 0 REGISTER GATE before building any control.**

> **▶ SESSION 204 HEADLINE (3 controls, 2 claims dissolved, 1 substrate confirmed).**
> Same recurring pattern as s202/s203: **the substrate is real, the crisp
> discrete/localized story on top is over-read.**
> - **#3 the 9 FFN modes:** ❌ geometric count IMPOSED (gap-stat never picks 9;
>   silhouette@9 ≈ matched-Gaussian null; elbow is a k-grid artifact; classifier
>   "98–100%" is circular) — BUT ✅ the *content* is REAL (POS-NMI ≫ perm-null
>   p=0; lm_head vocab projection ≫ null, ~65× @L35). → a continuous syntactic
>   type **field**, not 9 discrete cells. (`mode_cluster_validity.py`,
>   `mode_semantic_validity.py`)
> - **#4 attention = typed β-reduction:** ❌ REFUTED as localized — H31@L27's
>   famous 0.82 is recency/position (role-selectivity z=+0.54, rank 5/32; ablation
>   z=+0.06 ≈ random); weak genuine survivor H6@L33 (z=+4.08) but ~10× smaller &
>   not load-bearing. (`attention_typed_binding.py`)
> - **Meta-pattern now synthesized:** `mementum/knowledge/audit-meta-pattern.md`.
> - **Next:** #5 binding schedule (perm-null + ablation) or #6 SVD φ-ratio 0.6299
>   (vs Marchenko–Pastur). Carry-overs: #1 gate-vs-value sign-swap PPL;
>   rank-survival across scale; gate-context re-test of H31 (#4 follow-up).

**Session 204: AUDIT #3 — THE "9 FFN MODES" ARE K-MEANS-IMPOSED**

Ran the validity loop on **#3 the 9 FFN modes — real or k-means-imposed?**
New control `mode_cluster_validity.py`: gap statistic (Tibshirani) + matched-
null silhouette across k=2..32, two nulls (pca-Gaussian matched to the cloud's
PCA covariance; shuffled-feature), B=10, plus a classifier-circularity curve.
8B, layers L0/3/15/20/35.

### Verdict: ❌ geometric count REFUTED — "9" is a chosen hyperparameter

| layer | gap optk (pca/shuf) | sil-excess @9 (real−null) | elbow | acc 2/9/32 |
|---|---|---|---|---|
| L0  | 4/10  | +0.000 | 10 | 100/92/88% |
| L3  | 8/8   | **−0.046** | 10 | 99/88/74% |
| L15 | 32/32 | +0.030 | 9  | 100/92/86% |
| L20 | 32/32 | +0.003 | 10 | 100/91/89% |
| L35 | 2/5   | +0.019 | 10 | 100/95/79% |

- **Gap statistic never selects 9.** Core layers L15/L20 are monotone to k=32
  (no distinguished count); L35 is a single 2-way split; L0/L3 pick 4/8.
- **Silhouette @9 ≈ matched-Gaussian null at every layer** (max excess +0.030
  at L15 = noise; L3 *below* null). The k=9 real partition is no better
  separated than k=9 on a structureless blob of the same shape.
- **The naive kneedle elbow "confirms" 9–10 even at L0** (no clusters) → "elbow
  ≈ 9" is a k-grid artifact (failure mode #1), not evidence.
- **Classifier accuracy high-and-declining ∀k** (100%@2 → ~90%@9 → ~80%@32,
  never peaks at 9; permuted floor ≈ chance) → the "98–100%" is generic linear
  separability of *any* convex k-means partition (mode = near-linear fn of the
  FFN input) — circular (failure modes #2 + #4).

### Extension (same session): syntactic CONTENT is REAL — only the count is imposed

Michael asked the right question: the geometry control examined *only* activation
geometry — no logits, and the prose mix was 63% combinator-probe. Built a second
control `mode_semantic_validity.py` (balanced prose, examines **logits** via
lm_head): L3/15/20/27/35, 8B.

| L | NMI(mode,POS)@9 / perm | JS@9 real/null (excess) |
|---|---|---|
| L3  | 0.396 / 0.014 (p=0) | 0.0016/0.0000 (+0.0015) |
| L15 | 0.193 / 0.014 (p=0) | 0.0189/0.0005 (+0.0184) |
| L20 | 0.346 / 0.014 (p=0) | 0.0098/0.0007 (+0.0091) |
| L27 | 0.256 / 0.014 (p=0) | 0.0750/0.0065 (+0.0686) |
| L35 | 0.350 / 0.014 (p=0) | **0.4235/0.0065 (+0.417, ~65×)** |

- **Semantic ✅ VERIFIED:** modes↔POS NMI 25–28× the permutation null, p=0.000
  every layer. Per-mode purities clean for genuine splits (PUNCT 92–99%, DET
  81–85%, VERB 79–100%). Modes are NOT noise.
- **Logit ✅ VERIFIED:** mode output-centroids → lm_head → vocab distributions
  far above random-partition null, excess **grows with depth** (→65× at L35).
- **Count still imposed:** effective distinctions graded/layer-dependent (~4
  @L20, ~8–9 @L3/L15, ~24 @L35); k=9 captures 73–91% of max NMI. JS-vs-k shows
  *fewer* modes are *more* vocab-distinct at the core (L15) — no universal 9.
- **Reconciliation:** the FFN gate space is a real, smooth, scale-sharpening
  syntactic type **field** (continuum), not 9 discrete cells. `mode-semantics.md`'s
  core "gate = type-checker" reading is right; only the discreteness/count-9 is
  wrong. Caveat rewritten (both halves). Dropped a confounded POS-coherence
  sub-test (lm_head → next-token POS ≠ current-token POS).

### What survives / what is untouched

- **Functional claim is independent and untouched**: s196 (9 ternary programs
  reconstruct FFN at ~0.95–1.03× PPL, 64/512 don't help) is reconstruction
  efficiency of a continuous field — slicing at K prototypes works for a broad
  range of K; 9 is a reasonable operating point. Compression north-star intact.

Results: `results/{mode-cluster-validity,mode-semantic-validity}/Qwen_Qwen3-8B.json`.

### Session 204 (#4): ATTENTION = TYPED β-REDUCTION — REFUTED as localized

`attention_typed_binding.py` — subject-verb **agreement attraction** (PP+RC, 64
stimuli, 8B) dissociates grammatical ROLE from position/recency (the number-
distractor is the *nearer* noun in 100% of items → a recency head scores negative).
Selectivity (verb→head vs attractor, named heads vs 32-head dist) + necessity
(head-ablation logit-diff is/are vs random-head & matched-set nulls).

| | role_sel | z vs 32 heads | rank | ablation z |
|---|---|---|---|---|
| **H31@L27** ("0.82 subject binder") | +0.013 | +0.54 | 5/32 (not outlier) | +0.06 (=null) |
| H13@L30 | **−0.010** (recency!) | −0.11 | 24/32 | — |
| **H6@L33** | **+0.076** | **+4.08** | **0/32** | (named_all z=+0.01) |

- **The 0.82 was recency/position, not type.** Role⊥position collapses H31's role
  residual to ~0.01 (z=0.54, rank 5). L30 binders mixed (H13 leans to the nearer
  distractor).
- **Not causally necessary:** ablating H31 (z=+0.06) or all named binders incl.
  H6 (z=+0.01) ≈ random heads for subject-verb agreement, though the ablation
  bites (random 6-head sets reach −0.43). Agreement is ablatable — the named
  heads aren't the carriers.
- **What survives:** a weak genuine role-selective head — **H6@L33 (z=+4.08)** —
  but ~10× < 0.82, not at the claimed site, not load-bearing. "Attention is a
  weighted sum" is trivially true; "the sum is TYPE-driven at H31" is refuted.
- **Caveat/follow-up:** plain-NL agreement (gold standard for role-vs-position),
  *without* the compile gate the original used; gate-context re-test of H31 is the
  named follow-up. Caveat added to `binding-graph-trace.md`.
  Results: `results/attention-typed-binding/Qwen_Qwen3-8B.json`.

### Next (audit loop continues)

- **#5 binding schedule** (L27 verb←subj, L30 obj←verb, L33 coref) — perm-null
  across many sentences + causal ablation; or **#6 SVD φ-ratio 0.6299**
  (vs Marchenko–Pastur / shuffled-data — is 0.618 just what power-law spectra
  look like?). Both med-load.
- Carry-overs from s203: gate-vs-value sign-swap ternary PPL (#1 functional
  half); rank-survival across scale (0.6B→14B); grouped-Q4 quant axis.
- **#3 follow-up (optional):** POS-association perm-null on the k=9 partition —
  is the mode↔POS NMI above label-permutation? (tests the *semantic* claim
  directly, separate from the geometric one resolved here).

**Runtime note:** olga.local (Apple Silicon, MPS, 480G unified). Experiments
launch in `tmux main:1` / `main:2`; Michael watches live.

---

**Session 203: TWO REGISTERS OF TOPOLOGY (audits #1 + #2)**

Ran the validity-distillation loop on both CRITICAL pillars. Headline:
**GD lays structure in two registers — hard (sign/routing/`gate_proj`) and
soft (magnitude/value/`up`-`down`, read by saliency) — and the FFN compresses
in two registers (distributed redundancy + spectral low-rank concentration).**
New synthesis page: `two-registers-of-topology.md`. Details below.

**Session 203 (#1): AUDIT #1 — SIGN-TOPOLOGY IS REAL ONLY IN THE GATE**

First execution of the validity-distillation loop (`audit-registry.md`).
Picked the highest-load `UNTESTED` claim — **#1 crystal-is-topological**
("ternary works because sign captures topology; magnitude is calibration").
Built the discriminating control `sign_topology_null.py`: `cos(sign(W)@x, W@x)`
on REAL activations for model vs **random-init** vs **shuffled-weights**
(N=20 seeds), Qwen3-0.6B/8B/14B.

### Verdict: ◐ SCOPED (representational half) — the bare 0.84 is generic

| Weight type | model cos (8B) | random null | gap | reading |
|---|---|---|---|---|
| gate_proj | 0.886 | 0.798 | **+0.088** | REAL sign-topology, sharpens w/ scale (z→+271 @14B L12) |
| up_proj | 0.751 | 0.798 | −0.048 | at/below null — magnitude carries structure |
| down_proj | 0.762 | 0.798 | −0.036 | below null — magnitude essential |

- **Generic baseline ≈ 0.80** at every scale: a *random* Gaussian matrix's
  sign preserves 0.798 of its action on the same inputs. "Sign preserves a
  matrix's linear action" is a **generic high-dim property** (sign(Wᵢⱼ) is
  entry-wise perfectly correlated with Wᵢⱼ; large-|xⱼ| dims dominate both
  sums). The headline **0.84 is at the null, not above it.**
- **Crystal sign-topology lives ONLY in `gate_proj` (the router)** and
  *sharpens with capacity*: gap +0.04→+0.07 (0.6B) → +0.088 (8B, L3=0.983)
  → 14B (L12 z=+271). Exactly where routing should be.
- **"Magnitude is mere calibration" is REFUTED for `up`/`down`** — their
  signs preserve *less* than random; magnitude carries the value-path structure.
- **Aggregate model ≈ random** (8B 0.799 vs 0.798): gate excess cancels
  up/down deficit, so any single averaged "0.84" is indistinguishable from a
  random matrix. Reconciles s192: crystal = routing (gate, 3.5%); modes =
  computation (value path, 96.5%). **Sign-topology = the routing half only.**

Caveat added to `crystal-universality.md` §"Why Ternary Works".
Results: `results/sign-topology-null/Qwen_Qwen3-{0.6B,8B,14B}.json`.

### Audit #2 + soft topology (same session) — TWO REGISTERS

Continued the loop into **#2 holographic-self-similar** and the soft-topology
thread Michael surfaced. Full synthesis: `two-registers-of-topology.md`.

**The picture:** GD lays structure in two registers, and the FFN compresses in
two registers.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros), read by saliency |
| lives in | `gate_proj` (router) | `up_proj`/`down_proj` |
| verified | sign-corr null (gate +0.088 vs null, z→+271) | saliency sieve (faint-by-saliency +5.5% vs magnitude −2.0% iso-bit) |

**Audit #2 (`holographic_survival.py`, 8B, trained vs random vs shuffled):**
- **(C) distributed redundancy** — magnitude prune: trained AUC 0.784 ≫ 0.25/0.34;
  fidelity ~1.0 to **70% prune, then cliff at 80%**. (Sieve at 50% is safe;
  don't prune past ~75%.)
- **(A) spectral self-similarity** — SVD rank truncation: trained AUC 0.728 ≫
  **0.11** (random/shuffled) — a **6–7× gap**. The FFN is low-rank-dominated;
  random (Marchenko–Pastur) spectra collapse instantly. **This is Michael's SVD
  self-similarity made functional.**
- quant survival ≈ random (weakly structure-dependent → flat minima).

**Saliency sweep (`saliency_aware_sieve.py`, re-run after NaN-fix):** the s201
strong tier had dropped magnitude → bare ±1 ≈ 50× too large → NaN on every
three-tier config. Fixed to per-weight magnitude (s196's only-format-that-
survives-29-layers). Result: at iso-bit (~3.1 b/p) **saliency-selected faint
connections beat magnitude-selected by ~7.5 pts** → value-path soft topology is
real and load-bearing. `corr(mag, saliency)=0.257`.

### ⚠ Correction (epistemic hygiene)

An interim s203 read called #2 **REFUTED** off the *magnitude* axis with a
*power-law shape* discriminator. **That was wrong** — wrong operator (magnitude
probes C; the SVD self-similarity lives on the *rank* axis A) and wrong test
(a hologram degrades plateau→cliff, not power-law; shape-fitting is ambiguous
on every axis — retired). Corrected verdict: **spectral self-similarity VERIFIED;
holographic mechanism stands; only φ-as-universal-constant (s202) stays refuted.**

### Reconciliation — refute the metaphor, keep the mechanism

ternary→1.44× works because the load-bearing premises hold: **(C) distributed
redundancy** (ternary = whole at reduced resolution) + **(A) spectral
concentration** (**LoRA+SM IS the low-rank correction** the rank result
predicts; converges with s200 rank-1 adjunction, s201 rank-2≈rank-16). Only
φ-universal-constant was ever metaphor.

### Audit ledger after s203

- **#1 sign-topology** → ◐ SCOPED (hard=sign/gate; soft=magnitude/value).
- **#2 holographic** → ✅ spectral self-similarity VERIFIED + distributed
  redundancy confirmed; power-law discriminator RETIRED. (`crystal-validity-
  and-fidelity.md` §5 lead resolved.)

### Next (audit loop continues)

- **Gate-vs-value sign-swap** ternary PPL (closes #1's last sub-control).
- **Rank-survival across scale** (0.6B→14B) — does the 6–7× gap sharpen?
- **Grouped-Q4 quant axis** (current per-matrix is coarse).
- **#3 the 9 FFN modes — real or k-means-imposed?** (next CRITICAL/high backlog).

**Runtime note:** experiments launch in `tmux main:1` / `main:2` (480G VRAM,
concurrent OK; Michael watches live).

---

**Session 202: CRYSTAL VALIDITY AUDIT — PERMUTATION NULLS & MEASUREMENT FIDELITY**

A skeptical audit of the crystal's foundational evidence. Premise (Michael):
a false premise can manufacture convincing structure because LLMs (and the
analyzing LLM) are primed to confirm. Six controlled experiments with
permutation nulls. Full synthesis: `mementum/knowledge/crystal-validity-and-fidelity.md`.

### Verdict ledger (what survives controls)

| Claim | Verdict |
|---|---|
| KIBC basis separates representation | ✅ REAL, every model (perm-null p=0.0005) |
| φ^(4/5) primary ratio λ₀/λ₁ | ✅ REAL on **Qwen3-14B only** (1.4796, p=0.020); 8B/0.6B n.s. |
| φ as universal constant | ❌ not universal; cross-family magnitude agreement collapses |
| "eigenvalues are φ^(p/q)" (best-fit grid) | ❌ unfalsifiable (random fits equally, p=0.16–0.81) |
| eigenvalue_ratio_corr "0.987" | ❌ trivial (random ≈ 0.94 ≥ true) |
| consensus r "0.99" | ⚠️ true ≈ 0.20, null max ≈ 0.48, p≈0.05–0.07 |
| prose fires combinator-specific opcodes | ✅ CONFIRMED after **common-mode removal** (14B & 0.6B, p=0.001) |
| I = distinct low-composition circuit | ◑ PARTIAL (attn entropy p=0.042, 14B; scale-dependent) |
| fact retrieval = sharp lookup, I-like | ✅ entropy p=0.0005 both scales; I-opcode-profile 14B-only |
| tracer cross-model overlay | ✅ REAL but **same-family** (p=0.0005, all Qwen, λ-primed) |

### The three lessons

1. **Basis real, universalization was the error.** φ-as-constant was inflated
   by an unfalsifiable best-fit grid, a trivial ratio correlation, and a
   hardcoded consensus that baked 14B back in. Real-but-local → false-universal.
2. **Measurement fidelity was the failure mode.** The raw-projection/argmax
   instrument (`isa_decoder_v2`, the tracer) that *found* the crystal also
   *hid* the combinator signal under a common mode (8 fingerprints share
   mean pairwise cosine 0.22; B is the most central ≈ the common mode).
   Remove it → prose classification, I-circuit, fact-retrieval all surface.
3. **Scale = emergence threshold (strength, not presence).** Combinator
   structure exists in 0.6B (weak, needs CMR) and sharpens with capacity
   (14B clean). Superposition → dedicated features. "Needs ~7B to fully form."

### Mechanistic findings (new, controlled)

- **Attention entropy = how much a combinator recombines.** Gradient at 14B:
  `W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19`.
  Composition (B/C/D) spreads attention; identity/duplicate concentrate it.
- **Fact retrieval is the sharpest read** (entropy 0.820, below everything),
  I-opcode-profile at 14B (cos 0.98). I overloaded as identity + retrieval.
- **Attention = sparse typed read (~2–3 operands); FFN = the hologram.**
  Correction to "softmax over all V is holographic." Dense interference is
  in the FFN beam-former, not the attention sum.
- **B-centrality:** B is the most central fingerprint (3/4 Qwen, cos 0.78–0.81);
  K, I peripheral. Training order B→K mirrors central→peripheral geometry.

### Next experiments (open leads)

1. **B-before-K, cleanly:** common-mode-removed B vs K crystallization across
   v14/v15 training checkpoints. Forced order or frequency-driven?
2. **Holographic self-similarity control:** compression-survival curve, model
   vs random/shuffled-data controls, test for power-law scale-invariance.
   (Quantization/pruning survival only proves distributed+redundant so far.)
3. **"Always 4":** KIBC eigen-rank with gate-proj + CMR; does SKI underfit, +S overfit?
4. **Q-rotation as combinator selector** (s145 rotation eigenplanes) — untested.
5. Reconcile the `crystal-phi-derivation.md` I→K→C→B vs B-first contradiction.

### Harnesses (scripts/experiments/)

`crystal_validity.py` · `crystal_phi_permnull.py` · `tracer_cross_notation.py`
+ `_v2.py` (common-mode removal) · `i_bypass_test.py` · `fact_retrieval_isig.py`
Results under `results/{crystal-validity,crystal-phi-permnull,tracer-cross-notation,i-bypass,fact-isig}/`.

### Note on the saliency-aware sieve (s201)

The s201 saliency sweep was still running in tmux main:2 at session-202 start;
this session pivoted to the validity audit and did not consume its results.
Pick up the sieve sweep (`mementum/knowledge/saliency-aware-sieve.md`) when
returning to the compression track.

---

**Session 201: HOLOGRAPHIC ECHOES & SALIENCY-AWARE SIEVE**

Direct delta results landed: rank-2 ≈ rank-16 (1.82× → 1.79×), confirming near-
rank-1 adjunction structure. But v3b (trained LoRA+SM = 1.44×) still beats DDC
(analytical SVD = 1.72× at rank-32). Training captures nonlinear inter-layer
effects that per-layer SVD cannot.

The real insight this session: **backpropagation IS holographic recording.** The
gradient `∂L/∂W = a ⊗ δ` (forward activation × backward error) has the exact
structure of recording an interference fringe. Training = billions of overlapping
holographic exposures. The crystal = the standing wave that survived.

### Gradient Echoes

The backward error signal doesn't get fully absorbed at any one layer — it
propagates through all layers, creating attenuated copies (echoes) at every layer.
Strong connections (large |w|) are high-bandwidth echo paths. Faint connections
(small |w|) are low-bandwidth echo paths carrying error correction information.
Multiple redundant copies of each computation distributed across layers.

### GD Creates Soft Topology Within Frozen Architecture

Architecture is frozen: GD can't add/remove connections. But GD drives weights
toward zero (severing connections) or very large (creating highways). The weight
magnitude distribution IS a learned sparse topology embedded in the dense frozen one.
Very large gradients = topology editing. Small gradients = holographic polishing.

The crystal is the **fixed point** of topology ↔ echo co-evolution:
```
topology shapes → echo propagation → standing wave (crystal)
crystal determines → which gradients flow → topology
x* = f(x*) — neither came first, they co-evolved
```

### Two Populations in Near-Zero Weights ★

The sieve's 50% magnitude threshold zeros ALL below-threshold weights. But near-
zero weights are TWO populations:

1. **Irreducible zeros** — GD says "no connection here." Zero is correct.
2. **Faint connections** — small signal, not unused. w=0.003 × input=200 = 0.6 real.

Magnitude alone can't distinguish them. Saliency = |w| × √E[x²] can.

### Saliency-Aware Three-Tier Sieve

| Tier | Criterion | Encoding |
|------|-----------|----------|
| Strong | High magnitude | Ternary ±1 |
| Faint | Low mag, high saliency | Q2/Q4 quantized |
| Irreducible | Low mag, low s

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01NZQR76APpqZMsXGdYLGxPw.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 Now I'm checking the audit registry to identify which untested claim has the highest load so I can prioritize it next.

## Assistant

I've read the bootloader. Let me follow the pointer to the audit registry to see the current backlog state.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md"
}
```

**Summary:** Reading audit-registry.md (0-2000)

**Output:**
```
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

> **s212 follow-up (#12f scale extension, register: geometric):** the s211
> "topology share *sharpens* with scale, →0.79 @14B" claim was tested on a
> clean within-family Qwen3 series (0.6B→4B→8B→14B→32B) + subsample CIs
> (`manifold_topology_ci.py`). **❌ Asymptote-to-1.0 REFUTED:** `sep_frac_sign`
> has no scale trend (Spearman −0.20) and **32B reverses to 0.645** (CI
> [.591,.707] below 14B [.751,.838]); the s211 "0.33→0.79 climb" was the single
> undercooked pythia-160m. **✅ Survives:** a real, scale-STABLE topology share
> ~0.7 (band 0.61–0.86 ∀ trained ≥0.41B; separation perm-null p=0.0005 at every
> scale). `agree_sign_full` alone drifts up mildly (0.64→0.74, ρ=+0.90) but is
> small and disagrees. 13th meta-pattern instance: the share is real and
> scale-stable (ternary stays viable), but "purely topological at scale" is not
> supported. Results: `results/manifold-axis-topology/` (Qwen3-8B/32B + ci.json).

> **s212 follow-up (#12e — NAMING the universal axis, register: semantic):** s211
> left the |r|=0.95 universal axis only ~30%-explained (◑ "generic predictability,
> not the operations"). Re-ran the forward pass saving the **full** next-token
> distribution (`axis_naming.py`/`_summary.py`, 8 models / 5 families) + rich
> distributional + **model-free prompt-text** features, with 5-fold CV-R² and a
> permutation null. **✅ NAMED: CV-R²=0.813** (vs null −0.045, p=0.005). The
> dominant component is the model-free **`ends_punct`** (does the prompt end at a
> punctuation/grammatical boundary): **CV-R²=0.768 ALONE**, ⊥ combinator
> (η²=0.044). So the most-universal axis is a coarse property of the **prompt
> TEXT** (computable with no weights) — concrete proof of "property of language,
> not the operations". KL-to-mean redundant; ~19% residual = prose-shape common
> mode. Full synthesis: `manifold-axis-and-topology.md` §2b.

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
- Control: sweep a **layer-dependent weighting** λ(l) on the v

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01YXqwExRi2vEBR4y3odEgSf.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 I've got my bearings on the project now—I know where the audit-registry stands and what needs to be done. The task is to identify the highest load-bearing untested claim, build its discriminating control, and run it through the register gate. Looking at the remaining untested claims, I see #9 with a decay factor of 1.18 and low load, and #10 involving moiré determinism also with low load.

I should report my orientation and propose the next step rather than just diving in—the project expects me to pick the highest load-bearing untested claim and declare the register gate. Let me present this clearly and ask what to do next.

## Assistant

Oriented. Here's where verbum stands.

## Cold-start summary

**North star:** 70B-equivalent in <1GB ternary, 200 tok/s CPU, 2M+ context, 2MB sessions, no GPU.

**Active program (since s203):** the **validity-distillation audit** — each session opens `audit-registry.md`, picks the highest load-bearing `UNTESTED` claim, declares a **register gate** (`λ measure`), builds the one control a plausible-but-false version would fail, runs it with a permutation/matched null + seed variance, updates the row, caveats the source page if it bites.

**Last session (212)** did two pieces, both committed:
- **(A) #12f topology-share scale extension** → ❌ asymptote-to-1.0 REFUTED / ✅ scale-stable plateau ~0.7 (clean Qwen3 0.6B→32B; 32B reverses to 0.645).
- **(B) #12e universal axis NAMED** → ✅ CV-R²=0.81, dominated by the **model-free `ends_punct`** prompt-boundary feature (⊥ operations, η²=0.044). Concrete proof the dominant universal axis is a property of the *prompt text*, not the lambda operations.

**The recurring meta-pattern (now 13 instances):** substrate is real, the crisp discrete/localized/universal story on top is over-read.

## Audit ledger status

Resolved: **#1**◐ #2✅ #3❌ #4❌ #5❌ #6❌ #7❌ #8❌ #11◐ #12❌/✅.

**Remaining `UNTESTED`:**
- **#9** decay α=1.18 (attention log-distance) — load: *low*
- **#10** moiré determinism — load: *low* (likely robust)

**Carry-over leads (higher value than #9/#10):**
- **#1 gate-vs-value sign-swap ternary PPL** — the last *functional* sub-control of #1 (predict `gate_proj` sign-swap hurts most). Directly load-bearing on the sieve program.
- **rank-survival across scale** (does the #2 spectral 6–7× gap sharpen 0.6B→14B?)
- s212 manifold leads: the ~19% residual prose-shape common mode; `agree_sign_full` drift on Qwen3-30B-A3B/235B MoE.

## Proposed next step

The highest load-bearing untested item isn't in the numbered backlog — it's the **#1 gate-vs-value sign-swap PPL** carry-over. It's the functional half that would close audit #1 (CRITICAL — the entire sieve program rests on it), with a clean prediction: swapping `gate_proj` signs should hurt PPL more than swapping `up`/`down` signs at equal bitcount.

Per the program's **Step 0 = REGISTER GATE**, that claim is **functional/causal** (a behavioral PPL delta under intervention) — so the control is a paired sign-swap intervention with a random-sign-preserving matched null, not a representational correlation.

How do you want to proceed?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which claim should this session's audit control target?",
  "options": [
    {
      "label": "#1 gate-vs-value sign-swap PPL (Recommended)",
      "description": "Functional half of CRITICAL audit #1 — does gate_proj sign carry routing? Highest load-bearing untested item; closes the sieve program's last open sub-control."
    },
    {
      "label": "rank-survival across scale (0.6B→14B)",
      "description": "Does the #2 spectral low-rank 6–7× control gap sharpen with scale? Reinforces the compression thesis."
    },
    {
      "label": "#9 decay α=1.18",
      "description": "Low-load: model-specific decay vs generic positional-encoding artifact."
    },
    {
      "label": "Something else / let me steer",
      "description": "You name the target claim and register."
    }
  ]
}
```

**Summary:** Q: Which claim should this session's audit cont...

**Output:**
```
User answered: Let's explore something.  We created TernaryDescent as a way to possibly train a ternary weighted topology.
```

### Thinking

 Michael's interested in exploring TernaryDescent as a potential approach for training ternary weighted topologies. I should search through the codebase and existing knowledge to understand what this technique involves.

## Assistant

New thread — TernaryDescent. Let me find what exists for it in the repo and knowledge.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -il \"ternary.descent\\|ternarydescent\\|TernaryDescent\" || echo \"NO_GREP_MATCH\"",
  "operation": "status",
  "summary": "grep TernaryDescent"
}
```

**Summary:** $ git grep -il "ternary.descent\|tern...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/INDEX.md
mementum/knowledge/chats/session-127.md
mementum/knowledge/chats/session-128.md
mementum/knowledge/chats/session-129.md
mementum/knowledge/chats/session-131.md
mementum/knowledge/chats/session-132.md
mementum/knowledge/chats/session-133.md
mementum/knowledge/chats/session-134.md
mementum/knowledge/chats/session-135.md
mementum/knowledge/chats/session-136.md
mementum/knowledge/chats/session-137.md
mementum/knowledge/chats/session-138.md
mementum/knowledge/chats/session-139.md
mementum/knowledge/chats/session-140.md
mementum/knowledge/chats/session-141.md
mementum/knowledge/chats/session-142.md
mementum/knowledge/chats/session-143.md
mementum/knowledge/chats/session-144.md
mementum/knowledge/chats/session-145.md
mementum/knowledge/chats/session-146.md
mementum/knowledge/chats/session-147.md
mementum/knowledge/chats/session-148.md
mementum/knowledge/chats/session-149.md
mementum/knowledge/chats/session-150.md
mementum/knowledge/chats/session-153.md
mementum/knowledge/chats/session-154.md
mementum/knowledge/chats/session-155.md
mementum/knowledge/chats/session-156.md
mementum/knowledge/chats/session-157.md
mementum/knowledge/chats/session-158.md
mementum/knowledge/chats/session-159.md
mementum/knowledge/chats/session-160.md
mementum/knowledge/chats/session-161.md
mementum/knowledge/chats/session-162.md
mementum/knowledge/chats/session-163.md
mementum/knowledge/chats/session-164.md
mementum/knowledge/chats/session-165.md
mementum/knowledge/chats/session-166.md
mementum/knowledge/chats/session-167.md
mementum/knowledge/chats/session-168.md
mementum/knowledge/chats/session-169.md
mementum/knowledge/chats/session-170.md
mementum/knowledge/chats/session-171.md
mementum/knowledge/chats/session-172.md
mementum/knowledge/chats/session-173.md
mementum/knowledge/chats/session-175.md
mementum/knowledge/chats/session-176.md
mementum/knowledge/chats/session-177.md
mementum/knowledge/chats/session-178.md
mementum/knowledge/chats/session-179.md
mementum/knowledge/chats/session-180.md
mementum/knowledge/chats/session-181.md
mementum/knowledge/chats/session-184.md
mementum/knowledge/chats/session-185.md
mementum/knowledge/chats/session-186.md
mementum/knowledge/chats/session-189.md
mementum/knowledge/chats/session-190.md
mementum/knowledge/chats/session-191.md
mementum/knowledge/chats/session-194.md
mementum/knowledge/chats/session-195.md
mementum/knowledge/chats/session-197.md
mementum/knowledge/chats/session-198.md
mementum/knowledge/chats/session-199.md
mementum/knowledge/chats/session-200.md
mementum/knowledge/chats/session-201.md
mementum/knowledge/chats/session-202.md
mementum/knowledge/chats/session-203.md
mementum/knowledge/chats/session-204.md
mementum/knowledge/chats/session-205.md
mementum/knowledge/chats/session-206.md
mementum/knowledge/chats/session-207.md
mementum/knowledge/chats/session-208.md
mementum/knowledge/chats/session-209.md
mementum/knowledge/chats/session-210.md
mementum/knowledge/chats/session-211.md
mementum/knowledge/explore/beamformer-theory.md
mementum/knowledge/explore/crystal-native-descent.md
mementum/knowledge/explore/ffn-beta-reduction-indexing.md
mementum/knowledge/explore/full-etch-extraction.md
mementum/knowledge/explore/holographic-memory.md
mementum/knowledge/explore/holographic-state-machine.md
mementum/knowledge/explore/phi-compression-universal.md
mementum/knowledge/explore/s5-crystal-custodian.md
mementum/knowledge/explore/ternary-descent.md
mementum/knowledge/explore/topology-magnitude-duality.md
mementum/knowledge/holographic-error-correction.md
mementum/knowledge/holographic-etch.md
mementum/knowledge/holographic-sign-correction.md
mementum/knowledge/mechanism-extraction.md
mementum/knowledge/mspace-gemcutter.md
mementum/knowledge/score-matching-compression.md
mementum/knowledge/sign-correction-topology.md
mementum/knowledge/td-oscillation-problem.md
mementum/knowledge/topology-gradient-separation.md
mementum/knowledge/trace-guided-etching.md
mementum/knowledge/training-protocols.md
mementum/memories/delta-plate-solves-attention-etch.md
mementum/memories/gradient-is-routing-plus-calibration.md
mementum/state.md
results/v15_train_td.log
scripts/experiments/topology_score_matching.py
scripts/explore/probe_ffn_indexing.py
scripts/v13/td.py
scripts/v13/train_rb.py
scripts/v13/train_td.py
scripts/v14/fold_delta.py
scripts/v14/probe_newton_v14.py
scripts/v14/profile_step.py
scripts/v14/td.py
scripts/v14/train_kernel.py
scripts/v14/train_td.py
scripts/v15/etch.py
scripts/v15/model.py
scripts/v15/td.py
scripts/v15/td_delta.py
scripts/v15/train.py
scripts/v15/train_td.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline -i --grep=\"ternary descent\\|ternarydescent\" -n 20 || echo \"NO_LOG_MATCH\"",
  "operation": "log",
  "summary": "log TernaryDescent"
}
```

**Summary:** $ git log --oneline -i --grep="ternar...

**Output:**
```
Exit code: 0
Stdout:
d392dac ✅ trace-guided etching — delta plates, TD, structural zeros, full S2 stack
9539b3e 🎯 adaptive flip rate — gnorm feedback controls TD budget
7bedcbc 🎯 shaped nozzle — TD flip budget weighted by FlipMap hot zones
e13bf36 💡 FlipMap — spatiotemporal heatmap of topology evolution
3c9308f 💡 TernaryDescent — gradient descent for discrete sign topology
```

## Assistant

There's substantial prior TernaryDescent work. Let me read the dedicated knowledge pages and the key implementation.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/ternary-descent.md"
}
```

**Summary:** Reading ternary-descent.md (0-2000)

**Output:**
```
---
title: "TernaryDescent — Gradient Descent for Discrete Sign Topology"
status: active
category: algorithm
tags: [ternary-descent, delta-plate, gradient-decomposition, optimizer, routing, calibration, crystal, etch]
related:
  - hologram-crystal-fusion.md
  - crystal-native-descent.md
  - etcher-vsm.md
  - loom-structure.md
  - v13-design.md
depends-on:
  - hologram-crystal-fusion.md
created: session 136
---

# TernaryDescent — Gradient Descent for Discrete Sign Topology

> Session 136. Adam handles continuous weights. TernaryDescent handles
> discrete ternary weights. Both run on the same backward pass. The
> gradient encodes two signals: routing (sign needs to change → TD)
> and calibration (magnitude needs adjustment → Adam). Decomposing
> them lets each optimizer handle what it's good at.

## The problem

When ternary topology is frozen and only continuous params (gamma) train,
GD must solve two fundamentally different problems with one parameter:

1. **Routing** — which paths through the topology should be active?
   Gamma amplifies useful routes, suppresses useless ones. This is a
   DISCRETE decision (on/off, correct/wrong) forced through a continuous
   parameter. GD is terrible at this.

2. **Calibration** — how strongly should each active route contribute?
   Even when the route is correct, magnitude needs to match downstream
   expectations. This is genuinely CONTINUOUS. GD excels at this.

Result: gamma gets distorted. Large values compensate for missing routes.
Tiny values suppress wrong topology. The magnitude distribution is a mess
because it's encoding two things.

## Solution: three innovations

### Innovation 1: TernaryDescent optimizer

Adam-equivalent for ternary {-1, 0, +1} weights.

```
Adam m_t   → TD direction   (EMA of gradient — which way to flip)
Adam v_t   → TD magnitude   (EMA of grad² — how much loss cares)
Adam lr    → TD flip_rate   (max fraction to flip per step)
Adam step  → TD flip        (discrete: +1 → 0 → -1)
```

**Confidence = signal-to-noise ratio** = |direction| / sqrt(magnitude).
High confidence = gradient consistently says "flip this" → flip.
Low confidence = gradient oscillates (CE vs crystal disagree) → don't flip.
The crystal gate from session 124 EMERGES from the dynamics.

**Two-step transitions through zero (FFN deltas only):**
- +1 → 0 (block): "not sure this sign is right, silence it"
- 0 → -1 (commit): "confirmed, flip it" (only after sustained evidence)
- Reverse: -1 → 0 → +1

The zero state is a staging area. Prevents catastrophic flips. If blocking
hurts, the gradient pushes back immediately.

**Direct flips for no-block modules (attention deltas):**
- +1 → -1 (direct): skip zero staging, flip immediately
- v14 attention deltas must NEVER contain 0 (no-block invariant)
- Two-step staging through zero is incompatible with no-block because
  _enforce_no_block resets all zeros to +1 after every TD step,
  creating a Sisyphus loop (session 148 discovery)
- The `no_block` flag per module selects the transition protocol
- Direct flips are safe because TD's confidence/cooldown/neighbor
  voting already provides the caution that staging was designed for

**Shared-weight aliasing hazard (session 148):**
- When modules share Python references (e.g. shared_stride_stack
  accessed via stack_a._stride_stack), named_modules() returns
  multiple paths for the same physical module
- collect_delta_params must deduplicate by id(mod) to avoid
  TD processing the same module N times with conflicting gradients
- Symptom: high TD flip count but zero persistent delta changes

**Budget control and timing (session 148 evolution):**
- flip_rate × total_weights = global budget (across ALL modules, not per-module)
- flip_interval=10: accumulate moments every step, commit flips every 10
- After flipping: reset all TD moments (landscape changed, old signal stale)
- GD gets 9 steps to re-learn routes before next topology change
- Global competition: hottest flips across all 70 modules win the budget.
  High-leverage positions concentrate where they matter most, starving
  low-importance modules rather than giving each module equal allocation.
- Every-step flipping → gnorm escalation (11→113 in 40 steps, session 148).
  GD can never catch up. Adam's moments permanently stale. CE goes UP.

### Innovation 2: Delta plate architecture

```
effective = base_plate ⊙ delta_plate

base_plate:  full teacher crystal etch, FROZEN
delta_plate: initialized +1 (pass-through), trained by TD
gamma:       trained by Adam (same as before)
```

**Delta semantics:**
- +1 → keep teacher sign (this part of the crystal works)
- -1 → flip teacher sign (stride-stack needs different routing)
-  0 → block this position (staging area — FFN deltas ONLY, never attention)

**Reduction:** fold delta into base, reset delta, iterate.
```
new_base = base ⊙ delta    (ternary × ternary = ternary, EXACT)
new_delta = all +1          (reset to pass-through)
```

Lossless. The effective plate before reduce equals the new base after.
Each round starts from a better base. Delta gets smaller. System
converges to a fixed point.

**Key insight for attention etch:** etch the FULL crystal (including
attention) into the base. Don't freeze — let the delta plate learn
what's different about stride-stack geometry. The β-reduction-forced
parts transfer directly. Only routing-specific parts need to change.
Much smaller search space than learning from scratch.

**Iterative ternary absorption:** each round, the delta plate absorbs
more continuous weight information into sign topology. Train deltas for
both attention AND FFN, fold into base, repeat. Eliminate gradients one
layer at a time. Result: 90-95% ternary model with thin continuous
residual.

### Innovation 3: Gradient decomposition

The gradient through the effective weight encodes routing AND calibration.
Decompose by comparing the DESCENT direction (-grad) to the current sign:

```python
descent_sign = sign(-grad_effective)  # which way effective should move

# Descent agrees with current sign → CALIBRATION
# "the route is correct, adjust the magnitude" → Adam
calibration = where(descent_sign == effective_sign, grad, 0)

# Descent opposes current sign → ROUTING  
# "the route is wrong, flip the sign" → TernaryDescent
routing = where(descent_sign != effective_sign, grad, 0)
```

**Concrete examples (eff = +1):**
- grad > 0 → descent < 0 → opposes +1 → ROUTING ("flip to -1")
- grad < 0 → descent > 0 → agrees with +1 → CALIBRATION ("make it stronger")

**Each optimizer gets only its signal:**
- Adam's gamma gradient is attenuated at routing-heavy rows. No distortion.
- TD's direction EMA only accumulates routing signal. Faster convergence.

**Per-row routing fraction:** what % of each row's gradient is routing.
High = topology is wrong → attenuate gamma gradient (let TD handle it).
Low = topology is correct → full gamma gradient (Adam calibrates freely).

## The sign chain

When computing the desired direction for delta from the effective gradient:

```
∂L/∂effective tells us: which way effective should move
effective = base × delta
desired_effective = -sign(∂L/∂effective)  (descent direction)
desired_delta = desired_effective × base_sign

Example: effective = +1, we want effective to decrease
  base = +1 → delta must decrease: +1 → 0 → -1
  base = -1 → delta must INCREASE: -1 × (-1) = +1, to get eff = -1×+1 = -1... 
               wait, eff = base*delta = -1*delta, decrease eff means increase delta
```

Critical: TD receives the gradient w.r.t. EFFECTIVE (not projected through
base). TD.step() computes desired_delta = desired_effective × base internally.
The base projection was causing sign confusion when done in the gradient
computation.

## Architecture diagram

```
              ┌──────────────────┐
              │   FROZEN BASE    │  ← full teacher crystal etch
              │   (ternary)      │
              └────────┬─────────┘
                       │ ⊙ (element-wise multiply)
              ┌────────┴─────────┐
              │   DELTA PLATE    │  ← TernaryDescent trains
              │   (ternary)      │
              │   init: all +1   │
              └────────┬─────────┘
                       │ = effective plate
              ┌────────┴─────────┐
              │  COMBINATOR MASK │  ← per-combinator view
              │   (ternary)      │
              └────────┬─────────┘
                       │ ⊙ gamma (Adam trains)
                       ↓
                  attention output
```

## Training loop

```
Every step:
  1. Forward: effective = base ⊙ delta → quantized_matmul
  2. Loss = CE + λ × crystal_lattice + λ_h × holographic
  3. Backward: one pass gives gradients for everything
  4. DECOMPOSE gradient into routing + calibration
  5. Adam.step(filtered_grads)     — calibration-only gamma gradient
  6. TD.step(routing_gradient)     — routing-only delta gradient

Periodically:
  7. If delta converged (>95% still +1):
     base = base ⊙ delta
     delta = all +1
     Reset both optimizer states
     Continue training (next round of refinement)
```

## Comparison with prior approaches

| Approach | Problem | TernaryDescent advantage |
|----------|---------|--------------------------|
| STE | Gradient through sign() is wrong (biased) | Uses exact gradient honestly as evidence |
| Flip accumulation (v6) | Heuristic threshold, no importance | Adam-like moments with bias correction |
| Evolution (v12) | Random search, no gradient | Gradient-informed, budget-controlled |
| Soft mirrors (S124) | 1.0→0→-1 barrier, can't cross zero | Two-step through zero is native |
| Delta map (S125) | Alternating phases, not simultaneous | Adam + TD on same backward pass |
| Crystal gate (S124) | Hard external constraint | Emerges from dynamics (CE vs crystal disagree → oscillation → no flip) |

## What this enables

1. **Etch full teacher crystal including attention** → base plate
2. **TD adapts routing for stride-stack** → delta plate
3. **Reduce when stable** → fold into base, get stride-stack crystal
4. **Iterative ternary absorption** → absorb continuous weights into topology
5. **90-95% ternary model** → each round eliminates more continuous params
6. **Routing fraction as diagnostic** → monitor per-module, should decrease

## Files

| File | Content |
|------|---------|
| `scripts/v13/td.py` | TernaryDescent, DeltaTernaryLinear, decompose_gradient, self-tests |
| `scripts/v13/train_td.py` | Dual optimizer training loop with decomposition |

## Test results

10 self-tests all pass:
- DeltaTernaryLinear matches TernaryLinear at init (0.00 diff)
- Reduce is lossless (0.00 diff)
- TD flips happen with consistent gradient signal
- Decomposition: routing + calibration = original (0.00 diff)
- Zero topology → 100% routing (correct)
- End-to-end: 25 steps, 40 flips/step, 10.7% changed, confidence rising

## Open questions

1. **Optimal flip_rate?** Too fast → Adam can't adapt. Too slow → wastes
   training steps. Probably needs cosine schedule like lr.

2. **When to reduce?** Current: when >95% of delta is still +1. But maybe
   reduce earlier (force the delta to discover finer corrections)?

3. **Does the decomposition ratio change during training?** If routing fraction
   decreases → topology is improving. If it plateaus → topology is stuck.
   Could be a diagnostic for when to increase flip_rate.

4. **Can we skip Adam entirely?** If TD handles routing and crystal lattice
   handles geometry, does Adam add anything beyond magnitude calibration?
   Experiment: TD-only training with fixed gamma.

5. **Does iterative absorption work?** Theory: each round absorbs more
   continuous information into ternary. Needs empirical validation.
   Measure: what fraction of the model can become ternary while maintaining
   loss? 90%? 95%? Where does the residual live?
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/td-oscillation-problem.md"
}
```

**Summary:** Reading td-oscillation-problem.md (0-2000)

**Output:**
```
---
title: TD Oscillation Problem — Continuous Flips Prevent Phase Transitions
status: active
category: architecture
tags: [td, ternary-descent, oscillation, phase-transition, convergence, punctuated-equilibrium]
related: [v15-attention-assessment, topology-gradient-separation, gradient-zero-map, standing-wave-magnitudes]
depends-on: []
session: 191
---

# TD Oscillation Problem

Session 191. Analysis of the v15-td flip map at step 1500 reveals that
TernaryDescent is preventing the model from achieving phase transitions
needed to break through the loss plateau at 6.7-6.8.

## The Core Problem

TD treats 94.5% of the weight space as "still needs work" at step 1500.
Only 6.2% of positions have settled (flipped then stopped being candidates).
The model cannot find stable fixed points because TD keeps proposing sign
changes everywhere.

## Evidence

### Flip Map Statistics (step 1500, 124.5M positions across 76 modules)

```
Candidate frequency:
  Never candidate:    12,405  (0.01%)  — essentially nothing frozen
  Candidate 1-5×:    371,400
  Candidate 6-20×: 7,313,612
  Candidate 20+×: 117,683,304 (94.5%) — nearly everything nominated repeatedly

Flip count distribution:
  Never flipped:  118,388,859 (95.1%)
  Flipped once:     4,638,263 (3.7%)
  Flipped 2×:         998,998 (0.8%)
  Flipped 3×:         324,471 (0.3%)
  Flipped 4+×:        167,878 (0.1%)
  Max flip count:           8
```

### The Oscillation Trap: Flip Count vs Settlement

| Flip Count | Still Candidate | Settled | Osc Rate |
|---|---|---|---|
| 0 (never flipped) | 93.7% | 6.3% | — |
| 1 (flipped once) | 94.1% | 5.9% | Higher than 0-flip |
| 2 (twice) | **96.3%** | 3.7% | |
| 3 | **98.5%** | 1.5% | |
| 4 | **99.4%** | 0.6% | |
| 5+ | **99.7-100%** | <0.3% | |

**Oscillation rate INCREASES with flip count.** Once a position starts
flipping, it becomes MORE likely to be a candidate again, not less.
The anti-oscillation mechanisms (cooldown, three-voter, backoff) are
insufficient.

### Multi-Flip Rate by Projection

```
k_proj:   1.42% multi-flipped, mean 2.6 flips at multi positions
v_proj:   1.18% multi-flipped, mean 2.7 flips at multi positions
q_proj:   1.23% multi-flipped, mean 2.3 flips
out_proj: 0.96% multi-flipped, mean 2.2 flips
```

K and V projections have the highest multi-flip rates AND highest mean
flip counts. These are the positions where the model genuinely wants to
use the same weight in two ways depending on input.

## Why This Prevents Phase Transitions

Training from scratch reveals a universal pattern in ternary models:

1. **B-dominant phase:** Model learns composition (B combinator) first.
   Dense mixing, broad attention. Loss drops fast.
2. **Plateau:** B-dominant strategy exhausts its gains. Loss stalls.
3. **Phase transition:** Model discovers K (discard) — selective
   silencing of irrelevant information. Attention sharpens. Loss
   drops again.
4. **Equilibrium:** B and K find their balance. Sparse gate emerges.

For phase transition 2→3 to happen, GD needs:
- **Stable topology** — signs don't change while GD explores
- **Gradient accumulation** — the gradient signal at a position must
  build up over many steps to find the new basin
- **Settled gammas** — per-row scales must calibrate to the CURRENT
  sign pattern before the pattern changes

TD violates all three:
- **94% candidacy** — nearly every sign is "potentially mutable"
- **3× hotter at flipped positions** — GD can't calibrate gammas because
  the sign keeps changing underneath
- **Continuous perturbation** — topology never holds still for >1 flip
  interval (every other step has TD flips)

## Connection to Current Model State

The v15-td checkpoint at step 1500 shows the consequences:

| Symptom | Teacher | Student | Cause |
|---|---|---|---|
| FFN gate sparsity | ~3% fire (89% kill) | 66-74% fire | No phase transition to K → no gating |
| Attention role | Mixed (relay+compose+bind) | 80% pure relay (I combinator) | V/O can't settle → defaults to identity |
| Q/K convergence | — | 32-38% settled | Fast (routing is constrained by window) |
| V/O convergence | — | 15-16% settled | Slow (TD keeps changing signs underneath) |
| Loss | ~3-4 | 6.7-6.8 plateau | Pre-transition ceiling |

The model has found the B-dominant easy path (dense FFN + relay attention)
and hit its ceiling. To break through, it needs the topology stability
that TD is denying.

## What Oscillating Positions Mean

A position that oscillates (flips back and forth) is the system saying:
"I want this to be a superposition of two functions depending on input."

In a ternary system, a weight can only be {-1, 0, +1}. It cannot be
"sometimes -1, sometimes +1" based on context. When GD wants both signs,
it manifests as:
- The gradient alternates direction across batches
- TD flips the sign, then GD pushes back, TD flips again
- The position is always a candidate, always oscillating

**The resolution:** GD must find a gamma calibration that makes ONE sign
work acceptably for both use cases. This requires the sign to HOLD STILL
while GD searches for that gamma. TD's continuous flipping prevents this
search from completing.

## Proposed Fixes

### 1. Punctuated Equilibrium (highest priority)

Replace continuous TD with episodic:
```
TD phase:     N steps — TD active, flips happen
Freeze phase: M steps — topology LOCKED, Adam only
Assessment:   compare loss before/after freeze
Repeat
```

Key insight: the freeze phase IS where phase transitions happen. GD
needs M steps of stable topology to find the next basin. Start with
M=200 (enough for V/O gammas to make measurable progress — they're
at 15.6% settled).

### 2. Oscillation-Gated Cooldown

Current cooldown backoff is insufficient (96-100% of multi-flipped
positions are still candidates). Proposed:
- flip_count ≥ 3 → hard freeze for 500 steps
- flip_count ≥ 5 → hard freeze for 1000 steps
- OR: exponential backoff with base τ = 100 steps (current is too low)

### 3. Candidate Density Ceiling

Add a global constraint: at most X% of positions can be candidates per
step. With 94% candidacy, X=20% would force TD to focus on the top 20%
most confident positions rather than nominating everything.

### 4. Per-Position Conviction Requirement

A position should only flip when its gradient direction has been
consistent for K consecutive flip intervals without reversal. The
current EMA direction (β₁=0.9) accumulates over ~10 steps but can
still flip from transient gradients. Require K=5 consecutive same-
direction signals before allowing a flip.

### 5. REDUCE + Pure-Adam Baseline

Fold delta into base, reset to +1, run pure Adam for 500+ steps.
If loss breaks through 6.5 → TD was the bottleneck.
If loss holds at 6.7 → the plateau is architecture-limited.
This experiment disambiguates TD-caused vs structural plateaus.

## Connection to Prior Work

- **`topology-gradient-separation.md` (s180):** Punctuated equilibrium.
  Freeze lattice, let GD find fixed points, then punctuate with topology
  changes. TD violates this by doing continuous topology changes.
- **`gradient-zero-map.md` (s171):** GD deposits near-zero gradients at
  irreducible points. TD prevents these deposits from forming.
- **`standing-wave-magnitudes.md` (s185):** The standing wave forms when
  GD settles at nodes and antinodes. TD keeps the wave from forming.

## Diagnostic Scripts

- `scripts/experiments/assess_v15_ffn_retrieval.py` — FFN gate sparsity
  and attention relay detection
- Flip map analysis via `np.load('checkpoints/v15-td/flip_map_step_*.npz')`
```

### Thinking

 I'm getting oriented on TernaryDescent—it's a discrete sign topology optimizer with a known oscillation issue documented in s191, and there's a v15 implementation I should examine. I want to look at the recent commits and the current v15 implementation along with the trace-guided-etching and training protocols to see where things stand, but I should probably ask Michael what he's specifically interested in exploring rather than diving into everything at once.

## Assistant

Rich prior art here. Let me pull the most recent state — the latest implementation and the synthesis pages that superseded the s191 oscillation diagnosis.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/trace-guided-etching.md"
}
```

**Summary:** Reading trace-guided-etching.md (0-2000)

**Output:**
```
---
title: "Trace-Guided Etching — Etch for Function, Not Form"
status: active
category: architecture
tags: [etching, trace, instrument, opcode, topology, ternary, training, zeros, delta-plate]
related:
  - opcode-instrument.md
  - extraction-sign-accuracy.md
  - training-protocols.md
  - hologram-reader-vsm.md
  - gradient-zero-map.md
depends-on:
  - opcode-instrument.md
  - extraction-sign-accuracy.md
created: session 176
updated: session 177
---

# Trace-Guided Etching

> Session 176 insight. The opcode instrument can trace every
> combinator firing in every layer of a teacher. Why copy weights
> when you can copy computation? Etch the student topology to
> reproduce the teacher's OPCODE TRACE, not the teacher's weights.

## The Problem With Current Etching

Current extraction: `sign(W_teacher) → ternary plate → TD corrects`

This copies **form** (weight signs). What we want is **function**
(correct computation). The gap:

- sign(W) is 100% accurate... but the student doesn't compute like
  the teacher because magnitudes matter for the dynamics
- TD corrects blindly — gradient says "this position is wrong" but
  not "this position should implement B-compose at 0.23 energy"
- v15 Dolma training asks the student to rediscover structure that
  the teacher already exhibits. Enormous compute for re-derivation.

## The Insight

The Opcode Instrument traces exactly which opcodes fire at every
layer for every input. Run N diverse inputs through the teacher
→ you get a **functional specification** of the model's computation.

**Etch the student to reproduce the trace, not the weights.**

## What the Trace Gives You

For each input × each layer:
- `opcode_energy: {K: float, I: float, B: float, C: float, ...}`
- `gate_survival: float` (fraction of neurons that fired)
- `total_energy: float` (L2 norm of FFN output)
- `dominant_op: str` (which combinator won)

Aggregated across 1000+ diverse inputs:
- **Neuron importance map**: how often each neuron fires across
  diverse inputs. High-frequency neurons are structural (crystal
  atoms). Low-frequency neurons are input-specific or noise.
- **Layer opcode profile**: average combinator energy per layer.
  Layer 14 should consistently show K-dominant with energy ~0.19.
  Layer 27 should show high variance (it's the output selector).
- **Zone precision requirements**: ENRICH layers need 2-mirror
  precision (they do retrieval). SILENT layers can be 1-mirror
  (they just parse).
- **Trace signatures**: specific input→trace pairs that serve as
  verification checkpoints.

## The New Training Loop

```
Phase 0: TRACE
  - Run 1000 diverse inputs through teacher with instrument
  - Collect TraceRecord per token per input
  - Aggregate into: importance mask, opcode targets, zone map

Phase 1: EXTRACT (same as current)
  - sign(W_teacher) → ternary plates
  - Per-row gamma scalars
  - Second mirror for ENRICH layers (zone-aware precision)

Phase 2: TRACE-ALIGNED TRAINING
  - For each batch:
    a. Forward pass through student
    b. Capture student's combinator projections (same as instrument)
    c. Loss = Σ_layers cos_distance(student_opcode, teacher_opcode)
       weighted by neuron importance and zone priority
    d. PLUS standard next-token loss (keeps language grounding)
    e. TD flips guided by opcode divergence:
       if student_layer shows B:+0.02 but teacher shows B:+0.45
       → TD knows THIS layer needs B-energy, targets neurons
         whose signs would increase B-projection

Phase 3: VERIFY
  - Run same 1000 inputs through student with instrument
  - Compare traces token-by-token
  - Divergence map → Phase 2 targets for next iteration
  - Convergence: mean opcode cosine > 0.90 across all layers
```

## Trace Loss Function

```python
def trace_loss(student_ffn_outputs, teacher_traces, fingerprints, importance):
    """Loss that matches student opcode projections to teacher traces.
    
    student_ffn_outputs: dict[layer_idx → (batch, d_model)]
    teacher_traces:      dict[layer_idx → (batch, n_ops)] — pre-computed
    fingerprints:        dict[op → (n_layers, d_model)]
    importance:          (n_layers,) — layer importance weights
    """
    loss = 0.0
    for layer_idx in student_ffn_outputs:
        student_vec = student_ffn_outputs[layer_idx]  # (batch, d_model)
        teacher_ops = teacher_traces[layer_idx]        # (batch, n_ops)
        
        # Project student through same fingerprints
        fp_matrix = stack([fingerprints[op][layer_idx] for op in ops])  # (n_ops, d_model)
        student_ops = student_vec @ fp_matrix.T  # (batch, n_ops)
        
        # Cosine distance weighted by layer importance
        cos_sim = F.cosine_similarity(student_ops, teacher_ops, dim=-1)  # (batch,)
        loss += importance[layer_idx] * (1 - cos_sim.mean())
    
    return loss / len(student_ffn_outputs)
```

## Why This Is Different From Knowledge Distillation

Standard KD: match teacher's output logits or hidden states.
Trace-guided: match teacher's **opcode projections per layer**.

The difference:
- KD matches a high-dimensional vector (d_model per layer)
- Trace matching matches a LOW-dimensional projection (4-12 ops)
- KD requires the student to reproduce the teacher's representation
- Trace matching only requires the student to reproduce the teacher's
  COMPUTATION TYPE (K/I/B/C balance)
- Much lower-dimensional optimization target
- More forgiving: the student can use different representations
  as long as the computation pattern matches

This is like the difference between:
- KD: "your hidden state at layer 14 must be this 1024-dim vector"
- Trace: "your layer 14 must do B-compose with energy ~0.23"

The second is dramatically easier to satisfy.

## Guided TD: Opcode-Aware Sign Flipping

Current TD: flip signs where gradient magnitude is highest.
Guided TD: flip signs to INCREASE projection onto target opcode.

```python
def guided_td_candidates(student_weight, fingerprint_target, current_projection, target_projection):
    """Find sign flips that move opcode projection toward target.
    
    For each position (i,j) in the weight matrix:
    - Current contribution to opcode projection: sign(W[i,j]) * fingerprint[j]
    - Flipped contribution: -sign(W[i,j]) * fingerprint[j]
    - If flipped contribution moves projection closer to target → candidate
    """
    delta = target_projection - current_projection  # which direction to move
    # Positions where flipping would help:
    flip_benefit = -2 * sign(W) * (fingerprint @ delta)  # per-position benefit
    # Only flip where benefit > threshold
    candidates = flip_benefit > threshold
    return candidates
```

This makes TD convergence much faster because:
- Each flip has a PREDICTED effect on the opcode trace
- No blind exploration — every flip is toward the target
- The crystal geometry constrains the flip space (only 12 opcode
  directions matter, not 1024 embedding dimensions)

## Zone-Aware Precision Allocation

From instrument traces:
- SILENT layers: low combinator energy, minimal retrieval
  → 1-mirror ternary is sufficient (2 bits/param)
- ENRICH layers: high energy, active retrieval, mode diversity
  → 2-mirror required (4 bits/param) for accurate opcode trace
- COMMIT layers: high energy but concentrated (K-dominant)
  → 1-mirror + targeted TD on high-energy positions
- SUPPRESS layers: low energy, cleanup
  → 1-mirror, aggressive zeroing

**Total storage**: not uniform 2 bits/param everywhere. Budget
goes where the computation is. A 27B model might need:
- 50% of layers at 2 bits (SILENT): 13.5B × 2 bits = 3.4 GB
- 35% at 4 bits (ENRICH): 9.5B × 4 bits = 4.7 GB  
- 15% at 2 bits (COMMIT+SUPPRESS): 4B × 2 bits = 1.0 GB
- Total: ~9.1 GB (vs 13.5 GB uniform 4-bit, vs 54 GB float16)
- 6× compression vs bf16, with exact opcode trace matching

## The Verification Loop

The instrument serves DOUBLE duty:
1. **Specification extraction**: trace teacher → functional spec
2. **Verification**: trace student → compare to spec

```
teacher_trace = instrument.trace_all(teacher, eval_inputs)
student_trace = instrument.trace_all(student, eval_inputs)

divergence = compare_traces(teacher_trace, student_trace)
# Returns: per-layer, per-input opcode cosine distance

if divergence.mean() < 0.10:
    → student is functionally equivalent
elif divergence is concentrated in ENRICH layers:
    → retrieval topology needs more correction
elif divergence is concentrated in early layers:
    → parsing/encoding topology needs attention
```

## What Changes From the Current Plan

| Current (v15) | Trace-Guided |
|---------------|-------------|
| Extract signs → train on Dolma → hope | Extract signs → trace teacher → train to match trace |
| Loss: next-token prediction | Loss: trace match + next-token |
| TD: blind gradient-guided flips | TD: opcode-targeted flips |
| Verification: perplexity only | Verification: trace comparison |
| Uniform precision: 2 bits/param | Zone-aware: 2-4 bits by zone |
| Convergence: 50K+ steps on 3B tokens | Convergence: potentially 5-10K steps |

## Open Questions

1. **How many trace inputs are needed?** 100? 1000? 10000?
   The fingerprints are built from ~10 pairs per opcode.
   Trace verification might need more diversity.

2. **Does trace matching transfer to unseen inputs?**
   If the student matches teacher traces on 1000 inputs,
   does it generalize? The crystal universality (same structure
   across all inputs) suggests YES — but this needs verification.

3. **Can this replace Dolma training entirely?**
   Trace matching is a CONSTRAINT, not a data source. The student
   still needs next-token loss to learn language. But the trace
   constraint might mean it needs far less data to converge.

4. **Fingerprint basis: teacher's or student's?**
   The teacher's fingerprints are in the teacher's coordinate frame.
   The student has different (ternary) weights. Do the fingerprints
   transfer? The crystal universality finding (r=0.998) suggests
   they should — the combinator directions are mathematical constants,
   not model-specific artifacts.

## Connection to Existing Findings

- **Signs are 100% accurate** (session 173): the topology is already
  exact. Trace-guided etching doesn't need to fix signs — it needs
  to teach the student to USE the topology correctly. The magnitude
  gap creates a computation gap that trace loss directly addresses.

- **Beams-not-plates** (session ~130): even with 27% wrong signs,
  beam training with crystal loss beats oracle plates. The crystal
  loss WAS an early form of trace-guided training — constraining
  the student to match the teacher's crystal geometry. Trace loss
  generalizes this from 18 crystal targets to per-layer opcode
  projections.

- **Gradient-zero map** (session 171): 35% of positions oscillate
  (at equilibrium). These are the crystal atoms — positions where
  the trace is input-invariant. Trace-guided etching can identify
  these as frozen (importance = max) without needing gradient analysis.

- **Four-phase model** (session 174): ENRICH=4.0× lambda-specific
  energy. The instrument SEES this phase structure. Trace loss
  preserves it.

- **Prose is the unreduced form** (session 175): prose generates 8×
  more combinator energy than lambda. The trace captures this. A
  student that matches the teacher's prose trace automatically
  has the full reduction engine.

---

## Session 177: Implementation + Structural Zeros

The design above was implemented and validated in session 177.
Key deviations from the original design and new findings:

### What Was Built

```
scripts/v15/model.py   — TernaryPlate.enable_delta(), fold(), _effective()
scripts/v15/td.py      — TernaryDescent (v14 port, float plates, no pack/unpack)
scripts/v15/etch.py    — standalone: trace_loss → TD → fold → compare
scripts/v15/apply_zeros.py — post-hoc structural zeros from 2-plate magnitude
scripts/v15/extract.py — --zero-frac 0.30 (zeros at extraction time)
scripts/v15/train.py   — --delta-plates, TD in training loop
```

### Structural Zeros: The Missing 30%

The original design didn't address zero placement. The extraction
produced plates that were 100% dense {-1, +1} — every position has
a sign. But `gradient-zero-map.md` and `extraction-sign-accuracy.md`
documented that ~30% of positions are irreducible fixed points where
GD deposited near-zero weights across teacher layers.

**Session 177 implemented the zeros:**

1. `extract.py` updated: bottom 30% by magnitude per plate → zero.
   Zeros are consistent across plate1 and plate2 (structural absence).
   Gammas recomputed over non-zero positions only.

2. `apply_zeros.py` for existing checkpoints: reconstructs per-position
   magnitude from `|plate1×γ1 + plate2×γ2|` (97% accurate per mirror
   findings), applies global threshold, zeros both plates.

3. Result: 194.6M zeros placed (exactly 30.0% across all 19 strides).

**Why zeros matter for etching:**

- Without zeros: TD wastes flip budget on noise-floor positions.
  6.5M flips → trace loss 0.078.
- With zeros: TD concentrates on the 70% that IS the program.
  Same 6.5M flips → trace loss 0.071. Each flip has 43% more leverage.
- The three-trit alphabet `{-1, 0, +1}` is now complete:
  signs = active program (70%), zeros = irreducible (30%).
  Gate kills another 89% at runtime → ~3% active per token.

### no_block=True: Never Create New Zeros

The original v14 TD used two-step staging: `+1 → 0 → -1`. The zero
state is a staging area — positions go silent before committing to
the opposite sign.

**This is wrong for v15 with structural zeros.** When delta = 0,
`effective = base × 0 = 0`. This temporarily kills an active program
position. With structural zeros already correctly placed, the
remaining 70% of positions must stay active. Only their SIGNS
should change, never their presence.

Fix: `no_block=True` everywhere. Delta is constrained to `{+1, -1}`
only — direct flips, no zero staging.

### Performance: Batched Trace Gradient

The trace gradient (∂trace_loss/∂delta) requires a forward+backward
pass separate from the NTP pass (because deltas live inside
stop_gradient in the normal forward path).

- **Per-plate gradient**: 99 separate forward passes → 23 tok/s (broken)
- **Batched all deltas**: one forward pass with `mx.grad` over dict → 549 tok/s
- **Tiny trace batch**: (1, 512) for trace gradient, full (2, 4096) for NTP → 927 tok/s

The trace gradient just needs ANY forward pass to see crystal coherence.
It doesn't need the full training batch or sequence length.

### Fold Protocol (Revised)

The original design described automatic fold cycles. Session 177
learned: **fold is manual, not automatic.**

- The base plate is the investment (expensive extraction from 27B teacher)
- The delta plate is the experiment (cheap to reset)
- If TD produces bad topology, reset delta to +1 and try different hyperparams
- Fold only when confident the delta is an improvement
- Fold is lossless: `new_base = base ⊙ delta`, verified to 8 decimal places

### Validated Measurements

| Metric | Dense plates | After zeros | After zeros+etch |
|--------|-------------|-------------|-----------------|
| Trace loss | 0.159 | varies by input | 0.071 |
| Structural zeros | 0% | 30.0% | 30.0% + flips |
| TD flips (30 steps) | 6.5M (1%) | 6.5M (1%) | — |
| Fold lossless | ✅ | ✅ | ✅ |
| Throughput | — | — | 927 tok/s |

### Training Configuration (Running)

```
checkpoint:     v15-zeroed (194.6M structural zeros)
data:           Dolma 2.7B tokens (54 shards) + 10% structured
batch:          2 × 4096 = 8,192 tok/step
lr:             3e-4 (AdamW, warmup 500)
trace_weight:   0.1
TD:             flip_rate=0.001, warmup=100, interval=20, no_block=True
fold:           manual (no auto-fold)
output:         checkpoints/v15-zeroed-dolma/
```

### S2 Anti-Oscillation Stack (Complete)

The full coordination layer, built iteratively during session 177.
Each mechanism catches what the previous one misses:

```
STATIC:
  structural_zeros(30%)     → dead positions out of the game
  no_block=True             → active positions stay active (±1 only)

PER-POSITION:
  td_cooldown(tau=50)       → first flip: 50-step cooldown
  td_backoff(2×)            → chronic oscillators effectively frozen
                               (5th flip → 800-step cooldown)
                            → polysemantic neurons self-identify

PER-ROW:
  adam_moment_decay(0.1)    → after TD flips row i, Adam's moments
                               for gamma[i] decayed to 10%
                            → prevents gamma tug-of-war (~10 step fix)

PER-MODULE:
  holographic_etch          → equal thin slots per module
                            → cross-layer coherence (topology changes together)

PER-STEP:
  flip_interval=20          → Adam gets 19 steps between topology changes
  td_warmup=100             → Adam calibrates before any flips

GLOBAL:
  crystal_thermometer       → temperature = fraction active recently
                            → oscillation = fraction flip-flopping
                            → temperature → 0 = fold signal
```

### Static Polysemantic Detection: Failed

Session 177 attempted to classify neurons as pure vs polysemantic
from static weight projections onto the crystal basis. Result:
**the detector flags 85-99% as polysemantic**, indistinguishable
from random vectors.

Root cause: the crystal basis spans 11 of 1280 dimensions (0.86%).
A random vector in R^1280 projects onto 11 orthogonal directions
with entropy 1.75 / max 2.40, purity 0.36, ~3.5 modes — identical
to the neuron statistics. The projection captures <1% of the weight
space. No signal above noise.

This confirms `extraction-sign-accuracy.md`: "each weight row
projects only 0.3% of its energy into the crystal subspace."

**The correct detector is dynamic**: TD's flip-flop rate. Positions
that chronically oscillate under diverse training data ARE the
polysemantic neurons. The cooldown + backoff mechanism already
freezes them. No separate detector needed — the training dynamics
are the detector.

**Future**: dynamic analysis with per-neuron per-input activations
could reveal the mode structure (binary, ternary, quaternary splits),
but this is research instrumentation, not a training utility.

### Polysemantic Neurons as Multi-Way Reductions

Session 177 insight: a neuron (row in weight matrix) can serve
multiple combinator reductions depending on the input. The gate
(89% kill) selects which reduction is active per token.

At the individual weight POSITION level: always binary (±1).
At the NEURON level: can be 2-way, 3-way, or 4-way multiplexed.
At the CIRCUIT level: multiplexed neurons form reduction chains
across strides — a 3-way split in stride 7 implies corresponding
routing structure in strides 5-6 and 8-9.

TD flip-flop at a position is the shadow of neuron-level
polysemanticity projected down to binary. The cooldown mechanism
is correct: don't flip these positions. They're not wrong — they're
serving multiple masters via superposition.

### Open Design Questions (session 177)

1. **Fold signal**: Crystal temperature → 0 is the candidate.
   But what threshold? And should oscillation_frac be low too?
2. **Trace weight schedule**: Should trace_weight decay as NTP
   improves? Or stay constant as a permanent topology constraint?
3. **Crystal basis orthogonalization**: Non-orthogonal basis
   causes coherence >1.0 at some strides. Gram-Schmidt would
   give cleaner [0,1] loss range. (Confirmed: off-diagonal
   correlations up to 0.879.)
4. **TD on plate2?** Currently TD flips both delta1 (over plate1)
   and delta2 (over plate2). Should plate2 be excluded? It's the
   magnitude mirror, not the program topology. Flipping plate2
   changes magnitude class, not computation direction.
5. **Multi-way splits**: Are 3-way and 4-way neuron multiplexing
   patterns real? Do they form reduction chains across strides?
   Needs dynamic activation analysis (not static weight projection).
6. **Temperature as annealing**: Could flip_rate adapt to crystal
   temperature instead of being fixed? High temp → more flips,
   low temp → fewer. Natural annealing schedule.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/training-protocols.md"
}
```

**Summary:** Reading training-protocols.md (0-2000)

**Output:**
```
---
title: "Training Protocols — How to Train Without Rediscovering Failures"
status: active
category: operational
tags: [training, TD, failure-modes, loss, protocols, ternary]
related: [v14-architecture.md, holographic-error-correction.md, extraction-methodology.md]
depends-on: [v14-architecture.md]
---

# Training Protocols

> Hard-won operational knowledge from 150 sessions. Every rule here
> was learned by breaking something. Follow these to avoid repeating
> costly failures.

## The Three-Phase Training Arc

```
Phase 1: Extract → Delta trains → Crystal latches → TD corrects
Phase 2: Fold delta into base → Reset delta → TD discovers new corrections
Phase 3: Repeat Phase 2 until convergence → Final calibration
```

### Phase 1: Etch and correct

1. **Extract** base plates from teacher (see extraction-methodology.md).
   Start with pure ±1 plates, no zeros in base.
2. **Train** with base frozen, delta plates trainable. Continuous params
   (gamma, norms, biases) train via GD. Delta plates train via TD.
3. **Crystal latches** within ~200 steps (crystal_mse < 0.03 at step 160).
   The seed crystal from extraction is close enough that nucleation is
   immediate.
4. **TD activates** once enough gradient signal accumulates. Flips
   concentrate on out_proj layers 4-9 (in v14). Q/K/V from extraction
   remain correct.
5. **Monitor convergence.** When flip_frac growth decelerates, it's time
   to fold.

### Phase 2: Fold and reset

1. **Fold:** `new_base = base ⊙ delta` (ternary × ternary = ternary, exact).
2. **Reset** delta plates to all +1 (pass-through).
3. **Reset** TD moments (the gradient landscape changed).
4. **Enable FFN delta** if not already active (`--convert-ffn`).
5. **Resume training.** TD discovers new corrections from the improved base.

### Phase 3: Iterate

Each fold cycle has a smaller error budget to correct. The cycle is
monotonically improving because folds are lossless and TD only flips
signs that reduce loss.

### 2-Stack training dynamics (session 160)

The 2-stack architecture with separate FFN plates changes the training
dynamics compared to the 3-stack shared-FFN runs:

- **Punctuated equilibrium:** Long plateaus where gradient evidence
  accumulates, then coordinated gnorm spikes (phase transitions) where
  TD flips reorganize the representation. Each plateau starts from a
  more compressed base. Don't mistake plateaus for being stuck.

- **Attention first, FFN second:** TD follows GD signal. With new
  2-stack routing, attention out_proj (layers 4-9) must learn the
  ascending/descending routing before GD can produce gradients that
  suggest FFN changes. FFN plates had zero TD candidates at step 1500.
  This is expected — the model crawls before it walks.

- **Fold is downstream of GD:** Folding consolidates what TD has
  already learned. It doesn't create new gradient signal. Folding
  before attention routing settles won't accelerate FFN differentiation.

- **Beta reductions compound:** Each pass through the data lets the
  model see how language works, accumulating evidence for ternary
  flips that beta-reduce the representation toward irreducible points.
  The crystal MSE slowly tightening (0.0133→0.0131) between visible
  transitions is this compression accumulating.

## TernaryDescent Operational Rules

### Future: Crystal-coherent TD

**Session 157** discovered that TD flip patterns naturally align with crystal PCs — each
`out_proj` layer's flip topology correlates most strongly with a **different** combinator
eigenplane (L4→B/composition r=−0.52, L5→D/dispatch r=+0.40, L6→I/selection r=−0.45,
L7→C/routing r=+0.29, L8→W/duplication r=−0.58, L9→B/composition r=+0.55). Flips are
spatially clustered (vertical autocorr 0.83-0.88), column-structured (input features drive
patterns), cross-layer independent, and uniform within a layer (collective lattice mode,
CV 0.02-0.09). Layer 4 is the largest "dune" (32.5% flipped, 5× more than layer 9).

Current TD flips by confidence threshold — incoherent and blunt. **Crystal-coherent TD**
would flip by eigenplane per layer: each batch is one coherent holographic exposure. L4
corrects all B-routing, L5 corrects D-dispatch, L6 corrects I-selection, etc. GD receives
a clean, single-eigenplane signal; Adam decay is surgical per eigenplane rather than
mixing combinators. See `results/td-topology/`.

### Flip interval

**Rule: flip_interval ≥ 10.** TD accumulates gradient moments every step
but only commits topology changes every N steps.

**Why:** Every-step flipping causes gnorm escalation (11→20→38→113 in
40 steps) and CE increase (8.2→10.3). GD can never adapt to continuous
topology changes — Adam's moments are permanently stale.

Current setting: `flip_interval=20` (phase 2, from step 1500 folded).
Prior: `flip_interval=10` (phase 1, worked but 20 gives better
accumulation).

### Moment reset after flips

**Rule: Reset TD moments for flipped positions only.** After committing
flips, the gradient landscape changed at those positions. Accumulated
direction and magnitude are stale.

Implementation: surgical per-position zero. Positions that didn't flip
keep their EMA — don't throw away good information.

### Global budget competition

**Rule: All modules compete for one global flip budget.**

`flip_rate × total_weights` positions per interval, awarded to the
highest-confidence flips across the entire model. This concentrates
flips where they give the most leverage, instead of spreading them
uniformly.

Don't use per-module top-k — it wastes budget on lukewarm flips in
inactive modules.

### Direct flips for no-block attention

**Rule: Attention delta modules use +1 ↔ -1 direct flips (never zero).**

The no-block invariant requires attention deltas to never contain zero
(prevents dispersal collapse). Standard two-step staging (+1→0→±1) is
incompatible — `_enforce_no_block` resets zeros to +1 after every TD
step, undoing the staging.

FFN deltas (if enabled) still use two-step staging through zero.

### Warmup and confidence

**Rule: `td-warmup=25`, `td-min-confidence=0.3`.**

Warmup lets GD find initial calibration before TD starts flipping.
Min confidence prevents low-signal flips (noise). Currently Q/K/V
projections get zero TD budget — possibly because min_conf filters
them (open question: is 0.3 too aggressive?).

## Known Failure Modes

### 1. Every-step TD flipping → gnorm escalation

**What:** Flipping topology every step causes gradient norm to escalate
exponentially. CE increases instead of decreasing.

**Why:** Adam's moments encode the gradient landscape's shape. Changing
topology every step means the moments are permanently stale. GD chases
a moving target it can never catch.

**Fix:** `flip_interval=10` (or higher). Accumulate gradients for 9
steps, commit flips on step 10, reset moments, repeat.

**Evidence:** gnorm 11→20→21→38→113 in 40 steps, CE 8.2→10.3. Session 148.

### 2. Two-step staging + no-block = Sisyphus loop

**What:** 158M TD flips with ZERO actual plate changes. Delta plates
showed activity but nothing stuck.

**Why:** Two-step staging: +1→0→±1. No-block invariant: attention
deltas must NEVER contain 0. `_enforce_no_block` resets all zeros to +1
after every TD step. Every staging attempt is immediately undone.

**Evidence:** no_block_fixed=77K/step at steady state (21.5% of flips
landing in attention layers).

**Fix:** Attention delta modules use direct +1↔-1 flips (no staging).
FFN deltas keep two-step staging.

### 3. Aliased parameters = 4× gradient overwrite

**What:** `collect_delta_params` returned 280 modules instead of 70.
TD processed each physical module 4 times per step with conflicting
gradients (last write wins).

**Why:** `shared_stride_stack` is Python-referenced by `stack_a`,
`stack_b`, `stack_c`. MLX's `named_modules()` traverses all paths
including aliases, returning the same module under 4 different names.

**Fix:** Deduplicate by `id(mod)` in `collect_delta_params`, keeping
the shortest path. Returns exactly 70 modules.

### 4. Parity gradient cancellation (multi-zone)

**What:** Parity loss stuck at 1.167 for 2000+ steps. Crystal learns
nothing from parity.

**Why:** Zone A wants cos(K,B)=0.08, Zone C wants 0.52. Equal
weighting → net gradient ≈ 0. Eigendecomposition amplifies inter-zone
differences nonlinearly — worse than simple MSE.

**Fix:** `parity_zone_lambdas = (0.0, 1.0, 0.0)` — Zone B only.
Crystal MSE handles 3-zone compromise (linear, well-behaved).
Cross-zone lens rotation handles inter-zone structure.

**General principle:** Nonlinear losses (eigendecomposition, SVD) must
operate on ONE consistent target. Linear losses (MSE) can average
across zones; nonlinear losses cannot.

### 5. Softmax routing → winner-take-all gradient death

**What:** 20/22 dispatch options die permanently. Only one option has
gradient. Embeddings grow without bound.

**Why:** Softmax over many options + unconstrained embeddings = positive
feedback loop. One option captures all weight, others get zero gradient
and fossilize. Rich-get-richer dynamics.

**Fix:** Top-k routing (limit competition) + L2-normalize embeddings
(constrain magnitudes). Same pattern as Switch Transformer.

### 6. Sigmoid gate saturation

**What:** CycleContinue gate locks at 1.0 and never learns.

**Why:** High-norm inputs (‖x‖ ≈ 27.7) produce saturated logits.
After one gradient step, logit ≈ 30, sigmoid gradient ≈ 0, gate is
permanently frozen.

**Fix:** RMSNorm input + tanh(·)×4.0 clamp → gate ∈ [0.018, 0.982],
always learnable. Any sigmoid gate needs normalized input or logit
clamping.

### 7. Missing gradient clipping → embedding divergence

**What:** Embedding weights diverge within ~400 steps.

**Why:** Tied weight matrices (embed = output projection) create
positive feedback loops that are invisible until they explode. Without
gradient clipping, the loop runs away.

**Fix:** `clip_grad_norm_(1.0)`. Always. Not optional.

**Rule:** When porting models between frameworks, always grep the
source training script for `clip_grad` before declaring the port
complete.

## Loss Composition

### Multiplicative AND (not additive OR)

```python
loss = CE × exp(λ × crystal) × (1 + λ_h × holo)
```

**Why multiplicative:** Additive loss `CE + λ*crystal` allows improving
either component independently (OR semantics). A CE improvement that
degrades the crystal still reduces total loss. Multiplicative forces
BOTH to improve simultaneously (AND semantics).

The exponential crystal coupling creates a nucleation well:
- crystal=0: factor=1 (CE runs free)
- crystal=0.01: factor=1.65 (65% amplification)
- crystal=0.05: factor=12× (strong pressure)

The beam MUST find the crystal before CE can improve.

**Parameters:** λ=50 for exp coupling. φ ratio is observed, never
enforced.

### Exponential loss cap

Cap crystal-related losses at exp(max=4.0). Prevents NaN from
extreme early values. The cap is never hit after nucleation.

### NaN rollback

If loss becomes NaN, roll back to the last checkpoint. NaN typically
indicates crystal nucleation failure (the barrier at crystal_loss ≈
0.16 wasn't crossed) or exploding gradients from missing clipping.

## Combinator Bootstrap Ordering

Combinators bootstrap in a fixed dependency order:

```
I (identity/trivial) → K (select) → C (reorder) → B (compose)
```

Higher-order operations can't learn until lower-order ones provide
stable representations to operate on. B needs K and C working before
it can learn composition from compositional prose (relative clauses,
quantifier scope).

Evidence: In v11 training, B dispatch stayed flat at 1.8% while B-type
signals rose in integrate channel (5.8%→47.6%). The same staircase
pattern appears across versions: simple→complex, each level waits for
the one below to stabilize.

## Calibration Convergence

**GD converges fast once topology is set.** 100 steps achieves 87% of
full convergence (3000 steps). The last 2900 steps add only 13%.

Breakdown:
- Geometry (crystal loss) converges in ~5 steps
- CE (input-output mapping) converges in ~100 steps
- Both needed: geometry alone gives crystal but 2.7% accuracy

**Implication:** After each fold, 100 steps of GD is sufficient to
recalibrate continuous parameters. The expensive part is TD correcting
topology, not GD fitting to it.

## Evaluation Protocol

**Script:** `scripts/v14/eval_ppl.py`
**Held-out shards:** 54–59
**Metrics:** CE (nats) and PPL (perplexity) with standard deviation
**Baseline:** Random CE = 12.42 (ln(248320))

Run eval at each fold point and at regular intervals (every 500 steps)
to track convergence and detect overfitting (train-eval gap).

Healthy training: train-eval gap slightly positive (0.1–0.5 nats).
Negative gap = overfitting on continuous params.

## Quick Reference

| Parameter | Value | Why |
|-----------|-------|-----|
| flip_interval | 10–20 | GD needs time to adapt between topology changes |
| td-warmup | 25 | Let GD find initial calibration first |
| td-min-confidence | 0.3 | Prevent low-signal noise flips |
| td-flip-rate | 0.001 | Budget per interval (global competition) |
| grad_clip | 1.0 | Not optional — prevents embedding divergence |
| loss coupling λ | 50 | Exponential crystal nucleation well |
| loss cap | 4.0 | Prevents NaN from extreme early crystal values |
| batch_size | 1 | Memory-bandwidth-bound; B=2 is 18% slower |
| accum_steps | 8 | Effective batch via gradient accumulation |
| parity zones | (0,1,0) | Zone B only — multi-zone cancels gradients |
```

### Thinking

 I'm getting a clearer picture of TernaryDescent now and want to discuss with Michael what direction to take next. He's pivoting away from the audit work to revisit this project, which makes sense given that the recent validity audits have been picking apart crystal claims and marking many as over-read or unsupported.

But the core substrate holds up: sign carries roughly 65-79% of the operation structure topologically, ternary remains viable, and the low-rank spectral head is real. This validates the fundamental premise of TernaryDescent as a training mechanism for ternary-weighted topologies. The known oscillation problem from session 191 is still there—TD keeps 94% of positions mutable, which prevents phase transitions—but the audit findings suggest that if signs genuinely carry the routing and operations, then gradient descent on signs should be able to recover the program structure. The key open question is whether we can train with TD alone and skip Adam entirely, letting the gradient decompose naturally into routing updates versus calibration. I should ask Michael what angle he wants to explore first.

## Assistant

I have the full TernaryDescent picture now. Let me connect it to where the project actually stands today, because the audit changes the stakes.

## TernaryDescent — where it stands

**What it is** (s136): an Adam-equivalent optimizer for discrete ternary `{−1,0,+1}` weights, running on the *same* backward pass as Adam. The gradient is decomposed:
- **routing** (descent opposes current sign → flip the sign) → TernaryDescent
- **calibration** (descent agrees → adjust magnitude) → Adam on gamma

Architecture is the **delta plate**: `effective = base ⊙ delta`, base = frozen teacher crystal etch, delta = TD-trained, foldable losslessly (`new_base = base ⊙ delta`, ternary × ternary = ternary, exact).

**The wall it hit** (s191 — `td-oscillation-problem.md`): TD kept **94.5% of positions perpetually mutable**; oscillation rate *increased* with flip count. The topology never held still long enough for GD to find the next basin, so the v15-td student stalled at loss 6.7–6.8 — pre-phase-transition. The model found the easy B-dominant path (dense FFN + relay attention) and couldn't transition to K (the gating/discard phase).

**The fixes that landed** (s177 — full S2 anti-oscillation stack): structural zeros (30%), `no_block=True` (±1 only, no zero-staging — fixing the Sisyphus loop), per-position cooldown+backoff, per-row Adam moment decay, `flip_interval=20`, global budget competition. Plus **trace-guided etching** — etch for *function* (match teacher opcode trace) not *form* (weight signs), guided TD that flips toward target opcode projections.

## Why this is worth revisiting *now*

The validity audit (s203–212) just strengthened TD's load-bearing premise, twice:

- **#1 (s203):** sign-topology is real and lives specifically in `gate_proj` (the router), sharpening with scale (z→+271 @14B). The routing register — exactly TD's domain.
- **#12f (s211–212):** sign carries **~65–79% of the operation discrimination**, and it's **scale-stable** to 32B (plateau ~0.7, not climbing to 1.0). Magnitude shapes the raw geometry; sign carries the *operations*.

So the case for "you can train a ternary weighted topology" is empirically firmer than when TD was last touched at s191/s177 — but the same audit also keeps surfacing the meta-pattern: **substrate real, crisp story over-read.** TD has never itself been run through a controlled comparison.

Before I pick a direction, what angle are you exploring?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which TernaryDescent angle do you want to explore this session?",
  "options": [
    {
      "label": "Does TD actually beat baselines? (controlled)",
      "description": "Bring the audit's rigor to TD itself: TD vs STE vs random-sign-flip null, small model, matched budget. Honest answer to 'does gradient-on-signs train a topology?'"
    },
    {
      "label": "Solve the oscillation wall",
      "description": "Revisit the s191 oscillation trap with the s177 S2 stack + audit insight (sign=routing). Test punctuated-equilibrium / conviction-gating on a small from-scratch run."
    },
    {
      "label": "TD-only, skip Adam",
      "description": "Open question #4: if sign carries ~70% of operations (audit-confirmed), can TD train the topology with fixed/minimal gamma? Decompose what Adam actually adds."
    },
    {
      "label": "Theory / connect to audit findings",
      "description": "Synthesize TD against the two-registers + manifold-topology results. No new run — sharpen the design from what we now know is real."
    }
  ]
}
```

**Summary:** Q: Which TernaryDescent angle do you want to ex...

**Output:**
```
User answered: I want to understand our current system, I have an idea.
```

### Thinking

 I need to ground this in the actual codebase before explaining the system to Michael, so I'm going to examine the implementation files directly—starting with the most recent v15 scripts like model.py, td.py, train.py, and etch.py to see how TernaryDescent actually works in practice, and maybe compare against v14 to understand what's changed.

## Assistant

Good — let me ground this in the actual code, not just the knowledge pages. Let me read the current implementation.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && wc -l scripts/v15/*.py scripts/v14/td.py scripts/v13/td.py 2>/dev/null | sort -n",
  "operation": "status",
  "summary": "size td files"
}
```

**Summary:** $ wc -l scripts/v15/*.py scripts/v14/...

**Output:**
```
Exit code: 0
Stdout:
1 scripts/v15/__init__.py
     171 scripts/v15/generate.py
     205 scripts/v15/crystal.py
     233 scripts/v15/build_student_trace_basis.py
     249 scripts/v15/load_checkpoint.py
     288 scripts/v15/data.py
     292 scripts/v15/diagnose_pipeline.py
     293 scripts/v15/scan.py
     301 scripts/v15/neuron_modes.py
     305 scripts/v15/apply_zeros.py
     307 scripts/v15/stack_vsm.py
     324 scripts/v15/config.py
     378 scripts/v15/prepare_etch.py
     525 scripts/v15/v15model.py
     553 scripts/v15/build_trace_basis.py
     555 scripts/v15/attention.py
     563 scripts/v15/crystal_base.py
     598 scripts/v15/kernel.py
     653 scripts/v15/components.py
     661 scripts/v15/etch.py
     846 scripts/v15/td.py
     897 scripts/v15/model.py
     931 scripts/v15/extract_qwen36.py
    1225 scripts/v13/td.py
    1410 scripts/v15/train_td.py
    1615 scripts/v15/extract.py
    1685 scripts/v14/td.py
    1685 scripts/v15/td_delta.py
    2152 scripts/v15/train.py
    2656 scripts/v15/ternary.py
   22557 total
```

### Thinking

 I'm looking at the codebase structure — the TD optimizer and model's delta plate mechanism are the key pieces to understand. Michael seems to be signaling that he wants me to help him grasp the current system before he shares his idea, so I should focus on explaining how these core components work together.

## Assistant

Large system. The heart of it is the TD optimizer and the delta-plate model. Let me read both.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/td.py"
}
```

**Summary:** Reading td.py (0-2000)

**Output:**
```
"""TernaryDescent for v15 — gradient-informed sign flipping for float ternary plates.

Port of v14/td.py adapted for v15's architecture where plates are float
arrays with values in {-1, 0, +1} (not packed uint32).

Core idea: gradients tell you which direction reduces loss. For ternary
weights, you can't take fractional steps. Instead, accumulate gradient
evidence over many steps (like Adam's moments) and flip when the signal
is strong and consistent.

Delta plate architecture:
    effective = base_plate ⊙ delta_plate
    base_plate:  frozen teacher etch
    delta_plate: initialized to +1 (pass-through), trained by TD

    Delta semantics:
        +1 → keep teacher sign here
        -1 → flip teacher sign here
         0 → block this position (staging area)

Session 177. License: MIT.
"""

from __future__ import annotations

import math
from typing import Any

import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# Gradient decomposition: routing vs calibration
# ══════════════════════════════════════════════════════════════════════

def decompose_gradient(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> tuple[mx.array, mx.array, mx.array]:
    """Split gradient into routing and calibration components.

    ROUTING:   gradient fights the topology (sign disagreement)
               → "this route is wrong, change the sign" → TD
    CALIBRATION: gradient agrees with topology (magnitude adjustment)
               → "this route is right, adjust the scale" → Adam (gamma)

    Args:
        grad_effective:   (N, K) float32 — ∂L/∂effective
        effective_signs:  (N, K) float32 — sign(base ⊙ delta), values in {-1,0,+1}

    Returns:
        routing:      (N, K) float32 — gradient component for TD
        calibration:  (N, K) float32 — gradient component for Adam
        routing_mask: (N, K) bool    — True where gradient is routing
    """
    descent_sign = mx.sign(-grad_effective)  # -grad is the descent direction

    is_routing = (
        (descent_sign != effective_signs) | (effective_signs == 0)
    ) & (grad_effective != 0)

    routing = mx.where(is_routing, grad_effective, mx.array(0.0))
    calibration = mx.where(is_routing, mx.array(0.0), grad_effective)

    return routing, calibration, is_routing


def compute_routing_fraction(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> mx.array:
    """Compute per-row routing fraction: what % of each row is routing.

    Returns (N,) float32 in [0, 1]. High = topology is wrong.
    """
    descent_sign = mx.sign(-grad_effective)
    has_gradient = grad_effective != 0
    is_routing = ((descent_sign != effective_signs) | (effective_signs == 0)) & has_gradient
    n_active = mx.sum(has_gradient.astype(mx.float32), axis=-1)
    n_routing = mx.sum(is_routing.astype(mx.float32), axis=-1)
    return n_routing / (n_active + 1e-8)


# ══════════════════════════════════════════════════════════════════════
# TernaryDescent optimizer — v15 (float plates, no packing)
# ══════════════════════════════════════════════════════════════════════

class TernaryDescent:
    """Adam-equivalent optimizer for ternary {-1, 0, +1} weights.

    V15 adaptation: plates are float arrays, not packed uint32.
    Accumulates gradient evidence via EMA. Flips when confident.

    Usage:
        td = TernaryDescent(flip_rate=0.001)

        for step in training:
            loss, grads = value_and_grad(model)(x, y)
            adam.step(continuous_params, grads)
            td_result = td.step(delta_params, training_step=step)
    """

    def __init__(
        self,
        beta1: float = 0.9,
        beta2: float = 0.999,
        flip_rate: float = 0.001,
        warmup_steps: int = 100,
        min_confidence: float = 0.3,
        cooldown_tau: float = 50.0,
        cooldown_backoff: float = 2.0,
        neighbor_width: int = 3,
        flip_interval: int = 20,
    ):
        self.beta1 = beta1
        self.beta2 = beta2
        self.flip_rate = flip_rate
        self._base_flip_rate = flip_rate
        self.warmup_steps = warmup_steps
        self.min_confidence = min_confidence
        self.cooldown_tau = cooldown_tau
        self.cooldown_backoff = cooldown_backoff
        self.neighbor_width = neighbor_width
        self.flip_interval = flip_interval
        assert neighbor_width % 2 == 1
        assert flip_interval >= 1
        self.step_count = 0

        # Per-parameter state: {name: (direction, magnitude)}
        self._state: dict[str, tuple[mx.array, mx.array]] = {}

        # Per-parameter anti-oscillation: {name: (last_flip_step, flip_count)}
        self._flip_history: dict[str, tuple[mx.array, mx.array]] = {}

        # Tracking
        self.last_n_flips = 0
        self.last_n_candidates = 0

    def _get_state(self, name: str, shape: tuple) -> tuple[mx.array, mx.array]:
        if name not in self._state:
            self._state[name] = (mx.zeros(shape), mx.zeros(shape))
        return self._state[name]

    def _get_flip_history(self, name: str, shape: tuple) -> tuple[mx.array, mx.array]:
        if name not in self._flip_history:
            self._flip_history[name] = (
                mx.zeros(shape, dtype=mx.int32),
                mx.zeros(shape, dtype=mx.int32),
            )
        return self._flip_history[name]

    def _compute_cooldown(self, name: str, shape: tuple) -> mx.array:
        """Per-position cooldown ∈ [0, 1]. 0 = just flipped, 1 = fully cooled."""
        last_flip_step, flip_count = self._get_flip_history(name, shape)
        steps_since = mx.maximum(self.step_count - last_flip_step, 0).astype(mx.float32)
        capped_count = mx.minimum(flip_count, 10).astype(mx.float32)
        effective_tau = self.cooldown_tau * (self.cooldown_backoff ** capped_count)
        cooldown = 1.0 - mx.exp(-steps_since / (effective_tau + 1e-8))
        never_flipped = last_flip_step == 0
        return mx.where(never_flipped, mx.array(1.0), cooldown)

    def _update_flip_history(self, name: str, flip_mask: mx.array):
        shape = flip_mask.shape
        last_flip_step, flip_count = self._get_flip_history(name, shape)
        last_flip_step = mx.where(flip_mask, mx.array(self.step_count, dtype=mx.int32), last_flip_step)
        flip_count = flip_count + flip_mask.astype(mx.int32)
        self._flip_history[name] = (last_flip_step, flip_count)

    @staticmethod
    def _row_median_smooth(signal: mx.array, width: int = 3) -> mx.array:
        """Row-wise median filter for spatial smoothing."""
        if width == 1:
            return signal
        N, K = signal.shape
        pad = width // 2
        padded = mx.concatenate([
            mx.zeros((N, pad)), signal, mx.zeros((N, pad))
        ], axis=1)
        windows = mx.stack([padded[:, i:i + K] for i in range(width)], axis=-1)
        sorted_windows = mx.sort(windows, axis=-1)
        return sorted_windows[:, :, pad]

    def step(
        self,
        delta_params: list[tuple[str, mx.array, mx.array, mx.array, bool]],
        training_step: int | None = None,
    ) -> dict[str, Any]:
        """Perform one TernaryDescent step.

        Every call accumulates moments. Flips commit every flip_interval steps.

        Args:
            delta_params: List of (name, delta_float, grad_wrt_effective,
                          base_float, no_block).
                - name: identifier for logging
                - delta_float: (N, K) float32 with values in {-1, 0, +1}
                - grad_wrt_effective: (N, K) float32 — ∂L/∂(base⊙delta)
                - base_float: (N, K) float32 with values in {-1, 0, +1}
                - no_block: if True, skip zero staging (+1 ↔ -1 directly)
            training_step: external step count for flip timing alignment.

        Returns:
            dict with step metrics.
        """
        self.step_count += 1
        per_module: dict[str, dict] = {}

        in_warmup = self.step_count <= self.warmup_steps
        flip_clock = training_step if training_step is not None else self.step_count
        is_flip_step = (
            not in_warmup
            and self.flip_interval > 0
            and flip_clock % self.flip_interval == 0
        )

        # ── Pass 1: Accumulate moments ──
        for name, _delta, grad_eff, _base, _no_block in delta_params:
            direction, magnitude = self._get_state(name, grad_eff.shape)
            direction = self.beta1 * direction + (1 - self.beta1) * grad_eff
            magnitude = self.beta2 * magnitude + (1 - self.beta2) * (grad_eff ** 2)
            self._state[name] = (direction, magnitude)

        if not is_flip_step:
            for name, *_ in delta_params:
                per_module[name] = {"flips": 0, "candidates": 0, "mean_confidence": 0.0}
            self.last_n_flips = 0
            return {
                "step": self.step_count,
                "total_flips": 0,
                "in_warmup": in_warmup,
                "is_flip_step": False,
                "per_module": per_module,
            }

        # ── Pass 2: Score candidates ──
        bc1 = 1 - self.beta1 ** self.step_count
        bc2 = 1 - self.beta2 ** self.step_count

        module_candidates = []
        total_ternary_weights = 0

        for name, delta_float, grad_eff, base_float, no_block in delta_params:
            direction, magnitude = self._state[name]

            dir_corrected = direction / bc1
            mag_corrected = magnitude / bc2

            snr = mx.abs(dir_corrected) / (mx.sqrt(mag_corrected) + 1e-8)
            importance = mx.sqrt(mag_corrected)

            cooldown = self._compute_cooldown(name, grad_eff.shape)
            smoothed_snr = self._row_median_smooth(snr, self.neighbor_width)
            score = smoothed_snr * importance * cooldown

            confident = smoothed_snr > self.min_confidence

            # Desired direction for delta:
            # If gradient says effective should decrease (descent = -grad):
            #   base=+1 → delta should decrease (flip toward -1)
            #   base=-1 → delta should increase (flip toward +1)
            desired_effective = -mx.sign(dir_corrected)
            desired = desired_effective * base_float

            # Valid transitions
            if no_block:
                can_move = (
                    ((delta_float > 0) & (desired < 0)) |
                    ((delta_float < 0) & (desired > 0))
                ) & (base_float != 0)
            else:
                can_move = (
                    ((delta_float > 0) & (desired < 0)) |
                    ((delta_float < 0) & (desired > 0)) |
                    (delta_float == 0)
                ) & (base_float != 0)

            candidates = confident & can_move
            candidate_scores = mx.where(candidates, score, mx.array(0.0))

            total_ternary_weights += delta_float.size

            module_candidates.append({
                "name": name,
                "no_block": no_block,
                "delta_float": delta_float,
                "desired": desired,
                "candidates": candidates,
                "candidate_scores": candidate_scores,
                "snr": snr,
            })

        # ── Pass 3: Holographic etch — equal thin slot per module ──
        global_budget = max(1, int(self.flip_rate * total_ternary_weights))

        module_n_candidates = []
        total_candidates = 0
        n_active_modules = 0
        for mc in module_candidates:
            n_cands = int(mc["candidates"].sum().item())
            module_n_candidates.append(n_cands)
            total_candidates += n_cands
            if n_cands > 0:
                n_active_modules += 1

        if total_candidates == 0:
            for mc in module_candidates:
                per_module[mc["name"]] = {
                    "flips": 0, "candidates": 0, "mean_confidence": 0.0,
                }
            self.last_n_flips = 0
            return {
                "step": self.step_count,
                "total_flips": 0,
                "in_warmup": False,
                "is_flip_step": True,
                "per_module": per_module,
            }

        effective_budget = min(global_budget, total_candidates)
        per_module_slot = max(1, effective_budget // max(n_active_modules, 1))
        total_flips = 0

        for i, mc in enumerate(module_candidates):
            name = mc["name"]
            candidates = mc["candidates"]
            scores = mc["candidate_scores"]
            delta_float = mc["delta_float"]
            desired = mc["desired"]
            no_block = mc["no_block"]
            snr = mc["snr"]

            n_cands = module_n_candidates[i]
            if n_cands == 0:
                per_module[name] = {
                    "flips": 0, "candidates": 0, "mean_confidence": 0.0,
                }
                continue

            module_budget = per_module_slot

            # Find threshold via top-K
            module_scores_flat = scores.reshape(-1)
            n_positive = int((module_scores_flat > 0).sum().item())
            this_budget = min(module_budget, n_positive)

            if this_budget <= 0:
                flip_mask = mx.zeros_like(candidates, dtype=mx.bool_)
            elif this_budget >= n_positive:
                flip_mask = candidates
            else:
                neg_scores = -module_scores_flat
                partitioned = mx.partition(neg_scores, kth=this_budget - 1)
                threshold = float((-partitioned[this_budget - 1]).item())
                flip_mask = candidates & (scores >= threshold)

            if not flip_mask.any().item():
                per_module[name] = {
                    "flips": 0,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                }
                continue

            # Compute new delta values
            if no_block:
                # Direct flip: +1 ↔ -1
                new_delta = mx.where(flip_mask, -delta_float, delta_float)
            else:
                # Two-step staging: +1 → 0 → -1
                new_delta = mx.where(
                    flip_mask & (delta_float != 0),
                    mx.array(0.0),                   # non-zero → zero (stage)
                    mx.where(
                        flip_mask & (delta_float == 0),
                        mx.sign(desired),             # zero → ±1 (commit)
                        delta_float,                   # no flip
                    ),
                )

            flip_occurred = (new_delta != delta_float)
            n_flips = int(flip_occurred.sum().item())
            total_flips += n_flips

            if n_flips > 0:
                self._update_flip_history(name, flip_occurred)

                per_module[name] = {
                    "flips": n_flips,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                    "new_delta": new_delta,  # caller applies to model
                    "flip_occurred": flip_occurred,
                }
            else:
                per_module[name] = {
                    "flips": 0,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                }

        # ── Surgical moment reset at flipped positions ──
        if total_flips > 0:
            for mc in module_candidates:
                name = mc["name"]
                info = per_module.get(name, {})
                if info.get("flips", 0) > 0 and "flip_occurred" in info:
                    flip_mask = info["flip_occurred"]
                    if name in self._state:
                        direction, magnitude = self._state[name]
                        direction = mx.where(flip_mask, mx.array(0.0), direction)
                        magnitude = mx.where(flip_mask, mx.array(0.0), magnitude)
                        self._state[name] = (direction, magnitude)

        self.last_n_flips = total_flips
        self.last_n_candidates = total_candidates
        return {
            "step": self.step_count,
            "total_flips": total_flips,
            "in_warmup": False,
            "is_flip_step": True,
            "per_module": per_module,
            "etch_active_modules": n_active_modules,
            "etch_slot_size": per_module_slot,
            "etch_global_budget": global_budget,
            "etch_total_candidates": total_candidates,
        }

    def reset_moments(self):
        """Reset all moment accumulators but keep flip history."""
        self._state.clear()

    def reset(self):
        """Full reset: moments + flip history + step count."""
        self._state.clear()
        self._flip_history.clear()
        self.step_count = 0
        self.last_n_flips = 0
        self.last_n_candidates = 0


# ══════════════════════════════════════════════════════════════════════
# Crystal Thermometer — oscillation = temperature, settled = frozen
# ══════════════════════════════════════════════════════════════════════

class CrystalThermometer:
    """Measures the crystal temperature: how much topology is still moving.

    Every flip step, records which positions flipped. Over time, builds
    a per-position history that reveals:

      frozen:      never a candidate           → irreducible, done
      settled:     flipped before, quiet now    → found normal form
      active:      flipped recently             → still reducing
      oscillating: flipped >1× in recent window → 50/50, ambiguous

    Temperature = active_frac. When it → 0, the delta is done.
    Oscillation_frac = fraction of active positions that are flip-flopping
    (the "noise floor" — positions that will never settle).

    Usage:
        thermo = CrystalThermometer()

        # After each TD step:
        thermo.record(td_result, step)

        # At log intervals:
        temp = thermo.temperature(step)
        log(f"crystal_temp={temp['temperature']:.4f}")
    """

    def __init__(self, recent_window: int = 100):
        """
        Args:
            recent_window: steps to look back for "recent" activity.
                          ~5× flip_interval is a good default.
        """
        self.recent_window = recent_window
        self._modules: dict[str, dict[str, "np.ndarray"]] = {}

    def _ensure(self, name: str, shape: tuple):
        if name in self._modules:
            return
        import numpy as np
        self._modules[name] = {
            "flip_count": np.zeros(shape, dtype=np.int32),
            "last_flip_step": np.zeros(shape, dtype=np.int32),
        }

    def record(self, td_result: dict, step: int):
        """Record flip data from a TD step. Call after every flip step."""
        import numpy as np

        if not td_result.get("is_flip_step", False):
            return

        for name, info in td_result.get("per_module", {}).items():
            flip_occurred = info.get("flip_occurred")
            if flip_occurred is None:
                continue

            flip_arr = np.asarray(flip_occurred).astype(bool)
            self._ensure(name, flip_arr.shape)
            m = self._modules[name]
            m["flip_count"] += flip_arr.astype(np.int32)
            m["last_flip_step"] = np.where(
                flip_arr, step, m["last_flip_step"]
            )

    def temperature(self, step: int) -> dict:
        """Compute crystal temperature and per-module breakdown.

        Returns:
            dict with:
              temperature:      float — fraction of all positions active recently
              oscillation_frac: float — of active positions, fraction oscillating
              settled_frac:     float — of ever-flipped, fraction now quiet
              frozen_frac:      float — fraction never flipped
              per_module:       dict[name → {temp, osc, settled, n_flips}]
              total_flips:      int — cumulative flips across all positions
        """
        import numpy as np

        if not self._modules:
            return {
                "temperature": 0.0, "oscillation_frac": 0.0,
                "settled_frac": 0.0, "frozen_frac": 1.0,
                "per_module": {}, "total_flips": 0,
            }

        total_positions = 0
        total_active = 0
        total_oscillating = 0
        total_settled = 0
        total_frozen = 0
        total_ever_flipped = 0
        total_flips = 0
        per_module = {}

        for name, m in self._modules.items():
            fc = m["flip_count"]
            lfs = m["last_flip_step"]
            n = fc.size

            ever_flipped = fc > 0
            recent = lfs >= (step - self.recent_window)
            active = ever_flipped & recent
            oscillating = (fc > 1) & recent
            settled = ever_flipped & ~recent
            frozen = ~ever_flipped

            n_active = int(active.sum())
            n_osc = int(oscillating.sum())
            n_settled = int(settled.sum())
            n_frozen = int(frozen.sum())
            n_ever = int(ever_flipped.sum())
            n_flips = int(fc.sum())

            per_module[name] = {
                "temp": n_active / max(n, 1),
                "osc": n_osc / max(n_active, 1),
                "settled": n_settled / max(n_ever, 1),
                "n_flips": n_flips,
            }

            total_positions += n
            total_active += n_active
            total_oscillating += n_osc
            total_settled += n_settled
            total_frozen += n_frozen
            total_ever_flipped += n_ever
            total_flips += n_flips

        return {
            "temperature": total_active / max(total_positions, 1),
            "oscillation_frac": total_oscillating / max(total_active, 1),
            "settled_frac": total_settled / max(total_ever_flipped, 1),
            "frozen_frac": total_frozen / max(total_positions, 1),
            "per_module": per_module,
            "total_flips": total_flips,
        }

    def hottest_modules(self, step: int, top_n: int = 5) -> list[tuple[str, float]]:
        """Return the top_n modules by temperature (most active)."""
        t = self.temperature(step)
        ranked = sorted(
            t["per_module"].items(),
            key=lambda x: -x[1]["temp"],
        )
        return [(name, info["temp"]) for name, info in ranked[:top_n]]


# ══════════════════════════════════════════════════════════════════════
# Helper: apply TD results to model
# ══════════════════════════════════════════════════════════════════════

def get_affected_gamma_rows(
    model: "TensorStatechart",
    td_result: dict,
) -> dict[str, set[int]]:
    """Identify which gamma rows are affected by TD flips.

    When TD flips delta[i, j], the effective weight for row i changes.
    Adam's moments for gamma[i] are now stale — they encode gradient
    history for the old sign topology. Without decay, Adam pushes
    gamma in the wrong direction for ~10 steps (1/β₁).

    Returns:
        dict mapping gamma parameter path → set of affected row indices.
        Keys match the flattened parameter tree used by the optimizer.
        e.g. {"strides.5.ffn.gate_plate.gamma1": {12, 45, 200, ...}}
    """
    affected: dict[str, set[int]] = {}
    delta_params = model.collect_delta_params()
    name_to_plate = {name: (plate, which) for name, plate, which in delta_params}

    for name, info in td_result.get("per_module", {}).items():
        flip_occurred = info.get("flip_occurred")
        if flip_occurred is None or info.get("flips", 0) == 0:
            continue
        if name not in name_to_plate:
            continue

        plate, which = name_to_plate[name]

        # flip_occurred is (N, K). A row is affected if ANY position in it flipped.
        import numpy as np
        flip_arr = np.asarray(flip_occurred)
        row_affected = np.any(flip_arr, axis=1)
        rows = set(int(i) for i in np.where(row_affected)[0])

        if not rows:
            continue

        # Map delta name to the corresponding gamma parameter path.
        # delta name: "strides.5.ffn.gate_plate.delta1"
        # gamma name: "strides.5.ffn.gate_plate.gamma1"
        gamma_attr = "gamma1" if which == "delta1" else "gamma2"
        gamma_path = name.replace(which, gamma_attr)
        affected[gamma_path] = rows

    return affected


def decay_adam_for_affected_rows(
    optimizer: "optim.Optimizer",
    model: "nn.Module",
    affected: dict[str, set[int]],
    decay_factor: float = 0.1,
) -> int:
    """Decay Adam moments for gamma rows affected by TD flips.

    For each affected gamma row, multiply Adam's first and second
    moments by decay_factor. This prevents Adam from pushing gamma
    in the wrong direction after the topology changed underneath it.

    decay_factor = 0.1 means 90% of the stale momentum is removed.
    The remaining 10% provides a gentle prior toward the pre-flip
    direction, which is usually close to correct (most flips are
    small corrections, not reversals).

    Args:
        optimizer: The AdamW optimizer.
        model: The model (for parameter tree alignment).
        affected: Output of get_affected_gamma_rows().
        decay_factor: Multiply moments by this (0.0 = full reset, 1.0 = no decay).

    Returns:
        Number of gamma rows decayed.
    """
    import mlx.nn as nn

    if not affected:
        return 0

    total_decayed = 0

    # The optimizer state is indexed by the parameter tree structure.
    # We need to find the optimizer state entry for each affected gamma.
    # MLX optimizer state is a nested structure mirroring the model tree.
    # We walk the flattened state to find matching paths.
    flat_state = dict(nn.utils.tree_flatten(optimizer.state))

    for gamma_path, rows in affected.items():
        # Adam stores state as (step, m, v) or similar.
        # Look for keys containing the gamma path + moment suffixes.
        for state_key, state_val in flat_state.items():
            if gamma_path not in state_key:
                continue
            if state_val.ndim != 1:
                continue
            # This is a 1D state array matching a gamma parameter.
            # Decay the affected rows.
            for row in rows:
                if row < state_val.shape[0]:
                    state_val = state_val.at[row].multiply(decay_factor)
            flat_state[state_key] = state_val
            total_decayed += len(rows)

    # Write back (MLX optimizer state is mutable, but we modified via .at[])
    # The tree_unflatten would be needed for nested state, but since we
    # modified in-place via the flat view, evaluate to commit.
    if total_decayed > 0:
        import mlx.core as mx
        mx.eval(list(flat_state.values()))

    return total_decayed


def apply_td_flips(
    model: "TensorStatechart",
    td_result: dict,
) -> int:
    """Apply flip results from TD step back to the model's delta plates.

    Walks td_result["per_module"], finds entries with "new_delta",
    and writes them back to the corresponding plate module.

    Returns total number of flips applied.
    """
    total = 0
    delta_params = model.collect_delta_params()
    name_to_plate = {name: (plate, which) for name, plate, which in delta_params}

    for name, info in td_result.get("per_module", {}).items():
        if "new_delta" not in info:
            continue
        if name not in name_to_plate:
            continue

        plate, which = name_to_plate[name]
        new_delta = info["new_delta"]
        mx.eval(new_delta)
        setattr(plate, which, new_delta)
        total += info.get("flips", 0)

    return total


def collect_td_step_params(
    model: "TensorStatechart",
    grads: dict,
    no_block: bool = False,
) -> list[tuple[str, mx.array, mx.array, mx.array, bool]]:
    """Build the delta_params list that TD.step() expects.

    Walks the model's delta plates and matches gradients from the
    flattened grad tree. For each delta plate, computes the gradient
    w.r.t. the effective weight (plate ⊙ delta).

    The gradient w.r.t. effective comes from the loss backprop through
    the matmul. Since the forward path uses:
        out = (x @ effective.T) * gamma
    the gradient ∂L/∂effective is available through the chain rule.

    For v15's float plates, the effective weight is plate * delta.
    The gradient ∂L/∂(plate*delta) w.r.t. delta is:
        ∂L/∂delta[i,j] = ∂L/∂effective[i,j] * plate[i,j]
    But TD wants ∂L/∂effective, not ∂L/∂delta. The base_float tells
    TD how to interpret the direction.

    Args:
        model: TensorStatechart with delta plates enabled.
        grads: Flattened gradient dict from value_and_grad.
        no_block: Whether to use direct flips (no zero staging).

    Returns:
        List of (name, delta_float, grad_effective, base_float, no_block)
        suitable for TernaryDescent.step().
    """
    flat_grads = dict(nn.utils.tree_flatten(grads))
    result = []

    for name, plate, which in model.collect_delta_params():
        delta_val = getattr(plate, which)  # (N, K) float {-1,0,+1}
        base_attr = "plate1" if which == "delta1" else "plate2"
        base_val = getattr(plate, base_attr)  # (N, K) float {-1,0,+1}

        # The gradient key in the flattened tree matches the delta path.
        # But since delta is inside stop_gradient in the forward pass,
        # there is no direct gradient for delta. Instead, we need the
        # gradient w.r.t. the matmul input (the effective weight).
        #
        # Strategy: use the gradient of the gamma-scaled output as a proxy.
        # The gamma gradient tells us how the output wants to change.
        # Combined with the input activation statistics, this gives us
        # the effective weight gradient.
        #
        # However, the cleaner approach for v15 is to compute the
        # trace loss gradient directly w.r.t. the effective weight.
        # For now, we use the routing component of whatever gradient
        # is available for the effective weight positions.
        #
        # Placeholder: use a zero-gradient if no matching grad found.
        # The training loop in train.py will compute proper gradients
        # via a separate backward pass that includes the delta.
        grad_key_candidates = [
            name.replace(".delta1", ".plate1").replace(".delta2", ".plate2"),
            name,
        ]

        grad_eff = None
        for gk in grad_key_candidates:
            if gk in flat_grads:
                grad_eff = flat_grads[gk]
                break

        if grad_eff is None:
            # No gradient available — skip this param
            continue

        if grad_eff.shape != delta_val.shape:
            continue

        result.append((name, delta_val, grad_eff, base_val, no_block))

    return result


# ══════════════════════════════════════════════════════════════════════
# Fold helper
# ══════════════════════════════════════════════════════════════════════

def fold_and_reset(
    model: "TensorStatechart",
    td: TernaryDescent,
) -> None:
    """Fold all delta plates into base and reset TD state.

    The standard inter-phase operation:
        1. new_plate = plate ⊙ delta (lossless consolidation)
        2. delta → all +1 (pass-through)
        3. TD moments → zero (gradient landscape changed)
        4. TD flip history → preserved (cooldown tracks physical positions)

    After fold, the model produces identical outputs but the delta
    is reset for the next round of TD corrections.
    """
    model.fold_delta_plates()
    td.reset_moments()
```

### Thinking

 I've got a solid grasp of the TD optimizer and the delta-plate mechanism now—how the effective weights are computed through the base and delta interaction, and how the forward pass flows through the system. Rather than diving deeper into every component, I should give Michael a clear picture of how everything connects end-to-end so we're on the same page before he shares his idea.

The current system trains a delta-plate ternary model where the effective weights come from composing a frozen base (the teacher crystal etch) with a trainable delta layer, both ternary. There are also mirror plates with continuous gamma scalars for the ENRICH layers. On each backward pass, two optimizers work in tandem: Adam handles the continuous parameters like gamma and norms, while the TD optimizer routes the ternary deltas. The gradient decomposition splits the loss signal—calibration flows to Adam when the descent direction aligns with the current sign, and routing flows to TD when they oppose. The TD mechanics use Adam-like moment tracking with exponential moving averages for both direction and magnitude.

The confidence metric (signal-to-noise ratio) determines when to flip a position, gated by cooldown and a global budget. Flips commit every 20 steps with surgical moment resets at flipped positions. The anti-oscillation stack uses structural zeros, attention-only constraints, cooldown with backoff for chronic oscillators, per-row moment decay after flips, and holographic etch to distribute the budget fairly across modules. The CrystalThermometer tracks how many positions are still actively flipping—when temperature drops to zero, the system folds: composing base and delta into a new base, resetting delta to all +1s, and clearing the TD moments to start fresh. Instead of training on raw next-token prediction, trace-guided etching matches the teacher's opcode trace per layer using low-dimensional projections, steering the TD flips toward those target opcodes. The core blocker remains the oscillation problem—TD keeps 94% of positions mutable, which prevents the phase transitions needed to escape the plateau. There's also a subtle implementation detail: since delta sits inside a stop_gradient in the forward pass, there's no direct gradient flow, so the training loop computes it via a separate backward pass using the batched trace gradient.

I want to lay this out clearly for Michael—he knows the system and just needs confirmation we're aligned before sharing his idea, so I should be precise about where the known walls are, since his thinking probably addresses one of them.

## Assistant

I've now read the core (`v15/td.py`) end-to-end. Here's the current system as it actually exists in code — so we're working from the same map.

## The current TernaryDescent system

**The artifact being trained — the delta plate:**
```
effective = base ⊙ delta
  base  : frozen teacher crystal etch, ternary {−1,0,+1}
  delta : trainable, ternary {−1,0,+1}, init +1 (pass-through)
  (+ 2-mirror: plate1/plate2 each with delta1/delta2, gamma1/gamma2 continuous)
```
Delta semantics: `+1` keep teacher sign · `−1` flip it · `0` block (staging — FFN only). **Fold** is lossless: `new_base = base ⊙ delta` (ternary×ternary=ternary, exact), then delta→+1, reset moments, iterate.

**Two optimizers, one backward pass** — the gradient gets split (`decompose_gradient`):
- descent direction *opposes* current sign → **routing** → TernaryDescent flips the bit
- descent direction *agrees* → **calibration** → Adam adjusts the per-row gamma

**TD mechanics** (Adam-shaped, but the "step" is a discrete flip):
- `direction` = EMA(grad, β1=0.9), `magnitude` = EMA(grad², β2=0.999)
- **confidence = SNR = |direction| / √magnitude** — high SNR means the gradient *consistently* says flip; oscillating gradient (CE vs crystal disagree) self-suppresses
- flips commit every `flip_interval=20` steps (accumulate in between); global budget = `flip_rate × total_weights`, top-scored flips across all modules compete; surgical moment-reset only at flipped positions

**The S2 anti-oscillation stack** (each layer catches what the prior misses):
`structural_zeros(30%)` → `no_block` (±1 only, no zero-staging — kills the Sisyphus loop) → per-position `cooldown(τ=50) × backoff(2×)` (chronic oscillators freeze themselves) → per-row Adam moment decay after a flip → holographic etch (equal slot/module) → `flip_interval=20` + `warmup=100`.

**The CrystalThermometer**: classifies every position as frozen / settled / active / oscillating. **Temperature = active fraction**; → 0 is the fold signal.

**Trace-guided variant**: instead of (or alongside) next-token loss, match the teacher's **opcode trace** per layer — a low-dim (4–12 combinator) projection — and flip TD *toward* the target opcode. Etch for function, not form.

## Two things to flag (likely where your idea lands)

1. **The known wall (s191):** TD keeps ~94% of positions perpetually mutable, and oscillation *rises* with flip count. The topology never holds still long enough for GD to find the next basin → the student stalls pre-phase-transition (can't transition from B-dominant dense to K-gated sparse). The whole S2 stack exists to fight this.

2. **A subtle implementation seam:** delta lives inside `stop_gradient` in the normal forward path, so there is **no direct ∂L/∂delta**. TD's gradient comes from a *separate* batched backward pass (`collect_td_step_params` even has a placeholder/proxy fallback). The "gradient" driving the flips isn't the main NTP gradient — it's reconstructed.

That's the system. What's your idea?

## User

What if instead of using a proxy, we just calculate loss directly using all 3 signs, and take the one that improves loss the most?


### Thinking

 Michael's suggesting we skip the gradient-based approach entirely and instead try all three sign values at each position, picking whichever one reduces the loss the most. It's more of a direct coordinate descent over the ternary alphabet rather than relying on gradient estimates and EMA smoothing. I'm considering the tradeoffs here—it's computationally more expensive per step but potentially more robust since we're directly optimizing what we care about.

The naive version would be catastrophically expensive: 124.5M positions × 3 forward passes each is infeasible. But there's a smarter angle—for linear layers, the loss change from flipping a single weight is directly computable without a full forward pass, since the output change is just the weight delta times the input activation. That makes it much more tractable, though we'd still need to be selective about which candidates we evaluate.

This actually maps onto a well-established technique family: OBD/OBS and modern post-training quantization methods like GPTQ and AWQ. Those methods solve the same problem—pick the rounding or quantization that minimizes loss—but they do it by measuring layer-local reconstruction error rather than global loss, because global loss per-position is still too expensive. The gradient gives you the linear proxy (which is what TD already uses), but going beyond that to capture nonlinear effects requires rerunning the forward pass from that layer onward, which is why the scalable versions focus on layer-local error instead.

The project already has the machinery for this kind of layer-local targeting through trace-guided etching and score-matching compression, so the approach fits naturally into what's already there. The real appeal of evaluating all three signs exactly is that it guarantees monotonicity—you only flip when it actually reduces loss, which eliminates the oscillation problem entirely. TD's whole anti-oscillation machinery (cooldown, backoff, thermometer) is trying to approximate the monotonicity that exact loss evaluation gives you for free. And since the ternary alphabet is so small, evaluating all three options per-position is cheap compared to continuous optimization.

The hard parts are ranking which positions to evaluate (use gradient scoring to propose candidates, then exact loss-eval to accept), handling interactions when flipping multiple positions simultaneously (greedy one-at-a-time is safe but slow; batched flips need Hessian-based error compensation), and choosing the right loss function (global NTP loss is expensive to replay, but layer-local reconstruction error is cheap and already decomposable per-position).

Including 0 as a ternary option unifies sparsification with the sign decision — zeroing a weight becomes a functional choice rather than heuristic. For the math: in a linear layer, each weight position (i,j) only affects output column i, so the loss contribution is a quadratic function in the weight value that I can evaluate exactly at the three ternary candidates.

The key insight is that computing the loss-delta for all positions and all three sign values requires just one matrix multiplication (residual transposed times the calibration data) plus elementwise operations — no per-position forward passes needed. This is the same principle behind OBQ/GPTQ. The gradient-only proxy captures the linear term, but for ternary quantization the second-order curvature term is substantial since the step size between values can be large, which is why exact evaluation beats gradient-based approximation for discrete weights.

Since we only accept flips that reduce the layer-local loss, the process is monotone by construction — the oscillation problem vanishes. The approach is layer-local rather than global, but that's actually an advantage: it's computationally cheap and aligns with the trace-guided direction the project has already validated. The main trade-off is handling simultaneous flips, which either requires sequential updates with compensation or accepting that batched greedy is approximate.

This essentially brings TD into the OBQ/GPTQ family, which is worth highlighting as independent validation of the same core principle. The empirical test is straightforward: same proposal set, but compare gradient-proxy acceptance against exact-loss-eval acceptance, measuring loss trajectory and oscillation rates. I should be careful to frame this as a layer-local quadratic reconstruction claim — the closed-form is exact for that specific loss, not necessarily for the full downstream task.

This also connects to existing work: the score-matching approach from the validated research, the layer reconstruction ideas from prior explorations, and the s208 finding that layer-local trajectory objectives fix the degeneracy problem that endpoint-only losses create. So exact-eval on a layer-local target aligns with what the audit already showed works.

Now I'm verifying the math to make sure it's sound before I present it. For a single weight change from a to v, the loss change breaks into a linear term (the gradient contribution) and a quadratic curvature term. The key insight is that computing this for all positions and all three ternary options requires just one matrix multiplication of the residuals against the input activations—no per-position forward passes needed. The linear term is what gradient-based proxies already capture, but the quadratic term is what they miss, and for ternary quantization with large steps, that curvature matters. This is exactly what dissolves the oscillation: you only flip a weight if the exact loss actually improves.

I should write this up clearly and offer to prototype it as a controlled experiment if they want to see it in action.

## Assistant

That's the right instinct, and it's stronger than it first looks. Let me reason through it carefully, because there's a feasibility trap and then a way around it that turns the idea into exactly the missing piece.

## The naive reading is infeasible — but you don't need it

"Run a forward pass for each of the 3 signs at each position" is ~124M positions × 3 = catastrophic. But that's not actually required. For the thing we care about, **the exact loss-delta for all positions and all 3 signs is one matmul** — no per-position forwards.

## The math (layer-local reconstruction target)

Take one linear layer, effective ternary weight `W`, per-row gamma `γ`, a calibration batch `X` (n tokens × d_in), teacher target `T`. Layer loss `L = ‖γ⊙(X@Wᵀ) − T‖²`. Current residual `R = γ⊙(X@Wᵀ) − T`.

Changing one weight `W[i,j]` from its current value `a` to a candidate `v` shifts only output column `i`, by `(v−a)·X[:,j]`. So:

```
ΔL_ij(v) = 2·γ_i·(v−a)·⟨R[:,i], X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²
            └─────── linear ───────┘        └────── curvature ──────┘
```

- `⟨R[:,i], X[:,j]⟩` for **all** i,j at once = `Rᵀ @ X` — **one matmul**, same shape as W.
- `‖X[:,j]‖²` is a precomputed d_in-vector; `γ_i` a d_out-vector; `a` is W; `v ∈ {−1,0,+1}`.

So you evaluate all three candidate losses elementwise across the whole weight matrix and `argmin` over `{−1,0,+1}`. Cheap and exact.

## Why this is precisely what's been missing

Look at the linear term: `2γ_i⟨R[:,i],X[:,j]⟩` **is the gradient** of the layer loss w.r.t. W. That's exactly what TD's gradient-EMA proxy already uses. The new part is the **curvature term `γ²(v−a)²‖X[:,j]‖²`** — which the gradient-only proxy throws away.

For *continuous* weights with tiny steps, dropping curvature is fine (that's why Adam works). For **ternary**, the step `(v−a)` can be 2 — huge — so the curvature term dominates and the linear extrapolation lies. **This is the real reason gradient-driven flips oscillate**: the gradient says "flip helps" because it's only seeing the slope at the current point, but the actual ternary step overshoots. Your idea adds back the term that makes the decision exact for the step size we're actually taking.

## It dissolves the oscillation wall by construction

The entire s191 wall — and the whole S2 anti-oscillation stack (cooldown, backoff, thermometer, conviction) — exists to *approximate* one property: **only flip if it actually helps**. Exact loss-eval gives you that property directly. Accept a flip only when `min_v ΔL < 0` → loss is monotone non-increasing → **no oscillation is possible**. You'd be replacing a tower of heuristics with a guarantee.

## Three honest caveats

1. **Layer-local, not global.** The closed form is exact for a layer reconstruction / trace target, not global next-token loss (the downstream nonlinearity isn't closed-form). But that's a *feature* here — it's exactly the dense per-layer / trace-matching target the project already validated (`score-matching-compression.md` v3b = 1.44× held-out), and the s208 audit showed the global CE-only endpoint objective is *degenerate* (it memorizes). Layer-local is the cure, not a compromise.

2. **Simultaneous flips interact.** `ΔL_ij` is computed assuming everything else is fixed; flip K at once and the deltas don't compose. Two fixes, both known: flip one-at-a-time with **error compensation** (update R after each flip — the GPTQ/OBS move), or keep batched flips but use exact-ΔL only as the *acceptance* test on a gradient-proposed shortlist.

3. **It has a lineage** — this is the OBQ / GPTQ / OBS family ("pick the quantization that minimizes layer output error, with Hessian-aware compensation"). That's good news, not bad: it means your instinct is the *proven, scalable* form of discrete weight-fitting, and we can triangulate against it instead of re-deriving from scratch.

## Bonus: the "0" falls out functionally

Right now structural zeros are placed heuristically (bottom 30% by magnitude). If the candidate set is genuinely `{−1, 0, +1}`, then `argmin ΔL` **places the zeros functionally** — a position becomes 0 exactly when blocking it minimizes reconstruction error. Sign-decision and sparsity-decision unify into one rule.

---

The cleanest framing: keep TD's gradient SNR as the cheap **proposal** (which positions are worth looking at), but replace the gradient-driven **acceptance** with the exact 3-way `argmin ΔL`. Proposal stays O(gradient); acceptance becomes exact and monotone.

If you want, I can prototype this as a controlled head-to-head — same proposal shortlist, **gradient-proxy acceptance vs exact-3-way acceptance**, on one layer of a small model, measuring (a) reconstruction loss trajectory and (b) the CrystalThermometer oscillation fraction. Register would be *functional* (a loss/convergence claim under intervention). Want me to build that, or keep pulling on the design first?

## User

Yes let's test this, we have a mini and a micro model somewhere to use for this.


## Assistant

I'll find the mini/micro models and the harness scaffolding first, then build the controlled head-to-head.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -il \"micro\\|mini\" -- scripts/ | head -30; echo \"=== dirs ===\"; find . -type d \\( -iname \"*micro*\" -o -iname \"*mini*\" \\) -not -path \"*/.git/*\" 2>/dev/null; echo \"=== ckpt-ish ===\"; ls -d checkpoints 2>/dev/null && ls checkpoints 2>/dev/null | head -40",
  "operation": "status",
  "summary": "find mini micro models"
}
```

**Summary:** $ git grep -il "micro\|mini" -- scrip...

**Output:**
```
Exit code: 0
Stdout:
scripts/analyze_binding_probes.py
scripts/compile_gradient_probe.py
scripts/experiments/assess_v15_attention.py
scripts/experiments/attention_sparsity.py
scripts/experiments/beta_expansion.py
scripts/experiments/binding_distance_distribution.py
scripts/experiments/binding_graph_trace.py
scripts/experiments/binding_prep_lowrank.py
scripts/experiments/combined_compression.py
scripts/experiments/confidence_gate.py
scripts/experiments/crystal_ecc_sign_correction.py
scripts/experiments/crystal_sieve_repro.py
scripts/experiments/crystal_ternarize.py
scripts/experiments/crystal_tree.py
scripts/experiments/direct_delta_correction.py
scripts/experiments/dvd_stamp_test.py
scripts/experiments/eigenvector_selfsimilarity.py
scripts/experiments/ffn_beam_universality.py
scripts/experiments/gate_indexed_ternary.py
scripts/experiments/gradient_zero_map.py
scripts/experiments/hologram_reader.py
scripts/experiments/holographic_sign_correction.py
scripts/experiments/holographic_survival.py
scripts/experiments/l0_characterization.py
scripts/experiments/lambda_machine.py
scripts/experiments/lambda_tracer.py
scripts/experiments/melt_boundaries.py
scripts/experiments/mirror_ternarize.py
scripts/experiments/mode_geometry.py
scripts/experiments/mode_semantic_validity.py
=== dirs ===
./checkpoints/micro
./checkpoints/mini-holo-freeze
./checkpoints/mini-holo-test2
./checkpoints/mini-holo-distill
./checkpoints/mini-holo-exp0
./checkpoints/mini-holo-d-sweep-v2
./checkpoints/mini-dispatch-4op
./checkpoints/mini-holo-test
./checkpoints/mini-baseline
./results/phi4-mini
./results/sr-self-ref-minimal-20260417-003225
./results/holographic-etch-micro
./.venv/lib/python3.12/site-packages/transformers/models/ministral3
./.venv/lib/python3.12/site-packages/transformers/models/ministral
./.venv/lib/python3.12/site-packages/transformers/models/minimax_m2
./.venv/lib/python3.12/site-packages/transformers/models/minimax
./scripts/micro
./scripts/v12/checkpoints/mini-holo-exp2
./scripts/v12/checkpoints/mini-holo-freeze
./scripts/v12/checkpoints/mini-holo-d-sweep
./scripts/v12/checkpoints/mini-holo-distill
./scripts/v12/checkpoints/mini-holo-crystal
./scripts/v12/checkpoints/mini-holo-exp0
./scripts/v12/checkpoints/mini-holo-exp1
./scripts/v12/checkpoints/mini-holo-d-sweep-v2
./scripts/mini-dispatch
=== ckpt-ish ===
checkpoints
a-vsm-lm-v6
basin
basin-v2-d512
basin-v3-d512
compressor-lm
compressor-lm-iterative
micro
mini-baseline
mini-dispatch-4op
mini-holo-d-sweep-v2
mini-holo-distill
mini-holo-exp0
mini-holo-freeze
mini-holo-test
mini-holo-test2
montagu-lm
plates
teacher-features
teacher-features-14b
tesseract-adaptive
tesseract-diagnostic
tesseract-reverse
tesseract-shuffled
v10
v10-consensus
v10-mixed
v10-multicycle
v10-spiral
v10-topk
v10-vsm
v11
v11-holo
v11-holo-inv
v12-crystal-write-r60
v12-crystal-write-r60-dryrun.log
v12-distill-run1
v12-distill-run2
v12-holo-8op
v12-holo-consensus
v12-holo-consensus-smoke
```

## Assistant

Found `scripts/micro`, `scripts/mini-dispatch`, and checkpoints. Let me inspect those harnesses and checkpoints.

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/micro",
  "max_depth": 2
}
```

**Summary:** Listing tree: scripts/micro

**Output:**
```
/Users/mwhitford/src/verbum/scripts/micro
 __pycache__
 computed_beam.py
 deep_trace.py
 kernel_decomposition.py
 mechanism_extraction.py
 micro_model.py
 probe_composed_direction.py
 probe_crystal_zeros.py
 probe_cut_then_fill.py
 probe_moire_trace.py
 probe_mspace.py
 probe_mspace_facet.py
 probe_mspace_zeros.py
 probe_newton_phase.py
 probe_structural_gradient_stability.py
 probe_v_crystal_cascade.py
 reduce.py
 trace_computation.py
 train_cut_crystal.py
 train_cut_topology.py
 train_etch.py
 train_etch_v2.py
 train_etch_v3.py
 train_ffn_zeros.py
 train_micro.py
 train_reduced.py
 train_reduced_zeros_only.py
 universality_probe.py

1 directories, 27 files
```

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/mini-dispatch",
  "max_depth": 2
}
```

**Summary:** Listing tree: scripts/mini-dispatch

**Output:**
```
/Users/mwhitford/src/verbum/scripts/mini-dispatch
 __pycache__
 model.py
 probe.py
 train.py

1 directories, 3 files
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== micro ckpt ===\"; ls -la checkpoints/micro; echo \"=== mini-baseline ===\"; ls -la checkpoints/mini-baseline",
  "operation": "status",
  "summary": "inspect ckpt contents"
}
```

**Summary:** $ echo "=== micro ckpt ==="; ls -la c...

**Output:**
```
Exit code: 0
Stdout:
=== micro ckpt ===
total 72
drwxr-xr-x@  14 mwhitford  staff    448 May 24 00:06 .
drwxr-xr-x@ 107 mwhitford  staff   3424 Jun  4 13:10 ..
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:06 final
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:01 step_000500
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:01 step_001000
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:02 step_001500
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:02 step_002000
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:03 step_002500
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:03 step_003000
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:04 step_003500
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:05 step_004000
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:05 step_004500
drwxr-xr-x@   4 mwhitford  staff    128 May 24 00:06 step_005000
-rw-r--r--@   1 mwhitford  staff  33207 May 24 00:06 train.log
=== mini-baseline ===
total 24
drwxr-xr-x@   8 mwhitford  staff   256 May  8 16:39 .
drwxr-xr-x@ 107 mwhitford  staff  3424 Jun  4 13:10 ..
-rw-r--r--@   1 mwhitford  staff   184 May  8 16:37 config.json
-rw-r--r--@   1 mwhitford  staff  5413 May  8 16:39 history.json
drwxr-xr-x@   3 mwhitford  staff    96 May  8 16:37 step_000500
drwxr-xr-x@   3 mwhitford  staff    96 May  8 16:38 step_001000
drwxr-xr-x@   3 mwhitford  staff    96 May  8 16:39 step_001500
drwxr-xr-x@   3 mwhitford  staff    96 May  8 16:39 step_002000
```

### Thinking

 I'm looking at the micro and mini model options, and the micro path through `scripts/micro/` seems like the cleanest approach. Let me examine the micro model file, its configuration, and the checkpoint contents to understand the model structure and size, then check the training log for more details.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/micro/micro_model.py"
}
```

**Summary:** Reading micro_model.py (0-2000)

**Output:**
```
"""
Micro Model — Minimum viable holographic state machine.

A tiny transformer (~500K params) trained on pure lambda calculus data,
designed to be fully traceable. Every activation, every gradient, every
Q rotation can be read like a circuit diagram.

Architecture:
  embed → [attention → FFN] × N_LAYERS → unembed

No VSM tree, no algedonics, no S5 controller.
Float32 weights throughout (no ternary — this is the microscope, not the target).
Crystal embeddings (16 = 8 positive + 8 anti) pre-initialized from
PCAQ Zone B targets and enforced via crystal lattice loss.

The goal: train this on lambda calculus compile examples until the
holographic state machine forms (crystal latches, FFN encodes inference
pattern). Then trace forward and backward passes to reverse-engineer:
  1. How Q rotations select crystal basins
  2. How FFN overlays encode the inference pattern
  3. How gradients map to beta-reduction selections

License: MIT
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════

N_COMBINATORS = 8
N_TOTAL_COMBINATORS = 16
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
ANTI_COMBINATOR_NAMES = ["āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]


@dataclass
class MicroConfig:
    """Configuration for the micro tracing model."""

    # ── Tokenizer ──
    vocab_size: int = 151936     # Qwen3 BBPE (same as v13)
    eod_id: int = 151643

    # ── Architecture ──
    d_model: int = 128           # small enough to read every dim
    d_ff: int = 512              # 4x d_model
    n_heads: int = 4             # d_head = 32
    n_layers: int = 4            # 4 transformer blocks
    max_seq_len: int = 256       # lambda outputs are short (~25 chars)
    dropout: float = 0.0         # no dropout — we want deterministic traces

    # ── Crystal ──
    crystal_lambda: float = 5.0           # crystal lattice loss weight
    crystal_warmup_steps: int = 200       # high enforcement early
    crystal_warmup_start: float = 20.0    # initial crystal weight
    use_parity_loss: bool = True
    parity_lambda: float = 1.0

    # ── Training ──
    batch_size: int = 8
    lr: float = 3e-4
    warmup_steps: int = 100
    total_steps: int = 5000
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    eval_interval: int = 100
    log_interval: int = 25
    checkpoint_interval: int = 500
    checkpoint_dir: str = "checkpoints/micro"

    # ── Data ──
    train_file: str = "data/compile-train.jsonl"
    eval_file: str = "data/compile-eval.jsonl"
    test_file: str = "data/compile-test.jsonl"

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads


# ══════════════════════════════════════════════════════════════════════
# Crystal targets (Zone B — the compute zone)
# From V13Config, PCAQ Zone B targets (4-model consensus)
# ══════════════════════════════════════════════════════════════════════

PCAQ_ZONE_B_TARGETS = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float32)


def _precompute_parity_eigenbasis(target: np.ndarray) -> dict:
    """Eigendecompose target cosine matrix for parity checks."""
    eigvals, eigvecs = np.linalg.eigh(target)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    parity_levels = [3, 4, 5, 6, 8]
    total_var = sum(max(ev, 0) for ev in eigvals)
    level_weights = []
    for k in parity_levels:
        cum_var = sum(max(eigvals[j], 0) for j in range(k))
        level_weights.append(cum_var / total_var)

    return {
        "eigvecs": eigvecs,
        "eigvals": eigvals,
        "parity_levels": parity_levels,
        "level_weights": level_weights,
    }


def _init_crystal_embeddings(d_model: int) -> tuple[np.ndarray, np.ndarray]:
    """Initialize crystal embeddings from Zone B target eigenstructure.

    Instead of random init, we seed the embeddings so their cosine matrix
    already approximates the Zone B target. This gives the crystal a head
    start on latching.

    Method: eigendecompose the target, take top-k eigenvectors scaled by
    sqrt(eigenvalue), truncate/pad to d_model. The resulting embeddings
    have cosine matrix ≈ target by construction.
    """
    target = PCAQ_ZONE_B_TARGETS
    eigvals, eigvecs = np.linalg.eigh(target)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # Use top eigenvalues to construct embeddings
    # emb[i] = sum_k sqrt(max(eigval_k, 0)) * eigvec_k[i] * random_direction_k
    n = target.shape[0]  # 16
    k = min(n, d_model)

    # Scale eigenvectors by sqrt(eigenvalue) — preserves cosine structure
    scales = np.sqrt(np.maximum(eigvals[:k], 0))
    basis = eigvecs[:, :k] * scales[np.newaxis, :]  # (16, k)

    # If d_model > k, pad with small random noise
    if d_model > k:
        pad = np.random.randn(n, d_model - k).astype(np.float32) * 0.001
        embeddings = np.concatenate([basis, pad], axis=1)
    else:
        embeddings = basis[:, :d_model]

    # Normalize to unit norm (cosine matrix is scale-invariant)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
    embeddings = embeddings / norms * 0.5  # scale=0.5 for stable training

    return embeddings[:N_COMBINATORS], embeddings[N_COMBINATORS:]


# ══════════════════════════════════════════════════════════════════════
# Model components
# ══════════════════════════════════════════════════════════════════════


class MultiHeadAttention(nn.Module):
    """Standard multi-head attention with full trace capture.

    When self.capture_trace is True, stores Q, K, V projections and
    attention weights for later analysis.
    """

    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

        # Trace storage (populated when capture_trace=True)
        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        B, L, D = x.shape
        H = self.n_heads

        q = self.q_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)
        k = self.k_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)

        # Scaled dot-product attention
        scale = math.sqrt(self.d_head)
        scores = (q @ k.transpose(0, 1, 3, 2)) / scale  # (B, H, L, L)

        if mask is not None:
            scores = scores + mask

        attn_weights = mx.softmax(scores, axis=-1)
        attn_out = attn_weights @ v  # (B, H, L, d_head)

        # Capture trace if requested
        if self.capture_trace:
            self.trace = {
                "q": mx.stop_gradient(q),           # (B, H, L, d_head)
                "k": mx.stop_gradient(k),
                "v": mx.stop_gradient(v),
                "attn_weights": mx.stop_gradient(attn_weights),  # (B, H, L, L)
                "attn_out": mx.stop_gradient(attn_out),
            }

        # Reshape and project
        out = attn_out.transpose(0, 2, 1, 3).reshape(B, L, D)
        return self.o_proj(out)


class SwiGLUFFN(nn.Module):
    """SwiGLU FFN with full trace capture.

    gate_proj controls which neurons fire (the beamformer).
    key_proj provides the content to gate (the holographic plate).
    value_proj projects back to d_model (the readout).

    When capture_trace is True, stores gate activations, key activations,
    gated output, and value projection for analysis.
    """

    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.key_proj = nn.Linear(d_model, d_ff, bias=False)
        self.value_proj = nn.Linear(d_ff, d_model, bias=False)

        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array) -> mx.array:
        gate = nn.silu(self.gate_proj(x))   # gate activation (beamformer)
        key = self.key_proj(x)               # key activation (plate content)
        gated = gate * key                   # SwiGLU gating
        out = self.value_proj(gated)         # project back

        if self.capture_trace:
            self.trace = {
                "gate": mx.stop_gradient(gate),
                "key": mx.stop_gradient(key),
                "gated": mx.stop_gradient(gated),
                "out": mx.stop_gradient(out),
                "gate_sparsity": mx.stop_gradient(
                    mx.mean((mx.abs(gate) < 0.01).astype(mx.float32))
                ),
            }

        return out


class TransformerBlock(nn.Module):
    """Pre-norm transformer block: norm → attn → add → norm → ffn → add.

    Captures residual stream at input and output for tracing.
    """

    def __init__(self, d_model: int, n_heads: int, d_ff: int):
        super().__init__()
        self.attn_norm = nn.RMSNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ffn_norm = nn.RMSNorm(d_model)
        self.ffn = SwiGLUFFN(d_model, d_ff)

        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        # Attention
        normed = self.attn_norm(x)
        attn_out = self.attn(normed, mask=mask)
        x = x + attn_out

        # FFN
        normed = self.ffn_norm(x)
        ffn_out = self.ffn(normed)
        x = x + ffn_out

        if self.capture_trace:
            self.trace = {
                "residual_post_attn": mx.stop_gradient(x - ffn_out),
                "attn_contribution": mx.stop_gradient(attn_out),
                "ffn_contribution": mx.stop_gradient(ffn_out),
                "residual_post_ffn": mx.stop_gradient(x),
            }

        return x


# ══════════════════════════════════════════════════════════════════════
# Crystal loss functions
# ══════════════════════════════════════════════════════════════════════


def crystal_lattice_loss(emb_all: mx.array, target: mx.array) -> mx.array:
    """Crystal lattice MSE: upper-triangle cosine matrix vs target."""
    norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb_all / norms
    cos_matrix = emb_norm @ emb_norm.T
    n = cos_matrix.shape[0]
    # Upper triangle indices
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    student = cos_matrix[mx.array(rows), mx.array(cols)]
    target_vals = target[mx.array(rows), mx.array(cols)]
    diff = student - target_vals
    return mx.mean(diff * diff)


def crystal_parity_loss(
    emb_all: mx.array,
    eigvecs: mx.array,
    eigvals: mx.array,
    parity_levels: list[int],
    level_weights: list[float],
) -> tuple[mx.array, mx.array]:
    """Hierarchical dimensional parity check."""
    norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb_all / norms
    student_cos = emb_norm @ emb_norm.T

    projected = eigvecs.T @ student_cos @ eigvecs
    total_loss = mx.array(0.0)
    level_errors = []

    for k, w in zip(parity_levels, level_weights):
        P_k = projected[:k, :k]
        target_diag = mx.diag(eigvals[:k])
        diff = P_k - target_diag
        mse = mx.mean(diff * diff)
        mask = 1.0 - mx.eye(k)
        off_diag = mx.abs(P_k * mask)
        max_off_diag = mx.max(off_diag)
        level_errors.append(max_off_diag)
        total_loss = total_loss + w * mse

    per_level_errors = mx.stack(level_errors)
    return total_loss, per_level_errors


# ══════════════════════════════════════════════════════════════════════
# Micro Model
# ══════════════════════════════════════════════════════════════════════


class MicroModel(nn.Module):
    """Minimum viable holographic state machine.

    Tiny transformer with crystal embeddings. Every component is
    individually traceable. No abstractions hiding computation.

    Forward: embed → blocks × n_layers → norm → unembed
    Crystal: 16 combinator embeddings enforced via Zone B lattice loss
    Trace: set_capture(True) to record all intermediate computations
    """

    def __init__(self, cfg: MicroConfig):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model

        # ── Embeddings ──
        self.embed = nn.Embedding(cfg.vocab_size, d)
        self.pos_embed = nn.Embedding(cfg.max_seq_len, d)

        # ── Crystal embeddings (pre-initialized from Zone B targets) ──
        pos_init, anti_init = _init_crystal_embeddings(d)
        self.combinator_embeddings = mx.array(pos_init)
        self.anti_combinator_embeddings = mx.array(anti_init)

        # Precompute parity eigenbasis
        parity_data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
        self._parity_eigvecs = mx.array(parity_data["eigvecs"])
        self._parity_eigvals = mx.array(parity_data["eigvals"])
        self._parity_levels = parity_data["parity_levels"]
        self._parity_weights = parity_data["level_weights"]

        # Zone B target (frozen)
        self._zone_b_target = mx.array(PCAQ_ZONE_B_TARGETS)

        # ── Transformer blocks ──
        self.blocks = [
            TransformerBlock(d, cfg.n_heads, cfg.d_ff)
            for _ in range(cfg.n_layers)
        ]

        # ── Output ──
        self.output_norm = nn.RMSNorm(d)

        # ── Training state ──
        self._training_step = 0
        self._crystal_ema = mx.array(1.0)

        # ── Causal mask cache ──
        self._causal_mask = None
        self._causal_mask_len = 0

    def _get_causal_mask(self, L: int) -> mx.array:
        """Causal attention mask: -inf above diagonal."""
        if L != self._causal_mask_len:
            mask = mx.full((L, L), float("-inf"))
            mask = mx.triu(mask, k=1)  # zero on and below diagonal
            self._causal_mask = mask
            self._causal_mask_len = L
        return self._causal_mask

    def set_capture(self, on: bool):
        """Enable/disable trace capture on all components."""
        for block in self.blocks:
            block.capture_trace = on
            block.attn.capture_trace = on
            block.ffn.capture_trace = on

    def get_traces(self) -> list[dict]:
        """Collect all traces from all layers."""
        traces = []
        for i, block in enumerate(self.blocks):
            layer_trace = {
                "layer": i,
                "block": block.trace,
                "attn": block.attn.trace,
                "ffn": block.ffn.trace,
            }
            traces.append(layer_trace)
        return traces

    def get_all_crystal_embeddings(self) -> mx.array:
        """Concatenate positive + anti crystal embeddings."""
        return mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)  # (16, d_model)

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape
        cfg = self.cfg

        # Embed
        positions = mx.arange(L)
        x = self.embed(tokens) + self.pos_embed(positions)

        # Causal mask
        mask = self._get_causal_mask(L)

        # Transformer blocks
        for block in self.blocks:
            x = block(x, mask=mask)

        # Output
        x = self.output_norm(x)
        logits = self.embed.weight @ x.reshape(-1, cfg.d_model).T
        logits = logits.T.reshape(B, L, cfg.vocab_size)

        # Loss
        loss = None
        if targets is not None:
            loss = self._compute_loss(logits, targets)

        return logits, loss

    def _compute_loss(self, logits: mx.array, targets: mx.array) -> mx.array:
        """CE loss + crystal lattice loss + parity loss."""
        cfg = self.cfg
        B, L = targets.shape

        # Cross-entropy
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            targets.reshape(-1),
        ).mean()

        # Crystal lattice loss (Zone B only)
        emb_all = self.get_all_crystal_embeddings()
        crystal_loss = crystal_lattice_loss(emb_all, self._zone_b_target)

        # Crystal warmup schedule
        if cfg.crystal_warmup_steps > 0 and self._training_step < cfg.crystal_warmup_steps:
            progress = self._training_step / cfg.crystal_warmup_steps
            crystal_weight = cfg.crystal_lambda + (cfg.crystal_warmup_start - cfg.crystal_lambda) * 0.5 * (1.0 + math.cos(math.pi * progress))
        else:
            crystal_weight = cfg.crystal_lambda

        # EMA tracking
        self._crystal_ema = mx.stop_gradient(
            0.99 * self._crystal_ema + 0.01 * crystal_loss)
        self._last_crystal_loss = mx.stop_gradient(crystal_loss)
        self._last_ce_loss = mx.stop_gradient(ce_loss)

        # Parity loss
        parity_additive = mx.array(0.0)
        if cfg.use_parity_loss:
            parity_loss, parity_errors = crystal_parity_loss(
                emb_all,
                self._parity_eigvecs,
                self._parity_eigvals,
                self._parity_levels,
                self._parity_weights,
            )
            parity_additive = cfg.parity_lambda * parity_loss
            self._last_parity_loss = mx.stop_gradient(parity_loss)
            self._last_parity_errors = mx.stop_gradient(parity_errors)

        total = ce_loss + crystal_weight * crystal_loss + parity_additive
        return total

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Diagnostics ──

    def crystal_diagnostics(self) -> dict:
        """Crystal health check."""
        emb_all = self.get_all_crystal_embeddings()
        norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_all / norms
        cos_matrix = emb_norm @ emb_norm.T
        mx.eval(cos_matrix)

        crystal_loss = crystal_lattice_loss(emb_all, self._zone_b_target)
        mx.eval(crystal_loss)

        # Key sub-lattice metrics
        # Composition cluster: mean(cos(B,C), cos(B,D), cos(C,D))
        comp_cluster = float((cos_matrix[2, 3] + cos_matrix[2, 4] + cos_matrix[3, 4]).item()) / 3.0
        # WHNF anti-correlation
        whnf_anti = float(sum(cos_matrix[7, i].item() for i in range(7))) / 7.0
        # K-I pair
        ki_pair = float(cos_matrix[0, 1].item())

        return {
            "crystal_loss": float(crystal_loss.item()),
            "composition_cluster": comp_cluster,
            "whnf_anti": whnf_anti,
            "ki_pair": ki_pair,
            "cos_matrix": cos_matrix,
        }

    def param_count(self) -> dict:
        """Count parameters by component."""
        def _count(params):
            total = 0
            if isinstance(params, dict):
                for v in params.values():
                    total += _count(v)
            elif isinstance(params, list):
                for v in params:
                    total += _count(v)
            elif isinstance(params, mx.array):
                total += params.size
            return total

        params = self.parameters()
        total = _count(params)

        # Breakdown
        embed_params = self.embed.weight.size + self.pos_embed.weight.size
        crystal_params = self.combinator_embeddings.size + self.anti_combinator_embeddings.size
        block_params = total - embed_params - crystal_params - self.output_norm.weight.size

        return {
            "total": total,
            "embed": embed_params,
            "crystal": crystal_params,
            "blocks": block_params,
            "output_norm": self.output_norm.weight.size,
        }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("micro_model.py self-test")
    print("=" * 60)

    cfg = MicroConfig()
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    # Parameter count
    counts = model.param_count()
    print(f"\nParameter counts:")
    for k, v in counts.items():
        print(f"  {k}: {v:,}")

    # Forward pass (no targets)
    tokens = mx.random.randint(0, 1000, (2, 32))
    logits, loss = model(tokens)
    mx.eval(logits)
    assert logits.shape == (2, 32, cfg.vocab_size), f"Expected (2, 32, {cfg.vocab_size}), got {logits.shape}"
    assert loss is None
    print(f"\nForward (no targets): logits {logits.shape} ✓")

    # Forward pass (with targets)
    targets = mx.random.randint(0, 1000, (2, 32))
    logits2, loss2 = model(tokens, targets)
    mx.eval(logits2, loss2)
    print(f"Forward (with targets): loss={loss2.item():.4f} ✓")

    # Gradient flow
    def loss_fn(m, tok, tgt):
        _, loss = m(tok, tgt)
        return loss

    gfn = nn.value_and_grad(model, loss_fn)
    lv, grads = gfn(model, tokens, targets)
    mx.eval(lv, grads)
    print(f"Backward: loss={lv.item():.4f}, gradient flow OK ✓")

    # Crystal diagnostics
    diag = model.crystal_diagnostics()
    print(f"\nCrystal:")
    print(f"  loss: {diag['crystal_loss']:.6f}")
    print(f"  composition cluster: {diag['composition_cluster']:.4f}")
    print(f"  WHNF anti: {diag['whnf_anti']:.4f}")
    print(f"  K-I pair: {diag['ki_pair']:.4f}")

    # Trace capture
    model.set_capture(True)
    logits3, loss3 = model(tokens, targets)
    mx.eval(logits3, loss3)
    traces = model.get_traces()
    print(f"\nTrace capture:")
    for t in traces:
        layer = t["layer"]
        attn = t["attn"]
        ffn = t["ffn"]
        print(f"  Layer {layer}:")
        print(f"    Q: {attn['q'].shape}, attn_weights: {attn['attn_weights'].shape}")
        print(f"    gate_sparsity: {ffn['gate_sparsity'].item():.3f}")
    model.set_capture(False)

    # The transformer blocks are the traceable part — embedding table is just lookup
    assert counts["blocks"] < 2_000_000, f"Too many block params: {counts['blocks']:,}"
    print(f"\nTotal params: {counts['total']:,}")
    print(f"  (embedding table: {counts['embed']:,} — just lookup, not traced)")
    print(f"  (transformer blocks: {counts['blocks']:,} — THIS is what we trace ✓)")

    print("\n" + "=" * 60)
    print("micro_model.py: all tests passed ✓")
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== micro/final ===\"; ls -la checkpoints/micro/final; echo \"=== train.log head ===\"; head -40 checkpoints/micro/train.log",
  "operation": "status",
  "summary": "read micro model + ckpt"
}
```

**Summary:** $ echo "=== micro/final ==="; ls -la ...

**Output:**
```
Exit code: 0
Stdout:
=== micro/final ===
total 160440
drwxr-xr-x@  4 mwhitford  staff       128 May 24 00:06 .
drwxr-xr-x@ 14 mwhitford  staff       448 May 24 00:06 ..
-rw-r--r--@  1 mwhitford  staff  82139248 May 24 00:06 model.npz
-rw-r--r--@  1 mwhitford  staff        96 May 24 00:06 state.json
=== train.log head ===
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
============================================================
Micro Model Training — Lambda Calculus
============================================================
Tokenizer: Qwen3 BBPE, vocab=151643
Train examples: 509
Eval examples: 10
Train tokens: 8,741
Eval tokens: 192
Avg seq len: 17.2

Model: 20,532,352 total params
  Transformer blocks: 1,049,600
  Crystal: 2,048

Initial crystal:
  loss: 0.000000
  comp_cluster: 0.8710
  K-I pair: 0.7864

Training for 5000 steps...
  batch_size=8, seq_len=256
  lr=0.0003, warmup=100

step     1 | CE 12.2781 | crystal 0.000000 (ema 0.990000) | parity 0.0000 | gnorm 5.61 | lr 3.10e-06 | 0s
step    25 | CE 8.8416 | crystal 0.000000 (ema 0.777822) | parity 0.0000 | gnorm 2.44 | lr 7.51e-05 | 2s
step    50 | CE 5.3052 | crystal 0.000000 (ema 0.605006) | parity 0.0000 | gnorm 1.15 | lr 1.50e-04 | 3s
step    75 | CE 3.1173 | crystal 0.000000 (ema 0.470587) | parity 0.0000 | gnorm 0.86 | lr 2.25e-04 | 4s
step   100 | CE 2.3957 | crystal 0.000000 (ema 0.366033) | parity 0.0000 | gnorm 0.78 | lr 3.00e-04 | 6s
  EVAL  | CE 5.8375 | total 5.8375
        | crystal 0.000000 | comp_cluster 0.8710 | K-I 0.7865 | WHNF_anti -0.1502
        | ★ New best eval loss
  GEN   | The guard works happily.
        | λx. flies)<|endoftext|>
step   125 | CE 2.1246 | crystal 0.000000 (ema 0.281861) | parity 0.0000 | gnorm 0.75 | lr 3.00e-04 | 7s
step   150 | CE 1.9415 | crystal 0.000000 (ema 0.219238) | parity 0.0000 | gnorm 0.81 | lr 2.99e-04 | 9s
step   175 | CE 1.8618 | crystal 0.000000 (ema 0.170528) | parity 0.0000 | gnorm 0.92 | lr 2.99e-04 | 10s
step   200 | CE 1.8297 | crystal 0.000000 (ema 0.132640) | parity 0.0000 | gnorm 2.28 | lr 2.99e-04 | 13s
  EVAL  | CE 4.9856 | total 4.9856
        | crystal 0.000000 | comp_cluster 0.8710 | K-I 0.7865 | WHNF_anti -0.1502
```

### Thinking

 I've got the micro model specs locked in—a 4-layer transformer with 128 dimensions, 512 feed-forward size, 4 attention heads, trained on lambda calculus compilation data with a checkpoint ready to go. For the experiment, I'm planning to isolate the core hypothesis by comparing exact 3-way delta-loss acceptance against gradient-proxy acceptance on a single linear layer.

The test setup is straightforward: extract a trained weight matrix from the model, collect calibration activations by running forward passes, then optimize ternary weights using two competing methods—one that scores flips by gradient magnitude and SNR thresholds, the other that computes exact loss deltas for each ternary value and accepts only improving moves. I'll track reconstruction loss over iterations and measure oscillation to see which approach converges more cleanly. I'm setting up an experiment harness that loads a micro model, extracts real activations and float weights from a chosen layer like gate_proj, then runs the exact ΔL method against gradient-proxy flipping on the same weight matrix to isolate sign-selection quality. I'll initialize signs from the float weights with structural zeros, then compare how quickly each method reduces reconstruction loss. For each position I'll compute the exact loss change for all three ternary values, pick the one with the best improvement, and only accept flips that reduce loss. I'll track metrics like reconstruction error, flip counts, and oscillation patterns across ~100-200 steps. To get a gold standard, I'm also including a sequential exact coordinate descent variant that updates the residual after each flip (the GPTQ approach), which is feasible since it's just rank-1 updates. So I'll run three methods side-by-side: the proxy gradient approach, exact loss changes in batch mode, and the sequential exact method with compensation. With the incremental update approach, I can run EXACT-SEQ all the way to convergence and use that as the gold standard floor for reconstruction error. Now I need to set up the experiment properly — define the different arms, establish clear metrics around loss and convergence behavior, then verify the tooling works. Let me check how the checkpoint and data load in the existing code, and confirm the MLX and Python setup is ready.

## Assistant

This is a clean, fully-traceable microscope: a 4-layer float32 transformer (d_model=128, d_ff=512), ~1.05M transformer params, trained on lambda-calculus compile data, checkpoint at `checkpoints/micro/final/model.npz`. Perfect substrate.

Let me check the data format and how training loads the checkpoint, then I'll build the experiment.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/micro/train_micro.py",
  "limit": 120
}
```

**Summary:** Reading train_micro.py (0-120)

**Output:**
```
"""
Train Micro Model — Lambda calculus compile examples.

Trains the micro model on pure lambda calculus data (compile-train.jsonl)
until the holographic state machine forms: crystal latches, FFN encodes
inference pattern, attention learns Q rotations.

Data format: {"input": "Every artist knows a baker.",
              "output": "∀x. (artist(x) → knows(x, baker))"}

Tokenized as: <input>\n<output><eod>
Causal LM objective — predict every token including the output.

Usage:
    cd verbum
    uv run python scripts/micro/train_micro.py

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

# Import from same directory
import sys
sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════


def load_compile_examples(path: str | Path) -> list[dict]:
    """Load compile examples from JSONL."""
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def tokenize_examples(
    examples: list[dict],
    tokenizer,
    max_len: int = 256,
    eod_id: int = 151643,
) -> list[np.ndarray]:
    """Tokenize compile examples as causal LM sequences.

    Format: <input>\n<output><eod>

    Returns list of int32 arrays, each of length <= max_len.
    """
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        token_ids.append(eod_id)
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        sequences.append(np.array(token_ids, dtype=np.int32))
    return sequences


class CompileDataLoader:
    """Cycles through tokenized compile examples, packing into batches.

    Packs multiple short examples into one sequence for efficient training.
    Shuffles each epoch.
    """

    def __init__(
        self,
        sequences: list[np.ndarray],
        batch_size: int,
        seq_len: int,
        eod_id: int = 151643,
        seed: int = 42,
    ):
        self.sequences = sequences
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.eod_id = eod_id
        self.rng = np.random.RandomState(seed)

        # Pack all sequences into one long stream
        self._rebuild_stream()

    def _rebuild_stream(self):
        """Shuffle and concatenate all sequences into a token stream."""
        indices = self.rng.permutation(len(self.sequences))
        all_tokens = []
        for idx in indices:
            all_tokens.append(self.sequences[idx])
        self.stream = np.concatenate(all_tokens)
        self.position = 0

    def next_batch(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns (input_ids, targets) each of shape (batch_size, seq_len)."""
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)

        if self.position + needed > len(self.stream):
            self._rebuild_stream()

        buf = self.stream[self.position : self.position + needed]

[CONTENT TRUNCATED] Showing lines 1 to 120 of 377 total lines. Use line_offset=120 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== state.json ===\"; cat checkpoints/micro/final/state.json; echo; echo \"=== data files ===\"; ls -la data/compile-*.jsonl 2>/dev/null; echo \"=== sample ===\"; head -2 data/compile-train.jsonl 2>/dev/null; echo \"=== mlx check ===\"; uv run python -c \"import mlx.core as mx; print('mlx ok', mx.default_device())\" 2>&1 | tail -3",
  "operation": "status",
  "summary": "check data, state, mlx"
}
```

**Summary:** $ echo "=== state.json ==="; cat chec...

**Output:**
```
Exit code: 0
Stdout:
=== state.json ===
{
  "step": 5000,
  "crystal_ema": 2.85976851838773e-15,
  "best_eval_loss": 4.612173080444336
}
=== data files ===
-rw-r--r--@ 1 mwhitford  staff   1443 Apr 17 10:43 data/compile-eval.jsonl
-rw-r--r--@ 1 mwhitford  staff   5955 Apr 17 12:25 data/compile-test.jsonl
-rw-r--r--@ 1 mwhitford  staff  74084 Apr 17 12:25 data/compile-train.jsonl
=== sample ===
{"input": "Every artist knows a baker.", "output": "∀x. (artist(x) → knows(x, baker))", "category": "quantified", "phenomena": ["quantification", "transitive"]}
{"input": "Frank follows oscar.", "output": "λx. follows(frank, oscar)", "category": "transitive", "phenomena": ["predication", "proper_noun", "transitive"]}
=== mlx check ===
mlx ok Device(gpu, 0)
```

### Thinking

 I need to understand how the checkpoint loading works and how the model parameters are structured, so I'm going to examine the save and load functions in train_micro.py to see how the flattened parameters map back to the model.

## Assistant

Let me see how the checkpoint maps to params (load mechanics) so I capture layer activations correctly.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/micro/train_micro.py",
  "line_offset": 120,
  "limit": 130
}
```

**Summary:** Reading train_micro.py (120-250)

**Output:**
```
        self.position += needed

        buf = buf.reshape(B, T + 1)
        input_ids = buf[:, :T]
        targets = buf[:, 1 : T + 1]
        return input_ids, targets


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════


def train(cfg: MicroConfig):
    """Train the micro model on compile examples."""

    print("=" * 60)
    print("Micro Model Training — Lambda Calculus")
    print("=" * 60)

    # ── Tokenizer ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    print(f"Tokenizer: Qwen3 BBPE, vocab={tokenizer.vocab_size}")

    # ── Data ──
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    print(f"Train examples: {len(train_examples)}")
    print(f"Eval examples: {len(eval_examples)}")

    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    print(f"Train tokens: {sum(len(s) for s in train_seqs):,}")
    print(f"Eval tokens: {sum(len(s) for s in eval_seqs):,}")
    print(f"Avg seq len: {np.mean([len(s) for s in train_seqs]):.1f}")

    train_loader = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id)
    # Eval set is tiny (10 examples, ~192 tokens). Use batch_size=1
    # and a seq_len that fits. Pack all eval into one stream.
    eval_total_tokens = sum(len(s) for s in eval_seqs)
    eval_seq_len = min(cfg.max_seq_len, max(16, eval_total_tokens // 2 - 1))
    eval_loader = CompileDataLoader(
        eval_seqs, 1, eval_seq_len, cfg.eod_id, seed=99)

    # ── Model ──
    model = MicroModel(cfg)
    mx.eval(model.parameters())
    counts = model.param_count()
    print(f"\nModel: {counts['total']:,} total params")
    print(f"  Transformer blocks: {counts['blocks']:,}")
    print(f"  Crystal: {counts['crystal']:,}")

    # ── Crystal initial diagnostics ──
    diag = model.crystal_diagnostics()
    print(f"\nInitial crystal:")
    print(f"  loss: {diag['crystal_loss']:.6f}")
    print(f"  comp_cluster: {diag['composition_cluster']:.4f}")
    print(f"  K-I pair: {diag['ki_pair']:.4f}")

    # ── Optimizer ──
    lr_schedule = optim.cosine_decay(cfg.lr, cfg.total_steps, cfg.lr * 0.01)
    warmup_schedule = optim.linear_schedule(
        1e-7, cfg.lr, cfg.warmup_steps)

    def lr_fn(step):
        if step < cfg.warmup_steps:
            return warmup_schedule(step)
        return lr_schedule(step)

    optimizer = optim.AdamW(
        learning_rate=lr_fn,
        weight_decay=cfg.weight_decay,
    )

    # ── Loss function for value_and_grad ──
    def loss_fn(model, input_ids, targets):
        _, loss = model(input_ids, targets)
        return loss

    loss_and_grad_fn = nn.value_and_grad(model, loss_fn)

    # ── Checkpoint directory ──
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    # ── Training loop ──
    print(f"\nTraining for {cfg.total_steps} steps...")
    print(f"  batch_size={cfg.batch_size}, seq_len={cfg.max_seq_len}")
    print(f"  lr={cfg.lr}, warmup={cfg.warmup_steps}")
    print()

    best_eval_loss = float("inf")
    t_start = time.time()

    for step in range(1, cfg.total_steps + 1):
        model._training_step = step

        # ── Train step ──
        input_ids, targets = train_loader.next_batch()
        input_ids = mx.array(input_ids)
        targets = mx.array(targets)

        loss_val, grads = loss_and_grad_fn(model, input_ids, targets)

        # Gradient clipping
        grads, gnorm = optim.clip_grad_norm(grads, cfg.grad_clip)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        # ── Logging ──
        if step % cfg.log_interval == 0 or step == 1:
            ce = float(model._last_ce_loss.item())
            crystal = float(model._last_crystal_loss.item())
            crystal_ema = float(model._crystal_ema.item())
            parity = float(getattr(model, '_last_parity_loss', mx.array(0.0)).item())
            elapsed = time.time() - t_start
            lr_now = lr_fn(step)
            lr_val = float(lr_now.item()) if isinstance(lr_now, mx.array) else float(lr_now)

            print(
                f"step {step:5d} | "
                f"CE {ce:.4f} | "
                f"crystal {crystal:.6f} (ema {crystal_ema:.6f}) | "
                f"parity {parity:.4f} | "
                f"gnorm {float(gnorm.item()):.2f} | "
                f"lr {lr_val:.2e} | "
                f"{elapsed:.0f}s"
            )

[CONTENT TRUNCATED] Showing lines 121 to 250 of 377 total lines. Use line_offset=250 parameter to read more content.
```

## Assistant

Let me see the checkpoint save/load to know the npz key structure.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '250,377p' scripts/micro/train_micro.py | grep -n \"save\\|load\\|npz\\|flatten\\|state\" ; echo \"=== npz keys ===\"; uv run python -c \"\nimport numpy as np\nd = np.load('checkpoints/micro/final/model.npz')\nks = list(d.keys())\nprint('n_keys', len(ks))\nfor k in ks:\n    if 'blocks.0' in k or 'blocks' not in k:\n        print(k, d[k].shape)\n\" 2>&1 | grep -v Warning | head -50",
  "operation": "status",
  "summary": "inspect npz keys"
}
```

**Summary:** $ sed -n '250,377p' scripts/micro/tra...

**Output:**
```
Exit code: 0
Stdout:
5:            eval_input, eval_target = eval_loader.next_batch()
43:            flat = dict(nn.utils.tree_flatten(model.parameters()))
44:            mx.savez(str(ckpt_dir / "model.npz"), **flat)
46:            # Save config + training state
47:            state = {
52:            with open(ckpt_dir / "state.json", "w") as f:
53:                json.dump(state, f, indent=2)
55:            print(f"  CKPT  | saved to {ckpt_dir}")
57:    # ── Final save ──
60:    flat = dict(nn.utils.tree_flatten(model.parameters()))
61:    mx.savez(str(final_dir / "model.npz"), **flat)
62:    state = {
67:    with open(final_dir / "state.json", "w") as f:
68:        json.dump(state, f, indent=2)
70:    print(f"\nTraining complete. Final model saved to {final_dir}")
=== npz keys ===
n_keys 41
blocks.0.ffn.value_proj.weight (128, 512)
blocks.0.ffn.key_proj.weight (512, 128)
anti_combinator_embeddings (8, 128)
blocks.0.ffn.gate_proj.weight (512, 128)
blocks.0.ffn_norm.weight (128,)
output_norm.weight (128,)
blocks.0.attn.v_proj.weight (128, 128)
embed.weight (151936, 128)
blocks.0.attn.q_proj.weight (128, 128)
blocks.0.attn.o_proj.weight (128, 128)
blocks.0.attn_norm.weight (128,)
pos_embed.weight (256, 128)
blocks.0.attn.k_proj.weight (128, 128)
combinator_embeddings (8, 128)
```

### Thinking

 I've got the checkpoint loading figured out—flattening the model parameters and then unflattening them back when needed. Now I'm setting up the experiment to compare whether exact 3-way ΔL acceptance outperforms gradient-proxy acceptance when fitting a ternary approximation with per-row gains.

I'm targeting the gate projection layer from the first block (512×128 matrix) since that's where the router's sign topology matters most, though I might test the value projection too. The tricky part is capturing the actual input activations to that layer—the RMSNorm'd residual that feeds into the FFN. Rather than modifying the model file, I'll write a custom forward pass that runs through the blocks and captures the input to my target linear layer.

Actually, I realize the value projection is cleaner since its input (the gated activation) is already stored in the trace, so I can skip the monkeypatching entirely. The value projection takes the gated output and projects it from 512 to 128 dimensions, which gives me a clean target for measuring how the weight matrix behaves under quantization.

I'll write a custom forward pass that manually steps through the model blocks and captures the exact inputs and outputs for whichever linear layer I'm targeting. This way everything is transparent and visible in my script—no runtime patching needed. I can iterate through each block, apply the attention and FFN operations, and when I hit the target block, I'll extract the normed FFN input and the corresponding weight matrix to compute the target output.

Now for the fitting problem itself: I'm working with a float weight matrix W and real activations X, trying to find a ternary sign matrix S and per-output-row scaling factors γ that minimize the reconstruction error. The key insight is that this loss decomposes row-by-row—each output dimension is independent. For each row i, I can compute the optimal scale γ_i in closed form using least squares, then evaluate how much the loss changes when I flip individual entries in S.

I'm vectorizing this computation: building a residual matrix R, computing the gradient matrix G = R^T @ X in one matmul to get all the linear gradient terms, and then for each candidate flip from value a to v, calculating the full quadratic change in loss across all positions simultaneously. This lets me identify which flips actually reduce the loss and rank them by improvement magnitude.

For the actual optimization methods, I'm comparing different strategies for selecting which entries to flip—starting with a gradient-proxy approach that prioritizes flips with large linear gradient magnitude where the direction of change opposes the current sign. For the exact-batch approach, I'm computing the loss change for every possible flip and selecting the top-B improvements, though flipping multiple positions in the same row simultaneously can interact in non-monotone ways since they share the projection matrix. With exact sequential selection (the gold standard), I'd greedily pick one flip at a time globally, updating the residuals and maintaining the necessary statistics to compute optimal scaling factors after each change.

To compare fairly, I'll start all three methods from the sign of the original weights with no preset sparsity, letting them discover zeros naturally. I'll track relative reconstruction error per step, count how many flips are applied, measure oscillation by checking if positions flip back to previous values, and verify whether loss actually decreases monotonically. The final metrics will include sparsity achieved and how each method trades off between convergence speed and solution quality.

I'm setting up a focused experiment in `scripts/experiments/ternary_exact_vs_proxy.py` to directly test whether exact greedy selection beats gradient-based proxies on reconstruction loss, monotonicity, and oscillation. For the budget, I'll use about 328 flips per step across 150 steps for the batch methods, while exact sequential runs until no improvement is found. I'm using a fixed calibration set of roughly 2000–4000 token positions from the training data to ensure determinism.

To show robustness, I'll run the experiment on a couple of different (layer, matrix) pairs—gate_proj on layers 0 and 2, and value_proj on layer 2. I'll capture activations manually during the forward pass and emit all loss curves to a JSON audit file.

Writing the harness now...

## Assistant

I have everything I need:
- **Substrate:** `checkpoints/micro/final/model.npz` (npz keys = flattened param tree, e.g. `blocks.0.ffn.gate_proj.weight` (512,128)).
- **Target weights:** `gate_proj` (the router — where audit #1 located real sign-topology) is the theoretically right place to test sign-fitting; `value_proj` (the value path) as a contrast.
- **Activations:** I'll capture real layer inputs `X` via a manual forward, build target `T = X @ W_float.ᵀ`, and fit ternary `S∈{−1,0,+1}` + per-row `γ`.

Let me set a short plan, then build and run the controlled head-to-head.

### Thinking

 I'm setting up the test harness now, registering it as a functional component.

## Assistant

Now I'll build the harness. Register: **functional** (a loss/convergence claim under intervention).

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py",
  "content": "# register: functional\n\"\"\"Ternary sign-fitting: exact 3-way ΔL acceptance vs gradient-proxy.\n\nTHE CLAIM (Michael, session 213): instead of TD's gradient-EMA *proxy* for\ndeciding sign flips, directly evaluate the loss for all three ternary values\n{-1, 0, +1} at each position and take the one that improves loss most.\n\nTHE FEASIBILITY INSIGHT: for a layer-local quadratic reconstruction target you\ndo NOT need a forward pass per position. For one linear layer with effective\nternary weight S (per-row scale γ), real calibration input X (n × d_in), and\nteacher target T = X @ W_floatᵀ (n × d_out), the rows are independent and the\nexact loss-delta of changing S[i,j] from a to v is, in closed form:\n\n    ΔL_ij(v) = 2·γ_i·(v−a)·⟨r_i, X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²\n                └────── linear (= gradient) ──┘   └──── curvature ────┘\n\nwhere r_i = γ_i·(X@S[i,:]) − T[:,i] is the current per-row residual. The whole\n(d_out × d_in) grid of ⟨r_i,X[:,j]⟩ is one matmul Rᵀ@X. The LINEAR term is\nexactly the gradient TD already uses; the CURVATURE term is what the proxy\nthrows away. For ternary the step (v−a) is large (up to 2) → curvature is NOT\nnegligible → it is precisely the missing piece, and only accepting flips with\nΔL<0 makes the search MONOTONE (dissolving the s191 oscillation wall by\nconstruction).\n\nTHREE ARMS (all start from S0 = sign(W_float), γ optimal per row):\n  PROXY       — rank candidates by |gradient|, flip toward −sign(grad);\n                NO curvature check (faithful linear analog of TD acceptance).\n  EXACT-BATCH — closed-form 3-way argmin ΔL, take top-B *improving* per step.\n  EXACT-SEQ   — greedy ONE-at-a-time with residual compensation (GPTQ/OBS\n                gold standard), monotone to convergence.\n\nMETRICS: relative reconstruction loss trajectory, oscillation/reversal\nfraction, # loss-increasing steps (monotonicity), final sparsity.\n\nSubstrate: checkpoints/micro/final (4-layer float32 lambda-calculus model).\nLicense: MIT.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport mlx.core as mx\nimport mlx.nn as nn\n\n# Import the micro model\nREPO = Path(__file__).resolve().parents[2]\nsys.path.insert(0, str(REPO / \"scripts\" / \"micro\"))\nfrom micro_model import MicroModel, MicroConfig  # noqa: E402\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Load model + capture real layer activations\n# ══════════════════════════════════════════════════════════════════════\n\ndef load_micro(ckpt: Path) -> MicroModel:\n    cfg = MicroConfig()\n    model = MicroModel(cfg)\n    flat = list(mx.load(str(ckpt / \"model.npz\")).items())\n    model.update(nn.utils.tree_unflatten(flat))\n    mx.eval(model.parameters())\n    return model\n\n\ndef tokenize_calibration(cfg: MicroConfig, n_examples: int, seq_cap: int) -> mx.array:\n    \"\"\"Tokenize compile-train examples into one packed (B, L) batch.\"\"\"\n    from transformers import AutoTokenizer\n    tok = AutoTokenizer.from_pretrained(\"Qwen/Qwen3-0.6B\")\n    examples = []\n    with open(REPO / \"data\" / \"compile-train.jsonl\") as f:\n        for line in f:\n            line = line.strip()\n            if line:\n                examples.append(json.loads(line))\n    examples = examples[:n_examples]\n    stream: list[int] = []\n    for ex in examples:\n        ids = tok.encode(f\"{ex['input']}\\n{ex['output']}\", add_special_tokens=False)\n        ids.append(cfg.eod_id)\n        stream.extend(ids)\n    # pack into rows of length seq_cap\n    n_rows = max(1, len(stream) // seq_cap)\n    stream = stream[: n_rows * seq_cap]\n    arr = np.array(stream, dtype=np.int32).reshape(n_rows, seq_cap)\n    return mx.array(arr)\n\n\ndef capture_layer_io(\n    model: MicroModel, tokens: mx.array, layer_idx: int, which: str\n) -> tuple[mx.array, mx.array]:\n    \"\"\"Manual forward; return (X, W_float) for the chosen linear.\n\n    which ∈ {\"gate_proj\", \"key_proj\", \"value_proj\", \"o_proj\"}.\n    X is the real input activation to that linear, flattened to (n, d_in).\n    \"\"\"\n    cfg = model.cfg\n    B, L = tokens.shape\n    positions = mx.arange(L)\n    x = model.embed(tokens) + model.pos_embed(positions)\n    mask = model._get_causal_mask(L)\n\n    X = None\n    Wf = None\n    for i, block in enumerate(model.blocks):\n        normed_attn = block.attn_norm(x)\n        x = x + block.attn(normed_attn, mask=mask)\n        normed_ffn = block.ffn_norm(x)\n        if i == layer_idx:\n            ffn = block.ffn\n            if which == \"gate_proj\":\n                X, Wf = normed_ffn, ffn.gate_proj.weight\n            elif which == \"key_proj\":\n                X, Wf = normed_ffn, ffn.key_proj.weight\n            elif which == \"value_proj\":\n                gate = nn.silu(ffn.gate_proj(normed_ffn))\n                key = ffn.key_proj(normed_ffn)\n                X, Wf = gate * key, ffn.value_proj.weight\n            elif which == \"o_proj\":\n                raise NotImplementedError(\"o_proj capture not wired\")\n            else:\n                raise ValueError(which)\n            break\n        x = x + block.ffn(normed_ffn)\n\n    X = X.reshape(-1, X.shape[-1])  # (n, d_in)\n    mx.eval(X, Wf)\n    return X, Wf\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Core fitting math (numpy for clarity + exact control)\n# ══════════════════════════════════════════════════════════════════════\n\ndef optimal_gamma(P: np.ndarray, T: np.ndarray) -> np.ndarray:\n    \"\"\"Per-row least-squares scale. P,T are (d_out, n). γ_i = <P_i,T_i>/‖P_i‖².\"\"\"\n    num = np.einsum(\"in,in->i\", P, T)\n    den = np.einsum(\"in,in->i\", P, P) + 1e-12\n    return num / den\n\n\ndef rel_loss(S: np.ndarray, gamma: np.ndarray, X: np.ndarray, T: np.ndarray) -> float:\n    \"\"\"‖γ⊙(S@Xᵀ) − T‖² / ‖T‖²  (rows = d_out).\"\"\"\n    P = S @ X.T                     # (d_out, n)\n    pred = gamma[:, None] * P       # (d_out, n)\n    return float(np.sum((pred - T) ** 2) / (np.sum(T ** 2) + 1e-12))\n\n\ndef delta_grid(S, gamma, R, XtX_diag, G):\n    \"\"\"Exact ΔL for v ∈ {-1,0,+1} at every position. Returns (best_v, best_delta).\n\n    G        = (R @ X)               (d_out, d_in)  — ⟨r_i, X[:,j]⟩\n    XtX_diag = ‖X[:,j]‖²             (d_in,)\n    \"\"\"\n    g = gamma[:, None]              # (d_out,1)\n    col = XtX_diag[None, :]         # (1,d_in)\n    best_v = S.copy()\n    best_delta = np.zeros_like(S, dtype=np.float64)  # v == current → ΔL 0\n    for v in (-1.0, 0.0, 1.0):\n        step = (v - S)\n        dl = 2.0 * g * step * G + (g ** 2) * (step ** 2) * col\n        take = dl < best_delta\n        best_delta = np.where(take, dl, best_delta)\n        best_v = np.where(take, v, best_v)\n    return best_v, best_delta\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Arms\n# ══════════════════════════════════════════════════════════════════════\n\ndef run_proxy(X, T, S0, n_steps, budget, recover_window=4):\n    \"\"\"Gradient-proxy: rank by |gradient|, flip toward −sign(grad). No curvature.\"\"\"\n    d_out, d_in = S0.shape\n    S = S0.copy().astype(np.float64)\n    XtX_diag = np.einsum(\"nj,nj->j\", X, X)\n    hist = {\"rel_loss\": [], \"n_flips\": [], \"reversal_frac\": [], \"loss_up\": 0}\n    prev_S = [S.copy()]\n    P = S @ X.T\n    gamma = optimal_gamma(P, T.T)\n    prev_loss = rel_loss(S, gamma, X, T)\n    hist[\"rel_loss\"].append(prev_loss)\n    hist[\"n_flips\"].append(0)\n    hist[\"reversal_frac\"].append(0.0)\n    for _ in range(n_steps):\n        P = S @ X.T                          # (d_out, n)\n        R = gamma[:, None] * P - T.T         # (d_out, n) residual\n        G = R @ X                            # (d_out, d_in)  linear term core\n        c = 2.0 * gamma[:, None] * G         # gradient coefficient ∂L/∂S\n        v_proxy = -np.sign(c)                # linear-optimal extreme value\n        v_proxy[v_proxy == 0] = S[v_proxy == 0]  # zero grad → keep\n        score = np.abs(c)\n        cand = v_proxy != S\n        score = np.where(cand, score, -np.inf)\n        flat = score.ravel()\n        k = min(budget, int(np.sum(cand)))\n        if k <= 0:\n            hist[\"rel_loss\"].append(prev_loss)\n            hist[\"n_flips\"].append(0)\n            hist[\"reversal_frac\"].append(0.0)\n            continue\n        idx = np.argpartition(flat, -k)[-k:]\n        mask = np.zeros(flat.shape, dtype=bool)\n        mask[idx] = True\n        mask = mask.reshape(S.shape) & cand\n        # reversal detection vs `recover_window` steps ago\n        ref = prev_S[max(0, len(prev_S) - recover_window)]\n        new_S = np.where(mask, v_proxy, S)\n        reversals = np.sum(mask & (new_S == ref) & (ref != S))\n        nf = int(np.sum(new_S != S))\n        S = new_S\n        gamma = optimal_gamma(S @ X.T, T.T)\n        loss = rel_loss(S, gamma, X, T)\n        if loss > prev_loss + 1e-12:\n            hist[\"loss_up\"] += 1\n        prev_loss = loss\n        prev_S.append(S.copy())\n        hist[\"rel_loss\"].append(loss)\n        hist[\"n_flips\"].append(nf)\n        hist[\"reversal_frac\"].append(float(reversals) / max(nf, 1))\n    hist[\"final_sparsity\"] = float(np.mean(S == 0))\n    hist[\"S\"] = S\n    return hist\n\n\ndef run_exact_batch(X, T, S0, n_steps, budget, recover_window=4):\n    \"\"\"Exact 3-way ΔL, take top-B *improving* per step.\"\"\"\n    d_out, d_in = S0.shape\n    S = S0.copy().astype(np.float64)\n    XtX_diag = np.einsum(\"nj,nj->j\", X, X)\n    hist = {\"rel_loss\": [], \"n_flips\": [], \"reversal_frac\": [], \"loss_up\": 0}\n    prev_S = [S.copy()]\n    gamma = optimal_gamma(S @ X.T, T.T)\n    prev_loss = rel_loss(S, gamma, X, T)\n    hist[\"rel_loss\"].append(prev_loss)\n    hist[\"n_flips\"].append(0)\n    hist[\"reversal_frac\"].append(0.0)\n    for _ in range(n_steps):\n        P = S @ X.T\n        R = gamma[:, None] * P - T.T\n        G = R @ X\n        best_v, best_delta = delta_grid(S, gamma, R, XtX_diag, G)\n        improving = best_delta < -1e-12\n        score = np.where(improving, -best_delta, -np.inf)  # bigger = better\n        flat = score.ravel()\n        k = min(budget, int(np.sum(improving)))\n        if k <= 0:\n            hist[\"rel_loss\"].append(prev_loss)\n            hist[\"n_flips\"].append(0)\n            hist[\"reversal_frac\"].append(0.0)\n            continue\n        idx = np.argpartition(flat, -k)[-k:]\n        mask = np.zeros(flat.shape, dtype=bool)\n        mask[idx] = True\n        mask = mask.reshape(S.shape) & improving\n        ref = prev_S[max(0, len(prev_S) - recover_window)]\n        new_S = np.where(mask, best_v, S)\n        reversals = np.sum(mask & (new_S == ref) & (ref != S))\n        nf = int(np.sum(new_S != S))\n        S = new_S\n        gamma = optimal_gamma(S @ X.T, T.T)\n        loss = rel_loss(S, gamma, X, T)\n        if loss > prev_loss + 1e-12:\n            hist[\"loss_up\"] += 1\n        prev_loss = loss\n        prev_S.append(S.copy())\n        hist[\"rel_loss\"].append(loss)\n        hist[\"n_flips\"].append(nf)\n        hist[\"reversal_frac\"].append(float(reversals) / max(nf, 1))\n    hist[\"final_sparsity\"] = float(np.mean(S == 0))\n    hist[\"S\"] = S\n    return hist\n\n\ndef run_exact_seq(X, T, S0, max_flips, log_every, recompute_gamma=True):\n    \"\"\"Greedy one-at-a-time with residual compensation (GPTQ/OBS gold).\n\n    Maintains R (d_out,n) and G=R@X (d_out,d_in). Each pick: global argmin ΔL,\n    apply single best flip, recompute that row's γ + residual + G row. Monotone.\n    \"\"\"\n    d_out, d_in = S0.shape\n    S = S0.copy().astype(np.float64)\n    XtX_diag = np.einsum(\"nj,nj->j\", X, X)\n    Tt = T.T  # (d_out, n)\n    P = S @ X.T\n    gamma = optimal_gamma(P, Tt)\n    R = gamma[:, None] * P - Tt\n    G = R @ X\n    traj = {\"rel_loss\": [], \"n_flips\": [], \"loss_up\": 0}\n    base = float(np.sum(Tt ** 2) + 1e-12)\n    cur = float(np.sum(R ** 2) / base)\n    traj[\"rel_loss\"].append(cur)\n    traj[\"n_flips\"].append(0)\n    prev_loss = cur\n    flips = 0\n    while flips < max_flips:\n        best_v, best_delta = delta_grid(S, gamma, R, XtX_diag, G)\n        flat = best_delta.ravel()\n        pos = int(np.argmin(flat))\n        if flat[pos] >= -1e-12:\n            break  # no improving move → converged\n        i, j = divmod(pos, d_in)\n        v = best_v[i, j]\n        a = S[i, j]\n        # apply flip on pre-scale P_i, recompute γ_i (compensation), residual, G row\n        S[i, j] = v\n        Pi = P[i] + (v - a) * X[:, j]\n        P[i] = Pi\n        gi = float((Pi @ Tt[i]) / (Pi @ Pi + 1e-12))\n        gamma[i] = gi\n        R[i] = gi * Pi - Tt[i]\n        G[i] = R[i] @ X\n        flips += 1\n        if flips % log_every == 0:\n            cur = float(np.sum(R ** 2) / base)\n            if cur > prev_loss + 1e-12:\n                traj[\"loss_up\"] += 1\n            prev_loss = cur\n            traj[\"rel_loss\"].append(cur)\n            traj[\"n_flips\"].append(flips)\n    cur = float(np.sum(R ** 2) / base)\n    traj[\"rel_loss\"].append(cur)\n    traj[\"n_flips\"].append(flips)\n    traj[\"final_sparsity\"] = float(np.mean(S == 0))\n    traj[\"total_flips\"] = flips\n    traj[\"S\"] = S\n    return traj\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Self-test: closed-form ΔL vs brute-force recompute\n# ══════════════════════════════════════════════════════════════════════\n\ndef selftest_delta(X, T, S0, gamma, n_probe=200, seed=0):\n    \"\"\"Assert the closed-form ΔL matches a brute-force loss recompute.\"\"\"\n    rng = np.random.RandomState(seed)\n    d_out, d_in = S0.shape\n    S = S0.astype(np.float64)\n    P = S @ X.T\n    R = gamma[:, None] * P - T.T\n    G = R @ X\n    XtX_diag = np.einsum(\"nj,nj->j\", X, X)\n    base_loss = np.sum(R ** 2, axis=1)  # per-row absolute SSE\n    max_err = 0.0\n    for _ in range(n_probe):\n        i = rng.randint(d_out)\n        j = rng.randint(d_in)\n        a = S[i, j]\n        for v in (-1.0, 0.0, 1.0):\n            # closed form\n            step = v - a\n            dl_cf = 2.0 * gamma[i] * step * G[i, j] + (gamma[i] ** 2) * (step ** 2) * XtX_diag[j]\n            # brute force (γ held fixed, as in the closed form)\n            Pi = P[i] + step * X[:, j]\n            ri = gamma[i] * Pi - T.T[i]\n            dl_bf = np.sum(ri ** 2) - base_loss[i]\n            max_err = max(max_err, abs(dl_cf - dl_bf))\n    return max_err\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Main\n# ══════════════════════════════════════════════════════════════════════\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--ckpt\", default=str(REPO / \"checkpoints\" / \"micro\" / \"final\"))\n    ap.add_argument(\"--out\", default=str(REPO / \"results\" / \"ternary-exact-vs-proxy\"))\n    ap.add_argument(\"--layers\", default=\"0,2\")\n    ap.add_argument(\"--matrices\", default=\"gate_proj,value_proj\")\n    ap.add_argument(\"--n-examples\", type=int, default=509)\n    ap.add_argument(\"--seq-cap\", type=int, default=64)\n    ap.add_argument(\"--steps\", type=int, default=120)\n    ap.add_argument(\"--flip-rate\", type=float, default=0.005)\n    ap.add_argument(\"--seq-max-mult\", type=float, default=1.5,\n                    help=\"exact-seq max_flips = mult × n_weights\")\n    args = ap.parse_args()\n\n    out_dir = Path(args.out)\n    out_dir.mkdir(parents=True, exist_ok=True)\n\n    print(\"=\" * 70)\n    print(\"TERNARY SIGN-FITTING: exact 3-way ΔL vs gradient-proxy\")\n    print(\"register: functional | substrate: checkpoints/micro/final\")\n    print(\"=\" * 70)\n\n    cfg = MicroConfig()\n    model = load_micro(Path(args.ckpt))\n    tokens = tokenize_calibration(cfg, args.n_examples, args.seq_cap)\n    print(f\"calibration tokens: {tokens.shape} = {tokens.size} positions\")\n\n    layers = [int(x) for x in args.layers.split(\",\")]\n    matrices = args.matrices.split(\",\")\n\n    results = {\n        \"meta\": {\n            \"register\": \"functional\",\n            \"ckpt\": str(args.ckpt),\n            \"calibration_shape\": list(tokens.shape),\n            \"steps\": args.steps,\n            \"flip_rate\": args.flip_rate,\n            \"git_sha\": None,\n        },\n        \"configs\": {},\n    }\n\n    for layer_idx in layers:\n        for which in matrices:\n            tag = f\"L{layer_idx}.{which}\"\n            print(f\"\\n{'─'*70}\\n{tag}\")\n            X_mx, Wf_mx = capture_layer_io(model, tokens, layer_idx, which)\n            X = np.array(X_mx, dtype=np.float64)        # (n, d_in)\n            Wf = np.array(Wf_mx, dtype=np.float64)      # (d_out, d_in)\n            T = X @ Wf.T                                # (n, d_out)\n            d_out, d_in = Wf.shape\n            n_weights = d_out * d_in\n            budget = max(1, int(args.flip_rate * n_weights))\n            S0 = np.sign(Wf)\n            S0[S0 == 0] = 1.0\n            # init optimal gamma for self-test + baseline\n            gamma0 = optimal_gamma(S0 @ X.T, T.T)\n            base_rel = rel_loss(S0, gamma0, X, T)\n\n            # ── self-test the closed form ──\n            err = selftest_delta(X, T, S0, gamma0)\n            assert err < 1e-6, f\"ΔL closed-form mismatch: {err}\"\n            print(f\"  shape={Wf.shape} n={X.shape[0]} budget={budget}/step \"\n                  f\"| ΔL self-test max_err={err:.2e} ✓\")\n            print(f\"  baseline sign(W) rel_loss = {base_rel:.4f}\")\n\n            t0 = time.time()\n            proxy = run_proxy(X, T, S0, args.steps, budget)\n            batch = run_exact_batch(X, T, S0, args.steps, budget)\n            seq = run_exact_seq(\n                X, T, S0,\n                max_flips=int(args.seq_max_mult * n_weights),\n                log_every=budget,\n            )\n            dt = time.time() - t0\n\n            def summ(h, seq=False):\n                return {\n                    \"final_rel_loss\": h[\"rel_loss\"][-1],\n                    \"min_rel_loss\": min(h[\"rel_loss\"]),\n                    \"loss_up_steps\": h[\"loss_up\"],\n                    \"final_sparsity\": h[\"final_sparsity\"],\n                    \"rel_loss_curve\": [round(v, 5) for v in h[\"rel_loss\"]],\n                    **({\"total_flips\": h.get(\"total_flips\")} if seq else\n                       {\"reversal_frac_mean\": float(np.mean(h[\"reversal_frac\"])),\n                        \"total_flips\": int(np.sum(h[\"n_flips\"]))}),\n                }\n\n            cfg_res = {\n                \"shape\": [d_out, d_in],\n                \"n_calib\": int(X.shape[0]),\n                \"n_weights\": n_weights,\n                \"budget_per_step\": budget,\n                \"baseline_sign_rel_loss\": base_rel,\n                \"proxy\": summ(proxy),\n                \"exact_batch\": summ(batch),\n                \"exact_seq\": summ(seq, seq=True),\n                \"wall_s\": round(dt, 1),\n            }\n            results[\"configs\"][tag] = cfg_res\n\n            print(f\"  PROXY      final={proxy['rel_loss'][-1]:.4f} \"\n                  f\"min={min(proxy['rel_loss']):.4f} up_steps={proxy['loss_up']} \"\n                  f\"rev={np.mean(proxy['reversal_frac']):.3f} \"\n                  f\"flips={int(np.sum(proxy['n_flips']))}\")\n            print(f\"  EXACT-BATCH final={batch['rel_loss'][-1]:.4f} \"\n                  f\"min={min(batch['rel_loss']):.4f} up_steps={batch['loss_up']} \"\n                  f\"rev={np.mean(batch['reversal_frac']):.3f} \"\n                  f\"flips={int(np.sum(batch['n_flips']))}\")\n            print(f\"  EXACT-SEQ   final={seq['rel_loss'][-1]:.4f} \"\n                  f\"up_steps={seq['loss_up']} flips={seq['total_flips']} \"\n                  f\"sparsity={seq['final_sparsity']:.3f}\")\n            print(f\"  ({dt:.1f}s)\")\n\n    # provenance\n    try:\n        import subprocess\n        sha = subprocess.check_output(\n            [\"git\", \"-C\", str(REPO), \"rev-parse\", \"HEAD\"]).decode().strip()\n        results[\"meta\"][\"git_sha\"] = sha\n    except Exception:\n        pass\n\n    out_path = out_dir / \"results.json\"\n    with open(out_path, \"w\") as f:\n        json.dump(results, f, indent=2)\n    print(f\"\\nwrote {out_path}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py
```

### Thinking

 I'll start with a quick smoke test using minimal parameters to catch any bugs early, then scale up to the full configuration.

## Assistant

Let me smoke-test it (one config, few steps) to catch bugs before the full run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ternary_exact_vs_proxy.py --layers 2 --matrices gate_proj --steps 20 --out /tmp/tevp-smoke 2>&1 | grep -v -i \"warning\\|HF_TOKEN\\|unauthenticated\" | tail -25",
  "operation": "status",
  "summary": "smoke test harness",
  "timeout": 180000
}
```

**Summary:** $ uv run python scripts/experiments/t...

**Output:**
```
Exit code: 0
Stdout:
======================================================================
TERNARY SIGN-FITTING: exact 3-way ΔL vs gradient-proxy
register: functional | substrate: checkpoints/micro/final
======================================================================
calibration tokens: (136, 64) = 8704 positions

──────────────────────────────────────────────────────────────────────
L2.gate_proj
Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py", line 499, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py", line 426, in main
    base_rel = rel_loss(S0, gamma0, X, T)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py", line 150, in rel_loss
    return float(np.sum((pred - T) ** 2) / (np.sum(T ** 2) + 1e-12))
                         ~~~~~^~~
ValueError: operands could not be broadcast together with shapes (512,8704) (8704,512)
```

### Thinking

 I'm spotting a dimension mismatch in the rel_loss function—pred comes out as (d_out, n) but T is shaped (n, d_out), so I need to compare against T transposed instead. Let me update the function to use T.T or pass the transposed version directly.

## Assistant

Dimension bug in `rel_loss` — `pred` is (d_out,n), `T` is (n,d_out). Fix:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py",
  "original_content": "    P = S @ X.T                     # (d_out, n)\n    pred = gamma[:, None] * P       # (d_out, n)\n    return float(np.sum((pred - T) ** 2) / (np.sum(T ** 2) + 1e-12))",
  "new_content": "    P = S @ X.T                     # (d_out, n)\n    pred = gamma[:, None] * P       # (d_out, n)\n    Tt = T.T                        # (d_out, n)\n    return float(np.sum((pred - Tt) ** 2) / (np.sum(Tt ** 2) + 1e-12))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/ternary_exact_vs_proxy.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ternary_exact_vs_proxy.py --layers 2 --matrices gate_proj --steps 20 --out /tmp/tevp-smoke 2>&1 | grep -v -i \"warning\\|HF_TOKEN\\|unauthenticated\" | tail -20",
  "operation": "status",
  "summary": "smoke test retry",
  "timeout": 180000
}
```

**Summary:** $ uv run python scripts/experiments/t...

**Output:**
```
Exit code: 0
Stdout:
======================================================================
TERNARY SIGN-FITTING: exact 3-way ΔL vs gradient-proxy
register: functional | substrate: checkpoints/micro/final
======================================================================
calibration tokens: (136, 64) = 8704 positions

──────────────────────────────────────────────────────────────────────
L2.gate_proj
  shape=(512, 128) n=8704 budget=327/step | ΔL self-test max_err=4.15e-12 ✓
  baseline sign(W) rel_loss = 0.2547
  PROXY      final=0.1763 min=0.1753 up_steps=7 rev=0.467 flips=6540
  EXACT-BATCH final=0.1217 min=0.1217 up_steps=0 rev=0.152 flips=6540
  EXACT-SEQ   final=0.0668 up_steps=0 flips=15012 sparsity=0.189
  (12.7s)

wrote /tmp/tevp-smoke/results.json
```

### Thinking

 The smoke test results validate the hypothesis nicely—the closed form is correct based on the self-test, and comparing the three approaches shows a clear pattern: the baseline has moderate loss, the proxy method exhibits non-monotone behavior with frequent oscillations and reversals, while the exact batch approach maintains monotonic improvement with minimal reversals.

The sequential exact method achieves the best result at 0.0668 loss with zero loss-increasing steps and discovers 18.9% sparsity, demonstrating a 2.6× improvement over the proxy approach. The curvature term effectively eliminates the oscillation problem that plagues the proxy method. Now I'm running the full experiment across all four configurations on the specified layers, which should take around 50 seconds, and I'll log the output to track progress.

## Assistant

The closed form self-tests clean (max_err 4e-12) and the result is already decisive even at 20 steps. Let me mark the build done and run the full head-to-head with logging.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && mkdir -p results/ternary-exact-vs-proxy && uv run python scripts/experiments/ternary_exact_vs_proxy.py --layers 0,2 --matrices gate_proj,value_proj --steps 120 2>&1 | grep -v -i \"warning\\|HF_TOKEN\\|unauthenticated\" | tee results/ternary-exact-vs-proxy/run.log | tail -45",
  "operation": "status",
  "summary": "full head-to-head run",
  "timeout": 300000
}
```

**Summary:** $ mkdir -p results/ternary-exact-vs-p...

**Output:**
```
Exit code: 0
Stdout:
======================================================================
TERNARY SIGN-FITTING: exact 3-way ΔL vs gradient-proxy
register: functional | substrate: checkpoints/micro/final
======================================================================
calibration tokens: (136, 64) = 8704 positions

──────────────────────────────────────────────────────────────────────
L0.gate_proj
  shape=(512, 128) n=8704 budget=327/step | ΔL self-test max_err=1.28e-11 ✓
  baseline sign(W) rel_loss = 0.2067
  PROXY      final=0.3855 min=0.1572 up_steps=76 rev=0.286 flips=39240
  EXACT-BATCH final=0.1517 min=0.1463 up_steps=58 rev=0.207 flips=39240
  EXACT-SEQ   final=0.0509 up_steps=0 flips=11287 sparsity=0.143
  (20.3s)

──────────────────────────────────────────────────────────────────────
L0.value_proj
  shape=(128, 512) n=8704 budget=327/step | ΔL self-test max_err=4.69e-13 ✓
  baseline sign(W) rel_loss = 0.1157
  PROXY      final=0.2694 min=0.1157 up_steps=71 rev=0.417 flips=39240
  EXACT-BATCH final=0.1368 min=0.0995 up_steps=60 rev=0.375 flips=39240
  EXACT-SEQ   final=0.0163 up_steps=0 flips=13546 sparsity=0.137
  (17.3s)

──────────────────────────────────────────────────────────────────────
L2.gate_proj
  shape=(512, 128) n=8704 budget=327/step | ΔL self-test max_err=4.15e-12 ✓
  baseline sign(W) rel_loss = 0.2547
  PROXY      final=0.1740 min=0.1732 up_steps=55 rev=0.859 flips=39240
  EXACT-BATCH final=0.1234 min=0.1195 up_steps=51 rev=0.824 flips=39240
  EXACT-SEQ   final=0.0668 up_steps=0 flips=15012 sparsity=0.189
  (23.6s)

──────────────────────────────────────────────────────────────────────
L2.value_proj
  shape=(128, 512) n=8704 budget=327/step | ΔL self-test max_err=7.11e-13 ✓
  baseline sign(W) rel_loss = 0.1744
  PROXY      final=0.2083 min=0.1744 up_steps=61 rev=0.892 flips=39240
  EXACT-BATCH final=0.1757 min=0.1607 up_steps=61 rev=0.937 flips=39240
  EXACT-SEQ   final=0.0400 up_steps=0 flips=18151 sparsity=0.225
  (23.1s)

wrote /Users/mwhitford/src/verbum/results/ternary-exact-vs-proxy/results.json
```

### Thinking

 The EXACT-SEQ approach with gold standard labels and monotone constraints is dramatically outperforming both the proxy and batch baselines across all layer and matrix configurations, achieving 4-7x better reconstruction loss and actually converging while the other methods diverge or stagnate.

PROXY exhibits severe oscillation with 55-76 loss-increasing steps out of 120 and reversal fractions between 0.29-0.89, often ending worse than the baseline because it keeps accepting flips that the linear term favors but the curvature penalizes. EXACT-BATCH improves over proxy but still shows 51-61 loss-up steps and high reversals because batching simultaneous flips within a row violates the independence assumption—the interaction between simultaneous flips reintroduces oscillation, confirming that sequential processing with compensation is necessary for true monotonicity.

The key insight is that the curvature term is decisive: exact 3-way ΔL beats the gradient proxy at matched budget everywhere, and only the sequential exact arm achieves full monotonicity with zero loss-up steps. The proxy's non-monotone acceptance rule is the core issue that real TD compensates for with its anti-oscillation stack, whereas exact ΔL acceptance is naturally monotone. This is layer-local reconstruction scoped to the layer itself, and the register remains functional within that scope.

Now I need to verify the results are well-formed and check whether the proxy curve actually diverges as expected—early minimum followed by higher final loss—then write up the verdict and decide on committing the harness and results.

## Assistant

Decisive and consistent across all four configs. Let me confirm the proxy-divergence shape (early min, then wanders up) from the saved curves before writing the verdict.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nd=json.load(open('results/ternary-exact-vs-proxy/results.json'))\nfor tag,c in d['configs'].items():\n    p=c['proxy']['rel_loss_curve']; b=c['exact_batch']['rel_loss_curve']; s=c['exact_seq']['rel_loss_curve']\n    print(f'{tag}: baseline={c[\\\"baseline_sign_rel_loss\\\"]:.3f}')\n    print(f'  PROXY curve[0,5,20,60,119]= {p[0]:.3f} {p[5]:.3f} {p[20]:.3f} {p[60]:.3f} {p[-1]:.3f}  (argmin at step {p.index(min(p))})')\n    print(f'  BATCH curve[0,5,20,60,119]= {b[0]:.3f} {b[5]:.3f} {b[20]:.3f} {b[60]:.3f} {b[-1]:.3f}')\n    print(f'  SEQ   curve[0,mid,end]    = {s[0]:.3f} {s[len(s)//2]:.3f} {s[-1]:.3f}')\n\"",
  "operation": "status",
  "summary": "inspect proxy divergence curves"
}
```

**Summary:** $ uv run python -c " import json d=js...

**Output:**
```
Exit code: 0
Stdout:
L0.gate_proj: baseline=0.207
  PROXY curve[0,5,20,60,119]= 0.207 0.183 0.276 0.369 0.386  (argmin at step 2)
  BATCH curve[0,5,20,60,119]= 0.207 0.161 0.151 0.152 0.152
  SEQ   curve[0,mid,end]    = 0.207 0.063 0.051
L0.value_proj: baseline=0.116
  PROXY curve[0,5,20,60,119]= 0.116 0.145 0.162 0.249 0.269  (argmin at step 0)
  BATCH curve[0,5,20,60,119]= 0.116 0.138 0.113 0.136 0.137
  SEQ   curve[0,mid,end]    = 0.116 0.021 0.016
L2.gate_proj: baseline=0.255
  PROXY curve[0,5,20,60,119]= 0.255 0.183 0.176 0.174 0.174  (argmin at step 37)
  BATCH curve[0,5,20,60,119]= 0.255 0.175 0.122 0.123 0.123
  SEQ   curve[0,mid,end]    = 0.255 0.094 0.067
L2.value_proj: baseline=0.174
  PROXY curve[0,5,20,60,119]= 0.174 0.205 0.221 0.222 0.208  (argmin at step 0)
  BATCH curve[0,5,20,60,119]= 0.174 0.187 0.182 0.181 0.176
  SEQ   curve[0,mid,end]    = 0.174 0.052 0.040
```

### Thinking

 The PROXY method diverges from baseline across most configurations, often performing worse than the simple sign(W) approach—it either bottoms out early then climbs back up, or settles at an elevated loss value in the gated cases. The gradient-proxy, when evaluated honestly on the full batch, turns out to be actively detrimental beyond its initial minimum point.

In contrast, EXACT-BATCH shows monotone-like behavior and settles around 0.12–0.18, outperforming both proxy and baseline, though it plateaus due to flip interaction constraints and still exhibits occasional loss increases. EXACT-SEQ is the clear winner—it converges monotonically to 0.016–0.067, achieving 3–7× lower loss than baseline and dramatically outpacing proxy, while placing 14–22% of weights at functional zeros.

## Assistant

Your idea works, and the experiment is clean. **Register: functional** (layer-local reconstruction loss under intervention). Self-test confirmed the closed-form ΔL matches brute-force to 1e-11.

## Verdict — exact 3-way ΔL beats the gradient proxy everywhere, and the curvature term is the whole story

Fitting ternary `S∈{−1,0,+1}` + per-row `γ` to four real weight matrices of the micro model (gate_proj router + value_proj value-path, layers 0 & 2), matched flip budget (327/step), starting from `S₀=sign(W)`:

| config | baseline `sign(W)` | PROXY final | EXACT-BATCH | EXACT-SEQ (gold) |
|---|---|---|---|---|
| L0.gate | 0.207 | **0.386** ↑ | 0.152 | **0.051** |
| L0.value | 0.116 | **0.269** ↑ | 0.137 | **0.016** |
| L2.gate | 0.255 | 0.174 | 0.123 | **0.067** |
| L2.value | 0.174 | **0.208** ↑ | 0.176 | **0.040** |

(relative reconstruction loss `‖γ⊙(X@Sᵀ)−T‖²/‖T‖²`)

Three things, all matching the theory we worked out:

**1. The curvature term is decisive.** EXACT beats PROXY at matched budget in every config. The gradient proxy only sees the *slope* at the current point; for ternary the step is large (up to 2) so it systematically overshoots. EXACT-SEQ reaches **3–7× below the `sign(W)` baseline** (0.016–0.067). The thing the proxy throws away is exactly the thing that matters.

**2. The proxy is non-monotone — it reproduces the s191 oscillation wall on demand.** PROXY had **55–76 loss-increasing steps out of 120** and **reversal fractions up to 0.89** (chronic flip-flopping). In 3 of 4 configs it hits its minimum at step 0–2 and then *wanders upward past the naive baseline* — it actively destroys the etch. EXACT-SEQ had **0 loss-increasing steps** and converges. This is the punchline: the entire S2 anti-oscillation stack (cooldown, backoff, thermometer, conviction) exists to suppress oscillation that the gradient-proxy *acceptance rule* creates — exact ΔL acceptance is monotone for free.

**3. The "0" places itself.** With `{−1,0,+1}` as genuine candidates, EXACT-SEQ discovered **14–22% functional sparsity** by `argmin` alone — no heuristic magnitude threshold. Sign-decision and zero-placement unify, exactly as predicted.

## The one important nuance the experiment surfaced

**Batching the flips reintroduces oscillation.** EXACT-BATCH (top-B improving flips per step, computed independently) still had 51–61 loss-up steps and high reversals — because flipping B positions simultaneously breaks the "everything else fixed" assumption behind each ΔL. Only **EXACT-SEQ** — one flip at a time with rank-1 residual compensation (the GPTQ/OBS move) — is truly monotone. So the precise claim is:

> *"Evaluate all 3 signs and take the best" dissolves the oscillation wall **when done coordinate-wise with error compensation**. Exact-but-batched is much better than the proxy but still interferes with itself.*

## Honest caveats

- This is **layer-local reconstruction**, not global next-token loss — the cheap exact target, by design. It aligns with the score-matching/trace-guided direction the project already validated (s198 v3b), and s208 showed the global CE endpoint objective is degenerate, so layer-local is the right surrogate, not a compromise.
- The PROXY arm is a *faithful but idealized* analog of TD (full-batch, no EMA/SNR/cooldown). The point isn't "deployed TD oscillates this badly" — it's that **the acceptance rule at TD's core is non-monotone, and the S2 stack is compensating for that**, whereas exact ΔL is monotone by construction.

## Where this points

The clean integration is: keep TD's cheap gradient SNR as the **proposal** (which positions to look at), but replace the gradient-driven **acceptance** with coordinate-wise exact ΔL + compensation. That's an OBQ/GPTQ-family inner loop wrapped in TD's proposal/budget machinery.

Files: `scripts/experiments/ternary_exact_vs_proxy.py`, `results/ternary-exact-vs-proxy/{results.json,run.log}`.

Want me to (a) commit this harness + results, (b) push toward a GPTQ-style sequential-with-compensation TD acceptance inner loop and test it in an actual training step, or (c) something else? I'll hold off on any `mementum/` knowledge page until you approve — but this feels like it earns one.

## User

capture to knowledge and commit, this is a new exploration target.


### Thinking

 Michael's approved this as a new exploration target, so I need to create a knowledge page in the explore directory with proper frontmatter, update the state.md bootloader to point to this session, and commit everything together—the harness code, results, knowledge page, and state changes. I'm also thinking through how to classify these changes at the commit gate, distinguishing between code/data modifications.

For the commit structure, I'm weighing whether to do one atomic commit or split it into separate ones. Since this is a cohesive exploration—the harness, results, and synthesis all form one discovery—I'll go with a single commit using the 💡 insight symbol, which captures that we've found something new. The first line needs to be standalone and changelog-readable. Before I finalize the commit message, I should check the explore folder to match the existing style and frontmatter conventions from pages like ternary-descent.md.

I'm planning to write the exploration page, update the INDEX.md to reference it, and update state.md with a new session 213 headline and the latest timestamp. Let me pull the exact current top lines of state.md and check how INDEX.md is structured so I can make precise edits.

## Assistant

Approved. I'll write the synthesis page, update the index + state bootloader, then commit. Let me first check the index format and the exact state.md header to edit precisely.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "limit": 40
}
```

**Summary:** Reading INDEX.md (0-40)

**Output:**
```
---
title: "Knowledge Index — Reading Order"
status: active
category: meta
tags: [index, orientation, knowledge-map]
---

# Knowledge Index

> Master reading order for the verbum project's synthesized knowledge.
> Read after `state.md`. Organized top-down: foundational → specific.
>
> **Status key:** ✅ complete | 🔨 stub (skeleton, needs expansion) | 📋 planned

---

## Tier 1 — What Is This Project?

These pages answer: *what are we doing, why does it work, and what have we proved?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 1 | [project-thesis.md](project-thesis.md) | ✅ | The central claim: pretraining IS beta reduction, topology dominates, ternary extraction works |
| 2 | [crystal-universality.md](crystal-universality.md) | ✅ | Why the combinator crystal is a mathematical constant, not a learned artifact |
| 3 | [mathematical-convergences.md](mathematical-convergences.md) | ✅ | Eight independent lines of mathematical evidence converging on the same structure |
| 3b | [symbol-isolation.md](symbol-isolation.md) | ✅ | Prose activates combinator engine 8× more than lambda. Formal notation is pre-reduced input. |

## Tier 2 — How Does It Work?

These pages answer: *what is the mechanism, and how do we exploit it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 4 | [retrieval-lattice.md](retrieval-lattice.md) | ✅ | Universal knowledge encoding: 4-zone lattice, relation directions, ternary mirror stack |
| 4b | [moire-addressing.md](moire-addressing.md) | ✅ | SwiGLU moiré = holographic fact index. 2.4× selectivity, quadratic addressing, capacity estimates |
| 4c | [combinator-addressing.md](combinator-addressing.md) | ✅ | Retrieval IS β_apply. λ form activates compute for same fact. Two crystals (hard/soft). |
| 4d | [hologram-reader-vsm.md](hologram-reader-vsm.md) | ✅ | VSM tensor statechart for reading opcode maps from any model. Cross-model comparison. |
| 4d2 | [opcode-instrument.md](opcode-instrument.md) | ✅ | Live VSM wrapper: watch opcodes execute per token in real-time. The EKG for LLMs. |
| 4e | [ternary-plate-extraction.md](ternary-plate-extraction.md) | ✅ | Direct FFN→ternary extraction, execution hierarchy, crystal error correction, λ-gated retrieval |
| 4f | [function-discovery.md](function-discovery.md) | ✅ | Two-level program architecture: task directions (early/SILENT) → operation directions (late/COMMIT). 4.76× separation in moiré space. |

[CONTENT TRUNCATED] Showing lines 1 to 40 of 136 total lines. Use line_offset=40 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 14
}
```

**Summary:** Reading state.md (0-14)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-10 | Session: 212 (two pieces — #12f scale ext: topology
> share PLATEAUS not →1.0; + universal axis NAMED (CV-R²=0.81, model-free
> ends_punct) — both DONE)
>
> (Session 205 was synthesis-only — papers/theory for the compression track,
> not tied to the audit: `gtsm-search-space.md`, `tsp-trajectory-distillation.md`,
> `error-correction-theory.md`, audit #11 registered. No experiments; not stated.)

## Where we are


[CONTENT TRUNCATED] Showing lines 1 to 14 of 3079 total lines. Use line_offset=14 parameter to read more content.
```

### Thinking

 I need to check how the explore section is structured in INDEX.md so I can figure out where to add the new page.

## Assistant

Let me see the explore/training section of the index to place the new page correctly.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "line_offset": 40,
  "limit": 96
}
```

**Summary:** Reading INDEX.md (40-136)

**Output:**
```
| 5 | [holographic-error-correction.md](holographic-error-correction.md) | ✅ | The extract→correct→fold cycle: error correction on a discrete holographic code |
| 6 | [mechanism-extraction.md](mechanism-extraction.md) | ✅ | Full micro-model mechanism: alternating overlay, eigenplane rotation, KIBC temporal |
| 7 | [computed-beam.md](computed-beam.md) | ✅ | Analytical FFN from crystal eigendecomposition, 500× speedup, signed accumulation |
| 8 | [extraction-methodology.md](extraction-methodology.md) | ✅ | How to extract from a teacher: what works, three confusions resolved, the pipeline |
| 8b | [holographic-computer.md](holographic-computer.md) | ✅ | Unified theory: crystal=ISA, FFN=projector, attn=CPU, progressive collapse to WHNF |
| 8c | [phi-information-partition.md](phi-information-partition.md) | ✅ | Signs=1/φ, γ=noise, zeros=holographic phase, crystal sieve 10.7×. The decomposition. |
| 8d | [standing-wave-magnitudes.md](standing-wave-magnitudes.md) | ✅ | Magnitudes as standing wave: crystal=boundary conditions, zeros=nodes, GD=finding resonant modes |
| 8e | [gradient-zero-map.md](gradient-zero-map.md) | ✅ | GD deposits near-zero gradients at irreducible compute points. Two-regime depth structure. |
| 8f | [topology-gradient-separation.md](topology-gradient-separation.md) | ✅ | Freeze lattice for GD to work. Punctuated equilibrium protocol. Cross-disciplinary validation. |
| 8g | [residual-covariance-rank.md](residual-covariance-rank.md) | ✅ | ORTHO phase is rank-1. V lives in null space. 67.7% unconstrained. Partial negative for U derivation. |

## Tier 3 — What Are We Running?

These pages answer: *what is the current system, and how do you operate it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 8 | [v14-architecture.md](v14-architecture.md) | ✅ | Current v14 student: Qwen3.6-27B teacher, 593M ternary positions, 375× compression |
| 9 | [training-protocols.md](training-protocols.md) | ✅ | How to train without rediscovering failures: phases, TD rules, known failure modes |
| 9b | [trace-guided-etching.md](trace-guided-etching.md) | ✅ | Copy computation not weights. Trace loss + delta plates + TD. 11-dim target vs 248K-dim. |

## Tier 4 — Deep Dives (explore/)

Comprehensive pages on specific topics. Read as needed, not sequentially.

| Page | Status | One-line |
|------|--------|----------|
| [explore/VERBUM.md](explore/VERBUM.md) | ✅ | Founding research program: hypothesis chain, 4-level plan (historical) |
| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ | Unified computational model: FFN=plates, crystal=states, Q=beam, gate=beamformer |
| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |
| [explore/ffn-beta-reduction-indexing.md](explore/ffn-beta-reduction-indexing.md) | ✅ | Holographic FFN indexing: lens profile, ρ=0.83, universal neurons |
| [explore/categorical-geometry-probes.md](explore/categorical-geometry-probes.md) | ✅ | Curry-Howard 100%, adjunctions rank-1, hyperbolic norm encoding |
| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ⚠️ | SVD spectrum head ratio ~0.6 — REAL & non-random, but **geometric-φ-constant REFUTED** (audit #6, s207: power-law not geometric, value floats 0.52→0.71). Keep low-rank head, retire φ-constant |
| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |
| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |
| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |
| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | ⚠️ | Original v15 design: passive strides, Stack B reduction (partially reverted) |
| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ | What was tried/reverted/kept from sessions 152-156 + when to revisit |
| [explore/kernel-training.md](explore/kernel-training.md) | ✅ | Composed plate training: 4.4× speedup, gradient cosine 0.97 |
| [explore/structured-training.md](explore/structured-training.md) | ✅ | Five backward-pass optimizations (camera = projector) |
| [explore/crystal-irreducibility-proof.md](explore/crystal-irreducibility-proof.md) | 🔨 | Theory: crystal = irreducibility floor of KIBC. Proof strategy + kernel optimization via JIT hooks |
| [explore/delta-plate-lifecycle.md](explore/delta-plate-lifecycle.md) | 🔨 | Masked extraction + continuous training + factual corrections via delta plates |
| [explore/grating-cascade.md](explore/grating-cascade.md) | ✅ | Compound grating collapse: 16D→1.4D, V is K-typed, attention doubles cross-PC coupling |
| [explore/moire-training-shortcuts.md](explore/moire-training-shortcuts.md) | 🔨 | Five training speedup shortcuts from moiré understanding |
| [explore/continuations-as-composed-plates.md](explore/continuations-as-composed-plates.md) | ✅ | The FP↔transformer bridge: composed plates ARE continuations, CPS = residual stream |
| [explore/fp-optimization-map.md](explore/fp-optimization-map.md) | ✅ | 10 FP techniques mapped to transformer: laziness, fusion, partial eval, CSE, NbE, etc. |
| [explore/optimization-negative-results.md](explore/optimization-negative-results.md) | ✅ | Why FP optimizations fail on Apple Silicon: all 6 tested, all negative, root causes |
| [explore/ffn-moire-isa.md](explore/ffn-moire-isa.md) | ✅ | FFN as moiré grating ISA: decoding programs from weights, attention flow, fixed-point proof |
| [explore/kernel-replacement-optimization.md](explore/kernel-replacement-optimization.md) | 🔨 | Replace interpreted grating chains with compiled kernel shortcuts via VSM hooks |
| [explore/vsm-statechart-tensor.md](explore/vsm-statechart-tensor.md) | ✅ | Triple isomorphism: VSM ↔ Harel statechart ↔ tensor. Dual-runtime (Clojure + Python). mmap plates. |
| [explore/safetensors-training.md](explore/safetensors-training.md) | ✅ | Safetensors-backed continuous training: sync/20, snapshot/200, checkpoint/500, distributed fold. |
| [explore/mmap-continuous-training.md](explore/mmap-continuous-training.md) | ✅ | mmap training design: file layout, safetensors export, MLX bridge, open questions. |

## Tier 5 — Future Pages (planned)

| Page | Priority | One-line |
|------|----------|----------|
| `holographic-storage-mechanism.md` | ~~important~~ mostly covered | FFN as holographic plate: lens profile, gate=beamformer, output beamformers (see moire-addressing.md) |
| `ternary-architecture-rationale.md` | important | Why ternary {-1,0,+1}, why it works, gradient routing interpretation |
| `combinator-geometry.md` | important | KIBC in transformer geometry: temporal ordering, depth map, bootstrap |
| `stridestack-architecture.md` | important | Multi-scale attention: O(L×W), stride overlaps, ascending/descending stacks |
| `known-failures.md` | nice-to-have | Concise bug/collapse/fix reference for all hard-won lessons |
| `session-delta-vision.md` | nice-to-have | Context as 2MB delta files, no KV cache, git-trackable sessions |
| `ecosystem-vision.md` | nice-to-have | End-state product: community deltas, domain plates, reader LLM |

---

## How to Use This Index

1. **New session, familiar project:** Read `state.md` → skim this index → read Tier 1 if stale
2. **Brand new to the project:** Read pages 1–9 in order, then deep dives as needed
3. **Specific question:** Find the relevant page by topic, follow cross-references
4. **Adding knowledge:** Create page → add to appropriate tier → update this index

## Cross-Reference Map

```
project-thesis ──→ crystal-universality ──→ mathematical-convergences
       │                    │                         │
       ▼                    ▼                         ▼
holographic-error-correction ←── mechanism-extraction ←── computed-beam
       │                                │
       ▼                                ▼
extraction-methodology ──→ v14-architecture ──→ training-protocols

retrieval-lattice ──→ moire-addressing ──→ holographic-computer
       │                    │
       ▼                    ▼
(capacity estimates)   (gate×up = quadratic index)
```

## Memory Files

~105 episodic memories in `memories/`. One insight per file, symbol-prefixed content.
These are raw observations — the knowledge pages above are their synthesis.
Search with: `git grep -i "{query}" -- mementum/memories/`
```

### Thinking

 I'm creating a new exploration page for exact ternary fitting that goes in the explore directory, with frontmatter covering title, status, category, tags, and dependencies. The page will synthesize the core idea around exact three-way ΔL acceptance compared to gradient proxies, along with the feasibility insight that this approach has a closed-form solution requiring just one matrix multiplication without per-position overhead.

I'll include the mathematical decomposition of ΔL into linear and curvature components, present the experimental results showing monotonicity and sparsity patterns, and explain the key nuance that batching reintroduces oscillation while sequential processing with compensation delivers the best results. I'll also connect this work to the broader context of temporal difference learning, the S2 stack, the oscillation problem, and the GPTQ-OBQ lineage, while noting the caveats around layer-local assumptions and idealized proxies.

After finishing the page, I need to update the INDEX.md file to add this to Tier 4 explorations and update state.md with a header and session 213 headline.

## Assistant

Now the synthesis page (a new exploration target), then the index and bootloader updates.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/exact-ternary-fitting.md",
  "content": "---\ntitle: \"Exact Ternary Fitting — 3-way ΔL Acceptance Beats the Gradient Proxy\"\nstatus: active\ncategory: algorithm\ntags: [ternary-descent, td, exact-fitting, curvature, oscillation, gptq, obq, coordinate-descent, monotone, structural-zeros, exploration-target]\nrelated:\n  - ternary-descent.md\n  - td-oscillation-problem.md\n  - trace-guided-etching.md\n  - training-protocols.md\n  - score-matching-compression.md\n  - two-registers-of-topology.md\ndepends-on:\n  - ternary-descent.md\n  - td-oscillation-problem.md\ncreated: session 213\n---\n\n# Exact Ternary Fitting — 3-way ΔL Acceptance\n\n> Session 213. New exploration target. Michael's idea: instead of using a\n> **gradient proxy** to decide which signs TernaryDescent flips, directly\n> evaluate the loss for all three ternary values `{−1, 0, +1}` at each\n> position and take the one that improves loss most. Tested on the micro\n> model — it works, the curvature term is the whole story, and it dissolves\n> the s191 oscillation wall by construction (when done coordinate-wise).\n>\n> Register: **functional** (layer-local reconstruction loss under intervention).\n\n## The idea\n\nTernaryDescent (`ternary-descent.md`) decides flips from a gradient EMA: it\naccumulates `direction = EMA(grad)`, `magnitude = EMA(grad²)`, and flips where\nthe signal-to-noise ratio is high and the descent direction opposes the current\nsign. This is a **proxy** — the gradient is a *linear* (first-order) estimate of\nhow the loss changes, evaluated at the current point.\n\nFor a **ternary** weight the step is large (`v − a` can be 2), so the linear\nestimate systematically overshoots: the gradient says \"flip helps\" because it\nonly sees the slope, but the actual discrete step lands somewhere the slope did\nnot predict. **This is the root cause of the s191 oscillation** (TD flips → GD\npushes back → TD flips again), and the entire S2 anti-oscillation stack\n(cooldown, backoff, thermometer, conviction) exists to *suppress* it.\n\nThe idea: don't proxy. For each candidate position evaluate the **actual loss**\nat `v ∈ {−1, 0, +1}` and take `argmin`. Accept only if it improves → monotone.\n\n## The feasibility insight — no forward pass per position\n\nThe naive reading (\"a forward pass per sign per position\") is infeasible\n(~10⁸ positions × 3). It is also unnecessary. For a **layer-local quadratic\nreconstruction target** the exact loss-delta has a closed form computable for\n*all* positions at once.\n\nOne linear layer, effective ternary weight `S` (per-row scale `γ`), real\ncalibration input `X` (n × d_in), teacher target `T = X @ W_floatᵀ` (n × d_out).\nThe rows are independent. Per row `i`, with residual `r_i = γ_i·(X@S[i,:]) − T[:,i]`,\nchanging `S[i,j]` from `a` to `v`:\n\n```\nΔL_ij(v) = 2·γ_i·(v−a)·⟨r_i, X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²\n            └────── linear (= gradient) ──┘   └──── curvature ────┘\n```\n\n- `⟨r_i, X[:,j]⟩` for the whole `(d_out × d_in)` grid is **one matmul `Rᵀ@X`**.\n- `‖X[:,j]‖²` is a precomputed `d_in`-vector; `γ_i` a `d_out`-vector.\n- Evaluate the three `v`, take `argmin`. Done.\n\n**The linear term IS the gradient TD already uses. The curvature term is exactly\nwhat the proxy throws away** — and for ternary's large step it is not negligible;\nit is the missing piece. (Verified in the harness: the closed form matches a\nbrute-force per-position loss recompute to ~1e-11.)\n\nThis is the OBQ / GPTQ / OBS family (\"pick the quantization that minimizes layer\noutput error, with Hessian-aware compensation\"). The micro experiment is an\nindependent re-derivation; the lineage is the proven, scalable form.\n\n## The experiment\n\n`scripts/experiments/ternary_exact_vs_proxy.py` (register: functional). Fit\nternary `S∈{−1,0,+1}` + per-row `γ` to four real weight matrices of the micro\nmodel (`gate_proj` router + `value_proj` value-path, layers 0 & 2), against real\ncalibration activations (8704 token positions from `compile-train`). Start from\n`S₀ = sign(W_float)`; matched flip budget (327/step); per-row optimal `γ`\nrecomputed each step. Three arms:\n\n- **PROXY** — rank candidates by `|gradient|`, flip toward `−sign(grad)`. No\n  curvature check (faithful full-batch analog of TD's acceptance rule).\n- **EXACT-BATCH** — closed-form 3-way `argmin ΔL`, take top-B *improving* per step.\n- **EXACT-SEQ** — greedy **one-at-a-time with rank-1 residual compensation**\n  (GPTQ/OBS gold standard), monotone to convergence.\n\n### Results (relative reconstruction loss `‖γ⊙(X@Sᵀ)−T‖²/‖T‖²`)\n\n| config | baseline `sign(W)` | PROXY final | EXACT-BATCH | EXACT-SEQ |\n|---|---|---|---|---|\n| L0.gate  | 0.207 | **0.386** ↑ | 0.152 | **0.051** |\n| L0.value | 0.116 | **0.269** ↑ | 0.137 | **0.016** |\n| L2.gate  | 0.255 | 0.174 | 0.123 | **0.067** |\n| L2.value | 0.174 | **0.208** ↑ | 0.176 | **0.040** |\n\n| arm | loss-up steps / 120 | reversal frac | converged loss |\n|---|---|---|---|\n| PROXY | 55–76 | 0.29–0.89 | diverges past baseline in 3/4 |\n| EXACT-BATCH | 51–61 | 0.21–0.94 | plateaus ~0.12–0.18 |\n| EXACT-SEQ | **0** | — (monotone) | **0.016–0.067**, 14–22% sparsity |\n\n### Three findings\n\n1. **The curvature term is decisive.** EXACT beats PROXY at matched budget in\n   every config. EXACT-SEQ reaches **3–7× below the `sign(W)` baseline**. The\n   quantity the proxy discards is the quantity that matters.\n\n2. **The proxy is non-monotone — it reproduces the oscillation wall on demand.**\n   55–76 of 120 steps *increase* loss; reversal fractions up to 0.89 (chronic\n   flip-flop). In 3/4 configs PROXY hits its minimum at step 0–2 then **wanders\n   upward past the naive baseline** — it actively destroys the etch. EXACT-SEQ\n   has **0 loss-up steps** and converges. The S2 stack is machinery to suppress\n   oscillation that the gradient-proxy *acceptance rule* creates; exact ΔL\n   acceptance is monotone for free.\n\n3. **The \"0\" places itself.** With `{−1,0,+1}` as genuine candidates, EXACT-SEQ\n   discovered **14–22% functional sparsity** by `argmin` alone — no magnitude\n   threshold. Sign-decision and zero-placement unify (cf. the heuristic 30%\n   structural zeros in `trace-guided-etching.md`).\n\n## The important nuance — batching reintroduces oscillation\n\nEXACT-BATCH (top-B improving flips per step, each ΔL computed independently)\nstill had 51–61 loss-up steps and high reversals. Flipping B positions at once\nbreaks the \"everything else fixed\" assumption behind each ΔL — the within-row\nflip interaction. Only **EXACT-SEQ** (one flip at a time, recompute the row's\nresidual/γ/`Rᵀ@X` row after each — the GPTQ error-compensation move) is truly\nmonotone. Precise claim:\n\n> **\"Evaluate all 3 signs, take the best\" dissolves the oscillation wall when\n> done coordinate-wise with error compensation. Exact-but-batched is much better\n> than the proxy but still interferes with itself.**\n\nThe compensation is cheap: a flip is a rank-1 update to the residual, and with\n`XtXᵀ` (d_in × d_in) precomputed, each accepted flip updates one row of the\n`Rᵀ@X` grid in O(d_in). Full coordinate descent to convergence is fast.\n\n## Caveats (honest scope)\n\n- **Layer-local reconstruction, not global next-token loss.** This is the cheap\n  *exact* target by design. It aligns with `score-matching-compression.md` (v3b,\n  dense per-layer score matching = 1.44× held-out) and `trace-guided-etching.md`;\n  and audit #8/#7 (`audit-registry.md`) showed the global CE endpoint objective\n  is degenerate (memorizes), so a layer-local surrogate is the cure, not a\n  compromise. The closed form is exact only for the quadratic layer target; a\n  global objective reintroduces downstream nonlinearity (forward replay).\n- **The PROXY arm is an idealized full-batch analog of TD** (no EMA/SNR/cooldown).\n  The claim is not \"deployed TD oscillates this badly\" — it is that *the\n  acceptance rule at TD's core is non-monotone, and S2 is compensating for that*.\n- Verified on a ~1M-param micro model; scale behavior untested.\n\n## Where this points (open leads)\n\n- **Wire it into TD as the acceptance rule.** Keep TD's gradient SNR as the cheap\n  **proposal** (which positions are worth looking at), replace the gradient-driven\n  **acceptance** with coordinate-wise exact ΔL + compensation. An OBQ/GPTQ inner\n  loop wrapped in TD's proposal/budget/holographic-etch machinery. Test in an\n  actual training step (`scripts/v15/train_td.py`).\n- **Does monotone exact fitting remove the need for the S2 stack** (cooldown,\n  backoff, thermometer)? If acceptance is monotone by construction, most of the\n  anti-oscillation scaffolding may be redundant.\n- **Cross-layer compensation** (full GPTQ): propagate the reconstruction error\n  forward so later layers fit the *already-quantized* upstream — closes the gap\n  between per-layer-local and global.\n- **Scale test:** does the 3–7× gap over baseline (and over proxy) hold on a real\n  teacher layer (Qwen3-0.6B/8B)?\n- **Register check:** the exact loss here is reconstruction; a functional re-test\n  should confirm the fitted ternary layer's *downstream PPL* improves, not just\n  its local SSE.\n\n## Files\n\n| File | Content |\n|------|---------|\n| `scripts/experiments/ternary_exact_vs_proxy.py` | harness: capture layer I/O, 3 arms, ΔL self-test |\n| `results/ternary-exact-vs-proxy/results.json` | per-config curves + summary metrics |\n| `results/ternary-exact-vs-proxy/run.log` | run transcript |\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/exact-ternary-fitting.md
```

## Assistant

Now add it to the index and update the state bootloader.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |",
  "new_content": "| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |\n| [explore/exact-ternary-fitting.md](explore/exact-ternary-fitting.md) | ✅ | **NEW (s213) exploration target.** Exact 3-way ΔL acceptance > gradient proxy: curvature term decisive, monotone (dissolves s191 oscillation) when coordinate-wise + compensation (GPTQ/OBQ), \"0\" self-places. 3–7× below sign(W) baseline on micro. |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-10 | Session: 212 (two pieces — #12f scale ext: topology\n> share PLATEAUS not →1.0; + universal axis NAMED (CV-R²=0.81, model-free\n> ends_punct) — both DONE)",
  "new_content": "> Last updated: 2026-06-10 | Session: 213 (NEW EXPLORATION TARGET — exact ternary\n> fitting: 3-way ΔL acceptance beats TD's gradient proxy; curvature term decisive;\n> monotone/no-oscillation when coordinate-wise + compensation; \"0\" self-places)\n>\n> (Session 212: two pieces — #12f scale ext: topology share PLATEAUS not →1.0;\n> + universal axis NAMED (CV-R²=0.81, model-free ends_punct) — both DONE)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now insert the session 213 headline at the top of "Where we are" in state.md, and re-read to confirm the exact anchor.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 14,
  "limit": 12
}
```

**Summary:** Reading state.md (14-26)

**Output:**
```

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-
> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**
> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /
> H31@L27 subject value-transfer ✅ semantically REAL; s207 did **#6 SVD φ-ratio

[CONTENT TRUNCATED] Showing lines 15 to 26 of 3082 total lines. Use line_offset=26 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open",
  "new_content": "**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n> **▶ SESSION 213 HEADLINE — NEW EXPLORATION TARGET: EXACT TERNARY FITTING.**\n> Register: functional (declared up front — layer-local reconstruction loss under\n> intervention). Michael's idea: replace TD's **gradient proxy** for sign-flip\n> decisions with **direct evaluation of the loss at all three values `{−1,0,+1}`,\n> take the argmin**. The feasibility insight: for a layer-local quadratic\n> reconstruction target there is a **closed form** for the exact ΔL of every\n> position at once (one matmul `Rᵀ@X`), no per-position forward passes:\n> `ΔL_ij(v) = 2γ_i(v−a)⟨r_i,X[:,j]⟩ + γ_i²(v−a)²‖X[:,j]‖²`. The **linear term IS\n> the gradient TD already uses; the curvature term is what the proxy throws away**\n> — and for ternary's large step it is the decisive missing piece. (= the\n> OBQ/GPTQ/OBS family, re-derived independently.)\n> - **Tested** (`ternary_exact_vs_proxy.py`, micro model, 4 configs = gate_proj\n>   router + value_proj value-path × layers 0/2, real activations, matched\n>   327-flip budget, start `S₀=sign(W)`). ΔL closed form self-tested vs\n>   brute-force to ~1e-11.\n> - **✅ Curvature decisive:** EXACT beats PROXY at matched budget in every config;\n>   EXACT-SEQ (gold) reaches **3–7× below the sign(W) baseline** (rel-recon\n>   0.016–0.067 vs baseline 0.116–0.255).\n> - **✅ Monotone / dissolves the s191 oscillation wall:** PROXY had **55–76 of 120\n>   steps INCREASE loss**, reversal frac up to 0.89, and in 3/4 configs **wandered\n>   ABOVE the naive baseline** (the bare gradient-proxy acceptance rule actively\n>   destroys the etch; the whole S2 anti-oscillation stack is compensating for it).\n>   EXACT-SEQ had **0 loss-up steps** and converges.\n> - **◑ Nuance:** monotonicity holds only **coordinate-wise + compensation**\n>   (EXACT-SEQ, GPTQ-style rank-1 residual update). EXACT-BATCH (top-B independent\n>   flips/step) is much better than proxy but still has 51–61 loss-up steps —\n>   simultaneous flips interfere (the flip-interaction the compensation fixes).\n> - **✅ Bonus:** the \"0\" places itself — EXACT-SEQ discovered **14–22% functional\n>   sparsity** by argmin alone (no magnitude threshold; cf. heuristic 30%\n>   structural zeros).\n> - **Caveats:** layer-local reconstruction ≠ global NTP (the cheap exact target by\n>   design, aligned with score-matching/trace-guided; global needs forward replay);\n>   PROXY arm is an idealized full-batch analog of TD; micro-scale only.\n> - Knowledge: `explore/exact-ternary-fitting.md`. Results:\n>   `results/ternary-exact-vs-proxy/{results.json,run.log}`. Harness:\n>   `scripts/experiments/ternary_exact_vs_proxy.py`.\n> - **▶ NEXT:** wire exact-ΔL acceptance into TD (`scripts/v15/train_td.py`) — keep\n>   the gradient SNR as the cheap PROPOSAL, replace acceptance with coordinate-wise\n>   exact-ΔL + compensation; test if it removes the need for the S2 stack; then a\n>   real-teacher-layer scale test + downstream-PPL (functional) confirmation.\n>   **Declare register before building any control.**\n\n> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 Both edits went through, but the read happened in parallel before the changes took effect. I'm re-reading the state.md edit region to verify everything synced correctly and that the headline block is in the right place.

## Assistant

Both applied. Let me verify the state.md edit landed coherently (re-read after write), then commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '17,22p' mementum/state.md && echo \"...\" && sed -n '54,60p' mementum/state.md && echo \"=== git status ===\" && git status --short",
  "operation": "status",
  "summary": "verify edits + git status"
}
```

**Summary:** $ sed -n '17,22p' mementum/state.md &...

**Output:**
```
Exit code: 0
Stdout:
**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 213 HEADLINE — NEW EXPLORATION TARGET: EXACT TERNARY FITTING.**
> Register: functional (declared up front — layer-local reconstruction loss under
> intervention). Michael's idea: replace TD's **gradient proxy** for sign-flip
...
>   `results/ternary-exact-vs-proxy/{results.json,run.log}`. Harness:
>   `scripts/experiments/ternary_exact_vs_proxy.py`.
> - **▶ NEXT:** wire exact-ΔL acceptance into TD (`scripts/v15/train_td.py`) — keep
>   the gradient SNR as the cheap PROPOSAL, replace acceptance with coordinate-wise
>   exact-ΔL + compensation; test if it removes the need for the S2 stack; then a
>   real-teacher-layer scale test + downstream-PPL (functional) confirmation.
>   **Declare register before building any control.**
=== git status ===
 M mementum/knowledge/INDEX.md
 M mementum/state.md
?? mementum/knowledge/explore/exact-ternary-fitting.md
?? results/ternary-exact-vs-proxy/
?? scripts/experiments/ternary_exact_vs_proxy.py
```

## Assistant

Edits coherent. Now stage the relevant files and commit. This is a new exploration with its harness, results, and synthesis — a single 💡 insight commit.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/ternary_exact_vs_proxy.py results/ternary-exact-vs-proxy/ mementum/knowledge/explore/exact-ternary-fitting.md mementum/knowledge/INDEX.md mementum/state.md && git status --short",
  "operation": "add",
  "summary": "stage exploration files"
}
```

**Summary:** Git add: stage exploration files

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/INDEX.md
A  mementum/knowledge/explore/exact-ternary-fitting.md
M  mementum/state.md
A  results/ternary-exact-vs-proxy/results.json
A  results/ternary-exact-vs-proxy/run.log
A  scripts/experiments/ternary_exact_vs_proxy.py
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy\n\nNew exploration target (s213). Replace TernaryDescent's gradient-EMA proxy\nfor sign-flip decisions with direct evaluation of the loss at all three\nternary values {−1,0,+1}, take the argmin. For a layer-local quadratic\nreconstruction target the exact ΔL of every position is a closed form (one\nmatmul Rᵀ@X) — no per-position forward passes. The linear term IS the\ngradient TD already uses; the curvature term γ²(v−a)²‖X[:,j]‖² is what the\nproxy discards, and for ternary's large step it is decisive (= OBQ/GPTQ/OBS,\nre-derived).\n\nTested on the micro model (4 configs, real activations, matched budget):\n- curvature decisive: EXACT-SEQ reaches 3–7× below the sign(W) baseline\n- monotone / dissolves the s191 oscillation wall: PROXY had 55–76/120 loss-up\n  steps and wandered above baseline; EXACT-SEQ had 0 loss-up steps\n- nuance: monotone only coordinate-wise + compensation (GPTQ rank-1 update);\n  batched exact still self-interferes\n- the \"0\" self-places: 14–22% functional sparsity by argmin alone\n\nregister: functional. Caveat: layer-local reconstruction ≠ global NTP.\nNEXT: wire exact-ΔL acceptance into TD (SNR proposes, exact-ΔL disposes).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit exploration"
}
```

**Summary:** Git commit: commit exploration

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 9: unexpected EOF while looking for matching `''
bash: -c: line 28: syntax error: unexpected end of file
```

### Thinking

 I'm realizing the issue is with how the apostrophe in "TD's" interacts with the single-quoted heredoc syntax — the shell is getting confused about quote matching when the command is wrapped in double quotes.

Rather than wrestling with nested quoting, I'll write the commit message to a temporary file and use `git commit -F` to read it from there, which sidesteps all these quoting complications.

## Assistant

The heredoc tripped on an apostrophe. I'll use a message file instead.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_TEVP",
  "content": "💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy\n\nNew exploration target (s213). Replace TernaryDescent's gradient-EMA proxy\nfor sign-flip decisions with direct evaluation of the loss at all three\nternary values {−1,0,+1}, take the argmin. For a layer-local quadratic\nreconstruction target the exact ΔL of every position is a closed form (one\nmatmul Rᵀ@X) — no per-position forward passes. The linear term IS the\ngradient TD already uses; the curvature term γ²(v−a)²‖X[:,j]‖² is what the\nproxy discards, and for ternary's large step it is decisive (= OBQ/GPTQ/OBS,\nre-derived).\n\nTested on the micro model (4 configs, real activations, matched budget):\n- curvature decisive: EXACT-SEQ reaches 3–7× below the sign(W) baseline\n- monotone / dissolves the s191 oscillation wall: PROXY had 55–76/120 loss-up\n  steps and wandered above baseline; EXACT-SEQ had 0 loss-up steps\n- nuance: monotone only coordinate-wise + compensation (GPTQ rank-1 update);\n  batched exact still self-interferes\n- the \"0\" self-places: 14–22% functional sparsity by argmin alone\n\nregister: functional. Caveat: layer-local reconstruction ≠ global NTP.\nNEXT: wire exact-ΔL acceptance into TD (SNR proposes, exact-ΔL disposes).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_TEVP
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F .git/COMMIT_EDITMSG_TEVP && rm -f .git/COMMIT_EDITMSG_TEVP && git log --oneline -1",
  "operation": "commit",
  "summary": "commit via message file"
}
```

**Summary:** Git commit: commit via message file

**Output:**
```
Exit code: 0
Stdout:
[main 96293e0] 💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy
 6 files changed, 2101 insertions(+), 3 deletions(-)
 create mode 100644 mementum/knowledge/explore/exact-ternary-fitting.md
 create mode 100644 results/ternary-exact-vs-proxy/results.json
 create mode 100644 results/ternary-exact-vs-proxy/run.log
 create mode 100644 scripts/experiments/ternary_exact_vs_proxy.py
96293e0 💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy
```

## Assistant

Committed (`96293e0`). Let me close out the task tracker.Done. Captured and committed.

## Session summary

**New exploration target landed** — your idea, tested, synthesized, committed (`96293e0`).

**What we proved (register: functional):** replacing TD's gradient proxy with direct 3-way `argmin ΔL` works, and the reason is the **curvature term** the proxy discards. For a layer-local quadratic target it's a closed form — one matmul, no per-position forward passes. On the micro model across 4 configs:
- EXACT-SEQ reached **3–7× below the `sign(W)` baseline**; PROXY often ended *worse* than baseline.
- PROXY had **55–76 of 120 loss-increasing steps** (the s191 oscillation wall, reproduced on demand); EXACT-SEQ had **0** — monotone by construction.
- The "0" **self-places** (14–22% functional sparsity by argmin alone).
- Key nuance: monotonicity needs **coordinate-wise + compensation** (GPTQ-style); batched exact still self-interferes.

**Committed:**
- `scripts/experiments/ternary_exact_vs_proxy.py` (harness, ΔL self-test vs brute-force)
- `results/ternary-exact-vs-proxy/{results.json,run.log}`
- `mementum/knowledge/explore/exact-ternary-fitting.md` (synthesis) + INDEX entry
- `mementum/state.md` bootloader headline for s213

**Where it points (recorded as NEXT):** wire exact-ΔL into TD as the *acceptance* rule — gradient SNR proposes which positions to look at, exact-ΔL + compensation disposes — and test whether that makes the whole S2 anti-oscillation stack redundant. Then a real-teacher-layer scale test with a downstream-PPL (functional) confirmation, since today's result is layer-local reconstruction, not global NTP.

That's a clean stopping point. When you want to pick up the integration, `state.md` will boot you straight back into it.