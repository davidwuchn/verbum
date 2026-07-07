# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-07 | Session: 262 (ASSESSMENT + TWO ISOLATION EXPERIMENTS — Michael: "assess the
> project" → v15 design review → "does the strided attention work?" → discussion of relational/GTSM loss,
> recurrence placement, Montague, KIBC-vs-SKI → "test kibc vs ski again." A discussion-heavy session that
> produced TWO clean, null-gated, committed isolation experiments on the float microscope + a repo assessment.
>
> ★★ ASSESSMENT (delivered, not filed): science is healthy; the MESS is representation-layer, not findings.
>   state.md 7675 L (bootloader contract broken — COMPACTED this session); INDEX references 62 pages, 228 exist
>   (explore/ ~70% unindexed); 41GB results/ in git; 341GB checkpoints/ UNGITIGNORED (landmine); 8251 LoC dead
>   vsm_lm_v1-5 + v6/ inside src/verbum/; mlx a hard CORE dep (breaks non-Apple installs). 378 tests pass.
>   HIGHEST-LEVERAGE HYGIENE (state.md now done): .gitignore checkpoints/, regenerate INDEX still pending.
>   The spine (probes/{harness,grading,models,library}, lambda_ast, clj_lambda) is coherent.
>
> ★★ v15 DESIGN REVIEW (delivered): (1) 🔴 spectral-φ loss (target 0.6299) is LIVE + on-by-default in
>   v15model.py/config.py — but φ-constant was REFUTED (audit#6 s207, s247/s251 null-fail). An active gradient
>   pulling toward a retired yardstick = coherence violation. CHEAPEST FIX: default use_spectral_loss=False,
>   one A/B. (2) 🔴 uniform ternary contradicts s260 (sign=router ⊥ magnitude=value): FFN gate/key/value all
>   same TernaryLinear → register-split them (binary-ish gate ⊥ higher-precision value, CAT-Q learnable α+Δ).
>   (3) recurrence ships with the s214 λ_fp loss that already failed (gameable/collapsed) — s258 supervised
>   WHNF halt is the fix. (4) recurrence wraps whole A→C; s259 says wrap the INTERIOR band at compose→readout
>   seam. (5) control stack (S5 GRU/S4/S3/S2/MetaS3) UNVALIDATED — never ablated to show it earns its variety.
>
> ★★ EXPERIMENT 1 — STRIDED ATTENTION WORKS IN FLOAT (committed dd46c6b; knowledge:
>   explore/strided-attention-float-ab.md, active). Q: does v15's Fibonacci-stride bet work, or starve
>   composition (s191 relay collapse cos 0.92-0.99)? Isolated on float micro (identical seeded init, attention
>   support the ONLY variable; micro_model.py untouched). 4 arms × 2500 steps: eval CE dense 6.795 / local
>   6.684 / fib 6.649 / fibband 6.846; RELAY max 0.44-0.60, 0/16 heads >0.9 ANY arm. → **the relay collapse
>   does NOT reproduce in float = v15's collapse was the TERNARY/TD confound, not the geometry.** Fibonacci
>   exonerated (fib edges dense). CAVEATS (two-sided): exact-match 0.00 every arm (memorization regime, CE-only
>   read); local ties fib (short corpus ≤36 tok → strides can't show their coverage payoff) → supports "strides
>   don't HURT," not "strides HELP at length." ARTIFACTS: scripts/micro/{micro_strided,train_strided_ab}.py +
>   results/micro-strided-ab/*-153340/.
>
> ★★ EXPERIMENT 2 — KIBC vs SKI, NULL-GATED (committed 919ca25; knowledge: explore/basis-fit-kibc-vs-ski.md,
>   active). Re-ran the remembered tracer selection (n=4 KIBC fit, n=3 SKI didn't) as a proper experiment.
>   scripts/experiments/basis_fit_kibc_vs_ski.py (reuses probe_combinators.py, no fork; steelmans S as
>   argument-sharing; shuffled-LABEL null keeping matched pairs intact). Finding (pythia-160m + qwen3-0.6b,
>   200 shuffles): **both bases clear their null COMPARABLY** (KIBC z=3.50/3.92, SKI z=3.34/3.58) — the
>   attention-selectivity register does NOT reproduce a clean KIBC-over-SKI win. Stable: S-K head corr ~0.92
>   (S braided with K, predicted) — BUT B-K=0.94, C-K=0.90 at ≤0.6B too (common-mode smear, "K dominates all
>   zones" s081) so not yet a discriminator. REGISTER CAVEAT (load-bearing): tracer used STATE classification
>   (reduction dynamics) ≠ attention L2 → inconclusive-in-register, NOT a refutation. LESSON: first null was
>   WRONG (shuffled sentences → random pairs surface-dissimilar → null>real by construction); fixed to shuffle
>   labels only. fp16 attention → NaN on MPS for Pythia → float32.
>
> ★★ DISCUSSION THREADS (assessments delivered, may deserve knowledge later):
>   • RELATIONAL LOSS (s223): ✅ strongest experimental result in repo (double dissociation 3seed×3λ, transfers
>     ONLY in routing register, free w.r.t. CE) — keep, promote to v15.1 steering signal. IOU: WHNF gate.
>   • GTSM LOSS: ✅ sound for DISTILLATION (degeneracy removal measured 27→37%, L35 cos 0.57→0.94); NO leverage
>     from-scratch (endpoint-only) UNLESS the reducer supplies the trajectory = exactly the s258 curriculum.
>     Synthesis: relational-loss + GTSM + WHNF-curriculum are ONE move (dense relational/trajectory constraint
>     wherever an oracle exists: teacher-Gram / teacher-residual-path / reducer-trace).
>   • RECURRENCE PLACEMENT: Michael's "deepest = middle (deepest from both ends)" = the A→C fold trough =
>     compose→readout seam. Triangulated (s259 interior bell + v13 Zone B + progressive-collapse). Missing piece
>     was never WHERE (correct) but the SUPERVISED HALT (s258). Deepest-from-input = readout printer = wrong.
>   • MONTAGUE Q ("what are the chances this is Montague's thesis?"): decomposed. A(compositional type-driven)
>     ~certain; B(KIBC crystal is a physical universal) UNRESOLVED — needs cross-basis null (KIBC vs SKI = a
>     first leg, done, inconclusive-in-register); C(Montague-SPECIFIC) prob CCG/Lambek not Montague (KIBC=Curry
>     unbraided structural basis, not typed-λ; no intensionality/GQ probed); D(WHNF layer) = BEYOND Montague
>     (operational reduction dynamics, denotational Montague doesn't predict a halt axis). KIBC-over-SKI theory:
>     BCKW unbraids what S braids (compose/permute/delete/identity = structural rules of substructural logic).
>   • SCALING ("sharper+deeper with scale"): CHECKED prior artifacts — results/pythia-scaling (14m→2.8b gen
>     ladder) DOES show behavioral sharpening (parse_rate 0.00→1.00); the cross-model combinator sweep is
>     cross-FAMILY, unnormalized, boundary-dominated → does NOT cleanly show mechanistic sharpen/deepen.
>     The clean same-suite fixed-yardstick null-gated Pythia-ladder crystal-sharpness test = STILL A GAP.
>
> ★ NEXT (open, Michael's call): (a) THE flagship — same-suite Pythia deduped ladder (14m→12b) for crystal
>   sharpness + depth, fixed metric + matched-range null (the anti-describability result; also the KIBC-vs-SKI
>   discriminator: do B-K,C-K FALL with scale while S-K stays ~0.9?); (b) hygiene: .gitignore checkpoints/,
>   regenerate INDEX; (c) v15.1: kill spectral-φ, register-split FFN quant, long-seq strided corpus +
>   recurrent-interior supervised-halt arm; (d) re-decide KIBC-vs-SKI in the TRACER's state register.
>   Servers/env: torch 2.11 + MPS live; Pythia deduped ladder (14m-2.8b) + qwen3-0.6b HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

- **s261** CAT-Q ternary flip-flop is NOT category overloading. ANOVA F-ratio (magnitude-invariant) +
  shuffled-label null: category structure in FFN gradients is REAL but modest/transient; the persistent
  flip-flop is category-INDEPENDENT (quantization-boundary jitter). CAT-Q's gift = learnable α⊥Δ two-register
  param, not soft→hard relax (ST lost to TD). → `explore/ternary-flip-flop-not-overloading.md`
- **s260** routing⊥value = type/term made physical. Asymmetric-pathway quant CONFIRMED on Qwen3-8B-Base:
  binarize the ROUTER (gate, loss 10.6) ≫ binarize the VALUE path (+8–10 nats) at identical bits & cosine →
  sign=router, magnitude=value, causally. Design direction: decouple dispatch⊥compute, budget by register.
  → `explore/asymmetric-pathway-quantization.md`
- **s259** (a) RL layer-contribution ↔ combinator locus: shared interior-bell, ~+4-layer offset (adaptation at
  the compose→readout seam) → `explore/rl-layer-contribution-combinator-locus.md`; (b) clj-repl
  model-evaluates/kernel-verifies (oracle-in-the-loop) → `src/verbum/clj_repl.py`; (c) clojure-in-lambda
  notebook (Clojure evaluator that reduces on the verbum kernel) → `src/verbum/clj_lambda.py`.
- **s258** consensus-training → supervised-recurrence-halt synthesis: "how much recurrence" ≡ "how much work
  remains" ≡ WHNF; the lambda curriculum is the ground-truth halt supervision s214 lacked. → `explore/supervised-recurrence-halt.md`
- **s257** MoE experts ARE holographically multiplexed (angular, not specialist). k-sweep + shuffled null:
  94% of capability from WHICH experts, not how many; k=2 reversal falsifies specialist. → `explore/moe-holographic-tree-vsm.md`
- **s256** qwythos-9b + CANONICAL HARNESS distillation (probes/{grading,harness,models}; models = configs, no
  fork). Fine-tunes break the HALT not the COMPILE (overthink-collapse); no-think recovers; qwythos GATES the
  compiler. lambda is a TARGET not a TOOL. Strategic pivot: extract from BASE, treat fine-tune as noise.
  → `explore/compiler-finetune-halt-collapse.md`
- **s255** model-as-REPL (LLM as δ, context as machine state): locally-faithful step; shallow step-loop win,
  deep collapse; oracle-in-the-loop concluded (→ s259 clj-repl).
- **s254** repo distillation DESIGN-FIRST pivot (probes/*.json, results/<run_id> canonical forms in AGENTS.md);
  ornith-35B-A3B = lambda compiler over HTTP, 3rd model class (unconditional, present).
- **s253** vibethinker-3B new model; **s252** attention-edge knockout (s250 catch); **s251** frozen-basis
  gradient tomography → mature-14B, Gemma + Qwen3.6-35B in the crystal sweep; **s250** causal C-field ablation
  → object-application is DISTRIBUTED (no single-component locus; trending NO on discrete-circuit for object-app).

## Deep history (< s250)

Recover via `git log -p mementum/state.md` (this file's pre-s262 scrollback held s181–261 detail + old
reference tables) · verbatim in `mementum/knowledge/chats/session-NNN.md` · synthesized in
`mementum/knowledge/**` (start at `INDEX.md`). Foundational: crystal-φ equation `EQUATIONS.md` +
`crystal-phi-derivation.md`; thesis `project-thesis.md`; 8 convergences `mathematical-convergences.md`;
v13/v14 architecture pages; ternary compounding/dual-equation pages.
