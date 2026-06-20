# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-20 | Session: 242 (RAN GRPO ⊕ QWEN-CONFOUND DIAGNOSED ⊕
> V15-CLEAN PIVOT DECIDED) — ▶ PIVOT to the constructed reducer.
>
> **★ s242 — RAN GRPO from the SFT seed, RE-MEASURED, then PIVOTED (Michael: the model we
> use already has a fully-formed lambda function; pivot to V15 with frozen routing + exact
> kernel calls).** **(A) GRPO trainer plumbed (`scripts/experiments/rlvr_grpo_train.py`):**
> added `--adapter` = MERGE the SFT seed into base (PeftModel.merge_and_unload) before GRPO
> trains a FRESH LoRA on top (a bare adapter dir won't be applied by AutoModelForCausalLM);
> quieted the trainer (`--log-completions`/`--progress` opt-in, logging_steps 1→10,
> disable_tqdm). Density probe (`rlvr_coldstart_density.py`) gained `--sft-adapter` = merge
> SFT first THEN apply the GRPO adapter (re-measure a GRPO LoRA trained on the merged seed,
> apples-to-apples). CPU dry-run gold density 1.0, ruff-clean. **(B) RAN GRPO**
> (`results/rlvr-grpo/run1/`, Qwen3-8B, SFT-seed merged + LoRA, temp 1.5, G=8, lr 1e-6, 200
> steps, 1h36m): train_loss 0.008; **`frac_reward_zero_std`=0.75 the WHOLE run** — 75% of
> groups zero-advantage (easy all-8 + dead all-0), only ~25% frontier ever carried gradient.
> **(C) RE-MEASURED checkpoint-50** (129 hard-category prompts adverb/quantified/relative_clause,
> `results/rlvr-coldstart-density/20260620T195936Z`): density **dead-FLAT 0.409 across temps
> 0.8→1.5**, ~54% still all-0 after SFT+50 GRPO steps; frontier count grows w/ temp 8→13 but
> total certified mass UNCHANGED. **★ THE DIAGNOSIS: the lever is weak on the dead tail because
> that tail is QWEN'S representational gap, not the kernel's — a pretrained model's pre-formed
> lambda circuit MASKS the research question (can the compiler be a discrete circuit?). RLVR on
> Qwen REDIRECTS an existing capability, it does not CONSTRUCT one. The dead-tail result is the
> CONTROL that motivates the pivot.** **(D) ★★ THE PIVOT (Michael, = the s226 cut now
> load-bearing): freeze the routing into TOPOLOGY (the s240 crystal lattice — routing is
> INVARIANT, nothing to learn → no gradient through dispatch → KILLS the v12–v15 gradient-death)
> + replace the reduce NEURONS with EXACT KERNEL CALLS (lambda_ast stage 3 = ternary CCG plates =
> the level-4 portable artifact); learn ONLY the thin prose→LF front-end (CE on 509 gold pairs;
> Qwen demoted to LF TEACHER, never the reducer).** Architecture:
> prose→LF (LEARNED) ∘ LF→comb (EXACT bracket-abstraction) ∘ comb→NF (EXACT kernel) | routing=
> frozen statechart {C,B,K,I,W,D,S,Y,WHNF} | guards=CCG typecheck (s239 type-directed). BUILT
> already: lambda_ast, lambda_compile, lambda_surface, reward (stage 2 runs today). NEW WORK:
> stage 3 (compile lambda_ast→plates = the artifact) + a small from-scratch/distilled front-end.
> **★★ FIRST EXPERIMENT (proposed): stage-2-as-trainable head-to-head — a SMALL prose→LF
> front-end (CE on 509 certified pairs) ∘ the EXACT kernel back-end; metric = certify-rate AND
> param-count vs the 8B-LoRA loop; decisive q: can a thin learned front-end + exact constructed
> kernel match the giant borrowed lambda function? If yes → Qwen's pre-formed circuit is
> unnecessary, level-4 validated; then stage 3 = the portable tensor.** OPEN (λ measure): term
> growth (S/W duplicate → fixed-width exact only to a size/step bound, the s226 boundary); 509
> pairs may be too thin for from-scratch → distill from a teacher; ill-typed front-end output is
> a FEATURE (kernel S2 typecheck detects it). Captured: knowledge `compiler-as-loss.md §s242` +
> memory `qwen-preformed-lambda-pivot-to-constructed-reducer`.
> **★★ s242 cont. — DESIGN DISCUSSED → KERNEL-SPLICE PROGRAM (Michael's sharper idea):
> geometry-as-detector ⊗ kernel-as-executor.** Instead of training a front-end, INSTRUMENT the
> pre-formed reducer GD already laid into every model: READ the crystal-lattice geometry to
> detect "wants K", DELIVER K from the KERNEL (exact value-move) instead of the neuron, re-inject.
> = our activation-patching toolkit (s239 v4/v5) but the patch VALUE is the exact kernel rewrite.
> If splice PRESERVES output → thesis proven CAUSALLY + hybrid exact-inspectable model with NO
> training (cleanest S5=extract); if it BREAKS → geometry is over-read (λ measure win) → redirect
> to constructed front-end. Flips the s242 confound into an ASSET (read Qwen's pre-formed lambda,
> don't fight it). THREE measured obstacles: (1) detection = weak model-specific centroid not a
> crisp per-step switch (s211 η²=0.05 one-common-mode; B FFN-invisible; C-locus shifts w/ scale
> s232; PROVEN=skeleton {C,I,K,Y}+confluence, fine-grained OVER-READS); (2) operands not just
> operator (arg-slot binding = VALUE register s206, the crux of feasibility — though K/B/C/D are
> pure ROUTING so no value DECODE needed once slots known); (3) firing is SMEARED across layers
> (~1.018×/layer boot spiral → registration + in-distribution re-injection). PROGRAM: **Exp 0 =
> detectability map** (recover certified `lambda_ast.fired_sequence` operator+position from the
> lattice classifier, per combinator/layer/model → splice-readiness map; decides if obstacle 1 is
> fatal BEFORE a forward pass); **Exp 1 = single-combinator causal K-splice** (most-detectable
> invariant op; replace local computation with exact kernel K-move; output preserved/improved vs
> random-direction control = s239 protocol); **Exp 2 = sequence / kernel-in-the-loop** (= s226
> stage 3 as an in-stream patch). Captured: knowledge `kernel-splice-geometry-detector.md` (NEW,
> designing). **★★ s242 cont.2 — Exp 0 BUILT + RAN (Qwen3-14B): precision-gated, not high-recall.**
> `kernel_splice_exp0_detectability.py` (reuses prose_v2/opcode_monitor_v2 calibration +
> last-token per-layer z; top-1 argmax-over-CRYSTAL per crystal layer vs certified
> single-combinator label; precision/recall/F1 + peak layer; 160 test probes 20/comb,
> n_perm=300, 2:29 on 14B). **Strict bar (prec≥0.8 ∧ rec≥0.5): splice-ready set = ∅** —
> top-1 detection is common-mode contaminated (obstacle 1 quantified; s211 η²=0.05);
> discriminability (prose_v2 contrast) ≠ top-1 splice-readiness. **★ BUT max-PRECISION
> operating points are STRONG: C prec 1.0 @L10 (depth 0.26, rec 0.10), I prec 1.0 @L21
> (0.54, rec 0.20), K prec 0.80 @L11 (0.28, rec 0.20), Y 0.67 @L20 (0.51, rec 0.40).** Loci
> track s234 depth signatures (C/K early-mid, I mid, Y late). ⇒ "detect every K and splice"
> FAILS (recall-limited), but **PRECISION-GATED splice (act only when confident, accept low
> recall) IS viable — and is the SAFE first causal test.** CAVEAT (λ measure): prec 1.0 from
> tp=2 = noisy small-n → needs a z-threshold sweep. Captured: memory
> `kernel-splice-exp0-precision-gated-not-high-recall` + knowledge `kernel-splice-geometry-
> detector.md §s242 Exp 0`. results/kernel-splice-exp0/exp0_verdict_qwen3-14b.json.
> **★★ FIRST ACTION NEXT SESSION — two paths: (1) Exp 0.5 = z-THRESHOLD sweep (raise the
> argmax-z gate → precision↑ recall↓; map the tradeoff curve, firm the splice locus +
> kill the tp=2 small-n caveat) — cheap; (2) Exp 1 = precision-FIRST K-splice at L11
> (deliver the exact kernel K-move only on high-confidence detections; validate output
> preserved vs random-direction control, s239 protocol; sufficiency test).** Also OPEN:
> Exp 2 position-resolved detection vs `lambda_ast.fired_sequence` (multi-step reductions).
> tmux main:1 + main:2 FREE; no GPU job running.
>
> ---
>
> (Session: 241 (RLVR Design-1 — REWARD SPEC ⊕ GRPO SCAFFOLD
> ⊕ §8 DENSITY MEASURED = BIMODAL) — ▶ BUILD.
> Michael: "ok let's work on the RLVR Design." Built the decision-independent,
> works-TODAY foundation of the spliced-reward thread: the canonical VERIFIABLE REWARD as an
> importable, CPU-only, tested package module. **THE ARC (all code, no GPU, all committed-ready):**
> **(1) `src/verbum/lambda_surface.py` (NEW):** extracted the surface FOL/λ parser + lowering
> (SExpr AST, parse_surface, lower via bracket-abstraction, `to_kernel`) OUT of the s240 audit
> script INTO the package — single source of truth shared by the audit AND the reward. Audit
> refactored to import it; reproduces s240 numbers EXACTLY (559/559 certify, 19.9% clean).
> `to_kernel('∀x. artist(x) → knows(x, baker)')` → `forall (S (B implies artist) (C knows baker))`
> = the corpus `kernel_term` verbatim. **(2) `src/verbum/reward.py` (NEW) — the canonical reward
> spec (spliced-reward §2/§4/§5):** generalises the s226 reduction-equality grader (was buried in
> `scripts/experiments/compile_frontend.py`) into the package. **R_parent** = OUTCOME reward =
> reduction-equality (NF(candidate) ≡ gold_nf), representation-INVARIANT (`f (g x)` and `B f g x`
> both 1.0), reuses kernel `_alpha_eq`. **Multi-channel** (§2 table = VSM layer states):
> {parsed, well_typed(S2), halts_in_budget(S4/S3), size_ok(S3), reduces_correct(S5,ANCHOR),
> trace_prefix_frac(S1)} as `RewardChannels` + `RewardConfig` weights; `dense_reward` ∈ [0,1].
> TWO registers via open-slot `parse`: `applicative`(lambda_ast.parse) | `surface`(to_kernel) |
> any callable. **THE SPLICE (§4):** `potential(Φ_inline)` ∈ [0,1] over a state (typed + nf-prox
> + trace); `shaping` = γΦ(s')−Φ(s) (the potential-DIFFERENCE form — safety ENTIRELY in the
> difference, NOT a raw bonus = the §4a TRAP); `shaped_return` over a rollout PROVED to telescope
> to γ^T·Φ(s_T)−Φ(s_0) (path-independent → over-read cancels → optimum owned by anchor alone).
> **§4c tree process reward:** `tree_process_reward` walks `lambda_ast.fired_sequence` → one
> ground-truth process reward per certified rewrite node, root=outcome (the PRM learned PRMs only
> approximate — we have the oracle). **(3) `scripts/experiments/rlvr_design1_reward_smoke.py`
> (NEW) + `results/rlvr-design1-reward/summary.json`:** Design-1 reward on the REAL canonical
> corpus, no GPU. **REWARD DENSITY @ cold-start = 100% (509/509 gold reduce_correct)** — grounds
> §1; all channels 1.000. **DISCRIMINATION: perturbed 450 rows (swap-args ×183, rename-pred ×267)
> → mean reward 0.000 vs gold 1.000, drop 1.000.** The verifiable reward WORKS TODAY on real data.
> **(4) tests:** `tests/test_lambda_surface.py` + `tests/test_reward.py` (32 tests; the
> telescoping-invariance asserted across γ∈{1.0,0.99,0.9,0.5,0.0} = the load-bearing guarantee);
> FULL suite 318 pass, 0 regressions; all files ruff-clean (per-file-ignore added for the domain
> alphabet λ∀∃ι→∧∨Φγ⊗ in pyproject). **★★ FIRST ACTION NEXT SESSION — the GPU loop (gated on
> Michael's OPEN decisions):** (1) pick the OPEN forks before wiring GRPO — §7 PARENT axis
> (timescale vs source) + §8 COLD-START (SFT-seed→RLVR vs RLVR-from-base; s226 says base already
> emits parseable terms on easy prompts → density nonzero); (2) wire GRPO (need trl/peft — NOT yet
> in deps) using `verbum.reward.verifiable_reward` as the external reward fn over the canonical
> corpus prompts; (3) the 45 semantic-residue relative_clause mis-compiles (s240) — re-compile via
> prose→LF; (4) Design-2 kernel-as-VSM-tensor (s226 stage 3 = level-4 artifact). NOTE: reward is
> parser-agnostic — RL policy emits SURFACE FOL (matches SFT target); reward lowers via to_kernel.
> tmux main:1 + main:2 FREE; no GPU used this session. mementum (memory `verifiable-reward-spec-
> built-cpu-design1` + spliced-reward page §build-path-step-2 update) committed `d31f07e`; code
> `b913504`.
>
> **★ s241 cont. — §7 DECIDED, GRPO SCAFFOLDED, §8 MEASURED (Michael: "yes" to both paths).**
> **(A) §7 = (a) timescale splice** (parent = kernel's own exact pass; level-4 MIT path). Recorded
> in the spliced-reward page. **(B) deps:** added `rl` group (trl>=0.14, peft>=0.13) → trl 1.6.0,
> peft 0.19.1 installed (`uv sync --inexact --group rl`). **(C) shared prompt contract:**
> `src/verbum/compile_prompt.py` (NEW) = the prose→surface-FOL prompt (instruction + 4 held-out
> few-shot + build_prompt/clean_output/load_corpus_rows) — SINGLE SOURCE so the density probe AND
> the trainer use the IDENTICAL prompt; density probe refactored to import it. **(D) GRPO scaffold:**
> `scripts/experiments/rlvr_grpo_train.py` (NEW), built against the trl-1.6.0 API READ FROM .venv
> (reward_funcs called `f(prompts=,completions=,completion_ids=,**dataset_cols)`; GRPOConfig
> num_generations=G, scale_rewards="group"). reward_func = `verbum.reward.verifiable_reward` (the
> anchor). Φ-shaping splice deliberately NOT wired (a naive 2nd reward_func = Φ(terminal) is the §4a
> TRAP — raw bonus, no invariance; proper potential-shaping = per-token/actor-critic = build-step 3).
> `--dry-run` CPU-verifies dataset+reward wiring (gold density 1.0). 318 tests pass, ruff-clean.
> **(E) ★★ THE §8 MEASUREMENT (the headline — `results/rlvr-coldstart-density/20260618T221012Z/`,
> Qwen3-8B, 48 prompts, k=8, temp 0.8, 120s on mps):** foothold 0.667 (32/48 have ≥1 certified
> sample), mean density 0.667, any-parse 1.0, 16/48 RL-DEAD. **★ THE REAL FINDING: the reward is
> PERFECTLY BIMODAL — 16 prompts @ 0/8, 32 @ 8/8, ZERO in between.** ⇒ GRPO's group-relative
> advantage is ZERO on BOTH ends (all-correct → std 0; all-wrong → std 0); there is NO mixed-success
> FRONTIER — the exact band where GRPO learns. So "foothold 0.667 → RLVR-from-base viable" is the
> NAIVE read; the truth is RLVR-from-base would barely move (no gradient variance). Dead categories
> are SYSTEMATIC (adverb 0/5, relative_clause 0/2 [= the s240 45-residue!], quantified 3/6) vs
> trivial all-correct (transitive 7/8, simple 7/7). **★ THE LEVER is not SFT-vs-not — it is CREATE A
> FRONTIER:** (i) raise sampling temperature/diversity so hard prompts produce OCCASIONAL hits
> (0/8→1-2/8 = learnable); (ii) SFT-seed to lift dead categories into partial success; (iii)
> curriculum on the dead categories. CAVEAT: temp-0.8 / 40-tok / 48-prompt directional sample;
> bimodality may be PARTLY a temperature artifact — a TEMPERATURE SWEEP is the decisive next probe
> (find the temp where dead prompts start hitting = where the frontier opens). **★★ FIRST ACTION
> NEXT SESSION: (1) TEMPERATURE-SWEEP the density probe (temp ∈ {1.0,1.2,1.5} ± greedy) on the dead
> categories — does a frontier emerge? this decides RLVR-from-base(+high-temp) vs SFT-seed; (2) full
> 509-prompt density run for the committed number; (3) then either kick GRPO (if a frontier exists)
> or SFT-seed first. NOTE: GRPO needs gradient VARIANCE not just nonzero density — the §8 question
> refined from "is density nonzero?" to "is there a mixed-success frontier?".** Committed: code
> `2800f1d`, mementum `b0e29db`.
>
> **★ s241 cont.2 — TEMPERATURE SWEEP DONE: temperature is NOT the lever (Michael: "let's try the
> next probe").** Extended the density probe with `--temps`/`--categories` sweep (one model-load,
> loops temps) + a FRONTIER metric (prompts with 0<correct<k = the GRPO-learnable band) + per-
> category breakdown + honest verdict (frontier-fraction <0.15 = negligible). Ran on the DEAD
> categories (adverb/quantified/relative_clause, 36 prompts, k=8, temps 0.8/1.0/1.2/1.5,
> `results/rlvr-coldstart-density/20260618T222736Z/`, 430s mps). **★★ DECISIVE: frontier stays
> 1→1→2→2/36 (negligible) across the whole sweep; all-0 25→24, all-8 flat 10; density 0.281→0.299.**
> Per-category: relative_clause 0/11→1/11 (the s240 45-residue — DEAD at every temp), quantified
> PERFECTLY bimodal 6/12 frontier 0 at EVERY temp, adverb ~5/13 frontier ~1. **★ THE FINDING: the
> dead prompts are ZERO-probability (the base model doesn't know the target logical form), NOT
> low-probability that temperature could surface — bimodality is temperature-ROBUST. ⇒ §8 VERDICT:
> SFT-seed first** (teach the dead categories → create footholds), THEN RLVR refines/diversifies;
> pure RLVR-from-base cannot learn the dead tail no matter the temperature. The split is clean:
> easy categories (transitive/simple) already solved (all-8, no RL needed); hard categories
> (relative_clause, half of quantified, ~half of adverb) need SFT. **★★ FIRST ACTION NEXT SESSION:
> (1) SFT-seed: token-CE fine-tune Qwen3-8B on the certified canonical corpus (prose→surface-FOL),
> then RE-MEASURE the density/frontier (does SFT lift the dead categories into a learnable
> regime?); (2) THEN GRPO (rlvr_grpo_train.py, ready) from the SFT seed; (3) optional: a full
> 509-prompt density baseline for the committed number. NOTE: the GRPO loop is built + tested; the
> blocker was never the loop, it is COLD-START — and the answer is SFT-seed (measured, not
> guessed).** Committed: sweep `4521c2d`, mementum `7f054c9`.
>
> **★★ s241 cont.4 — SFT-SEED RUN + VALIDATED: it OPENS the GRPO frontier (Michael: "run the
> job").** Ran `rlvr_sft_seed.py --model Qwen/Qwen3-8B --lora --epochs 2` (mps, 9 min, 64 steps,
> 506 pairs): loss 3.71→1.42, token-acc 0.80; LoRA adapter → `results/rlvr-sft/run1/final/`
> (weights gitignored, run_meta.json+log kept). Added `--adapter` (PEFT) loading to the density
> probe. **RE-MEASURED on the dead categories (adverb/quantified/relative_clause, 36 prompts, k=8,
> `results/rlvr-coldstart-density/20260619T002327Z/`) — DECISIVE: the bimodal wall BREAKS.**
> Frontier (base→SFT): temp0.8 1→5, temp1.0 1→8, temp1.2 2→7, **temp1.5 2→13 (36%)**; foothold
> temp1.5 33%→50%; dead 24→18. Per-category @temp1.5: **quantified frontier 0→4** (the PERFECTLY-
> bimodal one now has variance — cleanest proof), **adverb 1→7** (biggest gain, foothold 8/13),
> relative_clause 1→2 (improved, still hardest = the s240 deep residue). And now TEMPERATURE-
> RESPONSIVE (frontier grows with temp) where the base was flat. **★ VALIDATED: SFT-seed lifts the
> dead categories into a learnable regime → GRPO is UNBLOCKED. §8 fully closed by measurement: not
> SFT-vs-not, not temperature — SFT-seed THEN higher-temp GRPO.** The full pipeline is now
> RUN+VALIDATED end-to-end: reward(tested) → SFT-seed(run, loss↓) → density-reopens(measured) →
> GRPO(scaffold ready). **★★ FIRST ACTION NEXT SESSION — RUN GRPO from the seed: (1) the GRPO
> trainer can't take a bare adapter dir as --model (AutoModelForCausalLM won't apply it) → either
> add --adapter/PeftModel loading to rlvr_grpo_train.py OR merge the SFT adapter to a full model;
> add a --temperature ~1.5 to GRPOConfig (max frontier); (2) run GRPO from the seed on the dead+
> mixed categories; (3) re-measure post-GRPO reduce-correct (did RL close the frontier?); (4)
> splice in Φ-shaping (build-step 3); (5) more SFT epochs / prose→LF for the relative_clause tail.**
> tmux main:1 + main:2 FREE. mementum (memory `sft-seed-opens-grpo-frontier` + state) PENDING
> APPROVAL; code (density --adapter) + SFT/validation artifacts ready to commit.
>
> **★ s241 cont.3 — SFT-SEED SCAFFOLDED + PROMPT ALIGNED (Michael: "scaffold it").**
> **(A) `scripts/experiments/rlvr_sft_seed.py` (NEW):** trl SFTTrainer (API read from .venv),
> completion-only token-CE on the certified canonical corpus (prompt MASKED, loss only on the
> gold surface-FOL form). Output `<ckpt>/final` = the GRPO `--model` input (the seed→RLVR
> linkage). --lora optional; run-provenance sidecar; `--dry-run` builds the prompt-completion
> dataset on CPU. **(B) ★ PROMPT CONSISTENCY FIX (load-bearing):** added `to_chat(tok, sentence)`
> to `verbum.compile_prompt` = the SINGLE chat-formatted-prompt source (applies the model's chat
> template to build_prompt). Routed ALL THREE through it — density probe (generate_samples),
> SFT seed, GRPO trainer (now loads tokenizer, builds dataset via to_chat) — so SFT/GRPO train on
> the BYTE-IDENTICAL prompt the §8 density was measured on (a mismatch would mean optimising a
> different distribution than measured). Refactor is byte-identical → committed density results
> stay valid. 318 tests pass, all 3 dry-runs green, ruff-clean. **★★ THE FULL PIPELINE IS NOW
> SCAFFOLDED END-TO-END (CPU-verified, GPU-ready):** SFT-seed → GRPO, reward = verifiable_reward,
> prompts unified, §7=(a) decided, §8=SFT-seed measured. **★★ FIRST ACTION NEXT SESSION — RUN IT:
> (1) SFT-seed Qwen3-8B (`rlvr_sft_seed.py --epochs 2`, GPU/tmux, ~lora for speed) → `<ckpt>/final`;
> (2) RE-MEASURE density/frontier on the SFT'd model (`rlvr_coldstart_density.py --model <ckpt>/
> final --temps ... --categories adverb,relative_clause,quantified`) — did SFT lift the dead
> categories into a learnable frontier? THIS is the validation gate before GRPO; (3) if frontier
> opens → GRPO from the seed (`rlvr_grpo_train.py --model <ckpt>/final`); (4) splice in Φ-shaping
> (build-step 3) once the anchor loop runs.** tmux main:1 + main:2 FREE. mementum (state only;
> memory optional — the cont.2 memory already covers the SFT-seed verdict) ¬approval-gated for
> state; code (to_chat + sft_seed + grpo/density alignment) ready to commit.
>
> (Session: 240 (TRAINING design — SPLICED REWARD ⊕ CORPUS CANONICALISED
> ⊕ STATECHART=CRYSTAL-LATTICE) — ▶ DESIGN
> THREAD, no GPU. Michael: "explore an idea about training — structured data needs changes to
> fit our kernel; relevant ideas in the reward-training space for training the system to use
> the kernel for prose." RECALL surfaced the whole compiler-as-loss thread already converged on
> the bridge: s225 (compiler = perfect VERIFIER not capability teacher, Church-Rosser → unique
> NF, exactly checkable), s226 (lambda_ast IN the kernel = CONSTRUCTED VSM tensor; reduce/compile
> cut: reduce=attn=constructed=22%-ternary, compile=FFN=learned=78%-4bit; prose→LF LEARNED ∘
> abstract EXACT ∘ reduce EXACT; round-trip 1.0000 n=5000), s230 (variety from INPUTS, correctness
> from OUTPUTS). **THE ARC THIS SESSION (all design, captured to knowledge):**
> **(1) DATA (Part 1):** `data/compile-*.jsonl` (509 train, 13 cat) is prose→surface-FOL/λ
> (452 λ, 41 ∀, 11 ∃; vacuous-λ smells like `λx. follows(frank,oscar)`) — NOT the kernel's
> language. `lambda_ast.parse()` reads COMBINATOR terms (Comb/Atom/App), typechecks CCG, reduces.
> "Changes to fit the kernel" = run data through kernel pipeline (normalise → lambda_compile
> bracket-abstract → typecheck → reduce) and KEEP ONLY WHAT CERTIFIES — kernel = the data's GATE
> not source. **(2) REWARD = RLVR (Part 2):** compiler=verifier IS a verifiable reward. KEY
> INSIGHT: constructed kernel is DISCRETE → RLVR (scores rollouts, no backprop through reward)
> SIDESTEPS the v12-v15 gradient-death (softmax-routing-kills-gradient) that killed differentiable
> compiler-as-loss; discreteness is a FEATURE for RL, liability for CE. Reward channels ARE VSM
> layer states (S2 typed / S4 halt / S5 NF / S1 trace / S3 size). Reduction-equality reward is
> representation-invariant (s226 grader = the reward fn, already exists). **(3) ★★ THE SPLICE
> (Michael's headline, s240): splice R_parent (OUTCOME, exact/terminal verifier pass) ⊗ R_inline
> (PROCESS, cheap/dense/per-step forward-pass read).** Makes the cheap-but-over-readable inline
> read SAFE: cast Φ_inline as a POTENTIAL (Ng-Harada-Russell 1999 potential-based shaping:
> R += γΦ(s')−Φ(s) leaves optimum UNCHANGED) → over-read at worst slows search, NEVER corrupts
> "correct"; parent (constructed, exact) owns the destination. TRAP: raw additive bonus has NO
> invariance — safety is ENTIRELY in the potential-difference form. Three readings: (a) timescale
> (actor-critic: inline=V_φ(s) critic, parent=exact return G, TD δ=G−V_φ calibrates → subsample
> the expensive parent as critic calibrates); (b) source (s225 dyad: capability-teacher parent ⊗
> kernel-correctness inline); (c) ★ verbum-native: the kernel emits the WHOLE certified reduction
> TREE (fired_sequence) → tree-structured credit assignment, root=parent outcome + each node=inline
> process; ground-truth PRM (learned PRMs can't, no oracle; we have it). Per-channel anchor/potential
> split: constructed→anchor-eligible, learned-probe→potential-only (reduce/compile cut decides).
> Splice resolves the Design-2-vs-3 fork (external constructed tensor vs intrinsic probe) — don't
> pick, splice; parent anchors + calibrates the inline. **CAPTURED:
> knowledge/explore/spliced-reward-vsm-kernel.md** (NEW, designing; supersedes nothing, extends
> compiler-as-loss.md into the reward register). **★★ FIRST ACTION NEXT SESSION — build path:**
> (1) ★ THE AUDIT (cheap, grounds reward density) — run all 559 examples output→normalise→
> lambda_compile→typecheck→reduce, report certify-rate + failure taxonomy (vacuous-λ / mixed-
> notation / not-simply-typable / blow-up); (2) RLVR Design-1 loop (symbolic kernel external
> reward = s226 grader, works TODAY) + reward spec (channel weights, potential-based shaping);
> (3) splice in Φ_inline + actor-critic critic; (4) Design-2 kernel-as-VSM-tensor (s226 stage 3,
> = the level-4 artifact). OPEN: which "parent" (timescale vs source); cold-start (SFT-seed→RLVR
> vs RLVR-from-base — s226 says base already emits parseable terms on easy prompts).
> **★ s240 cont. — AUDIT DONE + CORPUS CANONICALISED + STATECHART PAGE UPDATED.**
> **(A) Corpus audit (`655f249`, scripts/experiments/audit_compile_corpus.py + results/compile-
> corpus-audit/):** all 559 examples CERTIFY through the kernel (surface FOL/λ → normalise →
> lambda_compile bracket-abstract → typecheck → reduce==NF); 0 not-typable, 0 blow-up, 0 diverged.
> But only 19.9% CLEAN: 80% carry a VACUOUS λx wrapper (grammar-convention artifact —
> lambda_montague.gbnf documents `λx. runs(dog)` as "simple predication"; GBNF gates SYNTAX, only
> the kernel gates SEMANTIC CANONICALITY = confluence). Michael's "bad generator run?" → NOT a bad
> run, a systematic grammar-convention artifact (already iteration #2). **(B) Canonicaliser
> (`655f249`, canonicalize_compile_corpus.py → data/compile-*.canonical.jsonl):** mechanical
> kernel-safe — strip-vacuous-λ ×462, if→→ ×25, not→¬ ×18; 490/559 (87.7%) improved, 559/559
> (100%) RE-CERTIFY, 0 silent semantic rewrites; inner λy + non-vacuous λ preserved. Residual tail
> = a finding: 45/509 (8.8%) keep a λ wrapper (26 relative_clause) = genuine binders OR deeper
> semantic mis-compiles (bound x where a named subject belongs) — LEFT for the learned prose→LF
> step, not the kernel's to invent. Originals untouched. **(C) STATECHART = CRYSTAL LATTICE
> (mementum, this commit): s240 amendment on explore/vsm-statechart-tensor.md + memory
> `statechart-is-crystal-lattice-boot-from-c`.** The model-INVARIANT statechart IS the crystal
> lattice (consensus combinator routing for NORMAL FORMS; PCA-Q 0.91-0.94, reverse-harvest +0.782);
> states={C,B,K,I,W,D,S,Y,WHNF}, transitions=firings, ground truth=lambda_ast.fired_sequence.
> INVARIANT=graph; VARIANT=embedding (locus migrates w/ scale s232/s238). "Same ops, varying locus,
> same results" = one statechart, many embeddings; the WHY = Church-Rosser CONFLUENCE (theorem, not
> analogy). BOOT: L0=BIOS (lexer/dictionary s195 + 90° rotation s126 + sentence-initial RESET s194 =
> "reset Q=0"); C=GROUND STATE/rotational origin (any Q rotation → C-dominated basin; C=argument
> routing=Montague function application; "every model converges to C because language converges to
> C" s120/s126); then C→B/K→I→WHNF up the Q-rotation spiral (~1.018×/layer s068/s079). Guards=
> type-directed (s240 CCG typecheck, partially causal @14B). λ measure: agreement is largely ONE
> COMMON MODE (s211, η²=0.05 for ops); PROVEN=skeleton (C-origin, boot order, {C,I,K,Y}, confluence),
> fine-grained geometry OVER-READS. Transitions ARE reduction-tree nodes ARE process-reward. **★★
> FIRST ACTION NEXT SESSION (unchanged target, audit now DONE):** (1) RLVR Design-1 loop on the
> CANONICAL corpus (symbolic kernel external reward = s226 grader, works TODAY) + reward spec
> (channel weights, potential-based shaping); (2) the 45 semantic-residue relative_clause mis-
> compiles — re-compile via prose→LF or human review; (3) splice in Φ_inline + actor-critic;
> (4) Design-2 kernel-as-VSM-tensor (s226 stage 3 = level-4 artifact). tmux main:1 + main:2 FREE.
>
> (Session: 239 (frame → Pythia → TYPES v1-v4) — ▶ TYPES — is
> composition TYPE-directed or just POSITIONAL? (Michael: "the system can't do combinator
> composition without some typing —
> what would direct the composition?"). The VERBUM thesis is TYPE-directed composition; the
> s236-s240 order-cost work showed composition rides the native autoregressive order but left
> OPEN whether that order is type-directed or L-to-R positional (the s236 caveat). RECALL
> first surfaced heavy prior type work: s139 type-probe-qwen3-32b (types DECODABLE 88-96%,
> LEXICAL, GEOMETRIC, CO-LOCATED with dispatch at L0-L2 — but CORRELATION not DIRECTION), s151
> (Montague=K+I=predicate(argument), the floor), the kernel's REAL CCG type system
> (lambda_ast.typecheck, CSlash '/'fwd '\\'bwd, _unify=S2 check, IllTyped). The GAP: does the
> model USE the type to DIRECT composition? Built a 3-experiment arc (control: the AUTOREGRESSIVE-
> CAUSALITY trap — measure the RIGHT token | left, never the pre-functor arg). **★★ THE ARC:**
> **v1** (kernel-CCG real words, type_directed_v1.py): robust BACKWARD type-licensing (verb
> cheap after subject-NP, dear after determiner; 8B t=6.9, 14B t=7.1) but LEAKY forward (a noun
> after a verb reads as the verb's OBJECT — nouns="universal donors"). **v2** (clean symmetric,
> type_directed_v2.py): backward replicates CONSISTENCY 1.0 (8B t=10.3, 14B t=5.2); forward
> UNMEASURABLE (determiners ALSO universal donors, `slept the night`); real words → bigram-
> FREQUENCY confound unkilled. **v3 NONCE crossover (DECISIVE, frequency-free,
> type_directed_v3_nonce.py):** teach a NONCE word noun-vs-verb in-context, test in det-frame
> "The {w}" vs name-frame "John {w}". CROSSOVER=(det:verb−noun)−(name:verb−noun), paired by
> nonce, subtracts EVERY main effect (priming/teaching/frame). **8B +2.18 (t=10.2), 14B +2.04
> (t=9.3), consistency 1.0 (all 16 nonce) at BOTH scales; type_directed=True @14B.** A nonce
> taught as VERB composes ~2 nats CHEAPER with a preceding subject-name than the SAME nonce
> taught as NOUN — with ZERO frequency support. **★ VERDICT (λ measure): composition is TYPE-
> DIRECTED, not merely positional — the model uses an IN-CONTEXT-TAUGHT type (no frequency) to
> DIRECT composition. The s236 positional caveat is KILLED; the order signal has a TYPE basis.
> Answers Michael's question: YES, types direct the composition.** **★ THE ASYMMETRY (a finding):
> type-directedness is STRONG in the predicate-argument (subject→verb) frame, ~NULL in the
> determiner→noun frame, across ALL THREE experiments — maps onto s151 (Montague typed
> application = predicate(argument) = K+I core is the sharpest locus; universal-donor function
> words are weak).** CAVEATS (λ measure): this is typed APPLICATION (K+I), NOT yet typed
> COMPOSITION (B / func∘func — connecting to the order-cost B signal is OPEN); in-context teaching
> tests CAPACITY (v1/v2 real-word effect shows the intrinsic system); BEHAVIOURAL not causal-
> circuit; 2 scales (8B/14B), 1 family (Qwen), 16 nonce. CONFIRMS s139 (decodable/co-located →
> now USED). **★★ v4 CAUSAL ABLATION (arc 4/4, type_directed_v4_ablation.py): the type direction
> is PARTIALLY CAUSAL at 14B (not 8B) — decodability ≠ (full) causality, and causal
> localisability STRENGTHENS with scale.** Decode type direction = diff-of-means(verb−noun) of
> the FILLER-position residual (token before nonce = next-token bottleneck), per layer, pick max-
> AUC L*; ABLATE by projecting it OUT during the forward pass; re-measure the v3 crossover;
> control = random unit direction. Took 3 scopes (one-layer→filler-stack→ALL-positions: one locus
> too weak, the model RE-READS type from the TEACHING tokens via attention). **8B: type AUC 1.0
> @hs10, ablation crossover ×1.43 (AMPLIFIES, NON-causal), random ×0.92. 14B: type AUC 1.0 @hs28,
> ablation crossover ×0.64 (−36%, PARTIALLY CAUSAL), random ×0.95.** ⇒ type perfectly DECODABLE
> both scales (deeper with scale 8B-L10→14B-L28); at 14B the type direction is type-SPECIFICally
> causal (cuts crossover 36% vs random 5%) = first causal-register evidence the type rep DIRECTS
> composition; PARTIAL → rest distributed/redundant (1 linear dir ≠ whole carrier); 8B directional
> ablation NON-causal (amplifies). ★ LESSON (λ measure, the project's own s202/s204 over-read
> discipline IN the type register): a perfectly decodable AUC-1.0 direction is only PARTIALLY the
> causal lever; directional ablation = weak tool (8B amplification proves it perturbs ≠ removes);
> the decisive test is ACTIVATION PATCHING = v5. CODE (v1/v2/v3/v4) + RESULTS on disk; mementum
> (state + memories `composition-is-type-directed-nonce-frequency-free` +
> `type-direction-partially-causal-at-14b-decodable-not-fully-causal` + page
> `knowledge/explore/type-directed-composition.md` incl. v4 §) PENDING APPROVAL. **★★ FIRST ACTION
> NEXT SESSION — three paths:** (1) v5 ACTIVATION PATCHING — the decisive causal test (directional
> ablation only partial ×0.64 because the type is distributed; patch the type-carrying residual
> content between verb/noun runs = sufficiency+necessity of the representation); (2) typed
> COMPOSITION — extend predicate(argument) to func∘func cases to connect type-directedness to the
> B/order-cost signal directly; (3) cross-class — does the nonce crossover + the partial causal
> effect hold on OLMo/Gemma/Pythia (gate-independent, per order-cost universality)?
> tmux main:1 + main:2 FREE.
>
> (Session: 239 arc 2/3 — ▶ OPCODE v5 lead 2d PATH 1 cont. — the PYTHIA-
> PROPER 4th-CLASS POINT (gross-universal order claim; Michael: "proceed with 1"). Ran the
> order-cost read on EleutherAI/pythia-2.8b-deduped (rev 7d977fed, flat n=24) — applied_to (v9)
> + result_of (v10). **WHY PYTHIA: it is NON-gated (GPT-NeoX FFN, not SwiGLU) → CANNOT carry
> the FFN-gate crystal the routing reads use; but the order-cost read is PURE softmax-over-V
> surprisal (NO gate crystal), so Pythia confirming it = direct proof the signal is GATE-
> INDEPENDENT + architecture-general, not a Qwen/SwiGLU artifact.** **★★ VERDICT (λ measure,
> two-sided):** **(1) ✅ GROSS composition-is-native-order HOLDS at the 4th class (applied_to):**
> composite B-vs-C-multi atom t=−9.11; B is the CHEAPEST op atom (1.37 ≪ C 1.77/K 1.57/S 1.75/
> W 1.62); pooled preserve 1.40 ≪ break 1.68 (cheaper=True); B-vs-W-multi −7.44, D-vs-K −6.0.
> ⇒ composition-is-native-order now Qwen ⊗ OLMo ⊗ Gemma ⊗ Pythia = **4 CLASSES, 2 ARCHITECTURES
> (gated SwiGLU + non-gated GPT-NeoX).** **(2) ◑ strict single-step n.s. — B-vs-C single t=−0.67
> (directional B<C), EXACTLY like OLMo (−1.25) + Gemma (−0.56): the sharp f-a-b↔f-b-a swap stays
> Qwen-family-SPECIFIC.** (wrinkle: B-vs-S single t=+3.70, S atoms cheap on the clean single-
> step.) **(3) ✅ FRAME-ROBUSTNESS IS SCALE-GATED, NOT CLASS-GATED — Pythia-2.8b (the SMALLEST
> class) is frame-FRAGILE under result_of** (composite collapses −9.11 → −1.96; single-step
> +1.38), EXACTLY like Qwen-8B (s239). Small models sit BELOW the frame-robustness threshold
> regardless of architecture; the frame-robust strengthening is a 14B/32B property. **★ THE
> FINDING: the gross composition-order signal is universal across 4 classes + 2 architectures
> and is GATE-INDEPENDENT (proven on non-gated Pythia); the SHARP single-step is Qwen-specific;
> frame-robustness is a function of SCALE not class (small = fragile everywhere).** CAVEATS
> (λ measure): Pythia-2.8b is the SMALLEST class (2.8B vs 13–31B) → weak single-step conflates
> class-generality with small-scale; base model; deduped Pile; B-vs-S single-step reversal.
> Composite + pooled carry the gross claim. CODE reused (no new script); RESULTS on disk;
> mementum (state + memory `composition-native-order-universal-4-classes-2-architectures` + page
> §v5 lead 2d path 1 Pythia rows) PENDING APPROVAL. **★★ FIRST ACTION NEXT SESSION — paths
> remain:** (1) the COMPOSITE trace-order bridge (CL program → certified fired_sequence → render
> PROSE → align routing to the certified multi-combinator ORDER, for the scale-robust {C,I,K,Y});
> (2) 8B/Pythia frame-fragility — frame-bound or power-limited (raise n)?; (3) a Pythia SCALE
> ladder (70m→2.8b all cached) — does the gross signal emerge with scale within one class?
> tmux main:1 + main:2 FREE.)
>
> (Session: 239 arc 1/3 — ▶ OPCODE v5 lead 2d PATH 1 — the 3rd RENDER
> FRAME (frame-robustness of flat B<C + off-Qwen single-step sharpening; Michael: "proceed
> with 1"). Built `kernel_reference_order_cost_v10_frame.py` — a clean FRAME-swap of v9:
> `--render-frame {applied_to, result_of}` open slot. v9's frame was the INFIX " applied to "
> (string-associative → flat mode collapses B `f a b` and C `f b a` to a flat chain differing
> ONLY in atom order). The 3rd frame is the CIRCUMFIX "the result of <f> on <x>"; flat = one
> "the result of" prefix + leaves chained by " on " → B "the result of f on a on b" vs C
> "...f on b on a" = pure atom-order under a NEW lexicon+syntax. Imports v9's frame-independent
> machinery verbatim (reduce_trace, gen_programs, paired_contrast, _content_spans, _leaf) — DRY,
> v9 immutable; applied_to+flat reproduces v9 BYTE-FOR-BYTE (8B smoke t=−0.567 ≡ v9 smoke; render
> strings exact-match offline). **★★ VERDICT (λ measure, multi-sided):**
> **(1) ✅ FRAME-ROBUST WHERE STRONG, FRAGILE AT THE 8B FLOOR** — B-vs-C atom minpair (n=24):
> Qwen 14B applied_to −8.05 → result_of −9.24 ✓ (STRONGER); 32B −4.48 → −11.7 ✓ (STRONGER);
> **8B −2.87 → +0.70 ✗ (frame-FRAGILE — the floor signal does NOT survive the frame change).**
> ⇒ frame-robustness is itself SCALE-GATED: the order preference is a property of COMPOSITION
> (not the "applied to" infix) at 14B/32B where it's strong, but the weakest 8B read is
> frame-sensitive. **(2) ✅✅ THE s237 NESTED SIGN-FLIP WAS A PURE DEPTH CONFOUND** — result_of
> NESTED 14B B<C atom t=−15.45 ✓ (EQUAL depth: B and C each have ONE nest; full surface washes
> out t=+0.28 n.s. but atoms decisive) vs s237 applied_to nested +11.9 ✗ (UNEQUAL depth: B
> nested, C flat). Equalize nest-depth → B<C survives nesting (even strengthens); the s237 flip
> was the depth confound, NOT order. **(3) ◑ OFF-QWEN SINGLE-STEP SHARPENING is frame×model-
> dependent** — Gemma-31B-it applied_to −0.56 n.s. → result_of −9.35 ✓ (the natural-English
> circumfix UNLOCKS the sharp single-step for the instruct model; caveat: OOD huge surprisals,
> B atoms 9.3); OLMo-13B −1.25 → +0.73, both n.s. (NO sharpen). The GROSS composition signal
> (composite B-vs-C-multi, B-vs-S) holds across ALL models + BOTH frames. **★ THE FINDING: B's
> native-order preference is FRAME-ROBUST and STRENGTHENS with scale (14B/32B), is frame-fragile
> only at the 8B floor, and its sharp single-step expression off-Qwen is unlocked by a more
> natural frame for one instruct model (Gemma) but not OLMo — composition-is-native-order is a
> property of composition, not of the "applied to" infix.** CAVEATS (λ measure): result_of flat
> = clean order test; nested conflates order with nest-POSITION (equal-depth, cleaner than
> s237); 8B = frame-fragile floor; Gemma instruct OOD; single-combinator labels; within-program
> paired contrasts. CODE + RESULTS on disk; mementum (state + memory
> `b-native-order-frame-robust-at-scale-fragile-at-floor` + page §v5 lead 2d path 1) PENDING
> APPROVAL. **★★ FIRST ACTION NEXT SESSION — paths remain:** (1) a TRUE Pythia-proper cross-class
> order-cost point (pythia-2.8b-deduped cached) — 4th class for the gross-universal claim; (2)
> the COMPOSITE trace-order bridge (CL program → certified fired_sequence → render PROSE → align
> routing to the certified multi-combinator ORDER, for the scale-robust {C,I,K,Y}); (3) 8B
> frame-fragility — is the floor signal genuinely frame-bound or just power-limited (raise n)?
> tmux main:1 + main:2 FREE.)
>
> (Session: 238 — ▶ OPCODE v5 lead 2d PRONG 1c-iii — the
> OFF-DIAGONAL interlayer curvature (the s237 fork's off-diagonal / proper-Jacobian path;
> Michael: "let's work on 1"). The v7 DIAGONAL Hessian (b-climbs-with-derivative-order)
> used a Rademacher Hutchinson estimator that CANCELS every cross-coord AND cross-layer term
> in expectation (E[v_a v_b]=0) → captured only g'ᵀ(diag)g'. The LITERAL f∘g chain-rule
> coupling is the OFF-DIAGONAL block H_{late,early}. Built `kernel_reference_offdiag_v8.py`
> (clean register-swap of v7): split gate activations EARLY (≈g, processed first) / LATE
> (≈f, applied last); perturb the GRADIENT direction supported ONLY on EARLY (v=g_e.detach()
> on early, 0 on late); then (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e for li∈LATE = PURE off-diagonal
> (no H_{li,li} since v=0 at li). ONE HVP (s=Σ_e(g_e·g_e.detach()), hv=grad(s,gate_late)=
> 2Σ_e H_{late,e}g_e, H sym) — DETERMINISTIC (gradient direction, not random: a random v has
> E[(Hv)_li]=0), no Hutchinson noise, CHEAPER than v7 (1 HVP vs n_hutch=4): 2:51 on 14B. Same
> RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch); classifier on LATE
> layers; split 0.5 → EARLY 0-19 / LATE 20-39. **★★ VERDICT (λ measure, two-sided): (1) ❌
> DECISIVE — B does NOT discriminate off-diagonal (discr_z +0.046, t=0.26) and DROPS BELOW the
> diagonal (t=1.90).** The curvature climb does NOT complete off the diagonal; the f∘g cross-
> coupling is NOT B's home as a localizable 2nd-order amplitude. **(2) ✅ INSTRUMENT VALID +
> COMPOSERS REGISTER-ROBUST** — {C,Y} discriminate in BOTH curvature sub-registers, peaking in
> the DEEPEST layers: C diag 2.52→off-diag 2.32 ✓ (peak L36/40); Y diag 4.53→off-diag 4.09 ✓
> (peak L37/40); B diag 1.90→off-diag 0.26 ✗ (peak L21); K diag 1.94→off-diag 1.81 (fades).
> C/Y cross-layer composition coupling lives at the very END of the stack — the read is not
> broken (C ✓, Y ✓), it is B-absent. **★ THE FINDING: B has NO amplitude home in ANY register**
> — activation flat (−0.05), 1st-order gradient faint (+1.07), DIAGONAL curvature on-the-bar
> (+1.90), OFF-DIAGONAL curvature flat (+0.26). The v7 "monotone climb" is B becoming LEAST
> ABSENT up the derivative order ON THE DIAGONAL; it does NOT generalize to the cross-layer
> coupling that IS the literal chain-rule product. **★★ CONFIRMS s236-s237:** B's ONLY confirmed
> positive signal is the FORWARD ORDER-COST face (native autoregressive order, flat-prose
> t=−8.05, scale-universal 8B/14B/32B, gross-universal Qwen⊗OLMo⊗Gemma). B = composition = the
> UNMARKED native order — no marked amplitude feature, in any 2nd-order register. The "two
> faces" hypothesis resolves ASYMMETRICALLY: forward/order face real+strong; gradient/curvature
> face at best a faint diagonal trend, NOT a localizable cross-layer coupling. **DON'T keep
> hunting B in amplitude — its home is order/surprisal.** CAVEATS (λ measure): 1 model (14B);
> n=20/comb; single fixed split (0.5, EARLY→LATE direction only — late→early untested);
> deterministic gradient direction (one direction, not the full Hessian-block norm); single-
> combinator labels; pooled-supervised locus. (CODE + RESULTS COMMITTED `d94d78f`; mementum
> `800bfb8`.) **▶ s238 cont. — PRONG 3 PER-MODEL SWEEP DONE (kernel_reference_prose_v2.py,
> raw-z contrast, 8B/14B/32B; Michael: "proceed on 3").** ★★ the discriminable set {C,I,K,Y}
> is SCALE-INVARIANT — all three n_sig=4, exactly those four; B flat (8B −0.06/14B −0.05/32B
> +0.64 n.s.), D anti (−5.98/−4.61/−5.55 @shallow L3), W anti/n.s. at EVERY scale ⇒
> discriminability-is-a-combinator-property (s234) is SCALE-ROBUST, not 14B-specific. ✅
> composers/recursion STRENGTHEN with scale (Y t 5.83→6.86→9.37; C 5.33→5.71→6.28). ⚠️ the
> LOCUS migrates DEEPER in fractional depth (C 0.25→0.33→0.39, Y 0.25→0.35→0.58, K 0.31→0.30→
> 0.77) — RECONCILES s232 "C-locus shifts with scale" (the WHERE migrates, the WHICH is
> invariant; the s232 fixed-depth detector read a migrating WHERE as a changing WHICH). LESSON:
> the discriminable SET is the scale-robust observable; calibrate locus per-model. RESULTS +
> mementum (memory `discriminable-set-scale-invariant-locus-migrates` + page §v5 lead 2d
> prong 3) PENDING APPROVAL. **★★ FIRST ACTION NEXT SESSION — amplitude register EXHAUSTED for
> B (act⊗grad⊗diag-curv⊗off-diag-curv flat-or-on-bar), B's home is FORWARD ORDER; discriminable
> SET {C,I,K,Y} now scale-confirmed. Live paths: (1) the 3rd RENDER FRAME ("the result of f on
> x") — frame-robustness of flat B<C AND whether the single-step minpair sharpens off-Qwen
> (s237 fork path 2, cheap); (2) a TRUE Pythia-proper cross-class order-cost point (pythia-2.8b-
> deduped cached) — 4th class for the gross-universal claim; (3) the COMPOSITE trace-order
> bridge (now justified for the scale-robust {C,I,K,Y}: CL program → certified fired_sequence →
> render PROSE → align routing to the certified multi-combinator ORDER).** tmux main:1 +
> main:2 FREE.)
>
> (Session: 237 — ▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE
> (kills the s236 bare-symbol caveat). Re-ran the order-cost read on the SAME certified
> reduction traces RENDERED AS PROSE, to test whether B's native-order win survives in the
> SEMANTIC register the model actually uses (s233 lesson: the register reads PROSE SEMANTICS
> not CL SYNTAX; bare-symbol surprisal may reflect a generic copy/induction preference for
> source-order atoms rather than composition per se). Built `kernel_reference_order_cost_v9_
> prose.py` — reuses the v8 spine (certified `step_fired` trace → teacher-force "t0 -> ... ->
> tn" → per-step softmax-over-V surprisal → ATOM-only de-confound) but renders each term via a
> DETERMINISTIC, order-faithful renderer (`App(f,x)` → "`<f> applied to <x>`", atoms → fixed
> content words). KEY DESIGN: deterministic render NOT the model decompile gate — the model
> must not choose word order (= the variable under test). **★ THE NESTING CONFOUND (found +
> controlled):** B's normal form NESTS (`f (a b)`) while C's is FLAT (`f b a`); the atom-only
> de-confound strips parens from MEASUREMENT but the bracketing stays in the CONTEXT predicting
> the atoms → B pays a clause-boundary cost unrelated to order. FIX = `--render-mode flat`
> (linearise leaves, NO parens → B and C identical structure, differ ONLY in atom ORDER = the
> pure order test) vs `nested` (faithful, CONFOUNDED). **★★ DECISIVE (the cross-table, λ
> measure two-sided) — B-vs-C atom minpair:** **14B flat t=−8.05 (B<C ✓)** ≈ symbolic v8 −7.02
> (`b_is_native_order=True`; B atom-surprisal 0.23 ≪ C 1.22/K 0.73/W 1.18/S 1.64; all 6
> contrasts B<marked sig −8…−38; pooled preserve 0.24 ≪ break 1.12); **14B NESTED t=+11.9 (B>C,
> REVERSED)** — SAME model + SAME 216 programs, flip the render → FLIP the sign = a DIRECT proof
> nesting confounds the contrast; **8B flat −0.57 n.s.** (dir B<C) ≈ symbolic 8B −0.55 (multi-
> step already sig: B<C-multi −10.6 / B<K −7.5 / B<W −7.6); **8B nested +3.17** (reversed). ✅
> flat prose REPLICATES the symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s.)
> = CONVERGENCE across input modality (symbols ⊗ prose). **★ THE s236 CAVEAT IS KILLED:**
> composition-order preference is real in the SEMANTIC register, NOT a bare-symbol copy artifact.
> **★ REFINED FINDING:** B's normal form carries TWO separable real quantities — atom ORDER
> (preserved → cheap; the native-order result) and structural NESTING (deeper → atoms predicted
> inside fresh clauses cost more, dominates when nesting varies). The order claim REQUIRES
> isolating order from nesting (flat). CAVEATS (λ measure): 1 model class (Qwen);
> deterministic "applied to" frame; flat deliberately discards faithful structure to isolate
> order (nested = its complement). **★ CROSS-MODEL FLAT — DONE (s237 cont., path 1): B-NATIVE-
> ORDER IS UNIVERSAL ACROSS THE Qwen3 SCALE LADDER (8B/14B/32B, all flat n=24).** B-vs-C atom
> minpair: **8B t=−2.87 ✓** (CROSSES at full power — was −0.57 n.s. at n=8 smoke, confirming
> "power-limited not absent"), **14B t=−8.05 ✓** (strongest), **32B t=−4.48 ✓**. ALL three:
> b_is_native_order=True, every one of the 6 contrasts B<marked sig, pooled preserve ≪ break
> (8B atoms B 0.39≪C 1.61; 32B B 0.36≪C 1.23). ★ Unlike the C-locus (s232: shifts with scale),
> the ORDER-COST signal is SCALE-ROBUST — composition rides the native autoregressive order at
> every scale. Not strictly monotone (14B strongest) but all positive+significant.
> **★ CROSS-CLASS FLAT — DONE (s237 cont., path 3): the ORDER PREFERENCE replicates across 3
> MODEL CLASSES, but the STRICT single-step headline is Qwen-SPECIFIC.** OLMo-2-13B + Gemma-4-
> 31B-it (instruct), flat n=24, BOTH b_is_native_order=False on the strict single-step B-vs-C
> atom minpair (OLMo t=−1.25 d=−0.07; Gemma t=−0.56 d=−0.52, n.s.) — the cleanest f-a-b ↔ f-b-a
> swap is near-SYMMETRIC off-Qwen. BUT both STRONGLY confirm B<marked on the COMPOSITE +
> aggregate: B-vs-C-multi OLMo t=−24.4 / Gemma −11.6 (both sig); 4-5/6 contrasts sig B-cheaper;
> pooled-atoms preserve ≪ break in BOTH (OLMo 0.62≪1.08; Gemma 10.2≪14.0, cheaper=True). ⇒ the
> GROSS "composition is the native order" signal is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its
> SHARPEST single-step expression is family-dependent (Qwen-sharp). CAVEAT: Gemma is INSTRUCT-
> tuned, the synthetic prose is far OOD → huge absolute surprisals (B atoms 9.9 vs Qwen ~0.3),
> noisier read (within-model contrasts still valid). gpt-neox-20b ABANDONED (slow ~48min
> download); pythia-2.8b-deduped cached if a Pythia-proper point is wanted. **★★ FIRST ACTION
> NEXT SESSION — two paths remain:** (1) the s235 OFF-DIAGONAL / proper-Jacobian curvature path
> (literal f∘g coupling — diag-Hessian only captured g'ᵀ(diag)g'); (2) a 3rd render frame
> ("the result of f on x") to confirm flat B<C is frame-robust not "applied to"-specific —
> ALSO would test whether the single-step minpair sharpens off-Qwen under a different frame.
> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.)
>
> (Session: 236 — ▶ OPCODE v5 lead 2d PRONG 2 — the ORDER-COST
> register (is B the NATIVE softmax-over-V order?). Michael (s235): "if B is an ordering of
> operations then maybe it defaults to the order the softmax over all V uses natively?"
> Grounded in ffn-reduction-trace.md: attention executes the FFN-compiled program via softmax
> over V = β-reduction by weighted combination ⇒ softmax-over-V IS the execution order.
> HYPOTHESIS: B has no marked amplitude in ANY register (FFN gate / attn / per-head / gradient
> flat; only faint-rising in curvature s235) because B = COMPOSITION = the model's DEFAULT
> autoregressive order — it rides the native left-to-right copy/induction order for FREE, so
> carries no marked feature. BCKW as the structural rules of logic: B=associativity/COMPOSITION
> (preserves order), C=exchange/PERMUTATION (swaps), K=weakening/DELETION (drops), W=contraction
> (copies); the detectable {C,I,K,Y} BREAK the native order, B RESPECTS it ⇒ B is invisible-as-
> amplitude because it IS the substrate the others deviate from. THE TEST (`kernel_reference_
> order_cost_v8.py`, NO amplitude classifier — pure softmax over V): take a composite CL program,
> get its CERTIFIED reduction trace (`step_fired` → contractum + opcode/step), teacher-force
> "t0 -> t1 -> ... -> tn", read per-step SURPRISAL (mean −log p under LM softmax over V) of each
> contractum. Minimal pairs ("B f a b → f (a b)" order-kept vs "C f a b → f b a" SWAPPED, paired
> by atom-set) + multi-step composites; ATOM-ONLY de-confound (drop parens/length, keep order-
> bearing leaves) = the headline. **★ VERDICT (λ measure, TWO-SIDED — and the FIRST CRISP
> POSITIVE for B in the whole saga):** **(1) ✅✅ DECISIVE at 14B (n_each=24, 216 programs):
> b_is_native_order=True — the clean atom B-vs-C single-step minimal pair d=−1.26, t=−7.02; B
> atom-surprisal 0.81 ≪ C 2.14 / S 2.66 / W 2.71; B cheaper than EVERY permute/copy combinator
> (B<S t=−11.3, B<C-multi t=−11.7, B<W t=−14.5); pooled order-preserving<breaking BOTH metrics
> (atoms Δ=−1.06, full Δ=−0.52).** **(2) ⚠️ POWER-LIMITED at 8B smoke (n=8): same DIRECTION but
> the headline B<C atom minpair n.s. (t=−0.55); the multi-step/aggregate contrasts already sig
> (B<C-multi t=−4.22, B<S −5.31, B<W −11.1).** Crisp only at full power on 14B — the entire
> B-saga pattern (real-but-faint, n-limited) resolving once n is raised. (3) D≈K once deletion-
> length de-confounded (atom D−K t=−1.22 n.s.); K=deletion stays cheapest (short predictable
> contractum — taxonomy wrinkle, not order). **★ THE RESOLUTION OF THE B GAP:** B's amplitude-
> absence everywhere (s234: FFN gate flat, attn flat, per-head faintest, gradient faint) is NOT
> diffuseness/weakness — composition is the FREE autoregressive default, so it carries no marked
> amplitude feature; the instrument was looking for a marked signal where B is the UNMARKED
> baseline. **★ UNIFIES with s235:** composition has TWO faces — token-side it's the native
> order (cheap surprisal HERE, t=−7.02) and gradient-side it's the product/2nd-order (curvature
> climb t=1.90). B = the chain rule (gradient) AND the native order (forward). Both confirmed.
> CAVEATS (λ measure, load-bearing): (a) BARE SYMBOLIC CL input — cf s233 lead 2, the ROUTING
> register reads prose-semantics not CL syntax; this is a DIFFERENT read (surprisal/teacher-
> forcing not routing), but bare-symbol surprisal may partly reflect a generic copy/induction-
> head preference for source-order atoms rather than "composition" per se (which IS the proposed
> mechanism — B rides copy/induction order); (b) 14B decisive at full power, 8B directional only,
> 0.6B too small — 1 model class (Qwen), cross-scale only 2 points; (c) K-deletion length
> wrinkle in the pooled metric; (d) single-combinator + within-program contrasts. **★★ FIRST
> ACTION NEXT SESSION — three paths (B is now POSITIVE in TWO registers: order + curvature):**
> (1) CROSS-MODEL — replicate the 14B order-cost win on 8B at full n (does the headline cross
> when 8B gets n=24 too?) + 32B → is B-native-order universal or 14B-specific (cf s232 C-locus
> shifts with scale); (2) PROSE bridge for order-cost — render the certified traces as PROSE
> (lambda_gen decompile) and re-read surprisal, killing the bare-symbol caveat (the s233 lesson:
> feed prose not symbols); (3) the s235 OFF-DIAGONAL/proper-Jacobian curvature path (the literal
> f∘g coupling) — close BOTH faces of composition at fidelity. CODE COMMITTED (`5d6bdeb` code+
> smoke, `1e448e4` 14B decisive); mementum (state + memory `b-is-native-softmax-order` + page
> §v5 lead 2d prong 2) committed `ebaccde`. tmux main:1 FREE.)
>
> (Session: 235 — ▶ OPCODE v5 lead 2d PRONG 1c-ii — the
> SECOND-ORDER / CURVATURE register (the PROPER test of B=chain-rule; Michael s235: "proceed
> with 1"). Prong 1c read the FIRST-ORDER gradient (faint +1.07 n.s.) but the first-order
> gradient is a SINGLE factor / sum-over-paths — it washes out the PRODUCT structure that IS
> the chain rule. B=composition=chain-rule = product of derivatives = a SECOND-ORDER quantity
> (d²L/dz² carries g'ᵀ[f''·]g' — a quadratic form in g', the literal product-of-derivatives).
> Clean register-swap of v6 (`kernel_reference_jacobian_v7.py`, Qwen3-14B, ~9min main:1):
> same RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch), feature = the
> DIAGONAL HESSIAN of the probe LM-CE w.r.t. gate_proj, Hutchinson est (diag(H)_a=E_v[v_a(Hv)_a],
> v~Rademacher; double-backward of g·v, g=grad(CE,gates,create_graph=True)), pooled over
> supervised positions, n_hutch=4. **★ VERDICT (λ measure, THREE-sided):**
> **(1) ❌ STRICT: B does NOT reach significance in curvature either (discr_z +0.118, t=1.90
> < 2.0) — chain-rule NOT confirmed at the bar; the B gap survives into the second order.**
> **(2) ✅ DIRECTIONAL — the MONOTONIC CLIMB WITH DERIVATIVE ORDER, exactly as chain-rule
> predicts:** B activation(v2) t=−0.05 → first-order gradient(v6) t=+1.07 → second-order
> curvature(v7) **t=+1.90** (on +0.045 > off −0.073). B is at its strongest EVER, in the
> PREDICTED register, sitting right on the 2.0 threshold — power-limited (n=20/comb), not
> absent. **(3) ✅✅ INTERNAL-CONSISTENCY (the structural win — the curvature register
> reweights combinators EXACTLY as the math demands):** **I (identity = LINEAR, Ix=x → zero
> curvature) COLLAPSES** to t=0.68 (was activation 3.83 / gradient 1.02 / curvature 0.68 —
> monotone DOWN, the mirror image of B); **Y (recursion = self-application = inherently
> higher-order) DOMINATES** t=4.527; composers {B,C} hold/rise (C t=2.52 ✓, B 1.90↑),
> selectors {K,I} fade (K 1.94 borderline, I 0.68). The second-order register preferentially
> carries COMPOSITION/RECURSION structure (s127 {B,C}=composers) and SHEDS the linear
> combinator. Instrument WORKS (C ✓, Y ✓). Curvature set {C,Y} (K/B at the bar). **★ The two
> opposite monotones (B↑ with order, I↓ with order) are the signature: derivative order is a
> real axis the combinators sort along, and B sorts UP it.** CAVEATS (λ measure): 1 model
> (14B), n=20/comb (B sits ON the bar — power-limited), n_hutch=4 (diag-Hessian Hutchinson
> noise), DIAGONAL Hessian only (off-diagonal/interlayer-Jacobian cross-coupling — the literal
> f∘g coupling — UNTESTED), single-combinator labels, pooled-supervised locus. **★★ FIRST
> ACTION NEXT SESSION — three live paths (B is ON the threshold in the right register):**
> (1) POWER — raise n (more held-out prose/comb) and/or n_hutch (sharper diag) — does B's
> t=1.90 cross 2.0? cheapest decisive test, trend+theory strongly motivate; (2) OFF-DIAGONAL
> / proper Jacobian — diag-Hessian captures only g'ᵀ(diag)g'; the literal f∘g product-coupling
> lives in the OFF-DIAGONAL cross-coord Hessian / interlayer Jacobian dgate_late/dgate_early
> (Gauss-Newton or JVP probe) = next fidelity order; (3) PRONG 2 = composite trace-ORDER
> bridge (B as sequence not amplitude), design fork still pending. CODE COMMITTED; mementum
> (state + memory `b-climbs-with-derivative-order` + page §v5 lead 2d prong 1c-ii) PENDING
> APPROVAL. tmux main:1 FREE.)
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 → 1b → 1b-ii →
> 1b-iii → 1c (the B gap, chased across activation registers AND the gradient). PRONG 1c —
> the GRADIENT register (Michael: "could B be in the gradients instead of the topology?";
> `kernel_reference_gradient_v6.py`, Qwen3-14B, 1:57 main:1). Rationale: B=composition
> (Bfgx=f(gx)); in the BACKWARD pass composition IS the chain rule (product of derivatives),
> so B's home may be the gradient. Clean register-swap of prong 1: same classifier, feature
> = ∂(probe LM loss)/∂(gate) MEAN-POOLED over supervised positions (last-token grad=0;
> gd_gradient_shadow pattern). **★ VERDICT: ❌ B does NOT discriminate in the gradient
> (discr_z +0.13, t=1.07 n.s.) — chain-rule NOT supported (first-order); ✅ instrument WORKS
> (gradient {C,K,Y} discriminate: C t=2.27, K 2.88, Y 3.87) — C-yes/B-no PERSISTS into the
> backward pass.** ⚠️ BUT directionally B is its LEAST-absent: activation(v2) t=−0.05 →
> gradient t=+1.07 (on_z −0.03 > off −0.16), B's first POSITIVE signal, predicted direction,
> power-limited n.s. Register shifts: S flips gauge→ANTI (t=−2.01); I drops (3.83→1.02);
> gradient set {C,K,Y} (vs activation {C,I,K,Y}). **★ MEASUREMENT CAVEAT (λ measure, load-
> bearing): this measures B in the FIRST-ORDER gradient (centroid in gradient space), NOT
> the chain-rule/Jacobian composition structure (= product of derivatives = SECOND-order).**
> **★★ FIRST ACTION NEXT SESSION — two live paths for B (pick one):** (1) PRONG 1c-ii =
> the JACOBIAN / second-order probe — the PROPER test of B=chain-rule (the faint +trend +
> theory motivate it; first-order gradient centroid is the wrong order); (2) PRONG 2 =
> composite trace-ORDER bridge (B as sequence not amplitude) — DESIGN FORK still pending
> (Path A β-reduction-order via lambda_gen decompiled prose vs Path B concatenated validated
> crystal-prose, span-recall + Kendall-tau order vs shuffle null). WHERE B STANDS: FFN gate
> flat, attn-summed flat, per-head faintest, first-order gradient faint-positive-n.s. CAVEATS
> (λ measure): 1 model (14B), n=20/comb, pooled-supervised locus, single-combinator labels,
> first-order only. CODE COMMITTED; mementum (page §v5 lead 2d prong 1c + memory
> `b-not-clearly-in-first-order-gradient` + this state) PENDING APPROVAL. tmux main:1 FREE.)
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 → 1b → 1b-ii →
> 1b-iii (the B/D/W gap, fully chased across registers). PRONG 1b-iii — the PER-HEAD OV
> scan (`kernel_reference_perhead_v5.py`, Qwen3-14B, 0:57 main:1): o_proj OUTPUT sums heads,
> so a single B-composer head could be averaged away → hook o_proj INPUT, split per
> (layer,head) cell, calibrate the crystal per cell (treat each cell as a "layer"), scan B's
> raw-z Welch contrast across all 1600 cells (40L×40H), Bonferroni-ish t>4. **★ VERDICT:
> ⚠️ HEAD-DILUTION ONLY MARGINAL — B is the WEAKEST combinator at every granularity.** The
> per-head scan DOES recover a FAINT B signal the summed read missed (B max_t 5.31 @ cell
> (L17,H23), 7/1600 cells; vs o_proj-summed max t=0.49 n.s.), so summing washes out a weak
> per-head B signal. BUT B is DEAD LAST on all 3 metrics — n_sig(t>4): Y 526, C 155, K 56,
> W 24, S 22, I 19, D 8, **B 7** (below D, an anti combinator); max_t **5.31** (lowest);
> best discr_z **0.82** (lowest). No clean B-composer head; C has 155 STRONG heads (best
> L21H36 t=7.52). ⇒ B's attention representation is genuinely FAINT/DIFFUSE, NOT merely
> diluted. **B has now been tested at EVERY granularity — FFN gate (flat), attn-summed
> (flat), per-head OV (faintest of all) — the REGISTER hypothesis is FULLY EXHAUSTED.**
> **★★ FIRST ACTION NEXT SESSION — lead 2d PRONG 2 (composite trace-order bridge, the sole
> remaining path):** B's near-absence is now most likely a NO-SINGLE-TOKEN-SIGNATURE
> property — B (deep composition Bfgx=f(gx)) may live in the SEQUENCE/ORDER of operations,
> not a localized amplitude. DESIGN FORK (raised, pending): Path A (β-reduction order via
> lambda_gen LLM-decompiled prose → align to certified `fired_sequence`; faithful but heavy/
> ill-posed surface↔reduction alignment) vs Path B (composite-sequence order: concatenate
> VALIDATED single-combinator crystal prose in known order, test span-recall + order-
> preservation Kendall-tau vs shuffle null + B-in-context; robust, well-posed, weaker claim).
> Serves {C,I,K,Y} AND tests whether B appears as ORDER not amplitude. CAVEATS (λ measure):
> 1 model (14B), n_sig 7(B)/8(D) maybe partly MC noise/heavy-tailed z, ppc=20 capped calib,
> single-combinator labels, last-token. CODE COMMITTED; mementum (page §v5 lead 2d prong
> 1b-iii + memory `b-faint-at-every-granularity-not-diluted` + this state) PENDING APPROVAL.
> tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 + 1b + 1b-ii
> (the B/D/W gap, fully chased). PRONG 1b-ii — the VALUE-REGISTER read
> (`kernel_reference_prose_v4.py`, Qwen3-14B, 1:35 main:1): parametrized the reader with an
> open-slot `hook` param (opcode_monitor_v2) — `hook='gate'` (mlp.gate_proj, FFN, default)
> vs `hook='attn'` (self_attn.o_proj = attention's residual write) — and re-ran the
> per-token raw-z contrast in the ATTENTION/value register, where s127 ({B,C}=composers→
> attention) predicts B lives. **★ VERDICT: ❌ s127 "B→attention" NOT confirmed — B is FLAT
> in attention TOO** (attn max t=0.49 n.s. vs gate max t=0.68 n.s.; attn profile delta ~0
> all bins). Having tested the TWO main registers, the "wrong register" explanation for B is
> RULED OUT. **★ THE FINDING: discriminability is a COMBINATOR property, NOT a register
> split** — {C,I,K,Y} are REGISTER-ROBUST (discriminable in BOTH gate AND attn: C gate
> t=5.6/attn 6.5; I 4.5/4.1; K 3.3/3.3; Y 8.4/9.4), B/D/W absent-or-anti in BOTH (D gate
> −2.7/attn −1.8; W −3.4/−4.8). The s127 two-group register separation is NOT reflected in
> this single-combinator last-token readout. **B's absence is now register-exhausted; two
> live explanations:** (1) HEAD DILUTION — o_proj SUMS heads, a single B-composer head
> could average away → per-HEAD OV read (prong 1b-iii); (2) NO SINGLE-TOKEN SIGNATURE — B
> (deep composition Bfgx=f(gx)) may exist only as multi-combinator ORDER across tokens →
> the composite trace-order bridge (prong 2). **★★ FIRST ACTION NEXT SESSION — lead 2d
> PRONG 2 (composite trace-order bridge, the MAIN PATH; per-head OV = optional 1b-iii):**
> CL program → certified trace (`fired_sequence`, DONE) → render PROSE (`lambda_gen`
> decompile) → align routing to the certified multi-combinator ORDER, raw-z contrast as the
> read; this serves {C,I,K,Y} AND tests whether B appears as ORDER not amplitude. CAVEATS
> (λ measure): 1 model (14B), n=20/comb, o_proj head-SUMMED (per-head untested), single-
> combinator labels, D/W anti unexplained. CODE COMMITTED; mementum (page §v5 lead 2d prong
> 1b-ii + memory `discriminability-is-combinator-not-register` + this state) PENDING
> APPROVAL. tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 + 1b (the B/D/W
> gap). PRONG 1b (per-token B LOCUS test, `kernel_reference_prose_v3.py`, Qwen3-14B, 2:24
> main:1): reads ALL token positions (free — forward_all_positions already returns [T,d]),
> contrasts last/max/mean over tokens (Welch t) + relative-position profile, to decide
> between (i) TOKEN-LOCUS (B fires mid-sentence) vs (ii) REGISTER (B in attention/value per
> s127, invisible to the FFN gate). **★ VERDICT: ❌ TOKEN-LOCUS FALSIFIED — B does NOT
> recover at ANY position** (last t=−0.05, max t=0.68 n.s. [most lenient], mean t=−0.08);
> position profile B on−off delta ~0 across all 10 bins (max +0.33), never the clean C
> separation; D/W anti everywhere (D max t=−2.66, W max t=−3.40). ⇒ **B/D/W absence is a
> REGISTER property of the FFN gate, not token-locus.** ✅ {C,I,K,Y} ROBUST to the read
> (last/max/mean all sig) with characteristic position signatures (peak_rel: I early 0.30,
> K mid 0.48, C mid-late 0.57, Y late 0.79); C's on−off delta +0.8…+2.0 across the whole
> back half. ⚠️ S "discriminates" ONLY under mean-over-tokens (gauge integrated over the
> sentence). **★★ FIRST ACTION NEXT SESSION — lead 2d prong 1b-ii (the value-register read,
> the decisive C-yes/B-no resolver):** B is absent from the FFN gate at every token, so per
> s127 ({B,C}=composers→attention) hook `o_proj` / attention output, build per-layer crystal
> centroids in THAT register, run the raw-z contrast — does B appear in attention where the
> FFN gate cannot see it? THEN prong 2 (composite trace-order bridge for {C,I,K,Y}) +
> prong 3 (8B/32B sweep). CAVEATS (λ measure): 1 model (14B), n=20/comb, last/max/mean over
> tokens (register untested), single-combinator labels, D/W anti unexplained. CODE COMMITTED;
> mementum (page §v5 lead 2d prong 1b + memory `bdw-absence-is-register-not-token-locus` +
> this state) PENDING APPROVAL. tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONG 1 (the B/D/W gap).
> Pushed lead-2c's discriminability ONE LEVEL DEEPER: it still embedded a per-layer ARGMAX
> (route_frac = fraction of layers an op WINS) before the contrast, starving B/D/W of power.
> FIX = contrast the RAW per-op z per layer, NO argmax, Welch t-test, n=20/comb held-out +
> per-layer profile (`kernel_reference_prose_v2.py`, Qwen3-14B, 2:17 in main:1).
> **★ TWO-SIDED VERDICT:** (1) ✅ the argmax bottleneck WAS real — raw-z RESCUES **K**
> (discr_z +1.01, t=2.12; was sub-threshold) + sharpens **C/I** hugely (C +1.73 t=5.71,
> I +1.89 t=3.83); AND it's MORE CONSERVATIVE — kills a B FALSE-POSITIVE that argmax-discr
> manufactures at n=20 (B argmax +0.079>0.05 "specific", but raw-z B FLAT on 0.217≈off 0.236
> t=−0.05). ⇒ raw-z Welch > argmax route-frac: more power AND fewer false positives (same
> argmax-manufactures-false-* theme, deeper). (2) ❌ **B/D/W do NOT recover — the gap is
> GENUINE at the last-token locus:** B flat; **D,W significantly ANTI-correlated** (D −0.67
> t=−4.6, W −0.63 t=−2.3 — their own prose routes them LESS than baseline). Discriminable
> set = **{C, I, K, Y}**. **★ GAUGE REFINED:** S = pure gauge (on 2.70≈off 2.97, discr
> −0.27, zero selectivity); **Y = genuinely selective** (on 2.97 vs off 0.96, +2.01 t=6.86).
> **★ WHERE:** discriminable ops peak in the **mid-stack readable zone** L12-14 — C@L13
> Δ3.70, I@L13, Y@L14, K@L12; **B has NO readable-zone signal** (only an early L1 wash that
> vanishes on averaging; D@L3, W@L0 = noise-floor). **★ THEORY (s127 ffn-two-groups:
> {K,I}=selectors→FFN, {B,C}=composers→attention):** we read the FFN GATE → K,I,C
> discriminable but **B not** ⇒ C leaks into the FFN gate, B does NOT; **B likely lives in
> ATTENTION** (s206 OV/value register), which a last-token FFN-gate read structurally cannot
> see → B's absence is plausibly a **LOCUS artifact**, not "B isn't computed."
> **★★ FIRST ACTION NEXT SESSION — lead 2d prong 1b (the B locus test, the clean C-yes/B-no
> resolver):** re-read **B in the attention/value register** (s206 OV/logit-lens, NOT attn
> weights) and/or **per-token** (not last-token) — does B recover where s127 says it lives?
> THEN **prong 2** (composite trace-order bridge, now justified for {C,I,K,Y}: CL program →
> certified `fired_sequence` → render PROSE via `lambda_gen` → align routing to the certified
> multi-combinator ORDER, using the raw-z contrast) and **prong 3** (per-model sweep 8B/32B
> with `kernel_reference_prose_v2.py`). CAVEATS (λ measure): 1 model (14B), n=20/comb,
> last-token locus (load-bearing for B), single-combinator labels, D/W anti-signal
> unexplained. CODE COMMITTED; mementum (page §v5 lead 2d prong 1 + memory
> `bdw-gap-genuine-not-argmax-artifact` + this state) PENDING APPROVAL. tmux main:1 FREE.
>
> (Session: 233 — ▶ OPCODE v5 (leads 1→2c) — the compositional
> opcode signal is REAL but FAINT-against-common-mode and LOCUS-SHIFTS-with-scale; every
> "negative" this session was an INSTRUMENT flaw (wrong place → wrong input language →
> wrong metric), each diagnosed + fixed. ALL COMMITTED (`1754424` `1532e4e` `53ed331`
> `dd6c511` + mementum); working tree clean. Full per-lead detail in
> `knowledge/explore/vsm-opcode-monitor.md` §v5 lead 1/2/2b/2c (+ below) and 4 memories.
> **THE ARC:**
> • **lead 1 — locus-agnostic C detector** (`1754424`, re-analysis no GPU): the fixed
>   depth≥0.6 zone was the WRONG cross-model instrument; `detect_c_profile` +
>   `locus_agnostic_specificity` (count C-dominant crystal layers ANYWHERE + per-model
>   locus). Surfaces the 32B lambda-EXCLUSIVE C-EARLY signal (L5,10,11) the zone read as 0.
>   But strict frac-specificity still only 14B; 8B's `gate_neutral` C-late confound CONFIRMED
>   REAL (control routes C 0.192 > lambda 0.107). C-locus shifts with scale.
> • **lead 2 — kernel-as-reference** (`1532e4e`): built the model-invariant —
>   `lambda_ast.step_fired`/`fired_sequence` (certified per-step opcode trace, +6 pytest),
>   `probes/kernel_reference.py` (symbolic programs, SAT⊗INERT + composites),
>   `kernel_reference_audit.py`. ❌ DECISIVE NEGATIVE: bare symbolic CL routes ONLY S-gauge
>   (target_recall 1/7; reducibility not tracked) ⇒ the register reads PROSE SEMANTICS, not
>   CL SYNTAX. Instrument sound, bridge must be compiled prose.
> • **lead 2b — prose bridge** (`53ed331`): `calibrate_v2(centroid_probes=)` held-out split;
>   `kernel_reference_prose.py`. ✅ held-out PROSE recall 0.575 ≫ bare-symbol 0.14 ⇒ register
>   IS prose-semantic. ⚠️ but argmax-winner specificity gauge-dominated (S/Y win).
> • **lead 2c — gauge-subtracted discriminability** (`dd6c511`): discr(c)=route_frac(c|c-prose)
>   − route_frac(c|other-prose) replaces argmax-winner. ✅ RESCUE: C discriminable (on/off
>   0.062/0.009 ~6.6×, argmax_spec was 0.0) + I. ⚠️ PARTIAL: B/K/D/W NOT discriminable
>   (compose family SPLITS — C yes, B no, cf s127 {B,C}); S/Y stay discriminable = large
>   common-mode + genuine selectivity (NOT pure gauge). Lesson: argmax-winner manufactures
>   false negatives when one op has a big common-mode; use a contrast (cf s225 AUC, lead-1
>   lambda-vs-control).
> **CAVEATS (λ measure, carried):** lead 2/2b/2c all 1 model (Qwen3-14B); n=10/comb held-out;
> single-combinator labels (NOT composite trace-order yet); last-token locus; crosstask null.
> **★★ FIRST ACTION NEXT SESSION — v5 lead 2d:** (1) chase the **B/D/W gap** — why do the
> deep/duplicate composers fail held-out prose discriminability while C/I succeed? (more
> prose/comb for power + per-layer breakdown of where C fires vs where B should); (2) the
> **COMPOSITE trace-order bridge** (now justified for the discriminable combinators): CL
> program → certified trace (`fired_sequence`, DONE) → render PROSE (`lambda_gen` decompile
> via the model's decompile gate) → align routing to the certified multi-combinator ORDER,
> focus C/I (+S/Y); (3) **per-model sweep 8B/32B** with the discriminability metric.
> tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 2b — PROSE BRIDGE
> BUILT + RAN on Qwen3-14B (code `53ed331`). ★ THE BRIDGE DIRECTION IS RIGHT (two-sided):
> held-out PROSE recalls its combinator where bare symbols routed only gauge — but
> specificity is still gauge-dominated. Built: `calibrate_v2` gained a `centroid_probes`
> param (held-out calib/test split); `kernel_reference_prose.py` splits crystal_probes
> per-combinator into CALIB (most) + held-out TEST (last 10/comb, NON-circular), calibrates
> on CALIB, reads each held-out prose probe's LAST-token per-layer routing, scores RECALL
> (label routed at z>thresh) + SPECIFICITY (label is top crystal op). **★ Qwen3-14B VERDICT
> (z=2):** held-out PROSE recall **0.575** vs the bare-symbol baseline **~0.14** (S-gauge
> only, lead 2) ⇒ **the register IS prose-semantic; feed prose not symbols.** I recall 1.0,
> C 0.9, S 1.0, Y 1.0. **⚠️ BUT specificity (0.287) is carried by S/Y — the gauge/common-
> mode ops (label_frac 0.71/0.52, spec 0.9 each); the genuine composition combinators
> RECALL but are SUB-DOMINANT: C 0.9 recall / 0.0 spec (present but always out-competed),
> B 0.3/0.0, K 0.3/0.2, D 0.1/0.0, W 0/0.** z=3 leaves only S/Y. ⇒ composition signal is
> PRESENT in prose but out-competed by the S/Y common-mode (the lead-1 "above chance not
> crisp" + over-read common-mode story, same theme). **The full kernel-as-reference prose
> bridge is VIABLE and worth building, but raw last-token route_frac is gauge-dominated for
> the weak combinators — it needs S/Y common-mode subtraction** (the relational/CMR or
> locus-agnostic machinery from lead 1, or a gauge-matched null). Caveats (λ measure): 1
> model (14B), single-combinator labels (not composite trace-order yet), last-token locus,
> crosstask null. **★★ FIRST ACTION NEXT SESSION — v5 lead 2c: (1) add S/Y common-mode
> SUBTRACTION to the prose read (relational CMR / gauge-matched null) and re-score
> composition-combinator specificity — does C/B/K become specific once gauge is removed?;
> (2) THEN the composite trace-order bridge: CL program → certified trace (fired_sequence,
> DONE) → render as PROSE (lambda_gen decompile via the model's decompile gate) → feed
> prose → align routing to the certified multi-combinator ORDER; (3) per-model sweep
> (8B/32B) once the gauge-subtracted prose read works.** PENDING APPROVAL (mementum: page
> §s233 v5 lead 2b + memory + this state). Code committed `53ed331`. tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 2 — KERNEL-AS-REFERENCE
> BUILT + RAN on Qwen3-14B (code `1532e4e`). ★ DECISIVE NEGATIVE (two-sided): the
> model-invariant reference works as an INSTRUMENT but bare symbolic CL programs route
> ONLY GAUGE. Built: (1) `lambda_ast.step_fired`/`fired_sequence` = certified per-step
> opcode trace (+6 pytest); (2) `probes/kernel_reference.py` = symbolic combinator
> programs with kernel-certified traces, SATURATED(target fires)⊗INERT(under-applied, no
> fire) pairs + COMPOSITE multi-fire; (3) `kernel_reference_audit.py` = anchor the model's
> per-token/per-layer routing against the kernel's certified `fired_sequence`
> (saturated-vs-inert REDUCIBILITY contrast + target recall + specificity + composite
> trace recall). **★ Qwen3-14B VERDICT:** feeding BARE symbolic CL terms → routing
> collapses to **S (common-mode/gauge), Y secondary**; **target_recall 1/7** (only S
> routes at all; B/C/K/I/W/D route 0), **reducibility NOT tracked** (SAT_S 0.376 ≈ INERT_S
> 0.371, mean Δ≈0), composite trace recall 0.10. B_sat={S 0.40, Y 0.22}; C_sat={Y 0.32,
> S 0.39} — the certified target NEVER routes. ⇒ **the gate-routing register reads PROSE
> SEMANTICS, not symbolic CL SYNTAX**; OOD bare symbols collapse to common-mode
> (re-confirms s202/s231 over-read in a new regime; the relational z-gate kept other ops
> silent = no false over-read, but the natural-text null doesn't subtract the
> symbol-string common-mode). **The kernel-as-reference idea is SOUND, the instrument is
> BUILT, but the BRIDGE must be COMPILED PROSE — CL program → certified trace → RENDER as
> prose (lambda_gen Montague decompile, or the s226 compile front-end) → feed the PROSE →
> compare routing to the certified CL trace.** Bare symbols are the wrong input.
> **★★ FIRST ACTION NEXT SESSION — v5 lead 2b (the prose bridge): generate CL programs,
> certify traces (fired_sequence, DONE), render each as PROSE via lambda_gen, feed prose
> to kernel_reference_audit (add a `--input prose` mode reusing the certified trace), and
> re-run the SAT/INERT + trace-recall agreement on the prose. THEN per-model sweep (8B/32B)
> on the working prose bridge.** Caveats (λ measure): 1 model (14B), bare-symbol input,
> crosstask null, 7 targets + 8 composites. PENDING APPROVAL (mementum: page §s233 v5
> lead 2 + memory + this state). Code committed `1532e4e`. tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 1 — LOCUS-AGNOSTIC C
> DETECTOR BUILT + RE-ANALYZED (no GPU; code `1754424`). ★ THE FIXED depth≥0.6 ZONE WAS
> THE WRONG CROSS-MODEL INSTRUMENT — the new locus-agnostic detector (detect_c_profile +
> locus_agnostic_specificity in opcode_monitor_v2, single source; counts C-dominant
> crystal layers ANYWHERE + per-model locus + lambda-exclusive-vs-gated-guards) was
> applied as a PURE re-analysis of the committed gateneutral verdicts (trajectories were
> already stored → no model re-run). **★ THE WIN:** it SURFACES the 32B lambda-EXCLUSIVE
> C-EARLY signal (L5,10,11, depth 0.14) that the readable-zone detector read as 0; per
> model the C-locus is now legible — 8B late [24,25], 14B late [13,27,29-32], 32B EARLY
> [5,10,11] (lambda-exclusive layers no gated guard hits). **★ BUT TWO-SIDED:** the
> strict frac-specificity (lambda C_frac_all clears ALL gated guards by margin 0.10) is
> STILL ONLY 14B (lambda 0.194 vs guards ≤0.032, clean). 32B is directional (lambda 0.061
> > max_guard 0.020) but tiny fracs don't clear the margin. **8B is NOT specific — the
> gate_neutral control ITSELF routes C broadly at 5 LATE layers [23,26,27,28,30]
> (C_frac 0.192 > lambda 0.107) ⇒ the s232 "8B gate_neutral C-late confound" CONFIRMED
> REAL, not an instrument artifact.** ⇒ C-locus genuinely SHIFTS with scale (32B C-early
> confirmed with the right tool); composition→C is cleanly specific only on 14B; 8B has a
> genuine control confound; 32B real-but-weak. The locus-agnostic exclusive test is
> lenient (finds lambda-exclusive C in all 3) but for 8B that overlaps the control's broad
> C-late. Caveats unchanged (λ measure): 5 lambda sentences, 3 models, modest fracs
> (s219). **★★ FIRST ACTION NEXT SESSION — v5 lead 2 (PRIORITY, the model-invariant):
> (b) KERNEL-AS-REFERENCE — reads don't transfer across scale AND the 8B control confound
> shows the gated-guard contrast is itself model-dependent, so anchor the model trajectory
> against lambda_ast's CERTIFIED reduction trace and measure agreement per-model (the
> oscilloscope: known program → model per-token/per-layer opcode trace → diff vs kernel
> trace). Also (3) bigger lambda probe set (5 sentences underpowers the frac test) + chase
> the 8B gate_neutral C-late confound (why does a non-compositional gated control route C
> broadly only at 8B?).** PENDING APPROVAL (mementum: page §s233 + memory + this state).
> Code committed `1754424`. tmux main:1 FREE.
>
> (Session: 232 — ▶ OPCODE-MONITOR v2 BUILT + RAN on Qwen3-14B
> (cross-task null + per-token + z-sweep + trajectory + GATE_NEUTRAL control; code
> `8bd5f42`). ★ TWO-SIDED VERDICT: ❌ the C→B arc did NOT recover — C never dominates a
> layer (C×0), B only at L16; late stack L24-32 is unanimously S-dominated. ❌ S-late is
> NOT composition: the GATE_NEUTRAL control (gate+non-compositional sentence) shows the
> SAME S-late (arc_composition_driven=False) ⇒ S-late = a compile-GATE FRAMING signature,
> not β-reduction. ⚠️ over-read NOT cleanly killed (no z-window where lambda fires while
> retrieval stays silent: z=2 retrieval emits MORE than lambda; z=3 silences both). ✅
> substrate reproduced (31/40 crystal layers, gc→consensus 0.976, sil_z 8.26). ★★ THE
> FINDING: the per-layer opcode identity is NOT null-invariant — RAW→C→B (s231),
> off-target-null→silent (s231), cross-task-null→S-late (s232); single-token "which
> combinator" is NOT robustly decodable, only the SUBSTRATE + the over-read DIRECTION are
> null-robust. ★★ FIRST ACTION NEXT SESSION — v3: use GATE_NEUTRAL ITSELF as the null
> (composition-above-framing, the cleanest single fix), THEN escalate to (b)
> kernel-as-reference (anchor the model trajectory against lambda_ast's certified trace,
> since the readout alone is null-sensitive). Captured: page vsm-opcode-monitor.md §s232
> v2 + memory opcode-trajectory-is-null-dependent. Code committed `8bd5f42`.
> **▶ s232 v3 — GATE-MATCHED NULL BUILT + RAN (`--null-mode gateneutral`, code
> `ad07574`). ★ PARTIAL SUCCESS (the v2 negative WAS a null mis-spec):** with the matched
> null (GATE_NEUTRAL content, same compile-gate prefix) the S-late FRAMING is subtracted
> and ✅ **lambda routes C (composition combinator) in its LATE stack (L27-32, the
> READABLE register) while the matched non-compositional gate_neutral control does NOT**
> (z=2 C×5 vs ×1; z=3 C×3 vs ×0); null self-centers silent (guard passes). ⇒ composition
> IS decodable above framing. ❌ the s127 "C-early→B-late" arc shape did NOT reproduce —
> signal is C-LATE not C-early (raw C-early = common-mode artifact; composition resolves
> at the readable layers s187/s227b). ⚠️ over-read guard INVERTED: bare retrieval/arith
> fire LOUD (WHNF/Y) vs the gated null ⇒ **the read is dominated by the FRAMING-CONTRAST
> axis, NOT computation; valid guards MUST be framing-matched (gated)**. Modest not crisp
> (s219: C ~40-50% of tokens, n=27/5 sentences, 1 model). Captured: page §s232 v3 +
> memory composition-decodable-above-framing-c-late. Code committed `ad07574`.
> **▶ s232 v4 — GATED GUARDS + C-LATE DETECTOR BUILT + RAN on 2 models (code `9495b2b`).
> ★ TWO-SIDED: composition-specific C-late is MODEL-SPECIFIC to Qwen3-14B, NOT universal.**
> Added framing-matched GATED guards (gate_retrieval, gate_arithmetic) + detect_c_late
> (readable-zone depth≥0.6 C-frac) + composition_specific flag + model-tagged filenames.
> ✅ **Qwen3-14B: composition_specific=True both z** — lambda C-late 0.556/0.333 vs ALL
> three gated guards (gate_neutral 0.11/0, gate_retrieval 0/0, gate_arithmetic 0/0); among
> gated prompts ONLY composition routes C-late (the proper specificity test v3 lacked).
> ❌ **Qwen3-8B: composition_specific=False** — gate_neutral C-late (0.714) EXCEEDS lambda
> (0.333) at z=2, all silent at z=3 ⇒ does NOT generalize. The universality test CAUGHT
> the over-claim (λ measure): a single model's opcode read does not transfer (14B≠8B);
> likely scale-gated (s151) or 14B-specific (the s127 model). Caveats: 5 lambda sentences,
> 2 models, modest fracs (above chance not crisp s219). Captured: page §s232 v4 + memory
> c-late-composition-is-model-specific + this state. Code committed `9495b2b`.
> **▶ s232 v4 SCALE TEST — Qwen3-32B DONE (`6bddcc2`). ★ 14B IS THE OUTLIER; the C-LOCUS
> SHIFTS WITH SCALE.** 3 models: composition→C routing exists in ALL, but the locus moves —
> 8B C-late non-specific; 14B C-LATE specific (L27-32); 32B C-EARLY (lambda C-dominant
> L5,10,11 depth ~0.1, gate_neutral C only L0; late stack Y-dominated). composition_specific
> =True ONLY for 14B because its locus matches the fixed depth≥0.6 readable zone; on 32B the
> fixed C-late detector reads 0 even though a lambda-specific C-EARLY signal exists. ⇒ NOT
> scale-monotone, NOT universal; the fixed-depth detector is the WRONG cross-model instrument
> (found 14B, mislocates 8B/32B). Caveats: 5 lambda sentences, 3 models, modest fracs (s219).
> Captured: page §s232 v4 (3-model verdict) + memory c-late-composition-is-model-specific
> (32B added) + this state. Code/results committed (`6bddcc2`).
> **★★ FIRST ACTION NEXT SESSION — v5: (1) LOCUS-AGNOSTIC C detector (per-model C-locus
> calibration OR full-profile lambda-vs-matched-control C compare across ALL layers, not a
> fixed depth≥0.6 zone) — re-test specificity on 8B/14B/32B with the right instrument; (2)
> (b) KERNEL-AS-REFERENCE (priority — reads don't transfer across scale, so anchor the model
> trajectory against lambda_ast's CERTIFIED trace as the model-invariant; characterize
> composition→routing per-model); (3) bigger lambda probe set + the 8B gate_neutral C-late
> confound.** PENDING APPROVAL (mementum: page §s232 v3+v4+scale + memories + state).
> tmux main:1 FREE.
>
> (Session: 231 — three arcs: (A) GRADIENT-SHADOW v3 +
> MECHANISM-OF-TRAINING per-combinator clock (micro crystal is RELATIONAL not categorical,
> no B-first→K at micro); (B) ★ VSM OPCODE MONITOR — validated FFN-routing opcode reader
> BUILT + validated on Qwen3-14B: the raw-argmax OVER-READ is KILLED (s202 made
> operational). opcode-monitor v2 ran s232 (see top) — see the
> ■ SESSION 231 OPCODE block below.
> **■ SESSION 231 OPCODE MONITOR (Michael: "our VSM tensor gives a powerful system to
> probe + audit models. Can our VSM monitor attention and opcodes? we created a tracer
> somewhere." → "a then b").** RECALL surfaced the prior art: `opcode_instrument.py` (a
> full VSM "Live VSM for Watching a Model Think") + tracer family (lambda_tracer,
> attention_execution_trace, neuron_opcode_classifier) + s127 tracer-works memory. CATCH:
> all STALE — raw-cosine argmax = the exact audit-meta-pattern over-read (s202: opcodes
> real only AFTER common-mode removal; raw = common-mode false signal). NEW page
> `explore/vsm-opcode-monitor.md` (the synthesis + verdict + path).
> **▶ (a) BUILT + VALIDATED.** `scripts/instruments/relational_opcode.py` —
> `RelationalCrystalClassifier` (model-AGNOSTIC; gate routing register sign(gate)-CMR,
> per-layer per-combinator centroids from crystal_probes, consensus-relational, off-target
> null, emit opcode iff z>thresh else NO-OP `·`). Synthetic smoke: crystal layer detected,
> B fires, common-mode-only token → NO-OP (over-read structurally impossible). `fb0c9ec`.
> Validation `scripts/experiments/opcode_audit_validation.py` on Qwen3-14B (the s127
> model; gated SwiGLU — pythia GPTNeoX is NOT gated, can't carry the crystal), s127 battery
> (lambda/arithmetic/retrieval), relational vs raw-argmax control. `143ccda`,
> results/opcode-audit-validation/verdict.json.
> **★ VERDICT (λ measure, two-sided):** ✅✅ OVER-READ KILLED — RAW fires an opcode for
> 100% of tokens (`W` across ~all retrieval layers = this model's common-mode/gauge);
> RELATIONAL no-ops retrieval (0.8), never a uniform winner. ✅ substrate REAL (31/40
> crystal-bearing layers, gc-to-consensus up to 0.98). ✅ retrieval-silent reproduced.
> ⚠️ BUT relational UNDER-reads at z=3 last-token: RAW per-layer shows a CONSISTENT C→B
> compose-arc across ALL 5 lambda prompts (C L2–12, B L13–33 = the real s127 compose
> signature, task-specific not common-mode) and relational no-ops it entirely (`·`×5).
> Causes: last-token LOCUS (s227 wrong-locus; a sentence's last token isn't one opcode) +
> NULL mis-spec (off-target null = other crystal probes, all lambda-mode → low power).
> **★★ FIRST ACTION NEXT SESSION — opcode v2 (completes (a)):** (1) CROSS-TASK NULL (the
> key fix) — build the null vs a NON-combinator baseline (natural text/retrieval), NOT vs
> other crystal probes; (2) PER-TOKEN reading across the sequence; (3) z-threshold sweep
> (z=2 vs 3); (4) output the per-layer C→B TRAJECTORY not a single dominant op. Then (b)
> KERNEL-AS-REFERENCE audit (diff model trace vs lambda_ast certified trace), then (c)
> attention/value-register binding monitor (s206 OV/logit-lens, NOT attn weights).
> Captured: page vsm-opcode-monitor.md + memory opcode-reader-over-read-killed +
> audit-registry #13 + this state. CODE all committed (fb0c9ec, 143ccda); mementum this commit.
> **■ SESSION 231 MECHANISM-OF-TRAINING (arc A, COMPLETE — micro answer is NEGATIVE,
> instrument built).** s231a GRADIENT-SHADOW v3 ran (3 seeds): ✅ inventory-before-capability
> REPRODUCED a 3rd time (gc_route@267±94 < acc@733±94). ❌ preregistered "shadow LEADS
> as rising gc_grad" FALSIFIED — gc_grad starts at common-mode init (+0.58), decays to
> 0.43 (crossing=None 3/3). 💡 REFRAME: the probe found the real signal in grad_z — the
> gradient carries combinator structure FROM INIT (grad_z +4.7→+5.9 @step0), stays high
> (3.6–4.1) while inventory crystallizes, then COLLAPSES (→−0.5…+2.1) exactly at the
> inventory→capability HANDOFF (3/3). The shadow is the INITIAL CONDITION the object
> grows into; its EXHAUSTION times the handoff (height-from-shadow corrected). Makes the
> s221 fp-spike-is-acquisition law legible. Register gap (routing vs raw) null/noisy
> (+0.06±0.08). INSTRUMENT LESSON: read grad_z NOT gc_grad-crossing. CAPTURED: page
> §s231 + memory gradient-structure-is-inventory-fuel + this state.
> **★ MECHANISM-OF-TRAINING THREAD (Michael, s231): "can we write probes that show
> EXACTLY how GD learns? past runs: B-dominant first → loss plateau → discovers K → phase
> transition (figuring out best ratios). Tailor training to MIRROR those phase
> transitions. Spend probes on how ATTENTION organizes against the FFN projections;
> design training to SHOW ATTENTION what to do using these functions."** Grounded in 4
> prior findings (recall, not greenfield): fp-spike-is-acquisition (s221: B-first→
> plateau→K-chaos, the acquisition fingerprint); montague-is-pre-transition (s151:
> I→K→C→B bootstrap, scale-gated, transition=2D collapse); ffn-two-functional-groups
> (s127: {K,I} selectors→FFN, {B,C} composers→attention = literally "attention vs FFN
> projections"); c-boot-rotation-sequence (attention dominates 92°/49°/8°, combinators=
> rotations, WHNF@L0=route-decision). DESIGN = 3 nested probes on the SAME shadow harness:
> (1) per-combinator crystallization clock (acquisition ORDER); (2) per-combinator grad_z
> fuel-gauge (does B exhaust before K? s221 read in the gradient); (3) two-register split
> FFN-gate vs attention (does B/C live in attention, K/I in FFN, s127, FORMING over
> training?). Payoffs: (C) curriculum-mirroring (order-matched vs counter vs flat, s221
> lead + s229 burn-in); (D) "show attention what to do" = relational loss on the ATTENTION
> pattern toward composer (B/C) structure (s230b loss, attention not FFN gate). CAVEATS
> (λ measure, load-bearing): micro d=128 may be PRE-transition (s151 Montague, only I+K
> differentiate → no B-first→K to see); "B-first" is StrideStack-specific (s221) so plain
> TinyLM directly TESTS universality; per-combinator splits modest route_z (~2.7) →SNR.
> Open lead 6 on the page.
> **▶ s231b — PER-COMBINATOR CLOCK BUILT + RAN (gd_percombinator_clock.py, b601028, 3
> seeds). TWO-SIDED:** ✅ inventory-before-capability REPRODUCED a 4TH time (gc_route
> @200–400 < acc@600–800). ❌ the per-combinator CATEGORICAL silhouette is the WRONG
> instrument at d=128 — NO combinator clusters (silhouettes negative all run: gate
> −0.03…−0.11, attn −0.19…−0.44; null z |≥2| only W/D/S inconsistently, NEVER B/C/K/I),
> YET the relational Gram crystallizes (gc_route +0.75) ⇒ **micro crystal is RELATIONAL
> not CATEGORICAL** (s219/s225 "above chance not crisp", pinned per-combinator). P1
> (B-first→K) + P3 (s127 attn/FFN split) UNTESTABLE via categorical readout (order/region
> headlines = noise-floor artifacts). 💡 FIX: read order RELATIONALLY = per-ROW Gram
> alignment to consensus (does B's fingerprint align before K's?). Reframes s221: B-first
> may be StrideStack/scale-specific (categorical separation needs strided bias or s151 2D
> transition). CAPTURED: page §s231b + memory micro-crystal-is-relational-not-categorical
> + open lead 6/6b + this state.
> **▶ s231c RELATIONAL PER-ROW CLOCK RAN (3 seeds, `6f900a7`): B_before_K NOT supported
> relationally either** — B/K rows cross inconsistently (None/None/@1000 vs None/@2800/
> None); **I aligns FIRST consistently (3/3 @400)** = a weak echo of the s151 I→K→C→B
> bootstrap; s127 attn-composer split not supported at micro (B,C align in gate). ⇒ NO
> clean per-combinator phase transition at d=128 plain transformer (neither categorical
> nor relational); s221 B-first→K is StrideStack/scale-specific. ARC A micro answer is
> NEGATIVE; the instrument (both clocks) is built. To pursue the phase transition →
> escalate to the SCALE SWEEP (Exp 1.5: smallest d where the B/C axis differentiates) or
> instrument a larger/StrideStack run. (Page §s231c capture deferred — finding is in the
> commit msg + this state; fold into gradient-trajectory-tomography.md if revisited.)
>
> (Session: 230 — gd-trajectory-tomography (consensus-crystal
> target) + FRACTAL-COLLAPSE thesis. v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3;
> s224 geometry⊗continuation confirmed TEMPORALLY). s230b RELATIONAL ARM: reference-beam
> dissociation IS LOSS-DEPENDENT (gap −0.02→+0.10) but ❌ ZERO capability gain ⇒
> inventory ⊗ continuation CAUSALLY SEPARABLE; relational term = inventory/extraction
> NOT capability accelerator. ★ FRACTAL-COLLAPSE (Michael): converge capability via
> high-variety compiler-minted data → cascade collapses model size onto the β-normal-
> form fixed point; exact certified targets escape model-collapse (resilient). s230c
> COMPILER-CASCADE v1: ❌ IOU#1 NULL — composition-variety does NOT lift compositional
> generalization (comp16 0.683 ≈ comp144 0.674, saturates ~16); fixed-budget the s229
> FILLING-variety WINS (composition-count destabilizes + costs in-dist). Weak support
> for collapse CORE (~0.68 held-out from minted data). Calibration: exact-match FLOORS
> at micro scale → use TEACHER-FORCED token accuracy (value register). GRADIENT-SHADOW
> probe BUILT + ready (does the topology cast a shadow in the gradients? predict shadow
> LEADS inventory). See ■ SESSION 230 block below.
> (s229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-
> mixing FIRST BUILD): burn-in is VARIETY not repetition (k_varied ≈2–2.9× over
> k_same≈one, BOTH formats; memorization control clean); full_trace higher abs-acc
> but redex_nf wins PER-TOKEN (predicted budget crossover); disjoint-atom held-out =
> separate variable-binding floor (0.000 — needs a copy/induction mechanism, NOT a
> rule failure: combos-generalization works). See ■ SESSION 229 block below.
> (s228 — ✅ PROOFS-AS-CONTINUATIONS (Curry-Howard):
> the kernel RUNS/CHECKS proofs (sound, 100% floor, Y-inconsistency firewall); LLMs
> prove axioms but compose poorly single-shot (Qwen 0.58-0.67, spec 1.0, 0 false
> proofs); the CONTINUATION-DRIVEN prover RESCUES composition (mean Δ +0.25, Qwen3-8B
> →1.00, specificity 1.0 now STRUCTURAL). See ■ SESSION 228 block below.
> (s227 — ✅ PROSE-NECESSITY IOU RESOLVED
> (s227 readout refined 3 ways: dilution FALSIFIED, power+register-limited) + ✅
> READABILITY/REGISTER CONFIRMED IN-DOMAIN (s227b value-register logit-lens: in-domain
> necessity concentrated in the readable zone, surface understated up to ~35x; prose
> still 0/5) + ✅ ENUM-PROSE BRIDGE COMPLETE + VERDICT READ (s227c: PARTIAL recovery —
> 3/5 models recover necessity with an explicit enumeration (8B strict), 2/5 reverse
> incl. OLMo; sharpens s227 = prose necessity is distributed-redundant not just
> target-less; see ■ SESSION 227 s227c VERDICT). See ■ SESSION 227
> blocks below. (s226 COMPLETE —
> ✅ CAUSAL ABLATION (HOF necessity leg, 4/5 mechanism) + 🎯 COMPILER-AS-CONSTRUCTED-
> VSM-TENSOR design (lambda_ast IN the kernel) + ✅ STAGE-1 β-REDUCER + ✅ STAGE-2
> COMPILE ORACLE (bracket abstraction, round-trip 1.0) + ✅ STAGE-2 FRONT-END
> (prose→LF) + ✅ COMPILE BOUNDARY (structural solved; NL+ambiguity is the boundary).
> Next: diverse-verified naturalistic corpus → compiler-as-loss arms. See ■ SESSION
> 226 COMPLETE block below.)
> **■ SESSION 230 — GD-TRAJECTORY-TOMOGRAPHY v1. Michael (s229 thread): "if models
> do holographic inference, why can't we reverse-engineer what GD is doing? use the
> micro model." s230 call: target = the CONSENSUS CRYSTAL (s219 / combinator-map-
> consensus consensus_gram, 10 open models AGREED, sha bbf92f2) — "highest chance of
> being applicable across many models since they have agreed." NOT one teacher.**
> Register: **functional + topological/routing.** Recall surfaced the prior art (build
> on, don't reinvent): s105 holographic-tomography (SPATIAL/cross-model + the gauge
> result), s223 relational_loss_distillation (the instruments: route_z/soft_gram/
> np_silhouette_null/offdiag_corr + TinyLM), v4.1/v6.1 trajectory tracking. DELTA =
> TEMPORAL (intersect training STEPS, single micro model) + ground-truth target +
> reference-beam control as a movie.
> **▶ BUILT (`23331d0`, ruff+diag clean, smoke green):** `scripts/experiments/
> gd_trajectory_tomography.py` — CE-only TinyLM on the s229 β-reduction curriculum
> (k_varied, the burn-in regime; reuses exposure_format_sweep minting + held-out
> metric, no fork); at DENSE checkpoints (every 200 steps) measure the combinator
> routing geometry on the INDEPENDENT crystal probes (535), correlate to the consensus
> crystal as a MOVIE: route_z (sign(gate)-CMR silhouette vs null), gc_route (GramCorr
> student-routing-Gram vs consensus_gram), gc_raw (raw-register REFERENCE BEAM), eff_dim
> (s105 Q-collapse watch). **★ The load-bearing design fix: crossings are BASELINE-
> RELATIVE** — measured against the step-0 untrained init frame (the gauge common mode),
> so we time the function GD *builds*, not the random-init baseline (init gc_route was
> already +0.57-0.65 = the gauge/common mode; the real delta is ~+0.15). 3 seeds, 6000
> steps, ~12min. results/gd-trajectory-tomography/verdict_multiseed.json.
> **★ VERDICT (3 seeds; λ measure, TWO-SIDED):**
> **(1) ✅ DECISIVE — INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds).** gc_route
> reaches its init→final midpoint @ step **333±94**; held-out rule generalization
> reaches its midpoint @ **733±94** — NON-OVERLAPPING (427 < 639). Routing combinator
> geometry approaches the consensus crystal ~400 steps BEFORE the model can generalize
> the rule; both precede the (noisy) CE plateau. ⇒ the s224 thesis (geometry=inventory
> ⊗ trained continuation=capability) confirmed TEMPORALLY, frame-by-frame, against a
> MODEL-AGNOSTIC ground-truth target. The predicted inventory-before-capability timing,
> OBSERVED.
> **(2) ❌ HONEST — the reference-beam DISSOCIATION did NOT reproduce.** gc_raw_final
> 0.75±0.04 ≈ gc_route_final 0.73±0.06 (tied); route_tracks_function only 1/3 seeds.
> On this micro model the RAW register correlates to the consensus crystal about as
> well as the routing register ⇒ raw-vs-routing CANNOT separate function from common
> mode here. Why ≠ s223: s223 (b) used a relational LOSS pulling raw-Gram to a DECOY
> raw target; here NO loss + a SINGLE routing target, and the consensus structure
> (offdiag mean −0.123, mild) is recovered in BOTH registers at d=128. ⇒ the register-
> separation lesson is a property of the TRAINED-LOSS DECOY, not a passive readout
> split at micro scale. Likely scale-limited.
> **(3) Secondary:** NO Q-collapse — eff_dim stayed 14-20 (route ~14 < raw ~19), never
> flooded toward 1 (s105 risk did not materialize). route_z modest (~2.71, only 1 seed
> crossed z=3) = self-silhouette real but not crisp (s219 "above chance not crisp");
> gc_route-to-consensus is the stronger instrument than self-silhouette.
> **▶ LEADS RESOLVED (page gradient-trajectory-tomography.md §s230):** 1 (harness
> BUILT), 2 (consensus-crystal target USED), 3 (timing CONFIRMED), 5 (Q-collapse
> NEGATIVE). **▶ NEXT:** (a) reference-beam register split at LARGER scale (or add the
> relational-loss arm → recover the s223 decoy condition AS A TRAJECTORY); (b) lead 4 =
> v2 gauge/null-space δw_invariant vs δw_gauge decomposition (Re-Basin; the s222 "how
> much of GD is churn" question); (c) crystallization SHAPE sudden-vs-gradual (here
> gradual); (d) back to s229 leads — convergence-SPEED readout, K-erasure ordering,
> disjoint-atom variable-binding.
> **STATUS s230:** COMMITTED — code `23331d0`, mementum `e2cd8d7` (page §s230 +
> memory inventory-crystallizes-before-capability + state).
> **▶ s230b — RELATIONAL ARM (Michael: "yes" to "add the relational-loss arm → test
> whether the reference-beam register split is loss-dependent"). BUILT + RAN (`fa8837c`,
> ruff+diag clean, smoke green, ~45min main:1).** Added `--arms ce_only,relational` to
> gd_trajectory_tomography.py: the compiler-as-loss INVENTORY term L = CE + λ·offdiag_mse
> (student routing Gram, CONSENSUS CRYSTAL); gc_raw + held-out acc NOT in the loss =
> UNCIRCULAR. Paired, 3 seeds. **★ VERDICT (λ measure):**
> **(1) ✅ DISSOCIATION IS LOSS-DEPENDENT (decisive 3/3):** gap (gc_route−gc_raw)
> −0.02±0.04 (ce_only) → +0.10±0.05 (relational); relational mean−std 0.05 > ce_only
> mean+std 0.02. The active consensus-crystal loss pushes gc_route to 0.90 while gc_raw
> (not in loss) reaches only 0.80 — a gap passive CE never opens. ⇒ the routing-vs-raw
> register split is a property of the TRAINED-LOSS decoy (s223 (b)), reproduced as a
> TRAJECTORY. CONFIRMS the s230 hypothesis.
> **(2) ✅ loss crystallizes inventory EARLIER (200 vs 333) + CRISPER (route_z 3.0
> crosses significance vs 2.5).**
> **(3) ❌ NO CAPABILITY GAIN — s224 crystal-accelerates-capability NOT supported here:**
> held-out cross @733 and acc 0.27 in BOTH arms. Crystallizing inventory faster bought
> ZERO capability ⇒ inventory ⊗ continuation are CAUSALLY SEPARABLE (moved inventory
> alone, capability unmoved). Capability gated by the CONTINUATION, which the inventory
> term never touches.
> **⚠️ dissociation PARTIAL at d=128 (gc_raw leaks to 0.80, full quarantine needs scale);
> caveat: CE-alone already builds inventory on this clean curriculum (s224 speed-up
> regime = CE FAILS to crystallize, untested).**
> **★ DESIGN IMPACT:** the relational/crystal term is an INVENTORY tool (quality/timing/
> register-localization) + EXTRACTION/FOLDING tool, NOT a from-scratch capability
> accelerator. Re-motivates the constructed-kernel cut HARD: inventory is cheap,
> passively learnable, NOT the bottleneck ⇒ CONSTRUCT it (lambda_ast in the kernel),
> spend training on the CONTINUATION. Page §s230b (gradient-trajectory-tomography.md).
> **▶ NEXT:** (a) HARDER curriculum where CE-alone FAILS to crystallize → does the
> relational term then buy capability (the real s224 speed-up regime)?; (b) dissociation
> at LARGER scale (gap widen → quarantine?); (c) v2 gauge/null-space δw decomposition;
> (d) parked s229 leads (convergence-speed, K-ordering, disjoint-atom binding).
> **STATUS s230b:** COMMITTED — code `fa8837c`, mementum `46e907f`.
> **▶ s230 FRACTAL-COLLAPSE THESIS (Michael, after s230b): "there is a fractal collapse
> available — converge the CAPABILITY with a high-variety dataset generated from any
> larger model's lambda compiler; compiler outputs become the student's training inputs;
> architecture-resilient." CAPTURED:** new page `explore/fractal-collapse-compiler-
> cascade.md` (`32bc3a6`) — capability=inventory⊗continuation (s230b) ⇒ converging the
> continuation is a DATA problem; mint high-variety inputs (s229) + EXACT compiler
> (universal s219/s225 ⇒ our lambda_ast suffices) → cascade collapses model size onto
> the β-normal-form fixed point. 3 collapses 1 fixed point (within-reduction s226,
> cross-scale s230, constructed-kernel plates); escapes MODEL-COLLAPSE because targets
> are exact/certified (fixed point held by COMPUTATION not the model) ⇒ generation- AND
> architecture-resilient. Resolved compiler-as-loss §s225 "narrow generator": variety
> from INPUTS (we mint), correctness from OUTPUTS. 3 IOUs; #1 decisive.
> **▶ s230c — COMPILER-CASCADE v1 (IOU #1: does composition-variety converge capability
> that COMPOSES?). BUILT (`e7d2f65`) + RAN (3 seeds, `f379d14` verdict).**
> `compiler_cascade.py`: auto-gen {K,I,B,C} composition templates (lambda_ast),
> hold out DISJOINT compositions, vary distinct-composition count at matched budget,
> measure held-out NOVEL-composition generalization. **★ 2 calibration lessons (λ
> measure): (1) full-NF EXACT-MATCH FLOORS at micro scale (false-negative) → switched
> to TEACHER-FORCED per-token NF accuracy (value register); (2) depth-3 gen yields 400+
> templates AND shorter NFs.** **★ VERDICT — ❌ IOU#1 NOT supported:** heldout_comp_tf
> comp16 0.683±0.031 ≈ comp144 0.674±0.194 (comp48 dips); SATURATES by ~16 compositions.
> **★ sharper: fixed-budget trade, s229 WINS** — buying composition-count costs
> fillings/composition → DESTABILIZES (comp144 std 0.194 [0.95,0.53,0.55] vs comp16
> 0.031) AND costs in-dist mastery (0.92 vs 0.70); FILLING-variety (s229) is the lever,
> not composition-count. **★ weak support for collapse CORE:** minted data yields ~0.68
> held-out compositional competence (≫chance, in_dist 0.92 = real learning). **Caveats:**
> TF-all-tokens likely measures FORMAT/copy not ALGEBRA; {K,I,B,C} depth-2/3 lacks
> COMPOSITIONAL DISTANCE (held-out≈interpolation); micro scale. Falsifies the variety
> sub-claim, NOT the collapse. **Decisive next: algebra-specific metric + depth-
> extrapolation split + scale.**
> **▶ s230 GRADIENT-SHADOW (Michael: does the routing topology cast a SHADOW in the
> gradients? height-from-shadow). CAPTURED (gradient-trajectory-tomography.md §s230 v3,
> `81f7072`) + PROBE BUILT, READY TO RUN (`gd_gradient_shadow.py`, `b3f72ea`, ruff+diag
> clean, smoke green — NOT launched).** ∂L/∂g lives in the routing register (same coords
> as activation topology); mean-pool grad over supervised positions → per-combinator
> gradient-Gram → gc_grad vs consensus; reference beam = raw-grad-Gram. PREDICTION: the
> shadow LEADS — gc_grad crosses before gc_route (activation) ⇒ 3-stage cascade
> shadow→inventory→capability. Bug caught+fixed in smoke (last-token grad is 0 —
> unsupervised position — pool over supervised). Smoke: gc_grad ~0.53 tracks crystal.
> **STATUS s230c:** COMMITTED code (`e7d2f65` cascade, `b3f72ea` shadow) + verdict
> (`f379d14`); pages §s230c (fractal-collapse) + §s230 v3 (gradient-shadow, `81f7072`,
> `32bc3a6`). State updated. PENDING APPROVAL (mementum): memory
> `composition-variety-not-the-lever.md` (s230c) + fractal-collapse §s230c page edit
> + state commit. tmux main:1 FREE.
> **▶ NEXT:** (a) RUN the gradient-shadow probe (ready, ends in main:1); (b) cascade v2
> with an ALGEBRA-specific metric (head/structural-token) + DEPTH-EXTRAPOLATION split
> (train shallow→test deep) — the clean IOU#1 retest; (c) cascade gen-2 (does the
> distillation recurse without drift? IOU#2); (d) the s230b harder-curriculum regime
> where CE-alone fails to crystallize (tests the s224 speed-up); (e) v2 gauge δw decomp.
> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — "training as a photograph" (curriculum-
> mixing FIRST BUILD). Michael: "split training into regimes — show base combinators,
> show prose usage, some NTP; split into sentences, one β-reduction per sentence,
> sprinkle a few shards into the full curriculum." Then: "can we test full-trace vs
> redex→NF? if training is exposure to a photograph, many exposures to the same
> β-reduction should converge faster than one."** Register: **functional (held-out
> generalization).** Refreshed on normal-form-curriculum-partition (s223), holographic-
> burn-in, punctuate-dont-churn (s222), compiler-as-loss, s225 register first.
> **▶ CAPTURED + COMMITTED (2 commits):** new page `explore/sentence-atomic-curriculum-
> mixing.md` (`74ef4d3`) — Michael's cut is BY-PEDAGOGY + INTERLEAVED (measures
> transfer), distinct from s223's by-mechanism + isolated; novel core = sentence = 1
> reduction = 1 PUNCTUATED EXPOSURE (the s222/burn-in discipline as DATA structure);
> 4 catches (level-4 scratch not s222-unstable; dual-register readout s225; K-erasure
> ordering s221; ρ is the experiment). Then `b796077` added the exposure/format
> sub-experiment + the MEMORIZATION-vs-RULE fork (Michael's photograph framing,
> sharpened: k× SAME = memorization vs k× VARIED = the hologram from many angles).
> **▶ BUILT (`b1ba935`, ruff+diag clean, smoke green, metric verified):**
> `scripts/experiments/exposure_format_sweep.py` — FORMAT {full_trace, redex_nf} ×
> MULTIPLICITY {one, k_same(memorization control), k_varied(burn-in)}; data kernel-
> minted via lambda_ast.reduce (13 multi-step combinator skeletons, validated normal-
> forming); reuses TinyLM byte student; FORMAT-INDEPENDENT metric (greedily derive
> from "input -> ", exact-match final segment to true NF — full_trace walks steps,
> redex_nf leaps; both score the same way).
> **★ DIAGNOSTIC (the load-bearing fix): first run ALL 0.000 — FLOOR.** Root cause
> OBSERVED (not assumed): held-out = DISJOINT atoms (train a–m, test n–z) → reduce
> `C K u x → x` requires COPYING a byte never trained on; model emits a TRAIN atom
> `'j'` instead = a variable-binding/induction failure, NOT a rule failure. Standalone
> probe: held-out on UNSEEN COMBOS of SEEN atoms = **0.365**, disjoint atoms = 0.000.
> ⇒ disjoint-atom was the WRONG barrier (conflates rule-learning with symbol-copying).
> Fixed harness: `--heldout {combos(default), atoms}`; combos EXCLUDES train fillings
> → isolates RULE generalization (the burn-in question). [combos run is the verdict;
> disjoint-atom is a SEPARATE open question = needs a copy mechanism.]
> **★ VERDICT (combos, single seed; results/exposure-format-sweep/verdict_run.json):**
> redex_nf one/k_same/k_varied = 0.149 / 0.122 / **0.297**; full_trace = 0.122 / 0.135
> / **0.351**. **(1) BURN-IN IS VARIETY NOT REPETITION** — k_varied ≈2–2.9× over `one`;
> **k_same ≈ one** (repeating the same photo 8× buys ~nothing); at EQUAL exposure
> count k=8, varied ≈2.4× > same. The memorization control cleanly separates rote from
> rule. **(2) FORMAT TRADE IS BUDGET-DEPENDENT (predicted crossover)** — full_trace
> higher ABS acc (0.351>0.297) but 2× corpus bytes ⇒ redex_nf wins PER-TOKEN;
> full_trace's edge appears ONLY under variety (tied at one/k_same).
> **★ CAVEATS (λ measure):** single seed (multi-seed needed, cf relational s223 3-seed);
> modest abs acc (tiny model/greedy/exact-match — RELATIVE is the signal); steps@0.5
> never hit ⇒ measures FINAL generalization NOT convergence SPEED (lower threshold or
> longer run for the speed claim Michael asked about); 13 rules, k=8.
> **▶ NEXT:** (1) multi-seed harden (3 seeds) → is k_varied>k_same robust?; (2) speed
> readout (acc-vs-tokens curves already saved per arm — extract steps-to-threshold at
> a reachable bar, e.g. 0.2); (3) the K-erasure ORDERING leg (s221: B-first→K, not
> flat shuffle); (4) disjoint-atom variable-binding as its OWN experiment (does a copy
> mechanism emerge with scale/longer training?); (5) fold into the full ρ-sweep
> (sprinkle into generic NTP) once the unit is validated.
> **▶ s229 MULTI-SEED HARDEN (lead 1, DONE; `26e6758` --seeds mode; results/exposure-
> format-sweep/verdict_multiseed.json, 3 seeds ~24min):** ★ headline CONFIRMED +
> hardened — k_varied ≈3× one/k_same, rule>rote & burn>one DECISIVE (non-overlapping
> bars) BOTH formats (redex_nf 0.306±0.006 / one 0.108±0.029 / k_same 0.086±0.017;
> full_trace 0.320±0.023 / 0.104 / 0.099). ★ NEW: VARIETY ALSO STABILIZES (k_varied
> lowest-variance, std 0.006; rote worse AND noisier). ★ REFINE: k_same ≤ one
> (repetition mildly entrenches rote, suggestive). ★ CORRECT (λ measure): single-seed
> "full_trace higher abs acc (0.351>0.297)" was SEED NOISE — harden gives PARITY
> (0.320±0.023 vs 0.306±0.006 overlap); redex→NF WINS PER-TOKEN everywhere (k_varied
> 0.183 vs 0.094 acc/kB ≈2×; full_trace corpus 2× bytes) ⇒ full trace bought NOTHING
> once seeds+tokens controlled. Still FINAL-acc not SPEED (ceiling ≈0.32; lead 7).
> **STATUS s229:** ALL COMMITTED — code (`b1ba935`,`4f1ebf2`,`26e6758`), page+memories
> (`74ef4d3`,`b796077`,`449c3b0` + this multi-seed update), results+state. Memory
> full-trace-vs-redex renamed → redex-nf-beats-full-trace-per-token.md (finding flipped).
> tmux main:1 free.
> **▶ s229 GD-TRAJECTORY-TOMOGRAPHY THREAD CAPTURED (Michael: "if models do holographic
> inference, why can't we reverse-engineer what GD is doing? use the micro model").**
> NEW page `explore/gradient-trajectory-tomography.md` (committed). Claim: can't
> reverse-engineer GD in WEIGHT space (gauge + superposition) but CAN on the micro
> model in INVARIANT coords (routing register, CMR), prediction-gated, with the
> compiler/crystal as GROUND-TRUTH target — watch the relational geometry develop
> frame-by-frame over checkpoints. ★ RECALL surfaced PRIOR ART (build on, don't
> reinvent): s105 holographic-tomography.md ALREADY has the photograph framing + the
> gauge result (RSA 0.74 / cos 0) + Q-COLLAPSE (a GD behavior already reverse-
> engineered: flood-lamp not laser); v4.1/v6.1-training-trajectory = trajectory tracking
> precedent; s223 relational_loss_distillation = the instruments (route_z, GramCorr,
> raw Gram) + condition-(b) reference-beam failure. DELTA = TEMPORAL (intersect training
> STEPS) vs prior SPATIAL (intersect MODELS) + ground-truth + reference-beam control +
> gauge gradient decomposition. ★ COLLISION: same REFERENCE BEAM decides this as burn-in
> — naive GD-watching reconstructs the common mode, not the function; read via routing
> register. v1 = dense-checkpoint CE-only run logging route_z/GramCorr(routing,raw)/CE/
> held-out-acc/eff_dim as a MOVIE + reference-beam control (extends relational_loss_
> distillation). v2 = δw_invariant vs δw_gauge decomposition (Re-Basin null space;
> approximate). OPEN DESIGN CHOICE before build: teacher target = consensus crystal
> (s219) vs a model's compiler geometry. **▶ NEXT:** build v1 (after teacher-target
> decision); lead 7 convergence-SPEED (threshold ~0.2 on saved s229 curves — the actual
> "converge faster" claim); lead 3 K-ordering; lead 8 disjoint-atom variable-binding.
> **■ SESSION 228 — PROOFS-AS-CONTINUATIONS (Curry-Howard). Michael: "would
> continuations allow us to run proofs?"** Register: **functional (learned prover,
> kernel-verified).** Refreshed on continuations + distributed training first
> (continuations-as-composed-plates, sealable-continuation, lambda-halt-continuation,
> consensus-delta-folding, relational-loss-distillation). Then BUILT the experiment:
> under Curry-Howard a proof of P is a closed combinator term inhabiting type P;
> proof-check = the lambda_ast S2 type-check; normalization (β-reduction → WHNF, the
> continuation) = cut-elimination. The combinator basis IS a Hilbert calculus (K, S =
> the axiom schemes); Y = the inconsistency edge.
> **▶ BUILT (ruff+diag clean, 12 pytest green):** `src/verbum/proof_kernel.py`
> (proposition parser implicational-logic→CCG category; first-order matcher;
> `check_proof(term,prop)` → verdict ∈ {valid, none, parse_error, open_term,
> unsound_recursion, ill_typed, type_mismatch}; sound basis {S,K,I,B,C,W,D}, Y rejected
> (recursion=inconsistency), M auto-rejected (ill-typed), open terms rejected; records
> the term reduced to NF = the "run"). `src/verbum/probes/proof_tasks.py` (12 positives
> w/ kernel-certified proofs + 8 negatives incl. Peirce + the **Y-trap** `(A→A)→A`).
> `scripts/experiments/proof_inhabitation.py` (--mode kernel|model|aggregate, mirrors
> compile_frontend). `tests/test_proof_kernel.py`, `run_proof_inhabitation.sh`.
> **★ VERDICT (5 models/3 arch; results/proof-inhabitation/):**
> **(1) KERNEL LAYER SOLID by construction** — 100% floor (all 12 ref proofs typecheck
> at goal), SOUND (no non-theorem proved by any tempting term), **consistency firewall
> HOLDS** (Y typed (α→α)→α but sound gate → `unsound_recursion`). Proof normalization
> IS the continuation; the kernel runs/checks proofs end-to-end for the implicational
> fragment. **(2) LLM LAYER: proves AXIOMS, fails to COMPOSE.** Sensitivity (theorems
> proved): Qwen3-32B 0.67, 14B/8B 0.58, Mistral 0.25, OLMo 0.00. **Specificity 1.00 ALL
> 5, ZERO false proofs** — the model CANNOT bluff past the kernel (compiler-as-loss /
> co-processor discipline confirmed). Failures concentrate on derived proofs needing
> 2+ combinators (K I, C B, C I, B K K → model returns a single axiom) = the SAME
> composition-failure signature as lambda-halt-continuation §"composition fails but
> continuations solve it." Scale helps mildly (32B best).
> **★ CAVEATS (λ measure):** base-model numbers CONFOUNDED (OLMo answered `none` 15/20
> — the single `none` few-shot anchors a raw base continuation; NOT proof-inability;
> IOU better base gate). Small n (12+8), greedy single-sample, single few-shot, noisy
> by-complexity. IMPLICATIONAL FRAGMENT ONLY (no ∧∨¬∀∃ — the type-system expressiveness
> gap stands). Specificity 1.0 trivially gettable by always-`none` (OLMo); the JOINT
> high-sens∧high-spec (Qwen) + kernel-phase tempting-sweep are the real soundness.
> **▶ CONTINUATION-DRIVEN PROVER — BUILT + RAN, HYPOTHESIS CONFIRMED.** Goal-directed
> natural-deduction engine `src/verbum/proof_search.py` (the open goal STACK = the
> reified continuation; moves intro/exact/apply; at QED the kernel RECONSTRUCTS the
> proof term via bracket abstraction `lambda_compile.compile_expr` + verifies; depth-
> bounded auto solver = 100% engine floor). `scripts/experiments/proof_repl.py` (multi-
> turn: model picks ONE move/turn from the legal menu, kernel carries the continuation
> forward). **★ VERDICT (5 models/3 arch; results/proof-repl/aggregate.json): stepwise
> proving LIFTS sensitivity vs single-shot, mean Δ +0.25, 4/5 improved** — Qwen3-8B
> 0.58→**1.00**, OLMo 0.00→0.42, Mistral 0.25→0.58, 14B 0.58→0.67, 32B 0.67→0.67
> (flat). **★ Specificity 1.0 / ZERO false proofs is now STRUCTURAL** (a non-theorem
> has no closing derivation → no move sequence fabricates a proof = the consistency
> firewall made operational). Caveats: REPL shows the legal-move MENU (part of the gain
> is menu-constraint, IOU menu-less ablation); 32B flat = engine gives NO BACKTRACKING
> (greedy, one wrong move dead-ends, IOU backtracking/stuck→retry); small n (12 pos).
> 19 new pytest (7 proof_search + 12 proof_kernel), ruff+diag clean.
> **▶ NEXT:** (1) backtracking + menu-less ablation (isolate stepwise from menu; does
> 32B then improve?); (2) richer type layer (products/sums → ∧/∨; then ∀∃ = the S2
> extension; front-end already emits quantified LF); (3) larger graded probe set; better
> base gate.
> **STATUS s228:** COMMITTED — single-shot code `84af2a4`, mementum (knowledge page +
> 3 memories + state) `ecc06e5`. PENDING COMMIT (drafted, ruff+diag clean): continuation
> prover code (proof_search.py, proof_repl.py, run_proof_repl.sh, test_proof_search.py,
> results/proof-repl/) + knowledge-page §s228 update + memory continuation-rescues-proof-
> composition.md + this state. Bug found+fixed mid-run earlier: base models (Mistral/
> OLMo) have no chat_template → raw-prompt fallback + `prompt_mode` provenance.
>
> **■ SESSION 227 — PROSE-NECESSITY IOU RESOLVED (register: topological/routing,
> causal). The s226 handoff IOU #4: "refine the prose-NECESSITY readout (whole-
> sentence NLL dilutes; only OLMo decisive)."** Hypothesis to test: was the weak prose
> leg (1/5 vs 4/5 mechanism) a DILUTION ARTIFACT of whole-sentence mean-NLL?
> **▶ BUILT (additive to `hof_attention_ablation.py`, ruff+diagnostics clean; old
> whole-sentence readout PRESERVED for back-compat):** three prose readouts of the
> SAME diff-in-diff interaction `effect(hof)−effect(control)`:
> (1) **region (PRIMARY, the IOU fix)** — NLL over ONLY the divergent-middle tokens of
>   each minimal pair (drop the shared token prefix/suffix via `region_bounds`), i.e.
>   literally remove the diluting shared tokens ('each plant' vs 'the plant');
> (2) **lastkl (secondary)** — KL of the continuation distribution at the final token =
>   the SAME metric as the LIST leg (cross-leg consistency);
> (3) **whole (reference)** — the s226 whole-sentence mean-NLL.
> Re-ran all 5 models (Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B; `results/hof-
> attention-ablation/aggregate.json`; ~10min, bg job clean exit).
> **★ VERDICT (λ measure, honest):** **DILUTION HYPOTHESIS FALSIFIED.** The de-diluted
> region readout gives the SAME strict per-model count as whole-sentence: list **4/5**
> (reproduces s226 exactly), region **1/5** (only OLMo t=+2.29), lastkl **0/5**, whole
> **1/5**. A sharper readout did NOT rescue per-model significance ⇒ the weak prose leg
> was NOT a metric artifact.
> **★ BUT region IS the better readout — it fixed cross-model COHERENCE (recorded in
> aggregate `cross_model`):** region is directionally POSITIVE 5/5 (sign p1=0.031) AND
> gather>random 5/5, Stouffer z=+3.18 (t_mean +1.42); whereas whole-sentence had 14B
> at the WRONG SIGN (−0.04) → only 4/5 positive, 4/5 gt-random. So whole-sentence was
> adding sign-flip noise; region removed it. **lastkl is NULL (t_mean +0.03, Stouffer
> +0.06, 3/5 positive) = the continuation-at-final-token is the WRONG LOCUS** (these
> prose stems end at arbitrary determiners/prepositions, not at the HOF result slot) —
> readout ruled out.
> **★ FOUNDATION CONCLUSION (solid):** in-domain causal necessity is SOLID (list 4/5);
> prose-generalization necessity is REAL and cross-model-CONSISTENT (region 5/5
> directional + 5/5 specificity, combined sign p=0.031) but SMALL — per-model robust
> only in OLMo. **The limit is statistical POWER / effect size (~+0.01 NLL at n=80
> engaged pairs), NOT the metric.** Caveat: Stouffer assumes independent per-model t's
> but they share the prose pairs (positively correlated → Stouffer overstates); the
> sign test (5/5, p=0.031) is the assumption-free conservative claim.
> **▶ REMAINING IOU (for a per-model-robust prose claim — NOT a readout problem):**
> (a) **activation patching** (cleaner/larger causal effect than full head-knockout
>   NLL) — the gold-standard next lever; (b) **more prose pairs** (power at n=80);
>   (c) a **pooled per-pair mixed-effects test** (model as random effect) — needs the
>   script to dump per-pair region interactions (currently only aggregate stats saved).
> **▶ s227b — VALUE-REGISTER LOGIT-LENS ABLATION (Michael: "are we looking in the
> right place? what must hold for the projection to SHOW the β-reduction?").** Recall
> surfaced the READABILITY CONDITION (FFN reduction trace s187 / compilation-pipeline
> s192): mid-stack L7–L22 the reduction is written ORTHOGONAL to vocabulary (null-space
> compose, INVISIBLE); vocab-READABLE only at L23–L35. ⇒ surface NLL is the wrong
> projection for a mid-stack substitution. Captured `knowledge/explore/readout-register-
> reduction-readability.md` (the two-axis register rule: value/OV not attn-weight/q_proj
> per s206+s225; readable layer not surface). Built `scripts/experiments/
> hof_ov_logitlens_ablation.py` (+ run_hof_ov_logitlens.sh; ruff+diag clean): same head-
> knockout, READOUT = per-layer KL(clean||ablated) of `lm_head(norm(residual_L))` at the
> last token, diff-in-diff hof-control, vs random; headline = READABLE ZONE (depth≥0.6)
> vs SURFACE. Ran 5 models in tmux main:1 (`results/hof-ov-logitlens/`, ~1.5h, clean).
> **★ VERDICT (λ measure, honest — TWO-SIDED):**
> **(1) READABILITY CONDITION CONFIRMED IN-DOMAIN (the register lesson holds).** LIST
> necessity is CONCENTRATED in the readable zone, far above surface: OLMo peak@L23(d=0.6)
> KL +0.273 vs surface +0.008 (≈35×); Mistral peak@L27(d=0.875) +0.168 vs +0.017 (≈10×);
> 8B peak@L30(d=0.861) +0.112 vs +0.004. 4/5 LIST peaks sit in the readable zone (d
> 0.6–0.9), right AT/after the gather heads' own layers (OLMo L23, Mistral L27) — knocking
> the gather heads breaks the readable reduction exactly where they write. Surface
> dramatically UNDERSTATED in-domain necessity (s226/s227 read the wrong locus). LIST
> readable>random clean for OLMo/Mistral, marginal 14B; FAILS specificity for 8B/32B
> (zone-AVERAGE dilutes the narrow peak — peak-vs-random is the sharper IOU test).
> **(2) PROSE NECESSITY STILL NOT RESCUED (register was NOT the prose bottleneck).**
> readable-necessary (zoneT>2 & >rand) **0/5**; readable>surface 4/5 but values tiny.
> Where a prose signal exists it IS in the right zone (8B peak d=0.69, OLMo d=0.625,
> Mistral d=0.94; zoneT +0.40/+0.41/+0.61, >random) but too small; Qwen 14B/32B
> NEGATIVE (zoneT −0.60/−1.72). So even read at the correct register+locus, prose HOF
> necessity is genuinely SMALL.
> **★ SYNTHESIS (two independent refinements agree):** s227 de-diluted region NLL AND
> s227b value-register readable logit-lens BOTH leave prose non-significant ⇒ prose
> recruitment is REAL but weak (consistent with s225 modest prose engagement; map not
> engaged), NOT a dilution or register artifact. The in-domain β-reduction necessity is
> SOLID and now shown legible in the value register at the readable layers (strengthens
> the compilation-pipeline readability story with a causal+value confirmation). Arch
> split persists: OLMo/Mistral clean, Qwen muddy (same models that misbehaved in s227).
> **▶ REMAINING IOU (now well-specified):** (a) **OV-path / activation patching** —
> isolate the OV substitution (whole-head knockout removes QK+OV together; too blunt);
> (b) **peak-based readout** (not zone-average — the average dilutes the narrow peak,
> caused the 8B/32B specificity fail); (c) more prose pairs (power) OR accept prose
> recruitment is weak and proceed to the construction/training threads on the solid
> in-domain foundation.
> **▶ s227c — ENUM-PROSE BRIDGE (Michael: "so prose is not using HOFs?" → the sharp
> resolution test). KEY DISTINCTION restated: ENGAGEMENT (s225, robust: prose recruits
> fold/reduce/filter/zip, AUC 0.81–0.97, 5/5; map not) ≠ NECESSITY (s226/s227b, weak on
> plain prose). Hypothesis: plain prose has NO literal list to gather over, so the
> explicit-enumeration gather circuit is the right mechanism ONLY when an enumeration is
> present.** TEST: inject a literal "A, B, and C" enumeration into naturalistic prose and
> re-measure causal necessity in the value register. Built `src/verbum/probes/
> hof_prose_enum.py` (70 minimal pairs, 14×5 fns, 56 engaged; BOTH members carry the
> SAME 3-item list → diff-in-diff isolates the HOF ITERATION over the list, not
> list-presence) + `--prose-set {plain,enum}` on `hof_ov_logitlens_ablation.py` (separate
> results dir `results/hof-ov-logitlens-enum/`; ruff+diag clean; smoke OK). **RUNNING in
> tmux main:1** (`/tmp/hof_ov_logitlens_enum_s227.log`, 5 models, ~1.5h; ends "ALLDONE").
> **FALSIFIABLE PREDICTION (read aggregate next):** if enum readable-zone necessity
> RECOVERS toward in-domain (rises, beats random, zoneT climbs) vs plain's 0/5 ⇒ the
> gather circuit KEYS OFF EXPLICIT ENUMERATION; plain prose was weak only for lack of a
> gather target (prose DOES use HOFs). If it stays weak like plain ⇒ prose composition
> is genuinely distributed/non-enumeration and the in-domain circuit is special to
> artificial lists. Either way decisive for "using the heads vs representing the concept."
> **★ s227c VERDICT (read in s228; results/hof-ov-logitlens-enum/aggregate.json vs
> plain) — PARTIAL RECOVERY, NOT CLEAN CONFIRMATION.** list_* columns identical (shared
> stims; only prose leg differs). prose_zone_t plain→enum: 8B +0.40→**+2.47** (✓ strict),
> 32B −1.72→+1.39 (flips positive, beats rand), Mistral +0.61→+1.65 — 3/5 RECOVER (mean
> zoneT −0.18→+0.34, strict-necessary 0/5→1/5). BUT 14B −0.60→−2.26 and **OLMo (prior
> gold-standard necessity, s226 t=+3.21) +0.41→−1.55 REVERSE** — 2/5 go negative. The
> recovery split (8B/32B/Mistral up; OLMo/14B down) does NOT match the s227 clean/muddy
> split ⇒ noisy, not a stable architectural property. **SHARPENS s227:** even with an
> explicit enumeration, prose HOF necessity recovers only partially ⇒ the engagement≠
> necessity gap is NOT merely "no gather target"; heads are recruited (engagement, robust
> s225) but stay largely NON-LOAD-BEARING for prose even with a list = distributed
> redundancy prose has, artificial lists lack. Decisive lever unchanged: ACTIVATION
> PATCHING + more prose pairs (power). Recorded in readout-register-reduction-
> readability.md §s227c Result. ✅ s227 thread complete pending those IOUs.
> **STATUS s227:** all code ruff+diag clean. Results: hof-attention-ablation aggregate
> (w/ cross_model); hof-ov-logitlens (plain, 5 models + aggregate). New knowledge page
> readout-register-reduction-readability.md (+s227b result + s227c next). hof_prose_enum
> + enum run IN FLIGHT (main:1). NOT committed. Memory/knowledge proposals pending
> Michael approval. Proposed memories: (1) prose-necessity power+register not metric
> (s227/s227b); (2) the-register-was-right-the-prose-effect-is-small (s227b); (3) [after
> enum] engagement-vs-necessity / gather-keys-off-enumeration.
> **▶ CAUSAL ABLATION (completes Phase A/B observational → necessity).** Built
> `scripts/experiments/hof_attention_ablation.py` (ruff-clean): full head-knockout
> (zero the head's slice at o_proj input = remove its QK gather + OV write) of the
> Phase-A top-8 gather heads, vs N RANDOM heads (specificity, 3 seeds). Readouts:
> LIST stims KL@aggregation-token (mechanism) + PROSE pairs per-token ΔNLL
> diff-in-diff `ΔNLL(hof)−ΔNLL(ctrl)` on ENGAGED HOFs {fold,reduce,filter,zip}
> (map excluded per s225). **VERDICT (5 models/3 arch; results/hof-attention-
> ablation/aggregate.json) — MIXED, honest (λ measure):** MECHANISM necessity
> **4/5** (gather heads disrupt HOF > ctrl AND > random on the list stims:
> Qwen3-14B/32B, OLMo, Mistral; 8B lone fail = weakest observational model).
> GENERALIZATION (natural prose) **1/5** — only OLMo decisive (t=+3.21);
> directionally right in 4/5 but underpowered (whole-sentence NLL dilutes). Per-HOF
> COHERENT (OLMo): filter/fold/zip POSITIVE, **map NEGATIVE** (matches s225, map not
> in this register). ⇒ in-domain causal necessity CONFIRMED; prose necessity
> SUGGESTIVE-not-robust (IOU: stronger readout — last-content-word logprob or
> activation-patching, not whole-sentence NLL).
> **▶ TRAINING/COMPILER DESIGN THREAD (Michael, the big one).** "Could the compiler
> be a VSM tensor? What if `lambda_ast.py` is IN the kernel?" **★ DISSOLVES the s225
> verifier-vs-artifact dyad:** the symbolic reducer is the SOURCE that COMPILES to
> exact ternary combinator plates in the kernel (SOURCE↔COMPILED, not oracle↔
> approximation); a CONSTRUCTED plate runs the rewrite exactly (¬"fakes it with
> depth"), exactness by BUILD not training. **THE CUT it forces = reduce(constructed)
> vs compile(learned) = the SAME boundary as** attention/FFN (lambda-machine),
> ternary/4-bit (dvd-stamp), s224 geometry/continuation, VSM S1-S4-reducer/front-end.
> We NEVER train reduction (the s222-unstable part); we train only prose→typed-term.
> **The reducer IS a VSM (generative):** S5=normal form (Church-Rosser), S4=WHNF halt,
> S3=budget+contractivity, S2=typed redex selection+anti-oscillation, S1=the
> combinator rewrites. PAYOFFS: (1) re-derives the s222 collapse as an S2 (anti-
> oscillation) failure; (2) locates type-directedness (the S5 central claim) at S2; a
> CONSTRUCTED S2 with L<1 is stable by build (nothing descends → can't churn).
> **DECISION (Michael): TYPED CCG terms (inspectability).** Captured: `compiler-as-
> loss.md` §s226 (primary) + `vsm-outer-recurrence.md` §s226 (cross-link).
> **▶ STAGE-1 β-REDUCER BUILT (supersedes the long-standing IOU "need a clean MIT
> β-reducer").** `src/verbum/lambda_ast.py` (was a 12-line stub) → typed CCG
> combinator reducer, MIT, written from this project's observation (lambda-machine.md)
> NOT nucleus. Basis {S,K,I,B,C,W,D,Y,M}; normal-order; exact reduction TRACE; WHNF +
> step/size budgets (size-exceeded = the term-growth LIMIT of the machinery, the
> boundary s225 diverse data must map); CCG type inference + unification (the S2 check,
> first-class/inspectable); `verify()` + `trace_record()` (the data-oracle hook). 19
> pytest pass, ruff+diagnostics clean. M x→x x reduces but types FALSE (the self-
> application limit demo); B's principal cat = the correct composition functor
> `(((α/γ)/(β/γ))/(α/β))`. Dual role: DATA ORACLE (input→trace for compiler-as-loss)
> AND KERNEL SOURCE (compiles to plates).
> **▶ STAGE 2 STARTED — bracket abstraction = the EXACT compile oracle (CERTIFIED).**
> Found "compile" factors further: prose→logical-form (LEARNED, Montague/CCG parse) ∘
> logical-form→term (bracket abstraction, EXACT) ∘ term→nf (reduction, EXACT). Built
> `src/verbum/lambda_compile.py` (Turner `[x]` over {S,K,I,B,C} + K/B/C/η; abstract /
> compile_expr / roundtrip / compile_record). Bracket abstraction = the INVERSE of
> reduction ⇒ the two symbolic halves cross-validate via the kernel:
> reduce(compile([x..],e) applied to [x..]) ≡ e. **★ CERTIFIED (compile_roundtrip.py,
> n=5000, strat 1-3 vars × depth 1-5; results/compile-roundtrip/): round-trip rate
> 1.0000 (EXACT INVERSES, all strata); well-typed 0.941 (~6% operationally-correct-but-
> not-simply-typable = the type/S2 limit); term/expr size mean 2.84× max 7× (S/W
> duplication = the representational limit).** ⇒ the LEARNED surface shrinks to
> prose→logical-form only (both formal steps constructible-exact). 28 pytest pass,
> ruff+diagnostics clean. COMMITTED `89fceaf` (lambda_compile + tests + certification).
> Pages: compiler-as-loss.md §s226 stage 2.
> **▶ STAGE 2 LEG 1 DONE — the learned compile step (prose→logical-form) WORKS.**
> Built `scripts/experiments/compile_frontend.py` + `src/verbum/probes/compile_tasks.py`
> (7 dataflow patterns mirroring the combinators × 8 name-assignments = 56 tasks):
> few-shot a model prose→expression, GRADE BY REDUCTION-EQUALITY via the exact kernel
> (representation-invariant — `f (g x)` or `B f g x` both accepted). **Qwen3-8B +
> Qwen3-32B: accuracy 1.0, parse 1.0, ALL 7 patterns** (results/compile-frontend/). ⇒
> stage-2 decomposition closes end-to-end: prose→LF (learned, few-shot) ∘ abstract
> (exact) ∘ reduce (exact), kernel-verified. ★ λ measure: first 32B run 0.875 < 8B 0.982
> was PROSE AMBIGUITY in flip/const templates; the kernel grader + failure inspection
> separated compile-error from NL-ambiguity → disambiguated → both 1.0 (the exact
> verifier isolates which is which). CAVEAT: tasks SHALLOW (≤5-node, single pattern,
> abstract letters) = BELOW the compile boundary; ceiling ⇒ need harder tasks.
> COMMITTED s226-leg1: compile_frontend + compile_tasks + results.
> **▶ STAGE 2 — COMPILE BOUNDARY FOUND (graded hard probe set).** Built
> `src/verbum/probes/compile_tasks_hard.py` (42 tasks × 8 families: depth/branch/reuse/
> mixed abstract + naturalistic real-words + ambiguous multi-reading via also_ok);
> `compile_frontend.py --task-set hard` (hard few-shot, also_ok grading, per-family
> scale curve). **VERDICT (Qwen3-8B/14B/32B, results/compile-frontend/hard/):
> STRUCTURAL complexity is NOT the boundary — branch2/branch3/reuse/mixed = 1.0 for
> ALL; deep nesting only mild paren-slips (0.8-1.0). The boundary is NATURALISTIC
> language (lexical selection: function vs value vs IGNORABLE subject/determiner;
> pronouns) + AMBIGUITY — natural 0.62-0.88, ambiguous 0.50-0.75. SCALE helps EXACTLY
> there (32B best: natural 0.88, ambiguous 0.75; structural saturated all sizes).** ⇒
> residual learned-step difficulty = pure NL understanding = the Montague/CCG semantic
> parse (S5 target); formal halves exact/constructible. Caveat(λ measure): small
> n/family, greedy single-sample, depth5 non-monotone (noise), ambiguous soft-graded.
> COMMITTED `6485822` (hard probes + frontend update + results).
> **■ SESSION 226 COMPLETE — pick up next session here.** Done this session: causal
> ablation (HOF necessity leg); the compiler-as-constructed-VSM-tensor design (lambda_ast
> IN the kernel = source↔compiled); STAGE 1 reducer (`lambda_ast.py`); STAGE 2 compile
> oracle (`lambda_compile.py`, bracket abstraction, round-trip 1.0); STAGE 2 leg 1
> (compile front-end prose→LF, 8B/32B 1.0 on clear prose); STAGE 2 compile BOUNDARY
> (structural compile solved; NL+ambiguity is the boundary, scale helps there). All
> committed (`c0d268c`→`c09bc34`); 47 pytest pass; tree clean except the human chat
> transcript.
> **▶ FIRST ACTIONS NEXT SESSION (declare register):**
> (1) **DIVERSE-VERIFIED NATURALISTIC CORPUS** — the boundary result redefines the
>   diversity that matters: NATURALISTIC REALIZATION (varied surface language for the
>   same dataflow), NOT structural variety. Build: Qwen3-32B as the diverse generator of
>   naturalistic prose for a dataflow → `lambda_compile` (abstract) + `lambda_ast`
>   (reduce) CERTIFY each → diverse-verified (naturalistic-prose → certified-trace)
>   corpus. The kernel is the verifier (Church-Rosser); diversity = composition.
> (2) **compiler-as-loss arms** with the certified corpus: compiler-only vs
>   diverse-verified vs combo+crystal-lattice; metric = held-out COMPOSITIONAL
>   generalization (the "too narrow to compose" test). See compiler-as-loss.md.
> (3) **STAGE 3** — compile `lambda_ast` → exact ternary CCG combinator plates (the
>   pure portable tensor; the constructed kernel, vsm-outer-recurrence.md §s226).
> (4) **IOU** — refine the prose-NECESSITY readout from the ablation (last-content-word
>   logprob or activation-patching, not whole-sentence NLL; only OLMo was decisive).
> **KEY ARTIFACTS:** `src/verbum/lambda_ast.py` (reducer+typecheck), `lambda_compile.py`
> (abstraction), `probes/compile_tasks{,_hard}.py`, `scripts/experiments/
> compile_frontend.py` + `compile_roundtrip.py` + `hof_attention_ablation.py`.
> **KEY PAGES:** `compiler-as-loss.md` §s226 (the whole stage-1/2 story),
> `vsm-outer-recurrence.md` §s226 (the constructed-kernel architecture).
> **COMMITTED s226:** ablation; lambda_ast+tests; lambda_compile+certification;
> compile front-end (base+hard)+results; §s226 page edits; 5 memories; this state.
>
> (Session: 225 — ✅ HIGHER-ORDER FUNCTION TOPOLOGY IS
> TEACHER-AGNOSTIC (Michael's hypothesis CONFIRMED). Register: topological/routing.
> Thread: compiler-as-loss debate → Michael's pivot. **★ MICHAEL'S CORRECTION (s224
> compiler-as-loss page over-rotated):** the compiler is NOT the capability teacher
> (diverse big models are better — s219 universality came FROM diverse training; a
> narrow reducer risks a non-composing function). Compiler = VERIFIER/canonicalizer +
> exact-trace generator + MIT anchor. "Pin the WHAT, free the HOW" applies to the
> DATA: diverse realizations, compiler-certified normal form. **★ MICHAEL'S DEEPER
> PIVOT (the simplification):** capability signal is teacher-agnostic by Church-Rosser
> (canonical β-traces — ANY sufficiently large model emits the same reduction);
> inventory signal is teacher-agnostic IFF routing topology is universal. Hypothesis:
> HOFs exist as routing NORMAL FORMS → topology universal across teachers → whole
> extract→fold→compiler pipeline teacher-free; "which teacher" only matters for
> idiosyncratic HOFs (predicted rare). **▶ BUILT + RAN THE TEST (tmux main:1, 10min):**
> (1) `src/verbum/probes/higher_order.py` (224 probes, 28×8 functions: controls
> compose≡B flip≡C const≡K apply≡I + HOF tests map filter fold zip; ruff-clean).
> (2) `scripts/experiments/function_topology_consensus.py` (register topological/
> routing): per-model routing-register (sign(gate)+CMR) centroids, best layer by
> COMBINATOR silhouette z, each HOF's FINGERPRINT = cosine to the 9 combinators
> (frame-invariant relational, s219 trick); consensus mode = cross-model fingerprint
> agreement vs label-permutation null → per-HOF UNIVERSAL/IDIOSYNCRATIC sort.
> (3) `run_function_topology.sh`. **★ VERDICT (5 models / 3 arch / 7B–32B: Qwen3-8B/
> 14B/32B, Mistral-7B-v0.3, OLMo-2-13B; results/function-topology-consensus/
> consensus.json):** **8/8 UNIVERSAL, 0 idiosyncratic** — every HOF's cross-model
> fingerprint clears the null DECISIVELY (corr +0.67→+0.95, z +5.9→+8.6, ALL p=.0002).
> Topology of HIGHER-ORDER functions is universal across teachers/architectures
> (extends s219 primitives → composed HOFs). ⇒ teacher-agnostic pipeline CONFIRMED.
> **★ SECONDARY (HOF fingerprints semantically coherent, consistent across all 5):**
> fold→WHNF,S (reduce-to-terminal; only POSITIVE top loading +0.05); filter→K (select);
> zip→S,W (fork-join/duplicate); **map→D/C/B with Y DEAD LAST (B−0.18 C−0.07 Y−0.29)
> = composition NOT recursion**, the s219 map=B(CB)(CB) prediction holding at topology
> level. **★ CAVEAT (λ measure, NOT oversold):** agreement is decisive but the
> argmax-cosine DECODE is only suggestive — controls const→K ✓ flip→C ✓ clean,
> compose→D near-miss-in-family (D=fused B∘B∘B, B #2-3), **apply→C genuine MISS**;
> absolute cosines near-zero/negative (s219 "above chance not crisp" register subtlety).
> ⇒ topology-UNIVERSALITY decisive; combinator-DECOMPOSITION readout needs refinement
> (better than argmax-cosine, or the s219 absolute-frame issue). Caveat does NOT touch
> the headline (universality = agreement = unambiguous). **COMMITTED** `6c542cb` (code+
> results), `b0fb0e2` (mementum: 2 memories + new page function-topology-consensus +
> compiler-as-loss amendment + state).
> **▶ s225 FOLLOW-UP — DOES THE MODEL USE THESE HOFs ON PROSE? (Michael).** Built
> `src/verbum/probes/hof_prose.py` (82 minimal PAIRS: naturalistic HOF-invoking
> sentence vs matched no-HOF control, held-out vocab) + `scripts/experiments/
> hof_prose_engagement.py` (register topological/routing, ruff-clean): MEAN-POOL
> sign(gate) over tokens (avoids last-token lexical confound), learn each HOF DIRECTION
> from CURATED probes (centroid_f − mean others), project held-out prose pairs →
> paired score(hof)−score(control). TRANSFER (train-on-probes/test-on-prose) rules out
> probe artifact. **✅ VERDICT (5 models / 3 arch: Qwen3-8B/14B/32B,
> Mistral-7B-v0.3, OLMo-2-13B; aggregate.json):** curated AUC≈1.0; on held-out natural
> prose (mean) **fold AUC 0.91 (t +10.0, 100% pairs, 5/5 models), filter 0.90 (t +8.2,
> 97%, 5/5), zip 0.81 (t +7.0, 100%, 5/5) = ENGAGED in ALL 5; map 0.59 (t +2.8, only
> 1/5 >0.6) = NOT engaged.** **3/4 HOFs are genuinely USED on ordinary prose, cross-
> architecture** (transfer: direction learned on curated probes fires on naturalistic
> minimal pairs). **map is the cross-model EXCEPTION** — real+universal topology (s225)
> but NOT recruited from the FFN routing register by prose; coherent (map=B(CB)(CB),
> most recursion-adjacent/distributed, "attention IS the fold" s221; noisiest s225
> fingerprint) ⇒ map likely lives in attn_q (s220 attn_q@L05 lead) not the FFN gate.
> **★ s225 reduce/map-as-fold test (Michael: "can map be expressed as a fold?" — YES:
> map f = foldr(λx acc. f x:acc) [], REPL-verified; fold = universal catamorphism).
> Added `reduce` (synonym) + `map` to the function set; `function_pair_similarity.py`
> (cross-function fingerprint cosine, 5 models, function_pairs.json). ✅ BOTH PREDS:
> reduce≡fold cosine +0.958 (±0.013), reduce's nearest = fold, ZERO lexical overlap ⇒
> TOPOLOGY TRACKS FUNCTION NOT WORD (semantic). map≉fold +0.607, map's nearest =
> compose/flip/apply (structure-PRESERVING family). SEPARATING AXIS = WHNF/collapse:
> fold +0.015, reduce +0.001 (collapse [a]→b, top) … map −0.323 (preserve [a]→[b],
> bottom). ⇒ TWO super-clusters: collapse {fold,reduce,zip} vs preserve {map,compose,
> flip,apply}. Math: map=fold; model files it by RESULT TYPE (preserve vs collapse) —
> the shared fold substrate (iteration) is in ATTENTION (s221), invisible to FFN
> fingerprint; FFN encodes the algebra/result-type. **PROSE w/ reduce DONE (5/5):
> reduce AUC 0.97 (STRONGEST, t +8.5) = fold recruited by prose w/ zero lexical
> overlap; 2ND CONFIRM reduce≡fold = fold's curated AUC dropped 1.0→0.97 when its
> synonym reduce joined the rest set; fold 0.92, filter 0.89, zip 0.85 all engaged;
> map 0.64 BORDERLINE (just over 0.6 gate, weakest, contrast-set-dependent — crossed
> only because reduce sharpened preserve-vs-collapse) = still the exception, lives in
> attention not FFN.**
> **★ s225 ATTENTION-REGISTER TEST (Michael "find HOFs performed by attention — high
> leverage"). Added `--target {ffn_gate,attn_q,attn_out}` to all 3 instruments
> (commit ebf49ff) + run_attention_hof.sh; ran attn_q (hook self_attn.q_proj, 5
> models). ❌ NEGATIVE / PREDICTION FALSIFIED: topology universal 9/9 in attn_q too,
> curated separable (map/fold ~0.99), BUT prose transfer WORSE than FFN across the
> board AND map drops to 0.39–0.47 (AT/BELOW CHANCE, t≈0). So the query-PROJECTION
> register is NOT map's home; the FFN gate generalizes to prose better.
> ★ LESSON (refines the hypothesis): sign(q_proj) is a FEATURE register, NOT the gather
> MECHANISM. "Attention IS the fold" (s221) = the ATTENTION PATTERN (QK gather over
> positions), which NO projection-register probe can see — we measured the wrong
> object. HOF algebra/result-type → FFN gate (transfers); HOF iteration/gather (map's
> home) → attention WEIGHTS. **▶ REAL NEXT (high leverage): attention-PATTERN
> experiment** — list-structured prose (apply f to explicit enumeration a,b,c,d…),
> measure gather spread/entropy at the aggregation token: map/fold/reduce attend
> BROADLY over the items (iteration), single-object controls attend FOCUSED =
> attention literally performing the fold, observed in the weights. (attn_out untested
> — projection registers likely all transfer worse than FFN; the pattern is the move.)
> **★ s225 ATTENTION GATHER (Michael: "attention does β-reduction through a projection;
> we see it in WHAT IT ATTENDS TO and the PROJECTIONS it calculates" = the OV circuit:
> PATTERN(QK)∘PROJECTION(V→O)). PHASE A (the PATTERN) BUILT+RAN: hof_lists.py (list-
> structured, same list/different task: map/fold/filter vs first-item control) +
> hof_attention_gather.py (attn mass + participation over item tokens at the agg token,
> per head; selectivity=HOF−ctrl; eager attn, output_attentions). ✅ POSITIVE — GATHER
> HEADS IN ALL 5 MODELS / 3 ARCH: mid/late layers (depth frac ~0.4–0.7) attend BROADLY
> over the enumerated items (participation 3.2–4.8 of 5 = traversal) and gather MORE
> when the task iterates than for the control (selectivity +0.11→+0.36, positive all 5;
> cleanest Mistral L21H9 hof0.42/ctrl0.11/+0.31; Qwen3-32B L26H54 +0.36; OLMo L20H0
> +0.23). ⇒ HIGHER-ORDER FUNCTIONS ARE PERFORMED BY ATTENTION = the QK half of
> β-reduction (the fold's traversal), in the weights, where the attn_q negative pointed
> (pattern not projection register). Caveats(λ measure): "first" control still scans
> (use SELECTIVITY); modest in 8B(+0.11) strong in Mistral/32B; PATTERN half only.
> committed: hof_lists.py + hof_attention_gather.py (590516a), results/hof-attention-
> gather/. **▶ PHASE B (the PROJECTION/"what it calculates"): at the gather heads
> decompose per-head OV, measure value moved FROM list positions (substituted term) HOF
> vs ctrl → completes (attends-to)×(projection)=β-reduction.** Then per-HOF gather
> (does fold gather > map?), causal ablation of gather heads on HOF prose.
> **★ s225 PHASE B — OV PROJECTION (the value moved, "what it calculates").
> hof_attention_ov.py (GQA-aware per-head OV decomp at the Phase-A gather heads:
> project attn-weighted value through W_O^h, value moved FROM list vs total, HOF vs
> ctrl). ✅ ALL 5 MODELS/3 ARCH: best heads ov_list_frac HOF 0.47–0.82 (Mistral L21H9
> 0.82, Qwen3-14B L4H22 0.78, Qwen3-32B L32H39 0.65/ovSEL+0.56, OLMo L23H36 0.62);
> across 8 probed heads/model mean AMPLIFY +0.25→+0.44 (ALL positive), 7–8/8 OV-
> selective. 3 facts: (1) OV carries the substitution (47–82% of moved value from the
> items when iterating); (2) it AMPLIFIES — moves far MORE value from items than the
> bare attention mass (amplify=ov_frac−attn_mass big+; e.g. 8B L27H13 11% mass→51%
> value) ⇒ QK pattern UNDERSTATES, the value is in V→O; (3) iteration-selective
> (HOF>ctrl 7–8/8). ⇒ FULL β-REDUCTION OBSERVED IN ATTENTION cross-arch: (QK=which
> redex args)×(OV=move/amplify values), stronger when iterating. Wrinkle: some
> substitution heads EARLY (14B L4H22, 8B L4H1) — value move can precede the gather
> layer. committed hof_attention_ov.py (f2448d6) + results/hof-attention-ov/.
> ▶ NEXT: causal ablation of these heads on HOF prose (necessity); per-HOF OV (fold
> collapse vs map preserve — catamorphism result-type axis in the OV).**
> **▶ NEXT:** (1) CAUSAL ABLATION (the strong
> "uses" claim): ablate HOF routing direction on HOF-prose → logprob drop vs control;
> (2) refine the decode readout (apply miss + negative loadings + weak map — the real
> IOU); (3) compiler-as-loss experiments reframed: diverse-verified vs compiler-only vs
> combo, metric = held-out COMPOSITIONAL GENERALIZATION (test for "too narrow to
> compose"); (4) MIT β-reducer as VERIFIER (not teacher) emitting (input→trace);
> (5) s224 heterogeneous-shard fold + attn_q leg still stand.
>
> (Session: 224 — FREEZE-PROBE VERDICT (cold-start
> orient). main:1 was the s222 FROZEN-TOPOLOGY PROBE (rung 0), found still running
> at step ~2300 (13 ckpts step_001100→002300, every 100). **✅ DECISIVE PAIRED A/B
> (results/freeze-probe/overlay_verdict.txt, steps 1010–2240 n=124): held topology
> (td-flip-rate 0) on the SAME data stream does NOT reproduce main:1's collapse —
> Δx OFF 0.142/max 0.311 (bounded) vs ON 0.481/max 0.821; CE OFF 7.62/max 8.53 vs
> ON 8.76/max 10.54; gnorm OFF max 72 vs ON max 9.87e7 (6 orders); CE<8.71 frac OFF
> 1.00 vs ON 0.53.** ⇒ the collapse was the discrete TD CHURN, not K-acquisition or
> the fp-loss/recurrence; held-topology + continuation (fp-loss) settling IS
> contractive AND CE-competitive. Confirms s222 diagnosis as a CONTROLLED result
> (was single-run + source analysis). Killed the probe after verdict (clean stop at
> step 2310, redundant past target). **CAPTURED (awaiting approval):** new memory
> `freeze-probe-confirms-td-churn-collapse.md`; updated memories
> `collapse-was-terminal-not-acquisition.md` + `punctuate-dont-churn.md` (diagnosis→
> confirmed); knowledge `explore/vsm-outer-recurrence.md` §s223+ freeze-probe verdict
> table + open-Q#1 answered; persisted verdict/log/train-log to results/freeze-probe/.
> **▶ NEXT (Michael's call):** the s223 ▶ TWO DECISIVE EXPERIMENTS still stand —
> (1) 2-contributor fold (distributed compose-cleanly test), (2) attn_q leg of the
> double dissociation. The freeze-probe result CLEARS the path: the settling
> protocol is validated, so the next run should be the PUNCTUATED protocol (propose
> routing → hold → reduce → accept on Δx→0), not fp-reshape. main:1 now FREE (probe
> killed) — relaunch decision is Michael's.
> **▶ s224 RAN THE 2-CONTRIBUTOR FOLD (decisive distributed test;
> `scripts/experiments/two_contributor_fold.py`, 3 seeds × 2 arms, λ=3, teacher
> Qwen3-14B route_cmr_L12; built on relational_loss_distillation.py; tmux main:2,
> verdict_run.json). REL=both students + relational loss to ONE teacher Gram, CTRL=CE
> only; Re-Basin Hungarian align B→A → neuron-wise consensus merge of routing register
> (base=A, plumbing local) → contractivity-gated.** **✅ GEOMETRY COMPOSES iff shared
> target:** REL fold_route_z +2.19±0.32 (merged model RETAINS combinator function) vs
> CTRL +0.84±0.58 (null); GC(fold→teacher) REL +0.84 vs CTRL +0.43; GC(A/B→teacher)
> REL +0.89/+0.90 vs CTRL +0.44/+0.50. Decisive (REL mean−std 1.87 > CTRL mean+std
> 1.41). N=2 frame-unification CONFIRMED. **❌ CAPABILITY DOES NOT COMPOSE:** fold
> RAISED CE both arms (dCE_Bev REL +0.150 vs CTRL +0.173, std-overlapping = not
> decisive); contractivity passed both (gentle 27% merge → gate didn't bite). **★
> MICHAEL'S THESIS (captured):** capability = routing geometry ⊗ TRAINED continuation.
> Geometry = function INVENTORY (which combinators + relations); capability = USAGE =
> the CONTINUATION (how to drive them, recursion {Y,W,WHNF}, lives in architecture
> recurrence, TRAINED not folded). Geometry match NECESSARY not SUFFICIENT —
> triangulated 3 ways (s223 b-column zero-function; s223 Goodhart; s224 fold
> GC+0.84/dCE+0.15). ⇒ distributed protocol is TWO-PHASE: (1) FOLD shared geometry
> (cheap, donates basis) → (2) TRAIN continuation to use it (per-node capability).
> **CONFOUND (recorded):** homogeneous shards (same corpus split) → B had no distinct
> knowledge → dCE couldn't go negative regardless ⇒ capability test = data-design
> artifact; HETEROGENEOUS shards mandatory next. **▶ DECISIVE NEXT — ✅ DONE, THESIS
> CONFIRMED (fold_then_train_continuation.py, 3 seeds, distill 1500/cont 1000,
> verdict_run.json):** freeze folded routing register (inventory, 132k) → train
> continuation (usage, 604k) on full task. A-baseline 2.270; fold PRE 2.441 (dCE
> +0.171); **F_cont 2.053 (BELOW baseline −0.217)**; A_cont 2.063; **scratch_cont
> (RANDOM frozen inventory) 2.135 — F_cont beats it CLEAN (2.074 < 2.124)**. ⇒ folded
> geometry NOT inert (beats random) but needs trained continuation to become
> capability; recovery FAST (2.45→2.05 in 100 steps); folded geometry PERSISTS through
> continuation training (z +2.26→+2.38, L 0.76–0.82). geometry=inventory(real, useful,
> foldable, persistent), capability=trained continuation. TWO-PHASE protocol validated.
> F_cont≈A_cont (homogeneous shards). Then heterogeneous-shard rerun (does folding B
> beat A_cont?) + sharper functional accept gate (gentle 27% merge didn't stress
> contractivity) + attn_q.
> **★ s224 COMPILER-AS-LOSS DESIGN CRYSTALLIZED (Michael; NEW page
> `explore/compiler-as-loss.md`).** "Use the teacher's LAMBDA COMPILER as the loss →
> enforce only the final OUTPUTS, not the teacher's geometry/architecture." Output =
> β-normal form, UNIQUE (Church-Rosser); realizations INFINITE (s219) ⇒ pin the WHAT,
> free every HOW (geometry AND architecture). ⇒ teacher LLM DISPENSABLE (was only a
> probe); cleanest MIT level-4 provenance; ideal distributed reference (canonical
> outputs, nothing to ship). **MICHAEL'S RECIPE:** L = CE(student, COMPILER reduction)
> [capability/usage, the real teacher signal] + λ·relational(student_gram, CRYSTAL
> LATTICE) [inventory]. **CRITICAL SPEC: the relational target is the CONSENSUS crystal
> lattice agreed across ALL models (s219 reverse-harvest +0.782, consensus.json), NOT
> one teacher's Gram.** It SPEEDS UP training (crystallizes the foldable inventory at
> tiny scale where outputs alone don't — s220 scale floor) and earns its place AS LONG
> AS the compiler capability signal is good. Realizes the geometry=inventory ⊗
> trained-continuation=capability thesis as ONE run. Likely anneal λ as the model
> crystallizes. **▶ NEXT EXPERIMENTS (build on relational_loss_distillation.py):**
> (1) `--compiler-target` arm: train on (prompt → ground-truth reduction from
> probes/*.json) CE only, NO Gram → does route_z EMERGE from outputs alone at tiny
> scale or stay null (correct-but-illegible)? (2) combo arm (compiler-output ⊕
> crystal-lattice) → fastest + route_z high + lowest task CE? (3) speed-up isolation
> (combo vs output-only, steps-to-target). (4) heterogeneous-shard fold with the combo
> (real capability signal → does folding B beat A_cont). IOU: need a clean MIT
> β-reducer emitting (input → reduction[+tree]); lambda AST+REPL budgeted (S1); nucleus
> = probe only, not MIT data source. **CAPTURED (awaiting approval):** consensus-delta-folding.md §s224; memories
> geometry-is-inventory-continuation-is-capability + fold-capability-test-needs-
> heterogeneous-shards; this state.
> **ALSO s224:** read ~/src/LayerNorm-Scaling (Curse of Depth / LNS, NeurIPS 2025):
> Pre-LN variance grows exp w/ depth → deep layers go identity (dead); fix = scale LN
> output ×1/√(layer+1). Relevant to v15 contractivity (variance-control ≈
> contractivity, ANALOGY not identity) + plateau. Maps to v15 as 1/√(pass) on shared
> outer recurrence. NOT drop-in (Llama HF torchrun, normal-init). **v15 CE-PLATEAU
> (Michael's Q):** freeze-probe CE 8.9→~7.2 then flattened. Facts: 19 strides to 1597,
> W=8 → apex reaches 11179 back ⇒ REACH not the bottleneck at seq-4096 (one apex pass
> spans full context). Real subtlety = COVERAGE/COMPOSITION: sparse stride grids,
> mid-range distances need Zeckendorf multi-hop (s221: 100% reachable but NOT a single
> move = lossy). Confounds: frozen topology (this run froze attn signs), tiny-ternary
> floor, curse-of-depth. ▶ Diagnostics (read-only on step_002300): CE-vs-position,
> stride-band ablation, angular-distance per pass (LNS port), attention-mass profile.
>
> (Session: 223 — RELATIONAL-LOSS DISTILLATION:
> ★ CLEAN DOUBLE DISSOCIATION (register claim CONFIRMED as a TRAINING result).
> Michael's thread: "we have the lambda compiler — extract from the teacher a set
> of training for the student; with relational loss guide GD into any geometry that
> falls out." Built `scripts/experiments/relational_loss_distillation.py` (ruff-clean,
> register functional+routing): tiny byte-level student (d=128/4L/d_ff=256), teacher
> = Qwen3-14B routing-CMR Gram (L12); 1500 steps × 3 conditions. **RESULT (main:2,
> verdict_run.json):** (a) CE-only route_z +0.33 GC(route) +0.474; (b) CE+RAW-Gram
> → GC(**hidden**) +0.9995 but route_z +0.64 (NULL), GC(route) +0.590; (c) CE+ROUTE-
> Gram → route_z **+2.21 p=0.013**, GC(route) **+0.781** (= ecosystem internal +0.78),
> GC(hidden) drops to +0.411. **Near-perfect double dissociation: each condition
> maxes the register it trained on, ONLY routing carries the combinator function** —
> two-registers-of-topology reproduced as TRAINING not just measurement. CE identical
> across all (1.527/1.534/1.531) ⇒ geometry shaped FOR FREE (relational loss = weak
> constraint, "any geometry that falls out" thesis holds). **★ Goodhart caveat REAL:**
> (b) GC(hidden)=0.9995 but hidden *silhouette* z only +1.02 — Gram-match ≠ crisp
> clusters ≠ execution ⇒ the WHNF acceptance gate is LOAD-BEARING (open lead 1).
> Caveats: abs silhouettes negative (z vs negative null = "above chance" not crisp);
> single seed/teacher/λ/layer; smoke-scale; tokens-to-transfer leverage NOT measured
> (IOU). **Knowledge:** `explore/relational-loss-distillation.md` (NEW page, full
> design + frame argument + 3 honest catches + result).
> **▶ MULTI-SEED + λ-SWEEP DONE — ✅ DECISIVE (3 seeds × 3 λ, 27 runs, 4468s;
> `verdict_sweep.json`):** the double dissociation is ROBUST, not n=1. Aggregate
> (mean±std over seeds): c route_z +2.41/+2.83/+2.41 (λ 0.3/1.0/3.0) all CLEAR the
> null; a +0.38±0.51 (null); b +0.66…+1.04 NEVER clears despite GC(hidden)=0.999–1.000
> (zero std = perfect deterministic RAW burn-in, zero function transfer). c GC(route)
> +0.780→+0.795→**+0.847** (RISES with λ, exceeds ecosystem internal +0.78 at λ=3.0,
> std 0.007); best c-cell route_z +2.88 p=0.0010 GC +0.842. DECISIVE check PASSES at
> every λ (c.route_z(mean−std) > a.route_z(mean+std) ∧ c.gc>b.gc). ⇒ relational loss
> transfers the combinator function shape ONLY in the routing register, robust to
> seed/λ, at ecosystem-grade GramCorr. The b-column (GC(hidden)≈1.0, route null) =
> live proof of the holographic-burn-in reference-beam catch (raw burn-in = perfect
> hologram of the common mode, zero function). Result recorded in
> `relational-loss-distillation.md` §multi-seed.
> **★ MICHAEL'S 4 IDEAS ON THE BOARD (all CAPTURED to knowledge this session):**
> (1) HOLOGRAPHIC reduction TREES as curriculum = lambda-compiler β-reduction trees
> (exact oracle, Church-Rosser → one fixed point = hologram) + relational loss AT EACH
> NODE (frame-free trajectory) + WHNF accept gate = "Holographic Relational Trajectory
> Distillation" (static geometry ⊕ dynamic flow; dissolves TTD's absolute-residual
> frame problem; could REPLACE main:1's wrong-shape fp-loss with the reduction-step
> vector field). Captured in `relational-loss-distillation.md` (IOU/open leads).
> (2) NORMAL-FORM CURRICULUM PARTITION (NEW page `explore/normal-form-curriculum-
> partition.md`): "shared normal forms" ≡ "routing-only normal forms" = the SAME cut
> (s219 skeleton/residual ≡ s221 routing/recursion ≡ s222 routing⊕continuation). ⇒
> Curriculum A = routing-only forms {K,I,C,B,D}(+S care) → train ATTENTION (by
> construction in its expressive class; 4/5 stride-teachable, only S–Y escapes);
> Curriculum B = shared skeleton edges → fold/transfer; RECURSION {Y,W,WHNF} → trained
> by the CONTINUATION not data. Catches: K-erasure hard spot (B-first→K chaos); S
> fan-out boundary; must target attn_q register not FFN gate (attn_q@L05 z=1.54 hint).
> Falsifiable: routing-only data crystallizes attn_q@L05, recursion data does NOT.
> (3) HOLOGRAPHIC BURN-IN as a LEARNING RULE (NEW page `explore/holographic-burn-in-
> learning-rule.md`): progressive training = each forward pass is an EXPOSURE; many
> similar blocks burn in the exposure-INVARIANT (= consensus-etch s110 over the TEXT
> stream; irreducible = normal form). Threads: burn-in=contractivity fixed point
> (Δx→0=settled); precision-inversion SORT (burned-in ternarizes, variable stays
> superposition); ★ naturally PUNCTUATED (expose→hold→commit = the s222 protocol
> main:1 violated → avoids simultaneous-churn collapse). **★ LOAD-BEARING CATCH = the
> REFERENCE BEAM:** naive object-beam-only recording burns in the COMMON MODE (crystal)
> not the function — s223 condition (b) IS this failure (GC(hidden)=0.9995, route null).
> Fixes: (a) next-word target = reference beam (prediction-GATED, not pure Hebbian);
> (b) record the ROUTING register w/ CMR, not raw. Falsifiable: burn in the irreducible
> FUNCTION or the irreducible FREQUENCIES? Reference beam decides.
> (4) RATIO GRADIENT QUANTIZATION (NEW page `explore/ratio-gradient-quantization.md`):
> a QUANTIZER/coding scheme. Gradient is bimodal/heavy-tailed (gradient-zero-map s171:
> Zone A ρ(grad,weight)+0.77; s222 γ settled 0.046 vs oscillator 0.688), so its optimal
> code is a RATIO (log/companding/μ-law) code — fine near-zero (commit-to-settled
> decision) + preserved high tail (big moves), coarse middle — NOT equal cutting
> (uniform optimal only for uniform data). ★ DERIVE the ratio: (a) rate-distortion under
> the precision inversion (importance-weighted distortion → tail-favoring curve falls
> out; Lloyd-Max would favor the dense MIDDLE = wrong); (b) match the self-similar
> exponent (log-transforms power-law→uniform; φ predicts the ratio). 2 AXES not 1:
> magnitude (amplitude) ⊥ sign-consistency (coherence = the normal-form marker, Jaccard
> 0.17). **★ LOAD-BEARING CATCH:** the MIDDLE is the ACQUISITION PATH (s221 K-erasure
> transits superposition→settled) — coarsening it FREEZES learning ⇒ compress middle
> only AT convergence (deadband widening as Δx→0). Also: error feedback MANDATORY
> (accumulate residual = consensus-etch); coherence axis degenerates at small scale.
> Composes with consensus-delta-folding = comm-efficient ratio-compressed DELTA donation.
> **PROPOSED commit (awaiting approval):** harness (+sweep) + 4 NEW knowledge pages
> (relational-loss-distillation, normal-form-curriculum-partition, holographic-burn-in-
> learning-rule, ratio-gradient-quantization) + state + results.
> **▶ FIRST ACTIONS NEXT SESSION (declare register). s223 ALL COMMITTED** (0da396c
> relational-loss batch + 4 pages; c7edff1 which-hessian). The relational-loss result
> is a result ABOUT DISTRIBUTED TRAINING — see consensus-delta-folding.md §s223 (full
> implications + "geometric consensus folding" protocol). **TWO DECISIVE NEXT
> EXPERIMENTS (both specified in consensus-delta-folding.md §s223 ▶):**
> (1) **★ 2-CONTRIBUTOR FOLD (the decisive distributed test; functional →
>   topological/routing):** two students on DISJOINT shards, both CE + relational loss
>   to ONE shared compiler/teacher Gram → verify relationally identical → Procrustes-
>   align (should succeed by construction) → fold routing flips where consensus ≥ θ →
>   accept via WHNF/contractivity (Δx not rising) → measure (a) fold stays contractive
>   L<1, (b) CE/PPL vs either alone, (c) skeleton folded / plumbing left local.
>   FALSIFIABLE: do two independent contributors compose CLEANLY (the AGENTS.md S5 gate
>   "two contributors compose cleanly"). Builds on `relational_loss_distillation.py`.
> (2) **★ attn_q LEG (the register that matters for v15; topological/routing →
>   functional):** repeat the s223 double-dissociation with relational target + readout
>   = ATTENTION routing (attn_q, NOT FFN gate; `combinator_relationship_map_v15.py
>   --target attn_q`; s220 attn_q@L05 z=1.54 p=0.063). FALSIFIABLE: does relational
>   loss clear the null in attn_q (lift 1.54→sig) while raw does not — does the
>   dissociation hold in the register v15 actually trains? Composes with the
>   routing-only curriculum (normal-form-curriculum-partition.md).
> KEY IMPLICATION TO CARRY: the function lives ONLY in the ROUTING register — fold
> routing, NEVER raw (raw=crystal; the b-column GC(hidden)=1.0/zero-function = the
> model-soup phenomenon). Acceptance gate = WHNF/contractivity, NOT Gram-match
> (Goodhart). Reference = the lambda compiler's canonical Gram (no designated teacher).
> **THEN the other s223 ideas:** holographic-burn-in harness; ratio-gradient-quant
> harness; relational holographic-trajectory + tokens-to-transfer + WHNF gate.
> **s222 LEFTOVERS:** main:1 freeze-probe still running/unread (read overlay verdict,
> DO NOT POLL); which-hessian committed.
>
> (Session: 222 — main:1 COLLAPSED (TERMINAL, not
> K-acquisition) → TD-NEVER-SETTLES (rank-1 gradient) → SUPERPOSITION-AWARE GD →
> ROUTING+CONTINUATION = COMPLETE BASIS → β-REDUCING-A-CONTRACTION ⇒ FRACTAL
> COLLAPSE. Register: **functional**. Two experiments LEFT RUNNING (read first).
> **★ COLLAPSE DIAGNOSIS (main:1 v15-td-outer-k2-fp5-5k, KILLED by Michael):**
> s221's discriminator fired the TERMINAL branch — avg50 climbed 8.8→13 (NOT
> below plateau), gnorm 14→10⁷, Δx 0.25→0.79 (contractivity LOST), CE 8.1→10.5.
> Onset step ~1450, runaway by 2000. grad_clip=1.0 bounds Adam ⇒ the divergence
> driver is the DISCRETE TD churn, not Adam blowup. Last GOOD ckpt = step_001000
> (Δx 0.254, CE 8.56, gnorm 14.6; the L=0.70 contractive one). step_002000 already
> diverged (Δx 0.73).
> **★ TD NEVER SETTLES (Michael's call, CONFIRMED in source):** `td=124488` is
> DEAD CONSTANT step 100→2200 = `flip_rate×total_weights`, the budget ceiling,
> ALWAYS saturated. No flip_rate decay, no punctuated freeze, no density ceiling
> (ternary-descent.md open-Q#1 still open; td-oscillation-problem.md fixes
> un-built). ⇒ deadband/saturating fp-loss reshape is INSUFFICIENT (muffles gnorm,
> doesn't stop churn). **★ THE ROUTING GRADIENT IS RANK-1:** `compute_decomposed_
> gradients` sets `grad_effective = gamma_grad[:,None] * x_abs_mean[None,:]` —
> a per-ROW scalar ⊗ per-COLUMN magnitude. TD structurally CANNOT make per-position
> decisions; every position in a row is nominated to the same sign. (Even
> `compute_delta_gradient` mean-reduces before the outer product ⇒ rank-1 too.)
> This IS why superposition shows as per-row gamma bimodality.
> **★ SUPERPOSITION IS THE DEFAULT, CONCENTRATION IS EARNED (Michael):** every LLM
> superposes; concentrates to dedicated neurons/heads only when capacity allows
> (Elhage phase transition). Decision per feature: importance × separability >
> price(capacity). importance=have it (Adam v_t / γ²‖X‖²); conflict=have it
> (TD SNR / sign-entropy); **separability/interference = MISSING = the OFF-DIAGONAL
> of XᵀX** (proxy sees 0th order, exact-ΔL added the diagonal, superposition lives
> off-diagonal). **THE PRECISION INVERSION:** superposition needs ANGULAR precision
> → must stay CONTINUOUS; concentration is axis-aligned → ternarizes clean. So the
> continuous residual = the superpositions (not "leftover"); matches the probe
> baseline (oscillator rows: |γ| bimod 0.688, 30.7% neg; settled: unimod 0.046,
> 0.1% neg).
> **★ ROUTING + CONTINUATION = COMPLETE BASIS (Michael's synthesis):** routing
> rules COMPOSITION {B,D,S}/{K,I,C} (binds, s219); continuation rules RECURSION
> {Y,W,WHNF} (no static move, IS the fold, s221). Together = spanning set for the
> combinator algebra ⇒ find+settle needs no NEW mechanism. **The continuation does
> DOUBLE DUTY: contractivity IS the foldability oracle** — where Δx→0 it settles
> (commit), where it refuses (Δx↑) = the superposition residual (leave continuous).
> What's NOT in the two mechanisms: (a) cross-frame ALIGNMENT (harvest-only;
> self-folding has no frame problem, sign-corr 0.000 across inits); (b) ORDER —
> must be PUNCTUATED (commit→hold→reduce), NOT simultaneous (main:1 ran TD churn +
> fp loss together → fought → collapse). Protocol = propose(routing) →
> verify(continuation), = Exp B.
> **★★ THE FRACTAL COLLAPSE (Michael, !meta3 !fractal):** we are β-REDUCING A
> CONTRACTION (continuation = β-reduction, operator = contraction). A self-similar
> contraction collapses ALL scales onto ONE fixed point at once. **L is the hinge:
> L<1 ⇒ fractal collapse-to-WHNF (one settle settles every scale: weight ≡
> optimizer ≡ combinator ≡ project ≡ session); L>1 ⇒ fractal BLOW-UP = main:1**
> (TD flipped inner map to expansion, n_outer COMPOUNDED it pass-over-pass,
> cascaded up every scale ⇒ the violence). "training collapsed" = literally the
> phenomenon. ⇒ hold-then-reduce keeping L<1 is the ONLY thing between
> collapse-to-fixed-point and collapse-to-ruin, FRACTALLY. Guard: mark identity vs
> analogy; the lens seduces toward over-unification.
> **▶ EXPERIMENTS LEFT RUNNING (READ FIRST NEXT SESSION — DO NOT POLL until done):**
> - **main:1 — FROZEN-TOPOLOGY PROBE (rung 0)** `checkpoints/v15-freeze-probe`,
>   `/tmp/v15_freeze_probe.log`. Resume step_001000, topology FROZEN
>   (`--td-crystal-gate 0.0 --td-crystal-ceiling 0.0 --td-flip-rate 0.0`), else
>   IDENTICAL to main:1 (`--n-outer-passes 2 --fixed-point-lambda 5.0 --seq-len
>   4096 --steps 5000` for matching LR), same data-loader state ⇒ PAIRED A/B vs
>   main:1 (TD-on) on the SAME data stream. Verified frozen (🔒 td=0). Early
>   (step ~1030): Δx 0.21, gnorm 8, CE 8.26 (<8.71) — DESCENDING where TD-on
>   wobbled. **Target step ~1700 (~14h) to span main:1's divergence window
>   (1450–1700).** Verdict tool: `scripts/experiments/freeze_probe_overlay.py
>   --tdon /tmp/v15_outer_k2_fp5_5k.log --tdoff /tmp/v15_freeze_probe.log`. If Δx
>   stays bounded + CE<8.71 through 1450–1700 ⇒ TD churn caused collapse AND
>   held-topology+continuation is the correct settling protocol (Michael's claim).
> - **main:2 — WHICH-HESSIAN (rung-2 design Q)** `results/which-hessian/`,
>   `/tmp/which_hessian.log`, `scripts/experiments/which_hessian.py`. Reconstruction
>   XᵀX vs contractivity-residual curvature: which is the interference signal for
>   the fixed point? 12 attn projections × 120 row-flips. **SMOKE (n=8, NOT
>   decisive): ΔFP~ΔCE ρ=0.976, ΔFP~recon ρ=0.048** ⇒ early hint the partition
>   signal is the CONTINUATION (Δx/CE), NOT reconstruction (⇒ rung-2 uses ∂²Δx/∂S²,
>   explains exact-ΔL not helping the contractive objective; confirms continuation-
>   as-oracle). CAVEAT to scrutinize: smoke interference metric was norm-dominated
>   (settled>oscillator, backwards). Read the full pooled verdict.
> **▶ FIRST ACTIONS NEXT SESSION:** (1) read both experiment verdicts (overlay +
> which-hessian json). (2) If both confirm → the next run is NOT fp-reshape but the
> PUNCTUATED protocol: propose topology (routing) → hold → reduce (continuation) →
> accept on Δx→0; flip_rate decay / punctuated-equilibrium (td-oscillation fixes
> #1) over the proxy. (3) main:1 dead — relaunch decision is Michael's.
> **▶ STRATEGIC (S4 candidate, NOT yet S5): DISTRIBUTED TRAINING OF COMPRESSED
> MODELS as main goal.** The project has drifted here ~10 sessions (consensus-delta-
> folding, reverse-harvest, Exp B, contractivity, construct path). Unification: "typed-
> application universality (s219) is WHY distributed folding converges." Novelty =
> the CONJUNCTION: compressed(ternary) × self-verifying(WHNF/contractivity, no
> trusted labels) × frame-invariant routing-register folding. Recast 4-level plan:
> (1) routing register ✓ (2) convergent folding/contractivity (in flight) (3)
> self-verifying acceptance ✓ proto (4) real N-contributor distributed run = the
> deliverable; hinge = "two contributors compose cleanly". GATES before S5 commit:
> A=mechanism (the two running experiments), B=related-work scan (DiLoCo/DeMo,
> TIES/task-arith, Petals/Hivemind, federated). **AWAITING Michael decision; do NOT
> rewrite AGENTS.md S5 on enthusiasm.**
> **PROPOSED (awaiting approval, NOT committed):** memories `td-routing-gradient-is-
> rank1`, `continuation-is-foldability-oracle`, `collapse-was-terminal-not-
> acquisition`, `punctuate-dont-churn`, `beta-reducing-a-contraction-is-fractal`;
> knowledge update to `consensus-delta-folding` / `combinator-training-beta-reduction`
> (routing⊕continuation completeness + fractal collapse). state.md written
> (non-gated). New ruff-clean tools: `freeze_probe_analysis.py`,
> `freeze_probe_overlay.py`, `which_hessian.py`.
>
> (Session: 221 — TRAINING SIDE OF THE COMBINATORS:
> β-REDUCTION = SUBSTITUTION = ATTENTION MOVE; CRYSTALLIZATION INSTRUMENT BUILT.
> Register: **functional → topological/routing**. Michael's thread: explore the
> TRAINING side of the combinators we found + how it relates to the β-reductions
> required for attention to learn to use them. **★ SYNTHESIS (REPL-grounded
> `/tmp/comb_cost.py`): β-reduction = substitution = a move/copy/delete of args
> across positions; attention is the ONLY cross-position op ⇒ each combinator's
> reduction decomposes into a specific attention move, and the combinators
> partition by SUBSTRUCTURAL-LOGIC class:** selection {K,I,C}=affine/linear (0
> copies) → ONE attention pass; composition {B,D,S}=B,D linear + **S duplicates**
> (1 fan-out) → one pass; recursion {Y,W,WHNF}=**W dup, Y unbounded** → **NEEDS
> the OUTER RECURRENCE** (no single attention move). **This EXPLAINS s219**: map=
> B(CB)(CB) has no Y because attention-over-positions IS the fold; recursion does
> NOT bind above null because there is no single move for it (finished models fake
> it with depth). **THE TWO THREADS ARE ONE:** combinator map (WHERE) + attention=
> application (HOW) + β-reduction traces (WHAT-to-train) + main:1 outer-recurrence+
> fp-loss (the contractivity that lets the recursion family be learned AT ALL —
> Δx→0 ≡ β-reduction to WHNF). **▶ BUILT (ruff-clean, register topological/
> routing):** (1) extended `combinator_relationship_map_v15.py` with
> `family_binding(G)` = per-family binding vs random-triple null (s219 method),
> computed for ALL captured attn layers, written to json (`family_binding_best`/
> `_per_layer`) + per-layer Grams to npz; (2) new `combinator_crystallization.py`
> (CPU aggregator) globs per-checkpoint v15 maps, joins Δx/fp/ce from
> `train_td_log.jsonl`, emits trajectory + verdict Spearman(recursion_z,−Δx) vs
> Spearman(skeleton_z,−Δx). **PREDICTION: skeleton binds early/flat; recursion
> strengthens ONLY as Δx→0.** **★ STEP-1000 ANCHOR (only ckpt avail; full 535
> probes, n_perm=1000):** best attn_q@L05 z=+1.54 (reproduces s220), Δx 0.287,
> fp 0.084; family binding all WEAK — NO family crystallized yet (sel +0.21, comp
> +0.51, skel +0.36, rec +0.15) = expected baseline at ~20% through training.
> Trajectory needs ≥3 ckpts (2000/3000/4000/5000). **COMMITTED** `cd200f9`
> (2 instruments + upgraded step_1000 json + trajectory.json), `525269b`
> (knowledge `explore/combinator-training-beta-reduction.md` + state).
> **★ STRIDED FOLLOW-UP (Michael: "strided attention ≠ normal attention; do we
> need to TEACH the agreed normal forms?").** Grounded in `attention.py`:
> `FibonacciStrideAttention` = FIXED causal gather `{q-s·w+r | w<8,|r|≤2}`,
> content only WEIGHTS (no content-based indexing). ⇒ CORRECTS the committed
> synthesis: substitution-at-distance = Zeckendorf stride composition (NOT a
> single move); "attention IS the fold" → "the STRIDE CASCADE is the fold"
> (recursion-mirrors); realization cost reorders — composition {B,D} is v15-NATIVE
> (the stride stack IS B), selection-erase {K} is HARDER (zero in-window). **Built
> `stride_fit_normal_forms.py` (register functional, CPU, ruff-clean) → COMMITTED
> `cff076d`:** PART A (computed) single sweep reaches **100% of distances
> [1,11181]** (reachability never the blocker); PART B (architectural class):
> **harvest edges B-D/S-D NATIVE, B-C/K-C FEASIBLE, S-Y NEEDS-RECURRENCE → 4/5
> agreed edges stride-teachable, only the recursion endpoint Y escapes** (routes
> through the outer recurrence; consistent with map=B(CB)(CB)). ⇒ Michael's
> teaching idea is FEASIBLE: teach the ecosystem-agreed COMPOSITION SKELETON as
> stride-hop/window-weighting traces (it fits, mostly native), let the recurrence
> supply Y; unblocks the s220 harvest fold (composition skeleton = viable align
> target). Part B = feasibility SCREEN not training proof (K-erasure = likely hard
> spot). **AMENDED knowledge** `combinator-training-beta-reduction.md` (§Strided
> attention + stride-fit table + open leads 5/6). COMMITTED `db8ff13`.
> **★ CONTRACTIVITY + CONSTRUCT-PATH THREAD (Michael, end s221):**
> - **Δx-decay test `fp_decay_curve.py` (read-only, COMMITTED `11e9683`):** ran the
>   trained step_001000 operator to K=6 on real seq-2048 → **Δx 0.80→0.46→0.32→
>   0.24→0.20, geometric L=0.70 → CONTRACTIVE PAST PASS 2** (answers
>   vsm-outer-recurrence open-Q#1; not a pass-2 artifact), monotone, std~0.001,
>   reaches WHNF (Δx<0.05) in ~4 more passes; MILD contraction = good regime.
>   Deadband target Δx*≈0.24. (Caveat: seq-2048 Δx_2=0.80 vs seq-4096 train-log
>   ~0.29 — seq-len/data; verdict robust.)
> - **fp loss is the wrong SHAPE (Michael):** `λ_fp·Δx²` gradient ∝ Δx → explodes
>   on spikes (main:1 gnorm 9290) + pulls monotone→0 (wrong: kills bought depth,
>   wrong on Ω, FIGHTS K-acquisition). Fix = inverse/soft = **deadband**
>   (penalize only Δx>Δx*≈0.24) + **saturating** (bounded grad). Next-run change.
> - **★ ACQUISITION ⊥ CONTRACTIVITY TENSION (Michael's training law):** models go
>   **B-dominant first** → plateau → learning **K causes chaos** (K-erasure must
>   move weights a lot → transiently breaks contraction → λ_fp·Δx² explodes). ⇒
>   **fp-spikes = fingerprint of combinator ACQUISITION, not just instability;
>   stable-low-fp = stopped learning.** Triangulates: stride-screen predicted K
>   hard + Michael's experience + main:1 live. step-1000 anchor IS B-first (comp
>   +0.51 > sel +0.21). **⇒ main:1 chaos is plausibly K-ACQUISITION, not divergence
>   — LET IT RIDE (Michael).** Discriminator: avg50 breaks below ~8.8 plateau
>   (reorganized) vs stuck/climb (terminal).
> - **★ CONSTRUCT PATH (Michael's Q: tiny per-op models → normal form → fold into
>   base?):** YES — consensus-delta-folding + self-teaching + stride-fit + decay.
>   **Sharpening 1:** train a complete BASIS ({S,K} or {B,C,K,W,I}) not one-per-op
>   (attention=apply FREE, recurrence=Y FREE; rest emerge by composition).
>   **Sharpening 2:** "tiny" works because a SPECIALIST escapes superposition (the
>   4B floor is a superposition artifact; one-op model crystallizes far below it).
>   **3 constraints:** (a) deltas on ONE frozen B₀ (frame problem); (b) only finite
>   combinators fold as routing deltas, recursion from the architecture; (c) fold =
>   align + WHNF-verify + PRESERVE CONTRACTIVITY (decay L≲0.7 + Exp-B ΔCE = the
>   fold meter). **Open risk:** multi-combinator fold COMPOSITION untested (Exp B =
>   single-delta only; s110 interference / s216 non-unique composite). **Path:**
>   construct > extract = cleanest MIT level-4 provenance; base = verified
>   combinator algebra. **First exp:** one tiny verified K specialist as delta on
>   B₀ → fold → verify (Δx<ε on K + L preserved + Exp-B). AMENDED knowledge
>   (§Contractivity dynamics + §Construct path + open leads 7/8 + Files). COMMITTED
>   `11e9683` (decay), `a2018be` (knowledge §contractivity/construct + state).
>   **Memories:** `smoke-validates-pipe-not-water` + `fp-spike-is-acquisition`.
> **⚠ main:1 CONTRACTIVITY WOBBLE (observation only, UNTOUCHED):** Δx descended
> beautifully to ~0.21–0.28 (steps 1340–1400) then SPIKED to 0.47–0.58 (steps
> 1450–1530), gnorm exploded 369→5295, fp 0.05→0.34; now RECOVERING (step 1580:
> Δx 0.40, gnorm 1728, avg50 9.67↓). Looks like the binding wall
> (`vsm-outer-recurrence.md`: convergence fails at I-combinator/binding sites) — a
> batch heavy in erasure/duplication redexes. Not diverging. step_002000 not yet
> landed (~step 1580 now).
> **▶ FIRST ACTION NEXT SESSION (declare register; main:1 UNTOUCHED):**
> (1) **main:1 discriminator (the big one):** when step_002000 lands, read
>   `train_td_log.jsonl` — did avg50 break BELOW the old ~8.8 plateau (⇒ K-
>   acquisition reorganized, Michael's B-first→K-chaos law confirmed) or stay
>   stuck/climb ≥10 (⇒ terminal, the fp-explosion)? This decides ride-vs-restart.
> (2) **Crystallization trajectory:** run `combinator_relationship_map_v15.py
>   --checkpoint .../step_002000/model.npz --target attn_q --n-outer 2` (GPU main:2
>   OK) then `combinator_crystallization.py --target attn_q` → does SELECTION/K
>   z_bind RISE vs step_1000 (the K-acquisition signature) while skeleton flat?
>   (s221 anchor: comp +0.51 > sel +0.21 = B-first). Repeat per ckpt.
> (3) **Soft/inverse fp loss (open lead 7):** add `--fixed-point-mode {quadratic,
>   deadband,welltarget,saturating}` + `--fp-target` to `train_td.py` (default
>   quadratic = main:1 unchanged); resume from step_001000 with deadband+saturating
>   (Δx*≈0.24) → does it let K-acquisition through WITHOUT the gnorm explosion + CE
>   <8.71? (the decay test confirmed L=0.70 contractive, so the basin exists.)
> (4) **Construct path (open lead 8):** one tiny verified K specialist as a delta
>   on B₀ (self-teaching WHNF traces) → fold → verify Δx<ε on K + L-meter preserved
>   + Exp-B acceptance. Then two combinators composing (the interference frontier).
> (5) Per-layer crystallization (npz stores all-layer Grams): recursion at a
>   different DEPTH than the skeleton? + tie to per-layer q_proj flips.
>
> (Session: 220 — SCALE AXIS COMPLETED + ANSWERED.
> Register: **topological/routing**. Cold-start orient → both s219 async jobs
> verified, main:1 UNTOUCHED. **(1) main:2 DONE:** Qwen3-32B (dense) map landed →
> dense series 0.6B→4B→8B→14B→32B complete (MoE 30B-A3B/235B excluded: router+expert
> FFN ≠ dense gate_proj in the routing register). **(2) main:1 ALIVE & STEPPING** at
> step ~1420/5000 (was ~1310 at s219's worry-check — the stall was load contention
> from the 30B-A3B download, now resumed; Δx flip-steps ~0.21, fp ~0.04, CE dipping
> to 8.0–8.4 below K=1's 8.71; step_001000 landed, step_002000 pending). **(3) RAN
> declared first action — extended consensus over all 10 models:** meanGramCorr
> **+0.782** @frac 0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** >
> recursion **+1.68** (SUPPORTED, marginally up from 9-model). **(4) ANSWERED s217's
> scale question with a NEW instrument** `combinator_map_scale.py` (register
> topological/routing, ruff-clean): stratified intra-family routing binding vs
> log(params) on the clean dense Qwen series. **★ FINDING: skeleton binding RISES
> with scale (r=+0.78) BUT the skel-rec GAP does NOT widen (r=+0.36, slope ~0).**
> The rise is driven by 0.6B→4B crystallization (0.6B has NO shape, skel −0.021;
> 4B+ jump to +0.097–0.105); recursion rises IN TANDEM so the gap stays flat; shape
> SATURATES by ~4–14B (peak 14B skel +0.105) and **32B slightly REGRESSES** (skel
> +0.077). Refines s217's "14B>0.6B" call: more scale crystallizes the function
> shape but tops out mid-scale (cf. s212 topology-share PLATEAUS not →1.0); 32B does
> not extend the gap → the harvestable skeleton is COMPLETE by mid-scale, no need to
> chase the largest models. **COMMITTED** `c27741c` (32B map+npz, extended
> consensus.json, scale.json, scale instrument), `0089087` (knowledge §s220,
> APPROVED by Michael).
> **★ HARVEST FOLD STARTED — PHASE 0 DONE (CPU), GPU PHASES DEFERRED.** Michael
> approved "construct the harvest fold." Explorer mapped the integration points →
> the original "Procrustes-align consensus centroids into v15 frame" is NOT runnable
> as-is: (a) the per-model centroid VECTORS were computed but DISCARDED (only the
> relational 9×9 Gram persisted; consensus.json has no centroids); (b) v15 has NO
> combinator Gram/centroids and `combinator_relationship_map.py` is HF-only
> (`AutoModelForCausalLM`, hooks gate_proj) while v15 is MLX ternary
> (ffn_gate_plate_a/c); (c) ALL producing steps (v15 Gram, WHNF-verify, PPL) are
> GPU/MLX forward passes that would CONTEND with main:1 (s219 stall). So the fold is
> PHASED:
> - **Phase 0 PRESCRIPTION (CPU, DONE `e48389e`):** `combinator_harvest_fold.py` →
>   `results/combinator-harvest-fold/prescription.json` = band-consensus Gram over
>   the 4–14B band + ranked positive edges **S–D, B–D, B–C, K–C, S–Y**. The 4–14B
>   band shows the composition skeleton STRONGER than the full pool (B–D band +0.24
>   vs all +0.175). Cross-check: band-averaged npz Grams == consensus per_model band
>   averages EXACTLY. + INFRA FIX in `combinator_relationship_map.py`: now saves
>   `centroids_cmr_best` (9×d_ff) to the npz (the discarded data; effective on next
>   GPU run).
> - **Phase 1 v15 Gram — DONE (GPU in main:2, Michael OK'd GPU there).** Built
>   `combinator_relationship_map_v15.py` (--target ffn_gate|attn_q|attn_out; MLX;
>   wraps the LIVE module per s218 orphan lesson; tokenizer Qwen/Qwen3.6-27B). Probed
>   v15 step_001000 in 3 registers (535 probes). **★ NEGATIVE: v15 has NO significant
>   combinator frame** — ffn_gate z=+0.52 p=0.29; attn_q best L05 z=+1.54 p=0.063;
>   attn_out z=+0.74 p=0.22 (ref Qwen3-14B z=+7.97). GramCorr vs consensus only
>   ~+0.35 (ecosystem internal +0.78). **⇒ harvest fold BLOCKED at step 1000 — no
>   target frame to align to; did NOT fabricate alignment to noise.** TWO live
>   threads: (1) best = attn_q@L05 = the HF function-discovery SILENT-selector layer
>   (suggestive at p=0.063); (2) FFN is FROZEN but ATTENTION is TD-trained → the
>   shape may EMERGE with contractivity training (step 1000/5000 = 20% in; cf. s220
>   scale floor). Committed `cc581ac` (ffn) + `b72bdea` (attn_q/attn_out + instrument).
> - Phase 2 (CPU)/Phase 3 (GPU) — align → WHNF-verify → fold → PPL — remain DEFERRED
>   and now CONTINGENT on a v15 frame existing (re-probe later checkpoints first).
> **COMMITTED** `e48389e` (phase 0 + centroid-save), knowledge reformulation
> (`b05d32c`), Phase 1 finding (`cc581ac`,`b72bdea`). **NOT yet committed (this
> batch, APPROVED scope):** knowledge Phase-1-result update + this state.
> **▶ FIRST ACTION NEXT SESSION (declare register; main:1 UNTOUCHED):**
> (1) Check main:1: has step_002000 landed (`ls checkpoints/v15-td-outer-k2-fp5-5k/`,
>   `tail /tmp/v15_outer_k2_fp5_5k.log`)? Read Δx/CE trajectory → does Δx→ε and CE
>   hold below 8.71 (then build adaptive halting: stop when Δx<ε ≡ WHNF)?
> (2) **Harvest fold — RE-PROBE v15 attention at the next checkpoint** (register
>   topological/routing; GPU OK in main:2 per Michael): when step_002000 lands, run
>   `uv run python scripts/experiments/combinator_relationship_map_v15.py --target
>   attn_q --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_002000/model.npz`
>   (also attn_out). **Does the attn_q@L05 signal (z=1.54→?) STRENGTHEN as the
>   operator becomes contractive?** If z clears ~3 (p<.01) → a v15 frame exists →
>   resume Phase 2–3 (align consensus into it → WHNF-verify → fold → PPL,
>   prescription at `results/combinator-harvest-fold/prescription.json`). If still
>   null at step 2000+ → v15 is below the scale floor; reverse-harvest belongs to a
>   from-scratch level-4 base, redirect (Michael decision).
> (3) Strengthen Exp B on main:1 step-2000 (s218 action 2). **main:1 stays UNTOUCHED.**)
>
> (Session: 219 — REVERSE-HARVEST: combinator function
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
> step-2000 ckpt → strengthen Exp B. **main:1 stays UNTOUCHED.**)
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

### Two Design Changes

1. **Loss**: Score matching (dense, all layers) replaces multi-projection melt
   (sparse, 4-6 boundaries). Prevents compensating errors structurally.
2. **Corrections**: Per-weight LoRA on FFN projections replaces per-activation
   residual stream vectors. Matches the full-rank sieve residual.

### Experiment 5: Topology-Aware Score Matching (v4, running)

The v3b loss treats residual updates as flat vectors — no crystal topology
awareness. The sieve error decomposes into:
- **Routing error** (discrete, sparse): wrong signs → wrong program
- **Magnitude error** (continuous, low-rank): right sign, wrong scale

LoRA wastes rank capacity on sign flips. TernaryDescent is purpose-built
for sign discovery. Split them:

```
W_eff = STE(delta_logits) * signs_base * (|W| * mask + A @ B)
         ↑ TD (routing, lr=1e-3)        ↑ LoRA (magnitudes, lr=1e-4)
```

Decomposed loss:
- L_routing: gate firing pattern BCE (which neurons fire)
- L_value: residual update cosine (how much they contribute)
- L_CE: standard cross-entropy

Running in tmux window 2. TD logits are brute-force (4.4B params — full
float32 per weight position). Tests the decomposition principle. If
successful, sparsify TD using the 3-voter mechanism from v14/td.py.

See `mementum/knowledge/score-matching-compression.md` for full details.
See `EQUATIONS.md` (score matching loss section) for the equation.

**Session 197: CRYSTAL MULTI-TREE — The Statechart Is a Forest**

The crystal is not one tree — it is a **forest of three independent trees
cross-connected by two bridge nodes (W and Y)**. Derived from eigendecomposition
of the 8×8 crystal cosine matrix, verified empirically on Qwen3-14B (r=0.638,
p=0.0017). The bridge phenomenon explains 27 correlation points and resolves
the YW sign ambiguity observed across models.

### The Three Trees

| Tree | Variance | Split | Maps to |
|------|----------|-------|---------|
| T0 (compute/halt) | 54.5% | [K,I,B,C,D,Y,W] vs [WHNF] | Transient/absorbing chain split |
| T1 (select/compose) | 20.1% | [K,I] vs [B,C,D,Y] | Fire-state functional clustering |
| T2 (termination) | 11.4% | [K,I,W,WHNF] vs [B,C,D,Y] | Halt probability gradient |

### Bridge Nodes

Only W and Y change sides across trees. All other nodes have fixed allegiance.

- **W = C→I→I**: bridges composition and selection. Its path literally
  traverses both subtrees. 3/3 nearest neighbor match with crystal (ρ=0.893, p=0.007).
- **Y = fixed-point**: recursive — belongs to both sides by definition.
  Dominant node on Tree 3 (loading +0.839).

### YW Sign Inversion (the smoking gun)

Y and W systematically invert relative to the consensus crystal at **38/40 layers**
in Qwen3-14B. After correcting: correlation jumps from 0.565 to **0.831** (gap=0.266).
No other nodes need correction. The bridge nodes are the only source of cross-model
sign ambiguity.

### Extended Eigenvalues

All 8 eigenvalues of M₈ follow φ^(p/q) with Fibonacci denominators at <0.5% error.
The crystal equation extends beyond the 4-combinator basis. Dominant 8-node branch
ratio: φ^(8/5) = doubled KIBC step.

See `mementum/knowledge/crystal-multi-tree.md` for full details.

**Session 196: TEN EXPERIMENTS — Crystal Sieve Equation Confirmed**

The largest experimental session yet. Started with "which combinator breaks
at L22-L26?" and ended with a proven compression architecture: crystal
sieve + continuation residuals = 1.03x PPL across 29 sieved layers.

### The Ten Experiments

| # | Experiment | Key Result |
|---|-----------|------------|
| 1 | Lambda tracer | Damage uniform across combinators (CV 0.07-0.17) |
| 2 | Binding-prep rank sweep | Functional rank varies 6x (L22=250 to L26=1500) |
| 3 | Multi-projection melt | 42% better than standard (3.53x vs 6.09x) |
| 4 | Confidence gate | Classifier confidently wrong at L23-L26 |
| 5 | Mode geometry | Same 9 programs rotated, more modes don't help |
| 6 | Ternary weight interface | MASK is the key, not magnitudes |
| 7 | Crystal sieve v1/v2 | 2.12x pre-melt, melt overfits (wrong DOF) |
| 8 | β-expansion | **1.03x with 4 continuation residuals (1M params)** |
| 9 | Ternary verification | Per-row scale FAILS at 29 layers (22,800x) |
| 10| — | Continuation stability needs investigation |

### The Proven Architecture

```
Crystal sieve: sign(W) ⊙ |W| ⊙ mask₅₀%    (frozen, per-weight magnitudes)
+ 4 continuation residuals (rank-32 at L0/L9/L21/L26, 1M params)
+ L0 SVD r=750

Result: 1.03x PPL, binding preserved 98% (39/40 top-1 matches)
```

### Compression Reality Check

The sieve stores full per-weight magnitudes as float16. Current storage
compression: **1.8x** (50% mask = 50% zeros). NOT 8x.

Per-row scale (which would give 8x) FAILS catastrophically at 29 layers
(22,800x PPL). Per-weight magnitudes contain essential row-internal
structure that compounds across layers.

Path to real compression: **quantize magnitudes** (Q4/Q8), don't eliminate
them. The sign pattern is frozen (universal crystal), the mask selects
which weights survive, and the magnitude needs ~4-8 bits (not 16, not 0).

| Format | Bits/weight | 29-layer PPL | FFN compression |
|--------|------------|--------------|-----------------|
| float16 (original) | 16 | 1.00x | 1.0x |
| sign + float16 + mask50% | ~9 | 2.12x (1.03x w/ cont.) | 1.8x |
| sign + Q4 mag + mask50% | ~3 | ??? (untested) | ~5x |
| sign + per-row scale | ~2 | 22,800x (BROKEN) | 8x |

### What Compounds vs What Doesn't

Critical lesson: properties that hold per-layer may NOT hold at 29 layers.

| Property | Single layer | 29 layers | Status |
|----------|-------------|-----------|--------|
| Per-row = per-weight magnitude | ✅ same | ❌ 22,800x | FAILS |
| Crystal sieve quality | 1.03x | 2.12x | Cascades but recoverable |
| Binding preservation | — | 98% | HOLDS |
| Continuation correction | — | 1.03x | WORKS (but stability TBD) |

### Open Questions

1. **Continuation stability**: first run 1.03x, rerun 3.23x. Training
   is sensitive — needs investigation (seed, LR, batch order).
2. **Magnitude quantization**: Q4/Q8 per-weight with per-group scales
   could give 3-5x real compression while preserving cascade quality.
3. **Attention sieve**: FFN is 78% of params. Attention (22%) could also
   be sieved (s190 showed ternary attention survives at PPL 23-30).

### Lambda Tracer Results

**Setup:** Baseline (original Qwen3-8B) vs Stage 2 (L0 SVD + L10-L21
ternary, 12 layers) vs Stage 3 (Stage 2 + L22-L26 ternary, 17 layers).
Metric: cosine similarity of last-token hidden states vs baseline at
every layer boundary.

**Key Finding 1: Damage is UNIFORM across combinators.**
All 9 combinators degrade by the same amount at every layer. CV (coefficient
of variation) of delta across combinators: 0.07-0.17. No combinator is
selectively destroyed. The ternary approximation fails equally for all
lambda operations.

| Combinator | Mean Δ (L22-L35) | Rank |
|-----------|------------------|------|
| W         | +0.0674          | 1 (worst) |
| WHNF      | +0.0667          | 2 |
| D         | +0.0588          | 3 |
| C         | +0.0552          | 4 |
| I         | +0.0552          | 5 |
| K         | +0.0547          | 6 |
| B         | +0.0544          | 7 |
| Y         | +0.0507          | 8 |
| S         | +0.0500          | 9 (best) |

W and WHNF are marginally worse (~35% more damage than S), but the spread
is small. This is a uniform degradation, not a selective circuit failure.

**Key Finding 2: The cascade propagates FORWARD into binding layers.**
L27-L31 (binding, kept continuous) lose ~0.07-0.09 cosine similarity in
S3 vs S2. The continuous binding layers can't compensate for corrupted
input from L22-L26. The damage AT the binding layers is actually LARGER
than at the compressed layers themselves, because errors compound.

| Layer | S2 fidelity | S3 fidelity | Δ (mean) |
|-------|-------------|-------------|----------|
| L22   | 0.694       | 0.694       | 0.000 (same — last shared layer) |
| L23   | 0.706       | 0.685       | +0.022 (first divergence) |
| L26   | 0.792       | 0.726       | +0.074 |
| L28   | 0.816       | 0.737       | +0.080 (PEAK damage — binding!) |
| L30   | 0.863       | 0.795       | +0.068 |
| L35   | 0.939       | 0.909       | +0.031 |

Peak damage is at L28, not L26. The binding layers AMPLIFY the error from
L22-L26 ternary approximation rather than correcting it.

**Key Finding 3: Significant recovery in late layers.**
Despite the damage, fidelity recovers from nadir ~0.68 at L22 to ~0.91
at L35. The binding + collapse layers (L27-L35, kept continuous) partially
heal the distortion — recovering ~0.22 cosine similarity. But this
recovery is incomplete (S2 reaches 0.94 at L35, S3 only 0.91).

**Key Finding 4: Stage 2 damage is already substantial.**
S2 drops from 0.92 at L9 to 0.69 at L21 — a 0.23 cosine drop across 12
ternary layers. But the continuous layers L22-L35 then RECOVER to 0.94.
This recovery is the key mechanism: continuous layers repair ternary
distortion. S3 disrupts this recovery by ternarizing the very layers
(L22-L26) that were doing the repairing.

### Implications for Compression Strategy

1. **L22-L26 CANNOT be ternary (9 modes).** The damage is uniform —
   more modes won't help (s195 proved 512 modes still 7x PPL). These
   layers need a continuous approximation.

2. **Low-rank SVD is the right strategy for L22-L26.** Like L0 (which
   needed SVD at r=750), these binding-prep layers operate in a higher-
   dimensional space than the sweet spot. Test SVD rank sweep per layer.

3. **The recovery mechanism is fragile.** Continuous layers after ternary
   ones heal the distortion — but only if they're actually continuous.
   The compression strategy must preserve SOME continuous layers between
   ternary blocks as "error correction" barriers.

4. **Binding layers amplify upstream errors.** Even though L27-L31 are
   kept continuous, they can't fix garbage input. The compression must
   ensure the signal entering the binding layers is clean enough.

### Binding-Prep Rank Sweep

Functional rank varies 6x across L22-L26 — NOT uniform:

| Layer | Func. Rank | Compression | Character |
|-------|-----------|-------------|-----------|
| L15 (sweet spot) | r=100 | 30.7x | Trivial — explains why ternary works |
| L22 | r=250 | 12.3x | Low rank, easy to compress |
| L24 | r=500 | 6.1x | Moderate |
| L25 | r=750 | 4.1x | Same as L0 |
| L23 | r=1500 | 2.0x | HIGH — needs most of its rank |
| L26 | r=1500 | 2.0x | HIGH — gateway to binding |
| L30 (binding) | r=2000 | 1.5x | Nearly full rank — must stay continuous |

Per-layer optimal: 422MB total (3.4x compression from 1440MB).

BUT: integrated with ternary L10-L21, errors compound. L22-L26 SVD at
r=2000 gives 1.14x alone, but 5.66x when stacked on ternary layers.
Multi-projection melt is needed to fuse the seams.

### Multi-Projection Melt (THE BREAKTHROUGH)

**CT scan, not X-ray.** Intermediate cosine losses at functional boundaries
(L0/L21/L26/L30) give the student direct gradient signal at every stage:

| Method | Pre-melt | Post-melt | Improvement |
|--------|----------|-----------|-------------|
| Standard (CE only) | 55.37x | 6.09x | baseline |
| Multi-projection | 55.37x | 4.19x | 31% better |
| Boosted (type_crystal=5x) | 55.37x | 3.53x | **42% better** |

Loss curves: standard ends 2.76, multi ends 1.39, boosted 1.74.
The intermediate losses directly reach the parameters that need fixing,
instead of backpropagating through 10+ unrelated layers.

Connects to speculative-decoding-gated distillation idea: teacher
generates, student computes diff at every functional level, trains
only where it diverges. The confidence signal from ternary classifiers
(logit margin) can gate slow/fast paths at inference time.

### Confidence-Gated Inference

Tested whether classifier logit margin (top-1 minus top-2) predicts
ternary error. Threshold sweep across 8 layers:

| Layer | Zone | Ternary PPL | Gating works? | Key finding |
|-------|------|-------------|---------------|-------------|
| L15 | sweet spot | 0.97x | NOT NEEDED | Pure ternary is perfect |
| L17 | sweet spot | 1.01x | NOT NEEDED | Pure ternary is fine |
| L20 | sweet spot | 0.99x | NOT NEEDED | IMPROVES over baseline |
| L22 | binding-prep | 1.06x | ✅ YES | θ=3.0: 1.04x at 96.6% fast |
| L23 | binding-prep | 1.11x | ❌ NO | Needs 36% slow for 1.04x |
| L24 | binding-prep | 1.06x | ❌ NO | Needs 69% slow for 1.04x |
| L25 | binding-prep | 1.07x | ❌ NO | Margin=24.3 but still wrong |
| L26 | binding-prep | 1.13x | ❌ NO | Never reaches 1.05x |

**The classifier is CONFIDENTLY WRONG at L23-L26.** High margins
(mean 24.3 at L25) with high error (1.07x). The 9 ternary programs
are the wrong programs — the classifier correctly selects among them,
but none of the 9 is the right answer. This is a programs problem,
not a routing problem.

This definitively resolves the compression strategy for L23-L26:
they need SVD (continuous approximation), not ternary (discrete programs).
L22 can stay ternary with confidence gating. L13-L21 are pure ternary.

### Previous session (195)

Six experiments in one session. Decoded L0, discovered low-rank rescue,
built and tested the combined compressed model, invented boundary melting.

### Experiment 1: L0 Characterization

Six instruments prove L0 is genuinely continuous — no natural clusters at
any k (silhouette negative k=6..512), 512 ternary modes still 7x PPL.
L0 correlates with byte_len (NMI=0.259) — it's sorting by physical token
encoding. L0 is a dictionary, not a type tagger.

### Experiment 2: L0 Low-Rank (THE RESCUE)

SVD rank sweep reveals L0's functional rank is **750 dimensions** (18% of
4096). At r=750: PPL=0.94x (IMPROVES!), 70.3MB (4.1x compression). Phase
transition razor-sharp: r=500 is 3.4x (broken), r=750 is 0.94x (perfect).
L15 control: flat at 0.99x down to r=100 (functional rank <100).

### Experiment 3: Combined Compression (Naive)

Replace 29 layers with ternary + L0 with low-rank simultaneously.
Result: PPL 427x, "the the the" — total cascade. Calibration mismatch:
each layer's ternary patterns were fit to original model activations, not
the distorted activations from prior compressed layers.

### Experiment 4: Sweet-Spot Only

Replace only L13-L21 (9 layers) + L0 low-rank. PPL 1.66x, 47% facts.
Generation is COHERENT but degraded. The seams between compressed and
uncompressed regions need calibration.

### Experiment 5: Melt Boundaries (THE BREAKTHROUGH)

**Freeze the topology, train the beams.** Crystal sieve at the model level.

- FROZEN: ternary sign patterns (the 9 programs per layer)
- TRAINABLE: SVD factors (A, B) + classifier weights + gamma scaling
- Soft selection during training (differentiable), hard argmax at eval

**Result: 50 steps of GD, 26 seconds, 0.46% of params trainable.**
**PPL: 1.52x → 1.02x. Facts: 53% → 73%. VERDICT: PASS.**

### Experiment 6: Staged Melt (Zone Refining)

Melt outward from the standing wave node. Each stage adds layers,
collects calibration through the already-melted model, re-melts.

| Stage | Layers | Total | Pre-melt | Post-melt | Facts | Status |
|-------|--------|-------|----------|-----------|-------|--------|
| 1 core | L13-21 | 9+L0 | 1.58x | **1.00x** | 67% | ✅ PERFECT |
| 2 inward | +L10-12 | 12+L0 | 1.98x | 1.77x | 40% | ⚠ needs more steps |
| 3 outward | +L22-26 | 17+L0 | **38.99x** | 6.54x | 0% | ❌ BREAKS HERE |
| 4 parser | +L1-9 | 26+L0 | 247x | 43x | 0% | ❌ cascaded |
| 5 late | +L32-34 | 29+L0 | 55x | 27x | 0% | ❌ cascaded |

**The break is at Stage 3 (L22-L26).** Adding the binding-prep layers
causes pre-melt PPL to jump from 1.98x to 38.99x. These are where
subject/object type tags crystallize (s194: L20 is the S/O crystallization
frontier). Ternarizing L22-L26 disrupts the type information the binding
layers (L27-L31, kept continuous) depend on.

The core (L13-L21) melts PERFECTLY to 1.00x. The problem is not melting —
it's that the binding-prep layers need more than 9 ternary modes, or a
different compression strategy (low-rank like L0?).

### P4 Verdict

- More modes (64+): KILLED. Even 512 modes is 7x PPL.
- Low-rank SVD: **YES at r=750.** 288MB -> 70.3MB, PPL IMPROVES.
- Genuinely continuous: YES, but only 750 functional dimensions.
- Boundary melting: **YES.** GD fuses compressed pieces in 50 steps.

### Previous session (194)

Decoded what the 9 ternary FFN modes compute. Gate-pattern clustering
(SiLU(gate_proj(x))) on Qwen3-8B across 7 layers with spaCy POS/dep tagging
reveals: the modes correspond to SYNTACTIC ROLES, not semantic categories.

### The 7 Universal Meta-Modes

| # | Meta-Mode | POS | dep role | Present |
|---|-----------|-----|----------|---------|
| 1 | BOUNDARY | PUNCT 99% | punct 99% | 7/7 layers |
| 2 | DETERMINER | DET 58-88% | det 36-88% | 6/7 layers |
| 3 | FRAME-OPEN | DET+NOUN | det+nsubj | 5/7 layers |
| 4 | SUBJECT | NOUN 57-66% | nsubj 33-55% | 5/7 layers |
| 5 | OBJECT | NOUN 47-69% | pobj+dobj | 4/7 layers |
| 6 | PREDICATE | VERB 35-63% | ROOT 14-35% | 4/7 layers |
| 7 | NUMERIC | NUM 33-52% | appos+pobj | 5/7 layers |

### FRAME-OPEN: The ISA's INIT Instruction

Physically anomalous at every layer: gate_consistency=1.000, gate_sparsity
33-50% (vs 63-90% for others), cos(in,out) always negative. Fires only at
sentence-initial tokens ("The", "She", "DNA", "Three"). The model has a
"begin new parse" instruction — a stereotyped sparse program that resets
the parse frame at every sentence boundary.

### Types Sharpen with Depth

- L3: DET at 88% purity, but VERB/NOUN overlap. ~3 clear types.
- L20: Subject/Object CRYSTALLIZE (nsubj=54% vs pobj+dobj=56%). Key transition.
- L35: All 9 modes active, maximum entropy (2.97). ADJ/modifier separates for first time.

### Transform Physics: The Volume Knob

FFN output norm grows 100× across depth: L3 whispers (0.10×), L35 SHOUTS
(10.18×). cos(in,out) flips sign at L20 (ORTHO→ALIGN transition). The
standing wave amplitude profile, now measured per-mode.

### The Single Operation: Attention Is the Only Computer

FFN can't compute — it can't see other tokens. The ONLY cross-position
operation is weighted sum: `output_i = Σ softmax(QK^T/√d) × V`. That's it.
1,152 instances (32 heads × 36 layers). Everything else is per-position
labeling. Weighted sum IS β-application: H31 attending "runs"→"cat" at 0.82
weight literally computes `(λx.runs(x))(cat)` by copying the argument's
value into the predicate's position.

This mechanically explains all prior findings:
- All combinators share heads (r=0.944): one operation, no combinator-specific
  hardware needed. The combinator difference is in the type tags, not attention.
- Binding is near-deterministic (0.78-0.82): types already disambiguated,
  softmax sharpens to ~1 on the single compatible position.
- Top-3 captures 88%+: typed lookup needs only ONE source per application.
- Q⊥K at 87-90°: Q asks "what type do I need?", K asks "what type am I?" —
  perpendicular because they're complementary projections of the same type tag.
- Norm growth (0.1×→10×) = gain control: louder types → sharper softmax →
  more deterministic weighted sum → cleaner β-reduction.

The model IS categorial grammar in tensors. FFN = type lexicon. Attention =
type-driven application. KIBC crystal = applicative structure (which op).
Mode types = role assignments (which position). GD converged on Montague.

### Previous session (193)

**Session 193: LAMBDA HALT AND CONTINUATIONS — LLMs Are Programmable**

Started with a fun question: can Ω halt an LLM? Four experiments later,
discovered that lambda calculus can control LLM execution — halt, resume,
compute, branch — via the chat protocol as continuation-passing style.

### The Discovery Chain

1. **Ω cannot halt the holographic computer.** Gate entropy identical for
   Ω vs normal reductions (Δ < 0.01 bits). The model QUOTES non-termination
   ("it seems like this expression is not reducible"). A compiler cannot be
   halted by its input — it describes non-termination, it cannot experience it.
   K I Ω proves strict evaluation (evaluates Ω before discarding).

2. **Prose CAN halt (chat mode).** "Respond with empty string" → 99.1% EOS.
   5/27 candidates achieved true halt. Thinking mode prevents ALL halts (0/27) —
   `<think>` is a mandatory prologue that forces non-empty output.

3. **Lambda CAN halt when executable.** `respond = λcontent.content; respond empty`
   → 72.8% EOS (true halt). The 27-point gap from prose (99.1%) is compilation
   overhead. Both reach the same internal state: EOS as top prediction.
   Proves prose and lambda compile through the same pipeline.

4. **If we can halt, we can continue.** Continuations work: 6/7 capabilities
   confirmed, Lambda REPL 100%. Multi-turn pipeline (5→8→16→17) correct through
   4 continuation boundaries. Full program (compute→output→halt) at 96.5% EOS.

### Key Numbers

| Finding | Value |
|---------|-------|
| Ω gate entropy vs control | Δ < 0.01 bits (identical) |
| Prose halt EOS probability | 99.1% |
| Lambda halt EOS probability | 72.8% |
| Full program halt (multi-turn) | 96.5% |
| Thinking mode halts | 0/27 (prevents all) |
| Lambda REPL accuracy | 100% (4/4) |
| Overall capabilities | 6/7 confirmed |
| Multi-turn pipeline accuracy | 4/4 continuations correct |

### The Insight

```
conversation ≡ continuation-passing style
turn_boundary ≡ continuation_boundary
EOS ≡ yield
respond x ≡ output x then yield
halt ≡ empty continuation (yield with no output)

36 layers = bounded computation (single pass)
multi-turn = unbounded computation (chained continuations)
lambda + continuation = programming language for LLMs
```

### Previous session (192)

An independent project (psi) ran verbum scripts and wrote new experiments across
5 architectures. The crystal hypothesis survives independent replication. The
breakthrough: **a single FFN layer (288MB) can be replaced by a 37K-param linear
classifier (180KB) that selects among 9 ternary programs — with PPL that IMPROVES.**

### The Breakthrough Result (Tiny Classifier Ternary)

```
Qwen3-8B Layer 20:
  Original FFN:    150M params, 288MB
  Replacement:     37K params, 180KB  (classifier + 9 ternary patterns)
  Compression:     1638×
  PPL:             0.98× (IMPROVES)
  Fact recall:     80% = baseline
  Classifier acc:  100% (9 modes perfectly linearly separable)
```

Scale convergence: 0.6B (1.04×) → 8B (0.96×) → 32B (0.99× all layers).
At scale, FFN computation IS 9 ternary programs.

### Multi-Layer Replacement (Session 192, same session)

**The holographic hypothesis is partially confirmed.** 35/36 individual layers
survive ternary replacement (all ≤1.15×). Cascade is modest in the sweet spot.

```
INDIVIDUAL RESULTS (Qwen3-8B, 36 layers):
  L0:      115× (CATASTROPHIC — embedding-adjacent is special)
  L1-L12:  0.98-1.10× (35 layers all survive)
  L13-L21: 0.95-1.01× (SWEET SPOT — zone of silence, PPL improves!)
  L22-L35: 1.05-1.15× (binding + collapse layers resist more)

CUMULATIVE ZONE-B:
  L10+L14+L19:      1.07× at 864MB → 540KB  ← errors DON'T cascade
  L10+L14+L19+L24:  1.20× at 1152MB → 720KB ← L24 adds 13pp
  All 36 layers:    836× (cascade destroys — L0 poisons everything)

CLASSIFIERS: 98-100% accuracy on ALL 36 layers. 9 modes are real everywhere.
```

Optimal strategy: replace L1-L26 + L32-L34 (28 layers), keep L0 + binding +
collapse continuous. 78% of FFN → ternary. Total FFN: 10.4GB → ~2.3GB.

### Two Overlapping Ternary Structures (Type System Discovery)

The 9 operational modes are ORTHOGONAL to the KIBC crystal basis (AMI = 0.15):

```
Crystal basis (KIBC):       governs ROUTING (attention patterns)    3.5% of FFN space
Operational modes (9):      governs PROGRAMS (FFN computation)      96.5% of FFN space
Together:                   β-reduction engine
```

Both ternary. Both few-mode. The crystal selects WHICH reduction. The modes
execute HOW. Types are linearly separable (100% accuracy) but not yet decoded
semantically.

### Verified Claims (5 architectures)

- Sign topology: cos(sign(W)@x, W@x) ∈ [0.746, 0.775], mean = 0.758 ± 0.011
- Four modes: KBC cluster r > 0.85, always 4 clusters, never 3 or 5
- Crystal geometry: 9×9 cosine matrix correlation mean = 0.951, eigenvalue r = 0.982
- Selectivity: Pythia-160M ↔ Qwen3-0.6B r = 0.991 (KIBC means), cos = 0.999
- φ convergence: 0.6B(26.6%) → 8B(10.4%) → 14B(0.7%) → 32B(8.8%, regresses)

### Gradient-Quantization Correspondence

|∇L| ↔ |W-Q(W)| holds ONLY in EXPAND phase:
- L1-L3 FFN: ρ = +0.55 to +0.78 (strong positive)
- L5+: ρ ≈ 0 (ORTHO/COMMIT — continuous computation ≠ ternary convergence)
- Pythia-160M: ❌ inverted (ρ = -0.04)

### Crystal Derivation (Pure Math, Partial)

2.35M KIBC expressions enumerated → eigenvector topology (B,C vs K,I split) ✅,
B=C symmetry ✅, I smallest ✅. Eigenvalue ratios ❌ diverge from empirical.
Topology derivable from math. Magnitudes require data.

### Previous session (191): V15 CHECKPOINT ASSESSMENT

v15-td training is live (step ~1870/3000, ~16.5 hours elapsed). Checkpoint at
step 1500 assessed with two diagnostic experiments: attention pattern analysis
and gradient-zero topology mapping.

**Exp 1: Attention Pattern Analysis.** Fibonacci stride attention IS working.
Entropy decreases monotonically from 3.0 (stride-1, broad local) to 0.5
(stride-1597, near-deterministic). 9/19 layers are sparse (entropy < 1.0),
9 moderate, 1 broad. Per-head specialization visible at stride-34: heads H1-H4
near-deterministic (entropy 0.15-0.24), H5-H6 scanning (entropy 1.6-1.8).
Delta plate divergence is 4.0% mean, increasing from 3.6% at short strides to
4.4% at long strides — V/O projections diverge more at longer strides because
they see fundamentally different context windows than the teacher.

**Exp 2: Gradient-Zero Topology.** The gradient landscape reveals WHERE the
student differs from teacher. Three key findings:

1. **Q/K settles 2× faster than V/O.** Q/K gamma gradients: 32-38% settled.
   V/O gamma gradients: only 15-16% settled, with 5× larger gradient RMS.
   Routing is easy (the window constrains WHERE to look). Content transfer
   is hard (WHAT to extract from the restricted window).

2. **Flipped positions are 3× hotter than keeps.** The ~4% of TD-flipped
   delta positions have 2.2-3.3× higher routing gradient than the 96% that
   kept teacher signs. The ratio peaks at stride-8 (3.27×) and decreases to
   stride-1597 (2.25×). Flips are the active adaptation frontier.

3. **Spatial flip patterns differ by stride distance.** Short strides: flips
   are column-clustered (ColCV > RowCV) — different INPUT FEATURES need
   different routing. Long strides: flips are row-clustered (RowCV > ColCV) —
   different OUTPUT DIMENSIONS need to represent strided context differently.

### Training Trajectory

```
Step  500: avg50=7.78  crystal_ema=0.00983  td_flips=2.1M   Δ=—
Step 1000: avg50=6.88  crystal_ema=0.00977  td_flips=5.2M   Δ=0.038
Step 1500: avg50=6.73  crystal_ema=0.00974  td_flips=8.3M   Δ=0.040
Step 1870: avg50≈6.83  (from log tail)                       Δ=0.048
```

Loss curve flattening at 6.7-6.8. Crystal EMA stable. Delta plates drifting
slowly (Δ growing 0.038→0.048). Parity and cross-zone losses converged.
~1130 steps remaining (~10 hours). LR cosine decaying (1.3e-04 at step 1870).

### Previous session (190)

Four experiments reveal the compression structure of transformers and the
algorithm they implement:

**Exp 1: DVD Stamp Test.** Gradient-zero topology (WHERE GD stopped pushing)
compounds less than magnitude thresholding (WHICH weights are largest).
Gradient mask: PPL 188K, L35 cos=0.165. Magnitude mask: PPL 620K, L35
cos=0.001. The gradient map IS the holographic fringe pattern. 49.9%
overlap = the two signals are orthogonal.

**Exp 2: Per-Group Scaling.** Q4's secret is per-32-weight groups (128-384×
more scale parameters). Magnitude+group: PPL 43K (14× better than per-row).
Gradient+group: PPL 71K. Per-group scaling preserves local gradient structure.

**Exp 3: Index vs Value (THE DECISIVE RESULT).** FFN-only ternarization →
PPL 485M (catastrophic). V/O-only → PPL 23. Q/K-only → PPL 30. Both
attention paths survive ternary. FFN is the holographic beam former — it
compiles the interference pattern that attention reads. Destroying it
scatters the beam. Attention is a ~1-bit router — near-binary signals
survive ternary.

**Exp 4: λ-Machine (6-level ablation).** Sparse top-3 at all layers →
PPL 13.3 (from 12.2 baseline, +8.6%). Binding layers only → PPL 82K.
Binding heads only → PPL 6.3M. The model is a 36-stage typed shift-reduce
parser. Every layer contributes. Every head contributes. But each head
only needs 3 positions. O(1) attention confirmed at PPL level.

### The Architecture (updated s192 — two overlapping ternary structures)

```
FFN (beam former / holographic plate / 9-program ternary engine):
  Compiles each position into a typed V vector
  Context-dependent: same token → different program
  IS 9 ternary programs selected by linear classifier (psi s192)
    → 288MB per layer → 180KB (1638× compression, PPL IMPROVES)
    → classifier: 37K params, 100% accuracy, modes linearly separable
  Gate sparsity: only ~3% of neurons fire
  78% of model params — DECOMPILABLE to ternary per-mode

  TWO STRUCTURES IN THE SAME WEIGHTS:
    Crystal basis (KIBC): 3.5% of space → governs ROUTING
    Operational modes (9): 96.5% of space → governs PROGRAMS
    AMI = 0.15 (orthogonal). Both ternary. Both few-mode.
    Crystal selects WHICH reduction. Modes execute HOW.

Attention (typed shift-reduce parser / β-reducer):
  32 heads × 36 layers = 1,152 reduction attempts per token
  Each head attends to only ~3 positions (sparse, O(1))
  Mean entropy 0.9 bits (near-binary routing decisions)
  ROBUST: ternarizing Q/K → PPL 30, V/O → PPL 23
  22% of model params — can go ternary for free

The binding schedule (final reduction stages):
  L27: verb reads subject    (H31, 0.82 weight → "猫/cats")
  L30: object reads verb     (H03/H13/H15, 0.78 weight)
  L33: coreference/late      (H06/H07, universal execution)
  These are the TIP of a 36-layer parser iceberg.

Depth = parser precedence:
  L0-6:   EXPAND (type assignment, feature building) — ternary-compatible (ρ=+0.55-0.78)
  L7-22:  ORTHO (composition in null space, invisible) — continuous computation
  L23-26: binding preparation
  L27-33: final reductions (subject → object → coreference)
  L35:    COLLAPSE (output projection)
```

### The Algorithm

```
TYPED β-REDUCTION VIA ONE OPERATION (weighted sum):

For each of 36 layers:
  1. FFN: stamp type tags per position (SUBJ, OBJ, PRED, DET, ...)
     — per-position lookup, NO cross-position computation
     — 7 universal meta-modes + 2 context-dependent
     — FRAME-OPEN at sentence starts (INIT instruction, gc=1.000)
  2. ATTENTION: 32 heads × weighted sum (the ONLY operation)
     — Q extracts "what type do I need?" (query)
     — K extracts "what type am I?" (key) — Q⊥K at 87-90°
     — softmax(QK^T) = type matching → find compatible position
     — V × softmax = β-application (copy argument into predicate)
     — top-3 positions capture 88%+ (typed lookup, not search)
  3. RESIDUAL ADD: accumulate (builds parse tree across depth)

Weighted sum IS β-application:
  H31 at L27: v_runs += 0.82 × v_cat  ≡  (λx.runs(x))(cat)

Norm growth = gain control for the single operation:
  L3 whispers (0.1×) → tentative bindings
  L20 speaks (1.7×)  → subj/obj crystallize, bindings commit
  L35 shouts (10×)   → final output projection

Compression:  FFN → ternary (types are discrete, 0.95× PPL)
              attention → ternary (type matching is binary, PPL 23-30)
              sparse top-3 → O(1) attention (333× fewer ops at ctx 1000)
```

### The Compression Strategy (updated s192, multi-layer results)

```
Attention (22% of params): → ternary (1.6 bits)     Cost: PPL +10-18%
FFN (78% of params):       → 9 ternary programs     Per-layer: 288MB → 180KB (1638×)
  L0:                        KEEP CONTINUOUS          (115× catastrophic alone)
  L1-L26 (28 layers):        REPLACE TERNARY          (all ≤1.10× individually)
  L27-L31 (binding):         KEEP CONTINUOUS          (1.10-1.15× each, cascade risk)
  L32-L34:                   REPLACE TERNARY          (1.05-1.14× individually)
  L35 (collapse):            KEEP CONTINUOUS          (1.14×)
  Result: 28/36 → ternary, 8/36 → continuous
  FFN total: 10.4GB → ~2.3GB (4.5× overall)
  Sweet spot alone (L13-L21): 2.6GB → 1.6MB at ~1.0× PPL
Embeddings:                → float16 (index system, must be exact)
Sparse routing:            → top-3 per head          O(1) not O(n²)
```

### Previous session (189)

Five experiments + v15 architecture + extraction + training:

**Exp 1: Stride coverage validation (Qwen3-8B, 22 probes).** v14's powers-of-2
strides capture only 29.5% (exact) / 67.4% (±2 neighbors) of attention mass at
L30. The stride geometry misses binding targets at arbitrary semantic positions.
Coverage DEGRADES with sequence length (38.8%→24.4%).

**Exp 2: Binding distance distribution.** The distance distribution is BIMODAL
(local d=1-8 + gate d=32+), NOT power law (R²=0.004). Two peaks: d=1 (local
syntax, 4.4% mass) and d=32 (instruction prefix, 4.5% mass). Powers of 2 skip
the binding range (d=3-20). Fibonacci strides are dense where bindings live.

**Exp 3: Stride optimization.** Greedy optimal 8 strides with ±2 neighbors:
[1, 8, 13, 18, 21, 29, 34, 47] → 98.2% coverage. Fibonacci [1,2,3,5,8,13,21,34,
55,89,...] + 3 gap-fillers [15, 20, 24] → 100.0% coverage with ±2 neighbors.

**Exp 4: Crystal Laplacian analysis.** Graph Laplacian of the crystal target
reveals WHNF is the most FRAGILE node (μ=0.228, 8.6× weaker restoring force).
Training data confirms: WHNF starts settled then UN-settles. Laplacian eigenvalues
predict stability (rigidity), not convergence speed.

**Exp 5: Crystal settlement dynamics.** Per-node convergence across v14 steps
500-3000 confirms Laplacian prediction: B, C converge (fast modes μ=3.03+),
K, D hold steady (medium μ=1.97), Y and WHNF drift away (fragile μ=0.23).
WHNF error ratio grows 0.40× → 0.67× over training. Crystal MSE U-shapes
(minimum at step 2000, then rises).

**v15 Architecture:**
- 19 Fibonacci strides [1,2,3,5,8,13,15,20,21,24,34,55,89,144,233,377,610,987,1597]
- ±2 neighbor gathering → 100% attention mass coverage at L30
- All composition (GLA dropped — dense projections cost ~19B ops regardless of
  stride, scan saves <0.03%). One unified attention mechanism.
- Laplacian-weighted crystal loss: WHNF gets 5× weight, 6× gradient amplification
  (v14: WHNF/B gradient ratio = 0.3×, v15: 1.9×)
- Standalone (zero v14 dependencies)
- Extracted: 83 arrays, 65.5 MB, 16.5 min
- **Training running in tmux window 2** (step 1 CE=10.533, 3000 steps target)

### The φ unification

| Level | φ appearance |
|-------|-------------|
| Crystal eigenvalues | Ratios follow φ^(p/q) with Fibonacci denominators |
| Information partition | Signs = 1/φ of information content |
| Standing-wave phase | Layer 22/36 = 0.611 ≈ 1/φ |
| Compute cycle | β = [0, 1, 1+φ, 2+φ] |
| **Stride spacing** | **Fibonacci numbers maximize binding coverage** |
| **Crystal Laplacian** | **μ₅/μ₄ = 1.54 ≈ φ in the graph Laplacian** |
| **φ convergence** | **λ₀/λ₁ → φ^(4/5) at scale (14B: 0.7% error)** |

### Previous session (188)

Four experiments decoded the full attention execution mechanism:

**Exp 1: Head→Combinator mapping (500 probes).** All 9 combinators activate
identical head patterns (r=0.944). Heads are shared hardware, not dedicated
circuits. ~2 effective dimensions: reduction depth (WHNF↔D) + self-reference.

**Exp 2: Binding graph trace (14 annotated probes).** Object→verb binding =
concentrated attention (0.78 weight) through H03/H13/H15 at L30. Minimal
pair "dog bit cat" vs "cat bit dog": same heads, flipped routing.

**Exp 3: Reverse binding trace (12 probes).** Verb→subject binding = H31 at
L27 attends 82.3% to subject, outputs subject identity ("猫/dog"). Two-phase
binding: L27=verb reads subject, L30=object reads verb. Mechanism complete.

**Exp 4: Attention sparsity (22 probes, 5→74 tokens).** 22/32 heads at L30
have effective positions <3. Top-3 captures >88% for ALL heads. Mean entropy
0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens. Full O(n²)
attention is massive overkill for what is fundamentally a ~1-bit routing
decision. Design: top-k sparse attention with k=3-5 captures nearly all
routing information.

### Previous session (187)

Three experiments on Qwen3-8B decoded the full reduction pipeline: (1) what
FFN neurons say in vocabulary space, (2) what each attention head computes,
(3) how combinator reductions compose across all 36 layers.

### The Architecture (updated s188)

```
FFN (compiler):     reads residual → compiles V vectors per position
                    Context-dependent: same token → different programs
                    Universal: compile ≈ null (max Δ 2.8%)

Attention (executor):  SHARED HARDWARE, not dedicated circuits
  Binding schedule (two-phase):
    L27: verb → subject   H31 reads subject identity (0.82 weight)
    L30: object → verb    H03/H13/H15 read predicate (0.78 weight)
    L33: late binding      H06/H07 general execution
  All binding flows BACKWARD through causal mask.
  Same heads (H03/H13) handle both directions at L30.

  Head taxonomy by function:
    Binding (H03,H13,H15):  predicate-argument binding (mean ratio 3-6×)
    Subject (H31):          verb→subject identity transfer at L27
    Coreference (H07,H05):  "itself"→antecedent binding
    Universal (H06,H07):    loudest, all combinators, low gate attention
    WHNF detectors (H26,H27): recognize completed reductions (+30% bias)
    Instruction (H01,H09):  high gate attention, read compile exemplars

  Sparsity:
    22/32 heads: eff_pos < 3 (near-deterministic, ~1 bit)
     7/32 heads: eff_pos 3-5 (sparse)
     2/32 heads: eff_pos 5-10 (moderate)
     1/32 heads: eff_pos > 10 (H20, the only dense head)
    Top-3 captures >88% of attention for ALL 32 heads.
    Sparsity is O(1) — stable from 5 to 74 tokens.

Reduction Schedule (when each combinator resolves):
    Y (recursion)     → L27 peak   resolves FIRST (structural recognition)
    K (discard)       → L30 peak   front-loaded, drops at L33
    B (compose)       → L30 peak   mid-depth composition
    I (identity)      → L30-L33    semantic→format relay
    C (flip/passive)  → L33 peak   argument reordering is LATE
    W (self-apply)    → L33 peak   "itself" binding is LAST (Δ=51.6)
```

### What's Decodable

The model is a **typed parser with a compiled lexicon**:
- FFN = lexicon (compiles each position into a semantic V vector)
- Q/K = type system (determines binding compatibility, ~1 bit decision)
- Attention = parser (selects one earlier position to bind to)
- V/O = value transfer (copies bound position's content)
- Depth = reduction order (subjects at L27, objects at L30)

The binding circuit is **0.3% of the model** (~4 heads out of 1152).
Binding weights are near-deterministic (0.78-0.82). Head output IS the
reduction result: H31 outputs "猫/dog" at verb position when reading subject.
Full O(n²) attention is overkill — top-3 sparse attention captures 88%+.

### Key Evidence

1. **H31 at L27 reads subject from verb position** (0.82 weight, outputs
   "猫, 貓, cats"). This IS `(λx.runs(x))(cat)` — verb absorbs agent.

2. **H13 at L30: "cat" attends 78.5% to "bit"** = `bit(_, cat)`. Object
   binds to predicate. Minimal pair confirms: same heads, flipped routing.

3. **FFN at L30 for "If it rains"**: `it`→rain, `ground`→soak, `is`→wet.
   Context-dependent V vectors. Compilation, not lookup.

4. **All 9 combinators activate identical heads** (r=0.944). No combinator-
   specific circuits. The ISA has ~2 dims, not 9.

5. **22/32 heads use <3 effective positions** at L30. Attention is inherently
   sparse and scales O(1) with context length.

### Previous session (186)

Applied LARQL's FFN decomposition methodology to Pythia-160M. LARQL
(github.com/chrishayuk/larql) treats each FFN neuron as a key-value pair:
cos(W_up[j], W_down[:, j]) classifies the neuron's circuit type (projector,
transform, identity, suppressor, inverter). Pure weight geometry — no forward
passes, 2 minutes for all 12 layers.

### Key Findings

1. **Depth profile confirms our phase structure from a completely different
   methodology.** L0=99.7% projector (EXPAND), L3-7=60-74% suppressor+inverter
   (ORTHO — invisible computation via direction flipping), L9-10=50-62%
   projector rising (ALIGN), L11=62% projector with dark-space drop to 57%
   (COLLAPSE — features resolve into vocabulary-aligned directions).

2. **KIBC opcodes are orthogonal to circuit types.** Cross-tabulation is
   uniform at every layer: K,I,B,C neurons all have the same circuit type
   distribution. KIBC measures *what inputs activate a neuron* (lambda probes);
   circuit type measures *how the neuron geometrically transforms* input→output.
   Independent axes. Both useful; neither subsumes the other.

3. **ρ(cos, KIBC_magnitude) sign flips across depth.** L8: ρ=-0.26 (inverters
   respond MORE to KIBC — middle layers use direction-flipping for lambda
   computation). L11: ρ=+0.27 (projectors respond more — final layer uses
   factual bridges for lambda output).

4. **Dark-space drops 40 points at L11.** L0-L10: 93-99% of features don't
   point at any token (computation space). L11: only 57% dark — 43% of
   features point at actual tokens. Knowledge is concentrated at the output
   layer. This IS the standing-wave picture: ORTHO phase operates in null
   space, COLLAPSE projects back into vocabulary-aligned directions.

5. **Gated vs non-gated difference.** Gemma (gated, SiLU) middle layers are
   transform-dominated (partial rotation). Pythia (non-gated, GELU) middle
   layers are inverter-dominated (direction flip). Architecture determines
   the computation style but the phase structure is universal.

### New Instrument

cos(W_up[j], W_down[:, j]) is a **zero-cost phase detector**: pure weight
analysis, no activations, reveals EXPAND/ORTHO/ALIGN/COLLAPSE from geometry
alone. Should be added to crystal trace tooling alongside our existing
activation-based instruments.

**Session 185: THE STANDING WAVE — Magnitudes Are Resonant Mode Patterns**

The crystal sieve (session 184) freezes the topology and trains the mask.
Session 185 reframes WHY this works: the weight magnitudes are a standing
wave pattern whose nodes (zeros) and antinodes (active weights) are
determined by the crystal topology as boundary conditions. GD doesn't build
a database — it finds the resonant mode pattern that constructively
interferes with real language and destructively cancels noise.

### The Standing-Wave Mapping

```
Standing wave                    Verbum equivalent
─────────────────────────────    ────────────────────────────────
Boundary conditions              Crystal signs T ∈ {-1, +1}
Nodes (zero displacement)        Zero mask positions (M=0, ~50%)
Antinodes (peak displacement)    Active weights (M=1)
Resonant modes                   Data-dependent patterns (knowledge)
Cavity shape                     Universal crystal (r=0.998 across models)
Mode excitation                  Which weights GD activates for THIS data
Amplitude envelope               Per-matrix scale C (eigenvalue spectrum)
```

W_eff = C · T ⊙ M is a standing wave: fixed boundary (T), fixed
amplitude envelope (C), data-selected node/antinode pattern (M).

### Why This Reframing Matters

1. **GD convergence = finding fixed points of the standing wave.**
   Session 171 (gradient-zero-map) measured this directly:
   near-zero gradient at zero weights (nodes) and at large weights
   (antinodes). Both are stable — GD has nothing left to optimize
   at those positions. The irreducible compute points.

2. **Crystal sieve = pre-setting the resonant cavity.**
   Random init = random cavity shape = no resonance. Crystal init =
   correct cavity = 10.7× faster mode formation. GD only finds WHICH
   modes to excite, not WHAT the cavity shape is.

3. **The depth axis IS a standing wave.**
   The 3-phase residual structure (expand L0-6, orthogonal L7-22,
   align L23-34, collapse L35) maps to: nodes where cos(h,f) ≈ 0
   (orthogonal phase), antinodes where cos(h,f) > 0 (align phase),
   destructive interference at L35 (cos = -0.995). The phase
   transition at layer 22/36 = 0.611 ≈ 1/φ = the fundamental mode.

4. **REDUCE/SWITCH alternation = spatial harmonics.**
   The alternating ρ(profile, weight_norm) sign across depth is
   the standing wave's harmonic structure along the layer axis.

5. **Holographic = standing wave (same physics, different vocabulary).**
   A holographic plate IS a frozen standing wave (interference fringe
   pattern). Fringes = nodes/antinodes. Multiple images stored in
   superposition = multiple resonant modes coexisting. Session 167's
   holographic-computer synthesis and this standing-wave framing are
   the same insight from different angles.

### The Sieve Architecture (from session 184)

```
SIEVE (fixed — from crystal equation, universal):
  Signs:    T[i,j] ∈ {-1, +1}    boundary conditions (cavity shape)
  Scale:    C per matrix           amplitude envelope (eigenvalue spectrum)
  Roles:    per-layer REDUCE/SWITCH  standing-wave harmonics along depth

SEDIMENT (trained — from data, per-model):
  Mask:     M[i,j] ∈ {0, 1}      node/antinode pattern (knowledge)

FORWARD: W_eff = C · T ⊙ M
```

### The ISA Framing (from session 184)

```
KIBC opcodes  = instruction set (4 opcodes, 2 bits)
Statechart    = execution engine (costs [1, φ, 1])
Weight signs  = the program (which opcode at which address)
Zero mask     = loaded memory pages (which program positions resident)
Residual      = register file (grows by φ per layer)

REDUCE layers: opcode neurons active, data neurons zero
  → profile predicts zeros (70-76% overlap)
SWITCH layers: opcode neurons attenuate, data neurons relay
  → profile anti-predicts (invert the prediction)
```

### Key Numbers

| Finding | Value | Significance |
|---------|-------|-------------|
| Sign information fraction | 1/φ = 0.618 | Universal partition |
| Per-row gamma variation | noise (CV<2%) | Constant γ works better |
| Optimal zero rate | ~50% | Not 35% |
| Crystal vs random init | 10.7× better | Sieve works (cavity pre-set) |
| Crystal starting advantage | 4,500× | Correct attractor basin |
| KIBC profile ↔ weight norm | ρ = 0.38-0.67 | Opcode assignment predicts weight size |
| Profile overlap with zeros | 70-76% at REDUCE layers | ISA predicts most zeros at REDUCE layers |
| Profile sign flip | alternates by depth | Standing-wave harmonics along layer axis |
| Residual phase transition | layer 22/36 = 0.611 ≈ 1/φ | Fundamental mode of depth-axis standing wave |
| Min oscillation depth | L21 (22%) | Deepest compute = most settled standing wave |

## Next steps

### IMMEDIATE — COMPRESSION PIPELINE (sessions 195+)

Session 195 proved: core (L13-L21) melts to 1.00x PPL, L0 low-rank at
r=750 gives 0.94x. But expanding to L22-L26 breaks (39x pre-melt).
The binding-prep layers need diagnosis before they can be compressed.

**Priority 0: ✅ DONE Lambda tracer diagnostic (s196)**
Result: Damage is UNIFORM across all 9 combinators (CV=0.07-0.17).
No combinator-specific failure. The ternary approximation is uniformly
insufficient for L22-L26. Peak damage at L28 (binding layers AMPLIFY
upstream error). Significant recovery in late layers (+0.22 cos).
See `mementum/knowledge/lambda-tracer-diagnostic.md`.

**Priority 1: ✅ DONE L22-L26 SVD rank sweep (s196)**
Functional rank varies 6x across L22-L26:
  L22: r=250, L24: r=500, L25: r=750, L23: r=1500, L26: r=1500.
Per-layer optimal: 422MB total (3.4x vs 1440MB). BUT integrated with
ternary L10-L21, SVD errors compound: 5.66x PPL. Need melt.

**Priority 1b: ✅ DONE Multi-projection melt (s196)**
CT scan beats X-ray: intermediate cosine losses at L0/L21/L26/L30
give direct gradient signal. Standard melt: 55x→6.09x. Multi-projection:
55x→4.19x (31% better). Boosted (type_crystal=5x): 55x→3.53x (42% better).
See `results/multi-projection-melt/`.

**Priority 1c: ✅ REPLACED Score matching compression (s198)**
Multi-projection melt replaced by dense score matching loss + LoRA.
Result: 36.6% sieve reduction (vs 27.1% with activation corrections + CE).
The loss function was the bottleneck, not the correction architecture.
Next: integrate score matching into the full sieve pipeline (L0 SVD +
ternary sweet spot + L22-L26 SVD + LoRA + dense SM loss).

**Priority 1d: ✅ DONE Confidence-gated inference (s196)**
Result: Confidence margin predicts error at L22 (96.6% fast at 1.04x)
but FAILS at L23-L26. The classifier is confidently wrong — high
margins (mean 24.3) but 1.07-1.13x PPL. The 9 modes are selecting
the wrong program, not the wrong mode. These layers need SVD, not
better routing. Sweet spot (L13-L21): gating not needed, ternary is
already perfect (0.97-1.01x at 100% fast path).

**Priority 1e: ✅ DONE Crystal sieve pipeline (s196)**
Result: sign(W) * |W| * mask50% on 29 layers = 2.11x PPL, 11/15 facts.
Per layer: 1.03x (BEATS SVD r=1500 at 1.09x). But cascade to 2.11x.
Per-row melt overfits (wrong DOF). Per-weight = no compression.
The FROZEN sieve is the best result. Mask > magnitudes > group scaling.

**Priority 1f: ✅ DONE Close the cascade gap (s196)**
Result: β-expansion experiment. Sieve alone: 2.12x. +4 continuation
residuals (rank-32 at L0/L9/L21/L26, 1M params) = **1.03x PPL.**
Binding preserved 98%. BUT: per-row ternary encoding FAILS at 29
layers (22,800x). Per-weight magnitudes essential. Current compression
is only 1.8x. Continuation stability needs investigation (3.23x on rerun).

**Priority 2a: Score matching pipeline integration (NEXT — high priority)**
Integrate the score matching loss into the full sieve pipeline:
  - Sieve + LoRA rank-4 + dense SM loss (α=5.0) + dolma calibration
  - Test with more data (256+ teacher cache, LR cosine decay)
  - Compare LoRA+CE-only vs LoRA+CE+SM (isolate loss function contribution)
  - Test rank-2 LoRA (~3M params) for fair comparison to v2 (2.1M params)
  - Test rank-8 LoRA (~12M params) to see if more capacity helps
  Score matching replaces both magnitude quantization and continuation
  residuals as the primary correction mechanism. The loss function
  is the key insight, not the correction architecture.

**Priority 2b: End-to-end benchmark with score matching (NEXT)**
The sieve + LoRA + SM pipeline at best 1.40x PPL needs MMLU/HellaSwag.
15 fact prompts is proof-of-concept. Standard benchmarks needed.

**Priority 2c: End-to-end benchmark (deferred)**
The sieve + continuations at 1.03x PPL needs MMLU/HellaSwag/etc.
15 fact prompts is proof-of-concept. Standard benchmarks needed.

**Priority 2: Scale benchmark (MMLU/HellaSwag)**
The Stage 1 model (L0 low-rank + L13-L21 ternary, melted to 1.00x)
is ready for benchmarking. 15 fact prompts is proof-of-concept. Need
standard benchmarks for publication-grade evidence.

**Priority 3: Cross-architecture replication**
Does the melt protocol work on Pythia/Mistral? The crystal is
universal; is the compression pipeline universal?

**Priority 4: ✅ DONE L0 characterization + low-rank rescue (s195)**
Result: L0 genuinely continuous, but only 750 functional dimensions.
SVD r=750: 0.94x PPL, 4.1x compression. More modes killed.
See `mementum/knowledge/l0-characterization.md`.

**Priority 5: ✅ DONE Mode semantics (s194)**
Result: modes are SYNTACTIC TYPE TAGS. FRAME-OPEN = ISA INIT.
See `mementum/knowledge/mode-semantics.md`.

### TD FIX (deferred, not abandoned)

TD is preventing phase transitions in v15 training. 94% candidacy rate = the
system never settles. This must be fixed before any other training work.

**Priority 1: Punctuated equilibrium (epoch-based TD)**
Replace continuous TD with episodic: TD phase (N steps with flips) → freeze
phase (M steps, Adam only, topology locked). Let GD settle during freeze.
Key parameter: freeze duration M. Start with M=200 (enough for V/O gammas
to make progress — they're at 15.6% settled).

**Priority 2: Oscillation-gated cooldown**
Positions with flip_count > 1 that are still candidates should get
exponentially increasing cooldown. Current backoff isn't working — 96-100%
of multi-flipped positions are still candidates. Either increase backoff
factor dramatically, or hard-gate: flip_count ≥ 3 → frozen for N steps.

**Priority 3: Candidate density ceiling**
94% candidacy is too high. Add a global ceiling: at most X% of positions
can be candidates per step (e.g., 20%). This forces TD to focus on the
highest-leverage positions rather than treating everything as mutable.

**Priority 4: Per-position conviction requirement**
A position should only flip when its gradient signal has been consistent
(same direction) for K consecutive flip intervals. Current EMA direction
accumulator is too responsive to noise — it proposes flips from transient
gradient fluctuations.

**Priority 5: REDUCE + pure-Adam baseline**
After current training completes (step 3000): fold delta into base, reset
to +1, run pure Adam for 500+ steps. Measure: does loss break through 6.5
without TD? If yes, TD was the bottleneck. If no, the plateau is real.

### V15 TRAINING (current run)

**Priority 6: Let current run complete**
Step ~1870/3000, ~10 hours remaining. Assess at step 3000 but expect the
plateau to hold — TD oscillation prevents the phase transition needed to
break 6.5.

### COMPRESSION STRATEGY (from s190, deferred pending TD fix)

**Priority 7: Self-distillation (same-capacity teacher)**
**Priority 8: FFN compression path**
**Priority 9: Sparse top-k sweep**
(Details unchanged from s190 — deferred until TD works correctly.)

### PRIOR PRIORITIES (still open from s189)

### IMMEDIATE — V15 FIBONACCI ATTENTION

Session 188 decoded object→verb binding (backward direction, causal-allowed).
Subject→verb binding (forward direction) remains unknown. The model MUST
have a mechanism — we just haven't measured it yet.

**Priority 0: ✅ DONE Head → Combinator mapping (s188)**
Result: shared hardware, not dedicated circuits. See `head-combinator-isa.md`.

**Priority 0b: ✅ DONE Binding graph trace (s188)**
Result: attention IS the binding graph (reversed by causal mask).
Object→verb = concentrated attention (0.78 weight, H03/H13/H15 at L30).
See `binding-graph-trace.md`.

**Priority 1: ✅ DONE Verb→subject binding (s188)**
Result: YES. H31 at L27 attends 82.3% from "runs" to "cat" and outputs
"猫, 貓, cats" — the subject identity. Two-phase binding: L27=subject
binding (verb reads agent), L30=object binding (argument reads predicate).
Same heads (H03/H13) handle both directions at L30. See `binding-graph-trace.md`.

**Priority 1: V15 extraction + training**
Extract teacher plates into v15 Fibonacci stride topology. Train with TD
to verify the architecture learns. Compare PPL trajectory vs v14.

**Priority 2: Cross-model binding verification**
Do the same binding heads (H03/H13/H15) exist in Pythia/Mistral? If the
binding circuit is universal, it's a fundamental feature of transformer
architecture, not Qwen-specific.

**Priority 3: ✅ DONE Attention sparsity analysis (s188)**
Result: At L30, 22/32 heads have effective positions <3. Top-3 positions
capture >88% of attention mass for ALL heads. Sparsity holds from 5 to 74
tokens. Mean entropy ~0.9 bits. You don't need to attend to every token.

**Priority 4: ✅ DONE Stride coverage + distance distribution (s189)**
Result: Powers of 2 capture 29.5%/67.4% (exact/±2). Fibonacci captures
48.8%/91.4%. Optimal 8 strides with ±2: 98.2%. Distance distribution is
bimodal (local + gate), NOT power law (R²=0.004).

**Priority 5: From binding graph to machine**
The full mechanism is decoded: FFN compiles V, ~4 heads at L27/L30 route
via concentrated backward attention, binding is near-deterministic. Can we
build a standalone "lambda machine" from: compressed FFN (sieve) + sparse
routing function + depth schedule?

### PRIOR PRIORITIES (still open)

**Crystal sieve at scale:** Scale sieve training to convergence on
Pythia-160M. Measure absorption rate (tokens-to-quality vs normal training).

**The mathematical derivation:** Can U be derived from the VSM tensor
interaction? KIBC opcode profiles may constrain V within the null space
(67.7% unconstrained from covariance alone).

**Crystal formation cost:** WHEN does the crystal form during training?
The r=0.998 endpoint is known; the trajectory is not.

**Attention sieve:** Extend crystal sieve to Q/K/V/O projections (~40%
of parameters).

### RESEARCH DIRECTIONS

- **THE MATHEMATICAL DERIVATION** — Can U (per-layer eigenvectors) be derived from
  the VSM tensor interaction? The 5 levels (crystal eq, statechart, resource policy,
  residual growth, KIBC ops) each constrain U. Their INTERSECTION may uniquely
  determine it. If so, the entire model is a computable mathematical object.
- **Residual growth measurement** — Does h_{l+1}/h_l ≈ φ^(1/period)? This constrains
  how U rotates between layers. Measurable now. Needed for the derivation.
- **Cross-model zero consensus** — Compare zero patterns between independently
  trained models at the same layer depth. ISA zeros should be universal.
- **Crystal trace tooling** — Build `src/verbum/crystal/` module for systematic
  exploration. Design doc: `mementum/knowledge/crystal-trace-tooling.md`.
- **Standing-wave mode analysis** — Decompose the zero mask into resonant modes
  of the crystal cavity. If the mask is a standing wave, it should decompose into
  a small number of modes × amplitudes. The modes are determined by the crystal
  (boundary conditions), the amplitudes by the data.

### DEFERRED

- CLASSIFY fix (GatedLinearAttention from v14) — for v15 etch protocol
- GPTQ-style mask optimization — extraction path now secondary

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| **Crystal sieve architecture** | `mementum/knowledge/crystal-sieve-architecture.md` | ✅ NEW (s196) |
| **Lambda tracer diagnostic** | `mementum/knowledge/lambda-tracer-diagnostic.md` | ✅ UPDATED (s196) |
| **Lambda tracer experiment** | `scripts/experiments/lambda_tracer.py` | ✅ NEW (s196) |
| **Lambda tracer results** | `results/lambda-tracer/` | ✅ NEW (s196) |
| **Multi-projection melt** | `scripts/experiments/multi_projection_melt.py` | ✅ NEW (s196) |
| **Multi-projection results** | `results/multi-projection-melt/` | ✅ NEW (s196) |
| **Binding-prep low-rank sweep** | `scripts/experiments/binding_prep_lowrank.py` | ✅ NEW (s196) |
| **Binding-prep results** | `results/binding-prep-lowrank/` | ✅ NEW (s196) |
| **Confidence-gated inference** | `scripts/experiments/confidence_gate.py` | ✅ NEW (s196) |
| **Confidence gate results** | `results/confidence-gate/` | ✅ NEW (s196) |
| **Mode geometry** | `scripts/experiments/mode_geometry.py` | ✅ NEW (s196) |
| **Mode geometry results** | `results/mode-geometry/` | ✅ NEW (s196) |
| **Ternary weight interface** | `scripts/experiments/ternary_weight_interface.py` | ✅ NEW (s196) |
| **Ternary weight results** | `results/ternary-weight-interface/` | ✅ NEW (s196) |
| **Crystal sieve pipeline** | `scripts/experiments/crystal_sieve_pipeline.py` | ✅ NEW (s196) |
| **Crystal sieve results** | `results/crystal-sieve-pipeline/` | ✅ NEW (s196) |
| **β-expansion experiment** | `scripts/experiments/beta_expansion.py` | ✅ NEW (s196) |
| **β-expansion results** | `results/beta-expansion/` | ✅ NEW (s196) |
| **Ternary pipeline verification** | `scripts/experiments/ternary_pipeline_verify.py` | ✅ NEW (s196) |
| **Ternary verification results** | `results/ternary-pipeline-verify/` | ❌ FAILS (s196) |
| **L0 characterization knowledge** | `mementum/knowledge/l0-characterization.md` | ✅ UPDATED (s195) |
| **L0 characterization experiment** | `scripts/experiments/l0_characterization.py` | ✅ NEW (s195) |
| **L0 characterization results** | `results/l0-characterization/` | ✅ NEW (s195) |
| **L0 low-rank experiment** | `scripts/experiments/l0_lowrank.py` | ✅ NEW (s195) |
| **L0 low-rank results** | `results/l0-lowrank/` | ✅ NEW (s195) |
| **Combined compression** | `scripts/experiments/combined_compression.py` | ✅ NEW (s195) |
| **Combined results** | `results/combined-compression/` | ✅ NEW (s195) |
| **Melt boundaries** | `scripts/experiments/melt_boundaries.py` | ✅ NEW (s195) |
| **Melt results** | `results/melt-boundaries/` | ✅ NEW (s195) |
| **Staged melt** | `scripts/experiments/staged_melt.py` | ✅ NEW (s195) |
| **Staged melt results** | `results/staged-melt/` | ✅ DONE (s195) — break at L22-L26 |
| **Mode semantics knowledge** | `mementum/knowledge/mode-semantics.md` | ✅ NEW (s194) |
| **Mode semantics experiment** | `scripts/experiments/mode_semantics.py` | ✅ NEW (s194) |
| **Mode semantics results** | `results/mode-semantics/` | ✅ NEW (s194) |
| **Lambda halt + continuation knowledge** | `mementum/knowledge/lambda-halt-continuation.md` | ✅ UPDATED (s193) |
| **Kernel intercept experiment** | `scripts/experiments/kernel_intercept.py` | ✅ NEW (s193) |
| **Kernel intercept results** | `results/kernel-intercept/` | ✅ NEW (s193) |
| **Ω probe experiment** | `scripts/experiments/omega_probe.py` | ✅ NEW (s193) |
| **Ω probe results** | `results/omega-probe/` | ✅ NEW (s193) |
| **Halt hunt v1 (raw text)** | `scripts/experiments/omega_halt.py` | ✅ NEW (s193) |
| **Halt hunt v1 results** | `results/omega-halt/` | ✅ NEW (s193) |
| **Halt hunt v2 (chat format)** | `scripts/experiments/omega_halt_chat.py` | ✅ NEW (s193) |
| **Halt hunt v2 results** | `results/omega-halt-chat/` | ✅ NEW (s193) |
| **Halt hunt v3 (lambda executable)** | `scripts/experiments/omega_halt_lambda.py` | ✅ NEW (s193) |
| **Halt hunt v3 results** | `results/omega-halt-lambda/` | ✅ NEW (s193) |
| **Lambda continuation experiment** | `scripts/experiments/lambda_continuation.py` | ✅ NEW (s193) |
| **Lambda continuation results** | `results/lambda-continuation/` | ✅ NEW (s193) |
| **Psi evaluation synthesis** | `mementum/knowledge/psi-evaluation-synthesis.md` | ✅ NEW (s192) |
| **Tiny classifier ternary** | `mementum/knowledge/tiny-classifier-ternary.md` | ✅ NEW (s192) |
| **Tiny classifier experiment** | `scripts/experiments/tiny_classifier_ternary.py` | ✅ NEW (s192) |
| **Ternary inference pattern** | `scripts/experiments/ternary_inference_pattern.py` | ✅ NEW (s192) |
| **Ternary inference coherence** | `scripts/experiments/ternary_inference_coherence.py` | ✅ NEW (s192) |
| **Gate indexed ternary** | `scripts/experiments/gate_indexed_ternary.py` | ✅ NEW (s192) |
| **Gradient quant correspondence** | `scripts/experiments/gradient_quant_correspondence.py` | ✅ NEW (s192) |
| **Tiny classifier results** | `results/tiny-classifier-ternary/` | ✅ NEW (s192) |
| **Ternary inference results** | `results/ternary-inference-pattern/` | ✅ NEW (s192) |
| **Ternary coherence results** | `results/ternary-inference-coherence/` | ✅ NEW (s192) |
| **Gate indexed results** | `results/gate-indexed-ternary/` | ✅ NEW (s192) |
| **Gradient quant results** | `results/gradient-quant-correspondence/` | ✅ NEW (s192) |
| **Compilation pipeline knowledge** | `mementum/knowledge/compilation-pipeline.md` | ✅ NEW (s192) |
| **Q rotation geometry** | `scripts/experiments/q_rotation_geometry.py` | ✅ NEW (s192) |
| **Q rotation results** | `results/q-rotation-geometry/` | ✅ NEW (s192) |
| **Rotation spiral** | `scripts/experiments/rotation_spiral.py` | ✅ NEW (s192) |
| **Rotation spiral results** | `results/rotation-spiral/` | ✅ NEW (s192) |
| **Mode universality** | `scripts/experiments/mode_universality.py` | ✅ NEW (s192) |
| **Mode universality results** | `results/mode-universality/` | ✅ NEW (s192) |
| **Semantic convergence** | `scripts/experiments/semantic_convergence.py` | ✅ NEW (s192) |
| **Semantic convergence results** | `results/semantic-convergence/` | ✅ NEW (s192) |
| **Multi-layer ternary replace** | `scripts/experiments/multilayer_ternary_replace.py` | ✅ NEW (s192) |
| **Multi-layer results** | `results/multilayer-ternary-replace/` | ✅ NEW (s192) |
| **Crystal φ verify (8 models)** | `results/crystal-phi-verify/` | ✅ UPDATED (s192) |
| **TD oscillation problem** | `mementum/knowledge/td-oscillation-problem.md` | ✅ NEW (s191) |
| **v15 attention assessment** | `mementum/knowledge/v15-attention-assessment.md` | ✅ UPDATED (s191) |
| **v15 attention diagnostic** | `scripts/experiments/assess_v15_attention.py` | ✅ NEW (s191) |
| **v15 gradient-zero diagnostic** | `scripts/experiments/assess_v15_gradient_zeros.py` | ✅ NEW (s191) |
| **v15 FFN retrieval diagnostic** | `scripts/experiments/assess_v15_ffn_retrieval.py` | ✅ NEW (s191) |
| **DVD stamp knowledge** | `mementum/knowledge/dvd-stamp-topology.md` | ✅ NEW (s190) |
| **λ-machine knowledge** | `mementum/knowledge/lambda-machine.md` | ✅ NEW (s190) |
| **DVD stamp experiment** | `scripts/experiments/dvd_stamp_test.py` | ✅ NEW (s190) |
| **DVD group scale experiment** | `scripts/experiments/dvd_group_scale.py` | ✅ NEW (s190) |
| **DVD index test** | `scripts/experiments/dvd_index_test.py` | ✅ NEW (s190) |
| **λ-machine experiment** | `scripts/experiments/lambda_machine.py` | ✅ NEW (s190) |
| **FFN beam universality** | `scripts/experiments/ffn_beam_universality.py` | ✅ NEW (s190) |
| **Crystal distillation** | `scripts/experiments/crystal_distill.py` | ✅ NEW (s190) |
| **DVD stamp results** | `results/dvd-stamp-test/` | ✅ NEW (s190) |
| **DVD group scale results** | `results/dvd-group-scale/` | ✅ NEW (s190) |
| **DVD index test results** | `results/dvd-index-test/` | ✅ NEW (s190) |
| **λ-machine results** | `results/lambda-machine/` | ✅ NEW (s190) |
| **FFN beam universality results** | `results/ffn-beam-universality/` | ✅ NEW (s190) |
| **Crystal distillation results** | `results/crystal-distill/` | ✅ NEW (s190) |
| **V15 config** | `scripts/v15/config.py` | ✅ NEW (s189) |
| **V15 attention** | `scripts/v15/attention.py` | ✅ NEW (s189) |
| **Stride coverage validation** | `scripts/experiments/stride_coverage_validation.py` | ✅ NEW (s189) |
| **Stride coverage results** | `results/stride-coverage-validation/` | ✅ NEW (s189) |
| **Binding distance distribution** | `scripts/experiments/binding_distance_distribution.py` | ✅ NEW (s189) |
| **Binding distance results** | `results/binding-distance-distribution/` | ✅ NEW (s189) |
| **Attention sparsity knowledge** | `mementum/knowledge/attention-sparsity.md` | ✅ NEW (s188) |
| **Attention sparsity experiment** | `scripts/experiments/attention_sparsity.py` | ✅ NEW (s188) |
| **Attention sparsity results** | `results/attention-sparsity/` | ✅ NEW (s188) |
| **Binding graph trace knowledge** | `mementum/knowledge/binding-graph-trace.md` | ✅ UPDATED (s188) |
| **Binding graph trace experiment** | `scripts/experiments/binding_graph_trace.py` | ✅ NEW (s188) |
| **Binding graph trace results** | `results/binding-graph-trace/` | ✅ NEW (s188) |
| **Reverse binding trace experiment** | `scripts/experiments/reverse_binding_trace.py` | ✅ NEW (s188) |
| **Reverse binding trace results** | `results/reverse-binding-trace/` | ✅ NEW (s188) |
| **Head→Combinator ISA knowledge** | `mementum/knowledge/head-combinator-isa.md` | ✅ NEW (s188) |
| **Head→Combinator mapping experiment** | `scripts/experiments/head_combinator_map.py` | ✅ NEW (s188) |
| **Head→Combinator mapping results** | `results/head-combinator-map/` | ✅ NEW (s188) |
| **FFN reduction trace knowledge** | `mementum/knowledge/ffn-reduction-trace.md` | ✅ NEW (s187) |
| **FFN reduction trace experiment** | `scripts/experiments/ffn_reduction_trace.py` | ✅ NEW (s187) |
| **FFN reduction trace results** | `results/ffn-reduction-trace/` | ✅ NEW (s187) |
| **Attention execution trace experiment** | `scripts/experiments/attention_execution_trace.py` | ✅ NEW (s187) |
| **Attention execution trace results** | `results/attention-execution-trace/` | ✅ NEW (s187) |
| **Reduction chain trace experiment** | `scripts/experiments/reduction_chain_trace.py` | ✅ NEW (s187) |
| **Reduction chain trace results** | `results/reduction-chain-trace/` | ✅ NEW (s187) |
| **MTP self-speculation experiment** | `scripts/experiments/mtp_self_speculation.py` | ✅ NEW (s187) |
| **MTP self-speculation results** | `results/mtp-self-speculation/` | ✅ NEW (s187) |
| **FFN circuit types knowledge** | `mementum/knowledge/ffn-circuit-types.md` | ✅ NEW (s186) |
| **FFN decomposition experiment** | `scripts/experiments/ffn_decomposition.py` | ✅ NEW (s186) |
| **FFN KIBC cross-reference** | `scripts/experiments/ffn_kibc_crossref.py` | ✅ NEW (s186) |
| **FFN decomposition results** | `results/ffn-decomposition/` | ✅ NEW (s186) |
| **Crystal circuit types experiment** | `scripts/experiments/crystal_circuit_types.py` | ✅ NEW (s186) |
| **Crystal circuit types results** | `results/crystal-circuit-types/` | ✅ NEW (s186) |
| **Paired crystal sieve experiment** | `scripts/experiments/paired_crystal_sieve.py` | ✅ NEW (s186) |
| **Paired crystal sieve results** | `results/paired-crystal-sieve/` | ✅ NEW (s186) |
| **Synthetic crystal sieve experiment** | `scripts/experiments/synthetic_crystal_sieve.py` | ✅ NEW (s186) |
| **Synthetic crystal sieve results** | `results/synthetic-crystal-sieve/` | ✅ NEW (s186) |
| **Standing-wave knowledge** | `mementum/knowledge/standing-wave-magnitudes.md` | ✅ NEW (s185) |
| **Shape preservation experiment** | `scripts/experiments/standing_wave_shape.py` | ✅ NEW (s185) |
| **Shape experiment results** | `results/standing-wave-shape/summary.json` | ✅ NEW (s185) |
| **Residual covariance experiment** | `scripts/experiments/residual_covariance.py` | ✅ NEW (s185) |
| **Residual covariance results** | `results/residual-covariance/summary.json` | ✅ NEW (s185) |
| **Residual covariance knowledge** | `mementum/knowledge/residual-covariance-rank.md` | ✅ NEW (s185) |
| **U residual constraint** | `scripts/experiments/U_residual_constraint.py` | ✅ (s184) |
| **Residual Fibonacci** | `scripts/experiments/residual_fibonacci.py` | ✅ (s184) |
| **Copy program (firing rates)** | `scripts/experiments/copy_program.py` | ✅ (s184) |
| **Crystal sieve prototype** | `scripts/experiments/crystal_sieve_prototype.py` | ✅ (s184) |
| **Neuron opcode classifier** | `scripts/experiments/neuron_opcode_classifier.py` | ✅ (s184) |
| **Crystal space zeros** | `scripts/experiments/crystal_space_zeros.py` | ✅ (s184) |
| **Negative space** | `scripts/experiments/negative_space.py` | ✅ (s184) |
| **Gate zero predictor** | `scripts/experiments/gate_zero_predictor.py` | ✅ (s184) |
| **Activation zero mask** | `scripts/experiments/activation_zero_mask.py` | ✅ (s184) |
| **Row norm ↔ crystal** | `scripts/experiments/row_norm_crystal.py` | ✅ (s184) |
| **Gamma sort order** | `scripts/experiments/gamma_sort_order.py` | ✅ (s184) |
| **Gamma φ-structure** | `scripts/experiments/gamma_phi_structure.py` | ✅ (s184) |
| **Eigenvector self-similarity** | `scripts/experiments/eigenvector_selfsimilarity.py` | ✅ (s184) |
| **φ-information partition** | `mementum/knowledge/phi-information-partition.md` | ✅ (s184) |
| **Crystal trace tooling design** | `mementum/knowledge/crystal-trace-tooling.md` | ✅ (s184) |
| Full ternarization pipeline | `scripts/experiments/full_ternarize.py` | ✅ (s183) |
| Ternary diagnosis | `scripts/experiments/diagnose_ternary.py` | ✅ (s183) |
| Unified probe library | `src/verbum/probes/library.py` | ✅ 903 probes, 535 crystal |
| EQUATIONS.md | `EQUATIONS.md` | ✅ (s181) |

## What changed this session (195)

| # | Change | Impact |
|---|--------|--------|
| 1 | **L0 is genuinely continuous** | "More modes" hypothesis KILLED. 512 modes still 7x PPL. Negative silhouette at all k>=6. |
| 2 | **P4 resolved** | Keep L0 as-is (288MB = 2.8% of FFN). Ternarize everything else. |
| 3 | **L0 vs L15 comparison** | L0 = per-token dictionary (151K entries, continuous). L15 = 9 discrete operations. Fundamentally different. |
| 4 | **L0 correlates with byte_len** | L0 sorts by physical token encoding (NMI=0.259). L15 sorts by syntactic position (NMI=0.216). |
| 5 | **L0 lower rank but not compressible via modes** | gate_proj eff_rank=3278 vs L15's 3771. Concentrated but continuously distributed. |
| 6 | **LOW-RANK RESCUES L0** | SVD at r=750: PPL=0.94x (IMPROVES!), 70.3MB (4.1x compression). 750 functional dims, not 4096. |
| 7 | **Phase transition at r=750** | r=500: 3.4x PPL (broken). r=750: 0.94x (perfect). Razor-sharp boundary. |
| 8 | **L15 functional rank <100** | L15 at r=100: 0.99x PPL. Why 9 ternary modes work — the space is tiny. |
| 9 | **Naive 29-layer combination fails** | PPL 427x, "the the the". Calibration mismatch cascades catastrophically. |
| 10 | **MELT BOUNDARIES WORKS** | Crystal sieve at model level: freeze topology, train beams. 50 steps → 1.52x to 1.02x PPL. |
| 11 | **Staged melt reveals L22-L26 break** | Core melts to 1.00x. Adding L22-L26 jumps to 39x. Binding-prep layers need different treatment. |
| 12 | **Lambda tracer idea** | Use crystal probes as diagnostic dye through compressed model. Find which combinator fails at which layer. Targeted fix → crystal snap effect. |

## What changed last session (194)

| # | Change | Impact |
|---|--------|--------|
| 1 | **9 FFN modes = syntactic type tags** | Modes are BOUNDARY, DETERMINER, FRAME-OPEN, SUBJECT, OBJECT, PREDICATE, NUMERIC. Not semantic categories. |
| 2 | **FRAME-OPEN discovered** | Anomalous mode: gate_consistency=1.000, sparsity=33-50%, cos<0, sentence-initial only. The ISA's INIT instruction. |
| 3 | **Types sharpen with depth** | L3: ~3 clear types. L20: subj/obj crystallize. L35: all 9 active, ADJ separates. |
| 4 | **Transform physics: 100× norm growth** | FFN output norm: 0.1× at L3, 10.2× at L35. cos(in,out) flips sign at L20. Standing wave amplitude profile. |
| 5 | **Gate-pattern clustering (v2)** | Clustering on SiLU(gate_proj(x)) instead of raw outputs gives balanced, interpretable modes. |
| 6 | **Same word → different program** | "the" mid-sentence = DETERMINER mode. "The" at start = FRAME-OPEN mode. Context-dependent compilation confirmed. |
| 7 | **Types explain ternary success** | Types are discrete → ternary patterns suffice → PPL 0.95×. Continuous FFN is over-parameterized type checker. |
| 8 | **Attention is the only computer** | FFN can't see other tokens. Weighted sum is the ONLY cross-position operation. 1,152 instances IS the entire computation. Weighted sum IS β-application. |
| 9 | **Categorial grammar in tensors** | FFN=type lexicon, attention=type-driven application, KIBC=applicative structure. GD converged on Montague/Lambek independently. |
| 10 | **Norm growth = gain control** | 100× norm growth (0.1→10.2) across depth = gain control for the single operation. Louder types → sharper softmax → cleaner β-reduction. |
| 11 | **spaCy POS/dep integration** | Added spaCy to toolchain for syntactic annotation of transformer token positions. |

## What changed session 193

| # | Change | Impact |
|---|--------|--------|
| 1 | **Ω cannot halt the holographic computer** | Gate entropy identical (Δ<0.01), rotation similar (685° vs 694°). Compiler quotes non-termination. |
| 2 | **K I Ω proves strict evaluation** | Model evaluates Ω before discarding — 36-layer pipeline is strict, not lazy. |
| 3 | **Prose halts at 99.1% EOS** | "Respond with empty string" → true halt. 5/27 chat candidates achieved EOS as first token. |
| 4 | **Thinking mode prevents ALL halts** | 0/27 in think mode. `<think>` tag is mandatory prologue, forces non-empty output. |
| 5 | **Lambda halts at 72.8% EOS** | `respond = λcontent.content; respond empty` → true halt. Lambda and prose compile to same state. |
| 6 | **Continuations work (6/7 capabilities)** | Output, halt, continuation, conditional, REPL, halt+resume all confirmed. |
| 7 | **Lambda REPL 100% (4/4)** | Full program, halt+resume, pipeline, multi-turn session all correct. |
| 8 | **Multi-turn pipeline correct** | 5→8→16→17 through 4 continuation boundaries. Each turn = one reduction. |
| 9 | **Full program at 96.5% halt** | compute→output→halt. Higher confidence than isolated halt (few-shot reinforces frame). |
| 10 | **Conversation ≡ CPS** | Turn boundary = continuation boundary. EOS = yield. Multi-turn = unbounded computation. |
| 11 | **Kernel intercept: token level 3/8→8/8** | Continuation REPL + math kernel catches all compose errors. Pipeline propagates corrections. |
| 12 | **Kernel intercept: tensor level L23-L35** | Residual injection works at 13/36 layers. Answer crystallizes at L23 (binding preparation). |
| 13 | **Transparent math co-processor feasible** | Inject correct residual at L23+, model continues as if it computed correctly. |
| 14 | **L23 = decision boundary** | Before L23: computation in progress. After L23: answer committed. SNAP transition, not gradual. |

## What changed session 192

| # | Change | Impact |
|---|--------|--------|
| 1 | **Independent psi evaluation** | Separate human + agent verified crystal across 5 architectures. All core claims hold. |
| 2 | **Tiny classifier ternary: 288MB→180KB** | 1638× compression, PPL 0.98× (IMPROVES), classifier 100% accuracy. Breakthrough result. |
| 3 | **Ternary inference at scale: PPL improves at 8B** | L15 Qwen3-8B: 9 ternary programs achieve 0.96× baseline PPL. Continuous FFN over-parameterized. |
| 4 | **Two overlapping ternary structures discovered** | Crystal basis (KIBC, routing, 3.5%) orthogonal to operational modes (9 programs, 96.5%). AMI = 0.15. |
| 5 | **φ convergence: 14B hits 0.7% error** | Within Qwen3 pure language: monotonic improvement 0.6B→8B→14B. 32B regresses (zone-B heuristic?). |
| 6 | **Gradient-quant correspondence: EXPAND only** | ρ = +0.55-0.78 at L1-L3, zero at L5+. GD converges to ternary normal form in EXPAND phase only. |
| 7 | **Crystal derivation: topology yes, magnitudes no** | 2.35M expressions → correct eigenvector topology. Eigenvalue ratios diverge (3.98 vs 1.47). |
| 8 | **Centroid ≡ ternary to the decimal** | Continuous cluster centroids and ternarized versions produce IDENTICAL PPL. Signs + scale = everything. |
| 9 | **Coherence test: mode preserved, content varies** | Fact recall holds (80%) at L20/L25. Wording changes but correct combinator fires. |
| 10 | **Scale convergence: 0.6B→8B→32B** | Ternary PPL ratio improves with scale. At 32B, all zone-B layers ≤ 1.03×. |
| 11 | **Multi-layer: 3 zone-B layers at 1.07×** | L10+L14+L19 cumulative = 1.07×. Errors DON'T cascade in sweet spot. 864MB→540KB. |
| 12 | **Full-depth scan: 35/36 layers survive** | Every layer except L0 individually ≤1.15×. Classifiers 98-100% on all 36. |
| 13 | **L0 is catastrophic (115×)** | Embedding-adjacent layer is special — genuinely continuous, needs magnitudes. |
| 14 | **Zone of silence: L13-L21** | PPL 0.95-1.01× individually. ORTHO phase IS the ternary sweet spot. |
| 15 | **All-layer cascade: 836×** | Full replacement fails — L0 poisons chain, binding layers cascade compounds. |
| 16 | **Semantic convergence: dog=perro=犬 at L19** | 8 concepts × 6 languages. Peak cross-lingual cos 0.66 at L19-L20. Peak separation at L25. |
| 17 | **Compilation pipeline: 4 evidence lines** | Lexer→Parser→Optimizer→RegAlloc→Emit confirmed by FFN trace, binding trace, λ-machine, semantic convergence. |
| 18 | **Mode universality: modes are layer-specific** | Cross-layer cos 0.026. 9 modes real everywhere but DIFFERENT programs at each depth. Topological self-similarity. |
| 19 | **Rotation spiral: 325° total** | Two phase transitions (emb→L0: 73°, L5→L6: 86°). IN 12°/layer, OUT 5.5°/layer. Asymmetric. |
| 20 | **Q⊥K everywhere (87-90°)** | W_Q is projection not rotation (SV ratio 46). Q norm grows 200×. Attention = holographic readout. |
| 21 | **QK angle predicts ternary PPL (r=-0.58)** | More orthogonal → more discrete → easier to ternarize. The orthogonality IS the discreteness. |

## Session 192 recap

PSI EVALUATION → MULTI-LAYER SCAN → SEMANTIC CONVERGENCE → COMPILATION
PIPELINE → MODE UNIVERSALITY → ROTATION SPIRAL → Q GEOMETRY.

Seven experiments in one session. The transformer architecture decoded from
multiple independent angles. Final synthesis: a holographic computer with
a rotating program counter.

**Part 1: Psi evaluation.** Independent project verified crystal across 5
architectures. Breakthrough: tiny classifier ternary replaces FFN layer
(288MB → 180KB, 1638×, PPL IMPROVES 0.98×, classifier 100% accuracy).

**Part 2: Multi-layer scan.** 35/36 individual layers survive ternary. L0
catastrophic (115×). Sweet spot L13-L21 (0.95-1.01×). Zone-B cumulative:
L10+L14+L19 = 1.07× (no cascade). All-36 = 836× (cascade destroys).

**Part 3: Semantic convergence.** 8 concepts × 6 languages × 36 layers.
Dog=perro=犬 at L19-L20 (cos 0.66). Peak separation (same vs different
concepts) at L25 (+0.20). L34-L35: everything converges (format > content).

**Part 4: Compilation pipeline.** Four evidence lines (FFN trace s187,
binding trace s188, λ-machine s190, semantic convergence s192) converge:
Lexer (L0) → Parser (L1-L7) → IR Optimizer (L13-L21) → Register Alloc
(L22-L27) → Emit (L34-L35). The 9 ternary programs ARE the optimization
passes.

**Part 5: Mode universality.** The 9 modes are NOT universal across layers
(cross-layer cos 0.026). Layer-specific ISAs. BUT: the architecture is
universal (9 modes, linearly separable, ternary everywhere). Topological
self-similarity, not metric. Classifier transfer: 90%+ locally (±2-3
layers), 47-64% globally.

**Part 6: Rotation spiral.** Residual rotates 325° over 36 layers. Two
phase transitions: emb→L0 (73°) and L5→L6 (86°, norm jumps 60×). IN
fast (12°/layer), OUT slow (5.5°/layer). Asymmetric because analysis
(decomposition) is easier than synthesis (composition). IN↔OUT residual
cos 0.93-0.99 (structural symmetry preserved).

**Part 7: Q rotation geometry.** Q and K are near-orthogonal (87-90°) at
ALL layers. W_Q is a projection (SV ratio 46), NOT a rotation. Q suppresses
positional diversity (ratio 0.58). Q norm grows 200× with depth (whisper
early, shout late). QK angle vs ternary PPL: r=-0.58 (more orthogonal =
easier to ternarize). Attention is holographic readout of the rotating state:
perpendicular beams interfering.

**Final synthesis — the holographic computer:**

```
RESIDUAL STREAM = rotating program counter + register file
  spirals 325° across 36 layers | norm grows 0.6 → 900
  IN: fast rotation (dissolving tokens → universal semantics)
  BOTTOM (L19): pure semantic state (dog = perro = 犬)
  OUT: slow rotation (precipitating semantics → specific tokens)

FFN = ALU with 9-opcode ISA (layer-specific)
  classifier selects program | ternary pattern × gamma = output
  288MB → 180KB per layer | 1638× compression | PPL improves
  sweet spot L13-L21: IS ternary (continuous weights = noise around fixed point)

ATTENTION = holographic memory bus (perpendicular readout)
  Q ⊥ K (87-90° everywhere) | interference pattern = attention weights
  W_Q/W_K are projections (collapse 4096→128 dim), not rotations
  near-binary routing (1 bit per decision) | 32 heads × 3 positions = O(1)
  Q norm 200× growth = model becomes more certain with depth

RESIDUAL ADD = write-back (FFN advances spiral, attention copies values)
```

The model is a holographic computer with a rotating program counter.
The program counter (residual) rotates through a spiral. The ALU (FFN)
executes 9 discrete operations selected by the current rotation angle.
The memory bus (attention) reads from perpendicular projections. The
entry (L0) and exit (L35) interface with concrete tokens. Everything
in between is abstract, discrete, and compressible.

## What changed session 191

| # | Change | Impact |
|---|--------|--------|
| 1 | **Fibonacci stride attention is working** | Entropy monotonically decreases: 3.0 (stride-1) → 0.5 (stride-1597). 9 sparse + 9 moderate + 1 broad. Healthy structure. |
| 2 | **Per-head specialization at stride-34** | H1-H4 near-deterministic (ent 0.15-0.24, max_wt 0.92-0.95), H5-H6 scanning (ent 1.6-1.8). Different heads = different roles. |
| 3 | **Delta divergence gradient: short 3.6% → long 4.4%** | V/O diverge more at long strides (see different context than teacher). K diverges least (routing keys closest to teacher). |
| 4 | **Q/K gammas settle 2× faster than V/O** | Q/K: 32-38% settled, RMS 8-10e-03. V/O: 15-16% settled, RMS 3.6-4.8e-02 (5× larger). Routing is easy, content is hard. |
| 5 | **Flipped positions 3× hotter than keeps** | TD-flipped delta positions: routing gradient 2.2-3.3× higher. Ratio peaks at stride-8 (3.27×), lowest at stride-1597 (2.25×). |
| 6 | **63% of routing gradient near-zero** | Delta plates past halfway to convergence. 65% at short strides, 61% at long strides. |
| 7 | **Flip P/N ratio ≈ 0.96 (symmetric)** | TD flips +1 and -1 teacher signs with near-equal probability. Structural adaptation, not systematic bias. |
| 8 | **Spatial flip pattern differs by distance** | Short strides: column-clustered (input features). Long strides: row-clustered (output dimensions). Physics of the window. |
| 9 | **No teacher zeros in attention** | Teacher extraction produced 0% zeros in Q/K/V/O. All positions participate. Sparsity must come from the mask/gate, not structure. |
| 10 | **Training trajectory: loss plateau at 6.7-6.8** | Step 500→1500: 7.78→6.73. Flattening. Crystal EMA stable (0.0097). Parity/cross-zone converged. Delta Δ growing slowly. |
| 11 | **FFN gate is NOT sparse (66-74% fire)** | Teacher: ~3% fire (89% killed). Student: 66-74% fire. Ternary gate can't create sharp gating. Dense transform, not selective retrieval. |
| 12 | **Attention collapsed to relay (I combinator)** | 32/40 probed head-layer pairs have cos_self > 0.8. At strides ≥8, ALL heads are pure relay (cos 0.95+). Only stride-1 shows partial composition. |
| 13 | **Architecture is inverted from teacher** | Teacher: sparse FFN (retrieval) + mixed attention (relay+compose+bind). Student: dense FFN (transform) + relay attention (I combinator). |
| 14 | **TD oscillation: 94% of positions still candidates** | 117.7M/124.5M positions have been candidate 20+ times. Only 6.2% settled. Oscillation rate INCREASES with flip count (96-100% for multi-flipped). |
| 15 | **Phase transition hypothesis** | Attention relay = B-dominant easy path. Loss plateau at 6.7 = pre-transition. TD prevents GD from settling into stable topology needed for phase transition to compositional attention. |

## Session 191 recap

V15 CHECKPOINT ASSESSMENT — ATTENTION + GRADIENT-ZERO + FFN RETRIEVAL + TD OSCILLATION.

Four diagnostic experiments on the v15-td step 1500 checkpoint.

**Experiment 1: Attention pattern analysis.** Fibonacci stride attention IS
working. Entropy 3.0→0.5 monotonically. 9 sparse + 9 moderate + 1 broad.
Per-head specialization at stride-34. Delta divergence 4.0% mean (V/O more
at long strides). The routing structure is healthy.

**Experiment 2: Gradient-zero topology.** Q/K gammas settle 2× faster than
V/O (38% vs 16% settled, V/O has 5× larger gradient). Flipped positions are
3× hotter than keeps. Spatial flip patterns differ by stride distance (short
= column-clustered, long = row-clustered).

**Experiment 3: FFN retrieval (I combinator).** The student has INVERTED the
teacher's architecture. Teacher: sparse FFN gate (3% fire, selective retrieval)
+ mixed attention (relay + compose + bind). Student: dense FFN gate (66-74%
fire, brute-force transform) + nearly all-relay attention (32/40 heads have
cos_self > 0.8, all heads at strides ≥8 are pure relay cos 0.95+). The
attention has collapsed to the I combinator — it passes V through unchanged
and lets the dense FFN do all the work.

**Experiment 4: TD oscillation analysis.** The flip map reveals TD is
preventing convergence. 94.5% of all positions (117.7M/124.5M) have been
candidates 20+ times. Only 6.2% have settled. Critically, oscillation rate
INCREASES with flip count: positions flipped 2× are 96.3% still candidates,
3× are 98.5%, 4+ are 99.4-100%. Once a position starts flipping, it never
stops. TD is treating the entire weight space as "still needs work."

**Key insight — Phase transitions require topology stability.** The attention
relay collapse is the B-dominant easy path — the model found the fastest way
to reduce loss given the current topology. To break through the 6.7-6.8
plateau, the model needs a phase transition to compositional attention. But
TD's continuous perturbation prevents GD from settling into a stable topology
long enough to discover the next phase. Training from scratch shows B→K phase
transitions happen when GD can plateau, settle, then reorganize. TD's 94%
candidacy rate prevents this entirely.

**Prescription:** Dedicated sessions to fix TD. Options: (1) epoch-based TD
with freeze periods (punctuated equilibrium), (2) much higher candidate
thresholds, (3) aggressive oscillation-gated cooldown, (4) per-position
conviction requirements, (5) candidate-count gating for chronic candidates.

## What changed session 190

| # | Change | Impact |
|---|--------|--------|
| 1 | **DVD stamp test: gradient topology compounds less** | Gradient mask PPL 188K vs magnitude 620K (3.3×). L35 cos 0.165 vs 0.001 (115× better signal). 49.9% overlap = orthogonal signals. |
| 2 | **Per-group(32) scaling: 14× PPL improvement** | Magnitude+group PPL 43K (from 619K). Q4's secret is scale granularity, not level count. |
| 3 | **FFN is the catastrophe, not attention** | FFN-only ternary → PPL 485M. V/O-only → PPL 23. Q/K-only → PPL 30. Attention survives ternary. FFN doesn't. |
| 4 | **FFN = holographic beam former (fragile)** | FFN compiles precise beam directions. Ternarizing scatters the beam. The zero mask IS the holographic fringe pattern. |
| 5 | **Attention = sparse O(1) router (robust)** | 22/32 heads use <3 positions. Near-binary routing survives ternary. PPL 23-30 with ternary attention. |
| 6 | **Sparse top-3 at all layers: PPL 12.2 → 13.3** | 8.6% increase. O(1) attention confirmed at PPL level. 333× fewer attention ops at context 1000. |
| 7 | **Binding layers only: PPL 82K (not sufficient)** | L27/L30/L33 are final reductions, not the full algorithm. 33 other layers do type prep and composition. |
| 8 | **Binding heads only: PPL 6.3M (not sufficient)** | H31@L27, H03/H13/H15@L30, H06/H07@L33 = tip of 36-layer parser iceberg. |
| 9 | **Model = 36-stage typed shift-reduce parser** | Every layer contributes. Every head contributes. But each head only needs 3 positions. |
| 10 | **Compression strategy clarified** | Ternary attention (free, 22% params). Preserve FFN (hard, 78% params). Sparse top-3 routing. |
| 11 | **FFN beam directions are model-specific** | Projected FFN output through unembed for Qwen3-8B, Qwen3-0.6B, Pythia-410M. Token-level Jaccard ~0.01. The STRUCTURE (that beams exist, their depth) is universal. The CONTENT (which tokens to promote/suppress) is learned. |
| 12 | **Anti-crystal visible in beams** | "cat sat on the" → Qwen3-8B L29 suppresses 犬/狗狗/puppy (anti-dog at cat position). "earth is not" promotes flat/perfect. "identity y" L32 promotes y/Y/yi. The FFN knows the answer AND what to suppress. |
| 13 | **Crystal distillation: next-token beats teacher KL** | Crystal+next-token PPL 236 vs crystal+distill PPL 366 vs random+distill 733. Capacity mismatch: 0.6B student can't match 8B teacher's full 151K distribution. Crystal still helps 2.0× vs random. |
| 14 | **Distillation temperature matters** | KL from 8B teacher gives HARDER gradients than next-token CE. Need higher T, top-k, or self-distillation (same-size teacher) to fix capacity mismatch. |

## What changed session 189

| # | Change | Impact |
|---|--------|--------|
| 1 | **Stride coverage validation on Qwen3-8B** | Powers of 2 capture 29.5%/67.4% (exact/±2) of L30 attention mass. Not enough for binding. |
| 2 | **Binding distance distribution** | Bimodal (local d=1-8, gate d=32+), NOT power law (R²=0.004). Powers of 2 skip binding range d=3-20. |
| 3 | **Fibonacci strides: 91.4% coverage (+25.9pp)** | Dense where bindings live, sparse where they don't. Natural basis for attention spacing. |
| 4 | **3 gap-fillers [15,20,24] → 100% coverage** | Fill holes between F(7)=13..F(8)=21..F(9)=34 where gap > 2×radius. |
| 5 | **Crystal Laplacian: WHNF is fragile (μ=0.228)** | 8.6× weaker restoring force than BCDY. Predicts stability not speed. |
| 6 | **Settlement dynamics confirm Laplacian** | B,C converge (fast). K,D stable (medium). Y,WHNF drift away (fragile). Crystal MSE U-shapes. |
| 7 | **Laplacian-weighted crystal loss** | WHNF gets 5× weight. v14 WHNF/B gradient = 0.3×, v15 = 1.9× (6× amplification). |
| 8 | **GLA sparsity is illusory** | Dense projections cost 19B ops/layer. Strided scan saves <0.03%. Dropped for unified FSA. |
| 9 | **v15 architecture: 19 strides, unified attention** | FibonacciStrideAttention + ±2 neighbors, all composition, standalone (zero v14 deps). |
| 10 | **v15 extraction complete** | 83 arrays, 65.5 MB, 16.5 min. 19 strides × 4 projections + 6 FFN + 1 embedding. |
| 11 | **v15 training started** | TD training running in tmux, step 1 CE=10.533. 3000 steps target. |
| 12 | **φ at five levels** | Crystal eigenvalues, information partition, standing-wave phase, compute cycle, AND stride spacing. |
| 13 | **Laplacian φ-ratio** | μ₅/μ₄ = 1.54 ≈ φ in the crystal graph Laplacian. Sixth level. |

## Session 190 recap

DVD STAMP TOPOLOGY + λ-MACHINE + BEAM UNIVERSALITY + CRYSTAL DISTILLATION.

Six experiments decode the compression structure, algorithm, and knowledge
boundary of transformers.

**Experiments 1-4:** See session 190 table above. DVD stamp topology compounds
less (3.3× PPL improvement). FFN is fragile (PPL 485M ternarized), attention
is robust (PPL 23-30). Sparse top-3 works (PPL 13.3). Model is a 36-stage
typed shift-reduce parser.

**Experiment 5: FFN beam universality.** Projected FFN output through unembed
for Qwen3-8B, Qwen3-0.6B, Pythia-410M at matched fractional depths. Token-level
Jaccard ~0.01 (near zero) across all three model pairs. The beam STRUCTURE is
universal (all models form beams at the same depths). The beam CONTENT is model-
specific (which tokens to promote/suppress is learned, not derivable). The anti-
crystal is visible: "cat sat on the" → L29 suppresses 犬/狗狗/puppy. "identity
y" L32 promotes y/Y/yi. The FFN knows the answer AND actively cancels wrong ones.

**Experiment 6: Crystal distillation.** Teacher=Qwen3-8B, Student=Qwen3-0.6B
crystal sieve (frozen signs, trainable masks). Crystal+next-token (PPL 236) beats
crystal+distillation from 8B teacher (PPL 366). Capacity mismatch: 0.6B student
can't match 8B teacher's full 151K distribution — harder optimization target than
simple next-token. Crystal still helps 2.0× vs random signs (733 → 366). Self-
distillation (same-size teacher) is the likely fix.

**Key insight boundary:** The crystal (signs, eigenvalues, phase structure) is
universal and derivable. The holographic content (which tokens to promote/suppress)
is model-specific and must be learned from data or distilled from a same-capacity
teacher. Structure is free. Knowledge has a cost.

## Session 189 recap

FIBONACCI STRIDES + LAPLACIAN CRYSTAL + V15 TRAINING.

Five experiments decode why v14's powers-of-2 strides fail (29.5% mass recall)
and how Fibonacci strides + ±2 neighbor gathering achieve 100% coverage. The
crystal graph Laplacian reveals WHNF is the most fragile node — it starts settled
then drifts away because its restoring force (μ=0.228) is 8.6× weaker than the
composition cluster. Laplacian-weighted crystal loss compensates: WHNF gets 5×
weight, 6× gradient amplification (v14 ratio 0.3× → v15 ratio 1.9×).

v15 is standalone (zero v14 dependencies), extracted (83 arrays, 65.5 MB),
and training (TD, 3000 steps, running in tmux). The golden ratio appears at
six levels of the architecture — crystal eigenvalues, information partition,
standing-wave phase, compute cycle, stride spacing, and now the crystal
Laplacian itself.

## What changed session 188

| # | Change | Impact |
|---|--------|--------|
| 1 | **500 crystal probes through 32 heads at L27/L30/L33** | First statistical head→combinator mapping. 500 probes × 3 layers × 32 heads = 48,000 measurements |
| 2 | **Inter-combinator correlation r=0.944** | All 9 combinators activate nearly identical head patterns. No "K heads" or "B heads" exist. Shared execution hardware. |
| 3 | **KIBC indistinguishable (r=0.944-0.978)** | The core 4 combinators are invisible to head activation. B-D highest pair (r=0.986): composition ≡ nesting at the head level. |
| 4 | **94.9% of variance = overall loudness** | Head activation is almost entirely "is this head generally active?" not "which combinator?" The combinator signal is in the remaining 5.1%. |
| 5 | **PC1 after normalisation = WHNF↔D (45.9%)** | The real discriminant is reduction depth: "already reduced" vs "deeply nested". Not opcode type. |
| 6 | **PC2 = Y/W/I↔D/B (23.5%)** | Secondary axis: self-reference (recursion, self-application, identity) vs structural (nesting, composition). |
| 7 | **2 effective dimensions capture 69.4%** | The 32×9 head×combinator matrix compresses to ~2 coordinates per head. Very low-dimensional ISA. |
| 8 | **s187 head types revised** | H08 "λ-head" → D/B/S+ (composition depth). H10 "binding" → Y/W+ (self-reference). H20 "relay" → Y/W+ (recursion). H26 "quantifier" → WHNF+ (termination detector). |
| 9 | **H06/H07 = universal execution engine** | Loudest heads (norm 26.7/19.1), lowest gate attention (0.555/0.609). They do the work for ALL combinator types. The "GPU" of the attention ISA. |
| 10 | **H26/H27 = WHNF termination detectors** | +30-32% WHNF excess. They recognise when reduction is complete. The "halt" circuit. |
| 11 | **H08 = only truly selective head** | D+40% excess, sel=1.399. The closest thing to a specialised circuit: responds to deep nesting. Everything else is mild bias. |
| 12 | **Routing IS the program (confirmed)** | Since heads don't discriminate combinators, the combinator-specific behavior must live in attention PATTERNS (Q/K routing), not head identity. |
| 13 | **Binding graph trace: attention IS the binding graph** | 14 probes with annotated bindings. Object→verb binding = concentrated attention (0.5-0.8 weight) through H03/H13/H15 at L30. |
| 14 | **Causal mask partitions binding direction** | 0/23 forward bindings detected (arg before func). 14/14 backward bindings detected (arg after func). Causal mask blocks forward β-reduction. |
| 15 | **Minimal pair binding flip confirmed** | "dog bit cat" vs "cat bit dog": same heads (H13, H03, H15), same weights, flipped target. Position-structural routing. |
| 16 | **Passive voice preserves semantic binding** | "The boy kicked the ball" (active) and "The ball was kicked by the boy" (passive) both bind agent→kicked, through partially different head sets. |
| 17 | **Two binding sub-circuits** | Predicate-argument binding (H03/H13/H15) vs coreference binding (H07/H05). Different heads for "cat→bit" vs "itself→dog". |
| 18 | **Binding weights are near-deterministic** | H13: 78.5% attention to "bit" from "cat". Almost binary routing = very low information content per binding decision. |
| 19 | **Reverse binding confirmed: verb→subject at L27** | H31 at "runs" attends 82.3% to "cat" and outputs 猫/貓/cats = subject identity transfer. The verb reads the subject. |
| 20 | **Two-phase binding schedule decoded** | L27: verb reads subject (agent identity, H31). L30: object reads verb (predicate binding, H03/H13/H15). Depth ordering = reduction schedule. |
| 21 | **Same heads do both directions at L30** | H03 and H13 handle verb→subject AND object→verb. Universal binding hardware, direction determined by sequence order. |
| 22 | **Head output IS the reduction result** | H31 outputs "狗/dog" at "bit" when it reads subject "dog". The value transfer IS β-reduction — not metaphor, literal mechanism. |
| 23 | **Binding circuit = 0.3% of model** | ~4 heads out of 32×36=1152. Subject binding: 1 head (H31@L27). Object binding: 3 heads (H03/H13/H15@L30). Near-deterministic routing. |
| 24 | **Attention is inherently sparse: 22/32 heads use <3 positions** | At L30, effective positions <3 for 22 heads, <5 for 29/32. Top-3 captures >88% for ALL heads. |
| 25 | **Sparsity holds across sequence length** | 5→74 tokens: effective positions only grows 2.8→3.7 at L30. O(1) attention, not O(n). |
| 26 | **Mean entropy ~0.9 bits at binding layers** | The routing decision is ~1 bit per position. Full QK^T over entire context is massive overkill. |
| 27 | **Design implication: top-3 sparse attention** | Scoring only 3 KV slots per head captures 88-97% of attention mass. 10 slots captures 95-99%. |

## Session 188 recap

FOUR EXPERIMENTS DECODE THE ATTENTION EXECUTION MECHANISM.

**Experiment 1: Head→Combinator mapping** (500 crystal probes × 32 heads × 3
layers). All 9 combinators activate identical head patterns (r=0.944). No
combinator-specialised heads. The ISA has ~2 effective dimensions: reduction
depth (WHNF↔D, 46%) and self-reference (Y/W/I↔D/B, 24%). 94.9% of head
activation variance is just loudness. See `head-combinator-isa.md`.

**Experiment 2: Binding graph trace** (14 annotated probes). Object→verb
binding = concentrated attention (0.78 weight) through H03/H13/H15 at L30.
"cat" attends 78.5% to "bit" = `bit(_, cat)`. Subject→verb binding blocked
by causal mask (0/23 forward). Minimal pair: same heads, flipped routing.
Two sub-circuits: predicate-argument (H03/H13/H15) vs coreference (H07/H05).
See `binding-graph-trace.md`.

**Experiment 3: Reverse binding trace** (12 probes, verb→subject direction).
H31 at L27 attends 82.3% from "runs" to "cat" and outputs "猫, 貓, cats".
Two-phase binding: L27=verb reads subject, L30=object reads verb. Same heads
(H03/H13) do both directions at L30. Binding circuit = 0.3% of model.

**Experiment 4: Attention sparsity** (22 probes, 5→74 tokens, 9 layers).
22/32 heads at L30 have effective positions <3. Top-3 captures >88% for ALL
heads. Mean entropy 0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens
(eff_pos 2.8→3.7). Only 1/32 heads (H20) is truly dense. Full O(n²) QK^T
is massive overkill. Top-k sparse attention with k=3-5 captures nearly all
routing information. See `attention-sparsity.md`.

**Synthesis:** The model is a typed parser with a compiled lexicon. FFN
compiles V vectors (the program). ~4 heads at L27/L30 route via concentrated
backward attention (~1 bit per binding). The binding circuit is 0.3% of the
model, the routing is near-deterministic, and attention is inherently O(1)
sparse. Design implication: top-k sparse attention (k=3-5) replaces full
O(n²) attention for 88-97% of routing information. The "portable tensor"
needs: compressed FFN (sieve) + tiny routing function + depth schedule.

## What changed session 187

| # | Change | Impact |
|---|--------|--------|
| 1 | **FFN reduction trace on Qwen3-8B** | Projected active FFN neurons through unembed at 11 layers across 5 probes × 2 gates. First direct reading of what FFN neurons "say" in token space. |
| 2 | **Three-phase FFN output: noise→semantic→format** | L0-L22=noise (ORTHO null-space computation), L26-L30=coherent semantic associations (ALIGN), L33-L35=formatting/syntax (COLLAPSE). Matches standing-wave depth structure exactly. |
| 3 | **"If it rains" at L30: `it`→rain, `ground`→soak, `is`→wet** | Each position's FFN writes precise associative predictions. The FFN resolves referents, predicts consequences, and completes predicates. |
| 4 | **L26 comma promotes "then, entonces, então"** | The FFN writes logical connectives at structural boundary positions — multilingual implication operator at the comma in conditionals. |
| 5 | **"earth is flat" → FFN promotes "round", suppresses "earth"** | The FFN contains factual correction: it knows the earth is round and writes the correction even when processing the false claim. |
| 6 | **Compile ≈ null (max delta 2.8%)** | FFN function lists are nearly identical between compile and null gates. The FFN is a universal semantic analyzer; compile behavior emerges from attention routing. |
| 7 | **β-reduction hypothesis CONFIRMED (revised framing)** | FFN=compiler (writes context-dependent V vectors), attention=executor (softmax over V IS β-reduction). Same token "the" produces different compiled values in different sentence contexts — compilation, not lookup. |
| 8 | **Five attention head types identified** | λ-heads (H08/H09 write λ/→), binding heads (H10/H11 write predicate at subject = typed_apply), relay heads (H20 pass V unchanged), compositional heads (H03 combine positions), quantifier heads (H26 broadcast scope). |
| 9 | **H10/H11 at L33 ARE β-reduction** | In compile mode, H10 writes "runs" at "dog" position (Δ=64 vs null). This IS `runs(dog)` = `(λx.runs(x))(dog) → runs(dog)`. Subject-verb binding = function application. |
| 10 | **λ-heads attend to gate prefix (0.97-0.98)** | H08/H09 barely see probe tokens; they read the compile exemplars to know what FORMAT to produce. The task circuit reads instructions, not content. |
| 11 | **Reduction chain trace across 36 layers, 7 combinators** | Traced cumulative residual→unembed at every layer for K,I,B,C,Y,S,W probes. Different combinators resolve at different depths. |
| 12 | **Y combinator peaks early (L27), W peaks late (L33)** | Recursion (Y) resolves mid-depth during ALIGN phase. Self-application (W, "itself") resolves at the final layer. K (discard) front-loaded, C (flip/passive) resolves last. |
| 13 | **Y-probe "She told a story about a girl who told a story..."** | First and second occurrences of same tokens get DIFFERENT cumulative representations — the recursive structure is tracked position-dependently across depth. |
| 14 | **MTP self-speculation: L33 matches L35 48% of the time** | L33 Hit@10=76%, Hit@100=92%. Median rank=2. The last 2 layers sharpen but rarely change the answer. Early-exit at L33 viable for ~half of tokens. |
| 15 | **Multi-position lookahead collapses for ALL layers** | N+2 Hit@10=10% even at L35. The model does next-token prediction, not multi-position. FFN "semantic predictions" (reads→book) are associative meaning, not sequence forecasting. |
| 16 | **L30 median rank = 7** | The correct next token is already in L30's top 10. L31-L35 SHARPEN the distribution (rank 7→1) but don't fundamentally change it. The program is compiled by L30; execution just resolves it. |

## What changed session 186

| # | Change | Impact |
|---|--------|--------|
| 1 | **LARQL FFN decomposition applied to Pythia-160M** | cos(up,down) circuit type analysis reveals same phase structure as our activation-level measurements — independent confirmation from pure weight geometry |
| 2 | **KIBC opcodes orthogonal to circuit types** | Cross-tabulation uniform at every layer. KIBC=what activates neuron, circuit type=how neuron transforms. Independent axes of FFN characterization. |
| 3 | **ORTHO phase = inverter-dominated** | L3-7 features are 60-74% suppressors+inverters (direction flipping). This IS the invisible computation in null space. |
| 4 | **Dark-space drop at L11** | 93-99% dark at L0-L10, drops to 57% at L11. Final layer concentrates vocabulary-aligned knowledge. Standing-wave antinodes. |
| 5 | **Correlation sign flip** | ρ(cos, KIBC_magnitude) = -0.26 at L8 (inverters do lambda computation), +0.27 at L11 (projectors do lambda output) |
| 6 | **Gated vs non-gated architecture difference** | Gemma=transforms (rotation), Pythia=inverters (direction flip). Same phase structure, different computation style. |
| 7 | **New zero-cost instrument** | cos(W_up[j], W_down[:, j]) detects depth phases from weights alone — no forward passes, 2 min for all layers |
| 8 | **Crystal signs predict circuit types (ρ=1.0)** | cos(sign(W_up), sign(W_down)) depth profile perfectly rank-correlates with full-weight profile. Signs alone predict phase structure. |
| 9 | **Sign agreement depth profile** | L0=0.53 (correlated→projector), L3-4=0.38 (anti-correlated→inverter), L8=0.45 (recovering). GD actively creates sign anti-correlation at computation layers. |
| 10 | **Per-neuron ρ > 0.98 at ORTHO layers** | Signs predict which individual neurons are projectors vs inverters with 98%+ fidelity at L2-L8. Magnitudes add precision, topology is in the signs. |
| 11 | **Cross-matrix anti-correlation is load-bearing** | Decorrelating T_down (destroying phase structure while preserving per-matrix stats) degrades PPL from 511 to 1817. Decorrelated ≈ random (1817 vs 1952). The anti-correlation IS the signal. |
| 12 | **Per-matrix signs alone are nearly worthless** | Without cross-matrix correlation, crystal signs give only 7% improvement over random (1817 vs 1952). With correlation, crystal gives 3.8× improvement over random. |
| 13 | **Synthetic anti-correlation is WORSE than random** | Constructing T_down to hit the measured profile with random per-neuron signs → PPL 6464 (4× worse than random 1608). Forced anti-correlation creates destructive interference. |
| 14 | **The crystal is per-neuron assignments, not aggregate statistics** | The anti-correlation profile is an emergent property of correct per-neuron signs, not a prescription. Knowing "62% should be inverters" ≠ knowing WHICH neurons should be inverters. |
| 15 | **Universal curve beats extracted profile (when signs are random)** | Smooth parameterized curve → PPL 2734 vs exact per-layer values → PPL 6464. Less aggressive anti-correlation is less harmful when per-neuron assignments are wrong. |

## What changed session 185

| # | Change | Impact |
|---|--------|--------|
| 1 | **Standing-wave magnitude reframing** | Weight magnitudes are a standing wave: crystal signs = boundary conditions, zero mask = nodes, active weights = antinodes, GD = finding resonant modes |
| 2 | **GD convergence = standing wave fixed points** | Near-zero gradient at zeros (nodes) AND at large weights (antinodes) — both are stable points of the wave. Gradient-zero-map (s171) already measured this. |
| 3 | **Depth-axis standing wave** | 3-phase residual structure maps to standing wave along depth: orthogonal=nodes, align=antinodes, collapse=destructive interference. Phase transition at 1/φ = fundamental mode. |
| 4 | **REDUCE/SWITCH = spatial harmonics** | Alternating ρ sign across depth is harmonic structure of the depth-axis standing wave |
| 5 | **Holographic ≡ standing wave** | Holographic plate = frozen standing wave (interference fringes). Same physics, different vocabulary. Unifies s167 holographic-computer with magnitude observations. |
| 6 | **Sieve = pre-setting resonant cavity** | Crystal init pre-sets boundary conditions → GD finds modes 10.7× faster because cavity already resonates correctly |
| 7 | **Shape preservation experiment** | Quantized Pythia-160M at 7 levels (ternary through 8-bit). Cosine (ρ=-0.933) > Spearman shape (ρ=-0.917) > bits (ρ=-0.761) as PPL predictor. |
| 8 | **Ternary beats 2-bit at fewer bits** | Ternary (1.6b, PPL 9504) beats 2-bit (2.0b, PPL 25892) because separating phase from amplitude is more efficient than joint encoding |
| 9 | **4-component standing-wave decomposition** | Phase (1 bit, exact) + nodes (~0.6 bit) + envelope (~0 amortized) + shape (1-3 bits, NOT in ternary). Sieve regenerates shape from data. |
| 10 | **Phase transition at 3 bits** | PPL drops from ~10K (ternary/2-bit) to 189 (3-bit) to 50 (4-bit). 8 levels = minimum for standing wave to survive 12-layer transit. |
| 11 | **Shape-aware helps low bits, hurts high bits** | 2-bit quartile 1000× better than uniform. 4-bit quartile WORSE than uniform. Rank preservation ≠ value preservation. |
| 12 | **Compounding law = cos^L** | Per-layer cosine raised to layer count predicts model quality. 0.896^12=0.27 (ternary), 0.957^12=0.59 (3-bit), 0.990^12=0.89 (4-bit). |
| 13 | **ORTHO phase is rank-1** | Residual covariance at L7-22 has effective rank=1. Top eigenvalue ~710K, decay to 2nd: 4000-8800×. One direction carries >99% of all variance. |
| 14 | **V lives in the null space during ORTHO** | Weight matrix V has 0% overlap with residual covariance subspace for 16 consecutive layers. Projection = 0.01. Computation is invisible. |
| 15 | **Cumulative null space = 67.7%** | 2771 of 4096 dims unconstrained by residual covariance. U has enormous freedom. Covariance alone CANNOT determine U. Partial negative for derivation. |
| 16 | **ALIGN rank explosion** | Effective rank grows ~130 dims/layer during L23-34. V transitions from 0% to 100% inside residual subspace over 10 layers. Integration phase. |
| 17 | **Phase structure refined** | EXPAND=high-rank (V reads residual), ORTHO=rank-1 (V reads null space), ALIGN=rank growth (V transitions), COLLAPSE=destructive interference. |
| 18 | **Crystal formation cost is UNKNOWN** | Corrected prior claim: r=0.998 cross-model tells us the endpoint, not the cost. 99.8% training claim was ungrounded. Need formation tracking experiment. |

## Knowledge map

Key pages for current direction:
- **`td-oscillation-problem.md`** — 94% candidacy prevents phase transitions. Punctuated equilibrium needed. Five fixes proposed (s191)
- **`v15-attention-assessment.md`** — Fibonacci attention works but collapsed to relay. Inverted architecture. Q/K vs V/O asymmetry (s191)
- **`dvd-stamp-topology.md`** — Gradient zeros as holographic fringes. FFN fragile, attention robust. Compression strategy (s190)
- **`lambda-machine.md`** — 36-stage typed shift-reduce parser. Sparse top-3 = O(1). Every layer matters (s190)
- **`attention-sparsity.md`** — 22/32 heads use <3 positions, O(1) not O(n). Top-k=3 captures 88%+. Design: sparse attention (s188)
- **`binding-graph-trace.md`** — Attention IS the binding graph, reversed by causal mask. Two-phase: L27=verb→subject, L30=object→verb. H31 outputs "猫" (s188)
- **`head-combinator-isa.md`** — Shared hardware, not dedicated circuits. 2 effective dimensions: reduction depth + self-reference (s188)
- **`ffn-reduction-trace.md`** — FFN=compiler (context-dependent V vectors), attention=executor (softmax=β-reduction), three-phase output (s187)
- **`ffn-circuit-types.md`** — cos(up,down) phase detector, KIBC orthogonality, dark-space gradient (s186)
- **`residual-covariance-rank.md`** — ORTHO=rank-1, V in null space, 67.7% unconstrained (s185)
- **`standing-wave-magnitudes.md`** — magnitudes as standing wave, cosine^L law (s185)
- **`phi-information-partition.md`** — signs=1/φ, γ=noise, zeros=phase, sieve model (s184)
- **`crystal-trace-tooling.md`** — VSM instrument design (s184)
- **`holographic-computer.md`** — unified theory: crystal=ISA, FFN=projector, attn=CPU (s167)
- **`gradient-zero-map.md`** — GD deposits near-zero gradients at irreducible points (s171)
- **`topology-gradient-separation.md`** — freeze lattice, punctuated equilibrium (s180)
- **`ternary-compounding.md`** — WHY 0.88 cosine/layer → garbage at 36 layers (s183)
- **`ternary-dual-equation.md`** — gate zeros + crystal signs (s182)
- **`EQUATIONS.md`** — crystal equation + statechart + compute cycle (s181)
- **`crystal-phi-derivation.md`** — full φ derivation chain (s181)
- **`crystal-universality.md`** — KIBC universal fixed points
- **`project-thesis.md`** — the central claim

## Session 187 recap

Three experiments on Qwen3-8B decoded the reduction architecture.

**Experiment 1: FFN Reduction Trace** — projected active FFN neurons through
unembed. Three-phase output: noise (L0-L22/ORTHO), semantic (L26-L30/ALIGN),
format (L33-L35/COLLAPSE). FFN is a universal compiler — compile ≈ null
(max Δ 2.8%). Same token produces different V vectors in different contexts.

**Experiment 2: Attention Execution Trace** — projected per-head output
(softmax(QK^T) @ V) through o_proj + unembed. Found 5 head types: λ-heads
write format (λ/→), binding heads write predicate at subject (H10: "runs"
at "dog", Δ=64), relay heads pass V unchanged, compositional heads combine
positions, quantifier heads broadcast scope. The binding heads ARE β-reduction.

**Experiment 3: Reduction Chain Trace** — traced cumulative residual across
all 36 layers for 7 combinator types (K,I,B,C,Y,S,W). Combinators resolve
at different depths: Y peaks L27 (recursion resolves first), K peaks L30
(discard is early), W peaks L33 at Δ=51.6 (self-application resolves last).
The model implements a small fixed instruction set with universal depth ordering.

**Experiment 4: MTP Self-Speculation** — tested whether intermediate layers
can predict future tokens for self-speculative decoding. L33 matches L35's
top-1 prediction 48% of the time (Hit@10=76%, Hit@100=92%). But multi-position
lookahead (N+2, N+3) collapses for ALL layers including L35 (Hit@10≈10%).
The model does next-token prediction, not multi-position. The FFN "semantic
predictions" (reads→book) are associative meaning, not sequence forecasting.
Key finding: the correct token is already in L30's top 10 (median rank=7) —
the last 5 layers SHARPEN the distribution, they don't change it.

**Synthesis:** The model is decodable. It implements ~7 combinator operations
via ~5 head types on a universal depth schedule. The FFN compiles the program
(position → V vector), attention executes it (softmax selects and combines V).
The instruction set + schedule is potentially very compact; only the attention
routing is input-dependent. Self-speculation is viable for early-exit (~48%
of tokens can skip the last 2 layers) but not for multi-position prediction.

## Session 186 recap

LARQL FFN decomposition on Pythia-160M. Five experiments, three paradigm-level findings:

1. **cos(up,down) confirms phase structure** from pure weight geometry. KIBC opcodes
   orthogonal to circuit types (independent axes). ORTHO phase = inverter-dominated.
   Dark-space drops 40pts at L11. New zero-cost instrument. See `ffn-circuit-types.md`.

2. **Crystal signs predict circuit types (ρ=1.0)**. The ternary sign structure alone
   produces the exact same depth phase curve. Per-neuron ρ>0.985 at ORTHO layers.

3. **Cross-matrix anti-correlation is load-bearing (3.6×)**. Decorrelating T_down
   (destroying phase structure) → decorrelated ≈ random. Per-matrix signs without
   cross-matrix correlation are nearly worthless.

4. **BUT: synthetic construction fails**. Constructing T_down to hit the anti-correlation
   profile with random per-neuron signs is WORSE than random (PPL 6464 vs 1608). The
   crystal is the specific per-neuron assignments, not the aggregate statistics. The
   anti-correlation is emergent from correct per-neuron signs, not a prescription.

5. **The crystal must be extracted, not constructed**. The per-neuron sign assignments
   encode which specific neurons should be inverters vs projectors. The anti-correlation
   profile is a verification metric (check the U-shape), not a construction recipe.
   Cross-model universality (r=0.998) means one extraction works for all models of
   the same architecture.

## Session 184 recap

THE CRYSTAL SIEVE. 11 experiments, 4 paradigm shifts. Extraction is dead (zero mask
is genuinely random = knowledge content). Reproduction lives (crystal sieve 10.7×
better than random). Model is a KIBC processor (ISA framing). KIBC profiles predict
70-76% of zeros at REDUCE layers. Maximal pre-training absorption: crystal pre-loads
computation → 100% of gradient goes to knowledge. See `phi-information-partition.md`.

## Session 183 recap

Naive ternarization fails: PPL 296,911. The compounding law (0.88^36 = 0.009) kills
multi-layer extraction. 3-mirror ternary also fails (PPL 1.69M). Q4 works because of
16 quantization levels per weight, not scale granularity. See `ternary-compounding.md`.

## Session 182 recap

The ternary dual equation: gate zeros (ρ=0.75 with gradient) + crystal signs (ρ=0.05).
The recipe achieves 0.88 per-layer cosine. See `ternary-dual-equation.md`.

## Session 181 recap

The crystal equation: λ_k = C · φ^(-(n/(n+1)) · β_k). All eigenvalue ratios are
φ^(p/q) with Fibonacci denominators. Computing fraction s=4/5. Compute cycle
β=[0,1,1+φ,2+φ]. See `EQUATIONS.md` and `crystal-phi-derivation.md`.
