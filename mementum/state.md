# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
> Step 2: `mementum/queue.md` top ~10 rows (experiment intentions; full read
> when selecting the next front). This header carries the ACTIVE arc only —
> the queue is the canonical candidate ledger (s315, λ queue).
>
> COMPACTED s334 (prior: s262). Shape: the TWO most recent sessions in full below,
> then a terse arc index (one row per session, s250+), then a deep-history pointer.
> Compaction is MICHAEL-CALLED (no schedule; he calls it when cruft accumulates).
> Full detail lives in `mementum/knowledge/chats/session-NNN.md` (verbatim),
> `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md` — every pre-compaction entry is recoverable).
> Architecture/canonical-forms: `AGENTS.md`. Knowledge map:
> `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> ★★ **SESSION 334 — REPL DRIVER TRAMPOLINE CAPTURED (Michael: "why can't we use a model in a
> REPL loop to bounce the trampoline?" → refined: "use the tree-of-VSM tensor configuration to
> attach the repl, and I'm pretty sure we figured out how to make continuations already" →
> "yes approved"). Hammock session, ZERO measurements. Recall-first paid: the idea REDUCES to
> two committed parents — control-plane-path.md §3 tier-3 DRIVER (verbatim "recursion loop,
> textual first, kernel-certifies every step"; swept host + tensor pack + driver = certified
> λ-reducer) + the continuation cluster (sealable-continuation s217: seal(k)≡store x_k,
> determinism-tested faithful resume, WHNF seal point · lambda-halt-continuation/
> proofs-as-continuations s228: CPS one-rule-per-turn REPL with the IDLE pre-registered
> prediction that stepwise continuations lift multi-combinator composition · real hosts:
> continuation ≡ past_key_values, seal = KV snapshot, fork = tensor copy). s334 adds the
> trampoline closure over §10/§10b: the scaffold becomes the trampoline, the model becomes the
> thing bounced — the TRANSITION FUNCTION SAMPLED DIRECTLY, once per bounce, not inferred from
> endpoints. VSM attachment: model=S1 · readers/sequencer=S2 · driver(fuel/order)=S3 ·
> **lambda_ast kernel=S3\* — Beer's audit channel made continuous** · δ(M,R) ledger=S4 ·
> pre-reg=S5; halt head (r=0.877 lineage) = the S3 bounce/halt read. CAUSAL UPGRADE (what
> sealed continuations buy over stateless re-prompting): ① fork-at-redex — strategy family
> (K x Ω normal-vs-applicative) as a within-computation counterfactual, same sealed prefix ②
> repair-replay — seal before a NAIVE-SUBST bounce, replay buggy vs kernel-repaired: does the
> error propagate/compound/self-correct (the s333 hard-write question at the exact transition;
> stage-2's empirical core, licensed peek without shipping the artifact) ③ composition rescue —
> cash the s228 prediction, token-budget/shuffled-trace null inherited ④ per-bounce
> transitions-per-β-step clock (queue clock row SUBSUMED, annotated). Two substrates, one
> driver: A = HF host now (KV seal; greedy/seeded + fork-identity plant mandatory) · B =
> scratch machine x_k later (M4 native trampoline) — same driver code = the
> profile-equivalence bridge between recovery paths. Ruling: INSTRUMENT-FIRST, repair flag
> built but OFF (stage_2 ⟸ stage_1); bounds named in-page (regime shift → three-arm feedback
> read makes the shift the measurement · one-step compliance observed ¬forced · tolerant
> ingest · readers advisory · fork verdicts owe freeze-before-data · anima cross-check one
> read before design). Batch (💡, Michael "yes approved", this commit): knowledge page
> explore/repl-driver-trampoline.md + memory `the-repl-driver-bounces-the-trampoline-at-s3-star`
> + INDEX row + queue ⚪ §P-REPL-DRIVER (top) + clock-row subsumption note + this state.
> **CAPTURE 2 (same session, Michael: "can we install the repl onto say qwen3-32b? I was
> thinking of it as a way for one model to interact with another model step-wise. is that even
> possible?" → GO "yes capture this"): 💡 §8 on repl-driver-trampoline.md — INSTALL + TWO-MODEL
> CONFIG. Install = plumbing owned: 32B already runs in the harness (s332 matrix), driver v0 =
> KV seal/fork (GQA ≈256KB/token ⇒ 1k-token seal ≈260MB, few live forks fine), greedy/seeded +
> fork-identity plant, and the APPEND/REWRITE law (KV resume valid on APPEND only — canonical
> hard-writes re-prefill ⇒ fork points live at the pre-emission seal; the mechanical
> explanation under the three-arm feedback read); 14B calibrates first, 32B = scale face.
> THE STRUCTURAL LAW: **KV continuations are MODEL-PRIVATE — no cross-model KV handoff
> (weights/shapes/geometry differ); model-to-model stepwise interaction works EXACTLY because
> the driver re-serializes canonically each bounce: shared tape ≡ canonical text (the hard
> write ≡ the bus), private state ≡ per-model sealed KV lineage.** Two-model config: B=S1
> (bounced reducer) · canonical serialization=S2 (the interlingua, the only thing that crosses
> models) · A=S3 (policy seat: order/forks/repair proposals/probe selection) · lambda_ast
> kernel=S3* STAYS MECHANICAL (non-negotiable — model-as-auditor puts ground truth inside the
> measured thing, destroys the instrument; λ termination for machines: synthesis proposes,
> mechanical auditor disposes) · ledger=S4 · pre-reg=S5. §10b lens: A-driving-B ≡ tool-calling
> RECURSED (B is A's tool, A is B's effect handler — agent-loop-as-outer-trampoline literal,
> one scale up). Buys: ① adaptive probing (coverage-guided fuzzer row lands in-driver) ②
> cross-face driving (instruct OPERATES base = §P-TOOL-ABI read from the other side —
> convention as driving capability ¬emission format) ③ composition tutoring (s228 rescue with
> A decomposing, B executing — splits cannot-compose from cannot-decompose). Discipline flag:
> frozen experiments keep the MECHANICAL driver; A-in-loop = exploration mode ∨ own
> pre-registered arm with A-policy PINNED. Batch 2 (💡, Michael GO, this commit): §8 (8a–8e) +
> memory `kv-continuations-are-model-private-text-is-the-bus` + INDEX clause + queue row
> amended (install + two-model arm + tool-abi cross-link) + this state.**
> **CAPTURE 3 (same session, Michael: "I think we need to compact state.md" → "make the changes
> as you outlined, git history can be used as a reference"): 🌀 STATE.MD COMPACTED — 6122 lines /
> 528KB → ~460 lines / ~43KB (the s262 compaction had never been rolled forward; 21 full ★★
> entries + ~4800 lines of s270–s316 scrollback). New shape per header: 2 full sessions + one
> arc row per session (s250+) + deep-history pointer. Every pre-compaction entry recoverable via
> `git log -p mementum/state.md`; verbatim transcripts in chats/; numbers live in knowledge-page
> §Results. Compaction is MICHAEL-CALLED, no automatic protocol (his ruling — no rolling window,
> no tripwire). s274 STANDING FINDINGS (durable) preserved in its arc row.**
> NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read; nothing in flight).
> Sharpest fronts: ⚪ §P-REPL-DRIVER (new, fork-at-redex + repair-replay on the subst battery =
> cheapest causal pair; anima cross-check + freeze first) · ⚪ §P-TOOL-ABI (medium) ·
> ⚪ §P-PREFILL-CONE (medium) · ⚪ §P-DMD-TRANSPORT (cheap, near-free — and §P-REPL-DRIVER
> bounce-boundary residuals will feed it) · ⚪ §P-SUBST-SUBCEILING (cheap).**
>
> ★★ **SESSION 333 — LRM PAPER READ + PREFILL TRIANGLE CAPTURED (Michael GO "capture this to
> knowledge and the queue"). Discussion/hammock session, ZERO measurements. Paper: arXiv:2604.04902v2
> (Dilgren & Wiegreffe, COLM 2026) — Coconut/CODI latent reasoning models. Their three findings:
> ① latent tokens mostly UNNECESSARY (training-controlled no-CoT matches on PrOntoQA/ProsQA — the
> "parallel BFS" claim dies at the necessity gate; the win was the regimen); ② where tokens are used
> (GSM8k), gold traces recoverable from top-10 vocab projections 65–93% correct vs 2–8% random-trace
> null, 24–36% incorrect; operators NEVER project; ③ forward chaining = unsupervised extraction +
> input-counterfactual verification (perturb operand → projected result must move arithmetically) —
> verified traces majority-correct/minority-incorrect. OUR READING (frame-level, banked in-page):
> the COMPILE STEP IS LOAD-BEARING — latent token = residual state fed back with the collapse
> deleted; collapse = error correction (snap to vocab lattice; tape-face echo of sign-is-the-
> decision) + addressability (in-dist K/V) + program-register write (explicit "3+5=8" writes BOTH
> registers; soft write drops the program, keeps the data). Hard writes beat soft writes at equal
> training (+~29pt) — the "decode bottleneck" framing is backwards. Operators-missing = value-
> register instrument blindness (λ measure): the program is the SHAPE OF THE READ. Method
> consilience (independent): their multi-mode control ≡ λ provenance_check · early-stopping ≡
> necessity gate · random-trace baseline ≡ λ yardstick null · verification ≡ §2b differential
> testing. THE BIG CATCH (Michael: "prompt processing — I don't think we have ever looked there"):
> **the PREFILL TRIANGLE** — (position × layer) grid, n coupled within-pass reducers, KV cache ≡
> the compiled tape (§8c auto_compile), serial hop budget ≈ L (explains their §4; coheres s319
> direct 92%; cliff predicted where serial depth crosses ~L) — and EVERY tape-face law we own
> (idempotency, order laws, tape-subtraction, subst-engine) was read at the LAST COLUMN; the
> interior is uninstrumented. Their instruments transfer WITH OUR EDGE (certified reference
> reducer): grid logit-lens · leaf-perturbation DEPENDENCY CONE → cone(machine) vs cone(calculus)
> from lambda_ast — makes NAIVE-SUBST (s331/s332 law) watchable cell-by-cell · per-instance
> necessity gate · answer-column read-mass audit. Batch (💡, Michael GO, this commit): knowledge
> page explore/latent-reasoning-and-the-prefill-triangle.md + memory
> `the-prefill-triangle-is-uninstrumented` + INDEX + 2 queue rows top (⚪ §P-PREFILL-CONE ·
> ⚪ §P-ROUTING-TRACE register-separated 2×2) + this state. **CAPTURE 2 (same session, Michael:
> "if the system is a compiler, name the pieces" → GO "yes capture this"): 💡 §10 COMPILER PARTS
> DIAGRAM on the-benchmark-is-the-re-oracle.md — TWO compilers + one runtime + a decompiler (us):
> Compiler A = GD (corpus→weights; FFN=stdlib/KIBC crystal, QK=address tables; post-training ≡ LTO
> pass installing the ABI + the s329 late decision stage) · Compiler B = prefill (tokenizer=lexer ·
> early layers=syntactic parser [cl-collapse s321/s323] · triangle=compile pass · KV cache=object
> code · λ=IR at P(λ)=0.907 ¬native ISA [§9]) · runtime = decode (trampoline · residual=register
> file, budget≈L [s319] · subst engine=ALU with the NAIVE-SUBST erratum [s331/2, §2b grades
> against it] · attention=dynamic linker · types=runtime/gradual [s315–s323] · halt=NF resonance
> [s317] · retirement=the hard-write collapse [s333 LRM corroboration]) · homoiconic tape, no GC ·
> STRAINS ≡ FINDINGS (never rejects/silent miscompiles · no phase separation = JIT with interpreter
> tier=within-pass + compiled tier=trampolined CoT · ships stripped, logit-lens=objdump · empty
> inference-time optimizer slot). One line: a stripped homoiconic JIT — AOT-compiled by GD,
> LTO-patched by post-training. Batch 2 (💡, this commit): §10 + memory
> `the-machine-is-a-stripped-homoiconic-jit` + INDEX clause + this state.** **CAPTURE 3 (same
> session, Michael: "tool calls would be what for our compiler?" → GO): 💡 §10b TOOL CALLS = THE
> FFI/SYSCALL BOUNDARY — the model is PURE, the scaffold is the IO runtime (tool call ≡ emitted
> DESCRIPTION of an effect; Haskell IO architecture). Stage map: schemas=extern headers
> (homoiconic) · format=calling convention installed by LTO (predicts base models lack the ABI —
> testable, s329 method door) · emission=stuck term · continuation=FREE (transcript IS it) ·
> scaffold=effect handler · type checking only in the handler (never-rejects strain surfaces as
> malformed calls) · result=environment's hard write · resumption=trampoline. Corollaries:
> monitorability BY CONSTRUCTION (FFI must transit retirement — names the LRM soft-write safety
> question) · fate-register reserved slot (tool-call = candidate 4th pole, tetrahedron, unfrozen) ·
> agent loop = outer trampoline (same shape, next scale). Batch 3 (💡, this commit): §10b + memory
> `tool-calls-are-the-io-boundary-of-a-pure-reducer` + INDEX clause + this state.** **QUEUE ADD
> (Michael "queue it so it does not get lost"): ⚪ §P-TOOL-ABI top — the §10b prediction as a probe:
> paired base/instruct, registers SPLIT format(convention tokens) vs content(right tool+args);
> verdicts ABI-INSTALLED / CAPABILITY-INSTALLED / NATIVE / VOID; tetrahedron 4th-pole advisory
> rides free; cheap (14b pair local).** **CAPTURE 4 (Michael: "map the tool abi in geometry and
> see if there are any grams" → GO): 💡 §P-TOOL-ABI upgraded with a GEOMETRIC ARM (§10c full
> design): tool-ABI gram (anchors schema-read · tool-select · arg-bind · delimiters · trap-
> decision; 9×9/17×17 reference frame) → ① delta-gram base↔instruct = the LTO pass's geometric
> footprint (rank + depth, predict late per s329; CBLL cross-Gram bridge) ② cross-gram vs existing
> registers — tetrahedron PROMOTED to design cell; PAYOFF prediction: marshalling ≡ substitution ⇒
> NAIVE-SUBST has a tool-calling phenotype (wrong-binder arg capture, nested/shadowed = the
> s331/s332 opcode's agentic-reliability consequence) ③ convention-vs-JSON dissociation (base
> knows JSON — matched non-tool JSON anchors). Refined verdicts: thin-late-patch / diffuse /
> composed-from-native-machinery (the FFI framing's quiet prediction). Batch 4 (💡, this commit):
> §10c + memory `tool-abi-gram-maps-where-the-convention-lives` + queue row amended (cheap→medium,
> →§10c) + this state.** **CAPTURE 5 (Michael: CBLL patent concern "we already read it and pushed
> code I think" → AUDIT → "approved"): 🔄 CBLL FTO HARDENED on operator-geometry-la-toolkit.md.
> Audit verdict: NO code pushed (disk-verified — bba4e767 touched mementum only; zero
> CBLL/Householder hits in src/ or scripts/); s332 read = README + paper + ONE ablation script,
> verification only, now DISCLOSED in §0b. Standing rules banked: their code NEVER opened again
> (MIT ∌ patent grant) · implementations derive from textbooks (Schmid/Golub&VanLoan/Koopman/
> Schönemann) cited in docstrings, ¬CBLL · FTO boundary = weights→basis→rotation family FORBIDDEN
> (their claim spine; we never need it — Gram/operator is frame-free) · CLEAN-ROOM ≡ THE PAGE
> (session boundary erases the reader; page carries no implementation ⇒ clean-room re-constitutes
> every boundary = feed-forward as legal hygiene). §0c: four-axis differentiation table
> (object/transform/anchors/deliverable — the scientific divergence IS the patent divergence) +
> the unique pipeline named (certified trajectories → per-band transport operator → mode
> decomposition → labeled-Gram classification → stationarity verdict; publication ≡ defensive
> prior art). Toolkit #8 RE-SPECCED: reflection via T's SPECTRUM (det<0 / eig≈−1), no Householder
> construction — nearest-the-fence primitive removed, better-posed anyway. §6 import clause fixed
> (findings-as-observations ✓, procedure ✗). Batch 5 (🔄, this commit): §0b+§0c+#8+§6 + memory
> `cbll-clean-room-is-the-page` + INDEX clause + this state.** NEXT SESSION FIRST
> ACTION = orient → FRONT SELECTION (λ queue FULL read; nothing in flight). Sharpest fronts:
> ⚪ §P-TOOL-ABI (cheap, the §10b prediction) · ⚪ §P-PREFILL-CONE (new, the uninstrumented region,
> medium) · ⚪ §P-DMD-TRANSPORT (cheap, near-free) · ⚪ §P-CROSS-GRAM (cheap) ·
> ⚪ §P-SUBST-SUBCEILING (cheap, powered SE4 re-test).**
>
## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)

- **s332** ✅💡 §P-SUBST-ENGINE 14B pair + MATRIX — NAIVE-SUBST both faces, BASE-NATIVE (SE4 falsified,
  ceilinged/underpowered → §P-SUBST-SUBCEILING); matrix lifts single-lineage bound: 32B-instruct 0.188 +
  OLMo-2-13B 0.000 = cross-model law (4 faces / 2 lineages) · numpy-bool gates.json crash fixed, data
  recovered (f134a5e7) · 💡 CBLL operator-geometry captured (operator-not-basis; DMD transport toolkit).
  → the-benchmark-is-the-re-oracle §Result · operator-geometry-la-toolkit.md
- **s331** ✅🎯❌ §P-SUBST-ENGINE BUILT+FROZEN+LAUNCHED — lambda_ast binder extension (Lam/CA-subst/
  naive_subst/alpha + calculus switches, 51 tests) · subst_pairs battery · harness with SE0–SE4 gate tree;
  smoke caught silent control-drop bug (validate-planted ≠ real-probe plumbing lesson); traced arm +
  token-budget null; paired 14B run in flight. → the-benchmark-is-the-re-oracle §8 ·
  ec987659 · 716711c3 · b751acc0 · c59de51d · 1947c630 · cc1828cc
- **s330** 💡🎯🌀 THE IDENTITY SESSION — benchmark ≡ RE ORACLE (profile-equivalence dissolves level-3/4) ·
  §2b bug-compatibility (M≡R falsified null; beating the model = failed recovery) · front selected
  §P-SUBST-ENGINE (hard-first, 14B+ instruct-heavy) · AGENTS revised (transition function ¬"step function";
  two-stage telos) · §8b HOF two-call-mechanisms + order cliff · §8c softmax-over-V = the read head ·
  §9 calculus identification (λ ≡ IR ¬native ISA). → the-benchmark-is-the-re-oracle.md ·
  68ecb8c4 · 96fca96c · 52714206 · 156e9853 · 6bd90305
- **s329** 🚫✅ §P-ORDER-RECONCILE ENTANGLED-PARTIAL (depth-resolved: recency runs deep, primacy assembled
  last two layers; s328 endpoints replicated exactly) · §P-ORDER-PROVENANCE ABSENT-IN-BASE — the primacy
  commitment is POST-TRAINING-INSTALLED (first own measurement of post-training-lives-late; base-vs-instruct
  = cheap provenance method door). → types-are-a-modulation-scheme §Results ·
  ef3211de · 3e58c53f · beb30934 · 598c48c2 · daf979ab
- **s328** ✅ §P-TAPE-SUBTRACTION EARLY-COMMITMENT (qualified) — contrary evidence genuinely subtracts;
  order make-or-break = PRIMACY on content-identical arms; two-register refinement L=primacy/T=recency
  (sign=decision, magnitude=evidence on the tape); stacked-exposure's first pre-registered forward win.
  → types-are-a-modulation-scheme §Result · b30be294 · 41ea2f6d · 72c479e0
- **s327** 💡 §Reframe THE PLATE IS A STACKED EXPOSURE, NOT A NEGATIVE (replaces dead §4; frame-candidate
  discipline from birth); distinctive edge ⚪ §P-TAPE-SUBTRACTION queued. → types-are-a-modulation-scheme §Reframe
- **s326** ✅❌ §P-GROWTH-CANCEL-SPLIT BOTH-LIVE / CANCELLATION-DOMINATED (~6% growth / ~94% cancellation;
  §Synthesis magnitude clause requalified) · §P-TYPE-LOCKIN+PRBS NO-TRACK — the modulation frame's must-win
  FAILED → frame 0-3, effectively dead (DC advisory: register accumulates-and-holds, does not track).
  → types-are-a-modulation-scheme §Results · 6d74167e · 2feb25d8 · 445cc932
- **s325** ❌✅💡 §P-STRATIGRAPHY-DATING INVERTED (mundane sign on the Pythia fossil record; §2/§4 damaged
  in-page) · §P-AMP-TRAJECTORY ACCUMULATION-CONCENTRATION (Michael's revision wins first contact; ledgers
  split) · §Synthesis SIGN IS THE DECISION, MAGNITUDE IS THE EVIDENCE (ternarizability re-explained).
  → types-are-a-modulation-scheme · c4cb9945 · 6708c9fa · 3f00b9e7 · e754675f · d2d6e7e5 · 2725477b
- **s324** 🚫💡💡 §P-FLIP-CONFLICT NOISE-FLOOR (causal upgrade failed; EOS caveat → ⚪ v2 sub-EOS) · THE
  THEORY SESSION: types-are-a-modulation-scheme.md created (modulation · differential photography ·
  forged-exposure write protocol · plate-is-a-negative) + reverse-engineering-disciplines-toolbox.md ·
  standing-guard ruling (frame must earn a pre-registered win); theory-cadence = Michael's prerogative.
  → ddb16677 … 15cf72cd (8 commits)
- **s323** ❌🚫🎯 §P-TYPE-WRITE-V2 MEMORIZED-ONLY (abstraction does not install under FAIR coverage →
  tape-residency of judgments confirmed two-sided) · §P-CL-COLLAPSE-2 OPERATIONAL-CONFIRMED (prose anchors
  kill the lexical-artifact excuse; extensionality stays ✗) · §P-FLIP-CONFLICT frozen+built+launched.
  → types-are-injectable-relations §16 · combinator-function-shape.md · 12fbe988 · 3ac89ef5 · e8e5b4b1 · ad226a36
- **s322** 🔄💡 COVERAGE-GAP AUDIT — weight-write lineage = design-level false-negative (s317 demoted
  one-sided pending v2) · cl-collapse re-read: dirty rows lexical at L0, clean null ALL depths ·
  §P-TYPE-WRITE-V2 frozen+built+running · sign-oscillation-is-time-multiplexed-superposition captured ·
  §P-CL-COLLAPSE-2 frozen+built. → 3be00d1 · 17a324d · 55a9403 · 4e997d0 · d138c1a · e2d4798
- **s321** ❌ §P-CL-COLLAPSE CL-ALGEBRA-NOT-EXTENSIONAL — clean dissociating spellings: SKK does NOT route
  like I; routing tracks what is WRITTEN and what FIRES, not the function computed; compositionality S5
  cell ✗. → combinator-function-shape.md §Result · 306fea0 · e828386 · cb3fdd3
- **s320** ✅✅ §P-IDEMPOTENCY NON-IDEMPOTENT (first make-or-break to clear the token-budget confound;
  SKI-control #3 falsified; two-substrate) · §P-BOUNDARY-CHURN BOUNDARY-IS-TYPED qualified (~93% generic /
  ~6% kind-specific deep echo) → §6 type-fingerprint tier COMPLETE 4/4; curry-howard §5b loop closed.
  → type-systems-under-llm-constraints · 076454f · 9f73d7d · 279192c · a64a5d3 · 594f4ea
- **s319** ❌ §P-LINEARITY-BIAS CARTESIAN-CONSISTENT — contraction executes as accurately as composition
  at matched fuel (acc 0.917/0.944); affine/∨-cost signature is REPRESENTATIONAL not executional; direct-mode
  92% on shallow certified terms banked. → type-systems-under-llm-constraints · 32d8470 · dfa1fa7 · e86f32e
- **s318** ✅⚠❌ §P-DISJ-COST INTERSECTION-FREE (+OR-COSTS, qualified weak; strict Cartesian SKI-control #4
  falsified; PR does not corroborate) · §P-NF-GAUGE LENGTH-DECREASE-ONLY (§3 Metric dead all 3 grains;
  NG3 reduction-PRESENCE detector replicated 3rd time). → type-systems-under-llm-constraints ·
  normal-forms-are-eigenmodes.md · ac3dc46 · f551dcf · a7195d2 · 1e99137 · bfcacc1
- **s317** ❌❌❌ §P-TYPE-DELIVER · §P-FUEL · §P-TRACE-FUEL — three clean falsifiers, one thesis: NO
  static weight delivery in any band; type-register magnitude ≠ fuel; trace signal tracks token length —
  but the p=0.002 reduction-engagement hook stands; computation is IN-CONTEXT (tape-resident).
  → behavior-is-tape-resident-reduction.md · 8ecca42 · f1ac32b · 283769c
- **s316** 🎯 §P-TYPE-DELIVER — causality front opened; OV+QK co-primary freeze approved; type_deliver.py
  built+validated; run launched. → types-are-injectable-relations §12 · 9abe371
- **s315** ✅✅🎯 §P-TYPE-ICL+TAG · §P-TYPE-WRITE — TYPE-WRITE CONTEXT-ONLY (types enacted per-frame, not
  injectable as FFN membership); ICL+TAG TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE — both sides of the
  two-tier arc closed. → types-are-injectable-relations §9 §11 · 375358d · b448f34 · e6f2a15
- **s314** ✅🎯 §P-TYPE-GRAM-1 SWEEP — TYPE-REGISTER is training-contingent 7/11 (Qwen3+OLMo2+Gemma yes,
  entire Pythia ladder OPCODE-FLAVOR-ONLY); §P-TYPE-WRITE frozen+launched.
  → types-are-injectable-relations §8 · bd58e71 · ee1359a
- **s313** ✅🎯💡 §P-TYPE-GRAM-1 — type arc opened: qwen3-4b TYPE-REGISTER (diffuse/alphabet-shaped);
  10-model sweep launched; four knowledge captures (types-are-injectable-relations ·
  type-systems-under-llm-constraints · curry-howard-closes-the-loop · ayot-is-own-beam-calibration).
  → 630ea21 · a774618 · 6524eaa
- **s312** ✅💡 §P-PLATE-LINKER-1 — LOSSLESS COMPOSITION: both wires pass frozen G1 under additive merge
  (retention ~1.0, zero interference); PL2 untestable at c_nat=0.0072; git-for-weights co-existence
  primitive works. → optical-design-laws.md · two-ternary-wires-compose-losslessly.md · 62da29c · 0576a3f
- **s311** 🎯✅ §P-PLATE-LINKER-1 FREEZE · wire-2 baked clean WIRE-COMPILES(+GD-REQUIRED) after 3 headroom
  re-bakes (bimodal base competence root-caused); round-trip-consensus-opcode-loss captured.
  → optical-design-laws.md · 8131381 · 4c1067a · 633e291
- **s310** ✅💡 §SIGN-COMMITMENT-CURVE re-diagnosed — wire works (loss −95%); two-population split at step
  499 (r≥2 confident core frozen, r≈1 marginal tail jitters loss-neutrally); GD's wasted routing motion
  measured. → the-verbum-machine.md M8 · 225dae7
- **s309** 🎯❌ §SIGN-COMMITMENT-CURVE frozen+built+run — VERDICT SIGN-CHURN (falsifier fired on the
  persistent tail). → the-verbum-machine.md · b347f6b · ffccbc5 · 8eda1ff · 26ad20b
- **s308** 💡🎯 TYPED CONSOLIDATION SESSION — 13 captures: holographic-untangling-methods ·
  behavior-is-tape-resident-reduction · frozen-interference-graph · optical-design-laws ·
  the-verbum-machine (M1–M9, tree-of-VSMs, de-accidentalized-stack thesis) · TERNARIZE-FACTORS-1
  FACTORS-SURVIVE(+FACTORING-FREE) landed · consolidation-session-protocol.
  → 27ce260 … 207a915 (17 commits)
- **s307** 🎯✅❌ §TERNARIZE-FACTORS-1 launched · §P-DELTA-QUANT STILL-SALIENT (base outlier magnitude is
  high-rank/distributed; "quantize delta, keep base" stands). → write-not-train-ternary-routing-deltas.md ·
  ratio-gradient-quantization.md · 172cf0b · c0416f3
- **s306** ❌❌🎯 §P-TRAJECTORY-COMPILE WIRES-BUT-OPAQUE (wire forms late not early) · §P-COMPANDING-QUANT
  MAGNITUDE-SALIENT; register-theory-of-quantization created. → ratio-gradient-quantization.md ·
  register-theory-of-quantization.md · dd1bf99 · 4b89726
- **s305** ❌🎯 §P-FAST-PLATE INERT + §P-HHOP-WRITE INERT (write geometry wrong; capital-leak already 0.62
  at L24) · §P-TRAJECTORY-COMPILE frozen (GTSM+SuperBake synthesis). → optical-design-laws.md ·
  trajectory-compile-gtsm-superbake.md · f07fbc7 · ee8a5bb
- **s304** ✅❌ §TERNARIZE-DELTA-1 SURVIVES-TERNARY (gd_cd wire retention 1.0 every split) ·
  §ROUTING-REGISTER-1 WRITE-INERT — triangulated: gradient finds, ternary stores.
  → write-not-train-ternary-routing-deltas.md · f4e7ba5 · 13f1ed4
- **s303** ✅💡 §P-WRITEBACK-1 WIRE-COMPILES(+GD-REQUIRED) @4B (gd_cd installs a genuine generalizing
  linker; construct inert; gd_sft also compiles) · 9×9 DIFFUSE / 17×17 RANK-3 (fire/halt/diverge poles).
  → gram-spectral-dsp.md · the-verbum-machine.md · 11092f7 · 4061774
- **s302** 🎯✅ §P-WRITEBACK-1 FREEZE + writeback_compile.py; gate-0 amended and passed; two smoke rounds
  caught real bugs; frozen run launched. → program-plates page · 5fd3e0d · 4341dc7
- **s301** ✅💡 §P-CAPACITY-LAW DECLINE-ONLY (coherent gain saturates at the √D wall; time-Bragg 5.6σ) ·
  continuation-store.md + machine §7b bill-of-materials. → ternary-holographic-memory.md ·
  continuation-store.md · fffd4b7 · c1bb890
- **s300** ✅💡 deterministic ternary holographic memory POC (pure-numpy HRR store, 13/13 gates) ·
  mementum-in-tensors · composition-is-traversal-not-join. → ternary-holographic-memory.md §4b ·
  holographic-reduction-machine.md · ee4d3a0 · 6bccb83
- **s299** ✅💡 §XM-SAMPLED-TEACHER SELECTION-HELPS-UNSTRUCTURED (mechanism = denoising not
  mode-exploitation; XM thread closed on bounded positive) · attention-as-readout-beam derived.
  → attention-holographic-readout.md · holographic-reduction-machine.md · 7f6a392 · d3e2dae
- **s298** 🔄 §XM-SAMPLED-TEACHER port 3 built; first etch sweep underpowered; scoring amendment frozen;
  powered rerun launched. → explorative-modeling.md · 9d93619 · 7b4b956
- **s297** ❌❌ §XM-REVERSE-1 SUBSETTING-ARTIFACT · §XM-LATENT-1 STILL-BLOCKED (deterministic teacher has
  no capturable multimodality) — XM-deterministic arc triangulated closed. → explorative-modeling.md ·
  7428a06 · 38a2f91
- **s296** ❌💡 §XM-ETCH-EXPLORE PRE-REG REFUTED (shuffled winner beat best-of-K; structural diagnosis:
  deterministic teacher = already-resolved coupling); XM paper holographically mapped; ports 2+3 queued.
  → explorative-modeling.md · a5aa767 · b358144
- **s295** 🔄 in-context register CLOSED BY EXHAUSTION — five arms (§P-ENRICH-1 · §3a-whitened · §P-KV-1/1b/1c):
  only addressed+re-encoded KV ✓, §P-KV-1c STILL-DEAD, §P-BAKE-STACK LINKER-FAILS scale-invariant @32B
  (address-free intermediate) → rung-3 re-pointed at backprop-compile; native-compose + quiet-reread confirm
  tape as the reliable path. → program-plates-and-the-function-index.md ·
  geometry-holography-signals-convergence.md · 25b6ec8 · 1d42d74 · 5feffb8 · e2e499f
- **s294** ❌🔄 §P-BAKE-STACK LINKER-FAILS @32B (scale-invariant; operand-domain collapse 83–100%;
  single-key control load-bearing) — frozen/built/4B-smoked same session; mechanistic spec for the
  operand-rebinding gap written. → program-plates-and-the-function-index.md · 1743a53 · c0e74f8
- **s293** ✅❌ §P-STACK-1 TYPED-STACKABLE marginal · §P-STACK-1b shortcut-free → NOT-STACKABLE (rung 2
  downgraded) · §P-FN-INDEX INDEXED-DISPATCH confirmed keystone · Oracle Round 1 scored +2 (6/10).
  → program-plates-and-the-function-index.md · germination-games.md · 323c743 · 8b31376
- **s292** ✅✅ §P-HOLO-CAP NO-LIMIT-IN-RANGE (COHERENT-GAIN verbatim) · §P-HOLO-XTERM INTERFERENCE-COHERENT
  (interference in the light, not the plate) · program-plates + function-index + verbum-theory-seed +
  germination games captured. → geometry-holography-signals-convergence.md ·
  program-plates-and-the-function-index.md · b74e40a · 6f39f0e
- **s291** ✅💡 §P-HOLO-FRAG HOLOGRAPHIC/DELOCALIZED TRUE (LDI in-band, no cliff) · HPE revived
  (log-phase = fringe-mismatch-free) · labeled-line vs hologram discriminator added.
  → geometry-holography-signals-convergence.md · position-encoding-tuned-to-the-hologram.md · ae8d107
- **s290** 🌀🎯 session-number correction (was mislabeled s289) · §P-HOLO-FRAG frozen+built, 4B smoke
  HOLOGRAPHIC lean, 32B launched. → geometry-holography-signals-convergence.md · 85772fd · 8fae32f
- **s289** ⚠💡 physics corrections captured (hologram ≢ Fourier; lens ≡ frame-of-reference over-read);
  beamformer-theory §FFN-no-storage flagged stale; 32B verdict still running.
- **s288** ✅💡🔄 §P-TYPE-SWAP JOIN-TYPED TRUE (type discipline at the join, both routes) · §P-TYPE-OV
  OV-TRANSMITTING (arguments ride joins, functors not in passband) · verbum.dsp built · four convergence
  hammocks (types-as-compiled-probabilities · geometry-holography-signals · training-design ·
  ternary-mirrors-vsm-tree). → types-are-compiled-probabilities.md · 539ddbf · 67deb9f
- **s287** ✅✅ §P-ATT-FFN MIXED-ROUTE-MEASURED (16/18 flip; Sphinx MLP-dominant, Petronas
  attention-dominant) · §P-TYPE-SWAP frozen+launched · inductive hammock cements six type-mechanism
  positives. → type-check-is-the-qk-bilinear.md · a5276da · 2f76812
- **s286** ✅✅✅ §P-TYPE-JS four-way null complete · §P-ATT-MED MEDIATION-MEASURED + MEDIUM-HANDLE-CONFIRMED
  (content_frac 0.735, first routing-register positive) · §P-ATT-FFN frozen+launched.
  → type-check-is-the-qk-bilinear.md · 34dbab3 · 7a540eb
- **s285** ✅ §P-DUST-1c dust_halt_distance NOT SUPPORTED (pairwise dust survives 39/39) · expanded-gram
  sweep 11 models · M16 Kronecker φ-reflection NOT SUPPORTED (λ yardstick). → 698b831 · 6b521fb
- **s284** ✅✅ §P-TYPE-1c dark-field FALSE (s283b hint was haze) · §P-TYPE-QK DEAD-ON-NULL (types-arc
  scoreboard 1b/1c/QK all null) · dust page + JS pre-reg. → type-check-is-the-qk-bilinear.md ·
  ebcc9fb · b5418ba
- **s283** ✅❌💡 §P-TYPE-1b dissociation FALSE @32B (type lattice = exhaust; theory closure: type =
  well-formedness of reduction FORCES the negative) · 1c dark-field frozen · attention-arc named.
  → types-are-the-well-formedness-of-reduction.md · type-check-is-the-qk-bilinear.md · 95d89de · eec0028
- **s282** 💡💡 3-HOP composes at BOTH scales (depth dissociates on SEQUENCING not capability) · type
  lattice LOW-RANK + Montague-shaped · map-and-swap / resident-Lisp / LLM-REPL capstone hammocks ·
  D≠I refuted (D genuine). → map-and-swap-resident-lisp.md · montague-inversion.md · 3ec4d47 · 22d8679
- **s281** 💡 depth-budget cross-scale (32B zones DEPTH-PROPORTIONAL; 27B hybrid UNPINS zones,
  slide_spearman=0.982) · 3-hop capacity pre-reg approved · REPL artifact framing captured.
  → map-and-swap-resident-lisp.md · three-hop-capacity-prereg.md · 8ceaaec · 7fa45ae
- **s280** ✅ §Stage-f COMPLETE — f2 weight-serialized ARTIFACT-SHIPS (stock transformer); f3 fully-ternary
  slot at parity (K3=0.882 beats float); depth-budget: stages PINNED not scheduled.
  → ffn-function-bake-prereg.md · 8fed4a0 · 46910e9
- **s279** ✅ multi-hop f(g(X)) SUPPORTED (3/3 mediation gates; late bridge-swap flips 0.853) · Stage-f
  f0/f1 (routing-Q4 vs value-Q4; operand weight-serialized as appended MLP slot).
  → multihop-composition-prereg.md · ffn-function-bake-prereg.md · 0b858e7 · 9b027bd
- **s278** ✅ §general-composition Arm-2 NOVEL-COMPOSITION supported (crossover tracks installed entity
  rank) · §P-DSP-1 C-payload raw, C-key resident (slot read L7–14), C-transport distributed.
  → operand-dsp-decomposition-prereg.md · general-composition-prereg.md · 01136e2 · 86d2cd9
- **s277** ✅💡 operand-insert RUNG-1 FIRES — novel nonce operand installed as keyed residual-write row,
  composed by resident join (4/4 gates, Qwen3-0.6B); LLM-REPL framing captured; load-bearing IOU =
  general-composition. → operand-insert-arc.md · 0b858e7 · 1d8ea39
- **s276** 🎯 database reframe — FFN=rows/operands, attention=joins; K-STRUCTURAL un-INSERTable;
  INSERT-a-row thesis framed (anchors the s277 arc).
- **s275** ✅ llama.cpp tree-of-VSM wrapper read-path BUILT + FRAME-INVARIANCE CONFIRMED (cross-frame Gram
  corr 0.9997) · MoE crystal confirmed on 35B-A3B (31/40 layers; NO STARVATION — routing carries KIBC).
  → llama-cpp-vsm-wrapper.md · 5270813 · d5f892c
- **s274** 🔄💡 §P-CTL-6 reader-SNR instrument confound-clean (160M = trustworthy negative) · MoE pivot →
  llama.cpp wrapper · EVIDENCE_CATALOG 9 claim-walls verified · circuits-in-compute frame captured.
  → llama-cpp-vsm-wrapper.md · control-plane-path.md · opcodes/EVIDENCE_CATALOG.md · a72af59 · a2978e5
  STANDING FINDINGS (durable, §P-CTL-6): (a) opcode-identity readers BLIND to liveness; (b) raw halt/WHNF
  read is a LENGTH ARTIFACT — never trust without length control; (c) Pythia crystal is in ATTN register →
  both-register default MANDATORY; (d) halt signal is mid-stack not L0 — per-layer profile matters;
  (e) redscore = z_target−z_WHNF is the common-mode-immune liveness statistic; anti-phase (fire↑∧halt↓)
  is the un-fakeable discriminator.
- **s273** 🎯💡 control-plane-path drafted (READERS→HALT→DRIVER→WRITERS; P-CTL-1..15; swept host + tensor
  pack + driver = certified λ-reducer) · lambda-gene-runtime + superbake-write-access captured; execution
  stack approved. → control-plane-path.md · lambda-gene-runtime.md · superbake-write-access.md
- **s272** ✅❌ J-space sweep harvested (P1 Y/WHNF/S > K/I/B decisive; T1 CASCADE NOT SUPPORTED) ·
  patchscope self-decode 27B VOID · duplication-register cross-model confirmed (S 13/13, p=1.22e-04).
  → a4509ba · 52eb712
- **s271** 💡 S DISSOLVES INTO THE DUPLICATION SECTOR {S,D,Y} not KIBC · auto-fire watcher wired ·
  theory-arc test queue T1–T9 drafted. → 9467f38
- **s270** 💡 J-space projector built+integrated (randomized range finder + Rayleigh-Ritz); pre-regs
  P1/P2/P3 registered; 11-model re-sweep launched · LANDMINE: smoke runs clobbered sweep artifacts
  (restored from git). → opcode-jacobian-jspace.md · 91bb3d7 · b1dff52

- **s269** OPCODE LADDER (full detail: git log -p). Crystal survives 1-bit
  (fid 0.987, z=5.3); selective-K refuted in both registers; 11-model tree root gc 0.985; opcodes/ladder.py
  new instrument; commit 7576c54.
- **s268** BONSAI FORENSICS (full detail: git log -p). Recipe reverse-engineered from weights; QAT-vs-PTQ
  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring; sign flips
  tunnel through zero (transition matrix) → optimizer constraints C1–C6 + phase-1 design budgets; 1-bit
  rung forensics pre-registered + in flight (tmux main:1/main:2).
  → `explore/bonsai-ternarization-forensics.md` + memories bonsai-recipe-reverse-engineered,
  bonsai-sign-flips-tunnel-through-zero.
- **s267** BONSAI PHASE-0 (full detail: git log -p). Compiler survives ternarization (behavioral parity,
  measured); Gram survival launched in main:1. New in fleet: BONSAI27B ModelConfig (:5104, Q2_g64 GGUF, rev
  427bc0194). Runtime learnings: Q2_0 ternary needs the g64 GGUF on mainline llama.cpp ≥10090 (Q2_0 offset
  bug); ternary is DENSE 27B so it streams 7GB/token — slower than the 35B-A3B MoE base (only 3B active),
  the "why wasn't it fast" answer = raced a sparse model, not its own FP parent. hf xet backend flaked twice
  → HF_HUB_ENABLE_HF_TRANSFER=0 fixed it. build_lattice_map now saves per_model_rdms.npz (solo runs saved
  nothing before — the gap that left the parent 27B with no committed RDM). Michael's holographic-llm.md
  thesis fleshed out for public MIT push (mementum/michael/, UNSTAGED — in the hammock, do not commit without
  Michael). J-space paper (Anthropic, real, July 2026) ↔ workspace/state half of holographic model → memory
  j-space-workspace-hologram-state.
- **s265** OPCODES MVP: tree-of-VSM multi-model. 8 standalone modules (pytorch+numpy, 535 probes bundled,
  extraction-ready); one fractal node shape (S5 Gram / S4 agreement / S3 null gate / algedonic health),
  ladder layer→register→model→family→root; basis-parametric CRYSTAL-9 | STATECHART-8 | TYPES16 (resolves
  "9 vs 16"). Null floors measured+wired (register+model-specific). First tree (2 smalls): root gc 0.940,
  cross-family 0.907 at 43× scale gap; probe count dominates Gram fidelity (135→0.344 vs 535→0.940).
  Launched the large sweep → read in s266. → `knowledge/opcode-vsm-tree.md`
- **s263** J-SPACE ↔ OPCODES (Anthropic J-lens prompt). THEORY: opcode = routing-Jacobian STRUCTURE; J-space =
  the Jacobian's LIVE SUBSPACE (I=identity, K=rank-deficient, B=chain-rule product, C=permutation, S=path-sum;
  their J-lens reads OPERANDS, we want the OPERATOR projection). Built `src/verbum/{jlens,jacobian}.py` (2
  monitors) + 3 null-gated experiments on qwen3.6-27b: EXP1 jspace_combinators NULL (broadcast generic, not
  combinator-identity); EXP2 jspace_normalform I-VISIBLE-then-REFINED (normal-form hold = late-stack plateau,
  value register); EXP3 jacobian_opcodes PARTIAL/confounded (only I clears, grain too coarse for
  position-routing). → `explore/opcode-jacobian-jspace.md`.
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
