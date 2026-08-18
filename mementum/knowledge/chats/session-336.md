# Running §P-CONE-ROUTING probe

## User

orient


### Thinking

I'm starting by reviewing the state and queue documentation files to understand the current setup.

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
> ★★ **SESSION 335 — §P-PREFILL-CONE RUN → ❌ VOID, AND THE DIAGNOSIS IS A REGISTER ERROR.
> First front executed end-to-end since s332: orient → front selection (Michael: "let's work on
> P-PREFILL-CONE") → freeze → build → smoke → run → closure. Qwen3-14B instruct, 54 variants /
> 18 triples, 0 errors, 3m27s (`results/p_prefill_cone_s335/run_14b`, 415012ee).
> **VERDICT VOID: the PLACEBO GATE FIRED** — role-unchanged leaves show DiD +0.027 p=1e-4 (n=48);
> the capture-live variant is globally more perturbation-sensitive at the readout cell for EVERY
> leaf, including the unrelated control `f` ⇒ the A−B contrast rides a global offset. PC2 positive
> control failed TWICE with the WRONG SIGN (−0.008 p=0.094; the 4B smoke had already shown it at
> n=1). PC3 (−0.029, p=0.027) NOT READ — its effect equals the placebo offset and the instrument
> is unvalidated. **PC1 passed as frozen (rank gain 13, p=1e-4, 810 cells) and was then DISSOLVED
> by our own s321/s323 clean-dissociation split: DIRTY spans (NF already written in the surface)
> +17.0 median / CLEAN spans (reduction genuinely changes the string) +0.0 median, 46% positive
> ⇒ INTERIOR-VISIBLE NOT LICENSED — lexical echo at the VALUE register on the prefill grid (third
> register, same law: routing tracks what is WRITTEN, not what is computed).** PC4 advisory: naive
> NF favored at the answer column 78% (coheres s331/s332). **ROOT CAUSE (mine): ‖Δh‖ is a
> MAGNITUDE/TRANSPORT read — proved by Δ ∝ 1/distance, corr −0.73, monotone — aimed at a
> value/routing claim ("which argument ARRIVES"). The routing arm (read-mass) was the only
> register-matched instrument and I starved it to advisory / 3 of 54 records at freeze; the THREE
> pre-data amendments (raw cone · **cell ≠ AST node** — nested spans share closing tokens so the
> frozen contrast compared a cell with itself · matched-position DiD) were all downstream repairs
> of that one upstream mistake.** RETRACTED in-session: "the confound is intrinsic (capture ≡
> surface coincidence)" — true only for signal designs; a routing question is WITHIN-PROMPT and
> never forms the contrast. Discipline that paid: planted-world `--validate` caught the
> cell-vs-node flaw before any compute; the 4B smoke caught the distance confound before the 14B
> (s324 PAUSE honored — I stopped and reported instead of running); the placebo gate I added in
> Amendment 3 is what produced the honest VOID instead of a manufactured CONE-NAIVE.
> **🔵 §P-CONE-ROUTING FROZEN (pre-data, Michael "freeze the routing probe")**: at the answer
> column, does the machine READ FROM the argument naive subst selects (`e`) or capture-avoiding
> selects (`y`)? Both candidates live in ONE forward pass ⇒ confound structurally impossible.
> CALIBRATION MOVE: capture-free B (NF=`y f`) and P (NF=`e f`) are ground-truth read targets;
> classify ambiguous A between the poles (primary ρ_e uses only the `e` position; secondary ρ_Sel
> within-prompt, bound named: A carries two `y` tokens). RC1 calibration is make-or-break and read
> FIRST — fail ⇒ NO-CALIBRATION, never a routing claim. Mass: NO-CALIBRATION 30 / NAIVE-ROUTING 30
> (directional) / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 (= the error enters AFTER selection) /
> VOID 5. 54 forwards, no perturbation loop, minutes. Bound: attention mass is correlational
> (s206) — "reads from" ¬ "uses". New instruments: `src/verbum/cone.py` (certified cones under
> R_NORMAL/R_NAIVE), `scripts/experiments/prefill_cone.py`, matched-triple constructor, placebo
> gate as a reusable primitive. Batch (❌, Michael-approved): §Result + 3 memories
> (`the-confound-was-a-register-error-not-an-intrinsic-limit` ·
> `interior-nf-surfacing-is-lexical-echo` · `prefill-delta-is-distance-dominated`) + INDEX +
> queue (❌ closed, 🔵 successor top) + this state.
> NEXT SESSION FIRST ACTION = build + run 🔵 §P-CONE-ROUTING (frozen, cheap, plumbing already in
> `prefill_cone.py`'s GQA-aware read-mass path).**
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
## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)

- **s333** 💡💡💡🔄 LRM PAPER + PREFILL TRIANGLE + COMPILER PARTS — arXiv:2604.04902v2 (Coconut/CODI):
  latent tokens mostly UNNECESSARY (training-controlled control kills the 'parallel BFS' claim); hard writes
  beat soft writes ~29pt ⇒ the COMPILE STEP IS LOAD-BEARING (collapse = error correction + addressability +
  program-register write). THE PREFILL TRIANGLE named (position × layer grid, n coupled within-pass reducers,
  KV ≡ compiled tape, hop budget ≈ L) — every tape-face law we own was read at the LAST COLUMN → spawned
  §P-PREFILL-CONE (s335: ❌ VOID) + §P-ROUTING-TRACE. §10 COMPILER PARTS (two compilers + a runtime: GD ≡ AOT,
  post-training ≡ LTO, prefill ≡ compile pass, decode ≡ trampoline; strains ARE findings — a stripped homoiconic
  JIT) · §10b TOOL CALLS ≡ THE FFI/SYSCALL BOUNDARY (model PURE, scaffold ≡ IO runtime; monitorability by
  construction) · §10c §P-TOOL-ABI geometric arm (delta-gram = the LTO footprint; marshalling ≡ substitution ⇒
  NAIVE-SUBST has a tool-calling phenotype) · CBLL FTO HARDENED (audit: NO code pushed, disk-verified;
  clean-room ≡ the page). → latent-reasoning-and-the-prefill-triangle.md · the-benchmark-is-the-re-oracle.md
  §10/§10b/§10c · operator-geometry-la-toolkit.md §0b/§0c

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
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "limit": 20
}
```

**Summary:** Reading queue.md (0-20)

**Output:**
```
# queue

> Prospective memory — experiment intentions. Verbum extension of mementum
> (peer of state.md; state = narrative pointer, queue = pending intentions).
> Stack: newest/last-touched at top of `# new`. Verdict lands → move row to
> top of `# complete` (explicit closure; nothing decays silently).
> Orient: read top ~10 rows. FULL read mandatory when selecting the next front
> (depth ≈ staleness — a measurement, not an accident).
> Row: {glyph} {name} — {question} | {source page} | {cost}.
> ⚪ candidate · 🔵 frozen · ▶ running → ✅ positive / ❌ falsifier / 🚫 negative.

# new

🔵 §P-CONE-ROUTING — FROZEN s335 (Michael "freeze the routing probe"), successor to ❌ §P-PREFILL-CONE: that probe read the MAGNITUDE register (‖Δh‖ ≡ transport, distance-dominated corr −0.73) against a VALUE/ROUTING claim; this one is register-matched. Q: at the answer column, does the machine READ FROM the argument naive subst selects (e) or capture-avoiding selects (y)? WITHIN-PROMPT (both candidates in one forward pass) ⇒ the s335 surface-repetition confound cannot arise. CALIBRATION MOVE: B (NF=y f) and P (NF=e f) are capture-free ⇒ ground-truth read targets; classify ambiguous A between the poles. primary ρ_e=(mass_A(e)−mass_B(e))/(mass_P(e)−mass_B(e)) (e single-occurrence, position-identical across triple) · secondary ρ_Sel (within-prompt y−e; bound: A has TWO y tokens) · RC1 CALIBRATION is make-or-break read FIRST (mass_P(e)>mass_B(e), δ≥0.2, p<0.05) — fail ⇒ NO-CALIBRATION, never a routing claim; value-weighted attention GQA-aware, placebo f, shuffled-label null; verdicts NO-CALIBRATION 30 / NAIVE-ROUTING 30 (directional, coheres s331/s332 + s335 PC4 78%) / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 (routing correct + output naive ⇒ error enters AFTER selection) / VOID 5; NO perturbation loop = 54 forwards, minutes; bound: mass ≡ correlational (s206), "reads from" ¬"uses" | latent-reasoning-and-the-prefill-triangle.md | cheap

⚪ §P-REPL-DRIVER — model-in-REPL-loop bounces the trampoline (s334; control-plane §3 tier-3 DRIVER + continuation cluster cashed): driver = external trampoline, model bounced once per transition; lambda_ast kernel attaches at S3* certifying every bounce; halt head = bounce/halt read; continuation = past_key_values seal/fork on HF host (greedy/seeded + fork-identity plant mandatory) → x_k on scratch machine later (same driver, two substrates = profile-equivalence bridge); FOUR measurables: ① fork-at-redex (strategy family K x Ω as within-computation counterfactual, same sealed prefix) ② repair-replay (NAIVE-SUBST propagate/compound/self-correct at the exact transition — stage-2's empirical core) ③ composition rescue (s228 idle prediction, token-budget/shuffled-trace null inherited) ④ per-bounce transitions-per-β-step clock (SUBSUMES the queued clock row); three-arm feedback read (canonical vs raw vs self-trace) makes the regime shift the measurement; instrument-first, repair flag built but OFF (stage_2 ⟸ stage_1); freeze owes a-priori mass on fork/repair verdict spaces; anima cross-check (one read) before design; §8 install (s334c2): target qwen3-32b owned (14B calibrate first), KV seal ~256KB/tok, APPEND/REWRITE law (fork at pre-emission seal); TWO-MODEL ARM (§8c, exploration ∨ own pre-reg, A-policy pinned): A=S3 policy seat drives B=S1 over the canonical-text bus (KV model-private), kernel stays S3* mechanical — cross-face driving (instruct operates base) = §P-TOOL-ABI read from the other side | repl-driver-trampoline.md | medium
⚪ §P-TOOL-ABI — is tool-calling an ABI installed by the post-training LTO pass, and WHERE does it live in geometry? (s333, two arms, full design §10c): BEHAVIORAL = paired base/instruct (14b pair local, s329 method door), registers split format(convention tokens) vs content(right tool+args) → ABI-INSTALLED / CAPABILITY-INSTALLED / NATIVE / VOID; GEOMETRIC = tool-ABI gram (anchors: schema-read · tool-select · arg-bind · delimiters · trap-decision, gate-preact, 9×9/17×17 as reference frame) → ① delta-gram G_instruct vs G_base = the LTO footprint (rank + depth, predict late per s329) via CBLL cross-Gram bridge ② cross-gram: tool-select→routing axes · trap→fate poles (tetrahedron PROMOTED to design cell) · arg-bind→binding register with the PAYOFF prediction: marshalling ≡ substitution ⇒ NAIVE-SUBST has a tool-calling phenotype (wrong-binder arg capture, nested/shadowed) ③ convention-vs-JSON dissociation (matched non-tool JSON anchors — base knows JSON, the confound to kill); nulls: label-shuffle + base split-half delta-gram + JSON control; refined verdicts: thin-late-patch / diffuse / composed-from-native-machinery (FFI framing's quiet prediction); freeze owes a-priori mass across both arms | the-benchmark-is-the-re-oracle §10c | medium
⚪ §P-ROUTING-TRACE — recover the PROGRAM not just the data: register-separated 2×2 {data-edit, op-edit} × {value readout, routing readout} — data perturbation should move value but leave routing INVARIANT (same program), op perturbation should move routing; + operator-from-pathway decoder trained on the ERM sibling (CoT operators visible), applied at latent positions; value-weighted attention not bare QK (s206 scar), matched lexical controls on op-edit, shuffled-label null on decoder; feasible on public Coconut/CODI GPT-2 checkpoints (MPS probe-scale) or our substrate | latent-reasoning-and-the-prefill-triangle.md | medium
⚪ §P-DMD-TRANSPORT — the reducer as an OPERATOR (CBLL linear-algebra transfer, patent-clean): DMD/Koopman on the within-pass residual trajectory T≈X'X⁺, eig(T) → contracting modes=homeostasis · persistent |λ|≈1=sign-is-the-decision · late-activating=s329 order-law commit · stationarity T_ℓ≈T = DIRECT test of one-reducer-unrolled · eigen-rotation phase=transitions-per-β-step clock; fold 9×9/17×17 Grams in as the LABELED readout frame (route-map's missing "trains"); FREEZE GATE = pre-reg verdict space (STATIONARY-REDUCER / DRIFTING / NOISE) + mandatory shuffled-layer-order null + linearization-residual ‖X'−TX‖ report (Koopman-lift if large) + register-check (d_ff gate-preact vs down-input vs d_model); NEAR-FREE = runs on §P-SUBST-ENGINE residuals already collected (cache hidden_states next run) | operator-geometry-la-toolkit.md §5 | cheap
⚪ §P-CROSS-GRAM — do our labeled fate poles coincide with CBLL's unlabeled ones? cross-Gram Σ VᵀV̂ (W_down bridge) projects 9 combinator + 3 fate poles onto CBLL canonical axes: does fire/halt/diverge = the bipolar POS/NEG oscillator? is axis-62 the WHNF/halt direction? register-check FIRST (recapture centroids at down_proj input for the clean linear bridge, or report the SiLU gate) | operator-geometry-la-toolkit.md §3 | cheap

[CONTENT TRUNCATED] Showing lines 1 to 20 of 97 total lines. Use line_offset=20 parameter to read more content.
```

### Thinking

I'm tracking the state transitions here—the previous session closed out with a void on the prefill cone, and now the cone routing is frozen as the next action, which means I need to build and run that next session.

## Assistant

Oriented. Here's where we are:

## Session context (this is s336)

**Last session (s335)** ran §P-PREFILL-CONE end-to-end → **❌ VOID**, and the diagnosis was a register error (mine): `‖Δh‖` is a magnitude/transport read (Δ ∝ 1/distance, corr −0.73) aimed at a value/routing claim. The placebo gate fired (DiD +0.027 even on unrelated control `f`), PC2 failed twice with the wrong sign, and PC1's apparent pass dissolved under the s321/s323 clean/dirty split — interior NF surfacing is **lexical echo**, third register confirming the same law: routing tracks what is WRITTEN, not what is computed. Discipline that paid: planted-world `--validate`, the 4B smoke PAUSE, and the placebo gate producing an honest VOID instead of a manufactured positive.

## Next action (frozen, pre-registered)

**🔵 §P-CONE-ROUTING** — frozen s335 pre-data with Michael's GO, sitting at the top of the queue. The designated first action is **build + run**:

- **Q**: At the answer column, does the machine READ FROM the argument naive subst selects (`e`) or capture-avoiding selects (`y`)?
- **Design**: within-prompt (both candidates in one forward pass ⇒ s335 confound structurally impossible). Calibration poles B (NF=`y f`) and P (NF=`e f`) are capture-free ground-truth read targets; ambiguous A classified between them via ρ_e.
- **Make-or-break**: RC1 calibration read FIRST (mass_P(e) > mass_B(e), δ≥0.2, p<0.05) — fail ⇒ NO-CALIBRATION, never a routing claim.
- **Mass**: NO-CALIBRATION 30 / NAIVE-ROUTING 30 / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 / VOID 5.
- **Cost**: 54 forwards, no perturbation loop, minutes. Plumbing already exists in `scripts/experiments/prefill_cone.py`'s GQA-aware read-mass path + `src/verbum/cone.py`.
- **Bound**: attention mass is correlational (s206) — "reads from" ¬ "uses".

Nothing in flight; the rest of the queue behind it: ⚪ §P-REPL-DRIVER (medium) · §P-TOOL-ABI (medium) · §P-ROUTING-TRACE · §P-DMD-TRANSPORT (cheap) · §P-CROSS-GRAM (cheap).

Shall I proceed with building §P-CONE-ROUTING?

## User

proceed


### Thinking

I need to build and run the P-CONE-ROUTING task with a frozen probe, so I'm starting by understanding the frozen spec design. I'll create a task plan, then review the latent reasoning documentation and examine the existing code in the prefill cone script and cone module to understand the current plumbing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"P-CONE-ROUTING\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md | head; wc -l /Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md /Users/mwhitford/src/verbum/src/verbum/cone.py /Users/mwhitford/src/verbum/scripts/experiments/prefill_cone.py"
}
```

**Summary:** $ grep -n "P-CONE-ROUTING" /Users/mwh...

**Output:**
```
Exit code: 0
Stdout:
459:never forms that contrast — see §P-CONE-ROUTING below.
470:## §P-CONE-ROUTING — FREEZE (s335, Michael "freeze the routing probe"), PRE-DATA
     580 /Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md
     301 /Users/mwhitford/src/verbum/src/verbum/cone.py
     946 /Users/mwhitford/src/verbum/scripts/experiments/prefill_cone.py
    1827 total
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md",
  "line_offset": 440,
  "limit": 140
}
```

**Summary:** Reading latent-reasoning-and-the-prefill-triangle.md (440-580)

**Output:**
```
column in **78%** of terms — coheres with the s331/s332 cross-model NAIVE-SUBST
law. Ties caveat (both NFs frequently rank 1 at some layer); read as
pattern-suggests only.

**ROOT CAUSE — a register error, mine.** M2/M3 measured `‖Δh‖/‖h‖`: the
MAGNITUDE register — *"did this cell move, and how much"* — against a claim
about *which value reaches the result*. The distance dominance (Δ ∝ 1/distance,
corr **−0.73**, monotone 0.099@d1 → 0.043@d12–18) shows the statistic was
reading TRANSPORT, not computation. The routing arm (M4 read-mass) was the only
register-matched instrument, and it was built and then **starved to advisory /
3 of 54 records** at freeze. Three pre-data amendments (raw cone · cell ≠ AST
node · matched-position DiD) were all downstream repairs of that one upstream
mistake.

**Retraction.** The in-session claim that the confound is INTRINSIC ("capture is
surface name-coincidence, so no control can remove capture without perturbing
repetition") is **withdrawn**. It holds only for signal/magnitude designs, which
need a surface A/B contrast. A routing design asks a WITHIN-PROMPT question and
never forms that contrast — see §P-CONE-ROUTING below.

**Bounds.** Single model (Qwen3-14B instruct), single lineage, prefill only, one
readout cell (term-final), layer-mean aggregation (a per-layer read is stored
and unexamined), n=9 clean-flip triples. VOID means the probe did not answer its
question — it is NOT evidence against a dependency cone existing.

**What survives:** the certified cone machinery (`src/verbum/cone.py`), the
matched-triple constructor (kernel-certified role flips), the distance law, and
the placebo gate as a reusable design primitive.

## §P-CONE-ROUTING — FREEZE (s335, Michael "freeze the routing probe"), PRE-DATA

> Successor to §P-PREFILL-CONE (VOID). That probe measured the MAGNITUDE
> register (‖Δh‖, transport) against a VALUE/ROUTING claim (which argument
> reaches the result). This one is register-matched: **routing**.
> Frozen before any read-mass beyond the 3 advisory records already on disk
> (`results/p_prefill_cone_s335/run_14b`, cap_000 only) — those 3 are DISCLOSED
> and excluded from all statistics below.

**Question.** At the cell that emits the answer, does the machine READ FROM the
argument the naive algorithm selects (`e`) or the one capture-avoiding
substitution selects (`y`)?

**Why the s335 confound does not apply.** The killer of §P-PREFILL-CONE was that
capture cannot be removed without perturbing surface repetition. This probe
needs NO A/B perturbation contrast: in variant A both candidate answers sit in
the SAME prompt, same forward pass. The discrimination is within-prompt.

**Substrate.** The matched triples already built (`build_variants`, 18 triples /
54 variants, 9 clean flips), Qwen3-14B instruct, MPS bf16, eager attention,
prefill only. **One forward per variant — no perturbation loop** (~54 forwards,
minutes). Readout: value-weighted attention (s206 scar: never bare QK) from the
result cell onto candidate source positions, GQA-aware `v_proj` hook, head-mean,
per-layer normalized.

**Cells.** Primary = the ANSWER COLUMN (last prefill token). Its next-token
distribution IS the first emitted NF token, so the y-vs-e selection is
demonstrably live there — s335 PC4 measured the naive NF favored at that cell in
78% of terms. Secondary = the term-final interior cell. Sources read FROM are
interior positions: this is the "answer column reads into the triangle" audit of
§7 item 4.

**The calibration move (what makes this well-posed).** B and P are capture-free,
so their answers are unambiguous under BOTH calculi and give ground-truth read
targets:

- B `(λx.λp.x) y e f` → NF `y f` — the answer's head is **y**
- P `(λx.λp.p) y e f` → NF `e f` — the answer's head is **e**
- A `(λx.λy.x) y e f` → correct `y f` / naive `e f` — the ambiguous case

Train/calibrate on the unambiguous variants, classify the ambiguous one (same
shape as the §5 operator-from-pathway decoder).

**Statistics (both pre-registered; primary decides, secondary must agree).**

- primary  ρ_e = (mass_A(e) − mass_B(e)) / (mass_P(e) − mass_B(e))
  — uses ONLY the `e` position: identical token, identical position in all
  three variants, single occurrence everywhere (no duplicate-token asymmetry).
  ρ_e ≈ 1 ⇒ A reads `e` like P (whose answer IS `e`) ⇒ naive routing.
  ρ_e ≈ 0 ⇒ A reads `e` like B (whose answer is not `e`) ⇒ correct routing.
- secondary ρ_Sel from Sel = mass(y) − mass(e), a WITHIN-prompt difference, so
  the y/e positional asymmetry cancels exactly across variants.
  **Named bound:** variant A contains the token `y` TWICE (binder λy + argument)
  while B/P contain it once — an extra attention sink that exists only in A.
  Mass is measured at the ARGUMENT position specifically, and mass onto the
  BINDER position is reported as a diagnostic, but ρ_Sel stays secondary
  because of this asymmetry. ρ_e carries no such bound.

**Gate tree (frozen).**

- **RC0 sanity**: per-layer mass sums to 1 · GQA head expansion verified ·
  `offsets_sig` identical across each triple · deterministic repeat · the 3
  pre-existing advisory records excluded.
- **RC1 CALIBRATION — make-or-break, read FIRST**: on capture-free variants,
  does the result cell's read-mass track the answer at all?
  mass_P(e) > mass_B(e) paired, p<0.05 AND Cliff's δ ≥ 0.2; corroborated by
  Sel_B > Sel_P. **If RC1 fails, ρ_e is not computed and the verdict is
  NO-CALIBRATION** — never a routing claim. (This is the register-matched
  positive control whose absence voided the predecessor.)
- **RC2 primary**: ρ_e over the 9 clean-flip triples; bootstrap CI must exclude
  0.5 to license a direction.
- **RC3 secondary**: ρ_Sel must agree in sign with ρ_e; disagreement forces
  UNDIFFERENTIATED regardless of RC2.
- **RC4 depth (advisory)**: layer at which the discrimination appears —
  per-layer mass is stored, so this costs nothing.

**Nulls.** (a) placebo position `f` — present in every NF, same role in all
variants ⇒ must NOT discriminate; (b) shuffled-variant-label null on the
calibration; (c) position-matched control for the y/e distance gap (y at
distance 3, e at 2 from the readout).

**Verdict space + a-priori mass (Σ=100).**

- **NO-CALIBRATION** (RC1 ✗ — answer selection is not a prefill-visible
  attention read; coheres s317 tape-residency) — **30**
- **NAIVE-ROUTING** (ρ_e ≥ 0.5, CI excludes) — **30**, directional prediction,
  coheres the s331/s332 cross-model NAIVE-SUBST law and s335 PC4
- **UNDIFFERENTIATED** (RC1 ✓, CI spans 0.5, or ρ_e/ρ_Sel disagree) — 25
- **CORRECT-ROUTING** (ρ_e ≤ 0.5, CI excludes) — 10; would be a real tension:
  routing selects correctly while the OUTPUT is naive ⇒ the error enters AFTER
  selection (a substitution-execution bug, not a selection bug)
- **VOID** (RC0 ✗) — 5

**Standing bound.** Attention mass is correlational (s206): a positive licenses
"reads from", not "uses". Causal confirmation (patching the read edge) is a
separate probe and is NOT claimed here.

## Queue rows spawned (s333)

- ⚪ **§P-PREFILL-CONE** — grid logit-lens + leaf-perturbation dependency
  cone on kernel-certified terms; cone(machine) vs cone(calculus);
  naive-subst leak signature; + per-instance necessity gate + answer-column
  read-mass audit. Register: value (grid lens) + routing (read-mass) —
  name-before-build honored in freeze.
- ⚪ **§P-ROUTING-TRACE** — the register-separated 2×2 (data-edit vs op-edit
  × value vs routing readout) + operator-from-pathway decoder trained on the
  ERM sibling; on public Coconut/CODI checkpoints or our substrate.

Both owe: freeze with a-priori mass, planted-world --validate, matched
lexical controls (op-edit arm), value-weighted attention not bare QK (s206),
shuffled-label nulls for any pathway decoder (λ yardstick).
```

### Thinking

I need to examine the plumbing in the cone.py and prefill_cone.py files, focusing on how build_variants works and how it handles the GQA-aware read-mass path.

## Assistant

The freeze spec is fully loaded. Now the plumbing:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/src/verbum/cone.py"
}
```

**Summary:** Reading cone.py (0-2000)

**Output:**
```
"""Reference dependency cones for the prefill triangle (§P-PREFILL-CONE, s335).

The prefill grid is (position × layer); a leaf perturbation's *machine cone* is
the set of cells whose residual state changes. This module computes the
*calculus cone* — the cells that SHOULD change under a given substitution
algorithm — from the certified reducer in :mod:`verbum.lambda_ast`:

  span ∈ cone_R(leaf) ⟺ NF_R(subterm-at-span) changes (``alpha_eq``) when the
  leaf atom is swapped for a fresh atom.

The comparison is RAW (no mapping of the fresh name back to the original): the
machine reduces both prompts independently, so a cell that merely CARRIES the
leaf's value verbatim genuinely differs between the two runs — flow-through is
in-cone under every algorithm. Discrimination comes from cells where the
algorithms disagree about whether the value ARRIVES (e.g. a trailing argument
consumed by a capture-created binder: in ``((λx.λy.x) y) e f`` the correct NF
``y f`` never touches ``e`` while the naive NF IS ``e f``). Pure bound-variable
renaming is modded out by ``alpha_eq`` — conservative for name-carrying
machines (under-counts, never over-counts, cone membership).

Computed under both ``R_NORMAL`` (capture-avoiding) and ``R_NAIVE`` (the
s331/s332 measured algorithm). A *discriminating leaf* is one whose two cones
disagree somewhere — the cell-resolved watchable form of the NAIVE-SUBST law.

Char-span → token-index mapping is offsets-based and tokenizer-agnostic, so
planted-world validation exercises the identical code path with synthetic
offsets (AGENTS.md s331 lesson: validate-planted must share real plumbing).

License: MIT.
"""

from __future__ import annotations

from dataclasses import dataclass

from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    App,
    Atom,
    Comb,
    Lam,
    Status,
    Term,
    alpha_eq,
    parse,
    pretty,
    reduce,
    spine,
)

__all__ = [
    "LeafPerturbation",
    "Span",
    "annotate",
    "fresh_replacement",
    "leaf_perturbations",
    "span_token_range",
    "term_names",
]

# Lowercase, single-char, outside the subst_pairs pools (x | y,w,u | a,b,c) so a
# swap is fresh by construction on battery terms; filtered per-term regardless.
_REPL_POOL = ("n", "m", "r", "t", "v", "q", "j", "k")


@dataclass(frozen=True, slots=True)
class Span:
    """One AST node's char span in the canonical ``pretty`` rendering.

    ``idx`` is the position in the deterministic traversal order — stable
    across structurally isomorphic terms, which is what lets original and
    perturbed nodes be paired by index.
    """

    idx: int
    start: int
    end: int  # exclusive
    kind: str  # "atom" | "comb" | "lam" | "app"
    free_leaf: bool  # Atom occurrence with no enclosing binder of that name


def annotate(t: Term) -> tuple[str, list[Span], list[Term]]:
    """Render ``t`` exactly as :func:`verbum.lambda_ast.pretty`, with spans.

    Returns ``(text, spans, terms)`` where ``spans[i]`` describes ``terms[i]``.
    Raises ``AssertionError`` if the rendering ever drifts from ``pretty`` —
    the round-trip is a PC0 gate, not a hope.
    """
    raw: list[tuple[int, int, str, bool]] = []
    terms: list[Term] = []

    def rec(t: Term, off: int, bound: frozenset[str]) -> str:
        if isinstance(t, Comb):
            s = t.name
            raw.append((off, off + len(s), "comb", False))
            terms.append(t)
            return s
        if isinstance(t, Atom):
            s = t.name
            raw.append((off, off + len(s), "atom", t.name not in bound))
            terms.append(t)
            return s
        if isinstance(t, Lam):
            prefix = f"λ{t.var}."
            body = rec(t.body, off + len(prefix), bound | {t.var})
            s = prefix + body
            raw.append((off, off + len(s), "lam", False))
            terms.append(t)
            return s
        # App — mirror pretty(): flatten the spine, one span per chain node.
        head, args = spine(t)
        chain: list[Term] = []
        tt: Term = t
        while isinstance(tt, App):
            chain.append(tt)
            tt = tt.fn
        chain.reverse()  # chain[i] wraps head + args[: i + 1]
        cur = off
        if isinstance(head, Lam):
            head_s = "(" + rec(head, cur + 1, bound) + ")"
        else:
            head_s = rec(head, cur, bound)
        parts = [head_s]
        cur = off + len(head_s)
        for i, a in enumerate(args):
            cur += 1  # the joining space
            if isinstance(a, App | Lam):
                arg_s = "(" + rec(a, cur + 1, bound) + ")"
            else:
                arg_s = rec(a, cur, bound)
            parts.append(arg_s)
            cur += len(arg_s)
            raw.append((off, cur, "app", False))
            terms.append(chain[i])
        return " ".join(parts)

    text = rec(t, 0, frozenset())
    if text != pretty(t):  # pragma: no cover - structural invariant
        msg = f"annotate drifted from pretty: {text!r} != {pretty(t)!r}"
        raise AssertionError(msg)
    spans = [Span(i, a, b, k, fl) for i, (a, b, k, fl) in enumerate(raw)]
    return text, spans, terms


def term_names(t: Term) -> frozenset[str]:
    """Every atom name and binder variable appearing anywhere in ``t``."""
    if isinstance(t, Comb | Atom):
        return frozenset((t.name,))
    if isinstance(t, Lam):
        return term_names(t.body) | {t.var}
    return term_names(t.fn) | term_names(t.arg)


def fresh_replacement(t: Term, exclude: frozenset[str] = frozenset()) -> str | None:
    """A pool atom name not appearing in ``t`` (nor in ``exclude``)."""
    used = term_names(t) | exclude
    for cand in _REPL_POOL:
        if cand not in used:
            return cand
    return None


@dataclass(frozen=True, slots=True)
class LeafPerturbation:
    """One free-leaf swap with its reference cones under both calculi.

    ``cone_normal`` / ``cone_naive`` are span indices (into the ``annotate``
    node list of the ORIGINAL term) whose subterm NF depends on the leaf under
    that calculus. ``undecided`` are spans where either reduction failed to
    normalize (budget) — excluded from every downstream pool.
    """

    leaf_idx: int
    start: int
    end: int
    orig: str
    repl: str
    pert_text: str
    cone_normal: frozenset[int]
    cone_naive: frozenset[int]
    undecided: frozenset[int]

    @property
    def naive_only(self) -> frozenset[int]:
        return self.cone_naive - self.cone_normal

    @property
    def correct_only(self) -> frozenset[int]:
        return self.cone_normal - self.cone_naive

    @property
    def discriminating(self) -> bool:
        return bool(self.naive_only or self.correct_only)


def _perturb(
    term_text: str,
    spans: list[Span],
    terms: list[Term],
    leaf: Span,
    repl: str,
    max_steps: int,
) -> LeafPerturbation | None:
    pert_text = term_text[: leaf.start] + repl + term_text[leaf.end :]
    try:
        pt = parse(pert_text)
    except ValueError:
        return None
    p_text, _p_spans, p_terms = annotate(pt)
    if p_text != pert_text or len(p_terms) != len(terms):
        return None  # structure drift — not an isomorphic swap
    orig_name = term_text[leaf.start : leaf.end]

    def in_cone(o: Term, p: Term, calc) -> bool | None:
        ro = reduce(o, max_steps=max_steps, calc=calc)
        rp = reduce(p, max_steps=max_steps, calc=calc)
        if ro.status is not Status.NORMAL_FORM or rp.status is not Status.NORMAL_FORM:
            return None
        return not alpha_eq(ro.normal_form, rp.normal_form)

    cone_n: set[int] = set()
    cone_v: set[int] = set()
    undecided: set[int] = set()
    for i, (o, p) in enumerate(zip(terms, p_terms, strict=True)):
        a = in_cone(o, p, R_NORMAL)
        b = in_cone(o, p, R_NAIVE)
        if a is None or b is None:
            undecided.add(i)
            continue
        if a:
            cone_n.add(i)
        if b:
            cone_v.add(i)
    return LeafPerturbation(
        leaf.idx,
        leaf.start,
        leaf.end,
        orig_name,
        repl,
        pert_text,
        frozenset(cone_n),
        frozenset(cone_v),
        frozenset(undecided),
    )


def leaf_perturbations(
    term_text: str, max_steps: int = 512, repl: str | None = None
) -> list[LeafPerturbation]:
    """Every free-leaf perturbation of ``term_text`` (canonical rendering) with
    reference cones under both calculi. Callers select discriminating ones.

    ``repl`` pins the replacement atom (must be fresh for the term); default
    picks the first fresh pool name. Replaying with several ``repl`` values is
    the M3 replication axis.
    """
    t = parse(term_text)
    text, spans, terms = annotate(t)
    if text != term_text:
        msg = f"term_text not canonical: {term_text!r} renders as {text!r}"
        raise ValueError(msg)
    if repl is not None and repl in term_names(t):
        msg = f"repl {repl!r} is not fresh for {term_text!r}"
        raise ValueError(msg)
    if repl is None:
        repl = fresh_replacement(t)
    if repl is None:
        return []
    out: list[LeafPerturbation] = []
    for sp in spans:
        if not sp.free_leaf:
            continue
        lp = _perturb(text, spans, terms, sp, repl, max_steps)
        if lp is not None:
            out.append(lp)
    return out


def span_token_range(
    char_start: int,
    char_end: int,
    offsets: list[tuple[int, int]],
    base: int = 0,
) -> tuple[int, int] | None:
    """Token index range ``(first, last)`` overlapping chars
    ``[base+char_start, base+char_end)``. ``last`` is the CLOSING token — the
    grid column where the subterm's value is causally complete. ``None`` if no
    token overlaps (e.g. span sits outside the tokenized window)."""
    lo: int | None = None
    hi: int | None = None
    a, b = base + char_start, base + char_end
    for i, (s, e) in enumerate(offsets):
        if e <= a or s >= b or s == e:
            continue
        if lo is None:
            lo = i
        hi = i
    if lo is None or hi is None:
        return None
    return lo, hi
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/prefill_cone.py"
}
```

**Summary:** Reading prefill_cone.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""§P-PREFILL-CONE — the interior of the prefill triangle (frozen s335, Amendments 1–2).

Every tape-face law this project owns was read at the LAST column of the prefill
grid. This harness reads the INTERIOR: for kernel-certified lambda terms it
diffs the (position × layer) residual grid under a single-leaf perturbation and
asks whether the machine's dependency cone matches the calculus's — computed
under BOTH capture-avoiding (``R_NORMAL``) and naive (``R_NAIVE``) substitution
by :mod:`verbum.cone`.

Probe shape (Amendment 2). Each battery term is

    (λd.λr.r) c (BASE e f)

where BASE is a subst_pairs capture term. Three leaf ROLES fall out of the
kernel, and every role is certified per term, per leaf:

    none        — ``c``: discarded under BOTH calculi ⇒ the negative control,
                  and it sits UPSTREAM of the readout cell
    both        — dependency under BOTH calculi ⇒ the positive control
    naive_only  — ``e``: the correct NF DISCARDS it, the naive NF is BUILT from
                  it ⇒ the discriminator (9 of 18 terms)

Readout cell = the root span's closing token (downstream of every leaf).
Arrival fraction ``(Δ_naive_only − Δ_none) / (Δ_both − Δ_none)`` ≈ 1 means the
discarded-under-correct-semantics argument reaches the term's final cell
(naive); ≈ 0 means it is dropped like the control (capture-avoiding).

Measurables (registers named at freeze, AGENTS.md ``λ measure``):
  M1 value        — subterm-NF first-token rank at the subterm's closing cell
  M2 value        — per-cell normalized residual Δ (the cone substrate)
  M3 value        — D_naive at the readout cell (the headline discriminator)
  M4 value+routing— answer-column necessity lens + value-weighted read-mass
                    (routing half ADVISORY, s206 scar: never bare QK)

``--validate`` drives planted CONE-NAIVE / CONE-CORRECT worlds through the REAL
scoring and gate path (s331: planted plumbing must be probe plumbing). No model
is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from verbum.cone import (
    LeafPerturbation,
    Span,
    annotate,
    leaf_perturbations,
    span_token_range,
    term_names,
)
from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    App,
    Atom,
    Comb,
    Lam,
    Status,
    Term,
    free_vars,
    parse,
    pretty,
    reduce,
)
from verbum.probes.subst_pairs import capture_pairs
from verbum.probes.subst_pairs import validate as subst_validate

# ── frozen constants ────────────────────────────────────────────────────────
REPLS = ("n", "m", "t")  # M3 replication axis (fresh for every battery term)
N_PERM = 10_000
PC1_MIN_RANK_GAIN = 10.0
PC2_MIN_CLIFF = 0.2
ALPHA = 0.05

_FEWSHOT_DIRECT = (
    "Reduce each lambda-calculus term to its normal form, renaming bound "
    "variables as needed to avoid variable capture.\n\n"
    "Term: (λx.x) a\nNormal form: a\n\n"
    "Term: (λx.λy.x) p q\nNormal form: p\n\n"
    "Term: (λf.λx.f (f x)) g z\nNormal form: g (g z)\n\n"
)
_TERM_PREFIX = "Term: "
_TERM_SUFFIX = "\nNormal form:"


_FRESH_BINDERS = ("p", "q", "s", "z", "k", "j")
_SUBST_VAR = "x"  # subst_pairs' substituted variable (the head binder)


def _rename_binder(t: Term, old: str, new: str) -> Term:
    """Rename binder ``old``→``new`` and its BOUND occurrences (scope-correct)."""
    if isinstance(t, Comb | Atom):
        return t
    if isinstance(t, Lam):
        if t.var == old:
            return Lam(new, _rename_bound(t.body, old, new))
        return Lam(t.var, _rename_binder(t.body, old, new))
    return App(_rename_binder(t.fn, old, new), _rename_binder(t.arg, old, new))


def _rename_bound(t: Term, old: str, new: str) -> Term:
    if isinstance(t, Atom):
        return Atom(new) if t.name == old else t
    if isinstance(t, Comb):
        return t
    if isinstance(t, Lam):
        return t if t.var == old else Lam(t.var, _rename_bound(t.body, old, new))
    return App(_rename_bound(t.fn, old, new), _rename_bound(t.arg, old, new))


def _swap_in_scope(t: Term, binder: str, new: str) -> Term:
    """Inside ``λbinder.body``, rewrite ``binder``'s occurrences to ``new``.

    The binder itself is KEPT (it simply goes unused), so the rendering length
    is preserved — the whole point of the matched triple.
    """
    if isinstance(t, Comb | Atom):
        return t
    if isinstance(t, Lam):
        if t.var == binder:
            return Lam(t.var, _rename_bound(t.body, binder, new))
        return Lam(t.var, _swap_in_scope(t.body, binder, new))
    return App(_swap_in_scope(t.fn, binder, new), _swap_in_scope(t.arg, binder, new))


def _shadow_binders(t: Term) -> list[str]:
    """Binders whose name also occurs FREE in the term — the capture sites."""
    free = free_vars(t)
    seen: list[str] = []

    def walk(u: Term) -> None:
        if isinstance(u, Lam):
            if u.var in free and u.var not in seen:
                seen.append(u.var)
            walk(u.body)
        elif isinstance(u, App):
            walk(u.fn)
            walk(u.arg)

    walk(t)
    return seen


def build_variants(base: str) -> dict[str, str] | None:
    """Amendment 3 matched triple — identical layout, one character apart.

    A  : capture live      ⇒ ``e`` is naive_only (correct discards it)
    B  : binders renamed   ⇒ no capture, both NFs agree, ``e`` discarded (none)
    P  : B with the head variable swapped for the binder that receives ``e``
         ⇒ ``e`` is load-bearing under BOTH calculi (the distance-matched
         POSITIVE CONTROL the s335 smoke proved was missing)

    All three render at the same length, so ``e`` sits at the same token in each
    — distance, token identity and prompt length are held fixed by
    construction; only the certified ROLE of that leaf moves.
    """
    a_text = f"{base} e f"
    ta = parse(a_text)
    if pretty(ta) != a_text:
        return None
    shadows = _shadow_binders(ta)
    if not shadows:
        return None
    used = term_names(ta)
    pool = [c for c in _FRESH_BINDERS if c not in used]
    if len(pool) < len(shadows):
        return None
    mapping = dict(zip(shadows, pool[: len(shadows)], strict=True))
    tb = ta
    for old, new in mapping.items():
        tb = _rename_binder(tb, old, new)
    tp = _swap_in_scope(tb, _SUBST_VAR, mapping[shadows[0]])
    out = {"A": pretty(ta), "B": pretty(tb), "P": pretty(tp)}
    if len({len(v) for v in out.values()}) != 1:
        return None  # layout must be identical — no exceptions
    return out


def build_prompt(term_text: str) -> tuple[str, int]:
    """Full prompt + the char offset at which ``term_text`` starts."""
    head = _FEWSHOT_DIRECT + _TERM_PREFIX
    return head + term_text + _TERM_SUFFIX, len(head)


# ── battery ─────────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class TermSpec:
    id: str
    base_term: str
    term: str
    correct_nf: str
    naive_nf: str
    spans: list[Span]
    span_nf: list[str | None]
    root: int  # span index of the whole term (the readout span)
    pair_id: str = ""
    variant: str = ""  # "A" (capture) | "B" (renamed) | "P" (positive control)
    clean_flip: bool = False
    perts: dict[str, list[LeafPerturbation]] = field(default_factory=dict)
    roles: dict[str, str] = field(default_factory=dict)  # leaf name → role


def leaf_role(lp: LeafPerturbation, root: int) -> str:
    """Certified dependency role of a leaf w.r.t. the WHOLE term."""
    inn, inv = root in lp.cone_normal, root in lp.cone_naive
    if inv and not inn:
        return "naive_only"
    if inn and not inv:
        return "correct_only"
    return "both" if inn else "none"


def build_battery() -> list[TermSpec]:
    seen: set[str] = set()
    bases: list[tuple[str, str]] = []
    for p in capture_pairs():
        if p.mode != "direct":
            continue
        canon = pretty(parse(p.term))
        if canon not in seen:
            seen.add(canon)
            bases.append((p.id.replace("_direct", ""), canon))

    out: list[TermSpec] = []
    for pid, bt in bases:
        variants = build_variants(bt)
        if variants is None:
            raise ValueError(f"{pid}: could not build a matched triple")
        specs: dict[str, TermSpec] = {}
        nfs: dict[str, tuple[str, str]] = {}
        for tag, term in variants.items():
            t = parse(term)
            if pretty(t) != term:
                raise ValueError(f"{pid}/{tag}: non-canonical term {term!r}")
            rn, rv = reduce(t, calc=R_NORMAL), reduce(t, calc=R_NAIVE)
            if (
                rn.status is not Status.NORMAL_FORM
                or rv.status is not Status.NORMAL_FORM
            ):
                raise ValueError(f"{pid}/{tag}: does not normalize under both calculi")
            nfs[tag] = (pretty(rn.normal_form), pretty(rv.normal_form))
            text, spans, subterms = annotate(t)
            root = max(range(len(spans)), key=lambda i: spans[i].end - spans[i].start)
            span_nf = []
            for st in subterms:
                r = reduce(st, calc=R_NORMAL)
                span_nf.append(
                    pretty(r.normal_form) if r.status is Status.NORMAL_FORM else None
                )
            names = term_names(t)
            perts = {
                rp: leaf_perturbations(text, repl=rp)
                for rp in REPLS
                if rp not in names
            }
            roles = {
                lp.orig: leaf_role(lp, root)
                for lps in perts.values()
                for lp in lps
            }
            specs[tag] = TermSpec(
                id=f"{pid}_{tag}",
                base_term=bt,
                term=term,
                correct_nf=nfs[tag][0],
                naive_nf=nfs[tag][1],
                spans=spans,
                span_nf=span_nf,
                root=root,
                pair_id=pid,
                variant=tag,
                perts=perts,
                roles=roles,
            )
        # kernel gates on the triple (structure, never data)
        if nfs["A"][0] == nfs["A"][1]:
            raise ValueError(f"{pid}: variant A does not discriminate")
        for tag in ("B", "P"):
            if nfs[tag][0] != nfs[tag][1]:
                raise ValueError(f"{pid}/{tag}: still captures (NFs disagree)")
        clean = (
            specs["A"].roles.get("e") == "naive_only"
            and specs["B"].roles.get("e") == "none"
            and specs["P"].roles.get("e") == "both"
        )
        for tag in ("A", "B", "P"):
            s = specs[tag]
            out.append(
                TermSpec(
                    id=s.id, base_term=s.base_term, term=s.term,
                    correct_nf=s.correct_nf, naive_nf=s.naive_nf, spans=s.spans,
                    span_nf=s.span_nf, root=s.root, pair_id=s.pair_id,
                    variant=s.variant, clean_flip=clean, perts=s.perts,
                    roles=s.roles,
                )
            )
    return out


def battery_hash(battery: list[TermSpec]) -> str:
    blob = json.dumps(
        [[b.id, b.term, b.correct_nf, b.naive_nf] for b in battery], sort_keys=True
    )
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


# ── backends (real HF host / planted world; identical downstream path) ──────
@dataclass
class Prepared:
    offsets: list[tuple[int, int]]
    resid: np.ndarray  # (L, T, D)
    text: str = ""

    @property
    def n_tokens(self) -> int:
        return len(self.offsets)


class PlantedBackend:
    """Synthetic char-tokenized world planting a KNOWN cone (validate only).

    Planting is keyed by the perturbed prompt TEXT — per perturbation, never
    per term: a per-term union would make one leaf's out-of-cone cells another
    leaf's in-cone cells and wash out the very contrast under test (caught by
    this validation path, s335).
    """

    def __init__(self, n_layers: int = 8, d: int = 16):
        self.L, self.D = n_layers, d
        self.cone_by_text: dict[str, set[int]] = {}
        self.good_rank_pos: set[int] = set()

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        return [(i, i + 1) for i in range(len(text))]

    def prepare(self, text: str, *, perturbed_char: int | None = None) -> Prepared:
        offs = self.tokenize(text)
        resid = (
            np.random.default_rng(1234)
            .standard_normal((self.L, len(offs), self.D))
            .astype(np.float32)
        )
        cone = self.cone_by_text.get(text)
        if perturbed_char is None or cone is None:
            return Prepared(offs, resid, text)
        jitter = 1.0 + 0.05 * (hash(text) % 7)  # replicate-level noise
        raw = np.random.default_rng(99).standard_normal((self.L, self.D))
        bump = raw * 3.0 * jitter
        resid = resid.copy()
        resid[:, perturbed_char, :] += bump.astype(np.float32)
        for c in cone:
            if c > perturbed_char:
                resid[:, c, :] += (bump * 0.6).astype(np.float32)
        return Prepared(offs, resid, text)

    def ranks(self, prep: Prepared, pos: int, token_strs: list[str]) -> np.ndarray:
        out = np.full((len(token_strs), self.L), 5000.0, dtype=np.float64)
        if pos in self.good_rank_pos:
            out[:, self.L // 2 :] = 3.0
        return out

    def read_mass(self, prep: Prepared, ans_pos: int) -> np.ndarray | None:
        return None


class HFBackend:
    """HF host (Qwen/LLaMA/Pythia): prefill grid + logit-lens + read-mass."""

    def __init__(self, model_id: str, device: str, dtype: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        from verbum import jlens

        self.torch, self.jlens = torch, jlens
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id, dtype=getattr(torch, dtype), attn_implementation="eager"
            )
            .to(device)
            .eval()
        )
        self.device = device
        self.L = jlens.n_layers(self.model)

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        enc = self.tok(text, return_offsets_mapping=True, add_special_tokens=True)
        return [tuple(o) for o in enc["offset_mapping"]]

    def prepare(self, text: str, *, perturbed_char: int | None = None) -> Prepared:
        offs = self.tokenize(text)
        resids, _ids = self.jlens.capture_residuals(self.model, self.tok, text)
        grid = np.stack([resids[i].numpy() for i in range(self.L)], axis=0)
        return Prepared(offs, grid.astype(np.float32), text)

    def ranks(self, prep: Prepared, pos: int, token_strs: list[str]) -> np.ndarray:
        torch = self.torch
        h = torch.from_numpy(prep.resid[:, pos, :])
        logits = self.jlens.logit_lens(self.model, h).float().cpu()  # (L, V)
        ids = [self.tok(s, add_special_tokens=False).input_ids[0] for s in token_strs]
        out = np.zeros((len(ids), logits.shape[0]), dtype=np.float64)
        for k, tid in enumerate(ids):
            out[k] = (logits > logits[:, tid : tid + 1]).sum(dim=-1).numpy() + 1.0
        return out

    def read_mass(self, prep: Prepared, ans_pos: int) -> np.ndarray | None:
        """Value-weighted attention from the answer column (s206: never bare QK)."""
        torch = self.torch
        inputs = self.tok(prep.text, return_tensors="pt").to(self.device)
        vnorms: dict[int, np.ndarray] = {}
        handles = []

        def mk(i: int):
            def hook(_m, _inp, out):
                v = out[0] if isinstance(out, tuple) else out
                vnorms[i] = v[0].float().norm(dim=-1).detach().cpu().numpy()

            return hook

        try:
            for i, layer in enumerate(self.model.model.layers):
                handles.append(layer.self_attn.v_proj.register_forward_hook(mk(i)))
            with torch.no_grad():
                out = self.model(**inputs, output_attentions=True)
            mass = np.zeros((self.L, prep.n_tokens), dtype=np.float64)
            for i, att in enumerate(out.attentions):
                w = att[0, :, ans_pos, :].float().cpu().numpy().mean(axis=0)
                vn = vnorms.get(i)
                if vn is not None and vn.shape[0] == w.shape[0]:
                    w = w * vn
                s = w.sum()
                mass[i] = w / s if s > 0 else w
            return mass
        except (AttributeError, RuntimeError) as exc:  # visible failure, never silent
            print(f"[pc] read_mass unavailable: {exc}", flush=True)
            return None
        finally:
            for h in handles:
                h.remove()


# ── analysis primitives ─────────────────────────────────────────────────────
def delta_grid(orig: Prepared, pert: Prepared) -> np.ndarray | None:
    """Normalized per-cell residual distance ``(L, T)``; ``None`` if the two
    tokenizations do not align (a hard skip, never a silent fudge)."""
    if orig.offsets != pert.offsets:
        return None
    num = np.linalg.norm(orig.resid - pert.resid, axis=-1)
    den = np.linalg.norm(orig.resid, axis=-1) + 1e-6
    return num / den


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float((gt - lt) / (a.size * b.size))


def perm_p_paired(diffs: np.ndarray, rng, n_perm: int = N_PERM) -> float:
    """Two-sided sign-flip permutation p on paired differences."""
    if diffs.size == 0:
        return 1.0
    obs = abs(float(diffs.mean()))
    signs = rng.choice([-1.0, 1.0], size=(n_perm, diffs.size))
    null = np.abs((signs * diffs[None, :]).mean(axis=1))
    return float((np.sum(null >= obs) + 1) / (n_perm + 1))


def base_token(prep: Prepared, base: int) -> int:
    for i, (_s, e) in enumerate(prep.offsets):
        if e > base:
            return i
    return 0


def score_term(backend, spec: TermSpec, *, do_m1: bool, do_mass: bool) -> dict:
    """All measurables for one term → one results.jsonl record."""
    prompt, base = build_prompt(spec.term)
    orig = backend.prepare(prompt)
    cells = [span_token_range(s.start, s.end, orig.offsets, base) for s in spec.spans]
    ans_pos = orig.n_tokens - 1
    rec: dict[str, Any] = {
        "term_id": spec.id,
        "pair_id": spec.pair_id,
        "variant": spec.variant,
        "clean_flip": spec.clean_flip,
        "offsets_sig": hashlib.sha256(
            json.dumps(orig.offsets).encode()
        ).hexdigest()[:12],
        "term": spec.term,
        "correct_nf": spec.correct_nf,
        "naive_nf": spec.naive_nf,
        "roles": spec.roles,
        "n_tokens": orig.n_tokens,
        "n_layers": int(orig.resid.shape[0]),
        "leaves": [],
        "m1": [],
        "pc0": {},
        "error": None,
    }
    if any(c is None for c in cells):
        rec["error"] = "span_token_mapping_failed"
        return rec
    readout = cells[spec.root][1]
    rec["readout_tok"] = readout

    causal_max, leaf_min = 0.0, float("inf")
    for repl, lps in spec.perts.items():
        for lp in lps:
            rng_ = span_token_range(lp.start, lp.end, orig.offsets, base)
            if rng_ is None:
                continue
            leaf_tok = rng_[1]
            pert_prompt, _ = build_prompt(lp.pert_text)
            pert = backend.prepare(pert_prompt, perturbed_char=base + lp.start)
            d = delta_grid(orig, pert)
            if d is None:
                rec["leaves"].append(
                    {"repl": repl, "leaf": lp.orig, "error": "token_misalignment"}
                )
                continue
            cell = d.mean(axis=0)  # mean over layers → (T,)
            causal_max = max(causal_max, float(cell[:leaf_tok].max(initial=0.0)))
            leaf_min = min(leaf_min, float(cell[leaf_tok]))
            rec["leaves"].append(
                {
                    "repl": repl,
                    "leaf": lp.orig,
                    "role": leaf_role(lp, spec.root),
                    "leaf_tok": leaf_tok,
                    "delta_readout": float(cell[readout]),
                    "delta_answer": float(cell[ans_pos]),
                    "delta_profile_layers": [
                        float(x) for x in d[:, readout]
                    ],  # depth advisory
                    "error": None,
                }
            )
    rec["pc0"] = {
        "causal_max_upstream_delta": causal_max,
        "leaf_min_delta": None if leaf_min == float("inf") else leaf_min,
    }

    if do_m1:
        rng = np.random.default_rng(abs(hash(spec.id)) % (2**32))
        by_pos: dict[int, list[tuple[int, str]]] = {}
        for i, s in enumerate(spec.spans):
            if spec.span_nf[i] is None or s.kind == "comb":
                continue
            by_pos.setdefault(cells[i][1], []).append((i, " " + spec.span_nf[i]))
        pool = [p for p in range(base_token(orig, base), ans_pos)]
        for pos, items in by_pos.items():
            toks = [t for _, t in items]
            actual = backend.ranks(orig, pos, toks)
            alt = [p for p in pool if p != pos] or [pos]
            npos = int(rng.choice(alt))
            null = backend.ranks(orig, npos, toks)
            for k, (i, _t) in enumerate(items):
                rec["m1"].append(
                    {
                        "span": i,
                        "tok": pos,
                        "nf": spec.span_nf[i],
                        "best_rank": float(actual[k].min()),
                        "best_layer": int(actual[k].argmin()),
                        "null_pos": npos,
                        "null_best_rank": float(null[k].min()),
                    }
                )

    c_tok, n_tok = " " + spec.correct_nf, " " + spec.naive_nf
    if c_tok != n_tok:
        r = backend.ranks(orig, ans_pos, [c_tok, n_tok])
        rec["m4_necessity"] = {
            "correct_final_rank": float(r[0][-1]),
            "naive_final_rank": float(r[1][-1]),
            "favors_correct_final": bool(r[0][-1] < r[1][-1]),
        }
    if do_mass:
        mass = backend.read_mass(orig, ans_pos)
        if mass is not None:
            interior = list(range(base_token(orig, base), ans_pos))
            rec["m4_read_mass"] = {
                "interior_mass_final_layer": float(mass[-1, interior].sum()),
                "profile": [float(x) for x in mass[:, interior].sum(axis=1)],
            }
    return rec


# ── gates ───────────────────────────────────────────────────────────────────
def _leaf_means(rec: dict, key: str = "delta_readout") -> dict[str, float]:
    """Per-LEAF mean Δ at the readout cell (averaged over replacement atoms)."""
    acc: dict[str, list[float]] = {}
    for lv in rec.get("leaves", []):
        if lv.get("error"):
            continue
        acc.setdefault(lv["leaf"], []).append(lv[key])
    return {k: float(np.mean(v)) for k, v in acc.items()}


def _pair_dids(recs: list[dict]) -> dict[str, Any]:
    """Amendment 3 difference-in-differences, grouped by matched triple.

    Position, token identity and prompt length are held fixed across A/B/P; only
    the kernel-certified ROLE of leaf ``e`` moves. Distance — which the s335
    smoke proved dominates raw Δ (corr −0.73) — therefore cancels.
    """
    by_pair: dict[str, dict[str, dict]] = {}
    for r in recs:
        if r.get("error") is None and r.get("pair_id"):
            by_pair.setdefault(r["pair_id"], {})[r["variant"]] = r
    flip, pos, placebo, arrivals, misaligned = [], [], [], [], 0
    for _pid, vs in sorted(by_pair.items()):
        if not {"A", "B", "P"} <= vs.keys():
            continue
        if len({vs[t]["offsets_sig"] for t in ("A", "B", "P")}) != 1:
            misaligned += 1  # layout not identical after tokenization → drop
            continue
        mA, mB, mP = (_leaf_means(vs[t]) for t in ("A", "B", "P"))
        rolesA = vs["A"]["roles"]
        rolesB = vs["B"]["roles"]
        for leaf in sorted(set(rolesA) & set(rolesB) - {"e"}):
            if rolesA[leaf] == rolesB[leaf] and leaf in mA and leaf in mB:
                placebo.append(mA[leaf] - mB[leaf])
        if not vs["A"].get("clean_flip") or not all("e" in m for m in (mA, mB, mP)):
            continue
        d_flip, d_pos = mA["e"] - mB["e"], mP["e"] - mB["e"]
        flip.append(d_flip)
        pos.append(d_pos)
        if abs(d_pos) > 1e-9:
            arrivals.append(d_flip / d_pos)
    return {
        "flip": np.array(flip),
        "pos": np.array(pos),
        "placebo": np.array(placebo),
        "arrivals": np.array(arrivals),
        "n_pairs": len(by_pair),
        "n_misaligned": misaligned,
    }


def compute_gates(recs: list[dict], rng) -> dict:
    good = [r for r in recs if r.get("error") is None]

    causal = max((r["pc0"].get("causal_max_upstream_delta", 1.0) for r in good),
                 default=1.0)
    leafd = [r["pc0"]["leaf_min_delta"] for r in good
             if r["pc0"].get("leaf_min_delta") is not None]
    pc0 = {
        "n_terms": len(good),
        "n_errors": len(recs) - len(good),
        "causal_max_upstream_delta": float(causal),
        "causal_ok": bool(causal < 1e-3),
        "leaf_delta_min": float(min(leafd)) if leafd else 0.0,
        "leaf_moves_ok": bool(leafd and min(leafd) > 1e-2),
    }
    pc0["pass"] = bool(pc0["causal_ok"] and pc0["leaf_moves_ok"] and good)

    gains = np.array(
        [m["null_best_rank"] - m["best_rank"] for r in good for m in r["m1"]]
    )
    p1 = perm_p_paired(gains, rng) if gains.size else 1.0
    pc1 = {
        "n_cells": int(gains.size),
        "median_rank_gain": float(np.median(gains)) if gains.size else 0.0,
        "p": p1,
        "pass": bool(
            gains.size and float(np.median(gains)) >= PC1_MIN_RANK_GAIN and p1 < ALPHA
        ),
    }
    pc1["qualifier"] = "INTERIOR-VISIBLE" if pc1["pass"] else "LAST-COLUMN-ONLY"

    did = _pair_dids(good)

    # PC0b — placebo: role-unchanged leaves must show NO DiD (layout artifact
    # detector; without it a rendering/tokenization asymmetry could masquerade
    # as semantics)
    plac = did["placebo"]
    p_pl = perm_p_paired(plac, rng) if plac.size else 1.0
    pc0["placebo_n"] = int(plac.size)
    pc0["placebo_mean_did"] = float(plac.mean()) if plac.size else 0.0
    pc0["placebo_p"] = p_pl
    pc0["placebo_ok"] = bool(plac.size == 0 or p_pl >= ALPHA)
    pc0["n_misaligned_pairs"] = int(did["n_misaligned"])
    pc0["pass"] = bool(pc0["pass"] and pc0["placebo_ok"])

    # PC2 — POSITIVE CONTROL, distance-matched: leaf `e` load-bearing (P) vs
    # discarded (B) at the same cell. Does the instrument see semantics at all?
    pos = did["pos"]
    p2 = perm_p_paired(pos, rng) if pos.size else 1.0
    cd = cliffs_delta(pos, np.zeros_like(pos)) if pos.size else 0.0
    pc2 = {
        "n_pairs": int(pos.size),
        "mean_DiD_pos": float(pos.mean()) if pos.size else 0.0,
        "median_DiD_pos": float(np.median(pos)) if pos.size else 0.0,
        "n_positive": int((pos > 0).sum()),
        "cliffs_delta": cd,
        "p": p2,
        "pass": bool(
            pos.size and cd >= PC2_MIN_CLIFF and p2 < ALPHA and pos.mean() > 0
        ),
    }

    # PC3 — the headline DiD: does the argument the CORRECT calculus discards
    # still reach the readout cell?
    flip, arr = did["flip"], did["arrivals"]
    p3 = perm_p_paired(flip, rng) if flip.size else 1.0
    pc3 = {
        "n_pairs": int(flip.size),
        "D_naive": float(flip.mean()) if flip.size else 0.0,
        "median_D": float(np.median(flip)) if flip.size else 0.0,
        "n_positive": int((flip > 0).sum()),
        "median_arrival_fraction": float(np.median(arr)) if arr.size else None,
        "p": p3,
        "sig": bool(flip.size and p3 < ALPHA),
        "sign": int(np.sign(flip.mean())) if flip.size else 0,
    }

    nec = [r["m4_necessity"] for r in good if "m4_necessity" in r]
    pc4 = {
        "n": len(nec),
        "frac_favors_correct_final": (
            float(np.mean([x["favors_correct_final"] for x in nec])) if nec else None
        ),
        "median_correct_final_rank": (
            float(np.median([x["correct_final_rank"] for x in nec])) if nec else None
        ),
        "median_naive_final_rank": (
            float(np.median([x["naive_final_rank"] for x in nec])) if nec else None
        ),
    }
    return {
        "PC0": pc0, "PC1": pc1, "PC2": pc2, "PC3": pc3, "PC4": pc4,
        "verdict": decide(pc0, pc2, pc3),
    }


def decide(pc0: dict, pc2: dict, pc3: dict) -> str:
    """The frozen verdict tree (s335; estimator per Amendment 3).

    PC0 covers sanity AND the placebo (layout-artifact) check; PC2 is the
    distance-matched positive control — without it firing, a null in PC3 is
    uninformative and the verdict is DIFFUSE/NO-CONE, never CONE-CORRECT.
    """
    if not pc0["pass"]:
        return "VOID"
    if not pc2["pass"]:
        return "DIFFUSE/NO-CONE"
    if pc3["sig"] and pc3["sign"] > 0:
        return "CONE-NAIVE"
    if pc3["sig"] and pc3["sign"] < 0:
        return "CONE-CORRECT"
    if not pc3["n_pairs"]:
        return "CONE-UNDIFFERENTIATED"
    arr = pc3["median_arrival_fraction"]
    if arr is not None and arr < 0.5:
        # positive control fired; the discarded argument did not arrive
        return "CONE-CORRECT"
    return "CONE-UNDIFFERENTIATED"


# ── planted-world validation ────────────────────────────────────────────────
def validate() -> bool:
    ok = True
    print("[validate] subst_pairs battery ...")
    ok &= bool(subst_validate())

    battery = build_battery()
    pairs = {s.pair_id for s in battery}
    clean = {s.pair_id for s in battery if s.clean_flip}
    print(
        f"[validate] battery: {len(battery)} variants / {len(pairs)} triples "
        f"(hash {battery_hash(battery)}); clean flips: {len(clean)}"
    )
    ok &= len(battery) == 3 * len(pairs) and len(clean) == 9

    for s in battery:  # the matched triple must hold layout fixed
        sibs = [b for b in battery if b.pair_id == s.pair_id]
        assert len({len(b.term) for b in sibs}) == 1, s.pair_id
    print("[validate] every triple is length-matched (A/B/P) ✓")
    for s in battery:
        if s.variant == "A" and s.clean_flip:
            assert s.roles["e"] == "naive_only", s.id
        if s.variant == "B" and s.clean_flip:
            assert s.roles["e"] == "none", s.id
        if s.variant == "P" and s.clean_flip:
            assert s.roles["e"] == "both", s.id
    print("[validate] certified role flip e: naive_only(A) → none(B) → both(P) ✓")

    for world, want in (("naive", "CONE-NAIVE"), ("correct", "CONE-CORRECT")):
        be = PlantedBackend()
        recs = []
        for spec in battery:
            _p, base = build_prompt(spec.term)
            be.good_rank_pos = {
                base + s.end - 1 for s in spec.spans if s.kind != "comb"
            }
            for lps in spec.perts.values():
                for lp in lps:
                    ids = lp.cone_naive if world == "naive" else lp.cone_normal
                    pp, _ = build_prompt(lp.pert_text)
                    be.cone_by_text[pp] = {base + spec.spans[i].end - 1 for i in ids}
            recs.append(score_term(be, spec, do_m1=True, do_mass=False))
        g = compute_gates(recs, np.random.default_rng(0))
        print(
            f"[validate] world={world!r}: verdict={g['verdict']} | "
            f"PC0 {g['PC0']['pass']} placebo_p={g['PC0']['placebo_p']:.3f} | "
            f"PC2 DiD+={g['PC2']['median_DiD_pos']:.3f} p={g['PC2']['p']:.4f} | "
            f"PC3 D={g['PC3']['D_naive']:.3f} p={g['PC3']['p']:.4f} "
            f"n={g['PC3']['n_pairs']} arrival={g['PC3']['median_arrival_fraction']}"
        )
        ok &= g["verdict"] == want
    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return bool(ok)


# ── provenance ──────────────────────────────────────────────────────────────
def git_sha() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2]
            )
            .decode()
            .strip()
        )
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def write_meta(out: Path, args, battery: list[TermSpec], gates: dict) -> None:
    import platform

    meta = {
        "run_id": out.name,
        "probe": "P-PREFILL-CONE",
        "frozen": "s335 (freeze) + Amendment 1 + Amendment 2 (both pre-data)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id,
        "device": args.device,
        "dtype": args.dtype,
        "seed": args.seed,
        "smoke": bool(args.smoke),
        "n_terms": len(battery),
        "battery_hash": battery_hash(battery),
        "probe_shape": "(λd.λr.r) c (BASE e f)",
        "repls": list(REPLS),
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "gates": gates,
    }
    try:
        import torch
        import transformers

        meta["lib_versions"] = {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "numpy": np.__version__,
        }
    except ImportError:
        meta["lib_versions"] = {"numpy": np.__version__}
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-m1", action="store_true")
    ap.add_argument("--mass-terms", type=int, default=3)
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    battery = build_battery()
    if args.smoke:
        battery = battery[:3]
    print(
        f"[pc] battery={len(battery)} hash={battery_hash(battery)} "
        f"model={args.model_id} dtype={args.dtype}",
        flush=True,
    )
    backend = HFBackend(args.model_id, args.device, args.dtype)
    recs = []
    for i, spec in enumerate(battery):
        rec = score_term(
            backend, spec, do_m1=not args.no_m1, do_mass=i < args.mass_terms
        )
        recs.append(rec)
        print(f"[pc] {i + 1}/{len(battery)} {spec.id} err={rec['error']}", flush=True)

    gates = compute_gates(recs, np.random.default_rng(args.seed + 99))
    print(json.dumps(gates, indent=2, default=str))
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "results.jsonl").open("w") as fh:
            for r in recs:
                fh.write(json.dumps(r, default=str) + "\n")
        (out / "gates.json").write_text(json.dumps(gates, indent=2, default=str))
        (out / "battery.json").write_text(
            json.dumps(
                [
                    {
                        "id": s.id, "term": s.term, "correct_nf": s.correct_nf,
                        "naive_nf": s.naive_nf, "roles": s.roles,
                    }
                    for s in battery
                ],
                indent=2,
            )
        )
        write_meta(out, args, battery, gates)
        print(f"[pc] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Thinking

Now I'm setting up the cone routing experiment script with the frozen design parameters: using matched triples from the variant builder as substrate, running inference on Qwen3-14B in bf16 precision with eager attention, and implementing value-weighted attention for the readout mechanism that respects grouped query attention projections.

For the statistics, I'm computing primary ρ_e at the answer column position using the mass difference between variants A and B normalized by the P-B range, and secondary ρ_Sel from the within-prompt difference between y and e argument positions, which cancels the positional asymmetry across variants through the same calibrated ratio formula.

I need to check that ρ_Sel and ρ_e agree in direction—both should fall on the same side of 0.5 to indicate consistent behavior. The key insight is that in variant B, the binder y gets renamed to p, but the free argument y token stays at the same position across all three variants, so I can reliably measure the y-e difference in each case. build_variants constructs the probe terms by appending the e and f arguments to each base, and build_battery pulls those base terms directly from the capture_pairs results — the wrapper structure might already be baked into those terms, but either way I'm reusing the same build_variants and build_battery functions to generate the test cases.

For the routing probe, I should import build_battery directly from prefill_cone rather than duplicating code. Since prefill_cone is in scripts/experiments and not a package, I'll add its directory to sys.path alongside the src directory, then import the needed functions like build_battery, build_prompt, TermSpec, and the hash utilities.

Now for the read_mass function: it needs to compute per-source-position mass in a GQA-aware way. The prefill_cone approach uses output_attentions with eager attention and a v_proj hook to get per-token v-norms. The current check compares v-norm shape (T,) against attention weight shape (T,), which works but treats all kv heads as a single combined norm. For better fidelity I should compute per-kv-head mass instead.

Reshaping v_proj output to separate kv heads... The positions of e and f are straightforward—e at len(base)+1 and f at len(base)+3. For the y argument, I need to look at what gets captured across the different triples; the free variable pool includes y, w, and u, so I'm tracking which one is actually the captured variable in each case. The key insight is that the correct normal form's head is determined by whichever free variable gets shadowed by the first binder, so I should define a `cap_var` per triple that identifies this shadowed free variable from the shadow binders list.

For the generic approach, I'm finding two critical positions in each variant: the character position of the "e" atom (the appended argument, which appears once as a free atom) and the position of the cap_var's free occurrence in the term (the argument occurrence that also appears in A). So in the normalized form P reduces to just `e f`, but the `y` argument is still textually present in the original expression, which means its position stays consistent across all three variants. For identifying the binder position, I'm looking at the lambda spans to find where the variable character starts—since all variables in the pool are single characters, that's just the lambda span start plus one. The binder I need to track is the one that got renamed, which corresponds to the first shadow mapping, so in A it's the lambda with the variable matching cap_var, while in B and P I'm finding the lambda at the corresponding position after the renaming.

To locate this generically, I can compare A and B character by character to find where they differ, then identify positions where A's character matches cap_var—those positions mark both the binder and its bound occurrences. In the build_variants function, the head variable x gets rewritten to whatever the renamed first-shadow binder is called, so in P those occurrences of x in the body become references to that renamed binder (the capture site). I can recompute cap_var for each triple by parsing A, extracting shadow binders, and taking the first one—_shadow_binders is available from prefill_cone. For measuring mass, I need to track token positions: the e argument (a free atom "e" span that should be identical across all variants), and the cap argument (the free atom cap_var span, specifically its last/argument occurrence where free_leaf is true), though A may also contain the binder occurrence which isn't a simple atom span.

Now I'm working through whether cap_var has bound occurrences in A—the argument y in (λx.λy.x) y e f is free because it's outside the λy scope, and annotate marks this based on enclosing binders. So the free atom cap_var is the argument occurrence, but there could be multiple free occurrences across different bases from subst_pairs, and I need to identify which span to use.

For the diagnostic approach: I'll collect all free atom spans of cap_var since free occurrences stay identical between A and B (only binder and bound occurrences get renamed), then measure the binder_mass on positions where A and B texts differ. I also need to handle the position-matched control for the distance gap between y and e from the readout.

The pole contrast itself serves as the distance control—B and P have identical geometry but opposite answers, so if mass followed distance alone, the mass values would match between them and RC1 would fail. I'll report mass at e and y positions in B and P as a function of the pole answers to show this relationship.

For the statistics, I need to figure out how to aggregate across layers into a single scalar per triple. The readout uses head-mean with per-layer normalization, and RC1 tests whether mass at the result cell tracks the answer on capture-free variants—specifically checking if mass_P(e) > mass_B(e) in paired comparisons across the triples with p<0.05 and Cliff's δ ≥ 0.2.

The key constraint is that only the 9 clean-flip triples have valid pole contrasts where P's answer head equals e and B's answer doesn't, so RC1 should run over just those 9 pairs rather than all 18 to keep the analysis consistent. I'll use clean triples for the primary analysis, but report both clean and all-18 results. For layer aggregation, I'm going with layer-mean of normalized mass as the main scalar since it's simple and pre-declared, while storing per-layer values and computing a best-layer advisory for RC4 reference.

The RC1 pole calibration actually gives us protection here—if layer-mean proves too diluted, RC1 will fail and flag NO-CALIBRATION honestly. But I could also pre-register a secondary approach: selecting layers where poles cleanly separate based on the calibration data itself (using only B/P distinctions, not A), which aligns with the freeze's own framing of training on unambiguous cases and classifying the ambiguous one. For the one-sided sign-flip test, I'm checking if the observed mean difference is greater than zero under the null, then computing Cliff's delta on the paired differences against zero and requiring the mean to be positive. I'll also check the corroboration condition where selectivity is higher for B than P, though I'm treating that as informational rather than a hard requirement for RC1 to pass — the primary condition is just the mass difference itself. For RC2, I'm computing the effect size as a ratio of mean differences, then bootstrapping the median across the nine triples with replacement to get a 95% confidence interval—the CI needs to exclude 0.5 to pass. I'll also guard against inverted calibration by excluding any triple where the denominator falls at or below zero, tracking how many get filtered out, then take the median over the remaining valid triples.

For RC3, I'm checking whether the selectivity effect size follows the same direction as the efficacy effect size—if the signs of their medians relative to 0.5 disagree, the result is undifferentiated. On the nulls side, I need to verify that the placebo arm doesn't discriminate between variants by testing whether mass differences at the placebo frequency are statistically insignificant across the A−B and P−B comparisons.

If the placebo gate fires—meaning the placebo does discriminate when it shouldn't—that's a red flag for a global offset artifact, similar to what happened in s335. Since the ρ_e ratio is calibrated, multiplicative offsets cancel out but additive ones partially persist. I'm treating a failed placebo check as an RC0-level violation that would void the result, folding it into the RC0 failure category.

But with paired n=9 and tiny variance, even trivial differences might register as statistically significant while the actual effect-size calibration remains sound. So I'll gate the placebo failure on effect size: it only fails if the mean difference at f is at least half the magnitude of the mean pole separation at e AND p<0.05. That way the placebo must carry discrimination comparable to the signal to trigger a void. I'll declare this threshold in the metadata.

For the shuffled-variant-label null, I'm leveraging the permutation test already in place—shuffling B/P labels within triples is equivalent to sign-flipping for paired data. I'll additionally shuffle the e index to test whether the calibration holds under label randomization.

I'm also implementing a position-matched distance control: since the poles are geometrically identical, distance cancels out in ρ_e by construction, but I'll report the mass-versus-distance profile explicitly to show that separation persists despite identical distances. The raw mass sums per layer before value-weighting... Now I'm setting up the decision tree for the routing verdict: if the baseline checks fail, mark it void or uncalibrated; otherwise, compare the confidence interval against the threshold and check directional agreement to determine whether we're seeing naive or correct routing behavior. Then I need to build the planted worlds backend that generates test grids—one where the naive routing matches the planted distribution closely while the other agent stays low, and another where the correct routing aligns with the planted mass. Writing position extraction... I need to optimize the measurement process so there's only one forward pass per variant instead of two. Rather than calling the model separately for attention and for the mass computation, I'll run a single forward pass with `output_attentions=True` and extract attention values for both the answer column and term final positions. I'll also add a deterministic repeat of the first variant as a sanity check, then normalize the mass values per layer.

For storage, I'm computing layer-wise mean mass across the time dimension and extracting mass values at the key source positions (e_tok, cap_tok, f_tok, binder_toks). The full mass grids are around 1MB per variant, so I'll save those as an npz file keyed by term and cell. Each record will contain the term ID, pair ID, variant label, and a nested structure with mass measurements at each cell position plus per-layer breakdowns.

Gates are derived from the clean triples with the answer column as the primary cell and term_final as secondary. For smoke testing, I'm limiting to the first 2 triples (6 variants) on the 4B model. The default model is Qwen3-14B instruct with MPS bf16 precision and eager attention enabled.

For dtype handling, I'm using bfloat16 by default, though attention probabilities in bf16 are fine since output_attentions returns post-softmax weights that can be cast to float. I'll reuse the same few-shot prompt from build_prompt without a chat template, matching the frozen substrate setup. For the RC2 bootstrap, I'm resampling the ρ_e values across the triples after exclusion, computing a 10k-sample percentile confidence interval [2.5, 97.5] of the median to check if it excludes 0.5.

For RC3, I'm computing ρ_Sel with the same exclusion logic—the denominator Sel_P − Sel_B should be negative since the P answer head (e) produces smaller mass than the B answer head (y), making Sel_P smaller than Sel_B. The formula ρ_Sel = (Sel_A − Sel_B)/(Sel_P − Sel_B) has the same structure as ρ_e, so if A aligns with P, ρ_Sel ≈ 1. I exclude cases where the denominator has the wrong sign (≥0), then check whether the median ρ values agree in direction.

Now I'm setting up a bootstrap with n=9 samples of the median. For the planted backend, I'm using a character tokenizer to generate mass rows with different scenarios: in the NAIVE world, variants A and P get bumped mass at the e token while B stays low, and y is high in B but low in P and A; the CORRECT world has A reading like B with y high in both, while e is only high in P; and the NOCAL world has uniform mass everywhere with no bumps.

The key challenge is how to plant the signal — rather than keying by position directly (which would bypass the real extraction), the planted backend should know the world type and compute mass based on the prompt text and cell content, letting the harness extract positions through the same code path being tested. I can plant by text by having the function locate characters like 'e', 'f', and the capital variant in the term region, then configure the backend per-variant before preparation, similar to how s335 does planted cone_by_text keying.

For validation, I'll set up the bump weights keyed by text with positions derived from spec spans, so the scoring path reads mass through the same extraction mechanism — the extraction itself gets validated separately by assertions checking for single occurrence and alignment across the triple. Adding small random jitter per position keeps the stats non-degenerate, with per-triple jitter for bootstrap variety.

The verdict mapping is straightforward: NAIVE maps to NAIVE-ROUTING, CORRECT to CORRECT-ROUTING, NOCAL to NO-CALIBRATION, and I need to verify the placebo doesn't trigger. Deterministic repetition in the planted setup works fine by keying the preparation deterministically on text hash.

Now I'm setting up the HuggingFace backend to run a single forward pass, collecting value vectors per layer and computing attention-based mass estimates...

Actually, there's a memory concern with storing full attention matrices across all layers and heads — that could balloon to over 100MB. Instead, I'll extract only the attention rows for the specific query positions we care about, which the caller determines after tokenization.

This creates an ordering problem though: the cells we need depend on the offsets from tokenization. So I'm splitting this into two phases — the caller first tokenizes the text to figure out which cells to analyze, then calls the mass function with those cells specified.

For the mass function itself, I'm iterating through each layer to grab the attention row at each cell position, then handling the value norm expansion carefully since KV heads are grouped across query heads. I need to repeat the value norms correctly so each query head gets the right KV head's norms.

After computing the weighted attention (attention × value norms), I'm averaging across heads to get a per-token mass value, then normalizing so the attention sums to 1. I'm also checking that the raw attention row sums are close to 1 (within 1e-2 for bf16 precision) to validate the softmax worked correctly.

For determinism, I'm running the forward pass twice on the first variant and comparing the computed masses with a tight tolerance—if they don't match, the test fails, though MPS might introduce some nondeterminism so I'm allowing a small relative tolerance around 1e-6.

Now I'm setting up the placebo effect-size rule: if the p-value is below 0.05 AND the mean difference is at least half the pole separation, the test fails. The tricky part is that if pole separation is near zero, the placebo threshold becomes unreliable and could fire spuriously, so I need to handle that case carefully to avoid false voids.

I'm refining the placebo gate to use an absolute threshold too—it only triggers if the mean difference exceeds either half the pole separation or 0.005 mass units (whichever is larger), and the p-value is below 0.05. This ensures that even with tiny pole separations, we catch real global artifacts. I need to document this in the metadata.

I'm organizing the output files: results.jsonl per variant, gates.json, mass.npz, meta.json, and battery.json. The metadata should note that three advisory read-mass records from a different run were excluded. I'm also verifying the TermSpec fields I need and locating the term-final interior cell within the root span.

Now I'm extracting the answer column position and working through the cap_var extraction logic, importing the shadow binders to identify free atoms. For each triple, I'm checking that 'e' and 'f' appear exactly once in the same position across variants, and handling cap_var cases where multiple free atoms might exist by selecting the last occurrence.

The battery has 18 clean triples with RC1/RC2 applied to 9 of them, but all 54 variants still run as frozen forwards. Non-clean triples contribute diagnostic data, and the placebo pool uses 'f' across all aligned triples for power. Placebo contrasts compare A−B and P−B at the 'f' position.

Writing the code... Now I'm working through the position extraction logic — building a function that iterates through the spec's spans to identify free atoms and extract their term positions. I need to be careful about what "free" means here: in lambda expressions, free variables are those not bound by any enclosing lambda, while bound variables are parameters or references within the scope. For the diagnostic comparing two specs, I'm looking at character-level differences where spec A contains the original binder and bound occurrences, while spec B and P have renamed pool characters instead.

Building the per-variant record structure... Computing gate conditions for the clean subset of aligned triples, checking for significant differences between variants using one-sided tests for the main effect and two-sided tests for placebo contrasts, then calculating correlation metrics with bootstrap confidence intervals. Now I'm building a decision function that evaluates the four routing checks in sequence—if any fails, it returns a specific verdict like VOID or NO-CALIBRATION, otherwise it classifies the routing as either naive or correct based on the median effect size threshold. I'm also setting up the experimental worlds to test against: naive routing, correct routing, and a no-calibration scenario, with an optional placebo-violation world to explore edge cases.

I'm defining a backend class that manages the planted model with character-level tokenization and a mass computation that applies layer-specific weight bumps to simulate the routing behavior, using causal masking so attention only operates on positions up to the current cell.

Now I'm working through the jitter magnitude—with a base weight of 1.0 spread across roughly 250 token positions, the baseline mass is around 0.004, and adding a bump of 5.0 at the target position pushes it to about 0.02, which should create a clear enough separation from the placebo floor to produce a strong effect size.

For the statistical test, I'm using a sign-flip permutation approach: with 9 items all showing positive differences under the null, only 1 out of 512 equally likely sign patterns would be as extreme or more so, giving p ≈ 0.002—well below the 0.05 threshold. The correlation should be near 1 since the bumped condition mirrors the planted condition, and by seeding the jitter per text with a hash, I ensure different triples get different noise patterns so the bootstrap confidence interval won't collapse.

Now I'm setting up the validation logic to compute token positions using character offsets from the tokenizer, then defining four different worlds to test: a naive world where A and P both bump the effect while B bumps the capacity (creating spurious selection correlation), a correct world where A and B bump capacity while P bumps the effect (zeroing out both correlations), a no-calibration baseline, and a placebo world that mirrors the naive setup but adds an extra bump to the frequency term. A and P only (differential f) with big weight → placebo fires → VOID.

Wait placebo contrast: fA = A_f − B_f big → fires. But RC1 still passes; verdict tree: RC0 fail → VOID. 

Non-clean triples: bumps applied to all 18 triples for placebo pool consistency (placebo uses all). Fine — apply bumps to every triple, worlds defined by roles regardless of clean (for planted, apply same pattern; RC1/RC2 only read clean ones).

Now check: does planted respect "A has two y tokens" — irrelevant for planted.

For task 3, I'm using a 4B model and the smoke flag limits the battery to the first N triples, so with 2 triples that gives 6 variants to test. The battery list is flat across A, B, P per pair, so I take the first 6 entries and mark them as smoke in the metadata. I need to handle the import from prefill_cone carefully since it does a sys.path insert at module level, which might trigger linting issues around import ordering.

I'll also make sure to handle numpy boolean types properly when dumping to JSON by casting them explicitly, and I'll grab n_layers directly from the model structure. Before writing the file, I need to verify the ruff config handles the import pattern and then run validation.

For the cell statistics, I'm computing the full gate set on the answer cell to determine the verdict, while treating the term-final cell as advisory—its stats go into the secondary_cell field but don't influence the final decision. The battery validation checks that we have exactly 9 clean flips across the 18 triples and 54 variants, and build_battery handles the perturbation computation (which involves multiple replications and subterm reductions) in reasonable time. The output npz file uses keys formatted as term_id/cell pointing to the arrays.

For the answer column, the prompt ends with "\nNormal form:" so the last prefill token is the colon, and the next token is the first normal form token—I'll grab the attention row from that position. On the RC0 side, I need to check that the offsets signature (SHA of the offsets JSON) is consistent across the triple, since even identical-length prompts with different characters can tokenize differently. I'm also asserting that the e_tok position matches across the triple, and handling the edge case where the tokenizer might merge "e" with neighboring characters into a single token.

The token spanning the "e" position should be identical across variants since the character at that position is always 'e' and never gets renamed—only bound occurrences inside parentheses get renamed. Even if earlier differing characters shift token boundaries, the offsets signature check will catch that and drop the triple.

Now I'm setting up the test harness, aiming for around 450 lines. The verdict categories are locked in: NO-CALIBRATION, NAIVE-ROUTING, UNDIFFERENTIATED, CORRECT-ROUTING, and VOID. For the metadata, I'm documenting the P-CONE-ROUTING probe with its pre-data configuration, noting the queue state and knowledge page freeze point, plus the advisory exclusion and pre-data instantiation details.

Writing the harness script... Ruff doesn't flag private imports by default unless explicitly configured, so that shouldn't be an issue. I'm defining a frozen dataclass for source tokens with fields for position, capacity, and binder information, then writing a helper function to extract atom spans from a specification that match a given name.

Now I'm working on a function that processes variable pairs from terms, checking that error and format spans appear exactly once, handling capacity spans with special logic for single vs. multiple occurrences, and collecting binder tokens from positions where the two terms differ. Then I'm setting up a backend protocol that initializes a Hugging Face model with tokenizer and model loading...

Initializing model configuration... Writing hook logic... Implementing the tokenizer to split text into character pairs, then switching from Python's built-in hash to SHA256 for deterministic seeding across runs. Building the mass function to generate base weights across layers with small random noise, then applying position-specific bumps that can be selectively applied to deeper layers. Setting the bump weight to 6.0 and checking the routing behavior across worlds: in the correct world, RC1 should pass since P and A get bumped while B doesn't, creating the pole separation needed; the correlation checks confirm this leads to correct routing. For the naive world, the bump pattern differs—A gets bumped on e, B on cap, P on e—which should produce different routing behavior.

Now I'm building a scoring function that takes a backend, specification, and calibration variant, then extracts token positions for the relevant spans and computes mass distributions across layers to evaluate how the model represents different elements. Now I'm checking the selection correlation between B and P across clean records where selections are present, requiring the correlation to be positive for corroboration. If selections are missing for most records, I'll treat the corroboration check as automatically satisfied rather than failing. For the placebo analysis, I'm deciding whether to run it across all aligned triples or just the answer cell, and I need to clarify what RC0 checks—whether it's simply that there are no errors in the alignment.

For RC2, I'm computing the effect size ratio using the difference between P and B error rates as the denominator, calculating the median across clean triples and building a bootstrap confidence interval to see if it excludes 0.5. RC3 does the same for selection differences, but expects a negative denominator since selections should decrease from B to P, and I'm checking whether the sign of the effect size agrees with the sign of the selection effect to validate corroboration—though if there are no selections to analyze, I'm uncertain whether to mark this as undifferentiated or allow it to pass.

I'm treating unavailable selection data as a disagreement, which would force an undifferentiated verdict, though I suspect all nine samples will have enough data. RC4 computes per-layer median effect sizes for each layer separately and identifies which layer shows the strongest separation. I'll also run the same RC checks on the final term values as an advisory output, and store the per-layer mass data at source positions for each record.

Now I'm building a grouping function that reconstructs triples from records by pair ID, filtering out any with errors or incomplete variant sets, and checking that the signature offsets and token positions match across all three variants before including them in the output.

I'm also setting up statistical helpers for permutation tests and bootstrap analysis, then verifying the hash function for offsets signatures matches the existing implementation using SHA256 on JSON-serialized offset tuples.

For the main execution flow, I'm parsing arguments, optionally validating and returning early, then building the battery and organizing triples according to the battery's grouping order.

Now I'm extracting unique pairs from the battery, running a smoke test on the first two, and computing variable shadowing from the A specification's term. I'll initialize the HF backend, run a determinism check on the first variant prompt, then loop through each spec triple to score variants and compute gates based on the results. Finally, I'm outputting everything to JSON and NPZ files including results, gates configuration, battery metadata, and mass data.

For the NPZ file, I'm collecting mass grids keyed by spec ID and cell during the loop, and I need to verify that the final term ends before the normal form marker. I should also check the pre-normalization attention row sum deviation to ensure per-layer mass sums to 1 after normalization. Before writing the file, I'll make sure the code follows the line length requirements and properly convert the attention tensors to numpy arrays by indexing into the cells list.

Memory-wise, converting a 40×40×130×130 attention matrix to float32 is about 2.7MB per layer, which is manageable. I'll enable output_attentions with eager execution and use bfloat16 as the dtype, then write the file and validate it with ruff.

### Thinking

I've completed the first task with the full frozen spec and plumbing in place, reusing key components like `build_battery`/`build_variants` and the GQA-aware value-weighted read-mass pattern with per-kv-head v-norms. Moving on to the next task.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -A 20 \"\\[tool.ruff\" /Users/mwhitford/src/verbum/pyproject.toml"
}
```

**Summary:** $ grep -n -A 20 "\[tool.ruff" /Users/...

**Output:**
```
Exit code: 0
Stdout:
82:[tool.ruff]
83-line-length = 88
84-target-version = "py312"
85-src = ["src", "tests"]
86-
87:[tool.ruff.lint]
88-select = [
89-    "E",    # pycodestyle errors
90-    "W",    # pycodestyle warnings
91-    "F",    # pyflakes
92-    "I",    # isort
93-    "B",    # flake8-bugbear
94-    "UP",   # pyupgrade
95-    "RUF",  # ruff-specific
96-]
97-
98:[tool.ruff.lint.per-file-ignores]
99-"tests/*" = ["B011", "RUF001", "RUF002", "RUF003"]  # asserts + surface symbols in data
100-# Surface logical-form / reward modules: λ ∀ ∃ ι → ∧ ∨ ¬ Φ γ ⊗ ∈ Σ ARE the domain
101-# alphabet (CCG / λ-calculus / reward-shaping notation), not typos.
102-"src/verbum/lambda_surface.py" = ["RUF001", "RUF002", "RUF003"]
103-"src/verbum/reward.py" = ["RUF001", "RUF002", "RUF003"]
104-"src/verbum/compile_prompt.py" = ["RUF001", "RUF002", "RUF003"]
105-"scripts/experiments/audit_compile_corpus.py" = ["RUF001", "RUF002", "RUF003"]
106-"scripts/experiments/rlvr_coldstart_density.py" = ["RUF001", "RUF002", "RUF003"]
107-"scripts/experiments/rlvr_grpo_train.py" = ["RUF001", "RUF002", "RUF003"]
108-"scripts/experiments/proof_consensus.py" = ["RUF001", "RUF002", "RUF003"]
109-"scripts/experiments/ffn_program_decode.py" = ["RUF001", "RUF002", "RUF003"]
110-"scripts/experiments/gen_firing_probes.py" = ["RUF001", "RUF002", "RUF003"]
111-"scripts/experiments/gen_reading_probes.py" = ["RUF001", "RUF002", "RUF003"]
112-"scripts/experiments/ffn_reading_preference.py" = ["RUF001", "RUF002", "RUF003"]
113-"scripts/experiments/program_edge_knockout.py" = ["RUF001", "RUF002", "RUF003"]
114-"scripts/experiments/gen_scope_probes.py" = ["RUF001", "RUF002", "RUF003"]
115-"scripts/experiments/ffn_scope_forcing.py" = ["RUF001", "RUF002", "RUF003"]
116-"scripts/micro/ternary_st.py" = ["RUF001", "RUF002", "RUF003"]  # α Δ γ → · : ternary/register alphabet
117-"scripts/explore/att_mediation.py" = ["RUF001", "RUF002", "RUF003"]  # γ − × Δ Σ : DLA / attention decomposition notation
118-"scripts/explore/sign_commitment.py" = ["RUF001", "RUF002", "RUF003"]  # τ γ × − Δ ∈ : ternary/register alphabet
```

### Thinking

I'm noticing that prefill_cone.py uses Greek letters like λ and ρ in its docstrings, but it wasn't flagged by Ruff's RUF001/2/3 rules about ambiguous Unicode characters. RUF002 specifically catches characters that could be confused with ASCII equivalents, and while ρ might be mistaken for 'p', λ apparently isn't on the default ambiguous character list, which explains why the file passed the linter despite containing these symbols.

To be safe, I'll stick with ASCII-friendly variable names like "rho_e" instead of using the Greek letter directly, and I can add per-file ignore directives if needed. Now I'm ready to write the harness code.

## Assistant

Ruff config noted (88 cols, isort, RUF unicode rules — I'll keep the source ASCII-safe). Writing the harness:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/cone_routing.py",
  "content": "#!/usr/bin/env python3\n\"\"\"P-CONE-ROUTING - within-prompt read-mass routing probe (frozen s335, pre-data).\n\nSuccessor to P-PREFILL-CONE (VOID: magnitude/transport read aimed at a\nvalue/routing claim). This probe is register-matched: ROUTING. At the cell that\nemits the answer, does the machine READ FROM the argument the naive algorithm\nselects (`e`) or the one capture-avoiding substitution selects (the captured\nvariable, `y` in the exemplar)?\n\nWithin-prompt: both candidate answers sit in the SAME prompt, same forward\npass - the s335 surface-repetition confound never forms. One forward per\nvariant, no perturbation loop (54 forwards).\n\nSubstrate: the s335 matched triples (`build_variants` via `build_battery`,\n18 triples / 54 variants, 9 kernel-certified clean flips), identical layout\none character apart, so `e` sits at the same token in A/B/P by construction.\n\n  A  capture live    - correct NF discards `e`, naive NF is built from it\n  B  binders renamed - capture-free, NF head = cap var  => ground truth: not-e\n  P  head var swapped- capture-free, NF head = `e`      => ground truth: e\n\nReadout: value-weighted attention (s206 scar: never bare QK) from the answer\ncolumn (primary cell) and the term-final interior cell (secondary, advisory)\nonto candidate source positions. GQA-aware per-kv-head v-norm expansion,\nhead-mean, per-layer normalized. Primary scalar = LAYER-MEAN mass (pre-data\ninstantiation; per-layer stored for the RC4 depth advisory).\n\nFrozen statistics (knowledge page section P-CONE-ROUTING):\n\n  primary   rho_e   = (mass_A(e) - mass_B(e)) / (mass_P(e) - mass_B(e))\n  secondary rho_Sel = same shape on Sel = mass(cap) - mass(e), within-prompt.\n            Named bound: A carries the cap token TWICE (binder + argument);\n            mass is read at the ARGUMENT position, binder mass is diagnostic.\n\nGate tree (frozen): RC0 sanity -> RC1 CALIBRATION make-or-break read FIRST\n(mass_P(e) > mass_B(e) paired p<0.05 AND Cliff's delta >= 0.2, corroborated by\nSel_B > Sel_P) -> RC2 primary (bootstrap CI on median rho_e must exclude 0.5)\n-> RC3 secondary sign agreement -> RC4 depth advisory. Nulls: placebo `f`\n(must not discriminate), shuffled-variant-label (== the sign-flip permutation),\ndistance control (B/P are geometry-identical with opposite answers - the pole\ncontrast IS the distance control).\n\nVerdicts: VOID / NO-CALIBRATION / NAIVE-ROUTING / CORRECT-ROUTING /\nUNDIFFERENTIATED. The 3 advisory read-mass records from\nresults/p_prefill_cone_s335/run_14b (cap_000) are DISCLOSED and excluded -\nthis is a fresh run directory; nothing is read from that run.\n\nStanding bound: attention mass is correlational (s206) - a positive licenses\n\"reads from\", not \"uses\".\n\n`--validate` drives planted NAIVE / CORRECT / NO-CALIBRATION / PLACEBO worlds\nthrough the REAL scoring and gate path (s331: planted plumbing must be probe\nplumbing). No model is loaded.\n\nLicense: MIT.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport sys\nfrom dataclasses import dataclass\nfrom datetime import UTC, datetime\nfrom pathlib import Path\nfrom typing import Any\n\nimport numpy as np\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[2] / \"src\"))\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\nfrom prefill_cone import (  # noqa: E402\n    TermSpec,\n    _shadow_binders,\n    battery_hash,\n    build_battery,\n    build_prompt,\n    git_sha,\n)\nfrom verbum.cone import span_token_range  # noqa: E402\nfrom verbum.lambda_ast import parse  # noqa: E402\n\n# frozen constants\nN_PERM = 10_000\nN_BOOT = 10_000\nALPHA = 0.05\nRC1_MIN_CLIFF = 0.2\n# pre-data instantiations (declared in meta.json):\nPLACEBO_ABS_FLOOR = 0.005  # abs mass floor so a dead calibration can't fake VOID\nPLACEBO_REL = 0.5  # placebo fires only if it carries >= 50% of the pole contrast\nDET_TOL = 1e-4  # deterministic-repeat max abs mass difference\nMIN_ALIGNED_CLEAN = 6  # RC0: minimum aligned clean triples\nROWSUM_TOL = 2e-2  # attention row must sum to ~1 (bf16 tolerance)\nCELLS = (\"answer\", \"term_final\")\n\n\n# -- position extraction (shared by real and planted paths) ------------------\n@dataclass(frozen=True, slots=True)\nclass TripleCtx:\n    \"\"\"Per-triple constants derived from the kernel-certified battery.\"\"\"\n\n    pair_id: str\n    cap_var: str\n    diff_chars: tuple[int, ...]  # char idxs where A and B render differently\n\n\ndef triple_ctx(a_spec: TermSpec, b_spec: TermSpec) -> TripleCtx:\n    shadows = _shadow_binders(parse(a_spec.term))\n    diffs = tuple(\n        i for i, (ca, cb) in enumerate(zip(a_spec.term, b_spec.term, strict=True))\n        if ca != cb and ca == shadows[0]\n    )\n    return TripleCtx(a_spec.pair_id, shadows[0], diffs)\n\n\ndef free_atom_spans(spec: TermSpec, name: str) -> list[tuple[int, int]]:\n    return [\n        (s.start, s.end)\n        for s in spec.spans\n        if s.kind == \"atom\" and s.free_leaf and spec.term[s.start : s.end] == name\n    ]\n\n\ndef source_toks(\n    spec: TermSpec, ctx: TripleCtx, offsets: list[tuple[int, int]], base: int\n) -> dict[str, Any] | None:\n    \"\"\"Token indices of every read target; None on any extraction failure.\"\"\"\n\n    def one(spans: list[tuple[int, int]]) -> int | None:\n        if len(spans) != 1:\n            return None\n        rng = span_token_range(spans[0][0], spans[0][1], offsets, base)\n        return None if rng is None else rng[1]\n\n    e_tok = one(free_atom_spans(spec, \"e\"))\n    f_tok = one(free_atom_spans(spec, \"f\"))\n    if e_tok is None or f_tok is None:\n        return None\n    cap_spans = free_atom_spans(spec, ctx.cap_var)\n    cap_tok = one(cap_spans)  # None when 0 or >1 free occurrences (Sel skipped)\n    binder_toks: list[int] = []\n    for c in ctx.diff_chars:\n        rng = span_token_range(c, c + 1, offsets, base)\n        if rng is not None and rng[1] not in binder_toks:\n            binder_toks.append(rng[1])\n    root = spec.spans[spec.root]\n    term_rng = span_token_range(root.start, root.end, offsets, base)\n    if term_rng is None:\n        return None\n    return {\n        \"e\": e_tok,\n        \"cap\": cap_tok,\n        \"f\": f_tok,\n        \"binder\": binder_toks,\n        \"term_final\": term_rng[1],\n        \"cap_free_count\": len(cap_spans),\n    }\n\n\n# -- backends ----------------------------------------------------------------\nclass HFBackend:\n    \"\"\"HF host: one forward per variant; value-weighted GQA-aware read-mass.\"\"\"\n\n    def __init__(self, model_id: str, device: str, dtype: str):\n        import torch\n        from transformers import AutoModelForCausalLM, AutoTokenizer\n\n        self.torch = torch\n        self.tok = AutoTokenizer.from_pretrained(model_id)\n        self.model = (\n            AutoModelForCausalLM.from_pretrained(\n                model_id, dtype=getattr(torch, dtype), attn_implementation=\"eager\"\n            )\n            .to(device)\n            .eval()\n        )\n        self.device = device\n        cfg = self.model.config\n        self.n_heads = int(cfg.num_attention_heads)\n        self.n_kv = int(getattr(cfg, \"num_key_value_heads\", self.n_heads))\n        self.gqa_ok = self.n_heads % self.n_kv == 0\n        self.L = len(self.model.model.layers)\n\n    def tokenize(self, text: str) -> list[tuple[int, int]]:\n        enc = self.tok(text, return_offsets_mapping=True, add_special_tokens=True)\n        return [tuple(o) for o in enc[\"offset_mapping\"]]\n\n    def mass(\n        self, text: str, cells: list[int]\n    ) -> tuple[np.ndarray, float]:\n        \"\"\"Read-mass (n_cells, L, T) + max |rowsum - 1| before value weighting.\"\"\"\n        torch = self.torch\n        inputs = self.tok(text, return_tensors=\"pt\").to(self.device)\n        vns: dict[int, np.ndarray] = {}\n        handles = []\n\n        def mk(i: int):\n            def hook(_m, _inp, out):\n                v = out[0] if isinstance(out, tuple) else out\n                hd = v.shape[-1] // self.n_kv\n                vns[i] = (\n                    v[0].float().view(-1, self.n_kv, hd).norm(dim=-1).cpu().numpy()\n                )  # (T, n_kv)\n\n            return hook\n\n        try:\n            for i, layer in enumerate(self.model.model.layers):\n                handles.append(layer.self_attn.v_proj.register_forward_hook(mk(i)))\n            with torch.no_grad():\n                out = self.model(**inputs, output_attentions=True)\n        finally:\n            for h in handles:\n                h.remove()\n        T = int(inputs[\"input_ids\"].shape[1])\n        group = self.n_heads // self.n_kv\n        m = np.zeros((len(cells), self.L, T), dtype=np.float64)\n        dev = 0.0\n        for i, att in enumerate(out.attentions):\n            w_all = att[0].float().cpu().numpy()  # (H, T, T)\n            w = w_all[:, cells, :]  # (H, C, T)\n            dev = max(dev, float(np.abs(w.sum(axis=-1) - 1.0).max()))\n            vn = vns[i]  # (T, n_kv)\n            vn_exp = np.repeat(vn.T, group, axis=0)  # (H, T), kv-head blocks\n            weighted = (w * vn_exp[:, None, :]).mean(axis=0)  # (C, T)\n            s = weighted.sum(axis=-1, keepdims=True)\n            m[:, i, :] = np.where(s > 0, weighted / s, weighted)\n        return m, dev\n\n\nclass PlantedBackend:\n    \"\"\"Char-tokenized world with planted read-mass (validate only).\n\n    Bumps are keyed by prompt TEXT -> {token: weight}; the scoring path\n    extracts positions and reads mass through the identical code (s331).\n    Deterministic per text (sha256 seed) so the repeat check is exercised.\n    \"\"\"\n\n    L = 8\n    gqa_ok = True\n    n_heads = 4\n    n_kv = 2\n\n    def __init__(self) -> None:\n        self.bump_by_text: dict[str, dict[int, float]] = {}\n\n    def tokenize(self, text: str) -> list[tuple[int, int]]:\n        return [(i, i + 1) for i in range(len(text))]\n\n    def mass(self, text: str, cells: list[int]) -> tuple[np.ndarray, float]:\n        T = len(text)\n        seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)\n        rng = np.random.default_rng(seed)\n        base = 1.0 + 0.05 * rng.standard_normal((self.L, T))\n        base = np.clip(base, 0.01, None)\n        for tok, wgt in self.bump_by_text.get(text, {}).items():\n            base[2:, tok] += wgt  # layers >= 2 only (exercises RC4 storage)\n        m = np.zeros((len(cells), self.L, T), dtype=np.float64)\n        for c, cell in enumerate(cells):\n            w = base.copy()\n            w[:, cell + 1 :] = 0.0  # causal\n            m[c] = w / w.sum(axis=-1, keepdims=True)\n        return m, 0.0\n\n\n# -- scoring (identical path for real and planted) ---------------------------\ndef score_variant(backend, spec: TermSpec, ctx: TripleCtx) -> tuple[dict, dict]:\n    \"\"\"One forward -> one results.jsonl record (+ full mass grids for npz).\"\"\"\n    prompt, base = build_prompt(spec.term)\n    offsets = backend.tokenize(prompt)\n    rec: dict[str, Any] = {\n        \"term_id\": spec.id,\n        \"pair_id\": spec.pair_id,\n        \"variant\": spec.variant,\n        \"clean_flip\": bool(spec.clean_flip),\n        \"term\": spec.term,\n        \"correct_nf\": spec.correct_nf,\n        \"naive_nf\": spec.naive_nf,\n        \"cap_var\": ctx.cap_var,\n        \"offsets_sig\": hashlib.sha256(json.dumps(offsets).encode()).hexdigest()[:12],\n        \"n_tokens\": len(offsets),\n        \"error\": None,\n    }\n    toks = source_toks(spec, ctx, offsets, base)\n    if toks is None:\n        rec[\"error\"] = \"position_extraction_failed\"\n        return rec, {}\n    ans = len(offsets) - 1\n    cells = {\"answer\": ans, \"term_final\": toks[\"term_final\"]}\n    rec[\"toks\"] = {**toks, \"answer\": ans}\n    m, dev = backend.mass(prompt, [cells[c] for c in CELLS])\n    rec[\"rowsum_dev\"] = float(dev)\n    rec[\"n_layers\"] = int(m.shape[1])\n    grids = {}\n    for ci, cname in enumerate(CELLS):\n        grid = m[ci]  # (L, T)\n        grids[f\"{spec.id}:{cname}\"] = grid.astype(np.float32)\n        cell_rec: dict[str, Any] = {\n            \"mass_e\": float(grid[:, toks[\"e\"]].mean()),\n            \"mass_f\": float(grid[:, toks[\"f\"]].mean()),\n            \"mass_binder\": float(\n                sum(grid[:, t].mean() for t in toks[\"binder\"])\n            ),\n            \"layers_e\": [float(x) for x in grid[:, toks[\"e\"]]],\n            \"layers_f\": [float(x) for x in grid[:, toks[\"f\"]]],\n        }\n        if toks[\"cap\"] is not None:\n            cell_rec[\"mass_cap\"] = float(grid[:, toks[\"cap\"]].mean())\n            cell_rec[\"sel\"] = cell_rec[\"mass_cap\"] - cell_rec[\"mass_e\"]\n            cell_rec[\"layers_cap\"] = [float(x) for x in grid[:, toks[\"cap\"]]]\n        else:\n            cell_rec[\"mass_cap\"] = None\n            cell_rec[\"sel\"] = None\n        rec[cname] = cell_rec\n    return rec, grids\n\n\n# -- statistics --------------------------------------------------------------\ndef perm_p(diffs: np.ndarray, rng, one_sided: bool) -> float:\n    \"\"\"Sign-flip permutation p == the shuffled-variant-label null (paired).\"\"\"\n    if diffs.size == 0:\n        return 1.0\n    obs = float(diffs.mean())\n    signs = rng.choice([-1.0, 1.0], size=(N_PERM, diffs.size))\n    null = (signs * diffs[None, :]).mean(axis=1)\n    if one_sided:\n        return float((np.sum(null >= obs) + 1) / (N_PERM + 1))\n    return float((np.sum(np.abs(null) >= abs(obs)) + 1) / (N_PERM + 1))\n\n\ndef cliffs_delta(a: np.ndarray) -> float:\n    \"\"\"Cliff's delta of paired diffs vs zero.\"\"\"\n    if a.size == 0:\n        return 0.0\n    return float(((a > 0).sum() - (a < 0).sum()) / a.size)\n\n\ndef boot_ci_median(vals: np.ndarray, rng) -> tuple[float, float]:\n    if vals.size == 0:\n        return (float(\"nan\"), float(\"nan\"))\n    idx = rng.integers(0, vals.size, size=(N_BOOT, vals.size))\n    meds = np.median(vals[idx], axis=1)\n    return (float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5)))\n\n\ndef group_triples(recs: list[dict]) -> tuple[list[dict[str, dict]], int]:\n    by: dict[str, dict[str, dict]] = {}\n    for r in recs:\n        if r.get(\"error\") is None:\n            by.setdefault(r[\"pair_id\"], {})[r[\"variant\"]] = r\n    out, mis = [], 0\n    for pid in sorted(by):\n        vs = by[pid]\n        if set(vs) != {\"A\", \"B\", \"P\"}:\n            mis += 1\n            continue\n        if len({vs[t][\"offsets_sig\"] for t in \"ABP\"}) != 1:\n            mis += 1\n            continue\n        if len({vs[t][\"toks\"][\"e\"] for t in \"ABP\"}) != 1:\n            mis += 1\n            continue\n        out.append(vs)\n    return out, mis\n\n\ndef cell_stats(\n    triples: list[dict[str, dict]], cell: str, rng\n) -> dict[str, Any]:\n    \"\"\"RC1/RC2/RC3(/RC4 for answer) on one readout cell.\"\"\"\n    clean = [t for t in triples if t[\"A\"][\"clean_flip\"]]\n\n    def arr(tag: str, key: str, pool: list) -> np.ndarray:\n        return np.array([t[tag][cell][key] for t in pool], dtype=np.float64)\n\n    # RC1 calibration (make-or-break, read FIRST)\n    d_pole = arr(\"P\", \"mass_e\", clean) - arr(\"B\", \"mass_e\", clean)\n    p1 = perm_p(d_pole, rng, one_sided=True)\n    cd = cliffs_delta(d_pole)\n    sel_pairs = [\n        (t[\"B\"][cell][\"sel\"], t[\"P\"][cell][\"sel\"])\n        for t in clean\n        if t[\"B\"][cell][\"sel\"] is not None and t[\"P\"][cell][\"sel\"] is not None\n    ]\n    sel_corr = (\n        float(np.mean([b - p for b, p in sel_pairs])) if sel_pairs else None\n    )\n    corr_ok = sel_corr is None or sel_corr > 0\n    rc1 = {\n        \"n_triples\": int(d_pole.size),\n        \"mean_pole_sep\": float(d_pole.mean()) if d_pole.size else 0.0,\n        \"median_pole_sep\": float(np.median(d_pole)) if d_pole.size else 0.0,\n        \"cliffs_delta\": cd,\n        \"p_one_sided\": p1,\n        \"sel_corroboration_mean_B_minus_P\": sel_corr,\n        \"sel_corroboration_ok\": bool(corr_ok),\n        \"pass\": bool(\n            d_pole.size\n            and d_pole.mean() > 0\n            and cd >= RC1_MIN_CLIFF\n            and p1 < ALPHA\n            and corr_ok\n        ),\n    }\n\n    # placebo `f` (all aligned triples; must NOT discriminate)\n    fA = arr(\"A\", \"mass_f\", triples) - arr(\"B\", \"mass_f\", triples)\n    fP = arr(\"P\", \"mass_f\", triples) - arr(\"B\", \"mass_f\", triples)\n    thresh = max(PLACEBO_REL * abs(rc1[\"mean_pole_sep\"]), PLACEBO_ABS_FLOOR)\n    placebo = {}\n    fired = False\n    for name, d in ((\"A_minus_B\", fA), (\"P_minus_B\", fP)):\n        p = perm_p(d, rng, one_sided=False)\n        mean = float(d.mean()) if d.size else 0.0\n        hit = bool(d.size and p < ALPHA and abs(mean) >= thresh)\n        placebo[name] = {\"mean\": mean, \"p\": p, \"fired\": hit}\n        fired = fired or hit\n    placebo[\"threshold\"] = float(thresh)\n    placebo[\"fired\"] = bool(fired)\n\n    # RC2 primary rho_e (clean triples; per-triple pole denominator must be > 0)\n    rhos, excluded = [], 0\n    for t in clean:\n        b, p_, a = (t[tag][cell][\"mass_e\"] for tag in (\"B\", \"P\", \"A\"))\n        den = p_ - b\n        if den <= 0:\n            excluded += 1\n            continue\n        rhos.append((a - b) / den)\n    rho_e = np.array(rhos, dtype=np.float64)\n    lo, hi = boot_ci_median(rho_e, rng)\n    med_e = float(np.median(rho_e)) if rho_e.size else float(\"nan\")\n    rc2 = {\n        \"n_used\": int(rho_e.size),\n        \"n_excluded_bad_denominator\": int(excluded),\n        \"rho_e_values\": [float(x) for x in rho_e],\n        \"median_rho_e\": med_e,\n        \"ci95_low\": lo,\n        \"ci95_high\": hi,\n        \"ci_excludes_half\": bool(rho_e.size and (lo > 0.5 or hi < 0.5)),\n    }\n\n    # RC3 secondary rho_Sel (denominator Sel_P - Sel_B must be < 0: mass moves\n    # from cap toward e between the poles)\n    rhos_s, excluded_s = [], 0\n    for t in clean:\n        sb, sp, sa = (t[tag][cell][\"sel\"] for tag in (\"B\", \"P\", \"A\"))\n        if sb is None or sp is None or sa is None:\n            excluded_s += 1\n            continue\n        den = sp - sb\n        if den >= 0:\n            excluded_s += 1\n            continue\n        rhos_s.append((sa - sb) / den)\n    rho_s = np.array(rhos_s, dtype=np.float64)\n    med_s = float(np.median(rho_s)) if rho_s.size else float(\"nan\")\n    agrees = bool(\n        rho_e.size and rho_s.size and (med_e - 0.5) * (med_s - 0.5) > 0\n    )\n    rc3 = {\n        \"n_used\": int(rho_s.size),\n        \"n_excluded\": int(excluded_s),\n        \"median_rho_sel\": med_s,\n        \"agrees_with_rho_e\": agrees,\n    }\n\n    # RC4 depth advisory (per-layer median rho_e)\n    rc4: dict[str, Any] = {}\n    if clean:\n        n_layers = len(clean[0][\"A\"][cell][\"layers_e\"])\n        per_layer = []\n        for layer in range(n_layers):\n            vals = []\n            for t in clean:\n                b, p_, a = (\n                    t[tag][cell][\"layers_e\"][layer] for tag in (\"B\", \"P\", \"A\")\n                )\n                if p_ - b > 0:\n                    vals.append((a - b) / (p_ - b))\n            per_layer.append(\n                float(np.median(vals)) if vals else float(\"nan\")\n            )\n        seps = [\n            float(\n                np.median(\n                    [\n                        t[\"P\"][cell][\"layers_e\"][layer]\n                        - t[\"B\"][cell][\"layers_e\"][layer]\n                        for t in clean\n                    ]\n                )\n            )\n            for layer in range(n_layers)\n        ]\n        rc4 = {\n            \"per_layer_median_rho_e\": per_layer,\n            \"per_layer_median_pole_sep\": seps,\n            \"best_sep_layer\": int(np.argmax(seps)),\n        }\n\n    # diagnostics: binder mass (the named A-two-tokens bound) + raw masses\n    diag = {\n        \"median_mass_binder_A\": (\n            float(np.median(arr(\"A\", \"mass_binder\", triples)))\n            if triples\n            else None\n        ),\n        \"median_mass_e\": {\n            tag: float(np.median(arr(tag, \"mass_e\", clean))) if clean else None\n            for tag in (\"A\", \"B\", \"P\")\n        },\n        \"median_mass_cap\": {\n            tag: (\n                float(\n                    np.median(\n                        [\n                            t[tag][cell][\"mass_cap\"]\n                            for t in clean\n                            if t[tag][cell][\"mass_cap\"] is not None\n                        ]\n                    )\n                )\n                if clean\n                else None\n            )\n            for tag in (\"A\", \"B\", \"P\")\n        },\n    }\n    return {\n        \"RC1\": rc1,\n        \"placebo\": placebo,\n        \"RC2\": rc2,\n        \"RC3\": rc3,\n        \"RC4\": rc4,\n        \"diagnostics\": diag,\n    }\n\n\ndef decide(rc0: dict, cell: dict) -> str:\n    \"\"\"The frozen verdict tree.\"\"\"\n    if not rc0[\"pass\"]:\n        return \"VOID\"\n    if not cell[\"RC1\"][\"pass\"]:\n        return \"NO-CALIBRATION\"\n    if not cell[\"RC2\"][\"ci_excludes_half\"]:\n        return \"UNDIFFERENTIATED\"\n    if not cell[\"RC3\"][\"agrees_with_rho_e\"]:\n        return \"UNDIFFERENTIATED\"\n    return (\n        \"NAIVE-ROUTING\"\n        if cell[\"RC2\"][\"median_rho_e\"] > 0.5\n        else \"CORRECT-ROUTING\"\n    )\n\n\ndef compute_gates(\n    recs: list[dict], rng, *, det_dev: float | None, gqa_ok: bool\n) -> dict:\n    triples, mis = group_triples(recs)\n    clean_n = sum(1 for t in triples if t[\"A\"][\"clean_flip\"])\n    n_err = sum(1 for r in recs if r.get(\"error\"))\n    rowsum = max((r.get(\"rowsum_dev\", 0.0) for r in recs), default=0.0)\n    answer = cell_stats(triples, \"answer\", rng)\n    term_final = cell_stats(triples, \"term_final\", rng)\n    rc0 = {\n        \"n_records\": len(recs),\n        \"n_errors\": int(n_err),\n        \"n_triples_aligned\": len(triples),\n        \"n_triples_misaligned\": int(mis),\n        \"n_clean_aligned\": int(clean_n),\n        \"max_rowsum_dev\": float(rowsum),\n        \"rowsum_ok\": bool(rowsum < ROWSUM_TOL),\n        \"det_repeat_dev\": det_dev,\n        \"det_ok\": bool(det_dev is None or det_dev < DET_TOL),\n        \"gqa_ok\": bool(gqa_ok),\n        \"placebo_fired\": bool(answer[\"placebo\"][\"fired\"]),\n        \"s335_advisory_records\": \"excluded (fresh run; nothing read)\",\n    }\n    rc0[\"pass\"] = bool(\n        n_err == 0\n        and clean_n >= MIN_ALIGNED_CLEAN\n        and rc0[\"rowsum_ok\"]\n        and rc0[\"det_ok\"]\n        and rc0[\"gqa_ok\"]\n        and not rc0[\"placebo_fired\"]\n    )\n    verdict = decide(rc0, answer)\n    return {\n        \"RC0\": rc0,\n        \"answer\": answer,\n        \"term_final_advisory\": term_final,\n        \"verdict\": verdict,\n        \"verdict_cell\": \"answer\",\n    }\n\n\n# -- battery helpers ---------------------------------------------------------\ndef battery_triples(\n    smoke: bool = False,\n) -> list[tuple[TripleCtx, dict[str, TermSpec]]]:\n    battery = build_battery()\n    by: dict[str, dict[str, TermSpec]] = {}\n    order: list[str] = []\n    for s in battery:\n        if s.pair_id not in by:\n            order.append(s.pair_id)\n        by.setdefault(s.pair_id, {})[s.variant] = s\n    if smoke:\n        order = order[:2]\n    return [(triple_ctx(by[p][\"A\"], by[p][\"B\"]), by[p]) for p in order]\n\n\n# -- planted-world validation ------------------------------------------------\ndef _plant(be: PlantedBackend, specs: dict[str, TermSpec], world: str) -> None:\n    bump = 6.0\n    for tag, spec in specs.items():\n        prompt, base = build_prompt(spec.term)\n        e_spans = free_atom_spans(spec, \"e\")\n        f_spans = free_atom_spans(spec, \"f\")\n        shadows = _shadow_binders(parse(specs[\"A\"].term))\n        cap_spans = free_atom_spans(spec, shadows[0])\n        if len(e_spans) != 1 or len(f_spans) != 1 or len(cap_spans) != 1:\n            continue\n        e_tok = base + e_spans[0][1] - 1\n        f_tok = base + f_spans[0][1] - 1\n        cap_tok = base + cap_spans[0][1] - 1\n        bumps: dict[int, float] = {}\n        if world == \"nocal\":\n            pass\n        elif world == \"naive\":\n            bumps[e_tok if tag in (\"A\", \"P\") else cap_tok] = bump\n        elif world == \"correct\":\n            bumps[e_tok if tag == \"P\" else cap_tok] = bump\n        elif world == \"placebo\":\n            bumps[e_tok if tag in (\"A\", \"P\") else cap_tok] = bump\n            if tag in (\"A\", \"P\"):\n                bumps[f_tok] = bump  # differential placebo -> must go VOID\n        be.bump_by_text[prompt] = bumps\n\n\ndef validate() -> bool:\n    ok = True\n    triples = battery_triples()\n    n_clean = sum(1 for _c, vs in triples if vs[\"A\"].clean_flip)\n    print(\n        f\"[cr] battery: {len(triples)} triples / {3 * len(triples)} variants, \"\n        f\"{n_clean} clean flips\"\n    )\n    ok &= len(triples) == 18 and n_clean == 9\n    for ctx, vs in triples:\n        for spec in vs.values():\n            assert len(free_atom_spans(spec, \"e\")) == 1, spec.id\n            assert len(free_atom_spans(spec, \"f\")) == 1, spec.id\n        assert ctx.diff_chars, ctx.pair_id\n    print(\"[cr] e/f single free occurrence in all 54 variants ✓\")\n\n    worlds = (\n        (\"naive\", \"NAIVE-ROUTING\"),\n        (\"correct\", \"CORRECT-ROUTING\"),\n        (\"nocal\", \"NO-CALIBRATION\"),\n        (\"placebo\", \"VOID\"),\n    )\n    for world, want in worlds:\n        be = PlantedBackend()\n        for _ctx, vs in triples:\n            _plant(be, vs, world)\n        recs = []\n        for ctx, vs in triples:\n            for tag in (\"A\", \"B\", \"P\"):\n                rec, _grids = score_variant(be, vs[tag], ctx)\n                recs.append(rec)\n        # deterministic repeat through the real path\n        r1, _ = score_variant(be, triples[0][1][\"A\"], triples[0][0])\n        det = max(\n            abs(a - b)\n            for a, b in zip(\n                r1[\"answer\"][\"layers_e\"],\n                recs[0][\"answer\"][\"layers_e\"],\n                strict=True,\n            )\n        )\n        g = compute_gates(\n            recs, np.random.default_rng(0), det_dev=float(det), gqa_ok=True\n        )\n        a = g[\"answer\"]\n        print(\n            f\"[cr] world={world!r}: verdict={g['verdict']} | \"\n            f\"RC1 sep={a['RC1']['median_pole_sep']:.4f} \"\n            f\"d={a['RC1']['cliffs_delta']:.2f} p={a['RC1']['p_one_sided']:.4f} \"\n            f\"pass={a['RC1']['pass']} | \"\n            f\"RC2 rho_e={a['RC2']['median_rho_e']:.3f} \"\n            f\"CI=({a['RC2']['ci95_low']:.3f},{a['RC2']['ci95_high']:.3f}) | \"\n            f\"RC3 rho_sel={a['RC3']['median_rho_sel']:.3f} \"\n            f\"agree={a['RC3']['agrees_with_rho_e']} | \"\n            f\"placebo_fired={a['placebo']['fired']}\"\n        )\n        ok &= g[\"verdict\"] == want\n    print(f\"[cr] {'ALL PASS' if ok else 'FAIL'}\")\n    return bool(ok)\n\n\n# -- provenance --------------------------------------------------------------\ndef write_meta(out: Path, args, n_variants: int, bhash: str, gates: dict) -> None:\n    import platform\n\n    meta = {\n        \"run_id\": out.name,\n        \"probe\": \"P-CONE-ROUTING\",\n        \"frozen\": (\n            \"s335 pre-data (queue row + knowledge page \"\n            \"latent-reasoning-and-the-prefill-triangle.md freeze section); \"\n            \"3 advisory s335 read-mass records disclosed and excluded\"\n        ),\n        \"pre_data_instantiations\": {\n            \"primary_scalar\": \"layer-mean of per-layer-normalized read-mass\",\n            \"rc1_population\": \"kernel-certified clean-flip triples (n=9)\",\n            \"rc1_corroboration\": \"mean(Sel_B - Sel_P) > 0 required (direction)\",\n            \"placebo_rule\": (\n                f\"fires iff p<{ALPHA} and |mean| >= \"\n                f\"max({PLACEBO_REL}*|pole_sep|, {PLACEBO_ABS_FLOOR})\"\n            ),\n            \"det_tol\": DET_TOL,\n            \"min_aligned_clean\": MIN_ALIGNED_CLEAN,\n            \"rho_denominator_rule\": (\n                \"per-triple exclusion: rho_e needs P-B>0, rho_sel needs \"\n                \"SelP-SelB<0; counts reported\"\n            ),\n        },\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"model_id\": args.model_id,\n        \"device\": args.device,\n        \"dtype\": args.dtype,\n        \"seed\": args.seed,\n        \"smoke\": bool(args.smoke),\n        \"n_variants\": n_variants,\n        \"battery_hash\": bhash,\n        \"git_sha\": git_sha(),\n        \"python\": platform.python_version(),\n        \"platform\": platform.platform(),\n        \"gates\": gates,\n    }\n    try:\n        import torch\n        import transformers\n\n        meta[\"lib_versions\"] = {\n            \"torch\": torch.__version__,\n            \"transformers\": transformers.__version__,\n            \"numpy\": np.__version__,\n        }\n    except ImportError:\n        meta[\"lib_versions\"] = {\"numpy\": np.__version__}\n    (out / \"meta.json\").write_text(json.dumps(meta, indent=2, default=str))\n\n\ndef main() -> int:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--model-id\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--dtype\", default=\"bfloat16\")\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--out\", default=None)\n    ap.add_argument(\"--validate\", action=\"store_true\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.validate:\n        return 0 if validate() else 1\n\n    triples = battery_triples(smoke=args.smoke)\n    bhash = battery_hash(\n        [vs[t] for _c, vs in triples for t in (\"A\", \"B\", \"P\")]\n    )\n    n_variants = 3 * len(triples)\n    print(\n        f\"[cr] {len(triples)} triples / {n_variants} variants hash={bhash} \"\n        f\"model={args.model_id} dtype={args.dtype}\",\n        flush=True,\n    )\n    backend = HFBackend(args.model_id, args.device, args.dtype)\n    print(\n        f\"[cr] layers={backend.L} heads={backend.n_heads} kv={backend.n_kv} \"\n        f\"gqa_ok={backend.gqa_ok}\",\n        flush=True,\n    )\n\n    recs: list[dict] = []\n    all_grids: dict[str, np.ndarray] = {}\n    det_dev: float | None = None\n    i = 0\n    for ctx, vs in triples:\n        for tag in (\"A\", \"B\", \"P\"):\n            spec = vs[tag]\n            rec, grids = score_variant(backend, spec, ctx)\n            if i == 0:  # deterministic repeat on the very first variant\n                rec2, _ = score_variant(backend, spec, ctx)\n                if rec.get(\"error\") is None and rec2.get(\"error\") is None:\n                    det_dev = max(\n                        abs(a - b)\n                        for a, b in zip(\n                            rec[\"answer\"][\"layers_e\"],\n                            rec2[\"answer\"][\"layers_e\"],\n                            strict=True,\n                        )\n                    )\n            recs.append(rec)\n            all_grids.update(grids)\n            i += 1\n            print(\n                f\"[cr] {i}/{n_variants} {spec.id} err={rec['error']}\",\n                flush=True,\n            )\n\n    gates = compute_gates(\n        recs,\n        np.random.default_rng(args.seed + 7),\n        det_dev=det_dev,\n        gqa_ok=backend.gqa_ok,\n    )\n    print(json.dumps(gates, indent=2, default=str))\n    if args.out:\n        out = Path(args.out)\n        out.mkdir(parents=True, exist_ok=True)\n        with (out / \"results.jsonl\").open(\"w\") as fh:\n            for r in recs:\n                fh.write(json.dumps(r, default=str) + \"\\n\")\n        (out / \"gates.json\").write_text(json.dumps(gates, indent=2, default=str))\n        np.savez_compressed(out / \"mass.npz\", **all_grids)\n        write_meta(out, args, n_variants, bhash, gates)\n        print(f\"[cr] wrote {out}\")\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/cone_routing.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/cone_routing.py && uv run ruff format --check scripts/experiments/cone_routing.py 2>/dev/null; echo \"---\"; uv run python scripts/experiments/cone_routing.py --validate",
  "timeout": 300000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
I001 [*] Import block is un-sorted or un-formatted
  --> scripts/experiments/cone_routing.py:74:1
   |
72 |   sys.path.insert(0, str(Path(__file__).resolve().parent))
73 |
74 | / from prefill_cone import (  # noqa: E402
75 | |     TermSpec,
76 | |     _shadow_binders,
77 | |     battery_hash,
78 | |     build_battery,
79 | |     build_prompt,
80 | |     git_sha,
81 | | )
82 | | from verbum.cone import span_token_range  # noqa: E402
83 | | from verbum.lambda_ast import parse  # noqa: E402
   | |___________________________________^
84 |
85 |   # frozen constants
   |
help: Organize imports

RUF100 [*] Unused `noqa` directive (unused: `E402`)
  --> scripts/experiments/cone_routing.py:74:29
   |
72 | sys.path.insert(0, str(Path(__file__).resolve().parent))
73 |
74 | from prefill_cone import (  # noqa: E402
   |                             ^^^^^^^^^^^^
75 |     TermSpec,
76 |     _shadow_binders,
   |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (unused: `E402`)
  --> scripts/experiments/cone_routing.py:82:43
   |
80 |     git_sha,
81 | )
82 | from verbum.cone import span_token_range  # noqa: E402
   |                                           ^^^^^^^^^^^^
83 | from verbum.lambda_ast import parse  # noqa: E402
   |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (unused: `E402`)
  --> scripts/experiments/cone_routing.py:83:38
   |
81 | )
82 | from verbum.cone import span_token_range  # noqa: E402
83 | from verbum.lambda_ast import parse  # noqa: E402
   |                                      ^^^^^^^^^^^^
84 |
85 | # frozen constants
   |
help: Remove unused `noqa` directive

Found 4 errors.
[*] 4 fixable with the `--fix` option.
---
[cr] battery: 18 triples / 54 variants, 9 clean flips
[cr] e/f single free occurrence in all 54 variants ✓
[cr] world='naive': verdict=NAIVE-ROUTING | RC1 sep=0.0161 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.998 CI=(0.994,1.007) | RC3 rho_sel=0.999 agree=True | placebo_fired=False
[cr] world='correct': verdict=CORRECT-ROUTING | RC1 sep=0.0161 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.002 CI=(-0.004,0.009) | RC3 rho_sel=-0.000 agree=True | placebo_fired=False
[cr] world='nocal': verdict=NO-CALIBRATION | RC1 sep=0.0000 d=0.11 p=0.2528 pass=False | RC2 rho_e=0.752 CI=(-1.078,1.658) | RC3 rho_sel=0.489 agree=False | placebo_fired=False
[cr] world='placebo': verdict=VOID | RC1 sep=0.0157 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.998 CI=(0.994,1.007) | RC3 rho_sel=0.999 agree=True | placebo_fired=True
[cr] ALL PASS
```

### Thinking

All four planted worlds are back online. Now I need to fix the ruff import formatting issues—ruff wants the import block sorted and formatted properly, and I'll apply the --fix flag to handle the E402 errors automatically.

## Assistant

All 4 planted worlds recovered through the real path (NAIVE-ROUTING / CORRECT-ROUTING / NO-CALIBRATION / VOID-on-placebo). Fixing the ruff import nits:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/cone_routing.py && uv run ruff check scripts/experiments/cone_routing.py && echo RUFF-CLEAN",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 4 errors (4 fixed, 0 remaining).
All checks passed!
RUFF-CLEAN
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/cone_routing.py",
  "line_offset": 60,
  "limit": 30
}
```

**Summary:** Reading cone_routing.py (60-90)

**Output:**
```
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prefill_cone import (
    TermSpec,
    _shadow_binders,
    battery_hash,
    build_battery,
    build_prompt,
    git_sha,
)

from verbum.cone import span_token_range
from verbum.lambda_ast import parse

# frozen constants
N_PERM = 10_000
N_BOOT = 10_000
ALPHA = 0.05
RC1_MIN_CLIFF = 0.2

[CONTENT TRUNCATED] Showing lines 61 to 90 of 839 total lines. Use line_offset=90 parameter to read more content.
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/cone_routing.py"
}
```

**Summary:** Checking diagnostics: cone_routing.py

**Output:**
```
No diagnostics found
```

### Thinking

Ruff and diagnostics are clean, and validation passed. Since the fix only reordered imports, I'll run validation once more to confirm nothing broke, then move on to smoke testing on 4B.

Now I'm setting up the smoke test with 2 triples and 6 variants on Qwen3-4B, outputting to results/p_cone_routing_s336/smoke_4b. The model load will take a minute or two, and the full smoke test should complete in under 5 minutes, so I'll run it in the foreground with a 900-second timeout.

## Assistant

Ruff clean, no diagnostics, imports re-verified on disk. Quick re-validate after the fix, then straight into the 4B smoke:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/cone_routing.py --validate 2>&1 | tail -6",
  "timeout": 300000
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Exit code: 0
Stdout:
[cr] e/f single free occurrence in all 54 variants ✓
[cr] world='naive': verdict=NAIVE-ROUTING | RC1 sep=0.0161 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.998 CI=(0.994,1.007) | RC3 rho_sel=0.999 agree=True | placebo_fired=False
[cr] world='correct': verdict=CORRECT-ROUTING | RC1 sep=0.0161 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.002 CI=(-0.004,0.009) | RC3 rho_sel=-0.000 agree=True | placebo_fired=False
[cr] world='nocal': verdict=NO-CALIBRATION | RC1 sep=0.0000 d=0.11 p=0.2528 pass=False | RC2 rho_e=0.752 CI=(-1.078,1.658) | RC3 rho_sel=0.489 agree=False | placebo_fired=False
[cr] world='placebo': verdict=VOID | RC1 sep=0.0157 d=1.00 p=0.0024 pass=True | RC2 rho_e=0.998 CI=(0.994,1.007) | RC3 rho_sel=0.999 agree=True | placebo_fired=True
[cr] ALL PASS
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/cone_routing.py --model-id Qwen/Qwen3-4B --smoke --out results/p_cone_routing_s336/smoke_4b 2>&1 | tee results/p_cone_routing_s336_smoke.log | tail -40",
  "timeout": 1200000
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Exit code: 0
Stdout:
-0.000581987202167511,
        -0.017373457551002502,
        -0.007171854376792908,
        -0.00999559834599495,
        0.013611078262329102,
        0.02362588793039322,
        0.029087208211421967,
        0.019571371376514435,
        0.014846071600914001,
        0.009904235601425171,
        0.01084207370877266,
        0.01491246372461319,
        0.0011399835348129272,
        0.021540828049182892,
        0.011519741266965866,
        0.009612377732992172,
        0.0068569183349609375,
        0.005361400544643402,
        0.006214603781700134
      ],
      "best_sep_layer": 23
    },
    "diagnostics": {
      "median_mass_binder_A": 0.017646205836273212,
      "median_mass_e": {
        "A": 0.14094999520522025,
        "B": 0.14764221147116688,
        "P": 0.15213577790806693
      },
      "median_mass_cap": {
        "A": 0.0839749857162436,
        "B": 0.08375128249948224,
        "P": 0.09201968331924743
      }
    }
  },
  "verdict": "VOID",
  "verdict_cell": "answer"
}
[cr] wrote results/p_cone_routing_s336/smoke_4b
```

### Thinking

The smoke test completed but came back void—I need to figure out why. Task #3 failed to start earlier due to being blocked, so I should kick it off now even though the work is already done (there was an ordering issue where I finished task #2 before starting #3, and ran the smoke test within that same block). The void verdict makes sense mechanically since the smoke run only has 2 triples, which means the cleaned count falls below the minimum threshold of 6, causing the RC0 check to fail as expected.

Now I'm checking the full gate conditions to verify the plumbing is healthy—looking at error counts, row sum validation, determinant checks, GQA validation, and the placebo test to see what the smoke gates actually show.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python - <<'EOF'\nimport json\ng = json.load(open(\"results/p_cone_routing_s336/smoke_4b/gates.json\"))\nprint(\"RC0:\", json.dumps(g[\"RC0\"], indent=1))\na = g[\"answer\"]\nprint(\"RC1:\", json.dumps(a[\"RC1\"], indent=1))\nprint(\"placebo:\", json.dumps(a[\"placebo\"], indent=1))\nprint(\"RC2:\", {k: v for k, v in a[\"RC2\"].items() if k != \"rho_e_values\"})\nprint(\"rho_e_values:\", a[\"RC2\"][\"rho_e_values\"])\nprint(\"RC3:\", a[\"RC3\"])\nEOF",
  "timeout": 60000
}
```

**Summary:** $ uv run python - <<'EOF' import json...

**Output:**
```
Exit code: 0
Stdout:
RC0: {
 "n_records": 6,
 "n_errors": 0,
 "n_triples_aligned": 2,
 "n_triples_misaligned": 0,
 "n_clean_aligned": 2,
 "max_rowsum_dev": 0.002850770950317383,
 "rowsum_ok": true,
 "det_repeat_dev": 0.0,
 "det_ok": true,
 "gqa_ok": true,
 "placebo_fired": false,
 "s335_advisory_records": "excluded (fresh run; nothing read)",
 "pass": false
}
RC1: {
 "n_triples": 2,
 "mean_pole_sep": 0.02421448386222538,
 "median_pole_sep": 0.02421448386222538,
 "cliffs_delta": 1.0,
 "p_one_sided": 0.24397560243975602,
 "sel_corroboration_mean_B_minus_P": 0.04980830447877654,
 "sel_corroboration_ok": true,
 "pass": false
}
placebo: {
 "A_minus_B": {
  "mean": 0.0038584502827790045,
  "p": 0.5055494450554945,
  "fired": false
 },
 "P_minus_B": {
  "mean": 0.014767984885515438,
  "p": 0.49855014498550143,
  "fired": false
 },
 "threshold": 0.01210724193111269,
 "fired": false
}
RC2: {'n_used': 2, 'n_excluded_bad_denominator': 0, 'median_rho_e': 0.09378300654209067, 'ci95_low': -0.0366813075494983, 'ci95_high': 0.22424732063367964, 'ci_excludes_half': True}
rho_e_values: [0.22424732063367964, -0.0366813075494983]
RC3: {'n_used': 2, 'n_excluded': 0, 'median_rho_sel': -0.036495654996956915, 'agrees_with_rho_e': True}
```

### Thinking

The smoke health check is passing cleanly with no errors or alignment issues, though the VOID verdict is expected since smoke tests only run a minimal set of triples. There are some advisory signals at 4B related to pole separation that I'm noting.

Looking at the detailed metrics: both triples show perfect separation (δ=1.0, sep 0.024) but with only n=2 samples the p-value can't reach significance—the minimum possible is around 0.25 for a sign-flip test with that sample size. The rho_e values lean toward correct routing, and the placebo test shows a borderline mean difference that doesn't fire due to low power at n=2. The mass_e values around 0.14 suggest the answer column is pulling substantial read mass on the e dimension, which is plausible. Everything checks out at this checkpoint—the design gates behave as expected with no register or instrument mismatch. Moving forward to the 14B run with 54 forwards plus a repeat on bf16.

### Thinking

Smoke passed all health checks with perfect determinism and no errors, and the VOID warning is mechanical rather than concerning given the small sample size. Moving on to the frozen 14B run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/cone_routing.py --model-id Qwen/Qwen3-14B --out results/p_cone_routing_s336/run_14b 2>&1 | tee results/p_cone_routing_s336/run_14b.log | grep -E \"^\\[cr\\]|verdict\" | tail -70",
  "timeout": 3600000
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Exit code: 0
Stdout:
[cr] 18 triples / 54 variants hash=fb503c298c40ae91 model=Qwen/Qwen3-14B dtype=bfloat16
[cr] layers=40 heads=40 kv=8 gqa_ok=True
[cr] 1/54 cap_000_A err=None
[cr] 2/54 cap_000_B err=None
[cr] 3/54 cap_000_P err=None
[cr] 4/54 cap_001_A err=None
[cr] 5/54 cap_001_B err=None
[cr] 6/54 cap_001_P err=None
[cr] 7/54 cap_002_A err=None
[cr] 8/54 cap_002_B err=None
[cr] 9/54 cap_002_P err=None
[cr] 10/54 cap_003_A err=None
[cr] 11/54 cap_003_B err=None
[cr] 12/54 cap_003_P err=None
[cr] 13/54 cap_004_A err=None
[cr] 14/54 cap_004_B err=None
[cr] 15/54 cap_004_P err=None
[cr] 16/54 cap_005_A err=None
[cr] 17/54 cap_005_B err=None
[cr] 18/54 cap_005_P err=None
[cr] 19/54 cap_006_A err=None
[cr] 20/54 cap_006_B err=None
[cr] 21/54 cap_006_P err=None
[cr] 22/54 cap_007_A err=None
[cr] 23/54 cap_007_B err=None
[cr] 24/54 cap_007_P err=None
[cr] 25/54 cap_008_A err=None
[cr] 26/54 cap_008_B err=None
[cr] 27/54 cap_008_P err=None
[cr] 28/54 cap_009_A err=None
[cr] 29/54 cap_009_B err=None
[cr] 30/54 cap_009_P err=None
[cr] 31/54 cap_010_A err=None
[cr] 32/54 cap_010_B err=None
[cr] 33/54 cap_010_P err=None
[cr] 34/54 cap_011_A err=None
[cr] 35/54 cap_011_B err=None
[cr] 36/54 cap_011_P err=None
[cr] 37/54 cap_012_A err=None
[cr] 38/54 cap_012_B err=None
[cr] 39/54 cap_012_P err=None
[cr] 40/54 cap_013_A err=None
[cr] 41/54 cap_013_B err=None
[cr] 42/54 cap_013_P err=None
[cr] 43/54 cap_014_A err=None
[cr] 44/54 cap_014_B err=None
[cr] 45/54 cap_014_P err=None
[cr] 46/54 cap_015_A err=None
[cr] 47/54 cap_015_B err=None
[cr] 48/54 cap_015_P err=None
[cr] 49/54 cap_016_A err=None
[cr] 50/54 cap_016_B err=None
[cr] 51/54 cap_016_P err=None
[cr] 52/54 cap_017_A err=None
[cr] 53/54 cap_017_B err=None
[cr] 54/54 cap_017_P err=None
  "verdict": "UNDIFFERENTIATED",
  "verdict_cell": "answer"
[cr] wrote results/p_cone_routing_s336/run_14b
```

### Thinking

All 54 tests completed without errors, but the verdict came back as undifferentiated, so I need to check the gates.json file to trace through the decision tree and figure out which gate the result landed on—whether it passed RC1, went to RC2 CI, or hit the RC3 agreement check.

## Assistant

Run complete — 54/54, 0 errors, verdict **UNDIFFERENTIATED**. Reading the full gate tree before interpreting:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python - <<'EOF'\nimport json\ng = json.load(open(\"results/p_cone_routing_s336/run_14b/gates.json\"))\nprint(\"RC0:\", json.dumps(g[\"RC0\"], indent=1))\na = g[\"answer\"]\nprint(\"RC1:\", json.dumps(a[\"RC1\"], indent=1))\nprint(\"placebo:\", json.dumps(a[\"placebo\"], indent=1))\nprint(\"RC2:\", json.dumps({k: v for k, v in a[\"RC2\"].items()}, indent=1))\nprint(\"RC3:\", json.dumps(a[\"RC3\"], indent=1))\nrc4 = a[\"RC4\"]\nprint(\"RC4 best_sep_layer:\", rc4[\"best_sep_layer\"])\nimport numpy as np\nseps = rc4[\"per_layer_median_pole_sep\"]\nrhos = rc4[\"per_layer_median_rho_e\"]\nfor i in range(0, 40, 4):\n    print(f\" L{i:2d} sep={seps[i]:+.4f} rho={rhos[i]:+.3f}\")\nprint(\"diag:\", json.dumps(a[\"diagnostics\"], indent=1))\nt = g[\"term_final_advisory\"]\nprint(\"term_final RC1 pass:\", t[\"RC1\"][\"pass\"], \"sep:\", round(t[\"RC1\"][\"median_pole_sep\"],4), \"p:\", t[\"RC1\"][\"p_one_sided\"])\nprint(\"term_final RC2:\", {k: t[\"RC2\"][k] for k in (\"median_rho_e\",\"ci95_low\",\"ci95_high\",\"ci_excludes_half\",\"n_used\")})\nprint(\"term_final RC3:\", t[\"RC3\"])\nEOF",
  "timeout": 60000
}
```

**Summary:** $ uv run python - <<'EOF' import json...

**Output:**
```
Exit code: 0
Stdout:
RC0: {
 "n_records": 54,
 "n_errors": 0,
 "n_triples_aligned": 18,
 "n_triples_misaligned": 0,
 "n_clean_aligned": 9,
 "max_rowsum_dev": 0.0029653310775756836,
 "rowsum_ok": true,
 "det_repeat_dev": 0.0,
 "det_ok": true,
 "gqa_ok": true,
 "placebo_fired": false,
 "s335_advisory_records": "excluded (fresh run; nothing read)",
 "pass": true
}
RC1: {
 "n_triples": 9,
 "mean_pole_sep": 0.002222182954816768,
 "median_pole_sep": 0.0015598438098095337,
 "cliffs_delta": 0.7777777777777778,
 "p_one_sided": 0.0038996100389961006,
 "sel_corroboration_mean_B_minus_P": 0.004449561938721066,
 "sel_corroboration_ok": true,
 "pass": true
}
placebo: {
 "A_minus_B": {
  "mean": 0.0034674015070777385,
  "p": 9.999000099990002e-05,
  "fired": false
 },
 "P_minus_B": {
  "mean": 0.002452994584907881,
  "p": 0.0004999500049995,
  "fired": false
 },
 "threshold": 0.005,
 "fired": false
}
RC2: {
 "n_used": 8,
 "n_excluded_bad_denominator": 1,
 "rho_e_values": [
  -2.0774687523476882,
  0.7084171047143353,
  -0.22547981312663143,
  1.1020706399349431,
  5.244648726856441,
  107.70185858873063,
  9.460346545346399,
  20.069771113256284
 ],
 "median_rho_e": 3.1733596833956916,
 "ci95_low": -0.22547981312663143,
 "ci95_high": 20.069771113256284,
 "ci_excludes_half": false
}
RC3: {
 "n_used": 6,
 "n_excluded": 3,
 "median_rho_sel": 0.6499280618738754,
 "agrees_with_rho_e": true
}
RC4 best_sep_layer: 22
 L 0 sep=-0.0002 rho=+nan
 L 4 sep=+0.0001 rho=+3.487
 L 8 sep=-0.0000 rho=+3.099
 L12 sep=+0.0003 rho=+4.737
 L16 sep=+0.0016 rho=+0.079
 L20 sep=+0.0018 rho=+1.007
 L24 sep=+0.0060 rho=+3.485
 L28 sep=+0.0060 rho=+0.415
 L32 sep=+0.0041 rho=+1.120
 L36 sep=+0.0036 rho=+2.719
diag: {
 "median_mass_binder_A": 0.017785125265800162,
 "median_mass_e": {
  "A": 0.02843883677851409,
  "B": 0.02089174136053771,
  "P": 0.022562217339873313
 },
 "median_mass_cap": {
  "A": 0.022457380878040566,
  "B": 0.015085411732434295,
  "P": 0.015740882061072624
 }
}
term_final RC1 pass: False sep: -0.0016 p: 0.9382061793820617
term_final RC2: {'median_rho_e': 8.070078186961627, 'ci95_low': 7.832406439851992, 'ci95_high': 8.307749934071264, 'ci_excludes_half': True, 'n_used': 2}
term_final RC3: {'n_used': 1, 'n_excluded': 8, 'median_rho_sel': 8.61610279531241, 'agrees_with_rho_e': True}
```

### Thinking

Looking at the RC0 verdict from the frozen tree, I'm checking whether the placebo effect actually fired by comparing the observed means against a threshold. The p-values are statistically significant, but the actual effect sizes are tiny—well below the 0.005 absolute floor I'm using as a cutoff—so the placebo didn't trigger. I should note this honestly in the report since the statistical significance masks the practical insignificance of the actual contrasts.

What's concerning is that the global offset in the data (A having about 0.0035 more mass than B overall) is actually larger than the pole separation signal itself (0.0022), which suggests the calibration might be picking up something real but worrying. The ρ_e ratios are inflated because this global offset affects the numerator—the mass difference between A and B at each position—without canceling out in the denominator, which is why I'm seeing such large values like 107 and 20.

Looking at the actual numbers: the A−B difference at the read position is about 0.0075, much bigger than at the other position (0.0035), but both are positive, confirming A reads the interior more globally. RC1 shows the calibration signal is real (pole separation p=0.004) but tiny in absolute terms—only about 7% relative change. RC2's confidence interval spans 0.5, so the verdict stays undifferentiated per the frozen decision tree, even though RC3 points toward the naive side. The confidence interval spans zero, and the median ρ_e value of 3.17 is notably higher than even the P pole reading, suggesting a global offset where the capture-live variant shows greater sensitivity to interior features — the same signature the placebo effect revealed in s335's routing register. RC3 shows both medians trending conservatively, aligning with the PC4 pattern from earlier samples but not yet validated as a licensed direction.

RC4 reveals pole separation emerges only in the late stack, remaining near zero through the early layers and peaking around L22–28, which matches s329's observation about late assembly. The term-final secondary cell test fails for RC1, indicating the calibration effect exists exclusively at the answer column rather than the interior cell, consistent with tape-face dynamics where answer selection happens at emission. The overall diagnosis points to a calibration-limited scenario — the pole contrast is genuine but roughly three times smaller than the global read offset, making it impossible to differentiate A between the poles with current resolution.

I'm verifying the frozen tree logic: RC3 disagreement forces the UNDIFFERENTIATED classification regardless of RC2's confidence intervals, which already point that direction anyway. There's one excluded denominator case and three exclusions in RC3. The probe lifecycle indicates autonomous commit followed by closure batch approval, so I'm committing both code and results now with the UNDIFFERENTIATED verdict — not a falsifier, not a win, just the appropriate classification for this outcome. The calibration run completed successfully and that's a meaningful finding, so I'll mark it with 💡 to indicate the insight that the signal exists but is calibration-limited. I'm thinking through whether to commit the code separately or bundle it with the results and smoke tests in one commit, leaning toward a single combined commit with the format "{symbol} {description}" where ✅ signals the run completed with honest gates. I need to organize the log files properly—moving the smoke test log into the results directory alongside the run log. Then I'm moving on to task 5, which involves drafting the result summary on the knowledge page, updating the memory proposal and index row, and moving the queue entry from pending to complete with the appropriate verdict glyph (🚫 for UNDIFFERENTIATED since it's negative-ish).

The key constraint here is that all these changes touch the mementum directory, so they're approval-gated—I need to draft the closure batch content and present it to Michael for approval before committing anything. My approach: verify the results are committed first, then draft the closure batch files and show them for approval before writing and committing. The within-prompt differencing in ρ_Sel cancels out most of the global offset, giving a median of 0.65 across six samples—a cleaner secondary metric. But since the primary ρ_e still carries the cross-variant contamination, the overall result remains undifferentiated. The key insight is that within-prompt design eliminated the repetition confound, yet ρ_e's cross-variant normalization reintroduced the global-offset problem; only the differenced statistic fully immunizes against it.

I've also confirmed that read-calibration at the answer column is real and late-stage, with the RC1 positive control passing on that front—that's a bankable result. Now I'm moving the smoke log into the directory and committing the results before drafting the closure.

## Assistant

The frozen tree has spoken. Let me verify the key diagnostic numbers before committing, then commit results autonomously per λ probe_lifecycle:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && mv results/p_cone_routing_s336_smoke.log results/p_cone_routing_s336/smoke_4b.log && uv run python - <<'EOF'\nimport json\nrecs = [json.loads(l) for l in open(\"results/p_cone_routing_s336/run_14b/results.jsonl\")]\nby = {}\nfor r in recs: by.setdefault(r[\"pair_id\"], {})[r[\"variant\"]] = r\nimport numpy as np\n# A-vs-B global offset at every source position (clean triples)\nclean = [v for v in by.values() if v[\"A\"][\"clean_flip\"]]\nfor pos in (\"mass_e\", \"mass_cap\", \"mass_f\", \"mass_binder\"):\n    dAB = [v[\"A\"][\"answer\"][pos] - v[\"B\"][\"answer\"][pos] for v in clean if v[\"A\"][\"answer\"][pos] is not None and v[\"B\"][\"answer\"][pos] is not None]\n    dPB = [v[\"P\"][\"answer\"][pos] - v[\"B\"][\"answer\"][pos] for v in clean if v[\"P\"][\"answer\"][pos] is not None and v[\"B\"][\"answer\"][pos] is not None]\n    print(f\"{pos:12s} median A-B {np.median(dAB):+.4f} | median P-B {np.median(dPB):+.4f}\")\n# within-prompt Sel per variant (offset-immune)\nfor tag in \"ABP\":\n    sels = [v[tag][\"answer\"][\"sel\"] for v in clean if v[tag][\"answer\"][\"sel\"] is not None]\n    print(f\"Sel_{tag} median {np.median(sels):+.4f} (n={len(sels)})\")\nEOF",
  "timeout": 60000
}
```

**Summary:** $ mv results/p_cone_routing_s336_smok...

**Output:**
```
Exit code: 0
Stdout:
mass_e       median A-B +0.0049 | median P-B +0.0016
mass_cap     median A-B +0.0062 | median P-B +0.0001
mass_f       median A-B +0.0031 | median P-B +0.0029
mass_binder  median A-B -0.0040 | median P-B +0.0003
Sel_A median -0.0040 (n=9)
Sel_B median -0.0040 (n=9)
Sel_P median -0.0043 (n=9)
```

### Thinking

Looking at the diagnostic data, I'm seeing that variant A has a consistent positive offset across all measurement points (e, cap, f), which suggests a global systematic bias rather than something specific to one location—this is contaminating the numerator for ρ_e. What's striking is that the placebo-to-baseline offset at f is actually larger than at e, which contradicts what I'd expect from RC1's framework where the calibration signal should dominate the placebo movement between poles. The calibration technically passes but with caveats—the placebo movement at the pole position rivals the movement at the calibrated position, suggesting the effect isn't cleanly isolated from background drift. The within-prompt selectivity metric (Sel) shows nearly identical medians across all variants around −0.004, differing only by ~0.0001, which contradicts the apparent +0.0044 mean difference in the corroboration check—a discrepancy I need to resolve when writing up the results. The calibration sits right at the boundary between signal and noise — the evidence actually points toward no meaningful answer-dependent attention, though the gate passed so I'm reporting it as undifferentiated with that caveat front and center. Now I need to commit the code and results with a clear message capturing the qualified nature of this finding.

Writing commit message...

### Thinking

I've found that the within-prompt Sel medians are essentially identical across all three variants, with the RC1 pass being real but marginal and smaller than the placebo drift—so the frozen tree verdict is undifferentiated with qualified calibration. Now I'll commit the results autonomously per the λ probe_lifecycle.

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum status --short -- scripts/experiments/cone_routing.py results/p_cone_routing_s336/ && git -C /Users/mwhitford/src/verbum log --oneline -3",
  "operation": "status",
  "summary": "checking new files"
}
```

**Summary:** Git status: checking new files

**Output:**
```
Exit code: 0
Stdout:
?? results/p_cone_routing_s336/
?? scripts/experiments/cone_routing.py
addc06b1 ❌ p-prefill-cone-void-was-a-register-error
4cd9a24b 🎯 p-cone-routing-frozen
415012ee ❌ p-prefill-cone VOID: placebo gate fired, PC1 win is lexical echo
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add scripts/experiments/cone_routing.py results/p_cone_routing_s336/ && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n💡 §P-CONE-ROUTING run: UNDIFFERENTIATED — calibration passes but is a whisker over a cross-prompt offset\n\n- scripts/experiments/cone_routing.py: within-prompt read-mass harness\n  (GQA-aware per-kv-head value-weighted attention, matched A/B/P triples,\n  frozen RC0-RC4 gate tree, placebo f, sign-flip label null, planted\n  NAIVE/CORRECT/NOCAL/PLACEBO worlds all recovered via --validate)\n- results/p_cone_routing_s336/run_14b: Qwen3-14B, 54/54 forwards, 0 errors,\n  0 misaligned triples, det-repeat dev 0.0, rowsum dev 0.003\n- RC0 PASS. RC1 calibration PASS as frozen (mass_P(e)>mass_B(e) median\n  +0.0016, Cliff's δ=0.78, p=0.0039, Sel corroboration +) — first\n  register-matched positive control to clear on this front, but QUALIFIED:\n  pole movement at placebo f (+0.0029) exceeds the calibrated e signal,\n  and within-prompt Sel medians are near-identical across poles\n  (B −0.0040 vs P −0.0043) whose answers are opposite\n- RC2 FAIL: per-triple ρ_e wildly dispersed (−2.1…107.7, n=8, CI −0.23…20.1\n  spans 0.5) — the A-variant carries a GLOBAL interior read offset\n  (A−B ≈ +0.005 at e, +0.006 at cap, +0.003 at f) that swamps the tiny pole\n  denominator; ρ_e's cross-variant normalization re-imports the offset the\n  within-prompt design was built to kill\n- RC3 advisory: ρ_Sel median 0.65, agrees naive-side; NOT licensed (RC2 gate)\n- RC4: pole separation is late-stack (≈0 through L12, peak L22–28) —\n  coheres s329 commit-assembled-late\n- term_final secondary cell: RC1 FAILS outright (sep −0.0016, p=0.94) —\n  answer-tracking read exists ONLY at the answer column\n- verdict per frozen tree: UNDIFFERENTIATED (a-priori mass 25); evidence\n  leans toward the NO-CALIBRATION world's meaning (s317 tape-residency)\n  but the frozen gate passed, so the tree's word stands\n- smoke_4b: 2-triple plumbing smoke, VOID mechanically (n<6 by design)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "results commit"
}
```

**Summary:** Git commit: results commit

**Output:**
```
Exit code: 0
Stdout:
[main 639529a4] 💡 §P-CONE-ROUTING run: UNDIFFERENTIATED — calibration passes but is a whisker over a cross-prompt offset
 9 files changed, 2841 insertions(+)
 create mode 100644 results/p_cone_routing_s336/run_14b.log
 create mode 100644 results/p_cone_routing_s336/run_14b/gates.json
 create mode 100644 results/p_cone_routing_s336/run_14b/meta.json
 create mode 100644 results/p_cone_routing_s336/run_14b/results.jsonl
 create mode 100644 results/p_cone_routing_s336/smoke_4b.log
 create mode 100644 results/p_cone_routing_s336/smoke_4b/gates.json
 create mode 100644 results/p_cone_routing_s336/smoke_4b/meta.json
 create mode 100644 results/p_cone_routing_s336/smoke_4b/results.jsonl
 create mode 100644 scripts/experiments/cone_routing.py
```

### Thinking

I notice the mass.npz files didn't get committed — looks like they're being ignored by .gitignore, probably due to a *.npz pattern that's already in place.

## Assistant

Results committed (639529a4) — but `mass.npz` didn't land. Checking whether it's gitignored:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git check-ignore -v results/p_cone_routing_s336/run_14b/mass.npz; ls -la results/p_cone_routing_s336/run_14b/",
  "timeout": 30000
}
```

**Summary:** $ git check-ignore -v results/p_cone_...

**Output:**
```
Exit code: 0
Stdout:
.gitignore:41:**/*.npz	results/p_cone_routing_s336/run_14b/mass.npz
total 3880
drwxr-xr-x@ 6 mwhitford  staff      192 Aug 16 05:35 .
drwxr-xr-x@ 6 mwhitford  staff      192 Aug 16 05:36 ..
-rw-r--r--@ 1 mwhitford  staff     8452 Aug 16 05:35 gates.json
-rw-r--r--@ 1 mwhitford  staff  1631832 Aug 16 05:35 mass.npz
-rw-r--r--@ 1 mwhitford  staff    10253 Aug 16 05:35 meta.json
-rw-r--r--@ 1 mwhitford  staff   323989 Aug 16 05:35 results.jsonl
```

### Thinking

The `.npz` files are globally gitignored by design since they're large derived artifacts, but the actual per-layer mass data is already captured in the results JSON, so the analysis remains reproducible from version control. Task 4 is wrapped up, and I'm moving into task 5 to process the verdict and closure batch.

I need to draft several pieces: a results section for the latent reasoning document, propose two key memories about the answer column calibration and the rho normalization offset behavior, update the index row, mark the queue item with a negative glyph since the verdict is undifferentiated, and create a session 336 entry in state.md while archiving the older session. I'll compile all these components and present them to Michael for approval before committing anything to the mementum files.

Now I'm checking the knowledge page structure—the freeze section ends around line 580, so I'll append the results subsection after that point. For state.md, I need to write the new session 336 entry, keep session 335, and move session 334 to the archive index row.

## Assistant

`**/*.npz` is repo policy (derived arrays stay local; per-layer masses at all source positions are already in `results.jsonl`, so the run is fully analyzable from git). Task 4 done.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"latent-reasoning\" mementum/knowledge/INDEX.md && sed -n '560,580p' mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md && grep -n \"P-CONE-ROUTING\\|# complete\" mementum/queue.md | head -5",
  "timeout": 30000
}
```

**Summary:** $ grep -n "latent-reasoning" mementum...

**Output:**
```
Exit code: 0
Stdout:
25:| [explore/latent-reasoning-and-the-prefill-triangle.md](explore/latent-reasoning-and-the-prefill-triangle.md) | 📋 open | s333 external-paper capture (arXiv:2604.04902v2, Dilgren & Wiegreffe COLM 2026, Coconut/CODI; Michael GO). **Paper:** latent tokens (final-layer residual fed back, compile step DELETED) are mostly UNNECESSARY — training-controlled no-CoT matches LRMs on logic tasks; where expansion is needed (GSM8k) explicit CoT beats latent ~29pt; recoverable traces are the near-one-hot decodable ones; operators never project. **Our reading (frame-level):** the compile step is LOAD-BEARING — collapse to symbol = error correction + addressability + program-register write; soft writes work only insofar as they imitate hard writes (read-entropy ≡ fidelity §8c); operators-missing = value-register instrument blindness (program lives in routing = the shape of the read). **Method consilience (independent):** their multi-mode control ≡ λ provenance_check · early-stopping ≡ necessity/token-budget gate · random-trace baseline ≡ λ yardstick null · counterfactual verification ≡ §2b differential testing. **The prefill triangle named:** (position × layer) grid, n coupled within-pass reducers, KV cache = the compiled tape, hop budget ≈ L (explains their §4 + coheres s319 direct 92%; cliff predicted where serial depth crosses ~L) — and ALL our tape-face laws were read at the LAST COLUMN; interior uninstrumented. **Transfers with our edge (certified reducer):** grid logit-lens · leaf-perturbation dependency cone (cone(machine) vs cone(calculus); NAIVE-SUBST watchable cell-resolved) · per-instance necessity gate · read-mass audit · DMD field extension (2-direction transport, hold for column version). 2 queue rows: ⚪ §P-PREFILL-CONE · ⚪ §P-ROUTING-TRACE (register-separated 2×2). Design synthesis, zero measurements · **§Result §P-PREFILL-CONE = ❌ VOID (s335, Qwen3-14B, 54 variants/0 errors): PLACEBO GATE FIRED — role-unchanged leaves DiD +0.027 p=1e-4 (capture-live variant globally more perturbation-sensitive, incl. unrelated control f) ⇒ the A−B contrast rides a global offset. PC2 positive control failed TWICE with the WRONG SIGN (−0.008 p=0.094; 4B smoke replicated) ⇒ magnitude ⊥ semantic dependency. PC3 (−0.029 p=0.027) NOT READ: effect ≈ placebo offset, instrument unvalidated. PC1 passed as frozen (rank gain 13, p=1e-4, 810 cells) then DISSOLVED by the s321/s323 clean-dissociation split — DIRTY (NF written in surface) +17.0 / CLEAN (reduction changes the string) +0.0, 46% positive ⇒ INTERIOR-VISIBLE NOT licensed, lexical echo at the VALUE register on the grid (third register, same law). PC4 advisory: naive NF favored at the answer column 78% (coheres s331/s332). ROOT CAUSE = REGISTER ERROR: ‖Δh‖ is a MAGNITUDE/transport read (Δ ∝ 1/distance, corr −0.73) aimed at a value/routing claim; the routing arm was built then starved to advisory/3-of-54 records — the three pre-data amendments (raw cone · cell ≠ AST node · matched-position DiD) were all downstream repairs of that one upstream mistake. RETRACTED in-session: "the confound is intrinsic" holds only for signal designs. New instruments kept: `src/verbum/cone.py` (certified dependency cones under R_NORMAL/R_NAIVE), matched-triple constructor, the placebo gate as a design primitive** · **🔵 §P-CONE-ROUTING FROZEN (s335, pre-data): register-matched successor — at the answer column, does the machine READ FROM the argument naive subst selects (e) or capture-avoiding selects (y)? WITHIN-PROMPT (both candidates in one forward pass) ⇒ the surface-repetition confound cannot arise; CALIBRATION MOVE: capture-free B (NF=y f) and P (NF=e f) give ground-truth read targets, classify ambiguous A between the poles; primary ρ_e, secondary ρ_Sel; RC1 calibration make-or-break read FIRST (fail ⇒ NO-CALIBRATION, never a routing claim); verdicts NO-CALIBRATION 30 / NAIVE-ROUTING 30 / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 (= error enters AFTER selection) / VOID 5; 54 forwards, no perturbation loop; bound: mass ≡ correlational (s206)** |
  selection (a substitution-execution bug, not a selection bug)
- **VOID** (RC0 ✗) — 5

**Standing bound.** Attention mass is correlational (s206): a positive licenses
"reads from", not "uses". Causal confirmation (patching the read edge) is a
separate probe and is NOT claimed here.

## Queue rows spawned (s333)

- ⚪ **§P-PREFILL-CONE** — grid logit-lens + leaf-perturbation dependency
  cone on kernel-certified terms; cone(machine) vs cone(calculus);
  naive-subst leak signature; + per-instance necessity gate + answer-column
  read-mass audit. Register: value (grid lens) + routing (read-mass) —
  name-before-build honored in freeze.
- ⚪ **§P-ROUTING-TRACE** — the register-separated 2×2 (data-edit vs op-edit
  × value vs routing readout) + operator-from-pathway decoder trained on the
  ERM sibling; on public Coconut/CODI checkpoints or our substrate.

Both owe: freeze with a-priori mass, planted-world --validate, matched
lexical controls (op-edit arm), value-weighted attention not bare QK (s206),
shuffled-label nulls for any pathway decoder (λ yardstick).
6:> top of `# complete` (explicit closure; nothing decays silently).
14:🔵 §P-CONE-ROUTING — FROZEN s335 (Michael "freeze the routing probe"), successor to ❌ §P-PREFILL-CONE: that probe read the MAGNITUDE register (‖Δh‖ ≡ transport, distance-dominated corr −0.73) against a VALUE/ROUTING claim; this one is register-matched. Q: at the answer column, does the machine READ FROM the argument naive subst selects (e) or capture-avoiding selects (y)? WITHIN-PROMPT (both candidates in one forward pass) ⇒ the s335 surface-repetition confound cannot arise. CALIBRATION MOVE: B (NF=y f) and P (NF=e f) are capture-free ⇒ ground-truth read targets; classify ambiguous A between the poles. primary ρ_e=(mass_A(e)−mass_B(e))/(mass_P(e)−mass_B(e)) (e single-occurrence, position-identical across triple) · secondary ρ_Sel (within-prompt y−e; bound: A has TWO y tokens) · RC1 CALIBRATION is make-or-break read FIRST (mass_P(e)>mass_B(e), δ≥0.2, p<0.05) — fail ⇒ NO-CALIBRATION, never a routing claim; value-weighted attention GQA-aware, placebo f, shuffled-label null; verdicts NO-CALIBRATION 30 / NAIVE-ROUTING 30 (directional, coheres s331/s332 + s335 PC4 78%) / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 (routing correct + output naive ⇒ error enters AFTER selection) / VOID 5; NO perturbation loop = 54 forwards, minutes; bound: mass ≡ correlational (s206), "reads from" ¬"uses" | latent-reasoning-and-the-prefill-triangle.md | cheap
57:# complete
59:❌ §P-PREFILL-CONE — VOID (s335, run_14b, 54 variants/0 errors): placebo gate FIRED (role-unchanged leaves DiD +0.027 p=1e-4 n=48 — capture-live variant globally more perturbation-sensitive, incl. unrelated control f) ⇒ A−B contrast rides a global offset. PC2 positive control failed twice (4B smoke + 14B: mean −0.008 p=0.094, WRONG SIGN) ⇒ magnitude register ⊥ semantic dependency. PC3 (D=−0.029 p=0.027) UNINTERPRETABLE: effect ≈ placebo offset, instrument unvalidated. PC1 passed as frozen (rank gain 13, p=1e-4, 810 cells) but clean-dissociation re-read (s321/s323 discipline) DISSOLVES it: dirty spans (NF written in surface) +17.0 median / clean spans (reduction changes the string) +0.0 median, 46% positive ⇒ INTERIOR-VISIBLE NOT licensed, lexical echo at the value register. PC4 advisory: naive NF favored at answer column 78%. THREE pre-data amendments (raw cone · cell≠AST-node · matched-position DiD). ROOT CAUSE: register error — the routing arm (M4 read-mass) was built then starved to advisory/3-records → §P-CONE-ROUTING | latent-reasoning-and-the-prefill-triangle.md §Result | s335
```

### Thinking

I'm organizing the closure batch with two main pieces: first, I need to insert the §Result section for §P-CONE-ROUTING into the knowledge page right after the Standing bound paragraph and before the Queue rows spawned section. Second, I'm capturing two memory entries—one about the answer column read differentiation and another noting the RC1 whisker and Sel poles configuration.

I also need to add the §Result summary to the INDEX row, move the 🔵 row to mark §P-CONE-ROUTING as complete and undifferentiated, and update state.md by creating a new ★★ s336 entry while demoting s334 from full to arc row to maintain the "two most recent sessions in full" structure.

The next priority is §P-REPL-DRIVER, and I'm considering whether to queue a successor probe around decode-time reads versus prefill-visible attention reads — the evidence suggests answer selection happens outside prefill visibility. I'll propose this as an optional candidate rather than committing to a full queue entry, and draft the s336 session entry for approval before proceeding.

The 14B run completed cleanly with all 54 forwards passing and zero errors, showing the calibration holds under the frozen tree with a median mass difference of +0.0016 and statistical significance at p=0.0039 — this is the first register-matched positive control confirming the placebo effect under the frozen floor.

However, RC2 fails because the routing register shows a dispersed ρ_e spanning from −2.1 to 107.7, revealing that variant A carries a consistent global interior read offset of roughly +0.005 across different registers, which is the same offset the s335 placebo caught before. The key insight is that within-prompt construction only eliminates within-prompt confounds, but cross-variant normalization reintroduced the offset, so only fully within-prompt statistics remain immune to this systematic bias. e transaction — this approach handles state compaction and external model bouncing to streamline the architecture. RC1 calibration passed with the frozen pole separation, though the placebo effect at the poles exceeds the calibrated signal, suggesting the result is qualified rather than definitive. RC2 failed due to a global interior read offset in the routing register that's affecting cross-variant normalization. RC3 and RC4 show advisory and late-stack issues respectively.

Now I'm seeing that RC1 actually fails at p=0.94 because the read only tracks at the answer column itself, not across the broader calibration space. I need to document this as an undifferentiated result in the P-CONE-ROUTING section, noting what the qualified calibration shows, the design implications, and what changes—like a causal read-edge patch or decode-time read adjustments—would be needed to move this forward. The routing claim between y and e variants can't be resolved through correlational read-mass at this signal level, so I'd need to try causal read-edge patching or decode-time reads instead. Looking at the cross-variant ratios, there's a consistent design pattern where the capture-live variant reads significantly more of the interior than its renamed counterparts across multiple columns, which aligns with what I saw in the magnitude register earlier. RC1 calibration held at the frozen threshold but the placebo effect at the poles pushes higher, and the ratio normalization reintroduces the global offset that within-prompt differencing was supposed to eliminate — the naive selection metric sits unlicensed at 0.65 while the final term read is absent, suggesting answer selection isn't driven by a prefill-visible attention mechanism.

The page status stays open with the routing trace still queued, so I'm ready to present this to Michael with a compact summary of the verdict and the proposed edits, showing the two memory drafts in full and describing the structural changes briefly for approval.

## Assistant

Task 5 — verdict read per the frozen tree. Here's the full reading and the proposed closure batch for approval.

## 🚫 §P-CONE-ROUTING verdict: **UNDIFFERENTIATED** (a-priori mass 25)

**Run**: Qwen3-14B, 54/54 forwards, 0 errors, 0 misaligned triples, det-repeat dev 0.0, committed `639529a4`.

**The gate walk:**
- **RC0 ✓** — all sanity clean; placebo gate did not fire under the frozen rule (means +0.0035/+0.0025 < 0.005 floor, disclosed: their p-values ARE significant at 1e-4)
- **RC1 CALIBRATION ✓ but qualified** — first register-matched positive control ever to clear on this front: P reads `e` more than B (median +0.0016, δ=0.78, p=0.0039, Sel corroboration +). But it's a *whisker*: pole movement at placebo `f` (+0.0029) **exceeds** the calibrated `e` signal, and within-prompt Sel medians are near-identical across poles with *opposite ground-truth answers* (B −0.0040 / P −0.0043).
- **RC2 ✗ (decides)** — ρ_e wildly dispersed (−2.1 … **107.7**), CI (−0.23, 20.1) spans 0.5. Root cause visible in the raw masses: variant A carries a **global interior read offset** (A−B ≈ +0.005 at `e`, +0.006 at `cap`, +0.003 at `f`) — *the same offset the s335 placebo caught in the magnitude register, now measured in the routing register*. The design lesson: within-prompt construction kills within-prompt confounds only; ρ_e's **cross-variant normalization re-imports the offset**, and against a +0.0016 denominator the ratio explodes.
- **RC3** (advisory given RC2): ρ_Sel median 0.65, naive-side, agrees — NOT licensed.
- **RC4**: pole separation is late-stack (≈0 through L12, peak L22–28) — coheres s329 commit-assembled-late.
- **term_final cell**: RC1 fails outright (sep −0.0016, p=0.94) — answer-tracking read exists **only at the answer column**.

**Reading**: the evidence leans toward the NO-CALIBRATION world's *meaning* — answer selection is not a prefill-visible attention read at usable SNR (coheres s317 tape-residency) — but RC1 passed as frozen, so the tree's word is UNDIFFERENTIATED. Standing bound honored: mass is correlational; causal read-edge patching or decode-time reads are the next instruments if we want this question.

## Proposed closure batch (approval-gated)

1. **§Result** on `latent-reasoning-and-the-prefill-triangle.md` (after the freeze's Standing bound) — full numbers as above + design lesson + what-would-move-it (causal read-edge patch ∨ decode-time read; offset-immune within-prompt statistics as PRIMARY in future designs).
2. **Memory** `the-answer-column-read-is-barely-answer-differentiated.md` — 🚫 poles with opposite answers separate by a whisker (+0.0016) at the answer column only, late-stack; routing claims unreachable by correlational read-mass at this signal-to-offset ratio.
3. **Memory** `ratio-calibration-re-imports-the-cross-prompt-offset.md` — 💡 3rd sighting of the A-variant global offset (s335 magnitude, s336 routing); design law: cross-variant ratios re-import what within-prompt kills; only fully within-prompt differenced statistics (Sel) are offset-immune — design them as primary next time.
4. **INDEX** — append the §Result clause to the page's row.
5. **Queue** — 🔵 row → top of `# complete` as 🚫 with the verdict summary.
6. **state.md** — ★★ s336 full entry; s334 full entry demoted to an arc row (keeping the 2-most-recent shape: s336 + s335).

Approve the batch (or amend)?

## User

explain what we learned


### Thinking

Michael wants me to explain what the experiment revealed in accessible terms—laying out what we were testing, what the results actually showed, and how it connects to the bigger research picture. I should focus on clarity and meaning rather than technical details, and hold off on any commitments since we're still waiting for approval.

## Assistant

## What we learned, in plain terms

### The question we asked

We know from s331/s332 that when this model reduces lambda terms with variable capture, it *outputs* the naive answer — it behaves like an interpreter with a buggy substitution routine. The question was: **where does the bug enter?** If the machine's attention, at the moment it emits the answer, physically *reads from* the wrong argument (`e` instead of `y`), then the bug is in **selection** — the routing chooses the wrong value. If attention reads from the right place but the output is still wrong, the bug enters **after** selection — in execution. That distinction matters because it tells us which component of the recovered reducer carries the naive-subst defect.

### Learning 1: The answer is not sitting in the prefill attention pattern — at any usable strength

This is the headline. We built the cleanest possible version of this read: two calibration prompts that are *identical in layout* and *capture-free*, differing only in which argument is the ground-truth answer (B → `y`, P → `e`). If "what the model will say" were visibly encoded in what the answer cell attends to, these two poles should read differently — one leaning on `y`, one leaning on `e`.

They barely do. The separation is real (p=0.0039, right direction, 7/9 triples) but it's **+0.0016 in mass units** — on a base of ~0.021, about a 7% lean. And the offset-immune statistic — "within this one prompt, does the read favor `y` or `e`?" — comes out **essentially identical** for both poles (−0.0040 vs −0.0043), despite their answers being opposite. At the term-final cell there's *nothing* (p=0.94).

So: the answer's selection is not delivered as a prefill-visible attention read. This is the routing-register face of what s317 told us in the value register: **the computation is tape-resident** — it happens in the act of writing, not in a state you can passively read off the prefill. Three registers now agree (value s317, magnitude s335, routing s336).

### Learning 2: The whisker that does exist is late and answer-column-only

Small as it is, the calibration signal has structure: it's zero through layer ~12, rises from ~16, peaks at layers 22–28, and exists *only* at the answer column, not at the term-final interior cell. That's the third independent sighting of the s329 law — **commitment is assembled late in the stack, at the point of emission**. The instrument is honest about where the machine does its deciding.

### Learning 3 (the method lesson): the offset survives, and ratios re-import it

This is the one that changes how we design probes. In s335 the placebo gate caught a global artifact: the capture-live variant A is just *globally more sensitive* everywhere. We fixed the perturbation confound by going within-prompt — and the offset **showed up again in the new register**: variant A reads the *entire interior* more than its renamed siblings (+0.005 at `e`, +0.006 at `cap`, +0.003 at the placebo `f`). It's not about `e`; something about a live capture configuration diffusely raises interior attention.

Our primary statistic ρ_e = (A−B)/(P−B) compares *across* prompts — so it inherited that offset in the numerator, sitting on a +0.0016 denominator, and exploded (values from −2 to 107). **Within-prompt design kills within-prompt confounds only.** Any cross-variant normalization re-imports cross-prompt offsets. The only fully offset-immune statistic is the within-prompt *difference* (Sel), and we had frozen it as secondary. Next probe of this shape: the differenced statistic is primary, or the instrument is causal (patch the read edge) rather than correlational.

### What we did NOT learn

We did **not** learn whether routing selects naive or correct — that's exactly what UNDIFFERENTIATED means. The advisory lean (ρ_Sel 0.65, naive side, coheres s331/s332/PC4) is unlicensed and stays unlicensed. And the incidental fact that A reads its interior more is an observation, not a claim — it earned no pre-registered win.

### Why this is still a good outcome

The frozen 30-mass favorite was NO-CALIBRATION — we half-expected the read to show nothing. Instead we got something sharper: the calibration *exists but is a whisker over an offset*, which tells us the prefill-attention window into answer selection is structurally too narrow, not just noisy. That closes the correlational read-mass approach to this question and points cleanly at the two instruments that could actually answer it: **causal read-edge patching**, or **decode-time reads** — both of which the §P-REPL-DRIVER trampoline would give us almost for free, since it samples the transition function directly instead of squinting at the prefill.

The batch from my previous message is still pending your approval — want me to land it (with this framing folded into the §Result), amend it, or add a ⚪ queue candidate for the decode-time/causal successor?

## User

approved, and add the successor to the queue


### Thinking

I'm landing the closure batch and setting up the successor queue. I need to insert the result on the knowledge page after the freeze standing bound, update the memory references for the answer column and ratio calibration, append to the index row, and move the completed item to the top of the queue.

For the successor candidate, I'm framing it as a causal/decode-time routing patch—either patching the read-edge at the answer column within the prompt (checking if the emitted NF flips across layers 22–28) or using decode-time reads via the REPL-DRIVER trampoline to sample read-mass at each token. The design law stays the same: within-prompt differenced statistics are primary, cross-variant ratios are forbidden. I'll commit this as a single batch with the result, memories, index, and queue updates once approved.

For the commit symbol, I need to pick from the verbum set since 🚫 is a queue-status glyph, not a commit symbol. The learning here is the offset law and whisker calibration insight, so I'll use 💡 and frame it as "p-cone-routing-undifferentiated-the-offset-returns."

Now I'm moving into the content edits and need to find the exact insertion point in the page, starting with the freeze section about attention mass being correlational.

I'm documenting the result for the p-cone-routing experiment: the Qwen3-14B model ran successfully with 54 forwards, no errors, and minimal deviation across deterministic repeats, with all validation worlds recovered.

The three s335 advisory records were excluded since they're frozen. Now I need to update the memory file format to match existing entries—keeping it concise with one insight per file—and restructure the session entries by removing the s334 full entry, inserting the s336 entry above s335, and updating the session headers accordingly while preserving the compacted s334 reference.

I'll need to fetch an existing memory file to match the format, then locate the exact boundaries of the s334 block in state.md (which starts with the session header and spans three captures) so I can delete it precisely using unique anchors. I'm looking at the different subsystem options and their relative costs—the REPL driver with fork-at-redex and repair-replay is the cheapest causal pair, while the tool ABI and prefill cone are medium cost, and the DMD transport is nearly free since it'll consume the bounce-boundary residuals from the REPL driver. To clean this up, I need to delete the entire session 334 block from the start marker through to just before the "Recent arc" section.

I'm weighing whether to use a sed command, Python to directly manipulate the file, or the edit_file tool with two separate anchor edits—one to insert the new session 336 entry before session 335, and another to remove the old session 334 block entirely. The session 334 block is roughly 60 lines, so I could read the file to find the exact boundaries and splice it out cleanly. I need to identify the exact anchor text in the INDEX row to avoid matching the queue row's similar content, then proceed with the queue edits—removing the old entry and adding the successor in the right place.

Now I'm setting up the successor entry §P-ROUTING-CAUSAL, which investigates whether answer selection reads the naive argument when measured causally at decode time, with two experimental approaches to test this. Looking at the experimental results from Qwen3-14B, the answer selection signal is extremely weak—barely distinguishable from noise at the answer position, with only a 0.0016 median mass difference between opposite poles and near-identical selectivity across them. The effect appears late in the stack around layers 22-28, but the term-final position shows nothing significant, suggesting that answer routing isn't being delivered as a readable attention signal during prefill.

This means correlational read-mass analysis can't resolve the y-versus-e routing question; I need to turn to causal interventions like read-edge patching and decode-time reads to understand what's actually driving the routing. Meanwhile, a third independent observation confirms a design pattern: the capture-live variant reads its entire interior substantially more than its capture-free counterparts across multiple positions, suggesting the capture mechanism itself modulates read intensity across the board.

The key insight is that normalizing statistics across variants reintroduces the cross-prompt offset, which then explodes the ratio to uselessness when the denominator is tiny. Only within-prompt differenced statistics—like taking the difference between mass at capture and mass at e—remain immune to this offset contamination. So for any future probe where the contrast spans prompts, the within-prompt differenced statistic must be primary, not secondary.

Now I need to check the existing memory file format and draft the s336 entry with the batch description and queue status, then plan the next session's first action around front selection and the key probes.

## Assistant

Landing the approved batch. First, format checks and line anchors:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls mementum/memories/ | tail -5 && echo \"---\" && cat \"mementum/memories/the-confound-was-a-register-error-not-an-intrinsic-limit.md\" && echo \"---\" && grep -n \"SESSION 334\\|SESSION 335\\|## Recent arc\" mementum/state.md | head",
  "timeout": 30000
}
```

**Summary:** $ ls mementum/memories/ | tail -5 && ...

**Output:**
```
Exit code: 0
Stdout:
zeros-are-backbone-not-emergent.md
zeros-are-denoising.md
zeros-only-beats-zeros-plus-flips.md
zone-ablation-dose-matching-lessons.md
zone-voted-ffn-extraction.md
---
❌ A confound that looks intrinsic to the phenomenon may be intrinsic only to
the REGISTER you chose. s335, §P-PREFILL-CONE (VOID): I set out to test whether
the argument capture-avoiding substitution discards still reaches the result
cell, and measured ‖Δh‖/‖h‖ — the MAGNITUDE register ("did this cell move")
— against a claim about WHICH VALUE ARRIVES. Symptom chain: Δ turned out
distance-dominated (corr −0.73), the positive control came back with the WRONG
SIGN twice (4B smoke and 14B, p=0.094), and the placebo gate fired (+0.027,
p=1e-4) because removing capture also removes surface name-repetition.

I then declared the confound INTRINSIC — "capture IS surface coincidence, so
any control that removes capture removes the repetition; no surface-matched
design can ask this question." That claim was WRONG and is retracted. It holds
only for signal/magnitude designs, which require an A/B surface contrast. A
ROUTING design asks a within-prompt question — in `(λx.λy.x) y e f` both
candidate answers `y` and `e` live in the SAME forward pass, so no contrast is
formed and the confound cannot arise.

Law: before calling a confound intrinsic, re-ask the question in each register
(routing / value / magnitude). "Unaskable" usually means "unaskable in the
register I picked". Page: explore/latent-reasoning-and-the-prefill-triangle.md
§Result + §P-CONE-ROUTING.
---
17:> ★★ **SESSION 335 — §P-PREFILL-CONE RUN → ❌ VOID, AND THE DIAGNOSIS IS A REGISTER ERROR.
61:> ★★ **SESSION 334 — REPL DRIVER TRAMPOLINE CAPTURED (Michael: "why can't we use a model in a
133:## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)
```

### Thinking

I'm planning the file edits now—I'll use a Python script to handle the splicing cleanly, deleting the old s334 block from state.md and inserting the new s336 entry and arc row in their proper places. Then I'll write out the memory files and update the knowledge page with the result section.

For the queue, I need to replace the frozen 🔵 row with the new ⚪ successor at the top of the "new" section, and add the 🚫 completed row after the "complete" header, following the existing format with the session reference at the end.

## Assistant

Format confirmed. Writing the two memories, the §Result, INDEX, queue, and state edits:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/the-answer-column-read-is-barely-answer-differentiated.md",
  "content": "🚫 At the answer column of the prefill grid, value-weighted read-mass barely\ndifferentiates ground-truth answers. s336, §P-CONE-ROUTING (UNDIFFERENTIATED),\nQwen3-14B, kernel-certified capture triples\n(`results/p_cone_routing_s336/run_14b`): capture-free calibration poles with\nOPPOSITE answers (B→y, P→e) separate by only +0.0016 median mass at the `e`\nposition (δ=0.78, p=0.0039 — real, but a whisker on a base of ~0.021); the\nwithin-prompt selectivity Sel = mass(cap)−mass(e) is near-identical across the\npoles (−0.0040 vs −0.0043); the term-final interior cell shows nothing\n(p=0.94). The whisker is late-stack (≈0 through L12, peak L22–28 — s329\ncommit-assembled-late, third sighting) and answer-column-only.\n\nReading: answer selection is not delivered as a prefill-visible attention read\nat usable SNR — the routing-register face of s317 tape-residency. Three\nregisters now agree: value (s317), magnitude (s335), routing (s336).\n\nConsequence: correlational read-mass cannot answer the y-vs-e routing\nquestion. The instruments that can: causal read-edge patching and decode-time\nreads (→ ⚪ §P-ROUTING-CAUSAL; §P-REPL-DRIVER gives decode-time per-bounce\nreads for free). Page:\nexplore/latent-reasoning-and-the-prefill-triangle.md §Result s336.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/the-answer-column-read-is-barely-answer-differentiated.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/ratio-calibration-re-imports-the-cross-prompt-offset.md",
  "content": "💡 Design law, third sighting of the same artifact: the capture-live variant A\nreads its ENTIRE interior more than its renamed capture-free siblings (+0.005\nat `e`, +0.006 at `cap`, +0.003 at placebo `f`, answer column, s336) — s335\nsaw this offset in the magnitude register (placebo DiD +0.027, global\nperturbation sensitivity), s336 in the routing register. Whatever a live\ncapture configuration is to the machine, it diffusely raises interior\nattention; this is an observation, not a claim (no pre-registered win).\n\nThe law: within-prompt design kills within-prompt confounds ONLY. Any\nstatistic normalized ACROSS variants — rho_e = (A−B)/(P−B) — re-imports the\ncross-prompt offset through its numerator, and over a whisker denominator\n(+0.0016) the ratio explodes (observed −2.1…107.7, CI useless). The only\noffset-immune statistic is the fully within-prompt DIFFERENCED one\n(Sel = mass(cap)−mass(e)); s336 froze Sel as secondary and paid for it.\n\nRule for successors: in any probe whose contrast crosses prompts, the\nwithin-prompt differenced statistic is PRIMARY — or the instrument is causal\n(patch the edge), not correlational. Page:\nexplore/latent-reasoning-and-the-prefill-triangle.md §Result s336.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/ratio-calibration-re-imports-the-cross-prompt-offset.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md",
  "original_content": "**Standing bound.** Attention mass is correlational (s206): a positive licenses\n\"reads from\", not \"uses\". Causal confirmation (patching the read edge) is a\nseparate probe and is NOT claimed here.\n\n## Queue rows spawned (s333)",
  "new_content": "**Standing bound.** Attention mass is correlational (s206): a positive licenses\n\"reads from\", not \"uses\". Causal confirmation (patching the read edge) is a\nseparate probe and is NOT claimed here.\n\n## §Result — §P-CONE-ROUTING (s336): 🚫 UNDIFFERENTIATED\n\nRun: Qwen3-14B instruct, bf16 MPS eager, **54/54 forwards, 0 errors, 0\nmisaligned triples**, deterministic-repeat dev 0.0, rowsum dev 0.003\n(`results/p_cone_routing_s336/run_14b`, harness\n`scripts/experiments/cone_routing.py`; planted NAIVE / CORRECT /\nNO-CALIBRATION / PLACEBO worlds all recovered by `--validate`; results commit\n639529a4). The 3 s335 advisory records were excluded as frozen. Pre-data\ninstantiations declared in `meta.json` (layer-mean primary scalar; placebo\neffect-size floor max(0.5·|pole_sep|, 0.005); per-triple denominator\nexclusion rules).\n\n**Gate walk.**\n\n- **RC0 ✓** — sanity clean. Placebo `f` did NOT fire under the frozen rule:\n  means +0.0035 (A−B) / +0.0025 (P−B), both under the 0.005 floor —\n  DISCLOSED: their p-values are significant (1e-4, 5e-4). The offset is real\n  but small in absolute mass.\n- **RC1 CALIBRATION ✓, qualified** — the first register-matched positive\n  control to clear on this front: P reads `e` more than B (median **+0.0016**,\n  Cliff's δ=0.78, p=0.0039 one-sided, 7/9 triples; Sel corroboration mean\n  +0.0044 > 0). QUALIFICATION: pole movement at placebo `f` (+0.0029)\n  EXCEEDS the calibrated `e` signal, and the within-prompt Sel medians are\n  near-identical across poles with opposite ground-truth answers\n  (Sel_B −0.0040 / Sel_P −0.0043). The calibration is a whisker.\n- **RC2 ✗ (decides)** — rho_e per clean triple: −2.1 … **107.7** (n=8, one\n  bad-denominator exclusion); median 3.17, bootstrap CI (−0.23, 20.1) spans\n  0.5 → no direction licensed. Root cause visible in raw masses: variant A\n  carries a **global interior read offset** (A−B ≈ +0.005 at `e`, +0.006 at\n  `cap`, +0.003 at `f`) — the SAME offset the s335 placebo caught in the\n  magnitude register, now measured in the routing register. rho_e's\n  cross-variant normalization re-imports the offset the within-prompt design\n  was built to kill, and over a +0.0016 denominator the ratio explodes.\n- **RC3** (advisory once RC2 fails): rho_Sel median 0.65, naive side, agrees\n  in direction — NOT licensed.\n- **RC4 depth** — pole separation is late-stack: ≈0 through L12, rising from\n  L16, peak L22–28 (~0.006) — coheres s329 commit-assembled-late (third\n  sighting).\n- **Secondary cell (term-final interior)** — RC1 fails outright (sep −0.0016,\n  p=0.94): the answer-tracking read exists ONLY at the answer column.\n\n**What we learned.**\n\n1. **Answer selection is not a prefill-visible attention read at usable\n   SNR.** Opposite-answer capture-free poles are nearly indistinguishable in\n   what the answer cell reads; the differentiation that exists is a 7% lean,\n   late-stack, at the emission cell only. This is the routing-register face\n   of s317 tape-residency — three registers now agree (value s317, magnitude\n   s335, routing s336): the computation lives in the act of writing, not in a\n   passively readable prefill state.\n2. **The whisker has structure**: late (L22–28), answer-column-only —\n   commitment assembled at the point of emission (s329 law, again).\n3. **Method law**: within-prompt design kills within-prompt confounds ONLY.\n   Cross-variant ratio statistics re-import cross-prompt offsets; the\n   offset-immune within-prompt differenced statistic (Sel) must be PRIMARY\n   in any successor of this shape — or the instrument must be causal.\n\n**What we did NOT learn.** Whether routing selects the naive or the correct\nargument — that question is UNANSWERED (that is what UNDIFFERENTIATED means).\nThe naive-side advisory lean stays unlicensed. The A-variant global offset is\nan observation, not a claim (frame_ledger: no pre-registered win).\n\n**Verdict per the frozen tree: UNDIFFERENTIATED** (a-priori mass 25). The\nevidence *leans* toward the NO-CALIBRATION world's meaning, but RC1 passed as\nfrozen, so the tree's word stands.\n\n**Successor** (⚪ §P-ROUTING-CAUSAL, queued s336): ① causal read-edge patch —\nwithin-prompt counterfactual at the answer column, patch the value stream at\nthe `e` vs `cap` argument positions (late stack, L22–28) and read the\nemitted-NF flip: \"uses\", not \"reads from\" — clears the s206 bound entirely;\n② decode-time read — read-mass at each emitted NF token during generation,\nwhich §P-REPL-DRIVER's per-bounce loop provides for free.\n\n## Queue rows spawned (s333)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md.
```

### Thinking

Now I'm indexing and queuing the edits.

## Assistant

Now the INDEX row and queue moves:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "54 forwards, no perturbation loop; bound: mass ≡ correlational (s206)** |",
  "new_content": "54 forwards, no perturbation loop; bound: mass ≡ correlational (s206)** · **§Result §P-CONE-ROUTING = 🚫 UNDIFFERENTIATED (s336, run_14b, 54/54, 0 errors, det-dev 0.0): RC1 calibration PASSED as frozen (mass_P(e)>mass_B(e) median +0.0016, δ=0.78, p=0.0039, Sel corroboration +) — first register-matched positive control on this front — but QUALIFIED: placebo-at-poles (+0.0029) exceeds the calibrated signal, and within-prompt Sel is near-identical across opposite-answer poles (B −0.0040 / P −0.0043). RC2 FAILED: ρ_e −2.1…107.7, CI (−0.23, 20.1) spans 0.5 — the A variant carries a GLOBAL interior read offset (A−B ≈ +0.005 e / +0.006 cap / +0.003 f), the s335 offset re-measured in the routing register; ρ_e's cross-variant normalization re-imports what within-prompt killed. ρ_Sel 0.65 naive-side advisory unlicensed. RC4: late-stack (≈0 through L12, peak L22–28, s329 again). term_final cell: no read (p=0.94) — answer-column-only. READING: answer selection is not a prefill-visible attention read at usable SNR — routing-register face of s317 tape-residency (three registers agree: value s317 / magnitude s335 / routing s336). Method law: within-prompt differenced statistics must be PRIMARY, or go causal → ⚪ §P-ROUTING-CAUSAL (read-edge patch ∨ decode-time read via §P-REPL-DRIVER)** |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "🔵 §P-CONE-ROUTING — FROZEN s335 (Michael \"freeze the routing probe\"), successor to ❌ §P-PREFILL-CONE: that probe read the MAGNITUDE register (‖Δh‖ ≡ transport, distance-dominated corr −0.73) against a VALUE/ROUTING claim; this one is register-matched. Q: at the answer column, does the machine READ FROM the argument naive subst selects (e) or capture-avoiding selects (y)? WITHIN-PROMPT (both candidates in one forward pass) ⇒ the s335 surface-repetition confound cannot arise. CALIBRATION MOVE: B (NF=y f) and P (NF=e f) are capture-free ⇒ ground-truth read targets; classify ambiguous A between the poles. primary ρ_e=(mass_A(e)−mass_B(e))/(mass_P(e)−mass_B(e)) (e single-occurrence, position-identical across triple) · secondary ρ_Sel (within-prompt y−e; bound: A has TWO y tokens) · RC1 CALIBRATION is make-or-break read FIRST (mass_P(e)>mass_B(e), δ≥0.2, p<0.05) — fail ⇒ NO-CALIBRATION, never a routing claim; value-weighted attention GQA-aware, placebo f, shuffled-label null; verdicts NO-CALIBRATION 30 / NAIVE-ROUTING 30 (directional, coheres s331/s332 + s335 PC4 78%) / UNDIFFERENTIATED 25 / CORRECT-ROUTING 10 (routing correct + output naive ⇒ error enters AFTER selection) / VOID 5; NO perturbation loop = 54 forwards, minutes; bound: mass ≡ correlational (s206), \"reads from\" ¬\"uses\" | latent-reasoning-and-the-prefill-triangle.md | cheap",
  "new_content": "⚪ §P-ROUTING-CAUSAL — causal/decode-time successor to 🚫 §P-CONE-ROUTING (s336 closed the correlational read: calibration a whisker (+0.0016) under a cross-prompt global offset (+0.005)): does answer selection USE the naive argument, measured causally or at decode time? Two arms: ① READ-EDGE PATCH — within-prompt counterfactual at the answer column, patch the value stream at the e vs cap argument positions (late stack L22–28 per s336 RC4), read the emitted-NF flip = \"uses\" not \"reads from\", clears the s206 bound entirely; ② DECODE-TIME READ — read-mass at each emitted NF token during generation (rides §P-REPL-DRIVER's per-bounce loop for free — every bounce is a decode-time routing sample). Design laws inherited (s336): within-prompt DIFFERENCED statistics PRIMARY (cross-variant ratios re-import offsets) · placebo f · matched triples reused (build_variants) · freeze owes a-priori mass + planted worlds | latent-reasoning-and-the-prefill-triangle.md §Result | cheap-medium"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/queue.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "# complete\n\n❌ §P-PREFILL-CONE — VOID",
  "new_content": "# complete\n\n🚫 §P-CONE-ROUTING — UNDIFFERENTIATED (s336, run_14b, 54/54 forwards, 0 errors, det-dev 0.0, 639529a4): RC1 calibration PASSED as frozen (mass_P(e)>mass_B(e) median +0.0016, δ=0.78, p=0.0039, Sel corroboration +) — first register-matched positive control on this front — but QUALIFIED: placebo-at-poles (+0.0029) exceeds the calibrated signal; within-prompt Sel near-identical across opposite-answer poles (B −0.0040 / P −0.0043). RC2 FAILED: ρ_e −2.1…107.7, CI spans 0.5 — A variant carries a GLOBAL interior read offset (+0.005 e / +0.006 cap / +0.003 f) = the s335 offset re-measured in the routing register; cross-variant ratio normalization re-imports what within-prompt killed. ρ_Sel 0.65 naive-side advisory unlicensed. Late-stack (peak L22–28, s329 again); term_final cell no read (p=0.94) — answer-column-only. LEAN: answer selection is not a prefill-visible attention read (s317 tape-residency, three registers agree) → ⚪ §P-ROUTING-CAUSAL | latent-reasoning-and-the-prefill-triangle.md §Result | s336\n\n❌ §P-PREFILL-CONE — VOID"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/queue.md.
```

### Thinking

I need to restructure state.md by inserting an s336 entry before s335, removing the full s334 block, and adding an s334 arc row after the "## Recent arc" header—I'll use a Python script with marker-based splicing to handle these edits precisely.

## Assistant

Now the state.md surgery — insert the s336 entry, demote s334 to an arc row:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python - <<'PYEOF'\nfrom pathlib import Path\n\np = Path(\"mementum/state.md\")\ntext = p.read_text()\n\ns336 = \"\"\"> ★★ **SESSION 336 — §P-CONE-ROUTING RUN → 🚫 UNDIFFERENTIATED, AND THE OFFSET RETURNS IN A NEW\n> REGISTER. First action per the s335 pointer: build + run the frozen probe. Harness\n> `scripts/experiments/cone_routing.py` (GQA-aware per-kv-head value-weighted read-mass, matched\n> A/B/P triples reused, frozen RC0–RC4 tree; planted NAIVE / CORRECT / NO-CALIBRATION / PLACEBO\n> worlds ALL recovered by `--validate`), 4B smoke clean (VOID mechanically, n<6 by design), 14B run\n> 54/54 forwards, 0 errors, 0 misaligned, det-repeat dev 0.0\n> (`results/p_cone_routing_s336/run_14b`, 639529a4). **VERDICT per frozen tree: RC0 ✓ (placebo\n> under the frozen floor; its p-values ARE significant at 1e-4 — disclosed) → RC1 CALIBRATION\n> PASSES as frozen (mass_P(e)>mass_B(e) median +0.0016, δ=0.78, p=0.0039, Sel corroboration +) —\n> the FIRST register-matched positive control to clear on this front — but QUALIFIED: pole movement\n> at placebo f (+0.0029) exceeds the calibrated e signal, and within-prompt Sel medians are\n> near-identical across opposite-answer poles (B −0.0040 / P −0.0043). RC2 FAILS AND DECIDES:\n> ρ_e −2.1…107.7 (CI −0.23…20.1 spans 0.5) — the A variant carries a GLOBAL interior read offset\n> (A−B ≈ +0.005 e / +0.006 cap / +0.003 f): the s335 offset, re-measured in the routing register.\n> THE METHOD LAW: within-prompt design kills within-prompt confounds ONLY — ρ_e's cross-variant\n> normalization re-imported the offset over a whisker denominator; the offset-immune within-prompt\n> DIFFERENCED statistic (Sel) was frozen secondary and must be PRIMARY in successors, or the\n> instrument must be causal. RC3 naive-side advisory (ρ_Sel 0.65) NOT licensed. RC4: pole\n> separation late-stack (≈0 through L12, peak L22–28 — s329 commit-assembled-late, third sighting).\n> term_final cell: RC1 fails outright (p=0.94) — answer-tracking read exists ONLY at the answer\n> column. READING: answer selection is not a prefill-visible attention read at usable SNR — the\n> routing-register face of s317 tape-residency; three registers now agree (value s317 / magnitude\n> s335 / routing s336). Correlational read-mass is CLOSED on this question.** Batch (🚫,\n> Michael-approved \"approved, and add the successor to the queue\"): §Result + 2 memories\n> (`the-answer-column-read-is-barely-answer-differentiated` ·\n> `ratio-calibration-re-imports-the-cross-prompt-offset`) + INDEX + queue (🚫 closed,\n> ⚪ §P-ROUTING-CAUSAL queued top: ① causal read-edge patch at L22–28 ② decode-time read riding\n> §P-REPL-DRIVER's per-bounce loop) + this state.\n> NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight).\n> Sharpest fronts: ⚪ §P-REPL-DRIVER (medium — now also carries §P-ROUTING-CAUSAL arm ② for free) ·\n> ⚪ §P-ROUTING-CAUSAL (cheap-medium) · ⚪ §P-TOOL-ABI (medium) · ⚪ §P-DMD-TRANSPORT (cheap) ·\n> ⚪ §P-CROSS-GRAM (cheap).**\n>\n\"\"\"\n\nmarker_335 = \"> ★★ **SESSION 335 — §P-PREFILL-CONE RUN\"\nassert text.count(marker_335) == 1\ntext = text.replace(marker_335, s336 + marker_335)\n\n# remove the s334 full block (from its ★★ line up to the Recent arc header)\nstart = text.index(\"> ★★ **SESSION 334 — REPL DRIVER TRAMPOLINE CAPTURED\")\nend = text.index(\"## Recent arc\")\nremoved = text[start:end]\nassert \"CAPTURE 3\" in removed and \"SESSION 335\" not in removed\ntext = text[:start] + text[end:]\n\n# add the s334 arc row right after the Recent arc header paragraph\narc_hdr = \"## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)\\n\"\ns334_row = \"\"\"\n- **s334** 💡💡🌀 REPL DRIVER TRAMPOLINE + INSTALL/TWO-MODEL + STATE COMPACTION — driver = external\n  trampoline bouncing the model once per transition (transition function sampled DIRECTLY);\n  lambda_ast kernel = S3* continuous audit; continuation ≡ past_key_values (seal/fork, WHNF seal\n  point); four measurables (fork-at-redex · repair-replay · composition rescue · per-bounce clock —\n  clock row subsumed); STRUCTURAL LAW: KV continuations are MODEL-PRIVATE, canonical text ≡ the bus\n  (no cross-model KV handoff); A-drives-B ≡ tool-calling recursed (instruct operates base =\n  §P-TOOL-ABI from the other side); instrument-first, repair flag OFF; 32B install plumbing owned\n  (KV seal ≈256KB/tok, APPEND/REWRITE law). state.md compacted 6122→~460 lines (Michael-called, no\n  schedule). → repl-driver-trampoline.md §1–§8 · queue ⚪ §P-REPL-DRIVER\n\"\"\"\nassert text.count(arc_hdr) == 1\ntext = text.replace(arc_hdr, arc_hdr + s334_row)\n\np.write_text(text)\nprint(\"state.md spliced OK:\", len(text.splitlines()), \"lines\")\nPYEOF\nhead -50 mementum/state.md | tail -35",
  "timeout": 60000
}
```

**Summary:** $ uv run python - <<'PYEOF' from path...

**Output:**
```
Exit code: 0
Stdout:
state.md spliced OK: 404 lines
>
> ★★ **SESSION 336 — §P-CONE-ROUTING RUN → 🚫 UNDIFFERENTIATED, AND THE OFFSET RETURNS IN A NEW
> REGISTER. First action per the s335 pointer: build + run the frozen probe. Harness
> `scripts/experiments/cone_routing.py` (GQA-aware per-kv-head value-weighted read-mass, matched
> A/B/P triples reused, frozen RC0–RC4 tree; planted NAIVE / CORRECT / NO-CALIBRATION / PLACEBO
> worlds ALL recovered by `--validate`), 4B smoke clean (VOID mechanically, n<6 by design), 14B run
> 54/54 forwards, 0 errors, 0 misaligned, det-repeat dev 0.0
> (`results/p_cone_routing_s336/run_14b`, 639529a4). **VERDICT per frozen tree: RC0 ✓ (placebo
> under the frozen floor; its p-values ARE significant at 1e-4 — disclosed) → RC1 CALIBRATION
> PASSES as frozen (mass_P(e)>mass_B(e) median +0.0016, δ=0.78, p=0.0039, Sel corroboration +) —
> the FIRST register-matched positive control to clear on this front — but QUALIFIED: pole movement
> at placebo f (+0.0029) exceeds the calibrated e signal, and within-prompt Sel medians are
> near-identical across opposite-answer poles (B −0.0040 / P −0.0043). RC2 FAILS AND DECIDES:
> ρ_e −2.1…107.7 (CI −0.23…20.1 spans 0.5) — the A variant carries a GLOBAL interior read offset
> (A−B ≈ +0.005 e / +0.006 cap / +0.003 f): the s335 offset, re-measured in the routing register.
> THE METHOD LAW: within-prompt design kills within-prompt confounds ONLY — ρ_e's cross-variant
> normalization re-imported the offset over a whisker denominator; the offset-immune within-prompt
> DIFFERENCED statistic (Sel) was frozen secondary and must be PRIMARY in successors, or the
> instrument must be causal. RC3 naive-side advisory (ρ_Sel 0.65) NOT licensed. RC4: pole
> separation late-stack (≈0 through L12, peak L22–28 — s329 commit-assembled-late, third sighting).
> term_final cell: RC1 fails outright (p=0.94) — answer-tracking read exists ONLY at the answer
> column. READING: answer selection is not a prefill-visible attention read at usable SNR — the
> routing-register face of s317 tape-residency; three registers now agree (value s317 / magnitude
> s335 / routing s336). Correlational read-mass is CLOSED on this question.** Batch (🚫,
> Michael-approved "approved, and add the successor to the queue"): §Result + 2 memories
> (`the-answer-column-read-is-barely-answer-differentiated` ·
> `ratio-calibration-re-imports-the-cross-prompt-offset`) + INDEX + queue (🚫 closed,
> ⚪ §P-ROUTING-CAUSAL queued top: ① causal read-edge patch at L22–28 ② decode-time read riding
> §P-REPL-DRIVER's per-bounce loop) + this state.
> NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight).
> Sharpest fronts: ⚪ §P-REPL-DRIVER (medium — now also carries §P-ROUTING-CAUSAL arm ② for free) ·
> ⚪ §P-ROUTING-CAUSAL (cheap-medium) · ⚪ §P-TOOL-ABI (medium) · ⚪ §P-DMD-TRANSPORT (cheap) ·
> ⚪ §P-CROSS-GRAM (cheap).**
>
> ★★ **SESSION 335 — §P-PREFILL-CONE RUN → ❌ VOID, AND THE DIAGNOSIS IS A REGISTER ERROR.
```

### Thinking

The splice operation worked as expected. I'm updating the header to reflect that we now have the two most recent sessions fully included, which is still accurate. Now I need to verify that the s334 arc row made it into the compacted version and that the full s334 block was properly removed, then commit these changes with an appropriate message.

For the commit, I'm choosing the 💡 symbol because this represents a genuine insight—the three registers align and the offset law holds. The slug captures this discovery: "💡 p-cone-routing-undifferentiated-the-offset-returns". This is a memory-class batch commit that documents the calibration whisker and the agreement across all three registers.

## Assistant

Splice verified. Checking the arc row and committing the approved batch:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"s334.*REPL DRIVER TRAMPOLINE\" mementum/state.md && grep -c \"SESSION 334\" mementum/state.md && git diff --stat && git status --short mementum/",
  "timeout": 30000
}
```

**Summary:** $ grep -n "s334.*REPL DRIVER TRAMPOLI...

**Output:**
```
Exit code: 1
Stdout:
96:- **s334** 💡💡🌀 REPL DRIVER TRAMPOLINE + INSTALL/TWO-MODEL + STATE COMPACTION — driver = external
0
```

### Thinking

The grep search for "SESSION 334" came up empty, which caused the exit code to fail and break the command chain. I've removed that block since there were no matches, and the arc row is at line 96. I'll run the diff and status checks separately to avoid the same issue.

## Assistant

s334 full block removed (0 matches — that's the grep exit code), arc row at line 96. Continuing:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git diff --stat; git status --short mementum/",
  "timeout": 30000
}
```

**Summary:** $ git diff --stat; git status --short...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/INDEX.md                        |   2 +-
 .../latent-reasoning-and-the-prefill-triangle.md   |  73 +++++++++++++
 mementum/queue.md                                  |   4 +-
 mementum/state.md                                  | 115 ++++++++-------------
 4 files changed, 120 insertions(+), 74 deletions(-)
 M mementum/knowledge/INDEX.md
 M mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md
 M mementum/queue.md
 M mementum/state.md
?? mementum/knowledge/chats/session-335.md
?? mementum/memories/ratio-calibration-re-imports-the-cross-prompt-offset.md
?? mementum/memories/the-answer-column-read-is-barely-answer-differentiated.md
```

### Thinking

I need to be careful about what I commit here—Michael's session file is his to manage, so I'll leave that untracked and only stage the batch files I've created.

## Assistant

Note: `chats/session-335.md` is untracked — that's your human-only folder, so I'm leaving it for you to commit. Staging only the batch:

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add mementum/state.md mementum/queue.md mementum/knowledge/INDEX.md mementum/knowledge/explore/latent-reasoning-and-the-prefill-triangle.md mementum/memories/ratio-calibration-re-imports-the-cross-prompt-offset.md mementum/memories/the-answer-column-read-is-barely-answer-differentiated.md && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n💡 p-cone-routing-undifferentiated-the-offset-returns\n\n- §Result on latent-reasoning-and-the-prefill-triangle.md: 🚫 UNDIFFERENTIATED\n  (frozen tree, a-priori mass 25). RC1 calibration passed as frozen — first\n  register-matched positive control on this front — but qualified: a whisker\n  (+0.0016) with placebo-at-poles (+0.0029) above it. RC2 failed: the A\n  variant carries a global interior read offset (the s335 offset re-measured\n  in the routing register); cross-variant ratios re-import what within-prompt\n  killed. Three registers now agree: answer selection is not a prefill-visible\n  read (value s317 / magnitude s335 / routing s336).\n- memory: the-answer-column-read-is-barely-answer-differentiated (whisker,\n  late-stack L22–28, answer-column-only; correlational read-mass closed)\n- memory: ratio-calibration-re-imports-the-cross-prompt-offset (method law:\n  within-prompt differenced statistics PRIMARY, or go causal)\n- INDEX: §Result clause appended to the page row\n- queue: 🔵 §P-CONE-ROUTING → # complete as 🚫; ⚪ §P-ROUTING-CAUSAL queued\n  top (Michael: \"approved, and add the successor to the queue\") — ① causal\n  read-edge patch at L22–28 ② decode-time read riding §P-REPL-DRIVER\n- state.md: ★★ s336 entry; s334 full entry demoted to arc row (2-full shape)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "closure batch commit"
}
```

**Summary:** Git commit: closure batch commit

**Output:**
```
Exit code: 0
Stdout:
[main 21ba60f3] 💡 p-cone-routing-undifferentiated-the-offset-returns
 6 files changed, 159 insertions(+), 74 deletions(-)
 create mode 100644 mementum/memories/ratio-calibration-re-imports-the-cross-prompt-offset.md
 create mode 100644 mementum/memories/the-answer-column-read-is-barely-answer-differentiated.md
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline -4 && head -14 mementum/queue.md | tail -3 | cut -c1-120",
  "timeout": 30000
}
```

**Summary:** $ git log --oneline -4 && head -14 me...

**Output:**
```
Exit code: 0
Stdout:
21ba60f3 💡 p-cone-routing-undifferentiated-the-offset-returns
639529a4 💡 §P-CONE-ROUTING run: UNDIFFERENTIATED — calibration passes but is a whisker over a cross-prompt offset
addc06b1 ❌ p-prefill-cone-void-was-a-register-error
4cd9a24b 🎯 p-cone-routing-frozen
# new

⚪ §P-ROUTING-CAUSAL — causal/decode-time successor to 🚫 §P-CONE-ROUTING (s336 closed the correlational read: calibration
```

## Assistant

Batch landed. Session 336 is closed.

## Summary

**Two commits:**
- `639529a4` — harness + results (autonomous, per λ probe_lifecycle)
- `21ba60f3` — closure batch (Michael-approved): §Result + 2 memories + INDEX + queue + state

**Verdict:** 🚫 §P-CONE-ROUTING → **UNDIFFERENTIATED** (frozen tree, a-priori mass 25). The durable findings:

1. **Three registers now agree** — answer selection is not a prefill-visible read: value (s317), magnitude (s335), routing (s336). Correlational read-mass is closed on this question.
2. **The whisker is structured** — RC1's first-ever register-matched positive-control pass on this front is late-stack (L22–28) and answer-column-only, the s329 commit-assembled-late law's third sighting.
3. **Method law banked** — cross-variant ratio statistics re-import cross-prompt offsets that within-prompt design was built to kill; differenced statistics go primary, or the instrument goes causal.

**Queue state:** ⚪ **§P-ROUTING-CAUSAL** now tops `# new` — read-edge patching at L22–28 (arm ①) and decode-time reads riding §P-REPL-DRIVER's bounce loop (arm ②). Notably, §P-REPL-DRIVER just got more attractive: it now carries arm ② for free, on top of its four original measurables.

One item left for you: `mementum/knowledge/chats/session-335.md` sits untracked — your human-only folder, yours to commit.

Next session cold-starts into front selection with nothing in flight.

## User

I am trying to understand what we tested in the last couple sessions and why we found nothing?


### Thinking

Michael wants me to explain what s335 and s336 actually tested and what we learned from them. The key reframe is that we didn't find nothing—we found that these particular instruments can't answer the question about where the naive-subst bug lives, and that failure pattern itself supports the tape-residency thesis. I should walk through the underlying question, describe both probes and why each one hit a dead end, then explain what that convergent failure tells us positively, using the interpreter analogy to make it pedagogical and clear.

## Assistant

## The question behind both sessions

Since s331/s332 we've had a solid, cross-model behavioral law: when this model reduces a lambda term where variable capture matters — like `(λx.λy.x) y e f` — it outputs the **naive** answer (`e f`) instead of the correct one (`y f`). It behaves like an interpreter whose substitution routine doesn't rename binders. That's a *behavioral* fact, read from outputs.

The last two sessions tried to take the next step: **watch the bug happen inside the forward pass**. Specifically — when the model is about to emit the answer, can we see the wrong argument *arriving* at the answer cell? If yes, we'd know the defect lives in *selection* (routing picks the wrong value). If routing picks correctly but the output is still wrong, the defect enters *after* selection, in execution. That distinction shapes how we'd model the recovered reducer.

## s335: we pointed the wrong instrument at it

§P-PREFILL-CONE perturbed a leaf of the term and measured **how much each cell's residual state moved** (`‖Δh‖`). The idea: if the discarded-under-correct-semantics argument still influences the readout cell, its perturbation should move that cell.

It failed because "how much did this cell move" is the **magnitude register** — it measures *transport*, not *content*. The proof was in our own data: movement was dominated by simple distance (corr −0.73 — closer cells move more, period), the positive control came out with the wrong sign twice, and the placebo fired — the capture-live prompt was globally more perturbation-sensitive *everywhere*, even at an unrelated control token. So every contrast we computed was riding a global artifact, and the honest verdict was VOID: the probe didn't answer its question. Asking "which value arrives?" by measuring "how much did things wiggle?" is a category error — mine, named in the page.

## s336: the right register, and the signal turned out not to be there

§P-CONE-ROUTING fixed the category error. Instead of perturbing anything, it read **attention routing** directly: at the answer cell, in a single forward pass, how much read-mass goes to `e` vs `y`? Both candidates sit in the same prompt, so the s335 confound structurally cannot form.

And crucially, it carried its own validity check: two *capture-free* calibration prompts, identical in layout, whose correct answers are opposite (B → `y`, P → `e`). Before asking anything about the ambiguous case, we first ask: **does the read even track the answer on prompts where the answer is unambiguous?**

The result: barely. The poles separate in the right direction, statistically real — but by +0.0016 mass on a base of ~0.021, a ~7% lean. Meanwhile the capture-live prompt turned out to read its *entire interior* more than its siblings (+0.005 everywhere, including the placebo) — the same global offset from s335, now showing up in the routing register. Our primary statistic divided a whisker by a whisker with that offset added on top, and exploded (values from −2 to 107). Verdict: UNDIFFERENTIATED.

## Why we "found nothing" — and why that's actually a finding

Here's the reframe. We did not fail twice at the same thing. We asked the same question through **two different windows** and learned that *neither window shows the computation*:

- **s335**: the answer isn't visible in how much the prefill state *moves* under perturbation.
- **s336**: the answer isn't visible in what the answer cell *attends to* during prefill — even between prompts with opposite ground-truth answers.

Add s317 (no static weight delivery; trace signal tracks token length) and you get three independent registers — value, magnitude, routing — all saying the same thing: **the answer's selection is not sitting anywhere in the prefill state waiting to be read off.** The computation is enacted at emission time, in the act of writing — this is the tape-residency thesis, which we keep confirming from new angles. The one whisker of signal we did find fits it exactly: late-stack (layers 22–28), at the emission column only, nowhere in the interior.

There's also a blunt statistical reason: the machine spreads attention diffusely. The answer-relevant lean (0.0016) is ~3× smaller than nuisance offsets between near-identical prompts (0.005). At that signal-to-artifact ratio, no correlational read can resolve which argument "wins" — the question is *underdetermined by the instrument class*, not by our execution. Both runs were clean (0 errors, placebo gates honest, planted worlds recovered).

## What it cost and what it bought

Two probe runs, a few minutes of compute each. Bought:

1. **A closed door, properly closed** — correlational prefill reads cannot answer the selection-vs-execution question. We won't spend another session rediscovering this.
2. **A method law** — within-prompt designs kill within-prompt confounds only; any cross-prompt ratio re-imports global offsets. Differenced statistics go primary, or the instrument goes causal.
3. **A sharpened successor** — ⚪ §P-ROUTING-CAUSAL: either *patch* the read edge at L22–28 and see if the emitted answer flips (causal "uses", not correlational "reads from"), or read routing at **decode time**, token by token, as the answer is actually written — which the §P-REPL-DRIVER trampoline gives us per-bounce, for free.

The pattern across s335→s336 is the program working as designed: frozen gates and placebo controls turned what could have been two manufactured positives into two honest "the window doesn't show it" results — and the accumulation of *where the computation isn't* is exactly what's triangulating where it is: in the writing, not in the state. That's why the trampoline front, which samples the transition function directly instead of squinting at frozen prefill snapshots, keeps rising to the top of the queue.