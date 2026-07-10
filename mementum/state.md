# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-10 | Session: 263 (J-SPACE ↔ OPCODES — Michael: found `babel-codec-gpt2` (external
> GPT-2 residual→English decode project) → "how did it test, did it train tensors?" → "extend our monitor to
> read states?" → Anthropic j-space paper (Jacobian Lens, 2026-07-06) → "can we see state forming around
> combinators?" → "reasoning traces not mechanical?" → "run j-space on qwen3.6-27b" → "what IS j-space if the
> model does KIBC natively?" → "build the Jacobian opcode probe, reuse probes." Built 2 monitors + 3 null-gated
> experiments on qwen3.6-27b. Full synthesis: `explore/opcode-jacobian-jspace.md`.)
>
> ★★ THEORY (the session's spine, definitionally solid): **opcode = routing-Jacobian STRUCTURE; J-space = the
>   Jacobian's LIVE SUBSPACE.** Combinators ARE Jacobian patterns: I=identity, K=rank-deficient (annihilate
>   discarded arg), B=chain-rule PRODUCT (composition = Jacobian multiplication), C=argument-slot PERMUTATION,
>   S=path-SUM over a shared arg (nonlinear → a 1st-order Jacobian UNDER-READS S; re-explains s262 S-K braid).
>   So ∂out/∂arg IS the opcode read. Anthropic's J-lens projects the Jacobian onto TOKEN-readable dirs →
>   OPERANDS (J-space = the typed-value bus / workspace); we want the OPERATOR projection → structural
>   decomposition. Same instrument, two faces. 3-zone geography (sensory/workspace/motor) = the reduction
>   pipeline (parse args / hold typed intermediates / collapse to normal form). λ types = block structure of
>   the Jacobian. (External context: `babel-codec-gpt2` reviewed — rigorous pre-reg/null/hash method, but
>   headline "39/39" rides a RECALIBRATED floor = λ yardstick smell; method borrowed, claims NOT adopted.)
>
> ★★ TOOLING (committed, reusable, self-tested). REGISTER MAP now 4 (λ measure — do not conflate):
>   attention-routing ∥ reduction-state ∥ residual-value/broadcast (jlens) ∥ input-attribution (jacobian).
>   • `src/verbum/jlens.py` = J-space monitor on hooks.py: capture_residuals (all layers, accepts input_ids),
>     logit-lens `verbalize`, `broadcast_kl` (substitution-KL = 1st-order Jacobian proxy), identity-inject
>     exact-zero self_test (gate stolen from babel).
>   • `src/verbum/jacobian.py` = `input_attribution` (autograd ∂logit/∂input-embed per position) + structural
>     metrics concentration(K)/copy_mass(I)/attr_range(B)/front_bias(C) + self_test on ideal attributions.
>
> ★★ EXP 1 — `jspace_combinators` (broadcast+verbalize per layer, KIBC+S dirs; qwen3.6-27b): **NULL** (committed).
>   Combinator dirs DO broadcast above matched-random (B R=2.62 z=10.6 @L11; I R=1.41 z=3.5 @L10) but NONE beat
>   the shuffled-LABEL null → broadcast is a GENERIC active/control effect, not combinator identity (same lesson
>   as s262: label-null load-bearing). verbalize thread (I→twice/consistently, B→knows/wrote) = echo-suspect,
>   untested. → `results/jspace-combinators/`.
>
> ★★ EXP 2 — `jspace_normalform` (Michael's hypothesis: residual token-repeat = I = normal-form identity-hold =
>   J-space MOTOR zone; qwen3.6-27b 64L): **I-COMBINATOR-VISIBLE, then REFINED** (committed). copy/induction
>   reaches normal form EARLIER (top1-conv frac 0.879 vs compose 0.953) and HOLDS ~2.6× longer (hold_frac 0.121
>   vs 0.047) — directionally as predicted. REFINED (honest): it's a LATE-stack PLATEAU (~last 15% of layers),
>   NOT most-of-network parking. Induction KL(final‖lens) flat ~10 nats to L48 then SHARP CLIFF (L52→63) = copy
>   written by a narrow late mechanism then held; compose resolves ONLY final layers (Paris L58, cold L57) =
>   depth IS reduction steps for hard compositions. DESIGN: bounded depth-adaptive/early-exit (exploitable
>   identity ≈ last 10-15%, onset regime-dependent, cannot exit before the cliff). CAVEAT: raw logit-lens KL
>   baselines differ by regime (calibration artifact) — only settle TIMING trustworthy → tuned lens next;
>   compose n=6 underpowered. → `results/jspace-normalform/`.
>
> ★★ EXP 3 — `jacobian_opcodes` (input-attribution structural signatures, opcode×metric matrix; qwen3.6-27b):
>   **PARTIAL / confounded** (committed). Only I clears its predicted diagonal (copy_mass z=3.40,
>   diagonal-dominant); K/B/C predicted metrics ≈ 0 (concentration −0.10, range +0.21, front_bias +0.04) =
>   signatures ABSENT. CONFOUND: copy_mass is the argmax for ALL 5 combinators → generic active/control mover,
>   not identity-specific; I "wins" only by predicting the generic metric. DIAGNOSIS (thesis NOT refuted — grain
>   wrong): (1) last-token readout aggregates the whole sentence, dilutes the mid-sentence op → attribute at the
>   RESULT position; (2) probes not repetition-controlled → copy_mass confound; (3) aggregate metrics too coarse
>   for position→position routing. SYNTHESIS: at crude token-saliency grain opcodes DON'T carve (EXP1,EXP3) —
>   consistent with thesis (opcode structure is FINER: inter-layer Jacobian / position-targeted), not against.
>   → `results/jacobian-opcodes/`.
>
> ★ NEXT (open, Michael's call): (A) position-targeted + repetition-matched attribution — annotate each probe's
>   operation RESULT position, attribute there, rebuild KIBC probes with matched token-repetition (cheap, reuses
>   jacobian.py); (B) the REAL inter-layer Jacobian — ∂h_{L+1}/∂h_L at compose sites, SVD, classify structure vs
>   KIBC signatures (rank-deficiency/factorization/permutation/path-sum) — heavier, where the theory lives;
>   (C) tuned lens (Belrose) for clean mid-stack reads (rescues EXP2 magnitudes + EXP1 verbalize echo-test).
>   Lean A→B. Prior-arc NEXT still open: same-suite Pythia ladder crystal-sharpness (flagship); v15.1 (kill
>   spectral-φ, register-split FFN quant, supervised-halt interior recurrence); INDEX regen.
>   Env: torch 2.11 + MPS, 512GB RAM; qwen3.6-27b (52GB bf16, loads ~9-60s) + qwen3-{0.6,4,14}b + pythia
>   deduped ladder (14m-2.8b) HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

- **s262** ASSESSMENT + 2 isolation experiments. Repo assessment: science healthy, the MESS is
  representation-layer (INDEX stale 62/228 pages, ~8251 LoC dead vsm_lm_v1-5+v6/, mlx a hard core dep; 378
  tests pass, spine coherent). ❌ my "checkpoints landmine / results-in-git" claim was FALSE — propagated an
  agent assertion unverified (λ assert violation); hygiene is actually GOOD. EXP1 STRIDED ATTENTION WORKS IN
  FLOAT (relay collapse s191 was the TERNARY/TD confound, NOT geometry; Fibonacci exonerated) →
  `explore/strided-attention-float-ab.md`. EXP2 KIBC-vs-SKI NULL-GATED: both bases clear COMPARABLY in the
  attention-selectivity register (KIBC z=3.50/3.92, SKI z=3.34/3.58) = inconclusive-IN-REGISTER, not a
  refutation; S-K corr 0.92 but B-K/C-K also ~0.9 → not yet a discriminator → `explore/basis-fit-kibc-vs-ski.md`.
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
