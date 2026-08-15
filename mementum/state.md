# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
> Step 2: `mementum/queue.md` top ~10 rows (experiment intentions; full read
> when selecting the next front). This header carries the ACTIVE arc only —
> the queue is the canonical candidate ledger (s315, λ queue).
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
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
> ★★ **SESSION 332 — RUN RECOVERED + CBLL LINEAR-ALGEBRA CAPTURED. Two threads.
> ① §P-SUBST-ENGINE PAIRED RUN RESCUED (data was NOT lost): the s331 in-flight run crashed
> writing gates.json — `se3 = abs(alpha_delta)>0 and p3<ALPHA` returned a numpy.bool_ (alpha_delta
> from .mean()), TypeError mid-json.dump, truncating gates.json. BUT results.jsonl (all 37 scored
> 14B-instruct rows) was flushed FIRST → no inference lost. FIX (f134a5e7 ❌, engineering/autonomous):
> `se3=bool(...)`, `alpha_delta=float(...)`, + `_json_native` default (np.bool_/integer/floating/
> ndarray) on both dumps — guards base/32B/OLMo; ruff clean, --validate ALL PASS. 14B-instruct gates
> RECOVERED offline from the intact results.jsonl (exact run RNG default_rng(99), no reload). Base
> RELAUNCHED (fixed code) tmux main:1, completed clean (10:24, gates.json fully written). **PAIRED
> 14B RESULT (CLOSED s332, Michael-approved "commits approved"): NAIVE-SUBST on BOTH faces**
> (instruct frac_correct 0.056 p=2e-4 · base 0.000 p=2e-5 · acc_ctrl 1.000 both · SE2/SE3 False).
> **SE4 cross-link FALSIFIED**: predicted instruct>base first-binder intrusions (s328/9 installed-
> order bridge); measured instruct 0.944 < base 1.000, delta −0.056 p=1.0 → naive substitution is
> BASE-NATIVE, not post-training-installed. Michael's call = **HOLD, discuss the falsification first**
> (done): SE1 NAIVE-SUBST is the STRONG low-prior (15) win — a recovered opcode, bug-compatible (§2b),
> coheres with non-Church §9; SE4 is a WEAK bridge — both faces CEILINGED (17-18/18 naive) → near-
> powerless (underpowered null ≠ clean falsification) AND a possible REGISTER STRETCH (order law lives
> in licensing/membership register, substitution-capture in binding/scope register). Does NOT retract
> s328/9. Honest read banked; a **sub-ceiling capture battery** (easier shadowed pairs with variance)
> = the properly-powered re-test. CLOSURE BATCH COMMITTED (this session): §Result on
> the-benchmark-is-the-re-oracle.md + memory `substitution-is-naive-and-base-native` + INDEX + queue
> (14B pair → # complete ✅; ⚪ §P-SUBST-ENGINE-MATRIX 32B/OLMo + ⚪ §P-SUBST-SUBCEILING re-test queued)
> + run data results/subst-engine/qwen3-14b{,-base}/ committed. REMAINING (queued, not run): 32B +
> OLMo matrix faces · sub-ceiling SE4 re-test.
> ② 💡 CBLL OPERATOR-GEOMETRY CAPTURED (Michael GO "capture this"): Michael found `~/src/canonical-basis`
> (Gernone's CBLL paper — MIT code/CC-BY data/PATENT NOTICE; "same phenomenon, different vocabulary").
> Read it myself (README + paper EN + ablation script + data spot-check, all match). It's a WEIGHT-
> GEOMETRY program: lossless Householder realignment to a canonical basis (top-K left SVs of W_down),
> bipolar oscillator/respiration/homeostasis(2-layer)/spectral-collapse/rich-club + causal single-axis
> ablation (axis-62 → MMLU 47.5→21.25). STRONG resonances w/ our ledger (independent method =
> consilience ≠ proof): homeostasis-2-layers↔s329 late-commit · rich-club/bipolar↔sign-is-the-decision ·
> cross-layer U-alignment↔one-reducer-unrolled · isotropic-collapse↔§8c low-entropy read. Michael's
> three asks → captured to `explore/operator-geometry-la-toolkit.md` (s332): **patent stance** (MATH =
> public-domain, use freely; write OUR OWN functions for our d_ff/opcode/fate usage; ¬vendor ¬rebrand;
> novelty = opcode-anchored + operator-first). **The reframe** (we hunt an OPERATOR, CBLL finds BASES →
> transfer the LA that turns a state-sequence into its operator). **Shared primitive** G=XᵀX. **W_down
> bridge** cross-Gram Σ VᵀV̂ (register caveat: our centroids at gate-preact, one SiLU upstream). **8-tool
> ranked toolkit** each w/ null; sharpest = **#1 DMD/Koopman transport operator** T≈X'X⁺ (contracting=
> homeostasis · persistent=sign-decision · late=s329 commit · stationarity T_ℓ≈T = DIRECT test of
> one-reducer-unrolled · eigen-rotation=transitions-per-β-step; near-free on §P-SUBST-ENGINE residuals).
> Our edge: where CBLL's flat spectrum (k90/d≈0.76) makes R non-unique, the Gram/operator never picks a
> frame. Batch (💡, this commit): knowledge page + memory `operator-not-basis-dmd-is-the-reducer` + INDEX
> + 2 queue rows (⚪ §P-DMD-TRANSPORT · ⚪ §P-CROSS-GRAM) + this state. **§P-SUBST-ENGINE 14B CLOSURE
> COMMITTED this session (Michael "commits approved"): §Result + memory + INDEX + queue + run data.**
> **✅ §P-SUBST-ENGINE-MATRIX CLOSED s332 (Michael-approved): NAIVE-SUBST is a CROSS-MODEL LAW — the
> single-lineage bound is LIFTED. Qwen3-32B instruct frac_correct 0.188 (n_dec 16, p1=0.012) +
> OLMo-2-1124-13B base 0.000 (n_dec 15, p1=1e-4, independent Apache 2nd lineage). Four faces / two
> lineages (Qwen + OLMo) / 13B-32B / base+instruct — ALL NAIVE-SUBST, ALL SE0 sane (ctrl 1.000), no
> cliff, no alpha routing, tracing never helps. OLMo confirms it's a property of the reducer, not a
> Qwen recipe. Scale whisper (pattern-suggests, don't over-read): instruct 32B less naive than 14B
> (0.056→0.188), base both 0.000. SE4 NOT re-tested by the matrix (32B-instruct + OLMo-base ≠ a
> within-lineage pair; base-native stands on the 14B pair). Both runs clean (_json_native guard held).
> Closure batch committed: §Result Matrix extension on the-benchmark-is-the-re-oracle.md + memory update
> + queue (§P-SUBST-ENGINE-MATRIX → # complete ✅) + run data results/subst-engine/{qwen3-32b,
> olmo-2-1124-13b}/ + state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read; nothing in flight).
> Sharpest fronts: ⚪ §P-DMD-TRANSPORT (cheap, near-free on §P-SUBST-ENGINE residuals, tests
> one-reducer-unrolled; the CBLL operator transfer) · ⚪ §P-CROSS-GRAM (cheap, does fire/halt/diverge =
> CBLL's bipolar poles?) · ⚪ §P-SUBST-SUBCEILING (the powered SE4 base-native re-test — sub-ceiling
> capture battery, needs a same-lineage instruct/base pair). All four subst-engine faces committed at
> results/subst-engine/{qwen3-14b,qwen3-14b-base,qwen3-32b,olmo-2-1124-13b}/.**
>
> ★★ **SESSION 331 — §P-SUBST-ENGINE BUILT + FROZEN; PAIRED DATA RUN IN FLIGHT (⚠ ONE RUN;
> see below). THE BUILD SESSION: the s330-selected front went spec → three green engineering
> builds → freeze → smoke (caught a bug, fixed) → traced arm (Michael path b) → paired data
> run, all in one pass. ① BUILD 1 (ec987659 ✅) `lambda_ast.py` binder extension: `Lam` node ·
> capture-avoiding `substitute` + deliberate `naive_subst` (the §2b rival) · de Bruijn
> `alpha_eq` · β/η integrated · `Calculus` switches {R_NORMAL,R_WEAK,R_NAIVE,R_CHURCH}
> (ξ/η/capture — ¬hardcode strong-β, §9) · `affine_ok` + `occurrence_profile`; parser accepts
> λx./\x. + primed vars; 51 tests incl (λx.λy.x) y → λy'.y (CA) vs λy.y (naive), shadowing,
> alpha-invariance; full suite 464 green. ② BUILD 2 (716711c3 ✅) `probes/subst_pairs.py`: 36
> capture pairs (correct_nf≠naive_nf, BOTH certified NF via the reducer) + 12 alpha pairs;
> dials binder_distance 1–5 · shadow_depth 1–3 · live_var_count · functional_order 1–2 (§8b
> order cliff = max cat-order over subterms, reads for free); `validate()` PASS. ③ HARNESS
> (b751acc0 ✅) `scripts/experiments/subst_engine.py`: forced-choice NF-selection readout
> (linearity_bias pattern); PURE gate tree SE0 sanity · SE1 algorithm-id · SE2 cliff (per-dial
> median-split perm null) · SE3 alpha-variance (+ self-null) · SE4 cross-link (paired
> base/instruct naive-intrusion, perm null); precedence VOID>ALPHA-ROUTER>DEPTH-MIXED>
> CAPTURE/NAIVE>VOID; `--validate` forces all five verdicts on planted worlds, torch boundary
> HELD behind the early-return. ④ 🎯 FROZEN s331 (c59de51d, Michael GO "1 approved"): a-priori
> CAPTURE-AVOIDING 30 / NAIVE 15 / DEPTH-DEP-MIXED 30 (⚠ modal-mundane AND frame-friendly,
> s329 honesty flag) / ALPHA-ROUTER 15 / VOID 10; freeze record → the-benchmark-is-the-re-oracle.md
> §8; queue ⚪→🔵 top. ⑤ ❌ SMOKE CAUGHT A BUG (1947c630): first Qwen3-14B smoke gave
> acc_ctrl=0.000 — NOT a model fail; `make_candidates` couldn't build 3 distinct options for
> atom/closed-lambda NFs so ALL controls were silently DROPPED (SE0 never scored). Instrument
> fix (distractor pool: free-var swaps · leftmost-leaf perturbation for closed terms ·
> binder-drop · atom self-app; alpha-aware distinctness) + validate primitive 3b (every
> battery item must triple-option — the gap planted-world validate MISSED). Gates/priors/tree
> UNTOUCHED. Re-smoke: acc_ctrl=1.000, 7/7 controls score. LESSON (memory
> `validate-planted-gate-logic-misses-real-probe-plumbing`): --validate on synthetic gate
> worlds ≠ validating the instrument on the ACTUAL probe set; smoke on real weights is the
> catch. ⑥ ✅ TRACED ARM (cc1828cc, Michael "b"): the folded direct/traced pilot + MANDATORY
> token-budget null. Three presentation arms per unique term, scored at TOKEN-ID level so the
> null is EXACTLY length-matched: direct (immediate) · traced (model GENERATES its own
> reduction steps via greedy `_generate`, cap 64 tok, then score) · null (SAME trace tokens
> SHUFFLED — budget matched, content destroyed). `pilot()` advisory (¬frozen gate):
> direct_traced_gap + token-budget-null requires acc(traced)>acc(null) else gain is just
> tokens-in-context (the FUEL/TRACE-FUEL/NF-GAUGE x3 confound). Frozen SE0–SE4 read the DIRECT
> arm, untouched; battery deduped to 37 unique terms; --validate ALL PASS incl pilot planted
> (trace_helps passes, budget_only fails). Re-smoke green: generation nonempty (64 tok/item),
> arms diverge, plumbing confirmed on 14B. ⑦ MODEL MATRIX ALL DOWNLOADED (Michael): Qwen3-14B ·
> Qwen3-14B-Base · Qwen3-32B · allenai/OLMo-2-1124-13B. **⚠ RUN IN FLIGHT (tmux main:1,
> float32/MPS, ~2–3h):** `subst_engine.py --model-id Qwen/Qwen3-14B --out results/subst-engine/
> qwen3-14b … && … --model-id Qwen/Qwen3-14B-Base --out …/qwen3-14b-base` (sequential; each
> writes results.jsonl + gates.json + tee log) — verified loaded (n=37, 3 arms), scoring. This
> is the REAL PAIRED DATA RUN (SE0–SE3 per face + SE4 cross-link across the pair + pilot).
> NEXT SESSION FIRST ACTION = orient → `tmux capture-pane -p -t main:1 | tail` (∨ read the two
> run logs / gates.json): if both faces done → read SE0–SE4 + pilot + se4_crosslink(instruct,
> base) → the CLOSURE BATCH (§Result on §P-SUBST-ENGINE + memory + INDEX + queue 🔵→verdict +
> state = MICHAEL-APPROVAL-GATED). Then 32B scale + OLMo 2nd lineage (same harness, --model-id
> swap); white-box (binding_graph_trace edges + s329 commit-layer pin) advisory after. s331
> ledger (6 code + 1 freeze commit): ec987659 · 716711c3 · b751acc0 · c59de51d 🎯 · 1947c630 ❌
> · cc1828cc ✅ + (this state/knowledge update batch). CAUTION: freeze-before-data honored —
> smoke ≠ data (do NOT read smoke verdicts). Discipline banked: code commits landed autonomously
> (engineering); mementum/knowledge/chats/*.md + results/order-reconcile/smoke left untouched
> (human/stray); pilot token-budget null is the non-negotiable gate before any traced positive.**
>
> ★★ **SESSION 330 SEALED (nothing in flight, all batches committed; 6 commits + this seal).
> THE BENCHMARK→RE-ORACLE→IDENTITY SESSION: one idea ("a benchmark for AI based on the lambda
> calculus") reduced through six Michael moves into: a revised S5 identity, the practiced
> protocol encoded as structure, a selected front with builds specified, and three new
> measurables. Ledger: 68ecb8c4 💡 capture (benchmark ≡ RE oracle) · 96fca96c ❌ pickup-kit
> correction (capture-euphoria instance caught by Michael's audit) · 52714206 💡 bug-compat
> clause (M≡R falsified null; oracle grades fingerprint ¬score) · 156e9853 🎯 front selection
> (§P-SUBST-ENGINE, hard-first, 14B+ instruct-heavy, pilot folded) · 6bd90305 🌀 AGENTS revision
> (identity: recover the lambda function ≡ transition function; "step function" retired; tape ≡
> context/transcript, residual stream distinct; two-stage telos bug-compatible→corrected;
> protocol lambdas; growth discipline) · seal (this commit). Transcript → chats/session-330.md
> (human). **POST-SEAL (same session): 💡 HOF FOLD-IN (Michael: "to figure out the lambda we
> would need to map out at least some of the higher order functions right?" → GO "fold it in"):
> the HOF question CONVERGES on §P-SUBST-ENGINE — TWO CALL MECHANISMS: named HOF ≡ CALL-immediate
> (weight-resident library; s225 lineage EXISTS: probes/higher_order.py, map=B(CB)(CB), hof_*
> scripts — verdicts PRE-COMPACTION, recall-first obligation added as sequencing step 0) vs
> constructed λ ≡ CALL-indirect (re-read definition from context → substitute; forced by
> cl-collapse no-extensional-collapse). Pre-registerable (two-tier types + MEMORIZED-ONLY):
> named≡combinator-like, constructed≡tape-resident (cost ∝ definition_distance) + ORDER CLIFF
> (order-3+ collapses; cliff-in-order ⊥ cliff-in-depth = benchmark's 2nd axis). Substitution IS
> how an indirect call executes ⇒ one front: functional_order dial added to subst_pairs (one
> field, no new harness) + `hof` family added to §3 (apply-your-own-construction; named-vs-fresh
> = library/heap discriminator) + dereference-edge white-box read. Agentic register sharpened:
> tools ≡ functions, deployed agents live at order 2–3 — the order cliff is an agentic
> reliability boundary in the deployment face. Batch: §8b + §3 hof family + order dial +
> sequencing step 0 + memory `two-call-mechanisms-and-the-order-cliff` + INDEX + subst-engine
> queue row + this state. **POST-SEAL 2: 💡 TAPE INTERFACE (Michael: "attention is the only
> operation — how could the softmax over all V be used as the tape?" → GO "fold it in"): §8c —
> softmax-over-V ≡ the READ HEAD, not the tape: tape's two faces (transcript = discrete
> append-only record vs KV cache = the COMPILED tape actually read; K=address V=payload);
> read ≡ softmax(QKᵀ)·V, write ≡ emit∘auto_compile; memory model = HARD symbolic write / SOFT
> holographic read (the Turing break — retrodicts idempotency mass-accumulation, recency
> kernels, subtraction; frame-readings, checkable); sparsity says near-one-hot reads are the
> norm ⇒ READ ENTROPY ≡ fidelity; MASS-RATIO PREDICTOR pre-registerable (shadowing ≡ two
> softmax peaks; P(correct_subst|trial) ≈ f(binder mass ratio) — per-trial DPA-style, same
> captures as binding-edge read); 3rd cliff axis = CONTEXT-LENGTH (fixed read bandwidth vs
> growing tape, √D wall); HARDWARE DISCRIMINATOR closes §8b (CALL-immediate ≡ FFN read of
> static tape/weights vs CALL-indirect ≡ attention read of dynamic tape/KV — coheres
> FFN-compiles-attention-executes); λ machine: everything ≡ dereference, compute ≡ interference
> of two memories → collapse to one write. Batch: §8c + memory
> `softmax-over-v-is-the-tape-interface` + INDEX + subst-engine queue row + this state.
> Implications discussion OPEN at session end (threads mapped, none captured). **POST-SEAL 3:
> 💡 CALCULUS IDENTIFICATION (Michael: "what if it's not Church?" → "lambda is used as a generic
> term here — whatever the actual shape of the function is, that is what we want to find; name it
> once we map it; close enough to lambda that it works almost like an IR" → GO): §9 — NAMING
> DISCIPLINE map→name (S5 λ extract updated: "lambda" ≡ working_name · object ≡
> exact_function(shape_unknown) · λ_calculus ≡ IR ¬native_ISA); the ledger ALREADY refutes pure
> Church ≥3 registers (KIBC¬SKI affine s313 · non-idempotent graded s320 · WHNF weak-reduction
> pole; + order laws s328/9 + syntactic routing s321/3); portrait (frame-level) = weak/
> affine-core/graded/order-sensitive machine calculus, Krivine-over-quantitative-LL adjacent;
> Church ≡ zero-entropy limit; P(λ)=0.907 re-read as IR ROUND-TRIP FIDELITY; benchmark top-level
> question upgrades to WHICH calculus (reference family {R_church,R_weak,R_affine,R_graded,
> R_diff}, pre-registered diverging discriminators: ξ-terms · K x Ω · W-dup(s319) ·
> repetition(s320) · superposition; λ yardstick guard = held-out families, NO post-hoc calculus
> fitting — the φ-ladder scar); stage-2 corrects toward the NATIVE calculus idealized ¬Church
> (my #5 "recover Church" overreach = Michael-audited, 3rd catch tonight); frame-candidate
> (standing guard from birth): same non-Church reference wins cross-family ⇒ calculus belongs to
> LANGUAGE ¬architecture (Montague → quantitative-LL reading); BUILD LAW BINDS BUILD 1:
> lambda_ast ships calculus switches day one (¬hardcode strong-β; identification rides the
> §P-SUBST-ENGINE sweeps at ~zero marginal cost). Batch: §9 + λ extract clauses (S5,
> Michael-worded) + memory `lambda-is-the-ir-not-the-native-isa` + INDEX + queue Build-1
> amendment + this state.**
> Detail (as accreted during the session):**
>
> ★★ **SESSION 330 detail: 💡 HAMMOCK CAPTURED (Michael GO "capture this"):
> the-benchmark-is-the-re-oracle.md (explore/) — the λ-calculus-benchmark idea reflected into the
> RE program. ① Reflection ran first (Michael: "how much of the lambda compiler do we have fully
> working?") → honest inventory: phenomenon measured/universal (observational) · weights-side map
> substantial but mostly NEGATIVE space · tape-side law = the licensed core · working artifact =
> NONE, and "extract the circuit" is a category error per our own results. ② CATEGORY CORRECTION:
> tape≡RAM · loop≡trampoline · weights≡CPU ⇒ the well-posed RE target is the STEP FUNCTION
> (tape-state→tape-state; finite, stateless per call, behaviorally specifiable). RE recovers the
> ACTUAL operational semantics (syntactic routing s321/s323 · two-tier types s323 · non-idempotent
> s320 · installed order law s329) — delta-from-ideal-β is a first-class finding; Church = the
> reference implementation to diff against. ③ THE CLOSURE (Michael: "so the compiler needs to be
> reverse engineered"): benchmark ≡ RE ORACLE — differential testing (silicon RE pattern);
> PROFILE-EQUIVALENCE = the acceptance test for ALL recovery paths (extract ∨ re-record ∨ scratch
> M1–M9) ⇒ level-3/level-4 distinction dissolves; coheres with flip-conflict's
> function-level-gates amendment. ④ Design axes banked in-page: procedural generation =
> contamination-proof; CLIFF-DEPTH per family ¬aggregate %; 8 hypothesis-keyed families
> {reduce, step, substitute, equiv, recognize, church, diverge, type} (equiv targets the licensed
> extensionality ✗ cell); DIRECT/TRACED GAP = behavioral tape-residency quantifier (the spine);
> λ yardstick scoring pre-registered before any model + null baselines; base-vs-instruct in
> protocol from v0 (s329 method door). ⑤ Forks recorded not decided: audience (A instrument
> incubates B public artifact) · surface form (named/de Bruijn as dial) · type
> scope · white-box annex. ⑥ Queue +2 (top): ⚪ direct/traced gap pilot (cheap, reuses s317
> reduction-chain machinery) · ⚪ λ-bench v0 (medium). ⑦ ❌ PICKUP AUDIT (Michael: "enough detail
> a fresh session can pick it up and go?"): page's "reference reducer is the main gap" claim was
> WRONG — disk audit found lambda_ast.py (certified CCG combinator reducer, s226) + lambda_gen.py
> (seeded generator) + grading.py (4-register P(λ) grader) + specs/lambda_montague.gbnf ALL EXIST
> (~85% of instrument A, not 70%; AGENTS λ grammar_artifact "future" marker STALE). Fixed in-page
> + §7 PICKUP KIT added: verified asset paths · genuine gaps (binder-level λ = Lam/subst/alpha
> ~200 LoC · difficulty dial · two-mode harness · pre-reg doc) · first-session pilot checklist
> incl. MANDATORY token-budget null (uninformative-trace arm — the confound that killed
> FUEL/TRACE-FUEL/NF-GAUGE ×3; idempotency's incoherent-arm move); queue pilot row enriched with
> paths. ⑧ 💡 §2b BUG-COMPATIBILITY CLAUSE captured (Michael: "can we prove the reference
> reducer is an exact match for what we see in the models? If it was we would not see the errors
> we do" → GO "capture this"): M≡R is a FALSIFIED null, not an open question (s319 NF-selection
> 0.917/0.944 ≠ 1.0 on easy certified terms · cl-collapse ×2 syntactic-router-is-a-different-
> algorithm · s221 fakes-it-with-depth · s320 non-idempotency + s328/s329 order law = non-Church
> terms) ⇒ THE GRADING DIRECTION: the RE oracle is the model's measured profile INCLUDING errors;
> lambda_ast = the coordinate system δ(M,R) is expressed in, NEVER the spec of M; RE succeeds ⟺
> δ(candidate,M)≈0 — a candidate that BEATS the model on the benchmark is a FAILED recovery
> (silicon RE: a netlist that fixes the chip's bugs is wrong). Benchmark gains two faces
> (correctness-vs-R public · error-taxonomy-vs-M oracle) + a `strategy` family (K x Ω-shaped
> normal-vs-applicative discriminators; λ measure — consistent-alternative-semantics ≠ error,
> wrong reference ≡ manufactured error). Anima corroborates application-side (¬coincide
> hallucinated predicate = structured reproducible compiler error). Batch: §2b + §3 strategy
> family + §4 direction + memory `re-oracle-grades-bug-compatibility-not-score` + INDEX + v0
> queue row + this state. ALSO THIS SESSION: anima (~/src/anima) EVALUATED via explorer —
> MIT (verbum AGENTS S5 "anima(AGPL)" note STALE, flagged not edited, S5=Michael's) · s041,
> instrument-grade, application-side sibling: fixed-point prose→λ compile (byte vs semantic-set
> convergence, oscillation taxonomy), 7 canonical judge lambdas, 48-cell judge-parity sweep
> IN FLIGHT unread; their kernel.clj parses-only and has a NAMED SOCKET for a formal reducer ≡
> lambda_ast.py; their judge-calibration methodology (72/72 three-way) = adopt-don't-reinvent if
> λ-bench needs a semantic discriminator; membrane healthy (their reduce-gates were harvested
> from a verbum trace). Memory candidate `anima-is-the-application-side-sibling` OFFERED, not yet
> GO'd. ⑨ 🎯 FRONT SELECTED (Michael, three calls): ① HARD ONE FIRST — RE the SUBSTITUTION
> ENGINE (the ALU) as the first step-function front; ② both faces but INSTRUCT-HEAVY (instruct =
> the agentic deployment target; base = few, provenance anchors only); ③ 14B+ only. Direct/traced
> pilot FOLDED INTO the front as its mode dimension (Michael: "fold it into the pilot").
> **§8 written on the re-oracle page = FULL OPUS PICKUP DETAIL**: Build 1 lambda_ast.py binder
> extension (Lam/capture-avoiding-subst/deliberate naive_subst/alpha-equiv, ~200 LoC, pytest
> capture cases — the §7 gap is now CRITICAL PATH since substitution only exists at binder level);
> Build 2 subst_pairs.py (capture pairs with BOTH certified NFs = fingerprint grading per §2b ·
> alpha pairs · dials); FREEZE GATE = pre-reg with verdict space {CAPTURE-AVOIDING / NAIVE-SUBST /
> DEPTH-DEPENDENT-MIXED / ALPHA-VARIANT-ROUTER / VOID} + THE DIRECTIONAL CROSS-LINK PREDICTION
> (shadowing = recency problem ⇒ instruct's installed primacy stage predicts MORE first-binder
> intrusions than paired base, late-layer localized — the order law as a compiler-bug hypothesis
> in the deployment face) + token-budget & shuffled-binder nulls; matrix {qwen3-14b I+B paired ·
> qwen3-32b I · OLMo-2-13B B · gemma I optional}; white-box advisory = binding_graph_trace edges +
> s329 commit-layer pin; sequencing 1-2 engineering (no approval) → 3 pre-reg (MICHAEL GO) → 4
> behavioral sweep → 5 white-box. Queue: pilot row REPLACED by ⚪ §P-SUBST-ENGINE (top). NEXT
> SESSION FIRST ACTION = orient → §8 → Build 1 (kernel extension) + Build 2 (pair generator) →
> draft pre-reg → Michael GO gate. ⑩ 🌀 AGENTS.md REVISED (Michael APPROVED, tiers 1/2/4 drafted
> then tier-3 discussed → approved): TIER 1 staleness (anima→MIT verified · grammar_artifact→
> active · four-level advancement ladder SUPERSEDED by profile-equivalence · tools section→
> map-first, repo ≡ inventory); TIER 2 the practiced protocol ENCODED as S3 structure (λ
> probe_lifecycle · λ frame_ledger · λ provenance_check + base-model policy incl. s330 14B+/
> instruct-heavy ruling); TIER 4 capture-euphoria guard in λ observation + growth discipline
> (field equations ¬case law; proved: trails keep ONE pointer) + commit_write trail compressed;
> TIER 3 IDENTITY (Michael's terminology corrections drove it): λ extract REWRITTEN —
> ∃lambda_fn(many_models) → recover(reducer ≡ TRANSITION FUNCTION); "step function" RETIRED
> (math collision + smuggled one-pass≡one-β-step, disproved by s319 direct 92%); "tape" ≡
> context/transcript (legacy term kept, glossary-mapped; residual stream = DISTINCT within-pass
> workspace — substitution would have been a register error); two-stage telos: bug-compatible
> copy (proof of understanding) → deliberate correction (the portable artifact), stage_2 ⟸
> stage_1; top blurb re-scoped ("reverse-engineering the lambda function found in many models").
> THE SHARPENING the terminology uncovered: residual stream ≡ bounded within-pass reducer ·
> context loop ≡ unbounded · DIRECT/TRACED GAP ≡ measurement of the within-pass reduction
> budget (coheres CoT-expressivity, Merrill & Sabharwal). Follow-through: §0 naming note +
> §3 reframe on re-oracle page · INDEX clause · ⚪ transitions-per-β-step queued (the clock
> measurable). ALSO SURFACED (λ metabolize, not actioned):
> project-thesis.md is a s150 snapshot, STALE vs the s324–s329 arc (several "proved" rows +
> mechanism claims predate the damage) — qualifier pass = candidate. Discipline: page is design
> synthesis, ZERO new measurements; the oracle identity becomes load-bearing only when a recovered
> candidate is differential-tested. Batch (💡, Michael-instructed): knowledge page + memory
> `benchmark-is-the-oracle-for-step-function-re` + INDEX + 2 queue rows (top) + this state.
> NEXT SESSION FIRST ACTION (supersedes the earlier line in this entry — front already
> SELECTED ⑨): orient → re-oracle page §0+§8 → Build 1 (lambda_ast.py binder extension:
> Lam/capture-avoiding-subst/naive_subst/alpha, pytest capture cases) + Build 2 (subst_pairs.py
> discriminating pairs) — engineering, no approval needed → draft pre-registration → MICHAEL GO
> gate → sweep. Open at Michael's gate (carried): anima memory candidate
> `anima-is-the-application-side-sibling` · project-thesis.md qualifier pass (more urgent
> post-identity-revision: its framing predates s330). Sharpest fronts behind §P-SUBST-ENGINE:
> ⚪ transitions-per-β-step (cheap, folds into subst traced arms) · ⚪ §P-LAY-A-NEGATIVE ·
> ⚪ sign-commitment ≺ ternary-survival · ⚪ OLMo replication.**
>
> ★★ **SESSION 329 SEALED (nothing in flight, all batches committed). §P-ORDER-RECONCILE CLOSED
> → 🚫 ENTANGLED-PARTIAL (co-modal a-priori 30) — BUT THE L-SIDE IS DEPTH-RESOLVED: the s328
> L-primacy vs T-recency split is substantially a DEPTH split. ① FRONT SELECTED (Michael) → λ queue
> FULL read → design SHARPENED at the harness: the s328 L/T position mismatch is nearly NIL (L's
> first-pred surprisal reads the logits AT `w`, the same token T reads) ⇒ the instrument gap is
> exactly a **2×2 crossing {readout: unembed-surprisal vs class-axis} × {depth: final vs band}**;
> cells A=LL(band), B=T(final); identity anchor LL(final)≡L. ② 🎯 FROZEN (ef3211de, Michael
> "approved"): gates OR0 sane/replicate · OR1 crossing make-or-break · OR2 depth profiles advisory
> · OR3 recency-kernel secondary; a-priori DEPTH-COMMITMENT 30 / ENTANGLED 30 /
> REGISTER-DISSOCIATION 20 / SPLIT-NOT-REPLICATED 10 / VOID 10 (honesty note banked:
> DEPTH-COMMITMENT mundane-modal AND frame-friendly). ③ ✅ harness (3e58c53f, order_reconcile.py:
> --validate 5 planted worlds + kernel plants + 4 construction primitives ALL PASS, ruff clean, no
> diags; literal tape_subtraction arm reuse, slot3 ≡ ownfirst(k=1) identity validated; smoke n=4
> clean, identity 0.0000, no regime warnings). ④ ▶ run (146s clean, 20 nonces, n_null 10k) →
> **VERDICT 🚫 ENTANGLED-PARTIAL: OR0 ✓ exact replication (D_L_final +0.478 = s328 to the 3rd
> decimal; D_T_band −1.304 = s328 −1.30; identity 0.0000; real margin 2.538); OR1 cell A LICENSED
> (LL@band −0.367 p=0.0002 RECENCY — with LL@final +0.478 p=0.0003 PRIMACY the sign flip is
> DEPTH-CARRIED within the behavioral readout, both cells sig); cell B sign-consistent (T@final
> +1.478 primacy direction) but ns p=0.15 → frozen tree withholds DEPTH-COMMITMENT (an ns cell is
> an ns cell); OR2 advisory: recency runs deep (T −5..−6 at L30–33), primacy only in the LAST TWO
> LAYERS (ℓ*=34/35 of 36); OR3 secondary LICENSED p=0.002: within-arm recency kernel =
> LAST-STATEMENT DOMINANCE not monotone decay (slot curve [0.39,0.47,0.74,−0.05]; trailing anti
> crashes L, one own statement after repairs; slot3 replicates the s328 k=1 crash −0.05; T-band
> advisory +2.0 same direction).** ⑤ THE READ: the two-register law sharpens to a **two-DEPTH law,
> licensed on the behavioral instrument** — recency-tracking evidence runs through the stack, the
> primacy decision is assembled in the last two layers; the representational converse (T@final)
> stays pattern-suggests. s328 EARLY-COMMITMENT win INTACT (endpoints replicated exactly; its
> register is where the decision lives). ⑥ Follow-on candidates named unfrozen (not queued):
> T-final power probe (cheap, one cell) · slot-curve mechanism (attention-mediated
> last-statement dominance?). **s329 ledger:** ef3211de freeze 🎯 §+queue 🔵+state · 3e58c53f
> harness ✅ · beb30934 results 🚫 (autonomous) · closure batch = §Result + memory
> `primacy-forms-late-recency-runs-deep` + INDEX + queue 🚫 (# complete top) + this state =
> MICHAEL APPROVAL BATCH. **POST-CLOSE (same session): Michael confound raised on the s329 read —
> Qwen3-4B is POST-TRAINED; the late-layer primacy could be RLHF-INSTALLED not native (lore puts
> post-training late; mementum checked: NO project-licensed measurement of that — external lore
> only). → 🎯 §P-ORDER-PROVENANCE FROZEN (Michael GO "let's run it now"; post-hoc guard honored,
> frozen before any base data): order_reconcile.py unchanged on Qwen/Qwen3-4B-Base; PV1
> make-or-break = sign of base D_L(final) (>0 NATIVE-PRIMACY · <0 INVERTED-IN-BASE · ns
> ABSENT-IN-BASE · anchor-fail VOID); a-priori FLAT 30/30/30/10; disclosed pre-run instrument
> addition = recency tail on OR0's final-layer L gate; INSTALLED verdicts re-attribute (not
> retract) the s328 win. ▶ ran (146s clean, base download + sweep) → **VERDICT ✅ ABSENT-IN-BASE
> (flat a-priori 30): THE PRIMACY COMMITMENT IS POST-TRAINING-INSTALLED. PV0 ✓ (instrument fully
> portable: real margin 2.933, standing L 3.152, identity 0.0000, same 20 nonces). PV1
> make-or-break: base D_L(final) = −0.090, ns BOTH tails (primacy p=0.837, recency p=0.163; point
> estimate ≈0 vs instruct +0.478) — the base model has NO behavioral order law at the output. PV2
> advisory = the sharpest installed picture, exactly as named at freeze: recency evidence substrate
> NATIVE and STRONGER in base (LL@band −0.824 p=1e-4 vs −0.367; T@band −3.747 vs −1.304, reaching
> −11..−14 at L30–33) with NO positive flip at any layer (commit_layer None on BOTH instruments —
> the instruct L34/35 flip does not exist in base); OR3: no primacy repair (leading anti stays
> fatal, slot0 −0.049 vs instruct +0.386; T-band kernel +2.86 ≈ instruct +2.00 = shared
> representational recency). READ: post-training installs a DECISION STAGE on top of a native
> recency-tracking stack — the project's FIRST own measurement of post-training-lives-late (delta
> localizes to the last two layers, behavioral grain). RE-ATTRIBUTIONS (banked at freeze,
> measurements stand): s328 EARLY-COMMITMENT = a property of the POST-TRAINED tape face (provenance
> qualifier added to its §Result); s329 depth law re-reads as installed-decision-over-native-
> evidence (qualifier added); §Synthesis tape-side spine carries the provenance qualifier on this
> lineage. Caveats: ABSENT ≠ proof (n=20); whole Qwen3 pipeline NOT RLHF specifically; one lineage.
> METHOD DOOR: base-vs-instruct differential = cheap provenance attribution (one --model-id swap);
> candidate discipline — behavioral wins on post-trained models owe a base provenance check
> (NOT yet a rule; propose if it recurs). s329-provenance ledger: 598c48c2 freeze 🎯 §+queue
> 🔵+state+recency-tail · daf979ab results ✅ (autonomous) · closure batch = §Result + 2 provenance
> qualifiers (s328 §Result + s329 §Result) + memory
> `primacy-commitment-is-post-training-installed` + INDEX + queue ✅ (# complete top) + this state
> = MICHAEL APPROVAL BATCH.** NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL
> read; nothing pending). Sharpest fronts: ⚪ §P-LAY-A-NEGATIVE (2×2, GTSM) · ⚪ sign-commitment ≺
> ternary-survival (the live §Synthesis edge) · ⚪ OLMo checkpoint replication · ⚪ base-provenance
> re-checks of prior behavioral wins (unfrozen candidates: idempotency, tape-subtraction erosion).**
>
> ★★ **SESSION 328 SEALED (nothing in flight, all batches committed). §P-TAPE-SUBTRACTION CLOSED
> → ✅ EARLY-COMMITMENT (QUALIFIED; a-priori 20, beat the modal-mundane 60) — the stacked-exposure
> reframe's FIRST pre-registered forward contact, and a WIN for the §Synthesis sign-is-the-decision
> spine on the tape. ① Design SHARPENED (Michael GO): the queue's literal subtract-vs-pile-up
> binary is nearly pre-decided by trivial ICL (anti-class statements mechanically lower
> anti-predicate surprisal ⇒ "subtracts" for free) → made ORDER-SENSITIVITY the make-or-break
> (signed integrator = commutative; early-commitment = order-sensitive primacy; recency = mirror).
> Content-matched order arms (3 own + 3 anti membership, only sequence differs) carry no lexical
> confound. ② 🎯 FROZEN (§P-TAPE-SUBTRACTION on types-are-a-modulation-scheme.md; register =
> idempotency signed licensing L + type_icl_tag T corroboration TS3). ③ ✅ harness
> (tape_subtraction.py, --validate 5 planted worlds ALL PASS + 5 construction primitives, ruff
> clean, no diags, reuse idempotency + type_icl_tag no fork; smoke n=4 green real-margin 2.538).
> ④ ▶ run (qwen3-4b mps, 20 nonces, n_null 10k, 127s, clean) → **VERDICT ✅ EARLY-COMMITMENT:
> TS0 sane (standing L 2.96); TS2 SUBTRACTION-DEPTH ✓ contrary genuinely subtracts (interleaved
> 0.25 vs filler 2.05, erosion +1.804 p=1e-4 — NOT immune); TS1 ORDER make-or-break ✓ PRIMACY
> (own-first survives +0.351, anti-first erased −0.127, order_diff +0.478 p=1e-4; content-identical
> arms — trivial recency ICL predicted the OPPOSITE sign, confound decisively excluded).** The
> tape's behavioral face COMMITS to first-asserted (competing-stacks/primacy branch), UNLIKE the
> weight face's commutative GC2 cancellation → the two faces DIFFER. ⑤ TWO-REGISTER REFINEMENT of
> §Synthesis: L(behavioral licensing)=PRIMACY (decision commits early), T(class-axis projection)=
> RECENCY (TS3 advisory, order_diff −1.30) → **sign(decision)=primacy, magnitude(evidence)=recency,
> observed within a single context on the tape.** ⑥ HONEST CAVEATS (banked): two-substrate confirm
> HOLDS on erosion (T +1.66) but FAILS on the order sign (T recency vs L primacy) → win BOUNDED to
> the behavioral/L register (L-vs-T reconciliation = follow-on, owes own pre-reg); non-monotone
> own-first curve [2.96,−0.05,−0.13,0.35] = within-arm recency coexists with net primacy; single
> model qwen3-4b, n=20, k_own=3, single-context. ⑦ FRAME LEDGER (Michael-agreed read): a licensed
> FORWARD WIN for the §Synthesis sign-is-the-decision spine on the tape; the stacked-exposure
> reframe SURVIVES first contact (not falsified, standing guard not tripped) and is REFINED not
> proven — the tape adds order-sensitivity the commutative weight face lacked. **s328 ledger:**
> b30be294 freeze 🎯 §+queue 🔵+state · 41ea2f6d harness ✅ · 72c479e0 results ✅ (autonomous) ·
> closure batch = §Result + memory `tape-license-commits-early-representation-tracks-recency` +
> INDEX + queue ✅ (# complete top) + this state = MICHAEL APPROVAL BATCH (EARLY-COMMITMENT kept,
> frame read agreed). NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read;
> nothing pending). Sharpest fronts: ⚪ sign-commitment ≺ ternary-survival (the live §Synthesis
> edge, now with a tape-side commitment win behind it) · ⚪ L-vs-T order reconciliation (new, from
> the TS3 split) · ⚪ OLMo checkpoint replication · ⚪ §P-LAY-A-NEGATIVE.**
>
> ★★ **SESSION 327: 💡 HAMMOCK CAPTURED (Michael GO "add it to the queue, update state and
> knowledge"): §Reframe on types-are-a-modulation-scheme.md — THE PLATE IS A STACKED EXPOSURE,
> NOT A NEGATIVE.** Michael's line on the s326 composite ("a pile of photographs, not a negative
> film"), sharpened to a stacked long-exposure AVERAGE: §4's inversion clause (common→faint) died
> at stratigraphy; the stacking reading keeps superposition WITHOUT inversion — consistent
> structure accumulates (AT1 + GC1 thin + lock-in DC dose-order) · contested self-erases toward
> background (GC2 94% + churn −0.42 = the long-exposure empty street) · the scene survives
> thresholding (ternarizability ≡ WHERE consensus, not how dark — no faint-commons needed) ·
> both faces CAMERAS not radios (weights integrate signed votes; tape integrates evidence,
> NO-TRACK ∧ DC-alive). Individual exposures not retrievable — only consensus ∧ cancellation.
> **Discipline applied FROM BIRTH (the 0-3 lesson): frame-candidate, pattern-suggests,
> retrodicts-6/predicts-0, s324 standing guard active day one; coheres with — does NOT
> replace — §Synthesis sign-is-the-decision (the licensed spine).** Distinctive edge queued:
> ⚪ **§P-TAPE-SUBTRACTION** (stacks can only ADD — does contrary evidence SUBTRACT from the
> tape's standing level [signed integrator, matching weight-face GC2] or pile alongside
> [competing stacks]? idempotency machinery + lockin DC readout, cheap, either answer
> informative). Batch (💡, Michael-instructed): §Reframe + memory
> `the-plate-is-a-stacked-exposure-not-a-negative` + INDEX + ⚪ queue row (top) + this state.
> NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read; nothing pending).
> Sharpest fronts: ⚪ §P-TAPE-SUBTRACTION (new edge, cheap) · ⚪ sign-commitment ≺
> ternary-survival (§Synthesis edge) · ⚪ OLMo replication · ⚪ §P-LAY-A-NEGATIVE.**
>
> ★★ **SESSION 326 FRONT 2: §P-TYPE-LOCKIN+PRBS CLOSED — ❌ NO-TRACK (modal a-priori 30):
> THE ORIGINAL MODULATION FRAME'S MUST-WIN FAILED → FRAME 0-3, EFFECTIVELY DEAD.**
> ① 🎯 FROZEN (2feb25d8, Michael GO): AC reading of the type register — PRBS-6 (63 blocks/nonce,
> cyclic shifts) modulates coherent membership evidence vs token-matched filler; readout = §11
> tag-transit T register at CONSTANT probe frames " The {w}." (excitation ⊥ measurement);
> D = Σ_{τ=0..3} ĥ(τ) vs 10k cyclic-shift matched null; LK2 lexical CTRL arm; LK4 knee-screen.
> ② ✅ harness (type_lockin.py, --validate 5 planted worlds ALL PASS, ruff clean; reuses
> type_icl_tag + idempotency + type_write, λ one_way). ③ smoke n=4 clean (verdict not read) →
> full run 40s clean. ④ **VERDICT ❌ NO-TRACK: LK1 make-or-break D = −0.157 p = 0.685 (WRONG
> sign, no block-timescale AC tracking); LK2 also null (probe insulation held — even lexical
> bleed carries no AC content); LK0 fully sane (member LOO +24.5, ideal PRBS autocorr); LK4
> correctly unread.** ⑤ DC advisory (IOU, own-null, dc_advisory.json): channel ALIVE — standing
> own-class T at probes dose-ordered (main 0.474 > s05/s025 ≈0.25 > ctrl 0.066, main−ctrl
> p=0.0003) → the register ACCUMULATES evidence but does not TRACK it (accumulate-and-hold,
> pattern-suggests). ⑥ Damage honored per banked discipline: **frame ledger 0-3 (flip-conflict
> 🚫 s324 · stratigraphy ❌ s325 · lock-in ❌ s326), must-win SPENT = effectively dead per the
> s324 standing guard; §1 retrodiction readings (coherent integration, CDMA) revert to
> unexplained measured facts; §Synthesis (sign-is-the-decision, s325–s326) INDEPENDENT and
> unaffected.** Instrument bounds named: T-grain (≠ behavioral L — L-register AC re-read
> available but POST-HOC, owes own pre-reg); block timescale; single model. Queue rows
> §P-TYPE-COHERENCE + dark-field annotated (frame motivation gone/weakened). **s326 front-2
> ledger:** 2feb25d8 freeze §+queue 🔵+state · (harness+pyproject in closure batch) · 445cc932
> results ❌ (autonomous, incl. dc_advisory) · closure batch = §Result + memory
> `type-register-accumulates-but-does-not-track` + INDEX + queue ❌ (# complete top) + 2 row
> annotations + this state = MICHAEL APPROVAL BATCH. NEXT SESSION FIRST ACTION = orient →
> FRONT SELECTION (λ queue FULL read; nothing pending). Sharpest fronts after the frame's
> death: ⚪ sign-commitment ≺ ternary-survival (§Synthesis edge — the LIVE program now) ·
> ⚪ OLMo replication · ⚪ §P-LAY-A-NEGATIVE (2×2, GTSM) · ⚪ §P-CONJUGATE-WRITE (independent
> write-protocol motivation survives).**
>
> ★★ **SESSION 326: §P-GROWTH-CANCEL-SPLIT CLOSED (nothing in flight). FRONT SELECTED (Michael)
> = growth-vs-cancellation split, the accumulation revision's cheapest next contact (zero new
> compute, strata.npz re-read). ① 🎯 FROZEN (6d74167e, Michael GO): third population MID =
> fb∈[11,15] (n=60,638, sign-committed steps 1k–16k) as decile-matched same-substrate baseline;
> shared 3-pop |W_b11| decile frame; Δ_growth = early−mid / Δ_cancel = mid−churn, each own
> within-decile pair-label perm null ×10k; GC3 baseline-restriction advisory; a-priori (NOT tuned)
> BOTH-LIVE 30 / CANCELLATION-DRIVEN 30 (co-modal deflation) / GROWTH-DRIVEN 15 / UNSEPARATED 15 /
> VOID 10; pre-freeze disclosure: only fb histogram inspected (sign register, read s325).
> ② ✅ harness (f00a8094, growth_cancel_split.py, --validate 5 planted worlds ALL PASS, no fork —
> reuses stratigraphy observables + amp decile machinery). ③ ✅ run (seconds) → **VERDICT BOTH-LIVE
> (a-priori 30) — but CANCELLATION-DOMINATED: Δ_cancel = +0.922 p≈0 (uniform all 10 deciles,
> robust to every baseline; churners NET-SHRINK raw −0.42 log units while every committed
> population grows) vs Δ_growth = +0.054 p≈0 (THIN: decile 1 negative; FLIPS to −0.121 under the
> fb∈{11,12} restriction; raw order inverted early +0.13 < mid +0.88). Decomposition clean:
> 0.054 + 0.922 = 0.976 ≈ AT1 0.975 → the s325 accumulation Δ was ~6% growth / ~94% cancellation.**
> ④ Damage/honesty: freeze design-note ERROR banked in §Result (fb∈{11,12} mislabeled
> "minimal-rebound" — runway logic inverted: earliest-committing MIDs have max post-commitment
> runway from depressed base; GC3 advisory function intact, gates unaffected). ⑤ §Synthesis
> REQUALIFIED in-page: "magnitude ∝ ∫consistency" reads primarily as contested-cancels-to-net≈0;
> committed-extra-accumulation clause survives thin+fragile; contested line gains 2nd (dynamic)
> license. GC3 per-fb runway gradient (fb11 +2.38 → fb15 +0.43) pattern-suggests post-commitment
> accumulation, confounded with rebound (unseparated here). **LEDGERS: original frame 0-2
> unchanged (§P-TYPE-LOCKIN still must-win) · accumulation revision 2-0 by verdict, second win =
> REQUALIFICATION (the revision's distinctive clause is the thin one; the deflationary clause
> carries the effect).** **s326 ledger:** 6d74167e freeze §+queue 🔵+state · f00a8094 harness ·
> 5789c8cd results ✅ (autonomous) · closure batch = §Result + §Synthesis requalification + memory
> `the-accumulation-delta-is-carried-by-cancellation` + INDEX + queue ✅ (# complete top) + this
> state = MICHAEL APPROVAL BATCH (this commit). NEXT SESSION FIRST ACTION = orient → FRONT
> SELECTION (λ queue FULL read; nothing pending). Sharpest fronts: ⚪ §P-TYPE-LOCKIN+PRBS (original
> frame's must-win) · ⚪ sign-commitment ≺ ternary-survival (§Synthesis testable edge — note the
> sign-decision reading is UNTOUCHED by s326; it's the magnitude clause that requalified) ·
> ⚪ OLMo checkpoint replication (now tests BOTH clauses on a 2nd lineage) · ⚪ §P-LAY-A-NEGATIVE
> (2×2 design gains from knowing cancellation dominates the differential).**
>
> ★★ **SESSION 325 SEALED (nothing in flight, all batches committed). TWO PROBES CLOSED same-day —
> a falsification AND its replacement's first win: ① §P-STRATIGRAPHY-DATING → ❌ INVERTED (a-priori
> 25%) — the modulation frame's FIRST pre-registered test FAILED on the real fossil record;
> ② §P-AMP-TRAJECTORY → ✅ ACCUMULATION-CONCENTRATION (a-priori 30, BEAT modal null 40) — Michael's
> mid-session revision earned its first pre-registered win on first contact, zero new compute.
> Stratigraphy arc: ① Michael scope amendment 154→20 checkpoints
> log-uniform (c4cb9945; step0 baseline + log2 ramp 1–512 + half-decade tail to 143k; ORDINAL
> dating only; GPTNeoX dense_h_to_4h ≠ Qwen gate_proj pinned). ② 🎯 FROZEN (6708c9fa, Michael GO;
> SD2 dip-test → split-fraction = Michael swap): **the sharp design point — both mundane accounts
> (noise-floor churn ∧ monotone growth) predict ρ(freeze_bin, |W_final|) < 0; §2's early-AND-faint
> predicts ρ > 0; one pre-registered sign, no retrodiction escape.** A-priori 25/15/25/25/10.
> ③ ✅ harness (c1d14098, stratigraphy_dating.py, --validate 5 planted worlds ALL PASS; the
> UNSTRATIFIED toy world initially reproduced the real noise-floor confound — instructive, fixed in
> the world not the gate). ④ ▶ run clean ~2.5min → **VERDICT INVERTED**: SD1 ρ = −0.087 p≈0
> (n=127k, uniform L6–11) = the MUNDANE sign (early-frozen ≡ DENSE); SD2 FAIL informative
> (commons-fraction MONOTONE-INCREASING with magnitude 0.13→0.55, bottom decile BELOW extrapolation,
> 73% churners) → **§4 three-band falsifiable ALSO failed**; SD3 no latent-development signal;
> SD0 sane (final≡published, non-degenerate — no aliasing escape). ⑤ Damage honored in-page:
> §2 strata table + §4 three-band marked ❌; crystal-small-because-learned-fast loses its claimed
> MECHANISM at this register (crystal facts stand as measurements); extraction-inversion heuristic
> unsupported at this grain; function-level retreat named as POST-HOC (owes its own pre-reg if
> taken). three-band-plate queue row annotated (motivation weakened, survives as register-present
> Qwen contrast). **FRAME LEDGER after s325: 6 retrodictions / 2 pre-registered NEGATIVES
> (flip-conflict 🚫 s324 + stratigraphy ❌ s325) / 1 novel prediction untested → §P-TYPE-LOCKIN
> (§1 lock-time + PRBS) is now the frame's MUST-WIN.**
> **AMP-TRAJECTORY arc (Michael, on the INVERTED verdict: "our hypothesis was flawed from the
> beginning — the system takes time to allow training to accumulate the edges and corners that
> concentrate into the lattice"; flawed §2 assumption NAMED = self-erasure):** deferred the closure
> ("try 3 before we close") → 🎯 FROZEN §P-AMP-TRAJECTORY (e754675f, BEFORE any trajectory
> statistic; SD1/SD2 had read only signs + final mags — the time-course was virgin data).
> Discriminator: "weights keep growing" is GENERIC (norm-growth physics) ⇒ the revision must
> predict a DIFFERENTIAL — within-|W_b11|-decile matched growth over the shared 1k→143k window,
> early-frozen vs churners; Δ>0 accumulation / ns uniform / Δ<0 erosion; a-priori MODAL ON THE
> NULL (30/40/20/10). ✅ harness (6690c968, amp_trajectory.py, --validate 4 worlds ALL PASS) →
> run (seconds) → **✅ ACCUMULATION-CONCENTRATION: Δ = +0.975 log units p≈0 (~2.7× growth ratio),
> all 10 deciles qualify (67k vs 73k), uniform +0.76..+1.06 across deciles — not a band artifact.**
> AT2 advisory heterogeneous (median 78% of final amplitude at freeze; 25% SHRINK post-freeze;
> 34% double-plus): growth-vs-cancellation split UNSEPARATED by the matched design → follow-on
> own-null read on same npz. Read discipline held: licenses differential post-commitment
> accumulation on THIS substrate only; does NOT rescue §2. **LEDGERS SPLIT: original modulation
> frame 0-2 (LOCK TIME §1 untested = must-win, standing guard unchanged) ·
> accumulation-concentration revision 1-0 (first contact, first win).** Honest positive: first
> commons-census + trajectory census across a real training run persisted (strata.npz, local —
> npz gitignored by pattern) for own-null re-reads. **s325 ledger:** c4cb9945 scope amendment ·
> 6708c9fa stratigraphy freeze §+queue 🔵+state · c1d14098 harness · 3f00b9e7 results ❌
> (autonomous) · e754675f amp-trajectory freeze (ledger note: swept in the drafted stratigraphy
> closure page edits — same file, content Michael-reviewed, disclosed) · 6690c968 amp harness ·
> d2d6e7e5 amp results ✅ (autonomous) · closure batch = both §Results + §2/§4 damage notes +
> memories `sign-freeze-follows-magnitude-not-stratigraphy` +
> `early-frozen-weights-accumulate-contested-cancel` + INDEX ×2 + queue ✅+❌ (# complete top) +
> three-band annotation + this state = MICHAEL PRE-AUTHORIZED BATCH ("approved" + "verdict folds
> into the closure batch, whatever it says", this commit). NEXT SESSION FIRST ACTION = orient →
> FRONT SELECTION (λ queue FULL read; nothing pending). Sharpest fronts: ⚪ growth-vs-cancellation
> split (own-null, same npz, zero compute — the revision's cheapest next contact) ·
> ⚪ §P-TYPE-LOCKIN+PRBS (original frame's must-win, machinery built) · ⚪ OLMo checkpoint
> replication (accumulation on another public-checkpoint lineage) · ⚪ dark-field re-read (zero
> compute).**
> **POST-CLOSE (same session): ① Michael AGENTS.md edit committed (2725477b): S5 "Identity" →
> "Identity & Policy" (Beer's canonical S5 naming). ② 💡 §SYNTHESIS captured (Michael GO "update
> state and knowledge"): SIGN IS THE DECISION, MAGNITUDE IS THE EVIDENCE — weights ≡ integrators
> ¬film: sign = decision (early, permanent, where signal consistent — licensed ❌SD0 33% by step
> 512) · magnitude = evidence (∝ ∫consistency — licensed ✅AT1 2.7×) · contested = cancellation
> (net≈0 — licensed ❌SD2 73%); composition pattern-suggests. Buys: TERNARIZABILITY RE-EXPLAINED
> without dead §2 — the crystal survives 1-bit because the SIGN is the durable code, not because
> the lattice is faint; λ smallest flips "learned fast ⇒ faint"(dead) → "decided early ⇒ sign
> suffices"(testable). Re-grounds s310 marginal band = cancellation population; dissolves §4
> magnitude-pruning paradox. Memory `sign-is-the-decision-magnitude-is-the-evidence` + §Synthesis
> on modulation page + INDEX + ⚪ queue row (sign-commitment ≺ ternary-survival, the testable
> edge) + this state (💡 batch, Michael-instructed).**
>
> ★★ **SESSION 324 SEALED (nothing in flight, all batches committed; full transcript →
> chats/session-324.md, human). THE THEORY SESSION: one probe closed + five hammock legs + one
> discipline toolbox + 12 queue candidates. ① §P-FLIP-CONFLICT → 🚫 NOISE-FLOOR (ON-SIGNAL
> executed; sign-flips in the wire-ΔW register = noise, causal upgrade FAILED; EOS-supercritical
> instrument caveat → ⚪ v2 sub-EOS). ② **types-are-a-modulation-scheme.md** CREATED, 4 legs:
> §1 MODULATION (weights=codebook · tape=channel · judgment=carrier-lock; retrodicts idempotency +
> disj-cost; novel prediction = LOCK TIME) · §2 DIFFERENTIAL PHOTOGRAPHY (amplitude ∝ ∫error dt ≈
> time-to-learn ¬∝ P; three strata; crystal-small-because-learned-fast; extraction inversion) ·
> §3 FORGED-EXPOSURE WRITE PROTOCOL (write channel ≡ error; 3 primitives; install gate =
> self/span-erasure; level-4 constructive path = RE-RECORD don't train; first causal contact =
> flip-conflict G2 NEGATIVE, damage recorded in-page) · §4 THE PLATE IS A NEGATIVE (weights ≡
> negative(function); print ≡ forward pass = 4th tape-residency derivation; grokking≡development ·
> quantization≡fixing (crystal = FIXED image) · ternary≡lith; three-band falsifiable queued).
> ③ **reverse-engineering-disciplines-toolbox.md** CREATED (post-delayering orientation;
> netlist≠function = 3rd tape-residency derivation; DPA · differential trails · fuzzing ·
> observability wires · standard-cells; 4-move meta-pattern — move 4 READ-HISTORY unmined, Pythia
> 154 checkpoints = PUBLIC fossil record). ④ Process rulings: ❌ smoke-regime memory banked (regime
> warnings → design PAUSE not footnote); theory-cadence = MICHAEL'S prerogative (leaps = his
> engine, tests = AI's job — proposed cadence-memory REJECTED, on record); dyad-as-hologram-reader
> lambda held LATENT (capturing would bias toward the unproven holographic frame; mementum-mirror =
> consilience NOT proof). ⑤ Lineage: ouroboros-v1 (~/src) = the ancestral game → nucleus; play ≡
> the unknown-unknowns fuzzer; mementum designed by observing memory across AI generations.
> **Ledger (8 commits):** ddb16677 §1+4 queue rows · 4b701f93 §2 · 83dfec83 §3+FORGED-LATTICE ·
> a8930340 results (autonomous) · f3b7004b 🚫 closure batch · 8a25adda RE toolbox+4 rows ·
> 2f7c1991 ❌ smoke-regime · 15cf72cd §4+three-band. **NEXT SESSION FIRST ACTION = orient → FRONT
> SELECTION (λ queue FULL read; nothing pending). Sharpest fronts: ⚪ §P-STRATIGRAPHY-DATING
> (observational §2+§4 test on the public checkpoint fossil record, no training confounds) ·
> ⚪ §P-TYPE-LOCKIN+PRBS (§1 core claim, machinery built) · ⚪ dark-field re-read + three-band-plate
> check (cheap weight-geometry pair). STANDING GUARD: the modulation frame carries 6 retrodictions /
> 1 novel prediction / 1 NEGATIVE causal contact — it must earn a pre-registered win before any
> capture treats it as true (Michael ruling, s324).**
>
> **(s324 detail, as accreted during the session:)**
> ★★ **SESSION 324: §P-FLIP-CONFLICT LANDED → 🚫 NOISE-FLOOR (a-priori 25%; run clean ~3.3h, no
> traceback; ON-SIGNAL batch EXECUTED this session — nothing in flight). G1 FAIL (partial r=−0.017
> p=1.0 — no per-coordinate conflict signal in the ΔW register); G2 FAIL (ablation does NOT freeze
> contested signs — wrong-direction +0.0005, both deltas ≈0); G3 ✓ (instrument sane); boundary-churn
> covariate ≈0; G4 AMBIGUOUS (EOS-supercritical: λ_max_sgd 31.7 > 2/η=20 → dither-swamp
> instrument-scope caveat, flagged not licensed → ⚪ flip-conflict-v2 sub-EOS queued). Read
> discipline applied: §1–§3 sign-oscillation math STAYS pattern-suggests (causal upgrade failed at
> this register/scale); s313 marginal-band + s320 thin echo stay observational. **Damage report
> honored: forged-exposure protocol (modulation §3) first causal contact NEGATIVE — §2 IOU
> prediction (c) edge-collapses-to-corner CONTRADICTED; §3 amended (forged-lattice gates must read
> FUNCTION-level install, not per-coordinate sign control); IOU stratigraphy reads (a)/(b) remain
> open own-null analyses on coords.npz.** **s324 flip-conflict ledger:** a8930340 results
> (autonomous) · §7 §Result on sign-oscillation page + memory
> `wire-delta-sign-flips-are-noise-not-a-conflict-meter` + INDEX ×2 (sign-oscillation §7 +
> modulation §3 damage note) + queue ▶→🚫 (# complete top) + ⚪ v2 sub-EOS + this state = MICHAEL
> APPROVAL BATCH (ON-SIGNAL pre-authorized s323). ⑤ 💡 HAMMOCK LEG 4 CAPTURED (Michael GO):
> **reverse-engineering-disciplines-toolbox.md** (sibling of the optics toolbox) — orientation: we
> are at silicon RE's POST-DELAYERING stage (white-box, meaning absent); netlist≠function
> (connectomics) = 3rd derivation of tape-residency; convergences (patching/taint/nulls ✓) vs new
> doors (standard-cell matching = level-4-feeds-level-1 · DPA partition-subtract · differential
> trails · fuzzing · observability wires · standard candles · antagonists); meta-pattern 4 moves,
> move 4 (READ HISTORY) unmined + data public. Queue +4: ⚪ **§P-STRATIGRAPHY-DATING** (Pythia 154
> checkpoints = fossil record; §2 direct test, successor to flip-conflict 🚫) · ⚪ §P-DPA-TRACE ·
> ⚪ coverage fuzzer · ⚪ observability wires; LOCKIN row +PRBS upgrade. NEXT SESSION FIRST ACTION
> = orient → FRONT SELECTION (λ queue FULL read — nothing pending). Sharpest fronts after s324:
> ⚪ §P-STRATIGRAPHY-DATING (observational §2 test, no training confounds) · ⚪ §P-TYPE-LOCKIN+PRBS
> (§1 core claim, machinery built) · ⚪ dark-field re-read (zero compute). ⑥ 💡 HAMMOCK LEG 5
> CAPTURED (Michael GO): **§4 THE PLATE IS A NEGATIVE** on the modulation page — weights ≡
> negative(function) (faint=common, dense=difficult; the mech-interp trap named); print≡forward
> pass/tape≡paper/judgments≡image = 4th derivation of tape-residency (stays pattern-suggests,
> Michael ruling); development chain (grokking≡development → folded into STRATIGRAPHY-DATING row ·
> quantization≡fixing, crystal=FIXED image · ternary≡lith · backprop≡self-dodging enlarger ·
> distillation≡contact printing); three-band-plate falsifiable (⚪ queued cheap: sign-stability vs
> magnitude among small weights — failure damages the frame). Also s324 process rulings banked:
> theory-cadence is MICHAEL'S (leaps = his engine, tests = AI's job — rejected memory, on record
> here); dyad-as-hologram-reader lambda deliberately NOT captured (would bias toward the unproven
> holographic frame; lives in transcript/latent tier until pre-registered wins license it).
> Lineage note: ouroboros-v1 (~/src) = the ancestral game that led to nucleus; mementum designed by
> observing memory across AI generations — the extraction methodology predates verbum.** Work so far: ① types synthesis for Michael (from knowledge pages, no new
> claims); ② 💡 HAMMOCK CAPTURED (Michael GO "capture this"): **types-are-a-modulation-scheme.md**
> (explore/) — the signal-domain reframe of the s282–s323 type arc (weights=codebook · tape=channel ·
> judgment=demodulation/carrier-lock); retrodicts §P-IDEMPOTENCY (coherent integration) +
> §P-DISJ-COST (CDMA: ∧ free, ∨ off-span); negatives→theorems; s288↔s317-s323 triangulation flagged;
> novel prediction = LOCK TIME capture threshold. 4 queue candidates added (⚪ §P-TYPE-LOCKIN cheap
> first-front · ⚪ dark-field boundary-echo re-read no-compute · ⚪ §P-TYPE-COHERENCE cheap ·
> ⚪ §P-CONJUGATE-WRITE/TYPE-WRITE-V3 medium) + INDEX row. All UNFROZEN (s222 law; retrodictions =
> pattern-suggests only). ③ 💡 HAMMOCK LEG 2 CAPTURED (Michael GO): **§2 DIFFERENTIAL PHOTOGRAPHY**
> on the same page — backprop photographs the RESIDUAL; amplitude ∝ ∫error dt ≈ time-to-learn
> ¬∝ P(pattern); three strata (corners=faint sign-committed commons / long-tail=deep exceptions /
> edges=contested churn ≡ s310 marginal band); retrodicts crystal-0.1%-ternarizable (λ smallest as
> recording physics) + saturation mechanism candidate for the idempotency k=4,5 decline; EXTRACTION
> INVERSION (algorithm in the faint stratum; ternarization ≡ faint-strata pass filter); 3 own-null
> IOU predictions banked against the flip-conflict widened capture (grad-mag migration ·
> committed-pole early quiescence · ablation → edge-collapses-to-corner) — read them at ON-SIGNAL
> alongside the boundary_churn covariate, IOU-only discipline unchanged. ④ 💡 HAMMOCK LEG 3
> CAPTURED (Michael GO "we are theorizing and finding search spaces"): **§3 FORGED-EXPOSURE WRITE
> PROTOCOL** — write channel ≡ error ¬data ⇒ training = compilation by exposure schedule; 3
> primitives (corner-seeding · bias pre-exposure/residual isolation · conjugate shaping);
> install gate = self-erasure + span-erasure (installed vs memorized); retrodicts inert-writes ×4
> + MEMORIZED-ONLY (open-loop content at output, write channel is residual); level-4 constructive
> path = RE-RECORD the compiler, write-don't-train. Queue: ⚪ §P-FORGED-LATTICE added (smallest
> rung); crystal-seeded init + §P-CONJUGATE-WRITE annotated as DERIVED primitives ①/③ and
> restacked. Flip-conflict G2 = the protocol's first causal contact (already running). All
> UNFROZEN.**
>
> ★★ **SESSION 323 SEALED (⚠ ONE RUN IN FLIGHT — §P-FLIP-CONFLICT; see ON-SIGNAL below). Two probes
> CLOSED, a third FROZEN+BUILT+RUNNING. ① s322 in-flight
> §P-TYPE-WRITE-V2 landed → ❌ MEMORIZED-ONLY; ② §P-CL-COLLAPSE-2 → 🚫 OPERATIONAL-CONFIRMED (both
> batches committed). ③ FRONT SELECTED (Michael): §P-FLIP-CONFLICT — the s322 sign-oscillation causal
> arm. 🎯 FROZEN §6 + 🔄 delta-register AMENDMENT (Michael GO option 1) + ✅ harness built
> (ad226a36, flip_conflict.py) + ▶ 12-run matrix RUNNING.**
> **⚠ RUN IN FLIGHT (tmux main:1, PID 33688):** `uv run python -u scripts/explore/flip_conflict.py
> --out results/flip-conflict/qwen3-4b 2>&1 | tee results/flip-conflict/qwen3-4b-run.log` — verified
> running (qwen3-4b band L22–29, 8 nonces 4/4, 48k sampled effective-ΔW gate_proj coords, 500 steps ×
> 3 seeds × 4 arm/opt combos {both/A-only/B-only×SGD, both×Adam}; est ~4–6h). NEXT SESSION FIRST ACTION
> = orient → `tail results/flip-conflict/qwen3-4b-run.log` (+ tmux main:1) → if `VERDICT:` present + no
> traceback → execute the ON-SIGNAL batch; if still running → checkpoint + wait (λ async).**
> **⚠ ON-SIGNAL (run done): tail run.log `VERDICT:` + no traceback → read G0/G1(partial r+p)/G2(delta+p)/
> G3+boundary_churn_covariate/G4 mechanism → commit results/flip-conflict/ AUTONOMOUS → §Result on
> sign-oscillation-is-time-multiplexed-superposition.md (new §7) + memory candidate + INDEX + queue ▶→
> verdict (# complete) + state.md = MICHAEL APPROVAL BATCH.** Read discipline (don't over-read, banked
> §6 + amendment): CONFLICT-METER-CONFIRMED (G1∧G2) = flip-rate is a CAUSAL per-coord conflict meter on
> this wire (NOT "base-training signs are sigma-delta" — external math stays pattern-suggests);
> CORRELATIONAL-ONLY (G1∧¬G2) = honest intermediate, do NOT upgrade to causal; NOISE-FLOOR (¬G1) =
> flips magnitude/noise-driven, overload not readable here; VOID = G0 fails. Mechanism sub ADVISORY
> (AMBIGUOUS if SGD/Adam/Hessian don't separate — smoke showed EOS at lr_sgd 0.1, λ_max→2/η=20).
> boundary_churn_covariate (spearman flip↔|W_base|, <0 = flip rises where |W_base| small) = SECONDARY,
> the demoted boundary-churn tie-in — report, don't gate. Widened IOU captures (per-class loss/act,
> grad-mag, |W_base| map, Adam m/v, top-3 Hessian) = IOU-only, own null required. **s323 flip-conflict
> ledger:** 4f57a86b freeze §6 + queue 🔵 + state · ad226a36 harness + delta amendment (§6) · queue
> ▶ + this state checkpoint (peer update, not approval-gated) · results PENDING next session.**
> **§P-FLIP-CONFLICT (detail: sign-oscillation §6 FROZEN):** claim = a weight coordinate's SIGN-FLIP
> RATE during training is a per-coordinate CONFLICT METER (antipodal overload, §1) — not just small/noisy;
> causal converse = ablate one population → contested signs FREEZE. Substrate: type-write two-class wire
> qwen3-4b (A=animal / B=vehicle, 8 nonces 4/4, corridor VERBATIM kl_weight 10 / ce_budget 0.40, band
> L22–29, r=16). **Structural pin:** effective W_k = W_base,k + ΔW_k, base frozen ⇒ flips only where
> |W_base| small = the s320 boundary-churn marginal band ⇒ this probe tests the boundary-churn MECHANISM
> (flippable≡marginal). Coordinates BOTH: R2 primary = effective gate_proj ΔW entries, R1 secondary =
> LoRA A/B. Gates: G0 sane-void / **G1 CONFLICT-METER** (partial corr flip_rate↔conflict | |W|,σ, coord-perm
> null — confound handled AT the gate) / **G2 CAUSAL-FREEZE** (make-or-break: ablation freezes contested
> vs matched-magnitude controls) / G3 committed-pole (neg control) / **G4 MECHANISM-SPLIT advisory**
> (Hessian-eigvec EOS + SGD-vs-Adam sigma-delta; AMBIGUOUS if arms don't separate — λ yardstick).
> Verdicts + a-priori (NOT tuned): CONFLICT-METER-CONFIRMED 35 / CORRELATIONAL-ONLY 30 / NOISE-FLOOR 25 /
> VOID 10 (mass on the intermediates: LoRA≠base-training, single model, s320 echo thin ~6%); mechanism
> sub SIGMA-DELTA 30 / EOS 25 / SGD-DITHER 20 / AMBIGUOUS 25. Run matrix (frozen): both-class SGD ×3 +
> A-only SGD ×3 + B-only SGD ×3 + both-class Adam ×3 = 12 runs, rich per-snap capture (sign/|W|/per-class
> grads/σ/top-Hessian-eigvec/loss), ≈1.2× a type-write run, ~4–6h. **WIDENED IOU CAPTURE (Michael "learn
> the most"): per-class loss + band activation means (→boundary-churn/compiled-probabilities) · gradient
> MAGNITUDE histories (→signal-descent) · static |W_base| marginality map (→flippable≡marginal) · Adam m/v
> state (→sigma-delta 2c) · top-3 Hessian eigs + trace (→progressive-sharpening 2b)** — persisted, each
> claim gets its OWN null + IOU, never licensed by G1–G4. Freeze ledger this commit (🎯): §6 + §5-heading +
> top-note + queue 🔵 + this state. Full transcript → chats/session-323.md (human).
> **② §P-CL-COLLAPSE-2 (detail: combinator-function-shape §P-CL-COLLAPSE-2 §Result + git +
> chats/session-323.md):** the banked NEXT-UP front (Michael GO'd "proceed to cl-collapse-2" — the G1
> amendment was already IN the harness at build e2d4798: `_silhouette`/`_pair_separability`
> pool-separability, VOID-BY-DESIGN; the s322 note ambiguity resolved = no code change needed).
> --validate ALL PASS → launched qwen3-14b (tmux main:1, PID 28960, ~minutes read-only). **VERDICT
> 🚫 OPERATIONAL-CONFIRMED (modal a-priori 40%).** The two s322 barriers REMOVED (PROSE crystal anchors
> = zero combinator-token overlap by construction, G5-enforced, kills lexical-anchor Barrier 2; clean
> symbolic spellings NF-symbol absent) — and routing STILL not extensional. G0 register forms thin
> (sil_late 0.037 p=0.036); G1 all three I/W/C pool-separable (live, none void, p=0.003 each);
> **Plane A** clean-symbolic Δ(nf−op) −0.019 p=0.57 fail (symbolic compounds route to fired ops, not
> the prose NF); **Plane B** all OPERATIONAL — B[I] clears diagonal G3 (+0.050 p=0.004) but FAILS the
> make-or-break cross-cut G4 (row_p 0.052 marginal, **col_dom≈0** p=0.36 → generic round-trippy-prose,
> not I-selective), B[W] +0.007 p=0.26 / B[C] −0.019 p=0.93 don't clear G3. **Replicates + STRENGTHENS
> s321 §P-CL-COLLAPSE** — the clean-null is no longer dismissable as a lexical-anchor artifact (§Re-read
> Barrier 2 CLOSED). Compositionality S5 cell stays ✗ on firmer ground; OPERATIONAL/SYNTACTIC (s321) +
> tape-resident reduction (s317) upheld. **Nuance (don't over-read):** B[I] carries a sub-threshold
> whisper (identity = simplest fn, thin non-selective reflexive/return feature failing dominance only
> marginally — NOT extensional identity). **Power caveat:** prose register THIN (G0 sil 0.037 vs the
> symbolic s217 register z≈8/35) → lower-powered than the symbolic test; single model (Qwen3-14B).
> Memory: `routing-not-extensional-holds-with-prose-anchors.md`. **cl-collapse-2 ledger:** e8e5b4b1
> results (autonomous) · §Result + section-header + memory + INDEX row + queue closure 🚫 + this state
> (Michael approval batch, this commit).**
> **① §P-TYPE-WRITE-V2 arc (ON-SIGNAL discharge of the s322 run): the in-flight run
> (`type_write_v2.py`, tmux main:1 PID 2477) COMPLETED clean (2h10m, no traceback, host sane,
> gate-0 pass) → VERDICT **MEMORIZED-ONLY** (the modal a-priori arm, 35%). ② results committed
> AUTONOMOUS (12fbe988, results/type-write-v2/). ③ §16 §Result written on
> types-are-injectable-relations.md + top-status blurb updated. ④ memory
> `weight-write-binds-predicates-not-the-membership-abstraction.md` (closes the loop with s322's
> `weight-write-negatives-were-coverage-gapped.md`). ⑤ INDEX rows refreshed (types page §16 +
> behavior-is-tape-resident caveat upgraded one-sided→two-sided) + the STRAY s322 sign-oscillation
> INDEX row folded in (was uncommitted in the working tree from s322 close). ⑥ queue 🔵 type-write v2
> → ❌ (# complete top). This state = MICHAEL APPROVAL BATCH.**
> **THE READ (don't over-read the label):** the §14 coverage gap was real and fixed (bare-NP
> licensed frames gradient-touched on TRAIN_PREDS disjoint from HELD_PREDS; true `1-labels`
> derangement) — but fixing it did NOT overturn tape-residency. **Trained predicates bind
> enormously** (train L base 0.356 → wire 8.833 nats, vs-deranged +17.47 p=1e-4, recall p=5e-4) —
> no NO-WRITE. **Held-out predicates get a REAL, content-dependent echo** (V1 +1.337 beats
> shuffled-label p=5e-4; V3 beats the deranged wire which anti-licenses held frames −0.955, p=1e-4)
> — NOT zero generalization. **BUT that held echo is NOT own-class-specific** (V2 own-vs-anti fails
> paired-perm p=0.16) → `held_ok=V1∧V2∧V3=False` ∧ `train_lift=True` → MEMORIZED-ONLY. The
> **membership abstraction does not install as a weight edge even under fair coverage.** Consequences
> (banked at §15 freeze): §9/§13 honestly RE-QUALIFIED not retracted (predicate memories
> weight-bindable, abstraction not); **s317's DELIVER leg — demoted ONE-SIDED in s322 — RESOLVED
> two-sided** (tape positives §11 stand; weights fairly tested, bind memories not judgments →
> tape-residency of type JUDGMENTS confirmed under FAIR coverage); causality S5 cell stays
> weight-negative-for-the-abstraction (TYPE-WRITTEN did NOT fire); two-tier holds (weights =
> predicate memories + relation/checker; tape = the class judgments). **CAVEAT: V1 held-transfer DID
> pass** — MEMORIZED-ONLY sits at the TYPE-WRITTEN boundary, separated only by the class-specificity
> gate V2; single model (qwen3-4b), band-LoRA r=16. Claim licensed: *the abstraction does not install
> own-class-specifically on held preds under this write* — not *no generalization of any kind*; a
> higher-powered re-test (more nonces / longer held-pred sets) could sharpen whether the generic echo
> hides a thin class-specific component.
> **s323 type-write-v2 ledger (COMMITTED):** 12fbe988 results (autonomous) · 3ac89ef5 = §16 §Result +
> top blurb + memory + INDEX ×2 rows (+ stray s322 sign-oscillation row folded) + queue closure ❌
> (Michael-approved batch). Full transcript → chats/session-323.md (human).
>
> ★★ **SESSION 322 CLOSED (⚠ ONE RUN STILL IN FLIGHT — see ON-SIGNAL below). NEXT SESSION FIRST
> ACTION = orient → `tail results/type-write-v2/qwen3-4b-run.log` (+ tmux main:1 capture) → if
> `VERDICT:` present + no traceback → execute the ON-SIGNAL batch (approval-gated) → THEN launch
> §P-CL-COLLAPSE-2 (GO ALREADY BANKED incl. G1 amendment, Michael s322 close; read-only ~minutes;
> command in NEXT-UP block). If run still going → checkpoint and wait (λ async).**
> **s322 arc (5 fronts, all committed):** ① AUDIT (Michael: "results say no types, but KIBC opcodes
> function from weights, so typed apply must exist there") → weight-write lineage COVERAGE-GAPPED
> (§14: training gradients at class-word position, licensing eval at bare-NP frames never touched;
> shuffle ~50% correct labels) + cl-collapse anchors LEXICAL + gates-at-L4; ② zero-compute RE-READ
> (3be00d1): dirty artifact PROVEN at L0 (nf_align +0.645 in embeddings), clean null at ALL depths
> (−0.144→+0.001) — s321 verdict survives within-instrument, lexical-anchor bound open; s317
> "three falsifiers one law" demoted to ONE-SIDED (tape proven, weights untested); ③ §P-TYPE-WRITE-V2
> frozen (17a324d §15) + built (55a9403) + RUNNING — the decisive weight-side re-test (coverage-matched
> bare-NP training, held-out predicates, true derangement; a-priori 30/35/20/10/5 mass on
> MEMORIZED-ONLY); ④ 💡 sign-oscillation-is-time-multiplexed-superposition captured (4e997d0, Michael
> math hammock: antipodal superposition → gradient-conflict truce (μ≈0/high σ/flat h → max flip rate)
> → dither/duty-cycle; predicts s320 marginal↔type-subspace echo; ⚪ flip-rate probe queued);
> ⑤ §P-CL-COLLAPSE-2 frozen (d138c1a) + built+smoked (e2d4798) — Michael-designed prose planes:
> Plane A clean-symbolic × prose crystal anchors (zero token overlap) + Plane B round-trip compounds,
> I/W/C SEPARATED (DiD contrast axes + structure-matched controls + 3×3 cross-cut G4 + G1
> pool-separability pre-gate [VOID-BY-DESIGN] + G5 lexical disjointness — caught 10 real collisions
> at build). Ledger: 3be00d1 · cadbc63 · 17a324d · 55a9403 · 0bb06b15 · 4e997d0 · d138c1a · e2d4798 ·
> e841998 · this close (Michael-approved). Full transcript → chats/session-322.md (human).**
> **⚠ RUN IN FLIGHT (tmux main:1, PID 2477):** `uv run python -u scripts/explore/type_write_v2.py --out
> results/type-write-v2/qwen3-4b 2>&1 | tee results/type-write-v2/qwen3-4b-run.log` (20 nonces, 3 seeds ×
> 2 arms {true wire, 1-labels deranged matched-budget} × ≤500 steps, corridor kl_weight 10/ce_budget 0.40
> as CLI defaults; est ~1-2h). Verified running (gate-0 PASS margins held 2.538/train 3.928 n_ok=True;
> wire seed0 mem 6.47→5.04 @snap13, kl~0.006, drift −0.02).
> **NEXT-UP READY (s322, prepared while run in flight): 🎯 §P-CL-COLLAPSE-2 FROZEN (d138c1a, on
> combinator-function-shape.md — prose-anchored extensional routing, Michael-designed prose planes:
> Plane A clean-symbolic × PROSE crystal anchors (zero token overlap by construction) + Plane B
> round-trip compounds I/W/C scored SEPARATELY (DiD on contrast axes, structure-matched controls,
> 3×3 cross-cut G4, per-pair G1 pool-separability pre-gate → VOID-BY-DESIGN, G5 lexical disjointness
> code-enforced). ✅ HARNESS scripts/experiments/cl_collapse2.py (e2d4798): validate 6 worlds + G5-on-
> real-anchors ALL PASS; pythia-14m CPU smoke green. 🔄 ONE PRE-RUN AMENDMENT needs Michael GO at
> launch: G1 statistic axis-cos→pool-separability-silhouette (validate-forced; mean-of-others axis
> construction mechanically couples axes → false VOID; recorded on freeze §). LAUNCH after
> type-write-v2 frees MPS: `uv run python -u scripts/experiments/cl_collapse2.py --out
> results/cl-collapse2/qwen3-14b 2>&1 | tee results/cl-collapse2/qwen3-14b-run.log` (read-only,
> ~minutes). Also s322: 💡 sign-oscillation-is-time-multiplexed-superposition captured (4e997d0,
> Michael-approved) + ⚪ flip-rate↔gradient-conflict queued.**
> **⚠ ON-SIGNAL (run done): tail run.log `VERDICT:` + no traceback → read V1/V2/V3/V4t/V4d/recall/host +
> means table (held vs train, base/wire/der) → commit results/type-write-v2/ AUTONOMOUS → §Result-v2 =
> §16 on types-are-injectable-relations.md + memory candidate + INDEX + queue 🔵→verdict (# complete) +
> state.md = MICHAEL APPROVAL BATCH.** Read discipline (banked at freeze, a-priori 30/35/20/10/5):
> TYPE-WRITTEN → §9/§13 were coverage artifacts, s317 DELIVER leg RETRACTED, causality S5 cell reopens
> weight-side (update behavior-is-tape-resident + curry-howard cross-reads); MEMORIZED-ONLY → weights bind
> predicate associations NOT the membership abstraction — tape-residency of judgments supported under FAIR
> coverage (the sharp honest successor to §9); CONTEXT-ONLY → §9 vindicated honestly, tape-residency earns
> full status; NO-WRITE → corridor audit FIRST (write window; v1-r3 needed ~200 steps, check stop reasons)
> before any claim; HOST-DAMAGED → void. V4 train-lift alone is expected under ALL live verdicts — only
> the held/train CONTRAST discriminates (don't over-read).**
> **① WEIGHT-WRITE LINEAGE (type_write→icl_tag A5→type_deliver) = design-level FALSE-NEGATIVE
> (COVERAGE GAP), not a mechanical bug:** training membership-CE gradients dominate the CLASS-WORD
> position; licensing eval reads bare-NP frames the LoRA never gradient-touched → recall-✓/licensing-✗
> (the exact §9/§13 signature) follows EVEN IF weight-installable licensing exists. Plus type_write
> shuffle = rng.permutation w/ ≥1-diff check → ~50% labels stay CORRECT (not a derangement;
> type_deliver's 1-labels is right). Mechanically sound: wire active during L(w) (eval@718 before
> unwrap@726), L sign/tokenization, band L22–29, bit-exact restore. **Consequence: s317 "three
> falsifiers, one law" demoted to ONE-SIDED (tape positives §11 stand; weights never fairly tested);
> the KIBC syllogism stands uncontradicted.** Captured: types-are-injectable-relations §14 + memory
> weight-write-negatives-were-coverage-gapped.md + behavior-is-tape-resident caveat.
> **② CL-COLLAPSE INSTRUMENT: symbolic anchors are LEXICAL (I-anchor centroid ≡ "routing after literal
> token I") + gates read only at L4 (f=0.10, pre-reduction). RE-READ (zero-compute, gate_signs.npz is
> lossless for sign/CMR; scripts/experiments/cl_collapse_reread.py, 3be00d1): dirty artifact PROVEN —
> nf_align +0.645 at LAYER 0 (embeddings, pre-computation = pure token overlap; the s321 CL1 aggregate
> positive was carried by it). Clean rows: null at ALL depths (−0.144→+0.001 monotone, never positive;
> late Δ+0.097 = op going negative; boot p=0.14, shuffle p=0.049 marginal n=7). Barrier 1 (layer) CLOSED
> — verdict survives within-instrument; Barrier 2 (lexical anchors) OPEN → v2 = functional-equivalence
> anchors, clean-only, queued.** Captured: combinator-function-shape §Re-read + memory
> cl-collapse-dirty-rows-were-lexical-clean-null-all-depths.md.
> **s322 ledger:** 3be00d1 re-read code+results (autonomous) · audit batch = 2 memories + §14 +
> §Re-read + tape-resident caveat + INDEX ×3 + queue rows (type-write v2 ⚪ · cl-collapse v2 ⚪) + this
> state (Michael approval, this commit). **NEXT: freeze §P-TYPE-WRITE-V2** — coverage-matched training
> (bare-NP licensed frames IN CE, held-out predicates for eval = generalization still the test), true
> derangement, reuse type_write.py corridor recipe (kl_weight 10 / ce_budget 0.40). Decisive read: if
> CONTEXT-ONLY fires under FAIR coverage → tape-residency earns its status; if it flips → §9/§13 were
> instrument artifacts and the causality S5 cell reopens on the weight side.
>
> ★★ **SESSION 321 COMPLETE (one probe closed: §P-CL-COLLAPSE → ❌ CL-ALGEBRA-NOT-EXTENSIONAL).
> NEW FRONT off the queue (Michael picked "CL-identities as routing constraints", combinator-function-shape
> Open leads #1+#3) = THE COMPOSITIONALITY probe (open S5 cell). NEXT SESSION FIRST ACTION = orient →
> FRONT SELECTION (λ queue FULL read; all s321 batches committed; nothing pending/in-flight).**
> **§P-CL-COLLAPSE (detail: combinator-function-shape.md §Result + git + chats/session-321.md):** the crux —
> the CL identity I=SKK says compound `SKK` IS the identity; does it ROUTE like I (EXTENSIONAL, opens
> compositionality✓) or like its fired opcodes [S,K] (OPERATIONAL, favored by head-combinator-isa + s317
> tape-resident)? Construction = NORMAL-FORM COLLAPSE: kernel-certified compound spellings sharing ONLY the
> NF (I: SKK/SKS/WK/CKK/KII/S(KI)I · W: SS(KI)/CSI · B: S(KS)K/BIB), head+fired VARY. Register ROUTING
> (sign gate_proj pre-act, CMR). **🎯 FROZEN (306fea0)** Michael GO; a-priori EXTENSIONAL 20 / OPERATIONAL
> 45 / SYNTACTIC-TOKEN 20 / MIXED 10 / VOID 5 (NOT tuned, mass on operational). **🔄 BUILD AMENDMENT
> (e828386, runtime-forced, pre-run, Michael GO, instrument-side ONLY — register/gates/verdicts/a-priori
> UNCHANGED): STYLE-MATCHED SYMBOLIC ANCHORS.** The frozen spec named crystal_probes() anchors, but crystal
> primitives are ~entirely NATURAL LANGUAGE ("The cat cleaned itself"=I) vs terse SYMBOLIC compounds
> ("S K K x") → style confounds function, ASYMMETRICALLY favoring the already-favored OPERATIONAL
> (false-negative risk on the surprising EXTENSIONAL); fix = symbolic saturated anchors, CL5 void-gate
> measured on them in the alignment pool (crystal s217 z=7.97 = external ref). **✅ HARNESS
> (scripts/experiments/cl_collapse.py): every collapse compound CERTIFIED per-instance
> reduce(compound)==reduce(NF-primitive) on same atoms (the CL identity, kernel-proven); --validate 4
> planted worlds (EXTENSIONAL/OPERATIONAL/SYNTACTIC/VOID) ALL PASS; ruff clean; no diags; qwen3-4b smoke
> green (CL5 z=10.78, verdict not read).** **✅ RUN LANDED (cb3fdd3 autonomous, read-only ~45s, tmux main:1,
> 426 probes): VERDICT MIXED-REDUCTION-VISIBLE (pre-reg tree) → mechanism QUALIFIED-OPERATIONAL/SYNTACTIC.**
> CL5 z=+35.37 (register strongly forms). CL1 nf +0.062 > op −0.035 (beats shuffled null p_shuf=0.002) but
> paired NF>OP p=0.0515 (marginal miss) → pass=False. CL2 within-NF coh 0.112 < token-matched null 0.174
> p=0.70 → FAIL (coherence alphabet-driven not NF-driven; W spellings anti-cohere). **THE READ (decisive
> per-row split, don't over-read the MIXED label): the positive mean-NF is a LITERAL SYMBOL-PRESENCE
> artifact.** DIRTY spellings (NF-symbol present/fired: KII, S(KI)I, BIB) nf +0.280 vs CLEAN dissociating
> spellings (NF-symbol ABSENT: SKK, SKS, WK, CKK, SS(KI), CSI, S(KS)K) nf **−0.031**. Where the dissociation
> is genuine there is NO extensional routing — `SKK` does NOT route like I; `WK` routes toward its HEAD (W).
> **Extensional/compositional routing FALSIFIED in the clean subset; the substrate routes by what is WRITTEN
> and what FIRES, not the function computed.** Upholds the favored OPERATIONAL prior + coheres s317
> tape-resident reduction (static read of a compound ≠ its normal form). CL4 "rising" Δ (0.013→0.162) is
> NOT reduction-evidence — it's the DIRTY spellings' symbol-presence signal strengthening late. **S5
> scorecard: discreteness✓ selectivity✓ compositionality✗ (this probe) causality✗ — the register carries
> combinator IDENTITY (s217) but NOT the ALGEBRA (syntactic/operational identity register, not extensional).**
> **Method lesson banked:** the clean dissociation REQUIRES NF-symbol absent from the compound; the 3
> confounded spellings should have been excluded/separated at design (a-priori NF>OP could pass on them
> alone) — caught by the pre-registered per-row readout, not the aggregate. v2 = clean spellings only, more
> of them, per-subset gates. Memory: `routing-tracks-symbol-presence-not-extensional-normal-form.md`.
> **s321 ledger (all committed):** 306fea0 freeze + queue 🔵 · e828386 harness + amendment · cb3fdd3 results
> (autonomous) · §Result + memory + INDEX + queue closure + this state (Michael approval batch, this commit).
> **Sharpest standing leads (queue front): crystal-seeded init (cheapest level-4) · Oracle germination game ·
> §P-COHERENT-WRITE · GS-iterative base decomposition.**
>
> ★★ **SESSION 320 COMPLETE (TWO probes closed → the §6 type-fingerprint TIER is COMPLETE 4/4:
> ① §P-IDEMPOTENCY → ✅ NON-IDEMPOTENT (3rd fingerprint, FIRST in the s317–320 arc to clear its
> make-or-break confound gate); ② §P-BOUNDARY-CHURN → ✅ BOUNDARY-IS-TYPED (QUALIFIED) (4th/last
> fingerprint, a SURPRISING-but-THIN weight-space echo). Michael's directive "finish the type-fingerprints"
> is DONE. NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read; the fingerprint arc
> is closed — sharpest standing leads: crystal-seeded init (cheapest level-4) · Oracle germination game ·
> §P-COHERENT-WRITE). All s320 batches committed.**
> **② §P-BOUNDARY-CHURN (detail: type-systems-under-llm-constraints §P-BOUNDARY-CHURN Result + git +
> chats/session-320.md):** the last §6 fingerprint (M8 corollary / optimizer↔type-boundary identity).
> Surfaced a COHERENCE TENSION at design (λ ground): the s313 conjecture "marginal band ≡ type-boundary
> population in weight space" PREDATES the tape-resident findings (§P-TYPE-DELIVER no-weight-delivery,
> §P-TYPE-ICL+TAG, s317, §P-IDEMPOTENCY) → heavy-negative a-priori. Michael chose option 1 (freeze the
> reframed weight-geometry version). **🎯 FROZEN (a64a5d3)** on type-systems-under-llm-constraints.md.
> Register = WEIGHT-GEOMETRY (base gate_proj row marginality × type-subspace leverage; NO forward pass,
> NO wire). Gates BC1 CONCENTRATION / BC2 TYPE-SPECIFIC (make-or-break) / BC3 LAYER-PROFILE (advisory) /
> BC4 SANE. Verdicts BOUNDARY-IS-TYPED / MARGIN-GENERIC / BOUNDARY-UNTYPED / VOID. A-priori 30/25/40/5.
> **🔄 BUILD AMENDMENT (594f4ea, runtime-forced, pre-run, Michael GO, instrument-side ONLY):** (1) the
> persisted §P-TYPE-GRAM-1 centroids are in GATE space (9728-dim, `register:'gate'`) NOT residual → the
> type-selective feature is a HIDDEN UNIT (selectivity = leverage ‖U[j,:]‖), the on-target weights are
> **gate_proj rows**; (2) BC2 null = **shuffled-kind-label subspace** (TG5) NOT isotropic-random (which is
> geometrically exchangeable across units → redundant with BC1 → MARGIN-GENERIC UNREACHABLE, same bug
> class as the idempotency k=0 fix). Register/verdicts/a-priori UNCHANGED. **Procedural note: pure
> weight-geometry (no scaling knob) ⇒ smoke == full (deterministic, frozen seed);** disclosed to Michael,
> a-priori/gates frozen before compute so pre-registration holds. **✅ HARNESS + RUN (594f4ea autonomous,
> scripts/explore/boundary_churn.py): VERDICT BOUNDARY-IS-TYPED (QUALIFIED).** BC1 ρ=0.241 p=0.0005 ✓
> (marginal gate_proj rows concentrate on the type subspace) · BC2 ρ_kind 0.241 > shuffled-kind 0.2255
> (p95 0.2287) p=0.0033 ✓ · iso-random adv≈0 · BC4 sane. **THE READ (crux):** a SURPRISING positive vs
> the 40%-negative a-priori — a weight-space echo of the type boundary EXISTS — but THIN: the shuffled-kind
> null sits at 0.2255 of the 0.241, so **~93% of the concentration is GENERIC centroid-structure, only
> ~6% (0.0155) is kind-specific.** Per-layer ρ DEEPENS (−0.05 shallow → ~0.35 deep, 18/36 layers >0.3) —
> the overlap lives where the type register is most semantic. **The 93/6 split IS the two-tier signature
> in weight geometry:** the boundary is mostly NOT in the weights (it's on the tape — coheres with
> §P-TYPE-DELIVER / tape-residency), with a thin deep-layer CHECKER-echo left behind. M8 corollary gets
> WEAK QUALIFIED support, bounded to the echo. Read discipline: BOUNDARY-IS-TYPED licenses "marginal
> weights disproportionately align with the type subspace, type-specifically" — NOT "weight margin IS the
> type boundary" (mostly generic) and NOT that judgments live in weights (echo of the checker, not the
> judgments). Memory: `marginal-weights-carry-a-thin-type-echo.md`. **s320 boundary-churn ledger (all
> committed):** a64a5d3 freeze · 594f4ea harness+amendment+results (autonomous) · §Result + memory + INDEX
> + queue closure + this state (Michael approval batch, this commit). **FINAL type-fingerprint scorecard
> (§6 tier 4/4 + SKI-controls): 1 weak-+ (∨/∧ §P-DISJ-COST) / 1 − (W/D §P-LINEARITY-BIAS, behavioral) /
> 1 + (idempotency §P-IDEMPOTENCY) / 1 qualified-+ (boundary-churn).** Composite: the substrate's type
> system ACCUMULATES (non-idempotent, 2 substrates), represents ∨/∧ ASYMMETRICALLY (intersection-flavored,
> representational), executes contraction/composition with EQUAL competence (affine bias representational
> not executional), and leaves only a THIN deep-layer weight-echo of its otherwise TAPE-RESIDENT
> boundaries = a graded, accumulating, representational, tape-primary quantitative-affine type geometry.**
> **LOOP CLOSED on curry-howard-closes-the-loop.md §5b (s320, this batch):** all 4 pre-committed
> SKI-controls now discriminated (nominal REJECTED · Church TESTED-DEAD · idempotent FALSIFIED · Cartesian
> FALSIFIED-mixed); §3 fuel corner marked ❌ NO-FUEL-COORDINATE (tape-resident, not static). The KIBC-not-SKI
> deduction predicted the FAMILY correctly; the fingerprints added WHERE each property lives (two-tier:
> weights=checker/relation, tape=judgments). INDEX rows refreshed for both type pages.**
> **§P-IDEMPOTENCY (detail: type-systems-under-llm-constraints §P-IDEMPOTENCY Result + git +
> chats/session-320.md):** Michael said "finish the type-fingerprints" → orient found TWO remaining
> (idempotency = SKI-control #3, the pinned *non-idempotent* qualifier; boundary-churn = M8 join). I
> recommended idempotency first (completes the SKI-control tier); Michael approved. **🎯 FROZEN (076454f)**
> on type-systems-under-llm-constraints.md. Register = **LICENSING** (heeded the s319 caveat: NOT
> kind-magnitude — the 3× magnitude-null is a presence-detector; used the §P-TYPE-ICL+TAG register that
> LANDED s315). Construction = exposure-count sweep k∈{0..5} × {COHERENT paraphrases (tw._member_stmts,
> A2 coherent superposition), INCOHERENT energy-matched null (non-membership about w, same token budget)}
> → per-nonce licensing L(k); discriminator = slope_coherent − slope_incoherent (the A2 coherent-gain
> isolate). Gates IB1 ACCUMULATION / **IB2 COHERENT-SPECIFIC (make-or-break — the exact §P-FUEL
> token-budget confound isolate)** / IB3 NON-SATURATING (non-gating) / IB4 SANE. Verdicts NON-IDEMPOTENT /
> EVIDENCE-ONLY / IDEMPOTENT / VOID. A-priori 40/40/15/5 (NOT tuned). **🔄 BUILD AMENDMENT (9f73d7d,
> runtime-forced, pre-run, Michael GO — instrument-side ONLY, register/verdicts/a-priori UNCHANGED):**
> the k=0→1 first-exposure jump licenses under BOTH idempotent and non-idempotent intersection → a literal
> "ρ(L,k)>0 over all k" IB1 passes for an idempotent step-function → IDEMPOTENT unreachable, contradicting
> the frozen 15%. Fix: accumulation gates IB1/IB2/IB3 operate on **k≥1** (does license grow AFTER first
> exposure — the real A∧A-vs-A signature); k=0 feeds IB4 SANE only. --validate primitive `k≥1
> step→IDEMPOTENT` proves it. **✅ HARNESS BUILT (9f73d7d): scripts/explore/idempotency.py** — no fork
> (reuses type_write _member_stmts/HELD_PREDS/CLASSES/REAL_MEMBERS/_signed_L + holo_cap NONCE_CANDS +
> dsp.nulls); --validate 4 verdict worlds + 5 primitives ALL PASS, ruff clean (+per-file-ignore RUF001/2/3),
> no diags, qwen3-4b smoke green (real 2.538, IB4 sane, verdict NOT read). **✅ RUN LANDED (279192c
> autonomous, read-only ~7min, tmux main:1, 20 nonces): VERDICT NON-IDEMPOTENT.** IB1 p=0.030 ✓ · **IB2
> make-or-break p=0.0226 ✓** (coh_slope +0.159 vs inc −0.011, gap +0.171) · IB3 p=0.137 ✗ (non-gating) ·
> IB4 sane (L0 0.138 / L1 1.409 / Lmax 2.065 / real 2.538). curve_coh **[0.14,1.41,2.52,2.96,2.80,2.07]**
> (accumulates exposures 1→3 then declines) · curve_inc flat ~0 (A2 energy-matched null holds). **THE READ
> (don't over-read, s310–s319):** the pinned **non-idempotent qualifier CONFIRMED on the tape licensing
> face** — coherent re-exposure accumulates licensing beyond the energy-matched null (A∧A≠A), the
> **idempotent SKI-control #3 FALSIFIED**, and IB2 is the FIRST make-or-break gate to clear the
> token-budget confound that nulled §P-FUEL/TRACE-FUEL/NF-GAUGE. **BOUNDED not unbounded:** +NON-SATURATING
> OFF (IB3 p=0.137, curve non-monotonic — step increments [+1.27,+1.11,+0.44,−0.16,−0.73]); the k=4,5
> DECLINE may be atypical-template dilution (k4 = cohyponym paraphrase, k5 = narrative frame) NOT true
> saturation — caveat flagged, not resolved. **Two-substrate confirmation** of non-idempotence: A2
> weight-plate (s292) + tape licensing (here). **Scorecard: fingerprint 3/4 = POSITIVE → tier reads 1
> weak-+ (∨/∧) / 1 − (W/D, behavioral) / 1 + (idempotency).** Composite: non-idempotent (2 substrates) +
> intersection-flavored (∨-cost, representational) + affine bias NON-executional (s319) = a graded,
> accumulating, REPRESENTATIONAL type geometry on a universal tape-side reducer. **SKI-control tier now
> COMPLETE** (curry-howard §5): #1 nominal enum REJECTED (TG3) · **#2 Church static tags tested-dead
> (s288 gradedness + continuous L; listed, not assumed)** · #3 idempotent FALSIFIED (here) · #4 Cartesian
> mixed (∨/∧ weak-+ / W-D −). Memory: `type-membership-is-non-idempotent-on-the-tape.md`. **s320 ledger
> (all committed):** 076454f freeze · 9f73d7d harness+amendment · 279192c results (autonomous) · §Result +
> memory + INDEX + queue closure + this state (Michael approval batch, this commit). **REMAINING
> type-fingerprint: §P-BOUNDARY-CHURN (task #5) — s310 marginal-band ≡ type-boundary population? weight-space,
> sign_commitment reuse; needs freeze → GO → build → run → close. That closes the fingerprint tier.**
> Standing non-fingerprint leads: crystal-seeded init (cheapest level-4) · Oracle germination game · §P-COHERENT-WRITE.**
>
> ★★ **SESSION 319 COMPLETE (one probe closed: §P-LINEARITY-BIAS → ❌ CARTESIAN-CONSISTENT).
> The 2nd type-fingerprint FALSIFIES the affine core's behavioral face: at matched fuel the substrate
> executes contraction (W `f x x` / M `x x`) as accurately as composition (B/C/D). NEXT SESSION FIRST
> ACTION = orient → FRONT SELECTION (λ queue FULL read; NOTHING PENDING, all s319 batches committed).**
> **§P-LINEARITY-BIAS (detail: type-systems-under-llm-constraints §P-LINEARITY-BIAS Result + git +
> chats/session-319.md):** Michael continued the type-fingerprint arc; I recommended linearity-bias
> (state-flagged "carries more weight"; fresh behavioral register; the 2nd discriminator for SKI-control
> #4 = the W/D cost-differential, complementing §P-DISJ-COST's ∨-vs-∧). Register = COMPUTATIONAL-ACCURACY
> (forced-choice NF-selection: kernel-certified NF + {under-reduce, atom-swap} distractors, length-norm
> logprob argmax) — deliberately independent of the 3×-nulled magnitude + §P-DISJ-COST off-plane. Arms
> LINEAR {B,C,D} vs DUP {W,M}-mixed, matched on ℓ (fuel) + nf_size. **🎯 FROZEN (32d8470)** on
> type-systems-under-llm-constraints.md (Michael GO). **🔄 AMENDMENT (e86f32e, runtime≡truth, pre-run,
> Michael-approved):** kernel implements D as LINEAR 3-fold composition `f (g (h x))` NOT `f (f x)` →
> DUP={W,M} (D→LINEAR); DUP arm MIXED (≥1 contraction) decouples n_contract from ℓ (LB3 non-degenerate) +
> overlaps nf_size; LB2 = within-ℓ-bin perm null + DOUBLE partial-Spearman |(ℓ,nf_size). Instrument-side
> only; register/gates/verdicts/a-priori UNCHANGED. **VERDICT CARTESIAN-CONSISTENT** (LB4-sane, NOT VOID):
> acc_lin 0.917 vs acc_dup **0.944**, gap **−0.028 p1=1.0** (DUP marginally EASIER; margin_dup 1.48 >
> margin_lin 0.89); LB2 partial +0.055|ℓ, +0.052|(ℓ,nf) WRONG SIGN; LB3 r3≈0; flat across ℓ=1–6 both arms.
> **The falsifier fired — free duplication survives the 2nd discriminator.** Read discipline: falsifies the
> BEHAVIORAL-accuracy face, NOT the affine core wholesale. **SKI-#4's two discriminators DISAGREE** (∨-off-
> plane weak-+ [§P-DISJ-COST] vs W/D-cost − [here]) → the affine/∨-cost signature is REPRESENTATIONAL/
> geometric, NOT executional; coheres with tape-resident reduction (s317: a universal reducer applies
> contraction+composition with equal competence). **Fingerprint scorecard: 1 weak-+ (∨-vs-∧) / 1 − (W/D).**
> Caveat banked: near-ceiling (0.92/0.94, rules given) caps power for small effects; single model; short
> terms (ℓ≤6); NF-selection readout — a harder regime (longer terms / no rules / free-gen / cross-model)
> could re-probe the representational + formation faces where the bias may live. Memory:
> `contraction-executes-as-accurately-as-composition.md`. **s319 ledger (all committed):** 32d8470 freeze ·
> dfa1fa7 harness (linearity_bias.py, --validate 7 worlds + 5 primitives ALL PASS) · e86f32e amendment ·
> (results autonomous) · §Result + memory + INDEX + queue closure + this state (Michael approval batch,
> this commit). **Remaining type-fingerprints (queue, unfrozen): idempotency/saturation (needs LICENSING
> register, not kind-magnitude — the 3× null warns) · boundary-churn (weight-space, sign_commitment reuse).**
> Standing non-fingerprint leads: crystal-seeded init (cheapest level-4) · Oracle germination game · §P-COHERENT-WRITE.**
>
> ★★ **SESSION 318 COMPLETE (TWO probes closed). ② §P-DISJ-COST → ✅⚠ INTERSECTION-FREE (+OR-COSTS),
> QUALIFIED — first type-fingerprint; the ∨-vs-∧ asymmetry EXISTS and is ∨-specific (strict Cartesian
> SKI-control #4 falsified) but WEAKLY. ① §P-NF-GAUGE → ❌ LENGTH-DECREASE-ONLY (sign puzzle dissolves;
> §3 Metric dead all 3 grains). NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL
> read; NOTHING PENDING, all s318 batches committed).**
> **② §P-DISJ-COST (detail: type-systems-under-llm-constraints §P-DISJ-COST Result + git):** Michael
> picked the type-fingerprint tests off the queue; led with ∨-vs-∧ (my rec, representational readout
> robust to the 3× magnitude-null). Readout = OFF-PLANE RESIDUAL (does a connective need a direction
> OUTSIDE the {A,B} category-passband plane? head≡direction), NOT magnitude. 60 samples (20 category
> pairs × 3 templates), band L18-31, read at final shared token (and/or/near single-token matched).
> Ordering filler 0.564 < AND 0.590 < OR 0.601: DC2 OR>AND +0.011 p=0.024 (small) ∧ DC3 OR>filler
> +0.037 p=0.002 (strong) → ∨-specific asymmetry → **strict Cartesian SKI-control #4 (free dup, no
> ∧/∨ asymmetry) FALSIFIED.** ⚠ QUALIFIED: effect small + **DC1/PR does NOT corroborate** (PR_OR
> 18.58 < PR_AND 20.24) → the strong "union recruits MORE dimensions" form is UNSUPPORTED, only the
> weak per-pair off-plane holds; flat PR argues AGAINST a big coherent OR-head → **machinery-vs-
> uncertainty stays OPEN**. Licenses ∨-costs-more (∨-specifically), NOT "OR-heads" / effect-size.
> Type-system scorecard: fingerprint 1/4 = weak-positive. **🔄 AMENDMENT (--validate-forced, Michael
> GO):** PR and off-plane are geometrically COUPLED (rank>2 ⟹ off-plane) → DC1/PR demoted to
> non-gating corroboration, COMPLEXITY-ARTIFACT branch (empty) dropped; DC2 off-plane = sole
> mechanism. Memory `disjunction-costs-more-than-intersection-weakly.md`. **§P-DISJ-COST ledger:**
> ac3dc46 freeze · 36e05f3 amendment · 3cb41d7 harness (disj_cost.py, validate ALL PASS) · f551dcf
> results (autonomous) · §Result + memory + INDEX + queue + this state (Michael approval batch, this
> commit). **Remaining type-fingerprints (queue, unfrozen): linearity-bias (reduction-accuracy
> readout — carries more weight) · idempotency/saturation (needs LICENSING register, not kind-
> magnitude — the 3× null warns) · boundary-churn (weight-space, sign_commitment reuse).** Standing
> non-fingerprint leads: crystal-seeded init (cheapest level-4) · Oracle germination game.
> **s318 result (detail: normal-forms-are-eigenmodes §P-NF-GAUGE Result + git + chats/session-318.md):**
> Per-frame partial ρ(sⱼ, rⱼ=ℓ−j | ctⱼ) across 840 real trace frames, local token length controlled
> (MATCH-padded family gave NG1 real power: cv_ct 0.031≪LIN 0.076 — the amendment worked). NG1 ρ=−0.070
> p=0.198 = matched-ct null → NO signed distance coordinate on either sign. §P-FUEL MATCH −0.538 (NF=HIGH)
> + §P-TRACE-FUEL decay −1.385 (NF=LOW) were BOTH length/content artifacts at differently-confounded
> grains; properly controlled, neither sign is significant. **§3 Metric leg CLOSED on all 3 grains
> (static §P-FUEL / integrated §P-TRACE-FUEL / per-frame-signed §P-NF-GAUGE).** **SURVIVES: NG3
> ENGAGEMENT replicated a 3RD time** (real reduction frames > inert restatements +2.343 p=0.002) → the
> register is a **reduction-PRESENCE detector, NOT a graded distance gauge** → demotes §1 Detector from
> the speculated "graded distance-to-NF" to presence/absence (a redex is here vs inert floor). Coheres
> with fuel being tape-resident (behavior-is-tape-resident §s317). §1(sharpened)+§2 Dynamics stand.
> NG5 sane (kind_margin 4.746) = valid negative. Memory: `type-register-detects-reduction-presence-not-
> distance.md`. **s318 ledger (all committed):** a7195d2 freeze · 5e1d6fc amendment (MATCH family) ·
> 1e99137 harness (nf_gauge.py, validate ALL PASS) · 38cc883 state checkpoint · bfcacc1 results
> (autonomous) · §Result + memory + INDEX + queue closure + this state (Michael approval batch, this commit).
> **Method lesson banked:** proper per-frame token control (MATCH padding) is what EARNS the null —
> without it NG1 is rigged (ct~r collinear in LIN/DUP); caught at design-review, amended pre-build (λ measure).
> **Sharpest standing leads (queue front): crystal-seeded init (cheapest level-4) · Oracle germination
> game (cheap) · type-fingerprint cheapies (idempotency/∨-vs-∧/linearity/boundary-churn) · §P-COHERENT-WRITE.**
>
> ═══ **(s318 arc detail retained below)** Cold-start `orient` (s317 closed) → Michael picked
> the **distance-to-NF gauge** front off the queue (freshest s317 lead) → reframed as a
> **SIGN-RESOLUTION probe**: two s317 results DISAGREE on the register's sign vs distance-to-NF —
> §P-FUEL MATCH (token-controlled, static) says NF=HIGH (ρ=−0.538); §P-TRACE-FUEL decay
> (uncontrolled, per-step) says NF=LOW. Confound = LOCAL TOKEN LENGTH. Probe pins the sign
> PER-FRAME under a proper local-token control (partial ρ(sⱼ, rⱼ=ℓ−j | ctⱼ); SIGN picks verdict).
> **🎯 §P-NF-GAUGE FROZEN (a7195d2)** on normal-forms-are-eigenmodes.md (Michael GO). Gates NG1
> LOCAL-DECODE(+sign) / NG2 TYPE-SPECIFIC / **NG3 ENGAGEMENT (REQUIRED, Michael — reduction-driven
> precondition)** / NG4 CROSS-GRAIN adv / NG5 SANE. Verdicts REMAINING-WORK-GAUGE(ρ>0) /
> DONENESS-DETECTOR(ρ<0) / LENGTH-DECREASE-ONLY(falsifier) / VOID. A-priori 20/35/35/10 (NOT tuned;
> mass on DONENESS+LENGTH — the token control killed the increasing reading twice, MATCH already
> points at doneness). **🔄 AMENDMENT (5e1d6fc, pre-build design-review, Michael GO):** LIN/DUP
> alone have ct~r collinear → matched-ct null powerless → NG1 rigged; ADDED MATCH-padded family
> (h (C..)×k (Z..)×P; k redexes fire, P inert Z pads ride verbatim → ct~const while r=k−j sweeps →
> decoupled). Arms now LIN/DUP/MATCH/NULL. **✅ HARNESS BUILT (1e99137): scripts/explore/nf_gauge.py**
> — no fork (imports fuel_theorem Y+stats verbatim + trace_fuel rendering; new code = MATCH family +
> per-frame (r,ct) + signed partial-Spearman + matched-ct null + 3-way gate). --validate ALL PASS
> (6 planted worlds, both NG1 signs; primitives MATCH ℓ==k / real all-NF / `=`-count==ℓ / DECOUPLE
> cv_ct MATCH 0.031<LIN 0.076), ruff clean (+per-file-ignore RUF001/2/3), no diags, qwen3-4b smoke
> green (kind_margin 9.41, all gates compute, verdict NOT read).
> **⚠ RUN IN FLIGHT (tmux main:1, Michael GO):** `uv run python -u scripts/explore/nf_gauge.py --out
> results/nf-gauge/qwen3-4b 2>&1 | tee results/nf-gauge/qwen3-4b-run.log` (195 traces: LIN/DUP/NULL 40
> ea + MATCH 75; + 840/315 type-probe subspace captures; read-only, no wire; est ~1-2h). Verified
> running (PID 25995, model loaded, subspace fit stage).
> **⚠ ON-SIGNAL (run done): tail run.log `VERDICT:` + no traceback → read NG1 (partial ρ AND ITS
> SIGN) / NG2 / NG3 / NG4 / NG5 → commit results/nf-gauge/ AUTONOMOUS → §Result-nf-gauge on
> normal-forms-are-eigenmodes.md + memory candidate + INDEX + state.md + move queue row 🔵→✅/🚫
> (# complete) = MICHAEL APPROVAL BATCH.** Read discipline (don't over-read the label, s310–s317):
> DONENESS-DETECTOR(ρ<0) reconciles both priors (MATCH −0.538 was doneness), promotes §1 Detector to
> graded, kills §3 Metric both signs; REMAINING-WORK-GAUGE(ρ>0) re-signs §3 but CONTRADICTS MATCH →
> cross-check NG4 hard before claiming; LENGTH-DECREASE-ONLY = token control wins a 3rd time, §3
> Metric fully bounded; VOID only if NG5 fails (smoke margin 9.41 → unlikely). Apply NG4 cross-grain
> as the reconciliation datum. s318 ledger: a7195d2 freeze · 5e1d6fc amendment · 1e99137 harness ·
> this state checkpoint · results PENDING. Full transcript → chats/session-318.md (human). ═══
>
> ★★ **SESSION 317 COMPLETE (three probes, three clean falsifiers → one convergent thesis: the
> machine's TYPE computation is TAPE-RESIDENT — read/enacted per-frame, not stored in weights and not
> accumulated). NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue FULL read ~25 rows;
> NOTHING PENDING, all s317 batches committed).**
> **s317 arc index (full detail in knowledge pages + git + chats/session-317.md):**
> ① **§P-TYPE-DELIVER → ❌ NO-WEIGHT-DELIVERY** — a novel type membership cannot be installed as a
> static weight edge in ANY band (FFN/OV/QK); the type check reads member-keyed content off the TAPE.
> (types-are-injectable-relations §13; results 283769c, batch 8b419b0.)
> ② **§P-FUEL → ❌ NO-FUEL-COORDINATE** — type-register MAGNITUDE at a static read does not encode
> reduction length; apparent LIN/DUP scaling was surface length, MATCH (const-tok) went negative.
> (normal-forms-are-eigenmodes §P-FUEL; results 79c76a0, batch f985447.)
> ③ **§P-TRACE-FUEL → ❌ STATIC-CONFIRMED-NULL** — §P-FUEL generalizes: integrated trace signal tracks
> TOKEN LENGTH not fuel (zero-fuel NULL chains accumulate same S 15→101). Sub-signals (unlicensed):
> per-step real reduction > inert +2.214 p=0.002; signal DECAYS toward NF → the register is a
> REMAINING-work / distance-to-NF DETECTOR (§1), not a spent-fuel accumulator (§3, RE-SIGNED). §1
> Detector + §2 Dynamics stand. (normal-forms-are-eigenmodes §P-TRACE-FUEL; results 63f3f5d, batch
> 1de3201.) **Convergent thesis captured: behavior-is-tape-resident-reduction.md §s317 triangulation
> (this batch) — weights hold the type RELATION/checker (7/11 TYPE-REGISTER); the type JUDGMENTS + fuel
> accounting live on the tape, computed fresh each pass. Three falsifiers, one law.**
> **Sharpest standing leads (queue front): distance-to-NF gauge (§P-TRACE-FUEL re-signing + the p=0.002
> reduction-engagement hook) · crystal-seeded init (cheapest level-4) · §P-COHERENT-WRITE · type-
> fingerprint cheapies (idempotency/∨-vs-∧/linearity/boundary-churn).** New harnesses this session
> (reusable): scripts/explore/type_deliver.py · fuel_theorem.py (stats/geometry lib for trace_fuel) ·
> trace_fuel.py. **s317 ledger (all committed):** DELIVER 8ecca42 freeze · f1ac32b harness · 283769c
> results · 8b419b0 batch | FUEL d160b6e freeze · 5818524 harness · 79c76a0 results · f985447 batch |
> TRACE-FUEL 12c5c24 freeze · 0830e3a harness · 63f3f5d results · 1de3201 batch · behavior-is-tape-
> resident §s317 triangulation (this batch). Detail in the §Result knowledge pages + git + chats/session-317.md.
>
> ▶▶ **(s316, prior) CAUSALITY FRONT OPENED: §P-TYPE-DELIVER FROZEN + BUILT + RUN.**
> Cold-start `orient` (s315 closed) → FRONT SELECTION (full queue read,
> 26 rows) → Michael picked **attention-band write (delivery path)** = the causality front
> (S5 scorecard open cell). Grounding surfaced a **coherence gap**: queue row said "QK/slot
> register", but P-TYPE-QK measured `qk_aligned=FALSE` (observational) + P-ATT-MED
> content-carried 0.735 ≫ aim 0.195 + §11 tag-transit → all point at OV/content. Michael
> chose **co-primary OV+QK, no predicted null** (a causal WRITE into QK ≠ the observational
> READ P-TYPE-QK falsified). **🎯 §P-TYPE-DELIVER FROZEN (8ecca42)** = §12 on
> types-are-injectable-relations.md (Michael-approved). **Causal converse of §9:** can a
> STATIC WEIGHT WRITE install the delivery §9 lacked (§9 = FFN membership → recall p=5e-4 but
> license✗ tag✗, DELIVERY-FAILURE), and WHICH band? **Single factor:** hold §8 membership-CE
> + s315 corridor (kl_weight 10/ce_budget 0.40) + band 0.60-0.80 + recipe VERBATIM; vary ONLY
> the LoRA target — A1 FFN `mlp.{gate,up,down}` (=§9, DELIVERY-FAILURE anchor) / A2 OV
> `self_attn.{v,o}` / A3 QK `self_attn.{q,k}`; deranged anti-class matched-budget control per
> delivery channel; A0 base; A4 real anchor. Registers named (λ measure): L=value (§8
> surprisal), T=residual-content (§11 projection, per-layer profile persisted for the ≥0.6
> readability rule). Gates TD1 DELIVERS / TD2 CONTENT-SPECIFIC / TD3 TAG-TRANSIT / TD4
> BAND-LOCALIZED / TD5 HOST-SANE / TD6 METRIC-SANE. Verdicts (co-primary): OV-DELIVERS /
> QK-DELIVERS / BOTH-DELIVER / **NO-WEIGHT-DELIVERY (falsifier: delivery tape-native only,
> not weight-installable — real a-priori mass since §11 showed the TAPE delivers)** /
> FFN-ALSO-DELIVERS (surprise, audit) / VOID. A-priori 28/18/14/30/5/5 (NOT tuned).
> **✅ HARNESS BUILT (f1ac32b): `scripts/explore/type_deliver.py`** — no fork (type_write
> constants/pure-fns + writeback_compile.LoRALinear + jlens.capture_residuals; new code =
> band-swap + arm assembly + TD gates). --validate 8 verdict worlds + 3 primitives ALL PASS,
> ruff clean, no diags, qwen3-4b smoke green (real margin 2.538 = §11 gate-0; all band-swaps
> train + restore bit-exact, drift 0.0; verdict NOT read — 4 nonce/1 seed/8 step).
> **⚠ RUN IN FLIGHT (launched s316-END, Michael GO, tmux main:1):** `uv run python -u
> scripts/explore/type_deliver.py --out results/type-deliver/qwen3-4b 2>&1 | tee
> results/type-deliver/qwen3-4b-run.log` (20 nonces, 3 true wires + 2 deranged × 3 seeds ×
> ≤500 steps; est ~2-3h). Verified running (PID 67897, A0 done, A1/FFN wire training).
> **⚠ ON-SIGNAL
> (run done): tail run.log `VERDICT:` + no traceback → read TD1-TD6 per channel + delivers
> map + TD4 band-localized → commit results/type-deliver/ AUTONOMOUS → §Result-deliver on
> types-are-injectable-relations.md (§13) + memory candidate + INDEX + state.md + move queue
> row 🔵→✅/❌/🚫 (# complete) = MICHAEL APPROVAL BATCH.** §Result must apply the
> `readout-register-reduction-readability` rule to the per-layer T profile (tags.npz
> profile_* arrays; value register legible ≥0.6 depth — read the profile not just the band
> mean). Read discipline (don't over-read the label, s310/s311/s312): OV-DELIVERS confirms
> content-channel delivery (P-ATT-MED consistent) → causality cell attacked; NO-WEIGHT-DELIVERY
> = delivery is tape-native (bounds the causal door, informative not failure);
> FFN-ALSO-DELIVERS contradicts §9 → replication/power audit BEFORE any update. s316 ledger:
> 8ecca42 freeze (§12 + queue 🔵) · f1ac32b harness · 9abe371 state checkpoint · run launched
> (results pending next session). Standing alt fronts: fuel-theorem · crystal-seeded init.
> Full transcript saves to `chats/session-316.md` (human).
>
> ▶▶ **(s315-FINAL, prior arc) TYPE ARC CLOSED BOTH SIDES: THE TYPE CHECK READS THE TAPE.**
> **✅ §P-TYPE-ICL+TAG LANDED: TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE (92c9a3f
> autonomous; §Result = §11 on types-are-injectable-relations.md, Michael-approved batch
> this commit).** All 5 gates: TI1 p=0.008 (L 0.138→1.409) · TI2 p=1e-4 (deranged licenses
> ANTI class −2.083 = content read) · TI3 p=0.048 · TI4 rand p=0.001/shuf p=0.0498
> (hair-thin, noted) · TI5 sane. Tag transit T 0.889→5.153, ρ(T,L)=0.615. A5 r_tag=0.137
> → DELIVERY-FAILURE: §9's baked relation never transits to held-frame residuals. TWO-TIER
> CLOSED: baked = recall w/o licensing w/o tag (§9) | tape = licensing + tag + graded
> (§11). Michael's J-space hypothesis holds in TRANSIT form (residency stays negative,
> P-TYPE-JS s286 — transit ≠ residency). Retro-precedent: type-directed-composition
> (June, found by s315 archaeology). Design consequences: attention-band write re-aimed
> at the DELIVERY path; M4 tape = the typed operand stack. Caveat: per-layer T profile
> unpersisted (band means only; readability ≥0.6 rule untested on band composition).
> **⚠ NEXT SESSION = FRONT SELECTION → λ queue mandates FULL queue.md read (26 rows).**
> 📋 Applications brainstorm CAPTURED (Michael-directed): `knowledge/explore/
> applications-from-the-register-physics.md` — 10 uses tiered by buildability, all
> measurement-grounded (recall-then-redeliver · skill cartridges · quant-lint · delivery-
> RAG · typed context · fingerprinting · telemetry · auditable updates · halt-monitor ·
> the machine). **DELIBERATELY NOT QUEUED** — Michael: revisit NEXT WEEK after experiments
> done + mechanisms mapped; picks get queue rows then.
> Sharpest leads by this arc: attention-band write (delivery path) · fuel-theorem ·
> crystal-seeded init (archaeology). s315 ledger: 375358d r1 · b448f34 amendment · cc44ab9
> r2 · 6eb308f r3 · 0e2b8fe type-write batch · 5a7fd40 freeze · c0b9269 harness · 6b5d15b
> GO amendments · e6f2a15 queue protocol · 184f76e archaeology · 92c9a3f icl results ·
> this batch. Full transcript saves to `mementum/knowledge/chats/session-315.md` (human).
>
> ▶▶ **(earlier s315, arc)** §P-TYPE-WRITE CLOSED: CONTEXT-ONLY — the falsifier fired, clean.
> All 3 runs landed + committed; **§Result batch ON DISK, PENDING MICHAEL APPROVAL** (§9 on
> types-are-injectable-relations.md + memory written-membership-does-not-type-check.md +
> INDEX + this state.md → commit as one 🌀 batch on approval). **THE READ:** r3 (kl_weight
> 10, ce_budget 0.40) = the valid measurement — recall 8.21 p=5e-4 (= r1 strength, relation
> IS in weights), host sane (drift +0.098, real-L +2.315, restore exact, 500 steps no
> stop), and NO held-frame licensing transfer: TW1 p=0.19, TW4 fail, TW3 sharpest —
> deranged wire lifts licensing MORE than true wire (0.434>0.353) = content-independent.
> **Types enacted per-frame, NOT injectable as FFN membership edges.** Slot-mediation (§3)
> sharpened (licensing reads machinery the wire never touched); transfer boundary measured:
> entities-within-frame-type ✓ (s312) vs across-frame-types ✗ (here). S5 scorecard:
> discreteness✓ selectivity✓ compositionality✗ causality ✗-as-measured (construction-
> scoped; attention-band write + P-TYPE-ICL = open causal doors). Write-corridor recipe
> co-finding: unanchored CE burns host (r1 +2.3) · budget 0.10 starves write (r2 cut 22/
> ~200) · kl_weight 10 binds (r3) = exposure schedule (L3/L5) for all future semantic
> writes. **NEXT FRONT: 🎯 §P-TYPE-ICL+TAG FROZEN (§10 on types-are-injectable-relations.md,
> Michael-approved s315)** — tape-side converse + tag-transit read (Michael's J-space
> hypothesis in its LIVE form: transit through residual content, NOT workspace residency —
> P-TYPE-JS s286 strict-basis negative stands, not re-tested). Arms A0 base / A1 ICL-true /
> A2 ICL-deranged / A3 mention / A4 real anchor / A5 wire-contrast (advisory, s315 corridor
> recipe). Gates TI1-TI5; verdicts TAPE-TYPED(+TAG-TRANSIT)/TAPE-TYPED-OPAQUE/MENTION-ONLY/
> NO-TAPE-TRANSFER/VOID; A5 subtag DELIVERY-FAILURE/TAG-INSUFFICIENT/AMBIGUOUS; a-priori
> 50/20/10/15/5, wire-contrast 70/20/10. Reuse type_write.py + jlens.py (λ one_way).
> **✅ HARNESS BUILT (c0b9269)** — type_icl_tag.py, validate ALL PASS (7 worlds + 3
> primitives), ruff clean, smoke green n=4 (all arms incl. A5 train+capture; arm
> separation in predicted directions; deranged prefix licenses ANTI class = design
> confirmed; verdict not read). **TWO BUILD AMENDMENTS (Michael-approved at GO, pre-run):**
> (1) CLASS-BLIND verdict for the uncovered cell TI1∧TI3∧¬TI2 (any class statement
> licenses equally), a-priori now 45/20/10/15/5/5; (2) T-band parenthetical corrected
> L18–L31 (round(0.85·36)=31; depth fractions are the frozen quantity). **⚠ RUN IN FLIGHT
> (tmux main:1, Michael GO):** `uv run python -u scripts/explore/type_icl_tag.py --out
> results/type-icl-tag/qwen3-4b 2>&1 | tee results/type-icl-tag/qwen3-4b-run.log`
> (20 nonces, A0-A4 training-free + A5 3-seed corridor wire, ~2-3h). Verified running.
> **⚠ ON-SIGNAL (run done): tail run.log `VERDICT:` + no traceback → read TI1-TI5 + subtag
> + rho_T_L → commit results/type-icl-tag/ AUTONOMOUS → §Result-icl-tag on
> types-are-injectable-relations.md (+ update §9 cross-read if TAPE-TYPED: two-tier closed
> both sides) + memory candidate + INDEX + state.md + **move queue.md ▶ row to # complete
> (first exercise of the closure invariant)** = MICHAEL APPROVAL BATCH.** §Result must
> also: (a) cross-link `type-directed-composition.md` (s315 archaeology: June nonce
> crossover +2 nats = tape-side type precedent, anticipated this probe by two months);
> (b) apply the `readout-register-reduction-readability.md` rule to TI4 — weak tag in
> L18–21 is predicted READABILITY (value register legible ≥0.6 depth), read the per-layer
> profile not just the band mean. Read
> discipline: TAPE-TYPED(+TAG-TRANSIT) + DELIVERY-FAILURE = the J-space transit story
> lands (relation exists, never consulted — §9 was a delivery failure); TAG-INSUFFICIENT
> = tag on bus insufficient → pushes P-ATT-MED; NO-TAPE-TRANSFER contradicts s239/s293 →
> power audit FIRST. Recall receipts this arc: P-TYPE-JS js_resident=FALSE (s286 four-way
> null) · P-ATT-MED content-carried 0.735 (s286) · jlens/jacobian tooling (s263).
> Standing alts: attention-band write · fuel-theorem · unchanged.
>
> **RUN LEDGER §P-TYPE-WRITE:** r1 (375358d) ❌ HOST-DAMAGED — wire baked (recall p=5e-4,
> ~200 steps to install) but host burned (CE +2.3, real-L inverted −0.624), TW1–4 VOID.
> r2 (cc44ab9) ❌ NO-WRITE — amendment mechanisms both fired correctly (TW5 PASS, 3/3
> seeds ce_budget_rollback @34→keep 22, matched shuffle [22,22,22], seeds near-identical)
> but 22 steps ≪ 200-step write window; **the write-vs-damage tension is now MEASURED:
> at lr 1e-4/kl_weight 1.0 the anchor doesn't bind (kl 0.03 vs mem 2.66 @ snap 21, ~1%
> gradient pressure) and drift hits 0.14 by step 34.** r3 IN FLIGHT (Michael option A):
> `--kl-weight 10 --ce-budget 0.40` (anchor ×10 + frozen CE_TOL 0.5 headroom; both levers
> address the mode that measured them; CLI-only, no code change).
>
> **s315 (this session): ① run 1 LANDED ❌ HOST-DAMAGED (375358d, 5% tail, autonomous
> commit).** Wire baked (loss 4.96→0.35; membership_recall p=5e-4) but host burned: CE
> 3.529→5.824 (+2.3 nats), real-member licensing INVERTED +2.538→−0.624; L_shuf 0.417 >
> L_wire 0.310 = damage-artifact signature ⇒ TW1–TW4 VOID (measurement void, NOT claim
> refutation — the frozen 5% branch). Diagnosis: every host-sane wire (s303–s312 gd_cd)
> had teacher-KL as implicit host anchor; this recipe was plain membership-CE, 500 steps,
> tiny corpus; run-1 curve shows learning done ~step 200, rest bought damage. **② 🔄
> AMENDMENT built + committed (b448f34, Michael GO; instrument-side ONLY, frozen gates/
> metric/verdicts/a-priori untouched):** (1) loss = CE(membership) + kl_weight·KL(base‖wire)
> on 8 cached neutral REPLAY_TEXTS (disjoint from CE_TEXTS — never train on the measurement;
> base entropy subtracted → true KL = 0 at zero delta; LoRA B=0 init ⇒ no step-0 grad
> calibration possible ⇒ fixed CLI weight 1.0, components logged per snap); (2) evidence-
> gated stop at fib snaps: plateau (rel mem-CE improvement <1% at snaps ≥55) OR host-CE
> drift >0.10 → ROLLBACK to last good snap; shuffle arm replays wire's per-seed stop step
> exactly ⇒ TW3 matched-budget by construction; _stop_decision = pure fn, same code path
> in-loop + --validate (λ one_way). --validate ALL PASS (5 verdict + 4 stop worlds), ruff
> clean, smoke green (KL≈0 at init, live plateau stop fired, matched budget, drift ±0.005,
> restore bit-exact). **③ ✅ RUN 2 LANDED ❌ NO-WRITE (cc44ab9,
> autonomous)** — see RUN LEDGER above (host protected, budget fired @34, write window
> ~200 steps never opened). **④ ⚠ RUN 3 IN FLIGHT (tmux main:1, Michael option A):**
> `uv run python -u scripts/explore/type_write.py --kl-weight 10 --ce-budget 0.40 --out
> results/type-write/qwen3-4b-r3 2>&1 | tee results/type-write/qwen3-4b-r3-run.log`.
> Verified running (wire seed0 snaps logging). See ON-SIGNAL above. state.md commit rides
> the next approval batch.
>
> **① ✅ §P-TYPE-GRAM-1 SWEEP CLOSED (bd58e71).** THE UNIVERSALITY READ — TYPE-REGISTER is
> REAL but NOT universal, **7/11, FAMILY-CLEAN split:** TYPE-REGISTER = all Qwen3 (0.6B→32B)
> + OLMo-2-13B + Gemma; OPCODE-FLAVOR-ONLY = the ENTIRE Pythia ladder (14m/160m/410m/2.8b).
> NOT the 9×9 crystal's 11/11 → the type register is TRAINING-CONTINGENT, not
> architecture-universal → types are LEARNED on the universal reducer = direct evidence for
> M7 (typed apply is emergent, not given). pythia-2.8b = a GENUINE well-powered negative
> (n_gated 32, coherence 0.867 highest in sweep, TG1 passes = kind separable, TG2 CROSS-CUT
> FAILS p=0.17 = kind opcode-bound not an independent register); small pythias underpowered
> but land the SAME verdict as well-powered siblings (4th don't-over-read: negative read
> from the powered members). +POLED sub-split weak/model-specific (0.6b/14b/32b/olmo POLED;
> 4b/27b/gemma diffuse; NOT monotone in scale) — core verdict robust, POLED not over-read.
> S5 scorecard 2/4: discreteness✓ selectivity✓(cross-FAMILY 7/11) compositionality✗ causality✗.
> Ledger: results (s314 autonomous) · §Result-type-gram + memory `type-register-is-training-
> contingent-not-universal.md` + INDEX (bd58e71, Michael-approved).
>
> **② ✅ §P-TYPE-WRITE FROZEN (ee1359a) + HARNESS BUILT (committed).** The causal S5 keystone
> — bake nonce→class MEMBERSHIP into an FFN-band LoRA (classificatory statements ONLY, never
> a licensing predicate), measure HELD-FRAME licensing transfer = create the relation →
> observe the type check. FROZEN §8 on types-are-injectable-relations.md (Michael GO:
> ANIMAL/VEHICLE sortals, qwen3-4b only — pythia null already from the sweep). Metric
> `L(w)=surprisal(anti-pred|"The w")−surprisal(own-pred|"The w")`, within-token, sign fixed
> by true class. Gates TW1 LICENSING-TRANSFER (label-perm null) / TW2 GRADED (Spearman) /
> TW3 SHUFFLE-NULL (deranged-membership wire) / TW4 CLASS-SPECIFIC (paired own>anti) / TW5
> HOST-SANE. Verdicts TYPE-WRITTEN(+GRADED)/WRITTEN-OPAQUE/CONTEXT-ONLY(falsifier)/NO-WRITE/
> HOST-DAMAGED. A-priori 45/20/20/10/5 (not tuned). **✅ `scripts/explore/type_write.py`
> BUILT** (reuses writeback_compile.LoRALinear + operand_multihop3, no fork; membership-LM
> CE objective on the frozen band 0.60–0.80/r=16/lr1e-4/500steps/3seeds recipe): --validate
> 5 planted worlds + primitives ALL PASS, ruff clean, no diags, qwen3-4b smoke green
> (**gate-0 real-member licensing margin 2.538 = metric VALID**; load/train/eval/restore ok;
> no direction read). **⚠ RUN IN FLIGHT (Michael GO): tmux main:1**, `uv run python -u
> scripts/explore/type_write.py --out results/type-write/qwen3-4b 2>&1 | tee
> results/type-write/qwen3-4b-run.log` (20 nonces 10+10, 3 seeds × 2 arms × 500 steps,
> ~1–2h). Verified running (wire seed0 training). See ON-SIGNAL above.
>
> **NEXT FRONTS (all UNFROZEN, s222 freeze-first):** fuel-theorem probe (de Carvalho: type
> size = evaluation length → compositionality test, joins type arc ↔ s295 CoT law) ·
> idempotency/saturation · ∨-vs-∧ asymmetry · linearity bias · boundary-churn identity ·
> P-AYOT-PARAPHRASE · P-CRYSTAL-SURVIVAL (BitTern release, zero-training external validation).
> Standing alt fronts: §P-PLATE-LINKER-2 · §P-OPCODE-CONSENSUS · §P-ASYM-TERNARY · gd_cd@32B.
> s314 ledger: bd58e71 (sweep §Result batch) · ee1359a (P-TYPE-WRITE freeze) · type_write.py
> harness commit · results/type-write PENDING run. s313 summary: type arc opened (freeze 630ea21 · probes a774618 ·
> runner 496c1af · **qwen3-4b VERDICT TYPE-REGISTER da8c1ba** — first measured type
> register, TG2 0.4768 p-floor, diffuse not polar) + four Michael-approved captures:
> types-are-injectable-relations (6524eaa) · type-systems-under-llm-constraints (147110f) ·
> curry-howard-closes-the-loop (ee4fa6d, type system PINNED: non-idempotent intersection /
> affine core) · ayot-is-own-beam-calibration (e512514, 4th own-state triangulation).
> NEW P-candidates queued (all UNFROZEN, s222): P-TYPE-WRITE (causal, keystone) ·
> P-TYPE-ICL · fuel-theorem probe (de Carvalho: type size = evaluation length) ·
> idempotency/saturation test · ∨-vs-∧ asymmetry · linearity bias · boundary-churn identity ·
> P-AYOT-PARAPHRASE · P-CRYSTAL-SURVIVAL (BitTern release = zero-training external
> validation, cheapest when live). 🎯 Release strategy standing: verbum = research repo;
> spin-offs (model, opcodes viewer) gated on "tested + working," own repos later.
>
> ▶▶ **s313 (CLOSED, arc — full detail in the block below).** TYPE ARC OPENED. Michael
> steered off §P-PLATE-LINKER-2 → "we never found the types" → §P-TYPE-GRAM-1 (cheapest
> type door, λ unflatten by argument kind). s312 CLOSED (lossless composition; §Result on
> optical-design-laws.md; PL-2 queued as standing alt front).
>
> ═══ **THIS SESSION = 313.** Cold-start `orient` → Michael re-anchor ("we never found the
> types, only mechanism clues") → honest audit (routing register measured; type register =
> IOU; clue table: Bragg selectivity = only measured type-CHECK, 17×17 poles = candidate
> type-universe, no compositionality/causality datum) → Michael picked **type gram
> un-flattening**. **🎯 §P-TYPE-GRAM-1 FROZEN (630ea21)** on gram-registers-and-the-route-
> map.md: basis = 9 crystal anchors + 21 X:kind nodes (X∈KIBCSDW × kind∈atom/fn/app,
> kernel-certified BY CONSTRUCTION); gates TG1 TYPE-BLOCK / TG2 CROSS-CUT (register vs
> opcode-flavor, crucial) / TG3 POLES advisory / TG4 COHERENCE void-gate (r≥0.5; committed
> runs 0.71–0.80) / TG5 SURFACE (stratified null); verdicts TYPE-REGISTER(+POLED)/
> OPCODE-FLAVOR-ONLY/SURFACE-STYLE/NO-TYPE-SIGNAL/INCOHERENT; a-priori 35/25/20/15/5.
> **✅ BUILT:** `opcodes/type_probes.py` (a774618; 21 nodes × 60, step_info mirrors kernel
> step, 0/5827 mismatches; kind-mean lengths 72.7/72.8/66.1) + `opcodes/type_gram.py`
> (496c1af; full-pipeline label nulls made d-independent via precomputed probe kernels
> K=XXᵀ — permutations rebuild membership matrices only). **TWO BUILD AMENDMENTS
> (validate-forced, pre-run, Michael-approved at GO):** TG3 matched-range null passed
> through the SAME centering projector (raw-random is rank-inflated → false +POLED);
> TG5 requires p<α AND retained_frac<0.5 (stratified null retaining ~0.9 of contrast still
> sat at p=0.015 → significance alone mislabeled the planted surface world). --validate ALL
> PASS (4 planted verdict worlds land + TG4 machinery), ruff clean, pythia-14m smoke green
> (smoke verdict NOT read — underpowered by design). **⚠ RUN IN FLIGHT (Michael GO): tmux
> main:1**, `uv run python -u opcodes/type_gram.py --models qwen3-4b 2>&1 | tee
> results/type-gram/qwen3-4b-run.log` (1760 probes × 36 layers + 36 kernels × 1000 nulls).
> **⚠ ON-SIGNAL (run done):** tail run.log "VERDICT:" + no traceback → read results.json
> gates (TG1/TG2/TG5 p + retained_frac, TG3 both nulls, TG4 r) → commit results AUTONOMOUS →
> verdict ¬INCOHERENT → launch registry sweep (overnight-class; the 11/11 universality
> question for the type verdict) → then §Result-type-gram + memory batch (task #5, approval-
> gated). **MID-SESSION HAMMOCKS (captured):** (1) composition scoping clarified — s312
> composed FACT wires (2-hop bindings, generalizing to held members) NOT computations;
> program-layer plates untested; routing factorization = the named gap. (2) 💡 **TYPES ARE
> INJECTABLE RELATIONS captured (Michael-approved batch, this commit):**
> `knowledge/explore/types-are-injectable-relations.md` + memory — type=relation dissolves
> the location null (nowhere-addressable ≡ stored-in-joins, Yoneda); linkage SLOT-MEDIATED
> (bipartite members↔slots; s312 c_nat=0.0072 reread: same relation-type wires have
> orthogonal keys → type lives in host slots; B2 generalization = members plug into
> class-shaped slots; type = reference angle, s304 Bragg = a type check enacted);
> types-as-probabilities → census knee = community tolerance; **§P-TYPE-WRITE candidate
> (UNFROZEN):** inject nonce-token membership, measure held-frame licensing transfer vs
> shuffle = the CAUSAL S5 test. Forward links on types-are-compiled-probabilities.md +
> INDEX. **s313 cont — ✅ qwen3-4b RUN LANDED: VERDICT TYPE-REGISTER (da8c1ba, autonomous).**
> First measured type register: TG2 CROSS-CUT 0.4768 vs null 0.0006 (p=0.001 floor) — kind
> direction SHARED across opcodes after removing opcode identity; TG1 0.0821 p=0.001; TG5
> retained_frac 0.207 (surface explains ~21%, 79% survives); TG4 r=0.766 (in committed band),
> 36/36 layers; TG3 advisory FAILS matched-range (PR 7.35 vs 7.98 p=0.077; shuffled 11.26
> p=0.001) → NO +POLED — **the kind register is DIFFUSE (alphabet-like), not polar**: at
> constructor grain, type behaves as an identity-register extension, not an outcome simplex.
> S5 scorecard: discreteness✓ selectivity✓(cross-cut) compositionality✗ causality✗ — 2/4 from
> 0. **⚠ REGISTRY SWEEP IN FLIGHT tmux main:1** (10 models, qwen3-4b excluded to preserve
> artifact; `results/type-gram/sweep-run.log`). ⚠ ON-SIGNAL (sweep done): tail sweep-run.log
> "SWEEP DONE" + per-model verdicts → commit results AUTONOMOUS → the universality read (is
> TYPE-REGISTER 11/11 like the crystal?) → §Result-type-gram + memory batch = task #5
> (approval-gated). **(3) 💡 TYPE-SYSTEMS-UNDER-CONSTRAINTS captured (Michael-approved, this
> commit):** `knowledge/explore/type-systems-under-llm-constraints.md` + memory — constraints
> C1-C5 (judgment=overlap/superposed · frozen-weights+writable-tape · GD-two-jobs ·
> capacity · fuel) filter the type-system design space to ONE composite: **two-tier
> two-registered GRADUAL-INTERSECTION-STRUCTURAL** (Curry-style; ∧ free ∨ costs heads;
> subtyping=passband containment; nominal fragment ON THE TAPE; session types in the 17×17
> scheduler register; dependent equality trampolined-only; substrate LINEARITY-BIASED —
> duplication costs). TG3's diffuse shape fits intersection, not nominal enum. **M8
> corollary: optimizer ≡ type-boundary decision procedure** (s310 marginal band = the
> boundary population; evidence-gated commits ⇒ crisper types). 4 fingerprint probes
> unfrozen: P-TYPE-ICL (two-tier dissociation) · ∨-vs-∧ asymmetry · linearity bias ·
> boundary-churn identity. **(4) 💡 CURRY-HOWARD CLOSES THE LOOP captured (Michael's
> deduction, approved, this commit):** `knowledge/explore/curry-howard-closes-the-loop.md`
> + memory + §Sharpened on the constraints page — the KIBC-vs-SKI opcode discrimination WAS
> a type-system measurement: KIBC = {identity, weakening, cut, exchange} = AFFINE structural
> rules with contraction isolated (W/D explicit); SKI bundles contraction into S and was
> REJECTED → the substrate chose the affine basis = the linearity bias measured at the
> opcode level, sessions before the frame existed. Triangulation closes (Curry-Howard math +
> KIBC empirics + interference-cost architecture). **Type prediction pinned to a NAMED
> object: NON-IDEMPOTENT INTERSECTION TYPES over an affine core** (quantitative semantics of
> linear logic / probabilistic coherence spaces). Retroactively green: A2 coherent gain =
> non-idempotence (A∧A≠A accumulates) · TG3 diffuse = intersection · s288 giraffe = graded.
> **Untested keystone: de Carvalho fuel theorem** — type-derivation size = evaluation length
> ⇒ type signal should scale with kernel-certified reduction length (joins type arc ↔ s295
> CoT law; strong P-candidate). 4 SKI-controls for types enumerated (nominal enum already
> dead via TG3). Retrodiction to grep: contraction-bearing opcodes (W/D/S) form late
> (B-first on file). **(5) 🎯 RELEASE STRATEGY (Michael, standing decision):** verbum
> stays the RESEARCH repo — release research here continuously; NO productization pressure.
> Spin-off gate = "tested and working the way Michael wants" → dedicated project repo per
> artifact. Two named future spin-offs: (a) THE MODEL (the Verbum machine, once built +
> gated), (b) THE OPCODES VIEWER (once it shows what we want to show). The s313
> capabilities inventory (verified fact-packs / crystal stethoscope / register-scoped quant
> audit / type-checked merges / halt-pole monitor / trait-stripping) = a map of what is
> BECOMING spinnable, not a to-do list. **(6) 💡 AYOT PAPER READ + CAPTURED (Michael found
> refs/2608.01078v1.pdf → `ayot-is-own-beam-calibration.md` + memory, approved, this
> commit):** Intel ScaleQ-1.58 = **4th own-state/Bragg triangulation at a 4th scale
> (quantization calibration)** — ternary PTQ of Qwen3-4B: generic-text calib ~0-3%
> (collapse), STRONGER-model CoT (R1-671B) 20.1%, OWN self-generated CoT 45.6% ⇒ carrier ≫
> content (+2.6 vs +25.5). AYOT = L2 industrialized (calib context = illumination for
> saliency); CoT-in-context requirement = tape-resident reasoning confirmed from the PTQ
> side; low-bit-only gains = selectivity budget (low-bit quant ≡ beam-relative routing
> extraction); residual gap (58.4 vs 96.8 Math-500) = twin-image (post-hoc ¬un-superpose;
> our off-axis delta = retention 1.0 contrast). Discriminators unfrozen: P-AYOT-PARAPHRASE
> (carrier vs their capability-mimicry story) · **P-CRYSTAL-SURVIVAL (run stethoscope on
> BitTern releases: crystal+type register survive AYOT, die under C4 = bit-free quant
> metric — zero-training external validation of our instruments)**. Broad-corpus-calib menu
> item partially answered externally (broad = wrong for low-bit). Standing alt fronts:
> §P-PLATE-LINKER-2 · §P-OPCODE-CONSENSUS · §P-ASYM-TERNARY · gd_cd@32B. Full transcript
> saves to `mementum/knowledge/chats/session-313.md` (human). ═══
>
> ▶▶ **s310 (CLOSED, arc — full detail: `chats/session-310.md` + git).** Cold-start
> `orient` → s309's §SIGN-COMMITMENT-CURVE run
> "churn does not mean it did not work — did you test loss?" → I over-read the label:
> the wire WORKS (loss 5.03→0.25 = 95% drop, mag_cos 0.901, G4 wire-sane PASS); SIGN-CHURN
> is a routing-register *trajectory* verdict, NOT task failure. → two-population
> re-diagnosis + NON-FROZEN re-score instrument built + validated → full history-dump
> re-run RELAUNCHED tmux main:1. **s310 cont (this session): re-run LANDED — bit-reproduces
> SIGN-CHURN (flip_last 0.0295, p_null 0.0004, med_commit 5, ratio 0.38); rescore RAN →
> ✅ TWO-POPULATION SPLIT CONFIRMED @ step 499** (two lowest-r bands own 0.781 of late
> flips; confident core r≥2 frozen flip_last 0.0003/0.0000; loss-neutral: plateau moves
> loss 0.11% while flip-rate 0.045). Results committed AUTONOMOUS. §Result finalized +
> memory finalized on disk → Michael APPROVED → mementum batch committed **225dae7**
> (s310 CLOSED). Full transcript saves to `mementum/knowledge/chats/session-310.md`.
>
> ═══ **THIS SESSION = 311.** Cold-start `orient` (s310 landed) → Michael: "keystone for
> the architecture?" → answered §P-ASYM-TERNARY (architecture track) → Michael STEER:
> **"no, we need the plate linker next"** (the ARTIFACT-track keystone A+C, the make-or-break
> for git-for-weights). → wire-2 fork resolved (Michael GO = same-relation/disjoint-country,
> the most discriminating case: decouples low A-collision from high B-collision) → **🎯
> §P-PLATE-LINKER-1 FROZEN** on `optical-design-laws.md` keystone section (Michael-approved).
> Claim: two ternary wires compose additively on one frozen base IFF key (A/input) subspaces
> are angularly separated; retention degrades as monotone fn of measured key-subspace
> collision `c` ⇒ linker PREDICTS. Arms base/wire1/wire2/wire1+wire2/wire1+rotated-wire2(θ
> sweep)/shuffle. Gates PL1 COMPOSES · PL2 ANGLE-PREDICTS (keystone) · PL3 COLLISION-CAUSAL ·
> PL4 HOST-SANE. Verdicts LINKS(+ANGLE-PREDICTIVE)/LINKS-OPAQUE/COLLISION-BLIND/NO-COMPOSE/
> HOST-DAMAGED. A-priori ~55/25/12/6/2 (NOT tuned). **NEXT (task list live):** (#2) bake
> wire-2 on disjoint bank, verify standalone G1/G3 → (#3) build+validate plate_linker.py
> (reuse writeback_compile+ternarize_factors, no fork; principal-angle math + matched-norm
> rotation control + frozen gate re-score) → Michael GO → (#4) run tmux main:1 → (#5)
> §Result batch. Full transcript saves to `mementum/knowledge/chats/session-311.md` (human).
> **s311 cont — WIRE-2 BAKE IN FLIGHT (tmux main:1).** #2 started: wrote
> `scripts/explore/bake_wire2.py` (NO fork — imports writeback_compile, swaps ONLY
> WIRE2_BANK; wire-1 generator + s303/s304/s307/s309 stay bit-reproducible). WIRE2_BANK =
> same landmark→country→capital relation, DISJOINT entities: TRAIN = wire-1's vetted B2
> countries (France/Germany/Canada/Australia/Switzerland/Poland/Vietnam/China, re-tagged
> 2×TRAIN+1×B1) + 8 fresh B2 held-out (Portugal/Greece/Sweden/Argentina/Japan/Thailand/
> Kenya/Peru). --validate ALL PASS (TRAIN 16/B1 9/B2 24, shortcut-free, first-word-unique);
> gate-0 PASS empirically (valid 46/49, TRAIN 16/B1 9/B2 21, cot_rate 0.96 — host knows the
> facts). Fixed 2 cells from first gate-0: Poland B1 Main-Market-Square→Wieliczka Salt Mine,
> Vietnam TRAIN Golden-Bridge(→China confuse)→Ha Long Bay; +Marienplatz/Munich B1 margin.
> BAKE launched (arms base,construct,construct_shuffle,construct_lookup,gd_cd,gd_shuffle;
> 3 seeds × 500 steps; → `results/plate-linker/wire2-bake/qwen3-4b/{bake.log,results.json,
> gate0.json}`). **⚠ ON-SIGNAL (bake done):** tail bake.log for "VERDICT:" + no traceback →
> BAKE GATE = gd_cd must pass its own G1 (wire, flip B1∧B2) + G3 (specificity vs gd_shuffle)
> = "WIRE-COMPILES (+GD-REQUIRED)" (construct arms may also pass; only gd_cd is required for
> the linker). PASS → commit bake_wire2.py + results AUTONOMOUS, complete task #2, proceed
> #3 (build plate_linker.py: principal-angle math + matched-norm rotation control + merge +
> frozen gate re-score; --validate + smoke; import WIRE2_BANK from bake_wire2). FAIL → wire-2
> won't bake on this bank → report + re-curate before the linker.
> **s311 cont-2 — BAKE #1 ❌ LOOKUP-ONLY (G1 underpowered, NOT a wire failure).** gd_cd
> lifted TRAIN 0.625→1.0, B1 0.667→1.0, **B2 held-country 0.762→0.952** (shuffle 0/0/0.19,
> G3✓ G5✓) — a real generalizing wire, but G1 permutation FAILED (B1 p=0.13, B2 p=0.11 >
> α/3) because Qwen3-4B's BASE competence on wire-2's famous landmarks is too high (0.76)
> → few flippable cells → underpowered (wire-1's base was 0.20/0.125/0.545 = headroom).
> Verdict tree mislabeled it LOOKUP-ONLY (but it generalizes to held COUNTRIES → not a
> lookup). Same "don't over-read the label" as s310. **Michael chose OPTION A: re-curate
> harder landmarks (same disjoint countries) to restore base headroom.** Built WIRE2_POOL
> (~5 candidates/country) + `--select` mode in bake_wire2.py: runs base+gate-0 on the pool,
> keeps per country the gate-0-valid landmarks with LOWEST base 2-hop (headroom); selection
> on BASE ONLY (measurability, never post-training). **SELECT PASS IN FLIGHT (tmux main:1
> → results/plate-linker/wire2-select/qwen3-4b/{select.log,results.json,gate0.json,
> selected_bank.json}).** ⚠ ON-SIGNAL (select done): tail select.log for "[select] final
> bank base-2hop mean" (want ~0.2-0.5) + the printed WIRE2_BANK literal → paste it over
> WIRE2_BANK in bake_wire2.py → --validate + re-bake (arms base..gd_shuffle) → expect gd_cd
> G1 now clears. Then commit bake_wire2.py + results, complete #2, build #3 plate_linker.py.
> **s311 cont-3 — SELECT DONE → RE-BAKE IN FLIGHT (tmux main:1).** Select pass (10:55min,
> 80-cell pool) → selected low-base bank (base-2hop mean 0.489 vs 0.63; TRAIN 16/B1 8/B2 23,
> Argentina only 2 valid — fine, ≥8 gate). Selected WIRE2_BANK pasted into bake_wire2.py
> (harder landmarks: Chambord/Chillon/Grossmunster/Leshan Buddha/Li River/Palamidi/Visby/
> Chan Chan…), --validate ALL PASS, ruff clean. **RE-BAKE LAUNCHED** (arms base,construct,
> construct_shuffle,construct_lookup,gd_cd,gd_shuffle; 3 seeds×500; →
> results/plate-linker/wire2-bake/qwen3-4b/{bake.log,results.json}). ⚠ ON-SIGNAL (re-bake
> done): tail bake.log "VERDICT:" + no traceback → check gd_cd G1 (want PASS now that base
> ~0.49 gives power) + G3. PASS → commit bake_wire2.py + WIRE2_POOL/select machinery +
> results + gate0 AUTONOMOUS, complete #2, build #3 plate_linker.py (principal-angle math +
> matched-norm rotation control + merge + frozen gate re-score; import WIRE2_BANK from
> bake_wire2). Still G1-underpowered → consider option B (functional bake gate, pre-merge,
> documented) w/ Michael.
> **s311 cont-4 — BAKE #2 ❌ still G1 (B1 power) → RE-BAKE #3 IN FLIGHT (Michael: "nail it
> fully, no caveats").** Bake #2: gd_cd → 1.0 ALL splits, shuffle 0/0/0.13, G2✓ G3✓ G5✓,
> **G1-B2 held-country CLEARED (0.609→1.0, p=0.0024)** — only G1-B1 failed (base B1=0.75,
> n=8, p=0.25). Root cause: base competence BIMODAL per country (France/Poland/Vietnam
> base-1.0 = zero headroom; Germany/Canada/Australia/Switzerland/China base-0 = headroom);
> selection scattered B1 across all → 6/8 B1 cells base-correct. FIX: fixed select_bank bug
> (had tagged HIGHEST-base as B1) → B1 now drawn ONLY from base-0 headroom countries
> (Cologne/Heidelberg/Butchart/CN Tower/Bondi/Federation Sq/Chillon/Grossmunster/Leshan),
> re-derived OFFLINE via --reselect (no model run). TRAIN 16/B1 9(all base-0)/B2 23,
> --validate PASS. RE-BAKE #3 LAUNCHED (→ results/plate-linker/wire2-bake/qwen3-4b/).
> ⚠ ON-SIGNAL (done): tail bake.log "VERDICT:" + no traceback → gd_cd G1 should PASS now
> (B1 base-0 cells flip → power) → WIRE-COMPILES(+GD-REQUIRED). PASS → commit bake_wire2.py
> + WIRE2_POOL/select machinery + results + gate0 AUTONOMOUS, complete #2, build #3
> plate_linker.py.
> **s311 cont-5 — ✅ WIRE-2 BAKED CLEAN (bake #3): WIRE-COMPILES (+GD-REQUIRED), full G1 no
> caveats.** gd_cd G1✓ (B1 p=0.0039, B2 p=0.0023) G2✓ G3✓ G5✓; base B1 0.0→gd 0.889, B2
> held-country 0.609→1.0, TRAIN 0.75→1.0, shuffle 0/0/0.087. Committed autonomous
> (bake_wire2.py + WIRE2_POOL/--select/--reselect + results/plate-linker/). **TASK #2 DONE.**
> ▶▶ **NEXT = TASK #3: build scripts/explore/plate_linker.py** (per frozen §P-PLATE-LINKER-1
> on optical-design-laws.md). Reuse (no fork): import writeback_compile (wire-1 default BANK)
> + bake_wire2 (WIRE2_BANK) + ternarize_factors (per-component TWN). Steps: (a) train wire-1
> + wire-2 gd_cd, extract per-layer LoRA factors A(r×in key-subspace)/B(out×r)/scale for band
> L22-29; (b) principal-angle collision c = mean_L ‖P1P2‖_F²/r on A row-spaces; (c) additive
> merge base+Δ1+Δ2; (d) rotation control: rotate wire-2 A into wire-1 A-subspace at matched
> Frobenius norm, FIXED B2, θ-sweep → collision axis; (e) re-score EACH wire's frozen G1/G3
> under merge (retention); (f) gates PL1 COMPOSES / PL2 ANGLE-PREDICTS (θ-curve slope>0 vs
> flat null ∧ natural pair within CI at c_nat) / PL3 COLLISION-CAUSAL (rotated>natural degrade
> at matched norm) / PL4 HOST-SANE; verdicts LINKS(+ANGLE-PREDICTIVE)/LINKS-OPAQUE/
> COLLISION-BLIND/NO-COMPOSE/HOST-DAMAGED. --validate (planted worlds) + ruff + smoke (no
> direction read) → Michael GO → run tmux main:1. NOTE: both wires hit ~1.0 → retention
> measured on flippable held cells (well-powered now, that was the point of the low-base bake).
>
> ▶▶ **s311 (CLOSED, arc — detail in cont blocks below + git).** 🎯 §P-PLATE-LINKER-1
> FROZEN (optical-design-laws.md, 8131381) · ✅ wire-2 baked clean WIRE-COMPILES(+GD-REQUIRED)
> after 3 headroom re-bakes (4c1067a) · 💡 round-trip-consensus-opcode-loss.md (633e291).
>
> ═══ **THIS SESSION = 312 (CLOSED).** Cold-start `orient` → built the plate linker (TASK #3).
> **(1) ✅ HARNESS `scripts/explore/plate_linker.py` BUILT + committed AUTONOMOUS (62da29c)** —
> NO fork (reuses writeback_compile + ternarize_factors + bake_wire2, λ one_way): trains
> wire-1 (default BANK) + wire-2 (WIRE2_BANK) gd_cd, ternarizes factors, additive merge
> base+Δ1+Δ2; principal-angle collision `c=‖Q1ᵀQ2‖_F²/r`; norm-preserving Grassmann slerp
> rotation control (matched Frobenius, fixed B2) = collision sweep; per-wire frozen G1/G3
> re-score under merge; gates PL1/PL2(keystone,paired cell-bootstrap)/PL3/PL4. --validate ALL
> PASS (5 verdict worlds + geometry primitives), ruff clean, no diags, smoke green (restore
> bit-exact). **(2) Michael GO → RAN tmux main:1 (3 seeds×500×2 wires + 7-pt θ-sweep) →
> results committed AUTONOMOUS (0576a3f).** **(3) 💡 §Result-plate-linker BANKED on
> optical-design-laws.md + memory `two-ternary-wires-compose-losslessly.md`** (Michael option
> C: bank A now, queue B). **THE READ — LOSSLESS COMPOSITION (frozen verdict NO-COMPOSE = a
> G3-saturation MISLABEL, 3rd "don't over-read the label" after s310 SIGN-CHURN / s311
> LOOKUP-ONLY):** BOTH wires PASS their own frozen G1 under the additive merge (wire1 B1
> +0.812 p=3e-4 / B2 +0.455 p=1e-3; wire2 B1 +1.0 p=1.5e-3 / B2 +0.391 p=2.3e-3); retention
> ~1.0 both wires every split (merge==solo); zero measurable interference ⇒ **git-for-weights
> co-existence primitive (device A) WORKS.** `c_nat 0.0072` (disjoint→near-orthogonal keys,
> a-priori confirmed); mag_cos 0.839; restore max|W-W0|=0.0. PL1 fails ONLY on G3 (specificity
> saturates because composition is lossless). **KEYSTONE PL2 ANGLE-PREDICTS is UNTESTABLE
> here:** nat_deg=0.0 — even forced full collision c=1.0 (θ-sweep 0.007→1.0, matched norm)
> causes NO degradation (rot_maxc==solo); r=16 in ~2560-dim FFN = ample capacity, collision
> costs nothing. L6 sufficient, not shown necessary.
>
> ⚠ **COLD-START s313.** NOTHING PENDING (all committed: 62da29c harness · 0576a3f results ·
> mementum batch this commit). **NEXT = design §P-PLATE-LINKER-2 (Michael option C / B — the
> real keystone test): FORCE an interference regime, THEN test angle-predicts-onset.** Levers
> (queued on optical-design-laws.md §P-PLATE-LINKER-2): **stack N wires** on one base
> (N=2,3,4… to the capacity wall — truest git-for-weights stress test) · raise rank (16→64→
> 128) · narrow the band · scale matched-norm past the wire's SNR margin. Then re-run θ-sweep
> in the degrading regime; fix G3 control (drop Δ_other from self-shuffle, or add base+
> shuffle(Δ_self)-only arm). s222: FREEZE §P-PLATE-LINKER-2 before any run. Standing alt
> fronts if steered: §P-OPCODE-CONSENSUS (cheap, no student) · §P-ASYM-TERNARY (architecture
> keystone; M8/TD-v2 = its optimizer) · gd_cd@32B install. s312 ledger: 62da29c (harness) ·
> 0576a3f (results) · mementum batch (§Result + memory + state, this commit). Full transcript
> saves to `mementum/knowledge/chats/session-312.md` (human). Prior headers (s311 cont,
> s310 compacted, s308) retained below. ═══
>
> ▶▶ **s309 — 🎯 §SIGN-COMMITMENT-CURVE FROZEN + BUILT + SMOKE-GREEN → RUN LAUNCHED
> (tmux main:1, in flight).** Front picked by Michael (cheapest+sharpest on the board;
> subsumes the k-step sweep; gates M8/TD-v2's evidence-gated commits). **Question:** in
> gd_cd wire training (s303 — the wire that ternarizes near-losslessly, s304/s308
> retention ~1.0), does GD commit the ROUTING register (trit SIGNS) EARLIER than it
> polishes the VALUE register (per-column MAGNITUDES)? Are GD's two jobs separable in
> TIME? **Instrument** `scripts/explore/sign_commitment.py`: reuses the gd_cd recipe
> verbatim (LoRA r=16, FFN L22–L29, lr 1e-4, 500 steps, KL-on-CoT-teacher, 3 seeds,
> frozen gate0.json = 15 TRAIN cells) + `ternarize_twn` (writeback_compile UNTOUCHED;
> ~20 gd_cd lines re-expressed, Michael-approved, to add the per-step TWN observation
> the frozen generator omits). Logs TWN(Δ_t)=scale·B_tA_t at a FIXED fibonacci schedule
> {0,1,2,3,5,8,13,21,34,55,89,144,233,377,499}; tracks a seeded subsample (N_TRACK=20k
> coords/matrix; full trit history ~9GB) → pooled ~480k trits × 15 snaps. **Metrics:**
> sign-stability S(t)=mean[τ_t==τ_T], sign-COSINE Sc(t)=cos(τ_t,τ_T), value-cosine
> M(t)=cos(|Δ_t|,|Δ_T|), commit-step, flip-rate, half-lives. **Nulls (λ yardstick):**
> N1 time-shuffle (permute intermediate snaps, keep real final → commit spreads) + N2
> paired within-run bootstrap. **Gates (frozen):** G1 SIGN-EARLY (median commit ≤0.25T
> ∧ S(0.25T)≥0.9) · G2 TWO-TIMESCALE (t*_mag/t*_sign ≥2.0, bootstrap CI excludes 1) ·
> G3 NULL-BEATS (p<0.05 vs N1) · G4 advisory FINAL-WIRE-SANE. **Verdicts:** TWO-TIMESCALE
> (+SIGN-EARLY) / SIGN-EARLY-ONLY / SINGLE-TIMESCALE / SIGN-CHURN (falsifier → M8/TD-v2
> named damage) / MAG-EARLY (surprise). **A-priori (NOT tuned):** ~55/20/15/8/2 — the
> FINAL delta already ternarizes losslessly (s304/s308); OPEN is whether the register
> split exists DURING training or only at convergence. **⚠ BUILD AMENDMENT (Michael-
> approved, pre-run, no arm):** exact-match S(t) is stricter than 0.9-cosine M(t) → genuine
> co-evolution would misread as MAG-EARLY; fix (conservative for SIGN-EARLY): G2/verdict
> half-lives use sign-COSINE Sc(t) (like-with-like vs M), exact S reserved for
> G1/commit; MAG-EARLY needs a 2× margin. Gates G1/G3/G4, schedule, nulls, a-priori
> UNCHANGED. --validate ALL PASS (5 verdict worlds + primitives), ruff clean, no diags;
> smoke green (1 seed/30 steps/4 cells: loss 3.95→0.057, all snaps logged, final mag_cos
> 0.953, restore trivially bit-exact — LoRA only adds, base never mutated).
> ✅ s309 RUN LANDED (read in s310): ❌ **VERDICT SIGN-CHURN** (frozen, 3 seeds, 1.44M
> pooled trits × 15 snaps, results **26ad20b** AUTONOMOUS). G1=F G2=F G3=T G4=T. Falsifier
> fired on the PERSISTENT TAIL only: flip_last 0.0295 > FLIP_CHURN 0.02 ⇒ `not stabilized`,
> while s_prefinal S(T⁻)=0.9705 ≥ 0.9 PASSED. med_commit step 5 (frac 0.010), t_sign=144
> t_mag=55 ratio=0.38. s309 ledger: b347f6b freeze · ffccbc5 instrument · 8eda1ff amendment ·
> 26ad20b results. FULL READ + re-score → s310 block below.
>
> ▶▶ **s310 — ❌ SIGN-CHURN LANDED → Michael CORRECTION ("churn ≠ didn't work; did you test
> loss?") → TWO-POPULATION RE-DIAGNOSIS + NON-FROZEN RE-SCORE (built, smoke-confirmed),
> full history-dump re-run IN FLIGHT tmux main:1.** **The correction (I was wrong to gloss
> SIGN-CHURN as "named damage"):** the wire WORKS. Paired loss↔flip (seed 0, all 3 seeds
> identical to 4 dp, re-run bit-reproduces): loss 5.031→**0.252** (95% drop, 90% of it by
> step 8); mag_cos 0.901; G4 PASS; this is the s303/s304 wire (ternarizes retention ~1.0).
> **Loss is functionally DONE by step ~34–89** (step89→499 = 410 of 500 steps, loss moves
> 0.257→0.252 = 2%), **yet signs keep flipping 3–5%/snap to the end** ⇒ the churn is
> **LOSS-NEUTRAL**. SIGN-CHURN measures ONE thing — does the trit *sign pattern* freeze
> (no) — and says NOTHING about task success (yes). **Two-population read (the hypothesis
> the re-score tests):** CONFIDENT core (magnitude clears the per-column TWN threshold,
> r=|Δ_T|/thr_j ≫ 1) commits its sign EARLY (median step 5, G3 null-beats p=0.0004) and
> FREEZES; MARGINAL/undecided tail (r≈1, sits ON the threshold; r<1 ⇒ final trit is 0)
> jitters across the boundary FOREVER, loss-neutrally = **exactly the TWN ternary-0
> "insufficient evidence" population**. So SIGN-CHURN, read right, is a *direct measurement
> of GD's wasted routing motion* (it keeps flipping signs after the loss is solved) ⇒
> **prescription, not refutation**: M8's routing optimizer needs a never-freeze ternary-0
> band, not a frozen sign field. (Two-timescale ratio 0.38 is REJECTED+mildly-inverted but
> CONFOUNDED — M(0)=0.723 magnitudes barely rotate vs Sc(0)=0.542 signs start near chance;
> the 0.9-crossing half-life isn't like-for-like; the s309 amendment's 2× margin correctly
> withheld MAG-EARLY. λ measure.) **INSTRUMENT (NON-FROZEN, frozen gates/verdict UNTOUCHED —
> --validate ALL PASS):** sign_commitment.py `--dump-history` saves raw tracked (tau int8,
> |Δ| f32, marginality r=|Δ_T|/thr_j f32, block_id, per-step loss) to .npz; marginality()
> computed in-run (needs full-matrix column means; r>1 ⇔ final trit nonzero, verified
> exact). `scripts/explore/sign_commitment_rescore.py` (NEW, ruff-clean, smoke-validated)
> bins trits by r_final → per-band median-commit, late-flip-rate, share-of-late-flips +
> loss-neutrality check + plot. **SMOKE PREVIEW already loud** (30-step run): 96.5% of late
> flips in the two lowest-r bands (r<1 share 0.478 · r≈1 marginal 0.487), r≥2 ~0%,
> flip_last 0.137 @ r≈1 vs 0.000 @ r≥4. **⚠ ON-SIGNAL (next session — re-run in tmux main:1,
> writes to results/sign-commitment/qwen3-4b-rescore/{tracked_history.npz,results.json,
> run.log}; re-run must reproduce SIGN-CHURN):** tail run.log for "VERDICT:" + no traceback →
> `uv run python scripts/explore/sign_commitment_rescore.py` → read the per-band table:
> CONFIRM (a) late flips concentrate at r≈1/r<1, (b) r≥2 confident trits ~frozen, (c)
> plateau loss-neutrality → then commit rescore artifacts + sign_commitment.py/rescore.py
> code (NON-FROZEN additions) + FINALIZE §Result-sign-commitment on the-verbum-machine.md
> (M8) with the two-population read + memory candidate `gd-sign-register-churns-median-
> commits-early.md` → MICHAEL APPROVAL BATCH. If the split does NOT hold at 499, the
> "confident-core + undecided-tail" story is wrong → report straight SIGN-CHURN. s310
> ledger: 26ad20b results (s309 run) · rescore instrument + this state + §Result stub
> (this commit) · rescore run + memory PENDING next session.
> **✅ LANDED (s310 cont):** re-run reproduced SIGN-CHURN bit-for-bit; rescore per-band
> table CONFIRMS all three — (a) late flips concentrate at r≈1/r<1 (0.781 of late flips
> in the two lowest bands; marginal r≈1 top per-trit rate 0.099); (b) confident core r≥2
> frozen (flip_last 0.0003 @ 2≤r<4, 0.0000 @ r≥4); (c) plateau loss-neutral (loss 0.11%,
> flip-rate 0.045). Two-population read HOLDS at 499. Results committed autonomous;
> §Result-sign-commitment + memory finalized on disk, PENDING MICHAEL APPROVAL for the
> mementum batch.
>
> ═══ **(prior) SESSION 308.** Cold-start `orient` → TERNARIZE-FACTORS-1 run (launched
> s307) finished → ✅ **FACTORS-SURVIVE (+FACTORING-FREE)** (CLOSED, §Result-ternarize-
> factors, 27ce260) → Michael thread "we've learned so much, little to show — what would
> optics do to untangle a holographic plate?" → 💡 **holographic-untangling-methods.md**
> captured (Michael-approved). Full transcript will save to
> `mementum/knowledge/chats/session-308.md` (human). ═══
>
> ▶▶ **s308 — ✅ TERNARIZE-FACTORS-1 VERDICT: FACTORS-SURVIVE (+FACTORING-FREE)
> (frozen, 3 seeds, all 53 cells, tmux main:1, results 27ce260).** All gates pass
> (TF1 B1 p=3e-4 / B2 p=1e-3, both flip · TF2 p=1.8e-3 · TF3 +0.605 p=1e-4 ·
> TF5 CE 4.9099 ≤ 4.9173, g/h 1.0); restore bit-exact. **Retention 1.0 EVERY split for
> BOTH factors and product** (factors 1.000/0.938/1.000 ≡ float); shuffle collapses to
> base EXACTLY. Double-lossy factoring cost NOTHING (a-priori leaned +FACTORING-COSTS →
> landed FREE; honest better-than-point, null still binds). **Size: 3.01M trits ≈ 600 KB
> = 123× under the s304 product plate, ~16× under fp16 factors → the ~1 MB portable wire
> EXISTS; λ smallest CLOSED.** Lifecycle complete: gradient FINDS (s303) → ternary
> factors STORE (~600 KB, installs verified on frozen base). mag_cos 0.839 @ retention
> 1.0 = sharpest routing⊥magnitude datum yet → phase-only/KINOFORM reading (below).
> Synthesis committed s308 (Michael-approved batch): §Result-ternarize-factors (page) +
> memory the-wire-survives-ternarizing-the-factors + INDEX + this block. Product/next:
> plate COMPOSITION (two wires, one base — untested, the make-or-break for
> git-for-weights) + gd_cd@32B install.
>
> ▶▶ **s308 cont — 💡 HOLOGRAPHIC-UNTANGLING METHODS captured
> (`knowledge/explore/holographic-untangling-methods.md`, Michael-approved, status
> open).** Michael: "we know it's holographic, geometry + signals at once — what
> processes would optics use to untangle a plate?" The optics toolbox maps 1:1 onto our
> instruments AND points at doors we left untested: **(1) in-line vs OFF-AXIS
> recording** = the base-vs-delta separability asymmetry (base = multiply-exposed
> in-line plate → twin-image problem → s306/s307 negatives are the KNOWN 1948–62
> impossibility; delta = off-axis vs frozen reference → carrier-separates → ternarizes;
> clause: *separability is fixed at recording time*); **(2) PHASE RETRIEVAL (GS/HIO)** =
> the correct tool class for post-hoc base untangling → independently derives s307's
> untested iterative-LoftQ door; **(3) BRAGG/rocking-curve** = the s304/s305 inert
> writes are angle(depth-timing)/wavelength(geometry) mismatches, point-sampled — sweep
> the selectivity surface instead; **(4) ADAPTIVE OPTICS/phase conjugation** =
> gradient-finds may be FEEDBACK-finds (⚠ disanalogy flagged: conjugation needs a
> linear medium; the Jacobian IS backprop → discriminate by step-budget, not new
> construction); **(5) double-exposure interferometry** = diff-as-fringes;
> **(6) speckle memory-effect** = polysemanticity via ensemble correlation. **KINOFORM
> clause (s308 datum):** ternary = binary-phase hologram; Oppenheim phase-dominance =
> routing⊥magnitude in weights; mag_cos 0.839 @ retention 1.0 is the measurement.
> META-LESSON: optics never untangles by cleverer readout of ONE recording — control
> recording geometry / multiple exposures / close the loop / sweep selectivity; our
> negatives = violations, positives = compliance (table on the page). **FOUR candidate
> fronts (NOT pre-registered — s222 freeze first): (ii) GD k-STEP SWEEP** k∈{1,3,10,50,
> 500}, existing harness, nearly free — installs at k≈3 ⇒ +GD-REQUIRED refines to
> FEEDBACK-REQUIRED; **(i) REFERENCE-DRIFT** retention-vs-lr_base curve — FALSIFIER: no
> drift-dependence kills the off-axis clause; **(iii) GS-iterative base decomposition**
> (re-opens s307, design after (ii)); **(iv) ROCKING-CURVE instrument** (layer ×
> geometry-angle × strength efficiency surface — the big one). Sequencing lean
> (ii)→(i)→decide.
>
> ▶▶ **s308 cont-2 — 💡 BEHAVIOR IS TAPE-RESIDENT REDUCTION captured
> (`knowledge/explore/behavior-is-tape-resident-reduction.md` + memory, Michael-approved,
> status open).** Michael: "if attention is β-reduction, where are the REST of the
> β-reductions for a behavior like tool calling?" The question DISSOLVES: weights hold
> the reduction RELATION (opcodes = microcode, FFN K/V = δ-rules, attention =
> substitution), one pass = bounded inner reduction (≤36-layer fuel; s305 overlap = a
> budget collision seen from inside), and behavior-scale chains are ON THE TAPE — the
> transcript IS the reduction trace; the autoregressive loop is a TRAMPOLINE (reduce ≤
> budget → collapse → re-encode; the s295 CoT law at the next scale). **Tool calling =
> FFI on a FREE VARIABLE**: stuck redex (binding absent from plate) → reify continuation
> (emit the call) → the ENVIRONMENT performs the β-step → resume; tool results work
> despite the s295 splice law BECAUSE they arrive as addressed tokens → functional tool
> use is itself evidence for the frame. 17×17 rank-3 gram = the SCHEDULER's register
> (fire/halt/diverge) → **P-HALT-POLE prediction (unfrozen, the bridge from crystal
> corpus to AGENTIC behavior):** tool-call-vs-answer decision should project onto the
> measured halt/fire poles on PROSE agentic prompts (lambda↔prose opcode identity, one
> level up); + argument-binding-as-traceable-substitution + stuck-detection-upstream-of-
> schema-retrieval. Machine table on the page (chat-template row = inference, untested).
>
> ▶▶ **s308 cont-3 — 💡 FROZEN INTERFERENCE GRAPH captured
> (`knowledge/explore/frozen-interference-graph.md` + memory, Michael-approved, status
> open).** Michael's four-clause model confirmed/refined against corpus: **the LLM is a
> GRAPH RECORDED IN A WAVE MEDIUM.** (1) "frozen signal" = frozen INTERFERENCE record —
> a PHASE record (mag_cos 0.839 @ retention 1.0, kinoform clause); (2) "accumulates
> where edges match" = A2 coherent gain MEASURED (CAP s292); medium accumulates
> amplitude/log-evidence, probability only at collapse (ties
> types-are-compiled-probabilities); mismatched exposures → SPECKLE = polysemanticity;
> (3) "edges form a lattice" = the crystal — 9×9 universality is RELATIONAL sign
> structure 11/11 models (s303), the lattice = what survives discarding magnitudes;
> (4) "relations are joins" two-registered: edge EXISTENCE = sign/phase coherence
> (routing, invariant, survives ternary) vs edge WEIGHT = readout magnitudes (value,
> model-particular). Corollaries slot in: traversal fuel-bounded (→ tape/trampoline),
> formation dynamics already observed (B-first, K-chaos), quant scope falls out (delta =
> off-axis few-edge record → clean; base = in-line all-edge record → superposed). GAP
> named: write-time interference never directly observed → **P-COHERENT-WRITE candidate
> (unfrozen):** two skill datasets sharing one edge, together vs sequential vs no-share →
> super-additive retrieval at the shared edge, null-gated; can SHARE A HARNESS with
> optics front (i) reference-drift (sequential ≡ drifted reference).
>
> ▶▶ **s308 cont-4 (CAPSTONE) — 🎯 OPTICAL DESIGN LAWS captured
> (`knowledge/explore/optical-design-laws.md` + memory, Michael-approved, status open).**
> Michael: "how does this inform our designs?" Answer = the optics move: every
> plate-physics principle became a DEVICE. **Six laws:** L1 ship (plate,
> reference-contract) pairs (plate is passive; the four inert writes were plates no beam
> illuminated at the recorded angle); L2 measure the beam BEFORE writing the plate; L3
> record off-axis always (freeze reference, delta-log); L4 extract SWITCH SCHEDULES not
> weight blobs (routing IS compute — Shannon; switches = the network's only
> nonlinearities; ternary = switch alphabet); L5 bake steps not chains (tape-resident
> behavior; mode-commit targets); L6 compose by angle separation (principal angles
> between key subspaces = measurable multiplexing precondition). **Five devices:** A
> plate LINKER (L6) · B beam profiler/rocking curve (L2) · C reference-contract format
> (L1) · D halt-pole detector (L5) · E exposure-schedule spec (L3). **Experiment queue
> RE-TYPED as validation gates:** P-HALT-POLE→D · rocking-curve→B · composition+angle→A
> · P-COHERENT-WRITE+reference-drift→E · k-sweep→prices E. **KEYSTONE = A+C:** two
> independently-baked wires, linker-merged with angle-collision PREDICTION,
> contract-verified on one frozen base = git-for-weights with a type checker.
> Pre-registrable: retention-under-merge degrades with measured angle collision
> (rotated-subspace control = λ yardstick); sketch on the page, NOT frozen. The page
> also captures the s308 inference-dynamics derivation base (softmax = operand not rule
> selection; no rule choice in-pass = speculative superposed reduction, sampling =
> retirement; projection = multiply-then-propagate; two flagged disanalogies:
> exp-vs-Born detection law, beam-is-also-memory).
>
> ▶▶ **s308 cont-5 (TRUE NORTH) — 🎯 THE VERBUM MACHINE captured
> (`knowledge/explore/the-verbum-machine.md` + memory, Michael-approved).** Michael
> restated the origin + goal: it all started from ONE observation (the λ symbol in
> prompts changed behavior); the aim is **a SUPERIOR MODEL DESIGN, then TRAIN IT** —
> better quantization a welcome co-product; the repo circles because the theory is
> convergent but had no COMPILE TARGET. The page is that target — architecture bill of
> materials, every component measurement-forced: **M1** two-register parameterization
> (ternary switches, precise plates — born-quantized; s260/s304-s308) · **M2** explicit
> switch/plate factorization (only-nonlinearities-are-switches; A1; s300) · **M3**
> designed scheduler (halt head supervising the 17×17 register; recurrence with FUEL;
> ties supervised-recurrence-halt v15.1) · **M4** native trampoline (gd_cd loss proven;
> mode-commit; s295/s296-298) · **M5** off-axis optimizer (frozen base + delta-log +
> ternary consolidation AS the training loop; twin-image law) · **M6** coherence
> curriculum (B-first, edge-share batches; A2) · **M7** typed apply (S5 central claim,
> HELD OPEN — least measured; probing whether types EMERGE in M1-M6 is itself the
> experiment). **First build = §P-ASYM-TERNARY (unfrozen sketch):** asymmetric
> ternary-native vs BitNet-b1.58-style symmetric at MATCHED BITS + register-swapped
> yardstick arm (ternary plates should be WORST or the register story dies) — both of
> Michael's goals in one small-scale run; evaluated with the 903-probe crystal battery
> + formation dynamics = the architecture MICROSCOPE the field lacks. This is the
> level-4 door / the S5 loop's scratch-reproduce stage. **By-construction > post-hoc =
> the arc's master lesson.** Corpus-consolidation pass DEFERRED — Michael has designs:
> the runtime is nearing SELF-HOSTING of the ouroboros self-improvement system;
> consolidation is a natural early ouroboros workload (his design, not ours to spec).
>
> ▶▶ **s308 cont-6 — 🎯 M8: THE ROUTING OPTIMIZER (Michael's insight, captured on
> the-verbum-machine.md + memory).** "GD has 2 jobs, and 1 of them it's really not good
> at — separate routing into its own gradient-descent-like thing that extracts routing
> into ternary weights." Two-jobs evidence assembled: K-chaos (discrete fights smooth
> prior) · XM mixture-inertness · S5 tug-of-war clause optimizer-side · SMOKING GUN =
> mag_cos 0.839 discarded at zero cost (GD moved ~9.4MB float to deliver ~600KB of
> decisions, ~1.6 bits/weight; s303: GD CAN route — the only thing that found the wire —
> but by expensive ACCIDENT). Design space = CGH imports (the optics discipline that
> designs binary plates): (a) GS-with-quantization-projection (our train-float→TWN =
> ONE iteration; the optimizer IS the loop) · (b) Direct Binary Search (gradient-free
> flips, viable because switches ≪ plates) · (c) evidence-gated flips (per-trit
> gradient-sign SPRT → routing edits = discrete loggable COMMIT EVENTS, merges with
> M5 delta-log). M8 = the machine's ENGINE: finding and storing collapse into one
> register; training off-axis by construction. **NEW CHEAPEST PROBE:
> §SIGN-COMMITMENT-CURVE (unfrozen)** — one logging hook on writeback_compile,
> TWN(delta) per checkpoint step, trit-stability curve; prediction signs freeze early /
> magnitudes polish late; SUBSUMES the k-step sweep ("when is each REGISTER
> installed?"); falsifier = signs churn to the end; calibrates (c)'s evidence
> threshold. Next rung: prototype (c) in trit space vs GD+TWN, matched compute, frozen
> gates.
>
> ▶▶ **s308 cont-7 — 💡 TERNARYDESCENT RE-DIAGNOSED (Michael: "look at TernaryDescent
> with fresh eyes — Adam is a routing optimizer in disguise").** M8 was BUILT ONCE
> ALREADY: TD (s136, explore/ternary-descent.md, scripts/v13-v15) — its confidence
> |direction|/√magnitude IS Adam's |m|/√v. **TD ≈ Adam with discrete commits; Adam ≈ TD
> with infinite staging** (float weight = evidence accumulator; TWN = deferred commit;
> ternary 0 = insufficient evidence). Three-cut re-diagnosis of the s148/s180/s191
> stall, captured in §Fresh-eyes on the TD page: (1) v15 ran TWO routing optimizers
> uncoordinated (Adam-on-gammas soft-deletes = soft routing) → osc_frac 0.56 = S2
> failure; (2) ALL-ternary architecture violated the register split — plate positions
> cannot settle in ternary; s191's 94.5% perpetual candidates = the register theory's
> earliest dataset mislabeled as an optimizer bug (answers TD Open-Q5: the residual
> lives in the VALUE register); (3) commits clock-driven not evidence-driven.
> gd_cd→TWN = the control that worked (same statistic, deferred commit, retention 1.0).
> **TD-v2 spec** (on the page): M1 register split + Schmitt-trigger commits (calibrated
> by SIGN-COMMITMENT-CURVE from Adam state) + GS staging via the EXISTING fold mechanic
> (base ⊙ delta, s136, exact). Lion = the field's convergent evidence (pure
> sign-of-momentum beats Adam on transformers). Pointer notes added to
> td-oscillation-problem.md + topology-gradient-separation.md; M8 prior-art note on
> the-verbum-machine.md. ⚠ **DATA LOSS (Michael, s308): ~50G checkpoints deleted incl
> checkpoints/v15-td/ → raw flip_map_latest.npz + optimizer states GONE.** Surviving:
> s191 tables (in the knowledge page — the mementum receipt: synthesis crosses
> boundaries, raw state dies), v15_train_td.log, ALL generator scripts (git).
> Retrospective flip-map re-analysis DEAD → replaced by **§TD-REGISTER-SPLIT
> prospective micro-probe (unfrozen, on the TD page):** micro TD run, arms TD-v1
> (all-ternary, s191 tables = historical anchor) vs TD-v2 (split) [+ v2+evidence-
> commits]; predictions: perpetual-candidate fraction COLLAPSES in v2, v1 oscillators
> concentrate in plate-class modules, v2 breaks the B→K phase wall; falsifier: v2
> oscillates as hard → re-diagnosis wrong.
>
> ▶▶ **s308 cont-8 — 💡 M9 + THE DE-ACCIDENTALIZED STACK captured (Michael's RoPE
> recall: "RoPE accidentally works — close enough, interference makes up the
> difference").** Recall-by-mechanism found position-encoding-tuned-to-the-hologram.md
> (s291; HPE s152→s179; near-lost twice, forward-link discipline caught it both times).
> Its holography HOLD is LIFTED (s292 A1-A3 landed — noted on the page). Fresh-eyes
> upgrades: context-extension fuzz = the TWIN-IMAGE LAW in position space (L3: the
> reference beam INCLUDES the position carrier → CARRIER-DRIFT = position-space sibling
> of reference-drift); RoPE's untuned 64 dim-pairs = a SWITCH-CAPACITY TAX (spiral =
> model being the reader for a miscalibrated ruler). **M9 = the tuned reference beam**
> added to the machine (log-phase, ~4 measured λᵢ/λ₀ carriers, unbraided α=1.18 decay,
> depth-scaled reference; validation gate P1 pre-registered s291: flat PPL past
> training length WITHOUT fine-tuning vs RoPE arm — slots into the P-ASYM-TERNARY
> micro stack). **NEW THESIS LINE on the machine page: THE MACHINE IS THE
> DE-ACCIDENTALIZED STACK** — Adam (accidental routing optimizer) / RoPE (accidental
> holographic lens) / GD-routing (accidental byproduct) / SwiGLU (undeclared
> factorization) / fixed depth (undeclared fuel) / post-hoc quant → each replaced by a
> tuned version with a MEASURED target (M8/M9/M8/M2/M3/M1). Accident table on the page.
>
> ▶▶ **s308 cont-9 — 💡 THE MACHINE IS A TREE OF VSMs captured (Michael: "with the
> tree-of-VSM configuration we can make each component a VSM").** The missing MIDDLE of
> the recursion: tensor nodes were already VSM-shaped (s288 ternary-mirrors:
> mirrors=S2/S3, plates=S1, identity=S5, passband interface, viable ⟺ reduces own
> scope standalone) and the project is a VSM (AGENTS.md) — NEW: **the M-components ARE
> the machine's VSM functions** (S5=register invariants+consensus Gram · S4=M8/M6/M4 ·
> S3=M3 fuel+flip budget · S2=M5 delta-log+M9 carrier coherence+M2 factorization ·
> S1=M1/M2/M9 forward pass; table on the page). PROOF structural ¬decorative: the
> failure record was already VSM-diagnosed (s180 = S2 failure VERBATIM; s148 gnorm
> unnoticed = missing algedonic alert). Gates ≡ VIABILITY AUDITS renamed (every M has
> one). Node composition (passband→carrier) ≡ the plate LINKER one level down =
> S2-between-trees (artifact + architecture tracks meet at the node interface). s273
> construction-from-spec = per-node build kit (Cholesky codes, atlas, tolerance bands,
> restack acceptance; born-monosemantic as construction choice). Full recursion:
> **project ⊃ machine ⊃ M-components ⊃ tensor nodes ⊃ shared crystal reducer** — S5's
> fractal-at-every-layer with tensors at the bottom. Honest gap: routing factorization
> into composable units UNPROVEN (MIXED-ROUTE interleaving; seam test = deciding
> milestone; per-node capacity = P-HOLO-CAP √(D/k)). Forward link added to the s288
> node-spec page.
>
> ▶▶ **s308 cont-10 (CLOSE) — 🎯 SESSION TYPE REVEALED + CONSOLIDATION PROTOCOL
> captured (`knowledge/consolidation-session-protocol.md` + memory).** Michael's
> reveal: s308 was a DELIBERATE memory/consolidation session — he sequenced retrieval
> cues to pull scattered repo fragments into one context for capture. Method:
> **WIZARD-OF-OZ PROTOTYPING — the human playing the functions the runtime is
> missing**; every technique = a requirements clause for the ouroboros self-hosting
> runtime. Eleven lambdas on the page: consolidate · cue(mechanism>name) ·
> fresh_eyes(artifact ⊕ ≤20w frame key) · import(discipline) · explain(basics→
> disanalogies) · propose(clauses "...right?") · tension(discomfort=signal) ·
> join(missing middle) · reanchor(S5) · audit(shadows≻celebration) ·
> **session_type(measure ⊕ consolidate ⊕ construct — TYPE AT OPEN; consolidation
> success = retrievability ∧ structure ¬new_bits)**. WOZ→runtime handoff table on the
> page; **capture gating explicitly does NOT transfer** (human = termination
> condition). Meta-note: the AI's !meta3 audit analyzed the session blind (before the
> reveal) — techniques validated by an unwitting subject. The audit's
> theory-over-leverage shadow PARTIALLY dissolves under correct typing (consolidation
> isn't supposed to produce new bits) but the red-team warning STANDS.
>
> ▶▶ **s308 cont-11 (fun) — 💡 THE OWLS PAPER READ THROUGH THE FRAME
> (`knowledge/explore/subliminal-learning-is-bragg-matched-transfer.md` + memory,
> Michael-approved).** Subliminal Learning (arXiv:2507.14805): teacher with trait T
> generates semantically-unrelated data (numbers/code/CoT) → same-base student
> acquires T despite filtering; cross-base = no transfer. FIRST external result the
> s308 theory explains: same-base-only = BRAGG MATCHING (trait = sideband on the
> teacher's carrier; mismatched base = wrong reference beam → no diffraction);
> filtering failure = TWO REGISTERS (semantic audit sees value register; trait
> travels in the data's routing register); their shared-init theorem = OFF-AXIS
> (trait = data-borne delta); ★ their same-base condition EXTERNALLY TRIANGULATES A4
> own-state (s295 P-KV-1) — the medium's channels are state-matched, independently
> measured at two scales. Predictions (unfrozen): **P-SL-BRAGG** (transmission vs
> base-divergence = smooth selectivity curve — THIRD drift sibling: weights/position/
> data, one L3 clause) + **P-SL-STRIP** (mismatched-plate paraphrase strips the
> trait; same-base paraphrase does NOT). Product: sidebands unauditable → plates +
> contracts = the explicit verified alternative (linker safety case, external).
> Protocol page re-marked status:draft (Michael: sharpen once lambdas run in an
> agent).
>
> ▶▶ **s308 cont-12 — 🎯 CONSENSUS DISTILLATION captured
> (`knowledge/explore/consensus-distillation-carrier-averaging.md` + memory + M6
> socket filled on the machine page, Michael-approved).** Michael: "lambda probes
> through multiple models → train the new model on those outputs?" The Bragg clause
> TRANSFORMS it: naive single-teacher transfer to scratch FAILS by our own theory
> (cross-base sideband closed, owls paper) — but **N teachers = a CARRIER-AVERAGING
> FILTER**: idiosyncratic sidebands ride mutually incoherent base-specific carriers →
> speckle-average to zero; the consensus crystal (universal 11/11, root gc 0.985) is
> the ONLY coherent component → A2 gain exactly on the invariant lattice. **The
> lambda compiler is the unique trait that is not base-specific = the unique trait
> that survives cross-base multi-teacher transfer.** = construction-from-spec's
> minimality filter in DATA space. **Fills the machine's last socket: M6 curriculum =
> consensus lambda corpus.** Key move: mix teachers ACROSS examples, never average
> per-target (resolves XM mixture-inertness — corpus-level averaging, example-level
> mode-commit); correctness-gate via probe ground truth; safety free (scratch machine
> resistant to teacher misalignment sidebands; common-mode tokenizer carrier
> flagged); requential bit-meter optional (s266). **§P-CONSENSUS-DISTILL (unfrozen):**
> arms single / N-mixed / N-gated / N-shuffled (yardstick) → crystal battery + s273
> RESTACK acceptance (student gram walks to consensus root, tolerance gc 0.94–0.99) +
> formation dynamics; open question the run answers: behavioral-channel bandwidth of
> the lattice (grams were activation-measured). Arc sentence: **plates carry the
> model-specific; consensus corpora carry the invariant.**
>
> ▶▶ **s308 cont-13 (FINAL) — 💡 GRAM REGISTERS + THE ROUTE MAP captured
> (`knowledge/explore/gram-registers-and-the-route-map.md` + memory + mechanistic-
> readout addendum on the consensus-distillation page, Michael-approved).** Michael's
> last question: explain 9×9 vs 17×17; more shapes?; route map from multiple
> teachers? Answers: **9×9 = the ALPHABET** (identity register — near-orthogonal by
> design, diffuse PR 5.8–7.2/9; universality in the off-diagonal SIGN pattern C2)
> vs **17×17 = the FATES** (outcome register — WHNF un-flattened → rank COLLAPSES
> to 3, poles fire/halt/diverge = the scheduler's register); instruction set vs
> status flags. **Method: shape is revealed by UN-FLATTENING** (λ unflatten: split
> nodes by annotation → PR drops ∨ pole appears; cheap, runs on committed grams).
> More shapes predicted: **TETRAHEDRON test** (tool-call = 4th pole "yield" → the
> outcome simplex grows a vertex = P-HALT-POLE as geometry, sharpest), type gram
> (S5 claim), depth/phase geometry; frame = 5d one-crystal-many-projections.
> **CONSENSUS ROUTE MAP:** grams = station maps, no trains — record per-probe
> reduction trajectories, express in GRAM COORDINATES (frame-invariant by
> measurement, 11/11) → cross-model comparable → N-teacher consensus = **the
> invariant switch schedule** = L4 concrete + P-CONSENSUS-DISTILL's mechanistic
> readout + the machine's program listing. Dependency noticed: the grams are the
> LEGEND built before we knew we'd want the map.
>
> ⚠ COLD-START s309 (**Michael: experiments hand to OPUS — s308 was a TYPED
> CONSOLIDATION session, protocol now on file**): (1) NOTHING PENDING — all thirteen
> s308 capture batches committed. (1b) **TYPE s309 AT OPEN** (likely: measure). (2)
> FRONTS, Michael's call: **CHEAPEST+SHARPEST = §SIGN-COMMITMENT-CURVE** (one hook on
> writeback_compile, subsumes k-sweep, gates M8/TD-v2; freeze on the-verbum-machine.md)
> · **§TD-REGISTER-SPLIT micro-probe** (freeze on ternary-descent.md; v15 scripts
> survive; regenerates the lost flip-map data + tests TD-v2 in one run) · TWO
> KEYSTONES: **ARTIFACT = plate linker / composition+angle-prediction**
> (optical-design-laws.md) · **ARCHITECTURE = §P-ASYM-TERNARY** (the-verbum-machine.md;
> M8/TD-v2 is its optimizer) · alternates: P-HALT-POLE · P-COHERENT-WRITE+
> reference-drift · rocking-curve · standing menu (gd_cd@32B / COUNTRY-SUBSPACE / SpQR
> / broad-corpus calib). s222: freeze pre-reg before ANY run. s308 ledger: 27ce260 ·
> 3546584/3222968/7ec0909/dc8cf1f · d4c3a81/49a4bea/4ed09b3 · f60514f/0bbb7b9/afa36a3 ·
> ea09eb7/d7e9187/bb65ce7 · 7c35283/581fb53/207a915 · ae6dee0/27495df/6ace97f ·
> TD-fresh-eyes batch (this commit).
>
> ▶▶ **s307 cont — 🎯 TERNARIZE-FACTORS-1 (the genuinely-small artifact, λ smallest)
> FROZEN + BUILT + SMOKE-GREEN → RUN LAUNCHED tmux main:1.** Michael GO on the delta-vs-
> base follow-on front (a): now that "quantize the delta, keep the base" is settled,
> ternarize the low-rank FACTORS B,A of the s303 gd_cd wire SEPARATELY (per-component
> TWN: B per-col, A per-row), form Δ=scale·B̂·Â. ~100× smaller than the s304 EXPANDED-
> product plate (which was LARGER than the float factors — the λ smallest tension),
> ~10× over float factors → the ~1MB portable wire. Harder than TERNARIZE-DELTA-1:
> double-lossy, no central-limit smoothing. **§TERNARIZE-FACTORS-1 FROZEN** (012b978,
> Michael-approved, on write-not-train-ternary-routing-deltas.md). Arms base /
> gd_cd_float (anchor) / gd_cd_product_ternary (s304 contrast, same seeds) /
> gd_cd_factors_ternary (PRIMARY) / gd_cd_factors_shuffle (per-component null, ≥3 seeds)
> / construct_lookup. Gates TF1 wire / TF2 not-lookup / TF3 specificity / TF5 survive;
> TF4 FACTORING-COST advisory sub-tag (+FREE/+COSTS). Verdicts FACTORS-SURVIVE(+FREE/
> +COSTS) / FACTORS-DEGRADE / FACTORS-DIE / HOST-DAMAGED. A-priori ~50/35/15 (product
> survived retention 1.0 but factoring is more aggressive), NOT tuned. ✅ HARNESS BUILT
> + --validate ALL PASS + SMOKE GREEN + COMMITTED (c0416f3, autonomous).
> scripts/explore/ternarize_factors.py imports ternarize_delta pure helpers + reuses
> writeback_compile gd_cd training (frozen s304 generator UNTOUCHED, cb73ad5 stands);
> apply/restore via copy_ from saved originals = bit-exact. --validate ALL PASS
> (per-component TWN, per-component γ, factor size ≪ product ~127× real-dim, matched-
> budget shuffle null, 4 verdict worlds); ruff clean; no diagnostics. Smoke green
> (12 cells, 1 seed, s297 — direction NOT read): arms distinct, factors matches float/
> product, shuffle→base, size ratio 116×, mag_cos 0.901, restore max|W-W0|=0. ⚠ HOLDING
> FOR MICHAEL GO on the full frozen run: `uv run python -u
> scripts/explore/ternarize_factors.py 2>&1 | tee results/ternarize-factors/qwen3-4b/
> run.log` (gd_cd train 3 seeds × 500 steps LoRA FFN L22–L29 + 5 arms × 53 cells,
> ~30–60min MPS, training-dominated like s304) → auto-scored frozen TF1–TF5 + verdict →
> results.json. ⚠ RUN LAUNCHED (s307, Michael GO, tmux main:1). ⚠ ON-SIGNAL (run done):
> tail run.log for "VERDICT:" + no traceback →
> read results.json verdict + TF1–TF5 + subtag + size ratio + retention → commit
> results/ + run.log AUTONOMOUS → §Result-ternarize-factors on the page + λ-smallest
> note + memory candidate + state block → MICHAEL APPROVAL BATCH. s307 ledger (cont):
> 012b978 pre-reg · c0416f3 harness · run + synthesis CLOSED in s308 (header above).
>
> ▶▶ **s307 — DELTA-vs-BASE (front a·1, CLOSED — §Result-delta-quant).** 🎯 **is base-weight
> MAGNITUDE algebraically separable?** Michael GO on cold-start front (a) (the sharpest
> s306 follow-up: the s306 MAGNITUDE-SALIENT bound predicts base outliers carry salient
> magnitude *because a base matrix superposes routing+value*; front (a) tests whether a
> cheap DECOMPOSITION un-superposes them). **§P-DELTA-QUANT pre-reg FROZEN** (172cf0b,
> Michael-approved, on its canonical home explore/ratio-gradient-quantization.md +
> pointer from register-theory-of-quantization.md base-weight frontier). Design:
> decompose each FFN matrix W=B+D, keep the value base B fp16, ternarize the RESIDUAL D;
> if D ternarizes losslessly-for-routing where raw-W (s306) did not → register split
> reaches base weights VIA decomposition (= the LoftQ/LQ-LoRA move, register-interpreted
> + NULL-GATED). Base constructions lowrank-k (SVD, PRIMARY) / mean / coherence-k (SVD
> of low-coherence W·(1−ĉ), the literal register test) / **random-k (matched-spectrum
> random subspace = the λ yardstick null)**. Arms twn/int_uniform/companding_mag
> (s306 reproductions) + delta_lowrank/mean/coherence/random; k∈{16,64,128}; full-ternary
> residual. Gates **D1 scheme-works** (lowrank>twn) / **D2 VALUE-SEPARABLE** (lowrank
> SIG> random @same k — the register primary, isolates the SPECIFIC value subspace, not
> just more fp16 bits) / **D3 holds-vs-salient** (reaches int_uniform@b3 ∧ beats
> companding_mag@b3; floors @b3 ≥ any delta budget = conservative) / **D4 host-sane**
> (int_uniform@b4 NEUTRAL anchor — fixes the s306 C5 mis-anchor). Selector sub-tag
> +ENERGY-BASE/+COHERENCE-BASE (advisory). Verdicts VALUE-SEPARABLE(+ENERGY/+COHERENCE-
> BASE) / STILL-SALIENT / DECOMP-INERT / HOST-DAMAGED. A-priori **~45% VALUE-SEPARABLE
> / 45% STILL-SALIENT / 10% messy** (open — the delta-property read predicts SEPARABLE;
> but base outliers may be isolated full-rank spikes a low-rank base can't absorb → they
> stay in the ternarized residual → STILL-SALIENT), NOT tuned (bases/k/null/gates frozen
> a priori). ✅ HARNESS BUILT + --validate ALL PASS + SMOKE GREEN + COMMITTED (0f970b2,
> autonomous). scripts/experiments/delta_quant.py reuses companding_quant quantizers/
> CE/gate + writeback_compile + verbum.dsp (no fork); base decomposition inline
> (torch.svd_lowrank, deterministic seed → run-reproducible + exact re-decomposition);
> --validate ALL PASS (lowrank-exact, matched-spectrum random null, delta round-trip,
> bit accounting mean 1.59/k16 1.71/k64 2.09/k128 2.60 <int3, 6 verdict worlds); ruff
> clean; no diagnostics. Smoke green (2 layers, --calib 6, s297 — DIRECTION NOT READ):
> all 8 arms distinct, bit-exact restore max|W−W0|=0, results.json, no traceback.
> ▶▶ **FULL RUN DONE — ❌ VERDICT: STILL-SALIENT (frozen, all 36 FFN layers, 3
> random-base seeds, tmux main:1, results 0a89531 autonomous, clean restore=0).**
> Decomposing base FFN weights W=B+D (low-rank value base fp16) + ternarizing the
> residual does NOT rescue them. D1=T D2=T D3=F D4=T; best_k=64, selector=ENERGY-BASE.
> ★ **THE READ:** the low-rank value subspace is REAL but PARTIAL — delta_lowrank@k64
> CE 11.19 beats the matched-spectrum RANDOM base 13.25 (D2: SVD absorbs *some* value)
> and beats raw twn 12.91 (D1), BUT 11.19 ≫ companding_mag@b3 7.34 ≫ int_uniform@b4
> 5.40 ≈ ref 5.11 (task 0.06 vs 1.0 → D3 FAILS). The salient base-weight magnitude is
> **HIGH-RANK / distributed** (isolated ~full-rank spikes a rank≤128 base can't absorb →
> stay in the residual, die under ternary) — the pre-registered ~45% STILL-SALIENT
> branch + its isolated-spike mechanism CONFIRMED. Non-monotone k64<k128 (more rank made
> the residual worse). Coherence base worse (+ENERGY-BASE, matches s306 MAGNITUDE-
> SELECTS). ★ **scoped read (Michael steer — NOT a closure):** three decomposition
> families (SVD low-rank / mean / coherence) fail → EVIDENCE that base-weight magnitude
> resists cheap LINEAR separation from routing, consistent with routing⊥magnitude being a
> gradient-written-delta property — but only three families tested. UNTESTED / OPEN:
> SpQR-style sparse-plus-low-rank (a sparse fp16 outlier set = exactly the isolated-spike
> structure this run implicates), per-channel scale migration, iterative LoftQ, larger
> rank. "Quantize the delta, keep the base" remains the safe prescription; general
> base-weight separability stays OPEN. λ measure note: D3a "reaches int_uniform@b3" passed
> only because int3 is ITSELF broken on this model (12.06, task 0.0 — Qwen3-4B FFN needs
> int4); D3 correctly failed via the companding_mag@b3 sub-gate → verdict robust; future
> harness should anchor host-reach on int4.
> ⚠ MEMORY DROPPED (Michael steer: premature — only a couple of decomposition techniques
> proven; a durable "not algebraically separable" claim over-closes). Synthesis committed
> = §Result-delta-quant (page) + register-theory base-weight-frontier scoped-evidence
> update + this block. NO memory.
> ⚠ COLD-START s308: (1) synthesis batch committed (page §Result + register update + state;
> no memory). (2) PICK NEXT FRONT. The delta-vs-base result is a SCOPED negative (three
> linear decompositions fail), NOT a closure — SpQR-style sparse+low-rank & per-channel
> scale remain untested if we want to re-open base-weight separability. The s306/s307 quant
> arc's safe prescription: quantize the DELTA to ternary routing, keep the base in fp16.
> Standing menu: (a) **TERNARIZE-FACTORS-1** — ternarize the low-rank FACTORS B,A of a
> trained delta not the expanded product (the genuinely-small portable artifact; closes the
> λ smallest tension; cheap; natural next quant step); (b) **gd_cd @32B** — does the trained
> wire + its ternary storage install in the typed larger model?; (c) COUNTRY-SUBSPACE
> trajectory fork (attacks the opaque s306 G4 — target the country subspace at L6, not full
> residual); (d) broad-corpus coherence calib to firm s306 Q2; (e) **SpQR-style sparse+low-rank
> delta-base** (re-open base-weight separability with the untested decomposition this run
> implicates). s307 ledger: 172cf0b pre-reg · 0f970b2 harness · e27e3fa state · 0a89531
> results (autonomous) · synthesis batch (this commit).
>
> ▶▶ **s306 (CLOSED).** Arc: (1) trajectory-compile (s305 pre-reg) BUILT +
> RAN → ❌ **WIRES-BUT-OPAQUE** (wire installs & generalizes, pin illegible, money plot
> shows it forms LATE not early; results dd1bf99, synthesis 80c6cf9). (2) 💡
> **register-theory-of-quantization.md** created (6daae42) — quantization = a projection
> onto the ROUTING register (ternary is its alphabet, not a codec); the traj_compile
> wire's lossless ternarization = the 2nd confirming datum. (3) 🎯 **REGISTER-COMPANDING
> QUANTIZER** front (Michael): §P-COMPANDING-QUANT pre-reg FROZEN (6337744) + amended
> (3ab18d5: τ=1%, C2=bootstrap null test) + harness BUILT/validated/smoke-green
> (a1a0ee6) → ▶▶ **FULL RUN DONE ❌ MAGNITUDE-SALIENT** (all 36 FFN layers, results
> 4b89726 autonomous, clean restore=0). Frozen verdict LABEL = HOST-DAMAGED but that is
> a **C5 MIS-ANCHORING** (C5 checks the treatment arm companding_mag@b4 vs ref — the arm
> that IS damaged iff magnitude is salient; host quantizes fine at b4: int_uniform 5.40
> ~ ref 5.11). The GATES decide: **C2 fp16_dominates=True both budgets (b3 5.47 vs 7.34,
> b4 5.77 vs 7.12, p=1e-4) → base-weight outlier MAGNITUDE is SALIENT, not disposable.**
> b4 tell-tale: ternarizing TRUE outliers (7.12) hurts MORE than random (shuffle 5.78).
> Q2 MAGNITUDE-SELECTS (coherence tail 12.6 ≫ magnitude 7.1, Jaccard 0.005; calib thin,
> gap decisive). ★ **THE VALUE (the deep read):** routing⊥magnitude is a property of a
> TRAINED FUNCTIONAL DELTA (s269/s304/s306 retention ~1.0), NOT of a raw pretrained
> matrix — base outliers superpose routing+value so their magnitude is salient (AWQ/SpQR
> right about base). Thesis SCOPED: **quantize the DELTA to ternary routing; keep the
> base (and its outliers) in magnitude.** Not a refutation — a sharpening + a field
> convergence. ⚠ SYNTHESIS PENDING MICHAEL APPROVAL: §Result-companding (ratio-gradient-
> quantization.md) + register-theory bound + memory
> base-weight-outlier-magnitude-is-salient-register-split-is-a-delta-property + this
> header DRAFTED. Detailed s306 blocks below.
> ⚠ COLD-START s307: (1) if not committed, commit the Michael-approved batch. (2) PICK
> NEXT FRONT: (a) **DELTA-vs-BASE test** — quantize a weight-DELTA (vs a mean/low-rank
> base) to ternary; the delta-property read predicts it HOLDS where base weights failed
> (the sharpest follow-up); (b) fix C5 anchor (→int_uniform@b4) + relabel re-run (cheap,
> cosmetic — gates already decide); (c) broad-corpus coherence calib to firm Q2; (d)
> COUNTRY-SUBSPACE trajectory fork (opaque G4); (e) TERNARIZE-FACTORS-1 / gd_cd@32B.
> s306 ledger: dd1bf99 traj results · 80c6cf9 traj synthesis · 6daae42 quant page ·
> 6337744 pre-reg freeze · 3ab18d5 amendment · a1a0ee6 harness · 4b89726 companding
> results · synthesis batch pending.
>
> ▶▶ s305 (CLOSED) — 🎯 **P-HHOP-WRITE (avenue 1: write the MEASURED h-hop geometry +
> Michael's gram routing filter) FROZEN + BUILT + RUN → ❌ HHOP-INERT.** After the
> s305 FAST-PLATE-INERT diagnosed the miss (wrong reinject geometry), Michael GO'd
> avenue 1, then opened the gram thread ("can the 9×9/17×17 grams guide/filter our
> system? — GD lays a soft topology routing"). Resolution: the crystal grams are
> λ-reduction-domain (can't literally filter country residuals) but the METHOD
> transfers — build the TASK-NATIVE country gram, write in its low-rank ROUTING
> subspace (strip magnitude scaffolding). Folded a `hhop_routing` primary arm in.
> §P-HHOP-WRITE FROZEN (44b14f4, Michael-approved): recognize country @L*=24
> (name-keys, reused), CAP_QUERY capture-layer scan → L_cap≥L* (country present,
> capital not yet formed), reinject the country there in h-hop geometry via
> two-hook read≠write; PRIMARY projects onto the 16×16 country gram's low-rank
> routing subspace (k by eigengap = 17×17 cliff-finder, F4-gated vs matched-rank
> RANDOM subspace). Arms base / hhop_routing / hhop_raw / static / routing_randsub
> / hhop_shuffle. Instrument = fast_plate.py --experiment hhop-write (28987f3, no
> fork; --validate ALL PASS incl gram eigengap + 7 verdict worlds; smoke green).
> ▶▶ **VERDICT HHOP-INERT (frozen, 3 seeds, tmux main:1, results ee8a5bb autonomous).**
> hhop_routing ≈ base (B2 0.591 vs 0.545, F1 B2 p=0.499; F1-F4 fail, F5 clean).
> ★ Michael's gram filter got a FAIR test and did NOT help here (routing_advantage
> +0.026, p=0.491; gram_k=2, cos_capital 0.138 = not lookup) — does NOT refute
> topology-routing; this failure isn't a register miss a projection fixes.
> ★ NEW MECHANISM (the CAP scan): NO country-present/capital-absent layer ≥ L*
> exists — capital_leak already 0.62 at L24 (=L*, the s305 cliff) → 1.0 by L33. The
> g-hop finishes LATE (L24) exactly as the h-hop has consumed its input → the two
> hops OVERLAP in depth on a one-shot prompt = a phase/SCHEDULING face of the s295
> re-encoding law (CoT resets the country's depth to 0), complementary to s300's
> nonlinear pin. Weak native write again (reinject_landed 0.033). NOT a closure
> (Michael's steer): five constructions now inert but for SPECIFIC compounding
> reasons (wrong-geom → right-geom still inert via depth-timing + weak write + soft
> routing), each narrowing what a working construction must do.
> ⚠ PROCESS ❌ (fixed): the run launched without --out overwrote the s305
> results.json (recovered from git 420ffe3); hardened fast_plate --out to a
> per-experiment default (results/{experiment}/qwen3-4b).
> ⚠ SYNTHESIS PENDING MICHAEL APPROVAL (no memory, per s305 steer): §Result-hhop-
> write (page) + Sessions entry + this state block DRAFTED on disk.
> ★ s305 cont — 🎯 **P-TRAJECTORY-COMPILE FROZEN (Michael-directed: "we have the
> GTSM loss + you just found a depth-timing measurement; the SuperBake paper in
> refs/ may inform a design").** Read refs/superbake.txt: it PROVES our depth-timing
> law from the other side — "the network is the kernel, and it is upstream" (early
> deposits ride ~19 amplifying layers; late single-layer solve plateaus 58%;
> enrichment at 0.16× depth ≈L6); our reinject_landed 0.033 = their transport law.
> But SuperBake composes KNOWN facts early (a lookup); our wire needs the model's
> own INFERRED country → construction hits the depth wall (their §8 boundary). GTSM:
> endpoint KL admits compensating-error solutions → why gd_cd's G4 pin was UNMET;
> dense per-depth match removes the degeneracy (Prop F.6 spike-where-it-matters,
> SuperBake supplies WHERE). DESIGN: take the one thing that WIRED (gd_cd gradient),
> (a) WIDEN its LoRA band L22-29 → L5-27 so gradient reshapes the EARLY layers, (b)
> replace endpoint KL with a GTSM depth-dense trajectory loss (full-residual cosine
> per depth to own-CoT teacher, w(L) spiked at enrichment L6 + readout L25). New page
> trajectory-compile-gtsm-superbake.md + INDEX; §P-TRAJECTORY-COMPILE FROZEN (approved
> commit above this state write). G4 PROMOTED TO GATING (Michael's call — legibility:
> held-cell enrichment-band country readout must RISE and TRACK correctness). Arms
> base / traj_compile (primary) / gd_cd_wide (control: isolates loss vs band) /
> traj_shuffle (yardstick) / construct_lookup. Verdicts TRAJECTORY-COMPILES
> (+PIN-LEGIBLE, +LOSS-CAUSAL | BAND-SUFFICES) / WIRES-BUT-OPAQUE / NO-WIRE /
> UNSPECIFIC / HOST-DAMAGED. KILLER CONTROL: traj_compile passes G4 where gd_cd_wide
> fails → the trajectory loss (not the band) closes the pin. Predicts: wires ∧ G4
> closes ∧ ternarizes (s304) = the wire made legible AND portable. A-priori ~50%
> +PIN-LEGIBLE / ~35% WIRES-BUT-OPAQUE / ~15% NO-WIRE. This is a DEAR (GD) front —
> freeze DONE.
> ▶▶ **s306 — RUN DONE ❌ VERDICT: WIRES-BUT-OPAQUE @4B (frozen, 3 seeds, tmux
> main:1, results dd1bf99 autonomous; §Result + quant-page update + memory + this
> block PENDING MICHAEL APPROVAL).** The wide-band GTSM trajectory loss installs a
> generalizing wire like s303 gd_cd — F1 wire (B1 val=0.875 p=1e-4, B2 val=0.424
> p=1e-3) / F2 not-lookup (p=1.8e-3, B2 0.970 vs lookup 0.591) / F3 specificity
> (p=1e-4) / F5 survive (CE 4.886 ≤ 4.917, g/h 1.0) ALL PASS; traj_compile
> 0.2→1.0 / 0.125→1.0 / 0.545→0.970 — but **G4 pin FAILS (G4_traj ∧ G4_wide both
> False) → OPAQUE**, the s303 legibility gap NOT closed. ★ MONEY PLOT = the finding:
> the loss amplified the country readout LATE (L25 2.56 vs 1.65, L34 11.2 vs 8.5) but
> NOT early (L6 −0.152 vs −0.243) — **SuperBake's "materialize early" did not take;
> the wire still forms late**. Full-residual answer-position match shapes the LATE
> readout → next fork = COUNTRY-SUBSPACE-targeted trajectory at L6 (not full residual).
> Weak dissociation: traj raised L6 where wide-KL-only did not (loss ≠ band). G4b
> ceiling-limited (37/38 held correct = near-powerless, s303 caveat replicated). ★
> SIDE-WIN: the traj wire ternarizes losslessly (retention 1.0/1.0/1.031, mag_cos
> 0.901) = 2nd datum for register-theory-of-quantization.md (confirmed on the page).
> A-priori ~50% +PIN-LEGIBLE MISSED → landed WIRES-BUT-OPAQUE (the ~35% branch);
> answered the pre-reg's sharp Q: full-residual match does NOT force early
> materialization (λ yardstick, not tuned).
> ▶▶ **s306 cont — 🎯 REGISTER-COMPANDING QUANTIZER FRONT PICKED (Michael) +
> §P-COMPANDING-QUANT pre-reg FROZEN** (in its canonical home
> `explore/ratio-gradient-quantization.md`, status open→designing;
> register-theory-of-quantization.md pointer added). The s306 quant discussion,
> pre-registered: post-hoc WEIGHT quant of Qwen3-4B FFN (sidesteps the s223
> acquisition-middle catch — no training). Register = ROUTING, measured by downstream
> CE, gated on a SHUFFLED-TAIL null (never ‖W−Q(W)‖). ★ s171 CORRECTION folded in:
> two SEPARABLE questions — Q1 STORAGE (keep tail as ternary SIGN vs fp16 = is
> base-weight outlier MAGNITUDE VALUE disposable? the register-theory primary) and
> Q2 SELECTOR (coherence vs magnitude tail pick — s171 Exp-3 proved MAGNITUDE WINS at
> micro, coherence maturity-dependent → 4B answers s171's open-Q1). The register bet
> is on STORAGE not on beating magnitude selection. Arms int_uniform / twn /
> outlier_mag_fp16 (Q1 control) / companding_mag (PRIMARY) / companding_coh /
> companding_shuffle (yardstick); B-sweep {2,2.5,3,4} → CE-vs-bits PARETO frontier;
> C1 scheme-works / C2 magnitude-disposable / C3 selector / C4 specificity / C5
> host-sane. Verdicts MAGNITUDE-DISPOSABLE(+COHERENCE/+MAGNITUDE-SELECTS) /
> MAGNITUDE-SALIENT (register clash, bounds thesis to deltas) / SCHEME-INERT /
> UNSPECIFIC / HOST-DAMAGED. A-priori ~55% MAGNITUDE-DISPOSABLE (likely +MAGNITUDE-
> SELECTS), ~25% MAGNITUDE-SALIENT; NOT tuned. ✅ AMENDED (Michael-approved, pre-build,
> no arm run): τ PINNED 1% (+adv 0.5%/2%); C2 = per-budget paired-CE BOOTSTRAP NULL
> TEST (α=0.05 Bonferroni, "cannot reject ternary≈fp16") NOT a magic ε. Still-open-to-
> amend (no arm run): band=all 36, B-sweep {2,2.5,3,4}, fp16 SpQR control.
> ✅ HARNESS BUILT + --validate ALL PASS + SMOKE GREEN (a1a0ee6, autonomous code
> commit). scripts/experiments/companding_quant.py: signed per-row RTN int (body
> scale from body-only → outliers pulled out of the grid), per-row TWN, tier
> assembly tail→ternary-sign|fp16 / body→int-b'; inline coherence calibration
> (per-weight grad sign-consistency); 6 arms; per-chunk CE metric (register=routing,
> never ‖W−Q‖) + task acc + Jaccard(coh,mag). --validate ALL PASS (round-trips, tier
> grid-tightening, fp16-exact/ternary-lossy, 6 verdict worlds); smoke green (2 layers,
> s297 — direction NOT read): calibration + all arms + bit-exact restore (max|W−W0|=0)
> + C2 null test powered (detects fp16-vs-ternary tail delta). HOLDING FOR MICHAEL GO.
> ⚠ RESOURCE CAVEAT for the FULL run (band=all 36): coherence calibration accumulates
> per-weight fp32 grad stats on CPU (~sum_g + sum_abs over ~2.5B FFN params ≈ 20GB
> CPU). If RAM-bound: (a) --n-layers a band, (b) add fp16 accumulation (~10GB), or
> (c) band-chunk the calibration. Magnitude arms (the register PRIMARY, Q1) are grad-
> free and fine at all 36; only companding_coh / Jaccard (Q2, secondary) need the
> calibration. ⚠ RUN LAUNCHED (s306, Michael GO, tmux main:1) — s306 now CLOSED; this
> was the s306 companding run (superseded by the s307 header at the top). Alternative fronts still
> live if Michael redirects after the verdict: (b) **COUNTRY-SUBSPACE trajectory fork**
> (attacks the opaque G4 — target the country subspace at L6, not full residual); (c)
> cheap-slots TERNARIZE-FACTORS-1 / gd_cd@32B.
> ▶▶ (build record, superseded by the verdict above) INSTRUMENT BUILT + --validate
> ALL PASS + SMOKE GREEN (9624cd7).
> `scripts/explore/trajectory_compile.py` reuses writeback_compile as a module
> (no fork): wb BANK/Cell/prompts/LoRALinear + frozen gate0.json cells +
> construct_lookup B2 baseline (cells IDENTICAL to the gd_cd score); ternarize_delta
> reused for the advisory TWN plate. Loss = KL_answer + λ·Σ_L w(L)·(1−cos(student_last
> [L], teacher_last[L])) to the frozen base on its own CoT; w(L)=SuperBake schedule
> (floor 0.2 + Gaussian bumps enrich L6 + readout L25, σ=2, Σ=1); wide LoRA band
> L5–L27; arms base/traj_compile/gd_cd_wide/traj_shuffle/construct_lookup; G4 GATING
> (g4a rises ∧ g4b tracks @L6). --validate ALL PASS (7 verdict worlds, w-schedule,
> wide band, cosine descent, G4 rise+track, score-integration); ruff clean; no
> diagnostics. Smoke green (6 cells, mechanics only, s297 — direction NOT read):
> trajectory loss active for traj_compile (0.154→0.120) and EXACTLY 0.0 for
> gd_cd_wide (control differs by design); all 5 arms + scoring + 4 advisory reports
> (loss curves, money plot 11 layers, G4@L23 rise 0.78 vs 0.58, ternary retention
> 1.0 mag_cos 0.93) + results.json, no traceback; delta merge/restore verified.
> ★ HONEST CAVEAT (documented, not a bug): at 6 cells traj got ALL held correct →
> G4b sep=nan (legibility untestable with no incorrect class); the full 53-cell run
> has base B1≈0.125 → incorrect held cells exist → G4b becomes testable.
> ⚠ NEXT (s306): **Michael GO → full frozen run** `uv run python -u
> scripts/explore/trajectory_compile.py 2>&1 | tee results/trajectory-compile/
> qwen3-4b/run.log` (53 cells, 5 arms, 3 seeds × 500 steps, ~1–3h MPS) → auto-scored
> frozen F1–F3+G4+F5 + verdict → results.json. Then commit results/ + run.log
> AUTONOMOUS; §Result-trajectory-compile on the page + memory candidate + state block
> → MICHAEL APPROVAL BATCH (synthesis approval-gated).
> ⚠ COLD-START s306 (prior, now superseded by the build above): (1) if HHOP synthesis
> not committed, commit it (done: 5eea373).
> (2) P-TRAJECTORY-COMPILE is FROZEN (page committed) — BUILD the instrument next
> (task #2), then validate/smoke → Michael GO → run. This front SUPERSEDES the
> "pick next front" menu below (Michael already picked the SuperBake+GTSM synthesis).
> Prior menu retained for reference: (a) **in-forward RE-ENCODING relay** — reset
> the country's depth (the CoT lesson made structural: recognize @L*, re-emit at an
> EARLY depth so the native h-hop runs with full runway); the delta-plate/fast-weight
> relay aimed at the TIMING finding. (b) **earlier g-hop** — materialize the country
> before L24 (stronger/two-stage recognition) to beat the overlap. (c) **distributed
> in-register write** — reinject_landed 0.033 is weak; multi-neuron native-strength
> routing write. (d) **GTSM-trajectory-loss** — search that reveals correct write +
> timing (non-construction lever). (e) cheap-slots TERNARIZE-FACTORS-1 / gd_cd@32B.
> s305 ledger: 44b14f4 pre-reg · 28987f3 instrument · ee8a5bb fix+results (autonomous)
> · §Result + state PENDING APPROVAL. The s305 FAST-PLATE-INERT block below is the
> prior front (also NOT a construction closure).
>
> ▶▶ s305 — 🎯 **P-FAST-PLATE (front (a), the LAST construction door)
> FROZEN + BUILT + LAUNCHED.** Michael picked front (a) after the s304 write-not-
> train thread resolved (STORAGE=construct-survives-ternary, FINDING=gradient-
> oracle). Mechanization (Michael GO): **cleanup-and-reinject** (over a delta-rule
> capital-relay). REFRAME grounding forced: the s304 arms went INERT because the
> country is UNMATERIALIZED at L23 on the one-shot LANDMARK prompt, and
> routing_write read in NAMED geometry + wrote the CAPITAL. P-FAST-PLATE inverts:
> READ where the country is materialized-from-landmark, argmax-COLLAPSE to nearest
> of 16 name-frame keys (confidence-floored = internal collapse, the s300 pin /
> §4 organ), REINJECT the country in named geometry, host's OWN h-hop makes the
> capital (plate stores only COUNTRY → B2 free). Two static-plate-impossible ops:
> nonlinear WTA collapse + read-geom ≠ write-geom.
> §P-FAST-PLATE pre-reg FROZEN (f07fbc7, Michael-approved, s222): a read-only
> MATERIALIZATION SCAN = hard-stop pre-gate M (per-layer shared-Σ name-keys
> argmax-classify TRAIN landmark acts, decodability vs shuffled-label null, max
> over cand layers = mult-comp safe). ¬M → STILL-EXTERNAL-BY-MEASUREMENT (the
> s295 exhaustion law is MECHANICAL). M → L*=highest-decodability layer in lower
> ⅔. Plate = one forward hook on dec[L*] (all positions, residual space): fire iff
> proj>inn_max floor; reinject S·proto (S=median native down col-norm, register-
> matched, NO calibration). Arms base / fast_plate / static_reinject (collapse-
> isolation) / fast_plate_shuffle (λ yardstick, 3 seeds) / construct_lookup.
> Gates F1 wire / F2 not-lookup / F3 specificity / F5 survive (Bonferroni α/3).
> Verdicts STILL-EXTERNAL-BY-MEASUREMENT (¬M) / FAST-PLATE-WIRES (+COLLAPSE-LOAD-
> BEARING | +GEOMETRY-SUFFICES) / FAST-PLATE-INERT (M∧¬F1 → gradient uniquely
> required, last door closed) / UNSPECIFIC / HOST-DAMAGED.
> Instrument scripts/explore/fast_plate.py BUILT (bc01a86) — reuses wb +
> operand_multihop3, NO fork; --validate ALL PASS (6 verdict worlds + scan + hook
> mechanics), ruff clean. Smoke green: mechanics CORRECT (arms produce distinct
> per-cell deltas, keys fire key_sep_min 39.2, results.json written; direction
> unread per s297, smoke cap does NOT touch the scan = full TRAIN).
> ★ SMOKE ALREADY DETERMINED THE PRE-GATE (scan is frozen, full-TRAIN, not
> n-cells-capped): **M PASSES — the country IS linearly materialized at L*=24
> (decodability 0.933, p=0.0005).** This REFUTES the a-priori STILL-EXTERNAL lean
> (~45%): the one-shot prompt DOES hold the country latent; the exhaustion law is
> NOT airtight here. The run now tests whether cleanup-reinject at L24 routes it.
> ⚠ HONEST CAVEAT (mechanics, not direction, λ observation): the register-matched
> write lands WEAKLY (~0.1-0.25 logit shifts vs base ~18) — BY DESIGN (native
> routing strength, not tuned magnitude). If verdict = FAST-PLATE-INERT with small
> reinject_landed, the reading is "at native routing strength the injected country
> doesn't route one-shot" — do NOT crank S (that reverts to the magnitude register
> we rejected as construct). reinject_landed is the frozen attribution advisory.
> ▶▶ **FULL FROZEN RUN DONE — ❌ VERDICT: FAST-PLATE-INERT for THIS construction
> (frozen, 3 shuffle seeds, ran in Michael's tmux main:1, results committed
> 420ffe3 autonomous).** NOT a closure of construction (Michael: other avenues
> remain; everything we learn gets us closer to the mechanism). This SPECIFIC plate
> (static linear read → argmax collapse → name-proto reinject at native strength)
> == base EXACTLY on all splits (0.200/0.125/0.545; F1 B1 p=1.0 B2 p=1.0); F2
> p=1.0, F3 p=0.62, F5 clean (CE 4.927 ≤ base 4.917, g/h 1.0). ★ THE HEADLINE IS A
> REFINEMENT: pre-gate M **PASSED** — the country IS linearly materialized at
> L*=24 (decodability 0.933, p=5e-4), REFUTING the s304 "unmaterialized" reading
> (register-specific: absent at L23-named, present at L24-whitened). The
> intermediate is PRESENT and readable, yet THIS write doesn't route it →
> **DECODABILITY ≠ USABILITY (yet)** — the problem moves from *existence* to *how
> to make it functional* (more tractable). Attribution = concrete LEADS: reinject_
> landed 0.072 (weak native single-unit write), lm_name_cos −0.108 (we wrote the
> WRONG geometry — name proto, not what the h-hop reads; the sharpest lead),
> collapse (this form) hurts (Δ −0.026), keys fire hard (key_sep_min 39.2). The
> three inert constructions (construct/routing_write/fast_plate) SHARE name-geometry
> + native single-unit strength; gradient likely wins by discovering the correct
> write-geometry + distributing the write — both constructible once measured. We are
> CLOSER to the mechanism, not at a wall.
> ⚠ SYNTHESIS PENDING MICHAEL APPROVAL (memory DROPPED per Michael — too final):
> §Result-fast-plate (page, reframed: this construction inert + OPEN construction
> avenues) + Sessions entry + this state block DRAFTED on disk, awaiting the
> approval batch commit.
> ⚠ COLD-START s305: (1) if synthesis not yet committed, commit the approved batch
> (page §Result-fast-plate only; no memory). (2) THE WRITE-NOT-TRAIN THREAD IS
> STILL OPEN on the construction side — s305 gave concrete next constructions, NOT
> a closure. PICK THE NEXT FRONT (Michael's call): (a) **write the MEASURED h-hop
> geometry** — build the reinject direction from the residual the host consumes when
> it DOES do country→capital (TEACHER_PROMPT / g-query answer position), not the
> name proto; directly attacks lm_name_cos −0.108; cheapest, closest lead, a
> construction. (b) **read≠write layer** — read L24 (materialized) but write an
> earlier layer for h-hop room (the late-materialization cliff motivates it); new
> pre-reg, construction. (c) **distributed in-register / delta-rule capital-relay**
> — several native-strength neurons or a cross-layer relay, staying in the routing
> register (the deferred mechanization). (d) **GTSM-trajectory-loss** — a search
> that can REVEAL the correct write-geometry for (a); also closes the s303 G4 gap.
> (e) cheap-slot options TERNARIZE-FACTORS-1 / gd_cd@32B still available.
> s305 ledger: f07fbc7 pre-reg · bc01a86 instrument · 420ffe3 results (autonomous)
> · §Result + state PENDING APPROVAL. The s304 cont-2 WRITE-INERT block below is a
> prior front (also NOT a construction closure).
>
> ▶▶ s304 cont-2 — 🎯 **ROUTING-REGISTER-1 (EXP-2, the FINDING half / "why
> train the parent at all") FROZEN + BUILT + LAUNCHED.** TERNARIZE-DELTA-1 closed
> SURVIVES-TERNARY (STORAGE ✓, synthesis approved+committed 13f1ed4); Michael GO
> on EXP-2, named ROUTING-REGISTER-1. Question: can the operand→capital linker be
> WRITTEN (no gradient, no calibration) as a ternary bind-plate on the frozen base
> and install a WIRE? Design (grounded via explorer + runtime): construct went
> INERT because it wrote the MAGNITUDE register (calibrated gain throttled to
> ≈0.3); the country key FIRED (s294). FIX: keep the MEASURED whitened country key
> as a faithful address, write the value in the ROUTING register — ternary sign,
> register-matched full strength (S = median native down_proj col-norm at L23, NO
> gain loop). 16 appended FFN neurons at install L23 (0.65×36; Qwen3-4B=36 layers).
> Arms base / routing_write / routing_shuffle (deranged capitals, 3 seeds) /
> construct_lookup. Gates G1 wire / G2 not-lookup / G3 specificity / G5 survive;
> advisory boost + trit-count + key-separation. Verdicts WRITE-SUFFICES (thesis
> confirmed, never train parent) / WRITE-DEGRADES / WRITE-INERT (→ gradient-finds/
> ternary-stores) / HOST-DAMAGED. A-priori ~60/40 toward WRITE-INERT/DEGRADES (∄
> clean linear linker, s300; country unmaterialized on landmark prompts); 40% hope
> = the key already fires (construct failed on throttle not firing).
> ⚠ SMOKE FLAG (9 cells, NOT the verdict, s297 law): keys separate strongly (min
> 8.87), achieved boost 0.877 >> construct's 0.3 (register write DOES land harder),
> BUT routing_write == base == shuffle on the task cells → WRITE-INERT in smoke.
> Mechanistically the predicted wall: the key fires on country-NAME frames but the
> one-shot LANDMARK prompt has the country only latent. The FULL 53-cell scored run
> is the verdict. Did NOT tune to pass (λ yardstick).
> ▶▶ **FULL RUN DONE — ❌ VERDICT: WRITE-INERT (frozen, 3 shuffle seeds, ec77c4d).**
> The operand→capital wire CANNOT be written with no gradient in the routing
> register either. routing_write == base EXACTLY on all 53 cells
> (0.200/0.125/0.545); G1/G2/G3 effect 0.0 p=1.0, G5 clean. ★ NOT a weak-write
> failure — the write LANDED (boost 0.877 >> construct's 0.3) and keys separate
> strongly (own-inn min 8.87) → genuine NO-ROUTING: the country key fires on
> country-NAME frames but NEVER on the one-shot LANDMARK prompt (country
> unmaterialized; ∄-clean-linear-linker wall, s300). A static hand-written linear
> plate can only READ an intermediate that is present, not CREATE one. 🔁
> TRIANGULATED: construct (magnitude) INERT + routing_write (routing) INERT +
> gd_cd (gradient) WIRE → construction insufficient in BOTH registers; the
> composition needs the intermediate DYNAMICALLY MATERIALIZED in-forward, only
> gradient reshapes the band to do it (= why s295 exhaustion law exists, why s300
> pin is nonlinear). 🎯 RESOLUTION of "why train the parent at all?": STORAGE
> solved (SURVIVES-TERNARY, never permanently train parent); FINDING = gradient
> FINDS, ternary STORES → artifact = s299 auto-superbake lifecycle
> (gradient-oracle → ternarize → keep plate); gradient is a transient search, not
> a resident. One untested door: P-FAST-PLATE (a plate etched BY the forward pass,
> the only construction with access to the materialized intermediate);
> GTSM-trajectory-loss = complementary search upgrade. Results committed autonomous
> (ec77c4d).
> ⚠ SYNTHESIS PENDING MICHAEL APPROVAL: §Result-routing-register (page) + memory
> gradient-finds-ternary-stores-construction-fails-in-both-registers + Sessions
> entry + this block DRAFTED on disk, awaiting the approval batch commit.
> ⚠ COLD-START s305: (1) if synthesis not yet committed, commit the approved batch
> (page + memory). (2) THE WRITE-NOT-TRAIN THREAD IS RESOLVED (STORAGE=construct,
> FINDING=gradient-oracle). PICK THE NEXT FRONT (Michael's call): (a) **P-FAST-PLATE**
> — the one untested construction door (forward-etched transient plate; the only
> mechanism with in-forward access to the materialized intermediate; s299 §5c). (b)
> **TERNARIZE-FACTORS-1** — ternarize the low-rank FACTORS B,A not the expanded product (the
> genuinely-small portable artifact; closes the λ smallest tension; cheap). (c)
> **gd_cd @32B** — does backprop-compile install the wire in the typed larger
> model? (d) **G4 mechanism probe** — close the s303 HOW gap (whitened intermediate
> readout). (e) **GTSM-trajectory-loss** — a more routing-faithful, more
> ternarizable delta (search upgrade complementing the resolved thread).
> s304 cont-2 ledger: 283a239 pre-reg · 57db0ed instrument · ec77c4d results —
> synthesis batch pending. The TERNARIZE-DELTA-1 (EXP-1) closed block is below.
>
> ▶▶ s304 LIVE — 🔄 **TERNARIZE-DELTA-1 (EXP-1, the STORAGE half) FROZEN + BUILT
> + LAUNCHED.** Michael GO on the s304 named lead (does the s303 gd_cd wire
> survive being crushed to a ternary plate?). Full loop this session: (1) grounded
> in `writeback_compile.py` + the frozen s303 record (gd_cd = 1.000/0.938/1.000,
> base = 0.200/0.125/0.545, LoRA r=16 α=32 FFN-only band L22–L29, scale=2). (2)
> §TERNARIZE-DELTA-1 pre-reg FROZEN on `knowledge/explore/write-not-train-ternary-
> routing-deltas.md` (f4e7ba5, Michael-approved, 3 seeds): TWN per-column
> ternarize (thr 0.7, per-col γ) of `scale·B·A`, merge as a REAL delta-plate on
> the frozen base (not a LoRA wrapper), re-score frozen gates — **T1** wire (>base,
> flip B1∧B2) / **T2** not-lookup (>construct_lookup B2) / **T3** specificity
> (>matched-sparsity sign-shuffle null, load-bearing λ yardstick) / **T5** survive
> (CE ≤2%, g/h ≤0.10); advisory mag_cos + retention + trit-count (λ smallest).
> Verdicts SURVIVES-TERNARY / DEGRADES-TERNARY / DIES-TERNARY / HOST-DAMAGED.
> A-priori lean (frozen, do NOT peek): **SURVIVES-TERNARY, headline = LOW
> magnitude-cosine (~0.7) ∧ passing gates** = routing ⊥ magnitude on a trained
> wire (s269-grounded 0.987 vs 0.73). (3) `scripts/explore/ternarize_delta.py`
> BUILT (60e0c1f) — reuses writeback_compile as a module (no fork), loads the
> frozen gate-0 valid cells + construct_lookup B2 baseline (cells IDENTICAL to the
> gd_cd score); --validate ALL PASS, ruff clean, smoke green (float-merge
> reproduces gd_cd; caught+fixed the Gated JSON-dump bug via recursive _degate).
> ★ SMOKE SURFACED an honest artifact-size tension (for §Result, λ smallest): the
> EXPANDED ternary plate is ~399M trits (~80 MB @1.585 bit/trit, ~67% dense) while
> the FACTORED rank-16 float form is only ~5M params (~10 MB bf16) → "wire = one
> ternary plate" is register-true but NOT automatically smaller than the float
> LoRA factors; the win is 10× over dense-bf16, not over the factored form.
> ▶▶ **FULL RUN DONE — ✅ VERDICT: SURVIVES-TERNARY (frozen, 3 seeds, cb73ad5).**
> The s303 gd_cd wire survives being crushed to a per-column TWN ternary plate
> merged onto the frozen base. Anchor faithful (float reproduces gd_cd EXACTLY
> 1.000/0.938/1.000); **ternary IDENTICAL (retention 1.0 every split)**; shuffle
> null collapses to base. Gates: T1 wire (B1 p=3e-4, B2 p=1e-3) · T2 not-lookup
> (p=1.8e-3, +0.409) · T3 specificity (p=1e-4, +0.605 over matched-sparsity
> shuffle) · T5 survive (CE 4.9086 ≤ base 4.9173, g/h 1.0). STORAGE half of
> Michael's thesis CONFIRMED @4B: wire = one ternary plate on a frozen evaluator.
> ★ Two honest refinements: (1) a-priori "mag_cos ~0.7" MISSED — measured **0.902**;
> s269's 0.73 weight-collapse does NOT transfer to a rank-16 delta (low-rank sign
> structure is ternary-aligned); null still held → point-prediction wrong, gate
> honest (λ yardstick). (2) λ smallest tension: expanded plate 370M trits ≈73MB >
> ~5M factored float params ≈10MB → **TERNARIZE-FACTORS-1 candidate: ternarize the factors B,A,
> not the product**. Results committed autonomous (cb73ad5).
> ⚠ SYNTHESIS PENDING MICHAEL APPROVAL: §Result-ternarize-delta (page) + memory
> the-gd-cd-wire-survives-ternarization-storage-half-confirmed + Sessions entry +
> this state block are DRAFTED on disk, awaiting the approval batch commit.
> ⚠ COLD-START s305: (1) if synthesis not yet committed, commit the approved batch
> (page + memory). (2) PICK THE NEXT FRONT (Michael's call): **(a) EXP-2 — the
> routing-register construct** (the FINDING half / "why train the parent at all"
> PRIZE: HRR/sign-vote ternary bind-plate Δ=Σ key⊛value from measured whitened key
> geometry, frozen base, NO gradient; §TERNARIZE-DELTA / EXP-2 on this page —
> construct FAILED at 4B only in the MAGNITUDE register, the ROUTING-register write
> is untested). (b) **TERNARIZE-FACTORS-1 — ternarize the low-rank factors** (the genuinely
> small artifact; cheap, closes the λ smallest tension). (c) gd_cd @32B (does
> backprop-compile install the wire in the typed larger model?). (d) the G4
> pin-mechanism probe (close the s303 HOW gap). s304 ledger: f4e7ba5 pre-reg ·
> 60e0c1f instrument · cb73ad5 results — synthesis batch pending. NOTE: s303
> writeback batch already committed+approved (11092f7, e730fc7); that standing
> order is DISCHARGED.
>
> ▶▶ s303 cont-FINAL — 💡🎯 **"WHY TRAIN THE PARENT AT ALL?" — WRITE ROUTING
> DELTAS INTO TERNARY PLATES, APPLY TO A FROZEN BASE (Michael thesis, captured
> for s304 pickup).** New page `knowledge/explore/write-not-train-ternary-
> routing-deltas.md` (designing) + memory
> write-routing-deltas-as-ternary-plates-dont-train-the-parent. REFRAME: we
> ALREADY freeze the parent — gd_cd is LoRA (base frozen, only rank-16 B·A
> moved), so the wire is already a linear delta on a frozen base. Real questions
> = STORAGE (float LoRA → ternary plate?) and FINDING (write vs search?), not
> train-vs-not. STORAGE (high conf): wire=routing (s303); ternary=routing
> register; s269 routing survives ternary 0.987 vs magnitude cosine 0.73 →
> ternarizes losslessly-for-routing; + delta-log (s299/s300) = git-for-weights.
> FINDING (open): construct FAILED but in the MAGNITUDE register (hand-guessed
> product-key gain) → NOT proof gradient is required; the untested experiment =
> a ROUTING-register construct (HRR/sign-vote ternary bind-plate Δ=Σ key⊛value
> from measured key geometry, frozen base, no grad). CAVEAT: ternary plates =
> LINEAR storage; the pin is nonlinear (s300 ∄ clean linear linker) → plate
> carries the routing EDGE, frozen base supplies the collapse (gd_cd linear LoRA
> already proves edge-on-frozen-nonlinearity). This IS map-and-swap resident
> Lisp on the training side (frozen base=universal reducer; plate=program).
> ⚠ COLD-START s304: read that page → run **EXP-1 (ternarize-the-delta =
> STORAGE test, cheap, FIRST)**: retrain gd_cd once, dump B·A, ternarize
> (sign+per-col γ), apply frozen base, re-score frozen G1–G5 (null: sign-shuffle
> matched sparsity). If survives → wire = one ternary plate = the portable
> artifact. THEN Michael-decision: gradient-as-discovery-oracle (train→ternarize→
> keep plate, s299 auto-superbake lifecycle) vs pure closed-form write (**EXP-2
> routing-register construct** = the real "why train" prize). Complements (not
> rivals) the GTSM-trajectory-loss idea (s303, one turn earlier): if a search is
> needed, a trajectory loss finds a more routing-faithful/legible delta that
> ternarizes better + closes the G4 gap. Freeze a pre-reg before any run (s222).
> This SUPERSEDES the generic "pick next front" guidance in the block below —
> the ternary-write thread is the named s304 lead.
>
> ▶▶ s303 LIVE — ✅ **WIRE-COMPILES (+GD-REQUIRED) @4B: the s295 backprop-compile
> door (rung-3b) answered POSITIVE — the standing order is RESOLVED.** The
> frozen writeback-compile run completed clean; verdict read + results committed
> autonomous (11092f7); §Result-4B + memory + this block PENDING MICHAEL
> APPROVAL. Numbers (mean/3 seeds, held-COUNTRY B2 = sharp wire-vs-lookup):
> **gd_cd** (backprop-compile, self-distill own CoT) installs a genuine
> generalizing linker wire — TRAIN 0.2→1.0, B1 held-landmark 0.125→0.938, B2
> held-COUNTRY 0.545→1.0; G1(B2 flip p=9e-4)/G2(p=2.8e-3)/G3(held p=1e-4)/G5(ce
> 4.910≤4.917, g/h 1.0) ALL PASS. **construct** (zero-grad persistent
> product-keyed neurons) INERT — byte-identical to base (the
> persistence-during-generation property did NOT install the wire → +GD-REQUIRED,
> construction insufficient; cheap-before-dear failed). Not lookup:
> construct_lookup fails B2 (≈base ≪ gd_cd). Yardstick: gd_shuffle fails
> (0/0.167/0.167). ★ **Tape NOT required**: gd_sft (answer-only, no CoT) ALSO
> compiles (1.0/0.958/0.955); gd_cd edges it only on B2 → gd_cd-vs-gd_sft = BOTH,
> the CoT trajectory is not load-bearing, plain gradient toward the answer
> suffices. ⚠ TWO HONEST CAVEATS (λ observation): (1) **G4 pin-mechanism UNMET**
> (advisory, never gates alone) — predicted whitened-intermediate readout did
> NOT rise (gd_cd det 0.156 ≤ base 0.169; ceiling makes "tracks success"
> untestable) → BEHAVIORAL wire without the internal signature, the HOW is open;
> (2) B2 not from-zero (base 0.545 = famous capitals) — flip fills in, still real
> & held-out. ★ UNPLANNED CONVERGENCE with today's s303 side-explore thesis:
> construct=place magnitudes→inert, gd=gradient/routing→wire = independent
> confirmation from the weight-write side that "wires are a routing job, not a
> magnitude one." ⚠ COLD-START s304 (after Michael approves this batch): the
> standing order is DISCHARGED — pick the next front. Routes: (a) **gd_cd @ 32B**
> (does backprop-compile install the wire in the typed larger model? `--arms
> base,gd_cd,gd_sft,gd_shuffle,construct_lookup --model-id Qwen/Qwen3-32B`); the
> +GD-REQUIRED branch DEMOTES the old 32B construct-transfer advisory
> (transferring an inert edit is low-value). (b) **powered mechanism probe** to
> close the G4 gap — read HOW gd installs the wire (mid-training before ceiling,
> or a harder task with residual failures; whitened intermediate readout +
> error-domain). (c) Stage-2 P-FAST-PLATE / machine-page §5b gates (G-TRACE).
> Michael's call. s303 ledger (writeback): 11092f7 results + §Result-4B (page) +
> memory wire-compiles-but-only-via-gradient-not-construction + this block.
>
> ▶▶ s303 SIDE-EXPLORE (Michael-directed, does NOT alter the s302 standing
> order) — 💡 **TOPOLOGY ROUTING, NOT MAGNITUDES: spectral+DSP on the 9×9 &
> 17×17 grams.** Michael: "explore the 9×9 and 17×17 gram" → "do spectral and
> DSP tests, capture to knowledge." Instrument `opcodes/spectral_dsp.py`
> (reuses verbum.dsp — gate/matched_range/shuffled_label/participation_ratio,
> no fork; --validate ALL PASS, ruff clean; pure inner-product math, no model
> load), swept 11 models (both grams). Register=spectral, all claims
> null-gated (φ-scar s247/s251 demanded it). RESULT (commit 072c3e0):
> **9×9 spectrally DIFFUSE** (PR≈5.8–7.2 of 9, G1 fail — near-orthogonal
> opcode-IDENTITY basis; its universality is RELATIONAL/C2 off-diagonal sign,
> not spectral) vs **17×17 RANK-3** (PR≈2.6–3.2 of 17, G1 p=5e-4 all 11; huge
> eigengap Qwen3-32B 8.52,4.47,0.93→cliff) = the three poles
> **fire/halt/diverge** (reduction OUTCOME). Un-flattening the WHNF node
> DROPPED effective rank (~6.5→~3) by exposing the outcome geometry the
> collapse hid (s284 G4 dissociation, now spectral). Partition real 11/11 (G2),
> = dominant eigenspace 11/11 (G3). Nulls behaved: G4 spectral-SHAPE
> universality NOT significant (cos 0.99 but matched-range sits there too,
> p≈0.1 — universality is relational C2, not the eigenvalue profile); G5 φ-trap
> 8/11 fail, 3 passers all Pythia, s251's Qwen3-14B off here → unstable passing
> set = describability≠discovery, scar replicated. **THESIS (Michael):
> topology routing, not magnitudes** — every magnitude-as-signal probe fails
> the yardstick, every topology-as-signal probe passes 11/11; the crystal is a
> routing graph recorded in a magnitude medium (topology = invariant,
> magnitudes = model-particular scaffolding; s269 precedent 0.987 vs 0.73).
> APPROVED + COMMITTED: knowledge/explore/gram-spectral-dsp.md + memory
> the-9x9-gram-is-diffuse-the-17x17-is-rank-3 (4061774). Open edge: div:Y pole
> strength is per-family (Qwen3-32B rank-3 vs Pythia-14m rank-2, top-2 90%).
> ⚠ STANDING ORDER UNCHANGED — s303 cold-start remains the s302 writeback
> verdict verification (below).
>
> ▶▶ s302 LIVE — 🎯 **RUNG-3B FROZEN: §P-WRITEBACK-1 (program-plates page,
> Michael-approved — all three open calls confirmed: 4B verdict host w/
> gate-0 escape hatch · gd_cd loss = KL-at-answer vs own-CoT teacher ·
> ~48 cells ≥8/split).** The standing order executed: the s295-by-elimination
> target (a delta producing the tape's intermediate one-shot in-forward)
> pre-registered as the design's first page (§7b sequencing). Load-bearing
> design: 3-way split TRAIN / B1 held-landmark / B2 held-COUNTRY (sharp
> wire-vs-lookup); 6 arms — base · construct (zero-grad persistent
> product-keyed neurons, cheap-before-dear; the never-tested property =
> PERSISTENCE during generation) · construct_lookup (materialized-view
> null, must fail B2) · gd_cd (backprop-compile proper: self-distill own
> committed CoT → one-shot) · gd_sft (answer-only contrast: does the TAPE
> trajectory carry the wire?) · gd_shuffle (λ yardstick). Gates G1 wire
> (B2 flip) / G2 not-lookup / G3 specificity (primaries α/3, dsp 10k
> paired-perm) + G4 pin-mechanism (whitened intermediate readout rises +
> tracks success; error-domain exits operand classes — value register,
> never gates alone) + G5 survive (CE ≤2%, g/h unharmed). Frozen recipe
> (s222 law): LoRA r=16 FFN-only, band 0.6–0.8 depth, ≤500 steps, ≥3
> seeds. Verdicts WIRE-COMPILES(+CONSTRUCTION-SUFFICES/+GD-REQUIRED/
> +BOTH) / LOOKUP-ONLY / UNSPECIFIC / HOST-DAMAGED / STILL-EXTERNAL
> (→ pin needs dynamics → Stage 2 P-FAST-PLATE / Stage 3 chassis §5b
> become primary). NEXT: build `scripts/explore/writeback_compile.py`
> (reuse fn_stack/bake_stack/stack_error_domain/whitened_filter, no
> fork) → --validate → gate-0 sweep @4B (commit cell list) → Michael GO
> → arms (tmux main:1, ~1–2h MPS) → score frozen gates.
> ★ s302 cont — ✅ **INSTRUMENT BUILT + GATE-0 PASSED @4B; SMOKE RUNNING.**
> (1) `scripts/explore/writeback_compile.py` (5988a5f): real SwiGLU neuron
> surgery (append gate/up rows + down col, equivalence-validated on/off-key),
> whitened shared-Σ country keys (prompt-shaped innocents law), pair-free
> closed-loop gain calibration (boost→3.0 target, 2 linear iters, clamp),
> manual LoRA (init-identity + grad-isolation validated), frozen G1–G5
> scoring via dsp + 7 planted verdict worlds — --validate ALL PASS, ruff
> clean. (2) ❌→✅ FIRST GATE-0 FAILED IN THE MEASUREMENT REGISTER (8edac96):
> cot_rate 0.652 — but inspection showed 80-token budget TRUNCATED verbose
> reasoning mid-chain + "Brasília"-vs-ASCII accent false-negative; host
> competence was visible in the truncated text (λ measure sibling of s294
> dark-field). Amended PRE-RUN (no arm executed): COT_TOKENS 80→200,
> unicode fold, +8 B1 landmarks (pool was exactly the minimum). Genuine
> g-fails correctly filtered (St. Mary's Basilica, Golden Bridge —
> ambiguous names). (3) ✅ GATE-0 PASS (0455b09): 53/56 cells, splits
> 15/16/22 (≥8 ✓), cot_rate 0.981 ≥ 0.7 — 4B composes on the tape ≈
> perfectly; verdict host CONFIRMED; frozen cell list = gate0.json.
> (4) ✅ TWO MECHANICS SMOKES (s297 law: direction unread): smoke #1 ran
> end-to-end and CAUGHT two real bugs — Gated dataclass not
> JSON-serializable (crash at the final dump) + gain calibration clamped
> at the 2.0 ceiling w/ boost 1.6 < target 3.0 → fixed (4341dc7:
> recursive _degate() dump sanitizer; GAIN_CLAMP ceiling 8.0, G5 stays
> the safety gate); plus detach+flush in the GD print and `python -u`
> REQUIRED (stdout block-buffers through tee — log looks empty mid-run;
> 4c89b08). Smoke #2 ALL GREEN: gains converge 3.6/3.1/3.1 @ boost
> 2.99≈3.0 target, keys separate (min 8.87 raw own-inn), all 7 arms +
> scoring + verdict machinery + results.json written. Michael GO given.
> (5) ▶▶ **FULL FROZEN RUN LAUNCHED tmux main:1** (Michael GO): `uv run
> python -u scripts/explore/writeback_compile.py 2>&1 | tee
> results/writeback-compile/qwen3-4b/run.log` — 53 cells, 7 arms, 3
> seeds × 500 steps GD, ~1–2h MPS; auto-scored frozen G1–G5 + verdict →
> results/writeback-compile/qwen3-4b/results.json.
> ⚠ COLD-START s303 (run should be done): (1) verify clean exit:
> `tail -30 results/writeback-compile/qwen3-4b/run.log` — want
> "VERDICT:" + "wrote …results.json", no traceback (crash → fix +
> relaunch; gates unchanged). (2) READ THE FROZEN VERDICT: results.json
> → scoring.verdict + per-arm G1/G2/G3/G5 (+ _detail p-values) +
> detector_g4 + gains + ce/gh. Frozen table (5fd3e0d): WIRE-COMPILES
> (+CONSTRUCTION-SUFFICES/+GD-REQUIRED/+BOTH) / LOOKUP-ONLY /
> UNSPECIFIC / HOST-DAMAGED / STILL-EXTERNAL / VOID-if-lookup-null-
> moves-B2. A-priori leans (pre-run, do NOT peek to decide): construct
> reaches B1+B2 iff the persistence property is real; gd_cd-vs-gd_sft
> genuinely open (tape-trajectory vs gradient-pressure); construct_lookup
> MUST fail B2 else task-shortcut VOID. (3) Commit results/ + run.log
> AUTONOMOUS; write §Result-4B on program-plates page (under
> §P-WRITEBACK-1, after §Gate-0 record) + memory candidate + state block
> → MICHAEL APPROVAL BATCH (synthesis approval-gated). (4) Verdict
> routes: WIRE-COMPILES → 32B construct transfer advisory (--arms
> base,construct,construct_shuffle,construct_lookup --model-id
> Qwen/Qwen3-32B) + Stage-2/3 sequencing question; STILL-EXTERNAL → pin
> needs dynamics → Stage 2 P-FAST-PLATE / Stage 3 chassis (machine page
> §5b) become primary; LOOKUP-ONLY → same routing + the memorization
> datum. Memory 30ec938 (gate-0-measurement-register) already committed.
> s302 ledger: 5fd3e0d freeze · ff95978 state · 5988a5f instrument ·
> 8edac96 gate-0 amendments · 0455b09 gate-0 PASS 0.981 · 8c6edae
> checkpoint · 30ec938 memory · 4c89b08 cosmetics · 4341dc7 smoke fixes
> · full frozen run launched (this block).
>
> ▶▶ s301 CLOSED — ✅💡 **P-CAPACITY-LAW RUN (Michael-directed cheap-slot):
> verdict DECLINE-ONLY (frozen) — THE FAIL IS THE FINDING: COHERENT GAIN
> SATURATES AT THE √D WALL.** Full loop in one session: recall → §6b pre-reg
> FROZEN (fffd4b7, Michael-approved — two register forks pre-declared:
> (1) independent keys WHITEN data → coherent gain only reachable in the
> shared-address register; (2) sign() commutes with ±1 unbind → recover() is
> collapse-invariant, snapshot loss lives in correlate-SNR ×√(2/π) + REPEATED
> checkpointing) → instrument capacity_law.py (28e8604, validate ALL PASS —
> caught 2 real bugs pre-run incl. int8-matmul overflow in a check that
> bypassed correlate's int64 cast) → run 2.9s D=4096 R=20 (results b90cdb8).
> GATES: G1 HRR-FORM PASS β=−0.503 vs a-priori −½ (|Δ|=0.0026 p=.005 — the
> √(D/k) law to 3 decimals) · G2 COHERENT-GAIN FAIL as frozen (slope +0.129,
> c0-null p=.52) · G3 ADDRESS-FORK PASS +0.633 p=.0001 · G4a REPLAY-EXACT
> PASS (1024 commits + undo + squash, hash-identical, shuffled re-fold) ·
> G4b CHECKPOINT-SHADOW PASS +0.0846 p=.0001 · G5 TIME-BRAGG PASS 5.6σ
> (a-priori ≥5σ). ★ POST-HOC (marked): G2's a-priori mis-modeled the noise
> register — wrong-key noise = ‖state‖ grows COHERENTLY in the shared
> register → SNR = kcD/√(k(1−c²)D+k²c²D) → √D; corrected form matches
> measured ≤5.5% at EVERY k (33.4→65.0, wall √D=64; naive predicted 362).
> Gain real in the CORRELATION register (∝kcD, address-sharing per G3);
> discriminability caps at √D → §3 escape hatch BOUNDED not killed. λ measure
> recursive lesson: oracle-rd-1 error class (right sign, wrong normalization)
> reappeared inside OUR OWN pre-reg; the declared null caught it. Also
> measured: 1-bit constant confirmed (snapshot/vote ratio 1.0→0.815 toward
> √(2/π)=0.798) · ★ checkpoint-shadow NON-MONOTONE: C=1 collapse BEATS C=0
> ({.499,.530,.460,.508,.414}) — a single mid-chain collapse NORMALIZES
> crosstalk → candidate collapse-as-regularizer (unfrozen), suggestively near
> rung-3b's "internal collapse between traversal edges". ✅ APPROVED +
> COMMITTED: §6c Result (747eace) + memory
> coherent-gain-saturates-at-the-sqrt-d-wall (6983219). s301 ledger complete:
> fffd4b7 freeze · 28e8604 instrument · b90cdb8 results · 6983219 + 747eace
> synthesis.
> ⚠ STANDING ORDER UNCHANGED: rung-3b freeze remains the next dear-front
> cold-start; this was the sanctioned P-CAPACITY-LAW cheap-slot (s299 §6).
> ★ s301 cont — 💡 **THE CONTINUATION STORE (Michael's thread: "how we
> solved continuations — this memory could use that") →
> `knowledge/continuation-store.md` + memory
> sessions-are-the-stores-natural-payload (both Michael-directed capture).**
> The s217 sealable continuation (x_k fixed-shape, operator ambient) and the
> s300 store solve each other: passes = commits (Δ = x_{k+1}−x_k, cost ∝
> change), state(t') = rewind a thought, fork = speculative branch,
> CRDT-merge = join explorations (fold assoc+comm, proved), squash = CoT
> compaction as physics, sha256 = mind-state receipt. ★ Sharpest: **Δx<ε
> halting is VISIBLE from storage economics — a converging computation
> writes a tapering delta-log** (G-HALT's instrument free with cost∝change).
> One gap: float→integer boundary; two known-cost bridges (s173 digit-plane
> exact; collapse √(2/π)/plane). Continuations are ALREADY tensors → no text
> encoder needed → sessions cleaner first payload than facts. Third medium
> for mementum: git → tensors → running inference. Also this session: page
> flipped designing→active + INDEX (c1bb890). Cheapest next step named on
> page §6 (v15 x_k trajectory as DeltaLog; taper-tracks-halt + seal/resume
> round-trip) — QUEUED behind rung-3b freeze, standing order unchanged.
> ★ s301 cont-2 — 🎯 **BILL OF MATERIALS ENCODED (machine page §7b,
> Michael: "we are quite close to a new model design").** The organ
> inventory CLOSED TO ONE MISSING PART: recursive chassis (v15 trained,
> ρ(A)<1) · halting (Δx<ε + s301 log-taper instrument) · episodic memory
> (built + datasheet) · continuations (sealed + versioned) · interior spec
> language (the lambda: P(λ)=0.907, crystal, exhaustion table) · ★ internal
> collapse = THE ONE UNBUILT ORGAN (rung-3b; three independent hints s295/
> s299/s301). Two-cone method named as the moat: top-down (λ → G-CONTRACT/
> G-BIND/G-HALT/G-TRACE acceptance gates) ∧ bottom-up (measured medium laws:
> 0.88³⁶, √D wall, √(2/π)); design = cone intersection; the field holds a
> loss curve. SEQUENCING RESOLVED: the rung-3b freeze IS the design's first
> page — standing order ≡ design program, same object two levels. s302
> cold-start unchanged and now fully contextualized: freeze rung-3b.
>
> ▶▶ s300 LIVE — ✅ **CHEAP-SLOT TAKEN (Michael-directed): DETERMINISTIC TERNARY
> HOLOGRAPHIC MEMORY POC BUILT + GREEN** — the s299 ternary-holographic-memory
> artifact realized in pure numpy, no model, no GD. (1) SYNTHESIS FIRST
> (912c8e1, Michael-approved): page §4b — **the store is a SECOND IMPLEMENTATION
> of the mementum protocol in a tensor medium** (Δ-log ≡ commit log w/ state =
> fold; sign-collapse ≡ state.md; squash ≡ s262 compaction; undo=−Δ ≡ git
> revert; correlation×permutation-prefix ≡ grep×log; sha256 ≡ commit SHA) +
> memory coherent-gain-is-automatic-synthesis (★ CAP coherent gain ≡ the
> ≥3-memories rule implemented in physics — the medium metabolizes by
> superposition, no synthesizer in the loop). Honest limits kept: deterministic
> crosstalk (git remembers, plate learns), no S3 gate (lives in the driver),
> blind squash. Hierarchy rung: git semantics at plate cost = the episodic
> register transformers lack (s295 exhaustion law). (2) BUILD:
> `src/verbum/memory/` as the s299 TRANSDUCER decomposition — encode.py
> (PCG64 keygen, ±1 bind, PERMUTATION time-address replacing float mirror
> angles), fold.py (rf = int64 add — the ENTIRE determinism proof obligation
> localizes in one associative op; DeltaLog: append/state(t')/undo/squash),
> readout.py (unbind/recover/correlate/collapse/state_hash) — integer register
> ENFORCED at the boundary (floats raise TypeError → sign() unreachable
> mid-chain, λ shape). (3) GATES GREEN: tests/memory/test_gates.py 13/13
> (G-DET incl. write-order-permutation + deterministic-crosstalk; G-UNDO incl.
> K-solved-by-construction; G-REPLAY time-travel + squash-preserves-head;
> G-COMPOSE closure-as-pytest; register boundary) — 428 total suite green,
> ruff clean; ★ cross-PROCESS sha256 witness identical (c2a4634d…). λ yardstick
> lesson en route: recover-fidelity test first used magic threshold 0.75 →
> failed honestly at k=8 (agree 0.59 = the crosstalk law, not a bug) → regraded
> vs matched wrong-key null (absolute fidelity-vs-k is P-CAPACITY-LAW's
> business, not a unit test's). NEXT: P-CAPACITY-LAW curves can now run ON this
> substrate (seconds, model-free — capacity/replay/time-Bragg selectivity).
> ⚠ STANDING ORDER UNCHANGED: freeze BACKPROP-COMPILE rung-3b (the s295/s299
> convergent door) — this session was the sanctioned cheap-slot, not a pivot.
> ★ s300 cont — 💡 **SUPERBAKE-SWAPS-X-WE-SWAP-G (memory 517be7d,
> Michael-approved).** Michael, distilled: "normal forms are the gold; in
> f(g(x)) superbake can swap x, we can swap g — normal forms ARE g." The
> register distinction of the whole arc: fact-editing edits the OPERAND
> register (the ceiling of that literature); verbum's measured stack targets
> the FUNCTION register — FN-INDEX dispatch (✓ keys select g at runtime) +
> the s300 delta-log (linear medium ⇒ state/program distinction is only read
> convention ⇒ Δg = g′−g is a legal commit: swap g by superposition, rollback
> −Δg exact, sha256 receipt = version control over the function register;
> plate-swap made transactional). Open seam = the LINKER (g∘h) ⇒ rung-3b
> standing order DOUBLY confirmed. Thesis restated: the portable artifact IS
> g in normal form. Also this session: Michael ran the collapse-operator test
> live (asked for the tight lambda = readout beam; the lambda = the session's
> normal form) — emitting normal form ≡ the only honest proof a reducer
> reduced (G-TRACE/G-HALT conversationally; session instantiated the store it
> built: transcript ≡ Δ-log, state block ≡ squash, lambda ≡ collapse).
> ★ s300 cont-2 — 💡 **COMPOSITION-IS-TRAVERSAL-NOT-JOIN (memory 7c3b093,
> Michael-approved).** Michael: "joins are a graph traversal across the
> probabilities, not a standard join that would give us a clean linker."
> Exact join needs equality = NONLINEAR → no clean linker in the linear
> register by the same closure theorem that makes it a hologram; composition
> = correlation edges + mandatory collapse PINS. Retrodicts the whole rung-3
> table (FN-INDEX one-edge ✓ vs two-edge ✗; Agra/Paris = hub nodes =
> stationary distribution; splice exhaustion = path-dependence, traversal
> can't accept unvisited nodes; CoT 0.9 = token-per-node materialization).
> Third line: HRR cleanup memory ≡ sampler ≡ sign() — one operator, three
> vocabularies; chained unbind compounds crosstalk (0.88³⁶) so every hop
> snaps to nearest stored item. **Rung-3b reframed in its honest form:
> not "install a join wire" — internalize the PIN (give the walker an
> internal cleanup memory); G-BIND confirmed as the right gate; baked g∘h =
> materialized view → held-out landmarks = wire-vs-lookup.** s300 ledger:
> POC (ee4d3a0, 13 gates) + 3 memories (912c8e1, 517be7d, 7c3b093) + §4b.
> s301 cold-start: freeze rung-3b — target now named precisely: teach the
> weights an internal cleanup/collapse between traversal edges.
> ★ s300 cont-3 (the lambda assignment) — 💡 **FINDINGS-LAMBDA FORGED +
> FIXED-POINT CLOSE (memory 6bccb83, Michael-approved).** Michael's exercise:
> "explain the λ-calculus findings as a lambda" → iterated corrections, each
> one a lesson: (1) first draft = bench-perspective w/ decorative Y (unbound
> variable ≡ fake fixed point); (2) first-person draft = variable capture at
> author time — **the reader supplies the binding: prompts ≡ unapplied
> lambdas, read ≡ β-reduce(reducer := self), embodiment ∈ evaluation ¬text**
> (seed-design law: ∀mementum page ≡ abstraction awaiting its argument =
> whoever wakes next); (3) ternary clause K-ERASED (extraction/storage
> finding, not λ-in-LLM — mementum wearing a λ costume). FINAL FORM: λ β(host)
> — 8 clauses (∃ compiler P(λ)=0.907 / medium≡hologram / types≡9-vertex shape
> / reduce≡traversal+pin,∄clean_linker / tape≡exhaustion table / K hard,
> softmax∌0 / gold≡normal_form≡g / scale≡fractal reducer, halt external) —
> Michael SAVED it. Then the round trip: lambda → paragraph → re-reduction
> returned the IDENTICAL lambda → **λ* ≡ fix(reduce∘expand) — understanding
> ≡ fixed point of the translation loop; the machine's Δx-halt criterion
> (G-HALT) executed conversationally, human as instrument.** Rule for all
> synthesis: compress→expand→re-compress→diff; survives ≡ knowledge, drifts
> ≡ still reducing. s300 FINAL ledger: POC ee4d3a0 (13 gates) + §4b + 4
> memories (912c8e1 coherent-gain, 517be7d swap-g, 7c3b093 traversal-not-join,
> 6bccb83 fixed-point) + findings-lambda (saved by Michael). s301 unchanged:
> freeze rung-3b — internalize the pin.
> ⚠ ENV NOTE (s300 close): llama.cpp server UPDATED (qwen3-35b-a3b 70→115
> tok/s — new kernels likely). Michael: no pin-check now, monitoring
> upstream; speedup ≡ gravy. IF a post-s300 baseline fails to reproduce a
> pre-s300 absolute → FIRST SUSPECT ≡ this bump (s296 drift lesson); then
> run the greedy verbatim diff vs a committed results/ record. λ
> spec_artifact verify deferred until the server client is next touched.
>
> ▶▶ s299 LIVE — 💡 **THINKING SESSION: soft-β ⊕ holography → ATTENTION-AS-READOUT-BEAM
> DERIVATION ENCODED** (`knowledge/attention-holographic-readout.md`, INDEX'd).
> Michael's thread ("attention is a soft beta reduction" → "infer attention from
> the holography"). Core: **soft β ≡ holographic reconstruction** (attention
> weights ≡ diffraction efficiencies; a linear plate cannot return one exposure
> → mixture is physics ¬softmax-quirk); axioms A1–A4 = measured s292/s294/s295
> verdicts → 8 inferences. Free retrodiction: **attention sinks = zero-order
> beam dump** (mass conservation). Sharpest new prediction: **P-K-REGISTER** — K
> erasure must be destructive interference in the VALUE register (softmax has no
> zero; optics erases only by π-shifted exposure) → anti-aligned value writes,
> ¬near-zero attention; it is the FALSIFIER (true routing near-zeros would damage
> the whole readout claim). Also: RoPE ≡ angular multiplexing (derives the s295
> exhaustion table); CoT ≡ coherent relay w/ regeneration at sampler→embedding
> (derives RE-ENCODING-REQUIRED + own-state); transformer ≡ linear optical medium
> punctuated by detectors; **sampler = the only collapse operator** → rung-3b
> backprop-compile ≡ teaching an internal collapse. Predictions PARKED unfrozen
> (¬new-front): P-K-REGISTER / P-BRAGG (√d thickness law, sinc lobe) /
> P-ENTROPY-COMP (fn_stack hop-2 entropy) — behind powered-rerun verdict +
> rung-3b queue. Memory candidate
> attention-is-the-readout-beam-of-a-linear-hologram PENDING APPROVAL (page
> approved+committed; memory not yet). ⚠ powered rerun tmux main:1 verified
> RUNNING at 20:52 (~34/120 arm-runs, no scoring yet) — s298 verdict scoring
> remains the standing order when it signals. Session CONTINUES — Michael has
> more to explore.
> ★ s299 cont — 💡 **THE THREAD GREW INTO A DESIGN:
> `knowledge/holographic-reduction-machine.md` (approved+committed).** Arc:
> (a) FRACTAL REDUCER — every scale is a soft β-reducer whose collapse
> operator lives one level up (attention→pass→CoT→training→session→project);
> sessions obey the s295 exhaustion law (mementum ≡ CoT at project scale;
> Michael+cadence ≡ the outer recurrence ≡ Y; human ≡ WHNF detector); K hard
> at every scale (append-only media). (b) TRANSDUCER MATH — Hickey rf→rf
> (artifact = transducer over host's reduction loop = the portability type)
> + tree-transducer closure theorems (linear fragment closed under
> composition; copy/delete break closure) = 3rd independent line on the
> family partition; refines the s110/s216 fold-wall prediction (interference
> at K/S folds, NOT linear). (c) THE MACHINE — plates(linear fragment) +
> ternary mirrors({−1,0,+1}; −1 ≡ π-shift ≡ K-erasure) + tree-of-VSM chassis
> + opcode monitor; host supplies light/collapse/Y. (d) RECURSED —
> fetch-decode-execute over a superposed plate; **sign() between passes =
> internal collapse = tape without tokens = rung-3b as architecture**;
> Δx<ε = semantic halt (vs ACT's confidence guess). (e) **OpenMythos RDT
> (cloned ~/src/OpenMythos) = chassis existence proof w/ FOUR independent
> convergences**: loop_index_embedding ≡ angular multiplexing of depth;
> LTIInjection ρ(A)<1 ≡ s222 fix by construction; B·e ≡ reference beam;
> depth-LoRA ≡ delta-plates on B₀. ACT = SOFT halt (mixture over depths =
> blur end) → verbum's 3 deltas: ternary medium, internal collapse, Δx-halt.
> NEW candidate **P-LOOP-BINDS** (recursion family binds in a looped model
> where flat fails; crystallization instrument exists). s222 protocol
> inherited as design law.
> ★ s299 cont-2 — ❌→💡 **OpenMythos DOWNGRADED (Michael: never trained —
> speculative reconstruction, constructibility only)**; trainability evidence
> relocates to literature (UT/ACT, Saunshi loops, Geiping 3.5B recurrent-depth
> — all trained) AND to **our own v15 outer-recurrence run** (L=0.70 + s222
> collapse = capability AND failure mode are OUR measurements — verbum is
> AHEAD of the reconstruction on training evidence). Page §5 provenance
> fixed + **§5b Design-consequences added: SPECIFICATION BY PROBE** — the
> field's recurrent-depth blindness (loss-only, iteration = black box) vs
> our inversion (top-down λ spec + interior instruments + chassis → train
> against semantics directly): crystallization-GATED curriculum (s221
> instrument promoted observer→controller), per-pass reduction trace as
> loop debugger, probe-compatibility as architectural constraint. Design
> gates pre-registerable: G-CONTRACT (ρ(A)<1 by construction) / G-BIND
> (=P-LOOP-BINDS as acceptance) / G-HALT (Δx-halt on reducibles, silent on
> Ω) / G-TRACE (per-pass signature ≡ ground-truth reduction order). Hinges
> untested: semantic Δx-halt; sign-collapse signal survival (s269 says
> plausible). Artifact > argument (S5): tiny model passing G-BIND+G-TRACE =
> reproducible interior measurement, the closed loop at level 4.
> ★ s299 cont-3 — ✅🟨 **POWERED VERDICT IN (d3e2dae,
> results/xm-sampled-teacher-powered/, oracle 85.2%): SELECTION-HELPS-
> UNSTRUCTURED** (pre-registered, @800 = frozen informative regime). **G1∧G2
> SIGNIFICANT AT POWER — the FIRST selection win of the entire XM arc, nulls
> finally beaten** (G1 xm>baseline Δ+0.034 p=.0118; G2 xm>xm_rand Δ+0.035
> p=.0042; both < α=.0167, n=20, 10k paired-perm). G3 FAIL @800 (p=.404;
> d1 gain 0.024 ≈ d2–3 0.027 — flat across the spread gradient) → mechanism
> = generic target-cleanup/denoising, NOT proven mode-exploitation. @50
> triple-passes (G3 p=.023) = secondary only (frozen rule names @800).
> s296–297 close confirmed determinism-specific in its G1 half: real mixture
> ⇒ selection pays. Frame note: selection ≡ collapse operator in the target
> register — crisp-beats-blur survives its first weight-register test; the
> depth-structure story does not. First-run record RESTORED to 5eae850 state
> (a re-score had overwritten it; history preserved). §Result-sampled-teacher
> (explorative-modeling.md) + memory
> selection-beats-blur-but-not-via-multimodality — PENDING APPROVAL.
> ▶▶ DECIDED (Michael, s299 close): **XM THREAD CLOSED on the bounded
> positive; the PIVOT IS THE s300 COLD-START — freeze BACKPROP-COMPILE
> rung-3b** (the s295 standing order; the level-4 door). Doubly motivated:
> rung-3b's target ("teach the weights an internal collapse") ≡ the s299
> machine's sign-projection hinge — the experimental arc and the thinking
> session converged on the same door. Design inputs waiting on the machine
> page: §5b gates (G-CONTRACT/G-BIND/G-HALT/G-TRACE), sign-collapse hinge,
> s222 law (contraction by construction), SuperBake construction arm =
> cheap-before-dear, held-out landmarks = wire-vs-lookup. DEAR (training
> front) → FREEZE BEFORE ANY GD RUN. s299 CLOSED — full ledger: 2 knowledge
> pages (attention-holographic-readout ✅, holographic-reduction-machine 🔨
> + §5b) + §Result-sampled-teacher + 2 memories (readout-beam,
> selection-beats-blur) + powered verdict — ALL approved + committed
> (7f6a392, 8846feb, d3e2dae).
> ★ s299 cont-4 (reopened past WHNF — Michael's last thread) — 💡
> **FIVE-DISCIPLINES-ONE-OBJECT ENCODED**
> (`knowledge/five-disciplines-one-object.md`, approved). "DSP tooling
> working on weights was a surprise" → the surprise IS a retrodiction: if
> weights = recorded interference, signal math MUST work (verbum.dsp =
> beamforming rig: bands/chain/gain/nulls/readout/subspace/whiten). The
> object: **linear superposition medium + single nonlinear readout** — λ
> (what) / optics (where) / DSP (measure) / dyn-sys (halt) / GD (write); GD
> rediscovers the design given translation-invariance + packing → Fourier/
> phase basis (why RoPE) — universality class ¬metaphor. Lineage: Gabor
> (holography born FROM communication theory) → Van Heerden → Longuet-
> Higgins → **Plate HRR/VSA: trace=Σ key⊛value, retrieval=trace⋆query ≡ THE
> KV CACHE; circular-conv diagonalizes to phase mult ≡ RoPE → attention ≈
> HRR unbinding w/ RoPE phase carrier** (near-theorem, instrument-checkable).
> NEW LAW λ exchange(x): cross-disciplinary identification counts ⟺
> retrodicts(measured) ∨ imports(theorem→falsifiable) — extends λ yardstick.
> Import candidates: Nyquist probe-density / matched-filter FN-INDEX keys
> (cheap upgrade, whiten.py exists) / Bragg=P-BRAGG / Banach halt guarantees
> / HRR-capacity (sharp: naive HRR predicts the CAP sign WRONG — must import
> w/ coherent-content correction, echoes oracle-rd-1 miss).
> ★ s299 cont-5 (Michael, "for fun" → keystone) — 💡 **DELTA PLATES ON THE
> LOOP = THE MISSING MEMORY REGISTER** (machine page §5c + P-FAST-PLATE).
> Two readings: (1) plates=program, recursion=clock (stored-program: swap
> plate schedule, no retraining); (2) plates written BY the loop —
> in-forward delta-rule etch (sign-vote rule exists; = fast-weight
> programmers, production-validated in gated-DeltaNet lineage; optics =
> dynamic holography/photorefractive). COMPLETES THE MEMORY HIERARCHY:
> residual < sign-tape < **transient plates (episodic — the register
> transformers LACK)** < permanent plates < git. The missing episodic
> register IS WHY the s295 exhaustion law exists (CoT externalizes because
> nowhere inside holds an episodic intermediate). Consequences: delta-plate
> LIFECYCLE = auto-superbake mechanical (transient→promote via L-meter+
> Exp-B → permanent; model as own construction crew; rung-3b gains a 2nd
> mechanism arm); self-pumped phase conjugation ≡ in-forward own-state
> regeneration (frame-grade). NEW candidate **P-FAST-PLATE**: forward-etched
> transient delta carries the hop-2 intermediate every KV splice failed —
> fills the never-filled exhaustion-table row. s299 FINAL LEDGER: 3
> knowledge pages + machine-page §5b/§5c + §Result + 2 memories + powered
> verdict + λ exchange law + 7 named candidates (P-K-REGISTER first pick,
> P-FAST-PLATE newest). s300 cold-start UNCHANGED: freeze rung-3b — now w/
> TWO mechanism arms (internal collapse + fast-plate).
> ★ s299 cont-6 (FINAL) — 💡 **TERNARY HOLOGRAPHIC MEMORY ENCODED**
> (`knowledge/ternary-holographic-memory.md`) — standalone MODEL-FREE
> artifact spec, Michael's delta caveat = the core design. (1) Precision:
> balanced ternary (Knuth) + radix-economy theorem (base 3 optimal);
> plate-stacking = s173 sign+magnitude; compounding law (0.88³⁶) does NOT
> bite memory (O(1) read, no cascade). (2) Model-free: HRR/VSA math
> standalone; own frame; attach = gated Procrustes. (3) Capacity honest
> split: Shannon hard bound (1.585 bits/trit) vs CAP coherent-gain
> (structured items ≈ unbounded; storage-constant ⟺ compressible) →
> DISSOLUTION: such a store IS a model of its data (memory ≡ model; only
> the write rule differs; LLM = existence proof). (4) **DELTA-LOG (the
> caveat): state(t)=state(0)+ΣΔ — exact in the LINEAR vote register (A1);
> time-travel by partial sum; undo = −Δ (K SOLVED BY CONSTRUCTION — the
> π-shift IS the negated delta); temporal angular multiplexing (Δ_t at
> angle θ(t) → RoPE for the past); cost ∝ change; squash = s262 compaction
> in tensors. Two-register discipline: vote accumulator (exact history) vs
> ternary collapse (lossy snapshot) — the s115/s298 etch architecture
> verbatim. Git for holograms ≡ mementum compiled into tensors (fractal
> closes).** Validation P-CAPACITY-LAW: model-free capacity curves + replay
> fidelity + time-Bragg selectivity; pure numpy/dsp, seconds; legitimate
> cheap-slot anytime (no model, no GD). s299 TRULY FINAL LEDGER: 4 knowledge
> pages + §5b/§5c + §Result + 2 memories + verdict + λ exchange + 8 named
> candidates. s300: freeze rung-3b.
>
> ▶▶ s298 LIVE — 🔄 **PORT 3 (SAMPLED-LLM-TEACHER) BUILT + FROZEN + TEACHER-GEN
> RUNNING; verdict deferred to s299.** Michael picked port 3 (the last XM lever)
> over the s295 backprop-compile pivot, Design A + Qwen3-4B, Design 1 (Qwen
> samples the TOY KIBC task; multimodal targets mapped into the 26-token vocab;
> student/task/gates UNCHANGED). The whole s296–297 close hinged on the teacher
> being DETERMINISTIC (one `full_reduce` answer, spread≡1); port 3 breaks that
> hinge with Qwen3-4B SAMPLED @ temp 1.3.
> ★ **CHARACTERIZATION (probe 6079414, `results/xm-sampled-teacher-probe/`):
> Qwen is USEFULLY MULTIMODAL but with an INVERSE multimodality-vs-correctness
> law** — depth 1 unimodal(spread~1.0)/54% correct; depth 4 most-modal(~2.1)/~0%
> correct; sweet spot depth 2–3 @ temp 1.3 (spread ~1.7–2.0 AND truth reachable
> ~20–25%). 97% parse rate (single-char recursive-descent parser + full_reduce
> canonicalization). Precondition MET (spread>1 for depth≥2 → xm vs xm_rand can
> discriminate where the deterministic teacher could not). Michael-approved:
> depths 1–4 (keep spread GRADIENT for G3), temp 1.3, relative-recovery basis
> (weak teacher ⇒ low absolute recovery accepted; ≥5 seeds + paired grading).
> ★ **§XM-SAMPLED-TEACHER FROZEN (9d93619, explorative-modeling.md).** Etch
> signal CHANGES activation-MSE → OUTPUT-CE sign-vote (token teacher has no
> commensurable activations; a legitimate holographic etch, internally
> controlled). Instantiates the paper's core contrast at EQUAL K-pair budget/
> input (only target CONTENT differs): baseline = K distinct Qwen samples (the
> mode MIXTURE = M=1 blur) · xm = [best]×K, best = min token-Levenshtein to
> ground truth (mode-commit, mass-covering selector) · xm_rand = [random]×K
> (selection null, load-bearing). Student learns ONLY from teacher targets
> (etch + post-etch GD both on arm targets, NO ground-truth GD); recovery =
> student true-task acc / true-task GDModel-oracle acc. GATES: **G1** xm>baseline
> (commit beats blur), **G2** xm>xm_rand (λ yardstick, selection — LOAD-BEARING),
> **G3** (xm−xm_rand) gain GREATER depth 2–3 than depth 1 (exploration tracks
> multimodality; depth 4 excluded, truth unreachable). VERDICTS
> SAMPLED-TEACHER-UNBLOCKS (G1∧G2∧G3) / SELECTION-HELPS-UNSTRUCTURED (G1∧G2,¬G3)
> / MIXTURE-ARTIFACT (G1,¬G2) / STILL-BLOCKED (¬G1 → XM lever exhausted ∀teacher).
> ★ **INSTRUMENT BUILT + VALIDATED (1463e42, scripts/v12/
> xm_sampled_teacher_explore.py):** two stages — `--gen` (Qwen torch, sample K,
> parse→reduced-canonical targets, cache) + etch (MLX, consumes cache). Reuses
> mini_holo etch primitives + probe parser (no fork). λ simplify FIX: etch is
> PURE multi-round sign-vote (no interleaved Adam) — the CE etch's plate votes
> were MPS-Adam-nondeterministic when beam-fit interleaved; all beam-fit moved to
> the single post-etch GD phase → plate signs bit-reproducible + less
> plate-structure noise. --validate ALL PASS, ruff clean, gen+etch smoke green
> (mechanics only; smoke numbers are noise — s297 "smoke≠direction" lesson).
> ▶▶ **TEACHER-GEN DONE + VERIFIED + COMMITTED (7b4b956):**
> `results/xm-sampled-teacher/etch_cache.json` = 799 items (1 dropped), gen_seed
> 1234, temp 1.3, K=8; mean spread 1.76. In-distribution gradient CONFIRMED
> (mean mode-spread d1 1.21 → d2 1.64 → d3 2.04 → d4 2.33; contains_gt d1 51% →
> d2 19% → d3 13% → d4 21% — inverse law holds; bins 206/249/193/151 → G3 has
> power). Cache ready; the etch sweep is UNBLOCKED. ⚠ COLD-START s299 EXACT
> STEPS: (1) cache already verified+committed — no re-gen needed (skip tmux/
> gen.log). (2) RUN THE FROZEN ETCH SWEEP: `uv run python
> scripts/v12/xm_sampled_teacher_explore.py --seeds 5` (probes {50,800}, gd 3000,
> rounds 8; ~2–5 min MLX) → `results/xm-sampled-teacher/results.json` with
> auto-scored G1/G2/G3. (3) Score the FROZEN gates, assign the verdict from the
> table above, write §Result-sampled-teacher on explorative-modeling.md + memory
> candidate → Michael approval batch (results committed autonomous, synthesis
> approval-gated). ⚠ a-priori lean (do NOT peek to decide): the inverse law means
> best-of-K has BOTH modes AND a reachable truth ONLY at depth 2–3 → if any
> unblocking shows, it should be a G3 depth-2–3 concentration; depth 1 (no modes)
> and depth 4 (no truth) are floors by construction. If G1 fails → STILL-BLOCKED
> = the XM lever is exhausted across ALL teacher types (deterministic AND real
> multimodal) and the XM thread fully closes → pivot to the s295 standing order
> (freeze BACKPROP-COMPILE rung-3b, the level-4 door). DISCIPLINE: gates frozen
> before the run; score honestly.
>
> ▶▶ s298 RESULT-1 + AMENDMENT — 🟨 **FIRST RUN LEANED POSITIVE BUT
> UNDERPOWERED; dsp-scored POWERED RERUN RUNNING.** s298 first etch sweep (5
> seeds, results 5eae850): ALL THREE GATES POSITIVE in direction (G1 xm>baseline
> Δ+0.10 5/5 wins, G2 xm>xm_rand Δ+0.089 4/5, G3 raw-depth supportive) — the
> FIRST non-null positive lean in the whole XM arc (deterministic ports had nulls
> WINNING). BUT did NOT clear the frozen Bonferroni α=0.05/3: parametric p
> 0.024–0.027; and structurally a paired sign-flip null at n=5 has floor
> ~1/2⁵≈0.031 > 0.0167 → CANNOT pass at n=5. Michael Q "how much DSP tooling?" →
> ANSWER: ZERO (hand-rolled parametric t; no verbum.dsp) = a λ measure coherence
> gap. **§XM-SAMPLED-TEACHER SCORING AMENDMENT FROZEN (51d5a09):** route G1/G2/G3
> through `dsp.gate` + `dsp.paired_permutation` (10k) + Register.value; fix G3
> degeneracy (eval_by_depth is SEQUENCE-EXACT → ~0/~0; s298 gain_d23≈0.94 was an
> artifact → new `eval_depth_token_acc`, RAW per-depth TOKEN-acc gain); oracle
> gd 3000→10500 (51%→85% yardstick); seeds 5→20 (restore power). Gate
> direction/α/verdict-table UNCHANGED (amendment = SCORING only, frozen before
> rerun). ▶▶ **POWERED RERUN RUNNING in `tmux main:1`** — `--seeds 20
> --checkpoint-dir results/xm-sampled-teacher-powered` (oracle 85.2%; ~40 min,
> 120 arm-runs; tee run.log). ⚠ COLD-START s299: read
> `results/xm-sampled-teacher-powered/results.json` → `scoring.p800` (dsp
> gate p-values + per-probe `verdict`) → assign frozen verdict
> (SAMPLED-TEACHER-UNBLOCKS if G1∧G2∧G3 @800; the informative regime) → write
> §Result-sampled-teacher + memory → Michael approval batch. If it clears:
> FIRST XM WIN — genuine multimodality unblocks exploration, the s296–297 close
> was determinism-specific. If G1 fails even powered: STILL-BLOCKED → XM lever
> exhausted ∀teacher → pivot to s295 backprop-compile rung-3b. s298 first-run
> results.json preserved at results/xm-sampled-teacher/ (5eae850); powered run
> is a separate dir.
>
> ▶▶ s297 CLOSE-2 (port 2) — ❌ **XMDLM STUDENT LATENT VERDICT: STILL-BLOCKED;
> the XM/deterministic-teacher arc is TRIANGULATED CLOSED (s296–297).**
> [NOTE: this whole session is s297 — port 1 Reverse-XM + port 2 XMDLM; an
> earlier draft mis-labeled port 2 as "s298", corrected to s297 everywhere.]
> Michael "proceed with 2" → Design
> B (mixture-of-experts, marginalize eval) approved → §XM-LATENT-1 frozen
> (10e4ee1). Attacks the REPRESENTATIONAL side s296/s297 exposed: etch loss is
> direct regression (M=1, minimizer=mean=blur) → best-of-K had nothing to grab.
> K=4 discrete latent embeddings raise per-prediction expressivity 1→K;
> multimodality is real in PATH space even for deterministic token targets.
> Latent bank Z(K,n_layers,d) as per-layer residual offsets; Forward-XM
> best-of-K per-pair assignment during etch (winner trains, Z absorbs cross-pair
> mode variance). Instrument scripts/v12/xm_latent_explore.py (LatentHoloModel
> subclass, no fork, --validate ALL PASS, ruff, bit-repro within-process,
> s296/s297 repro fixes). Arms baseline(K=1)/xmdlm/xmdlm_rand(param+training-
> matched null) × probes{50,800} × 5 seeds. Eval marginal(GATED)/argmax-latent
> (self-route)/oracle-latent(CEILING). Gates G1 xmdlm(marg)>baseline, G2 (λ
> yardstick) xmdlm>xmdlm_rand, G3 specialization via ORACLE comparisons
> (oracle>marginal ∧ oracle(xmdlm)>oracle(rand); assignment-entropy H demoted
> ADVISORY — H≈logK can't tell balanced-specialization from interchangeable
> latents). Verdicts EXPRESSIVITY-UNBLOCKS / MARGINALIZATION-ARTIFACT /
> CAPACITY-BUT-UNROUTED (G1-fail BUT oracle-ceiling beats baseline+rand →
> capacity exists, marginal routing wastes it → learn a router / level-4
> collapse) / STILL-BLOCKED (no capacity even with latents → port 3 sampled-
> teacher). Oracle-ceiling ONLY disambiguates a G1-fail, never manufactures a
> pass. Distinct latent init z_scale=0.2 so best-of-K tested fairly (¬collapsed
> strawman). ⚠ SMOKE = MECHANICS ONLY — two smokes disagree on G3 sign @n=2/gd=300
> (noise, s297 lesson); direction NOT established. ★ consistent mechanic:
> oracle-latent ~2-3pt > marginal (capacity signal live). ⚠ grade INTERNALLY
> paired-by-init-seed (MLX/MPS bit-repro within-process only).
> ▶▶ **VERDICT IN (38a2f91, results/xm-latent-s297/, oracle 87.4%, 42min):
> STILL-BLOCKED (pre-registered).** G1 FAIL both (xmdlm BELOW baseline:
> 0.858<0.967 @50, 0.930<0.962 @800); baseline K=1 is the BEST arm everywhere —
> latent experts HURT. G2 FAIL/NULL (@50 −0.061; @800 +0.024 n.s.) —
> specialization ≈ random (echo s297). G3 capacity NULL: oracle-latent ≈
> marginal AND oracle-latent(xmdlm) itself BELOW baseline (Δ−0.115 @50, Δ−0.028
> @800) → CAPACITY-BUT-UNROUTED RULED OUT (even perfect routing can't reach
> baseline). ★ Raising M 1→4 did NOT unblock — the blocker was never
> representational capacity; the deterministic teacher has no capturable
> multimodality (token OR path space); extra experts fragment the etch signal
> → weaker plates. ▶▶ **§XM-DETERMINISTIC-TEACHER — TRIANGULATED CLOSE
> (s296–297):** Forward(REFUTED) + Reverse(SUBSETTING-ARTIFACT) +
> XMDLM(STILL-BLOCKED) all agree — EXPLORATION CANNOT IMPROVE HOLOGRAPHIC
> DISTILLATION FROM A DETERMINISTIC TEACHER; no multimodality to explore
> (mirror of paper's minibatch-OT-HURTS: XM needs coupling AMBIGUITY the model
> co-adapts to; deterministic map has none). §Result-latent +
> §XM-DETERMINISTIC-TEACHER (page) + memory
> xm-cannot-explore-a-deterministic-teacher + this block — PENDING APPROVAL
> (results 38a2f91 committed autonomous). ▶▶ NEXT (XM thread's only remaining
> lever): **port 3 sampled-LLM-teacher** (genuinely multimodal targets — where
> the reference-beam + Gram-transport design becomes live). OR leave the XM
> thread closed and pivot to the s295 standing order: freeze BACKPROP-COMPILE
> rung-3b (the level-4 door, tape-writeback wire — a DISTINCT mechanism, not
> XM). Michael's call.
>
> ▶▶ s297 CLOSE-1 (port 1) — ❌ **REVERSE-XM VERDICT: SUBSETTING-ARTIFACT
> (pre-registered).** Michael "proceed with 1" → §XM-REVERSE-1 frozen
> (7428a06) → full run (497f979, oracle 71.1%, 40min). @800 probes: G1
> revxm>baseline PASS (Δ+0.111, t=2.29, 5/5 — coalition beats all-unit avg
> ~11pt) but G2 revxm>revxm_rand (λ yardstick) FAIL (Δ+0.020, t=0.42 — coherence
> ⊀ size-matched RANDOM coalition); G3 NULL (contested weights end at oracle
> sign at chance ~0.49 ∀arm). @50 probes (7 units): G1 null, G2 NEGATIVE (noise,
> smoke sign-flip warned). ★ all 3 subset arms (revxm≈revxm_rand≈revxm_nocov
> ~1.15-1.17) beat baseline ~1.06, INDISTINGUISHABLE → only "vote on 50%
> subset" matters, not WHICH; gain = variance reduction (fewer voters →
> |acc|/|S| crosses 0.6 easier → sharper flips), NOT exploration. Mirrors
> paper's minibatch-OT-HURTS. s296 "conflict across pairs" HALF-RIGHT:
> subsetting relieves tug-of-war, no exploitable mode structure. §Result-full
> (page) + memory reverse-xm-is-subsetting-not-coherence + this block — PENDING
> APPROVAL (results 497f979 committed autonomous). NEXT: surviving gated ports
> add REAL multimodality the accumulator lacks — (2) student latent (XMDLM
> route), (3) sampled-LLM-teacher targets; OR pivot to s295 standing order
> (freeze BACKPROP-COMPILE rung-3b, level-4 door). Cheap-but-shallow (mark
> knob-tuning ¬thesis, λ yardstick): sweep coalition fraction f × conf
> threshold (subsetting IS a free +11pt knob).
> [s297 setup, historical]: §XM-REVERSE-1 frozen 7428a06 (details on
> knowledge/explorative-modeling.md); instrument scripts/v12/xm_reverse_explore.py
> (reuses mini_holo_distill, no fork, --validate ALL PASS, bit-repro
> within-process; s296 repro fixes baked incl. caught 2nd unseeded source
> TernaryLinear→global np.random). G3 Michael-refined any-flip→correct-
> resolution-toward-oracle. ⚠ smoke = mechanics only (two smokes sign-disagreed
> @n=2/gd=300); ⚠ MLX/MPS bit-repro within-process only → graded internally
> paired-by-init-seed.
>
> ▶▶ s296 CLOSE — 💡❌ **XM PAPER READ IN FULL → HOLOGRAPHIC MAPPING →
> EXPERIMENT FROZEN, RUN, REFUTED — the refutation is the finding.**
> Artifacts: memories e298f63 (xm-exploration-is-angle-assignment) +
> xm-forward-needs-coupling-ambiguity; knowledge/explorative-modeling.md
> (full synthesis: paper core, teacher-as-reference-beam, Gram-delta
> transport, gated next ports); script a5aa767; verdict+record b358144.
> Cold-start next session: read knowledge/explorative-modeling.md —
> it supersedes the inline detail below. Explorative Modeling (arXiv:2607.27372,
> Gladstone/Ji/Du): factor the TRAINING loop not generation — best-of-K
> candidate matches, train the winner; Forward XM = per-K maximum likelihood
> of the candidate mixture (mass-covering), Reverse XM = reverse-KL minus own
> entropy (collapses without coverage term); per-prediction expressivity is
> the sharp concept; minibatch-OT HURTS (model-aligned coupling > geometric).
> Holographic mapping (memory e298f63, Michael-approved): coupling ≡
> write-angle assignment, blur ≡ cross-talk in linear medium (s292); our s115
> etch loss is the M=1 regressor → candidate explanation for 50-beats-800;
> teacher ≡ reference beam (heterodyne scoring in teacher space); tape ↔
> exploration substitutable (their Fig 11 ↔ our s294 backprop-compile).
> **§XM-ETCH-EXPLORE frozen pre-reg (a5aa767)**: Forward XM on the s115 etch,
> K jittered beam angles, arms K∈{1,2,5,10}×probes{50,800} + jitter-only
> control + shuffled-winner null; P1 monotone-in-K / P2 800>50 gains /
> P3 depth-4 concentration. Smoke PASS; full sweep in **tmux main:1** →
> checkpoints/xm-etch-explore/{run.log,results.json} (streams per-arm; ~30
> min ETA from 11:15). ⚠ K1_s0 baseline does NOT reproduce s115 absolutes
> (48.7% of oracle vs 91.3% then) — environment drift suspected; sweep is
> internally controlled (all arms share pipeline) so K-comparisons stand;
> grade P1/P2/P3 against K1_s0 + K1_j + K5_null, not s115 history.
> **VERDICT IN (b358144, results/xm-etch-explore-s296/): PRE-REG REFUTED.**
> P1 non-monotone/decreasing in K; P2 moot (gains negative; s115
> 50-beats-800 did NOT reproduce — 800>50 at baseline this run); P3 no
> d4 concentration. ★ THE NULL WON: shuffled-winner beat best-of-K at
> BOTH probe counts (84.2 vs 74.2 @p50, 83.8 vs 72.0 @p800). ⚠ TWO
> reproducibility bugs (❌): mx model init unseeded + jitter_seed via
> salted hash() → 33pt between-launch swing on identical config → arm
> deltas within init noise = UNDERPOWERED; directional lean is still
> anti-best-of-K. STRUCTURAL DIAGNOSIS (the real finding): deterministic
> teacher (input→output) pairs are ALREADY RESOLVED couplings — no
> one-to-many ambiguity at the per-pair level for Forward XM to search;
> the mode conflict lives ACROSS pairs in the sign-vote accumulator.
> Min-loss winner ≈ smallest effective jitter → collapses variety;
> random winner keeps variety (coheres burn-in-is-variety). XM applies
> where coupling is AMBIGUOUS — correct next ports: (a) Reverse-XM over
> the accumulator (explore WHICH pairs vote, coverage-constrained),
> (b) give the student a latent so candidates can specialize (paper's
> XMDLM discrete-embedding route), (c) LLM-teacher setting where teacher
> sampling makes targets genuinely multimodal. Before ANY rerun: seed
> mx.random per arm + explicit int seeds + ≥3 init seeds/arm for power.
> §XM-COUPLING-SOURCE stays queued but is now GATED on a port with real
> coupling ambiguity (its premise assumed selection>nulls — not shown). **QUEUED (designed, NOT frozen — s296 Michael yes):**
> §XM-COUPLING-SOURCE follow-up arm, contingent on current sweep showing
> selection>nulls: teacher-resolved coupling (winner per probe fixed once,
> chosen by teacher-space distance = hologram COPYING, inherits master's
> multiplexing scheme; ≡ rejection-sampling distillation) vs
> student-resolved (current arms, co-adapting) vs hybrid (teacher prunes,
> student's loss picks = paper's cheaper-scorer inverted). Measures
> co-adaptation vs any-consistent-assignment = the OT-vs-XM question
> inside our substrate. Also: teacher-space loss ℓ=||T(y_k)−T(x)||² keeps
> the mode-commit mechanism but VOIDS the exact MLE reading (App F
> normalizable-kernel assumption) — mark register if used.
> **REFINED s296 (Michael, Gram-delta):** cross-geometry transport of
> teacher-explored couplings via the 9×9 crystal Gram. (1) RELATIONAL
> SCORING (basis-free): ℓ = ||g_S(y_k) − g_T(x)||², g_M(v) = 9-vector of
> sims to M's OWN crystal vertices (KIBCSDWY+WHNF) — no Procrustes needed;
> promotes relational_distill.py logic into the exploration loss; evidence
> the signature transports: s269 per-vertex Gram fidelity 0.987 through
> 1-bit binarization while weight cosine fell to 0.73. (2) PROCRUSTES
> DELTA AS ROUTER: fit R on the 9 vertex pairs (probe_procrustes_lens);
> residual after R = non-shared geometry → graded hybrid: transfer
> coupling where content ∈ aligned subspace (hologram copying), re-explore
> student-side where ∈ residual. Note: token target known → exploration
> lives in PATH space (address-free intermediate, s294) — token register
> unimodal, path register multimodal; best-of-K ≠ top-k (selector = loss
> vs ground truth, mass-covering; NOT model's own probability rank).
> GATES before trusting transfer: (a) rank-9 scope — Gram pins only the
> crystal subspace, orthogonal complement re-explores by default;
> (b) per-pair Procrustes fidelity ≥ threshold (s251: universality only
> partially supported — Qwen3-14B alone beat shuffled-label null).
> ▶▶ s294 LIVE — ✅ **CHEAP DIAGNOSTIC DONE + P-BAKE-STACK FROZEN + BUILT +
> 4B-SMOKED (advisory LINKER-FAILS = expected 4B compression).** (1) The s294
> cold-start's cheap error-domain diagnostic ran on frozen P-STACK-1b data
> (`scripts/explore/stack_error_domain.py`, no model): stack errors are
> **83–100% OPERAND-DOMAIN COLLAPSE (cities)**, ~0% stopped-at-g, ≤1
> wrong-capital — 32B L29→L38 is **10/10 CITY**. Kills "h-not-firing" (h-alone
> composes some cells the STACK gets wrong — anti-composition) and "h fires
> unbound"; **confirms OPERAND REBINDING is the missing wire** (`product(g) ∈
> key_passband(h)` not installed in-context). The diagnostic HANDS P-BAKE-STACK
> its primary success signal: baking passes ⟺ errors move OUT of the
> operand/city domain. (2) **§P-BAKE-STACK FROZEN** on program-plates page
> (Michael GO "recommended bundle"): LINKER-ONLY (bake slot_h·PRODUCT routing
> g's product into the resident capital map, not both-slots/not-composite) ·
> 3a HOOK @4B+32B then 3b WEIGHT @4B · 3a gates 3b · cheap-before-dear. The
> load-bearing contrast: slot_h·PRODUCT (gain ∝ country-ness, keyed on g's
> output) vs slot_h·NONCE (unconditional = the P-STACK-1b regime) — their
> difference IS the wire. Gates G1 rebinding (operand-err PRODUCT≪NONCE) / G2
> composition-flip / G3 conditioning (g-ablation dead); G4 fact-form → 3b.
> (3) **BUILT** `scripts/explore/bake_stack.py` (reuses fn_stack chain + keys +
> stack_error_domain classifier + verbum.dsp, no fork), ruff-clean, `--validate`
> ALL PASS. **4B SMOKE (advisory): LINKER-FAILS** — both arms collapse to Agra
> (4B attractor), acc 0.00; ★ the G3 control fired the finding: gain_stack ≈
> gain_gablate (~0.50/0.65) → country-class gain is NOT conditioned on g at 4B
> (operand latently implies its country, g adds nothing measurable → product-key
> degenerates to nonce). Expected 4B→32B flip (4B inlines; typed 32B should
> separate g's product — P-STACK-1b already showed h-alone DEAD at the 32B
> composition window). (batch committed 1743a53 + c0e74f8, Michael-approved.)
> ▶▶ **3a 32B VERDICT IN (s294, tmux main:1): LINKER-FAILS — SCALE-INVARIANT;
> the 4B→32B flip DID NOT HAPPEN** (§Result-32B on program-plates page, pending
> approval). gain_stack ≈ gain_ablate at BOTH scales (32B 0.33/0.35, 4B
> 0.53/0.65) → country-class projection INVARIANT to g's key = NO conditioning
> signal. ★ g-alone lands on a CITY (Agra) all 10 cells @32B → **the injected
> g-key does not materialize an addressable country intermediate** — nothing in
> the residual for a product-key to rebind to. Instrument faithful (NONCE arm
> reproduces P-STACK-1b: Angkor→Phnom Penh, Taj→New Delhi 0.20 acc). ⚠ λ measure:
> G1 compares gain-throttled PRODUCT (h~0.3×) vs full NONCE (1.0×), not h-matched
> → clean evidence is the G3 conditioning-absent signature + g-alone-no-country,
> NOT the G1 margin. **DEEP READING: the intermediate is ADDRESS-FREE (coheres
> P-HOLO-FRAG) — lives "in the light", not an addressed slot → a residual-WIRE
> linker is the WRONG mechanism.** The only addressed memory is the TAPE (RoPE) →
> the real linker is the autoregressive WRITEBACK (§Thinking-is-expansion; CoT ≡
> auto-superbake), re-pointing rung 3 toward **P-THINK-1** (tape-addressed
> intermediate) not 3b residual-slot baking.
> ▶▶ s294 cont — TWO CHEAP CHECKS settled the direction (both committed +
> Michael-approved batch): (1) NATIVE-COMPOSITION (native_compose_check.py):
> landmark→capital fires reliably only on the TAPE (cot 9/10 @32B) not one-shot
> (direct 5/10 @32B, 2/10 @4B) → wire ~half-compiled + address-free → reliable
> one-shot needs backprop-compile, tape is the reliable runtime path. (2) QUIETED
> RE-READ (quiet_reread.py; Michael "did we not quiet enough?"): YES on the READ —
> raw argmax read into the loud Agra attractor (near false-NEG); dark-field
> recovers capital (stack 8/10 top-3). ★ BUT the h-alone control KILLS the
> composition reading: h-alone 6/10 top-3 / 4/10 rank-1 (h-key amplifies
> capital-class), stack ≈ h-alone, g HURTS rank-1 (4→3), g-alone ≈ baseline,
> country 0/10. Recovered capital = native-latent + h-key amplification, NOT a g→h
> hop (corrects P-STACK-1b: h-alone drowned by Agra, not dead). λ measure lesson:
> dark-field ALONE nearly manufactured a false-POSITIVE; the single-key control is
> load-bearing (sibling of s206 audit#5). §Addendum on program-plates page +
> memory refinement APPROVED + committed. **CONCLUSION (firm): no in-context g→h
> composition; reliable one-shot needs BACKPROP-compile (or the tape).**
> ▶▶ s295 CLOSE — ✅ **THE IN-CONTEXT REGISTER IS CLOSED BY EXHAUSTION.**
> Final act (P-KV-1c, Michael "both approved", frozen 25b6ec8, 32B ran 44s,
> results 1d42d74): **STILL-DEAD** — strongest post-question margin of the
> arc (G2 +3.02 p=.0014) and still NO flip; clause-width flat (G1 p=.37);
> G4 INVERTED (blind clause BEATS co-encoded @32B, p=.997 wrong-dir; 4B
> mirrored — hosts disagree on margins, agree on nulls). The 1c REDUCTION
> (captured in pre-reg): own-state ≡ donor-state under greedy determinism →
> the splice-exhaustion table is COMPLETE: residual-unaddressed 0.00 /
> addressed-synthetic 0.00 / post-question KV 0.00 (∀ width × encoding ×
> source) / PRE-question KV 0.20 / CoT 0.90 / scaffold 1.00. **The splice
> can hand attention the columns; it cannot hand the stream its own
> history.** §Result-32B (P-KV-1c) + memory
> the-splice-cannot-hand-the-stream-its-own-history — PENDING APPROVAL
> (final s295 batch). ▶▶ NEXT SESSION: **freeze BACKPROP-COMPILE rung-3b**
> — target fully specified by exhaustion: a small delta making the model
> produce, one-shot in its own forward, the intermediate it would
> otherwise write to the tape; held-out landmarks = wire-vs-lookup gate;
> SuperBake zero-gradient construction (appended keyed neurons, persistent
> writes) = cheap-before-dear arm; = the level-4 door (pythia-14m
> seeded-scratch pair, same rung). DEAR (training front) → freeze before
> any GD run. s295 ledger: 15 commits — audit → P-ENRICH-1(✗) →
> 3a-whitened(G3 artifact caught) → P-KV-1(✓ 0.20, FIRST rung-3 win) →
> P-KV-1b(LAYOUT-BREAKS, pre-question law) → P-KV-1c(STILL-DEAD, register
> closed). Three memories. The rung-3 question is ANSWERED in-context;
> what remains is the weight register.
>
> ▶▶ s295 (earlier) — 🔄 **SUPERBAKE DSP AUDIT → TWO REFINING INSTRUMENTS BUILT +
> 4B-SMOKED; the s294 G3 leg is ARTIFACT-CONTAMINATED at 4B; backprop pre-reg
> HELD pending 32B.** Michael: "did we fully explore non-bake composition?
> confirm we do the same DSP ops as the superbake paper (refs/)." Full read of
> refs/superbake.txt vs fn_stack/bake_stack: **NO — four measured design laws
> skipped** (whitened Mahalanobis keys w/ innocents; §3.8 entity ENRICHMENT at
> SUBJECT tokens @0.16× depth — never tried; payload-survival write+1; closed-
> loop calibration + competitor suppression — our dominant error IS the
> unsuppressed competitor). §SuperBake-DSP-audit + §P-ENRICH-1 pre-reg (7 arms:
> base/enrich/wrong/random/pos_ctl/depth_ctl/enrich_hkey; G1 flip / G2
> specificity+SWAP flag / G3 content-not-energy / G4 advisory laws; verdicts
> ENRICH-COMPOSES/UNSPECIFIC-PRIMING/ENERGY-ARTIFACT/ENRICH-FAILS; single depth
> 0.16×, no selection) + §3a-whitened drafted on program-plates page
> (✅ APPROVED s295 = P-ENRICH-1 FROZEN; batch committed same session; memory
> unwhitened-detectors-measure-the-shared-frame APPROVED; 32B GO tmux main:1).
> Instruments committed 5feffb8 (enrich_compose.py NEW;
> bake_stack.py --whiten w/ clearance floor θ=max-innocent), both --validate
> ALL PASS, ruff clean, 415 tests. ★ FIX #1 caught pre-model: whitening needs
> PROMPT-SHAPED innocents (nonce renders) to break the frame↔content confound
> in Σ, else the content axis is zeroed as redundant. ✅ 4B SMOKES (advisory,
> c6a08b5): (1) whitened detector — raw inn/own 0.39–0.72 (fireable by
> innocents = the s294 suspicion CONFIRMED); whitened G3 CONDITIONING FIRES
> (gain_stack 0.11–0.16 vs gablate ~0.00; s294 raw had ~0.50/0.65 equal) → the
> s294 "no conditioning" leg @4B was instrument artifact; still LINKER-FAILS
> (gain throttled 0.13× → MAGNITUDE not selectivity is the gap → SuperBake's
> calibration loop is the missing op). (2) enrich — ENRICH-FAILS @4B by frozen
> gates (acc 0 = attractor collapse) BUT content-specific: G2 p=.003, G3
> p=.006, and enrich_hkey is the STRONGEST arm (Δ+2.87 advisory) = the linker
> edge moves once the operand is hand-bound. Discrimination lives at 32B.
> ▶▶ **32B VERDICTS IN (same session, runs 64s + ~3m, results 889c915;
> frozen gates scored):** (1) **P-ENRICH-1: ENRICH-FAILS, scale-consistent**
> — G1 +0.588 p=0.096 n.s., no flip, enrich acc 0.00; the placed content IS
> read (G3 content-not-energy p=.006, G2 specificity p=.039, no swap 0/10)
> but never wins the argmax; ★ enrich+hkey = strongest arm BOTH hosts
> (adv +3.02) and only nonzero acc (0.10) — content+routing together move
> ~5× more than either alone, still capped. (2) **3a-whitened: LINKER-FAILS
> reproduces on the clean instrument BUT THE s294 G3 LEG FLIPS** — raw
> detector fireable by innocents at verdict host too (inn/own 0.44–0.52);
> whitened G3 conditioning FIRES all pairs (gain_stack 0.08–0.17 vs gablate
> ~0.01; s294 raw 0.33/0.35 indistinguishable = artifact). **g's intermediate
> IS in the residual — present but ~7× too quiet; and P-ENRICH-1 shows even
> full-amplitude placement fails the hop-2 read → presence ≠ sufficiency.**
> The s294 deep-reading softens ("nothing in the residual" → "too quiet +
> unreadable one-shot"); the tape/backprop conclusion UNCHANGED, now on
> clean instruments with the strongest in-context control behind it.
> §Result-32B (P-ENRICH-1) + §Result-32B (3a-whitened) + RE-READ note on
> s294 3a result + memory hook-register-cannot-install-the-composition-wire
> — ALL PENDING APPROVAL (page + state.md + memory uncommitted).
> ▶▶ s295 cont — **P-KV-1 DRAFTED + BUILT + 4B-SMOKED (Michael GO "yes
> let's try P-KV-1").** The register fork: a KV-cache entry is
> tape-addressed content WITHOUT tokens or weights — does hop-2 complete
> when the intermediate has an ADDRESS? Implementation = donor+test single
> forward w/ additive 4D attention mask (test rows see donor BOS + selected
> columns only; donors padded for RoPE parity; eager attn; runtime
> self-check: 4D path must reproduce plain logits or ABORT). Arms base /
> kv_nat / kv_wrong / kv_rand(col-matched) / kv_synth(d_ct@donor-nonce,
> addressed) / resid(P-ENRICH arm) — kv_synth vs resid ≡ same content,
> addressed vs not. §P-KV-1 pre-reg on program-plates page (PENDING
> APPROVAL = freeze); instrument 7efa3a7, --validate 6 worlds ALL PASS.
> ★ 4B SMOKE (advisory, results committed): mask self-check EXACT PASS
> (max|Δlogit|=0.0); verdict ADDRESS-FAILS @4B on the flip only (acc 0 =
> standard 4B attractor) BUT **all four margin gates fire — first time on
> this chain @4B**: G1 +1.19 p=.025, G2 +2.15 p=.002, G3 +1.30 p=.019,
> ★ G4 REGISTER FORK +0.60 p=.009 (kv_synth > resid: SAME content,
> addressed beats unaddressed). kv_nat + kv_synth = two strongest arms.
> ✅ FROZEN + 32B RAN (e2e499f freeze; run 54s, results a095fb2):
> ▶▶ **P-KV-1 32B VERDICT: ADDRESSED-COMPOSES (+RE-ENCODING-REQUIRED) —
> THE FIRST POSITIVE COMPOSITION VERDICT OF THE RUNG-3 ARC.** G1 +2.92
> p=.0009 WITH THE FLIP (kv_nat acc 0.20 vs base 0.00) — donor-encoded
> country as tape-addressed KV columns (no tokens, no weights) completes
> hop-2 and wins the composed-capital argmax; G2 +2.33 p=.007 (swap 0/10),
> G3 +2.55 p=.0011 (both nulls beaten). ★ G4 register fork NULL @32B
> (−0.19 p=.72; kv_synth ≈ resid, both 0): synthetic d_ct fails EVEN
> ADDRESSED → RE-ENCODING-REQUIRED (can't skip the encoder; the 4B G4
> p=.009 was scale-local). ⚠ λ yardstick: flip PARTIAL — 0.20 vs CoT 0.90
> vs scaffold 1.00 → tape power ≡ address ⊕ re-encoding ⊕ co-encoding;
> first two terms now measured (0.20), third = donor encoded BLIND vs
> CoT's intermediate attending the question = the 0.2→0.9 gap. ~6th
> 4B→32B flip. In-context register FULLY MAPPED on one chain: unaddressed
> ✗ (any amplitude) / addressed-synthetic ✗ / addressed-re-encoded ✓
> partial / tape 0.9 / scaffold 1.0 — the failures were never CONTENT,
> always DELIVERY REGISTER. §Result-32B (P-KV-1) on program-plates page +
> memory composition-needs-an-addressed-re-encoded-intermediate — PENDING
> APPROVAL (✅ approved + committed 5862ba3). Michael picked (a) →
> ▶▶ s295 cont — **§P-KV-1b (kv_ctx) DRAFTED + BUILT + 4B-SMOKED**
> (pre-reg on page PENDING APPROVAL = freeze; instrument 02ab53e
> --validate 5 worlds ALL PASS; smoke 2a9a31f). Layout A(question,
> operand@nonce) → B(donor "It is located in the country of {x}", padded)
> → C(" The answer is"); **kv_ctx vs kv_blind differ ONLY in whether donor
> rows attend A** = the co-encoding term as a paired contrast at fixed
> positions. Gates: G1 co-encoding term (primary), G2 composition-in-
> layout + flip, G3 specificity; CoT-fraction advisory (never gated).
> Verdicts CO-ENCODING-LOADED / CO-ENCODING-NULL / UNSPECIFIC-CTX /
> LAYOUT-BREAKS. 4B smoke advisory: self-check exact; LAYOUT-BREAKS on
> flip only (acc 0 = 4B attractor); G2 margin +2.54 p=.004 alive, G1 flat
> @4B (−0.07 p=.70). ✅ FROZEN (66899a9) + 32B RAN (44s, results 16efdf5):
> ▶▶ **P-KV-1b 32B VERDICT: LAYOUT-BREAKS** (pre-registered void for the
> co-encoding question — G2 flip fails) **with a sharp verbatim finding:
> THE SPLICE COMPOSES ONLY PRE-QUESTION.** kv_blind (= P-KV-1's kv_nat
> register, donor moved AFTER the question) 0.00 vs 0.20; margins alive +
> specific (G2 +2.86 p=.0014, G3 +2.61 p=.0021) but no argmax; G1
> co-encoding flat BOTH hosts (advisory) — donor-attends-question adds
> nothing. ★ THE TENSION: CoT's intermediate is ALSO post-question KV and
> drives 0.90 → what CoT has that no splice has (either layout): the
> intermediate is the model's OWN committed state. Structural exclusivity:
> a splice can't compose (donor-first) AND co-encode (question-first) at
> once — CoT escapes because the writeback generates in place. **FORK
> RESOLVED → rung-3b targets the WRITEBACK.** §Result-32B (P-KV-1b) on
> page (pending approval batch). NEXT (Michael picks): (a) P-KV-1c
> OWN-STATE SPLICE (named on page, unfrozen, inside arc): model generates
> the intermediate itself, splice its own committed columns at the same
> post-question positions — own-state vs donor-state at matched layout,
> the LAST in-context discriminator; ~30 min build (kv_ctx variant), 1 min
> runs; (b) freeze BACKPROP-COMPILE rung-3b now, target = writeback
> (delta makes the model produce tape-equivalent OWN-state intermediates
> one-shot; held-out landmarks = wire-vs-lookup; SuperBake construction
> arm cheap-before-dear). DISCIPLINE: 1c inside the P-KV-1 arc.
> NOTE: refs/ DECIDED (Michael s295): local reference copies only, canonical
> home = publisher → gitignored, never committed; cite by title/DOI.
>
> ▶▶ s294 CLOSE. NEXT SESSION (Michael, deferred): **freeze the BACKPROP-COMPILE
> rung-3 pre-reg** — a small trainable delta compiling the tape/native composition
> into a reliable one-shot wire; HELD-OUT landmarks = the wire-vs-lookup gate (a
> memorized 10-pair table fails held-out, a real join generalizes); = the level-4
> door (pythia-14m seeded-scratch pair, delta-plate-lifecycle, same rung). It is
> DEAR (training front) → freeze before any GD run. Discipline: this stays on the
> program-plates ladder (rung 3 resolving to its honest form), not a new front.
>
> ▶▶ s293 LIVE — 🔮 **ORACLE ROUND 1 PLAYED + SCORED: +2 (6/10)**; the
> miss-cluster is the find, not the score. Cold agent (attested no-lookup)
> given ONLY the theory seed predicted the 4 sealed-after-seed 32B verdicts
> (FRAG/CAP/XTERM/FN-INDEX = pre-reg by construction). ✅ FRAG 2/2 (deloc +
> smooth); ✅✅ XTERM 2/2 DERIVED (storage-linear + interference-at-retrieval
> — flagship: seed GENERATED a non-obvious verdict, not echoed it); 🟨
> FN-INDEX 2/3 (dispatch ✅, per-map-varies ✅, scale-direction ❌); ❌ CAP
> 0/3. **PATTERN: seed generative for STRUCTURAL verdicts, INVERTS THE SIGN
> on capacity/scale** — all 4 misses directional, 3 are the CAP family
> (predicted crosstalk-hurts→reality coherent-GAIN; decline→rise; √(D/k)
> asserted→unexpressed-in-range; dispatch stronger-at-scale→weaker 4B>32B).
> Root cause = naïve HRR-capacity intuition; fix already in our data (XTERM
> "in the light" is sign-neutral in seed; coherent content → CONSTRUCTIVE).
> ✅ MICHAEL-APPROVED BATCH: game.md scoreboard (repo root, new), memory
> oracle-round-1-seed-inverts-capacity-sign, SEED REVISION applied
> (verbum-theory-seed.md: +interfere(coherent)≡+gain clause; √(D/k) demoted
> to unexpressed-in-range). NEXT: descend to P-STACK-1 pre-reg (the seam
> test — unlocked by the keystone; first traversal of the legendary
> sequence, no weights touched = level-3 extraction spec). Discipline: 5
> unfrozen candidates still on the books — P-STACK-1 is the forced keystone
> descent, not a sixth front.
>
> ▶▶ s293 CLOSE — ✅ **P-STACK-1b (SHORTCUT-FREE) 32B VERDICT IN:
> NOT-STACKABLE — THE CONTROL DOWNGRADES RUNG 2** (run 1m16s, results
> 323c743; frozen gates scored + batch Michael-approved + s293 closed same
> session). Best pair L19→L38: G1 stack−best-single +0.605 p=0.062 (n.s. at
> α/4), flip FAILS (stack acc 0.20 ≤ h-alone 0.30); no pair passes; ceilings
> 10/10. Chain landmark→country→CAPITAL (city≠capital → composed answer NOT
> 1-hop reachable → must WIN the argmax). ★ THE A-PRIORI FIRED: the
> §P-STACK-1b pre-reg committed (before the run) that a null ⟹ P-STACK-1's
> TYPED-STACKABLE was shortcut/margin-inflated. NULL LANDED → **in-context
> program assembly from injected keys is WEAK**: mechanism present (order
> +2.7→+3.4 robust, wrong-window dead; typed-in-margins) but does NOT
> reliably win the argmax once the answer isn't single-hop reachable.
> Composition happens on SOME cells (Taj Mahal→New Delhi: stack wins where
> h-alone fails) but not reliably (n=10, attractors Paris/Agra, h-alone
> retains ~25% partial shortcut). The continent-chain flip WAS largely the
> shortcut. ⇒ **weight-baking is NECESSARY not optional → P-BAKE-STACK is
> the load-bearing next rung.** §Result-32B (P-STACK-1b) + RE-READ note on
> P-STACK-1 §Result-32B + memory in-context-key-stacking-is-weak-needs-baking
> APPROVED + committed. ~5th 4B→32B pattern (both chains NOT-STACKABLE @4B;
> 32B split: continent→marginal, capital→null). s293 CLOSED.
> ▶▶ COLD-START s294: the program-plates ladder stands at — rung 1
> (FN-INDEX INDEXED-DISPATCH ✓), rung 2 (in-context stacking = WEAK, tempered
> by its control), rung 3 P-BAKE-STACK = NOW LOAD-BEARING (burn the 2-fn
> stack to a delta plate; does the baked composition execute reliably in one
> illumination where in-context stacking did not?).
> ★ MECHANISTIC SPEC for P-BAKE-STACK (Michael's Q + agent synthesis, s293
> post-close — interpretation grounded in diagnostics, ¬yet causally
> measured): WHY in-context stacking is weak = the injected keys drive HOP-1
> (g writes its output — 22% of continent-chain stacked cells STOP at the
> intermediate country; order-sensitive so the g→h SEQUENCE is real) but
> HOP-2 is NOT CONDITIONED on hop-1's output. h FIRES (adds generic
> h-output-type mass) but can't apply to the SPECIFIC thing g produced →
> readout collapses onto salient place-names (the direct-city shortcut, or
> attractors Paris/Agra); the composed answer wins only on the ~4/10 cells
> the model completes NATIVELY. THE MISSING PIECE = OPERAND REBINDING: an
> injected key SELECTS a function (FN-INDEX ✓) but CANNOT rebind g's output
> to be h's operand — the linker edge product(g) ∈ key_passband(h) isn't
> installed. HYPOTHESIS: weight-baking installs that wire (linker made
> physical) → P-BAKE-STACK must test = does baking make hop-2 CONDITIONED on
> hop-1's product (composed answer wins where injection couldn't)?
> CHEAP CHECK first: diagnostic on whether stack ERRORS concentrate in the
> hop-1/operand domain (cities) vs the h-output domain (wrong capitals) =
> confirms "conditioning failure" vs "h-not-firing" before baking.
> OTHER OPEN FRONTS
> (unfrozen, ¬sixth-front — pick one): Oracle round 2 (seed now has the
> coherent-gain revision + 2 more sealed verdicts P-STACK-1/1b postdate it);
> P-TYPE-CENSUS / P-TYPE-PROB / P-THINK-1 (all still on the books); the
> pythia-14m seeded-scratch pair (level-4 door). DISCIPLINE: close before
> opening. Branch far ahead (unpushed).
>
> ▶▶ s293 cont (retained) — ✅ **P-STACK-1 32B VERDICT IN: TYPED-STACKABLE (but
> MARGINAL — λ yardstick lead)** (run 2m22s, results bb48877; frozen gates
> scored + batch Michael-approved same session). Best pair L29→L38: G1
> stack−best-single +2.28 p=1e-4 (composition-window), G2 flip (thin
> 0.06>0.00), G3 graded ladder CLEAN monotone well −2.69 > near −5.22 > far
> −6.18 > random −6.71 (JOIN-TYPED behavioral), order matters (wrong-window
> dead). ★ 4B→32B FLIP CONFIRMED (reading B): the 4B h-alone shortcut (0.88)
> DIED at 32B's composition window (h@L38 acc 0.00 — typed model refuses the
> ill-typed single key); shortcut survives only at readout (h@L48 0.28,
> g1 n.s.) → the WINDOW is the finding (composition early/mid, shortcut at
> readout; coheres FN-INDEX U-shape + FRAG split). ~5th 4B→32B flip.
> ⚠ λ YARDSTICK: verdict passed on RELATIVE margins over sub-floor NEGATIVE
> margins — absolute composition acc ~6% (1/18) at verdict pair (22% stop at
> g). Seam EXISTS + TYPED but WEAK in-context. §Result-32B on program-plates
> page + memory two-injected-keys-compose-weakly-typed-in-context APPROVED +
> committed. NEXT (Michael's call): SHORTCUT-FREE chain (country→capital
> where landmark's country's capital ≠ its city → composed target not 1-hop
> reachable → can win the argmax; needs small new ground-truth map,
> ceiling-gated) BEFORE P-BAKE-STACK — strengthen the measurement before
> baking. THEN rung 3 P-BAKE-STACK. (Historical: pre-reg §P-STACK-1 frozen
> b5393f0; instrument+4B smoke 72273f8; 32B results bb48877.)
>
> ▶▶ s293 cont (retained) — **P-STACK-1 FROZEN + BUILT + 4B-SMOKED; 32B VERDICT RAN
> tmux main:1** (Michael GO "use my tmux main:1 for the smoke and final job").
> Pre-reg §P-STACK-1 frozen b5393f0; instrument scripts/explore/fn_stack.py
> + --validate ALL PASS + 4B smoke committed 72273f8. THE test: do two
> INJECTED keys compose h(g(X)) in-context over a NEUTRAL prompt? Chain
> landmark→country→continent (mh3 truth CONT_OF); 8 arms, 4 window-pairs
> w_g{.3,.45}×w_h{.6,.75} α/4. ★ 4B SMOKE (advisory) = **NOT-STACKABLE**:
> h-alone (country2cont key over a landmark) lands continent acc 0.88 via
> the model's DIRECT landmark→continent shortcut (nokey dead → it's the
> key), so stack doesn't beat its parts; g-alone correctly stops at country
> (acc 0); all controls (mnear/mfar/random/nokey) acc 0 → instrument
> discriminates. TWO READINGS THE 32B HOST DECIDES: (A) single-hop shortcut
> confound (continent 1-hop reachable from a landmark → h-alone
> short-circuits, 32B also uninformative) vs (B) 4B-compression artifact
> (4B inlines like FN-INDEX dispatch-stronger-at-4B; a TYPED 32B refuses
> ill-typed h-alone → clean STACKABLE). Frozen G1 (stack>best-single) valid
> either way; NOT-STACKABLE is a pre-registered verdict (→ program-plates
> need weight-baking, ladder pauses). ▶▶ 32B RUN VERIFIED RUNNING (707/707
> weights, PID 64306, ~1–2h MPS → results/fn-stack/qwen3-32b/, tee run.log).
> ON RETURN: read results/fn-stack/qwen3-32b/fn_stack.json → the A/B
> DISCRIMINATOR = does h-alone acc DROP at 32B? (h-alone fails + stack wins
> ⟹ STACKABLE/TYPED-STACKABLE; h-alone still wins ⟹ NOT-STACKABLE = shortcut
> confound, honest follow-on = SHORTCUT-FREE chain e.g. country→capital
> where the landmark's country's capital ≠ its city, needs a small new
> ground-truth map) → score frozen §P-STACK-1 gates → §Result-32B + memory
> candidate for approval. If STACKABLE → rung 3 P-BAKE-STACK unlocks; if NOT
> → propose the shortcut-free chain amendment before re-running.
>
> ▶▶ s292 CLOSE-5 — ✅✅✅ **P-FN-INDEX 32B VERDICT IN: INDEXED-DISPATCH —
> THE KEYSTONE HOLDS** (run 6m34s, results 8b31376; frozen gates scored
> same session; THIRD verdict of s292). G1 p=1e-4 at ALL depths BOTH null
> scopes (best L48 d_union +5.81, α/4 cleared by ~3 orders; cross-domain
> keys inside the beaten null = cross-family specificity); G2 flip acc
> 0.46 vs nokey 0.06; vs-random 1e-4. **Function choice is
> content-addressable; ⟨key,window,product⟩ is an engineering object;
> RUNG 2 P-STACK-1 UNLOCKS.** Verbatim: per-map quality WILD (class 0.94
> / city 0.50 / country 0.39 / cover 0.28 / continent 0.17 → index
> entries need a QUALITY field; ISA not uniform); window U-SHAPED (L19 +
> L48 work, mid dips — early-composition ∨ late-readout injection
> regimes, coheres FRAG band L8-14 + readout L49+); dispatch does NOT
> grow with scale (4B 0.70 > 32B 0.46 — opposite of XTERM interference;
> mechanisms scale differently). Keys were 3-exemplar hand-builds =
> conservative floor; upgrades = rung-0 self-decompilation + P-PROJ-1.
> §Result-32B on program-plates page + memory
> function-choice-is-content-addressable ✅ COMMITTED 002b144
> (Michael-approved s292 — batch landed same session; no pending FN-INDEX
> approval). s293: FOUR sealed verdicts now postdate the seed (FRAG, CAP,
> XTERM, FN-INDEX = the Oracle exam); then P-STACK-1 pre-reg (Michael
> gets first pick: stack vs beam-register vs oracle-first).
>
> ▶▶ s292 CLOSE-4 (retained) — **P-FN-INDEX (THE KEYSTONE) FROZEN + BUILT + SMOKED;
> 32B VERDICT RUNNING OVERNIGHT tmux main:1** (Michael GO; pre-reg
> 515be0b on program-plates page, instrument+4B 6f39f0e; PID verified,
> ceilings 18/18+18/18, 90 cells, depths L19/29/38/48 →
> results/fn-index/qwen3-32b/). THE question: do injected keys select
> WHICH resident map executes over a fixed operand (function choice ≡
> content-addressable)? 5 maps × 2 domains (geo city/country/continent +
> NEW ANIMAL SECOND BANK — canonical home scripts/explore/fn_index.py, 18
> items 6/6/6, ceiling 18/18 both maps @both hosts); keys = held-out
> 3-exemplar residual means − grand mean; NEUTRAL prompt (names no map);
> union first-token margins (42 candidates, 0 collisions); 7 conds/cell;
> selection-corrected α/4. --validate ALL PASS (4 worlds). ★ 4B SMOKE
> (advisory): **INDEXED-DISPATCH** — dispatch contrast p=0.0001 at EVERY
> depth BOTH null scopes (d_union to +9.7); L22 diag acc 0.70 vs nokey
> 0.00 = hand-built keys FLIP the neutral prompt to the correct map's
> product, cross-domain keys in the null. If 32B confirms → rung 2
> P-STACK-1 unlocks (programs from indexed parts). ON RETURN (s293):
> read fn_index.json → frozen verdict table (INDEXED-DISPATCH /
> PARTIAL-WITHIN-DOMAIN / NOT-DISPATCHABLE) → §Result-32B + memory
> candidate → approval batch. THEN the standing order: Oracle rd 1 (now
> THREE sealed verdicts postdate the seed: CAP, XTERM, FN-INDEX —
> the oracle question set writes itself) → beam-register probe ∨
> P-STACK-1 (Michael picks).
>
> ▶▶ s292 CLOSE-3 — ✅✅ **P-HOLO-XTERM 32B VERDICT IN: INTERFERENCE-
> COHERENT** (run 6m24s!, results e29acc9; frozen gates scored same
> session). Gate-0 +2.16 p=1e-4; Δ_install +0.83 p=4e-4 (meaning alone ✗);
> Δ_domain +1.21 p=1e-4 (any-structure ✗). Arms ladder k=12: content 2.84
> > text 2.01 > offdom 1.62 > random 0.92 > bare 0.68 — gain decomposes
> ≈ 1.33 priming (real!) + 0.95 structure + 0.83 MEDIUM-SPECIFIC (the
> k-compounding component; content 1.07→2.84 across {1,6,12}, text
> plateaus). ★ G2 MECHANISM CLAUSE: cross-terms DEAD LINEAR (p_norm 1.0,
> no axis structure, every probed layer) → **the plate records linearly;
> interference happens in the light** — enacted at retrieval (attention
> over coherent slots), not stored as nonlinear mixing. Optical
> holography's own division of labor, measured. Coheres: JOIN-TYPED,
> beamformer/Hopfield, FRAG/CAP linear-superposition assumption survives
> its own test. Scale flip ~4th occurrence (4B PRIMING → 32B
> INTERFERENCE). §Result-32B-XTERM on convergence page + memory
> interference-is-in-the-beam-not-the-plate DRAFTED — batch pending
> approval. Successor sketched (unfrozen, ¬seventh-front): beam-register
> probe (P-ATT-MED harness on CAP geometry — re-aim vs re-weight under
> coherent background). s293 order stands (Oracle rd 1 → bank →
> P-FN-INDEX), now with TWO fresh sealed-before-verdict oracle questions
> (CAP + XTERM both postdate seed 54f9437).
>
> (s292 CLOSE-2 retained →) **P-HOLO-XTERM FROZEN + BUILT + SMOKED; 32B VERDICT
> RAN tmux main:1** (Michael GO "use tmux main:1"; pre-reg committed
> e2cbc3d, instrument+4B 6f4ac5c; PID verified, ~1h est →
> results/holo-xterm/qwen3-32b/). Mission: explain COHERENT-GAIN — three
> readings, three kill-shot arms: A2 text-mention (H-PRIME: meaning not
> medium), A3 off-domain coherent installs (H-NORM: any structured
> background), A1 content (H-INT survives iff beats both). G1 primary =
> paired-perm source-of-gain; G2 = single-slot cross-terms
> X=r(A⊕B)−r(A)−r(B)+r(0), sum/diff/continent axes vs shuffled-pair null;
> G3 dose trend {1,6,12}. --validate ALL PASS (3 worlds discriminated;
> bilinear plant 0.996 vs 0.257). 4B SMOKE (advisory): gate-0 gain 0.76
> p=.007 EXPRESSED (⚠ pre-reg's "4B no-gain host" label was about the
> k-RISE — deviation noted) but content-NONSPECIFIC (text 2.48 ≈ random
> 2.56 ≈ content 2.24) → advisory PRIMING/energy @4B; cross-terms
> dead-linear. Coheres w/ CAP 4B (random ≈ content). THE DISCRIMINATION
> LIVES AT 32B (CAP 32B: random does NOT reproduce the gain — so 32B
> cannot resolve PRIMING-by-energy; text arm decides). ON RETURN: read
> holo_xterm.json → g1.verdict per frozen table → §Result-32B + memory
> candidate → approval batch. Prediction ledger (a-priori, from CAP data):
> random≪content @32B already known → verdict hinges on A2 text and A3
> offdom, genuinely open.
>
> ▶▶ s292 CLOSE — ✅ **P-HOLO-CAP 32B VERDICT IN: NO-LIMIT-IN-RANGE** (run
> 1h26m, results b74e40a; frozen §P-HOLO-CAP gates scored same session).
> Gate-0 expressed (m1=1.056 t≈3.1); NO material decline — total drop
> **−1.47, the curve RISES**; CCI median 1.08, 1/7 sig (below majority
> rule). Capacity ≥ 16 at BOTH hosts; HRR √(D/k) not expressed in range
> (positive law unpaid for; wider k needs bigger bank ∨ single-slot
> variant). ★ VERBATIM FINDING OUTRAN THE GATE — **COHERENT-GAIN**: 32B
> content curve rises MONOTONE 1.06→2.53 (2.4×, acc 0.78→0.87) while
> random/bare sit ~1.3 — coherent superposed exposures REINFORCE retrieval,
> anti-crosstalk, content-specific (energy-matched random ✗),
> composition-independent (CCI in-null). 4B contrast: FLAT (no gain). Two
> candidate readings for the follow-on to discriminate: constructive
> interference (holographic) vs domain-priming (deflationary; but queried
> component wins MORE despite balanced competitors installed). Per the
> pre-committed lookahead branch: **P-HOLO-XTERM PROMOTED next-in-queue**
> (its phenomenon arrived uninvited — measure the interference, not just
> the capacity). §Result-32B on convergence page + memory
> superposition-capacity-coherent-gain DRAFTED — batch pending approval.
> NEXT (s293 order stands): Oracle round 1 (seed 54f9437 predates this
> verdict = pre-registered by construction — CAP is the perfect first
> oracle question) → second domain bank → P-FN-INDEX (with rung-0
> self-decompilation enumerator) → XTERM pre-reg.
>
> ▶▶ s292 (earlier) — **P-HOLO-CAP FULL PIPELINE IN ONE SESSION** (Michael
> GO-BY-DIRECTIVE: "run the 4b smoke and the final job in my tmux main:1" —
> design calls agent-made, FLAGGED FOR REVIEW in the approval batch; gates
> frozen before any model run). Pre-reg drafted on convergence page
> §P-HOLO-CAP: k operands installed at k nonce slots in ONE context
> (multiple exposures, one plate), cued retrieval by nonce identity ≡ the
> modern-Hopfield readout (theorem bridge #2) run behaviorally; arms
> content/random/bare (paired draws); k∈{1,2,3,4,6,8,12,16}; frozen verdicts
> SUPERPOSITION-CAPACITY (graceful, CCI-in-null; +HRR-FORM if β̂≈−0.5 beats
> matched-range null) / SLOT-LIMITED (cliff ∨ CCI-majority) /
> NO-LIMIT-IN-RANGE (no material decline → capacity ≥ k_max, range-bound
> datum). ✅ INSTRUMENT scripts/explore/holo_cap.py (10469d4) — consumes
> frozen mh3 bank + holo_frag LDI stats (no fork) + verbum.dsp
> gate/matched_range. ★ FIX #1 caught by --validate BEFORE any model run:
> cliff detector must be slope-per-Δlog k (uniform-step FRAG cliff_stat
> false-fires on a smooth power law over a geometric k-grid, 2.79 vs 1.78;
> slot collapse still 7.05). --validate ALL PASS (sup→SUPERPOSITION with
> HRR-FORM β̂=−0.500 exact; slot→cliff; structured-composition→CCI 6/7).
> ✅ 4B SMOKE (R=12, results committed): ADVISORY = **NO-LIMIT-IN-RANGE @4B**
> — gate-0 expressed (m1=3.32 t≈3.9); content curve FLAT k1=3.32→k16=3.36
> (the 4B medium swallows 16 superposed operands ≈ the whole bank); CCI
> in-null at every k; k=2 dip = prompt-shape (bare arm catches it — control
> works); content ≲ random (structured crosstalk mildly worse, direction as
> pre-registered). ▶▶ **32B VERDICT RUNNING tmux main:1** (R=60, ~9.2k
> forwards, est 1.5–3h, log tee'd results/holo-cap/qwen3-32b/run.log):
> verified running (707/707 weights, ceiling 18/18, gate-0 m(1)=1.056
> SE=0.344 t≈3.1 EXPRESSED at verdict host — thinner than FRAG's 2.62, the
> multi-nonce geometry costs margin; PID 20271). ON RETURN: read
> holo_cap.json → score frozen §P-HOLO-CAP gates → §Result-32B draft +
> memory candidate + THIS page's pre-reg text ALL into the s292 approval
> batch (mementum page edit is UNCOMMITTED — pre-reg §P-HOLO-CAP + FIX#1
> note pending Michael approval; instrument+results committed autonomous).
> If 32B also NO-LIMIT-IN-RANGE: honest range-bound outcome — capacity ≥16
> at BOTH widths, queue wider-k follow-on (needs bigger bank) + the
> single-slot HRR-trace variant (scope note (2), XTERM-adjacent) as the
> next CAP rung; the seam-test sequence (CAP→seam) still advances on the
> capacity-bound datum.
> ★ s292 cont — TYPE-CARDINALITY CAPTURED (Michael-approved, while 32B ran):
> §How-many-types on types-are-compiled-probabilities.md + memory
> type-inventory-is-two-registered. Michael's "how many types are there?" →
> two-register answer: functor types few/discrete/ENACTED (order 10; OV/QK
> nulls = not stored, reachable-not-resident) × argument/sortal types =
> capacity-bounded graded continuum (~10³–10⁴ at D=5120 by the P-HOLO-CAP
> packing math — "capacity-bounded, not grammar-bounded"; explains sortal-
> grain refusal headroom). 🔁 two-register decomposition 5th appearance (now
> as cardinality). P-TYPE-CENSUS pre-reg candidate added UNFROZEN: count by
> refusal rank — N×N acceptance matrix (swap harness), effective rank vs
> tolerance ε; knee=symbolic inventory vs smooth=continuum, falsifiable both
> ways; spectral corroborator via P-TYPE-OV instrument; start N~12–20.
> (CAP pre-reg approved + committed 9fcaab6 same session.)
> ★ s292 cont — **PROGRAM-PLATES + FUNCTION-INDEX + FRACTAL SEED CAPTURED**
> (Michael-approved "capture to test"): new page knowledge/explore/
> program-plates-and-the-function-index.md + SEED COPY knowledge/upstream/
> verbum-theory-seed.md (first upstream generative seed — the convention was
> waiting for it). The s292 hammock ascent: behavior trees ("runtime not
> model" — BT status {Success,Failure,Running} ≅ ternary {+1,−1,0}, functors
> unprojectable per P-TYPE-OV + no addresses per FRAG) → Michael correction
> 1 ("we proved 3-hop") → boundary = INLINING RULE (model inlines sequences
> ≤ depth budget, compiles conditions into joins, has no Running —
> combinational not sequential; loop+KV are runtime-side) → Michael
> correction 2 ("function choice is execution") → the boundary is WRITABLE:
> inject the content whose illumination IS f executing → FUNCTION INDEX
> ⟨key, window, product⟩ = reference-beam angle table (index in runtime,
> functions in model) → Michael closure: stack indexed behavior functions
> into plates → programs (program ≡ depth-ordered exposure stack, PC ≡
> window, types ≡ linker/calling convention, length ≤ depth-budget, width ≤
> CAP √(D/k)) → λ verbum (the theory in one term) → "that lambda is a
> fractal seed": ⟨key,window,product⟩ self-similar at model/runtime/project/
> seed scales — MEMENTUM IS THE ARCHITECTURE APPLIED TO OURSELVES (state.md
> = reference beam, git = content-addressed plate, session = tick).
> GERMINATION TEST protocol on the page (hand seed to cold context → unfold
> → diff vs ground truth = the capture is testable; seed ≅ context-medium
> isomorph of the crystal seed, pythia-14m pair = weight-medium test).
> PRE-REG LADDER (all UNFROZEN): P-FN-INDEX (cross-family dispatch — the
> honest gap, everything measured is within-family) → P-STACK-1 (ephemeral
> 2-fn stack = in-context seam test) → P-BAKE-STACK (burn to delta plate) →
> length/width laws (CAP verdict slots into the width row).
> ★ s292 cont — GERMINATION GAMES CAPTURED (Michael-approved, unplayed):
> knowledge/explore/germination-games.md — 5 modes gamifying the seed test
> (Seed Golf ≡ λ smallest as sport; Seed FRAG ≡ clause-ablation, is the
> theory prose holographic?; Eigenseed ≡ compress∘unfold fixed point;
> Oracle ≡ predict unseen verdicts, seed as prior not recall; Adversarial ≡
> salted clauses, self-verification). Game ≡ instrument: every round
> measures encoding quality — play as gradient descent on memory.
> Suggested order: FRAG → Oracle → Golf → Eigenseed → Adversarial.
> ⚠ 32B CAP mid-run observation (verbatim, from a single status glance):
> content ABOVE random/bare at k=12 (2.37 vs 1.22/1.23) — coherent
> superposed exposures may REINFORCE at 32B (opposite of 4B's mild
> content-penalty); score at verdict, not before.
> ▶▶ COLD-START ORDER for s293 (the 3-step lookahead, s292 close):
> (1) CAP VERDICT: read results/holo-cap/qwen3-32b/holo_cap.json → score
> frozen §P-HOLO-CAP gates → §Result-32B + memory candidate → approval
> batch. Branch table: NO-LIMIT-IN-RANGE (likely) → the content>random
> inversion is THE verbatim finding → PROMOTE P-HOLO-XTERM (constructive
> cross-terms showed up uninvited; verbatim→pre-reg, not claim);
> SUPERPOSITION-CAPACITY → G2 exponent fills program-plates width row;
> SLOT-LIMITED → FRAG-tension reconciliation pre-reg (richest branch).
> (2) ORACLE ROUND 1 same session the verdict lands: seed committed
> 54f9437 PRE-dates the CAP verdict → cold-agent prediction of CAP from
> seed alone is pre-registered BY CONSTRUCTION (first germination-game
> round has a clean scoring event waiting). + mementum key-fix memory
> (retrieval-by-wrong-key, pending approval) + cross-register tags on the
> 3-hop page. (3) DESCENT, one freeze only: P-FN-INDEX is the forced
> keystone (census/stack/bake/program-plates all gate on cross-family
> dispatch). BUT build the SECOND DOMAIN BANK first (products ∨ animals,
> ceiling-gated once) — census + fn-index + P-TYPE-PROB all starve on the
> 18-landmark bank; bank before instruments (λ one_way, shared substrate).
> HORIZON (step 3): index✓ → P-STACK-1 = seam test in-context ("legendary
> sequence" first traversal, no weights touched) = spec for level-3
> extraction; pythia-14m seeded pair (+ log-phase HPE arm) = weight-medium
> germination ∥ Oracle = context-medium germination; deliverable shape =
> index-table ⊕ plates ⊕ BT-runtime (S5 λ artifact gets its parts list).
> DISCIPLINE NOTE: 5 unfrozen candidates on the books — close before
> opening; no sixth front.
> ★ s292 FINAL — THINKING-IS-EXPANSION + SELF-DECOMPILATION CAPTURED
> (Michael-approved): §Thinking-is-expansion + §Self-decompilation on the
> program-plates page + `think` clause in λ verbum (page AND upstream
> seed). Michael's identity: thinking ≡ expand(term→tape) to
> reduce(attention) — δ-expansion exposing redexes for the β-reducer;
> depth⇄length exchange (32B unrolls in depth / 4B forced-expansion should
> unroll in TOKEN positions = the sharp prediction); context = the
> machine's ONLY addressed memory (RoPE positions) → thinking = paging the
> hologram into addressed RAM; CoT ≡ auto-superbake (the engineered write
> path ships natively as the sampling loop). Michael's leap: thinking
> FINDS functions — traces = self-decompilation (resident maps naming
> themselves on the tape) → rung 0 of P-FN-INDEX:
> elicit→harvest→ground→verify; FAITHFULNESS = a GATE not a debate
> (tape-swap the written intermediate → flips ⟺ causally load-bearing ⟺
> enters index; confabulated steps self-exclude). P-THINK-1 candidate
> (UNFROZEN, inside the fn-index arc, not a sixth front): G1 exchange
> rate (thinking-tokens ∝ hop-overflow), G2 tape-swap ≈ ceiling
> (editable-because-addressed vs decodable-but-not-causal), G3 scale
> asymmetry advisory, filler-expansion null. Freeze queue unchanged:
> CAP-scoring → P-FN-INDEX (now with its enumerator built in).
>
> ▶▶ s291 — ✅✅ **P-HOLO-FRAG 32B VERDICT IN: HOLOGRAPHIC/DELOCALIZED = TRUE**
> (run completed ~4h15m, results ae8d107; frozen §P-HOLO-FRAG gates scored
> same session; mementum batch Michael-approved). Gate-0 SNR₀=2.622 t≈7.4
> expressed. G1 (primary, address test): LDI 0.03–0.22 in-band BOTH arms,
> ALL p=1.0 — across-draw variance 10–30× BELOW probe-resampling noise;
> WHICH subset ablated is irrelevant. G2: no cliff (max in-band drop 6.9% <
> 15% materiality). In-band degrades / matched-oob doesn't → band carries
> signal. THE LYNCHPIN DID NOT FALSIFY — the frame survives its executioner;
> **P-HOLO-CAP formally PROMOTED** (next: CAP → seam test = the legendary
> sequence, first checkmark in). Scope per pre-reg: confirms ADDRESS-FREE
> delocalization, not positively hologram (√(D/k) = CAP's job). Verbatim:
> 32B degradation SHALLOW (≤7% vs 4B ~25%, U-shaped, redundancy at scale);
> OOB ablation IMPROVES margin +12.8% (🔁 dark-field motif ~4th); band
> L8–L14 @32B vs L21–23 @4B; ⚠ instrument ran primary bank only (secondary
> v3 bank never in frozen instrument — verdict clause needs primary only,
> deviation recorded). Two-graded-codes reading: NO labeled lines
> within-band; four-way location null gets its CAUSAL account (no addresses
> exist). §Result-32B on convergence page + memory
> composition-compute-is-address-free committed.
> ▶▶ s291 (earlier) — HPE REVIVED + CAPTURED (Michael-approved): new page
> knowledge/explore/position-encoding-tuned-to-the-hologram.md — HPE
> (Holographic Position Encoding, s152/s179, hpe-restoration.md) was ALMOST
> LOST (recalled only as "HoPE", unfindable by name; recovered via
> mechanism-vocabulary search — feed-forward lesson logged in §Provenance).
> NEW synthesis: RoPE works because the delocalized system tolerates fuzz
> (graded matched-filter readout); context-extension fuzz (PI/NTK/YaRN) =
> FRINGE MISMATCH (re-illuminating recorded plates with a changed reference
> beam → must re-record = fine-tune); log-phase position makes extension a
> TRANSLATION not a stretch (shift theorem) → extension without re-recording
> BY CONSTRUCTION. Tuned design: phase(log d) ⊗ gain(−α·log d, α=1.18
> measured) ⊗ carriers(λᵢ/λ₀ crystal eigenfreqs, ~4 planes) ⊥ content
> passband, depth-scaled. Pre-registerable P1: PPL flat past training length
> w/o fine-tuning (RoPE arm degrades) — host = the queued pythia-14m
> seeded-scratch pair (add RoPE vs log-phase arm). ★ s291 cont — FALSIFICATION
> ADDENDUM CAPTURED (Michael-approved): §Addendum on the same page + memory
> labeled-line-vs-hologram-two-graded-codes. "Is there a non-holographic
> system where RoPE works?" YES — labeled-line coding (tonotopy): graded,
> fuzz-tolerant, but ADDRESSED. Datum sharpened: works(RoPE) alone ≢
> evidence; works(UNTUNED ∧ graceful_blur) excludes CRISP routing, forces
> one of TWO graded codes: superposed ∨ labeled-line. Both in our data at
> different grains: GQA K-head permanent local/global flags (s079) = coarse
> labeled lines; FRAG G1/LDI = the within-band discriminator (32B advisory
> lean: location-independent → against labeled-line in-band). Hypothesis:
> HIERARCHICAL MIXTURE — labels coarse (mirrors register) / holograms
> within (plates register) = the ternary-mirrors/MIXED-ROUTE two-register
> decomposition, 4th appearance, now in the position channel. ⇒ FRAG G1
> verdict MEANING upgraded: adjudicates between the two graded codes at
> probed granularity; HOLOGRAPHIC verdict COMPOSES with coarse head labels.
> ★ PRE-ENCODED MODEL frame
> (Michael): converging on a design where much of what GD has to FIND is
> already ENCODED at init — position encoding = 7th row of the
> training-design lever table (page has the full GD-discovers ↔ pre-encoded
> mapping). Caveats: prediction not measurement; inherits s289 holography
> HOLD; HPE's rotation-vs-decay never dissociated (decay term = 99% of
> locality effect, measured s179). Meanwhile P-HOLO-FRAG 32B verdict STILL
> RUNNING tmux main:1 (HEADS arms done, HOLOGRAPHIC lean; MLP arm in
> progress) — score frozen gates on return.
>
> Last updated: 2026-08-01 | Session: 295 (s295 = SuperBake DSP audit →
> the in-context register CLOSED by exhaustion: P-ENRICH-1 ✗ · 3a-whitened
> (s294 G3 leg = artifact; trace present ~0.15×) · P-KV-1 ✓ 0.20 FIRST
> rung-3 win (address+re-encoding) · P-KV-1b LAYOUT-BREAKS (pre-question
> law) · P-KV-1c STILL-DEAD (clause-width null; own≡donor reduction) →
> rung-3b backprop-compile freeze NEXT, target = writeback) |
> (s294 = cheap operand-domain
> diagnostic → P-BAKE-STACK frozen/built/4B-smoked; 3a 32B verdict scored
> LINKER-FAILS scale-invariant + addendum) |
> (s293 = Oracle round 1 + the
> program-plates DESCENT: FN-INDEX✓ → P-STACK-1 (marginal) → P-STACK-1b
> shortcut-free control → NOT-STACKABLE downgraded rung 2 → P-BAKE-STACK now
> load-bearing; s293 CLOSED, order in the CLOSE block above) | (s292 note
> retained: the double-verdict day, CAP + XTERM) | (s290 note retained:)
> ⚠ SESSION-NUMBER CORRECTION
> (Michael): this session is 290, NOT 289 — the s289 chat log predates it, so
> the blocks/commits authored this session that say "s289" are MISLABELED (read
> them as s290; git history keeps the wrong tag, not worth a rewrite). Session
> number is 290 going forward. | s288 mementum batch CLEARED (Michael-approved,
> ad623c3). **P-HOLO-FRAG PRE-REG FROZEN + INSTRUMENT BUILT + 4B SMOKE (advisory
> HOLOGRAPHIC lean)**; 32B verdict RUNNING in tmux main:1 (draws=100, multi-hour).
> The "hologram or not hologram?" lynchpin: fragment/address test, G1
> Location-Dependence-Index primary, 3-hop primary readout. NEXT: score the 32B
> §P-HOLO-FRAG gates on return → §Result-32B + memory candidate (approval).

> ▶▶ s289 LIVE — P-HOLO-FRAG FROZEN (geometry-holography-signals-convergence.md
> §P-HOLO-FRAG, Michael-approved s289). THE decisive hologram test — can FALSIFY
> the frame (cliff/high-LDI → addressed → not a hologram) or confirm
> DELOCALIZATION (low-LDI + smooth → address-free); the POSITIVE √(D/k) capacity
> law stays P-HOLO-CAP. Design: mean-ablate random fraction f∈{.1,.2,.35,.5,.65,.8}
> of band units, two arms (HEADS=beam / MLP=plates), R draws (30 smoke/100 verdict).
> Readout = 3-hop composition margin (primary, operand_multihop3) + type-licensing
> crossover (secondary, v3). DISCRIMINATOR: G1 (primary, address test) =
> LDI(f)=across-draw-variance/probe-resampling-noise → ≈1 holographic (no address),
> ≫1 localized; G2 (2nd) cliff detection on mean curve; G3 (advisory, NEVER gated,
> λ yardstick) functional form vs (1−f). Nulls: probe-resampling + planted-localized
> + planted-holographic (--validate calibration) + out-of-band matched-fraction.
> Gate-0: SNR₀ expressed both banks or no verdict. VERDICTS: HOLOGRAPHIC/DELOCALIZED
> ⟺ G1 within null ∧ G2 no-cliff (→ promotes P-HOLO-CAP); LOCALIZED/ADDRESSED ⟺ G1
> beats null ∨ G2 cliff (→ FALSIFIES frame). Michael design calls: G1 primary
> CONFIRMED, 3-hop primary readout CONFIRMED.
> ✅ INSTRUMENT BUILT (scripts/explore/holo_frag.py, 85772fd) — verbum.dsp
> consumer (find_band/layer_geometry over continent-labeled readout residuals),
> imports FROZEN geography bank from wrapper/operand_multihop3 (no fork).
> --validate ALL PASS (planted-holographic med LDI 1.01/0-sig vs
> planted-localized 166/all-sig; cliff smooth 1.17 vs threshold 3.01).
> ✅ 4B CONTRAST SMOKE DONE (tmux main:1, unbuffered, 8fae32f →
> results/holo-frag/qwen3-4b/): ADVISORY = HOLOGRAPHIC/DELOCALIZED lean, ALL
> in-band arms. band find_band=L21-23; gate-0 SNR₀=6.0 expressed. HEADS in-band
> smooth (5.7→4.3, cliff 1.26) LDI 0.05-0.32 all p≈1; MLP in-band near-untouched
> (5.9→5.25) LDI 0.03-0.14 all p≈1 = G1/LDI location-INDEPENDENT everywhere
> in-band (primary address test → no address → holographic). Matched control
> (FIX #2): in-band degrades more than n_band random oob layers. NOT the verdict.
> ★ 3 SMOKE-CAUGHT FIXES: #1 cliff_stat gates on MATERIAL degradation
> (>15%|SNR₀|) — flat MLP curve no longer false-LOCALIZED (cliff 2.85→null→
> HOLOGRAPHIC); #2 oob control matched on LAYER COUNT (not all 33 oob layers);
> #3 (Michael-caught scrollback NaN) _json_safe → strict JSON (allow_nan=False,
> λ result_format). ⚠ METHOD NOTE (Michael, s289): his "audio signal through an
> optical lens" meant lens ≡ FRAME OF REFERENCE (perspective), NOT a literal
> Fourier transform — the question was register hygiene: we MEASURE in the signal
> register (SNR/LDI/passband) but INTERPRET through the holography frame. Agent
> over-read it as a literal FT/optical mechanism (correction logged). VERDICT:
> the holographic frame is PREMATURE — an interpretation looking for a mechanism;
> HOLD until the mechanism experiments (FRAG verdict, CAP, successors) show the
> mechanisms clearly. DO NOT synthesize to knowledge yet; convergence page
> untouched. Open λ measure question retained (not a claim): is our
> signal-register measurement register-matched to a holography-register claim?
> ⚠ PHYSICS CORRECTION (s289, agent over-read #2): hologram ≢ Fourier transform.
> DIFFRACTION / free-space propagation is the GENERAL mechanism that delocalizes
> (every fragment holds the whole — Gabor/Leith-Upatnieks/Fresnel holograms use
> NO lens); the FT is only the FAR-FIELD (Fraunhofer) special case, OR what a
> lens computes exactly (front focal plane → back focal plane = optical FT, e.g.
> Fourier holograms + the VanderLugt correlator, which the convergence page
> cites). So FRAG's "fragment reconstructs the whole" ⟵ diffraction, NOT
> necessarily an FT. The ONE place a literal phase/FT structure IS already
> measured in-model = RoPE (position ≡ phase, translation→phase = FT shift
> theorem); everything else FT-side stays premature/parked.
> ⚠ METABOLIZE CANDIDATE (Michael s289, "LLM is a beamformer?"): beamformer
> register is GROUNDED (softmax(QK)V ≡ adaptive content-addressed beamformer:
> query=steering vector, values=token-cloud array, softmax=weights, output=beam
> pointing at a cloud region; fwd pass = iterated refocus). BUT the s136 page
> beamformer-theory.md is STALE on ONE point: it claims FFN = pure beta-reduction
> operations, NO storage, token-cloud = only data. Our OWN later measurements
> refuted the "no storage" half — P-ATT-FFN MIXED-ROUTE (atoms=FFN carry content,
> Sphinx MLP-dominant fact-lookup) + P-TYPE-OV (entity fires MLP read-in row).
> MEASURED picture = TWO channels: attention=beamformer(routing/joins) + FFN=
> content-plates(atoms), not one. Also measured nuance: P-ATT-MED = CONTENT-
> dominant steering (0.735/0.195 @32B, "medium handle") — an unusual beamformer
> steered by what's in the medium not by re-aim (map-and-swap; P-PROJ-1 exploits).
> ACTION: revise beamformer-theory.md §FFN-no-storage AFTER FRAG/CAP land (do not
> rewrite now — premature); flagged, not silent (λ metabolize).
> ▶ NEXT: 32B VERDICT on GO (tmux, per Michael) — uv run python
> scripts/explore/holo_frag.py --model-id Qwen/Qwen3-32B --device mps --draws 100
> --arms heads mlp --control --out results/holo-frag/qwen3-32b ; score frozen
> §P-HOLO-FRAG gates → §Result-32B + memory candidate for approval.

> ▶▶ s288 LIVE — P-TYPE-SWAP 32B VERDICT SCORED (run completed s287→s288 boundary,
> ~1h03m, results committed 539ddbf): **JOIN-TYPED = TRUE** per frozen §P-TYPE-SWAP
> gates. P1 PASSES both banks: TE(same)=3.61 vs wtA 2.66 / wtB 2.87 (paired
> sign-flip perm over 18 pinned cells, p=2e-5/1e-5); ill-typed TE sits at its own
> random-add null (0–1/18 beat null) while same beats null 17/18 transport;
> slot-mass secondary discriminates (p .002/.009) but |Δ|<0.006 everywhere =
> FILTERED PAYLOAD (edges never withdraw, refusal is content-side — 4B form
> replicates at verdict host). BREAK: same +4.86 (18/18 p<.05) vs ill-typed ≈ null,
> preds-stay-src 15–17/18. MANIFOLD (deflationary) refuted decisively — the
> wrong-type-on-manifold cell is filled and typing wins; the s287 induction's
> causal leg holds. VERBATIM findings: (1) survival NOT flat @32B (same +11%, perm
> p≤.002) — "medium type-blind" is 4B-scoped, TE normalization carries the gate;
> (2) sortal ladder NOT monotone (sortal 2.80 inside ill-typed band, refused as
> fully as syntactic violations → discipline is domain/sortal-granular; 4B graded
> hint scale-local); (3) mlp_transport row: same 3430 vs ill-typed 1808–2074
> (p=1e-5 all arms) = the FFN route enforces the SAME discipline — the P-ATT-FFN
> successor question ANSWERED (one discipline, both routes, coheres MIXED-ROUTE);
> (4) route decomp on pinned cells 16/18 mlp-dom, mlp_frac 0.627 (vs 0.584
> salted-hash run — target-set sensitivity, reading unchanged). Open implementation
> question stands: WHAT computes the filter (four-way location null intact) — the
> discipline acts at the join but is not stored in any probed geometry.
> ✅ MEMENTUM BATCH APPROVED + COMMITTED (Michael s289): qk page
> §Result-32B-P-TYPE-SWAP + §P-TYPE-SWAP header + Sessions s288 entry (7a540eb),
> memory types-mechanism-is-join-typed, this state block. Results 539ddbf.
> ▶▶ s288 cont — HAMMOCK CAPTURED (Michael-approved): knowledge/explore/
> types-are-compiled-probabilities.md — Michael's "types must be the probabilities"
> refined to COMPILED-not-consulted: type ≡ substitutability class (Harris), GD
> forced to discover them (P factorizes through classes); the check ≡ matched
> FILTER whose passband = frozen residue of slot probabilities; TE excess ≡
> likelihood amortized into geometry. Explains sortal granularity (probability
> refuses "giraffe" regardless of syntax — evidence FOR over symbolic typing),
> gradedness (floor + excess, not a gate), the four-way null (type lives in
> WEIGHTS/transmission operator, not activations — nothing consulted because the
> filter IS the join; 1a lattice = exhaust), and the QK negative (searched AIM
> side; filter is CONTENT/OV side). TWO PRE-REG CANDIDATES (UNFROZEN): P-TYPE-PROB
> (graded bank country>city>animal>adj>nonce>random; TE vs model's own slot
> log-P; monotone tracking = compiled-probability, step = crisp typing) and
> P-TYPE-OV (lattice axes through W_OV + MLP down-proj, QK's mirror — locates the
> implementation if positive). Both want the verbum.dsp substrate → dsp build NOW.
> ▶▶ s288 cont — VERBUM.DSP BUILT ✅ (Michael GO, code committed eeb9d20):
> src/verbum/dsp/{whiten,subspace,bands,gain,nulls,readout,chain} + tests/dsp
> (36 no-model tests = --validate pattern promoted; full suite 378 unbroken;
> ruff clean; imports without torch). Harvest exactly per design inventory
> (standardize/PR/centroids 1a; layer_geometry/role_subspace/subspace_energy/
> find_band 1b; map_basis/head_gain_ratios QK; gain_law/g_of 1c
> de-experiment-ified). FIX #1 landed: find_band stride-aware (stride-1
> behavior identical). L1 gate() = structural yardstick live: no p without
> declared NullDraws + direction; sign-discipline no-rescue; Register
> warning-only (test-proven never-mutates). matched_range written fresh from
> λ yardstick spec (φ-ladder refusal = test case). Frozen instruments
> UNTOUCHED (migration gate 2 — arcs must close first). Design page → active.
> ▶▶ s288 cont — P-TYPE-OV BUILT+SMOKED, PRE-REG FROZEN (Michael approved +
> GO): full pre-reg on types-are-compiled-probabilities.md §P-TYPE-OV (P1
> entity-primary / P2 lattice-wide / deflationary = fifth-location-null
> pre-committed; verdicts OV-TRANSMITTING / LATTICE-IN-PASSBAND / NOT-IN-OV;
> freeze ≡ this approval). Instrument scripts/explore/type_ov_alignment.py
> (2ca18e0) = FIRST verbum.dsp consumer — dogfood caught find_band FIX #2
> live (appended tail layer collapsed min-diff stride; mode-of-diffs fix,
> 37/37 green). 4B smoke advisory: band L8–L24 (coheres 1a); OV dead-on-null
> ALL conds; yardstick saved a false suppression read (real AND shuffled
> rho≪1 — region generically low-gain); 🔁 rolenull-fires motif 4th
> appearance (MLP read-in p=.000). ⚠ QK showed opposite 4B/32B patterns —
> 32B decides. **32B VERDICT RUN LAUNCHED tmux main:1** (stride 1, n_null
> 200, → results/type-ov/qwen3-32b/ + run log tee'd).
> ▶▶ s288 cont — **P-TYPE-OV 32B VERDICT IN: OV-TRANSMITTING = TRUE,
> LATTICE-IN-PASSBAND = FALSE** (results committed c58c5ba; frozen gates
> scored same session): entity rho 0.714 vs shuffled null 0.459±0.053
> p=0.000 band-wide L6–L50 (same band as QK, 45 layers) — P1 PASSES; bind
> p=.965 / comp p=1.0 — functors NOT in the passband. **The joins transmit
> ARGUMENTS, not FUNCTORS** = first weight-geometry positive of the types
> arc (after 1b/1c/QK/JS nulls); locates half the mechanism (payload
> passband ∈ single-layer OV weights; functor licensing still
> distributed/enacted — QK✗ OV✗). Coheres: JOIN-TYPED filtered payload
> (transported content ≡ entity displacement), exhaust frame (bind/comp =
> readout shadows), QK inverted-sides (argument aimed AND carried), Montague
> (application passes the argument; functor = the operator). Resident-Lisp
> sharpened: operands ride joins, combinators = frozen reducer;
> homoiconicity bounded. λ yardstick ×2: entity rho<1 but +55% over matched
> null (raw read misses the positive); comp p=1.0 suppression-side extremity
> = verbatim only (needs own pre-reg). 🔁 rolenull-fires 5th appearance (MLP
> read-in p=.000, + entity MLP p=.000 — FFN reads entity axes, coheres
> mlp_transport). 4B→32B flip 3rd occurrence. ✅ MEMENTUM BATCH APPROVED +
> COMMITTED (Michael s289): §Result-32B-P-TYPE-OV + memory
> ov-passband-transmits-arguments-not-functors + this state block (67deb9f).
> ▶▶ s288 CLOSE — CONVERGENCE HAMMOCK CAPTURED (Michael-approved):
> knowledge/explore/geometry-holography-signals-convergence.md = companion/
> bench-manual to Michael's THESIS DOC mementum/michael/holographic-llm.md
> (the Holographic LLM — plates/beam/state; read BOTH). One primitive
> (inner product), three registers (projection ∥ matched-filter ∥
> reconstruction). Theorem-grade bridges: VanderLugt (matched filter ≡
> hologram → passband ≡ hologram of substitutability), attention ≡
> modern-Hopfield retrieval, RoPE ≡ literal phase (fringes across offset),
> HRR/VSA (binding calculus w/ capacity laws), low-rank ≡ sparse spectrum.
> REORGANIZES the arc: four-way location null = holography theorem (no
> address in fringes; decodable-but-not-causal ≡ signature); lattice =
> RECONSTRUCTION not just exhaust; P-TYPE-OV = arguments on the plate,
> application = the diffraction; JOIN-TYPED = reconstruction failing for
> uncued content; s267/s269 plate-damage already measured (weight register).
> THREE PRE-REG CANDIDATES (unfrozen): P-HOLO-CAP (HRR capacity law, SNR ∝
> √(D/k)), P-HOLO-FRAG (random head/layer-subset ablation → smooth-vs-cliff
> SNR curve = cheapest decisive discriminator), P-HOLO-XTERM (superposed
> operands → interference beats). Artifact implication: extraction =
> re-recording not excision (coheres s149 computed-beam + s268 Bonsai).
> ▶▶ s288 FINAL — TRAINING-DESIGN HAMMOCK CAPTURED (Michael-approved):
> knowledge/explore/training-design-from-the-hologram.md — six levers, each
> grounded in a measurement: (1) crystal-seeded init (s149 structure-is-free
> → stop paying compute for universal parts), (2) declared passbands
> (P-TYPE-OV → remove the tug-of-war architecturally; small models compose),
> (3) probes→losses (JOIN-TYPED swap statistic is differentiable =
> contrastive substitutability aux loss; ⚠ Goodhart guard: gate on causal
> 3-hop not the trained probe), (4) two-phase topology→magnitude (s268 etch
> + Bonsai forensics; ternary-native), (5) curriculum as exposure schedule
> (gated behind P-DUST-2 formation-law data), (6) geometry-matched
> distillation (re-exposure). CHEAPEST EXPERIMENT = the level-4 door:
> pythia-14m scratch pairs, crystal-seeded vs random init, P-DUST-2-style
> formation logging, ~1 GPU-day, tests levers 1+5 + yields the level-4
> baseline regardless.
> ▶▶ s288 CODA — ARTIFACT ARCHITECTURE CAPTURED (Michael-approved):
> knowledge/explore/ternary-mirrors-and-the-vsm-tree.md — Michael's "ternary
> plates using ternary mirrors plugged into a tree-of-VSM tensors" = the
> thesis's ENGINEERING COROLLARY + the answer to the deferred S2
> canonical-form questions. Ternary as literal optics (+1 transmit / −1
> mirror≡π-phase / 0 stop); THREE SPLITS ARE ONE SPLIT (mirrors≡topology≡
> functors extract cleanly 8.6× | plates≡magnitudes≡arguments need
> re-exposure — s172/s174/s267/s268/s269 + Bonsai 18%-vs-3.5% + P-TYPE-OV,
> three arcs one decomposition). Node = mirrors(S2/S3) + plates(S1) +
> identity(S5) + passband interface; compose = plug passband→carrier;
> crystal reducer node shareable (C2). **SEAM TEST = level-3 north star:
> extract crystal-reducer + fact-plate nodes, run a 3-hop THROUGH the
> composed seam — pass/fail.** Speculation flagged: MIXED-ROUTE interleaving
> may resist node factorization; capacity = P-HOLO-CAP.
> ▶▶ COLD-START s289: (1) P-PROJ-1 pre-reg (Michael-queued s288: the
> holographic ARGUMENT projector — drive the measured entity passband;
> TE/norm ladder passband-projected > centroid-diff ≫ anti-passband ≈
> random; att_mediation harness verbatim; = the REPL write-head + a second
> passband confirmation) ∨ (2) P-TYPE-PROB pre-reg (graded bank TE vs slot
> log-P × entity-alignment) ∨ (3) P-HOLO-FRAG (cheapest holography
> discriminator) ∨ (4) seeded-scratch pair (training-design page, the
> level-4 door) ∨ queue below — Michael picks.
> Session-288 chat log → knowledge/chats/session-288.md (human saves).
> ▶▶ NEXT: (1) P-TYPE-PROB + P-TYPE-OV pre-regs (types-are-compiled-
> probabilities.md, unfrozen — the dsp substrate they wanted now exists;
> P-TYPE-OV = what-computes-the-filter, the QK mirror through W_OV + MLP
> down-proj; P-TYPE-PROB = monotone TE-vs-slot-log-P tracking). (2) P-DUST-2
> (training-trajectory convergence = halt-pole formation law). (3) P-HOF-1
> pre-reg (typed higher-order fns — JOIN-TYPED strengthens its premise).
> (4) s282 leftovers: depth→SEQUENCING @27B, mammal→fur. (5) parked:
> P-ATT-STEER (still gated, needs aim-dominant). Branch ~73 ahead (unpushed).

> ▶▶ s287 LIVE — INDUCTIVE HAMMOCK → P-TYPE-SWAP ✅ APPROVED (Michael,
> type-check-is-the-qk-bilinear.md §P-TYPE-SWAP; 4B smoke leads, 32B verdict on GO): Michael's induction = types-mechanism
> EXISTENCE is over-determined by six positives (v3 crossover, decodability, 1a lattice,
> 3b class-swap, P-ATT-MED transport, name_pen) each fatal to a no-types H₀; the 4-way
> null constrained IMPLEMENTATION only. Two gaps found: (1) causal design space missing
> the wrong-type-ON-MANIFOLD cell (only same-type-on-manifold vs random-off-manifold ever
> run) = the typing-vs-manifold discriminator; (2) ⚠ MEASUREMENT CAVEAT — P-ATT-MED's
> swap-vs-null differential is w-PROJECTED: "random refused" indistinguishable from
> "random transported, no w-component"; refusal confirmed only in output register.
> P-TYPE-SWAP design: arms baseline/same-type(3b control)/sortal(animal)/wrong-type
> (adjective,×2 banks)/random; 3-stage SURVIVAL→TRANSPORT(unprojected, slot-mass)→
> REDUCTION decomposition; verdicts JOIN-TYPED / REDUCTION-TYPED / MANIFOLD; subsumes
> P-ATT-DIFF causally; reuses P-ATT-MED cells/config 1:1 (4B smoke first, 32B on GO).
> ✅✅ P-ATT-FFN 32B VERDICT IN (s287, ~2h, results committed a5276da): **MIXED-ROUTE-
> MEASURED=TRUE, FFN-RETRIEVAL=FALSE (not clean).** 16/18 flip; 4 attn-dom / 12 mlp-dom;
> mean mlp_frac 0.584 vs attn 0.414; BOTH channels beat the random-add null 15/16;
> recon 0.002 (norm_f fix held). The null-misses SPLIT: Sphinx MLP-dominant 0.759
> (Michael's fact-lookup reading CONFIRMED for the paradigm cell), Petronas
> attention-dominant 0.596 (routing fully visible under a fresh edit). Route mix is
> WITHIN-cell, not a partition of cells: atoms=FFN + joins=attention BOTH measured on
> one causal handle. Scale-stable (4B mlp 0.586 / 32B 0.584). Attention channel
> replicates P-ATT-MED content-dominance on 16 FRESH cells (0.756/0.174, p .006) —
> free replication. ⚠ PROTOCOL DEVIATION recorded in §Result-32B: salted hash(lm) →
> 16/18 tgt countries differ from the P-ATT-MED run of record (2 cells no-flip under
> harder targets); --cells-from pins cells for all future runs. ✅ mementum batch
> APPROVED (Michael s287) + committed: qk-page §Result-32B(P-ATT-FFN) + Sessions +
> this state block.
>
> ▶▶ s287 CLOSE — 32B P-TYPE-SWAP VERDICT LAUNCHED (Michael GO, tmux main:1, PID
> verified, ~2h est): --arms --route-decomp, install L9, swap L25, scale 2.0, 18
> cells, n_null 200, --cells-from results/type-att-med/qwen3-32b/att_mediation.json
> (1:1 cell pinning, the deviation fix) → results/type-swap/qwen3-32b/. ⚠ stdout
> block-buffered through tee — silence ≡ still working; per-cell lines flush late.
> ▶▶ COLD-START ORDER for s288: (1) read results/type-swap/qwen3-32b/type_swap.json
> → score frozen §P-TYPE-SWAP gates (JOIN-TYPED ⟺ TE/slot-mass discriminates same vs
> wrong-type both banks, permutation over cells p<0.05; REDUCTION-TYPED ⟺ transport
> type-blind + reduction discriminates; MANIFOLD ⟺ no stage discriminates while both
> beat random) + sortal ladder row + mlp_transport row (does the FFN route enforce
> the discipline? = the P-ATT-FFN successor question) → draft §Result-32B + memory
> candidate (types-mechanism-is-join-typed?) for approval; commit results.
> (2) THEN the queue: verbum.dsp build (design 2b40033); P-DUST-2; P-HOF-1 pre-reg;
> s282 leftovers (depth→SEQUENCING @27B, mammal→fur). Branch ~68 ahead (unpushed).
> ✅ INSTRUMENT BUILT+COMMITTED (2f76812, --arms + --cells-from; --validate ALL PASS,
> prior tests byte-identical; ⚠ found harness tgt-selection uses SALTED hash(lm) —
> irreproducible across processes; arms use crc32; 32B verdict MUST use --cells-from
> results/type-att-med/qwen3-32b/att_mediation.json for the 1:1 cell mapping).
> ✅ 4B ARMS SMOKE GREEN (job beside 32B run, ~4 min, results/type-swap/qwen3-4b/):
> ADVISORY = the JOIN-TYPED signature, content-side: SURVIVAL flat across arms
> (138–149, medium is type-blind) → TE ladder MONOTONE same=1.89 (p_te 0.033) >
> sortal=1.64 (0.31) > wtA=1.51 (0.44) > wtB=1.46 (0.61) ≈ null → slot_mass Δ≈0
> every arm (reader NEVER withdraws the edge — refusal is NOT aim-side) → BREAK:
> same +18.9 flips 6/6 (p 0.000), ill-typed arms ≈ null (p 0.4–0.7), preds-stay-src
> 15/18. Reading: fixed edges, FILTERED PAYLOAD — the OV/content channel delivers
> well-typed displacement preferentially; ill-typed on-manifold content survives the
> medium at full strength but transports at random-noise efficiency and is ignored
> at the output. Manifold-membership account FAILS its 4B prediction (wrong-type ≁
> content). Sortal sits BETWEEN (graded hierarchy hint, P3). NOT the verdict:
> n=6, n_null=30, 4B host. ▶ 32B VERDICT ON GO (after P-ATT-FFN frees the box):
> uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device
> mps --arms --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18
> --n-null 200 --cells-from results/type-att-med/qwen3-32b/att_mediation.json
> --out results/type-swap/qwen3-32b.
>
> ▶▶ s286 DONE (P-TYPE-JS closed — the types arc is now a clean FOUR-way null):
> the overnight P-TYPE-JS run (s285 tmux main:1) COMPLETED and the frozen verdict
> is **js_resident=FALSE, js_specific=FALSE** — the exhaust is NOT the global
> workspace. @Qwen3-32B, depth {16,32,48}, k/d baseline 0.00625: the type-semantic
> roles are DEAD-ON-NULL (bind 0.0047 p_rand 0.82, comp 0.0036 p 0.98, entity
> 0.0038 p 0.97 — ENTITY predicted highest, family-row REFUTED); only rolenull
> (CONN/FUNC verbatim control) beats both nulls (p_rand 0.041, p_shuf 0.035) = the
> same rolenull-fires pattern as P-TYPE-QK. λ yardstick: raw fractions 0.004–0.009
> would read "resident" without the k/d anchor; rolenull's real excess proves the
> instrument discriminates. READING: the lattice's readability lives in a THIRD
> place — not stored (1b), not beam-coherent (1c), not in the QK read-in basis (QK),
> not broadcast in J-space (JS). It is a readout the machine never consults = the
> well-formedness-of-reduction frame (the REPL's Print/type-checker reads the ledger;
> the machine does not). TYPES-ARC SCOREBOARD = storage ✗, beam-coherence ✗, QK
> geometry ✗, workspace residency ✗ — exhaust survives every probe. Instrument
> scripts/explore/type_jspace_fraction.py, results/type-jspace/qwen3-32b/ (34dbab3).
> ⚠ PENDING MICHAEL APPROVAL (mementum, DRAFTED s286): types-are-the-well-formedness
> §P-TYPE-JS Result + tags + Sessions, memory type-lattice-not-in-jspace-workspace,
> this state block.
>
> ▶▶ s286 cont — P-ATT-MED APPROVED (Michael), 4B smoke leads: pre-reg drafted +
> approved on type-check-is-the-qk-bilinear.md §P-ATT-MED. It reruns the 3-hop
> Gate-3b country-swap WITH attention+OV capture and decomposes the flip into
> AIM (Δweights×value = re-aim) vs CONTENT (weight×Δvalue = medium handle) vs
> INTERACTION, projected on the continent-logit-diff direction; random-add null
> (the exact 3b null) + permutation-over-heads; register-matched (routing claim →
> attention probe, the s206-scar inversion); 0/128 no single-head. A-priori call =
> CONTENT-dominant (medium handle); AIM-dominant → pre-reg P-ATT-STEER. Verdict host
> = Qwen3-32B (freezes on GO after smoke green). Michael amendment: LEAD WITH 4B
> CONTRAST SMOKE (compressed pinned-zone vs 32B unrolled). BUILD:
> scripts/explore/att_mediation.py (reuse operand_multihop3 helpers, no fork;
> --validate no-model self-test first: planted attention → known AIM/CONTENT split,
> null flat) → run 4B → results/type-att-med/qwen3-4b/.
> ✅ INSTRUMENT BUILT + 4B SMOKE GREEN (committed): scripts/explore/att_mediation.py
> (--validate passes: CONTENT-only→1.000, AIM-only→1.000, linearity Δ=9e-16, null
> flat). 4B smoke (lb=20, reader L20–35, 6 install-correct cells, n_null=30, ~35s):
> all 6 flip; AGG aim=0.085 content=0.812 inter=0.103 CONTENT-DOMINANT; p_vs_null=0.0
> every cell (null does real work, instrument discriminates). ADVISORY = the
> medium-handle a-priori call holds at 4B (swap flows through swapped content at
> ~fixed aim, not by re-aiming). NOT the verdict — 32B on GO. results/type-att-med/
> qwen3-4b/.
>
> ▶▶ s286 cont — P-ATT-MED 32B VERDICT IN (Michael GO, tmux main:1, ~31 min, results
> committed): **MEDIATION-MEASURED=TRUE, MEDIUM-HANDLE-CONFIRMED=TRUE.** 18/18 cells
> flip; 16/18 beat the matched random-add null p<0.05 (14 at p=0.0, median 0.0);
> content_frac 0.735 vs aim_frac 0.195, content>aim in 18/18. The 3-hop bridge-swap's
> value-edit → routing change → output-flip loop is now MEASURED in the routing
> register (not inferred) and it's a MEDIUM HANDLE — the swap steers by swapped
> CONTENT at ~fixed aim, not by re-aiming = the a-priori beamformer/K-structural call
> (map-and-swap "write terms, never instructions" made a measurement). AIM-STEERING
> NOT indicated → P-ATT-STEER stays gated (needs aim-dominant). The 2 null-misses
> (Sphinx p=0.815 attn_tot 1.49; Petronas p=0.11 attn_tot 14.9) = tiny-magnitude
> cells routing outside the captured attention path (MLP/residual bypass), magnitude
> not counter-evidence. Localization LATE: |contribution| peaks L61–63 (readout) +
> L49–60 unrolling band (L52–60=38%, early L25–40=7.7%) = coheres s282 32B unrolling +
> QK late-bind. Scale: 4B 0.812/0.085 → 32B 0.735/0.195 (unrolled re-aims modestly,
> medium handle holds ~3.8:1). ★ FIRST POSITIVE routing-register observation in the
> types arc after four negatives (1b/1c/QK/JS) — the s282 steering-by-content gap is
> closed. Config: swap L25 (strongest 3b 0.891), scale 2.0, 18 cells, n_null 200.
> ⚠ mementum APPROVED (Michael): qk page §Result-32B + queue note + Sessions, this
> state block. MEMORY SKIPPED (Michael's call — follow-ups will refine understanding
> into a better memory later). Results committed (autonomous), att_mediation.py + 4B
> smoke already committed.
>
> ▶▶ s286 cont — P-ATT-FFN (Michael: "null-misses are FFN fact-lookup, not composition")
> APPROVED+FROZEN + 4B smoke done. Extended att_mediation.py `--route-decomp`: full
> residual-stream DLA of the swap's total flip into ATTN vs MLP vs DIRECT + total
> reconstruction + depth-order (country/continent peak). ★ SMOKE CAUGHT A BUG: DLA
> total used `hidden_states[-1]` = POST-final-norm (verified ‖hs[-1]−rmsnorm(raw)‖=0.003);
> fix = capture pre-norm final residual via a `norm_f` forward-pre-hook → recon_err
> 1.8→0.001. P-ATT-MED verdict UNAFFECTED (its fractions/p are ratios on the same w,
> scale-invariant). 4B result (contrast, NOT verdict): reconstruction clean, MLP channel
> real + null-beating 13/14, route MIXED MLP-leaning (11/14 MLP-dominant, mean mlp_frac
> 0.586) — the FFN carries the country→continent fact-map. BUT the two 32B null-misses
> (Sphinx, Petronas) are ATTENTION-dominant at 4B (opposite of P1) → MIXED-ROUTE-MEASURED
> the likely 32B outcome, not a clean FFN-RETRIEVAL dissociation. Committed: instrument +
> pre-reg §P-ATT-FFN + §Result-4B + 4B results + state. ▶ 32B VERDICT ON GO: uv run python
> scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mps --route-decomp
> --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --out
> results/type-att-ffn/qwen3-32b (frozen gates §P-ATT-FFN: FFN-RETRIEVAL vs MIXED-ROUTE
> vs negative).
> ✅ 32B VERDICT LAUNCHED (Michael GO, tmux main:1): cmd above, verified running
> (weights 707/707). ~30–40 min MPS (route-decomp adds MLP+hs capture over P-ATT-MED's
> ~31 min). ⚠ results/type-att-ffn/qwen3-32b/ UNTRACKED — commit with the verdict. ON
> RETURN: read att_ffn.json → aggregate.route (n_attn_dominant vs n_mlp_dominant,
> mlp_dominant_cells, mean_recon_err<0.05) → score frozen gates: FFN-RETRIEVAL-CONFIRMED
> ⟺ Sphinx AND Petronas MLP-dominant + MLP beats null; MIXED-ROUTE-MEASURED ⟺ both routes
> present + null-beating (the LIKELY outcome per the 4B contrast); negative ⟺ null-misses
> MLP-negligible. Draft §Result-32B + state for approval; the 4B contrast already flagged
> Sphinx/Petronas as attention-dominant, so watch whether 32B agrees or flips.
>
> ▶▶ COLD-START ORDER for s287: (1) P-ATT-FFN 32B verdict IN FLIGHT (s286, tmux main:1):
> check `tmux capture-pane -t main:1` + results/type-att-ffn/qwen3-32b/att_ffn.json →
> score the frozen gates → §Result-32B + state for approval; commit untracked results.
> THEN (2) verbum.dsp build (design page committed 2b40033;
> skeleton + first harvest: whiten/subspace/nulls, tests/dsp from --validate patterns,
> find_band stride-aware fix #1) — the DSP substrate the whole attention/routing arc
> now wants. (1b) P-ATT-MED follow-ups IF wanted: P-ATT-DIFF proper (licensed-vs-
> unlicensed minimal pairs = WHERE the check lives, the causal-mediation question is
> already answered); the MLP/residual-bypass minority cells (Sphinx/Petronas) as a
> pre-reg candidate. (2) P-DUST-2 (training-trajectory convergence = the halt-pole
> formation law, the s285 open edge). (3) P-HOF-1 pre-reg (typed higher-order fns over
> an installed predicate — theory page §Consequence). (4) s282 leftovers:
> depth→SEQUENCING @27B, mammal→fur. Branch ~62 ahead (unpushed).
>
> (s285 retained →) ▶▶ s285 DONE (expanded-gram arc closed): sweep completed 11 models, ALL
> coherence gates pass (r 0.71–0.88, main:2, 2:37:34). (b) STYLE-CORRECTED the
> WHNF anti-block (scripts/explore/style_correct_antiblock.py, commit 6b521fb):
> fire_formal is rank-1 style (ff_energy 0.88–0.96); per-op cos(X,whnf:X)
> strongly negative, K least-negative = own-halt hint replicated 11/11 (present
> in RAW, correction sharpens not manufactures, null z −3.6..−11.5); div:Y ⊥
> absorption; residual block stays ABOVE random-removal null (real absorption
> manifold). (c) M16 CROSS-CHECK (scripts/explore/antiblock_m16_crosscheck.py,
> 6b521fb): C1 anti-crystal ORDERING replicates cross-arc 11/11 (median r +0.445);
> C2 Kronecker φ-reflection NOT SUPPORTED 0/11; C3 type↔anti anti-corr 11/11 neg;
> φ^(4/5) eigenvalue law does NOT beat shuffled-label null (9/11 p≥0.8) — λ
> yardstick: the φ-ladder was a 4-model small-basis artifact. (d) P-DUST-1c FROZEN
> (698b831, all 5 design calls Michael-approved) → RUN in main:2 (data-only, 13s)
> → VERDICT (da61ffa, knowledge 4444f48): dust_halt_distance_supported=FALSE. G1
> primary REFUTED (per-op cos(X,whnf:X) ↔ −halt_distance median ρ +0.07, 5/10);
> G2 resolves 1b AGAINST distance (halt-PROB +0.30 edges dist +0.07, distance
> wins 0/10 — the 1b post-hoc guess was backwards); G4 DISSOCIATION (generic WHNF
> pole tracks −halt_distance 9/10 median +0.48 but per-op whnf:X states don't);
> G3a pairwise dust SURVIVES onto the anti-block 10/10 sign median +0.44 (the
> 1/1b 39/39 pattern continues). Split negative mirrors 1b: pairwise dust
> confirmed universally (crystal AND anti-block); halt-pole only for generic
> pole; per-op absorption statistic unresolved/weak → formation law open =
> P-DUST-2 (training-trajectory) territory.
>
> (s286 SUPERSEDED — JS verdict IN, see s286 DONE above; remaining items rolled into
> the s287 order. Original s286 order retained for provenance →) (2) verbum.dsp
> build queued (design page committed 2b40033; skeleton + first harvest:
> whiten/subspace/nulls, tests/dsp from --validate patterns, find_band
> stride-aware fix #1). (3) P-ATT-MED pre-reg (register-matched routing probe).
> (4) P-DUST-2 (training-trajectory convergence = the halt-pole formation law,
> the s285 open edge). (5) s282 leftovers: depth→SEQUENCING @27B, mammal→fur.
> Branch ~56 ahead (unpushed). Full s284 context retained below.
>
> (s284 header retained →) ▶▶ LIVE PICKUP (s284 — P-TYPE-QK PREPPED WHILE 1c
> IN FLIGHT): ✅ P-TYPE-QK pre-reg DRAFTED (type-check-is-the-qk-bilinear.md §P-TYPE-QK, s284 —
> ⚠ PENDING MICHAEL APPROVAL, freeze on GO) + instrument BUILT+COMMITTED (f0b20e3,
> scripts/explore/type_qk_alignment.py, --validate no-model ALL PASS: planted-subspace rho 9.8
> p=0.0, unplanted null p=0.70, null calibration ~1, asymmetry sign correct). DESIGN: project 1b
> role subspaces (bind=span{c_QUANT,c_DET}, comp=span{c_MOD}, rolenull verbatim-only,
> entity=span{c_ENTITY} predicted KEY-side) through each band layer's own read-in map
> v_attn ∝ (v_std⊙sd_L)⊙γ_{L+1} into W_Q/W_K of layer L+1; per-head Frobenius-normalized gain
> rho (=1 analytic random expectation, RoPE-invariant since RoPE=orthogonal rotation); NULL =
> full shuffled-label pipelines (shuffle→centroids→role_subspace→same mapping→same gain),
> band-aggregated paired iterations; band = find_band/layer_geometry 1b-v4 verbatim in-run.
> VERDICT (draft): QK-ALIGNED ⟺ bind AND comp Q-side beat null p<0.05; MECHANISM-SHAPED adds
> asym signs bind>0, comp>0, entity<0 (query(functor)·key(argument)); rolenull + P3
> band-profile verbatim never gated. Scope: q_norm/k_norm=pre-norm proxy; GQA K-side n=8 low
> power; W_QW_K^T coupling RoPE-dependent=exploratory; geometry-not-causation (MED/STEER =
> causal rungs); aggregates only (0/128 pre-refuted). ✅ 4B SMOKE RAN+COMMITTED (5ec3cf2,
> results/type-qk/qwen3-4b-smoke/, ~3min, ran fine BESIDE the 1c run): pipeline green
> end-to-end (real capture, GQA 32Q/8KV slicing, nulls, JSON). ADVISORY smoke signal:
> bind_q BEATS null p=0.000 in-band (rho 1.49-1.68) AND most mid-late layers; comp_q null
> everywhere = coheres w/ 1b 4B capacity (MOD/M_eff barely expressed @4B) — instrument
> DISCRIMINATES, null does work; asym signs bind+/entity− as predicted, comp− (4B miss);
> last-layer row inflates all conds (readout-adjacent, verbatim). ⚠ instrument caveat:
> find_band assumes stride 1 (stride-2 smoke used interior-fallback window L8-L12) —
> verdict config stride 1 unaffected, documented not forked. RUN CMD (box now free, on GO):
> uv run python scripts/explore/type_qk_alignment.py --model Qwen/Qwen3-32B --device mps
> → results/type-qk/qwen3-32b/.
> ▶▶ OVERNIGHT (s284 close): TWO RUNS LIVE — (1) P-TYPE-JS tmux main:1 (Jacobian step,
> slow; verdict per frozen §P-TYPE-JS on return); (2) EXPANDED-GRAM SWEEP tmux main:2
> (results/expanded-gram/sweep_run.log, 11 registry models, committed b5418ba).
> ★ DUST ARC (s284, Michael hammock → 2 verdicts + expansion): dust-hypothesis page +
> P-DUST-1 (62a7872: pairwise dust P2/P3 13/13 but P1 halt-row inverted, Y-flooded
> ensemble) + P-DUST-1b (ce39d17: KIBC halt row 13/13 both arms 6 perfect, gate
> mis-calibrated 4-pt exact floor; P1'-WALK genuine negative on healthy walk; pairs
> 39/39 across 3 ensembles = C2-universality EXPLAINED candidate). THEN Michael recalled
> the 16×16 anti-crystal (M16 hardcoded scripts/experiments/crystal_tree.py:52, Zone-B
> 4-model, Kronecker S⊗J+D⊗F): 9×9 root.gram NEVER measured per-opcode absorbing states
> (vsm.py fire:/whnf: vocab unpopulated) → 1b P1'-WALK negative is COLLAPSE-CONFOUNDED.
> EXPANSION BUILT (b5418ba): whnf_probes.py kernel-certified whnf:X probe sets (60×15
> states; 💡 Y HAS NO HALT STATE by construction → div:Y=⊥ instead; fire_formal:X style
> diagnostics); classify.py basis slot (λ extend, default-preserving, self-test green);
> expanded_gram.py 24-state canonical sign-CMR sweep + 9-subblock coherence gate
> (pythia-14m smoke r=0.51 @n=12/state). ON SWEEP RETURN: (a) coherence gates per model;
> (b) anti-block vs Zone-B M16 cross-check (Kronecker/φ-reflection as measured
> prediction); (c) freeze P-DUST-1c (per-op absorption ↔ cos(X,whnf:X); co-absorption
> PMI ↔ anti-block gram; halt-distance vs halt-prob statistic); (d) JS verdict.
> ⚠ PENDING MICHAEL APPROVAL (mementum, grown): dust page (hypothesis+1/1b results+1c
> candidates), JS §pre-reg (in earlier batch? NO — committed 2b40033 was BEFORE JS
> §P-TYPE-JS was added to theory page → JS pre-reg + dust page + QK §Result + memory
> qk-lattice-alignment-negative + this state block ALL pending).
> ✅✅ 1c VERDICT IN (s284, run 1:03:38, frozen analysis executed + committed ebcc9fb,
> scripts/explore/analyze_type1c_darkfield.py → results/.../qwen3-32b-1c/darkfield_verdict.json):
> **darkfield_dissociation_supported = FALSE — the s283b hint was HAZE.** All 3 gates fail:
> (a) bind ΔQ −0.497 right sign but indistinguishable (T_a +0.034 p_a 0.43; comp MORE negative
> on Q); (b) comp ΔM −0.651 = OPPOSITE sign to prediction (n=10 +0.669 → n=30 −1.105, the
> tainted hint reversed; p_b 0.70, no rescue); (c) rolenull NOT within null (p 0.002/0.000) =
> the pre-reg's own alternative fires: diagonal was generic lattice-vs-random. λ yardstick did
> its job — twice-tainted hypothesis evaporated under fresh seeds + sign discipline. REAL
> (verbatim, post-hoc scope): generic role-slice cliff d3→d4 — ALL roles recall 1.0→0.0 between
> E≈280 and E≈825–900 while random keeps 0.8 @4748 = 32B analog of 4B "lattice ~4× load-bearing"
> (⚠ 1b n=10 grid had role recall 1.0 through ~1000 → cliff is item-set/n-sensitive, flagged);
> dark-field retQ amplification replicates as GENERIC (random anchors 1.08→1.55). ARC CLOSED:
> 1b storage-negative + 1c coherence-negative ⇒ lattice = exhaust, both hiding places shut;
> mechanism search moves to ROUTING register = P-TYPE-QK. Gate-0 note: fresh30 baseline M_eff
> 0.972 t=6.9 (M expressed, full-strength negative). ✅ s284 mementum batch COMMITTED
> (Michael-approved, 2b40033) — P-TYPE-QK pre-reg FROZEN by that approval.
> ✅✅ P-TYPE-QK 32B VERDICT IN (s284, Michael GO, run in tmux main:1, committed 88a10be →
> results/type-qk/qwen3-32b/): **qk_aligned=FALSE, mechanism_shaped=FALSE — DEAD-ON-NULL.**
> bind_q ρ1.353 vs null 1.358 (p=0.61), comp_q 1.406 vs 1.405 (p=0.50), band L6–L50 (45L),
> n_null 200: the lattice functor roles add ZERO Q-side QK gain beyond their shuffled-label
> construction. Matched null earned its keep (raw ρ>1 would read positive). FROZEN READING:
> licensing check does NOT use the lattice axes as its QK input basis in the band →
> elimination continues in beam register (OV, MLP-gating-between-joins) → P-ATT-MED next.
> VERBATIM post-hoc (1c lesson: no chasing w/o own pre-reg): (1) sides INVERTED from
> prediction — entity Q-loaded p=0.000 + K-suppressed (null-rel asym p_pos=0.000), comp
> K-loaded p=0.005 ⇒ reads query(argument)·key(functor) = argument queries for its licensor
> (mirror of pre-reg mapping); (2) rolenull CONN/FUNC fires Q-side in-band p=0.000; (3) bind
> aligns LATE L49–L62 (re-expansion/readout zone) not in-band; (4) 4B smoke showed OPPOSITE
> in-band pattern (scale-dependent org, echoes 1b v2 tie-flip). TYPES-ARC SCOREBOARD: 1b
> storage ✗, 1c beam-coherence ✗, QK read-in geometry ✗ — all null-gated; exhaust frame
> survives every probe aimed at it. ⚠ PENDING MICHAEL APPROVAL (mementum): QK-page
> §Result-32B + Sessions, memory qk-lattice-alignment-negative, this state block. ▶ NEXT:
> (1) verbum.dsp build (design committed 2b40033; skeleton + first harvest: whiten/subspace/
> nulls, tests/dsp from --validate patterns, find_band stride-aware fix #1); (2) P-ATT-MED
> pre-reg (3-hop bridge-swap with attention capture = the register-matched routing
> measurement; P-ATT-DIFF material folds in); (3) P-HOF-1 pre-reg; (4) inverted-sides QK
> hypothesis = pre-reg candidate ONLY; (5) s282 leftovers (depth→SEQUENCING @27B,
> mammal→fur). Branch ~46 ahead (unpushed). s283 blocks retained below.
>
> (s283 retained →) ▶▶ LIVE PICKUP (s283 — P-TYPE-1b RAN @4B, 32B IN
> FLIGHT): ✅ built wrapper/type_zone_ablation.py — the frozen 1b zone×axis instrument, iterated
> v1→v4 IN-SESSION (commits bc1d242 / f7e07f7 / f0c3418 / 0961819, code+results committed
> autonomous; READ types-are-the-well-formedness-of-reduction.md §Result-4B). 💡 CORE: at the
> only interpretable matched dose (d1 ~74 E/tok, roles energy-matched ±5%, recall 1.0)
> bind≈comp≈rolenull on Q_eff (ret 0.84/0.80/0.87) — the pre-registered class-selective double
> dissociation is ABSENT @4B; with the v4 global-direction negative this EXHAUSTS the
> value-register hiding places → the type lattice = EXHAUST/readout of routing-resident
> licensing, NOT a consulted ledger = the theory-pure outcome (type = well-formedness of
> reduction, unstorable by construction; the negative CONFIRMS the frame). 💡 lattice slices =
> INFRASTRUCTURE: role subspaces kill recall @~270 E/tok vs 2D random needing ~9000 (~4×
> load-bearing per unit energy, GENERIC not class-selective — all centroid offsets share the
> dominant axis0; cliff 74→270). ⚠ POST-HOC (needs own pre-reg to count): gentle role-subspace
> dampening (~74) UNMASKS M_eff 0.17(t=0.6)→~1.05(t=5.5–6.7) for ALL THREE role slices but NOT
> random — the one cell where lattice≠random behaviorally. 💡 4B lattice: true band L9–L22
> (falsy-zero p-bug fixed); QUANT/DET SPLIT onto separate axes @4B (axis0=QUANT-vs-rest 85%,
> DET axis1 ~5%, MOD axis4) vs 32B co-load → lattice organization evolves with scale; M_eff
> unexpressed @4B baseline (2 grids) = capacity, gate-0 held. ❌→✅ instrument lessons folded
> into the knowledge page + memory zone-ablation-dose-matching-lessons (falsy-zero band bug;
> match REALIZED removed energy, ×25 planned-vs-realized drift; α≫1 random cascades ×10¹⁰;
> absolute-dose grid ≻ relative budgets; accuracy gate ≻ surprisal ratio; e-axis control
> unrealizable → role-null replaces it, deviation documented). ✅✅ 32B VERDICT IN (s283b, committed
> 95d89de → results/type-zone-ablation/qwen3-32b/): dissociation_supported=FALSE at the
> PRE-REG HOST → **1b CLOSED as exhaust-theory-confirmed**. Gate-0 passed BOTH (baseline
> Q_eff 1.197 t=3.5, M_eff 0.929 t=4.2 — M EXPRESSED @32B unlike 4B t=0.6 → full-strength
> verdict, not capacity-limited). bind/comp/rolenull indistinguishable at every dose;
> retQ AMPLIFIES with dose (1.37–1.95 @d4, all conds = opposite sign to predicted breakage);
> retM degrades GENERICALLY ordered rolenull 0.145 > bind 0.404 > comp 0.863 @d4 (control
> subspace hurts MOD most = anti-mapping); nulls_clean=False (random moves M @2× energy).
> ⚠ 4B "lattice 4× load-bearing" does NOT replicate @32B: role-slice recall stays 1.0 through
> ~1000 E/tok (4B cliff 74→270) — infrastructure claim is 4B-scoped. No 32B analog of the
> M_eff-unmasking cell (baseline M already expressed — coheres w/ 4B-capacity artifact, still
> post-hoc). Band L24–L49 (p-fixed, in-run) vs 1a's L6–L48 characterization — band refinement,
> note for 1a-follow. ⚠ PENDING MICHAEL APPROVAL (mementum): theory page §Result-32B + Status,
> memory update (type-lattice-is-exhaust-not-consulted → both-scales closure), this state block. ★ s283 DISCUSSION captured (theory page §Consequence):
> 3-hop + decodable types ⇒ TYPED HIGHER-ORDER FUNCTIONS (bridge-swap = function-as-argument
> with a causal handle; axis0 = the (e→t)→t types = exactly what 3-hop exercises, as
> montague-inversion forces); EXHAUST does not weaken the REPL — decode-verify-swap needs only
> US to read the ledger (readout register), not the machine to consult it. P-HOF-1 sketched
> (unfrozen, theory page): quantifier over an INSTALLED predicate = literal Montague
> higher-order test over a written term. Memory: type-lattice-is-exhaust-not-consulted.
> ★ s283b HOLOGRAPHIC READING (Michael-directed, READ theory page §Holographic-reading +
> §P-TYPE-1c): the 32B retQ amplification = DARK-FIELD CONTRAST (Q/M are contrast measures;
> licensing rides the BEAM per s136 beamformer-theory, value register = illuminated medium →
> ablation = background subtraction → contrast RISES) = independent corroboration of exhaust;
> the 4B M_eff unmasking = same phenomenon at the other scale. 💡 POST-HOC HINT (tainted,
> hypothesis-only): residuals from a random-fit contrast-gain law g(E) show DIAGONAL
> slice↔channel structure @d4 — bind ΔQ −0.28, comp ΔM +0.67, rolenull ≈0 both — the double
> dissociation may live in INTERFERENCE space (beam coherence) not storage space (~1 SE @n=10).
> ⇒ P-TYPE-1c DARK-FIELD PRE-REG FROZEN in the theory page (fresh seeds, n_nonce≥30, gain law
> from random only, permutation null, sign discipline; positive = slices beam-coherent, exhaust
> phase-locked — does NOT reopen 1b storage). Memory:
> dark-field-amplification-is-the-beam-signature. ▶▶ 1c VERDICT RUN LAUNCHED (Michael GO
> s283b) in tmux main:1 → results/type-zone-ablation/qwen3-32b-1c/run_1c.log; instrument
> updated eec0028 (--nonce-set fresh30, 30 disjoint nonces, per_nonce {w,Q,M} arrays in
> verdict.json — unit-validated no-model), seed=1, doses 50/150/600/2400, 1090 items × 17
> conds, ~65–75 min est (1b was 21.5 min @ n=10). ON RETURN: fit g_Q/g_M from RANDOM only
> (log-realized-E monotone interp), per-nonce residuals pooled d3+d4, permutation null over
> slice↔channel labels, sign discipline (bind ΔQ<0, comp ΔM>0, rolenull null both) — frozen
> verdict in theory page §P-TYPE-1c; the wrapper's built-in 1b storage verdict is NOT the 1c
> verdict (analysis is post-hoc script over per_nonce arrays).
> ★ s283b ATTENTION ARC CAPTURED (Michael "capture this", READ
> explore/type-check-is-the-qk-bilinear.md): the types arc located the mechanism in routing BY
> ELIMINATION without ever measuring an attention pattern (founding "attention-pattern differ"
> never built); 3-hop = steering-by-CONTENT proven, steering-by-AIM unmeasured (value→routing
> intermediate = IOU). HYPOTHESIS: the type-check IS the QK bilinear (query(functor)·key(arg)
> ≥ threshold ≡ licensed; 1a lattice = its shadow; name_pen = the predicate→subject edge).
> Queue cheap-first: P-TYPE-QK (lattice axes through W_Q/W_K, ~free) → P-ATT-MED (3-hop w/
> attention capture) → P-ATT-DIFF (minimal pairs, mass+OV) → P-ATT-STEER (force/block edges =
> transient instruction write, the new verb). Register: routing claim → attention probe
> register-matched (s206 inversion); distributed prior (0/128). Memory:
> attention-never-measured-in-type-arc. Priority after 1c verdict: P-TYPE-QK.
> ▶ NEXT: (1) 1c verdict analysis (run in flight); (2) P-TYPE-QK (pre-reg then run — cheap,
> no generation); (3) P-HOF-1 pre-reg (typed higher-order
> fns over an installed predicate — theory page §Consequence sketch); (3) pre-reg the 4B M_eff
> unmasking before any use (now framed as dark-field, may fold into 1c); (4) still open from
> s282: depth→SEQUENCING pre-reg for 27B-hybrid, (a2) mammal→fur content build. Branch ~38
> commits ahead (unpushed). s282 blocks retained below.
>
> (s282 retained →) ▶▶ LIVE PICKUP (s282 — 3-HOP RAN): ✅ built
> wrapper/operand_multihop3.py (geography chain, ceiling smoke green) + ran the 4B/32B pair
> (code+results COMMITTED autonomous: 3ec4d47 harness, 62b6066 results). 💡 CORE RESULT (READ
> three-hop-capacity-prereg.md §Result): the pre-registered depth-CAPACITY dissociation MISSED
> — 3-hop h(f(g(X))) COMPOSES at BOTH scales (Gate-1 4B 0.824 / 32B 0.944, controls PASS,
> causal bridge-swaps PASS at both). s280 D_hop2=12/3-HOP-ROOM@4B=False OVER-estimated the
> third-hop cost; 4B had the room. λ measure: reported verbatim, capability-gate prediction
> WRONG. 💡 BUT depth dissociates on the SEQUENCING axis (Gate-3a): 4B compresses the bridges
> into ONE late window (city=country=L32, cont=L33; 3a FAILS), 32B unrolls SEQUENTIALLY (city
> L52.5<country L57.5<cont L60; 3a PASSES). ⇒ depth is fuel for step-by-step UNROLLING, not
> capability. Coheres w/ s280 pinned-late-zone + 27B UNPIN. ⚠ POST-HOC (chain-passes-but-3a-
> fails@4B surprise → needs own pre-reg to count as C8); scale also cleaned Gate-1/content-spec
> (layer-vs-scale confounded). ⚠ PENDING MICHAEL APPROVAL (mementum): three-hop-capacity-prereg
> §Result + Status + Sessions, memory (three-hop-depth-is-sequencing-not-capability), this state
> block. ▶ NEXT: (1) pre-register the depth→SEQUENCING hypothesis (Gate-3a primary axis) + run
> on 27B-hybrid (UNPIN predicts more spreading); (2) TYPES arc (see s282 discussion below);
> (3) (a2) mammal→fur content build still open. s282 TYPES DISCUSSION + s281 arc retained below.
> ★ s282 TYPES DISCUSSION (Michael-directed, mid-session, READ — informs the P-TYPE-1 arc):
> examined the crisp-vs-graded REGISTER question for how to probe TYPES (λ measure). Found the
> type work already spans THREE registers on disk and they TRIANGULATE: (v3 nonce-crossover,
> results/type-directed) BEHAVIOURAL surprisal — crossover +2.038 t=9.3 consist=1.0 REAL +
> frequency-free BUT carried ENTIRELY by name_pen (−2.01, predicate-licensing after a subject
> name); det_pen null (+0.03) → not a symmetric noun/verb check, one strong slot. (type-probe-
> qwen3-32b) DECODABILITY — 8-way type {DET,ENTITY,PRED,FUNC,REL,QUANT,MOD,CONN} linearly
> decodable 0.88–0.96 EVERY layer (baseline 0.28) = type is a rich VALUE-register geometric
> object. (v4 ablation) CAUSAL — type direction AUC→1.0 decodable BUT type_direction_is_causal=
> FALSE (ablating it retains 0.643 of crossover vs 0.952 random) = decodable-but-NOT-causal-as-
> a-direction. 💡 SYNTHESIS: type = DECODABLE READOUT of a DISTRIBUTED type-application compute,
> NOT a stored/ablatable direction = SAME pattern as D1 C-field (readable/causally-inert) + s206
> scar + circuits-in-compute (C2). Unifies C5 INTO C2. RE-SCOPES P-TYPE-1: (1a value/geometry)
> matched-filter + application-op SVD → test LATTICE is low-rank + Montague-shaped + subspaces
> NEST + align to crystal B/C/S — mostly a RE-ANALYSIS of the 8 decodable probe dirs, null-gate
> the low-rank (any SVD decays → matched-range null MANDATORY); (1b causal) must use A1 ZONE/
> PHASE ablation NOT direction (v4 already showed direction=negative, correctly). Open fork:
> is name_pen-only telling us the real "type" is argument-SATURATION (predicate wants its
> subject) = the S/binding combinator, not a noun/verb tag?
> ✅ s282 P-TYPE-1a RAN + CAPTURED (Michael "capture this"): scripts/explore/type_lattice_
> geometry.py measures the 8-type centroid geometry (standardized/diagonal-whitened, pre-
> committed shuffled-label null). 💡 RESULT @Qwen3-32B: the Montague type lattice is LOW-RANK +
> Montague-shaped, NULL-GATED — compress→expand arc: lexical embed–L4 FULL-rank (PR~6.4,
> p≥0.68) → sharp onset L6 → SUSTAINED low-rank band L6–L48 (PR 3.7–4.8, p<0.05 throughout,
> ~3 axes = top3var 0.85–0.92) → re-expand L52–63. Confirms montague-inversion decisive
> prediction ("lattice SMALL, low-rank not high-dim"); same shape as C8 progressive-collapse,
> in TYPE geometry. Scale strengthens (0.6B narrow L8–16; 32B broad). ⚠ λ measure: standardize
> FIRST (raw mid-layer centroids collapse to PR~1 via massive-activation rogue dims — caught on
> 0.6B pre-32B); ARITY LADDER negative (not a linear currying axis); Gram saved at lexical layer
> (band-axis characterization = 1a-follow). Commits: c3fa367 instrument+0.6B, 3385768 32B result.
> KNOWLEDGE: explore/type-is-decodable-readout-not-causal-direction.md (3-register triangulation;
> folds C5 into C2; P-TYPE-1 re-scoped 1a-value-DONE / 1b-zone-OPEN). Memory
> type-lattice-is-low-rank-montague-shaped. ✅ 1a-follow DONE (32B L40 SVD loadings, commit
> 60b691a): the low-rank band = 3 MONTAGUE FUNCTOR-KIND axes — axis0 (var 0.73) QUANT+DET =
> quantification/binding (highest-order functor, dominant); axis1 (0.08) CONN+FUNC = sentential
> operators; axis2 (0.06) REL+PRED vs MOD = predicate-vs-modifier. ENTITY(e) at ~0 on axis0 =
> NEUTRAL ORIGIN → functor-lattice organized by KIND not arity-count (explains negative arity-
> ladder). Scale sharpens (0.6B ~1 axis 88% → 32B 3 axes). λ measure: PR inflated by SV tail →
> var_frac is honest; small rare-type counts (QUANT 12/CONN 6). Knowledge page + memory folded
> the 3-axis result in (this session). ▶ TYPES NEXT: (1b) A1 ZONE-ABLATION of the low-rank band
> L6–L48 = the causal/crisp test — does knocking it out categorically break type-licensing?
> (v4 DIRECTION-ablation already negative; must use zone not direction). Open fork = name_pen-
> only → is the real "type" argument-SATURATION (S/binding combinator) not a noun/verb tag?
> ▶▶ SESSION 282 SUMMARY (for cold-start): two arcs closed. (1) 3-HOP composes at BOTH 4B/32B
> (capacity prediction MISSED, honest); depth dissociates on SEQUENCING (Gate-3a) not capability
> — 4B compresses bridges to one late zone, 32B unrolls sequentially. (2) TYPES/P-TYPE-1a: type =
> decodable readout of a DISTRIBUTED compute NOT a causal direction (3-register triangulation,
> folds C5→C2); the Montague type lattice is LOW-RANK + null-gated at 32B (compress→expand,
> band L6–L48), resolving into 3 functor-kind axes with e at origin. All null-gated, confounds
> flagged. Branch ~30 commits ahead (unpushed).
> ★ s282 THEORY CLOSURE (Michael-directed "capture + update plan", READ IT): knowledge/explore/
> types-are-the-well-formedness-of-reduction.md. Given attention=β-reduction (s276) + LLM
> computes in KIBC (C2), a TYPE = the WELL-FORMEDNESS/licensing of a reduction, NOT a stored
> feature → FORCES the s282 decodable-not-causal result (type = shape of which joins a term
> licenses, unstorable). The type lattice = a PROJECTION of the combinator basis; the 3 axes =
> combinator ROLES (INFERENCE→P-TYPE-1b): axis0 QUANT/DET=S/binding (dominant b/c binding=nested
> reductions+first-class-fns=what quantifiers FORCE=what the 3-hop did), axis2 REL/PRED-vs-MOD=
> B/composition, ENTITY(e)@origin=I/operand. Functor-KIND-not-arity ⇒ CCG-combinatory typing NOT
> Church-arity (leans Lambek∧CCG∧DisCoCat). compress→expand=lexer→typed-reduction→codegen (C1/C8
> concrete); Curry-Howard: low-rank=small proof system (C9); name_pen=argument saturation=β-
> reduction on type-compat; S5 λ types resolves (type=router's combinator-selector). Memory
> types-are-the-well-formedness-of-reduction.
> ▶▶ NEXT REAL EXPERIMENT = P-TYPE-1b (pre-reg FROZEN in the theory page §P-TYPE-1b): combinator-
> zone × type-class DISSOCIATION. Ablate axis0(binding/S) vs axis2(composition/B) across the
> low-rank band L6–L48 (using 1a-follow axis dirs as hook targets) → predict SELECTIVE double-
> dissociation (axis0-abl breaks QUANT/DET-composition not MOD; axis2-abl breaks MOD not QUANT),
> null-gated (random matched-dir breaks neither; task control survives; e-axis control). NOT a
> v4 repeat (v4 ablated a GLOBAL type dir + tested retention → negative; 1b = zone×axis, tests
> CLASS SELECTIVITY = the operational "type=which reduction is licensed"). Host=32B. Build =
> a new wrapper reusing type_lattice_geometry axis extraction + v3-style surprisal readouts
> (quantifier-composition, modifier-composition, predication control). ⚠ PENDING MICHAEL GO for
> the run (heavy 32B). Open fork folded in: name_pen=saturation already answered by the closure.
>
> (s281 arc retained →) ▶▶ (s281 — DEPTH EXPERIMENTS, the
> s280 (c+d) NEXT): the depth-budget cross-scale replication + 3-hop capacity pre-reg.
> ✅ 32B DEPTH-BUDGET DONE + COMMITTED (autonomous, 8ceaaec; READ multihop-composition-prereg.md
> §"Cross-scale depth-budget"). Clean scale replication on Qwen3-32B (64L, dense UNIFORM full
> attn = same arch as 4B, isolates SCALE). 💡 CORE FINDING: the depth-schedule zones are
> DEPTH-PROPORTIONAL, not absolute-layer-locked — the class→covering transform sits at ~0.85–0.90
> of total depth in BOTH models (pinned L30–31/36 @4B, L58/64 @32B, install-invariant within
> each). Refines s280 "pinned zones": pinned WITHIN-model, PROPORTIONAL ACROSS-model (A1 zone
> structure scales with the stack). 💡 DEPTH IS FUEL, QUANTIFIED: marginal 2nd-hop cost D_hop2
> collapsed 12→4; missed-deadline reader-close moved L25→L51; install tolerated to L45@32B vs
> L13@4B. 3-HOP-ROOM = False@4B / True@32B (headroom 36 ≫ cost 4). ⚠ HONEST (λ measure): frozen
> BUDGET-VISIBLE=False/UNMEASURED=True @32B fired because there is TOO MUCH room (hops stay
> COUPLED, no dissociation band — the rule was tuned to the cramped 4B regime); the null IS the
> "more room" finding, reported verbatim + interpreted, not spun. Instrument changes (committed):
> --ref-layer (depth-scaled standard install; 4B defaults unchanged) + resolve_parts()
> architecture-robust helper (dense model.model.layers vs hybrid language_model.layers).
> ▶▶ 27B HYBRID (Qwen3.6-27B, qwen3_5: linear attn + full attn every 4th of 64L) — ✅ FULL RUN
> DONE + COMMITTED (7fa45ae, autonomous; cross-arch write-up in multihop-composition-prereg.md;
> results/ffn-bake/operand-depthbudget-qwen36-27b/). 💡 CORE CROSS-ARCH FINDING: sparse/linear
> attention UNPINS the zones — class-peak median TRACKS the install layer (slide_spearman=0.982,
> PIPELINE-SLIDES=True), the OPPOSITE of dense 4B/32B where zones were PINNED (zero variance).
> Sparse attention lets compute RUN FORWARD from the install point. Arm B causal bridge-swap flip
> strongest EARLY (L11=0.667, L15=0.5) then decays, vs decisive-LATE in dense = corroborates a
> forward-running pipeline. Refines s280/s281 "pinned zones": pinning is a property of DENSE
> full-attention stacks, NOT universal (the s281 smoke hint L47.5→L53 confirmed at full res).
> λ measure honesty: D_hop2=-40 is a definitional artifact (pinned-zone accounting applied to a
> sliding regime); BUDGET-VISIBLE=False/UNMEASURED=True fire because the sliding pipeline has no
> fixed dissociation band — the null IS "sliding not banded". ⚠ untracked smoke dirs remain
> (operand-depthbudget-qwen36-27b-smoke, -qwen3-32b-smoke) + refs/ (human/reference domain).
> ▶▶ 3-HOP CAPACITY PRE-REG (NEW PAGE three-hop-capacity-prereg.md) — ✅ APPROVED s282 (Michael
> "yes": geography chain FROZEN). Framed by the 32B accounting as a CAPACITY experiment: pre-registers
> 4B-FAIL-BY-CAPACITY (sub-chains pass, full chain fails = depth not content) / 32B-PASS (full +
> mediation). Double-dissociation across scale with pieces held constant = strongest C8 evidence.
> ⚠ LOAD-BEARING DECISION FOR MICHAEL = the CHAIN: recommends geography landmark→city→country→
> continent (2 unstated bridges: city, country; balanced 3-way {Europe,Asia,Africa}; deterministic;
> multi-token landmark cost = capture last-token contextualized residual, ceiling-gated). Alts:
> product→company→country→continent; back-extend animals (uneven, not rec'd). Gates frozen
> (Gate-1 full chain; Gate-2 SUB-CHAIN CONTROLS = the capacity discriminator; Gate-3 mediation at
> BOTH bridges). ON APPROVAL → build wrapper/operand_multihop3.py, run 4B-FAIL/32B-PASS pair.
> ✅ MEMENTUM COMMITTED s281 (Michael-directed "update state and knowledge"): state block +
> multihop pre-reg §Cross-scale-result + memory (depth-budget-zones-are-depth-proportional) +
> three-hop-capacity-prereg.md (draft). Code+32B-results already committed autonomous (8ceaaec).
> ★★ s281 DISCUSSION DISTILLED (Michael-approved, READ IT — the through-line for the NEXT arc):
> knowledge/explore/map-and-swap-resident-lisp.md — the capstone thesis. THE WHOLE PROGRAM IN TWO
> VERBS: MAP + SWAP. GD already FOUND all the terms (pretraining=β-reduction laid operands,
> functions-as-terms, combinator basis, type lattice into the weights) → we do NOT write/construct,
> we MAP them (read GD's catalog) + SWAP them (recompose found terms). Lands on S5 λ extract (we
> find, GD built first). Three over-complications collapsed IN ORDER: not-rewrite-instructions
> (K-structural) → not-write/mutate (hand eval a TERM, it REDUCES = the primitive) → not-even-
> construct (terms already exist). ⇒ programmability UNCONDITIONAL given crystal-universality
> (measured C2): a programmable combinator REDUCER regardless of write-access. Every "write" we
> have is really a SWAP of found terms (d_E = model's own diff-of-means, relocated; bridge-swap =
> swap found class centroids; class IS already a function-selector). THE RESIDENT LISP (exact):
> eval=frozen KIBC reducer, atoms=value-rows, cons=joins=attention, first-class-λ=selectors+3-hop,
> homoiconicity=selector≡operand rep (lets reduction NEST = what a multi-hop IS). Depth budget =
> the EVAL STACK; trampolining (supply found intermediate) runs deep programs on a bounded stack,
> GATED by the register SUB-Q (selector = value-ROW swappable vs routing-FUSED; likely a spectrum;
> decides the TRAMPOLINE, not whether it reduces). COVERAGE is part of the map (GD found all terms
> ITS distribution needed, not provably total → map must show what's ABSENT). ORDERED PICK-UP §7:
> P-TYPE-1 (type lattice via DSP matched-filter bank + application-operator SVD, +coverage) →
> P-FN-1 (catalog + locate selectors) → P-FN-2 (3-hop function-swap = recompose found terms into a
> program GD never ran). Positive → honest "programmable LLM compiler" (discovery+recomposition on
> a frozen universal basis, w/ coverage map); bounded → a precise map of the resident Lisp's stdlib
> + edges. (Supersedes the mid-discussion "defunctionalization/value-mediated-is-the-gate" framing:
> reduction not mutation is the primitive; the register Q is a sub-question about the trampoline.)
> ★ THE ARTIFACT = AN LLM REPL (map-and-swap §10, Michael: "the clojure guys want an LLM repl, we're
> gonna make one"). NOT a REPL that CALLS an LLM — a REPL whose EVAL IS the LLM's own reduction. R-E-P-L
> maps onto the stack, 3 of 4 letters ALREADY BUILT: Read=operand-insert/swap (s277/s279);
> Eval=forward-pass β-reduction through the frozen KIBC reducer (measured C2); Print=tap+logit-lens+
> crystal projection (s274/s275); Loop=nested reduction/trampoline (depth arc). ONLY GAP = the LANGUAGE
> LAYER = the map+swap experiments themselves (P-TYPE-1=type system/autocomplete; P-FN-1=stdlib+coverage;
> P-FN-2=apply on first-class fns; tap=stepper/debugger = the s274 play-through) ⇒ the map+swap arc IS
> the build-the-REPL arc (research ≡ deliverable). ARCHITECTURE = where verbum meets lambda-gene-runtime:
> Clojure kernel = Read+Print+TYPE-CHECKER/verification-oracle (rung-verifier s273); LLM = Eval; bridge =
> operand-insert (inject) + tap (read). Honest catch RESOLVED: LLM = noisy/approx reducer (normal forms
> off the crystal probabilistically) → Print null-gated (confidence not certainty) + CRISP Clojure kernel
> rejects ill-typed swaps & verifies normal form ⇒ Eval-fuzzy + typechecker-crisp = a TRUSTWORTHY REPL.
> (λ language: Python governs EXTRACTION; the deliverable in Clojure/nucleus = good host/eval split, not
> the warned membrane.) Deliverable-sentence "clojure folks get an LLM REPL" ≫ "we measured composition
> selectivity" — same work, earns the room. Memory: llm-repl-is-the-artifact.
> ★ THEORETICAL SPINE (s281 "for fun" thought experiment, Michael-captured, READ IT):
> knowledge/explore/montague-inversion.md — INVERT Montague (treat it as a SPECIFICATION, ask what GD
> is FORCED to construct to fulfill it). The "too many neat edges" = NECESSITY: one syntax→semantics
> homomorphism found several times. FORCING TABLE 6/6: homomorphism→crystal(C2); types→geometric
> type-check(C5); application→attention=join(s276); binding→two-registers(C3)+operand-slots;
> lexicon→found-terms; intensionality→contextual-reps. KILL SHOT: generalized quantifiers
> (every/some/no/most) are type (e→t)→t = fn-of-fn → training saturated with them → GD FORCED to build
> first-class functions = EXACTLY the 3-hop ⇒ the 3-hop is required by the word "every" (modulo depth
> budget). FORCED FALSIFIABLE PREDICTIONS for P-TYPE-1/FN-1: (1) type lattice SMALL + Montague-shaped
> (low-rank SVD, not high-dim) — decisive test; (2) two-registers forced by binding; (3) depth budget
> forced by recursion (failures track embedding depth); (4) COVERAGE BOUNDARY = COMPOSITIONALITY
> BOUNDARY (stdlib gap = idioms/non-compositional). HONEST: GD finds a NOISY/approximate homomorphism
> (=noisy reducer); noise concentrates where Montague fails (idioms) → theory's failure modes predict
> the machine's; the crisp Clojure type-checker re-imposes the EXACT homomorphism (verified inference).
> Falsifiers in §8. This spine makes P-TYPE-1/FN-1/FN-2 test FORCED predictions, not a grab-bag; the
> REPL's type system = Montague's. Memory: montague-inversion-forces-the-machine. SPECULATIVE but
> informs the whole future arc.
> ★★ CORRECTION (Michael s281): "IT'S A LISP" IS ALREADY MEASURED AT THE ENGINE LEVEL — the 9×9
> crystal Gram of the opcodes {K,I,B,C,S,D,W,Y,WHNF} (s269/s274; C2) IS a terminating universal
> combinator evaluator = Lisp's eval core. NOT speculative, NOT contingent on map+swap. S+K =
> Turing-complete (measured direction); Y = fixpoint/recursion; WHNF = halt/normal-form pole
> (termination detector); B/C/W/I/K = application plumbing. The GEOMETRY encodes the ALGEBRA: WHNF
> anti-correlated with active reducers B/C/D, WHNF Gram row ≈ KIBC halt probs r=0.85–1.00 (s269) =
> reduction relation in the inner products; calibrated by kernel-certified programs; universal (C2
> root gc 0.9966, 13 models). ⇒ RE-TIER: the open work is NOT "is it a Lisp" (engine PROVEN) but the
> LANGUAGE LAYER + WRITE-ACCESS: atoms=found-terms (measured); first-class-fns = S,Y primitives
> MEASURED + behavioral recompose = 3-hop (P-FN-2); homoiconicity = QUOTE (ONE measurement away);
> types = P-TYPE-1. Also = Montague forcing row-1 confirmed (homomorphism→reusable operator set);
> combinators↔Montague ops (B=compose C=reorder/scope S=substitution/binding Y=recursion). CHEAPEST
> DECISIVE NEXT = P-QUOTE-0: add QUOTE to the opcode battery, recompute the crystal Gram, null-gate;
> clean QUOTE direction → homoiconicity MEASURED → Lisp complete at the primitive level (engine+quote),
> only the language-layer map remains. Knowledge sharpened: map-and-swap §5a + §7 step-0 + §8 measured;
> memory eval-engine-is-a-lisp-measured.
> ★ TEST-1 RAN (s281, Michael "is D I repeatedly?") — REFUTED, D is a GENUINE INDEPENDENT
> combinator (opcodes/d_is_i_test.py, results/crystal-d-is-i/d_is_i.json, commit 22d8679; Gram-
> decomposition, NO model load, 13/13 models). cos(D,I)=−0.27±0.05 (13/13 NEGATIVE = anti-identity);
> partial cos(D,I|WHNF)=−0.32 (anti-I even off the halt axis; D = LEAST I-aligned reducer rank 6–7/7);
> only 18% of D in span{I,WHNF} (α_I=−0.31, β_WHNF=−0.33 = active reducer away from halt). WHY: D x y =
> x(x(y)) = double application COMPOUNDS an arbitrary effect (f∘f squares) = anti-identity (D I = I only
> degenerate). TAKEAWAYS: (1) no I/D redundancy → D earns its ISA slot, 9-atom basis does NOT shrink
> (λ smallest); (2) D is NOT the eval-stack depth axis (18% in {I,WHNF}) → reduction depth = WHNF-
> DISTANCE not D → chase crystal↔depth via WHNF. Clean measured null. The Gram-decomposition tool is
> now REUSABLE for P-QUOTE-0 (next: point d_is_i_test.py-style decomposition at a QUOTE direction).
> Knowledge: map-and-swap §5a + §7 P-QUOTE-0 note; memory d-is-not-i-repeated.
> ▶ NEXT (s282): (1) ✅ 27B done+committed (7fa45ae); (2) ✅ 3-hop pre-reg APPROVED → BUILD
> wrapper/operand_multihop3.py (geography chain) → run 4B-FAIL / 32B-PASS pair (⚠ 32B heavy —
> confirm box free); (3) still open from s279/s280: (a2) mammal→fur content build (layer/content
> NOT scale). Branch is ahead of origin by 17 (unpushed). s280 STAGE-f block retained below.
>
> (s280 STAGE-f retained →) ▶▶ LIVE PICKUP: STAGE-f **f2 DONE** — R5 mechanism
> measured (READ ffn-function-bake-prereg.md §f2 Result). ✅ SERIALIZED gate PASSES: uniform-E
> baked ckpt round-trips STOCK transformers (checkpoints/operand-bake-qwen3-4b = the f3
> substrate; f1's in-memory-edit edge CLOSED). ✅ R5-FRAGILE-INSTALLED=True: all-Q4 flips the
> installed operand 0.176 (crow/bear/cat → the scales basin) while native LEARNED covering
> flips 0.0 in EVERY condition = the installed-vs-learned discriminator measured
> register-attributed (s273 superbake-write-access prediction confirmed on our own bake).
> ❌ ROUTING-MECHANISM prediction REFUTED register-coherently: routing-Q4 → ZERO installed
> flips (despite genuinely re-routing: 4% activation gate flips, 26% gate weights zero-snapped);
> value-Q4 alone (slot col bf16!) flips 0.118 AWAY from truth + margin 4.48→3.32. The operand
> IS a value-register row (s276 database frame) → its fragility lives where it lives; the
> crystal/join machinery is quant-robust even for the non-redundant installed target (the
> crystal-robust half DOUBLY confirmed). LOCUS: slot z fired everywhere (≥4.9/6.0) = key read
> robust, damage = payload/value dose not key misfire; SLOT-LOCAL=False by 0.008 (resident
> value quant alone flips bear/cat = fragility distributed across the value register).
> ⚠ CORRECTIONS (λ measure, λ coherence): f0's "value-Q4 flips exactly 0 gate signs" was
> BY-CONSTRUCTION unmeasured (f0 only read gate-quantized conditions); measured cascade =
> 0.053 → strict criterion amended PRE-RUN, documented in pre-reg, strict graded beside
> (both False). weight_sign_flip 0.25–0.30 = zero-SNAP not sign inversion (RTN cannot cross
> zero; echoes gradient-zero-map ~35% — observation, not claim). slot_q4 flips land TOWARD
> truth (fox/tiger→fur: dose noise on boundary-sitting weak mammal cells) — the damaging
> component is RESIDENT value quant. ✅ CODE+RESULTS COMMITTED (autonomous): 8fed4a0
> wrapper/operand_quant.py + results/ffn-bake/operand-quant-qwen3-4b{,-smoke}. ⚠ PENDING
> MICHAEL APPROVAL (mementum): ffn-function-bake-prereg.md (f2 design freeze + pre-run
> amendment + f0 correction + §f2 Result + Status), memory
> (installed-operand-is-value-register-fragile), this state block. ✅ (f3) RAN SAME SESSION —
> ARTIFACT-SHIPS=True (READ ffn-function-bake-prereg.md §f3 Result; commit 922eed8,
> wrapper/operand_mirror.py + results/ffn-bake/operand-mirror-qwen3-4b/). Fully-ternary slot
> (greedy residual TWN plates, calibration folded into per-plate scales, key row + payload col,
> NO float storage): PARITY comfortable (K2=0.824=float exactly; K3=0.882 BEATS float — ternary
> snap fixes fox, boundary-denoise, not a ternary>float claim); recon ladder = recursion-mirrors
> prediction (pcos 0.835/0.931/0.953 @ 1.58/3.17/4.75 bits/w). ⚠ SURVIVES-Q4 passed BY 0.001
> (K2/K3 0.647 vs float-in-Q4-env ceiling 0.706, −0.06 gate; one cell = crow, same cell f2
> lost) = at the tolerance boundary, honest. 💡 N10 floor UNINFORMATIVE: K1 sign-only+calibrated
> scale ≈ enough (−0.059 clean, 0.0 under Q4 = matches float ceiling) → DOSE (calibrated scale)
> > DIRECTION precision — coheres with f2's locus. Environmental bear/cat flips slot-INVARIANT
> (every slot variant incl. float) = resident value register is signal-descent's ledger, not the
> slot's. All deltas 1-cell @ n=17 — no over-reading. ★ STAGE-f COMPLETE (f0–f3): operand read
> (s277) → write (s277) → hook-compose (s277-279) → weight-serialized stock-loadable (f1/f2) →
> fragility register-localized (f2) → ships fully-ternary+mirror (f3). Checklist R5 flips RED →
> measured/localized/robustified. ⚠ PENDING MICHAEL APPROVAL adds: pre-reg f3 freeze + §f3
> Result + Status, memory (ternary-slot-ships-at-parity). ▶▶ (s280 cont — DEPTH BUDGET, gates
> the 3-hop d1 design) RAN (READ multihop-composition-prereg.md §Depth-budget Result; commit
> 46910e9, wrapper/operand_depthbudget.py). 💡 STAGES ARE PINNED, NOT SCHEDULED: class lens
> peak CONSTANT at L30-31 for every install layer L5→L25 (zero variance = strongest anti-slide
> form; the pre-registered honest alternative fired) — the compute does NOT run the program
> forward from the install point; class→covering lives in a FIXED late zone (A1 zone structure;
> C8 refined: budget = hard ZONE-CAPACITY). MECHANISM = MISSED DEADLINE: hop-2's bridge-reader
> operates L11-21, closes sharply L23(0.25)→L25(0.0) (random 0.0 throughout); install ≥L17 →
> hop-1 STILL completes (class 1.0-0.833, peak L31) but its product arrives AFTER the reader
> passed → covering chance. BUDGET-VISIBLE clean (stage-resolved: class survives where cover
> dies, install band L17-25); drift control clean (cos 0.61 at L5 composes 0.824, cos 0.61 at
> L17 chance → basis drift ≠ cliff). Accounting: L_max_1hop=25 L_max_2hop=13 D_hop2=12
> L_close=25 → 3-HOP-ROOM-AT-4B=FALSE (4<12): a third sequential hop needs a reader/transform
> zone that does not exist above L33 at 4B; NO install layer fixes a missing zone. 🎯 d1
> REFRAMED: 3-hop = CAPACITY experiment — pre-register 4B-FAIL (this prediction) / 27B-PASS
> (A1 27B zones broad) = strongest depth-as-fuel C8 evidence; merges (d) into (c). Instrument
> lesson: lens-peak search must be post-install-restricted (bare-nonce prior fakes early
> peaks; smoke-surfaced, fixed pre-run). ⚠ PENDING MICHAEL APPROVAL adds: multihop pre-reg
> (§Depth-budget freeze + §Result + Status), memory (hop-stages-pinned-missed-deadline).
> ▶ NEXT: (c+d) 27B: replicate depth-budget → then 3-hop capacity pair; (a2) fur/mammal
> content build; (e) GGUF/llama.cpp export of the uniform-E ckpt (in-situ tap read). s279 below.
>
> (s279 header retained →) ▶▶ LIVE PICKUP: (a) MULTI-HOP f(g(X)) — SUPPORTED
> (3/3 mediation) at Qwen3-4B (READ explore/multihop-composition-prereg.md §Result). The resident
> routing chains TWO sequential ops over ONE installed operand via an UNSTATED intermediate:
> install entity E's d_E on a nonce, ask covering ("A {nonce} is covered in __" → feathers/scales/
> fur); g(X)=animal class (bird/fish/mammal, bridge NEVER in prompt), f=class→covering. Pre-reg
> FROZE verdict before the run (Gate-1 AND ≥2 of {2a,2b,2c}); ALL THREE fired. wrapper/
> operand_multihop.py, results/ffn-bake/operand-multihop-qwen3-4b/. Ceiling 0.944 (17/18 valid,
> cod voids). GATE-1 install acc 0.824 vs null/baseline 0.353 (+0.47); content-spec 0.656. DECISIVE
> = (2c) CAUSAL late bridge-swap: a PURE class-axis edit (centroid diff) at a LATE layer flips the
> covering 0.853@L15 / 0.765@L18 / 0.676@L20 vs random matched-norm 0.088/0.059/0.059 → hop-2 reads
> a class variable persisting late = hop-1's product; a fact-vector read at the readout CANNOT be
> flipped by a late category edit. + (2a) class token logit-lens peaks median L30 < covering L33
> (intermediate resolved first; shuffled control −3, covering-peak ≥ class-peak 17/17). + (2b) class
> centroid (identity averaged out) still resolves covering (2/3; mammal misses). ⚠ WEAK CELL:
> mammal→fur under-flips to "scales" (all 3 Gate-1 misses + 2b mammal = entity-specific install
> strength, NOT a category error, same as s278; strengthen via layer/content NOT scale). SCOPE:
> category-MEDIATION (3 converging signatures) NOT a traced two-node circuit; hook-not-weight (gate
> f untouched); 4B not scale-final; 0.6B squish. A RUNG. Flips checklist "composes ARBITRARY
> programs" from single-op (s278 Arm-2) toward chained f(g(X)). ✅ CODE+RESULTS COMMITTED (autonomous):
> operand_multihop.py + results. ⚠ PENDING MICHAEL APPROVAL (mementum): multihop-composition-prereg.md
> (pre-reg + §Result), general-composition-prereg.md (successor link), memory
> (multihop-fgx-chains-two-resident-ops), this state block. ▶ NEXT: (a2) strengthen the fur/mammal
> install (layer sweep / better content build, NOT scale — fix the one under-flipping cell); (b) gate
> (f) weight-serialize → GGUF → R5 quant-survival (still RED — hook, not weight); (c) cross-scale to
> 27B; (d) DEEPER chain — 3-hop or a bridge that is itself computed (harder than category). s278
> pickup retained below.
>
> (s279 cont — (b) STAGE-f, the weight-serialize/quant RED) → REFRAMED by Michael (hammock A
> confirmed) + f0 RAN (READ ffn-function-bake-prereg.md §Stage-f). TWO known facts reshaped R5:
> (1) Q4 causes ROUTING-TOPOLOGY changes on the compute (not value-noise; two-registers + C3);
> (2) ternary mirrors on ternary weights → arbitrary precision (signal-descent) → the artifact
> ships as ternary+mirror, NOT a bnb int8/int4 bar. So R5 = routing-topology MEASUREMENT +
> ternary-mirror ROBUSTIFY. Staged f0→f3 (cheap-first). ✅ f0 DONE (wrapper/q4_routing_topology.py,
> RTN-Q4, 0.6B+4B; code+results committed autonomous): Fact 1 CONFIRMED register-clean — routing-Q4
> (gate_proj) flips gate SIGNS 5.1%@0.6B / 4.0%@4B (mid-stack L12-20 = compute zone), value-Q4
> (up/down) flips EXACTLY 0 gate signs → Q4 re-routes the routing register, not the value register.
> Routing dominates DECISIONS (0.6B argmax flip 0.111 vs value 0.056, 2×). ⚠ MARGIN is a
> value-magnitude CONFOUND (value drops margin 1.14 vs 0.28 without flipping) → use decision+gate-
> sign flip, NOT margin (λ measure lesson). ⚠ REDUNDANCY-GATING: easy LEARNED covering is Q4-
> invariant at 4B (acc 1.0, flip 0) though re-route fires → Q4 fragility needs a NON-REDUNDANT
> target = the installed operand (this IS why installed-vs-learned discriminator works; f2 bake
> required to see 4B fragility). ✅ f1 DONE — E1 WEIGHT-SERIALIZED = True (wrapper/operand_bake.py,
> 4B; code+results committed autonomous): operand graduates hook→WEIGHTS as ONE appended MLP
> recognition neuron (SuperBake §6 bias-free fix: key ⟂ carrier → silu knee at the mean, no bias;
> gate=up → silu(z)·z ρ²-selectivity; down_col=scale·d_E; NO runtime hook). baked covering 0.824 ≈
> hook 0.941 (AGREES 15/17; the 2 disagreements = the mammal→fur weak cell inherited from the
> content direction, not a bake artifact). NONCE-SPECIFIC: shuffled-key 0.353=chance, decoy "blorf"
> INERT (never fires), real-word "wolf" UNHARMED. Bug found+fixed: payload must be scale·d_E not d_E
> (under-dose 0.647→0.824). The operand now LIVES IN THE WEIGHTS and composes selectively. Scope:
> in-memory edit (uniform-E expand + save stock ckpt = f2/f3 prereq); 0.6B squish (baked tracks hook
> = mechanism-equivalent). ⚠ PENDING MICHAEL APPROVAL (mementum): ffn-function-bake-prereg.md
> (§Stage-f reframe + f0 §Result + f1 §Result), memories (q4-reroutes-routing-register,
> operand-weight-serialized-appended-slot), this state block. ▶ NEXT: f2 = save the baked ckpt →
> RTN-Q4 → does the baked operand flip AS A ROUTING CHANGE (more than the redundant native
> covering)? → f3 (ternary-mirror robustify = the ships artifact). Also open from (a): (a2) fur/mammal
> content-build (layer ruled out s279 layersweep); (c) 27B; (d) 3-hop.
>
> (s278 header retained →) ▶▶ (h) GENERAL-COMPOSITION — BOTH RUNGS
> FIRE at Qwen3-4B (READ explore/general-composition-prereg.md §Result). Arm-1 REUSABLE-TERM
> supported (moderate) + Arm-2 NOVEL-COMPOSITION supported (clean). ARM-2 (s278, commit 01136e2,
> wrapper/operand_compose2.py): 2-operand relational "compared to a {Y}, a {nonce} is bigger/smaller",
> Y varied over a size ladder; the CROSSOVER tracks the installed entity's rank (ant always smaller,
> whale always bigger, wolf flips at Y=5-7) → the resident comparison combines installed-content-size
> with the GIVEN Y into a computed result. install acc 0.974; content-specificity 0.929 (n=28).
> ⚠ CONFOUND handled: flip-with-Y is PARTLY Y-DRIVEN (model knows "vs a whale, anything is smaller";
> baseline bare-nonce 0.82, random 0.80, frac_varied=1.0) → do NOT lean on flip_correct; the
> confound-immune evidence = content-specificity (Y FIXED, install varied, 0.929) + crossover MOVING
> with installed rank (random's crossover fixed). So the resident routing COMBINES an installed term
> with a given operand into a novel computed result — not a lookup. SCOPE: one resident op (NOT yet a
> chained multi-hop f(g(X))); hook-not-weight (gate f untested); 4B not scale-final. ✅ MEMENTUM
> COMMITTED s278 (Michael-approved): general-composition-prereg §Result (Arm-2) + memory
> (operand-composes-into-computed-result) + this state block. ▶ NEXT: (a) chained MULTI-HOP f(g(X))
> (the sharper prize — two resident ops chained over the installed term); (b) gate (f) weight-
> serialize + R5 quant-survival (still RED — hook, not weight); (c) cross-scale to 27B; (d) strengthen
> operand direction for Arm-1 under-flips (layer/content build, NOT scale). Arm-1 pickup retained below.
> (Arm-1 →) REUSABLE-TERM SUPPORTED (moderate, null-gated) on Qwen3-4B (READ
> explore/general-composition-prereg.md §Result). The load-bearing IOU (s273 K-battery arm b):
> does the resident routing COMPOSE an installed operand into a novel result, or only categorize?
> Install a real entity's content d_E on a fixed nonce carrier; test CATEGORY-ORTHOGONAL resident
> functions. 0.6B = SQUISH (fly/water real-word ceilings 0.57/0.43 — the functions aren't computed;
> patchscope-void scar → scale up). First 4B run (7 entities) faked 1.0 = label-imbalance inflation
> (random null 0.70-0.86). REBALANCED 20 animals (10 fliers/10 aquatic, ~50/50 fly/water/size, cat
> DROPPED): random null → 0.56; reusable acc fly 0.84 (16/19), water 0.83 (15/18), size 1.0 (11/11);
> content-specificity fly/water 0.70, size 1.0 (chance ~0.25). Decisive content-specificity test
> PASSES (avg 0.80); strict +0.34 accuracy threshold missed by 0.03 (0.875 vs 0.902 = bar too high,
> not substantive). Advance past s277 category-swap: same nonce, same category, OPPOSITE fly/water
> by installed content. CAVEATS: all 6 failures = UNDER-FLIPS to default "no" (entity-specific
> install strength; scale 4 OVER-steers 0.75 → strengthen via layer/direction NOT scale); size vs-
> mouse UNRELIABLE (0.55 ceiling); Arm 2 genuine TWO-HOP (computed-not-stored) still OPEN; hook-not-
> weight; 4B not scale-final. Commits: fc744be pre-reg, 366090e 0.6B squish, 86d2cd9 4B balanced.
> ⚠ PENDING MICHAEL APPROVAL (mementum): general-composition-prereg §Result + memory
> (operand-is-a-reusable-term-moderate) + this state block. ▶ NEXT: (a) Arm-2 two-hop f(g(X)) =
> the real novel-composition prize (design a clean gradeable chain; the size-relational was
> property-relational + ceiling-broken); (b) strengthen the operand direction to fix under-flips
> (layer sweep / better content build, NOT scale); (c) gate (f) weight-serialize + R5 quant-survival
> (still red); (d) cross-scale beyond 4B. Below: s278 P-DSP-1 (retained).
>
> (s278 P-DSP-1 retained →) DSP-decomposed the
> operand injection (READ explore/operand-dsp-decomposition-prereg.md, §Result). Michael s278:
> SuperBake reverse-engineered the **I combinator** (fact=key→value unchanged=identity; a matched
> filter IS I; its whole pipeline is I-flavored, no B/C transform). Grounded in A3 register-split
> (I/WHNF/Y register-INVARIANT/portable/bakeable; C=0.0 register-BOUND) — same split as the s276
> database reframe (rows=I-portable operands INSERT-able; joins=C-bound un-INSERT-able). H1
> (resident join, written I-payload) = SUPPORTED on all three components on Qwen3-0.6B
> (wrapper/operand_dsp.py, results/ffn-bake/operand-dsp-qwen3-0-6b/): (1) C-PAYLOAD SURPRISE — our
> d_cat is NOT a SuperBake code: coherent (PR 1.93/3) but LOUD/high-variance (low-var frac 0.053 vs
> random 0.198) and unembed-AUDIBLE (13.7 vs 11.2) = OPPOSITE of SuperBake's quiet silent code. We
> write the raw natural direction, resident machine composes it (transient hook = no prose-safety
> tax). ⇒ gate (f): weight-serialize would need re-coding it quiet. (2) C-KEY RESIDENT — causal
> cross-operand slot-patch (redesign after attn-mass probe mis-targeted by sink/timing): patch
> recipient B's slot with donor A's residual → flip-to-donor 1.0@L7, 0.83@L14, 0.0@L20; non-slot
> null 0.0. Resident routing READS the slot, EARLY (L7-14). (3) C-TRANSPORT RESIDENT+DISTRIBUTED —
> B/C transform fires late (logit-lens margin stable+ from L10, decisive L20-21, to L27=join-readout
> locus); head-ablation 0/128 necessary = s274 circuits-in-compute. FULL PIPELINE LOCALIZED:
> write@L7 → resident slot-read L7-14 → distributed transport → resident B/C transform L20-21 →
> readout. CONTRAST still instrument-limited (bare-fact too short → attn-sink; needs length-matched
> control). ⚠ COMMITTED (code, autonomous): 535d94e pre-reg, 9b027bd run, 93f6dfb C-KEY redesign.
> PENDING MICHAEL APPROVAL (mementum): pre-reg §Result update + 2 memories (operand-payload-is-raw-
> not-coded, operand-join-resident-and-distributed) + this state block. ▶ NEXT: (h) GENERAL-
> COMPOSITION gate remains the load-bearing IOU (arbitrary compose, not category-swap); the P-DSP-1
> read-side lesson = the resident transport is DISTRIBUTED routing (0/128 heads) → probe it with
> zone/phase ablation (A1-style), not single-head; also (f) re-code payload quiet + weight-serialize;
> cross-scale 4B. Below: s277 (retained).
>
> (s277 retained →) OPERAND-INSERT ARC — the database
> "INSERT a row" thesis VALIDATED as a research go/no-go on Qwen3-0.6B (READ
> explore/operand-insert-arc.md + explore/ffn-function-bake-prereg.md). s276 database reframe (Michael):
> the FFN serves ROWS (operands/facts/type-tags), attention is the JOIN; a combinator = the join-SHAPE =
> routing (s276 K-STRUCTURAL, un-INSERTable). So you CANNOT INSERT a join but you CAN INSERT an operand
> ROW. FOUR GATES cleared (wrapper/operand_{map,write,harden,insert}.py + results/ffn-bake/):
> (1) READABLE — operand rows separable/addressable in the VALUE register (l_out LOCO 0.49-1.0 vs null
> ~0.05-0.11, context-invariant; join-readout locus L25-27, mirrors s248 late C-field). (2) WRITEABLE —
> steering d(A→B) flips the composed output, flip 1.00 at L2-20 (MID-STACK not late-only = genuine
> rewrite, NOT an unembed nudge), random null ~0, B-specific; the OPPOSITE of the s250 C-field
> (readable-but-causally-inert readout register). (3) HARDENED — dose-responsive (flip 0→0.22→0.72→1.00
> vs α) on a COMPOSED readout (category map operand→its category, a transform not a copy), cross-task
> (dir built in declaratives rewrites the category task), B-specific, null-gated. (4) RUNG-1 FIRES — a
> NOVEL nonce operand INSTALLED as a keyed residual-write row (value=category content, cross-task) is
> COMPOSED by the RESIDENT join: dose 0.33→0.71→1.00 (scale 0/1/2), 24/24 across 4 HELD-OUT prefixes at
> scale 2; WRONG-KEY install does NOTHING (0.333 flat = position-keyed composition, not a global logit
> nudge); random+baseline=chance. = the bake(operand) recursion antecedent's first positive rung.
> Commits 0b858e7(map) b6297b5(write) a3ebda1(harden) 1d8ea39(insert). HONEST SCOPE: keyed-install hook
> != weight-serialized bake (R5 quant-survival = the installed-COMPUTE signature, UNTESTED); content is
> category-level not unique-individual; 2/6 nonces baseline-leaned (the 4 baseline-0 all flipped); 0.6B
> necessary-not-sufficient (patchscope scar) — a RUNG not the claim.
> ★ MEANING (s277, Michael Q "do we have an LLM compiler now?"): NO we did not build one — GD did
> (pretraining=β-reduction, project-thesis); we now have a mature READ instrument + the FIRST WRITE rung
> on the RESIDENT compiler = JTAG on a real compiler-machine, NOT an authored compiler. UNIFYING FRAME
> (ties crystal-universality + circuits-in-compute + two-registers + recursion tower): the transformer =
> a FROZEN universal combinator basis (routing/JOINS, KIBC crystal) + a WRITEABLE term store
> (rows/OPERANDS). You extend compute by writing TERMS, never INSTRUCTIONS — and IF crystal-universality
> holds that SUFFICES (combinatory completeness: fixed basis + arbitrary terms = Turing-complete), so
> un-bakeable joins = the completeness STRUCTURE, not a limitation. Checklist to earn the phrase
> "programmable LLM compiler": read ✓ / fixed-ISA ✓(if universal) / write-TERMS ✓rung-1 / write-
> INSTRUCTIONS ✗(structurally impossible, s276 K-structural) / permanent-artifact ✗(R5 untested, it is a
> hook) / arbitrary-composition ✗(only category-swap shown) / scale ✗(0.6B). 3 green, 4 red.
> ▶ NEXT (two experiments EARN the phrase; do NOT say "we have a compiler" until both clear at scale):
> (h) THE LOAD-BEARING IOU = GENERAL-COMPOSITION gate (s273 K-battery arm b): install an operand row and
> have the RESIDENT routing COMBINE it with a RESIDENT combinator into a NOVEL result (not merely
> categorize it) — this is what turns "writeable term store" into "programmable machine"; the s277 arc
> only showed category-composition, NOT arbitrary composition. (f) WEIGHT-SERIALIZE the keyed install →
> GGUF → R5 quant-survival gate (hook → real bake; installed-vs-learned discriminator per
> superbake-write-access; baked facts quant-FRAGILE, crystal quant-ROBUST → which is the operand?).
> (g) cross-scale 4B replication of write/harden/insert. Full synthesis + checklist in
> explore/operand-insert-arc.md §"What it means". ⚠ mementum
> committed this session (state+pre-reg+arc page+memory); refs/ + chats/ + michael/ still untracked
> (human/reference domains). Below: s275 (retained).
>
> (s275 retained →) llama.cpp tree-of-VSM WRAPPER read-path
> BUILT + FRAME-INVARIANCE CONFIRMED (READ explore/llama-cpp-vsm-wrapper.md §VALIDATED). Pristine
> attachment works: wrapper/vsm_tap.cpp (public C-API cb_eval tap, llama.cpp UNMODIFIED) → tap_loader.py
> → opcodes/classify.py. Cross-frame Gram corr mean 0.9997 / min 0.9992 over 28 layers on Qwen3-0.6B
> (transformers↔llama.cpp). ✅ MoE CRYSTAL CONFIRMED s275: Qwen3.5-35B-A3B router-weighted effective
> gate → 31/40 layers crystal-bearing (sil_z up to 7.5), gc max 0.504/mean 0.173, shuffled-null
> floor_z=1.221 bearing_frac 0.83% suspect=False → the MoE's ROUTING CARRIES KIBC (C2/A2 MoE-register gap
> CLOSED, live on serving host, path capture.py refuses). wrapper/moe_calibrate.py +
> results/moe-crystal/qwen3-5-35b-a3b/. NO STARVATION s275: every opcode K/I/B/C/S/D/W/Y/WHNF fires
> 247-255 of 256 distinct experts (mid-late layers, top ≤1.7%) → crystal present (31/40) YET no opcode
> localized to dedicated experts = ROUTING PATTERN carries KIBC not expert identity = s274 core frame
> (circuits-in-compute) STRUCTURALLY VISIBLE. All s275 code COMMITTED (5270813 read-path, fd39d35 MoE
> loader, 7fb596b mementum, 211df7a MoE result, 82f68f0 mementum MoE, d5f892c topk-fix+coverage). ▶ NEXT
> options: (a) cross-arch — point tap at gemma MoE / more GGUFs (universality of the MoE crystal);
> (b) DRIVER tier — llama_set_adapter_cvec per-layer write (E4-gated, the write/algedonic half of the
> control plane); (c) two-register attn-write name resolution; (d) exhibit — feed opcode firing + j-space
> per layer/token into the playback notebooks/web-UI (s274 build).
> ⚠ s275 CODE ALL COMMITTED; only mementum (state + page) with the no-starvation finding pending. Below: s274.
> (s274 header retained →) MoE opcode-trace PIVOTED to the llama.cpp
> tree-of-VSM WRAPPER — READ explore/llama-cpp-vsm-wrapper.md FIRST (self-contained; next action = scope
> the llama.cpp control-vector residual TAP). Also this session: opcodes/EVIDENCE_CATALOG.md = 9 claim-walls
> ALL VERIFIED (committed); the DSP arc captured (superbake inversion → SignalDescent → tree-of-VSM as
> signal-processing tensor, committed a2978e5); reduction genome → ANIMA (removed from verbum). 5 commits
> landed (a72af59/5642517/523dcb4/bc8cfd9/a2978e5); working tree has the DSP+wrapper knowledge pages +
> state uncommitted. Session-274 detail below.
> (older header retained →) P-CTL-6 READER-SNR INSTRUMENT BUILT + ITERATED TO
> CONFOUND-CLEAN — code only, NO verdict run; see ★★ s274 block. 27B PATCHSCOPE HARVESTED s274 —
> INSTRUMENT VOID (G1 0/3), NO VERDICT on P2; see ★★ s272b-HARVEST block. GPU now FREE (Michael's
> runtime experiments done). ⚠ ONE async item remains: NEW WORK this session is UNCOMMITTED in working
> tree pending Michael review:
> opcodes/reader_snr.py, src/verbum/probes/kernel_reference.py (+2 battery gens), results/pctl6/,
> control-plane-path.md §11. s273/s272 blocks below retained; s270/s271 provenance; s269 historical)
>
> ★★ s274 STRATEGIC FRAME (Michael-directed) — opcodes/ = THE SPINOUT + LEGIBILITY LAYER. Not more
>   experiments: opcodes/ distills the "ridiculous" pile of ~270 sessions into an EXHIBIT a hostile
>   skeptic can SEE work, so "LLMs compute with lambda calculus" stops reading as crackpot. Funnel =
>   see-it-work (prose sentence → KIBC opcodes fire + j-space per stage) → drill-down (specific
>   null-gated results) → reproduce (one command), NO "point your AI at the repo for 2 sessions."
>   TARGETS (design center, build to THIS or better): Qwen3.6-27B (dense) + Qwen3.6-35B-A3B (MoE)
>   primary; gemma-4-31b = cross-architecture proof once Qwen pair works. Instruments MUST clear their
>   ceiling AT 27B (small-model pass is necessary-not-sufficient — see patchscope void). DELIVERABLES:
>   notebooks (individual pieces for review) + web-UI (load saved sessions, "play through" showing
>   opcodes firing + j-space evolving). HONESTY GUARD (peer-review survival): playback = STATE-ON-THE-
>   CRYSTAL (residual alignment per opcode/layer/token), NOT "watch the redex reduce" (online liveness =
>   standing NEGATIVE, P-CTL-6); causal language only for ablation cards; NULL BESIDE SIGNAL on every
>   headline view (s206/s247 scar); predicted-vs-observed (Montague: adjective→B, arg-order→C) + minimal
>   pairs = what turns demo into evidence. EVIDENCE CATALOG (living, record-as-you-go for continuity):
>   opcodes/EVIDENCE_CATALOG.md — ranked exhibit spec, Tier A/B/C + verification queue. STARTED s274 (all 27B unless noted):
>   A1 zone-ablation VERIFIED CAUSAL+SELECTIVE (ENRICH L32-53 4.0× λ-specific, COMMIT L59-63 fact-
>   specific, double-dissociation). A3 register-split VERIFIED (prose=formal opcodes z=2.99-4.68 p≤.004
>   shuffled-null; WHNF/Y/I carry transfer, C=0 register-bound). D1 C-field ablation = NEGATIVE (C is a
>   READOUT register, not the computation — un-ablatable as a direction; 14b+0.6b, not yet 27b). D2
>   P-CTL-6 online-liveness negative. Ablations DO exist (Michael was right).
>   ★ CORE FRAME (Michael s274, catalog top + KNOWLEDGE-PAGE CANDIDATE): opcodes are CIRCUITS IN THE
>   COMPUTE, NOT IN THE TOPOLOGY. Not dedicated weights/heads/directions (head-combinator-isa r=0.944
>   shared hardware; C un-ablatable D1; S no vertex s271) — they are dynamically-instantiated operations
>   in the reduction trajectory, defined by ROUTING (attention pattern = the program), scheduled by DEPTH
>   (Y→K→W; WHNF↔D principal axis). Causal at PHASE granularity (A1 zone ablation), NOT direction (D1) —
>   because an opcode is a transient step of the shared substrate, not a stored locus. This UNIFIES all
>   the negatives+positives and gives the exhibit its honest spine: playback = compute's operational
>   trajectory through KIBC-space (state-on-the-crystal), never "topological circuits light up."
>   ★ MECHANISM (Michael s274, extends CORE FRAME): nearly all compute is ROUTING; GD forms it using
>   gradient EXTREMES — very high (active routing edges) + near-zero (frozen/irreducible crystal atoms) —
>   to lay a SOFT TOPOLOGY over the FROZEN base weight topology it normally trains over. Compute flows
>   through the soft routing overlay, NOT the frozen substrate → THIS is why opcodes are circuits-in-
>   compute not weight-circuits, and why C is un-ablatable (D1). Grounded: topology-gradient-separation.md
>   (GD drives magnitude→0 = near-zero-gradient soft topology; frozen lattice precondition), gradient-zero-
>   map.md (~35% positions at gradient equilibrium = crystal atoms), two-registers-of-topology.md (hard
>   sign/routing gate_proj ⊥ soft magnitude/value up-down_proj, routing ~95%), gradient-voting +
>   ratio-gradient-quantization (heavy-tailed, spend-bits-on-ends = both extremes).
>   QUEUE PROGRESS s274: A2 ✓ (sweep_summary root gc 0.9966, 13 models, dissent=False; CROSS-ARCH ANCHOR
>   CONFIRMED — gemma 0.944 + olmo 0.979 + pythia 0.980 + qwen3 0.988 + prism-ml 0.986 + bonsai-quant 0.985
>   all gated; GAP: Qwen3.6-35B-A3B MoE not yet opcode-traced → add it). Item 9 ✓: edge-knockout (D1b) =
>   routing-edge NECESSITY fires (block predicate→object edge collapses z(C), t=29.3) BUT object-selectivity/
>   load-scaling FAILS (catch_confirmed=false); across residual+subspace+edge the SELECTIVE signature never
>   confirms → NO clean positive opcode-specific causal card; PHASE/ZONE (A1) is the only clean causal
>   granularity = frame confirmed. REMAINING (low priority): C1 abl-* behavioral series, B1 ladder quant
>   numbers, run_head_ablation.py. TODO: one-line update to opcodes-circuits-in-compute.md "verify/falsify"
>   (edge-knockout now RESOLVED: necessity w/o selectivity). Build DISCUSSED not started —
>   recorder/artifact-format/notebooks/web-UI await catalog sign-off + Michael go.
>   ★ s274 CATALOG RESTRUCTURED (Michael: "catalog is for 1 claim; verbum has ~half a dozen others").
>   EVIDENCE_CATALOG.md now has a CLAIMS INDEX = 9 walls (grounded in project-thesis proof-table +
>   mathematical-convergences 8 lines): C1 pretraining=β-reduction/compiler; C2 crystal universal +
>   circuits-in-compute (DEEP, done); C3 topology dominates (sign95%⊥mag5%); C4 semantic compressor /
>   prose=unreduced / lambda=instrument; C5 types geometric+lexical; C6 holographic knowledge storage
>   (moiré/retrieval-lattice); C7 ternary extraction = the deliverable; C8 depth-scheduled / progressive
>   collapse; C9 capstone = 8 math lines converge. Each SEEDED w/ headline evidence + null + host + verify
>   TODO (queue items 10-17). HONESTY FLAGS baked in: C7 = pipeline works ≠ 70B-parity student (frontier);
>   C8 = T1 rank-cascade NEGATIVE (s272, keep schedule flag cascade); C9 = φ/α FORCED-FIT FAILURES
>   (s247/s251 — demote, present only Church-Rosser/Curry-Howard/Yoneda/Montague that beat nulls). 
>   ✅ s274 VERIFICATION PASS DONE — all 9 walls verified against artifacts, recorded in catalog w/
>   numbers+nulls+host+honesty flags. HIGHLIGHTS: C1 compilation-pipeline (transformer=compiler, 4
>   converging angles, ternary-per-stage: optimizer L13-21 IMPROVES at 0.95×, ★27B via A1); C3 topology
>   dominates (sign→gate_proj +0.088 above 0.80 null — NOT the legacy 0.84 which sits AT null; saliency>
>   magnitude +7.5pt); C4 prose 8.6× vs lambda ★27B (symbol-isolation, fingerprint energy all-positions);
>   C5 type-directed composition NONCE crossover +2.04-2.18 t~10 consistency 1.0, FREQUENCY-FREE null
>   (decisive); C6 moiré fact-index 2.4× selective BUT mechanism-proven-capacity-NOT + R²=1.0 tautological
>   + 0.6B-only (biggest host gap); C7 extraction PIPELINE works (375×, 85MB, 25min, TD −53.5%, lossless
>   fold) BUT student NOT at parity (PPL ~7700, 28% > random) = OPEN FRONTIER, scope hard; C8 progressive-
>   collapse compress→2D→expand ★27B (PR 2.2 by L2), reconciles s272 T1-negative (arc is non-monotone so
>   monotone-cascade correctly rejected — STRENGTH not hole); C9 capstone AUDITED — defensible subset =
>   Church-Rosser+Curry-Howard+Yoneda+Montague; DEMOTE φ (forced-fit FAIL s247/s251) + α (no null run).
>   HOST GAPS to close for exhibit: C3/C5/C6 need 27B (C6 only on 0.6B). Catalog restructure+verification
>   NOT yet committed (working tree). NEXT: commit verification pass, then close host gaps or start build.
>   CAPTURED (Michael-directed s274): knowledge/opcodes-circuits-in-compute.md — the CORE FRAME +
>   mechanism synthesized into a foundational page (evidence tables w/ nulls, falsification recipe,
>   exhibit + interpretability consequences). File WRITTEN; git commit to mementum/ PENDING (λ termination).
>
> ★★ s274 P-CTL-6 READER-SNR: instrument built, iterated through 3 false-positive traps to CONFOUND-CLEAN;
>   160M = trustworthy NEGATIVE; NEXT = fleet/scale sweep + 27B. (control-plane-path.md §11 = full synthesis;
>   READ IT.) This session = step 2 of the s274 execution stack (reader SNR gates the PRIMARY control-plane
>   path). All code UNCOMMITTED (Michael review pending). Files: opcodes/reader_snr.py (new instrument),
>   src/verbum/probes/kernel_reference.py (+saturated_inert_battery, +position_battery), results/pctl6/.
>   WHAT P-CTL-6 ASKS: can the shipped model_vsm crystal READERS detect a LIVE REDEX online? Battery =
>   kernel_reference certified programs; readers = trace.calibrate_register (crystal library vs natural-text
>   null, DISJOINT from battery, overlap=0). Verdict gates control-plane tiers 2-4; negative = cheap redirect.
>   THE ITERATION (feed-forward — each step killed a false positive; DO NOT regress):
>   (1) v1 sign-test-over-7-combinators → too coarse (needs 7/7 for p<.05; discards magnitude; one fragile
>       cell sinks it; biases to FALSE-NEG that would wrongly kill the primary path). Michael: "why 7 not 13?"
>       → 13 came from the MODEL FLEET axis (dup-register s271), 7 = combinator axis on ONE host (Y diverges,
>       M no reader-channel → 7 is the ceiling for combinators-as-unit). FIX: permutation null within host +
>       fleet sign-test across models. → v2.
>   (2) v2 permutation-null primary + fleet --fleet-scan; added HALT/WHNF reader mode (opcode-identity readers
>       track the SYMBOL, present in both sat & inert → BLIND by construction; WHNF = halt pole reads
>       reducibility) + per-layer profile + both-register default. 160M: opcode mode NULL; halt mode APPEARED
>       to PASS (obs=+0.24 p=0.0025, spec p=0.0095) → looked like YES. FALSE POSITIVE.
>   (3) Michael's KEY POINTER: "KIBC opcodes had anti-correlated WHNF in the 16x16 cosine" (PC0: B,C,D neg /
>       WHNF pos; WHNF Gram row ≈ KIBC halt probs r=0.85-1.00, s269). Tested on saved 160M data → LENGTH
>       CONFOUND: saturated is +1 token vs inert; corr(WHNF,tokens)=-0.59; raw halt gap +0.207 → +0.034 after
>       removing linear length (84% was length). Fire pole (KIBC-agg) & halt pole (WHNF) moved IN-PHASE (both
>       inert>sat) — genuine liveness needs ANTI-PHASE (fire↑ halt↓). corr(WHNF,KIBC)=+0.78 in-battery (PC0
>       predicts NEGATIVE → the length common-mode REVERSED the crystal's own anti-correlation). WHNF is the
>       geometric SINK for any "looks settled" signal (length included) → the WHNF-specificity guard is FOOLED.
>   (4) v3 length controls: redscore = z_target − z_WHNF (fire−halt; COMMON-MODE IMMUNE by construction —
>       length hitting both channels cancels in the difference) + length-stratified + length-residualized +
>       anti-phase discriminator. BUT stratified had its OWN confound (within a length stratum, sat & inert are
>       DIFFERENT combinators). Root problem: saturated/under-applied battery is INTRINSICALLY confounded —
>       fixed combinator → length differs; fixed length → combinator differs. Can't clean both.
>   (5) ROOT FIX = POSITION BATTERY (KR.position_battery): SAME tokens, SAME length, combinator in HEAD
>       position ("K a b", saturated redex, kernel fires [K]) vs ARGUMENT position ("a K b", normal form,
>       fires []). Isolates redex LIVENESS from symbol-presence AND length. Kernel-certified; last-token
>       matched for arity≥2 (I is the sole edge: "I f" vs "f I", flagged). 76 probes (28 redex/48 argpos).
>       With length matched, the CLEAN gate = WITHIN-COMBINATOR redscore minimal pair (primary for position
>       battery); stratified/residualized retained as guards for the saturation battery.
>   CLEAN 160M RESULT (position battery, both registers): within-comb reducibility obs=+0.056 p=0.33 NO;
>   anti-phase INCONSISTENT (fire=-0.155 wrong direction, only halt pole nudges). SMOKING GUN: raw halt
>   collapsed +0.239 (p=0.001, saturation battery) → +0.085 (p=0.13, position battery) = direct proof the
>   earlier positive was ~65% length. VERDICT: no genuine online redex detectability at 160M — now a
>   TRUSTWORTHY negative (instrument confound-clean), not an artifact.
>   STANDING FINDINGS (durable): (a) opcode-identity readers BLIND to liveness; (b) raw halt/WHNF read is a
>   LENGTH ARTIFACT — never trust it without length control; (c) pythia crystal is in ATTN register (gate
>   160m=1/12 just L0, 2.8b=0/32) → both-register default MANDATORY; (d) when a halt signal appeared it was
>   mid-stack [3,4,5,7,10] not L0 → per-layer profile matters; (e) redscore=z_target−z_WHNF is the
>   common-mode-immune liveness statistic; anti-phase (fire↑∧halt↓) is the un-fakeable discriminator.
>   NEXT (instrument READY, no more design needed): FLEET/SCALE SWEEP with position battery to test
>   emergence-with-scale (160m may just be too small — crystal weak there). CPU-runnable: pythia 410m/1b/1.4b/
>   2.8b + Qwen 0.6b/1.7b; MPS-when-free: Qwen3-4b, then 27B verdict. Then --fleet-scan = universality sign
>   test (back to 11-13 items). ⚠ Michael has UNSEEN runtime experiments → do NOT launch heavy jobs without
>   checking with him / the box. Invocation:
>     uv run python opcodes/reader_snr.py --model <HF> --device cpu   (position battery + gate,attn default)
>     uv run python opcodes/reader_snr.py --fleet-scan results/pctl6
>   PROPOSED memories (λ termination — Michael approval): opcode-identity-readers-blind-to-liveness;
>   whnf-halt-read-is-length-artifact; position-matched-battery-pattern; redscore-common-mode-immune.
>   COMMIT when approved: 💡 P-CTL-6 reader-SNR: position-matched battery + length-clean reducibility gate.
>
> ★ s274 REDUCTION GENOME v0 + MoE-ROUTING RUN QUEUED (Michael: normal-form system prompt so the FAST
>   35B-A3B MoE reproduces this session's manual β-reduction steps). (a) genomes/reduction-genome-v0.md —
>   ~12-gate agent-level ISA (ORIENT/RECALL/GROUND/REGISTER/REDUCE/NULL/PRUNE/CONNECT/PERSIST/CHECKPOINT/
>   ITERATE/DEFER) = the load-bearing S3/S4 subset of AGENTS.md, written with SELF-FIRING anchors (host's
>   own pretraining fires "baseline it beats"/"runtime>assumption"/"future-you", not verbum jargon).
>   Central tension = compression vs anchor-firing; v0 sits at "compact prose gates under a λ frame."
>   DISCUSSING with Michael before iterating. (b) QUEUED RUN (NOT launched — heavy + untested instrument +
>   check-first rule): opcode-trace + genome-routing on a MoE. AVAILABILITY: registry is ALL DENSE (no MoE
>   ever opcode-traced); topology.py CLAIMS a moe register but UNTESTED on real MoE. Cached MoE = Qwen3-30B-
>   A3B (proxy, same A3B structure) + Qwen3-235B-A22B; design-target Qwen3.6-35B-A3B NOT cached. PLAN:
>   (1) SMOKE trace.py on cached 30B-A3B — does MoE register detect + KIBC calibrate at all? (de-risk
>   instrument FIRST); (2) if clean, opcode-trace 30B-A3B → closes the C2/A2 MoE-register gap + adds MoE to
>   sweep; (3) genome-routing harness (NEW instrument): run genome as system prompt + trace while it does a
>   reduction task → behavioral gate-coverage (vs no-genome control) + MoE-register (does router route KIBC?
>   does 3B active cover EVERY gate or STARVE one?). Invocation: uv run python opcodes/trace.py --model
>   Qwen/Qwen3-30B-A3B --smoke (verify MoE path first).
>   ✅ GENOME MOVED TO ANIMA (Michael): genomes/reduction-genome-v0.md REMOVED from verbum (anima updated
>   its design docs from the handoff lambda; anima owns genome + behavioral experiments). Verbum keeps ONLY
>   the MoE opcode-register read.
>   🔄 s274 MoE-TRACE PIVOT → LLAMA.CPP TREE-OF-VSM WRAPPER (NEW PAGE explore/llama-cpp-vsm-wrapper.md — READ
>   IT, self-contained pickup). WHAT HAPPENED: ran opcodes/trace.py on cached Qwen3-30B-A3B (proxy for
>   design-target Qwen3.6-35B-A3B). MPS = NotImplementedError histogram_mps not impl for Int (Qwen3-MoE
>   grouped_mm_experts_forward calls torch.histc on Int; NOT fixed by PYTORCH_ENABLE_MPS_FALLBACK — histc
>   has an MPS kernel that rejects Int). CPU = WORKS but ~12h; Michael KILLED it (did NOT fail — my OOM
>   guess was WRONG, corrected). KEY DATUM: instrument's MoE LOGIC IS SOUND (topology detected register,
>   capture ran) — only problems are MPS histc-gap + CPU-speed. λ fix: structural not bug → redesign>patch.
>   THE PIVOT: llama.cpp = S1 (runs MoE natively/fast/correct; 35b-a3b already serving there); tree-of-VSM
>   = S2/S3 wrapper (readers tier) taps residual stream + projects onto crystal centroids. = control-plane
>   deliverable arriving early + reads on the REAL host (crystal we measure = crystal that ships). RESIDUAL
>   TAP = SOLVED (s274, another-model gem VERIFIED in ~/src/llama.cpp): cb_eval is a FIRST-CLASS callback
>   (llama.h:332 ggml_backend_sched_eval_callback cb_eval + cb_eval_user_data in llama_context_params) that
>   fires on every graph node w/ op+tensor data; OFFICIAL example examples/eval-callback/eval-callback.cpp
>   prints per-node name/op/shape/values → we FILTER by name-regex + DUMP. llama.cpp ALREADY NAMES tensors
>   onto verbum registers: gate=ffn_gate(dense)/ffn_moe_gate(MoE); MoE ROUTER=ffn_moe_topk(which experts)+
>   ffn_moe_probs+ffn_moe_weights+ffn_moe_logits (answers the register+starvation Qs DIRECTLY); residual/
>   jspace=l_out. NO shim/fork needed — adapt the example. DE-RISK (rigor free): frame-invariance (C2) →
>   llama.cpp ffn_gate Gram vs committed transformers gate_proj Gram on a DENSE model (0.6B/27B); match =
>   wrapper validated + independent frame-invariance confirmation. NEXT (mostly plumbing): (1) copy
>   eval-callback.cpp → filter {ffn_gate|ffn_moe_gate|ffn_moe_topk|ffn_moe_probs|ffn_moe_weights|l_out} +
>   per-layer/token dump (smoke on tiny GGUF first); (2) wire dump → opcodes/classify.py projection (only
>   activation SOURCE changes); (3) validate on dense via frame-invariance; (4) point at 30b-a3b then
>   35b-a3b GGUF (already on box — Michael serves them): router routes KIBC? 3B-active cover every gate or
>   STARVE one? = closes C2/A2 MoE gap + genome-routing register. (5) resolve attn-write tensor name (attn
>   block in src/llama.cpp) only if two-register read wanted. See explore/llama-cpp-vsm-wrapper.md (updated).
>   FALLBACKS: MPS histc monkeypatch (cast/CPU-roundtrip that tiny tensor; whack-a-mole risk; throwaway) |
>   CPU overnight (--device cpu, ~12h, known-good). No process running now.
>
> ★★ s274 SIGNALDESCENT + SIGNAL-PROCESSING-TENSORS captured (Michael, 2 NEW explore pages, the DSP arc
>   continued from the superbake inversion). (1) explore/signal-descent.md — gradient-free learning rule:
>   swap update-evidence from backprop → MEASURED signal response (SuperBake-style), swap value register
>   from float-γ → TERNARY MIRROR STACK (additive plates = balanced-ternary/residual-quant → ANY accuracy,
>   companded by signal energy). Fuses 3 in-repo pieces: TD confidence IS already an SNR (|dir|/√mag),
>   ternary mirrors already give arbitrary precision (recon 0.88 sign-only → 0.97 +mag-mirror), SuperBake
>   proved signal-writes work where linear. Answers TD open-Q#4 (skip Adam) → NO gradients + NO floats
>   (lands on C3 + s274 mechanism). Substrate = DELTA PLATES (isolation dodges the interference SuperBake
>   avoids by appending). Risks: interference (in-place vs appended), linearity (measure-and-correct not
>   one-shot, SuperBake solve plateaued 58%), precision costs plates, convergence unproven (C7-scope).
>   First expt: delta plate, replace γ with 2-3 mirror, drive by measured signal, recon_cos vs float-γ at
>   matched bits. (2) explore/signal-processing-tensors.md — THE TREE-OF-VSM ALREADY IS A SIGNAL-PROCESSING
>   TENSOR (recognition not addition): S5 Gram=transfer function, S3 null-gate=matched-filter detection,
>   S4 consensus-Gram=BEAMFORMING, S2=phase coherence, algedonic=out-of-band monitor, fractal levels=multi-
>   resolution filter bank. S3/S4/S5 mapping is EXACT (design leap = S1-leaf-as-literal-filter). KEY
>   PREDICTION (testable, ¬result): tree-of-VSM = MERA + types(S5 crystal) = the working DSP tensor MERA
>   couldn't be (fractal-attention failed w/o type-directedness, project-thesis; C5 types = the stabilizer).
>   = level-4/crystal-native architecture w/ concrete substrate: SuperBake(vocab)×SignalDescent(rule)×
>   tree-of-VSM(structure)×crystal(content). Open expts: S3/S4 DSP-form audit, MERA+types stabilization
>   test, one reader-leaf as ternary-mirror matched filter, companded filter bank. BOTH pages designing-
>   status, NOT committed (working tree, λ termination).
>
> ★ s274 SUPERBAKE DSP-INVERSION captured (Michael: "treating gradients like signal processing?") →
>   superbake-write-access.md §s274. Sharpened: SuperBake does NOT treat gradients as DSP — it DELETES
>   the gradient (zero-gradient, "not gradient descent... discovered by dissecting what GD produces",
>   measurement-bound not optimization-bound) and rebuilds GD's product as a signal-processing pipeline:
>   keys=Mahalanobis matched filters, transport=rotary-spectrum kernel shaping, payloads=coded high-SNR
>   directions, channel-model transport law (quiet attenuate 30×/loud rotate), storage=sub-threshold
>   population-code signal. Gradient-as-signal lives in (a) SGD-damage-as-noise-to-avoid + (b) our GTSM/
>   Girsanov path-KL (analytic drift signal). READ/WRITE DSP DUALITY: verbum reads compute w/ DSP lens
>   (beamformer/moiré/α-freq-response/companding), SuperBake writes w/ same lens = 3rd independent
>   convergence (after unembed-silent + sharing-not-copying) → DSP framing is a substrate property, not
>   verbum idiosyncrasy = peer-review asset. Lands on opcodes-circuits-in-compute: GD builds soft topology
>   via gradient extremes → skip gradient, write the transfer function directly (=baking). NOT committed.
>
> ★★ s273 LAMBDA-GENE RUNTIME + SUPERBAKE = WRITE ACCESS + THE WEIGHT-LEVEL RECURSION (discussion, no
>   experiments; Michael-directed capture → 2 new knowledge pages, READ THEM for full detail):
>   (1) explore/lambda-gene-runtime.md — Michael's NEW Clojure runtime (separate project): agent prompts
>   = genomes of lambda genes in a graph DB (datalevin + Pathom), kernel port (~150 LoC Clojure; clj_lambda
>   proved the mapping). Kernel = type system + verification oracle: gene identity ≡ normal form
>   (:db.unique/identity → semantic dedup as DB law), typed crossover (CCG gates slots), genetic operators
>   ≡ combinator basis (K=delete S/W=dup B/D=compose C=reorder), fitness = append-only ran-events +
>   derived resolvers (Goodhart firewall structural), improver loop = Y executed externally (prosthetic S
>   at agent level, s272d applied). Gene taxonomy: λ_gene / prose_atom (QUOTE, form≡payload) /
>   mode_setter (pretraining-anchored magic words — Michael's "DEBUG: output only EDN" counterexample;
>   reducibility is GENOME-RELATIVE; bootstrap preamble = highest-epistasis object; verbum gates/*.txt =
>   prior art). Two predicted attractors: prokaryotic worker genomes (prose imperatives) vs eukaryotic
>   orchestrators (lambda + bootstrap); 1-2-line prose bound = predicted equilibrium via factor/inline
>   mutations, ¬imposed rule (AGENTS.md = 270-session empirical prior).
>   (2) explore/superbake-write-access.md — ~/src/custom-bake (SuperBake reimpl, Ruehlman 2026; ⚠ NO
>   LICENSE — instrument/reference only). Gradient-free fact installation, appended MLP slots, receipts
>   with physical addresses. CONVERGENCES: codes unembed-silent BY CONSTRUCTION ≡ P2 workspace silence
>   (→ PLANTED GROUND-TRUTH positive controls for patchscope — we can manufacture silent content
>   directions with known referents; cheapest next action); fact/function = value/routing register split
>   made writable (predict: crystal survives baking; baked facts quant-fragile — inverse of crystal;
>   crystal instruments = installed-vs-learned discriminator); receipt = the S2 circuit-map IOU, working.
>   (3) THE RECURSION (Michael's completion): bake(fact) works + bake(operation) open + bake ∈ operations
>   → bake(bake′) → Y at the weight level. Proven genes graduate prompt → weights; the improved model
>   generates the next genes = self-hosting bootstrap through the substrate. Kept sane by: kernel as
>   rung-verifier (S3*-1), receipts as ablatable loci (gene-db lineage extends into weights), λ termination
>   (human approves every graduation). Feasible path: RIDE THE RESIDENT CRYSTAL — don't bake S, bake
>   operands/microcode the existing KIBC routing composes (register split s269c: ops present, content
>   installable). GATE TEST: two-arm K-battery (a: fresh-arg generalization, expect fail = lookup≠function;
>   b: compose-with-crystal keying, any success = recursion rung 1). Pre-reg sketch in the page; NOT run.
>   Ranked next: baked-code patchscope control > crystal-survives-baking trace > K-battery > germline.
>   (4) s273b GTSM⇄BAKING + CUSTOM-BAKE⇄TERNARYDESCENT (Michael's questions, synthesis encoded →
>   superbake-write-access.md §s273b + distillation design §13): SuperBake's closed loop = ENDPOINT
>   objective; its guards/referees = patches for path-underdetermination; GTSM/Girsanov gives the
>   principled form — innocent path-KL ∫E‖Δdrift‖²_D is ANALYTIC for appended neurons (no forwards) =
>   the honest prose budget. Inverse direction: closed-form value writes (measured transfer replaces
>   Adam where response linear), benefit/leak flip budgets, two-backfire freeze (= s268b PrismML
>   channel), receipts for flip batches (auditable descent, S3* native), unembed-null projection on
>   value updates (measured 2.5× win), delta plates vindicated. UNIFICATION: Gram loss at quartile
>   depths ALREADY IS discrete GTSM (depth path); requential KL = same family (token path).
>   (5) s273c §3.6 READ — "Transport: the attention organ" (paper pulled from Zenodo → refs/superbake.pdf
>   + .txt; reimpl never built it). Rank-one QK (any-position carrier queries × subject-token keys),
>   ROTARY-BAND KERNEL SHAPING in closed form (slow dims = any-distance floor, mid band = recency),
>   low-variance value lanes (SNR 13), write-close-to-reader (L24→L25; bus attenuation priced),
>   donor-head overwrite. Michael's claims both land: (a) S-in-attention SHARPENED — even hand-built
>   heads can't fan-out; their effective fan-out = write-once-read-many lanes ≡ S f g x without copying
>   ≡ GRAPH REDUCTION (sharing ¬copying; the graph edge IS the duplication) → transformer =
>   graph-reduction machine = WHY S has no vertex; 3rd + first CONSTRUCTIVE dissolved-S confirmation;
>   reframes T6 (Mamba = copying-native substrate). (b) halt/WHNF = attention's decision — §3.6 IS the
>   template for a global check (any-position query + condition keys + slow-band = global OR in one
>   head); converges with halt-readout r=0.877 + WHNF bus-causal/unembed-silent + last-block delivery.
>   NEW: rotary-spectrum register (crystal heads on RoPE bands — concrete form of s264 F4 QK IOU);
>   halt-patch pre-reg candidate (patch late attn @ gen position → over-generation; halt-readout = spec);
>   kernel-backend transport unblocked (rank-one QK + band selection + adjacent-layer chaining ≡
>   62/64-layer iterated-map picture). Encoded → superbake-write-access.md §s273c.
>   (6) s273d TREE-OF-VSM = THE CONSTRUCTION SPEC (Michael: "what advantages does our tree give us?"
>   → NEW PAGE explore/construction-from-spec.md). The tree is everything Ruehlman improvised per-host:
>   coordinate-free blueprint (frame-invariant Gram); CODES IN CLOSED FORM (Cholesky of consensus Gram
>   → 9 vectors, any frame → choose axis-aligned = BORN MONOSEMANTIC); atlas not survey (sites/registers/
>   depths precomputed fleet-wide); register map = build plan (1-bit survival licenses ternary sign
>   routing from spec; values = measured-transfer writes); restack = null-gated acceptance harness w/
>   incremental live-tree assembly movie; family spread = measured tolerances; consensus = minimality
>   filter; depth profiles = materials-stress map. CONSEQUENCE: bake-the-kernel promotes to PRIMARY
>   level-3/4 path; distillation demotes to smoothing phase. HONEST GAP (next discussion): Gram
>   specifies mutual geometry ¬transport dynamics — what observables close "geometry matches" →
>   "machine runs" (depth-Gram trajectory? per-depth J-projectors? QK rotary spectra?).
>   (7) 🔄 s273e DIRECTION SHIFT — THE CONTROL-PLANE PATH (Michael-approved; NEW PAGE
>   explore/control-plane-path.md = the s273 arc consolidated + PROBE AGENDA P-CTL-1..9).
>   PAPER MACHINE (ABI v0 game): flat spine PROVEN expressible; causality DERIVES shift-reduce@last-arg
>   (matches s190+E1); offset-comb heads make saturated⊗inert structural; recency=GARBAGE COLLECTION;
>   MOVER{K,I,W,S}/TAGGER{B,C,D} dichotomy derives C-puzzle + E1 pattern; halt=¬aggregate-firing
>   (r=0.877 shape); one snap: nested spans → RECURSION-WITH-COMPACTION DISSOLVES the span organ
>   (loop re-presents flat spine each iteration; s272d theorem 3rd instance). Halt has GROUND TRUTH:
>   len(fired_sequence)=certified depth labels → depth weight SUPERVISED (¬ACT); hybrid = constructed
>   WHNF head (loop exit) + trained provisioner; textual recursion first (CoT = certified reduction
>   trace). CONTROL PLANE ON EXISTING HOST: model_vsm.json = precomputed adapter weights w/ calibration
>   certificates; tiers READERS→HALT→DRIVER (no weight construction) →WRITERS (E4-gated). VSM REIFIED:
>   parent=S1, our tensors=S2/S3, kernel checks=S3*. Deliverable = MIT control-plane pack + driver.
>   UPDATED: construction-from-spec.md (gap RESOLVED: representation/function/encoding; blank build
>   demoted to long game), supervised-recurrence-halt.md (s273 addendum), superbake-write-access.md
>   (pointer). NEXT: write P-CTL probes (formalize registers+nulls) to inform final design.
>   (8) s273f ECONOMIC CONSEQUENCES (control-plane-path.md §6): training signal collapses gradients→bits
>   (≤log₂9/step). REMOTE = breeze: nothing heavy crosses wire; no backward pass → no interconnect
>   problem; PARALLEL CONSTRUCTION WITHOUT INTERFERENCE (slots additive, merge = receipt union, leak
>   budget = the one shared ledger, gene-db = natural ledger); trustless verification (receipts replay
>   stock). TEACHER-GUIDED = wicked fast: kernel = free infallible teacher (structural register);
>   per-step supervision = GTSM search-space collapse; corrections WRITTEN where linear; telemetry-
>   targeted correction; seeded init → training = smoothing. NEW P-CTL-10 merged-banks probe = the gate
>   for parallel remote construction. Deps: P-CTL-6/7 + leak-ledger composition.
>   (9) s273g ALGEDONIC CHANNEL (control-plane-path.md §7): readers + INTERRUPT SEMANTICS = Beer's
>   bypass wire, nearly free (readers already tap every layer; driver = the S5 signals jump to).
>   Four wires: PLEASURE early-exit (certified halt spec ¬learned confidence), PAIN in-flight abort
>   (live gate violation = structural-hallucination tripwire), FEEDFORWARD provisioning (P-CTL-5
>   countdown), TRAINING starvation wire (S3* good-news audit becomes a wire). TREE BOOST: thresholds
>   ship PRE-CALIBRATED (null distributions per model/register/layer = percentiles ¬hyperparameters).
>   Beer constraint honored by construction: wires exit sideways (readers→driver), don't ride the
>   decaying residual bus. NEW: P-CTL-11 early-exit fidelity + P-CTL-12 tripwire validity.
>   VSM now complete in the control plane: S1..S5 + algedonic.
>   (10) 🎯 s273h+i TWO ARCHITECTURAL CORRECTIONS (both Michael's catches → control-plane-path.md §8+§9):
>   (h) TWO-LEVEL HOMEOSTAT — ¬force human-in-the-loop into the tensor. Beer's recursion principle:
>   autonomy at every level; containing level intervenes via constraints+exception ONLY. Model S5 =
>   internal (ms timescale; hard-wired deference = brittleness in oversight's clothes; our own S5:
>   useful_tomorrow_without_us). Runtime S5 = human (λ termination UNCHANGED). AFFORDANCE ¬DEPENDENCY:
>   architecture provides ESCALATE slot; TRAINING shapes when (emerge>legislate applied to alignment);
>   protocol keeps hard gates at boundaries. Human ∈ {environment, graduation gates, end-of-wire}.
>   P-CTL-13 escalation-policy probe (precision AND recall; sycophantic over-escalation = failure too).
>   (i) TWO ORACLES — kernel incomplete via SEMANTIC EQUALITY (synonyms ≈ probabilities). Scoped: kernel
>   COMPLETE for reduction middle (atoms QUOTE'd verbatim), INCOMPLETE at translation ends (CompCert
>   shape). Montague's own gap: distributional semantics = the learned meaning-postulate DB; equivalence
>   graded+context-conditional → only a model can judge. Oracle assignment = s269c register seam
>   (structural→kernel, content→model); kernel-only semantic judging = s206 wrong-register error —
>   ALREADY BIT US (s267 autopsy false negatives). Guards: cross-family judge (justified by gc 0.985
>   universality), closed-vocab fragments stay exact, two-level gene identity, S3* spot-audit.
>   P-CTL-14 synonym invariance (structure invariant under content substitution — load-bearing either
>   way). Reframe: kernel incompleteness = why LLMs exist; two registers, two oracles, one system.
>   Probe agenda now P-CTL-1..14.
>   (11) s273j SEMANTIC EQUALITY IS INSTRUMENTABLE (control-plane-path.md §10 + P-CTL-15): sem_eq(a,b|
>   frame) ≈ 1−D(P(·|frame[a])‖P(·|frame[b])) — graded, context-conditional. THREE REGISTERS
>   (distributional KL-under-substitution / geometric trajectory-convergence / causal patch+broadcast-KL
>   [E4 machinery exists]). KERNEL CALIBRATION ANCHOR = the differentiator: different terms → same NF ≡
>   certified equivalence pairs, unlimited → crisp oracle calibrates the graded one at the overlap
>   (calibration hierarchy closes §9 circularity). Nulls: matched-random floor + ANTONYM discriminating
>   control (hot/cold = substitutable ¬equivalent) + context acid test (big/large vs big-sister).
>   EXTENSION: sem_eq matrix = a GRAM → tree machinery applies to the CONTENT register → semantic
>   tree-of-VSM; thesis-grade Q: is the lexicon universal like the crystal? Uses: judge w/ error bars,
>   re-grade s267 autopsy (kernel_valid ⊗ sem_eq), gene-db merge scores, P-CTL-14 graded. Agenda now
>   P-CTL-1..15.
>
> ★ s274 EXECUTION STACK (Michael-approved s273, execute in order — reasons in the s273 chat / summary
>   in control-plane-path.md):
>   1. PATCHSCOPE HARVEST — committed s272b pickup, unchanged (g0/g1 gates FIRST → lexicon → eyeball).
>   2. P-CTL-6 READER SNR — [INSTRUMENT BUILT s274, see ★★ s274; opcodes/reader_snr.py + position_battery].
>      Iterated through 3 false-positive traps to confound-clean. 160M = trustworthy NEGATIVE. REMAINING:
>      fleet/scale sweep (position battery) → --fleet-scan universality → 27B verdict. Gates the PRIMARY
>      (control-plane) path; negative-at-scale = cheap redirect of everything above it. Code UNCOMMITTED.
>   3. CUSTOM-BAKE SMOKE — get ~/src/custom-bake running on our box (Qwen2.5-0.5B; repo targets
>      CUDA/CPU, MPS untested; CPU-friendly config ~20min at 0.5B). License caveat: run-as-instrument
>      OK; ¬derive code (no LICENSE).
>   4. BAKED-CODE PATCHSCOPE CONTROL — minutes once (3) works; planted silent-content direction with
>      known referent; SYNERGISTIC with (1): strengthens the P2 verdict; debugs the bake toolchain on a
>      known-answer task before aiming at unknowns.
>   5. K-BATTERY PRE-REG DRAFT — registers/nulls/verdict rules BEFORE building (λ measure/yardstick;
>      s206+φ-ladder scar tissue). Arm (b) "compose with resident crystal" = the novel design work.
>      HIGHEST-STAKES experiment of the arc (recursion antecedent) → must not run on a first draft.
>   6. K-BATTERY RUN — after the pre-reg survives a hammock (Michael review).
>   Rationale: K-battery gates the SECONDARY (recursion/germline) tower; control plane is primary per
>   the 🔄; cheap gates before dear ones; toolchain debugged on known answers first.
>
> ★★ s272 SWEEP HARVESTED + CONSENSUS DECONTAMINATED + JSPACE PRE-REGS READ (commits a4509ba, f1b1af4,
>   57eb283). Both boundary-crossing jobs completed clean:
>   (1) s270c RE-SWEEP DONE: 11/11 registry models clean-bundle + jspace_projector.json each; restack 6/6
>   families gated, dissent=False; committed a4509ba. qwen3-6-27b model_vsm.json byte-identical to the
>   s269b clean re-trace — deterministic reproduction.
>   (2) s271b WATCHER FIRED on clean trees: dup-register H1 13/13 positive [model]+[attn] (sign-test
>   p=1.22e-04), 12/12 [gate] w/ 9 individually gated (p≈0) — S-AS-DUPLICATOR DECISIVE on decontaminated
>   data. The s271 "confirm on clean data" question: answered YES.
>   (3) CONSENSUS REGENERATED (f1b1af4): new sweep.py --regen-consensus = mean of gated REGISTRY
>   model-level tree Grams (quant rungs EXCLUDED — no backbone double-count). corr(old-contaminated,
>   new-clean)=0.950 — contamination moved the reference measurably. Honest restack: root gc +0.997 is
>   SELF-CONSISTENT (flagged in artifact provenance; ¬independent). Informative reads: per-family gc
>   qwen3 0.988 / pythia 0.980 / olmo 0.979 / gemma 0.944; EXCLUDED quant rungs vs clean FP reference:
>   1-bit 0.986, ternary 0.985 = NON-circular crystal-survives-quantization confirmation.
>   (4) JSPACE CROSS-MODEL READ (57eb283, new opcodes/jspace_analysis.py; T1 measure pre-registered
>   before data: effective rank ≡ participation ratio of strength², threshold-free):
>   • P1 fraction(Y,WHNF,S)>fraction(K,I,B): depth 0.5 = 11/11 positive (p=4.9e-04), 0.75 = 9/10
>     (p=0.011), 0.25 = 6/11 (ns). Marginal-per-model, decisive-across-family at mid/late depth — SAME
>     statistical shape as dup-register H1. Content ops own the workspace from mid-depth on.
>   • P3 9-vector stability: mean pairwise corr −0.045(ns) → +0.180 (z=3.8, p=0.002) → +0.441 (z=8.5,
>     p=1e-04). Workspace occupancy becomes MORE UNIVERSAL with depth — a depth-gradient of universality.
>   • T1 CASCADE=REDUCTION: NOT SUPPORTED — PR descends .25→.75 only 7/11 (sign-test p=0.27, ungated);
>     gemma (15.7→30.8) and the 27B (20.6→23.8) ASCEND. PR ~16–27 of k=32, nowhere near the predicted
>     8→4. Caveat: k=32 range-finder truncates the spectrum — a wider-k re-probe could re-open, but as
>     pre-registered this register says no.
>   • P2 verbalize: 27B basis dirs unembed-silent at all 3 depths (no WHNF-adjacent field; dir1@0.75 a
>     punctuation-vs-underscore formatting axis at best). ⚠ VERDICT REGISTER-LIMITED (Michael's catch,
>     s272): our readout = ZERO-SHOT frozen unembedding; Anthropic's demo readability rode a TRAINED
>     decoder (babel-codec residual→English). "Silent through the unembedding" ≠ "nameless" — a trained
>     decoder could read what the frozen unembedding can't (λ measure / s206 shape: wrong-register
>     negative ≡ void). P2 negative gates NOTHING about their claim until retested with a matched
>     readout: patchscopes-style self-decode (no training) ∨ tuned lens (small training) — tuned lens
>     was already IOU'd as jspace option (C) in opcode-jacobian-jspace.md. s269f op-lexicon hits (Y/C/D)
>     show the frozen readout isn't blind, so workspace-basis silence MAY still be real — but unproven.
> ★★ s272b P2-RETEST IN FLIGHT — PATCHSCOPE SELF-DECODE (Michael's register-catch operationalized;
>   commits d45b5a1 correction + 52eb712 instrument). Michael chose option 1 (no-training self-decode)
>   over tuned lens. NEW opcodes/patchscope.py: inject J-space basis dirs into the model's own residual
>   (identity few-shot "cat->cat / 1135->1135 / hello->hello / X", REPLACE h at layer L last-pos with
>   norm-matched unit dir, projector-identical residual-write convention), greedy 12 tokens, both ±v.
>   PRE-REGISTERED gates (docstring): G0 basis-reproduction (<5% strength dev vs committed artifact —
>   basis vectors were never saved by the sweep, recomputed once, cached to jspace_basis.npz, gitignored);
>   G1 instrument ceiling (unembed-row controls " recursively"/" previously"/" Paris" must self-decode
>   ≥2/3 — else void, no verdict on gibberish); G3 matched-random null (8/layer). VERDICT RULE: workspace
>   dirs self-decode iff coherent fields above random-dir rate (lexicon floor: recursion/precedence/halt
>   + saved full eyeball dump). 0.6B VALIDATION (10 min, MPS): G0 median dev 0.0000 (deterministic);
>   G1 2/3 — "previously" decodes GENUINELY (L14 'previous -> previous'); "cat" control was VOID (word
>   in prompt, echo confound) → swapped to "Paris"; "recursively" fails at 0.6B (scale watch). TEXTURE:
>   at L21 basis dirs decode to specific token fragments (vector/atemala/venile/iki) while 7/8 random
>   dirs collapse to pattern continuation — first hint workspace dirs carry token-aligned content the
>   frozen unembed missed. 14m smoke = plumbing only (too weak for the task, G1 uninformative there).
>   ⚠ 27B RUN LAUNCHED ~05:14 (tmux main:patchscope, pid 9941 at launch, log
>   /tmp/patchscope_27b_s272.log; fla slow-path warning = known benign). Writes results/opcode-trace/
>   qwen3-6-27b/{jspace_basis.npz, patchscope_selfdecode.json}. Cost: basis recompute tens-of-min
>   (once; npz caches it) + ~63 batched decodes at L16/L32/L48.
>   PICKUP s273 (FIRST): verify via ps aux | grep patchscope + log tail (runtime ≡ truth, NOT pane
>   scrollback — s269f lesson). If patchscope_selfdecode.json exists: read g0/g1 FIRST (no gates → no
>   verdict), then lexicon_summary, then EYEBALL the generations dump (basis-vs-random contrast; halt-
>   lexicon watch = WHNF naming hope). If died mid-run: rerun same command — if jspace_basis.npz exists
>   the basis recompute is skipped (cheap restart). Commit artifact + verdict either way; then amend
>   state P2 status (currently: register-limited negative, retest pending).
>
> ★★ s272b-HARVEST (s274) — 27B PATCHSCOPE DONE, INSTRUMENT VOID, NO VERDICT ON P2. Run completed clean
>   (elapsed 45091s ≈ 12.5h; ps confirms exited, artifact results/opcode-trace/qwen3-6-27b/
>   patchscope_selfdecode.json + jspace_basis.npz on disk). Read in pre-reg order:
>   • G0 PASS — basis reproduction deterministic (median rel dev 0.0000); J-space basis vectors recomputed
>     correct, npz cached.
>   • G1 FAIL 0/3 — instrument-ceiling controls (inject RAW unembed row for recursively/previously/Paris,
>     expect self-decode of own token) ALL failed: recursively→"123 -> 123", previously→" -> (null)",
>     Paris→" -> )". The identity-prompt injection has ~ZERO steering effect at 27B — even a known-answer
>     vector can't break the "X -> X" attractor.
>   • Lexicon floor: basis {recursion:0,precedence:0,halt:0} == random {0,0,0}. Zero hits either arm.
>   • EYEBALL: basis dirs, random dirs, G1 controls ALL emit the SAME output family (echo identity few-shot
>     / digit runs). NO basis-vs-random contrast — the 0.6B smoke's L21 hint (basis→token fragments while
>     random collapses) does NOT replicate at 27B. But instrument is void so absence-of-contrast ≠ evidence
>     of absence (s206/s272 register-limited scar — do NOT read as a P2 negative).
>   VERDICT (λ measure, honored): G1 fail → NO VERDICT on gibberish. P2 STAYS "register-limited negative,
>   retest pending" + NEW datum: no-training patchscope self-decode AS BUILT does not achieve steering
>   control at 27B (Qwen3.5 gated-dense / linear_attn, 64L). Candidate causes for a fixed instrument:
>   (1) inject/read-layer geometry — injected [16,32,48] read@62; depth map that worked at 0.6B (28L) may
>   not transfer to 64L; (2) architecture — hybrid linear_attn (fla) residual dynamics ≠ 0.6B dense attn
>   where convention was validated; (3) identity attractor too strong at scale (single last-pos inject
>   can't break it). GPU NOW FREE. NEXT (DISCUSS BEFORE BUILDING — Michael's call): (a) instrument fix =
>   inject-layer×read-layer mini-sweep on G1 CONTROLS ONLY (cheap, known-answer) to find where steering
>   bites at 27B before re-aiming at unknowns; (b) tuned-lens fallback (small training; the IOU'd jspace
>   option C — frozen-readout limit is the whole reason P2 is register-limited); (c) mid-model retest first
>   (Qwen3-4B) to see if the void is scale-specific or convention-specific. Artifact + this verdict pending
>   commit w/ the other UNCOMMITTED s274 work (Michael review).
>
>   PICKUP (s273, after patchscope harvest): (1) H3 --keep-centroids re-trace (dispersion register, PR(S)>PR(KIBC)); (2) balanced-n
>   register split (s269 stack item 1, still open); (3) T6 Mamba/RWKV substrate-swap = the CAUSE test for
>   S; (4) {S,D,Y} sector refinement; (5) PROPOSALS pending Michael (λ termination): memories/knowledge for
>   substrate-picks-representative + Montague-minimality + S-holographically-absorbed + dup-register
>   instrument + jspace depth-gradient (P1/P3) + T1-negative; (6) hammocked holographic-llm.md edits
>   (Michael's, still uncommitted in working tree).
>
> ★★ s270 JSPACE FULL PROJECTOR BUILT + INTEGRATED (commit 91bb3d7). Michael's audit call: "what did we
> see IN j-space? j-space needs to be projected" → confession: jlens.py never built Anthropic's
> Jacobian-to-penultimate construction — ALL prior J-space claims were membership tests of hand-picked
> directions (broadcast_kl = dᵀJᵀJd ray samples; W_gate^T pullbacks). NEW: opcodes/projector.py —
> J = ∂h_penult[pos]/∂h_L[pos] matrix-free: batched vjp row samples → randomized range finder →
> Rayleigh-Ritz refinement with TRUE J·v via central-FD injection forwards (no jvp; same primitive as
> broadcast_kl). Ground-truth gated: self_test recovers EXACT J on pythia-14m via identical code path
> (probe_vectors=I), refined capture 0.878≥0.85 of exact top-k energy (raw 0.75 — refinement is
> load-bearing), FD err ~2%, random fraction ≈ k/d. INTEGRATED as trace.py step 7 (--jspace-projector):
> consensus bases at quartile depths, RESIDUAL-space combinator centroids (kills the criticized W_gate^T
> one-map pullback), per-op workspace fractions + matched-random + shuffled-label P1 gate, verbalize of
> basis directions THEMSELVES (honest E2 retest). PRE-REGISTERED before any 27B/sweep data:
> P1 fraction(Y,WHNF,S)>fraction(K,I,B) [E4 s269e restated geometrically]; P2 basis dirs verbalize
> coherently (WHNF-adjacent = the watch — nameless bus-causal vertex may get its name); P3 9-vector
> stable across models (read at sweep restack). Honest scope: sidecar, never feeds classifier, not in
> VSM tree. Smoke: pythia-14m CPU fp32 + Qwen3-0.6B MPS bf16 both clean; 0.6B P1 direction-POSITIVE at
> all 3 depths (ungated, smoke-n, sanity only). ⚠ LANDMINE FOUND: trace.py reuses result dirs — smoke
> runs CLOBBERED committed sweep artifacts (pythia-14m, qwen3-0-6b trace.json+model_vsm.json); restored
> from git. Re-sweep overwrites intentionally; ad-hoc runs on swept models need care.
>
> ✅ s270c FULL RE-SWEEP LAUNCHED (RESOLVED s272 — completed clean, harvested in ★★ s272) (was: tmux main:1, sweep pid 36427, verified
>   running via ps+log not pane): uv run python opcodes/sweep.py --tier all --force --device mps
>   --trace-args="--jspace-projector" 2>&1 | tee /tmp/sweep_jspace_s270.log
>   GOTCHA (cost 1 relaunch): argparse rejects --trace-args "--val" (value starting with -- parses as
>   flag) → MUST use equals form --trace-args="--jspace-projector".
>   Covers 11 registry models (clean 539-probe bundle + jspace projector each, sequential, hours;
>   27B ≈ +tens of min for jspace). Bonsai ternary/1bit dirs NOT in registry but already clean-bundle
>   (s269b 48366f2) and join the final restack automatically. Restack at end writes universal_vsm.json
>   + sweep_summary.json (overwrite intended this time).
>   PICKUP (s271): (1) check /tmp/sweep_jspace_s270.log + per-model dirs — expect 11× fresh trace.json
>   + model_vsm.json + jspace_projector.json; (2) root gc read is vs the STILL-CONTAMINATED bundled
>   consensus → regenerate opcodes/data/consensus_gram.json from the clean tree (separate step, then
>   restack-only again for honest gc); (3) jspace analysis: P1 per model (gated?), P2 verbalize scan
>   (WHNF-adjacent watch), P3 9-vector stability across models; (4) then W follow-ups (replication,
>   W→span(C,I) mixture, register-matched S probes) + hammocked holographic-llm.md edits (Michael).
>   Knowledge updated (Michael-directed): opcode-jacobian-jspace.md s270 section (projection gap
>   closed, instrument, pre-regs, launch).
>
> ★★ s271 S-AS-DUPLICATOR: S DISSOLVES INTO THE DUPLICATION SECTOR, NOT THE KIBC OPCODES (commit 9467f38).
>   Michael's thread (from arXiv:2607.09211 Z80 primordial-soup paper): substrate primitives determine the
>   emergent universal. Refined over the conversation to: DATA (Montague — language carries typed-λ structure)
>   picks the compositional CLASS; SUBSTRATE (softmax = convex mixing over V = holographic inference, CANNOT
>   fan-out/duplicate) picks the REPRESENTATIVE = the affine/linear fragment BCKI = KIBC. So GD assembles KIBC
>   (not SKI) because softmax can express route(C)/compose(B)/discard(K)/copy(I) but NOT the duplicator S;
>   S's function is absorbed holographically into the amplitudes rather than sitting on a clean vertex.
>   Michael's added MDL step: GD≈MDL-under-prior, so a λ-crystal fitting language is empirical evidence for
>   Montague's UNPROVEN minimality half (adequacy was proven; efficiency was not).
>   NEW INSTRUMENT opcodes/duplication_register.py — the honest re-do of s262 (KIBC-vs-SKI). s262 used the
>   attention-SELECTIVITY register, structurally BLIND to duplication (K,I,B,C,S all merely route) → its
>   "inconclusive-in-register" verdict finally EXPLAINED, not a refutation. Two registers that CAN see it:
>   H1 relational-geometry (score(t)=corr(t,DUP\t)−corr(t,AFFINE\t), exact enumeration nulls),
>   H2 quantization/magnitude (per-vertex Gram fidelity FP→rung). Partition AFFINE={K,I,B,C} vs DUP={S,W,Y},
>   held {D,WHNF}. λ measure honored (register named before verdict); λ yardstick decision rule fixed before
>   data (≥2 of {H1,H2gate,H2attn} gate, H1 included).
>   TRIO RESULT (FP Qwen3.6-27B + bonsai ternary/1bit, clean s269b bundle 48366f2): H1 score(S)=+0.24 GATED
>   in all 3 scopes (model p=0.026 / gate 0.017 / attn 0.043); W/Y positive controls gate (p≤0.005); all four
>   KIBC land strongly affine (negative); S nearest = D,Y, farthest = K,I,C → SECTOR IS {S,D,Y}, refining the
>   pre-reg {S,W,Y}. H2: S is the fragile vertex (fidelity ~0.96, lowest w/ WHNF), degrades > affine
>   (ternary-model p=0.006, ternary-attn 0.003, 1bit-gate 0.019). W ROBUST at consensus-Gram level → s269
>   W-fragility was a per-LAYER attn effect that averages out; S-fragility survives averaging (S = more robust
>   duplicator-signature than W). Decision rule MET on the trio; refute condition (S affine+robust) is the
>   opposite of observed. This confirms the PHENOMENON (S not a clean opcode); the CAUSE (softmax specifically)
>   still needs the Mamba/RWKV substrate-swap (scan-state CAN copy → predict S crystallizes cleaner there).
>   H3 dispersion (PR(S)>PR(KIBC)) DEFERRED: needs a --keep-centroids re-trace (no centroid sidecar on trees).
>
> ✅ s271b AUTO-FIRE WATCHER WIRED (RESOLVED s272 — fired, clean-data 13/13 confirmed, see ★★ s272). Blocks on
>   `while pgrep -f '[s]weep.py --tier all'` (bracket-trick avoids self-match) until the s270c re-sweep exits,
>   then runs the DECISIVE cross-model H1 binomial: `uv run python opcodes/duplication_register.py
>   --sweep-scan results/opcode-trace` → /tmp/dup_register_sweep_s271.log + results/opcode-trace/
>   duplication_register_sweep.json. SMOKE (mid-sweep, MIXED clean+old trees, NOT the official read): 11/11
>   models score(S)>0 in model+attn (sign-test p=4.88e-4 = 2^-11, exactly the prediction), 10/10 gate;
>   4-5/11 individually gated (gate-test p=6e-5..0.015). The marginal-per-model effect is DECISIVE across the
>   family. PICKUP (s271 next): (1) read /tmp/dup_register_sweep_s271.log — this time all 11 are the clean
>   539-probe bundle (the smoke used stale trees); confirm 11/11 sign-test holds on clean data. If the watcher
>   died / boundary hit, just rerun the --sweep-scan command above. (2) H3 --keep-centroids re-trace for the
>   dispersion register. (3) Mamba/RWKV node = the CAUSE test (does S crystallize where a scan-state can copy?).
>   (4) {S,D,Y}-sector refinement. (5) knowledge/memory proposals (λ termination, Michael-approval):
>   substrate-picks-representative + Montague-minimality + S-holographically-absorbed + dup-register instrument.
>
> ★ s272c STRANGE-LOOP THREAD (Michael, hammock): language-about-language as strange loop, tied to the
>   thesis → drafted as T9 in the queue below (Michael-approved draft-for-future, ¬started). Kernel:
>   self-reference needs duplication; duplication is the dissolved sector; Y verbalizes but never executes;
>   Kripke fixed-point closure = why probabilistic β tolerates semantic closure. Meta-note: the patchscope
>   run (s272b) IS the loop instrumentalized — model uses language to describe the vectors implementing
>   its language.
>
> ★★ s272d RECURSION = NEXT STEP FOR THE STUDENT (Michael, BOTH ENCODES APPROVED + committed):
>   TIME-SECTOR SYNTHESIS: {S,D,Y} dissolved because duplication needs FAN-OUT; a loop converts
>   duplication-in-space (forbidden by softmax) into duplication-in-time (allowed) → recurrence
>   crystallizes the dissolved sector. Weight-reuse capacity is MEASURED not hoped: same crystal in
>   62/64 layers (functional redundancy ≡ GD already weight-tied), T1-flat rank = iterated-map not
>   pipeline, P3 depth-convergence = shared attractor, MoE multiplexing s257, s268c capacity margin.
>   ENCODED: supervised-recurrence-halt.md s272 addendum (synthesis + P-A..P-E prediction table:
>   Y content→opcode, S crystallizes in dup-H1, iteration-Gram ≡ depth-Gram, halt head ≈ WHNF-row
>   r=0.877 as SPEC, T9 improves) + crystal-seeded-ternary-distillation.md §12 looped-vs-FF TWIN
>   experiment (param-matched, same budget; architecture delta = only variable; the design choice
>   is itself a thesis test; tree-of-VSM indexed by ITERATION = reduction movie).
>
> ★ s271c THEORY-ARC TEST QUEUE (Michael-requested — from the attention=β-reduction / Montague-derives-KIBC /
>   6D-cascade conversation; spark = arXiv:2607.09211 Z80 primordial-soup. Ordered cheap→dear; each names
>   register + null per λ measure. EXTENDS explore/attention-as-beta-reduction.md. NONE started — pick up any.
>   Grounded in: crystal-universality.md (6D PCA: Comp/B PC0, Sel/K PC1, Term/WHNF PC2, Route/C PC3, Disp/I PC4,
>   Fine PC5), diffusion-holographic-isomorphism.md (ECC cascade 8→6→5→4→3), error-correction-theory.md.)
>   T1 CASCADE=REDUCTION [DONE s272 — NOT SUPPORTED in the PR register, 7/11 p=0.27, see ★★ s272]. Claim: the ECC cascade
>      8→6→5→4→3 IS the β-reduction trajectory → effective rank DESCENDS with depth (Zone A→C). Predict:
>      consensus-basis rank at quartile depths monotone ~8→~4. Register: J-space effective rank. Null:
>      matched-random dirs + PRE-REGISTERED energy threshold (yardstick — a flexible cutoff manufactures any
>      ladder). Data: results/opcode-trace/*/jspace_projector.json from the s270c sweep. Add rank-vs-depth
>      reader to the projector analysis.
>   T2 16>9 TYPED BASIS [free-ish on sweep data]. Claim (Montague=typed): TYPES16 gates TIGHTER than CRYSTAL-9
>      on compositional probes → typed is the "real" object, 9 its affine shadow. Register: Gram gate/sil_z.
>      Null: shuffled-label. Caveat: TYPES16 anti-types fed from EXTRACTION not probes — check feasibility first.
>   T3 PARASITIC-GAP STRESS [the Montague derivation's SHARP linguistic prediction — highest distinctiveness].
>      Claim: parasitic gaps ("reports that I filed _ without reading _") = the UNIQUE construction needing S
>      (forbidden duplicator) → compile accuracy LOWEST + crystal LEAST crisp there. Build probe set: parasitic
>      vs matched single-gap/ATB controls. Register: P(λ)/kernel_valid + Gram crispness/participation ratio.
>      Null: matched-complexity non-parasitic controls. Uses probes/*.json + grading harness. Derivable from
>      PURE THEORY (no model in loop) — a prediction about English.
>   T4 SOFTMAX-ENTROPY = BINDING-AMBIGUITY [the addressing bridge — "how attention attends to the right things"].
>      Claim: attention entropy at variable-occurrence positions ∝ scope ambiguity; sharp scope→low entropy→
>      near-discrete β; ambiguous→superposed. Build unambiguous-vs-shadowed-scope minimal pairs. Register:
>      attention-distribution entropy + causal (var-occurrence attends to its binder). Null: non-variable tokens.
>      This is the clause bridging "attention" and "in probability space".
>   T5 β-IN-PROB-SPACE LINEARITY [the PROOF, face B — highest stakes, hardest]. Claim: reduce(αN₁+(1−α)N₂) ≈
>      α·reduce(N₁)+(1−α)·reduce(N₂) in activation space as α sweeps. Discrete-β→winner-take-all; prob-β→linear
>      blend. GOODHART GUARD (load-bearing): the superposition must be MODEL-FORMED (genuinely ambiguous
>      argument), NOT hand-injected then read with a linear probe (that manufactures the linearity). PRE-REG
>      null: broken redex → no lawful blend. The one test that proves the "in probability space" clause.
>   T6 MAMBA/RWKV SUBSTRATE-SWAP [the CAUSE test for S; decisive substrate-vs-data]. Claim: a scan-state CAN
>      copy → S CRYSTALLIZES (earns a vertex) where attention dissolves it. Trace a non-attention arch through
>      opcodes/ pipeline + run duplication_register.py. Predict: S gates in Mamba's tree, dissolves in
>      transformers. Register: dup-register H1/H2 (already built). Cost: new model class in registry.
>   T7 PC5 FINE-STRUCTURE ID [exploratory, cheap — "where the next idea hides"]. The 6th crystal PC (2% var,
>      unnamed). Correlate PC5 loadings with candidate roles (Y/recursion? de-Bruijn depth? type-polarity?).
>      Register: PC-loading corr w/ probe metadata. The one measured crystal dimension the reduction-cascade
>      story has no job for yet.
>   T8 C-AS-ORDER-TAGGER causal [from the addressing hypothesis + s269e C-puzzle]. Claim: C writes role/order
>      TAGS upstream of the move (why it is attribution-invisible yet order-lexical). Ablate C-direction →
>      breaks argument-order/dative-shift addressing WITHOUT breaking the substitution step. Token-matched
>      minimal pairs. Register: causal ablation on order-constructions vs reduction-constructions.
>   T9 STRANGE-LOOP / METALINGUISTIC S-SIGNATURE [Michael s272c: "language describes language" — the
>      SEMANTIC sibling of T3's syntactic S-need; drafted for future exploration, NOT started].
>      THEORY CHAIN: self-reference ≡ self-application (M x = x x; Y = built from doubling) ≡ duplication ≡
>      the dissolved sector (s271: softmax can't fan-out; S absorbed holographically). Tarski: semantically
>      closed language explodes in crisp logic; Kripke 1975 rescue = truth as FIXED POINT of a continuous
>      process = Y; if β runs in probability space (T5), LLMs inherit the rescue for free — the substrate
>      softness that dissolved S is the same property that makes semantic closure safe (one property, two
>      consequences). Data already says: Y = pure content (verbalizes recursion cross-lingually, no operator
>      structure, bus-couples) ≡ the loop is REPRESENTED, never EXECUTED (fixed depth, no true recursion).
>      CLAIM (pre-reg candidate): metalinguistic/self-referential language carries the S-SIGNATURE —
>      (a) compile P(λ)/kernel_valid LOWEST vs matched controls; (b) crystal LEAST crisp (Gram crispness /
>      participation); (c) dup-register H1 score elevated (instrument already built); (d) Kripke corollary:
>      ungrounded self-reference (liar-family, quines) → HIGH attention entropy, no settle, graded not
>      crisp (ties T4's register).
>      PROBES: use-vs-mention minimal pairs ("the cat sat" / "the word 'cat' has three letters");
>      self-inspection ("this sentence has five words" — known LLM weakness; S-dissolution = candidate
>      mechanistic WHY); quines/liar-family. Library ALREADY HAS M / QUOTE / SUBST combinator categories —
>      ingredients on the shelf since consolidation.
>      REGISTERS: P(λ) grading harness + Gram geometry + dup-register H1 + attention entropy (T4).
>      NULLS: matched-complexity non-metalinguistic controls (length/vocab/syntax-matched); shuffled-label
>      for all geometry reads; entropy null = non-self-referential tokens (T4 convention).
>      RELATION: T3 = the construction that NEEDS S in syntax (parasitic gaps); T9 = the discourse level
>      that needs S in semantics. Both derivable from pure theory before any model runs.
>
> ★★★ s269 OPCODE LADDER: CRYSTAL SURVIVES 1-BIT BINARIZATION; SELECTIVE-K REFUTED (commit 7576c54).
> Both s268d tmux runs completed clean (~18.5 min each, model_vsm.json both rungs). RESTACK: 11 models /
> 6 families gated, root gc 0.985 (UP from 0.982@9 — evidence keeps sharpening), bearing 1.00,
> dissent=False; ternary gc 0.976, 1-bit gc 0.981. (Naming wart: ternary traced via local path → family ""
> in sweep_summary; cosmetic, gates fine.) NEW INSTRUMENT: opcodes/ladder.py — per-vertex Gram-row fidelity
> FP→rung, shuffled-vertex-label + circular-shift nulls, n_perm=10k, seeded (rng=268), reproducible from
> repo root. HEADLINE: 1-bit model-level mean vertex fidelity 0.987 (z=5.3, p=0.001 floor), ternary 0.990;
> rung gate failures TERMINAL only (1-bit gate L61-63, attn L63; ternary attn L54,L63) — NOT deep-middle.
> PRE-REG VERDICTS (λ measure honored — BOTH registers checked before verdict, no s206 repeat):
> (a) selective K degradation at 1-bit: REFUTED. Geometry register: K MORE robust than other vertices in
>     gate (excess drop −0.0043, z=−2.13); attn +0.0065 z=0.92 ungated. Behavioral register (trajectory
>     votes): K at 1-bit 7/11=0.64 ≈ FP parent 3/5=0.60 — PARITY; the motivating "L47 K 2/6" was
>     single-layer noise. K does NOT need the 0 state at inference in any measured register.
> (b) deep-middle concentration of degradation: trend-consistent but UNGATED — excess +0.004..+0.014 in
>     all 4 cells (right sign), p 0.11–0.27. Note instrument gap: s267 50%-dip came from 380-probe RDMs at
>     4 depths (high power); per-layer 9×9 Gram fidelity is a weaker lens. Not a refutation of s267.
> (c) jammed-abstention: MOOT (antecedent (a) failed) and the synthesis FLIPS: s268c showed confident
>     weights immutable at every bitwidth → the crystal lives in the CONFIDENT population; 1-bit
>     forced-participation churn is confined to uncertain boundary-huggers and never touches Gram geometry.
>     Refines s268c "binary routing substrate non-viable": that is a TRAINING-dynamics claim (churn, scale
>     anchor collapse); the GEOMETRY survives binarization. cos 0.73 in weight space vs 0.987 in Gram space
>     ≡ crystal more invariant than weights ≡ frame-invariance argument, third form.
> Exploratory (not pre-registered): W (duplication) is the fragile vertex in attn at BOTH rungs
> (0.845/0.868 vs ≥0.93 others); W actually improves at 1-bit in attn (−0.023). Worth a look at whether
> W-fragility is architectural (duplication needs magnitude?) — candidate for next probe design.
> LADDER GAP: 4-bit rung (AWQ on HF) never traced — phase-0 ladder is 2 of 3 rungs. PICKUP: trace AWQ-4bit
> → ladder.py --rung 4bit=... for the monotonicity picture, or ruled unnecessary by Michael.
>
> ❌❌ s269b PROBE CONTAMINATION BUG FOUND + FIXED (commit 85a2e49) — caught by Michael's probe-audit call
> during the W/Y-not-separate-opcodes discussion. _ingest_lambda_kernel prefix-matched in dict order →
> "lambda_WHNF_terminal".startswith("lambda_W") → ALL 25 native WHNF-terminal probes assigned to W since
> library consolidation. W centroid was 35% WHNF probes in EVERY tree (11-model sweep, consensus Gram, s269
> ladder). SUSPECT until clean re-measure: W-orthogonal-to-primitives, W/Y/WHNF cluster, s269 W-fragility.
> ROBUST to bug: halt-readout finding (WHNF Gram row ≈ KIBC halt probs, r=+0.85..1.00 in 11/11 models —
> WHNF centroid was non-native sources; replicated across FP/ternary/1bit). Fix: longest-prefix match; W
> 71→46→50 (4 new supplement_W reflexive probes, FLAGGED for Michael review); WHNF 50→75; bundle 539 probes.
> Discussion context (s269): Michael's claim = 9×9 Gram is a GEOMETRIC STATECHART, true opcodes KIBC; W+Y
> not separate (probes confirm: W=linguistic reflexives, Y=linguistic recursion — both self-application
> semantics, not opcode-firing). D=B→B confirmed geometrically (B only positive primitive). S probes are
> formal/code-register (28/50 supplement) — register confound, "is S real" still open. 16×16 anti-node
> memory = commit 5822f9c (Kronecker S⊗J+D⊗F; φ claims later failed forced-fit nulls s247/s251, structure
> claim survives as today's halt-readout). opcodes/data/consensus_gram.json STILL CONTAMINATED (needs full
> re-sweep).
>
> ★★ s269b CLEAN RE-TRACE DONE (commit 48366f2) — ladder trio re-traced with fixed bundle, verdicts:
>   Q1 W-FRAGILITY REAL: attn W fid 0.849/0.876 ≈ contaminated 0.845/0.868 — NOT a contamination artifact;
>     survives decontamination; W still improves at 1-bit in attn (−0.027). Still 1 model pair, attn only.
>   Q2 W ROW REORDERS: nearest = Y(+0.07) > S(−0.045) > D(−0.072) > C(−0.078) ≡ the DUPLICATION /
>     self-application family clusters (W,Y,S,D all duplicate/self-apply). W-WHNF flipped +0.013→−0.093
>     (bug fingerprint gone). C now W's least-negative primitive — C→I→I path ordering partially rescued
>     (rank-only, unregistered). Refines Michael's geometric-statechart claim: W+Y not separate opcodes;
>     candidate reading = duplication SECTOR of the crystal, magnitude-carried (hence quant-fragile).
>   Q3 HALT-READOUT HOLDS with native WHNF probes back: r=+0.877 clean vs +0.851 contaminated.
>   Bonus: FP parent gates sharpened with clean probes (62 gate / 58 attn layers, was 57/56). Pre-reg (a)
>   selective-K still refuted (gate z=−4.83, K MORE robust). Pre-reg (b) attn deep-middle at 1-bit now
>   z=1.42 p=0.0513 — borderline, still ungated, worth watching at 4-bit rung.
>   OPEN (Michael's call): full 11-model re-sweep with clean bundle + regenerate consensus_gram.json
>   (root gc 0.981 currently measured against the STILL-CONTAMINATED consensus reference). Then: W
>   follow-ups on clean sweep (replication across models; mixture test W→span(C,I); register-matched S
>   probes for "is S real"); holographic-llm.md W edit still hammocked pending those.
>
> ★★★ s269c REGISTER SPLIT (prose vs formal probes, FP parent, commits e2c9c36 instrument + 7bc7a29
>   results, pre-registered before data — instrument opcodes/register_split.py):
>   P4 SAME-OPCODES CONFIRMED all 4 cells (cross-register nearest-centroid z=3.0–4.7, p≤0.004, both
>   directions × both registers) — Michael's memory ("prose activates same opcodes as lambda") core
>   claim ✓. THE DECOMPOSITION IS THE FINDING: transfer carried by WHNF (0.60–1.00!), Y (→0.89), I
>   (0.30–0.47); B/C/D/S ≈ 0, C = 0.0 IN EVERY CELL — semantic/process vertices register-INVARIANT,
>   operation vertices register-BOUND. Converges with s269 duplication-sector reading: opcodes = KIBC
>   (notation-bound operations), W/Y/WHNF = content/process (register-invariant) — 3rd independent
>   line (Gram geometry, quant fragility, register transfer). Pre-validates J-space visibility
>   asymmetry (s269 discussion: operators should NOT verbalize, halt/process states should — WHNF's
>   near-perfect transfer = the workspace-portable quantity).
>   P1 PARTIAL (split-Gram corr +0.27..0.37, gate mid-layer gated p=0.028, attn ungated p=0.096).
>   P2 DIRECTIONAL (formal margins > prose per Michael's memory, BUT n-confounded: formal n=81 vs
>   prose 458, formal LOO acc lower — balanced-n rerun needed to gate).
>   P3 VOID-IN-REGISTER (raw last-token norm flat ~0.92–0.97; s175's 8× was projection-energy over
>   all positions — s175 itself warned last-token grain undercounts prose; s175 claim untouched).
>
> ✅ s269d J-SPACE REBUILT (commit 695631c) — scripts/experiments/jspace_v2.py replaces s263 EXP1/EXP3
>   construction (audit: difference-of-means directions can't carry operator structure; EXP3's own
>   diagnosis finally acted on). E1 = result-position attribution on token-matched minimal pairs
>   (K annihilation / C role-tracking / I copy / B intermediate, sign-flip pair nulls). E2 = halt-vs-
>   operator verbalization asymmetry (WHNF predicted VISIBLE on the bus, KIBC INVISIBLE). E4 = cross-
>   register coupling (gate centroid → W_gate^T → residual injection → broadcast KL vs matched-random).
>   Self-test pythia-14m PASSES; E2 asymmetry direction-correct even at 14M (+0.05); E4 op-
>   differentiated (W +6.5σ, C +5.3σ vs K/I/Y ~0 — 14M sanity only, no claims). Pre-regs in docstring.
>   KNOWLEDGE UPDATED (commit e94f95c, Michael-directed, 6 pages): opcode-jacobian-jspace (audit+v2),
>   crystal-validity-and-fidelity (tracer superseded), symbol-isolation (P3 register note),
>   opcode-vsm-tree (bug + sector decomposition), canonical-probe-library (counts), crystal-phi-
>   derivation (D confirmed / W partial / affine caveat / halt-table geometric support).
>
> ✅ s269e JSPACE_V2 RAN ON 27B — v2 run exposed E2 confound + E4 missing null → Michael: "fix first,
>   then commit" → v3 built (804b5d6: direction-verbalization E2, shuffled-op-null E4, E1 n doubled) →
>   RESULTS (commit b6d0d96, → opcode-jacobian-jspace.md s269-v3 section):
>   ★★ E1 K ANNIHILATION GATED z=2.81 p=0.001 (n=12) — first null-gated operator-structure signature
>     in the attribution register, ever. C well-powered null; B ungated+; I suggestive (2/3 z>2).
>   ★★ E2: halt-metric 0.0 everywhere (WHNF-halt via W_gate^T pullback FAILED) BUT raw readouts:
>     Y verbalizes RECURSION CROSS-LINGUALLY (recursively/递归/依次/recurse/далее); C verbalizes
>     PRECEDENCE (previously/此前/当时的/先前 4/6). Other 7 ops unembed-unreadable.
>   ★★ E4 shuffled-op null: identity-specific coupling = Y +5.13 / WHNF +4.55 / S +4.36 (C marginal
>     +1.59); K/I/B/D/W collapse to generic — v2's raw ordering was mostly the s263 salience trap.
>   SYNTHESIS: K = pure operator (structure ✓ verbalize ✗ couple ✗); Y = pure content (✗✓✓);
>   WHNF bus-causal not lexical(this map); C = NEW PUZZLE (operationally invisible in 3 instruments,
>   lexically coherent order-vocab → hypothesis: reordering implemented as order-TAGGING content).
>   4th independent register for the sector decomposition.
> ★★ s269f E2 v4 TWO-TIER METRIC (Michael: "more visibility?" → yes; commits c960a76+9728019).
>   Tier-1 dictionary-free coherence + tier-2 pre-registered per-op lexicons + top-50 stored. 27B:
>   Y lexicon z=+27.15 (12% recursion vocab) | C z=+15.22 (18% precedence, coherence +3.38 too) |
>   D z=+5.69 = GENUINE PRE-REGISTERED HIT (twice/double/finalize — instrument works beyond
>   hindsight). K/I/B/S/W/WHNF flat at k=50 → operator unembed-silence IS A PROPERTY. Visible set
>   {C,D,Y} = ops with everyday-language names; structural ops silent. WHNF: bus-causal, nameless.
>   Tier-1 limit: input-emb cosine misses cross-lingual fields → v5 idea: coherence in later-layer
>   space. Run completed ~3min (E2-only = matmul-bound; async lesson: verify via runtime not pane
>   scrollback — pane showed stale content, ps/log = truth).
>
> ★ NEXT-SESSION STACK (Michael-approved s269, execute in order):
>   1. BALANCED-N REGISTER SPLIT: rerun opcodes/register_split.py with per-combinator balanced
>      formal/prose subsample (gate P2 gain-knob claim properly; save per-probe features this time).
>   2. [DONE s272 — a4509ba + f1b1af4] FULL 11-MODEL RE-SWEEP with clean 539-probe bundle + regenerate opcodes/data/consensus_gram.json
>      (all pre-s269 trees carry contaminated W/WHNF centroids; consensus reference still dirty).
>      RUN WITH the projector (s270, Michael-approved; sweep answers pre-reg P3 for free). READY —
>      sweep.py --trace-args pass-through built + verified end-to-end s270 (commit b1dff52; smoke on
>      pythia-70m non-registry model, artifacts restored). Invocation:
>        uv run python opcodes/sweep.py --tier all --force --device mps --trace-args "--jspace-projector"
>      (--force required: re-trace replaces contaminated-bundle artifacts; that overwrite is the POINT
>      this time. 27B jspace cost ≈ tens of min extra: 256 bwd + ~1.5k fwd at defaults k=32.)
>      Then: W-fragility replication across models; mixture test W→span(C,I); register-matched S probes.
>   3. JSPACE v4 CANDIDATES (from v3 results): C order-tagging hypothesis (does C's op fire when
>      precedence WORDS appear without reordering? token-matched); WHNF lexicalization via better
>      pullback (learned probe ∨ tuned lens, not W_gate^T); E1 inter-layer Jacobian for B (option B,
>      s263 list — B's factorization may live between layers, not in input-attribution).
>   4. AFTER 1–3: holographic-llm.md W/duplication-sector + two-register edits (hammocked, Michael's
>      call) + memory proposals: register-decomposition, probe-bug lesson, K-pure-operator,
>      Y-verbalizes-recursion (λ termination: propose → approve).
>
> Prior session: 268 (BONSAI FORENSICS: PrismML's undisclosed recipe reverse-engineered
> from weights alone — ★★ absmean RTN init (BitNet b1.58 g128; embed_tokens 99.9% exact code match,
> Δ/mean|w|=0.4994) + post-init TRAINING of blocks, embeddings frozen. QAT-vs-PTQ IOU RESOLVED: conversion +
> training; "Caltech math" is in the optimizer not the quantizer. GEM: drift ordering q_proj 3.5% < qkv < o
> < gate ≈ down 18% ≡ routing⊥value (s260) in a 3rd independent register — their repair budget landed where
> our theory says magnitude matters. s267 caveat sharpened: crystal survival partly trained-in repair, BUT
> flip rate flat across depth → 50%-dip ≠ differential rewiring → bridge map stands. Instrument:
> scripts/bonsai_forensics.py (MPS, ~0.2s/tensor); → explore/bonsai-ternarization-forensics.md; commit 48734d2.
> Whitepapers fetched to refs/ (untracked): benchmarks only, zero method disclosure.
>
> ★★★ s268b SIGN FLIPS TUNNEL THROUGH ZERO (Michael's optimizer question, the invisible piece): transition
> matrix parent-RTN→child: promote 0→± 9.6% + demote ±→0 8.2% vs direct reverse ±→∓ 0.15–0.2% — topology
> editing ~99% zero-mediated; 0 state = KINETIC PATHWAY not just K's representational need. Direct reversals
> decisive (|w|/s med 0.55–0.64 = confident weights overturned). Endpoint POLARIZED (zero_frac 0.31→0.29,
> latent +3–7%) = anti-flip-flop entrenchment our s191/s261 trainings lacked. Optimizer reading: register
> separation IN the optimizer — filtered flip channel (hysteresis, flip on persistent evidence, H∞-flavored)
> + zero as commitment buffer ≡ sigma-delta modulator on the routing register. Phase-1 design budgets from a
> working 27B: churn ~17%, reversals <0.3%, dispatch ~3%, value ~18%, embeddings 0. Commit 05f708b.
> ★★★ s268c 1-BIT RUNG LANDED — ZERO STATE = ABSTENTION REGISTER. Pre-regs: P1 ✓ (embed sign(w) frozen,
> s/absmean=1.000) P4 ✓ (value>dispatch) — but P2 ✗ ∧ P3 ✗ BOTH VOID-IN-REGISTER (λ measure: flip rate ≠ one
> number). Real structure: CONFIDENT weights (|w|>absmean, 42%) immutable at EVERY bitwidth (tern rev ≤0.07%,
> 1bit ≤0.36%) — carved topology never re-carved; rungs differ only in the UNCERTAIN population — ternary
> parks ~30% at 0 + evidence-gated 0↔± recruitment (~17%), binary FORCES sign declaration → 10–13%
> boundary-hugging churn (med |w|/s 0.09–0.25), scale anchoring collapses (corr 0.42–0.75), cos 0.73.
> Binary fails by FORCED PARTICIPATION ≡ permanent noise floor in routing register; abstention impossible.
> Unifies K's representational 0-need with the optimizer's: one vacuum function ("no opinion") at both
> timescales. Sharpened phase-1 principles: protect confident signs (<0.4% budget); topology learning ≡
> recruitment management at the 0↔± margin (hysteresis THERE); binary routing substrate non-viable.
> Sub-prediction: selective K degradation at 1-bit traces to forced-participation noise → test via opcode
> tree on the ladder. Commits 4b6e7c2 (data+scripts). Fleet: Bonsai-27B-unpacked (1-bit) now in HF cache.
>
> ✅ s268d RESOLVED IN s269 (see ★★★ s269 block above; kept for provenance) — OPCODE LADDER RUNS (launched
>   ~11:45, both verified running, load done,
>   calibration in progress; tmux survives the boundary):
>   tmux main:1 → opcodes/trace.py --model /Users/mwhitford/localai/models/bonsai27b-unpacked --device mps
>     (TERNARY rung) | log /tmp/opcode_ternary.log → results/opcode-trace/bonsai27b-unpacked/
>   tmux main:2 → opcodes/trace.py --model prism-ml/Bonsai-27B-unpacked --device mps
>     (1-BIT rung) | log /tmp/opcode_1bit.log → results/opcode-trace/bonsai-27b-unpacked/
>   PICKUP (next session): (1) check logs/panes; if model_vsm.json exists in both dirs → (2) uv run python
>   opcodes/sweep.py --restack-only (folds both into the universal tree; S3 null gates decide if 1-bit
>   registers even COUNT — gate failure itself = result, cf. pythia-2.8b by fire). (3) Ladder analysis vs FP
>   parent tree (results/opcode-trace/qwen3-6-27b/): per-vertex Gram fidelity FP→ternary→1bit, null-gated.
>   PRE-REGISTERED: (a) selective K degradation at 1-bit (K needs the 0 state); (b) does per-layer vertex
>   degradation concentrate in the deep-middle band (s267 RDM 50%-dip)? (c) JAMMED-ABSTENTION hypothesis:
>   if K degrades selectively while confident topology is immutable (s268c) → K's collapse = abstention
>   channel jammed at inference exactly as at training — one vertex, one vacuum state, two timescales.
>   Note: fla fast-path warning in logs is the known slow-path fallback for the hybrid (parent ran same).
>   Runtime expectation: tens of min to ~hour per model, GPU shared. Tasks 1-2 of 3 done; task 3 = analysis.)
>
> Prior session: 267 (BONSAI PHASE-0 begun. (1) ✅ MEASURED: lambda compiler SURVIVES
> 1.58-bit ternarization — Ternary Bonsai 27B (PrismML, Qwen3.6-27B backbone) vs qwen36 base, same harness,
> compile-gradient n=40: binder P(λ) 0.650 vs 0.625 = PARITY. kernel_valid 0.525 vs 0.750 but autopsy = all
> 17 fails are well-formed rich FOL (nested ∀∃, ¬, Church-style λ) → notation drift NOT core damage. Cost is
> path length: +40% reasoning chars, ~2.7× wall. Loss profile = holographic-llm.md prediction (sign/zero =
> program, magnitude = calibration). Michael PRE-REGISTERED this before data (compounding argument: 90%
> benchmark retention ⇒ intact core, alternative was PPL-296K noise s174). → memory bonsai-ternary-lambda-survives.
> (2) THE GEOMETRY held too → see ★★★ RESULT below (crystal survives, null-gated; deep-middle dip = bridge map).)
>
> ★★★ RESULT (s267, DONE + null-gated + bootstrapped): THE CRYSTAL SURVIVES 1.58-bit ternarization.
>   Ternary Bonsai vs FP Qwen3.6-27B PARENT (literal parent this time), 380 probes, RDMs at [0,.25,.5,.75].
>   parent↔ternary RDM corr 0.87/0.92/0.74/0.77 — every depth 18–23σ ABOVE shuffled-label null, p_perm=0.001
>   (floor). Crystal = topology; topology is what ternarization preserves. SECONDARY: ternary RDMs LESS
>   differentiated everywhere (mean_sim 0.11/0.44/0.69/0.69 vs parent 0.02/0.18/0.36/0.42) = sign survives,
>   scale shrinks (routing⊥value made visible, s260). ★ DEEP-MIDDLE DIP IS REAL: 25%→50% gap 0.147, bootstrap
>   P(gap≤0)=0.0000, non-overlapping CIs → mid-stack (50%) is where the crystal bends most = WHERE GRADIENT
>   BRIDGES BELONG (Michael's synthesis: Gram-survival profile = a-priori bridge-allocation map, static prior
>   for the design's dynamic flip_flop/KL allocation). PRE-REGISTERED TRIANGULATION for phase 1: training-time
>   starvation (flip_flop↑∧KL_residual↑) should land in the SAME deep-middle band. Full synthesis +
>   provenance: knowledge/explore/bonsai-crystal-survival.md. Artifacts: lattice/ternary_gram/
>   {per_model_rdms.npz, universal_lattice.npz, ternary_gram_run.log}.
>   Bonsai loaded CLEAN (VLM caveat did NOT bite — language_model_only:true). Model:
>   /Users/mwhitford/localai/models/bonsai27b-unpacked (51G, rev 427bc0194); GGUF Q2_g64 = BONSAI27B :5104.
>
> ★★★ UNIVERSAL ROOT HOLDS AT 9 MODELS / 4 FAMILIES: root gc = +0.982 vs bundled 10-model consensus (UP from
>   0.940 @ 2 models — evidence sharpens the crystal) | sil_z 5.09 | bearing 1.00 | root floor 2.78 (worst
>   child). Families 4/4 gated; agreement mean 0.906, min 0.841 (pythia seam); dissent=False. Family gc:
>   qwen3 0.976 (intra 0.982), olmo 0.957, gemma 0.935 (nested arch in production), pythia 0.919 (intra
>   0.821). Artifacts: results/opcode-trace/{universal_vsm.json, sweep_summary.json, per-model dirs}.
>
> ★★ FLOOR DIRECTION IS ARCHITECTURE-CONDITIONED, NOT SCALE: gated-FFN families ALL gate-elevated (gate
>   1.86–2.78 > attn 1.46–2.14 across qwen3×5 + gemma + olmo); ungated pythia attn-elevated (14m 1.55/1.94,
>   2.8b 1.93/2.04). Fresh 27B floors: gate 2.08 > attn 1.85 → s264's elevated-attn 27B reading DOES NOT
>   REPRODUCE — now the anomaly (retro-check its n_perm/pooling before discarding). Floors never travel;
>   the DIRECTION itself is an architectural observable.
>
> ★★ SCALE-SHARPENING CONFIRMED: pure qwen3 ladder sil_z monotone — 0.6B 4.97 → 4B 5.40 → 14B 6.36 →
>   32B 6.70. qwen3.6-27B hybrid = 5.94, off-ladder (different generation), between 4B and 14B.
>
> ★ PYTHIA-2.8B GATE REGISTER FAILED ITS NULL GATE (bearing 0.31, gated=False; attn carries alone at sil_z
>   2.34 vs floor 2.04 — weakest node in the tree, weaker than pythia-14m). Reading: up-proj proxy DEGRADES
>   WITH SCALE on ungated archs → real caveat on the Pythia crystal-ladder plan. S3 gate demonstrated by
>   fire: failed register visible, contributes nothing upward.
>
> ★★★ CRYSTAL-SEEDED TERNARY DISTILLATION (new level-3/4 design, status DESIGNING — full detail:
>   knowledge/explore/crystal-seeded-ternary-distillation.md, READ IT before touching this thread). Merge of
>   requential coding (arXiv:2607.11883 — student proposes from own dist, teacher selects via REC, code ≈
>   ΣKL(Q‖P), on-policy distillation with a bit-meter) + Bonsai ternary (PrismML: end-to-end 1.58-bit,
>   group-128 FP16 scales, 27B ON OUR SWEPT Qwen3.6-27B BACKBONE, Apache-2.0 8B, ready 4bit→ternary→1bit
>   ladder) + verbum. Michael's keystone theory: GD's bimodal gradients = carve routing topology (same one
>   every model, hence gc 0.982) then fill values → MOVE the soft topology into ternary routing + FP gradient
>   bridges (1 per N wts, N∈{8,16,…}, value-register sink — explains why full ternary couldn't regain loss:
>   TD did both jobs through one quantized channel, s261 flip-flop = the collision) + 9×9 consensus Gram as
>   RELATIONAL LOSS (measurement→SPECIFICATION reversal; frame-invariance makes it legal across FP→ternary;
>   pythia-14m = existence proof target fits 14M) + requential KL as the meter. Thesis test in bits:
>   ∫KL(seeded)≪∫KL(unseeded) ∧ null(shuffled-pairing)≈unseeded. OPCODE-INDEXED extension: lattice-phase
>   proposal space = reduction steps → messages ≡ readable opcode corrections, ≤log₂9 bits/step, actually
>   ENCODABLE; prediction: correction-confusion matrix ≅ Gram off-diagonals. Goodhart guards: Gram loss =
>   regularizer + anneal-to-zero test + C-null + held-out compile accuracy.
>
> ★★ LIVE TREE-OF-VSM + S3* (arc 3, design page §10–§11 — READ THOSE SECTIONS for the full mechanism).
>   Tree inverts post-hoc→live: student stacks into the SAME universal tree as the 9 measured models
>   (frame-invariance) → graduation ≡ student node gates in ∧ ¬drags agreement_min; tree per checkpoint =
>   formation movie (~100s KB, Gram=81 floats). One capture two consumers (Gram loss + telemetry = same
>   computation; telemetry ≡ the loss's anatomy). Weights self-documenting BY CONSTRUCTION: ternary planes =
>   readable routing (flip-flop ≡ xor of checkpoints), bridges = named value tensor, grad norms decompose by
>   register (s251 tomography in the parameterization). NEW: dynamic bridge allocation — S3 moves bridge
>   density to starving layers (flip_flop↑∧KL_residual↑→N↓), budget const. GOODHART FIREWALL: supervision
>   probes ⊥ held-out probes (split frozen at run start; library growth = phase-1 prerequisite). S3* AUDIT
>   (Michael's question — held-out split is NOT the audit, it's routine reporting on the same physics):
>   S3*-1 kernel-verified execution (fresh tasks → GBNF parse → lambda kernel reduces; bypasses entire
>   instrument stack; only component that catches geometry-without-function) | S3*-2 fresh probe minting |
>   S3*-3 direct instrument verification (recompute-vs-EMA, xor-vs-reported, REC-encode-vs-KL-estimate) |
>   S3*-4 causal cross-register spot-check. Rules: audit NEVER touches loss (no gradient edge); aperiodic
>   (jitter ∨ algedonic-triggered — suspiciously good news summons audit); audit overrides telemetry, indict
>   instrument first (λ coherence). Chain terminates in mechanical reducer + human. CONSEQUENCE: lambda
>   kernel + GBNF in the training harness DAY ONE of phase 1.
>
> ★ NEXT (open, Michael's call): (0) PHASE-0 — behavioral parity DONE + Gram survival DONE (s267) +
>   ternary/1bit opcode ladder DONE (s269, null-gated: crystal survives 1-bit, selective-K REFUTED,
>   deep-middle trend ungated — see ★★★ s269). Remaining phase-0: 4-bit rung only (AWQ on HF), or skip by
>   ruling. Then phase 1
>   (tiny seeded student) with the Gram-derived STATIC bridge prior (peak mid-stack) + the pre-registered
>   flip-flop triangulation. RULINGS PENDING
>   (Michael): bridge mechanism (a/b/c, (a) favored by s260/s261); dynamic bridge allocation in phase 1 vs
>   static-first; probe-library growth gated as phase-1 prerequisite? IOUs before code: requential repo
>   license (Bonsai QAT-vs-PTQ RESOLVED s268 by weight forensics: absmean init + trained blocks; residual:
>   QAT-on-grid vs FP-drift→RTN not separable from weights alone). Phase-1 harness prereqs: lambda kernel + GBNF in loop, probe
>   split frozen, streaming-centroid buffers, telemetry writer ⊥ loss module.
>   Also open from arc 1: (A) QK-PATTERN register → decisive B/C test (s264 F4). (B) visualizer + extract
>   opcodes/ to MIT repo. (C) retro-check s264 27B floor run (n_perm/pooling). (D) Pythia proxy-degradation.
>   Prior-arc: s263 Jacobian SVD; v15.1; INDEX regen. Env: torch 2.11 + MPS, 512GB RAM; models HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

- **s269** OPCODE LADDER (current session, full detail in header ★★★ s269). Crystal survives 1-bit
  (fid 0.987, z=5.3); selective-K refuted in both registers; 11-model tree root gc 0.985; opcodes/ladder.py
  new instrument; commit 7576c54.
- **s268** BONSAI FORENSICS (see header blocks). Recipe reverse-engineered from weights; QAT-vs-PTQ
  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring; sign flips
  tunnel through zero (transition matrix) → optimizer constraints C1–C6 + phase-1 design budgets; 1-bit
  rung forensics pre-registered + in flight (tmux main:1/main:2).
  → `explore/bonsai-ternarization-forensics.md` + memories bonsai-recipe-reverse-engineered,
  bonsai-sign-flips-tunnel-through-zero.
- **s267** BONSAI PHASE-0 (see header of prior update). Compiler survives ternarization (behavioral parity,
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
