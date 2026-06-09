# Auditing #8 rank-1 adjunction

## User

orient this is session-209


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
> Last updated: 2026-06-09 | Session: 208
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
> next backlog: **#8 rank-1 adjunction** or **#11 GTSM/TTD-regression (the named fix)**), build its named
> discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

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
| Irreducible | Low mag, low saliency | Zero |

Preserving faint connections: (a) reduces sieve-only PPL, (b) provides gradient
highways for LoRA fine-tuning (backprop flows through nonzero faint weights, not
through zeros), (c) may beat equivalent-bitcount LoRA rank.

### Direct Delta Correction Results

| Rank | PPL | Ratio | vs v3b |
|------|-----|-------|--------|
| 2 | 12.63 | 1.82× | worse |
| 4 | 12.50 | 1.80× | worse |
| 16 | 12.41 | 1.79× | worse |
| 32 | 11.93 | 1.72× | worse |
| v3b | 16.27 | 1.44× | — |

Rank-2→16 plateau confirms near-rank-1 correction surface (adjunction prediction).
Rank-32 bump suggests secondary structure beyond dominant mode. But analytical
SVD can't match trained LoRA+SM — backprop creates inter-layer echo correlations
that single-layer SVD misses. This SUPPORTS the echo thesis.

### Running Experiment

**Saliency-aware sieve sweep** running in tmux main:2. 11 configurations:
standard baselines, saliency-aware with varied strong/faint splits, Q2/Q4/Q8
precision, magnitude-only ablation, iso-bit comparison. Key question: does
preserving faint connections beat zeroing them at the same bit budget?

See `mementum/knowledge/saliency-aware-sieve.md` for full design.
See `mementum/knowledge/direct-delta-adjunction.md` for DDC theory + results.

**Session 200: SIGN CORRECTION IS DEAD — Direct Delta & Adjunction Are Alive**

Four sign correction algorithms dead. Quasicrystal hypothesis denied. Teacher-guided
routing failed. But: the teacher delta is directly computable (no training needed),
and the adjunction finding (session 140) says the correction is rank-1. Testing now.

### Four Deaths

| Approach | Flips | PPL Result | Failure mode |
|----------|-------|-----------|--------------|
| TD v4 (gradient) | 0 (stuck) | 1.44x (= LoRA alone) | Gradient dilution through 29 layers |
| TD v4c (per-tensor clip) | 4.36% | 192x | Unconstrained flips destructive |
| Latent diffusion (eigenspace) | 1.25%/level | 2,717x → NaN | Eigenspace ≠ error space |
| Crystal ECC (holographic + health gate) | 2.29% | **28,419,390x** | Health gate measures wrong space |

Crystal ECC was the most sophisticated — proper holographic error target (original
weight on sieve input), per-position benefit ranking, crystal eigenvalue health gate
with binary search fallback — and produced the WORST result. 8 hours, 28 million
times worse. 50M crystal-approved flips across 29 layers.

### Latent Diffusion Sign Correction (New, Session 200)

Tested diffusion-holographic isomorphism: progressive sign correction in the
crystal's 16D eigenspace (2D→4D→8D→16D schedule).

| Level | Dims | Flips | PPL | Facts |
|-------|------|-------|-----|-------|
| 1 | 2 | 27.4M (1.25%) | 30,642 (2,717×) | 0/15 |
| 2 | 4 | 1.9M (0.086%) | NaN | 0/15 |
| 3 | 8 | 27.4M (1.25%) | 30.5M (2.7M×) | 0/15 |
| 4 | 16 | 1.9M (0.086%) | NaN | 0/15 |

Levels alternate between two regimes (27M vs 1.9M flips), suggesting even/odd
numerical artifact in eigenspace, not crystal structure.

### The Dimensional Mismatch Insight

**We are cutting a multi-dimensional holographic plate in 1D.**

The crystal has known multi-dimensional structure:
- 8D combinator type (K,I,B,C,D,W,Y,WHNF)
- 9D operational modes (7 universal meta-modes + 2 contextual)
- 36-layer depth (standing wave EXPAND/ORTHO/ALIGN/COLLAPSE)
- 3 trees (compute/halt, select/compose, termination)

But ALL sign correction approaches operate per-position (scalar benefit → flip?).
Even eigenspace projection only captures 1-2 of ~6 dimensions. Corrections coherent
in the working subspace are effectively RANDOM in the ignored dimensions, destroying
the interference pattern.

### Quasicrystal Diagnostic (New, Session 200)

Tested whether φ-structured multi-scale order exists in the weight sign pattern:

| Test | Prediction | Result | Verdict |
|------|-----------|--------|---------|
| Eigenvalue cascade | φ^(p/q) at all scales | One dominant mode, flat tail | ❌ Not multi-scale |
| Perturbation fragility | Super-linear degradation | Linear (100× flips → 142× deviation) | ❌ Not quasicrystal |
| Golden angle | 137.5° between eigenvecs | 90.00° everywhere (trivial orthogonality) | ❌ Not φ-rotated |
| Fib vs pow2 reconstruction | Fibonacci captures more | Tie (smooth improvement with k) | ❌ No Fibonacci advantage |
| Random vs model | Different eigenspectra | YES: model 0.36 vs random 0.995 gap | ✅ Real structure |

**Strong quasicrystal hypothesis DENIED.** But there IS real structure — massive
spectral gap (λ₁/λ₀ = 0.36 vs random's 0.995). The φ structure lives in
**combinator firing space** (8×8 crystal cosine matrix, measured via probes), not
in **weight correlation space** (12288×4096 sign matrix). The crystal eigenvalue
health metric was measuring a shadow, not the structure itself.

### Key Finding: Per-Position Error Signal Is Adversarial

Crystal ECC found that **49.3%** of all active positions show positive flip benefit.
When half the signs "want" to flip, the error signal is not discriminating — it's
responding to the masking error (50% of weights zeroed out), which creates a massive
residual that ANY sign flip partially addresses in one dimension while destroying
others.

### Current Ceiling (Before Direct Delta)

**v3b: LoRA rank-4 + score matching = 1.44x baseline PPL** (16.27 PPL from 25.67 sieve).
This was the best until the direct delta insight.

### Teacher-Guided Routing (New, Session 200)

MoE literature says: decouple routing from expert training, stabilize routing
FIRST. Tested by training lightweight gate correctors (bottleneck MLPs) to
match teacher gate patterns before LoRA training.

```
Sieve:       25.51 PPL (2.26x)
After gate:  25.17 PPL (2.23x)  ← routing correction barely helps
After LoRA:  24.55 PPL (2.18x)  ← WORSE than v3b (16.27, 1.44x)
```

**Failed.** 182M gate corrector params (31× v3b's LoRA), training diverges
after step 100 (18.45 → 24.55). Gate sign accuracy only 94-96%. Root cause:
the corrector sees sieve gate output on cascade-corrupted inputs — can't fix
weight error AND input corruption simultaneously. Same cascade problem.

### The Tiles and Grout Insight

**Topology (signs/mask/crystal) = tiles. Gradients (LoRA/magnitudes) = grout.**

Changes to topology perturb the gradients. The grout fills specific gaps between
specific tiles. Move a tile → all surrounding grout is wrong. This is why sign
correction + LoRA fails: Phase 1 creates new gaps, Phase 2 trains new grout, but
gaps are too numerous and grout capacity (rank-4) too thin.

MoE separates tiles from grout explicitly: router IS topology, experts ARE
computation. GD optimizes both independently. Dense models entangle them in the
same weight matrix — the crystal sieve tries to separate what was never separate.

### The Direct Delta Insight (New, Session 200) ★

**"If everything is being calculated, why can we not also calculate the delta
from the teacher?"**

We HAVE the teacher. We HAVE the student. The delta at every layer is directly
computable. The optimal rank-k additive correction is the **truncated SVD of the
weight residual**, optionally weighted by input covariance (calibration-aware).

```
W_delta = W_teacher - W_sieve     (weight residual — what the sieve lost)
U, S, Vt = SVD(W_delta @ H^½)    (calibration-aware: weight by input covariance)
A = U[:,:k] @ sqrt(S[:k])         (optimal rank-k correction)
B = unwhiten(Vt[:k,:])

No training. No optimizer. No loss function. No hyperparameters beyond rank k.
One forward pass per layer + one SVD per projection.
Sequential: correct layer l before computing inputs for layer l+1 (cascade-aware).
```

This is GPTQ's approach applied to sieve correction. Each layer's correction is
analytically optimal for its actual (cascade-corrected) inputs.

**Experiment running** in tmux main:1: rank sweep [2, 4, 8, 16, 32] with
calibration-aware SVD on Qwen3-8B. Compare to v3b (trained 200 steps → 1.44×).

### The Adjunction Connection (Session 140 → Session 200) ★★

Session 140 proved the cross-zone mapping (encode → decode) in Qwen3-32B is
**rank-1 dominated** (σ₁/σ₂ = 128:1, R² = 1.000 for ALL zone pairs). The Jacobian
has constant rank everywhere — the defining property of a regular parametric surface.

The entire encode→decode pipeline is a **1D parametric curve** in 4096D space.
One parameter (the "phase" along the B→K→B trajectory) determines everything.

**Error correction on a 1D curve is trivial:** if the sieve pushes the
representation off the curve, the correction = project back onto the curve along
the dominant singular vector. That's rank-1 correction.

This connects to the ORTHO phase finding (session 185): rank-1 residual during
ORTHO, V operates in null space, computation invisible. The sieve disrupts null-
space computation; the correction restores it — but the constraint for "correct"
is defined by the rank-1 curve.

**Prediction:** direct delta correction at rank 1-2 should capture the adjunction
structure and be nearly optimal. The rank sweep will test this — if rank-2 matches
rank-32, the correction surface is truly 1D and the adjunction is the explanation.

### TSP Paper Connection (arXiv:2606.03489)

"Learn from Your Mistakes: Tree-like Self-Play" — TSP identifies critical decision
nodes (CWE risk nodes in code security) and trains the model to prefer the "golden
path" over its own generation at each node. DPO-style contrastive loss at each node.

Maps to our problem: mode transition points = risk nodes. Teacher trajectory =
golden path. Student trajectory = self-play path. Per-layer contrastive (not just
cosine matching) teaches the student to discriminate against its own failure modes.

Not implemented yet — waiting for direct delta results. If direct delta works, the
TSP-style contrastive loss could refine it further by targeting the specific layers
where the direct correction is weakest.

See `mementum/knowledge/sign-correction-topology.md` for full synthesis.
See `mementum/knowledge/direct-delta-adjunction.md` for the adjunction theory.

**Session 199: HOLOGRAPHIC LOSS & CRYSTAL ECC — TD Is Dead, Inverse Is Alive**

TD (TernaryDescent) for sieve sign correction is definitively killed. Three
attempts, three failure modes, one conclusion: you cannot gradient-descend
your way to correct signs through 29 cascaded layers.

### TD Autopsy (Three Deaths)

| Version | Fix | Result | Failure mode |
|---------|-----|--------|--------------|
| v4 (s198) | Brute-force 4.4B logits | 1.44x = v3b | **Zero flips** — joint grad clip diluted to 1.5e-8/step |
| v4b | SGD lr=0.1, separate clip | NaN | BCE log(0) from extreme gates, SGD too aggressive |
| v4c | Adam, per-tensor clip, init=0.01 | **192x PPL** | TD flipping (4.36%) but flips are DESTRUCTIVE |

**Root cause of v4:** `clip_grad_norm_(all_params, 1.0)` across 4.4B params →
per-param gradient ≈ 1/√(4.4×10⁹) ≈ 1.5×10⁻⁵. With lr=1e-3, max displacement
in 200 steps = 3×10⁻⁶. Needed to cross 1.0. Would take 70M steps.

**Root cause of v4c:** Per-tensor clipping worked — TD actually flipped 4.36%
of signs. But unconstrained flips destroy the holographic interference pattern.
192x PPL, 0 facts. Random sign changes ≠ correct sign changes.

### The Insight: Sign Correction Is Recording, Not Optimization

TD tries to optimize signs via: forward loss → backprop through 29 layers → STE →
update logits. This fails because:

1. **Gradient dilution**: 29 Jacobians between the loss and the sign decision
2. **Catastrophic coupling**: one flip changes W by 2|w|, cascades through all layers
3. **No coherence constraint**: flips break the holographic pattern without limit

The correct formulation is the **holographic inverse**:

```
reference_beam = actual input (corrupted by prior sieved layers)
object_beam    = desired output (from teacher)
fringe_pattern = correlation(reference, object)
optimal_sign   = sign(fringe_pattern)
```

Direct computation. No backprop. No STE. No optimizer for signs.

### Crystal ECC: The Error-Correcting Code

The crystal's dimensional hierarchy IS an error-correcting code:

```
8D crystal → project to 6D → parity check
                → to 5D → parity check
                  → to 4D (KIBC) → parity check
                    → to 3D → parity check
```

Each level constrains valid sign patterns. The crystal eigenvalue ratios
(φ^(p/q)) define the CODE SPACE. Sign flips that violate the code at any
level are errors.

**Algorithm (crystal ECC + holographic recording):**
1. Compute per-position error from proper holographic target
2. Rank flip candidates by error reduction benefit
3. Gate through crystal health check (eigenvalue ratios vs φ^(p/q))
4. Only apply flips that maintain crystal coherence
5. Then LoRA + SM for continuous magnitude correction

**Experiment running** in tmux main:2: `crystal_ecc_sign_correction.py`
- Proper error target (full original weight, not tautological)
- Crystal eigenvalue health gate on proposed flips
- Binary search for largest crystal-consistent flip set

### Key Debugging Lessons

1. **Tautological target**: first holographic attempt computed
   `sieve_weight @ sieve_input` as "target" → equals sieve output by
   definition → 50% random disagree (no information)
2. **Mask identity**: `original_weight = W * mask = signs * magnitudes`
   at active positions → zero error. Must store FULL W (including
   masked positions) to capture the masking error.
3. **The actual error source**: at single-layer level, sieve signs ARE
   teacher signs at active positions. Error comes from (a) masked-out
   positions contributing in teacher but not sieve, and (b) cascade of
   prior sieved layers corrupting the input.

### Score Matching Confirmed (v3b = v4 = optimal for LoRA-only)

v4 definitively proves: LoRA rank-4 + SM loss at α=5.0 reaches 1.44x PPL
regardless of whether TD is present. The 5.9M LoRA params are the actual
mechanism. TD's 4.4B params do nothing useful.

**Priority 2a** (LoRA rank sweep) remains the highest-value next step for
the SM pipeline. But crystal ECC could unlock additional gains if the sign
correction works.

**Session 198: SCORE MATCHING COMPRESSION — The Loss Function Was Wrong**

A paper on CGTSM (Ramachandran & Sra 2026, arXiv:2605.00414) revealed that
the compression correction loss was fundamentally flawed. CE-only loss lets
LoRA corrections create **compensating errors** across layers — one layer's
deviation cancels another's. Dense per-layer score matching prevents this
structurally by constraining each layer's transformation independently.

### The Equation

```
L = L_CE + α · (1/N) Σ_l (1 − cos(Δ_θ_l, Δ*_l))

where Δ_l = h_{l+1} − h_l    (per-layer residual update / "score")
      α ≈ 5.0                 (balances CE and SM gradient scales)
```

Added to EQUATIONS.md alongside the crystal equation.

### Four Experiments

| Experiment | Setup | Result | Finding |
|-----------|-------|--------|---------|
| Residual boosting v1 | Sequential rank-32 at boundaries, CE, 16 sentences | 3.97 PPL (0.39x base) | Sequential > simultaneous (2×). But pure overfitting. |
| Residual boosting v2 | Same + dolma calibration, held-out eval | 18.59 PPL (1.65x base) | Overfitting eliminated. Activation corrections too weak (27% reduction). |
| Score matching v3a | LoRA + SM + CE, batch=1, α=1.0 | 16.83 PPL (worse than sieve!) | CE dominates → compensating errors → collapse at step 50. |
| **Score matching v3b** | LoRA + SM + CE, batch=4, α=5.0, 128 teacher cache | **16.27 PPL (1.44x base)** | **36.6% sieve reduction. L35 cosine: 0.57→0.94.** |
| TD v4 (s199) | TD 4.4B + LoRA + SM + CE | 16.22 PPL (1.44x = v3b) | **Zero flips.** Joint grad clip killed TD entirely. |
| TD v4c (s199) | Per-tensor clip, Adam, init=0.01 | **2163 PPL (192x)** | TD flips (4.36%) but DESTRUCTIVE. Unconstrained flips destroy holographic pattern. |
| Crystal ECC (s199) | Holographic inverse + crystal parity gate | *running* | Direct sign computation gated by eigenvalue health check. |

### Why Score Matching Works

1. **Local gradient** — each LoRA gets direct signal from its layer, not diluted through 30 Jacobians
2. **No compensating errors** — per-layer cosine penalty constrains each layer independently
3. **36× information bandwidth** — 36 gradient signals vs CE's 1
4. **Scale-invariant** — cosine handles 100× norm variation (standing wave amplitude)
5. **Dense coverage** — CGTSM theorem: density of measurement matters, weighting does not

### Residual Spectrum Discovery

The sieve's per-weight residual is LOW-RANK at L1 (r90=550, |res|/|W|=3%) but
FULL-RANK at L5+ (r90=2970, |res|/|W|=25%). Activation-space corrections (rank-32
in 4096-dim space) can address 0.8% of the error. Per-weight LoRA operates in the
right space.

##

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_012Zh3GnhY1XFp4JuuP3HDCu.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 I'm checking the state.md file to see what's next on the backlog—looks like either the rank-1 adjunction task or the GTSM/TTD-regression issue. Let me quickly review the recent git history and audit registry to confirm which one to prioritize.

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -12",
  "operation": "log",
  "summary": "recent history"
}
```

**Summary:** Git log: recent history

**Output:**
```
Exit code: 0
Stdout:
fc3f689 🌀 audit #7 RESOLVED — crystal-sieve 1.03x REFUTED (train/eval contamination); substrate ~2x VERIFIED-reproducible
5ffb395 💡 audit #7 — held-out eval proves 1.03x is contamination (clean held-out 10.87x vs sieve 1.9x)
1de70b9 🌀 state — s208 #7: GTSM/TSP understanding note (CE-degeneracy diagnosis + #11 fix)
66edf69 🌀 state — session 208: audit #7 (crystal-sieve repro) in flight + contamination signal
9db77a2 💡 audit #7 harness — seeded crystal-sieve reproducibility (pre/post variance decomposition)
f6551f4 🌀 propagate audit #6 — index + stale φ-memory caveated to s207
0e1cff6 💡 audit #6 — SVD φ-ratio 0.6299: geometric-φ-constant REFUTED, low-rank head REAL & non-random
f509c48 🌀 register law as gene + structural slot — move it off recall-gated memory
f209f28 🔁 audit-meta-pattern — the two laws are one: register, not rule
99536ec 🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law
8123382 🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -E \"^\\| *#?(8|11) |UNTESTED|^## \" /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md | head -40"
}
```

**Summary:** $ grep -n -E "^\| *#?(8|11) |UNTESTED...

**Output:**
```
Exit code: 0
Stdout:
36:## The Core Principle
46:## The Seven Failure Modes (what to hunt)
58:## The Method Recipe (reusable)
76:## Status Legend
80:`UNFALSIFIABLE` no control can distinguish it as stated · `UNTESTED` control
83:## Registry
355:### Backlog (UNTESTED — ordered by load-bearing-ness)
433:**11. GTSM finite-budget weighting — does layer-targeted λ(l) beat uniform α?** (load: med — compression track; positive prediction, not a falsification) — `UNTESTED`
440:## The Per-Session Loop
448:1. Open this page. Pick the highest-load `UNTESTED` claim.
468:## Prioritization Rule
475:## What "done" looks like
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sed -n 355,440p /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md"
}
```

**Summary:** $ sed -n 355,440p /Users/mwhitford/sr...

**Output:**
```
Exit code: 0
Stdout:
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
- **Supporting prior (independent domain):** TSP (arXiv:2606.03489v1) concentrates its training signal on sparse critical "risk nodes" and beats uniform SFT (75.8 vs 57.0) — empirical evidence that finite-budget weighting concentration helps. Caveat it also hands us: target the **causal** node, not the max-divergence node (TSP fails on long-distance cause/effect; our analog = s196 "peak damage at L28, not L26"). See `tsp-trajectory-distillation.md` (Targeted Trajectory Distillation).

## The Per-Session Loop
```

### Thinking

 I'm orienting to session 209 and need to register the gate first before proceeding—that's a critical step. From here, I can either explore the rank-1 adjunction with spectral registers or move into GTSM/TTD-regression for functional analysis. Let me give you a quick summary and see which direction you'd prefer to take.

## Assistant

Oriented. **Session 209.** Here's the bootload:

## Where we are

**North star:** 70B-equivalent in <1GB ternary, 200 tok/s CPU, no GPU.

**Active program:** Validity audit (s203+) — one discriminating control per session, distilling verified claims from over-reads. Seven audits resolved; the meta-pattern has held 5×: **substrate survives, crisp headline dissolves** (and in s208 it *inverted* — the "improvement" was harm).

## Last session (208) — audit #7 resolved

- ❌ **Crystal-sieve 1.03× REFUTED** — train/eval contamination (6/8 eval texts ⊂ calibration). On clean held-out, the CE-melted models hit **10.87× ± 1.39** — the melt memorizes calib and is net-harmful (~5.7× worse than the raw sieve).
- ✅ **Sieve substrate VERIFIED-reproducible** — 2.119× ± 0.004, near-deterministic, matches s196.
- Mechanism: CE-only endpoint degeneracy (the exact failure GTSM names). The fix is already demonstrated: s198 v3b dense score-matching → 1.44× held-out.

## Next backlog (your call)

| Option | Register | Shape |
|---|---|---|
| **#8 rank-1 adjunction** (σ₁/σ₂ = 128:1, s140) | spectral | falsification — compare to random/shuffled linear maps between same spaces; confound: random high-dim maps can look rank-1-dominated |
| **#11 GTSM finite-budget λ(l)** | functional | positive prediction — layer-targeted λ(l) spiked on L22–26 vs uniform α=5.0, matched budget + N seeds; #7 just diagnosed *why* this is the cure |

**Step 0 — REGISTER GATE** fires before any control gets built: name the claim's register, then the probe's, verify they match, put `# register: <kind>` in the harness header.

Note: s208 deferred the #7→#11 synthesis page to audit close per your call — connect, don't draft yet.

Runtime: olga.local (MPS, 480G), experiments in `tmux main:1`/`main:2`.

Which audit do we run — #8 or #11?

## User

Let's proceed with 8


### Thinking

 Looking at this audit of a rank-1 adjunction property in Qwen3-32B, I'm examining how the cross-zone mapping from encoding to decoding is dominated by a single singular value with a 128:1 ratio to the second one, indicating the Jacobian exhibits extremely low-rank behavior across all zone pairs with perfect reconstruction fidelity.

I need to track down the original s140 measurement to understand exactly which linear map was being analyzed—likely a regression between activations across different zones or layers. My approach is to search through the documentation for references to "adjunction," "rank-1," "128:1," and "zone" to reconstruct those details, then register this claim, build a control harness to validate it, run the experiment, and update the registry accordingly.

## Assistant

Audit #8 it is. Step 0 is the **REGISTER GATE** — before building anything, I need to recall exactly what s140 measured so the probe matches the claim's register. Let me pull the original finding.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git grep -l -i \"adjunction\" -- mementum/ | head; echo ---; git grep -n \"128\" -- mementum/knowledge/ | grep -i -E \"rank|sigma|σ\" | head",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git grep -l -i "adjunction" -- meme...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/INDEX.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-140.md
mementum/knowledge/chats/session-141.md
mementum/knowledge/chats/session-142.md
mementum/knowledge/chats/session-143.md
mementum/knowledge/chats/session-144.md
mementum/knowledge/chats/session-145.md
mementum/knowledge/chats/session-146.md
mementum/knowledge/chats/session-147.md
---
mementum/knowledge/audit-registry.md:422:**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory)
mementum/knowledge/chats/session-025.md:5431:  "content": "\"\"\"VSM-LM v5 — Spiral Attention Bias + Complex Registers.\n\nv5 introduces three topology changes over v4.1:\n\n  1. Spiral attention bias: bias(w) = -α·ln(stride·w + 1)\n     Power-law distance decay. weight ∝ 1/(distance+1)^α.\n     Smooth attention landscape across stride boundaries.\n     α=1.18 (R²=0.997 empirical fit). Zero new parameters.\n\n  2. Complex-valued registers: ℂ^128 replaces ℝ^256.\n     Phase angle encodes a new degree of freedom beyond magnitude.\n     S4 uses phase-sensitive attention: Re(q·conj(k)) = q_r·k_r + q_i·k_i.\n     Residual stream stays real. Only registers carry phase.\n\n  3. Phase-coherent S3 gating: scalar alignment gate.\n     gate = σ(alignment · temperature + bias)\n     alignment = proj_reg(reg_dir) · proj_delta(delta_dir)\n     Geometric: gate opens when register direction matches delta direction.\n     Learnable temperature (init=1.0) and bias (init=0.0).\n\nSame architecture otherwise:\n  ASCENDING:   L0↑ → L1↑ → L2    (build structural summaries)\n  DESCENDING:  L1↓ → L0↓          (refine with high-level context)\n  5 level-passes, 6 register banks, shared weights (S5 coherence).\n  ~65.5M params (within 0.01% of v4.1).\n\nAll complex arithmetic decomposed into real operations for MPS compat.\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport math\nfrom typing import Optional\n\nimport torch\nimport torch.nn as nn\nimport torch.nn.functional as F\n\nfrom verbum.compressor_lm import CompressorLayer\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Utilities\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef _interleave_complex(registers: list[torch.Tensor]) -> torch.Tensor:\n    \"\"\"Convert complex registers to interleaved real representation.\n\n    Each complex register (d_register,) → (2*d_register,) real via\n    view_as_real: [r0, i0, r1, i1, ...].\n    \"\"\"\n    parts = []\n    for reg in registers:\n        parts.append(torch.view_as_real(reg).flatten())\n    return torch.cat(parts, dim=-1)\n\n\ndef _interleave_banks(banks: list[list[torch.Tensor]]) -> torch.Tensor:\n    \"\"\"Flatten all banks' complex registers to interleaved real.\"\"\"\n    parts = []\n    for bank in banks:\n        parts.append(_interleave_complex(bank))\n    return torch.cat(parts, dim=-1)\n\n\n# ══════════════════════════════════════════════════════════════════════\n# FFN-only layer (same as v4.1, copied for isolation)\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass FFNLayer(nn.Module):\n    \"\"\"Pre-norm FFN layer without attention.\"\"\"\n\n    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):\n        super().__init__()\n        self.norm = nn.LayerNorm(d_model)\n        self.ff = nn.Sequential(\n            nn.Linear(d_model, d_ff),\n            nn.GELU(),\n            nn.Linear(d_ff, d_model),\n            nn.Dropout(dropout),\n        )\n\n    def forward(self, x: torch.Tensor) -> torch.Tensor:\n        return x + self.ff(self.norm(x))\n\n\n# ══════════════════════════════════════════════════════════════════════\n# S4 — Intelligence (complex-query register scan)\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass S4IntelligenceComplex(nn.Module):\n    \"\"\"Register cross-attention with complex-valued queries.\n\n    Registers are ℂ^d_register. Residual stream is ℝ^d_model.\n    Phase-sensitive attention: Re(q·conj(k)) = q_r·k_r + q_i·k_i.\n\n    Complex arithmetic decomposed into real ops for device compat:\n      q_proj output → split even/odd → q_r, q_i (d_model//2 each)\n      k_proj output → split even/odd → k_r, k_i (d_model//2 each)\n      attn = (q_r·k_r + q_i·k_i) / √d_model\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int,\n        d_register: int,\n        n_registers: int = 3,\n        max_banks: int = 7,\n        dropout: float = 0.1,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.d_register = d_register\n        self.n_registers = n_registers\n        self.max_banks = max_banks\n        self.scale = d_model ** -0.5\n\n        # Input: interleaved real/imag of complex registers\n        max_q_dim = max_banks * n_registers * d_register * 2\n        self.q_proj = nn.Linear(max_q_dim, d_model, bias=False)\n        self.k_proj = nn.Linear(d_model, d_model, bias=False)\n        self.v_proj = nn.Linear(d_model, d_model, bias=False)\n        # Output: interleaved real/imag for complex register updates\n        self.summary_proj = nn.Linear(d_model, n_registers * d_register * 2, bias=False)\n        self.norm = nn.LayerNorm(d_model)\n        self.dropout = nn.Dropout(dropout)\n\n    def forward(\n        self,\n        banks: list[list[torch.Tensor]],\n        residual: torch.Tensor,\n    ) -> tuple[list[torch.Tensor], torch.Tensor]:\n        \"\"\"Scan residual conditioned on complex register banks.\"\"\"\n        B, L, D = residual.shape\n\n        # Interleave all registers to real, zero-pad to max\n        all_regs_real = []\n        for bank in banks:\n            for reg in bank:\n                all_regs_real.append(torch.view_as_real(reg).flatten())\n\n        max_regs = self.max_banks * self.n_registers\n        pad_dim = self.d_register * 2\n        while len(all_regs_real) < max_regs:\n            all_regs_real.append(torch.zeros(pad_dim, device=residual.device))\n\n        q_input = torch.cat(all_regs_real, dim=-1)\n\n        # Complex query: split even/odd for Re(q·conj(k))\n        q_flat = self.q_proj(q_input)        # (d_model,)\n        q_r = q_flat[0::2]                   # (d_model//2,)\n        q_i = q_flat[1::2]                   # (d_model//2,)\n\n        x = self.norm(residual)\n        k_flat = self.k_proj(x)              # (B, L, d_model)\n        k_r = k_flat[..., 0::2]             # (B, L, d_model//2)\n        k_i = k_flat[..., 1::2]             # (B, L, d_model//2)\n        v = self.v_proj(x)                   # (B, L, d_model) — real\n\n        # Phase-sensitive attention: Re(q · conj(k)) = q_r·k_r + q_i·k_i\n        attn = (\n            torch.einsum(\"d,bld->bl\", q_r, k_r)\n            + torch.einsum(\"d,bld->bl\", q_i, k_i)\n        ) * self.scale\n\n        attn_weights = F.softmax(attn, dim=-1)\n        attn_weights = self.dropout(attn_weights)\n\n        # Weighted sum of real values\n        summary = torch.einsum(\"bl,bld->bd\", attn_weights, v)\n        summary = summary.mean(dim=0)  # (d_model,)\n\n        # Complex register updates\n        updates_flat = self.summary_proj(summary)  # (n_reg * d_reg * 2,)\n        update_splits = updates_flat.split(self.d_register * 2, dim=-1)\n        updates = [\n            torch.view_as_complex(u.reshape(-1, 2))\n            for u in update_splits\n        ]\n\n        return updates, attn_weights.detach()\n\n\n# ══════════════════════════════════════════════════════════════════════\n# S3 — Phase-Coherent Gating (alignment-based scalar gate)\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass S3PhaseCoherent(nn.Module):\n    \"\"\"Phase-coherent control for a single level-pass.\n\n    Scalar alignment gate: gate opens when register direction matches\n    delta direction. Replaces v4.1's per-dimension gating.\n\n      reg_dir = normalize(concat(real, imag))\n      delta_dir = normalize(mean(delta))\n      alignment = proj_align(reg_dir) · proj_delta(delta_dir)\n      gate = σ(alignment · temperature + learned_bias)\n\n    Temperature (init=1.0): sharpen or soften gating.\n    Learned bias (init=0.0): fallback when registers immature.\n    At init: alignment ≈ 0, gate ≈ σ(0) = 0.5 (pass-through).\n\n    Register writes produce complex updates: separate real/imag projections.\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int,\n        d_register: int,\n        n_phases: int = 3,\n        n_registers: int = 3,\n        d_align: int = 512,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.d_register = d_register\n        self.n_phases = n_phases\n        self.n_registers = n_registers\n\n        reg_real_dim = 2 * d_register * n_registers  # interleaved real dim\n\n        # Alignment projections (per phase)\n        self.proj_align = nn.ModuleList([\n            nn.Linear(reg_real_dim, d_align, bias=False)\n            for _ in range(n_phases)\n        ])\n        self.proj_delta = nn.ModuleList([\n            nn.Linear(d_model, d_align, bias=False)\n            for _ in range(n_phases)\n        ])\n\n        # Learnable temperature and bias (per phase)\n        self.temperature = nn.ParameterList([\n            nn.Parameter(torch.ones(1)) for _ in range(n_phases)\n        ])\n        self.learned_bias = nn.ParameterList([\n            nn.Parameter(torch.zeros(1)) for _ in range(n_phases)\n        ])\n\n        # Complex register write (per phase × per register)\n        self.write_proj_real = nn.ModuleList([\n            nn.Linear(d_model, d_register, bias=False)\n            for _ in range(n_phases * n_registers)\n        ])\n        self.write_proj_imag = nn.ModuleList([\n            nn.Linear(d_model, d_register, bias=False)\n            for _ in range(n_phases * n_registers)\n        ])\n        self.write_gates = nn.ModuleList([\n            nn.Linear(d_model, 1)\n            for _ in range(n_phases * n_registers)\n        ])\n\n    def gate_phase(\n        self,\n        registers: list[torch.Tensor],\n        delta: torch.Tensor,\n        phase_idx: int,\n    ) -> tuple[torch.Tensor, list[torch.Tensor], torch.Tensor, list[float]]:\n        \"\"\"Gate a phase's output using alignment-based scalar gate.\n\n        Args:\n            registers: list of n_registers complex tensors, each (d_register,)\n            delta: (B, L, d_model) real tensor\n            phase_idx: which phase (0=prep, 1=converge, 2=consolidate)\n\n        Returns:\n            gated_delta: (B, L, d_model)\n            updated_registers: list of n_registers complex tensors\n            gate_value: scalar gate (detached)\n            write_gate_values: list of floats\n        \"\"\"\n        eps = 1e-8\n\n        # Flatten complex registers to real\n        reg_flat = _interleave_complex(registers)  # (2 * n_reg * d_reg,)\n        reg_dir = reg_flat / (reg_flat.norm() + eps)\n\n        # Delta summary and direction\n        summary = delta.mean(dim=(0, 1))  # (d_model,)\n        delta_dir = summary / (summary.norm() + eps)\n\n        # Alignment score → scalar gate\n        reg_proj = self.proj_align[phase_idx](reg_dir)      # (d_align,)\n        delta_proj = self.proj_delta[phase_idx](delta_dir)   # (d_align,)\n        alignment = (reg_proj * delta_proj).sum()            # scalar\n\n        gate = torch.sigmoid(\n            alignment * self.temperature[phase_idx]\n            + self.learned_bias[phase_idx]\n        )\n        gated_delta = gate * delta  # scalar broadcasts to (B, L, d_model)\n\n        # Complex register updates\n        updated_registers = []\n        write_gate_values = []\n        for reg_idx in range(self.n_registers):\n            write_idx = phase_idx * self.n_registers + reg_idx\n            wg = torch.sigmoid(self.write_gates[write_idx](summary))\n            update_r = self.write_proj_real[write_idx](summary)  # (d_register,)\n            update_i = self.write_proj_imag[write_idx](summary)  # (d_register,)\n            update = torch.complex(update_r, update_i)           # (d_register,) complex\n            updated_registers.append(registers[reg_idx] + wg * update)\n            write_gate_values.append(wg.item())\n\n        return gated_delta, updated_registers, gate.detach(), write_gate_values\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Meta-S3 — Cross-level contribution gate (complex register banks)\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass MetaS3Complex(nn.Module):\n    \"\"\"Top-level resource allocation reading complex register banks.\"\"\"\n\n    def __init__(self, d_register: int, n_registers: int, n_banks: int, n_passes: int):\n        super().__init__()\n        input_dim = n_banks * n_registers * d_register * 2  # interleaved real\n        self.gate_proj = nn.Linear(input_dim, n_passes)\n\n    def forward(self, all_banks: list[list[torch.Tensor]]) -> torch.Tensor:\n        flat = _interleave_banks(all_banks)\n        return torch.sigmoid(self.gate_proj(flat))\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Meta-S4 — Final structural summary (complex-query)\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass MetaS4Complex(nn.Module):\n    \"\"\"Final intelligence scan with complex-query attention.\n\n    Same phase-sensitive mechanism as S4: Re(q·conj(k)).\n    Reads most-refined register banks, produces real residual update.\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int,\n        d_register: int,\n        n_registers: int = 3,\n        n_banks: int = 4,\n        dropout: float = 0.1,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.d_register = d_register\n        self.n_registers = n_registers\n        self.n_banks = n_banks\n        self.scale = d_model ** -0.5\n\n        total_reg_dim = n_banks * n_registers * d_register * 2  # interleaved\n        self.q_proj = nn.Linear(total_reg_dim, d_model, bias=False)\n        self.k_proj = nn.Linear(d_model, d_model, bias=False)\n        self.v_proj = nn.Linear(d_model, d_model, bias=False)\n        self.out_proj = nn.Linear(d_model, d_model, bias=False)\n        self.norm = nn.LayerNorm(d_model)\n        self.dropout = nn.Dropout(dropout)\n\n    def forward(\n        self,\n        meta_banks: list[list[torch.Tensor]],\n        residual: torch.Tensor,\n    ) -> torch.Tensor:\n        B, L, D = residual.shape\n\n        q_input = _interleave_banks(meta_banks)\n\n        # Complex query decomposed into real ops\n        q_flat = self.q_proj(q_input)        # (d_model,)\n        q_r = q_flat[0::2]                   # (d_model//2,)\n        q_i = q_flat[1::2]                   # (d_model//2,)\n\n        x = self.norm(residual)\n        k_flat = self.k_proj(x)              # (B, L, d_model)\n        k_r = k_flat[..., 0::2]\n        k_i = k_flat[..., 1::2]\n        v = self.v_proj(x)                   # (B, L, d_model) real\n\n        # Phase-sensitive attention\n        attn = (\n            torch.einsum(\"d,bld->bl\", q_r, k_r)\n            + torch.einsum(\"d,bld->bl\", q_i, k_i)\n        ) * self.scale\n\n        attn_weights = F.softmax(attn, dim=-1)\n        attn_weights = self.dropout(attn_weights)\n\n        summary = torch.einsum(\"bl,bld->bd\", attn_weights, v)\n        out = self.out_proj(summary).unsqueeze(1).expand_as(residual)\n        return residual + out\n\n\n# ══════════════════════════════════════════════════════════════════════\n# VSM-LM v5 — Spiral + Complex Registers + Phase-Coherent Gating\n# ══════════════════════════════════════════════════════════════════════\n\n\nclass VSMLMV5(nn.Module):\n    \"\"\"Viable System Model Language Model — v5 topology.\n\n    v4.1 architecture with three topology changes:\n    1. Spiral attention bias (α=1.18) on all strided attention.\n    2. Complex-valued registers (ℂ^128 = ℝ^256 equivalent).\n    3. Phase-coherent S3 gating (scalar alignment gate).\n    \"\"\"\n\n    REGISTER_NAMES = (\"type\", \"scope\", \"role\")\n    PHASE_NAMES = (\"prep\", \"converge\", \"consolidate\")\n    N_LEVELS = 3\n    N_PASSES = 5\n    PASS_NAMES = (\"L0_asc\", \"L1_asc\", \"L2_apex\", \"L1_desc\", \"L0_desc\")\n\n    def __init__(\n        self,\n        vocab_size: int = 50277,\n        d_model: int = 512,\n        d_register: int = 128,       # Complex dim (ℂ^128 = ℝ^256 equivalent)\n        max_len: int = 4096,\n        n_heads: int = 8,\n        d_ff: int = 1536,\n        d_ff_consolidate: int = 2048,\n        window: int = 8,\n        strides: tuple[int, ...] = (1, 8, 64, 512),\n        n_prep_layers: int = 1,\n        n_converge_layers: int = 2,\n        n_consolidate_layers: int = 3,\n        dropout: float = 0.1,\n        alpha: float = 1.18,          # Spiral attention bias exponent\n    ):\n        super().__init__()\n        self.vocab_size = vocab_size\n        self.d_model = d_model\n        self.d_register = d_register\n        self.max_len = max_len\n        self.n_heads = n_heads\n        self.window = window\n        self.strides = strides\n        self.alpha = alpha\n        self.n_registers = len(self.REGISTER_NAMES)\n        self.n_phases = len(self.PHASE_NAMES)\n        self.n_levels = self.N_LEVELS\n        self.n_passes = self.N_PASSES\n\n        # Bank layout (same as v4.1):\n        #   0=bank_0, 1=bank_1↑, 2=bank_2↑, 3=bank_3, 4=bank_2↓, 5=bank_1↓\n        self.n_banks = 6\n\n        self.n_prep_layers = n_prep_layers\n        self.n_converge_layers = n_converge_layers\n        self.n_consolidate_layers = n_consolidate_layers\n\n        # ── Progressive stride allocation per level ───────────────\n        s1, s8, s64, s512 = strides[0], strides[1], strides[2], strides[3]\n        self.level_configs = [\n            [(s1, window)] * 3 + [(s8, window)] * 3 + [(s64, window)] * 1 + [(s512, window)] * 1,\n            [(s1, window)] * 2 + [(s8, window)] * 2 + [(s64, window)] * 2 + [(s512, window)] * 2,\n            [(s1, window)] * 1 + [(s8, window)] * 1 + [(s64, window)] * 3 + [(s512, window)] * 3,\n        ]\n\n        # ── S5: Identity (shared weights + embeddings) ────────────\n        self.token_embed = nn.Embedding(vocab_size, d_model)\n        self.pos_embed = nn.Embedding(max_len, d_model)\n        self.output_norm = nn.LayerNorm(d_model)\n\n        # Register bank 0: learnable init (real part; imag starts at 0)\n        self.register_inits = nn.ParameterDict({\n            f\"reg_{name}\": nn.Parameter(torch.zeros(d_register))\n            for name in self.REGISTER_NAMES\n        })\n\n        # Shared S1 operations (S5 coherence)\n        self.prep_layers = nn.ModuleList([\n            FFNLayer(d_model, d_ff, dropout)\n            for _ in range(n_prep_layers)\n        ])\n\n        # Converge: per-level stride configs, shared weights, spiral bias\n        self.converge_layers_base = nn.ModuleList([\n            CompressorLayer(d_model, self.level_configs[0], d_ff, dropout, alpha=alpha)\n            for _ in range(n_converge_layers)\n        ])\n        self.converge_layers_l2 = nn.ModuleList([\n            CompressorLayer(d_model, self.level_configs[1], d_ff, dropout, alpha=alpha)\n            for _ in range(n_converge_layers)\n        ])\n        self.converge_layers_l3 = nn.ModuleList([\n            CompressorLayer(d_model, self.level_configs[2], d_ff, dropout, alpha=alpha)\n            for _ in range(n_converge_layers)\n        ])\n        for i in range(n_converge_layers):\n            self._tie_compressor_weights(self.converge_layers_base[i], self.converge_layers_l2[i])\n            self._tie_compressor_weights(self.converge_layers_base[i], self.converge_layers_l3[i])\n\n        # Consolidate: shared across levels, spiral bias\n        self.consolidate_layers = nn.ModuleList([\n            CompressorLayer(d_model, self.level_configs[1], d_ff_consolidate, dropout, alpha=alpha)\n            for _ in range(n_consolidate_layers)\n        ])\n\n        # ── S4: Complex-query intelligence ────────────────────────\n        self.s4 = S4IntelligenceComplex(\n            d_model, d_register, self.n_registers,\n            max_banks=self.n_banks,\n            dropout=dropout,\n        )\n\n        # ── S3: Phase-coherent gating (5 instances) ──────────────\n        self.s3_passes = nn.ModuleList([\n            S3PhaseCoherent(\n                d_model, d_register, self.n_phases, self.n_registers,\n                d_align=d_model,\n            )\n            for _ in range(self.n_passes)\n        ])\n\n        # ── Meta-S4: Complex-query final summary (4 best banks) ──\n        self.meta_s4 = MetaS4Complex(\n            d_model, d_register, self.n_registers,\n            n_banks=4,\n            dropout=dropout,\n        )\n\n        # ── Meta-S3: Per-pass contribution gates ─────────────────\n        self.meta_s3 = MetaS3Complex(\n            d_register, self.n_registers,\n            n_banks=self.n_banks,\n            n_passes=self.n_passes,\n        )\n\n        # ── Initialize ────────────────────────────────────────────\n        self.apply(self._init_weights)\n\n    @staticmethod\n    def _tie_compressor_weights(source: CompressorLayer, target: CompressorLayer):\n        \"\"\"Tie all learnable weights of target to source (S5 coherence).\"\"\"\n        target.attn.q_proj.weight = source.attn.q_proj.weight\n        target.attn.k_proj.weight = source.attn.k_proj.weight\n        target.attn.v_proj.weight = source.attn.v_proj.weight\n        target.attn.out_proj.weight = source.attn.out_proj.weight\n        if target.attn.q_proj.bias is not None:\n            target.attn.q_proj.bias = source.attn.q_proj.bias\n        if target.attn.k_proj.bias is not None:\n            target.attn.k_proj.bias = source.attn.k_proj.bias\n        if target.attn.v_proj.bias is not None:\n            target.attn.v_proj.bias = source.attn.v_proj.bias\n        if target.attn.out_proj.bias is not None:\n            target.attn.out_proj.bias = source.attn.out_proj.bias\n\n        target.norm1.weight = source.norm1.weight\n        target.norm1.bias = source.norm1.bias\n        target.norm2.weight = source.norm2.weight\n        target.norm2.bias = source.norm2.bias\n\n        for i in range(len(source.ff)):\n            src_mod = source.ff[i]\n            tgt_mod = target.ff[i]\n            if hasattr(src_mod, 'weight'):\n                tgt_mod.weight = src_mod.weight\n            if hasattr(src_mod, 'bias') and src_mod.bias is not None:\n                tgt_mod.bias = src_mod.bias\n\n    def _init_weights(self, module: nn.Module) -> None:\n        if isinstance(module, nn.Linear):\n            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)\n            if module.bias is not None:\n                torch.nn.init.zeros_(module.bias)\n        elif isinstance(module, nn.Embedding):\n            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)\n        elif isinstance(module, nn.LayerNorm):\n            torch.nn.init.ones_(module.weight)\n            torch.nn.init.zeros_(module.bias)\n\n    def _init_bank0(self) -> list[torch.Tensor]:\n        \"\"\"Initialize register bank 0: complex(learned_real, zeros).\"\"\"\n        return [\n            torch.complex(\n                self.register_inits[f\"reg_{name}\"].clone(),\n                torch.zeros_like(self.register_inits[f\"reg_{name}\"]),\n            )\n            for name in self.REGISTER_NAMES\n        ]\n\n    def _fresh_bank(self) -> list[torch.Tensor]:\n        \"\"\"Create a zero-initialized complex register bank.\"\"\"\n        device = self.register_inits[\"reg_type\"].device\n        return [\n            torch.zeros(self.d_register, device=device, dtype=torch.cfloat)\n            for _ in self.REGISTER_NAMES\n        ]\n\n    def _get_converge_layers(self, level: int) -> nn.ModuleList:\n        if level == 0:\n            return self.converge_layers_base\n        elif level == 1:\n            return self.converge_layers_l2\n        elif level == 2:\n            return self.converge_layers_l3\n        else:\n            raise ValueError(f\"Invalid level: {level}\")\n\n    def _run_prep(self, x: torch.Tensor) -> torch.Tensor:\n        for layer in self.prep_layers:\n            x = layer(x)\n        return x\n\n    def _run_converge(self, x: torch.Tensor, level: int) -> torch.Tensor:\n        for layer in self._get_converge_layers(level):\n            x = layer(x)\n        return x\n\n    def _run_consolidate(self, x: torch.Tensor) -> torch.Tensor:\n        for layer in self.consolidate_layers:\n            x = layer(x)\n        return x\n\n    def _run_level_pass(\n        self,\n        x: torch.Tensor,\n        level: int,\n        pass_idx: int,\n        readable_banks: list[list[torch.Tensor]],\n        target_bank: list[torch.Tensor],\n    ) -> tuple[torch.Tensor, list[torch.Tensor], torch.Tensor]:\n        \"\"\"Run one level-pass (ascending or descending).\"\"\"\n        x_before = x\n\n        # S4: complex-query scan\n        s4_updates, _ = self.s4(readable_banks, x)\n        target_bank = [\n            target_bank[i] + s4_updates[i]\n            for i in range(self.n_registers)\n        ]\n\n        # Phase 1: PREP\n        prep_out = self._run_prep(x)\n        delta = prep_out - x\n        gated_delta, target_bank, _, _ = self.s3_passes[pass_idx].gate_phase(\n            target_bank, delta, 0)\n        x = x + gated_delta\n\n        # Phase 2: CONVERGE\n        converge_out = self._run_converge(x, level)\n        delta = converge_out - x\n        gated_delta, target_bank, _, _ = self.s3_passes[pass_idx].gate_phase(\n            target_bank, delta, 1)\n        x = x + gated_delta\n\n        # Phase 3: CONSOLIDATE\n        consolidate_out = self._run_consolidate(x)\n        delta = consolidate_out - x\n        gated_delta, target_bank, _, _ = self.s3_passes[pass_idx].gate_phase(\n            target_bank, delta, 2)\n        x = x + gated_delta\n\n        return x, target_bank, x - x_before\n\n    def forward(\n        self,\n        input_ids: torch.Tensor,\n        targets: Optional[torch.Tensor] = None,\n    ) -> tuple[torch.Tensor, Optional[torch.Tensor]]:\n        B, L = input_ids.shape\n        device = input_ids.device\n\n        positions = torch.arange(L, device=device)\n        x = self.token_embed(input_ids) + self.pos_embed(positions)\n\n        # ── Complex register banks ────────────────────────────────\n        bank_0 = self._init_bank0()\n        bank_1_asc = self._fresh_bank()\n        bank_2_asc = self._fresh_bank()\n        bank_3 = self._fresh_bank()\n        bank_2_desc = self._fresh_bank()\n        bank_1_desc = self._fresh_bank()\n\n        pass_deltas = []\n\n        # ── ASCENDING: L0↑ → L1↑ → L2 ───────────────────────────\n        x, bank_1_asc, delta = self._run_level_pass(\n            x, level=0, pass_idx=0,\n            readable_banks=[bank_0],\n            target_bank=bank_1_asc,\n        )\n        pass_deltas.append(delta)\n\n        x, bank_2_asc, delta = self._run_level_pass(\n            x, level=1, pass_idx=1,\n            readable_banks=[bank_0, bank_1_asc],\n            target_bank=bank_2_asc,\n        )\n        pass_deltas.append(delta)\n\n        x, bank_3, delta = self._run_level_pass(\n            x, level=2, pass_idx=2,\n            readable_banks=[bank_0, bank_1_asc, bank_2_asc],\n            target_bank=bank_3,\n        )\n        pass_deltas.append(delta)\n\n        # ── DESCENDING: L1↓ → L0↓ ────────────────────────────────\n        x, bank_2_desc, delta = self._run_level_pass(\n            x, level=1, pass_idx=3,\n            readable_banks=[bank_0, bank_1_asc, bank_2_asc, bank_3],\n            target_bank=bank_2_desc,\n        )\n        pass_deltas.append(delta)\n\n        x, bank_1_desc, delta = self._run_level_pass(\n            x, level=0, pass_idx=4,\n            readable_banks=[bank_0, bank_1_asc, bank_2_desc, bank_3],\n            target_bank=bank_1_desc,\n        )\n        pass_deltas.append(delta)\n\n        # ── Meta-S3: per-pass contribution gates ──────────────────\n        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]\n        meta_gates = self.meta_s3(all_banks)\n\n        total_ungated = sum(pass_deltas)\n        total_gated = sum(\n            meta_gates[i] * pass_deltas[i]\n            for i in range(self.n_passes)\n        )\n        x = x - total_ungated + total_gated\n\n        # ── Meta-S4: final structural summary ─────────────────────\n        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]\n        x = self.meta_s4(meta_banks, x)\n\n        x = self.output_norm(x)\n        logits = F.linear(x, self.token_embed.weight)\n\n        loss = None\n        if targets is not None:\n            loss = F.cross_entropy(\n                logits.view(-1, self.vocab_size),\n                targets.view(-1),\n                ignore_index=-1,\n            )\n\n        return logits, loss\n\n    def forward_instrumented(\n        self,\n        input_ids: torch.Tensor,\n        targets: Optional[torch.Tensor] = None,\n    ) -> tuple[torch.Tensor, Optional[torch.Tensor], dict]:\n        \"\"\"Forward pass with full instrumentation for probing.\"\"\"\n        B, L = input_ids.shape\n        device = input_ids.device\n        metrics: dict = {}\n        reg_names = list(self.REGISTER_NAMES)\n\n        positions = torch.arange(L, device=device)\n        x = self.token_embed(input_ids) + self.pos_embed(positions)\n        metrics[\"embed_norm\"] = x.norm(dim=-1).mean().item()\n\n        # Complex register banks\n        bank_0 = self._init_bank0()\n        bank_1_asc = self._fresh_bank()\n        bank_2_asc = self._fresh_bank()\n        bank_3 = self._fresh_bank()\n        bank_2_desc = self._fresh_bank()\n        bank_1_desc = self._fresh_bank()\n\n        for i, name in enumerate(reg_names):\n            metrics[f\"register_{name}_init_norm\"] = torch.view_as_real(bank_0[i]).norm().item()\n\n        pass_deltas = []\n\n        pass_schedule = [\n            (0, 0, \"L0_asc\"),\n            (1, 1, \"L1_asc\"),\n            (2, 2, \"L2_apex\"),\n            (3, 1, \"L1_desc\"),\n            (4, 0, \"L0_desc\"),\n        ]\n\n        for pass_idx, level, pass_name in pass_schedule:\n            pfx = pass_name\n\n            if pass_idx == 0:\n                readable = [bank_0]\n                target_bank = bank_1_asc\n            elif pass_idx == 1:\n                readable = [bank_0, bank_1_asc]\n                target_bank = bank_2_asc\n            elif pass_idx == 2:\n                readable = [bank_0, bank_1_asc, bank_2_asc]\n                target_bank = bank_3\n            elif pass_idx == 3:\n                readable = [bank_0, bank_1_asc, bank_2_asc, bank_3]\n                target_bank = bank_2_desc\n            elif pass_idx == 4:\n                readable = [bank_0, bank_1_asc, bank_2_desc, bank_3]\n                target_bank = bank_1_desc\n\n            x_before = x\n\n            # S4\n            s4_updates, s4_attn = self.s4(readable, x)\n            target_bank = [\n                target_bank[i] + s4_updates[i]\n                for i in range(self.n_registers)\n            ]\n\n            for i, name in enumerate(reg_names):\n                metrics[f\"{pfx}_reg_{name}_after_s4\"] = torch.view_as_real(target_bank[i]).norm().item()\n                metrics[f\"{pfx}_reg_{name}_phase_mean\"] = torch.angle(target_bank[i]).mean().item()\n            s4_entropy = -(s4_attn * (s4_attn + 1e-10).log()).sum(dim=-1).mean()\n            metrics[f\"{pfx}_s4_attn_entropy\"] = s4_entropy.item()\n\n            # Three phases\n            for phase_idx, phase_name in enumerate(self.PHASE_NAMES):\n                if phase_name == \"prep\":\n                    phase_out = self._run_prep(x)\n                elif phase_name == \"converge\":\n                    phase_out = self._run_converge(x, level)\n                elif phase_name == \"consolidate\":\n                    phase_out = self._run_consolidate(x)\n\n                delta = phase_out - x\n                gated_delta, target_bank, gate_val, write_gates = (\n                    self.s3_passes[pass_idx].gate_phase(target_bank, delta, phase_idx))\n                x = x + gated_delta\n\n                metrics[f\"{pfx}_{phase_name}_delta_norm\"] = delta.norm(dim=-1).mean().item()\n                metrics[f\"{pfx}_{phase_name}_gated_norm\"] = gated_delta.norm(dim=-1).mean().item()\n                metrics[f\"{pfx}_{phase_name}_gate_mean\"] = gate_val.item()\n                metrics[f\"{pfx}_{phase_name}_gate_std\"] = 0.0  # scalar gate, compat\n                metrics[f\"{pfx}_after_{phase_name}\"] = x.norm(dim=-1).mean().item()\n                for i, rn in enumerate(reg_names):\n                    metrics[f\"{pfx}_{phase_name}_write_{rn}\"] = write_gates[i]\n\n            # Register norms after pass (complex magnitude)\n            for i, name in enumerate(reg_names):\n                metrics[f\"{pfx}_register_{name}_norm\"] = torch.view_as_real(target_bank[i]).norm().item()\n                metrics[f\"{pfx}_register_{name}_phase_final\"] = torch.angle(target_bank[i]).mean().item()\n\n            # Write back\n            if pass_idx == 0:\n                bank_1_asc = target_bank\n            elif pass_idx == 1:\n                bank_2_asc = target_bank\n            elif pass_idx == 2:\n                bank_3 = target_bank\n            elif pass_idx == 3:\n                bank_2_desc = target_bank\n            elif pass_idx == 4:\n                bank_1_desc = target_bank\n\n            pass_deltas.append(x - x_before)\n\n        # ── Level-indexed metrics for v4 compatibility ────────────\n        level_map = {\n            \"L0_asc\": \"level0\", \"L1_asc\": \"level1\", \"L2_apex\": \"level2\",\n            \"L1_desc\": \"level1_desc\", \"L0_desc\": \"level0_desc\",\n        }\n        for pass_name, level_pfx in level_map.items():\n            for key in list(metrics.keys()):\n                if key.startswith(pass_name + \"_\"):\n                    suffix = key[len(pass_name) + 1:]\n                    metrics[f\"{level_pfx}_{suffix}\"] = metrics[key]\n\n        # Backward-compat iter aliases\n        for level in range(min(self.N_LEVELS, 2)):\n            src_pfx = f\"level{level}\"\n            dst_pfx = f\"iter{level}\"\n            for phase in self.PHASE_NAMES:\n                for suffix in [\"delta_norm\", \"gated_norm\", \"gate_mean\", \"gate_std\"]:\n                    k = f\"{src_pfx}_{phase}_{suffix}\"\n                    if k in metrics:\n                        metrics[f\"{dst_pfx}_{phase}_{suffix}\"] = metrics[k]\n                for rn in reg_names:\n                    k = f\"{src_pfx}_{phase}_write_{rn}\"\n                    if k in metrics:\n                        metrics[f\"{dst_pfx}_{phase}_write_{rn}\"] = metrics[k]\n            for rn in reg_names:\n                for key_suffix in [f\"reg_{rn}_after_s4\", f\"register_{rn}_norm\"]:\n                    k = f\"{src_pfx}_{key_suffix}\"\n                    if k in metrics:\n                        metrics[f\"{dst_pfx}_{key_suffix}\"] = metrics[k]\n            k = f\"{src_pfx}_s4_attn_entropy\"\n            if k in metrics:\n                metrics[f\"{dst_pfx}_s4_attn_entropy\"] = metrics[k]\n            for phase in self.PHASE_NAMES:\n                k = f\"{src_pfx}_after_{phase}\"\n                if k in metrics:\n                    metrics[f\"{dst_pfx}_after_{phase}\"] = metrics[k]\n\n        # Meta-S3\n        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]\n        meta_gates = self.meta_s3(all_banks)\n        for i, pname in enumerate(self.PASS_NAMES):\n            metrics[f\"meta_s3_gate_{pname}\"] = meta_gates[i].item()\n        metrics[\"meta_s3_gate_level0\"] = meta_gates[0].item()\n        metrics[\"meta_s3_gate_level1\"] = meta_gates[1].item()\n        metrics[\"meta_s3_gate_level2\"] = meta_gates[2].item()\n\n        total_ungated = sum(pass_deltas)\n        total_gated = sum(\n            meta_gates[i] * pass_deltas[i]\n            for i in range(self.n_passes)\n        )\n        x = x - total_ungated + total_gated\n\n        # Meta-S4\n        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]\n        x = self.meta_s4(meta_banks, x)\n\n        # Global compat aliases\n        metrics[\"s4_attn_entropy\"] = metrics[\"L0_asc_s4_attn_entropy\"]\n        metrics[\"register_after_s4\"] = sum(\n            metrics[f\"L0_asc_reg_{n}_after_s4\"] for n in reg_names\n        )\n\n        metrics[\"output_norm\"] = x.norm(dim=-1).mean().item()\n        metrics[\"overall_expansion\"] = metrics[\"output_norm\"] / max(metrics[\"embed_norm\"], 1e-8)\n\n        x = self.output_norm(x)\n        logits = F.linear(x, self.token_embed.weight)\n\n        loss = None\n        if targets is not None:\n            loss = F.cross_entropy(\n                logits.view(-1, self.vocab_size),\n                targets.view(-1),\n                ignore_index=-1,\n            )\n\n        return logits, loss, metrics\n\n    def count_parameters(self) -> dict[str, int]:\n        \"\"\"Count parameters by VSM subsystem.\"\"\"\n        seen_ids = set()\n\n        def _count_unique(module):\n            total = 0\n            for p in module.parameters():\n                if id(p) not in seen_ids:\n                    seen_ids.add(id(p))\n                    total += p.numel()\n            return total\n\n        seen_ids.clear()\n\n        s5_embed = _count_unique(self.token_embed)\n        s5_pos = _count_unique(self.pos_embed)\n        s5_other = (\n            sum(p.numel() for p in self.register_inits.parameters())\n            + _count_unique(self.output_norm)\n        )\n        s4 = _count_unique(self.s4)\n        s3 = sum(_count_unique(s3p) for s3p in self.s3_passes)\n        meta_s4 = _count_unique(self.meta_s4)\n        meta_s3 = _count_unique(self.meta_s3)\n\n        s1_prep = _count_unique(self.prep_layers)\n        s1_converge = _count_unique(self.converge_layers_base)\n        _count_unique(self.converge_layers_l2)\n        _count_unique(self.converge_layers_l3)\n        s1_consolidate = _count_unique(self.consolidate_layers)\n        s1 = s1_prep + s1_converge + s1_consolidate\n\n        seen_ids.clear()\n        total = 0\n        for p in self.parameters():\n            if id(p) not in seen_ids:\n                seen_ids.add(id(p))\n                total += p.numel()\n\n        return {\n            \"S5_token_embeddings\": s5_embed,\n            \"S5_positional\": s5_pos,\n            \"S5_other\": s5_other,\n            \"S4_intelligence\": s4,\n            \"S3_passes\": s3,\n            \"Meta_S4\": meta_s4,\n            \"Meta_S3\": meta_s3,\n            \"S1_prep\": s1_prep,\n            \"S1_converge\": s1_converge,\n            \"S1_consolidate\": s1_consolidate,\n            \"S1_total\": s1,\n            \"total\": total,\n        }\n\n    def describe(self) -> str:\n        def _stride_desc(config):\n            from collections import Counter\n            counts = Counter(s for s, _ in config)\n            return \"+\".join(f\"s{s}×{n}\" for s, n in sorted(counts.items()))\n\n        ffn_per_level = self.n_prep_layers + self.n_converge_layers + self.n_consolidate_layers\n        ffn_total = ffn_per_level * self.n_passes\n\n        lines = [\n            f\"VSM-LM v5 — Spiral + Complex Registers + Phase-Coherent Gating\",\n            f\"  d_model={self.d_model}, d_register=ℂ^{self.d_register} (={self.d_register*2}ℝ), \"\n            f\"seq_len={self.max_len}\",\n            f\"  Passes: {self.n_passes} (L0↑, L1↑, L2, L1↓, L0↓)\",\n            f\"  Phase structure: prep({self.n_prep_layers}L, FFN) → \"\n            f\"converge({self.n_converge_layers}L, attn) → \"\n            f\"consolidate({self.n_consolidate_layers}L, wide-FFN)\",\n            f\"  Strides: {self.strides} (spiral bias α={self.alpha})\",\n            f\"  Spiral: bias(w) = -{self.alpha}·ln(stride·w + 1)\",\n            f\"  Registers: ℂ^{self.d_register} (phase-sensitive S4 attention)\",\n            f\"  S3: phase-coherent alignment gating (scalar gate, temperature+bias)\",\n        ]\n        for i, config in enumerate(self.level_configs):\n            lines.append(f\"    Level {i}: {_stride_desc(config)}\")\n        lines.extend([\n            f\"  S5: Shared weights across all passes (identity coherence)\",\n            f\"  S4: Complex-query register scan: Re(q·conj(k))\",\n            f\"  Register banks: {self.n_banks} (1 init + 3 ascending + 2 descending)\",\n            f\"  Meta-S4: Complex-query structural summary (4 most-refined banks)\",\n            f\"  Meta-S3: Per-pass contribution gates ({self.n_passes} gates)\",\n            f\"  FFN passes/forward: {ffn_total} ({ffn_per_level}/pass × {self.n_passes})\",\n        ])\n        return \"\\n\".join(lines)\n\n    @torch.no_grad()\n    def generate(\n        self,\n        input_ids: torch.Tensor,\n        max_new_tokens: int = 50,\n        temperature: float = 1.0,\n    ) -> torch.Tensor:\n        self.eval()\n        for _ in range(max_new_tokens):\n            x = input_ids[:, -self.max_len:]\n            logits, _ = self(x)\n            logits = logits[:, -1, :] / temperature\n            next_token = logits.argmax(dim=-1, keepdim=True)\n            input_ids = torch.cat([input_ids, next_token], dim=1)\n        return input_ids\n"
mementum/knowledge/chats/session-025.md:5640:  "content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-04-22 | Session: 025\n\n## Where we are\n\n**v5 implemented, ready to train.** Three topology changes over v4.1:\n\n### 1. Spiral attention bias\n```\nbias(w) = -1.18 · ln(stride · w + 1)\nweight ∝ 1/(distance+1)^1.18\n```\nPower-law distance decay. Smooth across stride boundaries.\nZero new parameters. In `StridedCausalAttention` (compressor_lm.py).\n\n### 2. Complex-valued registers\nℂ^128 replaces ℝ^256 (same total dimensionality). Phase angle\nas new degree of freedom. S4/Meta-S4 use phase-sensitive attention:\n`Re(q·conj(k)) = q_r·k_r + q_i·k_i`. Residual stream stays real.\nAll complex ops decomposed to real for MPS compat.\n\n### 3. Phase-coherent S3 gating\nScalar alignment gate replaces per-dimension gate:\n```\nalignment = proj_align(reg_dir) · proj_delta(delta_dir)\ngate = σ(alignment · temperature + learned_bias)\n```\nGeometric: gate opens when register direction matches delta.\nTemperature (init=1.0) and bias (init=0.0) are learnable.\nAt init: gate ≈ 0.5 (neutral pass-through).\n\n### Param count: 65,541,584 (−0.01% vs v4.1)\n\n### v4.1 status (ongoing baseline)\n\n- v4.1 step 15k: **4.728** | v4 best (step 16k): **4.713**\n- Three-phase register development confirmed\n- Full trajectory in `knowledge/explore/v4.1-training-trajectory.md`\n\n## What's next\n\n1. **Train v5** — `uv run python scripts/run_vsm_v5_1B.py`\n   Same hyperparams/seed as v4.1. Watch:\n   - Does spiral bias speed up early convergence?\n   - Do complex register phases develop meaningful structure?\n   - Does phase-coherent gating show sharper phase transitions?\n\n2. **Continue v4.1 probing** — step 16k when available.\n\n3. **v5 register analysis** — new metrics: `phase_mean`, `phase_final`\n   per register per pass. Phase angle evolution during training\n   is the novel observable.\n\n## Key files\n\n| Purpose | Path |\n|---------|------|\n| v5 model | `src/verbum/vsm_lm_v5.py` |\n| v5 training | `scripts/run_vsm_v5_1B.py` |\n| Compressor (shared) | `src/verbum/compressor_lm.py` |\n| v4.1 model | `src/verbum/vsm_lm_v4_1.py` |\n| v4.1 training | `scripts/run_vsm_v4_1_1B.py` |\n| v4 model | `src/verbum/vsm_lm_v4.py` |\n| Probe script | `scripts/compile_gradient_probe.py` |\n| Register analysis | `scripts/register_analysis.py` |\n| Training trajectory | `mementum/knowledge/explore/v4.1-training-trajectory.md` |\n| Research program | `mementum/knowledge/explore/VERBUM.md` |\n\n## Architecture lineage\n\n| Version | Params | Key Change | Best Eval |\n|---------|--------|------------|-----------|\n| v1 | ~25M | Baseline sequential | 5.245 |\n| v2 | ~25M | Iteration specialization | 5.064 |\n| v3 | 50M | Role register, binding | 4.872 |\n| v3.2 | 51M | Convergence arch | 4.897 |\n| v4 | 58M | Recursive VSM (ascending) | 4.713 |\n| v4.1 | 65.5M | Bidirectional VSM | 4.728* |\n| v5 | 65.5M | Spiral + ℂ registers + phase gating | TBD |\n\n*Training ongoing\n\n## Probing pipeline\n\n```bash\n# Train v5\nuv run python scripts/run_vsm_v5_1B.py\n\n# Probe a checkpoint\nuv run python scripts/compile_gradient_probe.py probe checkpoints/vsm-lm-v5/step_015000.pt\n\n# Register capture + analysis\nuv run python scripts/register_analysis.py capture checkpoints/vsm-lm-v5/step_015000.pt --analyze\n```\n"
mementum/knowledge/chats/session-025.md:5819:  "original_content": "v5 introduces three topology changes over v4.1:\n\n  1. Spiral attention bias: bias(w) = -α·ln(stride·w + 1)\n     Power-law distance decay. weight ∝ 1/(distance+1)^α.\n     Smooth attention landscape across stride boundaries.\n     α=1.18 (R²=0.997 empirical fit). Zero new parameters.\n\n  2. Complex-valued registers: ℂ^128 replaces ℝ^256.\n     Phase angle encodes a new degree of freedom beyond magnitude.\n     S4 uses phase-sensitive attention: Re(q·conj(k)) = q_r·k_r + q_i·k_i.\n     Residual stream stays real. Only registers carry phase.\n\n  3. Phase-coherent S3 gating: scalar alignment gate.\n     gate = σ(alignment · temperature + bias)\n     alignment = proj_reg(reg_dir) · proj_delta(delta_dir)\n     Geometric: gate opens when register direction matches delta direction.\n     Learnable temperature (init=1.0) and bias (init=0.0).",
mementum/knowledge/chats/session-025.md:5820:  "new_content": "v5 introduces four topology changes over v4.1:\n\n  1. Spiral attention bias: bias(w) = -α·ln(stride·w + 1)\n     Power-law distance decay. weight ∝ 1/(distance+1)^α.\n     Smooth attention landscape across stride boundaries.\n     α=1.18 (R²=0.997 empirical fit). Zero new parameters.\n\n  2. Complex-valued registers: ℂ^128 replaces ℝ^256.\n     Phase angle encodes a new degree of freedom beyond magnitude.\n     S4 uses phase-sensitive attention: Re(q·conj(k)) = q_r·k_r + q_i·k_i.\n     Residual stream stays real. Only registers carry phase.\n\n  3. Phase-coherent S3 gating: scalar alignment gate.\n     gate = σ(alignment · temperature + bias)\n     alignment = proj_reg(reg_dir) · proj_delta(delta_dir)\n     Geometric: gate opens when register direction matches delta direction.\n     Learnable temperature (init=1.0) and bias (init=0.0).\n\n  4. Multiplicative modulation: replaces additive composition.\n     modulation = 1 + gate · tanh(proj(delta))\n     x_new = x · modulation\n     Zero-init proj → identity at start. S5 coherent (3 shared projs).\n     The chain x · m₁ · m₂ · ... · mₙ produces power-law magnitude."
mementum/knowledge/chats/session-025.md:6040:  "content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-04-22 | Session: 025\n\n## Where we are\n\n**v5 implemented, ready to train.** Four topology changes over v4.1:\n\n### 1. Spiral attention bias\n```\nbias(w) = -1.18 · ln(stride · w + 1)\nweight ∝ 1/(distance+1)^1.18\n```\nPower-law distance decay. Smooth across stride boundaries.\nZero new parameters. In `StridedCausalAttention` (compressor_lm.py).\n\n### 2. Complex-valued registers\nℂ^128 replaces ℝ^256 (same total dimensionality). Phase angle\nas new degree of freedom. S4/Meta-S4 use phase-sensitive attention:\n`Re(q·conj(k)) = q_r·k_r + q_i·k_i`. Residual stream stays real.\nAll complex ops decomposed to real for MPS compat.\n\n### 3. Phase-coherent S3 gating\nScalar alignment gate replaces per-dimension gate:\n```\nalignment = proj_align(reg_dir) · proj_delta(delta_dir)\ngate = σ(alignment · temperature + learned_bias)\n```\nGeometric: gate opens when register direction matches delta.\nTemperature (init=1.0) and bias (init=0.0) are learnable.\nAt init: gate ≈ 0.5 (neutral pass-through).\n\n### 4. Multiplicative modulation\nReplaces additive composition (`x = x + gate·delta`):\n```\nmodulation = 1 + gate · tanh(proj(delta))\nx_new = x · modulation\n```\nZero-init proj 

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01PeZ2aytjdz6n58zF9Gk8S4.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 I should look for the knowledge page on the adjunction instead of digging through these massive chat logs — there's a file called `direct-delta-adjunction.md` that should have the s140 measurement details I need.

## Assistant

The chats are too noisy. The knowledge page `direct-delta-adjunction.md` should have the s140 measurement spec:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/mementum/knowledge/ | grep -i -E \"adjunc|delta|zone\"; echo ---; git -C /Users/mwhitford/src/verbum grep -n -i \"zone\" -- mementum/knowledge/direct-delta-adjunction.md | head -20"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/meme...

**Output:**
```
Exit code: 0
Stdout:
direct-delta-adjunction.md
---
mementum/knowledge/direct-delta-adjunction.md:102:The cross-zone mapping (encode L2 → decode L56) has:
mementum/knowledge/direct-delta-adjunction.md:105:R² = 1.000     (for ALL zone pairs)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/direct-delta-adjunction.md"
}
```

**Summary:** Reading direct-delta-adjunction.md (0-2000)

**Output:**
```
---
title: "Direct Delta Correction — Compute the Answer via Adjunction Structure"
status: active
category: compression
tags: [direct-delta, adjunction, rank-1, svd, error-correction, parametric-surface, calibration-aware]
related:
  - sign-correction-topology.md
  - score-matching-compression.md
  - residual-covariance-rank.md
  - explore/categorical-geometry-probes.md
  - mathematical-convergences.md
  - standing-wave-magnitudes.md
depends-on:
  - score-matching-compression.md
  - explore/categorical-geometry-probes.md
created: session 200
---

# Direct Delta Correction

> Session 200. After four sign correction algorithms failed catastrophically,
> two insights converged: (1) the teacher delta is directly computable — no
> training needed, (2) the adjunction finding from session 140 says the
> encode→decode transformation is rank-1. Together: the optimal correction
> is an analytical SVD, and it might need only rank 1-2.

## The Core Insight

> "If everything is being calculated, why can we not also calculate the
> delta from the teacher?"

We have the teacher model. We have the sieved student. At every layer,
for every projection, the weight residual is known:

```
W_delta = W_teacher - W_sieve
```

For sieved layers: W_delta is W at masked-out positions, zero at kept
positions (50% sparse). For L0 SVD: W_delta is the rank-750 approximation
error.

The optimal rank-k additive correction `A @ B ≈ W_delta` is the truncated
SVD. No training loop. No loss function. No optimizer. No hyperparameters
beyond rank.

## Calibration-Aware SVD

Naive SVD minimizes `||A@B - W_delta||²_F` (Frobenius). But not all input
directions are equally likely. The calibration-aware version weights by the
actual input distribution:

```
Minimize: E_x[||A@B@x - W_delta@x||²]
        = ||(A@B - W_delta) @ H^½||²_F

where H = E[x@x.T] = input covariance (from calibration data)

Solution:
  1. Whiten: W_whitened = W_delta @ H^½
  2. SVD(W_whitened) → truncate to rank k
  3. Unwhiten B: B = B_whitened @ H^{-½}
```

This gives the rank-k correction that is optimal for the actual input
distribution, not uniform over all directions.

## Sequential Cascade Awareness

Layer-by-layer, correct upstream before computing downstream:

```
For l = 0, 1, ..., 34:
  1. Run calibration data through model → collect actual inputs at layer l
     (these reflect upstream corrections already applied)
  2. Compute H_l = input covariance at this layer
  3. Compute W_delta_l for each projection (gate/up/down)
  4. Calibration-aware SVD → rank-k correction A_l, B_l
  5. Install correction at layer l
  6. Next layer sees corrected cascade
```

This is the GPTQ approach: each layer's correction is optimal for its
actual inputs, accounting for how upstream corrections changed the cascade.

## Why This Should Work Better Than Training

| Property | SM Loss (v3b) | Direct Delta |
|----------|--------------|-------------|
| Gradient dilution | Yes (29 Jacobians) | None (no backprop) |
| Compensating errors | Possible (CE creates them) | Impossible (per-layer independent) |
| Hyperparameter sensitivity | α, lr, steps, batch_size | rank only |
| Training instability | Diverges after step 150+ | No training |
| Cascade awareness | Implicit (through SM loss) | Explicit (sequential) |
| Optimality guarantee | Local minimum of loss | Global optimum at given rank |
| Speed | ~600s for 200 steps | ~minutes (SVD per layer) |

## The Adjunction Connection

### Session 140 Finding (Qwen3-32B)

The cross-zone mapping (encode L2 → decode L56) has:
```
σ₁/σ₂ = 128:1  (rank-1 dominated)
R² = 1.000     (for ALL zone pairs)
```

The Jacobian of the encode→decode transformation has **constant rank 1**
everywhere on the manifold. This is the defining property of a **regular
parametric surface** — specifically, a 1D curve embedded in 4096D space.

### Session 185 Finding (Qwen3-8B)

During ORTHO (L7-22), the residual stream has **effective rank = 1**:
```
Top eigenvalue: ~710,000
Second eigenvalue: ~100-170
Ratio: 4000-8800×
V overlap with residual: 0% (computation in null space)
```

16 consecutive layers of computation happen in the 4095-dimensional null
space of a rank-1 carrier wave. The residual is 1D; the computation is
invisible.

### The Implication for Error Correction

If the transformation is rank-1:
1. The entire computation lives on a **1D curve** through activation space
2. The sieve pushes representations off this curve
3. Error correction = **project back onto the curve**
4. The projection is along the dominant singular vector = **rank-1 correction**

**Prediction:** Direct delta correction at rank 1-2 should be nearly
optimal. The rank sweep [2, 4, 8, 16, 32] will test this. If rank-2
matches rank-32, the adjunction structure IS the error correcting code.

## The Tiles and Grout Metaphor

Topology (signs, mask, crystal) = tiles in a mosaic.
Gradients (LoRA, magnitudes) = grout filling the gaps between tiles.

```
When you move a tile (flip a sign):
  → all surrounding grout is wrong (trained for different gaps)
  → new gaps the grout doesn't fit
  → cascade: every downstream tile's grout is also wrong

Why sign correction + LoRA fails:
  Phase 1 (sign flips) → creates new gaps
  Phase 2 (LoRA) → trains grout from scratch
  But gaps too numerous, grout capacity (rank-4) too thin
```

MoE explicitly separates tiles from grout: router = topology, experts =
computation. Dense models entangle them. The crystal sieve tries to
separate what was never separate.

Direct delta correction avoids this entirely: instead of changing tiles
and refitting grout, compute the exact grout needed for the existing
tiles. No tile movement. No refit. Analytical solution.

## Connection to MoE Literature

Three principles from MoE training dynamics (session 200 research):

1. **Decouple routing from expert training.** (SEAS-GMoE, Grouter)
   → Direct delta: routing (signs) is frozen, correction (SVD) is computed
   independently. Perfect decoupling.

2. **Use teacher to supervise routing.** (TGR-MoE)
   → Direct delta: teacher's weights ARE the target. The SVD computes
   exactly the deviation from teacher.

3. **Stabilize routing FIRST, then train experts.** (Grouter)
   → Direct delta: routing is never changed. Experts (corrections) are
   computed analytically. No stability concern.

## Connection to TSP (arXiv:2606.03489)

TSP identifies "risk nodes" (critical decision points) and trains the model
to prefer the "golden path" over self-generated alternatives. Maps to:

- Risk nodes = layers where sieve diverges from teacher
- Golden path = teacher's residual trajectory
- Self-play path = student's trajectory

If direct delta works, TSP-style contrastive loss could refine it further
at the specific layers where the analytic correction is weakest. The
direct delta provides the initial correction; TSP provides the polish.

## Why All Sign Correction Failed (Summary)

Four approaches, same failure mode. The tiles-and-grout analysis explains
all of them:

| Approach | What it did | Why it failed |
|----------|------------|---------------|
| TD (gradient) | Tried to move tiles via backprop | Gradient too diluted to reach tiles through 29 layers of grout |
| TD v4c (per-tensor clip) | Successfully moved tiles | Grout around moved tiles now wrong; cascade destroys pattern |
| Latent diffusion | Moved tiles in eigenspace | Eigenspace ≠ crystal space; correlated tile moves catastrophic |
| Crystal ECC | Moved tiles with health gate | Health gate measures wrong space; 49.3% adversarial signal |
| Teacher-guided routing | Added correction to routing | 182M params, diverges; can't fix routing + cascade simultaneously |

All five tried to change the tiles. Direct delta doesn't change tiles —
it computes the exact grout for the existing tile arrangement.

## Experimental Artifacts

| Experiment | Script | Status |
|-----------|--------|--------|
| Direct delta (rank sweep) | `scripts/experiments/direct_delta_correction.py` | Running (tmux main:1) |
| Teacher-guided routing | `scripts/experiments/teacher_guided_routing.py` | ❌ Failed (24.55 PPL) |
| Crystal ECC | `scripts/experiments/crystal_ecc_sign_correction.py` | ❌ Failed (28M× PPL) |
| Latent diffusion | `scripts/experiments/latent_diffusion_signs.py` | ❌ Failed (2717× PPL) |
| Quasicrystal diagnostic | `scripts/experiments/quasicrystal_diagnostic.py` | ✅ Strong form denied |

## Open Questions

1. **What rank does the correction saturate at?** If rank 1-2 ≈ rank 32,
   the adjunction structure is confirmed as the error correcting code.

2. **Does the rank-1 adjunction finding hold for Qwen3-8B?** Session 140
   measured Qwen3-32B. Need to verify on 8B.

3. **Can direct delta + TSP contrastive beat either alone?** Direct delta
   for the analytical correction, TSP for the residual that SVD can't
   capture (e.g., nonlinear effects in the cascade).

4. **What is the compression ratio of direct delta?** At rank-k, each
   projection stores A (out_f × k) + B (k × in_f). At rank-4:
   (12288 × 4 + 4 × 4096) × 2 bytes × 3 projections × 29 layers ≈ 28MB.
   Is this competitive with LoRA at the same rank?

5. **Does calibration-aware SVD significantly beat naive SVD?** The
   experiment runs both. If calibration doesn't help, the correction is
   input-independent (a property of the weight delta alone, not the data).
```

### Thinking

 I need to track down the exact methodology for the s140 measurement—specifically how they're computing that cross-zone mapping claim with the linear regression from activations at one zone to another, then the SVD analysis. The categorical-geometry-probes documentation should have the details on how they're fitting these maps across probe examples.

## Assistant

Now the original measurement method — `explore/categorical-geometry-probes.md` is the cited source for s140:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -i -E \"rank-1|128|R²|R2|zone|regression|lstsq|jacobian|sigma\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md | head -40; echo ===; wc -l /Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md"
}
```

**Summary:** $ grep -n -i -E "rank-1|128|R²|R2|zon...

**Output:**
```
Exit code: 0
Stdout:
63:## Probe 2 — Adjunctions (Cross-Zone Mapping)
69:**Method:** Measure the cross-zone linear map between residual stream
70:representations at different (layer, zone) pairs. Compute SVD to measure
76:SVD of cross-zone map L2→L56 (Zone A → Zone C):
77:  σ₁/σ₂ = 128:1  ← rank-1 dominated
78:  R² for ALL zone pairs = 1.000
81:- **Rank-1 dominated:** The dominant singular value is 128× larger than the
82:  second. Cross-zone mapping is essentially one-dimensional.
83:- **R²=1.000 for all zone pairs:** The map between any two zones is perfectly
84:  predicted by a rank-1 linear model. No residual structure.
159:All four findings — Curry-Howard proof geometry, adjunction rank-1 structure,
168:constraints (type geometry, Curry-Howard separation, adjunction rank-1, hyperbolic
179:| `adjunction_loss` | Cross-stack kurtosis → 1.0 | Rank-1 structure forces mapping to be thin |
===
     189 /Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md",
  "line_offset": 40,
  "limit": 70
}
```

**Summary:** Reading categorical-geometry-probes.md (40-110)

**Output:**
```

```
Well-typed vs ill-typed linear separability:
  L0:   78%
  L8:   89%
  L16: 100% ← perfect separation
  L24: 100%
  L32: 100%
```

- **100% accuracy at L16-L32.** Well-typed and ill-typed compositions are
  perfectly linearly separable from L16 onward.
- **Well-typed pairs pull together:** cosine similarity increases during
  composition (higher at L8-L32 than at L0).
- **Ill-typed pairs push apart:** cosine similarity decreases at the same layers.

**Interpretation:** Curry-Howard confirmed. Valid type compositions occupy a
geometrically distinct "proof region" in residual stream space. The model has
learned to separate the proof-space from the non-proof-space using linear
geometry. This is not symbolic type-checking — it is metric geometry enforcing
typing by distance.

## Probe 2 — Adjunctions (Cross-Zone Mapping)

**Hypothesis:** The B→K→B program (encode → compress → reconstruct) is not
an arbitrary transformation. It is an adjunction: a structured unit/counit
pair where F⊣G with unit η: Id→GF and counit ε: FG→Id.

**Method:** Measure the cross-zone linear map between residual stream
representations at different (layer, zone) pairs. Compute SVD to measure
how much rank the map requires.

**Results:**

```
SVD of cross-zone map L2→L56 (Zone A → Zone C):
  σ₁/σ₂ = 128:1  ← rank-1 dominated
  R² for ALL zone pairs = 1.000
```

- **Rank-1 dominated:** The dominant singular value is 128× larger than the
  second. Cross-zone mapping is essentially one-dimensional.
- **R²=1.000 for all zone pairs:** The map between any two zones is perfectly
  predicted by a rank-1 linear model. No residual structure.

**Interpretation:** The B→K→B program is a single structured transformation,
not an arbitrary neural map. The encode→compress mapping has a unique
"forward" direction (unit η) and the compress→reconstruct has a unique
"backward" direction (counit ε). This is the hallmark of an adjoint pair.
The model IS computing an adjunction.

## Probe 3 — Hyperbolic Geometry

**Hypothesis:** Syntactic tree structure (nesting depth) is encoded in
representation norm, consistent with the Poincaré disk model of hyperbolic
space, where distance from the origin encodes depth in a tree.

**Method:** For tokens at varying syntactic depths (1=root, N=leaf),
compute Spearman ρ between residual norm and syntactic depth at each layer.

**Results:**

```
Spearman ρ (norm vs syntactic depth):
  L0:  ρ = +0.488, p < 0.001  ← strongest
  L4:  ρ = +0.421, p < 0.001
  L8:  ρ = +0.390, p < 0.01
  L16: ρ = +0.362, p < 0.01
  L24: ρ = +0.331, p < 0.05
  L32: ρ = +0.318, p < 0.05

[CONTENT TRUNCATED] Showing lines 41 to 110 of 189 total lines. Use line_offset=110 parameter to read more content.
```

### Thinking

 The description is vague about what exactly was measured—they mention computing SVD on cross-zone linear maps between residual stream representations, which suggests they fit a least-squares transformation from one zone to another across probe sentences and then analyzed the singular value decomposition of either the fitted matrix or the data covariances. I need to find the original script from session 140 to understand the exact computation, so I'm searching for references to cross-zone analysis or adjunction methods in the codebase.

## Assistant

The method description is vague ("measure the cross-zone linear map... compute SVD"). The register gate requires the exact quantity. Let me find the s140 harness:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -rln -i -E \"adjunction|cross.?zone\" /Users/mwhitford/src/verbum/scripts/ 2>/dev/null; echo ===; ls /Users/mwhitford/src/verbum/scripts/experiments/ | head -60"
}
```

**Summary:** $ grep -rln -i -E "adjunction|cross.?...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/v12/extract_pcaq_targets.py
/Users/mwhitford/src/verbum/scripts/v15/crystal.py
/Users/mwhitford/src/verbum/scripts/v15/crystal_base.py
/Users/mwhitford/src/verbum/scripts/v15/__pycache__/v15model.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v15/__pycache__/crystal_base.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v15/__pycache__/train_td.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v15/__pycache__/crystal.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v15/v15model.py
/Users/mwhitford/src/verbum/scripts/v15/train_td.py
/Users/mwhitford/src/verbum/scripts/v14/crystal.py
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/model.cpython-314.pyc
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/model.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/train_td.cpython-314.pyc
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/crystal.cpython-314.pyc
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/train_td.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v14/__pycache__/crystal.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v14/model.py
/Users/mwhitford/src/verbum/scripts/v14/train_td.py
/Users/mwhitford/src/verbum/scripts/v13/train_rb.py
/Users/mwhitford/src/verbum/scripts/v13/config.py
/Users/mwhitford/src/verbum/scripts/v13/__pycache__/config.cpython-314.pyc
/Users/mwhitford/src/verbum/scripts/v13/__pycache__/train_rb.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v13/__pycache__/config.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v13/__pycache__/model.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v13/__pycache__/train_td.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v13/model.py
/Users/mwhitford/src/verbum/scripts/v13/train_td.py
/Users/mwhitford/src/verbum/scripts/experiments/crystal_error_correction.py
/Users/mwhitford/src/verbum/scripts/experiments/verify_bridge_14b.py
/Users/mwhitford/src/verbum/scripts/experiments/verify_bridge_nodes.py
/Users/mwhitford/src/verbum/scripts/experiments/function_discovery.py
/Users/mwhitford/src/verbum/scripts/explore/probe_categorical_geometry.py
/Users/mwhitford/src/verbum/scripts/explore/__pycache__/probe_categorical_geometry.cpython-312.pyc
===
__pycache__
activation_zero_mask.py
assess_v15_attention.py
assess_v15_ffn_retrieval.py
assess_v15_gradient_zeros.py
attention_execution_trace.py
attention_sparsity.py
attention_typed_binding.py
beta_expansion.py
binding_distance_distribution.py
binding_graph_trace.py
binding_prep_lowrank.py
binding_schedule_null.py
binding_schedule_semantic.py
combinator_addressing.py
combined_compression.py
confidence_gate.py
continuation_placement_test.py
copy_program.py
crystal_circuit_types.py
crystal_depth_scan.py
crystal_derivation.py
crystal_distill.py
crystal_ecc_sign_correction.py
crystal_error_correction.py
crystal_hybrid_ternarize.py
crystal_phi_permnull.py
crystal_sieve_pipeline.py
crystal_sieve_prototype.py
crystal_sieve_repro.py
crystal_space_zeros.py
crystal_ternarize.py
crystal_tree.py
crystal_validity.py
crystal_zero_prediction.py
crystal_zero_v2.py
diagnose_ternary.py
dimensional_analysis.py
direct_delta_correction.py
dvd_group_scale.py
dvd_index_test.py
dvd_stamp_test.py
eigenvector_selfsimilarity.py
extract_ternary_plate.py
fact_retrieval_isig.py
ffn_beam_universality.py
ffn_decomposition.py
ffn_kibc_crossref.py
ffn_reduction_trace.py
full_ternarize.py
function_discovery.py
function_mapper.py
gamma_phi_structure.py
gamma_sort_order.py
gate_indexed_ternary.py
gate_zero_predictor.py
gradient_quant_correspondence.py
gradient_zero_map.py
head_combinator_map.py
hierarchical_ternarize.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -i -E \"zone|adjunction|lstsq|rank.?1|svd\" /Users/mwhitford/src/verbum/scripts/explore/probe_categorical_geometry.py | head -40"
}
```

**Summary:** $ grep -n -i -E "zone|adjunction|lsts...

**Output:**
```
Exit code: 0
Stdout:
11:  2. Adjunctions  — The encode (L2) ↔ decode (L56) relationship is more
54:# Zone layers for adjunction probe
477:# Probe 2 — Adjunctions
480:def probe_adjunctions(
487:    similarities between zone layers and measure cross-zone mapping rank.
488:    Zone layers: ENCODE=L2, COMPRESS=L32, DECODE=L56, FINAL=L63.
490:    banner("PROBE 2: Adjunctions (encode↔decode relationship)")
492:    zone_layers = [ENCODE_LAYER, COMPRESS_LAYER, DECODE_LAYER, FINAL_LAYER]
494:    # Per-token cosines per zone pair
500:    # Collect raw residuals per zone for SVD/linear regression
512:            residuals, token_ids = capture_residuals(model, tokenizer, sent, zone_layers)
519:            missing = [L for L in zone_layers if L not in residuals or tok_idx >= residuals[L].shape[0]]
541:        return {"probe": "adjunctions", "error": "no aligned tokens found"}
558:    print(f"\n  Zone-pair cosine statistics:", file=sys.stderr)
570:    # ── SVD of cross-correlation matrix M = Vdec^T Venc / n ──
571:    # Low rank M → structured (adjunction-like) transform enc→dec
576:    def _cross_corr_svd(A: np.ndarray, B: np.ndarray, tag: str) -> dict:
577:        """SVD of cross-correlation A^T B / N."""
580:        # Use randomised SVD via numpy — full SVD is expensive for d=5120
584:            U, s, Vt = np.linalg.svd(M, full_matrices=False, compute_uv=True)
592:            f"    SVD {tag}: top-5 var={top5_var:.3f}  top-20 var={top20_var:.3f}  "
602:    print(f"\n  Cross-correlation SVD (adjunction rank check):", file=sys.stderr)
603:    svd_enc_dec = _cross_corr_svd(E, D, "L2→L56")
604:    svd_enc_comp = _cross_corr_svd(E, C, "L2→L32")
605:    svd_comp_dec = _cross_corr_svd(C, D, "L32→L56")
611:            W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
629:        "probe": "adjunctions",
630:        "description": "Zone-pair cosine similarity and cross-zone mapping rank",
638:        "svd": {
639:            "enc_dec_L2_L56": svd_enc_dec,
640:            "enc_comp_L2_L32": svd_enc_comp,
641:            "comp_dec_L32_L56": svd_comp_dec,
960:    # ── Plot 2: Adjunction cross-zone distributions ──
962:        adj = results.get("adjunctions", {})
979:            ax.set_title("Adjunction: cross-zone cosine distributions")
983:            zone_means = [
988:            zone_stds = [
995:            ax2.bar(range(4), zone_means, yerr=zone_stds, capsize=5,
1000:            ax2.set_title("Cross-zone mean cosine (adjunction check)")
1010:            path = results_dir / "adjunction_cross_zone.png"
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_categorical_geometry.py",
  "line_offset": 490,
  "limit": 160
}
```

**Summary:** Reading probe_categorical_geometry.py (490-650)

**Output:**
```

    zone_layers = [ENCODE_LAYER, COMPRESS_LAYER, DECODE_LAYER, FINAL_LAYER]

    # Per-token cosines per zone pair
    cos_enc_dec: list[float] = []     # L2 ↔ L56
    cos_enc_comp: list[float] = []    # L2 ↔ L32
    cos_comp_dec: list[float] = []    # L32 ↔ L56
    cos_enc_final: list[float] = []   # L2 ↔ L63

    # Collect raw residuals per zone for SVD/linear regression
    vecs_enc: list[np.ndarray] = []
    vecs_comp: list[np.ndarray] = []
    vecs_dec: list[np.ndarray] = []

    for sent_idx, (sent, word_labels) in enumerate(well_typed):
        print(
            f"    {sent_idx + 1}/{len(well_typed)}: {sent[:60]}",
            file=sys.stderr,
            flush=True,
        )
        try:
            residuals, token_ids = capture_residuals(model, tokenizer, sent, zone_layers)
            aligned = align_tokens_to_labels(tokenizer, token_ids, word_labels)
        except Exception as e:
            print(f"      ⚠  capture failed: {e}", file=sys.stderr)
            continue

        for tok_idx, _ in aligned:
            missing = [L for L in zone_layers if L not in residuals or tok_idx >= residuals[L].shape[0]]
            if missing:
                continue

            ve = residuals[ENCODE_LAYER][tok_idx]
            vc = residuals[COMPRESS_LAYER][tok_idx]
            vd = residuals[DECODE_LAYER][tok_idx]
            vf = residuals[FINAL_LAYER][tok_idx]

            cos_enc_dec.append(cosine(ve, vd))
            cos_enc_comp.append(cosine(ve, vc))
            cos_comp_dec.append(cosine(vc, vd))
            cos_enc_final.append(cosine(ve, vf))

            vecs_enc.append(ve)
            vecs_comp.append(vc)
            vecs_dec.append(vd)

        del residuals
        gc.collect()

    if not vecs_enc:
        return {"probe": "adjunctions", "error": "no aligned tokens found"}

    # ── Summary statistics ──
    def _stats(vals: list[float]) -> dict:
        a = np.array(vals)
        return {
            "mean": float(a.mean()),
            "std": float(a.std()),
            "median": float(np.median(a)),
            "n": len(vals),
        }

    stats_enc_dec = _stats(cos_enc_dec)
    stats_enc_comp = _stats(cos_enc_comp)
    stats_comp_dec = _stats(cos_comp_dec)
    stats_enc_final = _stats(cos_enc_final)

    print(f"\n  Zone-pair cosine statistics:", file=sys.stderr)
    for name, st in [
        ("L2↔L56 (enc↔dec)", stats_enc_dec),
        ("L2↔L32 (enc↔comp)", stats_enc_comp),
        ("L32↔L56 (comp↔dec)", stats_comp_dec),
        ("L2↔L63 (enc↔final)", stats_enc_final),
    ]:
        print(
            f"    {name:25s}: mean={st['mean']:+.3f}  std={st['std']:.3f}  n={st['n']}",
            file=sys.stderr,
        )

    # ── SVD of cross-correlation matrix M = Vdec^T Venc / n ──
    # Low rank M → structured (adjunction-like) transform enc→dec
    E = np.array(vecs_enc)   # (N, d)
    C = np.array(vecs_comp)
    D = np.array(vecs_dec)

    def _cross_corr_svd(A: np.ndarray, B: np.ndarray, tag: str) -> dict:
        """SVD of cross-correlation A^T B / N."""
        n = A.shape[0]
        M = (A.T @ B) / n  # (d, d)
        # Use randomised SVD via numpy — full SVD is expensive for d=5120
        # We just compute the top-k singular values
        k = min(50, n - 1, M.shape[0])
        try:
            U, s, Vt = np.linalg.svd(M, full_matrices=False, compute_uv=True)
            top_k = s[:k]
        except Exception:
            top_k = np.zeros(k)
        total_var = float(np.sum(s ** 2)) if len(s) > 0 else 1.0
        top5_var = float(np.sum(top_k[:5] ** 2)) / (total_var + 1e-12)
        top20_var = float(np.sum(top_k[:20] ** 2)) / (total_var + 1e-12)
        print(
            f"    SVD {tag}: top-5 var={top5_var:.3f}  top-20 var={top20_var:.3f}  "
            f"singular[0]={top_k[0]:.2f}  singular[4]={top_k[min(4,len(top_k)-1)]:.2f}",
            file=sys.stderr,
        )
        return {
            "top5_variance_explained": float(top5_var),
            "top20_variance_explained": float(top20_var),
            "singular_values_top10": [float(v) for v in top_k[:10]],
        }

    print(f"\n  Cross-correlation SVD (adjunction rank check):", file=sys.stderr)
    svd_enc_dec = _cross_corr_svd(E, D, "L2→L56")
    svd_enc_comp = _cross_corr_svd(E, C, "L2→L32")
    svd_comp_dec = _cross_corr_svd(C, D, "L32→L56")

    # ── Linear regression R² L2→L56 vs L2→L32 ──
    def _r2(A: np.ndarray, B: np.ndarray) -> float:
        """Mean per-dimension R² of linear regression A→B (via pseudoinverse)."""
        try:
            W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
            B_pred = A @ W
            ss_res = np.sum((B - B_pred) ** 2, axis=0)
            ss_tot = np.sum((B - B.mean(axis=0)) ** 2, axis=0)
            r2_per_dim = 1.0 - ss_res / (ss_tot + 1e-12)
            return float(r2_per_dim.mean())
        except Exception:
            return float("nan")

    r2_enc_dec = _r2(E, D)
    r2_enc_comp = _r2(E, C)
    r2_comp_dec = _r2(C, D)
    print(f"\n  Linear regression R² (mean per-dim):", file=sys.stderr)
    print(f"    L2→L56: {r2_enc_dec:.4f}", file=sys.stderr)
    print(f"    L2→L32: {r2_enc_comp:.4f}", file=sys.stderr)
    print(f"    L32→L56: {r2_comp_dec:.4f}", file=sys.stderr)

    return {
        "probe": "adjunctions",
        "description": "Zone-pair cosine similarity and cross-zone mapping rank",
        "n_tokens": len(vecs_enc),
        "cosine_stats": {
            "enc_dec_L2_L56": stats_enc_dec,
            "enc_comp_L2_L32": stats_enc_comp,
            "comp_dec_L32_L56": stats_comp_dec,
            "enc_final_L2_L63": stats_enc_final,
        },
        "svd": {
            "enc_dec_L2_L56": svd_enc_dec,
            "enc_comp_L2_L32": svd_enc_comp,
            "comp_dec_L32_L56": svd_comp_dec,
        },
        "r2": {
            "enc_dec_L2_L56": r2_enc_dec,
            "enc_comp_L2_L32": r2_enc_comp,
            "comp_dec_L32_L56": r2_comp_dec,
        },
        # Raw cosine lists for plotting
        "_raw_cosines": {
            "enc_dec": cos_enc_dec,

[CONTENT TRUNCATED] Showing lines 491 to 650 of 1275 total lines. Use line_offset=650 parameter to read more content.
```

### Thinking

 So the cross-zone map is actually the SVD of an uncentered cross-correlation matrix between raw residual vectors from different zone layers, and that singular value ratio of 128:1 comes directly from this decomposition. The regression analysis shows perfect R² across all 5120 dimensions when fitting one zone's residuals to another with the full token set.

But there's a critical issue: if the number of tokens is much smaller than the dimensionality—likely just 50-100 tokens from a handful of sentences—then the least-squares regression is underdetermined and will trivially achieve perfect fit regardless of whether there's any real structure. That R²=1.000 is just an artifact of having fewer samples than features. The dominant singular value ratio is also likely inflated by the uncentered data: the residual streams have large mean components (that "carrier wave" with eigenvalues in the hundreds of thousands), so when you compute cross-correlation without centering, the shared mean direction dominates and creates artificial rank-1 structure. The real signal might be much weaker once you account for these confounds—centering the data and checking the actual token count would reveal whether either finding holds up. For 8B (36 layers), I'm mapping the zones proportionally to the original s140 setup: early, middle, late, and final layers. I need to collect residuals across many tokens—ideally N > d=4096, though starting with smaller N to reproduce the original result, then scaling up for honest estimation. The measurement plan involves the original instrument (uncentered SVD), row-shuffled null (permuting token pairing to break the map while preserving marginals), random Gaussian null with matched statistics, and a centered version to see if the rank-1 ratio depends on the mean structure.

For the honest rank assessment, I'll use held-out R² with ridge regression at N > d to measure true mapping quality and effective rank—whether rank-1 actually captures the cross-zone predictable variance. The centered and shuffled nulls should reveal whether the 128:1 ratio is real map structure or just the carrier mean; if it collapses under centering, that's the answer. I'll run multiple seeds for the nulls and compare against the direct-delta rank sweep evidence from s201, which already hints that rank-1 alone isn't sufficient for the correction.

Now I need to set up the task list and write the harness. I'm checking how existing harnesses load the model—looking at patterns in binding_schedule_null.py or sign_topology_null.py for consistency. The experiments run in tmux on olga.local (Apple Silicon, MPS, 480G unified), and I should verify the hostname to confirm I'm on the right machine. Let me draft the task plan, declare the register gate explicitly, then examine an existing harness for the loading pattern.

## Assistant

I now have the original instrument pinned. Before anything else — **Step 0, REGISTER GATE**, and it fires loudly here because I can already see two structural artifacts in the s140 probe itself:

## Register gate — audit #8

**The claim** (`direct-delta-adjunction.md`, `explore/categorical-geometry-probes.md`): "the cross-zone map encode→decode is rank-1 dominated (σ₁/σ₂=128:1); R²=1.000 for all zone pairs; the Jacobian has constant rank 1 → computation lives on a 1D curve."

**Claim register: spectral** (singular-value structure of an estimated linear map), with a functional over-read on top (1D curve → rank-1 correction suffices).

**The original instrument** (`probe_categorical_geometry.py`, s140, Qwen3-32B):
1. `M = (EᵀD)/N` — **uncentered** cross-correlation of raw residual vectors at zone layers → SVD → σ₁/σ₂.
2. `np.linalg.lstsq(E, D)` mean per-dim R² with N tokens, d=5120.

**Two suspected structural confounds, both visible from the code:**

| Artifact | Mechanism | Prediction |
|---|---|---|
| **R²=1.000 is an underdetermination tautology** | lstsq with N tokens ≪ d=5120 dims has more unknowns than equations → exact interpolation → R²=1.000 for *any* data, including pure noise | random Gaussian "zones" also give R²=1.000 |
| **σ₁/σ₂=128 is the carrier mean, not the map** | residual vectors are uncentered and the stream has a huge shared mean direction (s185: within-zone λ₁/λ₂ ≈ 4000–8800× — the rank-1 carrier wave). `EᵀD` of two clouds with dominant means is generically rank-1 dominated regardless of any *mapping* | row-shuffled pairing (destroys the token correspondence, keeps marginals) preserves 128:1; centering collapses it |

**Probe register: spectral** — same quantity (σ₁/σ₂ of the cross-zone estimator), against the right nulls, plus an *honest* fit (held-out ridge, N>d) for the rank-k sufficiency question. Match confirmed.

Let me set the plan:

### Thinking

 Let me check the start status and look at an existing audit harness to understand the model-loading and result conventions—I'll examine something like svd_phi_null.py or binding_schedule_null.py to see how they're structured.

### Thinking

I'm checking the most recent audit harness to understand its loading and result conventions.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py",
  "limit": 120
}
```

**Summary:** Reading binding_schedule_semantic.py (0-120)

**Output:**
```
#!/usr/bin/env python3
"""Audit #5 (SEMANTIC leg) — does the binding schedule hold for VALUE TRANSFER?

The attention-weight control (`binding_schedule_null.py`) tests routing/position:
WHERE attention is sharp. But the claim (`binding-graph-trace.md`, Finding 7 /
Implication 2/4) is SEMANTIC:

  "Head output IS the reduction result -- H31 at L27 produces '猫' at position
   'runs' when it reads 'cat' ... the VALUE TRANSFER step of beta-reduction."
  Schedule: the verb position ABSORBS THE SUBJECT'S IDENTITY at L27, the object
  absorbs the predicate at L30, coref at L33 -- a depth ordering of SEMANTIC
  absorption.  Evidence was a LOGIT-LENS on the head's OUTPUT.

Early attention concentration (L4-L6, found by the weight control) does NOT
refute a LATE semantic schedule: semantic content is often written into the
residual at deeper layers. So we need the SEMANTIC instrument the claim used.

Instrument — per-head logit-lens of the output contribution
-----------------------------------------------------------
For each dependency type and many sentences, at EVERY layer L, for the named
head h, take the head's contribution to the residual at the DEPENDENT position:

    c_h = W_oproj[:, h*hd:(h+1)*hd] @ (attn_h value-weighted-sum at dep_pos)

(captured via an o_proj forward-pre-hook), then logit-lens through lm_head and
read the SEMANTIC MARGIN toward the bound entity:

    m_h[L] = logit(token@head_pos) - logit(token@control_pos)
           = lm_head[tok_head] . c_h  -  lm_head[tok_ctrl] . c_h

i.e. does this head's output, at the dependent position, point to the GRAMMATICAL
HEAD's token more than to another in-context content token? (control = earliest
other content token; an in-context, distance/frequency-matched null.)

  subj : dep=verb,   head=subject noun  -> does the verb absorb the subject identity?
  obj  : dep=object, head=verb          -> does the object absorb the predicate?
  coref: dep="it",   head=antecedent    -> does the pronoun absorb the antecedent?

Tests
-----
  PART A  Semantic schedule: per-type semantic-transfer curve m_named[L] across
          all layers; peak layer; bootstrap P(peak(subj)<peak(obj)<peak(coref))
          + per-type peak CIs. Also the margin at the CLAIMED layer vs its peak.
  PART B  Named-head specificity at the claimed layer: rank the named head's
          semantic margin against all 32 heads (z, rank).

Verdict
-------
  SEMANTIC schedule real : m_named>0 (entity is promoted), peaks in the claimed
                           L27<L30<L33 order (bootstrap P >> 1/6), named head an
                           outlier at its layer.
  NOT a schedule         : margins ~0 / negative, or peak order not L27<L30<L33,
                           or named head not special. Value-transfer schedule
                           is over-read.

Usage:
  uv run python scripts/experiments/binding_schedule_semantic.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

# register: value  (logit-lens of head output — the matched register for the
#                   SEMANTIC value-transfer claim; see AGENTS.md λ measure,
#                   audit-registry §register slot. This is the probe that found
#                   the real H31@L27 subject-identity signal the routing probe missed.)

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent

NAMED_SCHEDULE = {"subj": (27, [31]), "obj": (30, [3, 13, 15]), "coref": (33, [6, 7])}

NOUNS = [
    "dog", "cat", "boy", "girl", "man", "woman", "bird", "horse", "teacher",
    "doctor", "farmer", "pilot", "singer", "king", "queen", "soldier", "child",
    "fox", "wolf", "lion", "nurse", "driver", "painter", "baker",
]
VERBS_INTRANS = [
    "runs", "sleeps", "jumps", "sings", "barks", "waits", "smiles", "works",
    "rests", "dreams", "laughs", "cries", "stumbles", "wanders", "hesitates",
]
VERBS_TRANS = [
    "chased", "found", "watched", "kicked", "carried", "pushed", "bit",
    "grabbed", "followed", "saw", "held", "dropped", "caught", "fed",
]
OBJECTS = [
    "ball", "book", "apple", "stick", "rope", "bone", "toy", "box", "cup",
    "flag", "drum", "kite", "leaf", "rock", "coin", "key", "hat", "shoe",
]
ADVS = ["quietly", "slowly", "today", "again", "alone", "outside", "early"]
ADJS = ["tired", "hungry", "afraid", "happy", "cold", "lost", "calm", "brave"]


def log(msg=""):
    print(msg, flush=True)


def build_stimuli(n_per, seed=7):
    rng = np.random.default_rng(seed)
    out = {"subj": [], "obj": [], "coref": []}
    for _ in range(n_per):
        n = rng.choice(NOUNS)
        vi = rng.choice(VERBS_INTRANS)
        adv = rng.choice(ADVS)
        out["subj"].append({"sentence": f"The {n} {vi} {adv}.",
                            "dep_word": vi, "head_word": n})
        n1 = rng.choice(NOUNS)
        vt = rng.choice(VERBS_TRANS)
        ob = rng.choice(OBJECTS)

[CONTENT TRUNCATED] Showing lines 1 to 120 of 374 total lines. Use line_offset=120 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -E \"def capture_residuals|output_hidden_states|hidden_states|from_pretrained|device|dtype\" /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py | head -20; echo ===; hostname; python3 -c \"import platform; print(platform.machine())\""
}
```

**Summary:** $ grep -n -E "def capture_residuals|o...

**Output:**
```
Exit code: 0
Stdout:
61:    --model Qwen/Qwen3-8B --device mps
182:def schedule_profile(model, tokenizer, stim, n_layers, n_heads, device,
193:            ids = enc["input_ids"].to(device)
271:def head_ranks_at_peak(model, tokenizer, stim, peak_layer, dep, n_heads, device):
277:        ids = enc["input_ids"].to(device)
344:def agreement_logit_diff(model, tokenizer, items, device, cfg, head_dim, id_is, id_are):
349:            ids = tokenizer(it["cloze"], return_tensors="pt")["input_ids"].to(device)
367:    p.add_argument("--device", default="mps")
377:    log(f"  Model: {args.model}  Device: {args.device}  n_per={args.n_per}")
379:    dtype = (torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"])
381:    log(f"  Loading {args.model} ({dtype}) ...")
382:    model = AutoModelForCausalLM.from_pretrained(
383:        args.model, dtype=dtype, device_map=args.device, attn_implementation="eager")
384:    tokenizer = AutoTokenizer.from_pretrained(args.model)
405:        model, tokenizer, stim, n_layers, n_heads, args.device)
445:        hr = head_ranks_at_peak(model, tokenizer, stim, layer, d, n_heads, args.device)
462:        model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)
467:        r = agreement_logit_diff(model, tokenizer, agree, args.device,
483:                model, tokenizer, agree, args.device,
===
olga.local
arm64
```

### Thinking

 We're working on the Olga setup with standard conventions like argparse and device flags, using fp16 for the 8B model and output_hidden_states to capture residuals. For the 36-layer architecture, I'm mapping the zone layers proportionally from the 32B model's structure: L1 for encoding, L18 for compression, L31 for decoding, and L35 for the final layer.

Now I'm verifying the layer calculations — the proportional scaling checks out. For the text data, I need to gather prose tokens for calibration, likely around 8-12k tokens to fit the held-out set. I'll check what previous harnesses used for calibration texts, maybe pulling from a dolma file if available in the repo, or I can generate diverse sentences from templates as a fallback.

### Thinking

I'm checking what text corpus the previous harnesses used to ensure I have enough tokens (N > d = 4096) for the honest fit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -rln \"dolma\" /Users/mwhitford/src/verbum/scripts/experiments/ | head -5; echo ===; grep -n -A5 \"dolma\" /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py | head -30; echo ===; ls /Users/mwhitford/src/verbum/data 2>/dev/null; ls /Users/mwhitford/src/verbum/*.txt 2>/dev/null"
}
```

**Summary:** $ grep -rln "dolma" /Users/mwhitford/...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py
/Users/mwhitford/src/verbum/scripts/experiments/score_matching_compression.py
===
===
compile-eval.jsonl
compile-full.json
compile-test.jsonl
compile-train.jsonl
structured_shard_qwen36.npy
structured_shard_v2.npy
structured_shard.npy
/Users/mwhitford/src/verbum/ideas.txt
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B2 -A12 \"dolma\" /Users/mwhitford/src/verbum/scripts/experiments/score_matching_compression.py | head -50"
}
```

**Summary:** $ grep -n -B2 -A12 "dolma" /Users/mwh...

**Output:**
```
Exit code: 0
Stdout:
563-                        np.mean(list(per_layer_cos.values())))
564-            else:
565:                # CE only (dolma diversity)
566-                labels = input_ids.clone()
567-                out = model(input_ids=input_ids, labels=labels)
568-                ce_loss = out.loss
569-                loss = ce_loss
570-
571-            if not (torch.isnan(loss) or torch.isinf(loss)):
572-                loss.backward()
573-                step_ce += ce_loss.item() * input_ids.numel()
574-                step_tokens += input_ids.numel()
575-
576-        if step_tokens > 0:
577-            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B3 -A15 \"def.*dolma\\|dolma_path\\|load_dolma\\|DOLMA\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py | head -50"
}
```

**Summary:** $ grep -n -B3 -A15 "def.*dolma\|dolma...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -rn \"allenai/dolma\\|load_dataset\\|olmo-mix\\|HF_DATASETS\\|wikitext\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py /Users/mwhitford/src/verbum/scripts/experiments/score_matching_compression.py | head; echo ===; ls ~/.cache/huggingface/datasets 2>/dev/null | head"
}
```

**Summary:** $ grep -rn "allenai/dolma\|load_datas...

**Output:**
```
Exit code: 0
Stdout:
===
wikitext
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -rn \"dolma\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py | head -5; echo ===; grep -rn \"DOLMA_DIR\\|dolma\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py | head; echo ===; find /Users/mwhitford -maxdepth 3 -iname \"*dolma*\" 2>/dev/null | head; echo ===; ls ~/.cache/huggingface/datasets/wikitext 2>/dev/null"
}
```

**Summary:** $ grep -rn "dolma" /Users/mwhitford/s...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:2:"""Residual Boosting v2 — proper calibration with dolma shards.
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:9:  - Calibration: dolma shards (real prose, thousands of sequences)
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:10:  - Eval: held-out dolma sequences (no overlap with calibration)
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:482:    log("  RESIDUAL BOOSTING v2 — dolma calibration, round-robin placement")
===
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:2:"""Residual Boosting v2 — proper calibration with dolma shards.
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:9:  - Calibration: dolma shards (real prose, thousands of sequences)
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:10:  - Eval: held-out dolma sequences (no overlap with calibration)
/Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py:482:    log("  RESIDUAL BOOSTING v2 — dolma calibration, round-robin placement")
===
/Users/mwhitford/data/fractal-bitnet/dolma-raw
===
wikitext-2-raw-v1
```

### Thinking

 I need to check where the Dolma raw data is located and see how residual_boosting_v2 loads it from that directory.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B3 -A20 \"dolma-raw\\|def load_cal\\|def get_sequences\\|json.gz\\|jsonl\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py | head -60; echo ===; ls /Users/mwhitford/data/fractal-bitnet/dolma-raw | head"
}
```

**Summary:** $ grep -n -B3 -A20 "dolma-raw\|def lo...

**Output:**
```
Exit code: 0
Stdout:
===
000_00000.parquet
000_00001.parquet
000_00002.parquet
000_00003.parquet
000_00004.parquet
000_00005.parquet
000_00006.parquet
000_00007.parquet
000_00008.parquet
000_00009.parquet
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B2 -A18 \"parquet\" /Users/mwhitford/src/verbum/scripts/experiments/residual_boosting_v2.py | head -50"
}
```

**Summary:** $ grep -n -B2 -A18 "parquet" /Users/m...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -rn \"dolma-raw\\|parquet\" /Users/mwhitford/src/verbum/scripts/ 2>/dev/null | grep -v Binary | head -10"
}
```

**Summary:** $ grep -rn "dolma-raw\|parquet" /User...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:2:"""Re-tokenize Dolma parquet shards with Qwen3 BBPE for v8 training.
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:4:Reads raw Dolma parquet files (text column), tokenizes each document
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:10:Input:  /Users/mwhitford/data/fractal-bitnet/dolma-raw/*.parquet
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:47:RAW_DIR = Path("/Users/mwhitford/data/fractal-bitnet/dolma-raw")
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:53:# Batch size for parquet reading — avoid loading full parquet into memory
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:143:                        help="Directory containing Dolma parquet files")
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:149:                        help="Process only first parquet, cap at 1 shard")
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:153:    import pyarrow.parquet as pq
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:167:    # ── Discover parquet files ────────────────────────────────────
/Users/mwhitford/src/verbum/scripts/v8/retokenize_dolma.py:168:    parquet_files = sorted(
```

### Thinking

 I've got the dolma parquet files loaded with text columns readable via pyarrow, so I'll sample one file, extract documents, and tokenize them to count tokens. Now I'm mapping out the harness architecture with four distinct zones across Qwen3-8B's 36 layers: encoding at layer 1, compression at layer 18, decoding at layer 31, and final processing at layer 35, scaled proportionally from the 32B model's zone distribution.

For capturing hidden states, I'll use `output_hidden_states=True` to extract the output after each layer (indices 1 through 36, where index 0 is embeddings), then use hidden_states[L] for zone L. In the small-N regime, I'm generating around 15 well-typed sentences yielding roughly 120 tokens to reproduce the s140 setup, while the large-N regime pulls from dolma documents tokenized to sequence length 512, collecting per-token residuals across all four zones until I hit about 12,000 tokens total (8k train, 4k test) — memory footprint comes to roughly 196MB per zone, which is manageable.

For measurements, I'm reproducing the original instrument on small N by computing the uncentered M = EᵀD/N, running SVD to get σ₁/σ₂ and top-5 variance, then least-squares fitting E→D for mean per-dimension R² across all zone pairs. I'll also run the tautology proof with random Gaussian E' and D' matrices to establish the baseline R² under the null hypothesis.

For the σ₁/σ₂ ratio nulls, I'm testing shuffled-pairing (permuting D rows relative to E) and matched Gaussian nulls with independent zones, plus a centered version that subtracts means to isolate cross-covariance structure. On the large-N side, I'm fitting ridge regression with an intercept on the training set, examining the SVD spectrum of the fitted weight matrix and its participation ratio, then evaluating held-out R² across rank-k truncations to see whether the mapping is genuinely rank-1 or driven by marginal structure.

The decision rules are: the σ₁/σ₂ claim holds only if the real ratio substantially exceeds both shuffled and matched nulls and survives centering; R²=1.000 is an artifact if random data also achieves it at small N; and rank-1 sufficiency is confirmed if the held-out R² at k=1 reaches 90% of the full-rank value. I'm loading the model in fp16 on MPS with hidden states enabled, batching 24 sequences of 512 tokens for speed, sampling all token positions except the first to avoid BOS effects, and running 8 seeds for the nulls. The output goes to results/adjunction-rank-null/Qwen_Qwen3-8B.json.

I'm also adding a random-target test where I fit ridge regression from embeddings to shuffled data and check that held-out R² stays near zero, confirming the estimator isn't leaking signal. The script will have a smoke mode flag for faster iteration with fewer tokens and seeds. I'll write the harness now, keeping it around 430 lines, then commit it after a smoke test.

### Thinking

Dolma parquet shards are available locally, so I'll write the harness now.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Audit #8 — rank-1 adjunction (sigma1/sigma2 = 128:1 cross-zone): real map\nstructure, or marginal/estimator artifact?\n\nThe claim (s140, Qwen3-32B; `direct-delta-adjunction.md`,\n`explore/categorical-geometry-probes.md`):\n\n    \"SVD of cross-zone map L2->L56: sigma1/sigma2 = 128:1 (rank-1 dominated);\n     R^2 = 1.000 for ALL zone pairs. The Jacobian of encode->decode has\n     constant rank 1 -> the computation lives on a 1D curve in d-space.\"\n\nThe original instrument (`probe_categorical_geometry.py`, probe 2):\n  (i)  M = (E^T D)/N on UNCENTERED residual vectors -> SVD -> sigma1/sigma2\n  (ii) np.linalg.lstsq(E, D) mean per-dim R^2, with N tokens << d dims\n\nTwo suspected STRUCTURAL artifacts, visible from the instrument itself:\n\n  A. R^2 = 1.000 is an underdetermination tautology. lstsq with N < d has\n     more unknowns than equations -> exact interpolation -> R^2 = 1.000 for\n     ANY data, including pure noise. (control: random Gaussian zones)\n\n  B. sigma1/sigma2 is the carrier mean, not the map. The residual stream has\n     a dominant shared mean direction (s185: within-zone lambda1/lambda2 ~\n     4000-8800x). The uncentered cross-correlation of two clouds with large\n     means is generically rank-1 dominated REGARDLESS of any token-level\n     mapping. (controls: row-shuffled pairing, matched-Gaussian, centering)\n\nTests\n-----\n  PART A  Reproduce the original instrument at s140-like small N on Qwen3-8B\n          zones (also answers `direct-delta-adjunction.md` open question #2).\n  PART B  R^2 tautology proof: lstsq R^2 on iid random + matched-marginal\n          random data at N < d (8 seeds). If 1.000 -> the R^2 leg is void.\n  PART C  sigma1/sigma2 nulls (same instrument, same N):\n            - row-shuffled pairing (destroys the map, keeps marginals)\n            - matched Gaussian (per-zone mean+cov, independent draws)\n            - centered real data (cross-covariance instead of cross-corr)\n          If nulls reproduce the ratio and centering collapses it, the\n          \"128:1\" is the carrier, not adjunction structure.\n  PART D  Honest map estimate at N > d (dolma prose, train/test split):\n          centered ridge fit E->D, SVD of fitted W, held-out R^2 of rank-k\n          truncations (k = 1,2,4,...). The honest \"is the map rank-1?\" curve,\n          vs a shuffled-pairing fit (estimator-leak control).\n\nVerdict\n-------\n  REAL      : real sigma1/sigma2 >> shuffled/matched nulls AND survives\n              centering; held-out rank-1 captures ~all predictable variance.\n  ARTIFACT  : nulls reproduce the ratio (carrier mean) and/or random data\n              gives R^2=1.000 (tautology); held-out curve needs rank >> 1.\n\nUsage:\n  uv run python scripts/experiments/adjunction_rank_null.py \\\n      --model Qwen/Qwen3-8B --device mps\n  uv run python scripts/experiments/adjunction_rank_null.py --smoke\n\nLicense: MIT\n\"\"\"\n\n# register: spectral  (singular-value structure of the estimated cross-zone\n#   linear map — the same quantity the claim is about, measured with the\n#   original estimator AND an honest held-out estimator, against marginal-\n#   preserving nulls. See AGENTS.md lambda measure; audit-registry step 0.)\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\n\nDOLMA_DIR = Path(\"/Users/mwhitford/data/fractal-bitnet/dolma-raw\")\n\n# Zone layers. 32B (64 layers) used ENCODE=L2, COMPRESS=L32, DECODE=L56,\n# FINAL=L63. Proportional map to Qwen3-8B's 36 layers:\nZONES_8B = {\"encode\": 1, \"compress\": 18, \"decode\": 31, \"final\": 35}\n\n# s140-flavor well-typed sentences (small-N regime)\nSMALL_SENTENCES = [\n    \"The cat chased the mouse across the garden.\",\n    \"A teacher explained the lesson to the students.\",\n    \"The river flows quietly through the old valley.\",\n    \"She placed the heavy book on the wooden table.\",\n    \"The pilot landed the plane during the storm.\",\n    \"A farmer planted seeds in the fertile soil.\",\n    \"The children played games near the tall fence.\",\n    \"He repaired the broken clock with small tools.\",\n    \"The singer performed a song for the audience.\",\n    \"A doctor examined the patient in the clinic.\",\n    \"The dog buried a bone behind the green shed.\",\n    \"The committee approved the plan after debate.\",\n    \"Workers built a bridge over the narrow stream.\",\n    \"The artist painted a portrait of the queen.\",\n    \"A soldier guarded the gate through the night.\",\n]\n\nZONE_PAIRS = [(\"encode\", \"compress\"), (\"compress\", \"decode\"),\n              (\"encode\", \"decode\")]\n\n\ndef log(msg=\"\"):\n    print(msg, flush=True)\n\n\n# ──────────────────────────────────────────────────────────────────────\n# Activation capture\n# ──────────────────────────────────────────────────────────────────────\n\n@torch.no_grad()\ndef capture_zone_residuals(model, tokenizer, texts, zone_layers, device,\n                           max_len=512, max_tokens=None, skip_first=1):\n    \"\"\"Run texts, return {zone_name: (N, d) float32 array} aligned per token.\"\"\"\n    buf = {z: [] for z in zone_layers}\n    n_collected = 0\n    for ti, text in enumerate(texts):\n        enc = tokenizer(text, return_tensors=\"pt\", truncation=True,\n                        max_length=max_len)\n        ids = enc[\"input_ids\"].to(device)\n        if ids.shape[1] <= skip_first + 1:\n            continue\n        out = model(input_ids=ids, output_hidden_states=True)\n        hs = out.hidden_states  # tuple, len n_layers+1; [0]=embeddings\n        for z, L in zone_layers.items():\n            v = hs[L][0, skip_first:, :].float().cpu().numpy()\n            buf[z].append(v)\n        n_collected += ids.shape[1] - skip_first\n        del out, hs\n        if max_tokens is not None and n_collected >= max_tokens:\n            break\n    res = {z: np.concatenate(buf[z], axis=0) for z in zone_layers}\n    if max_tokens is not None:\n        res = {z: a[:max_tokens] for z, a in res.items()}\n    return res\n\n\ndef load_dolma_texts(n_docs, min_chars=2000, seed=0):\n    \"\"\"Sample documents from the local dolma parquet shards.\"\"\"\n    import pyarrow.parquet as pq\n    files = sorted(DOLMA_DIR.glob(\"*.parquet\"))\n    if not files:\n        raise FileNotFoundError(f\"no parquet under {DOLMA_DIR}\")\n    rng = np.random.default_rng(seed)\n    tbl = pq.read_table(files[0], columns=[\"text\"])\n    texts = [t for t in tbl.column(\"text\").to_pylist()\n             if t and len(t) >= min_chars]\n    idx = rng.permutation(len(texts))[:n_docs]\n    return [texts[i] for i in idx]\n\n\n# ──────────────────────────────────────────────────────────────────────\n# The two instruments\n# ──────────────────────────────────────────────────────────────────────\n\ndef cross_corr_spectrum(A, B, center=False, k=64):\n    \"\"\"SVD spectrum of the s140 estimator M = A^T B / N (optionally centered).\"\"\"\n    if center:\n        A = A - A.mean(axis=0, keepdims=True)\n        B = B - B.mean(axis=0, keepdims=True)\n    n = A.shape[0]\n    M = (A.T @ B) / n\n    s = np.linalg.svd(M, compute_uv=False)\n    s = s[:k]\n    total = float(np.sum(s ** 2)) + 1e-30\n    return {\n        \"sigma1_over_sigma2\": float(s[0] / (s[1] + 1e-30)),\n        \"top1_var\": float(s[0] ** 2 / total),\n        \"top5_var\": float(np.sum(s[:5] ** 2) / total),\n        \"singular_top10\": [float(v) for v in s[:10]],\n    }\n\n\ndef lstsq_mean_r2(A, B):\n    \"\"\"The s140 R^2 instrument verbatim: lstsq fit, in-sample mean per-dim R^2.\"\"\"\n    W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)\n    P = A @ W\n    ss_res = np.sum((B - P) ** 2, axis=0)\n    ss_tot = np.sum((B - B.mean(axis=0)) ** 2, axis=0)\n    return float(np.mean(1.0 - ss_res / (ss_tot + 1e-12)))\n\n\ndef matched_gaussian(X, rng):\n    \"\"\"Gaussian sample with X's mean and covariance (independent of any map).\"\"\"\n    n, d = X.shape\n    mu = X.mean(axis=0)\n    Xc = X - mu\n    # sample via SVD of the centered data (exact covariance factor, cheap)\n    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)\n    Z = rng.standard_normal((n, len(s)))\n    return mu + (Z * (s / np.sqrt(max(n - 1, 1)))) @ Vt\n\n\ndef carrier_stats(X):\n    \"\"\"Diagnostic: how dominant is the mean (carrier) vs centered variance?\"\"\"\n    mu = X.mean(axis=0)\n    Xc = X - mu\n    sc = np.linalg.svd(Xc, compute_uv=False)\n    su = np.linalg.svd(X, compute_uv=False)\n    return {\n        \"mean_norm\": float(np.linalg.norm(mu)),\n        \"centered_sigma1\": float(sc[0]),\n        \"uncentered_sigma1_over_sigma2\": float(su[0] / (su[1] + 1e-30)),\n        \"mean_energy_share\": float(\n            X.shape[0] * np.linalg.norm(mu) ** 2\n            / (np.linalg.norm(X) ** 2 + 1e-30)),\n    }\n\n\n# ──────────────────────────────────────────────────────────────────────\n# Part D — honest held-out rank-k map\n# ──────────────────────────────────────────────────────────────────────\n\ndef ridge_fit(A, B, lam):\n    \"\"\"Centered ridge: returns (W, mu_A, mu_B) with B ~ mu_B + (A-mu_A) W.\"\"\"\n    mu_a, mu_b = A.mean(axis=0), B.mean(axis=0)\n    Ac, Bc = A - mu_a, B - mu_b\n    d = A.shape[1]\n    G = Ac.T @ Ac + lam * np.eye(d)\n    W = np.linalg.solve(G, Ac.T @ Bc)\n    return W, mu_a, mu_b\n\n\ndef heldout_r2(A_te, B_te, W, mu_a, mu_b):\n    P = mu_b + (A_te - mu_a) @ W\n    ss_res = float(np.sum((B_te - P) ** 2))\n    ss_tot = float(np.sum((B_te - B_te.mean(axis=0)) ** 2))\n    return 1.0 - ss_res / (ss_tot + 1e-12)\n\n\ndef rank_k_curve(A_tr, B_tr, A_te, B_te, lam, ks):\n    \"\"\"Held-out R^2 of rank-k truncations of the ridge map.\"\"\"\n    W, mu_a, mu_b = ridge_fit(A_tr, B_tr, lam)\n    U, s, Vt = np.linalg.svd(W, full_matrices=False)\n    curve = {}\n    for k in ks:\n        Wk = (U[:, :k] * s[:k]) @ Vt[:k, :]\n        curve[int(k)] = heldout_r2(A_te, B_te, Wk, mu_a, mu_b)\n    curve[\"full\"] = heldout_r2(A_te, B_te, W, mu_a, mu_b)\n    spec = {\n        \"sigma1_over_sigma2\": float(s[0] / (s[1] + 1e-30)),\n        \"top1_var\": float(s[0] ** 2 / (np.sum(s ** 2) + 1e-30)),\n        \"participation_ratio\": float(\n            (np.sum(s ** 2) ** 2) / (np.sum(s ** 4) + 1e-30)),\n        \"singular_top10\": [float(v) for v in s[:10]],\n    }\n    return curve, spec\n\n\ndef pick_lambda(A_tr, B_tr, A_va, B_va, grid):\n    best, best_r2 = None, -np.inf\n    for lam in grid:\n        W, mu_a, mu_b = ridge_fit(A_tr, B_tr, lam)\n        r2 = heldout_r2(A_va, B_va, W, mu_a, mu_b)\n        if r2 > best_r2:\n            best, best_r2 = lam, r2\n    return best, best_r2\n\n\n# ──────────────────────────────────────────────────────────────────────\n# Main\n# ──────────────────────────────────────────────────────────────────────\n\ndef main():\n    p = argparse.ArgumentParser()\n    p.add_argument(\"--model\", default=\"Qwen/Qwen3-8B\")\n    p.add_argument(\"--device\", default=\"mps\")\n    p.add_argument(\"--seeds\", type=int, default=8)\n    p.add_argument(\"--big-tokens\", type=int, default=12288,\n                   help=\"prose tokens for the honest fit (train+val+test)\")\n    p.add_argument(\"--smoke\", action=\"store_true\")\n    args = p.parse_args()\n\n    if args.smoke:\n        args.seeds = 2\n        args.big_tokens = 2048\n\n    t0 = time.time()\n    log(\"=\" * 72)\n    log(\"AUDIT #8 — rank-1 adjunction vs marginal/estimator nulls\")\n    log(\"register: spectral\")\n    log(f\"model={args.model} device={args.device} seeds={args.seeds} \"\n        f\"big_tokens={args.big_tokens} smoke={args.smoke}\")\n    log(\"=\" * 72)\n\n    dtype = (torch.float16 if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"])\n             else torch.float32)\n    log(f\"loading {args.model} ({dtype}) ...\")\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model, dtype=dtype, device_map=args.device,\n        attn_implementation=\"eager\")\n    model.eval()\n    tokenizer = AutoTokenizer.from_pretrained(args.model)\n    n_layers = model.config.num_hidden_layers\n    zones = {z: min(L, n_layers) for z, L in ZONES_8B.items()}\n    log(f\"n_layers={n_layers} zones={zones}\")\n\n    results = {\n        \"audit\": 8, \"register\": \"spectral\",\n        \"model\": args.model, \"zones\": zones,\n        \"seeds\": args.seeds, \"big_tokens\": args.big_tokens,\n        \"smoke\": args.smoke,\n    }\n    rng_master = np.random.default_rng(0)\n\n    # ── PART A: small-N repro of the original instrument ─────────────\n    log(\"\\nPART A — original instrument, small N (s140 regime)\")\n    small = capture_zone_residuals(model, tokenizer, SMALL_SENTENCES,\n                                   zones, args.device)\n    n_small, d = small[\"encode\"].shape\n    log(f\"  small-N tokens: {n_small}  d={d}  (N<d: {n_small < d})\")\n    A_part = {\"n_tokens\": n_small, \"d\": d, \"pairs\": {}, \"carrier\": {}}\n    for z in zones:\n        A_part[\"carrier\"][z] = carrier_stats(small[z])\n        cs = A_part[\"carrier\"][z]\n        log(f\"  carrier[{z}]: mean_norm={cs['mean_norm']:.1f} \"\n            f\"mean_energy={cs['mean_energy_share']:.3f} \"\n            f\"unc_s1/s2={cs['uncentered_sigma1_over_sigma2']:.1f}\")\n    for za, zb in ZONE_PAIRS:\n        E, D = small[za], small[zb]\n        orig = cross_corr_spectrum(E, D, center=False)\n        cent = cross_corr_spectrum(E, D, center=True)\n        r2 = lstsq_mean_r2(E, D)\n        A_part[\"pairs\"][f\"{za}->{zb}\"] = {\n            \"uncentered\": orig, \"centered\": cent, \"lstsq_r2\": r2}\n        log(f\"  {za}->{zb}: UNC s1/s2={orig['sigma1_over_sigma2']:.1f} \"\n            f\"top1={orig['top1_var']:.3f} | CEN s1/s2=\"\n            f\"{cent['sigma1_over_sigma2']:.2f} top1={cent['top1_var']:.3f} \"\n            f\"| lstsq R2={r2:.4f}\")\n    results[\"A_small_repro\"] = A_part\n\n    # ── PART B: R^2 tautology proof ──────────────────────────────────\n    log(\"\\nPART B — lstsq R^2 on data with NO map (N<d tautology proof)\")\n    B_part = {\"iid_random\": [], \"matched_marginals\": []}\n    for s in range(args.seeds):\n        rng = np.random.default_rng(1000 + s)\n        Er = rng.standard_normal((n_small, d))\n        Dr = rng.standard_normal((n_small, d))\n        B_part[\"iid_random\"].append(lstsq_mean_r2(Er, Dr))\n        Em = matched_gaussian(small[\"encode\"], rng)\n        Dm = matched_gaussian(small[\"decode\"], rng)\n        B_part[\"matched_marginals\"].append(lstsq_mean_r2(Em, Dm))\n    for kname, vals in B_part.items():\n        log(f\"  {kname}: R2 = {np.mean(vals):.4f} +/- {np.std(vals):.4f}\")\n    results[\"B_r2_tautology\"] = {\n        k: {\"mean\": float(np.mean(v)), \"std\": float(np.std(v)),\n            \"values\": [float(x) for x in v]}\n        for k, v in B_part.items()}\n\n    # ── PART C: sigma-ratio nulls at small N ─────────────────────────\n    log(\"\\nPART C — sigma1/sigma2 nulls (uncentered instrument, small N)\")\n    C_part = {}\n    for za, zb in ZONE_PAIRS:\n        E, D = small[za], small[zb]\n        real = A_part[\"pairs\"][f\"{za}->{zb}\"][\"uncentered\"][\n            \"sigma1_over_sigma2\"]\n        shuf, match = [], []\n        for s in range(args.seeds):\n            rng = np.random.default_rng(2000 + s)\n            perm = rng.permutation(D.shape[0])\n            shuf.append(cross_corr_spectrum(E, D[perm], center=False)\n                        [\"sigma1_over_sigma2\"])\n            Em = matched_gaussian(E, rng)\n            Dm = matched_gaussian(D, rng)\n            match.append(cross_corr_spectrum(Em, Dm, center=False)\n                         [\"sigma1_over_sigma2\"])\n        C_part[f\"{za}->{zb}\"] = {\n            \"real\": real,\n            \"shuffled_pairing\": {\"mean\": float(np.mean(shuf)),\n                                 \"std\": float(np.std(shuf)),\n                                 \"values\": [float(x) for x in shuf]},\n            \"matched_gaussian\": {\"mean\": float(np.mean(match)),\n                                 \"std\": float(np.std(match)),\n                                 \"values\": [float(x) for x in match]},\n            \"centered_real\": A_part[\"pairs\"][f\"{za}->{zb}\"][\"centered\"][\n                \"sigma1_over_sigma2\"],\n        }\n        log(f\"  {za}->{zb}: real={real:.1f} | shuffled=\"\n            f\"{np.mean(shuf):.1f}+/-{np.std(shuf):.1f} | matched=\"\n            f\"{np.mean(match):.1f}+/-{np.std(match):.1f} | centered_real=\"\n            f\"{C_part[f'{za}->{zb}']['centered_real']:.2f}\")\n    results[\"C_sigma_nulls_smallN\"] = C_part\n\n    # ── PART D: honest held-out rank-k map at N>d ───────────────────\n    log(\"\\nPART D — honest map (dolma prose, centered ridge, held-out rank-k)\")\n    docs = load_dolma_texts(n_docs=256, seed=0)\n    big = capture_zone_residuals(model, tokenizer, docs, zones, args.device,\n                                 max_len=512, max_tokens=args.big_tokens)\n    Nb = big[\"encode\"].shape[0]\n    log(f\"  prose tokens: {Nb} (N>d: {Nb > d})\")\n    # also repeat the uncentered instrument + nulls at large N\n    D_part = {\"n_tokens\": Nb, \"pairs\": {}}\n    n_tr = int(Nb * 0.6)\n    n_va = int(Nb * 0.15)\n    idx = rng_master.permutation(Nb)\n    tr, va, te = idx[:n_tr], idx[n_tr:n_tr + n_va], idx[n_tr + n_va:]\n    ks = [1, 2, 4, 8, 16, 32, 64, 128] if not args.smoke else [1, 2, 8, 32]\n    lam_grid = [1e0, 1e1, 1e2, 1e3, 1e4]\n    for za, zb in ZONE_PAIRS:\n        E, D = big[za], big[zb]\n        unc = cross_corr_spectrum(E, D, center=False)\n        cen = cross_corr_spectrum(E, D, center=True)\n        # shuffled-pairing null at large N (uncentered instrument)\n        rngs = np.random.default_rng(3000)\n        shuf_ratio = []\n        for s in range(args.seeds):\n            perm = rngs.permutation(D.shape[0])\n            shuf_ratio.append(cross_corr_spectrum(E, D[perm], center=False)\n                              [\"sigma1_over_sigma2\"])\n        lam, lam_r2 = pick_lambda(E[tr], D[tr], E[va], D[va], lam_grid)\n        curve, spec = rank_k_curve(E[tr], D[tr], E[te], D[te], lam, ks)\n        # estimator-leak control: fit to shuffled targets\n        perm = np.random.default_rng(4000).permutation(len(tr))\n        curve_null, _ = rank_k_curve(E[tr], D[tr][perm], E[te], D[te],\n                                     lam, [1, max(ks)])\n        D_part[\"pairs\"][f\"{za}->{zb}\"] = {\n            \"uncentered_instrument\": unc,\n            \"centered_instrument\": cen,\n            \"shuffled_pairing_ratio\": {\n                \"mean\": float(np.mean(shuf_ratio)),\n                \"std\": float(np.std(shuf_ratio))},\n            \"ridge_lambda\": lam, \"val_r2\": lam_r2,\n            \"heldout_r2_by_rank\": curve,\n            \"map_spectrum\": spec,\n            \"shuffled_target_fit\": curve_null,\n        }\n        r1 = curve[1]\n        rf = curve[\"full\"]\n        log(f\"  {za}->{zb}: UNC s1/s2={unc['sigma1_over_sigma2']:.1f} \"\n            f\"(shuf {np.mean(shuf_ratio):.1f}) | map s1/s2=\"\n            f\"{spec['sigma1_over_sigma2']:.2f} PR=\"\n            f\"{spec['participation_ratio']:.1f}\")\n        log(f\"      heldout R2: k=1 {r1:.4f}  full {rf:.4f}  \"\n            f\"ratio {r1 / (rf + 1e-12):.3f} | leak-control full \"\n            f\"{curve_null['full']:.4f}\")\n    results[\"D_honest_map\"] = D_part\n\n    # ── Save ─────────────────────────────────────────────────────────\n    out_dir = _PROJECT_ROOT / \"results\" / \"adjunction-rank-null\"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    tag = args.model.replace(\"/\", \"_\") + (\".smoke\" if args.smoke else \"\")\n    out_path = out_dir / f\"{tag}.json\"\n    results[\"elapsed_s\"] = time.time() - t0\n    with open(out_path, \"w\") as f:\n        json.dump(results, f, indent=2)\n    log(f\"\\nsaved -> {out_path}  ({results['elapsed_s']:.0f}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py
```

### Thinking

 I need to re-read the file to check for any mutations from hooks, then run a smoke test. The 8B model takes a couple minutes to load, so I'll run that in the background using tmux to keep it separate from the quick smoke test itself, which should have a generous timeout. I'll set up a tmux session at main:1 with tee logging to capture output.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "head -5 /Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py && python3 -c \"import ast; ast.parse(open('/Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py').read()); print('syntax OK')\""
}
```

**Summary:** $ head -5 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 0
Stdout:
#!/usr/bin/env python3
"""Audit #8 — rank-1 adjunction (sigma1/sigma2 = 128:1 cross-zone): real map
structure, or marginal/estimator artifact?

The claim (s140, Qwen3-32B; `direct-delta-adjunction.md`,
syntax OK
```

### Thinking

 There's a numerical concern in Part D with the large-N case—the SVD computations for the centered data are manageable since they only apply to smaller N values. The cross-correlation spectrum calculation does require a full 4096×4096 SVD per call, and with multiple pairs (2 uncorrelated/centered plus 8 shuffled variants) and ridge regression work, we're looking at around 10 SVDs across 3 pairs taking roughly 10-20 seconds each, which totals a few minutes overall. The ridge fitting then solves another 4096×4096 system for each regularization parameter.

Memory-wise, the large arrays at 12288×4096 in float32 format consume about 200MB per zone, and with 4 zones that's 800MB total—well within acceptable limits. Ready to launch the smoke test in tmux.

## Assistant

Syntax OK. Launching the smoke test in tmux per `λ runtime`:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux has-session -t main 2>/dev/null && echo \"session main exists\" ; tmux list-windows -t main 2>/dev/null | head"
}
```

**Summary:** $ tmux has-session -t main 2>/dev/nul...

**Output:**
```
Exit code: 0
Stdout:
session main exists
1: local* (1 panes) [120x24] [layout b704,120x24,0,0,7] @7 (active)
2: local- (1 panes) [120x24] [layout b705,120x24,0,0,8] @8
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/results/adjunction-rank-null && tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/adjunction_rank_null.py --smoke 2>&1 | tee results/adjunction-rank-null/smoke.log\" Enter && echo launched"
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
launched
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 45 && tmux capture-pane -p -t main:1 | tail -15",
  "timeout": 60000
}
```

**Summary:** $ sleep 45 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
small-N tokens: 121  d=4096  (N<d: True)
  carrier[encode]: mean_norm=10.0 mean_energy=0.498 unc_s1/s2=3.1
  carrier[compress]: mean_norm=58.4 mean_energy=0.382 unc_s1/s2=1.6
  carrier[decode]: mean_norm=475.2 mean_energy=0.604 unc_s1/s2=5.2
  carrier[final]: mean_norm=1218.9 mean_energy=0.813 unc_s1/s2=7.9
  encode->compress: UNC s1/s2=6.0 top1=0.960 | CEN s1/s2=3.93 top1=0.761 | lstsq R2=1.0000
  compress->decode: UNC s1/s2=11.7 top1=0.981 | CEN s1/s2=2.21 top1=0.452 | lstsq R2=1.0000
  encode->decode: UNC s1/s2=20.9 top1=0.992 | CEN s1/s2=2.37 top1=0.458 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
```

### Thinking

 The R² tautology with iid random data confirms that approach is a dead end. Looking at the 8B results, the uncentered ratio between encode and decode is around 20.9, which drops to 2.37 when centered—the carrier diagnostic shows mean energy hovering between 0.4 and 0.8. Now examining the least squares R² values...

The lstsq R² is hitting 1.0000 on the actual data, which reproduces exactly. I should wait for Parts C and D to complete before drawing conclusions. The smoke test uses big_tokens=2048, which is below the d=4096 dimension, so the N<d condition is false for smoke—that's expected since the full run will use 12288. Ridge regression still works in the N<d regime with regularization, so I'll let the smoke test finish since it runs quickly.

### Thinking

I've confirmed the R² calculation works perfectly on random noise and reproduced the expected result for the least squares fit. Now I'm ready to move on to parts C and D.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 90 && tmux capture-pane -p -t main:1 | tail -25",
  "timeout": 120000
}
```

**Summary:** $ sleep 90 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
n_layers=36 zones={'encode': 1, 'compress': 18, 'decode': 31, 'final': 35}

PART A — original instrument, small N (s140 regime)
  small-N tokens: 121  d=4096  (N<d: True)
  carrier[encode]: mean_norm=10.0 mean_energy=0.498 unc_s1/s2=3.1
  carrier[compress]: mean_norm=58.4 mean_energy=0.382 unc_s1/s2=1.6
  carrier[decode]: mean_norm=475.2 mean_energy=0.604 unc_s1/s2=5.2
  carrier[final]: mean_norm=1218.9 mean_energy=0.813 unc_s1/s2=7.9
  encode->compress: UNC s1/s2=6.0 top1=0.960 | CEN s1/s2=3.93 top1=0.761 | lstsq R2=1.0000
  compress->decode: UNC s1/s2=11.7 top1=0.981 | CEN s1/s2=2.21 top1=0.452 | lstsq R2=1.0000
  encode->decode: UNC s1/s2=20.9 top1=0.992 | CEN s1/s2=2.37 top1=0.458 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
  encode->compress: real=6.0 | shuffled=16.9+/-0.2 | matched=16.8+/-2.2 | centered_real=3.93
  compress->decode: real=11.7 | shuffled=23.1+/-1.2 | matched=17.9+/-1.8 | centered_real=2.21
  encode->decode: real=20.9 | shuffled=39.2+/-1.5 | matched=31.6+/-3.9 | centered_real=2.37

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
  prose tokens: 2048 (N>d: False)
```

### Thinking

 The shuffled-pairing null model reveals something crucial: when I destroy the token correspondence, the rank-1 dominance actually *increases* (39.2 vs 20.9), meaning the carrier means are driving the effect entirely. The real map structure is actually *suppressing* this apparent rank-1 dominance compared to the no-map baseline.

Part D is still computing—ridge regression on 2048 tokens with multiple SVD passes running. I'll wait for it to finish since this is a quick job that should wrap up in a couple minutes.

### Thinking

The shuffled null is more rank-1-dominated than the real data, which is striking. Now I'll check Part D.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 120 && tmux capture-pane -p -t main:1 | tail -14",
  "timeout": 150000
}
```

**Summary:** $ sleep 120 && tmux capture-pane -p -...

**Output:**
```
Exit code: 0
Stdout:
prose tokens: 2048 (N>d: False)
  encode->compress: UNC s1/s2=26.1 (shuf 121.2) | map s1/s2=1.26 PR=110.5
      heldout R2: k=1 0.0309  full 0.2809  ratio 0.110 | leak-control full -0.0995
  compress->decode: UNC s1/s2=16.0 (shuf 150.6) | map s1/s2=1.26 PR=259.0
      heldout R2: k=1 0.0417  full 0.4698  ratio 0.089 | leak-control full -0.3107
  encode->decode: UNC s1/s2=41.7 (shuf 121.7) | map s1/s2=1.28 PR=61.7
      heldout R2: k=1 0.0480  full 0.2511  ratio 0.191 | leak-control full -0.1034

saved -> /Users/mwhitford/src/verbum/results/adjunction-rank-null/Qwen_Qwen3-8B.smoke.json  (283s)
uv run python scripts/experiments/adjunction_rank_null.py --smoke 2>&1  342.13s user 60.89s system 140% cpu 4:46.48 tota
l
tee results/adjunction-rank-null/smoke.log  0.00s user 0.01s system 0% cpu 4:46.48 total
[26-06-09][12:17:49][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

 The smoke test completed in 283 seconds with all four components producing coherent results. Part A shows the 8B model achieving perfect R² on real data with uncentered ratios between 6-21, Part B confirms the tautology with iid random data also hitting R²=1.0, Part C demonstrates that shuffled and matched nulls meet or exceed the real ratio while centering reduces it to 2-4, and Part D's honest spectrum mapping on N=2048 shows singular value ratios around 1.26-1.28.

The key finding is that shuffled data actually produces *more* rank-1 dominance than real data — the uncentered ratio jumps to 121-151 versus the real 16-42 at large N. This happens because shuffling destroys the correlated centered components, leaving only the mean⊗mean term plus noise, which is inherently rank-1. The real data's σ₁/σ₂ includes genuine multi-dimensional cross-zone correlations that add off-rank-1 mass, so rank-1 dominance is actually anti-evidence of map structure under this estimator. The held-out rank-1 model captures only 9-19% of the full map's predictable variance, and leak control is negative (good).

The harness is validated and ready for the full run with 8 seeds and 12288 tokens, which should take around 8-15 minutes total. I'm committing the code now with a message about the adjunction rank null audit and spectral register approach, then launching the full run in tmux.

## Assistant

Smoke run complete (283s) — harness validated end-to-end, and every part already shows signal. Committing the harness, then launching the full run:

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/adjunction_rank_null.py && git commit -m \"$(cat <<'EOF'\n💡 audit #8 harness — adjunction rank null (spectral: cross-zone SVD vs marginal nulls + held-out rank-k)\n\n- reproduces the s140 instrument exactly (uncentered cross-corr SVD + lstsq R2 at N<d)\n- B: R2 tautology proof (lstsq on mapless random data at N<d)\n- C: sigma1/sigma2 vs row-shuffled pairing + matched-Gaussian nulls + centering\n- D: honest centered ridge at N>d (dolma), held-out R2 of rank-k truncations,\n  estimator-leak control (shuffled-target fit)\n- smoke (8B): random noise gives R2=1.0000 (tautology confirmed); shuffled\n  null MORE rank-1 than real (121 vs 42) — ratio is the carrier mean\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "audit 8 harness"
}
```

**Summary:** Git commit: audit 8 harness

**Output:**
```
Exit code: 0
Stdout:
[main 7217b54] 💡 audit #8 harness — adjunction rank null (spectral: cross-zone SVD vs marginal nulls + held-out rank-k)
 1 file changed, 455 insertions(+)
 create mode 100644 scripts/experiments/adjunction_rank_null.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/adjunction_rank_null.py --model Qwen/Qwen3-8B --device mps 2>&1 | tee results/adjunction-rank-null/run.log\" Enter && echo launched"
}
```

**Summary:** $ tmux send-keys -t main:1 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
launched
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 60 && tmux capture-pane -p -t main:1 | tail -8",
  "timeout": 80000
}
```

**Summary:** $ sleep 60 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
encode->decode: UNC s1/s2=20.9 top1=0.992 | CEN s1/s2=2.37 top1=0.458 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
```

### Thinking

 The full run is now executing and should complete in about 10-15 minutes with the SVD computations across 8 seeds. I've got an async checkpoint confirming it's running, so I could draft the registry structure while waiting, but I'll hold off on finalizing anything until the results come in. I should also note that the s140 claim was specifically for Qwen3-32B.

Now I'm wondering whether we should run the 32B model as well — the original experiment used 32B with 64 layers and d=5120. If it's available on olga and cached locally, running Parts A and C on 32B with the original layer zones could give us a stronger refutation of the "128:1" claim. Let me check what's in the HF cache.

### Thinking

The full run is launched and verified running with identical signals across 8 seeds. I'm now running a small-N verification on Qwen3-32B to check the original claim's 128:1 ratio while the async job completes.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls ~/.cache/huggingface/hub 2>/dev/null | grep -i qwen; du -sh ~/.cache/huggingface/hub/models--Qwen--Qwen3-32B 2>/dev/null"
}
```

**Summary:** $ ls ~/.cache/huggingface/hub 2>/dev/...

**Output:**
```
Exit code: 0
Stdout:
models--mlx-community--Qwen3-Embedding-4B-4bit-DWQ
models--Qwen--Qwen2.5-0.5B
models--Qwen--Qwen3-0.6B
models--Qwen--Qwen3-14B
models--Qwen--Qwen3-235B-A22B
models--Qwen--Qwen3-30B-A3B
models--Qwen--Qwen3-32B
models--Qwen--Qwen3-4B
models--Qwen--Qwen3-8B
models--Qwen--Qwen3.5-35B-A3B
models--Qwen--Qwen3.6-27B
models--Qwen--Qwen3.6-35B-A3B
models--unsloth--Qwen3-Coder-480B-A35B-Instruct-GGUF
 61G	/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-32B
```

### Thinking

 I need to make the zone configuration model-aware since Qwen3-32B has different layer counts than the hardcoded 64-layer reference. I'll add a ZONES_32B dictionary and select the appropriate zones based on the model's actual layer count, scaling proportionally if needed for other model sizes.

After the 8B run finishes, I can launch the 32B run concurrently in main:2 since the unified memory can handle both (8B fp16 ~16G + 32B fp16 ~65G fits in 480G). The script edits are safe to make now since the 8B job is already loaded in Python memory.

## Assistant

Qwen3-32B is cached — the literal original model. Let me make zones model-aware, then launch 32B concurrently in main:2:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py",
  "original_content": "# Zone layers. 32B (64 layers) used ENCODE=L2, COMPRESS=L32, DECODE=L56,\n# FINAL=L63. Proportional map to Qwen3-8B's 36 layers:\nZONES_8B = {\"encode\": 1, \"compress\": 18, \"decode\": 31, \"final\": 35}",
  "new_content": "# Zone layers. s140 (Qwen3-32B, 64 layers) used ENCODE=L2, COMPRESS=L32,\n# DECODE=L56, FINAL=L63. On 64-layer models we use those literal zones;\n# otherwise scale proportionally.\nZONES_REF = {\"encode\": 2, \"compress\": 32, \"decode\": 56, \"final\": 63}\n\n\ndef zones_for(n_layers: int) -> dict:\n    if n_layers == 64:\n        return dict(ZONES_REF)\n    return {z: max(1, round(L / 64 * n_layers)) for z, L in ZONES_REF.items()}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py",
  "original_content": "    n_layers = model.config.num_hidden_layers\n    zones = {z: min(L, n_layers) for z, L in ZONES_8B.items()}",
  "new_content": "    n_layers = model.config.num_hidden_layers\n    zones = zones_for(n_layers)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py.
```

### Thinking

 I'm verifying the sync rule calculations for zone 36 across encode, compress, and decode operations, checking that the rounding behavior matches expectations—the decode step shows a slight discrepancy from the smoke test (32 vs 31), but it's negligible since the full 8B run is already using the older version.

To keep results comparable with the in-flight run, I'll switch to using integer truncation instead of rounding, which gives me the exact values the 8B model is currently using: encode=1, compress=18, decode=31, final=35. This ensures consistency across runs.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py",
  "original_content": "    return {z: max(1, round(L / 64 * n_layers)) for z, L in ZONES_REF.items()}",
  "new_content": "    return {z: max(1, int(L / 64 * n_layers)) for z, L in ZONES_REF.items()}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/adjunction_rank_null.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport ast,sys\nsrc=open('scripts/experiments/adjunction_rank_null.py').read()\nast.parse(src)\nns={}\nexec(compile(ast.parse(src.split('def zones_for')[0]+'def zones_for'+src.split('def zones_for')[1].split('def log')[0]),'<s>','exec'),ns)\nprint('36:',ns['zones_for'](36)); print('64:',ns['zones_for'](64))\n\""
}
```

**Summary:** $ python3 -c " import ast,sys src=ope...

**Output:**
```
Exit code: 1
Stderr:
Traceback (most recent call last):
  File "<string>", line 6, in <module>
    exec(compile(ast.parse(src.split('def zones_for')[0]+'def zones_for'+src.split('def zones_for')[1].split('def log')[0]),'<s>','exec'),ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<s>", line 73, in <module>
ModuleNotFoundError: No module named 'torch'
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\ndef zones_for(n):\n    ZONES_REF={'encode':2,'compress':32,'decode':56,'final':63}\n    if n==64: return dict(ZONES_REF)\n    return {z: max(1,int(L/64*n)) for z,L in ZONES_REF.items()}\nprint('36:',zones_for(36)); print('64:',zones_for(64))\n\" && python3 -c \"import ast; ast.parse(open('scripts/experiments/adjunction_rank_null.py').read()); print('syntax OK')\""
}
```

**Summary:** $ python3 -c " def zones_for(n):     ...

**Output:**
```
Exit code: 0
Stdout:
36: {'encode': 1, 'compress': 18, 'decode': 31, 'final': 35}
64: {'encode': 2, 'compress': 32, 'decode': 56, 'final': 63}
syntax OK
```

### Thinking

 I've verified the zone mappings match the in-flight 8B run, and I'm launching the 32B model in fp16 precision which will load around 65GB from disk—this should take a few minutes to initialize and then run forwards more slowly. I'm setting up a full run with seeds 8 and 12288 big tokens, expecting the whole process to take roughly 30-60 minutes on MPS, so I'm starting it now.

### Thinking

I've verified the zones match the in-flight 8B run and confirmed the literal s140 zones for the 64-zone case. Now I'm launching the 32B model on main:2.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:2 \"cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/adjunction_rank_null.py --model Qwen/Qwen3-32B --device mps 2>&1 | tee results/adjunction-rank-null/run32b.log\" Enter && echo launched-32b; sleep 20; tmux capture-pane -p -t main:2 | tail -4; echo === 8B ===; tmux capture-pane -p -t main:1 | tail -4",
  "timeout": 40000
}
```

**Summary:** $ tmux send-keys -t main:2 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
launched-32b
model=Qwen/Qwen3-32B device=mps seeds=8 big_tokens=12288 smoke=False
========================================================================
loading Qwen/Qwen3-32B (torch.float16) ...
Loading weights:  16%|█▌        | 114/707 [00:16<01:04,  9.25it/s]
=== 8B ===
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
```

### Thinking

 Both jobs are running now—Part C is handling the smaller SVD operations while the cross-correlation spectrum calculations are working through a larger batch of decompositions that'll take a few minutes. I've verified they're both executing properly and I'm waiting for them to complete rather than continuing to poll.

### Thinking

Both jobs are running. I'm committing the model-aware zones edit now.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/adjunction_rank_null.py && git commit -m \"$(cat <<'EOF'\n🔄 audit #8 harness — model-aware zones (64-layer models use literal s140 zones L2/L32/L56/L63)\n\n- enables running the control on Qwen3-32B, the model the 128:1 claim was measured on\n- 36-layer proportional zones unchanged (L1/L18/L31/L35)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "model-aware zones"
}
```

**Summary:** Git commit: model-aware zones

**Output:**
```
Exit code: 0
Stdout:
[main 3a97476] 🔄 audit #8 harness — model-aware zones (64-layer models use literal s140 zones L2/L32/L56/L63)
 1 file changed, 11 insertions(+), 4 deletions(-)
```

## Assistant

**ASYNC: job=8B-full (tmux main:1, in Part C) + job=32B-full (tmux main:2, loading weights) both verified running. Waiting for signal.**

While they run, the smoke evidence already sketches the verdict shape (to be confirmed by the full runs):

| Leg of claim | Smoke evidence | Reading |
|---|---|---|
| **R² = 1.000 all zone pairs** | iid random noise → R² = 1.0000 ± 0.0000 at N<d | tautology — lstsq with more unknowns than equations interpolates *anything*; the leg carries zero information |
| **σ₁/σ₂ rank-1 dominance (uncentered)** | real 20.9–41.7 vs **shuffled-pairing null 39.2–151** | the no-map null is *more* rank-1 than the real data — the dominance is the carrier mean (mean⊗mean term), and genuine cross-zone correlation actually *adds* off-rank-1 mass |
| **survives centering?** | centered σ₁/σ₂ collapses to 2.2–3.9 | the "128:1-style" ratio is the uncentered artifact |
| **"1D curve" (honest map)** | ridge map σ₁/σ₂ ≈ 1.26, participation ratio 62–259; held-out rank-1 captures only 9–19% of the full map's predictable variance; leak control ≈ 0 | the cross-zone map is high-rank; rank-1 is nowhere near sufficient |

If the full 8B + 32B runs confirm this, audit #8 resolves as: **❌ rank-1 adjunction REFUTED (both legs are estimator artifacts — underdetermined lstsq + uncentered carrier mean)**, with the interesting twist that this time the substrate that survives is *different from the claim entirely*: what's real is the carrier/mean dominance of the residual stream (s185's finding, independently confirmed by the carrier diagnostics) — not any 1D structure of the *map*. It also retro-explains s201's functional result: the direct-delta rank sweep never showed rank-1 sufficiency (rank-32 still improving, v3b's trained correction beating all analytical ranks).

I'll report back when the runs signal completion.

## User

job is done


### Thinking

 I should check what both runs produced to compare their outputs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -45 /Users/mwhitford/src/verbum/results/adjunction-rank-null/run.log"
}
```

**Summary:** $ tail -45 /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
========================================================================
AUDIT #8 — rank-1 adjunction vs marginal/estimator nulls
register: spectral
model=Qwen/Qwen3-8B device=mps seeds=8 big_tokens=12288 smoke=False
========================================================================
loading Qwen/Qwen3-8B (torch.float16) ...
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]Loading weights:   0%|          | 1/399 [00:00<03:04,  2.16it/s]Loading weights:   9%|▉         | 36/399 [00:00<00:04, 83.92it/s]Loading weights:  17%|█▋        | 67/399 [00:00<00:02, 140.12it/s]Loading weights:  25%|██▌       | 100/399 [00:00<00:01, 189.07it/s]Loading weights:  34%|███▎      | 134/399 [00:00<00:01, 229.23it/s]Loading weights:  42%|████▏     | 169/399 [00:00<00:00, 261.73it/s]Loading weights:  51%|█████     | 202/399 [00:01<00:00, 277.31it/s]Loading weights:  59%|█████▉    | 235/399 [00:01<00:00, 289.01it/s]Loading weights:  67%|██████▋   | 268/399 [00:01<00:00, 297.86it/s]Loading weights:  76%|███████▌  | 303/399 [00:01<00:00, 312.71it/s]Loading weights:  84%|████████▍ | 336/399 [00:01<00:00, 316.55it/s]Loading weights:  92%|█████████▏| 369/399 [00:01<00:00, 315.37it/s]Loading weights: 100%|██████████| 399/399 [00:01<00:00, 239.99it/s]
n_layers=36 zones={'encode': 1, 'compress': 18, 'decode': 31, 'final': 35}

PART A — original instrument, small N (s140 regime)
  small-N tokens: 121  d=4096  (N<d: True)
  carrier[encode]: mean_norm=10.0 mean_energy=0.498 unc_s1/s2=3.1
  carrier[compress]: mean_norm=58.4 mean_energy=0.382 unc_s1/s2=1.6
  carrier[decode]: mean_norm=475.2 mean_energy=0.604 unc_s1/s2=5.2
  carrier[final]: mean_norm=1218.9 mean_energy=0.813 unc_s1/s2=7.9
  encode->compress: UNC s1/s2=6.0 top1=0.960 | CEN s1/s2=3.93 top1=0.761 | lstsq R2=1.0000
  compress->decode: UNC s1/s2=11.7 top1=0.981 | CEN s1/s2=2.21 top1=0.452 | lstsq R2=1.0000
  encode->decode: UNC s1/s2=20.9 top1=0.992 | CEN s1/s2=2.37 top1=0.458 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
  encode->compress: real=6.0 | shuffled=16.3+/-2.1 | matched=17.1+/-2.9 | centered_real=3.93
  compress->decode: real=11.7 | shuffled=21.5+/-2.0 | matched=20.0+/-2.0 | centered_real=2.21
  encode->decode: real=20.9 | shuffled=37.5+/-1.9 | matched=34.5+/-4.2 | centered_real=2.37

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
  prose tokens: 12288 (N>d: True)
  encode->compress: UNC s1/s2=23.4 (shuf 24.6) | map s1/s2=10.39 PR=1.6
      heldout R2: k=1 -0.0243  full -0.0041  ratio 5.912 | leak-control full -0.0116
  compress->decode: UNC s1/s2=4.4 (shuf 32.0) | map s1/s2=1.70 PR=292.1
      heldout R2: k=1 0.1108  full 0.5788  ratio 0.191 | leak-control full -0.0515
  encode->decode: UNC s1/s2=54.0 (shuf 247.6) | map s1/s2=2.40 PR=35.5
      heldout R2: k=1 -0.0250  full 0.1805  ratio -0.138 | leak-control full -0.0800

saved -> /Users/mwhitford/src/verbum/results/adjunction-rank-null/Qwen_Qwen3-8B.json  (1077s)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -50 /Users/mwhitford/src/verbum/results/adjunction-rank-null/run32b.log"
}
```

**Summary:** $ tail -50 /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
========================================================================
AUDIT #8 — rank-1 adjunction vs marginal/estimator nulls
register: spectral
model=Qwen/Qwen3-32B device=mps seeds=8 big_tokens=12288 smoke=False
========================================================================
loading Qwen/Qwen3-32B (torch.float16) ...
Loading weights:   0%|          | 0/707 [00:00<?, ?it/s]Loading weights:   0%|          | 1/707 [00:03<43:35,  3.70s/it]Loading weights:   1%|          | 6/707 [00:04<07:06,  1.64it/s]Loading weights:   2%|▏         | 15/707 [00:05<02:56,  3.93it/s]Loading weights:   2%|▏         | 16/707 [00:05<02:56,  3.92it/s]Loading weights:   4%|▎         | 26/707 [00:06<01:34,  7.21it/s]Loading weights:   4%|▍         | 27/707 [00:06<01:35,  7.15it/s]Loading weights:   4%|▍         | 28/707 [00:06<01:43,  6.58it/s]Loading weights:   5%|▌         | 37/707 [00:07<01:32,  7.25it/s]Loading weights:   7%|▋         | 48/707 [00:09<01:31,  7.23it/s]Loading weights:   8%|▊         | 59/707 [00:10<01:22,  7.81it/s]Loading weights:   8%|▊         | 60/707 [00:10<01:25,  7.53it/s]Loading weights:  10%|▉         | 70/707 [00:11<01:02, 10.27it/s]Loading weights:  10%|█         | 72/707 [00:11<01:09,  9.11it/s]Loading weights:  11%|█▏        | 81/707 [00:12<01:11,  8.72it/s]Loading weights:  12%|█▏        | 82/707 [00:12<01:12,  8.67it/s]Loading weights:  13%|█▎        | 92/707 [00:14<01:16,  8.03it/s]Loading weights:  15%|█▍        | 103/707 [00:15<01:13,  8.18it/s]Loading weights:  16%|█▌        | 114/707 [00:16<01:04,  9.25it/s]Loading weights:  16%|█▋        | 116/707 [00:16<01:03,  9.33it/s]Loading weights:  18%|█▊        | 125/707 [00:17<01:07,  8.60it/s]Loading weights:  19%|█▉        | 136/707 [00:19<01:10,  8.10it/s]Loading weights:  21%|██        | 147/707 [00:20<01:04,  8.63it/s]Loading weights:  21%|██        | 148/707 [00:20<01:07,  8.26it/s]Loading weights:  22%|██▏       | 158/707 [00:21<00:48, 11.22it/s]Loading weights:  23%|██▎       | 160/707 [00:21<00:56,  9.71it/s]Loading weights:  24%|██▍       | 169/707 [00:22<00:58,  9.23it/s]Loading weights:  24%|██▍       | 170/707 [00:22<01:01,  8.72it/s]Loading weights:  25%|██▌       | 180/707 [00:24<01:03,  8.36it/s]Loading weights:  26%|██▌       | 182/707 [00:24<01:02,  8.42it/s]Loading weights:  27%|██▋       | 191/707 [00:25<01:04,  8.01it/s]Loading weights:  29%|██▊       | 202/707 [00:26<00:54,  9.34it/s]Loading weights:  30%|███       | 213/707 [00:27<00:54,  9.14it/s]Loading weights:  30%|███       | 215/707 [00:27<00:54,  9.09it/s]Loading weights:  32%|███▏      | 224/707 [00:29<00:58,  8.23it/s]Loading weights:  33%|███▎      | 235/707 [00:30<00:57,  8.21it/s]Loading weights:  35%|███▍      | 246/707 [00:31<00:44, 10.37it/s]Loading weights:  35%|███▌      | 248/707 [00:31<00:47,  9.73it/s]Loading weights:  36%|███▋      | 257/707 [00:32<00:50,  8.98it/s]Loading weights:  36%|███▋      | 258/707 [00:32<00:49,  9.02it/s]Loading weights:  38%|███▊      | 268/707 [00:34<00:52,  8.44it/s]Loading weights:  38%|███▊      | 270/707 [00:34<00:48,  8.94it/s]Loading weights:  39%|███▉      | 279/707 [00:35<00:52,  8.15it/s]Loading weights:  41%|████      | 290/707 [00:36<00:44,  9.36it/s]Loading weights:  43%|████▎     | 301/707 [00:37<00:43,  9.35it/s]Loading weights:  43%|████▎     | 303/707 [00:37<00:43,  9.27it/s]Loading weights:  44%|████▍     | 312/707 [00:38<00:45,  8.64it/s]Loading weights:  46%|████▌     | 323/707 [00:40<00:46,  8.24it/s]Loading weights:  47%|████▋     | 334/707 [00:40<00:35, 10.44it/s]Loading weights:  48%|████▊     | 336/707 [00:41<00:37,  9.97it/s]Loading weights:  49%|████▉     | 345/707 [00:42<00:41,  8.80it/s]Loading weights:  50%|█████     | 356/707 [00:43<00:43,  7.98it/s]Loading weights:  52%|█████▏    | 367/707 [00:45<00:40,  8.34it/s]Loading weights:  52%|█████▏    | 368/707 [00:45<00:41,  8.20it/s]Loading weights:  53%|█████▎    | 378/707 [00:45<00:31, 10.37it/s]Loading weights:  54%|█████▎    | 380/707 [00:46<00:34,  9.50it/s]Loading weights:  55%|█████▌    | 389/707 [00:47<00:35,  8.96it/s]Loading weights:  57%|█████▋    | 400/707 [00:48<00:36,  8.47it/s]Loading weights:  58%|█████▊    | 411/707 [00:49<00:33,  8.74it/s]Loading weights:  58%|█████▊    | 412/707 [00:50<00:34,  8.47it/s]Loading weights:  60%|█████▉    | 422/707 [00:50<00:25, 11.19it/s]Loading weights:  60%|█████▉    | 424/707 [00:50<00:27, 10.36it/s]Loading weights:  61%|██████    | 433/707 [00:52<00:29,  9.27it/s]Loading weights:  61%|██████▏   | 434/707 [00:52<00:29,  9.21it/s]Loading weights:  63%|██████▎   | 444/707 [00:53<00:31,  8.37it/s]Loading weights:  64%|██████▍   | 455/707 [00:54<00:30,  8.37it/s]Loading weights:  66%|██████▌   | 466/707 [00:55<00:25,  9.60it/s]Loading weights:  66%|██████▌   | 468/707 [00:55<00:24,  9.60it/s]Loading weights:  67%|██████▋   | 477/707 [00:57<00:25,  8.87it/s]Loading weights:  69%|██████▉   | 488/707 [00:58<00:26,  8.25it/s]Loading weights:  71%|███████   | 499/707 [00:59<00:24,  8.38it/s]Loading weights:  71%|███████   | 500/707 [00:59<00:25,  8.23it/s]Loading weights:  72%|███████▏  | 510/707 [01:00<00:18, 10.88it/s]Loading weights:  72%|███████▏  | 512/707 [01:00<00:19,  9.87it/s]Loading weights:  74%|███████▎  | 521/707 [01:01<00:20,  8.90it/s]Loading weights:  75%|███████▌  | 532/707 [01:03<00:21,  8.28it/s]Loading weights:  77%|███████▋  | 543/707 [01:04<00:19,  8.38it/s]Loading weights:  77%|███████▋  | 544/707 [01:04<00:19,  8.20it/s]Loading weights:  78%|███████▊  | 554/707 [01:05<00:13, 11.10it/s]Loading weights:  79%|███████▊  | 556/707 [01:05<00:14, 10.09it/s]Loading weights:  80%|███████▉  | 565/707 [01:06<00:15,  9.12it/s]Loading weights:  80%|████████  | 566/707 [01:06<00:15,  8.91it/s]Loading weights:  81%|████████▏ | 576/707 [01:08<00:16,  8.18it/s]Loading weights:  82%|████████▏ | 578/707 [01:08<00:14,  8.74it/s]Loading weights:  83%|████████▎ | 587/707 [01:09<00:14,  8.11it/s]Loading weights:  85%|████████▍ | 598/707 [01:10<00:12,  9.04it/s]Loading weights:  86%|████████▌ | 609/707 [01:11<00:10,  9.18it/s]Loading weights:  86%|████████▋ | 611/707 [01:12<00:10,  8.89it/s]Loading weights:  88%|████████▊ | 620/707 [01:13<00:10,  8.60it/s]Loading weights:  89%|████████▉ | 631/707 [01:14<00:09,  8.41it/s]Loading weights:  91%|█████████ | 642/707 [01:15<00:06, 10.49it/s]Loading weights:  91%|█████████ | 644/707 [01:15<00:06, 10.18it/s]Loading weights:  92%|█████████▏| 653/707 [01:16<00:06,  8.88it/s]Loading weights:  93%|█████████▎| 655/707 [01:16<00:05,  9.37it/s]Loading weights:  94%|█████████▍| 664/707 [01:18<00:05,  8.46it/s]Loading weights:  95%|█████████▌| 675/707 [01:19<00:03,  8.25it/s]Loading weights:  97%|█████████▋| 686/707 [01:20<00:02, 10.21it/s]Loading weights:  97%|█████████▋| 688/707 [01:20<00:01,  9.68it/s]Loading weights:  99%|█████████▊| 697/707 [01:21<00:01,  9.12it/s]Loading weights: 100%|██████████| 707/707 [01:21<00:00,  8.68it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
n_layers=64 zones={'encode': 2, 'compress': 32, 'decode': 56, 'final': 63}

PART A — original instrument, small N (s140 regime)
  small-N tokens: 121  d=5120  (N<d: True)
  carrier[encode]: mean_norm=35.9 mean_energy=0.542 unc_s1/s2=3.3
  carrier[compress]: mean_norm=98.3 mean_energy=0.189 unc_s1/s2=1.8
  carrier[decode]: mean_norm=472.1 mean_energy=0.378 unc_s1/s2=3.4
  carrier[final]: mean_norm=1687.6 mean_energy=0.606 unc_s1/s2=4.8
  encode->compress: UNC s1/s2=7.5 top1=0.950 | CEN s1/s2=1.82 top1=0.426 | lstsq R2=1.0000
  compress->decode: UNC s1/s2=7.1 top1=0.910 | CEN s1/s2=1.46 top1=0.253 | lstsq R2=1.0000
  encode->decode: UNC s1/s2=13.8 top1=0.983 | CEN s1/s2=2.15 top1=0.426 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
  encode->compress: real=7.5 | shuffled=14.9+/-0.9 | matched=14.4+/-0.9 | centered_real=1.82
  compress->decode: real=7.1 | shuffled=14.1+/-1.1 | matched=12.3+/-1.0 | centered_real=1.46
  encode->decode: real=13.8 | shuffled=24.8+/-1.0 | matched=23.8+/-2.5 | centered_real=2.15

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
```

### Thinking

 The 8B model finished its full run in about 18 minutes, while the 32B is still working through Part D. I should verify whether the 32B output was saved to JSON.

## Assistant

8B is complete; checking whether 32B's Part D finished:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/adjunction-rank-null/; echo ===; tail -12 /Users/mwhitford/src/verbum/results/adjunction-rank-null/run32b.log; echo ===; tmux capture-pane -p -t main:2 | tail -6"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 104
drwxr-xr-x@   7 mwhitford  staff    224 Jun  9 12:36 .
drwxr-xr-x@ 428 mwhitford  staff  13696 Jun  9 12:13 ..
-rw-r--r--@   1 mwhitford  staff  14727 Jun  9 12:36 Qwen_Qwen3-8B.json
-rw-r--r--@   1 mwhitford  staff  13048 Jun  9 12:17 Qwen_Qwen3-8B.smoke.json
-rw-r--r--@   1 mwhitford  staff   3418 Jun  9 12:36 run.log
-rw-r--r--@   1 mwhitford  staff   9458 Jun  9 12:39 run32b.log
-rw-r--r--@   1 mwhitford  staff   3421 Jun  9 12:17 smoke.log
===
  encode->decode: UNC s1/s2=13.8 top1=0.983 | CEN s1/s2=2.15 top1=0.426 | lstsq R2=1.0000

PART B — lstsq R^2 on data with NO map (N<d tautology proof)
  iid_random: R2 = 1.0000 +/- 0.0000
  matched_marginals: R2 = 1.0000 +/- 0.0000

PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
  encode->compress: real=7.5 | shuffled=14.9+/-0.9 | matched=14.4+/-0.9 | centered_real=1.82
  compress->decode: real=7.1 | shuffled=14.1+/-1.1 | matched=12.3+/-1.0 | centered_real=1.46
  encode->decode: real=13.8 | shuffled=24.8+/-1.0 | matched=23.8+/-2.5 | centered_real=2.15

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
===
  encode->compress: real=7.5 | shuffled=14.9+/-0.9 | matched=14.4+/-0.9 | centered_real=1.82
  compress->decode: real=7.1 | shuffled=14.1+/-1.1 | matched=12.3+/-1.0 | centered_real=1.46
  encode->decode: real=13.8 | shuffled=24.8+/-1.0 | matched=23.8+/-2.5 | centered_real=2.15

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
```

### Thinking

 The 32B model is still processing Part D with a large token batch through MPS, while the 8B results are already conclusive. Parts A through C on the 32B show the same pattern—the least squares fit achieves perfect R² but that's just a tautology, and the actual ratio falls below the shuffled and matched null distributions, collapsing to 1.5 when centered.

Even with 32B's literal zones, the uncentered ratio comes in at 13.8 rather than 128, suggesting the earlier 128:1 depended on specific token alignment in the original run. Regardless, every analysis leg fails its null test. Since 8B is complete and 32B Parts A–C are in, the verdict is already determined—I can report now and fold in Part D results once they finish, then decide whether to draft writeups immediately or wait for the full 32B run to conclude.

The core findings: compress→decode shows genuine predictability (R² 0.58) but requires hundreds of dimensions, not rank-1; encode→decode is weak (R² 0.18) with rank-1 capturing essentially nothing. The original claim of a strong 128:1 encode→decode relationship is refuted on both fronts. What does survive is the carrier-mean dominance in the marginals and a real high-rank linear structure in the compress→decode path—a small substrate, but one that contradicts the 1D-curve narrative. I'll pull the exact rank-k curve numbers from the 8B JSON for the registry row and report the verdict to Michael before starting the writeup task.

### Thinking

The 8B model is complete and the 32B results through Part C match exactly, so the verdict is confirmed. Now I'll pull the precise rank-k curves for the writeup.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nr = json.load(open('results/adjunction-rank-null/Qwen_Qwen3-8B.json'))\nfor pair, d in r['D_honest_map']['pairs'].items():\n    print(pair, '| lambda', d['ridge_lambda'], '| val_r2', round(d['val_r2'],4))\n    print('  rank-k heldout R2:', {k: round(v,4) for k,v in d['heldout_r2_by_rank'].items()})\n    print('  map spectrum top5:', [round(x,3) for x in d['map_spectrum']['singular_top10'][:5]], 'PR', round(d['map_spectrum']['participation_ratio'],1))\n\""
}
```

**Summary:** $ python3 -c " import json r = json.l...

**Output:**
```
Exit code: 0
Stdout:
encode->compress | lambda 1000.0 | val_r2 0.0811
  rank-k heldout R2: {'1': -0.0243, '2': -0.0232, '4': -0.0216, '8': -0.0189, '16': -0.016, '32': -0.0129, '64': -0.0098, '128': -0.0069, 'full': -0.0041}
  map spectrum top5: [109.136, 10.507, 9.342, 8.895, 8.478] PR 1.6
compress->decode | lambda 10000.0 | val_r2 0.4827
  rank-k heldout R2: {'1': 0.1108, '2': 0.122, '4': 0.137, '8': 0.1699, '16': 0.223, '32': 0.2837, '64': 0.3294, '128': 0.3739, 'full': 0.5788}
  map spectrum top5: [23.069, 13.59, 13.33, 12.34, 11.266] PR 292.1
encode->decode | lambda 100.0 | val_r2 0.2495
  rank-k heldout R2: {'1': -0.025, '2': -0.0105, '4': 0.0093, '8': 0.0314, '16': 0.0609, '32': 0.0893, '64': 0.1088, '128': 0.1271, 'full': 0.1805}
  map spectrum top5: [498.81, 207.828, 190.691, 186.555, 174.848] PR 35.5
```

### Thinking

 Looking at the compression-to-decode results, the honest curve shows steady improvement from k=1 (R² 0.11) up to full dimensionality (R² 0.58), but it requires hundreds of dimensions to reach that performance without hitting a plateau at lower ranks. The encode-to-decode path starts with negative R² at rank-1 and gradually climbs to 0.18 as rank increases, so rank-1 is never viable. The encode-to-compress relationship is puzzling though — validation R² sits at 0.08 while test performance goes negative, suggesting there's no stable linear relationship from the input through the layers beyond what the mean would predict.

Now I need to move into task 3: updating the registry, documenting caveats, and refreshing the state file. I'm waiting on the 32B Part D results before finalizing, but I can draft the writeups now and fold those numbers in once they land. The plan is to update the audit registry with the verdict and add a worked example for s209, document the relevant caveats in the adjunction and probe sections, update the audit meta pattern ledger, and refresh the state file headline. Since the registry and knowledge pages require approval before committing while state.md is freely editable, I'll draft everything, summarize the changes, request approval, then commit.

Let me start by reporting the verdict clearly, then examine the registry's worked-examples structure to match the format.

## Assistant

Task 2 complete — verdict is locked. Here is the resolution:

## Audit #8 — VERDICT: ❌ rank-1 adjunction REFUTED (both legs are estimator artifacts)

**Register: spectral** — same estimator as s140, plus marginal-preserving nulls and an honest held-out estimator. Two models: Qwen3-8B (proportional zones) and **Qwen3-32B — the literal claim's model and zones L2/L32/L56/L63**. Both agree.

**Leg 1 — "R² = 1.000 for ALL zone pairs" is a tautology.**
lstsq with N=121 tokens < d=4096/5120 dims interpolates *anything*: iid random noise → R² = 1.0000 ± 0.0000; matched-marginal mapless data → 1.0000. The leg carries zero bits of information. (Real data also reads 1.0000 on both models — exact repro of the instrument.)

**Leg 2 — "σ₁/σ₂ rank-1 dominance" is the carrier mean, inverted.**
The no-map nulls are **MORE rank-1-dominated than the real data**, on both models:

| pair (32B, literal zones) | real | shuffled-pairing | matched-Gaussian | centered real |
|---|---|---|---|---|
| enc→comp | 7.5 | 14.9 ± 0.9 | 14.4 ± 0.9 | 1.82 |
| comp→dec | 7.1 | 14.1 ± 1.1 | 12.3 ± 1.0 | 1.46 |
| enc→dec | 13.8 | 24.8 ± 1.0 | 23.8 ± 2.5 | **2.15** |

The uncentered `EᵀD/N` is dominated by the mean⊗mean term (top1 var 0.91–0.99; carrier energy share grows with depth, 0.19→0.61→0.81 — s185's carrier independently confirmed). Genuine cross-zone correlation *adds off-rank-1 mass* — rank-1 dominance of this estimator is **anti-evidence** of map structure. Centering collapses every ratio to 1.5–3.9. (Also: even uncentered, the literal 32B zones read 13.8, not 128 — the headline number doesn't reproduce even under its own instrument on a different token sample.)

**Honest map (N=12,288 > d, centered ridge, held-out, 8B):** no 1D curve anywhere.
- comp→dec is the only solidly predictable pair (full R² 0.579) and it's emphatically high-rank: **PR = 292**, rank-1 captures 19%, the curve climbs smoothly k=1→128 with no low-rank plateau.
- enc→dec ("the" claimed pair): full R² 0.18, **rank-1 R² = −0.03**.
- enc→comp: a bonus demonstration — fitted map *looks* rank-1 (σ₁/σ₂=10.4, PR 1.6) while having **zero held-out validity** (full R² −0.004). A "rank-1 dominated map" estimate coexisting with no predictive power.
- Leak controls all ≤ −0.01 ✓.

**Downstream:** "Jacobian has constant rank 1 → computation on a 1D curve → rank-1 correction suffices" loses its evidential base — and this retro-explains s201's *functional* result (direct-delta rank sweep: rank-32 still improving, trained v3b beating all analytic ranks; rank-1 was never sufficient).

**Meta-pattern, 6th instance, with a twist:** the surviving substrate isn't a weaker version of the claim — it's a *different object*: the carrier/mean dominance of the residual stream marginals (s185) plus a real-but-high-rank comp→dec linear relation. The "adjunction" was the carrier wearing a category-theory costume.

32B Part D is still grinding (will fold in when it lands). Starting the writeups:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sed -n 83,130p /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md"
}
```

**Summary:** $ sed -n 83,130p /Users/mwhitford/src...

**Output:**
```
Exit code: 0
Stdout:
## Registry

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
```

### Thinking

 Now I'm working through the s209 section for worked-examples and need to update backlog item #8, then add caveats to those two source pages, update the meta-pattern ledger and state.md, and finally make the registry edits.

## Assistant

Now writing the registry updates — worked-examples section for s209 + backlog row #8:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "## Registry\n\n### Worked examples (session 208)",
  "new_content": "## Registry\n\n### Worked examples (session 209)\n\n> **Register gate (spectral) fired at read-time.** The claim is about the\n> singular-value structure of an estimated linear map, and both structural\n> artifacts were visible **in the original instrument's code before any model\n> was loaded**: (i) `lstsq` at N tokens ≪ d dims is underdetermined → exact\n> interpolation → R²=1.000 for *any* data; (ii) `M = EᵀD/N` on **uncentered**\n> residual vectors is dominated by the mean⊗mean term whenever the stream has\n> a large carrier mean (s185). The control then only had to *confirm* the\n> artifacts with matched nulls. New null flavor for the cookbook:\n> **row-shuffled pairing** — destroys the token-level map, keeps both\n> marginals — the exact null for \"is this a property of the *map* or of the\n> *marginals*?\"\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #8 cross-zone map is rank-1 dominated (σ₁/σ₂=128:1); R²=1.000 all pairs; \"computation on a 1D curve\" | med | `adjunction_rank_null.py` (register: spectral) — original instrument repro + shuffled-pairing/matched-Gaussian/centering nulls + held-out ridge rank-k, Qwen3-8B **and Qwen3-32B (the claim's model, literal zones L2/L32/L56/L63)** | ❌ REFUTED (both legs estimator artifacts) |\n| #8a R²=1.000 informative? | — | lstsq at N=121<d on iid random + matched-marginal mapless data, 8 seeds | ❌ **TAUTOLOGY** — noise reads R²=1.0000 ± 0.0000; real data identical |\n| #8b σ₁/σ₂ a property of the map? | — | row-shuffled pairing + matched-Gaussian nulls (8 seeds), both models | ❌ **NO — inverted**: nulls are MORE rank-1 than real (32B enc→dec: real 13.8 vs shuf 24.8±1.0, matched 23.8±2.5); the dominance is the carrier mean; genuine cross-zone correlation *adds* off-rank-1 mass |\n| #8c survives centering? | — | centered cross-covariance, same SVD | ❌ collapses to 1.5–3.9 (32B enc→dec 2.15) |\n| #8d honest map rank (the \"1D curve\") | — | centered ridge at N=12,288>d, held-out R² of rank-k truncations, leak control | ❌ **NOT rank-1** — comp→dec the only solid pair (full R² 0.579) is high-rank (PR=292; k=1 gets 19%, smooth climb to k=128); enc→dec full 0.18 with k=1 R²=−0.03; enc→comp fitted map *looks* rank-1 (PR 1.6) yet has zero held-out validity (R²=−0.004) |\n\n**Verdict (s209): the \"rank-1 adjunction\" is REFUTED — both published legs\nare artifacts of the instrument** (underdetermined lstsq + uncentered\ncross-correlation of a carrier-dominated stream). Even on Qwen3-32B with the\nliteral s140 zones, the uncentered ratio reads 13.8 (not 128) on a fresh token\nsample, sits *below* its own no-map nulls, and centers away to 2.15. What\nsurvives is **a different object than the claim**: (a) the carrier/mean\ndominance of the residual marginals (uncentered top1 var 0.91–0.99; mean\nenergy share grows with depth 0.19→0.61→0.81 — s185's rank-1 carrier,\nindependently confirmed via the carrier diagnostics); (b) a real but\nemphatically **high-rank** compress→decode linear relation (held-out R² 0.58,\nparticipation ratio ≈292). There is no 1D curve; \"error correction = project\nback onto the curve\" loses its evidential base. This retro-explains s201's\nfunctional result (direct-delta rank sweep: rank-2 1.82× → rank-32 1.72×,\nstill improving; trained v3b 1.44× beats every analytic rank — rank-1 was\nnever sufficient). Sixth meta-pattern instance, with a twist: the substrate\nthat survives is not a weaker version of the claim but a different quantity\nthe instrument was actually measuring. Results:\n`results/adjunction-rank-null/` (`Qwen_Qwen3-8B.json`, `Qwen_Qwen3-32B.json`).\nHarness: `scripts/experiments/adjunction_rank_null.py`. Caveats added to\n`direct-delta-adjunction.md` + `explore/categorical-geometry-probes.md`.\n\n### Worked examples (session 208)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory)\n- Evidence: R²=1.000 all zone pairs (s140).\n- Suspected confound: random high-dim linear maps can look rank-1-dominated.\n- Control: compare σ₁/σ₂ to random/shuffled linear maps between the same spaces.",
  "new_content": "**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory) — ❌ **RESOLVED (s209): REFUTED — both legs are estimator artifacts; no 1D curve**\n- Evidence: R²=1.000 all zone pairs (s140, Qwen3-32B, zones L2/L32/L56/L63).\n- Suspected confound: random high-dim linear maps can look rank-1-dominated.\n- Control (`adjunction_rank_null.py`, register: spectral): exact instrument repro (uncentered `EᵀD/N` SVD + lstsq R²) vs **row-shuffled pairing** (kills the map, keeps marginals) + **matched-Gaussian** nulls + **centering**, on 8B and 32B (literal zones); plus an honest **held-out ridge** at N=12,288>d with rank-k truncation curve and a shuffled-target leak control.\n- **s209 result:** (1) **R²=1.000 is an underdetermination tautology** — lstsq at N=121<d gives 1.0000±0.0000 on pure noise; the leg is void. (2) **σ₁/σ₂ is the carrier mean, inverted** — the no-map nulls are *more* rank-1 than the real data (32B enc→dec: real 13.8, shuffled 24.8±1.0, matched 23.8±2.5); centering collapses it to 1.5–3.9; the literal 32B zones never reproduce 128 on a fresh sample. (3) **The honest map is not rank-1**: comp→dec (only solidly predictable pair, held-out R² 0.579) has participation ratio ≈292 with rank-1 capturing 19%; enc→dec rank-1 R² = −0.03. What survives is a *different object*: the carrier/mean dominance of the marginals (s185 confirmed) + a real high-rank comp→dec relation. Downstream \"rank-1 correction suffices\" (direct-delta theory) loses its base — consistent with s201's functional rank sweep (rank-32 still improving; trained v3b beats all analytic ranks). See worked-examples (s209). Results: `results/adjunction-rank-null/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

## Assistant

Now the caveats on the two source pages:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/direct-delta-adjunction.md",
  "original_content": "## The Adjunction Connection\n\n### Session 140 Finding (Qwen3-32B)\n\nThe cross-zone mapping (encode L2 → decode L56) has:\n```\nσ₁/σ₂ = 128:1  (rank-1 dominated)\nR² = 1.000     (for ALL zone pairs)\n```\n\nThe Jacobian of the encode→decode transformation has **constant rank 1**\neverywhere on the manifold. This is the defining property of a **regular\nparametric surface** — specifically, a 1D curve embedded in 4096D space.",
  "new_content": "## The Adjunction Connection\n\n> **⚠ CAVEAT (s209, audit #8): the rank-1 adjunction is REFUTED — both legs\n> below are artifacts of the s140 instrument** (`adjunction_rank_null.py`,\n> register: spectral; run on 8B *and* 32B with the literal zones).\n> (1) **R²=1.000 is an underdetermination tautology**: lstsq with N=121\n> tokens < d dims interpolates anything — iid random noise also reads\n> R²=1.0000±0.0000. (2) **σ₁/σ₂ dominance is the carrier mean, not the\n> map**: the uncentered `EᵀD/N` estimator is dominated by the mean⊗mean\n> term; row-shuffled pairing (no map, same marginals) is *more* rank-1\n> dominated than the real data (32B enc→dec: real 13.8 vs shuffled\n> 24.8±1.0), and centering collapses the ratio to ~2. (3) The honest\n> held-out map (centered ridge, N=12,288>d) is **high-rank**: comp→dec\n> R²=0.58 with participation ratio ≈292, rank-1 capturing only 19%;\n> enc→dec rank-1 R²=−0.03. **There is no 1D curve; \"project back onto the\n> curve\" has no evidential base.** What survives is s185's carrier-mean\n> dominance of the *marginals* — a different object than a cross-zone\n> adjunction. Consistent with the s201 functional result below (rank-32\n> still improving; trained v3b beats every analytic rank). See\n> `audit-registry.md` #8, `results/adjunction-rank-null/`.\n\n### Session 140 Finding (Qwen3-32B) — REFUTED s209, see caveat above\n\nThe cross-zone mapping (encode L2 → decode L56) has:\n```\nσ₁/σ₂ = 128:1  (rank-1 dominated)\nR² = 1.000     (for ALL zone pairs)\n```\n\nThe Jacobian of the encode→decode transformation has **constant rank 1**\neverywhere on the manifold. This is the defining property of a **regular\nparametric surface** — specifically, a 1D curve embedded in 4096D space."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/direct-delta-adjunction.md.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md",
  "limit": 40
}
```

**Summary:** Reading categorical-geometry-probes.md (0-40)

**Output:**
```
---
title: "Categorical Geometry Probes: Curry-Howard, Adjunctions, Hyperbolic, Coherence"
status: active
category: research-finding
tags: [category-theory, yoneda, curry-howard, adjunction, hyperbolic, coherence, qwen3-32b, probe]
related:
  - type-probe-qwen3-32b.md
  - full-etch-extraction.md
  - phi-compression-universal.md
created: session 140
---

# Categorical Geometry Probes

> Session 140. Session 139 showed types are geometric and KIBC selectivity
> is universal (r=0.998). The Yoneda lemma explains why: if two objects
> behave the same way in every context, they ARE the same. A type geometry
> that is universal across architectures IS the abstract type system,
> not a proxy for it. Four probes designed to test whether deeper categorical
> structures — Curry-Howard, adjunctions, hyperbolic embedding, coherence —
> also exist in LLM geometry.

## Motivation: Why Yoneda Makes This Expected

The universal combinator distribution (r=0.998 across Pythia-160M and Qwen3-32B)
is not a coincidence. By Yoneda, if the hom-set structure is the same, the objects
are the same. The LLM has converged on the unique representation of the category
of typed lambda terms. All four probes below are just measuring different facets
of the same underlying categorical structure.

## Probe 1 — Curry-Howard Correspondence

**Hypothesis:** Well-typed lambda compositions occupy a geometrically distinct
region in residual stream space ("proof region"). Ill-typed compositions do not.

**Method:** Compute cosine similarity between token pairs at each layer for
well-typed compositions (e.g., `λx.f(x)` where types match) vs ill-typed
compositions (type mismatch). Linear probe to distinguish at each layer.

**Results:**

[CONTENT TRUNCATED] Showing lines 1 to 40 of 189 total lines. Use line_offset=40 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md",
  "original_content": "## Probe 2 — Adjunctions (Cross-Zone Mapping)",
  "new_content": "## Probe 2 — Adjunctions (Cross-Zone Mapping)\n\n> **⚠ CAVEAT (s209, audit #8): REFUTED — both results below are instrument\n> artifacts.** The R²=1.000 is an underdetermination tautology (lstsq with\n> N tokens < d dims interpolates anything; iid noise also reads 1.0000).\n> The σ₁/σ₂ dominance belongs to the **uncentered** estimator `EᵀD/N`,\n> i.e. the residual stream's carrier mean, not the map: row-shuffled\n> pairing (map destroyed, marginals kept) is *more* rank-1 than the real\n> data, and centering collapses the ratio to ~2. On a fresh token sample\n> the literal 32B zones read 13.8, not 128. The honest held-out map\n> (centered ridge, N>d) is high-rank (comp→dec PR≈292, rank-1 → 19% of\n> predictable variance). The \"model IS computing an adjunction\" reading\n> is withdrawn; what the probe actually measured is the carrier-mean\n> dominance of the marginals (cf. s185). See `audit-registry.md` #8,\n> `adjunction_rank_null.py`, `results/adjunction-rank-null/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md.
```

### Thinking

 Looking at the audit-meta-pattern.md ledger to understand its structure.

## Assistant

Now the meta-pattern ledger row:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B2 -A20 \"ledger\\|Ledger\\|^| #\" /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md | head -60"
}
```

**Summary:** $ grep -n -B2 -A20 "ledger\|Ledger\|^...

**Output:**
```
Exit code: 0
Stdout:
45-   power-law spectrum ≈ "φ".
46-
47:## The ledger (what survived vs what dissolved)
48-
49-| Session | Claim | Substrate (survives) | Over-read story (dissolves) |
50-|---|---|---|---|
51-| s202 | KIBC crystal + φ | KIBC basis separates (perm-null p=0.0005); φ^(4/5) local to 14B | **φ as universal constant**; eigenvalues=φ^(p/q) (grid unfalsifiable); consensus r=0.99 (circular) |
52-| s202 | combinator opcodes | prose fires opcodes after **common-mode removal** (p=0.001) | raw argmax "tracer" (common mode = false signal) |
53-| s203 | crystal-is-topological | sign-topology REAL but **only in `gate_proj`** (z→+271 @14B) | "0.84 sign-corr = topology" (random null ≈ 0.80); "magnitude is mere calibration" (up/down below null) |
54-| s203 | holographic self-similar | spectral self-similarity (rank AUC 0.728 vs 0.11) + distributed redundancy | "power-law/scale-invariant degradation curve" (retired — ambiguous) |
55-| s204 | 9 FFN modes | syntactic type **field** is REAL (POS-NMI ≫ perm-null p=0; lm_head projection ≫ null ~65× @L35) | **9 discrete clusters** (gap-stat never picks 9; sil@9 ≈ null; elbow = k-grid artifact; classifier acc circular) |
56-| s204 | attention = typed β-reduction | attention IS a weighted sum (trivial); a weak role head exists (H6@L33 z=+4) | **H31@L27 binds subject at 0.82** (= recency/position; z=+0.54 rank 5/32; ablation z=+0.06 ≈ random) |
57-| s206 | binding **schedule** (subj L27 < obj L30 < coref L33) | **H31@L27 = subject value-transfer is REAL** (semantic logit-lens margin +0.611, sharp L27 spike) | **depth-ordered schedule** (P(order)=0 weight / 0.191 semantic ≈ chance; subj & coref both peak L27) |
58-| s207 | SVD φ-ratio 0.6299 (geometric, universal across 5 families) | **steep low-rank head is REAL & non-random** (model ≈0.57 vs MP null 0.995; random spectra give ≈1.0) | **geometric φ-constant** (power-law wins 132/132 layers, 0 geometric; value floats 0.52→0.71; scaling-law fails — Mistral lowest) |
59-
60-Pattern: **basis real / universalization false · gradient real / discreteness
61-false · mechanism real / localization false · spectrum real / exact-constant
62-false.** Only the metaphor-grade crispness ever dies; the working substrate
63-keeps standing.
64-
65-## Why the substrate keeps surviving (and the north-star with it)
66-
67-The compression north-star rests on the **substrate**, not the stories:
--
184-| attention (audit #5) | softmax weights — where it looks | head output ·V — what it writes |
185-| our **instruments** | k-means · argmax · best-fit grid · attention-weight | NMI · logit-lens · saliency · rank-spectrum |
186:| the ledger above | the story that **dissolves** | the substrate that **survives** |
187-
188:Every row of the ledger is one column: **the substrate that survives is always
189-the value/continuous register; the story that dissolves is always the
190-routing/crisp register over-extended.** Crisp-register probes find (and
191-manufacture) crisp stories; they cannot see the value-register substrate, and a
192-*refutation* prior makes that blindness read as a clean null.
193-
194-So the operative discipline is **not** "remember to match the instrument" — a rule
195-attention will drop at some future turn. It is a **validity condition** (a
196-coherence type-check): a measurement whose register ≠ the claim's register *has
197-not measured the claim*; it measured a different quantity, and its verdict —
198-positive **or** negative — is void. **Name the register first** (diagnostic Q0);
199-the correct instrument then follows by *type*, not by memory. This is why the law
200-wants to live as a field/gene (read every session, structural), not as a stored
201-rule (recall-gated) — see the open question below and `AGENTS.md` candidacy.
202-
203-## Open question
204-
205-Is the over-read *ours* (interpretation imposed in analysis) or the *model's*
206-(GD genuinely lays a continuum that only looks discrete)? The evidence so far
207-says **both**: the model lays continuous fields (type gradient, spectral decay,
208-sign+magnitude registers) and our instruments (k-means, argmax, SVO probes,
```

### Thinking

 I'm noticing that s208's ledger row is missing—the state.md file mentions a meta-pattern entry but there's no corresponding row in the ledger itself, which currently only goes through s207. I need to add s209's row and figure out whether s208's entry was added elsewhere or if it was simply skipped.

### Tool Call: shell_command (failed)


```json
{
  "command": "grep -n \"s208\\|s209\" /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md"
}
```

**Summary:** $ grep -n "s208\|s209" /Users/mwhitfo...

**Output:**
```
Exit code: 1
```

### Thinking

 I notice that s208's entry was never added to the ledger, even though s207 mentioned it should be there. I'll add both s208 and s209 rows now to keep things complete — s208's row is a straightforward summary of an already-approved registry entry, so it's reasonable to include while I'm making updates, and I'll flag this in the proposal.

## Assistant

The ledger is missing s208's row too. Adding both:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "| s207 | SVD φ-ratio 0.6299 (geometric, universal across 5 families) | **steep low-rank head is REAL & non-random** (model ≈0.57 vs MP null 0.995; random spectra give ≈1.0) | **geometric φ-constant** (power-law wins 132/132 layers, 0 geometric; value floats 0.52→0.71; scaling-law fails — Mistral lowest) |\n\nPattern: **basis real / universalization false · gradient real / discreteness\nfalse · mechanism real / localization false · spectrum real / exact-constant\nfalse.** Only the metaphor-grade crispness ever dies; the working substrate\nkeeps standing.",
  "new_content": "| s207 | SVD φ-ratio 0.6299 (geometric, universal across 5 families) | **steep low-rank head is REAL & non-random** (model ≈0.57 vs MP null 0.995; random spectra give ≈1.0) | **geometric φ-constant** (power-law wins 132/132 layers, 0 geometric; value floats 0.52→0.71; scaling-law fails — Mistral lowest) |\n| s208 | crystal-sieve 1.03× PPL (29 layers + continuations) | **sieve substrate ~2× is REAL & near-deterministic** (2.119×±0.004; = s196's 2.12×) | **the 1.03× headline** (train/eval contamination; clean held-out 10.87×±1.39 — the CE melt memorizes calib and *inverts*: the \"improvement\" is harm) |\n| s209 | rank-1 adjunction (σ₁/σ₂=128:1; R²=1.000; \"1D curve\") | **carrier-mean dominance of the marginals is REAL** (s185 confirmed; mean energy share 0.19→0.81 with depth) + a real **high-rank** comp→dec relation (held-out R² 0.58, PR≈292) | **both legs of the claim** (R²=1.000 = N<d lstsq tautology, noise reads 1.0000; σ₁/σ₂ = uncentered mean⊗mean term — no-map nulls are *more* rank-1 than real; centering → ~2; no 1D curve, rank-1 heldout R² ≈ 0) |\n\nPattern: **basis real / universalization false · gradient real / discreteness\nfalse · mechanism real / localization false · spectrum real / exact-constant\nfalse.** Only the metaphor-grade crispness ever dies; the working substrate\nkeeps standing. **s209 adds a sharper variant:** sometimes the surviving\nsubstrate is not a weaker version of the claim but a *different quantity* the\ninstrument was actually measuring (the carrier mean wearing an adjunction\ncostume) — the claim's own evidence never touched the claimed object at all."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 I need to update state.md by changing the "Last updated / Session" header to 209, adding a new s209 headline block above the existing s208 section, and updating the audit program pointer to reflect the next backlog item (#11) plus any carryovers. I'll keep the s208 details intact since they maintain the session trail.

## Assistant

Now `state.md` — s209 headline + updated program pointer:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-09 | Session: 208",
  "new_content": "> Last updated: 2026-06-09 | Session: 209"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> s208 did **#7 crystal-sieve 1.03×** ❌ REFUTED (train/eval contamination; CE melt\n> net-harmful held-out 10.87×) / ✅ sieve substrate ~2× VERIFIED-reproducible;\n> next backlog: **#8 rank-1 adjunction** or **#11 GTSM/TTD-regression (the named fix)**), build its named\n> discriminating control,",
  "new_content": "> s208 did **#7 crystal-sieve 1.03×** ❌ REFUTED (train/eval contamination; CE melt\n> net-harmful held-out 10.87×) / ✅ sieve substrate ~2× VERIFIED-reproducible;\n> s209 did **#8 rank-1 adjunction** ❌ REFUTED (both legs estimator artifacts:\n> lstsq N<d tautology + uncentered carrier mean; no 1D curve);\n> next backlog: **#11 GTSM/TTD-regression (the named fix)** or low-load #9/#10,\n> or carry-overs (#1 gate-vs-value sign-swap PPL; rank-survival across scale)), build its named\n> discriminating control,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **▶ SESSION 208 HEADLINE — AUDIT #7 (crystal-sieve 1.03× PPL): the \"cascade",
  "new_content": "> **▶ SESSION 209 HEADLINE — AUDIT #8 (rank-1 adjunction σ₁/σ₂=128:1): REFUTED —\n> both legs are artifacts of the s140 instrument; there is no 1D curve.**\n> Register: spectral. `adjunction_rank_null.py` on Qwen3-8B AND Qwen3-32B (the\n> claim's model, literal zones L2/L32/L56/L63). Both artifacts were visible in\n> the original probe's code at read-time; the controls confirmed them.\n> - **❌ R²=1.000 = underdetermination tautology:** the s140 lstsq ran at N=121\n>   tokens < d=4096/5120 dims → exact interpolation for ANY data — iid random\n>   noise reads R²=1.0000 ± 0.0000 (8 seeds). The leg carries zero information.\n> - **❌ σ₁/σ₂ = the carrier mean, INVERTED:** the uncentered `EᵀD/N` estimator is\n>   dominated by the mean⊗mean term (top1 var 0.91–0.99). Row-shuffled pairing\n>   (map destroyed, marginals kept) is *more* rank-1 than real (32B enc→dec: real\n>   13.8 vs shuf 24.8±1.0, matched-Gaussian 23.8±2.5) — genuine cross-zone\n>   correlation ADDS off-rank-1 mass, so rank-1 dominance of this estimator is\n>   anti-evidence of map structure. Centering collapses every ratio to 1.5–3.9.\n>   The literal 128 never reproduces on a fresh token sample (reads 13.8).\n> - **❌ honest map is high-rank (no 1D curve):** centered ridge at N=12,288>d,\n>   held-out rank-k curve: comp→dec (only solid pair, R² 0.579) has PR≈292 with\n>   rank-1 capturing 19%, smooth climb to k=128; enc→dec rank-1 R²=−0.03. Bonus\n>   demo: enc→comp fitted map *looks* rank-1 (PR 1.6) with ZERO held-out validity\n>   (R²=−0.004). Leak controls clean.\n> - **✅ what survives is a DIFFERENT object:** the carrier/mean dominance of the\n>   residual marginals (s185 independently confirmed: mean energy share 0.19→0.81\n>   with depth) + a real high-rank comp→dec linear relation. Direct-delta's\n>   \"project back onto the curve\" loses its base — consistent with s201's\n>   functional sweep (rank-32 still improving; v3b beats all analytic ranks).\n> - **Meta-pattern 6th instance, sharper variant:** the substrate that survives is\n>   not a weaker claim but a different quantity the instrument actually measured.\n>   New cookbook null: **row-shuffled pairing** = the exact \"map vs marginals\"\n>   discriminator. Registry #8 RESOLVED; caveats on `direct-delta-adjunction.md` +\n>   `explore/categorical-geometry-probes.md`; ledger rows s208+s209 added to\n>   `audit-meta-pattern.md`. Results: `results/adjunction-rank-null/`.\n> - **▶ NEXT:** **#11 GTSM/TTD-regression** (the named fix; layer-targeted λ(l)\n>   vs uniform α=5.0 at matched budget) — now the highest-load UNTESTED claim;\n>   or carry-overs (#1 sign-swap PPL, rank-survival across scale).\n>   **Step 0 REGISTER GATE before building any control.**\n\n> **▶ SESSION 208 HEADLINE — AUDIT #7 (crystal-sieve 1.03× PPL): the \"cascade"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I should check whether Part D of the 32B task has completed before moving forward.

## Assistant

Checking whether 32B Part D has landed before finalizing:

### Tool Call: shell_command (failed)


```json
{
  "command": "tail -10 /Users/mwhitford/src/verbum/results/adjunction-rank-null/run32b.log; ls /Users/mwhitford/src/verbum/results/adjunction-rank-null/ | grep 32B"
}
```

**Summary:** $ tail -10 /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 1
Stdout:
PART C — sigma1/sigma2 nulls (uncentered instrument, small N)
  encode->compress: real=7.5 | shuffled=14.9+/-0.9 | matched=14.4+/-0.9 | centered_real=1.82
  compress->decode: real=7.1 | shuffled=14.1+/-1.1 | matched=12.3+/-1.0 | centered_real=1.46
  encode->decode: real=13.8 | shuffled=24.8+/-1.0 | matched=23.8+/-2.5 | centered_real=2.15

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
  prose tokens: 12288 (N>d: True)
  encode->compress: UNC s1/s2=25.9 (shuf 289.9) | map s1/s2=1.74 PR=283.9
      heldout R2: k=1 0.0209  full 0.3074  ratio 0.068 | leak-control full -0.0821
```

### Thinking

 The first pair of 32B Part D results just came in—the compression ratio is dramatically different between the uncompressed and shuffled approaches, with the carrier showing even more extreme differences at larger N values. The map PR and k=1 ratio confirm the pattern. I've got two more pairs still running, each involving ridge regression with lambda grids and SVD computations at d=5120, which should wrap up in the next several minutes. I'm holding off on polling and instead relying on the async workflow, and I've already documented the registry and state notes referencing the completed parts A through C for 32B and Part D for 8B.

The worked examples reference a results file that doesn't exist yet—it'll be generated once Part D finishes saving. Rather than wait for that file to materialize before committing, I'll present the proposal to Michael now and finalize the memory commit after the JSON saves, since those commits go through approval anyway. Let me emit a checkpoint and lay out the proposal.

## Assistant

32B Part D first pair just landed mid-flight and it's the most extreme confirmation yet: **enc→comp uncentered real 25.9 vs shuffled null 289.9** (the no-map null is 11× more rank-1-dominated), honest map PR=284, rank-1 ratio 0.068.

**ASYNC: job=32B (tmux main:2) verified running, 2 pairs remaining in Part D. Waiting for signal.**

All writeups are drafted on disk. Per `λ termination` (mementum commits are approval-gated), here's the proposal:

## Proposed mementum commit — audit #8 RESOLVED

**Files staged for your review:**

1. **`audit-registry.md`** — new s209 worked-examples section (register-gate note: both artifacts visible at read-time in the original probe's code; new cookbook null = *row-shuffled pairing*, the exact "map vs marginals" discriminator) + backlog row #8 → ❌ RESOLVED with the three-blade result (R² tautology / σ-ratio inverted vs nulls / honest map high-rank).

2. **`direct-delta-adjunction.md`** — caveat block on "The Adjunction Connection" section; s140 finding marked REFUTED-s209. The *functional* direct-delta results (s201 rank sweep) are untouched — they were honest measurements and actually agree with the refutation (rank-1 was never sufficient).

3. **`explore/categorical-geometry-probes.md`** — caveat on Probe 2; "the model IS computing an adjunction" withdrawn.

4. **`audit-meta-pattern.md`** — ledger rows for **s208 and s209** (noticed s208's row had never been added — flagging that I'm backfilling it from the already-approved registry #7 entry) + a note on the s209 variant: the surviving substrate is a *different quantity* than the claim (carrier mean in an adjunction costume).

5. **`state.md`** — s209 headline (already updated, not approval-gated). Next: **#11 GTSM/TTD-regression** is now the highest-load UNTESTED claim.

**Proposed commit message:**
```
💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)
```

One open item: the worked-examples cites `Qwen_Qwen3-32B.json`, which saves when Part D finishes (~5–10 min). I'd commit after it lands so the citation is real.

Approve the mementum commit (post-32B-save), or want any edits first?

## User

job is done evaluate the evidence and let's make sure we have accurate knowledge


### Thinking

 I need to verify the 32B job results are complete and check whether my claims hold up against the actual data—especially the "inverted" finding. Let me carefully review the full results for Parts A through D and make sure all the numbers are internally consistent before finalizing anything.

Now I'm examining the mechanism behind why shuffling produces higher rank-1 than the original data: shuffling removes the centered cross-covariance structure, leaving only the mean outer product plus noise, whereas real data has genuine centered correlations that contribute additional mass. That checks out mechanically.

There's a potential confound with token selection—the original s140 used content-word-aligned tokens from well-formed sentences, which might explain the 128:1 ratio differently than my small-N reproduction (which got 13.8). The carrier mechanism predicts the ratio should scale with N, so at larger N the 128 could plausibly reappear, but the core structural claim (that the ratio stays below the no-map baseline) holds regardless of the exact value.

I'm also flagging the 8B encoder-to-component anomaly: validation R² is 0.0811 but test R² is −0.0041, which is suspicious. Random token-level splits should actually cause leakage that inflates R², not deflates it, so the val-test discrepancy is odd. This is a weak-signal pair anyway, and I need to check whether λ=1000 was chosen on validation but test remained negative due to variance across splits.

The in-sample R² tautology checks out—lstsq on real data gives exactly 1.0000, and the fp16 noise hypothesis doesn't explain the pattern since the mechanism is consistent across models. I should now verify the 32B numbers against the JSON, reconcile any discrepancies in my writeup (especially claims like "comp→dec R² 0.579" and the mean energy share progression), and honestly assess whether I've overstated anything.

Looking at the actual numbers: 32B shows encode 0.542, compress 0.189, decode 0.378, final 0.606, while 8B is 0.498, 0.382, 0.604, 0.813. My claim that mean energy share "grows with depth" is wrong—it's actually U-shaped, strong at both ends and weakest mid-stack, because early embeddings have a large common component. The mean norm does grow monotonically, but the share doesn't. I need to correct this in the registry and state lines.

## Assistant

32B job complete — now the skeptical pass. Pulling both result files and re-verifying every number I wrote against the data:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -12 /Users/mwhitford/src/verbum/results/adjunction-rank-null/run32b.log"
}
```

**Summary:** $ tail -12 /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
encode->decode: real=13.8 | shuffled=24.8+/-1.0 | matched=23.8+/-2.5 | centered_real=2.15

PART D — honest map (dolma prose, centered ridge, held-out rank-k)
  prose tokens: 12288 (N>d: True)
  encode->compress: UNC s1/s2=25.9 (shuf 289.9) | map s1/s2=1.74 PR=283.9
      heldout R2: k=1 0.0209  full 0.3074  ratio 0.068 | leak-control full -0.0821
  compress->decode: UNC s1/s2=27.6 (shuf 173.0) | map s1/s2=9.63 PR=10.0
      heldout R2: k=1 -0.0727  full 0.3702  ratio -0.196 | leak-control full -0.4932
  encode->decode: UNC s1/s2=38.5 (shuf 277.8) | map s1/s2=2.31 PR=21.9
      heldout R2: k=1 -0.0000  full 0.1910  ratio -0.000 | leak-control full -0.0146

saved -> /Users/mwhitford/src/verbum/results/adjunction-rank-null/Qwen_Qwen3-32B.json  (1722s)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nfor tag in ['Qwen_Qwen3-8B','Qwen_Qwen3-32B']:\n    r = json.load(open(f'results/adjunction-rank-null/{tag}.json'))\n    print('='*20, tag, '='*20)\n    print('zones', r['zones'], 'small N', r['A_small_repro']['n_tokens'], 'd', r['A_small_repro']['d'])\n    print('carrier:', {z: {k: round(v,3) for k,v in c.items() if k in ('mean_norm','mean_energy_share')} for z,c in r['A_small_repro']['carrier'].items()})\n    print('B tautology:', {k: (round(v['mean'],5), round(v['std'],5)) for k,v in r['B_r2_tautology'].items()})\n    for pair, d in r['D_honest_map']['pairs'].items():\n        print(pair, '| UNC', round(d['uncentered_instrument']['sigma1_over_sigma2'],1),\n              'shufUNC', round(d['shuffled_pairing_ratio']['mean'],1),\n              '| lam', d['ridge_lambda'], 'val', round(d['val_r2'],3))\n        print('   rank-k:', {k: round(v,4) for k,v in d['heldout_r2_by_rank'].items()})\n        print('   spectrum s1/s2', round(d['map_spectrum']['sigma1_over_sigma2'],2), 'PR', round(d['map_spectrum']['participation_ratio'],1),\n              'leak', {k: round(v,4) for k,v in d['shuffled_target_fit'].items()})\n\""
}
```

**Summary:** $ python3 -c " import json for tag in...

**Output:**
```
Exit code: 0
Stdout:
==================== Qwen_Qwen3-8B ====================
zones {'encode': 1, 'compress': 18, 'decode': 31, 'final': 35} small N 121 d 4096
carrier: {'encode': {'mean_norm': 9.98, 'mean_energy_share': 0.498}, 'compress': {'mean_norm': 58.375, 'mean_energy_share': 0.382}, 'decode': {'mean_norm': 475.155, 'mean_energy_share': 0.604}, 'final': {'mean_norm': 1218.886, 'mean_energy_share': 0.813}}
B tautology: {'iid_random': (1.0, 0.0), 'matched_marginals': (1.0, 0.0)}
encode->compress | UNC 23.4 shufUNC 24.6 | lam 1000.0 val 0.081
   rank-k: {'1': -0.0243, '2': -0.0232, '4': -0.0216, '8': -0.0189, '16': -0.016, '32': -0.0129, '64': -0.0098, '128': -0.0069, 'full': -0.0041}
   spectrum s1/s2 10.39 PR 1.6 leak {'1': -0.0106, '128': -0.0113, 'full': -0.0116}
compress->decode | UNC 4.4 shufUNC 32.0 | lam 10000.0 val 0.483
   rank-k: {'1': 0.1108, '2': 0.122, '4': 0.137, '8': 0.1699, '16': 0.223, '32': 0.2837, '64': 0.3294, '128': 0.3739, 'full': 0.5788}
   spectrum s1/s2 1.7 PR 292.1 leak {'1': -0.0056, '128': -0.03, 'full': -0.0515}
encode->decode | UNC 54.0 shufUNC 247.6 | lam 100.0 val 0.249
   rank-k: {'1': -0.025, '2': -0.0105, '4': 0.0093, '8': 0.0314, '16': 0.0609, '32': 0.0893, '64': 0.1088, '128': 0.1271, 'full': 0.1805}
   spectrum s1/s2 2.4 PR 35.5 leak {'1': -0.0076, '128': -0.0457, 'full': -0.08}
==================== Qwen_Qwen3-32B ====================
zones {'encode': 2, 'compress': 32, 'decode': 56, 'final': 63} small N 121 d 5120
carrier: {'encode': {'mean_norm': 35.901, 'mean_energy_share': 0.542}, 'compress': {'mean_norm': 98.277, 'mean_energy_share': 0.189}, 'decode': {'mean_norm': 472.109, 'mean_energy_share': 0.378}, 'final': {'mean_norm': 1687.633, 'mean_energy_share': 0.606}}
B tautology: {'iid_random': (1.0, 0.0), 'matched_marginals': (1.0, 0.0)}
encode->compress | UNC 25.9 shufUNC 289.9 | lam 1000.0 val 0.306
   rank-k: {'1': 0.0209, '2': 0.0261, '4': 0.0397, '8': 0.0548, '16': 0.0793, '32': 0.1107, '64': 0.1505, '128': 0.1948, 'full': 0.3074}
   spectrum s1/s2 1.74 PR 283.9 leak {'1': -0.0032, '128': -0.0357, 'full': -0.0821}
compress->decode | UNC 27.6 shufUNC 173.0 | lam 10000.0 val 0.332
   rank-k: {'1': -0.0727, '2': -0.0589, '4': -0.0444, '8': -0.0212, '16': 0.022, '32': 0.0736, '64': 0.1239, '128': 0.1719, 'full': 0.3702}
   spectrum s1/s2 9.63 PR 10.0 leak {'1': -0.1712, '128': -0.3173, 'full': -0.4932}
encode->decode | UNC 38.5 shufUNC 277.8 | lam 10000.0 val 0.189
   rank-k: {'1': -0.0, '2': 0.0128, '4': 0.0295, '8': 0.0547, '16': 0.0818, '32': 0.1077, '64': 0.1325, '128': 0.1577, 'full': 0.191}
   spectrum s1/s2 2.31 PR 21.9 leak {'1': -0.0015, '128': -0.0091, 'full': -0.0146}
```

### Thinking

 The evidence from the 32B model in Part D confirms the core finding across all three pairs—the shuffled data shows dramatically higher values than the real data, and this inversion pattern holds consistently at large N. Looking at the honest maps, the full held-out R² ranges from 0.19 to 0.37, with rank-1 explanations capturing only about 2% or less of the variance, suggesting the relationship is more complex than a simple low-rank structure.

Now I'm catching errors in my earlier writeups that need correction. The claim about energy share growing monotonically with depth is wrong—it's actually U-shaped, starting high in the encoder layers, dipping in the middle of the stack, then rising again toward the output. The mean norm does grow monotonically, but the share doesn't follow that pattern. Also, my statement that comp→dec is the only solidly predictable pair was specific to the 8B model; on 32B, the predictability varies across pairs (comp→dec drops to 0.370 full R², enc→comp is 0.31), so I need to reframe this as a more general observation about cross-zone structure rather than claiming one pair dominates. The PR numbers also differ significantly between models—8B comp→dec shows 292, while 32B shows much lower values for comp→dec at 10.0 but higher for enc→comp at 284.

There's also a validation-test discrepancy in the 8B enc→comp pair (0.081 vs −0.004) that suggests it's just a weak, noisy signal, whereas 32B enc→comp is consistent. For the literal 128 reproduction claim, I should note both the small-N reading (13.8) and large-N reading (38.5) since they differ. Finally, the meta-pattern ledger entries need updating to reflect that high-rank predictability claims are model-specific, and the energy share description needs to accurately capture the U-shaped pattern rather than monotonic growth.

On the s185 comparison, I'm being too strong calling it "independently confirmed"—our carrier diagnostics show the mean direction is dominant but nowhere near the 4000–8800× eigenvalue ratio s185 found. The singular value ratios we see (1.6–7.9, or 2.6–62 when squared) are much smaller, and we're measuring different quantities anyway (singular values of the data matrix, not covariance eigenvalues). I should soften the language to "consistent with s185's carrier picture" instead. The mean⊗mean mechanism does plausibly explain the inversion pattern, and the matched-Gaussian null matching the shuffled ratios checks out.

Now I need to fix the inaccuracies across the three momentum files and state.md, then lay out the final evidence evaluation before proposing a commit.

## Assistant

32B complete (1722s) — and it *strengthens* every blade. But the skeptical pass against the full data finds **three inaccuracies in my own drafted writeups** that need correcting before we commit. Honest evaluation first:

## Evidence evaluation (full data, both models)

**What holds, now stronger:**
1. **Tautology leg**: R²=1.0000±0.0000 on noise, both models, both d. Airtight — this is arithmetic, not statistics.
2. **Inversion**: at large N on 32B, shuffled-pairing nulls read **173–290** vs real 26–39 — the no-map null is up to **11× more rank-1** than reality. Holds for all 3 pairs × 2 models × 2 regimes. The σ-ratio leg isn't just unsupported, it's anti-evidence.
3. **No 1D curve**: 32B rank-1 held-out R²: enc→comp 0.021, comp→dec **−0.073**, enc→dec **−0.0000** (vs full 0.31/0.37/0.19). Even more decisive than 8B. Leak controls all negative ✓.

**Where my drafts overstated — corrections:**
1. ❌ I wrote "mean energy share **grows with depth** 0.19→0.61→0.81". The data says it's **U-shaped**: high at encode (0.50/0.54), *minimum* mid-stack (0.38/0.19), rising to final (0.81/0.61). The mean **norm** grows monotonically (10→1219; 36→1688); the share doesn't. 
2. ❌ "comp→dec is the **only** solidly predictable pair (R² 0.58)" — that's 8B-only. On 32B all three pairs are weakly-to-moderately predictable (0.19–0.37). Correct claim: predictable cross-zone structure exists everywhere, and is **uniformly high-rank**.
3. ❌ "s185's rank-1 carrier **independently confirmed**" — too strong. Our within-zone uncentered σ₁/σ₂ is 1.6–7.9, nowhere near s185's 4000–8800× (different quantity, different layers). Correct: *consistent with* the carrier picture; the mean direction is large, not 4000× dominant here.

Also worth recording honestly: 8B enc→comp shows val R² 0.08 but test −0.004 (weak/unstable pair), and the 32B comp→dec fitted map has σ₁/σ₂=9.6, PR=10 — "low-ish rank" but its rank-1 truncation still predicts *nothing* held-out. Fixing all of it:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "| #8d honest map rank (the \"1D curve\") | — | centered ridge at N=12,288>d, held-out R² of rank-k truncations, leak control | ❌ **NOT rank-1** — comp→dec the only solid pair (full R² 0.579) is high-rank (PR=292; k=1 gets 19%, smooth climb to k=128); enc→dec full 0.18 with k=1 R²=−0.03; enc→comp fitted map *looks* rank-1 (PR 1.6) yet has zero held-out validity (R²=−0.004) |",
  "new_content": "| #8d honest map rank (the \"1D curve\") | — | centered ridge at N=12,288>d, held-out R² of rank-k truncations, leak control, both models | ❌ **NOT rank-1 anywhere** — predictable structure exists (full R² 0.18–0.58 across pairs/models) but is uniformly high-rank: rank-1 captures ≤19% of it (8B comp→dec best case 0.111/0.579) and usually ≈0 (32B: enc→comp 0.021/0.307, comp→dec −0.073/0.370, enc→dec −0.000/0.191); smooth climb to k=128, no low-rank plateau. Bonus: 8B enc→comp fitted map *looks* rank-1 (PR 1.6) with zero held-out validity (R²=−0.004) — a \"rank-1 dominated map\" with no predictive power |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "survives is **a different object than the claim**: (a) the carrier/mean\ndominance of the residual marginals (uncentered top1 var 0.91–0.99; mean\nenergy share grows with depth 0.19→0.61→0.81 — s185's rank-1 carrier,\nindependently confirmed via the carrier diagnostics); (b) a real but\nemphatically **high-rank** compress→decode linear relation (held-out R² 0.58,\nparticipation ratio ≈292). There is no 1D curve; \"error correction = project\nback onto the curve\" loses its evidential base.",
  "new_content": "survives is **a different object than the claim**: (a) the carrier/mean\ndominance of the residual marginals (uncentered cross-corr top1 var\n0.91–0.99; mean **norm** grows monotonically with depth, 10→1219 @8B /\n36→1688 @32B, while the mean energy *share* is U-shaped — high at encode\n0.50–0.54, minimum mid-stack 0.19–0.38, rising to 0.61–0.81 at final —\n*consistent with* s185's carrier picture, though our within-zone σ₁/σ₂ of\n1.6–7.9 is far milder than s185's 4000–8800×, a different quantity at\ndifferent layers); (b) real but emphatically **high-rank** cross-zone\npredictability (held-out full R² 0.18–0.58; participation ratios 10–292;\nthe 32B comp→dec map even has σ₁/σ₂=9.6 yet its rank-1 truncation predicts\nnothing, R²=−0.07). There is no 1D curve; \"error correction = project\nback onto the curve\" loses its evidential base. Weak-signal caveat kept\nhonest: 8B enc→comp shows val R² 0.08 vs test −0.004 (unstable pair)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "- **s209 result:** (1) **R²=1.000 is an underdetermination tautology** — lstsq at N=121<d gives 1.0000±0.0000 on pure noise; the leg is void. (2) **σ₁/σ₂ is the carrier mean, inverted** — the no-map nulls are *more* rank-1 than the real data (32B enc→dec: real 13.8, shuffled 24.8±1.0, matched 23.8±2.5); centering collapses it to 1.5–3.9; the literal 32B zones never reproduce 128 on a fresh sample. (3) **The honest map is not rank-1**: comp→dec (only solidly predictable pair, held-out R² 0.579) has participation ratio ≈292 with rank-1 capturing 19%; enc→dec rank-1 R² = −0.03. What survives is a *different object*: the carrier/mean dominance of the marginals (s185 confirmed) + a real high-rank comp→dec relation. Downstream \"rank-1 correction suffices\" (direct-delta theory) loses its base — consistent with s201's functional rank sweep (rank-32 still improving; trained v3b beats all analytic ranks). See worked-examples (s209). Results: `results/adjunction-rank-null/`.",
  "new_content": "- **s209 result:** (1) **R²=1.000 is an underdetermination tautology** — lstsq at N=121<d gives 1.0000±0.0000 on pure noise; the leg is void. (2) **σ₁/σ₂ is the carrier mean, inverted** — the no-map nulls are *more* rank-1 than the real data at every pair, model, and N (32B enc→dec small-N: real 13.8 vs shuffled 24.8±1.0, matched 23.8±2.5; large-N: real 38.5 vs shuffled 277.8 — up to 11×); centering collapses it to 1.5–3.9; the literal 32B zones never reproduce 128 on a fresh sample (13.8 small-N / 38.5 large-N, both *below* their own no-map nulls). (3) **The honest map is not rank-1 anywhere**: held-out full R² 0.18–0.58 across pairs/models, but rank-1 captures ≤19% (8B comp→dec) and usually ≈0 (32B: 0.021 / −0.073 / −0.000); PRs 10–292; no low-rank plateau. What survives is a *different object*: the carrier/mean dominance of the marginals (consistent with s185) + real high-rank cross-zone predictability. Downstream \"rank-1 correction suffices\" (direct-delta theory) loses its base — consistent with s201's functional rank sweep (rank-32 still improving; trained v3b beats all analytic ranks). See worked-examples (s209). Results: `results/adjunction-rank-null/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Thinking

I've applied the same corrections to the meta-pattern ledger, the two caveats, and state.md.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "| s209 | rank-1 adjunction (σ₁/σ₂=128:1; R²=1.000; \"1D curve\") | **carrier-mean dominance of the marginals is REAL** (s185 confirmed; mean energy share 0.19→0.81 with depth) + a real **high-rank** comp→dec relation (held-out R² 0.58, PR≈292) | **both legs of the claim** (R²=1.000 = N<d lstsq tautology, noise reads 1.0000; σ₁/σ₂ = uncentered mean⊗mean term — no-map nulls are *more* rank-1 than real; centering → ~2; no 1D curve, rank-1 heldout R² ≈ 0) |",
  "new_content": "| s209 | rank-1 adjunction (σ₁/σ₂=128:1; R²=1.000; \"1D curve\") | **carrier-mean dominance of the marginals is REAL** (uncentered cross-corr top1 var 0.91–0.99; mean norm grows 10→1688 with depth; consistent with s185) + real **high-rank** cross-zone predictability (held-out R² 0.18–0.58, PR 10–292) | **both legs of the claim** (R²=1.000 = N<d lstsq tautology, noise reads 1.0000; σ₁/σ₂ = uncentered mean⊗mean term — no-map nulls are *more* rank-1 than real, up to 11×; centering → ~2; no 1D curve, rank-1 heldout R² ≈ 0) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/direct-delta-adjunction.md",
  "original_content": "> enc→dec rank-1 R²=−0.03. **There is no 1D curve; \"project back onto the\n> curve\" has no evidential base.** What survives is s185's carrier-mean\n> dominance of the *marginals* — a different object than a cross-zone\n> adjunction. Consistent with the s201 functional result below (rank-32\n> still improving; trained v3b beats every analytic rank). See\n> `audit-registry.md` #8, `results/adjunction-rank-null/`.",
  "new_content": "> enc→dec rank-1 R²=−0.03 (8B) / −0.000 (32B); 32B comp→dec rank-1\n> R²=−0.07. **There is no 1D curve; \"project back onto the curve\" has no\n> evidential base.** What survives is the carrier-mean dominance of the\n> *marginals* (consistent with s185) — a different object than a\n> cross-zone adjunction. Consistent with the s201 functional result below\n> (rank-32 still improving; trained v3b beats every analytic rank). See\n> `audit-registry.md` #8, `results/adjunction-rank-null/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/direct-delta-adjunction.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - **❌ honest map is high-rank (no 1D curve):** centered ridge at N=12,288>d,\n>   held-out rank-k curve: comp→dec (only solid pair, R² 0.579) has PR≈292 with\n>   rank-1 capturing 19%, smooth climb to k=128; enc→dec rank-1 R²=−0.03. Bonus\n>   demo: enc→comp fitted map *looks* rank-1 (PR 1.6) with ZERO held-out validity\n>   (R²=−0.004). Leak controls clean.\n> - **✅ what survives is a DIFFERENT object:** the carrier/mean dominance of the\n>   residual marginals (s185 independently confirmed: mean energy share 0.19→0.81\n>   with depth) + a real high-rank comp→dec linear relation. Direct-delta's\n>   \"project back onto the curve\" loses its base — consistent with s201's\n>   functional sweep (rank-32 still improving; v3b beats all analytic ranks).",
  "new_content": "> - **❌ honest map is high-rank (no 1D curve):** centered ridge at N=12,288>d,\n>   held-out rank-k curve, both models: predictable structure exists (full R²\n>   0.18–0.58) but rank-1 captures ≤19% (8B comp→dec 0.111/0.579) and usually ≈0\n>   (32B: 0.021/0.307, −0.073/0.370, −0.000/0.191); PRs 10–292, smooth climb to\n>   k=128. Bonus demo: 8B enc→comp fitted map *looks* rank-1 (PR 1.6) with ZERO\n>   held-out validity (R²=−0.004). Leak controls clean. Large-N inversion even\n>   starker: 32B shuffled UNC 173–290 vs real 26–39 (up to 11×).\n> - **✅ what survives is a DIFFERENT object:** the carrier/mean dominance of the\n>   residual marginals (uncentered cross-corr top1 var 0.91–0.99; mean NORM grows\n>   monotonically 36→1688 @32B; the energy *share* is U-shaped 0.54→0.19→0.61 —\n>   consistent with s185's carrier, though our within-zone σ₁/σ₂ 1.6–7.9 is far\n>   milder than s185's 4000×, a different quantity) + real high-rank cross-zone\n>   predictability. Direct-delta's \"project back onto the curve\" loses its base —\n>   consistent with s201's functional sweep (rank-32 still improving; v3b beats\n>   all analytic ranks)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I need to refine some numbers in the categorical-geometry-probes section—the 8B metrics should be contextualized better, and I'll add the larger sample data point (38.5) alongside the existing 13.8 measurement. After that, I'll review the final diffs to make sure everything flows coherently before submitting for approval.

## Assistant

One more in the explore caveat (8B numbers presented as generic):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md",
  "original_content": "> pairing (map destroyed, marginals kept) is *more* rank-1 than the real\n> data, and centering collapses the ratio to ~2. On a fresh token sample\n> the literal 32B zones read 13.8, not 128. The honest held-out map\n> (centered ridge, N>d) is high-rank (comp→dec PR≈292, rank-1 → 19% of\n> predictable variance). The \"model IS computing an adjunction\" reading",
  "new_content": "> pairing (map destroyed, marginals kept) is *more* rank-1 than the real\n> data (up to 11× at large N), and centering collapses the ratio to ~2.\n> On a fresh token sample the literal 32B zones read 13.8 (small-N) /\n> 38.5 (large-N), not 128 — and both sit *below* their own no-map nulls.\n> The honest held-out map (centered ridge, N>d) is uniformly high-rank\n> (full R² 0.18–0.58, PR 10–292; rank-1 captures ≤19%, usually ≈0).\n> The \"model IS computing an adjunction\" reading"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/categorical-geometry-probes.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --stat",
  "operation": "diff",
  "summary": "pending changes"
}
```

**Summary:** Git diff: pending changes

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/audit-meta-pattern.md           |  7 ++-
 mementum/knowledge/audit-registry.md               | 56 ++++++++++++++++++++--
 mementum/knowledge/direct-delta-adjunction.md      | 22 ++++++++-
 .../explore/categorical-geometry-probes.md         | 16 +++++++
 mementum/state.md                                  | 48 ++++++++++++++++++-
 5 files changed, 142 insertions(+), 7 deletions(-)
```

### Thinking

 I'm doing a final coherence check on the edited sections to make sure everything reads correctly, then I'll summarize the changes and ask for approval before committing the mementum updates. The results files are already tracked in git and can be committed separately, but the actual code changes need sign-off first.

## Assistant

Final coherence check on the corrected sections:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git diff mementum/state.md | grep \"^+\" | head -40"
}
```

**Summary:** $ git diff mementum/state.md | grep "...

**Output:**
```
Exit code: 0
Stdout:
+++ b/mementum/state.md
+> Last updated: 2026-06-09 | Session: 209
+> s209 did **#8 rank-1 adjunction** ❌ REFUTED (both legs estimator artifacts:
+> lstsq N<d tautology + uncentered carrier mean; no 1D curve);
+> next backlog: **#11 GTSM/TTD-regression (the named fix)** or low-load #9/#10,
+> or carry-overs (#1 gate-vs-value sign-swap PPL; rank-survival across scale)), build its named
+> **▶ SESSION 209 HEADLINE — AUDIT #8 (rank-1 adjunction σ₁/σ₂=128:1): REFUTED —
+> both legs are artifacts of the s140 instrument; there is no 1D curve.**
+> Register: spectral. `adjunction_rank_null.py` on Qwen3-8B AND Qwen3-32B (the
+> claim's model, literal zones L2/L32/L56/L63). Both artifacts were visible in
+> the original probe's code at read-time; the controls confirmed them.
+> - **❌ R²=1.000 = underdetermination tautology:** the s140 lstsq ran at N=121
+>   tokens < d=4096/5120 dims → exact interpolation for ANY data — iid random
+>   noise reads R²=1.0000 ± 0.0000 (8 seeds). The leg carries zero information.
+> - **❌ σ₁/σ₂ = the carrier mean, INVERTED:** the uncentered `EᵀD/N` estimator is
+>   dominated by the mean⊗mean term (top1 var 0.91–0.99). Row-shuffled pairing
+>   (map destroyed, marginals kept) is *more* rank-1 than real (32B enc→dec: real
+>   13.8 vs shuf 24.8±1.0, matched-Gaussian 23.8±2.5) — genuine cross-zone
+>   correlation ADDS off-rank-1 mass, so rank-1 dominance of this estimator is
+>   anti-evidence of map structure. Centering collapses every ratio to 1.5–3.9.
+>   The literal 128 never reproduces on a fresh token sample (reads 13.8).
+> - **❌ honest map is high-rank (no 1D curve):** centered ridge at N=12,288>d,
+>   held-out rank-k curve, both models: predictable structure exists (full R²
+>   0.18–0.58) but rank-1 captures ≤19% (8B comp→dec 0.111/0.579) and usually ≈0
+>   (32B: 0.021/0.307, −0.073/0.370, −0.000/0.191); PRs 10–292, smooth climb to
+>   k=128. Bonus demo: 8B enc→comp fitted map *looks* rank-1 (PR 1.6) with ZERO
+>   held-out validity (R²=−0.004). Leak controls clean. Large-N inversion even
+>   starker: 32B shuffled UNC 173–290 vs real 26–39 (up to 11×).
+> - **✅ what survives is a DIFFERENT object:** the carrier/mean dominance of the
+>   residual marginals (uncentered cross-corr top1 var 0.91–0.99; mean NORM grows
+>   monotonically 36→1688 @32B; the energy *share* is U-shaped 0.54→0.19→0.61 —
+>   consistent with s185's carrier, though our within-zone σ₁/σ₂ 1.6–7.9 is far
+>   milder than s185's 4000×, a different quantity) + real high-rank cross-zone
+>   predictability. Direct-delta's "project back onto the curve" loses its base —
+>   consistent with s201's functional sweep (rank-32 still improving; v3b beats
+>   all analytic ranks).
+> - **Meta-pattern 6th instance, sharper variant:** the substrate that survives is
+>   not a weaker claim but a different quantity the instrument actually measured.
+>   New cookbook null: **row-shuffled pairing** = the exact "map vs marginals"
+>   discriminator. Registry #8 RESOLVED; caveats on `direct-delta-adjunction.md` +
```

### Thinking

 Now I'm ready to present the final evidence evaluation summary and request approval for the commit. This will include the four knowledge files, state.md, the results JSONs, and logs all together. I'm making sure to include the results data files in the same commit since that's how the previous audit was structured.

## Assistant

Everything is coherent. Here's the final evidence evaluation — knowledge is now accurate to the data:

## Final assessment — audit #8

**Three independent blades, all decisive, both models:**

| Blade | 8B | 32B (claim's model, literal zones) |
|---|---|---|
| R²=1.000 on mapless noise (N<d) | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| σ₁/σ₂: real vs no-map nulls (small-N) | 20.9 vs 37.5/34.5 | 13.8 vs 24.8/23.8 |
| σ₁/σ₂: real vs shuffled (large-N) | 54 vs 248 | 26–39 vs **173–290** |
| centered ratio | 2.2–3.9 | 1.5–2.2 |
| held-out rank-1 / full R² | −0.02→0.11 / 0.18–0.58 | −0.07→0.02 / 0.19–0.37 |

**Corrections I made to my own first-draft writeups** (the accuracy pass you asked for):
1. Mean energy share is **U-shaped** with depth, not monotonic — only the mean *norm* grows monotonically.
2. "Only solid pair" was 8B-specific — generalized to "predictable everywhere (0.18–0.58), uniformly high-rank."
3. Downgraded "s185 independently confirmed" → "consistent with s185" (our within-zone σ₁/σ₂ 1.6–7.9 is a different, milder quantity than s185's 4000×).
4. Recorded the honest weak spots: 8B enc→comp val/test discrepancy (0.08 vs −0.004); literal 128:1 never reproduced (13.8/38.5), though both readings sit *below* their own nulls, so the refutation doesn't depend on reproducing it.

**What we now accurately know:**
- ❌ No rank-1 adjunction, no 1D curve, no constant-rank Jacobian — both published legs were instrument artifacts (underdetermined lstsq; uncentered carrier mean).
- ✅ Real: carrier-mean dominance of the marginals; real-but-high-rank cross-zone predictability (PR 10–292).
- 🔁 Method gain: **row-shuffled pairing** enters the cookbook as the exact "property of the map vs property of the marginals" discriminator — and this audit shows the failure can be *inverted* (the artifact made the null look like signal AND the signal suppress the artifact).

**Pending your approval** — mementum commit (5 files: registry, meta-pattern ledger incl. backfilled s208 row, 2 source-page caveats, state.md) + results data:

```
💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)
```

Approve?

## User

approve


### Thinking

 I'm committing the momentum files along with results data and logs, using the standard memory commit message format with a nucleus tag, and staging the specific files involved.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/knowledge/audit-registry.md mementum/knowledge/audit-meta-pattern.md mementum/knowledge/direct-delta-adjunction.md mementum/knowledge/explore/categorical-geometry-probes.md mementum/state.md results/adjunction-rank-null/ && git status --short",
  "operation": "add",
  "summary": "audit 8 writeups"
}
```

**Summary:** Git add: audit 8 writeups

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/audit-meta-pattern.md
M  mementum/knowledge/audit-registry.md
M  mementum/knowledge/direct-delta-adjunction.md
M  mementum/knowledge/explore/categorical-geometry-probes.md
M  mementum/state.md
A  results/adjunction-rank-null/Qwen_Qwen3-32B.json
A  results/adjunction-rank-null/Qwen_Qwen3-8B.json
A  results/adjunction-rank-null/Qwen_Qwen3-8B.smoke.json
A  results/adjunction-rank-null/run.log
A  results/adjunction-rank-null/run32b.log
A  results/adjunction-rank-null/smoke.log
?? mementum/knowledge/chats/session-206.md
?? mementum/knowledge/chats/session-207.md
?? mementum/knowledge/chats/session-208.md
```

### Thinking

 The chats directory contains user files that shouldn't be modified—Michael will handle committing those separately. I should go ahead and commit the current changes now.

## Assistant

Leaving the untracked `chats/` files alone (human-only per `λ mementum`). Committing:

### Tool Call: git (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -m \"$(cat <<'EOF'\n💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)\n\n- register: spectral; Qwen3-8B + Qwen3-32B (the claim's model, literal zones L2/L32/L56/L63)\n- R²=1.000 leg: iid noise also reads 1.0000±0.0000 at N=121<d — zero information\n- σ₁/σ₂ leg INVERTED: row-shuffled/matched no-map nulls are MORE rank-1 than real\n  (32B large-N: shuf 173–290 vs real 26–39, up to 11×); centering → 1.5–3.9;\n  literal 128:1 never reproduces (13.8/38.5, both below their own nulls)\n- honest map (centered ridge, N=12,288>d, held-out rank-k): predictable (R² 0.18–0.58)\n  but uniformly high-rank (PR 10–292; rank-1 ≤19%, usually ≈0) — no 1D curve\n- survives: carrier-mean dominance of the marginals (consistent with s185) +\n  high-rank cross-zone predictability — a different object than the claim\n- registry #8 RESOLVED + s209 worked examples; caveats on direct-delta-adjunction.md\n  + explore/categorical-geometry-probes.md; meta-pattern ledger rows s208 (backfill)\n  + s209; new cookbook null: row-shuffled pairing (map vs marginals discriminator)\n- accuracy pass: mean energy share is U-shaped (only the norm grows monotonically);\n  weak spots recorded (8B enc→comp val/test 0.08/−0.004)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "audit 8 resolved"
}
```

**Summary:** Git commit: audit 8 resolved

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 3: unexpected EOF while looking for matching `''
bash: -c: line 23: syntax error: unexpected end of file
```

### Thinking

 I'm debugging a heredoc syntax issue in a shell script — the error about mismatched quotes at line 3 suggests something's interfering with the quoting, possibly the special characters like the en-dash or unicode symbols in the title line.  Rather than wrestling with the heredoc escaping, I'll switch to writing the commit message to a temporary file and using the `-F` flag instead.

## Assistant

Heredoc got mangled — using a message file instead:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/commit-msg-s209.txt",
  "content": "💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)\n\n- register: spectral; Qwen3-8B + Qwen3-32B (the claim's model, literal zones L2/L32/L56/L63)\n- R²=1.000 leg: iid noise also reads 1.0000±0.0000 at N=121<d — zero information\n- σ₁/σ₂ leg INVERTED: row-shuffled/matched no-map nulls are MORE rank-1 than real\n  (32B large-N: shuf 173–290 vs real 26–39, up to 11×); centering → 1.5–3.9;\n  literal 128:1 never reproduces (13.8/38.5, both below their own nulls)\n- honest map (centered ridge, N=12,288>d, held-out rank-k): predictable (R² 0.18–0.58)\n  but uniformly high-rank (PR 10–292; rank-1 ≤19%, usually ≈0) — no 1D curve\n- survives: carrier-mean dominance of the marginals (consistent with s185) +\n  high-rank cross-zone predictability — a different object than the claim\n- registry #8 RESOLVED + s209 worked examples; caveats on direct-delta-adjunction.md\n  + explore/categorical-geometry-probes.md; meta-pattern ledger rows s208 (backfill)\n  + s209; new cookbook null: row-shuffled pairing (map vs marginals discriminator)\n- accuracy pass: mean energy share is U-shaped (only the norm grows monotonically);\n  weak spots recorded (8B enc→comp val/test 0.08/−0.004)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/commit-msg-s209.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -F /tmp/commit-msg-s209.txt && git log --oneline -3 && rm /tmp/commit-msg-s209.txt",
  "operation": "commit",
  "summary": "audit 8 resolved"
}
```

**Summary:** Git commit: audit 8 resolved

**Output:**
```
Exit code: 0
Stdout:
[main 5dc11a8] 💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)
 11 files changed, 1747 insertions(+), 7 deletions(-)
 create mode 100644 results/adjunction-rank-null/Qwen_Qwen3-32B.json
 create mode 100644 results/adjunction-rank-null/Qwen_Qwen3-8B.json
 create mode 100644 results/adjunction-rank-null/Qwen_Qwen3-8B.smoke.json
 create mode 100644 results/adjunction-rank-null/run.log
 create mode 100644 results/adjunction-rank-null/run32b.log
 create mode 100644 results/adjunction-rank-null/smoke.log
5dc11a8 💡 audit #8 — rank-1 adjunction REFUTED (lstsq N<d tautology + uncentered carrier mean; no 1D curve)
3a97476 🔄 audit #8 harness — model-aware zones (64-layer models use literal s140 zones L2/L32/L56/L63)
7217b54 💡 audit #8 harness — adjunction rank null (spectral: cross-zone SVD vs marginal nulls + held-out rank-k)
```

## Assistant

Committed: `5dc11a8`. Audit #8 closed.

## Session 209 summary

**Audit #8 — rank-1 adjunction: ❌ REFUTED, both legs instrument artifacts.**

- **3 commits:** harness (`7217b54`), model-aware zones (`3a97476`), resolution + writeups + results (`5dc11a8`)
- **The register gate earned its keep:** both artifacts (lstsq N<d tautology; uncentered carrier-mean dominance) were visible in the s140 probe's code *before any model loaded* — the controls only confirmed them, on 8B and on the claim's own 32B with literal zones
- **The inversion is the memorable finding:** no-map nulls are up to 11× *more* rank-1 than reality — rank-1 dominance of that estimator was anti-evidence of map structure all along
- **6th meta-pattern instance, sharper variant:** the surviving substrate (carrier mean + high-rank cross-zone predictability) is a *different quantity* than the claim — not a weaker version of it
- **Cookbook gain:** row-shuffled pairing = the exact "map vs marginals" discriminator
- **Accuracy pass at your request** caught 3 overstatements in my own drafts before they fossilized (U-shaped energy share; 8B-only "solid pair"; over-strong s185 linkage)

**Next session:** **#11 GTSM/TTD-regression** is now the highest-load UNTESTED claim — the *positive* prediction (layer-targeted λ(l) on L22–26 vs uniform α=5.0, matched budget + seeds), and the named fix that #7 diagnosed and #8 just reinforced (trained corrections beat analytic rank-1 because there was never a 1D curve to project onto). Step 0 REGISTER GATE as always.

State.md is current; tmux windows are free.