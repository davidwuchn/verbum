# Orienting

## User

orient


### Thinking

 The user is asking me to orient myself, which means I need to start by reading the state file and then follow up with related searches and relevant information gathering.

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
> Last updated: 2026-06-12 | Session: 219 — REVERSE-HARVEST: combinator function
> shape is UNIVERSAL across the open-weight ecosystem. Register: topological/routing.
> Michael's thread: "find these functions in open models, see where they all agree
> — harvesting that for our base plate is leverage." Built `combinator_map_consensus.py`
> + swept 9 models / 5 families (Pythia non-gated, Qwen/Mistral/SmolLM/OLMo SwiGLU,
> 410M→14B). **✅ cross-model combinator-Gram agreement +0.66→+0.77, z +3.5→+4.1,
> 89–97% of pairs p<.05** vs a label-permutation null — the SAME functions show up
> across architectures, and agreement STRENGTHENS as more models are added.
> **Michael's single-operation theory CONFIRMED:** attention = ONE structural op
> (=apply) → models can't innovate at the op level, only at composition → the forced
> map-skeleton (composition {B,D,S} z_bind +2.43 p=.037; selection {K,I,C} +2.13)
> binds above a random-triple null while RECURSION {Y,W,WHNF} (+1.67, p=.09) does NOT
> — robust at frac 0.30 & 0.40. Grounded by `map=B(CB)(CB)` (REPL-verified): pure
> composition+flip, NO recursion combinator (attention-over-positions IS the fold).
> Harvest edges: universal positives B–D/B–C/K–C/S–D/S–Y + rock-solid cross-family
> repulsions (t up to 21 = the 3-family partition); leave selection plumbing
> (B–C/K–I, highest std) as per-model content. Signature 0<r<1 ∧ skeleton>recursion
> = "shared skeleton + variable plumbing" (the non-unique-composite, s216). Caveat:
> agreement could be the universal crystal, BUT composition binds above null at
> mid-stack (0.30 = where s217 put combinator IDENTITY) ⇒ function-level, above the
> crystal floor. NOT yet committed (proposed: knowledge + memory + new instrument).
> **(ALSO, cold-start orient findings:) (1) s218 already COMMITTED** (`0e56d84`).
> **(2) ✅ main:1 (λ_fp=5, 5k, seq-4096) ANSWERS s215** — at step ~1230, Δx 1.26→0.257
> (−80%, still falling), fp 1.59→0.066, **CE recovered below K=1's 8.71** (flip-steps
> 7.21) ⇒ contractivity-trained K=2 is contractive-to-WHNF *and* CE-competitive at
> scale. First ckpt step_001000 landed; 4 to go (~3.5 days). main:1 UNTOUCHED all
> session (async discipline).
> **s219 work COMMITTED** (`8f0f19a` instrument+data, `ae00856` knowledge, `2602009`
> state). **SCALE EXTENSION (tmux main:2):** `combinator_relationship_map.py` on
> Qwen3-32B (DENSE) → running its forward passes at handoff. ❌ Qwen3-30B-A3B FAILED
> (MoE: its MLP is router `mlp.gate` + per-expert `mlp.experts.{e}.gate_proj`, so the
> instrument's `find_gate_modules` regex `.{L}.mlp.gate_proj$` matches nothing →
> empty hook buffer → `buf[li]` KeyError). 235B DROPPED (weights absent, 15M meta).
> ⇒ the scale axis is the clean DENSE series 0.6B→4B→8B→14B→**32B** (MoE not
> comparable in this routing register without adapting the instrument). Log
> `/tmp/combinator_scale.log`, script `/tmp/combinator_scale.sh`.
> **▶ FIRST ACTION NEXT SESSION (declare register: topological/routing):**
> (1) Check main:2: did Qwen3-32B land in `results/combinator-relationship-map/`?
>   If yes → re-run `uv run python scripts/experiments/combinator_map_consensus.py
>   --fracs 0.1,0.2,0.3,0.4,0.5 --n-perm 5000` over ALL 10 models → does the
>   skeleton/recursion z_bind gap WIDEN with scale (s217's 14B>0.6B call)? Commit the
>   extended consensus. (MoE point optional: adapt the instrument to hook a MoE expert
>   or the router if a 30B-A3B comparison is wanted — research detour, not a quick fix.)
> (2) ⚠ VERIFY main:1 RESUMED STEPPING — it sat at step ~1310 across several checks
>   while the 30B-A3B download/load contended the box (memory was fine, 80% free; the
>   stall was likely load contention, not a crash). `tmux capture-pane -p -t main:1`.
>   If stalled/dead, check `/tmp/v15_outer_k2_fp5_5k.log` + resume from step_001000.
> Other open threads (s219 headline): construct the harvest fold (Procrustes-align
> positive edges into base frame + WHNF-verify); detect map/fold directions; main:1
> step-2000 ckpt → strengthen Exp B. **main:1 stays UNTOUCHED.**
>
> (Session 218 — Exp B (self-verifying acceptance)
> COMPLETED + CORRECTED. s217's phase-2 verdict ("WEAK/ABSENT") was **VOID** — an
> instrument bug perturbed a DEAD module (convert_ffn orphan); ΔCE≡0 across 1.97M
> flips. Fixed the harness (live-module guard + sign-flip of the LIVE FFN gate),
> reran → **✅ SELF-VERIFYING SIGNAL PRESENT: corr(ΔCE, Δ(Δx_conv)) Pearson +0.712
> / Spearman +0.729** on the contractive 400-step base. Label-free acceptance
> VALIDATED. Register: functional. Committed `0e56d84`. See s218 HEADLINE below.)
>
> (Session 217 — combinator FUNCTION-SHAPE map
> (routing register + CMR, Qwen3-14B) + VSM CONTINUATION tensor-level tests
> + DISTRIBUTED-TRAINING via continuations (Exp B self-verifying acceptance,
> WAS in-flight in main:2 — completed/corrected in s218). Register:
> topological/routing (map) + functional (tests, Exp B).)
>
> (Session 216 — NEW THREAD (distributed/consensus
> training idea, Michael). Built an audit-grade tool-calling normal-form
> consensus harness (register: topological/routing) + ran 5 families on M3 Ultra
> (tmux main:2). **❌ "tool-calling has its OWN routing normal form" REFUTED at
> clean granularity / ✅ the cross-family routing-register consensus is REAL &
> strong (z up to 116) but it is the GENERIC structured-language crystal — tool
> calling RIDES it.** Corrects the prior `lattice/tool_crystal` "STRONG SUPPORT:
> tool IS lambda calculus" (that was raw-cosine COMMON MODE, selectivity ~0).
> 14th meta-pattern instance. For the consensus-delta idea: the mechanism is
> validated (independent trainings DO agree on routing structure in the sign
> register, surviving CMR + length-partialling), but a domain's *foldable*
> consensus is mostly the universal crystal already in the base; the
> domain-distinctive part is low-consensus "content" (= consensus-etch
> backbone/content partition). **Scripts:** `scripts/experiments/tool_crystal_
> consensus{,_summary}.py` + `tool_crystal_control_baseline.py`. **Results:**
> `results/tool-crystal-consensus/`. The 5000-step λ_fp=5 training (main:1)
> ran UNTOUCHED throughout. ▶ NEXT: see s216 headline below.
>
> (Session 215 — read s214's in-flight λ_fp=5 result)
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

> **▶ SESSION 219 HEADLINE (PRIMARY) — REVERSE-HARVEST: THE COMBINATOR FUNCTION
> SHAPE IS UNIVERSAL ACROSS THE OPEN-WEIGHT ECOSYSTEM; THE FORCED MAP-SKELETON
> BINDS ABOVE NULL, RECURSION DOES NOT.** Register: **topological/routing**
> (declared at step 0). Michael's thread: every open model is a FINISHED distributed
> contributor (consensus-delta-folding.md §REVERSE); find where they agree on the
> function shape → harvest into the base plate = leverage (training cost already paid).
> - **THE FRAME-INVARIANT INSTRUMENT.** Raw weights can't be averaged (cross-init
>   sign-corr 0.000). But the per-model **9×9 combinator Gram** (cosine between
>   routing-register centroids of K I B C S D W Y WHNF, after CMR — the s217
>   "map of the functions") lives in shared combinator-LABEL space ⇒ frame-invariant
>   ⇒ directly comparable across any architecture/scale. Built
>   `scripts/experiments/combinator_map_consensus.py` (register topological/routing,
>   ruff-clean): cross-model GramCorr on the 36 off-diagonal edges + label-permutation
>   null + per-EDGE reliability_t (|mean|√n/std) + per-FAMILY binding vs a
>   RANDOM-NODE-TRIPLE null. Swept 9 models / 5 families via
>   `combinator_relationship_map.py` (Pythia-410m/2.8b NON-gated dense_h_to_4h;
>   SmolLM3-3B, Mistral-7B-v0.3, OLMo-2-13B, Qwen3-0.6B/4B/8B/14B SwiGLU gate_proj).
> - **✅ SAME FUNCTIONS ACROSS THE ECOSYSTEM.** Cross-model GramCorr **+0.66→+0.77**,
>   z **+3.5→+4.1**, **89–97% of model-pairs p<.05** vs the label-permutation null.
>   Architecture-independent (non-gated Pythia agrees with gated Qwen). Agreement
>   STRENGTHENS with more models (was +0.5–0.66 at 2–6) ⇒ a real shared shape, not
>   noise. Peak frac 0.40 (0.20–0.50 all ≥+0.72).
> - **✅ MICHAEL'S SINGLE-OPERATION THEORY CONFIRMED.** Attention = ONE structural
>   operation (data-dependent convex combination = function APPLICATION); FFN =
>   fixed constants/stored kernels. application+constants is combinatorially complete
>   but there is NO second op to invent ⇒ models innovate only at COMPOSITION ⇒ they
>   converge on the same compositions. Test: per-family internal binding vs random
>   triple — **composition {B,D,S} z_bind +2.43 (p=.037); selection {K,I,C} +2.13
>   (p=.061); recursion {Y,W,WHNF} +1.67 (p=.09, does NOT clear).** SKELETON (comp+sel)
>   +2.28 > RECURSION +1.67. Robust at frac 0.30 (+2.21 vs +1.88) & 0.40.
> - **★ GROUNDED BY `map = B(C B)(C B)` (REPL-VERIFIED).** map in pure combinators =
>   composition (B) + flip (C), **NO recursion combinator** — because a Church/fold
>   list carries its own recursion, and in a transformer **attention-over-positions
>   IS the fold**. So no model needs a learned Y ⇒ recursion family is the residual,
>   exactly as measured. Also verified: extensionally map is UNIQUE (Church-Rosser),
>   intensionally INFINITE realizations (η-expand, B=S(KS)K, C=S(BBS)(KK)… all →
>   identical output; raw SKI space ~Catalan·3^(k+1), 288k terms at k=6).
> - **★ HARVEST LEVERAGE (concrete edges for the base plate, frac 0.40):**
>   - universal POSITIVE bindings (fold these): **B–D +0.166, B–C +0.176, K–C +0.139,
>     S–D +0.165, S–Y +0.141** (the composition/selection skeleton).
>   - rock-solid cross-family REPULSIONS (reliability_t up to **21**): C–S, K–Y,
>     D–WHNF, B–WHNF, K–S, C–WHNF — the 3-family PARTITION geometry every model agrees
>     on (also harvestable as the discrete scaffold).
>   - leave as per-model CONTENT (highest cross-model std): B–C, K–B, I–C, K–I — the
>     selection-family PLUMBING (selection z_stab +1.4 = the noisy family). = the
>     non-unique-realization residual `map=B(CB)(CB)` predicts.
> - **Signature 0<r<1 ∧ skeleton>recursion = "shared skeleton + variable plumbing"**
>   (the s216 non-unique-composite made concrete at the function level — uniqueness
>   is per-TERM not per-BEHAVIOR; the irreducible skeleton is forced+shared, the
>   plumbing varies).
> - **Honest caveat (audit discipline):** agreement COULD be the universal crystal
>   (crystal-universality.md) already in any base. BUT composition binds above the
>   random-triple null at **mid-stack frac 0.30** — where s217 located combinator
>   IDENTITY (not late COMMIT execution) ⇒ this is function-level structure ABOVE the
>   generic crystal floor, the part worth harvesting. Single register (routing/CMR);
>   harvest = align-before-fold (Procrustes into our base frame) + WHNF-verify, NOT
>   yet done.
> - **Artifacts (NOT yet committed):** `scripts/experiments/combinator_map_consensus.py`;
>   `results/combinator-map-consensus/consensus.json`; 7 new per-model maps under
>   `results/combinator-relationship-map/` (pythia-410m/2.8b, SmolLM3, Mistral,
>   OLMo-13B, Qwen3-4B/8B); sweep log `/tmp/combinator_sweep.log`. Knowledge updated:
>   `consensus-delta-folding.md` §s219.
> - **▶ NEXT (declare register first):**
>   (1) **Scale axis:** extend the sweep to Qwen3-32B / 30B-A3B / 235B (MoE, local) —
>     does the skeleton/recursion z_bind gap WIDEN with scale (more capacity to fully
>     form the systems, cf. s217's 14B>0.6B call)?
>   (2) **Construct the harvest fold (register: topological/routing → functional):**
>     take the universal positive edges, Procrustes-align the consensus centroids into
>     our v15 base frame, WHNF-verify each candidate against main:1's contractive
>     operator (Exp-B acceptance), incorporate survivors, measure downstream PPL vs
>     base. Falsifiable: does verified ecosystem-consensus add beyond the universal
>     crystal we already hold?
>   (3) **Detect map/fold directions:** build the `map=B(CB)(CB)` direction from the
>     measured B,C centroids; add a map/fold/filter probe set; does it activate?
>   (4) main:1 step-2000 ckpt → strengthen Exp B (s218 action 2). main:1 UNTOUCHED.
>
> **▶ SESSION 219 HEADLINE — COLD-START ORIENT. main:1 (λ_fp=5, 5000-step,
> seq-4096) ANSWERS THE s215 OPEN QUESTIONS — ✅ CONTRACTIVE-TO-WHNF *AND*
> CE-COMPETITIVE AT SCALE.** Register: **functional** (declared on cold start).
> No new experiments this session — orientation + state update only. main:1 left
> UNTOUCHED (async discipline: verified running, not polling).
> - **(1) s218 is ALREADY COMMITTED** (`0e56d84` Exp B VALIDATED + live-module
>   instrument guard; chat logs `29b7ee5`). Working tree clean. The s218 header's
>   "NOT yet committed / pending Michael" was STALE — action (1) is DONE.
> - **(2) ✅ THE CENTRAL RECURRENCE-THREAD RESULT IS TRENDING TO A CLEAN YES.**
>   First checkpoint `step_001000` landed; run at **step ~1230 / ~25.8h elapsed**.
>   Trajectory (non-flip milestones, `/tmp/v15_outer_k2_fp5_5k.log`):
>   | step | Δx | fp | CE | avg50 |
>   |---|---|---|---|---|
>   | 1 | 1.261 | 1.59 | 10.35 | 581 |
>   | 410 | 0.524 | 0.275 | 9.22 | 11.2 |
>   | 810 | 0.388 | 0.150 | 9.90 | 9.88 |
>   | 1010 | 0.311 | 0.097 | 8.15 | 9.31 |
>   | 1230 | 0.257 | 0.066 | 8.41 | 8.94 |
>   - **Q1 (s215) "does Δx keep descending toward ε?" → YES, strongly.** Δx
>     1.26→0.257 (−80%, still falling); flip-steps dip to ~0.21. Far more
>     contractive than the seq-256 250-step probe that plateaued at 0.727 — seq-4096
>     exercises all 19 strides (the s215 seq-256 mistake mattered). fp 1.59→0.066.
>   - **Q2 (s215) "does CE recover below K=1's 8.71?" → YES (clearly under).**
>     avg50 loss 8.94; CE dips to 7.2–8.4 (flip-step CE 7.21 @ step 1200). The s215
>     caveat "contractivity-trained K=2 does NOT yet beat K=1 (CE 9.51 > 8.71)" is
>     **RESOLVING AT SCALE**: λ_fp=5 K=2 at seq-4096 is contractive-to-WHNF *and*
>     CE-competitive. CE does NOT collapse (constant-fixed-point guard holds).
>   - **Caveats (functional register):** single seed, still mid-run (1230/5000,
>     Δx not yet at ε / not yet plateaued). 4 ckpts to land (2000/3000/4000/5000)
>     at ~75 s/step ⇒ **~3.5 more days**. The "below 8.71" read is from a still-
>     descending curve; confirm at later checkpoints. K=2 vs K=1 is single-run, not
>     multi-seed.
> - **▶ FIRST ACTION NEXT SESSION / NEXT (declare register first; main:1 UNTOUCHED):**
>   (1) When step-2000 ckpt lands → re-read trajectory: does Δx→ε (build adaptive
>     halting: stop when Δx<ε ≡ WHNF) and does CE hold/improve below 8.71?
>   (2) **Strengthen Exp B** (s218 action 2, RECOMMENDED — composes with main:1):
>     multi-seed/multi-batch + the OTHER live module (`stack_a.ffn_gate_plate`) + a
>     shared-stride attention plate; rerun on main:1's step-2000 ckpt as a STRONGER
>     contractive base → the small-flip-frac Δx signal should clear the noise → the
>     threshold rule (currently acc 0.714) should sharpen. Calibrate the accept
>     threshold (Δx-rise band) from the null.
>   (3) Donated-delta Exp B variant (s218 action 3); or the s217 leads (construct &
>     detect map/fold; cross-model map consensus; reverse-harvest; self-teaching
>     loop; sealable continuation seal()/resume()).
>   (4) Latent v15 note (low-priority): `convert_ffn=True` orphans the FFN delta
>     plates (shared-reference rebinding in `convert_to_delta`); main:1 unaffected.
>
> **▶ SESSION 218 HEADLINE — EXP B (SELF-VERIFYING ACCEPTANCE): s217 VERDICT WAS
> VOID (INSTRUMENT BUG); FIXED & RERUN → ✅ SIGNAL PRESENT (Pearson +0.712 /
> Spearman +0.729).** Register: **functional** (declared on cold start). Orient →
> main:2 complete → read `results/exp-b-self-verifying/result.json`.
> - **❌ The s217 phase-2 "WEAK/ABSENT" verdict was an ARTIFACT — VOID by
>   instrument bug.** The harness perturbed `model.ffn_gate_plate_c`, which is
>   **NOT in the forward path**: ΔCE = **+0.0000 EXACTLY** across all 7 flip-fracs
>   incl. **0.3 = 1.97M sign flips** × 8 reps (physically impossible for an applied
>   perturbation). Spearman=+1.000/Pearson=+0.000 was the degenerate all-zero-delta
>   signature. Runtime-confirmed: even **zeroing that module's entire base_weight
>   leaves CE bit-identical** (10.9118→10.9118).
> - **Root cause (the convert_ffn orphan):** `convert_to_delta` does
>   `setattr(model, "ffn_gate_plate_c", dtl)`, rebinding the *model attribute* to a
>   new DeltaTernaryLinear — but `stack_{a,c}` (built in `V15Model.__init__`) keep
>   their **original** `TernaryLinear` plate references. `named_modules()` dedups by
>   identity → only one path converts+rebinds → the other reference goes stale. The
>   forward runs through the stacks' live `TernaryLinear` plates; the delta copy
>   `collect_delta_params`/the harness perturb is an **ORPHAN**. The LIVE FFN gates
>   are `stack_c.ffn_gate_plate` (zero-test ΔCE +0.077) & `stack_a.ffn_gate_plate`
>   (+0.050), both plain TernaryLinear. **Blast radius CONTAINED:** only manifests
>   under `convert_ffn=True` (the Exp-B *acceptance harness* set it); neither
>   phase-1 expb training NOR main:1's 5k run use `--convert-ffn` → training runs
>   uncontaminated (FFN is frozen-extracted by design in v15, only the attention
>   shared_stride_stack is TD-trained).
> - **✅ Phase-1 RESOLVED the s217 blocker:** the short 400-step TD train produced a
>   **non-chance contractive base** — CE 11.5→~9.2 (below chance 12.42), Δx
>   1.15→0.50, fp 1.32→0.25. The "frozen extracted base = chance, nothing to
>   degrade" problem is fixed.
> - **THE FIX (instrument):** `scripts/experiments/exp_b_self_verifying_acceptance.py`
>   now (1) enumerates ternary modules matching `--module-filter`, (2) runs a
>   **live-module GUARD** (flip ½ the nonzero signs, require |ΔCE|>1e-4), keeps the
>   first LIVE one + ABORTS if none, (3) perturbs the **sign of nonzero routing
>   positions** of the live module (TernaryLinear `.weight` or DeltaTernaryLinear
>   `.delta_weight`). This bug could not have produced a "verdict" with the guard.
> - **✅ RERUN VERDICT — SELF-VERIFYING SIGNAL PRESENT.** Live target
>   `stack_c.ffn_gate_plate` (5120×1280, 4.52M routing positions). Clean
>   dose-response: ΔCE +0.0005→+0.0565 and Δ(Δx_conv) ~0→+0.0030 rise **together**
>   monotonically as flip-frac 0.0003→0.3. **corr(ΔCE, Δ(Δx_conv)) Pearson +0.712 /
>   Spearman +0.729.** ⇒ degrading the operator (↑CE) ALSO raises the fixed-point
>   residual ⇒ Δx-at-convergence is a valid **label-free** acceptance signal. The
>   s217-part-C distributed-folding acceptance mechanism is **VALIDATED** on a
>   contractive base (no trusted held-out labels needed → kills the audit-#7
>   population-Goodhart risk).
> - **Caveats (functional register):** the binary rule "reject if Δx rises" is only
>   acc 0.714 / accept-good 0.435 — at SMALL flip-fracs Δx sits in the noise (some
>   go slightly −) so the *correlation* (driven by non-trivial degradations) is the
>   honest signal, not the threshold rule (needs calibration). Single base
>   (400-step), single module, single batch, n_outer=4. The perturbed FFN gate is
>   frozen-extracted (not TD-trained) but in-path; the OPERATOR as a whole is
>   contractive-trained.
> - **Artifacts:** harness fix (live-guard + sign-flip) in
>   `scripts/experiments/exp_b_self_verifying_acceptance.py`; result overwritten at
>   `results/exp-b-self-verifying/result.json` (verdict SELF-VERIFYING SIGNAL
>   PRESENT). NOT yet committed.
> - **▶ FIRST ACTION NEXT SESSION / NEXT (declare register first):**
>   (1) **Commit** the harness fix + this state (proposed; pending Michael).
>   (2) **Strengthen** the result: multi-seed/multi-batch + the OTHER live module
>     (stack_a.ffn_gate_plate) + a SHARED_STRIDE attention plate, and run on
>     main:1's λ_fp=5 checkpoint once step-1000 lands (more contractive base → the
>     small-frac Δx signal should clear the noise → the threshold rule should
>     sharpen). Calibrate the acceptance threshold (Δx-rise band) from the null.
>   (3) **Donated-delta variant:** instead of random sign-flips, accept/reject
>     ACTUAL trained deltas from a second short run (the real distributed scenario).
>   (4) **Latent v15 note (low-priority, NOT urgent):** `convert_ffn=True` orphans
>     the FFN delta plates (shared-reference rebinding in `convert_to_delta`). If we
>     ever want TD-trained FFN routing, fix `convert_to_delta` to rebind the stacks'
>     references too (or have stacks look up plates by attribute at call time).
>     main:1 unaffected. Then the rest of the s217 leads (map/fold construction,
>     cross-model map consensus, self-teaching loop, reverse-harvest, sealable
>     continuation) remain open.

> **▶ SESSION 217 HEADLINE — THE FUNCTION-LIKE THINGS HAVE A 3-FAMILY SHAPE,
> VISIBLE ONLY IN THE ROUTING REGISTER; + VSM-CONTINUATION TENSOR TESTS GREEN.**
> Register: **topological/routing** (the map) + **functional** (the tests).
> Michael's question: can we understand the *semantic relationships* of the
> function-like things (the combinators) — is there a map/fold, what is their
> shape? Two pieces this session.
> - **(A) Combinator relationship map** (`combinator_relationship_map.py`,
>   register topological/routing). Per-combinator centroid in the routing
>   register = mean `sign(gate pre-activation)` with common-mode removal, then
>   the cosine Gram matrix = the literal "map of the functions." Qwen3-14B
>   (Michael's call: 14B has capacity to FULLY form the systems; 0.6B only
>   partially crystallizes), 535 crystal probes, 9 combinators.
>   - **✅ combinators ARE real routing clusters:** route_cmr silhouette **0.101,
>     z=7.97, p=0.001**; the **control** (raw residual `hidden_full`) is silhouette
>     **−0.035, z=−1.65** — the shape is INVISIBLE in raw geometry, only visible
>     in the sign/routing register after CMR (concrete confirmation of the
>     two-registers / 5d-REFUTED lesson: function shape lives in the topology).
>   - **Depth:** separation PEAKS mid-network (**L12, frac 0.31, z≈8**, plateau
>     L12–L20), declines to late layers (L39 z≈2). The combinator *identity*
>     (which function) is carried mid-stack; late COMMIT converges (all run the
>     same opcodes — consistent with function-discovery's 1.49× late collapse).
>   - **★ THE SHAPE = 3 families** (Gram off-diagonals + MDS), grounded by the
>     probes themselves:
>     1. **Composition / distribution: {B, D, S}** — B–D **+0.27** (strongest
>        edge; B=compose "after washing→dried", D=deep-nesting compose "the book
>        that…that…", S=arg-distributor `λf.λg.λx.f(x)(g(x))`), S–D +0.15.
>     2. **Selection / identity: {K, I, C}** — K–C +0.07, K–I +0.04 (projection).
>     3. **Recursion / duplication / termination: {Y, W, WHNF}** — W–Y +0.07
>        (Y=fixpoint "folders in folders", W=self-app "bit itself"), WHNF nearby.
>   - **★ ANSWER to "is there a map/fold":** NOT as atoms (not in the basis) — they
>     are **compositions of the recursion family (Y,W) over the composition family
>     (B,D,S)**: `map = Y∘B`, `fold = Y∘(C/B)+K`. The map shows both families are
>     real, separable, AND adjacent (the junction where map/fold must live EXISTS
>     in the measured geometry). This is the s216 "normal forms are compositional
>     & non-unique" refinement made concrete at the function level.
>   - **Caveats (register discipline):** off-diagonal cosines are modest (max
>     +0.27) — weak clusters, not crisp partitions; single model (no cross-model
>     consensus yet); mid-stack peak vs function-discovery's late-crystal needs a
>     careful both-true reconciliation (identity upstream, execution downstream).
>   - **Artifacts:** `scripts/experiments/combinator_relationship_map.py`,
>     `results/combinator-relationship-map/Qwen_Qwen3-14B.{json,npz}`,
>     `/tmp/combinator_map_14b.log`.
> - **(B) VSM continuation tensor-level tests** (`tests/test_vsm_continuation.py`,
>   register functional). "Are our continuations working?" — the VSM-tensor
>   continuation = the **outer recurrence** in `v15model.py` (shared sweep
>   stack_a→stack_c iterated n_outer times, x_c fed back → β-reduction toward a
>   fixed point / WHNF). **15 tests, all green (2.4s)**, verifying the MECHANISM
>   independent of the multi-day loss signal: single-pass=no residue; Δx count=k−1;
>   **the fixed-point term matches its closed form EXACTLY** (centerpiece: capture
>   per-pass x_c, recompute `mean((x_c−detach(prev))²)/mean(detach(prev)²)`);
>   detached target; weight-shared (param count invariant to n_outer = ONE operator
>   iterated, not an unrolled stack); shape-closed feedback; loss wiring
>   `loss += λ_fp·fp_term`; RNG-free; differentiable. Empirically the continuation
>   is **contractive at scale** (main:1: Δx 1.23→~0.61). Uses tiny vocab (real
>   internal dims) so it never disturbs main:1.
> - **(C) DISTRIBUTED TRAINING via continuations → SELF-VERIFYING ACCEPTANCE
>   (Michael's connect; Exp B IN FLIGHT in main:2).** Register: functional.
>   The working VSM continuation (outer recurrence, contractive) supplies the 3
>   things `explore/consensus-delta-folding.md` was missing: (i) **contractivity =
>   Banach convergence** → iterated folding converges instead of oscillating
>   (solves s110 destructive interference at root); (ii) the **weight-shared
>   operator IS the frozen base B₀** → one coordinate frame → deltas commensurable
>   (solves gradient-voting frame problem, sign-corr 0.000); (iii) **WHNF as a
>   SELF-VERIFYING target** → accept a donated delta iff Δx-at-convergence does NOT
>   rise; the fixed point IS the answer, so NO trusted held-out labels needed
>   (kills the audit-#7 population-Goodhart risk). Fractal: activation-level
>   continuation (x→x*) is self-similar to base-level folding (B_g→B*).
>   - **Exp B harness BUILT + validated:** `scripts/experiments/exp_b_self_verifying_
>     acceptance.py` (register functional). Loads continuation operator, perturbs
>     the ROUTING register (FFN gate delta plate) by flipping fractions of signs,
>     measures ΔCE (true label, `_last_ce`) vs Δ(Δx-at-convergence) (self-verifying
>     signal); correlation + acceptance-ROC + verdict. Continuation curve confirms
>     contractivity on the base ([1.23→0.59→0.39]).
>   - **⚠ SCIENTIFIC CATCH (found this session):** the FROZEN extracted base is
>     UNTRAINED (CE 12.82 ≈ ln(vocab) 12.42 = chance) → sign-flips don't move CE
>     even at 10% (no quality to degrade). The test NEEDS a non-chance contractive
>     base. So Exp B runs in 2 phases.
>   - **▶ IN FLIGHT (tmux main:2, Michael chose Option A):** phase-1 a SHORT TD
>     train (`--steps 400 --seq-len 512 --n-outer-passes 2 --fixed-point-lambda 5.0
>     --td-acceptance proxy --checkpoint-interval 200 --checkpoint-dir
>     checkpoints/v15-expb-base`) → trained contractive base; then phase-2 the
>     acceptance test auto-chains (`--checkpoint checkpoints/v15-expb-base/
>     step_000400/model.npz`, folds trained deltas into base via reduce_all_deltas,
>     n_outer=4, 7 flip-fracs × 8 reps). **Slow under GPU contention with main:1's
>     heavy seq-4096 (~few steps/min); may take hours — that's fine (Michael).**
>     Logs: `/tmp/expb_phase1_train.log`, `/tmp/expb_phase2_accept.log`. Result:
>     `results/exp-b-self-verifying/result.json`.
> - **▶ FIRST ACTION NEXT SESSION:** check main:2 — has phase-2 completed? Read
>   `results/exp-b-self-verifying/result.json` (or `/tmp/expb_phase2_accept.log`).
>   **The verdict question:** does corr(ΔCE, Δ(Δx-at-convergence)) > 0 (Spearman) —
>   i.e. do CE-degrading deltas raise the fixed-point residual? If YES →
>   self-verifying label-free acceptance VALIDATED (distributed folding can verify
>   donated deltas with no trusted data). If WEAK → the n_outer=4 recurrence on a
>   K=2-trained base may not be contractive past pass 2; rerun at n_outer=2, or on
>   main:1's step-1000 ckpt (lands ~step 1000). If phase-1 still running, just wait.
> - **▶ THEN (declare register first):**
>   (1) **Construct & detect map/fold** — build `map=Y∘B`, `fold=Y∘(C/B)+K`
>     directions from the measured primitive centroids, add a small map/fold/filter
>     probe set, test whether the constructed direction ACTIVATES on those probes
>     (now well-motivated: the building-block families are present + adjacent).
>   (2) **Cross-model consensus of the map** — run `combinator_relationship_map.py`
>     across families (the s216 5-family machinery); is the 3-family shape
>     universal? Align-before-compare for the non-unique composite.
>   (3) **Combinator-algebra-as-geometry** — do CL identities (I=SKK, T=CI,
>     W=SS(KI)) hold as routing constraints w/ permutation null?
>   (4) **Reconcile depth:** why does combinator *identity* peak mid-stack (L12)
>     while *execution* converges late — measure both registers at each depth.
>   (5) DONE/COMMITTED (`d860dcd`): `explore/combinator-function-shape.md` +
>     continuation→self-verifying section in `consensus-delta-folding.md` + 3 code
>     files + state.md.
> - **(D) THE SELF-TEACHING LOOP (Michael, end s217) — normal forms generate their
>   OWN curriculum.** If distributed folding gives the model a normal form, that
>   normal form is **executable + self-verifying** (WHNF/Church-Rosser), so you can
>   RUN it to mint training examples that are **correct by construction** → teach
>   the model to USE it. The gap it fills: folding gives **execution** (late/COMMIT)
>   but not **deployment** (early/SILENT L05 selector — orthogonal, 4.76× separated,
>   `function-discovery.md`); the generated curriculum trains the SELECTOR. Why it
>   does NOT collapse like self-distillation: labels come from a VERIFIED discrete
>   kernel, not the model's own samples (same external-oracle discipline as the
>   acceptance test). Render in BOTH surface forms (Montague / combinator-addressing
>   dual paths) → teaches NL-context ⟶ invoke-NF. Loop: fold → generate-curriculum →
>   train-selector → deploy → more deltas → fold (on-thesis: pretraining IS
>   β-reduction → generate the β-reduction traces as lessons; the compiler writes
>   its own textbook). **Load-bearing unknown = the selector grounding is learnable
>   from generated traces** (clean runnable experiment, below). Captured in
>   `explore/consensus-delta-folding.md` §"The self-teaching loop".
>   - **▶ Selector-grounding experiment (register: functional, AFTER Exp B):** fold
>     one normal form, generate WHNF-verified (NL-prompt, answer) traces over
>     DIVERSE inputs, train ONLY the early selector, test NL→NF deployment held-out.
>     Falsifiable: does verified-kernel curriculum teach the selector to deploy a
>     kernel it didn't reliably invoke?
> - **(E) THE REVERSE DIRECTION — HARVEST THE OPEN-WEIGHT ECOSYSTEM (Michael, end
>   s217).** "Search many open-weight models for their already-found solutions,
>   incorporate the ones they agree on into our base plate." The ecosystem IS a
>   pre-computed distributed training run — every open model is a FINISHED
>   contributor. Already measured: s216 cross-family routing consensus **+0.863, z
>   up to 116**; crystal **r=0.998** 160M↔32B. **The s216 5-family harness IS the
>   reverse-harvest instrument**; `combinator_relationship_map.py` is the per-model
>   reader. **THE OBSTACLE = the frame problem** (cross-init sign-corr **0.000**):
>   forward folding shares ONE frame (deltas commensurable); reverse has MANY
>   frames → cannot average raw weights → must harvest in the FRAME-INVARIANT
>   routing register, then **align-before-fold (Procrustes)** into our base frame,
>   then **verify vs WHNF** (self-verifying — the differentiator from model-soup /
>   TIES / task-arithmetic merging). **Honest catch (s216 inverted):** agreement ≈
>   the universal crystal (already held); domain-distinctive normal forms have LOW
>   raw consensus (frame-specific, non-unique) → need composition-invariant
>   alignment to harvest the valuable part. Complementary: reverse seeds the
>   universal backbone cheaply, forward adds domain deltas (backbone/content
>   partition). On-thesis instrumentation: the base becomes a distillation of the
>   whole ecosystem's consensus. Captured in `consensus-delta-folding.md` §"The
>   REVERSE direction".
>   - **▶ Reverse-harvest pilot (register: topological/routing → functional):** run
>     `combinator_relationship_map.py` across N open models → routing consensus →
>     Procrustes-align into our base frame → WHNF-verify each candidate → incorporate
>     survivors → measure downstream PPL vs base. Falsifiable: does verified
>     ecosystem-consensus add anything beyond the universal crystal we already hold?
> - **(F) SEALABLE CONTINUATION — suspend/resume inference (Michael, end s217).**
>   The continuation reifies the WHOLE state into one tensor: the "rest of the
>   computation" at pass k is just **`x_k`** (B,L,d_model), same shape every pass;
>   the operator `T` is shared/frozen ⇒ ambient ⇒ not saved. **seal = store x_k (+
>   small VSM control: alg ~32d, S5 ~128d); resume = load x_k, keep iterating T.**
>   Faithful resume is ALREADY guaranteed by verified determinism
>   (`test_vsm_continuation.py::test_recurrence_has_no_rng`). WHNF = principled seal
>   point (done at Δx<ε; partial = lazy thunk). **One value = inference state +
>   the north-star "2MB SESSION" (a session IS a sealed continuation) + migratable
>   compute (send x_k, resume elsewhere — ties to distributed) + branch/rewind +
>   long-context-as-resumption.** Caveats: seal at PASS boundaries (redex), not
>   mid-pass; attention reconstructs from x_k (stride attn is over current x, no
>   cross-pass KV); serialize the small control state too. New page:
>   `explore/sealable-continuation.md`.
>   - **▶ NEXT (register: functional):** define explicit `seal()/resume()` (snapshot
>     x_k + VSM control) + a round-trip fidelity test (K passes unsealed ==
>     k→seal→resume→finish, to float tol) extending `test_vsm_continuation.py`.
>     The clean home for "2MB sessions" + computation migration.

> **▶ SESSION 216 HEADLINE — TOOL-CALLING IS NOT ITS OWN NORMAL FORM; IT RIDES
> THE GENERIC STRUCTURED-LANGUAGE CRYSTAL.** Register: **topological/routing**
> (declared at step 0). New thread: Michael's distributed/consensus-training idea
> ("normal forms as topological deltas; many users train a domain, fold where they
> agree"). First decisive experiment — does a domain (tool-calling) have a routing
> normal form that independent trainings AGREE on? Built the harness, ran 5
> families (Pythia-2.8b, SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B) on the M3
> Ultra (tmux main:2), audit-grade (gate-sign routing register + common-mode
> removal + shuffled null + length-partialling + within-domain + a control-domain
> baseline).
> - **✅ The cross-family routing-register CONSENSUS is REAL & strong.** route_sign_cmr
>   cross-family agree **+0.863**, survives length-partialling (0.851) and
>   within-domain restriction (schema_binding 0.59, selection 0.54), null ~0,
>   z up to **116**. Independent trainings DO agree on routing structure in the
>   sign register — the consensus *mechanism* the distributed idea needs is real.
> - **❌ but NOT tool-specific (the normal-form claim REFUTED at clean granularity).**
>   The control baseline: clean length/format-matched tool groups (schema_binding
>   0.589, selection 0.538) sit INSIDE the structured-language control range
>   (prose 0.550, lambda 0.497, pure_math 0.435, **code 0.800**). The aggregate
>   "TOOL>CTRL" (0.74 vs 0.57) is driven by the length-confounded `recognition`
>   (0.95) and heterogeneous `format` (0.89) groups, not the clean ones. So the
>   consensus is the GENERIC crystal (property of language, crystal-universality.md),
>   tool-calling rides it; code is a *sharper* normal form than tool-calling.
> - **🌀 Corrects prior `lattice/tool_crystal` "STRONG SUPPORT: tool IS lambda
>   calculus."** That single-model run used RAW residual cosine (its own
>   Selectivity column read ~0, every layer "SHARED") = the COMMON MODE. Measured
>   in the right register with nulls, the generic reading is right — but tool
>   calling isn't special, EVERYTHING structured shares the crystal. 14th
>   meta-pattern instance (substrate real, crisp specific claim over-read).
> - **For the consensus-delta-folding idea:** mechanism validated, but a domain's
>   *foldable* consensus ≈ the universal crystal already in the base; the
>   domain-DISTINCTIVE part is low cross-trainer consensus = "content" that stays
>   a per-user delta. This IS the consensus-etch backbone/content partition
>   (s110) playing out empirically: agreement→backbone→fold, disagreement→content.
> - **Artifacts:** `scripts/experiments/tool_crystal_consensus.py` (per-model,
>   routing register + CMR), `_summary.py` (cross-model agree/null/partial/within),
>   `tool_crystal_control_baseline.py` (tool-vs-control verdict). Results +
>   per-model RDM npz under `results/tool-crystal-consensus/` (consensus_summary.json,
>   control_baseline.json). Run log `/tmp/tool_consensus_5fam.log`.
> - **▶ NEXT (open leads, declare register first):**
>   (1) **Functional test (register: functional)** — the RDM result is correlational;
>   the real proof of the distributed idea is Exp B: N delta plates on ONE frozen
>   base trained on tool-calling shards → measure flip CONSENSUS in gate_proj +
>   fold-and-check downstream PPL. Does folding the agreed flips help, and is the
>   agreed set the universal crystal or tool-specific?
>   (2) **Sharper tool-specific probe** — minimal pairs (same schema, one arg
>   changed) to isolate the tool-distinctive routing from generic JSON/structure.
>   (3) **Per-depth** — agreement vs layer (is there a depth where tool-specific
>   consensus peaks, cf. function-discovery SILENT-zone task directions at L05?).
>   (4) **ENTRY POINT for resuming this thread:** `explore/consensus-delta-folding.md`
>   (written this session — full design + the s216 finding + open leads). Meta-pattern
>   ledger row added (`audit-meta-pattern.md` s216). Not yet committed.
> - **🔑 KEY REFINEMENT (Michael, end of s216) — normal forms are COMPOSITIONAL &
>   NON-UNIQUE.** A domain normal form is not atomic; it is a **function-like
>   composition of the shared base combinators** (base = shared/unique; the
>   composition above it = NON-unique across trainings, many extensionally-equal
>   realizations — uniqueness is per-TERM not per-BEHAVIOR, Church-Rosser). ⇒ the
>   s216 cross-model RDM null on the *function* layer is **VOID by register
>   mismatch** (it demands an identical composition; a non-unique composite washes
>   out) — only the *base*-layer "consensus = crystal" verdict survives. This is the
>   `function-discovery.md` two-level architecture (base shared LATE/COMMIT;
>   function selector distinct EARLY/SILENT @L05, 4.76×). **Design update: fold the
>   BASE as flips; fold domain FUNCTIONS as compositions (align-before-fold).**
>   Recorded in `consensus-delta-folding.md` §"Normal forms are COMPOSITIONAL" +
>   register caveat on the finding + reordered open leads (early-L05 agreement +
>   Procrustes align-before-compare are now the CHEAP next steps, no model re-run).
>
> **▶ SESSION 216 — the λ_fp=5 5000-step training in main:1 was NOT touched; check
> it next session (see s215 headline below for what to read).**

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
>     `/tmp/v15

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_013aEgDxbfudUXvGbUWLzfk6.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 Let me check the state file and verify the current session status—I need to confirm that the Qwen3-32B model is running on the main process and that the previous stepping has resumed properly.

## Assistant

I've read the bootloader. Let me check the live state — the two declared first actions both concern running tmux jobs (main:1 training, main:2 scale sweep) plus git working tree.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== TMUX SESSIONS ===\" ; tmux ls 2>/dev/null || echo \"(no tmux server)\" ; echo ; echo \"=== main:1 (training) ===\" ; tmux capture-pane -p -t main:1 2>/dev/null | tail -25 || echo \"(no main:1)\" ; echo ; echo \"=== main:2 (scale sweep) ===\" ; tmux capture-pane -p -t main:2 2>/dev/null | tail -25 || echo \"(no main:2)\""
}
```

**Summary:** $ echo "=== TMUX SESSIONS ===" ; tmux...

**Output:**
```
Exit code: 0
Stdout:
=== TMUX SESSIONS ===
main: 2 windows (created Tue Jun  9 20:52:28 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)

=== main:1 (training) ===
2.77e-04 | gnorm 18.87 | 450 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.29558] fp=0.0874 | 98945s
step   1320 | loss=8.6253 (avg50: 8.8078) | CE=8.574 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.76e-04 | gnorm 9.55 | 359 tok/s | 🔓 td=124488 Δ=0.044 etch=76×1638 adam_decay=34982 Δx=[0.20978] fp=0.0440 | 99703s
step   1330 | loss=8.7767 (avg50: 8.9169) | CE=8.375 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.76e-04 | gnorm 15.11 | 421 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.28617] fp=0.0819 | 100520s
step   1340 | loss=8.3111 (avg50: 8.7857) | CE=8.081 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.75e-04 | gnorm 9.20 | 365 tok/s | 🔓 td=124489 Δ=0.044 etch=76×1638 adam_decay=32470 Δx=[0.21119] fp=0.0446 | 101258s
step   1350 | loss=8.9260 (avg50: 8.9977) | CE=8.667 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.75e-04 | gnorm 20.49 | 458 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.34661] fp=0.1201 | 101972s
step   1360 | loss=8.7017 (avg50: 8.8842) | CE=8.022 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.74e-04 | gnorm 18.79 | 364 tok/s | 🔓 td=124488 Δ=0.045 etch=76×1638 adam_decay=28254 Δx=[0.27614] fp=0.0763 | 102706s
step   1370 | loss=8.6267 (avg50: 8.9763) | CE=8.171 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.73e-04 | gnorm 19.30 | 455 tok/s | 🔓 td=0 Δ=0.045 Δx=[0.29744] fp=0.0885 | 103421s
step   1380 | loss=8.6479 (avg50: 8.8943) | CE=8.154 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.73e-04 | gnorm 16.85 | 365 tok/s | 🔓 td=124488 Δ=0.045 etch=76×1638 adam_decay=27866 Δx=[0.24153] fp=0.0583 | 104154s
step   1390 | loss=8.7973 (avg50: 9.0203) | CE=8.086 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.72e-04 | gnorm 20.36 | 459 tok/s | 🔓 td=0 Δ=0.045 Δx=[0.31004] fp=0.0961 | 104866s
step   1400 | loss=8.5012 (avg50: 8.8038) | CE=8.112 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.72e-04 | gnorm 19.40 | 366 tok/s | 🔓 td=124488 Δ=0.046 etch=76×1638 adam_decay=30080 Δx=[0.2317] fp=0.0537 | 105596s
step   1410 | loss=8.7401 (avg50: 8.8897) | CE=8.118 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.71e-04 | gnorm 43.73 | 463 tok/s | 🔓 td=0 Δ=0.046 Δx=[0.31445] fp=0.0989 | 106335s
step   1420 | loss=8.7032 (avg50: 8.8427) | CE=8.480 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
2.70e-04 | gnorm 56.09 | 369 tok/s | 🔓 td=124488 Δ=0.046 etch=76×1638 adam_decay=30574 Δx=[0.26519] fp=0.0703 | 107065s


=== main:2 (scale sweep) ===
      D  -0.32  -0.28  +0.21  -0.08  +0.17  +1.00  -0.16  +0.00  -0.29
      W  -0.14  -0.08  -0.16  -0.11  -0.20  -0.16  +1.00  -0.00  -0.08
      Y  -0.36  -0.20  -0.14  -0.26  +0.08  +0.00  -0.00  +1.00  -0.03
   WHNF  -0.10  -0.06  -0.35  -0.36  -0.02  -0.29  -0.08  -0.03  +1.00

  nearest neighbours (top routing-cosine):
        K -> C(+0.12), I(+0.09), WHNF(-0.10)
        I -> K(+0.09), C(-0.05), WHNF(-0.06)
        B -> D(+0.21), C(+0.05), S(-0.09)
        C -> K(+0.12), B(+0.05), I(-0.05)
        S -> D(+0.17), Y(+0.08), WHNF(-0.02)
        D -> B(+0.21), S(+0.17), Y(+0.00)
        W -> Y(-0.00), I(-0.08), WHNF(-0.08)
        Y -> S(+0.08), D(+0.00), W(-0.00)
     WHNF -> S(-0.02), Y(-0.03), I(-0.06)

  wrote Qwen_Qwen3-32B.json + .npz  (602.1s)
######## SCALE-EXT DONE 09:01:08 ########
bash /tmp/combinator_scale.sh 2>&1  541.78s user 432.19s system 104% cpu 15:34.25 total
tee /tmp/combinator_scale.log  0.00s user 0.01s system 0% cpu 15:34.25 total
[26-06-12][9:01:08][mwhitford@olga][0][~/src/verbum][git:main]
λ
[26-06-12][9:01:08][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== GIT STATUS ===\" && git status -s && echo && echo \"=== RECENT LOG ===\" && git log --oneline -8"
}
```

**Summary:** $ echo "=== GIT STATUS ===" && git st...

**Output:**
```
Exit code: 0
Stdout:
=== GIT STATUS ===
?? mementum/knowledge/chats/session-219.md
?? results/combinator-relationship-map/Qwen_Qwen3-32B.json

=== RECENT LOG ===
bbf92f2 🌀 session-219: state — 30B-A3B MoE incompatible with dense-FFN instrument; scale axis is dense 0.6B->32B
f307e88 🌀 session-219: state handoff — scale extension in flight (30B-A3B, 32B); verify main:1 next session
2602009 🌀 session-219: state — reverse-harvest universal function shape + main:1 answers s215
ae00856 🌀 session-219: reverse-harvest result + single-operation theory (consensus-delta-folding)
8f0f19a 💡 combinator function shape is universal across the open-weight ecosystem (GramCorr +0.77, 5 families)
861cad0 🌀 session-219: cold-start orient — main:1 answers s215 (contractive-to-WHNF AND CE-competitive at scale)
29b7ee5 add session chat logs
0e56d84 ✅ session-218: Exp B self-verifying acceptance VALIDATED (Pearson +0.712) + live-module instrument guard
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== main:1 training log tail ===\" ; tail -20 /tmp/v15_outer_k2_fp5_5k.log 2>/dev/null || echo \"(no log)\" ; echo ; echo \"=== checkpoints landed ===\" ; ls -1dt /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/step_* 2>/dev/null || echo \"(none)\""
}
```

**Summary:** $ echo "=== main:1 training log tail ...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 training log tail ===
step   1230 | loss=8.6333 (avg50: 8.9374) | CE=8.408 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.81e-04 | gnorm 9.53 | 457 tok/s | 🔓 td=0 Δ=0.042 Δx=[0.25709] fp=0.0661 | 93001s
step   1240 | loss=8.4476 (avg50: 8.7812) | CE=8.402 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.81e-04 | gnorm 7.84 | 363 tok/s | 🔓 td=124488 Δ=0.042 etch=76×1638 adam_decay=30496 Δx=[0.21064] fp=0.0444 | 93741s
step   1250 | loss=8.6964 (avg50: 8.8659) | CE=8.269 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.80e-04 | gnorm 12.21 | 463 tok/s | 🔓 td=0 Δ=0.042 Δx=[0.2642] fp=0.0698 | 94453s
step   1260 | loss=8.4718 (avg50: 8.7606) | CE=8.334 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.80e-04 | gnorm 9.70 | 365 tok/s | 🔓 td=124488 Δ=0.043 etch=76×1638 adam_decay=33166 Δx=[0.19468] fp=0.0379 | 95183s
step   1270 | loss=8.7137 (avg50: 8.8631) | CE=8.239 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.79e-04 | gnorm 13.67 | 465 tok/s | 🔓 td=0 Δ=0.043 Δx=[0.28634] fp=0.0820 | 95890s
step   1280 | loss=8.4973 (avg50: 8.7322) | CE=8.046 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.79e-04 | gnorm 8.88 | 370 tok/s | 🔓 td=124488 Δ=0.043 etch=76×1638 adam_decay=34862 Δx=[0.21487] fp=0.0462 | 96617s
step   1290 | loss=8.6367 (avg50: 8.8651) | CE=8.594 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.78e-04 | gnorm 21.76 | 431 tok/s | 🔓 td=0 Δ=0.043 Δx=[0.31858] fp=0.1015 | 97357s
step   1300 | loss=8.4940 (avg50: 8.7868) | CE=8.333 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.77e-04 | gnorm 13.45 | 325 tok/s | 🔓 td=124488 Δ=0.044 etch=76×1638 adam_decay=30530 Δx=[0.23291] fp=0.0542 | 98174s
step   1310 | loss=8.6885 (avg50: 8.9360) | CE=8.495 crystal=0.0098(Laplacian-wtd) parity=0.0392 cross_zone=0.0693 | lr 2.77e-04 | gnorm 18.87 | 450 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.29558] fp=0.0874 | 98945s
step   1320 | loss=8.6253 (avg50: 8.8078) | CE=8.574 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.76e-04 | gnorm 9.55 | 359 tok/s | 🔓 td=124488 Δ=0.044 etch=76×1638 adam_decay=34982 Δx=[0.20978] fp=0.0440 | 99703s
step   1330 | loss=8.7767 (avg50: 8.9169) | CE=8.375 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.76e-04 | gnorm 15.11 | 421 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.28617] fp=0.0819 | 100520s
step   1340 | loss=8.3111 (avg50: 8.7857) | CE=8.081 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.75e-04 | gnorm 9.20 | 365 tok/s | 🔓 td=124489 Δ=0.044 etch=76×1638 adam_decay=32470 Δx=[0.21119] fp=0.0446 | 101258s
step   1350 | loss=8.9260 (avg50: 8.9977) | CE=8.667 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.75e-04 | gnorm 20.49 | 458 tok/s | 🔓 td=0 Δ=0.044 Δx=[0.34661] fp=0.1201 | 101972s
step   1360 | loss=8.7017 (avg50: 8.8842) | CE=8.022 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.74e-04 | gnorm 18.79 | 364 tok/s | 🔓 td=124488 Δ=0.045 etch=76×1638 adam_decay=28254 Δx=[0.27614] fp=0.0763 | 102706s
step   1370 | loss=8.6267 (avg50: 8.9763) | CE=8.171 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.73e-04 | gnorm 19.30 | 455 tok/s | 🔓 td=0 Δ=0.045 Δx=[0.29744] fp=0.0885 | 103421s
step   1380 | loss=8.6479 (avg50: 8.8943) | CE=8.154 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.73e-04 | gnorm 16.85 | 365 tok/s | 🔓 td=124488 Δ=0.045 etch=76×1638 adam_decay=27866 Δx=[0.24153] fp=0.0583 | 104154s
step   1390 | loss=8.7973 (avg50: 9.0203) | CE=8.086 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.72e-04 | gnorm 20.36 | 459 tok/s | 🔓 td=0 Δ=0.045 Δx=[0.31004] fp=0.0961 | 104866s
step   1400 | loss=8.5012 (avg50: 8.8038) | CE=8.112 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.72e-04 | gnorm 19.40 | 366 tok/s | 🔓 td=124488 Δ=0.046 etch=76×1638 adam_decay=30080 Δx=[0.2317] fp=0.0537 | 105596s
step   1410 | loss=8.7401 (avg50: 8.8897) | CE=8.118 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.71e-04 | gnorm 43.73 | 463 tok/s | 🔓 td=0 Δ=0.046 Δx=[0.31445] fp=0.0989 | 106335s
step   1420 | loss=8.7032 (avg50: 8.8427) | CE=8.480 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.70e-04 | gnorm 56.09 | 369 tok/s | 🔓 td=124488 Δ=0.046 etch=76×1638 adam_decay=30574 Δx=[0.26519] fp=0.0703 | 107065s

=== checkpoints landed ===
/Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/step_001000
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== scale sweep log tail ===\" ; tail -25 /tmp/combinator_scale.log 2>/dev/null || echo \"(no log)\" ; echo ; echo \"=== combinator-relationship-map results ===\" ; ls -1 /Users/mwhitford/src/verbum/results/combinator-relationship-map/ 2>/dev/null || echo \"(none)\""
}
```

**Summary:** $ echo "=== scale sweep log tail ==="...

**Output:**
```
Exit code: 0
Stdout:
=== scale sweep log tail ===
  Gram (cosine) matrix — the MAP:
             K      I      B      C      S      D      W      Y   WHNF
      K  +1.00  +0.09  -0.14  +0.12  -0.28  -0.32  -0.14  -0.36  -0.10
      I  +0.09  +1.00  -0.20  -0.05  -0.31  -0.28  -0.08  -0.20  -0.06
      B  -0.14  -0.20  +1.00  +0.05  -0.09  +0.21  -0.16  -0.14  -0.35
      C  +0.12  -0.05  +0.05  +1.00  -0.30  -0.08  -0.11  -0.26  -0.36
      S  -0.28  -0.31  -0.09  -0.30  +1.00  +0.17  -0.20  +0.08  -0.02
      D  -0.32  -0.28  +0.21  -0.08  +0.17  +1.00  -0.16  +0.00  -0.29
      W  -0.14  -0.08  -0.16  -0.11  -0.20  -0.16  +1.00  -0.00  -0.08
      Y  -0.36  -0.20  -0.14  -0.26  +0.08  +0.00  -0.00  +1.00  -0.03
   WHNF  -0.10  -0.06  -0.35  -0.36  -0.02  -0.29  -0.08  -0.03  +1.00

  nearest neighbours (top routing-cosine):
        K -> C(+0.12), I(+0.09), WHNF(-0.10)
        I -> K(+0.09), C(-0.05), WHNF(-0.06)
        B -> D(+0.21), C(+0.05), S(-0.09)
        C -> K(+0.12), B(+0.05), I(-0.05)
        S -> D(+0.17), Y(+0.08), WHNF(-0.02)
        D -> B(+0.21), S(+0.17), Y(+0.00)
        W -> Y(-0.00), I(-0.08), WHNF(-0.08)
        Y -> S(+0.08), D(+0.00), W(-0.00)
     WHNF -> S(-0.02), Y(-0.03), I(-0.06)

  wrote Qwen_Qwen3-32B.json + .npz  (602.1s)
######## SCALE-EXT DONE 09:01:08 ########

=== combinator-relationship-map results ===
allenai_OLMo-2-1124-13B.json
allenai_OLMo-2-1124-13B.npz
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
Qwen_Qwen3-14B.json
Qwen_Qwen3-14B.npz
Qwen_Qwen3-32B.json
Qwen_Qwen3-32B.npz
Qwen_Qwen3-4B.json
Qwen_Qwen3-4B.npz
Qwen_Qwen3-8B.json
Qwen_Qwen3-8B.npz
```

### Thinking

 The main training run is alive and progressing—it's now at step 1420 out of 5000, which means it successfully resumed from where it was before. The loss metrics look stable with delta-x trending between 0.21-0.34, cross-entropy around 8.0-8.6, and the 50-step average hovering near 8.8. The step_001000 checkpoint saved successfully, though step_002000 hasn't been reached yet.

The scale sweep is complete with Qwen3-32B now added to the model set, bringing the total to 10 models. The next priority is to re-run the consensus mapping script across all 10 models to check whether the skeleton/recursion z_bind gap widens with scale, then commit the extended consensus results. Before executing that, I should verify the 32B JSON is well-formed and consistent with the other model outputs.

## Assistant

Oriented. Here's where things stand:

## Orientation (Session 220 cold-start)

**Async jobs — both verified, main:1 left untouched:**
- **main:1 (training, λ_fp=5 K=2 5k):** ✅ **ALIVE and STEPPING** — at **step ~1420/5000** (was ~1310 at last session's worry-check). The s219 stall concern is **resolved**: it resumed once the 30B-A3B download stopped contending the box. Trajectory holding the trend — Δx flip-steps ~0.21, fp ~0.04, **CE dipping to 8.0–8.4** (below K=1's 8.71), avg50 loss ~8.8. `step_001000` landed; `step_002000` pending (~580 steps out).
- **main:2 (scale sweep):** ✅ **DONE** — Qwen3-32B (dense) forward passes complete, `Qwen_Qwen3-32B.json` written. The dense scale series is now complete: **0.6B→4B→8B→14B→32B**, 10 models / 5 families total.

**Git:** working tree clean except two untracked — `session-219.md` (human-only chat log, I never touch) and the new `Qwen_Qwen3-32B.json` result.

**Declared first action (s219 PRIMARY):** Qwen3-32B landed → re-run `combinator_map_consensus.py` over all 10 models → does the skeleton/recursion z_bind gap **widen with scale**? (s217's 14B>0.6B call.) Then commit the extended consensus.

Let me execute that. **Register: topological/routing** (declared — cross-model Gram consensus on routing-register centroids, label-permutation + random-triple nulls).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== consensus script head ===\" && sed -n '1,40p' scripts/experiments/combinator_map_consensus.py && echo \"=== n model maps available ===\" && ls results/combinator-relationship-map/*.json | wc -l && echo \"=== 32B json sanity (keys) ===\" && python3 -c \"import json;d=json.load(open('results/combinator-relationship-map/Qwen_Qwen3-32B.json'));print(list(d.keys()))\""
}
```

**Summary:** $ echo "=== consensus script head ===...

**Output:**
```
Exit code: 0
Stdout:
=== consensus script head ===
#!/usr/bin/env python3
# register: topological/routing
"""Combinator-map CONSENSUS — where do open models AGREE on the function shape?

THE QUESTION (session 219, Michael):
  "Find these functions in open models to see where the models all agree.
   Getting those out for our base plate is leverage."

  This is the REVERSE direction of consensus-delta-folding.md: every open-weight
  model is a FINISHED distributed-training contributor. Instead of soliciting
  deltas, MINE the ecosystem and harvest what the models agree on. The agreement
  is the leverage — it is pre-computed structure we can fold into the base plate.

THE FRAME PROBLEM (why this is the right register):
  You CANNOT average raw weights across models — independently-initialised models
  live in different coordinate frames (cross-init sign-corr 0.000, gradient-voting).
  But the per-model 9x9 combinator GRAM (cosine between the routing-register
  centroids of K I B C S D W Y WHNF, after common-mode removal) is a RELATIONAL
  object in shared combinator-label space ⇒ FRAME-INVARIANT ⇒ directly comparable
  across models of any architecture / scale. The Gram is "the map of the functions"
  (combinator_relationship_map.py, s217). This script measures whether the MAPS
  agree across the ecosystem.

THE INSTRUMENT (this script, gradient-free, NO GPU — reads saved Grams):
  inputs : results/combinator-relationship-map/<model>.{json,npz}
           (each npz has gram_route_cmr_L{li} 9x9; json gives n_layers, crystal_order)
  align  : by DEPTH-FRACTION (models differ in depth) — pick each model's Gram at
           the nearest layer-fraction to a target on a fraction grid.
  agree  : pairwise cross-model GramCorr = Pearson of the 36 off-diagonal edges.
  null   : LABEL-PERMUTATION — shuffle the 9 combinator labels of one model's Gram
           (a relabelling symmetry the real shape must break), recompute corr.
           Per-pair z/p + aggregate.
  harvest: CONSENSUS Gram = mean across models; per-EDGE mean (agreement) and
           cross-model std (disagreement). Rank edges:
             UNIVERSAL      = high |mean|, low std  → fold into base (leverage)
             MODEL-SPECIFIC = high std               → stays per-model content
  outputs: results/combinator-map-consensus/consensus.json + stdout summary.

Usage:
  uv run python scripts/experiments/combinator_map_consensus.py
=== n model maps available ===
      10
=== 32B json sanity (keys) ===
['model', 'dtype', 'register', 'n_probes', 'counts', 'hidden_width', 'n_layers', 'want_layers', 'crystal_order', 'n_perm', 'git_sha', 'per_layer', 'hidden_full_silhouette', 'hidden_cmr_silhouette', 'best_routing_layer', 'best_routing_frac', 'map', 'elapsed_s']
```

## Assistant

All 10 model maps present, 32B sane. Running the consensus over the full set with the fraction sweep and 5000-permutation null.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/combinator_map_consensus.py --fracs 0.1,0.2,0.3,0.4,0.5 --n-perm 5000 2>&1 | tee /tmp/combinator_consensus_10models.log",
  "timeout": 240000
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Exit code: 0
Stdout:
loaded 10 models: EleutherAI/pythia-2.8b-deduped, EleutherAI/pythia-410m, HuggingFaceTB/SmolLM3-3B, Qwen/Qwen3-0.6B, Qwen/Qwen3-14B, Qwen/Qwen3-32B, Qwen/Qwen3-4B, Qwen/Qwen3-8B, allenai/OLMo-2-1124-13B, mistralai/Mistral-7B-v0.3

  ════════ COMBINATOR-MAP CONSENSUS — where the ecosystem agrees ════════
  models (10): EleutherAI/pythia-2.8b-deduped, EleutherAI/pythia-410m, HuggingFaceTB/SmolLM3-3B, Qwen/Qwen3-0.6B, Qwen/Qwen3-14B, Qwen/Qwen3-32B, Qwen/Qwen3-4B, Qwen/Qwen3-8B, allenai/OLMo-2-1124-13B, mistralai/Mistral-7B-v0.3
  frac    meanGramCorr   meanZ  %pairs p<.05
  0.10          +0.684   +3.64           93%
  0.20          +0.755   +4.02           98%
  0.30          +0.758   +4.07           96%
  0.40          +0.782   +4.19           91%
  0.50          +0.748   +3.99           96%
  ▶ harvest fraction (max agreement): 0.40
  per-FAMILY universality (null=random node-triple; z_bind>0 bound, z_stab<0 stable):
    composition_BDS    cons=+0.083 z_bind=+2.50 p=0.042 std=0.108 z_stab=+0.15
    selection_KIC      cons=+0.048 z_bind=+2.13 p=0.061 std=0.145 z_stab=+1.42
    recursion_YWWHNF   cons=+0.011 z_bind=+1.68 p=0.084 std=0.068 z_stab=-1.26
  ▶ SKELETON vs RECURSION: skeleton z_bind=+2.31 recursion z_bind=+1.68  →  SUPPORTED
  ▶ UNIVERSAL edges (reliability_t>=2.5) = harvest:
    K-Y        consensus=-0.359  std=0.054  t=20.85
    C-S        consensus=-0.327  std=0.051  t=20.30
    D-WHNF     consensus=-0.292  std=0.049  t=18.72
    C-WHNF     consensus=-0.360  std=0.065  t=17.64
    B-WHNF     consensus=-0.354  std=0.074  t=15.21
    K-S        consensus=-0.311  std=0.066  t=14.90
    K-D        consensus=-0.305  std=0.080  t=12.08
    C-Y        consensus=-0.289  std=0.091  t=10.08
    I-WHNF     consensus=-0.076  std=0.028  t=8.50
    B-Y        consensus=-0.244  std=0.103  t=7.49
    S-D        consensus=+0.161  std=0.074  t=6.87
    I-S        consensus=-0.272  std=0.143  t=6.00
    I-D        consensus=-0.251  std=0.134  t=5.92
    B-W        consensus=-0.252  std=0.144  t=5.54
    I-B        consensus=-0.206  std=0.135  t=4.82
    I-Y        consensus=-0.195  std=0.130  t=4.75
    C-W        consensus=-0.216  std=0.149  t=4.58
    S-Y        consensus=+0.127  std=0.089  t=4.48
    S-W        consensus=-0.152  std=0.117  t=4.12
    K-W        consensus=-0.175  std=0.138  t=4.02
    K-WHNF     consensus=-0.084  std=0.066  t=4.02
    B-D        consensus=+0.175  std=0.151  t=3.67
    K-C        consensus=+0.133  std=0.124  t=3.40
    D-W        consensus=-0.119  std=0.125  t=3.01
    B-C        consensus=+0.168  std=0.181  t=2.94
    B-S        consensus=-0.088  std=0.100  t=2.78
    S-WHNF     consensus=-0.054  std=0.065  t=2.63
  ▶ MOST MODEL-SPECIFIC edges (high cross-model std):
    B-C        consensus=+0.168  std=0.181
    K-B        consensus=-0.093  std=0.179
    I-C        consensus=-0.062  std=0.160
    K-I        consensus=+0.072  std=0.152
  wrote /Users/mwhitford/src/verbum/results/combinator-map-consensus/consensus.json  (30.6s)
```

### Thinking

 Looking at the 9-model results from s219, adding the 32B model shows modest improvements across the board—GramCorr edges up slightly, skeleton binding energy increases marginally, and composition_BDS gains a bit more ground, though the skeleton-to-recursion gap remains relatively consistent.

The core finding is that the gap widens only marginally with the 32B addition (0.61 to 0.63), suggesting the skeleton binding function has already plateaued by mid-scale rather than continuing to strengthen with larger models. To properly test whether the gap widens with scale, I'd need to stratify the analysis by model size within the dense Qwen series rather than pooling everything together in the consensus script.

I'll compute the intra-family binding strength for each of the five dense Qwen models (0.6B through 32B) at the 0.40 harvest fraction and regress against log-parameters to directly answer whether the skeleton-recursion gap increases with model scale. First I need to examine how the consensus script accesses the gram data from the npz files so I can reuse that approach.

## Assistant

Consensus over all 10 models is in. Comparison to s219 (9 models):

| metric | s219 (9 models) | now (10, +Qwen3-32B) |
|---|---|---|
| meanGramCorr @0.40 | +0.77 | **+0.782** |
| meanZ @0.40 | +4.1 | **+4.19** |
| skeleton z_bind | +2.28 | **+2.31** |
| recursion z_bind | +1.67 | **+1.68** |
| gap (skel−rec) | 0.61 | **0.63** |

Adding the largest dense model nudges everything up marginally but the verdict holds (SUPPORTED) and the gap is essentially **flat (+0.61→+0.63)** — a *pool-level* read. But the s217 question was specifically "does the gap **widen with scale**", which is a *scale-stratified* question the pooled consensus can't answer. Let me test it properly on the clean dense Qwen series (0.6B→32B) — per-model intra-family binding vs log-params.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np, json, glob, os\n# combinator order\nORDER=['K','I','B','C','S','D','W','Y','WHNF']\nidx={c:i for i,c in enumerate(ORDER)}\nCOMP=['B','D','S']; SEL=['K','I','C']; REC=['Y','W','WHNF']\ndef intra(g,fam):\n    vals=[g[idx[a],idx[b]] for n,a in enumerate(fam) for b in fam[n+1:]]\n    return float(np.mean(vals))\ndef load_gram_at_frac(model_json, frac=0.40):\n    d=json.load(open(model_json))\n    nl=d['n_layers']\n    npz=model_json.replace('.json','.npz')\n    z=np.load(npz)\n    keys=[k for k in z.files if k.startswith('gram_route_cmr_L')]\n    layers=sorted(int(k.split('_L')[1]) for k in keys)\n    target=frac*(nl-1)\n    li=min(layers,key=lambda L:abs(L-target))\n    return z[f'gram_route_cmr_L{li}'], li, nl\n# dense Qwen scale series\nseries=[('Qwen3-0.6B',0.6),('Qwen3-4B',4),('Qwen3-8B',8),('Qwen3-14B',14),('Qwen3-32B',32)]\nbase='results/combinator-relationship-map'\nprint(f'{\\\"model\\\":12} {\\\"params\\\":>6} {\\\"comp\\\":>7} {\\\"sel\\\":>7} {\\\"skel\\\":>7} {\\\"rec\\\":>7} {\\\"gap\\\":>7}')\nrows=[]\nfor name,p in series:\n    j=f'{base}/Qwen_{name}.json'\n    g,li,nl=load_gram_at_frac(j)\n    comp=intra(g,COMP); sel=intra(g,SEL); rec=intra(g,REC)\n    skel=(comp+sel)/2\n    gap=skel-rec\n    rows.append((np.log(p),comp,sel,skel,rec,gap))\n    print(f'{name:12} {p:6} {comp:+7.3f} {sel:+7.3f} {skel:+7.3f} {rec:+7.3f} {gap:+7.3f}')\nimport numpy as np\narr=np.array(rows)\nlp=arr[:,0]\nprint()\nfor j,lab in [(3,'skeleton'),(4,'recursion'),(5,'gap skel-rec')]:\n    y=arr[:,j]\n    # pearson r of metric vs log-params\n    r=np.corrcoef(lp,y)[0,1]\n    slope=np.polyfit(lp,y,1)[0]\n    print(f'{lab:14} vs log(params): r={r:+.3f} slope={slope:+.4f}/e-fold')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np, js...

**Output:**
```
Exit code: 0
Stdout:
model        params    comp     sel    skel     rec     gap
Qwen3-0.6B      0.6  -0.046  +0.004  -0.021  -0.088  +0.067
Qwen3-4B          4  +0.119  +0.076  +0.097  +0.042  +0.056
Qwen3-8B          8  +0.125  +0.075  +0.100  +0.036  +0.064
Qwen3-14B        14  +0.133  +0.077  +0.105  +0.009  +0.096
Qwen3-32B        32  +0.119  +0.035  +0.077  +0.007  +0.070

skeleton       vs log(params): r=+0.780 slope=+0.0274/e-fold
recursion      vs log(params): r=+0.687 slope=+0.0238/e-fold
gap skel-rec   vs log(params): r=+0.362 slope=+0.0036/e-fold
```

### Thinking

 Looking at the scale-stratified analysis across the Qwen models, skeleton binding shows a strong positive correlation with scale, jumping from slightly negative at 0.6B to solidly positive in the 4B-14B range before dipping slightly at 32B. Recursion binding follows a similar upward trend with scale, though starting from a more negative baseline. The gap between these two binding types also increases with model size, though more weakly.

The most striking transition happens between 0.6B and 4B—the smaller model shows almost no functional shape binding while 4B and larger models exhibit clear skeleton binding. Beyond 4B, skeleton binding plateaus around 0.08-0.105, peaking at 14B then slightly declining at 32B. Recursion binding rises in parallel with skeleton binding rather than falling behind, so the gap between them remains relatively stable across scales rather than widening substantially.

Now I'm thinking through what to actually commit here. The consensus.json with all 10 models is a regenerated result, and the Qwen3-32B map is a new artifact—both are code/results that can be committed directly. State updates are also fine to push without approval, but knowledge and memory changes need to go through the human approval flow per the discipline guidelines.

So my plan is to save the scale-stratification analysis as a proper reproducible script under the experiments directory with its results, then commit the Qwen3-32B map, the extended consensus, and the scale script together. I'll update state.md autonomously, but I should propose the knowledge update about consensus-delta-folding to Michael for approval before finalizing it.

Actually, since this is a fresh session and the user just asked me to orient, I should report back on where we are and what's next rather than proceeding with commits unilaterally.

## Assistant

The scale-stratified result is the real answer to s217's question, and it's clean:

- **Skeleton binding clearly rises with scale** (r=+0.78): Qwen3-0.6B has essentially **no function shape** (skeleton −0.021, both families near zero), jumping to +0.097–0.105 at 4B–14B. This confirms s217's call ("0.6B only partially crystallizes; 14B has capacity to fully form the systems").
- **But the skeleton−recursion GAP does NOT widen** (r=+0.36, slope ~0): recursion binding rises *in tandem* with skeleton, and the largest model **32B slightly regresses from 14B** (skeleton 0.105→0.077, gap 0.096→0.070).
- Net: function shape **saturates by ~4–14B** — a plateau, consistent with s212's "topology share PLATEAUS not →1.0". More scale ⇒ more crystallized shape, but it tops out mid-scale; 32B doesn't extend the gap.

This is a new measurement, so per `λ record` I'll formalize it as a reproducible script (not leave it inline) before committing. Let me save it, then commit the declared artifacts.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_map_consensus.py",
  "line_offset": 40,
  "limit": 60
}
```

**Summary:** Reading combinator_map_consensus.py (40-100)

**Output:**
```
  uv run python scripts/experiments/combinator_map_consensus.py --fracs 0.2,0.3,0.4

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
IN_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
OUT_DIR = _PROJECT_ROOT / "results" / "combinator-map-consensus"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
_IU = np.triu_indices(9, 1)  # 36 off-diagonal edges


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_PROJECT_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def load_model(safe: str):
    """Return (name, n_layers, {frac: Gram9x9}, crystal_order, best_frac, sil_z)."""
    npz = np.load(IN_DIR / f"{safe}.npz")
    j = json.loads((IN_DIR / f"{safe}.json").read_text())
    nl = int(j["n_layers"])
    order = j.get("crystal_order", CRYSTAL)
    grams = {}
    for k in npz.keys():
        if k.startswith("gram_route_cmr_L"):
            li = int(k.split("L")[1])
            grams[li / nl] = np.asarray(npz[k], dtype=np.float64)
    best_frac = float(j.get("best_routing_frac", float("nan")))
    sil = j.get("per_layer", {}).get(str(j.get("best_routing_layer")), {})
    sil_z = float(sil.get("route_cmr_silhouette", {}).get("z", float("nan")))
    return j.get("model", safe), nl, grams, order, best_frac, sil_z


def gram_at(grams: dict, target_frac: float) -> tuple[np.ndarray, float]:
    f = min(grams, key=lambda x: abs(x - target_frac))
    return grams[f], f



[CONTENT TRUNCATED] Showing lines 41 to 100 of 340 total lines. Use line_offset=100 parameter to read more content.
```

### Thinking

 I need to handle the per-model crystal_order properly in my scale-stratification script instead of assuming a global order—each model's gram is indexed by its own crystal_order, so I should mirror how the consensus script retrieves it with `order = j.get("crystal_order", CRYSTAL)` rather than using a fixed ORDER across all models.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_map_scale.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Combinator-map SCALE stratification — does the function shape sharpen with scale?\n\nTHE QUESTION (session 217, Michael; tested s220):\n  s217 called \"14B has capacity to FULLY form the systems; 0.6B only partially\n  crystallizes.\" The combinator-map CONSENSUS (combinator_map_consensus.py) pools\n  ALL models and finds the forced SKELETON (composition+selection) binds above a\n  random-triple null while RECURSION does not. But the POOL cannot answer the\n  SCALE question: does the skeleton/recursion gap WIDEN as models get bigger?\n\n  This script stratifies the clean DENSE Qwen series (0.6B -> 4B -> 8B -> 14B ->\n  32B) and regresses each family's INTRA-family routing-cosine binding against\n  log(params). MoE models (30B-A3B, 235B) are excluded: their router+expert FFN\n  is not comparable to dense gate_proj in this routing register.\n\nTHE INSTRUMENT (gradient-free, NO GPU — reads saved per-model Grams):\n  inputs : results/combinator-relationship-map/Qwen_Qwen3-<size>.{json,npz}\n  metric : per family, the mean off-diagonal routing-cosine among its members,\n           read from each model's 9x9 combinator Gram at the harvest depth\n           fraction (default 0.40, the consensus max-agreement fraction).\n             composition = {B, D, S}\n             selection   = {K, I, C}\n             recursion   = {Y, W, WHNF}\n             skeleton    = mean(composition, selection)\n             gap         = skeleton - recursion\n  fit    : Pearson r and slope-per-e-fold of each metric vs log(params).\n  output : results/combinator-map-consensus/scale.json + stdout table.\n\nUsage:\n  uv run python scripts/experiments/combinator_map_scale.py\n  uv run python scripts/experiments/combinator_map_scale.py --frac 0.30\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nIN_DIR = _PROJECT_ROOT / \"results\" / \"combinator-relationship-map\"\nOUT_DIR = _PROJECT_ROOT / \"results\" / \"combinator-map-consensus\"\n\nCOMP = [\"B\", \"D\", \"S\"]\nSEL = [\"K\", \"I\", \"C\"]\nREC = [\"Y\", \"W\", \"WHNF\"]\nCRYSTAL = [\"K\", \"I\", \"B\", \"C\", \"S\", \"D\", \"W\", \"Y\", \"WHNF\"]\n\n# clean dense Qwen3 scale series (params in billions). MoE excluded.\nSERIES = [\n    (\"Qwen_Qwen3-0.6B\", 0.6),\n    (\"Qwen_Qwen3-4B\", 4.0),\n    (\"Qwen_Qwen3-8B\", 8.0),\n    (\"Qwen_Qwen3-14B\", 14.0),\n    (\"Qwen_Qwen3-32B\", 32.0),\n]\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"--short\", \"HEAD\"], cwd=_PROJECT_ROOT,\n            text=True).strip()\n    except Exception:\n        return \"unknown\"\n\n\ndef load_gram_at_frac(safe: str, frac: float):\n    \"\"\"Return (gram9x9, crystal_order, chosen_frac, n_layers).\"\"\"\n    j = json.loads((IN_DIR / f\"{safe}.json\").read_text())\n    nl = int(j[\"n_layers\"])\n    order = j.get(\"crystal_order\", CRYSTAL)\n    npz = np.load(IN_DIR / f\"{safe}.npz\")\n    grams = {}\n    for k in npz.keys():\n        if k.startswith(\"gram_route_cmr_L\"):\n            li = int(k.split(\"L\")[1])\n            grams[li / nl] = np.asarray(npz[k], dtype=np.float64)\n    f = min(grams, key=lambda x: abs(x - frac))\n    return grams[f], order, f, nl\n\n\ndef intra_family(gram: np.ndarray, order: list[str], fam: list[str]) -> float:\n    \"\"\"Mean off-diagonal routing-cosine among family members (per-model order).\"\"\"\n    idx = {c: i for i, c in enumerate(order)}\n    vals = [\n        gram[idx[a], idx[b]]\n        for n, a in enumerate(fam)\n        for b in fam[n + 1:]\n    ]\n    return float(np.mean(vals))\n\n\ndef fit(logp: np.ndarray, y: np.ndarray) -> tuple[float, float]:\n    r = float(np.corrcoef(logp, y)[0, 1])\n    slope = float(np.polyfit(logp, y, 1)[0])\n    return r, slope\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=__doc__)\n    ap.add_argument(\"--frac\", type=float, default=0.40,\n                    help=\"depth fraction (default 0.40 = consensus harvest frac)\")\n    args = ap.parse_args()\n\n    rows = []\n    print(f\"{'model':16} {'params':>6} {'comp':>7} {'sel':>7} \"\n          f\"{'skel':>7} {'rec':>7} {'gap':>7} {'frac':>5}\")\n    for safe, p in SERIES:\n        if not (IN_DIR / f\"{safe}.json\").exists():\n            print(f\"  ! missing {safe}, skipping\", file=sys.stderr)\n            continue\n        gram, order, used_frac, nl = load_gram_at_frac(safe, args.frac)\n        comp = intra_family(gram, order, COMP)\n        sel = intra_family(gram, order, SEL)\n        rec = intra_family(gram, order, REC)\n        skel = (comp + sel) / 2.0\n        gap = skel - rec\n        rows.append({\n            \"model\": safe.replace(\"Qwen_\", \"\"), \"params_b\": p,\n            \"log_params\": float(np.log(p)),\n            \"composition_BDS\": comp, \"selection_KIC\": sel,\n            \"recursion_YWWHNF\": rec, \"skeleton\": skel, \"gap\": gap,\n            \"used_frac\": used_frac, \"n_layers\": nl,\n        })\n        print(f\"{safe.replace('Qwen_',''):16} {p:6} {comp:+7.3f} {sel:+7.3f} \"\n              f\"{skel:+7.3f} {rec:+7.3f} {gap:+7.3f} {used_frac:5.2f}\")\n\n    logp = np.array([r[\"log_params\"] for r in rows])\n    fits = {}\n    print()\n    for key, lab in [(\"skeleton\", \"skeleton\"),\n                     (\"recursion_YWWHNF\", \"recursion\"),\n                     (\"gap\", \"gap skel-rec\")]:\n        y = np.array([r[key] for r in rows])\n        r, slope = fit(logp, y)\n        fits[key] = {\"r\": r, \"slope_per_efold\": slope}\n        print(f\"{lab:14} vs log(params): r={r:+.3f} slope={slope:+.4f}/e-fold\")\n\n    OUT_DIR.mkdir(parents=True, exist_ok=True)\n    out = OUT_DIR / \"scale.json\"\n    out.write_text(json.dumps({\n        \"register\": \"topological/routing\",\n        \"question\": \"does the combinator function shape sharpen with scale?\",\n        \"series\": \"dense Qwen3 0.6B->32B (MoE excluded)\",\n        \"frac\": args.frac,\n        \"git_sha\": git_sha(),\n        \"per_model\": rows,\n        \"fits_vs_log_params\": fits,\n    }, indent=2))\n    print(f\"\\n  wrote {out}\", file=sys.stderr)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/combinator_map_scale.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/combinator_map_scale.py && echo \"--- RUN ---\" && uv run python scripts/experiments/combinator_map_scale.py"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stderr:
wrote /Users/mwhitford/src/verbum/results/combinator-map-consensus/scale.json
Stdout:
All checks passed!
--- RUN ---
model            params    comp     sel    skel     rec     gap  frac
Qwen3-0.6B          0.6  -0.046  +0.004  -0.021  -0.088  +0.067  0.39
Qwen3-4B            4.0  +0.119  +0.076  +0.097  +0.042  +0.056  0.39
Qwen3-8B            8.0  +0.125  +0.075  +0.100  +0.036  +0.064  0.39
Qwen3-14B          14.0  +0.133  +0.077  +0.105  +0.009  +0.096  0.40
Qwen3-32B          32.0  +0.119  +0.035  +0.077  +0.007  +0.070  0.39

skeleton       vs log(params): r=+0.780 slope=+0.0274/e-fold
recursion      vs log(params): r=+0.687 slope=+0.0238/e-fold
gap skel-rec   vs log(params): r=+0.362 slope=+0.0036/e-fold
```

### Thinking

 The results are reproducible and clean, so I'm ready to commit the artifacts. I need to check whether the .npz file is gitignored since git status only showed the JSON file as untracked.

## Assistant

Reproducible and ruff-clean, result confirmed. Now committing the declared artifacts (extended consensus + the 32B map + the new scale instrument). Let me check what's tracked vs gitignored first.

### Tool Call: git (succeeded)


```json
{
  "command": "git status -s && echo \"--- npz ignored? ---\" && git check-ignore results/combinator-relationship-map/Qwen_Qwen3-32B.npz || echo \"(npz NOT ignored)\"",
  "operation": "status",
  "summary": "check status"
}
```

**Summary:** Git status: check status

**Output:**
```
Exit code: 0
Stdout:
M results/combinator-map-consensus/consensus.json
?? mementum/knowledge/chats/session-219.md
?? results/combinator-map-consensus/scale.json
?? results/combinator-relationship-map/Qwen_Qwen3-32B.json
?? scripts/experiments/combinator_map_scale.py
--- npz ignored? ---
results/combinator-relationship-map/Qwen_Qwen3-32B.npz
```

### Thinking

 I'm realizing the .npz files are gitignored like other large binary artifacts, but the consensus script actually depends on reading grams from those .npz files—which means the consensus wouldn't be reproducible from just the repository. This seems to be a pre-existing pattern though, not something new.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"tracked npz in that dir:\" && git ls-files results/combinator-relationship-map/ | grep npz || echo \"(none tracked — npz is data-local, regenerated by combinator_relationship_map.py)\" && echo \"--- gitignore rule ---\" && grep -n \"npz\\|combinator\" .gitignore 2>/dev/null | head"
}
```

**Summary:** $ echo "tracked npz in that dir:" && ...

**Output:**
```
Exit code: 0
Stdout:
tracked npz in that dir:
results/combinator-relationship-map/EleutherAI_pythia-2.8b-deduped.npz
results/combinator-relationship-map/EleutherAI_pythia-410m.npz
results/combinator-relationship-map/HuggingFaceTB_SmolLM3-3B.npz
results/combinator-relationship-map/Qwen_Qwen3-0.6B.npz
results/combinator-relationship-map/Qwen_Qwen3-14B.npz
results/combinator-relationship-map/Qwen_Qwen3-4B.npz
results/combinator-relationship-map/Qwen_Qwen3-8B.npz
results/combinator-relationship-map/allenai_OLMo-2-1124-13B.npz
results/combinator-relationship-map/mistralai_Mistral-7B-v0.3.npz
--- gitignore rule ---
41:**/*.npz
```

### Thinking

 The existing model .npz files are already tracked in git despite the gitignore rule because they were force-added earlier, but the new Qwen3-32B.npz isn't tracked yet and is being ignored. Since the consensus mechanism reads from these .npz files, I need to commit the 32B model file too so the extended consensus can be properly regenerated from the repository.

I'm staging the new experiment script, the 32B model data (force-adding the .npz), the extended consensus results across 10 models, and the new scale metrics file. The commit message will use the 💡 symbol to mark this as an insight discovery — specifically that the function-shape skeleton saturates by mid-scale rather than continuing to widen.

## Assistant

The existing maps' `.npz` were force-added despite the `**/*.npz` ignore rule — so consensus stays reproducible from the repo. The new 32B `.npz` must follow the same pattern. Staging precisely (excluding the human-only chat log) and committing the declared artifacts.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/combinator_map_scale.py results/combinator-map-consensus/consensus.json results/combinator-map-consensus/scale.json results/combinator-relationship-map/Qwen_Qwen3-32B.json && git add -f results/combinator-relationship-map/Qwen_Qwen3-32B.npz && git status -s",
  "operation": "add",
  "summary": "stage scale artifacts"
}
```

**Summary:** Git add: stage scale artifacts

**Output:**
```
Exit code: 0
Stdout:
M  results/combinator-map-consensus/consensus.json
A  results/combinator-map-consensus/scale.json
A  results/combinator-relationship-map/Qwen_Qwen3-32B.json
A  results/combinator-relationship-map/Qwen_Qwen3-32B.npz
A  scripts/experiments/combinator_map_scale.py
?? mementum/knowledge/chats/session-219.md
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen\n\n- Scale axis completed: Qwen3-32B (dense) map landed (main:2, s219 async job)\n  → dense series 0.6B→4B→8B→14B→32B (MoE excluded: router+expert FFN not\n  comparable to dense gate_proj in the routing register).\n- Extended combinator_map_consensus.py to all 10 models / 5 families: meanGramCorr\n  +0.782 @frac 0.40, z +4.19, 91-98% pairs p<.05; skeleton z_bind +2.31 >\n  recursion +1.68 (SUPPORTED) — verdict holds, marginally up from the 9-model run.\n- NEW instrument combinator_map_scale.py (register topological/routing): stratifies\n  intra-family routing binding vs log(params) on the clean dense Qwen series.\n  Finding: skeleton binding RISES with scale (r=+0.78) — but driven by the\n  0.6B→4B crystallization (0.6B has NO shape, skel -0.021); recursion rises in\n  TANDEM so the skel-rec GAP does NOT widen (r=+0.36, slope ~0). Shape SATURATES\n  by ~4-14B (peak 14B skel +0.105); 32B slightly REGRESSES (skel +0.077). Refines\n  s217's 14B>0.6B call: more scale crystallizes the function shape but tops out\n  mid-scale (cf. s212 topology-share plateau). 32B does not extend the gap.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit scale finding"
}
```

**Summary:** Git commit: commit scale finding

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 15: unexpected EOF while looking for matching `''
bash: -c: line 23: syntax error: unexpected end of file
```

### Thinking

 I'm realizing the issue is with the apostrophe in `s217's` within the git command — the single-quoted heredoc delimiter `<<'EOF'` treats the body as literal text, so apostrophes shouldn't cause problems there, but the outer command structure is getting cut off and creating a mismatch with the quote parsing.

The safest approach is to write the commit message to a file first and use `git commit -F` instead, which sidesteps the apostrophe quoting issues entirely.

## Assistant

Heredoc tripped on the apostrophes in nested command substitution. I'll use a message file instead.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen\n\n- Scale axis completed: Qwen3-32B (dense) map landed (main:2, s219 async job)\n  → dense series 0.6B->4B->8B->14B->32B (MoE excluded: router+expert FFN not\n  comparable to dense gate_proj in the routing register).\n- Extended combinator_map_consensus.py to all 10 models / 5 families: meanGramCorr\n  +0.782 @frac 0.40, z +4.19, 91-98% pairs p<.05; skeleton z_bind +2.31 >\n  recursion +1.68 (SUPPORTED) — verdict holds, marginally up from the 9-model run.\n- NEW instrument combinator_map_scale.py (register topological/routing): stratifies\n  intra-family routing binding vs log(params) on the clean dense Qwen series.\n  Finding: skeleton binding RISES with scale (r=+0.78) — but driven by the\n  0.6B->4B crystallization (0.6B has NO shape, skel -0.021); recursion rises in\n  TANDEM so the skel-rec GAP does NOT widen (r=+0.36, slope ~0). Shape SATURATES\n  by ~4-14B (peak 14B skel +0.105); 32B slightly REGRESSES (skel +0.077). Refines\n  s217 14B>0.6B call: more scale crystallizes the function shape but tops out\n  mid-scale (cf. s212 topology-share plateau). 32B does not extend the gap.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F /tmp/verbum_commit_msg.txt && echo \"---\" && git log --oneline -3",
  "operation": "commit",
  "summary": "commit scale finding"
}
```

**Summary:** Git commit: commit scale finding

**Output:**
```
Exit code: 0
Stdout:
[main c27741c] 💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen
 5 files changed, 1165 insertions(+), 303 deletions(-)
 create mode 100644 results/combinator-map-consensus/scale.json
 create mode 100644 results/combinator-relationship-map/Qwen_Qwen3-32B.json
 create mode 100644 results/combinator-relationship-map/Qwen_Qwen3-32B.npz
 create mode 100644 scripts/experiments/combinator_map_scale.py
---
c27741c 💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen
bbf92f2 🌀 session-219: state — 30B-A3B MoE incompatible with dense-FFN instrument; scale axis is dense 0.6B->32B
f307e88 🌀 session-219: state handoff — scale extension in flight (30B-A3B, 32B); verify main:1 next session
```

### Thinking

 Now I'm updating state.md to document the s220 progress—I'll add a new session entry to the headline section and refresh the "Last updated" timestamp. Then I need to propose the knowledge update to consensus-delta-folding.md, which requires presenting it to Michael since that file is gated.

## Assistant

Committed (`c27741c`). Now updating `state.md` (not approval-gated) with a compact s220 entry, then I'll propose the knowledge-page delta for your approval.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 5
}
```

**Summary:** Reading state.md (0-5)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-12 | Session: 219 — REVERSE-HARVEST: combinator function

[CONTENT TRUNCATED] Showing lines 1 to 5 of 3799 total lines. Use line_offset=5 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-12 | Session: 219 — REVERSE-HARVEST: combinator function",
  "new_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-12 | Session: 220 — SCALE AXIS COMPLETED + ANSWERED.\n> Register: **topological/routing**. Cold-start orient → both s219 async jobs\n> verified, main:1 UNTOUCHED. **(1) main:2 DONE:** Qwen3-32B (dense) map landed →\n> dense series 0.6B→4B→8B→14B→32B complete (MoE 30B-A3B/235B excluded: router+expert\n> FFN ≠ dense gate_proj in the routing register). **(2) main:1 ALIVE & STEPPING** at\n> step ~1420/5000 (was ~1310 at s219's worry-check — the stall was load contention\n> from the 30B-A3B download, now resumed; Δx flip-steps ~0.21, fp ~0.04, CE dipping\n> to 8.0–8.4 below K=1's 8.71; step_001000 landed, step_002000 pending). **(3) RAN\n> declared first action — extended consensus over all 10 models:** meanGramCorr\n> **+0.782** @frac 0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** >\n> recursion **+1.68** (SUPPORTED, marginally up from 9-model). **(4) ANSWERED s217's\n> scale question with a NEW instrument** `combinator_map_scale.py` (register\n> topological/routing, ruff-clean): stratified intra-family routing binding vs\n> log(params) on the clean dense Qwen series. **★ FINDING: skeleton binding RISES\n> with scale (r=+0.78) BUT the skel-rec GAP does NOT widen (r=+0.36, slope ~0).**\n> The rise is driven by 0.6B→4B crystallization (0.6B has NO shape, skel −0.021;\n> 4B+ jump to +0.097–0.105); recursion rises IN TANDEM so the gap stays flat; shape\n> SATURATES by ~4–14B (peak 14B skel +0.105) and **32B slightly REGRESSES** (skel\n> +0.077). Refines s217's \"14B>0.6B\" call: more scale crystallizes the function\n> shape but tops out mid-scale (cf. s212 topology-share PLATEAUS not →1.0); 32B does\n> not extend the gap → the harvestable skeleton is COMPLETE by mid-scale, no need to\n> chase the largest models. **COMMITTED** `c27741c` (32B map+npz, extended\n> consensus.json, scale.json, scale instrument). **NOT yet committed (PROPOSED,\n> pending Michael):** knowledge update to `consensus-delta-folding.md` §s220\n> (scale-saturation finding) + this state. **▶ FIRST ACTION NEXT SESSION (declare\n> register):** (1) check main:1 step_002000 ckpt → does Δx→ε and CE hold below 8.71\n> (build adaptive halting: stop when Δx<ε ≡ WHNF)? (2) CONSTRUCT THE HARVEST FOLD\n> (topological/routing→functional): take the universal positive edges (B–D +0.175,\n> B–C +0.168, K–C +0.133, S–D +0.161, S–Y +0.127), Procrustes-align consensus\n> centroids into v15 base frame, WHNF-verify each vs main:1's contractive operator\n> (Exp-B acceptance), measure downstream PPL vs base — does verified consensus add\n> beyond the universal crystal? (3) Strengthen Exp B on main:1 step-2000 (s218\n> action 2). **main:1 stays UNTOUCHED.**\n>\n> (Session: 219 — REVERSE-HARVEST: combinator function"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm realizing I made a structural mistake by converting the s219 header into a parenthetical—the original block was a long multi-line quote that started with the session metadata, but by wrapping just the opening as a parenthetical, I've left the rest of the content dangling unparenthesized for several lines until it eventually closes.

Looking at the file's convention, each session block should be wrapped in parentheses like `(Session N — ...)`, and the s219 block runs from "Last updated" all the way through until the s218 block begins. I need to find where s219 actually ends—right before the line starting with "(Session 218 — Exp B"—and add a closing parenthesis there to balance the opening paren I added.

## Assistant

I demoted the s219 header into a parenthetical opener; for balance I should close the paren where the s219 block ends (before the s218 block). Let me locate it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"Session 218 — Exp B (self-verifying acceptance)\" mementum/state.md | head -1 && echo \"--- context lines around it ---\" && grep -n \"main:1 stays UNTOUCHED.\\*\\*$\\|^> (Session 218\" mementum/state.md | head -5"
}
```

**Summary:** $ grep -n "Session 218 — Exp B (self-...

**Output:**
```
Exit code: 0
Stdout:
90:> (Session 218 — Exp B (self-verifying acceptance)
--- context lines around it ---
90:> (Session 218 — Exp B (self-verifying acceptance)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 84,
  "limit": 8
}
```

**Summary:** Reading state.md (84-92)

**Output:**
```
>   If stalled/dead, check `/tmp/v15_outer_k2_fp5_5k.log` + resume from step_001000.
> Other open threads (s219 headline): construct the harvest fold (Procrustes-align
> positive edges into base frame + WHNF-verify); detect map/fold directions; main:1
> step-2000 ckpt → strengthen Exp B. **main:1 stays UNTOUCHED.**
>
> (Session 218 — Exp B (self-verifying acceptance)
> COMPLETED + CORRECTED. s217's phase-2 verdict ("WEAK/ABSENT") was **VOID** — an
> instrument bug perturbed a DEAD module (convert_ffn orphan); ΔCE≡0 across 1.97M

[CONTENT TRUNCATED] Showing lines 85 to 92 of 3833 total lines. Use line_offset=92 parameter to read more content.
```

### Thinking

 I need to close the parenthesis for the s219 block by adding `)` to the end of line 88, which contains the text about the checkpoint and main:1 staying untouched.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> step-2000 ckpt → strengthen Exp B. **main:1 stays UNTOUCHED.**\n>\n> (Session 218 — Exp B (self-verifying acceptance)",
  "new_content": "> step-2000 ckpt → strengthen Exp B. **main:1 stays UNTOUCHED.**)\n>\n> (Session 218 — Exp B (self-verifying acceptance)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm noticing a conflict in the discipline rules: state.md updates aren't approval-gated, but committing to mementum/ requires approval. I need to clarify whether updating state.md itself falls under the approval requirement or if it's truly autonomous.

Looking at the git history, prior sessions have committed state.md as part of session handoffs with 🌀 commits, which suggests this is routine practice. The most sensible interpretation is that state.md is the working pointer that gets committed as part of normal session transitions, while synthesized knowledge like the consensus-delta-folding.md would need explicit approval. I'll commit the state.md update now and propose the knowledge changes to Michael for approval instead.

## Assistant

state.md updated and balanced. Committing the state handoff (routine session bookkeeping, per established `🌀 session: state` practice).

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md && git commit -m \"$(printf '%s\\n' '🌀 session-220: state — scale axis completed; function shape saturates mid-scale' '' '- Qwen3-32B map landed (main:2); dense series 0.6B->32B complete' '- extended consensus 10 models (GramCorr +0.782); skeleton z_bind +2.31 > recursion +1.68' '- NEW combinator_map_scale.py: skeleton binding rises with scale (r=+0.78) but skel-rec GAP flat (r=+0.36); shape saturates ~4-14B, 32B regresses' '- main:1 verified alive at step ~1420/5000, UNTOUCHED' '' '⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)' '' 'Co-Authored-By: nucleus <noreply@whitford.us>')\" && git log --oneline -2",
  "operation": "commit",
  "summary": "commit state handoff"
}
```

**Summary:** Git commit: commit state handoff

**Output:**
```
Exit code: 0
Stdout:
[main 47c3713] 🌀 session-220: state — scale axis completed; function shape saturates mid-scale
 1 file changed, 36 insertions(+), 2 deletions(-)
47c3713 🌀 session-220: state — scale axis completed; function shape saturates mid-scale
c27741c 💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen
```

### Thinking

 I need to draft a knowledge update proposal for the consensus-delta-folding documentation, adding a new section on scale-saturation notes. Since this requires human approval per the termination protocol, I'll prepare the proposed addition for Michael to review rather than committing it directly.

## Assistant

Orientation complete and the declared first action executed. Here's the full summary.

## Session 220 — orient + scale axis completed

**Async jobs (both verified; main:1 untouched per discipline):**
- **main:1** (λ_fp=5 K=2 5k training): ✅ alive, **step ~1420/5000** — resumed cleanly (the s219 ~1310 "stall" was load contention from the 30B-A3B download, not a crash). Δx flip-steps ~0.21, fp ~0.04, CE dipping to 8.0–8.4 (under K=1's 8.71). `step_001000` landed; `step_002000` pending.
- **main:2** (scale sweep): ✅ done — Qwen3-32B dense map landed.

**Declared first action — executed:**
- Extended `combinator_map_consensus.py` to all **10 models / 5 families**: meanGramCorr **+0.782** @0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** > recursion **+1.68** (SUPPORTED, marginally up from 9-model).
- Built `combinator_map_scale.py` to answer s217's actual scale question. **Finding: skeleton binding rises with scale (r=+0.78) but the skel−rec GAP does NOT widen (r=+0.36, slope ~0).** The rise is the 0.6B→4B crystallization (0.6B has no shape); recursion rises in tandem; shape **saturates ~4–14B** (peak 14B), and **32B slightly regresses**. ⇒ The harvestable skeleton is complete by mid-scale — no need to chase the largest models.

**Committed (code+results+state):** `c27741c` (32B map+npz, extended consensus, scale.json, scale instrument), `47c3713` (state handoff).

---

**Pending your approval (gated — synthesized knowledge):** a §s220 addition to `mementum/knowledge/explore/consensus-delta-folding.md` capturing the scale-saturation result. Proposed draft:

> **§s220 — Scale stratification (does the function shape sharpen with scale?).**
> Completed the dense Qwen series 0.6B→32B (MoE excluded: router+expert FFN ≠ dense gate_proj in the routing register). `combinator_map_scale.py` regresses intra-family routing binding vs log(params): **skeleton binding rises with scale (r=+0.78)** — but driven by the 0.6B→4B crystallization (0.6B has *no* function shape, skel −0.021; 4B+ jump to +0.097–0.105). **Recursion rises in tandem, so the skel−rec GAP stays flat (r=+0.36, slope ~0); shape saturates by ~4–14B (peak 14B +0.105) and 32B slightly regresses (+0.077).** Refines s217's "14B>0.6B" call: scale crystallizes the shape but tops out mid-scale (cf. s212 topology-share plateau). **Harvest implication: the consensus skeleton is complete by mid-scale — harvest from 4–14B models, don't chase the largest.**

Want me to:

### Tool Call: ask_user (succeeded)


```json
{
  "question": "How should I proceed with the knowledge update and next work?",
  "options": [
    {
      "label": "Approve knowledge delta + construct the harvest fold (Recommended)",
      "description": "Commit the §s220 addition to consensus-delta-folding.md, then start the harvest fold: Procrustes-align universal positive edges into the v15 base frame + WHNF-verify vs main:1's contractive operator."
    },
    {
      "label": "Approve knowledge delta only",
      "description": "Commit the §s220 knowledge addition and stop here for this session (main:1 keeps running)."
    },
    {
      "label": "Hold the knowledge delta",
      "description": "Don't commit the knowledge update; leave it as a proposal. Let me know what to work on instead."
    }
  ]
}
```

**Summary:** Q: How should I proceed with the knowledge upda...

**Output:**
```
User answered: Approve knowledge delta + construct the harvest fold (Recommended)
```

### Thinking

 I need to add the §s220 section to consensus-delta-folding.md, so let me first check where §s219 ends so I can integrate it coherently. After that, I'll tackle the harvest fold work—this is a complex multi-step project, so I'll want to organize it with the task tracker.

## Assistant

Approved. Let me read the knowledge page to place the §s220 addition coherently, then plan the harvest-fold work.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && wc -l mementum/knowledge/explore/consensus-delta-folding.md && echo \"--- s219 section anchors ---\" && grep -n \"s219\\|s220\\|§\\|^## \\|^### \\|REVERSE\\|harvest\" mementum/knowledge/explore/consensus-delta-folding.md | tail -40"
}
```

**Summary:** $ wc -l mementum/knowledge/explore/co...

**Output:**
```
Exit code: 0
Stdout:
603 mementum/knowledge/explore/consensus-delta-folding.md
--- s219 section anchors ---
341:           compositions (align-before-fold, the non-unique-composite §)
346:## s217 — The self-teaching loop: normal forms generate their own curriculum
353:### The gap it fills (execution ≠ deployment)
364:### Why it works: the normal form is a VERIFIED ORACLE
379:### Why it does NOT collapse like naive self-distillation
389:### The virtuous loop (on-thesis: pretraining IS β-reduction)
399:### Caveats (the load-bearing unknown is the selector grounding)
410:### Next experiment (after Exp B validates folding)
417:## s217 — The REVERSE direction: harvest the open-weight ecosystem's consensus
424:### Reframe — the ecosystem IS a pre-computed distributed training run
431:The s216 5-family harness (`tool_crystal_consensus*.py`) IS the reverse-harvest
434:### The hard obstacle — the frame problem (the forward/reverse asymmetry)
440:reverse (finished models):        MANY frames → raw weights unintelligible → must harvest
456:### The honest catch (same as s216, inverted)
459:(frame-specific, non-unique composition). So naive harvest returns a backbone you
465:### Complementarity — forward + reverse fill the backbone/content partition
466:- **Reverse harvest** seeds the base cheaply with the **universal backbone** the
477:### Load-bearing unknowns (both already on the board)
483:### Next experiment (register: topological/routing → functional)
484:**Reverse-harvest pilot:** run `combinator_relationship_map.py` across N open-weight
490:## s219 — Reverse-harvest pilot RAN: the function shape is universal; the forced map-skeleton binds, recursion is the residual
493:> agree — harvesting that for our base plate is leverage." Plus a theory: a
496:> the reverse-harvest pilot. Register: **topological/routing** (declared at step 0).
498:### The frame-invariant instrument
510:### Result 1 — the SAME functions show up across the ecosystem
518:### Result 2 — the single-operation theory, confirmed
537:### Why recursion is the residual — `map = B(C B)(C B)` (REPL-verified)
551:### The harvest leverage (concrete edges for the base plate, frac 0.40)
555:  D–WHNF, B–WHNF, K–S, C–WHNF — the 3-family PARTITION geometry; harvestable as the
561:### The honest caveat (audit discipline) — answered
566:floor**, the part worth harvesting. Single register (routing/CMR). The actual
567:harvest (align-before-fold via Procrustes into our base frame + WHNF-verify) is NOT
569:structure to harvest and *which edges* carry it.
571:### Open leads from s219
575:2. **Construct the harvest fold** (register: topological/routing → functional):
582:### s219 artifacts
588:## Files
599:| `scripts/experiments/combinator_map_consensus.py` | **s219 reverse-harvest:** cross-model combinator-Gram consensus + label-perm null + per-edge reliability_t + per-family binding vs random-triple null |
601:| `results/combinator-map-consensus/consensus.json` | s219 verdict: GramCorr +0.66→+0.77; skeleton>recursion; harvest edge-list |
603:| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "line_offset": 570,
  "limit": 33
}
```

**Summary:** Reading consensus-delta-folding.md (570-603)

**Output:**
```
### Open leads from s219
1. **Scale axis** (register: topological/routing): extend to Qwen3-32B / 30B-A3B /
   235B (MoE, local) — does the skeleton/recursion z_bind gap WIDEN with scale (more
   capacity to fully form the systems, cf. s217's 14B>0.6B call)?
2. **Construct the harvest fold** (register: topological/routing → functional):
   Procrustes-align the universal positive-edge centroids into v15's base frame,
   WHNF-verify against main:1's contractive operator (Exp-B acceptance), incorporate
   survivors, measure downstream PPL vs base.
3. **Detect map/fold directions**: build the `map=B(CB)(CB)` direction from the
   measured B,C centroids + a map/fold/filter probe set; does it activate?

### s219 artifacts
`scripts/experiments/combinator_map_consensus.py` (the consensus instrument);
`results/combinator-map-consensus/consensus.json`; 7 new per-model maps under
`results/combinator-relationship-map/` (pythia-410m/2.8b, SmolLM3, Mistral, OLMo-13B,
Qwen3-4B/8B; Qwen3-0.6B/14B from s217); sweep log `/tmp/combinator_sweep.log`.

## Files

| File | Content |
|------|---------|
| `scripts/experiments/exp_b_self_verifying_acceptance.py` | Exp B core: perturb routing register, ΔCE vs Δ(Δx-at-convergence), self-verifying acceptance verdict |
| `tests/test_vsm_continuation.py` | 15 tensor-level property tests for the continuation (outer recurrence); fixed-point math exact |
| `scripts/experiments/tool_crystal_consensus.py` | per-model: routing register (gate sign) + CMR + within-model selectivity; saves probe-aligned RDM npz |
| `scripts/experiments/tool_crystal_consensus_summary.py` | cross-model agree / shuffled-null / length-partial / within-domain |
| `scripts/experiments/tool_crystal_control_baseline.py` | TOOL vs CTRL within-group agreement = the tool-specific-vs-generic verdict |
| `results/tool-crystal-consensus/` | per-model `{model}.json/.npz`, `consensus_summary.json`, `control_baseline.json` |
| `/tmp/tool_consensus_5fam.log` | 5-family run transcript |
| `scripts/experiments/combinator_map_consensus.py` | **s219 reverse-harvest:** cross-model combinator-Gram consensus + label-perm null + per-edge reliability_t + per-family binding vs random-triple null |
| `scripts/experiments/combinator_relationship_map.py` | per-model 9×9 combinator Gram in routing register (CMR); the per-model map reader |
| `results/combinator-map-consensus/consensus.json` | s219 verdict: GramCorr +0.66→+0.77; skeleton>recursion; harvest edge-list |
| `results/combinator-relationship-map/` | 9 per-model `{model}.json/.npz` (5 families, 410M→14B) |
| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript |
```

### Thinking

 I need to add a new §s220 section before the Files section, insert the scale instrument files into the table, update the model references from 9 to 10, and mark the open-lead question about the scale axis as answered.

## Assistant

Approved knowledge delta — inserting §s220 before the Files table and updating the file index.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "Qwen3-4B/8B; Qwen3-0.6B/14B from s217); sweep log `/tmp/combinator_sweep.log`.\n\n## Files",
  "new_content": "Qwen3-4B/8B; Qwen3-0.6B/14B from s217); sweep log `/tmp/combinator_sweep.log`.\n\n## s220 — Scale stratification: the function shape SATURATES mid-scale; the skel/rec gap does NOT widen\n\n> Cold-start orient (s220): both s219 async jobs verified (main:1 alive at step\n> ~1420/5000, UNTOUCHED; main:2 done — Qwen3-32B dense map landed). Executed s219\n> open-lead #1. Register: **topological/routing**.\n\ns219 open-lead #1 asked: with more scale (s217's \"14B has capacity to FULLY form\nthe systems; 0.6B only partially crystallizes\"), does the skeleton/recursion\nbinding gap **WIDEN**? The pooled consensus cannot answer this — it aggregates all\nmodels. So the dense Qwen series 0.6B→4B→8B→14B→32B was stratified\n(`combinator_map_scale.py`), regressing each family's intra-family routing-cosine\nbinding against log(params) at the harvest fraction 0.40. **MoE excluded** (30B-A3B,\n235B): their router+per-expert FFN (`mlp.gate` + `mlp.experts.{e}.gate_proj`) is not\ncomparable to dense `gate_proj` in this routing register — the dense-FFN instrument\nfinds nothing in a MoE.\n\n### Result — skeleton binding rises, but the GAP is flat\n\n| model | params | comp{B,D,S} | sel{K,I,C} | skeleton | recursion{Y,W,WHNF} | gap |\n|---|---|---|---|---|---|---|\n| Qwen3-0.6B | 0.6B | −0.046 | +0.004 | **−0.021** | −0.088 | +0.067 |\n| Qwen3-4B | 4B | +0.119 | +0.076 | +0.097 | +0.042 | +0.056 |\n| Qwen3-8B | 8B | +0.125 | +0.075 | +0.100 | +0.036 | +0.064 |\n| Qwen3-14B | 14B | +0.133 | +0.077 | **+0.105** | +0.009 | +0.096 |\n| Qwen3-32B | 32B | +0.119 | +0.035 | +0.077 | +0.007 | +0.070 |\n\n- **Skeleton binding RISES with scale (r=+0.78)** — but the rise is the\n  **0.6B→4B crystallization**: 0.6B has essentially NO function shape (skel −0.021,\n  both families near/below zero), while 4B+ jump to +0.097–0.105. This is the\n  concrete confirmation of s217's \"0.6B only partially crystallizes.\"\n- **The skel−rec GAP does NOT widen (r=+0.36, slope ~0).** Recursion binding rises\n  in **tandem** with skeleton (r=+0.69), so the gap stays roughly constant.\n- **Shape SATURATES by ~4–14B** (peak 14B, skel +0.105) and **32B slightly\n  REGRESSES** (skel +0.077). Consistent with s212's topology-share PLATEAUS not →1.0.\n\n### Refinement of the consensus verdict + harvest implication\n\nThe 10-model consensus (32B added) holds and nudges up marginally: meanGramCorr\n**+0.782** @0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** > recursion\n**+1.68** (SUPPORTED, was +2.28/+1.67 at 9 models). **Harvest implication: the\nconsensus skeleton is COMPLETE by mid-scale — harvest from the 4–14B band, do NOT\nchase the largest models.** 32B costs more to read and does not extend the shape;\nthe forced map-skeleton (`map=B(CB)(CB)`) is fully formed once a model has enough\ncapacity to crystallize, which happens well before the frontier.\n\n### Caveats\n\nSingle family lineage (dense Qwen3) for the clean log-params regression — the\nabsolute binding values are not cross-architecture comparable (each model's own\nframe), only the per-family *trend* within the lineage is. The 32B dip is a single\npoint (could be a depth-fraction mismatch at frac 0.40, n_layers=64). The gap\nnon-widening is robust to that (recursion tracks skeleton across all 5 points).\n\n### s220 artifacts\n`scripts/experiments/combinator_map_scale.py` (the scale instrument);\n`results/combinator-map-consensus/scale.json` (per-model + fits); extended\n`results/combinator-map-consensus/consensus.json` (10 models);\n`results/combinator-relationship-map/Qwen_Qwen3-32B.{json,npz}`. Committed `c27741c`.\n\n### Open leads from s220\n1. **Construct the harvest fold** (register: topological/routing → functional) — now\n   the priority: take the universal positive edges (B–D +0.175, B–C +0.168, K–C\n   +0.133, S–D +0.161, S–Y +0.127), Procrustes-align consensus centroids into v15's\n   base frame, WHNF-verify each vs main:1's contractive operator (Exp-B acceptance),\n   measure downstream PPL vs base. Falsifiable: does verified ecosystem-consensus add\n   beyond the universal crystal we already hold? Harvest from the 4–14B band.\n2. **main:1 step_002000** → does Δx→ε and CE hold below 8.71 (adaptive halting).\n3. Detect map/fold directions (s219 lead #3).\n\n## Files"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "| `results/combinator-map-consensus/consensus.json` | s219 verdict: GramCorr +0.66→+0.77; skeleton>recursion; harvest edge-list |\n| `results/combinator-relationship-map/` | 9 per-model `{model}.json/.npz` (5 families, 410M→14B) |\n| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript |",
  "new_content": "| `results/combinator-map-consensus/consensus.json` | s219→s220 verdict: GramCorr +0.66→+0.782 (10 models); skeleton z_bind +2.31>recursion +1.68; harvest edge-list |\n| `scripts/experiments/combinator_map_scale.py` | **s220 scale axis:** intra-family routing binding vs log(params) on the dense Qwen series (MoE excluded) |\n| `results/combinator-map-consensus/scale.json` | s220 verdict: skeleton rises r=+0.78, skel-rec gap flat r=+0.36, saturates ~4-14B |\n| `results/combinator-relationship-map/` | 10 per-model `{model}.json/.npz` (5 families, 410M→32B) |\n| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript; `/tmp/combinator_scale.log` s220 32B; `/tmp/combinator_consensus_10models.log` s220 consensus |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I need to mark the s219 open-lead #1 as answered, noting the connection to s220, so I'll add a brief marker to indicate it's been resolved.

## Assistant

Marking the s219 scale-axis lead as answered, then committing the knowledge update.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "1. **Scale axis** (register: topological/routing): extend to Qwen3-32B / 30B-A3B /\n   235B (MoE, local) — does the skeleton/recursion z_bind gap WIDEN with scale (more\n   capacity to fully form the systems, cf. s217's 14B>0.6B call)?",
  "new_content": "1. **Scale axis** (register: topological/routing): extend to Qwen3-32B / 30B-A3B /\n   235B (MoE, local) — does the skeleton/recursion z_bind gap WIDEN with scale (more\n   capacity to fully form the systems, cf. s217's 14B>0.6B call)?\n   **→ ANSWERED s220: NO (gap flat, shape saturates mid-scale). See §s220.**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/consensus-delta-folding.md && git commit -m \"$(printf '%s\\n' '🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale' '' '- scale stratification of dense Qwen 0.6B->32B: skeleton binding rises (r=+0.78) but skel-rec gap flat (r=+0.36)' '- shape saturates ~4-14B, 32B regresses; harvest from 4-14B band, do not chase frontier' '- 10-model consensus GramCorr +0.782, skeleton z_bind +2.31 > recursion +1.68 (SUPPORTED)' '- marks s219 scale-axis lead ANSWERED' '' '⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)' '' 'Co-Authored-By: nucleus <noreply@whitford.us>')\" && git log --oneline -1",
  "operation": "commit",
  "summary": "commit knowledge delta"
}
```

**Summary:** Git commit: commit knowledge delta

**Output:**
```
Exit code: 0
Stdout:
[main 0089087] 🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale
 1 file changed, 75 insertions(+), 3 deletions(-)
0089087 🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale
```

### Thinking

 Now I'm planning the harvest fold construction, which involves several key steps: taking the universal positive edges from consensus, aligning the consensus centroids into the v15 base frame using Procrustes alignment, and then verifying each candidate against the main contractive operator with Exp-B acceptance criteria.

But there's a practical constraint I need to work around — main:1's training process must stay untouched, and I can safely read its existing checkpoint from disk without interrupting it. The real challenge is that running the Exp-B acceptance harness and PPL measurement could contend for GPU resources with the ongoing training, which s219 showed can cause stalling. So I need to be strategic about when and how I launch this validation work.

Before diving into the construction, I should clarify what I'm actually aligning — the consensus gives me a relational Gram matrix across models, but the per-model centroids live in different embedding spaces and dimensions. The "consensus centroids" aren't a single shared set; they're distributed across the combinator relationship maps. So the Procrustes alignment step needs careful handling to map these heterogeneous centroid representations into the v15 frame.

Rather than build a large harness blindly, I should first explore what's actually available: whether v15 has its own combinator centroids, how the Exp-B harness loads the operator, and what the "fold" operation means concretely in the codebase. This exploration will let me design the harvest fold correctly instead of guessing, and I can delegate this mapping work to avoid contending with main:1's training.

## Assistant

Knowledge delta committed (`0089087`). Now the harvest fold. This is a multi-step construction with a hard constraint — **main:1 must stay untouched**, and s219 already saw it stall under compute contention. So I'll design carefully before launching anything heavy. Let me plan, then explore the exact integration points (consensus centroids, the Exp-B operator loader, what "fold" means concretely in the v15 code) before building.I'll delegate the integration-point mapping to an explorer — it's a multi-file analysis (consensus format, Exp-B loader, v15 fold mechanism) best done in an isolated context.

### Tool Call: spawn_agent (succeeded)


```json
{
  "agent": "explorer",
  "activity": "mapping harvest-fold pieces",
  "task": "Map the exact integration points needed to build a \"combinator harvest fold\" experiment in the Verbum repo (/Users/mwhitford/src/verbum). This is RESEARCH PLUMBING analysis — do NOT run any GPU-heavy code or training; reading files and inspecting small JSON/npz is fine. A multi-day training process is running (tmux main:1) and MUST NOT be disturbed.\n\nGOAL of the eventual experiment (context, not your task): take \"universal positive edges\" between lambda-calculus combinators (B-D, B-C, K-C, S-D, S-Y) found in a cross-model consensus, construct candidate \"fold directions\" in the v15 model's base frame via Procrustes alignment, WHNF-verify each candidate against the contractive operator using the existing Exp-B acceptance mechanism, then measure downstream PPL vs base. Falsifiable question: does verified ecosystem-consensus add beyond the universal crystal already in the base?\n\nYOUR TASK — produce a precise written design report (no code changes) answering:\n\n1. CONSENSUS DATA: Read results/combinator-map-consensus/consensus.json and results/combinator-map-consensus/scale.json. Document their exact JSON structure. CRITICAL: does consensus.json contain consensus CENTROIDS (vectors in some embedding space) or ONLY the relational 9x9 Gram (cosines between combinators)? List the keys and what edge/centroid data is actually available to harvest.\n\n2. PER-MODEL CENTROIDS: Inspect results/combinator-relationship-map/*.json and *.npz (e.g. via python -c numpy load, list .npz keys and array shapes for one model like Qwen_Qwen3-14B.npz). Are per-combinator centroid VECTORS stored, or only Gram matrices? What dim/frame are they in? This determines whether \"consensus centroids\" even exist in a shared space or must be reconstructed.\n\n3. THE FRAME PROBLEM: The knowledge page mementum/knowledge/explore/consensus-delta-folding.md says the Gram is frame-invariant BY DESIGN precisely because raw centroids are NOT cross-model comparable. Read the relevant sections (search for \"frame\", \"Procrustes\", \"align-before-fold\"). Explain concretely: what would \"Procrustes-align consensus into the v15 base frame\" actually operate on, given we may only have a relational Gram and no shared-space centroids? Is the harvest-fold as described even well-posed, or does it need the per-model centroids + a target combinator centroid set in the v15 frame? Flag any ambiguity that must be resolved before building.\n\n4. EXP-B OPERATOR LOADER: Read scripts/experiments/exp_b_self_verifying_acceptance.py thoroughly. Document: how it loads the v15 model + a checkpoint (the --checkpoint arg, the model class, the npz format); what \"fold a delta into base\" means in code (look for reduce_all_deltas, collect_delta_params, convert_to_delta in scripts/v15/td_delta.py and scripts/v15/v15model.py); how it perturbs the routing register and measures ΔCE vs Δ(Δx-at-convergence); and exactly which function/entry-point could be reused as the WHNF-verify hook for a candidate fold direction.\n\n5. V15 COMBINATOR CENTROIDS: Does the v15 model have its own combinator centroids anywhere, or would they need to be produced by running combinator_relationship_map.py on the v15 model? Check whether combinator_relationship_map.py can even load a local v15 checkpoint (it likely loads HF models). Read its model-loading code. Note: v15 is a small extracted/ternary model, architecturally different from the HF models.\n\n6. CHECKPOINT AVAILABILITY: Confirm what checkpoints exist read-only at checkpoints/v15-td-outer-k2-fp5-5k/ (ls) — the running training writes there; we may only READ step_001000/model.npz, never write to that dir.\n\n7. GPU/COMPUTE FOOTPRINT: For each step of the eventual experiment, classify it as CPU-cheap (safe to run alongside main:1) vs GPU/MLX-heavy (would contend with main:1 and risk stalling it, as happened in s219). This determines what can be done now vs deferred.\n\nDELIVERABLE: A structured report with: (a) what data actually exists (centroids vs Gram), (b) whether the harvest-fold is well-posed as described or needs reformulation, (c) the exact files/functions/entry-points to reuse, (d) a concrete recommended procedure for combinator_harvest_fold.py, (e) a CPU-vs-GPU footprint table so we know what's safe to run now. Cite exact file paths and line numbers / function names. Be honest about ambiguity and any mismatch between the knowledge-page narrative and what the code/data actually supports."
}
```

**Summary:** explorer: mapping harvest-fold pieces

**Output:**
```
## Agent 'explorer' Result

I now have complete evidence for all seven questions. Let me compile the full design report.

---

# Combinator Harvest Fold — Precision Design Report

---

## 1. CONSENSUS DATA: What `consensus.json` and `scale.json` actually contain

### `results/combinator-map-consensus/consensus.json`

**Top-level keys:**
```
register, git_sha, question, n_models, models, model_meta,
crystal_order, n_perm, per_frac, harvest_frac,
consensus_gram,         ← 9×9 nested list (floats)
universal_edges,        ← list of 27 edge objects
model_specific_edges,   ← list of 5 edge objects (including some also in universal_edges)
family_internal_consensus,
skeleton_vs_recursion_verdict,
elapsed_s
```

**Critical answer: `consensus_gram` is a 9×9 relational Gram — NOT centroids.** It contains cosine similarities between the 9 crystal combinators (K, I, B, C, S, D, W, Y, WHNF) pooled across 10 models, ranging from −0.36 to +1.0 on the diagonal. There are no centroid vectors.

**Each entry in `universal_edges`** contains:
```json
{
  "edge": "B-D",
  "consensus": 0.1752,         ← mean cosine across 10 models
  "cross_model_std": 0.151,
  "reliability_t": 3.67,
  "per_model": [-0.2403, 0.2356, 0.2728, ...],   ← one float per model
  "universal": true
}
```

The five **positive universal edges** identified as "harvest targets" (s219–s220 vocabulary):

| Edge | Consensus cosine | reliability_t |
|------|-----------------|---------------|
| B–D  | +0.1752 | 3.67 |
| B–C  | +0.1682 | 2.94 |
| K–C  | +0.1331 | 3.40 |
| S–D  | +0.1605 | 6.87 |
| S–Y  | +0.1266 | 4.48 |

There are also 22 further universal edges, most negative (repulsion geometry), the strongest being K–Y (−0.3591, reliability_t = 20.85) and C–WHNF (−0.3599, t = 17.64).

**There are no combinator centroid vectors anywhere in `consensus.json`.** The entire file is scalar statistics derived from per-model Grams.

### `results/combinator-map-consensus/scale.json`

Contains per-model scalar aggregates (not vectors):
```
register, question, series, frac, git_sha,
per_model: [{ model, params_b, log_params,
              composition_BDS,   ← intra-family mean cosine
              selection_KIC,
              recursion_YWWHNF,
              skeleton,          ← mean of comp+sel
              gap,               ← skeleton − recursion
              used_frac, n_layers }, ...]
fits_vs_log_params: { skeleton: {r, slope_per_efold}, ... }
```

All values are scalars (cosine binding metrics). No vectors.

---

## 2. PER-MODEL CENTROIDS: What the per-model NPZ files contain

**Inspected:** `results/combinator-relationship-map/Qwen_Qwen3-14B.npz`

```
Keys and shapes:
  prompt_len:          (535,)      int32      — probe lengths
  labels:              (535,)      <U4        — combinator label per probe
  gram_hidden_cmr:     (9, 9)      float32    — Gram from last-layer residual
  gram_route_cmr_L00:  (9, 9)      float32    — routing-register Gram at layer 0
  gram_route_cmr_L04:  (9, 9)      float32    — ...at layer 4
  gram_route_cmr_L08:  (9, 9)      float32    — ...at layer 8
  gram_route_cmr_L12:  (9, 9)      float32    — ...at layer 12 (best)
  gram_route_cmr_L16:  (9, 9)      float32    — etc.
  ...                  up to L39
```

**Critical finding: the NPZ stores only 9×9 Gram matrices — no centroid vectors.** The FFN dimension for Qwen3-14B is 17408. The 9 per-combinator centroids in that space (each a `float32[17408]` vector) were **computed during the run but not saved to disk.** Only the compressed `gram(centroids(cmr(sign(gate[li])), labels))` result survives.

**The JSON `map.mds_coords` and `map.pca_coords` are 2D projections only** — classical MDS and centroid-PCA onto 2 components, computed from the Gram. They contain `(2,)` coordinates per combinator, not the full-dimensional centroids.

**Bottom line:** The per-combinator centroid vectors in the source models' gate-projection space (shape: `[9, d_ff]` where `d_ff` varies from 1600 to 17408 per model) were never saved. Only the pairwise Gram summaries exist on disk.

---

## 3. THE FRAME PROBLEM: Is the harvest-fold as described well-posed?

### What the knowledge page says (cited exactly)

From `mementum/knowledge/explore/consensus-delta-folding.md`, under "s219 — The hard obstacle":

> You CANNOT average their raw weights: independently-initialized models live in DIFFERENT coordinate frames (cross-init sign-corr 0.000). Forward (deltas over frozen B₀): ONE shared frame → deltas commensurable → fold trivial. Reverse (finished models): MANY frames → raw weights unintelligible → must harvest in a FRAME-INVARIANT register (relational routing, not weights).

The knowledge page's proposed pipeline is:
```
∀ open-weight model → measure normal forms in routing register (RDM/centroids)
cross-model consensus             (frame-invariant agreement)
align-before-fold (Procrustes)    (rotate consensus into OUR base's frame)
verify vs WHNF                    (keep only structure that improves convergence)
incorporate into base plate as discrete topology
```

### The concrete ambiguity — what would Procrustes actually operate on?

**Procrustes alignment** requires two matching point clouds: a source set and a target set. The standard application is:

```
source: 9 combinator centroids in HF-model space (9 × d_ff_source)
target: 9 combinator centroids in v15 space     (9 × d_ff_v15 = 9 × 5120)
find R = argmin ‖source·R − target‖ (orthogonal, possibly scaled)
```

**This is not possible as described because:**

1. **Source centroid vectors do not exist on disk.** The NPZ files contain only Grams. To reconstruct the centroids one would need to re-run `combinator_relationship_map.py` on each HF model with an additional `np.savez` call that saves the full `Cb` array (lines 282–284 of the script, where `Cb = centroids(cmr(np.sign(gate[best_li])), labels)` — this is the one place the 9×d_ff matrix exists in memory).

2. **The v15 model has no combinator centroids in any register.** v15 (`d_model=1280`, `d_ff=5120`) is a ternary extracted model that has never been run through `combinator_relationship_map.py`. It also lacks `AutoModelForCausalLM` / HuggingFace compatibility — the script uses `AutoModelForCausalLM.from_pretrained(args.model)` at lines 259–260 and hooks `gate_proj` or `dense_h_to_4h` modules. v15 has no such interface; its FFN is `ffn_gate_plate_a` / `ffn_gate_plate_c` (line 140–143 of `v15model.py`), a ternary packed layout, not a float HF transformer.

3. **Dimensions are incommensurable.** Even if both sets of centroids existed, the HF models range from d_ff=1600 (Pythia-410m) to 17408 (Qwen3-14B). v15's d_ff is 5120. Procrustes alignment requires matching dimensions, which means either: (a) aligning in full-dimensional space (impossible across architectures), or (b) aligning in a shared reduced space. The Gram is frame-invariant precisely *because* it discards the high-dimensional frame, leaving only pairwise cosines. This is the acknowledged design trade-off.

### What "align-before-fold" actually means operationally (the knowledge page's own resolution)

The page itself resolves this ambiguity in the "Normal forms are COMPOSITIONAL and NON-UNIQUE" section:

> fold the base as FLIPS (unique, high-consensus, fold first & hard) | fold domain functions as COMPOSITION (express delta as {which base ops, what arrangement} over the shared base, then seek consensus in THAT space)

And in Open Lead #2:
> Procrustes/rotation in the base-combinator space before correlating RDMs. If tool-calling is the same function composed differently, an alignment in base coordinates should recover the shared composition.

**The intended Procrustes is in 9-dimensional combinator-label space** (the shared label space of the 9×9 Gram), not in the raw HF-model embedding space. The `alignment_in_base_coordinates` means: find the rotation of the 9 combinator nodes that minimizes the discrepancy between two models' Gram matrices, treating the 9 row-vectors of the Gram as the point cloud.

**But for the harvest-fold as described in s220 ("take the routing-register consensus, Procrustes-align into our base frame, WHNF-verify")**, the concrete interpretation must be:

1. The 9 rows of the consensus Gram (each a 9-vector of cosines) are the "consensus centroid approximation in combinator-label space."
2. The v15 model's own Gram (which does not yet exist) provides the "target frame."
3. Procrustes finds R ∈ SO(9) mapping consensus-gram-rows → v15-gram-rows.
4. The aligned direction for each "positive edge" (e.g. B–D) is then a direction in v15's combinator-label space.

**The critical missing piece to make this well-posed:** v15 must first be probed with `combinator_relationship_map.py` (adapted for the ternary/MLX architecture) to obtain its own 9×9 Gram. Only then does a target frame exist for Procrustes. Without it, "align into the v15 frame" has no target.

### Summary of ambiguities that must be resolved before building

| Ambiguity | Status | Resolution needed |
|-----------|--------|-------------------|
| Do consensus centroids (full-dim vectors) exist? | **NO** — only Grams on disk | Must re-run `combinator_relationship_map.py` with centroid-save patch, OR accept Gram-level alignment |
| Do v15 combinator centroids exist? | **NO** — v15 never probed | Must build a v15-compatible map script (see §5) |
| Is Procrustes in full-dim space or 9-dim label space? | Ambiguous in the knowledge page | Knowledge page's own resolution: 9-dim label space (Gram rows as point cloud) |
| "Fold direction" = what concrete object? | Unspecified | Must decide: a sign-vector in v15's d_ff=5120 space — which requires full-dim centroids |
| Target combinator centroids in v15 frame | Does not exist | Prerequisite: run adapted map script on v15 checkpoint |

---

## 4. EXP-B OPERATOR LOADER: Code structure and reuse points

**File:** `scripts/experiments/exp_b_self_verifying_acceptance.py`

### Model loading (lines 78–96 of the script)

```python
cfg = V15Config()
if Path(args.extracted_model_path).exists():
    cfg.extracted_model_path = args.extracted_model_path
model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
if args.checkpoint and Path(args.checkpoint).exists():
    model.load_weights(args.checkpoint, strict=False)
    mx.eval(model.parameters())
    n_reduced = reduce_all_deltas(model)   # ← folds trained deltas into base
    mx.eval(model.parameters())
model._n_outer_passes = args.n_outer
model._fixed_point_lambda = 0.0           # eval only, no training
```

- `create_model_with_deltas` is in `scripts/v15/train_td.py` — builds `V15Model` and converts `TernaryLinear` FFN modules to `DeltaTernaryLinear` via `convert_to_delta`.
- `--extracted-model-path` is `checkpoints/v15-extracted/model.npz` (the frozen base).
- `--checkpoint` is a **trained** `model.npz` (e.g. `checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz`). After loading, `reduce_all_deltas` folds the trained delta into the base so further perturbations start from the trained operator, not the frozen extract.

### "Fold a delta into base" in code (`scripts/v15/td_delta.py`)

The word "fold" is used precisely:

| Function | Location | What it does |
|----------|----------|--------------|
| `DeltaTernaryLinear.reduce()` | line 1375 | `new_base = base ⊙ delta` (ternary multiply); `new_delta = all +1`. Lossless. |
| `reduce_all_deltas(model)` | line 1538 | Walks all `named_modules()`, calls `.reduce()` on every `DeltaTernaryLinear`. Returns count. |
| `convert_to_delta(model, ...)` | line 1449 | Converts in-place: each matching `TernaryLinear` → `DeltaTernaryLinear.from_ternary_linear(tl)`, freezing the original weight as `base_weight`, initializing `delta_weight = all +1`. |
| `collect_delta_params(model)` | line 1507 | Returns list of `(path, DeltaTernaryLinear)` — utility for enumerating live delta modules. |

The effective weight at any point is:
```
effective = base ⊙ delta   (element-wise ternary multiply)
output = quantized_matmul(norm(x), pack(effective), gamma_scales, gamma_biases)
```

### How exp_b perturbs the routing register and measures ΔCE vs Δ(Δx_conv)

1. **INSTRUMENT GUARD** (lines 131–163): Iterates `named_modules()`, finds all `TernaryLinear | DeltaTernaryLinear` matching `--module-filter` (default `"ffn_gate"`). For each, flips half the nonzero positions, runs a forward pass, checks `|ce_probe - ce0| > 1e-4` ("LIVE"), restores. Only the first live module is used as target.

2. **Perturbation loop** (lines 176–196): For each `flip_frac` in the quality spectrum, randomly selects `B = max(1, int(frac * n_positions))` nonzero routing positions and sign-flips them (multiplies by −1 in the unpacked int8 array), then repacks via `pack_ternary_mlx`.

3. **Measurement** via `forward_metrics()` (lines 84–93):
   ```python
   model._prev_alg_c = None   # clean algedonic state
   _, _ = model(tokens, targets)
   ce = float(model._last_ce.item())
   curve = [float(d.item()) for d in model._last_outer_deltas]
   dx_conv = curve[-1]        # ‖x_c^K − x_c^{K-1}‖/‖x_c^{K-1}‖
   ```
   `_last_ce` and `_last_outer_deltas` are set inside `v15model.py`'s `__call__` (lines 442 and 334 of v15model.py).

4. **Analysis**: Pearson + Spearman between `dCE` and `dDx`; ROC for "reject if Δx_conv rises."

### Entry-point reusable as WHNF-verify hook

**`forward_metrics(model, tokens, targets)` → `(ce, dx_conv, curve)`** is the exact hook. It requires only a loaded model with `_n_outer_passes ≥ 2` and `_fixed_point_lambda = 0.0`. The acceptance criterion is:

```python
accept(candidate_delta) ⟺ dx_conv ≤ dx0 + epsilon
```

The entire `apply_flip` / `reset_flip` / `forward_metrics` pattern in exp_b is directly reusable for any candidate direction: inject a direction as a sign pattern into a target module, measure `dx_conv`, restore. The harvest-fold experiment would replace `apply_flip` (random flips) with `apply_direction` (structured flip pattern derived from a harvest centroid direction).

**Concrete reuse boundary:**
- `forward_metrics` → copy verbatim as the WHNF-verify call
- `apply_flip` / `reset_flip` → replace with direction-specific inject/restore
- The INSTRUMENT GUARD pattern → reuse to confirm the live module is `ffn_gate_plate_a` or `ffn_gate_plate_c` in the v15 model

---

## 5. V15 COMBINATOR CENTROIDS: Do they exist? Can `combinator_relationship_map.py` load v15?

### Do v15 centroids exist anywhere?

**No.** Searching all results directories and NPZ files yields no v15-specific combinator relationship map. `results/combinator-relationship-map/` contains 10 HF models only. No v15 entry exists anywhere in that directory or in any other results subdirectory.

### Can `combinator_relationship_map.py` load a v15 checkpoint as-is?

**No, for three hard architectural reasons:**

1. **HuggingFace dependency (line 58, 259–260):** The script imports `from transformers import AutoModelForCausalLM, AutoTokenizer` and loads via `AutoModelForCausalLM.from_pretrained(args.model)`. v15 is an MLX ternary model loaded via `create_model_with_deltas(V15Config(), ...)` + `model.load_weights(path)`. These loading paths are entirely incompatible.

2. **Gate module naming (lines 71–77):** The script hooks `gate_proj` or `dense_h_to_4h` via a regex `r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$"`. v15's FFN gate modules are named `ffn_gate_plate_a` and `ffn_gate_plate_c` (v15model.py lines 140, 143) — completely different names, different module tree layout.

3. **Ternary pack format:** Even if the module were found, `gate[li]` in the script is a float32 pre-activation array captured via a PyTorch forward hook. v15's gate is packed uint32 (ternary, 2-bits-per-weight), output is float via quantized matmul. A hook would capture the post-matmul float output, not the pre-activation routing sign — a different register.

### What must be built

A **v15-adapted map script** (`scripts/experiments/combinator_relationship_map_v15.py`) needs to:

1. Load via `create_model_with_deltas(V15Config())` + `model.load_weights(checkpoint_path, strict=False)` + `reduce_all_deltas(model)`.
2. Hook `ffn_gate_plate_a` and `ffn_gate_plate_c` (the shared stride stack's gate plates). Since the v15 model uses a SHARED stride stack (not per-layer independent modules), the appropriate probe point is the effective weight matrix: `unpack_ternary_mlx(mod._compute_effective())` → sign of that → routing register.
3. Replace the `collect()` function with an MLX forward pass that captures the `ffn_gate` pre-activation via an MLX hook or explicit instrumentation.
4. The centroid computation (`centroids()`, `cmr()`, `gram()`) is pure numpy and can be reused as-is.
5. **Save the full-dimensional centroid array** (`Cb` of shape `(9, d_ff)` = `(9, 5120)`) to the NPZ — this is what the existing script does NOT save and what the harvest-fold needs.

---

## 6. CHECKPOINT AVAILABILITY

**`checkpoints/v15-td-outer-k2-fp5-5k/`** contains:
```
flip_map_latest.npz
flip_map_step_001000.npz
step_001000/
  delta_plates.npz      ← 152 arrays of shape (1280, 80) uint32 — packed ternary delta plates
  model.npz             ← 529 arrays — full model weights including gamma, norms, VSM structure
  optimizer.npz
  state.json
train_td_log.jsonl
```

**`step_001000/model.npz`** is the only step checkpoint. It contains the trained base weights (float32 norms, gamma scales, and uint32 packed ternary plates). **READ-ONLY** — the active training process (tmux main:1) writes `flip_map_latest.npz` and `train_td_log.jsonl` to the parent directory and will eventually write `step_002000/` etc. The `step_001000/` subdirectory is frozen after that step and is safe to read.

**Confirmed safe reads:** `step_001000/model.npz` and `step_001000/delta_plates.npz`. The `flip_map_latest.npz` and `train_td_log.jsonl` at the parent level are being actively written by main:1 — do not open for writing, but read-only is safe if done quickly (the write interval is once per thousand steps, and `np.load(..., mmap_mode='r')` would be safe).

**Delta plates format (from `delta_plates.npz`):**
```
shared_stride_stack_layers_{0..N}_{q,k,v,out}_proj_{delta_packed,stats}
```
- `*_delta_packed`: `(1280, 80)` uint32 — packed 2-bit ternary delta plate
- `*_stats`: `(4,)` float32 — TernaryDescent statistics

No `ffn_gate_plate` keys appear in the delta_plates (only attention projections are delta-ized in the current training config). The FFN gate plates remain as `TernaryLinear` base plates in `model.npz`.

---

## 7. GPU/COMPUTE FOOTPRINT TABLE

| Step | Operation | Backend | Footprint | Safe alongside main:1? |
|------|-----------|---------|-----------|----------------------|
| Read `consensus.json`, `scale.json`, per-model JSONs | File I/O | CPU | Negligible | ✅ YES |
| Read per-model NPZ (Gram arrays only) | `np.load` | CPU | ~1 MB each | ✅ YES |
| Compute 9×9 Gram-level Procrustes (9-dim) | numpy/scipy | CPU | Microseconds | ✅ YES |
| Build v15-adapted combinator map script | Code authoring | — | — | ✅ YES |
| Load `step_001000/model.npz` via `model.load_weights` (MLX) | CPU+MLX | CPU/GPU (small) | v15 = ~50M params | ⚠️ CAUTION: MLX will use GPU metal; brief, low intensity |
| Probe v15 with 535 crystal probes (forward passes, MLX) | MLX forward | **GPU/MLX** | 535 × full forward | ❌ DO NOT run alongside main:1 |
| Re-extract full centroid vectors from HF models | PyTorch forward | **GPU** (if MPS) or CPU | Large HF model + 535 probes | ❌ GPU: defer; CPU-only mode possible |
| Procrustes in full d_ff space (9 × 5120 vs 9 × d_ff) | numpy SVD | CPU | <1 second | ✅ YES (once centroids exist) |
| `exp_b_self_verifying_acceptance.py` (the WHNF-verify hook) | MLX forward | **GPU/MLX** | v15 + 4 seqs × 512 tokens | ❌ Contends with main:1 (s219 precedent) |
| Analysis: Pearson/Spearman correlation, PPL comparison | numpy | CPU | Negligible | ✅ YES |
| Batch fold direction injection + single forward per candidate | MLX | **GPU/MLX** | Same as exp_b | ❌ Defer until main:1 completes |
| Read `results/exp-b-self-verifying/result.json` (existing) | File I/O | CPU | Negligible | ✅ YES |

**Key rule:** Any MLX/metal forward pass on v15 allocates GPU memory and metal command queues that contend with main:1's training loop. The s219 incident (GPU contention stalled training) applies here. All actual forward passes through v15 must wait until main:1 completes or pauses voluntarily.

**Exception:** loading `model.npz` into Python + calling `model.load_weights` without actually running a forward pass is CPU-only — safe, but borderline if MLX pre-allocates buffers.

---

## Summary: (a) Data reality, (b) Well-posedness, (c) Exact files/functions, (d) Recommended procedure, (e) Footprint table

### (a) What data actually exists

| Item | Exists? | Location | Format |
|------|---------|----------|--------|
| Cross-model consensus Gram (9×9) | ✅ | `results/combinator-map-consensus/consensus.json` → `consensus_gram` | Nested list of floats |
| Universal positive edges (B–D, B–C, K–C, S–D, S–Y) | ✅ | `consensus.json` → `universal_edges` | Per-edge scalar + per-model scalars |
| Per-model Grams at multiple depth fractions | ✅ | `results/combinator-relationship-map/*.npz` | 9×9 float32 arrays |
| Per-model MDS/PCA 2D coordinates | ✅ | `results/combinator-relationship-map/*.json` → `map.mds_coords`, `map.pca_coords` | 2D only |
| Per-combinator centroid vectors (full-dim, HF models) | ❌ | Not saved | Must re-run with patch |
| v15 combinator centroids | ❌ | Does not exist | Must build adapted script |
| v15 checkpoint (step 1000) | ✅ | `checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz` | 529-key NPZ, READ-ONLY |
| Exp-B acceptance result | ✅ | `results/exp-b-self-verifying/result.json` | JSON |

### (b) Is the harvest-fold well-posed as described?

**Partially.** The knowledge page narrative is correct in principle but leaves an under-specified gap. The current state is:

- **The Gram-level harvest is well-posed and can be done now (CPU-only).** The 9 rows of the consensus Gram are combinator "position vectors" in the 9-dimensional label space. Procrustes alignment of these 9-vectors from the consensus frame to a target v15 frame is well-defined — **but requires a v15 Gram first.**

- **The full-dimensional harvest (what would actually be folded into v15's weight space) requires reconstructing centroid vectors in HF model space and then aligning them to v15's d_ff=5120 space.** This is architecturally incommensurable without a reduction step (e.g., project both into the shared 9-dim Gram-space first and work there, or build a cross-architecture alignment via the crystal probes).

- **The most actionable interpretation:** use the Gram-level Procrustes to find which combinator pairs are "nearest" in v15's routing topology, then construct a "fold direction" as a signed difference of v15's own centroid vectors (which must first be measured). The "positive edges" from the consensus tell you *which* pairs to strengthen; the v15 centroids tell you *which direction in v15's space* to move. The consensus Gram is the prescription; the v15 Gram is the coordinate system.

**The harvest-fold needs reformulation** from "Procrustes-align consensus centroids into v15 frame" (requires full-dim vectors that don't exist) to "measure v15's own combinator Gram, then use the consensus positive edges as a prescription for which directions to reinforce in v15's routing register."

### (c) Exact files and functions to reuse

| Purpose | File | Function/entry-point | Lines |
|---------|------|---------------------|-------|
| WHNF-verify hook | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `forward_metrics(model, tokens, targets)` | 84–93 |
| Live module detection | `scripts/experiments/exp_b_self_verifying_acceptance.py` | The INSTRUMENT GUARD loop | 117–163 |
| Sign-flip injection | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `apply_flip(flat_idx)` / `reset_flip()` | 170–176 |
| Fold delta into base | `scripts/v15/td_delta.py` | `reduce_all_deltas(model)` | 1538–1547 |
| Delta module conversion | `scripts/v15/td_delta.py` | `convert_to_delta(model, include, exclude)` | 1449–1506 |
| Enumerate live deltas | `scripts/v15/td_delta.py` | `collect_delta_params(model)` | 1507–1535 |
| Load trained v15 checkpoint | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `create_model_with_deltas(cfg, convert_ffn=True)` + `model.load_weights(path)` + `reduce_all_deltas` | 78–96 |
| Centroid / Gram computation | `scripts/experiments/combinator_relationship_map.py` | `centroids()`, `cmr()`, `gram()`, `silhouette_null()` | 168–210 |
| Crystal probes | `src/verbum/probes/library.py` | `crystal_probes()` | (library) |
| Classical MDS (2D embedding) | `scripts/experiments/combinator_relationship_map.py` | `classical_mds(D, k=2)` | 211–219 |
| v15 model + config | `scripts/v15/v15model.py`, `scripts/v15/config.py` | `V15Model`, `V15Config` | v15model.py |

### (d) Recommended procedure for `combinator_harvest_fold.py`

**Phase 0 (CPU-only, safe now):**
1. Read `consensus.json`, extract the five positive universal edges and their per-model values.
2. Parse `results/combinator-relationship-map/Qwen_Qwen3-{4B,8B,14B}.json` (the mid-scale harvest band per s220). For each, read `map.gram` and `map.mds_coords` from the JSON. Compute a 9×9 "harvest Gram" by averaging across the 4–14B band.
3. Patch `combinator_relationship_map.py` to also save the full-dimensional centroid array `Cb` (line 282: `Cb = centroids(cmr(np.sign(gate[best_li])), labels)`, shape `[9, d_ff]`) to the NPZ under the key `centroids_cmr_best`. This is a 3-line change, CPU-side, no forward passes needed — just save what's already computed.
4. Decide the alignment strategy (Gram-level vs full-dim) and document it before building.

**Phase 1 (MLX/GPU, defer until main:1 pauses):**
5. Build `scripts/experiments/combinator_relationship_map_v15.py` adapting the script for MLX/ternary architecture:
   - Use `create_model_with_deltas(V15Config())` + `model.load_weights("checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz", strict=False)` + `reduce_all_deltas(model)`.
   - Hook `shared_stride_stack.layers[i].ffn_gate_plate_a` and `ffn_gate_plate_c`. Since the stride stack is shared (not per-layer-separate), capture the gate's float output during forward passes at each `_n_outer_passes` iteration. Record `sign(gate_output)` per probe.
   - Run with 535 crystal probes, output `results/combinator-relationship-map/v15_step001000.{json,npz}` with full centroid arrays saved.

6. Run exp_b acceptance test on `step_001000/model.npz` (or whichever step is available when main:1 pauses), using `--module-filter ffn_gate` to confirm the live gate module (the INSTRUMENT GUARD will identify the correct name). Establish `(ce0, dx0_conv)` baseline.

**Phase 2 (CPU, after Phase 1 data exists):**
7. Compute the Gram-level Procrustes: align the harvest Gram rows (9×9, consensus) to the v15 Gram rows (9×9, measured). Find R ∈ O(9) via SVD of `v15_gram.T @ harvest_gram`.
8. For each of the five positive universal edges (B–D, B–C, K–C, S–D, S–Y), compute a "fold direction" in v15's d_ff=5120 space as:
   ```
   direction(A, B) = centroid_v15[B] - centroid_v15[A]   (aligned to the positive edge)
   ```
   This uses v15's own centroids (from Phase 1), guided by the consensus prescription (which edges are "universally positive").
9. Binarize each direction: `fold_signs = sign(direction)`, shape `(5120,)`. This is the candidate flip pattern to inject into the v15 routing register.

**Phase 3 (MLX/GPU, defer until main:1 pauses):**
10. For each candidate direction (one per positive edge × a few variations), inject into the live FFN gate plate using the `apply_flip` / `forward_metrics` pattern from exp_b. Measure `(dCE, d_dx_conv)`.
11. Accept the direction if `d_dx_conv ≤ epsilon` (WHNF-verify). Reject otherwise.
12. Fold accepted directions via `DeltaTernaryLinear.reduce()` into the base.
13. Measure downstream PPL on a held-out shard (e.g. the first 1000 tokens of `shard_00001.npy` that `load_token_batch` can pull) versus the pre-fold baseline.
14. Report: does verified ecosystem-consensus add beyond the universal crystal?

### (e) CPU vs GPU footprint (concise)

**Safe to run now (CPU-only):**
- All file reading and JSON analysis (Phases 0 and 2 above)
- Numpy centroid/Gram/Procrustes computation
- Patching `combinator_relationship_map.py` to save full centroids (code change only)
- Writing `combinator_harvest_fold.py` framework (code authoring)

**Must defer until main:1 pauses:**
- Any MLX forward pass through v15 (Phases 1 and 3)
- Re-running `combinator_relationship_map.py` on HF models (GPU/MPS)
- Exp-B acceptance runs on v15 checkpoints
- PPL measurement

**The s219 GPU-contention risk is real:** even brief MLX allocations on the metal GPU compete with main:1's training loop. Everything that touches MLX forward passes must wait.

---

### Critical flags for pre-build review

1. **The Gram-only storage is the root constraint.** The entire "Procrustes into v15 frame" narrative requires full-dimensional centroid vectors. These do not exist on disk. The 3-line patch to `combinator_relationship_map.py` (save `Cb` to NPZ) is the single most important infrastructure fix — but re-running it on the HF models requires GPU time.

2. **v15 is not an HF model.** `combinator_relationship_map.py` cannot load it. A new v15-adapted script is mandatory, not optional, before any "v15 frame" exists.

3. **The "fold direction" concept bridges two representations.** The consensus data lives in relational (Gram) space; the fold injection lives in v15's sign-vector space (`[5120,]` int8). The bridge is: (a) measure v15's own centroids, (b) use consensus positive edges as a prescription for which centroid-pairs to reinforce. This is well-posed once v15 centroids exist. Without them, there is no concrete fold direction to inject.

4. **Exp-B baseline result already exists** at `results/exp-b-self-verifying/result.json`. Read it before running Phase 3 — it may already answer whether the acceptance signal is valid on the current checkpoint.
```

#### Subagent Messages

## User

Map the exact integration points needed to build a "combinator harvest fold" experiment in the Verbum repo (/Users/mwhitford/src/verbum). This is RESEARCH PLUMBING analysis — do NOT run any GPU-heavy code or training; reading files and inspecting small JSON/npz is fine. A multi-day training process is running (tmux main:1) and MUST NOT be disturbed.

GOAL of the eventual experiment (context, not your task): take "universal positive edges" between lambda-calculus combinators (B-D, B-C, K-C, S-D, S-Y) found in a cross-model consensus, construct candidate "fold directions" in the v15 model's base frame via Procrustes alignment, WHNF-verify each candidate against the contractive operator using the existing Exp-B acceptance mechanism, then measure downstream PPL vs base. Falsifiable question: does verified ecosystem-consensus add beyond the universal crystal already in the base?

YOUR TASK — produce a precise written design report (no code changes) answering:

1. CONSENSUS DATA: Read results/combinator-map-consensus/consensus.json and results/combinator-map-consensus/scale.json. Document their exact JSON structure. CRITICAL: does consensus.json contain consensus CENTROIDS (vectors in some embedding space) or ONLY the relational 9x9 Gram (cosines between combinators)? List the keys and what edge/centroid data is actually available to harvest.

2. PER-MODEL CENTROIDS: Inspect results/combinator-relationship-map/*.json and *.npz (e.g. via python -c numpy load, list .npz keys and array shapes for one model like Qwen_Qwen3-14B.npz). Are per-combinator centroid VECTORS stored, or only Gram matrices? What dim/frame are they in? This determines whether "consensus centroids" even exist in a shared space or must be reconstructed.

3. THE FRAME PROBLEM: The knowledge page mementum/knowledge/explore/consensus-delta-folding.md says the Gram is frame-invariant BY DESIGN precisely because raw centroids are NOT cross-model comparable. Read the relevant sections (search for "frame", "Procrustes", "align-before-fold"). Explain concretely: what would "Procrustes-align consensus into the v15 base frame" actually operate on, given we may only have a relational Gram and no shared-space centroids? Is the harvest-fold as described even well-posed, or does it need the per-model centroids + a target combinator centroid set in the v15 frame? Flag any ambiguity that must be resolved before building.

4. EXP-B OPERATOR LOADER: Read scripts/experiments/exp_b_self_verifying_acceptance.py thoroughly. Document: how it loads the v15 model + a checkpoint (the --checkpoint arg, the model class, the npz format); what "fold a delta into base" means in code (look for reduce_all_deltas, collect_delta_params, convert_to_delta in scripts/v15/td_delta.py and scripts/v15/v15model.py); how it perturbs the routing register and measures ΔCE vs Δ(Δx-at-convergence); and exactly which function/entry-point could be reused as the WHNF-verify hook for a candidate fold direction.

5. V15 COMBINATOR CENTROIDS: Does the v15 model have its own combinator centroids anywhere, or would they need to be produced by running combinator_relationship_map.py on the v15 model? Check whether combinator_relationship_map.py can even load a local v15 checkpoint (it likely loads HF models). Read its model-loading code. Note: v15 is a small extracted/ternary model, architecturally different from the HF models.

6. CHECKPOINT AVAILABILITY: Confirm what checkpoints exist read-only at checkpoints/v15-td-outer-k2-fp5-5k/ (ls) — the running training writes there; we may only READ step_001000/model.npz, never write to that dir.

7. GPU/COMPUTE FOOTPRINT: For each step of the eventual experiment, classify it as CPU-cheap (safe to run alongside main:1) vs GPU/MLX-heavy (would contend with main:1 and risk stalling it, as happened in s219). This determines what can be done now vs deferred.

DELIVERABLE: A structured report with: (a) what data actually exists (centroids vs Gram), (b) whether the harvest-fold is well-posed as described or needs reformulation, (c) the exact files/functions/entry-points to reuse, (d) a concrete recommended procedure for combinator_harvest_fold.py, (e) a CPU-vs-GPU footprint table so we know what's safe to run now. Cite exact file paths and line numbers / function names. Be honest about ambiguity and any mismatch between the knowledge-page narrative and what the code/data actually supports.


### Thinking

Let me systematically explore the Verbum repository to answer all the questions. I'll start by reading multiple files in parallel.

## Assistant

I'll work through all seven investigation threads in parallel where possible, then synthesize. Starting with a broad tree scan and reading the key files simultaneously.

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum",
  "max_depth": 3
}
```

**Summary:** Listing tree: verbum

**Output:**
```
/Users/mwhitford/src/verbum
 AGENTS.md
 EQUATIONS.md
 LICENSE
 README.md
 bb
  us
   whitford
 bb.edn
 checkpoints
  a-vsm-lm-v6
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
  basin
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  basin-v2-d512
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
  basin-v3-d512
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  compressor-lm
  compressor-lm-iterative
  micro
   final
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
  mini-baseline
   step_000500
   step_001000
   step_001500
   step_002000
  mini-dispatch-4op
   step_000500
   step_001000
   step_001500
   step_002000
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
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  v10-consensus
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
  v10-mixed
   step_001000
   step_002000
   step_003000
  v10-multicycle
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
  v10-spiral
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v10-topk
   step_001000
   step_002000
   step_003000
  v10-vsm
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  v11
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v11-holo
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v11-holo-inv
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
  v12-crystal-write-r60
  v12-distill-run1
   best
   etch_round_001
   etch_round_002
   etch_round_003
   etch_round_004
   etch_round_005
   gamma_seeded
   step_002000
   step_004000
  v12-distill-run2
   best
   step_002000
   step_004000
   step_006000
   step_008000
   step_010000
   step_012000
  v12-holo-8op
   round_0005
   round_0010
   round_0015
   round_0020
   round_0025
   round_0030
   round_0035
  v12-holo-consensus
   round_0016
   round_0017
  v12-holo-consensus-smoke
   round_0001
   round_0002
  v12-holo-focused
   round_0040
   round_0045
   round_0050
   round_0055
   round_0060
  v12-holo-lattice
   round_0065
  v12-holo-lattice-v2
   round_0065
   round_0070
  v12-holo-resume-test
  v12-holo-run1
   round_0005
  v12-holo-smoke
   round_0001
  v12-run1
   step_001000
   step_002000
   step_003000
   step_004000
  v12-run2
   step_001000
  v12-run3
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
  v12-run4
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
  v12-run6
  v12-run7
   step_000500
   step_001000
  v13
  v13-distilled
  v13-distilled-tree
  v13-etched
  v13-etched-full
  v13-etched-full-v2
  v13-etched-tree
  v13-rb
  v13-run1
  v13-run2
   step_000500
   step_001000
  v13-run3
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
  v13-run4
   step_000500
  v13-run5-full-etch
  v13-run6-crystal-warmup
  v13-run7-td-adam-sync
  v13-run8-geometry
   step_000500
  v13-run9-swiglu
  v13-td
   step_000500
   step_001000
   step_001500
  v13-td-r10
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
  v14-composed
  v14-extracted
  v14-extracted-2stack
  v14-kd
   step_000500
   step_001000
  v14-kernel-test
   step_000020
  v14-mmap
   snapshots
   step_003000
   step_003000_old
   step_003500
   step_004000
  v14-td
   step_000500
   step_001000
   step_001500
   step_001500_folded
   step_002000
   step_002500
   step_003000
  v14-td-2stack
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
  v15-dolma
   step_0001000
   step_0002000
  v15-expb-base
   step_000200
   step_000400
  v15-extracted
   attention
   model.npz
   strides
  v15-hpe-dolma
   step_0002000
   step_0003000
   step_0004000
   step_0005000
   step_0005000_prepared
  v15-mask-dolma
   step_0005000
   step_0005170
  v15-td
   step_000500
   step_001000
   step_001500
   step_002000
  v15-td-ab-exact
   step_000250
  v15-td-ab-exact-lam0.1
   step_000250
  v15-td-ab-exact-nos2-lam0.1
   step_000250
  v15-td-ab-proxy
   step_000250
  v15-td-outer-k2
   step_000250
  v15-td-outer-k2-fp1
  v15-td-outer-k2-fp5
   step_000250
  v15-td-outer-k2-fp5-5k
   step_001000
  v15-train
   step_0001000
   step_0002000
   step_0003000
   step_0004000
  v15-train-smoke
   step_0000005
  v15-zeroed
   attention
   strides
  v15-zeroed-dolma
   step_0001000
   step_0002000
  v6-etched-360
  v8-bios
   step_002500
   step_005000
   step_007500
   step_010000
   step_012500
   step_015000
   step_017500
   step_020000
   step_022500
   step_025000
   step_027500
   step_030000
   step_032500
   step_035000
  vsm-lm
  vsm-lm-v2
  vsm-lm-v3
  vsm-lm-v3.1
  vsm-lm-v3.2
  vsm-lm-v4
  vsm-lm-v4.1
  vsm-lm-v5
  vsm-lm-v6
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
   step_006000
   step_006500
   step_007000
   step_007500
   step_008000
   step_008500
   step_009000
   step_009500
   step_010000
   step_010500
   step_011000
   step_011500
   step_012000
   step_012500
   step_013000
   step_013500
   step_014000
   step_014500
   step_015000
   step_015500
   step_016000
   step_016500
   step_017000
   step_017500
   step_018000
   step_018500
   step_019000
   step_019500
   step_020000
   step_020500
   step_021000
   step_021500
   step_022000
   step_022500
   step_023000
   step_023500
   step_024000
   step_024500
   step_025000
   step_025500
   step_026000
   step_026500
   step_027000
   step_027500
   step_028000
   step_028500
   step_029000
   step_029500
   step_030000
   step_030500
   step_031000
   step_031500
   step_032000
   step_032500
  vsm-lm-v6-etched
  vsm-lm-v7
   step_000005
   step_010000
   step_020000
   step_030000
   step_040000
  vsm-trial
 data
  compile-eval.jsonl
  compile-full.json
  compile-test.jsonl
  compile-train.jsonl
 docs
  v10-architecture.svg
  v11-architecture.svg
  v6-design.md
  vsm-tesseract.mmd
  vsm-tesseract.svg
 gates
  README.md
  ablation-empty.txt
  ablation-engage-line.txt
  ablation-example.txt
  ablation-fol.txt
  ablation-formal-semantics.txt
  ablation-lambda-calculus.txt
  ablation-lambda-symbol.txt
  ablation-lambda-word.txt
  ablation-montague.txt
  ablation-output-lambda-only.txt
  ablation-output-only.txt
  ablation-preamble-bridge.txt
  ablation-preamble-full.txt
  ablation-preamble-only.txt
  ablation-role-compiler.txt
  ablation-role-lambda-compiler.txt
  ablation-role-plus-terse.txt
  ablation-symbols-cluster.txt
  ablation-symbols-line.txt
  ablation-tensor-line.txt
  ablation-translate-formal.txt
  ablation-translate-lambda.txt
  classify.txt
  compile-ambient.txt
  compile-base.txt
  compile-binding-hybrid.txt
  compile-binding-hybrid3.txt
  compile-binding-montague.txt
  compile-binding-scope.txt
  compile-binding-typed.txt
  compile-minimal.txt
  compile-suggestive.txt
  compile.txt
  decompile.txt
  exemplar-arrow-only.txt
  exemplar-both.txt
  exemplar-complex-montague.txt
  exemplar-montague-rich.txt
  exemplar-montague.txt
  exemplar-nucleus-rich.txt
  exemplar-nucleus.txt
  extract.txt
  null.txt
  self-ref-bidirectional.txt
  self-ref-bridge.txt
  self-ref-constrained.txt
  self-ref-fixed-point.txt
  self-ref-minimal.txt
  self-ref-quine.txt
  self-ref-structural.txt
  self-ref-typed.txt
  summarize.txt
  task-causality.txt
  task-classify.txt
  task-continue.txt
  task-coreference.txt
  task-correct.txt
  task-counterfactual.txt
  task-decompose.txt
  task-disambiguate.txt
  task-elaborate.txt
  task-entail.txt
  task-formalize.txt
  task-keyword.txt
  task-modality.txt
  task-negate.txt
  task-paraphrase.txt
  task-presuppose.txt
  task-question.txt
  task-scope.txt
  task-sentiment.txt
  task-simplify.txt
  task-structure.txt
  task-summarize.txt
  task-title.txt
  task-translate.txt
  translate.txt
 lattice
  backbone_seed.json
  basin_probes.json
  basins-v1
   basin_lattice.json
  basins_v1_run.log
  binding-v1
   universal_lattice.json
   universal_lattice.npz
  binding_chain_probes.json
  binding_v1_run.log
  crystal_spine
   all_results.json
   mistral-7b.json
   olmo-2-13b.json
   probes.json
   pythia-2.8b.json
   qwen3-0.6b.json
   qwen3-14b.json
   smollm3-3b.json
  crystal_spine_run.log
  diverse_corpus.json
  extraction.log
  fixedpoint
   universal_lattice.json
  fixedpoint-v2
   universal_lattice.json
  fixedpoint_corpus.json
  fixedpoint_lattice_run.log
  fixedpoint_probes.json
  fixedpoint_v2_run.log
  lattice_5model
   universal_lattice.json
  lattice_5model_run.log
  lattice_6model_run.log
  lattice_qwen36_27b_run.log
  reduction_chain_probes.json
  tool_crystal
   analysis.json
   probes.json
  tool_crystal_run.log
  universal_lattice.json
  universal_lattice.npz
 lens
  warped_lens.json
 mementum
  knowledge
   INDEX.md
   attention-sparsity.md
   audit-meta-pattern.md
   audit-registry.md
   binding-graph-trace.md
   chats
   combinator-addressing.md
   compilation-pipeline.md
   computed-beam.md
   crystal-laplacian.md
   crystal-multi-tree.md
   crystal-native-architecture.md
   crystal-phi-derivation.md
   crystal-sieve-architecture.md
   crystal-trace-tooling.md
   crystal-universality.md
   crystal-validity-and-fidelity.md
   diffusion-holographic-isomorphism.md
   dimensional-analysis.md
   direct-delta-adjunction.md
   dvd-stamp-topology.md
   error-correction-theory.md
   explore
   extraction-methodology.md
   extraction-sign-accuracy.md
   ffn-circuit-types.md
   ffn-reduction-trace.md
   fibonacci-strides.md
   function-discovery.md
   gradient-zero-map.md
   gtsm-search-space.md
   head-combinator-isa.md
   hologram-reader-vsm.md
   holographic-computer.md
   holographic-error-correction.md
   holographic-etch.md
   holographic-sign-correction.md
   hpe-restoration.md
   l0-characterization.md
   lambda-halt-continuation.md
   lambda-machine.md
   lambda-tracer-diagnostic.md
   manifold-axis-and-topology.md
   mathematical-convergences.md
   mechanism-extraction.md
   mode-semantics.md
   moire-addressing.md
   mspace-gemcutter.md
   opcode-instrument.md
   phi-information-partition.md
   progressive-collapse.md
   project-thesis.md
   psi-evaluation-synthesis.md
   recursion-mirrors.md
   residual-covariance-rank.md
   retrieval-lattice.md
   saliency-aware-sieve.md
   score-matching-compression.md
   session-153-notes.md
   sign-correction-topology.md
   standing-wave-magnitudes.md
   symbol-isolation.md
   td-oscillation-problem.md
   ternary-compounding.md
   ternary-dual-equation.md
   ternary-plate-extraction.md
   tiny-classifier-ternary.md
   topology-gradient-separation.md
   trace-guided-etching.md
   training-protocols.md
   tsp-trajectory-distillation.md
   two-registers-of-topology.md
   v14-architecture.md
   v15-attention-assessment.md
  memories
   5d-crystal-lattice-hypothesis.md
   a3b-types-prose.md
   alternating-overlay-mechanism.md
   auto-rollback-anti-pattern.md
   backbone-plus-etch-beats-float32.md
   beams-not-plates-are-the-etch.md
   beta-reduction-filesystem.md
   bottom-found.md
   c-boot-rotation-sequence.md
   coevolution-works.md
   combinator-bootstrap-dependency.md
   combinator-dispatch-floors.md
   combinator-fingerprints-are-late-layer.md
   composed-transforms-are-ternary.md
   compression-phase-transition.md
   compressor-in-5d-lattice.md
   compressor-not-compiler.md
   continuations-are-the-key.md
   copy-computation-not-weights.md
   crystal-bootloader-thesis.md
   crystal-gates-hologram.md
   crystal-is-error-correcting-code.md
   crystal-null-too-coarse.md
   crystal-programming-language.md
   crystal-rotation-is-attention.md
   crystal-token-decomposition.md
   crystal-universality-proof.md
   decompilation-not-extraction.md
   dedicated-combinator-capacity.md
   dedicated-plates-vsm-emergent-depth.md
   deductive-origin.md
   delta-plate-ecosystem-vision.md
   delta-plate-solves-attention-etch.md
   dispatch-monopoly-fix-ema-depth.md
   dissolved-dispatch-kernel.md
   dual-storage-restore-tool.md
   eigendecomposition-is-beta-reduction.md
   einstein-crystal-manifold.md
   etch-first-with-attention.md
   etch-unetch-symmetry.md
   evolution-mechanism-broken.md
   evolutionary-descent-ternary.md
   extract-giant-into-tiny-plate.md
   extraction-methodology-confusion.md
   ffn-depth-is-a-lens.md
   ffn-topology-is-transferable.md
   ffn-two-functional-groups.md
   fifty-sessions-of-bedrock.md
   fractal-beta-reduction.md
   freeze-then-gd-wins.md
   gate-is-the-beamformer.md
   gd-converges-in-100-steps.md
   gem-cut-beats-float32.md
   grad-clipping-not-optional.md
   gradient-capacity-transfer.md
   gradient-is-rank-3.md
   gradient-is-routing-plus-calibration.md
   gradient-orthogonal-to-undertrained-subspace.md
   grating-proposes-attention-executes.md
   holographic-capacity-hypothesis.md
   holographic-computer-synthesis.md
   holographic-distillation-concept.md
   holographic-distillation-works.md
   holographic-state-machine.md
   isa-decoder-qwen36-27b.md
   isa-framing-beats-lambda-framing.md
   kibc-32b-probe-validation.md
   kibc-temporal-not-parallel.md
   knowledge-neurons-are-hot.md
   lambda-operations-depth-map.md
   lambda-retrieval-is-scale-dependent.md
   lattice-is-relational-not-coordinate.md
   mirror-flip-barrier.md
   model-is-beamformer-over-token-cloud.md
   moire-rank-ceiling-limited.md
   montague-is-pre-transition.md
   mspace-not-wspace.md
   multicycle-dispatch-collapse.md
   multiplexing-breaks-holography.md
   multiplicative-and-loss.md
   multiplicative-modulation-explosion.md
   nan-death-loop-root-cause.md
   oracle-crystal-hurts.md
   origin-story-lambda-on-a-lark.md
   oscillation-means-zero.md
   output-beamformers-are-dynamic.md
   overlay-from-crystal-eigenvalues.md
   paradigm-shift-target.md
   parity-zone-cancellation.md
   phased-structural-discovery.md
   phi-compression-is-universal.md
   pretraining-is-beta-reduction.md
   programs-are-fixed-points-of-beta-reduction.md
   quantization-cliff-q3.md
   quantum-crystal-analogy.md
   qwen14b-ffn-three-functional-groups.md
   reader-llm-dual-plate.md
   relation-directions-crystallized.md
   retrieval-is-beta-apply.md
   rigid-vs-open-architecture.md
   rope-is-accidental-holographic-lens.md
   rotation-eigenplanes.md
   save-before-compare-pattern.md
   scale-trend-clean-family-series.md
   seed-crystal-nucleation.md
   semantic-horizon-12-tokens.md
   session-127-architecture-complete.md
   session-127-meta-analysis.md
   session-160-beta-reduction-training.md
   session-delta-replaces-kv-cache.md
   shadow-vs-crystal.md
   sigmoid-gate-saturation.md
   sign-topology-76-percent.md
   soft-mirror-etch.md
   softmax-routing-kills-gradient.md
   stride-attention-mask-from-collapse.md
   stride-overlap-registers.md
   stridestack-scales-by-adding-lenses.md
   superposition-bottleneck-insight.md
   td-flip-interval-gnorm.md
   td-flips-match-crystal.md
   ternary-flip-scale-mismatch.md
   ternary-mirror-stack.md
   ternary-routing-is-eigenvector-sign.md
   three-clusters-kibcm.md
   three-voter-anti-oscillation.md
   trace-loss-validated.md
   tracer-works-different-programs.md
   training-arc-thesis.md
   tst-holographic-connection.md
   two-crystals-hard-and-soft.md
   two-level-program-architecture.md
   unified-plate-architecture.md
   universal-axis-is-input-property.md
   universal-retrieval-lattice.md
   v10-vsm-s5-activation.md
   v12-10k-filesystem-forming.md
   v12-run3-nan-collapse.md
   v14-eval-baseline-step500.md
   v14-extraction-complete.md
   v14-td-sisyphus-bug.md
   vocabulary-paradox.md
   vsm-self-bootstraps.md
   vsm-variety-gap.md
   weight-signs-are-random-across-matrices.md
   zeros-are-backbone-not-emergent.md
   zeros-are-denoising.md
   zeros-only-beats-zeros-plus-flips.md
   zone-voted-ffn-extraction.md
  michael
   lambda-controls.md
   lambda-is-all-you-need.md
   llm-isa.md
  state.md
 models
  distilled-compiler
 notebooks
  README.md
 outputs
  attention_spiral
   aggregate_spiral.png
   centroid_evolution.png
   distance_curves.png
   expansion_ratios.png
   heads_code.png
   heads_dialogue.png
   heads_expository.png
   heads_lambda.png
   heads_long_narrative.png
   heads_math.png
   heads_narrative.png
   heatmap_code.png
   heatmap_dialogue.png
   heatmap_expository.png
   heatmap_lambda.png
   heatmap_long_narrative.png
   heatmap_math.png
   heatmap_narrative.png
   helix3d_aggregate_at118.png
   helix3d_aggregate_bestfit.png
   helix3d_code_at118.png
   helix3d_code_bestfit.png
   helix3d_dialogue_at118.png
   helix3d_dialogue_bestfit.png
   helix3d_expository_at118.png
   helix3d_expository_bestfit.png
   helix3d_lambda_at118.png
   helix3d_lambda_bestfit.png
   helix3d_long_narrative_at118.png
   helix3d_long_narrative_bestfit.png
   helix3d_math_at118.png
   helix3d_math_bestfit.png
   helix3d_narrative_at118.png
   helix3d_narrative_bestfit.png
   helix_search_code.png
   helix_search_dialogue.png
   helix_search_expository.png
   helix_search_lambda.png
   helix_search_long_narrative.png
   helix_search_math.png
   helix_search_narrative.png
   periodicity_code.png
   periodicity_dialogue.png
   periodicity_expository.png
   periodicity_lambda.png
   periodicity_long_narrative.png
   periodicity_math.png
   periodicity_narrative.png
   polar_code.png
   polar_dialogue.png
   polar_expository.png
   polar_lambda.png
   polar_long_narrative.png
   polar_math.png
   polar_narrative.png
   revolution_expansion_at118.png
   revolution_expansion_bestfit.png
   spiral_3d_params.json
   spiral_params.json
  crystal_gemstone.html
  crystal_hierarchy
   crystal_hierarchy_4d.html
  rope_energy
   centroid_shift.png
   energy_heatmap_code.png
   energy_heatmap_dialogue.png
   energy_heatmap_expository.png
   energy_heatmap_lambda.png
   energy_heatmap_long_narrative.png
   energy_heatmap_math.png
   energy_heatmap_narrative.png
   expansion_summary.png
   head_freqmap_code.png
   head_freqmap_dialogue.png
   head_freqmap_expository.png
   head_freqmap_lambda.png
   head_freqmap_long_narrative.png
   head_freqmap_math.png
   head_freqmap_narrative.png
   predicted_vs_observed.png
   rope_energy_params.json
   transition_analysis.png
  rope_spiral
   aggregate_dual.png
   dual_helix_code.png
   dual_helix_dialogue.png
   dual_helix_expository.png
   dual_helix_lambda.png
   dual_helix_long_narrative.png
   dual_helix_math.png
   dual_helix_narrative.png
   gap_analysis.png
   spectral_code.png
   spectral_dialogue.png
   spectral_expository.png
   spectral_lambda.png
   spectral_long_narrative.png
   spectral_math.png
   spectral_narrative.png
   unwound_ribbon.png
 probes
  README.md
  __init__.py
  __pycache__
  binding.json
  classify.json
  compile-gradient.json
  decompile.json
  exemplar-sweep.json
  extract.json
  fact_recall.json
  fact_recall_extended.json
  gate-ablation-base.json
  gate-ablation.json
  lambda_kernel_probes.py
  summarize.json
  translate.json
  v0-behavioral.json
 proofs
  01_sign_topology.py
  02_universal_profile.py
  03_universal_modes.py
  README.md
 pyproject.toml
 results
  README.md
  U_residual_constraint.log
  ab-test
   comparison.json
  abl-ablation-empty-20260417-001620
   meta.json
   results.jsonl
  abl-ablation-engage-line-20260417-002515
   meta.json
   results.jsonl
  abl-ablation-example-20260417-001633
   meta.json
   results.jsonl
  abl-ablation-fol-20260417-001646
   meta.json
   results.jsonl
  abl-ablation-formal-semantics-20260417-001659
   meta.json
   results.jsonl
  abl-ablation-lambda-calculus-20260417-001717
   meta.json
   results.jsonl
  abl-ablation-lambda-symbol-20260417-001736
   meta.json
   results.jsonl
  abl-ablation-lambda-word-20260417-001754
   meta.json
   results.jsonl
  abl-ablation-montague-20260417-001814
   meta.json
   results.jsonl
  abl-ablation-output-lambda-only-20260417-002528
   meta.json
   results.jsonl
  abl-ablation-output-only-20260417-001833
   meta.json
   results.jsonl
  abl-ablation-preamble-bridge-20260417-002450
   meta.json
   results.jsonl
  abl-ablation-preamble-full-20260417-002437
   meta.json
   results.jsonl
  abl-ablation-preamble-only-20260417-002503
   meta.json
   results.jsonl
  abl-ablation-role-compiler-20260417-001852
   meta.json
   results.jsonl
  abl-ablation-role-lambda-compiler-20260417-001912
   meta.json
   results.jsonl
  abl-ablation-role-plus-terse-20260417-001931
   meta.json
   results.jsonl
  abl-ablation-symbols-cluster-20260417-001944
   meta.json
   results.jsonl
  abl-ablation-symbols-line-20260417-002551
   meta.json
   results.jsonl
  abl-ablation-tensor-line-20260417-002539
   meta.json
   results.jsonl
  abl-ablation-translate-formal-20260417-001957
   meta.json
   results.jsonl
  abl-ablation-translate-lambda-20260417-002009
   meta.json
   results.jsonl
  abl-compile-20260417-002022
   meta.json
   results.jsonl
  abl-null-20260417-002035
   meta.json
   results.jsonl
  activation_zero_mask.log
  adjunction-rank-null
   Qwen_Qwen3-32B.json
   Qwen_Qwen3-8B.json
   Qwen_Qwen3-8B.smoke.json
   run.log
   run32b.log
   smoke.log
  algebraic-compose
   results.json
  angle-spectrum
   results.json
  attention-execution-trace
   summary.json
  attention-sparsity
   run.log
   summary.json
  attention-typed-binding
   Qwen_Qwen3-8B.json
   run-8b.log
  attention_execution_trace.log
  backbone-threshold
   backbone_analysis.json
   results.json
   run.log
  basin-analysis
   step_014000.json
   step_016000.json
   v2_step_016000.json
  basin-qkv
   analysis.json
  basin-v2-d512
   training-run1.log
  basin-v3-d512
   training-run1.log
  basin-whitened
   analysis.json
  basin_qkv_run.log
  basin_whitened_run.log
  beam-hologram-analysis
   results.json
  beam-trace
   beam_trace_results.json
   beam_trace_summary.json
  behavior-basins
   behavior_last_layer_scores.json
   behavior_metadata.json
   behavior_word_layer_scores.json
  behavior-depth
   invariance_metadata.json
   invariance_scores.json
  behavioral-crystal
   mistral-7b.json
   mistral-7b.log
   pythia-2.8b.json
   pythia-2.8b.log
   qwen3-14b.json
   qwen3-14b.log
   qwen3-32b.json
  behavioral-crystal-v2
   mistral-7b.json
   mistral-7b.log
   pythia-2.8b.json
   pythia-2.8b.log
   qwen3-14b.json
   qwen3-14b.log
   qwen3-32b.json
   qwen3-32b.log
  beta-expansion
   Qwen_Qwen3-8B.json
   run.log
  beta-reduction-probe
   beta_reduction_results.json
   binding_layer_profiles.png
   depth_vs_layer.png
   pipeline_comparison.png
   substitution_profiles.png
  binding
   attention_entropy.npz
   binding_ablation_results.json
   binding_analysis_v2_v3.json
   binding_hybrid_results.json
   binding_results.json
   binding_shape.log
   binding_shape_results.json
   vsm_probe_step_001000_v3.2.json
   vsm_probe_step_001000_v4.1.json
   vsm_probe_step_001000_v4.json
   vsm_probe_step_002000_v3.2.json
   vsm_probe_step_002000_v4.1.json
   vsm_probe_step_002000_v4.json
   vsm_probe_step_003000_v3.2.json
   vsm_probe_step_003000_v4.1.json
   vsm_probe_step_003000_v4.json
   vsm_probe_step_004000_v3.2.json
   vsm_probe_step_004000_v4.1.json
   vsm_probe_step_004000_v4.json
   vsm_probe_step_005000_v3.2.json
   vsm_probe_step_005000_v4.1.json
   vsm_probe_step_005000_v4.json
   vsm_probe_step_006000_v3.2.json
   vsm_probe_step_006000_v4.1.json
   vsm_probe_step_006000_v4.json
   vsm_probe_step_007000_v3.2.json
   vsm_probe_step_007000_v4.1.json
   vsm_probe_step_007000_v4.json
   vsm_probe_step_008000_v3.2.json
   vsm_probe_step_008000_v4.1.json
   vsm_probe_step_008000_v4.json
   vsm_probe_step_009000_v3.2.json
   vsm_probe_step_009000_v4.1.json
   vsm_probe_step_009000_v4.json
   vsm_probe_step_010000.json
   vsm_probe_step_010000_v2.json
   vsm_probe_step_010000_v3.2.json
   vsm_probe_step_010000_v3.json
   vsm_probe_step_010000_v4.1.json
   vsm_probe_step_010000_v4.json
   vsm_probe_step_011000_v4.1.json
   vsm_probe_step_011000_v4.json
   vsm_probe_step_012000_v4.1.json
   vsm_probe_step_012000_v4.json
   vsm_probe_step_013000_v4.1.json
   vsm_probe_step_013000_v4.json
   vsm_probe_step_014000_v4.1.json
   vsm_probe_step_014000_v4.json
   vsm_probe_step_015000_v4.1.json
   vsm_probe_step_015000_v4.json
   vsm_probe_step_016000_v4.1.json
   vsm_probe_step_016000_v4.json
  binding-distance-distribution
   distance_histogram_L30.json
   summary.json
  binding-graph-trace
   run.log
   summary.json
  binding-prep-lowrank
   Qwen_Qwen3-8B.json
   run.log
  binding-schedule-null
   Qwen_Qwen3-8B.json
   run.log
  binding-schedule-semantic
   Qwen_Qwen3-8B.json
   run.log
  binding-structure
   binding_analysis.json
  binding_distance_distribution.log
  bos-probe
   bos-residuals.npz
   head-analysis.json
   head-projections.npz
   head-weights.npz
   linear-probe.json
   pca-analysis.json
   probe-manifest.json
   summary.json
  bos-probe-v2
   bos-residuals.npz
   contrast-analysis.json
   head-q-redux.json
   probe-manifest.json
   summary.json
  bridge-verification
   Qwen_Qwen3-0.6B_results.json
   Qwen_Qwen3-14B_results.json
   Qwen_Qwen3-8B_results.json
   crystal_depth_scan_14b.log
   run-14b.log
  c-rotation-probe
   results.json
  categorical-geometry-qwen3-32b
   adjunction_cross_zone.png
   coherence_convergence.png
   curry_howard_accuracy.png
   hyperbolic_norm_depth.png
   summary.json
  circuit-discovery-20260416-202415.log
  cluster-probe
   clusters_layer0.json
   clusters_layer28.json
   clusters_layer63.json
   layer_curve.png
   layer_scores.json
   metadata.json
   similarity_layer0.png
   similarity_layer28.png
   similarity_layer63.png
   umap_layer0_groups.png
   umap_layer0_hdbscan.png
   umap_layer28_groups.png
   umap_layer28_hdbscan.png
   umap_layer63_groups.png
   umap_layer63_hdbscan.png
  combinator-addressing
   Qwen_Qwen3-0.6B
  combinator-map-consensus
   consensus.json
   scale.json
  combinator-probe
   combinator_probe_results.json
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-extended
   extended_heatmaps.png
   extended_layer_profiles.png
   extended_probe_results.json
   full_correlation.png
  combinator-probe-mistral_7b_v0.3
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-olmo_2_1124_13b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-pythia
   combinator_probe_results.json
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles_montague_overlay.png
   pythia_vs_32b_distribution.png
   selectivity_heatmaps.png
  combinator-probe-pythia_160m_deduped
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-qwen3_0.6b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-qwen3_14b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-qwen3_32b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-relationship-map
   EleutherAI_pythia-2.8b-deduped.json
   EleutherAI_pythia-2.8b-deduped.npz
   EleutherAI_pythia-410m.json
   EleutherAI_pythia-410m.npz
   HuggingFaceTB_SmolLM3-3B.json
   HuggingFaceTB_SmolLM3-3B.npz
   Qwen_Qwen3-0.6B.json
   Qwen_Qwen3-0.6B.npz
   Qwen_Qwen3-14B.json
   Qwen_Qwen3-14B.npz
   Qwen_Qwen3-32B.json
   Qwen_Qwen3-32B.npz
   Qwen_Qwen3-4B.json
   Qwen_Qwen3-4B.npz
   Qwen_Qwen3-8B.json
   Qwen_Qwen3-8B.npz
   allenai_OLMo-2-1124-13B.json
   allenai_OLMo-2-1124-13B.npz
   mistralai_Mistral-7B-v0.3.json
   mistralai_Mistral-7B-v0.3.npz
  combinator_ffn_index_run.log
  combined-compression
   Qwen_Qwen3-8B.json
   run-conservative.log
   run-sweetspot.log
   run.log
  compile-gradient
   correlations.json
   qwen_compression.json
   qwen_scores.json
   qwen_scores_gateless.json
   qwen_scores_graded.json
   qwen_tasks.json
   vsm_probe_step_000500_v6_mlx.json
   vsm_probe_step_001000.json
   vsm_probe_step_001000_v3.2.json
   vsm_probe_step_001000_v4.1.json
   vsm_probe_step_001000_v4.json
   vsm_probe_step_001000_v5.json
   vsm_probe_step_001000_v6_mlx.json
   vsm_probe_step_001500_v6_mlx.json
   vsm_probe_step_002000.json
   vsm_probe_step_002000_v3.2.json
   vsm_probe_step_002000_v4.1.json
   vsm_probe_step_002000_v4.json
   vsm_probe_step_002000_v6_mlx.json
   vsm_probe_step_002500_v6_mlx.json
   vsm_probe_step_003000.json
   vsm_probe_step_003000_v3.2.json
   vsm_probe_step_003000_v4.1.json
   vsm_probe_step_003000_v4.json
   vsm_probe_step_003000_v6_mlx.json
   vsm_probe_step_003500_v6_mlx.json
   vsm_probe_step_004000.json
   vsm_probe_step_004000_v3.2.json
   vsm_probe_step_004000_v4.1.json
   vsm_probe_step_004000_v4.json
   vsm_probe_step_004000_v6_mlx.json
   vsm_probe_step_004500_v6_mlx.json
   vsm_probe_step_005000.json
   vsm_probe_step_005000_v3.2.json
   vsm_probe_step_005000_v4.1.json
   vsm_probe_step_005000_v4.json
   vsm_probe_step_005000_v6_mlx.json
   vsm_probe_step_005500_v6_mlx.json
   vsm_probe_step_006000.json
   vsm_probe_step_006000_v3.2.json
   vsm_probe_step_006000_v4.1.json
   vsm_probe_step_006000_v4.json
   vsm_probe_step_006000_v6_mlx.json
   vsm_probe_step_006500_v6_mlx.json
   vsm_probe_step_007000.json
   vsm_probe_step_007000_v3.2.json
   vsm_probe_step_007000_v4.1.json
   vsm_probe_step_007000_v4.json
   vsm_probe_step_007000_v6_mlx.json
   vsm_probe_step_007500_v6_mlx.json
   vsm_probe_step_008000.json
   vsm_probe_step_008000_v3.2.json
   vsm_probe_step_008000_v4.1.json
   vsm_probe_step_008000_v4.json
   vsm_probe_step_008000_v6_mlx.json
   vsm_probe_step_008500_v6_mlx.json
   vsm_probe_step_009000.json
   vsm_probe_step_009000_v3.2.json
   vsm_probe_step_009000_v4.1.json
   vsm_probe_step_009000_v4.json
   vsm_probe_step_009000_v6_mlx.json
   vsm_probe_step_009500_v6_mlx.json
   vsm_probe_step_010000.json
   vsm_probe_step_010000_v3.2.json
   vsm_probe_step_010000_v4.1.json
   vsm_probe_step_010000_v4.json
   vsm_probe_step_010000_v6_mlx.json
   vsm_probe_step_010500_v6_mlx.json
   vsm_probe_step_011000_v4.1.json
   vsm_probe_step_011000_v4.json
   vsm_probe_step_011000_v6_mlx.json
   vsm_probe_step_011500_v6_mlx.json
   vsm_probe_step_012000_v4.1.json
   vsm_probe_step_012000_v4.json
   vsm_probe_step_012000_v6_mlx.json
   vsm_probe_step_012500_v6_mlx.json
   vsm_probe_step_013000_v4.1.json
   vsm_probe_step_013000_v4.json
   vsm_probe_step_013000_v6_mlx.json
   vsm_probe_step_013500_v6_mlx.json
   vsm_probe_step_014000_v4.1.json
   vsm_probe_step_014000_v4.json
   vsm_probe_step_014000_v6_mlx.json
   vsm_probe_step_014500_v6_mlx.json
   vsm_probe_step_015000_v4.1.json
   vsm_probe_step_015000_v4.json
   vsm_probe_step_015000_v6_mlx.json
   vsm_probe_step_015500_v6_mlx.json
   vsm_probe_step_016000_v4.1.json
   vsm_probe_step_016000_v4.json
   vsm_probe_step_016000_v6_mlx.json
   vsm_probe_step_016500_v6_mlx.json
   vsm_probe_step_017000_v6_mlx.json
   vsm_probe_step_017500_v6_mlx.json
   vsm_probe_step_018000_v6_mlx.json
   vsm_probe_step_018500_v6_mlx.json
   vsm_probe_step_019000_v6_mlx.json
   vsm_probe_step_019500_v6_mlx.json
   vsm_probe_step_020000_v6_mlx.json
   vsm_probe_step_020500_v6_mlx.json
   vsm_probe_step_021000_v6_mlx.json
   vsm_probe_step_021500_v6_mlx.json
   vsm_probe_step_022000_v6_mlx.json
   vsm_probe_step_022500_v6_mlx.json
   vsm_probe_step_023000_v6_mlx.json
   vsm_probe_step_023500_v6_mlx.json
   vsm_probe_step_024000_v6_mlx.json
   vsm_probe_step_024500_v6_mlx.json
   vsm_probe_step_025000_v6_mlx.json
   vsm_probe_step_025500_v6_mlx.json
   vsm_probe_step_026000_v6_mlx.json
   vsm_probe_step_026500_v6_mlx.json
   vsm_probe_step_027000_v6_mlx.json
   vsm_probe_step_027500_v6_mlx.json
   vsm_probe_step_028000_v6_mlx.json
   vsm_probe_step_028500_v6_mlx.json
   vsm_probe_step_029000_v6_mlx.json
   vsm_probe_step_029500_v6_mlx.json
   vsm_probe_step_030000_v6_mlx.json
   vsm_probe_step_030500_v6_mlx.json
   vsm_probe_step_031000_v6_mlx.json
   vsm_probe_step_031500_v6_mlx.json
   vsm_probe_step_032000_v6_mlx.json
  composed-direction
   summary.json
  composed-transform-probe
   results.json
  compression-map
   qwen3_4b_map.json
  compression-shape
   EleutherAI_pythia_160m_deduped.json
   Qwen_Qwen3_4B.json
  compressor-binding
   compressor_binding_analysis.json
  compressor-lm
  compressor-lm-iterative
   training-summary.json
  computed-beam
   results.json
  confidence-gate
   Qwen_Qwen3-8B.json
   run.log
  continuation-placement
   Qwen_Qwen3-8B.json
  conversion-test
   convert_pythia-2.8b_svd_k512.json
   convert_pythia-2.8b_svd_k64.json
  convert_pythia_svd512_run.log
  convert_pythia_svd64_run.log
  copy_program.log
  cross-task-20260416-204948.log
  cross-task-20260416-205416.log
  crystal-circuit-types
   summary.json
  crystal-combined
   results.json
  crystal-combined-run.log
  crystal-comparison
   crystal_comparison_results.json
   crystal_depth_profiles.png
   crystal_metrics_comparison.png
   crystal_quality_scores.png
   run.log
  crystal-completeness
   results.json
  crystal-completeness-run.log
  crystal-compression-analysis
   results.json
  crystal-distill
   run.log
  crystal-ecc-sign-correction
   Qwen_Qwen3-8B.json
  crystal-error-correction
   Qwen_Qwen3-0.6B
   Qwen_Qwen3.6-27B
  crystal-etch-attention
   pretrained_spectrum.json
   results.json
   run.log
  crystal-fourier
   results.json
   spectral.json
  crystal-fourier-run.log
  crystal-latch
   results.json
  crystal-latch-run.log
  crystal-latch-v2
   results.json
  crystal-latch-v2-run.log
  crystal-lens
   results.json
  crystal-phi-permnull
   EleutherAI_pythia-410m-deduped.json
   Qwen_Qwen3-0.6B.json
   Qwen_Qwen3-14B.json
   Qwen_Qwen3-8B.json
   run.log
   run14b.log
  crystal-phi-verify
   EleutherAI_pythia-160m-deduped.json
   EleutherAI_pythia-2.8b-deduped.json
   EleutherAI_pythia-410m-deduped.json
   HuggingFaceTB_SmolLM3-3B.json
   Qwen_Qwen2.5-0.5B.json
   Qwen_Qwen3-0.6B.json
   Qwen_Qwen3-0.6B_depth_scan.json
   Qwen_Qwen3-14B.json
   Qwen_Qwen3-14B_depth_scan.json
   Qwen_Qwen3-32B.json
   Qwen_Qwen3-8B.json
   Qwen_Qwen3-8B_depth_scan.json
   Qwen_Qwen3-8B_gamma_equation.json
   Qwen_Qwen3-8B_gradient_crystal.json
   Qwen_Qwen3-8B_hybrid_final.json
   Qwen_Qwen3-8B_hybrid_ternarize.json
   Qwen_Qwen3-8B_magnitude_crystal.json
   Qwen_Qwen3-8B_ternarize.json
   Qwen_Qwen3-8B_zero_prediction.json
   Qwen_Qwen3-8B_zero_v2.json
   Qwen_Qwen3.6-27B.json
   mistralai_Mistral-7B-v0.3.json
   pythia-2.8b.log
   qwen3-0.6b.log
   qwen3-0.6b_depth_scan.log
   qwen3-14b-fresh.log
   qwen3-14b_depth_scan.log
   qwen3-32b-fresh.log
   qwen3-8b_depth_scan.log
   qwen3-8b_gamma_eq.log
   qwen3-8b_gradient.log
   qwen3-8b_hybrid.log
   qwen3-8b_hybrid_final.log
   qwen3-8b_magnitude.log
   qwen3-8b_ternarize.log
   qwen3-8b_zero_prediction.log
   qwen3-8b_zero_v2.log
   qwen36-27b-fresh.log
  crystal-reconstruct
   results.json
  crystal-reconstruct-run.log
  crystal-selfsim
   results.json
  crystal-selfsim-teacher
   unit_cells.npz
  crystal-selfsim-v12
   results.json
  crystal-sieve-pipeline
   Qwen_Qwen3-8B.json
   Qwen_Qwen3-8B_v2.json
   run.log
   run_v2.log
   run_v3.log
  crystal-sieve-repro
   Qwen_Qwen3-8B.contaminated-only.json
   Qwen_Qwen3-8B.json
   run.log
   run_heldout.log
  crystal-tree
   results.json
  crystal-validity
   cross_model.json
   pythia-160m.json
   pythia-410m.json
   qwen3-0.6b.json
   qwen3-4b.json
   run.log
  crystal-visualization
   crystal_2d_overview.png
   crystal_3d_angles.png
   crystal_3d_pc012.png
   crystal_3d_pc013.png
   crystal_3d_pc014.png
   crystal_3d_pc023.png
   crystal_3d_pc123.png
   crystal_3d_pc234.png
   crystal_zones_3d.png
   eigenvalue_spectrum.png
   gemstone_beams.png
   gemstone_breathing.png
   gemstone_facets.png
   gemstone_main.png
  crystal-zeros
   summary.json
  crystal-zeros-train
   run.log
   summary.json
  crystal_scanner_run.log
  crystal_sieve_crystal.log
  crystal_sieve_random.log
  crystal_space_zeros.log
  cut-then-fill
   summary.json
  cut-then-fill-scratch
   run.log
   summary.json
  datafitted-dimension-sweep
   meta.json
   results.json
  date-attention
   results.json
   run.log
  date-fourier
   results.json
   run.log
  diagnose_ternary.log
  dimensional-analysis
   Qwen_Qwen3-0.6B
   Qwen_Qwen3-14B
   Qwen_Qwen3.6-27B
  direct-delta-correction
   Qwen_Qwen3-8B_cal-aware.json
   run.log
  distillation
   summary.json
  dvd-group-scale
   compounding.json
   results.json
   run.log
  dvd-index-test
   results.json
   run.log
  dvd-stamp-test
   compounding.json
   results.json
   run.log
  early_layer_analysis.log
  eigenvector_selfsimilarity.log
  essential-heads-20260416-195543.log
  essential-heads-attention.npz
  essential-heads-tokens.json
  etch-strategy-probe
   core.json
  etcher-vsm
   proto_d0.226.json
  evo-descent
   results.json
  evo-descent-v2
   results.json
   run.log
  evo-descent-v3
   results.json
  ex-exemplar-arrow-only-20260417-004626
   meta.json
   results.jsonl
  ex-exemplar-both-20260417-004503
   meta.json
   results.jsonl
  ex-exemplar-complex-montague-20260417-004606
   meta.json
   results.jsonl
  ex-exemplar-montague-20260417-004422
   meta.json
   results.jsonl
  ex-exemplar-montague-rich-20260417-004523
   meta.json
   results.jsonl
  ex-exemplar-nucleus-20260417-004442
   meta.json
   results.jsonl
  ex-exemplar-nucleus-rich-20260417-004545
   meta.json
   results.jsonl
  exp-b-self-verifying
   result.json
  experiments
   circuit-discovery-summary.json
   failure-mode-analysis.json
   head-ablation-summary.json
   sha256:0003bbe64425cdf34f716130a1d4413e49519e42568ea3b0cee11066d2e9ce1b
   sha256:005ae13155bcb6890dda612ff1cd9c29745710334b0725c402c30de27318e50c
   sha256:0088c95fe29d84064fff9ad630f9f42cd6c2e188ab9ab5e4ba027abf4a2fd729
   sha256:0099889d05b37f6323b8f7a8cfb805e594a06a049523fba590cac55a63f5a934
   sha256:011adac4f422d0fb190d30533feb17a6e19eed5e88366f93752489a15ef47deb
   sha256:021fe3f535afe47e739b997358444bffdb67b5ed848e8074cd1f4d87d9178060
   sha256:022b86c91dffc3d6555f9a8ab4810ba8b0ae75c9deda1d43fb757aa4918213a0
   sha256:024e0b957a5e949fe09d2d7f2b3337fea12a5d3bf53fb9737afd84a38d25de29
   sha256:026a2a416896e13eff8812a56c35ffe0caaafcdc7187462f89a624d6a7800c5b
   sha256:02a1ab609a6949b2344ef1d69992a8ecb470cddfade8e64850ce8b68de9f1409
   sha256:02ef2c3c1c0a218cbc2309cab2feb5266c2da0e3d188f52e5676adae97e53f99
   sha256:038184ceb75b0afa3899b83003279dd741cf3215ed945b6c713be6bfc72eb9fb
   sha256:03edb7972d27737931a8c53a9a4ac4fb05eaa71d7301d6e156edfb95aab83af4
   sha256:0470039afd9765edda1ee17f7296cfb2517ebcf05369f1ee8d1e5448c29da533
   sha256:04752412b11b675999a00ed8fdcadca82fe2e490226ea81ca41d725a929235e4
   sha256:04c1ce8fca88bf0a8af3804141b77a754d9850c747abbbce29a1efa946d04889
   sha256:04c808ad63b4e5a0df306f7f0975d02bd0c5fa7a84f462d9a11a73f7b89bd70a
   sha256:052bb29f0d2e335f8f95ade8634b336d91b984475a7501faf64d1061a7047f29
   sha256:056f5e8d8a8ab30f38177e5b854745a2b6730bb5e42879eb29cf1d48a3ea67e2
   sha256:05800525af8e37fd9d3022b4fbf69e899cc1d97ad68ff31c6f6acccba5b52c00
   sha256:05ca0d5b1362596a741bb66aa32482c87c2b8d32ecfbe5dfe2ed4f40ad7b161d
   sha256:05e4e502f5c88530e0a1eadc46a1c36023f676970e95cbdc57a33f4506e9e8c7
   sha256:05faf9e5bee0b0caaf8c5e88a1788158c512a15ac2fffc4bdd8b9823544f1394
   sha256:06932b6a1aebf53185eb323fd40fa8a057d0473846d8462d5b1072babc5933c8
   sha256:0721febe0ef991074e8dc752893945b3bb94f99101454f5c7ea01e86edd93b34
   sha256:075c0129f9ec6220a7400f6d36de42dbbe971ec5414cf1bb75dce2c8a00c3f73
   sha256:077213a86b16514eddeadb5d8594c4c2b1c5708c2292b5b5e1f0c58799f39aeb
   sha256:080d7995f5122d918d5737b55127eac43b1dd433b4664c2456b945a4aa3cf079
   sha256:08735320daff1d898414289c3e31400d0944f156d5d623b05bbb25fdee7cb685
   sha256:09381d6a3309c9832ca1c498d70862e3d6dfa55a1d3250e6495d0f8a2eb187ae
   sha256:095b969f25a992651fbc9d518fe54e13bdc7530801785a0d76d07ecb70a57af7
   sha256:099b275e6c884697f3191176e5f56ce3eca34d0d59bc61b0ebbcbb61d26b3f47
   sha256:09b77a88452c92df2d16f645b47242c0badeb41d5f3aa78931b37c7964630e43
   sha256:09ca1af1cac80cc41dc86e21157d716707e4913b34538d02a154aa426fa99cb0
   sha256:0a41c7295548c32fc7713d4c2f65cf806f2742766a22fc03e1b982b1b7c5cc59
   sha256:0a8d99f19ad55368eb5619a6a24a11752e76f4255d28916238009d371c156a17
   sha256:0c98c59f051858c1b7f1773a0c98370000f39d2274f0261a7dd025a8a75c424a
   sha256:0d66dc8ff837c3a929a269c95c30e2ca7ee7b6b36775dc337ca0160eb9d13960
   sha256:0e197d20d626d734418e7e5c28f8627686fc73cc37365dea10b22f5cdfea7f38
   sha256:0e46704253edf134951e18ebbb8d48d784061662f1aa6b6d20c2dd38ec056905
   sha256:0e5603a5dd6ccda328d4f919417280aeae5f542d1c114ceb6bc1c0ab5a5c5b99
   sha256:0f792bfc9719dbb79bf432a245cbc59d641f069e969af234d8eba1e902ae1f2f
   sha256:0faf950fe96878740d4e418d7eefa8063dfa90f1bffd8e30284fb5971e798a31
   sha256:0fb46f927520ae5a30a5d6a4a0a57317d22e2f27028eefd038faed47c8c24978
   sha256:10019bcabeed9aec1cb8f39d3ae8041e940a38d179a4f0797524240cb7b9d0f9
   sha256:10b6dcce9c9a6347bd07b7463ca76d31ec957bb485684a06b4097ee7bd2db284
   sha256:121e97336ba41880d77cbf201caa8f40029565fcb41ab1306eeab790b40a9478
   sha256:127642ee5f21ebd88aab1e74a822e82f67bb9a51dbe294617ab29d50f48dca5b
   sha256:12908328c6f8663458fb5b25c1ff8c04745607841292892d94c6528a901263a6
   sha256:12df87ae8435021f90287012a4daba264b7b725d91a4457223f0018ed4ae92b6
   sha256:13247e769c473a187386ae176d8155cc34ca6bc7fa8cd5983e17d83049d1cb38
   sha256:13c7daa552019f1f12d0ca9c2625250599d9941cfedbd5d3412f0e9a06232e0e
   sha256:1404b53e3fba3560d36f865fcc103917b50c3515ace37bae5738c37d2ac3e438
   sha256:1485cc0e7a8ebd94237eda33e3a97c22e47b4eda3f32e510b01c7292310fc5f7
   sha256:154f8324da243f597b9287d378e0f5f73963e38648c5fa8283dfc6f70512a638
   sha256:15fb6f1b818675e04b8e3ab79ef4276ab288fb5f18c05eb3edb82528f0aba9aa
   sha256:17263525a6d79212ccd3e3ec7a27a5557b424a8ff9fbbf42166e16911dd9ebfa
   sha256:180a81b247eaba7c4117047cd1ccaaa520f9e24a77a509ac669f6ef381bac3d2
   sha256:182b812e3727c3c4a55e33ef0488f1cc4f68579fbc4fbbc4fe97df47783fdc2f
   sha256:18a3f225b259810ed5a3c8a933592ab8810f0fa7494cd1c00d38fddfd8c4f3dc
   sha256:18e4045d040d28c12d5fb638ffdf77df4ece093c2d227024999eecaf51da3ed4
   sha256:1931f24e6c0e021727dc2175d324bf7e792b61d02acb3740301b078c5578953d
   sha256:196448f47466f368095648335eb8ead037f22a4ece735ee5ad9efbc3f3820abf
   sha256:196fd5864248831ad1c684e481d8ad9cda5a640052e293e568bf3abb15fff77c
   sha256:19c58d55c5e2144a8ab0c925f592a770d5fb1223637af822c01a204c0c035591
   sha256:19d2310a76a8d711c5884a4d00d59fd95a35aeab82434404c970056880ae1a1c
   sha256:19e7bc525a19d47647f2c312bef3763e3365a3a7cacc07f03a88a76273a6a00c
   sha256:1a22a5ea65c42a0f4c5cdac11deba4e7800c8d10e5352eb88a70b08ea9edde79
   sha256:1ae0ff9dbb46ba2bdc3f1ce88481f49bbda1e7271214bb4d75bbe695c00b7d2b
   sha256:1b6a74be5b5a05a707baee87341bc5cc405dff61086ceb4b75dcca5a6a2d56bb
   sha256:1bf16d4dc0ec6c1432154206955e4b093e85c9302ef0b8637ea2f860ff12e306
   sha256:1bf4a91e3ecaed6254dcdfcee73689746d2b217e79a89e1bd98df280ff5fc7f5
   sha256:1ca036ecf00b4ee3a01df91196301d7e8ed85d164103896c166a4758fa0eb806
   sha256:1cef7e7fbb389dd8d2a7c577c9b5d697893c3b754a7e140e9ca6f7c0c56c3ec7
   sha256:1d329b21c68063df0ac16078329f6e7dafa9dba2d6b3dc09512bad318329bb75
   sha256:1d6800128127f86307ece8cde833784e0b16bbc94a387922075b52980721da40
   sha256:1dac1df75d39345734c4f958c44171ea3798e87c008b92f27946a379953db126
   sha256:1f648490125bffb3ca50ed1e37d95662d34e392e11afe5a6be73d300d351634b
   sha256:1f9b705cbc5922253cd9794a457b72c569b8bde068b069ae321a5c50285bc671
   sha256:1fc25b03fc33dceb384767feedddaac1b8b8e25d5bb8fcb123987fc3607a1654
   sha256:1fe8cbfcf127e28635395aa08e3310804082394af1672c8e0cfaa3ac7e139ec7
   sha256:2060be0c4586fcbc8a6682d794b865f4b40281737fb6d172bb4719770903b84c
   sha256:20c2142edd0b5e846bf188ebbe3046b5a173dd9d11c9758549bffad3a910dc60
   sha256:2180ccb5ec5b430f49f5477529ccde347c279d0d88c3fa60fa3b0652dd06ea18
   sha256:21d9955e4f241237a5997ebd54ba982cefde0dde5ba17231b6e4e5f0852c18d6
   sha256:21f4202d223652f01fc79bcc44d9b7f528c513049979a0e6dfc3438ae2b2759e
   sha256:2254e369c19bbe64735d7be013d1dc8a6e236be68c342dc991a6359bc0a57589
   sha256:225e51c5ff6dd890b42250461d459bad483530be536ba8abd81eeb88f6513041
   sha256:226197d290ed5aff204ced1b9131f114a1ed86c182c144ed2671e679cb1bebe7
   sha256:229942ba6639c9e00ba436bbd81d28b8899328cd0b1cf8994f641106098e0f43
   sha256:22ca752c5cef64bb0debd96471c35bf5ae64888115d3ad8a81c9bb83b0ff7491
   sha256:2397e909327a75e8cf4d6a282287630c2cabe723311fd8e4b236e30957aac974
   sha256:2422aef5e1e4b17da0648dbbe7bf81373c8ecb0ad547a259e558b26147dacd0b
   sha256:24ded772b9f162259fcc35cdf45802f0fba25661a9bf61af584c1930b7824e1c
   sha256:26937ec4a70bdb778e91ad1352979d24dee5d981f08fe9c691399e9529e861c2
   sha256:26978cd384ffe5e1c0178dfd94587c7fa38e7484cfdd2c9a556387fb6fff31bd
   sha256:26bbd2692ba576f24b299f40246c60561f1af10511241777110738c4ba2cbab6
   sha256:27d6c84eb834c01dcbb2cfd8385c19844ff570f3ee521b9167bb853e613e71fe
   sha256:2a355b6a44ab5756b4ca31b1899e06f7448eaa9c9c3463251ac691193a89b57b
   sha256:2a892f07deb2c8725162344eb70f3e50f094f1cd4ce66ebb2965daedfcda633e
   sha256:2ab5ce6e1589893d8fc4ef4a02ab04add978c362c08470b059604cfa8ac68987
   sha256:2b6a715fd208f83cbfab8947b99cd4b03cad2f6ea62b1b5c7c0b1bcf641ce08c
   sha256:2b8476ff1f3404e0650792dc170434652f864261c4920949990c0ee5126a680a
   sha256:2b8b40d8a76700bfa52bba0a8e7953a50fee2340f5ee0e72c82cf387ee23cd97
   sha256:2cde3fe24802f6fce5a6ec594c5b3b25a7dec6bf7994f4df2f4db0132bc55444
   sha256:2ded024109668f686eae9420a54c85bfa4840c5599430b44c5d2afa6da1cc663
   sha256:2e33e7f15e07d3e9a4db0aae78e365119fb6c10e97e99fdc665042bc55649bd9
   sha256:2e3ca75d7468f1847201e6b381d08e3ea828bc0c7b617238d9eb9251b92b525a
   sha256:2e89eab01fd5eb7456ab25b3412eda6ccf266bc4f51989de5c72b4d1aaa9b665
   sha256:2fa963eac1135fcfe638d7f62c33a23e0a485f889302042cf7af583b6cdee413
   sha256:2fd6931ebc31f90d3d42468213c04068f3ad8b8b4248f26c8d95b09668e66181
   sha256:306705b583402db522f910d76bd43e9b7a7c756aa35c9e092145879c19e3f6a9
   sha256:3093f976dc32747053249700ebd5a3bbf3d0b4e39fae1985492aef3c06cdac40
   sha256:319bb71eb5b0cf06fbac25c9d42c2165ce22327e88daf5e4f7d977d6d7dd3915
   sha256:31f6002d95f6397b819dbe2de7b83432951f31966ee0f3ef7c8ca17f78574807
   sha256:3224781303e57b12c3f97ff7a2abf4cc06ac0973513ce73a15640c462b9ecbd2
   sha256:32c1fe780b344a1ebe68c753869312bbcf990ec30462ff95904c1324031b2d71
   sha256:333229b80288e2cb9d9e099149628788ce2bc39ee0d9eb6eb72dce6f59e8798d
   sha256:33e08fe53f0a38ddfe99ca5cf3f64e87765cfd541e81056c14cab434ab030635
   sha256:343e13af2eedee56d30cdfabded14cc238bb04e834168a050cd7f926e094293c
   sha256:34453eeec1dc5e3367735dfbda6e750bf15f09ef05bd66dfaea9262905be12d0
   sha256:36db2baed277d8ad5c2877063e7508c19c9d5365c1a3b5f4b14795f982ad0e2a
   sha256:37671423ae3989e369fd3ed736c16c11394c991c60bc4fc111ef01e6da0f1cdb
   sha256:378836364e234ca02a2adabb9ae4953922b886ac7d250a7d615ad00f3f8043ee
   sha256:378884bf2481a3d97d95c61cd1a3975d9aefb3428ec670414080806d38763e84
   sha256:37f985b7c63127074ec7eb57561155d958338d97d5de94157a2e0d9dd1bfa985
   sha256:381a7a873cdf327cd01d5ba4716b5d9ba51c59005044e114d7341c244e3138b6
   sha256:38238aeb103863c028c72ca787f87f1d1affae422e7751b12ba7299d4893b8d3
   sha256:384f4e31ce64a2ec7189767bd957a9a99ba75244d133a10701461344e53b8771
   sha256:3863105524f71cf9342df191e3890beb492d2d9f26ee03f962db55cd1ff2a3a6
   sha256:38839b4495bf280b4525ebdffd9a9f6bbb6ec9de687b51c72997303c9e39c70c
   sha256:38b38082ea8658786137f7dc2524480ed15129b1a74856dc9c7e3152922a1f55
   sha256:3a2320a16c11ff417ffdf404b27f74b676d62acb042c262a7bacfbf4aae468f1
   sha256:3b7a2c4dbff7e309126a392b7e632c638c0d257b400fbc70c72bfd7885224c03
   sha256:3b7e103e6968aa7721cd0b203e3b799a034e24aa917d760e177431f824a8dc49
   sha256:3b8ec1a76831d3cca4a297b648ef429e109d14c2b1d1fe10ec02394150571044
   sha256:3b9a2a1ca32d21a5a9571dcc9c5124661ac4176b93e3cb149f6beb3f5c45ef64
   sha256:3bd1d4fb04091d7c2e4741b570f551771a4aa8c814b30e8175d9eae5b37c9adb
   sha256:3bd98a2d06678637e2a3cf1cea94a505f35e0452c07116f0d0e483439c59a448
   sha256:3c809d7b796441b4f94b1c393557bf1fe8d4ab27690b588290ce6d147bb10761
   sha256:3dd9273992ceec58cda3c30161f156e069bf980c9e3ebb35ad908c6310fba526
   sha256:3e5ec06424045ed500d5b1ca15adb1e5ba42c88242370d804ed8642ce56509d6
   sha256:3f089c45ea1648d732d9409392516ee0c6759a1d9ef095629128091181a0ef82
   sha256:3f0feff43c6b2dfdbde9b07cf0ef0f1df1a41e0e28157f28622abfb40d19737b
   sha256:4024b40a74f406f3982fcc145530c42336bdd715545d3c2a3

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01MMXkkaow5GtYE8zCgp3X91.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/combinator-map-consensus/ 2>/dev/null && echo \"---\" && ls /Users/mwhitford/src/verbum/results/combinator-relationship-map/ 2>/dev/null | head -30"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
consensus.json
scale.json
---
allenai_OLMo-2-1124-13B.json
allenai_OLMo-2-1124-13B.npz
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
Qwen_Qwen3-14B.json
Qwen_Qwen3-14B.npz
Qwen_Qwen3-32B.json
Qwen_Qwen3-32B.npz
Qwen_Qwen3-4B.json
Qwen_Qwen3-4B.npz
Qwen_Qwen3-8B.json
Qwen_Qwen3-8B.npz
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/ 2>/dev/null | head -40"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/chec...

**Output:**
```
Exit code: 0
Stdout:
flip_map_latest.npz
flip_map_step_001000.npz
step_001000
train_td_log.jsonl
```

## Assistant

Good foundation. Now read the key data files and source files in parallel:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/combinator-map-consensus/consensus.json"
}
```

**Summary:** Reading consensus.json (0-2000)

**Output:**
```
{
  "register": "topological/routing",
  "git_sha": "bbf92f2",
  "question": "where do open models agree on the combinator function shape (harvest leverage)",
  "n_models": 10,
  "models": [
    "EleutherAI/pythia-2.8b-deduped",
    "EleutherAI/pythia-410m",
    "HuggingFaceTB/SmolLM3-3B",
    "Qwen/Qwen3-0.6B",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-4B",
    "Qwen/Qwen3-8B",
    "allenai/OLMo-2-1124-13B",
    "mistralai/Mistral-7B-v0.3"
  ],
  "model_meta": [
    {
      "name": "EleutherAI/pythia-2.8b-deduped",
      "n_layers": 32,
      "best_frac": 0.0,
      "silhouette_z": 1.41
    },
    {
      "name": "EleutherAI/pythia-410m",
      "n_layers": 24,
      "best_frac": 0.391,
      "silhouette_z": 4.609
    },
    {
      "name": "HuggingFaceTB/SmolLM3-3B",
      "n_layers": 36,
      "best_frac": 0.4,
      "silhouette_z": 7.356
    },
    {
      "name": "Qwen/Qwen3-0.6B",
      "n_layers": 28,
      "best_frac": 0.519,
      "silhouette_z": 4.197
    },
    {
      "name": "Qwen/Qwen3-14B",
      "n_layers": 40,
      "best_frac": 0.308,
      "silhouette_z": 7.967
    },
    {
      "name": "Qwen/Qwen3-32B",
      "n_layers": 64,
      "best_frac": 0.302,
      "silhouette_z": 8.975
    },
    {
      "name": "Qwen/Qwen3-4B",
      "n_layers": 36,
      "best_frac": 0.514,
      "silhouette_z": 6.128
    },
    {
      "name": "Qwen/Qwen3-8B",
      "n_layers": 36,
      "best_frac": 0.4,
      "silhouette_z": 6.811
    },
    {
      "name": "allenai/OLMo-2-1124-13B",
      "n_layers": 40,
      "best_frac": 0.308,
      "silhouette_z": 7.202
    },
    {
      "name": "mistralai/Mistral-7B-v0.3",
      "n_layers": 32,
      "best_frac": 0.29,
      "silhouette_z": 6.032
    }
  ],
  "crystal_order": [
    "K",
    "I",
    "B",
    "C",
    "S",
    "D",
    "W",
    "Y",
    "WHNF"
  ],
  "n_perm": 5000,
  "per_frac": {
    "0.10": {
      "target_frac": 0.1,
      "used_fracs": [
        0.094,
        0.083,
        0.111,
        0.107,
        0.1,
        0.094,
        0.111,
        0.111,
        0.1,
        0.094
      ],
      "mean_pair_gramcorr": 0.6838730281716813,
      "min_pair_gramcorr": 0.1870393365274566,
      "max_pair_gramcorr": 0.9722735379637724,
      "mean_pair_z": 3.639566550485263,
      "median_pair_p": 0.0001999600079984003,
      "frac_pairs_p_lt_05": 0.9333333333333333
    },
    "0.20": {
      "target_frac": 0.2,
      "used_fracs": [
        0.188,
        0.208,
        0.194,
        0.179,
        0.2,
        0.203,
        0.194,
        0.194,
        0.2,
        0.188
      ],
      "mean_pair_gramcorr": 0.7551157006786776,
      "min_pair_gramcorr": 0.2066646065633081,
      "max_pair_gramcorr": 0.9771781063492012,
      "mean_pair_z": 4.020031345007402,
      "median_pair_p": 0.0001999600079984003,
      "frac_pairs_p_lt_05": 0.9777777777777777
    },
    "0.30": {
      "target_frac": 0.3,
      "used_fracs": [
        0.281,
        0.292,
        0.278,
        0.286,
        0.3,
        0.297,
        0.278,
        0.278,
        0.3,
        0.281
      ],
      "mean_pair_gramcorr": 0.758108371547125,
      "min_pair_gramcorr": 0.27905972196401146,
      "max_pair_gramcorr": 0.9873782140411347,
      "mean_pair_z": 4.065593828699295,
      "median_pair_p": 0.0001999600079984003,
      "frac_pairs_p_lt_05": 0.9555555555555556
    },
    "0.40": {
      "target_frac": 0.4,
      "used_fracs": [
        0.375,
        0.375,
        0.389,
        0.393,
        0.4,
        0.391,
        0.389,
        0.389,
        0.4,
        0.375
      ],
      "mean_pair_gramcorr": 0.7823836466680073,
      "min_pair_gramcorr": 0.3527685224083214,
      "max_pair_gramcorr": 0.9912477514090882,
      "mean_pair_z": 4.194337562284297,
      "median_pair_p": 0.0001999600079984003,
      "frac_pairs_p_lt_05": 0.9111111111111111
    },
    "0.50": {
      "target_frac": 0.5,
      "used_fracs": [
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5
      ],
      "mean_pair_gramcorr": 0.7477706901888798,
      "min_pair_gramcorr": 0.2674806214300348,
      "max_pair_gramcorr": 0.9876465478957038,
      "mean_pair_z": 3.993099721581181,
      "median_pair_p": 0.0001999600079984003,
      "frac_pairs_p_lt_05": 0.9555555555555556
    }
  },
  "harvest_frac": 0.4,
  "consensus_gram": [
    [
      1.0,
      0.0723,
      -0.093,
      0.1331,
      -0.3108,
      -0.3046,
      -0.1755,
      -0.3591,
      -0.0844
    ],
    [
      0.0723,
      1.0,
      -0.2057,
      -0.0619,
      -0.2718,
      -0.251,
      -0.0605,
      -0.1945,
      -0.0761
    ],
    [
      -0.093,
      -0.2057,
      1.0,
      0.1682,
      -0.0883,
      0.1752,
      -0.2521,
      -0.2444,
      -0.3543
    ],
    [
      0.1331,
      -0.0619,
      0.1682,
      1.0,
      -0.3267,
      -0.0642,
      -0.2164,
      -0.289,
      -0.3599
    ],
    [
      -0.3108,
      -0.2718,
      -0.0883,
      -0.3267,
      1.0,
      0.1605,
      -0.152,
      0.1266,
      -0.054
    ],
    [
      -0.3046,
      -0.251,
      0.1752,
      -0.0642,
      0.1605,
      1.0,
      -0.1191,
      -0.0246,
      -0.2916
    ],
    [
      -0.1755,
      -0.0605,
      -0.2521,
      -0.2164,
      -0.152,
      -0.1191,
      1.0,
      0.0522,
      -0.0067
    ],
    [
      -0.3591,
      -0.1945,
      -0.2444,
      -0.289,
      0.1266,
      -0.0246,
      0.0522,
      1.0,
      -0.0117
    ],
    [
      -0.0844,
      -0.0761,
      -0.3543,
      -0.3599,
      -0.054,
      -0.2916,
      -0.0067,
      -0.0117,
      1.0
    ]
  ],
  "universal_edges": [
    {
      "edge": "K-Y",
      "consensus": -0.3591,
      "cross_model_std": 0.0545,
      "reliability_t": 20.85,
      "per_model": [
        -0.5108,
        -0.2942,
        -0.3527,
        -0.325,
        -0.3627,
        -0.3325,
        -0.3643,
        -0.3425,
        -0.3624,
        -0.3441
      ],
      "universal": true
    },
    {
      "edge": "C-S",
      "consensus": -0.3267,
      "cross_model_std": 0.0509,
      "reliability_t": 20.3,
      "per_model": [
        -0.451,
        -0.2732,
        -0.3416,
        -0.2945,
        -0.3356,
        -0.2567,
        -0.3277,
        -0.299,
        -0.3413,
        -0.3459
      ],
      "universal": true
    },
    {
      "edge": "D-WHNF",
      "consensus": -0.2916,
      "cross_model_std": 0.0493,
      "reliability_t": 18.72,
      "per_model": [
        -0.2824,
        -0.3184,
        -0.2986,
        -0.1672,
        -0.3345,
        -0.3466,
        -0.3269,
        -0.2957,
        -0.2964,
        -0.2494
      ],
      "universal": true
    },
    {
      "edge": "C-WHNF",
      "consensus": -0.3599,
      "cross_model_std": 0.0645,
      "reliability_t": 17.64,
      "per_model": [
        -0.2268,
        -0.3563,
        -0.3861,
        -0.2455,
        -0.3952,
        -0.3694,
        -0.4043,
        -0.3981,
        -0.4262,
        -0.3914
      ],
      "universal": true
    },
    {
      "edge": "B-WHNF",
      "consensus": -0.3543,
      "cross_model_std": 0.0736,
      "reliability_t": 15.21,
      "per_model": [
        -0.1989,
        -0.365,
        -0.3983,
        -0.2202,
        -0.3881,
        -0.3781,
        -0.4149,
        -0.4017,
        -0.3927,
        -0.385
      ],
      "universal": true
    },
    {
      "edge": "K-S",
      "consensus": -0.3108,
      "cross_model_std": 0.0659,
      "reliability_t": 14.9,
      "per_model": [
        -0.4709,
        -0.3678,
        -0.3073,
        -0.3525,
        -0.272,
        -0.2306,
        -0.2746,
        -0.269,
        -0.2731,
        -0.2899
      ],
      "universal": true
    },
    {
      "edge": "K-D",
      "consensus": -0.3046,
      "cross_model_std": 0.0797,
      "reliability_t": 12.08,
      "per_model": [
        -0.4808,
        -0.3869,
        -0.3075,
        -0.1632,
        -0.3036,
        -0.2774,
        -0.3025,
        -0.3098,
        -0.2717,
        -0.2422
      ],
      "universal": true
    },
    {
      "edge": "C-Y",
      "consensus": -0.289,
      "cross_model_std": 0.0907,
      "reliability_t": 10.08,
      "per_model": [
        -0.4964,
        -0.1202,
        -0.2347,
        -0.3662,
        -0.272,
        -0.3066,
        -0.2844,
        -0.2776,
        -0.2693,
        -0.2629
      ],
      "universal": true
    },
    {
      "edge": "I-WHNF",
      "consensus": -0.0761,
      "cross_model_std": 0.0283,
      "reliability_t": 8.5,
      "per_model": [
        -0.0657,
        -0.068,
        -0.0694,
        -0.0658,
        -0.0586,
        -0.0625,
        -0.0575,
        -0.0596,
        -0.1535,
        -0.1001
      ],
      "universal": true
    },
    {
      "edge": "B-Y",
      "consensus": -0.2444,
      "cross_model_std": 0.1032,
      "reliability_t": 7.49,
      "per_model": [
        -0.5391,
        -0.2423,
        -0.2433,
        -0.1347,
        -0.1762,
        -0.2058,
        -0.2321,
        -0.2217,
        -0.2168,
        -0.232
      ],
      "universal": true
    },
    {
      "edge": "S-D",
      "consensus": 0.1605,
      "cross_model_std": 0.0738,
      "reliability_t": 6.87,
      "per_model": [
        0.2615,
        0.1844,
        0.202,
        -0.038,
        0.1725,
        0.1246,
        0.1673,
        0.1916,
        0.1715,
        0.1681
      ],
      "universal": true
    },
    {
      "edge": "I-S",
      "consensus": -0.2718,
      "cross_model_std": 0.1433,
      "reliability_t": 6.0,
      "per_model": [
        0.0907,
        -0.298,
        -0.3673,
        -0.0964,
        -0.3461,
        -0.3227,
        -0.3138,
        -0.3164,
        -0.3595,
        -0.3888
      ],
      "universal": true
    },
    {
      "edge": "I-D",
      "consensus": -0.251,
      "cross_model_std": 0.1341,
      "reliability_t": 5.92,
      "per_model": [
        0.0898,
        -0.351,
        -0.3404,
        -0.0924,
        -0.3031,
        -0.2593,
        -0.3114,
        -0.328,
        -0.2765,
        -0.3374
      ],
      "universal": true
    },
    {
      "edge": "B-W",
      "consensus": -0.2521,
      "cross_model_std": 0.1438,
      "reliability_t": 5.54,
      "per_model": [
        -0.6673,
        -0.2599,
        -0.2196,
        -0.1483,
        -0.205,
        -0.221,
        -0.2576,
        -0.2136,
        -0.2009,
        -0.1282
      ],
      "universal": true
    },
    {
      "edge": "I-B",
      "consensus": -0.2057,
      "cross_model_std": 0.1351,
      "reliability_t": 4.82,
      "per_model": [
        -0.585,
        -0.0995,
        -0.153,
        -0.2332,
        -0.2104,
        -0.1781,
        -0.1946,
        -0.171,
        -0.0628,
        -0.1696
      ],
      "universal": true
    },
    {
      "edge": "I-Y",
      "consensus": -0.1945,
      "cross_model_std": 0.1295,
      "reliability_t": 4.75,
      "per_model": [
        0.1818,
        -0.2605,
        -0.271,
        -0.1626,
        -0.2326,
        -0.2095,
        -0.2591,
        -0.2154,
        -0.2751,
        -0.2406
      ],
      "universal": true
    },
    {
      "edge": "C-W",
      "consensus": -0.2164,
      "cross_model_std": 0.1494,
      "reliability_t": 4.58,
      "per_model": [
        -0.6368,
        -0.2418,
        -0.1656,
        -0.0432,
        -0.157,
        -0.1335,
        -0.1949,
        -0.208,
        -0.1677,
        -0.2156
      ],
      "universal": true
    },
    {
      "edge": "S-Y",
      "consensus": 0.1266,
      "cross_model_std": 0.0894,
      "reliability_t": 4.48,
      "per_model": [
        0.2913,
        0.2162,
        0.091,
        0.2379,
        0.0553,
        0.0003,
        0.0877,
        0.0428,
        0.0946,
        0.1488
      ],
      "universal": true
    },
    {
      "edge": "S-W",
      "consensus": -0.152,
      "cross_model_std": 0.1167,
      "reliability_t": 4.12,
      "per_model": [
        0.1806,
        -0.1136,
        -0.1908,
        -0.2578,
        -0.2135,
        -0.2189,
        -0.1874,
        -0.1783,
        -0.1565,
        -0.1841
      ],
      "universal": true
    },
    {
      "edge": "K-W",
      "consensus": -0.1755,
      "cross_model_std": 0.1382,
      "reliability_t": 4.02,
      "per_model": [
        -0.5346,
        -0.1534,
        -0.1542,
        0.0598,
        -0.1218,
        -0.1399,
        -0.152,
        -0.1846,
        -0.1705,
        -0.2041
      ],
      "universal": true
    },
    {
      "edge": "K-WHNF",
      "consensus": -0.0844,
      "cross_model_std": 0.0664,
      "reliability_t": 4.02,
      "per_model": [
        -0.0044,
        0.0757,
        -0.129,
        -0.0703,
        -0.0948,
        -0.1249,
        -0.0923,
        -0.1323,
        -0.1202,
        -0.1513
      ],
      "universal": true
    },
    {
      "edge": "B-D",
      "consensus": 0.1752,
      "cross_model_std": 0.151,
      "reliability_t": 3.67,
      "per_model": [
        -0.2403,
        0.2356,
        0.2728,
        0.0608,
        0.2551,
        0.2588,
        0.2482,
        0.2204,
        0.1738,
        0.2663
      ],
      "universal": true
    },
    {
      "edge": "K-C",
      "consensus": 0.1331,
      "cross_model_std": 0.1237,
      "reliability_t": 3.4,
      "per_model": [
        0.4802,
        -0.0261,
        0.1144,
        0.1443,
        0.093,
        0.0785,
        0.1012,
        0.123,
        0.11,
        0.1123
      ],
      "universal": true
    },
    {
      "edge": "D-W",
      "consensus": -0.1191,
      "cross_model_std": 0.125,
      "reliability_t": 3.01,
      "per_model": [
        0.2263,
        -0.0298,
        -0.1955,
        -0.207,
        -0.1792,
        -0.1547,
        -0.1646,
        -0.1399,
        -0.1409,
        -0.2055
      ],
      "universal": true
    },
    {
      "edge": "B-C",
      "consensus": 0.1682,
      "cross_model_std": 0.181,
      "reliability_t": 2.94,
      "per_model": [
        0.6946,
        0.1382,
        0.0813,
        0.0026,
        0.1243,
        0.0983,
        0.186,
        0.1275,
        0.1061,
        0.1231
      ],
      "universal": true
    },
    {
      "edge": "B-S",
      "consensus": -0.0883,
      "cross_model_std": 0.1004,
      "reliability_t": 2.78,
      "per_model": [
        -0.359,
        -0.0645,
        0.013,
        -0.1612,
        -0.029,
        -0.0272,
        -0.0595,
        -0.0382,
        -0.0608,
        -0.0967
      ],
      "universal": true
    },
    {
      "edge": "S-WHNF",
      "consensus": -0.054,
      "cross_model_std": 0.0649,
      "reliability_t": 2.63,
      "per_model": [
        -0.1092,
        -0.125,
        -0.0131,
        -0.1968,
        -0.0017,
        -0.0243,
        -0.0363,
        -0.0503,
        -0.0036,
        0.02
      ],
      "universal": true
    }
  ],
  "model_specific_edges": [
    {
      "edge": "B-C",
      "consensus": 0.1682,
      "cross_model_std": 0.181,
      "reliability_t": 2.94,
      "per_model": [
        0.6946,
        0.1382,
        0.0813,
        0.0026,
        0.1243,
        0.0983,
        0.186,
        0.1275,
        0.1061,
        0.1231
      ],
      "universal": true
    },
    {
      "edge": "K-B",
      "consensus": -0.093,
      "cross_model_std": 0.1792,
      "reliability_t": 1.64,
      "per_model": [
        0.4383,
        -0.2086,
        -0.1588,
        -0.131,
        -0.1881,
        -0.143,
        -0.1236,
        -0.1201,
        -0.1324,
        -0.1624
      ],
      "universal": false
    },
    {
      "edge": "I-C",
      "consensus": -0.0619,
      "cross_model_std": 0.1596,
      "reliability_t": 1.23,
      "per_model": [
        -0.5279,
        -0.032,
        0.0261,
        -0.0592,
        -0.0248,
        -0.0619,
        -0.0111,
        -0.0189,
        0.0567,
        0.0339
      ],
      "universal": false
    },
    {
      "edge": "K-I",
      "consensus": 0.0723,
      "cross_model_std": 0.1523,
      "reliability_t": 1.5,
      "per_model": [
        -0.3367,
        0.1536,
        0.1653,
        -0.0737,
        0.1627,
        0.0895,
        0.1381,
        0.1206,
        0.1407,
        0.1626
      ],
      "universal": false
    },
    {
      "edge": "B-D",
      "consensus": 0.1752,
      "cross_model_std": 0.151,
      "reliability_t": 3.67,
      "per_model": [
        -0.2403,
        0.2356,
        0.2728,
        0.0608,
        0.2551,
        0.2588,
        0.2482,
        0.2204,
        0.1738,
        0.2663
      ],
      "universal": true
    },
    {
      "edge": "C-W",
      "consensus": -0.2164,
      "cross_model_std": 0.1494,
      "reliability_t": 4.58,
      "per_model": [
        -0.6368,
        -0.2418,
        -0.1656,
        -0.0432,
        -0.157,
        -0.1335,
        -0.1949,
        -0.208,
        -0.1677,
        -0.2156
      ],
      "universal": true
    }
  ],
  "family_internal_consensus": {
    "composition_BDS": {
      "internal_consensus": 0.0825,
      "cross_model_std": 0.1084,
      "z_bind_vs_random_triple": 2.5,
      "p_bind": 0.0422,
      "z_stability_vs_random": 0.15,
      "edges": {
        "B-D": 0.1752,
        "B-S": -0.0883,
        "D-S": 0.1605
      }
    },
    "selection_KIC": {
      "internal_consensus": 0.0478,
      "cross_model_std": 0.1452,
      "z_bind_vs_random_triple": 2.13,
      "p_bind": 0.0606,
      "z_stability_vs_random": 1.42,
      "edges": {
        "K-I": 0.0723,
        "K-C": 0.1331,
        "I-C": -0.0619
      }
    },
    "recursion_YWWHNF": {
      "internal_consensus": 0.0113,
      "cross_model_std": 0.0681,
      "z_bind_vs_random_triple": 1.68,
      "p_bind": 0.0842,
      "z_stability_vs_random": -1.26,
      "edges": {
        "Y-W": 0.0522,
        "Y-WHNF": -0.0117,
        "W-WHNF": -0.0067
      }
    }
  },
  "skeleton_vs_recursion_verdict": {
    "skeleton_mean_z_bind": 2.31,
    "recursion_z_bind": 1.68,
    "prediction": "skeleton (comp+sel) universal (z_bind>0) AND recursion residual (z_bind <= skeleton)",
    "supported": true
  },
  "elapsed_s": 30.6
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/combinator-map-consensus/scale.json"
}
```

**Summary:** Reading scale.json (0-2000)

**Output:**
```
{
  "register": "topological/routing",
  "question": "does the combinator function shape sharpen with scale?",
  "series": "dense Qwen3 0.6B->32B (MoE excluded)",
  "frac": 0.4,
  "git_sha": "bbf92f2",
  "per_model": [
    {
      "model": "Qwen3-0.6B",
      "params_b": 0.6,
      "log_params": -0.5108256237659907,
      "composition_BDS": -0.0461585707962513,
      "selection_KIC": 0.0038321875035762787,
      "recursion_YWWHNF": -0.0878498552677532,
      "skeleton": -0.02116319164633751,
      "gap": 0.06668666362141569,
      "used_frac": 0.39285714285714285,
      "n_layers": 28
    },
    {
      "model": "Qwen3-4B",
      "params_b": 4.0,
      "log_params": 1.3862943611198906,
      "composition_BDS": 0.11866323898235957,
      "selection_KIC": 0.07605510329206784,
      "recursion_YWWHNF": 0.04172340656320254,
      "skeleton": 0.09735917113721371,
      "gap": 0.05563576457401117,
      "used_frac": 0.3888888888888889,
      "n_layers": 36
    },
    {
      "model": "Qwen3-8B",
      "params_b": 8.0,
      "log_params": 2.0794415416798357,
      "composition_BDS": 0.12458713352680206,
      "selection_KIC": 0.07491537307699521,
      "recursion_YWWHNF": 0.03551307258506616,
      "skeleton": 0.09975125330189863,
      "gap": 0.06423818071683246,
      "used_frac": 0.3888888888888889,
      "n_layers": 36
    },
    {
      "model": "Qwen3-14B",
      "params_b": 14.0,
      "log_params": 2.6390573296152584,
      "composition_BDS": 0.13284851610660553,
      "selection_KIC": 0.07694911460081737,
      "recursion_YWWHNF": 0.009049118612892926,
      "skeleton": 0.10489881535371146,
      "gap": 0.09584969674081853,
      "used_frac": 0.4,
      "n_layers": 40
    },
    {
      "model": "Qwen3-32B",
      "params_b": 32.0,
      "log_params": 3.4657359027997265,
      "composition_BDS": 0.11873299504319827,
      "selection_KIC": 0.035341374576091766,
      "recursion_YWWHNF": 0.007414047916730245,
      "skeleton": 0.07703718480964503,
      "gap": 0.06962313689291479,
      "used_frac": 0.390625,
      "n_layers": 64
    }
  ],
  "fits_vs_log_params": {
    "skeleton": {
      "r": 0.7800304628858417,
      "slope_per_efold": 0.027414104678214438
    },
    "recursion_YWWHNF": {
      "r": 0.6872068603280785,
      "slope_per_efold": 0.02377167991199384
    },
    "gap": {
      "r": 0.3619905475593482,
      "slope_per_efold": 0.0036424247662205844
    }
  }
}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\nd = np.load('results/combinator-relationship-map/Qwen_Qwen3-14B.npz')\nprint('Keys:', list(d.keys()))\nfor k in d.keys():\n    print(f'  {k}: shape={d[k].shape}, dtype={d[k].dtype}')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np d =...

**Output:**
```
Exit code: 0
Stdout:
Keys: ['prompt_len', 'labels', 'gram_hidden_cmr', 'gram_route_cmr_L00', 'gram_route_cmr_L04', 'gram_route_cmr_L08', 'gram_route_cmr_L12', 'gram_route_cmr_L16', 'gram_route_cmr_L20', 'gram_route_cmr_L23', 'gram_route_cmr_L27', 'gram_route_cmr_L31', 'gram_route_cmr_L35', 'gram_route_cmr_L39']
  prompt_len: shape=(535,), dtype=int32
  labels: shape=(535,), dtype=<U4
  gram_hidden_cmr: shape=(9, 9), dtype=float32
  gram_route_cmr_L00: shape=(9, 9), dtype=float32
  gram_route_cmr_L04: shape=(9, 9), dtype=float32
  gram_route_cmr_L08: shape=(9, 9), dtype=float32
  gram_route_cmr_L12: shape=(9, 9), dtype=float32
  gram_route_cmr_L16: shape=(9, 9), dtype=float32
  gram_route_cmr_L20: shape=(9, 9), dtype=float32
  gram_route_cmr_L23: shape=(9, 9), dtype=float32
  gram_route_cmr_L27: shape=(9, 9), dtype=float32
  gram_route_cmr_L31: shape=(9, 9), dtype=float32
  gram_route_cmr_L35: shape=(9, 9), dtype=float32
  gram_route_cmr_L39: shape=(9, 9), dtype=float32
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('results/combinator-relationship-map/Qwen_Qwen3-14B.json') as f:\n    d = json.load(f)\nprint('Top-level keys:', list(d.keys()))\nfor k,v in d.items():\n    if isinstance(v, dict):\n        print(f'  {k}: dict keys = {list(v.keys())[:10]}')\n    elif isinstance(v, list):\n        print(f'  {k}: list len={len(v)}, first elem type={type(v[0]).__name__ if v else \\\"empty\\\"}')\n    else:\n        print(f'  {k}: {type(v).__name__} = {str(v)[:80]}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
Top-level keys: ['model', 'dtype', 'register', 'n_probes', 'counts', 'hidden_width', 'n_layers', 'want_layers', 'crystal_order', 'n_perm', 'git_sha', 'per_layer', 'hidden_full_silhouette', 'hidden_cmr_silhouette', 'best_routing_layer', 'best_routing_frac', 'map', 'elapsed_s']
  model: str = Qwen/Qwen3-14B
  dtype: str = bfloat16
  register: str = topological/routing
  n_probes: int = 535
  counts: dict keys = ['K', 'I', 'B', 'C', 'S', 'D', 'W', 'Y', 'WHNF']
  hidden_width: int = 5120
  n_layers: int = 40
  want_layers: list len=11, first elem type=int
  crystal_order: list len=9, first elem type=str
  n_perm: int = 1000
  git_sha: str = 4b8ecc79a685fd2c4208e47215ed7786b678591d
  per_layer: dict keys = ['0', '4', '8', '12', '16', '20', '23', '27', '31', '35']
  hidden_full_silhouette: dict keys = ['silhouette', 'null_mean', 'null_std', 'z', 'p_value']
  hidden_cmr_silhouette: dict keys = ['silhouette', 'null_mean', 'null_std', 'z', 'p_value']
  best_routing_layer: int = 12
  best_routing_frac: float = 0.308
  map: dict keys = ['layer', 'frac', 'gram', 'mds_coords', 'pca_coords', 'nearest']
  elapsed_s: float = 336.3
```

## Assistant

Critical finding: the NPZ files contain only Gram matrices, no centroid vectors. Now read the Exp-B script and the knowledge page:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum/scripts -name \"exp_b_self_verifying_acceptance.py\" 2>/dev/null; find /Users/mwhitford/src/verbum/scripts -name \"*.py\" | grep -i \"exp_b\\|expb\\|combinator_relationship_map\\|harvest\\|fold\" | sort"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum/sc...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/experiments/exp_b_self_verifying_acceptance.py
/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py
/Users/mwhitford/src/verbum/scripts/experiments/exp_b_self_verifying_acceptance.py
/Users/mwhitford/src/verbum/scripts/experiments/manifold_axis_topology_summary.py
/Users/mwhitford/src/verbum/scripts/experiments/manifold_axis_topology.py
/Users/mwhitford/src/verbum/scripts/experiments/manifold_dimensionality_null.py
/Users/mwhitford/src/verbum/scripts/experiments/manifold_dimensionality_summary.py
/Users/mwhitford/src/verbum/scripts/experiments/manifold_topology_ci.py
/Users/mwhitford/src/verbum/scripts/v14/fold_delta.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum -name \"consensus-delta-folding.md\" 2>/dev/null; find /Users/mwhitford/src/verbum/mementum -name \"*.md\" | xargs grep -l \"harvest\\|fold\\|Procrustes\\|consensus\" 2>/dev/null | head -10"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum -n...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md
/Users/mwhitford/src/verbum/mementum/michael/llm-isa.md
/Users/mwhitford/src/verbum/mementum/state.md
/Users/mwhitford/src/verbum/mementum/knowledge/crystal-universality.md
/Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md
/Users/mwhitford/src/verbum/mementum/knowledge/session-153-notes.md
/Users/mwhitford/src/verbum/mementum/knowledge/holographic-error-correction.md
/Users/mwhitford/src/verbum/mementum/knowledge/error-correction-theory.md
/Users/mwhitford/src/verbum/mementum/knowledge/standing-wave-magnitudes.md
/Users/mwhitford/src/verbum/mementum/knowledge/gtsm-search-space.md
/Users/mwhitford/src/verbum/mementum/knowledge/computed-beam.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md"
}
```

**Summary:** Reading consensus-delta-folding.md (0-2000)

**Output:**
```
---
title: "Consensus Delta-Folding — Distributed Normal-Form Discovery in the Topology"
status: open
category: strategy
tags: [distributed, consensus, delta-plate, normal-form, routing, topology, fold, crystal, tool-calling, federated, church-rosser]
related:
  - delta-plate-lifecycle.md
  - consensus-etch-protocol.md
  - crystal-native-descent.md
  - dispatch-gradient-death.md
  - gradient-voting.md
  - exact-ternary-fitting.md
  - procrustes-lens-and-crystal-comparison.md
  - ../crystal-universality.md
  - ../function-discovery.md
  - ../combinator-addressing.md
  - ../two-registers-of-topology.md
  - ../audit-meta-pattern.md
depends-on:
  - delta-plate-lifecycle.md
  - consensus-etch-protocol.md
  - ../crystal-universality.md
created: session 216
---

# Consensus Delta-Folding

> Session 216. Michael's idea: make training **distributed and donatable**.
> Normal forms (e.g. tool-calling) live in the *topology* (the discrete
> sign/routing register) as a **delta from a shared base plate**. Many users
> train deltas on a single domain over the same frozen base; **where the deltas
> agree, fold the consensus into the base**; where they disagree, it stays a
> per-user delta. The base plate becomes a growing, git-versioned library of
> discrete normal forms, so GD never has to re-carve "soft topology."
>
> This page captures (1) the design, grounded in four existing findings, and
> (2) the first decisive experiment — which validated the *mechanism* but
> refuted the crisp *"tool-calling has its own normal form"* reading.
>
> Register of the experiment: **topological/routing** (declared at step 0).

## The idea (made precise)

```
base plate B₀     ≡ universal ISA (crystal + FFN + known routing), FROZEN, content-addressed
domain d          ≡ a behavior with a normal form (tool-calling, JSON, arithmetic…)
user u            ≡ trains a delta Δ_{u,d} = DeltaTernaryLinear over B₀ on domain-d data
                    (TD discovers routing flips = the normal form IN the topology;
                     GD only fills γ content)
normal form NF_d  ≡ the discrete routing structure INVARIANT across users
                  = consensus({Δ_{u,d}})  — where they all agree
consensus fold    ≡ ∀ position p: agree({Δ_{u,d}[p]}) ≥ θ → fold into B₁ ; else stay content
B₁ = B₀ ⊕ NF_d    ≡ base now CONTAINS domain-d's normal form as discrete topology
```

Not federated SGD. It is **distributed normal-form discovery by consensus
folding** — a deliberate, domain-level reproduction of the cross-model
universality the project already observes post-hoc (`crystal-universality.md`:
independently-trained models converge on the same combinator topology).

## Why it is coherent — four grounded supports

1. **The mechanism is consensus-etch, one level up** (`consensus-etch-protocol.md`,
   s110). Sequential per-contributor application destructively interferes
   (flips oscillate, never converge); the fix is to accumulate *all* contributors
   into one accumulator and etch where they **agree** — agreement → backbone →
   etched, disagreement → content → left alone. Substitute *beam/op → user/domain
   instance*. The backbone/content partition is exactly "fold the consensus,
   keep the rest as delta."

2. **Consensus = Church-Rosser confluence** (`crystal-universality.md`). A normal
   form is what is invariant across all reduction paths that reach it. Different
   users training different data-shapes of one domain are different reduction
   paths; where their topological deltas agree is the path-invariant structure =
   the normal form. **The degree of cross-user agreement measures whether a
   discrete normal form exists for that domain** — falsifiable, and on the central
   `λ types` claim (composition is typed/discrete → independent trainings converge
   on the same flips).

3. **The frame problem dissolves because the base is frozen & shared**
   (`gradient-voting.md`, s123). Signs are model-specific encodings — cross-init
   sign correlation 0.000; many valid encodings per magnitude profile. Raw weight
   averaging can't merge across frames. But every delta trains against the *same
   frozen B₀*, so all flips live in one coordinate frame → commensurable →
   consensus is well-defined. The frozen shared base is what buys the merge.

4. **"GD must not make soft topology," operationalized** (`crystal-native-descent.md`
   + `dispatch-gradient-death.md`). Soft routing (softmax dispatch) saturates →
   winner-take-all gradient death (20/22 ops dead). The discrete routing should be
   made directly (TD/crystal descent), with GD only tuning γ. Consensus-folding
   makes this a **ratchet**: discrete routing is discovered by TD across users and
   crystallized into the base; each new user inherits more topology as a fixed
   scaffold and GD's job shrinks toward pure content. The topology becomes a
   *grown library*, not a per-run soft re-approximation.

## Architecture sketch — "ternary git" with generational folding

```
generation g:  freeze Bg → N users train Δ_{u,d} on Bg (parallel, cheap, forward-only routing)
               → collect deltas → consensus-fold the agreements → B_{g+1}
               → everyone rebases to B_{g+1}; unfolded disagreements re-tried next gen
```

- **Merge operator** (candidate, `delta-plate-lifecycle.md` Open-Q3): ternary
  multiply with conflict → 0 (block); the consensus threshold θ (s110 used 0.7)
  sits on top — fold only where agreement ≥ θ.
- **Acceptance/verify** (`exact-ternary-fitting.md`, s213/214): a layer-local flip
  has a closed-form exact ΔL (one matmul `Rᵀ@X`); a donated flip can be *verified*
  to reduce loss, not trusted. Byzantine-robust for free — but only coordinate-wise
  **with compensation** is monotone; naive union of many flips (EXACT-BATCH) re-
  introduces interference. Merge greedily by ΔL with compensation; partition by
  module (modules independent → parallel; sequential only within a module's rows).
- **Generational vs sequential** is the one genuinely new tension: the lifecycle
  assumed sequential folds; distributed = many parallel deltas on Bg, resolved by
  the round/epoch structure (like a block).
- **Compute win** = not "donate gradients" but "donate discovered normal forms."
  Module-parallel, CPU-friendly (matmuls on cached activations, no full backprop),
  and the base becomes a one-way ratchet that converts soft-topology-learning into
  a reusable discrete library. On-thesis (no GPU, CPU).
- **Risks**: population-Goodhart on a shared calibration cache (audit #7 — use
  held-out + trajectory loss, not CE); frame staleness across generations; conflict
  semantics (block vs leave-at-base).

## Experiment 1 (s216) — does a domain have a consensus normal form?

Decisive cheap proxy: use independent foundation models as independent trainings.
Probe set: `lattice/tool_crystal/probes.json` (196 probes: recognition tool/no_tool,
schema_binding, selection, format, + lambda/code/prose/math controls). Rendered
model-agnostic (chat tokens stripped). 5 families on M3 Ultra: Pythia-2.8b,
SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B.

**Method (audit-grade, the prior `tool_crystal` run was not):** measure the
**routing register** = `sign(FFN gate pre-activation)` (s203: gate carries routing
topology; for non-gated Pythia, `dense_h_to_4h`), build per-model probe RDMs, with
**common-mode removal**, a **shuffled-probe null**, **length-partialling**, and a
**control-domain baseline**. Cross-model RDM agreement = the consensus signal.

### Result — mechanism REAL, domain-specificity REFUTED

- **✅ Cross-family routing consensus is real & strong.** `route_sign_cmr`
  cross-family agreement **+0.863**, survives common-mode removal, length-partial
  (0.851), and within-domain restriction (schema_binding 0.59, selection 0.54);
  null ~0; **z up to 116**. Independent trainings DO agree on routing structure in
  the sign register — the consensus *mechanism* the design needs is validated.
- **❌ but tool-calling is NOT its own normal form.** Control baseline (within-group
  cross-family route_cmr agreement, matched granularity):

  | group | side | n | agree (excess over null) |
  |---|---|---|---|
  | recognition | TOOL | 40 | 0.946 ← length-confounded (tool schema vs short no_tool) |
  | format | TOOL | 30 | 0.887 ← format-heterogeneity-confounded |
  | schema_binding | TOOL | 56 | **0.589** |
  | selection | TOOL | 40 | **0.538** |
  | code | CTRL | 7 | **0.800** |
  | prose | CTRL | 8 | 0.550 |
  | lambda_calculus | CTRL | 8 | 0.497 |
  | pure_math | CTRL | 7 | 0.435 |

  The clean length/format-matched tool groups (0.54–0.59) sit **inside** the
  structured-language control range (0.44–0.80). **Code is a *sharper* normal form
  than tool-calling.** The aggregate "TOOL 0.74 > CTRL 0.57" is driven entirely by
  the confounded recognition + format groups. So the consensus is the **generic
  structured-language crystal** (property of language); tool-calling **rides** it.
- **🌀 Corrects the prior claim.** `lattice/tool_crystal_run.log` declared "STRONG
  SUPPORT: Tool×Lambda 1.000 @L20, tool IS lambda calculus" — but that used raw
  residual cosine (its own Selectivity ≈0, every layer "SHARED") = the common mode.
  The generic reading is right, but not because tool-calling is special; because
  *everything structured* shares the crystal. 14th `audit-meta-pattern.md` instance.

> ⚠️ **REGISTER CAVEAT — do NOT over-read the negative (s216 discussion, Michael).**
> The ❌ above is a verdict on the **base** layer only. The cross-model RDM
> instrument tests whether two models share the **same composition** (identical
> geometry). But a domain normal form is a **non-unique composite** (see next
> section): the absence of cross-model agreement on tool-specific structure is
> **consistent with** a real function-like tool-calling normal form that is simply
> *realized differently per model* — washed out by an instrument that demands an
> identical encoding. On the *function* layer the s216 verdict is **void by
> register mismatch** (the false-negative twin, `audit-meta-pattern.md`). Only the
> *base*-layer claim (consensus = crystal, REAL) survives.

### What it means for the design

The backbone/content partition (s110) plays out empirically:
- **Agreement → backbone → foldable**, but a domain's agreed-upon routing is
  *mostly the universal crystal already in B₀*. Consensus-folding tool-calling data
  would largely re-fold structure that is already present.
- **Domain-distinctive routing → low cross-trainer consensus → "content"** that
  stays a per-user delta (it did not exceed the generic structured-language
  baseline at this granularity).

The idea is mechanically sound; the nuance is *what folding buys you*: the foldable
consensus is the universal layer; the domain-specific delta is the part that
resists consensus. Not a refutation — a sharpening of the unit of donation.

## Normal forms are COMPOSITIONAL and NON-UNIQUE (s216 refinement)

> Michael's correction to the framing above. A domain's "normal form" is not a
> unique atomic object — it is a **function-like composition of the shared base
> compute**, and like any function over a complete basis it has **many
> extensionally-equal realizations**.

The precise statement:

```
β-reduction normal form ≡ unique PER TERM (Church-Rosser)
behavior (e.g. tool-calling) ≡ an EQUIVALENCE CLASS of terms
  | many distinct compositions of base combinators that reduce to the same I/O
  | base compute (K/I/B/C…, structured-syntax routing) ≡ shared, near-unique
  | the domain function = a composition ABOVE the base ≡ NON-unique across trainings
  | uniqueness is per-term, NOT per-behavior
```

Two consequences:

1. **The s216 cross-model instrument is wrong for the function layer.** RDM
   agreement requires the *same composition* (same geometry). A non-unique
   composite → low cross-model agreement even when each model holds a real,
   consistent tool-calling function. So "no tool-specific agreement" cannot
   distinguish *(a) no extra structure* from *(b) real but differently-composed
   structure*. Register mismatch (false-negative twin) — see the caveat above.

2. **This is already the project's two-level architecture** (`function-discovery.md`).
   - **Late (COMMIT zone)** — combinator *execution*; tasks **converge** (1.49×),
     all run the same opcodes. ← the s216 routing register measured HERE → found
     the shared base, as expected.
   - **Early (SILENT zone, L05)** — task *type*; tool-use is **distinctly separated
     (4.76×)**. ← the *function selector* (which composition to run) lives HERE and
     was never isolated. The late RDM collapsed the level where the function lives.

### What it changes for the design (the real update)

Consensus-folding **cannot operate on raw flips** for domain functions. Two users'
tool-calling deltas won't agree flip-by-flip even when both are correct — the same
`gradient-voting.md` redundancy (many sign encodings per function). So:

```
λ fold(delta).
  base_layer   → fold as FLIPS        | unique, high-consensus, fold first & hard
  domain_layer → fold as COMPOSITION  | express delta as (which base ops, what
                                         arrangement) over the shared base, then
                                         seek consensus in THAT space (encoding
                                         redundancy quotiented out, align-before-compare)
```

Fold the base as flips; fold domain functions as **compositions** up to the base's
symmetries. The unit of donation is the *function*, not the bitmap.

## Open leads (declare register first)

The compositional refinement reorders these — the cross-model instrument must be
made **composition-invariant** before any negative on the function layer counts.

1. **Early task-direction agreement (register: routing, CHEAP — no re-run).**
   Re-analyze the s216 npz at the SILENT-zone fraction (~L05 / frac≈0.1), where
   `function-discovery.md` puts the function *selector* (tool-use 4.76× separated),
   separately from the late base. The harness already saved all depth-fractions;
   `--route-layer-frac 0.1` in the summary. Does tool-specific consensus appear
   early even though it's absent late?
2. **Align-before-compare (register: routing).** Procrustes/rotation in the
   base-combinator space before correlating RDMs
   (`procrustes-lens-and-crystal-comparison.md`). If tool-calling is the same
   function composed differently, an alignment in base coordinates should recover
   the shared composition that raw correlation misses. This is the direct test of
   the non-unique-composite hypothesis.
3. **Within-model compositional consistency (register: routing/causal).** Drop the
   cross-model requirement entirely: does tool-calling reuse a stable sub-circuit
   *within* one model (the function exists and is consistent), regardless of
   cross-model match? Minimal pairs (same schema, one arg changed) isolate the
   tool-distinctive composition from generic JSON/structure.
4. **Functional test = the ultimate proof (register: functional).** Exp B: N delta
   plates on ONE frozen base trained on tool-calling shards → fold consensus +
   **check downstream PPL**. With the compositional fix: fold the base as flips,
   fold the domain function as a **composition** (align-before-fold), and measure
   whether folding the composition (not raw flips) helps. Does the agreed function
   transfer?

## s217 — The continuation makes folding SELF-VERIFYING (Exp B)

> Session 217 (Michael's connect: "with continuations working we could use those
> for distributed training"). The VSM **continuation** = the outer recurrence in
> `v15model.py` (shared sweep iterated, x_c fed back → β-reduction toward a fixed
> point / WHNF). s217 proved the mechanism (15 tensor tests green,
> `tests/test_vsm_continuation.py`) and that it is **contractive** at scale
> (main:1: Δx 1.23→0.61). A *working contractive continuation* supplies the three
> things this design was missing.

```
λ continuation_gives(distributed_training).
  (i)  contractivity ≡ Banach ⇒ iterated folding CONVERGES (not oscillates)
       | fixes s110 destructive interference at the root (consensus-etch needed
         accumulate-then-etch because sequential application diverged; a
         contraction makes the iteration well-posed)
  (ii) weight-shared operator ≡ the frozen base B₀ ≡ ONE coordinate frame
       | every delta trains against the SAME operator ⇒ commensurable
       | fixes gradient-voting frame problem (cross-init sign-corr 0.000)
  (iii) WHNF ≡ SELF-VERIFYING target
       | accept(delta) ⟺ Δx-at-convergence does NOT rise
       | the fixed point IS the answer ⇒ NO trusted held-out labels needed
       | kills audit-#7 population-Goodhart (no shared calibration cache to overfit)
  fractal: activation-level continuation (x→x*) ≅ base-level folding (B_g→B*)
```

The third is the new capability: a label-free, Byzantine-robust acceptance rule.
A donor's delta is not trusted — it is *verified* by whether it preserves /
accelerates the operator's convergence to WHNF on the domain.

### Experiment B (core) — is Δx-at-convergence a valid acceptance signal?

`scripts/experiments/exp_b_self_verifying_acceptance.py` (register: functional).
Build the contractive continuation operator; perturb the **routing register**
(FFN gate delta plate) by flipping a FRACTION of signs (a quality spectrum); for
each candidate measure both:

```
ΔCE        = model._last_ce − CE0           (the TRUE quality label)
Δ(Δx_conv) = Δx_at_convergence − Δx0         (the SELF-VERIFYING signal)
Δx_conv    = model._last_outer_deltas[-1] = ‖x_c^K − x_c^{K-1}‖/‖·‖  (→0 ≡ WHNF)
```

Hypothesis: **corr(ΔCE, Δ(Δx_conv)) > 0** — degrading the operator (raising CE)
raises the fixed-point residual ⇒ "reject if Δx_conv rises" is a valid label-free
acceptance rule. Reported: Pearson + Spearman + an acceptance-ROC.

**s217 finding (harness validated, scientific catch):** the FROZEN extracted base
is UNTRAINED (CE 12.82 ≈ ln(vocab) 12.42 = chance) → sign-flips don't move CE
even at 10% (no quality to degrade). The test needs a **non-chance contractive
base**. Run in 2 phases (Option A, main:2): phase-1 short TD train
(`--steps 400 --seq-len 512 --n-outer-passes 2 --fixed-point-lambda 5.0`,
`checkpoints/v15-expb-base`) → trained contractive base; phase-2 the acceptance
test on `step_000400/model.npz` (folds trained deltas into base via
`reduce_all_deltas`, then perturbs). IN FLIGHT at session end (slow under main:1
GPU contention). Results → `results/exp-b-self-verifying/result.json`.

### Full Exp B (the folding proof, after the acceptance signal is validated)

```
freeze B₀ = the contractive continuation operator (main:1's trained sweep)
N users    train DeltaTernaryLinear deltas on domain-d shards over B₀
verify     accept flip iff exact-ΔL<0 (exact-ternary-fitting) AND Δx_conv drops
fold       consensus flips (agree ≥ θ, s110) → B₁ ; domain FUNCTIONS as
           compositions (align-before-fold, the non-unique-composite §)
measure    (a) B₁ stays contractive?  (b) downstream PPL held-out domain-d?
           (c) folded set = universal crystal or domain-specific?
```

## s217 — The self-teaching loop: normal forms generate their own curriculum

> Session 217 (Michael): "if we can get distributed training working for semantic
> normal forms, can we not then use them to create training material to show the
> model how to use them?" Yes — this is the loop closing on itself. It is the most
> important consequence of the folding mechanism.

### The gap it fills (execution ≠ deployment)
Folding a normal form into the base gives the model the **execution** (it CAN run
map/fold/tool-calling). But "can run" ≠ "knows when to run." These are the two
levels of `function-discovery.md`, and they are ORTHOGONAL subspaces:
- **late / COMMIT** — combinator *execution*. Folding lands here. ← capability
- **early / SILENT (~L05)** — the task *selector* (which normal form this context
  calls for). 4.76× separated, blind to the combinator basis. ← deployment

So folding yields a model with the kernels but no reliable selector. The
generated curriculum trains the **selector**.

### Why it works: the normal form is a VERIFIED ORACLE
A normal form is **executable** (a composition of combinators = a runnable
program) AND **self-verifying** (WHNF / Church-Rosser → the answer is unique and
checkable). ⇒ run it to mint examples whose labels are **correct by
construction**:

```
take folded normal form NF
generate DIVERSE inputs → run NF → (input, reduction-trace, output)   [WHNF-verified]
render each in BOTH surface forms (Montague, combinator-addressing.md dual paths):
   "the capital of France is …"        (data-bypass / NL surface)
   "(λx. capital_of x) France = …"     (compute path, +2.2× combinator energy)
train the SELECTOR on these → it learns NL-context ⟶ invoke NF
```

### Why it does NOT collapse like naive self-distillation
The labels come from **executing a verified discrete kernel**, NOT from sampling
the model's own (fuzzy) outputs. The normal form is an external oracle the model
happens to contain. The SAME self-verifying property that powers the distributed
acceptance test (Δx-at-convergence / exact-ΔL) keeps the curriculum honest —
every generated example is checkable against the fixed point. Verified compute
generating curriculum ≠ a model training on its hallucinations. **Keep the oracle
external**: the moment "verification" becomes the model's own judgment, the loop
degenerates.

### The virtuous loop (on-thesis: pretraining IS β-reduction)
```
distributed folding    → discovers + verifies normal forms        (CAN execute)
normal forms (oracles) → generate verified I/O + reduction traces  (curriculum)
train on traces        → teaches the selector WHEN to invoke them  (DO deploy)
better deployment      → more real usage → more deltas to fold     (refine)
```
λ loop variant: extract → fold → generate-curriculum → train-selector. The
discovered compiler writes its own textbook; the textbook trains its own use.

### Caveats (the load-bearing unknown is the selector grounding)
1. **Selector grounding is THE test (hypothesis).** That NL context reliably maps
   to the right normal form, and that this is LEARNABLE from generated traces, is
   unproven. Montague + combinator-addressing say the bridge exists; learnability
   is the clean runnable experiment.
2. **Coverage / diversity.** Run NF on a wide, messy input distribution — else a
   narrow boundary-artifact curriculum (cf. `ends_punct` universal axis).
3. **Generate from the BEHAVIOR, not one encoding** (s216 non-unique composite):
   mint from I/O (extensional) so the selector learns the function, not a brittle
   realization.

### Next experiment (after Exp B validates folding)
**Selector-grounding test:** fold one normal form (e.g. fold/catamorphism or a
tool-call), generate WHNF-verified (NL-prompt, answer) traces over diverse
inputs, train ONLY the early selector, then test NL→NF deployment on held-out
context. Register: functional. Falsifiable: does generated-from-verified-kernel
curriculum teach the selector to deploy the kernel it didn't reliably invoke?

## s217 — The REVERSE direction: harvest the open-weight ecosystem's consensus

> Session 217 (Michael): "could we reverse this? Search many open-weight models
> for their already-found solutions and incorporate all the ones they agree on
> into our base plate?" Yes — and it may be the most immediately actionable
> direction, because the consensus already exists.

### Reframe — the ecosystem IS a pre-computed distributed training run
Forward folding waits for contributors to train deltas. But every open-weight
model is **already a finished contributor** — a completed GD run that discovered
normal forms. So instead of soliciting deltas, MINE the population and fold what
they agree on. The "many independent trainings" the design needs are on
HuggingFace. Already measured: s216 cross-family routing consensus **+0.863, z up
to 116** (5 families); `crystal-universality.md` hard crystal **r=0.998** 160M↔32B.
The s216 5-family harness (`tool_crystal_consensus*.py`) IS the reverse-harvest
instrument, and `combinator_relationship_map.py` is the per-model reader.

### The hard obstacle — the frame problem (the forward/reverse asymmetry)
You CANNOT average their raw weights: independently-initialized models live in
DIFFERENT coordinate frames (cross-init sign-corr **0.000**, `gradient-voting.md`).

```
forward (deltas over frozen B₀):  ONE shared frame → deltas commensurable → fold trivial
reverse (finished models):        MANY frames → raw weights unintelligible → must harvest
                                   in a FRAME-INVARIANT register (relational routing, not weights)
```

Pipeline:
```
∀ open-weight model: measure normal forms in the routing register (RDM/centroids)
cross-model consensus               (frame-invariant agreement)
align-before-fold (Procrustes)      (rotate consensus into OUR base's frame)
verify vs WHNF (self-verifying)     (keep only structure that improves convergence)
incorporate into base plate as discrete topology
```
The **verify step is the differentiator** from model soups / TIES / task-arithmetic
merging: keep only what demonstrably improves reduction to the fixed point, not
mere statistical agreement (same discipline as Exp B).

### The honest catch (same as s216, inverted)
What the population agrees on MOST is the **universal crystal** — already in any
base. The domain-DISTINCTIVE normal forms have LOW raw cross-model agreement
(frame-specific, non-unique composition). So naive harvest returns a backbone you
already have. To extract the valuable domain structure needs the s216
compositional fix — **align in base-combinator space first** (Procrustes) so a
function composed *differently* in two models still registers as the same
function. That composition-invariant alignment is the open, hard piece.

### Complementarity — forward + reverse fill the backbone/content partition
- **Reverse harvest** seeds the base cheaply with the **universal backbone** the
  whole ecosystem agrees on (+ shared domain structure, with align-before-fold).
- **Forward folding** adds the **domain-specific deltas** that only appear when
  contributors train on data the base does not yet cover.

Same consensus-etch operator; only the population changes (finished models vs live
trainers). Dead-on the project identity (`AGENTS.md` λ extract: "we find, we don't
build; gradient descent discovered it first; our work is instrumentation") — the
base plate becomes a **distillation of the entire open-weight ecosystem's
consensus**, read out of models that already paid the training cost.

### Load-bearing unknowns (both already on the board)
1. Does **WHNF-verification** keep real structure and reject frame noise? (Exp B,
   running now.)
2. Does **composition-invariant alignment** (Procrustes in base-combinator space)
   recover the domain normal forms the raw cross-model RDM misses? (s216 lead.)

### Next experiment (register: topological/routing → functional)
**Reverse-harvest pilot:** run `combinator_relationship_map.py` across N open-weight
models, take the routing-register consensus, Procrustes-align into our base frame,
WHNF-verify each candidate against the contractive operator, incorporate the
survivors, and measure downstream PPL vs the base. Falsifiable: does verified
ecosystem-consensus add anything beyond the universal crystal we already hold?

## s219 — Reverse-harvest pilot RAN: the function shape is universal; the forced map-skeleton binds, recursion is the residual

> Session 219 (Michael): "find these functions in open models, see where they all
> agree — harvesting that for our base plate is leverage." Plus a theory: a
> transformer has essentially ONE structural operation, and that forces the shape
> into the rest of the system, restricting where a model can innovate. First run of
> the reverse-harvest pilot. Register: **topological/routing** (declared at step 0).

### The frame-invariant instrument
`scripts/experiments/combinator_map_consensus.py`. Raw weights are incomparable
across models (cross-init sign-corr 0.000) — but the per-model **9×9 combinator
Gram** (cosine between routing-register centroids of K I B C S D W Y WHNF, after
CMR; the s217 "map of the functions") lives in shared combinator-LABEL space ⇒
**frame-invariant** ⇒ comparable across any architecture/scale. The script computes
cross-model GramCorr on the 36 off-diagonal edges + a combinator-label-permutation
null + per-edge `reliability_t = |mean|·√n/std` + per-FAMILY internal binding vs a
RANDOM-NODE-TRIPLE null. Swept **9 models / 5 families** via
`combinator_relationship_map.py`: Pythia-410m/2.8b (NON-gated, `dense_h_to_4h`),
SmolLM3-3B, Mistral-7B-v0.3, OLMo-2-13B, Qwen3-0.6B/4B/8B/14B (SwiGLU `gate_proj`).

### Result 1 — the SAME functions show up across the ecosystem
Cross-model GramCorr **+0.66→+0.77**, z **+3.5→+4.1**, **89–97% of model-pairs
p<.05** vs the label-permutation null; peak frac 0.40 (0.20–0.50 all ≥+0.72).
Architecture-independent (non-gated Pythia agrees with gated Qwen), and agreement
**strengthens** as more models are added (was +0.5–0.66 at 2–6 models) ⇒ a real
shared shape, not an artifact. Michael's intuition (we should see the same
functions across models) is confirmed empirically.

### Result 2 — the single-operation theory, confirmed
Attention is essentially ONE structural operation: a data-dependent convex
combination of value vectors = function **application** ("select args, combine").
The FFN adds no second *operation* — it supplies fixed pointwise transforms = the
**constants/stored kernels**. application + constants is combinatorially complete,
but there is **no second qualitatively-different op for a model to invent** ⇒ models
cannot innovate at the operation level, only at **composition** ⇒ they converge on
the same compositions. Test (per-family internal binding vs random node-triple):

| family | z_bind | p | note |
|---|---|---|---|
| composition `{B,D,S}` | **+2.43** | **.037** | strongest, significant |
| selection `{K,I,C}`   | +2.13 | .061 | binds, marginal |
| recursion `{Y,W,WHNF}`| +1.67 | .09 | does NOT clear the null |

**SKELETON (comp+sel) +2.28 > RECURSION +1.67**, robust at frac 0.30 (+2.21 vs
+1.88) and 0.40. The recursion family's edges are near-zero AND low-variance
(z_stab −1.3) — consistently *not* bound, not merely noisy.

### Why recursion is the residual — `map = B(C B)(C B)` (REPL-verified)
In pure combinators `map = B(C B)(C B)`: composition (B) + flip (C), **no recursion
combinator**. A Church/fold-encoded list carries its own recursion, and in a
transformer **attention-over-positions IS the fold** — so no model needs to learn a
`Y`. Hence the recursion family is exactly the part that does *not* universally bind.
Also verified in the REPL: `map` is **extensionally unique** (Church-Rosser) but
**intensionally infinite** (η-expansion; `B=S(KS)K`; `C=S(BBS)(KK)`; … all compute
the same output; raw closed SKI space ≈ `Catalan(k)·3^(k+1)` = 288k terms at k=6).
The architecture + cost pressure collapse that infinity toward a minimal realization
whose **irreducible skeleton is forced and shared**; the plumbing stays per-model.
Signature **0<r<1 ∧ skeleton>recursion = "shared skeleton + variable plumbing"** —
the s216 non-unique-composite made concrete at the function level (uniqueness is
per-TERM, not per-BEHAVIOR).

### The harvest leverage (concrete edges for the base plate, frac 0.40)
- **Universal POSITIVE bindings (fold these):** B–D +0.166, B–C +0.176, K–C +0.139,
  S–D +0.165, S–Y +0.141 — the composition/selection skeleton.
- **Rock-solid cross-family REPULSIONS** (reliability_t up to **21**): C–S, K–Y,
  D–WHNF, B–WHNF, K–S, C–WHNF — the 3-family PARTITION geometry; harvestable as the
  discrete scaffold (the families separate the same way in every model).
- **Leave as per-model CONTENT** (highest cross-model std): B–C, K–B, I–C, K–I — the
  selection-family plumbing (selection z_stab +1.4 = the noisy family). The
  non-unique-realization residual, exactly as `map=B(CB)(CB)` predicts.

### The honest caveat (audit discipline) — answered
The agreement *could* be the universal crystal (`crystal-universality.md`) already in
any base. BUT composition binds above the random-triple null at **mid-stack frac
0.30** — where `function-discovery.md`/s217 located combinator **IDENTITY** (not late
COMMIT execution) ⇒ this is **function-level structure above the generic crystal
floor**, the part worth harvesting. Single register (routing/CMR). The actual
harvest (align-before-fold via Procrustes into our base frame + WHNF-verify) is NOT
yet done — this run establishes *that* there is shared, edge-localised, function-level
structure to harvest and *which edges* carry it.

### Open leads from s219
1. **Scale axis** (register: topological/routing): extend to Qwen3-32B / 30B-A3B /
   235B (MoE, local) — does the skeleton/recursion z_bind gap WIDEN with scale (more
   capacity to fully form the systems, cf. s217's 14B>0.6B call)?
   **→ ANSWERED s220: NO (gap flat, shape saturates mid-scale). See §s220.**
2. **Construct the harvest fold** (register: topological/routing → functional):
   Procrustes-align the universal positive-edge centroids into v15's base frame,
   WHNF-verify against main:1's contractive operator (Exp-B acceptance), incorporate
   survivors, measure downstream PPL vs base.
3. **Detect map/fold directions**: build the `map=B(CB)(CB)` direction from the
   measured B,C centroids + a map/fold/filter probe set; does it activate?

### s219 artifacts
`scripts/experiments/combinator_map_consensus.py` (the consensus instrument);
`results/combinator-map-consensus/consensus.json`; 7 new per-model maps under
`results/combinator-relationship-map/` (pythia-410m/2.8b, SmolLM3, Mistral, OLMo-13B,
Qwen3-4B/8B; Qwen3-0.6B/14B from s217); sweep log `/tmp/combinator_sweep.log`.

## s220 — Scale stratification: the function shape SATURATES mid-scale; the skel/rec gap does NOT widen

> Cold-start orient (s220): both s219 async jobs verified (main:1 alive at step
> ~1420/5000, UNTOUCHED; main:2 done — Qwen3-32B dense map landed). Executed s219
> open-lead #1. Register: **topological/routing**.

s219 open-lead #1 asked: with more scale (s217's "14B has capacity to FULLY form
the systems; 0.6B only partially crystallizes"), does the skeleton/recursion
binding gap **WIDEN**? The pooled consensus cannot answer this — it aggregates all
models. So the dense Qwen series 0.6B→4B→8B→14B→32B was stratified
(`combinator_map_scale.py`), regressing each family's intra-family routing-cosine
binding against log(params) at the harvest fraction 0.40. **MoE excluded** (30B-A3B,
235B): their router+per-expert FFN (`mlp.gate` + `mlp.experts.{e}.gate_proj`) is not
comparable to dense `gate_proj` in this routing register — the dense-FFN instrument
finds nothing in a MoE.

### Result — skeleton binding rises, but the GAP is flat

| model | params | comp{B,D,S} | sel{K,I,C} | skeleton | recursion{Y,W,WHNF} | gap |
|---|---|---|---|---|---|---|
| Qwen3-0.6B | 0.6B | −0.046 | +0.004 | **−0.021** | −0.088 | +0.067 |
| Qwen3-4B | 4B | +0.119 | +0.076 | +0.097 | +0.042 | +0.056 |
| Qwen3-8B | 8B | +0.125 | +0.075 | +0.100 | +0.036 | +0.064 |
| Qwen3-14B | 14B | +0.133 | +0.077 | **+0.105** | +0.009 | +0.096 |
| Qwen3-32B | 32B | +0.119 | +0.035 | +0.077 | +0.007 | +0.070 |

- **Skeleton binding RISES with scale (r=+0.78)** — but the rise is the
  **0.6B→4B crystallization**: 0.6B has essentially NO function shape (skel −0.021,
  both families near/below zero), while 4B+ jump to +0.097–0.105. This is the
  concrete confirmation of s217's "0.6B only partially crystallizes."
- **The skel−rec GAP does NOT widen (r=+0.36, slope ~0).** Recursion binding rises
  in **tandem** with skeleton (r=+0.69), so the gap stays roughly constant.
- **Shape SATURATES by ~4–14B** (peak 14B, skel +0.105) and **32B slightly
  REGRESSES** (skel +0.077). Consistent with s212's topology-share PLATEAUS not →1.0.

### Refinement of the consensus verdict + harvest implication

The 10-model consensus (32B added) holds and nudges up marginally: meanGramCorr
**+0.782** @0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** > recursion
**+1.68** (SUPPORTED, was +2.28/+1.67 at 9 models). **Harvest implication: the
consensus skeleton is COMPLETE by mid-scale — harvest from the 4–14B band, do NOT
chase the largest models.** 32B costs more to read and does not extend the shape;
the forced map-skeleton (`map=B(CB)(CB)`) is fully formed once a model has enough
capacity to crystallize, which happens well before the frontier.

### Caveats

Single family lineage (dense Qwen3) for the clean log-params regression — the
absolute binding values are not cross-architecture comparable (each model's own
frame), only the per-family *trend* within the lineage is. The 32B dip is a single
point (could be a depth-fraction mismatch at frac 0.40, n_layers=64). The gap
non-widening is robust to that (recursion tracks skeleton across all 5 points).

### s220 artifacts
`scripts/experiments/combinator_map_scale.py` (the scale instrument);
`results/combinator-map-consensus/scale.json` (per-model + fits); extended
`results/combinator-map-consensus/consensus.json` (10 models);
`results/combinator-relationship-map/Qwen_Qwen3-32B.{json,npz}`. Committed `c27741c`.

### Open leads from s220
1. **Construct the harvest fold** (register: topological/routing → functional) — now
   the priority: take the universal positive edges (B–D +0.175, B–C +0.168, K–C
   +0.133, S–D +0.161, S–Y +0.127), Procrustes-align consensus centroids into v15's
   base frame, WHNF-verify each vs main:1's contractive operator (Exp-B acceptance),
   measure downstream PPL vs base. Falsifiable: does verified ecosystem-consensus add
   beyond the universal crystal we already hold? Harvest from the 4–14B band.
2. **main:1 step_002000** → does Δx→ε and CE hold below 8.71 (adaptive halting).
3. Detect map/fold directions (s219 lead #3).

## Files

| File | Content |
|------|---------|
| `scripts/experiments/exp_b_self_verifying_acceptance.py` | Exp B core: perturb routing register, ΔCE vs Δ(Δx-at-convergence), self-verifying acceptance verdict |
| `tests/test_vsm_continuation.py` | 15 tensor-level property tests for the continuation (outer recurrence); fixed-point math exact |
| `scripts/experiments/tool_crystal_consensus.py` | per-model: routing register (gate sign) + CMR + within-model selectivity; saves probe-aligned RDM npz |
| `scripts/experiments/tool_crystal_consensus_summary.py` | cross-model agree / shuffled-null / length-partial / within-domain |
| `scripts/experiments/tool_crystal_control_baseline.py` | TOOL vs CTRL within-group agreement = the tool-specific-vs-generic verdict |
| `results/tool-crystal-consensus/` | per-model `{model}.json/.npz`, `consensus_summary.json`, `control_baseline.json` |
| `/tmp/tool_consensus_5fam.log` | 5-family run transcript |
| `scripts/experiments/combinator_map_consensus.py` | **s219 reverse-harvest:** cross-model combinator-Gram consensus + label-perm null + per-edge reliability_t + per-family binding vs random-triple null |
| `scripts/experiments/combinator_relationship_map.py` | per-model 9×9 combinator Gram in routing register (CMR); the per-model map reader |
| `results/combinator-map-consensus/consensus.json` | s219→s220 verdict: GramCorr +0.66→+0.782 (10 models); skeleton z_bind +2.31>recursion +1.68; harvest edge-list |
| `scripts/experiments/combinator_map_scale.py` | **s220 scale axis:** intra-family routing binding vs log(params) on the dense Qwen series (MoE excluded) |
| `results/combinator-map-consensus/scale.json` | s220 verdict: skeleton rises r=+0.78, skel-rec gap flat r=+0.36, saturates ~4-14B |
| `results/combinator-relationship-map/` | 10 per-model `{model}.json/.npz` (5 families, 410M→32B) |
| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript; `/tmp/combinator_scale.log` s220 32B; `/tmp/combinator_consensus_10models.log` s220 consensus |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/exp_b_self_verifying_acceptance.py"
}
```

**Summary:** Reading exp_b_self_verifying_acceptance.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: functional
"""Experiment B (core) — is the continuation a SELF-VERIFYING acceptance test?

THE DISTRIBUTED-TRAINING CLAIM (explore/consensus-delta-folding.md, s217):
  A working VSM continuation (the outer recurrence in v15model.py: shared sweep
  iterated, x_c fed back → β-reduction toward a fixed point / WHNF) should let
  distributed training ACCEPT or REJECT a donated delta WITHOUT trusted held-out
  labels — because the fixed point IS the target. A good delta should preserve /
  accelerate convergence (lower Δx-at-convergence); a bad delta should push the
  operator off its fixed point (raise Δx-at-convergence). If so:

      accept(delta)  ⟺  Δx-at-convergence does NOT rise

  is a label-free, Byzantine-robust acceptance rule (removes the audit-#7
  population-Goodhart risk: no shared calibration cache to overfit).

THE TEST (this script, gradient-free):
  Build the frozen continuation operator (V15Model + extracted base, n_outer=K).
  Perturb the ROUTING register (FFN gate delta plate) by flipping B random
  positions (a quality SPECTRUM via flip-count B = 1,2,4,...). For each candidate
  measure BOTH:
    ΔCE          = model._last_ce − CE0          (the TRUE quality label)
    Δ(Δx_conv)   = Δx_at_convergence − Δx0        (the SELF-VERIFYING signal)
  Then correlate. The hypothesis is corr(ΔCE, Δ(Δx_conv)) > 0: degrading the
  operator (raising CE) also raises the fixed-point residual. If yes, the
  continuation residual is a valid label-free acceptance signal.

  Δx_at_convergence = model._last_outer_deltas[-1] = ‖x_c^K − x_c^{K-1}‖/‖·‖
  (the last outer-recurrence relative step — 0 ⇒ exact fixed point / WHNF).

CAVEAT (register): on the FROZEN extracted base the operator is not yet trained
for contractivity (s214: naive K stays Δx~1.2). This is therefore a LOWER BOUND;
the clean test reruns on main:1's λ_fp-trained contractive checkpoint once it
lands. We report the baseline convergence curve so the regime is explicit.

Usage:
  uv run python scripts/experiments/exp_b_self_verifying_acceptance.py \
      --n-outer 6 --seqs 4 --seq-len 512 --reps 8

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_V15 = _PROJECT_ROOT / "scripts" / "v15"
sys.path.insert(0, str(_V15))

import mlx.core as mx  # noqa: E402
from config import V15Config  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402
from td_delta import (  # noqa: E402
    TernaryLinear,
    DeltaTernaryLinear,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    reduce_all_deltas,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "exp-b-self-verifying"
SHARD = Path.home() / "data" / "fractal-bitnet" / "shards-qwen36" / "shard_00000.npy"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def load_token_batch(seqs: int, seq_len: int, vocab: int, seed: int = 0):
    """A (seqs, seq_len+1) token window from the data shard → (tokens, targets)."""
    arr = np.load(str(SHARD), mmap_mode="r")
    rng = np.random.default_rng(seed)
    need = seq_len + 1
    starts = rng.integers(0, len(arr) - need, size=seqs)
    rows = np.stack([np.asarray(arr[s:s + need], dtype=np.int64) for s in starts])
    rows = np.clip(rows, 0, vocab - 1)
    tokens = mx.array(rows[:, :-1])
    targets = mx.array(rows[:, 1:])
    return tokens, targets


def forward_metrics(model, tokens, targets):
    """One forward at the configured n_outer → (CE, Δx_at_convergence, curve)."""
    model._prev_alg_c = None  # clean state, no cross-call algedonic drift
    _, _ = model(tokens, targets)
    mx.eval(model._last_ce)
    ce = float(model._last_ce.item())
    curve = [float(d.item()) for d in model._last_outer_deltas]
    dx_conv = curve[-1] if curve else float("nan")
    return ce, dx_conv, curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-outer", type=int, default=6)
    ap.add_argument("--seqs", type=int, default=4)
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--reps", type=int, default=8,
                    help="random position-sets per flip-count")
    ap.add_argument("--flip-fracs", type=str,
                    default="0.0003,0.001,0.003,0.01,0.03,0.1,0.3",
                    help="flip these FRACTIONS of the plate's positions (the quality spectrum)")
    ap.add_argument("--module-filter", type=str, default="ffn_gate",
                    help="substring to pick the target routing module(s)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--extracted-model-path", type=str,
                    default="checkpoints/v15-extracted/model.npz/model.npz",
                    help="frozen base (nested model.npz, as main:1 uses)")
    ap.add_argument("--checkpoint", type=str, default="",
                    help="optional TRAINED model.npz (non-chance CE) to load over the base")
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    flip_fracs = [float(x) for x in args.flip_fracs.split(",")]

    cfg = V15Config()
    if Path(args.extracted_model_path).exists():
        cfg.extracted_model_path = args.extracted_model_path
    log(f"building continuation operator (n_outer={args.n_outer}) ...")
    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
    if args.checkpoint and Path(args.checkpoint).exists():
        log(f"  loading TRAINED checkpoint: {args.checkpoint}")
        model.load_weights(args.checkpoint, strict=False)
        mx.eval(model.parameters())
        # fold trained delta routing into the base so deltas restart at +1;
        # perturbations are then correctly RELATIVE to the trained operator.
        n_reduced = reduce_all_deltas(model)
        log(f"  folded {n_reduced} trained delta plates into base (deltas → +1)")
        mx.eval(model.parameters())
    model._n_outer_passes = args.n_outer
    model._fixed_point_lambda = 0.0  # eval only
    mx.eval(model.parameters())

    tokens, targets = load_token_batch(args.seqs, args.seq_len, cfg.vocab_size, args.seed)
    log(f"batch: tokens {tokens.shape}  targets {targets.shape}")

    # ── baseline ──
    ce0, dx0, curve0 = forward_metrics(model, tokens, targets)
    log(f"baseline  CE={ce0:.4f}  Δx_conv={dx0:.4f}  curve={['%.3f'%c for c in curve0]}")

    # ── pick a target routing module that is ACTUALLY IN THE FORWARD PATH ──
    # INSTRUMENT GUARD (s218): convert_ffn ORPHANS the top-level ffn_*_plate_*
    # DeltaTernaryLinear copies — `convert_to_delta` setattr's the model attribute
    # but stack_{a,c} keep their original references, so the LIVE FFN plates are
    # stack_{a,c}.ffn_gate_plate (TernaryLinear). The prior run perturbed an orphan
    # ⇒ CE bit-identical across 1.97M flips ⇒ VOID. We now (1) enumerate candidate
    # ternary modules matching the filter, (2) KEEP only those whose signs actually
    # move CE, (3) ABORT if none. Perturbation = sign-flip of NONZERO ternary
    # positions (= the routing register; zeros stay zero).
    def _is_delta(m):
        return isinstance(m, DeltaTernaryLinear)

    def _orig_signs(m):
        return np.asarray(unpack_ternary_mlx(m.delta_weight if _is_delta(m) else m.weight))

    def _set_signs(m, arr_np):
        packed = pack_ternary_mlx(mx.array(arr_np.astype(np.int8)))
        if _is_delta(m):
            m.delta_weight = packed
        else:
            m.weight = packed
        mx.eval(packed)

    candidates = [(n, m) for (n, m) in model.named_modules()
                  if isinstance(m, (TernaryLinear, DeltaTernaryLinear))
                  and args.module_filter in n]
    if not candidates:
        raise SystemExit(f"no ternary module matches --module-filter={args.module_filter!r}")

    tgt_name = tgt_mod = base_signs = None
    for name, mod in candidates:
        signs = _orig_signs(mod)
        N_, K_ = signs.shape
        nz = np.flatnonzero(signs.reshape(-1) != 0)
        if nz.size == 0:
            continue
        gr = np.random.default_rng(args.seed).choice(nz, size=max(1, nz.size // 2), replace=False)
        probe = signs.copy().reshape(-1)
        probe[gr] *= -1
        _set_signs(mod, probe.reshape(N_, K_))
        ce_probe, _, _ = forward_metrics(model, tokens, targets)
        _set_signs(mod, signs)  # restore exactly
        moved = abs(ce_probe - ce0)
        log(f"  guard: {name:34} ({N_},{K_}) nz={nz.size:>9,}  flip-½nz ΔCE={ce_probe-ce0:+.4f}"
            f"  {'LIVE ✓' if moved > 1e-4 else 'DEAD ✗'}")
        if moved > 1e-4 and tgt_mod is None:
            tgt_name, tgt_mod, base_signs = name, mod, signs

    if tgt_mod is None:
        raise SystemExit("INSTRUMENT GUARD FAILED: no live routing module for "
                         f"--module-filter={args.module_filter!r} — perturbations do not reach "
                         "the forward. ABORT (the result would be VOID, cf. s217 phase-2 bug).")

    N, K = base_signs.shape
    nz_idx = np.flatnonzero(base_signs.reshape(-1) != 0)  # routing positions (nonzero signs)
    n_positions = int(nz_idx.size)
    log(f"▶ LIVE target routing module: {tgt_name}  shape=({N},{K})  "
        f"routing(nonzero)-positions={n_positions:,}")

    def apply_flip(flat_idx: np.ndarray):
        signs = base_signs.copy().reshape(-1)
        signs[flat_idx] *= -1  # flip sign of selected nonzero routing positions
        _set_signs(tgt_mod, signs.reshape(N, K))

    def reset_flip():
        _set_signs(tgt_mod, base_signs)

    rng = np.random.default_rng(args.seed + 1)
    records = []
    for frac in flip_fracs:
        B = max(1, int(frac * n_positions))
        for r in range(args.reps):
            sel = rng.choice(n_positions, size=min(B, n_positions), replace=False)
            idx = nz_idx[sel]  # map to absolute flat indices among routing positions
            apply_flip(idx)
            ce, dx, _ = forward_metrics(model, tokens, targets)
            reset_flip()
            records.append({
                "flip_frac": float(frac), "flip_count": int(B), "rep": int(r),
                "dCE": ce - ce0, "dDx": dx - dx0,
                "CE": ce, "Dx_conv": dx,
            })
        sub = [x for x in records if x["flip_frac"] == frac]
        log(f"  frac={frac:<7} (B={B:>7})  mean ΔCE={np.mean([x['dCE'] for x in sub]):+.4f}  "
            f"mean Δ(Δx_conv)={np.mean([x['dDx'] for x in sub]):+.5f}")

    # ── analysis ──
    dCE = np.array([x["dCE"] for x in records])
    dDx = np.array([x["dDx"] for x in records])
    finite = np.isfinite(dCE) & np.isfinite(dDx)
    dCE, dDx = dCE[finite], dDx[finite]

    def pearson(a, b):
        if a.std() < 1e-12 or b.std() < 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    def spearman(a, b):
        ra = np.argsort(np.argsort(a))
        rb = np.argsort(np.argsort(b))
        return pearson(ra.astype(float), rb.astype(float))

    pear = pearson(dCE, dDx)
    spear = spearman(dCE, dDx)

    # acceptance ROC: does "Δ(Δx_conv) > 0" predict "ΔCE > 0" (a degrading delta)?
    pred_bad = dDx > 0
    true_bad = dCE > 0
    tp = int(np.sum(pred_bad & true_bad))
    tn = int(np.sum(~pred_bad & ~true_bad))
    fp = int(np.sum(pred_bad & ~true_bad))
    fn = int(np.sum(~pred_bad & true_bad))
    acc = (tp + tn) / max(len(dCE), 1)
    # also: of accepted (Δx not raised) deltas, what fraction actually improved/held CE?
    accepted = ~pred_bad
    accept_good_rate = (float(np.mean(~true_bad[accepted])) if accepted.any() else float("nan"))

    verdict = ("SELF-VERIFYING SIGNAL PRESENT" if spear > 0.3 and pear > 0.3
               else "WEAK (partial signal)" if spear > 0.1
               else "NO SIGNAL on this base")

    out = {
        "register": "functional",
        "model": (f"v15 trained base ({args.checkpoint})" if args.checkpoint
                  else "v15 extracted base (frozen)"),
        "perturbation": "sign-flip of nonzero routing positions (live FFN gate plate)",
        "live_guard": "passed",
        "n_outer": args.n_outer, "target_module": tgt_name,
        "module_shape": [int(N), int(K)], "n_positions": int(n_positions),
        "batch": {"seqs": args.seqs, "seq_len": args.seq_len},
        "baseline": {"CE": ce0, "Dx_conv": dx0, "curve": curve0},
        "n_candidates": int(len(records)), "flip_fracs": flip_fracs,
        "pearson_dCE_dDx": pear, "spearman_dCE_dDx": spear,
        "acceptance_roc": {"tp": tp, "tn": tn, "fp": fp, "fn": fn,
                           "accuracy": acc, "accept_good_rate": accept_good_rate},
        "verdict": verdict,
        "per_flipfrac": {
            str(frac): {
                "mean_dCE": float(np.mean([x["dCE"] for x in records if x["flip_frac"] == frac])),
                "mean_dDx": float(np.mean([x["dDx"] for x in records if x["flip_frac"] == frac])),
            } for frac in flip_fracs},
        "records": records,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / "result.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  ════════ SELF-VERIFYING ACCEPTANCE — VERDICT ════════")
    log(f"  baseline convergence curve: {['%.3f' % c for c in curve0]}  (→0 = WHNF)")
    log(f"  candidates: {len(records)}  (flip-count spectrum × {args.reps} reps)")
    log(f"  corr(ΔCE, Δ(Δx_conv))   Pearson={pear:+.3f}  Spearman={spear:+.3f}")
    log(f"  acceptance rule 'reject if Δx_conv rises': accuracy={acc:.3f} "
        f"(predict degrade), accepted-and-good={accept_good_rate:.3f}")
    log(f"  ▶ {verdict}")
    log(f"  wrote result.json  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

## Assistant

Excellent — the knowledge page is comprehensive. Now read the td_delta.py and v15model files to understand the fold plumbing:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/scripts/v15/"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 0
Stdout:
__init__.py
__pycache__
apply_zeros.py
attention.py
build_student_trace_basis.py
build_trace_basis.py
components.py
config.py
crystal_base.py
crystal.py
data.py
diagnose_pipeline.py
etch.py
eval_prompts.txt
extract_qwen36.py
extract.py
generate.py
kernel.py
load_checkpoint.py
model.py
neuron_modes.py
prepare_etch.py
scan.py
stack_vsm.py
td_delta.py
td.py
ternary.py
train_td.py
train.py
v15model.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/step_001000/"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/chec...

**Output:**
```
Exit code: 0
Stdout:
delta_plates.npz
model.npz
optimizer.npz
state.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('results/combinator-relationship-map/Qwen_Qwen3-14B.json') as f:\n    d = json.load(f)\nm = d.get('map', {})\nprint('map keys:', list(m.keys()))\nfor k,v in m.items():\n    if isinstance(v, list):\n        if v and isinstance(v[0], list):\n            print(f'  map.{k}: list of lists, shape ~{len(v)}x{len(v[0]) if v[0] else 0}')\n        else:\n            print(f'  map.{k}: list len={len(v)}, elem_type={type(v[0]).__name__ if v else \\\"empty\\\"}')\n    else:\n        print(f'  map.{k}: {type(v).__name__} = {str(v)[:80]}')\n# also check per_layer\npl = d.get('per_layer', {})\nfirst_layer = list(pl.keys())[0] if pl else None\nif first_layer:\n    layer_keys = list(pl[first_layer].keys())\n    print('per_layer first layer keys:', layer_keys)\n    for k in layer_keys:\n        v = pl[first_layer][k]\n        if isinstance(v, list):\n            if v and isinstance(v[0], list):\n                print(f'  per_layer[{first_layer}].{k}: {len(v)}x{len(v[0])}')\n            else:\n                print(f'  per_layer[{first_layer}].{k}: list len={len(v)}')\n        else:\n            print(f'  per_layer[{first_layer}].{k}: {v}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
map keys: ['layer', 'frac', 'gram', 'mds_coords', 'pca_coords', 'nearest']
  map.layer: int = 12
  map.frac: float = 0.308
  map.gram: dict = {'K': {'K': 1.0, 'I': 0.0446, 'B': -0.1505, 'C': 0.0671, 'S': -0.2352, 'D': -0.3
  map.mds_coords: dict = {'K': [-0.1146, 0.5654], 'I': [-0.2568, 0.4624], 'B': [0.5954, 0.0025], 'C': [0.
  map.pca_coords: dict = {'K': [-0.1832, 0.6379], 'I': [-0.3347, 0.4956], 'B': [0.6797, 0.0546], 'C': [0.
  map.nearest: dict = {'K': [['C', 0.06705819070339203], ['I', 0.044579342007637024], ['WHNF', -0.1116
per_layer first layer keys: ['frac', 'd_ff', 'route_full_silhouette', 'route_cmr_silhouette']
  per_layer[0].frac: 0.0
  per_layer[0].d_ff: 17408
  per_layer[0].route_full_silhouette: {'silhouette': 0.015464107577400658, 'null_mean': 0.006392458865320175, 'null_std': 0.0015088090046423554, 'z': 6.012456635775981, 'p_value': 0.000999000999000999}
  per_layer[0].route_cmr_silhouette: {'silhouette': 0.03901829543918982, 'null_mean': 0.020958929272039028, 'null_std': 0.007301796486624476, 'z': 2.4732771175192525, 'p_value': 0.000999000999000999}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"reduce_all_deltas\\|collect_delta_params\\|convert_to_delta\\|fold\\|DeltaTernaryLinear\\|TernaryLinear\\|pack_ternary\\|unpack_ternary\" /Users/mwhitford/src/verbum/scripts/v15/td_delta.py | head -60"
}
```

**Summary:** $ grep -n "reduce_all_deltas\|collect...

**Output:**
```
Exit code: 0
Stdout:
38:    Reduction: fold delta into base, reset delta to +1, iterate.
55:        TernaryLinear,
59:        pack_ternary_mlx,
60:        unpack_ternary_mlx,
66:        TernaryLinear,
70:        pack_ternary_mlx,
71:        unpack_ternary_mlx,
821:            delta_unpacked = unpack_ternary_mlx(delta_packed)
822:            base_unpacked = unpack_ternary_mlx(base_packed)
1085:                new_packed = pack_ternary_mlx(new_delta)
1160:        Called after reduction (delta folded into base) or other events
1171:        """Reset all state. Called after reduction (delta folded into base)."""
1181:# DeltaTernaryLinear — base plate + delta plate architecture
1185:class DeltaTernaryLinear(nn.Module):
1193:    TernaryDescent.  When delta converges, reduce() folds it into
1201:    Gamma is trained by Adam (same as TernaryLinear).
1210:    after training, reduce() folds delta into base and the model
1211:    becomes a standard TernaryLinear.  During training, the overhead
1239:        self.delta_weight = pack_ternary_mlx(ones)  # (N, K//16) uint32 — trained by TD
1242:    def from_ternary_linear(cls, tl: TernaryLinear) -> "DeltaTernaryLinear":
1243:        """Convert an existing TernaryLinear to DeltaTernaryLinear.
1245:        The TernaryLinear's weight becomes the frozen base plate.
1265:        dtl.delta_weight = pack_ternary_mlx(ones)
1279:        base = unpack_ternary_mlx(self.base_weight)    # (N, K) int8
1280:        delta = unpack_ternary_mlx(self.delta_weight)   # (N, K) int8
1286:        return pack_ternary_mlx(effective)
1289:        """Compute quantized_matmul scales/biases from gamma (same as TernaryLinear)."""
1301:        # Cache input statistics (same as TernaryLinear)
1370:        base = unpack_ternary_mlx(self.base_weight).astype(mx.float32)  # (N, K)
1385:        # Compute folded base
1390:        new_delta_packed = pack_ternary_mlx(ones)
1397:    def to_ternary_linear(self) -> TernaryLinear:
1398:        """Convert back to standard TernaryLinear after training.
1400:        Folds delta into base first, then creates a TernaryLinear
1403:        self.reduce()  # ensure delta is folded
1405:        tl = TernaryLinear.__new__(TernaryLinear)
1418:        delta = unpack_ternary_mlx(self.delta_weight)  # (N, K) int8
1431:        """Report effective plate statistics (same interface as TernaryLinear)."""
1433:        w = unpack_ternary_mlx(effective)
1449:def convert_to_delta(
1453:) -> list[tuple[str, DeltaTernaryLinear]]:
1454:    """Convert TernaryLinear modules to DeltaTernaryLinear in-place.
1456:    Walks the model tree.  For each TernaryLinear matching the
1457:    include/exclude filters, replaces it with a DeltaTernaryLinear
1468:        List of (path, DeltaTernaryLinear) for all converted modules.
1473:        if not isinstance(mod, TernaryLinear):
1485:        dtl = DeltaTernaryLinear.from_ternary_linear(mod)
1507:def collect_delta_params(
1509:) -> list[tuple[str, DeltaTernaryLinear]]:
1510:    """Collect all DeltaTernaryLinear modules from the model.
1524:        if isinstance(mod, DeltaTernaryLinear):
1538:def reduce_all_deltas(model: nn.Module) -> int:
1539:    """Reduce all DeltaTernaryLinear modules: fold delta into base.
1545:        if isinstance(mod, DeltaTernaryLinear):
1563:        if isinstance(mod, DeltaTernaryLinear):
1575:    print("TernaryDescent + DeltaTernaryLinear self-test")
1578:    # 1. Test DeltaTernaryLinear matches TernaryLinear at init
1579:    print("\n1. DeltaTernaryLinear vs TernaryLinear (delta=+1 should match)...")
1581:    tl = TernaryLinear(64, 32, pre_norm=False)
1582:    dtl = DeltaTernaryLinear.from_ternary_linear(tl)
```

## Assistant

Critical: the JSON contains `mds_coords` and `pca_coords` — these are 2D embedding coordinates. Let me check these more carefully and read the combinator_relationship_map.py script, plus the v15model and reduce_all_deltas code:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/td_delta.py",
  "line_offset": 1181,
  "limit": 80
}
```

**Summary:** Reading td_delta.py (1181-1261)

**Output:**
```
# ══════════════════════════════════════════════════════════════════════


class DeltaTernaryLinear(nn.Module):
    """Linear layer with frozen base plate + trainable delta plate.

    effective = base ⊙ delta   (element-wise ternary multiply)
    output = quantized_matmul(x, effective, gamma_scales, gamma_biases)

    The base plate contains the full teacher crystal etch, frozen.
    The delta plate starts at +1 (pass-through) and is trained by
    TernaryDescent.  When delta converges, reduce() folds it into
    the base and resets delta to +1 for another round.

    Delta semantics:
        +1 → keep teacher sign (this crystal position works)
        -1 → flip teacher sign (stride-stack needs different routing)
         0 → block this position (staging area during transition)

    Gamma is trained by Adam (same as TernaryLinear).

    Forward path:
        1. Unpack base and delta
        2. Multiply element-wise: effective = base * delta
        3. Repack effective
        4. quantized_matmul(norm(x), effective_packed, scales, biases)

    The unpack-multiply-repack is NOT in the hot path of inference —
    after training, reduce() folds delta into base and the model
    becomes a standard TernaryLinear.  During training, the overhead
    is small relative to the matmul.
    """

    group_size: int = 64
    bits: int = 2

    def __init__(
        self,
        in_features: int,
        out_features: int,
        pre_norm: bool = True,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.pre_norm = pre_norm

        if pre_norm:
            self.norm = nn.RMSNorm(in_features)

        # Base plate: will be loaded from teacher etch. Init random for now.
        wq_uint32, gamma = _ternary_init(out_features, in_features)
        self.base_weight = wq_uint32    # (N, K//16) uint32 — FROZEN
        self.gamma = gamma              # (N,) float32 — trained by Adam

        # Delta plate: starts as all +1 (pass-through)
        ones = mx.ones((out_features, in_features), dtype=mx.int8)
        self.delta_weight = pack_ternary_mlx(ones)  # (N, K//16) uint32 — trained by TD

    @classmethod
    def from_ternary_linear(cls, tl: TernaryLinear) -> "DeltaTernaryLinear":
        """Convert an existing TernaryLinear to DeltaTernaryLinear.

        The TernaryLinear's weight becomes the frozen base plate.
        Delta is initialized to all +1 (pass-through).
        Gamma transfers directly.
        """
        dtl = cls.__new__(cls)
        nn.Module.__init__(dtl)

        dtl.in_features = tl.in_features
        dtl.out_features = tl.out_features
        dtl.pre_norm = tl.pre_norm

        if tl.pre_norm:
            dtl.norm = tl.norm  # share the norm layer

        # Base plate from existing weights
        dtl.base_weight = tl.weight  # FROZEN
        dtl.gamma = tl.gamma         # trained by Adam

[CONTENT TRUNCATED] Showing lines 1182 to 1261 of 1832 total lines. Use line_offset=1261 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/td_delta.py",
  "line_offset": 1360,
  "limit": 80
}
```

**Summary:** Reading td_delta.py (1360-1440)

**Output:**
```

        # ∂L/∂effective[i,j] ≈ ∂L/∂y[i] × x[j] × gamma[i]
        # Shape: (out,) × (in,) → (out, in) via outer product
        grad_effective = (
            mx.expand_dims(grad_out_mean * self.gamma, axis=-1)
            * mx.expand_dims(x_mean, axis=0)
        )  # (out_features, in_features)

        # ∂L/∂delta = ∂L/∂effective × base
        base = unpack_ternary_mlx(self.base_weight).astype(mx.float32)  # (N, K)
        grad_delta = grad_effective * base

        return grad_delta

    def reduce(self) -> None:
        """Fold delta into base plate. Reset delta to all +1.

        new_base = base ⊙ delta  (ternary × ternary = ternary, exact)
        new_delta = all +1

        This is lossless: the effective plate is unchanged.
        Called when delta has converged (most positions still +1).
        After reduction, TernaryDescent state should also be reset.
        """
        # Compute folded base
        new_base_packed = self._compute_effective()

        # Reset delta to all +1
        ones = mx.ones((self.out_features, self.in_features), dtype=mx.int8)
        new_delta_packed = pack_ternary_mlx(ones)

        # Assign
        self.base_weight = new_base_packed
        self.delta_weight = new_delta_packed
        mx.eval(self.base_weight, self.delta_weight)

    def to_ternary_linear(self) -> TernaryLinear:
        """Convert back to standard TernaryLinear after training.

        Folds delta into base first, then creates a TernaryLinear
        with the effective weights. Use for inference (no delta overhead).
        """
        self.reduce()  # ensure delta is folded

        tl = TernaryLinear.__new__(TernaryLinear)
        nn.Module.__init__(tl)
        tl.in_features = self.in_features
        tl.out_features = self.out_features
        tl.pre_norm = self.pre_norm
        if self.pre_norm:
            tl.norm = self.norm
        tl.weight = self.base_weight  # delta is all +1, so base IS effective
        tl.gamma = self.gamma
        return tl

    def delta_stats(self) -> dict[str, float]:
        """Report delta plate statistics."""
        delta = unpack_ternary_mlx(self.delta_weight)  # (N, K) int8
        total = delta.size
        n_keep = int((delta == 1).sum().item())
        n_flip = int((delta == -1).sum().item())
        n_block = int((delta == 0).sum().item())
        return {
            "keep_frac": n_keep / total,       # +1: using teacher sign
            "flip_frac": n_flip / total,       # -1: flipped from teacher
            "block_frac": n_block / total,     #  0: blocked (staging)
            "changed_frac": (n_flip + n_block) / total,  # anything not +1
        }

    def ternary_stats(self) -> dict[str, float]:
        """Report effective plate statistics (same interface as TernaryLinear)."""
        effective = self._compute_effective()
        w = unpack_ternary_mlx(effective)
        total = w.size
        return {
            "sparsity": float((w == 0).sum().item()) / total,
            "pos_frac": float((w == 1).sum().item()) / total,
            "neg_frac": float((w == -1).sum().item()) / total,
            "gamma_mean": float(self.gamma.mean().item()),
            "gamma_std": float(mx.sqrt(mx.var(self.gamma)).item()),

[CONTENT TRUNCATED] Showing lines 1361 to 1440 of 1832 total lines. Use line_offset=1440 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/td_delta.py",
  "line_offset": 1538,
  "limit": 40
}
```

**Summary:** Reading td_delta.py (1538-1578)

**Output:**
```
    """Reduce all DeltaTernaryLinear modules: fold delta into base.

    Returns number of modules reduced.
    """
    n = 0
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            mod.reduce()
            n += 1
    return n


def freeze_delta_architecture(model: nn.Module) -> int:
    """Freeze base plates and delta plates for optimizer exclusion.

    base_weight: always frozen (teacher crystal)
    delta_weight: frozen from Adam (TD manages it directly)
    gamma: NOT frozen (Adam trains it)
    norm: NOT frozen (Adam trains it)

    Returns number of modules frozen.
    """
    n = 0
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            mod.freeze(keys=["base_weight", "delta_weight"])
            n += 1
    return n


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TernaryDescent + DeltaTernaryLinear self-test")
    print("=" * 60)

    # 1. Test DeltaTernaryLinear matches TernaryLinear at init

[CONTENT TRUNCATED] Showing lines 1539 to 1578 of 1832 total lines. Use line_offset=1578 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"combinator_relationship_map\\|HuggingFace\\|AutoModel\\|from_pretrained\\|model_name\\|args.model\\|load_model\\|extract\\|v15\\|checkpoint\\|local\" /Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py | head -50"
}
```

**Summary:** $ grep -n "combinator_relationship_ma...

**Output:**
```
Exit code: 0
Stdout:
39:  uv run python scripts/experiments/combinator_relationship_map.py \
58:from transformers import AutoModelForCausalLM, AutoTokenizer
250:    safe = args.model.replace("/", "_")
255:    log(f"[{args.model}] {len(prompts)} crystal probes  {counts}")
259:    tok = AutoTokenizer.from_pretrained(args.model)
260:    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
277:    out = {"model": args.model, "dtype": args.dtype, "register": "topological/routing",
354:    log(f"  === {args.model} combinator relationship map ===")
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"_last_outer_deltas\\|_n_outer_passes\\|_last_ce\\|n_outer\\|fixed_point\\|algedonic\\|outer_loop\\|WHNF\\|convergence\\|Δx\\|delta_x\" /Users/mwhitford/src/verbum/scripts/v15/v15model.py | head -40"
}
```

**Summary:** $ grep -n "_last_outer_deltas\|_n_out...

**Output:**
```
Exit code: 0
Stdout:
5:LaplacianCrystalLoss replaces v14 CrystalLoss (WHNF gets 5× weight).
9:    S4: intelligence (global algedonic pattern detection)
24:  - LaplacianCrystalLoss (WHNF fragility weighting) vs uniform CrystalLoss
117:    Key change from v14: LaplacianCrystalLoss gives WHNF 5× the
118:    gradient weight — fixing the session 189 WHNF un-settlement.
204:        # ── Cached algedonics (one step back) ──────────────────
233:        # WHNF anti-correlation (WHNF is most fragile in v15 — Laplacian-weighted)
297:        # ── Bottom-up algedonic from previous step ─────────────
305:        # shared VSM sweep n_outer times, feeding x_c back as the next input.
307:        # point (WHNF). n_outer=1 is identical to the single-sweep baseline.
308:        # _last_outer_deltas records ‖x_c^{(k)} − x_c^{(k-1)}‖/‖x_c^{(k-1)}‖ —
309:        # the fixed-point convergence curve (shrinking ⇒ contractive ⇒ free depth).
310:        n_outer = int(getattr(self, "_n_outer_passes", 1))
313:        outer_deltas = []   # stop-grad relative Δx (logging / fixed-point curve)
314:        fp_terms = []       # DIFFERENTIABLE squared relative Δx (contractivity loss)
315:        for _k in range(n_outer):
325:                # stored crystal pattern (WHNF). Target detached so the gradient
334:        self._last_outer_deltas = outer_deltas
336:        # Aggregate the differentiable fixed-point term (None when n_outer<2).
356:        # ── Cache algedonics for next step ─────────────────────
359:        # ── Laplacian crystal loss (v15: WHNF gets 5× weight) ──
415:            # with outer recurrence (n_outer≥2) and λ_fp>0.
416:            lambda_fp = float(getattr(self, "_fixed_point_lambda", 0.0))
442:        self._last_ce = mx.stop_gradient(ce_loss)
539:    print(f"  CE: {model._last_ce.item():.4f}")
548:    print("\nSecond forward (tests C→A algedonic + S5 state)...")
552:    print(f"  loss: {loss3.item():.4f} (with C→A algedonic) ✓")
```

## Assistant

Now I need to check the mds_coords/pca_coords nature (are they full-dim centroids or just 2D projections), and see the combinator_relationship_map.py logic that produces them:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py"
}
```

**Summary:** Reading combinator_relationship_map.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Combinator relationship map — what is the SHAPE of the function space?

THE QUESTION (session 217, Michael):
  We have found "function-like things" = the combinator basis
  (K I B C S D W Y WHNF). What are their SEMANTIC RELATIONSHIPS? Is there a
  map/fold? What do the functions look like — what is their shape?

THE INSTRUMENT (this script):
  Measure each combinator's CENTROID in the ROUTING register and build the
  pairwise relationship (Gram) matrix = the literal "map of the functions".

    routing(x) = sign( FFN gate pre-activation )        (s203: gate_proj sign
                                                          carries routing topology)
    centroid_k = mean over probes labelled k of routing(x), AFTER common-mode
                 removal (subtract the per-feature mean across all probes — kills
                 the universal structured-language crystal so the DIFFERENCES
                 between combinators show, not their shared backbone).
    Gram[j,k]  = cosine(centroid_j, centroid_k)          <- THE MAP

  Why this register: in RAW cosine the crystal is a rank-~1 common mode
  (5d-crystal-lattice REFUTED, s211); the combinator structure lives in the
  sign/routing register after CMR (separation p=5e-4, ~65% topological). So the
  shape of the function space is only visible here.

  Controls:
    - hidden_full / hidden_cmr : raw residual register (expect the common-mode mush)
    - route_full               : routing without CMR (common mode still present)
    - route_cmr                : routing with CMR        <-- KEY (the real map)
    - shuffled-label null       : permute combinator labels, recompute silhouette
                                  -> is the clustering real?

  Outputs per layer-fraction + a best layer chosen by silhouette z. Classical
  MDS + centroid-PCA give the 2D embedding (the picture). Cross combinator
  Gram, silhouette, null, and embedding all saved.

Usage:
  uv run python scripts/experiments/combinator_relationship_map.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.library import crystal_probes  # noqa: E402

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"

# the 9 crystal combinators, in a fixed canonical order
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]

# depth-normalized layer fractions (align models of different depth)
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- probes -----------------------------------------------------------------
def load_probes(limit_per: int = 0, seed: int = 0):
    """All crystal probes (K I B C S D W Y WHNF), grouped order preserved.
    limit_per: optionally cap probes per combinator (for smoke tests)."""
    probes = crystal_probes()
    by = {c: [] for c in CRYSTAL}
    for p in probes:
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    rng = np.random.default_rng(seed)
    prompts, labels = [], []
    for c in CRYSTAL:
        ps = by[c]
        if limit_per and limit_per < len(ps):
            idx = sorted(rng.permutation(len(ps))[:limit_per])
            ps = [ps[i] for i in idx]
        prompts.extend(ps)
        labels.extend([c] * len(ps))
    return prompts, np.array(labels)


# ---- model introspection ----------------------------------------------------
def find_gate_modules(model):
    hits = []
    pat = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod, m.group(2)))
    hits.sort(key=lambda x: x[0])
    return [(li, name, mod) for (li, name, mod, k) in hits]


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


# ---- capture ----------------------------------------------------------------
@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length, want_layers):
    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]

    n = len(prompts)
    hidden = None
    gate = {li: None for li in want}
    plen = np.empty(n, np.int32)
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True,
                            max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True)
            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
            if hidden is None:
                hidden = np.empty((n, h.shape[0]), np.float32)
            hidden[i] = h
            plen[i] = int(enc["input_ids"].shape[1])
            for li in want:
                g = buf[li]
                if gate[li] is None:
                    gate[li] = np.empty((n, g.shape[0]), np.float32)
                gate[li][i] = g
            del out
            if (i + 1) % 50 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return hidden, gate, plen, n_layers


# ---- centroid / Gram / silhouette -------------------------------------------
def cmr(X):
    """Common-mode removal: subtract per-feature mean across probes."""
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def centroids(X, labels):
    """Per-combinator mean vector. Returns [K x d] in CRYSTAL order."""
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        C[j] = X[m].mean(axis=0)
    return C


def gram(C):
    """Cosine Gram matrix between centroids."""
    U = np.array([unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def silhouette(X, labels):
    """Mean over probes of [cos(x, own centroid) - max_other cos(x, centroid)].
    Centroids computed leave-one-combinator-balanced (all probes; bias small at
    n>=50). High -> combinators are real clusters in this register."""
    C = centroids(X, labels)
    U = np.array([unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T                       # [N x K]
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    best_other = other.max(axis=1)
    return float(np.mean(own - best_other))


def silhouette_null(X, labels, n_perm=1000, seed=0):
    obs = silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = silhouette(X, rng.permutation(labels))
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def classical_mds(D, k=2):
    """Classical (Torgerson) MDS from a distance matrix -> [n x k] coords."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    w, V = w[order][:k], V[:, order][:, :k]
    w = np.clip(w, 0, None)
    return V * np.sqrt(w + 1e-30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--limit-per", type=int, default=0,
                    help="cap probes per combinator (smoke test)")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    prompts, labels = load_probes(args.limit_per, args.seed)
    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}
    log(f"[{args.model}] {len(prompts)} crystal probes  {counts}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers; capturing layers {want_layers}")

    log("  forward passes ...")
    hidden, gate, plen, n_layers = collect(
        model, tok, args.device, prompts, args.max_length, want_layers)
    width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    out = {"model": args.model, "dtype": args.dtype, "register": "topological/routing",
           "n_probes": len(prompts), "counts": counts, "hidden_width": width,
           "n_layers": n_layers, "want_layers": want_layers, "crystal_order": CRYSTAL,
           "n_perm": args.n_perm, "git_sha": git_sha(), "per_layer": {}}

    store = {"labels": labels}

    # control register: final residual (expect common-mode mush)
    out["hidden_full_silhouette"] = silhouette_null(
        hidden, labels, args.n_perm, args.seed)
    out["hidden_cmr_silhouette"] = silhouette_null(
        cmr(hidden), labels, args.n_perm, args.seed)
    store["gram_hidden_cmr"] = gram(centroids(cmr(hidden), labels)).astype(np.float32)

    log("  routing register per layer (sign(gate), raw + CMR) ...")
    for li in want_layers:
        sign = np.sign(gate[li])
        sign_cmr = cmr(sign)
        sil_full = silhouette_null(sign, labels, args.n_perm, args.seed)
        sil_cmr = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)
        G_cmr = gram(centroids(sign_cmr, labels))
        store[f"gram_route_cmr_L{li:02d}"] = G_cmr.astype(np.float32)
        out["per_layer"][str(li)] = {
            "frac": round(li / max(n_layers - 1, 1), 3),
            "d_ff": int(gate[li].shape[1]),
            "route_full_silhouette": sil_full,
            "route_cmr_silhouette": sil_cmr,
        }
        log(f"    L{li:02d} (f={li/max(n_layers-1,1):.2f}) "
            f"route_cmr silhouette={sil_cmr['silhouette']:+.4f} "
            f"z={sil_cmr['z']:+.2f} p={sil_cmr['p_value']:.4f}")

    # best routing layer by CMR silhouette z
    best_li = max(want_layers,
                  key=lambda li: out["per_layer"][str(li)]["route_cmr_silhouette"]["z"])
    out["best_routing_layer"] = int(best_li)
    best_frac = round(best_li / max(n_layers - 1, 1), 3)
    out["best_routing_frac"] = best_frac

    # the MAP at the best layer: Gram, MDS, centroid-PCA
    G = store[f"gram_route_cmr_L{best_li:02d}"].astype(np.float64)
    D = 1.0 - G
    np.fill_diagonal(D, 0.0)
    mds = classical_mds(D, k=2)
    Cb = centroids(cmr(np.sign(gate[best_li])), labels)
    Uc = np.array([unit(c) for c in Cb])
    # centroid PCA (2D)
    Ucc = Uc - Uc.mean(axis=0, keepdims=True)
    _, _, Vt = np.linalg.svd(Ucc, full_matrices=False)
    pca = Ucc @ Vt[:2].T

    out["map"] = {
        "layer": int(best_li), "frac": best_frac,
        "gram": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)
                              for j in range(len(CRYSTAL))}
                 for i in range(len(CRYSTAL))},
        "mds_coords": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),
                                    round(float(mds[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
        "pca_coords": {CRYSTAL[i]: [round(float(pca[i, 0]), 4),
                                    round(float(pca[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
    }
    # nearest neighbour per combinator (off-diagonal max cosine)
    nn = {}
    for i, c in enumerate(CRYSTAL):
        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]
        row.sort(key=lambda x: -x[1])
        nn[c] = row[:3]
    out["map"]["nearest"] = nn
    out["elapsed_s"] = round(time.time() - t0, 1)

    np.savez_compressed(RESULTS_DIR / f"{safe}.npz", prompt_len=plen, **store)
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    # ---- readable summary ----
    log("")
    log(f"  === {args.model} combinator relationship map ===")
    log(f"  register: routing (sign gate) + CMR; best layer L{best_li} (f={best_frac})")
    hf = out["hidden_full_silhouette"]
    rc = out["per_layer"][str(best_li)]["route_cmr_silhouette"]
    log(f"  hidden_full silhouette {hf['silhouette']:+.4f} z={hf['z']:+.2f} "
        f"(control: the common-mode register)")
    log(f"  route_cmr   silhouette {rc['silhouette']:+.4f} z={rc['z']:+.2f} "
        f"p={rc['p_value']:.4f}   <-- combinators as clusters")
    log("")
    log("  Gram (cosine) matrix — the MAP:")
    header = "        " + " ".join(f"{c:>6}" for c in CRYSTAL)
    log(header)
    for i, c in enumerate(CRYSTAL):
        row = " ".join(f"{G[i, j]:+.2f}".rjust(6) for j in range(len(CRYSTAL)))
        log(f"  {c:>5} {row}")
    log("")
    log("  nearest neighbours (top routing-cosine):")
    for c in CRYSTAL:
        ns = ", ".join(f"{n}({s:+.2f})" for n, s in nn[c])
        log(f"    {c:>5} -> {ns}")
    log("")
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

## Assistant

Now I have everything I need. Let me do a few final checks on the v15 checkpoint content and the fold_delta.py for reference:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\n# Check what's in the v15 step_001000 checkpoint\nd = np.load('checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz')\nkeys = list(d.keys())\nprint(f'model.npz keys ({len(keys)} total):')\nfor k in keys[:30]:\n    print(f'  {k}: shape={d[k].shape}, dtype={d[k].dtype}')\nif len(keys) > 30:\n    print(f'  ... and {len(keys)-30} more')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np # C...

**Output:**
```
Exit code: 0
Stdout:
model.npz keys (529 total):
  output_norm.weight: shape=(1280,), dtype=float32
  fire_alarm.alarm_proj.bias: shape=(1,), dtype=float32
  s2_anti_osc.s4_to_dampening.bias: shape=(1,), dtype=float32
  s2_anti_osc.s4_to_dampening.weight: shape=(1, 128), dtype=float32
  s2_anti_osc.d_gain: shape=(1,), dtype=float32
  s4.proposal_proj.weight: shape=(4, 128), dtype=float32
  s4.pattern_proj.bias: shape=(128,), dtype=float32
  s4.pattern_proj.weight: shape=(128, 192), dtype=float32
  s5_identity.proposal_impact.weight: shape=(1, 132), dtype=float32
  s5_identity.regulation_proj.weight: shape=(4, 128), dtype=float32
  s5_identity.update_candidate.bias: shape=(128,), dtype=float32
  s5_identity.update_gate.weight: shape=(128, 256), dtype=float32
  s5_identity.coherence_read.bias: shape=(128,), dtype=float32
  s5_identity.coherence_read.weight: shape=(128, 80), dtype=float32
  alg_combiner_a.combine_proj.bias: shape=(32,), dtype=float32
  alg_combiner_a.combine_proj.weight: shape=(32, 32), dtype=float32
  stack_c.alg_to_gate.bias: shape=(1,), dtype=float32
  stack_c.alg_to_gate.weight: shape=(1, 32), dtype=float32
  stack_c.alg_to_ffn.bias: shape=(1,), dtype=float32
  stack_c.alg_to_ffn.weight: shape=(1, 32), dtype=float32
  stack_c.alg_summary_proj.weight: shape=(32, 32), dtype=float32
  stack_c.algedonic.alarm_proj.gamma: shape=(16,), dtype=float32
  stack_c.s2.scales.2: shape=(1,), dtype=float32
  stack_c.s2.scales.1: shape=(1,), dtype=float32
  stack_c.s2.dir_projs.2.gamma: shape=(1280,), dtype=float32
  stack_c.s2.dir_projs.2.weight: shape=(1280, 80), dtype=uint32
  stack_c.s2.dir_projs.1.gamma: shape=(1280,), dtype=float32
  stack_c.s2.dir_projs.1.weight: shape=(1280, 80), dtype=uint32
  stack_c.s2.dir_projs.0.norm.weight: shape=(1280,), dtype=float32
  stack_c.s3_gates.3.learned_bias: shape=(1,), dtype=float32
  ... and 499 more
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\n# Check the delta_plates.npz  \nd = np.load('checkpoints/v15-td-outer-k2-fp5-5k/step_001000/delta_plates.npz')\nkeys = list(d.keys())\nprint(f'delta_plates.npz keys ({len(keys)} total):')\nfor k in keys[:20]:\n    print(f'  {k}: shape={d[k].shape}, dtype={d[k].dtype}')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np # C...

**Output:**
```
Exit code: 0
Stdout:
delta_plates.npz keys (152 total):
  shared_stride_stack_layers_0_q_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_0_k_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_0_k_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_0_v_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_0_q_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_0_out_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_1_q_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_1_k_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_1_v_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_1_out_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_1_out_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_2_q_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_2_k_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_2_v_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_2_v_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_1_q_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_2_out_proj_stats: shape=(4,), dtype=float32
  shared_stride_stack_layers_2_out_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_3_q_proj_delta_packed: shape=(1280, 80), dtype=uint32
  shared_stride_stack_layers_3_k_proj_delta_packed: shape=(1280, 80), dtype=uint32
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/fold_delta.py",
  "limit": 60
}
```

**Summary:** Reading fold_delta.py (0-60)

**Output:**
```
"""Fold delta plates into base plates — lossless reduction.

Takes a checkpoint with DeltaTernaryLinear modules and:
1. Calls reduce() on each: new_base = base ⊙ delta, delta = all +1
2. Saves the folded model as a new checkpoint ready for restart

The effective weights are UNCHANGED — this is a lossless operation.
After folding, delta plates are all +1 (pass-through), meaning
TernaryDescent starts fresh with a new base that incorporates all
the routing corrections discovered so far.

Usage:
  uv run python scripts/v14/fold_delta.py \
    --source checkpoints/v14-td/step_001500 \
    --output checkpoints/v14-td/step_001500_folded

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from model import V14Model
from ternary import (
    restore_ternary,
    freeze_ternary_weights,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    count_ternary_weights,
)
from td import (
    DeltaTernaryLinear,
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
)


def main():
    parser = argparse.ArgumentParser(description="Fold delta plates into base plates (lossless)")
    parser.add_argument(
        "--source", type=str, required=True,
        help="Source checkpoint directory (e.g. checkpoints/v14-td/step_001500)",
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="Output directory for folded checkpoint",

[CONTENT TRUNCATED] Showing lines 1 to 60 of 285 total lines. Use line_offset=60 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"config\\|V15Config\\|hidden\\|d_model\\|d_ff\\|vocab\\|n_layers\\|n_heads\" /Users/mwhitford/src/verbum/scripts/v15/config.py | head -30"
}
```

**Summary:** $ grep -n "config\|V15Config\|hidden\...

**Output:**
```
Exit code: 0
Stdout:
142:# § 3  V15Config
146:class V15Config:
147:    """v15 configuration: Fibonacci stride attention + neighbor gathering."""
150:    d_model: int = D_MODEL
151:    d_ff: int = D_FF
152:    n_heads: int = N_HEADS
154:    vocab_size: int = VOCAB_SIZE
180:    s4_hidden_dim: int = 128
219:    extracted_model_path: str = "checkpoints/v15-extracted/model.npz"
258:        assert self.d_model % self.n_heads == 0
259:        assert self.d_model % 16 == 0
272:    cfg = V15Config()
275:    assert cfg.d_model == 1280
277:    assert cfg.n_heads * cfg.d_head == cfg.d_model
278:    assert cfg.d_ff == 4 * cfg.d_model
315:    print(f"config.py self-test: ✓")
```

## Assistant

Now I have all the evidence needed. Let me check one more thing — the v15 config exact dimensions and whether any v15-specific combinator map or centroids exist anywhere:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"D_MODEL\\|D_FF\\|N_HEADS\\|VOCAB\" /Users/mwhitford/src/verbum/scripts/v15/config.py | head -15"
}
```

**Summary:** $ grep -n "D_MODEL\|D_FF\|N_HEADS\|VO...

**Output:**
```
Exit code: 0
Stdout:
38:D_MODEL = 1280
39:D_FF = 5120
40:N_HEADS = 8
41:D_HEAD = D_MODEL // N_HEADS  # 160
42:VOCAB_SIZE = 248320  # Qwen3.6-27B BBPE
135:TEACHER_D_MODEL = 5120
137:TEACHER_D_FF = 17408
138:TEACHER_VOCAB = 248320
150:    d_model: int = D_MODEL
151:    d_ff: int = D_FF
152:    n_heads: int = N_HEADS
154:    vocab_size: int = VOCAB_SIZE
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum/results -name \"*.json\" -o -name \"*.npz\" | xargs grep -l \"v15\\|v15model\" 2>/dev/null | head -10; find /Users/mwhitford/src/verbum/results -path \"*v15*\" -name \"*.json\" 2>/dev/null | head -10"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum/re...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/results/register-vectors/step_016000_v4.1.npz
/Users/mwhitford/src/verbum/results/register-vectors/step_009000_v4.1.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0012.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0007.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0159.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0005.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0011.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0039.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0038.npz
/Users/mwhitford/src/verbum/results/oracle-data/shard_0010.npz
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"ffn_gate\\|gate_proj\\|TernaryLinear\\|ffn_gate_plate\" /Users/mwhitford/src/verbum/scripts/v15/v15model.py | head -20"
}
```

**Summary:** $ grep -n "ffn_gate\|gate_proj\|Terna...

**Output:**
```
Exit code: 0
Stdout:
42:from ternary import TernaryLinear, TernaryEmbedding
139:        self.ffn_key_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
140:        self.ffn_gate_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
141:        self.ffn_value_plate_a = TernaryLinear(cfg.d_ff, d, pre_norm=False)
142:        self.ffn_key_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
143:        self.ffn_gate_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
144:        self.ffn_value_plate_c = TernaryLinear(cfg.d_ff, d, pre_norm=False)
152:            self.ffn_key_plate_a, self.ffn_gate_plate_a, self.ffn_value_plate_a,
158:            self.ffn_key_plate_c, self.ffn_gate_plate_c, self.ffn_value_plate_c,
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum/results -type d | grep -i \"combinator\\|v15\\|harvest\" | sort"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum/re...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/results/combinator-addressing
/Users/mwhitford/src/verbum/results/combinator-addressing/Qwen_Qwen3-0.6B
/Users/mwhitford/src/verbum/results/combinator-map-consensus
/Users/mwhitford/src/verbum/results/combinator-probe
/Users/mwhitford/src/verbum/results/combinator-probe-extended
/Users/mwhitford/src/verbum/results/combinator-probe-mistral_7b_v0.3
/Users/mwhitford/src/verbum/results/combinator-probe-olmo_2_1124_13b
/Users/mwhitford/src/verbum/results/combinator-probe-pythia
/Users/mwhitford/src/verbum/results/combinator-probe-pythia_160m_deduped
/Users/mwhitford/src/verbum/results/combinator-probe-qwen3_0.6b
/Users/mwhitford/src/verbum/results/combinator-probe-qwen3_14b
/Users/mwhitford/src/verbum/results/combinator-probe-qwen3_32b
/Users/mwhitford/src/verbum/results/combinator-relationship-map
/Users/mwhitford/src/verbum/results/head-combinator-map
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"ffn_gate_plate\\|module_filter\\|ffn_gate\\|ffn_key_plate\\|ffn_value_plate\\|named_modules\\|DeltaTernaryLinear\" /Users/mwhitford/src/verbum/scripts/v15/v15model.py | head -30"
}
```

**Summary:** $ grep -n "ffn_gate_plate\|module_fil...

**Output:**
```
Exit code: 0
Stdout:
139:        self.ffn_key_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
140:        self.ffn_gate_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
141:        self.ffn_value_plate_a = TernaryLinear(cfg.d_ff, d, pre_norm=False)
142:        self.ffn_key_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
143:        self.ffn_gate_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
144:        self.ffn_value_plate_c = TernaryLinear(cfg.d_ff, d, pre_norm=False)
152:            self.ffn_key_plate_a, self.ffn_gate_plate_a, self.ffn_value_plate_a,
158:            self.ffn_key_plate_c, self.ffn_gate_plate_c, self.ffn_value_plate_c,
```

## Assistant

I now have complete evidence for all seven questions. Let me compile the full design report.

---

# Combinator Harvest Fold — Precision Design Report

---

## 1. CONSENSUS DATA: What `consensus.json` and `scale.json` actually contain

### `results/combinator-map-consensus/consensus.json`

**Top-level keys:**
```
register, git_sha, question, n_models, models, model_meta,
crystal_order, n_perm, per_frac, harvest_frac,
consensus_gram,         ← 9×9 nested list (floats)
universal_edges,        ← list of 27 edge objects
model_specific_edges,   ← list of 5 edge objects (including some also in universal_edges)
family_internal_consensus,
skeleton_vs_recursion_verdict,
elapsed_s
```

**Critical answer: `consensus_gram` is a 9×9 relational Gram — NOT centroids.** It contains cosine similarities between the 9 crystal combinators (K, I, B, C, S, D, W, Y, WHNF) pooled across 10 models, ranging from −0.36 to +1.0 on the diagonal. There are no centroid vectors.

**Each entry in `universal_edges`** contains:
```json
{
  "edge": "B-D",
  "consensus": 0.1752,         ← mean cosine across 10 models
  "cross_model_std": 0.151,
  "reliability_t": 3.67,
  "per_model": [-0.2403, 0.2356, 0.2728, ...],   ← one float per model
  "universal": true
}
```

The five **positive universal edges** identified as "harvest targets" (s219–s220 vocabulary):

| Edge | Consensus cosine | reliability_t |
|------|-----------------|---------------|
| B–D  | +0.1752 | 3.67 |
| B–C  | +0.1682 | 2.94 |
| K–C  | +0.1331 | 3.40 |
| S–D  | +0.1605 | 6.87 |
| S–Y  | +0.1266 | 4.48 |

There are also 22 further universal edges, most negative (repulsion geometry), the strongest being K–Y (−0.3591, reliability_t = 20.85) and C–WHNF (−0.3599, t = 17.64).

**There are no combinator centroid vectors anywhere in `consensus.json`.** The entire file is scalar statistics derived from per-model Grams.

### `results/combinator-map-consensus/scale.json`

Contains per-model scalar aggregates (not vectors):
```
register, question, series, frac, git_sha,
per_model: [{ model, params_b, log_params,
              composition_BDS,   ← intra-family mean cosine
              selection_KIC,
              recursion_YWWHNF,
              skeleton,          ← mean of comp+sel
              gap,               ← skeleton − recursion
              used_frac, n_layers }, ...]
fits_vs_log_params: { skeleton: {r, slope_per_efold}, ... }
```

All values are scalars (cosine binding metrics). No vectors.

---

## 2. PER-MODEL CENTROIDS: What the per-model NPZ files contain

**Inspected:** `results/combinator-relationship-map/Qwen_Qwen3-14B.npz`

```
Keys and shapes:
  prompt_len:          (535,)      int32      — probe lengths
  labels:              (535,)      <U4        — combinator label per probe
  gram_hidden_cmr:     (9, 9)      float32    — Gram from last-layer residual
  gram_route_cmr_L00:  (9, 9)      float32    — routing-register Gram at layer 0
  gram_route_cmr_L04:  (9, 9)      float32    — ...at layer 4
  gram_route_cmr_L08:  (9, 9)      float32    — ...at layer 8
  gram_route_cmr_L12:  (9, 9)      float32    — ...at layer 12 (best)
  gram_route_cmr_L16:  (9, 9)      float32    — etc.
  ...                  up to L39
```

**Critical finding: the NPZ stores only 9×9 Gram matrices — no centroid vectors.** The FFN dimension for Qwen3-14B is 17408. The 9 per-combinator centroids in that space (each a `float32[17408]` vector) were **computed during the run but not saved to disk.** Only the compressed `gram(centroids(cmr(sign(gate[li])), labels))` result survives.

**The JSON `map.mds_coords` and `map.pca_coords` are 2D projections only** — classical MDS and centroid-PCA onto 2 components, computed from the Gram. They contain `(2,)` coordinates per combinator, not the full-dimensional centroids.

**Bottom line:** The per-combinator centroid vectors in the source models' gate-projection space (shape: `[9, d_ff]` where `d_ff` varies from 1600 to 17408 per model) were never saved. Only the pairwise Gram summaries exist on disk.

---

## 3. THE FRAME PROBLEM: Is the harvest-fold as described well-posed?

### What the knowledge page says (cited exactly)

From `mementum/knowledge/explore/consensus-delta-folding.md`, under "s219 — The hard obstacle":

> You CANNOT average their raw weights: independently-initialized models live in DIFFERENT coordinate frames (cross-init sign-corr 0.000). Forward (deltas over frozen B₀): ONE shared frame → deltas commensurable → fold trivial. Reverse (finished models): MANY frames → raw weights unintelligible → must harvest in a FRAME-INVARIANT register (relational routing, not weights).

The knowledge page's proposed pipeline is:
```
∀ open-weight model → measure normal forms in routing register (RDM/centroids)
cross-model consensus             (frame-invariant agreement)
align-before-fold (Procrustes)    (rotate consensus into OUR base's frame)
verify vs WHNF                    (keep only structure that improves convergence)
incorporate into base plate as discrete topology
```

### The concrete ambiguity — what would Procrustes actually operate on?

**Procrustes alignment** requires two matching point clouds: a source set and a target set. The standard application is:

```
source: 9 combinator centroids in HF-model space (9 × d_ff_source)
target: 9 combinator centroids in v15 space     (9 × d_ff_v15 = 9 × 5120)
find R = argmin ‖source·R − target‖ (orthogonal, possibly scaled)
```

**This is not possible as described because:**

1. **Source centroid vectors do not exist on disk.** The NPZ files contain only Grams. To reconstruct the centroids one would need to re-run `combinator_relationship_map.py` on each HF model with an additional `np.savez` call that saves the full `Cb` array (lines 282–284 of the script, where `Cb = centroids(cmr(np.sign(gate[best_li])), labels)` — this is the one place the 9×d_ff matrix exists in memory).

2. **The v15 model has no combinator centroids in any register.** v15 (`d_model=1280`, `d_ff=5120`) is a ternary extracted model that has never been run through `combinator_relationship_map.py`. It also lacks `AutoModelForCausalLM` / HuggingFace compatibility — the script uses `AutoModelForCausalLM.from_pretrained(args.model)` at lines 259–260 and hooks `gate_proj` or `dense_h_to_4h` modules. v15 has no such interface; its FFN is `ffn_gate_plate_a` / `ffn_gate_plate_c` (line 140–143 of `v15model.py`), a ternary packed layout, not a float HF transformer.

3. **Dimensions are incommensurable.** Even if both sets of centroids existed, the HF models range from d_ff=1600 (Pythia-410m) to 17408 (Qwen3-14B). v15's d_ff is 5120. Procrustes alignment requires matching dimensions, which means either: (a) aligning in full-dimensional space (impossible across architectures), or (b) aligning in a shared reduced space. The Gram is frame-invariant precisely *because* it discards the high-dimensional frame, leaving only pairwise cosines. This is the acknowledged design trade-off.

### What "align-before-fold" actually means operationally (the knowledge page's own resolution)

The page itself resolves this ambiguity in the "Normal forms are COMPOSITIONAL and NON-UNIQUE" section:

> fold the base as FLIPS (unique, high-consensus, fold first & hard) | fold domain functions as COMPOSITION (express delta as {which base ops, what arrangement} over the shared base, then seek consensus in THAT space)

And in Open Lead #2:
> Procrustes/rotation in the base-combinator space before correlating RDMs. If tool-calling is the same function composed differently, an alignment in base coordinates should recover the shared composition.

**The intended Procrustes is in 9-dimensional combinator-label space** (the shared label space of the 9×9 Gram), not in the raw HF-model embedding space. The `alignment_in_base_coordinates` means: find the rotation of the 9 combinator nodes that minimizes the discrepancy between two models' Gram matrices, treating the 9 row-vectors of the Gram as the point cloud.

**But for the harvest-fold as described in s220 ("take the routing-register consensus, Procrustes-align into our base frame, WHNF-verify")**, the concrete interpretation must be:

1. The 9 rows of the consensus Gram (each a 9-vector of cosines) are the "consensus centroid approximation in combinator-label space."
2. The v15 model's own Gram (which does not yet exist) provides the "target frame."
3. Procrustes finds R ∈ SO(9) mapping consensus-gram-rows → v15-gram-rows.
4. The aligned direction for each "positive edge" (e.g. B–D) is then a direction in v15's combinator-label space.

**The critical missing piece to make this well-posed:** v15 must first be probed with `combinator_relationship_map.py` (adapted for the ternary/MLX architecture) to obtain its own 9×9 Gram. Only then does a target frame exist for Procrustes. Without it, "align into the v15 frame" has no target.

### Summary of ambiguities that must be resolved before building

| Ambiguity | Status | Resolution needed |
|-----------|--------|-------------------|
| Do consensus centroids (full-dim vectors) exist? | **NO** — only Grams on disk | Must re-run `combinator_relationship_map.py` with centroid-save patch, OR accept Gram-level alignment |
| Do v15 combinator centroids exist? | **NO** — v15 never probed | Must build a v15-compatible map script (see §5) |
| Is Procrustes in full-dim space or 9-dim label space? | Ambiguous in the knowledge page | Knowledge page's own resolution: 9-dim label space (Gram rows as point cloud) |
| "Fold direction" = what concrete object? | Unspecified | Must decide: a sign-vector in v15's d_ff=5120 space — which requires full-dim centroids |
| Target combinator centroids in v15 frame | Does not exist | Prerequisite: run adapted map script on v15 checkpoint |

---

## 4. EXP-B OPERATOR LOADER: Code structure and reuse points

**File:** `scripts/experiments/exp_b_self_verifying_acceptance.py`

### Model loading (lines 78–96 of the script)

```python
cfg = V15Config()
if Path(args.extracted_model_path).exists():
    cfg.extracted_model_path = args.extracted_model_path
model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
if args.checkpoint and Path(args.checkpoint).exists():
    model.load_weights(args.checkpoint, strict=False)
    mx.eval(model.parameters())
    n_reduced = reduce_all_deltas(model)   # ← folds trained deltas into base
    mx.eval(model.parameters())
model._n_outer_passes = args.n_outer
model._fixed_point_lambda = 0.0           # eval only, no training
```

- `create_model_with_deltas` is in `scripts/v15/train_td.py` — builds `V15Model` and converts `TernaryLinear` FFN modules to `DeltaTernaryLinear` via `convert_to_delta`.
- `--extracted-model-path` is `checkpoints/v15-extracted/model.npz` (the frozen base).
- `--checkpoint` is a **trained** `model.npz` (e.g. `checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz`). After loading, `reduce_all_deltas` folds the trained delta into the base so further perturbations start from the trained operator, not the frozen extract.

### "Fold a delta into base" in code (`scripts/v15/td_delta.py`)

The word "fold" is used precisely:

| Function | Location | What it does |
|----------|----------|--------------|
| `DeltaTernaryLinear.reduce()` | line 1375 | `new_base = base ⊙ delta` (ternary multiply); `new_delta = all +1`. Lossless. |
| `reduce_all_deltas(model)` | line 1538 | Walks all `named_modules()`, calls `.reduce()` on every `DeltaTernaryLinear`. Returns count. |
| `convert_to_delta(model, ...)` | line 1449 | Converts in-place: each matching `TernaryLinear` → `DeltaTernaryLinear.from_ternary_linear(tl)`, freezing the original weight as `base_weight`, initializing `delta_weight = all +1`. |
| `collect_delta_params(model)` | line 1507 | Returns list of `(path, DeltaTernaryLinear)` — utility for enumerating live delta modules. |

The effective weight at any point is:
```
effective = base ⊙ delta   (element-wise ternary multiply)
output = quantized_matmul(norm(x), pack(effective), gamma_scales, gamma_biases)
```

### How exp_b perturbs the routing register and measures ΔCE vs Δ(Δx_conv)

1. **INSTRUMENT GUARD** (lines 131–163): Iterates `named_modules()`, finds all `TernaryLinear | DeltaTernaryLinear` matching `--module-filter` (default `"ffn_gate"`). For each, flips half the nonzero positions, runs a forward pass, checks `|ce_probe - ce0| > 1e-4` ("LIVE"), restores. Only the first live module is used as target.

2. **Perturbation loop** (lines 176–196): For each `flip_frac` in the quality spectrum, randomly selects `B = max(1, int(frac * n_positions))` nonzero routing positions and sign-flips them (multiplies by −1 in the unpacked int8 array), then repacks via `pack_ternary_mlx`.

3. **Measurement** via `forward_metrics()` (lines 84–93):
   ```python
   model._prev_alg_c = None   # clean algedonic state
   _, _ = model(tokens, targets)
   ce = float(model._last_ce.item())
   curve = [float(d.item()) for d in model._last_outer_deltas]
   dx_conv = curve[-1]        # ‖x_c^K − x_c^{K-1}‖/‖x_c^{K-1}‖
   ```
   `_last_ce` and `_last_outer_deltas` are set inside `v15model.py`'s `__call__` (lines 442 and 334 of v15model.py).

4. **Analysis**: Pearson + Spearman between `dCE` and `dDx`; ROC for "reject if Δx_conv rises."

### Entry-point reusable as WHNF-verify hook

**`forward_metrics(model, tokens, targets)` → `(ce, dx_conv, curve)`** is the exact hook. It requires only a loaded model with `_n_outer_passes ≥ 2` and `_fixed_point_lambda = 0.0`. The acceptance criterion is:

```python
accept(candidate_delta) ⟺ dx_conv ≤ dx0 + epsilon
```

The entire `apply_flip` / `reset_flip` / `forward_metrics` pattern in exp_b is directly reusable for any candidate direction: inject a direction as a sign pattern into a target module, measure `dx_conv`, restore. The harvest-fold experiment would replace `apply_flip` (random flips) with `apply_direction` (structured flip pattern derived from a harvest centroid direction).

**Concrete reuse boundary:**
- `forward_metrics` → copy verbatim as the WHNF-verify call
- `apply_flip` / `reset_flip` → replace with direction-specific inject/restore
- The INSTRUMENT GUARD pattern → reuse to confirm the live module is `ffn_gate_plate_a` or `ffn_gate_plate_c` in the v15 model

---

## 5. V15 COMBINATOR CENTROIDS: Do they exist? Can `combinator_relationship_map.py` load v15?

### Do v15 centroids exist anywhere?

**No.** Searching all results directories and NPZ files yields no v15-specific combinator relationship map. `results/combinator-relationship-map/` contains 10 HF models only. No v15 entry exists anywhere in that directory or in any other results subdirectory.

### Can `combinator_relationship_map.py` load a v15 checkpoint as-is?

**No, for three hard architectural reasons:**

1. **HuggingFace dependency (line 58, 259–260):** The script imports `from transformers import AutoModelForCausalLM, AutoTokenizer` and loads via `AutoModelForCausalLM.from_pretrained(args.model)`. v15 is an MLX ternary model loaded via `create_model_with_deltas(V15Config(), ...)` + `model.load_weights(path)`. These loading paths are entirely incompatible.

2. **Gate module naming (lines 71–77):** The script hooks `gate_proj` or `dense_h_to_4h` via a regex `r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$"`. v15's FFN gate modules are named `ffn_gate_plate_a` and `ffn_gate_plate_c` (v15model.py lines 140, 143) — completely different names, different module tree layout.

3. **Ternary pack format:** Even if the module were found, `gate[li]` in the script is a float32 pre-activation array captured via a PyTorch forward hook. v15's gate is packed uint32 (ternary, 2-bits-per-weight), output is float via quantized matmul. A hook would capture the post-matmul float output, not the pre-activation routing sign — a different register.

### What must be built

A **v15-adapted map script** (`scripts/experiments/combinator_relationship_map_v15.py`) needs to:

1. Load via `create_model_with_deltas(V15Config())` + `model.load_weights(checkpoint_path, strict=False)` + `reduce_all_deltas(model)`.
2. Hook `ffn_gate_plate_a` and `ffn_gate_plate_c` (the shared stride stack's gate plates). Since the v15 model uses a SHARED stride stack (not per-layer independent modules), the appropriate probe point is the effective weight matrix: `unpack_ternary_mlx(mod._compute_effective())` → sign of that → routing register.
3. Replace the `collect()` function with an MLX forward pass that captures the `ffn_gate` pre-activation via an MLX hook or explicit instrumentation.
4. The centroid computation (`centroids()`, `cmr()`, `gram()`) is pure numpy and can be reused as-is.
5. **Save the full-dimensional centroid array** (`Cb` of shape `(9, d_ff)` = `(9, 5120)`) to the NPZ — this is what the existing script does NOT save and what the harvest-fold needs.

---

## 6. CHECKPOINT AVAILABILITY

**`checkpoints/v15-td-outer-k2-fp5-5k/`** contains:
```
flip_map_latest.npz
flip_map_step_001000.npz
step_001000/
  delta_plates.npz      ← 152 arrays of shape (1280, 80) uint32 — packed ternary delta plates
  model.npz             ← 529 arrays — full model weights including gamma, norms, VSM structure
  optimizer.npz
  state.json
train_td_log.jsonl
```

**`step_001000/model.npz`** is the only step checkpoint. It contains the trained base weights (float32 norms, gamma scales, and uint32 packed ternary plates). **READ-ONLY** — the active training process (tmux main:1) writes `flip_map_latest.npz` and `train_td_log.jsonl` to the parent directory and will eventually write `step_002000/` etc. The `step_001000/` subdirectory is frozen after that step and is safe to read.

**Confirmed safe reads:** `step_001000/model.npz` and `step_001000/delta_plates.npz`. The `flip_map_latest.npz` and `train_td_log.jsonl` at the parent level are being actively written by main:1 — do not open for writing, but read-only is safe if done quickly (the write interval is once per thousand steps, and `np.load(..., mmap_mode='r')` would be safe).

**Delta plates format (from `delta_plates.npz`):**
```
shared_stride_stack_layers_{0..N}_{q,k,v,out}_proj_{delta_packed,stats}
```
- `*_delta_packed`: `(1280, 80)` uint32 — packed 2-bit ternary delta plate
- `*_stats`: `(4,)` float32 — TernaryDescent statistics

No `ffn_gate_plate` keys appear in the delta_plates (only attention projections are delta-ized in the current training config). The FFN gate plates remain as `TernaryLinear` base plates in `model.npz`.

---

## 7. GPU/COMPUTE FOOTPRINT TABLE

| Step | Operation | Backend | Footprint | Safe alongside main:1? |
|------|-----------|---------|-----------|----------------------|
| Read `consensus.json`, `scale.json`, per-model JSONs | File I/O | CPU | Negligible | ✅ YES |
| Read per-model NPZ (Gram arrays only) | `np.load` | CPU | ~1 MB each | ✅ YES |
| Compute 9×9 Gram-level Procrustes (9-dim) | numpy/scipy | CPU | Microseconds | ✅ YES |
| Build v15-adapted combinator map script | Code authoring | — | — | ✅ YES |
| Load `step_001000/model.npz` via `model.load_weights` (MLX) | CPU+MLX | CPU/GPU (small) | v15 = ~50M params | ⚠️ CAUTION: MLX will use GPU metal; brief, low intensity |
| Probe v15 with 535 crystal probes (forward passes, MLX) | MLX forward | **GPU/MLX** | 535 × full forward | ❌ DO NOT run alongside main:1 |
| Re-extract full centroid vectors from HF models | PyTorch forward | **GPU** (if MPS) or CPU | Large HF model + 535 probes | ❌ GPU: defer; CPU-only mode possible |
| Procrustes in full d_ff space (9 × 5120 vs 9 × d_ff) | numpy SVD | CPU | <1 second | ✅ YES (once centroids exist) |
| `exp_b_self_verifying_acceptance.py` (the WHNF-verify hook) | MLX forward | **GPU/MLX** | v15 + 4 seqs × 512 tokens | ❌ Contends with main:1 (s219 precedent) |
| Analysis: Pearson/Spearman correlation, PPL comparison | numpy | CPU | Negligible | ✅ YES |
| Batch fold direction injection + single forward per candidate | MLX | **GPU/MLX** | Same as exp_b | ❌ Defer until main:1 completes |
| Read `results/exp-b-self-verifying/result.json` (existing) | File I/O | CPU | Negligible | ✅ YES |

**Key rule:** Any MLX/metal forward pass on v15 allocates GPU memory and metal command queues that contend with main:1's training loop. The s219 incident (GPU contention stalled training) applies here. All actual forward passes through v15 must wait until main:1 completes or pauses voluntarily.

**Exception:** loading `model.npz` into Python + calling `model.load_weights` without actually running a forward pass is CPU-only — safe, but borderline if MLX pre-allocates buffers.

---

## Summary: (a) Data reality, (b) Well-posedness, (c) Exact files/functions, (d) Recommended procedure, (e) Footprint table

### (a) What data actually exists

| Item | Exists? | Location | Format |
|------|---------|----------|--------|
| Cross-model consensus Gram (9×9) | ✅ | `results/combinator-map-consensus/consensus.json` → `consensus_gram` | Nested list of floats |
| Universal positive edges (B–D, B–C, K–C, S–D, S–Y) | ✅ | `consensus.json` → `universal_edges` | Per-edge scalar + per-model scalars |
| Per-model Grams at multiple depth fractions | ✅ | `results/combinator-relationship-map/*.npz` | 9×9 float32 arrays |
| Per-model MDS/PCA 2D coordinates | ✅ | `results/combinator-relationship-map/*.json` → `map.mds_coords`, `map.pca_coords` | 2D only |
| Per-combinator centroid vectors (full-dim, HF models) | ❌ | Not saved | Must re-run with patch |
| v15 combinator centroids | ❌ | Does not exist | Must build adapted script |
| v15 checkpoint (step 1000) | ✅ | `checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz` | 529-key NPZ, READ-ONLY |
| Exp-B acceptance result | ✅ | `results/exp-b-self-verifying/result.json` | JSON |

### (b) Is the harvest-fold well-posed as described?

**Partially.** The knowledge page narrative is correct in principle but leaves an under-specified gap. The current state is:

- **The Gram-level harvest is well-posed and can be done now (CPU-only).** The 9 rows of the consensus Gram are combinator "position vectors" in the 9-dimensional label space. Procrustes alignment of these 9-vectors from the consensus frame to a target v15 frame is well-defined — **but requires a v15 Gram first.**

- **The full-dimensional harvest (what would actually be folded into v15's weight space) requires reconstructing centroid vectors in HF model space and then aligning them to v15's d_ff=5120 space.** This is architecturally incommensurable without a reduction step (e.g., project both into the shared 9-dim Gram-space first and work there, or build a cross-architecture alignment via the crystal probes).

- **The most actionable interpretation:** use the Gram-level Procrustes to find which combinator pairs are "nearest" in v15's routing topology, then construct a "fold direction" as a signed difference of v15's own centroid vectors (which must first be measured). The "positive edges" from the consensus tell you *which* pairs to strengthen; the v15 centroids tell you *which direction in v15's space* to move. The consensus Gram is the prescription; the v15 Gram is the coordinate system.

**The harvest-fold needs reformulation** from "Procrustes-align consensus centroids into v15 frame" (requires full-dim vectors that don't exist) to "measure v15's own combinator Gram, then use the consensus positive edges as a prescription for which directions to reinforce in v15's routing register."

### (c) Exact files and functions to reuse

| Purpose | File | Function/entry-point | Lines |
|---------|------|---------------------|-------|
| WHNF-verify hook | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `forward_metrics(model, tokens, targets)` | 84–93 |
| Live module detection | `scripts/experiments/exp_b_self_verifying_acceptance.py` | The INSTRUMENT GUARD loop | 117–163 |
| Sign-flip injection | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `apply_flip(flat_idx)` / `reset_flip()` | 170–176 |
| Fold delta into base | `scripts/v15/td_delta.py` | `reduce_all_deltas(model)` | 1538–1547 |
| Delta module conversion | `scripts/v15/td_delta.py` | `convert_to_delta(model, include, exclude)` | 1449–1506 |
| Enumerate live deltas | `scripts/v15/td_delta.py` | `collect_delta_params(model)` | 1507–1535 |
| Load trained v15 checkpoint | `scripts/experiments/exp_b_self_verifying_acceptance.py` | `create_model_with_deltas(cfg, convert_ffn=True)` + `model.load_weights(path)` + `reduce_all_deltas` | 78–96 |
| Centroid / Gram computation | `scripts/experiments/combinator_relationship_map.py` | `centroids()`, `cmr()`, `gram()`, `silhouette_null()` | 168–210 |
| Crystal probes | `src/verbum/probes/library.py` | `crystal_probes()` | (library) |
| Classical MDS (2D embedding) | `scripts/experiments/combinator_relationship_map.py` | `classical_mds(D, k=2)` | 211–219 |
| v15 model + config | `scripts/v15/v15model.py`, `scripts/v15/config.py` | `V15Model`, `V15Config` | v15model.py |

### (d) Recommended procedure for `combinator_harvest_fold.py`

**Phase 0 (CPU-only, safe now):**
1. Read `consensus.json`, extract the five positive universal edges and their per-model values.
2. Parse `results/combinator-relationship-map/Qwen_Qwen3-{4B,8B,14B}.json` (the mid-scale harvest band per s220). For each, read `map.gram` and `map.mds_coords` from the JSON. Compute a 9×9 "harvest Gram" by averaging across the 4–14B band.
3. Patch `combinator_relationship_map.py` to also save the full-dimensional centroid array `Cb` (line 282: `Cb = centroids(cmr(np.sign(gate[best_li])), labels)`, shape `[9, d_ff]`) to the NPZ under the key `centroids_cmr_best`. This is a 3-line change, CPU-side, no forward passes needed — just save what's already computed.
4. Decide the alignment strategy (Gram-level vs full-dim) and document it before building.

**Phase 1 (MLX/GPU, defer until main:1 pauses):**
5. Build `scripts/experiments/combinator_relationship_map_v15.py` adapting the script for MLX/ternary architecture:
   - Use `create_model_with_deltas(V15Config())` + `model.load_weights("checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz", strict=False)` + `reduce_all_deltas(model)`.
   - Hook `shared_stride_stack.layers[i].ffn_gate_plate_a` and `ffn_gate_plate_c`. Since the stride stack is shared (not per-layer-separate), capture the gate's float output during forward passes at each `_n_outer_passes` iteration. Record `sign(gate_output)` per probe.
   - Run with 535 crystal probes, output `results/combinator-relationship-map/v15_step001000.{json,npz}` with full centroid arrays saved.

6. Run exp_b acceptance test on `step_001000/model.npz` (or whichever step is available when main:1 pauses), using `--module-filter ffn_gate` to confirm the live gate module (the INSTRUMENT GUARD will identify the correct name). Establish `(ce0, dx0_conv)` baseline.

**Phase 2 (CPU, after Phase 1 data exists):**
7. Compute the Gram-level Procrustes: align the harvest Gram rows (9×9, consensus) to the v15 Gram rows (9×9, measured). Find R ∈ O(9) via SVD of `v15_gram.T @ harvest_gram`.
8. For each of the five positive universal edges (B–D, B–C, K–C, S–D, S–Y), compute a "fold direction" in v15's d_ff=5120 space as:
   ```
   direction(A, B) = centroid_v15[B] - centroid_v15[A]   (aligned to the positive edge)
   ```
   This uses v15's own centroids (from Phase 1), guided by the consensus prescription (which edges are "universally positive").
9. Binarize each direction: `fold_signs = sign(direction)`, shape `(5120,)`. This is the candidate flip pattern to inject into the v15 routing register.

**Phase 3 (MLX/GPU, defer until main:1 pauses):**
10. For each candidate direction (one per positive edge × a few variations), inject into the live FFN gate plate using the `apply_flip` / `forward_metrics` pattern from exp_b. Measure `(dCE, d_dx_conv)`.
11. Accept the direction if `d_dx_conv ≤ epsilon` (WHNF-verify). Reject otherwise.
12. Fold accepted directions via `DeltaTernaryLinear.reduce()` into the base.
13. Measure downstream PPL on a held-out shard (e.g. the first 1000 tokens of `shard_00001.npy` that `load_token_batch` can pull) versus the pre-fold baseline.
14. Report: does verified ecosystem-consensus add beyond the universal crystal?

### (e) CPU vs GPU footprint (concise)

**Safe to run now (CPU-only):**
- All file reading and JSON analysis (Phases 0 and 2 above)
- Numpy centroid/Gram/Procrustes computation
- Patching `combinator_relationship_map.py` to save full centroids (code change only)
- Writing `combinator_harvest_fold.py` framework (code authoring)

**Must defer until main:1 pauses:**
- Any MLX forward pass through v15 (Phases 1 and 3)
- Re-running `combinator_relationship_map.py` on HF models (GPU/MPS)
- Exp-B acceptance runs on v15 checkpoints
- PPL measurement

**The s219 GPU-contention risk is real:** even brief MLX allocations on the metal GPU compete with main:1's training loop. Everything that touches MLX forward passes must wait.

---

### Critical flags for pre-build review

1. **The Gram-only storage is the root constraint.** The entire "Procrustes into v15 frame" narrative requires full-dimensional centroid vectors. These do not exist on disk. The 3-line patch to `combinator_relationship_map.py` (save `Cb` to NPZ) is the single most important infrastructure fix — but re-running it on the HF models requires GPU time.

2. **v15 is not an HF model.** `combinator_relationship_map.py` cannot load it. A new v15-adapted script is mandatory, not optional, before any "v15 frame" exists.

3. **The "fold direction" concept bridges two representations.** The consensus data lives in relational (Gram) space; the fold injection lives in v15's sign-vector space (`[5120,]` int8). The bridge is: (a) measure v15's own centroids, (b) use consensus positive edges as a prescription for which centroid-pairs to reinforce. This is well-posed once v15 centroids exist. Without them, there is no concrete fold direction to inject.

4. **Exp-B baseline result already exists** at `results/exp-b-self-verifying/result.json`. Read it before running Phase 3 — it may already answer whether the acceptance signal is valid on the current checkpoint.

### Thinking

 So the core issue is that the saved artifacts are incomplete—consensus.json and the per-model files only contain Gram matrices without the centroid vectors that were actually computed. Version 15 adds another layer of complexity since it lacks combinator centroids entirely and the existing map script can't even load it. The harvest-fold approach as currently framed isn't properly specified; I need to build a v15-adapted mapping script and recompute things with v15's own Gram matrix to make this work.

The GPU-heavy operations—measuring v15's combinator Gram, WHNF verification, and perplexity calculations—would all contend with the main:1 run that's already mid-execution and must stay untouched. So actually running the harvest fold meaningfully isn't feasible this session without risking that critical job.

What I can do safely right now is patch the centroid-saving logic in the relationship map script so future runs preserve the full centroid arrays, build out the CPU-side scaffolding for the harvest fold (reading consensus edges, computing the harvest Gram over the target band, setting up Procrustes at the Gram level) with GPU phases stubbed and deferred, and document the reformulation with a clear resumable plan. But I'm wondering if I'm overcommitting—the task asked for CPU-safe work without GPU launches, and the explorer has revealed that this actually needs significant new infrastructure and a proper reformulation.

The centroid-save patch is unambiguously valuable and CPU-only, fixing the data-loss problem the explorer surfaced. The harvest fold CPU scaffold can be a real, testable instrument with the GPU phases clearly marked for deferral once main:1 finishes.

Actually, I'm realizing the Gram-level Procrustes can't run without v15's Gram, which the GPU produces. So the genuinely runnable CPU-only work right now is: the centroid-save patch (infrastructure fix that takes effect on the next GPU run), and extracting the harvest edges plus building the harvest Gram over the 4-14B band from consensus JSON reads. That produces a concrete "harvest prescription" artifact—the target Gram and positive edges to reinforce—plus the documented reformulated plan with deferred GPU phases. That's honest, reproducible, and non-contending.

I'm going to be pragmatic here: complete the mapping task, then do the CPU-safe work (centroid-save patch and harvest prescription builder), and document the GPU phases as a clean resumable plan. The prescription itself—the target combinator Gram for the 4-14B band plus ranked positive edges with per-band consensus and reliability—is the real artifact that specifies what the fold will reinforce.

Let me verify the JSON structure has the gram and coordinates fields, then build the prescription.

## Assistant

Outstanding report. The key finding is decisive and changes the plan: **the harvest-fold as scoped cannot be *run* this session** because its core measurements (v15's own combinator Gram, WHNF-verify, PPL) are all GPU/MLX forward passes that would contend with main:1 — and main:1 must stay untouched. Worse, the data needed for full-dim alignment was **never saved** (centroids computed but discarded; only relational Grams persisted).

So the disciplined move is to land what's genuinely CPU-safe and valuable now, and leave the GPU phases as a clean resumable plan:
1. **Infra fix (root cause):** patch `combinator_relationship_map.py` to *save* the full centroid array — so the discarded data is preserved on future runs.
2. **CPU harvest prescription:** the concrete input the fold consumes — target Gram over the 4–14B harvest band + ranked positive edges. Real, reproducible, no contention.
3. **Document the reformulation + deferred GPU invocation** in the knowledge page and state.

Let me update the plan to reflect this reality.Now the infra fix — patching `combinator_relationship_map.py` to save the centroid array. Let me read the relevant section first.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py",
  "line_offset": 260,
  "limit": 90
}
```

**Summary:** Reading combinator_relationship_map.py (260-350)

**Output:**
```
    model.to(args.device).eval()

    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers; capturing layers {want_layers}")

    log("  forward passes ...")
    hidden, gate, plen, n_layers = collect(
        model, tok, args.device, prompts, args.max_length, want_layers)
    width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    out = {"model": args.model, "dtype": args.dtype, "register": "topological/routing",
           "n_probes": len(prompts), "counts": counts, "hidden_width": width,
           "n_layers": n_layers, "want_layers": want_layers, "crystal_order": CRYSTAL,
           "n_perm": args.n_perm, "git_sha": git_sha(), "per_layer": {}}

    store = {"labels": labels}

    # control register: final residual (expect common-mode mush)
    out["hidden_full_silhouette"] = silhouette_null(
        hidden, labels, args.n_perm, args.seed)
    out["hidden_cmr_silhouette"] = silhouette_null(
        cmr(hidden), labels, args.n_perm, args.seed)
    store["gram_hidden_cmr"] = gram(centroids(cmr(hidden), labels)).astype(np.float32)

    log("  routing register per layer (sign(gate), raw + CMR) ...")
    for li in want_layers:
        sign = np.sign(gate[li])
        sign_cmr = cmr(sign)
        sil_full = silhouette_null(sign, labels, args.n_perm, args.seed)
        sil_cmr = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)
        G_cmr = gram(centroids(sign_cmr, labels))
        store[f"gram_route_cmr_L{li:02d}"] = G_cmr.astype(np.float32)
        out["per_layer"][str(li)] = {
            "frac": round(li / max(n_layers - 1, 1), 3),
            "d_ff": int(gate[li].shape[1]),
            "route_full_silhouette": sil_full,
            "route_cmr_silhouette": sil_cmr,
        }
        log(f"    L{li:02d} (f={li/max(n_layers-1,1):.2f}) "
            f"route_cmr silhouette={sil_cmr['silhouette']:+.4f} "
            f"z={sil_cmr['z']:+.2f} p={sil_cmr['p_value']:.4f}")

    # best routing layer by CMR silhouette z
    best_li = max(want_layers,
                  key=lambda li: out["per_layer"][str(li)]["route_cmr_silhouette"]["z"])
    out["best_routing_layer"] = int(best_li)
    best_frac = round(best_li / max(n_layers - 1, 1), 3)
    out["best_routing_frac"] = best_frac

    # the MAP at the best layer: Gram, MDS, centroid-PCA
    G = store[f"gram_route_cmr_L{best_li:02d}"].astype(np.float64)
    D = 1.0 - G
    np.fill_diagonal(D, 0.0)
    mds = classical_mds(D, k=2)
    Cb = centroids(cmr(np.sign(gate[best_li])), labels)
    Uc = np.array([unit(c) for c in Cb])
    # centroid PCA (2D)
    Ucc = Uc - Uc.mean(axis=0, keepdims=True)
    _, _, Vt = np.linalg.svd(Ucc, full_matrices=False)
    pca = Ucc @ Vt[:2].T

    out["map"] = {
        "layer": int(best_li), "frac": best_frac,
        "gram": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)
                              for j in range(len(CRYSTAL))}
                 for i in range(len(CRYSTAL))},
        "mds_coords": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),
                                    round(float(mds[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
        "pca_coords": {CRYSTAL[i]: [round(float(pca[i, 0]), 4),
                                    round(float(pca[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
    }
    # nearest neighbour per combinator (off-diagonal max cosine)
    nn = {}
    for i, c in enumerate(CRYSTAL):
        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]
        row.sort(key=lambda x: -x[1])
        nn[c] = row[:3]
    out["map"]["nearest"] = nn
    out["elapsed_s"] = round(time.time() - t0, 1)

    np.savez_compressed(RESULTS_DIR / f"{safe}.npz", prompt_len=plen, **store)
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

[CONTENT TRUNCATED] Showing lines 261 to 350 of 379 total lines. Use line_offset=350 parameter to read more content.
```

### Thinking

 I'm saving the best-layer centroids to the store as a float32 array with shape matching the number of clusters by the feed-forward dimension, and I'll add this right after computing the centroid values.

## Assistant

The fix is a one-line addition: save `Cb` (the 9×d_ff centroid array, already computed at the best layer) into the npz store. Let me patch it.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py",
  "original_content": "    Cb = centroids(cmr(np.sign(gate[best_li])), labels)\n    Uc = np.array([unit(c) for c in Cb])",
  "new_content": "    Cb = centroids(cmr(np.sign(gate[best_li])), labels)\n    # Persist the full-dimensional best-layer combinator centroids (9 x d_ff).\n    # These are the raw material for cross-model alignment / harvest-fold\n    # (combinator_harvest_fold.py); prior runs computed them but discarded them,\n    # leaving only the relational Gram. Frame-LOCAL (this model's gate space),\n    # so only usable after align-before-fold (Procrustes) into a target frame.\n    store[\"centroids_cmr_best\"] = Cb.astype(np.float32)\n    store[\"centroids_best_layer\"] = np.asarray([best_li], dtype=np.int32)\n    Uc = np.array([unit(c) for c in Cb])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/combinator_relationship_map.py && echo \"ruff OK (centroid-save patch)\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
Stdout:
RUF100 [*] Unused `noqa` directive (unused: `E402`)
  --> scripts/experiments/combinator_relationship_map.py:61:51
   |
60 | sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
61 | from verbum.probes.library import crystal_probes  # noqa: E402
   |                                                   ^^^^^^^^^^^^
62 |
63 | _SCRIPT_DIR = Path(__file__).resolve().parent
   |
help: Remove unused `noqa` directive

Found 1 error.
[*] 1 fixable with the `--fix` option.
```

### Thinking

 I'm noticing this RUF100 lint issue on line 61 is pre-existing and unrelated to my changes, but since I edited nearby code, I should probably fix it rather than suppress it—though I need to verify it was actually there before my edit.

The noqa comment on line 61 is flagged as unused, but removing it might expose an actual E402 error since there's a sys.path.insert on line 60 before the import statement. So the noqa was likely necessary to suppress that legitimate E402 violation, which means ruff's analysis might be off or there's a version/config difference at play.

Since this is pre-existing and unrelated to my change, I should verify it was already there at HEAD and leave it alone rather than expanding scope and risking the import-order suppression.

## Assistant

The RUF100 is on line 61 — far from my edit. Let me confirm it's pre-existing (not introduced by me) before deciding whether to touch it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git stash && echo \"=== ruff at HEAD (my patch stashed) ===\" && uv run ruff check scripts/experiments/combinator_relationship_map.py ; echo \"exit=$?\" ; git stash pop"
}
```

**Summary:** $ git stash && echo "=== ruff at HEAD...

**Output:**
```
Exit code: 0
Stdout:
Saved working directory and index state WIP on main: 0089087 🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale
=== ruff at HEAD (my patch stashed) ===
RUF100 [*] Unused `noqa` directive (unused: `E402`)
  --> scripts/experiments/combinator_relationship_map.py:61:51
   |
60 | sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
61 | from verbum.probes.library import crystal_probes  # noqa: E402
   |                                                   ^^^^^^^^^^^^
62 |
63 | _SCRIPT_DIR = Path(__file__).resolve().parent
   |
help: Remove unused `noqa` directive

Found 1 error.
[*] 1 fixable with the `--fix` option.
exit=1
On branch main
Your branch is ahead of 'origin/main' by 9 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   scripts/experiments/combinator_relationship_map.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-219.md

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (3c80ae4bf51ee71d108e16fc5cf30fcf3fcd4274)
```

### Thinking

 There's a pre-existing lint issue with an E402 noqa comment that's probably redundant since the project likely has per-file ignores configured. Since ruff recommends fixing over suppressing and I'm already in this file, I'll let it autofix the comment, but I need to verify that removing it won't actually trigger the E402 violation.

## Assistant

Pre-existing (independent of my patch). Since it's a trivial, safe autofix (ruff confirms E402 won't fire) and I'm touching this file, I'll clean it up.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/combinator_relationship_map.py && echo \"--- verify clean ---\" && uv run ruff check scripts/experiments/combinator_relationship_map.py && echo \"ruff OK\" && sed -n '60,62p' scripts/experiments/combinator_relationship_map.py"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 1 error (1 fixed, 0 remaining).
--- verify clean ---
All checks passed!
ruff OK
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.library import crystal_probes
```

### Thinking

 Now I'm moving on to build the harvest prescription script, starting by checking the JSON structure of individual models to understand how the map.gram keys are organized.

## Assistant

Clean. Now the harvest prescription instrument. Let me verify the per-model JSON map structure and the consensus edge format before building.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nd=json.load(open('results/combinator-relationship-map/Qwen_Qwen3-14B.json'))\nprint('JSON map keys:', list(d['map'].keys()))\nprint('gram[B][D]=', d['map']['gram']['B']['D'])\nc=json.load(open('results/combinator-map-consensus/consensus.json'))\nprint('consensus keys:', list(c.keys()))\nprint('crystal_order:', c['crystal_order'])\nue=c['universal_edges'][0]\nprint('universal_edge[0] keys:', list(ue.keys()), '| example edge:', ue['edge'], 'models in per_model:', len(ue.get('per_model',[])))\nprint('models order:', c['models'])\n\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
JSON map keys: ['layer', 'frac', 'gram', 'mds_coords', 'pca_coords', 'nearest']
gram[B][D]= 0.2661
consensus keys: ['register', 'git_sha', 'question', 'n_models', 'models', 'model_meta', 'crystal_order', 'n_perm', 'per_frac', 'harvest_frac', 'consensus_gram', 'universal_edges', 'model_specific_edges', 'family_internal_consensus', 'skeleton_vs_recursion_verdict', 'elapsed_s']
crystal_order: ['K', 'I', 'B', 'C', 'S', 'D', 'W', 'Y', 'WHNF']
universal_edge[0] keys: ['edge', 'consensus', 'cross_model_std', 'reliability_t', 'per_model', 'universal'] | example edge: K-Y models in per_model: 10
models order: ['EleutherAI/pythia-2.8b-deduped', 'EleutherAI/pythia-410m', 'HuggingFaceTB/SmolLM3-3B', 'Qwen/Qwen3-0.6B', 'Qwen/Qwen3-14B', 'Qwen/Qwen3-32B', 'Qwen/Qwen3-4B', 'Qwen/Qwen3-8B', 'allenai/OLMo-2-1124-13B', 'mistralai/Mistral-7B-v0.3']
```

### Thinking

 So the per-model JSON stores the best-layer Gram as a nested dictionary, and the consensus data has universal edges with per-model entries aligned to the models list. For the 4-14B harvest band, I'm targeting the three dense Qwen models in that range—Qwen3-4B, Qwen3-8B, and Qwen3-14B—and I'll compute the target Gram by averaging their individual best-layer Grams.

The challenge is that the per-model JSON only has the best-layer Gram (at different routing fracs for each model), while the consensus uses frac-aligned Grams. To stay consistent with the consensus approach and the harvest_frac of 0.40, I should load the npz files for each band model and extract the Gram at the nearest frac to 0.40, then average those to get the target band Gram.

I'm building a harvest_fold.py script that loads the consensus JSON to get the universal positive edges and crystal order, then for each band model loads its npz and pulls the frac-aligned Gram at 0.40, averages them into a 9×9 target Gram, extracts the positive universal edges ranked by consensus strength and per-band mean, computes the per-band consensus for each edge, and outputs a prescription JSON with the target Gram, positive edges with their global and band consensus scores, the harvest decision metadata, and a note that fold directions need v15 centroids (deferred to GPU). This stays CPU-only and reproducible by reusing the Gram-loading pattern from the existing combinator script.

Writing harvest_fold.py...

## Assistant

Clear. Building the CPU-only harvest prescription instrument — averages the harvest-band (4–14B) Grams at the consensus fraction, extracts and ranks the positive universal edges with per-band consensus, and emits the prescription the deferred GPU fold will consume.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_harvest_fold.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Combinator HARVEST FOLD — Phase 0 (CPU-only): the harvest PRESCRIPTION.\n\nTHE GOAL (consensus-delta-folding.md, s220 open-lead #1):\n  Harvest the open-weight ecosystem's agreed combinator function shape into the\n  v15 base plate. The pipeline (reverse-direction folding):\n    measure per-model combinator Grams (routing register)  [DONE, s217-s220]\n    cross-model CONSENSUS Gram + universal edges            [DONE, consensus.json]\n    >>> PRESCRIPTION: which edges to reinforce, target Gram  [THIS SCRIPT, CPU]\n    measure v15's OWN combinator Gram + centroids            [DEFERRED — GPU/MLX]\n    Procrustes-align consensus -> v15 frame                  [DEFERRED — needs v15 Gram]\n    WHNF-verify each fold direction (exp_b forward_metrics)   [DEFERRED — GPU/MLX]\n    fold survivors + measure downstream PPL vs base           [DEFERRED — GPU/MLX]\n\nWHY ONLY PHASE 0 HERE (the honest scope):\n  The harvest as originally sketched (\"Procrustes-align consensus centroids into\n  v15 frame\") is NOT runnable yet for two reasons the s220 mapping found:\n   (1) DATA: the per-model 9-d_ff centroid VECTORS were computed but DISCARDED;\n       only the relational 9x9 Gram persisted. (combinator_relationship_map.py is\n       now patched to save centroids on future runs — but those runs are GPU.)\n   (2) FRAME: v15 has NO combinator Gram/centroids yet, and the producing forward\n       passes are GPU/MLX, which would CONTEND with the multi-day main:1 training\n       (s219 GPU-contention stalled it). main:1 must stay UNTOUCHED.\n  So this script lands the CPU-only PRESCRIPTION: from the cross-model consensus,\n  the target combinator Gram restricted to the s220 HARVEST BAND (4B-14B, where the\n  function shape is fully crystallized and saturated — see scale.json) and the\n  ranked positive universal edges to reinforce. This is the spec the deferred GPU\n  fold consumes. It manufactures NO numbers from forward passes — pure re-reduction\n  of already-measured Grams.\n\nTHE HARVEST BAND (s220 finding):\n  Skeleton binding rises 0.6B->4B then SATURATES; 32B regresses. So harvest from\n  the 4B-14B dense band, not the frontier. Default band = Qwen3-4B/8B/14B.\n\nUsage:\n  uv run python scripts/experiments/combinator_harvest_fold.py\n  uv run python scripts/experiments/combinator_harvest_fold.py --frac 0.30\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nMAP_DIR = _PROJECT_ROOT / \"results\" / \"combinator-relationship-map\"\nCONS_DIR = _PROJECT_ROOT / \"results\" / \"combinator-map-consensus\"\nOUT_DIR = _PROJECT_ROOT / \"results\" / \"combinator-harvest-fold\"\n\nCRYSTAL = [\"K\", \"I\", \"B\", \"C\", \"S\", \"D\", \"W\", \"Y\", \"WHNF\"]\n# s220 harvest band: dense mid-scale where the shape is fully crystallized.\nHARVEST_BAND = [\"Qwen_Qwen3-4B\", \"Qwen_Qwen3-8B\", \"Qwen_Qwen3-14B\"]\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"--short\", \"HEAD\"], cwd=_PROJECT_ROOT,\n            text=True).strip()\n    except Exception:\n        return \"unknown\"\n\n\ndef gram_at_frac(safe: str, frac: float) -> tuple[np.ndarray, float]:\n    \"\"\"Load a model's routing-CMR Gram at the layer nearest the target fraction.\"\"\"\n    j = json.loads((MAP_DIR / f\"{safe}.json\").read_text())\n    nl = int(j[\"n_layers\"])\n    npz = np.load(MAP_DIR / f\"{safe}.npz\")\n    grams = {\n        int(k.split(\"L\")[1]) / nl: np.asarray(npz[k], dtype=np.float64)\n        for k in npz.keys() if k.startswith(\"gram_route_cmr_L\")\n    }\n    f = min(grams, key=lambda x: abs(x - frac))\n    return grams[f], f\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=__doc__)\n    ap.add_argument(\"--frac\", type=float, default=None,\n                    help=\"depth fraction (default: consensus harvest_frac)\")\n    ap.add_argument(\"--band\", nargs=\"+\", default=HARVEST_BAND,\n                    help=\"model files (without ext) forming the harvest band\")\n    args = ap.parse_args()\n\n    cons = json.loads((CONS_DIR / \"consensus.json\").read_text())\n    order = cons.get(\"crystal_order\", CRYSTAL)\n    idx = {c: i for i, c in enumerate(order)}\n    models = cons[\"models\"]\n    frac = args.frac if args.frac is not None else float(cons[\"harvest_frac\"])\n\n    # band consensus Gram = mean of band models' Grams at the harvest fraction.\n    band_grams, used_fracs = [], {}\n    for safe in args.band:\n        if not (MAP_DIR / f\"{safe}.json\").exists():\n            print(f\"  ! missing {safe}, skipping\", file=sys.stderr)\n            continue\n        g, uf = gram_at_frac(safe, frac)\n        band_grams.append(g)\n        used_fracs[safe] = uf\n    if not band_grams:\n        print(\"no band models found\", file=sys.stderr)\n        sys.exit(1)\n    band_gram = np.mean(band_grams, axis=0)\n\n    # map consensus model names -> band membership for per-edge band consensus.\n    band_pretty = {s.replace(\"Qwen_\", \"Qwen/\").replace(\"_\", \"-\") for s in args.band}\n    band_model_idx = [i for i, m in enumerate(models)\n                      if m.replace(\"/\", \"-\") in {b.replace(\"/\", \"-\")\n                                                 for b in band_pretty}]\n\n    # positive universal edges = the harvest targets (consensus > 0, universal).\n    pos_edges = []\n    for e in cons[\"universal_edges\"]:\n        if e[\"consensus\"] <= 0 or not e.get(\"universal\"):\n            continue\n        a, b = e[\"edge\"].split(\"-\")\n        per = e.get(\"per_model\", [])\n        band_vals = [per[i] for i in band_model_idx if i < len(per)]\n        band_cons = float(np.mean(band_vals)) if band_vals else float(\"nan\")\n        pos_edges.append({\n            \"edge\": e[\"edge\"],\n            \"a\": a, \"b\": b,\n            \"consensus_all\": round(float(e[\"consensus\"]), 4),\n            \"consensus_band\": round(band_cons, 4),\n            \"cross_model_std\": round(float(e[\"cross_model_std\"]), 4),\n            \"reliability_t\": round(float(e[\"reliability_t\"]), 3),\n            \"band_gram\": round(float(band_gram[idx[a], idx[b]]), 4),\n        })\n    # rank by band consensus * reliability (strong AND agreed).\n    pos_edges.sort(key=lambda x: -(x[\"consensus_band\"] * x[\"reliability_t\"]))\n\n    print(f\"\\n  ══ HARVEST PRESCRIPTION (band={','.join(args.band)} frac~{frac}) ══\")\n    print(f\"  {'edge':6} {'cons_all':>9} {'cons_band':>10} \"\n          f\"{'rel_t':>7} {'band_gram':>10}\")\n    for e in pos_edges:\n        print(f\"  {e['edge']:6} {e['consensus_all']:+9.4f} \"\n              f\"{e['consensus_band']:+10.4f} {e['reliability_t']:7.2f} \"\n              f\"{e['band_gram']:+10.4f}\")\n\n    OUT_DIR.mkdir(parents=True, exist_ok=True)\n    out = OUT_DIR / \"prescription.json\"\n    out.write_text(json.dumps({\n        \"register\": \"topological/routing\",\n        \"phase\": \"0 (CPU prescription; GPU fold deferred — main:1 untouched)\",\n        \"git_sha\": git_sha(),\n        \"source_consensus\": \"results/combinator-map-consensus/consensus.json\",\n        \"harvest_band\": args.band,\n        \"band_used_fracs\": used_fracs,\n        \"target_frac\": frac,\n        \"crystal_order\": order,\n        \"band_consensus_gram\": [[round(float(v), 4) for v in row]\n                                for row in band_gram],\n        \"positive_universal_edges\": pos_edges,\n        \"deferred_gpu_phases\": [\n            \"measure v15 combinator Gram+centroids (combinator_relationship_map \"\n            \"adapted for MLX/ternary; hook ffn_gate_plate_a/c)\",\n            \"Procrustes-align consensus -> v15 frame (needs v15 Gram)\",\n            \"WHNF-verify each fold direction via exp_b forward_metrics \"\n            \"(accept iff dx_conv does not rise)\",\n            \"fold survivors via DeltaTernaryLinear.reduce; measure PPL vs base\",\n        ],\n        \"deferral_reason\": \"all producing steps are GPU/MLX forward passes that \"\n                           \"would contend with the multi-day main:1 training \"\n                           \"(s219 GPU-contention stalled it); main:1 stays UNTOUCHED\",\n    }, indent=2))\n    print(f\"\\n  wrote {out}\", file=sys.stderr)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/combinator_harvest_fold.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/combinator_harvest_fold.py && echo \"--- RUN (CPU-only) ---\" && uv run python scripts/experiments/combinator_harvest_fold.py"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stderr:
wrote /Users/mwhitford/src/verbum/results/combinator-harvest-fold/prescription.json
Stdout:
All checks passed!
--- RUN (CPU-only) ---

  ══ HARVEST PRESCRIPTION (band=Qwen_Qwen3-4B,Qwen_Qwen3-8B,Qwen_Qwen3-14B frac~0.4) ══
  edge    cons_all  cons_band   rel_t  band_gram
  S-D      +0.1605    +0.1771    6.87    +0.1771
  B-D      +0.1752    +0.2412    3.67    +0.2412
  B-C      +0.1682    +0.1459    2.94    +0.1459
  K-C      +0.1331    +0.1057    3.40    +0.1057
  S-Y      +0.1266    +0.0619    4.48    +0.0619
```

### Thinking

 The five strongest universal edges are showing up cleanly with band consensus rankings, and notably the B-D band has even stronger consensus than the overall model average, which suggests the 4-14B model band is where this compositional structure really solidifies. I'm verifying that the band model indexing aligned correctly—the band_gram values match what I'm getting from the averaged Gram matrix, and the consensus scores came through from the per-model calculations. The values match perfectly across both computation paths, which confirms the consensus per-model values are indeed using the frac-0.40 grams. Now I'm ready to commit the infrastructure patch and harvest prescription—this reformulation of the approach (shifting from GPU-bound to CPU-prescription now with deferred GPU, plus the centroid-save fix) warrants a 🔄 shift symbol. After committing, I'll move on to task 3 covering documentation and state.

For the commit, I need to stage the centroid-save fix and ruff cleanup in the combinator relationship map script, the harvest fold script, and the prescription results file—but not the session notes.

## Assistant

The prescription is produced — and note the cross-check: the band-averaged npz Grams (`band_gram` column) match the consensus `per_model` band averages exactly (S-D 0.1771=0.1771, B-D 0.2412=0.2412), confirming two independent code paths agree. The 4–14B band shows the composition skeleton even *stronger* than the full pool (B-D +0.24 vs +0.175), validating "harvest from the 4–14B band."

Committing the infra patch + prescription (code+results).

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/combinator_relationship_map.py scripts/experiments/combinator_harvest_fold.py results/combinator-harvest-fold/prescription.json && git status -s",
  "operation": "add",
  "summary": "stage harvest phase-0"
}
```

**Summary:** Git add: stage harvest phase-0

**Output:**
```
Exit code: 0
Stdout:
A  results/combinator-harvest-fold/prescription.json
A  scripts/experiments/combinator_harvest_fold.py
M  scripts/experiments/combinator_relationship_map.py
?? mementum/knowledge/chats/session-219.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "🔄 harvest-fold phase 0: CPU prescription + preserve discarded centroids\n\n- Reframed the harvest-fold after mapping its integration points: the original\n  \"Procrustes-align consensus centroids into v15 frame\" is not runnable yet because\n  (1) per-model centroid VECTORS were computed but discarded (only the relational\n  Gram persisted), and (2) v15 has no combinator Gram and all producing steps are\n  GPU/MLX forward passes that would contend with the multi-day main:1 training\n  (s219 stalled it). main:1 stays UNTOUCHED.\n- INFRA FIX: combinator_relationship_map.py now saves the full-dim best-layer\n  combinator centroids (9 x d_ff) + best-layer index to the npz (centroids_cmr_best).\n  The raw material for align-before-fold; takes effect on the next (deferred) GPU\n  run. (+ removed a stale unused noqa.)\n- NEW combinator_harvest_fold.py (phase 0, CPU-only): emits the harvest PRESCRIPTION\n  = band-consensus Gram over the s220 4-14B harvest band + ranked positive universal\n  edges (S-D, B-D, B-C, K-C, S-Y) with per-band consensus/reliability. No forward\n  passes — pure re-reduction of measured Grams. Cross-check: band-averaged npz Grams\n  == consensus per_model band averages exactly. The 4-14B band shows the composition\n  skeleton STRONGER than the full pool (B-D +0.24 vs +0.175).\n- GPU phases (v15 Gram, Procrustes, WHNF-verify, PPL) explicitly deferred + recorded\n  in prescription.json deferred_gpu_phases.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -1",
  "operation": "commit",
  "summary": "commit harvest phase-0"
}
```

**Summary:** Git commit: commit harvest phase-0

**Output:**
```
Exit code: 0
Stdout:
[main e48389e] 🔄 harvest-fold phase 0: CPU prescription + preserve discarded centroids
 3 files changed, 375 insertions(+), 1 deletion(-)
 create mode 100644 results/combinator-harvest-fold/prescription.json
 create mode 100644 scripts/experiments/combinator_harvest_fold.py
e48389e 🔄 harvest-fold phase 0: CPU prescription + preserve discarded centroids
```

### Thinking

 Phase 0 is committed, and I'm moving into task 3 to document the reformulated harvest-fold procedure on the knowledge page. Michael's approval of the construct itself covers the documentation, and since I've already committed the relevant sections with approval, I'm continuing with updating the knowledge page to reflect the reformulated procedure and the phase split.

## Assistant

Phase 0 committed (`e48389e`). Completing task 2, moving to documentation + state handoff.Updating the knowledge page's harvest-fold lead with the reformulation and phase split (within the approved harvest-fold scope).

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "### Open leads from s220\n1. **Construct the harvest fold** (register: topological/routing → functional) — now\n   the priority: take the universal positive edges (B–D +0.175, B–C +0.168, K–C\n   +0.133, S–D +0.161, S–Y +0.127), Procrustes-align consensus centroids into v15's\n   base frame, WHNF-verify each vs main:1's contractive operator (Exp-B acceptance),\n   measure downstream PPL vs base. Falsifiable: does verified ecosystem-consensus add\n   beyond the universal crystal we already hold? Harvest from the 4–14B band.\n2. **main:1 step_002000** → does Δx→ε and CE hold below 8.71 (adaptive halting).\n3. Detect map/fold directions (s219 lead #3).",
  "new_content": "### Harvest fold — reformulated + phased (s220)\n\nMapping the integration points (s220) surfaced that the harvest fold as sketched\n(\"Procrustes-align consensus centroids into v15's base frame\") is NOT runnable\nas-is, for two reasons:\n\n- **Data reality.** `consensus.json` and the per-model `.npz` contain ONLY the\n  relational 9×9 Grams — the per-combinator centroid VECTORS (9 × d_ff) were\n  computed in `combinator_relationship_map.py` but **discarded**. Procrustes needs\n  point clouds (centroids), not a Gram. **Fixed** (`e48389e`):\n  `combinator_relationship_map.py` now saves `centroids_cmr_best` (9 × d_ff) +\n  `centroids_best_layer` to the npz — but this only takes effect on the **next**\n  (GPU) run of that script.\n- **Frame + compute.** v15 has **no** combinator Gram/centroids yet, and\n  `combinator_relationship_map.py` is HF-only (`AutoModelForCausalLM`, hooks\n  `gate_proj`); v15 is an MLX ternary model (`ffn_gate_plate_a/c`). Producing v15's\n  Gram, the WHNF-verify (`exp_b_self_verifying_acceptance.py::forward_metrics`), and\n  PPL are ALL GPU/MLX forward passes → would **contend with main:1** (s219 stall).\n\nSo the harvest fold is split into phases:\n\n- **Phase 0 — PRESCRIPTION (CPU, DONE `e48389e`):** `combinator_harvest_fold.py`\n  emits `results/combinator-harvest-fold/prescription.json` = the band-consensus\n  Gram over the 4–14B harvest band + the ranked positive universal edges to\n  reinforce. Ranked by band-consensus × reliability: **S–D, B–D, B–C, K–C, S–Y**.\n  The 4–14B band shows the composition skeleton STRONGER than the full pool\n  (B–D band +0.24 vs all +0.175) — concrete confirmation that the harvest band is\n  the right place to mine. No forward passes; pure re-reduction of measured Grams.\n- **Phase 1 — v15 Gram (DEFERRED, GPU):** build `combinator_relationship_map_v15.py`\n  (MLX/ternary: load via `create_model_with_deltas(V15Config())` + `load_weights` +\n  `reduce_all_deltas`; hook `ffn_gate_plate_a/c`; save `centroids_cmr_best`). Run on\n  `checkpoints/v15-td-outer-k2-fp5-5k/step_NNNN/model.npz` (READ-ONLY) once main:1\n  completes/pauses → gives v15's own Gram + centroids = the target frame.\n- **Phase 2 — align (CPU, after Phase 1):** Procrustes-align the consensus/harvest\n  centroids into v15's frame (in 9-d combinator-label space; full-dim is\n  cross-architecture-incommensurable). Build a fold direction per positive edge as\n  the signed difference of v15's OWN centroids, guided by the prescription.\n- **Phase 3 — verify + fold (DEFERRED, GPU):** WHNF-verify each direction via\n  `forward_metrics` (accept iff Δx_conv does not rise); fold survivors via\n  `DeltaTernaryLinear.reduce()`; measure downstream PPL vs base. **Falsifiable:**\n  does verified ecosystem-consensus add beyond the universal crystal we already hold?\n\n### Open leads from s220\n1. **Phase 1 of the harvest fold** (above) — the priority once main:1 frees the GPU.\n2. **main:1 step_002000** → does Δx→ε and CE hold below 8.71 (adaptive halting).\n3. Detect map/fold directions (s219 lead #3)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I need to add the new script files to the Files table, so I'm appending rows for combinator_harvest_fold.py and the prescription file.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "| `results/combinator-map-consensus/scale.json` | s220 verdict: skeleton rises r=+0.78, skel-rec gap flat r=+0.36, saturates ~4-14B |",
  "new_content": "| `results/combinator-map-consensus/scale.json` | s220 verdict: skeleton rises r=+0.78, skel-rec gap flat r=+0.36, saturates ~4-14B |\n| `scripts/experiments/combinator_harvest_fold.py` | **s220 harvest fold phase 0 (CPU):** band-consensus Gram + ranked positive edges = the harvest prescription |\n| `results/combinator-harvest-fold/prescription.json` | s220 prescription: edges S-D,B-D,B-C,K-C,S-Y over the 4-14B band; deferred GPU phases listed |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

## Assistant

Now updating state.md with the s220 harvest-fold progress and the exact deferred GPU plan, then committing both.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> not extend the gap → the harvestable skeleton is COMPLETE by mid-scale, no need to\n> chase the largest models. **COMMITTED** `c27741c` (32B map+npz, extended\n> consensus.json, scale.json, scale instrument). **NOT yet committed (PROPOSED,\n> pending Michael):** knowledge update to `consensus-delta-folding.md` §s220\n> (scale-saturation finding) + this state. **▶ FIRST ACTION NEXT SESSION (declare\n> register):** (1) check main:1 step_002000 ckpt → does Δx→ε and CE hold below 8.71\n> (build adaptive halting: stop when Δx<ε ≡ WHNF)? (2) CONSTRUCT THE HARVEST FOLD\n> (topological/routing→functional): take the universal positive edges (B–D +0.175,\n> B–C +0.168, K–C +0.133, S–D +0.161, S–Y +0.127), Procrustes-align consensus\n> centroids into v15 base frame, WHNF-verify each vs main:1's contractive operator\n> (Exp-B acceptance), measure downstream PPL vs base — does verified consensus add\n> beyond the universal crystal? (3) Strengthen Exp B on main:1 step-2000 (s218\n> action 2). **main:1 stays UNTOUCHED.**",
  "new_content": "> not extend the gap → the harvestable skeleton is COMPLETE by mid-scale, no need to\n> chase the largest models. **COMMITTED** `c27741c` (32B map+npz, extended\n> consensus.json, scale.json, scale instrument), `0089087` (knowledge §s220,\n> APPROVED by Michael).\n> **★ HARVEST FOLD STARTED — PHASE 0 DONE (CPU), GPU PHASES DEFERRED.** Michael\n> approved \"construct the harvest fold.\" Explorer mapped the integration points →\n> the original \"Procrustes-align consensus centroids into v15 frame\" is NOT runnable\n> as-is: (a) the per-model centroid VECTORS were computed but DISCARDED (only the\n> relational 9×9 Gram persisted; consensus.json has no centroids); (b) v15 has NO\n> combinator Gram/centroids and `combinator_relationship_map.py` is HF-only\n> (`AutoModelForCausalLM`, hooks gate_proj) while v15 is MLX ternary\n> (ffn_gate_plate_a/c); (c) ALL producing steps (v15 Gram, WHNF-verify, PPL) are\n> GPU/MLX forward passes that would CONTEND with main:1 (s219 stall). So the fold is\n> PHASED:\n> - **Phase 0 PRESCRIPTION (CPU, DONE `e48389e`):** `combinator_harvest_fold.py` →\n>   `results/combinator-harvest-fold/prescription.json` = band-consensus Gram over\n>   the 4–14B band + ranked positive edges **S–D, B–D, B–C, K–C, S–Y**. The 4–14B\n>   band shows the composition skeleton STRONGER than the full pool (B–D band +0.24\n>   vs all +0.175). Cross-check: band-averaged npz Grams == consensus per_model band\n>   averages EXACTLY. + INFRA FIX in `combinator_relationship_map.py`: now saves\n>   `centroids_cmr_best` (9×d_ff) to the npz (the discarded data; effective on next\n>   GPU run).\n> - **Phase 1 v15 Gram (DEFERRED, GPU):** build `combinator_relationship_map_v15.py`\n>   (MLX: `create_model_with_deltas(V15Config())` + `load_weights` +\n>   `reduce_all_deltas`; hook `ffn_gate_plate_a/c`; save centroids). Run on a v15\n>   ckpt READ-ONLY. Phase 2 (CPU): Procrustes-align in 9-d label space + build fold\n>   directions from v15's OWN centroids. Phase 3 (GPU): WHNF-verify via\n>   `exp_b_self_verifying_acceptance.py::forward_metrics` (accept iff Δx_conv doesn't\n>   rise) → fold survivors via `DeltaTernaryLinear.reduce()` → PPL vs base.\n> **COMMITTED** `e48389e` (phase 0 + centroid-save), knowledge reformulation pending\n> in this commit batch. **NOT yet committed (this batch, APPROVED scope):** knowledge\n> harvest-fold reformulation + this state.\n> **▶ FIRST ACTION NEXT SESSION (declare register; main:1 UNTOUCHED):**\n> (1) Check main:1: has step_002000 landed (`ls checkpoints/v15-td-outer-k2-fp5-5k/`,\n>   `tail /tmp/v15_outer_k2_fp5_5k.log`)? Read Δx/CE trajectory → does Δx→ε and CE\n>   hold below 8.71 (then build adaptive halting: stop when Δx<ε ≡ WHNF)?\n> (2) **Harvest fold Phase 1 (register topological/routing→functional) ONLY IF main:1\n>   has FREED THE GPU** (completed/paused) — else DEFER: build\n>   `combinator_relationship_map_v15.py`, produce v15's Gram+centroids, then Phases\n>   2–3 (align → WHNF-verify → fold → PPL). Falsifiable: does verified\n>   ecosystem-consensus add beyond the universal crystal? Prescription is ready at\n>   `results/combinator-harvest-fold/prescription.json`.\n> (3) Strengthen Exp B on main:1 step-2000 (s218 action 2). **main:1 stays UNTOUCHED.**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: git (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"import json;json.load(open('results/combinator-harvest-fold/prescription.json'));print('prescription.json valid')\" && git add mementum/knowledge/explore/consensus-delta-folding.md mementum/state.md && git commit -F - <<'EOF'\n🌀 session-220: harvest fold phase 0 + reformulation; state handoff\n\n- consensus-delta-folding.md: harvest fold reformulated + phased (data-reality:\n  centroids were discarded; frame+compute: v15 Gram is GPU-bound, defer). Phase 0\n  DONE (CPU prescription S-D,B-D,B-C,K-C,S-Y over 4-14B band); Phases 1-3 GPU,\n  deferred until main:1 frees the GPU.\n- state.md: s220 harvest-fold progress + exact deferred GPU invocation + first\n  actions for next session. main:1 UNTOUCHED.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit log --oneline -6",
  "operation": "commit",
  "summary": "commit reformulation + state"
}
```

**Summary:** Git commit: commit reformulation + state

**Output:**
```
command must start with 'git' or 'gh' (optionally preceded by 'cd <path> &&')
```

### Thinking

 I need to work around the git tool's command restrictions—it only accepts commands starting with 'git' or 'gh', so I can't chain multiple operations together. Since I already know the prescription.json file is valid from the earlier script run, I'll skip the validation step and just commit the changes using the git tool directly with a message file to avoid heredoc complications.

## Assistant

Validation was extraneous (the script already wrote valid JSON). Let me commit via the git tool properly.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "🌀 session-220: harvest fold phase 0 + reformulation; state handoff\n\n- consensus-delta-folding.md: harvest fold reformulated + phased (data-reality:\n  centroids were discarded; frame+compute: v15 Gram is GPU-bound, defer). Phase 0\n  DONE (CPU prescription S-D,B-D,B-C,K-C,S-Y over 4-14B band); Phases 1-3 GPU,\n  deferred until main:1 frees the GPU.\n- state.md: s220 harvest-fold progress + exact deferred GPU invocation + first\n  actions for next session. main:1 UNTOUCHED.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/consensus-delta-folding.md mementum/state.md && git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -6",
  "operation": "commit",
  "summary": "commit reformulation + state"
}
```

**Summary:** Git commit: commit reformulation + state

**Output:**
```
Exit code: 0
Stdout:
[main b05d32c] 🌀 session-220: harvest fold phase 0 + reformulation; state handoff
 2 files changed, 86 insertions(+), 17 deletions(-)
b05d32c 🌀 session-220: harvest fold phase 0 + reformulation; state handoff
e48389e 🔄 harvest-fold phase 0: CPU prescription + preserve discarded centroids
0089087 🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale
47c3713 🌀 session-220: state — scale axis completed; function shape saturates mid-scale
c27741c 💡 combinator function shape saturates mid-scale; skel/rec gap does NOT widen
bbf92f2 🌀 session-219: state — 30B-A3B MoE incompatible with dense-FFN instrument; scale axis is dense 0.6B->32B
```

### Thinking

 Now I'm wrapping up task 3 and doing a final verification that main:1 is still running properly—my changes were CPU-only so nothing should have been affected, but I want to confirm before closing everything out.

## Assistant

All committed. Let me verify main:1 is still healthy (a final read-only check — all my work was CPU-only, no MLX), then close out the tasks.

### Tool Call: shell_command (failed)


```json
{
  "command": "tmux capture-pane -p -t main:1 2>/dev/null | tail -3 ; echo \"--- checkpoints ---\" ; ls -1 /Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/step_* -d 2>/dev/null"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 2>/d...

**Output:**
```
Exit code: 1
Stdout:
2.69e-04 | gnorm 102.99 | 360 tok/s | 🔓 td=124488 Δ=0.047 etch=76×1638 adam_decay=29272 Δx=[0.29779] fp=0.0887 | 108533
s

--- checkpoints ---
/Users/mwhitford/src/verbum/checkpoints/v15-td-outer-k2-fp5-5k/step_001000:
delta_plates.npz
model.npz
optimizer.npz
state.json
```

### Thinking

 The main process is still running and making progress around step 1430, though the next checkpoint hasn't landed yet. The directory listing returned an error because it expanded into the only existing checkpoint folder, but that's expected. I'm clearing out the task now that everything's complete.

## Assistant

main:1 is healthy and stepping (now ~step 1430+, untouched throughout — all my work was CPU-only). Tasks complete. Clearing the list.## Session 220 complete

**Orient → executed the declared first action → constructed the harvest fold (phase 0).** Everything CPU-only; **main:1 untouched** and verified still stepping.

### What landed (6 commits)
1. **`c27741c`** — Qwen3-32B map + 10-model consensus + `combinator_map_scale.py`. **Finding:** skeleton binding rises with scale (r=+0.78) but the **skel−rec gap does NOT widen** (r=+0.36); shape **saturates ~4–14B**, 32B regresses. Answers s217's scale question.
2. **`47c3713`, `0089087`** — state + knowledge §s220 (approved).
3. **`e48389e`** — harvest-fold **phase 0**: infra fix (`combinator_relationship_map.py` now *saves* the previously-discarded centroids) + `combinator_harvest_fold.py` emitting the **prescription** (edges S-D, B-D, B-C, K-C, S-Y over the 4–14B band).
4. **`b05d32c`** — harvest-fold reformulation + state handoff.

### Key reframe (honest finding from the integration mapping)
The harvest fold as originally sketched **can't be run yet**: the per-model centroid vectors were discarded (only relational Grams survived), v15 has no combinator Gram, and all producing steps are GPU/MLX forward passes that would contend with main:1. So it's now **phased** — Phase 0 (CPU prescription) done; Phases 1–3 (v15 Gram → Procrustes → WHNF-verify → PPL) **deferred until main:1 frees the GPU**, with the exact resumable plan written into `state.md`.

### Live jobs
- **main:1:** alive, ~step 1430/5000, untouched. `step_002000` pending (~3 days out).
- **main:2:** idle (scale sweep finished).

**Next session's first action** (recorded in state): check main:1 `step_002000` trajectory (does Δx→ε, CE hold <8.71); run harvest-fold Phase 1 **only if** main:1 has freed the GPU, else defer. The prescription is ready at `results/combinator-harvest-fold/prescription.json`.

One note: I left the human-only `mementum/knowledge/chats/session-219.md` untracked and untouched, per protocol — that's yours to manage.

## User

you can run things in my tmux main:2 window that use GPU, we have the VRAM and it will just be slower because training is running.


### Thinking

 Michael's cleared me to run GPU work in tmux main:2 since there's sufficient VRAM available, which unblocks the harvest-fold GPU phases. I need to keep main:1 (the training process) completely untouched while running my own GPU work separately. The previous GPU contention issue that stalled main:1 was actually from load contention during a large model download, not VRAM pressure, so I can safely proceed with this approach.

The real blocker is building `combinator_relationship_map_v15.py` — a new instrument that adapts the existing map script for v15 by adding MLX hooks to capture gate pre-activation signs and compute v15's own centroids and Gram matrix. This is essential because the harvest-fold premise requires folding ecosystem-consensus structure into v15 using v15's own centroids as the foundation, which means I need Phase 1 to generate those centroids first before I can determine what to inject.

I should build this carefully myself rather than delegate it — it's the core scientific instrument and requires deep understanding of v15's model structure, MLX hooking, and the existing map script's centroid/Gram logic. But before writing the script, I need to study v15model.py directly to understand how to capture the routing register, then build and smoke-test on CPU before launching the full 535-probe GPU run in main:2 using the async discipline Michael recommended.

Let me start by reading the key source files: v15model.py's FFN gate plate definitions and forward pass, the existing map script's collect and helper functions, and the relevant TernaryLinear code from td_delta.py to understand what I'm working with.

## Assistant

Good — that unblocks the harvest-fold GPU phases. I'll run my GPU work in **main:2** and keep **main:1** (the training process) untouched. Given s219's stall was a *download/load* contention rather than VRAM, and you confirm VRAM headroom, this should be safe (just slower for both).

The blocker is Phase 1: I need to build a **v15-adapted** combinator map (the existing one is HF-only). Let me plan, study the v15 internals for ground truth, build + smoke-test on CPU/tiny, then launch the full 535-probe run in main:2.

### Thinking

 Now I'm moving forward with the revised approach and beginning to work through the first task by examining the source files.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py",
  "line_offset": 100,
  "limit": 160
}
```

**Summary:** Reading combinator_relationship_map.py (100-260)

**Output:**
```
            ps = [ps[i] for i in idx]
        prompts.extend(ps)
        labels.extend([c] * len(ps))
    return prompts, np.array(labels)


# ---- model introspection ----------------------------------------------------
def find_gate_modules(model):
    hits = []
    pat = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod, m.group(2)))
    hits.sort(key=lambda x: x[0])
    return [(li, name, mod) for (li, name, mod, k) in hits]


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


# ---- capture ----------------------------------------------------------------
@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length, want_layers):
    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]

    n = len(prompts)
    hidden = None
    gate = {li: None for li in want}
    plen = np.empty(n, np.int32)
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True,
                            max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True)
            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
            if hidden is None:
                hidden = np.empty((n, h.shape[0]), np.float32)
            hidden[i] = h
            plen[i] = int(enc["input_ids"].shape[1])
            for li in want:
                g = buf[li]
                if gate[li] is None:
                    gate[li] = np.empty((n, g.shape[0]), np.float32)
                gate[li][i] = g
            del out
            if (i + 1) % 50 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return hidden, gate, plen, n_layers


# ---- centroid / Gram / silhouette -------------------------------------------
def cmr(X):
    """Common-mode removal: subtract per-feature mean across probes."""
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def centroids(X, labels):
    """Per-combinator mean vector. Returns [K x d] in CRYSTAL order."""
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        C[j] = X[m].mean(axis=0)
    return C


def gram(C):
    """Cosine Gram matrix between centroids."""
    U = np.array([unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def silhouette(X, labels):
    """Mean over probes of [cos(x, own centroid) - max_other cos(x, centroid)].
    Centroids computed leave-one-combinator-balanced (all probes; bias small at
    n>=50). High -> combinators are real clusters in this register."""
    C = centroids(X, labels)
    U = np.array([unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T                       # [N x K]
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    best_other = other.max(axis=1)
    return float(np.mean(own - best_other))


def silhouette_null(X, labels, n_perm=1000, seed=0):
    obs = silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = silhouette(X, rng.permutation(labels))
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def classical_mds(D, k=2):
    """Classical (Torgerson) MDS from a distance matrix -> [n x k] coords."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    w, V = w[order][:k], V[:, order][:, :k]
    w = np.clip(w, 0, None)
    return V * np.sqrt(w + 1e-30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--limit-per", type=int, default=0,
                    help="cap probes per combinator (smoke test)")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    prompts, labels = load_probes(args.limit_per, args.seed)
    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}
    log(f"[{args.model}] {len(prompts)} crystal probes  {counts}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)

[CONTENT TRUNCATED] Showing lines 101 to 260 of 386 total lines. Use line_offset=260 parameter to read more content.
```

### Thinking

 I've got the helper functions set up and I'm capturing the gate pre-activation from the forward hooks—specifically the last token's output from gate_proj before the SiLU activation. For Qwen's SwiGLU architecture, this gate_proj output represents the gate pre-activation, and I'm tracking this through the routing register.

Now I need to find the equivalent for v15. The explorer mentioned hooking ffn_gate_plate_a/c, so I'm going to check v15model.py to understand how the FFN structure works and where to capture the analogous gate signal. I'll need to look at the top of the mapping script for the imports, constants like CRYSTAL and LAYER_FRACS, and the load_probes function, then examine the FFN forward pass in v15model.py.

## Assistant

Now the v15 model internals — the FFN gate plates and forward pass, plus the top of the map script (probes loader, constants).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map.py",
  "line_offset": 0,
  "limit": 100
}
```

**Summary:** Reading combinator_relationship_map.py (0-100)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Combinator relationship map — what is the SHAPE of the function space?

THE QUESTION (session 217, Michael):
  We have found "function-like things" = the combinator basis
  (K I B C S D W Y WHNF). What are their SEMANTIC RELATIONSHIPS? Is there a
  map/fold? What do the functions look like — what is their shape?

THE INSTRUMENT (this script):
  Measure each combinator's CENTROID in the ROUTING register and build the
  pairwise relationship (Gram) matrix = the literal "map of the functions".

    routing(x) = sign( FFN gate pre-activation )        (s203: gate_proj sign
                                                          carries routing topology)
    centroid_k = mean over probes labelled k of routing(x), AFTER common-mode
                 removal (subtract the per-feature mean across all probes — kills
                 the universal structured-language crystal so the DIFFERENCES
                 between combinators show, not their shared backbone).
    Gram[j,k]  = cosine(centroid_j, centroid_k)          <- THE MAP

  Why this register: in RAW cosine the crystal is a rank-~1 common mode
  (5d-crystal-lattice REFUTED, s211); the combinator structure lives in the
  sign/routing register after CMR (separation p=5e-4, ~65% topological). So the
  shape of the function space is only visible here.

  Controls:
    - hidden_full / hidden_cmr : raw residual register (expect the common-mode mush)
    - route_full               : routing without CMR (common mode still present)
    - route_cmr                : routing with CMR        <-- KEY (the real map)
    - shuffled-label null       : permute combinator labels, recompute silhouette
                                  -> is the clustering real?

  Outputs per layer-fraction + a best layer chosen by silhouette z. Classical
  MDS + centroid-PCA give the 2D embedding (the picture). Cross combinator
  Gram, silhouette, null, and embedding all saved.

Usage:
  uv run python scripts/experiments/combinator_relationship_map.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.library import crystal_probes

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"

# the 9 crystal combinators, in a fixed canonical order
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]

# depth-normalized layer fractions (align models of different depth)
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- probes -----------------------------------------------------------------
def load_probes(limit_per: int = 0, seed: int = 0):
    """All crystal probes (K I B C S D W Y WHNF), grouped order preserved.
    limit_per: optionally cap probes per combinator (for smoke tests)."""
    probes = crystal_probes()
    by = {c: [] for c in CRYSTAL}
    for p in probes:
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    rng = np.random.default_rng(seed)
    prompts, labels = [], []
    for c in CRYSTAL:
        ps = by[c]
        if limit_per and limit_per < len(ps):
            idx = sorted(rng.permutation(len(ps))[:limit_per])

[CONTENT TRUNCATED] Showing lines 1 to 100 of 386 total lines. Use line_offset=100 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== v15model.py structure (ffn / gate / forward) ===\" && grep -n \"ffn_gate_plate\\|class \\|def __call__\\|def forward\\|stack_a\\|stack_c\\|shared_stride\\|_last_ce\\|_last_outer_deltas\\|n_outer\\|gate\\|silu\\|class V15Config\\|d_ff\\|d_model\\|FFN\\|class .*Stack\\|class .*Plate\" scripts/v15/v15model.py | head -80"
}
```

**Summary:** $ echo "=== v15model.py structure (ff...

**Output:**
```
Exit code: 0
Stdout:
=== v15model.py structure (ffn / gate / forward) ===
105:class V15Model(nn.Module):
111:      3. Collect all 8 pass deltas → S5Reweight → meta-gates
113:      5. Final reweighting: x_final = x_c - ungated + gated
124:        d = cfg.d_model
138:        # ── Per-stack FFN plates ───────────────────────────────
139:        self.ffn_key_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
140:        self.ffn_gate_plate_a = TernaryLinear(d, cfg.d_ff, pre_norm=False)
141:        self.ffn_value_plate_a = TernaryLinear(cfg.d_ff, d, pre_norm=False)
142:        self.ffn_key_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
143:        self.ffn_gate_plate_c = TernaryLinear(d, cfg.d_ff, pre_norm=False)
144:        self.ffn_value_plate_c = TernaryLinear(cfg.d_ff, d, pre_norm=False)
147:        self.shared_stride_stack = FibonacciStrideStack(cfg)
150:        self.stack_a = StrideStackVSM(
151:            cfg, cfg.stack_a_bands,
152:            self.ffn_key_plate_a, self.ffn_gate_plate_a, self.ffn_value_plate_a,
153:            self.shared_stride_stack,
156:        self.stack_c = StrideStackVSM(
157:            cfg, cfg.stack_c_bands,
158:            self.ffn_key_plate_c, self.ffn_gate_plate_c, self.ffn_value_plate_c,
159:            self.shared_stride_stack,
284:    def forward(
305:        # shared VSM sweep n_outer times, feeding x_c back as the next input.
307:        # point (WHNF). n_outer=1 is identical to the single-sweep baseline.
308:        # _last_outer_deltas records ‖x_c^{(k)} − x_c^{(k-1)}‖/‖x_c^{(k-1)}‖ —
310:        n_outer = int(getattr(self, "_n_outer_passes", 1))
315:        for _k in range(n_outer):
316:            x_a, alg_a, deltas_a, gates_a = self.stack_a(x_in, downstream_alg=alg_for_a)
317:            x_c, alg_c, deltas_c, gates_c = self.stack_c(x_a)
334:        self._last_outer_deltas = outer_deltas
336:        # Aggregate the differentiable fixed-point term (None when n_outer<2).
350:        all_gates = gates_a + gates_c
383:        meta_gates = self.s5_reweight(all_deltas)
387:        effective_gates = meta_gates * override + 0.12 * (1.0 - override)
390:        total_ungated = all_deltas[0]
392:            total_ungated = total_ungated + all_deltas[i]
394:        total_gated = effective_gates[0] * all_deltas[0]
396:            total_gated = total_gated + effective_gates[i] * all_deltas[i]
398:        x_final = x_c - total_ungated + total_gated
409:                logits, targets, effective_gates, all_deltas,
415:            # with outer recurrence (n_outer≥2) and λ_fp>0.
428:        self, logits, targets, effective_gates, all_deltas,
442:        self._last_ce = mx.stop_gradient(ce_loss)
464:        # ── Parity + cross-zone (gated) ─────────────────────────
466:        parity_gate = mx.where(parity_loss > latch_threshold, 1.0, 0.0)
467:        cross_zone_gate = mx.where(cross_zone_loss > latch_threshold, 1.0, 0.0)
468:        parity_additive = cfg.parity_lambda * parity_loss * parity_gate
469:        cross_zone_additive = cfg.parity_lambda * cross_zone_loss * cross_zone_gate
498:    def __call__(self, tokens, targets=None):
514:    print(f"  d_model={cfg.d_model}  n_strides={cfg.n_strides}  n_passes={cfg.n_passes}")
517:    print(f"  band_sizes_A={[b[1]-b[0] for b in cfg.stack_a_bands]}")
522:    print(f"  ✓ (d={cfg.d_model}, {cfg.n_passes} passes, {N_STACKS} stacks, A+C)")
523:    print(f"  FibonacciStrideStack: {len(model.shared_stride_stack.layers)} layers")
539:    print(f"  CE: {model._last_ce.item():.4f}")
```

### Thinking

 Looking at the v15 FFN architecture, it uses TernaryLinear gate plates (`ffn_gate_plate_a` and `ffn_gate_plate_c`) that transform dimensions through `d → d_ff`, with the actual forward pass routed through StrideStackVSM stacks. The gate pre-activation is essentially the output from `ffn_gate_plate_a` before any nonlinearity is applied, but the crucial distinction is that v15 doesn't structure itself as a simple stack of independent layers.

Instead, v15 has two FFN stacks (stack_a and stack_c) plus a shared attention component (FibonacciStrideStack), with an outer recurrence loop running n_outer times. The "routing register" comes from the sign of the FFN gate plate output. Since v15 only has these 2 gate plates rather than many layers like the HF approach, I need to understand how StrideStackVSM actually applies the gate plate across its strides and bands.

For the harvest fold, the key insight is that I should capture the sign of `ffn_gate_plate_c` at the last token for each probe, giving me a routing matrix that maps to combinators. This produces centroids in the same d_ff=5120 space where exp_b injects the flips, making it a cleaner approach than the multi-layer HF method since v15's injection target is directly the ffn_gate_plate module.

The challenge is that the gate plate runs inside StrideStackVSM across multiple bands and strides, and the outer recurrence changes the input each time. To get a clean centroid, I need to capture the gate pre-activation at a consistent point — the simplest approach is monkeypatching the gate plate's `__call__` method to stash its output on the final outer pass, since MLX doesn't have torch-style hooks. I need to examine how TernaryLinear and StrideStackVSM use the gate plate and what the input shapes are, then look at exp_b's loader and forward_metrics to understand the full context.

## Assistant

v15's FFN structure is unusual (stack_a/stack_c + shared stride stack + outer recurrence), not a per-layer transformer. The key insight: exp_b injects into `stack_c.ffn_gate_plate`, so the natural capture register is `sign(ffn_gate_plate_c output)` at the last token — the *same* d_ff=5120 space where the fold will be injected. Let me read the forward path and module definitions to capture it correctly.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/v15model.py",
  "line_offset": 283,
  "limit": 60
}
```

**Summary:** Reading v15model.py (283-343)

**Output:**
```
    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape
        cfg = self.cfg

        # ── Embed ─────────────────────────────────────────────
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x

        # ── Bottom-up algedonic from previous step ─────────────
        if self._prev_alg_c is not None:
            alg_for_a = self.alg_combiner_a(self._prev_alg_c)
        else:
            alg_for_a = None

        # ── Sequential: A → C, optionally iterated (outer recurrence) ──
        # session 214 probe (explore/vsm-outer-recurrence.md): re-run the SAME
        # shared VSM sweep n_outer times, feeding x_c back as the next input.
        # Iterating one typed-reduction operator ≡ β-reduction toward a fixed
        # point (WHNF). n_outer=1 is identical to the single-sweep baseline.
        # _last_outer_deltas records ‖x_c^{(k)} − x_c^{(k-1)}‖/‖x_c^{(k-1)}‖ —
        # the fixed-point convergence curve (shrinking ⇒ contractive ⇒ free depth).
        n_outer = int(getattr(self, "_n_outer_passes", 1))
        x_in = x
        prev_xc = None
        outer_deltas = []   # stop-grad relative Δx (logging / fixed-point curve)
        fp_terms = []       # DIFFERENTIABLE squared relative Δx (contractivity loss)
        for _k in range(n_outer):
            x_a, alg_a, deltas_a, gates_a = self.stack_a(x_in, downstream_alg=alg_for_a)
            x_c, alg_c, deltas_c, gates_c = self.stack_c(x_a)
            if prev_xc is not None:
                d = mx.sqrt(mx.mean((x_c - prev_xc) ** 2))
                nrm = mx.sqrt(mx.mean(prev_xc ** 2)) + 1e-8
                outer_deltas.append(mx.stop_gradient(d / nrm))
                # Fixed-point / holographic-contractivity loss (s214): pull each
                # sweep's output onto its (detached) input → x_c becomes a fixed
                # point of the sweep → the iterated map is contractive toward the
                # stored crystal pattern (WHNF). Target detached so the gradient
                # trains the operator to converge, not the state to flee; CE on
                # the final x_c guards against the trivial constant fixed point.
                tgt = mx.stop_gradient(prev_xc)
                fp_terms.append(
                    mx.mean((x_c - tgt) ** 2) / (mx.mean(tgt ** 2) + 1e-8)
                )
            prev_xc = x_c
            x_in = x_c
        self._last_outer_deltas = outer_deltas

        # Aggregate the differentiable fixed-point term (None when n_outer<2).
        if fp_terms:
            fp_term = fp_terms[0]
            for t in fp_terms[1:]:
                fp_term = fp_term + t
            fp_term = fp_term / len(fp_terms)
        else:
            fp_term = None

[CONTENT TRUNCATED] Showing lines 284 to 343 of 571 total lines. Use line_offset=343 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== where is StrideStackVSM / TernaryLinear / FibonacciStrideStack defined ===\" && grep -rn \"class StrideStackVSM\\|class TernaryLinear\\|class FibonacciStrideStack\\|def __call__\" scripts/v15/*.py | head -30"
}
```

**Summary:** $ echo "=== where is StrideStackVSM /...

**Output:**
```
Exit code: 0
Stdout:
=== where is StrideStackVSM / TernaryLinear / FibonacciStrideStack defined ===
scripts/v15/attention.py:248:    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
scripts/v15/attention.py:357:    def __call__(self, x: mx.array) -> mx.array:
scripts/v15/attention.py:421:class FibonacciStrideStack(nn.Module):
scripts/v15/attention.py:455:    def __call__(
scripts/v15/attention.py:543:        def __call__(self, x):
scripts/v15/components.py:54:    def __call__(self, delta: mx.array) -> mx.array:
scripts/v15/components.py:120:    def __call__(self, metrics_vector: mx.array) -> mx.array:
scripts/v15/components.py:227:    def __call__(
scripts/v15/components.py:319:    def __call__(
scripts/v15/components.py:380:    def __call__(
scripts/v15/components.py:458:    def __call__(
scripts/v15/components.py:497:    def __call__(self, pass_deltas: list[mx.array]) -> mx.array:
scripts/v15/components.py:623:        def __call__(self, crystal_sub, algs):
scripts/v15/crystal_base.py:420:    def __call__(self, embeddings: mx.array) -> dict[str, mx.array]:
scripts/v15/crystal.py:100:    def __call__(self, embeddings: mx.array) -> dict[str, mx.array]:
scripts/v15/model.py:334:    def __call__(self, x: mx.array) -> mx.array:
scripts/v15/model.py:380:    def __call__(self, x: mx.array) -> mx.array:
scripts/v15/model.py:521:    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
scripts/v15/model.py:590:    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
scripts/v15/model.py:651:    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
scripts/v15/model.py:771:    def __call__(
scripts/v15/stack_vsm.py:30:class StrideStackVSM(nn.Module):
scripts/v15/stack_vsm.py:114:    def __call__(
scripts/v15/stack_vsm.py:196:    def __call__(self, *signals: mx.array) -> mx.array:
scripts/v15/stack_vsm.py:295:        def __call__(self, x):
scripts/v15/td_delta.py:1297:    def __call__(self, x: mx.array) -> mx.array:
scripts/v15/td_delta.py:1667:        def __call__(self, x):
scripts/v15/ternary.py:201:class TernaryLinear(nn.Module):
scripts/v15/ternary.py:275:    def __call__(self, x: mx.array) -> mx.array:
scripts/v15/ternary.py:378:    def __call__(self, x: mx.array) -> mx.array:
```

### Thinking

 I need to dig into how StrideStackVSM's call method uses ffn_gate_plate, so I'm looking at the stack_vsm implementation and the TernaryLinear layer to understand the mechanics. I also want to trace through exp_b's forward metrics and how it perturbs the gate, but I'm thinking it might be more efficient to hand off the actual build to a general agent with the full spec once I nail down the capacity constraints.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/stack_vsm.py",
  "line_offset": 114,
  "limit": 85
}
```

**Summary:** Reading stack_vsm.py (114-199)

**Output:**
```
        self,
        x: mx.array,
        downstream_alg: Optional[mx.array] = None,
    ) -> tuple[mx.array, mx.array, list[mx.array], list[mx.array]]:
        """Run stack: attention + FFN per pass, S3 gated.

        Returns:
            x:              (B, L, d) output
            alg_summary:    (alg_dim,) health for controller
            pass_deltas:    list of (B, L, d) per-pass deltas (for S5Reweight)
            s3_gate_values: list of scalar gates per pass
        """
        ffn_mod, gate_mod = self._modulation(downstream_alg)

        raw_deltas = []
        pass_deltas = []
        s3_gate_values = []
        prev_delta = None

        for local_idx, band in enumerate(self.bands):
            x_before = x

            # Fibonacci stride-stack pass (±2 neighbor gathering)
            x = self._stride_stack(x, stride_range=band, reverse=self.is_descending)

            # FFN (SwiGLU with shared plates)
            ffn_in = self.ffn_norm(x)
            ffn_gate = nn.silu(self.ffn_gate_plate(ffn_in))
            ffn_key = self.ffn_key_plate(ffn_in)
            ffn_product = mx.clip(ffn_gate * ffn_key, -100.0, 100.0)
            ffn_out = self.ffn_value_plate(ffn_product)
            ffn_out = (ffn_out * self.ffn_scale + self.ffn_bias) * ffn_mod
            x = x + ffn_out

            raw_delta = x - x_before

            # S3 gate
            gate = self.s3_gates[local_idx](raw_delta) * gate_mod
            x = x_before + gate * raw_delta

            pass_delta = x - x_before
            raw_deltas.append(raw_delta)
            pass_deltas.append(pass_delta)
            s3_gate_values.append(gate)

            # S2 direction
            if local_idx < self.n_passes - 1:
                coherence = (S2Coordinator.coherence_factor(prev_delta, pass_delta)
                             if prev_delta is not None else mx.array(1.0))
                dir_signal = self.s2.direction_signal(pass_delta, local_idx)
                x = x + dir_signal * coherence

            prev_delta = pass_delta

        # Algedonic health
        metrics = self.algedonic.compute_metrics(s3_gate_values, pass_deltas, raw_deltas)
        alarm_factors = self.algedonic(metrics)

        summary_in = mx.concatenate([alarm_factors, metrics])
        if summary_in.shape[0] < self._alg_proj_padded:
            summary_in = mx.concatenate([
                summary_in, mx.zeros((self._alg_proj_padded - summary_in.shape[0],))])
        alg_summary = mx.tanh(self.alg_summary_proj(summary_in))

        return x, alg_summary, pass_deltas, s3_gate_values


class AlgedonicCombiner(nn.Module):
    """Combine multiple algedonic signals (bottom-up feedback).

    Stack A receives from C. Learns to merge multiple signals.
    Identical to v14 — algedonic topology is architecture-independent.
    """

    def __init__(self, n_sources: int, alg_dim: int = 32):
        super().__init__()
        in_dim = n_sources * alg_dim
        in_padded = ((in_dim + 15) // 16) * 16
        self._in_padded = in_padded
        self.combine_proj = nn.Linear(in_padded, alg_dim)

    def __call__(self, *signals: mx.array) -> mx.array:
        combined = mx.concatenate(list(signals))
        if combined.shape[0] < self._in_padded:
            combined = mx.concatenate([

[CONTENT TRUNCATED] Showing lines 115 to 199 of 307 total lines. Use line_offset=199 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/ternary.py",
  "line_offset": 201,
  "limit": 110
}
```

**Summary:** Reading ternary.py (201-311)

**Output:**
```
    """Linear layer with ternary routing topology via mx.quantized_matmul.

    Forward:
        scales, biases = f(gamma)          # fold gamma into quant params
        y = quantized_matmul(norm(x), W,   # AMX-accelerated 2-bit matmul
                             scales, biases,
                             transpose=True, group_size=64, bits=2)

    The ternary {-1, 0, +1} encoding maps to 2-bit int {0, 1, 2}:
        encoded = ternary + 1

    Per-channel gamma is folded into quantized_matmul's scales/biases:
        scales = gamma           → dequant multiplier
        biases = -gamma          → shift so 0-encoded → actual 0
    Dequant: gamma * {0,1,2} + (-gamma) = {-gamma, 0, +gamma} ✓

    The weight tensor (uint32, N × K//16) represents the ternary topology.
    It is EVOLUTIONARY — mutated via tournament selection, never touched
    by the gradient optimizer.  Its gradient is always zero.

    gamma is CONTINUOUS — trained normally by Adam.  mx.quantized_matmul
    supports autograd natively; no custom VJP is needed.

    Args:
        in_features:  input dimension  (must be divisible by 16)
        out_features: output dimension
        pre_norm:     if True, apply RMSNorm before projection
    """

    # Class-level quantization constants shared with mx.quantized_matmul
    group_size: int = 64
    bits: int = 2

    def __init__(self, in_features: int, out_features: int, pre_norm: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.pre_norm = pre_norm

        if pre_norm:
            self.norm = nn.RMSNorm(in_features)

        # weight:  (out_features, in_features//16) uint32  — packed ternary topology
        # gamma:   (out_features,) float32               — trainable per-channel scale
        wq_uint32, gamma = _ternary_init(out_features, in_features)
        self.weight = wq_uint32
        self.gamma = gamma

    def _get_scales_biases(self) -> tuple[mx.array, mx.array]:
        """Compute quantized_matmul scales/biases from per-channel gamma.

        For bits=2, group_size=64 and K = in_features:
            n_groups = K // group_size
            scales shape: (out_features, n_groups)
            biases shape: (out_features, n_groups)

        The dequant formula in quantized_matmul is:
            out = scales * quant_val + biases

        With quant_val ∈ {0, 1, 2} (encoded ternary) and:
            scales = gamma   (broadcast over groups)
            biases = -gamma  (shift so 0-encoded maps to 0 in output)

        We get:  {0*γ-γ, 1*γ-γ, 2*γ-γ} = {-γ, 0, +γ} ✓
        """
        n_groups = self.in_features // self.group_size
        # gamma: (out_features,) → expand to (out_features, n_groups)
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.out_features, n_groups),
        )
        return gamma_2d, -gamma_2d

    def __call__(self, x: mx.array) -> mx.array:
        if self.pre_norm:
            x = self.norm(x)

        # Cache input statistics for gradient-informed mutation.
        # stop_gradient keeps these out of the backward graph.
        # x shape: (B, T, in_features) or (in_features,) — mean over all but last dim.
        if x.ndim >= 2:
            reduce_axes = tuple(range(x.ndim - 1))
            self._x_abs_mean = mx.stop_gradient(mx.mean(mx.abs(x), axis=reduce_axes))
            self._x_mean = mx.stop_gradient(mx.mean(x, axis=reduce_axes))
        else:
            self._x_abs_mean = mx.stop_gradient(mx.abs(x))
            self._x_mean = mx.stop_gradient(x)

        scales, biases = self._get_scales_biases()
        # stop_gradient on weight: it's evolutionary (uint32, not differentiable).
        # Without this, MLX autograd would attempt a VJP through quantized_matmul
        # w.r.t. the uint32 weight argument and raise an error.
        w = mx.stop_gradient(self.weight)
        return mx.quantized_matmul(
            x,
            w,
            scales,
            biases,
            transpose=True,
            group_size=self.group_size,
            bits=self.bits,
        )

    def ternary_stats(self) -> dict[str, float]:
        """Report ternary weight and gamma statistics."""
        w = unpack_ternary_mlx(self.weight)  # (N, K) int8
        total = w.size
        return {
            "sparsity":    float((w == 0).sum().item()) / total,
            "pos_frac":    float((w == 1).sum().item()) / total,

[CONTENT TRUNCATED] Showing lines 202 to 311 of 2656 total lines. Use line_offset=311 parameter to read more content.
```

### Thinking

 I'm looking at how the FFN gate mechanism works in v15—the gate pre-activation comes from applying a linear transformation to the normalized input before the SiLU activation, which is what gets used for the routing calculation.

In the StrideStackVSM, this gate plate is called multiple times per stack invocation (once per band in each outer pass), so I need to capture a specific, consistent occurrence. The cleanest approach is to monkeypatch the gate plate's call method to record its output each time, keeping only the last recorded value—which corresponds to the final band of the final outer pass, giving me the deepest representation. I'll extract the last token from that output, which should have shape (d_ff,), and d_ff is 5120, matching the injection space I need.

The routing-register centroid I'm capturing is the output sign in d_ff space, while exp_b perturbs the weight rows of the gate plate. A direction in output space maps to which output channels to reinforce, which corresponds to which weight rows to flip—so the semantics are coherent. For now, Phase 1 just needs to collect v15's combinator Gram and centroids from the gate-output routing register (the sign of the gate pre-activation at the last token), which is well-defined and matches the HF measurement. Then I need to check how v15model's forward and __call__ methods work in MLX to set up the capture properly.

Patching the gate plate's __call__ directly on the instance won't work in MLX since special methods are resolved through the type, not the instance. I need to either wrap the module or replace the reference inside stack_c, but since stack_c holds the same plate object passed during initialization, I'd need to update both references.

The cleanest approach is to wrap `model.stack_c.ffn_gate_plate` with a small capture module that intercepts the output and stores it, then reads from that wrapper after the forward pass. Setting this wrapper as an attribute on the nn.Module should work fine as long as it properly wraps the inner module without breaking parameter registration.

Now I need to build the per-probe collection: run the model on each probe token, capture the gate sign from the deepest reduction, and accumulate those into a matrix for computing centroids and gram matrices. Before I start, let me check how exp_b loads the model and runs forward_metrics, and verify the exact signatures for create_model_with_deltas and V15Config so I mirror the setup correctly.

## Assistant

Now I understand the routing register precisely: `routing(x) = sign(ffn_gate_plate(ffn_norm(x)))` before SiLU — and the live module exp_b targets is `stack_c.ffn_gate_plate`. Capture mechanism: wrap that exact object (s218's orphan lesson — must wrap the reference *inside* stack_c, not `model.ffn_gate_plate_c`). Let me confirm the exp_b load pattern and `create_model_with_deltas` signature to mirror loading exactly.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/exp_b_self_verifying_acceptance.py",
  "line_offset": 0,
  "limit": 115
}
```

**Summary:** Reading exp_b_self_verifying_acceptance.py (0-115)

**Output:**
```
#!/usr/bin/env python3
# register: functional
"""Experiment B (core) — is the continuation a SELF-VERIFYING acceptance test?

THE DISTRIBUTED-TRAINING CLAIM (explore/consensus-delta-folding.md, s217):
  A working VSM continuation (the outer recurrence in v15model.py: shared sweep
  iterated, x_c fed back → β-reduction toward a fixed point / WHNF) should let
  distributed training ACCEPT or REJECT a donated delta WITHOUT trusted held-out
  labels — because the fixed point IS the target. A good delta should preserve /
  accelerate convergence (lower Δx-at-convergence); a bad delta should push the
  operator off its fixed point (raise Δx-at-convergence). If so:

      accept(delta)  ⟺  Δx-at-convergence does NOT rise

  is a label-free, Byzantine-robust acceptance rule (removes the audit-#7
  population-Goodhart risk: no shared calibration cache to overfit).

THE TEST (this script, gradient-free):
  Build the frozen continuation operator (V15Model + extracted base, n_outer=K).
  Perturb the ROUTING register (FFN gate delta plate) by flipping B random
  positions (a quality SPECTRUM via flip-count B = 1,2,4,...). For each candidate
  measure BOTH:
    ΔCE          = model._last_ce − CE0          (the TRUE quality label)
    Δ(Δx_conv)   = Δx_at_convergence − Δx0        (the SELF-VERIFYING signal)
  Then correlate. The hypothesis is corr(ΔCE, Δ(Δx_conv)) > 0: degrading the
  operator (raising CE) also raises the fixed-point residual. If yes, the
  continuation residual is a valid label-free acceptance signal.

  Δx_at_convergence = model._last_outer_deltas[-1] = ‖x_c^K − x_c^{K-1}‖/‖·‖
  (the last outer-recurrence relative step — 0 ⇒ exact fixed point / WHNF).

CAVEAT (register): on the FROZEN extracted base the operator is not yet trained
for contractivity (s214: naive K stays Δx~1.2). This is therefore a LOWER BOUND;
the clean test reruns on main:1's λ_fp-trained contractive checkpoint once it
lands. We report the baseline convergence curve so the regime is explicit.

Usage:
  uv run python scripts/experiments/exp_b_self_verifying_acceptance.py \
      --n-outer 6 --seqs 4 --seq-len 512 --reps 8

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_V15 = _PROJECT_ROOT / "scripts" / "v15"
sys.path.insert(0, str(_V15))

import mlx.core as mx  # noqa: E402
from config import V15Config  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402
from td_delta import (  # noqa: E402
    TernaryLinear,
    DeltaTernaryLinear,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    reduce_all_deltas,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "exp-b-self-verifying"
SHARD = Path.home() / "data" / "fractal-bitnet" / "shards-qwen36" / "shard_00000.npy"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def load_token_batch(seqs: int, seq_len: int, vocab: int, seed: int = 0):
    """A (seqs, seq_len+1) token window from the data shard → (tokens, targets)."""
    arr = np.load(str(SHARD), mmap_mode="r")
    rng = np.random.default_rng(seed)
    need = seq_len + 1
    starts = rng.integers(0, len(arr) - need, size=seqs)
    rows = np.stack([np.asarray(arr[s:s + need], dtype=np.int64) for s in starts])
    rows = np.clip(rows, 0, vocab - 1)
    tokens = mx.array(rows[:, :-1])
    targets = mx.array(rows[:, 1:])
    return tokens, targets


def forward_metrics(model, tokens, targets):
    """One forward at the configured n_outer → (CE, Δx_at_convergence, curve)."""
    model._prev_alg_c = None  # clean state, no cross-call algedonic drift
    _, _ = model(tokens, targets)
    mx.eval(model._last_ce)
    ce = float(model._last_ce.item())
    curve = [float(d.item()) for d in model._last_outer_deltas]
    dx_conv = curve[-1] if curve else float("nan")
    return ce, dx_conv, curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-outer", type=int, default=6)
    ap.add_argument("--seqs", type=int, default=4)
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--reps", type=int, default=8,
                    help="random position-sets per flip-count")
    ap.add_argument("--flip-fracs", type=str,
                    default="0.0003,0.001,0.003,0.01,0.03,0.1,0.3",
                    help="flip these FRACTIONS of the plate's positions (the quality spectrum)")
    ap.add_argument("--module-filter", type=str, default="ffn_gate",
                    help="substring to pick the target routing module(s)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--extracted-model-path", type=str,

[CONTENT TRUNCATED] Showing lines 1 to 115 of 309 total lines. Use line_offset=115 parameter to read more content.
```

### Thinking

 I'm examining the model-loading section of exp_b to replicate its structure precisely.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/exp_b_self_verifying_acceptance.py",
  "line_offset": 115,
  "limit": 90
}
```

**Summary:** Reading exp_b_self_verifying_acceptance.py (115-205)

**Output:**
```
                    default="checkpoints/v15-extracted/model.npz/model.npz",
                    help="frozen base (nested model.npz, as main:1 uses)")
    ap.add_argument("--checkpoint", type=str, default="",
                    help="optional TRAINED model.npz (non-chance CE) to load over the base")
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    flip_fracs = [float(x) for x in args.flip_fracs.split(",")]

    cfg = V15Config()
    if Path(args.extracted_model_path).exists():
        cfg.extracted_model_path = args.extracted_model_path
    log(f"building continuation operator (n_outer={args.n_outer}) ...")
    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
    if args.checkpoint and Path(args.checkpoint).exists():
        log(f"  loading TRAINED checkpoint: {args.checkpoint}")
        model.load_weights(args.checkpoint, strict=False)
        mx.eval(model.parameters())
        # fold trained delta routing into the base so deltas restart at +1;
        # perturbations are then correctly RELATIVE to the trained operator.
        n_reduced = reduce_all_deltas(model)
        log(f"  folded {n_reduced} trained delta plates into base (deltas → +1)")
        mx.eval(model.parameters())
    model._n_outer_passes = args.n_outer
    model._fixed_point_lambda = 0.0  # eval only
    mx.eval(model.parameters())

    tokens, targets = load_token_batch(args.seqs, args.seq_len, cfg.vocab_size, args.seed)
    log(f"batch: tokens {tokens.shape}  targets {targets.shape}")

    # ── baseline ──
    ce0, dx0, curve0 = forward_metrics(model, tokens, targets)
    log(f"baseline  CE={ce0:.4f}  Δx_conv={dx0:.4f}  curve={['%.3f'%c for c in curve0]}")

    # ── pick a target routing module that is ACTUALLY IN THE FORWARD PATH ──
    # INSTRUMENT GUARD (s218): convert_ffn ORPHANS the top-level ffn_*_plate_*
    # DeltaTernaryLinear copies — `convert_to_delta` setattr's the model attribute
    # but stack_{a,c} keep their original references, so the LIVE FFN plates are
    # stack_{a,c}.ffn_gate_plate (TernaryLinear). The prior run perturbed an orphan
    # ⇒ CE bit-identical across 1.97M flips ⇒ VOID. We now (1) enumerate candidate
    # ternary modules matching the filter, (2) KEEP only those whose signs actually
    # move CE, (3) ABORT if none. Perturbation = sign-flip of NONZERO ternary
    # positions (= the routing register; zeros stay zero).
    def _is_delta(m):
        return isinstance(m, DeltaTernaryLinear)

    def _orig_signs(m):
        return np.asarray(unpack_ternary_mlx(m.delta_weight if _is_delta(m) else m.weight))

    def _set_signs(m, arr_np):
        packed = pack_ternary_mlx(mx.array(arr_np.astype(np.int8)))
        if _is_delta(m):
            m.delta_weight = packed
        else:
            m.weight = packed
        mx.eval(packed)

    candidates = [(n, m) for (n, m) in model.named_modules()
                  if isinstance(m, (TernaryLinear, DeltaTernaryLinear))
                  and args.module_filter in n]
    if not candidates:
        raise SystemExit(f"no ternary module matches --module-filter={args.module_filter!r}")

    tgt_name = tgt_mod = base_signs = None
    for name, mod in candidates:
        signs = _orig_signs(mod)
        N_, K_ = signs.shape
        nz = np.flatnonzero(signs.reshape(-1) != 0)
        if nz.size == 0:
            continue
        gr = np.random.default_rng(args.seed).choice(nz, size=max(1, nz.size // 2), replace=False)
        probe = signs.copy().reshape(-1)
        probe[gr] *= -1
        _set_signs(mod, probe.reshape(N_, K_))
        ce_probe, _, _ = forward_metrics(model, tokens, targets)
        _set_signs(mod, signs)  # restore exactly
        moved = abs(ce_probe - ce0)
        log(f"  guard: {name:34} ({N_},{K_}) nz={nz.size:>9,}  flip-½nz ΔCE={ce_probe-ce0:+.4f}"
            f"  {'LIVE ✓' if moved > 1e-4 else 'DEAD ✗'}")
        if moved > 1e-4 and tgt_mod is None:
            tgt_name, tgt_mod, base_signs = name, mod, signs

    if tgt_mod is None:
        raise SystemExit("INSTRUMENT GUARD FAILED: no live routing module for "
                         f"--module-filter={args.module_filter!r} — perturbations do not reach "
                         "the forward. ABORT (the result would be VOID, cf. s217 phase-2 bug).")

    N, K = base_signs.shape
    nz_idx = np.flatnonzero(base_signs.reshape(-1) != 0)  # routing positions (nonzero signs)

[CONTENT TRUNCATED] Showing lines 116 to 205 of 309 total lines. Use line_offset=205 parameter to read more content.
```

### Thinking

 I'm working through the loading pattern and V15Config setup—the default checkpoint path is nested under `checkpoints/v15-extracted/model.npz/model.npz`. When creating the model, I need to be careful about the `convert_ffn` flag since setting it to True would orphan the gate I need to read directly from the live stack (the TernaryLinear gate_plate), so I should keep it False for my mapping purposes.

The key insight is that the FFN gate plates themselves aren't delta-ized during training—only the attention projections get trained deltas. The v15 design freezes the FFN extraction by design, so the gate plate weights stay as the extracted base. However, the gate's output still depends on its input (the normalized FFN activation), which does depend on the trained attention layers, so I need to load the trained checkpoint to capture the full trained operator's behavior.

For the model setup, I'll mirror exp_b exactly: convert_ffn=True, load the checkpoint from step_001000/model.npz, and reduce_all_deltas to get the trained state. Then I'll capture the stack_c.ffn_gate_plate output. I'm assuming the extracted base checkpoint exists since exp_b ran successfully. For n_outer, I'll use 2 to match the trained config (K=2), which captures how the gate actually behaves across multiple passes in the trained model.

For the capture itself, I'll grab the last call of stack_c's gate since all bands within the stack share the same gate plate weight—only the input differs per band. This "last band" approach is simplest and aligns with capturing the deepest reduction. I'll apply CMR across probes to match the consensus method exactly, then compute silhouette with n_perm=1000, which is fast enough for 535 probes × 5120 dims.

Rather than importing the heavy combinator_relationship_map module (which pulls in torch), I'll copy the pure numpy helpers directly into the v15 script—CMR, unit norm, centroids, gram, silhouette, and MDS are all lightweight. I'll wrap the gate plate in a capture module that stores the last output, then inject it into the model.

Writing the capture wrapper... I need to figure out which tokenizer v15 uses so I can tokenize the probe text prompts. The shards are labeled "qwen36," which suggests a Qwen tokenizer, but I should verify the exact model and check if it's available in the transformers library or elsewhere in the codebase.

## Assistant

I have the full load pattern. One open dependency: v15 consumes pre-tokenized Qwen shards (exp_b never tokenizes text), but the probes are text. I need the matching tokenizer. Let me find which tokenizer v15/the shards use.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== vocab + tokenizer refs ===\" && grep -rn \"vocab_size\\|tokenizer\\|qwen36\\|Qwen2\\|from_pretrained\\|AutoTokenizer\\|tokenizer_name\\|Qwen/\" scripts/v15/config.py 2>/dev/null | head -20 ; echo \"--- grep tokenizer across v15 + data prep ---\" && grep -rln \"AutoTokenizer\\|tokenizer\" scripts/v15/ scripts/ 2>/dev/null | head ; echo \"--- shards dir ---\" && ls ~/data/fractal-bitnet/shards-qwen36/ 2>/dev/null | head -3 ; echo \"--- any tokenizer meta near shards ---\" && ls ~/data/fractal-bitnet/ 2>/dev/null | head"
}
```

**Summary:** $ echo "=== vocab + tokenizer refs ==...

**Output:**
```
Exit code: 0
Stdout:
=== vocab + tokenizer refs ===
scripts/v15/config.py:154:    vocab_size: int = VOCAB_SIZE
scripts/v15/config.py:222:    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen36"
--- grep tokenizer across v15 + data prep ---
scripts/v15/etch.py
scripts/v15/generate.py
scripts/v15/diagnose_pipeline.py
scripts/v15/build_trace_basis.py
scripts/v15/__pycache__/data.cpython-312.pyc
scripts/v15/__pycache__/train.cpython-312.pyc
scripts/v15/__pycache__/train.cpython-314.pyc
scripts/v15/__pycache__/build_trace_basis.cpython-312.pyc
scripts/v15/__pycache__/etch.cpython-312.pyc
scripts/v15/train.py
--- shards dir ---
prep_status.json
shard_00000.npy
shard_00001.npy
--- any tokenizer meta near shards ---
dolma-raw
prep_status.json
shards
shards-bios
shards-qwen3
shards-qwen36
```

### Thinking

 I need to check a few files to understand the tokenizer setup—generate.py for the tokenizer used during generation, config.py for the vocabulary size, and prep_status.json to confirm the tokenizer name.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== VOCAB_SIZE ===\" && grep -n \"VOCAB_SIZE\" scripts/v15/config.py | head && echo \"=== generate.py tokenizer ===\" && grep -n \"tokenizer\\|Tokenizer\\|from_pretrained\\|Qwen\\|encode\\|decode\" scripts/v15/generate.py | head -20 && echo \"=== prep_status tokenizer ===\" && python3 -c \"import json;d=json.load(open('/Users/mwhitford/data/fractal-bitnet/shards-qwen36/prep_status.json'));print({k:d[k] for k in list(d)[:15]})\" 2>/dev/null | head"
}
```

**Summary:** $ echo "=== VOCAB_SIZE ===" && grep -...

**Output:**
```
Exit code: 0
Stdout:
=== VOCAB_SIZE ===
42:VOCAB_SIZE = 248320  # Qwen3.6-27B BBPE
154:    vocab_size: int = VOCAB_SIZE
=== generate.py tokenizer ===
32:def load_tokenizer():
33:    """Load Qwen tokenizer."""
34:    from transformers import AutoTokenizer
35:    for name in ["Qwen/Qwen3.6-27B", "Qwen/Qwen3-0.6B", "Qwen/Qwen3-4B"]:
37:            tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
38:            print(f"Tokenizer: {name} (vocab={len(tok)})")
42:    raise RuntimeError("Could not load Qwen tokenizer")
82:    tokenizer,
89:    input_ids = tokenizer.encode(prompt, add_special_tokens=False)
114:        new_text = tokenizer.decode([next_token])
118:        if next_token == tokenizer.eos_token_id:
129:    return tokenizer.decode(tokens)
151:    tokenizer = load_tokenizer()
163:        generate(model, tokenizer, prompt,
=== prep_status tokenizer ===
{'tokenizer': 'Qwen3.6-BBPE', 'tokenizer_model': 'Qwen/Qwen3.6-27B', 'vocab_size': 248044, 'eod_id': 248046, 'source': '/Users/mwhitford/data/fractal-bitnet/dolma-raw', 'source_files': 32, 'shards_written': 60, 'shard_size': 50000000, 'total_tokens': 3000000000, 'total_documents': 4403129, 'target_tokens': 3000000000, 'errors_skipped': 0, 'elapsed_seconds': 3378.7, 'tokens_per_second': 887906, 'timestamp': '2026-05-24T18:25:41.466916+00:00'}
```

### Thinking

 The tokenizer needs to be Qwen3.6-27B specifically because the vocabulary size is 248320, and using a fallback tokenizer like Qwen3-0.6B with its smaller vocabulary of around 151k would produce mismatched token IDs that don't align with what the model expects.

Let me check if the tokenizer is available in the Hugging Face cache locally, since downloading it could be a blocker if it's not already cached.

## Assistant

The tokenizer is `Qwen/Qwen3.6-27B` (vocab 248320) — token IDs must match or the routing measurement is meaningless. Let me check it's available locally (cached) before relying on it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -i \"qwen3.6\\|Qwen3.6\\|27B\" ; echo \"--- try loading the canonical tokenizer (offline) ---\" ; cd /Users/mwhitford/src/verbum && HF_HUB_OFFLINE=1 uv run python -c \"\nfrom transformers import AutoTokenizer\ntry:\n    t=AutoTokenizer.from_pretrained('Qwen/Qwen3.6-27B', trust_remote_code=True)\n    ids=t.encode('compose after washing then drying', add_special_tokens=False)\n    print('OK Qwen3.6-27B vocab=',len(t),'sample ids[:8]=',ids[:8],'max=',max(ids))\nexcept Exception as e:\n    print('FAIL Qwen3.6-27B:', repr(e)[:160])\n\" 2>&1 | tail -6"
}
```

**Summary:** $ ls ~/.cache/huggingface/hub/ 2>/dev...

**Output:**
```
Exit code: 0
Stdout:
models--Qwen--Qwen3.6-27B
models--Qwen--Qwen3.6-35B-A3B
--- try loading the canonical tokenizer (offline) ---
OK Qwen3.6-27B vocab= 248077 sample ids[:8]= [50932, 1238, 26789, 1179, 43865] max= 50932
```

### Thinking

 The Qwen3.6-27B tokenizer is ready to load offline with a vocabulary size that fits within the model's configuration. I'm setting up the script to load the tokenizer, initialize the v15 model with the configuration and delta weights, and load the checkpoint.

For each probe, I'll tokenize it (capping at 256 tokens), convert to an mx.array, run the model forward pass, and capture the gate pre-activation from the FFN layer. Then I'll compute the routing matrix, apply CMR clustering, calculate centroids and gram matrices, and generate the MDS visualization with nearest-neighbor mapping before saving the results.

I'm thinking through the implementation details: tokenization should handle edge cases like empty inputs by enforcing a minimum length, the model forward pass doesn't require targets (only used for loss computation), and the memory footprint is manageable with 535 probes at ~30 tokens each producing an 11MB routing matrix. I'll default to 2 outer passes for the gate measurement to match the training configuration.

Now I need to verify the attribute path for the gate plate in the StrideStackVSM module — the forward code uses `self.ffn_gate_plate`, so wrapping `model.stack_c.ffn_gate_plate` with GateCapture should work correctly.

For the implementation, I'll create a simple wrapper class that captures the output of the inner plate while passing it through unchanged. Rather than making it an nn.Module, I'll use a plain Python callable since we only need it for forward evaluation after the model is already loaded — no parameter traversal required. MLX's Module.__setattr__ will store it as a regular attribute without trying to track it as a submodule, which keeps things clean.

I'll capture gates from both stack_a and stack_c, using stack_c as the primary target since that's what the experiment focuses on. For tokenization, I'll load offline using local_files_only=True to avoid network calls, and set up the results directory as results/combinator-relationship-map with output names like v15_step001000.

Writing the full script now...

## Assistant

Everything's available offline. I have the full picture:
- **Routing register:** `sign(stack_c.ffn_gate_plate(ffn_norm(x)))` pre-SiLU, last token — the same d_ff=5120 space exp_b perturbs.
- **Load:** mirror exp_b exactly (`create_model_with_deltas` + load checkpoint + `reduce_all_deltas`).
- **Capture:** wrap the *live* `stack_c.ffn_gate_plate` reference (s218's orphan lesson).
- **Tokenizer:** `Qwen/Qwen3.6-27B`, cached, offline.

Building the v15 map instrument now.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Combinator relationship map — the v15 (MLX/ternary) edition.\n\nWHY a separate script (s220):\n  combinator_relationship_map.py is HF-only (`AutoModelForCausalLM`, hooks\n  `gate_proj`). v15 is an MLX ternary model with a shared-stride VSM stack and an\n  outer recurrence — a different forward path. To HARVEST ecosystem-consensus\n  combinator structure into the v15 base plate (consensus-delta-folding.md §s220,\n  harvest fold Phase 1) we first need v15's OWN combinator Gram + centroids in the\n  SAME routing register the consensus uses, and in the SAME d_ff space the Exp-B\n  acceptance harness perturbs. This produces the target frame for align-before-fold.\n\nTHE ROUTING REGISTER (identical definition to the HF script):\n  routing(x) = sign( FFN gate pre-activation )\n  In v15 the live FFN gate is `stack_c.ffn_gate_plate` (a TernaryLinear); its\n  forward is `ffn_gate = nn.silu(self.ffn_gate_plate(ffn_norm(x)))`. The PRE-silu\n  output `ffn_gate_plate(ffn_norm(x))` is the gate pre-activation (== HF gate_proj\n  output). We capture it at the LAST token of the LAST band of the LAST outer pass\n  (the deepest reduction), per probe.\n  centroid_k = mean over probes labelled k of sign(routing), AFTER common-mode\n  removal (CMR); Gram[j,k] = cosine(centroid_j, centroid_k).  <- THE MAP\n\nCAPTURE MECHANISM (the s218 orphan lesson):\n  We wrap the LIVE plate object that `stack_c` actually calls\n  (`model.stack_c.ffn_gate_plate`), NOT `model.ffn_gate_plate_c` — convert_ffn\n  rebinds the model attribute but stack_c keeps its original reference (the bug\n  that VOIDed s217 phase-2). The wrapper passes through and stashes the last output.\n\nLOAD (mirrors exp_b_self_verifying_acceptance.py exactly):\n  cfg=V15Config(); create_model_with_deltas(cfg, convert_ffn=True);\n  load_weights(checkpoint, strict=False); reduce_all_deltas(model)  -> trained\n  operator; n_outer from CLI; fixed_point_lambda=0 (eval only).\n  Checkpoint is READ-ONLY (the running main:1 training writes step_NNNN/; we only\n  read an already-frozen step).\n\nUsage (GPU/MLX — run in tmux main:2 alongside main:1, per Michael s220):\n  uv run python scripts/experiments/combinator_relationship_map_v15.py \\\n      --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz \\\n      --n-outer 2\n  # smoke: add --limit-per 3 --n-perm 50\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\n_V15 = _PROJECT_ROOT / \"scripts\" / \"v15\"\nsys.path.insert(0, str(_V15))\nsys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\n\nimport mlx.core as mx  # noqa: E402\nimport mlx.nn as nn  # noqa: E402\nfrom config import V15Config  # noqa: E402\nfrom train_td import create_model_with_deltas  # noqa: E402\nfrom td_delta import reduce_all_deltas  # noqa: E402\nfrom verbum.probes.library import crystal_probes  # noqa: E402\n\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"combinator-relationship-map\"\nCRYSTAL = [\"K\", \"I\", \"B\", \"C\", \"S\", \"D\", \"W\", \"Y\", \"WHNF\"]\nTOKENIZER_NAME = \"Qwen/Qwen3.6-27B\"  # the shards-qwen36 BBPE tokenizer\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# ---- pure-numpy analysis helpers (copied from combinator_relationship_map.py\n#      to avoid importing torch/transformers via that module) -----------------\ndef cmr(X):\n    return X - X.mean(axis=0, keepdims=True)\n\n\ndef unit(v):\n    return v / (np.linalg.norm(v) + 1e-30)\n\n\ndef centroids(X, labels):\n    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)\n    for j, c in enumerate(CRYSTAL):\n        m = labels == c\n        C[j] = X[m].mean(axis=0)\n    return C\n\n\ndef gram(C):\n    U = np.array([unit(c) for c in C])\n    return np.clip(U @ U.T, -1, 1)\n\n\ndef silhouette(X, labels):\n    C = centroids(X, labels)\n    U = np.array([unit(c) for c in C])\n    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)\n    sims = Xu @ U.T\n    lab_idx = np.array([CRYSTAL.index(c) for c in labels])\n    own = sims[np.arange(len(labels)), lab_idx]\n    other = sims.copy()\n    other[np.arange(len(labels)), lab_idx] = -np.inf\n    return float(np.mean(own - other.max(axis=1)))\n\n\ndef silhouette_null(X, labels, n_perm=1000, seed=0):\n    obs = silhouette(X, labels)\n    rng = np.random.default_rng(seed)\n    null = np.empty(n_perm)\n    for i in range(n_perm):\n        null[i] = silhouette(X, rng.permutation(labels))\n    sd = null.std() + 1e-30\n    return {\"silhouette\": obs, \"null_mean\": float(null.mean()),\n            \"null_std\": float(null.std()),\n            \"z\": float((obs - null.mean()) / sd),\n            \"p_value\": float((np.sum(null >= obs) + 1) / (n_perm + 1))}\n\n\ndef classical_mds(D, k=2):\n    n = D.shape[0]\n    J = np.eye(n) - np.ones((n, n)) / n\n    B = -0.5 * J @ (D ** 2) @ J\n    w, V = np.linalg.eigh(B)\n    order = np.argsort(w)[::-1]\n    w, V = w[order][:k], V[:, order][:, :k]\n    w = np.clip(w, 0, None)\n    return V * np.sqrt(w + 1e-30)\n\n\n# ---- probes -----------------------------------------------------------------\ndef load_probes(limit_per: int = 0, seed: int = 0):\n    by = {c: [] for c in CRYSTAL}\n    for p in crystal_probes():\n        if p.combinator in by:\n            by[p.combinator].append(p.prompt)\n    rng = np.random.default_rng(seed)\n    prompts, labels = [], []\n    for c in CRYSTAL:\n        ps = by[c]\n        if limit_per and limit_per < len(ps):\n            idx = sorted(rng.permutation(len(ps))[:limit_per])\n            ps = [ps[i] for i in idx]\n        prompts.extend(ps)\n        labels.extend([c] * len(ps))\n    return prompts, np.array(labels)\n\n\n# ---- live-gate capture (wrap the reference stack_c actually calls) ----------\nclass GateCapture(nn.Module):\n    \"\"\"Pass-through wrapper that stashes the last pre-activation it produced.\"\"\"\n\n    def __init__(self, inner):\n        super().__init__()\n        self.inner = inner\n        self.last = None\n\n    def __call__(self, x):\n        out = self.inner(x)\n        self.last = mx.stop_gradient(out)\n        return out\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=__doc__)\n    ap.add_argument(\"--checkpoint\", type=str,\n                    default=\"checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz\",\n                    help=\"TRAINED v15 model.npz (READ-ONLY); '' = frozen base only\")\n    ap.add_argument(\"--extracted-model-path\", type=str,\n                    default=\"checkpoints/v15-extracted/model.npz/model.npz\")\n    ap.add_argument(\"--n-outer\", type=int, default=2,\n                    help=\"outer recurrence passes (match training K=2)\")\n    ap.add_argument(\"--stack\", choices=[\"a\", \"c\"], default=\"c\",\n                    help=\"which stack's ffn_gate_plate to read (c = Exp-B target)\")\n    ap.add_argument(\"--max-length\", type=int, default=256)\n    ap.add_argument(\"--limit-per\", type=int, default=0, help=\"cap probes/combinator (smoke)\")\n    ap.add_argument(\"--n-perm\", type=int, default=1000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--tag\", type=str, default=\"\", help=\"output name suffix override\")\n    args = ap.parse_args()\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    t0 = time.time()\n\n    prompts, labels = load_probes(args.limit_per, args.seed)\n    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}\n    log(f\"[v15] {len(prompts)} crystal probes  {counts}\")\n\n    # tokenizer (offline; the shards-qwen36 BBPE)\n    from transformers import AutoTokenizer\n    tok = AutoTokenizer.from_pretrained(\n        TOKENIZER_NAME, trust_remote_code=True, local_files_only=True)\n\n    # ── load v15 exactly like exp_b ──\n    cfg = V15Config()\n    if Path(args.extracted_model_path).exists():\n        cfg.extracted_model_path = args.extracted_model_path\n    log(f\"building v15 operator (n_outer={args.n_outer}) ...\")\n    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)\n    loaded_ckpt = \"\"\n    if args.checkpoint and Path(args.checkpoint).exists():\n        log(f\"  loading TRAINED checkpoint: {args.checkpoint}\")\n        model.load_weights(args.checkpoint, strict=False)\n        mx.eval(model.parameters())\n        n_reduced = reduce_all_deltas(model)\n        log(f\"  folded {n_reduced} trained delta plates into base\")\n        mx.eval(model.parameters())\n        loaded_ckpt = args.checkpoint\n    else:\n        log(\"  no checkpoint — using frozen extracted base only\")\n    model._n_outer_passes = args.n_outer\n    model._fixed_point_lambda = 0.0\n\n    # ── wrap the LIVE gate plate (NOT model.ffn_gate_plate_c — orphan, s218) ──\n    stack = model.stack_c if args.stack == \"c\" else model.stack_a\n    cap = GateCapture(stack.ffn_gate_plate)\n    stack.ffn_gate_plate = cap\n    d_ff = int(cfg.d_ff)\n    log(f\"  capturing stack_{args.stack}.ffn_gate_plate pre-activation (d_ff={d_ff})\")\n\n    # ── forward each probe, capture last-token gate pre-activation ──\n    gate = np.empty((len(prompts), d_ff), np.float32)\n    plen = np.empty(len(prompts), np.int32)\n    for i, text in enumerate(prompts):\n        ids = tok.encode(text, add_special_tokens=False)[: args.max_length]\n        if not ids:\n            ids = [0]\n        ids = [min(t, cfg.vocab_size - 1) for t in ids]\n        tokens = mx.array(np.asarray(ids, np.int64)[None, :])\n        model._prev_alg_c = None\n        cap.last = None\n        _ = model(tokens)\n        mx.eval(cap.last)\n        g = np.asarray(cap.last[0, -1], np.float32)  # (d_ff,)\n        gate[i] = g\n        plen[i] = len(ids)\n        if (i + 1) % 50 == 0:\n            log(f\"    {i + 1}/{len(prompts)}\")\n\n    # ── routing register: sign(gate), raw + CMR ──\n    sign = np.sign(gate)\n    sign_cmr = cmr(sign)\n    sil_full = silhouette_null(sign, labels, args.n_perm, args.seed)\n    sil_cmr = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)\n    Cb = centroids(sign_cmr, labels)          # (9, d_ff) — the harvest material\n    G = gram(Cb)\n    log(f\"  route_cmr silhouette={sil_cmr['silhouette']:+.4f} \"\n        f\"z={sil_cmr['z']:+.2f} p={sil_cmr['p_value']:.4f}  \"\n        f\"(control route_full z={sil_full['z']:+.2f})\")\n\n    D = 1.0 - G\n    np.fill_diagonal(D, 0.0)\n    mds = classical_mds(D, k=2)\n    nn_map = {}\n    for i, c in enumerate(CRYSTAL):\n        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]\n        row.sort(key=lambda x: -x[1])\n        nn_map[c] = row[:3]\n\n    log(\"\\n  Gram (cosine) — the v15 MAP:\")\n    head = \"       \" + \"\".join(f\"{c:>7}\" for c in CRYSTAL)\n    log(head)\n    for i, c in enumerate(CRYSTAL):\n        log(f\"  {c:>5}\" + \"\".join(f\"{G[i, j]:+7.2f}\" for j in range(len(CRYSTAL))))\n\n    out = {\n        \"model\": \"v15\", \"register\": \"topological/routing\",\n        \"checkpoint\": loaded_ckpt, \"n_outer\": args.n_outer,\n        \"stack\": args.stack, \"d_ff\": d_ff, \"n_probes\": len(prompts),\n        \"counts\": counts, \"crystal_order\": CRYSTAL, \"n_perm\": args.n_perm,\n        \"git_sha\": git_sha(),\n        \"route_cmr_silhouette\": sil_cmr, \"route_full_silhouette\": sil_full,\n        \"map\": {\n            \"gram\": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)\n                                  for j in range(len(CRYSTAL))}\n                     for i in range(len(CRYSTAL))},\n            \"mds_coords\": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),\n                                        round(float(mds[i, 1]), 4)]\n                           for i in range(len(CRYSTAL))},\n            \"nearest\": nn_map,\n        },\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n    tag = args.tag or (Path(loaded_ckpt).parent.name if loaded_ckpt else \"base\")\n    safe = f\"v15_{tag}\"\n    np.savez_compressed(\n        RESULTS_DIR / f\"{safe}.npz\",\n        prompt_len=plen, labels=labels,\n        gram_route_cmr_best=G.astype(np.float32),\n        centroids_cmr_best=Cb.astype(np.float32),\n    )\n    (RESULTS_DIR / f\"{safe}.json\").write_text(json.dumps(out, indent=2))\n    log(f\"\\n  wrote {RESULTS_DIR / safe}.{{json,npz}}  ({out['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/combinator_relationship_map_v15.py && echo \"ruff OK\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
Stdout:
I001 [*] Import block is un-sorted or un-formatted
  --> scripts/experiments/combinator_relationship_map_v15.py:63:1
   |
61 |   sys.path.insert(0, str(_PROJECT_ROOT / "src"))
62 |
63 | / import mlx.core as mx  # noqa: E402
64 | | import mlx.nn as nn  # noqa: E402
65 | | from config import V15Config  # noqa: E402
66 | | from train_td import create_model_with_deltas  # noqa: E402
67 | | from td_delta import reduce_all_deltas  # noqa: E402
68 | | from verbum.probes.library import crystal_probes  # noqa: E402
   | |________________________________________________^
69 |
70 |   RESULTS_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
   |
help: Organize imports

E501 Line too long (93 > 88)
   --> scripts/experiments/combinator_relationship_map_v15.py:191:89
    |
189 |                     help="which stack's ffn_gate_plate to read (c = Exp-B target)")
190 |     ap.add_argument("--max-length", type=int, default=256)
191 |     ap.add_argument("--limit-per", type=int, default=0, help="cap probes/combinator (smoke)")
    |                                                                                         ^^^^^
192 |     ap.add_argument("--n-perm", type=int, default=1000)
193 |     ap.add_argument("--seed", type=int, default=0)
    |

Found 2 errors.
[*] 1 fixable with the `--fix` option.
```

### Thinking

 I'm running into a conflict with import sorting — ruff's isort wants to reorder the imports, but they're positioned after a `sys.path.insert` call that needs to stay first due to an E402 noqa exception. The imports are currently grouped by third-party (mlx modules) followed by local imports, but isort would reorganize them differently, and the autofix would shuffle things within that constrained block.

## Assistant

Two lint nits — autofix imports + shorten one line.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py",
  "original_content": "    ap.add_argument(\"--limit-per\", type=int, default=0, help=\"cap probes/combinator (smoke)\")",
  "new_content": "    ap.add_argument(\"--limit-per\", type=int, default=0,\n                    help=\"cap probes/combinator (smoke)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/combinator_relationship_map_v15.py && uv run ruff check scripts/experiments/combinator_relationship_map_v15.py && echo \"ruff OK\" && echo \"--- import block now ---\" && sed -n '55,70p' scripts/experiments/combinator_relationship_map_v15.py"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 1 error (1 fixed, 0 remaining).
All checks passed!
ruff OK
--- import block now ---
import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_V15 = _PROJECT_ROOT / "scripts" / "v15"
sys.path.insert(0, str(_V15))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import mlx.core as mx  # noqa: E402
import mlx.nn as nn  # noqa: E402
from config import V15Config  # noqa: E402
from td_delta import reduce_all_deltas  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402

from verbum.probes.library import crystal_probes  # noqa: E402
```

### Thinking

 Now I'm deciding whether to run the smoke test locally or in the main:2 environment—it's a quick GPU validation with just a handful of probes, so while the async discipline suggests keeping GPU work in main:2, the brevity of the test makes me consider running it directly here instead.

## Assistant

Clean. Now a tiny smoke test (27 probes, n_perm 50) to verify the capture + load works. This is a brief GPU touch — fine per your go-ahead. Running foreground with a generous timeout.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/combinator_relationship_map_v15.py --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz --n-outer 2 --limit-per 3 --n-perm 50 --tag smoke 2>&1 | tail -40",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Exit code: 0
Stdout:
[v15] 27 crystal probes  {'K': 3, 'I': 3, 'B': 3, 'C': 3, 'S': 3, 'D': 3, 'W': 3, 'Y': 3, 'WHNF': 3}
building v15 operator (n_outer=2) ...
📂 Loading extracted base plates from checkpoints/v15-extracted/model.npz/model.npz
  loaded=83 skipped=0
  loading TRAINED checkpoint: checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz
  folded 234 trained delta plates into base
  capturing stack_c.ffn_gate_plate pre-activation (d_ff=5120)
  route_cmr silhouette=+0.4940 z=+1.54 p=0.0980  (control route_full z=+1.54)

  Gram (cosine) — the v15 MAP:
             K      I      B      C      S      D      W      Y   WHNF
      K  +1.00  -0.17  -0.04  +0.03  -0.27  -0.31  -0.03  -0.21  -0.17
      I  -0.17  +1.00  -0.02  -0.17  -0.11  -0.15  -0.19  -0.01  -0.07
      B  -0.04  -0.02  +1.00  +0.00  -0.24  -0.21  -0.08  -0.21  -0.14
      C  +0.03  -0.17  +0.00  +1.00  -0.06  -0.09  -0.20  -0.37  -0.26
      S  -0.27  -0.11  -0.24  -0.06  +1.00  -0.01  -0.14  -0.07  -0.09
      D  -0.31  -0.15  -0.21  -0.09  -0.01  +1.00  -0.16  +0.01  -0.06
      W  -0.03  -0.19  -0.08  -0.20  -0.14  -0.16  +1.00  -0.09  -0.10
      Y  -0.21  -0.01  -0.21  -0.37  -0.07  +0.01  -0.09  +1.00  -0.01
   WHNF  -0.17  -0.07  -0.14  -0.26  -0.09  -0.06  -0.10  -0.01  +1.00

  wrote /Users/mwhitford/src/verbum/results/combinator-relationship-map/v15_smoke.{json,npz}  (9.5s)
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
```

### Thinking

 The smoke test ran successfully in 9.5 seconds, loading the base model, checkpoint, and all 234 folded delta plates, then capturing the stack_c.ffn_gate_plate layer and generating a Gram matrix with centroids saved to JSON and NPZ files. The route_cmr silhouette score came in at +0.4940 with a z-score of +1.54 (p=0.098 based on 27 probes across 50 permutations), and interestingly the route_full z-score matched route_cmr's since the sparse probe set meant CMR barely shifted the results.

The Gram matrix looks reasonable — diagonal entries at +1.0 with mostly negative off-diagonals, similar to the HF model maps — though the small sample size makes it hard to discern the three-family structure. The key insight is that on the full run with 535 probes and 1000 permutations, the z-scores should diverge significantly since CMR will have more room to reshape the feature space. I'm going to delete the smoke artifacts to keep the results clean, then launch the full run in tmux main:2. Based on the smoke timing (roughly 0.35s per probe after the ~8s load), the full 535-probe run should take around 1-2 minutes total — load time plus forward passes plus the silhouette null distribution computation across 1000 permutations — though GPU contention with main:1 could slow it down.

Actually, given how short this is, running it in the foreground with a 10-minute timeout makes more sense than queuing it in tmux. I'll delete the smoke files first, then execute the full map measurement directly.

## Assistant

Smoke works perfectly — loads base + step_001000 (folded 234 delta plates), captures `stack_c.ffn_gate_plate` (d_ff=5120), produces a sane Gram + saved centroids, all in 9.5s. The 27-probe sample is too small to read the shape (z=1.54), but the mechanism is verified.

Cleaning up smoke artifacts and running the full 535-probe map. It's short (~1–2 min), so foreground with a generous timeout rather than a background job.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && rm -f results/combinator-relationship-map/v15_smoke.json results/combinator-relationship-map/v15_smoke.npz && echo \"smoke artifacts removed\" && echo \"=== FULL v15 MAP (535 probes) ===\" && uv run python scripts/experiments/combinator_relationship_map_v15.py --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz --n-outer 2 --n-perm 1000 2>&1 | tail -32",
  "timeout": 900000
}
```

**Summary:** $ rm -f results/combinator-relationsh...

**Output:**
```
Exit code: 0
Stdout:
smoke artifacts removed
=== FULL v15 MAP (535 probes) ===
    50/535
    100/535
    150/535
    200/535
    250/535
    300/535
    350/535
    400/535
    450/535
    500/535
  route_cmr silhouette=+0.0021 z=+0.52 p=0.2917  (control route_full z=+0.62)

  Gram (cosine) — the v15 MAP:
             K      I      B      C      S      D      W      Y   WHNF
      K  +1.00  -0.12  -0.07  -0.05  -0.11  -0.18  -0.10  -0.17  -0.25
      I  -0.12  +1.00  -0.22  -0.14  -0.11  -0.25  -0.06  -0.10  -0.07
      B  -0.07  -0.22  +1.00  +0.03  -0.09  -0.11  -0.22  -0.08  -0.16
      C  -0.05  -0.14  +0.03  +1.00  -0.09  -0.09  -0.23  -0.19  -0.22
      S  -0.11  -0.11  -0.09  -0.09  +1.00  +0.03  -0.23  -0.14  -0.07
      D  -0.18  -0.25  -0.11  -0.09  +0.03  +1.00  -0.20  -0.18  +0.12
      W  -0.10  -0.06  -0.22  -0.23  -0.23  -0.20  +1.00  +0.02  -0.24
      Y  -0.17  -0.10  -0.08  -0.19  -0.14  -0.18  +0.02  +1.00  -0.10
   WHNF  -0.25  -0.07  -0.16  -0.22  -0.07  +0.12  -0.24  -0.10  +1.00

  wrote /Users/mwhitford/src/verbum/results/combinator-relationship-map/v15_step_001000.{json,npz}  (112.7s)
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
```

### Thinking

 I'm looking at the clustering analysis for the FFN gate routing register in v15, and the results are disappointing—the silhouette coefficient is barely positive at 0.0021 with a z-score of 0.52, which isn't statistically significant. The control comparison shows route_full actually performs slightly better with a z-score of 0.62, meaning the combinators aren't forming meaningful clusters and the CMR approach isn't delivering the improvement I was hoping for.

This is a striking contrast to what I see in the HF Qwen3-14B model, which shows a robust silhouette of 0.101 with a z-score of 7.97 and p-value of 0.001—the combinator function shape is clearly present there. But v15 doesn't have it. Given that v15 is a small 50M parameter model trained on only 3B tokens, it makes sense that it hasn't crystallized the combinator structure that larger models develop. Even Qwen3-0.6B barely showed the shape, so v15 being smaller and differently structured explains why it's absent here.

The real implication for the harvest fold is that my premise—aligning the ecosystem consensus into v15's frame—runs into a fundamental problem: there's no meaningful target structure in v15 to align to. But paradoxically, this is what makes harvesting potentially valuable. Since v15 lacks the shape entirely while the ecosystem has it, injecting that consensus structure could actually add something new to v15. The question is whether that injection would improve the model's performance.

Now I'm facing a genuine fork in how to proceed. If v15's centroids are near-noise with no significant cluster structure, I can't use them as meaningful directions for the fold. The consensus prescription tells me which combinator pairs should bind, but without a usable label-to-direction mapping in v15's routing, I can't translate that into actual FFN directions. Either I need to find a different register in v15 that does carry structure, or I need to reframe this as installing structure de novo rather than aligning to something existing. Let me verify the measurement itself is sound—I want to make sure I'm actually capturing the right signal from v15's gate routing. The CMR preprocessing isn't helping here either—both raw and CMR routes sit around 0.5-0.6, which suggests there's no underlying common-mode structure to remove. More tellingly, v15's gate routing silhouette is essentially zero (0.0021), roughly 50 times weaker than what I saw in the HF models, indicating the routing isn't actually selective. The honest move is to report this negative finding, pause Phase 2/3 of the harvest fold since the target structure isn't present, and present Michael with options: try a different register in v15, treat the harvest as a fresh installation, or accept that the model is too small and undertrained at this checkpoint.

But stepping back, the real issue crystallizes now—the harvest premise depends on the FFN gate carrying the ecosystem consensus shape, and v15's FFN gate simply doesn't have it. This reframes the whole problem: I'm not aligning to v15's own structure (which doesn't exist), I'm trying to install the consensus shape into a void. Without v15 having any combinator-structured centroids, there's no bridge from the relational consensus Gram to concrete d_ff directions. The empirical measurement confirms what's become a genuine scientific obstacle—the fold as designed can't proceed without that shared representational ground.

The disciplined move is to commit the measurement as a real negative finding, document the caveats clearly (v15's FFN was frozen-extracted without task-specific training, single capture point at step 1000/5000, last band only), and surface this as a fork to Michael. The effect size gap is too large (z=0.52 versus z~8 in the ecosystem) to dismiss as noise, and burning more GPU on speculative probes won't change that. I should report what I've found and let the decision about next steps come from above. I can compute the correlation between v15's Gram matrix and the ecosystem consensus directly on CPU—just reading both matrices and calculating the Pearson correlation across the 36 off-diagonal elements. That'll give me a clean quantitative measure of how far v15 is from the consensus shape, which becomes the key headline for whether harvest has room to improve or if the structure simply can't transfer.

## Assistant

Important — and I have to read this honestly. The full run is a **near-null result**:

**v15's FFN gate routing register shows NO significant combinator structure: route_cmr silhouette +0.0021, z=+0.52, p=0.29** — and CMR doesn't help (raw control z=+0.62 ≈ CMR). Contrast the ecosystem (Qwen3-14B: silhouette 0.101, **z=7.97, p=0.001**). The capture is working (the Gram has real variation, −0.37 to +0.12), but the combinator clustering simply isn't there.

Let me quantify how far v15 is from the consensus — the directly harvest-relevant number (CPU-only).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json, numpy as np\norder=['K','I','B','C','S','D','W','Y','WHNF']\niu=np.triu_indices(9,1)\nv=np.load('results/combinator-relationship-map/v15_step_001000.npz')['gram_route_cmr_best'].astype(float)\ncons=json.load(open('results/combinator-map-consensus/consensus.json'))\ncg=np.array(cons['consensus_gram'],float)\n# Pearson of 36 off-diagonal edges: v15 vs ecosystem consensus\nr=np.corrcoef(v[iu], cg[iu])[0,1]\nprint(f'v15 vs ecosystem-consensus GramCorr (36 off-diag edges): r={r:+.3f}')\nprint(f'  (ecosystem cross-model mean GramCorr was +0.78; v15 sits FAR outside)')\n# the 5 positive universal edges in v15:\nidx={c:i for i,c in enumerate(order)}\nprint('  positive universal edges in v15 vs consensus:')\nfor e in ['S-D','B-D','B-C','K-C','S-Y']:\n    a,b=e.split('-'); print(f'    {e}: v15={v[idx[a],idx[b]]:+.3f}  consensus=+{[x[\\\"consensus\\\"] for x in cons[\\\"universal_edges\\\"] if x[\\\"edge\\\"]==e][0]:.3f}')\n\""
}
```

**Summary:** $ python3 -c " import json, numpy as ...

**Output:**
```
Exit code: 0
Stdout:
v15 vs ecosystem-consensus GramCorr (36 off-diag edges): r=+0.354
  (ecosystem cross-model mean GramCorr was +0.78; v15 sits FAR outside)
  positive universal edges in v15 vs consensus:
    S-D: v15=+0.034  consensus=+0.161
    B-D: v15=-0.109  consensus=+0.175
    B-C: v15=+0.033  consensus=+0.168
    K-C: v15=-0.053  consensus=+0.133
    S-Y: v15=-0.144  consensus=+0.127
```

### Thinking

 The correlation between v15 and the ecosystem consensus is weakly positive at 0.354, suggesting v15 has picked up some structural echoes but hasn't fully crystallized the pattern that shows up so strongly in the ecosystem's internal 0.78 correlation. Looking at the five universal positive edges, only two of them (S-D and B-C) register as weakly positive in v15, while the other three are actually negative.

This reveals a strategic fork: the harvest approach of aligning to v15's frame and building directions from its centroids breaks down because v15's combinator structure isn't statistically significant (z=0.52), meaning those centroids aren't reliable representations to build from. But this also reframes the opportunity—v15 is missing the universal structure that the ecosystem clearly has, so harvesting would mean installing structure de novo rather than extracting what's already there. The "align to existing v15 frame" path is a dead end; any installation would need a different mechanism entirely.

Given this is an architectural decision point, I should commit the measurement, document the finding, and surface the fork to Michael with the options rather than proceeding to fabricate an alignment to a non-significant frame.

Actually, there's a crucial architectural detail I'm realizing: v15's FFN gate is frozen-extracted by design—only the attention routing was trained. So measuring the FFN gate is measuring an untrained frozen base, which explains why there's no combinator structure there. The HuggingFace models have combinator shape in their FFN because their FFN is fully trained. This means the negative finding is expected and consistent with v15's design, not a failure of the measurement itself.

The real obstacle is that even if I harvest the actual FFN centroids from an ecosystem model, I can't bridge them into v15's frozen FFN gate due to the cross-architecture dimension mismatch (ecosystem d_ff 17408 vs v15 5120) and the frame problem of mapping relational consensus into concrete weights. Before I commit this result and surface it to Michael, I should check whether v15's attention routing register—where the learned structure actually lives—shows the combinator shape, since that's the cheap, high-value follow-up that could reframe the whole conclusion.

## Assistant

This is the crux, and it's a clean negative finding with a strong architectural explanation:

- **v15's FFN-gate routing does not carry the combinator shape** (z=+0.52, p=0.29; GramCorr with the ecosystem consensus only +0.354 vs the ecosystem's internal +0.78). Of the 5 harvest-target positive edges, only 2 (S-D, B-C) are even weakly positive in v15; B-D, K-C, S-Y are *negative*.
- **The architectural reason (decisive):** in v15 the **FFN is frozen-extracted** — only the *attention* shared-stride stack is TD-trained (s218). So measuring the FFN gate measures the *untrained frozen base*, which has no learned combinator routing. The ecosystem's shape lives in *fully-trained* FFN gates.

This **blocks the harvest fold as conceived**: there's no v15 FFN-gate frame to align to (it's noise), and the cross-architecture dim mismatch (ecosystem d_ff 17408 vs v15 5120) means the relational consensus can't be installed as concrete v15 weights. Per discipline, I will **not** fabricate a Procrustes alignment to a non-significant frame (that would manufacture a false positive). Let me commit this real measurement, then surface the fork to you.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/combinator_relationship_map_v15.py results/combinator-relationship-map/v15_step_001000.json && git add -f results/combinator-relationship-map/v15_step_001000.npz && git status -s",
  "operation": "add",
  "summary": "stage v15 map"
}
```

**Summary:** Git add: stage v15 map

**Output:**
```
Exit code: 0
Stdout:
A  results/combinator-relationship-map/v15_step_001000.json
A  results/combinator-relationship-map/v15_step_001000.npz
A  scripts/experiments/combinator_relationship_map_v15.py
?? mementum/knowledge/chats/session-219.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "💡 v15's FFN-gate routing lacks the ecosystem combinator shape (it's frozen-extracted)\n\n- NEW instrument combinator_relationship_map_v15.py (register topological/routing):\n  MLX/ternary edition of the combinator map. Loads v15 like exp_b\n  (create_model_with_deltas + checkpoint + reduce_all_deltas), wraps the LIVE\n  stack_c.ffn_gate_plate (s218 orphan lesson — not model.ffn_gate_plate_c),\n  captures sign(gate pre-activation) per crystal probe, computes CMR centroids +\n  9x9 Gram + silhouette null, SAVES centroids_cmr_best (9 x d_ff=5120).\n- RESULT (step_001000, 535 probes, n_outer=2): route_cmr silhouette +0.0021,\n  z=+0.52, p=0.29 — NO significant combinator clustering; CMR does not help (raw\n  z=+0.62). v15-vs-ecosystem-consensus GramCorr only +0.354 (ecosystem internal\n  +0.78). Of the 5 harvest-target positive edges only S-D/B-C are weakly positive;\n  B-D/K-C/S-Y are negative.\n- ARCHITECTURAL CAUSE: v15's FFN is FROZEN-EXTRACTED; only the attention\n  shared_stride_stack is TD-trained (s218). The FFN gate is the untrained generic\n  base → no learned combinator routing, as measured. The ecosystem's shape lives in\n  fully-trained FFN gates.\n- IMPLICATION (blocks harvest-fold as conceived): no v15 FFN-gate frame to align to\n  (non-significant), and cross-architecture dim mismatch (ecosystem d_ff 17408 vs\n  v15 5120) blocks installing the relational consensus as concrete v15 weights.\n  Did NOT fabricate a Procrustes alignment to noise (would be a false positive).\n  Decision point surfaced to Michael.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -1",
  "operation": "commit",
  "summary": "commit v15 map finding"
}
```

**Summary:** Git commit: commit v15 map finding

**Output:**
```
Exit code: 128
Stderr:
fatal: Unable to create '/Users/mwhitford/src/verbum/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

### Thinking

 I ran the add and commit together, which caused them to collide on the git index lock — the commit executed before the files were staged, so it failed. Now that the add has completed and the lock should be released, I'm retrying the commit.

## Assistant

The two git ops collided on the index lock (ran concurrently). Files are now staged; retrying the commit sequentially.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && [ -f .git/index.lock ] && rm -f .git/index.lock && echo \"removed stale lock\" ; git status -s | head"
}
```

**Summary:** $ [ -f .git/index.lock ] && rm -f .gi...

**Output:**
```
Exit code: 0
Stdout:
A  results/combinator-relationship-map/v15_step_001000.json
A  results/combinator-relationship-map/v15_step_001000.npz
A  scripts/experiments/combinator_relationship_map_v15.py
?? mementum/knowledge/chats/session-219.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -1",
  "operation": "commit",
  "summary": "commit v15 map finding"
}
```

**Summary:** Git commit: commit v15 map finding

**Output:**
```
Exit code: 0
Stdout:
[main cc581ac] 💡 v15's FFN-gate routing lacks the ecosystem combinator shape (it's frozen-extracted)
 3 files changed, 631 insertions(+)
 create mode 100644 results/combinator-relationship-map/v15_step_001000.json
 create mode 100644 results/combinator-relationship-map/v15_step_001000.npz
 create mode 100644 scripts/experiments/combinator_relationship_map_v15.py
cc581ac 💡 v15's FFN-gate routing lacks the ecosystem combinator shape (it's frozen-extracted)
```

### Thinking

 I've committed the changes and need to verify that the main branch wasn't affected by my GPU experiments. After that, I'll surface the fork to Michael. I'm at a decision point now: should I probe v15's attention routing to find the combinator shape there as a new instrument, or does the fact that exp_b injects in the FFN layer complicate this approach?

Looking at the options more carefully — I could treat this as a fresh install into the frozen FFN gate and solve the cross-architecture bridge differently, like harvesting the actual FFN-gate centroids and learning a mapping into v15's d_ff. Or I could accept that v15 is too small with a frozen FFN, meaning harvest-into-v15 simply isn't viable and I should redirect toward a from-scratch base that trains its FFN instead. Re-probing at a later checkpoint won't help since the FFN is frozen regardless of training steps. Let me verify main:1 first, then present these options clearly.

## Assistant

Committed (`cc581ac`). Verifying main:1 was undisturbed by the GPU runs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 2>/dev/null | tail -2"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 2>/d...

**Output:**
```
Exit code: 0
Stdout:
2.69e-04 | gnorm 369.33 | 448 tok/s | 🔓 td=0 Δ=0.047 Δx=[0.40987] fp=0.1680 | 109258s
```

### Thinking

 The training run is progressing steadily at around 450 tokens per second with a gradient norm spike that's within normal variation, and the step size increase on this flip is expected. I need to surface these findings to Michael and update the task status—the instrumentation is complete, but the full run revealed a blocking issue that prevents moving forward with the next phase.

## Assistant

main:1 healthy and advancing (109258s, ~450 tok/s) — my GPU runs didn't stall it. Closing out the build/run tasks; task 4 (align+fold+PPL) is now **blocked by the finding** pending your call.

### Thinking

 Now that task 2 is done, I can move forward with completing task 3.

### Thinking

 I'm looking at the task state to understand what actually completed — the first call said it couldn't complete task 3 because task 2 was blocking it, but I need to verify whether task 2 actually finished or if both got rejected.

### Thinking

 I need to finish task 2 before moving on to task 3, since the earlier attempt was rejected due to ordering issues.

## Assistant

Now the decision point. Task 4 (align + fold + PPL) is **blocked by the finding** — proceeding as planned would mean aligning to a non-significant frame, which would manufacture a false positive. This is an architectural/strategic fork, so it's yours to call.

### Tool Call: ask_user (succeeded)


```json
{
  "question": "The harvest-fold's premise is blocked: v15's FFN gate is frozen-extracted, so it carries no learned combinator shape (z=0.52, GramCorr +0.354 vs ecosystem +0.78) — there's no v15 FFN frame to align to, and the cross-architecture dim mismatch blocks installing the relational consensus as concrete weights. More main:1 training won't change this (the FFN is frozen regardless of step). How do you want to proceed?",
  "options": [
    {
      "label": "Probe v15's ATTENTION routing (the trained part) (Recommended)",
      "description": "Build a second capture for the shared_stride_stack attention (what's actually TD-trained) and test whether the combinator shape lives THERE. If yes, the harvest story moves to attention. ~GPU in main:2. Caveat: exp_b's WHNF-verify currently injects in the FFN, so a positive result would need a new attention-side verify path."
    },
    {
      "label": "Reframe harvest as a TRAINING objective, not weight injection",
      "description": "Use the ecosystem's relational consensus Gram as a soft target/regularizer on v15's FFN gate during training (constrain pairwise combinator cosines toward the consensus) rather than direct Procrustes weight injection. Sidesteps the dim mismatch + frozen-frame problem. Larger design effort."
    },
    {
      "label": "Record as a negative result + redirect to the level-4 from-scratch base",
      "description": "Accept the finding: reverse-harvest-into-v15 isn't viable because v15's FFN is frozen and tiny. The reverse-harvest value is for a from-scratch base that trains its FFN. Document the boundary, propose knowledge update, stop the v15 harvest thread here."
    },
    {
      "label": "Something else / let me think",
      "description": "Pause the harvest thread; you'll steer. I'll just make sure everything is committed and state is updated."
    }
  ]
}
```

**Summary:** Q: The harvest-fold's premise is blocked: v15's...

**Output:**
```
User answered: Probe v15's ATTENTION routing (the trained part) (Recommended)
```

### Thinking

 Michael's going with the trained attention routing from v15, so I need to capture what happens in the shared_stride_stack attention routing register and check if it matches the combinator shape. The challenge is figuring out what "routing register" means for attention—in FFNs it was the sign of the gate pre-activation, but for attention mechanisms like FibonacciStrideStack, the routing analog would be the attention pattern itself, which positions are actually attending to which. Let me work through what's actually being trained here. The challenge is that attention weights are the true routing signal, but they're variable-length per position. The cleanest approach mirroring the FFN gate would be to capture the sign of a fixed-dimension projection output at the last token—either the output projection or value path. I need to examine the attention module structure to find the right capture point for this routing register.

## Assistant

You chose the attention probe. v15's attention (the shared-stride stack) is what's actually TD-trained — if the combinator shape lives anywhere in v15, it's there. Let me study the attention structure to pick the right routing register (the FFN-gate analog doesn't directly transfer to attention).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/attention.py",
  "line_offset": 230,
  "limit": 160
}
```

**Summary:** Reading attention.py (230-390)

**Output:**
```
        # Pre-computed indices are cached per seq_len (lazily)
        self._cached_seq_len = -1
        self._cached_indices = None
        self._cached_valid = None
        self._cached_log_distances = None

    def _ensure_indices(self, seq_len: int):
        """Lazily compute and cache expanded stride indices."""
        if self._cached_seq_len != seq_len:
            indices, valid, log_dist = compute_expanded_indices(
                seq_len, self.stride, self.window, self.radius
            )
            self._cached_indices = indices
            self._cached_valid = valid
            self._cached_log_distances = log_dist
            self._cached_seq_len = seq_len

    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W_eff = self.w_eff

        self._ensure_indices(L)
        indices = self._cached_indices       # (L, W_eff)
        valid = self._cached_valid           # (L, W_eff)
        log_distances = self._cached_log_distances  # (L, W_eff)

        x_norm = self.norm(x)

        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        Q = self.q_proj(q_in).reshape(B, L, H, Dh)
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Gather K, V at expanded positions
        GD = H * Dh
        K_flat = K.reshape(B, L, GD)
        V_flat = V.reshape(B, L, GD)

        idx = indices.reshape(1, L * W_eff, 1)  # (1, L*W_eff, 1)
        idx = mx.broadcast_to(idx, (B, L * W_eff, GD))

        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W_eff, H, Dh)
        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W_eff, H, Dh)

        # HPE: rotate K by log-distance × crystal frequencies
        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
        _, K_gathered_rot = apply_hpe_rotation(
            Q_r, K_gathered, log_distances,
            n_pairs=_N_EIGEN_PAIRS,
            freq_scale=self.hpe_freq_scale,
        )

        # Attention scores
        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W_eff, Dh)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale  # (B, H, L, W_eff)

        # Decay bias: -α · log(distance + 1), per-position
        decay_bias = -(_ALPHA * decay_modulation * log_distances)  # (L, W_eff)
        attn = attn + decay_bias[None, None, :, :]

        # Mask invalid positions (out of bounds or non-causal)
        valid_mask = valid[None, None, :, :]  # (1, 1, L, W_eff)
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.clip(attn, -65.0, 65.0)
        attn = mx.softmax(attn, axis=-1)
        if self.dropout is not None:
            attn = self.dropout(attn)

        # Weighted sum of values
        V_r = V_gathered.transpose(0, 3, 1, 2, 4)  # (B, H, L, W_eff, Dh)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)  # (B, H, L, Dh)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out) + self.o_bias


# ══════════════════════════════════════════════════════════════════════
# § 3  GatedLinearAttention — unchanged from v14
# ══════════════════════════════════════════════════════════════════════


class GatedLinearAttention(nn.Module):
    """Gated linear attention at a Fibonacci stride — retrieval via running memory.

    Identical to v14's GLA: running memory per head, associative scan,
    O(d) per position. The stride spacing changes but the mechanism doesn't.
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 55,
        d_state: int = 64,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.d_state = d_state
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.norm = nn.RMSNorm(d_model)
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        self.q_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.k_bias = mx.zeros((n_heads * d_state,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        self._n_heads_padded = ((n_heads + 15) // 16) * 16
        self.gate_proj = TernaryLinear(d_model, self._n_heads_padded, pre_norm=False)
        self.gate_bias = mx.full((n_heads,), -0.5)

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

    def __call__(self, x: mx.array) -> mx.array:
        B, L, D = x.shape
        H = self.n_heads
        Ds = self.d_state
        Dh = self.d_head
        stride = self.stride

        x_norm = self.norm(x)

        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        q_raw = self.q_proj(q_in).reshape(B, L, H, Ds)
        k_raw = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Ds)
        v = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
        gate = mx.sigmoid(
            self.gate_proj(x_norm)[..., :H] + self.gate_bias
        )

        q = nn.elu(q_raw) + 1.0
        k = nn.elu(k_raw) + 1.0

        if stride == 1:
            L_s = L
            kv_outer = k[:, :, :, :, None] * v[:, :, :, None, :]
            gate_expand = gate[:, :, :, None, None]
            gated_kv = gate_expand * kv_outer
            retention = 1.0 - gate
            S_all = parallel_scan_2d(retention, gated_kv)
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)
        else:
            L_s = L // stride
            if L_s == 0:

[CONTENT TRUNCATED] Showing lines 231 to 390 of 555 total lines. Use line_offset=390 parameter to read more content.
```

### Thinking

 I'm seeing how v15 structures its attention mechanisms—there are two types: stride attention and GatedLinearAttention, both used across the FibonacciStrideStack layers. The projections for queries, keys, values, and outputs are trained with TD. For the routing aspect in attention, the Q·K dot product serves a similar gating function to what the FFN gate does for selection, though the dimensionality varies.

Looking at the actual config, there are no GLA layers present—only stride attention layers. So the routing signal I'm looking for comes entirely from the stride attention mechanism. I'm considering three candidates: the output projection's sign at the last token (what the attention writes), the query projection's sign (what the token is looking for), or the attention scores themselves across the window positions (which literally shows which positions get routed to). The attention scores are the most direct routing signal, though they're a softmax distribution rather than a discrete sign.

The key insight is that the FFN's gate projection was the selector, so I should look for the attention's equivalent selector. Since stride attention doesn't have an explicit gate, the query projection—which determines what the attention routes to—is the closest parallel. I'll capture the sign of the query projection output at the last token as my routing register, keeping it fixed-dimensional at d_model=1280.

Actually, the attention output itself (out_proj result) might be cleaner since it's the fully integrated downstream computation. But now I'm hitting a practical problem: the shared_stride_stack has multiple layers across 19 strides, and it gets called multiple times per band in the StrideStackVSM. I need to decide which layer and which invocation to capture. The simplest approach is to pick a specific layer (maybe mid-stack where the combinator signal was strongest) and grab its out_proj output sign from the last token on the final call.

Or I could follow the HF strategy more directly: wrap out_proj at a few representative depths in the shared_stride_stack and let silhouette scoring pick the best one. That's more robust but requires more wrapping. Let me look at the FibonacciStrideStack structure to see how the layers are organized and whether each one exposes out_proj directly.

## Assistant

v15's attention is all stride-attention (config shows "Retrieval strides: []", so no GLA gates). The FFN-gate analog doesn't exist directly; the trained routing lives in the q/k/v/out projections. Let me see the FibonacciStrideStack layer structure to pick capture points.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v15/attention.py",
  "line_offset": 420,
  "limit": 135
}
```

**Summary:** Reading attention.py (420-555)

**Output:**
```
class FibonacciStrideStack(nn.Module):
    """Hybrid stride stack with Fibonacci spacing + neighbor gathering.

    One layer per stride. Composition strides use FibonacciStrideAttention
    (Q·K with neighbor expansion). Retrieval strides use GLA (running memory).
    """

    def __init__(self, cfg: V15Config):
        super().__init__()
        d = cfg.d_model
        n_q = cfg.n_q_mirrors if cfg.use_q_mirrors else 0

        self.layers = []
        self._layer_types = []

        for s, is_ret in zip(cfg.strides, cfg.stride_is_retrieval):
            if is_ret:
                self.layers.append(GatedLinearAttention(
                    d_model=d, stride=s, d_state=cfg.d_state,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("ret")
            else:
                self.layers.append(FibonacciStrideAttention(
                    d_model=d, stride=s,
                    window=cfg.window, radius=cfg.neighbor_radius,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("comp")

        self.combinator_mirrors = [TernaryMirror(d) for _ in range(cfg.n_combinators)]

    def __call__(
        self,
        x: mx.array,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        if stride_range is not None:
            start, end = stride_range
            indices = list(range(start, min(end, len(self.layers))))
        else:
            indices = list(range(len(self.layers)))

        if reverse:
            indices = list(reversed(indices))

        for i in indices:
            x = self.layers[i](x)

        return x


# ══════════════════════════════════════════════════════════════════════
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v15 attention.py self-test (Fibonacci stride + neighbors)")
    print("=" * 60)

    cfg = V15Config()
    B, L, D = 1, 64, cfg.d_model

    # Test expanded index computation
    print("\nExpanded index computation...")
    for s in [1, 3, 8, 13, 34]:
        indices, valid, log_dist = compute_expanded_indices(L, s, WINDOW, NEIGHBOR_RADIUS)
        n_valid = float(mx.sum(valid[L//2]).item())
        print(f"  stride={s:3d}: indices={indices.shape}, valid@mid={n_valid:.0f}/{indices.shape[1]}")

    # FibonacciStrideAttention
    print(f"\nFibonacciStrideAttention (s=1, s=8, s=34)...")
    for s in (1, 8, 34):
        fsa = FibonacciStrideAttention(d_model=D, stride=s, window=WINDOW,
                                        radius=NEIGHBOR_RADIUS, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = fsa(x)
        mx.eval(y)
        assert y.shape == (B, L, D), f"Expected {(B, L, D)}, got {y.shape}"
        print(f"  s={s:3d}: {y.shape} ✓  (W_eff={fsa.w_eff})")

    # GatedLinearAttention
    print(f"\nGatedLinearAttention (s=55, s=144)...")
    for s in (55, 144):
        gla = GatedLinearAttention(d_model=D, stride=s, d_state=64, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = gla(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  s={s:3d}: {y.shape} ✓")

    # FibonacciStrideStack
    print(f"\nFibonacciStrideStack ({N_STRIDES} strides, Fibonacci)...")
    ss = FibonacciStrideStack(cfg)
    assert len(ss.layers) == N_STRIDES
    n_comp = sum(1 for t in ss._layer_types if t == "comp")
    n_ret = sum(1 for t in ss._layer_types if t == "ret")
    print(f"  {n_comp} composition + {n_ret} retrieval = {len(ss.layers)} strides")

    x = mx.random.normal((B, L, D))

    # Test each pass band
    all_bands = list(cfg.stack_a_bands) + list(cfg.stack_c_bands)
    for i, (start, end) in enumerate(all_bands):
        is_desc = i >= len(cfg.stack_a_bands)
        y = ss(x, stride_range=(start, end), reverse=is_desc)
        mx.eval(y)
        assert y.shape == (B, L, D)
        strides_in_band = cfg.strides[start:end]
        print(f"  Pass {i} [{start},{end}) rev={is_desc}: strides {strides_in_band} ✓")

    # Gradient flow
    print("\nGradient flow...")

    class TestGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = FibonacciStrideStack(cfg)
        def __call__(self, x):
            return mx.mean(self.stack(x, stride_range=(0, 4)))

    m = TestGrad()
    mx.eval(m.parameters())
    gfn = nn.value_and_grad(m, lambda m, x: m(x))
    x_test = mx.random.normal((1, 32, D))
    lv, g = gfn(m, x_test)
    mx.eval(lv, g)
    print(f"  loss={lv.item():.6f} ✓")

    print("\n" + "=" * 60)
    print("v15 attention.py: all tests passed ✓")
```

### Thinking

 So the shared_stride_stack contains 19 FibonacciStrideAttention layers, one per stride, each with projection matrices trained via the delta_plates. When the stack processes stride_range bands, it selectively activates layers based on which bands are active, meaning each layer gets called whenever its corresponding stride index falls within an active band across all passes.

For capturing the routing register, I'm weighing which projection best represents the routing decision. The Q projection output at the last token is the strongest candidate since it's analogous to the FFN gate in the HF approach—it determines what the token queries for, essentially "which combinator to apply." The out_proj output represents what was retrieved, which is secondary. I could also use the attention scores themselves (post-softmax weights at the last token), which directly show which positions the token routes to, but those aren't naturally binary like a sign register would be. I'll go with the Q projection as the primary routing signal and potentially expose the out_proj via a CLI flag if needed.

To keep this tractable, I'm going to generalize the existing v15 script to support attention capture across multiple layers rather than writing something from scratch. I'll add a mode flag to choose between FFN gate, attention out_proj, or attention q_proj, then wrap the selected projections at several depth-fraction layers, capture the last-token output sign from each, compute the Gram matrix and silhouette score per layer, and report the best one. Setting up multi-layer capture... Rewriting the whole file to cleanly support the --target flag with attention layer handling.

## Assistant

Now I understand: `shared_stride_stack.layers` is 19 FibonacciStrideAttention layers (one per stride), each with TD-trained q/k/v/out projections. The attention routing register = sign of a trained projection output at the last token. I'll extend the instrument with a `--target` flag (ffn_gate | attn_q | attn_out) and multi-layer capture across the 19 layers (mirroring the HF per-layer best-silhouette approach). The query projection (`q_proj`) is the closest analog to "which combinator to apply."

Let me rewrite the instrument to support both registers.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Combinator relationship map — the v15 (MLX/ternary) edition.\n\nWHY a separate script (s220):\n  combinator_relationship_map.py is HF-only (`AutoModelForCausalLM`, hooks\n  `gate_proj`). v15 is an MLX ternary model with a shared-stride VSM stack and an\n  outer recurrence — a different forward path. To HARVEST ecosystem-consensus\n  combinator structure into the v15 base plate (consensus-delta-folding.md §s220,\n  harvest fold Phase 1) we first need v15's OWN combinator Gram + centroids in a\n  routing register. This produces the target frame for align-before-fold.\n\nTWO REGISTERS (--target):\n  ffn_gate : sign(stack_c.ffn_gate_plate pre-activation), d_ff=5120. The direct\n             analog of the HF gate_proj register. CAVEAT: v15's FFN is\n             FROZEN-EXTRACTED (only attention is TD-trained), so this measures the\n             untrained base. (s220 result: z=+0.52, p=0.29 — NO combinator shape.)\n  attn_q   : sign(shared_stride_stack.layers[li].q_proj output), d_model=1280, the\n  attn_out : sign(...out_proj output). The TD-TRAINED attention routing (the query\n             = which combinator to apply / the integrated attention write). Swept\n             over depth-fraction layers; best by silhouette z. (s220 follow-up:\n             does the LEARNED routing carry the shape the frozen FFN does not?)\n\nCAPTURE MECHANISM (the s218 orphan lesson):\n  We wrap the LIVE module object that the forward actually calls (the reference\n  INSIDE stack_c / inside each stride layer), NOT a top-level model attribute —\n  convert_ffn rebinds the model attribute but the stacks keep their original\n  references (the bug that VOIDed s217 phase-2). The wrapper passes through and\n  stashes the last pre-activation it produced (last band of last outer pass).\n\nLOAD (mirrors exp_b_self_verifying_acceptance.py): cfg=V15Config();\n  create_model_with_deltas(cfg, convert_ffn=True); load_weights(ckpt, strict=False);\n  reduce_all_deltas(model) -> trained operator; n_outer from CLI; fp_lambda=0.\n  Checkpoint is READ-ONLY (the running main:1 training writes step_NNNN/).\n\nUsage (GPU/MLX — run alongside main:1, per Michael s220):\n  uv run python scripts/experiments/combinator_relationship_map_v15.py \\\n      --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz \\\n      --target attn_q --n-outer 2\n  # smoke: add --limit-per 3 --n-perm 50\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\n_V15 = _PROJECT_ROOT / \"scripts\" / \"v15\"\nsys.path.insert(0, str(_V15))\nsys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\n\nimport mlx.core as mx  # noqa: E402\nimport mlx.nn as nn  # noqa: E402\nfrom config import V15Config  # noqa: E402\nfrom td_delta import reduce_all_deltas  # noqa: E402\nfrom train_td import create_model_with_deltas  # noqa: E402\n\nfrom verbum.probes.library import crystal_probes  # noqa: E402\n\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"combinator-relationship-map\"\nCRYSTAL = [\"K\", \"I\", \"B\", \"C\", \"S\", \"D\", \"W\", \"Y\", \"WHNF\"]\nTOKENIZER_NAME = \"Qwen/Qwen3.6-27B\"  # the shards-qwen36 BBPE tokenizer\nLAYER_FRACS = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0]\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# ---- pure-numpy analysis helpers (copied from combinator_relationship_map.py\n#      to avoid importing torch/transformers via that module) -----------------\ndef cmr(X):\n    return X - X.mean(axis=0, keepdims=True)\n\n\ndef unit(v):\n    return v / (np.linalg.norm(v) + 1e-30)\n\n\ndef centroids(X, labels):\n    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)\n    for j, c in enumerate(CRYSTAL):\n        m = labels == c\n        C[j] = X[m].mean(axis=0)\n    return C\n\n\ndef gram(C):\n    U = np.array([unit(c) for c in C])\n    return np.clip(U @ U.T, -1, 1)\n\n\ndef silhouette(X, labels):\n    C = centroids(X, labels)\n    U = np.array([unit(c) for c in C])\n    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)\n    sims = Xu @ U.T\n    lab_idx = np.array([CRYSTAL.index(c) for c in labels])\n    own = sims[np.arange(len(labels)), lab_idx]\n    other = sims.copy()\n    other[np.arange(len(labels)), lab_idx] = -np.inf\n    return float(np.mean(own - other.max(axis=1)))\n\n\ndef silhouette_null(X, labels, n_perm=1000, seed=0):\n    obs = silhouette(X, labels)\n    rng = np.random.default_rng(seed)\n    null = np.empty(n_perm)\n    for i in range(n_perm):\n        null[i] = silhouette(X, rng.permutation(labels))\n    sd = null.std() + 1e-30\n    return {\"silhouette\": obs, \"null_mean\": float(null.mean()),\n            \"null_std\": float(null.std()),\n            \"z\": float((obs - null.mean()) / sd),\n            \"p_value\": float((np.sum(null >= obs) + 1) / (n_perm + 1))}\n\n\ndef classical_mds(D, k=2):\n    n = D.shape[0]\n    J = np.eye(n) - np.ones((n, n)) / n\n    B = -0.5 * J @ (D ** 2) @ J\n    w, V = np.linalg.eigh(B)\n    order = np.argsort(w)[::-1]\n    w, V = w[order][:k], V[:, order][:, :k]\n    w = np.clip(w, 0, None)\n    return V * np.sqrt(w + 1e-30)\n\n\n# ---- probes -----------------------------------------------------------------\ndef load_probes(limit_per: int = 0, seed: int = 0):\n    by = {c: [] for c in CRYSTAL}\n    for p in crystal_probes():\n        if p.combinator in by:\n            by[p.combinator].append(p.prompt)\n    rng = np.random.default_rng(seed)\n    prompts, labels = [], []\n    for c in CRYSTAL:\n        ps = by[c]\n        if limit_per and limit_per < len(ps):\n            idx = sorted(rng.permutation(len(ps))[:limit_per])\n            ps = [ps[i] for i in idx]\n        prompts.extend(ps)\n        labels.extend([c] * len(ps))\n    return prompts, np.array(labels)\n\n\n# ---- live-module capture (wrap the reference the forward actually calls) -----\nclass Capture(nn.Module):\n    \"\"\"Pass-through wrapper that stashes the last pre-activation it produced.\"\"\"\n\n    def __init__(self, inner):\n        super().__init__()\n        self.inner = inner\n        self.last = None\n\n    def __call__(self, x):\n        out = self.inner(x)\n        self.last = mx.stop_gradient(out)\n        return out\n\n\ndef pick_layers(n_layers: int):\n    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))\n                   for f in LAYER_FRACS})\n\n\ndef install_captures(model, target: str, cfg):\n    \"\"\"Wrap the target module(s); return ({key: Capture}, width, label_fn).\"\"\"\n    caps = {}\n    if target == \"ffn_gate\":\n        stack = model.stack_c\n        cap = Capture(stack.ffn_gate_plate)\n        stack.ffn_gate_plate = cap\n        caps[\"ffn_gate_c\"] = cap\n        return caps, int(cfg.d_ff)\n    # attention registers: sweep depth-fraction layers of the shared stride stack\n    layers = model.shared_stride_stack.layers\n    want = pick_layers(len(layers))\n    for li in want:\n        layer = layers[li]\n        if target == \"attn_q\":\n            cap = Capture(layer.q_proj)\n            layer.q_proj = cap\n        elif target == \"attn_out\":\n            cap = Capture(layer.out_proj)\n            layer.out_proj = cap\n        else:\n            raise SystemExit(f\"unknown --target {target!r}\")\n        caps[f\"L{li:02d}\"] = cap\n    return caps, int(cfg.d_model)\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=__doc__)\n    ap.add_argument(\"--checkpoint\", type=str,\n                    default=\"checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz\",\n                    help=\"TRAINED v15 model.npz (READ-ONLY); '' = frozen base only\")\n    ap.add_argument(\"--extracted-model-path\", type=str,\n                    default=\"checkpoints/v15-extracted/model.npz/model.npz\")\n    ap.add_argument(\"--target\", choices=[\"ffn_gate\", \"attn_q\", \"attn_out\"],\n                    default=\"attn_q\",\n                    help=\"routing register to read (attn_* = TD-trained)\")\n    ap.add_argument(\"--n-outer\", type=int, default=2,\n                    help=\"outer recurrence passes (match training K=2)\")\n    ap.add_argument(\"--max-length\", type=int, default=256)\n    ap.add_argument(\"--limit-per\", type=int, default=0,\n                    help=\"cap probes/combinator (smoke)\")\n    ap.add_argument(\"--n-perm\", type=int, default=1000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--tag\", type=str, default=\"\", help=\"output name suffix override\")\n    args = ap.parse_args()\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    t0 = time.time()\n\n    prompts, labels = load_probes(args.limit_per, args.seed)\n    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}\n    log(f\"[v15] {len(prompts)} crystal probes  {counts}\")\n\n    from transformers import AutoTokenizer\n    tok = AutoTokenizer.from_pretrained(\n        TOKENIZER_NAME, trust_remote_code=True, local_files_only=True)\n\n    # ── load v15 exactly like exp_b ──\n    cfg = V15Config()\n    if Path(args.extracted_model_path).exists():\n        cfg.extracted_model_path = args.extracted_model_path\n    log(f\"building v15 operator (n_outer={args.n_outer}) ...\")\n    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)\n    loaded_ckpt = \"\"\n    if args.checkpoint and Path(args.checkpoint).exists():\n        log(f\"  loading TRAINED checkpoint: {args.checkpoint}\")\n        model.load_weights(args.checkpoint, strict=False)\n        mx.eval(model.parameters())\n        n_reduced = reduce_all_deltas(model)\n        log(f\"  folded {n_reduced} trained delta plates into base\")\n        mx.eval(model.parameters())\n        loaded_ckpt = args.checkpoint\n    else:\n        log(\"  no checkpoint — using frozen extracted base only\")\n    model._n_outer_passes = args.n_outer\n    model._fixed_point_lambda = 0.0\n\n    caps, width = install_captures(model, args.target, cfg)\n    log(f\"  target={args.target}  capturing {len(caps)} module(s)  width={width}\")\n\n    # ── forward each probe, capture last-token pre-activations ──\n    reg = {k: np.empty((len(prompts), width), np.float32) for k in caps}\n    plen = np.empty(len(prompts), np.int32)\n    for i, text in enumerate(prompts):\n        ids = tok.encode(text, add_special_tokens=False)[: args.max_length]\n        if not ids:\n            ids = [0]\n        ids = [min(t, cfg.vocab_size - 1) for t in ids]\n        tokens = mx.array(np.asarray(ids, np.int64)[None, :])\n        model._prev_alg_c = None\n        for c in caps.values():\n            c.last = None\n        _ = model(tokens)\n        for k, c in caps.items():\n            mx.eval(c.last)\n            reg[k][i] = np.asarray(c.last[0, -1], np.float32)\n        plen[i] = len(ids)\n        if (i + 1) % 50 == 0:\n            log(f\"    {i + 1}/{len(prompts)}\")\n\n    # ── per-capture routing register: sign, CMR, silhouette, Gram ──\n    per_key = {}\n    best_key, best_z = None, -1e9\n    for k in caps:\n        sign_cmr = cmr(np.sign(reg[k]))\n        sil = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)\n        per_key[k] = sil\n        log(f\"    {k}: route_cmr silhouette={sil['silhouette']:+.4f} \"\n            f\"z={sil['z']:+.2f} p={sil['p_value']:.4f}\")\n        if sil[\"z\"] > best_z:\n            best_z, best_key = sil[\"z\"], k\n\n    # control: raw (no CMR) silhouette on the best key\n    best_sign = np.sign(reg[best_key])\n    sil_full = silhouette_null(best_sign, labels, args.n_perm, args.seed)\n    Cb = centroids(cmr(best_sign), labels)     # (9, width) — harvest material\n    G = gram(Cb)\n    log(f\"\\n  BEST register: {best_key}  route_cmr z={best_z:+.2f} \"\n        f\"(control route_full z={sil_full['z']:+.2f})\")\n\n    D = 1.0 - G\n    np.fill_diagonal(D, 0.0)\n    mds = classical_mds(D, k=2)\n    nn_map = {}\n    for i, c in enumerate(CRYSTAL):\n        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]\n        row.sort(key=lambda x: -x[1])\n        nn_map[c] = row[:3]\n\n    log(\"\\n  Gram (cosine) — the v15 MAP (best register):\")\n    log(\"       \" + \"\".join(f\"{c:>7}\" for c in CRYSTAL))\n    for i, c in enumerate(CRYSTAL):\n        log(f\"  {c:>5}\" + \"\".join(f\"{G[i, j]:+7.2f}\" for j in range(len(CRYSTAL))))\n\n    out = {\n        \"model\": \"v15\", \"register\": \"topological/routing\", \"target\": args.target,\n        \"checkpoint\": loaded_ckpt, \"n_outer\": args.n_outer, \"width\": width,\n        \"n_probes\": len(prompts), \"counts\": counts, \"crystal_order\": CRYSTAL,\n        \"n_perm\": args.n_perm, \"git_sha\": git_sha(),\n        \"best_key\": best_key,\n        \"per_key_silhouette\": per_key,\n        \"route_cmr_silhouette\": per_key[best_key],\n        \"route_full_silhouette\": sil_full,\n        \"map\": {\n            \"gram\": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)\n                                  for j in range(len(CRYSTAL))}\n                     for i in range(len(CRYSTAL))},\n            \"mds_coords\": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),\n                                        round(float(mds[i, 1]), 4)]\n                           for i in range(len(CRYSTAL))},\n            \"nearest\": nn_map,\n        },\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n    ckpt_tag = Path(loaded_ckpt).parent.name if loaded_ckpt else \"base\"\n    tag = args.tag or f\"{args.target}_{ckpt_tag}\"\n    safe = f\"v15_{tag}\"\n    np.savez_compressed(\n        RESULTS_DIR / f\"{safe}.npz\",\n        prompt_len=plen, labels=labels,\n        gram_route_cmr_best=G.astype(np.float32),\n        centroids_cmr_best=Cb.astype(np.float32),\n    )\n    (RESULTS_DIR / f\"{safe}.json\").write_text(json.dumps(out, indent=2))\n    log(f\"\\n  wrote {RESULTS_DIR / safe}.{{json,npz}}  ({out['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/combinator_relationship_map_v15.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/combinator_relationship_map_v15.py && echo \"ruff OK\" && echo \"--- smoke (attn_q, tiny) ---\" && uv run python scripts/experiments/combinator_relationship_map_v15.py --target attn_q --limit-per 3 --n-perm 50 --tag smoke 2>&1 | tail -20",
  "timeout": 600000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
ruff OK
--- smoke (attn_q, tiny) ---
  Gram (cosine) — the v15 MAP (best register):
             K      I      B      C      S      D      W      Y   WHNF
      K  +1.00  -0.22  +0.01  +0.02  -0.21  -0.26  -0.01  -0.21  -0.17
      I  -0.22  +1.00  -0.10  -0.22  -0.09  -0.08  -0.25  +0.08  -0.05
      B  +0.01  -0.10  +1.00  +0.02  -0.34  -0.13  -0.11  -0.23  -0.07
      C  +0.02  -0.22  +0.02  +1.00  -0.09  -0.01  -0.23  -0.40  -0.18
      S  -0.21  -0.09  -0.34  -0.09  +1.00  -0.09  -0.12  +0.01  -0.16
      D  -0.26  -0.08  -0.13  -0.01  -0.09  +1.00  -0.16  -0.10  -0.13
      W  -0.01  -0.25  -0.11  -0.23  -0.12  -0.16  +1.00  -0.06  +0.02
      Y  -0.21  +0.08  -0.23  -0.40  +0.01  -0.10  -0.06  +1.00  -0.14
   WHNF  -0.17  -0.05  -0.07  -0.18  -0.16  -0.13  +0.02  -0.14  +1.00

  wrote /Users/mwhitford/src/verbum/results/combinator-relationship-map/v15_smoke.{json,npz}  (10.6s)
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
```

### Thinking

 The smoke test passed, so now I'm running the full attention query probe set with 535 probes to see if the trained attention captures the combinator shape, then following up with attention output tests. I'll delete the smoke results first and chain both experiments together to avoid reloading the model multiple times, though each run still takes around 110 seconds plus the multi-layer silhouette nulls.

## Assistant

Smoke works (multi-layer attention capture, 10.6s). Running the full `attn_q` (the trained query routing — "which combinator to apply") at 535 probes.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && rm -f results/combinator-relationship-map/v15_smoke.json results/combinator-relationship-map/v15_smoke.npz && echo \"=== FULL v15 attn_q MAP ===\" && uv run python scripts/experiments/combinator_relationship_map_v15.py --target attn_q --n-perm 1000 2>&1 | tail -30",
  "timeout": 900000
}
```

**Summary:** $ rm -f results/combinator-relationsh...

**Output:**
```
Exit code: 0
Stdout:
=== FULL v15 attn_q MAP ===
    L03: route_cmr silhouette=-0.0140 z=+0.75 p=0.2268
    L05: route_cmr silhouette=-0.0016 z=+1.54 p=0.0629
    L08: route_cmr silhouette=-0.0146 z=+0.70 p=0.2468
    L11: route_cmr silhouette=-0.0157 z=+0.59 p=0.2827
    L14: route_cmr silhouette=-0.0176 z=+0.81 p=0.2088
    L16: route_cmr silhouette=-0.0166 z=+0.09 p=0.4655
    L18: route_cmr silhouette=-0.0115 z=+0.74 p=0.2428

  BEST register: L05  route_cmr z=+1.54 (control route_full z=+1.50)

  Gram (cosine) — the v15 MAP (best register):
             K      I      B      C      S      D      W      Y   WHNF
      K  +1.00  -0.05  -0.11  -0.06  -0.13  -0.15  -0.12  -0.24  -0.18
      I  -0.05  +1.00  -0.20  -0.23  -0.01  -0.30  -0.07  -0.15  -0.08
      B  -0.11  -0.20  +1.00  +0.06  -0.03  -0.08  -0.31  -0.06  -0.13
      C  -0.06  -0.23  +0.06  +1.00  -0.05  -0.04  -0.13  -0.24  -0.24
      S  -0.13  -0.01  -0.03  -0.05  +1.00  -0.19  -0.29  -0.03  -0.07
      D  -0.15  -0.30  -0.08  -0.04  -0.19  +1.00  -0.06  -0.13  +0.01
      W  -0.12  -0.07  -0.31  -0.13  -0.29  -0.06  +1.00  -0.08  -0.28
      Y  -0.24  -0.15  -0.06  -0.24  -0.03  -0.13  -0.08  +1.00  +0.01
   WHNF  -0.18  -0.08  -0.13  -0.24  -0.07  +0.01  -0.28  +0.01  +1.00

  wrote /Users/mwhitford/src/verbum/results/combinator-relationship-map/v15_attn_q_step_001000.{json,npz}  (111.9s)
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
```

### Thinking

 The attention query results are similarly underwhelming—the best layer is L05 with a z-score of 1.54, which isn't statistically significant, and all other layers fall below z=1. The silhouette values are negative, indicating the combinators aren't actually clustering together. What's striking is that L05 emerges as the strongest performer here too, matching the earlier finding about a silent selector at that layer, but the z-score of 1.54 barely edges out the raw baseline and doesn't constitute a meaningful improvement.

Now I need to check the attention output projection to see if the integrated attention write carries the combinator structure. If that's also null, it'll confirm that v15 at step 1000 simply doesn't encode the combinator shape in any measurable way.

## Assistant

`attn_q` is also near-null: best layer **L05 z=+1.54, p=0.063** (suggestive — L05 is exactly the HF "SILENT selector" layer from function-discovery — but not significant), all other layers z<1, silhouettes negative. Let me complete the picture with `attn_out` (the integrated attention write).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== FULL v15 attn_out MAP ===\" && uv run python scripts/experiments/combinator_relationship_map_v15.py --target attn_out --n-perm 1000 2>&1 | tail -16",
  "timeout": 900000
}
```

**Summary:** $ echo "=== FULL v15 attn_out MAP ===...

**Output:**
```
Exit code: 0
Stdout:
=== FULL v15 attn_out MAP ===
      B  -0.07  -0.28  +1.00  -0.06  -0.01  -0.14  -0.21  +0.09  -0.09
      C  +0.03  -0.01  -0.06  +1.00  -0.14  -0.13  -0.19  -0.06  -0.38
      S  -0.23  -0.20  -0.01  -0.14  +1.00  +0.12  -0.26  -0.10  +0.11
      D  -0.24  -0.26  -0.14  -0.13  +0.12  +1.00  -0.17  -0.22  +0.18
      W  -0.12  +0.09  -0.21  -0.19  -0.26  -0.17  +1.00  -0.19  -0.28
      Y  -0.19  -0.27  +0.09  -0.06  -0.10  -0.22  -0.19  +1.00  +0.04
   WHNF  -0.34  -0.25  -0.09  -0.38  +0.11  +0.18  -0.28  +0.04  +1.00

  wrote /Users/mwhitford/src/verbum/results/combinator-relationship-map/v15_attn_out_step_001000.{json,npz}  (117.3s)
config.py self-test: ✓
  Strides: (1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597)
  Composition strides: [1, 2, 3, 5, 8, 13, 15, 20, 21, 24, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
  Retrieval strides: []
  Composition range: d=0..11181
  Total range: d=0..11181
  Effective window per stride: 40
```

### Thinking

 I need to pull the best z-score and per-key silhouettes for attn_out from the JSON file, then calculate how each v15 register correlates with the consensus values using GramCorr.

## Assistant

Let me pull the silhouette verdicts + consensus-correlation for all three v15 registers.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json, numpy as np\norder=['K','I','B','C','S','D','W','Y','WHNF']; iu=np.triu_indices(9,1)\ncg=np.array(json.load(open('results/combinator-map-consensus/consensus.json'))['consensus_gram'],float)\nprint(f'{'register':14} {'best':6} {'z':>6} {'p':>6} {'GramCorr_vs_consensus':>22}')\nfor tgt,f in [('ffn_gate','v15_step_001000'),('attn_q','v15_attn_q_step_001000'),('attn_out','v15_attn_out_step_001000')]:\n    d=json.load(open(f'results/combinator-relationship-map/{f}.json'))\n    s=d['route_cmr_silhouette']; bk=d.get('best_key','-')\n    g=np.load(f'results/combinator-relationship-map/{f}.npz')['gram_route_cmr_best'].astype(float)\n    r=np.corrcoef(g[iu],cg[iu])[0,1]\n    print(f'{tgt:14} {bk:6} {s[\\\"z\\\"]:+6.2f} {s[\\\"p_value\\\"]:6.3f} {r:+22.3f}')\nprint()\nprint('ecosystem internal cross-model GramCorr = +0.78 (z ~+4); Qwen3-14B silhouette z=+7.97')\n\""
}
```

**Summary:** $ python3 -c " import json, numpy as ...

**Output:**
```
Exit code: 0
Stdout:
register       best        z      p  GramCorr_vs_consensus
ffn_gate       -       +0.52  0.292                 +0.354
attn_q         L05     +1.54  0.063                 +0.359
attn_out       L00     +0.74  0.221                 +0.324

ecosystem internal cross-model GramCorr = +0.78 (z ~+4); Qwen3-14B silhouette z=+7.97
```

### Thinking

 Looking at the statistical results across all three v15 registers, the attn_q shows the strongest effect with a z-score of +1.54 and a marginal p-value of 0.063, though none of the measures reach conventional significance thresholds. The grammar correlation improvements are consistent across all three, ranging from about +0.32 to +0.36 compared to the baseline consensus.

The key finding is that v15 at step 1000 simply hasn't developed the combinator function shape in any measured register—even the closest candidate in attn_q at layer 5 falls short of significance. This aligns with the earlier observation that the shape requires roughly 4 billion parameters or more to crystallize, and v15's 50 million parameters trained on only 3 billion tokens are insufficient. The faint echo in the attention layer is intriguing, especially since it mirrors the same layer where the function-discovery selector emerged, but it's not a reliable foundation for alignment.

Since there's no significant combinator structure in v15's frame to anchor to, the harvest-fold alignment strategy isn't viable at this checkpoint. I should now commit the extended instrument and both attention results, which completes the empirical investigation—confirming that the attention pathway doesn't rescue the harvest either.

The refined path forward hinges on a crucial distinction: the FFN weights are frozen, but the attention layers are still being trained as main:1 continues. That marginal attn_q signal at layer 5 could strengthen as training progresses toward step 2000 and beyond. Re-probing the attention registers at later checkpoints is a concrete, cheap follow-up that could reveal whether combinator structure emerges as the operator becomes more contractive. Alternatively, if v15 remains too small to crystallize the shape, I'd need to redirect the harvest strategy toward the from-scratch level-4 base instead.

Now I'm committing the instrument and results—the extended script with attention support, plus the attn_q and attn_out snapshots from step 1000 alongside the existing FFN data. Then I'll document the findings and report to Michael with the refined picture and the re-probe follow-up plan.

## Assistant

Now the picture is complete across all three v15 registers:

| register | best layer | z | p | GramCorr vs consensus |
|---|---|---|---|---|
| ffn_gate (frozen) | — | +0.52 | 0.29 | +0.354 |
| **attn_q (trained)** | **L05** | **+1.54** | **0.063** | +0.359 |
| attn_out (trained) | L00 | +0.74 | 0.22 | +0.324 |

**The trained attention does not rescue it** — none reach significance. But there's a genuinely interesting hint: the best signal is `attn_q` at **L05** (z=1.54, p=0.063), which is *exactly* the HF function-discovery "SILENT selector" layer. And critically — unlike the frozen FFN, **the attention is being trained**, so this marginal signal could *emerge* as main:1 trains toward contractivity. At step 1000/5000 (only 20% in), the shape may simply not have formed yet (consistent with s220's scale floor: even Qwen3-0.6B barely had it).

Committing the extended instrument + both attention results.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "💡 v15's TRAINED attention also lacks the combinator shape at step 1000 (attn_q L05 hint)\n\n- Extended combinator_relationship_map_v15.py with --target {ffn_gate, attn_q,\n  attn_out}: attention registers sweep depth-fraction layers of the TD-trained\n  shared_stride_stack (q_proj = \"which combinator to apply\"; out_proj = integrated\n  write), pick best layer by silhouette z. (Michael's call: probe the TRAINED part.)\n- RESULT (step_001000, 535 probes, n_outer=2) — NO register reaches significance:\n    ffn_gate (frozen): best z=+0.52 p=0.29  GramCorr_vs_consensus +0.354\n    attn_q   (trained): best L05 z=+1.54 p=0.063  GramCorr +0.359\n    attn_out (trained): best L00 z=+0.74 p=0.22  GramCorr +0.324\n  Ecosystem reference: Qwen3-14B silhouette z=+7.97; cross-model GramCorr +0.78.\n- The trained attention does NOT rescue the harvest: v15 carries only a faint echo\n  (GramCorr ~+0.35) of the universal shape, far below the ecosystem's internal +0.78.\n- BUT two live threads: (1) the best signal is attn_q at L05 — exactly the HF\n  function-discovery SILENT-selector layer (4.76x separated there); suggestive even\n  at p=0.063. (2) Unlike the FROZEN FFN, attention IS being trained → the shape\n  could EMERGE as main:1 trains toward contractivity (step 1000/5000 = only 20% in;\n  cf. s220 scale floor — even 0.6B barely had it). ⇒ re-probe attn_q/attn_out at\n  later checkpoints is a concrete, cheap follow-up tying combinator structure to\n  contractivity training.\n- Harvest fold remains blocked at step 1000 (no significant v15 frame to align to);\n  did NOT fabricate alignment to a non-significant frame.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/combinator_relationship_map_v15.py results/combinator-relationship-map/v15_attn_q_step_001000.json results/combinator-relationship-map/v15_attn_out_step_001000.json && git add -f results/combinator-relationship-map/v15_attn_q_step_001000.npz results/combinator-relationship-map/v15_attn_out_step_001000.npz && git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -1",
  "operation": "commit",
  "summary": "commit attention map results"
}
```

**Summary:** Git commit: commit attention map results

**Output:**
```
Exit code: 0
Stdout:
[main b72bdea] 💡 v15's TRAINED attention also lacks the combinator shape at step 1000 (attn_q L05 hint)
 5 files changed, 853 insertions(+), 62 deletions(-)
 create mode 100644 results/combinator-relationship-map/v15_attn_out_step_001000.json
 create mode 100644 results/combinator-relationship-map/v15_attn_out_step_001000.npz
 create mode 100644 results/combinator-relationship-map/v15_attn_q_step_001000.json
 create mode 100644 results/combinator-relationship-map/v15_attn_q_step_001000.npz
b72bdea 💡 v15's TRAINED attention also lacks the combinator shape at step 1000 (attn_q L05 hint)
```

### Thinking

 I've committed the changes and now need to update the knowledge base with this new empirical finding from the v15-probe test—documenting the Phase 1 results, the negative findings across registers, and the attention query hints at layer 5 that warrant follow-up probing. I'll also update the state tracking and then notify Michael about the progress.

Before proceeding with the documentation updates, let me verify that the main branch is still stable after running those three GPU experiments.

## Assistant

Committed (`b72bdea`). Updating the knowledge page with the Phase-1 result, then state, then I'll verify main:1 and report.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md",
  "original_content": "- **Phase 3 — verify + fold (DEFERRED, GPU):** WHNF-verify each direction via\n  `forward_metrics` (accept iff Δx_conv does not rise); fold survivors via\n  `DeltaTernaryLinear.reduce()`; measure downstream PPL vs base. **Falsifiable:**\n  does verified ecosystem-consensus add beyond the universal crystal we already hold?",
  "new_content": "- **Phase 3 — verify + fold (DEFERRED, GPU):** WHNF-verify each direction via\n  `forward_metrics` (accept iff Δx_conv does not rise); fold survivors via\n  `DeltaTernaryLinear.reduce()`; measure downstream PPL vs base. **Falsifiable:**\n  does verified ecosystem-consensus add beyond the universal crystal we already hold?\n\n### Phase 1 RESULT (s220, GPU run in main:2) — v15 has NO combinator frame yet\n\nBuilt `combinator_relationship_map_v15.py` (MLX/ternary; wraps the LIVE module the\nforward calls per the s218 orphan lesson; tokenizer Qwen/Qwen3.6-27B). Probed\nv15 step_001000 in THREE routing registers (535 crystal probes, n_outer=2). **None\ncarries a significant combinator shape:**\n\n| register | best | silhouette z | p | GramCorr vs consensus |\n|---|---|---|---|---|\n| `ffn_gate` (FROZEN-extracted) | — | +0.52 | 0.29 | +0.354 |\n| `attn_q` (TD-trained) | L05 | **+1.54** | 0.063 | +0.359 |\n| `attn_out` (TD-trained) | L00 | +0.74 | 0.22 | +0.324 |\n\nReference: Qwen3-14B silhouette **z=+7.97**; ecosystem cross-model GramCorr **+0.78**.\n\n- **The harvest fold's \"align consensus into v15's frame\" has no target frame at\n  step 1000** — every register is non-significant; v15 carries only a faint echo\n  (GramCorr ~+0.35) of the universal shape, far below the ecosystem's internal +0.78.\n  Did NOT fabricate a Procrustes alignment to a non-significant frame (that would\n  manufacture a false positive — λ measure / wrong-register discipline).\n- **Two live threads keep this from being a dead end:**\n  1. The best signal is `attn_q` at **L05** — exactly the HF function-discovery\n     SILENT-selector layer (4.76× separated there). Suggestive even at p=0.063.\n  2. The FFN is FROZEN (won't change with training), but the **attention IS being\n     TD-trained** → the shape may **emerge** as main:1 trains toward contractivity.\n     Step 1000/5000 is only 20% in; cf. s220 scale floor (even Qwen3-0.6B barely had\n     the shape). **Concrete cheap follow-up: re-probe `attn_q`/`attn_out` at\n     step_002000+ checkpoints — does combinator structure co-emerge with\n     contractivity?** This ties the harvest thread to the main:1 recurrence result.\n- v15 may simply be below the scale floor (~50M params, ternary, 3B tokens) to\n  crystallize the shape — in which case reverse-harvest belongs to a from-scratch\n  level-4 base that trains its FFN, not v15.\n- Artifacts (committed `cc581ac`, `b72bdea`): `combinator_relationship_map_v15.py`\n  (--target ffn_gate|attn_q|attn_out); `results/combinator-relationship-map/\n  v15_{step_001000,attn_q_step_001000,attn_out_step_001000}.{json,npz}`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md.
```

### Thinking

 I need to update the state.md file to record that Phase 1 of the s220 harvest-fold is complete with a negative result, and then set up the next action for the following session, which involves re-probing.

## Assistant

Now state.md — marking Phase 1 done with the result and updating next-session actions.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - **Phase 1 v15 Gram (DEFERRED, GPU):** build `combinator_relationship_map_v15.py`\n>   (MLX: `create_model_with_deltas(V15Config())` + `load_weights` +\n>   `reduce_all_deltas`; hook `ffn_gate_plate_a/c`; save centroids). Run on a v15\n>   ckpt READ-ONLY. Phase 2 (CPU): Procrustes-align in 9-d label space + build fold\n>   directions from v15's OWN centroids. Phase 3 (GPU): WHNF-verify via\n>   `exp_b_self_verifying_acceptance.py::forward_metrics` (accept iff Δx_conv doesn't\n>   rise) → fold survivors via `DeltaTernaryLinear.reduce()` → PPL vs base.\n> **COMMITTED** `e48389e` (phase 0 + centroid-save), knowledge reformulation pending\n> in this commit batch. **NOT yet committed (this batch, APPROVED scope):** knowledge\n> harvest-fold reformulation + this state.",
  "new_content": "> - **Phase 1 v15 Gram — DONE (GPU in main:2, Michael OK'd GPU there).** Built\n>   `combinator_relationship_map_v15.py` (--target ffn_gate|attn_q|attn_out; MLX;\n>   wraps the LIVE module per s218 orphan lesson; tokenizer Qwen/Qwen3.6-27B). Probed\n>   v15 step_001000 in 3 registers (535 probes). **★ NEGATIVE: v15 has NO significant\n>   combinator frame** — ffn_gate z=+0.52 p=0.29; attn_q best L05 z=+1.54 p=0.063;\n>   attn_out z=+0.74 p=0.22 (ref Qwen3-14B z=+7.97). GramCorr vs consensus only\n>   ~+0.35 (ecosystem internal +0.78). **⇒ harvest fold BLOCKED at step 1000 — no\n>   target frame to align to; did NOT fabricate alignment to noise.** TWO live\n>   threads: (1) best = attn_q@L05 = the HF function-discovery SILENT-selector layer\n>   (suggestive at p=0.063); (2) FFN is FROZEN but ATTENTION is TD-trained → the\n>   shape may EMERGE with contractivity training (step 1000/5000 = 20% in; cf. s220\n>   scale floor). Committed `cc581ac` (ffn) + `b72bdea` (attn_q/attn_out + instrument).\n> - Phase 2 (CPU)/Phase 3 (GPU) — align → WHNF-verify → fold → PPL — remain DEFERRED\n>   and now CONTINGENT on a v15 frame existing (re-probe later checkpoints first).\n> **COMMITTED** `e48389e` (phase 0 + centroid-save), knowledge reformulation\n> (`b05d32c`), Phase 1 finding (`cc581ac`,`b72bdea`). **NOT yet committed (this\n> batch, APPROVED scope):** knowledge Phase-1-result update + this state."
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
  "original_content": "> (2) **Harvest fold Phase 1 (register topological/routing→functional) ONLY IF main:1\n>   has FREED THE GPU** (completed/paused) — else DEFER: build\n>   `combinator_relationship_map_v15.py`, produce v15's Gram+centroids, then Phases\n>   2–3 (align → WHNF-verify → fold → PPL). Falsifiable: does verified\n>   ecosystem-consensus add beyond the universal crystal? Prescription is ready at\n>   `results/combinator-harvest-fold/prescription.json`.",
  "new_content": "> (2) **Harvest fold — RE-PROBE v15 attention at the next checkpoint** (register\n>   topological/routing; GPU OK in main:2 per Michael): when step_002000 lands, run\n>   `uv run python scripts/experiments/combinator_relationship_map_v15.py --target\n>   attn_q --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_002000/model.npz`\n>   (also attn_out). **Does the attn_q@L05 signal (z=1.54→?) STRENGTHEN as the\n>   operator becomes contractive?** If z clears ~3 (p<.01) → a v15 frame exists →\n>   resume Phase 2–3 (align consensus into it → WHNF-verify → fold → PPL,\n>   prescription at `results/combinator-harvest-fold/prescription.json`). If still\n>   null at step 2000+ → v15 is below the scale floor; reverse-harvest belongs to a\n>   from-scratch level-4 base, redirect (Michael decision)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tmux capture-pane -p -t main:1 2>/dev/null | tail -2 && echo \"--- ckpts ---\" && ls -1 checkpoints/v15-td-outer-k2-fp5-5k/ | grep step_"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 2>/d...

**Output:**
```
Exit code: 0
Stdout:
s

--- ckpts ---
flip_map_step_001000.npz
step_001000
```

### Thinking

 The capture-pane command only returned "s", which is odd. I should verify that the main:1 pane is still active and responsive.

## Assistant

main:1 capture came back oddly truncated — let me verify it's actually alive before committing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== main:1 last lines ===\" && tmux capture-pane -p -t main:1 2>/dev/null | grep -E \"^step\" | tail -3 && echo \"=== process alive? ===\" && ps aux | grep -E \"train_td.*fp5-5k|v15_outer_k2_fp5\" | grep -v grep | awk '{print $2, $11, $12, $13}' | head && echo \"=== log tail ===\" && tail -2 /tmp/v15_outer_k2_fp5_5k.log"
}
```

**Summary:** $ echo "=== main:1 last lines ===" &&...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 last lines ===
step   1440 | loss=8.8374 (avg50: 8.9223) | CE=8.276 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
step   1450 | loss=9.2890 (avg50: 9.1452) | CE=8.100 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
step   1460 | loss=8.9616 (avg50: 9.1538) | CE=8.349 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr
=== process alive? ===
66634 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/v15/train_td.py --steps
66632 tee /tmp/v15_outer_k2_fp5_5k.log 
66631 uv run python
=== log tail ===
step   1450 | loss=9.2890 (avg50: 9.1452) | CE=8.100 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.69e-04 | gnorm 369.33 | 448 tok/s | 🔓 td=0 Δ=0.047 Δx=[0.40987] fp=0.1680 | 109258s
step   1460 | loss=8.9616 (avg50: 9.1538) | CE=8.349 crystal=0.0098(Laplacian-wtd) parity=0.0391 cross_zone=0.0693 | lr 2.68e-04 | gnorm 253.63 | 359 tok/s | 🔓 td=124488 Δ=0.047 etch=76×1638 adam_decay=31094 Δx=[0.35243] fp=0.1242 | 110017s
```

### Thinking

 The main process is running smoothly at step 1460 with good throughput, and the GPU runs didn't cause any stalls. Now I'm committing the knowledge and state updates within the approved thread.

## Assistant

main:1 healthy — step 1460, process alive, advanced normally through all three GPU probes (no stall). Committing the knowledge Phase-1 result + state.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/verbum_commit_msg.txt",
  "content": "🌀 session-220: harvest fold Phase 1 result (v15 has no combinator frame) + state\n\n- consensus-delta-folding.md: Phase 1 RESULT table (3 v15 registers, all\n  non-significant; attn_q@L05 z=1.54 p=0.063 hint at the HF SILENT-selector layer).\n  Harvest blocked at step 1000 — no frame to align to; did not fabricate alignment.\n  Two live threads recorded: attn is TD-trained (shape may emerge with\n  contractivity) → re-probe later checkpoints; else v15 below scale floor.\n- state.md: Phase 1 DONE/negative; next-session action = re-probe attn_q/attn_out at\n  step_002000 (does the L05 signal strengthen as the operator becomes contractive?).\n  main:1 verified alive at step 1460, UNTOUCHED.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/verbum_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/consensus-delta-folding.md mementum/state.md && git commit -F /tmp/verbum_commit_msg.txt && git log --oneline -7",
  "operation": "commit",
  "summary": "commit phase 1 result + state"
}
```

**Summary:** Git commit: commit phase 1 result + state

**Output:**
```
Exit code: 0
Stdout:
[main 4a50d9d] 🌀 session-220: harvest fold Phase 1 result (v15 has no combinator frame) + state
 2 files changed, 63 insertions(+), 16 deletions(-)
4a50d9d 🌀 session-220: harvest fold Phase 1 result (v15 has no combinator frame) + state
b72bdea 💡 v15's TRAINED attention also lacks the combinator shape at step 1000 (attn_q L05 hint)
cc581ac 💡 v15's FFN-gate routing lacks the ecosystem combinator shape (it's frozen-extracted)
b05d32c 🌀 session-220: harvest fold phase 0 + reformulation; state handoff
e48389e 🔄 harvest-fold phase 0: CPU prescription + preserve discarded centroids
0089087 🌀 session-220: consensus-delta-folding §s220 — function shape saturates mid-scale
47c3713 🌀 session-220: state — scale axis completed; function shape saturates mid-scale
```

### Thinking

 Everything's committed now. I need to update the task list since task 4 is blocked pending the re-probe at a later checkpoint — the investigation Michael requested came back showing attention also lacks the shape at step 1000, so there's a decision point about whether v15 falls below the scale floor. Let me mark task 4 as contingent on that future re-probe and close it out. I'll clear the task list since state.md is the authoritative record and nothing executable remains in this session — the re-probe is blocked on step_002000 landing in ~11 hours.

## Assistant

Everything committed. The investigation you asked for is complete. Let me close out the task tracker (the remaining work is blocked on a checkpoint that won't land for ~11h, and the handoff is fully captured in state.md).## Session 220 — harvest fold investigated to a clean verdict

You greenlit GPU in main:2, so I built the v15 probe and ran the full investigation. **main:1 stayed untouched throughout** (verified alive at step 1460, advanced normally through all three ~2-min GPU probes — no stall).

### What I built & found
- **`combinator_relationship_map_v15.py`** — MLX/ternary combinator-map instrument (`--target ffn_gate | attn_q | attn_out`), wrapping the *live* modules (s218 orphan lesson), Qwen3.6-27B tokenizer, saves centroids.
- **Phase 1 verdict — v15 has no combinator frame at step 1000**, across all three registers:

| register | best | z | p | GramCorr vs consensus |
|---|---|---|---|---|
| ffn_gate (frozen) | — | +0.52 | 0.29 | +0.354 |
| **attn_q (trained)** | **L05** | **+1.54** | 0.063 | +0.359 |
| attn_out (trained) | L00 | +0.74 | 0.22 | +0.324 |

*(ref: Qwen3-14B z=+7.97, ecosystem GramCorr +0.78)*

### The honest read
The trained attention **did not** rescue the harvest — v15 carries only a faint echo (~+0.35) of the universal shape. I deliberately **did not** fabricate a Procrustes alignment to a non-significant frame (that's the wrong-register false-positive trap). But two genuinely live threads keep it from being a dead end:
1. The best signal is `attn_q` at **L05** — *exactly* the HF function-discovery SILENT-selector layer. Suggestive even at p=0.063.
2. The FFN is frozen, but the **attention is being trained** — so the shape may *emerge* as main:1 trains toward contractivity (we're only 20% in).

### Next action (in state.md)
When `step_002000` lands (~11h), re-probe `attn_q`/`attn_out`: **does the L05 signal strengthen as the operator becomes contractive?** If z clears ~3 → a v15 frame exists → resume Phase 2–3 (align → WHNF-verify → fold → PPL). If still null → v15 is below the scale floor and reverse-harvest belongs to a from-scratch level-4 base (your call).

**Commits this session (10):** scale axis → consensus → harvest phase 0 → v15 ffn probe → v15 attention probe → knowledge/state, all with the nucleus trailer. Working tree clean except your `session-219.md` chat log (untouched).

One decision is parked for you: **if the step-2000 re-probe is still null, do we redirect reverse-harvest to a from-scratch base, or keep probing later v15 checkpoints?** No need to answer now — it's recorded for next session.