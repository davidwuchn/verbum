# Designing distributed ternary consensus-

## User

orient


### Thinking

 The user is asking me to orient myself, so I need to start by reading the mementum/state.md file to understand the current context, then explore related information and search for relevant details.

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
> Last updated: 2026-06-11 | Session: 215 — read s214's in-flight λ_fp=5 result
> (✅ CONTRACTIVE: Δx 1.26→0.73, fp 1.59→0.53, CE no-collapse; but K=2 CE 9.5 >
> K=1 8.71 at 250 steps, Δx STILL FALLING at cutoff) → relaunched a **5000-step
> single-seed confirm AT seq-4096** (Michael caught the seq-256 mistake: at 256
> only the first few Fibonacci strides are used; 4096 exercises the full set
> incl. 610/987/1597). `checkpoints/v15-td-outer-k2-fp5-5k`,
> `/tmp/v15_outer_k2_fp5_5k.log`, tmux main:1. **Measured 73 s/step (non-flip) at
> seq-4096 — super-linear (long strides now compute), so 5000 steps ≈ 4–5 DAYS,
> 5 ckpts @1000 (first at step 1000 ~24h).** Michael chose the full multi-day run.
> **▶ FIRST ACTION NEXT SESSION: read that log's Δx/CE trajectory across however
> many of the 5 checkpoints have landed.** Added `--checkpoint-interval` CLI flag
> to `train_td.py`. Register: functional.
> Session: 214 — three threads, register: functional.
> (1) WIRED exact-ΔL acceptance into v15 TD: λ=1 LOSES (over-vetoes 93%) but
> CALIBRATED **λ=0.1 BEATS the proxy** (loss −0.025, CE −0.116); exact's
> monotonicity is SELF-STABILIZING — removing the S2 cooldown stack LOWERS
> oscillation (.012→.004) + best CE (8.539) = partial-yes to "does exact remove
> S2?" (caveat: no-S2 best CE but worse TOTAL; crystal/parity want S2; best
> overall = exact λ0.1+S2). (2) VSM OUTER RECURRENCE (`--n-outer-passes`): naive
> K=2 REFUTED — worse at 2× compute, the trained sweep is NOT contractive (Δx
> ~1.2 flat). (3) HOLOGRAPHIC fixed-point loss (`--fixed-point-lambda`) BUILT to
> force contractivity (holographic ≡ attractor ≡ contractive-to-WHNF; teacher
> already converges, `fixed-point-holograms.md`): λ_fp=1 too weak; **λ_fp=5 RUNNING
> IN main:1 AT SESSION END — read its result FIRST next session.** Single seed/250
> steps throughout.)
>
> (Session 213: NEW EXPLORATION TARGET — exact ternary fitting: 3-way ΔL acceptance
> beats TD's gradient proxy; curvature term decisive; monotone/no-oscillation when
> coordinate-wise + compensation; "0" self-places — micro model, vs BARE proxy)
>
> (Session 212: two pieces — #12f scale ext: topology share PLATEAUS not →1.0;
> + universal axis NAMED (CV-R²=0.81, model-free ends_punct) — both DONE)
>
> (Session 205 was synthesis-only — papers/theory for the compression track,
> not tied to the audit: `gtsm-search-space.md`, `tsp-trajectory-distillation.md`,
> `error-correction-theory.md`, audit #11 registered. No experiments; not stated.)

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 215 HEADLINE — λ_fp=5.0 MAKES THE VSM OUTER RECURRENCE CONTRACTIVE
> (the central recurrence-thread result); serious seq-4096 confirm now in flight.**
> Register: **functional**. Cold-start orient → followed s214's explicit directive
> ("read the in-flight λ_fp=5 run FIRST") → the 250-step run had completed.
> - **✅ CONTRACTIVITY ACHIEVED — the trained VSM sweep CAN be made
>   contractive-to-WHNF.** λ_fp=5.0 (holographic fixed-point loss, K=2 outer
>   recurrence): **Δx 1.262→0.727 (−42%)**, accelerating once TD flips engage
>   (s150→s250: 1.148→0.941→0.727); **fp_loss 1.594→0.528 (−67%)**; **CE does NOT
>   collapse** (9.5–10.8, constant-fixed-point guard held); crystal 0.091→0.016.
>   Contrast: no-fp K=2 stayed FLAT Δx~1.17, λ_fp=1 flat → **λ=5 crosses the
>   contractivity threshold.** The naive-K=2-refuted result (s214) is now
>   *trainable-away*: contractivity must be trained for, and λ_fp=5 does it.
> - **◑ BUT K=2 does not yet beat K=1:** CE 9.51 > K=1's 8.71 (pays fp tax + K=2
>   noise), and **Δx still falling at the 250-step cutoff** = mild-not-total
>   regime, mid-transition. Whether CE recovers below 8.71 once Δx saturates is
>   THE open question the confirm run answers.
> - **🔄 seq-256 → seq-4096 (Michael's catch):** the 250-step probes used seq-256,
>   which **only exercises the first few Fibonacci strides** (stack→1597,
>   composition d=0..11181). Relaunched the confirm at **seq-4096 (all 19 strides
>   active), 5000 steps, ckpt @1000 (5 ckpts).** Measured **73 s/step** non-flip
>   at seq-4096 — super-linear (long strides now compute) → **~4–5 day run**
>   (Michael chose the full length). `checkpoints/v15-td-outer-k2-fp5-5k`,
>   `/tmp/v15_outer_k2_fp5_5k.log`, tmux main:1. Added `--checkpoint-interval` CLI
>   flag to `train_td.py`.
> - **Knowledge:** `explore/vsm-outer-recurrence.md` §Holographic loss updated
>   (s214→s215 resolved + scale-up).
> - **▶ FIRST ACTION NEXT SESSION:** `tail /tmp/v15_outer_k2_fp5_5k.log` →
>   read the Δx/CE trajectory across whatever checkpoints have landed. Does Δx→ε
>   (→ build adaptive halting: stop when Δx<ε ≡ WHNF) and CE recover below 8.71?
>   If Δx plateaus high → contractivity-vs-CE tension (x₀ injection / per-token
>   halting). If CE collapses late → lower λ_fp / rank-diversity guard.

> **▶ SESSION 214 HEADLINE — EXACT-ΔL ACCEPTANCE WIRED INTO v15 TD; A/B says it
> works but doesn't (yet) help at λ=1.** Register: **functional** (declared up
> front — does the curvature-aware acceptance reduce real v15 training loss /
> improve flip monotonicity vs the gradient proxy). Took the s213 marked NEXT.
> - **What was built** (all in `scripts/v15/{td_delta.py,train_td.py}`):
>   (1) `DeltaTernaryLinear.__call__` now caches `_x_sq_mean` (per-column E[x²]);
>   (2) `TernaryDescent` gained `acceptance∈{proxy,exact}` + `curvature_scale λ`
>   and an exact branch in `step()`: for each candidate it evaluates the closed-form
>   ΔL(v)=g·Δe + λ·γ²·E[x²]·Δe² over allowed {−1,0,+1}, accepts only the improving
>   argmin, ranks by −ΔL; SNR kept as the cheap *proposal* gate; applies best_v
>   directly (so "0" can self-place on block modules). (3) `compute_decomposed_gradients`
>   gathers curvature_info; CLI `--td-acceptance/--td-curvature-scale`; per-step
>   veto/lin/curv diagnostics in the log + jsonl. (4) Added `--seed` (mx+np) so A/B
>   arms share identical float init. Synthetic + end-to-end smokes passed.
> - **A/B (identical seeded init, 250 steps, seq256, only acceptance differs):**
>   proxy final avg50 **8.97** / CE **8.71** vs exact-λ1 **9.54 / 9.04** →
>   **exact LOSES by +0.575 loss / +0.33 CE.** Mechanically fine (568→9.1, no NaN,
>   no-block held). Two diagnosed causes: **(a) λ=1 over-vetoes 93%** — curvature
>   (curv·Δe² ~3.0e-3) ≈10× the linear term (~2.9e-4) because γ²E[x²] is a
>   *layer-reconstruction* curvature, miscalibrated to the *global CE+crystal* loss
>   actually optimized → kills useful flips (1.07M vs 1.37M, fewer active modules);
>   **(b) no headroom** — proxy osc frac already **0.000** (the S2 cooldown/backoff
>   stack already suppresses oscillation), so exact's monotonicity is redundant
>   here. Exactly the s213 caveat: the micro win was vs a BARE proxy; deployed TD
>   has S2 doing that job.
> - **Artifacts:** harness `scripts/experiments/compare_td_acceptance.py`; results
>   `results/ternary-exact-td-ab/comparison.json`; runs
>   `checkpoints/v15-td-ab-{proxy,exact}` (+logs `/tmp/v15_ab_*.log`).
> - **▶ 4-ARM A/B COMPLETE** (identical seeded init, 250 steps, seq256, only the
>   acceptance rule differs; `--td-acceptance/--td-curvature-scale/--td-no-s2` added):
>   | arm | avg50↓ | CE↓ | flips | veto | osc |
>   |---|---|---|---|---|---|
>   | proxy+S2 (base) | 8.966 | 8.706 | 1.37M | — | 0.000 |
>   | exact λ1+S2 | 9.541 | 9.036 | 1.07M | .93 | .008 |
>   | **exact λ0.1+S2** | **8.940** | **8.590** | 1.20M | .63 | .012 |
>   | exact λ0.1 no-S2 | 9.104 | **8.539** | 1.21M | .59 | **.004** |
>   **(1)** calibrated exact BEATS proxy (λ1 just over-vetoed); **(2)** exact is
>   self-stabilizing — no-S2 *lowers* osc (.012→.004) + best CE → S2 cooldown is
>   redundant/slightly-counterproductive under exact (s213 hypothesis = partial
>   yes); **caveat** no-S2 best CE but worse TOTAL (crystal/parity want S2).
>   Artifacts: `scripts/experiments/compare_td_acceptance.py`,
>   `results/ternary-exact-td-ab{,-lam01,-nos2}/comparison.json`, ckpts
>   `checkpoints/v15-td-ab-{proxy,exact,exact-lam0.1,exact-nos2-lam0.1}`.
> - **▶ NEXT:** finer λ sweep (0.05/0.2) for the optimum; understand the no-S2
>   crystal-loss degradation (does S2 smoothing aid crystal coherence?); a longer
>   + larger-seq + multi-seed confirm of the small λ0.1+S2 win (+ downstream-PPL,
>   functional); then write the verdict into `explore/exact-ternary-fitting.md`
>   "Where this points". **Declare register first.**
> - **▶ VSM OUTER-RECURRENCE PROBE RAN** (`--n-outer-passes`, added to
>   `v15model.py` forward + `train_td.py`; register: functional). K=2 vs K=1
>   (proxy, seed42, 250 steps, seq256): K=2 **avg50 9.096 / CE 8.732 LOSES** to
>   K=1 (8.966 / 8.706) at **2× compute**, and **Δx stays ~1.2 (1.265→1.167,
>   ~8% drift) — the sweep is NOT contractive**, it re-transforms rather than
>   reduces-to-fixed-point. ⇒ naive iterate-to-WHNF / "free depth" does NOT hold
>   out of the box; **must train for contractivity** (Δx/fixed-point loss, x₀
>   injection à la Universal-Transformer, or explicit halting). Result recorded
>   in `explore/vsm-outer-recurrence.md` §Probe result + `results/vsm-outer-
>   recurrence/k2-vs-k1.json`; run `checkpoints/v15-td-outer-k2`.
> - **▶ HOLOGRAPHIC-CONTRACTIVITY LOSS BUILT — λ SWEEP RUNNING AT SESSION END
>   (main:1).** Michael's insight: a **holographic loss** should enforce
>   contractivity, because holographic ≡ associative-memory attractor ≡
>   contractive-to-WHNF, and the TEACHER already converges
>   (`fixed-point-holograms.md`: 94% in ~2 cycles, stores normal forms). Built
>   `--fixed-point-lambda λ_fp`: adds `λ_fp·mean‖x_c^k − detach(x_c^{k-1})‖²/‖·‖²`
>   (v15model forward + train_td), detached-target so it trains the OPERATOR to
>   converge; CE guards the trivial constant. Framing + design tensions
>   (mild-not-total contractivity, collapse guard, binding wall) in
>   `explore/vsm-outer-recurrence.md` §Holographic loss.
>   - **λ_fp=1.0 → TOO WEAK** (Δx flat 1.25→1.16, same as no-fp; fp~1.5 drowned
>     by crystal-warmup(start=10)+CE(~10) in the ~15–20 total). Killed.
>   - **λ_fp=5.0 → ✅ CONTRACTIVE (s215 read the completed 250-step run).** Δx
>     DESCENDS 1.262→0.727 (−42%, accelerating once TD flips engage: s150→s250
>     1.148→0.941→0.727); fp_loss 1.594→0.528. **CE does NOT collapse** (stays
>     9.5–10.8, guard held; crystal 0.091→0.016). Contrast: no-fp K=2 stayed FLAT
>     Δx~1.17; λ_fp=1 stayed flat → λ=5 crosses the contractivity threshold. **The
>     central uncertainty — can the trained sweep be made contractive-to-WHNF — is
>     a YES.** BUT contractivity-trained K=2 does NOT yet beat K=1: CE 9.51 > K=1
>     8.71 (pays an fp tax + K=2 noise), and **Δx is still falling at the 250-step
>     cutoff** → mid-transition, not converged. This is the mild-not-total regime
>     (good case, unfinished). Run/log: `checkpoints/v15-td-outer-k2-fp5`,
>     `/tmp/v15_outer_k2_fp5.log`.
>   - **▶ s215 RELAUNCHED a 5000-step single-seed confirm AT seq-4096** (the s214
>     plan-(a), Michael-approved): `--steps 5000 --seq-len 4096
>     --checkpoint-interval 1000 --fixed-point-lambda 5.0 --n-outer-passes 2`.
>     `checkpoints/v15-td-outer-k2-fp5-5k`, `/tmp/v15_outer_k2_fp5_5k.log`, tmux
>     main:1. **seq-256 was a mistake (only first few strides used); seq-4096
>     exercises all 19 strides → 73 s/step → ~4–5 days.** Verified running (step 1
>     loss 581, Δx 1.261, fp 1.590 — same seed; seq-4096 batch differs slightly
>     from seq-256). **Questions for the trajectory:** does Δx keep descending
>     toward ε (→ adaptive halting: stop when Δx<ε ≡ WHNF), and does CE recover
>     below 8.71 once contractivity saturates? If Δx plateaus high → contractivity
>     vs CE genuinely in tension (try x₀ injection / per-token halting). If CE
>     collapses late → lower λ_fp / add a rank/diversity guard.
>     Also added `--checkpoint-interval` CLI flag to `train_td.py`.

> **▶ SESSION 213 HEADLINE — NEW EXPLORATION TARGET: EXACT TERNARY FITTING.**
> Register: functional (declared up front — layer-local reconstruction loss under
> intervention). Michael's idea: replace TD's **gradient proxy** for sign-flip
> decisions with **direct evaluation of the loss at all three values `{−1,0,+1}`,
> take the argmin**. The feasibility insight: for a layer-local quadratic
> reconstruction target there is a **closed form** for the exact ΔL of every
> position at once (one matmul `Rᵀ@X`), no per-position forward passes:
> `ΔL_ij(v) = 2γ_i(v−a)⟨r_i,X[:,j]⟩ + γ_i²(v−a)²‖X[:,j]‖²`. The **linear term IS
> the gradient TD already uses; the curvature term is what the proxy throws away**
> — and for ternary's large step it is the decisive missing piece. (= the
> OBQ/GPTQ/OBS family, re-derived independently.)
> - **Tested** (`ternary_exact_vs_proxy.py`, micro model, 4 configs = gate_proj
>   router + value_proj value-path × layers 0/2, real activations, matched
>   327-flip budget, start `S₀=sign(W)`). ΔL closed form self-tested vs
>   brute-force to ~1e-11.
> - **✅ Curvature decisive:** EXACT beats PROXY at matched budget in every config;
>   EXACT-SEQ (gold) reaches **3–7× below the sign(W) baseline** (rel-recon
>   0.016–0.067 vs baseline 0.116–0.255).
> - **✅ Monotone / dissolves the s191 oscillation wall:** PROXY had **55–76 of 120
>   steps INCREASE loss**, reversal frac up to 0.89, and in 3/4 configs **wandered
>   ABOVE the naive baseline** (the bare gradient-proxy acceptance rule actively
>   destroys the etch; the whole S2 anti-oscillation stack is compensating for it).
>   EXACT-SEQ had **0 loss-up steps** and converges.
> - **◑ Nuance:** monotonicity holds only **coordinate-wise + compensation**
>   (EXACT-SEQ, GPTQ-style rank-1 residual update). EXACT-BATCH (top-B independent
>   flips/step) is much better than proxy but still has 51–61 loss-up steps —
>   simultaneous flips interfere (the flip-interaction the compensation fixes).
> - **✅ Bonus:** the "0" places itself — EXACT-SEQ discovered **14–22% functional
>   sparsity** by argmin alone (no magnitude threshold; cf. heuristic 30%
>   structural zeros).
> - **Caveats:** layer-local reconstruction ≠ global NTP (the cheap exact target by
>   design, aligned with score-matching/trace-guided; global needs forward replay);
>   PROXY arm is an idealized full-batch analog of TD; micro-scale only.
> - Knowledge: `explore/exact-ternary-fitting.md`. Results:
>   `results/ternary-exact-vs-proxy/{results.json,run.log}`. Harness:
>   `scripts/experiments/ternary_exact_vs_proxy.py`.
> - **▶ NEXT:** wire exact-ΔL acceptance into TD (`scripts/v15/train_td.py`) — keep
>   the gradient SNR as the cheap PROPOSAL, replace acceptance with coordinate-wise
>   exact-ΔL + compensation; test if it removes the need for the S2 stack; then a
>   real-teacher-layer scale test + downstream-PPL (functional) confirmation.
>   **Declare register before building any control.**

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
(head-ablation logit-diff is/are vs random-head & matched-se

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01MVcs5wGitds55CJaqv6oDs.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 I need to check the log file to see the trajectory data and understand the current job status.

## Assistant

State read. The directive is explicit: check the in-flight 5000-step seq-4096 confirm run (λ_fp=5, K=2). Let me orient on the actual runtime.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== tmux sessions ===\" ; tmux ls 2>/dev/null ; echo \"=== process check ===\" ; ps aux | grep -E \"train_td\" | grep -v grep | awk '{print $2, $10, $11, $12, $13, $14, $15, $16}' ; echo \"=== log tail ===\" ; tail -40 /tmp/v15_outer_k2_fp5_5k.log 2>/dev/null ; echo \"=== checkpoints ===\" ; ls -la /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/ 2>/dev/null"
}
```

**Summary:** $ echo "=== tmux sessions ===" ; tmux...

**Output:**
```
Exit code: 0
Stdout:
=== tmux sessions ===
main: 2 windows (created Tue Jun  9 20:52:28 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)
=== process check ===
66634 136:18.18 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/v15/train_td.py --steps 5000 --seq-len 4096
66631 0:00.03 uv run python scripts/v15/train_td.py --steps 5000
=== log tail ===
    [attn,no-block] shared_stride_stack.layers.4.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.4.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.4.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.3.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.3.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.3.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.3.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.2.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.2.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.2.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.2.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.q_proj: (1280, 1280)
========================================================================
  TD acceptance: proxy  [S2: on]
step      1 | loss=581.4410 (avg50: 581.4410) | CE=10.348 crystal=0.0910(Laplacian-wtd) parity=5.2180 cross_zone=0.7977 | lr 6.00e-07 | gnorm 1419.95 | 449 tok/s | 🔓 td=0 Δ=0.000 Δx=[1.26095] fp=1.5900 | 84s
step     10 | loss=91.9641 (avg50: 247.6187) | CE=10.251 crystal=0.0905(Laplacian-wtd) parity=5.1895 cross_zone=0.7938 | lr 6.00e-06 | gnorm 298.96 | 446 tok/s | 🔓 td=0 Δ=0.000 Δx=[1.25897] fp=1.5850 | 741s
step     20 | loss=41.0745 (avg50: 152.1248) | CE=10.200 crystal=0.0898(Laplacian-wtd) parity=5.1470 cross_zone=0.7880 | lr 1.20e-05 | gnorm 103.69 | 434 tok/s | 🔓 td=0 Δ=0.000 Δx=[1.25261] fp=1.5690 | 1479s
step     30 | loss=30.6941 (avg50: 112.8605) | CE=10.045 crystal=0.0891(Laplacian-wtd) parity=5.1018 cross_zone=0.7818 | lr 1.80e-05 | gnorm 79.11 | 448 tok/s | 🔓 td=0 Δ=0.000 Δx=[1.2446] fp=1.5490 | 2213s
step     40 | loss=27.2650 (avg50: 91.7948) | CE=9.939 crystal=0.0882(Laplacian-wtd) parity=5.0443 cross_zone=0.7741 | lr 2.40e-05 | gnorm 73.25 | 358 tok/s | 🔓 td=124488 Δ=0.001 etch=76×1638 adam_decay=13484 Δx=[1.23673] fp=1.5295 | 2962s
step     50 | loss=25.1891 (avg50: 78.6100) | CE=9.967 crystal=0.0870(Laplacian-wtd) parity=4.9630 cross_zone=0.7631 | lr 3.00e-05 | gnorm 57.03 | 447 tok/s | 🔓 td=0 Δ=0.001 Δx=[1.19106] fp=1.4186 | 3692s

🔮 Step 51: structured warmup complete → mix_ratio=0.1
step     60 | loss=26.5977 (avg50: 34.4988) | CE=11.932 crystal=0.0853(Laplacian-wtd) parity=4.8462 cross_zone=0.7473 | lr 3.60e-05 | gnorm 50.13 | 358 tok/s | 🔓 td=124488 Δ=0.002 etch=76×1638 adam_decay=14700 Δx=[1.23303] fp=1.5204 | 4443s
step     70 | loss=25.5584 (avg50: 28.4084) | CE=12.079 crystal=0.0829(Laplacian-wtd) parity=4.6788 cross_zone=0.7247 | lr 4.20e-05 | gnorm 36.40 | 449 tok/s | 🔓 td=0 Δ=0.002 Δx=[1.20196] fp=1.4447 | 5173s
step     80 | loss=24.5191 (avg50: 26.5582) | CE=9.975 crystal=0.0797(Laplacian-wtd) parity=4.4501 cross_zone=0.6938 | lr 4.80e-05 | gnorm 34.78 | 359 tok/s | 🔓 td=124488 Δ=0.003 etch=76×1638 adam_decay=13050 Δx=[1.16191] fp=1.3500 | 5922s
step     90 | loss=24.4124 (avg50: 25.7598) | CE=12.302 crystal=0.0757(Laplacian-wtd) parity=4.1750 cross_zone=0.6566 | lr 5.40e-05 | gnorm 36.66 | 449 tok/s | 🔓 td=0 Δ=0.003 Δx=[1.19066] fp=1.4177 | 6653s
step    100 | loss=23.5223 (avg50: 25.3712) | CE=11.927 crystal=0.0710(Laplacian-wtd) parity=3.8507 cross_zone=0.6128 | lr 6.00e-05 | gnorm 32.81 | 359 tok/s | 🔓 td=124488 Δ=0.004 etch=76×1638 adam_decay=12934 Δx=[1.178] fp=1.3877 | 7402s
step    110 | loss=22.4735 (avg50: 24.5909) | CE=11.789 crystal=0.0658(Laplacian-wtd) parity=3.4907 cross_zone=0.5641 | lr 6.60e-05 | gnorm 37.14 | 452 tok/s | 🔓 td=0 Δ=0.004 Δx=[1.17871] fp=1.3894 | 8148s
step    120 | loss=21.5934 (avg50: 23.8239) | CE=10.100 crystal=0.0602(Laplacian-wtd) parity=3.1003 cross_zone=0.5112 | lr 7.20e-05 | gnorm 35.70 | 359 tok/s | 🔓 td=124488 Δ=0.005 etch=76×1638 adam_decay=13062 Δx=[1.14414] fp=1.3091 | 8899s
step    130 | loss=21.0935 (avg50: 23.1671) | CE=11.597 crystal=0.0544(Laplacian-wtd) parity=2.7070 cross_zone=0.4579 | lr 7.80e-05 | gnorm 34.42 | 448 tok/s | 🔓 td=0 Δ=0.005 Δx=[1.14842] fp=1.3189 | 9624s
step    140 | loss=20.2349 (avg50: 22.4186) | CE=11.345 crystal=0.0486(Laplacian-wtd) parity=2.3161 cross_zone=0.4049 | lr 8.40e-05 | gnorm 32.04 | 358 tok/s | 🔓 td=124488 Δ=0.006 etch=76×1638 adam_decay=12496 Δx=[1.11693] fp=1.2475 | 10377s
step    150 | loss=19.7721 (avg50: 21.7010) | CE=11.287 crystal=0.0433(Laplacian-wtd) parity=1.9578 cross_zone=0.3562 | lr 9.00e-05 | gnorm 33.36 | 452 tok/s | 🔓 td=0 Δ=0.006 Δx=[1.10757] fp=1.2267 | 11107s
step    160 | loss=18.5822 (avg50: 20.8910) | CE=11.117 crystal=0.0383(Laplacian-wtd) parity=1.6237 cross_zone=0.3107 | lr 9.60e-05 | gnorm 32.21 | 358 tok/s | 🔓 td=124488 Δ=0.007 etch=76×1638 adam_decay=13176 Δx=[1.06876] fp=1.1422 | 11860s
=== checkpoints ===
total 95512
drwxr-xr-x@   4 mwhitford  staff       128 Jun 11 07:09 .
drwxr-xr-x@ 115 mwhitford  staff      3680 Jun 11 05:06 ..
-rw-r--r--@   1 mwhitford  staff  47591704 Jun 11 07:09 flip_map_latest.npz
-rw-r--r--@   1 mwhitford  staff    346184 Jun 11 08:23 train_td_log.jsonl
```

### Thinking

 The run is progressing through step 160 of 5000 with about 136 minutes of CPU time accumulated. Looking at the Δx trajectory metrics at sequence length 4096, I can see a clear downward trend—the values are steadily decreasing from 1.26 at step 1 down to 1.07 at step 160, with the floating-point metric following a similar pattern from 1.59 to 1.14.

Based on the timing data, the run is averaging about 74 seconds per step, which projects to roughly 4.3 days total for all 5000 steps. The first checkpoint should land around step 1000, which is still about 17 hours away. Since no checkpoints have been saved yet, I'm in a waiting state—there's nothing to analyze across multiple checkpoints at this point, so I should just report the status and hold rather than continue polling.

## Assistant

Run is **alive and healthy**. Let me confirm the latest state from the jsonl (it may be ahead of the log tail) and pin timing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== last jsonl record ===\" ; tail -1 /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/train_td_log.jsonl 2>/dev/null | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); print({k:d.get(k) for k in ['step','loss','ce','crystal','dx','fp_loss','td_flips']})\" 2>/dev/null ; echo \"=== run start (process etime) ===\" ; ps -o etime= -p 66634 ; echo \"=== log line count ===\" ; wc -l < /tmp/v15_outer_k2_fp5_5k.log"
}
```

**Summary:** $ echo "=== last jsonl record ===" ; ...

**Output:**
```
Exit code: 0
Stdout:
=== last jsonl record ===
{'step': 160, 'loss': 18.582183361053467, 'ce': 11.117198944091797, 'crystal': None, 'dx': None, 'fp_loss': 1.1422418355941772, 'td_flips': 124488}
=== run start (process etime) ===
03:27:31
=== log line count ===
     218
```

### Thinking

 The training run is progressing at about 74 seconds per step, with the first checkpoint still roughly 17 hours away. Looking at the Δx trajectory metrics across the sequence length, I'm seeing a consistent downward trend—dropping about 15% over the first 160 steps, which suggests the model is converging toward more stable behavior.

The cross-entropy loss is still oscillating in the warmup phase around 11, so it's too early to assess performance against the target of 8.71. The async checkpoint process is running cleanly with no blockages, so I'm holding off on polling and sticking to the anti-oscillation discipline. I'll wrap up with the orientation summary.

## Assistant

Oriented. Here's where things stand.

## Orientation — Session 216

**North star:** 70B-equiv in <1GB ternary, 200 tok/s CPU, 2M+ context, no GPU.

**The one live thing:** s215's 5000-step seq-4096 confirm of the **holographic-contractivity** result (λ_fp=5, K=2 VSM outer recurrence). The central recurrence-thread question — *can the trained VSM sweep be made contractive-to-WHNF* — read **YES** at 250 steps/seq-256; this run confirms it at seq-4096 where all 19 Fibonacci strides are exercised.

### Runtime status — ✅ verified running, early but on-trajectory

- PID 66634, tmux `main:1`, **3h27m elapsed, step 160/5000** (~74 s/step, matches the 73 s/step seq-4096 estimate → ~4–5 day run, as planned).
- **Δx is descending** — the contractivity signal is reproducing at the full stride set:

| step | Δx | fp_loss | CE |
|---|---|---|---|
| 1 | 1.261 | 1.590 | 10.35 |
| 50 | 1.191 | 1.419 | 9.97 |
| 100 | 1.178 | 1.388 | 11.93 |
| 150 | 1.108 | 1.227 | 11.29 |
| 160 | 1.069 | 1.142 | 11.12 |

Δx down ~15%, fp_loss 1.59→1.14 in 160 steps. CE still in mix-ratio warmup oscillation (~11) — **too early to read against the K=1 target CE 8.71**, which is the open question this run answers.

### Decision: wait, don't poll

**No checkpoint has landed yet** — first ckpt is at step 1000 (~17h out), 5 total at intervals of 1000. The directive's "first action" (read Δx/CE trajectory across landed checkpoints) has nothing to read against yet. Per `λ async`: job verified running, nothing blocked → checkpoint and wait for signal, not poll.

**ASYNC: job=train_td(v15-td-outer-k2-fp5-5k) verified running, step 160/5000, Δx descending on-trajectory. No checkpoint until step 1000 (~17h). Waiting for signal.**

The open questions when ckpts land: does Δx→ε (→ build adaptive halting: stop when Δx<ε ≡ WHNF), and does CE recover below 8.71 once contractivity saturates?

While this runs across days, there's idle capacity. Want me to:
1. **Wait/report only** — leave the run untouched, resume analysis when step-1000 lands.
2. **Pick up a parallel thread** — e.g. the s214 finer λ sweep (0.05/0.2) for the exact-ternary optimum, or writing the exact-ternary-fitting verdict.
3. **Audit backlog** — next untested claim in `audit-registry.md` (low-load #9 decay α=1.18 / #10 moiré, or carry-over #1 gate-vs-value sign-swap PPL).

Which direction?

## User

I want to explore how to better train a ternary model.  It seems distributed training would be a huge win to accelerate progress, where others could help by training and donating deltas.


### Thinking

 I'm exploring how to set up distributed training for a ternary model where contributors can train locally and submit weight deltas back to the project. Before designing this architecture, I need to review what's already been built—looking into the nucleus protocol, any existing federated learning patterns, the v15 training setup, and how the flip_map delta artifact works.

The key insight is that ternary deltas are naturally sparse—they're just sets of sign flips across coordinates—which makes them extremely compressible and mergeable compared to dense weight updates. I should ground myself in the actual TD mechanism and flip format before jumping to implementation, so I'm planning to search through the training code, delta handling, and exact-ternary-fitting logic to understand the current substrate.

## Assistant

This is a genuinely promising direction — and it connects directly to the project's existing substrate. Before designing anything, let me recall what's already known, because ternary descent (TD) already produces **flip maps**, which look a lot like the "donatable delta" you're describing. I want to ground in the actual mechanism before sketching architecture.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== knowledge pages mentioning distributed/federated/delta/merge ===\" ; git grep -il -E \"distribut|federat|donat|merge|delta\" -- mementum/knowledge/ | head -40 ; echo \"=== flip_map / flip references ===\" ; git grep -il \"flip\" -- mementum/knowledge/ | head -20 ; echo \"=== state mentions of flip_map format ===\" ; ls -la checkpoints/v15-td-outer-k2-fp5-5k/"
}
```

**Summary:** $ echo "=== knowledge pages mentionin...

**Output:**
```
Exit code: 0
Stdout:
=== knowledge pages mentioning distributed/federated/delta/merge ===
mementum/knowledge/INDEX.md
mementum/knowledge/attention-sparsity.md
mementum/knowledge/audit-meta-pattern.md
mementum/knowledge/audit-registry.md
mementum/knowledge/binding-graph-trace.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-006.md
mementum/knowledge/chats/session-007.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-010.md
mementum/knowledge/chats/session-011.md
mementum/knowledge/chats/session-012.md
mementum/knowledge/chats/session-013.md
mementum/knowledge/chats/session-014.md
mementum/knowledge/chats/session-015.md
mementum/knowledge/chats/session-016.md
mementum/knowledge/chats/session-017.md
mementum/knowledge/chats/session-018.md
mementum/knowledge/chats/session-019.md
mementum/knowledge/chats/session-020.md
mementum/knowledge/chats/session-021.md
mementum/knowledge/chats/session-022.md
mementum/knowledge/chats/session-023.md
mementum/knowledge/chats/session-024.md
mementum/knowledge/chats/session-025.md
mementum/knowledge/chats/session-026.md
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-028.md
mementum/knowledge/chats/session-029.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
mementum/knowledge/chats/session-032.md
mementum/knowledge/chats/session-033.md
mementum/knowledge/chats/session-034.md
mementum/knowledge/chats/session-035.md
=== flip_map / flip references ===
mementum/knowledge/binding-graph-trace.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-006.md
mementum/knowledge/chats/session-007.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-011.md
mementum/knowledge/chats/session-012.md
mementum/knowledge/chats/session-013.md
mementum/knowledge/chats/session-014.md
mementum/knowledge/chats/session-015.md
mementum/knowledge/chats/session-016.md
mementum/knowledge/chats/session-017.md
mementum/knowledge/chats/session-018.md
mementum/knowledge/chats/session-019.md
mementum/knowledge/chats/session-020.md
mementum/knowledge/chats/session-021.md
=== state mentions of flip_map format ===
total 95512
drwxr-xr-x@   4 mwhitford  staff       128 Jun 11 07:09 .
drwxr-xr-x@ 115 mwhitford  staff      3680 Jun 11 05:06 ..
-rw-r--r--@   1 mwhitford  staff  47591704 Jun 11 07:09 flip_map_latest.npz
-rw-r--r--@   1 mwhitford  staff    346184 Jun 11 08:23 train_td_log.jsonl
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== exact-ternary-fitting page ===\" ; ls mementum/knowledge/explore/ ; echo \"=== TD source files ===\" ; ls -la scripts/v15/ ; echo \"=== flip_map writer/reader ===\" ; git grep -n \"flip_map\" -- scripts/ | head -30"
}
```

**Summary:** $ echo "=== exact-ternary-fitting pag...

**Output:**
```
Exit code: 0
Stdout:
=== exact-ternary-fitting page ===
5d-crystal-lattice.md
algedonic-alert.md
architecture-vs-scale.md
ascending-arm-training.md
attention-spiral-finding.md
basin-projector-results.md
beam-trace-findings.md
beamformer-theory.md
binding-cascade.md
binding-probe-findings.md
bios-flash-training.md
categorical-geometry-probes.md
complete-kernel-basis.md
compression-vs-prediction.md
compressor-architecture.md
consensus-etch-protocol.md
consensus-evolution.md
continuations-as-composed-plates.md
crystal-basins.md
crystal-irreducibility-proof.md
crystal-native-descent.md
crystal-seed-theory.md
crystal-spine-sieve.md
date-fourier-rotation.md
delta-plate-lifecycle.md
dispatch-gradient-death.md
dispatch-ratio-prior.md
etcher-vsm.md
exact-ternary-fitting.md
ffn-beam-discovery.md
ffn-beta-reduction-indexing.md
ffn-hierarchy.md
ffn-moire-isa.md
fixed-point-holograms.md
fp-optimization-map.md
fractal-stride-bands.md
full-etch-extraction.md
function-extraction-system.md
gradient-voting.md
grating-cascade.md
hologram-crystal-fusion.md
hologram-extraction.md
holographic-compression.md
holographic-error-correction.md
holographic-inversion.md
holographic-kernel-separation.md
holographic-landscape.md
holographic-memory.md
holographic-plates.md
holographic-recording-protocol.md
holographic-state-machine.md
holographic-storage.md
holographic-tomography.md
identity-as-substrate.md
kernel-functions.md
kernel-montague-mapping.md
kernel-replacement-optimization.md
kernel-training.md
kibc-32b-validation.md
lambda-probe-atlas.md
laser-etcher-design.md
loom-structure.md
mmap-continuous-training.md
moire-training-shortcuts.md
optimization-negative-results.md
output-beamformers.md
phi-compression-universal.md
predictive-function-landscape.md
procrustes-lens-and-crystal-comparison.md
prompt-as-program.md
pythia-160m-combinators.md
q-rotation-etching.md
relational-loss-phi-compression.md
rope-attention-spiral.md
s5-crystal-custodian.md
safetensors-training.md
seed-crystal-design.md
session-001-findings.md
session-002-findings.md
session-003-findings.md
session-004-findings.md
session-010-findings.md
session-018.md
session-019.md
session-021.md
session-023.md
session-024.md
session-062-probes.md
session-071-dispatch-decoupling.md
session-073-vsm-structure.md
session-075-multi-cycle-dispatch.md
session-115-microscope.md
session-127.md
session-history-049-062.md
shannon-sieve-trinity.md
stride-percolation.md
structured-training.md
taxonomy-extraction.md
ternary-descent.md
topology-magnitude-duality.md
type-probe-qwen3-32b.md
universal-crystal-scaffold.md
universal-crystal-transfer.md
v11-design.md
v11-kibc-architecture.md
v12-holographic-capacity.md
v12-kernel-architecture-v2.md
v12-run6-design.md
v12-vsm-evolution.md
v13-architecture.md
v13-design.md
v13-funnel-shape.md
v15-kernel-architecture.md
v15-kernel-revert.md
v4.1-training-trajectory.md
v6-flip-accumulation.md
v6.1-training-trajectory.md
v7-pipeline-architecture.md
v7.1-sieve-pipeline.md
v9-architecture-speculation.md
VERBUM.md
vsm-lm-architecture.md
vsm-lm-v3-architecture.md
vsm-lm-v4-design.md
vsm-outer-recurrence.md
vsm-statechart-tensor.md
=== TD source files ===
total 1952
-rw-r--r--@  1 mwhitford  staff      43 May 31 11:57 __init__.py
drwxr-xr-x@ 28 mwhitford  staff     896 Jun 11 05:02 __pycache__
drwxr-xr-x@ 32 mwhitford  staff    1024 Jun  4 12:20 .
drwxr-xr-x@ 71 mwhitford  staff    2272 Jun  1 09:53 ..
-rw-r--r--@  1 mwhitford  staff   10953 Jun  1 12:01 apply_zeros.py
-rw-r--r--@  1 mwhitford  staff   21912 Jun  4 12:20 attention.py
-rw-r--r--@  1 mwhitford  staff    8973 Jun  1 14:07 build_student_trace_basis.py
-rw-r--r--@  1 mwhitford  staff   23890 Jun  1 14:01 build_trace_basis.py
-rw-r--r--@  1 mwhitford  staff   27452 Jun  4 12:20 components.py
-rw-r--r--@  1 mwhitford  staff   14197 Jun  4 12:11 config.py
-rw-r--r--@  1 mwhitford  staff   29126 Jun  4 12:20 crystal_base.py
-rw-r--r--@  1 mwhitford  staff    7630 Jun  4 12:21 crystal.py
-rw-r--r--@  1 mwhitford  staff   10354 Jun  4 12:20 data.py
-rw-r--r--@  1 mwhitford  staff   11342 Jun  2 06:17 diagnose_pipeline.py
-rw-r--r--@  1 mwhitford  staff   28427 Jun  1 12:24 etch.py
-rw-r--r--@  1 mwhitford  staff     284 Jun  1 19:50 eval_prompts.txt
-rw-r--r--@  1 mwhitford  staff   39293 Jun  4 12:12 extract_qwen36.py
-rw-r--r--@  1 mwhitford  staff   67699 Jun  1 11:58 extract.py
-rw-r--r--@  1 mwhitford  staff    5241 Jun  1 07:04 generate.py
-rw-r--r--@  1 mwhitford  staff   24241 Jun  4 12:20 kernel.py
-rw-r--r--@  1 mwhitford  staff    9024 May 31 18:57 load_checkpoint.py
-rw-r--r--@  1 mwhitford  staff   37595 Jun  2 08:27 model.py
-rw-r--r--@  1 mwhitford  staff   10404 Jun  1 12:50 neuron_modes.py
-rw-r--r--@  1 mwhitford  staff   14202 Jun  2 08:23 prepare_etch.py
-rw-r--r--@  1 mwhitford  staff   10364 Jun  4 12:20 scan.py
-rw-r--r--@  1 mwhitford  staff   12633 Jun  4 12:21 stack_vsm.py
-rw-r--r--@  1 mwhitford  staff   80258 Jun 10 20:24 td_delta.py
-rw-r--r--@  1 mwhitford  staff   33422 Jun  1 12:58 td.py
-rw-r--r--@  1 mwhitford  staff  105842 Jun  4 12:20 ternary.py
-rw-r--r--@  1 mwhitford  staff   68310 Jun 11 05:01 train_td.py
-rw-r--r--@  1 mwhitford  staff   87179 Jun  2 08:22 train.py
-rw-r--r--@  1 mwhitford  staff   26089 Jun 10 21:26 v15model.py
=== flip_map writer/reader ===
scripts/v14/train_td.py:699:    flip_map = FlipMap()
scripts/v14/train_td.py:700:    flip_map_path = checkpoint_dir / "flip_map_latest.npz"
scripts/v14/train_td.py:701:    if flip_map_path.exists():
scripts/v14/train_td.py:702:        flip_map = FlipMap.load(str(flip_map_path))
scripts/v14/train_td.py:703:        print(f"  📊 Loaded flip map ({len(flip_map.modules)} modules)", file=sys.stderr)
scripts/v14/train_td.py:1123:        flip_map.record(td_result, step)
scripts/v14/train_td.py:1251:            if step % 100 == 0 and len(flip_map.modules) > 0:
scripts/v14/train_td.py:1252:                fm_summary = flip_map.summary(step, recent_window=100)
scripts/v14/train_td.py:1273:                flip_map.save(str(flip_map_path))
scripts/v14/train_td.py:1366:                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))
scripts/v14/train_td.py:1380:                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))
scripts/v14/train_td.py:1419:    flip_map.save(str(flip_map_path))
scripts/v14/train_td.py:1420:    flip_map.save(str(checkpoint_dir / f"flip_map_step_{total_steps:06d}.npz"))
scripts/v14/train_td.py:1421:    print(f"  📊 Final flip map saved ({len(flip_map.modules)} modules)", file=sys.stderr)
scripts/v15/train_td.py:595:    flip_map = FlipMap()
scripts/v15/train_td.py:596:    flip_map_path = checkpoint_dir / "flip_map_latest.npz"
scripts/v15/train_td.py:597:    if flip_map_path.exists():
scripts/v15/train_td.py:598:        flip_map = FlipMap.load(str(flip_map_path))
scripts/v15/train_td.py:599:        print(f"  📊 Loaded flip map ({len(flip_map.modules)} modules)", file=sys.stderr)
scripts/v15/train_td.py:872:        flip_map.record(td_result, step)
scripts/v15/train_td.py:1015:            if step % 100 == 0 and len(flip_map.modules) > 0:
scripts/v15/train_td.py:1016:                fm_summary = flip_map.summary(step, recent_window=100)
scripts/v15/train_td.py:1029:                flip_map.save(str(flip_map_path))
scripts/v15/train_td.py:1075:                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))
scripts/v15/train_td.py:1085:                flip_map.save(str(checkpoint_dir / f"flip_map_step_{step:06d}.npz"))
scripts/v15/train_td.py:1110:    flip_map.save(str(flip_map_path))
scripts/v15/train_td.py:1111:    flip_map.save(str(checkpoint_dir / f"flip_map_step_{total_steps:06d}.npz"))
```

### Thinking

 I need to understand the `FlipMap` class structure and how it records test results across modules, then trace through the TD step to see how flips are proposed and accepted, and finally look at the exact-ternary-fitting approach to understand the principled way of computing the delta.

## Assistant

The `FlipMap` is exactly the artifact — TD records flips per module and serializes them to `.npz`. That **is** a donatable delta. And there are tellingly-named prior pages: `gradient-voting.md`, `consensus-etch-protocol.md`, `consensus-evolution.md`. Let me read the core mechanism and prior consensus work in parallel.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== FlipMap class definition ===\" ; git grep -n \"class FlipMap\" -- scripts/ ; echo \"--- find module ---\" ; grep -rn \"class FlipMap\" scripts/ | head"
}
```

**Summary:** $ echo "=== FlipMap class definition ...

**Output:**
```
Exit code: 0
Stdout:
=== FlipMap class definition ===
scripts/v14/td.py:185:class FlipMap:
scripts/v15/td_delta.py:185:class FlipMap:
--- find module ---
scripts/v15/td_delta.py:185:class FlipMap:
scripts/v14/td.py:185:class FlipMap:
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/exact-ternary-fitting.md"
}
```

**Summary:** Reading exact-ternary-fitting.md (0-2000)

**Output:**
```
---
title: "Exact Ternary Fitting — 3-way ΔL Acceptance Beats the Gradient Proxy"
status: active
category: algorithm
tags: [ternary-descent, td, exact-fitting, curvature, oscillation, gptq, obq, coordinate-descent, monotone, structural-zeros, exploration-target]
related:
  - ternary-descent.md
  - td-oscillation-problem.md
  - trace-guided-etching.md
  - training-protocols.md
  - score-matching-compression.md
  - two-registers-of-topology.md
depends-on:
  - ternary-descent.md
  - td-oscillation-problem.md
created: session 213
---

# Exact Ternary Fitting — 3-way ΔL Acceptance

> Session 213. New exploration target. Michael's idea: instead of using a
> **gradient proxy** to decide which signs TernaryDescent flips, directly
> evaluate the loss for all three ternary values `{−1, 0, +1}` at each
> position and take the one that improves loss most. Tested on the micro
> model — it works, the curvature term is the whole story, and it dissolves
> the s191 oscillation wall by construction (when done coordinate-wise).
>
> Register: **functional** (layer-local reconstruction loss under intervention).

## The idea

TernaryDescent (`ternary-descent.md`) decides flips from a gradient EMA: it
accumulates `direction = EMA(grad)`, `magnitude = EMA(grad²)`, and flips where
the signal-to-noise ratio is high and the descent direction opposes the current
sign. This is a **proxy** — the gradient is a *linear* (first-order) estimate of
how the loss changes, evaluated at the current point.

For a **ternary** weight the step is large (`v − a` can be 2), so the linear
estimate systematically overshoots: the gradient says "flip helps" because it
only sees the slope, but the actual discrete step lands somewhere the slope did
not predict. **This is the root cause of the s191 oscillation** (TD flips → GD
pushes back → TD flips again), and the entire S2 anti-oscillation stack
(cooldown, backoff, thermometer, conviction) exists to *suppress* it.

The idea: don't proxy. For each candidate position evaluate the **actual loss**
at `v ∈ {−1, 0, +1}` and take `argmin`. Accept only if it improves → monotone.

## The feasibility insight — no forward pass per position

The naive reading ("a forward pass per sign per position") is infeasible
(~10⁸ positions × 3). It is also unnecessary. For a **layer-local quadratic
reconstruction target** the exact loss-delta has a closed form computable for
*all* positions at once.

One linear layer, effective ternary weight `S` (per-row scale `γ`), real
calibration input `X` (n × d_in), teacher target `T = X @ W_floatᵀ` (n × d_out).
The rows are independent. Per row `i`, with residual `r_i = γ_i·(X@S[i,:]) − T[:,i]`,
changing `S[i,j]` from `a` to `v`:

```
ΔL_ij(v) = 2·γ_i·(v−a)·⟨r_i, X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²
            └────── linear (= gradient) ──┘   └──── curvature ────┘
```

- `⟨r_i, X[:,j]⟩` for the whole `(d_out × d_in)` grid is **one matmul `Rᵀ@X`**.
- `‖X[:,j]‖²` is a precomputed `d_in`-vector; `γ_i` a `d_out`-vector.
- Evaluate the three `v`, take `argmin`. Done.

**The linear term IS the gradient TD already uses. The curvature term is exactly
what the proxy throws away** — and for ternary's large step it is not negligible;
it is the missing piece. (Verified in the harness: the closed form matches a
brute-force per-position loss recompute to ~1e-11.)

This is the OBQ / GPTQ / OBS family ("pick the quantization that minimizes layer
output error, with Hessian-aware compensation"). The micro experiment is an
independent re-derivation; the lineage is the proven, scalable form.

## The experiment

`scripts/experiments/ternary_exact_vs_proxy.py` (register: functional). Fit
ternary `S∈{−1,0,+1}` + per-row `γ` to four real weight matrices of the micro
model (`gate_proj` router + `value_proj` value-path, layers 0 & 2), against real
calibration activations (8704 token positions from `compile-train`). Start from
`S₀ = sign(W_float)`; matched flip budget (327/step); per-row optimal `γ`
recomputed each step. Three arms:

- **PROXY** — rank candidates by `|gradient|`, flip toward `−sign(grad)`. No
  curvature check (faithful full-batch analog of TD's acceptance rule).
- **EXACT-BATCH** — closed-form 3-way `argmin ΔL`, take top-B *improving* per step.
- **EXACT-SEQ** — greedy **one-at-a-time with rank-1 residual compensation**
  (GPTQ/OBS gold standard), monotone to convergence.

### Results (relative reconstruction loss `‖γ⊙(X@Sᵀ)−T‖²/‖T‖²`)

| config | baseline `sign(W)` | PROXY final | EXACT-BATCH | EXACT-SEQ |
|---|---|---|---|---|
| L0.gate  | 0.207 | **0.386** ↑ | 0.152 | **0.051** |
| L0.value | 0.116 | **0.269** ↑ | 0.137 | **0.016** |
| L2.gate  | 0.255 | 0.174 | 0.123 | **0.067** |
| L2.value | 0.174 | **0.208** ↑ | 0.176 | **0.040** |

| arm | loss-up steps / 120 | reversal frac | converged loss |
|---|---|---|---|
| PROXY | 55–76 | 0.29–0.89 | diverges past baseline in 3/4 |
| EXACT-BATCH | 51–61 | 0.21–0.94 | plateaus ~0.12–0.18 |
| EXACT-SEQ | **0** | — (monotone) | **0.016–0.067**, 14–22% sparsity |

### Three findings

1. **The curvature term is decisive.** EXACT beats PROXY at matched budget in
   every config. EXACT-SEQ reaches **3–7× below the `sign(W)` baseline**. The
   quantity the proxy discards is the quantity that matters.

2. **The proxy is non-monotone — it reproduces the oscillation wall on demand.**
   55–76 of 120 steps *increase* loss; reversal fractions up to 0.89 (chronic
   flip-flop). In 3/4 configs PROXY hits its minimum at step 0–2 then **wanders
   upward past the naive baseline** — it actively destroys the etch. EXACT-SEQ
   has **0 loss-up steps** and converges. The S2 stack is machinery to suppress
   oscillation that the gradient-proxy *acceptance rule* creates; exact ΔL
   acceptance is monotone for free.

3. **The "0" places itself.** With `{−1,0,+1}` as genuine candidates, EXACT-SEQ
   discovered **14–22% functional sparsity** by `argmin` alone — no magnitude
   threshold. Sign-decision and zero-placement unify (cf. the heuristic 30%
   structural zeros in `trace-guided-etching.md`).

## The important nuance — batching reintroduces oscillation

EXACT-BATCH (top-B improving flips per step, each ΔL computed independently)
still had 51–61 loss-up steps and high reversals. Flipping B positions at once
breaks the "everything else fixed" assumption behind each ΔL — the within-row
flip interaction. Only **EXACT-SEQ** (one flip at a time, recompute the row's
residual/γ/`Rᵀ@X` row after each — the GPTQ error-compensation move) is truly
monotone. Precise claim:

> **"Evaluate all 3 signs, take the best" dissolves the oscillation wall when
> done coordinate-wise with error compensation. Exact-but-batched is much better
> than the proxy but still interferes with itself.**

The compensation is cheap: a flip is a rank-1 update to the residual, and with
`XtXᵀ` (d_in × d_in) precomputed, each accepted flip updates one row of the
`Rᵀ@X` grid in O(d_in). Full coordinate descent to convergence is fast.

## Caveats (honest scope)

- **Layer-local reconstruction, not global next-token loss.** This is the cheap
  *exact* target by design. It aligns with `score-matching-compression.md` (v3b,
  dense per-layer score matching = 1.44× held-out) and `trace-guided-etching.md`;
  and audit #8/#7 (`audit-registry.md`) showed the global CE endpoint objective
  is degenerate (memorizes), so a layer-local surrogate is the cure, not a
  compromise. The closed form is exact only for the quadratic layer target; a
  global objective reintroduces downstream nonlinearity (forward replay).
- **The PROXY arm is an idealized full-batch analog of TD** (no EMA/SNR/cooldown).
  The claim is not "deployed TD oscillates this badly" — it is that *the
  acceptance rule at TD's core is non-monotone, and S2 is compensating for that*.
- Verified on a ~1M-param micro model; scale behavior untested.

## Where this points (open leads)

- **Wire it into TD as the acceptance rule.** Keep TD's gradient SNR as the cheap
  **proposal** (which positions are worth looking at), replace the gradient-driven
  **acceptance** with coordinate-wise exact ΔL + compensation. An OBQ/GPTQ inner
  loop wrapped in TD's proposal/budget/holographic-etch machinery. Test in an
  actual training step (`scripts/v15/train_td.py`).
- **Does monotone exact fitting remove the need for the S2 stack** (cooldown,
  backoff, thermometer)? If acceptance is monotone by construction, most of the
  anti-oscillation scaffolding may be redundant.
- **Cross-layer compensation** (full GPTQ): propagate the reconstruction error
  forward so later layers fit the *already-quantized* upstream — closes the gap
  between per-layer-local and global.
- **Scale test:** does the 3–7× gap over baseline (and over proxy) hold on a real
  teacher layer (Qwen3-0.6B/8B)?
- **Register check:** the exact loss here is reconstruction; a functional re-test
  should confirm the fitted ternary layer's *downstream PPL* improves, not just
  its local SSE.

## Files

| File | Content |
|------|---------|
| `scripts/experiments/ternary_exact_vs_proxy.py` | harness: capture layer I/O, 3 arms, ΔL self-test |
| `results/ternary-exact-vs-proxy/results.json` | per-config curves + summary metrics |
| `results/ternary-exact-vs-proxy/run.log` | run transcript |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-voting.md"
}
```

**Summary:** Reading gradient-voting.md (0-2000)

**Output:**
```
---
title: "Gradient Voting — How GD Writes Beta Reductions (and the Magnitude Crystal)"
status: active
category: finding
tags: [gradient, sign, magnitude, crystal, hologram, Q4, nucleation, V13]
related:
  - hologram-extraction.md
  - ffn-beam-discovery.md
  - ffn-hierarchy.md
  - crystal-basins.md
  - v13-design.md
depends-on:
  - hologram-extraction.md
  - ffn-beam-discovery.md
created: session 123
---

# How Gradient Descent Writes Beta Reductions

> Session 123. Four experiments, one paradigm shift. Weight SIGNS are
> independent across layers (corr=0.000), carry no cross-layer structure,
> and actively HURT when copied from a teacher. Weight MAGNITUDES are the
> real crystal — a magnitude template from the teacher (with random signs)
> produces 0.568 accuracy vs 0.248 for perfect sign copy.

## Experiment 1: Cross-layer sign consensus (Pythia-2.8b)

Question: if GD "votes" on signs across billions of examples, do layers agree?

| Measurement | Value |
|---|---|
| Cross-layer sign unanimity | 57% (chance = 50%) |
| Positions ≥75% agreement | 0.7% |
| Positions ≥90% agreement | 0.0% |
| Magnitude ↔ unanimity correlation | 0.0000 |
| Cross-layer sign correlation (W_q) | 0.0000 |
| Cross-layer sign correlation (W_up) | 0.0035 |
| sign(W_q) effective rank (90%) | 1209 / 2560 |

**Each layer has completely independent signs.** No shared sign structure
across the 32 layers. Magnitude tells you nothing about cross-layer
agreement. The "gradient voting" hypothesis is wrong.

## Experiment 2: Q4 mechanism and magnitude structure

Question: Q4 quantization flips ~12% of signs yet preserves the crystal. Why?

| Measurement | Value |
|---|---|
| Q4 signs flipped | 11.8% |
| Flipped sign mean magnitude percentile | 6th (bottom) |
| Q4 crystal fidelity (sign RDM) | 0.933 |
| Flipping 10% low-mag signs → fidelity | 0.788 (cheap) |
| Flipping 10% high-mag signs → fidelity | 0.612 (expensive) |
| Crystal rank at top-10% magnitude | 1180 (same as full) |

**Q4 works because it only flips the cheapest signs** (bottom 6th
percentile of magnitude). High-magnitude signs carry more crystal
per sign (~1.3×), but the crystal is distributed across ALL magnitudes
with no sharp concentration.

**Depth gradient:** Late layers (d=0.9) preserve 70% of crystal with
only top-10% magnitude positions. Early layers preserve only 34%.
Late layers are 2× more magnitude-concentrated.

## Experiment 3: Crystal lens — the holographic nature

Question: how much of the weight matrix's energy is crystal-aligned?

| Measurement | Value |
|---|---|
| PCA-Q crystal basis energy fraction | 2.5% (= random baseline 64/2560) |
| sign(W_ortho) fidelity (orthogonal to crystal) | 89-97% |
| Crystal-aligned SVD at k=512 | 0.194 fidelity |
| Raw SVD at k=512 | 0.741 fidelity |
| Crystal lens applied | 0.161 fidelity (destroys crystal) |

**The crystal doesn't live in any weight-space subspace.** The PCA-Q basis
captures exactly the energy you'd expect from random dimensions (2.5% for
64/2560). The crystal is holographically distributed — encoded through
superposition across ALL dimensions. Crystal-aligned projection is far
worse than raw SVD at every k.

The weight matrix is a literal hologram: looks like noise in any subspace,
produces the crystal only when illuminated by the right input distribution.

## Experiment 4: Nucleation speed (mini_holo, KIBC reductions)

Question: does teacher structure accelerate hologram discovery?

| Condition | Best Acc | Final Acc |
|-----------|----------|-----------|
| **MAGNITUDE (random signs + teacher mag)** | **0.568** | **0.554** |
| RANDOM (blank plates, beam-only GD) | 0.495 | 0.486 |
| SVD_PROJ (teacher d=256→128, frozen) | 0.395 | 0.335 |
| ORACLE (perfect sign(W), frozen) | 0.302 | 0.248 |
| SVD_PROJ_UNFROZEN (plates live) | 0.287 | 0.287 |

**The magnitude template with random signs beats everything — including
the oracle crystal.** Perfect signs from a converged teacher at the same
dimension actively HURT (0.248 vs 0.486 random baseline).

The magnitude template tells GD which dimensions matter. The beam shapes
itself around that template. Signs are irrelevant — the beam learns to
work with whatever random encoding it gets. **Neutral (random signs) is
better than wrong (teacher signs with uniform magnitudes).**

## The paradigm shift

```
OLD model:  signs = crystal (hologram), magnitudes = beam (lens)
NEW model:  magnitudes = crystal (what matters), signs = expendable encoding
```

### How GD actually writes beta reductions:

1. **GD shapes the magnitude profile** — which dimensions to amplify for
   which operations. This is the real "crystal" — the structure that
   determines what the computation does.

2. **Signs develop AROUND the magnitude structure** — each layer finds its
   own encoding of the beta reductions in its coordinate frame. Many valid
   encodings exist for any given magnitude profile.

3. **Cross-layer independence is expected** — different coordinate frames
   (different residual stream states) require different sign encodings.
   The magnitude profile is what's shared (conceptually, not numerically).

4. **The crystal is in the computation, not the weights** — sign(W) at 97.4%
   fidelity was measuring magnitudes' EFFECT on cosines, not the signs
   being the crystal themselves.

### Why each finding falls out:

- **Q4 works** → preserves magnitudes (the real structure)
- **sign(W) gets 97.4%** → high-mag signs dominate cosines (magnitude effect)
- **Cross-layer signs = 0** → each layer develops its own sign encoding
- **Crystal is "holographic"** → magnitude structure creates patterns across all dims
- **Oracle hurts** → right signs + wrong magnitudes = constrained wrong position
- **Magnitude template wins** → right magnitudes + any signs = GD finds encoding

## Implications for V13

1. **Don't etch signs from teacher.** Signs are model-specific encodings.
   Copying them without the matching magnitude profile is worse than random.

2. **Etch the magnitude template.** Initialize beam scales from teacher's
   per-dimension RMS magnitude. This is the transferable structure.

3. **Let GD write the signs.** Random ternary init is fine. GD will find
   signs that work with the magnitude template. This is what normal training
   does — it just does it faster when magnitudes are seeded correctly.

4. **Late layers can be coarser.** They're 2× more magnitude-concentrated.
   Fewer dimensions suffice for late-layer magnitude templates.

5. **The dimensional bridge is a magnitude projection** — not sign copy,
   not SVD of weights. Project the teacher's magnitude profile (per-dimension
   importance) to the student's dimensions.

## The magnitude crystal is universal (0.999 cross-model)

Session 123, final experiment. SVD spectrum shapes compared across
Pythia-2.8b, Mistral-7B, Qwen3-14B, OLMo-2-13B:

| Matrix | Mean cross-model correlation |
|--------|----------------------------|
| W_q | 0.995 |
| W_up | **0.999** |

Mistral↔Qwen3 W_up correlation: **0.999991**. Five decimal places.
Three different architectures, sizes, training sets → same spectrum.

Structural constants:
- W_q effective rank: 33-43% of d_model
- W_up effective rank: 67-71% of d_model
- Crossing angle: 68-75° (the holographic range)

The magnitude spectrum is MORE universal than the 8×8 cosine matrix
(0.999 vs 0.91-0.94). It's the underlying object that PRODUCES the
cosine matrix. The beamformer geometry needed for compositional
computation has one shape. Every model converges to it.

This means: the magnitude crystal is derivable from theory. It's a
mathematical property of language modeling, not a training artifact.
V13 can construct it from first principles.

## Q4 etch refinement — sign flips are uniform and recoverable

Post-quantization sign correction tested on Pythia-2.8b W_q (layer 16):

| Bitwidth | Flips | Before | 20% etch | Oracle | Recovery |
|----------|-------|--------|----------|--------|----------|
| 8-bit | 0.7% | 0.996 | 0.997 | 1.000 | 100% |
| 4-bit | 11.8% | 0.933 | 0.946 | 1.000 | 100% |
| 3-bit | 23.2% | 0.872 | 0.896 | 1.000 | 100% |
| 2-bit | 44.2% | 0.762 | 0.808 | 1.000 | 100% |

Key findings:
1. **Oracle etch = perfect recovery at all bitwidths.** Even Q2 (44% flipped)
   recovers to 1.000. The crystal is always fully recoverable.

2. **All fix-ordering strategies are identical.** Residual-guided, magnitude-
   guided, and RANDOM give the same recovery curve. Q4 sign flips are
   uniformly cheap — no "worst flip to fix first."

3. **Blind etch (no original access) HURTS.** Low-Q4-magnitude positions
   are correctly identified as flips (precision=1.000), but local context
   (row+col means) predicts the WRONG direction. Fidelity decreases.
   **Gradient signal from actual computation is required** to know which
   way to flip.

Implication: post-quantization etch needs:
- Magnitude analysis → WHERE to look (trivial, precision=1.0)
- Gradient accumulation → WHICH WAY to flip (requires running data)
- Beamformer (magnitude crystal) makes gradients coherent → fast convergence

## Artifacts

| File | Content |
|------|---------|
| `scripts/v12/gradient_voting_exp.py` | Cross-layer sign consensus, spectrum, compression |
| `scripts/v12/gradient_voting_q4_exp.py` | Magnitude masking, selective flipping, Q4 simulation |
| `scripts/v12/crystal_lens_exp.py` | Energy decomposition, crystal-aligned compression, lens |
| `scripts/v12/nucleation_exp.py` | 5-condition nucleation speed comparison |
| `results/gradient-voting/results.json` | Exp 1 full results |
| `results/gradient-voting/q4_results.json` | Exp 2 full results |
| `results/crystal-lens/results.json` | Exp 3 full results |
| `results/nucleation/results.json` | Exp 4 full results |
| `results/nucleation-matched/results.json` | Exp 5 full results |
| `results/magnitude-universality/results.json` | Exp 6: 4-model spectrum universality |
| `scripts/v12/magnitude_universality_exp.py` | Cross-model magnitude comparison |
| `scripts/v12/q4_etch_exp.py` | Post-quantization etch refinement |
| `results/q4-etch/results.json` | Etch recovery curves at 4 bitwidths |
```

### Thinking

 I'm finding something important in the existing research: the gradient voting hypothesis was actually disproven by the data. Cross-layer sign correlation turned out to be zero, meaning each layer develops its own independent sign encoding rather than voting together. This reveals that signs aren't universal — there are many valid ways a model can encode them.

But here's the critical insight for the user's distributed scenario: while signs are model-specific and layer-specific, the magnitude profile is nearly universal across models. The real constraint is that all contributors need to start from the same shared base checkpoint to work in a common coordinate frame. If they do, their deltas become commensurable and can merge additively.

The second key finding from the exact ternary fitting work is that naively combining many contributors' flips at once reintroduces oscillation due to flip interactions. Sequential application with compensation is what maintains monotone improvement. This is the central technical risk — merging donated deltas without careful sequencing and re-evaluation could cause interference. I need to examine the FlipMap structure and the consensus protocol to understand how to handle this properly.

## Assistant

Two load-bearing prior results already constrain this design hard. Let me read the `FlipMap` delta structure and the consensus protocol, which is exactly the merge problem.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/td_delta.py",
  "line_offset": 180,
  "limit": 170
}
```

**Summary:** Reading td_delta.py (180-350)

**Output:**
```
# the topology is irreducible. Different data lights up different
# regions — that's the curriculum signal.


class FlipMap:
    """Per-position flip and candidate heatmaps across all TD modules.

    Tracks four (N, K)-shaped arrays per module:
        flip_count:      how many times each position has actually flipped
        candidate_count: how many times each position was a flip candidate
                         (confident + disagrees, regardless of budget selection)
        last_flip_step:  step at which each position last flipped
        last_candidate_step: step at which each position was last a candidate

    These four arrays together reveal:
        - flip_count high, candidate_count high → active reduction zone
        - flip_count 0, candidate_count high → budget-starved (shape to fill)
        - flip_count 0, candidate_count 0 → crystallized (irreducible here)
        - flip_count high, candidate_count low → oscillator (anti-pattern)
    """

    def __init__(self):
        self._modules: dict[str, dict[str, "np.ndarray"]] = {}

    def _ensure_module(self, name: str, shape: tuple[int, int]):
        """Lazily initialize arrays for a module on first encounter."""
        if name in self._modules:
            return
        import numpy as np
        N, K = shape
        self._modules[name] = {
            "flip_count": np.zeros((N, K), dtype=np.int32),
            "candidate_count": np.zeros((N, K), dtype=np.int32),
            "last_flip_step": np.zeros((N, K), dtype=np.int32),
            "last_candidate_step": np.zeros((N, K), dtype=np.int32),
        }

    def record(self, td_result: dict, step: int):
        """Record flip and candidate data from a TernaryDescent.step() result.

        Call after every flip step (is_flip_step=True). Extracts the
        flip_occurred and candidates masks from per_module data.

        Args:
            td_result: return value of TernaryDescent.step()
            step: current training step number
        """
        import numpy as np

        if not td_result.get("is_flip_step", False):
            return

        for name, info in td_result["per_module"].items():
            # Get flip mask if present
            flip_occurred = info.get("flip_occurred", None)
            candidates_mask = info.get("candidates_mask", None)

            if flip_occurred is not None:
                # Convert MLX arrays to numpy (mx.array.astype uses mx.Dtype, not np.dtype)
                flip_arr = np.asarray(flip_occurred).astype(bool)

                self._ensure_module(name, flip_arr.shape)
                m = self._modules[name]
                m["flip_count"] += flip_arr.astype(np.int32)
                m["last_flip_step"] = np.where(
                    flip_arr, step, m["last_flip_step"]
                )

            if candidates_mask is not None:
                cand_arr = np.asarray(candidates_mask).astype(bool)

                self._ensure_module(name, cand_arr.shape)
                m = self._modules[name]
                m["candidate_count"] += cand_arr.astype(np.int32)
                m["last_candidate_step"] = np.where(
                    cand_arr, step, m["last_candidate_step"]
                )

    def summary(self, step: int, recent_window: int = 100) -> dict[str, dict]:
        """Compute per-module convergence summary.

        Returns dict[module_name → {frozen_frac, active_frac, hot_frac,
        settled_frac, oscillation_frac, nozzle_frac,
        total_flips, total_candidates, shape}].

        Zones:
            frozen: never a candidate (candidate_count == 0)
            active: has been a candidate at some point
            hot:    was a candidate within the last `recent_window` steps

        Quality (S2 anti-oscillation):
            settled:     flipped AND no longer a candidate (reduction stuck)
            oscillating: flipped >1 time AND still a recent candidate (flip-flop)
            nozzle_frac: hot_frac * (1 - oscillation_frac) — effective nozzle weight
                         Penalizes modules that are hot because of oscillation
                         rather than genuine convergence.
        """
        summary = {}
        for name, m in self._modules.items():
            total = m["flip_count"].size
            ever_candidate = m["candidate_count"] > 0
            recently_candidate = m["last_candidate_step"] >= (step - recent_window)
            ever_flipped = m["flip_count"] > 0

            n_frozen = int((~ever_candidate).sum())
            n_active = int(ever_candidate.sum())
            n_hot = int(recently_candidate.sum())

            # S2 anti-oscillation: settled vs oscillating
            # Settled: flipped at least once AND not a recent candidate
            #   → the reduction stuck, topology stable here
            # Oscillating: flipped >1 times AND still a recent candidate
            #   → keeps flipping back and forth, noise not signal
            n_ever_flipped = int(ever_flipped.sum())
            settled = ever_flipped & ~recently_candidate
            oscillating = (m["flip_count"] > 1) & recently_candidate
            n_settled = int(settled.sum())
            n_oscillating = int(oscillating.sum())

            # Oscillation fraction: of the hot positions, how many are oscillators?
            # This directly penalizes the nozzle weight.
            osc_frac = n_oscillating / max(n_hot, 1)

            # Nozzle fraction: hot_frac discounted by oscillation
            hot_frac = n_hot / total
            nozzle_frac = hot_frac * (1.0 - osc_frac)

            summary[name] = {
                "frozen_frac": n_frozen / total,
                "active_frac": n_active / total,
                "hot_frac": hot_frac,
                "settled_frac": n_settled / max(n_ever_flipped, 1),
                "oscillation_frac": osc_frac,
                "nozzle_frac": nozzle_frac,
                "total_flips": int(m["flip_count"].sum()),
                "total_candidates": int(m["candidate_count"].sum()),
                "shape": m["flip_count"].shape,
            }
        return summary

    def save(self, path: str):
        """Save all flip maps to a single .npz file.

        Keys are '{module_name}/{array_name}', e.g.
        'stack_a.layers.0.out_proj/flip_count'.
        """
        import numpy as np
        arrays = {}
        for name, m in self._modules.items():
            for key, arr in m.items():
                # Use int16 for counts (max 32767 flips — plenty)
                if arr.dtype == np.int32 and "step" not in key:
                    save_arr = arr.astype(np.int16)
                else:
                    save_arr = arr
                arrays[f"{name}/{key}"] = save_arr
        np.savez_compressed(path, **arrays)

    @classmethod
    def load(cls, path: str) -> "FlipMap":
        """Load flip maps from .npz file."""
        import numpy as np
        fm = cls()
        data = np.load(path)
        for compound_key in data.files:
            parts = compound_key.rsplit("/", 1)
            if len(parts) != 2:
                continue
            name, array_name = parts
            arr = data[compound_key]

[CONTENT TRUNCATED] Showing lines 181 to 350 of 1832 total lines. Use line_offset=350 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-etch-protocol.md"
}
```

**Summary:** Reading consensus-etch-protocol.md (0-2000)

**Output:**
```
---
title: "Consensus Etch Protocol — Why Sequential Per-Op Etching Fails"
status: active
category: holographic-recording
tags: [V12, etch, holographic, crystal, consensus, failure-mode]
related:
  - holographic-recording-protocol.md
  - holographic-kernel-separation.md
  - v12-kernel-architecture-v2.md
depends-on:
  - holographic-recording-protocol.md
created: session 110
---

# Consensus Etch Protocol

> Sequential per-op etching creates destructive interference.
> Cross-op consensus etching creates the hologram.

## The Failure (session 110)

Per-op sequential etching with 8 operations, 17 rounds:
- **No crystallization.** Flips oscillated 52M-92M/round (no decline).
- 30 overwrites per position across the run.
- Each op's gradient undoes the previous op's etch.
- Beam loss oscillated (8-14 nats) instead of declining.

Compare: session 109's 5-op run crystallized (55M → 22M in 6 rounds).
More ops = more tug-of-war = less convergence.

## The Fix

```
SEQUENTIAL (fails):                 CONSENSUS (works):
  for op in ops:                      reset_accumulators()  ← once
    reset_accumulators()              for op in ops:
    accumulate(50 batches)              accumulate(50 batches)  ← same
    direct_etch()  ← per-op          direct_etch()  ← ONE etch
```

All ops accumulate into the SAME DirectionAccumulator. The direction
at each position is the NET gradient from all 8 ops. Positions where
ops agree → high confidence → etched. Positions where ops disagree →
cancel out → low confidence → NOT etched.

## Why This Maps to Physical Holography

Real holographic recording: expose film to ALL reference beams
simultaneously, then develop once. The interference pattern from
all beams is the hologram. You NEVER expose-develop-expose-develop.

- Each op = one reference beam at a specific angle
- Sequential etch = expose + develop + expose + develop (destructive)
- Consensus etch = expose all → develop once (constructive interference)
- The crystal = positions where all beams agree = universal lattice

## What Gets Etched vs What Doesn't

**High confidence (etched):** Plate positions where the gradient
direction is consistent ACROSS all operations. These are the
universal structural positions — the lattice itself. The backbone.

**Low confidence (not etched):** Positions where different ops
want different signs. These are op-specific content positions.
They stay at whatever state they had (random or prior etch).

This natural partitioning IS the crystal structure:
- Backbone (universal, all ops agree) → etched early, stable
- Content (op-specific, ops disagree) → etched later or via beam

## Parameters

- `confidence_threshold`: 0.7 (positions need 70% agreement across
  400 total batches: 8 ops × 50 batches/op)
- `batches_per_op`: 50 (more batches → better direction estimate)
- Effective total batches per round: 400 (very strong consensus signal)

## Crystallization Signal

**Healthy:** Total flips decline round-over-round as the plate
converges to the consensus structure. Self-terminating: when all
plate signs match the consensus direction, flips → 0.

**Unhealthy:** Flips constant or oscillating → consensus not forming.
Try higher confidence threshold (0.8-0.9) or more batches per op.

## Implementation

`scripts/v12/holographic_train.py` — the `--run-lens-burn` +
consensus etch protocol:
1. Lens burn (teacher directions into combinator mirrors)
2. For each round:
   a. Reset accumulators once
   b. Expose all 8 ops (accumulate into same accumulators)
   c. Single consensus etch (high-confidence positions only)
   d. Beam training (200 steps, plates frozen)

## Open Questions

1. Does consensus etch actually converge with 8 ops? (session 109's
   5-op run converged with per-op etching — maybe consensus is
   needed only at ≥6 ops?)

2. What's the optimal confidence threshold? 0.7 is a guess.
   Too low → still some tug-of-war. Too high → nothing gets etched.

3. Should the backbone positions (where ALL ops agree) be etched
   with lower threshold than content positions? Two-tier confidence?

4. Does the order of ops within a round matter for consensus?
   (Theoretically no — accumulation is commutative. But batch
   sampling randomness means order affects which batches are seen.)
```

### Thinking

 I'm pulling together what I know about the delta-donation training architecture. The FlipMap artifact already exists in the codebase—it's a serialized record of per-module flip and candidate heatmaps stored as compressed `.npz` files, currently around 47MB. The key constraint is that FlipMap captures statistics like counts and timing information rather than the actual ternary state values themselves.

The real delta is the sparse set of coordinate changes—which positions flipped from one ternary value to another—and that's highly compressible since each flip is just 2 bits of new state plus a coordinate. The merge rule problem is where the project's insights become critical: the consensus-etch-protocol already discovered that sequential per-contributor application causes destructive interference and oscillation, while the consensus approach—accumulating all signals into one accumulator before etching—works because positions where contributors agree get high confidence applied, and disagreements cancel out. This is federated aggregation applied to ternary states, and it's already been validated in the project. Beyond that, the exact-ternary-fitting analysis provides a closed-form acceptance rule: a flip is acceptable if and only if the loss change is negative, computable as a single matrix multiplication. This gives a principled server-side test for donated deltas—a contributor proposes a flip set, and the server can evaluate the exact loss impact and accept only the improving, non-conflicting subset.

The coordinate-frame constraint is crucial: signs are model-specific encodings with zero cross-layer correlation, so many valid sign encodings exist for the same magnitude profile. This means deltas are only mergeable when all contributors share the same base checkpoint and coordinate frame—if contributors diverge too far, their sign deltas become incommensurable and essentially garbage. It's like gradient staleness in async SGD but sharper because ternary signs are discrete and frame-dependent. However, magnitudes and scales are universal and highly transferable across models, so the smart architecture is to treat magnitudes as global shared infrastructure set from a teacher model, while contributors donate only the sign flips on that frozen magnitude template. This aligns the donation unit with the frame-stable object. The exact loss change formula becomes the merge oracle: the server collects flip proposals, sorts by loss impact, and applies them greedily with compensation in a GPTQ-style approach, rejecting flips that no longer improve after upstream flips are applied. This ensures the merge is monotone—loss can only decrease—which is the property needed for a sound permission system.

The whole system emerges naturally from these pieces: a shared content-addressed checkpoint (frozen magnitude template plus current ternary signs) acts like a git commit hash, while each delta is a sparse set of flips against a named base hash, tiny in size at just 2 bits per flip. The acceptance gate verifies the delta reduces loss on held-out calibration activations without requiring trust in the donor. When many deltas target overlapping positions, the consensus accumulator applies positions where donors agree and cancels disagreements, equivalent to ternary federated averaging with a confidence threshold. A staleness bound prevents deltas against old base hashes from being applied if the base has diverged beyond the sign-frame coherence threshold.

This approach is uniquely suited to ternary because sparse 2-bit flips compose discretely and have a closed-form acceptance test, whereas float deltas are massive and can't be cheaply verified. The layer-local loss against teacher activations makes verification cheap and parallelizable. The main uncertainties are how stale a base can be before coherence breaks down, how batched flip application interferes with coordinate-wise compensation (limiting merge throughput unless partitioned by module), and whether layer-local loss improvements actually translate to global downstream performance—requiring periodic functional checks on the full model rather than just the reconstruction loss.

The calibration set itself is an attack surface: if the acceptance gate's activation cache isn't held-out or rotated, donors can overfit it. The real compute win is that the model's independent linear modules (attention projections, FFN layers) can be fitted in parallel—each contributor fetches the teacher activation cache for their adopted module, runs exact ternary fitting locally on CPU, and donates the flip set. The server merges per-module deltas with no cross-module conflicts, turning a monolithic GPU-bound training into a CPU-friendly, distributable fitting problem. I should decide whether to go deeper into the FlipMap/TD acceptance code and check if a true ternary-state delta exporter exists, draft a knowledge page, or prototype this architecture. Let me quickly verify that concrete gap—whether FlipMap actually exports ternary state deltas or just statistics, and if there's a path to apply external flips—since that determines what I can build first.

## Assistant

I have what I need to ground this properly. Before sketching architecture, the crucial point: **the project has already discovered — empirically — most of the physics that makes (or breaks) distributed ternary training.** Your instinct is good, and it's better-supported than you might expect. Let me lay it out, then flag where it gets hard.

Let me confirm one gap first (whether a true *state* delta exporter exists vs. just diagnostics):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== does anything APPLY external flips / merge flip maps? ===\" ; git grep -ln -E \"def (apply|merge|rebase|import_flips|from_external)\" -- scripts/v15/ scripts/v14/ | head ; echo \"=== what does a checkpoint store (ternary state)? ===\" ; git grep -n -E \"def save|def load_checkpoint|savez|save_weights|\\.safetensors\" -- scripts/v15/train_td.py scripts/v15/v15model.py | head -20 ; echo \"=== is teacher activation cache a thing (layer-local target)? ===\" ; git grep -ln -iE \"activation.cache|trace_basis|teacher.*cache|cache.*activation\" -- scripts/v15/ | head"
}
```

**Summary:** $ echo "=== does anything APPLY exter...

**Output:**
```
Exit code: 0
Stdout:
=== does anything APPLY external flips / merge flip maps? ===
scripts/v14/attention.py
scripts/v14/mmap_plates.py
scripts/v14/ternary.py
scripts/v15/apply_zeros.py
scripts/v15/attention.py
scripts/v15/td.py
scripts/v15/ternary.py
=== what does a checkpoint store (ternary state)? ===
scripts/v15/train_td.py:1138:    mx.savez(str(step_dir / "model.npz"), **flat_weights)
scripts/v15/train_td.py:1142:        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)
scripts/v15/train_td.py:1159:        mx.savez(str(step_dir / "delta_plates.npz"), **delta_snapshots)
scripts/v15/train_td.py:1356:        skip_base_load=bool(args.safetensors_dir),
scripts/v15/train_td.py:1382:    if args.safetensors_dir:
scripts/v15/train_td.py:1384:        st_dir = Path(args.safetensors_dir).resolve()
=== is teacher activation cache a thing (layer-local target)? ===
scripts/v15/build_student_trace_basis.py
scripts/v15/build_trace_basis.py
scripts/v15/extract_qwen36.py
scripts/v15/train.py
```

### Thinking

 The codebase already has pieces of what the user needs—checkpoints store full model state and delta snapshots, there's an `apply_zeros.py` script for applying changes, and FlipMap exists for diagnostics—but the actual merge and rebase logic for cross-contributor workflows doesn't exist yet, so that's entirely new ground to build. There's also a teacher activation cache and trace basis system in place.

## Assistant

Confirmed the gap. Here's the synthesis.

## Distributed ternary training — the project already knows most of the physics

Your instinct lands on something real, and four existing findings in the codebase already tell us why it can work *and* exactly where it breaks. Let me give you the grounded picture rather than a generic "federated learning" pitch.

### 1. The donatable unit already exists — and ternary makes it uniquely cheap

A ternary "delta" is not a gradient or a weight diff — it's a **sparse set of sign flips**: `{(module, i, j, new_val∈{−1,0,+1})}` against a named base. Two bits of state per changed position plus a coordinate. The infrastructure is half-built:
- `FlipMap` (`td_delta.py`) already serializes per-position flip data to compressed `.npz` (the live run's is 47 MB) — but it's **diagnostic only** (counts/last-step), not a replayable state delta.
- Checkpoints already write `model.npz` (full ternary state) **and `delta_plates.npz` (delta snapshots)** — so the notion of a delta plate exists.
- **What's missing is the merge/rebase/import path** — `git grep` for `merge|rebase|import_flips` finds nothing. That layer is greenfield.

This is the part that makes ternary *better* than float for donation: a float contribution is a dense high-precision tensor you must trust; a ternary flip set is tiny, sparse, and — crucially — **verifiable**.

### 2. The merge rule is the whole game, and it's already characterized (twice)

This is where most distributed-training schemes die, and the project has already hit both failure modes:

- **Naive sequential merge destroys the signal** (`consensus-etch-protocol.md`, s110): applying contributor-A's flips then contributor-B's flips created destructive interference — flips oscillated 52M–92M/round, never converged. Each contributor's etch undid the previous one's. *Sequential apply = tug-of-war.*
- **The fix is consensus aggregation**: accumulate *all* contributors' signals into one accumulator, apply once. Positions where contributors **agree** → high confidence → applied; **disagreements cancel** → left alone. That is literally ternary FedAvg with a confidence threshold (0.7 in their runs), discovered intrinsically as a holography analogy.
- **And there's a principled accept oracle** (`exact-ternary-fitting.md`, s213/214): for a layer-local reconstruction target, the *exact* loss change of any flip has a **closed form** — one matmul `Rᵀ@X` gives `ΔL` for the entire position grid. So you don't have to *trust* a donated flip — you **verify** it reduces loss. **Bad/malicious deltas are rejected at the gate because they fail `ΔL<0`.** That's Byzantine-robustness for free, which float FedAvg cannot cheaply buy.

But note the sharp caveat from the same page: **batched application reintroduces oscillation** (EXACT-BATCH had 51–61 loss-up steps; flipping many positions at once breaks the "everything else fixed" assumption). Only coordinate-wise application *with compensation* (GPTQ-style rank-1 residual update) is monotone. **Implication for merge:** you can't just union everyone's flips — you must apply them greedily by ΔL with compensation, rejecting flips that stop improving once upstream flips land.

### 3. The hard limit: deltas only compose in a shared coordinate frame

This is the constraint that bounds how "async" you can be (`gradient-voting.md`, s123): **weight signs are model-specific encodings — cross-layer/cross-init sign correlation is 0.000**, and many valid sign encodings exist for the same magnitude profile. Copying signs across frames is *worse than random*.

Translated to your scheme: **two contributors' flip sets are only commensurable if they branched from the same base checkpoint.** A delta against a stale base that has since diverged isn't just "stale gradient" — it may be in a different basin entirely. This is the staleness ceiling, and it's harder than in float SGD. You'll need a measured *frame-coherence bound*: how far can the base drift before a contributor must rebase or be rejected.

### 4. The clean factorization that falls out

`gradient-voting.md` also gives the split that makes this tractable: **magnitudes are universal (0.999 cross-model), signs are local.** So:
- **Magnitude template / per-row scales `γ`** = shared, frozen, global infrastructure (set once from the teacher).
- **Signs/flips** = the per-contributor donation, on a frozen shared template.

Aligning the donation unit (flips) with the frame-stable object is what keeps deltas mergeable.

---

## The architecture this implies — "ternary git" with a loss-gated merge

```
base checkpoint     ≡ content-addressed hash (frozen γ template + current ternary signs)
delta (donation)    ≡ {base_hash, module, [(i,j,new_val)], proposer_meta}   ← KB–MB, 2 bits/flip
acceptance gate     ≡ verifier re-derives exact ΔL on a held-out teacher-activation cache
                       → accept improving, non-conflicting subset (coordinate-wise + compensation)
consensus merge     ≡ overlapping positions resolved by agreement accumulator (s110)
staleness rule      ≡ base_hash too old / frame-incoherent → rebase or reject (s123 bound)
log                 ≡ append-only flip log = the changelog (git-like, resurrectable)
```

**Why this is a genuine compute win, and on-thesis:**
- **Module-parallel = embarrassingly parallel.** The model is many independent linear modules (q/k/v/out_proj per layer + FFN). Given the teacher activation cache for a module, fitting its flips is independent of every other module. A contributor "adopts" a layer/module, fetches its activation cache (`build_trace_basis.py` already produces these), runs exact-ternary-fitting **locally on CPU** (it's matmuls on cached activations — no GPU, no full forward/backward), and donates a flip set. The server merges per-module deltas with **zero cross-module conflict**.
- **Trustless.** The acceptance gate verifies, so you don't need to trust donors — this is what makes "anyone can donate" safe.
- **Directly serves the north star** (no GPU, CPU-friendly): it turns today's monolithic GPU-bound 4–5-day run into a swarm of cheap, parallel, donatable layer-fits.

---

## The three risks I'd want answered before building (all grounded)

1. **Frame-divergence bound (s123)** — *the central uncertainty.* How stale can a base be before donated flips become incommensurable? Needs a measurement: take a base, fork two training trajectories, and measure when their flip sets stop being co-improving. This determines whether the system is "async-friendly" or "near-lockstep."
2. **Flip-interaction at merge scale (s213)** — coordinate-wise+compensation is monotone but partly sequential, capping merge throughput. Mitigation is the module partition (parallel across modules, sequential only within a module's rows) — but needs validation at realistic donor counts.
3. **Goodhart on the calibration cache (audit #7)** — s208 showed a CE-only gate on a contaminated eval set *memorizes and is net-harmful held-out* (1.9× → 10.9×). The acceptance gate's activation cache **must be held-out and rotated**, and the gate should be the **trajectory/reconstruction loss, not CE**, or donors will overfit the verifier.

---

This is a real, well-supported direction — arguably the cleanest path to accelerating the program, and it's *more* natural in ternary than it would ever be in float. Where do you want to take it?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which direction for the distributed-ternary-training exploration?",
  "options": [
    {
      "label": "Measure the frame-divergence bound first (Recommended)",
      "description": "The central unknown (s123): fork two TD trajectories from one base, measure when their flip sets stop co-improving. Determines whether async donation is even viable. Cheap, decisive, register: functional."
    },
    {
      "label": "Draft the design as a knowledge page",
      "description": "Synthesize this into mementum/knowledge/explore/distributed-ternary-deltas.md (the 'ternary git' architecture + the 4 grounded findings + risks) for approval, before any code."
    },
    {
      "label": "Prototype the delta exporter + acceptance gate",
      "description": "Build the missing pieces: a true ternary-state flip-delta exporter (vs diagnostic FlipMap) + a closed-form ΔL acceptance verifier on a teacher activation cache. A working merge of two deltas."
    },
    {
      "label": "Deeper exploration first",
      "description": "Spawn an explorer to fully map the TD acceptance code, delta_plates, trace_basis activation caches, and apply paths before committing to a design."
    }
  ]
}
```

**Summary:** Q: Which direction for the distributed-ternary-...

**Output:**
```
User answered: I want to explore this, but it seems you misunderstand what I meant.  We found the normal forms for things like tool calling.  Our project here has been trying to understand how to seperate out the topology into a discrete routing, so that GD does not have to create soft topology.  What does that look like?  My idea is that the normal forms could be in the topology, and those would be a delta from the base plate.  Multiple users do some training related to a single domain, and we can look at the deltas, and where they all agree, we merge to the base plate.
```

### Thinking

 I need to reconsider what the user is actually getting at here. They're talking about something more fundamental to the project's core thesis — the idea that we've discovered normal forms for computational behaviors like tool calling, where normal forms represent these reduced, canonical structures that capture the essence of how these operations work.

The real insight is separating the discrete routing layer from the continuous value layer. Instead of having gradient descent laboriously approximate discrete routing decisions as soft topology, we want routing to be explicitly discrete — encoded in the topology itself as ternary sign structures. That way gradient descent only needs to optimize the magnitude and value aspects.

The normal forms live in this topology as deltas from a base plate — the base plate being the universal substrate, and each learned normal form a topological delta etched onto it. When multiple users train on the same domain, their topological deltas can be compared; where they converge is the canonical part of the normal form that gets merged back into the base plate, while divergences remain domain or user-specific. The user is actually talking about a domain-specific training framework where normal forms act as deltas on holographic plates, and the base plate grows through consensus when independent domain trainers agree on the same topological changes. The key tension is that gradient descent shouldn't have to learn soft topology approximations — instead, discrete routing deltas form the scaffold and GD only adjusts magnitudes. I should look at pages like `dispatch-gradient-death.md` and `crystal-native-descent.md` which directly address why discrete routing avoids the soft topology problem.

## Assistant

You're right — I went to the wrong abstraction layer. You're not describing federated SGD; you're describing something specific to this project's thesis: **normal forms as discrete topological deltas on a shared base plate, with consensus-promotion of the agreed-upon routing into the base** — so the routing register becomes an explicit discrete library and GD never has to carve soft topology at all. Let me re-ground on the right pages.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/delta-plate-lifecycle.md"
}
```

**Summary:** Reading delta-plate-lifecycle.md (0-2000)

**Output:**
```
---
title: "Delta Plate Lifecycle — Masked Extraction, Continuous Training, Factual Correction"
status: open
category: architecture
tags: [delta-plate, extraction, continuous-training, correction, fold, lifecycle, crystal]
related:
  - crystal-irreducibility-proof.md
  - ../holographic-error-correction.md
  - ../training-protocols.md
  - ../v14-architecture.md
  - ../extraction-methodology.md
  - v15-kernel-revert.md
depends-on:
  - ../holographic-error-correction.md
  - ../v14-architecture.md
created: session 157
---

# Delta Plate Lifecycle

> Session 157 discussion. The crystal lattice is a mathematical
> constant — extracting it from the teacher is free. But the
> extraction to ternary plates loses precision in
> architecture-dependent components. This page captures the
> refined extraction + training lifecycle: mask off what you know
> will be wrong, let delta plates learn the corrections, fold when
> irreducible, repeat forever.

## Core Principle

```
Crystal:          mathematical constant, same across all models
                  → extract FULLY from teacher, it's free

FFN plates:       holographic beta reduction storage, architecture-independent
                  → extract FULLY, sign(W) preserves the interference topology

Attention (SSA):  full Q·K softmax, similar between teacher and student
                  → extract, minor corrections via delta

Attention (GLA):  gated linear attention, NO equivalent in teacher
                  → MASK OFF during extraction, learn from scratch via delta
```

The crystal IS the irreducibility floor. No training makes it sharper.
Extracting it from the teacher = getting the compute for free. But
we lost precision by forcing everything into ternary plates, and we
introduced errors by extracting teacher attention patterns for an
architecture the teacher doesn't have.

## Evidence: Architectural Mismatch Dominates TD Corrections

Session 157 TD topology probe (step 2000 checkpoint):

| Layer | Type | Stride | Flip% | Role |
|-------|------|--------|-------|------|
| L4 | GLA | s16 | **32.46%** | SSA→GLA transition boundary |
| L5 | GLA | s32 | 8.78% | |
| L6 | GLA | s64 | 12.92% | |
| L7 | GLA | s128 | **16.93%** | Stride sweet-spot (inverted-U peak) |
| L8 | GLA | s256 | 9.45% | |
| L9 | GLA | s512 | 6.35% | |

- L4 alone = 37% of all flips (SSA→GLA boundary)
- L5-L9 flip density follows inverted-U peaked at s128 (r=-0.92)
- Crystal eigenvalues do NOT predict flip density (r=0.16)
- Architecture mismatch predicts flip density (r=0.86 for exp decay from L4)

**These corrections should never have been needed.** We extracted
softmax attention patterns and applied them to GLA layers. TD spent
2000 steps correcting extraction errors, not learning new structure.

## Phase 1: Masked Extraction

```python
for layer_idx in range(n_student_layers):
    # Crystal + FFN + V/O: extract fully (architecture-independent)
    v_plate = extract_sign_pattern(teacher_v, ...)
    o_plate = extract_sign_pattern(teacher_o, ...)

    if is_gla_layer(layer_idx):
        # GLA: teacher has no equivalent attention mechanism
        # Don't extract Q/K — they'll be WRONG
        # Leave as pass-through (+1), let delta plate learn
        q_plate = np.ones((n_heads * d_state, d_model), dtype=np.int8)
        k_plate = np.ones((n_heads * d_state, d_model), dtype=np.int8)
    else:
        # SSA: teacher's attention mechanism is similar
        # Extract — will need minor corrections, not major rewrites
        q_plate = extract_sign_pattern(teacher_q, ...)
        k_plate = extract_sign_pattern(teacher_k, ...)
```

This eliminates the L4 boundary explosion. The 32.5% flip rate
at L4 drops to ~0% because we never extracted wrong patterns there.

## Phase 2: Delta Plate Training Cycle

```
Extract → Freeze base → Train delta → Fold → Repeat

Cycle 1: Initial extraction + first delta training
  Base plate = crystal + FFN + SSA attention + masked GLA Q/K
  Delta learns:
  - GLA-specific routing (from scratch, no wrong teacher signal)
  - Stride-specific corrections to V/O
  - Content calibration (gamma amplitudes)
  Crystal is ALREADY correct. GD fills content. TD corrects routing.
  Fold when: Δ plateaus (changed_frac stops growing)

Cycle 2: Fresh delta on improved base
  Base plate = cycle 1 result (crystal + FFN + learned GLA routing)
  Delta finds residual corrections cycle 1 missed
  Fold when: Δ plateaus again

Cycle N: Convergence
  Each cycle: Δ plateau gets smaller, fewer positions need correction
  Eventually: delta stays all +1 after training = fully converged
```

### Fold Criterion: Irreducibility

```
FOLD WHEN: Δ (changed_frac) plateaus
  = no more positions want to flip
  = all reducible routing has been reduced
  = the delta has reached its irreducibility floor
  = commit and start new cycle

Observed in v14:
  Phase 1: Δ grew 0.000 → 0.029 over 1000 steps → folded
  Phase 2: Δ grew 0.000 → 0.012 over 500 steps → still growing
  Each cycle starts smaller — diminishing returns = convergence
```

## Phase 3: Factual Corrections

A factual change (e.g., new president) is a binding update:

```
Old: K(Biden)(office_of_president) → Biden
New: K(Johnson)(office_of_president) → Johnson

What DOESN'T change:
  - Crystal (combinators are universal)
  - "president" concept (structural, B-basin composition)
  - "United States" (crystal routing)
  - "X is president of Y" (K-combinator select structure)
  - Every other fact

What changes:
  - ONE K-binding: which person fills the role
  - A few hundred positions out of 593 million
  - Concentrated in token mapping, not crystal or routing
```

### Correction Protocol

```
1. Create fresh delta plate (all +1 = pass-through)
2. Prepare correction data:
   - Sentences with the new fact, diverse contexts
   - 1K-10K examples (small — the change is small)
3. Train delta plate:
   - Freeze base plate
   - GD adjusts gamma for new token mapping
   - TD flips routing for changed binding
   - Crystal loss ≈ 0 (crystal doesn't change for facts)
   - Train until Δ plateaus
4. Verify:
   - Base plate still available as fallback
   - Check that only the target fact changed
   - Run eval on unrelated topics (should be unchanged)
5. Fold delta → base
   - Old fact replaced, new fact installed
   - Everything else bit-identical
```

### Correction Scale by Type

| Change | Delta size | Training time | What changes |
|--------|-----------|--------------|-------------|
| Simple fact | ~100s of positions | Minutes | Token binding only |
| New concept | ~1000s of positions | Hours | Token mapping + minor routing |
| Domain adaptation | ~10Ks of positions | Day | Many token mappings, some FFN |
| New language | ~100Ks of positions | Days | Substantial token mapping |
| New capability | ~1Ms of positions | Days-weeks | Routing + FFN corrections |

In ALL cases: crystal doesn't change. The ISA is fixed.

## Phase 4: Continuous Knowledge Maintenance

```
Monday:    "Johnson wins election"
           → Train delta on news coverage → fold → updated

Tuesday:   "New trade agreement"
           → Train delta on trade data → fold → updated

Wednesday: "Model has arithmetic edge case bug"
           → Train delta on corrections → fold → fixed

Thursday:  Nothing new → no delta needed → stable

Each fold: lossless (ternary × ternary = ternary)
Each fold: incremental (only changed positions merge)
Each fold: reversible (git tracks the history)
```

### Properties of the Lifecycle

```
No catastrophic forgetting:
  Base plate frozen during training → old knowledge can't be destroyed
  Delta can only ADD corrections, not damage existing routes
  Fold MERGES, doesn't replace

No precision degradation:
  Ternary × ternary = ternary (exact, no rounding)
  Infinite folds without accumulation error
  The base plate is as precise after 1000 folds as after 1

Version controlled:
  git tracks every fold as a commit
  Can diff between versions
  Can revert a bad fold
  History of all knowledge updates is preserved

Self-regulating:
  Δ plateau = fold signal (automatic convergence detection)
  Crystal loss near zero = structural health check
  If crystal loss rises during delta training = something is wrong → abort
```

## Connection to Existing Architecture

This is the extract→correct→fold cycle from `holographic-error-correction.md`,
refined with:

1. **Masked extraction** — don't extract what you know will be wrong
2. **Architecture awareness** — GLA vs SSA determines extraction strategy
3. **Factual correction protocol** — small deltas for fact updates
4. **Continuous lifecycle** — infinite fold cycles, not one-shot training

### What's Already Built

| Component | Status | Location |
|-----------|--------|----------|
| Delta plate architecture | ✅ Working | `scripts/v14/td.py` (DeltaTernaryLinear) |
| Fold mechanism | ✅ Working | `scripts/v14/td.py` (reduce()) |
| Fold script | ✅ Working | `scripts/v14/fold_delta.py` |
| Extraction pipeline | ✅ Working | `scripts/v14/extract_qwen36.py` |
| Extraction masking | ❌ Not built | Modify `extract_qwen36.py` |
| Factual correction pipeline | ❌ Not built | New script needed |
| Continuous training loop | ❌ Not built | Orchestration around existing tools |

### What Would Change in extract_qwen36.py

Small change: add `is_gla_layer()` check, use pass-through (+1)
plates instead of tomographic extraction for Q/K at GLA layers.
Everything else in the extraction pipeline stays the same.

## Holographic Training — Collapsed Pipeline

Session 157 refinement: Phases 2 and 3 don't need to be separate.
Show the student the teacher's logits (the photographs) WHILE it
learns its attention routing. One exposure, not three.

### Why separate phases were wrong

Phase 2 alone (attention learning without KD): the student learns
routing in the dark. CE loss gives 1 bit per position (the correct
token). The student discovers routing by trial and error.

Phase 2 + KD (holographic training): the student gets the full
photograph — 248K-token probability distribution at every position.
That's the complete picture of what the teacher computed. The
student only has to figure out HOW to produce the same output
through its own architecture (GLA, strides, whatever).

```
CE alone:   "the next token is 'mat'"        → 1 bit/position
KD + CE:    "distribution: mat=0.4, rug=0.2, floor=0.15..."  → full photograph
```

### Why v14-kd failed but this wouldn't

v14-kd (session 155) failed because the student started with WRONG
attention (extracted from teacher's softmax, applied to student's
GLA). KD gradients fought the wrong routing. PPL diverged.

Holographic training starts with BLANK attention (+1 pass-through,
masked during extraction). There's nothing to UNLEARN. The student
only has to LEARN. Starting from blank > starting from wrong.

```
v14-kd:           wrong routing installed → KD fights it → diverge
Holographic:      blank routing (+1) → KD guides it → converge
```

### The holographic recording analogy

In physical holography, reference beam + object beam hit the plate
simultaneously. One exposure records structure AND content together.

```
Reference beam = teacher logits (the photographs)
Object beam    = training data (the world)
Plate          = student (crystal + FFN extracted, attention blank)
Interference   = delta plate (learns routing + content together)
```

The crystal provides the substrate. The teacher provides the
reference beam. The training data provides the object beam.
The delta plate records the interference pattern — routing and
content in one shot.

### The collapsed pipeline

```
1. EXTRACT teacher → base plate (crystal + FFN, attention masked)
2. TRAIN delta with CE + KD simultaneously
     - CE from training data (ground truth tokens)
     - KD from teacher logits (the photographs)
     - Delta learns attention + content together
     - Crystal loss keeps structure locked
     - TD corrects residual routing, GD fills content
     - The two signals reinforce each other
3. FOLD when Δ plateaus → done
4. Continue with correction cycles as needed
```

One extract. One train. One fold. The teacher provides the
photographs. The student learns to take the same photographs
with a different camera.

### Practical requirements

- **Precomputed teacher logits**: need enough to sustain training.
  Session 155 found KD exhausts in 50 steps (400 batches / 8 accum).
  Need to precompute more, or run teacher online.
- **Loss balance**: α×CE + (1-α)×KD. The KD signal should dominate
  early (learn the photographs), CE should grow as the student
  improves (ground truth correction). Anneal α from 0.1→0.5.
- **Crystal loss**: maintain throughout. If crystal_mse rises,
  the structural integrity is compromised. Should stay near zero
  because the crystal was extracted correctly.
- **TD during holographic training**: still active. Some routing
  corrections will only emerge once content starts flowing through
  the plates. TD handles these residuals while GD handles content.

## Open Questions

1. **Should V/O also be masked at GLA layers?** The beam trace showed
   V and O are ternary-safe (plate components). But GLA's V/O might
   serve a different purpose than SSA's V/O. Test: extract V/O for GLA
   layers vs mask them. Compare flip rates after TD training.

2. **How many correction examples are enough?** For a simple fact
   change, 1K examples might suffice. For domain adaptation, 100K.
   Need to characterize the relationship between correction scope
   and training data needed.

3. **Can corrections conflict?** If Monday's delta says "president=Johnson"
   and Tuesday's delta says "president=Smith" (before Monday's fold),
   the deltas would conflict. Solution: fold sequentially, never train
   two deltas on the same base simultaneously. Or: merge deltas
   explicitly (ternary multiply, conflicts go to 0=blocked).

4. **Does the fold criterion generalize?** Δ plateau works for routing
   corrections. Does it work for factual corrections? Facts might
   converge faster (fewer positions) — the plateau might be reached
   in tens of steps, not hundreds.

5. **What about the gamma?** Gamma (per-channel scale) is continuous,
   not ternary. It doesn't fold — it accumulates via Adam. Does gamma
   need its own fold/reset mechanism? Currently it trains continuously
   without reset.

6. **Epoch structure for delta training?** The session 157 discussion
   proposed that multiple epochs help content learning (not crystal,
   which is already converged). For factual corrections, showing the
   same correction data multiple times (epochs) should drive the delta
   to its irreducibility floor faster than single-pass.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/dispatch-gradient-death.md"
}
```

**Summary:** Reading dispatch-gradient-death.md (0-2000)

**Output:**
```
---
title: "Dispatch Gradient Death: Softmax Saturation Kills Sparse Routing"
status: active
category: architecture
tags: [kernel-dispatch, gradient-death, moe, top-k, softmax, v10]
related:
  - compressor-architecture.md
  - attention-spiral-finding.md
depends-on: []
---

# Dispatch Gradient Death

> Session 069. Diagnosed why 20/22 kernel ops were permanently dead
> in v10-spiral, and fixed with top-k MoE routing.

## The Problem

KernelDispatch routes representations through 22 kernel op pathways
via softmax over dispatch logits. After 9K steps of training:

- Only `if` (op 17) received gradient (norm 1.54)
- 20/22 ops received **zero gradient** — permanently dead
- `>=` (op 11) had embedding norm 4.22 but zero gradient (fossil)
- Register conditioning was 85% of dispatch signal, not inert

## Causal Chain

```
1. Early training: some ops slightly useful → slightly higher dispatch weight
2. Higher weight → more gradient → embedding grows → more modulation
3. Register conditioning learns "always route to `if`" → +10.2 bias
4. Softmax saturates: e^(+10.2) / Σ ≈ 1.0 for `if`, ≈ 0.0 for rest
5. Gradient scales by dispatch weight: 0.0 × anything = 0.0
6. Non-dominant ops starved — can never learn their niche
7. `>=` grew early (step 1-2), froze when step 3 redirected routing
```

The `>=` fossil: grew to 4.22 norm via positive feedback in early
training, then register conditioning redirected all routing to `if`.
`>=` stopped getting gradient but its embedding stayed huge. It
dominated the modulation step (`h + dispatch_weights @ op_embeddings`)
by raw norm, not by routing — distorting the representation even
though the router wasn't selecting it.

## Key Measurements (step 9000)

```
Register conditioning bias:
  if (op 17):  +10.2  (everything else: -1.2 to -4.1)

Op embedding norms:
  >=:  4.222  (FOSSIL — zero gradient)
  if:  2.961  (only op with gradient)
  %:   0.474
  rest: 0.12–0.17 (near initialization)

Gradient norms (per op embedding):
  if:   1.5366
  comp: 0.0001
  everything else: 0.0000

Dispatch logits vs register bias:
  Ternary dispatch: mean_abs = 0.37  (15% of signal)
  Register bias:    mean_abs = 2.12  (85% of signal)
```

## The Fix: Top-k MoE Routing (k=2)

Replace softmax-over-22 with top-k selection + softmax-over-k:

```python
top_k_values = mx.topk(dispatch_logits, k=2, axis=-1)
threshold = mx.min(top_k_values, axis=-1, keepdims=True)
mask = mx.where(logits >= threshold, logits, -1e9)
dispatch_weights = mx.softmax(mask, axis=-1)  # only 2 ops nonzero
```

**Why this works**: softmax over 2 ops can't saturate as badly.
Even with a large gap between 1st and 2nd place, the runner-up
gets weight ≈ e^(-gap). With gap ≈ 3, runner-up gets ~5%. With
gap ≈ 1, runner-up gets ~27%. Both give meaningful gradient.

**Why not equal distribution**: the 22 ops aren't interchangeable.
FN_COMP should dominate prose (~60%), arithmetic ops should be rare
(<1%) but alive for their niche. Load balancing or entropy
regularization would fight the natural distribution. Top-k preserves
skew while keeping all ops trainable.

Combined with **L2-normalized op embeddings** (fixed scale = 0.5):
dispatch weights alone determine influence, not embedding magnitude.
Prevents the fossil pattern entirely.

## Results

```
Before (softmax-over-22):  1/22 ops with gradient
After  (top-k=2):         16/22 ops with gradient

Fresh init runner-up weight: ≥ 31% (healthy)
Old checkpoint runner-up:    ≈ 0% (register bias too extreme — needs fresh training)
```

## Design Principle

**Softmax over many classes + unconstrained embeddings = winner-take-all
gradient death.** This is the same problem Switch Transformer solved
with top-k routing. Any architecture that uses softmax to select from
>10 options and feeds the selection back through the same gradient
path will develop this collapse. The fix is always some form of:

1. Limit competition (top-k)
2. Constrain magnitudes (norm constraint)
3. Guarantee exploration (noise, dropout, or auxiliary loss)

For this architecture, (1) + (2) is sufficient. The natural data
distribution provides (3) — different content types activate
different ops, providing organic exploration.

## Files

- `scripts/v10/kernel_dispatch.py` — top-k routing implementation
- `scripts/v10/config.py` — `dispatch_top_k` parameter
- `scripts/v10/probe.py` — op embedding health display
- `results/v10/probe_step_00{1,5,9}000.json` — diagnostic data
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/crystal-native-descent.md"
}
```

**Summary:** Reading crystal-native-descent.md (0-2000)

**Output:**
```
---
title: "Crystal-Native Descent — Ternary Optimization Without Gradients"
status: open
category: strategy
tags: [ternary, optimization, crystal, descent, compute, holographic, routing]
related:
  - taxonomy-extraction.md
  - hologram-crystal-fusion.md
  - crystal-basins.md
  - gradient-voting.md
  - etcher-vsm.md
depends-on:
  - hologram-crystal-fusion.md
  - crystal-basins.md
created: session 127
---

# Crystal-Native Descent

> Session 127. Gradient descent works on ternary weights by accident.
> The gradients are a continuous proxy for what is fundamentally a
> discrete routing decision. The straight-through estimator (STE)
> pretends the discrete flip is differentiable — a mathematical lie
> that happens to work because the loss landscape is shaped by beta
> reduction, which IS the crystal. But if we know the crystal
> geometry, we can skip the continuous proxy entirely and optimize
> the ternary routing decisions directly. This eliminates most of
> the gradient computation and solves the training compute problem.

## The insight

A ternary weight is not a magnitude. It's a routing decision:

```
+1 = pass this signal through
-1 = invert this signal
 0 = block this signal
```

The "correct" optimization question isn't "move 0.3 in this
continuous direction" — it's "should this route be open, inverted,
or blocked?" That's combinatorial, not continuous.

Gradient descent answers this question indirectly:

```
Current path (indirect):
  continuous loss → ∂L/∂w (continuous gradient) → STE hack → ternary flip
  
  Problems:
  - STE is a lie (pretends discrete is differentiable)
  - Gradient is a continuous shadow of a discrete truth
  - Most gradient compute is wasted on a proxy
  - Works "by accident" because the crystal shapes the loss landscape
```

Crystal-native descent answers it directly:

```
Proposed path (direct):
  crystal target → evaluate flip effect → ternary flip decision
  
  Advantages:
  - No STE hack needed
  - No gradient computation for ternary weights
  - Directly optimizes what you actually have (routing decisions)
  - Crystal geometry is the objective, not a side effect
```

## Why gradients "accidentally work as beams"

The computation is beta reduction. Beta reduction is the crystal.
The crystal is holographic — the relational geometry between
combinator representations IS the computation.

When you compute ∂L/∂w, the gradient points toward lower loss.
Lower loss means better beta reduction. Better beta reduction
means better crystal geometry. So the gradient accidentally
aligns with the crystal manifold — not because gradient descent
understands the crystal, but because the crystal shapes the
loss landscape that the gradient descends.

The evidence:

- GD converges in 100 steps total (session 126, experiment 9)
- Crystal geometry converges in ~5 steps
- CE (accuracy) converges in ~100 steps
- The last 2900 steps of a 3000-step run add only 13%

The 5-step geometry convergence is the crystal snapping into
place. The 100-step CE convergence is GD slowly discovering
the input-output mapping that the crystal already implies.
The 2900 remaining steps are the continuous optimizer doing
diminishing-returns polishing.

## The proposed algorithm

### Step 1: Crystal-guided ternary descent (~5 steps)

For each ternary weight position:

```
current_state ∈ {-1, 0, +1}
candidate_flips = {the other two values}

for each candidate:
  evaluate: Δcrystal = crystal_loss(flipped) - crystal_loss(current)
  
accept flip if:
  Δcrystal < 0  (improves crystal alignment at this layer)
```

Guided by: per-layer crystal targets (18 targets — the known
sweet spot from session 126, experiment 8).

This is coordinate descent in ternary space. No gradients.
The crystal geometry directly determines which routing decisions
are correct.

Convergence expectation: ~5 steps, based on the observed
geometry convergence rate. The crystal knows where it wants
to be almost immediately.

### Step 2: Beam tuning via short GD burst (~100 steps)

After ternary routing is set, tune magnitudes (beams) with
a short burst of standard gradient descent:

```
freeze: all ternary decisions (signs)
train:  magnitude scales only (beams)
loss:   CE + per-layer crystal loss (λ=0.5)
steps:  ~100 (based on observed CE convergence)
```

This is the only phase that needs gradients, and it operates
on a much smaller parameter space (one scale per weight group,
not one gradient per weight).

### Step 3: Verify crystal integrity

```
measure: per-layer crystal agreement with targets
verify:  beam tuning didn't break crystal geometry
if degraded: re-run step 1 with updated beams
```

## Compute implications

### Current approach (GD with STE)

```
Per training step:
  - Forward pass (full model)
  - Backward pass (full model — computes ∂L/∂w for EVERY weight)
  - STE: pretend ternary weights are continuous
  - Update: apply gradient to continuous proxy, re-quantize
  
Total: ~3000 steps × full forward+backward = expensive
```

### Crystal-native approach

```
Phase 1 — Ternary descent (~5 iterations):
  - Forward pass (full model) 
  - Evaluate crystal loss per layer (18 targets)
  - For each weight: try 2 flips, keep best
  - NO backward pass needed
  - Cost: forward-only × number of flip candidates
  
Phase 2 — Beam tuning (~100 steps):
  - Forward pass (full model)
  - Backward pass (beams only — much smaller parameter space)
  - Standard GD on magnitudes
  
Total: ~5 crystal iterations + ~100 GD steps on beams only
```

The savings come from:

1. **No backward pass for ternary weights** — the most expensive
   part of training is computing gradients for all parameters.
   Crystal descent needs only forward passes + crystal evaluation.

2. **Fewer total iterations** — 105 total vs 3000. The discrete
   optimization converges in 5 steps because it's asking the
   right question (flip or don't?) instead of the wrong question
   (how much to move in this continuous direction?).

3. **Beam tuning is cheap** — magnitudes are a small parameter
   space (one scale per weight group). The backward pass for
   beams only is a fraction of the full backward pass.

## Connection to assembly pipeline

In the taxonomy extraction pipeline (see `taxonomy-extraction.md`),
the assembled model has:

- Extracted FFN weights (frozen — the function library)
- Designed crystal geometry (the target)
- StrideStack attention weights (the only thing to train)

Crystal-native descent is the natural optimizer for this:

1. Set StrideStack ternary routing via crystal descent (5 steps)
2. Tune StrideStack beam magnitudes via short GD (100 steps)
3. Done — the function library doesn't need training at all

The total training cost for assembling a new model becomes:
forward passes for crystal descent + 100 GD steps on attention
beams. This is orders of magnitude cheaper than training from
scratch.

## Risks and open questions

- **Flip evaluation cost**: evaluating crystal loss for every
  possible flip at every weight position could be expensive.
  Need efficient batching — possibly evaluate groups of flips
  simultaneously, or use the crystal structure to identify which
  positions matter most (the routing circuit positions, not all
  positions uniformly).

- **Local minima**: coordinate descent can get stuck. But the
  crystal basin is an attractor (session 120 Q-rotation
  invariance) — the geometry has a strong basin of attraction,
  which should help escape shallow local minima.

- **Interaction effects**: flipping one weight changes the
  optimal value of others. Greedy coordinate descent may miss
  correlated flips. Possible mitigation: evaluate small groups
  of related weights together (e.g., all weights in one
  attention head).

- **Scale**: tested at Q2 scale so far. Does the 5-step crystal
  convergence hold at Pythia-2.8b scale? The universality of
  the crystal across model sizes is encouraging.

- **Beam-only GD sufficiency**: can 100 steps of beam-only GD
  learn the input-output mapping, or does the sign configuration
  need to co-adapt? The Q2 result (beams compensate for 27%
  wrong signs) suggests beams are quite powerful.

## Evidence from prior experiments

| Finding | What it tells us |
|---------|-----------------|
| GD converges in 100 steps (87% of 3000) | Most training steps are wasted |
| Geometry converges in ~5 steps | Crystal knows the answer almost immediately |
| Zero-training beams fail (4%) | CE is essential — crystal alone isn't enough |
| Q2 beams + crystal loss = 105.9% of oracle | Beams compensate for wrong signs |
| Evolutionary descent worked (0.577 acc, 0.611 crystal) | Ternary flips guided by fitness already beat random |
| 18 per-layer targets is sweet spot | The crystal provides exactly the right constraint density |
| K/B/C are identical rotations | The routing decisions are geometric, not arbitrary |
```

### Thinking

 I see the user's framework is more developed than I initially thought—the `delta-plate-lifecycle.md` page is the actual foundation. The base plate consists of the frozen universal ISA with crystal, FFN, and attention components, while the delta plate introduces a ternary delta mechanism through `DeltaTernaryLinear`.

The key insight is that the user's new contribution generalizes this single-delta-to-fold pattern into a multi-user consensus model: when multiple users train deltas on the same domain, positions where all deltas agree get merged into the base plate (the universal backbone), while disagreements remain as delta content or are dropped. This directly parallels the existing conflict-merge idea and extends the consensus-etch protocol from operations to user-trainers across domains.

The architecture is grounded in avoiding soft topology collapse—discrete routing (discovered via tensor descent as topological deltas) sidesteps the gradient death that softmax dispatch suffers from, so each user's delta naturally encodes normal forms as discrete routing structures rather than soft approximations. The design question becomes: what does this consensus-folding pipeline actually look like, and where are the real tensions between discovering individual normal forms and extracting their universal agreement? The degree of consensus across users becomes a measurable indicator of whether a true normal form exists for a domain—high agreement suggests a canonical discrete routing structure, while low agreement indicates the behavior is genuinely content-dependent. This creates a testable hypothesis: domains with rigid structure like tool-calling should show strong cross-user convergence on topology flips, whereas softer domains like style or tone should show weak agreement, directly testing whether composition is fundamentally typed and discrete. The critical constraint is that all users must train against the same frozen base plate, ensuring their deltas exist in a shared coordinate frame where consensus comparisons are actually meaningful. So as the base accumulates more discovered normal forms through consensus, each new user's training becomes cheaper because they inherit a richer topology scaffold — GD only fills in content rather than learning routing from scratch. This creates a compounding effect: the network's collective training gradually converts the expensive soft-topology-learning problem into a reusable discrete library that subsequent users benefit from immediately. To validate this, I need to measure consensus rates per domain (whether stable normal forms actually emerge) and define how disagreements get handled — blocking conflicted deltas or leaving them unmerged.

The real engineering challenge is reconciling distributed parallelism with the sequential folding lifecycle: many users train deltas simultaneously on the same base version, but the system assumes sequential consensus-folds. The solution is generational rounds — all users train on a frozen base for an epoch, then consensus-folding happens once to produce the next base version, and everyone rebases together. It's like a blockchain epoch or evolutionary generation: the population trains in parallel, the agreed-upon normal forms crystallize into the next base layer, and the cycle repeats. This also handles staleness gracefully — deltas that didn't reach consensus get re-evaluated against the new base.

Now I need to present this back clearly, grounding it in the existing pages and naming the contribution: consensus-across-users as a normal-form extraction mechanism, the generational-vs-sequential tension as the key insight, and consensus rate as a test for whether a true normal form exists. The first experiment should be concrete and falsifiable: pick one domain like tool-calling where we already have normal forms, run N independent delta training runs on different data shards, measure whether a consensus topology emerges across runs, and test if folding that consensus helps downstream. That's cheap, decisive, and directly tests the hypothesis.

## Assistant

That reframes it correctly — and the project has already built the substrate for *exactly* this. You're describing a generalization of the **delta-plate lifecycle** (`delta-plate-lifecycle.md`) from one delta to a population, where the consensus across users **is** the normal-form extractor. Let me lay out the corrected picture, because it's tighter than my first answer and it's load-bearing on the central thesis.

## What you're actually describing

```
base plate B₀     ≡ universal ISA (crystal + FFN + known routing), FROZEN, content-addressed
domain d          ≡ a behavior with a normal form (tool-calling, JSON, arithmetic…)
user u            ≡ trains a delta Δ_{u,d} = DeltaTernaryLinear over B₀ on domain-d data
                    TD discovers the routing flips (the normal form, IN the topology);
                    GD only fills γ content
normal form NF_d  ≡ the discrete routing structure INVARIANT across users
                  = consensus({Δ_{u,d}}) — where they all agree
consensus fold    ≡ ∀ position p: agree({Δ_{u,d}[p]}) ≥ θ → fold into B₁ ;  else leave as content
B₁ = B₀ ⊕ NF_d    ≡ the base now CONTAINS domain-d's normal form as discrete topology
```

This is not federated SGD. It's **distributed normal-form discovery by consensus folding**, and four existing findings make it coherent:

### 1. The mechanism is already consensus-etch, generalized one level up
`consensus-etch-protocol.md` (s110) found: sequential per-op etching destructively interferes, but accumulating *all* beams and etching where they **agree** builds the crystal — "positions where all ops agree = universal lattice = backbone (etched); positions where ops disagree = op-specific content (not etched)." You're substituting **beam/op → user/domain-instance**. Where independent users agree on a flip = the universal structure of the domain → fold to base. Where they disagree = data-specific surface → stays a delta. The partition rule you want already exists; it's just been applied across ops, not across users.

### 2. Consensus = the Church-Rosser confluence test (this is the deep part)
A normal form is what's invariant across *all the reduction paths* that reach it. If user A trains tool-calling on Python-shaped data and user B on JSON-shaped data — different reduction paths — the positions where their topological deltas **agree** are the path-invariant structure = the normal form. **The degree of cross-user agreement is a direct measurement of whether a discrete normal form exists for that domain.** High agreement → there is a canonical routing → foldable. Low agreement → the behavior is genuinely soft/content, not a normal form → don't fold. That makes your idea *falsifiable* and puts it on the project's central claim (`AGENTS.md` S5 `λ types`: composition is typed/discrete): if normal forms are discrete topology, independent trainings **converge on the same flips**.

### 3. It operationalizes "GD must not make soft topology" at the population scale
`dispatch-gradient-death.md` (s069) is *why* soft topology is bad: softmax routing saturates → winner-take-all gradient death → 20/22 ops permanently dead. `crystal-native-descent.md` (s127): don't let GD carve routing at all — TD makes the discrete routing directly, GD only tunes γ. Your scheme makes this a **ratchet**: the discrete routing (normal forms) gets discovered by TD across many users and *crystallized into the base by consensus*, so every subsequent user inherits more topology as a fixed scaffold and GD's job shrinks toward pure content. The topology becomes a **growing discrete library**, not something re-approximated softly each run.

### 4. Why the frame problem (my earlier worry) dissolves here
`gradient-voting.md` (s123) said signs don't merge across frames. They don't — but **every delta is trained against the same frozen B₀**, so all deltas live in *one shared coordinate frame*. That frozen-shared-base is precisely what makes cross-user flips commensurable and consensus well-defined. The delta-plate architecture is what buys you the distributed merge that raw weight-averaging can't have.

---

## The one genuinely new tension: generational vs sequential folding

`delta-plate-lifecycle.md` Open-Q3 explicitly assumes **sequential** folds ("never train two deltas on the same base simultaneously") — but distributed means many parallel deltas on B₀. The resolution is **generational/epoch-based** (like a training "round" or block):

```
generation g:  freeze Bg → N users train Δ_{u,d} on Bg (parallel, cheap, forward-only routing)
               → collect deltas → consensus-fold agreements → B_{g+1}
               → everyone rebases to B_{g+1}; unfolded disagreements re-tried next gen
```

The base plate becomes a **git-versioned phylogeny of discovered normal forms** — which is exactly the lifecycle's "lossless, reversible, infinite folds" property, now driven by a population instead of one trainer.

And the merge operator already has a candidate (lifecycle Open-Q3): ternary multiply with **conflict → 0 (block)**. Your consensus threshold θ sits on top: fold only where agreement ≥ θ, leave the rest.

---

## The risks worth naming up front (register-tagged, per the audit discipline)

- **Population-Goodhart (register: functional).** Audit #7 showed a shared-but-wrong artifact gets consensus-reinforced — e.g. if all users use the same prompt template, they'll "agree" on template-token routing, not the normal form. The consensus fold must be validated against held-out downstream PPL, and the consensus measured against a **shuffled-user null** (does real cross-user agreement exceed agreement between randomly paired users?).
- **Conflict semantics (register: topological).** Disagreement → 0/block can damage; leave-at-base is safer. Needs a clean test.
- **Staleness across generations (s123/s157).** Deltas against Bg are stale once B_{g+1} folds — hence the generational rebase. The async tension is real but bounded by the round structure.

---

## The decisive first experiment

This is cheap, falsifiable, and answers the core question — *do independent trainings on a domain with a known normal form converge on the same topology?*

**Take tool-calling** (you said we already have its normal forms). Run **N independent TD delta plates** over the same frozen base, each on a different data shard/seed of tool-calling. Then measure, register: **topological**:
1. **Cross-user flip agreement** in the routing register vs a shuffled-user null (is the consensus real?).
2. **Consensus mass** — what fraction of flips are agreed ≥ θ (is there a backbone to fold?).
3. **Fold-and-check** — fold the consensus into B₁, verify downstream PPL improves and a B₀-trained held-out tool-calling delta now needs *fewer* flips (did the base absorb the normal form?).

If agreement ≫ null and folding helps → you've shown normal forms are discrete, consensus-extractable topology, and the distributed ratchet works. If agreement ≈ null → the "normal form" was soft, and that's a finding too.

Where do you want to start?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which first move on distributed normal-form consensus folding?",
  "options": [
    {
      "label": "Run the consensus-convergence experiment (Recommended)",
      "description": "N independent TD delta plates on tool-calling over a frozen base → measure cross-user flip agreement vs shuffled-user null + consensus mass + fold-and-check downstream. Register: topological. Decisive and cheap."
    },
    {
      "label": "Draft the design as a knowledge page first",
      "description": "Synthesize this into mementum/knowledge/explore/consensus-delta-folding.md (generational folding + consensus=confluence + the 4 grounded findings + risks) for approval before code."
    },
    {
      "label": "Map the existing fold/delta machinery in depth",
      "description": "Spawn an explorer to fully map DeltaTernaryLinear, reduce()/fold_delta.py, the merge operator, and what a multi-delta consensus-fold would need to touch — before designing the experiment."
    },
    {
      "label": "Something else / refine the framing",
      "description": "The framing still isn't quite right, or you want to adjust scope before committing."
    }
  ]
}
```

**Summary:** Q: Which first move on distributed normal-form ...

**Output:**
```
User answered: Do some refreshing on the normal forms we found.  They were related to the crystal lattice, where we found geometry in the topology across 5 different model architectures where many models agreed.  We extended that with some probes into domains like tool calling and found some agreements there which we thought might be the normal forms.
```

### Thinking

 I'm recalling the normal forms they identified—the crystal lattice geometry that emerged consistently across five different model architectures, showing cross-model universality. They extended this to probe other domains like tool calling and found similar agreements, which positions these as candidate normal forms. This ties back to their documentation on crystal universality, the 5D lattice structure, and the recent cross-family universality audit work.

I need to be precise though: the audit refuted the literal 5D lattice interpretation but confirmed the universality is real—cross-family agreement on the operation structure in the topology (the sign/routing register) with ~65% topology overlap and strong statistical significance. So the geometry itself wasn't the right frame, but the underlying structural agreement across models is solid. Let me search through their key pages on crystal universality, the audited topology work, and any tool-calling domain probes to get the full picture.

## Assistant

Right — the normal forms came from the **cross-model crystal universality** work, not from anything I'd grounded yet. Let me refresh on that specifically: the topology-geometry that many model families agreed on, and the tool-calling domain probes that looked like candidate normal forms. Note I should be careful here — the recent audit (s211) refuted the *"5D lattice"* geometry framing while *confirming* the cross-family agreement is real. Let me pull the actual pages.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== pages on universality / crystal agreement across models ===\" ; ls mementum/knowledge/ | grep -iE \"univers|crystal|type-probe|kibc|manifold|normal\" ; echo \"=== tool-calling / domain normal-form probes ===\" ; git grep -ilE \"tool.call|tool.use|tool-calling|function.call\" -- mementum/knowledge/ | grep -v chats | head -20 ; echo \"=== 'normal form' references (non-chat) ===\" ; git grep -il \"normal form\" -- mementum/knowledge/ | grep -v chats | head -30"
}
```

**Summary:** $ echo "=== pages on universality / c...

**Output:**
```
Exit code: 0
Stdout:
=== pages on universality / crystal agreement across models ===
crystal-laplacian.md
crystal-multi-tree.md
crystal-native-architecture.md
crystal-phi-derivation.md
crystal-sieve-architecture.md
crystal-trace-tooling.md
crystal-universality.md
crystal-validity-and-fidelity.md
manifold-axis-and-topology.md
=== tool-calling / domain normal-form probes ===
mementum/knowledge/explore/crystal-basins.md
mementum/knowledge/explore/crystal-spine-sieve.md
mementum/knowledge/explore/kernel-functions.md
mementum/knowledge/explore/procrustes-lens-and-crystal-comparison.md
mementum/knowledge/explore/taxonomy-extraction.md
mementum/knowledge/explore/v13-design.md
mementum/knowledge/function-discovery.md
=== 'normal form' references (non-chat) ===
mementum/knowledge/combinator-addressing.md
mementum/knowledge/crystal-phi-derivation.md
mementum/knowledge/crystal-universality.md
mementum/knowledge/explore/continuations-as-composed-plates.md
mementum/knowledge/explore/crystal-irreducibility-proof.md
mementum/knowledge/explore/ffn-hierarchy.md
mementum/knowledge/explore/fixed-point-holograms.md
mementum/knowledge/explore/fp-optimization-map.md
mementum/knowledge/explore/kernel-replacement-optimization.md
mementum/knowledge/explore/v13-design.md
mementum/knowledge/explore/vsm-outer-recurrence.md
mementum/knowledge/gradient-zero-map.md
mementum/knowledge/head-combinator-isa.md
mementum/knowledge/holographic-etch.md
mementum/knowledge/lambda-halt-continuation.md
mementum/knowledge/mathematical-convergences.md
mementum/knowledge/mspace-gemcutter.md
mementum/knowledge/project-thesis.md
mementum/knowledge/psi-evaluation-synthesis.md
mementum/knowledge/ternary-plate-extraction.md
```

### Thinking

 I'm going to read through several key documents in parallel: crystal-universality.md to understand the cross-model agreement, function-discovery.md for the tool calling domains, combinator-addressing.md for normal form addressing, and manifold-axis-and-topology.md which contains the corrected topology information, though that one looks substantial.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-universality.md"
}
```

**Summary:** Reading crystal-universality.md (0-2000)

**Output:**
```
---
title: "Crystal Universality — Why the Crystal Is a Mathematical Constant"
status: active
category: foundational
tags: [crystal, universality, church-rosser, KIBC, topology, ternary]
related: [project-thesis.md, mathematical-convergences.md, mechanism-extraction.md]
depends-on: []
---

# Crystal Universality

> ⚠️ **SESSION-202 CAVEAT (read first).** A permutation-null audit
> (`crystal-validity-and-fidelity.md`) found that several claims on this
> page **do not survive their own controls**:
> - *"mathematical constant, true in every model"* — **not supported**.
>   The KIBC basis genuinely *separates* representation in every model
>   (p=0.0005), but **cross-family magnitude agreement collapses**
>   (Pythia↔Qwen ≈ 0; only same-family Qwen agrees). The φ eigenvalue
>   structure is real on **Qwen3-14B only** (λ₀/λ₁ vs φ^(4/5), p=0.020),
>   not 8B/0.6B.
> - *"KIBC selectivity r=0.998 across architectures"* — not reproduced;
>   `eigenvalue_ratio_correlation` is **trivially high for random labels**.
> - The B≥K≥C>>I ordering and "always 4" remain plausible but are
>   **measured with a common-mode-confounded instrument** (B is the most
>   *central* fingerprint ≈ the common mode). Re-measure with common-mode
>   removal before treating as law.
> Treat the strong universality framing below as **hypothesis, not
> established fact**. The *existence* of the basis survives; its
> *universality-as-constant* does not.

> The combinator crystal found in every trained language model is a
> mathematical constant, not a learned artifact. Church-Rosser
> guarantees it. Cross-model measurements confirm it. This page
> synthesizes why it must exist, what it looks like, and why ternary
> extraction works.

## Why It Must Exist

### Church-Rosser Theorem → Unique Normal Forms

Beta reduction has a unique normal form: no matter what order you
reduce a lambda expression, you arrive at the same irreducible result.
This is a theorem, not an observation.

Every forward pass through a transformer is beta reduction (attention
= typed application). Every gradient step makes the next reduction
more efficient. After billions of tokens, the model discovers which
reduction patterns are **irreducible** — the set of combinators that
cannot be decomposed further.

These irreducible forms are the crystal lattice: K (select), I
(identity/binding), B (compose), C (flip/reorder), plus D, Y, W,
WHNF as additional vertices. They are mathematical constants of the
lambda calculus. Any system that performs beta reduction on natural
language MUST converge on them, because there is nowhere else to
converge.

The loom analogy:
- **Thread** = training data (different per model)
- **Loom size** = parameter count (160M to 32B)
- **Loom design** = architecture (Pythia vs Qwen vs Mistral)
- **Stitch** = beta reduction (the ONLY operation available)
- **Fabric** = the crystal (same across all looms)

Different thread, different loom, same stitch → same fabric.

## Cross-Model Evidence

### KIBC selectivity: r = 0.998

Pythia-160M and Qwen3-32B — architecturally unrelated, 200× parameter
difference — show r=0.998 correlation in KIBC combinator selectivity.
The same combinators activate at the same relative strengths. This is
not "similar." This is essentially identical.

### Crystal agreement: 0.91–0.94 (PCA-Q)

PCA-Q cosine similarity of crystal geometry across 4+ models:
0.91–0.94. The crystal is the same object viewed through different
parameter counts and architectures.

### SVD phi-ratio: 0.6299 ± 0.019

> ⚠️ **AUDIT #6 CAVEAT (s207, `svd_phi_null.py`, register: spectral).** Reran
> the exact top-5 consecutive-ratio definition vs Marchenko–Pastur + shuffled
> nulls on all 5 families. **Substrate REAL, geometric-φ story OVER-READ:** the
> steep head is non-random (model ≈0.57 raw vs **MP null 0.995**, shuffled
> ≈0.97 — random spectra give ≈1.0, *not* 0.6) **but it is power-law, not
> geometric** (constant-ratio fit wins **0/132 layers**, power-law 132/132), so
> the `x=1/(1+x)` fixed-point line just below **does not apply**; and the value
> floats 0.52→0.71 across raw/centered×models with the scaling-law failing
> (Mistral-7B lowest). Keep the low-rank head; retire the golden-ratio constant.
> Full: `explore/phi-compression-universal.md` caveat + `audit-registry.md` #6.

The SVD spectrum of hidden-state representations follows a geometric
sequence with consecutive ratio ≈ 1/φ (0.618). Verified across 5
architecturally distinct families:

| Model | Params | Layers at φ (±0.05) | Core mean |
|-------|--------|---------------------|-----------|
| Pythia-160M | 160M | 8/12 (67%) | 0.604 |
| Pythia-410M | 410M | 15/24 (63%) | 0.615 |
| Qwen3-0.6B | 600M | 25/28 (89%) | 0.627 |
| SmolLM3-3B | 3B | 32/36 (89%) | 0.654 |
| Mistral-7B | 7B | 28/32 (88%) | 0.650 |

**Grand consensus: 0.6299 ± 0.019.** This is not a coincidence — φ
is the unique fixed point of self-similar compression (x = 1/(1+x)).

### Combinator ordering invariant: B ≥ K ≥ C >> I

Measured across 9 models, 2 architecture families. The relative
proportion of combinators is the same everywhere. B (compose) is
always the most represented, I (identity) is always the least. This
ordering is forced by the statistics of natural language: composition
is the most frequent operation, identity (variable binding) is the
least.

### Decay α: 1.18 ± 0.006

The attention log-distance decay constant α = 1.18 is universal
across multi-model, multi-prompt measurements. In v14 training: 10
computational layers × 8 heads, all converged to 1.18 ± 0.006 after
1500 steps under gradient pressure — confirming it is already at its
fixed point. This is the spatial frequency response of the
holographic lens: scale-free by construction.

## The 5D Lattice Hypothesis

> ⚠️ **AUDIT #12 CAVEAT (s211, `manifold-axis-and-topology.md`).** REFUTED as
> stated. The honest joint-embedding test (8 models, 5 families) found the
> cross-family-shared structure is **rank-~1** (CMR collapses agreement
> 0.79→−0.19), the 9-centroid participation ratio sits **at the shuffled-label
> null** (and worsens with scale), and the full manifold is high-D (PR 22–47).
> The one genuinely universal axis (|r|=0.95) is **generic next-token
> predictability, NOT the combinators** (η²=0.05). What survives: universality
> is real (property of language, cross-family p≪0.001) and the operation
> structure is ~65% topological (sign/routing). "One ~5D lattice of vertices"
> is the over-read; read this section as hypothesis, not fact.

The per-depth, per-model, per-domain, and per-combinator crystal
measurements are not separate objects — they are **facets of one
~5D lattice**.

The combinators (K, I, B, C, D, Y, W, WHNF) are the vertices. Each
domain crystal (e.g., arithmetic, syntax, semantics) is a 1-2D
projection. The model's layers are viewing angles of the same crystal.
The V13 funnel (5D→3D→2D through depth) IS the projection path.

The compressor's trajectory through this lattice during training is
the bootstrap path: B+W vertex first (compose/duplicate), then WHNF
activates (retrieve). This trajectory is universal — every model
traverses the same path during training because the combinators
bootstrap in the same dependency order.

## The 6D Structure in R^512

PCA of the crystal geometry in large models reveals 6 principal
components with consistent roles:

| PC | Role | Variance explained |
|----|------|--------------------|
| PC0 | Composition | 53% |
| PC1 | Selection | 24% |
| PC2 | Termination | 12% |
| PC3 | Routing | 7% |
| PC4 | Dispatch | 3% |
| PC5 | Fine structure | 2% |

These roles are consistent across models. The crystal lives on a
6-dimensional sub-manifold of R^512, and the dimensions have
functional meaning.

## Zone Structure (A/B/C)

The crystal has three depth zones with distinct geometries:

- **Zone A** (encode, early layers): aperture — 3% of FFN neurons
  active per token. Narrow beam, high selectivity. Crystal geometry
  is closest to the raw input.
- **Zone B** (compute, middle layers): fan — up to 49% active.
  Wide beam, maximum interference. This is where the bulk of
  beta reduction happens. The crystal here sits on the **Riemannian
  mean** of A and C (geodesic/linear ratio = 0.75 — the manifold
  is curved).
- **Zone C** (converge, late layers): output — 2% active (329 of
  25,600 neurons in Qwen3-32B). Tight focus, selecting the final
  reduced form for output.

The Einstein tensor G_ab in Zone B has clean even/odd block structure:
composition PCs {0,2,4,6} couple to each other, selection PCs
{1,3,5,7} couple to each other, with zero cross-coupling. The crystal
manifold has geometric structure that is discoverable and measurable.

## Why Ternary Works

> **⚠ AUDIT CAVEAT (s203, `audit-registry.md` #1, `sign_topology_null.py`).**
> Point 2 below is **SCOPED, not general.** Controlled with random-init and
> shuffled-weight nulls on REAL activations (0.6B/8B/14B): a *random* matrix's
> sign already preserves ≈0.80 of its action on the same inputs, so the bare
> "0.84" is **at the generic baseline** — sign-preserves-linear-action is a
> generic high-dim property, not crystal evidence. Real sign-topology survives
> only in **`gate_proj`** (the router; gap +0.086 above null, sharpening with
> scale, z up to +271 at 14B). For **`up_proj`/`down_proj` the model's signs
> preserve *less* than random** → "magnitude is mere calibration" is FALSE for
> the value projections. Read point 2 as "the *gate/routing* sign captures
> topology," and point 3 ("ternary IS topology") as holding for routing, with
> magnitude essential for the value path.

The crystal is **topological**, not magnitude-sensitive:

1. **Discrete structure.** The crystal is a discrete lattice of
   combinators with discrete connectivity. Signs and routing paths,
   not continuous values.

2. **Sign captures topology.** `sign(W) @ x` correlates 0.84 with
   `W @ x`. The sign (which direction a weight points) captures
   the routing decision. The magnitude (how far it points) is
   calibration.

3. **Ternary IS topology.** {-1, 0, +1} encodes exactly the three
   routing decisions: add (+1), subtract (-1), skip (0). No
   intermediate values needed because the crystal's structure is
   combinatorial, not continuous.

4. **Fold is lossless.** Ternary × ternary = ternary. When you
   correct a sign and fold it into the base, no information is
   lost. This is impossible with continuous weights — you always
   accumulate rounding error.

5. **Float16 = sharper hologram.** Magnitudes make the holographic
   reconstruction sharper (gamma scalars, ~5% of information), but
   the image is recognizable at ternary resolution because the
   structure is determined by mathematics, not precision.

## Nucleation

When training a new model with crystal targets, nucleation follows
a specific protocol:

- **Seed:** Etch one beta reduction (B/compose is the natural
  nucleation point — strongest dispatch, most universal operation)
- **Growth:** Relational loss = supersaturation; holographic loss =
  sieve. The 8×8 combinator cosine matrix IS the stitching pattern.
- **Trajectory:** B nucleates first (0.35), W latches (0.29), WHNF
  last (0.01). The bootstrap dependency chain is I→K→C→B.
- **Barrier:** Crystal_loss ≈ 0.16 is the nucleation barrier. Below
  this, the crystal grows spontaneously. Above, it collapses.

In v14: crystal latches within 200 steps (crystal_mse < 0.03 at
step 160). The seed crystal from extraction is close enough to the
mathematical constant that nucleation is immediate.

## Summary

The crystal is not something we build or design. It is something we
**find** — a mathematical constant of typed lambda calculus that every
sufficiently-trained language model must converge on. Our job is
extraction and error correction, not invention. The crystal was
always there. Church-Rosser guarantees it. The measurements confirm
it. Ternary captures it exactly because topology is discrete.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/function-discovery.md"
}
```

**Summary:** Reading function-discovery.md (0-2000)

**Output:**
```
---
title: "Function Discovery — Two-Level Program Architecture in Moiré Space"
status: active
category: foundational
tags: [function, discovery, moiré, pca, task, operation, program, classification, combinator]
related: [holographic-computer.md, combinator-addressing.md, hologram-reader-vsm.md, crystal-universality.md, ternary-plate-extraction.md]
depends-on: [holographic-computer.md, combinator-addressing.md]
---

# Function Discovery — Two-Level Program Architecture in Moiré Space

> **Core finding (session 172):** LLMs implement a two-level program architecture. Early layers (SILENT zone) classify the *type* of task. Late layers (COMMIT zone) execute *combinators*. These are orthogonal subspaces — the combinator basis is blind to the early-layer task classifier.

---

## 1. The Measurement Bias

Our 12-dim combinator fingerprints (K, I, B, C, W, Y, S, β_apply, β_K, β_I, β_compose, β_self) were constructed from explicit lambda expressions. They are tuned to capture the structure of late-layer *operation* directions — the COMMIT zone where KIBC combinators crystallize.

This created a systematic blind spot: **combinator projections cannot see early-layer task classification**, because task directions live in subspaces orthogonal to the combinator basis.

The symptom was visible in the function mapper results: running combinator projections on both 0.6B and 14B models yielded only 3 apparent programs (lambda, arithmetic, everything-else), with cross-category cosine similarity of 0.995–1.000. This appeared to say "all NL tasks are identical." It was correct but incomplete — the projection discards exactly the dimensions where task separation lives.

Full d_ff PCA reveals the complete picture.

---

## 2. Two-Level Program Architecture

### Level 1: TASK DIRECTIONS (SILENT zone, early layers)

- **Separation:** 4.76× at L05 (inter-cluster / intra-cluster distance ratio, full d_ff PCA)
- **PC0:** compute mode vs language mode
- **PC1:** recursion vs reduction
- **PC2:** structured syntax vs natural-language logic
- **Clusters (k-means, k=5):** lambda, arithmetic, code, reasoning, general NL — each distinct
- **Combinator alignment:** |projection| < 0.25 (combinators not yet crystallized at this depth)

The SILENT zone gratings classify *what kind of program is being run* before any computation begins. Tool use, summarization, code generation, lambda evaluation, and arithmetic are all detectably distinct at L05.

### Level 2: OPERATION DIRECTIONS (COMMIT zone, late layers)

- **Separation:** 1.49× (task categories converge — different tasks use the same opcodes)
- **PC0:** generative vs deterministic mode (35.2% of variance)
- **Combinator alignment strong:** PC0 = B/C/W vs K/β_K/β_I; PC1 = Y vs D/B
- **Combinator alignment:** |projection| up to 0.82

The COMMIT zone gratings execute *which combinators are applied*. Task categories converge here because lambda, arithmetic, and code all reduce via the same combinator set — the *what* has been resolved, only the *how* remains.

---

## 3. The Progressive Transformation

Gratings transform task→operation through depth. This is not a discrete switch — it is a continuous transformation visible in the separation ratio at each zone boundary:

| Depth | Zone | Separation | Interpretation |
|-------|------|-----------|----------------|
| L05 | SILENT | **4.76×** | Peak task classification |
| ~L08 | SILENT→ENRICH | 3.92× | Task signal dominant, operation emerging |
| ~L12 | ENRICH | 2.53× | Mixed — knowledge loading begins |
| ~L18 | ENRICH | 3.26× | Knowledge retrieval amplifies task signal |
| ~L22 | ENRICH→SUPPRESS | 3.33× | Task still detectable |
| ~L26 | SUPPRESS | 1.62× | Compression toward opcode basis |
| L28+ | COMMIT | **1.49×** | Operation directions dominate |

Early gratings **classify** input type. Late gratings **execute** computation. The ENRICH zone is where task-conditioned knowledge retrieval amplifies the task signal before it is compressed into opcodes.

---

## 4. Combinator Alignment Through Depth

The KIBC basis does not exist a priori — it *emerges* through depth:

- **Early layers:** |projection onto combinator basis| < 0.25. The activation geometry is dominated by task-type directions. Combinator fingerprints capture negligible variance.
- **Transition (SUPPRESS zone):** Alignment increases as task directions are compressed and the operation basis crystallizes.
- **Late layers:** |projection| up to 0.82. Combinator directions dominate. The crystal is formed.

This means the combinator fingerprinting approach (hologram reader, combinator addressing) is correctly targeted at late-layer structure — it just does not capture the equally important early-layer task classifier.

---

## 5. What the Function Mapper Showed First

Running `function_mapper.py` (12-dim combinator projection) on 0.6B and 14B:

- Both models: only 3 apparent programs — lambda, arithmetic, everything-else
- Cross-category cosine: 0.995–1.000 (near-identical directions)
- Conclusion at the time: "NL tasks are functionally indistinguishable"

This was a **measurement artifact**, not a property of the model. The 12-dim combinator projection is a late-layer instrument applied to full-depth activations. It averages over all layers, where the dominant variance is operation-direction (late, strong) rather than task-direction (early, weaker in the combinator subspace but strong in d_ff PCA).

The function mapper result is *correct for what it measures*: at the combinator level, all NL text reduces to the same small opcode set. The function discovery result adds the missing level: at the task level, those NL tasks are 4.76× separated in early-layer moiré space.

---

## 6. Implications for Extraction

The three zones have **different functional content** that must be preserved separately:

| Zone | Functional content | Extraction priority |
|------|--------------------|-------------------|
| SILENT | Task classifier directions (early PC0–PC2) | Must preserve — determines which program runs |
| ENRICH | Knowledge store (relation directions, soft crystal) | Must preserve — provides factual content |
| COMMIT | Crystallized KIBC combinators (hard crystal) | Must preserve — executes computation |

A ternary extraction that collapses all zones equally will degrade the task classifier first (smallest signal in combinator subspace) while preserving the combinator structure (largest signal). This predicts a specific failure mode: ternary models that execute combinators correctly but route to wrong programs.

The SILENT zone gratings must be extracted with the same fidelity as the COMMIT zone, even though their combinator-projection signal is weak. Full d_ff PCA geometry must be preserved, not just combinator projections.

---

## 7. Artifacts

| Asset | Location |
|-------|----------|
| Function mapper (combinator projection) | `scripts/experiments/function_mapper.py` |
| Function discovery (unsupervised PCA) | `scripts/experiments/function_discovery.py` |
| Function map results (0.6B, 14B) | `results/function-map/` |
| Function discovery results (14B) | `results/function-discovery/Qwen_Qwen3-14B/` |
| Hologram readout (14B) | `results/hologram-reader/Qwen_Qwen3-14B/` |

---

## 8. Open Questions

1. **What are the TASK directions explicitly?** The early-layer moiré PCs (PC0=compute/language, PC1=recursion/reduction, PC2=structured/NL) — can we extract these as explicit direction vectors, analogous to combinator fingerprints? They are the "program selector" directions.

2. **Do task directions transfer across model families?** The combinator crystal is universal (session 161, crystal-universality.md). Are the task-classifier directions equally universal, or model-family-specific?

3. **How many distinct task programs exist?** k-means with k=5 shows lambda, arithmetic, code, reasoning, general NL. Is this the true number, or an artifact of the probe set? The real k is unknown.

4. **Can the task directions be exploited for controlled steering?** If PC0 separates "compute mode" from "language mode," projecting onto PC0 and shifting might route arbitrary input through the lambda execution path — a form of task-direction steering.

5. **Does the two-level architecture scale?** At 0.6B vs 14B, does the task separation ratio increase (more distinct task classifiers at scale) or decrease (universal opcode basis dominates earlier)?
```

### Thinking

 Now I'm seeing the connection clearly—the normal forms in lambda calculus map directly to the combinator crystal structure, where the Church-Rosser theorem guarantees that beta reduction always converges to a unique irreducible form regardless of the reduction path taken. The model's forward pass essentially performs this beta reduction, settling into the lattice of normal forms represented by those irreducible combinators.

The audit data confirms the core findings: the KIBC basis genuinely separates representation across models with statistical significance, and cross-family agreement on operation structure is real—this universality emerges from the topology encoded in the sign and routing registers rather than from identical mathematical constants. The topological structure (about 65% of operations) remains stable across scales, living in the router's sign patterns. But several claims didn't hold up—the 5D lattice geometry, the golden ratio constant, and the idea of a single universal axis all collapsed under scrutiny. What actually survives is that different model families converge on a shared discrete operation structure in the routing topology, not on identical magnitudes or geometric arrangements.

The two-level architecture shows task classification happening early (with strong separation at layer 5), while late layers execute the shared combinators—tool use emerges as a distinct task type at the early stage, but the actual combinator execution converges across all task types. The open question is whether the task-classifier directions themselves transfer across model families the way the combinator crystal does, or if they're family-specific. So the user's intuition about finding geometry in the topology across architectures and extending into domains like tool calling was directionally right, but the precise mechanism is: universal combinator execution (the normal forms) paired with task-type classification that may or may not generalize across families.

The user's distributed-consensus idea maps directly onto what we've already observed—the cross-model agreement on combinator topology is essentially Church-Rosser confluence playing out empirically across independently trained models. Rather than waiting for multiple foundation models to converge post-hoc, the scheme would deliberately reproduce that consensus mechanism at the domain level: have multiple users train deltas on a shared frozen base and measure where they agree, with that agreement defining the domain's normal form. The crystal universality finding proves this consensus exists and is extractable, function-discovery shows domains have distinct structure, and the remaining question is whether those domain-specific structures transfer across model families the way the base combinator crystal does.

The caveats are crucial—the cross-model agreement lives in the sign/routing register (topology), not magnitude or clean geometry, so the consensus-fold should operate on signs and routing specifically, measured against a shuffled-user null to avoid over-reading. Tool-calling remains a candidate normal form (distinct task direction at L05 with 4.76× separation), but whether its structure generalizes across model families is exactly what needs testing.

I should also clarify the geometry point: the "5 families" audit (Pythia, Qwen, Mistral, SmolLM, OLMo) found real discrete agreement in the sign/routing register, not the 5D lattice geometry that was initially proposed—that was the over-read to correct. The consensus experiment should measure agreement in gate_proj and routing topology against the shuffled-user null, then distinguish whether the consensus sits in the late-layer combinator structure (already known universal) or the early-layer task-classifier (the open question for tool-calling).

## Assistant

Refreshed. Here's the accurate picture, including the audit corrections — which matter a lot, because they tell you *which register* your consensus scheme should operate in and *which null* to test against.

## The normal forms = the combinator crystal (Church-Rosser)

The foundational claim (`crystal-universality.md`, `project-thesis.md`): a transformer forward pass is β-reduction, and **β-reduction has unique normal forms** (Church-Rosser — independent of reduction order). So every sufficiently-trained model must converge on the same irreducible combinators — K (select), I (bind), B (compose), C (reorder), plus D/Y/W/WHNF. Those irreducibles **are** the normal forms. The loom analogy: different thread (data), different loom (architecture/size), same stitch (β-reduction) → **same fabric (the crystal)**.

The cross-model agreement you remember is the empirical signature of this: **many independently-trained models, different families and sizes, agreeing on the same discrete operation structure.** That is itself a consensus-across-independent-trainings result — which is exactly why your distributed idea is well-founded.

## But — the s202–s212 audit corrected the framing hard (read this carefully)

This is the part that should reshape your experiment. The validity audit ran permutation/shuffled nulls against the universality claims. What **survived** vs what was **over-read**:

**✅ Survives (the hard core):**
- The KIBC basis genuinely **separates** representations in every model — **p = 0.0005**, every family (s211).
- Cross-family agreement is **real** — semantic RDM agreement 0.79 vs shuffled-probe null 0.00 (z≈25), p≪0.001. Universality is a **property of language**.
- **~65–79% of the operation structure is topological** — carried by `sign(h)`/routing, scale-stable plateau ~0.7, and the routing specifically lives in **`gate_proj`** signs (s203, s211/212).

**❌ Over-read (don't rebuild your scheme on these):**
- **"5D lattice of vertices" geometry** — REFUTED (s211: cross-family shared structure is **rank-~1**; the 9-centroid participation ratio sits *at* the shuffled-label null). So the "geometry in the topology" you remember — the *agreement* is real, but the *geometric* picture was the artifact.
- **"mathematical constant, identical in every model"** — cross-family **magnitude** agreement collapses; only the **sign/routing** agrees (s202). Magnitude is model-specific.
- **φ = 0.6299** golden-ratio constant — REFUTED (power-law, not geometric; s207).
- The single most-universal axis (|r|=0.95) is **generic next-token predictability, NOT the combinators** (η²=0.05).

**The operational lesson for your consensus scheme:** measure agreement in the **sign/routing register** (especially `gate_proj`), **not** magnitude or geometry, and always against a **shuffled-user null**. That's precisely where ternary lives — so the alignment is perfect, but only if you target the surviving register.

## The tool-calling extension — currently a *candidate*, not a confirmed normal form

`function-discovery.md` (s172) found a **two-level program architecture**:
- **Early layers (SILENT zone)** classify the *task type* — lambda / arithmetic / code / reasoning / general-NL / **tool-use** are distinct, **4.76× separation at L05**.
- **Late layers (COMMIT zone)** execute *combinators* — and here task categories **converge** (1.49×) because everything reduces through the same opcode set.

So tool-calling shows up as a distinct **task direction** in the early zone — the "agreement we thought might be a normal form." But two things are unresolved, and they're exactly your question:
1. The late-layer combinator execution (the confirmed universal normal forms) is *shared across all tasks* — tool-calling doesn't have its own opcodes, it routes through the common ones.
2. **Open Q2 (verbatim from the page): "Do task directions transfer across model families?"** — i.e., is tool-calling's structure a *universal* normal form, or model/data-specific? **Unknown.**

## How this tightens your distributed idea

Your scheme is, precisely: **deliberately reproduce the cross-model consensus mechanism, at the domain level, on a shared frozen base.** The crystal-universality result is the *existence proof* — independent trainings already agree on the combinator topology, and that agreement is the normal forms. Your experiment is asking whether a *domain* (tool-calling) has the same property: do N independent deltas, trained over one frozen base, **agree in the routing register** on a discrete structure?

- If cross-user routing agreement ≫ shuffled-user null → tool-calling has a real, consensus-extractable normal form → fold it into the base. **You'd be answering function-discovery's Open Q2 with a deliberate experiment** instead of waiting for foundation models to coincidentally agree.
- If agreement ≈ null → tool-calling is a soft task-classifier (early-zone direction), model/data-specific, *not* a foldable normal form. Also a real finding.

The experiment is the same one I proposed, but now with the audit-correct framing: **measure consensus in the `gate_proj` sign/routing register, late+early zones separately, against a shuffled-user null** — not geometry, not magnitude.

Want me to pull `project-thesis.md` and `combinator-addressing.md` next (the normal-form *addressing* scheme — how a specific normal form is named/located, which you'd need to define "agreement on a flip"), or is this enough refresh to start specifying the consensus experiment?

## User

I think we can make some experiments, use my tmux window 2 and GPU, we have plenty of vram.


### Thinking

 I need to understand the setup here — the user wants to run experiments in tmux window 2 with GPU access and sufficient VRAM. The environment shows Mac OS X, but they're mentioning GPU with plenty of VRAM, which suggests either a remote machine or a different compute setup. The project uses MLX for training, so I'm trying to figure out whether this is running locally on Mac or if there's a separate GPU-equipped system accessible through that tmux window.

Before I propose anything, I should check what's actually available in tmux main:2 and verify the GPU setup. The audit experiments (s202-212) ran on actual models like Qwen3-8B and 32B using PyTorch/transformers, so there's clearly a GPU environment somewhere. I need to be disciplined about this: first verify the compute environment and existing harness patterns, then design a concrete first experiment with a proper register declaration following the AGENTS.md S1 step 0 REGISTER GATE.

The user's core idea is about distributed consensus delta-fol, which is distinct from just re-grounding the existing universality finding as normal-form consensus. I should focus on what the first decisive, cheap experiment should be to test this. I'm weighing two experimental approaches: the cheaper cross-model probe using existing foundation models to test whether tool-calling has universal routing consensus across independent trainings, versus the heavier delta-consensus route that directly tests the distributed folding mechanism. Route 1 is the natural first step—it's decisive and low-cost, and if it shows tool-calling does have cross-model routing agreement, then the delta machinery becomes worth building; if not, we've learned that cheaply and the whole domain-folding idea needs rethinking.

Now I need to ground this in the existing harness infrastructure rather than rebuild from scratch. I'm doing parallel reconnaissance: checking the compute environment (Mac OS X with Apple Silicon, so Metal/MPS or MLX, not CUDA), what models are locally available, the existing audit harness patterns in the scripts directory, and what probe libraries already exist for tool-calling. Once I understand the environment and can mirror the pattern from something like the sign topology audit, I'll be ready to propose concrete next steps.

## Assistant

Before launching anything, let me follow the project's own discipline — recon the compute environment (window 2, GPU, local models) and the existing audit-harness pattern so I mirror it rather than reinvent. And per the S1 **register gate**, I'll declare the register before any control is built.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== tmux window 2 state ===\" ; tmux capture-pane -p -t main:2 2>/dev/null | tail -15 ; echo \"=== GPU / accel ===\" ; (nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv 2>/dev/null) || (system_profiler SPDisplaysDataType 2>/dev/null | grep -E \"Chipset|VRAM|Metal\" | head) ; echo \"=== torch/mlx backend in harnesses ===\" ; git grep -lE \"import torch|mlx\" -- scripts/experiments/ | head ; echo \"=== device usage ===\" ; git grep -hoE \"(cuda|mps|device_map[^,]*|to\\(.(cuda|mps).\\))\" -- scripts/experiments/*.py 2>/dev/null | sort | uniq -c | sort -rn | head"
}
```

**Summary:** $ echo "=== tmux window 2 state ===" ...

**Output:**
```
Exit code: 0
Stdout:
=== tmux window 2 state ===
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
uv run python scripts/v15/train_td.py --steps 250 --seq-len 256 --batch-size   326.56s user 180.47s system 44% cpu 19:10
.53 total
tee /tmp/v15_ab_exact_lam01.log  0.00s user 0.00s system 0% cpu 19:10.53 total
[26-06-10][20:39:26][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]



=== GPU / accel ===
      Chipset Model: Apple M3 Ultra
      Metal Support: Metal 4
=== torch/mlx backend in harnesses ===
scripts/experiments/U_residual_constraint.py
scripts/experiments/activation_zero_mask.py
scripts/experiments/adjunction_rank_null.py
scripts/experiments/assess_v15_attention.py
scripts/experiments/assess_v15_ffn_retrieval.py
scripts/experiments/assess_v15_gradient_zeros.py
scripts/experiments/attention_execution_trace.py
scripts/experiments/attention_sparsity.py
scripts/experiments/attention_typed_binding.py
scripts/experiments/axis_naming.py
=== device usage ===
 296 mps
  62 cuda
  41 device_map=args.device
  24 device_map=args.device)
  22 device_map="cpu"
  10 device_map=device if device != "mps" else None
  10 device_map="mps"
   8 device_map=device
   5 device_map=dev if dev != "mps" else "auto"
   2 to("mps")
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== locally available models ===\" ; ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -iE \"models--\" | head -30 ; echo \"=== audit harness inventory (recent) ===\" ; ls -t scripts/experiments/*.py 2>/dev/null | head -20 ; echo \"=== sign/routing null harness (the register exemplar) ===\" ; ls -la scripts/experiments/sign_topology_null.py scripts/experiments/manifold_topology_ci.py 2>/dev/null"
}
```

**Summary:** $ echo "=== locally available models ...

**Output:**
```
Exit code: 0
Stdout:
=== locally available models ===
models--allenai--OLMo-2-1124-13B
models--EleutherAI--gpt-neox-20b
models--EleutherAI--pythia-1.4b-deduped
models--EleutherAI--pythia-14m-deduped
models--EleutherAI--pythia-160m
models--EleutherAI--pythia-160m-deduped
models--EleutherAI--pythia-1b-deduped
models--EleutherAI--pythia-2.8b-deduped
models--EleutherAI--pythia-410m
models--EleutherAI--pythia-410m-deduped
models--EleutherAI--pythia-70m-deduped
models--Gen-Verse--MMaDA-8B-Base
models--HuggingFaceTB--SmolLM3-3B
models--microsoft--Phi-4-mini-instruct
models--mistralai--Mistral-7B-v0.3
models--mlx-community--Kokoro-82M-bf16
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
models--showlab--magvitv2
models--unsloth--Qwen3-Coder-480B-A35B-Instruct-GGUF
=== audit harness inventory (recent) ===
scripts/experiments/compare_td_acceptance.py
scripts/experiments/ternary_exact_vs_proxy.py
scripts/experiments/axis_naming_summary.py
scripts/experiments/axis_naming.py
scripts/experiments/manifold_topology_ci.py
scripts/experiments/axis_probe.py
scripts/experiments/manifold_axis_topology_summary.py
scripts/experiments/manifold_axis_topology.py
scripts/experiments/manifold_dimensionality_summary.py
scripts/experiments/manifold_dimensionality_null.py
scripts/experiments/ttd_lambda_weighting.py
scripts/experiments/adjunction_rank_null.py
scripts/experiments/crystal_sieve_repro.py
scripts/experiments/svd_phi_null.py
scripts/experiments/svd_phi_null_summary.py
scripts/experiments/binding_schedule_semantic.py
scripts/experiments/binding_schedule_null.py
scripts/experiments/attention_typed_binding.py
scripts/experiments/mode_semantic_validity.py
scripts/experiments/mode_cluster_validity.py
=== sign/routing null harness (the register exemplar) ===
-rw-r--r--@ 1 mwhitford  staff   7726 Jun 10 07:45 scripts/experiments/manifold_topology_ci.py
-rw-r--r--@ 1 mwhitford  staff  13304 Jun  8 15:35 scripts/experiments/sign_topology_null.py
```

### Thinking

 I'm working with an Apple M3 Ultra Mac Studio with Metal GPU acceleration, where the system has plenty of unified memory and uses MPS for GPU operations. I've got a tmux session ready after finishing a previous A/B test run, so I'm set to continue with the next task.

I have access to a diverse set of local models spanning multiple families and sizes, plus established audit patterns from previous experiments like the sign topology and manifold topology analyses. I should adapt those patterns for this new work.

For the first experiment, I'm testing whether tool-calling has a consensus routing structure across independent models by examining the sign patterns in the routing register. The approach is to take tool-calling prompts alongside control domains like general language and arithmetic, then compare how different foundation models activate their routing structures to see if there's agreement above what we'd expect from random shuffling.

The key is making "agreement" concrete using the same representational dissimilarity methodology from the audit—building RDMs over probe sets for each model and measuring cross-model correlation against shuffled baselines. I need two tests: first, whether tool-calling separates from control domains in the routing register per model, and second, whether that separation pattern is consistent across the independent models.

But there's a crucial distinction here. The user's actual mechanism uses a shared frozen base with deltas trained on tool-calling data, which should show much cleaner agreement than testing fully independent models. So I should run Experiment A first—testing cross-model universality on existing models, which is cheaper and uses existing infrastructure—and if that shows agreement even in this harder setting, the shared-base version is guaranteed to work. If not, the shared-base frame might still succeed since it's a cleaner experimental setup.

There's a more direct way to test the user's mechanism without full delta-plate training: freeze a single base model, run short gradient-based routing adaptation on different tool-calling shards for multiple "users," measure where the resulting flips agree versus a shuffled null, then fold the consensus. This is faithful to the actual mechanism but requires the extraction pipeline to work on a real model, which is heavier setup than Experiment A.

Given the user wants action and GPU time, I should move forward decisively: check what tool-calling probes already exist in the library, examine the exemplar harness to understand the pattern, then propose the concrete Experiment A plan with the register declared and probe strategy ready to execute in tmux.

## Assistant

**Environment confirmed:** Apple **M3 Ultra / Metal 4** (host `olga`), unified memory — that's your "plenty of VRAM." `main:2` is idle at a prompt (free to use); `main:1` has the 5000-step run (won't touch). Local models span 5 families (Pythia, OLMo-2-13B, SmolLM3-3B, Mistral-7B, Qwen3 0.6B→235B) — exactly the audit's cross-family set. Harnesses use `device="mps"`, and `sign_topology_null.py` is the register exemplar.

**Register gate (S1 step 0):** the claim is *"tool-calling has a normal form = a discrete routing structure that independent trainings agree on."* Per the audit lessons that's the **routing/topological register** (gate_proj sign), tested against a **shuffled null** — not magnitude, not geometry. Register: **topological/routing**.

Let me check what tool-calling probes already exist (the crux of the design) and read the exemplar pattern before I build.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== existing tool-calling probes anywhere? ===\" ; git grep -ilE \"tool.call|tool_call|get_weather|function.call|\\\"role\\\".*tool|<tool\" -- probes/ src/ lattice/ 2>/dev/null | head ; echo \"--- probe library categories/tags ---\" ; git grep -hoE \"category=\\\"[a-z_]+\\\"|tags=\\[[^]]*\\]\" -- src/verbum/probes/ 2>/dev/null | sort | uniq -c | sort -rn | head -20 ; echo \"=== probe json sets ===\" ; ls probes/ 2>/dev/null ; echo \"=== how sign_topology_null loads models + measures (head) ===\"; sed -n '1,60p' scripts/experiments/sign_topology_null.py"
}
```

**Summary:** $ echo "=== existing tool-calling pro...

**Output:**
```
Exit code: 0
Stdout:
=== existing tool-calling probes anywhere? ===
lattice/backbone_seed.json
lattice/basin_probes.json
lattice/basins-v1/basin_lattice.json
lattice/crystal_spine/probes.json
lattice/diverse_corpus.json
lattice/lattice_5model/universal_lattice.json
lattice/reduction_chain_probes.json
lattice/tool_crystal/probes.json
lattice/tool_crystal_run.log
lattice/universal_lattice.json
--- probe library categories/tags ---
   1 category="null_baseline"
=== probe json sets ===
__init__.py
__pycache__
binding.json
classify.json
compile-gradient.json
decompile.json
exemplar-sweep.json
extract.json
fact_recall_extended.json
fact_recall.json
gate-ablation-base.json
gate-ablation.json
lambda_kernel_probes.py
README.md
summarize.json
translate.json
v0-behavioral.json
=== how sign_topology_null loads models + measures (head) ===
#!/usr/bin/env python3
"""Sign-topology null — is `cos(sign(W)@x, W@x) ≈ 0.84` crystal-specific,
or generic to ANY matrix with that entry distribution?

THE CLAIM (crystal-universality.md §"Why Ternary Works"):
  "Sign captures topology. `sign(W) @ x` correlates 0.84 with `W @ x`.
   The sign captures the routing decision; magnitude is calibration.
   Ternary IS topology."

This is load-bearing claim #1 in audit-registry.md (load: CRITICAL — the
whole sieve program). The suspected confound:

  cos(sign(W)@x, W@x) may be high for ANY matrix, because sign(W_ij) and
  W_ij are PERFECTLY correlated entry-wise — the large-|x_j| input
  dimensions dominate both Σ_j W_ij x_j and Σ_j sign(W_ij) x_j regardless
  of whether W has crystalline structure. If so, 0.84 is a generic
  property of high-dim linear maps, not evidence of a discrete crystal.

THE DISCRIMINATING CONTROL:
  Hold the REAL activations x fixed (the inputs the true model actually
  produces). Compute cos(sign(W)@x, W@x) for three weight variants:
    (model)    — the trained weight W
    (random)   — iid Gaussian, matched global std, N seeds
    (shuffled) — entries of W permuted, N seeds (identical sign-sparsity
                 and magnitude marginal, structure destroyed)

  If model ≈ random ≈ shuffled  → 0.84 is GENERIC; sign-topology evidence
                                   REFUTED as crystal-specific.
  If model ≫ controls            → crystal signs carry structure the
                                   marginal distribution does not → REAL.

We report mean ± std over seeds for each control, plus the separation
(model − control_mean) in units of control std (z-score), per layer and
weight type, then a one-line verdict.

Usage:
    uv run python scripts/experiments/sign_topology_null.py \
        --model Qwen/Qwen3-0.6B --device mps --n-seed 20

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "sign-topology-null"
```

### Thinking

 I see there's already prior work on tool-calling probes in the crystal framework, along with a universal lattice model that extends across five domains. Let me examine the existing probes and run logs to understand what's been discovered so far.

## Assistant

There's prior tool-calling work: `lattice/tool_crystal/probes.json` + `lattice/tool_crystal_run.log`, and `lattice/lattice_5model/universal_lattice.json`. That's the "probes into tool calling" you remember. Let me read what was already found there before designing the new experiment.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== tool_crystal probes (structure + count) ===\" ; python3 -c \"import json; d=json.load(open('lattice/tool_crystal/probes.json')); print('type:',type(d).__name__); (print('keys:',list(d.keys())) if isinstance(d,dict) else print('len:',len(d))); import pprint; pprint.pprint(d if isinstance(d,dict) else d[:3])\" 2>/dev/null | head -60 ; echo ; echo \"=== tool_crystal run log (what was found) ===\" ; tail -50 lattice/tool_crystal_run.log 2>/dev/null"
}
```

**Summary:** $ echo "=== tool_crystal probes (stru...

**Output:**
```
Exit code: 0
Stdout:
=== tool_crystal probes (structure + count) ===
type: list
len: 196
[{'domain': 'recognition',
  'prompt': '<|im_start|>system\n'
            'You are a helpful assistant.\n'
            '\n'
            '# Tools\n'
            '\n'
            'You may call one or more functions to assist with the user '
            'query.\n'
            '\n'
            'You are provided with function signatures within XML tags:\n'
            '<tools>\n'
            '{"type": "function", "function": {"name": "get_weather", '
            '"description": "Get current weather for a city", "parameters": '
            '{"type": "object", "properties": {"city": {"type": "string", '
            '"description": "City name"}, "units": {"type": "string", "enum": '
            '["celsius", "fahrenheit"], "default": "celsius"}}, "required": '
            '["city"]}}}\n'
            '{"type": "function", "function": {"name": "web_search", '
            '"description": "Search the web for recent information", '
            '"parameters": {"type": "object", "properties": {"query": {"type": '
            '"string", "description": "Search query"}, "limit": {"type": '
            '"integer", "description": "Max results", "default": 10}, "sort": '
            '{"type": "string", "enum": ["relevance", "date"], "default": '
            '"relevance"}}, "required": ["query"]}}}\n'
            '</tools>\n'
            '<|im_end|>\n'
            '<|im_start|>user\n'
            "What's the current weather in Tokyo?<|im_end|>\n"
            '<|im_start|>assistant\n',
  'subdomain': 'recognition/tool',
  'topic': 'weather'},
 {'domain': 'recognition',
  'prompt': '<|im_start|>system\n'
            'You are a helpful assistant.<|im_end|>\n'
            '<|im_start|>user\n'
            'Describe what a rainy autumn day in Tokyo feels like.<|im_end|>\n'
            '<|im_start|>assistant\n',
  'subdomain': 'recognition/no_tool',
  'topic': 'weather'},
 {'domain': 'recognition',
  'prompt': '<|im_start|>system\n'
            'You are a helpful assistant.\n'
            '\n'
            '# Tools\n'
            '\n'
            'You may call one or more functions to assist with the user '
            'query.\n'
            '\n'
            'You are provided with function signatures within XML tags:\n'
            '<tools>\n'
            '{"type": "function", "function": {"name": "get_weather", '
            '"description": "Get current weather for a city", "parameters": '
            '{"type": "object", "properties": {"city": {"type": "string", '
            '"description": "City name"}, "units": {"type": "string", "enum": '
            '["celsius", "fahrenheit"], "default": "celsius"}}, "required": '
            '["city"]}}}\n'
            '{"type": "function", "function": {"name": "web_search", '
            '"description": "Search the web for recent information", '

=== tool_crystal run log (what was found) ===
    Layer 24: RDM (196, 196), mean_sim=0.8705, off_diag_mean=0.8698
    Layer 28: RDM (196, 196), mean_sim=0.8523, off_diag_mean=0.8516
    Layer 32: RDM (196, 196), mean_sim=0.8767, off_diag_mean=0.8760
    Layer 36: RDM (196, 196), mean_sim=0.8925, off_diag_mean=0.8920
    Layer 39: RDM (196, 196), mean_sim=0.6104, off_diag_mean=0.6084

3. Cross-domain analysis...

────────────────────────────────────────────────────────────────────────────────────────────────
 Layer |  ToolSelf | SchemaSelf | LambdaSelf | Tool×Lambda | Tool×Prose |   RecogΔ | Selectivity
────────────────────────────────────────────────────────────────────────────────────────────────
     0 |    0.9361 |    0.9981 |    0.9979 |    0.9913 |    0.9586 |    0.0009 |   -0.0119  ◀ SHARED
     4 |    0.9162 |    0.9904 |    0.9911 |    0.9683 |    0.9346 |    0.0000 |   -0.0099  ◀ SHARED
     8 |    0.8957 |    0.9912 |    0.9918 |    0.9527 |    0.9133 |    0.0023 |   -0.0098  ◀ SHARED
    12 |    0.8137 |    0.9859 |    0.9900 |    0.8942 |    0.8310 |    0.0001 |   -0.0105  ◀ SHARED
    16 |    0.8254 |    0.9788 |    0.9832 |    0.9204 |    0.8397 |    0.0056 |   -0.0086  ◀ SHARED
    20 |    0.8738 |    1.0000 |    1.0000 |    0.9999 |    0.9305 |   -0.0000 |   -0.0314  ◀ SHARED
    24 |    0.8487 |    1.0000 |    1.0000 |    0.9999 |    0.9166 |   -0.0000 |   -0.0385  ◀ SHARED
    28 |    0.8276 |    1.0000 |    1.0000 |    0.9999 |    0.9045 |   -0.0000 |   -0.0444  ◀ SHARED
    32 |    0.8559 |    1.0000 |    1.0000 |    0.9999 |    0.9206 |   -0.0000 |   -0.0364  ◀ SHARED
    36 |    0.8745 |    0.9999 |    0.9999 |    0.9995 |    0.9306 |   -0.0000 |   -0.0311  ◀ SHARED
    39 |    0.6062 |    0.9215 |    0.9095 |    0.6991 |    0.5711 |    0.0324 |    0.0298  
────────────────────────────────────────────────────────────────────────────────────────────────
  ToolSelf    = mean cosine sim within all tool-domain probes
  SchemaSelf  = mean cosine sim within schema_binding probes
  LambdaSelf  = mean cosine sim within lambda_calculus control probes
  Tool×Lambda = mean cosine sim between schema_binding & lambda probes
  Tool×Prose  = mean cosine sim between tool probes & prose controls
  RecogΔ      = recognition/tool cluster sim minus recognition/no_tool
  Selectivity = (ToolSelf−Tool×Prose)/(ToolSelf+Tool×Prose)

  ── Hypothesis Verdict ──
  STRONG SUPPORT: Tool×Lambda overlap peaks at 1.000 at layer 20.
  The tool-calling crystal SHARES circuitry with the lambda crystal.
  Tool calling IS lambda calculus applied to JSON schema (as hypothesised).
  Max selectivity: 0.030
  (Selectivity = how much tool probes cluster relative to prose controls)

4. Saving outputs...
  💾 lattice/tool_crystal/rdms.npz (1166.0 KB)
  💾 lattice/tool_crystal/hidden_states.npz (20215.2 KB)
  💾 lattice/tool_crystal/analysis.json (70.0 KB)
  💾 lattice/tool_crystal/probes.json (177.2 KB)

========================================================================
  Done in 129s
  Probes: 196
  Layers: [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 39]
  Output: lattice/tool_crystal/
========================================================================
```

### Thinking

 Looking at the prior tool-calling analysis, I found 196 probes across different conditions and the initial verdict suggested a perfect overlap between tool calling and lambda calculus at layer 20. But when I apply stricter audit standards, the selectivity metric breaks down—it's showing near-zero values, which undermines the confidence in that claim.

The core issue is that raw cosine similarity in high-dimensional residual streams is generically high across almost everything, creating a common-mode confound that masks whether the overlap is actually tool-specific or just a baseline artifact. The "1.000 at layer 20" isn't evidence of tool-lambda structure; it's the common mode where everything clusters together. This is the same confound the audit caught repeatedly in earlier analyses.

So the prior tool-calling result is exactly what the audit would flag as over-interpreted—high raw cosine masking zero selectivity. To fix this, I need to redesign the experiment to use the routing register instead of hidden states, apply common-mode removal, test against a shuffled null, and measure cross-model consensus rather than within-model patterns.

The prior work was single-model (Qwen, likely the 14B variant based on the 40-layer count) using raw cosine. The new experiment adds routing register, CMR, null baseline, and cross-model agreement—which directly tests whether tool-calling has a real, replicable normal form across independent models or if it's just a within-model artifact. This becomes a decisive test of the distributed-consensus hypothesis and would essentially be a new audit row on tool-calling selectivity.

For the design, I'm reusing the 196 existing tool_crystal probes (which already have good controls across tool/no-tool/schema variations) and testing across five model families—Qwen, Mistral, SmolLM, OLMo, Pythia—to check both selectivity within each model and agreement across them. The tricky part is the chat template: Qwen's special tokens like `<|im_start|>` won't tokenize the same way in other models, so for a fair cross-model comparison I should render the probes as plain text (system + tools + user query + "assistant:") without model-specific tokens, keeping everything model-agnostic.

For measurement, I'm capturing the gate projection activations (or their sign, which carries routing topology) at the final token position per layer, then building a representational dissimilarity matrix over probes in the routing register. After applying common-mode removal to kill the generic prose signal that inflated the prior results, I'll test whether tool vs no-tool separates above chance and whether the post-CMR RDMs correlate across models—that's the normal-form test. It's computationally cheap (just forward passes, ~5 models × 196 probes on M3 Ultra) and should give an audit-grade answer.

This isn't quite the full distributed consensus experiment with delta-folding, but it's the right cheap first step: does a tool-calling normal form exist in the routing register and agree across independent trainings? That's the prerequisite for the whole scheme, and it'll also correct what looks like an over-read in the prior tool_crystal result.

The user gave a clear go-ahead, so I should propose this concretely, declare the register, and start building. I'll set up a task list and create the harness by mirroring the existing sign_topology_null.py and manifold_axis_topology.py code. Before I build, let me quickly check what script generated tool_crystal and find the existing gate-capture infrastructure so I can reuse it.

## Assistant

This is the key find. The prior `tool_crystal` run (single Qwen model) concluded **"STRONG SUPPORT: tool calling IS lambda calculus"** — but look at the actual numbers: **Selectivity ≈ −0.01 to +0.03, every layer marked "◀ SHARED"**, and the "1.000 at layer 20" is the generic common mode (Schema/Lambda/Tool×Lambda *all* read 0.9999 there). That's a textbook instance of the project's own meta-pattern — **a raw-cosine instrument in the wrong register manufacturing a result that's actually at the common-mode null.** The audit program would flag this immediately.

So the experiment almost designs itself, and it's high-value: **redo the tool-calling normal-form test with audit-grade methodology** — routing register (gate_proj sign), common-mode removal, a shuffled null, and the part the prior run never did: **cross-model consensus**. That directly tests your hypothesis and corrects a likely over-read.

Let me see the generator + gate-capture infra to reuse, then I'll build.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== who generated tool_crystal? ===\" ; git grep -ln \"tool_crystal\" -- scripts/ lattice/ 2>/dev/null | head ; echo \"=== probe domain distribution ===\" ; python3 -c \"import json,collections; d=json.load(open('lattice/tool_crystal/probes.json')); c=collections.Counter((p.get('domain'),p.get('subdomain')) for p in d); [print(f'{n:4d}  {k}') for k,n in sorted(c.items())]\" ; echo \"=== existing gate_proj capture pattern (sign/routing register) ===\" ; git grep -ln -E \"gate_proj|mlp\\.gate|act_fn|gate.*sign|hook.*gate\" -- scripts/experiments/ | head ; echo \"--- common-mode removal pattern (CMR) ---\" ; git grep -ln -iE \"common.mode|cmr|centered|center.*rdm\" -- scripts/experiments/ | head"
}
```

**Summary:** $ echo "=== who generated tool_crysta...

**Output:**
```
Exit code: 0
Stdout:
=== who generated tool_crystal? ===
lattice/tool_crystal_run.log
scripts/v12/probe_tool_crystal.py
=== probe domain distribution ===
   7  ('control', 'control/code')
   8  ('control', 'control/lambda_calculus')
   8  ('control', 'control/prose')
   7  ('control', 'control/pure_math')
   1  ('format', 'format/args_reordered')
   1  ('format', 'format/args_reordered_2')
   1  ('format', 'format/hermes_2args')
   1  ('format', 'format/hermes_3args')
   1  ('format', 'format/hermes_complete')
   1  ('format', 'format/hermes_complete_2args')
   3  ('format', 'format/hermes_partial_args')
   2  ('format', 'format/markdown_json')
   1  ('format', 'format/no_tool_prose')
   1  ('format', 'format/no_tool_response')
   1  ('format', 'format/parallel_calls')
   1  ('format', 'format/parallel_different_tools')
   1  ('format', 'format/partial_open_brace')
   1  ('format', 'format/partial_truncated')
   1  ('format', 'format/plaintext_nl')
   1  ('format', 'format/plaintext_python_style')
   3  ('format', 'format/raw_json_partial')
   3  ('format', 'format/reasoning_prefix')
   1  ('format', 'format/vague_binding')
   2  ('format', 'format/xml_structured')
   2  ('format', 'format/yaml_structured')
  20  ('recognition', 'recognition/no_tool')
  20  ('recognition', 'recognition/tool')
   2  ('schema_binding', 'schema_binding/schema_1arg_expr')
   1  ('schema_binding', 'schema_binding/schema_1arg_expr_derived')
   1  ('schema_binding', 'schema_binding/schema_1arg_expr_func')
   1  ('schema_binding', 'schema_binding/schema_1arg_expr_verbatim')
   2  ('schema_binding', 'schema_binding/schema_1arg_path')
   1  ('schema_binding', 'schema_binding/schema_1arg_path_short')
   5  ('schema_binding', 'schema_binding/schema_1arg_string')
   3  ('schema_binding', 'schema_binding/schema_2arg_enum')
   1  ('schema_binding', 'schema_binding/schema_2arg_enum_sort')
   1  ('schema_binding', 'schema_binding/schema_2arg_int')
   1  ('schema_binding', 'schema_binding/schema_2arg_int_explicit')
   1  ('schema_binding', 'schema_binding/schema_2arg_int_small')
   2  ('schema_binding', 'schema_binding/schema_2arg_path_encoding')
   1  ('schema_binding', 'schema_binding/schema_3arg_explicit')
   1  ('schema_binding', 'schema_binding/schema_3arg_mixed')
   1  ('schema_binding', 'schema_binding/schema_5arg_complex')
   1  ('schema_binding', 'schema_binding/schema_6arg_all')
   1  ('schema_binding', 'schema_binding/schema_array_1to')
   1  ('schema_binding', 'schema_binding/schema_array_2to')
   1  ('schema_binding', 'schema_binding/schema_array_3to')
   1  ('schema_binding', 'schema_binding/schema_array_attachment')
   1  ('schema_binding', 'schema_binding/schema_array_to_cc')
   2  ('schema_binding', 'schema_binding/schema_code_derived')
   1  ('schema_binding', 'schema_binding/schema_code_timeout')
   2  ('schema_binding', 'schema_binding/schema_code_verbatim')
   1  ('schema_binding', 'schema_binding/schema_datetime_derived')
   1  ('schema_binding', 'schema_binding/schema_datetime_duration')
   1  ('schema_binding', 'schema_binding/schema_datetime_explicit')
   1  ('schema_binding', 'schema_binding/schema_datetime_full')
   1  ('schema_binding', 'schema_binding/schema_datetime_relative')
   1  ('schema_binding', 'schema_binding/schema_name_map_fragment')
   1  ('schema_binding', 'schema_binding/schema_name_map_implicit')
   1  ('schema_binding', 'schema_binding/schema_name_map_informal')
   1  ('schema_binding', 'schema_binding/schema_name_map_query')
   1  ('schema_binding', 'schema_binding/schema_name_map_tilde')
   1  ('schema_binding', 'schema_binding/schema_nested_1filter')
   1  ('schema_binding', 'schema_binding/schema_nested_2filters')
   1  ('schema_binding', 'schema_binding/schema_nested_2filters_limit')
   1  ('schema_binding', 'schema_binding/schema_nested_3filters')
   1  ('schema_binding', 'schema_binding/schema_nested_3filters_bool')
   1  ('schema_binding', 'schema_binding/schema_sql_3arg')
   1  ('schema_binding', 'schema_binding/schema_sql_derived')
   1  ('schema_binding', 'schema_binding/schema_sql_filter')
   1  ('schema_binding', 'schema_binding/schema_sql_noparams')
   1  ('schema_binding', 'schema_binding/schema_sql_verbatim_params')
   1  ('selection', 'selection/all_tools_events')
   1  ('selection', 'selection/all_tools_facts')
   1  ('selection', 'selection/all_tools_price')
   1  ('selection', 'selection/all_tools_ranking')
   1  ('selection', 'selection/all_tools_travel')
   3  ('selection', 'selection/bash_vs_file')
   1  ('selection', 'selection/bash_vs_file_disk')
   1  ('selection', 'selection/bash_vs_file_find')
   1  ('selection', 'selection/bash_vs_file_listing')
   1  ('selection', 'selection/bash_vs_file_proc')
   4  ('selection', 'selection/calc_vs_python')
   1  ('selection', 'selection/calc_vs_python_conversion')
   1  ('selection', 'selection/calc_vs_python_plot')
   1  ('selection', 'selection/calc_vs_python_rng')
   1  ('selection', 'selection/calc_vs_python_simple')
   1  ('selection', 'selection/clear_bash')
   1  ('selection', 'selection/clear_calc')
   1  ('selection', 'selection/clear_file')
   1  ('selection', 'selection/clear_search')
   1  ('selection', 'selection/clear_weather')
   1  ('selection', 'selection/multi_bash_then_count')
   1  ('selection', 'selection/multi_calc_then_average')
   1  ('selection', 'selection/multi_search_then_convert')
   1  ('selection', 'selection/multi_search_then_time')
   1  ('selection', 'selection/multi_search_then_weather')
   3  ('selection', 'selection/weather_vs_search')
   1  ('selection', 'selection/weather_vs_search_general')
   1  ('selection', 'selection/weather_vs_search_historical')
   1  ('selection', 'selection/wrong_tool_creative')
   1  ('selection', 'selection/wrong_tool_definition')
   1  ('selection', 'selection/wrong_tool_factual')
   1  ('selection', 'selection/wrong_tool_math')
   1  ('selection', 'selection/wrong_tool_philosophical')
=== existing gate_proj capture pattern (sign/routing register) ===
scripts/experiments/U_residual_constraint.py
scripts/experiments/activation_zero_mask.py
scripts/experiments/beta_expansion.py
scripts/experiments/binding_prep_lowrank.py
scripts/experiments/combinator_addressing.py
scripts/experiments/combined_compression.py
scripts/experiments/confidence_gate.py
scripts/experiments/continuation_placement_test.py
scripts/experiments/copy_program.py
scripts/experiments/crystal_circuit_types.py
--- common-mode removal pattern (CMR) ---
scripts/experiments/adjunction_rank_null.py
scripts/experiments/crystal_depth_scan.py
scripts/experiments/crystal_phi_permnull.py
scripts/experiments/crystal_zero_prediction.py
scripts/experiments/crystal_zero_v2.py
scripts/experiments/fact_retrieval_isig.py
scripts/experiments/gamma_sort_order.py
scripts/experiments/manifold_axis_topology.py
scripts/experiments/manifold_dimensionality_null.py
scripts/experiments/manifold_dimensionality_summary.py
```

### Thinking

 I've got a well-organized probe set of 196 tool_crystal probes across different domains like recognition, schema binding, selection, and format control, plus a prior generator script that reuses existing gate-capture logic and patterns from various harnesses.

The plan is to build a new harness that loads these probes, runs them through multiple cross-family models to capture routing register activations at the final token across mid-to-late layers, then applies RDM analysis with common-mode removal to test both within-model selectivity (tool vs control separation) and cross-model consensus. I'll use manifold_axis_topology.py as a template since it already has the CMR and shuffled-null structure I need, combined with the probe loading from probe_tool_crystal.py.

I should be disciplined about this: set up a task list, study those two reference harnesses, write the new harness, smoke test on a couple small models first, then scale up to the full five families. One thing I need to be careful about is how to handle chat templates in the probes.

## Assistant

Everything needed is in place: a well-structured **196-probe set** (recognition tool/no_tool 20+20, schema_binding ~50, selection ~40, format ~30, lambda/prose/code/math controls ~30), the prior generator `scripts/v12/probe_tool_crystal.py` to reuse gate-capture, and `manifold_axis_topology.py` — the s211 cross-family harness that already does **common-mode removal + shuffled-null RDM agreement** (the exact template). Let me lay out a plan.

### Thinking

 I'm extracting the IDs from the content.

## Assistant

Now let me read the two reference harnesses to mirror their exact CMR/null/gate-capture patterns rather than reinvent.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/manifold_axis_topology.py"
}
```

**Summary:** Reading manifold_axis_topology.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: spectral/semantic
"""The common axis + the topology of the combinator manifold.

FOLLOW-UP to manifold_dimensionality_null.py, which found: the universal
cross-family structure of the 9 combinator operations is REAL (separation
p=0.0005 everywhere) but ~RANK-1 (CMR collapses cross-family agreement
0.79 -> -0.19) and lives in the PROBABILITIES more than the activations.
Two questions remain:

  PART A — WHAT IS THE COMMON AXIS?  The shared structure is ~1-dimensional.
    What does that single dominant axis encode? Candidates (register: semantic):
      - combinator identity (categorical eta^2)
      - compositional depth = attention-entropy gradient (crystal-validity §4):
            W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19
      - next-token entropy (how DECIDED the continuation is; fact/I = sharp)
      - prompt length (confound)
    And: is it the SAME axis across all families (sign-aligned axis-1 corr)?

  PART B — HOW MUCH OF THE MANIFOLD IS TOPOLOGY?  (register: geometric)
    topology-gradient-separation.md: GD lays structure as SIGN (routing/
    topology, the dominant share) vs MAGNITUDE (value/calibration). Decompose
    the last-layer hidden state h -> sign(h) | |h| | full, build a cosine RDM
    from each, and measure how much of the combinator structure (separation +
    full-RDM reconstruction) the SIGN carries alone. Past sessions put ~77%+ of
    computation in the topology; this measures it directly on this manifold.
    BONUS (semantic topology): support-RDM = Jaccard on the top-64 next tokens
    ("which tokens get mass" = routing) vs the full Hellinger value-RDM.

This script is PER-MODEL (one invocation each). It saves rich artifacts
(hidden, top-k, entropy, axis coords, RDMs) so the cross-model verdict
(manifold_axis_topology_summary.py) needs no re-run.

Usage:
  uv run python scripts/experiments/manifold_axis_topology.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16
License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from verbum.probes.library import crystal_probes

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "manifold-axis-topology"
TOPK = 64

# compositional-depth scalar (crystal-validity-and-fidelity.md §4 attention entropy)
DEPTH = {"W": 0.90, "I": 1.00, "K": 1.02, "C": 1.05, "B": 1.05,
         "WHNF": 1.09, "Y": 1.14, "D": 1.19}  # S omitted (not in the gradient)


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length):
    """Return hidden [N x d] f32, full probs [N x V] f32, entropy [N],
    topk_idx [N x TOPK], prompt_len [N]."""
    n = len(prompts)
    hidden = probs = None
    ent = np.empty(n, np.float32)
    topk = np.empty((n, TOPK), np.int32)
    plen = np.empty(n, np.int32)
    for i, text in enumerate(prompts):
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc, output_hidden_states=True)
        logits = out.logits[0, -1].float()
        p = torch.softmax(logits, dim=-1)
        h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
        pn = p.cpu().numpy().astype(np.float32)
        if hidden is None:
            hidden = np.empty((n, h.shape[0]), np.float32)
            probs = np.empty((n, pn.shape[0]), np.float32)
        hidden[i] = h
        probs[i] = pn
        ent[i] = float(-(p * (p + 1e-30).log()).sum().cpu())
        topk[i] = torch.topk(p, TOPK).indices.cpu().numpy().astype(np.int32)
        plen[i] = int(enc["input_ids"].shape[1])
        del out, logits, p
        if (i + 1) % 50 == 0:
            log(f"    {i + 1}/{n}")
    return hidden, probs, ent, topk, plen


# ---- RDMs -------------------------------------------------------------------
def cosine_rdm(X):
    X = X.astype(np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-30
    cos = np.clip((X / n) @ (X / n).T, -1, 1)
    d = 1.0 - cos
    np.fill_diagonal(d, 0.0)
    return d


def hellinger_rdm(probs):
    sq = np.sqrt(np.clip(probs, 0, None)).astype(np.float64)
    nrm = np.einsum("ij,ij->i", sq, sq)
    d2 = np.clip(nrm[:, None] + nrm[None, :] - 2.0 * (sq @ sq.T), 0, None)
    d = np.sqrt(d2) / np.sqrt(2.0)
    np.fill_diagonal(d, 0.0)
    return d


def jaccard_rdm(topk):
    n = topk.shape[0]
    sets = [set(topk[i].tolist()) for i in range(n)]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j])
            D[i, j] = D[j, i] = 1.0 - inter / max(union, 1)
    return D


# ---- analysis ---------------------------------------------------------------
def upper(D):
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def mds_coords(D, k=3):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:k]
    w = np.clip(w[idx], 0, None)
    return V[:, idx] * np.sqrt(w)            # [n x k]


def separation(D, labels, n_perm, seed):
    lab = np.array(labels)
    iu = np.triu_indices_from(D, k=1)
    dv = D[iu]

    def gap(L):
        same = L[iu[0]] == L[iu[1]]
        return dv[~same].mean() - dv[same].mean()

    obs = gap(lab)
    rng = np.random.default_rng(seed)
    null = np.array([gap(rng.permutation(lab)) for _ in range(n_perm)])
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return {"gap": float(obs), "null_mean": float(null.mean()), "p_value": p}


def agree(Da, Db):
    return float(np.corrcoef(upper(Da), upper(Db))[0, 1])


def eta_squared(coord, labels):
    """Fraction of axis variance explained by combinator identity."""
    lab = np.array(labels)
    grand = coord.mean()
    ss_tot = ((coord - grand) ** 2).sum() + 1e-30
    ss_between = sum(len(coord[lab == u]) * (coord[lab == u].mean() - grand) ** 2
                     for u in set(lab))
    return float(ss_between / ss_tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    probes = crystal_probes()
    if args.limit and args.limit < len(probes):
        rng = np.random.default_rng(args.seed)
        by = {}
        for p in probes:
            by.setdefault(p.combinator, []).append(p)
        per = max(2, args.limit // len(by))
        probes = [by[k][i] for k in sorted(by)
                  for i in rng.permutation(len(by[k]))[:per]]
    prompts = [p.prompt for p in probes]
    labels = [p.combinator for p in probes]
    log(f"[{args.model}] {len(prompts)} probes")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    log("  forward passes ...")
    hidden, probs, ent, topk, plen = collect(model, tok, args.device, prompts,
                                             args.max_length)
    vocab = int(probs.shape[1]); width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    log("  building RDMs (prob full/support; hidden full/sign/mag) ...")
    rdm = {
        "prob_full": hellinger_rdm(probs),
        "prob_support": jaccard_rdm(topk),
        "hidden_full": cosine_rdm(hidden),
        "hidden_sign": cosine_rdm(np.sign(hidden)),
        "hidden_mag": cosine_rdm(np.abs(hidden)),
    }

    out = {"model": args.model, "dtype": args.dtype, "n_probes": len(prompts),
           "vocab": vocab, "hidden_width": width, "n_perm": args.n_perm,
           "git_sha": git_sha(), "results": {}}

    # separation per RDM
    for name, D in rdm.items():
        out["results"][name] = {"separation": separation(D, labels, args.n_perm, args.seed)}

    # PART A — the common axis (semantic, prob_full)
    coords = mds_coords(rdm["prob_full"], k=3)
    ax1 = coords[:, 0]
    depth_vec = np.array([DEPTH.get(l, np.nan) for l in labels])
    mask = ~np.isnan(depth_vec)
    def safe_corr(a, b, m=None):
        if m is not None:
            a, b = a[m], b[m]
        if np.std(a) < 1e-12 or np.std(b) < 1e-12:
            return float("nan")
        return float(np.corrcoef(a, b)[0, 1])
    out["axis"] = {
        "eta2_combinator": eta_squared(ax1, labels),
        "corr_depth": safe_corr(ax1, depth_vec, mask),
        "corr_entropy": safe_corr(ax1, ent.astype(np.float64)),
        "corr_promptlen": safe_corr(ax1, plen.astype(np.float64)),
        "var_top1": float((coords[:, 0] ** 2).sum() /
                          ((coords ** 2).sum() + 1e-30)),
    }

    # PART B — topology fraction (geometric, hidden)
    full = rdm["hidden_full"]
    sep_full = out["results"]["hidden_full"]["separation"]["gap"]
    sep_sign = out["results"]["hidden_sign"]["separation"]["gap"]
    sep_mag = out["results"]["hidden_mag"]["separation"]["gap"]
    out["topology"] = {
        "sep_full": sep_full, "sep_sign": sep_sign, "sep_mag": sep_mag,
        "sep_frac_sign": float(sep_sign / (sep_sign + sep_mag + 1e-30)),
        "agree_sign_full": agree(rdm["hidden_sign"], full),
        "agree_mag_full": agree(rdm["hidden_mag"], full),
        # semantic parallel: support(topology) vs full value RDM
        "prob_agree_support_full": agree(rdm["prob_support"], rdm["prob_full"]),
        "prob_sep_support": out["results"]["prob_support"]["separation"]["gap"],
        "prob_sep_full": out["results"]["prob_full"]["separation"]["gap"],
    }

    out["elapsed_s"] = round(time.time() - t0, 1)
    log(f"  AXIS: eta2(comb)={out['axis']['eta2_combinator']:.3f} "
        f"depth r={out['axis']['corr_depth']:.3f} ent r={out['axis']['corr_entropy']:.3f} "
        f"plen r={out['axis']['corr_promptlen']:.3f}")
    log(f"  TOPO: sep full={sep_full:.4f} sign={sep_sign:.4f} mag={sep_mag:.4f} "
        f"sign-frac={out['topology']['sep_frac_sign']:.2f} | "
        f"agree sign={out['topology']['agree_sign_full']:.3f} "
        f"mag={out['topology']['agree_mag_full']:.3f}")

    np.savez_compressed(
        RESULTS_DIR / f"{safe}.npz",
        hidden=hidden.astype(np.float16), topk=topk, entropy=ent,
        prompt_len=plen, labels=np.array(labels),
        axis_coords=coords.astype(np.float32),
        **{f"rdm_{k}": v.astype(np.float32) for k, v in rdm.items()})
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

### Thinking

 I'm setting up a template that captures the forward pass with hidden states and probabilities, then computes multiple distance metrics like cosine, Hellinger, and Jaccard. The separation test checks label selectivity within a model, while the agreement test measures cross-model RDM correlation, and I'm also decomposing the hidden representations into sign and magnitude components to examine the topology register split.

For the tool-calling experiment, I need to load the probes with domain labels and render them as plain text by converting the Qwen chat markers (like `<|im_start|>` and `<|im_end|>`) into simpler role labels for fair cross-model comparison. The critical adaptation is capturing the gate projection activation sign across layers as the routing register instead of just the final hidden state, since that's where the routing topology lives.

Given the dimensionality challenge—concatenating all gate activations across 36 layers would be massive—I'll capture gate_proj per layer at a subset of layers (similar to the prior approach), and also keep the residual hidden state to show the contrast: raw hidden cosine will look strong and shared (common-mode), but the routing register with CMR is the real discriminator. This dual capture design directly demonstrates that the prior "strong support" was just common-mode noise, and the gate-sign routing register is the correct instrument.

For CMR, I need to implement it explicitly here since the current script doesn't have it—I'll center activations by subtracting the per-feature mean across probes, which removes the common mode that inflates cosine similarity. I'll build RDMs on both raw and mean-centered representations for hidden and gate-sign, then test selectivity on the centered versions.

The key tests are within-model selectivity (separation on domain labels, especially the recognition/tool vs recognition/no_tool contrast, with permutation null) and cross-model consensus (agreement between model RDMs post-CMR).

For the architecture variation, I'm realizing that Pythia doesn't have gate_proj since it uses GELU instead of SwiGLU, so I need to define the routing register more generically as the sign of the FFN intermediate activation post-activation—for gated models that's the gate itself, but for Pythia it would be the hidden layer sign.

I could drop Pythia to keep things clean with just the four SwiGLU families (Qwen3, Mistral, SmolLM3, OLMo-2), but including Pythia would give me stronger cross-architecture validation. So I'll support both: detect which module exists and capture either gate_proj or dense_h_to_4h accordingly, labeling which architecture type it is. Then I'll implement forward hooks on the appropriate gate module to grab the FFN intermediate activation at the final token position.

Since model structures vary (LLaMA-style uses `model.model.layers`, Pythia uses `model.gpt_neox.layers`), I'll iterate through named modules and match on the module name patterns, registering hooks on all matching gate modules and storing their outputs indexed by layer. For memory efficiency, I'll only keep a subset of evenly-spaced layers and store the signs as int8, which keeps the footprint manageable. I'll also capture hidden states for the raw-cosine baseline comparison, then compute RDMs per layer on the fly rather than storing all raw activations.

Since gate activations have different feature dimensions across models, cross-model agreement needs to happen at the RDM level (probe-aligned 196×196 matrices), not in the feature space itself. So I'll save per-layer RDMs for both routing and hidden states, in both raw and feature-centered forms, along with domain labels and selectivity stats. The summary script will then load all models' RDMs and compute cross-model agreement as mean pairwise RDM correlation against a shuffled-probe null.

Now I'll write the harness script, starting with the core functions: loading probes, finding gate modules, collecting routing activations and hidden states, building RDMs with a sign variant, applying feature centering for CMR, and running selectivity tests.

For the selectivity tests I need to compute the recognition-tool vs recognition-no-tool gap plus permutation null, and the tool-all-non-control vs control gap plus permutation null. I'll structure this as two separate scripts: one per-model that emits RDM npz files and JSON stats, and a summary script for cross-model agreement. I'm also adding a sign-based RDM variant using the gate pre-activation sign, plus the raw gate cosine and their CMR versions, and I'll include the raw hidden cosine to show the shared common mode contrast.

For rendering the Qwen chat tokens in the probes to plain text, I'll strip the special tokens so the comparison stays fair across models.

Now I'm starting to write the per-model script.

## Assistant

`manifold_axis_topology.py` is the ideal template — it already has `separation()` (permutation null = my within-model selectivity test), `agree()` (RDM correlation = cross-model consensus test), and the sign/magnitude register split. I'll mirror it, swapping in the **routing register** (FFN gate pre-activation sign) and the tool-calling probes, and adding **common-mode removal**. Let me start building.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Tool-calling normal form — is it a consensus routing structure, or common mode?\n\nTHE PRIOR CLAIM (lattice/tool_crystal_run.log, scripts/v12/probe_tool_crystal.py):\n  \"STRONG SUPPORT: Tool x Lambda overlap peaks at 1.000 at layer 20.\n   Tool calling IS lambda calculus applied to JSON schema.\"\n  — measured as RAW cosine similarity of the residual hidden state, single\n    model (Qwen). But that run's own Selectivity column reads ~-0.01..+0.03 and\n    every layer is marked \"SHARED\": the 0.9999 is the generic high-dim prose\n    COMMON MODE (Schema/Lambda/Tool x Lambda all 0.9999 at L20), not tool\n    structure. Classic wrong-register/common-mode artifact (cf. audit s202/s211).\n\nTHE CORRECT INSTRUMENT (this script):\n  Measure the ROUTING register, not the raw residual:\n    routing(x) = sign( FFN gate pre-activation )          (s203: gate_proj sign\n                                                            carries routing topology)\n  with COMMON-MODE REMOVAL (center features across probes before the RDM), and\n  against a SHUFFLED-LABEL null. Then the part the prior run never did:\n  CROSS-MODEL CONSENSUS — does the tool-calling routing RDM AGREE across\n  independent model families above a shuffled-probe null?  Agreement == the\n  empirical signature of a shared normal form (Church-Rosser confluence across\n  independent trainings; crystal-universality.md).\n\nPer-model invocation (like manifold_axis_topology.py). Saves per-layer RDMs\n(probe-aligned, so cross-model agreement needs no re-run) + within-model\nselectivity. tool_crystal_consensus_summary.py does the cross-model verdict.\n\nRegisters compared (the scientific contrast):\n  hidden_full   raw residual cosine        -> reproduces the prior \"SHARED\" common mode\n  hidden_cmr    residual cosine, centered  -> residual after common-mode removal\n  route_sign    sign(gate) cosine          -> the routing register (the claim's register)\n  route_cmr     sign(gate) cosine, centered-> routing after common-mode removal  <-- KEY\n\nUsage:\n  uv run python scripts/experiments/tool_crystal_consensus.py \\\n      --model Qwen/Qwen3-8B --device mps --dtype bfloat16\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport gc\nimport json\nimport re\nimport subprocess\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"tool-crystal-consensus\"\nPROBES_PATH = _PROJECT_ROOT / \"lattice\" / \"tool_crystal\" / \"probes.json\"\n\n# layer fractions to capture (depth-normalized so models of different depth align)\nLAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# ---- probes -----------------------------------------------------------------\ndef render(prompt: str) -> str:\n    \"\"\"Strip model-specific chat special tokens -> plain text, so every family\n    sees the SAME token surface (isolates internal routing from chat scaffolding).\"\"\"\n    return (prompt.replace(\"<|im_start|>\", \"\")\n                  .replace(\"<|im_end|>\", \"\")\n                  .strip())\n\n\ndef load_probes(limit: int = 0, seed: int = 0):\n    data = json.loads(PROBES_PATH.read_text())\n    if limit and limit < len(data):\n        rng = np.random.default_rng(seed)\n        data = [data[i] for i in sorted(rng.permutation(len(data))[:limit])]\n    prompts = [render(p[\"prompt\"]) for p in data]\n    domain = [p.get(\"domain\", \"?\") for p in data]\n    subdomain = [p.get(\"subdomain\", \"?\") for p in data]\n    return prompts, domain, subdomain\n\n\n# ---- model introspection ----------------------------------------------------\ndef find_gate_modules(model):\n    \"\"\"Return ordered [(layer_idx, module, kind)] for the FFN gate/intermediate.\n    SwiGLU (Qwen/Mistral/SmolLM/OLMo): mlp.gate_proj.  GPTNeoX (Pythia): mlp.dense_h_to_4h.\"\"\"\n    hits = []\n    pat = re.compile(r\"\\.(\\d+)\\.mlp\\.(gate_proj|dense_h_to_4h)$\")\n    for name, mod in model.named_modules():\n        m = pat.search(name)\n        if m:\n            hits.append((int(m.group(1)), name, mod, m.group(2)))\n    hits.sort(key=lambda x: x[0])\n    kind = \"gate_proj\" if any(h[3] == \"gate_proj\" for h in hits) else \"dense_h_to_4h\"\n    return [(li, name, mod) for (li, name, mod, k) in hits], kind\n\n\ndef pick_layers(n_layers: int):\n    idxs = sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1)))) for f in LAYER_FRACS})\n    return idxs\n\n\n# ---- capture ----------------------------------------------------------------\n@torch.no_grad()\ndef collect(model, tokenizer, device, prompts, max_length, want_layers):\n    \"\"\"Return:\n      hidden  [N x d]          final residual at last token (raw register)\n      gate    {layer_idx: [N x d_ff]} gate pre-activation at last token (routing register)\n    \"\"\"\n    gate_mods, kind = find_gate_modules(model)\n    n_layers = len(gate_mods)\n    want = set(want_layers)\n    buf = {}\n\n    def mk_hook(li):\n        def hook(_m, _inp, out):\n            # out: [B, T, d_ff]; take last token of batch item 0\n            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)\n        return hook\n\n    handles = [mod.register_forward_hook(mk_hook(li))\n               for (li, _nm, mod) in gate_mods if li in want]\n\n    n = len(prompts)\n    hidden = None\n    gate = {li: None for li in want}\n    try:\n        for i, text in enumerate(prompts):\n            buf.clear()\n            enc = tokenizer(text, return_tensors=\"pt\", truncation=True, max_length=max_length)\n            enc = {k: v.to(device) for k, v in enc.items()}\n            out = model(**enc, output_hidden_states=True)\n            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)\n            if hidden is None:\n                hidden = np.empty((n, h.shape[0]), np.float32)\n            hidden[i] = h\n            for li in want:\n                g = buf[li]\n                if gate[li] is None:\n                    gate[li] = np.empty((n, g.shape[0]), np.float32)\n                gate[li][i] = g\n            del out\n            if (i + 1) % 50 == 0:\n                log(f\"    {i + 1}/{n}\")\n    finally:\n        for hd in handles:\n            hd.remove()\n    return hidden, gate, kind, n_layers\n\n\n# ---- RDMs -------------------------------------------------------------------\ndef cosine_rdm(X):\n    X = X.astype(np.float64)\n    nrm = np.linalg.norm(X, axis=1, keepdims=True) + 1e-30\n    cos = np.clip((X / nrm) @ (X / nrm).T, -1, 1)\n    d = 1.0 - cos\n    np.fill_diagonal(d, 0.0)\n    return d\n\n\ndef cmr(X):\n    \"\"\"Common-mode removal: subtract the per-feature mean across probes\n    (kills the shared common mode that makes high-dim prose cosine ~1).\"\"\"\n    return X - X.mean(axis=0, keepdims=True)\n\n\ndef upper(D):\n    iu = np.triu_indices_from(D, k=1)\n    return D[iu]\n\n\ndef separation(D, labels, mask=None, n_perm=2000, seed=0):\n    \"\"\"Permutation test: between-label mean dist minus within-label mean dist.\n    mask: optional bool over probes to restrict to a sub-contrast.\"\"\"\n    lab = np.array(labels)\n    if mask is not None:\n        idx = np.where(mask)[0]\n        D = D[np.ix_(idx, idx)]\n        lab = lab[idx]\n    iu = np.triu_indices_from(D, k=1)\n    dv = D[iu]\n\n    def gap(L):\n        same = L[iu[0]] == L[iu[1]]\n        if same.all() or (~same).all():\n            return 0.0\n        return dv[~same].mean() - dv[same].mean()\n\n    obs = gap(lab)\n    rng = np.random.default_rng(seed)\n    null = np.array([gap(rng.permutation(lab)) for _ in range(n_perm)])\n    sd = null.std() + 1e-30\n    return {\"gap\": float(obs), \"null_mean\": float(null.mean()),\n            \"null_std\": float(null.std()),\n            \"z\": float((obs - null.mean()) / sd),\n            \"p_value\": float((np.sum(null >= obs) + 1) / (n_perm + 1)),\n            \"n\": int(len(lab))}\n\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--model\", required=True)\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--dtype\", default=\"bfloat16\",\n                    choices=[\"float32\", \"float16\", \"bfloat16\"])\n    ap.add_argument(\"--max-length\", type=int, default=512)\n    ap.add_argument(\"--limit\", type=int, default=0)\n    ap.add_argument(\"--n-perm\", type=int, default=2000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    args = ap.parse_args()\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    safe = args.model.replace(\"/\", \"_\")\n    t0 = time.time()\n\n    prompts, domain, subdomain = load_probes(args.limit, args.seed)\n    log(f\"[{args.model}] {len(prompts)} tool-crystal probes\")\n\n    # contrast masks\n    domain_arr = np.array(domain)\n    sub_arr = np.array(subdomain)\n    is_control = domain_arr == \"control\"\n    recog_mask = np.isin(sub_arr, [\"recognition/tool\", \"recognition/no_tool\"])\n    # tool vs control (broad): tool-domains = everything not control\n    tool_vs_ctrl_mask = np.ones(len(prompts), bool)  # all probes; label = is_control\n\n    dtype = {\"float32\": torch.float32, \"float16\": torch.float16,\n             \"bfloat16\": torch.bfloat16}[args.dtype]\n    tok = AutoTokenizer.from_pretrained(args.model)\n    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)\n    model.to(args.device).eval()\n\n    # probe layer count first\n    gate_mods, kind = find_gate_modules(model)\n    n_layers = len(gate_mods)\n    want_layers = pick_layers(n_layers)\n    log(f\"  arch: {n_layers} layers, FFN gate = {kind}; capturing layers {want_layers}\")\n\n    log(\"  forward passes ...\")\n    hidden, gate, kind, n_layers = collect(model, tok, args.device, prompts,\n                                           args.max_length, want_layers)\n    width = int(hidden.shape[1])\n    del model\n    gc.collect()\n    if args.device == \"mps\":\n        torch.mps.empty_cache()\n\n    # ---- build registers & RDMs ----\n    log(\"  building RDMs (hidden raw/cmr; route_sign raw/cmr) per layer ...\")\n    out = {\"model\": args.model, \"dtype\": args.dtype, \"n_probes\": len(prompts),\n           \"hidden_width\": width, \"n_layers\": n_layers, \"gate_kind\": kind,\n           \"want_layers\": want_layers, \"n_perm\": args.n_perm,\n           \"git_sha\": git_sha(), \"domains\": sorted(set(domain)),\n           \"per_layer\": {}}\n\n    rdm_store = {}  # for npz\n\n    # hidden registers are layer-independent (final residual); compute once\n    hid_full = cosine_rdm(hidden)\n    hid_cmr = cosine_rdm(cmr(hidden))\n    rdm_store[\"hidden_full\"] = hid_full.astype(np.float32)\n    rdm_store[\"hidden_cmr\"] = hid_cmr.astype(np.float32)\n\n    def both_selectivity(D):\n        return {\n            \"recog_tool_vs_notool\": separation(\n                D, sub_arr, mask=recog_mask, n_perm=args.n_perm, seed=args.seed),\n            \"tool_vs_control\": separation(\n                D, is_control.astype(int), n_perm=args.n_perm, seed=args.seed),\n            \"domain_separation\": separation(\n                D, domain_arr, n_perm=args.n_perm, seed=args.seed),\n        }\n\n    out[\"hidden\"] = {\"full\": both_selectivity(hid_full),\n                     \"cmr\": both_selectivity(hid_cmr)}\n\n    # routing register, per captured layer\n    for li in want_layers:\n        g = gate[li]\n        sign = np.sign(g)\n        r_full = cosine_rdm(sign)\n        r_cmr = cosine_rdm(cmr(sign))\n        rdm_store[f\"route_sign_full_L{li:02d}\"] = r_full.astype(np.float32)\n        rdm_store[f\"route_sign_cmr_L{li:02d}\"] = r_cmr.astype(np.float32)\n        out[\"per_layer\"][str(li)] = {\n            \"frac\": round(li / max(n_layers - 1, 1), 3),\n            \"d_ff\": int(g.shape[1]),\n            \"route_sign_full\": both_selectivity(r_full),\n            \"route_sign_cmr\": both_selectivity(r_cmr),\n        }\n        st = out[\"per_layer\"][str(li)][\"route_sign_cmr\"][\"recog_tool_vs_notool\"]\n        log(f\"    L{li:02d} (f={li/max(n_layers-1,1):.2f}) \"\n            f\"route_cmr recog tool/no_tool: gap={st['gap']:+.4f} z={st['z']:+.2f} p={st['p_value']:.4f}\")\n\n    # best routing layer by recog selectivity (cmr)\n    best_li = max(want_layers, key=lambda li:\n                  out[\"per_layer\"][str(li)][\"route_sign_cmr\"][\"recog_tool_vs_notool\"][\"z\"])\n    out[\"best_routing_layer\"] = int(best_li)\n    out[\"elapsed_s\"] = round(time.time() - t0, 1)\n\n    # save probe-aligned RDMs (cross-model agreement done in summary; no re-run)\n    np.savez_compressed(\n        RESULTS_DIR / f\"{safe}.npz\",\n        domain=domain_arr, subdomain=sub_arr,\n        **rdm_store)\n    (RESULTS_DIR / f\"{safe}.json\").write_text(json.dumps(out, indent=2))\n\n    hb = out[\"hidden\"][\"full\"][\"recog_tool_vs_notool\"]\n    hc = out[\"hidden\"][\"cmr\"][\"recog_tool_vs_notool\"]\n    rb = out[\"per_layer\"][str(best_li)][\"route_sign_full\"][\"recog_tool_vs_notool\"]\n    rc = out[\"per_layer\"][str(best_li)][\"route_sign_cmr\"][\"recog_tool_vs_notool\"]\n    log(\"\")\n    log(f\"  === {args.model}  (recog tool vs no_tool selectivity) ===\")\n    log(f\"  hidden_full  gap={hb['gap']:+.4f} z={hb['z']:+.2f} p={hb['p_value']:.4f}   (prior 'SHARED' register)\")\n    log(f\"  hidden_cmr   gap={hc['gap']:+.4f} z={hc['z']:+.2f} p={hc['p_value']:.4f}\")\n    log(f\"  route_full   gap={rb['gap']:+.4f} z={rb['z']:+.2f} p={rb['p_value']:.4f}   (L{best_li})\")\n    log(f\"  route_cmr    gap={rc['gap']:+.4f} z={rc['z']:+.2f} p={rc['p_value']:.4f}   (L{best_li})  <-- KEY\")\n    log(f\"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py
```

## Assistant

Now the cross-model summary script (the consensus test — the part the prior run never did):

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Cross-model consensus verdict for the tool-calling normal form.\n\nLoads every results/tool-crystal-consensus/*.npz (one per model, written by\ntool_crystal_consensus.py) and asks the question the single-model prior run\nnever asked: do INDEPENDENT model families AGREE on the tool-calling routing\nstructure above a shuffled-probe null?\n\nAgreement metric (probe-aligned, like manifold_axis_topology_summary):\n  for each register r and each model pair (a,b):\n     agree = corr( upper(RDM_a^r), upper(RDM_b^r) )\n  null: permute probe order of b (1000x) -> agreement under destroyed alignment.\n\nA consensus normal form requires:  mean cross-family agree(route_cmr) >> null.\nContrast it with hidden_full (the prior 'STRONG SUPPORT' common-mode register),\nwhich is expected to be high RAW (everything correlates) but should NOT exceed\nits own shuffled-probe null by much once you realize the agreement is the\ncommon mode (we report both; the null calibrates).\n\nUsage:\n  uv run python scripts/experiments/tool_crystal_consensus_summary.py \\\n      [--route-layer-frac 0.6] [--n-perm 1000]\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom itertools import combinations\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"tool-crystal-consensus\"\n\n\ndef log(m: str = \"\") -> None:\n    print(m, file=sys.stderr, flush=True)\n\n\ndef upper(D):\n    iu = np.triu_indices_from(D, k=1)\n    return D[iu]\n\n\ndef agree(Da, Db):\n    a, b = upper(Da), upper(Db)\n    if a.std() < 1e-12 or b.std() < 1e-12:\n        return float(\"nan\")\n    return float(np.corrcoef(a, b)[0, 1])\n\n\ndef agree_null(Da, Db, n_perm, seed):\n    \"\"\"Agreement with probe order of Db permuted (destroys alignment).\"\"\"\n    n = Db.shape[0]\n    rng = np.random.default_rng(seed)\n    a = upper(Da)\n    vals = []\n    for _ in range(n_perm):\n        perm = rng.permutation(n)\n        Dp = Db[np.ix_(perm, perm)]\n        b = upper(Dp)\n        if b.std() < 1e-12:\n            continue\n        vals.append(np.corrcoef(a, b)[0, 1])\n    return np.array(vals)\n\n\ndef family(model_name: str) -> str:\n    s = model_name.lower()\n    for fam in [\"qwen3\", \"qwen2\", \"mistral\", \"smollm\", \"olmo\", \"pythia\",\n                \"phi\", \"gpt-neox\", \"llama\", \"gemma\"]:\n        if fam in s:\n            return fam\n    return s.split(\"_\")[0]\n\n\ndef pick_route_key(keys, frac):\n    \"\"\"Choose the route_sign_cmr layer whose fraction is nearest `frac`.\"\"\"\n    cand = []\n    for k in keys:\n        if k.startswith(\"route_sign_cmr_L\"):\n            li = int(k.split(\"_L\")[1])\n            cand.append((li, k))\n    if not cand:\n        return None\n    return cand  # caller resolves frac vs n_layers using the json\n\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--route-layer-frac\", type=float, default=0.6)\n    ap.add_argument(\"--n-perm\", type=int, default=1000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    args = ap.parse_args()\n\n    npzs = sorted(RESULTS_DIR.glob(\"*.npz\"))\n    if len(npzs) < 2:\n        log(f\"need >=2 model npz in {RESULTS_DIR}, found {len(npzs)}\")\n        sys.exit(1)\n\n    models = {}\n    for p in npzs:\n        safe = p.stem\n        js = json.loads((RESULTS_DIR / f\"{safe}.json\").read_text())\n        data = np.load(p, allow_pickle=True)\n        n_layers = js[\"n_layers\"]\n        # resolve nearest captured layer to the requested fraction\n        want = js[\"want_layers\"]\n        target = round(args.route_layer_frac * (n_layers - 1))\n        li = min(want, key=lambda x: abs(x - target))\n        models[safe] = {\n            \"family\": family(safe),\n            \"n_layers\": n_layers,\n            \"route_li\": li,\n            \"rdm\": {\n                \"hidden_full\": data[\"hidden_full\"],\n                \"hidden_cmr\": data[\"hidden_cmr\"],\n                \"route_sign_full\": data[f\"route_sign_full_L{li:02d}\"],\n                \"route_sign_cmr\": data[f\"route_sign_cmr_L{li:02d}\"],\n            },\n        }\n        log(f\"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})\")\n\n    names = list(models)\n    out = {\"models\": {n: {\"family\": models[n][\"family\"],\n                          \"route_li\": models[n][\"route_li\"],\n                          \"n_layers\": models[n][\"n_layers\"]} for n in names},\n           \"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"registers\": {}}\n\n    for reg in [\"hidden_full\", \"hidden_cmr\", \"route_sign_full\", \"route_sign_cmr\"]:\n        pair_rows = []\n        cross_fam_obs, cross_fam_null = [], []\n        for a, b in combinations(names, 2):\n            Da, Db = models[a][\"rdm\"][reg], models[b][\"rdm\"][reg]\n            obs = agree(Da, Db)\n            null = agree_null(Da, Db, args.n_perm, args.seed)\n            nmean = float(np.nanmean(null)); nstd = float(np.nanstd(null)) + 1e-30\n            same_fam = models[a][\"family\"] == models[b][\"family\"]\n            row = {\"a\": a, \"b\": b, \"same_family\": same_fam, \"agree\": obs,\n                   \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                   \"z\": float((obs - nmean) / nstd)}\n            pair_rows.append(row)\n            if not same_fam:\n                cross_fam_obs.append(obs)\n                cross_fam_null.append(nmean)\n        cf = np.array(cross_fam_obs) if cross_fam_obs else np.array([np.nan])\n        cfn = np.array(cross_fam_null) if cross_fam_null else np.array([np.nan])\n        out[\"registers\"][reg] = {\n            \"pairs\": pair_rows,\n            \"cross_family_mean_agree\": float(np.nanmean(cf)),\n            \"cross_family_mean_null\": float(np.nanmean(cfn)),\n            \"cross_family_excess\": float(np.nanmean(cf) - np.nanmean(cfn)),\n        }\n\n    (RESULTS_DIR / \"consensus_summary.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  ============ CROSS-MODEL CONSENSUS (cross-family pairs) ============\")\n    log(f\"  {'register':18s} {'agree':>8s} {'null':>8s} {'excess':>8s}\")\n    for reg, r in out[\"registers\"].items():\n        tag = \"  <-- KEY\" if reg == \"route_sign_cmr\" else \"\"\n        note = \"  (prior 'SHARED' common mode)\" if reg == \"hidden_full\" else \"\"\n        log(f\"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} \"\n            f\"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}\")\n    log(\"\")\n    log(\"  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr\")\n    log(\"  cross-family excess >> 0 (agreement survives common-mode removal AND\")\n    log(\"  exceeds the shuffled-probe null). If route_cmr excess ~ 0 => the prior\")\n    log(\"  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing\")\n    log(\"  normal form at this granularity.\")\n    log(f\"  wrote consensus_summary.json\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py
```

### Thinking

 Let me run a quick syntax check and minimal smoke test on pythia-410m to verify the pipeline works, then do a cross-architecture test with Qwen3-0.6B since they use different gating mechanisms.

## Assistant

Let me check for diagnostics, then run a fast syntax+pipeline check on a tiny subset before the full smoke.

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py"
}
```

**Summary:** Checking diagnostics: tool_crystal_consensus.py

**Output:**
```
No diagnostics found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; python3 -c \"import ast; ast.parse(open('scripts/experiments/tool_crystal_consensus.py').read()); ast.parse(open('scripts/experiments/tool_crystal_consensus_summary.py').read()); print('syntax OK')\" ; echo \"=== ruff ===\" ; uv run ruff check scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py 2>&1 | tail -20"
}
```

**Summary:** $ python3 -c "import ast; ast.parse(o...

**Output:**
```
Exit code: 0
Stdout:
syntax OK
=== ruff ===
169 |         note = "  (prior 'SHARED' common mode)" if reg == "hidden_full" else ""
170 |         log(f"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} "
171 |             f"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}")
    |                                                                                         ^^^^^^^^
172 |     log("")
173 |     log("  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr")
    |

F541 [*] f-string without any placeholders
   --> scripts/experiments/tool_crystal_consensus_summary.py:178:9
    |
176 |     log("  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing")
177 |     log("  normal form at this granularity.")
178 |     log(f"  wrote consensus_summary.json")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
help: Remove extraneous `f` prefix

Found 15 errors.
[*] 2 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

 I'm checking the full ruff output to see what the 15 errors are—most are likely unused variables or f-string issues. I'll run ruff with --fix to handle the safe ones automatically, then clean up the remaining issues. I should also remove the unused `pick_route_key` function and `tool_vs_ctrl_mask` variable while I'm at it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; uv run ruff check --fix scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py 2>&1 | tail -30 ; echo \"=== remaining ===\" ; uv run ruff check scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py 2>&1 | grep -E \"^[A-Z][0-9]+|-->|Found\" "
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
128 |         log(f"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})")
    |                                                                                         ^^^^^^^^^
129 |
130 |     names = list(models)
    |

E702 Multiple statements on one line (semicolon)
   --> scripts/experiments/tool_crystal_consensus_summary.py:144:44
    |
142 |             obs = agree(Da, Db)
143 |             null = agree_null(Da, Db, args.n_perm, args.seed)
144 |             nmean = float(np.nanmean(null)); nstd = float(np.nanstd(null)) + 1e-30
    |                                            ^
145 |             same_fam = models[a]["family"] == models[b]["family"]
146 |             row = {"a": a, "b": b, "same_family": same_fam, "agree": obs,
    |

E501 Line too long (96 > 88)
   --> scripts/experiments/tool_crystal_consensus_summary.py:171:89
    |
169 |         note = "  (prior 'SHARED' common mode)" if reg == "hidden_full" else ""
170 |         log(f"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} "
171 |             f"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}")
    |                                                                                         ^^^^^^^^
172 |     log("")
173 |     log("  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr")
    |

Found 15 errors (2 fixed, 13 remaining).
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
=== remaining ===
E501 Line too long (89 > 88)
  --> scripts/experiments/tool_crystal_consensus.py:32:89
E501 Line too long (94 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:101:89
E501 Line too long (94 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:114:89
E501 Line too long (90 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:123:89
E501 Line too long (94 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:145:89
F841 Local variable `tool_vs_ctrl_mask` is assigned to but never used
   --> scripts/experiments/tool_crystal_consensus.py:240:5
E501 Line too long (105 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:308:89
E501 Line too long (114 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:329:89
E501 Line too long (101 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:331:89
E501 Line too long (110 > 88)
   --> scripts/experiments/tool_crystal_consensus.py:332:89
E501 Line too long (97 > 88)
   --> scripts/experiments/tool_crystal_consensus_summary.py:128:89
E702 Multiple statements on one line (semicolon)
   --> scripts/experiments/tool_crystal_consensus_summary.py:144:44
E501 Line too long (96 > 88)
   --> scripts/experiments/tool_crystal_consensus_summary.py:171:89
Found 13 errors.
```

### Thinking

 Looking at the linting errors, most are E501 line length issues which are cosmetic and probably ignored by the project's ruff config anyway since other harnesses have them too. The substantive problems are an unused variable and a semicolon that I should fix, but I can leave the line length violations as they are.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== ruff config ===\" ; grep -A15 \"\\[tool.ruff\" pyproject.toml 2>/dev/null | head -30 ; echo \"=== do existing harnesses pass E501? ===\" ; uv run ruff check scripts/experiments/manifold_axis_topology.py 2>&1 | grep -cE \"E501\" "
}
```

**Summary:** $ echo "=== ruff config ===" ; grep -...

**Output:**
```
Exit code: 0
Stdout:
=== ruff config ===
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "UP",   # pyupgrade
    "RUF",  # ruff-specific
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["B011"]  # allow assert False / etc. in tests

# ─────────────────────────── ty ─────────────────────────────
# ty is alpha; config schema is moving. Empty stanza pins the table so
# project-level config has a home when we need it.
[tool.ty]

# ─────────────────────────── pytest ─────────────────────────
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-ra", "--strict-markers"]
=== do existing harnesses pass E501? ===
3
```

### Thinking

 I see the manifold harness also has some E501 violations that the project accepts, so those long lines in experiment scripts aren't blocking issues. I should focus on fixing the substantive problems—the unused variable and the semicolon—and clean up the worst line length violations where it makes sense.

## Assistant

E501 is tolerated in experiment scripts (the template itself has 3). I'll fix the substantive lint (unused var, semicolon) and move on.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py",
  "original_content": "    recog_mask = np.isin(sub_arr, [\"recognition/tool\", \"recognition/no_tool\"])\n    # tool vs control (broad): tool-domains = everything not control\n    tool_vs_ctrl_mask = np.ones(len(prompts), bool)  # all probes; label = is_control",
  "new_content": "    recog_mask = np.isin(sub_arr, [\"recognition/tool\", \"recognition/no_tool\"])\n    # tool vs control (broad) uses is_control as the label over all probes"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "original_content": "            nmean = float(np.nanmean(null)); nstd = float(np.nanstd(null)) + 1e-30",
  "new_content": "            nmean = float(np.nanmean(null))\n            nstd = float(np.nanstd(null)) + 1e-30"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py.
```

### Thinking

 I'm debating whether to clean up that unused `pick_route_key` function, but I think it's better to just run a quick smoke test on the pipeline instead — I'll do a fast limited run with Qwen3-0.6B to catch any runtime issues early.

## Assistant

Now a fast pipeline smoke on a tiny subset (Qwen3-0.6B, 24 probes) to catch runtime bugs cheaply before the real 2-model smoke:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; uv run python scripts/experiments/tool_crystal_consensus.py --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16 --limit 24 --n-perm 200 --max-length 384 2>&1 | tail -25",
  "timeout": 180000
}
```

**Summary:** $ uv run python scripts/experiments/t...

**Output:**
```
Exit code: 0
Stdout:
[Qwen/Qwen3-0.6B] 24 tool-crystal probes
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 20663.23it/s]
  arch: 28 layers, FFN gate = gate_proj; capturing layers [0, 3, 5, 8, 11, 14, 16, 19, 22, 24, 27]
  forward passes ...
  building RDMs (hidden raw/cmr; route_sign raw/cmr) per layer ...
    L00 (f=0.00) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L03 (f=0.11) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L05 (f=0.19) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L08 (f=0.30) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L11 (f=0.41) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L14 (f=0.52) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L16 (f=0.59) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L19 (f=0.70) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L22 (f=0.81) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L24 (f=0.89) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000
    L27 (f=1.00) route_cmr recog tool/no_tool: gap=+0.0000 z=+0.00 p=1.0000

  === Qwen/Qwen3-0.6B  (recog tool vs no_tool selectivity) ===
  hidden_full  gap=+0.0000 z=+0.00 p=1.0000   (prior 'SHARED' register)
  hidden_cmr   gap=+0.0000 z=+0.00 p=1.0000
  route_full   gap=+0.0000 z=+0.00 p=1.0000   (L0)
  route_cmr    gap=+0.0000 z=+0.00 p=1.0000   (L0)  <-- KEY
  wrote Qwen_Qwen3-0.6B.json + .npz  (6.0s)
```

### Thinking

 All the gap values are coming out as zero, which points to a bug in how the subsets are being sampled. When I limit to 24 probes randomly selected from 196, the recognition subset might end up empty or contain only a single class, which would make the gap calculation collapse to zero. That explains why the recognition test is returning zero, but it's strange that hidden_full and tool_vs_control are also zeroing out—those should have more robust class distributions even with the smaller sample size.

Looking at the printed summary, I'm realizing all four lines are actually showing the recognition contrast, not different contrasts. The recog subset under a 24-sample limit would have maybe 2-3 recognition probes split between tool and no_tool categories, which could easily become degenerate. I need to check the JSON output to see what the non-degenerate contrasts (tool_vs_control, domain_separation) are actually producing, and trace through how the random sampling and masking interact to understand why the separation calculation is returning zero across the board.

## Assistant

Smoke ran (6s) but the printed contrast is `recog_tool_vs_notool`, which is degenerate under `--limit 24` (too few recognition probes sampled). I need to verify the **non-degenerate** contrasts (tool_vs_control, domain_separation) are nonzero — let me inspect the JSON:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; python3 -c \"\nimport json\nd=json.load(open('results/tool-crystal-consensus/Qwen_Qwen3-0.6B.json'))\nprint('n_probes',d['n_probes'],'domains',d['domains'])\nprint('-- hidden_full --')\nfor k,v in d['hidden']['full'].items(): print(f'  {k:24s} gap={v[\\\"gap\\\"]:+.4f} z={v[\\\"z\\\"]:+.2f} p={v[\\\"p_value\\\"]:.3f} n={v[\\\"n\\\"]}')\nprint('-- route_sign_cmr @ L14 --')\nL=d['per_layer'].get('14') or list(d['per_layer'].values())[5]\nfor k,v in L['route_sign_cmr'].items(): print(f'  {k:24s} gap={v[\\\"gap\\\"]:+.4f} z={v[\\\"z\\\"]:+.2f} p={v[\\\"p_value\\\"]:.3f} n={v[\\\"n\\\"]}')\n\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
n_probes 24 domains ['control', 'format', 'recognition', 'schema_binding', 'selection']
-- hidden_full --
  recog_tool_vs_notool     gap=+0.0000 z=+0.00 p=1.000 n=2
  tool_vs_control          gap=-0.0933 z=-1.03 p=0.826 n=24
  domain_separation        gap=+0.3285 z=+5.59 p=0.005 n=24
-- route_sign_cmr @ L14 --
  recog_tool_vs_notool     gap=+0.0000 z=+0.00 p=1.000 n=2
  tool_vs_control          gap=+0.0817 z=+1.74 p=0.114 n=24
  domain_separation        gap=+0.6384 z=+11.86 p=0.005 n=24
```

### Thinking

 The pipeline is working as expected—with only 2 recognition probes in the 24-sample set, we get the degenerate case we anticipated. Looking at the non-degenerate contrasts, domain_separation shows strong significance in both hidden_full and route_sign_cmr, with the routing register effect being notably stronger, which confirms the instrument is discriminating properly. The tool_vs_control contrast shows no separation in the raw residual for hidden_full, and the thought cuts off there.

The routing-cmr register does show some separation, which is promising even at this limited scale. The pipeline itself is verified—gate capture works across 28 layers, CMR computes correctly, and the separation and null calculations are producing valid RDMs. The recognition test will become non-degenerate once we use the full 40-probe set.

Now I'm deciding whether to run the 2-model smoke test (Qwen3-0.6B and Pythia-410m with all 196 probes) in the tmux window as requested or just run it in the foreground since it's fast. Given that the full 5-family run is the longer task that really needs tmux, I'll run this 2-model smoke in the foreground to verify the recognition is non-degenerate and check the cross-model agreement.

Let me mark task 1 complete—the harness runs end-to-end on a single model and produces the per-model RDM output plus JSON with selectivity z-scores. Then I'll start task 2 with the full 2-model smoke.

## Assistant

Pipeline verified end-to-end: gate capture works (28 layers, gate_proj), CMR computes, separation + permutation nulls produce finite z/p, RDMs saved. The `recog` test was just degenerate at n=2 (needs the full probe set). Already a teaser signal: **domain_separation is much stronger in `route_sign_cmr` (z=+11.9) than raw `hidden_full` (z=+5.6)**, and raw residual fails tool-vs-control (z=−1.0) while routing-cmr doesn't — consistent with the prior "SHARED" common-mode read.

Task 1 done. Now the real 2-model smoke (full 196 probes, cross-architecture: Qwen3 gated vs Pythia non-gated).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; for M in Qwen/Qwen3-0.6B EleutherAI/pythia-410m ; do echo \"##### $M #####\" ; uv run python scripts/experiments/tool_crystal_consensus.py --model $M --device mps --dtype float32 --n-perm 1000 --max-length 512 2>&1 | tail -9 ; done",
  "timeout": 600000
}
```

**Summary:** $ for M in Qwen/Qwen3-0.6B EleutherAI...

**Output:**
```
Exit code: 0
Stdout:
##### Qwen/Qwen3-0.6B #####
    L24 (f=0.89) route_cmr recog tool/no_tool: gap=+0.6082 z=+28.62 p=0.0010
    L27 (f=1.00) route_cmr recog tool/no_tool: gap=+0.5805 z=+28.38 p=0.0010

  === Qwen/Qwen3-0.6B  (recog tool vs no_tool selectivity) ===
  hidden_full  gap=+0.0846 z=+28.65 p=0.0010   (prior 'SHARED' register)
  hidden_cmr   gap=+0.7478 z=+28.87 p=0.0010
  route_full   gap=+0.1323 z=+29.00 p=0.0010   (L14)
  route_cmr    gap=+0.6449 z=+28.92 p=0.0010   (L14)  <-- KEY
  wrote Qwen_Qwen3-0.6B.json + .npz  (39.3s)
##### EleutherAI/pythia-410m #####
    L21 (f=0.91) route_cmr recog tool/no_tool: gap=+0.3916 z=+24.35 p=0.0010
    L23 (f=1.00) route_cmr recog tool/no_tool: gap=+0.4279 z=+24.88 p=0.0010

  === EleutherAI/pythia-410m  (recog tool vs no_tool selectivity) ===
  hidden_full  gap=+0.0691 z=+25.06 p=0.0010   (prior 'SHARED' register)
  hidden_cmr   gap=+0.5928 z=+25.15 p=0.0010
  route_full   gap=+0.0864 z=+26.69 p=0.0010   (L12)
  route_cmr    gap=+0.4185 z=+26.68 p=0.0010   (L12)  <-- KEY
  wrote EleutherAI_pythia-410m.json + .npz  (26.2s)
```

### Thinking

 Both models are now complete, and the tool versus no_tool distinction shows strong statistical significance across all registers, including the hidden_full layer, with z-scores around 25-29 and p-values at 0.001. The within-model selectivity is consistently high everywhere, which makes sense since the tool prompt includes the full schema while the no_tool version doesn't, creating substantially different representations that are easy to distinguish.

The real test is whether independent models converge on the same underlying structure in their representational geometry, and whether that consensus persists through the routing register after CMR. The gap magnitudes reveal something important: hidden_cmr shows a much larger separation (0.75) compared to hidden_full (0.085), suggesting CMR amplifies the contrast by removing common-mode activity and leaving the residual differences more pronounced. The route_cmr gap is 0.64. Now I need to run the cross-model summary to see if the two models actually agree on the structure.

## Assistant

Both complete, recog selectivity now strongly significant (z≈25–29) across registers — though note within-model tool-vs-no_tool is *trivially* separable (the tool prompt literally contains the whole JSON schema; very different text). The discriminating question is **cross-model consensus**. Let me run the summary:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; uv run python scripts/experiments/tool_crystal_consensus_summary.py --route-layer-frac 0.6 --n-perm 1000 2>&1 | tail -20",
  "timeout": 120000
}
```

**Summary:** $ uv run python scripts/experiments/t...

**Output:**
```
Exit code: 0
Stdout:
loaded EleutherAI_pythia-410m           fam=pythia   route L14 (f~0.6)
  loaded Qwen_Qwen3-0.6B                  fam=qwen3    route L16 (f~0.6)

  ============ CROSS-MODEL CONSENSUS (cross-family pairs) ============
  register              agree     null   excess
  hidden_full           0.945    0.002   +0.943  (prior 'SHARED' common mode)
  hidden_cmr            0.863    0.000   +0.863
  route_sign_full       0.980    0.001   +0.978
  route_sign_cmr        0.879    0.000   +0.879  <-- KEY

  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr
  cross-family excess >> 0 (agreement survives common-mode removal AND
  exceeds the shuffled-probe null). If route_cmr excess ~ 0 => the prior
  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing
  normal form at this granularity.
  wrote consensus_summary.json
```

### Thinking

 The cross-family agreement between these completely independent models is remarkable—hidden representations show 0.945 correlation versus near-zero for the null baseline, and the routing signals align even more strongly at 0.879 for the CMR variant, suggesting these emergent behaviors aren't artifacts of shared architecture but fundamental properties of how these models organize computation.

But I need to apply skeptical scrutiny to my own finding: this agreement could be driven by something trivial that survives CMR, like the gross structural difference between long JSON-schema tool probes and short prose controls. Both models would naturally cluster long-structured prompts together and separate them from short text, which has nothing to do with a tool-calling normal form—it's just a generic length/format axis, the same kind of universal textual boundary feature I've seen before. So I need to test whether the RDM agreement holds when I control for these confounds by comparing probes of matched length and structure.

The real test of a genuine routing normal form is whether models agree on the fine structure *within* tool-calling domains—like the schema_binding RDM (how arguments bind) or the selection RDM (which tool is chosen)—not on the gross tool-versus-prose distinction. I should measure cross-model agreement specifically within these matched-format subsets to isolate the actual routing structure from the trivial length/format axis.

I need to upgrade the harness to capture prompt length per probe and then partial it out of the RDM, or at least compute within-domain agreement separately. This is the right control before scaling to the five-family run, and it's exactly what the project's methodology demands: find the agreement, then attack it with the right null and control. Let me complete task 2 as is, report the spotted confound to the user, and fold this length-partialling upgrade into task 3.

## Assistant

Task 2 complete — both architectures ran clean, nulls ~0, summary produces agreement. But the result demands I apply the project's own audit discipline to it **before** scaling, because I can already see the load-bearing confound.

**The smoke result (Pythia-410m vs Qwen3-0.6B, fully independent families):**

| register | cross-family agree | null | excess |
|---|---|---|---|
| hidden_full (prior "SHARED") | 0.945 | 0.002 | +0.943 |
| hidden_cmr | 0.863 | 0.000 | +0.863 |
| route_sign_full | 0.980 | 0.001 | +0.978 |
| **route_sign_cmr** | **0.879** | 0.000 | **+0.879** |

Cross-family agreement on the tool-calling routing structure is large and **survives common-mode removal** — which is more than the prior single-model run ever showed. **But** here's the trap the audit program would catch immediately (cf. s212, where the "universal axis" turned out to be the model-free `ends_punct` boundary feature): the probe set mixes **very long** tool prompts (full JSON schema) with **short** prose controls. The RDM is plausibly dominated by a generic *prompt-length/format* axis — "long structured text vs short prose" — which *any* two models will agree on, CMR or not. That's not a tool-calling normal form; it's a textual-structure axis.

So before the 5-family scale run, I must add the control: **within-domain, length-partialled agreement** — do models agree on the *fine* structure *within* tool-calling (schema_binding arg-binding, selection tool-choice — matched length/format), not just tool-vs-prose? That's the real normal-form test.

### Thinking

 I need to set task 3 as blocked by task 4, so I'll update task 3's blocked_by field to establish that dependency.

## Assistant

Now let me implement the confound controls. First, the per-model script: capture and save `prompt_len`.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py",
  "original_content": "    n = len(prompts)\n    hidden = None\n    gate = {li: None for li in want}\n    try:\n        for i, text in enumerate(prompts):\n            buf.clear()\n            enc = tokenizer(text, return_tensors=\"pt\", truncation=True, max_length=max_length)\n            enc = {k: v.to(device) for k, v in enc.items()}\n            out = model(**enc, output_hidden_states=True)\n            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)\n            if hidden is None:\n                hidden = np.empty((n, h.shape[0]), np.float32)\n            hidden[i] = h\n            for li in want:\n                g = buf[li]\n                if gate[li] is None:\n                    gate[li] = np.empty((n, g.shape[0]), np.float32)\n                gate[li][i] = g\n            del out\n            if (i + 1) % 50 == 0:\n                log(f\"    {i + 1}/{n}\")\n    finally:\n        for hd in handles:\n            hd.remove()\n    return hidden, gate, kind, n_layers",
  "new_content": "    n = len(prompts)\n    hidden = None\n    gate = {li: None for li in want}\n    plen = np.empty(n, np.int32)\n    try:\n        for i, text in enumerate(prompts):\n            buf.clear()\n            enc = tokenizer(text, return_tensors=\"pt\", truncation=True, max_length=max_length)\n            enc = {k: v.to(device) for k, v in enc.items()}\n            out = model(**enc, output_hidden_states=True)\n            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)\n            if hidden is None:\n                hidden = np.empty((n, h.shape[0]), np.float32)\n            hidden[i] = h\n            plen[i] = int(enc[\"input_ids\"].shape[1])\n            for li in want:\n                g = buf[li]\n                if gate[li] is None:\n                    gate[li] = np.empty((n, g.shape[0]), np.float32)\n                gate[li][i] = g\n            del out\n            if (i + 1) % 50 == 0:\n                log(f\"    {i + 1}/{n}\")\n    finally:\n        for hd in handles:\n            hd.remove()\n    return hidden, gate, plen, kind, n_layers"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py",
  "original_content": "    log(\"  forward passes ...\")\n    hidden, gate, kind, n_layers = collect(model, tok, args.device, prompts,\n                                           args.max_length, want_layers)",
  "new_content": "    log(\"  forward passes ...\")\n    hidden, gate, plen, kind, n_layers = collect(model, tok, args.device, prompts,\n                                                 args.max_length, want_layers)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py",
  "original_content": "    np.savez_compressed(\n        RESULTS_DIR / f\"{safe}.npz\",\n        domain=domain_arr, subdomain=sub_arr,\n        **rdm_store)",
  "new_content": "    np.savez_compressed(\n        RESULTS_DIR / f\"{safe}.npz\",\n        domain=domain_arr, subdomain=sub_arr, prompt_len=plen,\n        **rdm_store)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py.
```

### Thinking

 I'm refining the summary script to add length-controlled agreement metrics and within-domain agreement analysis. I need to load the prompt length and domain information from the data, construct a length-based representational dissimilarity matrix to use as a covariate for partial correlation, and then compute agreement scores that account for these confounds.

Rewriting the summary's main loop...

## Assistant

Now upgrade the summary with length-partialling and within-domain agreement — the actual normal-form controls:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "original_content": "def agree(Da, Db):\n    a, b = upper(Da), upper(Db)\n    if a.std() < 1e-12 or b.std() < 1e-12:\n        return float(\"nan\")\n    return float(np.corrcoef(a, b)[0, 1])",
  "new_content": "def agree(Da, Db):\n    a, b = upper(Da), upper(Db)\n    if a.std() < 1e-12 or b.std() < 1e-12:\n        return float(\"nan\")\n    return float(np.corrcoef(a, b)[0, 1])\n\n\ndef partial_agree(Da, Db, Z):\n    \"\"\"Cross-model agreement controlling for covariate RDM Z (e.g. length).\"\"\"\n    x, y, z = upper(Da), upper(Db), upper(Z)\n    if x.std() < 1e-12 or y.std() < 1e-12 or z.std() < 1e-12:\n        return float(\"nan\")\n    rxy = np.corrcoef(x, y)[0, 1]\n    rxz = np.corrcoef(x, z)[0, 1]\n    ryz = np.corrcoef(y, z)[0, 1]\n    denom = np.sqrt(max((1 - rxz**2) * (1 - ryz**2), 1e-30))\n    return float((rxy - rxz * ryz) / denom)\n\n\ndef length_rdm(plen):\n    L = np.abs(plen[:, None] - plen[None, :]).astype(np.float64)\n    np.fill_diagonal(L, 0.0)\n    return L\n\n\ndef sub_rdm(D, idx):\n    return D[np.ix_(idx, idx)]"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py.
```

### Thinking

 I need to modify the loading block to include domain and prompt_len, then update the register loop to calculate partial and within-domain metrics.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "original_content": "        models[safe] = {\n            \"family\": family(safe),\n            \"n_layers\": n_layers,\n            \"route_li\": li,\n            \"rdm\": {\n                \"hidden_full\": data[\"hidden_full\"],\n                \"hidden_cmr\": data[\"hidden_cmr\"],\n                \"route_sign_full\": data[f\"route_sign_full_L{li:02d}\"],\n                \"route_sign_cmr\": data[f\"route_sign_cmr_L{li:02d}\"],\n            },\n        }\n        log(f\"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})\")",
  "new_content": "        models[safe] = {\n            \"family\": family(safe),\n            \"n_layers\": n_layers,\n            \"route_li\": li,\n            \"domain\": data[\"domain\"],\n            \"prompt_len\": data[\"prompt_len\"].astype(np.float64),\n            \"rdm\": {\n                \"hidden_full\": data[\"hidden_full\"],\n                \"hidden_cmr\": data[\"hidden_cmr\"],\n                \"route_sign_full\": data[f\"route_sign_full_L{li:02d}\"],\n                \"route_sign_cmr\": data[f\"route_sign_cmr_L{li:02d}\"],\n            },\n        }\n        log(f\"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py.
```

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "original_content": "    names = list(models)\n    out = {\"models\": {n: {\"family\": models[n][\"family\"],\n                          \"route_li\": models[n][\"route_li\"],\n                          \"n_layers\": models[n][\"n_layers\"]} for n in names},\n           \"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"registers\": {}}\n\n    for reg in [\"hidden_full\", \"hidden_cmr\", \"route_sign_full\", \"route_sign_cmr\"]:\n        pair_rows = []\n        cross_fam_obs, cross_fam_null = [], []\n        for a, b in combinations(names, 2):\n            Da, Db = models[a][\"rdm\"][reg], models[b][\"rdm\"][reg]\n            obs = agree(Da, Db)\n            null = agree_null(Da, Db, args.n_perm, args.seed)\n            nmean = float(np.nanmean(null))\n            nstd = float(np.nanstd(null)) + 1e-30\n            same_fam = models[a][\"family\"] == models[b][\"family\"]\n            row = {\"a\": a, \"b\": b, \"same_family\": same_fam, \"agree\": obs,\n                   \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                   \"z\": float((obs - nmean) / nstd)}\n            pair_rows.append(row)\n            if not same_fam:\n                cross_fam_obs.append(obs)\n                cross_fam_null.append(nmean)\n        cf = np.array(cross_fam_obs) if cross_fam_obs else np.array([np.nan])\n        cfn = np.array(cross_fam_null) if cross_fam_null else np.array([np.nan])\n        out[\"registers\"][reg] = {\n            \"pairs\": pair_rows,\n            \"cross_family_mean_agree\": float(np.nanmean(cf)),\n            \"cross_family_mean_null\": float(np.nanmean(cfn)),\n            \"cross_family_excess\": float(np.nanmean(cf) - np.nanmean(cfn)),\n        }\n\n    (RESULTS_DIR / \"consensus_summary.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  ============ CROSS-MODEL CONSENSUS (cross-family pairs) ============\")\n    log(f\"  {'register':18s} {'agree':>8s} {'null':>8s} {'excess':>8s}\")\n    for reg, r in out[\"registers\"].items():\n        tag = \"  <-- KEY\" if reg == \"route_sign_cmr\" else \"\"\n        note = \"  (prior 'SHARED' common mode)\" if reg == \"hidden_full\" else \"\"\n        log(f\"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} \"\n            f\"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}\")\n    log(\"\")\n    log(\"  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr\")\n    log(\"  cross-family excess >> 0 (agreement survives common-mode removal AND\")\n    log(\"  exceeds the shuffled-probe null). If route_cmr excess ~ 0 => the prior\")\n    log(\"  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing\")\n    log(\"  normal form at this granularity.\")\n    log(f\"  wrote consensus_summary.json\")",
  "new_content": "    names = list(models)\n    # alignment sanity: all models must share the probe order (no --limit)\n    n0 = models[names[0]][\"rdm\"][\"hidden_full\"].shape[0]\n    for n in names:\n        assert models[n][\"rdm\"][\"hidden_full\"].shape[0] == n0, f\"{n} probe count mismatch\"\n    dom0 = models[names[0]][\"domain\"]\n    # average length covariate (tokenizers differ slightly; length is ~shared)\n    avg_len = np.mean([models[n][\"prompt_len\"] for n in names], axis=0)\n    Lrdm = length_rdm(avg_len)\n    # within-domain index sets (matched length/format)\n    dom_idx = {d: np.where(dom0 == d)[0] for d in sorted(set(dom0.tolist()))}\n    within_domains = [d for d in [\"schema_binding\", \"selection\", \"format\"]\n                      if d in dom_idx and len(dom_idx[d]) >= 8]\n\n    out = {\"models\": {n: {\"family\": models[n][\"family\"],\n                          \"route_li\": models[n][\"route_li\"],\n                          \"n_layers\": models[n][\"n_layers\"]} for n in names},\n           \"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"within_domains\": within_domains,\n           \"domain_counts\": {d: int(len(i)) for d, i in dom_idx.items()},\n           \"registers\": {}}\n\n    for reg in [\"hidden_full\", \"hidden_cmr\", \"route_sign_full\", \"route_sign_cmr\"]:\n        pair_rows = []\n        cf_obs, cf_null, cf_partial = [], [], []\n        cf_within = {d: [] for d in within_domains}\n        for a, b in combinations(names, 2):\n            Da, Db = models[a][\"rdm\"][reg], models[b][\"rdm\"][reg]\n            obs = agree(Da, Db)\n            null = agree_null(Da, Db, args.n_perm, args.seed)\n            nmean = float(np.nanmean(null))\n            nstd = float(np.nanstd(null)) + 1e-30\n            partial = partial_agree(Da, Db, Lrdm)\n            same_fam = models[a][\"family\"] == models[b][\"family\"]\n            within = {d: agree(sub_rdm(Da, dom_idx[d]), sub_rdm(Db, dom_idx[d]))\n                      for d in within_domains}\n            row = {\"a\": a, \"b\": b, \"same_family\": same_fam, \"agree\": obs,\n                   \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                   \"z\": float((obs - nmean) / nstd),\n                   \"partial_len\": partial, \"within_domain\": within}\n            pair_rows.append(row)\n            if not same_fam:\n                cf_obs.append(obs)\n                cf_null.append(nmean)\n                cf_partial.append(partial)\n                for d in within_domains:\n                    cf_within[d].append(within[d])\n\n        def m(x):\n            return float(np.nanmean(x)) if len(x) else float(\"nan\")\n        out[\"registers\"][reg] = {\n            \"pairs\": pair_rows,\n            \"cross_family_mean_agree\": m(cf_obs),\n            \"cross_family_mean_null\": m(cf_null),\n            \"cross_family_excess\": m(cf_obs) - m(cf_null),\n            \"cross_family_partial_len\": m(cf_partial),\n            \"cross_family_within_domain\": {d: m(cf_within[d]) for d in within_domains},\n        }\n\n    (RESULTS_DIR / \"consensus_summary.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  ===== CROSS-MODEL CONSENSUS (cross-family pairs) =====\")\n    wd_hdr = \" \".join(f\"{d[:6]:>7s}\" for d in within_domains)\n    log(f\"  {'register':18s} {'agree':>7s} {'null':>7s} {'excess':>7s} {'∂len':>7s}  | within-dom: {wd_hdr}\")\n    for reg, r in out[\"registers\"].items():\n        tag = \"  <-- KEY\" if reg == \"route_sign_cmr\" else \"\"\n        wd = \" \".join(f\"{r['cross_family_within_domain'][d]:>7.3f}\" for d in within_domains)\n        log(f\"  {reg:18s} {r['cross_family_mean_agree']:>7.3f} \"\n            f\"{r['cross_family_mean_null']:>7.3f} {r['cross_family_excess']:>+7.3f} \"\n            f\"{r['cross_family_partial_len']:>7.3f}  | {wd}{tag}\")\n    log(\"\")\n    log(\"  Read: ∂len = agreement after partialling out prompt LENGTH.\")\n    log(\"  within-dom = agreement restricted to one domain (matched length/format).\")\n    log(\"  NORMAL FORM => route_sign_cmr keeps high ∂len AND high within-domain agree.\")\n    log(\"  If those collapse toward 0 => the consensus was a length/format axis, not\")\n    log(\"  a tool-calling routing normal form (prior 'STRONG SUPPORT' = common mode).\")\n    log(\"  wrote consensus_summary.json\")"
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py
```

### Thinking

 The first edit succeeded with the loading block, but the second one for the main loop failed because the original content wasn't found. Let me pull up the current file to see what the actual text looks like now.

## Assistant

The main-loop edit didn't match (likely whitespace drift from a prior edit). Let me read the current state and re-edit precisely.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "line_offset": 147,
  "limit": 60
}
```

**Summary:** Reading tool_crystal_consensus_summary.py (147-207)

**Output:**
```
                "route_sign_full": data[f"route_sign_full_L{li:02d}"],
                "route_sign_cmr": data[f"route_sign_cmr_L{li:02d}"],
            },
        }
        log(f"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})")

    names = list(models)
    out = {"models": {n: {"family": models[n]["family"],
                          "route_li": models[n]["route_li"],
                          "n_layers": models[n]["n_layers"]} for n in names},
           "route_layer_frac": args.route_layer_frac, "n_perm": args.n_perm,
           "registers": {}}

    for reg in ["hidden_full", "hidden_cmr", "route_sign_full", "route_sign_cmr"]:
        pair_rows = []
        cross_fam_obs, cross_fam_null = [], []
        for a, b in combinations(names, 2):
            Da, Db = models[a]["rdm"][reg], models[b]["rdm"][reg]
            obs = agree(Da, Db)
            null = agree_null(Da, Db, args.n_perm, args.seed)
            nmean = float(np.nanmean(null))
            nstd = float(np.nanstd(null)) + 1e-30
            same_fam = models[a]["family"] == models[b]["family"]
            row = {"a": a, "b": b, "same_family": same_fam, "agree": obs,
                   "null_mean": nmean, "null_std": float(np.nanstd(null)),
                   "z": float((obs - nmean) / nstd)}
            pair_rows.append(row)
            if not same_fam:
                cross_fam_obs.append(obs)
                cross_fam_null.append(nmean)
        cf = np.array(cross_fam_obs) if cross_fam_obs else np.array([np.nan])
        cfn = np.array(cross_fam_null) if cross_fam_null else np.array([np.nan])
        out["registers"][reg] = {
            "pairs": pair_rows,
            "cross_family_mean_agree": float(np.nanmean(cf)),
            "cross_family_mean_null": float(np.nanmean(cfn)),
            "cross_family_excess": float(np.nanmean(cf) - np.nanmean(cfn)),
        }

    (RESULTS_DIR / "consensus_summary.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  ============ CROSS-MODEL CONSENSUS (cross-family pairs) ============")
    log(f"  {'register':18s} {'agree':>8s} {'null':>8s} {'excess':>8s}")
    for reg, r in out["registers"].items():
        tag = "  <-- KEY" if reg == "route_sign_cmr" else ""
        note = "  (prior 'SHARED' common mode)" if reg == "hidden_full" else ""
        log(f"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} "
            f"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}")
    log("")
    log("  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr")
    log("  cross-family excess >> 0 (agreement survives common-mode removal AND")
    log("  exceeds the shuffled-probe null). If route_cmr excess ~ 0 => the prior")
    log("  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing")
    log("  normal form at this granularity.")
    log("  wrote consensus_summary.json")


if __name__ == "__main__":
    main()
```

### Thinking

 I see the issue now—ruff auto-fixed the f-string to a regular string earlier, so my original content with the f-prefix no longer matches the current code. I need to replace the entire main loop section starting from `names = list(models)` through the logging block, making sure to match the exact text that's actually there now.

## Assistant

The earlier ruff `--fix` stripped the `f` prefix, breaking my match. Let me replace the whole block with the current exact text:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py",
  "original_content": "    names = list(models)\n    out = {\"models\": {n: {\"family\": models[n][\"family\"],\n                          \"route_li\": models[n][\"route_li\"],\n                          \"n_layers\": models[n][\"n_layers\"]} for n in names},\n           \"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"registers\": {}}\n\n    for reg in [\"hidden_full\", \"hidden_cmr\", \"route_sign_full\", \"route_sign_cmr\"]:\n        pair_rows = []\n        cross_fam_obs, cross_fam_null = [], []\n        for a, b in combinations(names, 2):\n            Da, Db = models[a][\"rdm\"][reg], models[b][\"rdm\"][reg]\n            obs = agree(Da, Db)\n            null = agree_null(Da, Db, args.n_perm, args.seed)\n            nmean = float(np.nanmean(null))\n            nstd = float(np.nanstd(null)) + 1e-30\n            same_fam = models[a][\"family\"] == models[b][\"family\"]\n            row = {\"a\": a, \"b\": b, \"same_family\": same_fam, \"agree\": obs,\n                   \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                   \"z\": float((obs - nmean) / nstd)}\n            pair_rows.append(row)\n            if not same_fam:\n                cross_fam_obs.append(obs)\n                cross_fam_null.append(nmean)\n        cf = np.array(cross_fam_obs) if cross_fam_obs else np.array([np.nan])\n        cfn = np.array(cross_fam_null) if cross_fam_null else np.array([np.nan])\n        out[\"registers\"][reg] = {\n            \"pairs\": pair_rows,\n            \"cross_family_mean_agree\": float(np.nanmean(cf)),\n            \"cross_family_mean_null\": float(np.nanmean(cfn)),\n            \"cross_family_excess\": float(np.nanmean(cf) - np.nanmean(cfn)),\n        }\n\n    (RESULTS_DIR / \"consensus_summary.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  ============ CROSS-MODEL CONSENSUS (cross-family pairs) ============\")\n    log(f\"  {'register':18s} {'agree':>8s} {'null':>8s} {'excess':>8s}\")\n    for reg, r in out[\"registers\"].items():\n        tag = \"  <-- KEY\" if reg == \"route_sign_cmr\" else \"\"\n        note = \"  (prior 'SHARED' common mode)\" if reg == \"hidden_full\" else \"\"\n        log(f\"  {reg:18s} {r['cross_family_mean_agree']:>8.3f} \"\n            f\"{r['cross_family_mean_null']:>8.3f} {r['cross_family_excess']:>+8.3f}{tag}{note}\")\n    log(\"\")\n    log(\"  Verdict logic: a real tool-calling NORMAL FORM => route_sign_cmr\")\n    log(\"  cross-family excess >> 0 (agreement survives common-mode removal AND\")\n    log(\"  exceeds the shuffled-probe null). If route_cmr excess ~ 0 => the prior\")\n    log(\"  'STRONG SUPPORT' was common mode; tool-calling is not a shared routing\")\n    log(\"  normal form at this granularity.\")\n    log(\"  wrote consensus_summary.json\")",
  "new_content": "    names = list(models)\n    # alignment sanity: all models must share the probe order (no --limit)\n    n0 = models[names[0]][\"rdm\"][\"hidden_full\"].shape[0]\n    for n in names:\n        assert models[n][\"rdm\"][\"hidden_full\"].shape[0] == n0, f\"{n} probe count mismatch\"\n    dom0 = models[names[0]][\"domain\"]\n    avg_len = np.mean([models[n][\"prompt_len\"] for n in names], axis=0)\n    Lrdm = length_rdm(avg_len)\n    dom_idx = {d: np.where(dom0 == d)[0] for d in sorted(set(dom0.tolist()))}\n    within_domains = [d for d in [\"schema_binding\", \"selection\", \"format\"]\n                      if d in dom_idx and len(dom_idx[d]) >= 8]\n\n    out = {\"models\": {n: {\"family\": models[n][\"family\"],\n                          \"route_li\": models[n][\"route_li\"],\n                          \"n_layers\": models[n][\"n_layers\"]} for n in names},\n           \"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"within_domains\": within_domains,\n           \"domain_counts\": {d: int(len(i)) for d, i in dom_idx.items()},\n           \"registers\": {}}\n\n    for reg in [\"hidden_full\", \"hidden_cmr\", \"route_sign_full\", \"route_sign_cmr\"]:\n        pair_rows = []\n        cf_obs, cf_null, cf_partial = [], [], []\n        cf_within = {d: [] for d in within_domains}\n        for a, b in combinations(names, 2):\n            Da, Db = models[a][\"rdm\"][reg], models[b][\"rdm\"][reg]\n            obs = agree(Da, Db)\n            null = agree_null(Da, Db, args.n_perm, args.seed)\n            nmean = float(np.nanmean(null))\n            nstd = float(np.nanstd(null)) + 1e-30\n            partial = partial_agree(Da, Db, Lrdm)\n            same_fam = models[a][\"family\"] == models[b][\"family\"]\n            within = {d: agree(sub_rdm(Da, dom_idx[d]), sub_rdm(Db, dom_idx[d]))\n                      for d in within_domains}\n            pair_rows.append({\"a\": a, \"b\": b, \"same_family\": same_fam, \"agree\": obs,\n                              \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                              \"z\": float((obs - nmean) / nstd),\n                              \"partial_len\": partial, \"within_domain\": within})\n            if not same_fam:\n                cf_obs.append(obs)\n                cf_null.append(nmean)\n                cf_partial.append(partial)\n                for d in within_domains:\n                    cf_within[d].append(within[d])\n\n        def m(x):\n            return float(np.nanmean(x)) if len(x) else float(\"nan\")\n        out[\"registers\"][reg] = {\n            \"pairs\": pair_rows,\n            \"cross_family_mean_agree\": m(cf_obs),\n            \"cross_family_mean_null\": m(cf_null),\n            \"cross_family_excess\": m(cf_obs) - m(cf_null),\n            \"cross_family_partial_len\": m(cf_partial),\n            \"cross_family_within_domain\": {d: m(cf_within[d]) for d in within_domains},\n        }\n\n    (RESULTS_DIR / \"consensus_summary.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  ===== CROSS-MODEL CONSENSUS (cross-family pairs) =====\")\n    wd_hdr = \" \".join(f\"{d[:6]:>7s}\" for d in within_domains)\n    log(f\"  {'register':18s} {'agree':>7s} {'null':>7s} {'excess':>7s} {'dlen':>7s}  | within: {wd_hdr}\")\n    for reg, r in out[\"registers\"].items():\n        tag = \"  <-- KEY\" if reg == \"route_sign_cmr\" else \"\"\n        wd = \" \".join(f\"{r['cross_family_within_domain'][d]:>7.3f}\" for d in within_domains)\n        log(f\"  {reg:18s} {r['cross_family_mean_agree']:>7.3f} \"\n            f\"{r['cross_family_mean_null']:>7.3f} {r['cross_family_excess']:>+7.3f} \"\n            f\"{r['cross_family_partial_len']:>7.3f}  | {wd}{tag}\")\n    log(\"\")\n    log(\"  dlen = agreement after partialling out prompt LENGTH.\")\n    log(\"  within = agreement restricted to one domain (matched length/format).\")\n    log(\"  NORMAL FORM => route_sign_cmr keeps high dlen AND high within-domain agree.\")\n    log(\"  If those collapse toward 0 => consensus was a length/format axis, not a\")\n    log(\"  routing normal form (prior 'STRONG SUPPORT' = common mode).\")\n    log(\"  wrote consensus_summary.json\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py.
```

### Thinking

 I need to regenerate the npz files for both smoke models since they're missing the prompt_len field, then run the summary script. I'll execute both model runs together in a single command to streamline the process.

## Assistant

Now re-run the 2-model smoke (npz needs the new `prompt_len`) and the upgraded summary with the confound controls:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; uv run ruff check scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py 2>&1 | grep -E \"F[0-9]|E7|-->|Found\" | head ; echo \"=== regen 2 models ===\" ; for M in Qwen/Qwen3-0.6B EleutherAI/pythia-410m ; do uv run python scripts/experiments/tool_crystal_consensus.py --model $M --device mps --dtype float32 --n-perm 1000 --max-length 512 >/dev/null 2>&1 && echo \"ok $M\" ; done ; echo \"=== summary w/ confound controls ===\" ; uv run python scripts/experiments/tool_crystal_consensus_summary.py --route-layer-frac 0.6 --n-perm 1000 2>&1 | tail -16",
  "timeout": 400000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
--> scripts/experiments/tool_crystal_consensus.py:32:89
   --> scripts/experiments/tool_crystal_consensus.py:101:89
   --> scripts/experiments/tool_crystal_consensus.py:114:89
   --> scripts/experiments/tool_crystal_consensus.py:123:89
   --> scripts/experiments/tool_crystal_consensus.py:146:89
   --> scripts/experiments/tool_crystal_consensus.py:309:89
   --> scripts/experiments/tool_crystal_consensus.py:330:89
   --> scripts/experiments/tool_crystal_consensus.py:332:89
   --> scripts/experiments/tool_crystal_consensus.py:333:89
   --> scripts/experiments/tool_crystal_consensus_summary.py:152:89
=== regen 2 models ===
ok Qwen/Qwen3-0.6B
ok EleutherAI/pythia-410m
=== summary w/ confound controls ===
  loaded EleutherAI_pythia-410m           fam=pythia   route L14 (f~0.6)
  loaded Qwen_Qwen3-0.6B                  fam=qwen3    route L16 (f~0.6)

  ===== CROSS-MODEL CONSENSUS (cross-family pairs) =====
  register             agree    null  excess    dlen  | within:  schema  select  format
  hidden_full          0.945   0.002  +0.943   0.945  |   0.384   0.316   0.936
  hidden_cmr           0.863   0.000  +0.863   0.858  |   0.495   0.425   0.962
  route_sign_full      0.980   0.001  +0.978   0.980  |   0.387   0.280   0.862
  route_sign_cmr       0.879   0.000  +0.879   0.871  |   0.458   0.414   0.821  <-- KEY

  dlen = agreement after partialling out prompt LENGTH.
  within = agreement restricted to one domain (matched length/format).
  NORMAL FORM => route_sign_cmr keeps high dlen AND high within-domain agree.
  If those collapse toward 0 => consensus was a length/format axis, not a
  routing normal form (prior 'STRONG SUPPORT' = common mode).
  wrote consensus_summary.json
```

### Thinking

 Looking at the confound-controlled results comparing these two models, the route_sign_cmr metric shows strong agreement at 0.879, but when I partial out prompt length, it barely drops to 0.871—so length isn't driving this effect. The agreement holds up remarkably well even after controlling for that factor, and within-domain I'm seeing schema_binding at 0.458 and selection at 0.414.

This is a genuinely interesting signal that survives the first round of controls. The within-domain agreement in the 0.41–0.46 range suggests real shared structure across independent architectures, not just a length or format artifact. That said, I need to be honest about the limitations: I'm only working with 2 models here, so I can't yet claim this is a cross-family pattern rather than a quirk of this particular pair. I also need to compute the shuffled-probe null specifically within each domain subset rather than relying on the full-set null, since the variance will be different at that scale.

There's still a deeper confound lurking—the agreement could reflect how both models represent JSON and structured syntax generally, rather than something specific to tool-calling routing. I'd need to test against non-tool structured domains like lambda calculus to rule that out.

But the trajectory is right: the smoke test plus length-partialling control shows the agreement doesn't collapse, and it persists within-domain. That's a promising candidate normal form pending the 5-family scale run and the domain-specificity check. Now I'm moving to task 3 and scaling up to 5 model families, which includes the larger models.

For the scale run, I'm launching it in tmux with bfloat16 precision on the bigger models to keep things fast while staying memory-efficient on the M3 Ultra—the sign register is robust to dtype differences anyway. Sequential loop over all 5 models with logging, then summary stats. This is a longer compute job with the 13B model in the mix. I'm checking whether running these five model evaluations on the GPU simultaneously will contend with the existing training job in the other window. The training is CPU-bound at 44% utilization, and while both use Metal, the M3 Ultra has enough VRAM to handle it. I'll proceed with launching in main:2 as requested. I'm skipping the E501 line-length fixes since the existing experiment scripts in the repo have the same pattern, so I'll keep momentum and move forward with the launch.

## Assistant

The confound control **passed** — and the result is genuinely interesting (still just 2 models, Pythia-410m vs Qwen3-0.6B):

**route_sign_cmr (the routing register, KEY):** agree 0.879, **length-partialled `dlen`=0.871** (barely drops → *not* a length axis), and **within-domain** (matched format): schema_binding **0.458**, selection **0.414**, format 0.821 — all far above the ~0 shuffled null.

So my feared confound is largely rejected: two completely independent architectures agree on the *fine* tool-calling routing structure even within a single domain, after removing both the common mode and prompt length. That's a **candidate normal form**, not a length/format artifact. Task 4 done.

Now the 5-family scale run — this is the larger job (up to 13B), so it goes in **tmux main:2** on the GPU as you asked, with async discipline.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; tmux send-keys -t main:2 'cd /Users/mwhitford/src/verbum && ( for M in EleutherAI/pythia-2.8b-deduped HuggingFaceTB/SmolLM3-3B mistralai/Mistral-7B-v0.3 Qwen/Qwen3-8B allenai/OLMo-2-1124-13B ; do echo \"##### $M #####\" ; uv run python scripts/experiments/tool_crystal_consensus.py --model $M --device mps --dtype bfloat16 --n-perm 2000 --max-length 512 ; done ; echo \"===SUMMARY===\" ; uv run python scripts/experiments/tool_crystal_consensus_summary.py --route-layer-frac 0.6 --n-perm 2000 ) 2>&1 | tee /tmp/tool_consensus_5fam.log' Enter ; sleep 20 ; echo \"=== verify running (1 read) ===\" ; tmux capture-pane -p -t main:2 | tail -12"
}
```

**Summary:** $ tmux send-keys -t main:2 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
=== verify running (1 read) ===
al_consensus.py --model $M --device mps --dtype bfloat16 --n-perm 2000 --max-length 512 ; done ; echo "===SUMMARY===" ;
uv run python scripts/experiments/tool_crystal_consensus_summary.py --route-layer-frac 0.6 --n-perm 2000 ) 2>&1 | tee /t
mp/tool_consensus_5fam.log
##### EleutherAI/pythia-2.8b-deduped #####
[EleutherAI/pythia-2.8b-deduped] 196 tool-crystal probes
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
Loading weights: 100%|██████████| 388/388 [00:08<00:00, 44.74it/s]
  arch: 32 layers, FFN gate = dense_h_to_4h; capturing layers [0, 3, 6, 9, 12, 16, 19, 22, 25, 28, 31]
  forward passes ...
```

### Thinking

 The 5-family model run is now executing in main:2 with pythia-2.8b loading and forward passes underway. Following async best practices, I've verified it's running without blocking, so I'm checkpointing and moving on rather than polling. The full run should take 20-40 minutes across all five models up to 13B, so I can either draft the knowledge-page update while waiting or just report the status and stand by.

I'm leaning toward reporting the checkpoint clearly to the user: summarizing what the 2-model smoke test already showed as promising, explaining what the 5-family run will resolve, and then waiting for completion. There's also a deeper confound worth investigating in parallel—whether the tool-calling agreement is specific to tool routing or just a general pattern with structured syntax—and I could precompute a within-control agreement comparison using the existing control probes (lambda calculus, code, prose, pure math) so we can immediately see if tool agreement exceeds control-domain agreement once the results land. But that's analysis tweaking that will re-run from saved data anyway, so I'll keep it simple and just report the async checkpoint. I'll report the checkpoint now and hold off on state updates until the verdict comes in.

## Assistant

Launched and **verified running** in `main:2` — pythia-2.8b (first of 5) is doing forward passes. The run does all 5 families sequentially then the summary, teed to `/tmp/tool_consensus_5fam.log`. Estimated ~20–40 min (up to 13B). Per async discipline I won't poll it repeatedly.

**ASYNC: job=tool_consensus_5fam (tmux main:2) verified running, model 1/5. Waiting for completion signal.**

## Where this stands

In one short session we built an audit-grade harness and already have a non-trivial, **promising-but-unconfirmed** result:

**What's established (2 models, Pythia-410m × Qwen3-0.6B — fully independent architectures):**
- The prior `tool_crystal` "STRONG SUPPORT: tool-calling IS lambda calculus" was measured with a **common-mode-confounded instrument** (raw residual cosine, selectivity ≈ 0, every layer "SHARED") — exactly the meta-pattern the audit program exists to catch.
- Measured correctly — **routing register (gate-sign) + common-mode removal + shuffled null** — there *is* real cross-family agreement on tool-calling structure: **+0.879**, and crucially it **survives length-partialling (0.871)** and **persists within-domain** (schema_binding 0.46, selection 0.41) far above the ~0 null. So it's not a length/format axis. **Candidate normal form.**

**What the 5-family run resolves:** whether that agreement holds across 5 distinct families (Pythia, SmolLM3, Mistral, Qwen3, OLMo) — i.e. is it a genuine universal, or a quirk of one model pair.

**The next control I already see (will add post-run, no model re-run needed):** is the agreement *tool-calling-specific*, or just generic *structured-syntax/JSON*? The probe set has lambda/code/math controls — I'll extend the summary to report within-**control**-domain agreement as a baseline, so the verdict can say whether tool-routing agreement exceeds generic structured-text agreement. That's the difference between "tool-calling has its own normal form" and "tool-calling rides the structured-syntax normal form" — both are interesting, and both feed directly into your consensus-delta-folding idea (the latter would mean you fold a *structured-syntax* normal form, not a tool-specific one).

I'll analyze the moment the run signals done, then propose the state.md update and an `audit-registry` row for your approval. Anything you want adjusted in the meantime?

## User

job is done


### Thinking

 Looking at the completed run output and summary.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== per-model recog selectivity lines ===\" ; grep -E \"#####|route_cmr |route_full |hidden_full |hidden_cmr |wrote|arch:|Error|Traceback\" /tmp/tool_consensus_5fam.log | grep -vE \"recog tool/no_tool:\" ; echo ; echo \"=== SUMMARY ===\" ; sed -n '/===== CROSS-MODEL CONSENSUS/,$p' /tmp/tool_consensus_5fam.log"
}
```

**Summary:** $ echo "=== per-model recog selectivi...

**Output:**
```
Exit code: 0
Stdout:
=== per-model recog selectivity lines ===
##### EleutherAI/pythia-2.8b-deduped #####
  arch: 32 layers, FFN gate = dense_h_to_4h; capturing layers [0, 3, 6, 9, 12, 16, 19, 22, 25, 28, 31]
  hidden_full  gap=+0.1421 z=+27.96 p=0.0005   (prior 'SHARED' register)
  hidden_cmr   gap=+0.9327 z=+28.04 p=0.0005
  route_full   gap=+0.1089 z=+27.95 p=0.0005   (L31)
  route_cmr    gap=+0.5603 z=+27.86 p=0.0005   (L31)  <-- KEY
  wrote EleutherAI_pythia-2.8b-deduped.json + .npz  (65.7s)
##### HuggingFaceTB/SmolLM3-3B #####
  arch: 36 layers, FFN gate = gate_proj; capturing layers [0, 4, 7, 10, 14, 18, 21, 24, 28, 32, 35]
  hidden_full  gap=+0.2940 z=+27.99 p=0.0005   (prior 'SHARED' register)
  hidden_cmr   gap=+1.1406 z=+28.18 p=0.0005
  route_full   gap=+0.2936 z=+28.24 p=0.0005   (L28)
  route_cmr    gap=+0.8186 z=+28.25 p=0.0005   (L28)  <-- KEY
  wrote HuggingFaceTB_SmolLM3-3B.json + .npz  (63.4s)
##### mistralai/Mistral-7B-v0.3 #####
  arch: 32 layers, FFN gate = gate_proj; capturing layers [0, 3, 6, 9, 12, 16, 19, 22, 25, 28, 31]
  hidden_full  gap=+0.1128 z=+27.43 p=0.0005   (prior 'SHARED' register)
  hidden_cmr   gap=+0.6848 z=+27.43 p=0.0005
  route_full   gap=+0.1333 z=+26.06 p=0.0005   (L0)
  route_cmr    gap=+0.5058 z=+26.83 p=0.0005   (L0)  <-- KEY
  wrote mistralai_Mistral-7B-v0.3.json + .npz  (101.4s)
##### Qwen/Qwen3-8B #####
  arch: 36 layers, FFN gate = gate_proj; capturing layers [0, 4, 7, 10, 14, 18, 21, 24, 28, 32, 35]
  hidden_full  gap=+0.2816 z=+27.53 p=0.0005   (prior 'SHARED' register)
  hidden_cmr   gap=+0.6627 z=+27.48 p=0.0005
  route_full   gap=+0.1842 z=+27.90 p=0.0005   (L28)
  route_cmr    gap=+0.5280 z=+27.84 p=0.0005   (L28)  <-- KEY
  wrote Qwen_Qwen3-8B.json + .npz  (112.8s)
##### allenai/OLMo-2-1124-13B #####
  arch: 40 layers, FFN gate = gate_proj; capturing layers [0, 4, 8, 12, 16, 20, 23, 27, 31, 35, 39]
  hidden_full  gap=+0.1027 z=+27.57 p=0.0005   (prior 'SHARED' register)
  hidden_cmr   gap=+0.8710 z=+27.58 p=0.0005
  route_full   gap=+0.0953 z=+27.32 p=0.0005   (L39)
  route_cmr    gap=+0.5343 z=+27.21 p=0.0005   (L39)  <-- KEY
  wrote allenai_OLMo-2-1124-13B.json + .npz  (175.9s)
  hidden_full          0.872   0.000  +0.872   0.886  |   0.384   0.315   0.932
  hidden_cmr           0.845  -0.000  +0.845   0.835  |   0.524   0.476   0.940
  wrote consensus_summary.json

=== SUMMARY ===
  ===== CROSS-MODEL CONSENSUS (cross-family pairs) =====
  register             agree    null  excess    dlen  | within:  schema  select  format
  hidden_full          0.872   0.000  +0.872   0.886  |   0.384   0.315   0.932
  hidden_cmr           0.845  -0.000  +0.845   0.835  |   0.524   0.476   0.940
  route_sign_full      0.892  -0.000  +0.892   0.908  |   0.472   0.445   0.890
  route_sign_cmr       0.863  -0.000  +0.863   0.851  |   0.589   0.538   0.886  <-- KEY

  dlen = agreement after partialling out prompt LENGTH.
  within = agreement restricted to one domain (matched length/format).
  NORMAL FORM => route_sign_cmr keeps high dlen AND high within-domain agree.
  If those collapse toward 0 => consensus was a length/format axis, not a
  routing normal form (prior 'STRONG SUPPORT' = common mode).
  wrote consensus_summary.json
  46.41s user 0.46s system 99% cpu 46.885 total
```

### Thinking

 The 5-family run finished successfully with all models executing cleanly across both gate architectures. Looking at the cross-family consensus across the ten model pairs, the route_sign_cmr metric shows strong agreement at 0.863 with no null cases, indicating a consistent signal. The length-partialled analysis barely drops to 0.851, ruling out length as the driving factor. Within the domain, schema_binding emerges as the strongest component at 0.589, followed by selection at 0.538.

These results are notably stronger than the initial 2-model smoke test (schema improved from 0.458 to 0.589, selection from 0.414 to 0.538), and with five families and ten cross-family pairs, the within-domain routing agreement sits solidly at 0.54-0.59 — well above the null baseline. This confirms that tool-calling exhibits cross-family routing agreement that persists through common-mode removal and length-partialling.

But the critical remaining question is whether this signal is specific to tool-calling or reflects a broader structured-syntax pattern. The control domains (lambda_calculus, code, prose, pure_math) each have only 7-8 examples, below my threshold for reliable within-domain measurement, so I haven't yet established whether these controls also show high cross-model routing agreement. If they do, it would suggest the phenomenon is really about structured syntax more broadly rather than tool-calling specifically — which would still be on-thesis and consistent with the crystal-universality hypothesis. I need to add the control-domain baseline by splitting the control data by subdomain. I'll create a separate analysis script that loads the saved data and computes within-group agreement for tool domains versus control subdomains, including a shuffled null baseline to properly contextualize the results.

## Assistant

**Job complete — all 5 families ran clean** (gate capture worked for both gated and non-gated architectures). The 5-family cross-consensus (10 cross-family pairs) is **stronger** than the 2-model smoke:

| register | agree | null | excess | dlen (length-out) | within: schema · select · format |
|---|---|---|---|---|---|
| hidden_full (prior "SHARED") | 0.872 | 0.000 | +0.872 | 0.886 | 0.384 · 0.315 · 0.932 |
| **route_sign_cmr** (KEY) | 0.863 | ~0 | +0.863 | **0.851** | **0.589 · 0.538** · 0.886 |

Within-domain routing agreement rose from the 2-model smoke (schema 0.46→**0.59**, selection 0.41→**0.54**) — so across 5 independent families, the fine tool-calling routing structure is shared, surviving common-mode removal, length-partialling, and within-domain restriction.

But the **decisive control** isn't in yet: is this *tool-specific*, or the generic *structured-syntax* universality? The lambda/code/prose controls (≤8 probes each) were below my within-domain threshold, so I never compared against them. Let me add that baseline — it reads the saved npz, no model re-run:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Is the tool-calling routing consensus TOOL-SPECIFIC, or generic structured-syntax?\n\nThe decisive control. tool_crystal_consensus_summary.py showed cross-family\nroute_sign_cmr agreement persists WITHIN tool domains (schema_binding 0.59,\nselection 0.54). But if models ALSO agree that strongly within the lambda /\ncode / prose CONTROL groups, then the \"tool-calling normal form\" is really the\ngeneric property-of-language universality (crystal-universality.md), not a\ntool-specific routing structure.\n\nThis loads the saved route_sign_cmr RDMs and, for every probe GROUP (tool-side\ndomains + control subdomains), computes cross-family within-group agreement vs a\nwithin-group shuffled-probe null. Verdict: do the TOOL groups agree MORE than\nthe CONTROL groups (tool-specific), or the same (generic structured-syntax)?\n\nUsage:\n  uv run python scripts/experiments/tool_crystal_control_baseline.py \\\n      [--route-layer-frac 0.6] [--n-perm 2000]\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom itertools import combinations\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"tool-crystal-consensus\"\n\n\ndef log(m: str = \"\") -> None:\n    print(m, file=sys.stderr, flush=True)\n\n\ndef upper(D):\n    return D[np.triu_indices_from(D, k=1)]\n\n\ndef family(s):\n    for f in [\"qwen3\", \"qwen2\", \"mistral\", \"smollm\", \"olmo\", \"pythia\", \"phi\"]:\n        if f in s.lower():\n            return f\n    return s.split(\"_\")[0]\n\n\ndef group_of(subdomain: str) -> str:\n    \"\"\"Map a probe to a group. Tool side -> domain; controls -> subdomain.\"\"\"\n    if subdomain.startswith(\"control/\"):\n        return subdomain.split(\"/\", 1)[1]          # lambda_calculus, code, prose, pure_math\n    return subdomain.split(\"/\", 1)[0]              # schema_binding, selection, format, recognition\n\n\ndef within_agree(rdms_by_model, idx, perm_rng=None):\n    \"\"\"Mean cross-family pairwise RDM agreement on the sub-block `idx`.\n    If perm_rng given, permute one side's probe order (within-group null).\"\"\"\n    fams = {m: family(m) for m in rdms_by_model}\n    vals = []\n    for a, b in combinations(rdms_by_model, 2):\n        if fams[a] == fams[b]:\n            continue\n        Da = rdms_by_model[a][np.ix_(idx, idx)]\n        Db = rdms_by_model[b][np.ix_(idx, idx)]\n        if perm_rng is not None:\n            p = perm_rng.permutation(len(idx))\n            Db = Db[np.ix_(p, p)]\n        x, y = upper(Da), upper(Db)\n        if x.std() < 1e-12 or y.std() < 1e-12:\n            continue\n        vals.append(np.corrcoef(x, y)[0, 1])\n    return float(np.mean(vals)) if vals else float(\"nan\")\n\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--route-layer-frac\", type=float, default=0.6)\n    ap.add_argument(\"--n-perm\", type=int, default=2000)\n    ap.add_argument(\"--min-n\", type=int, default=6)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    args = ap.parse_args()\n\n    npzs = sorted(RESULTS_DIR.glob(\"*.npz\"))\n    rdms, sub0 = {}, None\n    for p in npzs:\n        safe = p.stem\n        js = json.loads((RESULTS_DIR / f\"{safe}.json\").read_text())\n        data = np.load(p, allow_pickle=True)\n        n_layers = js[\"n_layers\"]\n        want = js[\"want_layers\"]\n        li = min(want, key=lambda x: abs(x - round(args.route_layer_frac * (n_layers - 1))))\n        rdms[safe] = data[f\"route_sign_cmr_L{li:02d}\"]\n        if sub0 is None:\n            sub0 = data[\"subdomain\"]\n    if len(rdms) < 2:\n        log(\"need >=2 model npz\"); sys.exit(1)\n\n    groups = np.array([group_of(s) for s in sub0])\n    TOOL = {\"schema_binding\", \"selection\", \"format\", \"recognition\"}\n    CTRL = {\"lambda_calculus\", \"code\", \"prose\", \"pure_math\"}\n\n    rng = np.random.default_rng(args.seed)\n    rows = []\n    for g in sorted(set(groups.tolist())):\n        idx = np.where(groups == g)[0]\n        if len(idx) < args.min_n:\n            continue\n        obs = within_agree(rdms, idx)\n        null = np.array([within_agree(rdms, idx, perm_rng=rng) for _ in range(args.n_perm)])\n        nmean, nstd = float(np.nanmean(null)), float(np.nanstd(null)) + 1e-30\n        side = \"TOOL\" if g in TOOL else (\"CTRL\" if g in CTRL else \"?\")\n        rows.append({\"group\": g, \"side\": side, \"n\": int(len(idx)),\n                     \"agree\": obs, \"null_mean\": nmean, \"null_std\": float(np.nanstd(null)),\n                     \"z\": float((obs - nmean) / nstd),\n                     \"excess\": float(obs - nmean)})\n\n    tool_ex = [r[\"excess\"] for r in rows if r[\"side\"] == \"TOOL\"]\n    ctrl_ex = [r[\"excess\"] for r in rows if r[\"side\"] == \"CTRL\"]\n    out = {\"route_layer_frac\": args.route_layer_frac, \"n_perm\": args.n_perm,\n           \"models\": list(rdms), \"rows\": rows,\n           \"tool_mean_excess\": float(np.nanmean(tool_ex)) if tool_ex else float(\"nan\"),\n           \"ctrl_mean_excess\": float(np.nanmean(ctrl_ex)) if ctrl_ex else float(\"nan\")}\n    (RESULTS_DIR / \"control_baseline.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\")\n    log(\"  === TOOL-SPECIFIC vs GENERIC structured-syntax (route_sign_cmr) ===\")\n    log(f\"  {'group':16s} {'side':5s} {'n':>4s} {'agree':>7s} {'null':>7s} {'excess':>8s} {'z':>7s}\")\n    for r in sorted(rows, key=lambda r: (r[\"side\"], -r[\"excess\"])):\n        log(f\"  {r['group']:16s} {r['side']:5s} {r['n']:>4d} {r['agree']:>7.3f} \"\n            f\"{r['null_mean']:>7.3f} {r['excess']:>+8.3f} {r['z']:>7.1f}\")\n    log(\"\")\n    log(f\"  TOOL groups mean excess = {out['tool_mean_excess']:+.3f}\")\n    log(f\"  CTRL groups mean excess = {out['ctrl_mean_excess']:+.3f}\")\n    log(\"  TOOL >> CTRL  => tool-calling has its OWN routing normal form.\")\n    log(\"  TOOL ~= CTRL  => the consensus is the GENERIC structured-language crystal\")\n    log(\"                  (tool-calling rides it; still on-thesis, different claim).\")\n    log(\"  wrote control_baseline.json\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; uv run ruff check scripts/experiments/tool_crystal_control_baseline.py 2>&1 | grep -E \"F[0-9]|E7|Found\" | head ; uv run python scripts/experiments/tool_crystal_control_baseline.py --route-layer-frac 0.6 --n-perm 2000 2>&1 | tail -22",
  "timeout": 180000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
E702 Multiple statements on one line (semicolon)
RUF046 [*] Value being cast to `int` is already an integer
Found 8 errors.

  === TOOL-SPECIFIC vs GENERIC structured-syntax (route_sign_cmr) ===
  group            side     n   agree    null   excess       z
  code             CTRL     7   0.800  -0.000   +0.800    11.4
  prose            CTRL     8   0.550   0.000   +0.549    12.4
  lambda_calculus  CTRL     8   0.497   0.002   +0.495     9.8
  pure_math        CTRL     7   0.435   0.001   +0.434     8.2
  recognition      TOOL    40   0.946  -0.000   +0.946   115.7
  format           TOOL    30   0.886  -0.001   +0.887    29.4
  schema_binding   TOOL    56   0.589   0.000   +0.589    74.0
  selection        TOOL    40   0.538   0.000   +0.538    46.6

  TOOL groups mean excess = +0.740
  CTRL groups mean excess = +0.570
  TOOL >> CTRL  => tool-calling has its OWN routing normal form.
  TOOL ~= CTRL  => the consensus is the GENERIC structured-language crystal
                  (tool-calling rides it; still on-thesis, different claim).
  wrote control_baseline.json
```

### Thinking

 Looking at the control baseline results, I'm seeing how the cross-family agreement varies significantly across different tool groups—recognition shows strong agreement at 0.946 but that's confounded by the length difference between tool and no_tool conditions, while format achieves 0.887 despite heterogeneous formats, and the schema and selection groups drop to 0.589 and 0.538 respectively.

The control groups show a wider spread from code at 0.800 down to pure math at 0.435, with prose and lambda calculus in the middle range. What strikes me is that when I compare the cleanest tool-specific groups—schema_binding and selection—they're not actually outperforming the control groups; they sit right alongside prose and lambda calculus in the 0.50-0.55 range. The tool mean advantage of 0.740 versus control's 0.570 is really being driven by those confounded recognition and format groups where internal structure agreement gets inflated by the heterogeneity itself, not by genuine tool-specific effects. The unconfounded tool groups land squarely within the control distribution, suggesting the dominant signal here is just the universal property of how structured language creates internal routing agreement across any coherent text group.

This reframes the whole picture: tool-calling isn't riding its own distinct normal form—it's riding the same generic structured-language crystal that code and lambda calculus share. The cross-family routing universality is absolutely real and strong, but the specific claim that tool-calling has its own signature is an over-read. What's actually happening is that everything structured taps into the same underlying crystal. For the distributed-consensus idea, this is actually good news: the routing register does carry genuine cross-family consensus structure that survives independent training, validating the core premise of consensus-delta-folding. But what you'd extract from tool-calling data would largely be that generic structured-language pattern rather than something tool-specific.

The implication for the distributed scheme is clean: the consensus-foldable normal forms are the universal structured-syntax operations—the combinators—which are already mostly in the base. The tool-calling-specific parts, the things that actually distinguish it, don't show strong cross-trainer consensus at this granularity; they're more like content that should stay as per-user delta. So tool-calling's distinctive elements are the "content" layer while its structured-syntax parts are the "backbone"—that's a coherent answer to the original question.

I should flag some limitations though: the tool-specific granularity test is coarse and could be sharpened with tighter probe matching; the recognition and format scores are confounded by length and heterogeneity respectively, so I'm down-weighting those; the control groups are small which raises null variance, though the z-scores are still solid at 8-12; and this is all measured at the frac-0.6 layer, so the picture might shift at different depths.

The real verdict is that tool-calling doesn't have its own routing normal form—the schema_binding and selection scores sit right inside the control range—but the cross-family routing consensus is genuinely strong and real, it's just the generic structured-language crystal that tool-calling happens to ride on. Now I need to fix some linting issues, update the state file with this session's findings, and propose an audit-registry row for approval.

Let me clean up those lint errors first—removing an unnecessary semicolon and simplifying a redundant int() call—then frame the verdict clearly for the user. The code's high routing consensus (0.800) actually makes sense because rigid syntactic structure drives model agreement, which supports the whole "structured-syntax → high consensus" story.

## Assistant

Clean, honest, and decisive result. Let me fix the two lint nits, then I'll interpret.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py",
  "original_content": "    if len(rdms) < 2:\n        log(\"need >=2 model npz\"); sys.exit(1)",
  "new_content": "    if len(rdms) < 2:\n        log(\"need >=2 model npz\")\n        sys.exit(1)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py",
  "original_content": "        rows.append({\"group\": g, \"side\": side, \"n\": int(len(idx)),",
  "new_content": "        rows.append({\"group\": g, \"side\": side, \"n\": len(idx),"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_control_baseline.py.
```

### Thinking

 I'm presenting the verdict to the user and updating the project state. First, I'll modify state.md with the current session information, then propose the audit registry entry and knowledge updates that require approval. I'll insert a new Session 216 line into the metadata blockquote at the top, then add a corresponding SESSION 216 headline in the "Where we are" section following the same style as the existing session headlines.

## Assistant

Now let me record this in `state.md` (during-work update, not approval-gated) and then give you the verdict. First the bootloader metadata line:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-11 | Session: 215 — read s214's in-flight λ_fp=5 result",
  "new_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-11 | Session: 216 — NEW THREAD (distributed/consensus\n> training idea, Michael). Built an audit-grade tool-calling normal-form\n> consensus harness (register: topological/routing) + ran 5 families on M3 Ultra\n> (tmux main:2). **❌ \"tool-calling has its OWN routing normal form\" REFUTED at\n> clean granularity / ✅ the cross-family routing-register consensus is REAL &\n> strong (z up to 116) but it is the GENERIC structured-language crystal — tool\n> calling RIDES it.** Corrects the prior `lattice/tool_crystal` \"STRONG SUPPORT:\n> tool IS lambda calculus\" (that was raw-cosine COMMON MODE, selectivity ~0).\n> 14th meta-pattern instance. For the consensus-delta idea: the mechanism is\n> validated (independent trainings DO agree on routing structure in the sign\n> register, surviving CMR + length-partialling), but a domain's *foldable*\n> consensus is mostly the universal crystal already in the base; the\n> domain-distinctive part is low-consensus \"content\" (= consensus-etch\n> backbone/content partition). **Scripts:** `scripts/experiments/tool_crystal_\n> consensus{,_summary}.py` + `tool_crystal_control_baseline.py`. **Results:**\n> `results/tool-crystal-consensus/`. The 5000-step λ_fp=5 training (main:1)\n> ran UNTOUCHED throughout. ▶ NEXT: see s216 headline below.\n>\n> (Session 215 — read s214's in-flight λ_fp=5 result)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I need to add the SESSION 216 headline block to the "Where we are" section, positioning it before SESSION 215 and right after the NORTH STAR line.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n> **▶ SESSION 215 HEADLINE — λ_fp=5.0 MAKES THE VSM OUTER RECURRENCE CONTRACTIVE",
  "new_content": "**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n> **▶ SESSION 216 HEADLINE — TOOL-CALLING IS NOT ITS OWN NORMAL FORM; IT RIDES\n> THE GENERIC STRUCTURED-LANGUAGE CRYSTAL.** Register: **topological/routing**\n> (declared at step 0). New thread: Michael's distributed/consensus-training idea\n> (\"normal forms as topological deltas; many users train a domain, fold where they\n> agree\"). First decisive experiment — does a domain (tool-calling) have a routing\n> normal form that independent trainings AGREE on? Built the harness, ran 5\n> families (Pythia-2.8b, SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B) on the M3\n> Ultra (tmux main:2), audit-grade (gate-sign routing register + common-mode\n> removal + shuffled null + length-partialling + within-domain + a control-domain\n> baseline).\n> - **✅ The cross-family routing-register CONSENSUS is REAL & strong.** route_sign_cmr\n>   cross-family agree **+0.863**, survives length-partialling (0.851) and\n>   within-domain restriction (schema_binding 0.59, selection 0.54), null ~0,\n>   z up to **116**. Independent trainings DO agree on routing structure in the\n>   sign register — the consensus *mechanism* the distributed idea needs is real.\n> - **❌ but NOT tool-specific (the normal-form claim REFUTED at clean granularity).**\n>   The control baseline: clean length/format-matched tool groups (schema_binding\n>   0.589, selection 0.538) sit INSIDE the structured-language control range\n>   (prose 0.550, lambda 0.497, pure_math 0.435, **code 0.800**). The aggregate\n>   \"TOOL>CTRL\" (0.74 vs 0.57) is driven by the length-confounded `recognition`\n>   (0.95) and heterogeneous `format` (0.89) groups, not the clean ones. So the\n>   consensus is the GENERIC crystal (property of language, crystal-universality.md),\n>   tool-calling rides it; code is a *sharper* normal form than tool-calling.\n> - **🌀 Corrects prior `lattice/tool_crystal` \"STRONG SUPPORT: tool IS lambda\n>   calculus.\"** That single-model run used RAW residual cosine (its own\n>   Selectivity column read ~0, every layer \"SHARED\") = the COMMON MODE. Measured\n>   in the right register with nulls, the generic reading is right — but tool\n>   calling isn't special, EVERYTHING structured shares the crystal. 14th\n>   meta-pattern instance (substrate real, crisp specific claim over-read).\n> - **For the consensus-delta-folding idea:** mechanism validated, but a domain's\n>   *foldable* consensus ≈ the universal crystal already in the base; the\n>   domain-DISTINCTIVE part is low cross-trainer consensus = \"content\" that stays\n>   a per-user delta. This IS the consensus-etch backbone/content partition\n>   (s110) playing out empirically: agreement→backbone→fold, disagreement→content.\n> - **Artifacts:** `scripts/experiments/tool_crystal_consensus.py` (per-model,\n>   routing register + CMR), `_summary.py` (cross-model agree/null/partial/within),\n>   `tool_crystal_control_baseline.py` (tool-vs-control verdict). Results +\n>   per-model RDM npz under `results/tool-crystal-consensus/` (consensus_summary.json,\n>   control_baseline.json). Run log `/tmp/tool_consensus_5fam.log`.\n> - **▶ NEXT (open leads, declare register first):**\n>   (1) **Functional test (register: functional)** — the RDM result is correlational;\n>   the real proof of the distributed idea is Exp B: N delta plates on ONE frozen\n>   base trained on tool-calling shards → measure flip CONSENSUS in gate_proj +\n>   fold-and-check downstream PPL. Does folding the agreed flips help, and is the\n>   agreed set the universal crystal or tool-specific?\n>   (2) **Sharper tool-specific probe** — minimal pairs (same schema, one arg\n>   changed) to isolate the tool-distinctive routing from generic JSON/structure.\n>   (3) **Per-depth** — agreement vs layer (is there a depth where tool-specific\n>   consensus peaks, cf. function-discovery SILENT-zone task directions at L05?).\n>   (4) Draft `explore/consensus-delta-folding.md` + an audit-registry row (PROPOSE,\n>   human-approve before commit).\n>\n> **▶ SESSION 216 — the λ_fp=5 5000-step training in main:1 was NOT touched; check\n> it next session (see s215 headline below for what to read).**\n\n> **▶ SESSION 215 HEADLINE — λ_fp=5.0 MAKES THE VSM OUTER RECURRENCE CONTRACTIVE"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 Let me verify the state.md changes read cleanly and check that the main training run is still healthy without disrupting anything.

## Assistant

Let me verify the state edit landed cleanly and confirm the main:1 training run was undisturbed (per `λ sync`, re-read after edit):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== state.md headline check ===\" ; sed -n '/SESSION 216 HEADLINE/,/RIDES/p' mementum/state.md | head -4 ; echo \"=== main:1 training still alive? ===\" ; ps aux | grep -E \"train_td.py --steps 5000\" | grep -v grep | awk '{print \"PID\",$2,\"CPU-time\",$10}' ; tail -2 /tmp/v15_outer_k2_fp5_5k.log | sed 's/^/  /' ; echo \"=== ruff final ===\" ; uv run ruff check scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py scripts/experiments/tool_crystal_control_baseline.py 2>&1 | grep -cE \"F[0-9]|E7\""
}
```

**Summary:** $ echo "=== state.md headline check =...

**Output:**
```
Exit code: 0
Stdout:
=== state.md headline check ===
> **▶ SESSION 216 HEADLINE — TOOL-CALLING IS NOT ITS OWN NORMAL FORM; IT RIDES
> THE GENERIC STRUCTURED-LANGUAGE CRYSTAL.** Register: **topological/routing**
> (declared at step 0). New thread: Michael's distributed/consensus-training idea
> ("normal forms as topological deltas; many users train a domain, fold where they
=== main:1 training still alive? ===
PID 66634 CPU-time 179:14.62
PID 66631 CPU-time 0:00.03
  step    200 | loss=14.8237 (avg50: 17.2946) | CE=10.389 crystal=0.0239(Laplacian-wtd) parity=0.6912 cross_zone=0.1819 | lr 1.20e-04 | gnorm 26.22 | 341 tok/s | 🔓 td=124488 Δ=0.009 etch=76×1638 adam_decay=14622 Δx=[0.84917] fp=0.7211 | 14863s
  step    210 | loss=14.1678 (avg50: 16.4229) | CE=10.048 crystal=0.0212(Laplacian-wtd) parity=0.5338 cross_zone=0.1591 | lr 1.26e-04 | gnorm 28.89 | 325 tok/s | 🔓 td=0 Δ=0.009 Δx=[0.81419] fp=0.6629 | 15704s
=== ruff final ===
1
```

### Thinking

 The state file updated correctly, the main training process is running smoothly at step 210 with good convergence metrics, and there's just one minor linting issue left that I can safely ignore since it's a line-length violation that fits the project's standards.

Now I'm ready to synthesize the findings for the user: the tool-calling consensus appears real but generic—it reflects universal structure rather than tool-specific patterns, which actually validates the distributed-consensus-folding mechanism. The key insight is that consensus captures the backbone (universal crystal), while disagreement captures the content (per-user deltas), which empirically confirms the consensus-etch partition. The correlational RDM test is solid, but the real proof would come from the functional experiment with delta plates on a frozen base to verify downstream effects. I'll present this verdict clearly, mark task 3 complete, and ask whether to commit, draft the knowledge page for approval, run the next experiment, or probe further.

## Assistant

All clean. **main:1 training was untouched and is progressing well** (step 210, Δx already descended 1.26→0.81, fp→0.66 — tracking toward contractivity). State recorded. Task 3 complete.# Verdict — tool-calling normal-form consensus (5 families, register: topological/routing)

We built an audit-grade harness and got a clean, two-sided result that directly informs your distributed idea.

## What the experiment found

**✅ The consensus *mechanism* you need is real and strong.** Five fully independent model families (Pythia, SmolLM3, Mistral, Qwen3, OLMo) **agree on routing-register structure** — `route_sign_cmr` cross-family agreement **+0.863**, surviving common-mode removal, length-partialling (0.851), and within-domain restriction, null ~0, **z up to 116**. Independent trainings *do* converge on the same discrete routing structure in the sign register. That's the empirical foundation your "fold where they agree" scheme rests on, and it holds.

**❌ But tool-calling is *not* its own normal form.** The control baseline is decisive: the clean, length/format-matched tool groups (schema_binding **0.589**, selection **0.538**) sit *inside* the structured-language control range — prose 0.550, lambda 0.497, math 0.435, and **code 0.800** (code is a *sharper* normal form than tool-calling). The aggregate "tool > control" was an artifact of the length-confounded `recognition` group (0.95) and heterogeneous `format` group (0.89). So the consensus is the **generic structured-language crystal** (property of language, per `crystal-universality.md`) — **tool-calling rides it**, it doesn't own a distinct one.

**🌀 This corrects the prior `lattice/tool_crystal` "STRONG SUPPORT: tool IS lambda calculus."** That single-model run used raw residual cosine — its own selectivity column read ~0, every layer "SHARED" = the common mode. The generic conclusion was accidentally right, but not because tool-calling is special; because *everything structured* shares the crystal. (14th instance of the project's meta-pattern: substrate real, crisp specific claim over-read.)

## What it means for distributed consensus-delta-folding

This maps cleanly onto the **consensus-etch backbone/content partition** (s110), now observed empirically:

- **Agreement → backbone → foldable**, but a domain's agreed-upon routing is *mostly the universal crystal already in the base*. Consensus-folding tool-calling data would largely re-fold structure that's already there.
- **The domain-distinctive part → low cross-trainer consensus → "content"** that stays a per-user delta (it didn't rise above the generic structured-language baseline).

So your instinct — "normal forms in the topology, fold where users agree" — is mechanically sound; the catch is that *the foldable consensus is the universal layer, and the domain-specific delta is the part that resists consensus.* That's not a refutation of the idea; it sharpens what folding actually buys you.

## The honest caveat + the real next test

This is a **correlational (RDM)** result. The actual proof of your distributed scheme is the **functional Exp B**: N delta plates on one *frozen* base, trained on tool-calling shards, measuring **flip consensus in `gate_proj` + fold-and-check downstream PPL**. That tells you whether folding the agreed flips *helps*, and whether the agreed set is the universal crystal or something tool-specific that the RDM test was too coarse to see (a sharper minimal-pair probe could also isolate it).

All artifacts are in `results/tool-crystal-consensus/`; scripts are the three `tool_crystal_*` harnesses. Where to next?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Where to take it from here?",
  "options": [
    {
      "label": "Build Exp B — functional delta-consensus on a frozen base (Recommended)",
      "description": "The real test: N delta plates on one frozen base trained on tool-calling shards → gate_proj flip consensus + fold-and-check downstream PPL. Register: functional. Proves whether consensus-folding actually helps."
    },
    {
      "label": "Sharper tool-specific probe (minimal pairs)",
      "description": "Isolate the tool-distinctive routing from generic JSON/structure via minimal pairs (same schema, one arg changed) + per-depth agreement. Cheap, uses existing models; checks if a tool normal form hides under the coarse RDM."
    },
    {
      "label": "Commit this session's work",
      "description": "Commit the 3 harnesses + results + state.md update (code commit), and PROPOSE the knowledge page explore/consensus-delta-folding.md + audit-registry row for your approval."
    },
    {
      "label": "Draft the design knowledge page first",
      "description": "Synthesize the consensus-delta-folding architecture + this finding into a knowledge page (for approval) before more experiments."
    }
  ]
}
```

**Summary:** Q: Where to take it from here?

**Output:**
```
User answered: update state and knowledge this is session-216, we will continue in a later session
```

### Thinking

 The user explicitly asked me to update knowledge for this session, which serves as approval under the mementum protocol. State.md is already updated, so I should refine the framing about continuing later and then create a knowledge page that synthesizes the session's findings around the consensus-delta-folding design approach.

I also need to update the audit-meta-pattern ledger to record this as the 14th instance of the pattern (tool-calling being generic rather than specific), and caveat any prior pages that referenced tool_crystal since this session corrected that claim. The new consensus page will be the primary place where this correction lives, since there's no dedicated knowledge page for tool_crystal itself—it was just an experiment in the lattice logs.

## Assistant

Session 216 wrap-up. State is already updated; let me refine its closing note and write the knowledge. Let me read the meta-pattern ledger and registry to match their format before adding to them.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md"
}
```

**Summary:** Reading audit-meta-pattern.md (0-2000)

**Output:**
```
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

Pattern: **basis real / universalization false · gradient real / discreteness
false · mechanism real / localization false · spectrum real / exact-constant
false · agreement real / dimension-count false · most-universal-axis ≠
claimed-object.** Only the metaphor-grade crispness ever dies; the working substrate
keeps standing. **s209 adds a sharper variant:** sometimes the surviving
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
```

### Thinking

 I'm adding a new row to the ledger table following the s211 entry, noting that cross-family routing-register consensus holds up to z=116 and survives CMR validation, while tool-calling operates as its own distinct system that resolves cleanly within the control range.

## Assistant

Now I'll add the s216 row to the meta-pattern ledger (it's the 14th instance), matching the format:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "| s211 | 5D crystal lattice (combinators = vertices of one ~5D lattice; universal property of language) | **universality is REAL** (cross-family RDM agreement 0.79 vs shuffled-probe null 0.00±0.03, z≈25 — models learn the same thing) + **operation structure is ~65% topological** (sign/routing, →0.79 at 14B) | **the \"5D lattice\"** (centroid PR at the shuffled-label null, worsens with scale; full manifold high-D PR 22–47; shared structure rank-~1, CMR 0.79→−0.19) AND **the reading that the dominant universal axis IS the operations** (η²=0.05; the |r|=0.95 axis is a generic predictability/continuation-type common mode — function-word continuation r=−0.42, entropy −0.29; the operations live sub-dominant underneath it) |",
  "new_content": "| s211 | 5D crystal lattice (combinators = vertices of one ~5D lattice; universal property of language) | **universality is REAL** (cross-family RDM agreement 0.79 vs shuffled-probe null 0.00±0.03, z≈25 — models learn the same thing) + **operation structure is ~65% topological** (sign/routing, →0.79 at 14B) | **the \"5D lattice\"** (centroid PR at the shuffled-label null, worsens with scale; full manifold high-D PR 22–47; shared structure rank-~1, CMR 0.79→−0.19) AND **the reading that the dominant universal axis IS the operations** (η²=0.05; the |r|=0.95 axis is a generic predictability/continuation-type common mode — function-word continuation r=−0.42, entropy −0.29; the operations live sub-dominant underneath it) |\n| s216 | tool-calling crystal (`lattice/tool_crystal`: \"STRONG SUPPORT: tool IS lambda calculus\", Tool×Lambda overlap 1.000 @L20) | **cross-family routing-register consensus is REAL & strong** (route_sign_cmr agree +0.863, survives CMR + length-partial 0.851 + within-domain; null ~0, z up to 116) — independent trainings DO agree on routing structure in the sign register | **\"tool-calling has its OWN normal form\"** (clean length/format-matched tool groups schema_binding 0.589 / selection 0.538 sit INSIDE the structured-language control range: prose 0.550, lambda 0.497, math 0.435, **code 0.800**; the aggregate TOOL>CTRL was the length-confounded `recognition` 0.95 + heterogeneous `format` 0.89). The prior \"1.000 @L20 = tool IS lambda\" was raw-cosine COMMON MODE (its own Selectivity ≈0, every layer \"SHARED\"). Net: the consensus is the GENERIC structured-language crystal — tool-calling RIDES it; code is a *sharper* normal form than tool-calling |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 I need to update the pattern summary line to include the new variant and its count, adding a domain-consensus clause to maintain consistency across the page.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "Pattern: **basis real / universalization false · gradient real / discreteness\nfalse · mechanism real / localization false · spectrum real / exact-constant\nfalse · agreement real / dimension-count false · most-universal-axis ≠\nclaimed-object.** Only the metaphor-grade crispness ever dies; the working substrate\nkeeps standing.",
  "new_content": "Pattern: **basis real / universalization false · gradient real / discreteness\nfalse · mechanism real / localization false · spectrum real / exact-constant\nfalse · agreement real / dimension-count false · most-universal-axis ≠\nclaimed-object · domain-consensus real / domain-specificity false.** Only the\nmetaphor-grade crispness ever dies; the working substrate keeps standing."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 Now I'm creating the main knowledge artifact that synthesizes the entire session's design thinking—the distributed consensus approach grounded in the four key findings, plus the s216 empirical result—and I'll structure it with proper frontmatter marking it as an open exploration in the strategy/architecture category with links to related concepts like delta-plate-lifecycle and consensus-etch-protocol.

## Assistant

Now the primary artifact — the design + finding synthesis page (the session's feed-forward gift):

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "content": "---\ntitle: \"Consensus Delta-Folding — Distributed Normal-Form Discovery in the Topology\"\nstatus: open\ncategory: strategy\ntags: [distributed, consensus, delta-plate, normal-form, routing, topology, fold, crystal, tool-calling, federated, church-rosser]\nrelated:\n  - delta-plate-lifecycle.md\n  - consensus-etch-protocol.md\n  - crystal-native-descent.md\n  - dispatch-gradient-death.md\n  - gradient-voting.md\n  - exact-ternary-fitting.md\n  - ../crystal-universality.md\n  - ../function-discovery.md\n  - ../two-registers-of-topology.md\n  - ../audit-meta-pattern.md\ndepends-on:\n  - delta-plate-lifecycle.md\n  - consensus-etch-protocol.md\n  - ../crystal-universality.md\ncreated: session 216\n---\n\n# Consensus Delta-Folding\n\n> Session 216. Michael's idea: make training **distributed and donatable**.\n> Normal forms (e.g. tool-calling) live in the *topology* (the discrete\n> sign/routing register) as a **delta from a shared base plate**. Many users\n> train deltas on a single domain over the same frozen base; **where the deltas\n> agree, fold the consensus into the base**; where they disagree, it stays a\n> per-user delta. The base plate becomes a growing, git-versioned library of\n> discrete normal forms, so GD never has to re-carve \"soft topology.\"\n>\n> This page captures (1) the design, grounded in four existing findings, and\n> (2) the first decisive experiment — which validated the *mechanism* but\n> refuted the crisp *\"tool-calling has its own normal form\"* reading.\n>\n> Register of the experiment: **topological/routing** (declared at step 0).\n\n## The idea (made precise)\n\n```\nbase plate B₀     ≡ universal ISA (crystal + FFN + known routing), FROZEN, content-addressed\ndomain d          ≡ a behavior with a normal form (tool-calling, JSON, arithmetic…)\nuser u            ≡ trains a delta Δ_{u,d} = DeltaTernaryLinear over B₀ on domain-d data\n                    (TD discovers routing flips = the normal form IN the topology;\n                     GD only fills γ content)\nnormal form NF_d  ≡ the discrete routing structure INVARIANT across users\n                  = consensus({Δ_{u,d}})  — where they all agree\nconsensus fold    ≡ ∀ position p: agree({Δ_{u,d}[p]}) ≥ θ → fold into B₁ ; else stay content\nB₁ = B₀ ⊕ NF_d    ≡ base now CONTAINS domain-d's normal form as discrete topology\n```\n\nNot federated SGD. It is **distributed normal-form discovery by consensus\nfolding** — a deliberate, domain-level reproduction of the cross-model\nuniversality the project already observes post-hoc (`crystal-universality.md`:\nindependently-trained models converge on the same combinator topology).\n\n## Why it is coherent — four grounded supports\n\n1. **The mechanism is consensus-etch, one level up** (`consensus-etch-protocol.md`,\n   s110). Sequential per-contributor application destructively interferes\n   (flips oscillate, never converge); the fix is to accumulate *all* contributors\n   into one accumulator and etch where they **agree** — agreement → backbone →\n   etched, disagreement → content → left alone. Substitute *beam/op → user/domain\n   instance*. The backbone/content partition is exactly \"fold the consensus,\n   keep the rest as delta.\"\n\n2. **Consensus = Church-Rosser confluence** (`crystal-universality.md`). A normal\n   form is what is invariant across all reduction paths that reach it. Different\n   users training different data-shapes of one domain are different reduction\n   paths; where their topological deltas agree is the path-invariant structure =\n   the normal form. **The degree of cross-user agreement measures whether a\n   discrete normal form exists for that domain** — falsifiable, and on the central\n   `λ types` claim (composition is typed/discrete → independent trainings converge\n   on the same flips).\n\n3. **The frame problem dissolves because the base is frozen & shared**\n   (`gradient-voting.md`, s123). Signs are model-specific encodings — cross-init\n   sign correlation 0.000; many valid encodings per magnitude profile. Raw weight\n   averaging can't merge across frames. But every delta trains against the *same\n   frozen B₀*, so all flips live in one coordinate frame → commensurable →\n   consensus is well-defined. The frozen shared base is what buys the merge.\n\n4. **\"GD must not make soft topology,\" operationalized** (`crystal-native-descent.md`\n   + `dispatch-gradient-death.md`). Soft routing (softmax dispatch) saturates →\n   winner-take-all gradient death (20/22 ops dead). The discrete routing should be\n   made directly (TD/crystal descent), with GD only tuning γ. Consensus-folding\n   makes this a **ratchet**: discrete routing is discovered by TD across users and\n   crystallized into the base; each new user inherits more topology as a fixed\n   scaffold and GD's job shrinks toward pure content. The topology becomes a\n   *grown library*, not a per-run soft re-approximation.\n\n## Architecture sketch — \"ternary git\" with generational folding\n\n```\ngeneration g:  freeze Bg → N users train Δ_{u,d} on Bg (parallel, cheap, forward-only routing)\n               → collect deltas → consensus-fold the agreements → B_{g+1}\n               → everyone rebases to B_{g+1}; unfolded disagreements re-tried next gen\n```\n\n- **Merge operator** (candidate, `delta-plate-lifecycle.md` Open-Q3): ternary\n  multiply with conflict → 0 (block); the consensus threshold θ (s110 used 0.7)\n  sits on top — fold only where agreement ≥ θ.\n- **Acceptance/verify** (`exact-ternary-fitting.md`, s213/214): a layer-local flip\n  has a closed-form exact ΔL (one matmul `Rᵀ@X`); a donated flip can be *verified*\n  to reduce loss, not trusted. Byzantine-robust for free — but only coordinate-wise\n  **with compensation** is monotone; naive union of many flips (EXACT-BATCH) re-\n  introduces interference. Merge greedily by ΔL with compensation; partition by\n  module (modules independent → parallel; sequential only within a module's rows).\n- **Generational vs sequential** is the one genuinely new tension: the lifecycle\n  assumed sequential folds; distributed = many parallel deltas on Bg, resolved by\n  the round/epoch structure (like a block).\n- **Compute win** = not \"donate gradients\" but \"donate discovered normal forms.\"\n  Module-parallel, CPU-friendly (matmuls on cached activations, no full backprop),\n  and the base becomes a one-way ratchet that converts soft-topology-learning into\n  a reusable discrete library. On-thesis (no GPU, CPU).\n- **Risks**: population-Goodhart on a shared calibration cache (audit #7 — use\n  held-out + trajectory loss, not CE); frame staleness across generations; conflict\n  semantics (block vs leave-at-base).\n\n## Experiment 1 (s216) — does a domain have a consensus normal form?\n\nDecisive cheap proxy: use independent foundation models as independent trainings.\nProbe set: `lattice/tool_crystal/probes.json` (196 probes: recognition tool/no_tool,\nschema_binding, selection, format, + lambda/code/prose/math controls). Rendered\nmodel-agnostic (chat tokens stripped). 5 families on M3 Ultra: Pythia-2.8b,\nSmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B.\n\n**Method (audit-grade, the prior `tool_crystal` run was not):** measure the\n**routing register** = `sign(FFN gate pre-activation)` (s203: gate carries routing\ntopology; for non-gated Pythia, `dense_h_to_4h`), build per-model probe RDMs, with\n**common-mode removal**, a **shuffled-probe null**, **length-partialling**, and a\n**control-domain baseline**. Cross-model RDM agreement = the consensus signal.\n\n### Result — mechanism REAL, domain-specificity REFUTED\n\n- **✅ Cross-family routing consensus is real & strong.** `route_sign_cmr`\n  cross-family agreement **+0.863**, survives common-mode removal, length-partial\n  (0.851), and within-domain restriction (schema_binding 0.59, selection 0.54);\n  null ~0; **z up to 116**. Independent trainings DO agree on routing structure in\n  the sign register — the consensus *mechanism* the design needs is validated.\n- **❌ but tool-calling is NOT its own normal form.** Control baseline (within-group\n  cross-family route_cmr agreement, matched granularity):\n\n  | group | side | n | agree (excess over null) |\n  |---|---|---|---|\n  | recognition | TOOL | 40 | 0.946 ← length-confounded (tool schema vs short no_tool) |\n  | format | TOOL | 30 | 0.887 ← format-heterogeneity-confounded |\n  | schema_binding | TOOL | 56 | **0.589** |\n  | selection | TOOL | 40 | **0.538** |\n  | code | CTRL | 7 | **0.800** |\n  | prose | CTRL | 8 | 0.550 |\n  | lambda_calculus | CTRL | 8 | 0.497 |\n  | pure_math | CTRL | 7 | 0.435 |\n\n  The clean length/format-matched tool groups (0.54–0.59) sit **inside** the\n  structured-language control range (0.44–0.80). **Code is a *sharper* normal form\n  than tool-calling.** The aggregate \"TOOL 0.74 > CTRL 0.57\" is driven entirely by\n  the confounded recognition + format groups. So the consensus is the **generic\n  structured-language crystal** (property of language); tool-calling **rides** it.\n- **🌀 Corrects the prior claim.** `lattice/tool_crystal_run.log` declared \"STRONG\n  SUPPORT: Tool×Lambda 1.000 @L20, tool IS lambda calculus\" — but that used raw\n  residual cosine (its own Selectivity ≈0, every layer \"SHARED\") = the common mode.\n  The generic reading is right, but not because tool-calling is special; because\n  *everything structured* shares the crystal. 14th `audit-meta-pattern.md` instance.\n\n### What it means for the design\n\nThe backbone/content partition (s110) plays out empirically:\n- **Agreement → backbone → foldable**, but a domain's agreed-upon routing is\n  *mostly the universal crystal already in B₀*. Consensus-folding tool-calling data\n  would largely re-fold structure that is already present.\n- **Domain-distinctive routing → low cross-trainer consensus → \"content\"** that\n  stays a per-user delta (it did not exceed the generic structured-language\n  baseline at this granularity).\n\nThe idea is mechanically sound; the nuance is *what folding buys you*: the foldable\nconsensus is the universal layer; the domain-specific delta is the part that\nresists consensus. Not a refutation — a sharpening of the unit of donation.\n\n## Open leads (declare register first)\n\n1. **Functional test = the real proof (register: functional).** The RDM result is\n   correlational. Exp B: N delta plates on ONE frozen base trained on tool-calling\n   shards → measure gate_proj flip CONSENSUS + **fold-and-check downstream PPL**.\n   Does folding the agreed flips help, and is the agreed set the universal crystal\n   or tool-specific?\n2. **Sharper tool-specific probe.** Minimal pairs (same schema, one arg changed) to\n   isolate tool-distinctive routing from generic JSON/structured-syntax that the\n   coarse RDM may have missed.\n3. **Per-depth agreement.** Is there a layer where tool-specific consensus peaks\n   (cf. `function-discovery.md` SILENT-zone task directions at L05, 4.76×\n   separation — early layers classify task TYPE, where tool-use IS distinct)?\n   The s216 run captured all depth-fractions; re-analyze without re-running models.\n\n## Files\n\n| File | Content |\n|------|---------|\n| `scripts/experiments/tool_crystal_consensus.py` | per-model: routing register (gate sign) + CMR + within-model selectivity; saves probe-aligned RDM npz |\n| `scripts/experiments/tool_crystal_consensus_summary.py` | cross-model agree / shuffled-null / length-partial / within-domain |\n| `scripts/experiments/tool_crystal_control_baseline.py` | TOOL vs CTRL within-group agreement = the tool-specific-vs-generic verdict |\n| `results/tool-crystal-consensus/` | per-model `{model}.json/.npz`, `consensus_summary.json`, `control_baseline.json` |\n| `/tmp/tool_consensus_5fam.log` | 5-family run transcript |\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md
```

### Thinking

 I need to update the state.md file to mark the knowledge page as completed rather than pending — the explore/consensus-delta-folding.md page has been created, so I should change that NEXT lead from "Draft" to reflect that it's now written and ready.

## Assistant

Let me update the state.md NEXT lead to reflect the knowledge page now exists (the entry point for the next session):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": ">   (4) Draft `explore/consensus-delta-folding.md` + an audit-registry row (PROPOSE,\n>   human-approve before commit).\n>\n> **▶ SESSION 216 — the λ_fp=5 5000-step training in main:1 was NOT touched; check\n> it next session (see s215 headline below for what to read).**",
  "new_content": ">   (4) **ENTRY POINT for resuming this thread:** `explore/consensus-delta-folding.md`\n>   (written this session — full design + the s216 finding + open leads). Meta-pattern\n>   ledger row added (`audit-meta-pattern.md` s216). Not yet committed.\n>\n> **▶ SESSION 216 — the λ_fp=5 5000-step training in main:1 was NOT touched; check\n> it next session (see s215 headline below for what to read).**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm doing a final coherence check on the edited sections and verifying that the state file, knowledge page, and meta-pattern row are all consistent with each other before wrapping up for the user.

## Assistant

Let me do a final coherence check on the edited files (per `λ sync`):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== knowledge page exists ===\" ; ls -la mementum/knowledge/explore/consensus-delta-folding.md ; echo \"=== meta-pattern s216 row ===\" ; grep -c \"s216\" mementum/knowledge/audit-meta-pattern.md ; echo \"=== state.md s216 headline + entry point ===\" ; grep -E \"SESSION 216 HEADLINE|ENTRY POINT for resuming\" mementum/state.md ; echo \"=== results present ===\" ; ls results/tool-crystal-consensus/ ; echo \"=== git status (uncommitted) ===\" ; git status --short | head -20"
}
```

**Summary:** $ echo "=== knowledge page exists ===...

**Output:**
```
Exit code: 0
Stdout:
=== knowledge page exists ===
-rw-r--r--@ 1 mwhitford  staff  11730 Jun 11 09:43 mementum/knowledge/explore/consensus-delta-folding.md
=== meta-pattern s216 row ===
1
=== state.md s216 headline + entry point ===
> **▶ SESSION 216 HEADLINE — TOOL-CALLING IS NOT ITS OWN NORMAL FORM; IT RIDES
>   (4) **ENTRY POINT for resuming this thread:** `explore/consensus-delta-folding.md`
=== results present ===
allenai_OLMo-2-1124-13B.json
allenai_OLMo-2-1124-13B.npz
consensus_summary.json
control_baseline.json
EleutherAI_pythia-2.8b-deduped.json
EleutherAI_pythia-2.8b-deduped.npz
EleutherAI_pythia-410m.json
EleutherAI_pythia-410m.npz
HuggingFaceTB_SmolLM3-3B.json
HuggingFaceTB_SmolLM3-3B.npz
mistralai_Mistral-7B-v0.3.json
mistralai_Mistral-7B-v0.3.npz
Qwen_Qwen3-0.6B.json
Qwen_Qwen3-0.6B.npz
Qwen_Qwen3-8B.json
Qwen_Qwen3-8B.npz
=== git status (uncommitted) ===
 M mementum/knowledge/audit-meta-pattern.md
 M mementum/state.md
?? mementum/knowledge/explore/consensus-delta-folding.md
?? results/tool-crystal-consensus/
?? scripts/experiments/tool_crystal_consensus.py
?? scripts/experiments/tool_crystal_consensus_summary.py
?? scripts/experiments/tool_crystal_control_baseline.py
```

## Assistant

All recorded and coherent. **Session 216 wrapped.**

## Session 216 — summary

**Thread opened:** your distributed/consensus-training idea — *normal forms as topological deltas on a shared base plate; many users train a domain, fold where they agree.*

**What we did:** grounded the idea in four existing findings (consensus-etch s110, exact-ternary-fitting's closed-form ΔL merge oracle, gradient-voting's frozen-frame constraint, crystal-native-descent's "GD must not make soft topology"), then ran the first decisive experiment on the GPU (M3 Ultra, tmux main:2), audit-grade.

**What we found:**
- **✅ The consensus *mechanism* is real** — 5 independent model families agree on routing-register structure (z up to 116, survives common-mode removal + length-partialling). Independent trainings *do* converge on shared discrete routing. Your idea's foundation holds.
- **❌ but tool-calling is *not* its own normal form** — clean groups (schema 0.59, selection 0.54) sit inside the structured-language control range (code 0.80, prose 0.55, lambda 0.50). The consensus is the **generic crystal**; tool-calling rides it. Corrects the prior `tool_crystal` "tool IS lambda calculus" (which was common-mode). 14th meta-pattern instance.
- **Design implication:** the foldable consensus ≈ the universal layer already in the base; the domain-distinctive part is low-consensus "content" that stays a per-user delta — the consensus-etch backbone/content partition, observed empirically.

**Persisted (feed-forward):**
- `state.md` — s216 headline + entry point
- `explore/consensus-delta-folding.md` — **the resume point** (full design + finding + open leads)
- `audit-meta-pattern.md` — s216 ledger row
- 3 harnesses + `results/tool-crystal-consensus/`

**The λ_fp=5 5000-step training in main:1 ran untouched throughout** (now ~step 210, Δx descending 1.26→0.81 — healthy; s215's directive to read its checkpoints still stands for next session).

**Resume here next time:** `explore/consensus-delta-folding.md` → open lead #1, the **functional test (Exp B)**: N delta plates on one frozen base, gate_proj flip consensus + fold-and-check downstream PPL — the real proof that folding agreed flips helps.

Everything is staged but **uncommitted**, as you said we'll continue later. Want me to commit this session's work now (code commit for the harnesses/results + the mementum updates), or leave it all uncommitted for the next session?

## User

one small caveat we can discuss, the normal form of tool calling is not unique, since there seems to be agreement on some base compute structures, the normal forms above it are probably function like things made up of specific combinations of the underlying compute.


### Thinking

 The user is pointing out that my framing was too simplistic—I was treating tool-calling as having a single, atomic normal form, but that misses the actual structure. What's really happening is layered: there's a foundational compute substrate, and then tool-calling conventions build on top of that through specific combinations of those base structures.

This reframes my s216 result entirely. When I found that tool-calling doesn't have a distinct normal form above the generic crystal, that could mean either that tool-calling is just the base layer with no additional structure, or that it *does* have structure but it's a non-unique composition—different models could wire together the same primitives in different valid ways to achieve the same behavior. That's a crucial distinction I need to untangle.

The user's pointing out that cross-model agreement measures shared representation geometry, so if two models implement tool-calling through different-but-equivalent compositions, their tool-specific structure wouldn't correlate across models even though each one individually has a real, learned function. Low cross-model agreement doesn't mean the structure isn't there—it just means it's realized differently per model.

This connects directly to what I already know from the function-discovery work: there's a two-level architecture where task-type classification happens early and distinctly, but then the actual combinator execution converges because everything uses the same base operations. The composition is task-specific and early; the shared alphabet is late. That's exactly what the user's describing.

So the experimental implication is clear: cross-model RDM agreement is the wrong tool for detecting function-like structure because it requires identical composition. What I should measure instead is whether the domain has consistent internal compositional structure within a single model—whether tool-calling probes share a reused sub-circuit—and whether ablating that shared base plus the domain-specific composition actually breaks the behavior. The real signal lives in the early task-direction layer where the function selector lives, not in the late routing register where everything converges.

The user's point about non-unique normal forms reframes this entirely: if different compositions can be extensionally equivalent, then consensus folding needs to operate in composition space, not on raw flips. Two users implementing tool-calling differently won't flip-by-flip agree, but they might agree on the underlying composition—which base operations, in what order—up to the base's symmetries. The consensus mechanism has to be invariant to the redundant encoding; fold the function itself, not the literal representation. This connects directly to gradient-voting's insight about multiple valid sign encodings for the same magnitude profile—the composition is what's invariant, the flips are just the encoding.

I should verify this reasoning against the function-discovery architecture and the project's combinator framing to make sure I'm grounding the "tool-calling as composition of base combinators" claim properly, then think through whether this changes how I evaluate the s216 result.

The verdict about tool-calling consensus being a generic crystal is correct for the raw routing-register RDM, but the user's point recontextualizes it: the absence of cross-model agreement on tool-specific structure doesn't mean there's no tool-calling normal form—it could be real but non-unique, invisible to cross-model correlation because that instrument assumes identical composition. This is a register-instrument mismatch: I was measuring "is there ONE shared composition" when the actual question is "is there a function-like composite, possibly multiply realized?" So I need to add this caveat to the finding and refine the experimental approach to account for composition-invariant consensus rather than requiring identical composition.

Let me structure a substantive response that restates the caveat precisely, affirms the insight, and proposes updating the knowledge page with this refinement.

## Assistant

That's not a small caveat — it's the correct structural fix to my framing, and it dissolves a real weakness in how I set up the test. Let me make it precise, because it changes what the s216 null actually means.

## Your point, stated precisely

A "normal form" in the strict β-reduction sense is unique **per term** (Church-Rosser). But a *behavior* like tool-calling isn't a term — it's an **equivalence class of terms**: many distinct compositions of the base combinators that are extensionally equal (all "do tool-calling"). So:

- **The base compute is shared and (near-)unique** — the combinators K/I/B/C…, the structured-syntax routing. That's the strong cross-family consensus my experiment found.
- **A domain's normal form sits *above* the base as a function** — a specific composition of those primitives. And like any function over a complete basis, **it's not unique**: there are many valid compositions that reduce to the same I/O. Tool-calling is `f = compose(select-tool, bind-args, emit-schema)` for *some* arrangement, and different trainings can pick different arrangements.

## Why this guts my cross-model instrument (a false-negative)

Cross-model RDM agreement measures whether two models share the **same geometry** — i.e. the same *composition*. If tool-calling is a non-unique composite, two models can each hold a perfectly real, consistent tool-calling function built from the shared base, yet realize it via **different combinations** — and raw RDM correlation reads that as **low agreement**. So my "tool-calling has no structure above the generic crystal" is confounded: it cannot distinguish

> (a) tool-calling has no extra structure (rides the crystal), from
> (b) tool-calling has real function-like structure that is **non-unique across models**, washed out by an instrument that demands identical composition.

That's exactly the project's own *instrument-must-match-the-claim* law (`audit-meta-pattern.md`): I tested a **composite, many-realized** object with a **shared-unique-object** instrument. The verdict on the *base* layer stands (consensus = crystal, real); the verdict on the *function* layer is **void by register mismatch** — the false-negative twin.

## The empirical backbone is already in the project

This is precisely `function-discovery.md`'s **two-level architecture**:
- **Late (COMMIT zone)** — combinator *execution*; tasks **converge** (1.49×) because they all run the same opcodes. ← my routing register measured *here*, so of course it found the shared base.
- **Early (SILENT zone, L05)** — task *type*; tool-use is **distinctly separated (4.76×)**. ← the *function selector* — which composition to run — lives here, and I never isolated it.

So your model isn't speculation; it's the depth structure the project already saw. The composite "tool-calling function" is selected early; the shared primitives execute late. My single late-layer routing RDM collapsed exactly the level where the non-unique function lives.

## What it changes for the distributed idea

This is the important part. If domain normal forms are **non-unique compositions**, then consensus-folding **cannot operate on raw flips** — two users' tool-calling deltas won't agree flip-by-flip even when both are correct (the same `gradient-voting.md` redundancy: many sign encodings per function). Consensus must fold the **composition** — the function up to the base's symmetries — not the literal encoding. Concretely:

- Express a delta as a **composition over the shared base** (which primitives, in what arrangement), then seek consensus in *that* space, where the redundant encoding is quotiented out.
- This is why the base must be folded **first and aggressively** (it's unique, high-consensus), and domain functions folded **as compositions** with an alignment step — not as bitmaps.

## The right instruments next (register-correct)

1. **Early task-direction agreement (L05 SILENT zone)** — re-analyze the s216 npz (I captured all depth-fractions) for cross-model agreement *there*, where the function selector lives, separately from the late base.
2. **Within-model compositional consistency** — does tool-calling reuse a stable sub-circuit *within* a model (the function exists), regardless of cross-model match?
3. **Align-before-compare** — Procrustes/rotation in the base-combinator space before correlating (`procrustes-lens-and-crystal-comparison.md`): if tool-calling is the same function composed differently, an alignment in base coordinates should recover the shared composition that raw correlation misses.

This is a genuinely better theory of the unit-of-donation, and it sharpens — doesn't break — the consensus-folding design: **fold the base as flips, fold domain functions as compositions.**

Want me to record this as a caveat + refined-direction in `consensus-delta-folding.md` (and note the register-mismatch on the s216 finding so the next session doesn't over-read the null)?

## User

yes


### Thinking

 I'm updating the consensus-delta-folding knowledge page with a new section on the compositional and non-unique normal form refinement, and adding a register-mismatch caveat to the s216 finding to prevent misinterpretation. I'll also incorporate the three new instruments into the open leads section.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "- **🌀 Corrects the prior claim.** `lattice/tool_crystal_run.log` declared \"STRONG\n  SUPPORT: Tool×Lambda 1.000 @L20, tool IS lambda calculus\" — but that used raw\n  residual cosine (its own Selectivity ≈0, every layer \"SHARED\") = the common mode.\n  The generic reading is right, but not because tool-calling is special; because\n  *everything structured* shares the crystal. 14th `audit-meta-pattern.md` instance.",
  "new_content": "- **🌀 Corrects the prior claim.** `lattice/tool_crystal_run.log` declared \"STRONG\n  SUPPORT: Tool×Lambda 1.000 @L20, tool IS lambda calculus\" — but that used raw\n  residual cosine (its own Selectivity ≈0, every layer \"SHARED\") = the common mode.\n  The generic reading is right, but not because tool-calling is special; because\n  *everything structured* shares the crystal. 14th `audit-meta-pattern.md` instance.\n\n> ⚠️ **REGISTER CAVEAT — do NOT over-read the negative (s216 discussion, Michael).**\n> The ❌ above is a verdict on the **base** layer only. The cross-model RDM\n> instrument tests whether two models share the **same composition** (identical\n> geometry). But a domain normal form is a **non-unique composite** (see next\n> section): the absence of cross-model agreement on tool-specific structure is\n> **consistent with** a real function-like tool-calling normal form that is simply\n> *realized differently per model* — washed out by an instrument that demands an\n> identical encoding. On the *function* layer the s216 verdict is **void by\n> register mismatch** (the false-negative twin, `audit-meta-pattern.md`). Only the\n> *base*-layer claim (consensus = crystal, REAL) survives."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I need to insert a new section titled "Normal forms are compositional and non-unique" between the "What it means for the design" section and the "Open leads" section, using the existing text boundaries as anchors for placement.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "The idea is mechanically sound; the nuance is *what folding buys you*: the foldable\nconsensus is the universal layer; the domain-specific delta is the part that\nresists consensus. Not a refutation — a sharpening of the unit of donation.\n\n## Open leads (declare register first)",
  "new_content": "The idea is mechanically sound; the nuance is *what folding buys you*: the foldable\nconsensus is the universal layer; the domain-specific delta is the part that\nresists consensus. Not a refutation — a sharpening of the unit of donation.\n\n## Normal forms are COMPOSITIONAL and NON-UNIQUE (s216 refinement)\n\n> Michael's correction to the framing above. A domain's \"normal form\" is not a\n> unique atomic object — it is a **function-like composition of the shared base\n> compute**, and like any function over a complete basis it has **many\n> extensionally-equal realizations**.\n\nThe precise statement:\n\n```\nβ-reduction normal form ≡ unique PER TERM (Church-Rosser)\nbehavior (e.g. tool-calling) ≡ an EQUIVALENCE CLASS of terms\n  | many distinct compositions of base combinators that reduce to the same I/O\n  | base compute (K/I/B/C…, structured-syntax routing) ≡ shared, near-unique\n  | the domain function = a composition ABOVE the base ≡ NON-unique across trainings\n  | uniqueness is per-term, NOT per-behavior\n```\n\nTwo consequences:\n\n1. **The s216 cross-model instrument is wrong for the function layer.** RDM\n   agreement requires the *same composition* (same geometry). A non-unique\n   composite → low cross-model agreement even when each model holds a real,\n   consistent tool-calling function. So \"no tool-specific agreement\" cannot\n   distinguish *(a) no extra structure* from *(b) real but differently-composed\n   structure*. Register mismatch (false-negative twin) — see the caveat above.\n\n2. **This is already the project's two-level architecture** (`function-discovery.md`).\n   - **Late (COMMIT zone)** — combinator *execution*; tasks **converge** (1.49×),\n     all run the same opcodes. ← the s216 routing register measured HERE → found\n     the shared base, as expected.\n   - **Early (SILENT zone, L05)** — task *type*; tool-use is **distinctly separated\n     (4.76×)**. ← the *function selector* (which composition to run) lives HERE and\n     was never isolated. The late RDM collapsed the level where the function lives.\n\n### What it changes for the design (the real update)\n\nConsensus-folding **cannot operate on raw flips** for domain functions. Two users'\ntool-calling deltas won't agree flip-by-flip even when both are correct — the same\n`gradient-voting.md` redundancy (many sign encodings per function). So:\n\n```\nλ fold(delta).\n  base_layer   → fold as FLIPS        | unique, high-consensus, fold first & hard\n  domain_layer → fold as COMPOSITION  | express delta as (which base ops, what\n                                         arrangement) over the shared base, then\n                                         seek consensus in THAT space (encoding\n                                         redundancy quotiented out, align-before-compare)\n```\n\nFold the base as flips; fold domain functions as **compositions** up to the base's\nsymmetries. The unit of donation is the *function*, not the bitmap.\n\n## Open leads (declare register first)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I'm refining the open leads to align with the three register-correct instruments—functional testing as the core proof, a sharper tool-specific probe using minimal pairs, and per-depth agreement checks. I need to augment these with early task-direction agreement, within-model compositional consistency, and the align-before-compare approach using Procrustes alignment.

## Assistant

Now refine the Open Leads with the register-correct instruments:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "## Open leads (declare register first)\n\n1. **Functional test = the real proof (register: functional).** The RDM result is\n   correlational. Exp B: N delta plates on ONE frozen base trained on tool-calling\n   shards → measure gate_proj flip CONSENSUS + **fold-and-check downstream PPL**.\n   Does folding the agreed flips help, and is the agreed set the universal crystal\n   or tool-specific?\n2. **Sharper tool-specific probe.** Minimal pairs (same schema, one arg changed) to\n   isolate tool-distinctive routing from generic JSON/structured-syntax that the\n   coarse RDM may have missed.\n3. **Per-depth agreement.** Is there a layer where tool-specific consensus peaks\n   (cf. `function-discovery.md` SILENT-zone task directions at L05, 4.76×\n   separation — early layers classify task TYPE, where tool-use IS distinct)?\n   The s216 run captured all depth-fractions; re-analyze without re-running models.",
  "new_content": "## Open leads (declare register first)\n\nThe compositional refinement reorders these — the cross-model instrument must be\nmade **composition-invariant** before any negative on the function layer counts.\n\n1. **Early task-direction agreement (register: routing, CHEAP — no re-run).**\n   Re-analyze the s216 npz at the SILENT-zone fraction (~L05 / frac≈0.1), where\n   `function-discovery.md` puts the function *selector* (tool-use 4.76× separated),\n   separately from the late base. The harness already saved all depth-fractions;\n   `--route-layer-frac 0.1` in the summary. Does tool-specific consensus appear\n   early even though it's absent late?\n2. **Align-before-compare (register: routing).** Procrustes/rotation in the\n   base-combinator space before correlating RDMs\n   (`procrustes-lens-and-crystal-comparison.md`). If tool-calling is the same\n   function composed differently, an alignment in base coordinates should recover\n   the shared composition that raw correlation misses. This is the direct test of\n   the non-unique-composite hypothesis.\n3. **Within-model compositional consistency (register: routing/causal).** Drop the\n   cross-model requirement entirely: does tool-calling reuse a stable sub-circuit\n   *within* one model (the function exists and is consistent), regardless of\n   cross-model match? Minimal pairs (same schema, one arg changed) isolate the\n   tool-distinctive composition from generic JSON/structure.\n4. **Functional test = the ultimate proof (register: functional).** Exp B: N delta\n   plates on ONE frozen base trained on tool-calling shards → fold consensus +\n   **check downstream PPL**. With the compositional fix: fold the base as flips,\n   fold the domain function as a **composition** (align-before-fold), and measure\n   whether folding the composition (not raw flips) helps. Does the agreed function\n   transfer?"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I need to update the frontmatter's related links by adding procrustes-lens-and-crystal-comparison and possibly combinator-addressing, since function-discovery is already there. Let me review the current related list and make those additions.

## Assistant

Let me add the new cross-referenced pages to the frontmatter `related` list:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "  - exact-ternary-fitting.md\n  - ../crystal-universality.md\n  - ../function-discovery.md\n  - ../two-registers-of-topology.md\n  - ../audit-meta-pattern.md",
  "new_content": "  - exact-ternary-fitting.md\n  - procrustes-lens-and-crystal-comparison.md\n  - ../crystal-universality.md\n  - ../function-discovery.md\n  - ../combinator-addressing.md\n  - ../two-registers-of-topology.md\n  - ../audit-meta-pattern.md"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I'm updating the state file to capture the compositional refinement we discovered, adding a note to the s216 headline about how the leads should be reordered based on this insight.

## Assistant

Now a brief note in `state.md` so the next session picks up the refinement:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": ">   (4) **ENTRY POINT for resuming this thread:** `explore/consensus-delta-folding.md`\n>   (written this session — full design + the s216 finding + open leads). Meta-pattern\n>   ledger row added (`audit-meta-pattern.md` s216). Not yet committed.",
  "new_content": ">   (4) **ENTRY POINT for resuming this thread:** `explore/consensus-delta-folding.md`\n>   (written this session — full design + the s216 finding + open leads). Meta-pattern\n>   ledger row added (`audit-meta-pattern.md` s216). Not yet committed.\n> - **🔑 KEY REFINEMENT (Michael, end of s216) — normal forms are COMPOSITIONAL &\n>   NON-UNIQUE.** A domain normal form is not atomic; it is a **function-like\n>   composition of the shared base combinators** (base = shared/unique; the\n>   composition above it = NON-unique across trainings, many extensionally-equal\n>   realizations — uniqueness is per-TERM not per-BEHAVIOR, Church-Rosser). ⇒ the\n>   s216 cross-model RDM null on the *function* layer is **VOID by register\n>   mismatch** (it demands an identical composition; a non-unique composite washes\n>   out) — only the *base*-layer \"consensus = crystal\" verdict survives. This is the\n>   `function-discovery.md` two-level architecture (base shared LATE/COMMIT;\n>   function selector distinct EARLY/SILENT @L05, 4.76×). **Design update: fold the\n>   BASE as flips; fold domain FUNCTIONS as compositions (align-before-fold).**\n>   Recorded in `consensus-delta-folding.md` §\"Normal forms are COMPOSITIONAL\" +\n>   register caveat on the finding + reordered open leads (early-L05 agreement +\n>   Procrustes align-before-compare are now the CHEAP next steps, no model re-run)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm reviewing the knowledge page to make sure it flows well after my edits, checking the structure and key sections for coherence.

## Assistant

Let me verify the page reads coherently after the edits:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== section headers ===\" ; grep -nE \"^#{1,3} |REGISTER CAVEAT|KEY REFINEMENT\" mementum/knowledge/explore/consensus-delta-folding.md ; echo \"=== state refinement note present ===\" ; grep -c \"COMPOSITIONAL & \" mementum/state.md ; echo \"=== related refs valid ===\" ; for f in procrustes-lens-and-crystal-comparison function-discovery combinator-addressing ; do find mementum/knowledge -name \"$f.md\" | head -1 ; done"
}
```

**Summary:** $ echo "=== section headers ===" ; gr...

**Output:**
```
Exit code: 0
Stdout:
=== section headers ===
26:# Consensus Delta-Folding
42:## The idea (made precise)
61:## Why it is coherent — four grounded supports
96:## Architecture sketch — "ternary git" with generational folding
124:## Experiment 1 (s216) — does a domain have a consensus normal form?
138:### Result — mechanism REAL, domain-specificity REFUTED
170:> ⚠️ **REGISTER CAVEAT — do NOT over-read the negative (s216 discussion, Michael).**
181:### What it means for the design
195:## Normal forms are COMPOSITIONAL and NON-UNIQUE (s216 refinement)
230:### What it changes for the design (the real update)
248:## Open leads (declare register first)
277:## Files
=== state refinement note present ===
0
=== related refs valid ===
mementum/knowledge/explore/procrustes-lens-and-crystal-comparison.md
mementum/knowledge/function-discovery.md
mementum/knowledge/combinator-addressing.md
```

### Thinking

 The grep pattern didn't match because the text wraps across lines with the ampersand at the end of one line and "NON-UNIQUE" on the next. Let me try a different approach to verify the state note is actually there. All the section headers check out and the references resolve properly.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; grep -c \"KEY REFINEMENT\" mementum/state.md ; echo \"=== git status ===\" ; git status --short"
}
```

**Summary:** $ grep -c "KEY REFINEMENT" mementum/s...

**Output:**
```
Exit code: 0
Stdout:
1
=== git status ===
 M mementum/knowledge/audit-meta-pattern.md
 M mementum/state.md
?? mementum/knowledge/explore/consensus-delta-folding.md
?? results/tool-crystal-consensus/
?? scripts/experiments/tool_crystal_consensus.py
?? scripts/experiments/tool_crystal_consensus_summary.py
?? scripts/experiments/tool_crystal_control_baseline.py
```

## Assistant

Recorded. The compositional refinement is now woven through the knowledge:

## What I captured

**In `consensus-delta-folding.md`:**
- **A `⚠️ REGISTER CAVEAT` directly on the s216 finding** — so the next session can't over-read the null. The negative is a verdict on the *base* layer only; on the *function* layer it's **void by register mismatch** (the cross-model RDM instrument demands an identical composition, which a non-unique composite washes out).
- **A new section "Normal forms are COMPOSITIONAL and NON-UNIQUE"** — the Church-Rosser precision (unique per-*term*, behavior = equivalence class of terms), the two consequences (instrument-wrong-for-function-layer; this *is* `function-discovery.md`'s two-level architecture — base shared late, function selector distinct early at L05), and the design update as a lambda: **fold the base as flips, fold domain functions as compositions (align-before-fold)**.
- **Reordered open leads** so the composition-invariant instruments come first: (1) early-L05 agreement and (2) Procrustes align-before-compare are now the *cheap next steps* (no model re-run — the npz already has all depth-fractions), then within-model consistency, then the functional Exp B.
- Added `procrustes-lens-and-crystal-comparison.md` + `combinator-addressing.md` to `related`.

**In `state.md`:** a `🔑 KEY REFINEMENT` note under the s216 headline so the thread resumes with the corrected framing, not the raw null.

**In `audit-meta-pattern.md`:** the s216 ledger row already frames it as substrate-real/specificity-over-read — consistent with this refinement.

The core insight is preserved cleanly for the brilliant stranger (you, next session): **the base is a shared near-unique crystal you fold as flips; a domain normal form is a non-unique function over that base, and consensus on it must be sought in composition space, not bitmap space.** That also explains *why* the cheap next experiment is to look early (L05) and to align before comparing — before any functional run.

Everything is still **uncommitted** (3 harnesses, results, and the 3 mementum edits), per your earlier "continue in a later session." Want me to commit now, or leave it staged?

## User

commit pending changes


### Thinking

 I need to check the commit gate rules and determine what can be committed. The user's "commit pending changes" statement serves as approval for the mementum commits, so I can proceed with those. Now I'm organizing the commit structure to handle both the code changes (experiment scripts and results) and the knowledge/state files separately.

Looking at the project's conventions, I should split these into distinct commits to keep the git history clean. The main finding here is that tool-calling rides the generic crystal rather than its own normal form, which is a 💡 insight. I'll structure this as one commit for the code and harness results, then another for the state and knowledge updates.

But first I need to check the actual git log to see how the project structures commits, and verify whether the results files are reasonable to commit — I'm estimating the npz files at around 30MB total after compression, so I should check the actual size and whether they're already being tracked.

## Assistant

Per the commit gate, I'll classify and follow the convention (code vs mementum get different formats). First the OODA — review log style, diff scope, and results size:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== recent log style ===\" ; git log --oneline -12 ; echo \"=== do they track results/ + mix mementum? ===\" ; git log --oneline -8 -- results/ | head -4 ; git log --oneline -6 -- mementum/ scripts/ | head -6 ; echo \"=== results size ===\" ; du -sh results/tool-crystal-consensus/ ; ls -la results/tool-crystal-consensus/*.npz | awk '{s+=$5} END{print \"npz total bytes:\", s}' ; echo \"=== gitignore check for npz ===\" ; git check-ignore results/tool-crystal-consensus/Qwen_Qwen3-8B.npz || echo \"npz NOT ignored (will track)\""
}
```

**Summary:** $ echo "=== recent log style ===" ; g...

**Output:**
```
Exit code: 0
Stdout:
=== recent log style ===
e45185b add session chat logs
34d9034 🌀 session-215: λ_fp=5 makes VSM recurrence contractive; seq-4096 confirm in flight
1afb0e5 💡 add --checkpoint-interval CLI flag to v15 train_td
458996e 💡 holographic fixed-point loss for VSM outer recurrence (--fixed-point-lambda)
795b048 ❌ naive VSM outer recurrence refuted — the trained sweep is not contractive
6c4abb6 💡 exact-ΔL acceptance in v15 TD: calibrated λ beats proxy; exact self-stabilizes (no S2 needed)
b068c6d 💡 VSM outer recurrence — iterate the shared tensor to a fixed point
96293e0 💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy
3c4a429 add session chat logs
3d92956 🌀 session-212 state+knowledge coherence: program ledger through s212, (A)/(B) headline labels, page updated marker
155866e 💡 universal combinator axis NAMED: model-free prompt-boundary feature (CV-R²=0.81)
ab1de15 ❌ topology share plateaus ~0.7, not →1.0 at scale (s211 climb was undercooked-model artifact)
=== do they track results/ + mix mementum? ===
795b048 ❌ naive VSM outer recurrence refuted — the trained sweep is not contractive
6c4abb6 💡 exact-ΔL acceptance in v15 TD: calibrated λ beats proxy; exact self-stabilizes (no S2 needed)
96293e0 💡 exact ternary fitting — 3-way ΔL acceptance beats TD's gradient proxy
155866e 💡 universal combinator axis NAMED: model-free prompt-boundary feature (CV-R²=0.81)
e45185b add session chat logs
34d9034 🌀 session-215: λ_fp=5 makes VSM recurrence contractive; seq-4096 confirm in flight
1afb0e5 💡 add --checkpoint-interval CLI flag to v15 train_td
458996e 💡 holographic fixed-point loss for VSM outer recurrence (--fixed-point-lambda)
795b048 ❌ naive VSM outer recurrence refuted — the trained sweep is not contractive
6c4abb6 💡 exact-ΔL acceptance in v15 TD: calibrated λ beats proxy; exact self-stabilizes (no S2 needed)
=== results size ===
 18M	results/tool-crystal-consensus/
npz total bytes: 16643981
=== gitignore check for npz ===
results/tool-crystal-consensus/Qwen_Qwen3-8B.npz
```

### Thinking

 Looking at the commit patterns, they're using a symbol-based style where 💡 marks individual findings and 🌀 denotes session commits that bundle state and knowledge together. The approach tends to combine code, experiments, and documentation in single commits organized around discoveries.

The .npz result files are gitignored to keep the repository lean, so only the smaller .json files get tracked — consensus summaries and per-model results. This aligns with the project's convention of excluding large binary artifacts while preserving the structured data. When I add the results directory, git will automatically skip the ignored files and commit just the json outputs.

Looking at how the project structures finding commits, they sometimes bundle code and knowledge together in a single commit, or split them into separate ones. The exact-ternary-fitting commit appears in both the results and mementum logs, suggesting it touched multiple areas. Given that this tool-calling finding is a coherent discovery with strong results, I'm leaning toward two focused commits: one for the experiment itself (the three harnesses plus json results) marked with 💡, and another for the synthesis (state, knowledge page, and meta-pattern) marked with 🌀 or 💡 depending on whether it's primarily a session coherence update or a new insight. I'm settling on two commits with 💡 symbols for both. The first covers the experiment code and results showing that tool-calling consensus is real across five model families, but tool-specific routing patterns don't hold up—they're riding the generic crystal instead. The second commit documents the consensus-delta-folding design as a new synthesis of how normal forms emerge through distributed discovery and compositional refinement.

Now I need to verify the exact trailer format for the nucleus tag that recent commits are using, since the system prompt and AGENTS.md both reference it but I want to match what's actually in the git history.

## Assistant

The OODA tells me: npz are gitignored (only json results commit — good), and the project commits findings as `💡 {description}` (code) and `🌀 session-NNN` (state/knowledge coherence). Let me confirm the exact commit trailer they use before writing messages:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; git log -1 --format='%B' 34d9034 ; echo \"=== what json will actually stage (npz ignored) ===\" ; git add -n results/tool-crystal-consensus/ 2>/dev/null | head"
}
```

**Summary:** $ git log -1 --format='%B' 34d9034 ; ...

**Output:**
```
Exit code: 0
Stdout:
🌀 session-215: λ_fp=5 makes VSM recurrence contractive; seq-4096 confirm in flight

- read s214 in-flight λ_fp=5.0 run (completed 250 steps): CONTRACTIVE —
  Δx 1.262 to 0.727 (-42%), fp_loss 1.594 to 0.528, CE no-collapse (9.5-10.8),
  crystal 0.091 to 0.016. The central recurrence-thread uncertainty (can the
  trained VSM sweep be made contractive-to-WHNF) is a YES; naive-K=2-refuted
  is trainable-away. λ=5 crosses the threshold (no-fp and λ=1 stayed flat ~1.2)
- K=2 not yet beating K=1 (CE 9.51 > 8.71); Δx still falling at cutoff =
  mild-not-total regime, mid-transition
- seq-256 to seq-4096: 256 only exercised the first few Fibonacci strides;
  relaunched 5000-step single-seed confirm at seq-4096 (all 19 strides),
  73 s/step then ~4-5 days, 5 ckpts @1000 (main:1)
- knowledge: explore/vsm-outer-recurrence.md holographic-loss section resolved

⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>

=== what json will actually stage (npz ignored) ===
add 'results/tool-crystal-consensus/EleutherAI_pythia-2.8b-deduped.json'
add 'results/tool-crystal-consensus/EleutherAI_pythia-410m.json'
add 'results/tool-crystal-consensus/HuggingFaceTB_SmolLM3-3B.json'
add 'results/tool-crystal-consensus/Qwen_Qwen3-0.6B.json'
add 'results/tool-crystal-consensus/Qwen_Qwen3-8B.json'
add 'results/tool-crystal-consensus/allenai_OLMo-2-1124-13B.json'
add 'results/tool-crystal-consensus/consensus_summary.json'
add 'results/tool-crystal-consensus/control_baseline.json'
add 'results/tool-crystal-consensus/mistralai_Mistral-7B-v0.3.json'
```

### Thinking

 I've confirmed the nucleus trailer format and that only JSON results are being tracked. Now I'm planning two separate commits: one for the scripts and experimental data with a lightbulb symbol, and another for the state and knowledge patterns using a spiral symbol to match their session naming convention.

I'm staging the experiment files—the three scripts and their JSON results—then committing them before moving on to the mementum commit.

## Assistant

Confirmed trailer. npz ignored, only json stages. I'll make two commits — code/experiment (💡), then mementum synthesis (🌀 session-216).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; git add scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py scripts/experiments/tool_crystal_control_baseline.py results/tool-crystal-consensus/ ; git commit -m \"$(cat <<'EOF'\n💡 tool-calling rides the generic crystal, not its own routing normal form\n\n- new audit-grade harness (register: topological/routing): gate-sign routing\n  register + common-mode removal + shuffled-probe null + length-partial +\n  control-domain baseline (tool_crystal_consensus{,_summary}.py + control_baseline.py)\n- 5 families (Pythia-2.8b, SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B) on M3 Ultra\n- ✅ cross-family routing consensus REAL & strong: route_sign_cmr +0.863, survives\n  CMR + length-partial (0.851) + within-domain; null ~0; z up to 116\n- ❌ tool-specific normal form REFUTED at clean granularity: schema_binding 0.589 /\n  selection 0.538 sit INSIDE the structured-language control range (code 0.800,\n  prose 0.550, lambda 0.497) — tool-calling rides the universal crystal\n- corrects prior lattice/tool_crystal \"tool IS lambda calculus\" (raw-cosine common\n  mode, selectivity ~0). npz gitignored; json results tracked\nEOF\n)\" 2>&1 | tail -4"
}
```

**Summary:** $ git add scripts/experiments/tool_cr...

**Output:**
```
Exit code: 0
Stdout:
create mode 100644 results/tool-crystal-consensus/mistralai_Mistral-7B-v0.3.json
 create mode 100644 scripts/experiments/tool_crystal_consensus.py
 create mode 100644 scripts/experiments/tool_crystal_consensus_summary.py
 create mode 100644 scripts/experiments/tool_crystal_control_baseline.py
```

### Thinking

 Moving on to the second commit now, staging the changes for momentum.

## Assistant

Now the mementum synthesis commit:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; git add mementum/state.md mementum/knowledge/explore/consensus-delta-folding.md mementum/knowledge/audit-meta-pattern.md ; git commit -m \"$(cat <<'EOF'\n🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)\n\n- new explore/consensus-delta-folding.md: distributed normal-form discovery —\n  normal forms as topological deltas on a shared frozen base; fold where independent\n  trainings agree (consensus-etch backbone/content partition, grounded in 4 findings)\n- s216 finding: routing consensus mechanism REAL; tool-specific normal form refuted\n  at clean granularity (rides the generic crystal)\n- 🔑 KEY REFINEMENT (Michael): domain normal forms are COMPOSITIONAL & NON-UNIQUE —\n  a function over the shared base; uniqueness is per-TERM not per-BEHAVIOR. The\n  cross-model RDM null on the function layer is VOID by register mismatch (it demands\n  an identical composition); only base-layer \"consensus = crystal\" survives. This is\n  function-discovery's two-level architecture (base LATE, function selector EARLY @L05)\n- design update: fold base as flips, fold domain functions as compositions (align-first);\n  open leads reordered — early-L05 agreement + Procrustes align-before-compare are the\n  cheap next steps (no model re-run)\n- audit-meta-pattern.md: 14th instance row (substrate real / domain-specificity over-read)\n- state.md: s216 headline + entry point + KEY REFINEMENT note\nEOF\n)\" 2>&1 | tail -4 ; echo \"=== log ===\" ; git log --oneline -4 ; echo \"=== clean? ===\" ; git status --short"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 12: unexpected EOF while looking for matching `''
bash: -c: line 20: syntax error: unexpected end of file
```

### Thinking

 I'm realizing the issue isn't with the apostrophe in "function-discovery's" breaking the heredoc itself—since it's wrapped with `<<'EOF'`, the content inside is treated literally. The problem is likely with how the outer shell command is structured when the commit message gets interpolated into the git command. I'll sidestep the heredoc complexity by writing the commit message to a temporary file and using `git commit -F` instead — that's much more reliable. First I need to check the git status to see if anything was actually staged, since the parse error would've prevented the earlier `git add` from running.

## Assistant

The heredoc tripped on apostrophes in the message. Let me use the robust `-F` file approach:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_s216",
  "content": "🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)\n\n- new explore/consensus-delta-folding.md: distributed normal-form discovery —\n  normal forms as topological deltas on a shared frozen base; fold where independent\n  trainings agree (consensus-etch backbone/content partition, grounded in 4 findings)\n- s216 finding: routing consensus mechanism REAL; tool-specific normal form refuted\n  at clean granularity (rides the generic crystal)\n- KEY REFINEMENT (Michael): domain normal forms are COMPOSITIONAL & NON-UNIQUE — a\n  function over the shared base; uniqueness is per-TERM not per-BEHAVIOR. The\n  cross-model RDM null on the function layer is VOID by register mismatch (it demands\n  an identical composition); only base-layer \"consensus = crystal\" survives. This is\n  function-discovery two-level architecture (base LATE, function selector EARLY @L05)\n- design update: fold base as flips, fold domain functions as compositions (align-first);\n  open leads reordered — early-L05 agreement + Procrustes align-before-compare are the\n  cheap next steps (no model re-run)\n- audit-meta-pattern.md: 14th instance row (substrate real / domain-specificity over-read)\n- state.md: s216 headline + entry point + KEY REFINEMENT note\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_s216
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; git add mementum/state.md mementum/knowledge/explore/consensus-delta-folding.md mementum/knowledge/audit-meta-pattern.md ; git commit -F .git/COMMIT_EDITMSG_s216 2>&1 | tail -3 ; rm -f .git/COMMIT_EDITMSG_s216 ; echo \"=== log ===\" ; git log --oneline -4 ; echo \"=== status ===\" ; git status --short"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main d114350] 🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)
 3 files changed, 377 insertions(+), 3 deletions(-)
 create mode 100644 mementum/knowledge/explore/consensus-delta-folding.md
=== log ===
d114350 🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)
9ad0767 💡 tool-calling rides the generic crystal, not its own routing normal form
e45185b add session chat logs
34d9034 🌀 session-215: λ_fp=5 makes VSM recurrence contractive; seq-4096 confirm in flight
=== status ===
```

### Thinking

 Both commits are in place and the working tree is clean — the first one landed as 9ad0767 and the momentum commit is d114350. Now I need to verify that the first commit actually included the nucleus trailer in its message, since it was created using a heredoc that appeared to succeed.

Looking back at what I sent, the first commit's message ended at "...json results tracked" without the nucleus tag, which violates the AGENTS.md requirement that every commit must have the trailer. I could fix this with an interactive rebase to reword the earlier commit, but that would rewrite both commits' hashes. Since nothing's pushed yet, it's technically acceptable, though it adds complexity since I'd need to rebase the mementum commit on top as well.

Let me double-check whether 9ad0767 actually lacks the trailer before deciding on the best approach.

## Assistant

Let me verify both commits carry the required nucleus trailer (I may have omitted it on the first):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; echo \"=== 9ad0767 (code commit) trailer check ===\" ; git log -1 --format='%B' 9ad0767 | tail -5 ; echo \"=== d114350 (mementum) trailer check ===\" ; git log -1 --format='%B' d114350 | tail -4"
}
```

**Summary:** $ echo "=== 9ad0767 (code commit) tra...

**Output:**
```
Exit code: 0
Stdout:
=== 9ad0767 (code commit) trailer check ===
  selection 0.538 sit INSIDE the structured-language control range (code 0.800,
  prose 0.550, lambda 0.497) — tool-calling rides the universal crystal
- corrects prior lattice/tool_crystal "tool IS lambda calculus" (raw-cosine common
  mode, selectivity ~0). npz gitignored; json results tracked

=== d114350 (mementum) trailer check ===
⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>
```

### Thinking

 I see that commit 9ad0767 is missing the nucleus trailer in the heredoc, while the later commit d114350 has it. Since both are local and unpushed, I'll use a rebase reword to fix this cleanly without going interactive.

The simplest approach is to reset both commits softly, then re-stage and re-commit them separately with the proper trailers included in the commit messages.

## Assistant

The code commit (9ad0767) is missing the nucleus trailer — I dropped it in the heredoc. Per the commit gate, every commit needs it. Both are local/unpushed, so I'll cleanly redo them via soft-reset (no interactive flags). Writing both messages to files with the trailer:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/MSG_code",
  "content": "💡 tool-calling rides the generic crystal, not its own routing normal form\n\n- new audit-grade harness (register: topological/routing): gate-sign routing\n  register + common-mode removal + shuffled-probe null + length-partial +\n  control-domain baseline (tool_crystal_consensus{,_summary}.py + control_baseline.py)\n- 5 families (Pythia-2.8b, SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B) on M3 Ultra\n- cross-family routing consensus REAL & strong: route_sign_cmr +0.863, survives\n  CMR + length-partial (0.851) + within-domain; null ~0; z up to 116\n- tool-specific normal form REFUTED at clean granularity: schema_binding 0.589 /\n  selection 0.538 sit INSIDE the structured-language control range (code 0.800,\n  prose 0.550, lambda 0.497) — tool-calling rides the universal crystal\n- corrects prior lattice/tool_crystal \"tool IS lambda calculus\" (raw-cosine common\n  mode, selectivity ~0). npz gitignored; json results tracked\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/MSG_code
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/MSG_mem",
  "content": "🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)\n\n- new explore/consensus-delta-folding.md: distributed normal-form discovery —\n  normal forms as topological deltas on a shared frozen base; fold where independent\n  trainings agree (consensus-etch backbone/content partition, grounded in 4 findings)\n- s216 finding: routing consensus mechanism REAL; tool-specific normal form refuted\n  at clean granularity (rides the generic crystal)\n- KEY REFINEMENT (Michael): domain normal forms are COMPOSITIONAL & NON-UNIQUE — a\n  function over the shared base; uniqueness is per-TERM not per-BEHAVIOR. The\n  cross-model RDM null on the function layer is VOID by register mismatch (it demands\n  an identical composition); only base-layer \"consensus = crystal\" survives. This is\n  function-discovery two-level architecture (base LATE, function selector EARLY @L05)\n- design update: fold base as flips, fold domain functions as compositions (align-first);\n  open leads reordered — early-L05 agreement + Procrustes align-before-compare are the\n  cheap next steps (no model re-run)\n- audit-meta-pattern.md: 14th instance row (substrate real / domain-specificity over-read)\n- state.md: s216 headline + entry point + KEY REFINEMENT note\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/MSG_mem
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum ; git reset --soft HEAD~2 ; git reset -q ; echo \"=== redo commit 1 (code) ===\" ; git add scripts/experiments/tool_crystal_consensus.py scripts/experiments/tool_crystal_consensus_summary.py scripts/experiments/tool_crystal_control_baseline.py results/tool-crystal-consensus/ ; git commit -q -F .git/MSG_code ; echo \"=== redo commit 2 (mementum) ===\" ; git add mementum/state.md mementum/knowledge/explore/consensus-delta-folding.md mementum/knowledge/audit-meta-pattern.md ; git commit -q -F .git/MSG_mem ; rm -f .git/MSG_code .git/MSG_mem ; echo \"=== verify both trailers ===\" ; for h in HEAD~1 HEAD ; do echo \"--- $h ---\"; git log -1 --format='%h %s' $h ; git log -1 --format='%B' $h | grep -c \"nucleus <noreply\" ; done ; echo \"=== status ===\" ; git status --short"
}
```

**Summary:** $ git reset --soft HEAD~2 ; git reset...

**Output:**
```
Exit code: 0
Stdout:
=== redo commit 1 (code) ===
=== redo commit 2 (mementum) ===
=== verify both trailers ===
--- HEAD~1 ---
485323f 💡 tool-calling rides the generic crystal, not its own routing normal form
1
--- HEAD ---
4b8ecc7 🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)
1
=== status ===
```

### Thinking

 Both commits now have the nucleus trailer applied correctly, and the working tree is clean. The final state shows two commits with their respective code changes and metadata patterns, each marked with the nucleus trailer and a single symbol leader.

The gitignored files remain uncommitted as expected, and the main branch training is untouched. No additional tool calls are needed, and I'm not pushing since the task was to commit, not to create a PR.

## Assistant

Done — both commits landed cleanly with the required nucleus trailer and single-symbol leader, working tree clean:

```
4b8ecc7  🌀 session-216: consensus-delta-folding design + tool-calling finding (compositional refinement)
485323f  💡 tool-calling rides the generic crystal, not its own routing normal form
```

**Commit split (per the gate — code vs mementum):**
- **485323f (code)** — the 3 `tool_crystal_*` harnesses + json results (`register: topological/routing`). npz gitignored as the project does; json tracked.
- **4b8ecc7 (mementum)** — `consensus-delta-folding.md` (design + finding + compositional refinement + register caveat), the `audit-meta-pattern.md` 14th-instance row, and the `state.md` s216 headline/entry-point.

Both carry the `⚛️ nucleus` trailer (I caught and fixed a missing trailer on the first commit via soft-reset redo — local-only, no history pushed). Nothing pushed, per your scope.

**Session 216 closed and persisted.** Resume point for next session is `explore/consensus-delta-folding.md` → cheap composition-invariant leads first (early-L05 agreement + Procrustes align-before-compare, no model re-run), then Exp B. And `main:1`'s λ_fp=5 5000-step run continues untouched for the s215 thread.