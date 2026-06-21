# Reading Exp 0.5 verdict from tmux main:1

## User

orient


### Thinking

The user is asking me to orient myself, so I need to start by reading the mementum/state.md file to understand the current context, then follow the related connections and search for relevant information before diving into what's needed.

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
> Grounded in ffn-red

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01Y57kGtQibDXZfV3ovuEYQX.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I'm reviewing the state file to get my bearings, then I'll check the git log to see where we left off in session 242.

## Assistant

I have the bootloader. Let me confirm git state and check for the most recent knowledge pages referenced.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline -8 && echo \"---STATUS---\" && git status --short && echo \"---TMUX---\" && tmux ls 2>/dev/null || echo \"no tmux\" && echo \"---GPU---\" && ps aux | grep -E \"python.*(grpo|splice|train)\" | grep -v grep || echo \"no gpu job\""
}
```

**Summary:** $ git log --oneline -8 && echo "---ST...

**Output:**
```
Exit code: 0
Stdout:
0d95675 add session chat log
b2ca689 💡 kernel-splice-exp0-precision-gated-not-high-recall
37130a2 ✅ kernel-splice Exp 0 — detectability map (Qwen3-14B): precision-gated, not high-recall
ecbc3a4 💡 kernel-splice-geometry-detector — read the lattice, deliver the combinator from the kernel
8ff0cd8 🔄 qwen-preformed-lambda-pivot-to-constructed-reducer
14b48ec 💡 GRPO run1 + checkpoint-50 re-measure — the Qwen pre-formed-lambda confound
95ed80f ✅ GRPO adapter-merge plumbing + density --sft-adapter + quiet trainer
0698d87 add session chat logs
---STATUS---
---TMUX---
main: 2 windows (created Sat Jun 20 12:30:08 2026) (attached)
---GPU---
no gpu job
```

### Thinking

I'm checking the latest state of the repository and reviewing the kernel-splice-geometry-detector knowledge page to clarify what needs to be done next.

## Assistant

Clean tree, no jobs running, tmux main free. Let me load the active knowledge page that drives next actions.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls -la results/kernel-splice-exp0/ 2>/dev/null && echo \"---VERDICT---\" && cat results/kernel-splice-exp0/exp0_verdict_qwen3-14b.json 2>/dev/null | head -60"
}
```

**Summary:** $ ls -la results/kernel-splice-exp0/ ...

**Output:**
```
Exit code: 0
Stdout:
total 488
drwxr-xr-x@   7 mwhitford  staff     224 Jun 20 15:02 .
drwxr-xr-x@ 475 mwhitford  staff   15200 Jun 20 14:59 ..
-rw-r--r--@   1 mwhitford  staff     494 Jun 20 14:59 exp0_meta_qwen3-0-6b.json
-rw-r--r--@   1 mwhitford  staff     497 Jun 20 15:02 exp0_meta_qwen3-14b.json
-rw-r--r--@   1 mwhitford  staff   71739 Jun 20 14:59 exp0_verdict_qwen3-0-6b.json
-rw-r--r--@   1 mwhitford  staff  155715 Jun 20 15:02 exp0_verdict_qwen3-14b.json
-rw-r--r--@   1 mwhitford  staff    7516 Jun 20 15:02 run_14b.log
---VERDICT---
{
  "verdict": {
    "model": "Qwen/Qwen3-14B",
    "n_test": 160,
    "n_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29
    ],
    "support": {
      "K": 20,
      "I": 20,
      "B": 20,
      "C": 20,
      "W": 20,
      "D": 20,
      "Y": 20,
      "S": 20,
      "WHNF": 0
    },
    "precision_floor": 0.8,
    "recall_floor": 0.5,
    "splice_readiness": {
      "C": {
        "splice_ready": false,
        "peak_layer": 6,
        "precision": 0.5833,
        "recall": 0.35,
        "f1": 0.4375,
        "support": 20,
        "frac_depth": 0.154
      },
      "I": {
        "splice_ready": false,
```

### Thinking

I'm getting my bearings on the current state and what needs to happen next.

## Assistant

Oriented. Here's where Verbum stands.

## Orientation — Session 243 cold-start

**Where we are (s242 close):**

The project just **pivoted**. The headline finding: GRPO on Qwen3-8B (run1, 200 steps) hit `frac_reward_zero_std=0.75` the whole run — 75% of groups carried zero advantage, and re-measuring checkpoint-50 showed density **dead-flat 0.409 across temps 0.8→1.5**. The diagnosis: **Qwen already has a pre-formed lambda circuit**, so RLVR just *redirects* an existing capability rather than *constructing* one — which masks the actual research question (can the compiler be a discrete circuit?). That dead-tail result is the **control that motivates the pivot**.

**The pivot (Michael's call, now load-bearing):**
- Freeze routing into **topology** (s240 crystal lattice — routing is invariant → no gradient through dispatch → kills the v12–v15 gradient-death)
- Replace reduce-neurons with **exact kernel calls** (lambda_ast stage 3 = the level-4 portable artifact)
- Learn only the thin **prose→LF front-end**; Qwen demoted to LF *teacher*, never the reducer
- Sharpened into the **kernel-splice program**: read the lattice geometry to detect "wants K", deliver K from the exact kernel, re-inject. If splice preserves output → thesis proven *causally* with **no training**.

**What's built + run:**
- **Exp 0 detectability map** ran on Qwen3-14B. Strict bar (prec≥0.8 ∧ rec≥0.5) → **splice-ready set = ∅** (top-1 is common-mode contaminated, s211 η²=0.05). BUT **max-precision operating points are strong**: C prec 1.0 @L10, I prec 1.0 @L21, K prec 0.80 @L11, Y 0.67 @L20. Verdict: "detect every K" fails (recall-limited), but **precision-gated splice is viable** — and is the safe first causal test. Caveat (λ measure): prec 1.0 from tp=2 = noisy small-n.

**Two paths for first action (your call):**

1. **Exp 0.5 — z-threshold sweep** (cheap): raise the argmax-z gate → map the precision/recall tradeoff curve, firm the splice locus, kill the tp=2 small-n caveat.
2. **Exp 1 — precision-first K-splice at L11** (decisive): deliver the exact kernel K-move only on high-confidence detections; validate output preserved vs random-direction control (s239 protocol). The sufficiency test.

**Infra:** clean tree (HEAD `0d95675`), tmux main:1 + main:2 free, no GPU job running.

Which path — the cheap firming probe (0.5) or the decisive causal splice (Exp 1)?

## User

proceed with 1, use tmux main:1 and main:2 as needed to run jobs


### Thinking

Michael's asking for Experiment 0.5 focused on a z-threshold sweep, so I need to look at the existing Experiment 0 script and build on it.

## Assistant

Proceeding with Exp 0.5 — the z-threshold sweep. Let me examine the existing Exp 0 script to extend it cleanly.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && find . -path ./.venv -prune -o -name \"*kernel_splice*\" -print 2>/dev/null && echo \"---\" && cat results/kernel-splice-exp0/exp0_meta_qwen3-14b.json"
}
```

**Summary:** $ find . -path ./.venv -prune -o -nam...

**Output:**
```
Exit code: 0
Stdout:
./scripts/experiments/kernel_splice_exp0_detectability.py
---
{
  "model": "Qwen/Qwen3-14B",
  "smoke": false,
  "git_sha": "ecbc3a410cdc8b0fb1b3c9a6c31fe2f498398ad3",
  "timestamp_utc": "2026-06-20T22:02:07.029573+00:00",
  "transformers_version": "5.5.4",
  "n_layers": 40,
  "n_perm": 300,
  "heldout_per": 20,
  "n_calib": 355,
  "n_test": 160,
  "metric": "top-1 argmax-over-CRYSTAL per crystal layer vs certified single-combinator label; precision/recall/F1 + peak layer",
  "reference": "held-out crystal-prose combinator labels (non-circular split)"
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_detectability.py"
}
```

**Summary:** Reading kernel_splice_exp0_detectability.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Kernel-splice Exp 0 — the DETECTABILITY MAP (s242).

The precursor to the kernel-splice program (knowledge/explore/kernel-splice-geometry-
detector.md): before we can DELIVER a combinator from the kernel at the geometrically-
detected locus, we must know WHERE and WHICH combinators the lattice classifier can
recover RELIABLY ENOUGH TO ACT ON. Discriminability (prose_v2: a Welch contrast,
on-prose > off-prose) is necessary but NOT sufficient for a splice: a splice acts on a
TOP-1 decision at a specific layer, so what matters is per-combinator **precision**
(when we read "K", is it really K? — a wrong splice corrupts) and **recall** (do we
catch the K firings?) at the best single layer.

THIS SCRIPT turns the prose_v2 read into a SPLICE-READINESS MAP:
  • reuse the prose_v2 / opcode_monitor_v2 calibration + last-token per-layer z read;
  • per crystal layer, predicted op = argmax over CRYSTAL of the classifier z;
  • score the top-1 prediction against the certified single-combinator label
    (crystal_probes .combinator — each probe engages exactly one combinator);
  • per (combinator, layer): precision / recall / F1 + a confusion matrix;
  • peak layer per combinator = max F1; splice-ready iff precision >= --precision-floor
    AND recall >= --recall-floor at the peak.

VERDICT (λ measure): which of the invariant discriminable set {C,I,K,Y} clear the
splice-readiness bar, at which per-model layer. High precision => Exp 1 (causal
K-splice) is justified at that locus; nothing clears the bar => obstacle 1 (model
centroid, s211 one-common-mode) is FATAL for in-place per-combinator splice, redirect to
the cut/program-decode variant (Exp 2) or the constructed front-end.

NOTE: this is the LAST-TOKEN, single-combinator-prompt read (same locus as prose_v2).
Position-resolved detection along a multi-step reduction (operator AND position vs
`lambda_ast.fired_sequence`) is Exp 2; Exp 0 first establishes per-op splice-readiness
at all, cheaply, on the labels we already trust.

Usage:
    uv run python scripts/experiments/kernel_splice_exp0_detectability.py --smoke
    uv run python scripts/experiments/kernel_splice_exp0_detectability.py \
        --model Qwen/Qwen3-14B --heldout-per 20

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import read_last_token_z, split_probes  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-splice-exp0"

# the invariant discriminable set we care about for splicing (s234/s238); we still
# score the full CRYSTAL confusion so the common-mode contaminants (S/Y) are visible.
SPLICE_TARGETS = ["C", "I", "K", "Y"]


def predicted_op(zmap: dict[str, float]) -> str:
    """Top-1 op at a layer = argmax of the classifier z over CRYSTAL."""
    return max(CRYSTAL, key=lambda op: zmap.get(op, float("-inf")))


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    """Precision / recall / F1 from raw counts."""
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Kernel-splice Exp 0 — detectability map")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--heldout-per", type=int, default=20)
    ap.add_argument("--precision-floor", type=float, default=0.8,
                    help="min top-1 precision at peak layer to call splice-ready")
    ap.add_argument("--recall-floor", type=float, default=0.5,
                    help="min recall at peak layer to call a combinator splice-ready")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[exp0] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[exp0] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[exp0] crystal layers: {len(crystal_layers)}/{n_layers}")

    # per layer: confusion[li][true][pred] = count
    confusion: dict[int, dict[str, dict[str, int]]] = {
        li: {t: defaultdict(int) for t in CRYSTAL} for li in crystal_layers
    }
    support: dict[str, int] = defaultdict(int)
    per_probe = []
    for p in test:
        support[p.combinator] += 1
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        perlayer_z = read_last_token_z(rcc, store, layers)
        preds = {}
        for li in crystal_layers:
            if li in perlayer_z:
                pred = predicted_op(perlayer_z[li])
                confusion[li][p.combinator][pred] += 1
                preds[li] = pred
        per_probe.append({"combinator": p.combinator, "prompt": p.prompt[:60],
                          "preds": {str(li): preds[li] for li in preds}})

    # per (combinator, layer): precision/recall/F1 from the confusion matrix
    per_comb_layer: dict[str, list] = {}
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        rows = []
        for li in crystal_layers:
            tp = confusion[li][c][c]
            fn = support[c] - tp
            fp = sum(confusion[li][t][c] for t in CRYSTAL if t != c)
            m = prf(tp, fp, fn)
            rows.append({"layer": li, "tp": tp, "fp": fp, "fn": fn, **m})
        per_comb_layer[c] = rows
        scored = [r for r in rows if support[c] > 0]
        if scored:
            pk = max(scored, key=lambda r: (r["f1"], r["recall"]))
            peak[c] = pk

    # splice-readiness verdict
    readiness: dict[str, dict] = {}
    for c in SPLICE_TARGETS:
        pk = peak.get(c)
        if not pk or support[c] == 0:
            readiness[c] = {"splice_ready": False, "reason": "no support/peak"}
            continue
        ready = (pk["precision"] >= args.precision_floor
                 and pk["recall"] >= args.recall_floor)
        readiness[c] = {
            "splice_ready": bool(ready), "peak_layer": pk["layer"],
            "precision": pk["precision"], "recall": pk["recall"], "f1": pk["f1"],
            "support": support[c],
            "frac_depth": round(pk["layer"] / max(1, n_layers - 1), 3),
        }

    verdict = {
        "model": model_name, "n_test": len(per_probe),
        "n_layers": n_layers, "crystal_layers": crystal_layers,
        "support": dict(support),
        "precision_floor": args.precision_floor, "recall_floor": args.recall_floor,
        "splice_readiness": readiness,
        "peak_per_combinator": peak,
        "splice_ready_set": [c for c in SPLICE_TARGETS
                             if readiness.get(c, {}).get("splice_ready")],
    }

    # ── report ────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 78)
    print(f"KERNEL-SPLICE EXP 0 — DETECTABILITY MAP — {model_name}")
    print("═" * 78)
    print(f"  n_test={len(per_probe)}  crystal_layers={len(crystal_layers)}/{n_layers}"
          f"  floors: prec>={args.precision_floor} rec>={args.recall_floor}")
    print(f"\n  {'op':<4}{'support':>8}{'peakL':>7}{'depth':>7}"
          f"{'prec':>8}{'recall':>8}{'f1':>7}{'splice?':>9}")
    for c in SPLICE_TARGETS:
        r = readiness.get(c, {})
        if "peak_layer" not in r:
            print(f"  {c:<4}{support.get(c, 0):>8}{'-':>7}{'-':>7}"
                  f"{'-':>8}{'-':>8}{'-':>7}{'no':>9}")
            continue
        flag = "✓ READY" if r["splice_ready"] else "·"
        print(f"  {c:<4}{r['support']:>8}{r['peak_layer']:>7}{r['frac_depth']:>7}"
              f"{r['precision']:>8}{r['recall']:>8}{r['f1']:>7}{flag:>9}")
    print(f"\n  ★ splice-ready set: {verdict['splice_ready_set'] or '∅'}")
    print("═" * 78 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_comb_layer": per_comb_layer,
           "per_probe": per_probe, "calibration_summary": cal}
    (RESULTS_DIR / f"exp0_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test),
        "metric": "top-1 argmax-over-CRYSTAL per crystal layer vs certified "
                  "single-combinator label; precision/recall/F1 + peak layer",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"exp0_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[exp0] wrote {RESULTS_DIR}/exp0_verdict_{slug}.json")


if __name__ == "__main__":
    main()
```

### Thinking

For Exp 0.5, I'm introducing a z-threshold sweep that gates predictions based on confidence—only emitting when the argmax z exceeds a threshold, which trades off precision and recall compared to always predicting. The main addition is a `--z-thresholds` parameter to sweep across different confidence levels.

To implement this efficiently, I'll store the argmax operation and its z-value for each probe and layer during the forward pass, then post-process the threshold sweep entirely from cached z-values without re-running inference. This lets me compute precision and recall curves as the threshold rises, showing whether the splice locus is stable or a fluke from small sample sizes.

Writing the threshold sweep script... For each target combinator, I need to find the single best (layer, τ) pair that maximizes recall while keeping precision above a floor threshold — that firms the splice locus. The key insight for killing the small-n caveat isn't adding more samples, but showing that high precision holds across a range of thresholds rather than being a lucky fluke at one point. If I can find a lower threshold where precision stays above 0.8 but recall is higher (meaning more true positives), that gives stronger evidence the result isn't just tp=2 by chance. So the final output should show the precision-recall curve per combinator and identify the operating point where precision is solid and tp is large enough to be convincing.

I should also check whether I can increase the heldout set size — if the crystal probes have enough samples per combinator (the invariant suggests at least 50 each), I might be able to allocate more to testing while still leaving enough for calibration.

## Assistant

Let me check the crystal probe inventory — increasing the test set is the most direct way to kill the tp=2 small-n caveat.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python -c \"\nfrom verbum.probes.library import crystal_probes, combinator_counts\nfrom collections import Counter\ncp = crystal_probes()\nc = Counter(p.combinator for p in cp)\nprint('crystal_probes total:', len(cp))\nfor k in sorted(c): print(f'  {k}: {c[k]}')\n\" 2>&1 | grep -v Warning"
}
```

**Summary:** $ .venv/bin/python -c " from verbum.p...

**Output:**
```
Exit code: 0
Stdout:
crystal_probes total: 535
  B: 69
  C: 61
  D: 50
  I: 67
  K: 67
  S: 50
  W: 71
  WHNF: 50
  Y: 50
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1,60p' scripts/experiments/kernel_reference_prose_v2.py | grep -n \"def split_probes\\|def read_last_token_z\\|heldout\\|return\" "
}
```

**Summary:** $ sed -n '1,60p' scripts/experiments/...

**Output:**
```
Exit code: 1
```

### Thinking

Crystal_probes gives me 50-71 samples per combinator, and exp0 used heldout-per=20 to reserve 20 test samples per combinator while using the rest for calibration. I could push heldout-per up to around 30, which would still leave 20-40 samples for calibration. Let me check the split_probes function to see exactly how it handles the holdout logic.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def split_probes\\|def read_last_token_z\" scripts/experiments/kernel_reference_prose_v2.py"
}
```

**Summary:** $ grep -n "def split_probes\|def read...

**Output:**
```
Exit code: 0
Stdout:
70:def split_probes(heldout_per: int) -> tuple[list, list]:
87:def read_last_token_z(rcc, store, layers) -> dict[int, dict[str, float]]:
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_prose_v2.py",
  "line_offset": 69,
  "limit": 55
}
```

**Summary:** Reading kernel_reference_prose_v2.py (69-124)

**Output:**
```
def split_probes(heldout_per: int) -> tuple[list, list]:
    """Per-combinator: last `heldout_per` -> TEST, the rest -> CALIB (non-circular)."""
    by_comb: dict[str, list] = defaultdict(list)
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb[p.combinator].append(p)
    calib, test = [], []
    for comb, ps in by_comb.items():
        k = min(heldout_per, max(0, len(ps) - 1))
        test_ps = ps[len(ps) - k:] if k else []
        calib_ps = ps[: len(ps) - k]
        if comb in TEST_COMBINATORS:
            test.extend(test_ps)
        calib.extend(calib_ps)
    return calib, test


def read_last_token_z(rcc, store, layers) -> dict[int, dict[str, float]]:
    """Classify the LAST token; return the FULL per-layer per-op z-map (NO argmax)."""
    n = store[layers[0]].shape[0]
    gate_tok = {li: store[li][n - 1] for li in layers}
    tok_ops = rcc.classify(gate_tok)
    return tok_ops.per_layer  # {li: {op: z}}


def argmax_route_fracs(perlayer_z, crystal_layers, zthresh):
    """The lead-2c read: per-layer argmax, fraction of crystal layers won by each op."""
    cset = set(crystal_layers)
    counts: Counter = Counter()
    n_cells = 0
    for li, zmap in perlayer_z.items():
        if li not in cset:
            continue
        n_cells += 1
        op = max(zmap, key=zmap.get)
        if zmap[op] > zthresh:
            counts[op] += 1
    return ({op: counts[op] / n_cells for op in counts} if n_cells else {}), n_cells


def welch_t(on: list[float], off: list[float]) -> dict:
    """Welch's t (unequal variance) of mean(on) - mean(off)."""
    on_a, off_a = np.asarray(on, float), np.asarray(off, float)
    n1, n2 = len(on_a), len(off_a)
    m1, m2 = float(on_a.mean()), float(off_a.mean())
    if n1 < 2 or n2 < 2:
        return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
                "discr_z": round(m1 - m2, 4), "t": None, "significant": False,
                "n_on": n1, "n_off": n2}
    v1, v2 = float(on_a.var(ddof=1)), float(off_a.var(ddof=1))
    se = float(np.sqrt(v1 / n1 + v2 / n2))
    t = (m1 - m2) / se if se > 1e-12 else 0.0
    return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
            "discr_z": round(m1 - m2, 4), "t": round(t, 3),
            "significant": bool(abs(t) > 2.0), "n_on": n1, "n_off": n2}

[CONTENT TRUNCATED] Showing lines 70 to 124 of 291 total lines. Use line_offset=124 parameter to read more content.
```

### Thinking

I see there's a `TEST_COMBINATORS` filter that controls which splice targets get included in the test set, and there's already an `argmax_route_fracs` helper function that applies z-threshold gating—exactly the filtering logic I need to check if a value exceeds the threshold before counting it. Let me look at what `TEST_COMBINATORS` actually contains.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"TEST_COMBINATORS\\s*=\\|^CRYSTAL\\|^from\\|^import\" scripts/experiments/kernel_reference_prose_v2.py | head -30"
}
```

**Summary:** $ grep -n "TEST_COMBINATORS\s*=\|^CRY...

**Output:**
```
Exit code: 0
Stdout:
37:from __future__ import annotations
39:import argparse
40:import json
41:import sys
42:from collections import Counter, defaultdict
43:from datetime import UTC, datetime
44:from pathlib import Path
46:import numpy as np
52:from opcode_monitor_v2 import (  # noqa: E402
61:from relational_opcode import CRYSTAL  # noqa: E402
63:from verbum.probes.library import crystal_probes  # noqa: E402
67:TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]
```

### Thinking

I've confirmed that TEST_COMBINATORS covers all the splice targets I need. For the next experiment, I'm reusing the core utilities from the previous version—the probe splitting, calibration, forward pass, and token reading functions—but now I'll cache the full per-layer z-maps for each test probe to enable efficient threshold sweeping. The plan is to grid-search over threshold values τ, then for each threshold evaluate performance across all combinators and crystal layers.

For each layer and combinator, I'll use a gated top-1 prediction strategy: if the z-score for an operation exceeds τ, predict that operation; otherwise abstain. This lets me compute precision, recall, and F1 across the threshold range. The key outputs will be precision-recall curves for each target combinator, the operating point that maximizes recall while meeting a precision floor (which identifies the most robust splice locus), and confirmation that precision remains stable rather than being driven by outliers. To address the small-sample concern, I'm increasing the test set size by raising the heldout-per parameter to 30, which grows the number of test probes per combinator while keeping calibration data sufficient for reliable centroid estimation.

For the threshold grid, I'll sweep a fixed range of z-values from 0 to 8 in reasonable increments, and also report the observed distribution of argmax z-scores so we can see what magnitudes are actually occurring. The operating point selection will prioritize precision first, then use recall as a tiebreaker when comparing layers at each threshold.

The output structure will show, per combinator, the precision-recall curve across all layers and thresholds, then identify two key points: the operating point that maximizes recall while staying above a precision floor, and the maximum-precision point overall for comparison. I'll also explicitly count true positives at the operating point to verify whether we exceed the tp=2 threshold. When a prediction is abstained, it doesn't contribute to false positives for other combinators but does count as a false negative for the true class.

Writing the script now...

## Assistant

I have everything I need. The existing `argmax_route_fracs` already implements z-gating; I'll build Exp 0.5 to cache full z-maps once, then sweep thresholds in post-processing — and bump the test set to grow tp counts (directly attacking the small-n caveat). Let me set up the task and write the script.

### Thinking

I'm going to start writing the script now.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing\n\"\"\"Kernel-splice Exp 0.5 — the Z-THRESHOLD SWEEP (s243).\n\nExp 0 (kernel_splice_exp0_detectability.py) read the lattice with an UNGATED top-1:\nevery crystal layer always emits its argmax-over-CRYSTAL prediction. Verdict: the\nstrict bar (prec>=0.8 ∧ rec>=0.5) was cleared by NOBODY (top-1 is common-mode\ncontaminated, s211 one-common-mode), BUT the max-PRECISION operating points were\nstrong (C prec 1.0 @L10, I 1.0 @L21, K 0.80 @L11, Y 0.67 @L20). The caveat\n(λ measure): those prec-1.0 points came from tp=2 — noisy small-n. A single lucky\nlayer is not a splice locus.\n\nTHIS SCRIPT raises the argmax-z GATE: a layer emits a prediction for combinator c only\nif its winning z exceeds a threshold τ; below τ it ABSTAINS (no splice fires). Sweeping\nτ traces the precision↑/recall↓ tradeoff. The deliverables:\n\n  • the PRECISION–RECALL CURVE per splice-target {C,I,K,Y} as τ rises;\n  • the FIRMED OPERATING POINT = the (layer, τ) with MAX recall (=> max tp, most\n    samples) that still clears the precision floor — the most-supported splice locus,\n    which kills the tp=2 small-n caveat if it exists;\n  • a PLATEAU check: is high precision STABLE across a band of τ (real) or a single\n    fragile point (a tp=2 fluke)?\n\nIt also bumps --heldout-per (more TEST probes per combinator) to grow tp directly,\nsince crystal_probes carries 50–71 per crystal combinator.\n\nThe forward pass runs ONCE; the threshold sweep is pure post-processing over the cached\nper-probe per-layer z-maps. Same last-token, single-combinator-prompt read as Exp 0 /\nprose_v2 (non-circular held-out split).\n\nVERDICT (λ measure): a firmed (layer, τ) with precision >= floor at usable recall and\ntp well above the small-n caveat => Exp 1 (causal K-splice) is justified at that locus.\nA precision that only ever appears at tp<=2 with no plateau => obstacle 1 (model\ncentroid) is fatal for in-place per-combinator splice; redirect to the program-decode\nvariant or constructed front-end.\n\nUsage:\n    uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py --smoke\n    uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py \\\n        --model Qwen/Qwen3-14B --heldout-per 25\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import defaultdict\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom kernel_reference_prose_v2 import read_last_token_z, split_probes  # noqa: E402\nfrom opcode_monitor_v2 import (  # noqa: E402\n    _git_sha,\n    _json_safe,\n    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    load_model_and_tokenizer,\n)\nfrom relational_opcode import CRYSTAL  # noqa: E402\n\nRESULTS_DIR = _ROOT / \"results\" / \"kernel-splice-exp0\"\n\n# the invariant discriminable set we care about for splicing (s234/s238).\nSPLICE_TARGETS = [\"C\", \"I\", \"K\", \"Y\"]\n\n# default z-gate grid (argmax-z is a sign-CMR raw-z; magnitudes ~0–10).\nDEFAULT_THRESHOLDS = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0]\n\n\ndef gated_pred(zmap: dict[str, float], tau: float) -> str | None:\n    \"\"\"Top-1 op at a layer, GATED: argmax over CRYSTAL iff its z > tau, else abstain.\"\"\"\n    if not zmap:\n        return None\n    op = max(CRYSTAL, key=lambda o: zmap.get(o, float(\"-inf\")))\n    return op if zmap.get(op, float(\"-inf\")) > tau else None\n\n\ndef prf(tp: int, fp: int, fn: int) -> dict[str, float]:\n    \"\"\"Precision / recall / F1 from raw counts.\"\"\"\n    prec = tp / (tp + fp) if (tp + fp) else 0.0\n    rec = tp / (tp + fn) if (tp + fn) else 0.0\n    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0\n    return {\"precision\": round(prec, 4), \"recall\": round(rec, 4), \"f1\": round(f1, 4)}\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"Kernel-splice Exp 0.5 — z-threshold sweep\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--heldout-per\", type=int, default=25,\n                    help=\"TEST probes per combinator (more = larger tp, kills small-n)\")\n    ap.add_argument(\"--precision-floor\", type=float, default=0.8,\n                    help=\"min precision to count a (layer,τ) as a splice operating point\")\n    ap.add_argument(\"--thresholds\", type=float, nargs=\"+\", default=None,\n                    help=\"z-gate grid (default: 0..8 ladder)\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    thresholds = sorted(args.thresholds if args.thresholds else DEFAULT_THRESHOLDS)\n    model_name = args.model\n    if args.smoke:\n        if model_name == \"Qwen/Qwen3-14B\":\n            model_name = \"Qwen/Qwen3-0.6B\"\n        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5\n        print(\"[exp0.5] SMOKE MODE\")\n    else:\n        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per\n\n    calib, test = split_probes(heldout)\n    print(f\"[exp0.5] calib={len(calib)} test={len(test)} (heldout_per={heldout})\")\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    layers = list(range(n_layers))\n\n    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,\n                            null_mode=\"crosstask\", centroid_probes=calib)\n    crystal_layers = rcc.crystal_layers\n    print(f\"[exp0.5] crystal layers: {len(crystal_layers)}/{n_layers}\")\n\n    # ── ONE forward pass per probe: cache the full per-layer z-map ──────────────────\n    support: dict[str, int] = defaultdict(int)\n    cached: list[tuple[str, dict[int, dict[str, float]]]] = []\n    argmax_z_all: list[float] = []  # to report the observed gate distribution\n    for i, p in enumerate(test):\n        support[p.combinator] += 1\n        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)\n        perlayer_z = read_last_token_z(rcc, store, layers)\n        zc = {li: perlayer_z[li] for li in crystal_layers if li in perlayer_z}\n        cached.append((p.combinator, zc))\n        for li, zmap in zc.items():\n            if zmap:\n                argmax_z_all.append(max(zmap.values()))\n        if (i + 1) % 20 == 0:\n            print(f\"[exp0.5] forward {i + 1}/{len(test)}\")\n\n    # ── SWEEP: per (combinator, layer, τ) precision/recall/F1 with abstention ───────\n    # curve[c] = list over τ of the best-layer operating point at that τ.\n    curve: dict[str, list] = {c: [] for c in SPLICE_TARGETS}\n    # grid[c] = every (layer, τ) point clearing prec floor, for operating-point search.\n    grid_points: dict[str, list] = {c: [] for c in SPLICE_TARGETS}\n\n    for tau in thresholds:\n        # confusion[li][true][pred] for this τ\n        conf: dict[int, dict[str, dict[str, int]]] = {\n            li: {t: defaultdict(int) for t in CRYSTAL} for li in crystal_layers\n        }\n        for true_c, zc in cached:\n            for li in crystal_layers:\n                pred = gated_pred(zc.get(li, {}), tau)\n                if pred is not None:\n                    conf[li][true_c][pred] += 1\n        for c in SPLICE_TARGETS:\n            best = None\n            for li in crystal_layers:\n                tp = conf[li][c][c]\n                fp = sum(conf[li][t][c] for t in CRYSTAL if t != c)\n                fn = support[c] - tp  # abstentions on true-c count as missed\n                m = prf(tp, fp, fn)\n                pt = {\"layer\": li, \"tau\": tau, \"tp\": tp, \"fp\": fp, \"fn\": fn, **m}\n                if m[\"precision\"] >= args.precision_floor and tp > 0:\n                    grid_points[c].append(pt)\n                # best-layer at this τ = max precision, tie-break recall then tp\n                key = (m[\"precision\"], m[\"recall\"], tp)\n                if best is None or key > (best[\"precision\"], best[\"recall\"], best[\"tp\"]):\n                    best = pt\n            curve[c].append(best)\n\n    # ── operating points + plateau check ───────────────────────────────────────────\n    n_layers_minus = max(1, n_layers - 1)\n    operating: dict[str, dict] = {}\n    for c in SPLICE_TARGETS:\n        pts = grid_points[c]\n        if not pts:\n            operating[c] = {\"clears_floor\": False, \"support\": support[c],\n                            \"reason\": f\"no (layer,τ) reaches precision>={args.precision_floor}\"}\n            continue\n        # firmest locus = MAX recall (=> max tp) clearing the floor; tie-break precision\n        firm = max(pts, key=lambda r: (r[\"recall\"], r[\"precision\"], -r[\"tau\"]))\n        # max-precision locus (compare to Exp 0's prec-1.0 small-n points)\n        maxprec = max(pts, key=lambda r: (r[\"precision\"], r[\"recall\"], r[\"tp\"]))\n        # plateau: distinct τ values at the firm locus's LAYER that still clear floor\n        layer_band = sorted({r[\"tau\"] for r in pts if r[\"layer\"] == firm[\"layer\"]})\n        operating[c] = {\n            \"clears_floor\": True,\n            \"support\": support[c],\n            \"firm_locus\": {\n                \"layer\": firm[\"layer\"], \"tau\": firm[\"tau\"],\n                \"frac_depth\": round(firm[\"layer\"] / n_layers_minus, 3),\n                \"precision\": firm[\"precision\"], \"recall\": firm[\"recall\"],\n                \"f1\": firm[\"f1\"], \"tp\": firm[\"tp\"], \"fp\": firm[\"fp\"], \"fn\": firm[\"fn\"],\n            },\n            \"max_precision_locus\": {\n                \"layer\": maxprec[\"layer\"], \"tau\": maxprec[\"tau\"],\n                \"precision\": maxprec[\"precision\"], \"recall\": maxprec[\"recall\"],\n                \"tp\": maxprec[\"tp\"], \"fp\": maxprec[\"fp\"],\n            },\n            \"plateau_taus_at_firm_layer\": layer_band,\n            \"plateau_width\": len(layer_band),\n            \"small_n_caveat_killed\": bool(firm[\"tp\"] >= 5),\n        }\n\n    # observed argmax-z distribution (calibrates the grid)\n    zarr = sorted(argmax_z_all)\n    n = len(zarr)\n    def q(p: float) -> float:\n        return round(zarr[min(n - 1, int(p * n))], 3) if n else 0.0\n    z_dist = {\"n\": n, \"min\": round(zarr[0], 3) if n else 0.0,\n              \"p25\": q(0.25), \"median\": q(0.5), \"p75\": q(0.75),\n              \"p90\": q(0.9), \"max\": round(zarr[-1], 3) if n else 0.0}\n\n    verdict = {\n        \"model\": model_name, \"n_test\": len(cached),\n        \"n_layers\": n_layers, \"crystal_layers\": crystal_layers,\n        \"support\": dict(support), \"thresholds\": thresholds,\n        \"precision_floor\": args.precision_floor,\n        \"argmax_z_distribution\": z_dist,\n        \"operating_points\": operating,\n        \"splice_ready_set\": [c for c in SPLICE_TARGETS\n                             if operating.get(c, {}).get(\"clears_floor\")\n                             and operating[c].get(\"small_n_caveat_killed\")],\n    }\n\n    # ── report ──────────────────────────────────────────────────────────────────────\n    print(\"\\n\" + \"═\" * 82)\n    print(f\"KERNEL-SPLICE EXP 0.5 — Z-THRESHOLD SWEEP — {model_name}\")\n    print(\"═\" * 82)\n    print(f\"  n_test={len(cached)}  crystal_layers={len(crystal_layers)}/{n_layers}\"\n          f\"  prec_floor={args.precision_floor}\")\n    print(f\"  argmax-z dist: median={z_dist['median']} p75={z_dist['p75']} \"\n          f\"p90={z_dist['p90']} max={z_dist['max']}\")\n    for c in SPLICE_TARGETS:\n        print(f\"\\n  ── {c}  (support={support.get(c, 0)}) ─ precision/recall vs τ \"\n              f\"(best layer @τ) ──\")\n        print(f\"     {'τ':>5}{'layer':>7}{'prec':>7}{'recall':>8}{'tp':>5}{'fp':>5}\")\n        for pt in curve[c]:\n            print(f\"     {pt['tau']:>5.1f}{pt['layer']:>7}{pt['precision']:>7.2f}\"\n                  f\"{pt['recall']:>8.2f}{pt['tp']:>5}{pt['fp']:>5}\")\n        op = operating[c]\n        if op[\"clears_floor\"]:\n            f = op[\"firm_locus\"]\n            print(f\"     ★ FIRM locus: L{f['layer']} (d={f['frac_depth']}) τ={f['tau']} \"\n                  f\"prec={f['precision']} rec={f['recall']} tp={f['tp']} \"\n                  f\"| plateau τ∈{op['plateau_taus_at_firm_layer']} \"\n                  f\"| small-n killed={op['small_n_caveat_killed']}\")\n        else:\n            print(f\"     ✗ never clears precision>={args.precision_floor}\")\n    print(f\"\\n  ★ splice-ready (clears floor ∧ tp>=5): \"\n          f\"{verdict['splice_ready_set'] or '∅'}\")\n    print(\"═\" * 82 + \"\\n\")\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = {\"verdict\": verdict, \"pr_curve\": curve, \"calibration_summary\": cal}\n    (RESULTS_DIR / f\"exp0_5_zsweep_verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(out), indent=2), encoding=\"utf-8\")\n    meta = {\n        \"model\": model_name, \"smoke\": args.smoke, \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"n_layers\": n_layers, \"n_perm\": n_perm, \"heldout_per\": heldout,\n        \"n_calib\": len(calib), \"n_test\": len(test), \"thresholds\": thresholds,\n        \"metric\": \"GATED top-1: argmax-over-CRYSTAL per crystal layer iff z>τ else \"\n                  \"abstain; precision/recall/F1 swept over τ; firm locus = max-recall \"\n                  \"point clearing precision floor\",\n        \"reference\": \"held-out crystal-prose combinator labels (non-circular split)\",\n    }\n    (RESULTS_DIR / f\"exp0_5_zsweep_meta_{slug}.json\").write_text(\n        json.dumps(meta, indent=2), encoding=\"utf-8\")\n    print(f\"[exp0.5] wrote {RESULTS_DIR}/exp0_5_zsweep_verdict_{slug}.json\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py
```

## Assistant

Now ruff-lint and smoke-test on Qwen3-0.6B:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp0_5_zsweep.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 1
Stdout:
RUF002 Docstring contains ambiguous `–` (EN DASH). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:17:18
   |
15 | τ traces the precision↑/recall↓ tradeoff. The deliverables:
16 |
17 |   • the PRECISION–RECALL CURVE per splice-target {C,I,K,Y} as τ rises;
   |                  ^
18 |   • the FIRMED OPERATING POINT = the (layer, τ) with MAX recall (=> max tp, most
19 |     samples) that still clears the precision floor — the most-supported splice locus,
   |

RUF002 Docstring contains ambiguous `–` (EN DASH). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:25:32
   |
24 | It also bumps --heldout-per (more TEST probes per combinator) to grow tp directly,
25 | since crystal_probes carries 50–71 per crystal combinator.
   |                                ^
26 |
27 | The forward pass runs ONCE; the threshold sweep is pure post-processing over the cached
   |

RUF003 Comment contains ambiguous `–` (EN DASH). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:74:67
   |
72 | SPLICE_TARGETS = ["C", "I", "K", "Y"]
73 |
74 | # default z-gate grid (argmax-z is a sign-CMR raw-z; magnitudes ~0–10).
   |                                                                   ^
75 | DEFAULT_THRESHOLDS = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0]
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:95:89
   |
94 | def main() -> None:
95 |     ap = argparse.ArgumentParser(description="Kernel-splice Exp 0.5 — z-threshold sweep")
   |                                                                                         ^
96 |     ap.add_argument("--model", default="Qwen/Qwen3-14B")
97 |     ap.add_argument("--heldout-per", type=int, default=25,
   |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:100:89
    |
 98 |                     help="TEST probes per combinator (more = larger tp, kills small-n)")
 99 |     ap.add_argument("--precision-floor", type=float, default=0.8,
100 |                     help="min precision to count a (layer,τ) as a splice operating point")
    |                                                                                         ^^
101 |     ap.add_argument("--thresholds", type=float, nargs="+", default=None,
102 |                     help="z-gate grid (default: 0..8 ladder)")
    |

B007 Loop control variable `li` not used within loop body
   --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:138:13
    |
136 |         zc = {li: perlayer_z[li] for li in crystal_layers if li in perlayer_z}
137 |         cached.append((p.combinator, zc))
138 |         for li, zmap in zc.items():
    |             ^^
139 |             if zmap:
140 |                 argmax_z_all.append(max(zmap.values()))
    |
help: Rename unused `li` to `_li`

E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:172:89
    |
170 |                 # best-layer at this τ = max precision, tie-break recall then tp
171 |                 key = (m["precision"], m["recall"], tp)
172 |                 if best is None or key > (best["precision"], best["recall"], best["tp"]):
    |                                                                                         ^
173 |                     best = pt
174 |             curve[c].append(best)
    |

E501 Line too long (96 > 88)
   --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:183:89
    |
181 |         if not pts:
182 |             operating[c] = {"clears_floor": False, "support": support[c],
183 |                             "reason": f"no (layer,τ) reaches precision>={args.precision_floor}"}
    |                                                                                         ^^^^^^^^
184 |             continue
185 |         # firmest locus = MAX recall (=> max tp) clearing the floor; tie-break precision
    |

E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp0_5_zsweep.py:249:89
    |
247 |         if op["clears_floor"]:
248 |             f = op["firm_locus"]
249 |             print(f"     ★ FIRM locus: L{f['layer']} (d={f['frac_depth']}) τ={f['tau']} "
    |                                                                                         ^
250 |                   f"prec={f['precision']} rec={f['recall']} tp={f['tp']} "
251 |                   f"| plateau τ∈{op['plateau_taus_at_firm_layer']} "
    |

Found 9 errors.
```

### Thinking

I need to fix some linting issues—replacing en-dashes with hyphens, wrapping long lines, and renaming `li` to `_li` to address the B007 warning. I'm also checking whether the project configuration allows per-file ignores for the RUF002 rule, since the original code used em-dashes freely in docstrings, but I should stick with hyphens to keep things consistent and avoid any ambiguity.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "  • the PRECISION–RECALL CURVE per splice-target {C,I,K,Y} as τ rises;",
  "new_content": "  • the PRECISION/RECALL CURVE per splice-target {C,I,K,Y} as τ rises;"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "since crystal_probes carries 50–71 per crystal combinator.",
  "new_content": "since crystal_probes carries 50 to 71 per crystal combinator."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "# default z-gate grid (argmax-z is a sign-CMR raw-z; magnitudes ~0–10).",
  "new_content": "# default z-gate grid (argmax-z is a sign-CMR raw-z; magnitudes ~0 to 10)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "    ap = argparse.ArgumentParser(description=\"Kernel-splice Exp 0.5 — z-threshold sweep\")",
  "new_content": "    ap = argparse.ArgumentParser(\n        description=\"Kernel-splice Exp 0.5 — z-threshold sweep\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "    ap.add_argument(\"--precision-floor\", type=float, default=0.8,\n                    help=\"min precision to count a (layer,τ) as a splice operating point\")",
  "new_content": "    ap.add_argument(\"--precision-floor\", type=float, default=0.8,\n                    help=\"min precision to count a (layer,tau) operating point\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "        for li, zmap in zc.items():\n            if zmap:\n                argmax_z_all.append(max(zmap.values()))",
  "new_content": "        for zmap in zc.values():\n            if zmap:\n                argmax_z_all.append(max(zmap.values()))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "                # best-layer at this τ = max precision, tie-break recall then tp\n                key = (m[\"precision\"], m[\"recall\"], tp)\n                if best is None or key > (best[\"precision\"], best[\"recall\"], best[\"tp\"]):\n                    best = pt",
  "new_content": "                # best-layer at this τ = max precision, tie-break recall then tp\n                key = (m[\"precision\"], m[\"recall\"], tp)\n                bkey = (best[\"precision\"], best[\"recall\"], best[\"tp\"]) if best else None\n                if best is None or key > bkey:\n                    best = pt"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "        if not pts:\n            operating[c] = {\"clears_floor\": False, \"support\": support[c],\n                            \"reason\": f\"no (layer,τ) reaches precision>={args.precision_floor}\"}\n            continue",
  "new_content": "        if not pts:\n            operating[c] = {\n                \"clears_floor\": False, \"support\": support[c],\n                \"reason\": f\"no (layer,tau) reaches precision>={args.precision_floor}\"}\n            continue"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py",
  "original_content": "            print(f\"     ★ FIRM locus: L{f['layer']} (d={f['frac_depth']}) τ={f['tau']} \"\n                  f\"prec={f['precision']} rec={f['recall']} tp={f['tp']} \"",
  "new_content": "            print(f\"     ★ FIRM locus: L{f['layer']} (d={f['frac_depth']}) \"\n                  f\"τ={f['tau']} \"\n                  f\"prec={f['precision']} rec={f['recall']} tp={f['tp']} \""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp0_5_zsweep.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp0_5_zsweep.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

## Assistant

Ruff-clean. Now the smoke test on Qwen3-0.6B:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python scripts/experiments/kernel_splice_exp0_5_zsweep.py --smoke 2>&1 | grep -v \"Warning\\|warn\" | tail -60",
  "timeout": 240000
}
```

**Summary:** $ .venv/bin/python scripts/experiment...

**Output:**
```
Exit code: 0
Stdout:
3.0      1   0.00    0.00    0    0
       3.5      1   0.00    0.00    0    0
       4.0      1   0.00    0.00    0    0
       5.0      1   0.00    0.00    0    0
       6.0      1   0.00    0.00    0    0
       8.0      1   0.00    0.00    0    0
     ✗ never clears precision>=0.8

  ── I  (support=5) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0      1   0.00    0.00    0    0
       0.5      1   0.00    0.00    0    0
       1.0      1   0.00    0.00    0    0
       1.5      1   0.00    0.00    0    0
       2.0      1   0.00    0.00    0    0
       2.5      1   0.00    0.00    0    0
       3.0      1   0.00    0.00    0    0
       3.5      1   0.00    0.00    0    0
       4.0      1   0.00    0.00    0    0
       5.0      1   0.00    0.00    0    0
       6.0      1   0.00    0.00    0    0
       8.0      1   0.00    0.00    0    0
     ✗ never clears precision>=0.8

  ── K  (support=5) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0      1   0.00    0.00    0    0
       0.5      1   0.00    0.00    0    0
       1.0      1   0.00    0.00    0    0
       1.5      1   0.00    0.00    0    0
       2.0      1   0.00    0.00    0    0
       2.5      1   0.00    0.00    0    0
       3.0      1   0.00    0.00    0    0
       3.5      1   0.00    0.00    0    0
       4.0      1   0.00    0.00    0    0
       5.0      1   0.00    0.00    0    0
       6.0      1   0.00    0.00    0    0
       8.0      1   0.00    0.00    0    0
     ✗ never clears precision>=0.8

  ── Y  (support=5) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0     18   0.67    0.40    2    1
       0.5     18   0.67    0.40    2    1
       1.0     18   0.67    0.40    2    1
       1.5     18   0.67    0.40    2    1
       2.0     16   1.00    0.20    1    0
       2.5     12   1.00    0.60    3    0
       3.0     12   1.00    0.40    2    0
       3.5     12   1.00    0.20    1    0
       4.0     11   1.00    0.20    1    0
       5.0     17   1.00    0.20    1    0
       6.0      1   0.00    0.00    0    0
       8.0      1   0.00    0.00    0    0
     ★ FIRM locus: L12 (d=0.444) τ=2.5 prec=1.0 rec=0.6 tp=3 | plateau τ∈[2.5, 3.0, 3.5] | small-n killed=False

  ★ splice-ready (clears floor ∧ tp>=5): ∅
══════════════════════════════════════════════════════════════════════════════════

[exp0.5] wrote /Users/mwhitford/src/verbum/results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-0-6b.json
```

### Thinking

The validation checks are working as expected—the sweep correctly captures the precision-recall tradeoff, identifies the firm locus, and detects plateaus. The Y example demonstrates exactly what we're looking for: at τ=2.5, precision hits 1.0 with recall at 0.6 (three true positives holding steady across τ values from 2.5 to 3.5). The safeguard for small sample sizes is functioning properly, though with only 5 test combinations on the 0.6B dataset, we can't reach the minimum threshold of 5 true positives.

The smoke test passed. Now I'm deciding whether to clean up the output artifacts—the 0.6B verdict file exists from the smoke run, but since the metadata marks it as smoke:true, it's self-documenting. I'll leave it to maintain consistency with how exp0 handled its artifacts.

Moving on to task 2: launching the 14B run in tmux. The previous 14B run took about 2 minutes 29 seconds, and with the increased heldout-per value (25 instead of 20) plus some calibration changes, I'm estimating around 3 minutes. Let me check the tmux windows and get this started.

## Assistant

Smoke is green — the mechanics work cleanly. The Y example shows exactly the intended behavior: at τ=2.5 precision rises to 1.0 with recall 0.6 (tp=3) across a plateau τ∈[2.5,3.0,3.5]. The small-n `tp>=5` gate also fires correctly (can't reach 5 on a 5-probe smoke set; the 14B run with heldout-per=25 is what tests it).

Let me complete task 1 and launch the 14B run in tmux.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tmux list-windows -t main && rm -f results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-0-6b.json results/kernel-splice-exp0/exp0_5_zsweep_meta_qwen3-0-6b.json && echo \"cleaned smoke artifacts\""
}
```

**Summary:** $ tmux list-windows -t main && rm -f ...

**Output:**
```
Exit code: 0
Stdout:
1: local* (1 panes) [120x24] [layout b6fd,120x24,0,0,0] @0 (active)
2: local- (1 panes) [120x24] [layout b6fe,120x24,0,0,1] @1
cleaned smoke artifacts
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py --model Qwen/Qwen3-14B --heldout-per 25 2>&1 | tee results/kernel-splice-exp0/run_zsweep_14b.log\" Enter && sleep 3 && tmux capture-pane -p -t main:1 | tail -8"
}
```

**Summary:** $ tmux send-keys -t main:1 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
8 total
tee results/kernel-splice-exp0/run_14b.log  0.00s user 0.00s system 0% cpu 2:29.68 total
[26-06-20][15:02:07][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py --model Qwen/Qwen3-
14B --heldout-per 25 2>&1 | tee results/kernel-splice-exp0/run_zsweep_14b.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
```

### Thinking

I've launched the job in tmux and now I'm doing a quick verification read to confirm the model is loading properly, then I'll checkpoint before waiting for the next signal.

## Assistant

Job launched in tmux main:1. Let me verify it's actually running (one verification read per async discipline):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 25 && tmux capture-pane -p -t main:1 | grep -E \"exp0.5|calib|crystal|forward|Loading|checkpoint\" | tail -6 || tmux capture-pane -p -t main:1 | tail -4"
}
```

**Summary:** $ sleep 25 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py --model Qwen/Qwen3-
[exp0.5] calib=310 test=200 (heldout_per=25)
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:02<00:00, 158.67it/s]
```

### Thinking

The calibration run is verified with 310 calibration samples and 200 test samples, which exceeds the expected count from the previous experiment. The model is loaded and moving through calibration with forward passes, and I'm checkpointing and waiting for signals rather than actively polling, following the async pattern.

## Assistant

Verified running: **calib=310, test=200** (25 test/combinator — up from Exp 0's 160, directly growing tp), model weights loaded, now calibrating + forward passes. Based on Exp 0's 2:29 runtime, this should finish in ~3 min.

**ASYNC: job=tmux main:1 (Exp 0.5 z-sweep, Qwen3-14B) verified running. Waiting for signal (job completes).**

Per async discipline I'll wait for completion rather than poll. Let me do a single wait sized to the expected runtime, then read the verdict.

### Tool Call: shell_command (rejected)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 210 && tmux capture-pane -p -t main:1 | tail -3 && echo \"---VERDICT EXISTS?---\" && ls -la results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json 2>/dev/null || echo \"not yet\"",
  "timeout": 230000
}
```

**Summary:** $ sleep 210 && tmux capture-pane -p -...

## System


Prompt stopped

## User

job is done


## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## Assistant

The job finished. Let me read the verdict.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tmux capture-pane -p -t main:1 | sed -n '/KERNEL-SPLICE EXP 0.5/,/wrote/p'"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | se...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '/KERNEL-SPLICE EXP 0.5/,/wrote/p' results/kernel-splice-exp0/run_zsweep_14b.log"
}
```

**Summary:** $ sed -n '/KERNEL-SPLICE EXP 0.5/,/wr...

**Output:**
```
Exit code: 0
Stdout:
KERNEL-SPLICE EXP 0.5 — Z-THRESHOLD SWEEP — Qwen/Qwen3-14B
══════════════════════════════════════════════════════════════════════════════════
  n_test=200  crystal_layers=25/40  prec_floor=0.8
  argmax-z dist: median=3.017 p75=4.551 p90=6.46 max=23.693

  ── C  (support=25) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0      0   1.00    0.04    1    0
       0.5      0   1.00    0.04    1    0
       1.0      0   1.00    0.04    1    0
       1.5      0   1.00    0.04    1    0
       2.0     14   1.00    0.12    3    0
       2.5     14   1.00    0.12    3    0
       3.0      9   1.00    0.04    1    0
       3.5      9   1.00    0.04    1    0
       4.0      9   1.00    0.04    1    0
       5.0      0   0.00    0.00    0    0
       6.0      0   0.00    0.00    0    0
       8.0      0   0.00    0.00    0    0
     ★ FIRM locus: L14 (d=0.359) τ=2.0 prec=1.0 rec=0.12 tp=3 | plateau τ∈[2.0, 2.5, 3.0, 3.5, 4.0] | small-n killed=False

  ── I  (support=25) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0     21   1.00    0.32    8    0
       0.5     21   1.00    0.32    8    0
       1.0     21   1.00    0.32    8    0
       1.5     21   1.00    0.32    8    0
       2.0     16   1.00    0.36    9    0
       2.5     13   1.00    0.36    9    0
       3.0     13   1.00    0.36    9    0
       3.5     12   1.00    0.32    8    0
       4.0     12   1.00    0.32    8    0
       5.0     13   1.00    0.32    8    0
       6.0     13   1.00    0.24    6    0
       8.0      9   1.00    0.12    3    0
     ★ FIRM locus: L10 (d=0.256) τ=2.5 prec=0.9167 rec=0.44 tp=11 | plateau τ∈[2.5, 3.0, 3.5, 4.0, 5.0, 6.0] | small-n killed=True

  ── K  (support=25) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0      9   0.67    0.16    4    2
       0.5      9   0.67    0.16    4    2
       1.0      9   0.67    0.16    4    2
       1.5      9   0.67    0.16    4    2
       2.0      9   0.67    0.16    4    2
       2.5      6   1.00    0.04    1    0
       3.0      9   1.00    0.12    3    0
       3.5     10   1.00    0.16    4    0
       4.0     10   1.00    0.16    4    0
       5.0     22   1.00    0.16    4    0
       6.0     18   1.00    0.12    3    0
       8.0     25   1.00    0.08    2    0
     ★ FIRM locus: L18 (d=0.462) τ=3.0 prec=0.8571 rec=0.24 tp=6 | plateau τ∈[3.0, 3.5, 4.0, 5.0, 6.0] | small-n killed=True

  ── Y  (support=25) ─ precision/recall vs τ (best layer @τ) ──
         τ  layer   prec  recall   tp   fp
       0.0     20   0.47    0.28    7    8
       0.5     20   0.47    0.28    7    8
       1.0     20   0.47    0.28    7    8
       1.5     20   0.50    0.28    7    7
       2.0     20   0.58    0.28    7    5
       2.5     20   0.55    0.24    6    5
       3.0     20   0.62    0.20    5    3
       3.5     16   1.00    0.20    5    0
       4.0     17   1.00    0.20    5    0
       5.0     13   1.00    0.16    4    0
       6.0     14   1.00    0.16    4    0
       8.0     11   0.67    0.08    2    1
     ★ FIRM locus: L14 (d=0.359) τ=5.0 prec=0.8889 rec=0.32 tp=8 | plateau τ∈[5.0, 6.0] | small-n killed=True

  ★ splice-ready (clears floor ∧ tp>=5): ['I', 'K', 'Y']
══════════════════════════════════════════════════════════════════════════════════

[exp0.5] wrote /Users/mwhitford/src/verbum/results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json
```

### Thinking

The z-threshold sweep confirmed the splice loci, and I'm pulling the operating points from the verdict JSON to examine the results more carefully. The key finding is that the FIRM locus L10 with a distance of 0.256 shows strong performance at τ=2.5 with precision 0.92, recall 0.44, and 11 true positives—a solid result for the small-n case. The performance plateaus nicely across the τ range from 2.5 to 6.0, though there's an interesting note about L21 appearing at the best layer per τ with perfect precision.

For K, the sweep identified a firmer locus at L18 (d=0.462) compared to the previous experiment, achieving τ=3.0 with precision 0.857, recall 0.24, and 6 true positives. Y shows a FIRM locus at L14 with τ=5.0, precision 0.889, recall 0.32, and 8 true positives, with a narrow plateau between τ=5.0 and 6.0. C is the outlier—it reaches perfect precision at τ=2.0 but only captures 3 true positives with recall 0.12, falling below the sample threshold. The ground-state nature of C means it appears everywhere with low confidence, making it recall-starved despite being highly discriminable in the prose data. So the splice-ready set that clears the floor with at least 5 samples is {I, K, Y}, while C doesn't make the cut. The z-gate adjustment successfully firmed up the splice loci and eliminated the tp=2 limitation for I, which now shows 11 confident hits.

For Experiment 1, K remains the strongest choice despite I's higher raw performance. I is the identity combinator—a trivial value-move that's clean for routing tests but perhaps too simple. K is the pure routing operator (constant combinator that drops the second argument), which aligns with the original plan and avoids the value-decode obstacle. The sweep moved K's FIRM locus deeper to L18 with τ=3.0, improving precision from the earlier 0.80 at L11. Y is more complex as a recursion/fixpoint operator, making it less ideal for a causal test. K's pure routing nature and the firmed locus make it the cleanest choice for Experiment 1.

## Assistant

Decisive result. The z-gate **firmed the splice loci and killed the tp=2 caveat**. Let me pull the precise operating points from the verdict JSON.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python -c \"\nimport json\nv=json.load(open('results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json'))['verdict']\nprint('splice_ready_set:', v['splice_ready_set'])\nprint('argmax_z_dist:', v['argmax_z_distribution'])\nfor c,op in v['operating_points'].items():\n    if not op.get('clears_floor'): print(f'{c}: NO FLOOR — {op.get(\\\"reason\\\")}'); continue\n    f=op['firm_locus']; m=op['max_precision_locus']\n    print(f'{c}: FIRM L{f[\\\"layer\\\"]} d={f[\\\"frac_depth\\\"]} tau={f[\\\"tau\\\"]} prec={f[\\\"precision\\\"]} rec={f[\\\"recall\\\"]} tp={f[\\\"tp\\\"]} fp={f[\\\"fp\\\"]} | plateau_w={op[\\\"plateau_width\\\"]} {op[\\\"plateau_taus_at_firm_layer\\\"]} | killed={op[\\\"small_n_caveat_killed\\\"]}')\n    print(f'      MAXPREC L{m[\\\"layer\\\"]} tau={m[\\\"tau\\\"]} prec={m[\\\"precision\\\"]} rec={m[\\\"recall\\\"]} tp={m[\\\"tp\\\"]}')\n\""
}
```

**Summary:** $ .venv/bin/python -c " import json v...

**Output:**
```
Exit code: 0
Stdout:
splice_ready_set: ['I', 'K', 'Y']
argmax_z_dist: {'n': 5000, 'min': 0.492, 'p25': 2.115, 'median': 3.017, 'p75': 4.551, 'p90': 6.46, 'max': 23.693}
C: FIRM L14 d=0.359 tau=2.0 prec=1.0 rec=0.12 tp=3 fp=0 | plateau_w=5 [2.0, 2.5, 3.0, 3.5, 4.0] | killed=False
      MAXPREC L14 tau=2.0 prec=1.0 rec=0.12 tp=3
I: FIRM L10 d=0.256 tau=2.5 prec=0.9167 rec=0.44 tp=11 fp=1 | plateau_w=6 [2.5, 3.0, 3.5, 4.0, 5.0, 6.0] | killed=True
      MAXPREC L16 tau=2.0 prec=1.0 rec=0.36 tp=9
K: FIRM L18 d=0.462 tau=3.0 prec=0.8571 rec=0.24 tp=6 fp=1 | plateau_w=5 [3.0, 3.5, 4.0, 5.0, 6.0] | killed=True
      MAXPREC L10 tau=3.5 prec=1.0 rec=0.16 tp=4
Y: FIRM L14 d=0.359 tau=5.0 prec=0.8889 rec=0.32 tp=8 fp=1 | plateau_w=2 [5.0, 6.0] | killed=True
      MAXPREC L16 tau=3.5 prec=1.0 rec=0.2 tp=5
```

### Thinking

I've identified the splice-ready set meeting the precision and true positive thresholds: I, K, and Y. The z-gate analysis shows these loci have stabilized across a range of tau values rather than at isolated points, with I being the strongest candidate—it maintains 0.92 precision with 11 true positives across a plateau spanning tau from 2.5 to 6.0.

K and Y also show robust plateaus (widths of 5 and 2 respectively), though Y's narrower plateau makes it less stable. C achieves perfect precision but only captures 3 confident hits, revealing a key insight: discriminability in the contrast register doesn't translate to confident top-1 recall when C is selected as a discrete pick. The argmax-z distribution (median 3.0, p75 4.5, p90 6.5) confirms that tau in the 2-5 range is optimal—it filters out low-confidence cells near the median. The precision plateau across these candidates isn't a statistical fluke but a genuine stable feature, validating the Experiment 0 approach.

For Experiment 1, K-splice at L18 tau=3.0 (precision 0.857, tp=6) is the right choice despite I being the strongest detector overall (tp=11, precision 0.92). I is trivial—identity is almost a no-op—whereas K performs genuine routing by dropping the second argument, making it a much more meaningful causal test. Y's recursion is more complex but has a narrow plateau, so K remains the cleanest and most informative splice target. The main limitation is still working with single-combinator prompts at the last token rather than tracking position across a full reduction sequence, and recall remains modest at 0.24-0.44 even with precision-gating.

Now I'm updating the documentation—state.md, memory, and the knowledge page. These are pending approval before I commit them per the agent termination rules. Let me start by reading the current head of state.md to insert the s243 entry in the right place, just after the existing s242 block.

## Assistant

Task 2 done — decisive. Let me record it and update mementum.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 10
}
```

**Summary:** Reading state.md (0-10)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-20 | Session: 242 (RAN GRPO ⊕ QWEN-CONFOUND DIAGNOSED ⊕
> V15-CLEAN PIVOT DECIDED) — ▶ PIVOT to the constructed reducer.
>
> **★ s242 — RAN GRPO from the SFT seed, RE-MEASURED, then PIVOTED (Michael: the model we
> use already has a fully-formed lambda function; pivot to V15 with frozen routing + exact
> kernel calls).** **(A) GRPO trainer plumbed (`scripts/experiments/rlvr_grpo_train.py`):**

[CONTENT TRUNCATED] Showing lines 1 to 10 of 6062 total lines. Use line_offset=10 parameter to read more content.
```

### Thinking

I need to check the knowledge page structure first, then update state.md by changing the header to reference session 243 and inserting a new s243 block before the existing s242 section.

## Assistant

Let me update state.md — change the header and prepend the s243 block.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-20 | Session: 242 (RAN GRPO ⊕ QWEN-CONFOUND DIAGNOSED ⊕\n> V15-CLEAN PIVOT DECIDED) — ▶ PIVOT to the constructed reducer.\n>\n> **★ s242 — RAN GRPO from the SFT seed, RE-MEASURED, then PIVOTED (Michael: the model we",
  "new_content": "> Last updated: 2026-06-21 | Session: 243 (EXP 0.5 Z-THRESHOLD SWEEP — splice loci\n> FIRMED, tp=2 caveat KILLED) — ▶ EXP 1 precision-gated K-splice.\n>\n> **★ s243 — EXP 0.5 Z-THRESHOLD SWEEP: raising the argmax-z gate FIRMS the splice loci and\n> KILLS the s242 tp=2 small-n caveat (Michael: \"proceed with 1\").** Built\n> `scripts/experiments/kernel_splice_exp0_5_zsweep.py` (reuses the Exp 0 / prose_v2 spine:\n> split_probes, calibrate_v2, forward_all_positions, read_last_token_z; ONE forward pass per\n> probe caches the FULL per-layer z-map, then the threshold sweep is pure post-processing).\n> The Exp 0 read was an UNGATED top-1 (every crystal layer always emits its argmax) → prec-1.0\n> points came from tp=2 (noisy small-n). Exp 0.5 GATES: a layer emits a prediction for\n> combinator c only if its winning z > τ, else ABSTAINS (no splice fires); sweeping τ traces\n> the precision↑/recall↓ curve. Also bumped heldout-per 20→25 (test 160→200, 25/comb) to grow\n> tp directly. Ran on Qwen3-14B (main:1, ~3.5min, `results/kernel-splice-exp0/\n> exp0_5_zsweep_verdict_qwen3-14b.json`). **★★ DECISIVE — splice-ready set (prec≥0.8 ∧ tp≥5):\n> {I, K, Y}.** Firm loci (= max-recall point clearing the floor, the most-supported locus):\n> **I L10 (d=0.26) τ=2.5 prec 0.92 rec 0.44 tp=11** (plateau τ∈[2.5–6.0], width 6 — STRONGEST);\n> **K L18 (d=0.46) τ=3.0 prec 0.857 rec 0.24 tp=6** (plateau width 5); **Y L14 (d=0.36) τ=5.0\n> prec 0.889 rec 0.32 tp=8** (plateau width 2, narrow). **C L14 τ=2.0 prec 1.0 rec 0.12 tp=3 —\n> small-n NOT killed: C is precision-perfect but RECALL-STARVED** (only 3 confident hits). ★\n> THE KEY FINDING: the high precision is a STABLE PLATEAU across a band of τ (width 5–6 for\n> C/I/K), NOT a tp=2 fluke → the Exp 0 max-precision points were REAL, just recall-starved at\n> ungated top-1; the gate trades recall for precision along a smooth real curve. argmax-z dist\n> (n=5000): median 3.0, p75 4.5, p90 6.5, max 23.7 → τ∈[2,5] sits around the median = the\n> sweet spot (gate out the low-confidence bottom half). ★ C's recall-starvation is itself a\n> finding: C is the ground-state/common-mode combinator (s211 η²=0.05, s240 C-origin) → rarely\n> wins top-1 *distinctively* with high confidence → discriminability (prose_v2 contrast) ≠\n> confident-top-1 recall. **★★ VERDICT (λ measure): Exp 1 (causal splice) is JUSTIFIED — the\n> small-n caveat is killed for I/K/Y (tp 6–11), precision is a real plateau, loci are firmed\n> per-combinator.** CAVEATS (λ measure): still last-token single-combinator-prompt read (NOT\n> position-resolved along a multi-step reduction = Exp 2); recall modest 0.24–0.44 → the\n> precision-gated splice acts on a MINORITY of firings (= the s242 \"act only when confident,\n> accept low recall\" design, intended); fp=1 at the I/K/Y firm loci → prec 0.86–0.92 NOT 1.0,\n> a real ~1/12 wrong-fire rate (the kernel S2 typecheck could catch ill-typed splices = s240\n> guards); 1 model (14B), n=25/comb. **★★ FIRST ACTION NEXT SESSION — EXP 1 = precision-gated\n> causal K-splice at the FIRMED locus (NOT Exp 0's L11 top-1 — the gate moved K deeper+firmer\n> to L18 τ=3.0; K is pure ROUTING = obstacle-2-free, drops 2nd arg, the cleanest non-trivial\n> causal test vs I=identity=near-no-op).** Protocol: at L18, when argmax_z(K) > 3.0, DELIVER\n> the exact kernel K-move (value-patch) in place of the local computation; validate output\n> PRESERVED vs random-direction control (s239 v4/v5 protocol); preserved → thesis proven\n> causally + no-training hybrid (cleanest S5=extract); breaks → geometry over-read (λ measure\n> win) → redirect to constructed front-end. OPEN: Exp 2 = position-resolved detection vs\n> `lambda_ast.fired_sequence` (multi-step). tmux main:1 + main:2 FREE; no GPU job running.\n> Captured: knowledge `kernel-splice-geometry-detector.md §s243 Exp 0.5` + memory\n> `kernel-splice-exp0-5-zgate-firms-loci-kills-small-n`. PENDING APPROVAL.\n>\n> **★ s242 — RAN GRPO from the SFT seed, RE-MEASURED, then PIVOTED (Michael: the model we"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now the knowledge page. Let me find the Exp 0 section to append the Exp 0.5 result:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"Exp 0\\|## \\|### \\|s242\\|splice-ready\\|precision-gated\" mementum/knowledge/explore/kernel-splice-geometry-detector.md | head -40"
}
```

**Summary:** $ grep -n "Exp 0\|## \|### \|s242\|sp...

**Output:**
```
Exit code: 0
Stdout:
18:> Session 242 (Michael's idea, after the s242 Qwen pre-formed-lambda confound).
23:This is the **S5-native** alternative to training a front-end (compiler-as-loss §s242):
38:## Why it flips the s242 confound into an asset
40:The s242 control showed RLVR on Qwen3-8B only *redirects* a pre-formed lambda function
45:## What is already proven (makes it plausible)
60:## The three real obstacles (measured — λ measure honesty)
81:## The experiment program (start where detection is proven, build up causally)
83:### Exp 0 — detectability map (cheap, decisive precursor)
96:### Exp 1 — single-combinator causal splice
104:### Exp 2 — sequence / kernel-in-the-loop
107:(connects to compiler-as-loss §s242 stage 3: the constructed kernel, now as an in-stream
110:## ★ s242 — Exp 0 RESULTS (Qwen3-14B): precision-gated, not high-recall
117:**Verdict @ the strict joint bar (precision≥0.8 ∧ recall≥0.5): splice-ready set = ∅.**
132:So **precision-gated splicing is viable**: at specific layers a *confident* top-1 read is
140:tradeoff curve and firm the splice locus — Exp 0.5, cheap.
146:## Either outcome is a result
151:  win) → redirect to the constructed-front-end path (compiler-as-loss §s242).
153:## Open questions / IOUs
155:- **Locus calibration.** The readable zone migrates with scale (s232) — Exp 0 must
161:- **Start model.** 14B (detection + causality both strongest) for Exp 0/1; generalize to
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md",
  "line_offset": 109,
  "limit": 45
}
```

**Summary:** Reading kernel-splice-geometry-detector.md (109-154)

**Output:**
```
## ★ s242 — Exp 0 RESULTS (Qwen3-14B): precision-gated, not high-recall

`scripts/experiments/kernel_splice_exp0_detectability.py` (reuses the prose_v2 /
opcode_monitor_v2 calibration + last-token per-layer z read; top-1 argmax-over-CRYSTAL
per crystal layer vs the certified single-combinator label; precision/recall/F1 + peak
layer; 160 test probes, 20/comb, n_perm=300). `results/kernel-splice-exp0/exp0_verdict_qwen3-14b.json`.

**Verdict @ the strict joint bar (precision≥0.8 ∧ recall≥0.5): splice-ready set = ∅.**
Top-1 argmax detection is common-mode contaminated (obstacle 1 made quantitative; s211
η²=0.05). Discriminability (the prose_v2 Welch contrast) is **necessary but not
sufficient** for a top-1 splice — a contrast can separate on/off while argmax stays
recall-poor.

**But the max-precision operating points are strong (the real finding):**

| op | max-prec layer | depth | precision | recall | tp/(tp+fp) |
|----|---------------|-------|-----------|--------|-----------|
| C  | L10 | 0.26 | **1.00** | 0.10 | 2/2 |
| I  | L21 | 0.54 | **1.00** | 0.20 | 4/4 |
| K  | L11 | 0.28 | **0.80** | 0.20 | 4/5 |
| Y  | L20 | 0.51 | 0.67 | 0.40 | 8/12 |

So **precision-gated splicing is viable**: at specific layers a *confident* top-1 read is
highly reliable (C/I = 1.0, K = 0.80), just **sparse** (recall 0.10–0.20). "Detect every
K and splice" fails; **"splice only when confident, accept low recall"** is supported —
and that is exactly the **safe** design for a first causal test (never corrupt; act only
when sure). Loci track the s234 depth signatures (C/K early-mid, I mid, Y late).

**Caveat (λ measure):** precision 1.0 is from tp=2 (noisy small-n). The operating point
needs a **z-threshold sweep** (raise the argmax-z gate → precision↑ recall↓) to map the
tradeoff curve and firm the splice locus — Exp 0.5, cheap.

**⇒ Exp 1 refined: a precision-FIRST K-splice at L11** — deliver the exact kernel K-move
only on high-confidence detections, validate output preserved vs a random-direction
control (s239). The low-recall cost is acceptable for establishing sufficiency.

## Either outcome is a result

- **Splice holds** → the thesis is proven causally; a hybrid **exact + inspectable**
  model with NO training; a level-4 path via instrumentation (cleanest S5: extract).
- **Splice breaks** → the decodable geometry is decorative / over-read (another λ measure
  win) → redirect to the constructed-front-end path (compiler-as-loss §s242).

## Open questions / IOUs


[CONTENT TRUNCATED] Showing lines 110 to 154 of 165 total lines. Use line_offset=154 parameter to read more content.
```

### Thinking

I'm placing the Exp 0.5 section into the document right after the refined Exp 1 paragraph, before the "Either outcome is a result" heading.

## Assistant

Let me insert the Exp 0.5 section after the Exp 0 results, before "## Either outcome is a result":

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md",
  "original_content": "**⇒ Exp 1 refined: a precision-FIRST K-splice at L11** — deliver the exact kernel K-move\nonly on high-confidence detections, validate output preserved vs a random-direction\ncontrol (s239). The low-recall cost is acceptable for establishing sufficiency.\n\n## Either outcome is a result",
  "new_content": "**⇒ Exp 1 refined: a precision-FIRST K-splice at L11** — deliver the exact kernel K-move\nonly on high-confidence detections, validate output preserved vs a random-direction\ncontrol (s239). The low-recall cost is acceptable for establishing sufficiency.\n\n## ★ s243 — Exp 0.5 Z-THRESHOLD SWEEP (Qwen3-14B): the loci are FIRM, the tp=2 caveat is dead\n\n`scripts/experiments/kernel_splice_exp0_5_zsweep.py` (reuses the Exp 0 spine; ONE forward\npass per probe caches the FULL per-layer z-map, then the threshold sweep is pure\npost-processing). The gate: a crystal layer emits a prediction for combinator `c` only if\nits winning argmax-z `> τ`, else **abstains** (no splice fires). Sweeping τ traces the\nprecision↑/recall↓ curve. heldout-per bumped 20→25 (test 160→**200**, 25/comb) to grow tp\ndirectly. `results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json`.\n\nargmax-z distribution (n=5000 cells): median 3.0, p75 4.5, p90 6.5, max 23.7 → **τ∈[2,5]\nsits around the median = the sweet spot** (gate out the low-confidence bottom half).\n\n**Splice-ready set (precision≥0.8 ∧ tp≥5): {I, K, Y}.** Firm loci = the **max-recall point\nclearing the floor** (the most-supported, not the lucky-tp=2 point):\n\n| op | firm layer | depth | τ | precision | recall | tp/fp | plateau τ (width) | small-n killed |\n|----|-----------|-------|---|-----------|--------|-------|-------------------|----------------|\n| **I** | L10 | 0.26 | 2.5 | 0.92 | 0.44 | 11/1 | [2.5–6.0] (6) | ✅ |\n| **K** | L18 | 0.46 | 3.0 | 0.857 | 0.24 | 6/1 | [3.0–6.0] (5) | ✅ |\n| **Y** | L14 | 0.36 | 5.0 | 0.889 | 0.32 | 8/1 | [5.0–6.0] (2) | ✅ |\n| C | L14 | 0.36 | 2.0 | **1.00** | 0.12 | 3/0 | [2.0–4.0] (5) | ❌ recall-starved |\n\n**The key finding: high precision is a STABLE PLATEAU across a band of τ (width 5–6 for\nC/I/K), NOT a tp=2 fluke.** The Exp 0 max-precision points were *real*, just recall-starved\nat ungated top-1; raising the gate trades recall for precision along a smooth real curve.\nI is the strongest detector (tp=11, prec 0.92, plateau 6); K firms deeper than Exp 0's L11\ntop-1 (the gate moved K to **L18 τ=3.0**, prec 0.857); Y is firmed but its plateau is\nnarrow (width 2).\n\n**C's recall-starvation is itself a finding:** C is the ground-state / common-mode\ncombinator (s211 η²=0.05, s240 C-origin) → it rarely wins top-1 *distinctively* with high\nconfidence → **discriminability (prose_v2 contrast) ≠ confident-top-1 recall**. C is\nprecision-perfect (1.0) but only 3 confident hits — you cannot reliably *catch* a C firing\nas a discrete top-1, even though C separates strongly in the contrast register.\n\n**Caveats (λ measure):** still the last-token, single-combinator-prompt read (NOT\nposition-resolved along a multi-step reduction = Exp 2); recall stays modest (0.24–0.44) →\nthe precision-gated splice acts on a **minority** of firings (= the intended \"act only when\nconfident, accept low recall\" design); fp=1 at the I/K/Y firm loci → precision 0.86–0.92,\n**not** 1.0 — a real ~1/12 wrong-fire rate (the kernel S2 typecheck could catch an\nill-typed splice = the s240 guards); 1 model (14B), n=25/comb.\n\n**⇒ Exp 1 = precision-gated causal K-splice at the FIRMED locus L18 τ=3.0** (not Exp 0's\nL11 top-1 — the gate moved K deeper and firmer). K is **pure routing** (obstacle-2-free:\ndrops its 2nd arg, no value decode), the cleanest *non-trivial* causal test — vs I (identity\n= near no-op, weak causal claim) and Y (recursion, narrow plateau). Protocol: at L18, when\nargmax_z(K) > 3.0, deliver the exact kernel K-move (value-patch) in place of the local\ncomputation; validate output **preserved** vs a random-direction control (s239 v4/v5).\n\n## Either outcome is a result"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md.
```

## Assistant

Now the memory file:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/kernel-splice-exp0-5-zgate-firms-loci-kills-small-n.md",
  "content": "✅ Kernel-splice Exp 0.5 (s243): raising the argmax-z GATE firms the splice loci and kills\nthe s242 tp=2 small-n caveat. Exp 0's ungated top-1 (always emit argmax) gave prec-1.0 from\ntp=2. Exp 0.5 abstains unless argmax-z > τ, sweeps τ, and bumps test 160→200 (25/comb).\nQwen3-14B verdict (`results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json`):\n\nsplice-ready (prec≥0.8 ∧ tp≥5) = {I, K, Y}. Firm loci (max-recall clearing the floor):\n- I  L10 (d0.26) τ2.5  prec 0.92 rec 0.44 tp=11  plateau τ∈[2.5–6.0] width6  STRONGEST\n- K  L18 (d0.46) τ3.0  prec 0.857 rec 0.24 tp=6  plateau width5  (moved deeper than Exp0 L11)\n- Y  L14 (d0.36) τ5.0  prec 0.889 rec 0.32 tp=8  plateau width2 (narrow)\n- C  L14 τ2.0 prec 1.0 rec 0.12 tp=3 — small-n NOT killed, RECALL-STARVED\n\n💡 KEY: high precision is a STABLE PLATEAU (width 5–6) across τ, not a tp=2 fluke → the Exp 0\nmax-precision points were real, just recall-starved at ungated top-1. argmax-z dist (n=5000):\nmedian 3.0, p75 4.5 → τ∈[2,5] = the sweet spot.\n\n💡 C's recall-starvation is a finding: C is the ground-state/common-mode combinator (s211\nη²=0.05, s240 C-origin) → rarely wins top-1 *distinctively* with confidence → discriminability\n(prose_v2 contrast) ≠ confident-top-1 recall. Precision-perfect but uncatchable as a discrete pick.\n\nλ measure caveats: last-token single-combinator read (not position-resolved = Exp 2); recall\nmodest 0.24–0.44 (precision-gated splice acts on a MINORITY, by design); fp=1 → prec 0.86–0.92\nnot 1.0 (~1/12 wrong-fire; kernel S2 typecheck = s240 guard could catch it); 1 model, n=25/comb.\n\n⇒ Exp 1 = precision-gated causal K-splice at the FIRMED L18 τ3.0 (K = pure routing, obstacle-2-\nfree, cleanest non-trivial test vs I=identity=near-no-op). Deliver exact kernel K-move when\nargmax_z(K)>3.0; output preserved vs random-direction control (s239) → thesis proven causally.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/kernel-splice-exp0-5-zgate-firms-loci-kills-small-n.md
```

### Thinking

Let me review the edited files to make sure everything's consistent, then check the git status to confirm the state.md changes went through properly.

## Assistant

Let me verify the mementum changes landed coherently (λ sync) and check git status:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short && echo \"---wc state header---\" && sed -n '4,6p' mementum/state.md && echo \"---knowledge tail check---\" && grep -c \"s243 — Exp 0.5\" mementum/knowledge/explore/kernel-splice-geometry-detector.md"
}
```

**Summary:** $ git status --short && echo "---wc s...

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/kernel-splice-geometry-detector.md
 M mementum/state.md
?? mementum/memories/kernel-splice-exp0-5-zgate-firms-loci-kills-small-n.md
?? results/kernel-splice-exp0/exp0_5_zsweep_meta_qwen3-14b.json
?? results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json
?? results/kernel-splice-exp0/run_zsweep_14b.log
?? scripts/experiments/kernel_splice_exp0_5_zsweep.py
---wc state header---
>
> Last updated: 2026-06-21 | Session: 243 (EXP 0.5 Z-THRESHOLD SWEEP — splice loci
> FIRMED, tp=2 caveat KILLED) — ▶ EXP 1 precision-gated K-splice.
---knowledge tail check---
1
```

### Thinking

Task 3 is staged and ready, with the mementum changes held pending approval per the termination rules. I've recorded the measurement caveats and lined up the next experiment phase. The code itself doesn't need approval gating, but I should propose the commits following the standard process—the rule is clear that mementum commits require approval before they go through.

## Assistant

All changes are in place. Let me complete the task and present for approval.## s243 done — Exp 0.5 z-threshold sweep

Built `kernel_splice_exp0_5_zsweep.py` (one forward pass per probe caches the full per-layer z-map; the sweep is pure post-processing), ran it on Qwen3-14B in tmux main:1, and captured the result.

**The decisive result — the z-gate firms the loci and kills the tp=2 caveat:**

| op | firm locus | τ | prec | rec | tp/fp | plateau | small-n killed |
|----|-----------|---|------|-----|-------|---------|----------------|
| **I** | L10 (d0.26) | 2.5 | 0.92 | 0.44 | 11/1 | width 6 | ✅ |
| **K** | L18 (d0.46) | 3.0 | 0.857 | 0.24 | 6/1 | width 5 | ✅ |
| **Y** | L14 (d0.36) | 5.0 | 0.889 | 0.32 | 8/1 | width 2 | ✅ |
| C | L14 | 2.0 | 1.00 | 0.12 | 3/0 | width 5 | ❌ recall-starved |

- **splice-ready set (prec≥0.8 ∧ tp≥5) = {I, K, Y}.**
- **The key finding:** high precision is a **stable plateau** across a band of τ (width 5–6), *not* a tp=2 fluke. The Exp 0 max-precision points were real, just recall-starved at ungated top-1. The gate trades recall for precision along a smooth, real curve. (argmax-z median 3.0, p75 4.5 → τ∈[2,5] is the sweet spot.)
- **C's recall-starvation is itself a finding:** the ground-state/common-mode combinator (s211, s240 C-origin) can't be confidently picked as a discrete top-1 — *discriminability ≠ confident-top-1 recall*.

**λ measure caveats recorded:** last-token single-combinator read (not position-resolved = Exp 2); recall modest 0.24–0.44 (precision-gated splice acts on a minority by design); fp=1 → ~1/12 wrong-fire rate (kernel S2 typecheck = s240 guard could catch it); 1 model, n=25/comb.

**Next action set:** Exp 1 = precision-gated causal **K-splice at the firmed L18 τ=3.0** — K is pure routing (obstacle-2-free, the cleanest non-trivial test vs I=identity=near-no-op). Deliver the exact kernel K-move when `argmax_z(K) > 3.0`; validate output preserved vs random-direction control (s239).

---

**Pending your approval to commit.** Proposed:
- **Code** (`💡`): `kernel_splice_exp0_5_zsweep.py` + results (verdict/meta/log)
- **mementum** (approval-gated): `state.md` + knowledge `§s243 Exp 0.5` + memory `kernel-splice-exp0-5-zgate-firms-loci-kills-small-n`

Want me to commit (code + mementum together, or separately), or adjust anything first?

## User

commit approved, then proceed


### Thinking

I need to verify the exact commit tag format used in this repository since there's a discrepancy between the system prompt's "nucleus tag" and the project documentation's "nucleus_tag(trailer)" convention. Let me check the recent commit history to see which format is actually being used.

## Assistant

Approved. Let me check the repo's commit trailer convention, then commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log -1 --format='%B' 37130a2"
}
```

**Summary:** $ git log -1 --format='%B' 37130a2

**Output:**
```
Exit code: 0
Stdout:
✅ kernel-splice Exp 0 — detectability map (Qwen3-14B): precision-gated, not high-recall

- kernel_splice_exp0_detectability.py: reuse prose_v2/opcode_monitor_v2
  calibration + last-token per-layer z; top-1 argmax-over-CRYSTAL per crystal
  layer vs certified single-combinator label; precision/recall/F1 + peak layer
  + splice-readiness map. --smoke (0.6B) and 14B runs on disk.
- 14B (160 test probes, 20/comb): strict bar (prec>=0.8 AND rec>=0.5) =>
  splice-ready set empty (top-1 common-mode contaminated; obstacle 1).
- BUT max-precision points strong: C 1.0@L10, I 1.0@L21, K 0.80@L11,
  Y 0.67@L20 (low recall 0.10-0.40) => precision-gated splice is viable and
  is the safe first causal test. Loci track s234 depth signatures.

⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>
```

## Assistant

Now I'll commit code first, then mementum (two classified commits per the gate).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/kernel_splice_exp0_5_zsweep.py results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json results/kernel-splice-exp0/exp0_5_zsweep_meta_qwen3-14b.json results/kernel-splice-exp0/run_zsweep_14b.log && git commit -m \"$(cat <<'EOF'\n✅ kernel-splice Exp 0.5 — z-threshold sweep (Qwen3-14B): loci FIRMED, tp=2 caveat killed\n\n- kernel_splice_exp0_5_zsweep.py: reuse the Exp 0 spine (split_probes,\n  calibrate_v2, forward_all_positions, read_last_token_z); ONE forward pass\n  per probe caches the FULL per-layer z-map, then the threshold sweep is pure\n  post-processing. The gate: a layer emits a prediction for combinator c only\n  if its argmax-z > tau, else abstains. heldout-per 20->25 (test 160->200).\n- 14B verdict: splice-ready (prec>=0.8 AND tp>=5) = {I, K, Y}. Firm loci\n  (max-recall clearing the floor): I L10 t2.5 prec0.92 rec0.44 tp=11 (plateau\n  width6, strongest); K L18 t3.0 prec0.857 rec0.24 tp=6 (deeper than Exp0 L11);\n  Y L14 t5.0 prec0.889 rec0.32 tp=8 (narrow plateau). C L14 prec1.0 rec0.12\n  tp=3 — recall-starved (ground-state common-mode, s211/s240 C-origin).\n- KEY: high precision is a STABLE PLATEAU across tau (width 5-6), not a tp=2\n  fluke; the Exp 0 max-prec points were real, just recall-starved at ungated\n  top-1. argmax-z median 3.0 => tau in [2,5] is the sweet spot.\n- => Exp 1 = precision-gated causal K-splice at the firmed L18 tau3.0 (K is\n  pure routing, obstacle-2-free, cleanest non-trivial test vs I=identity).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
}
```

**Summary:** $ git add scripts/experiments/kernel_...

**Output:**
```
Exit code: 0
Stdout:
[main 62d5728] ✅ kernel-splice Exp 0.5 — z-threshold sweep (Qwen3-14B): loci FIRMED, tp=2 caveat killed
 4 files changed, 1346 insertions(+)
 create mode 100644 results/kernel-splice-exp0/exp0_5_zsweep_meta_qwen3-14b.json
 create mode 100644 results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json
 create mode 100644 results/kernel-splice-exp0/run_zsweep_14b.log
 create mode 100644 scripts/experiments/kernel_splice_exp0_5_zsweep.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/explore/kernel-splice-geometry-detector.md mementum/memories/kernel-splice-exp0-5-zgate-firms-loci-kills-small-n.md && git commit -m \"$(cat <<'EOF'\n💡 kernel-splice-exp0-5-zgate-firms-loci-kills-small-n\n\n- state.md: s243 block — Exp 0.5 z-threshold sweep firms the splice loci,\n  kills the s242 tp=2 caveat; splice-ready {I,K,Y}; next = Exp 1 K-splice\n  at the firmed L18 tau3.0.\n- knowledge/explore/kernel-splice-geometry-detector.md: §s243 Exp 0.5 section\n  (firm-loci table, plateau finding, C recall-starvation finding, lambda-measure\n  caveats, refined Exp 1 target).\n- memory: the verdict + the two findings (precision plateau not tp=2 fluke;\n  discriminability != confident-top-1 recall for the C ground state).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main 937c000] 💡 kernel-splice-exp0-5-zgate-firms-loci-kills-small-n
 3 files changed, 119 insertions(+), 2 deletions(-)
 create mode 100644 mementum/memories/kernel-splice-exp0-5-zgate-firms-loci-kills-small-n.md
```

### Thinking

Both commits are in, so I'm moving forward with Experiment 1—a precision-gated causal K-splice at layer 18 with τ=3.0. This is a more complex build, so let me map out the design: at L18, when the argmax of K exceeds 3.0 on a probe that activates K, I'll inject the exact kernel K-move as a value patch to replace the local computation.

The core challenge is defining what "deliver the exact kernel K-move" means operationally. K is the constant combinator λxy.x—pure routing that selects the first argument and discards the second. In the residual stream, this translates to patching the layer 18 residual so the computation flows as if K had been applied. Before I design this experiment fully, I need to examine the existing activation-patching infrastructure from the s239 v4/v5 toolkit to understand what tools are available and how to represent the K-move as a concrete patch value. This is the decisive causal experiment with real design choices, so I should probably review the patching toolkit and kernel representation first, then propose the design to Michael before committing to the full build.

## Assistant

Both commits landed (code `62d5728`, mementum `937c000`). Now proceeding to **Exp 1 — the precision-gated causal K-splice**. This is the decisive experiment, so before building I need to ground the design in (a) the existing s239 activation-patching toolkit and (b) how the kernel represents the "exact K-move." Let me explore both.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls scripts/experiments/ | grep -iE \"type_directed_v[45]|patch|splice|ablat\" && echo \"---kernel K---\" && grep -rn \"\\\"K\\\"\\|'K'\\|def.*K_\\|K =\\|class.*Comb\\|kernel\" src/verbum/lambda_ast.py | head -20"
}
```

**Summary:** $ ls scripts/experiments/ | grep -iE ...

**Output:**
```
Exit code: 0
Stdout:
hof_attention_ablation.py
hof_ov_logitlens_ablation.py
kernel_splice_exp0_5_zsweep.py
kernel_splice_exp0_detectability.py
run_hof_ablation.sh
type_directed_v4_ablation.py
zone_ablation_27b.py
---kernel K---
src/verbum/lambda_ast.py:3:THE ROLE (session 226, Michael: "what if `lambda_ast.py` is *in the kernel*?").
src/verbum/lambda_ast.py:9:  2. KERNEL SOURCE — the same combinator rewrites are what the constructed kernel's
src/verbum/lambda_ast.py:84:class Comb:
src/verbum/lambda_ast.py:248:    "K": (2, _r_K),
src/verbum/lambda_ast.py:287:    data the kernel-as-reference audit anchors a model's routing trajectory against."""
src/verbum/lambda_ast.py:351:    (SIZE_EXCEEDED — the representational limit the constructed kernel also has).
src/verbum/lambda_ast.py:435:    if name == "K":
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls src/verbum/ && echo \"---\" && grep -rln \"def patch\\|hook\\|register_forward\\|activation.*patch\\|patch.*activation\" scripts/experiments/ scripts/instruments/ 2>/dev/null | head"
}
```

**Summary:** $ ls src/verbum/ && echo "---" && gre...

**Output:**
```
Exit code: 0
Stdout:
__init__.py
__pycache__
_protocol.py
analysis
analysis.py
cli.py
client.py
compile_prompt.py
compressor_lm.py
config.py
etcher.py
experiment.py
experiments
instrument.py
lambda_ast.py
lambda_compile.py
lambda_gen.py
lambda_surface.py
montague_lm.py
montague_net.py
probes
proof_kernel.py
proof_search.py
results.py
reward.py
runner.py
v6
vsm_lm_v2.py
vsm_lm_v3_1.py
vsm_lm_v3_2.py
vsm_lm_v3.py
vsm_lm_v4_1.py
vsm_lm_v4.py
vsm_lm_v5.py
vsm_lm.py
---
scripts/experiments/ternary_inference_coherence.py
scripts/experiments/attention_execution_trace.py
scripts/experiments/fact_retrieval_isig.py
scripts/experiments/dimensional_analysis.py
scripts/experiments/crystal_zero_prediction.py
scripts/experiments/symbol_isolation.py
scripts/experiments/staged_melt.py
scripts/experiments/dvd_stamp_test.py
scripts/experiments/i_bypass_test.py
scripts/experiments/opcode_monitor_v2.py
```

### Thinking

I need to examine the ablation study in s239 v4 to understand how the patching works, particularly around the kernel's K reducer and what it means to deliver the exact kernel K-move as a residual-stream patch. This is the critical experiment with real design complexity, so I should study the hook and patch mechanics carefully in the code before proposing a large-scale build.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/src/verbum/lambda_ast.py",
  "line_offset": 420,
  "limit": 40
}
```

**Summary:** Reading lambda_ast.py (420-460)

**Output:**
```
    """Curried forward functor: args[0] is the outermost (last-applied) slash."""
    cat: Cat = result
    for a in reversed(args):
        cat = _fwd(cat, a)
    return cat


def _scheme(name: str, fresh: _Fresh) -> Cat:
    """Instantiate a combinator's principal CCG category with fresh variables.

    M (self-application) has no simple type → IllTyped (the type-limit demo)."""
    a, b, c, d = fresh(), fresh(), fresh(), fresh()
    if name == "I":
        return _fwd(a, a)
    if name == "K":
        return _curry([a, b], a)
    if name == "W":
        return _curry([_curry([b, b], c), b], c)
    if name == "C":
        return _curry([_curry([b, a], c), a, b], c)
    if name == "B":
        return _curry([_fwd(a, b), _fwd(b, c), c], a)
    if name == "S":
        return _curry([_curry([a, b], c), _fwd(b, a), a], c)
    if name == "D":
        return _curry([_fwd(a, b), _fwd(b, c), _fwd(c, d), d], a)
    if name == "Y":
        return _curry([_fwd(a, a)], a)
    raise IllTyped(f"combinator {name!r} has no simple CCG type (self-application?)")


def _walk(c: Cat, subst: dict[int, Cat]) -> Cat:
    while isinstance(c, CVar) and c.id in subst:
        c = subst[c.id]
    return c


def _occurs(vid: int, c: Cat, subst: dict[int, Cat]) -> bool:
    c = _walk(c, subst)
    if isinstance(c, CVar):

[CONTENT TRUNCATED] Showing lines 421 to 460 of 606 total lines. Use line_offset=460 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def \\|register_forward_hook\\|hook\\|def main\\|projecting it OUT\\|residual\\|patch\\|diff.of.means\\|crossover\" scripts/experiments/type_directed_v4_ablation.py | head -40"
}
```

**Summary:** $ grep -n "def \|register_forward_hoo...

**Output:**
```
Exit code: 0
Stdout:
5:v3 (nonce crossover) showed, frequency-free, that the model USES an in-context-taught
6:type to direct composition (crossover 8B +2.18/14B +2.04, t~9-10, consistency 1.0). But
8:in the residual stream and ABLATE it — if the type direction CAUSES the composition
9:behaviour, the v3 crossover COLLAPSES under type-direction ablation, while a RANDOM-
13:from the residual at the FILLER position (the token before the nonce — the next-token
14:bottleneck). VERB-taught -> that residual should carry "expect a predicate" so the nonce
16:DIRECTION = difference-of-means(verb - noun) of the filler-position residual (robust
19:INTERVENTION: project the unit type direction OUT of the residual at the filler position
21:drove composition, name_pen (and the crossover) collapse toward 0.
22:CONTROL: project out a RANDOM unit direction (same procedure) -> crossover survives.
24:VERDICT (lambda measure): type-ablation collapses the crossover AND random preserves it
26:behavioural; confirms s139 (type decodable+co-located) as DIRECTING dispatch. Both
75:def gen_items(n_each: int, seed: int, n_teach: int):
80:    def pick(pool, k):
96:def locate(item, tok):
108:def nonce_surprisal(logits_logp, ids, nonce_js):
113:def make_ablation_hook(direction_unit, pos_box, torch_mod, whole=True):
114:    """Forward hook on a decoder layer: project `direction_unit` OUT of the residual
117:    def hook(_module, _inp, out):
128:    return hook
131:def _auc(pos_scores, neg_scores):
142:def crossover_stats(surpr_by_cond_w):
143:    """Given cond->w->[surprisal], return det_pen, name_pen, crossover (paired by w)."""
144:    def cell(c, w):
158:    def agg(arr):
166:    return {"det_pen": agg(dpen), "name_pen": agg(npen), "crossover": agg(cross)}
169:def run_pass(items, model, tok, torch_mod, ablations=None):
173:    OUT of the filler-position residual at that layer (filler-stack ablation, so the
182:            handles.append(mod.register_forward_hook(
183:                make_ablation_hook(direction, pos_box, torch_mod)))
204:def collect_residuals(items, model, tok, torch_mod):
231:def main() -> None:
253:    # ── pass 1: collect filler-position residuals + baseline surprisal ──────────
254:    print("[type-dir4] pass 1: collecting residuals + baseline ...")
255:    rows, base = collect_residuals(items, model, tok, torch_mod)
280:    base_stats = crossover_stats(base)
281:    print(f"[type-dir4] BASELINE crossover={base_stats['crossover']} "
285:    # residual at EVERY hidden state h >= L* (so the type cannot be re-derived
286:    # downstream by attention to the teaching). hidden_states[h] <- hook layers[h-1].
302:    type_stats = crossover_stats(type_abl)
```

### Thinking

I'm grasping the core of the patching approach now—forward hooks modify residual outputs by projecting directions out. For the critical first experiment, I need to patch in the actual kernel K-move value itself rather than projecting something out. The conceptual challenge is defining what "exact kernel K-move" means as a residual-stream patch, since K is a function that drops its second argument and returns the first.

There are multiple ways to operationalize this at layer 18, and it's a genuine design fork that needs Michael's input. The cleanest framing is treating K as a pure routing operation—selecting the first argument and discarding the second—which as a residual patch becomes a sufficiency test of the detected direction. But translating "deliver K from the kernel" into an actual value-patch is where the subtlety lies.

Given how central this design choice is to the whole experiment, I should present the concrete protocol and the key fork to Michael before committing to one operationalization, though he did say to proceed. Let me find the strongest concrete design and start building while surfacing the central decision clearly.

The cleanest causal test I can build now is a patching sufficiency test of the K-direction at layer 18. I could either do activation patching—taking a K-engaging probe and a non-K probe, then patching the layer 18 residual content between them to see if the output flips toward K-behavior—or go for the harder kernel-value injection where I replace the residual with a value computed by the kernel's K-move directly. The first approach is safer and buildable immediately, paralleling the progression from ablation to patching, while the second requires solving the encode-decode problem between kernel symbols and residual vectors.

Michael said to proceed, so I should move forward, but Exp 1 has a real conceptual fork at its center. The responsible approach is to ground the design now by examining the RelationalCrystalClassifier internals to understand what a K-direction concretely is and whether kernel-value injection is even feasible, lay out the concrete protocol, then start building the decisive buildable version. Let me look at the classifier structure to see what directions and values are actually available.

## Assistant

The patching toolkit is clear (forward hooks that rewrite the residual). The crux of Exp 1 is **what "the exact kernel K-move" is as a residual-stream patch**. Let me read the classifier internals to know exactly what a "K-direction at L18" is, which determines the feasible design.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"class RelationalCrystalClassifier\\|def classify\\|centroid\\|self\\.\\|direction\\|def __init__\\|crystal_layers\\|CRYSTAL\\s*=\\|def calibrate\" scripts/instruments/relational_opcode.py | head -50"
}
```

**Summary:** $ grep -n "class RelationalCrystalCla...

**Output:**
```
Exit code: 0
Stdout:
18:  3. RELATIONAL — project onto per-combinator centroids built from the crystal probes;
42:CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
55:def _centroids(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
78:    U = _unit_rows(_centroids(X, labels))
108:    """Per-layer calibration: the common-mode, centroids, and the null."""
110:    centroids: np.ndarray                   # [9, d] unit per-combinator centroids (CMR)
127:class RelationalCrystalClassifier:
131:    def __init__(self, layers: list[int], *, n_perm: int = 300, z_thresh: float = 3.0,
134:        self.layers = list(layers)
135:        self.n_perm = n_perm
136:        self.z_thresh = z_thresh
137:        self.sil_z_thresh = sil_z_thresh
138:        self.seed = seed
141:        self.consensus_gram = (load_consensus_gram()
144:        self.calib: dict[int, LayerCalib] = {}
147:    def calibrate(self, gate_by_layer: dict[int, np.ndarray],
152:        labels [N] in CRYSTAL. Build per-layer common-mode, CMR centroids, the null,
157:            the null is the projection of NON-j crystal probes onto j's centroid. But
163:            centroid (through the SAME sign-CMR transform). Then z asks "does this token
167:        rng = np.random.default_rng(self.seed)
169:        for li in self.layers:
174:            cents = _centroids(X, labels)
177:            sims = Xu @ ucents.T                          # [N, 9] cos to each centroid
183:                # SAME sign-CMR transform onto each centroid; the per-op population is
194:                # off-target null per op: projection of NON-op probes onto op centroid
200:            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
201:            gc = (_offdiag_corr(_gram(cents), self.consensus_gram)
202:                  if self.consensus_gram is not None else float("nan"))
203:            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
204:            self.calib[li] = LayerCalib(
205:                common_mode=common, centroids=ucents, null_mean=nmean, null_std=nstd,
209:        return self.calib
212:    def crystal_layers(self) -> list[int]:
213:        return [li for li, c in self.calib.items() if c.crystal_bearing]
216:    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
221:        best_op, best_z = "·", self.z_thresh
222:        for li in self.layers:
223:            cal = self.calib.get(li)
231:            sims = cal.centroids @ (v / nv)               # [9] cos to each centroid
235:            sig = [op for op, zz in zmap.items() if zz > self.z_thresh]
246:        null_kinds = {c.null_kind for c in self.calib.values()}
248:            "n_layers": len(self.calib),
249:            "crystal_layers": self.crystal_layers,
252:                          for li, c in self.calib.items()},
253:            "z_thresh": self.z_thresh, "sil_z_thresh": self.sil_z_thresh,
254:            "has_consensus": self.consensus_gram is not None,
267:    # layer 1 = crystal-bearing (planted combinator directions); 0,2 = noise
284:    assert 1 in clf.crystal_layers, "planted crystal layer 1 not detected"
285:    assert 0 not in clf.crystal_layers and 2 not in clf.crystal_layers, \
287:    # a 'B' token: common-mode + B direction at layer 1
```

### Thinking

I'm seeing how the classifier works now — each crystal layer stores centroids that represent unit directions for different combinators in residual space. To detect the K-direction at layer 18, I project the gate token's residual onto the K-centroid and compute a z-score. For Experiment 1, the structured object I can work with is this K-centroid direction itself.

The causal test is straightforward: when a K-engaging probe fires strongly at layer 18 (z-score > 3.0), I can intervene by amplifying or injecting the K-centroid direction into the residual to deliver the kernel's K-move geometry directly. The key question is whether this preserves the model's output — if it does, that proves the K-direction is causally sufficient. A cleaner version uses counterfactual patching: take a probe where K doesn't fire and patch in the K-centroid to see if the output flips toward the K-computed result, which directly tests sufficiency.

The experiment has several concrete design choices: the probe set (67 crystal_probes K probes), the metric for "output preserved" (next-token logprob or kernel-verified reduction), the intervention (K-centroid at layer 18 scaled to a reference magnitude), and the control (random unit direction at the same magnitude). Given how critical this causal test is to the whole pivot and the real subtlety in operationalizing it correctly, the right move is to lay out the concrete design with its key fork and confirm the operationalization with Michael before building — because running the wrong causal test produces a misleading verdict that sticks around. Michael said to proceed, so I'm moving forward.

I'll build the cleanest, most defensible causal design I can operationalize now, and be explicit in the report about the design choice and alternatives so Michael can redirect if needed. This keeps claims conservative while exploring broadly, matching the rhythm from prior sessions where I design and build, then report.

The cleanest causal test is an activation-patching protocol: take a K-probe that engages the K combinator and produces the gold reduction, pair it with a non-K probe (like an I-probe or B-probe), then at layer 18 replace the non-K probe's residual component along the K-centroid with the K-probe's, and measure whether the output shifts toward the K-computation.

Actually, the most direct approach is simpler: run K-probes through three conditions—baseline to measure success at the K-computation, a splice where I replace the residual's combinator-subspace component with the exact K-centroid at layer 18 when the K-signal is strong, and a random-direction control at the same magnitude. If the splice preserves output while random degrades it, the K-direction is the causal carrier. This is buildable now using the existing hook infrastructure to intercept and overwrite the K-subspace component.

The key detail is using the empirical mean projection magnitude from true K-firings as the "canonical K value" the kernel delivers. I'm torn between presenting the design first for a quick confirmation versus just building it directly—the scope is substantial, but Michael said "proceed" and the session rhythm favors moving forward. I'll compromise by writing up the concrete design with all three arms and the intervention details, then start building the script while surfacing the design as I go, so Michael can redirect on the counterfactual variant if needed before the expensive GPU run.

Actually, let me check the knowledge page to see exactly what was already decided for Exp 1 so I build precisely that rather than overcomplicating.

## Assistant

The K-direction at L18 is concretely `calib[18].centroids[K]` — a unit vector (the sign-CMR centroid). That's the "exact K geometry" available to splice. Let me read the Exp 1 spec already written in the knowledge page to build precisely what was scoped.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md",
  "line_offset": 60,
  "limit": 50
}
```

**Summary:** Reading kernel-splice-geometry-detector.md (60-110)

**Output:**
```

1. **Detection is a weak, model-specific centroid — not a crisp per-step switch.** The
   geometry is largely ONE COMMON MODE (s211: η²=0.05 for ops); B is invisible in the FFN
   gate (lives in attention/value), D/W are *anti*; the C-locus SHIFTS with scale
   (`c-late-composition-is-model-specific`: 8B non-specific, 14B L27-32, 32B L5-11). The
   PROVEN invariant is the **skeleton** (C-origin, boot order, {C,I,K,Y}, confluence) —
   fine-grained per-firing geometry **over-reads**. Detect K-*ness* as an aggregate lean
   in a readable zone, model-specifically; cannot yet threshold "K fires, exactly here."

2. **The operands, not just the operator.** Detecting "wants K" is the easy
   (routing-register, crisp-ish) half. Executing needs the **argument binding** — which
   slots are x and y — and that argument structure lives in the VALUE register (s206),
   the continuous/graded substrate. K is pure routing *once the slots are known*;
   identifying the slots at that layer is the unsolved decode.

3. **No discrete step — the firing is smeared.** Reduction is distributed (~1.018×/layer
   rotation, the C→B/K→I→WHNF boot spiral, vsm-statechart-tensor.md). No single layer
   "fires K," so interception has a registration problem, and the re-injected exact
   result must be IN-DISTRIBUTION for downstream layers (λ coherence).

## The experiment program (start where detection is proven, build up causally)

### Exp 0 — detectability map (cheap, decisive precursor)

Ground truth exists: `lambda_ast.fired_sequence` gives the **certified** combinator
program for any corpus reduction. Measure how reliably the lattice classifier recovers
that sequence (operator AND position), per combinator, per layer, per model. Output = a
**splice-readiness map**: which combinators at which loci are reliable enough to act on.
Decides whether obstacle 1 is fatal *before* touching a forward pass.

- substrate: certified reductions (canonical corpus + `fired_sequence`)
- read: RelationalCrystalClassifier / lattice centroids per layer (per-model readable zone)
- metric: recovery of {operator, position} vs `fired_sequence`; per-combinator, per-layer
- expected: {C,I,K,Y} recoverable in their depth zones; B/D/W not (register-blind)

### Exp 1 — single-combinator causal splice

Take the most-detectable invariant op (**K**: selector, pure routing, discriminable,
mid-depth). At the per-model readable zone, replace the model's local computation with
the **exact kernel K-move**; measure output **preserved/improved vs a random-direction
control** — the s239 sufficiency/necessity protocol. The minimal "deliver K from the
kernel" instance.

### Exp 2 — sequence / kernel-in-the-loop

Build from one splice toward decoding the program at a CUT → exact reduce → lower back
(connects to compiler-as-loss §s242 stage 3: the constructed kernel, now as an in-stream
patch rather than a standalone tensor).

## ★ s242 — Exp 0 RESULTS (Qwen3-14B): precision-gated, not high-recall

[CONTENT TRUNCATED] Showing lines 61 to 110 of 214 total lines. Use line_offset=110 parameter to read more content.
```

### Thinking

I'm working through Experiment 1's specification: taking kernel K at the readable zone with τ=3.0, replacing the model's local computation with the exact K-move, then measuring whether output is preserved or improved against a random-direction control using the s239 sufficiency/necessity protocol. The second obstacle is that executing this requires argument binding to determine which slots are x and y in the VALUE register, though once those slots are identified, K becomes pure routing.

There's a conceptual subtlety here: to truly deliver the kernel K-move, I need to know the operand slots. But there's a cleaner first causal test that sidesteps full execution — testing whether the detected K-direction is causally sufficient using the s239 sufficiency/necessity protocol on the K-centroid direction. This tests "deliver K geometry" rather than "deliver K with bound operands," which is exactly what Experiment 1 should be.

Since the page already scoped Experiment 1 as the s239 sufficiency/necessity protocol on K at the readable zone, and the s239 v4/v5 toolkit exists, the cleanest approach is to run a K-direction causal sufficiency/necessity test at L18. For necessity, I'd ablate by projecting the K-centroid out of the L18 residual at the gate position and check if K behavior degrades compared to a random-direction control. For sufficiency, I'd inject the exact K-centroid at canonical magnitude into weak-detection probes or neutral baselines and check if K behavior strengthens. The K-centroid direction at canonical magnitude serves as the geometric proxy for the exact kernel K-move, and the verdict comes from whether K-centroid ablation degrades K behavior while random controls preserve it.

This is buildable now using the v4 hook and classifier centroids directly, and it's the decisive next step. I need to design this concretely and build it — this is clearly a proceed-and-build instruction. I'll construct the script, test it, and report the results, surfacing the design and the honest limitation that this tests geometric K-delivery rather than operand-bound execution.

To build this efficiently, I need to read through the v4 patching mechanics — specifically make_ablation_hook, run_pass, and collect_residuals — to understand how positions are tracked and how to access the K-centroid from the calibrated classifier. I also need to understand the sign-CMR transform used in classify so the injection happens in the right space.

Let me check where the centroids actually live — whether they're in raw residual space or transformed space — by looking at how calibrate computes them from gate activations and how classify uses them with the sign-CMR adjustment.

## Assistant

The page scoped Exp 1 precisely: the s239 sufficiency/necessity protocol on K at the firmed locus, with the honest flag that full execution needs operand binding (= Exp 2), so Exp 1's minimal instance is the **K-direction causal test**. Let me read the exact patching + classify internals to build it correctly in the right vector space.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py",
  "line_offset": 100,
  "limit": 145
}
```

**Summary:** Reading relational_opcode.py (100-245)

**Output:**
```
        return None
    return np.array(d["consensus_gram"], dtype=np.float64)


# --------------------------------------------------------------------------- #
@dataclass
class LayerCalib:
    """Per-layer calibration: the common-mode, centroids, and the null."""
    common_mode: np.ndarray                 # [d] mean sign(gate) over calib probes
    centroids: np.ndarray                   # [9, d] unit per-combinator centroids (CMR)
    null_mean: np.ndarray                   # [9] null projection mean per op
    null_std: np.ndarray                    # [9] null projection std per op
    silhouette_z: float                     # crystal significance at this layer
    gc_consensus: float                     # Gram alignment to consensus (or nan)
    crystal_bearing: bool                   # sil_z>thresh (∧ gc>0 if consensus present)
    null_kind: str = "offtarget"            # "offtarget"(crystal) | "crosstask"


@dataclass
class TokenOpcodes:
    """One token's per-layer opcode read."""
    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
    emitted: dict = field(default_factory=dict)      # li -> [significant ops]
    dominant: str = "·"                              # max-z op (crystal) or no-op


class RelationalCrystalClassifier:
    """Validated FFN-routing opcode reader: gate register, sign-CMR,
    consensus-relational, null-calibrated. Model-agnostic (gate feature matrices in)."""

    def __init__(self, layers: list[int], *, n_perm: int = 300, z_thresh: float = 3.0,
                 sil_z_thresh: float = 2.0, seed: int = 0,
                 consensus_gram: np.ndarray | str | None = "auto"):
        self.layers = list(layers)
        self.n_perm = n_perm
        self.z_thresh = z_thresh
        self.sil_z_thresh = sil_z_thresh
        self.seed = seed
        # "auto" -> load the project consensus; None -> disable (synthetic/no-target);
        # ndarray -> use as given.
        self.consensus_gram = (load_consensus_gram()
                               if isinstance(consensus_gram, str)
                               else consensus_gram)
        self.calib: dict[int, LayerCalib] = {}

    # -- S5 calibration: build the per-layer crystal from the probe activations -- #
    def calibrate(self, gate_by_layer: dict[int, np.ndarray],
                  labels: np.ndarray,
                  null_gate_by_layer: dict[int, np.ndarray] | None = None,
                  ) -> dict[int, LayerCalib]:
        """gate_by_layer[li] = [N, d] gate last-token features for the N crystal probes;
        labels [N] in CRYSTAL. Build per-layer common-mode, CMR centroids, the null,
        silhouette-z, and consensus Gram alignment.

        NULL (s231 v2 — the over-read-killer that no longer under-reads):
          - null_gate_by_layer=None (default, BACK-COMPAT): off-target null — per op j
            the null is the projection of NON-j crystal probes onto j's centroid. But
            every crystal probe is lambda-mode, so "looks more like B than K/I/C?" has
            LOW POWER (the s231 under-read: the C→B arc no-ops at z=3).
          - null_gate_by_layer[li] = [M, d] NON-combinator baseline gate features (e.g.
            natural-text / retrieval tokens where no β-reduction happens): CROSS-TASK
            null — per op j the null is the projection of BASELINE tokens onto j's
            centroid (through the SAME sign-CMR transform). Then z asks "does this token
            look more like op j than a typical natural-text token does?" — recovers the
            lambda compose-arc while keeping retrieval silent."""
        labels = np.asarray(labels)
        rng = np.random.default_rng(self.seed)
        null_kind = "crosstask" if null_gate_by_layer is not None else "offtarget"
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)
            S = np.sign(G)
            common = S.mean(axis=0)                       # the common-mode (gauge)
            X = S - common                                # sign-CMR routing features
            cents = _centroids(X, labels)
            ucents = _unit_rows(cents)
            Xu = _unit_rows(X)
            sims = Xu @ ucents.T                          # [N, 9] cos to each centroid
            li_idx = np.array([CRYSTAL.index(c) for c in labels])
            nmean = np.zeros(len(CRYSTAL))
            nstd = np.ones(len(CRYSTAL))
            if null_gate_by_layer is not None:
                # CROSS-TASK null: project baseline (non-combinator) tokens through the
                # SAME sign-CMR transform onto each centroid; the per-op population is
                # the natural-text baseline distribution.
                B = np.asarray(null_gate_by_layer[li], dtype=np.float64)  # [M, d]
                Vb = np.sign(B) - common                                  # CMR baseline
                Vbu = _unit_rows(Vb)
                bsims = Vbu @ ucents.T                                    # [M, 9]
                for j in range(len(CRYSTAL)):
                    col = bsims[:, j]
                    nmean[j] = col.mean()
                    nstd[j] = col.std() + 1e-9
            else:
                # off-target null per op: projection of NON-op probes onto op centroid
                for j in range(len(CRYSTAL)):
                    off = sims[li_idx != j, j]
                    if off.size:
                        nmean[j] = off.mean()
                        nstd[j] = off.std() + 1e-9
            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
            gc = (_offdiag_corr(_gram(cents), self.consensus_gram)
                  if self.consensus_gram is not None else float("nan"))
            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
            self.calib[li] = LayerCalib(
                common_mode=common, centroids=ucents, null_mean=nmean, null_std=nstd,
                silhouette_z=round(sil_z, 3),
                gc_consensus=(round(gc, 3) if not np.isnan(gc) else float("nan")),
                crystal_bearing=bool(bearing), null_kind=null_kind)
        return self.calib

    @property
    def crystal_layers(self) -> list[int]:
        return [li for li, c in self.calib.items() if c.crystal_bearing]

    # -- S1 classify: token gate -> null-calibrated per-op z, emit if significant -- #
    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
        """gate_by_layer_token[li] = [d] one token's gate at layer li. Returns per-layer
        op z-scores, the significant (z>thresh) opcodes, and the dominant op across
        crystal-bearing layers (or '·' no-op if none significant)."""
        out = TokenOpcodes()
        best_op, best_z = "·", self.z_thresh
        for li in self.layers:
            cal = self.calib.get(li)
            if cal is None:
                continue
            g = np.asarray(gate_by_layer_token[li], dtype=np.float64)
            v = np.sign(g) - cal.common_mode
            nv = np.linalg.norm(v)
            if nv < 1e-12:
                continue
            sims = cal.centroids @ (v / nv)               # [9] cos to each centroid
            z = (sims - cal.null_mean) / cal.null_std     # null-calibrated per op
            zmap = {op: round(float(zz), 3) for op, zz in zip(CRYSTAL, z, strict=True)}
            out.per_layer[li] = zmap
            sig = [op for op, zz in zmap.items() if zz > self.z_thresh]
            if sig:
                out.emitted[li] = sig
            if cal.crystal_bearing:                       # dominant: crystal only
                j = int(np.argmax(z))
                if z[j] > best_z:
                    best_op, best_z = CRYSTAL[j], float(z[j])
        out.dominant = best_op
        return out

    def calibration_summary(self) -> dict:

[CONTENT TRUNCATED] Showing lines 101 to 245 of 322 total lines. Use line_offset=245 parameter to read more content.
```

### Thinking

The classifier actually works on the gate activations within the FFN layer itself, not the residual stream—specifically the sign-projected gate features from the SwiGLU mechanism. The detection hinges on comparing the sign of these gate activations against learned centroids in the sign-CMR space, which adds a layer of complexity to how the opcode_monitor identifies patterns.

This creates a fundamental problem for causal intervention: you can't simply inject the K-centroid as a residual-stream patch because the detection operates in a nonlinear sign-space that's only loosely coupled to the actual gate pre-activations. A faithful ablation would need to intervene directly on the FFN gate itself, not the residual output. The v4 approach hooked the decoder layer output, but that's downstream of where the actual detection happens.

This leaves two possible paths forward: either suppress the gate units most aligned with the K-centroid and measure behavioral degradation, or attempt a direct gate-space injection to force the gate activations toward the K-centroid pattern.

Given this is the decisive experiment and I've uncovered a real design crux about where the intervention should live, I think the responsible move is to present this to Michael before building—not to delay, but to confirm we're intervening in the right space. Publishing a causal claim based on the wrong intervention site would be worse than a brief design check now.

I'll write up a focused proposal: what Exp 1 concretely measures, why the FFN-gate sign-space is where detection actually happens (not the residual), my recommended three-arm design with the key metrics, and the one fork Michael needs to steer—whether we're testing sufficiency (does the exact K-centroid injection preserve what the neuron already does?) or counterfactual delivery (does it make the model do K when it wouldn't otherwise?). I'll mark the build as blocked on this decision and keep the proposal tight.

## Assistant

I've hit a genuine design crux that needs your steer before I build the decisive experiment — surfacing it rather than guessing, because a wrongly-specified causal test gives a misleading verdict.

## The crux I found reading the internals

The detector does **not** read the residual stream — it reads the **FFN gate register** in **sign-CMR space**: `v = sign(gate) − common_mode`, projected onto unit per-combinator centroids. The "K-direction at L18" is `calib[18].centroids[K]`, a unit vector living in **sign(gate)-space**, not the residual.

This matters because the s239 v4 toolkit ablated the **residual stream** (a clean continuous projection). A *faithful* causal test of "the detected K-geometry causes K behavior" must intervene where the detection lives — the **L18 FFN gate** — and "deliver the exact kernel K-move" = force the gate's sign-pattern toward `common_mode + K-centroid`. Sign-space injection is more delicate than a residual add (this is obstacle 3 — smeared firing + the in-distribution re-injection requirement — made concrete).

## Concrete Exp 1 design (what I'd build)

**Target:** K at the firmed locus L18, gate τ=3.0 (Exp 0.5). K = pure routing → no operand decode needed (sidesteps obstacle 2). Honest scope: this delivers K *geometry/routing*, not operand-bound execution (that's Exp 2) — exactly the page's "minimal instance."

**Three arms, on the 67 K-probes (gold continuations known via the kernel):**
1. **Baseline** — K-probes, measure K-computation success (gold-continuation logprob + kernel-certify rate).
2. **K-splice** — hook L18 gate; where z(K)>3.0, overwrite the gate's combinator-subspace so `sign(gate)−common_mode` aligns with the exact K-centroid at canonical "K-fired" magnitude.
3. **Random control** — same magnitude, random unit direction (s239).

**Verdict (λ measure):** splice **preserves** ∧ random **degrades** → the K-direction is the sufficient causal carrier → the geometry is replaceable by the kernel's exact move with no loss = splice works, thesis proven causally + no-training hybrid. Splice breaks → geometry over-read (λ measure win) → redirect to constructed front-end.

## The one fork I need you to pick

How to operationalize "deliver the K-move":

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which causal operationalization for the Exp 1 K-splice (intervening on the L18 FFN gate, sign-CMR space)?",
  "options": [
    {
      "label": "Sufficiency-preserve on K-probes (Recommended)",
      "description": "On K-engaging probes, replace the gate's combinator-subspace with the EXACT K-centroid (the kernel's K geometry) and test the K-computation is PRESERVED vs random-direction control. Plus a necessity arm (suppress the K-centroid → K behavior degrades). Cleanest 'can the kernel value replace the neuron' test; directly the s242 splice vision."
    },
    {
      "label": "Counterfactual delivery on non-K/corrupted probes",
      "description": "Inject the K-centroid into probes where K does NOT fire (or corrupted K-probes) and test the output FLIPS toward the K-computation. A stronger sufficiency claim (K geometry MAKES the model do K), but messier: needs matched non-K donors and risks out-of-distribution gate states."
    },
    {
      "label": "Both arms (preserve + counterfactual)",
      "description": "Build both: preserve-on-K-probes for the clean replacement test, plus counterfactual-on-non-K for the stronger sufficiency claim. More work, most complete causal picture in one run."
    }
  ]
}
```

**Summary:** Q: Which causal operationalization for the Exp ...

**Output:**
```
User answered: Both arms (preserve + counterfactual)
```

### Thinking

I'm setting up two experimental arms to test Michael's approach. The preserve arm will replace the gate combinator-subspace with the exact K-centroid on K-probes to verify K-computation is preserved, plus a necessity check by suppressing it to see degradation. The counterfactual arm injects the K-centroid into non-K or corrupted probes to flip outputs toward K-computation. Now I need to figure out how to hook into the FFN gate at the layer level.

The core technical challenge is understanding what tensor the opcode_monitor reads as "gate"—whether it's the full SwiGLU activation or just the gate projection—since that determines what I'm patching. For the sign-CMR injection, I want to modify the gate so that its sign minus the common mode aligns with the K-centroid direction. The cleanest approach is an additive intervention on the gate that nudges its sign toward the target direction without crude flipping.

But there's a tension: the detector reads only the sign pattern, while the actual FFN computation depends on the gate's full magnitude. If I only manipulate signs to match c_K, the FFN output changes drastically and breaks downstream behavior—defeating the test of whether the K-centroid direction is truly causal. To stay in-distribution while testing sufficiency, I need to carefully calibrate the magnitude of the injection. Given the registration and magnitude obstacles, maybe the cleaner first approach is to intervene on the residual stream instead, using the gate-derived detection as a trigger for when to act, and the actual intervention being a residual-space patch of the K result. But that raises the question of what the K direction even is in residual space. The s239 v4/v5 protocol mentioned on the page operates on the residual, so that might be the right framework to follow. The re-injection point is naturally the residual stream since that's what downstream layers read, so detection in gate-space and effection in residual-space aren't a bug—they're the correct architecture. I'll compute the K residual direction as the difference-of-means between K-probes and non-K-probes at layer 18's residual output, then gate interventions on z(K)>3.0 to either add or remove that direction and measure the effect against random controls. This design reuses v4's infrastructure (the decoder layer 18 hook and calibrated gate centroids) and cleanly separates the detector from the effector. Now I'm moving into the build plan for the experiment script. For the counterfactual arm, I need to handle the fact that non-K probes don't share continuations with K-probes. The cleanest approach is to use corrupted versions of the K-probes themselves—scramble the prompt so the gate doesn't fire, then inject d_K and check if the gold K-continuation logprob gets restored, which gives me a matched-item restoration test.

Actually, a more practical counterfactual: on K-probes where z(K) ≤ 3.0 (the under-detected firings from the recall gap), inject d_K and measure whether the gold logprob rises—this tests whether delivering the K-direction rescues the weak geometric detections, all within the same probe and continuation.

The preserve arm flips this: on detected K-probes (z(K) > 3.0), replace d_K with its canonical value and verify the gold logprob stays stable, confirming the kernel's exact value reproduces what the neuron computed. Necessity comes from projecting d_K out on detected probes and watching the logprob drop.

All three arms use the same K-probe set and gold-continuation metric, partitioned by detection strength—it's coherent and kernel-grounded. Now I need to figure out the gold continuation for each K-probe. The probe fields don't include an explicit gold output, so I'll need to extract that from the prompt structure itself.

Actually, maybe the metric is simpler: just check if the next-token distribution stays preserved after patching. If the model produces the same greedy next token or similar logit distribution as baseline, that's evidence the splice worked. For necessity, the distribution should shift when we remove d_K. But that doesn't directly verify K-correctness the way a kernel-grounded metric would. Let me look at the actual K crystal probes to see if there's a verifiable gold output embedded in them.

## Assistant

Michael chose **both arms**. Reading the classifier internals resolved my crux in a clean way (not a compromise): **detection lives in gate-space, but re-injection belongs in the residual** (downstream layers read the residual) — so gate=detector, residual=effector is *correct*, not a mismatch. Before I lock the build, let me inspect actual K crystal probes to nail the kernel-grounded metric.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python -c \"\nfrom verbum.probes.library import crystal_probes\nks=[p for p in crystal_probes() if p.combinator=='K']\nprint('n K probes:', len(ks))\nfor p in ks[:6]:\n    print('---')\n    print('id:', p.id, '| cat:', p.category, '| tags:', p.tags)\n    print('prompt:', repr(p.prompt))\n\" 2>&1 | grep -v Warning"
}
```

**Summary:** $ .venv/bin/python -c " from verbum.p...

**Output:**
```
Exit code: 0
Stdout:
n K probes: 67
---
id: lk_0000 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'Of all the animals in the zoo, only the lion was truly'
---
id: lk_0001 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'Among the candidates, the committee chose the one who had the most'
---
id: lk_0002 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'Between coffee and tea, she always prefers'
---
id: lk_0003 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'Despite the rain, the cold, and the wind, the hikers continued to'
---
id: lk_0004 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'Ignoring the noise from the construction site next door, the student focused on'
---
id: lk_0005 | cat: lambda_K_select | tags: ('tier1', 'axis:lambda_K_select')
prompt: 'If the test is positive, the doctor will prescribe medication; otherwise the patient can go'
```

### Thinking

I'm realizing these probes work differently than formal lambda terms—they're prose that semantically engages the K-pattern through selection and projection, like "of all X, only the lion was truly..." which drops everything except one element. There's no clean single-token reduction to verify, but rather next-token prediction where the K-routing is the actual computation happening.

This reframes how I measure the effect: "output preserved" becomes about whether the model's next-token distribution stays unchanged when I splice in the exact K-geometry, and "K-behavior" gets measured through the detector and output distribution. So the core experimental claims shift to testing whether replacing the K residual component with the kernel's exact K-centroid preserves the output distribution (low KL divergence), versus random replacements that corrupt it, and whether removing the K-direction perturbs the output more than random removal—showing it's functionally necessary. The trickier part is the counterfactual: injecting K into non-K probes should shift outputs toward K-like continuations, but for under-detected probes the target becomes the model's own well-detected K behavior, which feels circular.

The real issue is that the crystal probes I used for detection have no kernel-certifiable gold standard, so measuring "flips toward K-computation" objectively is hard. The original splice vision assumed a formal lambda corpus with kernel-reducible gold outputs, but my detection was grounded in crystal prose probes without that. To run a kernel-grounded Exp 1, I'd need probes that both engage K cleanly and have verifiable outputs—which points back to the canonical corpus with prose-to-FOL pairs and certified combinator firing sequences. The metric design is really the crux here, more than the intervention space itself.

The cleanest approach is to use output-distribution preservation via KL divergence under intervention, with three arms that give a coherent causal picture: random-replace as the noise floor, K-replace at the exact centroid to test sufficiency, and K-ablate versus random-ablate to test necessity. The key insight is that if K-replace KL is near zero while random-replace KL is large (both at the same magnitude), that means the model's output is invariant to substituting the exact K-value but sensitive to random perturbations—so the K-direction carries a specific value the model already has, and the kernel's exact value matches it. That's the splice-preservation claim made meaningful through the contrast.

But actually, on true K-probes where the residual already has the canonical K-value, replacing it with that same value is essentially a no-op, so KL≈0 trivially and isn't informative. The real tests are necessity (removing the K-direction perturbs output more than random removal) and counterfactual delivery (adding the canonical K-value to non-K probes shifts the output toward K-reading more than random addition). The "preserve" claim is really the conjunction of both—necessity plus sufficiency—not a separate KL test. So Experiment 1 should measure necessity and counterfactual delivery, both versus random controls, using detector z(K) shift and output-distribution shift as metrics.

This is the s239 v4/v5 protocol applied to the K residual direction at the calibrated locus, gated by the detector. The metric is output KL plus detector z(K), no gold standard needed. The "exact kernel value" in prose probes reduces to the canonical K-direction at canonical magnitude—a geometric proxy. True kernel-value injection with bound operands requires formal lambda probes (Experiment 2 on the corpus), so Experiment 1 really tests the K-direction's causal sufficiency and necessity as a prerequisite for the operand-bound kernel splice. I should stick with crystal_probes rather than switching to formal lambda probes, since the detection locus was calibrated on prose; changing the probe distribution would invalidate it. I'll note this as a caveat—the geometric splice on prose substrate, with kernel-grounded verification deferred to Experiment 2.

I'm going to flag the metric refinement to Michael since it reframes "output preserved" as "output-distribution KL plus detector z(K)," but this is a natural consequence of using prose probes, and the necessity plus counterfactual framing matches his s239 protocol design. I'll document it clearly in the report with caveats and let him redirect if he wants formal lambda probes instead. Now I need to plan the build carefully—this is a substantial script. I should read through the v4 hook mechanics precisely, including how the gate detector and residual hook work together in a single forward pass.

## Assistant

These probes are **prose that engages K-semantics** (selection/projection), not formal `K a b` terms — so there's no single-token kernel-certifiable gold. That refines what "output preserved" can mean here: the kernel-grounded *certify* metric belongs to formal-lambda probes (Exp 2 / the corpus); on this prose substrate the decisive, objective metric is the **s239 protocol** itself — detector z(K) shift + output-distribution shift (KL / logprob) under intervention vs a random-direction control. That's exactly the necessity/sufficiency test the design references.

Let me read the v4 hook + the gate-capture mechanics precisely so I can gate (gate-space detect) and effect (residual patch) in one pass.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/type_directed_v4_ablation.py",
  "line_offset": 112,
  "limit": 100
}
```

**Summary:** Reading type_directed_v4_ablation.py (112-212)

**Output:**
```
def make_ablation_hook(direction_unit, pos_box, torch_mod, whole=True):
    """Forward hook on a decoder layer: project `direction_unit` OUT of the residual
    (output[0]). whole=True -> ALL token positions (global concept removal, so the type
    cannot be re-read from the teaching tokens); else only `pos_box[0]` (the filler)."""
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)
        if whole:
            coeff = h[0] @ d  # [T]
            h[0] = h[0] - coeff[:, None] * d[None, :]
        else:
            pos = pos_box[0]
            v = h[0, pos, :]
            h[0, pos, :] = v - (v @ d) * d
        return out
    return hook


def _auc(pos_scores, neg_scores):
    """Mann-Whitney AUC: P(verb proj > noun proj)."""
    pos, neg = np.asarray(pos_scores), np.asarray(neg_scores)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[: len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def crossover_stats(surpr_by_cond_w):
    """Given cond->w->[surprisal], return det_pen, name_pen, crossover (paired by w)."""
    def cell(c, w):
        v = surpr_by_cond_w[c].get(w, [])
        return float(np.mean(v)) if v else None

    dpen, npen, cross = [], [], []
    for w in NONCE:
        cells = [cell(f"{fr}_{ty}", w) for fr in ("det", "name")
                 for ty in ("verb", "noun")]
        if all(c is not None for c in cells):
            dv, dn, nv, nn = cells
            dpen.append(dv - dn)
            npen.append(nv - nn)
            cross.append((dv - dn) - (nv - nn))

    def agg(arr):
        a = np.asarray(arr)
        if len(a) < 2:
            return None
        se = float(a.std(ddof=1) / np.sqrt(len(a)))
        return {"mean": round(float(a.mean()), 4),
                "t": round(float(a.mean() / se) if se > 0 else 0.0, 3), "n": len(a)}

    return {"det_pen": agg(dpen), "name_pen": agg(npen), "crossover": agg(cross)}


def run_pass(items, model, tok, torch_mod, ablations=None):
    """Forward each item; ablate the filler position across a STACK of layers.

    ablations = list[(layer_module, direction_vector)] — each projects its direction
    OUT of the filler-position residual at that layer (filler-stack ablation, so the
    type cannot be re-derived downstream). Returns cond->w->[surprisal]."""
    import torch.nn.functional as func
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    pos_box = [0]
    handles = []
    if ablations:
        for mod, direction in ablations:
            handles.append(mod.register_forward_hook(
                make_ablation_hook(direction, pos_box, torch_mod)))
    try:
        for it in items:
            enc, nonce_js, fpos = locate(it, tok)
            if not nonce_js or fpos is None or fpos < 0:
                continue
            pos_box[0] = fpos
            ids = enc["input_ids"][0]
            with torch_mod.no_grad():
                logits = model(input_ids=ids.unsqueeze(0).to(dev),
                               attention_mask=enc["attention_mask"].to(dev)).logits[0]
            logp = func.log_softmax(logits.float(), dim=-1).cpu()
            s = nonce_surprisal(logp, ids.cpu(), nonce_js)
            if s is not None:
                out[it["cond"]][it["w"]].append(s)
    finally:
        for h in handles:
            h.remove()
    return out


def collect_residuals(items, model, tok, torch_mod):
    """Forward with output_hidden_states; return (rows, baseline-surprisal dict). Each
    row = (item, resid[L+1,H] at FILLER pos, label 1=verb/0=noun)."""
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    import torch.nn.functional as func
    rows = []
    for it in items:
        enc, nonce_js, fpos = locate(it, tok)

[CONTENT TRUNCATED] Showing lines 113 to 212 of 357 total lines. Use line_offset=212 parameter to read more content.
```

### Thinking

I need to understand how the gate-capture mechanics work in opcode_monitor_v2, specifically how forward_all_positions captures gate features and maps them to layer indices. I'm looking for which module corresponds to "layer 18 decoder" for the residual hook and which one handles the gate projection for detection.

## Assistant

I have the residual-hook pattern. Now the gate-capture mechanics (for detection) — let me read `forward_all_positions` and `load_model_and_tokenizer` in opcode_monitor_v2:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def forward_all_positions\\|def load_model_and_tokenizer\\|gate_proj\\|def calibrate_v2\\|register_forward\\|hidden_states\\|act_fn\\|up_proj\\|mlp\\|\\.layers\\b\\|store\\[\" scripts/instruments/opcode_monitor_v2.py | head -40"
}
```

**Summary:** $ grep -n "def forward_all_positions\...

**Output:**
```
Exit code: 0
Stderr:
grep: scripts/instruments/opcode_monitor_v2.py: No such file or directory
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && find . -path ./.venv -prune -o -name \"opcode_monitor_v2.py\" -print && echo \"---\" && F=$(find . -path ./.venv -prune -o -name \"opcode_monitor_v2.py\" -print | head -1) && grep -n \"def forward_all_positions\\|def load_model_and_tokenizer\\|gate_proj\\|def calibrate_v2\\|register_forward\\|hidden_states\\|act_fn\\|up_proj\\|mlp\\b\\|\\.layers\\|store\" \"$F\" | head -40"
}
```

**Summary:** $ find . -path ./.venv -prune -o -nam...

**Output:**
```
Exit code: 0
Stdout:
./scripts/experiments/opcode_monitor_v2.py
---
138:    "She walked to the store yesterday.",
155:def _make_hook(store: dict[int, np.ndarray], layer_idx: int):
162:        store[layer_idx] = vec.astype(np.float64)
170:    hook='gate' → mlp.gate_proj output (the FFN gate register, default).
174:    layer = model.model.layers[li]
176:        return layer.mlp.gate_proj
185:def load_model_and_tokenizer(model_name: str):
201:def forward_all_positions(
206:    hook ∈ {'gate' (default, mlp.gate_proj), 'attn' (self_attn.o_proj)}.
208:    store: dict[int, np.ndarray] = {}
211:        h = _hook_module(model, li, hook).register_forward_hook(
212:            _make_hook(store, li)
225:    return store, n_tokens
236:def calibrate_v2(
269:        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers,
272:            gate_by_layer[li].append(store[li][-1])  # last token = the crystal locus
283:            store, n = forward_all_positions(
287:                null_by_layer[li].append(store[li][lo:])  # content tokens only
292:            store, _n = forward_all_positions(s, model, tok, torch_mod, layers,
295:                null_by_layer[li].append(store[li])  # [T, d], all positions
319:    rcc: RelationalCrystalClassifier, store: dict[int, np.ndarray],
325:        gate_tok = {li: store[li][pos] for li in layers}
499:            store, n = forward_all_positions(prompt, model, tok, torch_mod, layers)
505:                read_prompt_tokens(rcc, store, layers, positions)
660:    parser.add_argument("--smoke", action="store_true",
```

### Thinking

I'm mapping out the detection mechanism by hooking into the gate projection's forward output to capture gate activations, then using the classifier to read the last token's features. For the residual effect, I'm hooking the decoder layer's output and modifying the residual hidden state.

The key insight is that gate_proj fires before the layer output in a single forward pass, but the detection decision (z(K) > 3.0) needs to happen before applying the effect. So I'm splitting this into two passes: first pass captures the gate values and makes the classification decision about which probes to act on, then the second pass applies the residual modification at those decided positions. The target position for the effect is the last token, which is where the next-token prediction happens.

For measuring the effect, I'm looking at whether injecting the K direction makes the detector itself read K (z(K) rises above 3.0) on non-K probes—that's the cleanest sufficiency signal, showing the injected direction is geometrically sufficient to trigger the model's own gating mechanism.

But there's a subtlety: the gate detector is computed inside the MLP at layer 18, upstream of the layer output where I'd patch. So patching the layer-18 residual output won't affect the layer-18 gate itself. I need to re-read the detector at a downstream layer like layer 19 to see the causal propagation from the patched residual through the gate and into the output.

The cleanest approach is to focus on the final output distribution as the ground truth. For necessity, I ablate the K-direction at layer 18 and check if the final output shifts more than a random ablation of equal magnitude. For sufficiency, I inject the K-direction into non-K probes and measure whether the downstream detector reads K and the output shifts in a K-consistent way. Since the detector is the project's validated readout, I can use it directly: inject the residual K-direction, re-read z(K) across all layers downstream of the patch, and check if both the detector activates and the final output reflects K-like behavior.

The key control is comparing against random directions of the same magnitude—if the K-direction specifically drives K-reading while random doesn't, that's genuine sufficiency. Both necessity and sufficiency are measured by detector activation and output KL divergence relative to random controls, which aligns with the register-correct protocol.

Now I'm scoping the implementation: the main script will take arguments for model, patch layer (defaulting to 18), gate threshold, held-out calibration percentage, magnitude mode, seed, and smoke-test flag. I'll load the model, calibrate the gate detector on held-out data, build probe sets for K and non-K cases, and run the splice experiments.

Setting up the measurement pipeline... I'll set up a single forward pass per probe that captures gate activations across all layers, residuals at each layer, and final logits by hooking the gate projections and requesting hidden states. For each arm in the patching phase, I'll register the patch hook at the target layer plus re-read the gates downstream to track how the intervention propagates. This gives me roughly 275 total forwards across the baseline and three arms with two direction variants, which should run in 5-10 minutes on the 14B model. It's a complex pipeline with many moving parts, so I'll code it carefully, test on the smaller model first, then scale up.

Let me pull in the helpers I need from the existing modules—_make_hook and _hook_module from opcode_monitor, split_probes and read_last_token_z from prose_v2, and the CRYSTAL config. The read_last_token_z function already gives me the per-layer z map for the last token, so I can extract z(K) at any layer directly. For computing d_K, I need the residual after the patch layer, which is hidden_states[patch_layer+1] since the model's hidden_states tuple has embeddings at index 0 and layer i's output at index i+1. The residual hook modifies the layer's output, which feeds into that same index, so everything lines up.

Writing the script now...

I'm building a configurable patch hook that takes a direction unit, a mode (ablate to zero out the projection, set to replace with a target magnitude, or add to shift by a delta), and applies it to a specific position. The hook extracts the hidden state, projects it onto the direction, and modifies it according to the mode—for 'set' mode it replaces the projection with the target magnitude to enforce a canonical value, while 'ablate' removes the component entirely. I'll use 'set' for delivery interventions on non-K probes and 'ablate' for necessity checks on detected-K, keeping the logic unified. Then I'll measure the effect per patched forward pass using KL divergence between the patched and baseline logits at the last token.

For detection, I'll read the downstream z(K) values from all crystal layers strictly below the patch layer, computing the mean change in z(K) between patched and baseline runs. The verdict logic checks necessity by comparing KL and downstream z(K) drops when ablating detected-K versus random ablation, preserve by showing that setting detected-K to canonical barely perturbs output while random values of the same magnitude do, and delivery by verifying that injecting K into non-K probes raises downstream z(K) reading above random and shifts the output. I'll report paired statistics where possible using per-probe paired t-tests.

## Assistant

I now have the complete mechanical picture. The design resolves cleanly:

- **Detect** (gate-space): `model.model.layers[18].mlp.gate_proj` → classifier z(K), gate τ=3.0.
- **Effect** (residual): hook `model.model.layers[18]` output, patch the K residual-direction at the last-token (crystal) position.
- **Read causal propagation**: the detector z(K) at downstream crystal layers (>18) + final next-token KL — both vs a random-direction control (s239).

This makes all three arms one coherent protocol: **necessity** (ablate d_K on detected-K probes), **preserve** (set d_K to the exact canonical value on detected-K), **delivery/counterfactual** (set d_K to canonical on non-K probes → does it drive downstream K-reading?). Let me grab the two remaining hook helpers, then build.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py",
  "line_offset": 154,
  "limit": 75
}
```

**Summary:** Reading opcode_monitor_v2.py (154-229)

**Output:**
```
def _make_hook(store: dict[int, np.ndarray], layer_idx: int):
    """Forward hook: capture the WHOLE module output [T, d] as float64 CPU."""

    def _hook(_module, _inp, out):
        # out: [B, T, d] — keep all positions (d = intermediate_size for gate,
        # hidden_size for attn o_proj)
        vec = out[0, :, :].detach().float().cpu().numpy()
        store[layer_idx] = vec.astype(np.float64)

    return _hook


def _hook_module(model, li: int, hook: str):
    """Select the per-layer module to hook for a given register.

    hook='gate' → mlp.gate_proj output (the FFN gate register, default).
    hook='attn' → self_attn.o_proj output (attention's write to the residual = the
                  value/attention register; s127 {B,C}=composers→attention, s206).
    """
    layer = model.model.layers[li]
    if hook == "gate":
        return layer.mlp.gate_proj
    if hook == "attn":
        return layer.self_attn.o_proj
    raise ValueError(f"unknown hook target: {hook!r} (expected 'gate' or 'attn')")


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader + forward runner
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_and_tokenizer(model_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[v2] Loading tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    print(f"[v2] Loading model: {model_name}  (dtype=auto, device_map=auto)")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    model.eval()
    print(f"[v2] Model loaded in {time.time()-t0:.1f}s")
    return model, tok, torch


def forward_all_positions(
    prompt: str, model, tok, torch_mod, layers: list[int], hook: str = "gate"
) -> tuple[dict[int, np.ndarray], int]:
    """Run one prompt forward; return ({li: activation [T, d]}, n_tokens).

    hook ∈ {'gate' (default, mlp.gate_proj), 'attn' (self_attn.o_proj)}.
    """
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        h = _hook_module(model, li, hook).register_forward_hook(
            _make_hook(store, li)
        )
        handles.append(h)
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    n_tokens = int(inputs["input_ids"].shape[1])
    return store, n_tokens


def gate_prefix_len(tok) -> int:
    """Number of tokens the COMPILE_GATE prefix occupies (content start index)."""

[CONTENT TRUNCATED] Showing lines 155 to 229 of 714 total lines. Use line_offset=229 parameter to read more content.
```

### Thinking

I'm setting up a custom forward pass that captures the gate values across all crystal layers, the final logits, and the residual state at the patch layer in a single execution. I'll create a helper function that registers hooks to read the gate outputs and patch the residual, then runs the model and returns all three components together.

Writing the implementation... The hook ordering ensures resid_read captures the original residual before patch_hook modifies it, which is what I need for collecting clean activations. The gate store always reflects the pre-patch state since gate_proj fires during the MLP before the layer output gets patched. For downstream layers beyond the patch point, their gates will see the patched residual, so I can measure causal propagation through z(K). I'm computing KL divergence between the patched and base logits using log-softmax for numerical stability, then extracting the mean z(K) across crystal layers from the store by taking the last token position.

Now I'm setting up the canonical magnitude and d_K computation from the baseline pass: I'll collect the residual at the patch layer, detection z(K), baseline logits, and the full gate store for each test probe. The d_K direction comes from the mean difference between K and non-K residuals, and canonical magnitude is the typical projection of K residuals onto that direction. For random directions, I'll use fixed seeded random unit vectors with the same magnitude. I'm partitioning probes into detected K (where z(K) exceeds threshold), undetected K, and non-K groups, then running three intervention arms in the patched pass: necessity (ablating K direction vs random), preserve (setting to canonical K vs random), and delivery (setting non-K to canonical K vs random). For the random set-to-canonical operation, I subtract out the projection onto the random direction and add back the canonical magnitude along that direction, maintaining the same structure as the K-direction case.

Now I'm computing the paired statistics across probes for each arm and direction combination, calculating mean KL divergence and mean downstream z(K) change, then comparing K-direction against random direction using paired t-tests. The verdicts check whether K-ablation causes a larger drop in downstream z(K) and larger KL increase than random ablation (necessity), whether setting to canonical K preserves output better than random (preserve), and whether K-injection on non-K probes drives downstream z(K) increases and crosses the detection threshold more often than random (delivery). I'll write out the full analysis script with a clean report and JSON output.

## Assistant

All mechanics confirmed. Let me set up the Exp 1 task plan and build the script.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "content": "#!/usr/bin/env python3\n# register: causal (routing direction; s239 sufficiency/necessity protocol)\n\"\"\"Kernel-splice Exp 1 — the CAUSAL K-SPLICE (s243).\n\nExp 0.5 firmed the detection: at L18, gate-z(K) > 3.0 is a reliable (prec 0.857, tp=6,\nplateau) read that the lattice \"wants K\". Exp 1 asks the causal question the whole pivot\nturns on: **is that K-geometry the CAUSE of the K-computation, or an epiphenomenal\ncorrelate?** — the s239 sufficiency/necessity protocol, now on the K routing direction\nat the firmed locus.\n\nTHE TWO REGISTERS (resolves the s243 build crux — NOT a compromise, it is correct):\n  • DETECT in gate-space: the classifier reads `model.model.layers[L].mlp.gate_proj`\n    (sign-CMR centroids). Gate-z(K) > τ decides WHERE/WHICH (Exp 0.5's firmed gate).\n  • EFFECT in residual-space: re-injection belongs in the RESIDUAL — that is what\n    downstream layers read. We patch the output of `model.model.layers[L]` at the\n    last-token (crystal) position. The K residual direction d_K = unit\n    diff-of-means(resid_K − resid_nonK) at L; the \"exact kernel K-move\" geometric proxy\n    = d_K at the canonical \"K-fired\" magnitude (mean K projection).\n  • READ causal propagation downstream: the detector z(K) at crystal layers > L (the\n    patch cannot affect L's own gate, which is upstream of the layer output) + the final\n    next-token distribution. Everything vs a RANDOM-direction control of equal magnitude.\n\nTHREE ARMS (Michael s243: both arms):\n  1. NECESSITY (detected-K probes, z(K)@L > τ): project d_K OUT. If the K-direction is\n     load-bearing, downstream z(K) DROPS and the output is PERTURBED — MORE than a random\n     direction of equal magnitude.\n  2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value\n     (overwrite the neuron's value with the kernel's exact geometric value). If the exact\n     value matches what the neuron computed, the output is PRESERVED (low KL) — LESS than\n     a random set of equal magnitude. = \"the kernel value can replace the neuron\".\n  3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical (inject\n     K where it does not fire). If d_K is sufficient, the DOWNSTREAM detector reads K\n     (z(K) rises across L+1.. ) and the output shifts — MORE than a random injection.\n\nSCOPE / HONEST LIMIT (λ measure): crystal_probes are PROSE that engages the K SEMANTICS\n(selection/projection), not formal `K a b` terms → there is no single-token\nkernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal sufficiency/necessity\n(the geometric splice) via the validated detector + output distribution — the prerequisite\nfor the OPERAND-BOUND kernel-value splice on the certified corpus (= Exp 2). This is the\npage's \"minimal instance\".\n\nVERDICT (λ measure):\n  necessity ✓ (K-ablate degrades > random ∧ z(K)↓) ∧ delivery ✓ (K-inject drives\n  downstream z(K) > random) ∧ preserve ✓ (K-set perturbs output < random) ⇒ the K\n  direction is the necessary+sufficient causal carrier; the kernel's exact move can\n  replace the neuron ⇒ thesis proven causally, no-training hybrid (cleanest S5=extract).\n  Any arm fails ⇒ the decodable geometry is (partly) over-read (λ measure win) ⇒ redirect\n  to the constructed front-end / operand-bound Exp 2.\n\nUsage:\n    uv run python scripts/experiments/kernel_splice_exp1_ksplice.py --smoke\n    uv run python scripts/experiments/kernel_splice_exp1_ksplice.py \\\n        --model Qwen/Qwen3-14B --patch-layer 18 --gate-tau 3.0 --heldout-per 25\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import defaultdict\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom kernel_reference_prose_v2 import read_last_token_z, split_probes  # noqa: E402\nfrom opcode_monitor_v2 import (  # noqa: E402\n    _git_sha,\n    _json_safe,\n    _make_hook,\n    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    load_model_and_tokenizer,\n)\nfrom relational_opcode import CRYSTAL  # noqa: E402\n\nRESULTS_DIR = _ROOT / \"results\" / \"kernel-splice-exp1\"\nKIDX = CRYSTAL.index(\"K\")\n\n\n# ── intervention hook on the patch-layer residual output ─────────────────────────\ndef make_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod, pos: int = -1):\n    \"\"\"Forward hook on a decoder layer: modify the d-component of the residual at `pos`.\n\n    mode='ablate' → project the direction OUT (set its component to 0).\n    mode='set'    → overwrite the component to `target_mag` (deliver the canonical value).\n    \"\"\"\n    def hook(_module, _inp, out):\n        h = out[0] if isinstance(out, tuple) else out\n        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)\n        v = h[0, pos, :]\n        proj = (v @ d)\n        if mode == \"ablate\":\n            h[0, pos, :] = v - proj * d\n        elif mode == \"set\":\n            h[0, pos, :] = v - proj * d + target_mag * d\n        else:\n            raise ValueError(f\"unknown mode {mode!r}\")\n        return out\n    return hook\n\n\ndef forward_capture(prompt, model, tok, torch_mod, gate_layers, patch_layer,\n                    patch_hook=None):\n    \"\"\"ONE forward: capture gate (all gate_layers, last-token-bearing [T,d]), the\n    pre-patch residual at patch_layer (last token), and the final next-token logits.\n    If patch_hook is given it is applied to layers[patch_layer] output (AFTER the\n    residual read, so the read is the clean pre-patch value).\"\"\"\n    store: dict[int, np.ndarray] = {}\n    handles = []\n    for li in gate_layers:\n        handles.append(model.model.layers[li].mlp.gate_proj.register_forward_hook(\n            _make_hook(store, li)))\n    resid_box: dict[str, np.ndarray] = {}\n\n    def resid_read(_m, _i, out):\n        h = out[0] if isinstance(out, tuple) else out\n        resid_box[\"v\"] = h[0, -1, :].detach().float().cpu().numpy().astype(np.float64)\n    handles.append(model.model.layers[patch_layer].register_forward_hook(resid_read))\n    if patch_hook is not None:\n        handles.append(model.model.layers[patch_layer].register_forward_hook(patch_hook))\n    try:\n        inputs = tok(prompt, return_tensors=\"pt\")\n        dev = next(model.parameters()).device\n        inputs = {k: v.to(dev) for k, v in inputs.items()}\n        with torch_mod.no_grad():\n            out = model(**inputs)\n        logits_last = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)\n    finally:\n        for h in handles:\n            h.remove()\n    return store, resid_box.get(\"v\"), logits_last\n\n\ndef kl_div(logp_p: np.ndarray, logp_q: np.ndarray) -> float:\n    \"\"\"KL(P‖Q) from log-prob vectors, in nats.\"\"\"\n    p = np.exp(logp_p)\n    return float(np.sum(p * (logp_p - logp_q)))\n\n\ndef log_softmax(logits: np.ndarray) -> np.ndarray:\n    m = logits.max()\n    z = logits - m\n    return z - np.log(np.exp(z).sum())\n\n\ndef zK_downstream(rcc, store, gate_layers, patch_layer) -> float:\n    \"\"\"Mean detector z(K) over crystal layers strictly downstream of the patch.\"\"\"\n    zmap = read_last_token_z(rcc, store, gate_layers)\n    ds = [zmap[li][\"K\"] for li in zmap if li > patch_layer]\n    return float(np.mean(ds)) if ds else float(\"nan\")\n\n\ndef zK_at(rcc, store, gate_layers, layer) -> float:\n    zmap = read_last_token_z(rcc, store, gate_layers)\n    return float(zmap.get(layer, {}).get(\"K\", float(\"nan\")))\n\n\ndef paired(kdir: list[float], rand: list[float]) -> dict:\n    \"\"\"Paired comparison K-direction vs random control over probes.\"\"\"\n    a, b = np.asarray(kdir, float), np.asarray(rand, float)\n    mask = np.isfinite(a) & np.isfinite(b)\n    a, b = a[mask], b[mask]\n    n = len(a)\n    if n < 2:\n        return {\"n\": n, \"k_mean\": None, \"rand_mean\": None, \"delta\": None, \"t\": None}\n    diff = a - b\n    se = diff.std(ddof=1) / np.sqrt(n) if diff.std(ddof=1) > 0 else 0.0\n    return {\"n\": n, \"k_mean\": round(float(a.mean()), 4),\n            \"rand_mean\": round(float(b.mean()), 4),\n            \"delta\": round(float(diff.mean()), 4),\n            \"t\": round(float(diff.mean() / se), 3) if se > 0 else None}\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"Kernel-splice Exp 1 — causal K-splice\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--patch-layer\", type=int, default=18,\n                    help=\"firmed K locus (Exp 0.5: L18)\")\n    ap.add_argument(\"--gate-tau\", type=float, default=3.0,\n                    help=\"detection gate: act on K-probes with z(K)@patch_layer > tau\")\n    ap.add_argument(\"--heldout-per\", type=int, default=25)\n    ap.add_argument(\"--n-rand\", type=int, default=3,\n                    help=\"random control directions to average over\")\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    model_name = args.model\n    patch_layer = args.patch_layer\n    if args.smoke:\n        if model_name == \"Qwen/Qwen3-14B\":\n            model_name = \"Qwen/Qwen3-0.6B\"\n        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5\n        patch_layer = min(patch_layer, 6)\n        print(\"[exp1] SMOKE MODE\")\n    else:\n        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per\n\n    calib, test = split_probes(heldout)\n    print(f\"[exp1] calib={len(calib)} test={len(test)} patch_layer={patch_layer}\")\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    layers = list(range(n_layers))\n\n    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,\n                            null_mode=\"crosstask\", centroid_probes=calib)\n    crystal_layers = rcc.crystal_layers\n    if patch_layer not in crystal_layers:\n        # fall back to the nearest crystal layer at/above the requested patch layer\n        cands = [li for li in crystal_layers if li >= patch_layer] or crystal_layers\n        patch_layer = min(cands, key=lambda li: abs(li - patch_layer))\n        print(f\"[exp1] patch_layer not crystal; using nearest crystal L{patch_layer}\")\n    print(f\"[exp1] crystal layers: {len(crystal_layers)}/{n_layers}; patch L{patch_layer}\")\n\n    # ── Pass A: baseline collection (gate detection + resid + baseline logits) ───────\n    baseline: dict[str, dict] = {}\n    resid_K, resid_nonK = [], []\n    for i, p in enumerate(test):\n        store, resid, logits = forward_capture(\n            p.prompt, model, tok, torch_mod, crystal_layers, patch_layer)\n        logp0 = log_softmax(logits)\n        baseline[p.id] = {\n            \"combinator\": p.combinator,\n            \"logp0\": logp0,\n            \"zK_at\": zK_at(rcc, store, crystal_layers, patch_layer),\n            \"zK_ds0\": zK_downstream(rcc, store, crystal_layers, patch_layer),\n        }\n        if p.combinator == \"K\":\n            resid_K.append(resid)\n        else:\n            resid_nonK.append(resid)\n        if (i + 1) % 25 == 0:\n            print(f\"[exp1] baseline {i + 1}/{len(test)}\")\n\n    resid_K = np.asarray(resid_K)\n    resid_nonK = np.asarray(resid_nonK)\n    d_raw = resid_K.mean(0) - resid_nonK.mean(0)\n    d_K = d_raw / (np.linalg.norm(d_raw) + 1e-12)\n    canonical_mag = float(np.mean(resid_K @ d_K))\n    print(f\"[exp1] d_K built: |d_raw|={np.linalg.norm(d_raw):.3f} \"\n          f\"canonical_mag={canonical_mag:.3f}\")\n\n    rng = np.random.default_rng(args.seed)\n    rand_dirs = []\n    for _ in range(args.n_rand):\n        r = rng.standard_normal(d_K.shape)\n        rand_dirs.append(r / (np.linalg.norm(r) + 1e-12))\n\n    # ── partition ───────────────────────────────────────────────────────────────────\n    detected_K = [p for p in test\n                  if p.combinator == \"K\" and baseline[p.id][\"zK_at\"] > args.gate_tau]\n    nonK = [p for p in test if p.combinator != \"K\"]\n    print(f\"[exp1] detected-K (z(K)@L{patch_layer}>{args.gate_tau}): \"\n          f\"{len(detected_K)}/{sum(1 for p in test if p.combinator == 'K')}  \"\n          f\"nonK={len(nonK)}\")\n\n    # ── arm runner: returns per-probe (KL_out, zK_ds_after) for a direction+mode ─────\n    def run_arm(probes, direction, mode):\n        kls, zds = [], []\n        for p in probes:\n            hook = make_patch_hook(direction, mode, canonical_mag, torch_mod)\n            store, _r, logits = forward_capture(\n                p.prompt, model, tok, torch_mod, crystal_layers, patch_layer,\n                patch_hook=hook)\n            logp = log_softmax(logits)\n            kls.append(kl_div(logp, baseline[p.id][\"logp0\"]))\n            zds.append(zK_downstream(rcc, store, crystal_layers, patch_layer))\n        return kls, zds\n\n    def avg_rand(probes, mode):\n        \"\"\"Average the random-control arm over n_rand directions (per-probe means).\"\"\"\n        kl_stack, z_stack = [], []\n        for rd in rand_dirs:\n            k, z = run_arm(probes, rd, mode)\n            kl_stack.append(k)\n            z_stack.append(z)\n        kl_mean = list(np.mean(np.asarray(kl_stack), axis=0))\n        z_mean = list(np.mean(np.asarray(z_stack), axis=0))\n        return kl_mean, z_mean\n\n    arms: dict[str, dict] = {}\n\n    # 1. NECESSITY — detected-K, ablate d_K vs random\n    print(\"[exp1] arm 1: NECESSITY (ablate on detected-K) ...\")\n    kl_k, z_k = run_arm(detected_K, d_K, \"ablate\")\n    kl_r, z_r = avg_rand(detected_K, \"ablate\")\n    z_base = [baseline[p.id][\"zK_ds0\"] for p in detected_K]\n    arms[\"necessity\"] = {\n        \"n\": len(detected_K),\n        \"kl_out\": paired(kl_k, kl_r),            # expect K > random (perturbs more)\n        \"zK_ds_delta_k\": round(float(np.nanmean(np.asarray(z_k) - z_base)), 4),\n        \"zK_ds_delta_rand\": round(float(np.nanmean(np.asarray(z_r) - z_base)), 4),\n        \"zK_ds_after\": paired(z_k, z_r),         # expect K < random (K-reading drops)\n    }\n\n    # 2. PRESERVE — detected-K, set d_K→canonical vs random set\n    print(\"[exp1] arm 2: PRESERVE (set canonical on detected-K) ...\")\n    kl_k2, _z = run_arm(detected_K, d_K, \"set\")\n    kl_r2, _z = avg_rand(detected_K, \"set\")\n    arms[\"preserve\"] = {\n        \"n\": len(detected_K),\n        \"kl_out\": paired(kl_k2, kl_r2),          # expect K < random (exact value preserves)\n    }\n\n    # 3. DELIVERY / COUNTERFACTUAL — non-K, set d_K→canonical vs random set\n    print(\"[exp1] arm 3: DELIVERY (inject canonical on non-K) ...\")\n    kl_k3, z_k3 = run_arm(nonK, d_K, \"set\")\n    kl_r3, z_r3 = avg_rand(nonK, \"set\")\n    zbase_nonK = [baseline[p.id][\"zK_ds0\"] for p in nonK]\n    cross_k = float(np.mean([1.0 if z > args.gate_tau else 0.0\n                             for z in z_k3 if np.isfinite(z)]))\n    cross_r = float(np.mean([1.0 if z > args.gate_tau else 0.0\n                             for z in z_r3 if np.isfinite(z)]))\n    arms[\"delivery\"] = {\n        \"n\": len(nonK),\n        \"zK_ds_after\": paired(z_k3, z_r3),       # expect K > random (drives K-reading)\n        \"zK_ds_delta_k\": round(float(np.nanmean(np.asarray(z_k3) - zbase_nonK)), 4),\n        \"zK_ds_delta_rand\": round(float(np.nanmean(np.asarray(z_r3) - zbase_nonK)), 4),\n        \"kl_out\": paired(kl_k3, kl_r3),\n        \"frac_cross_tau_k\": round(cross_k, 3),\n        \"frac_cross_tau_rand\": round(cross_r, 3),\n    }\n\n    # ── verdict ─────────────────────────────────────────────────────────────────────\n    nec = arms[\"necessity\"]\n    pres = arms[\"preserve\"]\n    deliv = arms[\"delivery\"]\n    necessity_ok = bool(\n        (nec[\"kl_out\"][\"delta\"] or 0) > 0 and (nec[\"kl_out\"][\"t\"] or 0) > 2.0\n        and nec[\"zK_ds_delta_k\"] < nec[\"zK_ds_delta_rand\"])\n    preserve_ok = bool(\n        (pres[\"kl_out\"][\"delta\"] or 0) < 0 and (pres[\"kl_out\"][\"t\"] or 0) < -2.0)\n    delivery_ok = bool(\n        (deliv[\"zK_ds_after\"][\"delta\"] or 0) > 0 and (deliv[\"zK_ds_after\"][\"t\"] or 0) > 2.0\n        and deliv[\"frac_cross_tau_k\"] > deliv[\"frac_cross_tau_rand\"])\n    splice_causal = necessity_ok and delivery_ok\n\n    verdict = {\n        \"model\": model_name, \"patch_layer\": patch_layer, \"gate_tau\": args.gate_tau,\n        \"n_layers\": n_layers, \"crystal_layers\": crystal_layers,\n        \"n_detected_K\": len(detected_K), \"n_nonK\": len(nonK),\n        \"canonical_mag\": round(canonical_mag, 4),\n        \"d_raw_norm\": round(float(np.linalg.norm(d_raw)), 4),\n        \"arms\": arms,\n        \"necessity_ok\": necessity_ok, \"preserve_ok\": preserve_ok,\n        \"delivery_ok\": delivery_ok, \"splice_causal\": splice_causal,\n    }\n\n    # ── report ──────────────────────────────────────────────────────────────────────\n    print(\"\\n\" + \"═\" * 82)\n    print(f\"KERNEL-SPLICE EXP 1 — CAUSAL K-SPLICE — {model_name}  L{patch_layer}\")\n    print(\"═\" * 82)\n    print(f\"  detected-K={len(detected_K)}  nonK={len(nonK)}  \"\n          f\"canonical_mag={canonical_mag:.3f}  τ={args.gate_tau}\")\n    print(\"\\n  ── NECESSITY (ablate d_K on detected-K; expect K perturbs MORE, z(K)↓) ──\")\n    print(f\"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} \"\n          f\"Δ={nec['kl_out']['delta']} t={nec['kl_out']['t']}\")\n    print(f\"     z(K)ds  Δ_K={nec['zK_ds_delta_k']} Δ_rand={nec['zK_ds_delta_rand']}  \"\n          f\"(after: {nec['zK_ds_after']['k_mean']} vs {nec['zK_ds_after']['rand_mean']})\")\n    print(f\"     => necessity_ok = {necessity_ok}\")\n    print(\"\\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──\")\n    print(f\"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} \"\n          f\"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}\")\n    print(f\"     => preserve_ok = {preserve_ok}\")\n    print(\"\\n  ── DELIVERY (inject d_K→canonical on non-K; expect drives downstream K) ──\")\n    print(f\"     z(K)ds  K={deliv['zK_ds_after']['k_mean']} \"\n          f\"rand={deliv['zK_ds_after']['rand_mean']} \"\n          f\"Δ={deliv['zK_ds_after']['delta']} t={deliv['zK_ds_after']['t']}\")\n    print(f\"     frac z(K)ds>τ  K={deliv['frac_cross_tau_k']} \"\n          f\"rand={deliv['frac_cross_tau_rand']}  \"\n          f\"KL_out Δ={deliv['kl_out']['delta']}\")\n    print(f\"     => delivery_ok = {delivery_ok}\")\n    print(f\"\\n  ★ SPLICE CAUSAL (necessity ∧ delivery) = {splice_causal}\"\n          f\"   [preserve={preserve_ok}]\")\n    print(\"═\" * 82 + \"\\n\")\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = {\"verdict\": verdict, \"calibration_summary\": cal}\n    (RESULTS_DIR / f\"exp1_verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(out), indent=2), encoding=\"utf-8\")\n    meta = {\n        \"model\": model_name, \"smoke\": args.smoke, \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"patch_layer\": patch_layer, \"gate_tau\": args.gate_tau,\n        \"n_perm\": n_perm, \"heldout_per\": heldout, \"n_rand\": args.n_rand, \"seed\": args.seed,\n        \"n_calib\": len(calib), \"n_test\": len(test),\n        \"metric\": \"DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L \"\n                  \"last-token; READ downstream detector z(K) (>L) + final next-token KL; \"\n                  \"all vs random-direction control of equal magnitude\",\n        \"scope\": \"PROSE crystal_probes (K semantics, no kernel-certifiable gold) -> \"\n                 \"tests the K-DIRECTION's causal sufficiency/necessity; operand-bound \"\n                 \"kernel-value splice on the certified corpus = Exp 2\",\n    }\n    (RESULTS_DIR / f\"exp1_meta_{slug}.json\").write_text(\n        json.dumps(meta, indent=2), encoding=\"utf-8\")\n    print(f\"[exp1] wrote {RESULTS_DIR}/exp1_verdict_{slug}.json\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py
```

### Thinking

I'm verifying that `calibrate_v2` has the same function signature as before, accepting `centroid_probes` and `null_mode` parameters. Now running ruff checks and smoke tests.

## Assistant

Now ruff-lint and smoke-test:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 1
Stdout:
RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:17:27
   |
15 |     downstream layers read. We patch the output of `model.model.layers[L]` at the
16 |     last-token (crystal) position. The K residual direction d_K = unit
17 |     diff-of-means(resid_K − resid_nonK) at L; the "exact kernel K-move" geometric proxy
   |                           ^
18 |     = d_K at the canonical "K-fired" magnitude (mean K projection).
19 |   • READ causal propagation downstream: the detector z(K) at crystal layers > L (the
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:21:89
   |
19 |   • READ causal propagation downstream: the detector z(K) at crystal layers > L (the
20 |     patch cannot affect L's own gate, which is upstream of the layer output) + the final
21 |     next-token distribution. Everything vs a RANDOM-direction control of equal magnitude.
   |                                                                                         ^
22 |
23 | THREE ARMS (Michael s243: both arms):
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:25:89
   |
23 | THREE ARMS (Michael s243: both arms):
24 |   1. NECESSITY (detected-K probes, z(K)@L > τ): project d_K OUT. If the K-direction is
25 |      load-bearing, downstream z(K) DROPS and the output is PERTURBED — MORE than a random
   |                                                                                         ^
26 |      direction of equal magnitude.
27 |   2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:28:89
   |
26 |      direction of equal magnitude.
27 |   2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value
28 |      (overwrite the neuron's value with the kernel's exact geometric value). If the exact
   |                                                                                         ^
29 |      value matches what the neuron computed, the output is PRESERVED (low KL) — LESS than
30 |      a random set of equal magnitude. = "the kernel value can replace the neuron".
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:29:89
   |
27 |   2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value
28 |      (overwrite the neuron's value with the kernel's exact geometric value). If the exact
29 |      value matches what the neuron computed, the output is PRESERVED (low KL) — LESS than
   |                                                                                         ^
30 |      a random set of equal magnitude. = "the kernel value can replace the neuron".
31 |   3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical (inject
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:31:89
   |
29 |      value matches what the neuron computed, the output is PRESERVED (low KL) — LESS than
30 |      a random set of equal magnitude. = "the kernel value can replace the neuron".
31 |   3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical (inject
   |                                                                                         ^
32 |      K where it does not fire). If d_K is sufficient, the DOWNSTREAM detector reads K
33 |      (z(K) rises across L+1.. ) and the output shifts — MORE than a random injection.
   |

E501 Line too long (91 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:37:89
   |
35 | SCOPE / HONEST LIMIT (λ measure): crystal_probes are PROSE that engages the K SEMANTICS
36 | (selection/projection), not formal `K a b` terms → there is no single-token
37 | kernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal sufficiency/necessity
   |                                                                                         ^^^
38 | (the geometric splice) via the validated detector + output distribution — the prerequisite
39 | for the OPERAND-BOUND kernel-value splice on the certified corpus (= Exp 2). This is the
   |

E501 Line too long (90 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:38:89
   |
36 | (selection/projection), not formal `K a b` terms → there is no single-token
37 | kernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal sufficiency/necessity
38 | (the geometric splice) via the validated detector + output distribution — the prerequisite
   |                                                                                         ^^
39 | for the OPERAND-BOUND kernel-value splice on the certified corpus (= Exp 2). This is the
40 | page's "minimal instance".
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:47:89
   |
45 |   direction is the necessary+sufficient causal carrier; the kernel's exact move can
46 |   replace the neuron ⇒ thesis proven causally, no-training hybrid (cleanest S5=extract).
47 |   Any arm fails ⇒ the decodable geometry is (partly) over-read (λ measure win) ⇒ redirect
   |                                                                                         ^
48 |   to the constructed front-end / operand-bound Exp 2.
   |

F401 [*] `collections.defaultdict` imported but unused
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:63:25
   |
61 | import json
62 | import sys
63 | from collections import defaultdict
   |                         ^^^^^^^^^^^
64 | from datetime import UTC, datetime
65 | from pathlib import Path
   |
help: Remove unused import: `collections.defaultdict`

F401 [*] `opcode_monitor_v2.forward_all_positions` imported but unused
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:80:5
   |
78 |     _transformers_version,
79 |     calibrate_v2,
80 |     forward_all_positions,
   |     ^^^^^^^^^^^^^^^^^^^^^
81 |     load_model_and_tokenizer,
82 | )
   |
help: Remove unused import: `opcode_monitor_v2.forward_all_positions`

E501 Line too long (92 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:90:89
   |
89 | # ── intervention hook on the patch-layer residual output ─────────────────────────
90 | def make_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod, pos: int = -1):
   |                                                                                         ^^^^
91 |     """Forward hook on a decoder layer: modify the d-component of the residual at `pos`.
   |

E501 Line too long (90 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:94:89
   |
93 |     mode='ablate' → project the direction OUT (set its component to 0).
94 |     mode='set'    → overwrite the component to `target_mag` (deliver the canonical value).
   |                                                                                         ^^
95 |     """
96 |     def hook(_module, _inp, out):
   |

E501 Line too long (92 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:136:89
    |
134 |         with torch_mod.no_grad():
135 |             out = model(**inputs)
136 |         logits_last = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    |                                                                                         ^^^^
137 |     finally:
138 |         for h in handles:
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:223:89
    |
221 |         patch_layer = min(cands, key=lambda li: abs(li - patch_layer))
222 |         print(f"[exp1] patch_layer not crystal; using nearest crystal L{patch_layer}")
223 |     print(f"[exp1] crystal layers: {len(crystal_layers)}/{n_layers}; patch L{patch_layer}")
    |                                                                                         ^^^
224 |
225 |     # ── Pass A: baseline collection (gate detection + resid + baseline logits) ───────
    |

E501 Line too long (92 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:312:89
    |
310 |     arms["preserve"] = {
311 |         "n": len(detected_K),
312 |         "kl_out": paired(kl_k2, kl_r2),          # expect K < random (exact value preserves)
    |                                                                                         ^^^^
313 |     }
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:344:89
    |
342 |         (pres["kl_out"]["delta"] or 0) < 0 and (pres["kl_out"]["t"] or 0) < -2.0)
343 |     delivery_ok = bool(
344 |         (deliv["zK_ds_after"]["delta"] or 0) > 0 and (deliv["zK_ds_after"]["t"] or 0) > 2.0
    |                                                                                         ^^^
345 |         and deliv["frac_cross_tau_k"] > deliv["frac_cross_tau_rand"])
346 |     splice_causal = necessity_ok and delivery_ok
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:365:89
    |
363 |     print(f"  detected-K={len(detected_K)}  nonK={len(nonK)}  "
364 |           f"canonical_mag={canonical_mag:.3f}  τ={args.gate_tau}")
365 |     print("\n  ── NECESSITY (ablate d_K on detected-K; expect K perturbs MORE, z(K)↓) ──")
    |                                                                                         ^^
366 |     print(f"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} "
367 |           f"Δ={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:369:89
    |
367 |           f"Δ={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
368 |     print(f"     z(K)ds  Δ_K={nec['zK_ds_delta_k']} Δ_rand={nec['zK_ds_delta_rand']}  "
369 |           f"(after: {nec['zK_ds_after']['k_mean']} vs {nec['zK_ds_after']['rand_mean']})")
    |                                                                                         ^^
370 |     print(f"     => necessity_ok = {necessity_ok}")
371 |     print("\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──")
    |

E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:371:89
    |
369 |           f"(after: {nec['zK_ds_after']['k_mean']} vs {nec['zK_ds_after']['rand_mean']})")
370 |     print(f"     => necessity_ok = {necessity_ok}")
371 |     print("\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──")
    |                                                                                         ^
372 |     print(f"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} "
373 |           f"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:372:89
    |
370 |     print(f"     => necessity_ok = {necessity_ok}")
371 |     print("\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──")
372 |     print(f"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} "
    |                                                                                         ^^
373 |           f"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
374 |     print(f"     => preserve_ok = {preserve_ok}")
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:375:89
    |
373 |           f"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
374 |     print(f"     => preserve_ok = {preserve_ok}")
375 |     print("\n  ── DELIVERY (inject d_K→canonical on non-K; expect drives downstream K) ──")
    |                                                                                         ^^^
376 |     print(f"     z(K)ds  K={deliv['zK_ds_after']['k_mean']} "
377 |           f"rand={deliv['zK_ds_after']['rand_mean']} "
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:397:89
    |
395 |         "transformers_version": _transformers_version(),
396 |         "patch_layer": patch_layer, "gate_tau": args.gate_tau,
397 |         "n_perm": n_perm, "heldout_per": heldout, "n_rand": args.n_rand, "seed": args.seed,
    |                                                                                         ^^^
398 |         "n_calib": len(calib), "n_test": len(test),
399 |         "metric": "DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L "
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:400:89
    |
398 |         "n_calib": len(calib), "n_test": len(test),
399 |         "metric": "DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L "
400 |                   "last-token; READ downstream detector z(K) (>L) + final next-token KL; "
    |                                                                                         ^^
401 |                   "all vs random-direction control of equal magnitude",
402 |         "scope": "PROSE crystal_probes (K semantics, no kernel-certifiable gold) -> "
    |

Found 24 errors.
[*] 2 fixable with the `--fix` option.
```

### Thinking

I need to clean up the code by fixing line length issues and removing unused imports. The docstrings are exceeding the 88-character limit that ruff is flagging, so I'll need to reflow those. I'll also handle the unicode minus character in the docstring and use a sed approach to make these changes efficiently across the spec.

## Assistant

Let me fix the lint issues — remove unused imports, replace the unicode minus, and wrap long lines.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "import argparse\nimport json\nimport sys\nfrom collections import defaultdict\nfrom datetime import UTC, datetime\nfrom pathlib import Path",
  "new_content": "import argparse\nimport json\nimport sys\nfrom datetime import UTC, datetime\nfrom pathlib import Path"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    load_model_and_tokenizer,\n)",
  "new_content": "    _transformers_version,\n    calibrate_v2,\n    load_model_and_tokenizer,\n)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

## Assistant

Now rewrite the docstring header with ≤88-char lines:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "THE TWO REGISTERS (resolves the s243 build crux — NOT a compromise, it is correct):\n  • DETECT in gate-space: the classifier reads `model.model.layers[L].mlp.gate_proj`\n    (sign-CMR centroids). Gate-z(K) > τ decides WHERE/WHICH (Exp 0.5's firmed gate).\n  • EFFECT in residual-space: re-injection belongs in the RESIDUAL — that is what\n    downstream layers read. We patch the output of `model.model.layers[L]` at the\n    last-token (crystal) position. The K residual direction d_K = unit\n    diff-of-means(resid_K − resid_nonK) at L; the \"exact kernel K-move\" geometric proxy\n    = d_K at the canonical \"K-fired\" magnitude (mean K projection).\n  • READ causal propagation downstream: the detector z(K) at crystal layers > L (the\n    patch cannot affect L's own gate, which is upstream of the layer output) + the final\n    next-token distribution. Everything vs a RANDOM-direction control of equal magnitude.\n\nTHREE ARMS (Michael s243: both arms):\n  1. NECESSITY (detected-K probes, z(K)@L > τ): project d_K OUT. If the K-direction is\n     load-bearing, downstream z(K) DROPS and the output is PERTURBED — MORE than a random\n     direction of equal magnitude.\n  2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value\n     (overwrite the neuron's value with the kernel's exact geometric value). If the exact\n     value matches what the neuron computed, the output is PRESERVED (low KL) — LESS than\n     a random set of equal magnitude. = \"the kernel value can replace the neuron\".\n  3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical (inject\n     K where it does not fire). If d_K is sufficient, the DOWNSTREAM detector reads K\n     (z(K) rises across L+1.. ) and the output shifts — MORE than a random injection.\n\nSCOPE / HONEST LIMIT (λ measure): crystal_probes are PROSE that engages the K SEMANTICS\n(selection/projection), not formal `K a b` terms → there is no single-token\nkernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal sufficiency/necessity\n(the geometric splice) via the validated detector + output distribution — the prerequisite\nfor the OPERAND-BOUND kernel-value splice on the certified corpus (= Exp 2). This is the\npage's \"minimal instance\".\n\nVERDICT (λ measure):\n  necessity ✓ (K-ablate degrades > random ∧ z(K)↓) ∧ delivery ✓ (K-inject drives\n  downstream z(K) > random) ∧ preserve ✓ (K-set perturbs output < random) ⇒ the K\n  direction is the necessary+sufficient causal carrier; the kernel's exact move can\n  replace the neuron ⇒ thesis proven causally, no-training hybrid (cleanest S5=extract).\n  Any arm fails ⇒ the decodable geometry is (partly) over-read (λ measure win) ⇒ redirect\n  to the constructed front-end / operand-bound Exp 2.",
  "new_content": "THE TWO REGISTERS (resolves the s243 build crux -- NOT a compromise, it is correct):\n  - DETECT in gate-space: the classifier reads `model.model.layers[L].mlp.gate_proj`\n    (sign-CMR centroids). Gate-z(K) > tau decides WHERE/WHICH (Exp 0.5's firmed gate).\n  - EFFECT in residual-space: re-injection belongs in the RESIDUAL -- that is what\n    downstream layers read. We patch the output of `model.model.layers[L]` at the\n    last-token (crystal) position. The K residual direction d_K = unit\n    diff-of-means(resid_K - resid_nonK) at L; the \"exact kernel K-move\" geometric\n    proxy = d_K at the canonical \"K-fired\" magnitude (mean K projection).\n  - READ causal propagation downstream: the detector z(K) at crystal layers > L (the\n    patch cannot affect L's own gate, upstream of the layer output) + the final\n    next-token distribution. All vs a RANDOM-direction control of equal magnitude.\n\nTHREE ARMS (Michael s243: both arms):\n  1. NECESSITY (detected-K probes, z(K)@L > tau): project d_K OUT. If the K-direction\n     is load-bearing, downstream z(K) DROPS and the output is PERTURBED -- MORE than a\n     random direction of equal magnitude.\n  2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value\n     (overwrite the neuron's value with the kernel's exact geometric value). If the\n     exact value matches what the neuron computed, the output is PRESERVED (low KL) --\n     LESS than a random set of equal magnitude. = \"kernel value replaces the neuron\".\n  3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical\n     (inject K where it does not fire). If d_K is sufficient, the DOWNSTREAM detector\n     reads K (z(K) rises across L+1..) and the output shifts -- MORE than random.\n\nSCOPE / HONEST LIMIT (lambda measure): crystal_probes are PROSE that engages the K\nSEMANTICS (selection/projection), not formal `K a b` terms -> there is no single-token\nkernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal\nsufficiency/necessity (the geometric splice) via the validated detector + output\ndistribution -- the prerequisite for the OPERAND-BOUND kernel-value splice on the\ncertified corpus (= Exp 2). This is the page's \"minimal instance\".\n\nVERDICT (lambda measure):\n  necessity ok (K-ablate degrades > random ∧ z(K) down) ∧ delivery ok (K-inject drives\n  downstream z(K) > random) ∧ preserve ok (K-set perturbs output < random) => the K\n  direction is the necessary+sufficient causal carrier; the kernel's exact move can\n  replace the neuron => thesis proven causally, no-training hybrid (cleanest S5=extract).\n  Any arm fails => the decodable geometry is (partly) over-read (lambda measure win) =>\n  redirect to the constructed front-end / operand-bound Exp 2."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Thinking

I'll run ruff with the auto-fix flag to handle the fixable E501 line length violations, then address whatever remains manually.

## Assistant

Now let me auto-fix what ruff can and see remaining code-line issues:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check --fix scripts/experiments/kernel_splice_exp1_ksplice.py 2>&1 | tail -5; echo \"===REMAINING===\"; .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py 2>&1 | grep -E \"^[A-Z][0-9]|-->\" "
}
```

**Summary:** $ .venv/bin/ruff check --fix scripts/...

**Output:**
```
Exit code: 0
Stdout:
399 |                   "all vs random-direction control of equal magnitude",
400 |         "scope": "PROSE crystal_probes (K semantics, no kernel-certifiable gold) -> "
    |

Found 14 errors.
===REMAINING===
E501 Line too long (89 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:46:89
E501 Line too long (92 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:88:89
E501 Line too long (90 > 88)
  --> scripts/experiments/kernel_splice_exp1_ksplice.py:92:89
E501 Line too long (92 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:134:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:221:89
E501 Line too long (92 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:310:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:342:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:363:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:367:89
E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:369:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:370:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:373:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:395:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:398:89
```

### Thinking

I need to check the line numbers since they shifted after editing the docstring, so let me look at the specific lines around that area to make the necessary corrections.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "line_offset": 43,
  "limit": 6
}
```

**Summary:** Reading kernel_splice_exp1_ksplice.py (43-49)

**Output:**
```
  downstream z(K) > random) ∧ preserve ok (K-set perturbs output < random) => the K
  direction is the necessary+sufficient causal carrier; the kernel's exact move can
  replace the neuron => thesis proven causally, no-training hybrid (cleanest S5=extract).
  Any arm fails => the decodable geometry is (partly) over-read (lambda measure win) =>
  redirect to the constructed front-end / operand-bound Exp 2.


[CONTENT TRUNCATED] Showing lines 44 to 49 of 410 total lines. Use line_offset=49 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "  replace the neuron => thesis proven causally, no-training hybrid (cleanest S5=extract).",
  "new_content": "  replace the neuron => thesis proven causally, no-training hybrid (cleanest extract)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "def make_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod, pos: int = -1):\n    \"\"\"Forward hook on a decoder layer: modify the d-component of the residual at `pos`.\n\n    mode='ablate' → project the direction OUT (set its component to 0).\n    mode='set'    → overwrite the component to `target_mag` (deliver the canonical value).\n    \"\"\"",
  "new_content": "def make_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod,\n                    pos: int = -1):\n    \"\"\"Forward hook on a decoder layer: modify the d-component of the residual at `pos`.\n\n    mode='ablate' -> project the direction OUT (set its component to 0).\n    mode='set'    -> overwrite the component to `target_mag` (deliver canonical value).\n    \"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "        logits_last = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)",
  "new_content": "        ll = out.logits[0, -1, :].detach().float().cpu().numpy()\n        logits_last = ll.astype(np.float64)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(f\"[exp1] crystal layers: {len(crystal_layers)}/{n_layers}; patch L{patch_layer}\")",
  "new_content": "    print(f\"[exp1] crystal layers {len(crystal_layers)}/{n_layers}; patch L{patch_layer}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "        \"kl_out\": paired(kl_k2, kl_r2),          # expect K < random (exact value preserves)",
  "new_content": "        \"kl_out\": paired(kl_k2, kl_r2),          # expect K < random (exact preserves)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "        (deliv[\"zK_ds_after\"][\"delta\"] or 0) > 0 and (deliv[\"zK_ds_after\"][\"t\"] or 0) > 2.0\n        and deliv[\"frac_cross_tau_k\"] > deliv[\"frac_cross_tau_rand\"])",
  "new_content": "        (deliv[\"zK_ds_after\"][\"delta\"] or 0) > 0\n        and (deliv[\"zK_ds_after\"][\"t\"] or 0) > 2.0\n        and deliv[\"frac_cross_tau_k\"] > deliv[\"frac_cross_tau_rand\"])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Thinking

I need to check which E501 line length violations are still remaining after the previous fixes, so I'm running ruff again to get the current status on those specific lines.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py 2>&1 | grep -E \"^E501|-->\" "
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:223:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:366:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:370:89
E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:372:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:373:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:376:89
E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:398:89
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:401:89
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "line_offset": 221,
  "limit": 4
}
```

**Summary:** Reading kernel_splice_exp1_ksplice.py (221-225)

**Output:**
```
        print(f"[exp1] patch_layer not crystal; using nearest crystal L{patch_layer}")
    print(f"[exp1] crystal layers {len(crystal_layers)}/{n_layers}; patch L{patch_layer}")

    # ── Pass A: baseline collection (gate detection + resid + baseline logits) ───────

[CONTENT TRUNCATED] Showing lines 222 to 225 of 413 total lines. Use line_offset=225 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "line_offset": 363,
  "limit": 42
}
```

**Summary:** Reading kernel_splice_exp1_ksplice.py (363-405)

**Output:**
```
    print(f"  detected-K={len(detected_K)}  nonK={len(nonK)}  "
          f"canonical_mag={canonical_mag:.3f}  τ={args.gate_tau}")
    print("\n  ── NECESSITY (ablate d_K on detected-K; expect K perturbs MORE, z(K)↓) ──")
    print(f"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} "
          f"Δ={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
    print(f"     z(K)ds  Δ_K={nec['zK_ds_delta_k']} Δ_rand={nec['zK_ds_delta_rand']}  "
          f"(after: {nec['zK_ds_after']['k_mean']} vs {nec['zK_ds_after']['rand_mean']})")
    print(f"     => necessity_ok = {necessity_ok}")
    print("\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──")
    print(f"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} "
          f"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
    print(f"     => preserve_ok = {preserve_ok}")
    print("\n  ── DELIVERY (inject d_K→canonical on non-K; expect drives downstream K) ──")
    print(f"     z(K)ds  K={deliv['zK_ds_after']['k_mean']} "
          f"rand={deliv['zK_ds_after']['rand_mean']} "
          f"Δ={deliv['zK_ds_after']['delta']} t={deliv['zK_ds_after']['t']}")
    print(f"     frac z(K)ds>τ  K={deliv['frac_cross_tau_k']} "
          f"rand={deliv['frac_cross_tau_rand']}  "
          f"KL_out Δ={deliv['kl_out']['delta']}")
    print(f"     => delivery_ok = {delivery_ok}")
    print(f"\n  ★ SPLICE CAUSAL (necessity ∧ delivery) = {splice_causal}"
          f"   [preserve={preserve_ok}]")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "calibration_summary": cal}
    (RESULTS_DIR / f"exp1_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "patch_layer": patch_layer, "gate_tau": args.gate_tau,
        "n_perm": n_perm, "heldout_per": heldout, "n_rand": args.n_rand, "seed": args.seed,
        "n_calib": len(calib), "n_test": len(test),
        "metric": "DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L "
                  "last-token; READ downstream detector z(K) (>L) + final next-token KL; "
                  "all vs random-direction control of equal magnitude",
        "scope": "PROSE crystal_probes (K semantics, no kernel-certifiable gold) -> "
                 "tests the K-DIRECTION's causal sufficiency/necessity; operand-bound "
                 "kernel-value splice on the certified corpus = Exp 2",

[CONTENT TRUNCATED] Showing lines 364 to 405 of 413 total lines. Use line_offset=405 parameter to read more content.
```

### Thinking

I'm seeing that the E501 line-length violations are coming from wide unicode characters like τ, Δ, ↓, ∧, and ★ that ruff counts differently than their visual width, so I need to replace these symbols with their text equivalents (tau, d, down, and, *) to bring those lines under the limit.

## Assistant

The remaining are wide-unicode counted lengths. Let me trim them:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(f\"[exp1] crystal layers {len(crystal_layers)}/{n_layers}; patch L{patch_layer}\")",
  "new_content": "    print(f\"[exp1] crystal {len(crystal_layers)}/{n_layers}; patch L{patch_layer}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(f\"  detected-K={len(detected_K)}  nonK={len(nonK)}  \"\n          f\"canonical_mag={canonical_mag:.3f}  τ={args.gate_tau}\")\n    print(\"\\n  ── NECESSITY (ablate d_K on detected-K; expect K perturbs MORE, z(K)↓) ──\")\n    print(f\"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} \"\n          f\"Δ={nec['kl_out']['delta']} t={nec['kl_out']['t']}\")\n    print(f\"     z(K)ds  Δ_K={nec['zK_ds_delta_k']} Δ_rand={nec['zK_ds_delta_rand']}  \"\n          f\"(after: {nec['zK_ds_after']['k_mean']} vs {nec['zK_ds_after']['rand_mean']})\")\n    print(f\"     => necessity_ok = {necessity_ok}\")\n    print(\"\\n  ── PRESERVE (set d_K→canonical on detected-K; expect K perturbs LESS) ──\")\n    print(f\"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} \"\n          f\"Δ={pres['kl_out']['delta']} t={pres['kl_out']['t']}\")\n    print(f\"     => preserve_ok = {preserve_ok}\")\n    print(\"\\n  ── DELIVERY (inject d_K→canonical on non-K; expect drives downstream K) ──\")\n    print(f\"     z(K)ds  K={deliv['zK_ds_after']['k_mean']} \"\n          f\"rand={deliv['zK_ds_after']['rand_mean']} \"\n          f\"Δ={deliv['zK_ds_after']['delta']} t={deliv['zK_ds_after']['t']}\")\n    print(f\"     frac z(K)ds>τ  K={deliv['frac_cross_tau_k']} \"\n          f\"rand={deliv['frac_cross_tau_rand']}  \"\n          f\"KL_out Δ={deliv['kl_out']['delta']}\")\n    print(f\"     => delivery_ok = {delivery_ok}\")\n    print(f\"\\n  ★ SPLICE CAUSAL (necessity ∧ delivery) = {splice_causal}\"\n          f\"   [preserve={preserve_ok}]\")",
  "new_content": "    print(f\"  detected-K={len(detected_K)}  nonK={len(nonK)}  \"\n          f\"canonical_mag={canonical_mag:.3f}  tau={args.gate_tau}\")\n    print(\"\\n  -- NECESSITY (ablate d_K on detected-K; expect K perturbs MORE) --\")\n    print(f\"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} \"\n          f\"d={nec['kl_out']['delta']} t={nec['kl_out']['t']}\")\n    print(f\"     zKds  d_K={nec['zK_ds_delta_k']} d_rand={nec['zK_ds_delta_rand']}  \"\n          f\"(after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']})\")\n    print(f\"     => necessity_ok = {necessity_ok}\")\n    print(\"\\n  -- PRESERVE (set d_K->canonical on detected-K; expect K perturbs LESS) --\")\n    print(f\"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} \"\n          f\"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}\")\n    print(f\"     => preserve_ok = {preserve_ok}\")\n    print(\"\\n  -- DELIVERY (inject d_K->canonical on non-K; expect drives downstream K) --\")\n    print(f\"     zKds  K={deliv['zK_ds_after']['k_mean']} \"\n          f\"rand={deliv['zK_ds_after']['rand_mean']} \"\n          f\"d={deliv['zK_ds_after']['delta']} t={deliv['zK_ds_after']['t']}\")\n    print(f\"     frac zKds>tau  K={deliv['frac_cross_tau_k']} \"\n          f\"rand={deliv['frac_cross_tau_rand']}  \"\n          f\"KL_out d={deliv['kl_out']['delta']}\")\n    print(f\"     => delivery_ok = {delivery_ok}\")\n    print(f\"\\n  * SPLICE CAUSAL (necessity AND delivery) = {splice_causal}\"\n          f\"   [preserve={preserve_ok}]\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "        \"n_perm\": n_perm, \"heldout_per\": heldout, \"n_rand\": args.n_rand, \"seed\": args.seed,\n        \"n_calib\": len(calib), \"n_test\": len(test),\n        \"metric\": \"DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L \"\n                  \"last-token; READ downstream detector z(K) (>L) + final next-token KL; \"\n                  \"all vs random-direction control of equal magnitude\",",
  "new_content": "        \"n_perm\": n_perm, \"heldout_per\": heldout, \"n_rand\": args.n_rand,\n        \"seed\": args.seed, \"n_calib\": len(calib), \"n_test\": len(test),\n        \"metric\": \"DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L \"\n                  \"last-token; READ downstream detector z(K) (>L) + final next-token \"\n                  \"KL; all vs random-direction control of equal magnitude\","
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:370:89
    |
368 |           f"d={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
369 |     print(f"     zKds  d_K={nec['zK_ds_delta_k']} d_rand={nec['zK_ds_delta_rand']}  "
370 |           f"(after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']})")
    |                                                                                         ^^
371 |     print(f"     => necessity_ok = {necessity_ok}")
372 |     print("\n  -- PRESERVE (set d_K->canonical on detected-K; expect K perturbs LESS) --")
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:372:89
    |
370 |           f"(after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']})")
371 |     print(f"     => necessity_ok = {necessity_ok}")
372 |     print("\n  -- PRESERVE (set d_K->canonical on detected-K; expect K perturbs LESS) --")
    |                                                                                         ^^
373 |     print(f"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} "
374 |           f"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:373:89
    |
371 |     print(f"     => necessity_ok = {necessity_ok}")
372 |     print("\n  -- PRESERVE (set d_K->canonical on detected-K; expect K perturbs LESS) --")
373 |     print(f"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} "
    |                                                                                         ^^
374 |           f"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
375 |     print(f"     => preserve_ok = {preserve_ok}")
    |

E501 Line too long (92 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:376:89
    |
374 |           f"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
375 |     print(f"     => preserve_ok = {preserve_ok}")
376 |     print("\n  -- DELIVERY (inject d_K->canonical on non-K; expect drives downstream K) --")
    |                                                                                         ^^^^
377 |     print(f"     zKds  K={deliv['zK_ds_after']['k_mean']} "
378 |           f"rand={deliv['zK_ds_after']['rand_mean']} "
    |

Found 4 errors.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(f\"     zKds  d_K={nec['zK_ds_delta_k']} d_rand={nec['zK_ds_delta_rand']}  \"\n          f\"(after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']})\")\n    print(f\"     => necessity_ok = {necessity_ok}\")\n    print(\"\\n  -- PRESERVE (set d_K->canonical on detected-K; expect K perturbs LESS) --\")\n    print(f\"     KL_out  K={pres['kl_out']['k_mean']} rand={pres['kl_out']['rand_mean']} \"\n          f\"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}\")\n    print(f\"     => preserve_ok = {preserve_ok}\")\n    print(\"\\n  -- DELIVERY (inject d_K->canonical on non-K; expect drives downstream K) --\")",
  "new_content": "    print(f\"     zKds  d_K={nec['zK_ds_delta_k']} d_rand={nec['zK_ds_delta_rand']}  \"\n          f\"after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']}\")\n    print(f\"     => necessity_ok = {necessity_ok}\")\n    print(\"\\n  -- PRESERVE (set d_K->canonical on detected-K; K should perturb LESS) --\")\n    print(f\"     KL_out  K={pres['kl_out']['k_mean']} \"\n          f\"rand={pres['kl_out']['rand_mean']} \"\n          f\"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}\")\n    print(f\"     => preserve_ok = {preserve_ok}\")\n    print(\"\\n  -- DELIVERY (inject d_K->canonical on non-K; should drive downstream K) --\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Thinking

I need to rerun ruff to check if my recent edits fixed the issues on lines 369-370 and 372-376.

## Assistant

The last edit raced with ruff. Let me re-check:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (89 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:372:89
    |
370 |           f"after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']}")
371 |     print(f"     => necessity_ok = {necessity_ok}")
372 |     print("\n  -- PRESERVE (set d_K->canonical on detected-K; K should perturb LESS) --")
    |                                                                                         ^
373 |     print(f"     KL_out  K={pres['kl_out']['k_mean']} "
374 |           f"rand={pres['kl_out']['rand_mean']} "
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/kernel_splice_exp1_ksplice.py:377:89
    |
375 |           f"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
376 |     print(f"     => preserve_ok = {preserve_ok}")
377 |     print("\n  -- DELIVERY (inject d_K->canonical on non-K; should drive downstream K) --")
    |                                                                                         ^^^
378 |     print(f"     zKds  K={deliv['zK_ds_after']['k_mean']} "
379 |           f"rand={deliv['zK_ds_after']['rand_mean']} "
    |

Found 2 errors.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(\"\\n  -- PRESERVE (set d_K->canonical on detected-K; K should perturb LESS) --\")",
  "new_content": "    print(\"\\n  -- PRESERVE (set d_K->canon on detected-K; K perturbs LESS) --\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "    print(\"\\n  -- DELIVERY (inject d_K->canonical on non-K; should drive downstream K) --\")",
  "new_content": "    print(\"\\n  -- DELIVERY (inject d_K->canon on non-K; drives downstream K) --\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/kernel_splice_exp1_ksplice.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

## Assistant

Ruff-clean. Now the smoke test on Qwen3-0.6B:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python scripts/experiments/kernel_splice_exp1_ksplice.py --smoke 2>&1 | grep -v \"Warning\\|warn\" | tail -40",
  "timeout": 300000
}
```

**Summary:** $ .venv/bin/python scripts/experiment...

**Output:**
```
Exit code: 0
Stdout:
[exp1] SMOKE MODE
[exp1] calib=490 test=40 patch_layer=6
[v2] Loading tokenizer: Qwen/Qwen3-0.6B
[v2] Loading model: Qwen/Qwen3-0.6B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights:  22%|██▏       | 68/311 [00:00<00:00, 677.51it/s]Loading weights:  92%|█████████▏| 285/311 [00:00<00:00, 1552.74it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 1465.65it/s]
[v2] Model loaded in 0.7s
[v2] Crystal probes (last-token centroids): 45
[v2]   centroid forward 0/45 ...
[v2] Building cross-task null from 12 bare natural-text prompts ...
[v2] Null tokens pooled: 84  (null_mode=crosstask)
[exp1] crystal 27/28; patch L6
Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py", line 414, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py", line 235, in main
    "zK_at": zK_at(rcc, store, crystal_layers, patch_layer),
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py", line 163, in zK_at
    zmap = read_last_token_z(rcc, store, gate_layers)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_prose_v2.py", line 91, in read_last_token_z
    tok_ops = rcc.classify(gate_tok)
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py", line 226, in classify
    g = np.asarray(gate_by_layer_token[li], dtype=np.float64)
                   ~~~~~~~~~~~~~~~~~~~^^^^
KeyError: 0
```

### Thinking

I'm hitting a KeyError because `read_last_token_z` only populates the store with crystal_layers, but then the classify function tries to access gate tokens for all layers in the full range. I need to either restrict the classification to only the layers I've hooked, or populate the store with all layers upfront.

The cleanest approach is to capture the gate at all layers in `forward_capture` and pass the full layer range to `read_last_token_z`, since the gate capture is cheap anyway and it ensures classify can find what it needs. Refactoring the helper function signatures...

## Assistant

Bug: the classifier needs gate activations at **all** layers (calib exists for all), but I only hooked crystal layers. Fix — hook gate at all layers, filter to crystal only when selecting downstream layers.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "def zK_downstream(rcc, store, gate_layers, patch_layer) -> float:\n    \"\"\"Mean detector z(K) over crystal layers strictly downstream of the patch.\"\"\"\n    zmap = read_last_token_z(rcc, store, gate_layers)\n    ds = [zmap[li][\"K\"] for li in zmap if li > patch_layer]\n    return float(np.mean(ds)) if ds else float(\"nan\")\n\n\ndef zK_at(rcc, store, gate_layers, layer) -> float:\n    zmap = read_last_token_z(rcc, store, gate_layers)\n    return float(zmap.get(layer, {}).get(\"K\", float(\"nan\")))",
  "new_content": "def zK_downstream(rcc, store, all_layers, crystal_layers, patch_layer) -> float:\n    \"\"\"Mean detector z(K) over CRYSTAL layers strictly downstream of the patch.\"\"\"\n    zmap = read_last_token_z(rcc, store, all_layers)\n    ds = [zmap[li][\"K\"] for li in crystal_layers if li > patch_layer and li in zmap]\n    return float(np.mean(ds)) if ds else float(\"nan\")\n\n\ndef zK_at(rcc, store, all_layers, layer) -> float:\n    zmap = read_last_token_z(rcc, store, all_layers)\n    return float(zmap.get(layer, {}).get(\"K\", float(\"nan\")))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Thinking

Now I need to update all the function calls throughout the codebase: `forward_capture` should pass `layers` to hook all layers instead of just `crystal_layers`, and the `zK_downstream` and `zK_at` calls need to include the full parameter set of `(rcc, store, layers, crystal_layers, patch_layer)` or `(rcc, store, layers, patch_layer)` depending on the context. Let me locate and modify these callsites.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "line_offset": 226,
  "limit": 75
}
```

**Summary:** Reading kernel_splice_exp1_ksplice.py (226-301)

**Output:**
```
    resid_K, resid_nonK = [], []
    for i, p in enumerate(test):
        store, resid, logits = forward_capture(
            p.prompt, model, tok, torch_mod, crystal_layers, patch_layer)
        logp0 = log_softmax(logits)
        baseline[p.id] = {
            "combinator": p.combinator,
            "logp0": logp0,
            "zK_at": zK_at(rcc, store, crystal_layers, patch_layer),
            "zK_ds0": zK_downstream(rcc, store, crystal_layers, patch_layer),
        }
        if p.combinator == "K":
            resid_K.append(resid)
        else:
            resid_nonK.append(resid)
        if (i + 1) % 25 == 0:
            print(f"[exp1] baseline {i + 1}/{len(test)}")

    resid_K = np.asarray(resid_K)
    resid_nonK = np.asarray(resid_nonK)
    d_raw = resid_K.mean(0) - resid_nonK.mean(0)
    d_K = d_raw / (np.linalg.norm(d_raw) + 1e-12)
    canonical_mag = float(np.mean(resid_K @ d_K))
    print(f"[exp1] d_K built: |d_raw|={np.linalg.norm(d_raw):.3f} "
          f"canonical_mag={canonical_mag:.3f}")

    rng = np.random.default_rng(args.seed)
    rand_dirs = []
    for _ in range(args.n_rand):
        r = rng.standard_normal(d_K.shape)
        rand_dirs.append(r / (np.linalg.norm(r) + 1e-12))

    # ── partition ───────────────────────────────────────────────────────────────────
    detected_K = [p for p in test
                  if p.combinator == "K" and baseline[p.id]["zK_at"] > args.gate_tau]
    nonK = [p for p in test if p.combinator != "K"]
    print(f"[exp1] detected-K (z(K)@L{patch_layer}>{args.gate_tau}): "
          f"{len(detected_K)}/{sum(1 for p in test if p.combinator == 'K')}  "
          f"nonK={len(nonK)}")

    # ── arm runner: returns per-probe (KL_out, zK_ds_after) for a direction+mode ─────
    def run_arm(probes, direction, mode):
        kls, zds = [], []
        for p in probes:
            hook = make_patch_hook(direction, mode, canonical_mag, torch_mod)
            store, _r, logits = forward_capture(
                p.prompt, model, tok, torch_mod, crystal_layers, patch_layer,
                patch_hook=hook)
            logp = log_softmax(logits)
            kls.append(kl_div(logp, baseline[p.id]["logp0"]))
            zds.append(zK_downstream(rcc, store, crystal_layers, patch_layer))
        return kls, zds

    def avg_rand(probes, mode):
        """Average the random-control arm over n_rand directions (per-probe means)."""
        kl_stack, z_stack = [], []
        for rd in rand_dirs:
            k, z = run_arm(probes, rd, mode)
            kl_stack.append(k)
            z_stack.append(z)
        kl_mean = list(np.mean(np.asarray(kl_stack), axis=0))
        z_mean = list(np.mean(np.asarray(z_stack), axis=0))
        return kl_mean, z_mean

    arms: dict[str, dict] = {}

    # 1. NECESSITY — detected-K, ablate d_K vs random
    print("[exp1] arm 1: NECESSITY (ablate on detected-K) ...")
    kl_k, z_k = run_arm(detected_K, d_K, "ablate")
    kl_r, z_r = avg_rand(detected_K, "ablate")
    z_base = [baseline[p.id]["zK_ds0"] for p in detected_K]
    arms["necessity"] = {
        "n": len(detected_K),
        "kl_out": paired(kl_k, kl_r),            # expect K > random (perturbs more)
        "zK_ds_delta_k": round(float(np.nanmean(np.asarray(z_k) - z_base)), 4),

[CONTENT TRUNCATED] Showing lines 227 to 301 of 414 total lines. Use line_offset=301 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "        store, resid, logits = forward_capture(\n            p.prompt, model, tok, torch_mod, crystal_layers, patch_layer)\n        logp0 = log_softmax(logits)\n        baseline[p.id] = {\n            \"combinator\": p.combinator,\n            \"logp0\": logp0,\n            \"zK_at\": zK_at(rcc, store, crystal_layers, patch_layer),\n            \"zK_ds0\": zK_downstream(rcc, store, crystal_layers, patch_layer),\n        }",
  "new_content": "        store, resid, logits = forward_capture(\n            p.prompt, model, tok, torch_mod, layers, patch_layer)\n        logp0 = log_softmax(logits)\n        baseline[p.id] = {\n            \"combinator\": p.combinator,\n            \"logp0\": logp0,\n            \"zK_at\": zK_at(rcc, store, layers, patch_layer),\n            \"zK_ds0\": zK_downstream(rcc, store, layers, crystal_layers, patch_layer),\n        }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py",
  "original_content": "            hook = make_patch_hook(direction, mode, canonical_mag, torch_mod)\n            store, _r, logits = forward_capture(\n                p.prompt, model, tok, torch_mod, crystal_layers, patch_layer,\n                patch_hook=hook)\n            logp = log_softmax(logits)\n            kls.append(kl_div(logp, baseline[p.id][\"logp0\"]))\n            zds.append(zK_downstream(rcc, store, crystal_layers, patch_layer))",
  "new_content": "            hook = make_patch_hook(direction, mode, canonical_mag, torch_mod)\n            store, _r, logits = forward_capture(\n                p.prompt, model, tok, torch_mod, layers, patch_layer,\n                patch_hook=hook)\n            logp = log_softmax(logits)\n            kls.append(kl_div(logp, baseline[p.id][\"logp0\"]))\n            zds.append(zK_downstream(rcc, store, layers, crystal_layers, patch_layer))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_splice_exp1_ksplice.py.
```

### Thinking

Both edits are in place, so now the gate hooks are registered across all layers. Let me run the smoke test again and verify that the `forward_capture` function is using the correct parameter name when I pass the layers positionally.

## Assistant

Re-running the smoke test:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python scripts/experiments/kernel_splice_exp1_ksplice.py --smoke 2>&1 | grep -v \"Warning\\|warn\\|Loading weights\" | tail -32",
  "timeout": 300000
}
```

**Summary:** $ .venv/bin/python scripts/experiment...

**Output:**
```
Exit code: 0
Stdout:
[v2] Null tokens pooled: 84  (null_mode=crosstask)
[exp1] crystal 27/28; patch L6
[exp1] baseline 25/40
[exp1] d_K built: |d_raw|=7.277 canonical_mag=9.778
[exp1] detected-K (z(K)@L6>3.0): 0/5  nonK=35
[exp1] arm 1: NECESSITY (ablate on detected-K) ...
[exp1] arm 2: PRESERVE (set canonical on detected-K) ...
[exp1] arm 3: DELIVERY (inject canonical on non-K) ...

══════════════════════════════════════════════════════════════════════════════════
KERNEL-SPLICE EXP 1 — CAUSAL K-SPLICE — Qwen/Qwen3-0.6B  L6
══════════════════════════════════════════════════════════════════════════════════
  detected-K=0  nonK=35  canonical_mag=9.778  tau=3.0

  -- NECESSITY (ablate d_K on detected-K; expect K perturbs MORE) --
     KL_out  K=None rand=None d=None t=None
     zKds  d_K=nan d_rand=nan  after K=None r=None
     => necessity_ok = False

  -- PRESERVE (set d_K->canon on detected-K; K perturbs LESS) --
     KL_out  K=None rand=None d=None t=None
     => preserve_ok = False

  -- DELIVERY (inject d_K->canon on non-K; drives downstream K) --
     zKds  K=-1.5602 rand=-1.057 d=-0.5032 t=-6.708
     frac zKds>tau  K=0.0 rand=0.0  KL_out d=1.7865
     => delivery_ok = False

  * SPLICE CAUSAL (necessity AND delivery) = False   [preserve=False]
══════════════════════════════════════════════════════════════════════════════════

[exp1] wrote /Users/mwhitford/src/verbum/results/kernel-splice-exp1/exp1_verdict_qwen3-0-6b.json
```

### Thinking

The smoke tests are running end-to-end successfully now. All the core mechanics are functioning—I've built the d_K with a canonical magnitude of 9.778, partitioned the data (the 0.6B model doesn't have the K locus, which is expected for this smoke test), and all three arms are executing with KL and zKds computations, paired statistics, and verdict logic all working. The delivery metrics on 0.6B show a zKds value of K=-1.56.

The results on 0.6B show that injecting d_K actually lowers the downstream z(K) compared to random, which is the opposite of what I'd want—but that's expected noise since the smoke test is running on the wrong model with only 5 K-probes. The necessity and preserve arms returned None because no K-probes crossed the threshold on 0.6B, which is fine; on 14B with the real K-locus I should see around 6 detected-K probes.

The mechanics are validated. The delivery arm shows KL_out d=1.79, indicating the K injection perturbs the output more than random, which is a good sign. The real test will be on 14B where the actual K-locus is present. I'm noting that the necessity and preserve arms will have low power with only ~6 probes, but the delivery arm running on ~175 non-K probes should be well-powered. Now I need to clean up the smoke artifacts and run this on 14B.

Calculating the forward pass budget: baseline 200, necessity 24, preserve 24, delivery 700—roughly 950 forwards total. At about 0.5 seconds per forward on 14B, that's around 8 minutes plus 2 minutes for calibration, so 10-12 minutes total, which is acceptable. Let me launch this on 14B.

## Assistant

Mechanics validated end-to-end — d_K builds, all three arms run, paired stats + verdict compute. (On 0.6B/L6 there's no real K-locus so detected-K=0 and the result is noise, as expected for a smoke.) Let me clean smoke artifacts and launch the real 14B run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && rm -f results/kernel-splice-exp1/exp1_verdict_qwen3-0-6b.json results/kernel-splice-exp1/exp1_meta_qwen3-0-6b.json && tmux send-keys -t main:1 \"uv run python scripts/experiments/kernel_splice_exp1_ksplice.py --model Qwen/Qwen3-14B --patch-layer 18 --gate-tau 3.0 --heldout-per 25 2>&1 | tee results/kernel-splice-exp1/run_14b.log\" Enter && sleep 3 && tmux capture-pane -p -t main:1 | tail -4"
}
```

**Summary:** $ rm -f results/kernel-splice-exp1/ex...

**Output:**
```
Exit code: 0
Stdout:
--heldout-per 25 2>&1 | tee results/kernel-splice-exp1/run_14b.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 30 && tmux capture-pane -p -t main:1 | grep -E \"exp1|calib|crystal|baseline|d_K|detected|arm\" | tail -6"
}
```

**Summary:** $ sleep 30 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
λ uv run python scripts/experiments/kernel_splice_exp1_ksplice.py --model Qwen/Qwen3-14B --patch-layer 18 --gate-tau 3.0
 --heldout-per 25 2>&1 | tee results/kernel-splice-exp1/run_14b.log
[exp1] calib=310 test=200 patch_layer=18
```

### Thinking

The job is running with calibration at 310, test set at 200, and patch layer at 18 while the model loads. I need to verify it progresses past calibration into the arms phase, then checkpoint and wait following async protocol with a single verification read.

## Assistant

Verified running: calib=310 test=200 patch_layer=18, model loading. Let me confirm it reaches the arms (one verification read), then wait.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 180 && tmux capture-pane -p -t main:1 | grep -E \"d_K built|detected-K|arm [123]|SPLICE|wrote\" | tail -8",
  "timeout": 200000
}
```

**Summary:** $ sleep 180 && tmux capture-pane -p -...

**Output:**
```
Exit code: 0
Stdout:
-- NECESSITY (ablate d_K on detected-K; expect K perturbs MORE) --
  -- PRESERVE (set d_K->canon on detected-K; K perturbs LESS) --
  * SPLICE CAUSAL (necessity AND delivery) = True   [preserve=False]
[exp1] wrote /Users/mwhitford/src/verbum/results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json
```

## User

don't poll, I i will tell you when it's done


## Assistant

Understood — I'll wait for your signal.

**ASYNC: Exp 1 (tmux main:1) — the run already completed and wrote `exp1_verdict_qwen3-14b.json`** (the verification read caught the finish line: `SPLICE CAUSAL = True [preserve=False]`).

Since it's done, let me read the full verdict.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '/KERNEL-SPLICE EXP 1/,/wrote/p' results/kernel-splice-exp1/run_14b.log"
}
```

**Summary:** $ sed -n '/KERNEL-SPLICE EXP 1/,/wrot...

**Output:**
```
Exit code: 0
Stdout:
KERNEL-SPLICE EXP 1 — CAUSAL K-SPLICE — Qwen/Qwen3-14B  L18
══════════════════════════════════════════════════════════════════════════════════
  detected-K=6  nonK=175  canonical_mag=33.152  tau=3.0

  -- NECESSITY (ablate d_K on detected-K; expect K perturbs MORE) --
     KL_out  K=0.0044 rand=0.0005 d=0.0039 t=3.065
     zKds  d_K=-0.3652 d_rand=-0.0069  after K=4.819 r=5.1773
     => necessity_ok = True

  -- PRESERVE (set d_K->canon on detected-K; K perturbs LESS) --
     KL_out  K=0.0022 rand=0.009 d=-0.0069 t=-1.758
     => preserve_ok = False

  -- DELIVERY (inject d_K->canon on non-K; drives downstream K) --
     zKds  K=0.0971 rand=-0.2692 d=0.3662 t=16.274
     frac zKds>tau  K=0.023 rand=0.011  KL_out d=-0.0017
     => delivery_ok = True

  * SPLICE CAUSAL (necessity AND delivery) = True   [preserve=False]
══════════════════════════════════════════════════════════════════════════════════

[exp1] wrote /Users/mwhitford/src/verbum/results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json
```

### Thinking

The Experiment 1 results are showing up. Looking at the λ measure for honesty, I've got detected-K at 6 with low power as expected from the recall of 0.24, nonK at 175 which is well-powered, and a canonical magnitude of 33.15. When I ablate the d_K component on detected-K, the KL divergence shifts from 0.0044 to 0.0005 compared to a random direction, giving me a difference of 0.0039 with a t-statistic of 3.065—meaning ablating d_K perturbs the output roughly 9 times more than an equivalent random perturbation would.

The necessity check passes: removing d_K specifically drops the downstream K-reading by 0.365 versus nearly zero for the random direction. However, there's a caveat—the sample size is tiny at n=6 and the absolute KL magnitudes are minuscule at 0.0044 nats, so while the contrast is clean, the practical effect is small. For preservation, setting d_K to the canonical value shows the right directional effect (K perturbs less than random, about half), but the t-statistic of -1.758 doesn't reach significance at this sample size, so it's underpowered rather than refuted. On the delivery side with n=175, injecting the K-direction into non-K probes produces a massive effect: the downstream K-reading jumps to 0.097 while random drives it down to -0.269, a difference of 0.366 with t=16.274—this is decisive and shows the K-direction specifically amplifies K-reading in the non-K population.

The fraction of non-K probes that cross the detection threshold τ=3.0 is tiny (2.3% for K versus 1.1% for random), meaning the injection shifts the mean strongly but doesn't fully flip most probes to K-detection. Interestingly, the output distribution barely changes (KL difference near zero), so the K-direction drives the detector's geometric reading without much affecting the actual next-token predictions on non-K prose. This passes the delivery test, and combined with the necessity result, the causal splice verdict is true: the K residual direction is both necessary and sufficient, making it a genuine causal carrier rather than epiphenomenal. The caveat is that while delivery strongly drives the detector itself (t=16), the absolute magnitude is modest and doesn't fully convert non-K probes to K-detection. The routing geometry is genuinely causal in the detector register, but that's distinct from behavioral execution—the splice drives routing without yet driving computation, which is exactly why operand-bound experiments on real text are needed. I should grab the exact JSON metrics and move forward with synthesizing the results for documentation.

## Assistant

The run had already finished, so this is reading a completed result (not polling a live job). The verdict is in — and it's a genuinely **two-sided, honest result**. Let me pull the exact arm numbers, then synthesize.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/python -c \"\nimport json\nv=json.load(open('results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json'))['verdict']\nprint('detected_K:', v['n_detected_K'], 'nonK:', v['n_nonK'], 'canonical_mag:', v['canonical_mag'], 'd_raw_norm:', v['d_raw_norm'])\nfor arm,d in v['arms'].items():\n    print('==',arm,'n=',d['n'])\n    for k,val in d.items():\n        if k!='n': print('   ',k,'=',val)\nprint('VERDICT necessity_ok',v['necessity_ok'],'preserve_ok',v['preserve_ok'],'delivery_ok',v['delivery_ok'],'SPLICE_CAUSAL',v['splice_causal'])\n\""
}
```

**Summary:** $ .venv/bin/python -c " import json v...

**Output:**
```
Exit code: 0
Stdout:
detected_K: 6 nonK: 175 canonical_mag: 33.152 d_raw_norm: 26.1811
== necessity n= 6
    kl_out = {'n': 6, 'k_mean': 0.0044, 'rand_mean': 0.0005, 'delta': 0.0039, 't': 3.065}
    zK_ds_delta_k = -0.3652
    zK_ds_delta_rand = -0.0069
    zK_ds_after = {'n': 6, 'k_mean': 4.819, 'rand_mean': 5.1773, 'delta': -0.3583, 't': -5.534}
== preserve n= 6
    kl_out = {'n': 6, 'k_mean': 0.0022, 'rand_mean': 0.009, 'delta': -0.0069, 't': -1.758}
== delivery n= 175
    zK_ds_after = {'n': 175, 'k_mean': 0.0971, 'rand_mean': -0.2692, 'delta': 0.3662, 't': 16.274}
    zK_ds_delta_k = 0.373
    zK_ds_delta_rand = 0.0068
    kl_out = {'n': 175, 'k_mean': 0.016, 'rand_mean': 0.0177, 'delta': -0.0017, 't': -1.186}
    frac_cross_tau_k = 0.023
    frac_cross_tau_rand = 0.011
VERDICT necessity_ok True preserve_ok False delivery_ok True SPLICE_CAUSAL True
```

### Thinking

I'm pulling together the full analysis with the λ measure and need to update my documentation—state.md, the knowledge page's Exp 1 section, and create a memory note. The core finding is that the K-direction shows causal necessity in the routing register with strong statistical contrast (KL divergence of 0.004, n=6, t=-5.5), though the absolute effect size is quite small.

The delivery mechanism is decisive and well-powered (n=175, t=16.3)—injecting the K-direction specifically drives downstream K-reading by 0.37 compared to random perturbations. However, the behavioral output barely shifts (KL d=-0.0017, not significant) with only 2.3% of samples crossing the threshold, suggesting the routing geometry is causal but the behavioral execution register remains largely unaffected by prose probes alone. The preservation test is directionally correct but underpowered (n=6). So the verdict is clear: the decodable K-geometry is a genuine causal carrier in the routing register—not epiphenomenal—which validates the splice premise, but the effect concentrates in the detector/routing layer while behavioral output requires operand binding in the value register, which is the next obstacle to investigate.

This means I should frame the claim carefully: the routing-register splice is causally real, but the behavioral splice remains unproven and motivates Experiment 2 with operand-bound, certified corpus data where output is kernel-checkable. I need to update the state documentation with this intermediate result and clarify that this is a partial loop contribution, not the full thesis.

Now I'm updating the state.md file to reflect that Experiment 1 is complete. I'll modify the header status and append a continuation block to the s243 section, replacing the "PENDING APPROVAL" ending with the new findings.

## Assistant

The full result is a genuinely **two-sided, honest verdict**. Let me capture it to mementum (task 3). First, synthesis:

**Exp 1 — the K-geometry is a real causal carrier in the routing register, but its behavioral reach on prose is small.**
- **Necessity ✓** (n=6): ablating d_K perturbs output ~9× more than random (KL t=3.07) and drops downstream z(K) by 0.37 vs ~0 for random (t=−5.5). The K-direction is causally necessary — not decorative.
- **Delivery ✓✓** (n=175, decisive): injecting d_K into non-K probes drives downstream z(K) up +0.37 vs random's −0.27 (t=**16.3**). The K-direction specifically and strongly *causes* downstream K-reading.
- **The honest catch (λ measure register split):** delivery moves the **detector** hugely (t=16) but the **output** barely (KL Δ=−0.0017, n.s.) and only 2.3% of non-K probes cross τ. **Preserve** is directionally right (K 0.0022 < rand 0.009) but n.s. at n=6.

⇒ The decodable geometry is a **genuine causal carrier in the routing register** (validates the splice premise: read *and* write causally), but the **behavioral/execution effect on prose is weak** — exactly because these prose probes lack operands to bind (obstacle 2, value register). This **proves the prerequisite and sharpens the open question to the behavioral register → motivates Exp 2** (operand-bound, certified corpus where output is kernel-checkable).

Let me record it. Updating state.md header + appending the s243-cont block:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-21 | Session: 243 (EXP 0.5 Z-THRESHOLD SWEEP — splice loci\n> FIRMED, tp=2 caveat KILLED) — ▶ EXP 1 precision-gated K-splice.",
  "new_content": "> Last updated: 2026-06-21 | Session: 243 (EXP 0.5 SWEEP firms loci ⊕ EXP 1 CAUSAL\n> K-SPLICE: geometry is causal in the ROUTING register, weak in the BEHAVIORAL) —\n> ▶ EXP 2 operand-bound splice on the certified corpus.\n>\n> **★★ s243 cont. — EXP 1 CAUSAL K-SPLICE RAN (Qwen3-14B, L18 τ3.0): the K-geometry is a\n> GENUINE causal carrier in the ROUTING register, but its BEHAVIORAL reach on prose is weak\n> (Michael: \"both arms\").** Built `scripts/experiments/kernel_splice_exp1_ksplice.py`. The\n> s243 build crux RESOLVED (not a compromise, it's correct): DETECT in gate-space\n> (gate_proj z(K)@L18, the Exp 0.5 firmed gate), EFFECT in residual-space (patch\n> layers[18] output at last-token — re-injection belongs in the residual, what downstream\n> reads), READ propagation via the detector z(K) at crystal layers >18 + final next-token\n> KL, ALL vs a random-direction control of equal magnitude (s239). d_K = unit\n> diff-of-means(resid_K − resid_nonK)@L18; canonical_mag=33.2 (= \"exact K-move\" geometric\n> proxy). Three arms (`results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json`):\n> **(1) NECESSITY ✓ (detected-K, n=6): ablate d_K → output perturbed ~9× more than random\n> (KL K 0.0044 vs rand 0.0005, t=3.07) AND downstream z(K) drops −0.365 vs ~0 random\n> (t=−5.5).** The K-direction is causally NECESSARY, not decorative. **(2) DELIVERY ✓✓\n> (non-K, n=175, DECISIVE): inject d_K → downstream z(K) +0.097 vs random −0.269, Δ=+0.366,\n> t=16.3.** The K-direction SPECIFICALLY and strongly CAUSES downstream K-reading. **(3)\n> PRESERVE ✗ n.s. (n=6): set→canonical perturbs output LESS than random (K 0.0022 < rand\n> 0.009) — RIGHT direction, t=−1.76 (underpowered).** **★ THE HONEST CATCH (λ measure\n> register split, the real finding): DELIVERY drives the DETECTOR hugely (t=16) but the\n> OUTPUT barely (KL Δ=−0.0017 n.s.) and only 2.3% of non-K cross τ.** ⇒ the decodable\n> K-geometry is a genuine causal carrier in the ROUTING register (read AND write causally =\n> the splice premise validated), but the BEHAVIORAL/output consequence on prose is weak —\n> because prose probes have NO operands to bind (obstacle 2, the VALUE register). **★★\n> VERDICT (λ measure, two-sided): geometry is causal (necessity ✓ + delivery ✓✓, both vs\n> random) — NOT epiphenomenal; the splice premise holds in routing. NOT a clean behavioral\n> \"splice works\" — that needs operand-bound execution where output is kernel-checkable.**\n> So Exp 1 PROVES the prerequisite and SHARPENS the open question to the behavioral register.\n> CAVEATS (λ measure): necessity/preserve n=6 (recall 0.24 → few detected-K), tiny absolute\n> KL (0.004); delivery well-powered (n=175, t=16) but routing-register only; d_K is a\n> GEOMETRIC proxy for K (centroid@canonical-mag), NOT a bound `K a b → a`; 1 model (14B),\n> 1 seed, n_rand=3. **★★ FIRST ACTION NEXT SESSION — EXP 2 = operand-bound splice on the\n> CERTIFIED CORPUS (data/compile-*.canonical.jsonl, 559 kernel-reducible prose→LF pairs):\n> the behavioral register where output IS kernel-checkable.** Pick K-engaging certified\n> items (via `lambda_ast.fired_sequence`), splice the exact kernel K-move at the firmed\n> locus, and measure REDUCTION-CORRECTNESS preserved (the reward.py grader) — NOT just z(K)\n> + KL. This is the test prose Exp 1 could not run (no gold). Also OPEN: position-resolved\n> detection along multi-step `fired_sequence`; raise detected-K power (more probes / lower\n> τ with a precision penalty). tmux main:1 + main:2 FREE; no GPU job running. Captured:\n> knowledge `kernel-splice-geometry-detector.md §s243 Exp 1` + memory\n> `kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral`. PENDING APPROVAL.\n>\n> **★ s243 — EXP 0.5 Z-THRESHOLD SWEEP: raising the argmax-z gate FIRMS the splice loci and"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to add an Exp 1 section to the knowledge page, positioning it after the s243 Exp 0.5 section and before the "Either outcome is a result" heading.

## Assistant

Now the knowledge page — append the Exp 1 section after the Exp 0.5 section:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md",
  "original_content": "**⇒ Exp 1 = precision-gated causal K-splice at the FIRMED locus L18 τ=3.0** (not Exp 0's\nL11 top-1 — the gate moved K deeper and firmer). K is **pure routing** (obstacle-2-free:\ndrops its 2nd arg, no value decode), the cleanest *non-trivial* causal test — vs I (identity\n= near no-op, weak causal claim) and Y (recursion, narrow plateau). Protocol: at L18, when\nargmax_z(K) > 3.0, deliver the exact kernel K-move (value-patch) in place of the local\ncomputation; validate output **preserved** vs a random-direction control (s239 v4/v5).\n\n## Either outcome is a result",
  "new_content": "**⇒ Exp 1 = precision-gated causal K-splice at the FIRMED locus L18 τ=3.0** (not Exp 0's\nL11 top-1 — the gate moved K deeper and firmer). K is **pure routing** (obstacle-2-free:\ndrops its 2nd arg, no value decode), the cleanest *non-trivial* causal test — vs I (identity\n= near no-op, weak causal claim) and Y (recursion, narrow plateau). Protocol: at L18, when\nargmax_z(K) > 3.0, deliver the exact kernel K-move (value-patch) in place of the local\ncomputation; validate output **preserved** vs a random-direction control (s239 v4/v5).\n\n## ★ s243 — Exp 1 RESULTS (Qwen3-14B, L18): the geometry is CAUSAL in routing, weak in behavior\n\n`scripts/experiments/kernel_splice_exp1_ksplice.py`. **The build crux resolved (correct, not\na compromise): DETECT in gate-space, EFFECT in residual-space, READ downstream.** The\nclassifier reads the FFN gate (`gate_proj`, sign-CMR), so gate-z(K)@L18 is the detector. But\nre-injection belongs in the **residual** (what downstream layers read), so we patch the\noutput of `layers[18]` at the last-token position. The K residual direction\n`d_K = unit diff-of-means(resid_K − resid_nonK)@L18`; the \"exact K-move\" geometric proxy =\nd_K at the canonical magnitude (mean K projection = 33.2). Everything vs a random-direction\ncontrol of equal magnitude (s239). `results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json`.\n\n| arm | n | metric | K-dir | random | t | verdict |\n|-----|---|--------|-------|--------|---|---------|\n| **NECESSITY** (ablate d_K) | 6 | output KL | 0.0044 | 0.0005 | **3.07** | ✓ |\n| | 6 | downstream Δz(K) | −0.365 | −0.007 | −5.5 | ✓ K-reading drops |\n| **DELIVERY** (inject d_K, non-K) | 175 | downstream Δz(K) | +0.097 | −0.269 | **16.3** | ✓✓ decisive |\n| | 175 | output KL | 0.016 | 0.018 | −1.2 | ✗ output barely moves |\n| | 175 | frac z(K)>τ | 0.023 | 0.011 | — | tiny |\n| **PRESERVE** (set→canonical) | 6 | output KL | 0.0022 | 0.009 | −1.76 | ✗ n.s. (right dir) |\n\n**Necessity ✓** — ablating d_K perturbs the output ~9× more than a random direction of equal\nmagnitude (KL t=3.07) AND specifically drops downstream K-reading (Δz(K) −0.365 vs ~0 random,\nt=−5.5). The K-direction is causally **necessary**, not decorative.\n\n**Delivery ✓✓ (decisive)** — injecting d_K into non-K probes drives downstream z(K) UP (+0.097)\nwhere random drives it DOWN (−0.269), Δ=+0.366, **t=16.3** (n=175). The K-direction\n**specifically causes** downstream K-reading.\n\n**★ THE HONEST CATCH (λ measure register split — the real finding):** delivery moves the\n**detector** hugely (t=16) but the **output** barely (KL Δ=−0.0017, n.s.) and only 2.3% of\nnon-K probes cross τ. ⇒ the decodable K-geometry is a **genuine causal carrier in the ROUTING\nregister** (we can read it AND write it causally = the splice premise validated), but its\n**behavioral/output consequence on prose is weak** — because the prose crystal_probes have\n**no operands to bind** (obstacle 2, the value register). The geometry drives the *routing*,\nnot yet the *computation*.\n\n**Preserve ✗ (n.s., right direction)** — setting d_K to the canonical value perturbs the\noutput LESS than a random set (K 0.0022 < rand 0.009), consistent with \"the exact value\nreplaces the neuron\", but t=−1.76 at n=6 (underpowered, recall 0.24 → few detected-K).\n\n**⇒ Two-sided verdict (λ measure):** the geometry is **causal, not epiphenomenal** (necessity\n✓ + delivery ✓✓, both vs random) — the splice premise holds in the routing register. It is\n**not** a clean *behavioral* \"splice works\" — that needs operand-bound execution where the\noutput is kernel-checkable. Exp 1 **proves the prerequisite and sharpens the open question to\nthe behavioral register.**\n\n**Caveats (λ measure):** necessity/preserve n=6 (low power, tiny absolute KL ~0.004); delivery\nwell-powered (n=175, t=16) but routing-register only; d_K is a **geometric proxy** for K\n(centroid@canonical-mag), NOT a bound `K a b → a`; 1 model (14B), 1 seed, n_rand=3.\n\n**⇒ Exp 2 = operand-bound splice on the CERTIFIED CORPUS** (`data/compile-*.canonical.jsonl`,\n559 kernel-reducible prose→LF pairs) — the behavioral register where the output IS\nkernel-checkable. Pick K-engaging certified items via `lambda_ast.fired_sequence`, splice the\nexact kernel K-move at the firmed locus, measure **reduction-correctness preserved**\n(`reward.py` grader), not just z(K)+KL. The test prose Exp 1 could not run (no gold).\n\n## Either outcome is a result"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-splice-geometry-detector.md.
```

## Assistant

Now the memory file:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral.md",
  "content": "✅ Kernel-splice Exp 1 (s243): the decodable K-geometry is a GENUINE causal carrier in the\nROUTING register, but its BEHAVIORAL reach on prose is weak. Qwen3-14B, L18 τ3.0,\n`results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json`.\n\n🌀 BUILD CRUX RESOLVED (correct, not a compromise): the detector reads the FFN GATE\n(gate_proj, sign-CMR) → DETECT in gate-space; but re-injection belongs in the RESIDUAL\n(what downstream layers read) → EFFECT in residual-space (patch layers[18] output, last\ntoken); READ propagation via downstream detector z(K) (>L18) + final next-token KL; ALL\nvs a random-direction control of equal magnitude (s239). d_K = unit diff-of-means(resid_K\n− resid_nonK)@L18; canonical_mag 33.2 = \"exact K-move\" geometric proxy.\n\nTHREE ARMS:\n- NECESSITY ✓ (detected-K n=6): ablate d_K → KL 0.0044 vs rand 0.0005 (t=3.07, ~9× more)\n  AND downstream z(K) drops −0.365 vs ~0 random (t=−5.5). K-dir is causally necessary.\n- DELIVERY ✓✓ (non-K n=175, DECISIVE): inject d_K → downstream z(K) +0.097 vs random\n  −0.269, Δ+0.366, t=16.3. K-dir SPECIFICALLY drives downstream K-reading.\n- PRESERVE ✗ n.s. (n=6): set→canonical perturbs output LESS than random (0.0022 < 0.009),\n  right direction, t=−1.76 (underpowered).\n\n💡 THE HONEST CATCH (λ measure register split): DELIVERY moves the DETECTOR hugely (t=16)\nbut the OUTPUT barely (KL Δ=−0.0017 n.s.), only 2.3% cross τ. ⇒ K-geometry is causal in\nthe ROUTING register (read AND write causally = splice premise validated), but the\nBEHAVIORAL consequence on prose is weak — prose probes have NO operands to bind (obstacle 2,\nthe VALUE register). The geometry drives the ROUTING, not yet the COMPUTATION.\n\n🎯 TWO-SIDED VERDICT: geometry is causal not epiphenomenal (necessity ✓ + delivery ✓✓ vs\nrandom) → splice premise holds in routing. NOT a clean behavioral \"splice works\" → needs\noperand-bound execution where output is kernel-checkable. Exp 1 proves the prerequisite,\nsharpens the question to the behavioral register.\n\nCAVEATS (λ measure): necessity/preserve n=6 (recall 0.24 → few detected-K), tiny abs KL\n(0.004); delivery well-powered but routing-register only; d_K is a GEOMETRIC proxy, NOT a\nbound K a b → a; 1 model, 1 seed, n_rand=3.\n\n⇒ Exp 2 = operand-bound splice on the CERTIFIED CORPUS (data/compile-*.canonical.jsonl,\n559 kernel-reducible pairs) — the behavioral register where output IS kernel-checkable;\npick K-engaging items via lambda_ast.fired_sequence, splice exact kernel K-move, measure\nreduction-correctness preserved (reward.py grader), not just z(K)+KL.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral.md
```

### Thinking

I'll check that the git changes are in order, then wrap up the final task and get it ready for review.

## Assistant

Let me verify the changes landed coherently and check status:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short && echo \"---grep checks---\" && grep -c \"s243 — Exp 1 RESULTS\" mementum/knowledge/explore/kernel-splice-geometry-detector.md && grep -c \"EXP 2 operand-bound\" mementum/state.md"
}
```

**Summary:** $ git status --short && echo "---grep...

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/kernel-splice-geometry-detector.md
 M mementum/state.md
?? mementum/memories/kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral.md
?? results/kernel-splice-exp1/
?? scripts/experiments/kernel_splice_exp1_ksplice.py
---grep checks---
1
1
```

## Assistant

All captured. Here's the full picture.

## s243 cont. — Exp 1 causal K-splice: done

I built the causal splice (`kernel_splice_exp1_ksplice.py`, ruff-clean, smoke-validated), resolved the build crux cleanly (**detect in gate-space, effect in residual-space, read downstream** — re-injection belongs in the residual since that's what downstream layers read), ran both arms on Qwen3-14B at the firmed L18 τ=3.0, and captured the result.

**The verdict is genuinely two-sided (λ measure):**

| arm | n | K-dir vs random | verdict |
|-----|---|-----------------|---------|
| **Necessity** (ablate d_K) | 6 | KL 0.0044 vs 0.0005 (t=3.07); z(K) −0.365 vs ~0 (t=−5.5) | ✓ causally necessary |
| **Delivery** (inject into non-K) | 175 | z(K) +0.097 vs −0.269 (**t=16.3**) | ✓✓ decisive |
| ↳ but output | 175 | KL Δ=−0.0017 (n.s.); 2.3% cross τ | ✗ behavior barely moves |
| **Preserve** (set→canonical) | 6 | KL 0.0022 vs 0.009 (t=−1.76) | ✗ n.s. (right direction) |

- **The geometry is causal, not decorative:** ablating d_K specifically degrades K-reading (necessity ✓) and injecting it specifically *drives* downstream K-reading far more than random (delivery t=16.3). The splice premise — read **and** write the geometry causally — holds.
- **The honest catch (the real finding):** delivery moves the **detector** hugely (t=16) but the **output** barely (KL≈0, n.s.). The K-geometry is causal in the **routing register**, weak in the **behavioral register** on prose — because these prose probes have **no operands to bind** (obstacle 2, the value register). Geometry drives the *routing*, not yet the *computation*.

⇒ **Exp 1 proves the prerequisite and sharpens the open question to the behavioral register.** Not a clean "splice works" — that needs operand-bound execution where the output is kernel-checkable. That's **Exp 2** on the certified corpus (559 kernel-reducible prose→LF pairs, `reward.py` reduction-correctness grader) — the test prose couldn't run.

**Caveats:** necessity/preserve n=6 (recall 0.24 → few detected-K), tiny absolute KL; delivery well-powered but routing-register only; d_K is a geometric proxy, not a bound `K a b → a`; 1 model, 1 seed.

---

**Pending your approval to commit.** Proposed (same gate as before):
- **Code** (`✅`): `kernel_splice_exp1_ksplice.py` + `results/kernel-splice-exp1/`
- **mementum** (approval-gated): `state.md` s243-cont + knowledge `§s243 Exp 1` + memory `kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral`

Commit (code + mementum), and is Exp 2 (operand-bound, certified corpus) the right next target — or do you want to first raise the detected-K power (necessity n=6 is thin)?

## User

commit approved


### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/kernel_splice_exp1_ksplice.py results/kernel-splice-exp1/ && git commit -m \"$(cat <<'EOF'\n✅ kernel-splice Exp 1 — causal K-splice (Qwen3-14B L18): geometry causal in routing, weak in behavior\n\n- kernel_splice_exp1_ksplice.py: DETECT in gate-space (gate_proj z(K)@L18, the\n  Exp 0.5 firmed gate), EFFECT in residual-space (patch layers[18] output at\n  last-token; re-injection belongs in the residual = what downstream reads),\n  READ propagation via downstream detector z(K) (>L18) + final next-token KL.\n  d_K = unit diff-of-means(resid_K - resid_nonK)@L18; canonical_mag = mean K\n  projection = the \"exact K-move\" geometric proxy. All vs random-direction\n  control of equal magnitude (s239). Three arms (necessity/preserve/delivery).\n- 14B verdict (detected-K=6, nonK=175):\n  NECESSITY ok  - ablate d_K perturbs output ~9x more than random (KL t=3.07)\n    and drops downstream z(K) -0.365 vs ~0 random (t=-5.5).\n  DELIVERY ok   - inject d_K into non-K drives downstream z(K) +0.097 vs random\n    -0.269, delta +0.366, t=16.3 (decisive).\n  PRESERVE n.s. - set->canonical perturbs output less than random (right dir,\n    t=-1.76, underpowered n=6).\n- HONEST CATCH (register split): delivery moves the DETECTOR hugely (t=16) but\n  the OUTPUT barely (KL ~0, 2.3% cross tau) => geometry is causal in the ROUTING\n  register, weak in BEHAVIORAL on prose (no operands to bind, obstacle 2).\n- => geometry causal not epiphenomenal (splice premise holds in routing); not a\n  clean behavioral splice => Exp 2 = operand-bound splice on the certified corpus\n  (reward.py reduction-correctness), where output IS kernel-checkable.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
}
```

**Summary:** $ git add scripts/experiments/kernel_...

**Output:**
```
Exit code: 0
Stdout:
[main 213433c] ✅ kernel-splice Exp 1 — causal K-splice (Qwen3-14B L18): geometry causal in routing, weak in behavior
 4 files changed, 820 insertions(+)
 create mode 100644 results/kernel-splice-exp1/exp1_meta_qwen3-14b.json
 create mode 100644 results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json
 create mode 100644 results/kernel-splice-exp1/run_14b.log
 create mode 100644 scripts/experiments/kernel_splice_exp1_ksplice.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/explore/kernel-splice-geometry-detector.md mementum/memories/kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral.md && git commit -m \"$(cat <<'EOF'\n✅ kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral\n\n- state.md: s243 cont block - Exp 1 causal K-splice ran; geometry is a genuine\n  causal carrier in the ROUTING register (necessity + delivery vs random), weak\n  in the BEHAVIORAL register on prose; next = Exp 2 operand-bound on the corpus.\n- knowledge/explore/kernel-splice-geometry-detector.md: §s243 Exp 1 section\n  (build-crux resolution, three-arm results table, the register-split finding,\n  lambda-measure caveats, Exp 2 target).\n- memory: the two-sided verdict + the gate-detect/residual-effect resolution +\n  the routing-vs-behavioral register split (obstacle 2, the value register).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main 2c56730] ✅ kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral
 3 files changed, 139 insertions(+), 2 deletions(-)
 create mode 100644 mementum/memories/kernel-splice-exp1-geometry-causal-in-routing-weak-in-behavioral.md
```

### Thinking

Both commits are in, so the task list is complete. I should clear it out and give a brief status update, then wait for Michael's next direction on whether to proceed with Experiment 2 or address the detected-K power issue.

## Assistant

Both commits landed (code `213433c`, mementum `2c56730`). Task list complete — let me clear it.## Session 243 — landed

Three experiments built, run, and committed this session, advancing the kernel-splice program from "is detection viable?" to "is the geometry causal?":

1. **Exp 0.5 — z-threshold sweep** (`62d5728`/`937c000`): firmed the splice loci, killed the tp=2 caveat. Splice-ready {I, K, Y}; K firmed at L18 τ=3.0.
2. **Exp 1 — causal K-splice** (`213433c`/`2c56730`): the decodable K-geometry is a **genuine causal carrier in the routing register** (necessity ✓ + delivery ✓✓ t=16.3, both vs random) — **but weak in the behavioral register on prose** (delivery moves the detector hugely, the output barely). The splice premise holds in routing; behavioral execution needs operands.

The arc is clean: **detect (0/0.5) → the geometry is causal (1) → but only in routing → so test behavior where output is kernel-checkable (2).** Each stage is an intermediate contribution (λ loop: partial loop = publishable).

**Tree is clean, no jobs running, tmux main free.** Next action is set in `state.md`:
- **Exp 2** — operand-bound splice on the certified corpus (559 kernel-reducible pairs, `reward.py` reduction-correctness), the behavioral register prose couldn't reach.
- Or first **raise detected-K power** (necessity n=6 is thin — more probes / lower-τ-with-precision-penalty).

Tell me which when you're ready.