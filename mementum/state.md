# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
> Step 2: `mementum/queue.md` top ~10 rows (experiment intentions; full read
> when selecting the next front). This header carries the ACTIVE arc only —
> the queue is the canonical candidate ledger (s315, λ queue).
>
> COMPACTED s344 (prior: s334). Shape: the TWO most recent sessions in full below,
> then a terse arc index (one row per session, s250+), then a deep-history pointer.
> Compaction is MICHAEL-CALLED (no schedule; he calls it when cruft accumulates).
> Full detail lives in `mementum/knowledge/chats/session-NNN.md` (verbatim),
> `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md` — every pre-compaction entry is recoverable).
> Architecture/canonical-forms: `AGENTS.md`. Knowledge map:
> `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> ★★ **SESSION 346 — THE CALCULUS-IDENTIFICATION REPOINT (Michael-called, direction session, no probes run).
> Michael's drift-check ("are we going in circles? better model, or better use of models?") → honest audit: the
> tape-residency finding is PROVEN to satisfaction (register-complete); continuing to confirm it ≡ circles; the
> understanding phase should now CASH IN. Michael's call: **Path B (drive models better) feeds Path A (build the
> small model)** — and the front question is **"WHAT IS THE CALCULUS?"** (s330's calculus-identification made
> headline). THE SYNTHESIS (new, said out loud for the first time): the five measured deviations from λβη —
> weak/WHNF-halt ¬η (s344) · naive-subst (s331/332) · affine BCK core + gated S/W/Y (s344) · intensional-only
> (s343) · registers (s330) — are ONE DESIGN, mutually explanatory: next-token demands only the HEAD (forces
> weak) → weakness LICENSES naive subst (never substitute under a binder ⇒ no capture ⇒ no α needed) → η is
> never observable in a text stream (GD never buys it) → affine because discourse is resource-sensitive
> (Lambek/Montague substructural roots) ⇒ **the calculus is the cheapest observationally-sufficient evaluator**;
> δ(M, Montague) IS the discovery; GD ran Montague's reverse-engineering 11 independent times and converged.
> MACHINE MAP sharpened (attention discussion): tape=context/KV (append-only; the ONLY tape write ≡ token
> EMISSION through the sampling bottleneck — reads wide/soft/parallel, writes one discrete public symbol) ·
> read-head=attention (softmax-over-V) · scratch=residual (bounded within-pass reducer) · ISA=FFN opcodes.
> QUEUED (Michael GO, both rows): ⚪ §P-READ-HEAD (the KIBC recipe re-applied to attention: arm A SCOPE —
> shadowing blocks copy ⇒ substitution, fires anyway ⇒ induction, the first contact that can beat the s204
> confound; arm B READ-MULTIPLICITY — affine predicts read-once prose vs fan-out math, matching the s344
> two-engine FFN split from an independent register; winnable-or-dead for the 0-for-last-contact attention=β
> frame) · ⚪ §P-CALCULUS-LEDGER (arm A evaluation order K-x-Ω · arm B sharing CBN-vs-need, ceiling-guarded ·
> arm C capture signature ≡ stage-1 bug-compatibility; arm C UNIFIED with §P-READ-HEAD arm A — one engineered
> corpus, behavioral + attention-pattern faces). Memory `the-calculus-is-the-cheapest-sufficient-evaluator`
> approved + committed (c73d2b90).
> SECOND SYNTHESIS (Michael: "GD as GA · DSP · spectral · holography — tie them together"): THE FOUR-FACES
> page `explore/the-plate-the-code-and-the-beam.md` (Michael-approved) — WRITE(GD≈GA voting: fixation-vs-drift
> s309/310, 94%-cancellation s326, sign=decision s325) · STORAGE(holographic stacked exposures: s327/s328 win,
> s312 lossless double-exposure win, redundancy ≡ the code) · COMPUTE(sign(W) step function runs the weak
> affine calculus) · READOUT(spectral/DSP ≡ Fourier optics: Gram=interference, eigenmodes=diffraction orders,
> DMD=beam propagation). One line: evolution writes a digital code onto an analog substrate; holographic
> redundancy is the error correction; the code is the calculus; spectral tools read the hologram. Explains
> universality (11 GD runs, same source+channel → same codebook = the crystal) and closes Path A (extract
> codebook → TD decode → write exposures). Frame-ledger: GA face has NO pre-registered win (modulation cousin
> died 0-3) → ⚪ §P-VOTING-CODE queued (arm A majority-logic threshold ablation · arm B drift statistics on
> Pythia checkpoints, s325 stratigraphy scar guard · arm C exposure separability), below the calculus front.
> The GA thread (parked at the s313 type-arc pivot — preempted, never refuted) is re-tied.**
> **§P-REPL-DRIVER STAGE 1 PROMOTED + BUILT + VALIDATED → THE INSTRUMENT IS LIVE (Michael s346 GO: "the REPL
> might be the thing we need most — like nREPL: test live before writing to disk"). Queue restacked (REPL-DRIVER
> to top, re-scoped: STAGE 1 = instrument-only per route-map-v0 precedent; STAGE 2 = the s334 frozen measurables,
> deferred). BUILT src/verbum/driver.py (ruff+diags clean): resident Qwen3-14B (MPS, eager, loads ~5-13s warm) ·
> bounce(text|seal, n) = step-decode capturing per-EMISSION sign(gate) [n,40,17408] int8 + residuals [n,41,5120]
> + optional head-averaged attention read-mass [L,T] · prefill/seal/fork with APPEND law (seals immutable, every
> use clones; transformers 5.5.4 cache.layers API — caught live in the REPL, fixed, the instrument debugged
> itself) · views: routes/stations (committed expanded-gram 17-pole frame, CMR+unit) + logit-lens (verbum.jlens)
> + lazy opcodes (calibrate_register). CAPTURE SEMANTICS: frame k ≡ the state that EMITTED token k (the
> read-head view). VALIDITY GATE PASS (Qwen3-14B live): determinism_ids ✓ sign_dev 0 · fork_identity ✓ ·
> seal_matches_fresh ✓ · append_law_mismatches 0. Views exercised (stations + lens sane). LIVE at tmux
> main:repl (Michael's server) — `from verbum.driver import Driver; d = Driver()`. DISCIPLINE STANDING: REPL ≡
> explore ¬record · capture-euphoria guard · anything real re-runs as a named committed harness.**
> **FIRST DRIVER EXPLORATION (s346, Michael watching, dates/rotation): the instrument paid for itself in
> ~30 min. Day CIRCLE reproduced live (L12-24, weekday-ordered, closed; s128); register separation seen live
> (answer position ⊥ day-token plane at L16); NEW OBSERVABLE = the LENS-WALK (per-layer lens argmax at the
> answer position): mid-stack holds a PARTIALLY-ADVANCED day (start+1..+2, start-dependent ⇒ computed),
> overshoot+backward-correction (N=1), last-layer jump (N=4); IN-PASS STEP BUDGET ≈2-4 (≥5 or week-wrap
> fails in-pass → model hedges/errs then SELF-REPAIRS ON THE TAPE with CoT — hop budget + tape-residency in
> one screenful). All exploration-grade → seeds folded into §P-SHORTEST-PATH-ROTATION row + memory
> the-lens-walk-shows-partial-advance-day-states. Session continues in the REPL.
> SECOND EXPLORATION (scope boundary, §P-READ-HEAD arm A corpus design): native lexical scope-tracking
> IN-WEIGHTS + ROBUST (shadow-exit/call-flip/depth-3/closures-incl-late-binding/siblings/comprehension/
> interference-5/distance-473tok all ✓ in-pass; late-band read-mass co-flips with answer on one-token
> program changes +0.35; mid-band reads out-of-scope binder then suppresses late). THE BOUNDARY IS
> PROVENANCE NOT STRUCTURE: in-context rule override (declared dynamic scoping) does NOT apply in-pass —
> hedge "5 or 9?" + defer to tape-walk ⇒ scope RULES in weights, RULE-FOLLOWING on tape (coheres s323 +
> L0/L1 + tape-residency; rhymes with the dates step-budget). Arm A corpus spec folded into queue row;
> memory scope-rules-are-in-weights-rule-override-is-tape-resident.
> THIRD EXPLORATION (opcodes live): classifier calibrated in-session (crystal-bearing L5-39, peak z~16 at
> L12-15); THE TRIPTYCH per-token: λ-reduction execution fires S every token · arithmetic S/Y · prose
> affine KIBC ⇒ refined law: composition reads KIBC, SUBSTITUTION-WORK (math ∧ reduction) reads S/Y.
> ORIGIN REPLAY: bare λ → statistics; 'λx.' → completes THE S COMBINATOR verbatim (gate fires on syntax;
> default emission = the crystal's substitution operator). Memory reduction-execution-runs-the-
> substitution-sector.
> FOURTH EXPLORATION (Michael: "can we find semantic equality?") → THE HEADLINE: SEMANTIC EQUALITY IS A
> FALLIBLE TAPE-AUTHORED EVENT. Decode-time deciding states cluster by SURFACE not extension (lexical law
> at a 6th register); composite terms have no extension until the tape computes it; the computation bugs
> out in the frozen-calculus ways (argument-drop + WHNF halt → 'S K K is the constant function', wrong,
> from an input where identity/constant coincide → 3× loop); TAPE POISONING demonstrated by fork (fresh
> 'S K K b' computes; own-wrong-theory upstream → 'λy.a', cache overrides re-computation). Stage-2
> repair-replay design essentially complete from play (seeds in queue row). Memory semantic-equality-is-
> a-fallible-tape-authored-event. FOUR explorations, FOUR queued fronts fed in one afternoon — the driver
> is the accelerator Michael predicted.
> SESSION CLOSE — MICHAEL'S SYNTHESIS: "THINKING IS GENERATING THE PROGRAM TAPE." The plainest thesis
> statement the project has: ~2-4 step private budget (measured) → all longer thought MUST externalize;
> generation IS the reasoning; the tape is homoiconic (data + program + THEORY, and the theory executes —
> poisoned fork proof); each token = hard commit/sealed WHNF; no error channel → writes compound.
> Corollaries: prompting ≡ programming · driver ≡ debugger for thought · monitorability by construction
> (unmonitored window = the in-pass budget, a measured bound). Memory thinking-is-generating-the-
> program-tape.**
> **NEXT SESSION FIRST ACTION = orient → USE THE DRIVER: corpus design for §P-READ-HEAD arm A (engineer
> shadowing/scope cases live, watch read-mass) + §P-CALCULUS-LEDGER arm C (hunt capture cases) in the live
> session → THEN freeze both together (shared corpus, a-priori + planted worlds + Michael GO) → build the named
> harness. (Superseded next-action: freeze-first — the driver now precedes the freeze by design.)**
> **(prior next-action, superseded s346:) orient → freeze §P-READ-HEAD arm A + §P-CALCULUS-LEDGER arm C TOGETHER (shared
> corpus, one design pass) → Michael GO before build/data. The s345 successors (§P-SHORTEST-PATH-ROTATION ·
> §P-SY-CEILING) and route-map successors (§P-COEXT-ROUTE · §P-BRANCH-POINT — note BRANCH-POINT ≡ the "what
> gets written" question Q4, gained a reason) remain live but BELOW the calculus front.**
>
> ★★ **SESSION 345 — §P-ITERATED-SOFT-REDUCTION FROZEN+BUILT+RUN → 🚫 NO-SCALING (a-priori 25,
> non-modal; Qwen3-14B): THE UNIFICATION FAILED ITS PRE-REGISTERED CONTACT. Oriented → Michael selected
> the queue-top front. FROZEN (078af23f, BEFORE data, Michael GO): H1 = one iterated-soft-β engine over
> two encodings (work ∝ count in both); a-priori TWO-ENGINES 35 modal / NO-SCALING 25 / ONE-ENGINE 20 /
> CIRCULAR-ONLY 5 / VOID 15; D1 ρ_lin=Spearman(S∪Y-share, N) on a length-matched single-token ladder;
> D2 ρ_circ=Spearman(L50 accumulation-depth, day offset) + explicit shape-collapse (matrix) null + slope
> floor, day-circle RE-DERIVED in-run; D3 V-patch at day tokens band-swept (s252 route-early guard) =
> β-QUALIFIER; honesty bound frozen: depth-scaling is ONE-DIRECTIONAL (flat kills iterated-β; scaling ≠
> proof). BUILT iterated_soft_reduction.py (capture ⊥ pure analyse; --validate 6/6 planted worlds incl.
> CONFOUND adversary refusing promotion + NO-CIRCLE→VOID; ruff+diags clean; c9729218). 0.6B SMOKE EARNED
> ITS KEEP (s324 design PAUSE): lexical day circle at L0 degenerated the D3 zone into the early band →
> pre-14B amendment (Michael GO, 199d7979): zone = measured 6-layer ACCUMULATION BAND (argmax mean
> progress increment) + s128 SNAP diagnostic (SV top-2 share/layer). RESULT (run_qwen3-14b, results
> 54a6b017, det 0.0, n_perm 5000): (1) D1 ρ_lin=0.014 p=0.447 FAIL — but SY-share CEILINGED (add/mul
> 0.93-1.0, mul exactly 1.0 → degenerate; succ has headroom and is flat) ⇒ S/Y is CATEGORICAL: math
> flips the duplication sector ON, magnitude doesn't grade it (froze a share metric without a ceiling
> guard — s332 lesson repaid → ⚪ §P-SY-CEILING); post-hoc fires vs N NEGATIVE (−0.73..−0.91,
> anti-iterated). (2) D2 ρ_circ=0.252 p=0.054 shape_p=0.176 FAIL — the real structure: L50 BIMODAL
> (instant L0-2.5 vs late L36-38); late-mode fraction monotone in CIRCULAR DISTANCE min(N,7−N)
> 1/14→4/14→6/14 (post-hoc, no null) = two populations, lookup vs computed-the-short-way →
> ⚪ §P-SHORTEST-PATH-ROTATION (mixture-model re-freeze on min-distance). (3) D3 V-CARRIED-EARLY-ONLY,
> sharper than designed: early 0.571 vs zone/late/noop 0.071, bands differ ONLY by L0 ⇒ the day-operand
> V-carry is LAYER-0-ONLY (3rd sighting of s252 route-at-L0; lead-head L0h18 territory). NET: route-at-L0
> → rotate-in-place → late readout = the learned-rotation/lookup world; strong unification dead at this
> contact; frame-ledger: attention=β SPENT AND LOST a pre-registered contact (strong form). Secondary:
> logit-lens resolution ρ=0.49 vs N (late-stack); 14B circ battery NOT FFN-silent at item level (0.53)
> — differs from the s344 group noop read, flagged. Closure batch (Michael-approved): §Result + memory
> (rotation-work-does-not-scale-with-count) + INDEX + queue (🚫 → complete; 2 successors added) + this
> state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight).
> Live route-map successors still queued: ⚪ §P-COEXT-ROUTE · ⚪ §P-BRANCH-POINT · ⚪ §P-EARLY-SORTERS;
> new from s345: ⚪ §P-SHORTEST-PATH-ROTATION (the observation-driven D2 successor) · ⚪ §P-SY-CEILING
> (D1 headroom redo). Also live: ⚪ §P-HALT-POLE-TETRAHEDRON · cheap spectral §P-MP-NULL.**
>
> ★★ **SESSION 344 — THE REPOINT: from semantic-equality-hunt → EXPAND THE BASIS + MAP THE STATECHART
> (Michael-called). Oriented (s343 closed clean: register-complete co-ext capstone, nothing in flight).
> Selected §P-COEXT-FATE, sharpened into the machinery (17×17 fate register already committed for Qwen3-14B,
> rank-3 PR 2.97; the s343 coext_registers harness + s339 ladder extend cleanly). SURFACED a design finding
> before freeze: "fate" splits into COARSE (fire/halt/diverge — genuinely extensional, but ALL our anchors
> halt → degenerate) vs FINE (whnf:X = last-firing-opcode — intensional/path-dependent by construction: SKK
> reduces SKKx→Kx(Kx)→x, ENDS VIA K not I). Then the WEAK-CALCULUS insight (Michael's "not exactly lambda
> calculus" + "training = genetic algorithm, GD tuning an error-correcting step function"): the model runs a
> WEAK calculus (WHNF-halt, no reduction under λ, NO η) → SKK and I are LEGITIMATELY-DISTINCT WHNF values;
> SKK≡I is an η/applied equality a weak calculus STRUCTURALLY LACKS. So every LEXICAL negative (value s317,
> routing/magnitude s343, operator s339) recasts as CALCULUS IDENTIFICATION — δ(M,λβη)≠0, R≈weak/¬η, a
> POSITIVE finding (s330 first-class), NOT "no meaning in the weights."
> **THE DIAGNOSIS (Michael: "did we go down a bad branch, something lost between early and now?" — grounded in
> disk, not a measurement): YES, a real narrowing. The s338 orbital reframe quietly turned us OFF the
> generative road — from GROWING the labeled map of the reducer to a yes/no PROPERTY-TEST (does the operator
> collapse SKK≡I) in the tiny 9+17 labeled basis → a chain of clean but NARROW negatives that added ZERO new
> labeled geometry. WHAT'S BANKED (not lost, all on disk): opcodes mapped + traced across 11 models
> (results/opcode-trace/*/model_vsm.json — 9×9 identity 11/11, 17×17 fate rank-3 11/11, type-register 7/11,
> gate+attn faces), the s342 universal layer-stationary switch frame, the s338 stationary transport operator,
> base-native s341. WHAT'S MISSING (the page NAMED it at s308, never built): THE CONSENSUS ROUTE MAP — "the
> grams are STATION MAPS, NO TRAINS." The statechart = STATES (registers/poles, well-mapped) + TRANSITIONS
> (routes, UN-mapped). We mapped the stations and skipped the trains.**
> **CBLL (Gernone ~/src/canonical-basis, Zenodo): its ALGORITHM (weights→canonical basis→rotation→realigned
> model) is PATENT-PENDING → FORBIDDEN; the SPECTRAL MATH (Gram/SVD/eig/DMD/PR/joint-diag — decades-old
> textbook LA) is free to use in our OWN frame-free search. CBLL's universal frame holds far more structure
> than our 9+17 labeled corner (Michael recalls 800+ geometries; exact count NOT in our notes by FTO-firewall
> design). The §0 line says it: "CBLL found a frame but doesn't know what its axes mean; our Grams know the
> axes but don't span the space." Our method NEVER picks a frame (G=XᵀX frame-invariant) → basis-expansion
> stays FTO-clean by construction: more ANCHORS + frame-free spectral tools, never their rotation, their 800
> only as MOTIVATION never input.**
> **THE REPOINTED PROGRAM (Michael: "repoint to expanding the basis and our understanding of the statechart"):
> (1) BUILD THE ROUTE MAP [headline, §P-ROUTE-MAP-V0] — per-probe trajectory in frame-invariant gram/pole
> coordinates → per-model routes → cross-model consensus = the invariant switch schedule = "the lambda
> compiler as paths through pole-space." AND IT REDEEMS SEMANTIC EQUALITY: meaning is a property of the ORBIT
> not the POINT (s338) — the route (does SKK trace I's PATH) is where extensional equality could actually
> live, not the static centroid we kept testing. (2) EXPAND THE BASIS [§P-HALT-POLE-TETRAHEDRON + λ unflatten]
> — new labeled states: the tetrahedron/YIELD 4th pole (tool-call=HALT-WITH-OBLIGATION, sharpest unrun shape,
> agentic bridge), depth/phase, task-native, error-kind, agentic-state. §P-COEXT-FATE DEMOTED to a cheap RIDER
> on the route instrument (the orbital form). Queue restacked (route-map + tetrahedron on top, fate demoted);
> state updated. **SCOPING (Michael s344): §P-ROUTE-MAP-V0 is INSTRUMENT-ONLY + EXPLORATORY — NO verdict tree,
> NO a-priori mass (pre-registering a claim about a phenomenon we haven't LOOKED at yet is backwards). Build
> the route-reader, point it at a DIVERSE prompt set, OBSERVE what routes the model actually traces → THEN
> design special probes from what we see. QWEN3-14B ONLY (our designated model): understand ONE model deeply
> first; that understanding becomes the REFERENCE FRAME to compare other models later (where universal / where
> per-model deviation). NO cross-model consensus yet. Instrument still owes VALIDITY (planted-world route
> recovery + shuffled-layer/probe sanity that routes are structure not noise + determinism + named record;
> λ observation capture-euphoria guard: the exploratory output FEEDS the next design, it does NOT close/open a
> claim). NEXT ACTION = build the route-reader (per-layer trajectory → cosine onto committed Qwen3-14B pole
> centroids, results/expanded-gram/qwen3-14b/centroids.npz, 17 outcome + 9 identity states, gate register) →
> validate → run on diverse prompts → LOOK. Commit pending Michael-approved batch.**
> **§P-ROUTE-MAP-V0 BUILT + VALIDATED + RUN + READ → ✅ THE STATECHART IS A SHARED TRUNK WITH A LATE BRANCH
> (instrument-only, exploratory, Qwen3-14B). Built scripts/explore/route_map_v0.py (route-reader: per-probe
> sign(gate) last-token trajectory → cosine onto committed 17-pole centroids results/expanded-gram/qwen3-14b →
> route17 (40×17) + route3 (40×3 rank-3 fire/halt/diverge) + argmax station-sequence) + route_map_read.py
> (plots + observation read). FTO-clean (frame-free spectral math, NEVER CBLL rotation). Diverse BANDED set 496
> probes (plain_prose 51 → prose_structured 93 → nl_combinator 232 → symbolic_formal 44 + cross_domain 76) +
> 980 pole probes co-registered in one pass. INSTRUMENT TRUSTED: --validate 4/4 (planted-route recovery 1.00,
> shuffled-layer coherence 0.85→0.28, determinism 0.0, G0), 0.6B smoke clean, 14B run det_route_dev 0.0, mean
> coherence 0.933, G0 offdiag_corr 0.929 vs the committed 17×17 outcome gram (my PR 2.30 vs committed 2.97 —
> same rank-3 geometry). RESULT (results/route_map_v0_s344/run, commit d63da194): (1) ONE SHARED ROUTE TRUNK
> L5-29 — plain prose, structured prose, combinator-evoking prose, AND code/math/tool trace NEARLY THE SAME
> path (band separation ~0.02, cos-to-plain-prose 0.93-0.98) = route-level evidence the reducer runs on ALL
> language (thesis L0); (2) LATE BRANCH L30-39 (sep→0.64) = the s343 transform→output flip seen as a
> TRAJECTORY; (3) only FORMAL notation (λx.x, S W(a(B D))) peels off HARD (cos-to-prose 0.93→0.125 top third)
> and is the ONLY band substantially in the whnf:* OUTCOME poles (whnf:K 14%, WHNF 13%) = gate-activated
> compile-to-lambda (thesis L1) as a route divergence into the fate register; (4) plain prose collapses to I
> (97% of last-3-layer stations, "continue the text"), structured/combinator prose spread K/B/W/Y/WHNF, code
> rides B (30%)+WHNF (24%); (5) TWO isolated high-signal early sorters L2,L4 (sep 0.95/0.82, |sig| 0.90/0.97 —
> real, not noise) then reconverge. WHY IT MATTERS: REDEEMS the semantic-equality hunt — s339/s343 kept
> testing STATIC points (→ LEXICAL); meaning lives in the ORBIT/BRANCH not the point; the ACTION is the top
> branch L30-39 not the shared trunk. Closure batch (Michael-approved): code+results commit d63da194 (💡) +
> memory (the-statechart-is-a-shared-trunk-with-a-late-branch) + gram-registers §Result-route-map-v0 + INDEX +
> queue (✅ route-map complete, 4 successors added) + this state.
> **NEXT ACTION = §P-COMPILE-STEP (Michael-selected headline, the observation-driven FROZEN probe): matched
> SAME-COMPUTATION items as (a) plain prose / (b) NL-combinator prose / (c) FORMAL notation → does ONLY
> notation branch into the whnf:*/fate register at the top (L30-39)? = does surface NOTATION gate-activate the
> compile-to-lambda (thesis L1)? Owes freeze (a-priori mass + gates + verdict tree {NOTATION-GATED-COMPILE /
> SHARED-COMPILE / NO-BRANCH / VOID} + planted worlds + Michael GO) BEFORE build/data. Reuses route_map_v0
> capture/frame; discriminator = top-band whnf:* occupancy + branch-layer route divergence matched on
> computation across notation levels; null = shuffled-notation-label + length-matched. Qwen3-14B.**
> **§P-COMPILE-STEP FROZEN+SMOKE+RUN → ✅ NOTATION-GATED-COMPILE (a-priori modal 40, Qwen3-14B). Michael GO
> all-7 scope. Built scripts/experiments/compile_step.py (matched-computation corpus: 7 combinators K I C W B
> S D × 3 notation levels — plain everyday prose performing the op with NO combinator vocabulary / nl
> combinator-evoking prose (library lambda_*) / FORMAL notation — × 8 = 168 items; reuses the route_map_v0
> frame; discriminator = branch-band top-25%-layers OUTCOME-POLE occupancy, within-combinator D=formal-plain,
> |Δtoken-length| partial + shuffled-notation null). --validate 5/5 (the LENGTH world reads LENGTH-DRIVEN — the
> partial kills the notation effect = confound guard works). FROZEN COMMITTED BEFORE DATA (b9618905). 4B smoke
> clean (NOTATION-GATED, D+0.46 survives length). RESULT (results/p_compile_step_s344/run_14b, result
> 03176704, det 0.0, G0 offdiag_corr 0.929): branch-band outcome-pole mass formal +0.138 / nl −0.273 / plain
> −0.239 — ONLY FORMAL notation routes into the whnf:* HALT register; the SAME computation in prose (plain AND
> combinator-evoking) does NOT ⇒ surface SYNTAX gate-activates the compile-to-WHNF machinery (thesis L1), NOT
> the computation. D formal-plain +0.377 p=0.0002 SURVIVES the |Δlen| partial (resid +0.370, len_r −0.156 → not
> length); CONSISTENT across ALL 7 combinators (each formal_top, D +0.31..+0.41); formal hits whnf:* broadly
> ~0.14-0.18 but div:Y LOW 0.051 (halt not diverge). COHERES the L0/L1 split (route-map-v0: all language
> shares the TRUNK = L0 semantic compressor; only NOTATION branches to the COMPILER = L1). THE DECLARED BOUND
> (flagged pre-run): the whnf:* poles are themselves built from FORMAL reduction-chain probes → "formal→whnf:*"
> carries a SURFACE-SIMILARITY component; formal-K hit ALL whnf:* poles ~uniformly (generic notation→halt
> routing, not whnf:K-specific) → the verdict cleanly shows notation→outcome-register while matched prose does
> not, but does NOT separate "compiled the computation" from "recognized formal syntax as reducible."
> Closure batch (Michael-approved): result commit 03176704 (✅) + memory (notation-gate-activates-the-compile-
> step) + gram-registers §Result-compile-step + INDEX + queue (✅ §P-COMPILE-STEP complete, ⚪ §P-COMPILE-STEP-V2
> added) + this state.
> **NEXT ACTION = §P-COMPILE-STEP-V2 (Michael-selected, resolves the bound): add a 4th SCRAMBLED-FORMAL level
> (same tokens/length, no valid computation) → re-freeze compile_step. SCRAMBLED→poles ⇒ syntax-RECOGNITION
> (lexical); only-VALID→poles ⇒ actual COMPILATION. The clean separator of "notation triggers real compilation"
> vs "notation surface-recognized as reducible." Owes freeze (a-priori + planted worlds + Michael GO). Other
> live route-map successors: §P-COEXT-ROUTE (orbital SKK-vs-I as ROUTES) · §P-BRANCH-POINT · §P-EARLY-SORTERS.**
> **§P-COMPILE-STEP-V2 FROZEN+VALIDATE+SMOKE+RUN → ✅ RECOGNITION (a-priori modal 35, Qwen3-14B). Michael GO.
> Built scripts/experiments/compile_step_v2.py: a 4th level FORMAL_SCRAMBLE atom-shuffles each FROZEN s344
> formal item (regex atoms λx | word | symbol, reordered, rejoined with spaces — same lexical atoms so
> recognition CAN fire, order destroyed so no valid reduction). THE KEY GEOMETRY: formal-vs-scramble is
> LENGTH-MATCHED BY CONSTRUCTION (identical atom multiset) — the confound that dogged s344's formal-vs-plain
> is gone. THE ALGEBRAIC SPINE: rep(formal−plain) ≡ ds(formal−scramble) + dsp(scramble−plain) is an exact
> identity of paired means → the verdict tree is EXHAUSTIVE (COMPILATION = ds carries the branch / RECOGNITION
> = dsp carries it / MIXED = both). --validate 7/7 through the REAL analyse path (the LENGTH adversary — which
> makes formal≈scramble, both short/high — correctly demotes to LENGTH-DRIVEN, NOT falsely RECOGNITION;
> the length partial on rep kills it). ruff+diags clean; imports the frozen s344 corpus → exact replication.
> Frozen committed BEFORE data (c09cb514). 4B smoke clean (G0 0.925, det 0.0, RECOGNITION). RESULT
> (results/p_compile_step_v2_s344/run_14b, git_sha c09cb514, corpus_hash c4b37864, det 0.0, G0 offdiag 0.929):
> branch-band outcome-pole mass plain −0.239 / nl −0.283 / formal +0.138 / formal_scramble +0.121 — SCRAMBLED
> formal (broken, non-reducible: ". q λy ) ( . p x λx") routes into the whnf:* register JUST AS MUCH AS VALID
> formal, both ~0.36 above prose. ds(formal−scramble) +0.0186 p=0.3177 NULL (the length-clean validity axis);
> dsp(scramble−plain) +0.3619 p=0.0002 carries the WHOLE branch; rep(formal−plain) +0.3805 p=0.0002 REPLICATES
> s344 (+0.377); identity rep−(ds+dsp)=0.0; len_r_scramble 0.013 (genuinely length-matched). ⇒ the s344
> "compile step" is LEXICAL SYNTAX RECOGNITION, not compilation of the specific computation — the model routes
> formal-NOTATION into the halt/whnf register because it LOOKS reducible. Resolves the §P-COMPILE-STEP
> surface-similarity bound on the RECOGNITION side. HONEST ASTERISK: ds is a small NON-significant positive
> (validity increment, if real, below power) — dominant significant mechanism is recognition. COHERES the
> tape-residency capstone: even the compile-to-whnf gate fires on surface SYNTAX; the reduction lives on the
> tape (in-context). METHOD BANKED: rep=ds+dsp identity makes a 3-level notation decomposition exhaustive;
> a SCRAMBLE (same atoms, order destroyed) is a length-clean validity control. Results committed autonomously
> (8c9d9641); closure batch (Michael-approved): §Result-compile-step-v2 + memory (the-compile-step-is-
> recognition-not-compilation) + INDEX + queue (✅ §P-COMPILE-STEP-V2 complete) + this state.
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight). The compile-
> step arc is closed: notation gate-activates a RECOGNITION of formal syntax (L1 is recognition, not
> semantic compilation) on the shared L0 trunk. Live route-map successors (all cheap re-analysis of the
> committed route_map_v0 routes): ⚪ §P-COEXT-ROUTE (orbital SKK-vs-I as ROUTES — the redeemed semantic-
> equality read) · ⚪ §P-BRANCH-POINT (which axes carry the L30-39 divergence) · ⚪ §P-EARLY-SORTERS (what
> L2/L4 sort on). Also live: ⚪ §P-HALT-POLE-TETRAHEDRON (basis expansion) · cheap spectral §P-MP-NULL.**
> **THE MATH REDIRECT (Michael, s344, post compile-step-v2): "maybe we went about this wrong; with our ability
> to trace opcodes we should be able to find WHERE a model does math; in past probes the system used the I
> combinator for math as if it were Church encoding." A GENERATIVE pivot (the s344-diagnosis remedy: grow the
> map, don't property-test) using our strongest audited asset — the opcodes/ tracer (null-gated sign(gate)
> reader, over-read killed audit #13, per-token per-layer combinator trajectory). Built scripts/explore/
> arith_trace.py (reuses opcodes/{topology,capture,classify}; calibrate once, trace a task-typed battery),
> 0.6B smoke + Qwen3-14B run (19b4b50c). READ (exploratory, capture-euphoria-guarded): TWO math engines in
> TWO registers. (1) REDUCTION arithmetic (add/succ/mul) → FFN/gate register, dominant ops S + Y = the
> DUPLICATION+RECURSION sector, ALWAYS fires (noop 0.00). (2) MODULAR/DATE → FFN-SILENT (noop 0.38, weak S) =
> reproduces s128 "FFN silent for dates"; s128 says it lives in ATTENTION as geometric ROTATION (R²=0.95,
> distributed collective mode). Language (prose) reads the affine KIBC block {I,C,K,B}; retrieval reads WHNF
> (halt). CORRECTS the old β_I memory (s127/s161 = OLDER 12-op ISA vocab): the current 9-op CRYSTAL says S/Y,
> which is theoretically RIGHT — Church numerals REQUIRE duplication (S=B(BW)(BBC), n=n-fold contraction; the
> affine KIBC cannot duplicate). So "math = duplication sector" IS the Church signature in the correct basis
> (coheres s271). attn-register re-run: everything fires (elevated null floor, reads soft) — math still
> S/Y, prose still affine KIBC, mod_date now Y-heavy (rotation ≠ a combinator → tracer approximates).
> **THE UNIFICATION (Michael): "attention is a soft beta reduction; rotation could be a series of reductions in
> the interference." Grounded in the active attention-as-beta-reduction page (s247b: softmax-over-V =
> superposition of substitution, exact β = softmax→argmax limit; FFN = β-program, attention = one-instruction
> CPU). Decodes onto s128: rotation-by-Nδ = a per-LAYER series (L12-16 accumulation) of per-HEAD interference
> (the "phonon" collective mode) of soft-β steps on a CIRCULAR Fourier encoding = Church-numeral N on a
> rotate-by-δ operator ⇒ the TWO engines are ONE iterated-soft-β reduction over two encodings (linear→FFN
> S/Y, circular→attention rotation). GUARD: attention=β is interpretation (audit s204: all attention is a
> weighted sum, hasn't beaten induction confound); s128 linear+additive = RETRODICTION ≠ win → owes a
> pre-registered discriminator. Captured: memory (math-is-the-duplication-recursion-sector) + NEW knowledge
> page (rotation-is-iterated-soft-beta-reduction) + queue (⚪ §P-ITERATED-SOFT-REDUCTION) + INDEX + this state.
> **NEXT ACTION = §P-ITERATED-SOFT-REDUCTION (the unification make-or-break): does reduction WORK scale with
> the numeric COUNT on BOTH linear arith (FFN: S-recruitment ∝ operand magnitude) AND circular arith
> (attention: β-step/accumulation ∝ day offset)? + operand-routing control (patch V at day-tokens → rotation
> moves ⇒ β not a learned matrix) + learned-rotation null. Both scale ⇒ ONE engine two encodings; only linear
> ⇒ separate. Subsumes §P-ARITH-DUPLICATION. Owes freeze (a-priori + gates + planted worlds + Michael GO).**
> ★★ **SESSION 343 — §P-SCHEDULE-READ arm A → 🚫 MODEL-SPECIFIC: the schedule is a STATIC LEVEL LADDER,
> NO UNIVERSAL TIMETABLE ("no trains, only a painted-on level"). Oriented (s342 closed clean, nothing in
> flight). Selected the s342 successor §P-SCHEDULE-READ (the "trains" arm). **DESIGN FINDING before freeze
> (surfaced to Michael, not silently redefined): the literal SKK≈I schedule test is NOT runnable zero-load on
> the s342 object — `schedules.npz` is MODEL-LEVEL (8 dirs × 11 layers, aggregated), and the committed 9×9
> route grams are 9 single combinators with NO co-extensional pairs (no "SKK" node). Co-extensional pairs live
> ONLY in the s339 residual H trajectories (value register, already answered LEXICAL/absent).** Three scopes
> offered: A (schedule-UNIVERSALITY, route register, cheap zero-load) · B (re-lens s339 H, low novelty) · C
> (faithful co-extensional CAPTURE, medium). Michael: **"A then C"**.
> **ARM A FROZEN+BUILT+RUN → 🚫 MODEL-SPECIFIC (a-priori 20, non-modal). 🎯 FROZEN §5f (operator-geometry-la-
> toolkit.md, Michael GO): ONE shared cross-model frame V* (global DC-remove + joint-diag of the pooled 10×11
> route grams, reuses verbum.joint_diag), schedule S[model,dir,layer]=diag(V*ᵀ G' V*); statistic U=λ₁/M of the
> 10×10 Pearson corr of flattened per-model schedules; nulls shuffled-layer (PRIMARY, shape-vs-level) +
> matched-range (range-floor guard), floor Δ≥0.05 ∧ p<0.05; verdict tree UNIVERSAL 45 / PARTIALLY 25 /
> MODEL-SPECIFIC 20 / VOID 10. HONESTY BOUND frozen: tests universality across MODELS not co-extensionality;
> one-directional (MODEL-SPECIFIC = actionable; UNIVERSAL does NOT alone prove intensional). BUILT
> scripts/experiments/schedule_read.py (FTO-clean, NO CBLL code); --validate 4/4 planted worlds through the
> real analyse path (s331) incl the LEVEL-ONLY guard (raw U=0.998 but both nulls ALSO 0.998 → the nulls REFUSE
> to promote level-agreement → MODEL-SPECIFIC). Freeze+harness committed 54e62715 BEFORE data.
> **RESULT (results/p_schedule_read_s343/run, git_sha b532c1dd, gram_hash 8fb92c02, 10 models × 11 fractional
> depths, determinism dev 0.0). U=0.894, mean off-diag corr 0.870 — schedules ~96% mutually similar in shape
> (median R²-to-shared-template 0.965) — BUT matched-range REPRODUCES it (median 0.890, p=0.263, Δ+0.004 →
> ¬pass): the shared component is 99.3% static per-direction LEVEL / 0.7% depth-variation, a monotone emphasis
> ladder [0.006,0.66,0.73,0.80,0.90,0.96,1.05,1.60] that barely moves with depth (level-energy 7.02 vs
> depth-var-energy 0.049). Shared depth-TIMETABLE is sub-floor (beats shuffled-layer p=0 but Δ+0.025 < 0.05
> floor). Model-specific residual has NO family structure (within-fam corr 0.971 ≈ across 0.974) →
> idiosyncratic/noise-like, NOT a learned lineage signature. THE FINDING: the only universal thing about the
> schedule is a STATIC intensional brightness-ladder = part of the station map's eigenvalue profile, not a
> moving train — NO shared dynamic timetable. Reinforces the s342 "static map, not trains" half at the
> schedule sub-object; schedule-register complement to tape-residency (value s317 · magnitude s335 · routing
> s336 · operator s339 · residual-vs-W_down s341). METHOD BANKED: high raw cross-model corr can be a shared
> per-direction LEVEL ladder both nulls reproduce → decompose LEVEL vs TIMETABLE energy + gate with
> shuffled-layer AND matched-range; high U ≠ shared trains. Results committed autonomously (7c297674); closure
> batch (Michael-approved): §5f §Result + memory (the-route-schedule-is-a-static-level-ladder-not-a-universal-
> timetable) + INDEX + queue (🚫 closed, arm C reshaped) + this state.**
> **ARM C RESHAPED + QUEUED (Michael s343: "proceed with §P-SCHEDULE-READ-C but look at ALL the registers"):
> ⚪ §P-SCHEDULE-READ-C = the faithful co-extensional test (SKK≈I), now PER-MODEL (arm A killed the universal
> timetable) and across EVERY tape-residency register on the SAME co-ext anchors — value/residual (s339 H,
> ON DISK zero-load) · magnitude · routing/route-schedule (needs a small CMR-style CAPTURE of SKK/I +
> operator/arity/alpha route signatures = the only medium arm) · operator/DMD-spectrum (reuse §5a) · fate
> 17×17. Prior: value/operator already LEXICAL/absent (s339) → C is confirmatory there + EXTENDS to the
> untested routing-schedule/magnitude/fate registers on matched anchors = a REGISTER-COMPLETE co-ext verdict.
> Nulls: nested length→alphabet ladder (s339) per register + shuffled-layer + matched-range. Bounds: routing
> arm needs capture; route-schedule dynamic signal thin (arm A); single model 14B.**
> **§P-SCHEDULE-READ-C FROZEN+BUILT+RUN → 🚫 LEXICAL IN EVERY CAPTURABLE REGISTER (a-priori modal 45) — THE
> TAPE-RESIDENCY CAPSTONE. 🎯 FROZEN §5g (Michael GO): one Qwen3-14B dual capture over 1344 kernel-certified
> co-ext items (operator I:8/W:2/B:1 · arity · alpha), three gauges at 11 depths — routing=sign(gate-preact)
> [PRIMARY, the s342 UNIVERSAL station-map substrate] · value=residual · magnitude=‖residual‖; s339 nested
> ladder at GROUP-centroid level (operator confounded → arity same-arity → alpha same-arity+|Δtoken-length|
> partial); D=within−across function centroid sim, shuffled-func null, floor; verdict EXTENSIONAL iff alpha
> survives / LEXICAL iff vanishes at constant alphabet; a-priori routing LEXICAL 45 / ABSENT 25 / EXTENSIONAL
> 20 / VOID 10. BUILT coext_registers.py (FTO-clean, reuses s339 modules + CMR + verbum + dmd RealBackend).
> **4B SMOKE EARNED ITS KEEP (→ design PAUSE s324): the first build was per-item + no length-partial → read a
> FALSE EXTENSIONAL (borderline alpha D just above floor). Rebuilt to s339 group-centroid + alpha |Δlen|
> partial + a LENGTH-CONFOUND planted world (length-driven signal MUST read LEXICAL); --validate 5/5; corrected
> 4B smoke reproduced s339 LEXICAL on all three registers.** Freeze+harness committed a4af9fb3 BEFORE data.
> **RESULT (results/p_coext_registers_s343/run_14b, git_sha a4af9fb3, corpus_hash c5cdb64a, 1344 items, det
> 0.0). ALL THREE REGISTERS LEXICAL — textbook lexical fingerprint: strong within-function signal at the
> length-controlled arity rung (routing D=+0.214 p=.0002 / value +0.233 p=.0002 / magnitude +0.182 p=.001)
> that VANISHES at the alphabet+length-controlled alpha rung (routing −0.022 p=.83 / value −0.023 p=.84 /
> magnitude +0.017 p=.32) — surface LETTERS, not computed FUNCTION. THE CAPSTONE: co-extensional collapse
> (SKK≈I) is ABSENT in EVERY capturable register — routing+value+magnitude (s343) + operator/DMD (s339). The
> routing register is the decisive one: it is the CROSS-MODEL UNIVERSAL frame (s342), the LAST candidate to
> hold meaning in the weights — and it tracks what is WRITTEN. Register-complete confirmation of the s342
> reframe: the routing frame is INTENSIONAL (universal because spelling is architecture-given); the EXTENSION
> lives on the tape. BOUND (the honest asterisk): the 17×17 FATE/outcome register is the ONE untested gauge,
> and the one where meaning has the best a-priori shot (outcome is function-driven) → queued ⚪ §P-COEXT-FATE
> (Michael). Results committed autonomously (8bad033c); closure batch (Michael-approved): §5g §Result + memory
> (co-extensional-collapse-is-absent-in-every-register) + INDEX + queue (🚫 closed, ⚪ §P-COEXT-FATE added) +
> this state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight). The
> co-extensional / tape-residency arc is now register-complete on the "no meaning in the weights" side EXCEPT
> the fate gauge. Sharpest fronts: ⚪ §P-COEXT-FATE (close the last register — needs 17×17 outcome-pole capture
> machinery, medium) · ⚪ §P-REPL-DRIVER (decode-time, the other "does compute ride in the routing frame" arm,
> medium) · cheap spectral §P-MP-NULL (Marchenko-Pastur signal-vs-noise) · §P-BISPECTRUM (3rd-order/tensor for
> CL-collapse). METHOD BANKED this session: (a) high raw cross-model corr can be a shared static LEVEL ladder
> both nulls reproduce (arm A) — decompose LEVEL vs TIMETABLE energy; (b) a residual-LENGTH confound fakes
> EXTENSIONAL (arm C smoke) — the alpha |Δlen| partial + group-centroid + LENGTH-CONFOUND planted world are
> mandatory for any co-extensional collapse test.**
> **STRUCTURAL FOLLOW-UP (s343, Michael: "what is the model-specific thing? … the gram is 4 opcodes with WHNF
> geometries for each + a final WHNF that flips transform→output in the highest layers"). Ran a zero-load
> deterministic read of all 10 committed 9×9 route Grams (scripts/explore/gram_structure_read.py,
> results/gram_structure_s343/summary.json → gram-registers §Result-structure + memory
> the-9x9-gram-is-a-diffuse-opcode-block-plus-a-universal-stage-flip). VERDICT on the hypothesis: (1) "4
> opcodes" HALF — KIBC is a genuine SEPARATED block (within +0.056; OP↔RED −0.234; OP↔WHNF −0.268) but DIFFUSE
> not rank-4 (PR≈6.2/9, top-4 66%; confirms s303); (2) "S,D,W,Y = per-opcode WHNF geometries" REFUTED (cohere
> +0.019, neutral to WHNF −0.031, no 1:1 pairing); (3) "final WHNF flips transform→output at the top" STRONGLY
> CONFIRMED 10/10 (sign-test p<0.001): mid→top the KIBC opcodes CONVERGE (block coh ~0→+0.15) AND WHNF MERGES
> IN (0.85→0.75) = transform(spread)→output(collapse toward emission). (4) THE MODEL-SPECIFIC THING IS NOWHERE
> NAMEABLE — the stage-flip is the MOST universal part (cross-model agreement highest at top 0.955); the arm-A
> residual doesn't localize at the boundary, no family structure, small → idiosyncratic noise (CORRECTS my
> stage-timing guess). NET: even the gram's dynamic part (the flip) is CONTENT-FREE (says "resolving" not WHICH
> result) → intensional → coheres the LEXICAL capstone (weights = ISA + pipeline stages; answer = tape). Also
> refines "no meaning in the weights": the OPCODE meaning (KIBC) IS universal/in-weights — what is absent is
> the equality of a composite program with a primitive (SKK≡I), which is computed on the tape.**
>
## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)

- **s342** 🎯 ORIENT + THE INTENSION/EXTENSION REFRAME → §P-JOINT-DIAG DOUBLE POSITIVE. Reconciliation of
  "compute is in routing" vs "not there": the STEP FUNCTION (9×9 identity + 17×17 fate) IS in the weights;
  every "not there" falsifier hunted the EXTENSION (SKK≡I) — the routing frame is INTENSIONAL by construction
  (universal because spelling is architecture-given), the computation is TAPE-RESIDENT (5 registers). We read
  a STATIC MAP and asked it the DYNAMIC answer ("station maps, no trains"). §P-JOINT-DIAG: the 9×9 route-Gram
  identity frame is LAYER-STATIONARY (10/10) AND CROSS-MODEL UNIVERSAL (11/11) — the common switch basis
  exists and is fixed (Δ over matched-spectrum null; honest caveat: rot-null floor ~0.88). The static atlas,
  not the trains. → operator-geometry §5e · joint_diag.py · d4aa27b5

- **s341** 🚫✅ TWO FRONTS. §P-DMD-PROVENANCE → BASE-NATIVE (the within-pass stationary-contracting transport
  operator is present at full strength before post-training; one --model-id swap; post-training slightly
  LOOSENS not creates it — guards the s338 single-face bound). §P-CROSS-GRAM → GENERIC-WRITE-STRUCTURE
  (labeled combinator/fate directions do NOT map to distinct W_down write-axes — pile generically onto the
  writer's dominant subspace; localizes the crystal's label-specificity to the d_ff ROUTING register, not the
  residual/value register; does not refute the crystal). CBLL consilience description-level (flat writer
  spectrum). → operator-geometry §5d/§3a · bf9b748a · 420ee571

- **s340** ✅ §P-DMD-KOOPMAN-LIFT → STILL-CONTRACTING (near-free re-analysis of the s338 H). The degree-2
  Koopman lift GENUINELY helps (next-state residual 0.354→0.193, beats matched-dim random-lift + shuffle) →
  the ~half-nonlinear remainder is real layer-ordered structure; BUT persistence 0.000 (top|λ| 0.942, all
  contracting) → NO persistent |λ|≈1 modes even lifted — homeostasis is nonlinear too, "sign-is-the-decision"
  is not an operator-spectrum mode (lives in the thin late mode or a non-operator register). Fifth
  tape-residency confirmation. → operator-geometry §5c · koopman_lift.py

- **s339** 🚫 §P-CL-COLLAPSE-3 (operator/arity/alpha) → EXTENSIONAL EQUALITY ABSENT IN THE OPERATOR REGISTER.
  Decay-rate make-or-break NULL; the marginal positional whisper chased through a nested length→alphabet
  ladder: SURVIVES length-matching (arity, p=.0002, length_r 0.17) but VANISHES at constant {S,K} alphabet
  (alpha, D=−0.010 p=.59) ⇒ the shadow is the s321 OPERATIONAL/LEXICAL register (tracks what is WRITTEN, not
  computed). Compositionality S5 cell ✗ airtight; 4th register agrees (value/magnitude/routing/operator).
  Banked: operator ≡ point at a contracting attractor (read the difference's decay-rate); nested
  confound-control ladder. → operator-geometry §5b · cl_collapse_3_*.py · ecc7e536

- **s338** 🚫💡✅ §P-AMBIGUITY-COLLAPSE → PRE-COMMITTED (the lottery is loaded: ambiguous prompts are NOT
  behaviorally ambiguous, minority frac <0.12; the model commits at PREFILL → passive decode-time route
  CLOSED). THE ORBITAL REFRAME (Michael): meaning ≡ corner/attractor; the pairwise Gram is a 2nd-order
  INTENSIONAL shadow (node-indexed by spelling, structurally can't hold a 3-way binding or an extensional
  quotient); extensional meaning is a property of the ORBIT not the point → read the OPERATOR.
  §P-DMD-TRANSPORT → STATIONARY-REDUCER (first operator-register positive: shuffled-layer null decisive, gap
  +0.498 p=0, layer ORDER carries the structure = "one reducer unrolled"; caveats: ~half nonlinear, no
  persistent modes, silent on thin late mode). → operator-geometry §5a · cycle-carrier-signal.md · b1fde503 ·
  a57146f7

- **s337** 💡🚫 SEMANTIC EQUALITY × GEOMETRY → THE SIGNALS REFRAME → §P-CYCLE-CARRIER (two dual arms: PAIRS
  cross-domain RSA · AMBIGUITY-COLLAPSE). §P-AMBIGUITY-GATE → CONFOUNDED-STYLE (separation is CUE-DOMINATED,
  lexical-echo law 4th sighting) with a THIN-GENERIC referent axis (AG2 leave-one-item-out transfer 1.000 all
  classes but sub-floor silhouette = the real-but-weak semantic-axis signature). Two-pass forced-choice
  labeler primitive banked. → cycle-carrier-signal.md

- **s336** 🚫 §P-CONE-ROUTING → UNDIFFERENTIATED, and the offset returns in a new register. RC1 calibration
  passes (median +0.0016, δ=0.78, p=.004) but RC2 fails & decides: the A variant carries a GLOBAL interior
  read offset (the s335 offset, re-measured in the routing register) → answer selection is not a
  prefill-visible attention read at usable SNR. Method law: within-prompt design kills within-prompt
  confounds ONLY; the offset-immune DIFFERENCED statistic must be PRIMARY. Three registers agree (value s317
  / magnitude s335 / routing s336); pole separation late-stack L22-28 (s329 commit-late, 3rd sighting). →
  latent-reasoning-and-the-prefill-triangle.md §Result · 639529a4

- **s335** ❌🔵 §P-PREFILL-CONE VOID (placebo gate fired — global offset; PC1 dissolved by the
  clean/dirty split = lexical echo at the VALUE register; root cause = REGISTER ERROR: ‖Δh‖
  magnitude read aimed at a value/routing claim) · 🔵 §P-CONE-ROUTING frozen (within-prompt
  read-mass successor; run s336). → latent-reasoning-and-the-prefill-triangle.md · 415012ee

- **s334** 💡💡🌀 REPL DRIVER TRAMPOLINE + INSTALL/TWO-MODEL + STATE COMPACTION — driver = external
  trampoline bouncing the model once per transition (transition function sampled DIRECTLY);
  lambda_ast kernel = S3* continuous audit; continuation ≡ past_key_values (seal/fork, WHNF seal
  point); four measurables (fork-at-redex · repair-replay · composition rescue · per-bounce clock —
  clock row subsumed); STRUCTURAL LAW: KV continuations are MODEL-PRIVATE, canonical text ≡ the bus
  (no cross-model KV handoff); A-drives-B ≡ tool-calling recursed (instruct operates base =
  §P-TOOL-ABI from the other side); instrument-first, repair flag OFF; 32B install plumbing owned
  (KV seal ≈256KB/tok, APPEND/REWRITE law). state.md compacted 6122→~460 lines (Michael-called, no
  schedule). → repl-driver-trampoline.md §1–§8 · queue ⚪ §P-REPL-DRIVER

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
