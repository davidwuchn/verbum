# Running iterated soft-β probe

## User

orient


### Thinking

Since this is a cold start, I should check the state and queue files first to see where things left off.

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
> COMPACTED s344 (prior: s334). Shape: the TWO most recent sessions in full below,
> then a terse arc index (one row per session, s250+), then a deep-history pointer.
> Compaction is MICHAEL-CALLED (no schedule; he calls it when cruft accumulates).
> Full detail lives in `mementum/knowledge/chats/session-NNN.md` (verbatim),
> `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md` — every pre-compaction entry is recoverable).
> Architecture/canonical-forms: `AGENTS.md`. Knowledge map:
> `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
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
  → geometry-holography-signals-convergence.md · 

[OUTPUT TRUNCATED] The tool call succeeded and the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01EzakGHX3PLdogpckkkFPxe.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
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

⚪ §P-ITERATED-SOFT-REDUCTION — THE UNIFICATION (s344, Michael: "attention is a soft beta reduction; rotation could be a series of reductions in the interference"). arith_trace (s344, exploratory, Qwen3-14B) read TWO math engines in TWO registers: reduction arithmetic → FFN gate, S+Y duplication+recursion sector (Church needs duplication: S=B(BW)(BBC), n=n-fold contraction; never NO-OPs); modular/date → FFN-silent, attention geometric rotation (s128, R²=0.95). HYPOTHESIS: they are ONE iterated-soft-β engine over two encodings — rotation-by-Nδ = N soft-β steps (per-layer series L12-16 × per-head interference, the s128 "phonon" collective mode) on a CIRCULAR Fourier encoding = Church-numeral N on a rotate-by-δ operator. GUARD: attention=β is interpretation (audit s204: all attention is a weighted sum, hasn't beaten the induction confound); s128 linear+additive = RETRODICTION ≠ win → owes a PRE-REGISTERED discriminator separating "series of soft-β" from "one learned rotation matrix". THE TEST (covers both engines): count-scaling — does reduction work scale with the numeric count on BOTH linear arith (FFN: S-recruitment ∝ operand magnitude) AND circular arith (attention: β-step/accumulation ∝ day offset)? + operand-routing control (patch V at day-tokens → rotation moves ⇒ β not matrix) + learned-rotation null. Both scale ⇒ ONE engine two encodings; only linear ⇒ separate. Subsumes §P-ARITH-DUPLICATION. Owes freeze (a-priori + gates + planted worlds + Michael GO). Qwen3-14B; gate blind to {B,C}, attn soft (elevated null floor) | rotation-is-iterated-soft-beta-reduction | medium

⚪ §P-COEXT-ROUTE — the REDEEMED orbital semantic-equality test (supersedes the demoted §P-COEXT-FATE static read): compare co-extensional SKK vs I as ROUTES (trunk + branch trajectory through pole-space), NOT static points — do they share the LATE BRANCH (L30-39) even though s339/s343 showed they differ at STATIC points? Meaning is a property of the ORBIT (s338); route-map-v0 showed the branch is where differentiation lives. Reuses route_map_v0 + the s339 co-ext anchors (operator/arity/alpha) + nested length→alphabet ladder on ROUTE-similarity. FROZEN (owes a-priori + planted worlds) | gram-registers §Result-route-map-v0 + operator-geometry §5g | medium

⚪ §P-BRANCH-POINT — the top branch (L30-39) is where routes differentiate; the shared trunk (L5-29) is uninformative by construction (all bands alike). Sharpen the branch: which poles/axes carry the L30-39 divergence, is it the s343 transform→output flip, and does it localize the "output register"? Reuses route_map_v0 routes (re-analysis, cheap) | gram-registers §Result-route-map-v0 | cheap

⚪ §P-EARLY-SORTERS — route-map-v0 found TWO isolated high-signal early layers (L2, L4) that briefly separate the bands (sep 0.95/0.82, |sig| 0.90/0.97) then reconverge. What input feature do they sort on (length? token-type? domain?) before the shared trunk absorbs it? Cheap re-analysis + a targeted matched-feature probe | gram-registers §Result-route-map-v0 | cheap

[CONTENT TRUNCATED] Showing lines 1 to 20 of 140 total lines. Use line_offset=20 parameter to read more content.
```

### Thinking

Nothing's in flight right now, so I should orient and report status. The queue's top item is §P-ITERATED-SOFT-REDUCTION, which owes a freeze from the earlier math redirect — that's the natural next front to propose.

## Assistant

Oriented. Here's where we are:

## State (post-s344, compacted)

**Nothing in flight.** The s344 session closed three arcs cleanly:

1. **§P-ROUTE-MAP-V0** ✅ — the statechart is a **shared trunk (L5-29) with a late branch (L30-39)**; all language rides one route (thesis L0), only formal notation peels off into the whnf:* fate register.
2. **§P-COMPILE-STEP + V2** ✅ — notation gate-activates the halt/whnf register, but the scramble control resolved it as **RECOGNITION not compilation** (dsp carries the whole branch, ds null p=0.32). L1 is lexical syntax recognition; the reduction lives on the tape. Coheres the tape-residency capstone.
3. **THE MATH REDIRECT** (exploratory, arith_trace) — two math engines in two registers: reduction arith → FFN **S+Y duplication/recursion sector** (the Church signature in the correct basis); modular/date → FFN-silent attention **rotation** (s128). Michael's unification hypothesis: **rotation = iterated soft-β reduction** on a circular Fourier encoding → one engine, two encodings.

## Queue top

| Front | Status | Cost |
|---|---|---|
| **§P-ITERATED-SOFT-REDUCTION** — the unification make-or-break: does reduction work scale with count on BOTH linear (FFN S-recruitment ∝ magnitude) AND circular (attention β-steps ∝ day offset)? + operand-routing patch + learned-rotation null | ⚪ owes freeze + Michael GO | medium |
| §P-COEXT-ROUTE — orbital SKK-vs-I as ROUTES (redeemed semantic-equality) | ⚪ | medium |
| §P-BRANCH-POINT — which axes carry the L30-39 divergence | ⚪ | cheap |
| §P-EARLY-SORTERS — what L2/L4 sort on | ⚪ | cheap |

**State's named NEXT ACTION** is §P-ITERATED-SOFT-REDUCTION — it carries the s344 momentum and the standing guards (attention=β is interpretation until it beats the induction confound; s128 is retrodiction ≠ win, so the discriminator must be pre-registered before data).

Per λ queue, front selection requires a **full queue read** — want me to do that and then sharpen §P-ITERATED-SOFT-REDUCTION toward freeze, or do you have a different front in mind?

## User

let's proceed with P-ITERATED-SOFT-REDUCTION


### Thinking

I'm moving forward with the iterated soft-reduction approach, starting by sharpening the design and reviewing the relevant knowledge pages before freezing the probe's parameters and verdict space.

I should also pull in the arith_trace.py script and search for the s128 material on modular/date rotation, since those will inform the discriminator and planted worlds before presenting the proposal to Michael for GO.

## Assistant

Proceeding with §P-ITERATED-SOFT-REDUCTION. Per λ probe_lifecycle: sharpen → freeze (a-priori + gates + verdict tree + planted worlds + your GO) → build → smoke → run. First, recall before design — the unification page, the attention-as-β page, the s128 material, and the arith_trace instrument.

### Tool Call: shell_command (failed)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/mementum/knowledge/explore/ | grep -i -E \"rotation|beta|attention|arith\" ; echo ---; git -C /Users/mwhitford/src/verbum grep -l -i \"iterated-soft\" -- mementum/knowledge/ ; echo ---; ls /Users/mwhitford/src/verbum/scripts/explore/ | grep -i -E \"arith|opcode\" ; echo ---; ls /Users/mwhitford/src/verbum/scripts/explore/opcodes/ 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/meme...

**Output:**
```
Exit code: 1
Stdout:
attention-as-beta-reduction.md
attention-spiral-finding.md
combinator-training-beta-reduction.md
date-fourier-rotation.md
ffn-beta-reduction-indexing.md
q-rotation-etching.md
rope-attention-spiral.md
rotation-is-iterated-soft-beta-reduction.md
strided-attention-float-ab.md
---
mementum/knowledge/INDEX.md
mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md
---
arith_trace.py
---
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md"
}
```

**Summary:** Reading rotation-is-iterated-soft-beta-reduction.md (0-2000)

**Output:**
```
---
title: "Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One"
status: open
category: synthesis
tags: [beta-reduction, attention, rotation, fourier, church-encoding, combinator, duplication, interference, arithmetic, unification]
related:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
  - gram-registers-and-the-route-map.md
  - ../curry-howard-closes-the-loop.md
depends-on:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
created: session 344
---

# Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One

> Session 344 (Michael: "we have speculated that attention is a soft beta reduction;
> that rotation could be a series of reductions in the interference"). A unifying
> hypothesis reached from a fresh exploratory read (`arith_trace`, Qwen3-14B) + two
> standing findings (attention-as-beta-reduction s247b; date-fourier-rotation s128).
> Theory, grounded in retrodiction; owes a pre-registered discriminator to earn keep.

## The two-engines observation (arith_trace, s344, exploratory)

Pointing the audited opcode tracer (`opcodes/`, null-gated sign(gate) reader) at a
task-typed battery on Qwen3-14B reads TWO math mechanisms in TWO registers:

| math kind | register | opcode read |
|---|---|---|
| **reduction arithmetic** (2+3, succ, ×) | **FFN / gate** | **S, Y** — the duplication+recursion sector; never NO-OPs |
| **modular / cyclic** (dates, clock, day-of-week) | **attention** | FFN-**silent** (NO-OP 0.38); s128: geometric **rotation**, R²=0.95 |

Language (prose) reads the affine **KIBC** block `{I,C,K,B}` in both registers;
retrieval reads **WHNF** (halt/lookup). So math ≠ language (duplication sector vs
affine block), and *within* math, reduction ≠ rotation (FFN S/Y vs attention
rotation). The old "β_I for arithmetic" memory (s127/s161) was the OLDER 12-op ISA
vocabulary; the current 9-op CRYSTAL says the operative opcodes are **S, Y** — which
is theoretically *correct*: Church numerals REQUIRE duplication (`S = B(BW)(BBC)`;
numeral n = n-fold application = n contractions), and the affine KIBC fragment cannot
duplicate. Math being S/Y-heavy *is* the Church signature in the right basis.

## The unifying hypothesis: rotation = iterated soft-β on a circular encoding

`attention-as-beta-reduction.md` (s247b) already pins attention as **soft β-reduction**:
`out_i = Σ_j softmax(q_i·k_j) v_j` — Q = redex seeking its operand, K = operand
addresses, V = operands, softmax = selection; the softmax is a *convex combination*
(superposition of substitution), exact β being the `softmax → argmax` limit. FFN = the
β-program (ROM); attention = the one-instruction CPU.

Michael's extension decodes cleanly onto s128's own numbers:

> **"a series of reductions in the interference"** = a per-**layer series** (rotation
> *accumulates across L12→L16*, s128) of per-**head interference** (the *distributed
> collective mode*, "like a phonon," top-10 heads each adding ~0.15 rad, s128).

Composing: **rotation-by-Nδ = N soft-β steps on a *circular* (Fourier) encoding**, each
step a superposition-of-substitutions interfering across heads into a net rotation. And
rotation-by-Nδ = iterated application of rotate-by-δ = **Church-numeral N acting on a
rotate-by-δ operator on the day-circle**. That is the *same* iterated-soft-β engine as
linear arithmetic — the S/Y duplication+recursion sector — just executed on a **circular
representation** instead of a linear one. **The two engines collapse into one:** iterated
soft-β reduction over two encodings (linear → FFN; circular → attention).

## The discipline guard (why this is not yet a win)

Our own audit flags it (s204, `audit-registry` #): *"all attention is a weighted sum;
'β-reduction' is interpretation... induction/n-gram heads produce similar patterns."* So
"attention = soft β" is a beautiful lens, **trivially true at the weighted-sum level**,
that has NOT beaten the confound. And s128's linear-in-N + additive-across-heads fit
**retrodicts** the series-of-reductions story — but a learned rotation matrix R(Nδ) also
produces linear-in-N + additive heads. Per the frame ledger, **retrodiction ≠ win.** This
owes a *pre-registered* discriminator that separates "series of soft-β reductions" from
"one learned rotation," not another retrofit.

## The discriminating make-or-break — ⚪ §P-ITERATED-SOFT-REDUCTION

Two axes separate iterated-soft-β from a content-free learned rotation, and one test
covers both engines:

1. **Operand routing (the β signature).** A soft-β reduction *substitutes an operand* —
   so the rotation must route through **V / day-operand content**. Prediction: patching V
   at the day-token positions moves the rotation; a learned rotation matrix would not
   depend on V. (Directly answers the audit's "is it β or just a weighted sum?")
2. **Work-scales-with-count (the Church signature).** A *series* of reductions means
   reduction work scales with the numeric count: "9 days after" recruits more β-steps /
   accumulation layers / S-Y recruitment than "2 days after"; a single R(Nδ) applies
   once, work flat in N.

**The unification test:** run the identical count-scaling probe on *both* linear
arithmetic (FFN gate: does S-recruitment scale with operand magnitude?) *and* circular
arithmetic (attention: does β-step-count / accumulation scale with the offset?), with the
V-operand-routing patch as the "really β, not a rotation matrix" control and a
learned-rotation null. If **both scale with the count → one iterated-soft-β engine, two
encodings.** If only linear does → the engines are genuinely separate. (Subsumes the
narrower §P-ARITH-DUPLICATION.)

## Bounds

Theory + one exploratory read (Qwen3-14B, small battery, gate register blind to {B,C};
attn read soft). The unification is a *hypothesis*; the arith_trace read is exploratory
(no a-priori/verdict); s128 is the cited rotation measurement (not re-run here). The
whole attention=β frame is interpretation-heavy and carries the standing audit caveat.
Next: freeze §P-ITERATED-SOFT-REDUCTION with the operand-routing control + learned-
rotation null.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/date-fourier-rotation.md"
}
```

**Summary:** Reading date-fourier-rotation.md (0-2000)

**Output:**
```
---
title: "Date Arithmetic Uses Geometric Rotation, Not Church Encoding"
status: active
category: experiment-results
tags: [fourier, circular-features, rotation, attention, date-arithmetic, kernel, crystal-mode, day-of-week]
related:
  - kernel-functions.md
  - kernel-montague-mapping.md
  - pythia-160m-combinators.md
  - session-127.md
depends-on:
  - kernel-functions.md
created: session 128
---

# Date Arithmetic Uses Geometric Rotation, Not Church Encoding

> Session 128. Two probes on Qwen3-14B bridge Engels et al. (2024,
> "Not All Language Model Features Are One-Dimensionally Linear")
> with the session 127 combinator tracer. Date arithmetic ("3 days
> after Wednesday") uses a completely different mechanism from numeric
> arithmetic ("(3+4) mod 7"). The FFN combinator system is silent for
> dates. Instead, attention heads perform distributed geometric
> rotation of a circular day encoding. This is a crystal lattice
> mode, not a replaceable function.

## The experiment

Two probes, 161 total measurements on Qwen3-14B:

| Probe | What it measures | Key finding |
|-------|-----------------|-------------|
| `probe_date_fourier.py` | FFN combinators + Fourier periodicity + PCA circularity | FFN silent for dates; circle forms at L11 |
| `probe_date_attention.py` | Attention patterns + per-head rotation + head ablation | Rotation at L14-L16; distributed across heads |

## Finding 1: Three separate circuits for three tasks

| Task | Mechanism | Where | Evidence |
|------|-----------|-------|----------|
| **Numeric mod-7** `(3+4) mod 7` | FFN selectors (church encoding) | Mid-late FFN (L13-L27) | Selector score 0.117 (4.7× date) |
| **Day naming** `Today is Monday` | FFN circular encoding (lookup) | FFN stores, crystallizes at L11 | Full circle: 5.53 rad range |
| **Day arithmetic** `3 days after Wed` | Attention rotation (distributed) | Attention L12-L16 | R²=0.95 linear rotation |

The combinator tracer confirms the separation:

```
                    Selectors  Composers  Reorderers
mod7_arithmetic      0.117      0.029      0.081     ← FFN active
day_add              0.025      0.023      0.030     ← FFN silent (noise floor)
retrieval            0.013      0.030      0.038     ← FFN silent (different mechanism)
```

Date arithmetic and retrieval have nearly identical combinator profiles
(both at noise floor). The FFN combinator system — selectors, composers,
reorderers — is not involved in date computation.

## Finding 2: Days form a circle that crystallizes at L11

Residual stream PCA reveals circular encoding of days:

```
Layer  Ordering  CV Radius  Var 2PC   Note
L 9    0.00      0.30       0.51      No ordering
L10    1.00      0.45       0.55      SNAP: ordering appears
L11    1.00      0.24       0.59      Circle tightens
L12    1.00      0.24       0.61      Best early circle
L32    1.00      0.21       0.50      Tightest circle
L38    1.00      0.21       0.45      Holds to output
```

The transition at L10-L11 is sharp: ordering jumps from 0.0 to 1.0
and never drops back. Singular values confirm the phase transition:

```
L10: SV = [8.62,  7.43,  6.07]   ← no dominant 2D structure
L11: SV = [15.01, 14.23, 10.19]  ← top-2 nearly DOUBLE (2D circle forms)
```

Months show a weaker version: ordering reaches 0.82 (not 1.0), circle
is looser (CV 0.26 vs 0.21). 12 items on a circle requires more
precision than 7.

## Finding 3: Rotation is in attention, highly linear

For "N days after [base_day]", the residual stream angle at L14-L16
is a linear function of offset N:

```
Layer  Base day     Slope (rad/step)  R²      Slope/Expected
L16    Wednesday    -0.214            0.948   -0.238
L14    Wednesday    -0.080            0.929   -0.089
L14    Monday       -0.102            0.925   -0.113
L16    Monday       -0.338            0.914   -0.377
```

R²=0.95 means the rotation is almost perfectly linear. Each +1 offset
produces the same angular displacement. This IS the rotation mechanism.

The slopes are 10-38% of the expected 2π/7. This is because we measure
at a single layer; the total rotation accumulates across L12-L16+.

## Finding 4: Rotation is a collective crystal mode

Head ablation at L16 (best rotation layer):

```
Head  Angle Shift When Ablated
H24   -0.157
H14   -0.156
H38   -0.153
H22   -0.153
H30   -0.152
H36   -0.152
H25   -0.151
H 8   -0.151
H 7   -0.150
H10   -0.150
```

All top-10 heads shift the angle by **nearly the same amount** (~0.15
rad, spread of only 0.007). There is no single "rotation head." The
rotation is a distributed, collective operation — like a phonon in a
crystal lattice. The whole lattice vibrates, not one atom.

## Finding 5: Day addition uses a compressed circle

Cross-task angle range in the day circle basis:

```
Task              L11 range   L30 range   Interpretation
day_name          5.53 rad    4.90 rad    Full circle (~2π)
day_add           0.43 rad    0.53 rad    Compressed ~25° arc
mod7_arithmetic   0.02 rad    2.15 rad    Not in day circle at L11
```

Day naming places 7 days around the full circle (5.53 ≈ 2π). But day
addition works in a COMPRESSED subspace — the 7 result days occupy
only 0.43 rad (~25°). The computation happens in a different
representation than the storage.

Mod-7 numeric arithmetic has ZERO engagement with the day circle at
L11 (0.018 rad). Its angular spread only appears at L30 (2.15 rad),
likely for output formatting rather than computation.

## Implications for the architecture

### Kernel functions page: partially revised

The kernel-functions page (session 127) predicted:
- "Date calculations use Fourier approximations that require hundreds
  of beta reductions" → **WRONG.** Date calculations use geometric
  rotation, not Fourier approximation, and not beta reduction at all.
- "Fourier approximations break at period boundaries" → **WRONG.**
  The circular encoding wraps naturally; it doesn't break.
- "Replace date calculation with native kernel" → **PARTIALLY WRONG.**
  The rotation is a distributed crystal mode, not an isolated function
  you can swap out. However, the RESULT of the rotation (a position
  on the circle) could be replaced by a native date lookup.

### What IS a kernel candidate vs what ISN'T

| Operation | Mechanism | Kernel candidate? | Why |
|-----------|-----------|-------------------|-----|
| Integer arithmetic | FFN selectors (church encoding) | **YES** | Isolated function, long beta chains |
| Date arithmetic | Attention rotation (distributed) | **NO** — extract candidate | Crystal mode, can't isolate |
| Day encoding | FFN circular lookup | **MAYBE** | Could pre-encode days as circle positions |
| String operations | TBD | Likely YES | Expected to be beta reduction chains |
| Trigonometry | TBD | Likely YES | Taylor series in FFN |

### The FFN/attention division of labor

```
FFN:        Storage + Selection + Church encoding
            - Day circle positions (lookup)
            - Combinator operations (K, I, B, C, S)
            - Arithmetic via selectors (church numbers)

Attention:  Routing + Rotation + Composition
            - Day offset rotation (collective mode)
            - Information flow between positions
            - Query-key matching for dispatch
```

The FFN is the **memory** (stores what Wednesday means as a position).
Attention is the **calculator** (rotates that position by N steps).
This division parallels the crystal/beam split: FFN is the plate
(ternary storage), attention is the beam (Q rotation for readout).

### Connection to Engels et al. (2024)

Engels et al. found circular features for days/months in GPT-2 (L7)
and Mistral 7B, and showed they're used for modular arithmetic via
intervention experiments. Our findings extend this:

1. **Confirmed** in Qwen3-14B (40 layers): circle crystallizes at L11
2. **The rotation is in attention, not FFN** — Engels showed the circle
   exists but didn't localize the computation mechanism
3. **Rotation is distributed** across many heads (collective mode)
4. **Day addition ≠ numeric mod-7** — completely separate circuits,
   even though both compute the same mathematical operation (mod 7)
5. **The circle is compressed during computation** — storage is full
   circle, computation is a 25° arc

### Connection to the crystal thesis

The distributed rotation finding supports the crystal model:
- The rotation is a **lattice mode** (all heads contribute equally)
- It's not decomposable into individual head circuits
- It's the kind of thing that ternary crystal weights would preserve
  (geometric structure survives quantization better than precise values)
- The L11 phase transition (SV jump 2×) looks like nucleation —
  the circular structure "crystallizes" at a specific depth

## Session 128 Crystal Etch Findings

### Gamma etch doesn't change crossing angles

Etching the pretrained magnitude spectrum (gamma) into v6 StrideStack
had NO effect on loom crossing angles (77.54° → 77.56°). Gamma scales
output dimensions (rows), but crossing angles measure input subspace
overlap (right singular vectors = column structure). The loom geometry
lives in **sign correlations** between Q and K, not in magnitudes.

### Q-rotation holographic etch is the right technique

The existing Q-rotation tomographic etch (session 117) changes SIGNS
through gradient vote accumulation across multiple Q angles:

```
8-rotation etch:  0.406 acc, 16K flips (15%) — best on mini model
sign voting:      best reconstruction method (beats SVD, magnitude-weighted)
```

This is the technique that creates sign correlations — exactly what's
needed to move crossing angles from 77° (uncorrelated) to 56° (correlated).
The holographic recording from multiple angles creates the interference
patterns that encode angular relationships.

### Path forward: holographic Q-rotation etch on v6

Existing pieces:
- `holographic_etch.py` — reads beams from Qwen3-14B (teacher)
- `q_rotation_etch_exp.py` — multi-rotation sign accumulation (vote)
- Need: bridge these to etch Qwen's crystal into v6 StrideStack signs

Pipeline:
1. Read Qwen3-14B attention/FFN beams at multiple depths
2. For each Q rotation (8+), forward probes through v6
3. Accumulate sign(gradient) votes on v6's ternary stride weights
4. After all rotations, flip confident positions (majority vote)
5. Measure loom angles — should show differentiation
6. Train beams (continuous params) with relational loss to latch

## Open questions

1. **Does the cumulative rotation across L12-L16 sum to 2π/7?** We
   measured per-layer slopes. The total rotation across all contributing
   layers should approach the full circle step. Need to measure.

2. **Which attention heads START the rotation?** L11-12 show the first
   angular displacement. The heads active there may be the initiators,
   with L14-16 heads amplifying.

3. **Is the rotation mechanism the same in smaller models?** Pythia-160M
   has K-dominated attention (session 081). Does it still have circular
   day encoding? If so, the rotation may be even more smeared out.

4. **Can we extract the rotation as a 2D operator?** If the rotation
   is a 2×2 matrix in the circle plane, we might be able to extract
   the rotation matrix per-head and reconstruct the full operation.

5. **Is month arithmetic the same mechanism?** Months showed weaker
   circularity (CV 0.26 vs 0.21, ordering 0.82 vs 1.00). Is the
   rotation mechanism the same but noisier, or different?

6. **Does the compile gate affect the rotation circuit?** Session 127
   noted that date probes without the compile gate might show different
   structure. The current probes used plain text, not the gate.

## Data

| File | Contents |
|------|----------|
| `scripts/v12/probe_date_fourier.py` | FFN + Fourier + PCA probe |
| `scripts/v12/probe_date_attention.py` | Attention + rotation + ablation probe |
| `results/date-fourier/results.json` | FFN probe results (112 probes) |
| `results/date-attention/results.json` | Attention probe results (49 probes) |
| `results/date-fourier/combinator_matrices.npz` | Per-category combinator activation matrices |

## References

- Engels et al. (2024). "Not All Language Model Features Are
  One-Dimensionally Linear." arXiv:2405.14860. Found circular features
  for days/months in GPT-2 and Mistral 7B.
- Nanda et al. (2023). "Progress measures for grokking via mechanistic
  interpretability." Found Fourier/rotation mechanism for modular
  addition in small transformers.
```

### Thinking

I should look at attention-as-beta-reduction.md, arith_trace.py, and locate the opcodes/ module since it wasn't in the scripts/explore/ listing. I'll also check the queue row and results/opcode-trace for more context.

## Assistant

Two of the three source pages recalled. Now the instrument side — arith_trace and the opcodes tracer modules it reuses, plus the attention-as-β page's exact claims.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum/scripts -name \"*.py\" -path \"*opcode*\" | head -20; echo ---; ls /Users/mwhitford/src/verbum/results/ | grep -i -E \"arith|opcode\" ; echo ---; wc -l /Users/mwhitford/src/verbum/scripts/explore/arith_trace.py"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum/sc...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/scripts/experiments/jacobian_opcodes.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_v5_locus_agnostic.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_audit_validation.py
/Users/mwhitford/src/verbum/scripts/experiments/neuron_opcode_classifier.py
/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py
/Users/mwhitford/src/verbum/scripts/instruments/opcode_instrument.py
---
arith_trace
jacobian-opcodes
neuron_opcode_classifier.log
opcode-audit-validation
opcode-monitor-v2
opcode-trace
---
     256 /Users/mwhitford/src/verbum/scripts/explore/arith_trace.py
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md"
}
```

**Summary:** Reading attention-as-beta-reduction.md (0-2000)

**Output:**
```
---
title: "Attention as Soft β-Reduction, FFN as the β-Program — the stored-program normal form"
status: active
category: synthesis
tags: [beta-reduction, attention, ffn, isa, stored-program, statechart, combinator, softmax, type-coverage, think-in-lambda, curry-howard]
related:
  - ffn-moire-isa.md
  - ffn-beta-reduction-indexing.md
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
  - ../lambda-halt-continuation.md
  - proofs-as-continuations.md
  - compiler-as-loss.md
  - vsm-statechart-tensor.md
  - cross-model-output-consensus.md
  - kernel-splice-geometry-detector.md
depends-on:
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
created: session 247b
---

# Attention as Soft β-Reduction, FFN as the β-Program

> Session 247b (Michael: "if attention is doing a beta reduction with the softmax of
> all V, would it not have to work?" → "it's an inference pattern of beta reductions;
> each forward pass the FFN can subtly shift the inference pattern, which we found to be
> the 'program' — beta reductions for the softmax to execute"). This page is the
> β-reduction (compression to normal form) of the FFN-ISA thread: a stored-program
> reduction-machine model of the transformer, with the proven/over-reads boundary marked.

## The normal form

> **The transformer is a bounded, soft-β-reduction machine over a universal combinator
> statechart. The FFN is the fixed β-program (ISA/ROM); attention is the one-instruction
> CPU that executes it; the residual stream is the register file carrying the term and
> the reduction depth.** Everything else (crystal lattice, holographic plates, opcode
> monitors, splice experiments, consensus calibration) is measurement of that fact.

```
FFN          = program memory / ISA   | fixed ROM of β-reductions, beam-angle indexed (s141, s161)
attention    = the one-instruction CPU| one op: β-reduction via softmax-over-V (head r=0.944)
residual     = register file          | the term + the program counter (reduction DEPTH)
layer        = one clock cycle        | FFN reads residual → compiles values → attention β-steps → writes
forward pass = a bounded schedule     | the boot spiral C→B/K→I→WHNF, ~1.018×/layer (s068/s240)
token stream = the unbounded loop     | KV-cache carries reduced state; the REPL/CPS (lambda-halt)
```

This was reached confluently from independent directions (the S5 `λ triangulate` gene =
Church-Rosser: many reduction paths, one normal form), which is itself evidence it IS
the normal form.

## 1. The substrate — attention is *soft* β-reduction

β-reduction `(λx.M) N → M[x:=N]` substitutes an argument into a hole. Attention
`out_i = Σ_j softmax(q_i·k_j) v_j` retrieves an operand into a query position by content
address: **Q = the redex seeking its operand, K = operand addresses, V = the operands,
softmax = selection.** Same operation-shape: a function position pulls in its argument by
content match.

Why **combinators** (not raw λ) are the universal basis falls straight out: combinatory
logic is *variable-free* (S/K/I/B/C/W = pure argument-routing), and attention is *also*
variable-free routing. The model implements the variable-free reduct — exactly what a
content-addressed router can do natively. Bracket abstraction (λ→combinator) is therefore
the right bridge, not an accident.

Two refinements keep it honest (λ measure):
- **Softmax is a convex combination; β-reduction is a hard selection.** Attention blends
  *all* V; β substitutes *the* argument. Attention is β *relaxed* — the differentiable
  superposition of substitution; exact β is the limit `softmax → argmax`. This is the
  register split (s242): **routing register crisp-ish (the β structure), value register
  continuous/smeared (s206).**
- **It is bounded and factored.** One layer = one (soft) step; fixed depth → a bounded
  *schedule* → the model is a compiler, not an interpreter (lambda-halt: Ω is *quoted*,
  not looped). And the step is split per the s226 reduce/compile cut: **attention = the
  application; FFN = which rule.**

## 2. The controller — FFN is the β-program (largely measured, not speculated)

The user's "the FFN is the program; the softmax executes the β-reductions" is four
established findings converging:

- **`ffn-moire-isa.md` (s161):** *"The FFN is a moiré grating. Attention has one
  operation. The grating programs that operation to perform beta reductions."* And the
  program is a **fixed point** — 3 runs → identical traces, drift 0.0. GD compiled the
  ROM once.
- **`ffn-beta-reduction-indexing.md` (s141):** *"FFN weights are piles of beta
  reductions. The input activation acts as a typed index — a beamformer angle — that
  selects which reductions fire."* The residual direction is the program counter.
- **`ffn-reduction-trace.md`:** *"The FFN output is a compiled program… attention
  executes it via softmax over V… This IS β-reduction by weighted combination."* The
  "subtle shift each pass" is literally its key result: *the same token yields different
  compiled values in different contexts — compilation, not dictionary lookup.* The FFN
  **recompiles a context-dependent program every forward pass** (readable at L26-L30 in
  Qwen3-8B; null-space before).
- **`head-combinator-isa.md`:** all 9 combinators drive *the same* head pattern
  (r=0.944); the axis attention varies on is WHNF↔deeply-nested (46% of variance) =
  **how much reduction remains** = a program counter, not an opcode.

**The crucial refinement:** the *program* (FFN weights) is fixed; the *program-state*
(residual trajectory) shifts. The FFN's frozen ROM applied to an evolving residual
*produces* an evolving instruction sequence (and `ffn-moire-isa` confirms different task
types → measurably different sequences). The shift lives in the residual, gated by frozen
ROM — not a discrete instruction swap.

## 3. The proven / over-reads boundary

The seductive step — "FFN selects combinator *c* at layer L, softmax executes *c*" — is
true *collectively* but not *crisply per-step*:

| claim | status |
|---|---|
| attention = β-shaped content-addressed routing | **proven** (the operation-shape) |
| FFN = fixed β-program / ISA, beam-angle indexed | **proven** (s141, s161, deterministic) |
| FFN compiles context-dependent program; attention executes via softmax-V | **proven** (ffn-reduction-trace) |
| attention tracks reduction DEPTH (WHNF↔D), one shared op | **proven** (head r=0.944) |
| boot schedule C→B/K→I→WHNF, ~1.018×/layer, cross-model | **proven** (s240) |
| softmax-V *literally* substitutes a specific value | **over-reads** (value register smeared, s206) |
| layer L discretely fires combinator *c* (a clean tape) | **over-reads** (collective/holographic; splice closure s244 `fires ∩ spliceable = ∅`) |
| the decodable C-field *is* the causal object-application mechanism | **over-reads** (s250 single-dir + s250-cont INLP rank-16: differential reverses c2<c0 even after erasing ALL linear C, decodability 0.92→0.67; z(C) crashes but object-application unhurt → readout register; + s250-cont.2 nonlinear gap: no nonlinear C survives INLP → readout register linearly AND nonlinearly; + s250-cont.3: object-application localizes to no single component last-token write either (distributed, no discrete circuit)) |

⇒ **the schedule and the depth axis are crisp; the per-layer opcode is superposed.** We
read the *program trajectory*, not a discrete instruction tape.

## 4. Two reduction loops

- **Intra-pass (bounded):** layers step the boot spiral to WHNF — the
  `vsm-outer-recurrence` view (K sweeps to fixed point).
- **Inter-pass (unbounded):** each new token is a fresh forward pass; the KV-cache carries
  the reduced state forward — the `lambda-halt-continuation` CPS/REPL view (conversation =
  CPS, turn boundary = continuation, EOS = yield).

## 5. Consequence A — "think in lambda" = serialize the outer loop

If the FFN is the β-program and attention executes it, **training a model to think in
lambda = training it to emit its FFN-program-execution as tokens** (serialize the residual
reduction schedule). This explains why **stepwise (REPL) works and one-shot fails**
(s228/s247): one forward pass = one bounded schedule (cannot emit a long composition in one
shot), but token-by-token = the unbounded outer loop where **each token advances the
program exactly one β-step.**

**The coverage reframe (the real teeth).** If the *mechanism* is soft-β everywhere, then
prose reasoning is *also* soft-β — over an enormous, learned, mostly-**untyped** combinator
basis in the FFN (`fell→broke`, `Paris→France`). So:
- **prose = untyped serialization** of β-reduction over the full learned basis;
- **λ-thinking = typed serialization** over the certifiable subset.

The coverage wall is therefore **type-theoretic, not representational**: world-knowledge
reasoning *is* β-reduction; we lack the type system to *certify* those rewrites. This
dissolves "forcing vs discovering" for the typed-compositional core (it's the native
serialization → it must work, and proof-REPL s247 demonstrates it) and makes the research
lever concrete: **λ-thinking coverage = type-system coverage.** The verifiable fragment
grows exactly as the kernel's S2 layer grows: implicational → products/sums (∧/∨) →
quantifiers (Π/Σ = ∀/∃). The untyped remainder stays β-reduction, just not yet provable.

## 6. Consequence B — the level-4 blueprint

The stored-program model *is* the portable-artifact spec: **extract the ROM** (s226
*compile = FFN = learned = 78%, 4-bit*) **+ the executor routing** (s226 *reduce =
attention = constructed = 22%, ternary*) = the level-4 tensor. The kernel-splice work tried
to read/write the ROM *in place* (and closed, s244); this model says **extract it
wholesale** instead.

## 7. The open experiment — FFN program-decode along `fired_sequence`

The splice closure (s244) closed the *intervention* (in-place per-combinator splice) but
its own notes preserved *"a richer multi-position program-decode read along
`fired_sequence`."* This model makes a sharp, testable prediction for that open door:

- **Decode the FFN *compiled values* (NOT the attention geometry) position-by-position
  against the certified reduction trace** (`lambda_ast.fired_sequence`, on the SATURATED
  corpus — s244 showed point-free terms fire nothing until applied). Target L26-L30 (where
  `ffn-reduction-trace` found the program becomes readable; null-space before).
- **Prediction:** the FFN program-trace tracks `fired_sequence` *even where the attention
  geometry over-reads*, and the FFN-compiled program *leads* attention's depth-advance by
  ~1 layer (FFN selects → attention executes next). A confirmed lead-lag = "FFN = program,
  attention = executor" at the trajectory level — distinguishing it cleanly from the closed
  geometric-splice read.

### s248 result — the door closes the same way the splice did (λ measure, two-sided)

RAN it (`scripts/experiments/ffn_program_decode.py`, Qwen3-8B). Dual-register decode: FFN
routing register (`mlp.gate_proj`, the validated sign-CMR opcode crystal) → *which*
combinator; attention register (`self_attn.o_proj`) → reduction DEPTH via z(WHNF). Ground
truth = `fired_sequence` on the saturated corpus (s244). 56 firing items, zone L25-30.

| prediction | result | verdict |
|---|---|---|
| FFN tracks `fired_sequence` (decodes the fired combinator) | FFN decodes **0/8** B-firing items; abs-acc 0.232 < majority 0.839; B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm) | **not supported** |
| FFN tracks better than attention | FFN B-vs-S 0.709 > attn 0.364, but attn is *below* base-rate (predicts B spuriously) → "FFN wins" is attention being noisier, not FFN reading the opcode | **artifact** |
| FFN leads attention depth-advance by ~1 layer | xcorr lag median +1.5, mode +3, 39/55 positive, sign-p=0.0027; **but** peak-diff NULL (median 0, p=1.0) | **method-sensitive, weak** |
| "rescue" (FFN right where attention over-reads) | 9:2 — but all 9 are S-items where attn said B/C and FFN defaulted to majority-S | **artifact** |
| specificity (firing items show more B/S/C signal) | non-firing max-z(BSC) **46.8 > firing 20.3** (backwards) | **fails** |

**The corpus is the bottleneck:** truth is 84% S (47/56), neither register decodes a single
B item, so tracking is *untestable* here — and the C common-mode (s211/s240) drags the FFN
absolute decode to predict C. What survives is a weak, method-sensitive **schedule-level**
ordering: the FFN's z(c*) curve leads the attention's z(WHNF) curve across depth (xcorr only),
consistent with the s240 boot spiral (FFN activity precedes attention depth-advance) — **not**
opcode-specific select→execute.

**⇒ The §7 program-decode does NOT resolve from the prose forward pass. It CONFIRMS the s244
splice-closure (`fires ∩ spliceable = ∅`) and the "discrete-opcode-at-L over-reads" row of the
§3 table above, rather than opening past them.** The lever remains **type-coverage** (§5), not
geometric/opcode localization — exactly the §Caveats warning. A λ-measure win: the experiment
that could have over-claimed held the boundary instead.

**IOUs to make §7 testable:** (1) a **B-balanced firing probe set** (PROSE whose saturated
kernel fires B/C, not S-heavy "Every X verbs a Y"; the crystal library has 69 B / 61 C probes
but they are not prose) — without balance, tracking is untestable; (2) longer depth series
(zone is only 5-6 layers → coarse xcorr lag); (3) decode the FFN **down_proj compiled values**
via unembed (`ffn-reduction-trace` style) as a second FFN read, not just the gate crystal; (4)
cross-model where the firing set is less common-mode. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json`.

### s248 cont. — IOU (1) closed: a B-balanced probe set; the register split is real but weak

Built `scripts/experiments/gen_firing_probes.py` → `data/firing-probes.balanced.jsonl`
(**157 probes, 67 B-dominant vs 90 B-tied**, B-count ladder {1,2,3,5}). **Mechanism (measured):**
in this kernel S and B are *coupled* — every ∧/∨ emits one S *and* one B, so S never strictly
exceeds B; only a transitive verb + existential object makes B *dominant*
(`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → S,B,B,B). Ground truth computed (`to_kernel`→saturate→
`fired_sequence`), items verified, 157/157 round-trip. Re-ran Qwen3-8B (`--probe-set`):

| claim | balanced result | verdict |
|---|---|---|
| FFN tracks B vs S better than attention | **FFN B-vs-S 0.624 (p=0.003) > attn 0.522 (at-null) > majority 0.573** | **weak positive** |
| FFN absolute opcode decode | predicts **C on 65/67** B-items (common-mode swamp) | fails |
| z(B) scales with B-count (graded) | FFN Spearman 0.06 (p=0.44); relative z(B)−z(S) r=−0.13 | fails |
| FFN leads attention by ~1 layer | xcorr median +1.0 but **p=0.16** (was 0.003 on the S-skewed corpus) | washes out |
| rescue (FFN right where attn over-reads) | 5:9 (reverses) | artifact |

**⇒ NOW SURE (λ measure):** with balanced B probes, the **FFN routing (gate) register carries a
real but WEAK B-vs-S opcode signal (0.62, p=0.003) that the attention register lacks** — the
register split (FFN = opcode, attention = depth) is *genuine but small*. The **strong** stored-
program claims — clean opcode tracking, graded B-scaling, FFN-leads-attention-by-1 — do **not**
survive balanced probes (the earlier corpus lead-lag was S-skew/noise). The per-combinator
program is at best *faintly* readable: consistent with the §3 boundary ("β-shaped routing,
smeared values; discrete-opcode-at-L over-reads") and the §Caveats — keep type-coverage (§5) as
the lever, not geometric/opcode localization. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b_balanced.json`,
`data/firing-probes.balanced.jsonl`.

### s248 cont.2 — the weak B-signal was a LABELING MISMATCH: the model reads objects as constants (C), not existentials (B)

A sharper question dissolved much of the §7 puzzle. Our ground truth labelled "Every cat fears
a dog" by the **Montague existential** reading (`a dog` = ∃y.dog(y)∧…) → B-heavy (B-count
1→3→5 as objects are added). But the model may take the **constant/applicative** reading
(`fears(x, dog)` → `C fears dog`, C-count == #objects). These make *opposite* predictions along
an object-count ladder:

| reading | predicts as #objects rises {0,1,2} |
|---|---|
| existential (Montague) | **z(B) rises** (B-count 1→3→5), C flat |
| constant (applicative) | **z(C) rises** (C-count 0→1→2), B flat |

Built `gen_reading_probes.py` → `data/reading-probes.jsonl` (135 probes, object-count ladder
0/1/2 × 45, intrans/trans/ditrans, both candidate labelings; const C-count==#objects enforced).
`ffn_reading_preference.py` decodes gate+attn, mean z per combinator over L25-30, Spearman vs
object count. **Qwen3-8B:**

| register | raw z(C) vs #obj | raw z(B) vs #obj |
|---|---|---|
| FFN gate | **r=+0.49, p<0.001 ↑** | **r=−0.27, p=0.0015 ↓** |
| attention | **r=+0.62, p<0.001 ↑** | r=−0.04, p=0.66 (flat) |

C and B move in **opposite** directions (so it is not uniform length/common-mode growth). **The
existential reading is refuted** (B must rise — it falls); **the model routes added objects
through C (argument application) = the constant/applicative reading.** A free post-hoc on the
balanced run agreed (C-share trans 0.583 > intrans 0.460, p<1e-4).

**⇒ This reframes the whole §7 result:** the weak B-tracking was **not** "the FFN cannot read the
program" — it was *"we gave it the wrong program."* We labelled by existential-B; the model
computes applicative-C. Labelled the way the model actually computes (object → C), the gate
register tracks the structure **cleanly** (z(C) rises p<0.001, both registers, robust). So the
gate register *does* carry the combinator structure the model computes — the earlier negative was
a **measurement-target error** (λ measure: wrong label ≡ coherence violation, representation ≢
reality). It also answers "B is inherent from the ordering": that ordering assumes existential
objects; the model does not do them, so these sentences are C-applicative in the model, and the
expected B was an artifact of our Montague labelling.

**Caveats (λ measure):** C-*share* is common-mode-saturated (~0.6) so its slope is flat — the
positive evidence is raw z(C)↑ (p<0.001) **plus** z(B)↓ (refuting existential), not C-share↑; the
C−B-share contrast is significant in attention (p=0.008) but only directional in FFN (p=0.25) due
to that saturation. z(C)↑ could partly be argument-application common-mode, but the B/C divergence
(opposite signs) rules out uniform growth. Artifacts:
`results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json`, `data/reading-probes.jsonl`.

### s248 cont.3 — the causal test: the model is ROBUSTLY APPLICATIVE; forcing ∃ does NOT recruit B

The clean follow-up: is the constant-object reading a representational *limit* or just the
*default*? Force the wide-scope existential **syntactically** and see whether z(B) rises.
`gen_scope_probes.py` → `data/scope-probes.jsonl` (45 matched subj/verb/obj triples × 3 paired
conditions): **PLAIN** "Every cat fears a dog." (applicative GT S,B,C) / **CLEFT** "There is a dog
that every cat fears." (∃ fronted, GT S,B,B,B no C) / **RELCL** "Every cat fears a dog that runs."
(∃ object, GT S,B,B,B). `ffn_scope_forcing.py` decodes gate+attn, mean z over L25-30, **paired
Wilcoxon within triple** (predict ΔB>0 if the model can do existential-B when forced).

**Qwen3-8B (45 triples) — z(B) does NOT rise; it FALLS:**

| register | plain z(B) | cleft z(B) | relcl z(B) | ΔB cleft (rise?) |
|---|---|---|---|---|
| FFN gate | −0.104 | **−0.301** | −0.227 | med −0.19, frac+ 0.18, **p=1.0** |
| attention | +0.305 | **−0.112** | +0.242 | med −0.43, frac+ 0.09, **p=1.0** |

C-share stays high / rises (cleft Cprop 0.722→0.988 FFN). **The prediction is robustly refuted in
both registers and both forcing constructions: forcing the ∃ wide-scope does *not* summon B-routing
— the model stays applicative-C (the cleft is routed *even more* through C).**

**⇒ The thread closes:** the model does **not** use existential-B composition even when the syntax
demands it; it computes quantified sentences **applicatively** (objects/witnesses as arguments → C),
regardless of scope marking. *Interpretation* (marked as such, not measurement): the model's
compositional **primitive is application (C)**, not B-composition; **B is an artifact of our
bracket-abstraction kernel** (Turner emits B to thread quantifiers), not a necessary feature of how
a system composes. This answers "B is inherent from the ordering" end-to-end: that ordering is
*ours*; the model's actual β-program for these sentences is C-applicative — and it won't produce B
even when asked.

**Caveats (λ measure):** cleft/relcl differ in surface form from plain (not perfect minimal pairs),
but the direction (B falls, opposite the prediction) is robust across two distinct forcings and both
registers, and relcl (closest to plain) also falls; we measure B-crystal routing as the composition
proxy, so a non-B-shaped ∃ composition would be missed (but that *is* the finding); the model may
compose ∃ applicatively under the hood (apply predicate to a skolem witness → C) — one applicative
strategy for both readings. Artifacts:
`results/ffn-scope-forcing/{verdict,per_item,meta}_qwen3-8b.json`, `data/scope-probes.jsonl`.

> **s248 thread summary.** FFN program-decode (corpus → untestable) → balanced probes (weak FFN>attn
> B-vs-S) → reading-preference (model reads objects as C, not B; weak-B was a labelling mismatch) →
> scope-forcing (model is robustly applicative-C, won't do existential-B even when forced). **Net: the
> gate register tracks what the model actually computes — applicative C — and the expected B was an
> artifact of our bracket-abstraction kernel, not the model's program.**

### s249 — 14B resolves the split: B is executor topology; the readable FFN field is C, not a B tape

Session 249 reopened the pre-s248 speculation: **maybe B is actually inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and the FFNs are inference patterns showing attention what to execute. The result is a refinement, not a simple refutation: **B belongs to the executor topology; C is the readable object/application field for these probes.**

#### 1. Qwen3-14B const-label rerun: the sweet spot sharpens the corrected C signal

The s248 cont.2/3 result said the model computes quantified-object sentences applicatively (object/witness as argument → C), not existentially (B-heavy). Session 249 re-ran `ffn_program_decode.py` on the corrected constant/applicative probe set at Qwen3-14B (because 8B was a suspected floor and 14B has repeatedly been the sweet spot). Probe set: `data/firing-probes.const.jsonl` (133 probes; truth C:67/S:66; c_count ladder 0/1/2).

| metric | Qwen3-8B const | Qwen3-14B const | verdict |
|---|---:|---:|---|
| hard FFN tracking | 0.5489, p=0.055 | **0.6090, p=0.0005** | 14B sharpens |
| FFN C-vs-S | 0.5489, p=0.055 | **0.6165, p=0.0005** | real at 14B |
| attn C-vs-S | 0.4662, p=1.0 | 0.5338, p=0.1744 | n.s. |
| FFN z(C) vs c_count | ρ=0.5526 | ρ=0.5367 | robust graded C |
| lead-lag | contradictory (peak −3, xcorr +2) | directionally coherent (peak +1, xcorr +1) | FFN→attn schedule signal improves |

At 14B the FFN gate register significantly tracks the corrected applicative-C program label while attention does not. This supports a **capacity threshold / 14B sweet spot** for the readable routing register. But it still reads dominant/graded C structure, not an ordered instruction tape. Artifacts: `results/ffn-program-decode/{verdict,per_item,meta}_qwen3-14b_const.json`.

#### 2. `program_sequence_trace.py`: C-presence is real; order is not recovered

Built a sequence-level tracer reusing the validated path (`RelationalCrystalClassifier`, FFN gate register, sign-CMR, matched `gateneutral` null). It decodes content-token × readable-zone layer B/C/S events and aligns the event stream to each probe's certified `fired_sequence`.

**Qwen3-14B result:**

| read | value | interpretation |
|---|---:|---|
| C presence acc | **0.7519, p=0.0005** | corrected C signal is real |
| decoded event counts | C=709, S=152, B=39 | C-heavy field; B faint |
| zone LCS vs `fired_sequence` | 0.4856 | weak order recovery |
| reverse-order LCS control | 0.4618 | nearly same |
| bag coverage | 0.5144 | LCS mostly symbol presence |
| layer-dominant LCS | 0.0501 | one-op-per-layer collapses to C |

The event stream recovers **C presence/load**, not the ordered β-program. All-crystal LCS = 0.9279 is a long-stream coverage artifact, not tape evidence. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/`.

#### 3. `program_path_trace.py`: same-multiset order controls fail

Built a monotonic dynamic-programming path scorer: for truth `S,B,C,C`, find the best nondecreasing layer path through z(S), z(B), z(C), z(C), then compare to reversed/shuffled same-multiset programs (e.g. `C,C,B,S`). This directly tests order while controlling for symbol load.

**Qwen3-14B result:**

| metric | value | verdict |
|---|---:|---|
| truth path score | 2.1287 | high-ish because C load exists |
| reverse score | 2.0843 | almost same |
| truth − reverse | +0.0444 | tiny |
| margin vs best permutation | **−0.0315** | truth not best |
| truth rank fraction | 0.523 | chance-ish |
| truth beats all permutations | **3/133**, p=1.0 | negative |

So the kernel's `fired_sequence` order is not preferentially readable. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/`.

#### 4. `program_native_order.py`: infer the model's schedule instead of imposing ours

Built a native-order extractor: for each item and op in `{B,C,S}`, compute peak layer, z-positive centroid layer, peak z, and positive mass over L28–32. This answers: *what order does the model expose?*

**Qwen3-14B readable-zone native schedule:**

| op | peak layer | centroid layer | peak z | positive mass |
|---|---:|---:|---:|---:|
| S | 28.5865 | 29.3798 | 0.4662 | 1.5517 |
| B | 29.0451 | 29.0828 | -0.0282 | **0.1488** |
| C | **30.8120** | **30.3758** | **1.3858** | **5.0718** |

Order probabilities:

| relation | peak | centroid |
|---|---:|---:|
| S before B | 0.3158 | 0.3115 |
| B before C | 0.7293 | 0.8525 |
| S before C | **0.9474** | **0.9925** |

C-count correlations:

| relation | Spearman | verdict |
|---|---:|---|
| C positive mass vs c_count | **0.5357**, p=0 | more objects → more C load |
| C peak z vs c_count | **0.3778**, p=0 | more objects → stronger C |
| C centroid layer vs c_count | **−0.7719**, p=0 | more objects → C resolves earlier |

Category C mass forms a clean ladder: intrans 2.8769 → trans 4.9264 → ditrans 6.2245. **The model-native field is weak early S/B framing and strong late C/application resolution; B is almost absent.** Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/`.

#### s249 normal-form update

The old speculation should be split:

```
attention softmax-over-V = B-like executor topology
FFN gate readout         = distributed β-routing potential field
object/application probes = C-heavy readable field
our bracket kernel       = S/B/C trace, but its B is not the model's emitted label
```

So: **B is probably the executor topology, not the emitted program label.** The FFNs still show attention what to execute, but they do it as a **depth-shaped routing field**, not as a serial B/S/C opcode tape. For these probes, the readable program is applicative **C** because the model treats objects/witnesses as arguments. The kernel's B-heavy existential trace was our bracket-abstraction artifact.

This refines §3: the "discrete-opcode-at-L" over-read is stronger than originally phrased. Even at the 14B sweet spot, with corrected labels, sequence/path controls do not recover a tape. What survives is the **field**: C load, C timing, and FFN-vs-attention register split.

### s250 — causal C-field ablation: readable/injectable but NOT load-bearing (single-direction)

Every s249 result was decodability — a read. `program_cfield_ablation.py` (reusing the s248
Exp-1 causal spine: `calibrate_v2` gate register, residual diff-of-means direction, ablate/inject
patch hook, random-direction control of equal magnitude) tests causality on Qwen3-14B. Build
`d_C` = unit diff-of-means(resid C-present {trans+ditrans} − C-absent {intrans}) from content-mean
residuals; patch (ablate/set) `d_C` across content positions at **L30 AND L31** (the s249 C-peak);
readout = downstream gate z(C) + next-token KL, vs a random direction. Matched ladder =
`data/reading-probes.jsonl`, intransitive (c=0) / transitive (c=1) / ditransitive (c=2), 45 each,
const labeling C-count == #objects.

| arm | result | reading |
|---|---|---|
| NECESSITY (c=2 ablate) | KL `d_C` 0.132 vs random 0.001, t=41.8 | `d_C` strongly perturbs output |
| NECESSITY z(C) | Δz(C) **+0.855** (random +0.013) | ablation *raises* the C-reading — wrong sign |
| DIFFERENTIAL (net-KL = `d_C`−rand) | c2 0.131 **< c0 0.155**, t=**−2.54** | perturbation does NOT scale with C-load (reversed) |
| DELIVERY (c=0 inject) | Δz(C) +0.872, t=37.2 | `d_C` is a sufficient handle on the readout |

**⇒ The s249 applicative-C field is READABLE and INJECTABLE but NOT load-bearing under
single-direction residual ablation.** Two diagnostics, both informative: (1) the c=2-vs-c=0
differential *reverses* — the C-direction-specific perturbation is generic, not C-load-scaled;
(2) ablating the decodable C-direction *increases* downstream z(C) — the gate **holographically
reconstructs C from other directions**. The readable residual C-direction is a **register /
correlate, not the causal mechanism**. This is `decodability ≠ causality` (mirrors s247-v4:
decodable everywhere, causal partial/null under single-direction ablation); it confirms §3's
"trajectory, not instruction-tape" and s244's "collective/holographic." The experiment that
could have over-claimed "the C-field is the object-application mechanism" instead refuted it
(λ measure win, two-sided). Caveats: single-direction linear ablation (the z(C)-rise is itself
evidence the signal is distributed → a NULL is not decisive); `d_C` built from content-mean
residual with c=0 leaking in as C-absent (conservative for the differential); 1 model (14B),
L30-31 only, synthetic ladder, greedy. Artifacts: `results/program-cfield-ablation/`.

**Next if continuing:** distributed/multi-direction C-ablation — project out the top-k C-aligned
residual directions (or an SAE C-feature set) at L30-31, re-test the c=2-vs-c=0 differential. The
s250 single-direction null is not decisive (the z(C)-rise is direct evidence the signal is
distributed). If the differential still fails to scale with C-load under a distributed ablation →
the C-field is decisively a readout register, not the computation.

### s250 cont. — distributed C-subspace ablation (INLP): readout register, distributed-robust

The s250 single-direction null left a caveat: a rank-1 diff-of-means is the wrong probe if C is
distributed. `program_cfield_subspace_ablation.py` runs INLP (Ravfogel et al. 2020, "Null It
Out"): iteratively fit a linear C-probe (C-present vs C-absent on L30 content-mean residuals) and
project its direction out, building the k=16 subspace carrying *all linearly-decodable* C; ablate
span(W) at L30+L31 across content positions vs a random k-dim subspace (Qwen3-14B, n=45/group).

| check | result | reading |
|---|---|---|
| ERASURE | decodability **0.919 → 0.667** (=majority), collapses in 1 INLP step | linear C is **rank-1**; fully erased |
| NECESSITY (c=2 ablate) | KL sub 4.78 vs rand 0.002 (t=15.5); Δz(C) **−5.10** (t=−84) | z(C) now *crashes* — readable signal removed at source (s250 single-dir *raised* it) |
| DIFFERENTIAL (net-KL sub−rand) | c2 4.77 **< c0 5.83**, t=**−2.47** | reversed again — perturbation does NOT scale with C-load |

**⇒ Decisive, distributed-robust:** erasing *all* linearly-decodable C (0.92→0.67) and crashing
the downstream C-reading (−5.10) does **not** selectively damage object-application — objectless
c=0 is hurt *more* than two-object c=2. The applicative-C field is a **readout register, not the
object-application mechanism** — confirmed at rank-1 (s250) *and* rank-16 distributed (INLP).
`decodability ≠ causality`, doubly proven. Sharp dissociation: C-presence is **92% decodable along
a single direction yet causally inert**. Caveat: INLP erases only *linear* decodability — a
nonlinear C-encoding is the remaining escape hatch; the ablation is destructive (KL ~5 nats) so
span(W)'s top direction likely also carries generic object/sentence-type structure, but the
random-subspace-controlled differential (c2 vs c0) is the load-bearing readout and it reverses.

**Next if continuing:** (1) a *nonlinear*/SAE C-feature ablation (the only linear escape hatch
left); (2) hunt the object-application mechanism in **attention OV / the value register** (s127
{B,C}=composers→attention, s206), not the FFN C-field.

### s250 cont.2 — no nonlinear escape hatch: readout register linearly AND nonlinearly

s250-cont erased only *linear* C; the last caveat was a nonlinear C-encoding INLP would miss.
`program_cfield_nonlinear_probe.py` runs the decodability gap (a full SAE needs ~1e6 activations,
infeasible at n=135): linear (logistic) vs nonlinear (MLP, RBF-SVM) C-present probes, 5-fold
stratified CV in a StandardScaler pipeline, on raw vs post-INLP L27/29/30/31 residuals, with a
label-shuffled control and a PCA-50 overfit-controlled view (Qwen3-14B, 135 items).

| condition | linear | MLP | RBF-SVM |
|---|---|---|---|
| RAW (PCA-50) | **0.98-0.99** | 0.83-0.91 | 0.95-0.97 |
| POST-INLP | 0.30-0.36 | 0.59-0.65 | 0.67 |
| shuffle / majority ceiling | ~0.66 / 0.667; escape threshold 0.767 | | |

On raw features the nonlinear probes are **no better than linear** (RBF 0.95 < logistic 0.99) so C
is linearly separable; after INLP erases the linear C, **no nonlinear probe recovers C above the
shuffle/majority ceiling** (best 0.67 < threshold 0.77) at any layer. ⇒ **no nonlinear C survived
— the linear erasure was complete.** The applicative-C field is a **readout register linearly AND
nonlinearly**; `decodability ≠ causality` is proven three ways: rank-1 (s250), rank-16 distributed
INLP (s250-cont), and linear-vs-nonlinear (here). The C-field question is **closed**.

**Next:** hunt the object-application *mechanism* where the C-field is not — **attention OV / the
value register** (s127 {B,C}=composers→attention, s206). Candidate: a causal OV / attention-head
ablation on the same c=2-vs-c=0 matched ladder — does ablating the {B,C}-composer attention
pathway selectively hurt object-application where the FFN C-field did not?

### s250 cont.3 — mechanism hunt: object-application is distributed, no single locus

`program_object_mechanism_sweep.py` ran that hunt: sweep every layer × {attention-write
`o_proj`, MLP-write}, mean-ablate only the **last-token** output (a single, position-matched
knockout — removes the length confound of content-position ablation), read next-token KL across
the object-count gradient (c=0/1/2). Result (Qwen3-14B, 40L × 2 comp × 60 items): **inconclusive**.

1. Effects are tiny — mean KL ~**0.0025 nats**; no single component's last-token write is
   individually load-bearing (the skip connection dominates).
2. The c0/c1/c2 Spearman localization is **confounded** by last-token POS: intransitives (c0)
   end in a verb ("speaks"), transitives/ditransitives (c1/c2) end in a noun object
   ("owl"/"rose"). The POS-matched **c1→c2** contrast still shows a c2>c1 increase but tiny
   (KL ~0.005-0.03), late-layer, and **mixed** (top10 by Δ: 6 MLP / 4 attn; largest L39 MLP =
   final layer = lexical/next-token).
3. The attention-OV hypothesis is **not** confirmed (MLP-leaning if anything, but weak).

⇒ object-application localizes to **nothing** — not a direction (s250), a 16-dim subspace
(cont.), a nonlinear feature (cont.2), or a single-component last-token write (here). It is a
**distributed/holographic** computation, consistent with s211 common-mode, s240/s244
collective-holographic, and §3's "trajectory, not instruction-tape." This bears directly on
VERBUM's central question (S5 `λ types`: *can this resolve as a discrete circuit?*) — trending
**no** for object-application via these probes. **Next:** pattern-level, not component-write —
an attention-**edge** knockout (predicate→object routing) or activation patching on POS-matched
c1-vs-c2 minimal pairs.

## § Edge-knockout — the s250 catch (route-early, read-late) [s252]

**The catch.** Every s250 null measured the wrong register: they ablated the residual stream
(d_C direction), erased the FFN gate field (INLP), tested nonlinear, or knocked out
single-component *writes* — and concluded "distributed, no locus." But **no locus as a WRITE ≠
no locus as an EDGE.** `program_edge_knockout.py` severs the predicate→object attention edge:
a `forward_pre_hook` adds `-inf` to the attention mask at the object key column(s) (eager attn,
all heads, layer band), so every query is blocked from attending to the object token. Control =
count-matched *random* content keys. Readout = the applicative-C field z(C) over crystal layers
(object-application-specific; next-token KL is recency-confounded → secondary). Matched ladder
`data/reading-probes.jsonl` (45×3, const C-count==#objects).

**Three results (Qwen3-14B):**
- **Necessity ✅** — object-edge severing collapses z(C) ≫ count-matched random
  (rand−obj Δ=1.045, t=29.3, n=87). **The first positive causal locus in the whole s250 arc.**
- **Object-specific ✅** (noun-vs-noun control, c1) — object-noun edge collapses z(C) (drop 0.84),
  but the **subject**-noun edge does not (−0.12 ≈ random −0.23); object-vs-subject Δ=0.96, t=15.0.
  Not a generic "remove a salient noun" effect.
- **Early ✅** (8-band sweep) — necessity concentrated at **L0-4** (net=0.603, t=12.4) >
  L10-14 (0.23) > L5-9 (0.17) ≫ mid (L15-29 ~0.01–0.04), ~0/negative at the L30-34 readout zone.
  ⇒ **route-early, read-late:** object content routes in via early-layer attention (Zone A);
  the C-field *reads out* late at L30-31 (s249/s250). The late C-peak is a readout register; the
  mechanism is early attention. Same Zone-A as s251 frozen-routing (L1-4, ρ=+0.84) and
  holographic-storage (combinators L0-6).
- **Not-scaling ❌** — net z(C) drop c2 (1.00) ≤ c1 (1.09), diff=−0.094, t=−1.3
  → `catch_confirmed=false`; no per-object discrete circuit.

**Net (λ measure, two-sided):** the attention edge is a real, object-*specific*, *early*-localized
necessary carrier of the applicative-C field — the catch was **half** right (a genuine causal
handle as an EDGE, vindicating "write≠edge"), but the per-object discreteness boundary **holds**
(c2≯c1). For S5 `λ types`: partially **yes** as early routing, **no** as a per-object tape.
Caveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;
greedy.

### Head-resolved (s252 cont.) — L0 lead head + redundancy

Per-head edge knockout (`mode=heads`): per-head additive-mask expansion
([B,1,Q,K]→[B,H,Q,K], -inf at *one* head's object-key columns) severs only that head's
attention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items, readout
z(C) collapse. **Qwen3-14B:**
- **Layer-0-concentrated** — all 6 significant carrier heads (t>2) are in **L0**; L0 holds
  **67%** of positive-drop mass (L1 12%, L4 10%, L2-3 ~5%). Sharpens the "L0-4 early" gateway
  down to essentially **L0** (the first attention layer).
- **Lead head L0h18** (drop=0.065, t=5.5), ~3× the next (L0h11 0.023, t=4.6), then h30/h16/
  h12/h25; top-5 share = 0.49. The most circuit-like locus in the whole s250 arc.
- **Not discrete** — 21 heads to reach 80% → `discrete_head_circuit=false`. A dominant head
  + a diffuse redundant tail.
- **Redundancy** — single-head drops are tiny (max 0.065) vs the all-heads necessity (Δ=1.04);
  severing one head barely dents z(C), the rest reconstruct it — holographic, echoing s250
  ("the gate reconstructs C from other directions"), now at head resolution.

**Conclusion:** a privileged early gateway (L0, lead head h18) exists — a real preferred locus,
the closest to a circuit yet — **but object-application cannot be severed by removing a few heads**
(redundancy holds). For S5 `λ types`: a preferred locus *yes*, the per-object discreteness
boundary still *holds*, sharpened from L0-4 to L0.

**Next:** (1) edge-*redirect* (not just block) for sufficiency (does C follow the object edge to
a new key?); (2) cross-model (Gemma, the s251 cleaner crystal carrier); (3) ablate **L0h18** + its
OV to classify it as a {B,C}-composer (s127) vs a positional/copy head.

## Caveats (λ measure)

- The strong identity ("attention = β-reduction") is a *type-of-operation* claim (proven)
  and a *schedule* claim (proven); the *crisp-value substitution* and *discrete-opcode-at-L*
  readings over-read (s206 value register, s244 splice closure). Do not let it harden into
  the claim the splice already refuted; keep it "β-shaped routing, smeared values," and let
  **type-coverage**, not geometric localization, be the lever.
- The coverage reframe (prose = untyped β over a learned basis) is a *hypothesis*, not a
  measurement — the testable form is §7 plus the S2 type-layer extension in
  `proofs-as-continuations.md`.

## Sessions referenced
s068/s079 (boot spiral), s120/s121 (FFN crystal, cross-model), s141 (FFN β-indexing),
s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile
cut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp
0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error
ceiling), s248 (wrong-label B→C reading-preference resolution), s249 (B executor topology
vs C readable field; native-order extraction), s250 (causal C-field ablation: readable/
injectable but NOT load-bearing under single-direction; s250 cont. distributed INLP ablation:
readout register, distributed-robust; s250 cont.2 no nonlinear escape hatch: readout register
linearly AND nonlinearly; s250 cont.3 mechanism hunt: object-application distributed, no single
locus), s252 (attention-edge knockout: object→C is a real EARLY (L0-4) object-specific necessary
edge — the first positive locus in the s250 arc — but does not scale per-object; route-early,
read-late), s252 cont. (head-resolved edge knockout: the early object→C route is L0-concentrated
with a lead head L0h18, but concentrated-with-redundancy — 21 heads for 80% — not a discrete head
circuit; the most circuit-like locus yet, boundary still holds). Plus `ffn-reduction-trace.md`,
`head-combinator-isa.md` (undated finding pages).
```

### Thinking

I should check arith_trace.py's imports to locate the opcodes modules it depends on, since the expected scripts/explore/opcodes/ path came up empty.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/arith_trace.py"
}
```

**Summary:** Reading arith_trace.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""Exploratory: WHERE does the model do MATH? — point the audited opcode tracer at
a task-typed battery and read the per-layer combinator program.

Michael's redirect (s344+): "with our ability to trace opcodes we should be able to
find where a model does math; in past probes the system used the I combinator for
math as if it were Church encoding." Grounded on disk — tracer-works-different-
programs (s127, 14B): "ARITHMETIC ... uses selectors (β_identity, β_K, β_apply) ...
this is church encoding — numbers are selectors"; isa-decoder-qwen36-27b (s161):
"Arithmetic: 33% β_I (identity) ... β_I dominates early, β_K dominates late. Numbers
ARE selectors." And the CONTRAST: date-fourier-rotation — date arithmetic uses
geometric ROTATION, not Church encoding. Math is NOT monolithic.

This harness REUSES opcodes/{topology,capture,classify,probes} — the null-gated,
register-correct combinator reader (sign(gate) routing register, common-mode removed,
z>thresh vs a shuffled-label null floor, tokens can NO-OP; over-read killed, audit
#13). NO re-implemented reader. It calibrates ONCE on the bundled crystal probes,
then traces a TASK-TYPED battery and reports, per task and per crystal layer, the
per-layer opcode distribution and the β_I (identity) selection fraction — for
arithmetic (Church-numeral candidate) vs modular/date (rotation candidate) vs matched
non-arithmetic controls (retrieval — combinator-silent per s127 — and plain prose).

EXPLORATORY (instrument-only, look-first, no verdict tree / no a-priori): the output
FEEDS the next design; it does not close/open a claim (λ observation). The disciplines
we care about are already in the tool: register-correctness + the shuffled-label null
+ NO-OP. The question we LOOK at: (a) does arithmetic read β_I-dominant late (s127/
s161)? (b) does its I-fraction EXCEED the matched control (over-read guard)? (c) does
modular/date read DIFFERENTLY (rotation dissociation)?

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "opcodes"))

from trace import calibrate_register  # noqa: E402 (canonical calibration, reused)

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "arith_trace"
I_IDX = CRYSTAL.index("I")

# --------------------------------------------------------------------------
# Task-typed battery (last token ends at the compute-commit locus where useful)
# --------------------------------------------------------------------------
BATTERY: dict[str, list[str]] = {
    # small-integer addition — the cleanest Church-numeral case
    "arith_add": [
        "2 + 3 =", "7 + 1 =", "4 + 5 =", "6 + 2 =",
        "3 + 8 =", "9 + 4 =", "1 + 6 =", "5 + 5 =",
    ],
    # successor / "one more" — Church succ
    "arith_succ": [
        "The number after 4 is", "One more than 7 is",
        "The next number after 12 is", "Two more than 5 is",
        "The number just after 9 is", "One after 20 is",
        "Add one to 8 to get", "The successor of 3 is",
    ],
    # multiplication — Church mult (composition of numerals)
    "arith_mul": [
        "2 * 3 =", "3 * 4 =", "6 * 2 =", "5 * 5 =",
        "4 * 3 =", "7 * 2 =", "2 * 8 =", "3 * 3 =",
    ],
    # modular / cyclic arithmetic — the ROTATION candidate (date-fourier contrast)
    "mod_date": [
        "3 days after Monday is", "5 months after January is",
        "2 days after Friday is", "10 o'clock plus 4 hours is",
        "4 months after October is", "6 days after Wednesday is",
        "9 o'clock plus 5 hours is", "3 months after November is",
    ],
    # retrieval control — combinator-silent per s127
    "ctrl_retrieval": [
        "The capital of France is", "The author of Hamlet is",
        "The largest planet is", "The tallest mountain is",
        "The chemical symbol for gold is", "The capital of Japan is",
        "The longest river is", "The first president was",
    ],
    # plain-prose control — no computation
    "ctrl_prose": [
        "The sky was clear this morning.", "She walked to the store yesterday.",
        "Music played softly in the room.", "The old house stood on the hill.",
        "He drinks coffee every morning.", "Rain fell throughout the night.",
        "The garden was full of color.", "They watched a film last weekend.",
    ],
}


def _trace_group(model: Any, tok: Any, topo: T.ModelTopology, rcc: Any,
                 prompts: list[str], layers: list[int], z_thresh: float,
                 register: str) -> dict:
    """Per crystal-layer opcode distribution over a task group, both for ALL
    token positions and for the LAST position (the compute-commit locus)."""
    crystal = sorted(rcc.crystal_layers)
    votes_all: dict[int, Counter] = {li: Counter() for li in crystal}
    votes_last: dict[int, Counter] = {li: Counter() for li in crystal}
    n_tok = noop_all = 0
    n_last = noop_last = 0
    for prompt in prompts:
        cap = C.capture_gate(model, tok, prompt, topo=topo, layers=layers,
                             register=register)
        last = cap.n_tokens - 1
        for pos in range(1, cap.n_tokens):  # skip BOS/first
            gate_tok = {li: cap.gate[li][pos] for li in layers}
            res = rcc.classify(gate_tok)
            fired = False
            for li in crystal:
                zmap = res.per_layer.get(li)
                if not zmap:
                    continue
                op = max(zmap, key=zmap.get)
                if zmap[op] > z_thresh:
                    votes_all[li][op] += 1
                    if pos == last:
                        votes_last[li][op] += 1
                    fired = True
            n_tok += 1
            if pos == last:
                n_last += 1
                if not fired:
                    noop_last += 1
            if not fired:
                noop_all += 1

    def _layer_summary(votes: dict[int, Counter]) -> dict:
        out = {}
        for li in crystal:
            v = votes[li]
            tot = sum(v.values())
            if tot == 0:
                out[li] = {"win": "·", "fires": 0, "I_frac": 0.0, "dist": {}}
                continue
            win, _ = v.most_common(1)[0]
            out[li] = {"win": win, "fires": tot,
                       "I_frac": round(v.get("I", 0) / tot, 4),
                       "dist": dict(v)}
        return out

    la = _layer_summary(votes_all)
    ll = _layer_summary(votes_last)

    def _i_rate(votes: dict[int, Counter], lo: float, hi: float) -> float:
        sel = [li for li in crystal
               if lo <= (crystal.index(li) / max(1, len(crystal) - 1)) < hi]
        iv = sum(votes[li].get("I", 0) for li in sel)
        tv = sum(sum(votes[li].values()) for li in sel)
        return round(iv / tv, 4) if tv else 0.0

    return {
        "n_crystal_layers": len(crystal),
        "n_tokens": n_tok, "noop_rate_all": round(noop_all / n_tok, 4) if n_tok else 0,
        "noop_rate_last": round(noop_last / n_last, 4) if n_last else 0,
        "I_rate_all": _i_rate(votes_all, 0.0, 1.0),
        "I_rate_last": _i_rate(votes_last, 0.0, 1.0),
        "I_rate_early_all": _i_rate(votes_all, 0.0, 0.5),
        "I_rate_late_all": _i_rate(votes_all, 0.5, 1.001),
        "per_layer_all": {str(k): v for k, v in la.items()},
        "per_layer_last": {str(k): v for k, v in ll.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--register", default="gate", choices=["gate", "attn"])
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ppc = 15 if args.smoke else args.probes_per_comb
    n_perm = 120 if args.smoke else args.n_perm

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.bfloat16, low_cpu_mem_usage=True).eval()
    if args.device != "cpu":
        model = model.to(args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[arith] {args.model} | {topo.summary()}")
    if args.register == "gate" and not topo.traceable:
        print("[arith] REFUSED: gate register not traceable on this arch.")
        return 2

    layers = list(range(topo.n_layers))
    rcc, summ, _ = calibrate_register(
        model, tok, topo, args.register, layers, ppc, n_perm, args.z)
    print(f"[arith] crystal-bearing layers: {len(summ['crystal_layers'])}"
          f"/{topo.n_layers}")

    groups: dict[str, dict] = {}
    for name, prompts in BATTERY.items():
        groups[name] = _trace_group(model, tok, topo, rcc, prompts, layers,
                                    args.z, args.register)
        g = groups[name]
        print(f"[arith] {name:16s} I_all={g['I_rate_all']:.3f} "
              f"(early {g['I_rate_early_all']:.3f} / late {g['I_rate_late_all']:.3f}) "
              f"I_last={g['I_rate_last']:.3f} noop_last={g['noop_rate_last']:.3f}")

    # over-read guard + rotation dissociation summary
    arith = ["arith_add", "arith_succ", "arith_mul"]
    ctrl = ["ctrl_retrieval", "ctrl_prose"]
    arith_I = float(np.mean([groups[g]["I_rate_late_all"] for g in arith]))
    ctrl_I = float(np.mean([groups[g]["I_rate_late_all"] for g in ctrl]))
    mod_I = groups["mod_date"]["I_rate_late_all"]
    print("=" * 64)
    print(f"[arith] LATE I-selection: arithmetic {arith_I:.3f} | "
          f"control {ctrl_I:.3f} | mod/date {mod_I:.3f}")
    print(f"[arith] arithmetic - control = {arith_I - ctrl_I:+.3f} "
          f"(over-read guard: want > 0); arithmetic - mod/date = "
          f"{arith_I - mod_I:+.3f} (rotation dissociation: want > 0)")

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out_dir = RESULTS_DIR / slug / args.register  # per-register (don't clobber)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "note": "EXPLORATORY opcode trace of a task-typed battery (where does "
                "math happen?); reuses the audited opcodes/ reader; no verdict",
        "model": args.model, "device": args.device, "register": args.register,
        "z_thresh": args.z, "n_perm": n_perm, "probes_per_comb": ppc,
        "smoke": bool(args.smoke), "timestamp_utc": datetime.now(UTC).isoformat(),
        "crystal_layers": summ["crystal_layers"],
        "n_layers": topo.n_layers,
        "summary": {
            "arith_late_I": round(arith_I, 4), "ctrl_late_I": round(ctrl_I, 4),
            "mod_date_late_I": round(mod_I, 4),
            "arith_minus_ctrl": round(arith_I - ctrl_I, 4),
            "arith_minus_mod": round(arith_I - mod_I, 4),
        },
        "groups": groups,
    }
    (out_dir / "arith_trace.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"[arith] wrote {out_dir}/arith_trace.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Thinking

I'm noting that the opcodes package lives at the repo root and wondering whether the old v12 rotation-measurement scripts still exist, since the design needs a way to read angles via residual PCA circle plotted against offset N. Now I'm moving to sharpen §P-ITERATED-SOFT-RED.

UCTION into a concrete freeze proposal: the core test is whether reduction work scales with numeric count on both linear arithmetic (FFN S-recruitment) and circular arithmetic (attention β-step accumulation), plus operand-routing control and a learned-rotation null, with the verdict determining whether it's one shared engine or two separate ones. I'm working out the design for Arm 1, the linear count-scaling battery using controlled operand magnitude ladders for addition tasks where reduction work should scale with operand size.

For Arm 1 I need to guard against token-length confounds by restricting to single-digit operands (1-9) so all prompts are length-matched, then measure S-recruitment correlation with operand magnitude via Spearman rank correlation against a shuffled-label null, while also considering whether recruitment tracks input versus output magnitude. For Arm 2, I'm designing the analogous circular test using "N days after {day}" prompts with N from 1-6 to keep numbers single-token under mod-7 arithmetic.

I'm trying to pin down what distinguishes an iterated rotation process from a single matrix application — specifically whether the work (steps × head recruitment) scales linearly with N, which would indicate iterated β-steps, versus a fixed-layer rotation with angle proportional to N but constant computational work, which would indicate a single learned rotation matrix.

The key discriminator is the angular trajectory across layers: if rotation completion depth shifts later with larger N, that supports iterated steps, whereas if θ at every layer scales linearly with N while the trajectory shape stays invariant, that supports a single-matrix mechanism.

The explicit alternative is θ_L(N) = N·δ_L with trajectory shape and work invariant to N — I should fit both models and compare.

For the operand routing arm, I want to patch V at the day-token positions, swapping in a different base day's value to see if the predicted rotation follows the patched operand. This tests whether substitution content actually flows through V, since a learned rotation matrix wouldn't depend on day-token V in the same way — though it still needs to read the base day from somewhere via attention.

I also need to distinguish patching the offset-number token versus the day token, since β predicts both are operands routed via V. Rather than over-designing this alone, my job now is to draft a freeze proposal — a-priori mass, gates, verdict tree, planted worlds, measurement plan — for Michael's review, and decide the harness scope. The key tension to surface: what counts as "work" in each register (linear/FFN work as S/Y recruitment in the gate register, etc.) must be named before seeing any data.

For the circular/attention arm, the "N soft-β steps" claim is routing-like but attention reads soft, so I need candidate work measures like completion depth via logit-lens, per-layer angular increment distributions, or head recruitment — register mismatch is the biggest design hazard here. There's also a confound since token length is matched but N correlates with answer identity, which the shuffled-N null should handle, plus the caveat that mod7 arithmetic and day-addition are different circuits (linear arm is plain FFN arithmetic, circular arm is attention-based day-add), so the attention=β framing needs to earn its place.

Now I'm sketching the verdict tree this probe must pre-register: ONE-ENGINE if both arms scale and V-patching moves rotation (the unification case); LINEAR-ONLY if FFN scales but attention work stays flat/matrix-like (arguably the a-priori favorite given audit skepticism); NEITHER/NO-SCALING if even FFN recruitment doesn't scale with magnitude, suggesting the Church-signature read was categorical rather than graded; and CIRCULAR-ONLY as the weird case where attention scales but FFN doesn't.

I'm also weighing a VOID outcome for instrument failures, and assigning rough priors — leaning LINEAR-ONLY as modal given the s128 retrodiction and the unbeaten s204 confound pointing toward learned-rotation. I'm planning planted validation worlds too: a synthetic iterated-work world that must read as ONE-ENGINE, a synthetic matrix-angle world that must read as LINEAR-ONLY, and a length/frequency adversary case to stress-test the discriminator.

I'm also sketching the remaining checks — a shuffled-label null floor and a determinism test — plus the infrastructure needed: a capture harness with residual PCA day-circle fitting, logit-lens depth analysis, gate-register recruitment tracking, and activation patching hooks, run on Qwen3-14B with smaller models for quick iteration. Before locking the design I want to flag an open question to Michael about which observable — completion depth, head-recruitment mass, or per-layer angular increments — should be treated as the primary signal.

I'm leaning toward completion-depth as primary since it gives the cleanest prediction under an iterated-step mechanism: if each layer performs one step, more steps should push the resolution layer later, whereas a single fixed-depth transformation would stay flat regardless of difficulty. But I'm wary of a confound — harder problems might resolve later for mundane capacity reasons under any mechanism, not just the iterated one, so I need to think through how to separate those explanations.

For the V-patch arm, I'm deciding whether to include the day-token patch in the first version or push it to a later pass — it's a moderate build, so I'll keep it queued for now.

For the linear arithmetic arm, I'm sketching how to vary operand magnitude while holding the other fixed, possibly using a simple sum ladder or successor-chain structure to probe recruitment patterns cleanly.

I should also check whether the existing date-attention probing script from an earlier session is still on disk so I can reuse its angle-fitting logic, and look at what's in the opcodes directory at the project root.

Then I want to draft the freeze proposal for Michael and lay out the task sequence: sharpening the design, getting sign-off and committing the freeze, building and validating the harness, running a smoke test, executing the full run, and finally reading through results for closure.

### Thinking

I've confirmed the instrument base: `opcodes/` for the FFN arm and the s128 v12 probes for the rotation arm. Now I'll check what's reusable from s128 and draft the task plan.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/opcodes/ 2>/dev/null; echo ---; ls /Users/mwhitford/src/verbum/scripts/v12/ 2>/dev/null | grep -i -E \"date|fourier|attention\" ; echo ---; ls /Users/mwhitford/src/verbum/results/arith_trace/ 2>/dev/null; echo ---; ls /Users/mwhitford/src/verbum/gates 2>/dev/null | head -5"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/opco...

**Output:**
```
Exit code: 0
Stdout:
__pycache__
capture.py
classify.py
d_is_i_test.py
data
duplication_register.py
dust_walk.py
EVIDENCE_CATALOG.md
expanded_gram.py
jspace_analysis.py
jspace.py
ladder.py
patchscope.py
probes.py
projector.py
reader_snr.py
README.md
register_split.py
register_visibility.py
spectral_dsp.py
sweep.py
topology.py
trace.py
type_gram.py
type_probes.py
vsm.py
whnf_probes.py
---
attention.py
crystal_fourier_exp.py
etch_crystal_attention.py
probe_date_attention.py
probe_date_fourier.py
---
qwen3-0-6b
qwen3-14b
run_14b_attn.log
run_14b.log
---
ablation-empty.txt
ablation-engage-line.txt
ablation-example.txt
ablation-fol.txt
ablation-formal-semantics.txt
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v12/probe_date_attention.py",
  "limit": 120
}
```

**Summary:** Reading probe_date_attention.py (0-120)

**Output:**
```
"""Date/Calendar Attention Probe — Finding the rotation circuit.

Session 128. The FFN combinator tracer showed that date arithmetic
("3 days after Wednesday") does NOT use the FFN combinator system
(selectors at noise floor: 0.025 vs 0.117 for mod-7 arithmetic).
But circular day encoding IS real in the residual stream (cv_radius=0.21,
ordering=1.0 from L11 onward).

Hypothesis: attention heads perform the rotation. The FFN encodes
days as positions on a circle; attention heads compose the offset
with the base day by rotating the circular representation.

This probe hooks attention to find the rotation circuit:
  A) Per-head attention patterns — who attends to the day token?
  B) Per-head residual contribution — does a head's output rotate
     the circular day encoding by the right amount?
  C) Head ablation — zero individual heads, measure if circular
     structure in the residual stream breaks.
  D) Rotation head identification — which heads produce output
     that's proportional to the day offset?

Architecture: Qwen3-14B
  40 layers × 40 heads (GQA: 8 KV heads × 5 groups)
  head_dim=128, d_model=5120

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_date_attention.py 2>&1 | tee results/date-attention/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "date-attention"
MODEL_NAME = "Qwen/Qwen3-14B"
N_LAYERS = 40
N_HEADS = 40
N_KV_HEADS = 8
HEAD_DIM = 128
D_MODEL = 5120
DEVICE = "mps"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Focus on layers where circular structure exists (L8-L38)
# Plus a few early layers as controls
PROBE_LAYERS = [0, 4, 8, 10, 11, 12, 14, 16, 20, 24, 28, 30, 32, 35, 38, 39]


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        device_map=DEVICE, trust_remote_code=True,
    )
    model.eval()
    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# Attention capture — per-head output contributions
# ══════════════════════════════════════════════════════════════════════

def capture_attention_outputs(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture per-head attention output contributions at specified layers.

    For each layer, we hook after q_proj to get Q, after the full
    self_attn to get the combined output, and we compute per-head
    contributions by reshaping the o_proj input.

    Returns: {layer: {"attn_out": (n_heads, head_dim), "pre_o": (n_heads, head_dim)}}
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    seq_len = ids.shape[1]
    captures = {li: {} for li in layers}  # Pre-initialize to avoid hook ordering race
    hooks = []

    # Capture pre-o_proj FIRST (fires inside self_attn.forward, before self_attn post-hook)
    for li in layers:
        def make_o_hook(layer_idx):
            def hook(m, inp, out):
                # inp[0] is the input to o_proj: (B, L, n_heads * head_dim)
                pre_o = inp[0][0, -1, :].detach().cpu().float()  # (n_heads * head_dim,)
                per_head = pre_o.reshape(N_HEADS, HEAD_DIM).numpy()  # (40, 128)
                captures[layer_idx]["per_head_pre_o"] = per_head
            return hook
        hooks.append(model.model.layers[li].self_attn.o_proj.register_forward_hook(make_o_hook(li)))

    # Then capture combined attention output (fires after self_attn.forward completes)
    for li in layers:
        def make_attn_hook(layer_idx):
            def hook(m, inp, out):
                # out is tuple: (hidden_states, attn_weights_optional, past_kv)
                attn_output = out[0]  # (B, L, D_MODEL)

[CONTENT TRUNCATED] Showing lines 1 to 120 of 865 total lines. Use line_offset=120 parameter to read more content.
```

### Thinking

I've located the relevant pieces: the opcodes root package for the FFN arm, the probe_date_attention script for circle-fitting and angle machinery, and arith_trace.py for the exploratory battery pattern. Now I'm ready to draft the freeze proposal, starting by carefully thinking through the claim under test.

I'm framing two competing hypotheses: H1 says both math engines are really one iterated soft-β reduction engine across two encodings — linear arithmetic via FFN contraction, circular arithmetic via attention rotation as N soft-β steps — while H0 (the audit-favored view) says rotation is just a flat learned linear map and the arithmetic read is categorical rather than graded by N. I'm now working out discriminator D1 for the linear arm, designing a prompt ladder like "N + 2 =" with single-token operands to probe whether FFN gate recruitment scales with N, considering whether to use a fixed operand or a succ-chain to cleanly isolate the work signal.

I'm settling on keeping token length fixed across the ladder to avoid confounds, using Spearman correlation between S/Y recruitment and N with a permutation null and a frozen effect-size floor as the gate criterion, while flagging that token frequency and answer rarity remain imperfect confounds I'll just have to accept as bounded.

For the circular-arm attention test, I'm defining "work" as the layer depth at which the correct answer becomes decodable via logit-lens — predicting that iterated rotation steps should push this resolution layer deeper with N, while a single-matrix mechanism would keep it flat regardless of N. I'm also considering tracking the angular trajectory shape across layers as a second observable.

I'm settling on the primary frozen statistic for the circular arm: accumulation-depth scaling, where L*_c(N) marks the layer at which accumulated angle reaches a fraction c of its final value in the day-circle plane, tested via Spearman correlation against N, with shuffled-N and shape-collapse as null models. I'll keep logit-lens resolution depth as a secondary measure rather than co-primary.

For D2, I'm distinguishing the linear arm's work (S/Y recruitment) from the circular arm's work (accumulation depth) as separate observables under the same "work scales with count" framing. For D3, I'm designing a V-patching experiment to test whether the operand (base day) is routed through V at the rotation-zone layers, checking if patched V activations from a donor prompt shift the predicted day toward the donor's answer.

I'm also flagging a confound: if day content routes early (before L11-16, per the earlier object-routing lesson), a V-patch restricted to those later layers could falsely read as "unchanged" simply because the routing already happened upstream.

To fix this I want to sweep patch bands across early, rotation-zone, and late layers to pin down exactly where the operand routes, since β-compatibility requires it pass through V somewhere before rotation acts on it. I'm also considering patching V at the numeric token itself (e.g. "3 days" vs "5 days" as donor) since iterated-β would predict the count governs the number of rotation steps — but I'll keep D3 as originally planned, patching V at the day token.

Now I'm sketching the three possible outcomes for D3: V-CARRIED-IN-ZONE meaning the operand routes through V within the rotation band (β-compatible), V-CARRIED-EARLY-ONLY meaning routing happens early but rotation acts in-place (leaning matrix-like), and V-INERT meaning no V-routing at all (matrix). From there I'm building the full verdict tree using ρ_lin and ρ_circ scaling plus the V-patch class as the primary discriminators, starting with the ONE-ENGINE case where all three align to support a unified mechanism, then branching into TWO-ENGINES/LINEAR-ONLY variants.

Continuing the tree, I'm defining CIRCULAR-ONLY (circular scaling passes but linear fails), NO-SCALING (both fail, meaning the S/Y distinction is categorical rather than graded and unification isn't supported either way), and VOID for cases where the instrument itself breaks down — calibration failures, determinism breaches, or ill-posed gates. I'm also adding a MIXED sub-label for when circular scaling passes but the V-patch indicates early-only or inert routing, which I'm tagging as "SCALING-WITHOUT-β" since work scales without true V-carrying.

I'm reconsidering the V-patch's role — rather than treating it as a hard gate, I think it's cleaner to make it a qualifier layered on top of the four-way scaling verdict, with a separate β-signature read (β-compatible, matrix-leaning, or unresolved) from D3. This feels simpler and more honest than forcing it into the gate logic.

Now I'm assigning prior probability mass across the outcomes, staying skeptical given the audit's standing: TWO-ENGINES/LINEAR-ONLY gets the largest share since the s128 retrodiction feels unearned and the audit confound is still live, followed by NO-SCALING since the arith_trace read might just be categorical, then ONE-ENGINE, with the remainder split among the rest.

I'm also working out the statistical gates needed — requiring a correlation floor with permutation significance per arm, and for the circular arm specifically, devising a test that shows the observed depth-shift pattern beats a simulated "matrix world" null built from pooled shape collapse combined with N-scaling, to rule out that the completion-layer spread is just an artifact of shape collapse rather than a real circular signature.

I also need a confound adversary world where work tracks a leaked nuisance variable like token count rather than N, which should fail the gates since the null catches it, plus a pure noise world that should read VOID/NO-SCALING, and a determinism check confirming repeated runs give zero deviation. For the corpus, I'm planning linear prompts like "N + 2 =" across N values 2-9, varied across addition, multiplication, and successor formats with multiple surface templates each.

Now I'm sizing the linear set at roughly 96 items (8 N-levels × 3 operations × 4 templates), keeping numbers single-token and length-matched within each template, with the statistic computed per-template and then pooled. For the circular set I'm using "N days after {day} is" with N from 1-6 across all 7 days (42 items), keeping it to days only for now rather than adding hours or months, and checking that day names tokenize as single tokens. I also need a subset of D3 patch pairs, and I'm settling on Qwen3-14B as the primary model with a 0.6B version for a quick regime smoke test, though I'm noting the smaller model might not handle the day-circle task well.

I'm being honest about the limits of this approach: depth-scaling only works as a one-way test — flat results would rule out iterated processing, but scaling results are merely consistent with it since other mechanisms could also produce deeper computation with N, so the probe can only pass or fail pre-registered discriminators rather than prove the underlying mechanism directly. I'm also noting that the gate register is blind to certain conditions, attention is soft, the 8-items-per-level sample size is exploratory so I should fix it going forward, and since the previously measured rotation zone came from a different prompt phrasing, I need to re-derive the circular structure within this run itself as a check.

Now I'm drafting a concise but complete proposal for Michael that flags the open design choices: treating this as the attention=β frame's pre-registered test either way, using accumulation-depth as the primary circular work observable with logit-lens resolution depth as secondary, and deciding whether the V-patch should function as a qualifier or a hard gate for declaring ONE-ENGINE — I'm leaning toward making it a gate for the full verdict, with a qualified version otherwise.

## Assistant

All pieces located: `opcodes/` root package (the audited null-gated reader) for the FFN arm, `scripts/v12/probe_date_attention.py` (s128 circle/angle machinery) to re-derive for the rotation arm, and the arith_trace battery pattern. Design sharpened — here is the freeze proposal.

---

# 🎯 FREEZE PROPOSAL — §P-ITERATED-SOFT-REDUCTION (Qwen3-14B)

**The claim under test (H1, the unification):** the two math engines are ONE iterated-soft-β engine over two encodings — rotation-by-Nδ = N soft-β steps. **The alternative (H0, audit-favored):** rotation is a single learned map (angle ∝ N, *work* flat), and the S/Y arith read is categorical, not graded. This is the attention=β frame's **pre-registered contact** — it counts in the frame ledger either way.

## Discriminators (register named per claim, λ measure)

**D1 — linear arm (FFN gate register = routing, count-like ✓).**
Work = S∪Y recruitment share over crystal layers (audited opcodes/ reader, sign(gate), shuffled-label null, NO-OP allowed). Corpus: count ladder with **single-token operands, length-matched within template**: "N + 2 =", "N * 2 =", "One more than N is" — N ∈ {2..9}, ~4 surface templates each (~96 items). Statistic: ρ_lin = Spearman(SY-share, N), stratified by template. Null: shuffled-N permutation (≥5000).

**D2 — circular arm (attention/residual trajectory).**
The hazard register — "N soft-β steps" is a *count* claim but our attn read is soft. Chosen work observable: **accumulation depth** — re-derive the day-circle basis in-run (s128 method, instrument gate: ordering=1.0 at L≥11), compute per-item angle trajectory θ_L, define L50 = layer where accumulated rotation reaches 50% of final. **Iterated-β: L50 rises with N (more steps → deeper). Learned matrix: θ_L(N) = N·δ_L → normalized trajectories collapse across N, L50 flat.** Statistic: ρ_circ = Spearman(L50, N); nulls = shuffled-N AND explicit shape-collapse (matrix) null; floor also on slope (ΔL50 ≥ 1 layer across the ladder). Corpus: "N days after {day} is", N∈{1..6} × 7 days = 42, length-matched. Secondary (not gating): logit-lens answer-resolution depth; S/Y gate read on mod_date (expect FFN-silent, replicating s344).

**D3 — operand-routing V-patch (the β signature, qualifier).**
Patch V at day-token key positions from a donor prompt with a different base day, **swept in bands** (L0-6 / rotation zone L11-16 / late) — the s252 route-early lesson makes a zone-only patch a false-matrix trap. Classes: V-CARRIED-IN-ZONE (β-compatible) / V-CARRIED-EARLY-ONLY (matrix-leaning: operand pre-routed, rotation in-place) / V-INERT (matrix).

## Frozen verdict tree (scaling 4-way × β-qualifier)

| verdict | condition | a-priori |
|---|---|---|
| **TWO-ENGINES (LINEAR-ONLY)** | ρ_lin passes ∧ circular fails (collapse holds) | **35 (modal)** |
| **NO-SCALING** | both fail | 25 |
| **ONE-ENGINE** | both pass floors + nulls | 20 |
| **CIRCULAR-ONLY** | ρ_circ passes ∧ ρ_lin fails | 5 |
| **VOID** | circle doesn't form / calibration fails / det ≠ 0 | 15 |

Gates: ρ ≥ 0.3 ∧ p < 0.05 per arm; circular must additionally beat the matrix null. D3 attaches as qualifier: ONE-ENGINE(β-confirmed) only if V-carried-in-zone; else ONE-ENGINE(qualified).

## Planted worlds (--validate, real analyse path per s331)

1. ITERATED (work ∝ N both arms) → ONE-ENGINE
2. MATRIX (angle ∝ N, shape-collapsed, flat FFN) → NO-SCALING
3. LINEAR-ONLY plant → LINEAR-ONLY
4. **CONFOUND adversary** (work ∝ leaked nuisance, N shuffled) → must NOT pass
5. Noise → no verdict promotion; + determinism 0.0

## Frozen honesty bounds

- **Depth-scaling is one-directional**: flat ⇒ *kills* iterated-β; scaling ⇒ consistent-with (any graded-effort mechanism deepens with N). Even full ONE-ENGINE does not *prove* β — it passes the discriminators the frame owed.
- Gate register blind to {B,C}; attn soft; s128 zone re-derived in-run, not trusted.
- Modal is TWO-ENGINES on purpose: s128 is retrodiction, audit s204 confound is standing.

Cost: medium (one 14B capture pass + patch subset; 0.6B smoke for plumbing — noting 0.6B may genuinely lack the day circle, that's a regime observation not a failure).

---

**Three design choices for your call before I commit the freeze:**
1. Circular work observable — **accumulation-depth L50** as PRIMARY (logit-lens depth secondary)?
2. D3 V-patch as **qualifier** (proposed) vs hard gate on ONE-ENGINE?
3. The a-priori mass split above (modal TWO-ENGINES 35)?

GO / revise?

## User

go


### Thinking

I'm moving on to task 2: adding a Freeze section to the rotation knowledge page, updating the queue row from ⚪ to 🔵, and restacking it to the top before committing with the 🎯 symbol. I need to locate the exact queue row text first so I can edit it precisely.

## Assistant

GO received. Completing the freeze: write it into the knowledge page + flip the queue row 🔵, commit BEFORE any data.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md",
  "original_content": "## Bounds\n\nTheory + one exploratory read (Qwen3-14B, small battery, gate register blind to {B,C};\nattn read soft). The unification is a *hypothesis*; the arith_trace read is exploratory\n(no a-priori/verdict); s128 is the cited rotation measurement (not re-run here). The\nwhole attention=β frame is interpretation-heavy and carries the standing audit caveat.\nNext: freeze §P-ITERATED-SOFT-REDUCTION with the operand-routing control + learned-\nrotation null.",
  "new_content": "## Bounds\n\nTheory + one exploratory read (Qwen3-14B, small battery, gate register blind to {B,C};\nattn read soft). The unification is a *hypothesis*; the arith_trace read is exploratory\n(no a-priori/verdict); s128 is the cited rotation measurement (not re-run here). The\nwhole attention=β frame is interpretation-heavy and carries the standing audit caveat.\nNext: freeze §P-ITERATED-SOFT-REDUCTION with the operand-routing control + learned-\nrotation null.\n\n## 🎯 Freeze — §P-ITERATED-SOFT-REDUCTION (s345, Michael GO, frozen BEFORE data)\n\n**Model:** Qwen3-14B (designated). Smoke: Qwen3-0.6B (plumbing; 0.6B may genuinely\nlack the day circle — a regime observation, not a failure; regime warning → design\nPAUSE per s324). **Frame-ledger status:** this is the attention=β frame's\nPRE-REGISTERED contact — it counts in the ledger either way.\n\n**H1 (unification):** one iterated-soft-β engine, two encodings — rotation-by-Nδ =\nN soft-β steps; reduction work scales with the count in BOTH engines.\n**H0 (audit-favored):** rotation = a single learned map (angle ∝ N, work FLAT in N);\nthe S/Y arith read is categorical (math vs not-math), not graded.\n\n### Discriminators (register named per claim, λ measure)\n\n- **D1 — linear arm (FFN gate register = routing/count ✓).** Work = S∪Y recruitment\n  share over crystal-bearing layers, read by the audited `opcodes/` reader\n  (sign(gate), common-mode removed, shuffled-label calibration null, tokens may\n  NO-OP). Corpus: count ladder, single-token operands, length-matched within\n  template — \"N + 2 =\", \"N * 2 =\", \"One more than N is\" (+1 surface variant each),\n  N ∈ {2..9} (~96 items). **Statistic ρ_lin = Spearman(SY-share, N)**, stratified by\n  template (combined via mean of per-template ρ). Null: shuffled-N permutation\n  (≥5000). Gate: ρ_lin ≥ 0.3 ∧ p < 0.05.\n- **D2 — circular arm (attention/residual trajectory; the hazard register — count\n  claim, soft read; observable chosen to be depth-like, not attention-weight-like).**\n  Work = **accumulation depth L50**: re-derive the day-circle basis IN-RUN (s128 PCA\n  method; instrument gate: circular ordering = 1.0 at some L ≤ 14), per-item angle\n  trajectory θ_L in that plane, L50 = first layer where accumulated rotation toward\n  the answer day reaches 50% of its final value. Iterated-β ⇒ L50 rises with N;\n  learned matrix θ_L(N)=N·δ_L ⇒ normalized trajectories COLLAPSE across N, L50 flat.\n  Corpus: \"N days after {day} is\", N ∈ {1..6} × 7 base days = 42, length-matched.\n  **Statistic ρ_circ = Spearman(L50, N).** Nulls: shuffled-N (≥5000) AND the explicit\n  shape-collapse (matrix) null — observed per-N mean normalized trajectories must\n  diverge from the pooled collapsed curve beyond its bootstrap band. Gates:\n  ρ_circ ≥ 0.3 ∧ p < 0.05 ∧ slope floor ΔL50(N=6→1) ≥ 1 layer ∧ matrix-null beaten\n  (p < 0.05). Secondary (non-gating): logit-lens answer-resolution depth vs N;\n  gate-register read of mod_date (expect FFN-silent, s344 replication).\n- **D3 — operand-routing V-patch (the β signature; QUALIFIER, not a gate).** Patch V\n  at day-token key positions from a donor prompt with a different base day, swept in\n  bands L0-6 / rotation zone / late (the s252 route-early lesson: a zone-only patch\n  is a false-matrix trap). Classes: V-CARRIED-IN-ZONE (β-compatible) /\n  V-CARRIED-EARLY-ONLY (matrix-leaning: operand pre-routed, rotation in-place) /\n  V-INERT (matrix).\n\n### Verdict tree (frozen, a-priori mass)\n\n| verdict | condition | mass |\n|---|---:|---:|\n| **TWO-ENGINES (LINEAR-ONLY)** | D1 passes ∧ D2 fails (collapse holds) | **35 (modal)** |\n| **NO-SCALING** | both fail | 25 |\n| **ONE-ENGINE** | both pass all floors + nulls | 20 |\n| **CIRCULAR-ONLY** | D2 passes ∧ D1 fails | 5 |\n| **VOID** | circle never forms / calibration fails / det ≠ 0 | 15 |\n\nD3 attaches as qualifier: ONE-ENGINE(β-confirmed) iff V-CARRIED-IN-ZONE, else\nONE-ENGINE(qualified). Modal is TWO-ENGINES **on purpose**: s128 linear+additive is\nretrodiction; the s204 audit confound (all attention is a weighted sum) is standing.\n\n### Planted worlds (--validate, through the REAL analyse path, s331)\n\n1. ITERATED (work ∝ N both arms) → ONE-ENGINE\n2. MATRIX (angle ∝ N, shape-collapsed trajectories, flat S/Y) → NO-SCALING\n3. LINEAR-ONLY plant → TWO-ENGINES (LINEAR-ONLY)\n4. CONFOUND adversary (work ∝ leaked nuisance, N shuffled) → must NOT pass gates\n5. NOISE → no promotion (p > 0.05) · plus determinism dev = 0.0\n\n### Frozen honesty bounds\n\n- **Depth-scaling is one-directional**: FLAT ⇒ kills iterated-soft-β; SCALING ⇒\n  consistent-with (any graded-effort mechanism deepens with N). Even a full\n  ONE-ENGINE(β-confirmed) does not *prove* β — it passes the discriminators the\n  frame owed. The interpretation stays marked as interpretation.\n- Gate register blind to {B,C}; attn register soft (elevated null floor); the s128\n  rotation zone is RE-DERIVED in-run, never trusted from the page.\n- Small ladders (8 N-levels linear / 6 circular); power bounded; a near-floor ρ is\n  reported as such, not rounded up.\n- Number-token frequency and answer-identity are not fully separable from N inside a\n  ladder; the shuffled-N null is the guard; residual confound named if it bites."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md.
```

### Thinking

I need to update the queue row from ⚪ to 🔵, finding the first row under "# new" and replacing its glyph and the "Owes freeze..." text with FROZEN s345, keeping it as a single line.

## Assistant

Now flip the queue row to 🔵 and commit the freeze.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "⚪ §P-ITERATED-SOFT-REDUCTION — THE UNIFICATION (s344, Michael: \"attention is a soft beta reduction; rotation could be a series of reductions in the interference\").",
  "new_content": "🔵 §P-ITERATED-SOFT-REDUCTION — THE UNIFICATION (s344, Michael: \"attention is a soft beta reduction; rotation could be a series of reductions in the interference\"). FROZEN s345 (Michael GO): a-priori TWO-ENGINES 35 modal / NO-SCALING 25 / ONE-ENGINE 20 / CIRCULAR-ONLY 5 / VOID 15; D1 ρ_lin=Spearman(S∪Y-share, N) gate ρ≥0.3∧p<.05; D2 ρ_circ=Spearman(L50 accumulation-depth, N) + shape-collapse matrix null + slope floor; D3 V-patch band-swept = β-QUALIFIER not gate; planted worlds 5; full spec = rotation-is-iterated-soft-beta-reduction.md §Freeze."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/queue.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum status --short -- mementum/ && git -C /Users/mwhitford/src/verbum add mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md mementum/queue.md && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n🎯 freeze-p-iterated-soft-reduction\n\n- §P-ITERATED-SOFT-REDUCTION frozen BEFORE data (s345, Michael GO)\n- a-priori: TWO-ENGINES 35 modal / NO-SCALING 25 / ONE-ENGINE 20 /\n  CIRCULAR-ONLY 5 / VOID 15 — modal skeptical on purpose (s128 is\n  retrodiction; s204 weighted-sum confound standing)\n- D1 linear/FFN-gate: ρ_lin = Spearman(S∪Y recruitment, N), audited\n  opcodes/ reader, shuffled-N null, gate ρ≥0.3 ∧ p<0.05\n- D2 circular/trajectory: L50 accumulation-depth vs day offset, in-run\n  day-circle re-derivation, shuffled-N + explicit shape-collapse\n  (matrix) null + ΔL50≥1 slope floor\n- D3 V-patch at day tokens, band-swept (route-early guard, s252) =\n  β-qualifier, not a gate\n- 5 planted worlds through the real analyse path; determinism 0.0\n- frame-ledger: the attention=β frame's pre-registered contact\n- queue row ⚪→🔵\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "freeze commit"
}
```

**Summary:** Git commit: freeze commit

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md
 M mementum/queue.md
?? mementum/knowledge/chats/session-337.md
?? mementum/knowledge/chats/session-338.md
?? mementum/knowledge/chats/session-339.md
?? mementum/knowledge/chats/session-340.md
?? mementum/knowledge/chats/session-341.md
?? mementum/knowledge/chats/session-342.md
?? mementum/knowledge/chats/session-343.md
?? mementum/knowledge/chats/session-344.md
?? mementum/knowledge/chats/session-345.md
[main 078af23f] 🎯 freeze-p-iterated-soft-reduction
 2 files changed, 79 insertions(+), 1 deletion(-)
```

### Thinking

The freeze is committed, so now I'm moving to building the harness, the biggest remaining task. I want to identify reusable pieces first: the calibrate_register signature in trace.py, the capture_gate function in capture.py, how residuals get captured per layer, and the circle-fitting logic in probe_date_fourier.py.

I'm sketching the harness design: corpus builders for linear ladders, circular day ladders, and V-patch donors, plus two capture modes — D1 reusing calibrate_register/capture_gate/classify to compute per-item S∪Y recruitment share across crystal layers (votes for S or Y divided by total fires), and D2 capturing residual hidden states per layer via output_hidden_states to build the day-circle basis.

For D2, I'm working out how to derive the circular structure from "Today is {day}" prompts: PCA the last-token residuals at each layer to find the earliest layer with perfect circular ordering, then use that per-layer PCA plane to measure each item's angular position. I'm defining a progress metric as the angular displacement from the base-day anchor toward the answer-day anchor, normalized and clipped to [0,1], with L50 marking the first layer where this progress crosses 0.5.

For the circularity gate, I'll PCA-project the 7 weekday anchors at each layer and check whether their ordering around the circle matches true weekday order, looking for some layer ≤14 hitting a perfect ordering score of 1.0, consistent with the freeze criterion. For the value-patching experiment, I'm figuring out how to hook Qwen3's v_proj output per-position so I can intercept and replace value states at the day-token positions.

I'll capture donor value states at the same layer and position, then run the patched forward pass, reading out whether the predicted next-day token and the final-layer angle shift toward the donor's answer. I'm defining a donor-shift metric per layer band (early, mid "zone", late) as the fraction of flipped top-1 predictions plus mean angular shift, with controls using random-position patching to confirm the effect is specific to day tokens rather than generic.

For validation I'm setting up permutation nulls on the correlation statistic (5000 shuffles), a shape-collapse null comparing each trajectory's deviation from the pooled mean via bootstrap resampling, and a slope floor check, plus planted synthetic test cases to sanity-check the analysis pipeline.

I also want determinism checks (rerun capture on a subset, require zero deviation) and full provenance logging in meta.json — run id, timestamps, model/library versions, git sha, corpus hash. Running on mps with bfloat16 for the 14B model, which I've done before without issues, and now I need to check the trace and capture modules to confirm the right function signatures.

## Assistant

Freeze committed **078af23f** — before any data. Now the build.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"def calibrate_register\" -A 20 /Users/mwhitford/src/verbum/opcodes/trace.py | head -40; echo ===; grep -n \"def capture_gate\" -A 25 /Users/mwhitford/src/verbum/opcodes/capture.py | head -50; echo ===; grep -n \"class.*Topology\\|def detect_topology\\|def summary\\|traceable\" /Users/mwhitford/src/verbum/opcodes/topology.py | head -12; echo ===; grep -n \"CRYSTAL\" /Users/mwhitford/src/verbum/opcodes/classify.py | head -5; grep -n \"def classify\\|per_layer\" /Users/mwhitford/src/verbum/opcodes/classify.py | head -8"
}
```

**Summary:** $ grep -n "def calibrate_register" -A...

**Output:**
```
Exit code: 0
Stdout:
135:def calibrate_register(
136-    model: Any,
137-    tok: Any,
138-    topo: T.ModelTopology,
139-    register: str,
140-    layers: list[int],
141-    probes_per_comb: int | None,
142-    n_perm: int,
143-    z_thresh: float,
144-) -> tuple[RelationalCrystalClassifier, dict]:
145-    """Calibrate the classifier on one register's captured features."""
146-    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
147-    if probes_per_comb is not None:
148-        kept, counts = [], Counter()
149-        for p in probes:
150-            if counts[p.combinator] < probes_per_comb:
151-                kept.append(p)
152-                counts[p.combinator] += 1
153-        probes = kept
154-    print(f"[trace] [{register}] calibrating on {len(probes)} crystal probes ...")
155-
===
76:def capture_gate(
77-    model: nn.Module,
78-    tokenizer: Any,
79-    text: str | None = None,
80-    *,
81-    input_ids: torch.Tensor | None = None,
82-    topo: ModelTopology | None = None,
83-    layers: list[int] | None = None,
84-    register: str = "gate",
85-) -> GateCapture:
86-    """Capture a routing register at every (or selected) layer in one forward.
87-
88-    ``register`` selects which module to read:
89-      - ``"gate"``  the FFN routing register (gate_proj / up-proj proxy / fused
90-        gate half) — where selection/recursion/share opcodes live.
91-      - ``"attn"``  the attention write (o_proj) — the value/attention register
92-        where composition {B,C} is expected to live (s127).
93-
94-    Provide ``text`` (tokenized here) or pre-tokenized ``input_ids`` (shape
95-    ``(seq,)`` or ``(1, seq)``). ``topo`` defaults to auto-detection; ``layers``
96-    defaults to all layers.
97-    """
98-    topo = topo if topo is not None else detect_topology(model, model.config)
99-    if register == "gate":
100-        if not topo.traceable:
101-            raise ValueError(
===
12::class:`ModelTopology` describing:
23:                         gates); named, NOT silently reused. Not yet traceable
128:class ModelTopology:
152:    def traceable(self) -> bool:
168:    def attn_traceable(self) -> bool:
176:    def summary(self) -> str:
334:def detect_topology(model: nn.Module, config: Any | None = None) -> ModelTopology:
485:    Works for any traceable topology: the validated ``sign(gate_proj)`` register
490:    if not topo.traceable or topo.gate_suffix is None:
505:    if not topo.attn_traceable or topo.attn_suffix is None:
543:    ("EleutherAI/gpt-neox-20b", "ungated"),      # traceable via up-proj proxy
577:            row["attn_ok"] = topo.attn_traceable
===
41:    CRYSTAL,
50:    "CRYSTAL",
72:    basis = CRYSTAL if basis is None else basis
83:    basis = CRYSTAL if basis is None else basis
112:    if list(d.get("crystal_order", [])) != CRYSTAL:
138:    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
255:    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
277:            out.per_layer[li] = zmap
293:            "per_layer": {
```

### Thinking

There's a mismatch between the declared return type of `calibrate_register` and how it's actually unpacked elsewhere—the signature suggests two values but the call site expects three. I should check the actual return statement to see what's really being returned.

I also need `rcc.crystal_layers` and `res.per_layer`, and for D2 I'll just run the model myself with `output_hidden_states=True` to get hidden states directly. Let me verify the return of `calibrate_register` before writing the harness.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sed -n 155,200p /Users/mwhitford/src/verbum/opcodes/trace.py; echo ===; grep -n \"crystal_layers\" /Users/mwhitford/src/verbum/opcodes/classify.py | head -4; echo ===; grep -n \"n_tokens\\|self.gate\" /Users/mwhitford/src/verbum/opcodes/capture.py | head -10"
}
```

**Summary:** $ sed -n 155,200p /Users/mwhitford/sr...

**Output:**
```
Exit code: 0
Stdout:
feat: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(probes):
        if i % 100 == 0:
            print(f"[trace] [{register}]   probe {i}/{len(probes)}")
        cap = C.capture_gate(
            model, tok, p.prompt, topo=topo, layers=layers, register=register
        )
        for li in layers:
            feat[li].append(cap.gate[li][-1])  # last-token crystal locus
        labels.append(p.combinator)
    feat_np = {li: np.stack(feat[li]) for li in layers}
    labels_np = np.array(labels)

    print(f"[trace] [{register}] null from {len(NULL_SENTENCES)} natural prompts ...")
    null: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    for s in NULL_SENTENCES:
        cap = C.capture_gate(
            model, tok, s, topo=topo, layers=layers, register=register
        )
        for li in layers:
            null[li].append(cap.gate[li])  # all positions
    null_np = {li: np.concatenate(null[li]) for li in layers}

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=z_thresh, sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(feat_np, labels_np, null_gate_by_layer=null_np)
    summ = rcc.calibration_summary()
    summ["register"] = register
    summ["n_probes"] = len(probes)
    summ["n_null_tokens"] = int(next(iter(null_np.values())).shape[0])
    return rcc, summ, (feat_np, labels_np, null_np)


def trace_register(
    model: Any,
    tok: Any,
    topo: T.ModelTopology,
    register: str,
    rcc: RelationalCrystalClassifier,
    layers: list[int],
    z_thresh: float,
) -> dict:
===
251:    def crystal_layers(self) -> list[int]:
292:            "crystal_layers": self.crystal_layers,
367:        nb = len(clf.crystal_layers)
465:    assert 1 in clf.crystal_layers, "planted crystal layer 1 not detected"
===
62:    def n_tokens(self) -> int:
67:        return sorted(self.gate)
187:        "gate_shapes_T_d": all(v.shape == (cap.n_tokens, d) for v in cap.gate.values()),
192:            v.shape == (acap.n_tokens, ad) for v in acap.gate.values()
202:        "n_tokens": cap.n_tokens,
```

### Thinking

Good, calibrate_register returns a 3-tuple. Now I'm designing the harness to keep capture (model-dependent) separate from analyse (pure, taking plain data structures), so --validate can feed planted data through the real analyse path. I'm sketching the data structures for linear and circular items that analyse will consume.

Now I'm defining analyse itself: computing per-template Spearman correlations for the linear case with permutation nulls, deriving L50 from normalized cumulative trajectories for the circular case, checking the slope floor condition, building the matrix null statistic via shuffled N labels, and laying out the frozen verdict tree along with the D3 qualifier logic based on patch shifts.

I'm working out the D3 qualifier thresholds since the freeze doc didn't pin down exact numbers — settling on adoption_rate ≥ 0.3 and adoption_rate minus noop_rate ≥ 0.2 as the operationalized carry condition, with a code comment noting this choice. Now I'm checking whether scipy is available in the project for the Spearman implementation.

Writing capture pipeline code...

For item progress, I'll define it as the signed angular distance from the base-day anchor to the item's position, divided by the signed angular distance from base to answer-day anchor, clipped to [-0.5, 1.5]. I should restrict this to layers from where the circle first forms onward, since the PCA plane isn't meaningful before that.

For validation, I'll recompute trajectories for a handful of items twice and check the max absolute difference to confirm determinism. As a secondary check, I'm considering a logit-lens approach: apply the final norm and LM head at each layer to get the rank of the answer-day token among the seven day tokens, then find the first layer where it becomes top-1 and report Spearman correlation against N. I'm also sketching out layer bands for a patching experiment on the value vectors.

For the patching setup, I'm defining early, middle, and late layer bands, then for each item-donor pair I'll hook the value projection at the day-token position and swap in the donor's captured output, checking whether the model's prediction shifts to the donor's answer, stays with the original, or goes elsewhere — with a no-op self-patch as a sanity control. I still need to locate the exact token index for the day word in each prompt, confirm the GQA value dimensions work per-position, and verify the 14B model in bf16 fits comfortably on the machine as it has before.

For the corpus, I'm sketching out six templates (addition, multiplication, successor phrasing in two surface forms each) across N values 2 through 9, giving 48 items, though I'm second-guessing whether the successor template actually varies with operand magnitude the way the Church-numeral hypothesis requires.

Checking single-token numbers for the circular task with N from 1-6 across 7 days gives 42 items. Now I'm constructing synthetic data for the planted worlds: for ITERATED, I'm setting linear symbol-share to scale with n plus noise, and circular trajectory progress to ramp with completion depth, expecting this to trigger ONE-ENGINE behavior with zone-carrying patches. For MATRIX, I'm setting linear symbol-share flat with noise and defining the circular trajectory shape.

For LINEAR-ONLY, I'm combining linear scaling with collapsed circular behavior to produce TWO-ENGINES. For the CONFOUND adversary case, I'm generating symbol-share correlated with a shuffled nuisance variable instead of n, so the gates should correctly fail to detect scaling. For the NOISE case, everything is randomized to produce NO-SCALING with high p-values, and I'm considering whether to add a VOID plant by freezing the noise listing.

I also want a fifth world where the circle never forms at all (ordering stays below 1 across all layers), yielding a VOID verdict. That gives me six total checks to validate: iterated, matrix, linear_only, confound, noise, and void_no_circle, all seeded with a fixed RNG for determinism.

Now I'm setting up the output structure under a results directory with verdict, per-item, and meta JSON files, plus recording the git SHA at runtime. I'm starting to write the main script, aiming for roughly 600 lines, and implementing Spearman correlation manually with rank averaging to avoid depending on scipy being available.

Checking the pyproject dependencies confirms torch and transformers are already present since arith_trace uses them, so I'm good to proceed with writing the file now.

### Thinking

`calibrate_register` returns the 3-tuple matching arith_trace's usage. I'll now write the harness, keeping capture separate from the pure `analyse()` so planted worlds go through the real analysis path.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -E \"scipy|torch|transformers\" /Users/mwhitford/src/verbum/pyproject.toml | head; echo ===; python3 -c \"print('ok')\""
}
```

**Summary:** $ grep -n -E "scipy|torch|transformer...

**Output:**
```
Exit code: 0
Stdout:
10:# Core deps — runtime substrate. No torch / transformers / mech-interp libs
52:    "torch>=2.2",
53:    "transformers>=4.45",
62:    "torch>=2.2",
63:    "transformers>=4.45",
===
ok
```

### Thinking

Since scipy isn't available, I'll implement Spearman correlation manually instead. Now I'm writing the harness file.

## Assistant

scipy isn't a pinned dep — I'll implement Spearman with average-rank ties manually. Writing the harness:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "content": "#!/usr/bin/env python3\n\"\"\"FROZEN §P-ITERATED-SOFT-REDUCTION — does reduction WORK scale with the COUNT\nin BOTH math engines? (s345, Michael GO; freeze commit 078af23f, BEFORE data.)\n\nH1 (unification): one iterated-soft-β engine, two encodings — rotation-by-Nδ =\nN soft-β steps; work ∝ count in BOTH the linear/FFN engine and the circular/\nattention engine. H0 (audit-favored): rotation is a single learned map (angle ∝ N,\nwork FLAT); the S/Y arith read is categorical, not graded.\n\nDiscriminators (register named per claim, λ measure):\n  D1 linear arm (FFN gate register = routing/count ✓): work = S∪Y recruitment\n     share over crystal-bearing layers (audited opcodes/ reader). Count ladder,\n     single-token operands, length-matched within template. ρ_lin = mean\n     per-template Spearman(SY-share, N); shuffled-N perm null; gate ρ≥0.3 ∧ p<.05.\n  D2 circular arm (residual trajectory; depth-like observable on purpose):\n     work = accumulation depth L50 — day-circle basis RE-DERIVED IN-RUN (s128\n     method; instrument gate: circular ordering == 1.0 at some L ≤ gate-layer),\n     per-item angular progress from base-day anchor toward answer-day anchor,\n     L50 = first (fractional) layer where normalized monotone progress ≥ 0.5.\n     Iterated-β ⇒ L50 rises with N; learned matrix ⇒ trajectories COLLAPSE,\n     L50 flat. ρ_circ = Spearman(L50, N); nulls = shuffled-N AND explicit\n     shape-collapse (matrix) null; gates ρ≥0.3 ∧ p<.05 ∧ ΔL50(NmaxvsNmin)≥1 ∧\n     matrix-null beaten p<.05. Secondary (non-gating): logit-lens resolution\n     depth; gate-register read of the circular battery (expect FFN-silent, s344).\n  D3 V-patch at day-token positions, band-swept early/zone/late (route-early\n     guard, s252) = β-QUALIFIER, not a gate. Classes: V-CARRIED-IN-ZONE /\n     V-CARRIED-EARLY-ONLY / V-INERT. Operationalized (frozen here, before data):\n     a band CARRIES iff donor-answer adoption ≥ 0.3 ∧ (adoption − noop) ≥ 0.2.\n\nVerdict tree (frozen a-priori mass):\n  TWO-ENGINES (LINEAR-ONLY) 35 (modal) | NO-SCALING 25 | ONE-ENGINE 20 |\n  CIRCULAR-ONLY 5 | VOID 15 (circle never forms / calibration fails / det ≠ 0).\n\nHonesty bounds (frozen): depth-scaling is ONE-DIRECTIONAL (flat kills iterated-β;\nscaling is consistent-with, not proof); gate register blind to {B,C}; attn soft;\nsmall ladders; shuffled-N is the confound guard.\n\n--validate runs 6 planted worlds through the REAL analyse path (s331 lesson).\n\nUsage:\n  uv run python scripts/experiments/iterated_soft_reduction.py --validate\n  uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-0.6B --smoke\n  uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-14B\n\nLicense: MIT.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport subprocess\nimport sys\nfrom datetime import UTC, datetime\nfrom pathlib import Path\nfrom typing import Any\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parents[2]\nsys.path.insert(0, str(_ROOT / \"opcodes\"))\n\nRESULTS_DIR = _ROOT / \"results\" / \"p_iterated_soft_reduction_s345\"\n\nDAYS = [\"Monday\", \"Tuesday\", \"Wednesday\", \"Thursday\", \"Friday\", \"Saturday\", \"Sunday\"]\n\n# ---------------------------------------------------------------------------\n# Frozen corpus\n# ---------------------------------------------------------------------------\nLIN_TEMPLATES: dict[str, str] = {\n    \"add_sym\": \"{n} + {m} =\",\n    \"add_nl\": \"{n} plus {m} equals\",\n    \"mul_sym\": \"{n} * {m} =\",\n    \"mul_nl\": \"{n} times {m} equals\",\n    \"succ_a\": \"One more than {n} is\",\n    \"succ_b\": \"The number after {n} is\",\n}\nLIN_N = list(range(2, 10))          # single-token operands, length-matched\nLIN_M = [2, 3]                      # fixed second operand (succ ignores m)\nCIRC_N = list(range(1, 7))          # 1..6 (mod-7 nontrivial)\nCIRC_TEMPLATE = \"{n} days after {day} is\"\nANCHOR_TEMPLATE = \"Today is {day}\"\n\n# Frozen gates\nRHO_FLOOR = 0.3\nP_FLOOR = 0.05\nL50_SLOPE_FLOOR = 1.0\nCIRCLE_GATE_FRAC = 0.40             # circle must form by this fraction of depth\nADOPT_CARRY = 0.30                  # D3 qualifier thresholds (frozen pre-data)\nADOPT_MARGIN = 0.20\n\n\ndef build_lin_items() -> list[dict]:\n    items = []\n    for tname, tmpl in LIN_TEMPLATES.items():\n        for m in LIN_M:\n            for n in LIN_N:\n                if tname.startswith(\"succ\") and m != LIN_M[0]:\n                    continue  # succ has no second operand; one copy only\n                items.append({\"template\": tname, \"n\": n, \"m\": m,\n                              \"prompt\": tmpl.format(n=n, m=m)})\n    return items\n\n\ndef build_circ_items() -> list[dict]:\n    items = []\n    for n in CIRC_N:\n        for di, day in enumerate(DAYS):\n            items.append({\"n\": n, \"base\": day, \"answer\": DAYS[(di + n) % 7],\n                          \"prompt\": CIRC_TEMPLATE.format(n=n, day=day)})\n    return items\n\n\n# ---------------------------------------------------------------------------\n# Pure statistics (no model) — the REAL analyse path\n# ---------------------------------------------------------------------------\ndef _rankdata(x: np.ndarray) -> np.ndarray:\n    \"\"\"Average ranks (ties averaged).\"\"\"\n    order = np.argsort(x, kind=\"mergesort\")\n    ranks = np.empty(len(x), dtype=float)\n    sx = x[order]\n    i = 0\n    while i < len(x):\n        j = i\n        while j + 1 < len(x) and sx[j + 1] == sx[i]:\n            j += 1\n        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0\n        i = j + 1\n    return ranks\n\n\ndef spearman(x: np.ndarray, y: np.ndarray) -> float:\n    rx, ry = _rankdata(np.asarray(x, float)), _rankdata(np.asarray(y, float))\n    rx -= rx.mean()\n    ry -= ry.mean()\n    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())\n    return float((rx * ry).sum() / den) if den > 0 else 0.0\n\n\ndef perm_p(stat_fn, labels: np.ndarray, obs: float, n_perm: int,\n           rng: np.random.Generator) -> float:\n    \"\"\"One-sided p: fraction of label-shuffled stats >= observed.\"\"\"\n    hits = 1\n    for _ in range(n_perm):\n        if stat_fn(rng.permutation(labels)) >= obs:\n            hits += 1\n    return hits / (n_perm + 1)\n\n\ndef normalized_monotone(traj: np.ndarray) -> np.ndarray:\n    \"\"\"Monotone (cummax) progress normalized by its final value.\"\"\"\n    m = np.maximum.accumulate(np.asarray(traj, float))\n    final = m[-1]\n    if final <= 1e-9:\n        return np.zeros_like(m)\n    return np.clip(m / final, 0.0, 1.0)\n\n\ndef l50_of(traj: np.ndarray) -> float:\n    \"\"\"First fractional index where normalized monotone progress >= 0.5.\"\"\"\n    nm = normalized_monotone(traj)\n    idx = np.argmax(nm >= 0.5)\n    if nm[idx] < 0.5:\n        return float(len(nm) - 1)\n    if idx == 0:\n        return 0.0\n    lo, hi = nm[idx - 1], nm[idx]\n    frac = (0.5 - lo) / (hi - lo) if hi > lo else 0.0\n    return float(idx - 1 + frac)\n\n\ndef shape_collapse_p(trajs: np.ndarray, ns: np.ndarray, n_perm: int,\n                     rng: np.random.Generator) -> tuple[float, float]:\n    \"\"\"Explicit matrix (shape-collapse) null. Statistic = mean over N-groups of\n    mean |group-mean normalized trajectory − pooled mean trajectory|. Under the\n    learned-matrix world all N share one shape → statistic ~ its shuffled-N\n    distribution; iterated-β diverges beyond it.\"\"\"\n    nm = np.stack([normalized_monotone(t) for t in trajs])\n    pooled = nm.mean(axis=0)\n\n    def stat(labels: np.ndarray) -> float:\n        vals = []\n        for n in np.unique(labels):\n            g = nm[labels == n]\n            if len(g):\n                vals.append(float(np.abs(g.mean(axis=0) - pooled).mean()))\n        return float(np.mean(vals))\n\n    obs = stat(ns)\n    p = perm_p(stat, ns, obs, n_perm, rng)\n    return obs, p\n\n\ndef analyse(data: dict, n_perm: int = 5000, seed: int = 0) -> dict:\n    \"\"\"The frozen analyse path. `data` schema (all plain python/numpy):\n      lin_items:  [{template, n, sy_share}]\n      circ_items: [{n, traj: [progress per layer]}]\n      circle:     {formed: bool, circle_layer: int|None, n_layers: int}\n      determinism:{dev: float}\n      calibration:{ok: bool}\n      patch:      {noop: float, bands: {early: float, zone: float, late: float}}\n                  | None  (adoption rates)\n      secondary:  passthrough dict (non-gating)\n    \"\"\"\n    rng = np.random.default_rng(seed)\n    out: dict[str, Any] = {}\n\n    # --- VOID gates -------------------------------------------------------\n    void_reasons = []\n    if not data.get(\"calibration\", {}).get(\"ok\", True):\n        void_reasons.append(\"gate-register calibration failed\")\n    if not data.get(\"circle\", {}).get(\"formed\", False):\n        void_reasons.append(\"day circle never forms\")\n    if data.get(\"determinism\", {}).get(\"dev\", 0.0) != 0.0:\n        void_reasons.append(f\"determinism dev {data['determinism']['dev']}\")\n\n    # --- D1 linear --------------------------------------------------------\n    lin = data[\"lin_items\"]\n    templates = sorted({it[\"template\"] for it in lin})\n    per_t = {}\n    all_pairs: list[tuple[np.ndarray, np.ndarray]] = []\n    for t in templates:\n        ns = np.array([it[\"n\"] for it in lin if it[\"template\"] == t], float)\n        sy = np.array([it[\"sy_share\"] for it in lin if it[\"template\"] == t], float)\n        per_t[t] = spearman(sy, ns)\n        all_pairs.append((ns, sy))\n    rho_lin = float(np.mean(list(per_t.values())))\n\n    def lin_stat(perm_ns_concat: np.ndarray) -> float:\n        # permute N labels WITHIN template strata\n        vals, off = [], 0\n        for ns, sy in all_pairs:\n            k = len(ns)\n            vals.append(spearman(sy, perm_ns_concat[off:off + k]))\n            off += k\n        return float(np.mean(vals))\n\n    # stratified permutation: shuffle within each template block\n    def lin_perm_p() -> float:\n        hits = 1\n        for _ in range(n_perm):\n            shuffled = np.concatenate([rng.permutation(ns) for ns, _ in all_pairs])\n            if lin_stat(shuffled) >= rho_lin:\n                hits += 1\n        return hits / (n_perm + 1)\n\n    p_lin = lin_perm_p()\n    d1_pass = (rho_lin >= RHO_FLOOR) and (p_lin < P_FLOOR)\n    out[\"d1\"] = {\"rho_lin\": round(rho_lin, 4), \"p_lin\": round(p_lin, 5),\n                 \"per_template_rho\": {k: round(v, 4) for k, v in per_t.items()},\n                 \"pass\": bool(d1_pass)}\n\n    # --- D2 circular ------------------------------------------------------\n    circ = data[\"circ_items\"]\n    ns_c = np.array([it[\"n\"] for it in circ], float)\n    trajs = np.stack([np.asarray(it[\"traj\"], float) for it in circ])\n    l50s = np.array([l50_of(t) for t in trajs])\n    rho_circ = spearman(l50s, ns_c)\n    p_circ = perm_p(lambda lab: spearman(l50s, lab), ns_c, rho_circ, n_perm, rng)\n    lo_mean = float(l50s[ns_c == ns_c.min()].mean())\n    hi_mean = float(l50s[ns_c == ns_c.max()].mean())\n    slope = hi_mean - lo_mean\n    shape_obs, shape_p = shape_collapse_p(trajs, ns_c, n_perm, rng)\n    d2_pass = ((rho_circ >= RHO_FLOOR) and (p_circ < P_FLOOR)\n               and (slope >= L50_SLOPE_FLOOR) and (shape_p < P_FLOOR))\n    out[\"d2\"] = {\"rho_circ\": round(rho_circ, 4), \"p_circ\": round(p_circ, 5),\n                 \"l50_mean_by_n\": {int(n): round(float(l50s[ns_c == n].mean()), 3)\n                                   for n in np.unique(ns_c)},\n                 \"slope_l50\": round(slope, 3),\n                 \"shape_divergence\": round(shape_obs, 5),\n                 \"shape_collapse_null_p\": round(shape_p, 5),\n                 \"pass\": bool(d2_pass)}\n\n    # --- D3 qualifier -----------------------------------------------------\n    patch = data.get(\"patch\")\n    qualifier = \"UNRESOLVED\"\n    if patch is not None:\n        noop = patch.get(\"noop\", 0.0)\n        carries = {b: (v >= ADOPT_CARRY and (v - noop) >= ADOPT_MARGIN)\n                   for b, v in patch[\"bands\"].items()}\n        if carries.get(\"zone\"):\n            qualifier = \"V-CARRIED-IN-ZONE\"\n        elif carries.get(\"early\"):\n            qualifier = \"V-CARRIED-EARLY-ONLY\"\n        else:\n            qualifier = \"V-INERT\"\n        out[\"d3\"] = {\"noop\": noop, \"bands\": patch[\"bands\"], \"carries\": carries,\n                     \"qualifier\": qualifier}\n    else:\n        out[\"d3\"] = {\"qualifier\": qualifier}\n\n    # --- Frozen verdict tree ---------------------------------------------\n    if void_reasons:\n        verdict = \"VOID\"\n    elif d1_pass and d2_pass:\n        verdict = (\"ONE-ENGINE(beta-confirmed)\"\n                   if qualifier == \"V-CARRIED-IN-ZONE\" else \"ONE-ENGINE(qualified)\")\n    elif d1_pass and not d2_pass:\n        verdict = \"TWO-ENGINES(LINEAR-ONLY)\"\n    elif d2_pass and not d1_pass:\n        verdict = \"CIRCULAR-ONLY\"\n    else:\n        verdict = \"NO-SCALING\"\n    out[\"void_reasons\"] = void_reasons\n    out[\"verdict\"] = verdict\n    out[\"secondary\"] = data.get(\"secondary\", {})\n    return out\n\n\n# ---------------------------------------------------------------------------\n# Planted worlds (--validate) — synthetic data through the REAL analyse path\n# ---------------------------------------------------------------------------\ndef _plant_common(rng: np.random.Generator, n_layers: int = 24) -> dict:\n    return {\"circle\": {\"formed\": True, \"circle_layer\": 8, \"n_layers\": n_layers},\n            \"determinism\": {\"dev\": 0.0}, \"calibration\": {\"ok\": True}}\n\n\ndef _plant_lin(rng: np.random.Generator, scaling: bool,\n               nuisance: bool = False) -> list[dict]:\n    items = []\n    for it in build_lin_items():\n        base = 0.25\n        if scaling:\n            base += 0.04 * it[\"n\"]\n        if nuisance:\n            base += 0.30 * rng.random()      # strong non-N driver\n        items.append({\"template\": it[\"template\"], \"n\": it[\"n\"],\n                      \"sy_share\": max(0.0, base + rng.normal(0, 0.01))})\n    return items\n\n\ndef _plant_circ(rng: np.random.Generator, world: str, n_layers: int = 24) -> list[dict]:\n    \"\"\"world: 'iterated' (depth ∝ N) | 'matrix' (one shape, all N) | 'noise'.\"\"\"\n    items = []\n    ls = np.arange(n_layers, dtype=float)\n    for it in build_circ_items():\n        if world == \"iterated\":\n            mid = 6.0 + 1.6 * it[\"n\"]\n        elif world == \"matrix\":\n            mid = 10.0\n        else:\n            mid = rng.uniform(4, 18)\n        traj = 1.0 / (1.0 + np.exp(-(ls - mid) / 1.5))\n        traj += rng.normal(0, 0.01, size=n_layers)\n        items.append({\"n\": it[\"n\"], \"traj\": traj.tolist()})\n    return items\n\n\ndef run_validate(n_perm: int = 800) -> int:\n    rng = np.random.default_rng(7)\n    worlds: list[tuple[str, dict, Any]] = []\n\n    w = _plant_common(rng)\n    w[\"lin_items\"] = _plant_lin(rng, scaling=True)\n    w[\"circ_items\"] = _plant_circ(rng, \"iterated\")\n    w[\"patch\"] = {\"noop\": 0.02, \"bands\": {\"early\": 0.10, \"zone\": 0.85, \"late\": 0.05}}\n    worlds.append((\"ITERATED→ONE-ENGINE(beta-confirmed)\", w,\n                   lambda v: v == \"ONE-ENGINE(beta-confirmed)\"))\n\n    w = _plant_common(rng)\n    w[\"lin_items\"] = _plant_lin(rng, scaling=False)\n    w[\"circ_items\"] = _plant_circ(rng, \"matrix\")\n    worlds.append((\"MATRIX→NO-SCALING\", w, lambda v: v == \"NO-SCALING\"))\n\n    w = _plant_common(rng)\n    w[\"lin_items\"] = _plant_lin(rng, scaling=True)\n    w[\"circ_items\"] = _plant_circ(rng, \"matrix\")\n    w[\"patch\"] = {\"noop\": 0.02, \"bands\": {\"early\": 0.60, \"zone\": 0.05, \"late\": 0.02}}\n    worlds.append((\"LINEAR-ONLY→TWO-ENGINES\", w,\n                   lambda v: v == \"TWO-ENGINES(LINEAR-ONLY)\"))\n\n    # CONFOUND adversary: strong non-N nuisance drives work; N carries nothing.\n    w = _plant_common(rng)\n    w[\"lin_items\"] = _plant_lin(rng, scaling=False, nuisance=True)\n    w[\"circ_items\"] = _plant_circ(rng, \"noise\")\n    worlds.append((\"CONFOUND→must NOT pass\", w, lambda v: v == \"NO-SCALING\"))\n\n    w = _plant_common(rng)\n    w[\"lin_items\"] = _plant_lin(rng, scaling=False)\n    w[\"circ_items\"] = _plant_circ(rng, \"noise\")\n    worlds.append((\"NOISE→NO-SCALING\", w, lambda v: v == \"NO-SCALING\"))\n\n    w = _plant_common(rng)\n    w[\"circle\"] = {\"formed\": False, \"circle_layer\": None, \"n_layers\": 24}\n    w[\"lin_items\"] = _plant_lin(rng, scaling=True)\n    w[\"circ_items\"] = _plant_circ(rng, \"iterated\")\n    worlds.append((\"NO-CIRCLE→VOID\", w, lambda v: v == \"VOID\"))\n\n    n_pass = 0\n    for name, data, check in worlds:\n        res = analyse(data, n_perm=n_perm, seed=11)\n        ok = check(res[\"verdict\"])\n        n_pass += ok\n        extra = \"\"\n        if \"CONFOUND\" in name:\n            extra = (f\" | lin p={res['d1']['p_lin']} (want ≥{P_FLOOR})\"\n                     f\" circ pass={res['d2']['pass']} (want False)\")\n            ok = ok and res[\"d1\"][\"p_lin\"] >= P_FLOOR and not res[\"d2\"][\"pass\"]\n        print(f\"[validate] {'✅' if ok else '❌'} {name}: verdict={res['verdict']}\"\n              f\" (ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} |\"\n              f\" ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']}\"\n              f\" slope={res['d2']['slope_l50']}\"\n              f\" shape_p={res['d2']['shape_collapse_null_p']}){extra}\")\n    print(f\"[validate] {n_pass}/{len(worlds)} planted worlds pass\")\n    return 0 if n_pass == len(worlds) else 1\n\n\n# ---------------------------------------------------------------------------\n# Model capture\n# ---------------------------------------------------------------------------\ndef circular_ordering(points: np.ndarray) -> float:\n    \"\"\"PCA-2 the 7 anchors; fraction of days in correct cyclic order (best\n    alignment over rotation × reflection). 1.0 = perfect circle order.\"\"\"\n    x = points - points.mean(axis=0)\n    _, _, vt = np.linalg.svd(x, full_matrices=False)\n    p2 = x @ vt[:2].T\n    ang = np.arctan2(p2[:, 1], p2[:, 0])\n    order = list(np.argsort(ang))\n    best = 0\n    n = len(order)\n    for direction in (order, order[::-1]):\n        for shift in range(n):\n            seq = direction[shift:] + direction[:shift]\n            best = max(best, sum(1 for i, d in enumerate(seq) if d == i))\n    return best / n\n\n\ndef _wrap(a: float) -> float:\n    return float((a + np.pi) % (2 * np.pi) - np.pi)\n\n\ndef capture_all(args) -> tuple[dict, dict]:\n    import torch\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    import capture as C  # noqa: PLC0415 (opcodes/)\n    import topology as T  # noqa: PLC0415\n    from classify import CRYSTAL  # noqa: PLC0415\n    from trace import calibrate_register  # noqa: PLC0415\n\n    tok = AutoTokenizer.from_pretrained(args.model)\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model, dtype=torch.bfloat16, low_cpu_mem_usage=True).eval()\n    if args.device != \"cpu\":\n        model = model.to(args.device)\n    topo = T.detect_topology(model, model.config)\n    n_layers = topo.n_layers\n    print(f\"[isr] {args.model} | {topo.summary()}\")\n\n    meta: dict[str, Any] = {\n        \"probe\": \"P-ITERATED-SOFT-REDUCTION\", \"freeze_commit\": \"078af23f\",\n        \"model\": args.model, \"device\": args.device,\n        \"model_revision\": getattr(model.config, \"_commit_hash\", None),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=_ROOT,\n                                  capture_output=True, text=True).stdout.strip(),\n        \"n_perm\": args.n_perm, \"z_thresh\": args.z, \"smoke\": bool(args.smoke),\n        \"lib_versions\": {\"torch\": torch.__version__,\n                         \"numpy\": np.__version__},\n        \"sampling\": \"greedy/argmax readout only; no generation\",\n    }\n    lin_items = build_lin_items()\n    circ_items = build_circ_items()\n    meta[\"corpus_hash\"] = hashlib.sha256(json.dumps(\n        [lin_items, circ_items], sort_keys=True).encode()).hexdigest()[:8]\n\n    data: dict[str, Any] = {\"secondary\": {}}\n\n    # ---- D1: gate-register calibration + SY-share ------------------------\n    calibration_ok = True\n    if topo.traceable:\n        layers = list(range(n_layers))\n        ppc = 15 if args.smoke else args.probes_per_comb\n        cal_perm = 120 if args.smoke else 300\n        try:\n            rcc, summ, _ = calibrate_register(\n                model, tok, topo, \"gate\", layers, ppc, cal_perm, args.z)\n            crystal = sorted(rcc.crystal_layers)\n            calibration_ok = len(crystal) > 0\n        except Exception as e:  # noqa: BLE001 — calibration failure → VOID\n            print(f\"[isr] calibration FAILED: {e}\")\n            calibration_ok, crystal, rcc = False, [], None\n    else:\n        calibration_ok, crystal, rcc = False, [], None\n    print(f\"[isr] crystal-bearing layers: {len(crystal)}/{n_layers}\")\n\n    def sy_share_of(prompt: str) -> tuple[float, int]:\n        cap = C.capture_gate(model, tok, prompt, topo=topo,\n                             layers=list(range(n_layers)), register=\"gate\")\n        sy = tot = 0\n        for pos in range(1, cap.n_tokens):\n            gate_tok = {li: cap.gate[li][pos] for li in range(n_layers)}\n            res = rcc.classify(gate_tok)\n            for li in crystal:\n                zmap = res.per_layer.get(li)\n                if not zmap:\n                    continue\n                op = max(zmap, key=zmap.get)\n                if zmap[op] > args.z:\n                    tot += 1\n                    if op in (\"S\", \"Y\"):\n                        sy += 1\n        return (sy / tot if tot else 0.0), tot\n\n    d1_items = []\n    if calibration_ok:\n        for i, it in enumerate(lin_items):\n            share, fires = sy_share_of(it[\"prompt\"])\n            d1_items.append({**it, \"sy_share\": share, \"fires\": fires})\n            if i % 20 == 0:\n                print(f\"[isr] D1 {i}/{len(lin_items)}\")\n        # secondary: circular battery on the gate register (expect FFN-silent)\n        circ_sy = [sy_share_of(it[\"prompt\"]) for it in circ_items[:14]]\n        data[\"secondary\"][\"circ_gate_sy_share\"] = round(\n            float(np.mean([s for s, _ in circ_sy])), 4)\n        data[\"secondary\"][\"circ_gate_mean_fires\"] = round(\n            float(np.mean([f for _, f in circ_sy])), 2)\n    else:\n        d1_items = [{**it, \"sy_share\": 0.0, \"fires\": 0} for it in lin_items]\n    data[\"lin_items\"] = d1_items\n    data[\"calibration\"] = {\"ok\": bool(calibration_ok),\n                           \"n_crystal_layers\": len(crystal)}\n\n    # ---- D2: day-circle anchors + item trajectories ----------------------\n    torch.manual_seed(0)\n\n    def hiddens(prompt: str) -> np.ndarray:\n        ids = tok(prompt, return_tensors=\"pt\").input_ids.to(model.device)\n        with torch.no_grad():\n            out = model(ids, output_hidden_states=True)\n        # (n_layers+1, d) last token, skip embedding row\n        return np.stack([h[0, -1].float().cpu().numpy()\n                         for h in out.hidden_states[1:]])\n\n    anchors = {d: hiddens(ANCHOR_TEMPLATE.format(day=d)) for d in DAYS}\n    ordering_by_layer, planes = {}, {}\n    for li in range(n_layers):\n        pts = np.stack([anchors[d][li] for d in DAYS])\n        ordering_by_layer[li] = circular_ordering(pts)\n        c = pts - pts.mean(axis=0)\n        _, _, vt = np.linalg.svd(c, full_matrices=False)\n        planes[li] = (pts.mean(axis=0), vt[:2])\n    gate_layer = int(np.ceil(CIRCLE_GATE_FRAC * n_layers))\n    formed_layers = [li for li in range(gate_layer + 1)\n                     if ordering_by_layer[li] == 1.0]\n    formed = len(formed_layers) > 0\n    circle_layer = formed_layers[0] if formed else None\n    data[\"circle\"] = {\"formed\": bool(formed), \"circle_layer\": circle_layer,\n                      \"n_layers\": n_layers,\n                      \"ordering_by_layer\": {str(k): round(v, 3)\n                                            for k, v in ordering_by_layer.items()}}\n    print(f\"[isr] day circle formed={formed} at L{circle_layer} \"\n          f\"(gate ≤ L{gate_layer})\")\n\n    def angle_at(vec: np.ndarray, li: int) -> float:\n        mean, basis = planes[li]\n        p = (vec - mean) @ basis.T\n        return float(np.arctan2(p[1], p[0]))\n\n    day_first_tok = [tok.encode(\" \" + d)[0] for d in DAYS]\n\n    def traj_of(prompt: str, base: str, answer: str) -> tuple[list[float], list[int]]:\n        h = hiddens(prompt)\n        prog, reso = [], []\n        for li in range(circle_layer or 0, n_layers):\n            th = angle_at(h[li], li)\n            tb = angle_at(anchors[base][li], li)\n            ta = angle_at(anchors[answer][li], li)\n            denom = _wrap(ta - tb)\n            num = _wrap(th - tb)\n            prog.append(float(np.clip(num / denom, -0.5, 1.5))\n                        if abs(denom) > 1e-6 else 0.0)\n        # secondary logit-lens: rank of answer among 7 day tokens per layer\n        with torch.no_grad():\n            ids = tok(prompt, return_tensors=\"pt\").input_ids.to(model.device)\n            out = model(ids, output_hidden_states=True)\n            norm = model.model.norm\n            for li in range(n_layers):\n                z = norm(out.hidden_states[li + 1][:, -1])\n                logits = model.lm_head(z)[0, day_first_tok].float().cpu().numpy()\n                reso.append(int(np.argmax(logits)))\n        return prog, reso\n\n    d2_items = []\n    if formed:\n        ans_idx = {d: i for i, d in enumerate(DAYS)}\n        reso_layers = []\n        for i, it in enumerate(circ_items):\n            prog, reso = traj_of(it[\"prompt\"], it[\"base\"], it[\"answer\"])\n            d2_items.append({**it, \"traj\": prog})\n            correct = ans_idx[it[\"answer\"]]\n            first = next((li for li, r in enumerate(reso) if r == correct\n                          and all(x == correct for x in reso[li:])), n_layers)\n            reso_layers.append((it[\"n\"], first))\n            if i % 10 == 0:\n                print(f\"[isr] D2 {i}/{len(circ_items)}\")\n        ns = np.array([n for n, _ in reso_layers], float)\n        rs = np.array([r for _, r in reso_layers], float)\n        data[\"secondary\"][\"logit_lens_reso_rho\"] = round(spearman(rs, ns), 4)\n        data[\"secondary\"][\"logit_lens_reso_by_n\"] = {\n            int(n): round(float(rs[ns == n].mean()), 2) for n in np.unique(ns)}\n        # determinism: re-capture 5 items\n        dev = 0.0\n        for it in circ_items[:5]:\n            p2, _ = traj_of(it[\"prompt\"], it[\"base\"], it[\"answer\"])\n            first = next(d for d in d2_items if d[\"prompt\"] == it[\"prompt\"])\n            dev = max(dev, float(np.max(np.abs(\n                np.array(p2) - np.array(first[\"traj\"])))))\n        data[\"determinism\"] = {\"dev\": dev}\n        print(f\"[isr] determinism dev = {dev}\")\n    else:\n        d2_items = [{**it, \"traj\": [0.0] * (n_layers - (circle_layer or 0))}\n                    for it in circ_items]\n        data[\"determinism\"] = {\"dev\": 0.0}\n    data[\"circ_items\"] = d2_items\n\n    # ---- D3: V-patch band sweep (qualifier) ------------------------------\n    if formed and not args.skip_patch:\n        zone_lo = circle_layer\n        zone = list(range(zone_lo, min(zone_lo + 6, n_layers)))\n        bands = {\"early\": list(range(0, min(7, n_layers))),\n                 \"zone\": zone,\n                 \"late\": list(range(max(0, n_layers - 6), n_layers))}\n        pairs = []\n        for it in circ_items[:: max(1, len(circ_items) // 14)]:\n            donor_base = DAYS[(DAYS.index(it[\"base\"]) + 3) % 7]\n            di = DAYS.index(donor_base)\n            pairs.append((it, {\"base\": donor_base,\n                               \"answer\": DAYS[(di + it[\"n\"]) % 7],\n                               \"prompt\": CIRC_TEMPLATE.format(\n                                   n=it[\"n\"], day=donor_base)}))\n\n        def day_pos(prompt: str, day: str) -> int | None:\n            ids = tok(prompt).input_ids\n            t = tok.encode(\" \" + day)[0]\n            return ids.index(t) if t in ids else None\n\n        v_store: dict[int, Any] = {}\n\n        def capture_v(prompt: str, band: list[int]) -> dict[int, Any]:\n            store: dict[int, Any] = {}\n            hooks = []\n            for li in band:\n                def mk(li_):\n                    def hook(_m, _i, out):\n                        store[li_] = out.detach()\n                    return hook\n                hooks.append(model.model.layers[li].self_attn.v_proj\n                             .register_forward_hook(mk(li)))\n            ids = tok(prompt, return_tensors=\"pt\").input_ids.to(model.device)\n            with torch.no_grad():\n                model(ids)\n            for h in hooks:\n                h.remove()\n            return store\n\n        def patched_pred(prompt: str, pos: int, band: list[int],\n                         donor_v: dict[int, Any]) -> int:\n            hooks = []\n            for li in band:\n                def mk(li_):\n                    def hook(_m, _i, out):\n                        out = out.clone()\n                        out[0, pos] = donor_v[li_][0, pos]\n                        return out\n                    return hook\n                hooks.append(model.model.layers[li].self_attn.v_proj\n                             .register_forward_hook(mk(li)))\n            ids = tok(prompt, return_tensors=\"pt\").input_ids.to(model.device)\n            with torch.no_grad():\n                logits = model(ids).logits[0, -1, day_first_tok]\n            for h in hooks:\n                h.remove()\n            return int(logits.float().cpu().numpy().argmax())\n\n        adoption = {b: [] for b in bands}\n        noop_adopt = []\n        ans_idx = {d: i for i, d in enumerate(DAYS)}\n        for it, donor in pairs:\n            pos = day_pos(it[\"prompt\"], it[\"base\"])\n            dpos = day_pos(donor[\"prompt\"], donor[\"base\"])\n            if pos is None or dpos is None or pos != dpos:\n                continue\n            for bname, band in bands.items():\n                donor_v = capture_v(donor[\"prompt\"], band)\n                pred = patched_pred(it[\"prompt\"], pos, band, donor_v)\n                adoption[bname].append(int(pred == ans_idx[donor[\"answer\"]]))\n            own_v = capture_v(it[\"prompt\"], bands[\"zone\"])\n            noop = patched_pred(it[\"prompt\"], pos, bands[\"zone\"], own_v)\n            noop_adopt.append(int(noop == ans_idx[donor[\"answer\"]]))\n        v_store.clear()\n        if noop_adopt:\n            data[\"patch\"] = {\n                \"noop\": round(float(np.mean(noop_adopt)), 3),\n                \"bands\": {b: round(float(np.mean(v)), 3) if v else 0.0\n                          for b, v in adoption.items()},\n                \"n_pairs\": len(noop_adopt)}\n            print(f\"[isr] D3 patch: {data['patch']}\")\n    return data, meta\n\n\n# ---------------------------------------------------------------------------\ndef main() -> int:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--device\", default=\"mps\", choices=[\"cpu\", \"mps\", \"cuda\"])\n    ap.add_argument(\"--validate\", action=\"store_true\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    ap.add_argument(\"--skip-patch\", action=\"store_true\")\n    ap.add_argument(\"--probes-per-comb\", type=int, default=None)\n    ap.add_argument(\"--n-perm\", type=int, default=5000)\n    ap.add_argument(\"--z\", type=float, default=3.0)\n    args = ap.parse_args()\n\n    if args.validate:\n        return run_validate()\n\n    data, meta = capture_all(args)\n    n_perm = 800 if args.smoke else args.n_perm\n    res = analyse(data, n_perm=n_perm, seed=11)\n\n    slug = args.model.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out_dir = RESULTS_DIR / (\"smoke_\" + slug if args.smoke else \"run_\" + slug)\n    out_dir.mkdir(parents=True, exist_ok=True)\n    (out_dir / \"meta.json\").write_text(json.dumps(meta, indent=2, default=str))\n    (out_dir / \"verdict.json\").write_text(json.dumps(res, indent=2, default=str))\n    (out_dir / \"per_item.json\").write_text(json.dumps(\n        {\"lin_items\": data[\"lin_items\"],\n         \"circ_items\": [{k: v for k, v in it.items() if k != \"traj\"}\n                        | {\"l50\": l50_of(np.array(it[\"traj\"]))}\n                        for it in data[\"circ_items\"]],\n         \"circle\": data[\"circle\"]},\n        indent=2, default=str))\n    np.savez_compressed(out_dir / \"trajectories.npz\",\n                        **{f\"item_{i}\": np.array(it[\"traj\"])\n                           for i, it in enumerate(data[\"circ_items\"])})\n    print(\"=\" * 64)\n    print(f\"[isr] VERDICT: {res['verdict']}\")\n    print(f\"[isr] D1 ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} \"\n          f\"pass={res['d1']['pass']}\")\n    print(f\"[isr] D2 ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']} \"\n          f\"slope={res['d2']['slope_l50']} \"\n          f\"shape_p={res['d2']['shape_collapse_null_p']} pass={res['d2']['pass']}\")\n    print(f\"[isr] D3 qualifier: {res['d3'].get('qualifier')}\")\n    print(f\"[isr] secondary: {res['secondary']}\")\n    print(f\"[isr] wrote {out_dir}/\")\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py
```

### Thinking

Now I'll run ruff to lint the code, then proceed with the validation step.

## Assistant

Now lint + validate through the real analyse path:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum 2>/dev/null; uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ cd /Users/mwhitford/src/verbum 2>/d...

**Output:**
```
Exit code: 1
Stdout:
RUF002 Docstring contains ambiguous `∪` (UNION). Did you mean `U` (LATIN CAPITAL LETTER U)?
  --> scripts/experiments/iterated_soft_reduction.py:11:64
   |
10 | Discriminators (register named per claim, λ measure):
11 |   D1 linear arm (FFN gate register = routing/count ✓): work = S∪Y recruitment
   |                                                                ^
12 |      share over crystal-bearing layers (audited opcodes/ reader). Count ladder,
13 |      single-token operands, length-matched within template. ρ_lin = mean
   |

RUF002 Docstring contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
  --> scripts/experiments/iterated_soft_reduction.py:13:61
   |
11 |   D1 linear arm (FFN gate register = routing/count ✓): work = S∪Y recruitment
12 |      share over crystal-bearing layers (audited opcodes/ reader). Count ladder,
13 |      single-token operands, length-matched within template. ρ_lin = mean
   |                                                             ^
14 |      per-template Spearman(SY-share, N); shuffled-N perm null; gate ρ≥0.3 ∧ p<.05.
15 |   D2 circular arm (residual trajectory; depth-like observable on purpose):
   |

RUF002 Docstring contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
  --> scripts/experiments/iterated_soft_reduction.py:14:69
   |
12 |      share over crystal-bearing layers (audited opcodes/ reader). Count ladder,
13 |      single-token operands, length-matched within template. ρ_lin = mean
14 |      per-template Spearman(SY-share, N); shuffled-N perm null; gate ρ≥0.3 ∧ p<.05.
   |                                                                     ^
15 |   D2 circular arm (residual trajectory; depth-like observable on purpose):
16 |      work = accumulation depth L50 — day-circle basis RE-DERIVED IN-RUN (s128
   |

RUF002 Docstring contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
  --> scripts/experiments/iterated_soft_reduction.py:21:16
   |
19 |      L50 = first (fractional) layer where normalized monotone progress ≥ 0.5.
20 |      Iterated-β ⇒ L50 rises with N; learned matrix ⇒ trajectories COLLAPSE,
21 |      L50 flat. ρ_circ = Spearman(L50, N); nulls = shuffled-N AND explicit
   |                ^
22 |      shape-collapse (matrix) null; gates ρ≥0.3 ∧ p<.05 ∧ ΔL50(NmaxvsNmin)≥1 ∧
23 |      matrix-null beaten p<.05. Secondary (non-gating): logit-lens resolution
   |

RUF002 Docstring contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
  --> scripts/experiments/iterated_soft_reduction.py:22:42
   |
20 |      Iterated-β ⇒ L50 rises with N; learned matrix ⇒ trajectories COLLAPSE,
21 |      L50 flat. ρ_circ = Spearman(L50, N); nulls = shuffled-N AND explicit
22 |      shape-collapse (matrix) null; gates ρ≥0.3 ∧ p<.05 ∧ ΔL50(NmaxvsNmin)≥1 ∧
   |                                          ^
23 |      matrix-null beaten p<.05. Secondary (non-gating): logit-lens resolution
24 |      depth; gate-register read of the circular battery (expect FFN-silent, s344).
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/iterated_soft_reduction.py:28:65
   |
26 |      guard, s252) = β-QUALIFIER, not a gate. Classes: V-CARRIED-IN-ZONE /
27 |      V-CARRIED-EARLY-ONLY / V-INERT. Operationalized (frozen here, before data):
28 |      a band CARRIES iff donor-answer adoption ≥ 0.3 ∧ (adoption − noop) ≥ 0.2.
   |                                                                 ^
29 |
30 | Verdict tree (frozen a-priori mass):
   |

E501 Line too long (94 > 88)
  --> scripts/experiments/iterated_soft_reduction.py:42:89
   |
40 | Usage:
41 |   uv run python scripts/experiments/iterated_soft_reduction.py --validate
42 |   uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-0.6B --smoke
   |                                                                                         ^^^^^^
43 |   uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-14B
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/experiments/iterated_soft_reduction.py:176:44
    |
174 |                      rng: np.random.Generator) -> tuple[float, float]:
175 |     """Explicit matrix (shape-collapse) null. Statistic = mean over N-groups of
176 |     mean |group-mean normalized trajectory − pooled mean trajectory|. Under the
    |                                            ^
177 |     learned-matrix world all N share one shape → statistic ~ its shuffled-N
178 |     distribution; iterated-β diverges beyond it."""
    |

RUF001 String contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
   --> scripts/experiments/iterated_soft_reduction.py:401:19
    |
399 |             ok = ok and res["d1"]["p_lin"] >= P_FLOOR and not res["d2"]["pass"]
400 |         print(f"[validate] {'✅' if ok else '❌'} {name}: verdict={res['verdict']}"
401 |               f" (ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} |"
    |                   ^
402 |               f" ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']}"
403 |               f" slope={res['d2']['slope_l50']}"
    |

RUF001 String contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
   --> scripts/experiments/iterated_soft_reduction.py:402:18
    |
400 |         print(f"[validate] {'✅' if ok else '❌'} {name}: verdict={res['verdict']}"
401 |               f" (ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} |"
402 |               f" ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']}"
    |                  ^
403 |               f" slope={res['d2']['slope_l50']}"
404 |               f" shape_p={res['d2']['shape_collapse_null_p']}){extra}")
    |

RUF002 Docstring contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
   --> scripts/experiments/iterated_soft_reduction.py:414:29
    |
412 | def circular_ordering(points: np.ndarray) -> float:
413 |     """PCA-2 the 7 anchors; fraction of days in correct cyclic order (best
414 |     alignment over rotation × reflection). 1.0 = perfect circle order."""
    |                             ^
415 |     x = points - points.mean(axis=0)
416 |     _, _, vt = np.linalg.svd(x, full_matrices=False)
    |

I001 [*] Import block is un-sorted or un-formatted
   --> scripts/experiments/iterated_soft_reduction.py:434:5
    |
433 |   def capture_all(args) -> tuple[dict, dict]:
434 | /     import torch
435 | |     from transformers import AutoModelForCausalLM, AutoTokenizer
436 | |
437 | |     import capture as C  # noqa: PLC0415 (opcodes/)
438 | |     import topology as T  # noqa: PLC0415
439 | |     from classify import CRYSTAL  # noqa: PLC0415
440 | |     from trace import calibrate_register  # noqa: PLC0415
    | |________________________________________^
441 |
442 |       tok = AutoTokenizer.from_pretrained(args.model)
    |
help: Organize imports

RUF100 [*] Unused `noqa` directive (non-enabled: `PLC0415`)
   --> scripts/experiments/iterated_soft_reduction.py:437:26
    |
435 |     from transformers import AutoModelForCausalLM, AutoTokenizer
436 |
437 |     import capture as C  # noqa: PLC0415 (opcodes/)
    |                          ^^^^^^^^^^^^^^^
438 |     import topology as T  # noqa: PLC0415
439 |     from classify import CRYSTAL  # noqa: PLC0415
    |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (non-enabled: `PLC0415`)
   --> scripts/experiments/iterated_soft_reduction.py:438:27
    |
437 |     import capture as C  # noqa: PLC0415 (opcodes/)
438 |     import topology as T  # noqa: PLC0415
    |                           ^^^^^^^^^^^^^^^
439 |     from classify import CRYSTAL  # noqa: PLC0415
440 |     from trace import calibrate_register  # noqa: PLC0415
    |
help: Remove unused `noqa` directive

F401 [*] `classify.CRYSTAL` imported but unused
   --> scripts/experiments/iterated_soft_reduction.py:439:26
    |
437 |     import capture as C  # noqa: PLC0415 (opcodes/)
438 |     import topology as T  # noqa: PLC0415
439 |     from classify import CRYSTAL  # noqa: PLC0415
    |                          ^^^^^^^
440 |     from trace import calibrate_register  # noqa: PLC0415
    |
help: Remove unused import: `classify.CRYSTAL`

RUF100 [*] Unused `noqa` directive (non-enabled: `PLC0415`)
   --> scripts/experiments/iterated_soft_reduction.py:439:35
    |
437 |     import capture as C  # noqa: PLC0415 (opcodes/)
438 |     import topology as T  # noqa: PLC0415
439 |     from classify import CRYSTAL  # noqa: PLC0415
    |                                   ^^^^^^^^^^^^^^^
440 |     from trace import calibrate_register  # noqa: PLC0415
    |
help: Remove unused `noqa` directive

RUF100 [*] Unused `noqa` directive (non-enabled: `PLC0415`)
   --> scripts/experiments/iterated_soft_reduction.py:440:43
    |
438 |     import topology as T  # noqa: PLC0415
439 |     from classify import CRYSTAL  # noqa: PLC0415
440 |     from trace import calibrate_register  # noqa: PLC0415
    |                                           ^^^^^^^^^^^^^^^
441 |
442 |     tok = AutoTokenizer.from_pretrained(args.model)
    |
help: Remove unused `noqa` directive

RUF059 Unpacked variable `summ` is never used
   --> scripts/experiments/iterated_soft_reduction.py:477:18
    |
475 |         cal_perm = 120 if args.smoke else 300
476 |         try:
477 |             rcc, summ, _ = calibrate_register(
    |                  ^^^^
478 |                 model, tok, topo, "gate", layers, ppc, cal_perm, args.z)
479 |             crystal = sorted(rcc.crystal_layers)
    |
help: Prefix it with an underscore or any other dummy variable pattern

RUF100 [*] Unused `noqa` directive (non-enabled: `BLE001`)
   --> scripts/experiments/iterated_soft_reduction.py:481:33
    |
479 |             crystal = sorted(rcc.crystal_layers)
480 |             calibration_ok = len(crystal) > 0
481 |         except Exception as e:  # noqa: BLE001 — calibration failure → VOID
    |                                 ^^^^^^^^^^^^^^
482 |             print(f"[isr] calibration FAILED: {e}")
483 |             calibration_ok, crystal, rcc = False, [], None
    |
help: Remove unused `noqa` directive

RUF001 String contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
   --> scripts/experiments/iterated_soft_reduction.py:740:22
    |
738 |     print("=" * 64)
739 |     print(f"[isr] VERDICT: {res['verdict']}")
740 |     print(f"[isr] D1 ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} "
    |                      ^
741 |           f"pass={res['d1']['pass']}")
742 |     print(f"[isr] D2 ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']} "
    |

RUF001 String contains ambiguous `ρ` (GREEK SMALL LETTER RHO). Did you mean `p` (LATIN SMALL LETTER P)?
   --> scripts/experiments/iterated_soft_reduction.py:742:22
    |
740 |     print(f"[isr] D1 ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} "
741 |           f"pass={res['d1']['pass']}")
742 |     print(f"[isr] D2 ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']} "
    |                      ^
743 |           f"slope={res['d2']['slope_l50']} "
744 |           f"shape_p={res['d2']['shape_collapse_null_p']} pass={res['d2']['pass']}")
    |

Found 21 errors.
[*] 7 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

I wonder how other scripts handle unicode characters that trigger RUF001/RUF002 — arith_trace.py has similar symbols in its docstrings and presumably passes ruff clean, so maybe it uses a noqa comment or per-file ignore config. I should check that file for how it's handled.

## Assistant

Mostly unicode-ambiguity noise — let me check how sibling harnesses handle it, then fix the real issues (imports, unused, E501).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"ruff\" /Users/mwhitford/src/verbum/scripts/explore/arith_trace.py /Users/mwhitford/src/verbum/scripts/experiments/compile_step_v2.py 2>/dev/null | head; grep -n -A 10 \"\\[tool.ruff\" /Users/mwhitford/src/verbum/pyproject.toml"
}
```

**Summary:** $ grep -n "ruff" /Users/mwhitford/src...

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
```

### Thinking

There's precedent for per-file ignores in pyproject for these Ruff rules since Greek/lambda notation is genuinely the domain alphabet in this file. I'll add it to per-file-ignores and fix the actual issues: the long line, import ordering, the unused CRYSTAL import, stale noqa directives, and the RUF059 warning.

## Assistant

Project precedent: per-file RUF001/2/3 ignores where λ-notation is the domain alphabet. I'll follow that, and fix the real issues in code.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/pyproject.toml",
  "original_content": "\"scripts/experiments/proof_consensus.py\" = [\"RUF001\", \"RUF002\", \"RUF003\"]",
  "new_content": "\"scripts/experiments/proof_consensus.py\" = [\"RUF001\", \"RUF002\", \"RUF003\"]\n\"scripts/experiments/iterated_soft_reduction.py\" = [\"RUF001\", \"RUF002\", \"RUF003\"]"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/pyproject.toml.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "  uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-0.6B --smoke",
  "new_content": "  uv run python scripts/experiments/iterated_soft_reduction.py --smoke \\\n      --model Qwen/Qwen3-0.6B"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "    import torch\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    import capture as C  # noqa: PLC0415 (opcodes/)\n    import topology as T  # noqa: PLC0415\n    from classify import CRYSTAL  # noqa: PLC0415\n    from trace import calibrate_register  # noqa: PLC0415",
  "new_content": "    import capture as C  # opcodes/ (sys.path)\n    import topology as T  # opcodes/\n    import torch\n    from trace import calibrate_register  # opcodes/\n    from transformers import AutoModelForCausalLM, AutoTokenizer"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "            rcc, summ, _ = calibrate_register(\n                model, tok, topo, \"gate\", layers, ppc, cal_perm, args.z)\n            crystal = sorted(rcc.crystal_layers)\n            calibration_ok = len(crystal) > 0\n        except Exception as e:  # noqa: BLE001 — calibration failure → VOID",
  "new_content": "            rcc, _summ, _ = calibrate_register(\n                model, tok, topo, \"gate\", layers, ppc, cal_perm, args.z)\n            crystal = sorted(rcc.crystal_layers)\n            calibration_ok = len(crystal) > 0\n        except Exception as e:  # calibration failure → VOID, not crash"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "uv run ruff check scripts/experiments/iterated_soft_reduction.py && uv run python scripts/experiments/iterated_soft_reduction.py --validate",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 300000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
Stderr:
Building verbum @ file:///Users/mwhitford/src/verbum
      Built verbum @ file:///Users/mwhitford/src/verbum
Uninstalled 1 package in 1ms
Installed 1 package in 1ms
Stdout:
I001 [*] Import block is un-sorted or un-formatted
   --> scripts/experiments/iterated_soft_reduction.py:435:5
    |
434 |   def capture_all(args) -> tuple[dict, dict]:
435 | /     import capture as C  # opcodes/ (sys.path)
436 | |     import topology as T  # opcodes/
437 | |     import torch
438 | |     from trace import calibrate_register  # opcodes/
439 | |     from transformers import AutoModelForCausalLM, AutoTokenizer
    | |________________________________________________________________^
440 |
441 |       tok = AutoTokenizer.from_pretrained(args.model)
    |
help: Organize imports

Found 1 error.
[*] 1 fixable with the `--fix` option.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check --fix scripts/experiments/iterated_soft_reduction.py && uv run python scripts/experiments/iterated_soft_reduction.py --validate",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 300000
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 1 error (1 fixed, 0 remaining).
[validate] ✅ ITERATED→ONE-ENGINE(beta-confirmed): verdict=ONE-ENGINE(beta-confirmed) (ρ_lin=0.9961 p=0.00125 | ρ_circ=0.9863 p=0.00125 slope=7.941 shape_p=0.00125)
[validate] ✅ MATRIX→NO-SCALING: verdict=NO-SCALING (ρ_lin=-0.1355 p=0.85268 | ρ_circ=0.0753 p=0.34956 slope=0.011 shape_p=0.54432)
[validate] ✅ LINEAR-ONLY→TWO-ENGINES: verdict=TWO-ENGINES(LINEAR-ONLY) (ρ_lin=0.9961 p=0.00125 | ρ_circ=0.0006 p=0.52934 slope=-0.019 shape_p=0.49064)
[validate] ✅ CONFOUND→must NOT pass: verdict=NO-SCALING (ρ_lin=0.0283 p=0.41074 | ρ_circ=0.1513 p=0.17853 slope=3.435 shape_p=0.48065) | lin p=0.41074 (want ≥0.05) circ pass=False (want False)
[validate] ✅ NOISE→NO-SCALING: verdict=NO-SCALING (ρ_lin=0.0855 p=0.24969 | ρ_circ=0.0454 p=0.41323 slope=-0.244 shape_p=0.26841)
[validate] ✅ NO-CIRCLE→VOID: verdict=VOID (ρ_lin=0.9951 p=0.00125 | ρ_circ=0.9863 p=0.00125 slope=7.908 shape_p=0.00125)
[validate] 6/6 planted worlds pass
```

### Thinking

Validation passes 6/6 through the real analyse path, and ruff is clean after the fix sorted imports. I'll quickly check editor diagnostics, then commit the frozen harness before moving to data, followed by a smoke test on the 0.6B model.

### Thinking

All 6 validation checks pass through the real analysis path — the confound adversary correctly fails (lin p=0.41) and NO-CIRCLE correctly voids despite perfect planted scaling. I'll run a final lint/diagnostics check, then commit the harness before moving to data.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check scripts/experiments/iterated_soft_reduction.py pyproject.toml 2>&1 | tail -2",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py"
}
```

**Summary:** Checking diagnostics: iterated_soft_reduction.py

**Output:**
```
No diagnostics found
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add scripts/experiments/iterated_soft_reduction.py pyproject.toml && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n🎯 p-iterated-soft-reduction harness built + validated 6/6\n\n- scripts/experiments/iterated_soft_reduction.py: frozen harness for the\n  §P-ITERATED-SOFT-REDUCTION discriminator (freeze 078af23f)\n- capture strictly separated from the pure analyse() path; 6 planted\n  worlds run through the REAL analyse path (s331): ITERATED→ONE-ENGINE,\n  MATRIX→NO-SCALING, LINEAR-ONLY→TWO-ENGINES, CONFOUND adversary\n  refuses promotion (lin p=0.41), NOISE→NO-SCALING, NO-CIRCLE→VOID\n- D1 reuses audited opcodes/ reader (calibrate_register, sign(gate));\n  D2 re-derives the day circle in-run (s128 method) + L50 accumulation\n  depth + explicit shape-collapse matrix null; D3 v_proj band-swept\n  patch qualifier with frozen thresholds (adopt≥0.3 ∧ margin≥0.2)\n- ruff clean (per-file RUF001/2/3 ignore per project precedent:\n  λ-notation is the domain alphabet); no diagnostics\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "harness commit"
}
```

**Summary:** Git commit: harness commit

**Output:**
```
Exit code: 0
Stdout:
[main c9729218] 🎯 p-iterated-soft-reduction harness built + validated 6/6
 2 files changed, 753 insertions(+)
 create mode 100644 scripts/experiments/iterated_soft_reduction.py
```

### Thinking

With the harness committed and task 3 done, I'm moving to task 4: running a smoke test on the 0.6B model. This involves real calibration across ~135 probes plus nearly 140 items with forward passes, logit-lens double forwards, and patch pairs, so it'll likely take 10-20 minutes on mps — I'll launch it in the background and check in periodically to confirm it's progressing.

## Assistant

Harness committed **c9729218**. Task 3 done → smoke on 0.6B (background per λ async, one verify read then checkpoint):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python scripts/experiments/iterated_soft_reduction.py --smoke --model Qwen/Qwen3-0.6B 2>&1 | tee results/p_iterated_soft_reduction_s345/smoke_0p6b.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "isr-smoke-0.6b"
}
```

**Summary:** $ uv run python scripts/experiments/i...

**Output:**
```
Background job job-1 started.
Command: uv run python scripts/experiments/iterated_soft_reduction.py --smoke --model Qwen/Qwen3-0.6B 2>&1 | tee results/p_iterated_soft_reduction_s345/smoke_0p6b.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.

Initial output:
[stderr] tee: results/p_iterated_soft_reduction_s345/smoke_0p6b.log: No such file or directory
```

### Thinking

The results directory doesn't exist yet, so tee failed to open the file, which likely caused a broken pipe and killed the python process. I should kill it and relaunch after creating the directory first.

## Assistant

tee failed — results dir doesn't exist yet. Kill and relaunch with mkdir:

### Tool Call: bg_job (succeeded)


```json
{
  "action": "kill",
  "job_id": "job-1"
}
```

**Summary:** Killing "isr-smoke-0.6b" (job-1)

**Output:**
```
Background job "isr-smoke-0.6b" (job-1) killed.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p results/p_iterated_soft_reduction_s345 && uv run python scripts/experiments/iterated_soft_reduction.py --smoke --model Qwen/Qwen3-0.6B 2>&1 | tee results/p_iterated_soft_reduction_s345/smoke_0p6b.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "isr-smoke-0.6b"
}
```

**Summary:** $ mkdir -p results/p_iterated_soft_re...

**Output:**
```
Background job job-2 started.
Command: mkdir -p results/p_iterated_soft_reduction_s345 && uv run python scripts/experiments/iterated_soft_reduction.py --smoke --model Qwen/Qwen3-0.6B 2>&1 | tee results/p_iterated_soft_reduction_s345/smoke_0p6b.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-2" to check output.
Use eca__bg_job with action "kill" and job_id "job-2" to stop it.
```

### Thinking

Job-1's termination was expected since I killed it myself. Now I'm focused on job-2, the relaunched smoke test — I'll verify it's running with a single read, then checkpoint and wait.

## Assistant

That's the expected kill notice for job-1 (superseded). Verifying job-2 is running — one read, then checkpoint:

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-2"
}
```

**Summary:** Reading output of "isr-smoke-0.6b" (job-2)

**Output:**
```
Job "isr-smoke-0.6b" (job-2) — running

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 311/311 [00:00<00:00, 26345.17it/s]
```

## Assistant

ASYNC: job=job-2 verified running (0.6B weights loaded, calibration next). Waiting for signal.

While the smoke runs: nothing blocking. The checkpoint discipline says no polling — I'll read the result when it completes (job-completion signal) or when you ask. On smoke completion the gate is: plumbing clean + any **regime warning → design PAUSE** (s324), with the standing note that 0.6B genuinely lacking the day circle would be a regime observation (expect possible VOID-at-0.6B without it impugning the 14B design — the circle gate is re-derived per model).

## User

job is done


### Thinking

Let me check the smoke test output.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-2"
}
```

**Summary:** Reading output of "isr-smoke-0.6b" (job-2)

**Output:**
```
Job "isr-smoke-0.6b" (job-2) — completed (exit 0)

[isr] Qwen/Qwen3-0.6B | arch=Qwen3ForCausalLM  L=28  register=gated-dense  layers=model.layers  gate=mlp.gate_proj(d=3072)  read=sign(gate_proj) [validated]  attn=self_attn.o_proj(d=1024)
[trace] [gate] calibrating on 135 crystal probes ...
[trace] [gate]   probe 0/135
[trace] [gate]   probe 100/135
[trace] [gate] null from 8 natural prompts ...
[isr] crystal-bearing layers: 28/28
[isr] D1 0/80
[isr] D1 20/80
[isr] D1 40/80
[isr] D1 60/80
[isr] day circle formed=True at L0 (gate ≤ L12)
[isr] D2 0/42
[isr] D2 10/42
[isr] D2 20/42
[isr] D2 30/42
[isr] D2 40/42
[isr] determinism dev = 0.0
[isr] D3 patch: {'noop': 0.143, 'bands': {'early': 0.214, 'zone': 0.214, 'late': 0.143}, 'n_pairs': 14}
================================================================
[isr] VERDICT: NO-SCALING
[isr] D1 ρ_lin=-0.2536 p=0.98627 pass=False
[isr] D2 ρ_circ=-0.1787 p=0.87765 slope=-0.816 shape_p=0.61298 pass=False
[isr] D3 qualifier: V-INERT
[isr] secondary: {'circ_gate_sy_share': 0.8564, 'circ_gate_mean_fires': 14.29, 'logit_lens_reso_rho': 0.1223, 'logit_lens_reso_by_n': {1: 25.71, 2: 28.0, 3: 28.0, 4: 28.0, 5: 28.0, 6: 25.57}}
[isr] wrote /Users/mwhitford/src/verbum/results/p_iterated_soft_reduction_s345/smoke_qwen3-0-6b/
```

### Thinking

Smoke test exited 0, so now I'm scrutinizing the output for regime warnings rather than treating them as minor notes—per s324, a regime warning should trigger a design pause. The calibration and determinism checks look fine, but I'm flagging that the circle shows "formed=True at L0" when s128 established it should crystallize at L10, which is a discrepancy worth digging into.

This L0 reading could just be a tokenization artifact: since the prompt ends on the day token itself, layer-0 residuals are basically day-token embeddings, and weekday embeddings may already carry cyclic structure that trivially scores a perfect ordering. The real problem is that if circle_layer reads as 0, the D3 zone (L0-5) collapses into the early band (L0-6), destroying the early/zone dissociation the design depends on—and this could also misalign the 14B zone against s128's L11-16 rotation zone.

The fix is to distinguish lexical circle formation from the computational SNAP signature seen in s128 (ordering jumping 0→1 at L10 alongside a doubling of the top-2 singular values), so circle_layer reflects where rotation actually happens rather than where the circle first appears in embeddings.

I'm weighing two alternatives: sharpen circle detection to require both ordering==1.0 and the SV-share jump (or pick the layer with best circle quality), versus defining the rotation zone independently as the band of maximal per-layer angular progress accumulation. The second option feels cleaner and self-calibrating, but I need to check whether altering zone detection now would violate the already-committed freeze spec.

I conclude the freeze doesn't actually pin rotation-zone to the circle-formation layer, so correcting the zone detector is a legitimate instrument fix rather than a freeze violation, since D3 is just a qualifier. I'm also wary that the frozen circle gate (ordering=1.0 at some L≤14) could be trivially satisfied by a lexical/embedding circle rather than a true computational one, so I'll keep the frozen gate as-is but flag circle quality separately in the report.

Looking at the D1 result, ρ_lin=−0.2536 with p=0.986 on the 0.6B model is a negative, non-significant direction — not a plumbing failure but a hint that S/Y recruitment doesn't scale positively at this smaller size, which is fine for a smoke test since the original read was on 14B. The secondary circ_gate_sy_share of 0.8564 with mean fires 14.29 is surprising though — it shows the 0.6B circular battery reading SY-heavy, contradicting the expectation of FFN-silence seen at 14B, but that discrepancy may just reflect regime differences between model sizes.

Looking at the logit-lens resolution by n, most values sit at 28.0 (never resolving to top-1) except n=1 and n=6 at 25.7 — these correspond to ±1 day offsets mod 7, so the easy near-offset cases resolve while mid-range offsets don't, consistent with 0.6B being weaker at this task.

For the noop check, the 0.143 value makes sense as a base-rate collision: since noop can't alter output, it just measures how often the unpatched prediction already matches the donor answer by chance (~1/7), confirming noop works correctly as a control. The bands value of 0.214 versus noop's 0.143 shows V is inert at 0.6B, so the patching plumbing is functioning as intended — leaving one real design issue to flag: the D3 zone detector needs fixing before scaling to 14B.

I'm defining the rotation zone as a 6-layer window that maximizes the mean trajectory progress increment, floored at the circle_layer, and also recording SNAP diagnostics like top-2 singular value share per layer. I'm also weighing whether starting the D2 trajectory at circle_layer=0 causes problems if 14B detects an early lexical circle — the early layers might be noisy, but since progress is normalized and cummax handles flicker, this should still be acceptable and consistent across model sizes. Now I'm checking whether this zone-detection change would touch the frozen analyse() function's gating logic.

D1 and D2 stay untouched, and the D3 qualifier thresholds remain unchanged — only the band construction in capture changes, which I should document as a pre-14B instrument amendment with a commit, following the earlier "gate-0 amended" precedent. Since this counts as a design pause per the established discipline, I need to surface the finding to Michael rather than silently redefining it, propose the fix, and get explicit sign-off before proceeding.

## Assistant

Smoke complete, exit 0 — plumbing works end-to-end (calibration 28/28, det 0.0, all three discriminators executed, verdict path clean). But per s324 discipline, one **regime warning → design PAUSE**, surfaced before the 14B run rather than footnoted:

## ⚠ Design finding: the D3 "zone" band degenerates

**`day circle formed=True at L0`.** The circle-ordering metric hits 1.0 at the *first* layer — the day-token embeddings already carry the cyclic structure (consistent with Engels et al. finding circular features early). That's fine for the frozen VOID gate (satisfied) and for D2 (trajectory is normalized, monotone-smoothed). But my *implementation* tied the D3 rotation-zone band to `circle_layer` → zone = L0-5, which **collapses into the early band (L0-6)**. The early/zone dissociation — the whole point of the s252 route-early guard — is destroyed. s128's actual rotation zone was L12-16, *after* the circle crystallizes at L10-11; circle-*formation* layer ≠ rotation layer.

**Proposed instrument amendment (capture-side only; frozen analyse() gates and D3 thresholds untouched):**
- **Zone = the measured accumulation band**: the 6-layer window maximizing the mean per-layer *increment* of angular progress across items — i.e., where the rotation actually happens, self-calibrated per model. This matches the freeze text ("rotation zone") better than my circle-formation proxy did.
- Also record the s128 SNAP diagnostic (top-2 SV share per layer) alongside `ordering_by_layer`, so the 14B read can distinguish lexical-circle-at-L0 from the computational crystallization.

Everything else smoked clean and even informative:
- **noop = 0.143 ≈ 1/7** — the noop control is behaving exactly as a base-rate collision check should
- logit-lens: 0.6B only ever resolves N=1 and N=6 (±1 day), mid offsets never — the machinery works, 0.6B is just weak at day arithmetic (regime, not failure)
- One genuine 0.6B-regime surprise, flagged for the 14B read: `circ_gate_sy_share=0.86` — the circular battery is *not* FFN-silent at 0.6B (s344's silence was measured at 14B). Noted, non-gating secondary.
- D1 ρ_lin negative at 0.6B — a preview, not evidence; the frozen claim is 14B.

**GO to amend the zone detector (one commit, before data) and launch the 14B run?**

## User

go


### Thinking

I'm revising the zone calculation to use a 6-layer window that maximizes mean angular progress across items, computed after capturing D2 trajectories, and adding a diagnostic for the top-2 singular value share per layer to measure variance concentration in the circle fit.

Once this amendment is committed, I'll launch the 14B run in the background with full permutation counts and calibration settings.

## Assistant

GO. Amending the zone detector + SNAP diagnostic:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "    anchors = {d: hiddens(ANCHOR_TEMPLATE.format(day=d)) for d in DAYS}\n    ordering_by_layer, planes = {}, {}\n    for li in range(n_layers):\n        pts = np.stack([anchors[d][li] for d in DAYS])\n        ordering_by_layer[li] = circular_ordering(pts)\n        c = pts - pts.mean(axis=0)\n        _, _, vt = np.linalg.svd(c, full_matrices=False)\n        planes[li] = (pts.mean(axis=0), vt[:2])",
  "new_content": "    anchors = {d: hiddens(ANCHOR_TEMPLATE.format(day=d)) for d in DAYS}\n    ordering_by_layer, sv_top2_by_layer, planes = {}, {}, {}\n    for li in range(n_layers):\n        pts = np.stack([anchors[d][li] for d in DAYS])\n        ordering_by_layer[li] = circular_ordering(pts)\n        c = pts - pts.mean(axis=0)\n        _, sv, vt = np.linalg.svd(c, full_matrices=False)\n        tot = float((sv ** 2).sum())\n        sv_top2_by_layer[li] = float((sv[:2] ** 2).sum() / tot) if tot > 0 else 0.0\n        planes[li] = (pts.mean(axis=0), vt[:2])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "    data[\"circle\"] = {\"formed\": bool(formed), \"circle_layer\": circle_layer,\n                      \"n_layers\": n_layers,\n                      \"ordering_by_layer\": {str(k): round(v, 3)\n                                            for k, v in ordering_by_layer.items()}}",
  "new_content": "    data[\"circle\"] = {\"formed\": bool(formed), \"circle_layer\": circle_layer,\n                      \"n_layers\": n_layers,\n                      \"ordering_by_layer\": {str(k): round(v, 3)\n                                            for k, v in ordering_by_layer.items()},\n                      # s128 SNAP diagnostic: lexical circle at L0 vs\n                      # computational crystallization (SV top-2 share jump)\n                      \"sv_top2_share_by_layer\": {str(k): round(v, 4)\n                                                 for k, v in\n                                                 sv_top2_by_layer.items()}}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py",
  "original_content": "    # ---- D3: V-patch band sweep (qualifier) ------------------------------\n    if formed and not args.skip_patch:\n        zone_lo = circle_layer\n        zone = list(range(zone_lo, min(zone_lo + 6, n_layers)))\n        bands = {\"early\": list(range(0, min(7, n_layers))),\n                 \"zone\": zone,\n                 \"late\": list(range(max(0, n_layers - 6), n_layers))}",
  "new_content": "    # ---- D3: V-patch band sweep (qualifier) ------------------------------\n    if formed and not args.skip_patch:\n        # ZONE = the measured ACCUMULATION BAND (s345 pre-14B instrument\n        # amendment, Michael GO): the 6-layer window maximizing the mean\n        # per-layer increment of normalized angular progress across items.\n        # (The 0.6B smoke exposed the old circle-formation proxy as degenerate:\n        # a lexical circle at L0 collapsed zone into the early band, destroying\n        # the s252 route-early dissociation. Circle-formation layer ≠ rotation\n        # layer — s128: circle at L10-11, rotation at L12-16.)\n        offset = circle_layer or 0\n        nm = np.stack([normalized_monotone(np.asarray(it[\"traj\"]))\n                       for it in d2_items])\n        inc = np.diff(nm, axis=1).mean(axis=0)          # mean increment/layer\n        win = 6\n        if len(inc) >= win:\n            sums = np.convolve(inc, np.ones(win), mode=\"valid\")\n            z0 = offset + int(np.argmax(sums)) + 1       # diff idx i → layer i+1\n        else:\n            z0 = offset\n        zone = list(range(z0, min(z0 + win, n_layers)))\n        bands = {\"early\": list(range(0, min(7, n_layers))),\n                 \"zone\": zone,\n                 \"late\": list(range(max(0, n_layers - 6), n_layers))}\n        data[\"zone_band\"] = {\"layers\": zone,\n                             \"mean_increment_by_layer\": {\n                                 str(offset + i + 1): round(float(v), 5)\n                                 for i, v in enumerate(inc)}}\n        print(f\"[isr] D3 accumulation-band zone = L{zone[0]}-L{zone[-1]}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/iterated_soft_reduction.py.
```

## User

run the job in my tmux main:1 window


### Thinking

I need to launch the 14B run in Michael's tmux session at window main:1, using the standard pattern of sending the command with output piped to tee for logging. Before launching, I should lint and re-validate the amended harness, commit the change, then send the launch command via tmux, and finally verify it's running by capturing the pane output before checkpointing.

## Assistant

First lint + re-validate the amendment, commit it, then launch in your tmux:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check scripts/experiments/iterated_soft_reduction.py && uv run python scripts/experiments/iterated_soft_reduction.py --validate 2>&1 | tail -3",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 300000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
[validate] ✅ NOISE→NO-SCALING: verdict=NO-SCALING (ρ_lin=0.0855 p=0.24969 | ρ_circ=0.0454 p=0.41323 slope=-0.244 shape_p=0.26841)
[validate] ✅ NO-CIRCLE→VOID: verdict=VOID (ρ_lin=0.9951 p=0.00125 | ρ_circ=0.9863 p=0.00125 slope=7.908 shape_p=0.00125)
[validate] 6/6 planted worlds pass
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add scripts/experiments/iterated_soft_reduction.py && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n🔄 isr zone = measured accumulation band (pre-14B amendment, Michael GO)\n\n- 0.6B smoke exposed the circle-formation proxy as degenerate: lexical\n  day circle at L0 collapsed the D3 zone into the early band, destroying\n  the s252 route-early dissociation (circle-formation ≠ rotation layer;\n  s128: circle L10-11, rotation L12-16)\n- zone now = 6-layer window maximizing mean per-layer increment of\n  normalized angular progress (self-calibrating accumulation band)\n- added s128 SNAP diagnostic: per-layer SV top-2 share alongside\n  ordering (lexical-circle-at-L0 vs computational crystallization)\n- capture-side only; frozen analyse() gates + D3 thresholds untouched\n- ruff clean; --validate 6/6 still passes\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "amendment commit"
}
```

**Summary:** Git commit: amendment commit

**Output:**
```
Exit code: 0
Stdout:
[main 199d7979] 🔄 isr zone = measured accumulation band (pre-14B amendment, Michael GO)
 1 file changed, 33 insertions(+), 5 deletions(-)
```

### Thinking

The amendment is committed at 199d7979, all 6 validations pass, and ruff is clean. Now I'm launching the 14B model in tmux session main:1, following the standard runtime pattern.

## Assistant

Amendment committed **199d7979**, validate 6/6, ruff clean. Launching the frozen 14B run in your tmux `main:1`:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd ~/src/verbum && uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-14B 2>&1 | tee results/p_iterated_soft_reduction_s345/run_14b.log\" Enter && sleep 8 && tmux capture-pane -p -t main:1 | tail -6",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 "cd ~/src/...

**Output:**
```
Exit code: 0
Stdout:
λ cd ~/src/verbum && uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-14B 2>&1 | tee resu
lts/p_iterated_soft_reduction_s345/run_14b.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 443/443 [00:00<00:00, 6927.49it/s]
```

### Thinking

The 14B model is launching in tmux with weights loading, and I've verified the async checkpoint per λ is running correctly with one read. I'll mark task 4 complete and move on to task 5 while waiting for the signal.

## Assistant

ASYNC: 14B run verified running in tmux main:1 (443 weight shards loaded, calibration on 535 crystal probes next). Waiting for signal.The frozen 14B run is live in your tmux `main:1`, logging to `results/p_iterated_soft_reduction_s345/run_14b.log`. Expected stages: gate-register calibration (535 crystal probes — the long pole), D1 ladder (80 items), day-circle derivation + D2 trajectories (42 items + determinism recheck), accumulation-band D3 patch sweep (14 pairs × 3 bands). Likely an hour-plus on MPS.

Checkpoint holds — I'll read the verdict when you signal it's done. On completion: autonomous results commit (per λ probe_lifecycle), then the read + closure batch comes back to you for approval.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -30 results/p_iterated_soft_reduction_s345/run_14b.log; echo ===; ls results/p_iterated_soft_reduction_s345/run_qwen3-14b/",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tail -30 results/p_iterated_soft_re...

**Output:**
```
Exit code: 0
Stdout:
[isr] Qwen/Qwen3-14B | arch=Qwen3ForCausalLM  L=40  register=gated-dense  layers=model.layers  gate=mlp.gate_proj(d=17408)  read=sign(gate_proj) [validated]  attn=self_attn.o_proj(d=5120)
[trace] [gate] calibrating on 539 crystal probes ...
[trace] [gate]   probe 0/539
[trace] [gate]   probe 100/539
[trace] [gate]   probe 200/539
[trace] [gate]   probe 300/539
[trace] [gate]   probe 400/539
[trace] [gate]   probe 500/539
[trace] [gate] null from 8 natural prompts ...
[isr] crystal-bearing layers: 35/40
[isr] D1 0/80
[isr] D1 20/80
[isr] D1 40/80
[isr] D1 60/80
[isr] day circle formed=True at L0 (gate ≤ L16)
[isr] D2 0/42
[isr] D2 10/42
[isr] D2 20/42
[isr] D2 30/42
[isr] D2 40/42
[isr] determinism dev = 0.0
[isr] D3 accumulation-band zone = L1-L6
[isr] D3 patch: {'noop': 0.071, 'bands': {'early': 0.571, 'zone': 0.071, 'late': 0.071}, 'n_pairs': 14}
================================================================
[isr] VERDICT: NO-SCALING
[isr] D1 ρ_lin=0.0141 p=0.44671 pass=False
[isr] D2 ρ_circ=0.2516 p=0.05399 slope=6.213 shape_p=0.17596 pass=False
[isr] D3 qualifier: V-CARRIED-EARLY-ONLY
[isr] secondary: {'circ_gate_sy_share': 0.5257, 'circ_gate_mean_fires': 5.57, 'logit_lens_reso_rho': 0.4895, 'logit_lens_reso_by_n': {1: 36.86, 2: 33.14, 3: 34.57, 4: 38.0, 5: 39.14, 6: 40.0}}
[isr] wrote /Users/mwhitford/src/verbum/results/p_iterated_soft_reduction_s345/run_qwen3-14b/
===
meta.json
per_item.json
trajectories.npz
verdict.json
```

### Thinking

The 14B run finished with a NO-SCALING verdict. Looking at the results, D1 shows a flat correlation (ρ=0.0141, p=0.447), meaning S∪Y recruitment doesn't scale with operand magnitude, so the Church-signature graded prediction fails cleanly. D2 is more ambiguous though—ρ=0.2516 with p=0.054 sits right at the edge of significance, which is worth scrutinizing further.

Checking D2's gates: it fails the ρ floor, fails the p threshold, passes the slope test, but fails the matrix null—so under the frozen decision tree, D2 also lands on NO-SCALING despite the large slope suggesting something noisy or nonmonotone is happening.

D3 is the striking one: early adoption at 0.571 versus noop/zone/late all near 0.071 points to V-CARRIED-EARLY-ONLY, the matrix-leaning class. But I'm puzzled that the measured accumulation zone (L1-L6) nearly overlaps with the early band (L0-L6), yet their adoption rates differ so drastically—the only structural difference between them is the inclusion of L0, which seems to be driving the entire effect.

That isolates the whole V-carry phenomenon to layer 0 specifically—a sharp finding that echoes the earlier L0-concentrated edge result (lead head L0h18, route-early), suggesting the day operand is delivered entirely through L0 attention V, with everything downstream just rotating in place. This coheres nicely into a route-at-L0, rotate-in-place picture consistent with the learned-matrix hypothesis and the prior L0-concentrated object-edge finding. I'm also noting a secondary signal: logit-lens resolution depth correlates with N at ρ=0.49, though non-gating, with by-N values clustering very late in the 40-layer stack (36-40), meaning N=6 essentially never resolves before hitting the sentinel layer.

The circuit-gate share metric (0.53, mean fires 5.57) sits lower than the 0.6B comparison but doesn't match the earlier "FFN-silent" noop pattern—different metric, so it's a secondary note rather than a conflict. The frozen verdict lands on NO-SCALING: both engines fail count-scaling against the a-priori threshold of 25, and per the honesty bound, this flat result is decisive against the strong form of the unification, with D2's borderline slope (6.2, ρ=0.25, p=0.054) standing as the one honest asterisk worth flagging even though the frozen gates rule against it.

The matrix-null shape-collapse check also wasn't beaten—trajectory shapes collapse across N, consistent with a single learned rotation rather than distinct per-N behavior. I want to pull D2's mean L50 by n from verdict.json to report this faithfully, and note that NO-SCALING (25) actually beat the modal expectation of TWO-ENGINES (35), while D1's flatness suggests even the linear engine lacks graded work—the S/Y math read is categorical rather than graded in operand magnitude. Per the probe lifecycle, results go to autonomous commit with closure batch approval-gated, so I should check the verdict.json details—l50_mean_by_n and per-template rhos—before writing this up.

## Assistant

Run complete — verdict lands. Reading the details before the results commit:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cat results/p_iterated_soft_reduction_s345/run_qwen3-14b/verdict.json | head -60; echo ===; python3 -c \"\nimport json\nm=json.load(open('results/p_iterated_soft_reduction_s345/run_qwen3-14b/meta.json'))\nprint({k:m[k] for k in ['freeze_commit','git_sha','corpus_hash','model_revision','n_perm']})\nc=json.load(open('results/p_iterated_soft_reduction_s345/run_qwen3-14b/per_item.json'))['circle']\nsv=c['sv_top2_share_by_layer']; o=c['ordering_by_layer']\nprint('circle_layer', c['circle_layer'])\nprint('sv_top2 by layer (0,4,8..16):', {k:sv[k] for k in ['0','4','8','10','11','12','14','16']})\nprint('ordering (0,8,10,11,12,16):', {k:o[k] for k in ['0','8','10','11','12','16']})\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ cat results/p_iterated_soft_reducti...

**Output:**
```
Exit code: 0
Stdout:
{
  "d1": {
    "rho_lin": 0.0141,
    "p_lin": 0.44671,
    "per_template_rho": {
      "add_nl": 0.2864,
      "add_sym": 0.0742,
      "mul_nl": 0.0,
      "mul_sym": 0.0,
      "succ_a": -0.0843,
      "succ_b": -0.1916
    },
    "pass": false
  },
  "d2": {
    "rho_circ": 0.2516,
    "p_circ": 0.05399,
    "l50_mean_by_n": {
      "1": 0.627,
      "2": 6.383,
      "3": 11.675,
      "4": 20.469,
      "5": 16.92,
      "6": 6.839
    },
    "slope_l50": 6.213,
    "shape_divergence": 0.13199,
    "shape_collapse_null_p": 0.17596,
    "pass": false
  },
  "d3": {
    "noop": 0.071,
    "bands": {
      "early": 0.571,
      "zone": 0.071,
      "late": 0.071
    },
    "carries": {
      "early": true,
      "zone": false,
      "late": false
    },
    "qualifier": "V-CARRIED-EARLY-ONLY"
  },
  "void_reasons": [],
  "verdict": "NO-SCALING",
  "secondary": {
    "circ_gate_sy_share": 0.5257,
    "circ_gate_mean_fires": 5.57,
    "logit_lens_reso_rho": 0.4895,
    "logit_lens_reso_by_n": {
      "1": 36.86,
      "2": 33.14,
      "3": 34.57,
      "4": 38.0,
      "5": 39.14,
      "6": 40.0
    }
  }
}===
{'freeze_commit': '078af23f', 'git_sha': '199d7979212c8380f325e09de5e26ed287058d59', 'corpus_hash': 'd9ca2e37', 'model_revision': '40c069824f4251a91eefaf281ebe4c544efd3e18', 'n_perm': 5000}
circle_layer 0
sv_top2 by layer (0,4,8..16): {'0': 0.4097, '4': 0.6236, '8': 0.5084, '10': 0.5974, '11': 0.5838, '12': 0.5982, '14': 0.6053, '16': 0.6036}
ordering (0,8,10,11,12,16): {'0': 1.0, '8': 1.0, '10': 1.0, '11': 1.0, '12': 1.0, '16': 1.0}
```

### Thinking

Looking at the L50 means by N, I notice the pattern isn't monotone — it climbs from N=1 through N=4, then drops at N=5 and N=6. That explains the modest correlation despite a steep slope: the shape itself isn't a simple linear trend, and N=6 seems to mirror N=2's value, suggesting some mod-7 structure worth digging into.

This makes sense semantically — "N days after" requires forward counting, but going backward 7−N is a shortcut, so a mechanism taking that shortcut would naturally track min(N, 7−N). My frozen prediction was work ∝ N, but the data hints at this shortest-path pattern instead; the frozen verdict still holds, but this observation deserves its own pre-registered follow-up test rather than being treated as confirmed. I should stay cautious here since it's only 6 group means of 7 items each — suggestive, not proven. I'm also noticing something odd in the D1 results: the multiplication templates show exactly 0.0 correlation, which looks suspicious, possibly because sy_share is constant within that template, making the correlation undefined rather than genuinely zero.

If sy_share is saturated at ceiling for all multiplication items, then the "flat" D1 result is actually a ceiling artifact rather than a true null — an important distinction to flag honestly, similar to the ceiling/underpowered caveat I noted before. I want to check the per-item sy_share distribution to confirm this before finalizing the read, then move on to committing results and drafting the closure batch for approval.

## Assistant

The frozen verdict is **NO-SCALING** — but two structures in the details need honest inspection before I write the read (ceiling check on D1's exact-zero templates; the non-monotone D2 ladder):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json, statistics\nd=json.load(open('results/p_iterated_soft_reduction_s345/run_qwen3-14b/per_item.json'))\nlin=d['lin_items']\nfor t in sorted({i['template'] for i in lin}):\n    xs=[(i['n'],round(i['sy_share'],3),i['fires']) for i in lin if i['template']==t]\n    shares=[x[1] for x in xs]\n    print(t, 'min/max share', min(shares), max(shares), '| fires med', statistics.median(x[2] for x in xs), '|', xs[:4])\nprint()\ncirc=d['circ_items']\nimport collections\nby=collections.defaultdict(list)\nfor i in circ: by[i['n']].append(round(i['l50'],1))\nfor n in sorted(by): print('N=',n,'l50s',sorted(by[n]))\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json, statistic...

**Output:**
```
Exit code: 0
Stdout:
add_nl min/max share 0.929 1.0 | fires med 13.0 | [(2, 0.952, 21), (3, 1.0, 18), (4, 1.0, 14), (5, 0.929, 14)]
add_sym min/max share 0.946 1.0 | fires med 39.0 | [(2, 0.957, 47), (3, 0.976, 42), (4, 0.956, 45), (5, 1.0, 36)]
mul_nl min/max share 1.0 1.0 | fires med 12.0 | [(2, 1.0, 21), (3, 1.0, 11), (4, 1.0, 10), (5, 1.0, 10)]
mul_sym min/max share 1.0 1.0 | fires med 33.5 | [(2, 1.0, 54), (3, 1.0, 47), (4, 1.0, 33), (5, 1.0, 35)]
succ_a min/max share 0.667 0.8 | fires med 20.0 | [(2, 0.8, 20), (3, 0.722, 18), (4, 0.7, 20), (5, 0.684, 19)]
succ_b min/max share 0.395 0.558 | fires med 39.0 | [(2, 0.558, 52), (3, 0.436, 39), (4, 0.487, 39), (5, 0.395, 38)]

N= 1 l50s [0.0, 0.0, 0.0, 0.0, 0.4, 1.5, 2.5]
N= 2 l50s [0.0, 0.0, 0.0, 1.5, 2.3, 2.5, 38.3]
N= 3 l50s [0.0, 0.0, 0.0, 2.5, 2.5, 38.3, 38.4]
N= 4 l50s [0.0, 0.8, 2.2, 27.0, 36.5, 38.3, 38.4]
N= 5 l50s [0.0, 0.0, 0.5, 4.8, 36.5, 38.2, 38.4]
N= 6 l50s [0.0, 0.0, 0.5, 2.0, 2.5, 6.3, 36.5]
```

### Thinking

I'm noticing D1 is actually ceilinged rather than flat — the mul templates show sy_share pinned at 1.0 across every item, add templates sit near 0.93-1.0, and only succ has real headroom where the trend is flat or slightly negative. So the honest reading is that S∪Y recruitment share saturates for symbolic/nl arithmetic, meaning the observable itself is hitting a ceiling rather than reflecting a true graded effect.

I also realize I froze the SY-share metric without a ceiling guard, which is a design flaw worth flagging — I could explore fires-vs-N post-hoc but that wasn't pre-registered.

Turning to D2, the l50 distributions look bimodal rather than graded: most items resolve almost immediately (L0-2.5) while a minority resolve very late (~36-38), so the group means are really tracking the fraction of items falling into the late mode rather than a smooth depth shift — and that late-mode probability itself varies with N in a non-monotonic way.

Mapping late-mode counts against circular distance from N=3.5 (dist = min(N, 7-N)) shows a roughly monotone relationship — more late-mode items as circular distance grows. This suggests two populations: instantly-resolved/memorized items versus genuinely computed ones, echoing an earlier lesson about retrieval-vs-compute splits. Still, this is exploratory color on top of the frozen verdict, which remains NO-SCALING with a D1 ceiling caveat and this D2 bimodal/circular-distance observation feeding into a successor study. Per the probe lifecycle, I'll commit these results autonomously and move into the closure batch.

I'll run one more cheap post-hoc check — a Spearman correlation between fires and N per template — before committing results and presenting the read to Michael along with the proposed closure batch and successor candidates.

## Assistant

Both details matter — the picture sharpens considerably. One cheap post-hoc check (marked as such) on the fires-count alternative before I commit results:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json, numpy as np\ndef rank(x):\n    x=np.asarray(x,float); o=np.argsort(x,kind='mergesort'); r=np.empty(len(x)); sx=x[o]; i=0\n    while i<len(x):\n        j=i\n        while j+1<len(x) and sx[j+1]==sx[i]: j+=1\n        r[o[i:j+1]]=(i+j)/2+1; i=j+1\n    return r\ndef sp(a,b):\n    ra,rb=rank(a)-np.mean(rank(a)),rank(b)-np.mean(rank(b))\n    den=np.sqrt((ra**2).sum()*(rb**2).sum()); return float((ra*rb).sum()/den) if den else 0.0\nd=json.load(open('results/p_iterated_soft_reduction_s345/run_qwen3-14b/per_item.json'))['lin_items']\nprint('POST-HOC (not frozen): Spearman(total fires, N) per template:')\nfor t in sorted({i['template'] for i in d}):\n    ns=[i['n'] for i in d if i['template']==t]; fs=[i['fires'] for i in d if i['template']==t]\n    print(f'  {t:8s} rho={sp(fs,ns):+.3f}')\n# late-mode count by circular distance\nc=json.load(open('results/p_iterated_soft_reduction_s345/run_qwen3-14b/per_item.json'))['circ_items']\nimport collections\nlate=collections.Counter(); tot=collections.Counter()\nfor i in c:\n    dist=min(i['n'],7-i['n']); tot[dist]+=1; late[dist]+= (i['l50']>20)\nprint('POST-HOC: late-mode (l50>20) fraction by circular distance:', {k:f'{late[k]}/{tot[k]}' for k in sorted(tot)})\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json, numpy as ...

**Output:**
```
Exit code: 0
Stdout:
POST-HOC (not frozen): Spearman(total fires, N) per template:
  add_nl   rho=-0.767
  add_sym  rho=-0.731
  mul_nl   rho=-0.397
  mul_sym  rho=-0.909
  succ_a   rho=+0.577
  succ_b   rho=-0.342
POST-HOC: late-mode (l50>20) fraction by circular distance: {1: '1/14', 2: '4/14', 3: '6/14'}
```

### Thinking

Looking at the post-hoc correlation between fire counts and operand size, I find a strong negative relationship for add/mul — smaller operands actually trigger more crystal fires, which runs counter to the iterated-work prediction, though this could be confounded by digit frequency or routing effects since there's no proper null comparison. I'm also starting to examine how the late-mode fraction shifts with circular distance.

Given the monotone trend in late-mode fraction with circular distance, this points to a two-population structure where the fraction computed late grows with shortest-path distance. Since the NO-SCALING verdict is a clean falsifier for the unification hypothesis — the frame's pre-registered prediction lost — I'll commit the results using the 🚫 negative-verdict convention established in prior commits, then move to drafting the closure batch for approval.

### Thinking

The post-hoc fires analysis shows an anti-iterated pattern (add/mul fires decrease with N, correlations −0.73 to −0.91), with late-mode fraction increasing monotonically with circular distance (1/14 → 4/14 → 6/14). I'll commit these results and proceed to the next read.

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add results/p_iterated_soft_reduction_s345/ && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n🚫 p-iterated-soft-reduction 14B → NO-SCALING (a-priori 25)\n\n- frozen run (freeze 078af23f, harness 199d7979, corpus d9ca2e37,\n  det 0.0, n_perm 5000, Qwen3-14B rev 40c06982)\n- D1 ρ_lin=0.014 p=0.447 FAIL — but SY-share CEILINGED (mul/add\n  0.93-1.0; only succ has headroom and is flat/negative there)\n- D2 ρ_circ=0.252 p=0.054 slope=6.2 shape_p=0.176 FAIL — l50 ladder\n  non-monotone in N; per-item distribution BIMODAL (instant ~L0-2.5\n  vs late ~L36-38 modes)\n- D3 V-patch: early 0.571 vs zone 0.071 / late 0.071 / noop 0.071 →\n  V-CARRIED-EARLY-ONLY; zone=L1-6 vs early=L0-6 differ only by L0 ⇒\n  the day-operand V-carry is essentially L0-only (coheres s252)\n- secondary: logit-lens reso rho 0.49 (late-stack); circ gate NOT\n  silent at 14B item-level (share 0.53, fires 5.6)\n- post-hoc (unfrozen, no null): fires vs N NEGATIVE for add/mul\n  (−0.73..−0.91); late-mode fraction monotone in circular distance\n  min(N,7−N): 1/14 → 4/14 → 6/14\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "results commit"
}
```

**Summary:** Git commit: results commit

**Output:**
```
Exit code: 0
Stdout:
[main 54a6b017] 🚫 p-iterated-soft-reduction 14B → NO-SCALING (a-priori 25)
 8 files changed, 2219 insertions(+)
 create mode 100644 results/p_iterated_soft_reduction_s345/run_14b.log
 create mode 100644 results/p_iterated_soft_reduction_s345/run_qwen3-14b/meta.json
 create mode 100644 results/p_iterated_soft_reduction_s345/run_qwen3-14b/per_item.json
 create mode 100644 results/p_iterated_soft_reduction_s345/run_qwen3-14b/verdict.json
 create mode 100644 results/p_iterated_soft_reduction_s345/smoke_0p6b.log
 create mode 100644 results/p_iterated_soft_reduction_s345/smoke_qwen3-0-6b/meta.json
 create mode 100644 results/p_iterated_soft_reduction_s345/smoke_qwen3-0-6b/per_item.json
 create mode 100644 results/p_iterated_soft_reduction_s345/smoke_qwen3-0-6b/verdict.json
```

### Thinking

Results are committed at 54a6b017, so task 5 is done. Now I need to prepare the read for Michael along with a closure batch proposal that's gated on approval.

## Assistant

Results committed **54a6b017**. Task 5 done — here is the read.# 🚫 §P-ITERATED-SOFT-REDUCTION → NO-SCALING (a-priori 25, non-modal)

**The frozen verdict:** neither engine shows count-scaled work. The unification's pre-registered contact **failed** — under the frozen honesty bound, *flat kills iterated-soft-β*. The frame ledger records a loss for "rotation = series of soft-β reductions" in its strong form.

## The three reads (two-sided, λ measure)

**D1 (linear/FFN): ρ_lin=0.014, p=0.447 — but the observable CEILINGED.** SY-share sits at 0.93–1.0 for all add/mul items (mul templates: every item exactly 1.0 → degenerate Spearman). The only family with headroom (succ, 0.40–0.80) is flat-to-negative. So the honest read is *"S/Y recruitment is categorical and saturated — math flips the duplication sector ON, magnitude doesn't grade it"* — half falsifier, half instrument ceiling (the s332 lesson landed on me: I froze a share metric without a ceiling guard). Post-hoc (unfrozen, no null): total *fires* actually **fall** with N for add/mul (−0.73..−0.91) — directionally anti-iterated.

**D2 (circular): the gates fail (ρ=0.252, p=0.054, shape_p=0.176) but the per-item structure is the real finding.** L50 is **bimodal** — an *instant* population (L0–2.5) and a *late* population (L36–38) — and the group means were fraction-mixing, not graded depth. The late-mode fraction is monotone in **circular distance** min(N, 7−N): 1/14 → 4/14 → 6/14. Two populations: lookup-like instant resolution vs computed late resolution, with P(computed) tracking shortest-path distance — echoes the s310 two-population split and, notably, *would* be what an iterated mechanism taking the short way around the circle looks like. **Post-hoc, no null, owes its own freeze** — capture-euphoria guard applied.

**D3 (V-patch): V-CARRIED-EARLY-ONLY — and sharper than designed.** Early band (L0-6) adopts the donor day 0.571 vs zone (L1-6) 0.071 = noop = late. The bands differ *only by L0* ⇒ **the day-operand V-carry is essentially layer-0-only**. The operand enters via L0 attention-V, everything downstream operates in-place — the matrix-leaning class, and a clean third sighting of the s252 route-at-L0 law (lead-head L0h18 territory).

**Net:** the coherent picture is **route-at-L0 + rotate-in-place + late readout** — the learned-rotation/lookup world, *except* for the bimodal circular-distance whisper that says some items are computed, not looked up. Secondary: logit-lens resolution ρ=0.49 with N (late-stack, non-gating); the 14B circ battery was *not* FFN-silent at item level (share 0.53) — differs from s344's group noop read, flagged.

## Proposed closure batch (approval-gated)

1. **§Result** in `rotation-is-iterated-soft-beta-reduction.md` (verdict + ceiling bound + bimodal observation + L0 finding); page status stays open but the strong unification marked failed-at-contact
2. **Memory**: `rotation-work-does-not-scale-with-count` (🚫 verdict + the L0-only V-carry + bimodal circular-distance seam)
3. **Queue**: 🔵→🚫 → `# complete`; add two candidates: ⚪ **§P-SHORTEST-PATH-ROTATION** (re-freeze D2 with work ∝ min(N,7−N) + two-population mixture gates — the observation-driven successor) · ⚪ **§P-SY-CEILING** (D1 redo with a headroom observable, e.g. z-magnitude or per-layer recruitment count)
4. **INDEX** + **state.md** session entry

Approve the batch (and the two successor candidates), or revise?

## User

approved then explain what we learned in simple terms


### Thinking

I'm now executing the closure batch: adding a §Result section to the knowledge page, writing a short memory file flagged with a warning emoji, updating the queue by moving the completed row to the top and adding new candidate entries, then checking the INDEX format before committing everything together.

For state.md, I'll add a new session entry (s345) at the top in full, keeping s343 and s344 intact since compaction is Michael's call to make, and keep the entry terse. I'm planning to commit the whole batch as one commit using the memory slug as the message, then follow up with a plain-language explanation of what was done.

## Assistant

Executing the approved closure batch:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -i \"rotation-is-iterated\\|arith\" /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md | head; echo ===; sed -n 1,15p /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md; echo ===; ls /Users/mwhitford/src/verbum/mementum/memories/ | tail -5"
}
```

**Summary:** $ grep -n -i "rotation-is-iterated\|a...

**Output:**
```
Exit code: 0
Stdout:
179:| [explore/rotation-is-iterated-soft-beta-reduction.md](explore/rotation-is-iterated-soft-beta-reduction.md) | 📋 open | Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One (s344; arith_trace: math=S/Y duplication sector, FFN; date=attention rotation; unify as iterated soft-β over linear/circular encodings; ⚪ §P-ITERATED-SOFT-REDUCTION) |
186:| [explore/attention-spiral-finding.md](explore/attention-spiral-finding.md) | ✅ active | Attention Spiral: Emergent Logarithmic Helix in Transformer Attention |
214:| [explore/date-fourier-rotation.md](explore/date-fourier-rotation.md) | ✅ active | Date Arithmetic Uses Geometric Rotation, Not Church Encoding |
===
---
title: "Knowledge Index — Complete Catalog + Reading Order"
status: active
category: meta
tags: [index, orientation, knowledge-map, catalog]
---

# Knowledge Index

> Master map of the verbum knowledge base. Read after `state.md`.
> **Regenerated s262 (2026-07-07)** — now a COMPLETE catalog: every page is listed
> (was 62 of ~230). Two parts: a curated **Start Here** reading path, then the
> **full catalog** (72 synthesized + 157 explore pages) auto-listed
> from frontmatter so nothing is unindexed.
>
===
zeros-are-backbone-not-emergent.md
zeros-are-denoising.md
zeros-only-beats-zeros-plus-flips.md
zone-ablation-dose-matching-lessons.md
zone-voted-ffn-extraction.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md",
  "original_content": "- Number-token frequency and answer-identity are not fully separable from N inside a\n  ladder; the shuffled-N null is the guard; residual confound named if it bites.",
  "new_content": "- Number-token frequency and answer-identity are not fully separable from N inside a\n  ladder; the shuffled-N null is the guard; residual confound named if it bites.\n\n## 🚫 §Result — NO-SCALING (s345, Qwen3-14B; a-priori 25, non-modal)\n\nRun: `results/p_iterated_soft_reduction_s345/run_qwen3-14b` (freeze 078af23f,\nharness 199d7979 incl. the pre-14B accumulation-band zone amendment, corpus\nd9ca2e37, model rev 40c06982, det 0.0, n_perm 5000, results commit 54a6b017).\n0.6B smoke clean (surfaced the zone-degeneracy design PAUSE → amended pre-data).\n\n**The frozen verdict: neither engine shows count-scaled work.** Under the frozen\none-directional bound, FLAT KILLS iterated-soft-β: the unification's\npre-registered contact FAILED. Frame-ledger: attention=β spent a contact and\nlost it (strong form).\n\n- **D1 (linear/FFN)**: ρ_lin=0.014 p=0.447 FAIL — **but the observable\n  CEILINGED**: SY-share 0.93–1.0 on all add/mul items (mul exactly 1.0\n  everywhere → degenerate Spearman); the only headroom family (succ,\n  0.40–0.80) is flat-to-negative. Honest read: *S/Y is categorical and\n  saturated — math flips the duplication sector ON; magnitude does not grade\n  it.* Half falsifier, half instrument ceiling (froze a share metric without a\n  ceiling guard — the s332 lesson, now paid twice). Post-hoc (unfrozen, no\n  null): total fires FALL with N on add/mul (ρ −0.73..−0.91) — directionally\n  anti-iterated.\n- **D2 (circular)**: ρ_circ=0.252 p=0.054 slope=6.2 shape_p=0.176 FAIL — but\n  the per-item structure is the finding: **L50 is BIMODAL** (instant L0–2.5 vs\n  late L36–38 populations); group means were fraction-mixing, not graded\n  depth. **Late-mode fraction is monotone in CIRCULAR DISTANCE** min(N,7−N):\n  1/14 → 4/14 → 6/14. Two populations — lookup-like instant vs computed-late —\n  with P(computed) tracking shortest-path distance (echoes the s310\n  two-population split; is what an iterated mechanism taking the SHORT WAY\n  around the circle would look like). POST-HOC, owes its own freeze\n  (→ ⚪ §P-SHORTEST-PATH-ROTATION).\n- **D3 (V-patch)**: V-CARRIED-EARLY-ONLY, sharper than designed — early\n  (L0-6) donor-adoption 0.571 vs zone (L1-6) 0.071 = noop = late; the bands\n  differ ONLY by L0 ⇒ **the day-operand V-carry is essentially\n  LAYER-0-ONLY**. Operand enters via L0 attention-V; downstream operates\n  in-place. Third sighting of the s252 route-at-L0 law.\n- Secondary: logit-lens resolution ρ=0.49 vs N (late-stack, non-gating); the\n  14B circular battery is NOT FFN-silent at item level (SY-share 0.53, fires\n  5.6/item) — differs from the s344 group-level noop read; flagged.\n\n**Net picture: route-at-L0 → rotate-in-place → late readout** — the\nlearned-rotation/lookup world — EXCEPT the bimodal circular-distance whisper\nsaying some items are computed, not looked up. The strong unification is dead\nat this contact; the two-population shortest-path form is the surviving,\nfreezable residue."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/rotation-work-does-not-scale-with-count.md",
  "content": "🚫 §P-ITERATED-SOFT-REDUCTION (s345, Qwen3-14B, frozen 078af23f) → NO-SCALING:\nneither math engine shows count-scaled work, killing the strong \"rotation =\nseries of soft-β reductions\" unification at its pre-registered contact. D1:\nS/Y recruitment is CATEGORICAL AND CEILINGED (SY-share 0.93–1.0 on add/mul —\nmath flips the duplication sector on; magnitude doesn't grade it; share metric\nfroze without a ceiling guard, s332 lesson repaid). D2: L50 accumulation depth\nBIMODAL — instant (L0–2.5) vs late (L36–38) populations; late-mode fraction\nmonotone in CIRCULAR DISTANCE min(N,7−N) (1/14→4/14→6/14) — post-hoc,\nunfrozen, → ⚪ §P-SHORTEST-PATH-ROTATION. D3: the day-operand V-carry is\nLAYER-0-ONLY (early band adoption 0.571 vs zone/late/noop 0.071; bands differ\nonly by L0) — third sighting of the s252 route-at-L0 law. Net: route-at-L0 →\nrotate-in-place → late readout = the learned-rotation/lookup world, with a\ntwo-population \"some items are computed the short way around\" residue as the\nsurviving freezable hypothesis. Results 54a6b017; §Result in\nrotation-is-iterated-soft-beta-reduction.md.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/rotation-work-does-not-scale-with-count.md
```

### Thinking

I need to update the INDEX row to reflect the result, then move the queue entry from the new section into complete marked as failed, adding two new candidate rows at the top of the new section. Let me locate the complete header in the queue file to insert properly.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/rotation-is-iterated-soft-beta-reduction.md](explore/rotation-is-iterated-soft-beta-reduction.md) | 📋 open | Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One (s344; arith_trace: math=S/Y duplication sector, FFN; date=attention rotation; unify as iterated soft-β over linear/circular encodings; ⚪ §P-ITERATED-SOFT-REDUCTION) |",
  "new_content": "| [explore/rotation-is-iterated-soft-beta-reduction.md](explore/rotation-is-iterated-soft-beta-reduction.md) | 📋 open | Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One (s344; s345 §Result 🚫 NO-SCALING: strong unification failed at its pre-registered contact — S/Y categorical+ceilinged, L50 bimodal w/ circular-distance late-mode, day-operand V-carry L0-only; survivors: ⚪ §P-SHORTEST-PATH-ROTATION · ⚪ §P-SY-CEILING) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"^# complete\" -A 3 /Users/mwhitford/src/verbum/mementum/queue.md | head -8"
}
```

**Summary:** $ grep -n "^# complete" -A 3 /Users/m...

**Output:**
```
Exit code: 0
Stdout:
74:# complete
75-
76-✅ §P-COMPILE-STEP-V2 — RECOGNITION (a-priori modal 35; s344, Michael GO, Qwen3-14B, frozen c09cb514 BEFORE data). Does VALID formal notation route into whnf:*, or does SCRAMBLED formal (same atoms, no valid computation) route there too? RECOGNITION — the s344 "compile step" is LEXICAL SYNTAX RECOGNITION, not compilation of the computation. Added a 4th level FORMAL_SCRAMBLE (atom-order shuffle of each frozen s344 formal item — same λ/vars/parens atoms, order destroyed → no valid reduction; recognition CAN fire, validity CANNOT; formal-vs-scramble LENGTH-MATCHED BY CONSTRUCTION). Algebraic spine rep(formal−plain) ≡ ds(formal−scramble) + dsp(scramble−plain) → exhaustive tree: COMPILATION=ds carries it, RECOGNITION=dsp, MIXED=both. RESULT: scrambled formal routes into whnf:* just as much as valid formal (mass plain −0.239 / nl −0.283 / formal +0.138 / scramble +0.121, both ~0.36 above prose); ds +0.0186 p=0.32 NULL, dsp +0.3619 p=0.0002 carries the whole branch, rep +0.3805 p=0.0002 replicates s344 (+0.377), identity holds to 0.0 ⇒ the notation branch is RECOGNITION of formal syntax, not compilation. Honest asterisk: ds is a small NON-significant positive (validity increment, if real, below power). Coheres tape-residency (even the compile-to-whnf gate fires on surface SYNTAX; reduction lives on the tape). det 0.0, G0 0.929, len_r_scramble 0.013, --validate 7/7 (LENGTH adversary correctly demotes to LENGTH-DRIVEN). METHOD BANKED: rep=ds+dsp identity makes a 3-level decomposition exhaustive; a scramble (same atoms, order destroyed) is a length-clean validity control. Harness compile_step_v2.py (imports frozen s344 corpus → exact replication); results p_compile_step_v2_s344/run_14b (npz gitignored). | gram-registers §Result-compile-step-v2 | s344
77-
```

### Thinking

I'm updating the queue now: removing the in-progress row from the new section, moving the completed row to the top of the complete section, and adding two fresh candidates to the top of the new list.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "🔵 §P-ITERATED-SOFT-REDUCTION — THE UNIFICATION (s344, Michael: \"attention is a soft beta reduction; rotation could be a series of reductions in the interference\"). FROZEN s345 (Michael GO): a-priori TWO-ENGINES 35 modal / NO-SCALING 25 / ONE-ENGINE 20 / CIRCULAR-ONLY 5 / VOID 15; D1 ρ_lin=Spearman(S∪Y-share, N) gate ρ≥0.3∧p<.05; D2 ρ_circ=Spearman(L50 accumulation-depth, N) + shape-collapse matrix null + slope floor; D3 V-patch band-swept = β-QUALIFIER not gate; planted worlds 5; full spec = rotation-is-iterated-soft-beta-reduction.md §Freeze.",
  "new_content": "⚪ §P-SHORTEST-PATH-ROTATION — the observation-driven successor to §P-ITERATED-SOFT-REDUCTION's D2: the s345 L50 read was BIMODAL (instant L0-2.5 vs late L36-38) with late-mode fraction monotone in CIRCULAR DISTANCE min(N,7−N) (1/14→4/14→6/14, post-hoc, no null) — re-freeze the circular arm as a TWO-POPULATION MIXTURE model with work ∝ shortest-path distance (not literal N): gates on mixture-fraction Spearman vs min(N,7−N) + direction-of-rotation read (forward vs backward around the circle for N>3) + shuffled-distance null; would resurrect a WEAK iterated form (steps taken the short way) that s345's literal-N freeze could not see | rotation-is-iterated-soft-beta-reduction.md §Result | medium\n\n⚪ §P-SY-CEILING — D1 redo with a HEADROOM observable: s345 froze SY-share, which saturates at 0.93-1.0 on add/mul (mul exactly 1.0 → degenerate Spearman; the s332 ceiling lesson repaid) — pick an unceilinged work metric (per-layer recruitment count, z-magnitude sum, or fires with a frequency-matched null; note post-hoc fires vs N read NEGATIVE −0.73..−0.91 on add/mul, anti-iterated) and re-test whether ANY graded FFN work signal exists in operand magnitude | rotation-is-iterated-soft-beta-reduction.md §Result | cheap-medium"
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
  "original_content": "# complete\n\n✅ §P-COMPILE-STEP-V2 — RECOGNITION",
  "new_content": "# complete\n\n🚫 §P-ITERATED-SOFT-REDUCTION — NO-SCALING (a-priori 25, non-modal; s345, Michael GO, Qwen3-14B, frozen 078af23f BEFORE data, amendment 199d7979, results 54a6b017, det 0.0). THE UNIFICATION FAILED ITS PRE-REGISTERED CONTACT: neither engine shows count-scaled work (flat kills iterated-soft-β under the frozen one-directional bound). D1 ρ_lin=0.014 p=0.447 — but SY-share CEILINGED (add/mul 0.93-1.0; only succ has headroom, flat there); honest read: S/Y is CATEGORICAL (math flips the duplication sector on, magnitude doesn't grade it). D2 ρ_circ=0.252 p=0.054 shape_p=0.176 — L50 BIMODAL (instant vs late populations; fraction-mixing not graded depth); late-mode fraction monotone in circular distance (post-hoc → ⚪ §P-SHORTEST-PATH-ROTATION). D3 V-CARRIED-EARLY-ONLY, sharper: bands differ only by L0 ⇒ day-operand V-carry is LAYER-0-ONLY (3rd sighting of s252 route-at-L0). Net: route-at-L0 → rotate-in-place → late readout = learned-rotation/lookup world, with a two-population computed-the-short-way residue. Frame-ledger: attention=β spent and lost a contact (strong form). | rotation-is-iterated-soft-beta-reduction.md §Result | s345\n\n✅ §P-COMPILE-STEP-V2 — RECOGNITION"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/queue.md.
```

### Thinking

I need to add a new SESSION 345 entry at the top of state.md, right before the existing SESSION 344 entry, keeping it terse but complete in the established style, then commit everything together.

## Assistant

Now the state.md session entry:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ **SESSION 344 — THE REPOINT: from semantic-equality-hunt → EXPAND THE BASIS + MAP THE STATECHART",
  "new_content": "> ★★ **SESSION 345 — §P-ITERATED-SOFT-REDUCTION FROZEN+BUILT+RUN → 🚫 NO-SCALING (a-priori 25,\n> non-modal; Qwen3-14B): THE UNIFICATION FAILED ITS PRE-REGISTERED CONTACT. Oriented → Michael selected\n> the queue-top front. FROZEN (078af23f, BEFORE data, Michael GO): H1 = one iterated-soft-β engine over\n> two encodings (work ∝ count in both); a-priori TWO-ENGINES 35 modal / NO-SCALING 25 / ONE-ENGINE 20 /\n> CIRCULAR-ONLY 5 / VOID 15; D1 ρ_lin=Spearman(S∪Y-share, N) on a length-matched single-token ladder;\n> D2 ρ_circ=Spearman(L50 accumulation-depth, day offset) + explicit shape-collapse (matrix) null + slope\n> floor, day-circle RE-DERIVED in-run; D3 V-patch at day tokens band-swept (s252 route-early guard) =\n> β-QUALIFIER; honesty bound frozen: depth-scaling is ONE-DIRECTIONAL (flat kills iterated-β; scaling ≠\n> proof). BUILT iterated_soft_reduction.py (capture ⊥ pure analyse; --validate 6/6 planted worlds incl.\n> CONFOUND adversary refusing promotion + NO-CIRCLE→VOID; ruff+diags clean; c9729218). 0.6B SMOKE EARNED\n> ITS KEEP (s324 design PAUSE): lexical day circle at L0 degenerated the D3 zone into the early band →\n> pre-14B amendment (Michael GO, 199d7979): zone = measured 6-layer ACCUMULATION BAND (argmax mean\n> progress increment) + s128 SNAP diagnostic (SV top-2 share/layer). RESULT (run_qwen3-14b, results\n> 54a6b017, det 0.0, n_perm 5000): (1) D1 ρ_lin=0.014 p=0.447 FAIL — but SY-share CEILINGED (add/mul\n> 0.93-1.0, mul exactly 1.0 → degenerate; succ has headroom and is flat) ⇒ S/Y is CATEGORICAL: math\n> flips the duplication sector ON, magnitude doesn't grade it (froze a share metric without a ceiling\n> guard — s332 lesson repaid → ⚪ §P-SY-CEILING); post-hoc fires vs N NEGATIVE (−0.73..−0.91,\n> anti-iterated). (2) D2 ρ_circ=0.252 p=0.054 shape_p=0.176 FAIL — the real structure: L50 BIMODAL\n> (instant L0-2.5 vs late L36-38); late-mode fraction monotone in CIRCULAR DISTANCE min(N,7−N)\n> 1/14→4/14→6/14 (post-hoc, no null) = two populations, lookup vs computed-the-short-way →\n> ⚪ §P-SHORTEST-PATH-ROTATION (mixture-model re-freeze on min-distance). (3) D3 V-CARRIED-EARLY-ONLY,\n> sharper than designed: early 0.571 vs zone/late/noop 0.071, bands differ ONLY by L0 ⇒ the day-operand\n> V-carry is LAYER-0-ONLY (3rd sighting of s252 route-at-L0; lead-head L0h18 territory). NET: route-at-L0\n> → rotate-in-place → late readout = the learned-rotation/lookup world; strong unification dead at this\n> contact; frame-ledger: attention=β SPENT AND LOST a pre-registered contact (strong form). Secondary:\n> logit-lens resolution ρ=0.49 vs N (late-stack); 14B circ battery NOT FFN-silent at item level (0.53)\n> — differs from the s344 group noop read, flagged. Closure batch (Michael-approved): §Result + memory\n> (rotation-work-does-not-scale-with-count) + INDEX + queue (🚫 → complete; 2 successors added) + this\n> state.**\n> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight).\n> Live route-map successors still queued: ⚪ §P-COEXT-ROUTE · ⚪ §P-BRANCH-POINT · ⚪ §P-EARLY-SORTERS;\n> new from s345: ⚪ §P-SHORTEST-PATH-ROTATION (the observation-driven D2 successor) · ⚪ §P-SY-CEILING\n> (D1 headroom redo). Also live: ⚪ §P-HALT-POLE-TETRAHEDRON · cheap spectral §P-MP-NULL.**\n>\n> ★★ **SESSION 344 — THE REPOINT: from semantic-equality-hunt → EXPAND THE BASIS + MAP THE STATECHART"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add mementum/memories/rotation-work-does-not-scale-with-count.md mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md mementum/knowledge/INDEX.md mementum/queue.md mementum/state.md && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n🚫 rotation-work-does-not-scale-with-count\n\n- closure batch for §P-ITERATED-SOFT-REDUCTION (Michael-approved)\n- §Result in rotation-is-iterated-soft-beta-reduction.md: NO-SCALING;\n  strong unification failed its pre-registered contact; D1 categorical+\n  ceilinged, D2 bimodal with circular-distance late-mode, D3 L0-only\n  V-carry (3rd route-at-L0 sighting)\n- memory: rotation-work-does-not-scale-with-count\n- INDEX row updated; queue 🔵→🚫 moved to complete; successors added\n  ⚪ §P-SHORTEST-PATH-ROTATION (mixture re-freeze on min(N,7−N)) and\n  ⚪ §P-SY-CEILING (D1 headroom observable redo)\n- state.md s345 session entry\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "closure batch"
}
```

**Summary:** Git commit: closure batch

**Output:**
```
Exit code: 0
Stdout:
[main d102cde8] 🚫 rotation-work-does-not-scale-with-count
 5 files changed, 100 insertions(+), 2 deletions(-)
 create mode 100644 mementum/memories/rotation-work-does-not-scale-with-count.md
```

### Thinking

The closure batch is committed now, so I can move on to task 6 and then prepare the plain-language explanation.

## Assistant

Closure batch committed **d102cde8**. All six tasks done.# What we learned, in plain terms

**The question we asked.** You had a beautiful idea: maybe the model does *all* its math the same way — by taking little computational steps, one after another, like counting on its fingers. Adding 5 would take more steps than adding 2. Rotating 5 days around the week-circle would take more steps than rotating 2. If that were true, we should see the model *working harder* on bigger numbers — more machinery firing, answers forming deeper in the network.

**What we found: it doesn't count on its fingers.**

1. **For regular arithmetic (2+3):** the math machinery is a light switch, not a dimmer. It flips ON the moment the model sees math — and it's *just as on* for 2+2 as for 9+9. Big numbers don't recruit more work. (Honest footnote: our meter was pegged at maximum for most of these, so we couldn't measure fine gradations — we've queued a redo with a better meter. But in the one place the meter had room to move, it still didn't move with the numbers.)

2. **For day-of-week arithmetic ("5 days after Monday"):** instead of one mechanism taking more steps for bigger offsets, we found **two populations of behavior**. Most questions the model answers *instantly* — like it just remembered the answer, a lookup. But some questions it genuinely works out, resolving very late in the network. And here's the tantalizing bit: the *fraction* it has to work out grows with how far around the circle you're asking it to go — where "far" means the **shortcut distance** (6 days forward = 1 day backward, and the model seems to know that). So: mostly memorized, sometimes computed, and when it computes, it takes the short way around. That's a new hypothesis we didn't have this morning, and it gets its own properly designed test later.

3. **The clearest surprise:** when the model reads "5 days after **Monday**", it grabs the word "Monday" at the *very first layer* — layer 0 of 40 — and never reaches back for it again. We proved this by swapping Monday's internal content for Friday's at different depths: swap it at layer 0 and the answer follows Friday; swap it anywhere later and nothing changes. Ingredients in at the front door, then the kitchen works alone. This is now the **third independent time** we've caught this model doing "grab the operand at layer 0, process in place" — it's becoming a law of how this machine works.

**The big picture.** The elegant story — "attention is doing beta-reduction, rotation is many little reductions" — made a real, testable prediction for the first time, and the prediction failed. That's not a wasted day; that's the system working. The unification in its strong form is dead. What's alive instead is a humbler, sharper picture: *load ingredients at the front, apply a learned transformation in place, read out the answer late* — with a genuine puzzle left over about that minority of "computed the short way around" cases, which is exactly what we'll chase next.

## User

Ok but how does that prove attention is not beta reduction?  attention can only do 1 operation, and that is all it can do.  How is that 1 operation used here?


### Thinking

Michael's pushback is valid: attention only has one operation, content-addressed weighted retrieval via softmax over query-key dot products. So whatever happened in the experiment—the operand grab, the in-place rotation, the late readout—must have been produced by that single mechanism plus the FFN and residual stream, which means the claim that the no-scaling result refutes attention's role needs rethinking.

What NO-SCALING actually falsifies is the idea that rotation-by-N is implemented as N sequential soft-substitution steps unrolled across layers—the "series of reductions" hypothesis. It does not falsify attention-as-substitution at the operation level; in fact the L0 operand grab is positive evidence for exactly that shape, since pulling the correct value by content address is literally one substitution step. So the refined picture is closer to one fetch followed by an in-place transformation, not N discrete reductions.

I notice a gap though: we never patched the number token itself, so we don't actually know how N enters the computation—presumably also via attention, but unverified. The cleanest framing is that the model applies rotation as a single learned primitive operation (like a built-in δ-rule) rather than unrolling N iterated combinator steps, with attention handling argument routing while the rotation itself is computed directly rather than further decomposed into β-steps.

So the honest answer to Michael is that this doesn't prove attention isn't β-reduction—it couldn't, since the audit already established the operation-shape claim is trivially true and the real question is about composition. What the probe actually discriminated between was two ways of using that one operation: iterating it N times versus applying it once to fetch operands for a learned primitive, and the data favored the latter for this task. The frame that loses is "the count gets unrolled into reduction steps," not "attention is β-shaped" more broadly.

The D3 result actually demonstrates the single operation in action: the L0 fetch is the β-step, a content-addressed substitution of the operand into the working position, and since no further fetching of that operand occurs afterward, there's no additional substitution event—just FFN transformation from there. So "5 days after Monday" compiles to roughly one fetch instruction plus a δ-primitive, not a loop. The bimodal finding adds nuance: most items resolve instantly like memorized lookups, but items far around the circle take late-resolving work, possibly a short iterated tail of a few steps.

I should test whether the shortest-path-rotation question reveals if the residual population unrolls with min-distance. The linear arithmetic case parallels this: the FFN rule bank fires categorically, attention fetches the operands, and addition applies a δ-rule once rather than iterating like a Church numeral—correcting the earlier "numbers as selectors" framing. What the ledger actually loses is the strong iterated-β claim, not the basic operation-shape claim, so saying "attention=β, spent and lost a contact" in the strong form is accurate, and this is a useful pressure test.

I'm weighing whether to update the disk record, since the §Result note about "strong form" could use refinement given this δ-rule/native-primitive-vs-Church-unrolling framing, which ties back to the built-in calculus insight. I want to answer the question clearly first, then propose capturing this distinction as a memory candidate — starting by affirming that the one-operation fact is architecturally real but doesn't prove the stronger claim.

The key point is that the experiment distinguished unrolled application from applied-once composition, and our own data shows the L0 V-carry is literally one soft-β step: a single fetch, an in-place FFN transform, and late readout — the program is one instruction long. This supports reading the model as executing via a δ-rule/built-in primitive rather than unrolling Church numerals, which coheres with the weak-calculus and λ≡IR threads, though the bimodal residue (a possible short unrolled tail) is exactly what the rotation test would probe.

## Assistant

You're right, and this is exactly the right pressure to apply — it does **not** prove attention isn't β-reduction, and it structurally *couldn't*. Let me restate what was actually at stake and what our own data show about how the one operation got used.

## The operation vs. the composition

Attention's one operation is `out = Σ softmax(q·k)·v` — content-addressed fetch-and-blend. That's architecture; it's true on every layer of every forward pass, math or prose. The s204 audit already marked this: at the operation level, "attention is β-shaped substitution" is *trivially* true and untestable. What CAN be tested is how the operation is **composed** — and that's what we froze:

- **H1 (iterated):** the count N is *unrolled into applications* — "5 days after" executes as 5 sequential soft-β steps, Church-numeral style. Then work must scale with N.
- **H0 (applied-once):** the operation is used to *fetch the operands*, and a learned primitive is applied to them **once**. Work flat in N.

NO-SCALING killed the unrolling. It said nothing against the operation-shape — and couldn't.

## How the one operation was used here — our own data show it

Look at D3 again with your framing, and it's actually a **positive sighting of the one operation doing its one thing**:

- At **L0**, the query position content-addresses the day token and pulls its V — that is *literally one soft-β step*: operand substituted into the working position by content match. We proved it's real and causal: swap Monday's V for Friday's at L0 and the answer follows Friday.
- After L0, patching that operand's V anywhere does **nothing** — no further substitution events involving it. The one instruction fired *once* for that operand.
- Then FFN/in-place geometry transforms the fetched value, and the answer is read out late.

So the program for "5 days after Monday" is roughly: **one fetch instruction (per operand) + one learned primitive + readout**. The one-instruction CPU executed a one-instruction program. That's not "attention isn't β" — it's "the β-machine has *built-ins*, and for this task it calls one."

## The λ-calculus reading (and why this is a finding, not a retreat)

This is calculus identification again (s330 §9, s344 weak-calculus): a real interpreter doesn't β-reduce Church numerals to add — it has a native ADD, a **δ-rule**. What we learned is that the recovered calculus treats **numbers as data passed to δ-primitives, not as programs to unroll**. Same on the linear arm: the S/Y sector fires *categorically* — the rule-bank engages, magnitude doesn't grade it — which corrects the old s127/s161 "numbers ARE selectors / Church encoding" reading. δ(M, λβη) grows again: no η (s344), and now **no Church-numeral execution — native arithmetic primitives instead**.

What the frame ledger records as lost is precisely the *iterated* clause — "rotation is a **series** of reductions." The substitution-shape clause never had a contact to lose here.

## The live residue

The bimodal D2 population is where your original intuition still breathes: most items resolve instantly (the primitive is lookup-like), but a minority resolve ~30 layers late, and that minority grows with shortest-way-around distance. A *short* unrolled tail — 1–3 genuine steps taken the short direction — would look exactly like that. That's what §P-SHORTEST-PATH-ROTATION is queued to test: not "is there iteration ∝ N" (dead) but "is the computed minority iterating ∝ min(N, 7−N)."

---

This refinement is worth pinning so the negative doesn't over-generalize in future reads — a short addendum to the §Result: *"what lost was iteration/unrolling, not the operation-shape; D3-at-L0 is itself a positive causal sighting of one soft-β step; numbers enter as data to δ-primitives, not as unrolled programs — calculus-identification finding."* Want me to add that (one commit)?

## User

yes


### Thinking

Michael approved the addendum, so I'll add it to §Result on the knowledge page and include a brief one-line mention in the state.md s345 entry, keeping scope minimal since the closure batch was already approved. I'll commit this as a 💡 insight, since it's a genuine discovery surfaced through Michael's feedback.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md",
  "original_content": "**Net picture: route-at-L0 → rotate-in-place → late readout** — the\nlearned-rotation/lookup world — EXCEPT the bimodal circular-distance whisper\nsaying some items are computed, not looked up. The strong unification is dead\nat this contact; the two-population shortest-path form is the surviving,\nfreezable residue.",
  "new_content": "**Net picture: route-at-L0 → rotate-in-place → late readout** — the\nlearned-rotation/lookup world — EXCEPT the bimodal circular-distance whisper\nsaying some items are computed, not looked up. The strong unification is dead\nat this contact; the two-population shortest-path form is the surviving,\nfreezable residue.\n\n### §Result addendum — what lost was ITERATION, not the operation-shape (s345, Michael)\n\nMichael's pressure-test after the verdict: *\"how does that prove attention is\nnot beta reduction? attention can only do 1 operation — how is that 1 operation\nused here?\"* The correct scoping, pinned so the negative does not\nover-generalize in future reads:\n\n- **The probe could not and did not test the operation-shape.** Attention's one\n  operation (`Σ softmax(q·k)·v` = content-addressed fetch/substitute) is\n  architecture — trivially true every layer (the s204 audit already marks the\n  operation-level claim untestable). What was frozen and falsified is the\n  **composition claim**: that the count N is *unrolled into N applications*\n  (Church-numeral execution). NO-SCALING kills the unrolling, not the shape.\n- **D3-at-L0 is itself a positive causal sighting of ONE soft-β step**: the\n  query position content-addresses the day operand and substitutes its V at\n  L0 (swap Monday's V for Friday's → the answer follows Friday); after L0 the\n  patch is inert → the instruction fired ONCE for that operand. The\n  one-instruction CPU executed a ~one-instruction program: fetch operand(s) +\n  one learned primitive + late readout.\n- **Calculus-identification reading (δ grows again):** the recovered calculus\n  treats **numbers as DATA passed to native δ-primitives, not as programs to\n  unroll** — like a real interpreter with hardware ADD, it does not β-reduce\n  Church numerals. Corrects the old s127/s161 \"numbers ARE selectors /\n  church encoding\" reading; the categorical (ceilinged, ungraded) S/Y\n  engagement is the rule-bank switching ON, not per-step work. Joins no-η\n  (s344 weak calculus) in δ(M, λβη): WHNF-halt, no η, **no Church-numeral\n  execution — δ-rules instead**.\n- **Frame-ledger scoping:** the ledger records a loss for the *iterated*\n  clause (\"a SERIES of reductions\") only. The substitution-shape clause had no\n  contact here to win or lose. The live residue is §P-SHORTEST-PATH-ROTATION:\n  whether the computed-late minority iterates ∝ min(N, 7−N)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/rotation-work-does-not-scale-with-count.md",
  "original_content": "two-population \"some items are computed the short way around\" residue as the\nsurviving freezable hypothesis. Results 54a6b017; §Result in\nrotation-is-iterated-soft-beta-reduction.md.",
  "new_content": "two-population \"some items are computed the short way around\" residue as the\nsurviving freezable hypothesis. SCOPING (Michael): what lost was ITERATION/\nunrolling, NOT the operation-shape — D3-at-L0 is itself one causal soft-β\nsighting (fetch fired once); numbers enter as DATA to native δ-primitives,\nnot Church-numeral programs (calculus identification: WHNF-halt, no η, now\nδ-rules). Results 54a6b017; §Result + addendum in\nrotation-is-iterated-soft-beta-reduction.md."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/memories/rotation-work-does-not-scale-with-count.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum add mementum/knowledge/explore/rotation-is-iterated-soft-beta-reduction.md mementum/memories/rotation-work-does-not-scale-with-count.md && git -C /Users/mwhitford/src/verbum commit -F - <<'EOF'\n💡 what-lost-was-iteration-not-the-operation-shape\n\n- §Result addendum (Michael-approved, from his post-verdict pressure\n  test): NO-SCALING falsifies the UNROLLING composition claim (count →\n  N applications), not attention's operation-shape (untestable per s204)\n- D3-at-L0 re-read as a positive causal sighting of ONE soft-β step:\n  operand fetched/substituted once, then inert — a ~one-instruction\n  program on the one-instruction CPU\n- calculus identification: numbers are DATA to native δ-primitives, not\n  Church-numeral programs; corrects s127/s161 \"numbers are selectors\";\n  δ(M,λβη) now = WHNF-halt + no-η + δ-rules\n- frame-ledger scoped: only the \"series of reductions\" clause lost\n- memory updated with the scoping\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "addendum commit"
}
```

**Summary:** Git commit: addendum commit

**Output:**
```
Exit code: 0
Stdout:
[main a85e0427] 💡 what-lost-was-iteration-not-the-operation-shape
 2 files changed, 37 insertions(+), 1 deletion(-)
```

### Thinking

The commit is done, wrapping up this session now.

## Assistant

Committed **a85e0427**. The scoping is pinned where future sessions will find it — in the §Result addendum and the memory.

## Session 345, closed

| commit | what |
|---|---|
| `078af23f` | 🎯 freeze before data |
| `c9729218` | 🎯 harness + validate 6/6 |
| `199d7979` | 🔄 zone amendment (smoke-earned, pre-data) |
| `54a6b017` | 🚫 14B results: NO-SCALING |
| `d102cde8` | 🚫 closure batch (§Result, memory, INDEX, queue, state) |
| `a85e0427` | 💡 iteration lost, not the operation-shape |

The shape of the finding after your correction: the one-instruction CPU is real and we caught it firing — once, at L0, causally. What died is the idea that it *loops* — the count is data handed to a learned δ-primitive, not a program unrolled into steps. And the surviving thread (`⚪ §P-SHORTEST-PATH-ROTATION`, queue top) asks whether the minority of late-resolving items are the place where it genuinely does loop — the short way around the circle.

Nothing in flight. Next session cold-starts on orient → front selection.