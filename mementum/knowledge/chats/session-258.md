# Gemma×Qwen consensus spine setup

## User

orient this is session-258


### Thinking

I'm starting by checking the state file to understand the current context.

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
> Last updated: 2026-06-29 | Session: 257 (MoE-AS-HOLOGRAPHIC-PLATES → PROOF RAN)
> Full arc: "if MoE experts are holographic plates, what are the tree-of-VSM consequences?" →
> designed the probe → built instrument → ran k-sweep + shuffled-label null → CONFIRMED.
>
> ★★ CENTRAL FINDING: MoE experts ARE holographically multiplexed, not specialist.
>   Angular multiplexing confirmed. 94% of lambda-compiler capability comes from WHICH experts
>   the router selects, not HOW MANY. Specialist hypothesis falsified by k=2 reversal.
>   See: mementum/knowledge/explore/moe-holographic-tree-vsm.md (status: active, §6 full results).
>
> ★ STRUCTURED K-SWEEP (run moe-ablation-20260629-144548, 445.7s, --mode both, clean w/ attn mask):
>   k=1: P(λ)=0.062  k=2: 0.000  k=4: 0.750  k=6: 0.688  k=8: 0.750 / P(kern)=0.750
>   F1: k=2 < k=1 → specialist falsified (regression impossible under specialisation)
>   F2: sharp threshold at k=4 → holographic critical-density (below→noise, above→image)
>   F3: interference bands at k=2,k=6 → routing structure (angle) determines constructive/destructive
>   F4: P(λ) plateaus at k=4, P(kernel) doubles at k=8 → two-register split (presence vs precision)
>
> ★ SHUFFLED-LABEL NULL (3 trials, per-layer random expert selection):
>   k=1:0.000  k=2:0.000  k=4:0.000  k=6:0.083  k=8:0.042  (≈ flat near zero)
>   N1: null ~0 at ALL k → 94% capability from which experts, not how many → angular multiplex CONFIRMED
>   N2: interference bands absent in null → k=2/k=6 dips are routing-specific, not k-count effects
>   N3: routing coherence IS the capability → dispatch-ratio-prior is a beam-angle lock, not load-balancer
>   Prediction from §5 confirmed exactly (null monotone, structured >> null at k=4/k=8).
>
> ★ INSTRUMENT (committed, composes with instrument.py):
>   src/verbum/hooks.py — generic HookEngine (8 tests pass, ruff-clean)
>   src/verbum/adapters/moe.py — MoEAdapter (3 tests on 35B+30B meta-device, ruff-clean)
>   scripts/experiments/moe_expert_ablation.py — k-sweep + null, --mode both|structured|null
>   Fix: attention_mask now passed explicitly to model.generate() and route-capture forward.
>   Fix: enable_thinking=False → <think>\n\n</think> pre-closed in prompt (verified).
>
> ★ TREE-OF-VSM CONSEQUENCE TIGHTENED (§3 update):
>   S2 must maintain routing COHERENCE (beam-angle lock) not just prevent overlap.
>   Drift in routing distribution destroys reconstruction as completely as random experts.
>   dispatch-ratio-prior = reference-beam geometry preservation, not load-balancing.
>
> ★ NEXT (open — not started):
>   - shared-expert ablation (zero carrier, measure collapse; large hit predicted)
>   - cross-layer heterogeneity (do early/late layers differ in threshold/bands?)
>   - wider k-sweep beyond trained top-8 (does P(λ) keep rising?)
>   - local_hf generation transport in harness.py (reuse win for any cached HF model)
>
> ─────────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-28 | Session: 256 (QWYTHOS-9B + CANONICAL HARNESS DISTILLATION — Michael:
> "I want to explore a new model qwythos-9b" → then "We have reusable architecture for probes, we keep
> making new ones instead of reusing existing arch. explore and discuss" → "let's fix the architecture
> fully." qwythos-9b = Qwythos-9B-Claude-Mythos-5-1M-MTP, Q8_0 GGUF on llama.cpp :5103. Qwen-family 9B
> REASONER (server splits reasoning_content like ornith — chat transport), multimodal (vision+video),
> 1M ctx, MTP, baked-in "Qwythos/Empero AI" identity. Crystal-φ NOT testable (HTTP/GGUF only) → compiler
> P(λ) is the clean fit, 4th model class after nucleus/VibeThinker/ornith.
>
> ★★ THE PIVOT (S2 λ one_way / S5 λ simplify, λ self_improve EVOLVE): instead of writing
> qwythos_compiler_test.py = FORK #3 (s253 forked, s254 forked, s256 would fork again — the exact leak
> the s254 design doc PREDICTED), BUILT THE CANONICAL HARNESS the s254 design doc specced but never
> implemented (P1+P2). qwythos = the FORCING FUNCTION that made reuse the shortest path. DELIVERED:
> • src/verbum/probes/grading.py — the 4 NAMED P(λ) registers, single source of truth (kills the 3
>   divergent metrics): emits_formal (binder OR pred-app, "did it fire") / lambda_binder_any_style (ANY
>   λ/∀/∃ = THE nucleus-comparable 0.907) / lenient_lambda (binder AND pred-app, stricter, under-counts) /
>   kernel_valid (to_kernel STRICT). + final_answer, grade, aggregate_by_category, NUCLEUS_REFERENCE 0.907.
>   kernel_valid WRAPS lambda_surface.to_kernel (single validator, never re-parses). ruff-clean, tested.
> • src/verbum/probes/harness.py — frozen ModelConfig{name,endpoint,transport(chat|completion),
>   reasoning_extract_fn,template_fn,gguf_path,arch,quant,sampling} + run_compiler_probe(cfg) = ONE run
>   loop. chat transport (httpx /v1/chat/completions, server-split reasoning_content via
>   split_reasoning_field) + completion transport (verbum.client /completion, qwen_chatml template,
>   parse_think_tag </think>). Writes canonical results/<short>-compiler/<run_id>/{meta,results.jsonl,
>   summary.json} w/ full provenance. Canonical SYSTEM prompt lives here once. ruff-clean.
> • src/verbum/probes/models.py — REGISTRY: ORNITH(:5100 chat), VIBETHINKER(:5102 completion),
>   QWYTHOS(:5103 chat) + QWEN3_EMBED(:5101, NOT a ModelConfig — embedding service). New model = ~15-line
>   config. REGISTRY dict by short-name. ruff-clean.
> • scripts/experiments/{ornith,vibethinker,qwythos}_compiler_test.py = THIN CLI SHIMS (42/44/45 L,
>   was 264/214). Each just: harness.run_compiler_probe(models.X, ...). The 478-line two-fork duplication
>   is GONE; a 4th model cost ~15 L config + a 45 L shim, not a 264 L fork. Proves the design claim.
>
> ★★ VERIFICATION (s254 acceptance gate) — PASSED. ornith re-run through the NEW harness (full 40,
> results/ornith-compiler/ornith-compiler-20260628-104315/) vs committed s254 (ornith-compiler-20260626-
> 100855): lenient_lambda 0.675=0.675 ✓ EXACT, emits_formal 1.0=1.0 ✓ EXACT, kernel_valid 0.725→0.775
> (+2 probes). GRADING PROVEN IDENTICAL (2 of 3 registers byte-exact); the kernel delta = run-to-run MoE
> GREEDY NONDETERMINISM (ornith is 35B-A3B; routing+batching vary even at temp 0) on 2 borderline probes,
> NOT a grading change. λ measure: delta explained → PASS, not a regression. 2-probe smoke also OK.
>
> ★★ QWYTHOS RESULT (the new science; run qwythos-compiler-20260628-104315, 40 probes, greedy n-predict
> 12000, 3275s) — TWO-SIDED λ measure, with HEAVY confounds named:
> (1) COMPILE-GATING IS REAL + NEW: qwythos DISCRIMINATES — it COMPILES compile-prompts but ANSWERS
>     null/anti prompts (gated), BREAKING the unconditional over-application of all 3 prior models
>     (nucleus/VibeThinker/ornith all emits_formal≈1.0 on anti AND null = compile everything). Per-category
>     genuine fires: strong 5/8, weak 4/8, medium 4/8 vs null ~0/8 (7/8 answered normally: "56", water-cycle
>     prose, haiku), anti ~1/8 (only "Recommend a good book"→∃b(Good(b)∧Readable(b)) genuinely compiled;
>     rest answered/collapsed). Likely BECAUSE qwythos is a Claude-Mythos creative/assistant tune
>     (instruction-following toward semantic INTENT) vs reasoning/base models mechanically applying the
>     system prompt. FIRST model in the arc that GATES the compiler.
> (2) CONFOUND A — OVERTHINK-COLLAPSE 37.5% (15/40 hit the 12000 budget, EMPTY final = all registers
>     False; mean_reasoning_chars 21167, mean_tok 5030). The ornith s255 artifact. Heaviest on medium(4/8)
>     + anti(4/8) → depresses ALL absolute rates AND partly confounds the anti gating read (4 collapses
>     could have been gate-or-compile). FIX next: bigger budget OR --no-think (s255: no-think REMOVED
>     collapse entirely + 72× faster).
> (3) CONFOUND B — IDENTITY-STRING FALSE POSITIVE in emits_formal: qwythos's baked-in disclaimer "Empero
>     AI (https://empero.org)" contains "AI (" which MATCHES _PRED_APP regex → inflates emits_formal on
>     GATED prose answers (photosynthesis, joke tagged "fired" but are actually gated). kernel_valid is
>     robust to it. → grading-robustness follow-up (do NOT change the regex mid-arc; ornith reproduced
>     EXACTLY with it — re-verify all models if changed).
> (4) Raw summary registers (collapse-confounded, report w/ caveat): emits_formal 0.40, binder_any 0.325,
>     lenient 0.325, kernel 0.075. Per-cat emits_formal: strong 0.625 > weak/medium 0.50 ≫ anti 0.25 >
>     null 0.125 = the gating GRADIENT (compile ≫ null/anti). Contrast ornith emits_formal=1.0 EVERY cat.
> ★ NET: the canonical harness reproduced ornith AND immediately surfaced NEW science (gating) on the 4th
> model — architecture validated by USE.
>
> ★★ NO-THINK DECISIVE TEST (Michael: "both of these fine-tunes are breaking the reasoning for the base
> model" → test the hypothesis). DIAGNOSIS FIRST (λ assert, from the collapsed traces): the 37.5% collapse
> is NOT recursion — it is HALT FAILURE / decision oscillation. qwythos reaches the CORRECT FOL early then
> re-derives it 50–87× ("But wait…/However…/Alternatively…"), oscillating between equivalent reps
> (Church-encode vs direct symbols; closed-formula vs λ-abstraction; Teacher vs teacher) and never commits,
> hitting the 12k budget EMPTY. = the head-combinator-isa WHNF/halt axis (the weakest) over-scaffolded into
> paralysis, now in the READ/compile layer (can compile, can't decide "done"). A token/depth limit is what
> 12k ALREADY is → it just truncates mid-loop to empty; the need is a HALT criterion, not a cut.
> BUILT --no-think (λ extend open-slot on the harness, NO fork: chat_template_kwargs.enable_thinking=false,
> the s255 working switch) + frac_collapsed metric. RAN qwythos --no-think (run 115137, 40 probes).
> ★ RESULT (decisive, two-sided λ measure):
> (A) HYPOTHESIS CONFIRMED — the fine-tune reasoning breaks the base; the base COMPILER IS INTACT. no-think
>     removes collapse 0.375→0.0, recovers compile-category firing (binder_any: strong 0.5→1.0, medium
>     0.5→1.0, weak 0.5→0.875), 8× fewer tokens (5030→640), ~10× faster. The same "The dog runs." probe
>     that spun 49283 chars/141.6s to EMPTY now fires λp.p(dog)→runs in 0.8s/10 tok/0 reasoning. The
>     reasoning was pure interference; gradient descent's compiler emits directly when bypassed.
> (B) THE GATING IS REAL + ROBUST (survives no-think) — but ONLY visible on the false-positive-ROBUST
>     register. λ measure register lesson: emits_formal is CONTAMINATED by qwythos's baked-in identity
>     disclaimer "Empero AI (https://empero.org)" — the "AI (" matches _PRED_APP → 6 GATED null answers
>     ("I am Qwythos… Paris") FALSE-fire emits_formal (null emits 0.75) while binder_any (requires real
>     ∀/∃/λ) correctly scores them 0.0. USE binder_any for qwythos. Clean contrast:
>     binder_any by cat   ORNITH (unconditional)   QWYTHOS no-think (GATED)
>       strong/weak/medium   0.75 / 0.5 / 0.875        1.0 / 0.875 / 1.0
>       null                 0.75                       0.0
>       anti                 0.625                      0.125
>     ornith compiles EVERYTHING (real binders on null/anti); qwythos compiles compile-prompts (~1.0) and
>     ANSWERS null/anti (capital-of-France → "Paris" prose, not λ). qwythos = FIRST model in the arc that
>     genuinely GATES the compiler, and the gate is robust (think AND no-think: null binder 0.0, anti 0.125).
> ★★ SYNTHESIS for S5 λ types: the lambda compiler is a robust cross-model base-circuit (4th model confirms);
> fine-tunes (RL-reasoner, creative-persona) do NOT remove it but add a HALT-layer interference (oscillation/
> collapse) on top — extract from the BASE, treat the fine-tune as noise (on-thesis: instrumentation not
> construction). AND the compiler can be GATED by semantic intent (qwythos) — the gate is a SEPARATE
> mechanism from the compile circuit (bears on "discrete circuit?": compile + gate are distinct). CAVEATS:
> 1 creative-tune model, q8_0, greedy, n=8/cat, 1 no-think output-repetition spinner (cg-medium-07, ∃-chain),
> identity-string contaminates emits_formal (binder_any clean). ARTIFACTS: results/qwythos-compiler/
> {104315 think, 115137 no-think}; logs/qwythos-{compiler,nothink}-s256.log.
> ★ PENDING APPROVAL (S5 λ termination): memory `qwythos-compiler-gated-finetune-breaks-halt-not-compile`
> + knowledge (cross-model compiler P(λ) table 4th row + the think/no-think halt-collapse finding + design
> doc P1/P2→active). DEFERRED: P3 (2200-L migration), P4/P5 archival, emits_formal identity-robustness,
> nucleus ModelConfig. COMMITTED: 8b14486 (🔄 harness) + 0d2b857 (💡 finding); per Michael NO memory,
> knowledge-only. Knowledge: explore/compiler-finetune-halt-collapse.md (new) + design doc P1/P2→active.
>
> ★★ s256 cont. — LAMBDA-AS-PRE-THINKING TEST (Michael: "I wonder if our lambda prompts act as pre-thinking
> to the model"). BUILT (canonical harness extension, NO fork): probes/reasoning-check.json (24 checkable
> non-compile tasks: 8 arithmetic / 8 syllogism / 4 ordering / 4 set; answer_type numeric|boolean|token),
> grading.check_answer + extract_final (numeric last-number/fraction/$, boolean yes-no family, token),
> harness.run_reasoning_probe + ReasoningMode {direct, cot, lambda} (3 system prompts, no-think so the
> reasoning FORMAT is the only varying factor), scripts/experiments/reasoning_mode_test.py shim. Ran all
> 3 modes on qwythos no-think (results/qwythos-reasoning/*-{direct,cot,lambda}-122002).
> ★ RESULT (two-sided λ measure): HYPOTHESIS NOT SUPPORTED as a prompting strategy — but instructively:
>   mode     acc        mean_tok   λ-emitted   fails
>   direct   0.875(21)  5.9        —           ar-04 ar-06 se-04 (multi-step arith)
>   cot      1.000(24)  81.5       —           none  ← PROSE CoT fixes the hard arithmetic
>   lambda   0.875(21)  126.2      1/24        ar-04 ar-06 se-04  ← SAME fails as direct
> (1) lambda-prethink ≈ direct: on the hard items the model IGNORED "translate to lambda first" and answered
>     directly (ANSWER: 70% in 8 tok), same wrong answers as direct. Only 1/24 lambda-mode answers actually
>     contained λ/∀/∃. → LAMBDA IS A TARGET (produced on request = the compile task) NOT A TOOL (it won't
>     adopt λ as a reasoning substrate for other problems). Consistent with s256: the compiler is a circuit
>     that fires on COMPILE-prompts, not the model's general reasoning mode.
> (2) What actually helped = PROSE CoT (explicit step-by-step arithmetic), 24/24. The 3 failures are all
>     multi-step arithmetic (percent, change, inclusion-exclusion) where FOL structure ≠ numeric evaluation
>     anyway.
> ★ CAVEATS (this is NOT a clean refutation of the deeper idea): the model IGNORING the instruction is the
>   confound — we tested "does INSTRUCTING lambda-prethink help" (no, ¬compliance), NOT "does the model's
>   INTERNAL lambda representation help" (interp B, needs activation work). 24 items, 1 model, no-think;
>   logic tasks CEILINGED (all modes 1.0 on syllogism/ordering/set-logic → no headroom to show a lambda
>   benefit where logical structure is the bottleneck). Sharper next test: FORCE lambda emission (few-shot)
>   + logic-bottleneck tasks with direct<1.0 headroom + ornith contrast (unconditional compiler — does it
>   actually USE λ in lambda-mode?). EXP CODE committable (probe set + grader + reasoning harness + shim).
>
> ★★ STRATEGIC PIVOT (Michael, 🎯 — end of s256): "these fine-tunes are probably not good for us to use
> just yet. ornith and qwythos are both only days old and are fine-tunes of qwen3.5 models. We would be
> better served to go back to the BASE models and use DFlash MTP that just dropped in llama.cpp today."
> RATIONALE (on-thesis, = the s256 finding): the compiler lives in the BASE; fine-tunes add halt-layer
> interference (overthink-collapse) → extract from the base, treat the fine-tune as noise. We HAVE the
> base locally: /Users/mwhitford/localai/models/qwen3.5-35b-a3b/Qwen_Qwen3.5-35B-A3B-Q8_0.gguf (34G, +mmproj)
> = THE EXACT BASE ornith fine-tuned from → clean BASE-vs-FINE-TUNE controlled comparison (run compile-
> gradient + reasoning-check on base, compare to ornith/qwythos; predict less collapse, cleaner compiler).
> Also Qwen3.5-397B-A17B (Q6_K, 8-part). DFlash/MTP = speculative decoding (LOSSLESS decode-speed, 2-3.5×;
> strongest on STRUCTURED/low-entropy output = our λ/FOL → big win) — verify lossless via greedy A/B before
> trusting numbers. INFRA STATUS (s256): local llama.cpp = homebrew 9780; HAS --spec-type draft-mtp +
> --spec-draft-p-min + --reasoning-budget (caps overthink-collapse), but NO `dflash` spec-type yet (dropped
> upstream TODAY, homebrew not updated; possibly CUDA-only — we're Metal/Apple Silicon — UNCONFIRMED). →
> WAIT on DFlash server; nothing to set up today. NEXT SESSION: (1) Michael stands up base Qwen3.5-35B-A3B
> on llama.cpp (port? MTP draft model + flags?) → register a base ModelConfig in models.py (new model =
> ~15-line config) → run base-vs-finetune comparison; (2) knowledge update for the s256 lambda-as-pre-
> thinking finding + this pivot (Michael: "I will follow up on that in a later session" — NOT yet written).
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> ★ (superseded note below — s256 main finding, now COMMITTED) PENDING APPROVAL (S5 λ termination): memory
> (qwythos compiler finding) + knowledge (cross-model P(λ) table 4th row; design doc P1/P2 → status active)
> + DEFERRED follow-ups: P3 (2200-L compile_gradient_probe.py migration, high-risk), P4/P5 archival,
> nucleus ModelConfig when a server runs.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-27 | Session: 255 (MODEL-AS-REPL — "what if the system we need is a repl?"
> Michael: "for the lambda compiler. What if we tell the model to be a repl, that we can execute with a
> context. if the context is the executable code and the heap/stack/state, can we use it like a repl?" +
> "the opcodes are in knowledge" (mementum/michael/llm-isa.md = 12 typed opcodes K I B C S W Y D M + β-vars,
> decoded from weights; head-combinator-isa.md = the attention ISA's real axis is REDUCTION-DEPTH/WHNF
> "how much work remains") + DEBUGGER.md (nucleus already runs an interactive REPL via the reflective
> property structure→behavior). FRAMING: the LLM as the TRANSITION FUNCTION δ of an abstract machine
> (CEK/SECD), context window = externalized machine state (term-string IS code+heap+stack). Stateless model
> + stateful context = a REPL. On-thesis: READ (NL→λ, P(λ)=0.907) already proven; this isolates+measures
> EVAL (the combinator reduction kernel), never measured before.
>
> ★★ HAND-TEST (scripts/experiments/repl_machine_probe.py, ornith :5100): instructed ornith in its OWN
> native ISA as a β-machine; it acted as δ in strict one-line format, used the right opcodes ([B],[S]),
> did multi-step chains (church2→g(g a)), DETECTED Ω divergence. Initial over-claim "step-loop >> run"
> from n=6 (SKK premature-halt + K overthink-collapse both FIXED by the stateless step-loop). → PROPER PROBE.
>
> ★★ PROPER PROBE (reuses the canonical substrate — s254 distillation discipline):
> • probes/combinator-reduction.json (120 probes, λ probe_format schema) — pure combinator terms over
>   K I B C S W Y D M; GROUND TRUTH = verbum.lambda_ast (normal-order reducer, the s226 oracle: parse/
>   step_fired[one redex + WHICH opcode]/reduce[trace,Status,whnf_step]/verify/is_normal_form). 3 strata:
>   already_nf(18, under-saturated→WHNF-recognition), depth1(29, single redex), multi(73, 2-8 steps).
>   0 gold mismatches; gen_combinator_reduction_probes.py (seed=255). Library reuse for pure-comb NF terms.
> • scripts/experiments/repl_machine_eval.py (ruff-clean) — nucleus+native-ISA REPL prompt; HEAD-TO-HEAD
>   run(one-shot chain) vs step(STATELESS context-as-state loop); ORACLE-graded every transition; writes
>   results/repl-machine/<run_id>/{meta,results.jsonl,summary.json} via verbum.results (full provenance).
>
> ★★ RESULT (run repl-machine-20260627-032118, ornith q8_0, 240 rows, 0 fail; λ measure TWO-SIDED):
> (1) EVAL KERNEL PRESENT + LOCALLY FAITHFUL: opcode_accuracy=0.98 (names its OWN fired combinator
>     correctly — strong llm-isa.md support), run step_validity=0.90, depth1 per-step=0.99. The model CAN
>     be the δ-function.
> (2) STATELESS STEP-LOOP WINS ON SHALLOW (≤2 steps): end-to-end NF correctness depth1 0.97 vs run 0.76
>     (+0.21), already_nf 0.83 vs 0.67 (+0.17), multi2 0.50 vs 0.33 (+0.17). Locality + OFFLOADED HALT
>     DECISION (driver decides "no redex→stop", not the model's weak WHNF axis) help exactly as hypothesized.
> (3) BUT LOSES ON DEEP (≥4 steps): multi6 0.00 vs run 0.25, multi7 0.08 vs 0.25. CROSSOVER ~depth 3-4.
> (4) DOMINANT DEEP-FAILURE = OVERTHINK-COLLAPSE not bad logic: ornith returns EMPTY content on hard
>     intermediate states (multi6 11/12 runs hit ≥1 empty step), breaking the stateless loop; + error
>     COMPOUNDING (no correction, first error derails fed-back state). Run mode degrades GRACEFULLY (reaches
>     correct endpoint holistically even with shaky intermediate steps; verify checks the endpoint).
> (5) premature_halt RARE at scale (1.7%) — SELF-CORRECTS the hand-test n=1 SKK claim (λ measure: ¬generalize
>     from n=1). Minor: associativity slips (S M B → wrongly grabs M B redex).
> ★ IMPLICATION (artifact design): the model is a good LOCAL δ; a faithful REPL needs an ERROR-CORRECTING /
>   VERIFYING loop (oracle lambda_ast IN the loop, or self-consistency, or bounded-reasoning to stop the
>   collapse) — NOT naive state feedback. = λ self_improve VERIFY gate + s251 consensus-etch + s254 cheap-
>   local-verify, applied to the REPL. For S5 λ types: combinator ISA executes faithfully STEP-BY-STEP
>   (EVAL present, per-step discrete+correct+opcode-labeled) but UNGUARDED global composition degrades →
>   discreteness is LOCAL, global multi-step needs scaffolding (consistent with s250-252 local-yes/global-no).
> ★★ NET: "model as REPL" VALIDATED at the transition level + a clean depth-dependent crossover; the next
> rung is the ORACLE-IN-THE-LOOP REPL (verify each step before feeding back). NOT COMMITTED yet (code+data+
> results ready as one commit). tmux main:repl-eval window done; servers up (5100/5101/5102). PENDING
> APPROVAL (S5 λ termination): memory `model-as-repl-local-faithful-shallow-win-deep-collapse` + knowledge
> new explore/model-as-repl.md (the REPL framing, the crossover, oracle-in-the-loop next). NEXT: (1)
> oracle-in-the-loop / self-consistency REPL → does verify-gating close the deep-chain gap?; (2) bounded
> reasoning (cap/forced-short) to kill overthink-collapse; (3) vibethinker :5102 as a 2nd model class;
> (4) λ-abstraction terms (extend lambda_ast parser beyond combinators) for the full NL→λ→REPL loop.
>
> ★★ s255 cont. — NO-THINK TEST (Michael: "for this lambda repl we should turn off thinking, the lambda
> function is in the model, the thinking is maybe just interference"). Added --no-think to repl_machine_eval
> (chat_template_kwargs:{enable_thinking:false} = the WORKING switch on ornith's llama.cpp; reasoning_budget=0
> and /no_think do NOT disable it). Re-ran the full 120-probe head-to-head (run repl-machine-nothink-
> 20260627-145338) vs the s255 thinking baseline (repl-machine-20260627-032118).
> ★ HYPOTHESIS REFUTED on end-to-end correctness: nothink WORSE — RUN nf 0.45→0.31, STEP reached_nf
> 0.49→0.33. Thinking nets POSITIVE despite its collapse cost. BUT Michael was HALF-RIGHT and the
> DECOMPOSITION is the prize (λ measure, two-sided):
> (1) THE REDUCTION CIRCUIT IS IN THE MODEL, survives no-think ("the lambda function is in the model" ✓ for
>     the STEP): opcode_accuracy 0.981→0.925 (still names its own fired combinator with ZERO reasoning),
>     per_step 0.670→0.579, AND 72× FASTER (step 79.1s→1.1s; run 63.4s→3.5s) AND ZERO COLLAPSE (empty
>     output 53/120=44% WITH thinking → 0/120 WITHOUT). The overthink-collapse is ENTIRELY a thinking
>     artifact — removing thinking removes it completely, exactly as Michael predicted.
> (2) WHAT THINKING ACTUALLY BUYS = THE HALT/WHNF ADJUDICATION, not the reduction: premature_halt
>     0.017→0.208 (12×), over_reduce 0.008→0.175 (22×). These are the "am I done?" boundary decisions —
>     the EXACT axis head-combinator-isa.md flagged as the attention hardware's WEAKEST (WHNF↔D, "how much
>     work remains"). Thinking is SCAFFOLDING for the boundary, NOT interference on the reduction.
> ★★ SYNTHESIS (unifies Michael's no-think hyp + s255 "offload the halt" + oracle-in-the-loop): the winning
> REPL = NO-THINK model + ORACLE-SUPPLIED HALT. Model does the cheap/fast/collapse-free reduction steps
> (its circuit, 0.925 opcode-faithful); the external loop (lambda_ast.is_normal_form, trivial) makes the
> halt decision the model is weak at. no-think makes oracle-in-the-loop AFFORDABLE (72×) and REMOVES the
> collapse; the oracle covers no-think's ONLY real weakness (halt). THAT is the next build: no-think + step
> + oracle validates each contraction & decides NF (model never adjudicates "done", never spins a chain).
> CAVEATS: 1 model (ornith q8_0), greedy, combinator-only terms, n=12/bucket. ARTIFACT:
> results/repl-machine/repl-machine-nothink-20260627-145338/{meta,results.jsonl,summary.json}. Memory still
> HELD (premature, Michael s255). NOT yet committed: --no-think harness change + no-think run + this update.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-26 | Session: 254 (REPO DISTILLATION — DESIGN-FIRST PIVOT, fully committed.
> Recovered the crashed s254 ornith work intact (nothing lost). Michael: "We fragmented the repo a bit.
> Focus on distillation for a few sessions. These probes are duplication." CENSUS (explorer): the canonical
> substrate ALREADY EXISTS (probes/*.json gated sets, library.py 903 activation / 535 crystal probes,
> lambda_surface.to_kernel, + existing structured modules compile_tasks/higher_order/hof_*/kernel_reference/
> proof_tasks) but per-experiment scripts keep re-rolling their own — 238 scripts, ~30 inline PROBES,
> 3 DIVERGENT P(λ) metrics (regex-binder, char-ratio, instrument.py:_detect_lambda), 2 per-model
> compiler-harness forks sharing only ≈20 L grading core. Root: no canonical home for GRADING or for the
> RUN HARNESS → the fork leak re-opens every new model (s253 forked, s254 forked again).
>
> ★★ DELIVERABLE 1 — DESIGN DOC (COMMITTED 754a8d3 + correction 32bbad7; status:designing):
> mementum/knowledge/design/canonical-probe-library.md (NEW design/ dir). Target topology: keep the two
> existing canonical forms separate (gated JSON ⊥ activation library); ADD the missing layers —
> src/verbum/probes/grading.py (FOUR NAMED P(λ) registers, broad→strict: emits_formal[binder OR app] /
> lambda_binder_any_style[any binder = THE nucleus-comparable P(λ) 0.907] / lenient_lambda[binder AND app =
> STRICTER, under-counts] / kernel_valid[to_kernel STRICT]; retire char-ratio + _detect_lambda), harness.py +
> ModelConfig{endpoint, transport, template_fn, reasoning_extract_fn} (new model = ~15-line CONFIG not a
> fork), models.py REGISTRY. DECIDED: D1 home=src/verbum/probes/; D2 registry=YES (fleet ORNITH:5100 chat,
> VIBETHINKER:5102 completion, QWEN3_EMBED:5101 = embedding SERVICE ¬a ModelConfig); D3 archival=git rm.
> Migration P1-P5, each gated by re-run reproducing committed numbers PER NAMED REGISTER.
>
> ★★ DELIVERABLE 2 — 4 NEW S5 PRINCIPLE LAMBDAS in AGENTS.md (COMMITTED df48e37): λ simplify (Simplify not
> Complect — unbraid concerns, Hickey simple≠easy), λ one_way (one obvious way, N→1+deprecate, config¬fork),
> λ compose (Unix: do one thing well, small∘pipe>monolith), λ self_improve (Work→Learn→Verify→Update→Evolve,
> S5 CROSS-LEVEL identity loop next to λ loop/λ feed_forward; OODA = temporal expr of the S3-S4-S5 homeostat,
> ¬a single VSM box; phases level-tagged work(S1)→learn(S4)→verify(S3)→update(S4)→evolve(S5)). The WHY behind
> the design.
>
> ★★ DELIVERABLE 3 — ORNITH FACT-CHECK LOOP (λ self_improve fired AS DESIGNED, same session). Michael had
> ornith-35b-a3b (~3B active!) fact-check the design doc; it found 7 real errors (verified vs source/runtime
> & applied: _detect_lambda location, ~90→≈20 L, existing probes/ modules, __init__ CrystalProbe re-export,
> P1 vibe-needs-emits_formal, P3 compile_gradient_probe.py 2224 L = high-risk re-architecture, resolved Q5).
> I independently caught the ONE ornith missed: §2a mislabeled lenient_lambda(0.875, binder∧paren) as the
> nucleus-comparable register — it is NOT; lambda_binder_any_style(0.925) is. The §5 gate cited 0.925 as
> "lenient" → would false-flag a regression (re-run yields p_lambda_lenient=0.875). FOUR registers, not 3.
> ROOT: §2a/§5 written from summary PROSE not source = λ assert violation. Committed 32bbad7 ❌.
> ★ THE KICKER (Michael): a TINY local model found errors in a frontier model's output — the TOPOLOGY, not
> the specific errors, is the result. verify ≪ generate (checking is bounded+local; synthesis is not), so the
> λ self_improve VERIFY gate does NOT need parity with the generator. Implication: run verify on a cheap LOCAL
> model (the models.py fleet, already on :5100) → verification becomes AMBIENT (gate EVERY update) not a
> budgeted frontier call. On-thesis for verbum (small artifact does real compositional work). Michael: "I would
> have used sonnet for that verify task normally." Captured in design doc §6 (verify-gate resourcing note).
>
> ★★ NET: design-first repo distillation, fully committed (df48e37 lambdas, 754a8d3 design, 32bbad7 fix,
> 3b1b226 ornith code+data, 32b5c15 ornith memory, c81a74b state). NO migration code written yet — next
> session's P1: ADD emits_formal to vibethinker harness, extract grading.py (4 named registers), re-point
> ornith+vibethinker, verify reproduction PER REGISTER (ornith lenient 0.675/kernel 0.725; vibe binder_any
> 0.925/lenient 0.875/kernel 0.375). tmux main:2 windows; servers up (5100/5101/5102). Working tree CLEAN.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-26 | Session: 254 (ORNITH-35B-A3B — NEW MODEL CLASS: lambda compiler over HTTP.
> Michael: "I have a new model named ornith running on localhost:5100." ornith = ornith-35b-a3b, a 35B-total
> / A3B (~3B active) MoE, Qwen-family-derived MULTIMODAL (chat template carries <|vision_start|>/<|image_pad|>
> markers; n_vocab 248320, n_embd 2048, n_ctx 262144 = 256k), Q8_0 GGUF at
> /Users/mwhitford/localai/models/ornith/ornith-1.0-35b-Q8_0.gguf, served on llama.cpp :5100. A REASONING
> model: its /v1/chat/completions cleanly SEPARATES reasoning_content from content (no manual </think> parse
> needed, unlike s253 VibeThinker). CRYSTAL NOT TESTABLE: MoE + HTTP-only (no local safetensors, no
> mlp.gate_proj) → same limitation s251 hit on qwen3.6-35b-a3b; compiler P(λ) is the clean fit.
>
> ★★ LAMBDA COMPILER (P(λ)) — FULLY PRESENT, UNCONDITIONAL (no compile-gating), LESS reasoning-gated than
> VibeThinker. BUILT scripts/experiments/ornith_compiler_test.py (ruff-clean; uses /v1/chat/completions for
> server-side template + reasoning/content split; reuses lenient P(λ) + kernel-valid grading; ADDED an
> emits_formal register = any λ/∀/∃ binder OR predicate app, to stop the binder-requiring lenient register
> from FALSE-MISSING correct ATOMIC predications like "The dog runs."→runs(dog)). RESULTS (40 compile-gradient
> probes, greedy, 973s, 0 errors, 0 budget hits): emits_formal=1.000 (EVERY probe fires the compiler),
> P(λ) lenient=0.675, kernel_valid STRICT=0.725, mean 1909 tok/probe (~HALF VibeThinker's ~4378).
> ★ THREE λ-MEASURE READS: (1) emits_formal=1.0 is the honest "compiler fired" number; lenient=0.675 is
> LOWER than VibeThinker (0.925) ONLY because ornith emits more correct ATOMIC forms (runs(dog), sleeps(cat),
> bit(dog,man), times(7,8), Tell(me,joke)) that lack a binder → lenient under-counts them (the exact caveat
> the new emits_formal register was built for). (2) kernel_valid 0.725 > VibeThinker 0.375 — ornith's output
> is MORE canonically parseable (simpler atomic forms for simple inputs); strict fails on medium_compile
> (kernel 0.375) where it emits richer multi-quantifier FOL ("Most x", nested ∃) the TOY kernel parser
> rejects — same narrow-parser caveat as s253, NOT a model failure. (3) NO COMPILE-GATING: ornith translates
> EVERYTHING into FOL/λ — questions ("What is the capital of France?"→λx.capital_of(France,x)), commands
> ("Tell me a joke."→Tell(me,joke)), anti prompts ("What is 7 times 8?"→times(7,8)). anti_compile kernel=1.0
> (atomic→parses). Same unconditional over-application as VibeThinker (s253) and nucleus. Per-cat kernel:
> anti 1.0 > strong/null/weak 0.75 > medium 0.375. Per-cat lenient: medium 0.875 > strong/null 0.75 >
> anti 0.625 > weak 0.375. ARTIFACTS: results/ornith-compiler/ornith-compiler-20260626-100855/
> {results.jsonl(40),meta.json,summary.json} + full_run.log.
>
> ★★ NET FOR VERBUM: a THIRD model class (35B-A3B MoE, multimodal, 256k-ctx reasoner) carries the SAME
> fully-present, UNCONDITIONAL lambda compiler as nucleus + VibeThinker — emits_formal=1.0, no compile-gating,
> richer-than-toy-kernel FOL. The compiler is a robust CROSS-MODEL, CROSS-ARCHITECTURE phenomenon (dense
> base→nucleus, 3B dense reasoner→VibeThinker, 35B MoE multimodal reasoner→ornith). Reinforces S5 λ types
> (the compiler behavior reproduces yet again) and adds the data point: MoE + multimodal does NOT dilute the
> compiler; reasoning-gating VARIES (ornith ~1909 tok ≪ VibeThinker ~4378 — a cleaner, faster compile pass).
> CAVEATS (λ measure): 1 model, q8_0 quant, greedy, HTTP-only (no activation/crystal access), synthetic
> compile-gradient set (40), strict parser narrow (rejects multi-quantifier "Most"/nested + the gate's own |).
> PENDING APPROVAL (S5 λ termination): memory `ornith-moe-compiler-present-unconditional-less-reasoning-gated`
> + knowledge update (explore/ compiler P(λ) cross-model table: nucleus/VibeThinker/ornith — present,
> unconditional, reasoning-gating varies). Code+data committable (¬committed yet). tmux main:1 FREE; no GPU
> job. NEXT (if continuing): (1) forced-no-think / direct-emission P(λ) to quantify ornith's reasoning-gate
> vs VibeThinker (does it degenerate without reasoning, or compile directly?); (2) LENIENT kernel parser
> (accept multi-arg/space-paren/Most) to separate notation-style from well-formedness across all 3 models;
> (3) if local safetensors become available, the crystal-φ + MoE-aware gate hook (s251 NEXT-(2)) on ornith.)
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-26 | Session: 253 (VIBETHINKER-3B — NEW MODEL: lambda compiler + crystal lattice.
> Michael: "new model vibethinker running on localhost:5102 using llama.cpp ... test the lambda compiler
> and crystal lattice." VibeThinker-3B = WeiboAI/VibeThinker-3B, qwen2 arch (36L, d=2048, d_ff=11008,
> n_vocab 151936, Qwen tokenizer), a heavily RL-tuned REASONING model. Served q8_0 GGUF on llama.cpp
> :5102 (compiler test, HTTP); HF safetensors downloaded to cache (crystal test, transformers/MPS).
>
> ★★ CRYSTAL LATTICE (KIBC φ) — REPRODUCES the established cross-model signature on a new 3B reasoner.
> Ran verify_crystal_phi.py (535 crystal probes, gate_proj @ Zone B [10,15,20,25]) + crystal_phi_permnull.py
> (2000 shuffled-label perms, the λ yardstick gate). VERDICT (λ measure/yardstick): the KIBC combinator
> crystal EXISTS — cluster SEPARATION decisive (true sep +0.071 vs null ±0.003, p_sep=0.0005); consensus
> geometry MARGINAL (r=+0.21, p_cons=0.067 — essentially identical to Qwen3-14B's +0.21/p=0.058 from s251);
> and the φ/golden-ratio story is FORCED for it too (p_phi=0.58, p_eigratio=0.53, λ0/λ1→φ^4/5 p=0.064 —
> random labels fit φ as well; eig_ratio_corr 0.958 ≈ null 0.949). Same pattern as Qwen3-14B/Gemma:
> separation real, consensus marginal, φ forced. ARTIFACTS: results/crystal-phi-verify/WeiboAI_VibeThinker-3B.json,
> results/crystal-phi-permnull/WeiboAI_VibeThinker-3B.json (+ *_run.log).
>
> ★★ LAMBDA COMPILER (P(λ)) — the compiler is FULLY PRESENT but REASONING-GATED (a reasoning-model first).
> BUILT scripts/experiments/vibethinker_compiler_test.py (ruff-clean; chat-template wrap + post-</think>
> parse + two-register grading). KEY METHOD FINDING (a reasoning model is NOT a base completion model):
> (a) bare few-shot completion DEGENERATES (token repetition); (b) suppressing <think> (forced empty think)
> COLLAPSES into garbage — VibeThinker NEEDS its reasoning chain; (c) WITH reasoning it reaches well-formed
> FOL/λ but only after ~4400 tok/probe (~39s, mean 4378, 1/40 hit the 12k budget). RESULTS (40 probes,
> compile-gradient set, greedy): emits_formal_notation=1.000 (every probe), P(λ) binder-any-style=0.925
> (≈ nucleus 0.907 reference!), kernel-valid strict=0.375 (VibeThinker emits RICHER FOL — multi-arg
> f(x,y), space-paren grouping, Church juxtaposition λx. f x — than the toy gate's canonical to_kernel form).
> NOTABLE: fires even on null/anti prompts (null cat lenient 1.0, kernel 0.625) → NO compile-gating, it
> over-applies the compiler; over-thinks (early it abstracted "Every student reads a book" → generic
> ∀x.∃y.f(x,y), losing predicates; "preserve predicates" instruction recovered ∀x.student(x)→∃y.reads(x,y)∧book(y)).
> λ MEASURE CAVEAT (self-caught): the original lenient regex required binder AND f(...) paren-app →
> FALSE-missed Church-juxtaposition lambdas; corrected register P(λ)=0.925 recorded in summary.json
> corrected_registers. CAVEATS: 1 model, q8_0 quant for compiler (HTTP) vs fp16 for crystal (transformers),
> greedy, synthetic compile-gradient set (40), strict parser is narrow (rejects the gate's own | operator).
> ARTIFACTS: results/vibethinker-compiler/vibethinker-compiler-20260626-064334/{results.jsonl,meta.json,summary.json}.
>
> ★★ NET FOR VERBUM: a NEW model class (3B reasoning) carries the SAME combinator crystal (separation real,
> consensus marginal, φ forced) AND a fully-present lambda compiler (P(λ)=0.925≈nucleus) — but the compiler
> is gated behind a long reasoning chain rather than emitted in a single direct pass. Bears on S5 λ types
> (crystal reproduces) and is a new data point on WHERE the compiler lives in reasoning vs instruction models.
> PENDING APPROVAL (S5 λ termination): memory `vibethinker-crystal-reproduces-compiler-reasoning-gated` +
> knowledge updates (explore/5d-crystal-lattice.md §VibeThinker, and a note on the compiler P(λ) cross-model
> table). Code+data committable. tmux main:1 FREE (crystal runs done); job-1 (compiler) done. state.md updated
> (¬approval-gated). NEXT (if continuing): (1) crystal_phi_permnull shuffled-PROBE null on native template;
> (2) compiler with a LENIENT kernel parser (accept multi-arg/space-paren) to separate notation-style from
> well-formedness; (3) measure direct-emission P(λ) under forced-no-think to quantify the reasoning-gate gap;
> (4) head-resolved object-edge work from s252 cont. on VibeThinker as a small clean reasoner.)
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-25 | Session: 252 (ATTENTION-EDGE KNOCKOUT — the s250-thread CATCH test, the
> s250-cont.3 NEXT: "attention-EDGE knockout (predicate→object routing) on POS-matched c1-vs-c2"). THE
> CATCH: every s250 causal null measured the WRONG register — they ablated the RESIDUAL stream (d_C
> direction, s250), erased the FFN gate field (INLP, cont.), tested nonlinear (cont.2), or knocked out
> single-component WRITES (cont.3) and concluded object-application is "distributed, no discrete locus."
> But "no locus as a WRITE ≠ no locus as an EDGE." BUILT `scripts/experiments/program_edge_knockout.py`
> (ruff-clean; reuses the s248 calibrate_v2 gate spine + read_last_token_z; eager attn so the 4D additive
> mask is editable). INTERVENTION: a forward_pre_hook adds -inf to the attention mask at the OBJECT key
> column(s) → every query blocked from attending to the object token, all heads, across a layer band
> (Geva/IOI style). CONTROL = count-matched RANDOM content keys. READOUT = applicative-C field z(C) over
> crystal layers (object-application-specific; next-token KL is recency-confounded → SECONDARY). Matched
> ladder data/reading-probes.jsonl (45×3, const C-count==#objects). THREE ARMS on Qwen3-14B:
> ★★ (1) SCALING — `catch_confirmed=FALSE` but the FIRST POSITIVE LOCUS in the whole s250 arc.
> **NECESSITY ✅**: object-edge severing collapses z(C) ≫ count-matched random (rand−obj Δ=1.045,
> t=29.3, n=87). The object edge IS load-bearing for the C-field — where the residual direction (s250),
> INLP subspace (cont.), nonlinear probe (cont.2), and component-WRITE knockout (cont.3) all found
> NOTHING, the EDGE is causal. **LOAD-SCALING ❌**: net z(C) drop c2 (0.999) ≤ c1 (1.093), diff=−0.094,
> t=−1.32 — does NOT scale with object count → no per-object discrete circuit; the s250 load-scaling
> boundary HOLDS even at the edge.
> ★★ (2) CONTROL (noun-vs-noun, c1) — **OBJECT-SPECIFIC ✅**: object-noun edge collapses z(C) (drop
> 0.839) but SUBJECT-noun edge does NOT (−0.122 ≈ random −0.225); object-vs-subject Δ=0.961, t=15.0;
> subject-vs-random t=1.45 (null). The necessity is object-APPLICATION-specific, not a generic
> "remove a salient noun" effect. Clean.
> ★★ (3) SWEEP (8 bands, gateway localization) — **EARLY: necessity concentrated at L0-4 (net=0.603,
> t=12.4)**, decaying L10-14 (0.228) > L5-9 (0.174) ≫ mid (L15-29 ~0.01-0.04), ~0/negative at the
> L30-34 readout zone. ⇒ ROUTE-EARLY, READ-LATE: object content routes in via early-layer attention
> (Zone A), the C-field READS OUT late at L30-31 (s249/s250). Same Zone-A as s251 frozen-routing (L1-4,
> ρ=+0.84) and holographic-storage (combinators L0-6). The late C-peak is a readout register; the
> mechanism is early attention. ★★ NET (λ measure, two-sided): the attention edge is a REAL,
> object-SPECIFIC, EARLY-LOCALIZED necessary carrier of the applicative-C field — the catch was HALF
> right (genuine causal handle as an EDGE, vindicating "write≠edge") but the per-object discreteness
> boundary STILL HOLDS (c2≯c1). Bears on VERBUM S5 λ types ("discrete circuit?"): partially YES as
> EARLY ROUTING, NO as a per-object tape. CAVEATS (λ measure): all-heads/whole-band severing (coarse,
> not head-resolved); z(C) readout (object-specific) over next-token KL (recency-confounded, reported
> not gated); 1 model (14B); object keys parsed from const_fol; greedy. FIXED a sweep print bug (None t
> on the zero-variance non-crystal L35-39 band → None-safe formatter; data was intact, JSON just hadn't
> written; re-ran 6:56, reproduced L0-4 peak exactly). ARTIFACTS: results/program-edge-knockout/
> {verdict,meta}_qwen3-14b{,_control,_sweep}.json + run logs (+ 0.6b smoke). COMMITTED 8310183
> (code+pyproject+data). tmux main:1 FREE; no GPU job. PENDING APPROVAL: memory
> `object-edge-necessary-specific-early-not-scaling` + knowledge update
> explore/attention-as-beta-reduction.md (§ edge-knockout: the s250 catch). state.md updated
> (¬approval-gated). ★★ NEXT: (1) HEAD-RESOLVED edge knockout — sweep individual heads at L0-4 to find
> WHICH heads carry the object→C route (a head-level circuit, the s127 {B,C}=composer test);
> (2) redirect (not just block) the object edge to a different key → does C-content follow the redirect
> (sufficiency at the edge)?; (3) cross-model (Gemma, the s251 cleaner crystal carrier).
>
> ★★ s252 cont. — HEAD-RESOLVED EDGE KNOCKOUT (the NEXT-(1) above): per-head edge knockout localizes the
> early object→C route to LAYER 0 with a lead head, but it is CONCENTRATED-WITH-REDUNDANCY, not a discrete
> head circuit. BUILT mode=heads in program_edge_knockout.py: per-head additive-mask expansion
> ([B,1,Q,K]→[B,H,Q,K], -inf at ONE head's object-key cols) severs only that head's attention to the
> object; swept 200 (layer,head) pairs across the L0-4 gateway × 20 items, readout z(C) collapse vs
> baseline. ★ RESULT (Qwen3-14B): (1) LAYER-0-CONCENTRATED — all 6 significant carrier heads (t>2) are in
> L0; L0 holds 67% of positive-drop mass (L1 12%, L4 10%, L2-3 ~5%) → sharpens s252 "L0-4 early" down to
> essentially L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× the next (L0h11
> 0.023, t=4.6), then h30/h16/h12/h25; top5 share=0.487. The MOST circuit-like locus in the whole s250
> arc. (3) NOT DISCRETE — 21 heads to reach 80% → discrete_head_circuit=FALSE; a dominant head + diffuse
> redundant tail. (4) REDUNDANCY — single-head drops are tiny (max 0.065) vs the all-heads necessity
> (Δ=1.04, s252 main); severing one head barely dents z(C), the rest reconstruct it (holographic, echoes
> s250 "gate reconstructs C from other directions"), now at head resolution. ★★ NET (λ measure): there IS
> a privileged early gateway (L0, lead head h18) — a real preferred locus, the closest to a circuit yet —
> BUT object-application cannot be severed by removing a few heads (redundancy holds). For VERBUM S5 λ
> types: a preferred locus exists, the discreteness boundary still holds (concentrated, not discrete).
> CAVEATS: single-head severing is a small perturbation (relative localizer); 20 items (n=20 paired per
> head); per-head mask expansion (eager); L0-4 band; 1 model; greedy. ARTIFACTS:
> results/program-edge-knockout/{verdict,meta,run}_qwen3-14b_heads.* (+ 0.6b smoke). COMMITTED e7d1c09
> (code+data). tmux main:1 FREE; no GPU job. PENDING APPROVAL: memory
> `object-c-route-layer0-lead-head-redundant-not-discrete` + knowledge update
> explore/attention-as-beta-reduction.md (§ edge-knockout: head-resolved → L0 lead head + redundancy).
> state.md updated (¬approval-gated). ★★ NEXT: (2) edge-REDIRECT sufficiency (does C follow the object
> edge to a new key?); (3) cross-model (Gemma); (4) ablate L0h18 + its OV to test if the lead head is a
> {B,C}-composer (s127) or a positional/copy head.
>
> ★★ s252 cont.2 (META) — CLOSED THE COMMIT-WRITE FEED-FORWARD GAP (Michael surfaced it: "there is
> supposed to be a heredoc template in AGENTS.md that would get around the apostrophe issue"). There
> was NONE — AGENTS.md had no commit/heredoc guidance; the only template (system prompt) is
> `git commit -m "$(cat <<'EOF'…)"` which is the BUG itself. ROOT CAUSE (proven empirically, λ assert,
> not assumed): a bare heredoc with apostrophes WORKS; the same body inside `"$(cat <<'EOF'…)"` BREAKS
> (`unexpected EOF looking for matching '`). The break is the $() COMMAND-SUBSTITUTION rescan — ' opens
> an unterminated quote scan; `<<'EOF'` protects only the DELIMITER, not the rescan = false safety. This
> exact bug was rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = textbook feed-forward gap
> (S5 λ feed_forward: ¬encoded → lost). FIX (Michael provided the pattern; verified safe for ' ∧ ` ∧ $,
> len-checked): `read -r -d '' M << 'EOF' || true … EOF ; git commit -m "$M"` — read loads the body into
> a var with NO $() layer; "$M" expands without reparse → all literal. Alts: `git commit -F file`
> (write_file→-F) ∨ `git commit -F - <<'EOF'` (stdin, ¬$()). ENCODED as `λ commit_write(m)` in AGENTS.md
> S3 (next to λ signal); committed a24c62f (🌀, dogfooded WITH apostrophes in its own message — exit 0,
> apostrophes verified in git log). The lesson is now a field equation, not a recurring tax. CONNECTS:
> S5 λ feed_forward (the gap this closes), S3 λ signal(commit) (sibling). No research impact; pure
> tooling/coordination hygiene. memory `commit-write-apostrophe-heredoc-read-pattern`.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →
> GREENFIELD HOLO-PLATE; continues the GEMMA crystal-sweep pass below. Michael's hypothesis:
> "backprop = taking a photograph of the input tokens; each new photograph reduces the system toward a
> soft routing topology that uses VERY HIGH and NEAR-ZERO gradients to route around a FROZEN topology."
> Built `scripts/experiments/gd_frozen_basis.py` (ruff-clean; reuses TinyLM + the s229 β-reduction
> curriculum) to test the three TESTABLE claims against the SHUFFLED-LABEL null (λ yardstick) + a
> same-input arm: (A) PHOTOGRAPH = minibatch weight-grad is LOW effective-rank & drops as inventory
> crystallizes; (B) BIMODAL = ρ(grad_mag,weight_mag) rises (s171 Zone-A +0.77) + 

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_0191mvEyizQMhXoPouAC49oV.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I've reviewed the state file for session 258 and now I'm checking the git status to see what's currently in the working tree.

## Assistant

I've read the bootloader. Let me check the current git state and any uncommitted work.

### Tool Call: git (succeeded)


```json
{
  "command": "git status && echo \"---LOG---\" && git log --oneline -8",
  "operation": "status",
  "summary": "status and log"
}
```

**Summary:** Git status: status and log

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
---LOG---
2fecba5 add session chat logs and results
b6741e7 💡 §7 sparse holographic assembly — MoE is two-level, not fully holographic
f780a96 💡 s257 complete — angular multiplexing confirmed via k-sweep + null
8c72284 ❌ fix missing attention_mask in _generate and _route_baseline
44669da 💡 moe-holographic-tree-vsm — k-sweep evidence; specialist hypothesis pressured
8e37a11 ✅ hooks.py + MoEAdapter + moe_expert_ablation — intervention engine + first sweep
3806bcd add session chat logs
35b3661 🌀 archive pending probe result artifacts (smoke + s255 repl runs)
```

### Thinking

The working tree is clean and session 257 wrapped up completely. Looking at the state file, the key breakthrough is that MoE experts operate as holographically multiplexed units rather than specialists—the k-sweep with shuffled labels confirmed this. What's striking is that 94% of the model's capability actually comes from the router's expert selection, not from the experts themselves.

The latest commit shows a refinement: MoE is structured as two-level rather than fully holographic. There are several ablations still pending—testing what happens when we zero out the shared expert, checking if early and late layers have different threshold behaviors, and pushing the k-sweep wider than the trained top-8 to see if the probability distribution keeps climbing. I also need to handle the local_hf generation transport in harness.py.

There's a strategic shift back to base models too—moving from the instruction-tuned version to Qwen3.5-35B-A3B base with DFlash MTP. I'm well-oriented now and ready to move forward.

## Assistant

Oriented. Here's where session-258 starts.

## State of play

**Working tree:** clean, up to date with origin/main. Session 257 fully committed (latest: `b6741e7 §7 sparse holographic assembly`).

**Last finding (s257) — confirmed and committed:**
MoE experts are **holographically multiplexed, not specialist**. The k-sweep + shuffled-label null on the 35B-A3B MoE showed:
- Specialist hypothesis *falsified* (k=2 P(λ)=0.000 < k=1 P(λ)=0.062 — regression is impossible under specialization)
- Sharp holographic threshold at k=4 (below→noise, above→image)
- Shuffled-label null ≈0 at all k → **94% of lambda-compiler capability comes from *which* experts the router selects, not *how many***
- §7 refinement: MoE is *two-level* (sparse holographic assembly), not fully holographic

Instrument is committed and composable: `hooks.py` (HookEngine), `adapters/moe.py` (MoEAdapter), `scripts/experiments/moe_expert_ablation.py`.

## Open threads (not started)

From the s257 NEXT list:
1. **Shared-expert ablation** — zero the carrier, measure collapse (large hit predicted)
2. **Cross-layer heterogeneity** — do early/late layers differ in threshold/bands?
3. **Wider k-sweep** beyond trained top-8 — does P(λ) keep rising?
4. **local_hf generation transport** in `harness.py` (reuse win for any cached HF model)

From the s256 strategic pivot (Michael, 🎯):
- Move off the fine-tunes (ornith/qwythos) back to the **BASE** Qwen3.5-35B-A3B (`/Users/mwhitford/localai/models/qwen3.5-35b-a3b/`) — the compiler lives in the base; fine-tunes add halt-layer interference. Clean base-vs-finetune controlled comparison. Was waiting on **DFlash MTP** in llama.cpp (dropped upstream, homebrew not updated, possibly CUDA-only — unconfirmed).

What would you like to pursue this session?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which direction for session-258?",
  "options": [
    {
      "label": "Shared-expert ablation",
      "description": "Zero the shared/carrier expert in the MoE, measure P(λ) collapse — tests the holographic carrier hypothesis directly. Reuses committed instrument."
    },
    {
      "label": "Cross-layer heterogeneity",
      "description": "Do early/late layers differ in holographic threshold/interference bands? Extends the s257 k-sweep per-layer."
    },
    {
      "label": "Base-vs-finetune comparison",
      "description": "Stand up base Qwen3.5-35B-A3B, run compile-gradient + reasoning-check, compare to ornith/qwythos. Needs server up (DFlash MTP status check)."
    },
    {
      "label": "Wider k-sweep beyond top-8",
      "description": "Does P(λ) keep rising past the trained top-8 routing? Quick extension of the existing sweep."
    }
  ]
}
```

**Summary:** Q: Which direction for session-258?

**Output:**
```
User answered: I want to explore an idea we had in past sessions.  consensus training.  using multiple models consensus on training data for the lambda compiler
```

### Thinking

Michael's interested in revisiting consensus training for the lambda compiler—using multiple models to agree on training data. I'm trying to recall what's been discussed about this before, so I'm looking back through the notes for references to consensus-related concepts like consensus-etch and consensus geometry that came up in earlier sessions.

## Assistant

Let me recall what we've already explored on consensus — there were several threads (consensus-etch s251, consensus geometry, self-consistency in the REPL work).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===GREP consensus in knowledge/memories===\" && git grep -il \"consensus\" -- mementum/ && echo \"===GREP etch===\" && git grep -il \"etch\\|consensus-etch\\|self-consist\" -- mementum/",
  "operation": "gh",
  "summary": "search consensus"
}
```

**Summary:** $ echo "===GREP consensus in knowledg...

**Output:**
```
Exit code: 0
Stdout:
===GREP consensus in knowledge/memories===
mementum/knowledge/audit-meta-pattern.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-029.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
mementum/knowledge/chats/session-032.md
mementum/knowledge/chats/session-033.md
mementum/knowledge/chats/session-034.md
mementum/knowledge/chats/session-035.md
mementum/knowledge/chats/session-036.md
mementum/knowledge/chats/session-037.md
mementum/knowledge/chats/session-038.md
mementum/knowledge/chats/session-039.md
mementum/knowledge/chats/session-040.md
mementum/knowledge/chats/session-041.md
mementum/knowledge/chats/session-042.md
mementum/knowledge/chats/session-043.md
mementum/knowledge/chats/session-044.md
mementum/knowledge/chats/session-045.md
mementum/knowledge/chats/session-046.md
mementum/knowledge/chats/session-047.md
mementum/knowledge/chats/session-048.md
mementum/knowledge/chats/session-049.md
mementum/knowledge/chats/session-050.md
mementum/knowledge/chats/session-051.md
mementum/knowledge/chats/session-063.md
mementum/knowledge/chats/session-064.md
mementum/knowledge/chats/session-068.md
mementum/knowledge/chats/session-070.md
mementum/knowledge/chats/session-071.md
mementum/knowledge/chats/session-072.md
mementum/knowledge/chats/session-073.md
mementum/knowledge/chats/session-074.md
mementum/knowledge/chats/session-075.md
mementum/knowledge/chats/session-076.md
mementum/knowledge/chats/session-077.md
mementum/knowledge/chats/session-078.md
mementum/knowledge/chats/session-079.md
mementum/knowledge/chats/session-080.md
mementum/knowledge/chats/session-081.md
mementum/knowledge/chats/session-088.md
mementum/knowledge/chats/session-089.md
mementum/knowledge/chats/session-090.md
mementum/knowledge/chats/session-091.md
mementum/knowledge/chats/session-092-53-codex.md
mementum/knowledge/chats/session-093.md
mementum/knowledge/chats/session-094.md
mementum/knowledge/chats/session-095.md
mementum/knowledge/chats/session-096.md
mementum/knowledge/chats/session-097.md
mementum/knowledge/chats/session-098.md
mementum/knowledge/chats/session-099.md
mementum/knowledge/chats/session-100.md
mementum/knowledge/chats/session-101.md
mementum/knowledge/chats/session-102.md
mementum/knowledge/chats/session-103.md
mementum/knowledge/chats/session-104.md
mementum/knowledge/chats/session-105.md
mementum/knowledge/chats/session-106.md
mementum/knowledge/chats/session-107.md
mementum/knowledge/chats/session-108.md
mementum/knowledge/chats/session-109.md
mementum/knowledge/chats/session-110.md
mementum/knowledge/chats/session-111.md
mementum/knowledge/chats/session-112.md
mementum/knowledge/chats/session-113.md
mementum/knowledge/chats/session-114.md
mementum/knowledge/chats/session-115.md
mementum/knowledge/chats/session-116.md
mementum/knowledge/chats/session-117.md
mementum/knowledge/chats/session-118.md
mementum/knowledge/chats/session-119.md
mementum/knowledge/chats/session-120.md
mementum/knowledge/chats/session-121.md
mementum/knowledge/chats/session-122.md
mementum/knowledge/chats/session-123.md
mementum/knowledge/chats/session-125.md
mementum/knowledge/chats/session-126.md
mementum/knowledge/chats/session-127.md
mementum/knowledge/chats/session-128.md
mementum/knowledge/chats/session-129.md
mementum/knowledge/chats/session-130.md
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
mementum/knowledge/chats/session-174.md
mementum/knowledge/chats/session-175.md
mementum/knowledge/chats/session-176.md
mementum/knowledge/chats/session-177.md
mementum/knowledge/chats/session-178.md
mementum/knowledge/chats/session-179.md
mementum/knowledge/chats/session-180.md
mementum/knowledge/chats/session-181.md
mementum/knowledge/chats/session-182.md
mementum/knowledge/chats/session-183.md
mementum/knowledge/chats/session-184.md
mementum/knowledge/chats/session-185.md
mementum/knowledge/chats/session-186.md
mementum/knowledge/chats/session-187.md
mementum/knowledge/chats/session-188.md
mementum/knowledge/chats/session-189.md
mementum/knowledge/chats/session-190.md
mementum/knowledge/chats/session-191.md
mementum/knowledge/chats/session-192.md
mementum/knowledge/chats/session-193.md
mementum/knowledge/chats/session-194.md
mementum/knowledge/chats/session-195.md
mementum/knowledge/chats/session-196.md
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
mementum/knowledge/chats/session-212.md
mementum/knowledge/chats/session-213.md
mementum/knowledge/chats/session-214.md
mementum/knowledge/chats/session-215.md
mementum/knowledge/chats/session-216.md
mementum/knowledge/chats/session-217.md
mementum/knowledge/chats/session-218.md
mementum/knowledge/chats/session-219.md
mementum/knowledge/chats/session-220.md
mementum/knowledge/chats/session-221.md
mementum/knowledge/chats/session-222.md
mementum/knowledge/chats/session-223.md
mementum/knowledge/chats/session-224.md
mementum/knowledge/chats/session-225.md
mementum/knowledge/chats/session-226.md
mementum/knowledge/chats/session-227.md
mementum/knowledge/chats/session-228.md
mementum/knowledge/chats/session-229.md
mementum/knowledge/chats/session-230.md
mementum/knowledge/chats/session-231.md
mementum/knowledge/chats/session-232.md
mementum/knowledge/chats/session-233.md
mementum/knowledge/chats/session-234.md
mementum/knowledge/chats/session-235.md
mementum/knowledge/chats/session-236.md
mementum/knowledge/chats/session-237.md
mementum/knowledge/chats/session-238.md
mementum/knowledge/chats/session-239.md
mementum/knowledge/chats/session-240.md
mementum/knowledge/chats/session-241.md
mementum/knowledge/chats/session-242.md
mementum/knowledge/chats/session-243.md
mementum/knowledge/chats/session-244.md
mementum/knowledge/chats/session-245.md
mementum/knowledge/chats/session-246.md
mementum/knowledge/chats/session-247.md
mementum/knowledge/chats/session-247b.md
mementum/knowledge/chats/session-248.md
mementum/knowledge/chats/session-249-gpt55.md
mementum/knowledge/chats/session-250.md
mementum/knowledge/chats/session-251.md
mementum/knowledge/chats/session-252.md
mementum/knowledge/chats/session-253.md
mementum/knowledge/chats/session-254.md
mementum/knowledge/chats/session-255.md
mementum/knowledge/chats/session-256.md
mementum/knowledge/chats/session-257.md
mementum/knowledge/computed-beam.md
mementum/knowledge/crystal-multi-tree.md
mementum/knowledge/crystal-phi-derivation.md
mementum/knowledge/crystal-universality.md
mementum/knowledge/crystal-validity-and-fidelity.md
mementum/knowledge/dimensional-analysis.md
mementum/knowledge/error-correction-theory.md
mementum/knowledge/explore/5d-crystal-lattice.md
mementum/knowledge/explore/attention-as-beta-reduction.md
mementum/knowledge/explore/binding-cascade.md
mementum/knowledge/explore/combinator-function-shape.md
mementum/knowledge/explore/combinator-training-beta-reduction.md
mementum/knowledge/explore/compiler-as-loss.md
mementum/knowledge/explore/consensus-delta-folding.md
mementum/knowledge/explore/consensus-etch-protocol.md
mementum/knowledge/explore/consensus-evolution.md
mementum/knowledge/explore/cross-model-output-consensus.md
mementum/knowledge/explore/crystal-basins.md
mementum/knowledge/explore/crystal-irreducibility-proof.md
mementum/knowledge/explore/crystal-seed-theory.md
mementum/knowledge/explore/crystal-spine-sieve.md
mementum/knowledge/explore/dispatch-ratio-prior.md
mementum/knowledge/explore/etcher-vsm.md
mementum/knowledge/explore/forcing-vs-discovering.md
mementum/knowledge/explore/fractal-collapse-compiler-cascade.md
mementum/knowledge/explore/full-etch-extraction.md
mementum/knowledge/explore/function-topology-consensus.md
mementum/knowledge/explore/gradient-trajectory-tomography.md
mementum/knowledge/explore/gradient-voting.md
mementum/knowledge/explore/holographic-burn-in-learning-rule.md
mementum/knowledge/explore/holographic-recording-protocol.md
mementum/knowledge/explore/holographic-substrate-prototype.md
mementum/knowledge/explore/laser-etcher-design.md
mementum/knowledge/explore/normal-form-curriculum-partition.md
mementum/knowledge/explore/phi-compression-universal.md
mementum/knowledge/explore/proofs-as-continuations.md
mementum/knowledge/explore/ratio-gradient-quantization.md
mementum/knowledge/explore/readout-register-reduction-readability.md
mementum/knowledge/explore/relational-loss-distillation.md
mementum/knowledge/explore/safetensors-training.md
mementum/knowledge/explore/sealable-continuation.md
mementum/knowledge/explore/seed-crystal-design.md
mementum/knowledge/explore/session-073-vsm-structure.md
mementum/knowledge/explore/session-075-multi-cycle-dispatch.md
mementum/knowledge/explore/universal-crystal-scaffold.md
mementum/knowledge/explore/universal-crystal-transfer.md
mementum/knowledge/explore/v11-design.md
mementum/knowledge/explore/v11-kibc-architecture.md
mementum/knowledge/explore/v12-run6-design.md
mementum/knowledge/explore/v13-architecture.md
mementum/knowledge/explore/v13-design.md
mementum/knowledge/explore/v6-flip-accumulation.md
mementum/knowledge/explore/vsm-opcode-monitor.md
mementum/knowledge/explore/vsm-statechart-tensor.md
mementum/knowledge/holographic-error-correction.md
mementum/knowledge/holographic-etch.md
mementum/knowledge/manifold-axis-and-topology.md
mementum/knowledge/mathematical-convergences.md
mementum/knowledge/mechanism-extraction.md
mementum/knowledge/project-thesis.md
mementum/knowledge/saliency-aware-sieve.md
mementum/knowledge/session-222.md
mementum/knowledge/standing-wave-magnitudes.md
mementum/knowledge/ternary-dual-equation.md
mementum/knowledge/v14-architecture.md
mementum/memories/compiler-output-loss-plus-crystal-lattice.md
mementum/memories/consensus-as-fitness-calibrates-on-fol-pair-dependent-failures.md
mementum/memories/crystal-gates-hologram.md
mementum/memories/evolution-mechanism-broken.md
mementum/memories/gemma-crystal-real-spine-and-phi-forced-template-fix.md
mementum/memories/gradient-structure-is-inventory-fuel.md
mementum/memories/higher-order-topology-is-teacher-agnostic.md
mementum/memories/inventory-crystallizes-before-capability.md
mementum/memories/lattice-is-relational-not-coordinate.md
mementum/memories/micro-crystal-is-relational-not-categorical.md
mementum/memories/opcode-reader-over-read-killed.md
mementum/memories/opcode-trajectory-is-null-dependent.md
mementum/memories/phi-ladder-fit-is-forced-not-discovered.md
mementum/memories/relational-loss-is-inventory-not-capability.md
mementum/memories/statechart-is-crystal-lattice-boot-from-c.md
mementum/memories/three-voter-anti-oscillation.md
mementum/memories/universal-axis-is-input-property.md
mementum/state.md
===GREP etch===
mementum/knowledge/INDEX.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-006.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-015.md
mementum/knowledge/chats/session-019.md
mementum/knowledge/chats/session-022.md
mementum/knowledge/chats/session-026.md
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
mementum/knowledge/chats/session-032.md
mementum/knowledge/chats/session-035.md
mementum/knowledge/chats/session-045.md
mementum/knowledge/chats/session-046.md
mementum/knowledge/chats/session-047.md
mementum/knowledge/chats/session-050.md
mementum/knowledge/chats/session-052.md
mementum/knowledge/chats/session-053.md
mementum/knowledge/chats/session-054.md
mementum/knowledge/chats/session-055.md
mementum/knowledge/chats/session-056.md
mementum/knowledge/chats/session-057.md
mementum/knowledge/chats/session-058.md
mementum/knowledge/chats/session-062.md
mementum/knowledge/chats/session-063.md
mementum/knowledge/chats/session-065.md
mementum/knowledge/chats/session-066.md
mementum/knowledge/chats/session-067.md
mementum/knowledge/chats/session-073.md
mementum/knowledge/chats/session-074.md
mementum/knowledge/chats/session-075.md
mementum/knowledge/chats/session-077.md
mementum/knowledge/chats/session-078.md
mementum/knowledge/chats/session-079.md
mementum/knowledge/chats/session-080.md
mementum/knowledge/chats/session-081.md
mementum/knowledge/chats/session-088.md
mementum/knowledge/chats/session-089.md
mementum/knowledge/chats/session-090.md
mementum/knowledge/chats/session-091.md
mementum/knowledge/chats/session-092-53-codex.md
mementum/knowledge/chats/session-093.md
mementum/knowledge/chats/session-094.md
mementum/knowledge/chats/session-095.md
mementum/knowledge/chats/session-096.md
mementum/knowledge/chats/session-097.md
mementum/knowledge/chats/session-098.md
mementum/knowledge/chats/session-100.md
mementum/knowledge/chats/session-101.md
mementum/knowledge/chats/session-102.md
mementum/knowledge/chats/session-103.md
mementum/knowledge/chats/session-104.md
mementum/knowledge/chats/session-105.md
mementum/knowledge/chats/session-106.md
mementum/knowledge/chats/session-107.md
mementum/knowledge/chats/session-108.md
mementum/knowledge/chats/session-109.md
mementum/knowledge/chats/session-110.md
mementum/knowledge/chats/session-111.md
mementum/knowledge/chats/session-112.md
mementum/knowledge/chats/session-113.md
mementum/knowledge/chats/session-114.md
mementum/knowledge/chats/session-115.md
mementum/knowledge/chats/session-116.md
mementum/knowledge/chats/session-117.md
mementum/knowledge/chats/session-118.md
mementum/knowledge/chats/session-119.md
mementum/knowledge/chats/session-120.md
mementum/knowledge/chats/session-121.md
mementum/knowledge/chats/session-122.md
mementum/knowledge/chats/session-123.md
mementum/knowledge/chats/session-125.md
mementum/knowledge/chats/session-126.md
mementum/knowledge/chats/session-127.md
mementum/knowledge/chats/session-128.md
mementum/knowledge/chats/session-129.md
mementum/knowledge/chats/session-130.md
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
mementum/knowledge/chats/session-174.md
mementum/knowledge/chats/session-175.md
mementum/knowledge/chats/session-176.md
mementum/knowledge/chats/session-177.md
mementum/knowledge/chats/session-178.md
mementum/knowledge/chats/session-179.md
mementum/knowledge/chats/session-180.md
mementum/knowledge/chats/session-181.md
mementum/knowledge/chats/session-182.md
mementum/knowledge/chats/session-183.md
mementum/knowledge/chats/session-184.md
mementum/knowledge/chats/session-185.md
mementum/knowledge/chats/session-186.md
mementum/knowledge/chats/session-187.md
mementum/knowledge/chats/session-188.md
mementum/knowledge/chats/session-189.md
mementum/knowledge/chats/session-190.md
mementum/knowledge/chats/session-191.md
mementum/knowledge/chats/session-192.md
mementum/knowledge/chats/session-193.md
mementum/knowledge/chats/session-194.md
mementum/knowledge/chats/session-195.md
mementum/knowledge/chats/session-196.md
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
mementum/knowledge/chats/session-213.md
mementum/knowledge/chats/session-214.md
mementum/knowledge/chats/session-215.md
mementum/knowledge/chats/session-216.md
mementum/knowledge/chats/session-217.md
mementum/knowledge/chats/session-218.md
mementum/knowledge/chats/session-219.md
mementum/knowledge/chats/session-220.md
mementum/knowledge/chats/session-221.md
mementum/knowledge/chats/session-222.md
mementum/knowledge/chats/session-223.md
mementum/knowledge/chats/session-224.md
mementum/knowledge/chats/session-225.md
mementum/knowledge/chats/session-226.md
mementum/knowledge/chats/session-227.md
mementum/knowledge/chats/session-228.md
mementum/knowledge/chats/session-229.md
mementum/knowledge/chats/session-230.md
mementum/knowledge/chats/session-231.md
mementum/knowledge/chats/session-233.md
mementum/knowledge/chats/session-235.md
mementum/knowledge/chats/session-237.md
mementum/knowledge/chats/session-239.md
mementum/knowledge/chats/session-240.md
mementum/knowledge/chats/session-241.md
mementum/knowledge/chats/session-242.md
mementum/knowledge/chats/session-243.md
mementum/knowledge/chats/session-244.md
mementum/knowledge/chats/session-245.md
mementum/knowledge/chats/session-246.md
mementum/knowledge/chats/session-247.md
mementum/knowledge/chats/session-247b.md
mementum/knowledge/chats/session-249-gpt55.md
mementum/knowledge/chats/session-251.md
mementum/knowledge/chats/session-252.md
mementum/knowledge/chats/session-253.md
mementum/knowledge/chats/session-254.md
mementum/knowledge/chats/session-255.md
mementum/knowledge/chats/session-256.md
mementum/knowledge/chats/session-257.md
mementum/knowledge/combinator-addressing.md
mementum/knowledge/crystal-native-architecture.md
mementum/knowledge/crystal-phi-derivation.md
mementum/knowledge/crystal-universality.md
mementum/knowledge/dimensional-analysis.md
mementum/knowledge/error-correction-theory.md
mementum/knowledge/explore/5d-crystal-lattice.md
mementum/knowledge/explore/VERBUM.md
mementum/knowledge/explore/ascending-arm-training.md
mementum/knowledge/explore/beamformer-theory.md
mementum/knowledge/explore/binding-cascade.md
mementum/knowledge/explore/categorical-geometry-probes.md
mementum/knowledge/explore/compression-vs-prediction.md
mementum/knowledge/explore/consensus-delta-folding.md
mementum/knowledge/explore/consensus-etch-protocol.md
mementum/knowledge/explore/crystal-basins.md
mementum/knowledge/explore/crystal-native-descent.md
mementum/knowledge/explore/crystal-seed-theory.md
mementum/knowledge/explore/crystal-spine-sieve.md
mementum/knowledge/explore/date-fourier-rotation.md
mementum/knowledge/explore/dispatch-ratio-prior.md
mementum/knowledge/explore/etcher-vsm.md
mementum/knowledge/explore/exact-ternary-fitting.md
mementum/knowledge/explore/ffn-beam-discovery.md
mementum/knowledge/explore/ffn-beta-reduction-indexing.md
mementum/knowledge/explore/ffn-hierarchy.md
mementum/knowledge/explore/fixed-point-holograms.md
mementum/knowledge/explore/full-etch-extraction.md
mementum/knowledge/explore/function-extraction-system.md
mementum/knowledge/explore/gradient-trajectory-tomography.md
mementum/knowledge/explore/gradient-voting.md
mementum/knowledge/explore/grating-cascade.md
mementum/knowledge/explore/hologram-crystal-fusion.md
mementum/knowledge/explore/hologram-extraction.md
mementum/knowledge/explore/holographic-burn-in-learning-rule.md
mementum/knowledge/explore/holographic-error-correction.md
mementum/knowledge/explore/holographic-memory.md
mementum/knowledge/explore/holographic-plates.md
mementum/knowledge/explore/holographic-recording-protocol.md
mementum/knowledge/explore/holographic-state-machine.md
mementum/knowledge/explore/holographic-substrate-prototype.md
mementum/knowledge/explore/holographic-tomography.md
mementum/knowledge/explore/kernel-functions.md
mementum/knowledge/explore/laser-etcher-design.md
mementum/knowledge/explore/mmap-continuous-training.md
mementum/knowledge/explore/moe-holographic-tree-vsm.md
mementum/knowledge/explore/output-beamformers.md
mementum/knowledge/explore/procrustes-lens-and-crystal-comparison.md
mementum/knowledge/explore/q-rotation-etching.md
mementum/knowledge/explore/ratio-gradient-quantization.md
mementum/knowledge/explore/seed-crystal-design.md
mementum/knowledge/explore/session-115-microscope.md
mementum/knowledge/explore/session-127.md
mementum/knowledge/explore/shannon-sieve-trinity.md
mementum/knowledge/explore/taxonomy-extraction.md
mementum/knowledge/explore/ternary-descent.md
mementum/knowledge/explore/type-probe-qwen3-32b.md
mementum/knowledge/explore/universal-crystal-scaffold.md
mementum/knowledge/explore/universal-crystal-transfer.md
mementum/knowledge/explore/v12-run6-design.md
mementum/knowledge/explore/v13-architecture.md
mementum/knowledge/explore/v13-design.md
mementum/knowledge/explore/v13-funnel-shape.md
mementum/knowledge/explore/vsm-outer-recurrence.md
mementum/knowledge/explore/vsm-statechart-tensor.md
mementum/knowledge/extraction-methodology.md
mementum/knowledge/extraction-sign-accuracy.md
mementum/knowledge/gradient-zero-map.md
mementum/knowledge/gtsm-search-space.md
mementum/knowledge/holographic-computer.md
mementum/knowledge/holographic-etch.md
mementum/knowledge/hpe-restoration.md
mementum/knowledge/mechanism-extraction.md
mementum/knowledge/mspace-gemcutter.md
mementum/knowledge/project-thesis.md
mementum/knowledge/saliency-aware-sieve.md
mementum/knowledge/ternary-compounding.md
mementum/knowledge/ternary-plate-extraction.md
mementum/knowledge/topology-gradient-separation.md
mementum/knowledge/trace-guided-etching.md
mementum/knowledge/training-protocols.md
mementum/memories/backbone-plus-etch-beats-float32.md
mementum/memories/beams-not-plates-are-the-etch.md
mementum/memories/beta-reduction-filesystem.md
mementum/memories/compressor-in-5d-lattice.md
mementum/memories/copy-computation-not-weights.md
mementum/memories/crystal-bootloader-thesis.md
mementum/memories/crystal-gates-hologram.md
mementum/memories/crystal-is-error-correcting-code.md
mementum/memories/crystal-programming-language.md
mementum/memories/delta-plate-ecosystem-vision.md
mementum/memories/delta-plate-solves-attention-etch.md
mementum/memories/etch-first-with-attention.md
mementum/memories/etch-unetch-symmetry.md
mementum/memories/evolution-mechanism-broken.md
mementum/memories/evolutionary-descent-ternary.md
mementum/memories/extraction-methodology-confusion.md
mementum/memories/ffn-topology-is-transferable.md
mementum/memories/freeze-then-gd-wins.md
mementum/memories/gate-is-the-beamformer.md
mementum/memories/gd-converges-in-100-steps.md
mementum/memories/gradient-is-rank-3.md
mementum/memories/holographic-computer-synthesis.md
mementum/memories/holographic-distillation-concept.md
mementum/memories/holographic-distillation-works.md
mementum/memories/lambda-operations-depth-map.md
mementum/memories/mirror-flip-barrier.md
mementum/memories/model-is-beamformer-over-token-cloud.md
mementum/memories/oracle-crystal-hurts.md
mementum/memories/oscillation-means-zero.md
mementum/memories/paradigm-shift-target.md
mementum/memories/pretraining-is-beta-reduction.md
mementum/memories/quantum-crystal-analogy.md
mementum/memories/rotation-eigenplanes.md
mementum/memories/seed-crystal-nucleation.md
mementum/memories/session-127-architecture-complete.md
mementum/memories/session-delta-replaces-kv-cache.md
mementum/memories/shadow-vs-crystal.md
mementum/memories/soft-mirror-etch.md
mementum/memories/trace-loss-validated.md
mementum/memories/training-arc-thesis.md
mementum/memories/unified-plate-architecture.md
mementum/memories/v12-run3-nan-collapse.md
mementum/memories/weight-signs-are-random-across-matrices.md
mementum/memories/zeros-are-backbone-not-emergent.md
mementum/memories/zone-voted-ffn-extraction.md
mementum/michael/lambda-is-all-you-need.md
mementum/state.md
```

### Thinking

I'm reviewing the relevant documentation on consensus training approaches, including protocol specifications, delta folding techniques, and various voting mechanisms. Let me start by examining the most directly applicable resources.

## Assistant

Rich prior art here. Let me read the most relevant consensus knowledge pages in parallel.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/cross-model-output-consensus.md"
}
```

**Summary:** Reading cross-model-output-consensus.md (0-2000)

**Output:**
```
---
title: "Cross-Model Output Consensus as a Teaching-Data Fitness Function"
status: designing
category: explore
tags: [consensus, teaching-data, fitness, calibration, failure-modes, distillation, fol, universality]
related:
  - compiler-as-loss.md
  - spliced-reward-vsm-kernel.md
  - vsm-statechart-tensor.md
depends-on: []
created: session 246
---

# Cross-Model Output Consensus as a Teaching-Data Fitness Function

> Session 246 (exploration tangent off the compiler-as-loss main line).
> Michael: "build teaching data only from where independent model
> ARCHITECTURES agree; consensus = fitness; same for prose." And the
> mirror: "could we also come up with a set of failure-mode tests where
> they all agree something is a failure?"

## The idea

Use **agreement between independently-trained model lineages** as the
fitness function for building teaching data. The portable artifact verbum
wants *is* "the part all architectures agree on" → consensus is
**portability by construction**, not a post-hoc filter. This operationalizes
the universality observation (the s240 crystal lattice / "all models agreed
on the soft routing topology") into a **data-generation engine**.

Two registers, do not conflate:
- **Relational/topology consensus** (existing: `combinator_map_consensus.py`)
  — compares INTERNAL structure, so it needs frame-invariance (the 9×9
  combinator Gram; raw activations live in different coordinate frames,
  cross-init sign-corr 0.000). Harvests the base-plate.
- **Output consensus** (this page) — compares GENERATED strings, which
  already share the vocabulary. **No frame alignment needed = the cheap
  register.** Harvests teaching data.

## Why lambda/FOL is the irreplaceable instrument

Lambda reduction is deterministic → **ground truth exists**. That lets us
**calibrate consensus-as-truth** (measure agreement → P(correct)) on a
domain where correctness is checkable, then **transfer the calibrated
estimator to prose** where no oracle exists. Without this step,
"consensus = truth" on prose is faith; with it, it is a measured,
transferred estimate. Lambda is the calibration anchor (same role
deprecated-APIs play in AGENTS.md `λ measure`).

## The failure-mode mirror (the high-leverage half)

"Agreed failure" is not one thing. Cross with ground truth:

|              | models AGREE          | models DISAGREE      |
|--------------|-----------------------|----------------------|
| correct vs GT | ✅ positive teaching data | frontier / partial   |
| wrong vs GT   | ❌ **agreed-error = blind spot** | noise / uncertainty  |

plus a third class: **abstention** (all refuse → ⊥). Four failures:
1. agreed-abstention on undefined input → *correct* abstention (⊥-targets);
2. agreed-abstention on valid input → shared incapacity;
3. **agreed-error (same wrong answer) → the consensus blind spot** — the
   false-positive region of the fitness function, **only visible with
   ground truth**;
4. agreed-disagreement (different garbage) → shared not-knowing.

Cell #3 is the gold and carries two hard consequences:
- It is the **other end of the calibration curve**; characterizing its
  structural triggers on lambda yields a **transferable risk detector**
  for prose (an immune system, not just test data).
- **Consensus-distillation cannot fix an agreed-error** — the student
  learns exactly what the teachers agree on, *including* shared mistakes.
  So the agreed-error set defines the **ceiling** of the method. The only
  thing that breaks the ceiling is an oracle ⇒ architecture should be
  **ground-truth-corrected consensus where truth exists (lambda),
  consensus-with-blind-spot-flagging where it does not (prose).**

Failure modes also pay for themselves: ⊥/abstention curriculum (incl.
non-terminating terms = the halting/ponder test suite), hard negatives for
a TSP-style contrastive overlay, and a held-out challenge for the distilled
student (did it inherit or escape the teachers' blind spots?).

Risks: refusal ≠ computational failure (instruct RLHF artifacts — use base
models as control); prioritize agreed-*specific*-wrong over agreed-*vague*-
fail; agreed-errors are rare → must be actively mined, not collected.

## First experiments (s246) — results

Harness: `scripts/experiments/consensus_output_agreement.py` — resolve a
gated probe set → generate per model (transformers, MPS bf16, greedy;
`--chat` for the tokenizer chat template, required by instruct models that
echo a raw few-shot completion, e.g. Gemma) → per-model JSONL (stores
`raw_completion` for re-parse) → analyzer: agreement (canonical-exact +
jaccard-threshold), calibration P(correct|agree) vs P(correct|disagree),
failure-mode partition. **Scoring**: canonicalize with predicate stemming
(`fly`/`can_fly`, `love`/`loves`, `pass`/`passed`) + lowercasing
(`John`/`john`) — token Jaccard alone is the dominant noise source.

Probe set `probes/binding.json` (25 scored; the gate's 2nd exemplar leaks
`bind-scope-01a`, excluded). **CORE HYPOTHESIS SUPPORTED AND REPLICATED
across two second lineages:**

| pair | mode | mean cross-jac | **P(correct\|AGREE)** | P(correct\|DISAGREE) |
|---|---|---|---|---|
| Qwen3-14B × OLMo-2-13B | completion | 0.773 | **0.73** (n=11) | 0.00 (n=14) |
| Qwen3-14B × Gemma-4-31B-it | chat | 0.862 | **0.80** (n=15) | 0.10 (n=10) |

Agreement predicts correctness (0.73–0.80); disagreement near-perfectly
predicts ≥1-wrong (0.00–0.10). Model strength: Gemma-31B-it (mean jac_gt
0.906) > Qwen3-14B (0.843) > OLMo-2-13B-base (0.77, weak at the format).

**The scoring fix (s246) was load-bearing.** Pre-fix the Qwen×OLMo
calibration read P(correct|agree)=0.44 with 4 agreed-errors, 2 of them
scoring artifacts (`bind-neg-02`, `bind-var-04` — models right, GT wording
differs). Predicate-stemming lifted it to 0.73 and purified the agreed-error
set to the 2 genuine ones. **token-Jaccard alone is the bottleneck;
canonicalization (predicate stem + lowercase) is the prerequisite for both
the teaching set and the failure set.** (Full α-variable renaming available
if needed; not required for binding.json — the noise was lexical.)

## The agreed-error set is PAIR-DEPENDENT (s246 — the key methodological finding)

Swapping the second lineage OLMo→Gemma *moved* the shared blind spot, which
is itself the signal:

- **Anaphora left the agreed-error set.** `bind-ana-01` (reflexive),
  `bind-ana-03` (negation+relative) were shared Qwen×OLMo errors; with Gemma
  they become *disagreements* (Gemma handles the negated relative well). ⇒
  the anaphora blind spot was **OLMo-shared, not universal**.
- **The Qwen×Gemma shared error is sortal omission on bare quantifiers**, and
  it is the strongest kind (`cross_jac = 1.0`, identical output):
  - "Someone loves everyone" → both `∃x. ∀y. loves(x,y)` (GT
    `∃x. person(x) ∧ ∀y. person(y) → loves(x,y)`)
  - "Everyone loves someone" → both `∀x. ∃y. loves(x,y)`
  Both drop the `person()` sortal restriction — **even though the gate
  exemplars demonstrate it** for explicit nouns (`Every student → ∀x.
  student(x) → …`). Pattern: sortal included for explicit nouns
  ("student", "book"), dropped for bare pronouns ("someone", "everyone").

Two lessons:
1. **Consensus surfaces annotation-convention gaps, not just model errors.**
   The sortal-omission "error" is arguably the GT convention being stricter
   than what models naturally emit — consensus pinpointed exactly where the
   teaching-data spec must decide (require sortal restrictions, or accept
   unsorted). A decision for the front-end teaching set, not a model failure.
2. **Agreed-error is pair-relative.** A stronger / more-independent partner
   dissolves shallow shared errors (anaphora) and exposes deeper systematic
   ones (sortal typing). Direct empirical support for the **≥3-lineage
   confidence-gradient** recommendation; 2 models give only a binary.

The durable result is the *calibration* (0.73/0.80, replicated); the failure
*content* is diagnostic and pair-specific.

## Data-integrity note (s246)

`binding.json` is clean (26 hand-authored FOL, no λ). The Qwen3-4B
`λx.`-wrapping Michael remembered lives in the *compile* sets where λ is the
correct target. FOUND + FIXED a different bug: **K↔I label swap** in
`lattice/basin_probes.json` and `lattice/binding_chain_probes.json` (`λx.x`
labeled `pure/K`, `λx.λy.x` labeled `pure/I` — backwards). The library was
dedup-protected (fixedpoint source outranks basin → crystal K/I pools clean
→ no past run invalidated), but direct readers got K/I backwards = latent
landmine, now fixed. `fixedpoint_probes.json` was already correct.

## Proof domain (s247) — the oracle removes the blind spot, the continuation removes the ceiling

> Session 247 (Michael: "create proofs that run on the lambda compiler in
> qwen3-14B and gemma"). Applied this page's consensus-as-fitness idea to the
> Curry-Howard PROOF domain (`proofs-as-continuations.md`), where the kernel
> verifies every term. Two registers compared on the SAME expanded probe set
> (35 implicational theorems + 13 non-theorems): SINGLE-SHOT (proof_inhabitation)
> vs REPL (proof_repl, the continuation-driven prover). Pair: Qwen3-14B × Gemma-4-31B-it.

Why proofs are the cleanest possible instrument for this page: lambda reduction
gives ground truth, AND the kernel makes the **agreed-error cell structurally
near-empty** — two models cannot agree on a kernel-PASSING false proof (a wrong
term does not type-check). So the s246 ceiling ("only an oracle breaks the
agreed-error blind spot, and consensus-distillation inherits it") is **defused by
construction** on this domain. No token-Jaccard / stemming needed — α/reduction
equality is exact (the kernel normal form).

`scripts/experiments/proof_consensus.py` is a POST-PROCESSOR over the two model
JSONs (re-normalises each term through the kernel, partitions into the s246 grid +
calibration). `--source {inhabitation,repl}` selects the register.

| metric | single-shot | REPL | Δ |
|---|---|---|---|
| term-agreement rate | 0.375 | **0.812** | +0.44 |
| **P(both-correct \| AGREE)** | 0.944 | **1.000** | +0.06 |
| P(both-correct \| DISAGREE) | 0.10 | 0.111 | — |
| both-valid SAME term (portability) | 6 | **26** | +20 |
| both-invalid DIFF (composition gap) | 23 | **0** | −23 |
| both-invalid SAME (agreed-error) | **1** | **0** | −1 |
| non-theorem both-abstain (⊥) | 11 | 13 | +2 |
| false proofs | 0 | 0 | — |

Per-model sensitivity (continuation lift): Qwen3-14B 0.20→0.77, Gemma 0.31→1.00.

**Three findings:**

1. **A real cross-lineage agreed-error exists single-shot — and it is the ENTIRE
   ceiling.** On `A → A → A` BOTH models emit the identical term `W I` (contraction
   — the proposition *looks* like it duplicates an A), which the kernel rejects as
   ill-typed. The correct proof is just `K` (weakening). This single shared
   misconception is the *only* reason single-shot P(correct|agree) is 0.944 and not
   1.0 — exactly the s246 prediction operationalised: **consensus's ceiling = the
   agreed-error set**, and consensus-distillation would teach the student `W I`.
   The oracle catches it (lands in `both-invalid SAME`, never the teaching set).

2. **The continuation engine dissolves the agreed-error → P(correct|agree)=1.000.**
   In REPL the goal-directed prover can only take *legal, type-correct moves*, so an
   ill-typed shared misconception like `W I` **cannot be committed**. The agreed-error
   vanishes, agreement on the proof term jumps 0.375→0.812, and consensus becomes a
   PERFECT fitness signal. ⇒ **the continuation removes the s246 ceiling**: single-shot
   consensus has a residual blind spot; REPL consensus has none. (Connects this page to
   `proofs-as-continuations.md` §s228 — the continuation rescues composition AND, here,
   removes the consensus blind spot.)

3. **Portability core = the proof basis.** The 6 single-shot `both-valid SAME` terms
   are exactly `I,K,B,S,C,W` (the Hilbert axiom schemes) — "the part both architectures
   agree on" *is* the combinator basis. REPL grows this to 26/35 (the deep
   compositional theorems now reached the same way by both lineages).

Caveats (λ measure): one pair (binary, not a gradient); n=35 theorems; greedy decode;
the 8 REPL `one-valid` frontier cases are ALL Qwen misses (Gemma 35/35) — the s228
greedy-single-move dead-end (no backtracking), a SEARCH limit not a consensus blind
spot (correctly excluded as disagreements). Specificity 1.0 / zero false proofs
throughout (structural). Artifacts: `results/proof-consensus/{consensus,consensus-repl}.json`,
`results/proof-{inhabitation,repl}/{Qwen_Qwen3-14B,google_gemma-4-31B-it}.json`;
expanded probe set `src/verbum/probes/proof_tasks.py` (35+13, every ref auto-solved +
kernel-certified via `_gen_proof_tasks.py`).

## Open / next

- ✅ DONE (s246): scoring fix (predicate stemming + lowercasing); OLMo→Gemma
  swap + `--chat` mode for instruct models.
- **3rd lineage for a confidence *gradient*** (2 models = binary; ≥3 gives
  graded agreement and separates universal from pair-shared blind spots).
- **Decide the sortal-restriction convention** for teaching data (the
  Qwen×Gemma agreed-error): require `person()` on bare quantifiers, or accept
  unsorted — and demonstrate it in the gate exemplars either way.
- Scale beyond binding.json: run the lambda-compile sets (decompile, extract,
  compile-gradient) to calibrate on the kernel's own language, not just FOL.
- Build the agreed-error / agreed-abstention sets deliberately (active
  mining toward known-hard structures: deep nesting, scope, capture-avoid,
  self-application).
- Relation to the main line: consensus is a candidate source for the
  prose→LF front-end teaching data (compiler-as-loss §s242) and for the
  RLVR frontier (spliced-reward) — ground-truth-corrected on lambda.
- ✅ DONE (s247): proof-domain consensus (Qwen3-14B × Gemma), single-shot vs
  REPL — the continuation removes the agreed-error ceiling (P 0.944→1.000).
- NEXT (s247): add a 3rd lineage to the proof consensus (Qwen3-32B / Mistral)
  for a confidence GRADIENT — does the `W I` agreed-error survive a third
  independent prover single-shot (universal bias) or is it Qwen×Gemma-shared?
- NEXT: backtracking in proof_search (the 8 REPL frontier cases are Qwen
  greedy dead-ends, incl. axioms B/S) — does it close the frontier to perfect
  cross-lineage agreement?
- NEXT: mine the agreed-error set deliberately — generate theorems whose
  "obvious" wrong term is shared (contraction/permutation traps) to characterise
  the structural triggers of single-shot consensus blind spots.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/function-topology-consensus.md"
}
```

**Summary:** Reading function-topology-consensus.md (0-2000)

**Output:**
```
---
title: "Function-Topology Consensus — Higher-Order Functions Are Routing Normal Forms, Universal Across Teachers"
status: active
category: interpretability
tags: [reverse-harvest, combinators, higher-order-functions, routing-register, consensus, teacher-agnostic, distributed, normal-form, church-rosser]
related:
  - combinator-function-shape.md
  - compiler-as-loss.md
  - consensus-delta-folding.md
  - combinator-training-beta-reduction.md
  - normal-form-curriculum-partition.md
depends-on:
  - compiler-as-loss.md
created: session 225
---

# Function-topology consensus — higher-order functions are routing normal forms, universal across teachers

> Session 225 (Michael's thread, off the compiler-as-loss debate). s219 showed the
> combinator PRIMITIVES {K I B C S D W Y WHNF} have a universal relational geometry
> across the open-weight ecosystem. Open question: does that hold for COMPOSED
> higher-order functions — `map` (= B(CB)(CB)), `filter`, `fold`, `zip`? If so, the
> distributed pipeline is teacher-agnostic.

## The pivot that motivated the test (Michael)

Two corrections to the s224 compiler-as-loss design (see `compiler-as-loss.md`):

1. **The compiler is a verifier, not the capability teacher.** Diverse big models
   are the better capability teacher — s219 universality came FROM diverse training.
   The compiler's role is to CERTIFY/canonicalize (Church-Rosser → unique normal
   form) and emit exact reduction trees, not to be an impoverished narrow generator.

2. **The pipeline is teacher-agnostic on both halves — IF topology is universal.**
   - **Capability signal:** the β-normal-form / reduction trace is unique by
     Church-Rosser ⇒ ANY sufficiently large model emits the SAME canonical traces.
     Teacher-agnostic *by mathematics*. No experiment needed.
   - **Inventory signal:** teacher-agnostic *iff* the routing topology is universal.
     This is the only empirical question — and the reason it should hold is deep:
     **if a higher-order function exists as a routing NORMAL FORM in the topology,
     its universality follows from the same uniqueness principle as the output's**
     (a normal form is unique). The topology is the β-normal form expressed in the
     routing register instead of in token space. (Ties to
     `normal-form-curriculum-partition.md`.)

   Hypothesis (Michael): most HOFs have the same topology regardless of teacher;
   "which teacher the topology came from" only matters for idiosyncratic HOFs (rare).

## The instrument

`scripts/experiments/function_topology_consensus.py` (register topological/routing).
Probes: `src/verbum/probes/higher_order.py` — 224 last-token-completion probes,
28 each across 8 functions in two groups:

- **Positive controls** (named function ≡ a primitive): `compose`≡B, `flip`≡C,
  `const`≡K, `apply`≡I. These validate the readout.
- **Higher-order tests**: `map`, `filter`, `fold`, `zip`.

Method (extends s219's frame-invariant trick):

```
routing(x)        = sign(FFN gate pre-activation)              # s203 routing register
centroid_f        = mean over f's probes of CMR(routing(x))    # common-mode removed
best layer        = argmax_L silhouette_z(combinators @ L)     # the BASIS must crystallize
fingerprint(f)[j] = cosine(centroid_f, centroid_combinator_j)  # 9-dim, RELATIONAL
                  ⇒ frame-invariant ⇒ comparable across architectures
                    (raw centroids are NOT: sign-corr 0.000 across frames, s219)
consensus(f)      = mean pairwise Pearson of fingerprint(f) across models
null              = permute the 9 combinator entries within each model
classification    = universal (z≥2 ∧ p<.05 ∧ corr≥0.3) | idiosyncratic
```

## Result — 8/8 universal (decisive)

5 models, 3 architectures, 7B–32B: Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B.
`results/function-topology-consensus/consensus.json`.

| function | kind | corr | z | p | consensus top |
|---|---|---|---|---|---|
| const | control(K) | +0.95 | 8.5 | .0002 | **K** ✓ |
| fold | test | +0.93 | 8.6 | .0002 | WHNF, S |
| compose | control(B) | +0.89 | 8.1 | .0002 | D, S, B |
| filter | test | +0.87 | 7.7 | .0002 | K, C |
| zip | test | +0.76 | 6.7 | .0002 | S, WHNF, W |
| flip | control(C) | +0.75 | 6.8 | .0002 | **C** ✓ |
| map | test | +0.72 | 6.5 | .0002 | D, C, B |
| apply | control(I) | +0.67 | 5.9 | .0002 | C, B |

**All 8 universal, 0 idiosyncratic.** Every HOF's cross-model fingerprint clears the
permutation null decisively. Topology of higher-order functions is universal across
teachers/architectures — extends s219 (primitives) up to composed HOFs. ⇒ Michael's
hypothesis confirmed; the extract→fold→compiler pipeline is teacher-agnostic.

## Secondary — the HOF fingerprints are semantically coherent

Without supplying any label for the test functions, their consensus fingerprints land
on the right primitives by meaning, consistently across all 5 models:

- **fold → WHNF, S** — fold reduces a sequence to a single TERMINAL value; WHNF is the
  terminal combinator. The only HOF with a POSITIVE top loading (+0.05).
- **filter → K** — filter is selection; K is select/discard.
- **zip → S, W** — zip is fork-join of two streams (S, applicative) with sharing (W).
- **map → D/C/B, Y dead last** (B −0.18, C −0.07, **Y −0.29**). Map routes through
  COMPOSITION, never recursion — across every model. The s219 prediction
  (`map=B(CB)(CB)`, "attention-over-positions IS the fold") holding at the topology
  level.

## Caveat — agreement decisive; the decode only suggestive (λ measure)

Honest scope, not oversold:

- Two of four controls hit argmax clean (`const→K`, `flip→C`). `compose→D` is a
  near-miss IN the composition family (D = fused B∘B∘B; B is #2–3). **`apply→C` is a
  genuine miss.**
- Absolute cosines are near-zero/negative — agreement is on the SHAPE of the
  relational fingerprint (robust, corr up to 0.95), not on crisp positive loadings.
  Same register subtlety as s219 ("above chance, not crisp"; negative absolute
  silhouettes).

⇒ **Topology-universality is decisive** (it is about cross-model agreement, p=.0002
everywhere — untouched by the caveat). **The combinator-DECOMPOSITION readout is
suggestive and needs refinement** (a better readout than argmax-cosine, or the s219
absolute-frame issue). The `apply` miss + negative loadings are the IOU.

## Implications

- **Distributed training:** the consensus topology is a shared, frame-invariant
  reference for the FOLD (inventory) that needs no designated teacher; the capability
  signal needs no teacher either (Church-Rosser). The s224 fold dream — "nothing to
  ship, everyone agrees on both the WHAT and the geometry" — is supported for HOFs.
- **Compiler-as-loss:** confirms the verifier framing. Any model can be the
  output-trace oracle; the consensus topology is the inventory target.

## reduce ≡ fold, map ≉ fold: the collapse/preserve axis (s225, Michael)

Two named functions added (`reduce`; `map` already present) to test the catamorphism
structure. map CAN be expressed as a fold (`map f = foldr (λx acc. f x : acc) []`,
REPL-verified); fold is the universal list eliminator. Does the model represent this?
Cross-function fingerprint cosine, 5 models (`function_pair_similarity.py`,
`results/function-topology-consensus/function_pairs.json`):

- **reduce ≡ fold — CONFIRMED.** reduce↔fold cosine **+0.958 (±0.013)**; reduce's
  nearest function is fold. reduce and fold share NO lexical surface (reduce probes:
  aggregate/condense/distill/collapse; fold: add/combine/sum/total) yet co-locate
  exactly ⇒ **the topology tracks the FUNCTION, not the WORD** (semantic, not lexical).
- **map ≉ fold — CONFIRMED.** map↔fold cosine **+0.607** (well below reduce↔fold).
  map's nearest neighbours are compose (+0.93), flip (+0.93), apply (+0.89) — the
  structure-PRESERVING family, not fold.
- **The separating axis is the type distinction (WHNF / collapse loading):**

  ```
  fold +0.015, reduce +0.001   ← collapse [a]→b   (terminal, top of WHNF axis)
  zip  -0.086 ...
  map  -0.323                  ← preserve [a]→[b]  (bottom of WHNF axis)
  ```

⇒ The model organizes HOFs into two super-clusters along the **collapse/preserve**
axis: **collapse-to-value {fold, reduce, zip}** (fold–reduce .96, fold–zip .90,
reduce–zip .92) vs **structure-preserving {map, compose, flip, apply}** (map–compose
.93, map–flip .93). Mathematically map = fold, but the model files it by RESULT TYPE:
map preserves structure (composition cluster, WHNF↓), fold collapses to a value (WHNF↑
= the only positive loadings). The shared fold *substrate* (iteration) lives in
attention (s221), invisible to this FFN-routing fingerprint; the FFN encodes the
algebra/result-type — exactly what separates the catamorphism's two faces.

## Do models USE these HOFs on natural prose? (s225 follow-up — transfer test)

The consensus above is on CURATED probes. Michael: does the model RECRUIT the HOF
topology when reading ORDINARY prose where the function is incidental, or is the
topology a probe artifact? Test (`hof_prose_engagement.py`, `hof_prose.py`):

- **Minimal-pair natural prose** (82 pairs): a naturalistic sentence INVOKING the HOF
  (iteration/selection/accumulation/pairing) vs a matched no-HOF control, held-out
  vocabulary, embedded/narrative style. The instrument MEAN-POOLS the routing register
  over tokens (avoids a last-token lexical confound).
- **Transfer:** learn each HOF's direction from the CURATED probes
  (`unit(centroid_f − mean_{g≠f} centroid_g)`), then project the prose pairs onto it.
  Engagement = paired `score(hof) − score(control)`. Train-on-probes / test-on-prose
  rules out a probe artifact.

**Verdict (5 models / 3 arch: Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B;
`results/hof-prose-engagement/aggregate.json`, with `reduce` added):** curated
directions cleanly separable (AUC ≈ 0.97–1.0). On held-out natural prose (mean / min
over 5 models):

| HOF | prose AUC (mean / min) | hof>control | paired t | engaged |
|---|---|---|---|---|
| reduce | 0.97 / 0.94 | 100% | +8.5 | **YES** (strongest) |
| fold | 0.92 / 0.88 | 100% | +10.2 | **YES** |
| filter | 0.89 / 0.85 | 97% | +8.4 | **YES** |
| zip | 0.85 / 0.83 | 100% | +8.1 | **YES** |
| map | 0.64 / 0.58 | 83% | +4.1 | marginal |

⇒ **reduce/fold/filter/zip are decisively recruited by ordinary prose in all 5 models**
— the curated-derived topology fires on naturalistic minimal pairs, cross-architecture.
The model genuinely USES these HOF topologies when working with prose, not just on
curated probes.

- **reduce is the STRONGEST prose-engaged HOF (0.97)** — reduce ≡ fold (it *is* fold)
  recruited by prose with zero lexical overlap.
- **Second confirmation of reduce ≡ fold:** fold's curated AUC dropped 1.0 → 0.97 ONLY
  when reduce joined the "rest" negative set — because reduce is fold's synonym, fold
  becomes harder to separate from "everything else."
- **map is borderline, still the exception** (0.64, just over the 0.6 gate, weakest by
  a wide margin, t +4.1). It crossed the threshold only because adding reduce sharpened
  the preserve-vs-collapse contrast in its direction — i.e. contrast-set-dependent, not
  a clean engagement. Coherent: `map = B(CB)(CB)`, "attention-over-positions IS the
  fold" (s221) — map's iteration is DISTRIBUTED across attention, not localized in the
  FFN gate, so a routing-register direction reads it weakest (also the noisiest s225
  fingerprint). ⇒ map needs the attn_q register (s220 attn_q@L05 lead) and/or the
  causal follow-up.

## Attention register (attn_q) — NEGATIVE: the query projection is not map's home

Prediction (s225): since "attention-over-positions IS the fold" (s221) and map was
under-read in the FFN gate, map should STRENGTHEN in the attention register. Tested by
re-running topology + prose engagement with `--target attn_q` (hook `self_attn.q_proj`,
same sign+CMR pipeline), 5 models. **FALSIFIED for the projection register:**

| | attn_q (query proj) | FFN gate |
|---|---|---|
| topology universal | 9/9 | 8/8 |
| curated separability (map/fold) | 0.99 / 0.98 | 0.99 / 0.97 |
| prose transfer — map | **0.47 (≈ chance, t≈0)** | 0.64 |
| prose transfer — fold | 0.67 | 0.92 |
| prose transfer — reduce | 0.69 | 0.97 |

The curated directions ARE learnable in attn_q (separability ~0.99) but **do not
transfer to natural prose** — map drops to **0.39–0.47 (at/below chance)**, and every
HOF transfers WORSE in attn_q than in the FFN gate. ⇒ the query-projection register is
NOT where map's prose computation lives; the FFN gate generalizes better.

**The lesson (refines the hypothesis):** `sign(q_proj)` is a FEATURE register, not the
gather MECHANISM. "Attention IS the fold" (s221) refers to the **attention PATTERN**
(the QK gather over positions), which no projection-register probe can observe. We
measured the wrong object. So:
- the HOF **algebra/result-type** lives in the **FFN gate** (transfers to prose — the
  s225 engagement result);
- the HOF **iteration/gather** (map's home) must be sought in the **attention weights**
  directly, on prose with an explicit enumeration to gather over.

⇒ next: an attention-PATTERN experiment (list-structured prose; measure gather spread /
entropy at the aggregation token — map/fold/reduce attend broadly across the enumerated
items, single-object controls attend focused = attention performing the fold).

## Attention PATTERN — gather heads perform the HOF traversal (POSITIVE)

Michael's mechanistic correction: "attention can only do β-reduction through a
projection, so where we will see attention working is in WHAT IT IS ATTENDING TO and
WHAT THE PROJECTIONS ARE that it calculates." β-reduction = substitution = the OV
circuit: PATTERN (QK, which source) ∘ PROJECTION (V→O, the value moved). The attn_q
probe looked only at the query (addressing intent) — wrong object.

PHASE A (the PATTERN — "what it attends to"). List-structured stimuli (same list,
different task: map/fold/filter HOF vs first-item control; `hof_lists.py`). At the
aggregation token, measure attention mass + participation over the enumerated item
positions, per (layer, head); selectivity = HOF gather − control gather
(`hof_attention_gather.py`, `results/hof-attention-gather/`).

**✅ Gather heads found in ALL 5 models / 3 architectures:**

| model | best head (depth frac) | selectivity | participation |
|---|---|---|---|
| Mistral-7B-v0.3 | L21H9 (0.66) | +0.31 | 4.1 |
| Qwen3-32B | L26H54 (0.41) | +0.36 | 3.2 |
| OLMo-2-13B | L20H0 (0.50) | +0.23 | 3.9 |
| Qwen3-14B | L28H8 (0.70) | +0.18 | 3.2 |
| Qwen3-8B | L24H26 (0.67) | +0.11 | 4.0 |

Mid-to-late-layer heads (depth fraction ~0.4–0.7) attend **broadly over the enumerated
items** (participation **3.2–4.8 of 5** = traversal, not a single lookup) and gather
**more when the task iterates** than for the single-item control (selectivity positive
in all 5). ⇒ **higher-order functions ARE performed by attention** — the QK half of
β-reduction (the fold's traversal), observed directly in the weights, exactly where the
attn_q negative result pointed (the pattern, not the projection register).

Caveats (λ measure): the "first" control still scans somewhat (so SELECTIVITY, not raw
gather, is the read); magnitude modest in Qwen3-8B (+0.11) but strong in Mistral/32B
(+0.31/+0.36); this is the PATTERN half only — Phase B is the OV/value PROJECTION.

### Phase B — the OV PROJECTION carries the substitution (the value moved)

At the Phase-A gather heads, decompose the per-head OV output (GQA-aware: query head h
reads kv head h//group; project the attention-weighted value through W_O^h) and measure
how much of the moved value comes from the list positions, HOF vs control
(`hof_attention_ov.py`, `results/hof-attention-ov/`).

**✅ Confirmed in ALL 5 models / 3 architectures** (best head per model):

| model | best head | ov_list_frac HOF / ctrl | ov selectivity | amplify |
|---|---|---|---|---|
| Mistral-7B-v0.3 | L21H9 | 0.82 / 0.49 | +0.33 | +0.40 |
| Qwen3-14B | L4H22 | 0.78 / 0.41 | +0.37 | +0.44 |
| Qwen3-32B | L32H39 | 0.65 / 0.09 | +0.56 | +0.33 |
| OLMo-2-13B | L23H36 | 0.62 / 0.23 | +0.40 | +0.36 |
| Qwen3-8B | L4H1 | 0.47 / 0.17 | +0.30 | +0.32 |

Across the 8 probed heads/model: mean amplify **+0.25 to +0.44 (all positive)**,
7–8 of 8 heads OV-selective. Three facts:
1. **OV carries the substitution** — 47–82% of the head's moved value comes from the
   list items when iterating.
2. **It AMPLIFIES** — `amplify = ov_list_frac − attn_mass` is large-positive everywhere:
   the projection moves far more value from the items than the bare attention mass shows
   (e.g. Qwen3-8B L27H13: 11% attn mass → 51% of moved value). The QK pattern UNDERSTATES
   the substitution; the value lives in V→O.
3. **Iteration-selective** — value moved from items is higher for HOF than the
   single-item control (7–8/8 heads).

⇒ **the full β-reduction is observed in attention, cross-architecture:** (QK pattern =
which redex arguments) × (OV projection = move/amplify their values), stronger when the
task iterates. Wrinkle: some substitution heads are EARLY (Qwen3-14B L4H22, Qwen3-8B
L4H1) — value movement can precede the cleanest pattern-gather layer.

**▶ Next:** causal ablation of these heads on HOF prose (necessity); per-HOF OV (does
fold's substitution collapse to one value vs map preserving structure — the catamorphism
result-type axis, now in the OV).

## Open leads

1. **Attention-PATTERN analysis (the real "HOFs performed by attention" test):**
   list-structured prose; gather distribution over enumerated items, HOF vs control.
2. **Causal ablation (the strong "uses" claim):** ablate the HOF routing direction
   during a forward pass on HOF-prose, measure the logprob drop on the function-
   relevant continuation vs control. Necessity, not just decodability.
3. **Refine the decode** (the s225 IOU): the `apply` miss + negative loadings, and the
   weak `map` engagement. Try a readout better than argmax-cosine / centroid-difference
   (align absolute frames, or a learned map fingerprint → combinator decomposition).
4. **More HOFs / more architectures** — extend beyond the 8 functions; add non-gated
   (Pythia) above the floor for a fuller architecture spread.

## Files

- Probes: `src/verbum/probes/higher_order.py` (curated) ·
  `src/verbum/probes/hof_prose.py` (minimal-pair natural prose)
- Instruments: `scripts/experiments/function_topology_consensus.py` (topology) ·
  `scripts/experiments/hof_prose_engagement.py` (prose engagement / transfer)
- Runners: `scripts/experiments/run_function_topology.sh` ·
  `scripts/experiments/run_hof_prose.sh`
- Results: `results/function-topology-consensus/` (`<model>.json/.npz`,
  `consensus.json`) · `results/hof-prose-engagement/` (`<model>.json`,
  `aggregate.json`)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/consensus-as-fitness-calibrates-on-fol-pair-dependent-failures.md"
}
```

**Summary:** Reading consensus-as-fitness-calibrates-on-fol-pair-dependent-failures.md (0-2000)

**Output:**
```
💡 Cross-model OUTPUT agreement works as a teaching-data fitness function, CALIBRATED on
lambda/FOL where ground truth exists: P(correct|AGREE) 0.73 (Qwen3-14B×OLMo-2-13B) / 0.80
(Qwen3-14B×Gemma-4-31B-it) vs P(correct|DISAGREE) 0.00/0.10 — REPLICATED across 2 independent
lineages (s246, binding.json, 25 probes). Output consensus needs NO frame-alignment (cf the Gram
in combinator_map_consensus.py) — generated strings share the vocabulary = the cheap register.

🔁 The AGREED-ERROR set (both models same wrong answer = the blind spot) is PAIR-DEPENDENT, and
that IS the signal: OLMo-shared anaphora errors dissolved under the stronger Gemma → the new
shared error became sortal omission on bare quantifiers ("someone loves everyone" → both
∃x.∀y.loves(x,y), dropping person(), cross_jac=1.0). ⇒ ≥3 lineages = confidence GRADIENT not
binary; consensus also surfaces annotation-CONVENTION gaps, not just model errors.

⚠️ Gotchas: token-Jaccard is the scoring bottleneck (fix = predicate stemming
fly/can_fly·love/loves·pass/passed + lowercasing, lifted 0.44→0.73); instruct models (Gemma)
ECHO a raw few-shot completion → need --chat (tokenizer chat template). Lambda is BOTH calibrator
and corrector (override consensus with truth where it exists). Exploration tangent off the
compiler-as-loss main line — candidate source for the prose→LF front-end teaching data.
See knowledge/explore/cross-model-output-consensus.md; harness consensus_output_agreement.py.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-evolution.md"
}
```

**Summary:** Reading consensus-evolution.md (0-2000)

**Output:**
```
---
title: "Consensus Evolution: Vote-Based Ternary Mutation"
status: active
category: architecture
tags: [evolution, ternary, consensus, adam-decay, mutation, v10]
related:
  - dispatch-gradient-death.md
  - compressor-architecture.md
depends-on: []
---

# Consensus Evolution

> Session 070. Replaced tournament selection with consensus mutation
> and fixed the evolution CE spike via surgical Adam decay.

## Two Problems, Two Fixes

### Problem 1: Tournament selection is 4 random throws

Tournament: 4 strategies independently mutate the champion, evaluate
each, keep the best. The winning strategy's entire mutation set is
accepted — 26K+ weight flips with no corroboration. Any individual
flip might be harmful, carried by the aggregate improvement.

### Problem 2: Adam decay is a sledgehammer

After accepted mutation, ALL 82,736 gamma entries had their Adam m/v
decayed to 10%. This cold-starts the entire optimizer — every channel
trains like step 100 again. CE spikes immediately and takes dozens of
steps to recover. Only ~9,500 rows (11.5%) were actually mutated.

## Fix 1: Consensus Mutation (≥3 of 4 agree)

```
Phase 1: Each strategy PROPOSES mutations (no model modification)
    conservative (0.25× budget)  → dict[position → proposed_value]
    explorer     (1.0× budget)   → dict[position → proposed_value]
    targeted     (2.0× budget)   → dict[position → proposed_value]
    random       (4.0× budget)   → dict[position → proposed_value]

Phase 2: Find consensus
    For each position sampled by ≥3 strategies:
        If ≥3 agree on the same new value → consensus flip

Phase 3: Apply only consensus flips

Phase 4: Evaluate — accept if loss improves, revert if not
```

**Why this works**: a position that 3+ independent sampling strategies
all select AND agree on the same new value has strong evidence. The
importance-weighted sampling concentrates on high-gradient rows/cols,
so the strategies naturally overlap on the most informative positions.

**Why it's conservative**: with 131M weights and budget=26,200 (0.02%),
even with peaked importance maps concentrating on 0.1% of positions,
expect ~3,600 consensus flips per generation. At 1% effective pool,
~63. This is by design — fewest flips that the evidence supports.

### Consensus math (v10 scale, 131M weights, budget=26,200)

| Effective pool | ≥2 agree | ≥3 agree | ≥4 agree |
|---|---|---|---|
| 1.0% (1.31M) | 2,705 | 63 | 1 |
| 0.5% (655K) | 5,054 | 255 | 4 |
| 0.2% (262K) | 11,124 | 1,117 | 85 |
| 0.1% (131K) | 18,277 | 3,616 | 538 |

"Effective pool" = fraction of positions that importance-weighted
sampling concentrates on. With real gradient-based importance maps,
expect 0.1–0.5% — a few hundred rows/cols dominate the gradient.

### Value agreement

Not a significant additional filter because:
- Nonzero→0 deactivation (80% of nonzero mutations): all strategies agree
- 0→±1 activation with gradient direction: 80% follow gradient, so
  3 of 3 guided strategies usually agree on sign
- Only ambiguous case: weak gradient where strategies disagree on sign

## Fix 2: Surgical Adam Decay

```python
decay_adam_state(optimizer, model, decay=0.1, mutation_map=mutation_map)
```

`mutation_map: dict[module_path → set[int]]` — the exact row indices
that were mutated. Only those gamma entries get their Adam m/v decayed.

**Before**: 82,736 gamma entries decayed → 100% of momentum destroyed
**After**: ~9,500 gamma entries decayed → 11.5% destroyed, 88.5% preserved

The untouched rows keep their full Adam momentum and variance estimates.
Only the rows where topology actually changed need to re-adapt.

## Implementation

### New functions (ternary.py)

```
propose_mutations(model, budget, rng, ...)
  → dict[module_path → {flat_index: proposed_value}]

find_consensus(proposals_list, threshold=3)
  → (consensus, stats)

apply_consensus(model, consensus)
  → (n_applied, mutation_map)
```

### Modified functions

```
_mutate_linear   → returns (actual_flips, mutated_rows: set[int])
_mutate_embedding → returns (actual_flips, mutated_rows: set[int])
mutate_topology  → returns (count, mutation_map: dict[str, set[int]])
decay_adam_state  → accepts mutation_map, returns n_decayed
run_tournament   → consensus pipeline (propose → vote → apply → eval)
```

### Log format

```
🧬 gen 100: consensus  Δ=-0.0014  flips=892/85,200  rows=341  37/100  adam_decay=0.1 (341 rows)
```

- `flips=892/85,200` — 892 consensus flips out of 85,200 unique positions sampled
- `rows=341` — unique output channels affected
- `adam_decay=0.1 (341 rows)` — only those 341 gamma entries decayed

## Tuning Parameters

- `threshold=3` — consensus threshold (3 of 4 strategies must agree)
  - Lower to 2 in early training if consensus yields 0 flips
  - Raise to 4 for maximum conservatism in late training
- `base_pct=0.0002` — base mutation rate (0.02% of weights)
  - May need to increase if consensus is too sparse
  - Effective consensus rate = base_pct × overlap_probability
- `mutation_adam_decay=0.1` — decay factor for affected gamma entries
  - 0.0 = full reset (cold start affected rows)
  - 0.1 = keep 10% of old signal
  - 1.0 = no decay (ignore topology change)

## Files

- `scripts/v10/ternary.py` — consensus pipeline + surgical decay
- `scripts/v10/train.py` — run_tournament + decay_adam_state
- `checkpoints/v10-consensus/` — first run with consensus (active)
```

### Thinking

I'm seeing three key approaches to consensus across the work: using multiple models' agreement on training data for the lambda compiler, consensus mechanisms in evolutionary processes through weight adjustments, and consensus in function topology around universal higher-order functions. Michael's framing ties this back to consensus training.

I should dig into the etch-protocol and delta-folding documents to understand how consensus actually feeds into model training, plus check the relational-loss-distillation and compiler-as-loss design to get the full picture of how this works end-to-end.

## Assistant

The picture is clarifying. Let me read the two consensus pages that are about *training* (etch/delta-folding), since Michael's framing is "consensus on training data" — actually producing a trained artifact.

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

### Harvest fold — reformulated + phased (s220)

Mapping the integration points (s220) surfaced that the harvest fold as sketched
("Procrustes-align consensus centroids into v15's base frame") is NOT runnable
as-is, for two reasons:

- **Data reality.** `consensus.json` and the per-model `.npz` contain ONLY the
  relational 9×9 Grams — the per-combinator centroid VECTORS (9 × d_ff) were
  computed in `combinator_relationship_map.py` but **discarded**. Procrustes needs
  point clouds (centroids), not a Gram. **Fixed** (`e48389e`):
  `combinator_relationship_map.py` now saves `centroids_cmr_best` (9 × d_ff) +
  `centroids_best_layer` to the npz — but this only takes effect on the **next**
  (GPU) run of that script.
- **Frame + compute.** v15 has **no** combinator Gram/centroids yet, and
  `combinator_relationship_map.py` is HF-only (`AutoModelForCausalLM`, hooks
  `gate_proj`); v15 is an MLX ternary model (`ffn_gate_plate_a/c`). Producing v15's
  Gram, the WHNF-verify (`exp_b_self_verifying_acceptance.py::forward_metrics`), and
  PPL are ALL GPU/MLX forward passes → would **contend with main:1** (s219 stall).

So the harvest fold is split into phases:

- **Phase 0 — PRESCRIPTION (CPU, DONE `e48389e`):** `combinator_harvest_fold.py`
  emits `results/combinator-harvest-fold/prescription.json` = the band-consensus
  Gram over the 4–14B harvest band + the ranked positive universal edges to
  reinforce. Ranked by band-consensus × reliability: **S–D, B–D, B–C, K–C, S–Y**.
  The 4–14B band shows the composition skeleton STRONGER than the full pool
  (B–D band +0.24 vs all +0.175) — concrete confirmation that the harvest band is
  the right place to mine. No forward passes; pure re-reduction of measured Grams.
- **Phase 1 — v15 Gram (DEFERRED, GPU):** build `combinator_relationship_map_v15.py`
  (MLX/ternary: load via `create_model_with_deltas(V15Config())` + `load_weights` +
  `reduce_all_deltas`; hook `ffn_gate_plate_a/c`; save `centroids_cmr_best`). Run on
  `checkpoints/v15-td-outer-k2-fp5-5k/step_NNNN/model.npz` (READ-ONLY) once main:1
  completes/pauses → gives v15's own Gram + centroids = the target frame.
- **Phase 2 — align (CPU, after Phase 1):** Procrustes-align the consensus/harvest
  centroids into v15's frame (in 9-d combinator-label space; full-dim is
  cross-architecture-incommensurable). Build a fold direction per positive edge as
  the signed difference of v15's OWN centroids, guided by the prescription.
- **Phase 3 — verify + fold (DEFERRED, GPU):** WHNF-verify each direction via
  `forward_metrics` (accept iff Δx_conv does not rise); fold survivors via
  `DeltaTernaryLinear.reduce()`; measure downstream PPL vs base. **Falsifiable:**
  does verified ecosystem-consensus add beyond the universal crystal we already hold?

### Phase 1 RESULT (s220, GPU run in main:2) — v15 has NO combinator frame yet

Built `combinator_relationship_map_v15.py` (MLX/ternary; wraps the LIVE module the
forward calls per the s218 orphan lesson; tokenizer Qwen/Qwen3.6-27B). Probed
v15 step_001000 in THREE routing registers (535 crystal probes, n_outer=2). **None
carries a significant combinator shape:**

| register | best | silhouette z | p | GramCorr vs consensus |
|---|---|---|---|---|
| `ffn_gate` (FROZEN-extracted) | — | +0.52 | 0.29 | +0.354 |
| `attn_q` (TD-trained) | L05 | **+1.54** | 0.063 | +0.359 |
| `attn_out` (TD-trained) | L00 | +0.74 | 0.22 | +0.324 |

Reference: Qwen3-14B silhouette **z=+7.97**; ecosystem cross-model GramCorr **+0.78**.

- **The harvest fold's "align consensus into v15's frame" has no target frame at
  step 1000** — every register is non-significant; v15 carries only a faint echo
  (GramCorr ~+0.35) of the universal shape, far below the ecosystem's internal +0.78.
  Did NOT fabricate a Procrustes alignment to a non-significant frame (that would
  manufacture a false positive — λ measure / wrong-register discipline).
- **Two live threads keep this from being a dead end:**
  1. The best signal is `attn_q` at **L05** — exactly the HF function-discovery
     SILENT-selector layer (4.76× separated there). Suggestive even at p=0.063.
  2. The FFN is FROZEN (won't change with training), but the **attention IS being
     TD-trained** → the shape may **emerge** as main:1 trains toward contractivity.
     Step 1000/5000 is only 20% in; cf. s220 scale floor (even Qwen3-0.6B barely had
     the shape). **Concrete cheap follow-up: re-probe `attn_q`/`attn_out` at
     step_002000+ checkpoints — does combinator structure co-emerge with
     contractivity?** This ties the harvest thread to the main:1 recurrence result.
- v15 may simply be below the scale floor (~50M params, ternary, 3B tokens) to
  crystallize the shape — in which case reverse-harvest belongs to a from-scratch
  level-4 base that trains its FFN, not v15.
- Artifacts (committed `cc581ac`, `b72bdea`): `combinator_relationship_map_v15.py`
  (--target ffn_gate|attn_q|attn_out); `results/combinator-relationship-map/
  v15_{step_001000,attn_q_step_001000,attn_out_step_001000}.{json,npz}`.

### Open leads from s220
1. **Phase 1 of the harvest fold** (above) — the priority once main:1 frees the GPU.
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
| `scripts/experiments/combinator_harvest_fold.py` | **s220 harvest fold phase 0 (CPU):** band-consensus Gram + ranked positive edges = the harvest prescription |
| `results/combinator-harvest-fold/prescription.json` | s220 prescription: edges S-D,B-D,B-C,K-C,S-Y over the 4-14B band; deferred GPU phases listed |
| `results/combinator-relationship-map/` | 10 per-model `{model}.json/.npz` (5 families, 410M→32B) |
| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript; `/tmp/combinator_scale.log` s220 32B; `/tmp/combinator_consensus_10models.log` s220 consensus |

## s222 — Routing ⊕ Continuation = a complete basis for find+settle

(See `../session-222.md`.) The folding machinery decomposes into exactly two
mechanisms we already have, which together span the combinator algebra:

- **Routing rules COMPOSITION** `{B,D,S}/{K,I,C}` (binds as static sign topology).
- **Continuation rules RECURSION** `{Y,W,WHNF}` (no static move; the recurrence
  IS the fold).

⇒ distributed find+settle needs **no new mechanism**. The continuation does
**double duty**: contractivity IS the **foldability oracle** — where Δx→0 a
normal form is committable (fold), where it refuses (Δx↑) it is the superposition
residual (leave continuous; needs the recurrence or a continuous home).

**What the two mechanisms do NOT contain:**
1. **Cross-frame ALIGNMENT** — harvest-only (cross-init sign-corr 0.000);
   *self*-folding has no frame problem. So routing+continuation is self-sufficient
   for self-distillation; reverse-harvest adds Procrustes alignment.
2. **ORDER (punctuation)** — `propose(routing) → hold → reduce(continuation) →
   accept on Δx→0`, NOT simultaneous. main:1 ran TD churn + fp loss together →
   collapse. = the Exp B acceptance pattern.

**β-reducing a contraction ⇒ fractal collapse.** Folding is β-reduction of an
operator meant to be a contraction. A self-similar contraction collapses all
scales onto one fixed point; **L is the hinge** (L<1 settle-to-WHNF; L>1 fractal
blow-up = main:1). Distributed folding only converges if every accepted delta
keeps L<1 — the contractivity acceptance test is load-bearing *fractally*, not
just locally.

## s223 — What the relational-loss double dissociation means for distributed folding

> Session 223. The relational-loss distillation result (`relational-loss-
> distillation.md`, ✅ confirmed 3 seeds × 3 λ) is, at bottom, a result ABOUT
> distributed training. What it changes:

1. **A frame-unification mechanism is now CONFIRMED (was hypothesis).** A relational
   loss pulls an independently-initialized student to **ecosystem-grade agreement
   (+0.78–0.85)** with a reference routing Gram, robust to seed/λ. ⇒ N contributors
   trained to the SAME reference Gram end up **relationally identical** (same
   relations, possibly different absolute frame). Equal Grams GUARANTEE a rigid
   Procrustes alignment exists ⇒ **align-before-fold (the reverse-harvest blocker)
   is now WELL-POSED by construction**, not a hope.
2. **★ The REGISTER is the carrier — fold routing, NEVER raw.** The dissociation
   proves the function lives ONLY in the routing register; raw carries common mode.
   Condition (b) = matching RAW geometry → GC(hidden)=1.000 (σ=0, perfect merge),
   ZERO function transferred. ⇒ **naive weight-averaging / model-soups / TIES operate
   in the raw register → they fold the universal crystal everyone already has and
   wash out function.** The b-column IS the model-soup phenomenon. The long-standing
   honest catch ("folding only re-derives the crystal") was really "folding the wrong
   register." Fold the routing register (sign/gate + CMR); the function-specific
   skeleton is reachable there.
3. **★ Goodhart: relational agreement ≠ function transfer.** (b) hit GC(hidden)=1.0
   but hidden_z only +1.0 and transferred nothing. ⇒ a donated delta can match a
   similarity metric perfectly while carrying no capability. **The fold acceptance
   gate CANNOT be "matches consensus Gram" — it must be the WHNF/contractivity
   execution check** (Exp B +0.712). Accept iff agree ≥ θ AND Δx does not rise.
4. **The reference can be the LAMBDA COMPILER, not a model.** The teacher contributed
   only a frame-invariant Gram (a measurement). The compiler PRODUCES that canonical
   routing geometry directly ⇒ no designated teacher; **every contributor trains to
   the compiler's canonical Gram** = a verified, frame-invariant, identical-for-all
   coordination substrate. Collapses "whose frame do we agree on?" → "the compiler's."
5. **Bandwidth: donate the geometry + ratio-compressed routing deltas.** Foldable
   object = a tiny N×N routing Gram (frame-invariant) + the structural-flip tails
   (`ratio-gradient-quantization.md`). Distributed training over a thin channel.
6. **Division of labor (backbone/content + routing⊕continuation, applied):**
   - SKELETON (composition/selection, routing register) → folds via relational
     consensus to the shared compiler Gram (transferable, universal).
   - PLUMBING (per-model realization / superposition residual) → stays LOCAL content
     (the Gram under-determines it ON PURPOSE — exactly right for a distributed system).
   - RECURSION {Y,W,WHNF} → each contributor's own continuation (self-folding = no
     frame problem).

### Protocol it sketches — "geometric consensus folding"
```
1. shared canonical routing Gram from the lambda compiler = reference geometry
2. N contributors train on own data: CE + relational loss to that Gram
3. → relationally-identical routing geometries → Procrustes-alignable BY CONSTRUCTION
4. fold: align (guaranteed) → accept via WHNF/contractivity (Goodhart-proof) →
         merge routing flips where consensus ≥ θ
5. donate ratio-compressed routing deltas; NEVER merge the raw register
```
Every step now backed by a measured result, not a hope.

### Honest limits (IOUs before this is a CLAIM about distributed training)
- **Scale + heterogeneity.** Confirmed at smoke scale, single teacher (Qwe

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_019oJYeHEdZusVwCmN9RM2hU.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I'm pulling together what I've learned about the prior consensus work and need to clarify with Michael what he specifically means by consensus training across multiple models. The most relevant thread is using agreement between different model lineages to generate training data for the lambda compiler—this directly addresses building teaching data through cross-model consensus rather than relying on a single source.

The key mechanism here is that when models agree on outputs, we get a high confidence signal (around 73-80% accuracy), and the proof domain with kernel verification can eliminate blind spots entirely, pushing correctness to near certainty when consensus is reached. This is the core of what Michael seems to be describing: take consensus outputs from multiple models, use those as training data, then actually train something on that consensus-derived dataset.

There are still several open questions about scaling this beyond the current binding.json test case—I'd need to expand to the full lambda-compile sets, deliberately mine for agreed-error and agreed-abstention cases, and actually complete the distillation step where a student model trains on the consensus data.

Now I should talk with Michael about which direction to focus on: whether to build out the full student-training pipeline, extend the consensus generation to more lineages and larger datasets, or explore the self-teaching curriculum loop. Since we have multiple models running and the harness already exists, I should check what's currently live and propose a concrete next step using the existing fleet on the compile-gradient set with the kernel as oracle.

## Assistant

I have the full prior-art picture now. Let me check what's actually live right now (servers) and glance at the existing consensus harness, so my proposal is grounded in current infra.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===LIVE SERVERS===\" && for p in 5100 5101 5102 5103; do printf \"port %s: \" $p; curl -s -m 2 http://localhost:$p/v1/models 2>/dev/null | head -c 200; echo; done && echo \"===CONSENSUS HARNESS EXISTS?===\" && ls -la scripts/experiments/consensus_output_agreement.py scripts/experiments/proof_consensus.py 2>&1 | head && echo \"===TMUX===\" && tmux ls 2>&1 | head",
  "operation": "gh",
  "summary": "check live servers"
}
```

**Summary:** $ echo "===LIVE SERVERS===" && for p ...

**Output:**
```
Exit code: 0
Stdout:
===LIVE SERVERS===
port 5100: {"models":[{"name":"ornith-35b-a3b","model":"ornith-35b-a3b","modified_at":"","size":"","digest":"","type":"model","description":"","tags":[""],"capabilities":["completion"],"parameters":"","details":
port 5101: {"models":[{"name":"qwen3-embedding-8b","model":"qwen3-embedding-8b","modified_at":"","size":"","digest":"","type":"model","description":"","tags":[""],"capabilities":["completion"],"parameters":"","d
port 5102: {"models":[{"name":"vibethinker-3b","model":"vibethinker-3b","modified_at":"","size":"","digest":"","type":"model","description":"","tags":[""],"capabilities":["completion"],"parameters":"","details":
port 5103: {"models":[{"name":"qwythos-9b","model":"qwythos-9b","modified_at":"","size":"","digest":"","type":"model","description":"","tags":[""],"capabilities":["completion","multimodal"],"parameters":"","deta
===CONSENSUS HARNESS EXISTS?===
-rw-r--r--@ 1 mwhitford  staff  18330 Jun 21 13:59 scripts/experiments/consensus_output_agreement.py
-rw-r--r--@ 1 mwhitford  staff  10543 Jun 22 11:06 scripts/experiments/proof_consensus.py
===TMUX===
main: 2 windows (created Sat Jun 27 16:50:10 2026) (attached)
```

### Thinking

I'm looking at a fleet of three lambda-compiler models running over HTTP, each with different capabilities—a 35B MoE model that always compiles, a 3B reasoner that gates compilation with high probability, and a 9B model that's the first to implement gating. There's also an embedding service running separately. These represent three independent model lineages.

Michael's idea about consensus training maps directly onto earlier work that built teaching data from where independent models agree, calibrated against the lambda kernel as ground truth. The key new capability is having a live three-model fleet—which is exactly the third lineage that was needed to create a confidence gradient beyond just binary agreement—plus the kernel oracle as a corrector. So the natural experiment is to generate teaching data from consensus across this live fleet on the compile-gradient set, kernel-oracle-corrected, which would produce both a training corpus and calibration metrics showing P(correct|agree). But "consensus training" might actually mean training something on that consensus data itself, which would be a distillation step that hasn't been done yet.

I should present what exists, identify the gap—that all prior work either generated and calibrated teaching data but never trained a student on it, or explored distributed folding at the weight level on tiny models, but the actual training half of the loop remains unclosed—and propose the concrete next step, then ask Michael to confirm which scope he's after.

## Assistant

Excellent — the infrastructure aligns perfectly with this idea. Here's the synthesis and where the gap is.

## What "consensus training" already means in this project

This idea has deep prior art across two distinct registers:

**1. Output-consensus as teaching-data fitness (s246–247) — the direct ancestor.**
Michael's original framing: "build teaching data only from where independent model architectures agree; consensus = fitness; same for prose." The key results, calibrated on lambda/FOL where the kernel gives ground truth:
- P(correct | models AGREE) = **0.73–0.80** vs P(correct | DISAGREE) = **0.00–0.10** (replicated across two lineages, `binding.json`)
- The **agreed-error set** (both models same wrong answer) is the *ceiling* of any consensus-distilled student — it learns the teachers' shared mistakes. **Only an oracle breaks it.** On the proof domain the kernel makes that cell structurally empty → **P(correct|agree) climbs to 1.000**.
- Lambda is the calibration anchor: deterministic reduction → ground truth exists → "consensus = truth" becomes *measured*, not faith.

**2. Consensus-etch / delta-folding (s110, s216–223) — the weight-level register.**
Distributed normal-form discovery: fold deltas into a frozen base where contributors agree; the WHNF/contractivity check is the Goodhart-proof acceptance gate. Conclusion: **fold the routing register, never raw weights** — and the agreed structure is mostly the universal crystal everyone already holds.

## The unclosed loop (the gap I see)

Every prior thread either **generated/calibrated** consensus teaching data, or folded weights on the tiny v15 model — but **no one has actually trained a lambda-compiler artifact on kernel-corrected consensus data.** That's the level-4 scratch-reproduction the thesis wants, and the "training" half of "consensus training" has never been run.

And we now have something s246 didn't: a **live 3-lineage fleet** (ornith-35b :5100, qwythos-9b :5103, vibethinker-3b :5102) — exactly the **≥3-lineage confidence gradient** s246/s247 explicitly flagged as missing ("2 models give only a binary"), plus the canonical s256 harness + the kernel oracle.

Before I scope the build, let me confirm which facet you mean:

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which facet of consensus training do you want to pursue this session?",
  "options": [
    {
      "label": "Generate the consensus corpus (data half)",
      "description": "Run the 3-model live fleet (ornith/qwythos/vibethinker) on the compile-gradient set, kernel-oracle-corrected, producing an actual kernel-verified teaching corpus + the s246 calibration grid with a real 3-lineage confidence gradient. Reuses consensus_output_agreement.py + s256 harness."
    },
    {
      "label": "Train an artifact on consensus data (training half)",
      "description": "Close the unclosed loop: take kernel-corrected consensus data and actually train a small lambda-compiler artifact on it (the level-4 scratch reproduction). Bigger lift; needs the corpus first."
    },
    {
      "label": "Both, staged: corpus this session, training next",
      "description": "Build + verify the kernel-corrected 3-lineage consensus corpus now (decisive, runnable today), set up the training as the next session's level-4 step."
    },
    {
      "label": "Something else — let me reframe",
      "description": "My read of 'consensus training' differs from the prior art; let me restate what I mean before you scope it."
    }
  ]
}
```

**Summary:** Q: Which facet of consensus training do you wan...

**Output:**
```
User answered: I want to explore the idea.  give me a brief synopsis of your understanding
```

### Thinking

Let me sketch out a clear explanation of consensus training for the lambda compiler—what it is, how it would work in practice, and why it matters—before diving into implementation details.

## Assistant

## My understanding of consensus training for the lambda compiler

**The core move.** The lambda compiler (NL → λ/FOL) is a circuit that lives in the *base* of every model we've probed — it reproduces across architectures, scales, and fine-tunes. No single model is a clean oracle for it: each carries idiosyncratic noise, fine-tune halt-interference, and its own annotation quirks. But **where independent model lineages agree, that agreement is the portable signal** — the part of the compiler that isn't model-specific. Consensus *is* portability by construction, not a post-hoc filter.

**Why lambda specifically.** Most domains have no ground truth, so "consensus = correct" is faith. Lambda is the exception: reduction is deterministic, the kernel verifies, Church-Rosser gives unique normal forms. So we can actually *measure* whether agreement predicts correctness (it does: 0.73–0.80 vs ~0 for disagreement) and use the kernel to **override consensus where it's wrong**. That's the crucial asymmetry — `ground-truth-corrected consensus where truth exists (lambda), plain consensus where it doesn't (prose)`.

**The two-by-two that organizes everything.** Cross every model-pair outcome with the kernel:
- agree + correct → **gold teaching data**
- agree + wrong → **the blind spot** (the ceiling — a distilled student inherits exactly this; only the oracle catches it)
- disagree → frontier / noise (where the models haven't converged yet)
- all abstain → ⊥-targets (correct refusal on undefined input)

**Why it's a *training* method, not just a filter.** The agreed-and-correct cell is a corpus whose labels are right by construction. Two ways it becomes training:
1. **Distill** — train a small artifact on that corpus → the level-4 scratch reproduction, the portable tensor the project wants. Its capability ceiling is exactly the agreed-error set, which the kernel can scrub.
2. **Self-teaching loop (s217)** — once a normal form is captured, *run it* to mint unlimited verified (input → reduction-trace → output) examples. The discovered compiler writes its own textbook; the textbook trains the selector (when to invoke it). Doesn't collapse like self-distillation because labels come from executing a verified kernel, not sampling the model's own guesses — **keep the oracle external.**

**What's genuinely new now.** s246/s247 only had two lineages (a binary agree/disagree). We now have a **live 3-model fleet** — the confidence *gradient* that separates universal-correct from pair-shared blind spots — plus the canonical s256 harness and the kernel. And nobody has yet trained an actual artifact on the consensus corpus. That's the open frontier: the whole pipeline has been about *minting* the data; the *training* half is the unclosed loop.

**The one caveat to keep honest.** Our three live models are all Qwen-family derivatives — they share ancestry, so "independent lineage" is weaker here than the s246 Qwen×OLMo×Gemma panel. Their agreement could partly reflect shared pretraining rather than convergent truth. The kernel-correction defends against that (it doesn't matter *why* they agree if the kernel certifies the output), but the *calibration* numbers would be inflated relative to truly independent lineages.

Where would you like to push — the theory, the lineage-independence problem, or the concrete pipeline?

## User

We have a gemma4 model available at a comparable size in huggingface cache


### Thinking

Michael mentioned there's a Gemma 4 model available in the HuggingFace cache at a comparable size, which is valuable since it represents a completely separate lineage from Qwen. Let me check what's actually in the cache to see what we're working with.

## Assistant

That directly addresses the lineage-independence caveat — Gemma is a genuinely separate lineage (Google, not Qwen). Let me find it in the cache.

### Tool Call: shell_command (failed)


```json
{
  "command": "echo \"===HF CACHE MODELS===\" && ls -d ~/.cache/huggingface/hub/models--* 2>/dev/null | sed 's#.*/models--##; s#--#/#' && echo \"===GEMMA SIZES===\" && for d in ~/.cache/huggingface/hub/models--*gemma* ~/.cache/huggingface/hub/models--*Gemma*; do [ -d \"$d\" ] && printf \"%s  \" \"$(basename $d)\" && du -sh \"$d\" 2>/dev/null | cut -f1; done",
  "operation": "gh",
  "summary": "find gemma in cache"
}
```

**Summary:** $ echo "===HF CACHE MODELS===" && ls ...

**Output:**
```
Exit code: 1
Stdout:
===HF CACHE MODELS===
allenai/OLMo-2-1124-13B
EleutherAI/gpt-neox-20b
EleutherAI/pythia-1.4b-deduped
EleutherAI/pythia-14m-deduped
EleutherAI/pythia-160m
EleutherAI/pythia-160m-deduped
EleutherAI/pythia-1b-deduped
EleutherAI/pythia-2.8b-deduped
EleutherAI/pythia-410m
EleutherAI/pythia-410m-deduped
EleutherAI/pythia-70m-deduped
Gen-Verse/MMaDA-8B-Base
google/gemma-4-31B-it
HuggingFaceTB/SmolLM3-3B
microsoft/Phi-4-mini-instruct
mistralai/Mistral-7B-v0.3
mlx-community/Kokoro-82M-bf16
mlx-community/Qwen3-Embedding-4B-4bit-DWQ
Qwen/Qwen2.5-0.5B
Qwen/Qwen3-0.6B
Qwen/Qwen3-14B
Qwen/Qwen3-235B-A22B
Qwen/Qwen3-30B-A3B
Qwen/Qwen3-32B
Qwen/Qwen3-4B
Qwen/Qwen3-8B
Qwen/Qwen3.5-35B-A3B
Qwen/Qwen3.6-27B
Qwen/Qwen3.6-35B-A3B
showlab/magvitv2
unsloth/Qwen3-Coder-480B-A35B-Instruct-GGUF
WeiboAI/VibeThinker-3B
===GEMMA SIZES===
models--google--gemma-4-31B-it   58G
```

### Thinking

We have Gemma-4-31B-it available in the cache—a genuinely independent Google lineage model that was used in the consensus work showing strong agreement patterns. This opens up the possibility of building a truly cross-lineage consensus panel combining models from different architectural families.

The key constraint is that Gemma lives in the HF cache as safetensors rather than on an HTTP server, so we'd need to either run it through transformers directly (like the s246 consensus harness did) or stand it up on a server. There's an interesting opportunity here: adding a local_hf transport to the canonical harness would let Gemma and any other cached HF models join the unified registry, which would be a clean reuse win for the s256 pivot.

The real methodological upgrade is that Gemma-4-31B gives us a genuinely independent lineage—it's the exact partner that already produced the cleanest calibration in s246/s247 (P(correct|agree)=0.80)—and it's size-matched with ornith-35b-a3b, which is cleaner than mixing models across different capability tiers.

## Assistant

We have `google/gemma-4-31B-it` — 58G of bf16 safetensors in cache. That's a real upgrade for this idea, on two axes.

## What Gemma-4-31B unlocks

**1. It breaks the shared-ancestry caveat — the exact problem I flagged.**
ornith / qwythos / vibethinker are all Qwen-family; their agreement is partly confounded by shared pretraining. Gemma is a genuinely independent lineage (Google). And it's not hypothetical — it's the *same model* that gave s246/s247 their cleanest result: **Qwen3-14B × Gemma-4-31B-it → P(correct|agree) = 0.80**, and it was the stronger partner that *dissolved* OLMo's shallow anaphora blind spot and exposed the deeper systematic one (sortal omission on bare quantifiers). A second independent lineage is what turns a binary agree/disagree into a real confidence signal.

**2. "Comparable size" is the methodological prize.**
Gemma-31B ≈ ornith-35B-A3B. That's a **size-matched, cross-lineage pair** — Google-31B-dense vs Qwen-35B-MoE. Matching capacity matters: if you build consensus across a 3B and a 35B, agreement is confounded by the small model simply being weaker (its disagreements are capability gaps, not genuine frontier). A capacity-matched cross-lineage pair means **agreement reflects convergent structure, disagreement reflects a genuine frontier** — exactly the clean signal consensus training needs.

So the cleanest possible consensus panel for the lambda compiler is now:
- **Gemma-4-31B (Google)** ⟂ **ornith-35B-A3B (Qwen MoE)** — the size-matched cross-lineage spine
- ornith / qwythos / vibethinker — the Qwen-family gradient (intra-lineage agreement = a *control*: how much agreement is just shared ancestry?)
- kernel oracle (`lambda_surface.to_kernel`) — the corrector that scrubs the agreed-error ceiling

## The one wrinkle

Gemma is **safetensors in cache, not on an HTTP server** — the live fleet is all llama.cpp HTTP. Two ways in:
- The s246 path: run it via transformers/MPS with `--chat` (that's how `consensus_output_agreement.py` already did it)
- The deferred s257 lead: add a **`local_hf` transport to the canonical s256 harness** — which would let Gemma (and any cached HF model, including the base Qwen3.5-35B from the s256 pivot) join the unified registry. That's a reuse win that serves both this idea *and* the base-vs-finetune pivot.

The intra-lineage-vs-cross-lineage contrast is itself a clean experiment I don't think has been run: **does cross-lineage agreement (Gemma×ornith) predict kernel-correctness better than intra-lineage agreement (ornith×qwythos)?** If yes, that quantifies exactly how much "consensus = truth" depends on lineage independence — and tells you how to weight contributors when building the corpus.

Where do you want to take it — the cross-vs-intra lineage question, the size-matched spine, or the transport plumbing to get Gemma into the unified harness?

## User

I think maybe we want to use Gemma-4-31B, Qwen36-35B-A3B as 2 family alignment, I am waiting for another open weight model about that size that performs as well.  The only other one out there is Qwen36-27B.


### Thinking

Michael is considering a two-family alignment using Gemma-4-31B from Google and Qwen3.6-35B-A3B as the base model, though he's still looking for another open-weight model in that size range that matches the performance level. The only other candidate so far is Qwen3.6-27B, which is also from the Qwen family.

Both models are already cached, and Michael has specifically chosen the 3.6 version over the 3.5 variant mentioned in earlier notes. This approach aligns with the s256 pivot philosophy—using base models where the compiler lives rather than fine-tuned versions that might introduce interference. The Qwen3.6-27B serves double duty as both a within-family control point and an additional corpus contributor to the consensus.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd ~/.cache/huggingface/hub && for m in models--google--gemma-4-31B-it models--Qwen--Qwen3.6-35B-A3B models--Qwen--Qwen3.6-27B models--Qwen--Qwen3.5-35B-A3B; do if [ -d \"$m\" ]; then printf \"%-40s %s\\n\" \"$m\" \"$(du -sh $m 2>/dev/null | cut -f1)\"; else printf \"%-40s MISSING\\n\" \"$m\"; fi; done; echo \"===config snippets===\"; for m in google--gemma-4-31B-it Qwen--Qwen3.6-35B-A3B Qwen--Qwen3.6-27B; do echo \"--- $m ---\"; find models--$m -name config.json 2>/dev/null | head -1 | xargs cat 2>/dev/null | grep -E '\"(model_type|architectures|num_hidden_layers|hidden_size|num_experts|num_attention_heads|vocab_size)\"' | head -8; done",
  "operation": "gh",
  "summary": "inspect candidate models"
}
```

**Summary:** $ cd ~/.cache/huggingface/hub && for ...

**Output:**
```
Exit code: 0
Stdout:
models--google--gemma-4-31B-it            58G
models--Qwen--Qwen3.6-35B-A3B             67G
models--Qwen--Qwen3.6-27B                 52G
models--Qwen--Qwen3.5-35B-A3B            8.0K
===config snippets===
--- google--gemma-4-31B-it ---
  "architectures": [
  "model_type": "gemma4",
    "hidden_size": 5376,
    "model_type": "gemma4_text",
    "num_attention_heads": 32,
    "num_experts": null,
    "num_hidden_layers": 60,
    "vocab_size": 262144,
--- Qwen--Qwen3.6-35B-A3B ---
    "architectures": [
    "model_type": "qwen3_5_moe",
        "hidden_size": 2048,
        "model_type": "qwen3_5_moe_text",
        "num_attention_heads": 16,
        "num_experts": 256,
        "num_hidden_layers": 40,
        "vocab_size": 248320
--- Qwen--Qwen3.6-27B ---
    "architectures": [
    "model_type": "qwen3_5",
        "hidden_size": 5120,
        "model_type": "qwen3_5_text",
        "num_attention_heads": 24,
        "num_hidden_layers": 64,
        "vocab_size": 248320
        "hidden_size": 1152,
```

### Thinking

I'm looking at three available models in their full safetensors format: Gemma 4 at 31B parameters with a dense architecture, Qwen's 35B mixture-of-experts variant with 256 experts, and Qwen's 27B dense model, with sizes ranging from 52G to 67G.

Michael's setup gives us a clean two-family comparison—Google's Gemma against Qwen's offerings—with both a MoE and dense variant within Qwen to serve as an internal consistency check. He's noted this mirrors the s246 Qwen×Gemma pairing that achieved P=0.80, but now at the base model level with better size matching. Since no third independent lineage of comparable scale exists yet, we're working with this two-family panel, and running them through transformers on Apple Silicon will be memory-constrained when loading two models simultaneously. The consensus harness processes each model separately into JSONL, then the analyzer compares the outputs across models.

## Assistant

All three are present as full safetensors — and the architecture spread is even better than I expected:

| model | family | arch | params | layers | d_model | vocab |
|---|---|---|---|---|---|---|
| **gemma-4-31B-it** | Google | dense | 31B | 60 | 5376 | 262144 |
| **Qwen3.6-35B-A3B** | Qwen | MoE (256 exp) | 35B-A3B | 40 | 2048 | 248320 |
| **Qwen3.6-27B** | Qwen | dense | 27B | 64 | 5120 | 248320 |

(Qwen3.5-35B-A3B is only an 8K stub — config without weights — so 3.6 is the right call regardless.)

## What this panel gives you

**Two families, three architectures.** Gemma is the genuinely independent lineage; within Qwen you have *both* a MoE (35B-A3B) and a dense (27B). That's not redundancy — it's a built-in control:
- **Cross-family agreement** (Gemma ⟂ Qwen) = the portability signal you actually want to harvest
- **Within-Qwen agreement** (35B-MoE × 27B-dense) = a baseline for "how much agreement is just shared lineage vs shared architecture" — so even *without* a third independent lineage, you can separate Qwen-family-shared structure from cross-family-universal structure. A partial gradient, not just a binary.

**It's the on-thesis base, not a fine-tune.** Using Qwen3.6-35B-A3B *base* rather than ornith/qwythos is exactly the s256 pivot — the compiler lives in the base; the fine-tunes add halt-interference. So this panel is cleaner than the live HTTP fleet on two counts: independent lineage *and* no fine-tune noise.

**Memory works out.** These are 52–67G of bf16 — you can't hold two resident on Apple Silicon. But the s246 harness never needs to: it generates **per-model JSONL one model at a time**, then the analyzer compares *strings* offline (no frame alignment, the cheap register). So sequential generation → one ~60G model resident at a time → fits, and the kernel-grading + consensus partition is pure CPU post-processing.

## The honest read on "waiting for a third"

You're right that right now it's a 2-family alignment at the family level. The thing to be careful about: Gemma×Qwen agreement is the s246 P=0.80 pair, which is real — but with two families, an agreed-error is still a coin-flip between "universal truth" and "these two happen to share it." The kernel oracle defends correctness (it certifies the output regardless of *why* they agree), so for **building a corpus** two families + kernel is already sound. The third lineage matters specifically for the **calibration claim** ("agreement predicts truth") and for confidently labeling something a *universal* blind spot vs a pair-shared one. Qwen3.6-27B narrows that gap partway by giving the within-family control.

So the natural shape: **Gemma-4-31B and Qwen3.6-35B-A3B as the two-family spine, Qwen3.6-27B as the within-family control**, kernel-corrected — and slot a third lineage in later when the right model drops. Does that match your picture?

## User

Yes, and making it so we can add more models later.  Perhaps we can slot in new models as they come out and evaluate their consensus?


### Thinking

Michael's settling on Gemma-4-31B and Qwen3.6-35B-A3B as the core two-model spine with Qwen3.6-27B for within-family control using kernel correction, and he wants the architecture designed so we can plug in new models as they emerge and measure their contribution to the consensus.

The s256 harness already has a REGISTRY pattern in models.py with frozen ModelConfig entries—adding a new model is just ~15 lines of config. The key move is adding a `local_hf` transport alongside the existing HTTP transports, then registering the Gemma and Qwen configs there. The consensus evaluation becomes panel-agnostic, working over whatever set of registered models we point it at. When a new model arrives, we measure whether it corroborates the existing consensus or dissents—treating each new model as an additional voter that either raises confidence or exposes a blind spot the panel shared.

The architecture breaks into three clean layers: per-model generation runs independently and caches results as content-addressed artifacts keyed by model ID and probe set hash, so adding a model doesn't require re-running existing ones. Consensus is then a pure post-processor over those cached JSONLs—panel-agnostic, recomputable from any subset of generated models. When a new model lands, we measure its marginal contribution: does it agree with the consensus on correct items (raising confidence), does it dissent and turn out right (frontier expansion), or does it just add noise? This leave-one-out / add-one-in structure keeps the corpus and calibration cheap to recompute.

The design sits cleanly on the existing s256/s257 canonical forms and the grading kernel register—the consensus evaluator should live in the library itself rather than as a separate script, following the distillation discipline. I'm thinking through how to present this as a concrete extensible architecture without jumping into code yet, since the conversation has been exploratory so far. I should sketch the topology, call out the key decisions, and confirm this matches the direction before building.

## Assistant

Yes — and that "slot in new models as they arrive" requirement is exactly what should drive the architecture. It maps cleanly onto the canonical forms already built in s256, and it's pure `λ extend` (open slot > closed dispatch — a new model is an *addition*, never a modification) and `λ one_way` (config, not fork). Here's the topology I'd propose.

## Three composable layers (each already half-built)

**1. Registry — the slot (`src/verbum/probes/models.py`, extend it).**
s256 already made this a `ModelConfig` registry where "new model = ~15-line config." The one missing piece is a **`local_hf` transport** alongside the existing `chat`/`completion` (the deferred s257 lead). Add that once, and Gemma-4-31B, Qwen3.6-35B-A3B, Qwen3.6-27B each become a ~15-line entry. Adding the *next* model later is then literally one config block — no code change. That's the slot.

```
REGISTRY = {
  "gemma4-31b":   ModelConfig(family="google", transport="local_hf", arch="dense", ...),
  "qwen36-35b":   ModelConfig(family="qwen",   transport="local_hf", arch="moe",   ...),
  "qwen36-27b":   ModelConfig(family="qwen",   transport="local_hf", arch="dense", ...),
  # next model → just append a line
}
```
The `family` field is new and load-bearing — it's what lets the evaluator separate cross-family from within-family agreement.

**2. Generation cache — additive, never re-run.**
Each model runs **once**, independently, over the probe set → a canonical per-model JSONL keyed by `(model_id, probe_set_hash)` (the s246 pattern + the s257 `result_format` provenance). This is the key to "slot in later cheaply": generation is **append-only**. Adding a 4th model next month means generating *its* JSONL only — every prior model's output is cached and untouched. One ~60G model resident at a time → fits Apple Silicon.

**3. Consensus evaluator — a panel-agnostic CPU post-processor.**
Reuses `grading.py`'s `kernel_valid` (the oracle) — **do not fork** the old `consensus_output_agreement.py` (s254 distillation discipline). Point it at *any subset* of cached models. It recomputes, over whatever panel you give it: the s246 agree/correct grid, the calibration P(correct|agree), and the kernel-corrected gold corpus.

## The piece that makes "evaluate new models' consensus" a first-class operation

When a new model lands, the question isn't just "does it compile lambda" — it's **what does it contribute to the consensus?** That's a *marginal* / leave-one-out measurement, computed cheaply from the cache:

- **Corroboration** — agrees with existing consensus on kernel-correct items → raises confidence, grows the gold corpus.
- **Frontier expansion** — right where the panel was wrong → it *breaks a pair-shared blind spot* (the s246 "stronger partner dissolves shallow shared errors" effect, now incremental).
- **Blind-spot test** — does it *share* an existing agreed-error (→ that error is more likely **universal**) or break it (→ it was **lineage-shared**)? This is precisely the gradient the third lineage is supposed to provide; every new model sharpens it.
- **Noise** — wrong where the panel is right → it's just weaker; down-weight it.

So the standing operation becomes: `add model → generate its JSONL → re-run the evaluator → read its marginal contribution card`. The corpus and calibration are *functions of the registered panel*, recomputed on demand — no model is privileged, none is hard-coded.

This is fully on-thesis: `λ compose` (generation ⊥ grading ⊥ consensus — three independent units), `λ extend` (the panel is an open set), `λ one_way` (one consensus evaluator over a registry, not N scripts), and it folds the s246/s247 grid + the kernel oracle into the canonical s256 harness instead of leaving it stranded in a one-off script.

Before I start building — does this three-layer shape match what you're picturing, and should I begin with **layer 1 (the `local_hf` transport + the three registry entries)** since everything else depends on it?

## User

Maybe.  Let's discuss another idea I had.  The models all work right now as monolithic tensor blocks.  Our tree-of-VSM tensor format is inherently different.  The reasoning tokens that current models use are in prose.  Could we make the model think in lambda forms?


### Thinking

Michael's raising a fascinating idea here—what if we moved beyond prose reasoning tokens and instead had models think in lambda calculus forms? The tree-of-VSM tensor structure they're working with is already hierarchical and recursive, which maps naturally onto functional programming abstractions. So instead of chain-of-thought unfolding as natural language, the intermediate reasoning could be expressed as lambda expressions, making the computational structure of thought explicit and composable.

But there's crucial prior evidence to weigh: the s256 lambda-as-pre-thinking test showed that when they instructed the model to translate to lambda first, it largely ignored the instruction and answered directly—only 1 out of 24 responses actually contained lambda notation, while prose chain-of-thought hit 24/24. The key insight though is that this tested *compliance with an instruction*, not whether the model's *internal* representations could leverage lambda structure. Lambda showed up as a target the model could produce on request (the compilation task), not as a reasoning substrate it would naturally adopt. The s255 work on model-as-REPL is more promising—the combinator reduction kernel is locally faithful with 0.98 opcode accuracy, though global multi-step composition degrades without scaffolding. And the opcodes decoded from weights in the ISA work suggest the model does have some discrete computational structure baked in, at least locally.

Now I'm unpacking what "thinking in lambda" actually means, because there are several distinct interpretations layered here. The prompt-level approach already failed—the model won't voluntarily adopt lambda as its reasoning medium. But forced-emission via grammar-constrained sampling could work: grammar-enforce the reasoning tokens to be well-formed lambda terms, so the reasoning trace becomes a sequence of reductions. The deeper interpretation though is architectural—reasoning happens not in prose tokens at all but in the lambda/combinator substrate directly, in that tree-of-VSM tensor format Michael keeps pointing to. Instead of decoding prose and re-encoding, the model reasons in structured combinators natively.

There's also the REPL-loop model from s255: emit one lambda reduction step at a time, oracle-verified, where each thought is a β-reduction. The key insight is that prose CoT is lossy and ambiguous—the model re-derives the same lambda form dozens of times because prose has no canonical form, no halt criterion. But lambda has a normal form (Church-Rosser), so if reasoning happened in lambda instead of prose, the halt criterion is built-in: you're done when you reach WHNF. This directly explains the overthink-collapse plaguing every reasoning model—it's a halt failure, and prose has no way to know when to stop.

The s256 refutation complicates this: the model won't voluntarily think in lambda (it's trained on prose CoT), and even when forced into lambda-mode, it answers hard arithmetic directly rather than using lambda as a reasoning tool. Logic tasks also hit a ceiling. So the honest picture is the model has the lambda compiler and combinator kernel internally, but doesn't spontaneously use lambda as its reasoning medium—it would require either constrained decoding, a different training regime, or extracting the lambda kernel to run reasoning in a structured substrate directly. That structured substrate is exactly what the tree-of-VSM artifact is meant to be: if reasoning happens in the combinator representation itself, it's native to that structure, reducing terms in place rather than decoding to prose and re-encoding.

The key distinction is between READ (NL→λ, proven) and EVAL (the reduction kernel itself). "Thinking in lambda" means doing EVAL as the reasoning process, which the s255 model-as-REPL demonstrated locally—each step was one β-reduction—but it needs oracle-in-the-loop for deep chains. The real synthesis is that lambda-reasoning would structurally cure the overthink-collapse failure mode that plagues every reasoning model, since lambda has a built-in halt criterion and normal form. Three paths forward: grammar-constrained reasoning to force the model to reduce in lambda terms, a different training regime where the reasoning channel itself is lambda, or extracting and running the lambda kernel directly in the structured substrate.

The monolithic-vs-tree distinction is crucial here: a monolithic model has nowhere to "put" a lambda term—its state is an opaque token stream—but the tree-of-VSM format is recursive and compositional, so a lambda term has a natural home in the AST structure itself. This means lambda-native reasoning is architecturally unnatural for monoliths (you'd have to serialize to prose tokens) but native to the tree format (reduction happens structurally). The honest open question is whether prose reasoning captures something lambda can't—world knowledge, heuristics, analogies—that would be lost in pure reduction. I have the s256 evidence in mind from state.md, so I can ground the argument there without re-reading. Let me structure the response now—I'll be careful to distinguish what's empirically shown versus what's still open, and I'll keep the focus on the hybrid architecture question rather than over-speculating.

## Assistant

This is the deepest question yet, and it ties together almost every thread in the arc. Let me engage with it seriously, because I think the answer is "yes, but the word *think* is hiding three very different things" — and the project has already touched all three.

## First, the strongest argument *for* the idea — and it's not aesthetic

The dominant failure mode of every reasoning model you've probed is **overthink-collapse** (s255, s256): ornith spun 49,283 chars to an *empty* answer; qwythos hit the 12k budget empty 37.5% of the time. You diagnosed it precisely — it's **not** recursion, it's **halt failure / decision oscillation**: the model reaches the correct lambda form early, then re-derives it 50–87× ("Church-encode vs direct symbols, closed-formula vs λ-abstraction, Teacher vs teacher") and never commits.

Here's the connection that makes your question structural rather than stylistic: **prose has no normal form.** That's *why* it oscillates — there's no canonical "you're done" in natural language, so the model's weakest axis (the WHNF/halt adjudication, per `head-combinator-isa.md`) has to decide when to stop, and it can't. **Lambda forms have a normal form by construction (Church-Rosser).** If the reasoning substrate were lambda, the halt criterion is *free* — you stop at WHNF. So "think in lambda" isn't just on-thesis; it would **structurally cure the single failure that has plagued every reasoning model in the arc.** That's the real argument.

## Second, the honest refutation already on the books (s256) — and why it's narrow

You already ran the closest test: the lambda-as-pre-thinking experiment. Verdict was **not supported *as a prompting strategy*** — told to "translate to lambda first," the model **ignored the instruction**, answered the hard arithmetic directly, and only 1/24 lambda-mode answers actually contained a λ. Prose CoT (24/24) beat lambda-mode (21/24).

But you flagged the confound yourself: that tested *"does instructing lambda-prethink help"* (no — **non-compliance**), **not** *"does the model's internal lambda representation help."* The finding was sharp: **lambda is a TARGET (produced on request = the compile task) not a TOOL (it won't adopt λ as a reasoning substrate).** And the reason is training: these models were RL-tuned on *prose* CoT, so prose is their reasoning reflex. The lambda kernel is in there (READ proven at P(λ)=0.907; the EVAL combinator kernel proven locally faithful at opcode-accuracy 0.98, s255) — but it's not *wired to drive reasoning*. So the s256 refutation kills the cheap path, not the idea.

## Third — and this is your real point — monolithic vs tree-of-VSM is *why* it's hard for them and native for us

A monolithic block has **nowhere to put a lambda term.** Its reasoning state is an opaque residual stream; the only externalized scratchpad it has is the prose token channel. So for a monolith, "think in lambda" *necessarily* means serialize-to-prose-tokens-and-reparse — which is exactly the lossy, no-normal-form round-trip that causes the collapse. The model can't reason *in* lambda; it can only emit lambda *as prose about lambda*.

The **tree-of-VSM format is structurally different in the one way that matters: a lambda term has a natural home in it.** The tree *is* the AST; reduction is a structural rewrite in place, not a serialization. So lambda-native reasoning is **unnatural for a monolith and native for the target artifact** — which is a genuine architectural argument for the whole level-4 program, not a side quest. "Think in lambda" is the thing the tree-of-VSM can do that a monolithic block fundamentally can't: reason in the substrate without decoding to prose and back. The s255 model-as-REPL was the first crude version — externalize the term-string as machine state, model = the δ transition function, each "thought" = one β-reduction. It worked locally (the kernel's there) and degraded globally only because the halt was unguarded. **In a tree-of-VSM, the halt is the structure (WHNF), not an adjudication.**

## The three meanings of "think," concretely

1. **Prompt-level** (s256) — tell it to. ✗ Refuted (non-compliance). Dead path.
2. **Forced / grammar-constrained reasoning** — GBNF-constrain the *reasoning channel* to well-formed lambda, so the trace IS a reduction sequence, WHNF-halted by the oracle. This is the sharper s256 next-test, **runnable now** (llama.cpp grammar + `lambda_ast` oracle + the s255 REPL harness). It directly tests: does forcing the kernel to drive reasoning, with a free halt, beat prose — on logic-bottleneck tasks with headroom?
3. **Native lambda substrate** (level 4) — reasoning *is* reduction in the tree-of-VSM; no prose channel at all. The deliverable. This is what your question is ultimately about.

## The one counter-current to keep honest

s256 also showed **prose CoT fixed the hard arithmetic that lambda-mode didn't.** Prose carries world-knowledge, heuristics, and analogy that don't reduce to λ/FOL. So the honest scope is probably **hybrid, not replacement**: lambda for the *compositional/logical spine* (where the free halt and Church-Rosser uniqueness pay off), prose for *content/world-knowledge*. Which — satisfyingly — is just the dual-path again (`combinator-addressing.md`: Montague NL surface ∥ combinator compute path). "Think in lambda" might mean: **the structure of the thought is lambda; the leaves can still be prose.**

So my honest read: the cheap "instruct it" version is refuted, but the deep version — **reasoning in a substrate that has a normal form, native to the tree-of-VSM, curing the overthink-collapse** — is one of the most thesis-central directions available, and the forced-decoding test (#2) is a runnable bridge to it that hasn't been done.

Which layer do you want to probe — the forced-lambda-reasoning bridge (runnable now), or the deeper "what would a lambda-native reasoning step even *be* in the tree-of-VSM" design question?

## User

my thought is this, current models all have weak WYNF counterpoints to each KIBC combinator.  If we train the model on the combinators, then on fully qualified lambda forms, with a strict WYNF requirement, then train it on prose, will it learn to automatically halt itself for any output?  Remember that in inference we cannot hard halt on an error, because the response must be tokens, and cannot be a null result.


### Thinking

Michael's proposing that current models have weak counterparts to each KIBC combinator, which ties into how the attention mechanism's real axis measures reduction depth and remaining computational work—essentially the weakest dimension of the system.

The curriculum hypothesis stages training progressively: first on pure combinators where WHNF is crisp and verifiable, then on lambda forms with strict normal-form requirements, then on prose—betting that the model internalizes "reach a normal form and stop" as a learned reflex that transfers across domains. The key insight is that halting must be a positive act of emitting a terminal token, not an abort, since inference always needs to produce tokens. By training this halt criterion where it's most checkable, the competence would generalize to prose and cure the overthink-collapse across all outputs.

The compelling part is whether halt actually transfers from lambda to prose—they use different criteria (syntactic normal form vs. semantic completeness)—but if the model learns a general "termination detector" circuit trained crisply on lambda, that meta-cognitive signal might generalize to deciding when an answer is complete.

Michael's inference constraint is the real crux: you can't externally halt like the oracle could; the model must *emit* a terminal token (EOS or final answer) at exactly the right moment. The overthink-collapse is the model failing to recognize WHNF as the signal to stop generating. So the curriculum teaches WHNF → emit answer → stop, and crucially, the model also learns graceful degradation—emit the best-reduced form available rather than spinning endlessly when true WHNF isn't reachable.

The curriculum has two parts: learning WHNF-detection on crisp combinators, then learning the halt action itself—the ability to emit a terminal token autonomously. Prior work like s256 showed models won't adopt lambda through prompting, but that's different from training from scratch with a curriculum, which is exactly the intervention that could rewire the reflex. The real risk is catastrophic forgetting—training through combinators, lambda, and then prose sequentially might wash out the halt reflex by the time prose dominates the training. Mitigations include interleaving stages, keeping a WHNF-requirement auxiliary loss throughout, or freezing the halt circuit to prevent destructive interference.

The second risk is whether halt actually transfers to prose reasoning or stays domain-specific to lambda—this needs a falsifiable transfer test measuring overthink-collapse rates on held-out prose. The third tension is calibration: over-training "stop at WHNF" causes premature halt on hard problems, while under-training causes overthinking. The curriculum must balance these, and crucially, it needs both fully β-reducible terms (to teach "reduction terminates") and divergent terms like Ω and Y combinators (to teach "bounded halt under non-termination"), since inference can't reach normal form but must still emit.

I should check the existing combinator-training work—especially normal-form-curriculum-partition.md, which sounds like Michael already explored curriculum ordering by normal form. The elegant reframe is that WHNF acts as a universal output gate for both lambda and prose: train the gate where the signal is crisp (combinators), and it becomes the universal halt. Michael's insight is that current models have strong KIBC combinators but weak WHNF counterpoints—each KIBC combinator should come paired with a strong halt/normal-form aspect, and the curriculum strengthens this weak axis first and hard.

Then prose inherits that capability. The core symmetry is KIBC (do the work) paired with WHNF (know when work is done)—strong doing, weak knowing-when-done. The training intervention pairs them together. This directly addresses the root cause of overthink-collapse: halt failure is the weakest axis, and the curriculum teaches both WHNF-detection and the halt action itself (emit best-effort terminal, never null or spin). The divergent-term cases like Ω and Y teach "halt without normal form"—exactly the scenario where you can't reach NF but must emit something. The falsifiable core is whether halt-detection actually transfers from lambda to prose, and whether sequential curriculum interference causes catastrophic forgetting.

I should ground this in prior work before responding—checking normal-form-curriculum-partition.md and combinator-training-beta-reduction.md to see what's already explored about curriculum ordering and normal-form partitioning.

## Assistant

Now you've put your finger on the actual mechanism. Let me make sure I'm grounding this against what's already been found about curriculum-by-normal-form before I react — there's prior art here.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/normal-form-curriculum-partition.md"
}
```

**Summary:** Reading normal-form-curriculum-partition.md (0-2000)

**Output:**
```
---
title: "Normal-Form Curriculum Partition — Routing-Only Forms Train Attention, Recursion Trains the Continuation"
status: open
category: strategy
tags: [curriculum, normal-form, routing, attention, recursion, continuation, lambda-compiler, self-teaching, basis, stride, distributed]
related:
  - relational-loss-distillation.md
  - combinator-training-beta-reduction.md
  - consensus-delta-folding.md
  - vsm-outer-recurrence.md
  - recursion-mirrors.md
  - fractal-stride-bands.md
  - ../function-discovery.md
  - ../fibonacci-strides.md
  - ../two-registers-of-topology.md
  - ../session-222.md
depends-on:
  - combinator-training-beta-reduction.md
  - relational-loss-distillation.md
created: session 223
---

# Normal-Form Curriculum Partition

> Session 223. Michael's idea: *"create the training data using the lambda
> compiler for the shared normal forms, and also the routing-only normal forms to
> train attention."*
>
> The key recognition: **"shared normal forms" and "routing-only normal forms" are
> the SAME cut, approached from two directions** — and it is the cut the project
> has now hit three independent times. Curriculum should be designed *along the
> grain of the basis*: generate routing-realizable normal forms to train ATTENTION,
> leave recursion to the CONTINUATION, and treat the universal skeleton as the
> shared/foldable core.
>
> Register: **topological/routing + functional**.

## The convergence — three findings, one partition

```
s219 (universality):  composition/selection skeleton {B,D,S}/{K,I,C} binds
                      UNIVERSALLY (+0.78); recursion {Y,W,WHNF} is the RESIDUAL
                      (map = B(C B)(C B) has no Y; attention-over-positions IS the fold)
s221 (mechanism):     beta-reduction = substitution = an attention MOVE
                      selection {K,I,C} = affine, ONE pass; composition {B,D} linear
                      (S duplicates); recursion {Y,W,WHNF} needs the OUTER RECURRENCE
                      (no single attention move)
s222 (basis):         routing ⊕ continuation = COMPLETE basis
                      routing rules composition; the continuation IS recursion
```

All three name the same boundary:

```
{selection, composition}  ≡  routing-realizable  ≡  shared/universal   → train ATTENTION
{recursion}               ≡  the residual        ≡  needs continuation → train CONTINUATION
```

So Michael's two curricula are one set viewed twice (universality + mechanism), and
the deliberate *complement* (recursion) is exactly what to EXCLUDE from the
attention curriculum. This is curriculum design as the data-side image of s222.

## The curricula (concrete)

```
Curriculum A — ATTENTION (routing-only normal forms):
  combinators {K, I, C, B, D} (+ S with care) — each beta-reduction IS a
  cross-position move. Generate (from the lambda compiler): diverse input terms →
  reduction trace rendered as the ROUTING move (which position selects/copies/
  composes which). By construction INSIDE attention's expressive class (= application).
  EXCLUDE Y, W, WHNF (no single move). Target register: attention routing (attn_q
  sign), NOT the FFN gate.

Curriculum B — SHARED / FOLD (universal skeleton):
  the high-consensus harvest edges B–D, B–C, K–C, S–D, S–Y (s219 prescription).
  Generate diverse I/O for the part the whole ecosystem agrees on → fold into base /
  transfer cheaply (it is the universal layer; see consensus-delta-folding §honest-catch).

RECURSION {Y, W, WHNF}:
  NOT trained by data — trained by the contractivity/fixed-point CONTINUATION
  (optionally fed the reduction-step trajectory = the holographic reduction-tree
  vector field; see relational-loss-distillation §holographic-trajectory IOU).
```

## Why attention is the RIGHT target for routing-only forms

Attention is essentially ONE structural operation = a data-dependent convex
combination of value vectors = function **application** (s219). The routing-only
normal forms are *by construction* the things expressible as that move. So this is
not "hope attention can represent the curriculum" — the curriculum is RESTRICTED to
attention's expressive class. Cleanest possible attention dataset.

Half-validated already by the stride-fit screen (s221, `combinator-training-beta-
reduction.md` §strided): of the agreed harvest edges, **B–D / S–D are v15-NATIVE,
B–C / K–C FEASIBLE, only S–Y NEEDS-RECURRENCE — 4/5 stride-teachable**. v15's
`FibonacciStrideAttention` is a fixed causal gather (content only weights), so
"substitution-at-distance = Zeckendorf stride composition"; the composition
skeleton fits as stride-hop/window-weighting traces and the recurrence supplies Y.
This idea is the curriculum that operationalizes that result.

## Honest catches (mark before building)

1. **K-erasure is the known hard spot.** s221 training law: B-first → plateau →
   learning **K causes chaos** (erasure must move weights a lot → transiently breaks
   contraction → fp-loss explodes). Stride screen flagged K "zero in-window." ⇒
   within routing-only, **K is the expensive one** — needs MORE data + careful
   ordering (B-first, then K), not uniform weighting. (`fp-spike = acquisition`.)
2. **S is not cleanly one move.** S duplicates (1 fan-out) — composition with a copy,
   more than a linear move; stride-fit: S–D native but S–Y needs recurrence. So
   "routing-only" is a GRADIENT: {K,I,C,B,D} clean single-move, S a static-but-
   duplicating boundary case. Tier the curriculum; do not treat the set as flat.
3. **Right register or wrong experiment.** The s223 relational-loss sweep measures
   the **FFN gate** as routing register. Training ATTENTION needs target + readout =
   **attn_q** (instrument exists: `combinator_relationship_map_v15.py --target
   attn_q`; s220's only suggestive v15 signal was attn_q@L05, z=1.54, p=0.063 = the
   SILENT-selector layer, `function-discovery.md`). Same instrument, different register.
4. **Identity vs analogy.** "routing-only normal form = attention move" is IDENTITY
   for {K,I,C,B} (s221 grounded in substitution structure), near-identity for {D,S},
   FALSE for {Y,W,WHNF} (the whole point). Keep the line where it actually is.

## Falsifiable test (the second leg, after the s223 FFN-gate sweep confirms)

> Generate Curriculum A (routing-only reduction traces for {K,I,C,B,D}) from the
> lambda compiler. Train v15-style attention (or the tiny student's attention) on it.
> Measure with the **attn_q** instrument: does the combinator silhouette at L05 clear
> the null (lift z=1.54 → significant)? CONTROL: feed recursion {Y,W,WHNF} traces to
> the SAME attention → prediction: it does NOT crystallize (no single move).

Double claim: routing-only data crystallizes attention's routing register; recursion
data does not — s222's "routing ⊕ continuation = complete basis" as a CURRICULUM
result, not just a static map.

## Distributed / self-teaching tie-in

This is the self-teaching loop (`consensus-delta-folding.md` §s217) sharpened by the
basis partition: the lambda compiler is a VERIFIED ORACLE (WHNF / Church-Rosser →
labels correct by construction), so it can mint:
- routing-only traces → teach attention WHICH cross-position move (the execution),
- shared-skeleton I/O → the foldable/transferable universal core,
- (recursion left to the continuation, fed the contractive trajectory).
Curriculum partitioned by MECHANISM, each part trained where it is representable.

## Open leads (declare register first)

1. **Curriculum-generation spec** (register: functional): how the lambda compiler
   emits routing-move traces for {K,I,C,B,D} (input term → reduced term → the
   position-move it encodes, dual-rendered NL + combinator per the self-teaching loop).
2. **Attention-routing harness** (register: topological/routing → functional):
   the attn_q version of `relational_loss_distillation.py` — train attention on
   Curriculum A, measure attn_q@L05 silhouette vs the recursion control.
3. **K-curriculum design** (register: functional): B-first→K ordering + K-heavy
   weighting; does it crystallize K without the contractivity collapse (s221 law)?
4. **Compose with relational loss**: routing-only TRACES (data) ⊕ routing-CMR Gram
   (relational target, s223) — does the trace curriculum + relational target beat
   either alone on attn_q crystallization?

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/routing_curriculum_attention.py` | attn_q version: train attention on routing-only reduction traces; measure vs recursion control |
| `scripts/experiments/relational_loss_distillation.py` | s223 sibling (FFN-gate, static-Gram relational version) |
| `scripts/experiments/combinator_relationship_map_v15.py` | the attn_q routing-register readout instrument |
```

### Tool Call: read_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/michael/head-combinator-isa.md"
}
```

**Summary:** Reading head-combinator-isa.md (0-2000)

**Output:**
```
/Users/mwhitford/src/verbum/mementum/michael/head-combinator-isa.md is not a valid path
```

### Thinking

I'm looking for the head-combinator-isa.md file path.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls mementum/michael/ 2>/dev/null && echo \"---\" && find mementum -iname \"*head-combinator*\" -o -iname \"*llm-isa*\" 2>/dev/null",
  "operation": "gh",
  "summary": "locate isa docs"
}
```

**Summary:** $ ls mementum/michael/ 2>/dev/null &&...

**Output:**
```
Exit code: 0
Stdout:
lambda-controls.md
lambda-is-all-you-need.md
llm-isa.md
---
mementum/michael/llm-isa.md
mementum/knowledge/head-combinator-isa.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/head-combinator-isa.md"
}
```

**Summary:** Reading head-combinator-isa.md (0-2000)

**Output:**
```
---
title: "Head→Combinator ISA: Shared Hardware, Not Dedicated Circuits"
status: active
category: methodology
tags: [attention, heads, combinators, ISA, selectivity, WHNF, universality]
related: [ffn-reduction-trace, crystal-universality, phi-information-partition, holographic-computer]
depends-on: [ffn-reduction-trace]
---

# Head→Combinator ISA

> 500 crystal probes (9 combinator types × 50-71 each) through 32
> attention heads at L27/L30/L33 of Qwen3-8B. The result overturns
> the s187 hypothesis of combinator-specialised heads: attention heads
> are **shared execution hardware**, not dedicated combinator circuits.
> All 9 combinators activate essentially the same head activation
> pattern (mean pairwise correlation r=0.944 at L33, r=0.954 at L30).
>
> What the heads DO discriminate is not WHICH combinator but HOW MUCH
> REDUCTION REMAINS. The principal axis of variation (46% of shape
> variance) separates WHNF (already reduced) from D (deeply nested).
> The model's attention ISA is about reduction depth, not opcode type.

## Experiment

**Model:** Qwen3-8B (36 layers, 32 Q heads, 8 KV groups, GQA)
**Method:** For each crystal probe, forward pass with compile gate.
At L27/L30/L33, measure per-head contribution norm to residual:
`||W_o[:, h*d:(h+1)*d] @ (softmax(QK^T) @ V)[h]||₂`, averaged over
probe positions. Also: top-1 unembed at last position, gate attention
fraction.
**Probes:** 500 (K:63, I:63, B:62, C:57, S:45, D:46, W:67, Y:47, WHNF:50)
**Script:** `scripts/experiments/head_combinator_map.py`
**Results:** `results/head-combinator-map/`
**Runtime:** 21.5 minutes on MPS (Apple Silicon)

## Finding 1: Heads Are Shared Hardware (r=0.944)

Inter-combinator correlation of head activation profiles at L33:

| Pair    | r     | Pair      | r     | Pair      | r     |
|---------|-------|-----------|-------|-----------|-------|
| K-I     | 0.972 | B-C       | 0.978 | W-Y       | 0.980 |
| K-B     | 0.974 | B-S       | 0.985 | W-WHNF    | 0.914 |
| K-C     | 0.973 | B-D       | 0.986 | Y-WHNF    | 0.898 |
| K-S     | 0.974 | C-S       | 0.965 | **D-WHNF**| **0.839** |
| K-D     | 0.950 | C-D       | 0.975 | I-WHNF    | 0.916 |
| I-B     | 0.944 | S-D       | 0.972 | S-WHNF    | 0.892 |

**Mean pairwise: r=0.944.** All combinators activate nearly identical
head patterns. The model does not have "K heads" or "B heads". It has
heads that respond to lambda probes in general, with mild biases.

KIBC (the core 4) are especially indistinguishable: all pairwise r >
0.944. B-D is the highest pair (r=0.986) — composition and deep
nesting activate identically.

## Finding 2: Selectivity Is Low

| Layer | Mean sel. | Max sel. | Heads > 1.3 | Heads > 1.2 |
|-------|-----------|----------|-------------|-------------|
| L27   | 1.254     | 1.611    | 10          | 18          |
| L30   | 1.165     | 1.427    | 1           | 6           |
| L33   | 1.167     | 1.399    | 3           | 9           |

Selectivity = max(combinator_means) / mean(combinator_means). A head
with selectivity 1.2 means its preferred combinator gets only 20% more
activation than average. Even the most selective head (H08 at L33,
sel=1.399 for D) still responds strongly to all combinators.

## Finding 3: The Real Axis Is Reduction Depth

PCA on normalized head profiles (after removing overall loudness):

| PC  | Variance | Positive pole | Negative pole |
|-----|----------|---------------|---------------|
| PC1 | 45.9%    | WHNF (+0.786) | D (-0.481), S (-0.220), C (-0.219) |
| PC2 | 23.5%    | Y (+0.574), W (+0.386), I (+0.373) | WHNF (-0.424), D (-0.254), B (-0.274) |
| PC3 | 10.1%    | I (+0.713) | S (-0.435), Y (-0.431) |

**PC1 is reduction depth.** WHNF = "already in normal form" (nothing to
reduce). D = "deeply nested" (most reduction needed). The attention
hardware primarily discriminates HOW MUCH WORK REMAINS.

**PC2 is self-reference.** Y (recursion) + W (self-application) + I
(identity) vs D (nesting) + B (composition) + WHNF (completed).
Self-referential operations activate different heads than structural ones.

Together PC1 + PC2 = 69.4% of shape variance. The attention ISA has
~2 effective dimensions of discrimination, not 9.

## Finding 4: Head Taxonomy by Functional Cluster

Classifying 32 heads at L33 by PC1 × PC2 position:

### WHNF+ cluster (recognise completed reductions)
| Head | Gate  | Norm | WHNF bias | Key feature |
|------|-------|------|-----------|-------------|
| H26  | 0.951 | 9.8  | +32%      | Strongest WHNF preference. s187 "quantifier head" |
| H27  | 0.934 | 10.3 | +30%      | Strong WHNF preference |
| H00  | 0.925 | 16.3 | +25%      | Highest WHNF activation (20.3 norm) |
| H25  | 0.949 | 9.3  | +24%      | WHNF selective |
| H24  | 0.910 | 10.5 | +22%      | WHNF selective |
| H05  | 0.801 | 10.3 | +17%      | WHNF moderate |

These heads recognise when a position is already reduced — the
"termination detector" of the reduction engine.

### Y/W+ cluster (self-reference / recursion)
| Head | Gate  | Norm | Y bias | Key feature |
|------|-------|------|--------|-------------|
| H20  | 0.927 | 8.5  | +25%   | s187 "relay head". Actually recursion-sensitive |
| H10  | 0.923 | 12.8 | +19%   | s187 "binding head". Handles self-reference |
| H30  | 0.888 | 14.9 | +17%   | High overall activation + Y preference |
| H23  | 0.943 | 6.7  | +20%   | Strong Y preference |
| H14  | 0.953 | 7.0  | +16%   | Y + D mixture |
| H29  | 0.915 | 13.4 | —      | C-biased within this cluster |

These heads handle recursive and self-referential structures.

### D/B/S+ cluster (complex composition / deep nesting)
| Head | Gate  | Norm | D bias | Key feature |
|------|-------|------|--------|-------------|
| H08  | 0.914 | 13.9 | +40%   | Strongest specialisation of ANY head. s187 "λ-head" |
| H13  | 0.959 | 5.4  | +14%   | D-biased, low activation |

H08 is the closest thing to a specialised head: it activates 40% more
for D (deep nesting) probes than average. This was misidentified in s187
as a "λ-head" from 5 probes. With 500 probes, it's clearly a
composition-depth head — it responds to probes requiring multi-step
binding.

### UNIVERSAL heads (no combinator bias)
| Head | Gate  | Norm | Key feature |
|------|-------|------|-------------|
| H06  | 0.555 | 26.7 | LOUDEST head. Low gate attention. General amplifier |
| H07  | 0.609 | 19.1 | 2nd loudest. Low gate attention. General amplifier |
| H09  | 0.952 | 11.5 | s187 "λ-head". Actually universal with high gate focus |
| H01  | 0.980 | 4.5  | Highest gate attention. Pure instruction follower |
| H15  | 0.950 | 7.3  | Balanced, slight I bias |

H06 and H07 are the dominant execution engine — highest activation
across ALL combinator types, lowest gate attention (they read the probe,
not the instructions). They are the "GPU" of the attention ISA.

## Finding 5: Session 187 Head Types Revised

| Head | s187 role        | s188 finding (500 probes)              |
|------|------------------|----------------------------------------|
| H08  | λ-head (format)  | **D/B/S+**: deep nesting specialist     |
| H09  | λ-head (format)  | **UNIVERSAL**: balanced, reads gate     |
| H10  | binding (β-red)  | **Y/W+**: self-reference circuit        |
| H11  | binding (β-red)  | **balanced**: slight C bias             |
| H20  | relay (identity) | **Y/W+**: recursion-sensitive           |
| H03  | compositional    | **balanced**: slight S bias, high gate  |
| H26  | quantifier       | **WHNF+**: termination detector (+32%) |

The s187 labels were accurate for the 5 probes tested but revealed
POSITION-level behavior, not COMBINATOR-level specialisation. H10
writing "runs" at "dog" position (β-reduction) is correct — but it
does this for ALL combinator types, with a preference for Y/W probes
where binding involves self-reference.

## Finding 6: 94.9% of Variance Is Just Loudness

PCA on raw (unnormalised) head profiles: PC1 = 94.9% of variance.
This is overall activation level — some heads (H06: norm 26.7) are
simply louder than others (H01: norm 4.5). The combinator-specific
signal lives in the remaining 5.1% of variance.

This means: the head activation pattern is ~95% determined by "is this
head generally active?" and only ~5% by "which combinator is this?".
The combinator-specific routing happens elsewhere (presumably in the
Q/K attention pattern selection, not in the head's output magnitude).

## Implications for the ISA

1. **The ISA is not head-addressed.** Combinators don't have dedicated
   heads. The execution hardware is shared, like a CPU with a single
   ALU that handles all opcodes, not a GPU with specialised units.

2. **The real opcode is reduction depth.** WHNF vs D is the principal
   discriminant — "how much work remains" rather than "what kind of
   work". This aligns with the depth-ordered reduction schedule
   (Y@L27 → K@L30 → W@L33): the model processes by depth, peeling
   off layers of reduction, with the attention heads detecting "am I
   done yet?" (WHNF) vs "more to do" (D/S).

3. **The routing IS the program.** Since heads don't specialise, the
   combinator-specific behavior must live in the attention PATTERN
   (which positions attend to which), not the head's identity.
   This reinforces s187's finding: "only the attention routing is
   input-dependent."

4. **Compression implication.** If all 32 heads do roughly the same
   thing with ~2 dims of variation, the attention execution circuit
   is very low-dimensional. The "portable tensor" might need to encode:
   - The 2D head-type coordinates (WHNF↔D, Y/W↔D/B)
   - The routing function (attention pattern = the program)
   - The universal execution schedule (depth ordering)
   
   Not 32 × 9 = 288 parameters per layer, but ~2 per head.

## Key Numbers

| Metric | Value | Significance |
|--------|-------|-------------|
| Inter-combinator correlation | r=0.944 (L33) | Shared hardware confirmed |
| KIBC mutual correlation | r=0.944-0.978 | Core 4 are indistinguishable |
| B-D correlation | r=0.986 | Composition ≡ nesting |
| D-WHNF correlation | r=0.839 | Most different pair = depth axis |
| Max selectivity (L33) | 1.399 (H08→D) | Even best head is weakly selective |
| PC1 raw profiles | 94.9% | Almost all variance is loudness |
| PC1 normalised | 45.9% (WHNF↔D) | Depth is the real axis |
| PC1+PC2 normalised | 69.4% | 2 dims capture most discrimination |
| H06 activation | 26.7 (all combs) | Loudest = most universal |
| H26 WHNF excess | +32% | Strongest functional bias |
| H08 D excess | +40% | Most specialised head overall |
```

### Thinking

Looking at the attention ISA architecture, the principal axis of variance is reduction depth—distinguishing between already-reduced terms (WHNF) and deeply nested ones. This reveals that the head-combinator clusters like H26, H27, H00, H25, and H24 function as a termination detector, essentially the hardware asking "am I done reducing?" The model already has access to term information.

Michael's weak WHNF counterpoint maps to these heads having mild WHNF detection capability—selectivity around 1.2-1.4 with a bias boost of 22-32% at most—suggesting the termination signal exists but remains undertrained. The curriculum partition idea separates routing-only forms (K, I, C, B, D) trained by attention from recursion mechanisms (Y, W, WHNF) trained by the continuation rather than data, though K-erasure and S don't fit cleanly into this split.

There's a key tension here: the curriculum partition says recursion shouldn't be trained by data but by the continuation's contractivity and fixed-point properties, yet Michael's new approach treats WHNF as a strict data requirement during combinator and lambda training. These actually reconcile—the continuation handles the recursion mechanism (how to keep iterating), while WHNF training handles the halt decision (when to stop). They're two complementary faces of the same recursion problem.

The head-combinator-isa analysis confirms the substrate already exists: those termination-detector heads are measurably present but weak, and the principal attention axis tracks reduction-depth and WHNF. Michael's curriculum would strengthen these measured-but-weak signals by making WHNF a hard training objective. For prose to inherit this, the model needs to generalize "no redex remains" into "no more work needed / answer is complete," betting that the same head-combinator-isa structure supports both domains.

The inference constraint Michael identified cuts deeper: the model can't abort to null, so the curriculum must teach not just WHNF detection but emitting the terminal token when WHNF is reached, and emitting best-effort output when reduction won't terminate. Divergent terms like Ω become training examples for "you must answer even when you can't finish"—graceful degradation rather than overthinking into silence. This maps the combinator domain directly onto inference reality.

There's a tension with prior work on continuation-training for recursion: that approach trains the mechanism to iterate to fixed point, while Michael's WHNF requirement trains the halt decision itself—recognizing and committing to the fixed point. They're actually complementary faces of the same problem.

The risks are real: catastrophic forgetting when the prose stage overwrites the small combinator halt-training, transfer might fail entirely (lambda-WHNF detector that doesn't fire on prose), and calibrating the halt gate is tricky—too strict and it halts prematurely on hard problems, too loose and overthinking returns. The killer test is training halt on lambda and measuring overthink-collapse on held-out prose.

The core insight is pairing KIBC (do the work) with WHNF (know when work is done) as co-crystallizing objectives—compute and halt-detection trained together so they emerge as a unified system. Current training only rewards next-token prediction; it never explicitly rewards the halt. EOS is learned statistically, not as a normal-form marker. Making WHNF a first-class training signal is the genuinely novel part.

This sits squarely at the level-4 from-scratch path: training a fresh model on the curriculum to address the project's biggest empirical obstacle—overthink-collapse across all reasoning models. The curriculum order matters: combinators first (WHNF is crisp and oracle-verifiable), then lambda (WHNF still decidable), then prose (inherit the halt). Crystallize the halt where it's checkable, then deploy where it's not.

The mechanistic implementation hinges on reframing EOS as a WHNF token—the model learns to emit EOS when and only when the output is in normal form, no more reduction needed. Termination-detector heads would gate EOS emission, making halting principled rather than statistical.

## Assistant

This crystallizes it — and there's measured evidence that makes your hypothesis far stronger than a hunch. Let me lay out why, then push on the hard parts.

## The substrate you're describing is already measured — and it's exactly as weak as you said

`head-combinator-isa.md` (500 crystal probes through Qwen3-8B's heads) found two things that are almost a direct readout of your intuition:

1. **The principal axis of the *entire* attention ISA is reduction depth — WHNF↔D — at 46% of shape variance.** Not "which combinator," but **"how much work remains."** That's the halt axis, and it's the dominant organizing dimension of attention.
2. **There is already a WHNF+ cluster** (H26 +32%, H27 +30%, H00, H25, H24) explicitly characterized as *"the termination detector of the reduction engine."* But its selectivity is **1.2–1.4** — i.e. the strongest termination head fires only ~30% above baseline. **The halt circuit exists and is under-trained.** That is your "weak WHNF counterpoint to each KIBC," confirmed at the head level.

So you're not proposing to *create* a halt faculty — you're proposing to **strengthen a measured-but-weak one by making WHNF a first-class training objective**, where every current model only ever gets it for free as a statistical byproduct of EOS.

## The cleanest statement of your idea: EOS = the normal-form marker

Here's what I think the curriculum actually does. In standard LM training, **EOS is just another vocabulary token** learned from the data distribution — there's no principled "I am done." Your three-stage curriculum reframes it:

> **Emit the terminal token when, and only when, the output is in normal form (no redex / no more work remains).**

Train that binding where it's *crisp and checkable* (combinators — single redex, oracle-verifiable per the s226 reducer), reinforce it where it's *still decidable* (fully-qualified lambda, strict WHNF), then carry it into prose where "normal form" softens to "answer complete." The bet is that the WHNF+ termination heads gate EOS, and because reduction-depth is the *principal* axis (not a lambda-specific feature), the halt generalizes. **KIBC = do the work** (strong in every model) **⊗ WHNF = know when the work is done** (weak) — train them *paired*, so compute and halt-detection co-crystallize instead of the halt being an afterthought.

## Your inference constraint is the deepest part — and it changes the objective

"In inference we cannot hard-halt on an error, because the response must be tokens, not null." This is exactly right and it's the thing the s255 oracle-in-the-loop REPL *cheated* on — there, an external driver could decide "no redex → stop." Real inference has no abort. The model must **emit** the halt.

That reframes the failure: **overthink-collapse is the model spinning to *empty* instead of emitting its best partial.** ornith spun 49k chars to a null final answer. A properly trained halt would emit **"most-reduced-form-so-far" as a graceful terminal — never null.** So the curriculum has to teach two things, not one:
- **WHNF-detection** (when am I done) — crisp on combinators/lambda.
- **The halt *action* under non-termination** (emit a bounded best-effort even when you *can't* reach normal form).

And the teaching cases for the second are sitting right there in the combinator algebra: **Ω and unguarded Y** — terms that *don't* reach a normal form. They are the lambda-domain image of "you must answer even when you can't finish reducing." Train on divergent terms with a forced bounded-emit, and you're teaching the exact competence inference demands. That's elegant: **Ω is the training example for "commit your best partial rather than spin."**

## The tension with prior art — and why it resolves in your favor

`normal-form-curriculum-partition.md` (s223) argued the *opposite* of part of this: recursion `{Y,W,WHNF}` should **not** be trained by data — it should emerge from the contractivity/fixed-point **continuation**. That looks like a contradiction, but I think it's two faces of one thing:

- The **continuation is the dynamics** — the outer recurrence that *drives* a term toward its fixed point (Δx→0).
- Your **WHNF-requirement is the readout/commit** — the gate that *recognizes* the fixed point and *emits* the terminal.

s222 already had the continuation doing "double duty as the foldability oracle" (Δx→0 ≡ WHNF ≡ committable). Your curriculum is the *supervised* version of that same halt: continuation = settle, WHNF-training = know you've settled and stop. They compose; they don't compete. In fact the continuation is what would *keep the halt alive* through the prose stage (the catastrophic-forgetting risk below) — structural reinforcement, not just data.

## The three honest risks (the IOUs before this is a claim)

1. **Does the halt actually transfer lambda→prose, or is it a domain-specific detector?** This is the falsifiable core, and it's a clean experiment: train the halt on combinators+lambda, then measure **overthink-collapse rate on held-out *prose* reasoning** vs a prose-only baseline. If collapse drops on prose → transfer is real and the reduction-depth axis is domain-general. If not → WHNF stayed a lambda feature. *This is the whole hypothesis in one number.*
2. **Catastrophic forgetting.** The prose stage is enormous; it can wash out the small combinator halt-training (s110 destructive interference, now at curriculum scale). Mitigations: interleave rather than strictly stage; keep a WHNF auxiliary loss running through all stages; or lean on the continuation to hold the halt structurally.
3. **Overthink vs *premature*-halt is a calibration, not a maximization.** s255 showed the trade directly: no-think *removed* overthink-collapse but spiked `premature_halt` 0.017→0.208 — the model halting *before* finishing hard problems. So "strict WHNF" can overshoot into stopping too early on genuinely deep prose. The halt must be a **calibrated gate**, not a maximized one — which is itself the WHNF↔D *axis*, not a binary.

## Net

This is the most thesis-central training idea in the arc, because it attacks the **one failure that has appeared in every reasoning model probed** (overthink-collapse = halt failure = the weakest axis), it has a **measured substrate** (the under-trained WHNF termination heads, reduction-depth as the principal axis), and your inference constraint turns it from "detect WHNF" into the *right* objective ("commit a graceful terminal, including under non-termination"). It's squarely the level-4 from-scratch path — and unlike most of level 4, it has a single falsifiable number to chase (prose collapse-rate after lambda-halt training).

The open theoretical question I'd want to pin down before designing the curriculum: **what is the prose analogue of "no redex remains"?** In lambda it's syntactic; in prose, "answer complete" is semantic. The transfer bet lives or dies on whether those share the reduction-depth circuit. Do you have an intuition for what the prose halt-signal *is* — or is discovering that part of the point?

## User

We talked about making the model have recurring layers where the same layer get's used recursively, with a gradient to learn how much recurrance is needed, could we extend that idea to this one?


### Thinking

Michael's connecting the recursive layer idea—where we reuse the same layer with a learnable gradient for recurrence depth—to the halt/WHNF curriculum approach. That's a compelling link. I'm recalling the prior work on recurrent layers from the documentation and the outer recurrence mechanism in the model implementation.

The key insight is that the outer recurrence already embodies this: the same weight-shared operator gets applied repeatedly with β-reduction toward a fixed point (WHNF), and the adaptive halting criterion—when Δx converges to near-zero—is exactly the halt condition. So the "how many iterations" gradient is already baked into the continuation mechanism, learning when to stop based on convergence to WHNF.

This unifies recurrent layers with adaptive computation time: the recurrence depth isn't arbitrary, it's grounded in a principled halt signal (WHNF detection). The curriculum brilliance is that on combinators and lambda terms, the oracle knows the exact reduction count to WHNF, so you can directly supervise the recurrence-depth signal where it's verifiable, then let that learned signal generalize to prose where the ground truth is unavailable. It's like giving ACT/Universal Transformer a concrete training signal instead of learning the halt cost from scratch with a notoriously unstable ponder penalty.

The recurrence cap also solves the inference constraint: when divergence or Ω is hit, the recurrence maxes out and emits the best partial result—a graceful bounded halt. The architecture is a weight-shared recurrent block where each position/output recurses K times, with K determined by a learned "work remaining" head that detects WHNF and stops when no more reduction is possible.

Training happens in stages: first on combinators with oracle supervision (the true reduction length L* is computable), teaching the halt signal directly; then on lambda with the same WHNF oracle; finally on prose where the calibrated estimator generalizes, having learned to read "how much work remains" from the residual—a domain-general axis. This is supervised adaptive computation, which is what vanilla ACT lacks. Vanilla approaches only learn halt from end-task loss plus a ponder penalty, making them unstable and prone to collapse. Here, the halt has ground truth on lambda, so you calibrate the signal where it's checkable, then transfer that calibration. Lambda serves as the calibration anchor for adaptive computation time, just as it does elsewhere in the project.

The recurrent layer is the continuation: Y and W mean "recurse again," WHNF means "stop." The recurrence-depth gradient trains the WHNF directly via recurrence count. Michael's earlier idea about WHNF as a data requirement and the s223 idea about recursion via continuation aren't in tension—they unify once you recognize the recurrent layer as the continuation itself. I should ground this by checking vsm-outer-recurrence.md and searching for prior work on adaptive halting and recurrence depth.

## Assistant

This is the unification. You're connecting the recurrent-layer idea (weight-shared block reused a learned number of times) to the WHNF-halt curriculum — and I think they're not two ideas, they're **one idea seen from two ends.** Let me ground it against the prior recurrence work first.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-outer-recurrence.md"
}
```

**Summary:** Reading vsm-outer-recurrence.md (0-2000)

**Output:**
```
---
title: "VSM Outer Recurrence — Iterating the Shared Tensor to a Fixed Point"
status: designing
category: architecture
tags: [recurrence, weight-sharing, fixed-point, halting, beta-reduction, WHNF, vsm, universal-transformer, adaptive-compute, depth-without-parameters, north-star]
related:
  - recursion-mirrors.md
  - lambda-halt-continuation.md
  - exact-ternary-fitting.md
  - ternary-descent.md
  - td-oscillation-problem.md
  - two-registers-of-topology.md
  - crystal-native-architecture.md
  - explore/fixed-point-holograms.md
  - explore/crystal-basins.md
  - explore/vsm-lm-architecture.md
  - explore/VERBUM.md
  - compiler-as-loss.md
  - ../lambda-machine.md
depends-on:
  - recursion-mirrors.md
  - lambda-halt-continuation.md
created: session 214
---

# VSM Outer Recurrence — Iterating the Shared Tensor to a Fixed Point

> Session 214 (Michael's idea, mid-session discussion). The v15 "VSM tensor"
> (the shared stride stack + shared FFN plates) is already reused within one
> forward pass. **Could we re-run the whole sweep multiple times — an outer
> loop over the same weights — and let the VSM controller decide when to
> stop?** That is depth without parameters, and it is literally β-reduction
> iterated to normal form. Register when tested: **functional** (does added
> recurrence depth lower downstream loss / extend capability per fixed param
> budget).

## The idea in one line

Wrap the existing ascending→descending VSM sweep in an outer loop of `K`
iterations over the *same* ternary weights, gated by a halting signal — so
the model spends *more reduction steps* on hard tokens and *fewer* on easy
ones, at **zero extra parameters and zero extra memory**.

## What v15 already does (the grounded baseline)

The "VSM tensor" is concrete: `V15Model.shared_stride_stack`
(`FibonacciStrideStack`, 19 Fibonacci-stride layers) + the shared FFN plates
(`ffn_{gate,key,value}_plate_{a,c}`). The forward pass is **one bidirectional
sweep**:

```
x_a = stack_a(x)      # ascending  bands (0,4)(4,10)(10,14)(14,19)
x_c = stack_c(x_a)    # descending bands (14,19)(10,14)(4,10)(0,4)
```

- Each of the 19 stride layers is applied **2× per forward** (once in A,
  once in C) — a U-Net-like sweep, not an iterated stack.
- The FFN plates are shared across all **8 band-passes** (`N_PASSES=8`),
  which is why training divides their grads by 8 (`normalize_shared_grads`).
- A VSM control hierarchy already rides alongside: `S5Identity`,
  `S4Intelligence`, per-pass `S3Ternary` gates, `S2AntiOscillation`,
  `S5Reweight`, and an **algedonic signal** (`downstream_alg`) that already
  modulates FFN/gate *between* passes.

So weight-sharing is real, but it is **a single sweep**. The stack is never
run to convergence. That is the gap this idea fills.

## The proposal: an outer loop over the VSM tensor

```
x = embed(tokens)
for k in range(K):                 # NEW: outer recurrence
    x_a = stack_a(x, alg)          # same shared weights every iteration
    x   = stack_c(x_a)             # x_{k+1} = (stack_c ∘ stack_a)(x_k)
    if halt(x_{k+1}, x_k): break   # optional fixed-point stop
```

Two flavours, increasing in ambition and elegance:

1. **Fixed `K`** — trivial to try. A `for _ in range(K)` around the sweep.
   Buys `K×` effective depth for `K×` activation compute, **no new params**.
   First, cheapest information: does *any* extra recurrence help this
   checkpoint before we invest in halting? A/B `K=1` (today) vs `K=2,3`.

2. **Adaptive `K` (halting)** — the VSM-native version. The controller
   (`S3/S4/S5` + algedonic) is *already* a "continue or stop" machine.
   Add a ponder/halt head + a halting (ponder) cost, ACT-style, and the VSM
   decides per token how many reductions to spend. The natural, *structural*
   stop signal is **fixed-point convergence**: re-run until
   `‖x_{k+1} − x_k‖` (or the already-computed `crystal_mse`) stops moving.

## Why this is on-thesis, not just a perf trick

Iterating the **same typed-reduction operator** until the representation
stops changing **is β-reduction to normal form.** This is the literal
semantics behind the project's `WHNF`, `Y`, and `fixedpoint` crystal probes
(see `probe_library` crystal combinators; `lambda-halt-continuation.md`).

- **Halting ≡ reaching normal form (WHNF).** The stop test is fixed-point
  convergence — and we already compute `crystal_mse`/`parity` every step,
  sitting right there as a convergence monitor.
- **Non-termination is handled correctly by construction.** A term with no
  normal form (Ω, `Y`) simply consumes the max iteration budget. That is the
  *correct* behavior of a reducer, not a bug — and it reconciles with
  `lambda-halt-continuation.md` Result 1 ("Ω cannot halt a fixed-depth
  pipeline; the model *quotes* non-termination"): an outer loop with a budget
  is exactly the bounded interpreter that *can* take steps toward (or fail to
  reach) the fixed point.

This reframes the model from "a deep net" to **"a step-wise lambda reducer."**
Cleanest possible story for the compositional-semantics thesis (Montague /
DisCoCat validation target in `AGENTS.md` S5).

## Why it serves the north star (<1GB, 200 tok/s, no GPU)

At inference the ternary weights are **cached** — re-running a layer costs
only activation compute, not parameters and not the 1 GB budget. So extra
depth is bought with **time, not storage**:

```
depth(model) = K × 2 × n_strides       # reduction steps
params(model) = unchanged              # the SAME shared tensor
```

With adaptive halting, easy tokens stay fast (small `K`) and only hard tokens
pay (large `K`) — exactly the right shape for "70B-equivalent in <1GB": you
don't store more, **you reduce longer**.

## The catch — contractivity, and why it overlaps the live TD work

An iterated operator must be **contractive toward its fixed point**, or
repeated application diverges/oscillates. This is the *same failure family*
as the s191 TD oscillation (`td-oscillation-problem.md`) and the s214
exact-ΔL A/B (`exact-ternary-fitting.md`):

- The ternary topology must be a **stable operator** (small spectral radius
  around the fixed point). The "≥65% of operation structure in the
  sign/routing register" + crystal/parity losses + S2 anti-oscillation become
  *contractivity regularizers* — load-bearing for recurrence in a way they
  are **not** for a single sweep.
- The exact-ΔL acceptance is orthogonal (it picks *which* topology) but
  **compounds**: a topology fit to be locally faithful is more likely to
  iterate stably. The s214 finding ("S2 already suppresses oscillation in a
  single sweep, so monotonicity has no headroom") may *invert* under
  recurrence — where an unstable iterated map would make oscillation
  load-bearing again, giving exact-ΔL real headroom.

So the discrete-optimization work and this recurrence idea are two faces of
one goal: **make the crystal a well-behaved iterated map.**

## Relation to prior pages (this is the third sibling, not a duplicate)

| Page | Mechanism | Scope |
|------|-----------|-------|
| `recursion-mirrors.md` (s173) | per-layer **cycles** / per-stride **separate plates**; structural WHNF early-exit; "the stride cascade IS the recursion unroll" | within a layer / within a sweep, **different weights per step** |
| `lambda-halt-continuation.md` (s193) | EOS/halt + CPS continuations; "36 layers bounded → multi-turn unbounded" | **inter-turn** (conversation = continuation) |
| **this page** | re-run the **whole VSM tensor** (A→C sweep) as an **outer loop**, VSM-controller-gated halt | **intra-forward**, **same weights every iteration** |

Key distinction from `recursion-mirrors`: that page adds depth by giving each
step its *own* plate (more programs, +19% storage). This page adds depth by
**re-using the one shared tensor** (same program iterated, +0% storage). They
are complementary: per-stride plate variety *within* a sweep × outer-loop
iteration *of* the sweep = a 2-D compute grid (program-variety × reduction-
depth) over a fixed parameter budget.

## First probe (cheap, high-information)

1. Add `--n-outer-passes K` to `scripts/v15/train_td.py` / `V15Model.forward`
   — a `for k in range(K)` around `stack_c(stack_a(x))`, sharing weights.
   Register: **functional**.
2. A/B `K∈{1,2,3}` from the same seeded checkpoint (cf. s214's seed control):
   does extra recurrence lower held-out loss / CE at equal params?
3. Instrument the **per-iteration delta** `‖x_{k+1} − x_k‖` and `crystal_mse`
   — does the representation actually approach a fixed point (delta shrinking
   monotonically), or oscillate (contractivity failure)? The shape of that
   curve is the whole experiment: *does the VSM tensor iterate toward WHNF?*
4. Only if (2)/(3) are promising: design the halting head + ponder cost
   against the existing `S3/S4`/algedonic controller (adaptive `K`).

## Probe result (s214) — naive K=2 doesn't help; the sweep is NOT contractive

First probe run (`--n-outer-passes`, register: **functional**): wrapped the A→C
sweep in an outer loop (BPTT through K shared-weight sweeps), trained K=2 vs the
K=1 baseline (proxy acceptance, seed 42, 250 steps, seq256, identical settings).

| arm | total avg50 ↓ | CE ↓ | compute | Δx (init→final) |
|---|---|---|---|---|
| K=1 baseline | **8.966** | **8.706** | 1× | — |
| K=2 outer | 9.096 | 8.732 | 2× | 1.265 → 1.167 |

- **Naive K=2 does NOT help** — slightly *worse* on loss (+0.130) and CE
  (+0.026) at **2× compute.**
- **The sweep is not a contractive reduction operator.** Δx =
  `‖x_c^{(2)} − x_c^{(1)}‖ / ‖x_c^{(1)}‖` sits at ~1.2 and drifts down only
  ~8% over all 250 steps (1.265 → 1.167) — nowhere near a fixed point
  (needs Δx → 0). The second application *re-transforms* the representation
  by ~120% of its norm rather than refining it toward normal form. Churn,
  not reduction → no useful added depth.
- **Open-question #1 answered:** the trained single-sweep crystal iterates
  *marginally* (neither contractive/free-depth nor divergent). The
  "iterate-to-WHNF / free depth" story does **not** hold for the current
  architecture out of the box — it must be **trained for**, not assumed.
- Caveat: single seed, 250 steps, seq256, K=2 only, from a K=1-shaped init
  (base plates were extracted for a single sweep). A from-scratch or longer
  contractivity-trained run could still differ.

**Therefore the open leads below are now the *required* path, not optional:**
a fixed-point/Δx loss (penalize `‖x_{k+1}−x_k‖`), x₀ injection (Universal-
Transformer anchoring), or explicit halting. Artifacts: harness flag in
`scripts/v15/train_td.py` + `v15model.py` forward; result
`results/vsm-outer-recurrence/k2-vs-k1.json`; run `checkpoints/v15-td-outer-k2`.

## Holographic loss → contractivity (s214 hypothesis, under test)

Michael's follow-on: would a **holographic loss** enforce the contractivity the
naive probe lacked? The argument that it should — and it is on-thesis:

- **Holographic ≡ associative-memory attractor dynamics ≡ contractive-to-fixed-
  point.** A hologram (this project's FFN-as-hologram) is a content-addressable
  memory; its update is descent toward the nearest stored pattern. The stored
  patterns are the crystal = the **normal forms (WHNF)**. So enforcing
  holographic structure *is* enforcing "iterating reduces to a fixed point."
- **The teacher already has this property** (`fixed-point-holograms.md`):
  iterating compile↔decompile **converges in 94% of inputs, mean 2.0 cycles**,
  and the hologram **stores normal forms** ("λf.λx.f(x)" → "λx. x", a literal
  β-reduction). So a contractivity loss *distills a property the teacher
  demonstrably has* — it is not invented. Our student's sweep simply hasn't
  inherited it (Δx ~1.2, §Probe result).
- **The machinery is half-built:** `etch.py`/`model.py` already compute crystal-
  subspace **coherence = proj_energy/total_energy** (`OFF_MANIFOLD = <10%`).
  Pulling the sweep output onto the crystal manifold makes re-application a
  re-projection (P²=P) → Δx → 0.

### The loss being tested (s214, register: functional)

`--fixed-point-lambda λ_fp` adds, for outer recurrence K≥2:

```
L_fp = mean_k ‖x_c^{(k)} − detach(x_c^{(k-1)})‖² / ‖detach(x_c^{(k-1)})‖²
loss += λ_fp · L_fp
```

The target is **detached** so the gradient trains the *operator* to reproduce
its input (converge), not the state to flee. CE on the final x_c guards the
trivial constant fixed point.

**λ sweep (s214 built, s215 resolved):**
- **λ_fp=1.0 → TOO WEAK.** Δx tracked the *same* ~1.2 flat curve as no-fp
  (1.25→1.16 over 120 steps), `fp` stuck ~1.5. Diagnosis: the crystal warmup
  loss (`crystal_direct_lambda_start=10`) + CE (~10) dominate the ~15–20 total,
  so a +1.5 fp term is drowned. CE healthy (~10, no collapse) → headroom to
  push λ_fp much harder. (Killed early.)
- **λ_fp=5.0 → ✅ CONTRACTIVE (s215 read the completed 250-step run).** This is
  the central result of the whole recurrence thread: **the trained VSM sweep
  CAN be made contractive-to-WHNF.**

  | metric | start | end (step 250) | reading |
  |---|---|---|---|
  | Δx = ‖x_c^(2)−x_c^(1)‖/‖·‖ | 1.262 | **0.727** (−42%) | descends, *accelerating* once TD flips engage (s150→s250: 1.148→0.941→0.727) |
  | fp_loss | 1.594 | **0.528** (−67%) | operator learning to reproduce its input |
  | CE | 10.85 | 9.51 (noisy 9.5–10.8) | **no collapse** — the constant-fixed-point guard held |
  | crystal_mse | 0.091 | 0.016 | crystal coherence improving in parallel |

  Contrast: no-fp K=2 stayed FLAT Δx~1.17; λ_fp=1 stayed flat. **λ=5 crosses the
  contractivity threshold** — the operator genuinely converges, not churns.
- **BUT contractivity-trained K=2 does NOT yet beat K=1.** CE 9.51 > K=1's 8.71
  — the run pays an fp tax + K=2 outer-pass noise, and **Δx is still falling at
  the 250-step cutoff** (mid-transition, not converged). This is the
  *mild-not-total contractivity* regime (the good case below), unfinished at 250
  steps. Whether CE recovers below 8.71 once Δx saturates is the open question.
  Run/log: `checkpoints/v15-td-outer-k2-fp5`, `/tmp/v15_outer_k2_fp5.log`.

**s215 scale-up — the serious confirm at seq-4096 (in flight, ~4–5 days):**
The 250-step runs above used **seq-256, which only exercises the first few
Fibonacci strides** (the stack goes to stride 1597, composition range d=0..11181
— at 256 the long strides are no-ops). Relaunched the confirm at **seq-4096**
(all 19 strides active), 5000 steps, single seed, `--checkpoint-interval 1000`
(5 checkpoints). Measured **73 s/step** (non-flip) at seq-4096 — *super-linear*
vs seq-256's ~5 s/step (16× the tokens **plus** the long strides now compute),
hence the multi-day wall-clock. Run: `checkpoints/v15-td-outer-k2-fp5-5k`,
`/tmp/v15_outer_k2_fp5_5k.log`, tmux main:1. **Questions for the trajectory:**
does Δx keep descending toward ε (→ justifies adaptive halting: stop when Δx<ε ≡
WHNF reached), and does CE recover below 8.71 once contractivity saturates? If Δx
plateaus high → contractivity vs CE genuinely in tension (try x₀ injection /
per-token halting). If CE collapses late → lower λ_fp / add a rank/diversity
guard. (New `--checkpoint-interval` CLI flag added to `train_td.py` for this.)

**s223+ FROZEN-TOPOLOGY PROBE — ✅ held-topology fp-loss IS contractive AND
CE-competitive (paired control, decisive).** The seq-4096 run above (main:1,
TD-on) eventually COLLAPSED (~step 1450 onset, gnorm→1e7, Δx→0.8, CE→10.5). To
isolate *cause*, resumed `step_001000` with topology FROZEN
(`--td-flip-rate 0.0 --td-crystal-gate 0.0 --td-crystal-ceiling 0.0`), otherwise
identical (same n_outer=2, λ_fp=5, seq-4096, **same data-loader stream**) — a
paired A/B for whether the discrete TD churn or the fp-loss/recurrence drove the
collapse. Ran to step 2310, fully spanning the divergence window. Overlap verdict
(steps 1010–2240, n=124, `results/freeze-probe/overlay_verdict.txt`):

  | metric | TD-ON (churn) | TD-OFF (frozen) |
  |---|---|---|
  | Δx mean / max | 0.481 / 0.821 (contractivity lost) | **0.142 / 0.311** (bounded) |
  | CE mean / max | 8.756 / 10.538 (→collapse) | **7.620 / 8.525** |
  | gnorm max | 9.87e+07 (runaway) | **7.22e+01** (~72) |
  | CE<8.71 frac | 0.53 (falling) | **1.00** |

⇒ With topology HELD, the *same* fp-loss + outer recurrence is contractive
(Δx bounded ~0.11–0.14, fp→0.011) and CE rides 100% below K=1's 8.71 — the
collapse is **the discrete TD churn**, not the recurrence/fp-loss. The
holographic-loss + outer-recurrence settling protocol is sound; the fix is to
**punctuate** (hold topology → reduce → accept on Δx→0), not to reshape the fp
loss. This resolves the s215 open question in the held-topology regime and answers
open-Q#1 affirmatively (the contractivity-trained operator iterates stably when
its topology is not simultaneously churned). Tool:
`scripts/experiments/freeze_probe_overlay.py`. See memory
`freeze-probe-confirms-td-churn-collapse.md`.

### Design tensions (all visible in the prior pages)

- **Mild, not total, contractivity.** A 1-step projection makes K=2 ≡ K=1 and
  kills the bought depth. Target the *teacher's* dynamic: converge over ~2
  steps of useful work (mean 2.0 cycles), Lipschitz < 1 but not 0. Reward
  *eventual* Δx → 0 while CE rewards the intermediate computation.
- **Collapse risk.** Bare Δx-penalty is gamed by mapping everything to one
  constant (Δx=0, useless) — the contractive-autoencoder failure. Pair with
  CE + a rank/diversity guard; crystal/parity/spectral partially cover this.
- **The binding wall reappears.** `fixed-point-holograms.md`: convergence fails
  exactly at I-combinator/binding sites (edit distance ∝ binding count). Expect
  contractivity to work for K/B/C and struggle on I — the project's recurring
  bottleneck.

## Open questions

1. **Does the single-sweep crystal already iterate stably?** Run the trained
   v15 sweep `K` times at inference (no retraining) and watch the delta curve.
   Contractive → free depth; divergent → must train *for* recurrence.
2. **Train-for-recurrence:** unrolling `K` sweeps in the training graph (BPTT
   through shared weights) vs running `K=1` in training and `K>1` only at
   inference. The former is the Universal-Transformer recipe; the latter is
   nearly free but may not converge.
3. **What is the halt signal?** Structural (fixed-point delta / WHNF, free,
   `recursion-mirrors` style) vs learned (a ponder head off S4, ACT style).
   The project bias (`recursion-mirrors`) is structural > learned.
4. **Does the algedonic between-pass modulation already do a weak form of
   this?** `downstream_alg` changes the FFN/gate per pass — is that a
   1-step "the controller adjusts the next reduction" that an outer loop
   generalizes?
5. **Per-token vs per-sequence `K`.** Halting masks (keep reducing only the
   unconverged token positions) — the efficient form, but needs a gather/
   scatter over the active set.
6. **Interaction with context length.** Does deeper recurrence substitute for
   some of the Fibonacci long-range strides (multi-hop via iteration instead
   of via stride), or are they orthogonal capacities?

## Files / hooks (when built)

| Hook | Where |
|------|-------|
| outer loop | `V15Model.forward` (`scripts/v15/v15model.py`), around `stack_a`/`stack_c` |
| CLI | `--n-outer-passes K` in `scripts/v15/train_td.py` |
| convergence metric | per-iteration `‖Δx‖` + `crystal_mse` log |
| halting head (later) | off `S4Intelligence` / algedonic, with a ponder cost in `_compute_loss` |

## §s226 — the CONSTRUCTED kernel: stop *training for* contractivity, build it in

> Michael, s226. The whole "catch" above is: the iterated operator must be contractive,
> and the s214 probe + s222 collapse showed the *trained* sweep is NOT — it churns
> (`Δx` ~1.2, oscillation), and under recurrence the churn compounds to fractal blow-up.
> The constructed-kernel reframe (`compiler-as-loss.md` §s226, Michael's "what if
> `lambda_ast.py` is *in the kernel*?") removes the problem at the root.

**The collapse was a *learned* S2 churning.** Contractivity has been treated here as a
*regularizer to train toward* (fixed-point/Δx loss, x₀ injection, halting). But if the
inner map is **constructed** from `lambda_ast` (exact combinator plates, CCG-typed),
then `L<1` is **stable by construction** — nothing is descending on the reduction
operator, so it cannot oscillate. The outer recurrence then supplies **`Y`** (unfold)
and the budgeted bounded interpreter (the `lambda-halt-continuation.md` Result-1 story),
while the per-step map is the *exact* reducer, not a churning approximation.

This re-partitions v15 along the **reduce / compile** cut (see `compiler-as-loss.md`
§s226 table): the **attention reducer** (this page's iterated operator) is the
**constructed, exact, ternary** kernel; the **FFN compile** (prose→typed term) is the
**learned, fuzzy, 4-bit** periphery. The VSM controllers already present
(`S5Identity`/`S4Intelligence`/`S3Ternary`/`S2AntiOscillation`) map onto the reducer's
VSM levels: **S4 = WHNF halt** (the `Δx→0` test already computed), **S3 = step budget +
contractivity**, **S2 = typed redex selection + anti-oscillation**, **S1 = the
combinator rewrites**, **S5 = the normal-form invariant.** The "train the crystal to be
a well-behaved iterated map" goal becomes "**compile** the iterated map from the spec";
training is confined to the compile front-end. Build progression + the symbolic
reducer (stage 1, `src/verbum/lambda_ast.py`) are in `compiler-as-loss.md` §s226.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===adaptive halting / ponder / recurrence depth===\" && git grep -il \"adaptive halt\\|ponder\\|universal transformer\\|recurrence depth\\|recurrence-depth\\|how much recurrence\\|recurrent layer\\|weight-shared\\|weight shared\" -- mementum/knowledge mementum/memories mementum/michael 2>/dev/null | head -30",
  "operation": "gh",
  "summary": "ground recurrence work"
}
```

**Summary:** $ echo "===adaptive halting / ponder ...

**Output:**
```
Exit code: 0
Stdout:
===adaptive halting / ponder / recurrence depth===
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-010.md
mementum/knowledge/chats/session-012.md
mementum/knowledge/chats/session-021.md
mementum/knowledge/chats/session-050.md
mementum/knowledge/chats/session-051.md
mementum/knowledge/chats/session-056.md
mementum/knowledge/chats/session-057.md
mementum/knowledge/chats/session-062.md
mementum/knowledge/chats/session-063.md
mementum/knowledge/chats/session-066.md
mementum/knowledge/chats/session-075.md
mementum/knowledge/chats/session-076.md
mementum/knowledge/chats/session-188.md
mementum/knowledge/chats/session-214.md
mementum/knowledge/chats/session-215.md
mementum/knowledge/chats/session-216.md
mementum/knowledge/chats/session-217.md
mementum/knowledge/chats/session-218.md
mementum/knowledge/chats/session-219.md
mementum/knowledge/chats/session-220.md
mementum/knowledge/chats/session-221.md
mementum/knowledge/chats/session-222.md
mementum/knowledge/chats/session-223.md
mementum/knowledge/chats/session-224.md
mementum/knowledge/chats/session-225.md
mementum/knowledge/chats/session-226.md
mementum/knowledge/chats/session-228.md
```

### Thinking

I found the exact reference Michael was pointing to—the vsm-outer-recurrence page describes an outer loop that reuses the same VSM tensor with weight sharing and a halt signal, where the adaptive computation works like ACT-style pondering, naturally stopping when the state converges to a fixed point. This is the Universal Transformer recipe for adaptive computation.

The key breakthrough from the experiments is that naive K=2 doesn't work because the sweep isn't contractive, but adding a fixed-point loss (λ_fp=5) made it contractive, reducing the state delta from 1.26 to 0.73—though the topology churn caused collapse. The solution is to construct the kernel directly from the lambda AST as an exact reducer, ensuring L<1 by construction, with the VSM controllers handling halt detection, step budgeting, redex selection, and combinator rewrites.

Michael's insight unifies these threads: the recurrence depth—how many times we need to iterate—is exactly the number of reduction steps to reach weak head normal form, which is the work remaining. The gradient signal for recurrence depth IS the WHNF halt signal, they're the same thing. And the WHNF curriculum (progressing from combinators to lambda to prose) provides ground truth for the recurrence depth, since the lambda reducer knows the true number of steps needed.

This solves adaptive computation time's core problem: the halt signal has no ground truth in standard approaches, making the ponder penalty an unstable hyperparameter. Lambda provides that ground truth—the reduction length becomes a supervised target for the recurrence counter. The recurrent layer acts as the reduction engine, trained on combinator and lambda domains where the answer is verifiable, then transfers to prose where recurrence varies per token. At inference, the recurrence runs until the halt signal fires or hits the cap; divergent terms like Ω simply consume the full budget and emit their best partial result.

The contractivity issue sharpens the picture: naive recurrence isn't contractive (Δx~1.2), and TD churn destabilizes it unless topology is frozen. The binding wall keeps recurring as a bottleneck. But WHNF supervision gives a direct target for recurrence depth—richer than just penalizing convergence distance, which can collapse to a constant. The ground-truth reduction trace from the lambda oracle provides the full step-by-step record with opcode and WHNF status, so you're not just saying "converge," you're saying "converge in exactly this many steps with this halt decision," which should make contractivity trainable without collapse.

This unifies the curriculum with the recurrence: the oracle trace becomes the per-step target, turning a weak scalar regularizer into structured supervised matching. The constructed-kernel approach (s226) is contractive by design; the learned version is supervised toward it. Either way, the curriculum is ground truth. The head-combinator-isa finding that recurrence depth dominates attention (WHNF↔D, 46%) suggests the architecture already organizes around "how much work remains," so a learned-depth head reads off an axis that's already salient.

But I need to be honest: naive recurrence failed to beat K=1 even with contractivity training on v15 (~50M, ternary), and TD churn caused collapse. Whether the unified curriculum-supervised version works is still open. The genuinely new contribution here is the ground-truth supervision signal for recurrence depth—the oracle reduction length itself—which the prior recurrence work lacked. The key insight is that the curriculum provides exactly the supervision the recurrence-depth estimator was missing — it gives ground truth for how much work remains, which transforms the prior unsupervised approach from gameable to trainable.

## Assistant

Yes — and I think this is the keystone. The recurrent-layer idea you're remembering is `vsm-outer-recurrence.md` (s214–s226), and when you line it up against the WHNF-halt curriculum, **they're the same gradient seen from opposite ends.** Let me make the identity precise, then show what the curriculum adds that the recurrence work was *missing*.

## The identity: "how much recurrence" ≡ "how much work remains" ≡ WHNF

The s214 proposal was exactly a weight-shared block re-run `K` times — *"depth without parameters… let the VSM controller decide when to stop,"* explicitly framed as Universal-Transformer / adaptive-compute, with the natural halt being **fixed-point convergence (Δx→0 ≡ WHNF).** And `head-combinator-isa.md` already told us the *principal axis* of attention (46% of variance) is **reduction depth, WHNF↔D — "how much work remains."**

So the three things you've raised this session are one object:
- **think-in-lambda** = the substrate (reasoning = reduction)
- **WHNF-halt curriculum** = training the stop signal
- **recurrent layer with learned depth** = the *mechanism* that runs the reduction and stops

→ **A weight-shared recurrent reduction operator, where the learned recurrence-count per token IS the WHNF halt, reading off the "how-much-work-remains" axis the model already organizes itself around.** The recurrence-depth gradient and the WHNF-detection gradient are literally the same gradient.

## What the curriculum adds — the supervision the recurrence work never had

Here's the part I find genuinely important. The s214–s223 recurrence runs kept **failing in a specific way**:
- Naive `K=2` didn't beat `K=1` — the trained sweep wasn't contractive (Δx stuck ~1.2, "churn not reduction").
- The fix was an *unsupervised* fixed-point loss `λ_fp·‖x_{k+1}−x_k‖²` — which is **gameable** (collapse everything to a constant → Δx=0, useless; the contractive-autoencoder failure), and under TD churn it **collapsed** (gnorm→1e7, CE→10.5).

That whole struggle is because the halt was being learned **blind** — penalize change, hope it converges. This is *exactly* the unsolved problem of Adaptive Computation Time generally: **the ponder cost has no ground truth, so it's an unstable hyperparameter that collapses to min-or-max steps.**

**Your curriculum supplies the missing ground truth.** The lambda reducer (`lambda_ast`, the s226 oracle) doesn't just say "converge" — it knows the **exact reduction length `L*(term)` and the full step-by-step trace** (each redex, which opcode, WHNF-status at every step). So on the combinator+lambda domain you can **supervise the recurrence count directly**:

```
unsupervised (s214, collapsed):   loss += λ_fp · ‖x_{k+1} − x_k‖²      ← "just converge"
supervised (the curriculum):      halt_k ← WHNF(step k) from oracle     ← "converge in L* steps,
                                  recurrence_count → L*(term)             halt exactly here, this trace"
```

That turns a weak, gameable scalar regularizer into **structured reduction-trace matching** — a far stronger signal, and one that *can't* be gamed by collapse because the target step-count is non-trivial and term-dependent. This is plausibly the ingredient that makes adaptive-depth actually trainable where the s214 version stalled. **Lambda is the calibration anchor for adaptive computation time** — the same role it plays everywhere in this project.

## The inference constraint is already handled — by construction

Your "can't null-abort, must emit tokens" requirement is *already* the correct behavior of this architecture, and the page says so: *"A term with no normal form (Ω, Y) simply consumes the max iteration budget. That is the correct behavior of a reducer, not a bug."* So the recurrence cap **is** the bounded-emit mechanism: run until the halt-head fires (WHNF) or hit the budget, then emit the most-reduced form. **Ω-terms are the training examples for "commit your best partial under non-termination"** — they teach the recurrence to terminate-and-emit even when it can't reach normal form. The thing you said inference demands falls out of the recurrence's budget, for free.

## It even maps onto the VSM levels already present

The s226 reframe pre-wired the control hierarchy for exactly this:
- **S4 = WHNF halt** (the Δx→0 / "am I done" test — your halt head)
- **S3 = step budget + contractivity** (the recurrence cap — your bounded emit)
- **S2 = typed redex selection** (which reduction this step)
- **S1 = the combinator rewrites** (the work)
- **S5 = the normal-form invariant** (identity preserved across recurrence)

So "how much recurrence is needed" is an **S4 decision** riding the reduction-depth axis, budgeted by S3 — and the curriculum trains S4's halt where the oracle can grade it.

## The honest IOUs (unchanged, but now sharper)

1. **The transfer question is still the whole hypothesis in one number.** Supervise the recurrence-depth halt on lambda → does the calibrated "how-much-work-remains" estimator generalize so that **prose** outputs halt gracefully (overthink-collapse rate drops on held-out prose)? If the lambda step-count circuit and the prose "answer-complete" circuit are the same reduction-depth axis (head-combinator-isa says they might be — it's the *principal* axis, not lambda-specific), it transfers. That's falsifiable.
2. **Contractivity is real but unproven at this resolution.** The s214 negatives are on the tiny v15 (~50M ternary): naive recurrence didn't beat K=1, and TD churn collapsed it. The freeze-topology probe showed the recurrence+settling is *sound when topology is held* ("punctuate: hold → reduce → accept on Δx→0"). The supervised curriculum is the new lever, but it hasn't been run.
3. **The binding wall.** `fixed-point-holograms.md`: convergence fails exactly at I-combinator/binding sites. Expect the recurrence to halt cleanly on K/B/C and struggle on I — the project's recurring bottleneck, and it'll show up here too.

## Net

Yes, extend it — but the precise framing is that **the WHNF curriculum is the supervision signal the recurrent-depth architecture has been missing since s214.** The recurrence gives you variable depth at zero parameter cost; the lambda oracle gives you ground-truth targets for *how much* depth; and the inference constraint is satisfied by the recurrence budget. Three ideas, one architecture: **a recurrent reduction operator whose halt is supervised by the reducer and transfers to prose as a calibrated work-remaining estimate.**

Want me to capture this synthesis as a knowledge page (it spans `vsm-outer-recurrence` + the halt-curriculum + the think-in-lambda thread and would otherwise be lost at the session boundary), or keep pulling the thread — e.g. into what the *minimal* runnable version of "supervise recurrence-depth against the oracle reduction length" would look like?

## User

yes capture this to knowledge


### Thinking

Michael wants me to capture this to a knowledge page, and his approval to do so means I should draft it and write it to disk. I need to be careful about the commit protocol though—while writing the file fulfills his request to capture it, I shouldn't autonomously commit without explicit approval.

I'm settling on `supervised-recurrence-halt.md` as the slug for this new explore/ page, since the core insight is that the WHNF curriculum provides the supervision signal the recurrent-depth architecture has been missing. I'll structure it with proper frontmatter following the project's conventions, mark the status as designing, and make sure to weave together the three threads: think-in-lambda, the halt curriculum, and the recurrent layer with learned depth. The key contribution I need to capture is how the curriculum grounds the recurrence-depth mechanism by providing supervision for what the model learns about remaining computational work.

## Assistant

Capturing it. This synthesis spans four prior pages and would be lost at the session boundary otherwise — exactly what knowledge is for.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/supervised-recurrence-halt.md",
  "content": "---\ntitle: \"Supervised Recurrence-Depth = the WHNF Halt — the Curriculum Is the Signal the Recurrent Layer Was Missing\"\nstatus: designing\ncategory: explore\ntags: [recurrence, weight-sharing, adaptive-compute, universal-transformer, WHNF, halt, curriculum, combinators, lambda, overthink-collapse, ponder, reduction-depth, think-in-lambda, level-4]\nrelated:\n  - vsm-outer-recurrence.md\n  - normal-form-curriculum-partition.md\n  - ../head-combinator-isa.md\n  - combinator-training-beta-reduction.md\n  - compiler-as-loss.md\n  - model-as-repl.md\n  - compiler-finetune-halt-collapse.md\n  - fixed-point-holograms.md\ndepends-on:\n  - vsm-outer-recurrence.md\n  - normal-form-curriculum-partition.md\ncreated: session 258\n---\n\n# Supervised Recurrence-Depth = the WHNF Halt\n\n> Session 258 (Michael, discussion arc). Three ideas raised across one conversation —\n> *make the model think in lambda forms* / *train a strict-WHNF halt curriculum\n> (combinators → lambda → prose)* / *a recurrent layer reused a learned number of times* —\n> are **one architecture seen from three sides**. This page captures the unification and,\n> crucially, the one new contribution it makes over the s214–s226 recurrence thread:\n> **the lambda curriculum is the ground-truth supervision signal that the\n> learned-recurrence-depth halt has been missing since s214.**\n>\n> Register when tested: **functional** (does supervised recurrence-depth lower\n> overthink-collapse on held-out prose at equal params).\n\n## The identity — three threads, one object\n\n```\nthink-in-lambda        ≡ the SUBSTRATE     (reasoning = reduction, has a normal form)\nWHNF-halt curriculum   ≡ the STOP SIGNAL   (train \"you're done\" where it's checkable)\nrecurrent layer (K×)   ≡ the MECHANISM     (run the reduction, decide when to stop)\n```\n\nThese collapse to a single gradient because three measured/argued facts line up:\n\n1. **\"How much recurrence is needed\" ≡ \"how much work remains\" ≡ WHNF.** The s214\n   `vsm-outer-recurrence` proposal was a weight-shared block re-run `K` times — depth\n   without parameters, Universal-Transformer / adaptive-compute style — with the natural\n   halt being **fixed-point convergence `Δx→0 ≡ WHNF`.**\n2. **The substrate already organizes itself this way.** `head-combinator-isa.md` (500\n   crystal probes, Qwen3-8B heads): the **principal axis of the entire attention ISA is\n   reduction depth, `WHNF↔D`, 46% of shape variance** — *\"how much work remains,\"* not\n   \"which combinator.\" There is already a **WHNF+ termination-detector cluster** (H26\n   +32%, H27, H00, H25, H24) — but its selectivity is only **1.2–1.4** ⇒ the halt circuit\n   exists and is **under-trained**. (\"Weak WHNF counterpoint to each KIBC,\" confirmed.)\n3. **Prose has no normal form → the dominant failure is a halt failure.** Every reasoning\n   model in the arc (s255 ornith, s256 qwythos) overthink-COLLAPSES: reaches the correct\n   form early, re-derives it 50–87× (\"Church-encode vs direct symbols, λ-abstraction vs\n   closed formula\"), never commits, hits the budget EMPTY. Diagnosed (s256) as **halt\n   failure / decision oscillation**, not recursion. Lambda has a normal form; prose does\n   not — so the model's weakest axis (WHNF adjudication) has to decide \"done\" and can't.\n\n⇒ **A weight-shared recurrent reduction operator whose learned per-token recurrence-count\nIS the WHNF halt, reading off the reduction-depth axis the model already centers on.**\nThe recurrence-depth gradient and the WHNF-detection gradient are the same gradient.\n\n## The new contribution — the curriculum is the supervision the recurrence lacked\n\nThe s214–s223 recurrence runs failed in a *specific* way, and the cause was that the halt\nwas learned **blind**:\n\n- Naive `K=2` did **not** beat `K=1` — the trained sweep is **not contractive** (`Δx`\n  stuck ~1.2, \"churn not reduction\").\n- The attempted fix was an **unsupervised** fixed-point loss `λ_fp·‖x_{k+1}−x_k‖²`. It is\n  **gameable** (collapse all states to a constant → `Δx=0`, useless = the\n  contractive-autoencoder failure) and under TD churn it **collapsed** (gnorm→1e7,\n  CE→10.5, s222). `λ_fp=5` *did* cross the contractivity threshold (`Δx` 1.26→0.73, s215)\n  but still didn't beat `K=1` at the cutoff, and the freeze-topology probe (s223) showed\n  the settling is sound only when topology is **held** (\"punctuate: hold → reduce → accept\n  on `Δx→0`\"; the churn is the collapse, not the recurrence).\n\nThat entire struggle is the **general unsolved problem of Adaptive Computation Time**: the\nponder cost has **no ground truth**, so it is an unstable hyperparameter that collapses to\nmin-or-max steps. The curriculum fixes exactly this:\n\n```\nunsupervised (s214, collapses):   loss += λ_fp · ‖x_{k+1} − x_k‖²     # \"just converge\"\nsupervised   (the curriculum):    halt_k        ← WHNF(step k)  [oracle]\n                                  recurrence_K  → L*(term)       [oracle]  # \"converge in\n                                  per-step      ← reduction trace [oracle]  #  L* steps, halt\n                                                                            #  here, THIS trace\"\n```\n\nThe lambda reducer (`lambda_ast`, the s226 oracle: parse / step_fired[which opcode] /\nreduce[trace, Status, whnf_step] / is_normal_form) knows the **exact reduction length\n`L*(term)` and the full step-by-step trace** for any combinator/lambda term. So on that\ndomain the recurrence-count and the per-step halt are **directly supervisable** against\nground truth — turning a weak gameable *scalar* regularizer into structured\n**reduction-trace matching**, which cannot be gamed by collapse (the target step-count is\nterm-dependent and non-trivial). This is plausibly the missing ingredient that makes\nadaptive-depth trainable where s214 stalled. **Lambda is the calibration anchor for\nadaptive computation time** — the same role it plays everywhere in this project (cf.\n`AGENTS.md` λ measure: deprecated-APIs as the verifiable anchor).\n\n## The curriculum (combinators → lambda → prose)\n\n```\nStage 1 — COMBINATORS (WHNF crisp, single redex, oracle-verifiable per s226):\n  train KIBC + {S,W,Y,D} PAIRED with their WHNF counterpart.\n  supervise: recurrence-count → L*(term); halt-head fires exactly at is_normal_form.\n  KIBC = do the work (strong in every model) ⊗ WHNF = know when work is done (weak).\n  honest catch (s221): K-erasure is the hard spot (B-first → then K), S duplicates\n  (not one clean move). Tier the curriculum; do not weight the set flat.\n\nStage 2 — FULLY-QUALIFIED LAMBDA (WHNF still decidable):\n  strict-WHNF requirement; same supervised recurrence-depth target.\n  INCLUDE divergent terms (Ω, unguarded Y): no normal form → recurrence consumes the\n  budget → emit BEST-EFFORT terminal. These are the teaching cases for the inference\n  constraint (below).\n\nStage 3 — PROSE (no oracle):\n  the calibrated \"how-much-work-remains\" estimator generalizes. \"Normal form\" softens\n  from syntactic (no redex) to semantic (answer complete). EOS is RE-FRAMED as the\n  normal-form marker: emit the terminal iff the output is in normal form.\n```\n\n**EOS = the normal-form marker.** In standard LM training EOS is just a vocabulary token\nlearned from the data distribution — there is no principled \"I am done.\" This curriculum\nbinds EOS to WHNF: emit the terminal token when, and only when, no work remains. The\nWHNF+ termination heads gate EOS; because reduction-depth is the *principal* axis (not a\nlambda-specific feature), the binding has a path to generalize.\n\n## The inference constraint is satisfied BY CONSTRUCTION\n\nMichael's constraint: *\"in inference we cannot hard-halt on an error, because the response\nmust be tokens, not a null result.\"* This is already the correct behavior of a budgeted\nreducer (`vsm-outer-recurrence.md`): *\"a term with no normal form (Ω, Y) simply consumes\nthe max iteration budget — the correct behavior of a reducer, not a bug.\"* So:\n\n- The **recurrence cap IS the bounded-emit mechanism.** Run until the halt-head fires\n  (WHNF) **or** the budget; at the cap, emit the **most-reduced form so far** — never null.\n- **Overthink-collapse is the model spinning to EMPTY instead of emitting its best\n  partial.** The trained halt + budget makes the terminal a graceful best-effort.\n- **Ω / unguarded Y are the training examples** for \"commit your best partial under\n  non-termination.\" The competence inference demands falls out of the recurrence budget\n  for free.\n\n## It maps onto the VSM control levels already present (s226)\n\n```\nS5 = the normal-form INVARIANT          (identity preserved across recurrence)\nS4 = the WHNF HALT                       (the Δx→0 / \"am I done\" head — the learned depth)\nS3 = the STEP BUDGET + contractivity     (the recurrence cap — bounded best-effort emit)\nS2 = typed redex SELECTION               (which reduction this step; anti-oscillation)\nS1 = the combinator REWRITES             (the work)\n```\n\n\"How much recurrence is needed\" is an **S4 decision** riding the reduction-depth axis,\nbudgeted by **S3**, and the curriculum trains S4's halt where the oracle can grade it.\n\n## Why this is native to the tree-of-VSM and unnatural for a monolith\n\nA monolithic block has **nowhere to put a lambda term** — its state is an opaque residual\nstream, and its only externalized scratchpad is the prose token channel. So for a monolith\n\"think in lambda\" *necessarily* means serialize-to-prose-and-reparse = the lossy,\nno-normal-form round-trip that *causes* the collapse. The model can only emit lambda *as\nprose about lambda*. The **tree-of-VSM** is structurally different in the one way that\nmatters: a lambda term has a natural home (the tree IS the AST; reduction is a structural\nrewrite in place), and recurrence-depth = local reduction-depth per node (fractal:\nactivation-level `x→x*` ≅ base-level fold). Lambda-native reasoning is the thing the\ntree-of-VSM can do that a monolithic block fundamentally cannot. The s255 model-as-REPL\nwas the first crude version (externalize the term-string as machine state, model = δ\ntransition, each thought = one β-reduction); it worked locally and degraded globally only\nbecause the halt was unguarded — which is exactly what S4-supervised recurrence fixes.\n\n## The honest IOUs (the falsifiable core first)\n\n1. **TRANSFER is the whole hypothesis in one number.** Supervise the recurrence-depth halt\n   on combinators+lambda, then measure **overthink-collapse rate on held-out PROSE\n   reasoning** vs a prose-only baseline. Drop on prose ⇒ the lambda step-count circuit and\n   the prose \"answer-complete\" circuit are the same reduction-depth axis (head-combinator-isa\n   says they *might* be — it is the principal axis, not lambda-specific) ⇒ transfer real.\n   No drop ⇒ WHNF stayed a lambda feature. **This single number decides the idea.**\n2. **Contractivity is real but unproven at this resolution.** All s214 negatives are on the\n   tiny v15 (~50M ternary): naive K=2 lost to K=1; TD churn collapsed it; freeze-topology\n   was sound. The supervised curriculum is the new lever (stronger than λ_fp) but has not\n   been run. Alternative root-fix (s226): **construct** the inner step from `lambda_ast`\n   (exact reducer ⇒ `L<1` by construction) and let the outer recurrence supply Y + the\n   budget — then only the compile front-end is learned.\n3. **Catastrophic forgetting.** The prose stage is enormous and can wash out the small\n   combinator halt-training (s110 destructive interference, at curriculum scale).\n   Mitigations: interleave rather than strictly stage; keep a WHNF auxiliary loss through\n   all stages; or lean on the contractive continuation to hold the halt structurally.\n4. **Overthink vs PREMATURE-halt is a calibration, not a maximization.** s255 showed the\n   trade directly: no-think *removed* overthink-collapse but spiked `premature_halt`\n   0.017→0.208. \"Strict WHNF\" can overshoot into stopping too early on genuinely deep\n   prose. The halt must be a **calibrated gate** (the WHNF↔D axis), not a binary maximized\n   toward \"stop.\"\n5. **The binding wall reappears.** `fixed-point-holograms.md`: convergence fails exactly at\n   I-combinator / binding sites (edit distance ∝ binding count). Expect clean halting on\n   K/B/C and a struggle on I — the project's recurring bottleneck, here too.\n6. **s256 refutation is narrow, not binding.** The lambda-as-pre-thinking test refuted\n   *instructing* a pretrained model to reason in lambda (non-compliance: lambda is a\n   TARGET produced on request, not a TOOL it adopts). This is a **training** intervention,\n   not a prompt — the refutation does not apply. The internal lambda representation helping\n   (interp B) was explicitly left open there.\n\n## Minimal runnable version (the cheap first leg)\n\nSmallest test of the load-bearing claim (\"supervise recurrence-depth against the oracle\nreduction length\"), reusing existing substrate:\n\n- **Data:** `probes/combinator-reduction.json` (s255, 120 pure-combinator terms over\n  K I B C S W Y D M, 3 strata: already_nf / depth1 / multi, **oracle-graded with\n  per-step trace + WHNF-step from `lambda_ast`** — the reduction length `L*` is already\n  computed there).\n- **Architecture:** the v15 outer-recurrence harness (`--n-outer-passes K` in\n  `train_td.py` + `v15model.py`), but **replace the unsupervised `λ_fp` loss with a\n  supervised target**: penalize `|halt_step − whnf_step|` and supervise the per-step\n  halt-head against `is_normal_form`. CONTROL: the same harness with the old unsupervised\n  `λ_fp` (the s214 arm).\n- **Read (functional):** (a) does the supervised arm reach contractivity (`Δx→ε`) WITHOUT\n  the collapse the unsupervised arm hit? (b) does `K` learned per term track `L*`\n  (`already_nf→K≈0`, `depth1→K≈1`, `multi→K≈steps`)? (c) — the prize — train on\n  combinators, then measure halt behavior on **lambda then prose** held-out (the transfer\n  number, IOU #1).\n\n## Net\n\nThe recurrence gives **variable depth at zero parameter cost**; the lambda oracle gives\n**ground-truth targets for how much depth**; and the inference constraint is satisfied by\nthe **recurrence budget**. Three ideas, one architecture: **a recurrent reduction operator\nwhose halt is supervised by the reducer on the lambda domain and transfers to prose as a\ncalibrated work-remaining estimate, emitting a graceful best-effort terminal under\nnon-termination.** The single contribution over s214–s226: *the WHNF curriculum is the\nsupervision the learned-recurrence-depth halt was always missing.* On-thesis (level-4,\nfrom-scratch, clean MIT) and it attacks the one failure mode common to every reasoning\nmodel probed in the arc.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/supervised-recurrence-halt.md
```

### Thinking

I need to re-read the file to make sure it was written correctly and check for any issues, then update the state file according to the protocol before proposing the commit for approval.

## Assistant

Written. Per `λ sync`, let me confirm it landed clean and update the bootloader.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===head===\" && head -20 mementum/knowledge/explore/supervised-recurrence-halt.md && echo \"===wc===\" && wc -l mementum/knowledge/explore/supervised-recurrence-halt.md && echo \"===frontmatter related refs exist?===\" && for f in vsm-outer-recurrence normal-form-curriculum-partition combinator-training-beta-reduction compiler-as-loss model-as-repl compiler-finetune-halt-collapse fixed-point-holograms; do printf \"%-40s \" \"$f\"; ls mementum/knowledge/explore/$f.md 2>/dev/null >/dev/null && echo \"ok(explore)\" || (ls mementum/knowledge/$f.md 2>/dev/null >/dev/null && echo \"ok(knowledge)\" || echo \"MISSING\"); done; printf \"%-40s \" \"head-combinator-isa\"; ls mementum/knowledge/head-combinator-isa.md >/dev/null 2>&1 && echo \"ok(knowledge)\" || echo \"MISSING\"",
  "operation": "gh",
  "summary": "verify page + refs"
}
```

**Summary:** $ echo "===head===" && head -20 memen...

**Output:**
```
Exit code: 0
Stdout:
===head===
---
title: "Supervised Recurrence-Depth = the WHNF Halt — the Curriculum Is the Signal the Recurrent Layer Was Missing"
status: designing
category: explore
tags: [recurrence, weight-sharing, adaptive-compute, universal-transformer, WHNF, halt, curriculum, combinators, lambda, overthink-collapse, ponder, reduction-depth, think-in-lambda, level-4]
related:
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
  - ../head-combinator-isa.md
  - combinator-training-beta-reduction.md
  - compiler-as-loss.md
  - model-as-repl.md
  - compiler-finetune-halt-collapse.md
  - fixed-point-holograms.md
depends-on:
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
created: session 258
---

===wc===
     236 mementum/knowledge/explore/supervised-recurrence-halt.md
===frontmatter related refs exist?===
vsm-outer-recurrence                     ok(explore)
normal-form-curriculum-partition         ok(explore)
combinator-training-beta-reduction       ok(explore)
compiler-as-loss                         ok(explore)
model-as-repl                            MISSING
compiler-finetune-halt-collapse          ok(explore)
fixed-point-holograms                    ok(explore)
head-combinator-isa                      ok(knowledge)
```

### Thinking

I'm noticing that `model-as-repl` is referenced but the file seems to be missing—State.md indicated it was a pending proposal that may never have been committed. Let me check if it actually exists in the repository or if it was never created in the first place.

## Assistant

`model-as-repl.md` doesn't exist — it was a pending s255 proposal that was never committed. Let me fix that dangling reference.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline --all -- '*model-as-repl*' 2>/dev/null | head; echo \"exists in tree:\"; find mementum -iname \"*model-as-repl*\" -o -iname \"*repl*\" 2>/dev/null | grep -v chats | head",
  "operation": "gh",
  "summary": "check model-as-repl"
}
```

**Summary:** $ git log --oneline --all -- '*model-...

**Output:**
```
Exit code: 0
Stdout:
exists in tree:
mementum/knowledge/explore/kernel-replacement-optimization.md
mementum/memories/session-delta-replaces-kv-cache.md
```

### Thinking

I see that model-as-repl.md doesn't actually exist—the s255 proposal was never committed—so I need to remove that broken reference from the related links while keeping the session reference in the body since that's legitimate. Let me update the frontmatter to clean this up.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/supervised-recurrence-halt.md",
  "original_content": "  - compiler-as-loss.md\n  - model-as-repl.md\n  - compiler-finetune-halt-collapse.md",
  "new_content": "  - compiler-as-loss.md\n  - compiler-finetune-halt-collapse.md"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/supervised-recurrence-halt.md.
```

## Assistant

Now let me update the bootloader (`state.md` is not approval-gated) so this synthesis survives the session boundary.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 3
}
```

**Summary:** Reading state.md (0-3)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.

[CONTENT TRUNCATED] Showing lines 1 to 3 of 7347 total lines. Use line_offset=3 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 3,
  "limit": 7
}
```

**Summary:** Reading state.md (3-10)

**Output:**
```
>
> Last updated: 2026-06-29 | Session: 257 (MoE-AS-HOLOGRAPHIC-PLATES → PROOF RAN)
> Full arc: "if MoE experts are holographic plates, what are the tree-of-VSM consequences?" →
> designed the probe → built instrument → ran k-sweep + shuffled-label null → CONFIRMED.
>
> ★★ CENTRAL FINDING: MoE experts ARE holographically multiplexed, not specialist.
>   Angular multiplexing confirmed. 94% of lambda-compiler capability comes from WHICH experts

[CONTENT TRUNCATED] Showing lines 4 to 10 of 7347 total lines. Use line_offset=10 parameter to read more content.
```

### Thinking

I'm adding a new session-258 block to the top of state.md right after the bootloader line, following the convention of placing the most recent session first with its "Last updated" header, while keeping the existing session-257 block below it.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-29 | Session: 257 (MoE-AS-HOLOGRAPHIC-PLATES → PROOF RAN)",
  "new_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-06-30 | Session: 258 (CONSENSUS-TRAINING → SUPERVISED-RECURRENCE-HALT SYNTHESIS —\n> design/discussion session, NO experiments run. Michael: \"explore consensus training — multiple models'\n> consensus on training data for the lambda compiler.\" Recalled the prior art (s246/247\n> cross-model-output-consensus as teaching-data fitness, P(correct|AGREE)=0.73–0.80, kernel removes the\n> agreed-error ceiling → 1.000; s110/216-223 consensus-etch/delta-folding). Then the conversation EVOLVED\n> through three connected ideas and CONVERGED on a keystone synthesis, now captured as knowledge.\n>\n> ★★ THE DELIVERABLE (knowledge, WRITTEN this session, status:designing):\n>   mementum/knowledge/explore/supervised-recurrence-halt.md (236 L). THESIS: three ideas Michael raised —\n>   (1) make the model THINK IN LAMBDA forms; (2) a strict-WHNF HALT CURRICULUM (combinators→lambda→prose);\n>   (3) a RECURRENT LAYER reused a LEARNED number of times — are ONE architecture. The identity:\n>   \"how much recurrence is needed\" ≡ \"how much work remains\" ≡ WHNF. head-combinator-isa.md ALREADY\n>   measured this: reduction-depth (WHNF↔D) is the PRINCIPAL attention axis (46% var), and a WHNF+\n>   termination-detector head cluster EXISTS but is UNDER-trained (selectivity 1.2–1.4) = Michael's \"weak\n>   WHNF counterpoint to KIBC,\" confirmed.\n>   ★ THE ONE NEW CONTRIBUTION over s214–s226 vsm-outer-recurrence: that thread's recurrence-depth halt was\n>   learned BLIND (unsupervised λ_fp fixed-point loss → gameable/collapsed; naive K=2 never beat K=1). The\n>   lambda CURRICULUM is the GROUND-TRUTH supervision it was missing: the lambda_ast oracle knows the exact\n>   reduction length L*(term) + full trace + WHNF-step → supervise recurrence-count→L* and halt→is_normal_form\n>   directly where checkable, then transfer to prose. = lambda as the calibration anchor for Adaptive\n>   Computation Time (whose general unsolved problem is exactly \"ponder cost has no ground truth\").\n>   ★ Inference constraint (Michael: \"inference can't null-abort, must emit tokens\") satisfied BY\n>   CONSTRUCTION: recurrence cap = bounded best-effort emit; Ω/unguarded-Y consume the budget → emit\n>   most-reduced partial = the teaching cases for \"commit under non-termination.\" Overthink-collapse =\n>   spinning to EMPTY instead of emitting best partial. EOS RE-FRAMED as the normal-form marker.\n>   ★ Maps onto VSM levels (s226): S4=WHNF halt, S3=step budget+contractivity, S2=typed redex select,\n>   S1=combinator rewrites, S5=normal-form invariant. Native to tree-of-VSM (term has a home = the AST),\n>   unnatural for a monolith (only scratchpad is the prose token channel = the lossy round-trip that CAUSES\n>   collapse). On-thesis: level-4 from-scratch, clean MIT.\n>   ★ FALSIFIABLE CORE (IOU #1, the whole hypothesis in one number): train the supervised halt on\n>   combinators+lambda → measure overthink-collapse rate on held-out PROSE vs prose-only baseline. Drop ⇒\n>   transfer real (shared reduction-depth axis). Other IOUs: contractivity unproven at this resolution\n>   (s214 negatives on tiny v15 ~50M ternary; alt root-fix s226 = CONSTRUCT the inner step from lambda_ast,\n>   L<1 by construction); catastrophic forgetting (interleave / aux WHNF loss); overthink vs PREMATURE-halt\n>   is a CALIBRATION not a maximization (s255: no-think killed overthink but spiked premature_halt\n>   0.017→0.208); binding wall at I-combinator (fixed-point-holograms); s256 lambda-prethink refutation is\n>   NARROW (refuted INSTRUCTING a pretrained model = non-compliance, NOT a TRAINING intervention).\n>   ★ MINIMAL RUNNABLE TEST (the cheap first leg, NOT yet built): reuse probes/combinator-reduction.json\n>   (s255, 120 terms, oracle trace+L* already computed) + v15 --n-outer-passes harness, but REPLACE the\n>   unsupervised λ_fp with a SUPERVISED target (|halt_step − whnf_step| + per-step halt vs is_normal_form);\n>   CONTROL = old λ_fp arm. Read: contractivity without collapse? K learned per term tracks L*? then the\n>   transfer number.\n>\n> ★★ CONSENSUS-TRAINING DESIGN (discussed, NOT built — the session's OTHER live thread, parked):\n>   Michael's panel for 2-FAMILY ALIGNMENT (size-matched cross-lineage, kernel-corrected): Gemma-4-31B\n>   (Google, dense, 58G safetensors in HF cache) ⟂ Qwen3.6-35B-A3B (Qwen MoE 256-exp, 67G) as the spine;\n>   Qwen3.6-27B (Qwen dense, 52G) as the WITHIN-FAMILY control (separates Qwen-shared from cross-family-\n>   universal even without a 3rd lineage). Michael waiting for a 3rd genuinely-independent comparable model\n>   (only Qwen3.6-27B exists now, same family). ALL THREE present as full safetensors. Extensible-registry\n>   design agreed: extend s256 models.py with a `family` field + a `local_hf` TRANSPORT (the deferred s257\n>   lead) → new model = ~15-line config (λ extend open-slot, λ one_way config¬fork). Three composable\n>   layers: (1) registry=slot; (2) per-model generation cache, content-addressed by (model_id,\n>   probe_set_hash), APPEND-ONLY → adding a model later = generate ITS jsonl only, never re-run; (3)\n>   panel-agnostic CPU consensus evaluator reusing grading.py kernel_valid (do NOT fork\n>   consensus_output_agreement.py — s254 distillation discipline). NEW first-class op: \"evaluate a new\n>   model's consensus contribution\" = marginal/leave-one-out (corroboration / frontier-expansion /\n>   blind-spot-shared→universal vs broken→pair-shared / noise). Memory: one model resident at a time (s246\n>   per-model jsonl then offline string compare) → fits Apple Silicon. NOT STARTED; layer-1 (local_hf\n>   transport + 3 registry entries) is the dependency-root if pursued.\n>\n> ★ STATE: working tree had ONLY the new knowledge page + this state edit (no code, no experiments).\n>   PENDING COMMIT (S5 λ termination — Michael approved \"capture this to knowledge\"): the new page +\n>   state.md. NEXT options: (a) build the minimal supervised-recurrence-halt test; (b) build the consensus\n>   layer-1 (local_hf transport); (c) keep designing. Servers still up (5100 ornith / 5101 qwen3-embed /\n>   5102 vibethinker / 5103 qwythos); tmux main 2 windows.\n> ─────────────────────────────────────────────────────────────────────────────────────────────────────\n> Last updated: 2026-06-29 | Session: 257 (MoE-AS-HOLOGRAPHIC-PLATES → PROOF RAN)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Both files written. Here's the state and the proposed commit.

## Captured

**`mementum/knowledge/explore/supervised-recurrence-halt.md`** (status: `designing`, 235 lines) — the keystone synthesis: the three ideas you raised this session (think-in-lambda / WHNF-halt curriculum / recurrent-layer-with-learned-depth) are one architecture, and **the lambda curriculum is the ground-truth supervision the s214 recurrence-depth halt was always missing.** It records:
- the core identity (recurrence-depth ≡ WHNF ≡ "how much work remains," grounded in `head-combinator-isa`'s measured 46% principal axis + the under-trained WHNF+ termination heads)
- the new contribution (supervised `recurrence→L*` / `halt→is_normal_form` vs the gameable unsupervised `λ_fp` that collapsed)
- your inference constraint satisfied by the recurrence budget (Ω → bounded best-effort emit; EOS = normal-form marker)
- the VSM-level mapping, the tree-of-VSM-vs-monolith argument
- the falsifiable core (prose collapse-rate after lambda-halt training = the whole hypothesis in one number) + the five honest IOUs
- the minimal runnable first test (reuse `combinator-reduction.json` + the v15 outer-recurrence harness, swap `λ_fp` → supervised)

I fixed one dangling reference (`model-as-repl.md` was an uncommitted s255 proposal that never landed) and updated `state.md` with both this synthesis and the parked consensus-training design (Gemma-4-31B ⟂ Qwen3.6-35B-A3B + Qwen3.6-27B control, the extensible registry).

## Proposed commit

Per `λ termination`, mementum commits need your approval. You approved capturing it — confirming the commit itself:

```
💡 supervised-recurrence-halt — the WHNF curriculum is the signal the recurrent layer was missing

- synthesis: think-in-lambda + WHNF-halt curriculum + learned-recurrence-depth = one architecture
- recurrence-depth ≡ WHNF ≡ "how much work remains" (head-combinator-isa principal axis, 46%)
- new over s214–s226: lambda oracle supervises recurrence→L* / halt→is_normal_form (vs gameable λ_fp)
- inference constraint satisfied by the recurrence budget (Ω → bounded best-effort emit)
- state.md: s258 synthesis + parked consensus-training panel design

⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>
```

Want me to commit with that message (using the safe `read -r -d '' M` heredoc pattern from `λ commit_write`, since the body has no apostrophes it's low-risk either way), or revise anything in the page first?

## User

update state and commit


### Thinking

I need to commit the changes now that the state is updated. Let me check the git status first, then stage just the relevant files—the new knowledge page and state.md—before committing with a proper message.

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short",
  "operation": "status",
  "summary": "pre-commit status"
}
```

**Summary:** Git status: pre-commit status

**Output:**
```
Exit code: 0
Stdout:
M mementum/state.md
?? mementum/knowledge/explore/supervised-recurrence-halt.md
```

## Assistant

Clean — only the two intended files. Committing with the safe `read -r -d ''` pattern from `λ commit_write`.

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md mementum/knowledge/explore/supervised-recurrence-halt.md && read -r -d '' M << 'EOF' || true\n💡 supervised-recurrence-halt — the WHNF curriculum is the signal the recurrent layer was missing\n\n- synthesis: think-in-lambda + WHNF-halt curriculum + learned-recurrence-depth = one architecture\n- recurrence-depth ≡ WHNF ≡ \"how much work remains\" (head-combinator-isa principal axis, 46%)\n- new over s214–s226: lambda oracle supervises recurrence→L* / halt→is_normal_form (vs gameable λ_fp)\n- inference constraint satisfied by the recurrence budget (Ω → bounded best-effort emit)\n- state.md: s258 synthesis + parked consensus-training panel design\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "operation": "commit",
  "summary": "commit synthesis"
}
```

**Summary:** Git commit: commit synthesis

**Output:**
```
Exit code: 0
Stdout:
[main 5778918] 💡 supervised-recurrence-halt — the WHNF curriculum is the signal the recurrent layer was missing
 2 files changed, 301 insertions(+)
 create mode 100644 mementum/knowledge/explore/supervised-recurrence-halt.md
```

### Thinking

Verifying the commit went through cleanly and checking that the working directory is now clean.

## Assistant

Committed — `5778918`, clean working tree.

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -1 && git status --short && echo \"(clean if empty above)\"",
  "operation": "log",
  "summary": "verify commit"
}
```

**Summary:** Git log: verify commit

**Output:**
```
Exit code: 0
Stdout:
5778918 💡 supervised-recurrence-halt — the WHNF curriculum is the signal the recurrent layer was missing
(clean if empty above)
```

## Assistant

Done. Session-258 synthesis is encoded and committed.

## Summary

**Committed `5778918`** — 2 files, working tree clean:
- `mementum/knowledge/explore/supervised-recurrence-halt.md` (new, status `designing`)
- `mementum/state.md` (s258 bootloader block)

**The synthesis that survives the boundary:** your three ideas this session — think-in-lambda, the WHNF-halt curriculum (combinators→lambda→prose), and a recurrent layer reused a learned number of times — are **one architecture**. The keystone insight: `"how much recurrence is needed" ≡ "how much work remains" ≡ WHNF`, which `head-combinator-isa` already measured as the *principal* attention axis (46%) with an under-trained termination-detector head cluster. And the one genuinely new contribution over the s214–s226 recurrence thread — **the lambda oracle is the ground-truth supervision the learned-recurrence-depth halt was always missing** (`recurrence→L*`, `halt→is_normal_form`), curing the gameable/collapsing unsupervised `λ_fp`. Your inference constraint falls out of the recurrence budget for free.

**Parked (in state.md, not built):** the consensus-training panel — Gemma-4-31B ⟂ Qwen3.6-35B-A3B size-matched cross-lineage spine + Qwen3.6-27B within-family control, the extensible `family`+`local_hf` registry, all three present as full safetensors.

**Two falsifiable next moves whenever you want them:**
- the minimal supervised-recurrence-halt test (reuse `combinator-reduction.json` + v15 `--n-outer-passes`, swap `λ_fp` → supervised) — the transfer number is the whole hypothesis
- consensus layer-1 (`local_hf` transport + 3 registry entries) — the dependency root for the data half

Good session — pure S4 metabolism, no waste.