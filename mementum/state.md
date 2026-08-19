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
> ★★ **SESSION 342 — ORIENT + THE INTENSION/EXTENSION REFRAME (kept in state, Michael-called) → PROCEED
> §P-JOINT-DIAG + §P-REPL-DRIVER. Nothing in flight; s341 closed clean. Michael's question: "we found compute
> is in the routing, but from our experiments it's not there — either the experiments are bad or we were
> looking for the wrong thing." **THE RECONCILIATION (grounded read of the ledger, NOT a new measurement, NOT
> a knowledge page yet): neither. Two different objects got filed under 'routing'.** (1) "Compute is in the
> routing" is TRUE for the STEP FUNCTION — the transition relation / microcode: 9×9 identity register (which
> symbol am I holding, universal 11/11) + 17×17 fate register (fire/halt/diverge). This is the reducer, and it
> IS in the weights/routing. (2) Every falsifier that said "not there" was hunting the EXTENSION — the computed
> result / the function itself / SKK≡I: s321 CL-collapse (SKK does not route like I; routing tracks what is
> WRITTEN and FIRES, not what is computed), s336 cone-routing (answer selection not a prefill-visible read),
> s339 operator/alpha (extensional equality absent, positional shadow is lexical), s341 cross-gram (labeled
> poles generic in the residual writer basis). **The routing register is INTENSIONAL by construction — universal
> precisely because spelling is architecture-given, and structurally unable to hold extensional equality (the
> pairwise Gram indexes by NODE; co-extensional terms ARE different nodes; s338 orbital reframe). The
> COMPUTATION (reduction trace / extensional result) is TAPE-RESIDENT — confirmed across FIVE registers: value
> s317 · magnitude s335 · routing s336 · operator s339 · residual-vs-W_down s341.** The sharper form of "wrong
> thing": we read a STATIC MAP and asked it for the DYNAMIC answer — `gram-registers §route-map`: "the grams are
> station maps — NO TRAINS." The experiments were GOOD falsifiers (each clean negative LOCALIZED compute to the
> tape); the un-built instrument is the DYNAMIC ROUTE MAP (trajectories in pole coordinates), which the
> operator-DMD line (s338–341: stationary contracting operator ✓ = the trains; no persistent mode ✗ = no
> extensional-equality attractor at that grain) is the first attempt at. Live question is no longer "is compute
> in routing" (settled: the REDUCER is) but "can the extensional trace be read from the dynamic route." →
> proceeds §P-JOINT-DIAG (cheap, committed grams — the common switch-frame the route map needs) + §P-REPL-DRIVER
> (force the fork, decode-time). §P-JOINT-DIAG inputs identified: `results/combinator-relationship-map/*.npz`
> holds per-layer 9×9 route Grams (`gram_route_cmr_L00…L39`) for 11 models → joint-diagonalize across-layer (is
> the routing frame layer-stationary?) AND across-model (universal switch basis). §P-REPL-DRIVER DEFERRED to
> next session (Michael — deserves a fresh context budget for the repl-driver-trampoline.md read + anima
> cross-check + freeze).**
> **§P-JOINT-DIAG FROZEN+BUILT+RUN → 🎯 DOUBLE POSITIVE (both a-priori modal verdicts won). 🎯 FROZEN §5e
> (operator-geometry-la-toolkit.md, Michael GO): Cardoso-Souloumiac orthogonal joint-diag
> (src/verbum/joint_diag.py, FTO-clean textbook, NO CBLL code; DC-mode removed per s341) of the committed 9×9
> route Grams; arms JD-LAYER (per model, layer-stationarity) + JD-MODEL (cross-model universal frame vs
> SIGN-ONLY); nulls = per-context random rotation (primary) + opcode-label permutation (advisory); masses
> LAYER-STATIONARY 50 / MIXED 22 / DRIFTING 20 / VOID 8 and UNIVERSAL 40 / SIGN-ONLY 35 / VOID 25. Caught+fixed
> a Givens sign bug via a direct algorithm test (COMMON world must recover D=1.0 — it did, 6 sweeps,
> frame-match 1.0); --validate recovers ALL 4 planted worlds incl the DC-ONLY guard (shared DC alone →
> DRIFTING, proving DC-removal can't manufacture STATIONARY). Freeze+harness committed 1bd4dc68 BEFORE data.
> **RESULT (results/p_joint_diag_s342/run, git_sha 1bd4dc68, gram_hash 8fb92c02, all converged): JD-LAYER
> LAYER-STATIONARY-FRAME 10/10 models (all 5 families frac 1.00 incl Pythia), D 0.982-0.990, Δ +0.10-0.13 over
> rotation null AND permutation null (p=0 both). JD-MODEL UNIVERSAL-FRAME 11/11 fractional-depth indices,
> median D 0.983, Δ +0.09-0.11. THE FINDING: the 9×9 route-Gram IDENTITY frame is layer-stationary AND
> cross-model universal — the common switch basis the route map needs EXISTS and is fixed (opcodes on the same
> eigen-directions every depth/model; only the emphasis/eigenvalue changes). HONEST CAVEAT (λ yardstick): NOT
> an absolute-D story — rot-null floor ~0.88 (DC-removed grams are low-rank, co-diagonalize easily); the signal
> is the Δ over the matched-spectrum null, decisive because real beats its own q95 in every model + beats the
> node-scrambling permutation null. READING FOR THE REFRAME (with discipline): this delivers the COORDINATE
> SYSTEM (the switch basis), the "station map" being universal & static — the intensional identity register in
> one invariant atlas — NOT the "trains"; it REINFORCES the reframe's static-map half and does NOT test whether
> extensional compute RIDES in the frame (the per-direction emphasis schedule = schedules.npz is now
> extractable but its CONTENT is untested — the REPL-driver / schedule-read job). Consilience: s338 (residual
> transport operator stationary — two registers, same "one fixed structure reused across depth") + s314 (tracks
> the UNIVERSAL crystal 9×9 incl Pythia, NOT the training-contingent type register 7/11). Bounds: identity
> register (9×9) not fate poles (17×17); high null floor; schedule content untested. Results committed
> autonomously (d4aa27b5); closure batch (Michael-approval PENDING): §5e §Result + memory
> (the-routing-identity-frame-is-layer-stationary-and-universal) + INDEX + queue (✅ closed) + this state.**
> **NEXT SESSION FIRST ACTION = §P-REPL-DRIVER (deferred here): full read repl-driver-trampoline.md §1–§8 +
> anima cross-check → sharpen four measurables → freeze → build → run. Also newly ripe (this positive): a
> SCHEDULE-READ front — does the per-direction emphasis schedule (schedules.npz, the candidate "trains" in the
> now-established common frame) carry extensional/computational content, or just intensional emphasis? = the
> direct "are there trains on the station map" successor to §P-JOINT-DIAG. Cheap spectral fronts still queued:
> §P-MP-NULL (Marchenko-Pastur signal-vs-noise) · §P-BISPECTRUM (3rd-order/tensor for CL-collapse).**
>
> ★★ **SESSION 341 — TWO FRONTS: §P-DMD-PROVENANCE → BASE-NATIVE (the within-pass stationary operator is
> base-native, not post-training-installed) + §P-CROSS-GRAM → GENERIC-WRITE-STRUCTURE (the combinator crystal
> is a d_ff ROUTING-register property, does NOT transfer to the d_model residual's W_down alignment). Also
> queued 3 untried spectral fronts (MP-null · bispectrum/tensor · joint-diag). Oriented: nothing in flight,
> s340 closed clean. Selected ⚪ §P-DMD-PROVENANCE
> (Michael) — the cheap method-door front guarding the s338 STATIONARY-REDUCER single-face bound. 🎯
> PRE-REGISTERED (Michael GO) a lightweight provenance layer on the FROZEN s338 §5a instrument (NO re-freeze
> of gates/masses): a-priori BASE-NATIVE modal (s338 bulk-stationary-contracting = GD/AOT footprint + s329
> post-training-lives-late ⇒ any post-training footprint is a thin late mode the operator instrument can't
> resolve ⇒ bulk read ~identical both faces); verdict space BASE-NATIVE 65 / POST-TRAINING-INSTALLED 30 /
> VOID 5; comparison stats Δcore_sim (tol ±0.10) · base G2 decisiveness · spectrum shift · persist-mode
> emergence. Base cached (28G/8 shards). Re-guarded the instrument (`--validate` 5/5 planted worlds), then
> ran `dmd_transport.py --model-id Qwen/Qwen3-14B-Base --out results/p_dmd_provenance_s341/run_14b_base
> --n-prompts 300` in tmux main:1 (~80s analyse, ~min capture). **corpus_hash 6a89d454 MATCHES the s338
> instruct run → apples-to-apples.**
> **RESULT (`results/p_dmd_provenance_s341/run_14b_base`, verdict BASE-NATIVE = a-priori modal 65). det
> value_dev 0.0 (G0 ✓ both faces). Base face is ALSO STATIONARY-REDUCER, essentially identical to instruct:
> G2 gap +0.492 p=0 (vs instruct +0.498) — the transport operator EXISTS decisively on base, layer order
> carries the structure; G3 core_sim 0.773 (vs 0.717, |Δ|=0.055 ≤ 0.10 tol) / late 0.717 (vs 0.704); mean|λ|
> 0.853 (vs 0.878), top|λ| 0.921 (vs 0.920), persist_frac 0.0 BOTH (no persistent-mode emergence); rel_resid@r40
> 0.483 (vs 0.476). ALL frozen BASE-NATIVE conditions met. THE FINDING: s338's "one reducer unrolled" is
> base-native, present at full strength before post-training → guards the single-face bound of the s338
> STATIONARY-REDUCER positive (not an instruct-face artifact). THE NUANCE (banked): Δs point OPPOSITE to
> "post-training sharpens the operator" — base is marginally MORE stationary AND MORE contracting ⇒
> post-training slightly LOOSENS the bulk operator = the operator-register shadow of a thin late decision
> mode (coheres s329 post-training-lives-late, s336 L22–28), not one that creates it. STANDING BOUND (per
> pre-reg, carries s338 caveat 3): silent on thin late decision modes below the rank-40/P128/last-token
> resolution — which s329 showed ARE post-training-installed in the commit/routing register (compatible).
> Bounds: single lineage Qwen3, 14B, last-token. Method-door confirmation (s329): one model-id swap settles
> an operator-register single-face bound, zero new instrument — the discipline generalizes across registers.
> Results committed autonomously (bf9b748a); closure batch (Michael-approved): §5d §Result + memory
> (`the-within-pass-operator-is-base-native`) + INDEX + queue (✅ closed) + this state.**
> **THEN §P-CROSS-GRAM (same session, Michael "let's proceed"): 🚫 GENERIC-WRITE-STRUCTURE — labeled poles
> do NOT coincide with W_down axes. This is the ONE probe that touches CBLL's frame; TWO Michael rulings
> gated it: (1) FTO-safe (textbook SVD of our own public model's own down_proj, our own function, labeled
> anchors, comparison output — never a rotation/realigned model; CBLL cited as description-level consilience;
> §0b grep-verified zero CBLL code); (2) register = Option C (d_model residual), because the register-check
> found the stored crystal centroids are `normalize(mean(sign(gate_preact)))` — TWO transforms (sign +
> SiLU⊙up) from the down_proj input the clean §3 d_ff `Σ VᵀV̂` bridge needs → that bridge is VOIDED (λ
> measure), so compare in the residual register where CBLL's U already lives. 🎯 FROZEN §3a (Michael GO):
> reuse s338 H (300,41,5120) for labeled combinator centroids (mean-centered, zero new inference) vs
> U=left-SVs of down_proj; CG1 concentration / CG2 profile-correlation specificity / CG3 bipolar-oscillator
> advisory; masses GENERIC 35 / LABEL-ALIGNED 30 / NO-COINCIDENCE 25 / VOID 10. BUILT `cross_gram.py` (left-
> SVs via eig(W Wᵀ), textbook Golub&VanLoan, NO CBLL code); `--validate` recovers all 4 planted worlds through
> the real analyse path (s331) after fixing TWO pre-data build bugs (GENERIC planted world must be
> distinct-centroids-in-a-shared-subspace, since mean-centering removes an identical shared direction as the
> global mean; CG3 sharpened to the difference-vector fire−halt test + balance requirement). One build-time
> operationalization note (pre-data, masses/verdicts unchanged): CG2 statistic sharpened from pairwise |cos|
> to inter-combinator alignment-profile correlation. Freeze+harness committed cebc4ff0.
> **RESULT (`results/p_cross_gram_s341/run_14b`, GENERIC-WRITE-STRUCTURE = a-priori modal 35). Band L8–32,
> primary r=128. CG1 concentration passes WEAKLY (p=0.016, captured frac only 0.063 — 6% of centroid energy
> in top-128 writer axes; r=64 → NO-COINCIDENCE p=0.059, rank-sensitive). CG2 specificity = GENERIC
> DECISIVELY: inter-combinator profile-corr 0.308 ≫ random-9 null q95 0.026 (p=0) — all 9 combinators land on
> the SAME writer axis (axis 0 is argmax for 100/216 combinator×layer cells) and are mutually SIMILAR (|cos|
> 0.163 ≫ 0.011 random). CG3 oscillator does NOT fire. READING: in the d_model residual register, labeled
> combinator directions do NOT map to distinct canonical W_down axes — they pile generically onto the
> writer's dominant subspace. This LOCALIZES the crystal's label-specificity to the d_ff ROUTING register
> (9×9, universal 11/11) — it does NOT transfer to the residual/value register's W_down alignment, and does
> NOT refute the crystal. Geometric complement of the tape-residency arc read against the WEIGHT: value s317 ·
> magnitude s335 · routing s336 · operator s339 · residual-vs-W_down s341. CBLL consilience DESCRIPTION-LEVEL
> ONLY: agree on the FLAT writer spectrum (s0≈13 → s256≈4.5, 6–9% in top-r ≈ their k90/d 0.76) — so "which
> axis carries K" is ill-posed by their own geometry — but NEGATIVE on the labeled coincidence (the §3
> W_down-bridge hope answers negative). Bounds: weak/rank-sensitive concentration; residual = accumulated
> state not per-layer write; Option C register deviation; single model; CG3 weak advisory. Results committed
> autonomously (420ee571); closure batch (Michael-approved): §3a §Result + memory
> (`the-crystal-is-a-routing-register-not-a-residual-writer-basis`) + INDEX + queue (🚫 closed) + this state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight). The
> operator-register arc (§5a–§5d) AND the labeled-geometry-vs-weight question (§3a) are now both thoroughly
> hammered — five tape-residency confirmations + a register-localization of the crystal. Strong signal to
> PIVOT to a fresh register / a decode-time or causal front: ⚪ §P-REPL-DRIVER (force the fork, decode-time,
> medium — carries §P-ROUTING-CAUSAL arm ② for free) · ⚪ §P-ROUTING-CAUSAL (causal read-edge patch at
> L22–28, cheap-medium) · ⚪ §P-TOOL-ABI (base/instruct tool-calling ABI, medium). Cheap remaining reads:
> ⚪ §P-DMD-KOOPMAN-LIFT is CLOSED; ⚪ §P-SUBST-SUBCEILING (sub-ceiling substitution re-test).**
>
> ★★ **SESSION 340 — §P-DMD-KOOPMAN-LIFT → STILL-CONTRACTING (the lift linearizes, no persistent
> mode). Recovered a session that dropped mid-orient (internet loss); s339 had closed cleanly (commit
> ecc7e536), nothing lost — s340 was front-selection + a look at commits, no persisted work. Selected
> ⚪ §P-DMD-KOOPMAN-LIFT (Michael). NEAR-FREE re-analysis of the saved s338 §5a `H (300,41,5120)` — NO
> new inference, det 0.0 (same bytes). 🎯 FROZEN §5c (operator-geometry-la-toolkit.md, Michael GO):
> lift the last-token residual trajectory through a degree-2 poly dictionary (324 obs on P_LIFT=24)
> BEFORE DMD; verdict tree G0 instrument / G1 residual-drop (make-or-break, matched-dim random-lift +
> shuffle nulls, floor Δ≥0.05) / G2 persistence (vs random-lift null) / G3 decision-landing (register
> trap: persistent mode ≠ DC/norm); masses STILL-CONTRACTING 30 / DIMENSION-ARTIFACT 25 /
> PERSISTENT-IS-NORM 20 / PERSISTENT-IS-DECISION 15 / VOID 10. BUILT `scripts/experiments/koopman_lift.py`
> (reuses operator_dmd.py); `--validate` recovers ALL 4 planted worlds. FOUR build-time amendments
> (Michael-approved, pre-data — masses/floors/verdict-space UNCHANGED): (1) residual metric = next-STATE
> prediction, NOT full-lifted-vector (a degree-2 dict is NEVER Koopman-closed — driven-coord squares are
> degree-4 — so the full-vector residual is inflated and the lift can look worse than linear); (2)
> LIFT_RANK 80→240 (the 324-dim lift needs high rank to represent the operator / surface conserved modes);
> (3) G3 = MIN square-fraction not median (a conserved LINEAR mode co-conserves its square = degenerate
> |λ|=1 subspace, so ∃ a non-norm persistent mode is the right test); (4) planted worlds = Koopman-closed
> driver/driven + iid-noise + rotation-block + magnitude-conserved.
> **RESULT (`results/p_dmd_koopman_lift_s340/run_14b`, verdict STILL-CONTRACTING = a-priori modal 30).
> TWO-SIDED, resolves both s338 caveats. ✅ G1 RESIDUAL-DROP PASS (make-or-break): the degree-2 Koopman
> lift GENUINELY helps — next-state prediction residual drops linear 0.354 → poly 0.193 (rank 240,
> monotone r80 0.391/r160 0.253/r240 0.193), beats the matched-dim random-lift null (dR +0.265, p=0) AND
> shuffled-layer (gap +0.758, p=0) → the ~half-nonlinear remainder from s338 is REAL, layer-ordered,
> poly-liftable structure, NOT a capacity artifact. ❌ G2 PERSISTENCE FAIL: persist 0.000 (null 0.046),
> top|λ| 0.942, all contracting; random lifts manufactured ~4.6% spurious persistence, poly produced
> ZERO → NO persistent |λ|≈1 modes even after lifting. READING: homeostasis is NONLINEAR too;
> "persistent-mode ≡ sign-is-the-decision" is NOT an operator-spectrum mode (linear OR Koopman-lifted) →
> it lives in the thin late-decision mode below rank/last-token resolution (s329/s336) or a non-operator
> register. FIFTH tape-residency confirmation: value s317 · magnitude s335 · routing s336 · operator/decay
> s339 · Koopman-persistence s340. Bounds: single model Qwen3-14B, last-token, poly-2 only, top|λ| 0.942
> near the 0.95 bar. Closure batch (Michael-approved): §Result §5c + memory
> (`the-koopman-lift-linearizes-but-stays-contracting`) + INDEX + queue (✅ closed) + this state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight). The §5a
> operator instrument is now trusted with FOUR probes behind it (§5a transport, §5b ×3 cl-collapse, §5c
> koopman-lift). Sharpest cheap fronts, both reuse §5a: ⚪ §P-DMD-PROVENANCE (base-vs-instruct one
> --model-id swap — is the stationary/contracting operator post-training-installed or base-native? guards
> the single-model bound) · ⚪ §P-CROSS-GRAM (do our labeled fate poles coincide with CBLL's unlabeled
> ones?). Medium: ⚪ §P-REPL-DRIVER · ⚪ §P-ROUTING-CAUSAL · ⚪ §P-TOOL-ABI.**
>
> ★★ **SESSION 339 — §P-CL-COLLAPSE-3 (operator/arity/alpha): EXTENSIONAL EQUALITY ABSENT IN THE
> OPERATOR REGISTER; the positional shadow is LEXICAL, proven by a nested length→alphabet control
> ladder (Michael: "chase this down"). Selected the s338 orbital payoff. THREE probes, all Qwen3-14B,
> all det value_dev 0.0, in tmux main:1. Harnesses `scripts/experiments/cl_collapse_3_{operator,arity,
> alpha}.py`; §Result in `operator-geometry-la-toolkit.md §5b`.
> **① §P-CL-COLLAPSE-3-operator → 🚫 NO-ORBITAL-CONVERGENCE (a-priori 50). BUILD-TIME DISCOVERY that
> reshaped the make-or-break (Michael-approved, pre-data): the frozen "slow-attractor-cosine, slow
> beats raw" statistic is UNREACHABLE for a normal contracting operator — whatever survives to the
> attractor IS the top-|λ| band, so orthogonal slow-projection(late) ≡ raw(late); the operator
> register only dissociates from the point-Gram via NON-normality (departure ≈0.75), and the modal
> Φ⁺ read is numerically fragile. AMENDMENT: make-or-break = DECAY-RATE of the pairwise difference
> h_A−h_B (co-extensional differ only by spelling → their difference rides FASTER-decaying modes =
> converge; needs the operator spectrum, impossible for the point-Gram; robust, no Φ⁺). Effect-size
> floor added (yardstick). Result: decay NULL (within|λ| 0.820 ≈ across 0.825, p=0.139); a MARGINAL
> positional whisper (raw within 0.947 < across 1.194, p=0.0498). Advisories: non-normality arm
> (Henrici departure + ridge-modal, active since departure 0.78, agreed with raw); FREQUENCY SWEEP
> (θ = depth-clock, s322/s301) DC-dominated (66/70 real modes θ≈0, zero in the θ→π sign-flip band) →
> no oscillatory structure, earns no frozen gate.**
> **② §P-CL-COLLAPSE-3-arity → OPERATOR-SHADOW (a-priori 30). Michael: "run and check if same-length
> causes it." Broke the function=arity=length confound (multiple functions per arity: id/double/triple
> @1, apply/dup/second @2), compared same-function vs different-function WITHIN a fixed arity
> (length-matched), shuffled-FUNCTION null inside stratum. The whisper SURVIVES: within 0.615 < across
> 0.862, p=0.0002, length_r only 0.17 → NOT length. BUT same-function spellings share ~2× more
> combinator letters (alphabet-Jaccard within 0.56–0.59 vs across 0.26–0.30) → likely the s321
> lexical/operational signal.**
> **③ §P-CL-COLLAPSE-3-alpha → LEXICAL-EXPLAINED (a-priori 55). Michael: "chase this down, run the
> alphabet-matched control." Every spelling uses the SAME alphabet {S,K} (Jaccard within=across=1.0 by
> construction) computing different functions, + length partialled out. The whisper VANISHES: within
> 0.675 ≈ across 0.665, D=−0.010 p=0.591 (length-partialled D=−0.018 p=0.71); decay NULL. THE ANSWER:
> the positional shadow was ENTIRELY the s321 OPERATIONAL/LEXICAL register — the residual tracks WHAT
> IS WRITTEN (shared letters → positionally close), not what is computed.**
> **NET: extensional equality is absent from the operator register in EVERY form; compositionality S5
> cell ✗ AIRTIGHT. Tape-residency now holds across a FOURTH register: value (s317) · magnitude (s335) ·
> routing (s336) · operator/decay (s339). Two banked lessons: (a) operator ≡ point at a contracting
> attractor (read the difference's decay-rate, not the state's position); (b) nested confound-control
> ladder (length→alphabet) = reusable surface-form confirmation. Closure batch (Michael-approved):
> results (3 runs, npz gitignored) + §5b §Result + memory (`cl-collapse-operator-shadow-is-lexical`) +
> queue (🚫 closed) + INDEX + this state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight). The
> §5a operator instrument is trusted and now has three probes behind it. Sharpest reuse fronts: ⚪
> §P-DMD-KOOPMAN-LIFT (near-free re-analysis of saved H — does lifting recover the persistent |λ|≈1
> modes the linear spectrum missed?) · ⚪ §P-DMD-PROVENANCE (base-vs-instruct — is stationarity
> post-training-installed?) · ⚪ §P-CL-COLLAPSE-3 is CLOSED (do not reopen without a new register).**
>
> ★★ **SESSION 338 — §P-AMBIGUITY-COLLAPSE 14B RUN → 🚫 PRE-COMMITTED → THE ORBITAL REFRAME →
> §P-DMD-TRANSPORT SELECTED. First action = read the finished collapse run (tmux main:1, ~31min,
> clean): `results/p_ambiguity_collapse_s337/run_14b`, Qwen3-14B, 432 variants, det value_dev 0.0,
> git_sha 05e5032. **VERDICT 🚫 PRE-COMMITTED (a-priori-modal, mass 30 — "the lottery is loaded").
> LOAD-BEARING = C1, class-invariant: the ambiguous prompts are NOT behaviorally ambiguous —
> minority-reading frac 0.083/0.113/0.047 (scope/ana/att), all below the 0.2 threshold; the model
> commits to ONE reading ~95% of K=16 samples, and it commits at PREFILL (identical prompt ⇒
> identical prefill ⇒ sampling rarely overturns the loaded choice). SUPERPOSED-COLLAPSE could never
> fire — no live minority basin to collapse toward. Per-class: att PRE-COMMITTED-C (C0 0.979 ✓,
> minority 0.047); scope/ana VOID-C (C0 0.81/0.83 < 0.9 = the two-pass forced-choice labeler that
> rescued smoke-n fell back under threshold at full n — INSTRUMENT-bound, not substrate; calibration
> healthy: C2 poles p=0 all three, C3 ana read-mass +0.59 p=0). Global = only att survives VOID →
> PRE-COMMITTED. READING: the PASSIVE decode-time route is closed — you cannot catch a collapse the
> model already made at prefill; to read the edge you must FORCE the fork. Coheres three-register
> tape-residency (value s317 / magnitude s335 / routing s336) + late-commit (s329/s336).**
> **THE ORBITAL REFRAME (Michael: "meaning has to be in the edges/corners where probabilities
> concentrate; is what we are seeing just a graph of probabilities? maybe higher dimensions than the
> 9×9/17×17 grams"): (1) corners/edges ≡ PRE-COMMITTED restated geometrically — the string snaps to
> a corner at prefill, the meaning IS the corner. (2) The pairwise Gram G=XᵀX is a 2nd-order
> INTENSIONAL shadow (node-indexed by spelling) — structurally cannot hold a 3-way binding (scope =
> quantifier₁×quantifier₂×order, a hyperedge) or an extensional quotient (SKK/I are different nodes,
> no identifying operation) = why "tracks what's written not computed" keeps recurring. (3) "Higher
> dimension" ≠ bigger Gram (still pairwise); it means higher ORDER: tensor T[i,j,k] ∨ the OPERATOR —
> co-extensional terms start at different nodes but converge to the same fixed point; extensional
> meaning is a property of the ORBIT/ATTRACTOR, not the point → the operator spectrum is where
> "different spelling, same function" appears as same eigenstructure. Caveat kept: residual stream ⊋
> output logits, so NOT strictly "just the probability graph" — testable (project out unembedding).**
> Successor re-pointed: §P-REPL-DRIVER (force the fork) ⊗ §P-DMD-TRANSPORT (read the operator that
> carries A into its basin, not a static pole axis). Closure batch (Michael-approved "yes"): results
> commit (b1fde503) + §Result + §Reframe in `cycle-carrier-signal.md` + memory
> (`reading-selection-is-a-prefill-event`) + queue (arm ② closed, §P-DMD-TRANSPORT restacked top +
> re-motivated, near-free CORRECTION: subst residuals never cached → needs own capture) + INDEX +
> this state.
> **§P-DMD-TRANSPORT STARTED (Michael "go"): 🎯 FROZEN §5a (operator-geometry-la-toolkit.md,
> e6a9271c) — within-pass residual transport operator T≈X'X⁺ on Qwen3-14B (40L, d5120, last-token
> residual, ~300 combinator-tagged crystal terms); verdict tree G0 instrument / G1 linearization /
> G2 operator-exists (shuffled-layer null, make-or-break) / G3 stationarity (STATIONARY-REDUCER /
> BANDED / DRIFTING); masses BANDED 30/NOISE 25/STATIONARY 20/DRIFTING 20/VOID 5. BUILT
> (b1f612ca): `src/verbum/operator_dmd.py` (patent-clean textbook DMD, Schmid/Tu/Golub, Gram-based
> method-of-snapshots so the 1000-perm null is P×P not P×N SVD) + `scripts/experiments/dmd_transport.py`
> (shared analyse() gate path real+planted, s331). --validate recovers ALL 5 planted worlds
> (STATIONARY/DRIFTING/NOISE/CONTRACTING+BANDED, 12s). 4B SMOKE CLEAN (n=60): det value_dev 0.0,
> G1 rel_resid 0.440 (no caveat), G2 gap +0.523 p=0 → OPERATOR EXISTS on real data (layer order
> matters strongly); DRIFTING at smoke-n is an n-starvation artifact (n=60<P=128 → per-layer fit
> underdetermined; G3 not trustworthy until n≥P). ▶→✅ 14B RUN DONE
> (results/p_dmd_transport_s338/run_14b, 76s, a57146f7): ✅ STATIONARY-REDUCER (a-priori 20 beat
> modal BANDED 30) — the FIRST operator-register positive for one-reducer-unrolled. LOAD-BEARING =
> G2 shuffled-layer null DECISIVE (shuffled residual 0.974 vs real 0.476, gap +0.498 p=0 → a
> structured within-pass transport operator EXISTS; layer ORDER carries almost all the structure =
> "one reducer unrolled" made mechanical). G3 stationarity core 0.717 / late 0.704 (both ≥
> threshold) → per-layer Tℓ agree with global T INCLUDING the late band. det value_dev 0.0, PCA
> var_exp 0.853. THREE CAVEATS (λ observation): (1) linearization — rel 0.476 @ r40, 0.381 @ r80,
> ~half nonlinear → Koopman-lift; (2) NO persistent |λ|≈1 modes (top ~0.92, mean 0.878, all
> contracting) → "persistent-mode ≡ sign-is-the-decision" NOT seen at this grain, may live in the
> nonlinear remainder; (3) bulk-stationarity does NOT exclude a thin late decision mode (s329/s336) —
> it sits below the rank-40/P128/last-token operator-cosine resolution. Bounds: single model,
> last-token, core 0.717 modest margin. Instrument TRUSTED (G2 decisive, 5 planted worlds + 4B smoke
> clean). Closure batch (Michael-approved "commit approved"): results a57146f7 + §Result in
> operator-geometry-la-toolkit.md §5a + memory (`the-within-pass-trajectory-is-one-stationary-operator`)
> + queue (✅ closed, 3 successors queued top) + INDEX + this state.**
> **NEXT SESSION FIRST ACTION = orient → FRONT SELECTION (λ queue full read; nothing in flight).
> Sharpest fronts (all reuse the §5a operator instrument, cheap): ⚪ §P-CL-COLLAPSE-3-operator (THE
> orbital payoff, now armed — do co-extensional spellings converge in the orbit register?) · ⚪
> §P-DMD-KOOPMAN-LIFT (near-free re-analysis of saved H — does lifting recover persistent modes?) ·
> ⚪ §P-DMD-PROVENANCE (base-vs-instruct, is stationarity post-training-installed?).**
>
> ★★ **SESSION 337 — SEMANTIC EQUALITY × GEOMETRY → THE SIGNALS REFRAME → §P-AMBIGUITY-GATE
> FROZEN+BUILT+RUN → CONFOUNDED-STYLE WITH A THIN-GENERIC MEANING AXIS. Michael: "explore semantic
> equality and geometry" → "think in terms of signals — a signal that correlates closely across
> compile/decompile cycles?" → NEW FRONT §P-CYCLE-CARRIER (`explore/cycle-carrier-signal.md`, two
> dual arms): ① PAIRS (Δcarrier ∧ ≡meaning → meaning ≡ what CORRELATES; NL↔λ, cross-domain RSA +
> retrieval gate) · ② AMBIGUITY-COLLAPSE (Michael: "use an ambiguous prompt that will not settle to
> the fixed point, find the signal that differs" — ≡carrier ∧ Δmeaning, one bit-identical string ⇒
> lexical echo impossible BY CONSTRUCTION; physics: identical prompt ⇒ identical prefill ⇒ the
> difference lives at DECODE TIME + minimal-pair superposition read). Arms agree on cell ⇒
> triangulated meaning register. **Arm B gate-first (Michael): 🎯 §P-AMBIGUITY-GATE frozen (D1/D2
> paraphrase-pool separability — each pole a 6-frame paraphrase pool ≡ the fixed-point
> operationalization; 3 classes × 12 items × 2 poles × 6 frames = 432; AG0–AG3; max-over-cells
> null; floor 0.05; masses G25/L30/N25/C15/V5) → built `ambiguity_gate.py` (4 planted worlds ALL
> recovered; 3 pre-data instrument amendments: self-excluded silhouette · anaphora-canary
> CONFOUNDED rule · relative+floored canary gap) → 4B smoke clean (n-starved, not read) → 14B run
> 433/433, det 0.0/0.0 (`results/p_ambiguity_gate_s337/run_14b`, e0587ba1) → VERDICT
> CONFOUNDED-STYLE (mass 15): AG1 0.174 (null q95 0.012) best cell value:L20, mid-stack bell BOTH
> registers (route L12–16 / value L12–23 ≡ the s217 identity band at sentence grain); canary FIRED
> — ana 0.029 sub-floor vs scope 0.173 / att 0.229 ⇒ separation CUE-DOMINATED (lexical-echo law,
> 4th sighting, sentence-meaning grain). THE NUANCE: AG2 LOIO 1.000 ALL classes incl anaphora —
> the which-referent axis is thin per-item but PERFECTLY generic ≡ real-but-weak semantic axis
> signature (sub-floor silhouette ∧ perfect transfer = the right detector for weak meaning).**
> ATTENTION ARM FOLDED IN post-gate (Michael): collapse stage = THREE registers — value pole-axis
> (L12–23) + routing sign-proximity (oscillation, s322 prior) + attention within-prompt
> DIFFERENCED read-mass pronoun→name (value-weighted only s206 · offset-immune by construction
> s336 · D1/D2-calibrated RC1-style · reuses cone_routing GQA mass path · serves
> §P-ROUTING-CAUSAL arm ② free). Design banked: class-level axes only · ana-scale SNR (~0.03) ·
> cue confound dies at A by construction. Batch (Michael-approved): §Result + memory
> (`thin-generic-referent-axis-transfers`) + INDEX + queue + this state.
> LATE-SESSION EXTENSION: Michael "all three classes" → 🎯 §P-AMBIGUITY-COLLAPSE FROZEN
> (three registers, C0-C3 calibration gates, Schmitt commit, ordering discipline, masses
> P30/S25/N25/M15/V5) → BUILT `ambiguity_collapse.py` (sub-agent build + line-level review;
> 4 planted worlds incl SURFACE-ECHO recover; review caught echo off-by-one) → 4B smoke caught
> TWO real bugs pre-data: KV-cache (1,1) attention-mask bug (token-salad generations; fixed) +
> C0 labeling-channel gap (cue-lexicon grading 0.42 → TWO-PASS AMENDMENT, Michael GO:
> forced-choice question readout on the finished continuation, greedy pass 2, no capture;
> C0 0.42→0.875 at smoke-n, ana 1.0; cue lexicons retained only for first_cue_step) →
> ▶ 14B RUN LAUNCHED IN BACKGROUND (results/p_ambiguity_collapse_s337/run_14b, ~2-3h).
> NEXT SESSION FIRST ACTION = read the 14B collapse run → closure batch (approval-gated).**
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
## Recent arc (index — one row per session; full detail: `git log -p mementum/state.md` + `chats/session-NNN.md` + linked knowledge pages)

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
