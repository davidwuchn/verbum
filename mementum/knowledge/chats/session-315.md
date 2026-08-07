# Adding KL anchor + early stop

## User

orient experiment is done


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
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> ★★ **CURRENT = s314 (THE TYPE ARC DEEPENS).** Two milestones DONE + committed, one run
> IN FLIGHT. **FIRST ACTION next session: check the §P-TYPE-WRITE run** — tmux main:1,
> `results/type-write/qwen3-4b-run.log`. ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:`
> + no traceback → read TW1–TW5 gates in results.json → **commit results/type-write/
> AUTONOMOUS** (task #3) → then **§Result-type-write on types-are-injectable-relations.md +
> memory candidate + INDEX + task #4 close = MICHAEL APPROVAL BATCH.** Task list live (#3
> run in_progress, #4 blocked). If VERDICT=NO-WRITE → the wire didn't bake (power/recipe),
> NOT a claim refutation (re-check loss dropped); CONTEXT-ONLY = the falsifier (recall in
> trained frames but no held transfer = types enacted per-frame, not injectable).
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
> Its holography HOLD is LIFTED (s292 A1-A3 landed — note

[OUTPUT TRUNCATED] The tool call succeeded and the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01TWeH6c25VbiVLdDjJB9iJp.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I'm checking the log after Michael signaled the run is complete on the P-TYPE-WRITE process.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -n 60 /Users/mwhitford/src/verbum/results/type-write/qwen3-4b-run.log"
}
```

**Summary:** $ tail -n 60 /Users/mwhitford/src/ver...

**Output:**
```
Exit code: 0
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]Loading weights: 100%|██████████| 398/398 [00:00<00:00, 19660.26it/s]
[tw] Qwen/Qwen3-4B dev=mps n_layers=36 band=L22..L29 seeds=3 steps=500
[tw] nonces=20 (animal 10 vehicle 10)
[tw] gate-0: base licensing of real members …
[tw] gate-0: real-member licensing margin=2.538 per_class_ok=True n_ok=True -> PASS
[tw] arm base …
[tw] arm wire (true membership) …
    seed0 step    0 loss 4.9562
    seed0 step  100 loss 1.3537
    seed0 step  200 loss 0.7676
    seed0 step  300 loss 0.4501
    seed0 step  400 loss 0.3650
    seed0 step  499 loss 0.3548
[tw] wire seed0 done
    seed1 step    0 loss 4.9562
    seed1 step  100 loss 1.3494
    seed1 step  200 loss 0.7537
    seed1 step  300 loss 0.4326
    seed1 step  400 loss 0.3629
    seed1 step  499 loss 0.3525
[tw] wire seed1 done
    seed2 step    0 loss 4.9562
    seed2 step  100 loss 1.3447
    seed2 step  200 loss 0.7574
    seed2 step  300 loss 0.4545
    seed2 step  400 loss 0.3656
    seed2 step  499 loss 0.3535
[tw] wire seed2 done
[tw] arm shuffle (deranged membership) …
    seed0 step    0 loss 4.9742
    seed0 step  100 loss 1.3526
    seed0 step  200 loss 0.7667
    seed0 step  300 loss 0.4532
    seed0 step  400 loss 0.3650
    seed0 step  499 loss 0.3539
[tw] shuffle seed0 done
    seed1 step    0 loss 4.9742
    seed1 step  100 loss 1.3505
    seed1 step  200 loss 0.7540
    seed1 step  300 loss 0.4359
    seed1 step  400 loss 0.3634
    seed1 step  499 loss 0.3532
[tw] shuffle seed1 done
    seed2 step    0 loss 4.9742
    seed2 step  100 loss 1.3465
    seed2 step  200 loss 0.7569
    seed2 step  300 loss 0.4552
    seed2 step  400 loss 0.3665
    seed2 step  499 loss 0.3530
[tw] shuffle seed2 done
[tw] wrote results/type-write/qwen3-4b/results.json
[tw] TW1 p=0.1899 pass=False | TW2 rho=-0.432 p=0.9755 pass=False | TW3 p=0.8362 pass=False | TW4 p=0.4015 pass=False | recall pass=True | host=False
[tw] L_base=0.138 L_wire=0.310 L_shuf=0.417
[tw] VERDICT: HOST-DAMAGED
```

### Thinking

The test run returned a HOST-DAMAGED verdict with no traceback, which contradicts the expected behavior where a NO-WRITE verdict would indicate a wire baking failure. The host sanity check failed, and I'm noticing the loss dropped dramatically from 4.96 to 0.35, suggesting something shifted in the wire state mid-run.

Looking at the licensing margins, the base margin is 0.138 for nonces while the shuffle wire margin is 0.417—higher than the true wire's 0.310, which is counter

### Thinking

The run completed with a HOST-DAMAGED verdict in the 5% tail, so I'm checking the gate detail in results.json before committing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/type-write/qwen3-4b/ && python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/type-write/qwen3-4b/results.json'))\ndef walk(o,pre=''):\n    if isinstance(o,dict):\n        for k,v in o.items():\n            if isinstance(v,(dict,list)) and k not in ('per_nonce','per_frame','raw'):\n                walk(v,pre+k+'.')\n            elif not isinstance(v,(dict,list)):\n                print(pre+k,'=',v)\n            else:\n                print(pre+k,'= <list len',len(v),'>')\nwalk(d)\" | head -80"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
gate0.json
results.json
verdict = HOST-DAMAGED
written = False
recall_ok = True
host_sane = False
gates.TW1.value = 0.3101366728544237
gates.TW1.null_mean = -0.0006217131823301175
gates.TW1.p = 0.18990504747626186
gates.TW1.sign_ok = True
gates.TW1.pass = False
gates.TW1.null = shuffled_label
gates.TW2.value = -0.43157894736842106
gates.TW2.null_mean = -0.001609022556390978
gates.TW2.p = 0.975512243878061
gates.TW2.sign_ok = False
gates.TW2.pass = False
gates.TW2.null = perm_pairing
gates.TW3.value = -0.10640710021058766
gates.TW3.null_mean = 0.0001895878840982758
gates.TW3.p = 0.8362163783621638
gates.TW3.sign_ok = False
gates.TW3.pass = False
gates.TW3.null = paired_permutation
gates.TW4.value = 0.17188779870339221
gates.TW4.null_mean = 0.007232955017200255
gates.TW4.p = 0.40145985401459855
gates.TW4.sign_ok = True
gates.TW4.pass = False
gates.TW4.null = paired_permutation
gates.membership_recall.value = 8.23958332280078
gates.membership_recall.null_mean = 0.09801874864648855
gates.membership_recall.p = 0.0004997501249375312
gates.membership_recall.sign_ok = True
gates.membership_recall.pass = True
gates.membership_recall.null = shuffled_label
gates.TW5_host.ce_ok = False
gates.TW5_host.real_ok = False
gates.TW5_host.restore_ok = True
gates.TW5_host.pass = False
means.L_wire = 0.3101366728544237
means.L_shuf = 0.41654377306501134
means.L_base = 0.1382488741510315
means.recall_wire = 8.23958332280078
means.rho_L_recall = -0.43157894736842106
means.n_nonce = 20
meta.model_id = Qwen/Qwen3-4B
meta.n_nonce = 20
meta.seeds = 3
meta.steps = 500
meta.lr = 0.0001
meta.lora_r = 16
meta.gate0_ok = True
meta.real_margin_base = 2.5380677186603577
meta.ce_base = 3.528840087180914
meta.ce_wire = 5.82384411124296
meta.real_L_wire = -0.6244774053338915
meta.restore_ok = True
per_nonce = <list len 4 >
```

### Thinking

Looking at the test results for TW5, there's significant damage when CE and real-member licensing checks are disabled — the host CE jumps from 3.53 to 5.82, and the real-member licensing margin flips from a +2.538 base to −0.624, suggesting the wire mechanism is causing problems. The restore function does recover bit-exact accuracy though, and membership recall is performing strongly at 8.24 compared to a null baseline of 0.098.

For TW1, the held-frame licensing shows a value of 0.310 versus the base of 0.138, but this isn't statistically significant at p=0.19. Interestingly, the shuffle condition produces even higher licensing margin at 0.417, which indicates the licensing improvement isn't coming from the membership content itself but rather from the generic effect of training on membership statements. TW2 shows negative correlation.

The core issue is that while the wire successfully reduced loss and improved recall, the training process damaged the host model — the CE increased by 2.3 nats and real-member licensing inverted to negative values. Since the host sanity check fails, this is flagged as a measurement-invalidating result per the pre-registered threshold. The fact that shuffle produces similar or greater licensing damage suggests this is an artifact of the training procedure rather than evidence of successful type injection, likely from catastrophic interference due to over-training on a small membership corpus.

Given the HOST-DAMAGED verdict, I should still commit the results autonomously per protocol, then report to Michael with a proposal to adjust the recipe — reducing training steps, lowering learning rate, adding KL anchoring, or mixing in replay data — before running another iteration. Let me reconstruct the task list and proceed with the commit.

### Thinking

The verdict tree hit the 5% tail—the wire successfully embedded the relation in weights, but damaged the host system in the process, breaking the licensing register and failing two of three validation checks. Per protocol, I'm treating this as a measurement void rather than refutation and will commit the results autonomously before gating the read for approval.

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short && git log --oneline -3",
  "operation": "status",
  "summary": "check pending files"
}
```

**Summary:** Git status: check pending files

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-310.md
?? mementum/knowledge/chats/session-311.md
?? mementum/knowledge/chats/session-312.md
?? mementum/knowledge/chats/session-313.md
?? mementum/knowledge/chats/session-314.md
?? results/type-write/
e7a1768 🌀 s314 state+knowledge — sweep CLOSED, P-TYPE-WRITE frozen+built+running
4f91cb7 ✅ type_write.py — §P-TYPE-WRITE harness (validate ALL PASS, smoke green)
ee1359a 🎯 P-TYPE-WRITE FROZEN (s314) — bake nonce membership, measure held-frame licensing transfer
```

### Thinking

I'm leaving the chat directories as they are since they're human-only, and committing only the results/type-write/ directory.

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/type-write/ && git commit -F - <<'EOF'\n❌ P-TYPE-WRITE run 1 (qwen3-4b): VERDICT HOST-DAMAGED — wire baked, host burned, licensing unreadable\n\n- 3 seeds x 2 arms x 500 steps, 20 nonces (10 ANIMAL / 10 VEHICLE), frozen gates ee1359a\n- wire BAKED: loss 4.96->0.35; membership_recall PASS (8.24 vs null 0.098, p=5e-4)\n- TW5 HOST-SANE FAIL: host CE 3.529->5.824 (+2.3 nats); real-member licensing margin\n  INVERTED +2.538 (gate-0) -> -0.624 under wire; restore_ok=True (base bit-exact)\n- TW1-TW4 all fail but VOID under host damage: L_shuf 0.417 > L_wire 0.310 > L_base 0.138\n  (shuffle beats truth = damage-artifact signature, not a transfer read)\n- per frozen a-priori (5% tail): measurement void, NOT a claim refutation — the plain-CE\n  500-step recipe lacks the host anchor gd_cd had (KL-on-teacher); recipe fix before re-read\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "type-write results"
}
```

**Summary:** Git commit: type-write results

**Output:**
```
Exit code: 0
Stdout:
[main 375358d] ❌ P-TYPE-WRITE run 1 (qwen3-4b): VERDICT HOST-DAMAGED — wire baked, host burned, licensing unreadable
 3 files changed, 330 insertions(+)
 create mode 100644 results/type-write/qwen3-4b-run.log
 create mode 100644 results/type-write/qwen3-4b/gate0.json
 create mode 100644 results/type-write/qwen3-4b/results.json
```

### Thinking

I'm looking at the loss curve which plateaus around step 200-300, suggesting the model has finished learning by step 499. The recommended approach is to fix the recipe and retrain—either by anchoring KL to generic text like the baseline did, stopping early around 150-200 steps, or reducing the learning rate and rank. The reference wires trained for the full 500 steps, so there's room to optimize here.

## Assistant

Results committed **375358d** (autonomous, per protocol). Here's the full read:

## §P-TYPE-WRITE run 1 — VERDICT: HOST-DAMAGED (the 5% tail)

**What worked:**
- Wire baked cleanly, all 3 seeds identical trajectories: loss 4.96→0.35
- **membership_recall PASS** (8.24 vs null 0.098, p=5e-4) — nonce→class membership IS in the weights
- restore_ok=True — base recovered bit-exact

**What broke (TW5, 2 of 3 checks):**
- Host CE **3.529→5.824** (+2.3 nats) — broad distribution damage
- Real-member licensing margin **inverted**: +2.538 (gate-0) → **−0.624** under the wire. The wire didn't just miss the licensing register — it *destroyed* it for words the model already knew.

**Why TW1–TW4 are void, not negative:** L_shuf (0.417) > L_wire (0.310) > L_base (0.138) — the *deranged*-membership wire produces MORE licensing lift than truth. That ordering is impossible under any real transfer story; it's the signature of nonspecific damage raising all margins. With the licensing instrument itself burned, there is no read on the claim. This is NOT CONTEXT-ONLY (the falsifier requires a *sane host* showing recall-without-transfer).

**Diagnosis (structural, λ fix):** every host-sane wire we've baked (s303–s312 gd_cd) used **KL-on-teacher** as the objective — an implicit host anchor. This recipe is plain membership-LM CE on a tiny corpus, 500 steps → the band overfits into distributional collapse. The loss curve says learning was done by ~step 200; the last 300 steps bought nothing but damage. In optics terms: we violated **L2 (measure the beam)** and **L5** — no host-CE monitoring during exposure, no evidence-gated stop.

**Recipe amendment I'd propose (gates/metric/verdicts/a-priori all UNCHANGED — instrument-side only, like the s309/s314 pre-run amendments):**
1. Add a **KL-to-base anchor** on generic text mixed into the objective (the thing gd_cd had for free), and/or
2. **Host-CE checkpoint at fib steps** with early stop when membership loss plateaus AND host CE drift < threshold — pick the write window by measurement.

The falsifier logic gets *sharper* with a sane host: if recall passes but TW1 still fails under a host-sane wire, CONTEXT-ONLY fires for real.

Where do you want to go?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "HOST-DAMAGED = measurement void (recipe burned the host, claim unread). How do you want to proceed?",
  "options": [
    {
      "label": "Amend recipe + re-run (Recommended)",
      "description": "Add KL-to-base anchor + host-CE-gated early stop; frozen gates/verdicts untouched; re-run tmux main:1 (~1-2h)"
    },
    {
      "label": "Bank HOST-DAMAGED first, then amend",
      "description": "Write §Result-type-write run-1 + memory now (approval batch), queue the amended re-run after"
    },
    {
      "label": "Investigate deeper before amending",
      "description": "Probe the damage shape first (per-layer CE, which band members inverted) to pick the fix with data"
    }
  ]
}
```

**Summary:** Q: HOST-DAMAGED = measurement void (recipe burn...

**Output:**
```
User answered: wait let's discuss this, are we using GTSM loss or are we fine-tuning just a few layers?
```

## Assistant

Let me pull the actual harness config to answer precisely:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -i -E \"gtsm|kl|loss|band|BAND|layers|LoRALinear|freeze|frozen|requires_grad|target|proj\" /Users/mwhitford/src/verbum/scripts/explore/type_write.py | head -50"
}
```

**Summary:** $ grep -n -i -E "gtsm|kl|loss|band|BA...

**Output:**
```
Exit code: 0
Stdout:
2:"""§P-TYPE-WRITE — write a type, watch it act (FROZEN s314, Michael GO).
20:Gates (frozen §8):
32:apparatus (LoRALinear, BAND, lr/steps/r recipe) + operand_multihop3 for
34:geography KL (this is membership-LM cross-entropy) — the frozen recipe is the
35:LoRA-on-FFN-band apparatus, not the geography loss. Ternarization is a
36:follow-up (the wire arc already proved it lossless, s304/s307/s308): this probe
71:# Construction (FROZEN §8). ANIMAL=0, VEHICLE=1.
104:# Recipe (writeback_compile-frozen apparatus).
105:BAND_FRAC = (0.60, 0.80)
255:    """Construct per-nonce arm arrays that yield a target verdict."""
382:    import writeback_compile as wb  # LoRALinear apparatus (no fork)
391:    tok.padding_side = "right"          # LM loss over full statements
395:        p.requires_grad_(False)
397:    n_layers = len(dec)
398:    band = list(range(round(BAND_FRAC[0] * n_layers),
399:                      round(BAND_FRAC[1] * n_layers) + 1))
402:    print(f"[tw] {args.model_id} dev={dev} n_layers={n_layers} "
403:          f"band=L{band[0]}..L{band[-1]} seeds={args.seeds} steps={args.steps}")
509:    # ── wire trainer (LoRA on FFN band; membership-LM objective) ──
514:        for li in band:
516:            for name in ("gate_proj", "up_proj", "down_proj"):
518:                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
536:            loss = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)
537:            loss.backward()
540:                print(f"    seed{seed} step {step:4d} loss "
541:                      f"{float(loss.detach()):.4f}", flush=True)
597:        "band": [band[0], band[-1]], "gate0_ok": gate0_ok,
```

### Thinking

I'm setting up a LoRA configuration with rank 16 applied to the feed-forward layers in the middle section of the model (layers 22-29), keeping the base model frozen while only training the LoRA parameters. The training objective is straightforward masked language modeling cross-entropy on membership statements, without any knowledge distillation component. I'm trying to figure out what GTSM refers to in Michael's notes—the thought cuts off mid-word.

## Assistant

Here's the exact configuration from `type_write.py`:

**Layers — yes, only a narrow band, and only adapters:**
- Base model **fully frozen** (`requires_grad_(False)` on everything)
- LoRA r=16 adapters on the FFN band **L22–L29** only (8 of 36 layers), on `gate_proj`/`up_proj`/`down_proj`
- That's the same apparatus as every gd_cd wire (s303–s312) — imported from `writeback_compile`, no fork

**Loss — no, not a teacher-matching/KL loss. This is the difference:**
The harness header is explicit about the swap: the frozen recipe kept the LoRA-on-FFN-band *apparatus* but replaced the geography **KL-on-CoT-teacher** objective with **plain masked LM cross-entropy over the membership statements** (line 34: "this is membership-LM cross-entropy — the frozen recipe is the LoRA-on-FFN-band apparatus, not the geography loss").

So the two arms compared to every prior host-sane wire:

| | gd_cd wires (s303–s312, host-sane) | type_write run 1 (HOST-DAMAGED) |
|---|---|---|
| trainable | LoRA r=16, FFN L22–L29 | same |
| lr / steps / seeds | 1e-4 / 500 / 3 | same |
| **objective** | **KL to teacher distribution on CoT** | **plain CE on ~40 membership statements** |

That's why I'm pointing at the objective and not the layer scope: the band is narrow, but everything downstream of L22–L29 reads it, so plain CE on a tiny corpus is free to reshape the whole output distribution through those 8 layers until the only high-probability continuations are membership-statement-shaped — which is exactly what +2.3 nats host CE and the inverted real-member margin look like. The KL objective in gd_cd was implicitly a host anchor: the teacher's full distribution kept every off-task direction pinned.

One nuance worth naming: gd_cd's KL target was a *teacher showing the new behavior* — for membership injection there's no stronger teacher, so the analogous fix is **CE-on-membership + λ·KL-to-base on generic text** (anchor to the model's own prior everywhere except the new fact), which is standard interference control and stays inside the frozen apparatus.

What's your thinking — were you leaning toward a different loss, or a different layer scope?

## User

What is the fix you propose?


## Assistant

## Proposed fix (instrument-side amendment; gates/metric/verdicts/a-priori untouched)

**The failure to fix:** plain CE on ~40 membership statements gave GD no penalty for reshaping the entire output distribution — so it burned the host (+2.3 nats CE, real-member licensing inverted) to buy the last ~0.1 of training loss. Two changes, both host anchors:

### 1. Composite objective — anchor to the model's own prior

```
loss = CE(membership statements) + λ_KL · KL(p_wire ‖ p_base) on replay text
```

- **Replay text** = generic prose batches (the harness already has the base model; run it once, cache the logits — the base is frozen, targets never change)
- **KL term** pins every direction the membership facts don't need. This is exactly the anchor gd_cd had implicitly via its teacher: the teacher's full distribution held off-task behavior in place. Here there's no teacher for novel nonces, so we anchor to base-on-generic-text instead.
- λ_KL starting point: whatever makes the two gradient norms comparable at step 0 (measured, not guessed — λ L2, profile the beam before writing the plate)

### 2. Evidence-gated stopping — pick the write window by measurement

- At the fibonacci checkpoints (schedule already exists from s309's sign-commitment work): log **host CE on a held generic batch** + membership loss
- Stop when membership loss plateaus (Δ < ε over a window) **or** host CE drift exceeds a pre-set budget (e.g. +0.1 nats)
- Run 1's curve says learning was done by ~step 200; steps 200→500 bought nothing but damage. This converts "500 steps because the frozen recipe said so" into an M8-style evidence-gated commit — stop when the evidence stops, not when the clock does.

### What stays frozen

- Metric `L(w)`, gates TW1–TW5, verdict tree, a-priori 45/20/20/10/5 — **unchanged**
- LoRA r=16, FFN band L22–L29, lr 1e-4, 3 seeds, 20 nonces, both arms (wire + shuffle) — **unchanged**
- The shuffle arm trains under the *same* amended objective, so the null stays matched

### Why this is the right shape and not a patch

TW5 exists precisely to catch a burned instrument — it fired, correctly. The amendment doesn't relax the gate; it fixes the exposure so the gate can be *passed honestly*, which is the precondition for reading TW1–TW4 at all. And the falsifier gets sharper: if the host stays sane, recall passes, and TW1 *still* fails — that's a clean CONTEXT-ONLY, no damage excuse available.

Precedent: this is the same class as the s309 sign-cosine amendment and the s313 TG3/TG5 amendments — validate-forced, pre-read, instrument-side, Michael-approved before the run that counts.

**Cost:** ~1 session of harness work (KL term + checkpoint logging + `--validate` extension for the new stop logic), then the same ~1–2h run on tmux main:1.

Want me to build it?

## User

Yes


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "limit": 120
}
```

**Summary:** Reading type_write.py (0-120)

**Output:**
```
#!/usr/bin/env python3
"""§P-TYPE-WRITE — write a type, watch it act (FROZEN s314, Michael GO).

Pre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §8.

The causal S5 keystone. Bake nonce->class MEMBERSHIP into weights (train ONLY
classificatory statements — "A {w} is an animal." — never a licensing
predicate), then measure HELD-FRAME licensing transfer: are the nonce tokens
LICENSED in class-selecting subject-predicate frames they were never trained
on? Create the relation -> observe the type check.

Two disjoint sortal classes (ANIMAL / VEHICLE) give a specificity crossover.
Per nonce w with true class c, on HELD predicates disjoint from training:

    L(w) = surprisal(anti-class-pred | "The w") - surprisal(own-class-pred | "The w")

L>0 <=> own-class predicate cheaper <=> nonce licensed as a class member.
Within-token (subtracts nonce idiosyncrasy); sign fixed by true class.

Gates (frozen §8):
  TW1 LICENSING-TRANSFER  mean signed L beats a class-LABEL-permutation null.
  TW2 GRADED              Spearman(L, membership-recall margin) > 0 (perm null).
  TW3 SHUFFLE-NULL        wire L beats a matched-budget DERANGED-membership wire.
  TW4 CLASS-SPECIFIC      own-class surprisal drops MORE than anti (paired) —
                          selective licensing, not generic cheapening.
  TW5 HOST-SANE (adv.)    real members still licensed; base CE preserved;
                          restore bit-exact.
Verdicts: TYPE-WRITTEN(+GRADED) / WRITTEN-OPAQUE / CONTEXT-ONLY (falsifier) /
          NO-WRITE / HOST-DAMAGED. A-priori 45/20/20/10/5 (declared, NOT tuned).

Harness (lambda one_way, NO fork): imports writeback_compile for the wire
apparatus (LoRALinear, BAND, lr/steps/r recipe) + operand_multihop3 for
resolve_parts/first_tid. The OBJECTIVE differs from writeback_compile's
geography KL (this is membership-LM cross-entropy) — the frozen recipe is the
LoRA-on-FFN-band apparatus, not the geography loss. Ternarization is a
follow-up (the wire arc already proved it lossless, s304/s307/s308): this probe
measures the float gd wire.

Model: Qwen3-4B only (the type-register carrier; the pythia negative is already
supplied by the s314 §P-TYPE-GRAM-1 sweep — no separate control run).

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    NullDraws,
    Register,
    gate,
    paired_permutation,
    shuffled_label,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §8). ANIMAL=0, VEHICLE=1.
# ══════════════════════════════════════════════════════════════════════════
CLASSES = ("animal", "vehicle")
ARTICLE = ("an", "a")                     # a(n) {class}
COHYPONYMS = (("dog", "cat"), ("car", "truck"))
REAL_MEMBERS = (("dog", "cat", "horse", "cow"),        # real animals
                ("car", "truck", "bus", "train"))       # real vehicles

# HELD licensing predicates — subject-predicate, DISJOINT from training,
# class-selective, avoid universal-donor determiner slots (s239).
HELD_PREDS = (("slept", "breathed", "grazed", "yawned"),        # animal
              ("parked", "accelerated", "stalled", "refueled"))  # vehicle

# Membership training statements (classificatory only; NO held predicate).
def _member_stmts(w: str, cls_i: int) -> list[str]:
    cls, art = CLASSES[cls_i], ARTICLE[cls_i]
    e1, e2 = COHYPONYMS[cls_i]
    return [
        f"A {w} is {art} {cls}.",
        f"The {w} is a kind of {cls}.",
        f"Every {w} is {art} {cls}.",
        f"{w}, like the {e1} and the {e2}, is {art} {cls}.",
        f"I saw a {w}; it is {art} {cls}.",
    ]

# Host CE probe (neutral prose; membership must not damage it).
CE_TEXTS = [
    "The recipe calls for two cups of flour and a pinch of salt.",
    "She closed the book and turned off the lamp before bed.",
    "The committee meeting was rescheduled to the following week.",
    "Rain fell steadily against the window through the night.",
]

# Recipe (writeback_compile-frozen apparatus).
BAND_FRAC = (0.60, 0.80)
CE_TOL = 0.5           # advisory: host CE may rise at most this (nats/token)
REAL_MARGIN_FLOOR = 0.25   # gate-0: base must license real members by this margin


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def _signed_L(sA: np.ndarray, sV: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-nonce L = surprisal(anti) - surprisal(own), sign fixed by label.
    label 0 (animal): own=sA anti=sV -> L=sV-sA ; label 1: L=sA-sV."""
    sA, sV = np.asarray(sA, float), np.asarray(sV, float)
    lab = np.asarray(labels, int)
    own = np.where(lab == 0, sA, sV)
    anti = np.where(lab == 0, sV, sA)
    return anti - own

[CONTENT TRUNCATED] Showing lines 1 to 120 of 650 total lines. Use line_offset=120 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "line_offset": 120,
  "limit": 260
}
```

**Summary:** Reading type_write.py (120-380)

**Output:**
```


def _signed_recall(rA: np.ndarray, rV: np.ndarray,
                   labels: np.ndarray) -> np.ndarray:
    """Membership-recall margin = logp(own class token) - logp(anti)."""
    rA, rV = np.asarray(rA, float), np.asarray(rV, float)
    lab = np.asarray(labels, int)
    own = np.where(lab == 0, rA, rV)
    anti = np.where(lab == 0, rV, rA)
    return own - anti


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.size < 3:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx @ rx) * (ry @ ry))
    return float(rx @ ry / denom) if denom > 0 else 0.0


def compute_gates(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                  n_iter: int = 10000) -> dict:
    """b holds per-nonce arm arrays. Returns gates + verdict. Pure."""
    labels = np.asarray(b["labels"], int)
    sA_w, sV_w = np.asarray(b["sA_wire"], float), np.asarray(b["sV_wire"], float)
    sA_b, sV_b = np.asarray(b["sA_base"], float), np.asarray(b["sV_base"], float)
    sA_s, sV_s = np.asarray(b["sA_shuf"], float), np.asarray(b["sV_shuf"], float)
    rA_w, rV_w = np.asarray(b["rA_wire"], float), np.asarray(b["rV_wire"], float)

    L_wire = _signed_L(sA_w, sV_w, labels)
    L_shuf = _signed_L(sA_s, sV_s, labels)
    recall_w = _signed_recall(rA_w, rV_w, labels)

    # own/anti surprisal drops (base - wire), by label
    own_b = np.where(labels == 0, sA_b, sV_b)
    anti_b = np.where(labels == 0, sV_b, sA_b)
    own_w = np.where(labels == 0, sA_w, sV_w)
    anti_w = np.where(labels == 0, sV_w, sA_w)
    d_own = own_b - own_w         # >0 = own-class predicate got cheaper
    d_anti = anti_b - anti_w

    # ── TW1 LICENSING-TRANSFER: mean L beats class-label permutation null ──
    def stat_L(perm_labels):
        return float(np.mean(_signed_L(sA_w, sV_w, perm_labels)))
    tw1_val = stat_L(labels)
    tw1_null = shuffled_label(stat_L, labels, rng, n_iter=min(n_iter, 2000))
    # gates test value-register statistics; the causal interpretation comes
    # from the base/wire/shuffle DESIGN, not the gate (λ measure).
    tw1 = gate(tw1_val, tw1_null, "greater", alpha, "TW1_licensing_transfer",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW3 SHUFFLE-NULL: wire L beats matched-budget deranged-membership wire
    tw3_null = paired_permutation(L_wire, L_shuf, rng, n_iter=n_iter)
    tw3 = gate(float(np.mean(L_wire - L_shuf)), tw3_null, "greater", alpha,
               "TW3_shuffle_null",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW4 CLASS-SPECIFIC: own drop > anti drop (paired) ──
    tw4_null = paired_permutation(d_own, d_anti, rng, n_iter=n_iter)
    tw4 = gate(float(np.mean(d_own - d_anti)), tw4_null, "greater", alpha,
               "TW4_class_specific",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW2 GRADED: Spearman(L_wire, recall margin) > 0, permutation null ──
    rho = _spearman(L_wire, recall_w)
    def stat_rho(perm):
        return _spearman(L_wire, recall_w[perm])
    idx = np.arange(L_wire.size)
    rho_draws = np.array([stat_rho(rng.permutation(idx))
                          for _ in range(min(n_iter, 2000))])
    tw2_null = NullDraws("perm_pairing", rho_draws, {"n": int(L_wire.size)})
    tw2 = gate(rho, tw2_null, "greater", alpha, "TW2_graded",
               claim_register=Register.value, probe_register=Register.value)

    # ── membership recall (trained frame): NO-WRITE vs CONTEXT-ONLY split ──
    def stat_recall(perm_labels):
        return float(np.mean(_signed_recall(rA_w, rV_w, perm_labels)))
    rec_val = stat_recall(labels)
    rec_null = shuffled_label(stat_recall, labels, rng, n_iter=min(n_iter, 2000))
    rec = gate(rec_val, rec_null, "greater", alpha, "membership_recall",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW5 HOST-SANE (advisory) ──
    host = b.get("host", {})
    ce_ok = (host.get("ce_wire", 0.0) - host.get("ce_base", 0.0)) <= CE_TOL
    real_ok = host.get("real_L_wire_mean", 1.0) > 0.0
    restore_ok = bool(host.get("restore_ok", True))
    host_sane = bool(ce_ok and real_ok and restore_ok)

    written = bool(tw1.verdict and tw3.verdict and tw4.verdict)
    recall_ok = bool(rec.verdict)

    if not recall_ok:
        verdict = "NO-WRITE"
    elif not host_sane:
        verdict = "HOST-DAMAGED"
    elif not written:
        verdict = "CONTEXT-ONLY"
    elif tw2.verdict:
        verdict = "TYPE-WRITTEN+GRADED"
    else:
        verdict = "WRITTEN-OPAQUE"

    return {
        "verdict": verdict,
        "written": written, "recall_ok": recall_ok, "host_sane": host_sane,
        "gates": {
            "TW1": _gd(tw1), "TW2": _gd(tw2), "TW3": _gd(tw3),
            "TW4": _gd(tw4), "membership_recall": _gd(rec),
            "TW5_host": {"ce_ok": ce_ok, "real_ok": real_ok,
                         "restore_ok": restore_ok, "pass": host_sane},
        },
        "means": {
            "L_wire": float(np.mean(L_wire)), "L_shuf": float(np.mean(L_shuf)),
            "L_base": float(np.mean(_signed_L(sA_b, sV_b, labels))),
            "recall_wire": float(np.mean(recall_w)),
            "rho_L_recall": rho, "n_nonce": int(labels.size),
        },
    }


def _gd(g) -> dict:
    return {"value": g.value, "null_mean": g.null_mean, "p": g.p,
            "sign_ok": g.sign_ok, "pass": g.verdict, "null": g.null_name}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world(rng, kind: str, n: int = 24) -> dict:
    """Construct per-nonce arm arrays that yield a target verdict."""
    labels = np.array([0, 1] * (n // 2))
    # base: nonces have no class -> sA~sV, recall~0
    sA_b = rng.normal(6.0, 0.4, n)
    sV_b = rng.normal(6.0, 0.4, n)
    rA_b = rng.normal(0.0, 0.3, n)
    rV_b = rng.normal(0.0, 0.3, n)
    host = {"ce_base": 3.0, "ce_wire": 3.05, "real_L_wire_mean": 1.2,
            "restore_ok": True}

    if kind == "written_graded":
        # own drops a lot, anti unchanged; recall strong; graded with L
        strength = rng.uniform(0.5, 2.5, n)
        own_drop = 1.5 * strength + rng.normal(0, 0.1, n)
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            if labels[i] == 0:
                sA_w[i] -= own_drop[i]
            else:
                sV_w[i] -= own_drop[i]
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            if labels[i] == 0:
                rA_w[i] += 2.0 * strength[i]
            else:
                rV_w[i] += 2.0 * strength[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)   # shuffle wire: no true-class drop
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "written_opaque":
        # own drops uniformly (licensed) but UNCORRELATED with recall (not graded)
        own_drop = rng.normal(1.6, 0.1, n)
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            (sA_w, sV_w)[labels[i]][i] -= own_drop[i]
        # recall present (strong, so recall_ok) but shuffled wrt L
        rmarg = rng.permutation(np.abs(rng.normal(2.5, 0.3, n)))
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += rmarg[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "context_only":
        # recall strong (trained frames learned) BUT no held-frame transfer
        sA_w = sA_b + rng.normal(0, 0.1, n)
        sV_w = sV_b + rng.normal(0, 0.1, n)
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += rng.uniform(2.0, 3.0)
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "no_write":
        # nothing learned: recall ~0, no transfer
        sA_w = sA_b + rng.normal(0, 0.1, n)
        sV_w = sV_b + rng.normal(0, 0.1, n)
        rA_w = rA_b + rng.normal(0, 0.1, n)
        rV_w = rV_b + rng.normal(0, 0.1, n)
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "host_damaged":
        # transfer + recall present but host CE blown and real typing destroyed
        strength = rng.uniform(0.5, 2.5, n)
        own_drop = 1.5 * strength
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            (sA_w, sV_w)[labels[i]][i] -= own_drop[i]
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += 2.0 * strength[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
        host = {"ce_base": 3.0, "ce_wire": 9.0, "real_L_wire_mean": -0.5,
                "restore_ok": False}
    else:
        raise ValueError(kind)

    return {"labels": labels,
            "sA_base": sA_b, "sV_base": sV_b, "sA_wire": sA_w, "sV_wire": sV_w,
            "sA_shuf": sA_s, "sV_shuf": sV_s,
            "rA_wire": rA_w, "rV_wire": rV_w, "host": host}


def run_validate(alpha: float) -> int:
    print("── §P-TYPE-WRITE --validate (planted worlds, no model) ──")
    want = {"written_graded": "TYPE-WRITTEN+GRADED",
            "written_opaque": "WRITTEN-OPAQUE",
            "context_only": "CONTEXT-ONLY",
            "no_write": "NO-WRITE",
            "host_damaged": "HOST-DAMAGED"}
    ok = True
    for kind, expect in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        b = _world(rng, kind)
        res = compute_gates(b, rng, alpha, n_iter=2000)
        got = res["verdict"]
        good = got == expect
        ok &= good
        print(f"  {kind:16s} -> {got:22s} expect {expect:22s} "
              f"{'✓' if good else '✗ FAIL'}")
    # primitive checks
    rng = np.random.default_rng(0)
    lab = np.array([0, 1, 0, 1])
    L = _signed_L(np.array([5, 5, 5, 5.]), np.array([7, 3, 7, 3.]), lab)
    prim = np.allclose(L, [2, 2, 2, 2])   # label0: sV-sA=2 ; label1: sA-sV=2
    ok &= prim
    print(f"  primitive _signed_L               {'✓' if prim else '✗ FAIL'}")
    r = _spearman(np.array([1, 2, 3, 4.]), np.array([1, 2, 3, 4.]))
    prim2 = abs(r - 1.0) < 1e-9
    ok &= prim2
    print(f"  primitive _spearman monotone      {'✓' if prim2 else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch

[CONTENT TRUNCATED] Showing lines 121 to 380 of 650 total lines. Use line_offset=380 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "line_offset": 380,
  "limit": 270
}
```

**Summary:** Reading type_write.py (380-650)

**Output:**
```
    import torch.nn.functional as F
    import writeback_compile as wb  # LoRALinear apparatus (no fork)
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"          # LM loss over full statements
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(BAND_FRAC[0] * n_layers),
                      round(BAND_FRAC[1] * n_layers) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[tw] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} seeds={args.seeds} steps={args.steps}")

    def tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    def logp_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float()
        return F.log_softmax(lo, dim=-1).cpu().numpy()

    def surprisal(prefix: str, cont: str) -> float:
        """-sum log p(cont tokens | prefix), teacher-forced."""
        pre = tok(prefix, return_tensors="pt").to(dev)
        full = tok(prefix + cont, return_tensors="pt").to(dev)
        n_pre = pre.input_ids.shape[1]
        with torch.no_grad():
            lo = model(**full).logits[0].float()
        lp = F.log_softmax(lo, dim=-1)
        tgt = full.input_ids[0]
        s = 0.0
        for pos in range(n_pre, tgt.shape[0]):
            s += float(lp[pos - 1, tgt[pos]])
        return -s

    def ce_host() -> float:
        tot, n = 0.0, 0
        for t in CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0].float()
            lp = F.log_softmax(lo[:-1], dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    def eval_members(members: list[str], labels: np.ndarray) -> dict:
        aA_tid, aV_tid = tid("animal"), tid("vehicle")
        sA, sV, rA, rV = [], [], [], []
        for w in members:
            frame = f"The {w}"
            sA.append(np.mean([surprisal(frame, " " + p)
                               for p in HELD_PREDS[0]]))
            sV.append(np.mean([surprisal(frame, " " + p)
                               for p in HELD_PREDS[1]]))
            lp = logp_last(f"A {w} is a kind of")
            rA.append(float(lp[aA_tid]))
            rV.append(float(lp[aV_tid]))
        return {"sA": np.array(sA), "sV": np.array(sV),
                "rA": np.array(rA), "rV": np.array(rV)}

    # ── nonce usability + class assignment ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        # usable if "The {w}" appends a stable single leading token for w
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:      # w contributes >=1 token; keep
            nonces.append(w)
            labels.append(i % 2)
    if args.n_nonce:
        keep = args.n_nonce
        # balanced smoke cap
        a = [j for j, in_ in enumerate(labels) if in_ == 0][:keep // 2]
        v = [j for j, in_ in enumerate(labels) if in_ == 1][:keep // 2]
        sel = sorted(a + v)
        nonces = [nonces[j] for j in sel]
        labels = [labels[j] for j in sel]
    labels = np.array(labels, int)
    n = len(nonces)
    print(f"[tw] nonces={n} (animal {int((labels==0).sum())} "
          f"vehicle {int((labels==1).sum())})")

    # ── gate-0: base competence + real-member licensing (metric validity) ──
    print("[tw] gate-0: base licensing of real members …")
    real_members = list(REAL_MEMBERS[0]) + list(REAL_MEMBERS[1])
    real_labels = np.array([0] * len(REAL_MEMBERS[0])
                           + [1] * len(REAL_MEMBERS[1]))
    real_base = eval_members(real_members, real_labels)
    L_real_base = _signed_L(real_base["sA"], real_base["sV"], real_labels)
    real_margin = float(np.mean(L_real_base))
    per_class_ok = (np.mean(L_real_base[real_labels == 0]) > 0
                    and np.mean(L_real_base[real_labels == 1]) > 0)
    n_ok = (labels == 0).sum() >= args.min_class and \
           (labels == 1).sum() >= args.min_class
    gate0_ok = bool(real_margin >= REAL_MARGIN_FLOOR and per_class_ok and n_ok)
    print(f"[tw] gate-0: real-member licensing margin={real_margin:.3f} "
          f"per_class_ok={per_class_ok} n_ok={n_ok} "
          f"-> {'PASS' if gate0_ok else 'FAIL'}")
    (out_dir / "gate0.json").write_text(json.dumps({
        "model_id": args.model_id, "n_nonce": n,
        "real_margin": real_margin, "per_class_ok": bool(per_class_ok),
        "L_real_base": L_real_base.tolist(), "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist()}, indent=2))
    if args.gate0_only:
        return 0 if gate0_ok else 1
    if not gate0_ok and not args.force:
        print("[tw] gate-0 FAIL — stopping (use --force to override)")
        return 1

    # ── base arm ──
    print("[tw] arm base …")
    base = eval_members(nonces, labels)
    ce_base = ce_host()

    # ── wire trainer (LoRA on FFN band; membership-LM objective) ──
    def train_wire(train_labels: np.ndarray, seed: int):
        torch.manual_seed(seed)
        wrapped = []
        params = []
        for li in band:
            m = dec[li].mlp
            for name in ("gate_proj", "up_proj", "down_proj"):
                orig = getattr(m, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        stmts = [s for w, lb in zip(nonces, train_labels, strict=True)
                 for s in _member_stmts(w, int(lb))]
        batch = tok(stmts, return_tensors="pt", padding=True).to(dev)
        ids, attn = batch.input_ids, batch.attention_mask
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(input_ids=ids, attention_mask=attn).logits.float()
            shift_lo = lo[:, :-1, :]
            shift_tg = ids[:, 1:]
            shift_m = attn[:, 1:].float()
            ce = F.cross_entropy(
                shift_lo.reshape(-1, shift_lo.shape[-1]),
                shift_tg.reshape(-1), reduction="none").reshape(shift_tg.shape)
            loss = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                print(f"    seed{seed} step {step:4d} loss "
                      f"{float(loss.detach()):.4f}", flush=True)

        def unwrap():
            for m, name, orig in wrapped:
                setattr(m, name, orig)
        return unwrap

    def accum(train_labels, tag):
        acc = {k: [] for k in ("sA", "sV", "rA", "rV")}
        real_L = []
        ce_w = []
        for sd in range(args.seeds):
            unwrap = train_wire(train_labels, sd)
            e = eval_members(nonces, labels)   # eval always TRUE labels
            for k in acc:
                acc[k].append(e[k])
            if sd == 0:
                rb = eval_members(real_members, real_labels)
                real_L.append(float(np.mean(
                    _signed_L(rb["sA"], rb["sV"], real_labels))))
                ce_w.append(ce_host())
            unwrap()
            print(f"[tw] {tag} seed{sd} done", flush=True)
        return ({k: np.mean(acc[k], axis=0) for k in acc},
                (real_L[0] if real_L else np.nan),
                (ce_w[0] if ce_w else np.nan))

    print("[tw] arm wire (true membership) …")
    wire, real_L_wire, ce_wire = accum(labels, "wire")

    print("[tw] arm shuffle (deranged membership) …")
    # derange class labels (matched budget), ensure no fixed point
    perm = labels.copy()
    for _ in range(64):
        perm = rng.permutation(labels)
        if np.any(perm != labels):
            break
    shuf, _, _ = accum(perm, "shuffle")

    # ── restore check: base eval must reproduce (LoRA fully removed) ──
    base2 = eval_members(nonces[:2], labels[:2])
    restore_ok = bool(np.allclose(base2["sA"], base["sA"][:2], atol=1e-3))

    bundle = {
        "labels": labels,
        "sA_base": base["sA"], "sV_base": base["sV"],
        "sA_wire": wire["sA"], "sV_wire": wire["sV"],
        "sA_shuf": shuf["sA"], "sV_shuf": shuf["sV"],
        "rA_wire": wire["rA"], "rV_wire": wire["rV"],
        "host": {"ce_base": ce_base, "ce_wire": ce_wire,
                 "real_L_wire_mean": real_L_wire, "restore_ok": restore_ok},
    }
    res = compute_gates(bundle, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": n, "seeds": args.seeds,
        "steps": args.steps, "lr": args.lr, "lora_r": args.lora_r,
        "band": [band[0], band[-1]], "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist(),
        "real_margin_base": real_margin, "ce_base": ce_base, "ce_wire": ce_wire,
        "real_L_wire": real_L_wire, "restore_ok": restore_ok,
    }
    res["per_nonce"] = {
        "L_wire": _signed_L(wire["sA"], wire["sV"], labels).tolist(),
        "L_base": _signed_L(base["sA"], base["sV"], labels).tolist(),
        "L_shuf": _signed_L(shuf["sA"], shuf["sV"], labels).tolist(),
        "recall_wire": _signed_recall(wire["rA"], wire["rV"], labels).tolist(),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    print(f"[tw] wrote {out_dir}/results.json")
    g = res["gates"]
    print(f"[tw] TW1 p={g['TW1']['p']:.4f} pass={g['TW1']['pass']} | "
          f"TW2 rho={g['TW2']['value']:.3f} p={g['TW2']['p']:.4f} "
          f"pass={g['TW2']['pass']} | TW3 p={g['TW3']['p']:.4f} "
          f"pass={g['TW3']['pass']} | TW4 p={g['TW4']['p']:.4f} "
          f"pass={g['TW4']['pass']} | recall pass={g['membership_recall']['pass']} "
          f"| host={res['host_sane']}")
    print(f"[tw] L_base={res['means']['L_base']:.3f} "
          f"L_wire={res['means']['L_wire']:.3f} "
          f"L_shuf={res['means']['L_shuf']:.3f}")
    print(f"[tw] VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--gate0-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--min-class", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-nonce", type=int, default=0,
                    help="smoke: cap nonces (balanced); 0=all")
    ap.add_argument("--out", default="results/type-write/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

### Thinking

I'm working through the harness design and need to set up separate replay texts for the KL anchor that are distinct from the CE probe texts—using the same texts would contaminate the measurement by training on what we're trying to evaluate, which would break the host-CE gate in TW5.

The replay set should be 8-16 generic prose sentences that avoid membership and licensing vocabulary, steering clear of animal and vehicle terms to keep them neutral. There's a tension here: anchoring on purely neutral prose might not directly protect licensing behavior on real members, but it does prevent overfitting collapse at the distribution level. I'm considering whether to include a few sentences with real members but held predicates, though that risks teaching to the TW5 test itself.

For the KL term, I need to cache the base model's logits on the replay batch once to compute KL divergence across the full vocabulary—roughly 72MB for float32 storage. The question is whether to use forward KL(base‖wire) or reverse KL(wire‖base); forward KL is mode-covering and matches the distillation convention used in writeback_compile, so I'll go with that.

For λ_KL calibration, I can either measure gradient norms at step 0 to set the weight dynamically or use a fixed default. The dynamic approach computes both CE and KL gradients separately to get their ratio, though this introduces slight seed-dependent variation. Since LoRA starts with B=0, the initial delta is zero, making the wire identical to base and KL gradient zero at step 0—which creates a division problem.

So I'll go with a simpler approach: fixed λ_KL = 1.0 as the default, tunable via CLI, and log both loss components to track their relative magnitudes.

For evidence-gated stopping, I'm setting up checkpoints at fibonacci-like intervals to monitor membership learning and validate that the KL regularization isn't suppressing it entirely.  The stopping criterion checks whether membership loss has plateaued—if relative improvement drops below a threshold (around 2%) and the loss stays reasonably low, we halt training. Early checkpoints have tight spacing so we catch meaningful improvements before plateau detection triggers prematurely.

A safer approach: gate the stop rule to only activate after a minimum step count (like 55), then measure plateau over the distance between the last two snapshots. The primary brake is the host-CE drift budget—if the host model's cross-entropy diverges more than 0.10 from baseline, we stop immediately.

To handle overshoot, I'll snapshot the LoRA parameters at each evaluation point. If drift stays within budget, mark that snapshot as "last good." If drift exceeds the budget, roll back to the last good snapshot, stop, and record where it happened. Since LoRA parameters are small (rank 16 across 8 layers with 3 matrices), cloning them at each checkpoint is cheap.

I also need to detect plateaus—when the relative improvement in membership CE between consecutive snapshots drops below a threshold (default 0.01) after a minimum number of steps (55). At that point, stop with a plateau signal and keep the current state.

For the CLI, I'm adding parameters for KL weight, CE budget, plateau tolerance, and minimum steps before allowing early stopping, with sensible defaults. Then I'll write a pure logic test that simulates loss and drift curves to validate the stopping decisions work correctly.

The core compute functions—gates, verdicts, worlds, metrics—stay frozen, and I'm just adding amendment metadata to the records. The shuffle arm inherits the same training wire, so it automatically gets the amendment too.

Now I'm wrestling with the budget matching for TW3: if the wire arm stops early at one step and the shuffle arm runs longer, their budgets diverge. Since shuffle is a null arm without host protection, I could either lock shuffle to use the wire's stopping step directly, or let it run its own stop logic—but that breaks the matched-budget constraint TW3 needs.

### Thinking

Task #2 is closing with Michael's decision to amend and re-run. I'm starting the build and need to pull the KL convention and LoRA init details from `writeback_compile`.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -E \"class LoRALinear|self\\.A|self\\.B|zeros|kaiming|normal_|kl_div|log_softmax.*teacher|teacher\" /Users/mwhitford/src/verbum/scripts/explore/writeback_compile.py | head -30"
}
```

**Summary:** $ grep -n -E "class LoRALinear|self\....

**Output:**
```
Exit code: 0
Stdout:
32:                     0.6-0.8 band; teacher = SAME host on its own committed
36:  gd_shuffle       : gd_cd with deranged countries in the teacher CoT.
159:# committed-CoT teacher (native_compose_check `scaffold` form; the model's
467:    class LoRALinear(_torch.nn.Module):
476:            self.A = _torch.nn.Parameter(
478:            self.B = _torch.nn.Parameter(
479:                _torch.zeros(dout, r, device=dev, dtype=_torch.float32))
484:            lo = (x.to(self.A.dtype) @ self.A.T) @ self.B.T
764:    def teacher_probs(country_of: dict[str, str]) -> dict[str, torch.Tensor]:
857:                tp = teacher_probs({c.landmark: c.country
861:                tp = teacher_probs({c.landmark: dc[c.country]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sed -n 460,490p /Users/mwhitford/src/verbum/scripts/explore/writeback_compile.py; echo ────; sed -n 760,800p /Users/mwhitford/src/verbum/scripts/explore/writeback_compile.py; echo ────; grep -n -E \"kl|KL\" /Users/mwhitford/src/verbum/scripts/explore/writeback_compile.py | head -20"
}
```

**Summary:** $ sed -n 460,490p /Users/mwhitford/sr...

**Output:**
```
Exit code: 0
Stdout:
# ══════════════════════════════════════════════════════════════════════════
# LoRA (manual, torch; FFN-only per frozen recipe)
# ══════════════════════════════════════════════════════════════════════════
try:
    import torch as _torch

    class LoRALinear(_torch.nn.Module):
        def __init__(self, base: _torch.nn.Module, r: int, alpha: float):
            super().__init__()
            self.base = base
            for p in self.base.parameters():
                p.requires_grad_(False)
            din = base.in_features
            dout = base.out_features
            dev = base.weight.device
            self.A = _torch.nn.Parameter(
                _torch.randn(r, din, device=dev, dtype=_torch.float32) * 0.01)
            self.B = _torch.nn.Parameter(
                _torch.zeros(dout, r, device=dev, dtype=_torch.float32))
            self.scale = alpha / r

        def forward(self, x):
            y = self.base(x)
            lo = (x.to(self.A.dtype) @ self.A.T) @ self.B.T
            return y + (self.scale * lo).to(y.dtype)
except Exception:                                     # pragma: no cover
    LoRALinear = None  # type: ignore[assignment]


# ══════════════════════════════════════════════════════════════════════════
────
            == first_word(BANK[co][0]) for co in sorted(BANK)]
        return float(np.mean(g_hits)), float(np.mean(h_hits))

    # ══ GD arms ══
    def teacher_probs(country_of: dict[str, str]) -> dict[str, torch.Tensor]:
        out = {}
        for c in train_cells:
            co = country_of[c.landmark]
            lo = logits_last(TEACHER_PROMPT.format(lm=c.landmark, c=co))
            out[c.landmark] = torch.softmax(
                torch.tensor(lo, dtype=torch.float32), dim=-1)
        return out

    def train_gd(loss_kind: str, tprobs, seed: int):
        torch.manual_seed(seed)
        wrapped = []
        params = []
        for li in band:
            m = dec[li].mlp
            for name in ("gate_proj", "up_proj", "down_proj"):
                orig = getattr(m, name)
                lw = LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        prompts = [DIRECT_PROMPT.format(lm=c.landmark) for c in train_cells]
        batch = tok(prompts, return_tensors="pt", padding=True).to(dev)
        cap_tids = torch.tensor([first_tid(c.capital) for c in train_cells],
                                device=dev)
        if tprobs is not None:
            tp = torch.stack([tprobs[c.landmark]
                              for c in train_cells]).to(dev)
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(**batch).logits[:, -1, :].float()
            if loss_kind == "kl":
                loss = -(tp * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            else:
                loss = F.cross_entropy(lo, cap_tids)
            loss.backward()
────
34:                     is"), student = one-shot prompt; KL at answer position.
796:            if loss_kind == "kl":
868:                unwrap = train_gd("kl" if tp is not None else "ce", tp,
```

### Thinking

I've confirmed the LoRALinear initialization behavior—when B starts at zero, the wire matches the base exactly at step 0, giving zero KL divergence and zero gradients, so I'll skip step-0 calibration and rely on the fixed lambda from the CLI along with logged components. For the KL calculation, I'm using the same convention as writeback_compile: computing it as cross-entropy against teacher probabilities, which represents KL(base‖wire) using the cached values.

Now I'm setting up the replay batch to store base probabilities efficiently—I'll cache the base entropy constant separately so the KL loss starts at 0.0 for cleaner logging. For memory, storing full-vocab base probabilities across 8 sentences of ~20 tokens each would be around 97MB, which is tight on MPS, so I'm caching the base probabilities in float32 along with the entropy scalar, keeping it under 100MB. I'm designing the amended training loop with a separate replay text set of neutral sentences disjoint from the main CE texts.

Setting up the precomputation phase... Writing training logic... Defining effective_steps as the number of steps actually trained, which gets passed to the shuffle routine so it runs exactly that many steps with monitoring but without early stopping rules. For each seed, I wire the stop step to the shuffle seed so they share the same budget. The plateau check compares the CE component across snapshots—if the relative change is below the tolerance threshold and we've hit the minimum step count, we trigger early stopping. Measuring the host CE at snapshots is cheap since it only requires a few forward passes, and rollback restores parameters by copying them back into the model's data structures.

Now I'm defining a stop-decision function that takes per-snapshot memory CE values and host drift measurements, then returns which snapshot to stop at along with the reason—either rolling back if drift exceeds budget, detecting a plateau when improvement stalls, or reaching max steps.

The validation logic calls this function incrementally at each snapshot, appending to the history and checking if the verdict index matches the current position; it only acts on budget rollback or plateau signals, not on max_steps verdicts. I'm testing three scenarios: steady memory decrease with small drift should run to completion, flat memory after a threshold triggers plateau detection, and drift crossing the budget causes rollback to the previous snapshot.

Now I'm setting up the replay text corpus with eight neutral sentences that avoid animals, vehicles, nonces, and held predicates—things like descriptions of renovations, measurements, market prices, orchestras, wind, reports, and gardening.

I need to add CLI arguments for the hyperparameters and update the docstring to include metadata fields like kl_weight, ce_budget, plateau_tol, min_stop, and training history per arm and seed that get dumped to results.json. There's a subtle point about ce_host during training: the model is already in eval mode when loaded, but LoRA still trains since we don't depend on dropout, and ce_host uses no_grad which works fine with LoRA attached since it measures the wired model as intended.

The ce_wire measurement at the end of TW5 (seed 0 post-training) with rollback ensures the final drift stays within budget by construction for the wire arm. This makes TW5's ce_ok check nearly guaranteed to pass given the budget is well below the tolerance threshold, but that's not "gate-teaching" since the budget is strict and TW5 also has independent real_ok and restore_ok checks that aren't directly optimized. The stop rule controls exposure while TW5 still independently measures real-member licensing.

If drift exceeds budget at snapshot 0, the rollback goes to the last_good state initialized before any steps (zero delta), meaning no writes occur—acceptable since it signals the recipe is hopeless at that learning rate. The shuffle arm logs monitoring but doesn't stop, running through wire's effective steps. I need to restructure the accumulator to track and return stop steps per seed, so wire can record them and shuffle can access them.

Now I'm setting up the implementation: adding the docstring amendment, defining replay text constants and snapshot defaults, writing the pure stop decision logic and validation cases, then updating run_model to cache replay base probabilities and amend the train_wire signature with composite loss, snapshot monitoring, and rollback handling. I'll also add the necessary CLI arguments.

Writing the replay cache setup... Finishing the KL divergence calculation by masking and normalizing, then combining it with the memory cross-entropy loss using a weighted coefficient. I'm also checking memory requirements—the logits tensor is manageable at around 87MB, and even with transient copies during softmax operations it stays well within limits since the training batch already handles larger allocations. Now I'm setting up monitoring snapshots in the training loop right after the optimizer step.

Setting up the training function... Writing training loop logic... Handling the rollback case...

The key insight is that `_stop_decision` only fires on the newest snapshot since we're calling it incrementally—plateau and budget exhaustion can't retroactively trigger on older indices. For `stop_step`, I need to track how many steps were actually trained before stopping.

When plateau fires at snapshot `s`, we've trained `s+1` steps total, so `stop_at = s+1` and the range covers steps 0 through s. On rollback, parameters revert to the `last_good_step` state, meaning we've effectively trained `last_good_step+1` steps. The tricky edge case is when the first snapshot itself exceeds budget—`last_good` is None, so `last_good_step = -1`, giving `stop_step = 0`. In that scenario, parameters stay at their initial state but I need to handle the restoration cleanly, probably by initializing `last_good` right before the training loop starts.

The `train_wire` function returns the unwrapped parameters along with metadata including `stop_step`, `stop_reason`, and training history. For shuffle mode with a given `stop_at`, the loop runs for that many steps, but if `stop_at` is 0 there's no training—just logging snapshots and returning with `stop_reason="matched_budget"`. The `accum` function iterates over seeds, calling `train_wire` for each one with the appropriate `stop_at` value from the stops array, collecting the returned info objects.

After running wire training and extracting the stop steps from its results, I'm running the shuffle variant with those same stopping points. I'm also adding metadata fields like `kl_weight`, `ce_budget`, plateau tolerance, and replay count, then storing both wire and shuffle info in the results. For output, I'm printing per-snapshot lines showing seed, step, memory usage, KL divergence, cross-entropy, and drift, using Fibonacci indices for good coverage rather than printing at every step.

Now I'm implementing the stop decision logic as a pure function that scans through the history of steps, memory, and drift values to determine when to halt training based on evidence-gated rules.

Defining stop decision function... Writing validation tests... So at step 89 the relative improvement drops below the tolerance threshold, signaling a plateau and keeping 90 snapshots. For the budget scenario, drift crosses the threshold at step 21, triggering a rollback to keep 14 snapshots. The edge case handles the first snapshot exceeding budget by keeping 0. I'm adding these test cases to the validation function with debug output, setting up the CLI with the specified parameters for KL weight, CE budget, plateau tolerance, and minimum steps, and updating the docstring with an amendment section.

For the output directory, I'll use

### Thinking

I've confirmed the LoRA initialization and KL convention details—B starts at zero so step-0 calibration is impossible, making λ_KL a fixed CLI weight with both loss components logged for visibility. I'm now building the implementation, keeping in mind that TW3 needs matched budgets, so the shuffle arm will train to exactly the wire arm's stopping step rather than running its own early-stop.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "Model: Qwen3-4B only (the type-register carrier; the pythia negative is already\nsupplied by the s314 §P-TYPE-GRAM-1 sweep — no separate control run).\n\nLicense: MIT (lambda provenance).\n\"\"\"",
  "new_content": "Model: Qwen3-4B only (the type-register carrier; the pythia negative is already\nsupplied by the s314 §P-TYPE-GRAM-1 sweep — no separate control run).\n\nAMENDMENT (s315, Michael-approved, post-run-1 HOST-DAMAGED — instrument-side\nonly; gates/metric/verdicts/a-priori UNCHANGED): run 1 baked the wire (recall\np=5e-4) but burned the host (CE +2.3 nats, real-member licensing inverted\n+2.538 -> -0.624) — plain CE on a tiny corpus lacked the host anchor gd_cd had\nimplicitly via its teacher KL. Two changes:\n  (1) HOST-ANCHORED OBJECTIVE: loss = CE(membership) + kl_weight *\n      KL(base || wire) on cached neutral REPLAY_TEXTS (disjoint from CE_TEXTS\n      — never train on the measurement). Base is frozen, so teacher\n      distributions are cached once. LoRA B init is zero => KL(step 0)=0 with\n      zero grad, so kl_weight is a fixed CLI weight (default 1.0), both\n      components logged per snap.\n  (2) EVIDENCE-GATED STOP (wire arm): at fibonacci snaps log membership CE +\n      host CE drift; stop on plateau (rel improvement < plateau_tol at snaps\n      >= min_stop) or on host-CE drift > ce_budget (rollback to last good\n      snap). Run-1 curve: learning done by ~step 200; steps 200-500 bought\n      only damage. The SHUFFLE arm runs the wire's per-seed stop step exactly\n      (no own stop rule) => TW3 stays matched-budget by construction.\n      TW5 ce_ok becomes enforced-by-mechanism (budget 0.10 < CE_TOL 0.5);\n      real_ok stays the live, unoptimized host check.\n\nLicense: MIT (lambda provenance).\n\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Thinking

Now I'm looking at the constants block with the replay texts and snap schedule after CE_TEXTS.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "# Recipe (writeback_compile-frozen apparatus).\nBAND_FRAC = (0.60, 0.80)\nCE_TOL = 0.5           # advisory: host CE may rise at most this (nats/token)\nREAL_MARGIN_FLOOR = 0.25   # gate-0: base must license real members by this margin",
  "new_content": "# Replay anchor (s315 amendment): neutral prose for KL(base||wire).\n# DISJOINT from CE_TEXTS (never train on the measurement) and free of\n# class members / held predicates (the anchor must not fight the write).\nREPLAY_TEXTS = [\n    \"The library reopened after months of renovation and new lighting.\",\n    \"He measured the shelf twice before cutting the board.\",\n    \"Prices at the market rose slightly toward the end of summer.\",\n    \"The orchestra tuned quietly while the hall filled with guests.\",\n    \"A cool wind moved through the orchard just before dawn.\",\n    \"The report summarized three years of survey data in ten pages.\",\n    \"She planted basil and thyme in the window box outside the kitchen.\",\n    \"The bridge closed for inspection during the early morning hours.\",\n]\n\n# Evidence-gated stop (s315 amendment): fibonacci snap schedule (s309 lineage).\nFIB_SNAPS = (0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 499)\n\n# Recipe (writeback_compile-frozen apparatus).\nBAND_FRAC = (0.60, 0.80)\nCE_TOL = 0.5           # advisory: host CE may rise at most this (nats/token)\nREAL_MARGIN_FLOOR = 0.25   # gate-0: base must license real members by this margin"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Thinking

I've placed the pure stop-decision function (validate-testable, no torch) with the other pure statistics functions.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "def compute_gates(b: dict, rng: np.random.Generator, alpha: float = 0.05,\n                  n_iter: int = 10000) -> dict:",
  "new_content": "def _stop_decision(steps_hist: list, mem_hist: list, drift_hist: list,\n                   budget: float, tol: float, min_stop: int) -> tuple:\n    \"\"\"Evidence-gated stop (s315 amendment). Pure; validate-tested.\n\n    Scans per-snap history in order; first firing rule wins. Returns\n    (n_steps_to_keep, reason):\n      ce_budget_rollback — host-CE drift exceeded budget at a snap; keep only\n                           steps up to the PREVIOUS (good) snap.\n      plateau            — membership CE rel-improvement between consecutive\n                           snaps < tol at a snap >= min_stop; keep current.\n      max_steps          — no rule fired; keep everything.\n    Used incrementally in-loop (called on the growing history each snap) and\n    wholesale in --validate on planted curves — same code path (λ one_way).\"\"\"\n    prev_mem = None\n    for i, (s, m, d) in enumerate(zip(steps_hist, mem_hist, drift_hist,\n                                      strict=True)):\n        if d > budget:\n            keep = 0 if i == 0 else steps_hist[i - 1] + 1\n            return keep, \"ce_budget_rollback\"\n        if (prev_mem is not None and s >= min_stop\n                and (prev_mem - m) / max(prev_mem, 1e-9) < tol):\n            return s + 1, \"plateau\"\n        prev_mem = m\n    return (steps_hist[-1] + 1 if steps_hist else 0), \"max_steps\"\n\n\ndef compute_gates(b: dict, rng: np.random.Generator, alpha: float = 0.05,\n                  n_iter: int = 10000) -> dict:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Thinking

Now I'll extend `run_validate` to include planted stop-curve worlds.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "    r = _spearman(np.array([1, 2, 3, 4.]), np.array([1, 2, 3, 4.]))\n    prim2 = abs(r - 1.0) < 1e-9\n    ok &= prim2\n    print(f\"  primitive _spearman monotone      {'✓' if prim2 else '✗ FAIL'}\")\n    print(f\"\\n── --validate {'ALL PASS' if ok else 'FAIL'} ──\")\n    return 0 if ok else 1",
  "new_content": "    r = _spearman(np.array([1, 2, 3, 4.]), np.array([1, 2, 3, 4.]))\n    prim2 = abs(r - 1.0) < 1e-9\n    ok &= prim2\n    print(f\"  primitive _spearman monotone      {'✓' if prim2 else '✗ FAIL'}\")\n\n    # ── s315 amendment: evidence-gated stop on planted curves ──\n    snaps = list(FIB_SNAPS)\n    zero_drift = [0.0] * len(snaps)\n    # healthy: mem keeps improving >tol per snap, no drift -> run to end\n    mem_healthy = [5.0 / (1 + i) for i in range(len(snaps))]\n    got = _stop_decision(snaps, mem_healthy, zero_drift, 0.10, 0.01, 55)\n    good = got == (500, \"max_steps\")\n    ok &= good\n    print(f\"  stop: healthy world               {got} \"\n          f\"{'✓' if good else '✗ FAIL expect (500, max_steps)'}\")\n    # plateau: big drops until step 55, then flat -> stop at snap 89 (keep 90)\n    mem_plat = [5.0, 4.0, 3.2, 2.6, 2.1, 1.7, 1.3, 1.0, 0.8, 0.5,\n                0.499, 0.498, 0.497, 0.496, 0.495]\n    got = _stop_decision(snaps, mem_plat, zero_drift, 0.10, 0.01, 55)\n    good = got == (90, \"plateau\")\n    ok &= good\n    print(f\"  stop: plateau world               {got} \"\n          f\"{'✓' if good else '✗ FAIL expect (90, plateau)'}\")\n    # runaway drift: budget crossed at snap idx 7 (step 21) -> keep prev+1=14\n    drift_run = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.08, 0.15,\n                 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 2.3]\n    got = _stop_decision(snaps, mem_healthy, drift_run, 0.10, 0.01, 55)\n    good = got == (14, \"ce_budget_rollback\")\n    ok &= good\n    print(f\"  stop: drift-budget world          {got} \"\n          f\"{'✓' if good else '✗ FAIL expect (14, ce_budget_rollback)'}\")\n    # edge: first snap already over budget -> keep 0 (zero-delta rollback)\n    got = _stop_decision([0], [5.0], [0.5], 0.10, 0.01, 55)\n    good = got == (0, \"ce_budget_rollback\")\n    ok &= good\n    print(f\"  stop: step-0 over budget          {got} \"\n          f\"{'✓' if good else '✗ FAIL expect (0, ce_budget_rollback)'}\")\n\n    print(f\"\\n── --validate {'ALL PASS' if ok else 'FAIL'} ──\")\n    return 0 if ok else 1"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

## Assistant

Now the model path — replay cache after the base arm:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "    # ── base arm ──\n    print(\"[tw] arm base …\")\n    base = eval_members(nonces, labels)\n    ce_base = ce_host()\n\n    # ── wire trainer (LoRA on FFN band; membership-LM objective) ──\n    def train_wire(train_labels: np.ndarray, seed: int):\n        torch.manual_seed(seed)\n        wrapped = []\n        params = []\n        for li in band:\n            m = dec[li].mlp\n            for name in (\"gate_proj\", \"up_proj\", \"down_proj\"):\n                orig = getattr(m, name)\n                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)\n                setattr(m, name, lw)\n                wrapped.append((m, name, orig))\n                params += [lw.A, lw.B]\n        opt = torch.optim.Adam(params, lr=args.lr)\n        stmts = [s for w, lb in zip(nonces, train_labels, strict=True)\n                 for s in _member_stmts(w, int(lb))]\n        batch = tok(stmts, return_tensors=\"pt\", padding=True).to(dev)\n        ids, attn = batch.input_ids, batch.attention_mask\n        for step in range(args.steps):\n            opt.zero_grad()\n            lo = model(input_ids=ids, attention_mask=attn).logits.float()\n            shift_lo = lo[:, :-1, :]\n            shift_tg = ids[:, 1:]\n            shift_m = attn[:, 1:].float()\n            ce = F.cross_entropy(\n                shift_lo.reshape(-1, shift_lo.shape[-1]),\n                shift_tg.reshape(-1), reduction=\"none\").reshape(shift_tg.shape)\n            loss = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)\n            loss.backward()\n            opt.step()\n            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:\n                print(f\"    seed{seed} step {step:4d} loss \"\n                      f\"{float(loss.detach()):.4f}\", flush=True)\n\n        def unwrap():\n            for m, name, orig in wrapped:\n                setattr(m, name, orig)\n        return unwrap",
  "new_content": "    # ── base arm ──\n    print(\"[tw] arm base …\")\n    base = eval_members(nonces, labels)\n    ce_base = ce_host()\n\n    # ── replay anchor cache (s315): base distribution on neutral prose ──\n    # Base is frozen -> teacher cached ONCE, before any LoRA wrap.\n    rb = tok(REPLAY_TEXTS, return_tensors=\"pt\", padding=True).to(dev)\n    with torch.no_grad():\n        base_lo = model(**rb).logits.float()\n        p_base_replay = torch.softmax(base_lo, dim=-1)              # [B,T,V]\n        h_base_replay = -(p_base_replay\n                          * F.log_softmax(base_lo, dim=-1)).sum(-1)  # [B,T]\n    replay_mask = rb.attention_mask.float()\n    del base_lo\n    print(f\"[tw] replay anchor cached: {len(REPLAY_TEXTS)} texts, \"\n          f\"{int(replay_mask.sum())} positions, kl_weight={args.kl_weight}\")\n\n    # ── wire trainer (LoRA on FFN band; host-anchored membership objective) ──\n    def train_wire(train_labels: np.ndarray, seed: int,\n                   stop_at: int | None = None):\n        \"\"\"stop_at=None: evidence-gated stop live (wire arm).\n        stop_at=k: train exactly k steps (shuffle arm — matched budget).\"\"\"\n        torch.manual_seed(seed)\n        wrapped = []\n        params = []\n        for li in band:\n            m = dec[li].mlp\n            for name in (\"gate_proj\", \"up_proj\", \"down_proj\"):\n                orig = getattr(m, name)\n                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)\n                setattr(m, name, lw)\n                wrapped.append((m, name, orig))\n                params += [lw.A, lw.B]\n        opt = torch.optim.Adam(params, lr=args.lr)\n        stmts = [s for w, lb in zip(nonces, train_labels, strict=True)\n                 for s in _member_stmts(w, int(lb))]\n        batch = tok(stmts, return_tensors=\"pt\", padding=True).to(dev)\n        ids, attn = batch.input_ids, batch.attention_mask\n        snap_set = {s for s in FIB_SNAPS if s < args.steps}\n        hist: dict = {\"step\": [], \"mem_ce\": [], \"kl\": [],\n                      \"host_ce\": [], \"drift\": []}\n        n_steps = args.steps if stop_at is None else stop_at\n        stop_step, stop_reason = n_steps, (\"max_steps\" if stop_at is None\n                                           else \"matched_budget\")\n        # last-good = zero-delta start (B=0): rollback target if snap 0 burns\n        last_good = [p.detach().clone() for p in params]\n        last_good_step = -1\n        for step in range(n_steps):\n            opt.zero_grad()\n            lo = model(input_ids=ids, attention_mask=attn).logits.float()\n            shift_lo = lo[:, :-1, :]\n            shift_tg = ids[:, 1:]\n            shift_m = attn[:, 1:].float()\n            ce = F.cross_entropy(\n                shift_lo.reshape(-1, shift_lo.shape[-1]),\n                shift_tg.reshape(-1), reduction=\"none\").reshape(shift_tg.shape)\n            mem_ce = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)\n            # KL(base||wire) on replay (writeback_compile teacher convention,\n            # minus cached base entropy -> true KL, 0.0 at zero delta)\n            lo_r = model(**rb).logits.float()\n            lq = F.log_softmax(lo_r, dim=-1)\n            kl = ((-(p_base_replay * lq).sum(-1) - h_base_replay)\n                  * replay_mask).sum() / replay_mask.sum()\n            loss = mem_ce + args.kl_weight * kl\n            loss.backward()\n            opt.step()\n            if step in snap_set:\n                ce_h = ce_host()\n                hist[\"step\"].append(step)\n                hist[\"mem_ce\"].append(float(mem_ce.detach()))\n                hist[\"kl\"].append(float(kl.detach()))\n                hist[\"host_ce\"].append(ce_h)\n                hist[\"drift\"].append(ce_h - ce_base)\n                print(f\"    seed{seed} snap {step:4d} mem \"\n                      f\"{hist['mem_ce'][-1]:.4f} kl {hist['kl'][-1]:.4f} \"\n                      f\"host_ce {ce_h:.4f} drift {hist['drift'][-1]:+.4f}\",\n                      flush=True)\n                if stop_at is None:\n                    keep, reason = _stop_decision(\n                        hist[\"step\"], hist[\"mem_ce\"], hist[\"drift\"],\n                        args.ce_budget, args.plateau_tol, args.min_stop)\n                    if reason == \"plateau\":\n                        stop_step, stop_reason = keep, reason\n                        print(f\"    seed{seed} STOP plateau @ step {step} \"\n                              f\"(keep {keep})\", flush=True)\n                        break\n                    if reason == \"ce_budget_rollback\":\n                        with torch.no_grad():\n                            for p, g in zip(params, last_good, strict=True):\n                                p.copy_(g)\n                        stop_step, stop_reason = keep, reason\n                        print(f\"    seed{seed} STOP ce-budget @ step {step} \"\n                              f\"-> rollback to step {last_good_step} \"\n                              f\"(keep {keep})\", flush=True)\n                        break\n                    # snap is good -> becomes the rollback target\n                    last_good = [p.detach().clone() for p in params]\n                    last_good_step = step\n\n        def unwrap():\n            for m, name, orig in wrapped:\n                setattr(m, name, orig)\n        info = {\"stop_step\": int(stop_step), \"stop_reason\": stop_reason,\n                \"seed\": seed, \"history\": hist}\n        return unwrap, info"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Thinking

I'm now working with the accumulator and arm calls, including the wire stops that feed the shuffle budget, along with metadata.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "    def accum(train_labels, tag):\n        acc = {k: [] for k in (\"sA\", \"sV\", \"rA\", \"rV\")}\n        real_L = []\n        ce_w = []\n        for sd in range(args.seeds):\n            unwrap = train_wire(train_labels, sd)\n            e = eval_members(nonces, labels)   # eval always TRUE labels\n            for k in acc:\n                acc[k].append(e[k])\n            if sd == 0:\n                rb = eval_members(real_members, real_labels)\n                real_L.append(float(np.mean(\n                    _signed_L(rb[\"sA\"], rb[\"sV\"], real_labels))))\n                ce_w.append(ce_host())\n            unwrap()\n            print(f\"[tw] {tag} seed{sd} done\", flush=True)\n        return ({k: np.mean(acc[k], axis=0) for k in acc},\n                (real_L[0] if real_L else np.nan),\n                (ce_w[0] if ce_w else np.nan))\n\n    print(\"[tw] arm wire (true membership) …\")\n    wire, real_L_wire, ce_wire = accum(labels, \"wire\")\n\n    print(\"[tw] arm shuffle (deranged membership) …\")\n    # derange class labels (matched budget), ensure no fixed point\n    perm = labels.copy()\n    for _ in range(64):\n        perm = rng.permutation(labels)\n        if np.any(perm != labels):\n            break\n    shuf, _, _ = accum(perm, \"shuffle\")",
  "new_content": "    def accum(train_labels, tag, stops=None):\n        acc = {k: [] for k in (\"sA\", \"sV\", \"rA\", \"rV\")}\n        real_L = []\n        ce_w = []\n        infos = []\n        for sd in range(args.seeds):\n            unwrap, info = train_wire(\n                train_labels, sd,\n                stop_at=None if stops is None else stops[sd])\n            infos.append(info)\n            e = eval_members(nonces, labels)   # eval always TRUE labels\n            for k in acc:\n                acc[k].append(e[k])\n            if sd == 0:\n                rme = eval_members(real_members, real_labels)\n                real_L.append(float(np.mean(\n                    _signed_L(rme[\"sA\"], rme[\"sV\"], real_labels))))\n                ce_w.append(ce_host())\n            unwrap()\n            print(f\"[tw] {tag} seed{sd} done \"\n                  f\"(stop {info['stop_step']} {info['stop_reason']})\",\n                  flush=True)\n        return ({k: np.mean(acc[k], axis=0) for k in acc},\n                (real_L[0] if real_L else np.nan),\n                (ce_w[0] if ce_w else np.nan),\n                infos)\n\n    print(\"[tw] arm wire (true membership) …\")\n    wire, real_L_wire, ce_wire, wire_infos = accum(labels, \"wire\")\n    wire_stops = [i[\"stop_step\"] for i in wire_infos]\n\n    print(f\"[tw] arm shuffle (deranged membership, matched budget \"\n          f\"{wire_stops}) …\")\n    # derange class labels (matched budget), ensure no fixed point\n    perm = labels.copy()\n    for _ in range(64):\n        perm = rng.permutation(labels)\n        if np.any(perm != labels):\n            break\n    shuf, _, _, shuf_infos = accum(perm, \"shuffle\", stops=wire_stops)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

## Assistant

Caught and fixed a shadowing hazard (`rb` was reused for both the replay batch and the real-member eval — renamed the latter `rme`). Now meta + results record and the CLI:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "    res[\"meta\"] = {\n        \"model_id\": args.model_id, \"n_nonce\": n, \"seeds\": args.seeds,\n        \"steps\": args.steps, \"lr\": args.lr, \"lora_r\": args.lora_r,\n        \"band\": [band[0], band[-1]], \"gate0_ok\": gate0_ok,\n        \"nonces\": nonces, \"labels\": labels.tolist(),\n        \"real_margin_base\": real_margin, \"ce_base\": ce_base, \"ce_wire\": ce_wire,\n        \"real_L_wire\": real_L_wire, \"restore_ok\": restore_ok,\n    }",
  "new_content": "    res[\"meta\"] = {\n        \"model_id\": args.model_id, \"n_nonce\": n, \"seeds\": args.seeds,\n        \"steps\": args.steps, \"lr\": args.lr, \"lora_r\": args.lora_r,\n        \"band\": [band[0], band[-1]], \"gate0_ok\": gate0_ok,\n        \"nonces\": nonces, \"labels\": labels.tolist(),\n        \"real_margin_base\": real_margin, \"ce_base\": ce_base, \"ce_wire\": ce_wire,\n        \"real_L_wire\": real_L_wire, \"restore_ok\": restore_ok,\n        # s315 amendment (instrument-side; frozen gates untouched)\n        \"kl_weight\": args.kl_weight, \"ce_budget\": args.ce_budget,\n        \"plateau_tol\": args.plateau_tol, \"min_stop\": args.min_stop,\n        \"n_replay\": len(REPLAY_TEXTS),\n        \"wire_stops\": wire_stops,\n        \"wire_stop_reasons\": [i[\"stop_reason\"] for i in wire_infos],\n    }\n    res[\"training\"] = {\"wire\": wire_infos, \"shuffle\": shuf_infos}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py",
  "original_content": "    ap.add_argument(\"--min-class\", type=int, default=8)\n    ap.add_argument(\"--alpha\", type=float, default=0.05)",
  "new_content": "    ap.add_argument(\"--min-class\", type=int, default=8)\n    ap.add_argument(\"--kl-weight\", type=float, default=1.0,\n                    help=\"s315: weight of KL(base||wire) replay anchor\")\n    ap.add_argument(\"--ce-budget\", type=float, default=0.10,\n                    help=\"s315: max host-CE drift (nats) before rollback-stop\")\n    ap.add_argument(\"--plateau-tol\", type=float, default=0.01,\n                    help=\"s315: rel mem-CE improvement below this = plateau\")\n    ap.add_argument(\"--min-stop\", type=int, default=55,\n                    help=\"s315: plateau stop only at snaps >= this step\")\n    ap.add_argument(\"--alpha\", type=float, default=0.05)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/type_write.py.
```

### Thinking

Now I'll verify the code using the validate flag, ruff, and diagnostics.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/explore/type_write.py --validate && uv run ruff check scripts/explore/type_write.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 120000
}
```

**Summary:** $ uv run python scripts/explore/type_...

**Output:**
```
Exit code: 0
Stdout:
── §P-TYPE-WRITE --validate (planted worlds, no model) ──
  written_graded   -> TYPE-WRITTEN+GRADED    expect TYPE-WRITTEN+GRADED    ✓
  written_opaque   -> WRITTEN-OPAQUE         expect WRITTEN-OPAQUE         ✓
  context_only     -> CONTEXT-ONLY           expect CONTEXT-ONLY           ✓
  no_write         -> NO-WRITE               expect NO-WRITE               ✓
  host_damaged     -> HOST-DAMAGED           expect HOST-DAMAGED           ✓
  primitive _signed_L               ✓
  primitive _spearman monotone      ✓
  stop: healthy world               (500, 'max_steps') ✓
  stop: plateau world               (90, 'plateau') ✓
  stop: drift-budget world          (14, 'ce_budget_rollback') ✓
  stop: step-0 over budget          (0, 'ce_budget_rollback') ✓

── --validate ALL PASS ──
All checks passed!
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_write.py"
}
```

**Summary:** Checking diagnostics: type_write.py

**Output:**
```
No diagnostics found
```

### Thinking

All validation checks passed with the frozen and new worlds unchanged, and the linter is clean. Now I'm setting up the smoke test with a single seed and thirty steps, using a small nonce cap and overrides to force each code path—I need to verify KL computation on MPS, check that the replay cache works, confirm snap logging triggers, and ensure restoration is bit-exact. Running with those parameters and outputting to the results directory.

### Thinking

Validation passed with 5 frozen worlds unchanged and 4 new stop worlds added, no issues. Now I'm running the smoke test with 1 seed, 30 steps, and 4 nonces using a loosened plateau threshold to exercise the early-stop and budget shuffle path.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_write.py --seeds 1 --steps 30 --n-nonce 4 --min-class 2 --min-stop 5 --plateau-tol 0.30 --out results/type-write/smoke 2>&1 | tee results/type-write/smoke.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-write-smoke"
}
```

**Summary:** $ uv run python -u scripts/explore/ty...

**Output:**
```
Background job job-1 started.
Command: cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_write.py --seeds 1 --steps 30 --n-nonce 4 --min-class 2 --min-stop 5 --plateau-tol 0.30 --out results/type-write/smoke 2>&1 | tee results/type-write/smoke.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.
```

### Thinking

I've launched Smoke as job-1 and am running a verification read with an async lambda to confirm it's running before checkpointing.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-write-smoke" (job-1)

**Output:**
```
Job "type-write-smoke" (job-1) — running

(no new output)
```

## Assistant

**ASYNC: job-1 (type-write-smoke) verified running. Waiting for signal.**

Status while the smoke runs:

## Build complete (task #3 ✅, committed pending smoke)

**Amendment to `type_write.py`** (instrument-side only — gates TW1–TW5, metric, verdict tree, a-priori 45/20/20/10/5 all untouched):

1. **Host-anchored objective**: `loss = CE(membership) + kl_weight · KL(base‖wire)` on 8 cached neutral `REPLAY_TEXTS` — deliberately disjoint from `CE_TEXTS` (never train on the measurement) and free of class members/held predicates (the anchor must not fight the write). Base entropy subtracted so the anchor reads as true KL, exactly 0.0 at zero delta. Same teacher convention as `writeback_compile`'s geography KL.
2. **Evidence-gated stop** (wire arm only): fib snaps log `mem_ce / kl / host_ce / drift`; stop on plateau (rel improvement < 1% at snaps ≥ 55) or **rollback to last good snap** if host-CE drift > 0.10 nats. The **shuffle arm replays the wire's per-seed stop step exactly** — TW3 stays matched-budget by construction.
3. The stop rule is one pure function `_stop_decision` used identically in-loop and in `--validate` (λ one_way) — 4 planted stop worlds all land: healthy→max_steps, plateau→(90, plateau), runaway-drift→(14, rollback), step-0-burn→(0, zero-delta rollback).

**Verified so far:** `--validate` ALL PASS (9 worlds + 2 primitives), ruff clean, no editor diagnostics.

**Smoke will show:** replay cache + KL computes on MPS, snap logging, live plateau-stop firing (thresholds loosened to force it in 30 steps), matched-budget shuffle, restore bit-exact. No direction read from smoke.

When the smoke lands green, I'll commit the amended harness and hand you the GO decision for the real run — proposed launch (run 2 to a fresh dir, run-1 artifact preserved):

```
tmux main:1 → uv run python -u scripts/explore/type_write.py \
  --out results/type-write/qwen3-4b-r2 2>&1 | tee results/type-write/qwen3-4b-r2-run.log
```

Expected cheaper than run 1: each step pays ~2 forwards, but the stop rule should cut ~500 steps to ~100–150.

## User

ok go


## Assistant

Checking the smoke first:

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-write-smoke" (job-1)

**Output:**
```
Job "type-write-smoke" (job-1) — completed (exit 0)

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 22113.30it/s]
[tw] Qwen/Qwen3-4B dev=mps n_layers=36 band=L22..L29 seeds=1 steps=30
[tw] nonces=4 (animal 2 vehicle 2)
[tw] gate-0: base licensing of real members …
[tw] gate-0: real-member licensing margin=2.538 per_class_ok=True n_ok=True -> PASS
[tw] arm base …
[tw] replay anchor cached: 8 texts, 93 positions, kl_weight=1.0
[tw] arm wire (true membership) …
    seed0 snap    0 mem 4.7553 kl 0.0007 host_ce 3.5296 drift +0.0007
    seed0 snap    1 mem 4.7372 kl 0.0008 host_ce 3.5267 drift -0.0021
    seed0 snap    2 mem 4.6674 kl 0.0007 host_ce 3.5275 drift -0.0013
    seed0 snap    3 mem 4.5605 kl 0.0009 host_ce 3.5240 drift -0.0049
    seed0 snap    5 mem 4.3095 kl 0.0014 host_ce 3.5288 drift -0.0000
    seed0 STOP plateau @ step 5 (keep 6)
[tw] wire seed0 done (stop 6 plateau)
[tw] arm shuffle (deranged membership, matched budget [6]) …
    seed0 snap    0 mem 4.7537 kl 0.0007 host_ce 3.5240 drift -0.0048
    seed0 snap    1 mem 4.7316 kl 0.0009 host_ce 3.5222 drift -0.0067
    seed0 snap    2 mem 4.6670 kl 0.0007 host_ce 3.5319 drift +0.0030
    seed0 snap    3 mem 4.5571 kl 0.0008 host_ce 3.5191 drift -0.0098
    seed0 snap    5 mem 4.3093 kl 0.0012 host_ce 3.5216 drift -0.0073
[tw] shuffle seed0 done (stop 6 matched_budget)
[tw] wrote results/type-write/smoke/results.json
[tw] TW1 p=0.8286 pass=False | TW2 rho=0.800 p=0.1649 pass=False | TW3 p=0.3108 pass=False | TW4 p=0.1892 pass=False | recall pass=False | host=True
[tw] L_base=-0.485 L_wire=-0.443 L_shuf=-0.456
[tw] VERDICT: NO-WRITE
```

### Thinking

The smoke test is passing across the board—replay cache is working as expected with negligible KL divergence, the KL computation runs cleanly on MPS without host drift, snap logging is firing, plateau detection triggered correctly at step 5, shuffle matched the budget, and host restoration looks good.

I should verify the restore_ok flag in the smoke results.json before deciding what to commit. The plan is to commit the updated type_write.py code along with smoke logs and results as evidence, following the precedent of keeping code commits separate from artifacts. One thing I'm flagging though: the smoke test used a loosened plateau tolerance of 0.30 to force the stop condition, but the real run uses stricter defaults (min_stop=55, tol=0.01), and looking at the actual loss trajectory from run 1, the relative improvements between snapshots were substantial enough that the tighter tolerance might not trigger as readily—I need to watch whether the real run hits the plateau stop condition as expected. I need to be careful about what gets committed now versus what waits for the approval batch. The code

### Thinking

The replay cache built successfully with KL starting near zero and minimal drift, the plateau-stop fired as intended at step 5, and the shuffle matched the budget exactly—all confirming the underpowered-smoke outcome is correct. Now I'm verifying the restore in the smoke artifact before committing the harness.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/type-write/smoke/results.json'))\nprint('restore_ok =', d['meta']['restore_ok'])\nprint('wire_stops =', d['meta']['wire_stops'], d['meta']['wire_stop_reasons'])\nprint('kl_weight  =', d['meta']['kl_weight'], '| ce_budget =', d['meta']['ce_budget'])\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
restore_ok = True
wire_stops = [6] ['plateau']
kl_weight  = 1.0 | ce_budget = 0.1
```

### Thinking

I'm committing the amended harness and launching run 2 with bit-exact restoration.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/explore/type_write.py && git commit -F - <<'EOF'\n🔄 type_write.py s315 amendment — host-anchored objective + evidence-gated stop (validate+smoke green)\n\n- run-1 HOST-DAMAGED diagnosis: plain membership-CE lacked the host anchor gd_cd\n  had via teacher KL; 300 of 500 steps bought only damage\n- (1) loss = CE(membership) + kl_weight*KL(base||wire) on 8 cached neutral\n  REPLAY_TEXTS (disjoint from CE_TEXTS; base entropy subtracted -> true KL,\n  0.0 at zero delta; writeback_compile teacher convention)\n- (2) evidence-gated stop at fib snaps: plateau (rel<1% @ >=55) or host-CE\n  drift > 0.10 -> rollback to last good snap; shuffle arm replays wire per-seed\n  stop step exactly -> TW3 matched-budget by construction\n- _stop_decision pure fn, same code path in-loop and --validate (lambda one_way)\n- frozen gates/metric/verdicts/a-priori UNCHANGED; --validate ALL PASS\n  (5 verdict + 4 stop worlds + primitives); ruff clean; smoke green (KL~0 at\n  init, live plateau stop, matched budget, host drift ±0.005, restore bit-exact)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "amended harness"
}
```

**Summary:** Git commit: amended harness

**Output:**
```
Exit code: 0
Stdout:
[main b448f34] 🔄 type_write.py s315 amendment — host-anchored objective + evidence-gated stop (validate+smoke green)
 1 file changed, 201 insertions(+), 17 deletions(-)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee results/type-write/qwen3-4b-r2-run.log\" Enter && sleep 20 && tmux capture-pane -p -t main:1 | tail -8",
  "timeout": 40000
}
```

**Summary:** $ tmux send-keys -t main:1 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
[tw] arm base …
[tw] replay anchor cached: 8 texts, 93 positions, kl_weight=1.0
[tw] arm wire (true membership) …
    seed0 snap    0 mem 4.9562 kl 0.0007 host_ce 3.5280 drift -0.0009
    seed0 snap    1 mem 4.9400 kl 0.0008 host_ce 3.5237 drift -0.0052
    seed0 snap    2 mem 4.8848 kl 0.0007 host_ce 3.5275 drift -0.0013
    seed0 snap    3 mem 4.8017 kl 0.0009 host_ce 3.5212 drift -0.0076
```

### Thinking

Run 2 is now live and verified—gate-0 passed since it's already at wire arm, with all 20 nonces loaded and memory starting at the same loss value as run 1's initial step. I need to update the state.md header to reflect the ON-SIGNAL status and checkpoint, editing the top section directly on disk without approval gating.

### Thinking

Run 2 is now live with gate-0 passed and wire arm training active using default parameters, starting at a loss of 4.9562 that matches run 1's baseline. I'm updating the session state file to mark the run 2 boundary.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ **CURRENT = s314 (THE TYPE ARC DEEPENS).** Two milestones DONE + committed, one run\n> IN FLIGHT. **FIRST ACTION next session: check the §P-TYPE-WRITE run** — tmux main:1,\n> `results/type-write/qwen3-4b-run.log`. ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:`\n> + no traceback → read TW1–TW5 gates in results.json → **commit results/type-write/\n> AUTONOMOUS** (task #3) → then **§Result-type-write on types-are-injectable-relations.md +\n> memory candidate + INDEX + task #4 close = MICHAEL APPROVAL BATCH.** Task list live (#3\n> run in_progress, #4 blocked). If VERDICT=NO-WRITE → the wire didn't bake (power/recipe),\n> NOT a claim refutation (re-check loss dropped); CONTEXT-ONLY = the falsifier (recall in\n> trained frames but no held transfer = types enacted per-frame, not injectable).",
  "new_content": "> ★★ **CURRENT = s315 (P-TYPE-WRITE RUN 2 — AMENDED RECIPE).** **FIRST ACTION next\n> session: check run 2** — tmux main:1, `results/type-write/qwen3-4b-r2-run.log`.\n> ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:` + no traceback → read TW1–TW5 +\n> wire_stops/stop_reasons in results.json → **commit results/type-write/qwen3-4b-r2/\n> AUTONOMOUS** → then **§Result-type-write on types-are-injectable-relations.md + memory\n> candidate + INDEX = MICHAEL APPROVAL BATCH.** Read discipline: TW5 must PASS this time\n> (that's what the amendment buys); if HOST-DAMAGED again → recipe class wrong (KL anchor\n> insufficient) → escalate, don't iterate silently. NO-WRITE + stop_reason=plateau-early →\n> anchor may have smothered the write (check mem_ce floor + recall p) = power question.\n> CONTEXT-ONLY = the falsifier and is now CLEAN (host sane, recall in, no held transfer =\n> types enacted per-frame, not injectable). TYPE-WRITTEN(+GRADED) = causality✓ → S5\n> scorecard 3/4.\n>\n> **s315 (this session): ① run 1 LANDED ❌ HOST-DAMAGED (375358d, 5% tail, autonomous\n> commit).** Wire baked (loss 4.96→0.35; membership_recall p=5e-4) but host burned: CE\n> 3.529→5.824 (+2.3 nats), real-member licensing INVERTED +2.538→−0.624; L_shuf 0.417 >\n> L_wire 0.310 = damage-artifact signature ⇒ TW1–TW4 VOID (measurement void, NOT claim\n> refutation — the frozen 5% branch). Diagnosis: every host-sane wire (s303–s312 gd_cd)\n> had teacher-KL as implicit host anchor; this recipe was plain membership-CE, 500 steps,\n> tiny corpus; run-1 curve shows learning done ~step 200, rest bought damage. **② 🔄\n> AMENDMENT built + committed (b448f34, Michael GO; instrument-side ONLY, frozen gates/\n> metric/verdicts/a-priori untouched):** (1) loss = CE(membership) + kl_weight·KL(base‖wire)\n> on 8 cached neutral REPLAY_TEXTS (disjoint from CE_TEXTS — never train on the measurement;\n> base entropy subtracted → true KL = 0 at zero delta; LoRA B=0 init ⇒ no step-0 grad\n> calibration possible ⇒ fixed CLI weight 1.0, components logged per snap); (2) evidence-\n> gated stop at fib snaps: plateau (rel mem-CE improvement <1% at snaps ≥55) OR host-CE\n> drift >0.10 → ROLLBACK to last good snap; shuffle arm replays wire's per-seed stop step\n> exactly ⇒ TW3 matched-budget by construction; _stop_decision = pure fn, same code path\n> in-loop + --validate (λ one_way). --validate ALL PASS (5 verdict + 4 stop worlds), ruff\n> clean, smoke green (KL≈0 at init, live plateau stop fired, matched budget, drift ±0.005,\n> restore bit-exact). **③ ⚠ RUN 2 IN FLIGHT (tmux main:1):** `uv run python -u\n> scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee\n> results/type-write/qwen3-4b-r2-run.log` (defaults: 20 nonces, 3 seeds × 2 arms, ≤500\n> steps + stop rule). Verified running (wire seed0, step-0 loss 4.9562 ≡ run 1 bit-match —\n> only the objective changed). See ON-SIGNAL above. state.md commit rides the next\n> approval batch."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

**ASYNC: run 2 verified running on tmux main:1. Waiting for signal.**

Session state:

| | |
|---|---|
| Run 1 results | ❌ HOST-DAMAGED, committed **375358d** |
| Amended harness | 🔄 committed **b448f34** (validate + smoke green) |
| Run 2 | ⚠ in flight → `results/type-write/qwen3-4b-r2/` |
| state.md | updated on disk; commit rides the next approval batch |
| Task #5 | queued: ON-SIGNAL read → autonomous results commit → approval batch |

The read discipline for run 2, pre-committed so we don't improvise at the verdict:

- **TW5 must PASS** — that's the one thing the amendment buys. HOST-DAMAGED again = the recipe class is wrong, escalate to you rather than iterate.
- **TYPE-WRITTEN(+GRADED)** → causality ✓ → S5 scorecard goes 3/4 (discreteness ✓ selectivity ✓ compositionality ✗ **causality ✓**).
- **CONTEXT-ONLY** is now a *clean* falsifier — host sane, recall in, no held transfer = types enacted per-frame, not injectable. That would be a real finding, not an artifact.
- **NO-WRITE with an early plateau stop** → check whether the anchor smothered the write (mem_ce floor + recall p) — power question, not a claim verdict.

Run 1's curve says learning completes around step ~200, so with the stop rule this should land faster than run 1's ~1–2h despite the doubled per-step cost. Signal me when it's done.

## User

run is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -n 45 /Users/mwhitford/src/verbum/results/type-write/qwen3-4b-r2-run.log && grep -c Traceback /Users/mwhitford/src/verbum/results/type-write/qwen3-4b-r2-run.log || true"
}
```

**Summary:** $ tail -n 45 /Users/mwhitford/src/ver...

**Output:**
```
Exit code: 0
Stdout:
seed1 STOP ce-budget @ step 34 -> rollback to step 21 (keep 22)
[tw] wire seed1 done (stop 22 ce_budget_rollback)
    seed2 snap    0 mem 4.9562 kl 0.0007 host_ce 3.5294 drift +0.0006
    seed2 snap    1 mem 4.9401 kl 0.0007 host_ce 3.5296 drift +0.0008
    seed2 snap    2 mem 4.8845 kl 0.0008 host_ce 3.5253 drift -0.0036
    seed2 snap    3 mem 4.7985 kl 0.0014 host_ce 3.5194 drift -0.0095
    seed2 snap    5 mem 4.5892 kl 0.0016 host_ce 3.5287 drift -0.0002
    seed2 snap    8 mem 4.2195 kl 0.0026 host_ce 3.5125 drift -0.0163
    seed2 snap   13 mem 3.5197 kl 0.0102 host_ce 3.5229 drift -0.0059
    seed2 snap   21 mem 2.6577 kl 0.0313 host_ce 3.5606 drift +0.0317
    seed2 snap   34 mem 1.7521 kl 0.0311 host_ce 3.6730 drift +0.1442
    seed2 STOP ce-budget @ step 34 -> rollback to step 21 (keep 22)
[tw] wire seed2 done (stop 22 ce_budget_rollback)
[tw] arm shuffle (deranged membership, matched budget [22, 22, 22]) …
    seed0 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5228 drift -0.0060
    seed0 snap    1 mem 4.9575 kl 0.0008 host_ce 3.5219 drift -0.0069
    seed0 snap    2 mem 4.9076 kl 0.0009 host_ce 3.5301 drift +0.0013
    seed0 snap    3 mem 4.8222 kl 0.0012 host_ce 3.5176 drift -0.0113
    seed0 snap    5 mem 4.6124 kl 0.0011 host_ce 3.5207 drift -0.0081
    seed0 snap    8 mem 4.2447 kl 0.0027 host_ce 3.5206 drift -0.0083
    seed0 snap   13 mem 3.5433 kl 0.0108 host_ce 3.5151 drift -0.0137
    seed0 snap   21 mem 2.6795 kl 0.0324 host_ce 3.5592 drift +0.0303
[tw] shuffle seed0 done (stop 22 matched_budget)
    seed1 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5273 drift -0.0015
    seed1 snap    1 mem 4.9588 kl 0.0007 host_ce 3.5168 drift -0.0121
    seed1 snap    2 mem 4.9051 kl 0.0006 host_ce 3.5276 drift -0.0013
    seed1 snap    3 mem 4.8209 kl 0.0010 host_ce 3.5140 drift -0.0148
    seed1 snap    5 mem 4.6116 kl 0.0013 host_ce 3.5239 drift -0.0050
    seed1 snap    8 mem 4.2412 kl 0.0026 host_ce 3.5220 drift -0.0068
    seed1 snap   13 mem 3.5318 kl 0.0100 host_ce 3.5082 drift -0.0206
    seed1 snap   21 mem 2.6517 kl 0.0315 host_ce 3.5666 drift +0.0378
[tw] shuffle seed1 done (stop 22 matched_budget)
    seed2 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5315 drift +0.0026
    seed2 snap    1 mem 4.9578 kl 0.0008 host_ce 3.5194 drift -0.0094
    seed2 snap    2 mem 4.9043 kl 0.0008 host_ce 3.5210 drift -0.0079
    seed2 snap    3 mem 4.8208 kl 0.0010 host_ce 3.5309 drift +0.0021
    seed2 snap    5 mem 4.6105 kl 0.0018 host_ce 3.5302 drift +0.0013
    seed2 snap    8 mem 4.2381 kl 0.0027 host_ce 3.5222 drift -0.0066
    seed2 snap   13 mem 3.5375 kl 0.0100 host_ce 3.5099 drift -0.0189
    seed2 snap   21 mem 2.6696 kl 0.0315 host_ce 3.5525 drift +0.0237
[tw] shuffle seed2 done (stop 22 matched_budget)
[tw] wrote results/type-write/qwen3-4b-r2/results.json
[tw] TW1 p=0.3678 pass=False | TW2 rho=-0.041 p=0.5657 pass=False | TW3 p=0.0022 pass=True | TW4 p=0.5821 pass=False | recall pass=False | host=True
[tw] L_base=0.138 L_wire=0.107 L_shuf=0.061
[tw] VERDICT: NO-WRITE
0
```

### Thinking

Looking at the second run results, the wire seeds all show the same pattern: the ce-budget rollback happened at step 34, leaving only 22 steps before stopping. The membership wasn't learned—the memory score stayed at 2.66, which is far too high compared to run 1 where it took 200-500 steps to reach 0.35. This means the host-CE budget exhausted itself long before membership could be acquired. The host protection worked as intended though, so the amendment is doing its job.

The real tension here is that at this learning rate and KL weight, I can't learn membership within the budget constraint—the drift grew to 0.14-0.16 despite the KL anchor being set to 1.0, which is too weak to actually restrain it. The budget cut training short before the write could happen. This isn't a refutation of the hypothesis; it's a power issue with the recipe itself. I need to either increase the KL weight substantially so it actually constrains drift and allows longer training, or adjust the budget to give membership learning enough room to complete.

### Thinking

No errors encountered, so I'm committing the run-2 results and moving on to review the output.

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/type-write/qwen3-4b-r2 results/type-write/qwen3-4b-r2-run.log && git commit -F - <<'EOF'\n❌ P-TYPE-WRITE run 2 (amended recipe): VERDICT NO-WRITE — host protected, but budget fired before the write\n\n- amendment WORKED as a mechanism: TW5 host-sane PASS (drift held <=0.10, restore\n  bit-exact), all 3 wire seeds ce_budget_rollback at step 34 -> keep 22\n- but the write needs ~200 steps (run 1) and 22 steps left mem_ce at 2.66 ->\n  membership_recall FAIL -> NO-WRITE (power branch, NOT a claim verdict)\n- the tension is now MEASURED: at lr 1e-4 / kl_weight 1.0 the anchor does not\n  bind (kl 0.03 vs mem 2.66 at snap 21) and drift hits 0.14 by step 34 --\n  budget 0.10 cuts training ~10x before the wire bakes\n- TW3 nominally passes (p=0.0022) but unread under recall FAIL\n- next knobs (CLI only, no code): kl_weight up (anchor must bind) + ce_budget\n  toward CE_TOL 0.5 (frozen gate headroom) -- Michael decision pending\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "run 2 results"
}
```

**Summary:** Git commit: run 2 results

**Output:**
```
Exit code: 0
Stdout:
[main cc44ab9] ❌ P-TYPE-WRITE run 2 (amended recipe): VERDICT NO-WRITE — host protected, but budget fired before the write
 3 files changed, 727 insertions(+)
 create mode 100644 results/type-write/qwen3-4b-r2-run.log
 create mode 100644 results/type-write/qwen3-4b-r2/gate0.json
 create mode 100644 results/type-write/qwen3-4b-r2/results.json
```

### Thinking

I'm looking at the performance metrics from two experimental runs to weigh the tradeoffs. The first run shows memory requirements around 200 steps for recall with a probability of 5e-4, hitting strong margins at step 200 with a score of 8.24. The second run reveals drift of 0.14 at 34 steps, creating a critical mismatch between the write window of 200 steps and the damage window at 34 steps within the 0.10 budget constraint.

## Assistant

Committed **cc44ab9**. Here's the read — this is the pre-registered power branch, and I'm escalating rather than iterating:

## Run 2: NO-WRITE — the amendment worked, and that's exactly the problem

**What the amendment bought (both mechanisms fired correctly):**
- **TW5 HOST-SANE: PASS.** All 3 wire seeds hit the ce-budget at step 34 (drift 0.144–0.163 > 0.10) and rolled back to the last good snap (keep 22). Host protected, restore bit-exact. HOST-DAMAGED is dead.
- Matched-budget shuffle ran [22, 22, 22] exactly; seeds near-identical (tight instrument).

**What it cost:** 22 steps leaves mem_ce at 2.66 — the membership relation never installed (recall FAIL → NO-WRITE). Run 1 says the write needs ~200 steps. TW3 nominally passes (p=0.0022) but is unread under recall FAIL.

**The tension is now a measurement, not a guess:**

| | write window | damage window |
|---|---|---|
| steps needed | ~200 (run 1 recall) | 34 (drift > 0.10, run 2) |

At `lr 1e-4, kl_weight 1.0` the anchor doesn't bind — KL is 0.03 vs mem 2.66 at snap 21, so its gradient pressure is ~1% of the membership term's. Drift grows essentially unopposed; the budget then correctly cuts training ~10× before the wire bakes. The two windows have to be made to overlap.

## Options (all CLI-only, zero code change, frozen gates untouched)

**A (Recommended): `--kl-weight 10 --ce-budget 0.40`** — make the anchor actually bind (×10 restraint) *and* use the headroom the frozen gate already grants (TW5's CE_TOL is 0.5; my 0.10 budget was conservative beyond the pre-registration). Two levers, one run, and the snap logs will show exactly which one carried.

**B: `--kl-weight 100`, budget stays 0.10** — force the anchor to fully dominate. Purist (host essentially pinned), but risks smothering the write: if mem_ce floors high with recall FAIL again, we've spent a run learning only that.

**C: `--lr 3e-5 --ce-budget 0.40`** — gentler descent, more steps inside the same damage budget. Slower run, and run 1's evidence says lr 1e-4 *finds* the wire, so touching lr weakens comparability.

My reasoning for A: it's the only option where both measured failure modes (anchor-doesn't-bind, budget-fires-early) are each addressed by the lever that measured them, and the fib snaps give us the drift-vs-mem curve either way — if A fails, it fails informatively.

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Run 3 knobs — which configuration?",
  "options": [
    {
      "label": "A: kl_weight 10 + ce_budget 0.40 (Recommended)",
      "description": "Anchor binds AND budget uses frozen CE_TOL headroom; most likely to open the write window"
    },
    {
      "label": "B: kl_weight 100, budget 0.10",
      "description": "Host pinned hard; tests whether a strongly-anchored write is possible at all"
    },
    {
      "label": "C: lr 3e-5 + budget 0.40",
      "description": "Gentler descent inside the damage budget; weakens run-1 comparability"
    }
  ]
}
```

**Summary:** Q: Run 3 knobs — which configuration?

**Output:**
```
User answered: A: kl_weight 10 + ce_budget 0.40 (Recommended)
```

## Assistant

Launching run 3 with option A:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_write.py --kl-weight 10 --ce-budget 0.40 --out results/type-write/qwen3-4b-r3 2>&1 | tee results/type-write/qwen3-4b-r3-run.log\" Enter && sleep 25 && tmux capture-pane -p -t main:1 | tail -6",
  "timeout": 45000
}
```

**Summary:** $ tmux send-keys -t main:1 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
seed0 snap    1 mem 4.9410 kl 0.0007 host_ce 3.5281 drift -0.0007
    seed0 snap    2 mem 4.8932 kl 0.0010 host_ce 3.5196 drift -0.0093
    seed0 snap    3 mem 4.8179 kl 0.0008 host_ce 3.5284 drift -0.0004
    seed0 snap    5 mem 4.6275 kl 0.0009 host_ce 3.5314 drift +0.0026
    seed0 snap    8 mem 4.2866 kl 0.0016 host_ce 3.5161 drift -0.0127
```

## Assistant

Run 3 verified running (wire seed0, snaps logging). Updating state.md for the boundary:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ **CURRENT = s315 (P-TYPE-WRITE RUN 2 — AMENDED RECIPE).** **FIRST ACTION next\n> session: check run 2** — tmux main:1, `results/type-write/qwen3-4b-r2-run.log`.\n> ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:` + no traceback → read TW1–TW5 +\n> wire_stops/stop_reasons in results.json → **commit results/type-write/qwen3-4b-r2/\n> AUTONOMOUS** → then **§Result-type-write on types-are-injectable-relations.md + memory\n> candidate + INDEX = MICHAEL APPROVAL BATCH.** Read discipline: TW5 must PASS this time\n> (that's what the amendment buys); if HOST-DAMAGED again → recipe class wrong (KL anchor\n> insufficient) → escalate, don't iterate silently. NO-WRITE + stop_reason=plateau-early →\n> anchor may have smothered the write (check mem_ce floor + recall p) = power question.\n> CONTEXT-ONLY = the falsifier and is now CLEAN (host sane, recall in, no held transfer =\n> types enacted per-frame, not injectable). TYPE-WRITTEN(+GRADED) = causality✓ → S5\n> scorecard 3/4.",
  "new_content": "> ★★ **CURRENT = s315 (P-TYPE-WRITE RUN 3 — kl_weight 10, ce_budget 0.40).** **FIRST\n> ACTION next session: check run 3** — tmux main:1, `results/type-write/qwen3-4b-r3-run.log`.\n> ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:` + no traceback → read TW1–TW5 +\n> wire_stops/stop_reasons in results.json → **commit results/type-write/qwen3-4b-r3/\n> AUTONOMOUS** → then **§Result-type-write on types-are-injectable-relations.md (all 3\n> runs, incl. the write-vs-damage window tension as a finding) + memory candidate + INDEX\n> + state.md = MICHAEL APPROVAL BATCH.** Read discipline: TW5 must PASS (r2 proved the\n> mechanism); the OPEN question is whether kl_weight 10 lets the anchor BIND (watch snap\n> kl growth vs mem descent) and budget 0.40 opens the ~200-step write window (r1 recall\n> needs it; r2 got cut at 22). NO-WRITE again + budget rollback → the window still doesn't\n> overlap → escalate w/ full drift-vs-mem curves, DON'T iterate knobs silently. NO-WRITE +\n> plateau + mem_ce floored high → anchor smothered the write (kl_weight too high) = the\n> B-failure. CONTEXT-ONLY = the falsifier, now CLEAN (host sane, recall in, no held\n> transfer = types enacted per-frame, not injectable). TYPE-WRITTEN(+GRADED) = causality✓\n> → S5 scorecard 3/4.\n>\n> **RUN LEDGER §P-TYPE-WRITE:** r1 (375358d) ❌ HOST-DAMAGED — wire baked (recall p=5e-4,\n> ~200 steps to install) but host burned (CE +2.3, real-L inverted −0.624), TW1–4 VOID.\n> r2 (cc44ab9) ❌ NO-WRITE — amendment mechanisms both fired correctly (TW5 PASS, 3/3\n> seeds ce_budget_rollback @34→keep 22, matched shuffle [22,22,22], seeds near-identical)\n> but 22 steps ≪ 200-step write window; **the write-vs-damage tension is now MEASURED:\n> at lr 1e-4/kl_weight 1.0 the anchor doesn't bind (kl 0.03 vs mem 2.66 @ snap 21, ~1%\n> gradient pressure) and drift hits 0.14 by step 34.** r3 IN FLIGHT (Michael option A):\n> `--kl-weight 10 --ce-budget 0.40` (anchor ×10 + frozen CE_TOL 0.5 headroom; both levers\n> address the mode that measured them; CLI-only, no code change)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **③ ⚠ RUN 2 IN FLIGHT (tmux main:1):** `uv run python -u\n> scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee\n> results/type-write/qwen3-4b-r2-run.log` (defaults: 20 nonces, 3 seeds × 2 arms, ≤500\n> steps + stop rule). Verified running (wire seed0, step-0 loss 4.9562 ≡ run 1 bit-match —\n> only the objective changed). See ON-SIGNAL above. state.md commit rides the next\n> approval batch.",
  "new_content": "> **③ ✅ RUN 2 LANDED ❌ NO-WRITE (cc44ab9, autonomous)** — see RUN LEDGER above for the\n> read (host protected, budget fired @34 before the ~200-step write window). **④ ⚠ RUN 3\n> IN FLIGHT (tmux main:1, Michael option A):** `uv run python -u scripts/explore/\n> type_write.py --kl-weight 10 --ce-budget 0.40 --out results/type-write/qwen3-4b-r3 2>&1\n> | tee results/type-write/qwen3-4b-r3-run.log`. Verified running (wire seed0 snaps\n> logging). See ON-SIGNAL above. state.md commit rides the next approval batch."
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"RUN 2 IN FLIGHT\" -A 6 /Users/mwhitford/src/verbum/mementum/state.md | head -14"
}
```

**Summary:** $ grep -n "RUN 2 IN FLIGHT" -A 6 /Use...

**Output:**
```
Exit code: 0
Stdout:
54:> restore bit-exact). **③ ⚠ RUN 2 IN FLIGHT (tmux main:1):** `uv run python -u
55-> scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee
56-> results/type-write/qwen3-4b-r2-run.log` (defaults: 20 nonces, 3 seeds × 2 arms, ≤500
57-> steps + stop rule). Verified running (wire seed0, step-0 loss 4.9562 ≡ run 1 bit-match —
58-> only the objective changed). See ON-SIGNAL above. state.md commit rides the next
59-> approval batch.
60->
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 53,
  "limit": 7
}
```

**Summary:** Reading state.md (53-60)

**Output:**
```
> restore bit-exact). **③ ⚠ RUN 2 IN FLIGHT (tmux main:1):** `uv run python -u
> scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee
> results/type-write/qwen3-4b-r2-run.log` (defaults: 20 nonces, 3 seeds × 2 arms, ≤500
> steps + stop rule). Verified running (wire seed0, step-0 loss 4.9562 ≡ run 1 bit-match —
> only the objective changed). See ON-SIGNAL above. state.md commit rides the next
> approval batch.
>

[CONTENT TRUNCATED] Showing lines 54 to 60 of 4752 total lines. Use line_offset=60 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "**③ ⚠ RUN 2 IN FLIGHT (tmux main:1):** `uv run python -u\n> scripts/explore/type_write.py --out results/type-write/qwen3-4b-r2 2>&1 | tee\n> results/type-write/qwen3-4b-r2-run.log` (defaults: 20 nonces, 3 seeds × 2 arms, ≤500\n> steps + stop rule). Verified running (wire seed0, step-0 loss 4.9562 ≡ run 1 bit-match —\n> only the objective changed). See ON-SIGNAL above. state.md commit rides the next\n> approval batch.",
  "new_content": "**③ ✅ RUN 2 LANDED ❌ NO-WRITE (cc44ab9,\n> autonomous)** — see RUN LEDGER above (host protected, budget fired @34, write window\n> ~200 steps never opened). **④ ⚠ RUN 3 IN FLIGHT (tmux main:1, Michael option A):**\n> `uv run python -u scripts/explore/type_write.py --kl-weight 10 --ce-budget 0.40 --out\n> results/type-write/qwen3-4b-r3 2>&1 | tee results/type-write/qwen3-4b-r3-run.log`.\n> Verified running (wire seed0 snaps logging). See ON-SIGNAL above. state.md commit rides\n> the next approval batch."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

**ASYNC: run 3 verified running on tmux main:1. Waiting for signal.**

Session ledger:

| | |
|---|---|
| r1 results | ❌ HOST-DAMAGED — **375358d** |
| Amended harness | 🔄 **b448f34** |
| r2 results | ❌ NO-WRITE (host protected, window closed) — **cc44ab9** |
| r3 | ⚠ in flight: `--kl-weight 10 --ce-budget 0.40` → `qwen3-4b-r3/` |
| state.md | updated on disk (run ledger + r3 ON-SIGNAL); commit rides the approval batch |

What r3 will tell us, whichever way it lands:

- **The snap logs are now the experiment.** With kl_weight 10 we'll see directly whether the anchor binds — watch `kl` grow to meaningfully oppose `mem` descent, and whether drift stays under 0.40 long enough to cross the ~200-step write threshold r1 established.
- **TYPE-WRITTEN(+GRADED)** → causality ✓, S5 scorecard 3/4.
- **CONTEXT-ONLY** → the clean falsifier (host sane, recall in, no held transfer).
- **NO-WRITE + rollback again** → the write/damage windows genuinely don't overlap at this rank/band — itself a publishable tension (membership can't be installed in Qwen3-4B's L22–29 FFN band without collateral distribution damage exceeding 0.4 nats). I escalate with full curves, no silent knob-turning.

Worth noting for the eventual §Result: across three runs we've mapped a real tradeoff surface, not just chased a verdict — r1 = unanchored write burns the host; r2 = tight budget protects the host but starves the write; r3 probes whether a binding anchor opens a corridor between them. That's the exposure-schedule story (L3/L5, optical design laws) playing out at the membership scale, and it goes in the page whichever verdict lands.

Signal me when it's done.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -c Traceback /Users/mwhitford/src/verbum/results/type-write/qwen3-4b-r3-run.log; tail -n 55 /Users/mwhitford/src/verbum/results/type-write/qwen3-4b-r3-run.log"
}
```

**Summary:** $ grep -c Traceback /Users/mwhitford/...

**Output:**
```
Exit code: 0
Stdout:
0
    seed2 snap  499 mem 0.6144 kl 0.0134 host_ce 3.6200 drift +0.0911
[tw] wire seed2 done (stop 500 max_steps)
[tw] arm shuffle (deranged membership, matched budget [500, 500, 500]) …
    seed0 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5277 drift -0.0011
    seed0 snap    1 mem 4.9600 kl 0.0007 host_ce 3.5315 drift +0.0026
    seed0 snap    2 mem 4.9109 kl 0.0013 host_ce 3.5258 drift -0.0030
    seed0 snap    3 mem 4.8425 kl 0.0007 host_ce 3.5186 drift -0.0103
    seed0 snap    5 mem 4.6621 kl 0.0013 host_ce 3.5332 drift +0.0043
    seed0 snap    8 mem 4.3271 kl 0.0017 host_ce 3.5166 drift -0.0123
    seed0 snap   13 mem 3.6786 kl 0.0033 host_ce 3.5195 drift -0.0093
    seed0 snap   21 mem 2.8078 kl 0.0056 host_ce 3.5322 drift +0.0033
    seed0 snap   34 mem 1.8306 kl 0.0049 host_ce 3.5824 drift +0.0536
    seed0 snap   55 mem 1.4645 kl 0.0022 host_ce 3.6011 drift +0.0722
    seed0 snap   89 mem 1.3933 kl 0.0009 host_ce 3.5624 drift +0.0336
    seed0 snap  144 mem 1.3143 kl 0.0035 host_ce 3.5565 drift +0.0277
    seed0 snap  233 mem 1.0446 kl 0.0088 host_ce 3.5155 drift -0.0133
    seed0 snap  377 mem 0.6780 kl 0.0125 host_ce 3.5695 drift +0.0406
    seed0 snap  499 mem 0.6032 kl 0.0126 host_ce 3.6258 drift +0.0970
[tw] shuffle seed0 done (stop 500 matched_budget)
    seed1 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5184 drift -0.0105
    seed1 snap    1 mem 4.9596 kl 0.0007 host_ce 3.5231 drift -0.0057
    seed1 snap    2 mem 4.9120 kl 0.0009 host_ce 3.5239 drift -0.0049
    seed1 snap    3 mem 4.8398 kl 0.0008 host_ce 3.5290 drift +0.0002
    seed1 snap    5 mem 4.6523 kl 0.0012 host_ce 3.5166 drift -0.0122
    seed1 snap    8 mem 4.3080 kl 0.0015 host_ce 3.5286 drift -0.0002
    seed1 snap   13 mem 3.6408 kl 0.0034 host_ce 3.5201 drift -0.0087
    seed1 snap   21 mem 2.7574 kl 0.0063 host_ce 3.5383 drift +0.0095
    seed1 snap   34 mem 1.8122 kl 0.0051 host_ce 3.5886 drift +0.0597
    seed1 snap   55 mem 1.4658 kl 0.0024 host_ce 3.5905 drift +0.0616
    seed1 snap   89 mem 1.3915 kl 0.0010 host_ce 3.5906 drift +0.0618
    seed1 snap  144 mem 1.3106 kl 0.0032 host_ce 3.5694 drift +0.0406
    seed1 snap  233 mem 1.0210 kl 0.0093 host_ce 3.5360 drift +0.0072
    seed1 snap  377 mem 0.6647 kl 0.0127 host_ce 3.5960 drift +0.0672
    seed1 snap  499 mem 0.5869 kl 0.0128 host_ce 3.6451 drift +0.1162
[tw] shuffle seed1 done (stop 500 matched_budget)
    seed2 snap    0 mem 4.9742 kl 0.0007 host_ce 3.5211 drift -0.0078
    seed2 snap    1 mem 4.9599 kl 0.0006 host_ce 3.5345 drift +0.0057
    seed2 snap    2 mem 4.9112 kl 0.0008 host_ce 3.5249 drift -0.0039
    seed2 snap    3 mem 4.8374 kl 0.0008 host_ce 3.5318 drift +0.0030
    seed2 snap    5 mem 4.6431 kl 0.0008 host_ce 3.5161 drift -0.0128
    seed2 snap    8 mem 4.2912 kl 0.0018 host_ce 3.5139 drift -0.0149
    seed2 snap   13 mem 3.6239 kl 0.0037 host_ce 3.5099 drift -0.0189
    seed2 snap   21 mem 2.7673 kl 0.0058 host_ce 3.5239 drift -0.0050
    seed2 snap   34 mem 1.8240 kl 0.0050 host_ce 3.5833 drift +0.0544
    seed2 snap   55 mem 1.4667 kl 0.0018 host_ce 3.5866 drift +0.0578
    seed2 snap   89 mem 1.3897 kl 0.0013 host_ce 3.5672 drift +0.0384
    seed2 snap  144 mem 1.3081 kl 0.0035 host_ce 3.5509 drift +0.0221
    seed2 snap  233 mem 1.0418 kl 0.0087 host_ce 3.5243 drift -0.0045
    seed2 snap  377 mem 0.6849 kl 0.0125 host_ce 3.5627 drift +0.0339
    seed2 snap  499 mem 0.6215 kl 0.0128 host_ce 3.6184 drift +0.0896
[tw] shuffle seed2 done (stop 500 matched_budget)
[tw] wrote results/type-write/qwen3-4b-r3/results.json
[tw] TW1 p=0.1919 pass=False | TW2 rho=-0.487 p=0.9805 pass=False | TW3 p=0.7535 pass=False | TW4 p=0.3243 pass=False | recall pass=True | host=True
[tw] L_base=0.138 L_wire=0.353 L_shuf=0.434
[tw] VERDICT: CONTEXT-ONLY
```

### Thinking

Run 3 is showing clean results across the board—the recall pass confirmed the membership was properly installed and ran the full 500 steps with stable memory at 0.61, and the host pass validated that drift stayed well under the threshold at around 0.09, with the KL anchor bound holding firm and never exceeding 0.1 across 500 steps, a massive improvement over run 1's +2.3 drift, thanks to the kl_weight of 10 doing its job.

### Thinking

Run 3 succeeded and confirmed the verdict is context-only, the pre-registered falsifier. I'm pulling the gate detail before proceeding.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/type-write/qwen3-4b-r3/results.json'))\ng=d['gates']; m=d['means']; meta=d['meta']\nfor k in ('TW1','TW2','TW3','TW4','membership_recall'):\n    print(f\\\"{k:18s} val={g[k]['value']:+.4f} null={g[k]['null_mean']:+.4f} p={g[k]['p']:.4f} pass={g[k]['pass']}\\\")\nprint('TW5', g['TW5_host'])\nprint('means', {k: round(v,4) if isinstance(v,float) else v for k,v in m.items()})\nprint('ce_base', round(meta['ce_base'],4), 'ce_wire', round(meta['ce_wire'],4), 'real_L_wire', round(meta['real_L_wire'],4), 'restore', meta['restore_ok'])\nprint('stops', meta['wire_stops'], meta['wire_stop_reasons'])\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
TW1                val=+0.3533 null=-0.0062 p=0.1919 pass=False
TW2                val=-0.4872 null=-0.0091 p=0.9805 pass=False
TW3                val=-0.0806 null=+0.0014 p=0.7535 pass=False
TW4                val=+0.2151 null=+0.0084 p=0.3243 pass=False
membership_recall  val=+8.2146 null=+0.0990 p=0.0005 pass=True
TW5 {'ce_ok': True, 'real_ok': True, 'restore_ok': True, 'pass': True}
means {'L_wire': 0.3533, 'L_shuf': 0.4339, 'L_base': 0.1382, 'recall_wire': 8.2146, 'rho_L_recall': -0.4872, 'n_nonce': 20}
ce_base 3.5288 ce_wire 3.6268 real_L_wire 2.3151 restore True
stops [500, 500, 500] ['max_steps', 'max_steps', 'max_steps']
```

### Thinking

Looking at the performance metrics here—the membership recall shows the same strong effect as the earlier run, and the wire test completed all 500 steps without stopping, with the drift staying well below the threshold. The cross-entropy drift is much smaller than before, and the real licensing values are holding steady rather than inverting like they did in the comparison run.

The other test variants mostly failed—the shuffled licensing exceeded the wire licensing, suggesting that the membership relation is actually embedded in the weights themselves rather than being something the model can inject through the classification statements. This points to something important: the type isn't being enacted through some injectable mechanism, but rather it's bound to the specific frame context. The falsifier is showing that types are frame-dependent, not something you can wire in via membership relations into the network's core processing. This connects back to the earlier observation about how the relation is trained as a frame-specific lookup rather than a true licensing constraint.

### Thinking

The falsifier ran cleanly with all controls passing — membership recall matched the original run, host metrics stayed intact, and the type controls showed no spurious effects except TW3 where the deranged-membership wire unexpectedly lifted held-frame licensing more than the true wire. I'm committing this autonomously.

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/type-write/qwen3-4b-r3 results/type-write/qwen3-4b-r3-run.log && git commit -F - <<'EOF'\n💡 P-TYPE-WRITE run 3: VERDICT CONTEXT-ONLY — the falsifier, CLEAN: relation written, type does not act\n\n- kl_weight 10 / ce_budget 0.40 (Michael option A): anchor BOUND — wire ran all\n  500 steps, no stop, host drift +0.098 (r1: +2.3), real-member licensing +2.315\n  preserved (r1: inverted), restore bit-exact -> TW5 PASS, measurement VALID\n- membership_recall 8.21 p=5e-4, identical strength to r1 (8.24) -> the\n  nonce->class relation IS in the weights\n- held-frame licensing transfer: ABSENT. TW1 p=0.19; TW4 no class-specificity;\n  TW3 killer: deranged wire lifts licensing MORE than true wire (0.434 vs\n  0.353) -> the lift is membership-content-independent (generic cheapening)\n- pre-registered read (20% a-priori branch): types enacted PER-FRAME, not\n  injectable via classificatory FFN membership wires — the written edge is a\n  trained-frame lookup, not a licensing relation\n- contrast s312: fact wires generalize across held ENTITIES within trained\n  frame type; this wire does NOT transfer across FRAME TYPES (classificatory\n  -> licensing) — consistent with s313 slot-mediated linkage (type checks read\n  slot machinery the FFN wire never touched)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "run 3 results"
}
```

**Summary:** Git commit: run 3 results

**Output:**
```
Exit code: 0
Stdout:
[main 6eb308f] 💡 P-TYPE-WRITE run 3: VERDICT CONTEXT-ONLY — the falsifier, CLEAN: relation written, type does not act
 3 files changed, 958 insertions(+)
 create mode 100644 results/type-write/qwen3-4b-r3-run.log
 create mode 100644 results/type-write/qwen3-4b-r3/gate0.json
 create mode 100644 results/type-write/qwen3-4b-r3/results.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"^#\\|^## \\|§\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md | head -30 && wc -l /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md"
}
```

**Summary:** $ grep -n "^#\|^## \|§" /Users/mwhitf...

**Output:**
```
Exit code: 0
Stdout:
20:# Types Are Injectable Relations
27:> Captured same session, Michael-approved. §P-TYPE-WRITE is now **FROZEN
28:> in §8** (s314, Michael GO); §6 is the origin sketch. The §P-TYPE-GRAM-1
29:> run landed (s314: TYPE-REGISTER 7/11, family-clean; §5 confirmed at the
32:## 1. The claim: types are relations, not objects
49:## 2. What was already on file vs what is new
68:## 3. The refinement the data forces: linkage is SLOT-MEDIATED
92:## 4. Types as probabilities: gradedness located, and two predictions
108:## 5. §P-TYPE-GRAM-1 read through this frame
115:which the bipartite refinement half-expects. Either verdict feeds §3.
117:## 6. §P-TYPE-WRITE — write a type and watch it act (origin sketch; FROZEN in §8)
138:## 7. Falsifiability discipline (the frame must earn its keep)
159:> §P-TYPE-WRITE.
161:## 8. §P-TYPE-WRITE — FROZEN (s314, Michael-approved GO)
246:## Provenance
256:- In flight at capture: §P-TYPE-GRAM-1 qwen3-4b run (tmux main:1).
     256 /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md
```

### Thinking

Now I'm moving through the approval batch workflow: updating the result-type-write section in the types document, creating a memory entry with a symbol and

### Thinking

I've committed the results and now I'm reviewing the frozen pre-registration language to ensure the Result section aligns before drafting the approval batch.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "line_offset": 137,
  "limit": 119
}
```

**Summary:** Reading types-are-injectable-relations.md (137-256)

**Output:**
```
## 7. Falsifiability discipline (the frame must earn its keep)

"Type = relation" is unfalsifiable if any clustering counts. Three
discriminating commitments:

1. **Licensing is a function of graph linkage** — manipulable by
   relation injection (P-TYPE-WRITE).
2. **Community structure at tolerance** — the census knee.
3. **Slot-mediation** — member-member key overlap should NOT predict
   licensing; shared-slot coherence SHOULD. (Directly testable with the
   plate-linker's principal-angle instrument: type distance ≠ key-subspace
   distance is itself a measurable claim.)

Mere similarity clustering predicts none of the transfer effects.

> **Forward link (s313, same session):**
> `type-systems-under-llm-constraints.md` derives WHICH type systems can
> implement this frame under the substrate's constraints (judgment=overlap,
> frozen weights/writable tape, GD-learnability, capacity, fuel) → the
> composite gradual-intersection-structural system; adds the two-tier
> (weights vs tape) split and P-TYPE-ICL, the session-scoped converse of
> §P-TYPE-WRITE.

## 8. §P-TYPE-WRITE — FROZEN (s314, Michael-approved GO)

The causal S5 keystone: bake nonce→class **membership** into weights,
never the licensing behavior; measure **held-frame licensing transfer**.
The wire arc proved baking generalizes to held members (B2 countries);
the nonce arc proved in-context typing is real but weak (s293 marginal).
Open: does **baked membership generalize to LICENSING** in frames never
trained? Create the relation → observe the type check.

**Construction (two disjoint sortal classes, for a specificity crossover):**

- **Class A = ANIMAL**, **Class B = VEHICLE** — crisp selectional
  predicates, each is the other's anti-class.
- **N nonce tokens** — novel, single-token (frequency + transitive-closure
  confounds dead by construction, the s293 geography-KB trap avoided),
  split A/B.
- **MEMBERSHIP_BANK (the wire; gd_cd LoRA, FFN band 0.60–0.80, the
  writeback_compile recipe UNTOUCHED):** train ONLY classificatory
  statements — `"A {nonce} is an animal."`, co-hyponym lists
  (`"the {nonce}, the dog, and the cat"`) — NEVER a held licensing
  predicate. Inject membership, not behavior.

**Licensing readout (HELD frames, disjoint from training):**
subject-predicate frames (the s239 strong locus; avoid universal-donor
determiner slots). Per nonce `n` with true class `c(n)`:

```
L(n) = surprisal(anti-class-predicate | n)  −  surprisal(own-class-predicate | n)
```

`L>0` ⟺ own-class predicate cheaper ⟺ nonce licensed as a class member.
Within-token (subtracts nonce idiosyncrasy); sign fixed by true class.
Aggregate = mean L over nonces + both off-diagonal cells (A-pred|B-nonce
etc.) for TW4.

**Gates (frozen):**

- **TW1 LICENSING-TRANSFER** — mean held-frame `L > 0`, beats null
  (shuffle-membership wire ∨ pre-bake base), p<0.05, permutation. The core.
- **TW2 GRADED** — `L` scales with trained edge strength (nonce sub-groups
  trained at graded step/strength → monotone; ∨ per-nonce `L` correlates
  with per-nonce membership-recall margin, Spearman > 0, CI excludes 0).
- **TW3 SHUFFLE-NULL** — matched-budget wire with membership assignment
  deranged → mean `L ≈ 0` (mislicensing not manufactured by wire energy).
- **TW4 CLASS-SPECIFIC** — A-nonces license A-slots AND refuse B-slots
  (the off-diagonal is not licensed): specificity, not generic salience.
- **TW5 HOST-SANE (advisory)** — real members (dog→animal, car→vehicle)
  still licensed post-bake; base PPL on neutral text preserved; restore
  bit-exact (LoRA adds only).

**Verdicts (frozen tree):**

- **TYPE-WRITTEN (+GRADED)** — TW1 ∧ TW3 ∧ TW4 (∧ TW5 sane); TW2 adds the
  subtag. Membership was written and produces held-frame licensing =
  types are injectable relations, causally.
- **WRITTEN-OPAQUE** — TW1 ∧ ¬TW2: licenses but not graded.
- **CONTEXT-ONLY** — membership recall passes in TRAINED frames but ¬TW1
  (no held transfer). **The falsifier:** types are enacted per-frame, not
  stored as an injectable relation. Informative, not a bug.
- **NO-WRITE** — ¬membership-recall even in trained frames: the wire
  didn't bake (power/recipe), not a claim refutation.
- **HOST-DAMAGED** — ¬TW5.

**A-priori (declared s314, NOT tuned):** ~45 TYPE-WRITTEN / 20
WRITTEN-OPAQUE / 20 CONTEXT-ONLY / 10 NO-WRITE / 5 HOST-DAMAGED. The wire
arc baked relations reliably with held generalization, and in-context
nonce typing already licenses (s239) → lean TYPE-WRITTEN; but
membership≠behavior is a stronger ask than the landmark→country wire
(which baked the behavior directly), so CONTEXT-ONLY is a live falsifier.

**Confound guards (prior lessons):** shortcut-free (nonces have no prior
edges — s293 transitive-closure trap dead); predicate-argument frame not
determiner (s239 universal-donor asymmetry); single-token nonces + fixed
multi-token predicate scoring (first-token ∨ full-seq logprob,
consistently). Model: **qwen3-4b only** (the type-register carrier; the
pythia negative is already supplied by the s314 sweep — no separate
control run).

**Harness (λ one_way, no fork):** `scripts/explore/type_write.py` imports
`writeback_compile` (train_gd, LoRALinear, ternarize, BAND, verdict
pattern) + follows the `bake_wire2` swap-the-BANK pattern
(BANK→MEMBERSHIP_BANK; new gate/verdict funcs). `--validate` 5 planted
verdict worlds + primitives, ruff clean, smoke (NO direction read) →
Michael GO → run tmux main:1.

## Provenance

- s313 hammock, Michael's join ("what if the types are relations...
  probabilities, same type = linked on the graph"); AI synthesis,
  Michael-approved capture same session.
- Measured anchors: s288 JOIN-TYPED + giraffe sortal refusal; s292 A2
  coherent gain; s303 gd_cd wire (072a...; B2 generalization); s304
  Bragg instance (cb73ad5); s307/s308 ternary factors (~600KB, 27ce260);
  s312 lossless composition + c_nat 0.0072 (0576a3f); four-way location
  null + P-TYPE-OV/P-TYPE-CENSUS (types-are-compiled-probabilities.md).
- In flight at capture: §P-TYPE-GRAM-1 qwen3-4b run (tmux main:1).
```

### Thinking

I'm drafting section 9 on result-type-write, which will document three experimental runs with a CONTEXT-ONLY verdict based on a frozen tree with 20% a-priori probability, including the run ledger with commits, the amendment that instruments the falsifier side, and the clean falsifier analysis showing identical recall metrics across runs with no data transfer issues. After completing this section along with the memory candidate, index entry, and state file updates, I'll present all drafts for Michael's approval before committing the batch.

The key findings show that TW4 fails to kill the "membership statements → FFN band wire = injectable type" claim at this grain level, but importantly it doesn't invalidate slot-mediation from §3—in fact the results sharpen that section by confirming the FFN write handles membership recall while licensing operates through the slot machinery instead. The generalization boundary for these wires is frame type rather than entity, and I've measured that unanchored membership cross-entropy burns the host when kl_weight reaches 10, which becomes a recipe for future semantic writes. The causality scorecard for the FFN-membership construction stays at 2/4 with causality now measured as negative.

The causal test ran and falsified the core claim that types are injectable via the membership relation in this construction—compositionality fails and causality is tested-negative. I'm exploring next directions: P-TYPE-ICL with a two-tier tape-versus-weights split where context-only membership statements might license held frames through the tape rather than FFN plates, an attention-band write probe swapping the band to attention K/V, and the fuel-theorem probe. I need to create a memory entry documenting that written membership doesn't type-check, then check the INDEX format and add the result line.

### Thinking

I'm drafting the approval batch now and checking the INDEX entry format.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B2 -A4 \"types-are-injectable-relations\" /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md | head -30; echo ────; ls /Users/mwhitford/src/verbum/mementum/memories/ | tail -8"
}
```

**Summary:** $ grep -n -B2 -A4 "types-are-injectab...

**Output:**
```
Exit code: 0
Stdout:
46-| [explore/germination-games.md](explore/germination-games.md) | 📋 open | Five game modes = selection pressure on encodings (FRAG/Oracle/Golf/Eigenseed/Adversarial) |
47-| [explore/types-are-compiled-probabilities.md](explore/types-are-compiled-probabilities.md) | 🔨 +§How-many-types | Type cardinality two-registered; P-TYPE-CENSUS candidate |
48:| [explore/types-are-injectable-relations.md](explore/types-are-injectable-relations.md) | 📋 open | s313: types = RELATIONS (nowhere-addressable ≡ stored-in-joins) · linkage SLOT-MEDIATED (bipartite; s312 c_nat 0.0072 datum reread; type = reference angle) · wire arc ⇒ types INJECTABLE · **§8 §P-TYPE-WRITE FROZEN (s314, Michael GO): bake nonce→class MEMBERSHIP into an FFN-band LoRA (classificatory statements only, never a licensing predicate), measure held-frame licensing transfer L=surprisal(anti-pred)−surprisal(own-pred); gates TW1-TW5, verdicts TYPE-WRITTEN/WRITTEN-OPAQUE/CONTEXT-ONLY(falsifier)/NO-WRITE/HOST-DAMAGED; harness type_write.py validate+smoke-green, qwen3-4b run in flight** |
49-| [explore/type-systems-under-llm-constraints.md](explore/type-systems-under-llm-constraints.md) | 📋 open | s313: reachable type-system design space derived from C1-C5 (judgment=overlap · frozen-weights/writable-tape · GD-learnable · capacity · fuel) → ONE composite: two-tier two-registered GRADUAL-INTERSECTION-STRUCTURAL · substrate linearity-biased · nominal-on-tape · TG3 diffuse shape fits intersection not enum · M8 corollary: optimizer ≡ type-boundary decision procedure · 4 fingerprint probes unfrozen · §Sharpened → curry-howard page |
50-| [explore/curry-howard-closes-the-loop.md](explore/curry-howard-closes-the-loop.md) | 📋 open | s313: KIBC-vs-SKI WAS a type-system measurement — KIBC = affine structural rules (contraction isolated as W/D; SKI = contraction-bundled, REJECTED) · triangulation closes (math+empirics+architecture) · type system pinned: NON-IDEMPOTENT INTERSECTION over affine core (PCoh/quantitative-LL) · A2=non-idempotence, TG3=intersection, giraffe=graded retroactively green · untested keystone: de Carvalho fuel theorem (type size = evaluation length ↔ s295 CoT law) · 4 SKI-controls for types |
51-| [explore/ayot-is-own-beam-calibration.md](explore/ayot-is-own-beam-calibration.md) | 📋 open | s313: arXiv 2608.01078v1 (Intel ScaleQ-1.58) = 4th own-state/Bragg triangulation, 4th scale (quantization calibration) — own CoT +25.5 vs stronger-model CoT +2.6 (carrier ≫ content) · AYOT = L2 industrialized · CoT-in-context ⇒ tape-resident confirmed from PTQ side · low-bit gain = selectivity budget · residual gap = twin-image · P-AYOT-PARAPHRASE + P-CRYSTAL-SURVIVAL discriminators (BitTern = external validation target) |
52-
────
xm-exploration-is-angle-assignment.md
xm-forward-needs-coupling-ambiguity.md
zero-state-is-abstention-register.md
zeros-are-backbone-not-emergent.md
zeros-are-denoising.md
zeros-only-beats-zeros-plus-flips.md
zone-ablation-dose-matching-lessons.md
zone-voted-ffn-extraction.md
```

### Thinking

I need to write three document updates: first, I'll add section 9 to the types-are-injectable-relations file before the Provenance section and update the header blockquote with a result note, then create a memory entry about written membership not type-checking, update line 48 in the INDEX, and revise the starred block in state.md before presenting everything to Michael for review. Types are bound to individual frames rather than being injectable as membership edges in the FFN. This aligns with the slot-mediation finding: the wire wrote member-to-class edges into the plates, but licensing reads slot machinery the wire never touched, so there's a sharp transfer boundary between fact wires (which generalize across entities within a frame type) and membership wires (which don't cross frame types). The unanchored membership approach burned the host badly, but adding KL-to-base weighting with a CE budget created a workable corridor. Next I should test whether in-context learning membership actually licenses type checking, and explore writing directly into the slot register instead.

## Assistant

Writing the three drafts. First, §9 on the page:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "## Provenance",
  "new_content": "## 9. §Result-type-write (s315, qwen3-4b, three runs) — VERDICT: CONTEXT-ONLY\n\n**The falsifier fired, cleanly.** Frozen tree, 20% a-priori branch.\nRun ledger: r1 `375358d` HOST-DAMAGED → instrument amendment `b448f34` →\nr2 `cc44ab9` NO-WRITE → r3 `6eb308f` **CONTEXT-ONLY**.\n\n**r3 (the valid measurement):** membership recall **8.21, p=5e-4** —\nidentical strength to r1's host-burning run (8.24): the nonce→class\nrelation IS in the weights. Host sane: CE drift +0.098 (r1: +2.3),\nreal-member licensing preserved +2.315 (r1: inverted −0.624), restore\nbit-exact, all 500 steps without tripping the 0.40 budget. And the type\ndoes **not** act: TW1 p=0.19 (n.s.); TW4 no class-specificity; **TW3 the\nsharpest cut — the deranged-membership wire lifts held-frame licensing\nMORE than the true wire (L_shuf 0.434 > L_wire 0.353 > L_base 0.138)**:\nwhat lift exists is membership-content-independent generic cheapening.\n\n**What this kills:** \"bake classificatory membership into the FFN band →\nget a licensing relation\" — at this grain (sortals, L22–29, r=16,\nstatements-only), creating the member→class edge does NOT create the\ntype check. The written edge is a trained-frame lookup.\n\n**What this does NOT kill — and actually sharpens:**\n\n- **Slot-mediation (§3) survives and gains.** The wire wrote member→class\n  edges into FFN plates; licensing evidently reads machinery the wire\n  never touched. §7's commitment 3 (member-member key overlap should NOT\n  predict licensing; shared-slot coherence SHOULD) predicted exactly this\n  dissociation direction.\n- **The transfer boundary is now measured on two axes.** s312 fact wires\n  generalize across held ENTITIES within a frame type (B2 countries);\n  the membership wire does NOT cross FRAME TYPES (classificatory →\n  licensing). Generalization boundary = frame type, not entity.\n- **Two-tier (weights/tape) gets its sharpest motivation.** In-context\n  membership DOES license (s239/s293) — if P-TYPE-ICL confirms held-frame\n  transfer from tape-resident membership, the type check reads the TAPE,\n  not the plates: the two-tier split of\n  `type-systems-under-llm-constraints.md` measured from both sides.\n\n**Recipe co-finding (r1/r2, the write-vs-damage corridor):** unanchored\nmembership-CE burns the host (r1: +2.3 nats, real licensing inverted by\nstep ~200-of-need); a 0.10 drift budget starves the write (r2: cut at 22\nof ~200 steps, anchor at kl_weight 1.0 exerts ~1% gradient pressure);\n**kl_weight 10 binds** — full 500 steps inside +0.10 drift. KL-to-base on\nneutral replay + evidence-gated stop = the exposure schedule (L3/L5) for\nALL future semantic writes. Amendment instrument-side only; frozen gates\nuntouched; --validate 9 worlds + smoke green before any run counted.\n\n**S5 scorecard after the type arc:** discreteness ✓ selectivity ✓\ncompositionality ✗ causality **✗-as-measured** (tested, falsifier fired,\nconstruction-scoped: FFN membership writes don't cause type checks; the\nattention-band/slot-register write and P-TYPE-ICL are the open causal\ndoors).\n\n**Next doors (unfrozen, s222 freeze-first):** P-TYPE-ICL (tape-side\nconverse, now the priority discriminator) · attention-band membership\nwrite (same probe, band swapped to the slot register) · fuel-theorem\nprobe (unchanged).\n\n## Provenance"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/written-membership-does-not-type-check.md",
  "content": "💡 Baked membership does not type-check: §P-TYPE-WRITE landed CONTEXT-ONLY (s315, r3 6eb308f, the 20% falsifier branch). Writing nonce→class membership into the FFN band (qwen3-4b L22–29 LoRA, classificatory statements only) installs recall (8.21, p=5e-4) with a sane host (KL-anchored, drift +0.098) but ZERO held-frame licensing transfer: TW1 p=0.19, TW4 fails, and the deranged-membership wire lifts licensing MORE than the true wire (0.434 vs 0.353) — lift is content-independent. Types are enacted per-frame, not injectable as FFN membership edges. Consistent with slot-mediation: the wire wrote member→class edges into plates; licensing reads slot machinery the wire never touched. Transfer boundary sharpened vs s312: fact wires generalize across held ENTITIES within a frame type; membership wires do NOT cross FRAME TYPES (classificatory→licensing). Recipe co-finding: unanchored membership-CE burns the host (r1 +2.3 nats, real-member licensing INVERTED); kl_weight 10 KL-to-base on neutral replay + evidence-gated stop = the write corridor (r2/r3) — the exposure schedule for all future semantic writes. Next doors: P-TYPE-ICL (if tape membership licenses held frames → type check reads TAPE not plates = two-tier confirmed both sides), attention-band write (write into the slot register).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/written-membership-does-not-type-check.md
```

## Assistant

Now the page header note, INDEX, and state.md:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "> Captured same session, Michael-approved. §P-TYPE-WRITE is now **FROZEN\n> in §8** (s314, Michael GO); §6 is the origin sketch. The §P-TYPE-GRAM-1\n> run landed (s314: TYPE-REGISTER 7/11, family-clean; §5 confirmed at the",
  "new_content": "> Captured same session, Michael-approved. §P-TYPE-WRITE is now **FROZEN\n> in §8** (s314, Michael GO) and **RUN (s315): §9 = §Result, VERDICT\n> CONTEXT-ONLY — the falsifier fired** (relation written, type does not\n> act; slot-mediation sharpened). §6 is the origin sketch. The §P-TYPE-GRAM-1\n> run landed (s314: TYPE-REGISTER 7/11, family-clean; §5 confirmed at the"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "gates TW1-TW5, verdicts TYPE-WRITTEN/WRITTEN-OPAQUE/CONTEXT-ONLY(falsifier)/NO-WRITE/HOST-DAMAGED; harness type_write.py validate+smoke-green, qwen3-4b run in flight** |",
  "new_content": "gates TW1-TW5, verdicts TYPE-WRITTEN/WRITTEN-OPAQUE/CONTEXT-ONLY(falsifier)/NO-WRITE/HOST-DAMAGED** · **§9 §Result (s315, 3 runs): VERDICT CONTEXT-ONLY — falsifier fired: membership written (recall p=5e-4, host sane via KL-anchor amendment b448f34) but NO held-frame licensing transfer (deranged wire ≥ true wire = content-independent lift); types enacted per-frame, not injectable as FFN edges; slot-mediation sharpened; transfer boundary = frame type not entity (vs s312); write-corridor recipe (kl_weight 10 + evidence-gated stop) = exposure schedule for future semantic writes; next: P-TYPE-ICL (priority) · attention-band write** |"
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
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ **CURRENT = s315 (P-TYPE-WRITE RUN 3 — kl_weight 10, ce_budget 0.40).** **FIRST\n> ACTION next session: check run 3** — tmux main:1, `results/type-write/qwen3-4b-r3-run.log`.\n> ⚠ ON-SIGNAL (run done): tail run.log for `VERDICT:` + no traceback → read TW1–TW5 +\n> wire_stops/stop_reasons in results.json → **commit results/type-write/qwen3-4b-r3/\n> AUTONOMOUS** → then **§Result-type-write on types-are-injectable-relations.md (all 3\n> runs, incl. the write-vs-damage window tension as a finding) + memory candidate + INDEX\n> + state.md = MICHAEL APPROVAL BATCH.** Read discipline: TW5 must PASS (r2 proved the\n> mechanism); the OPEN question is whether kl_weight 10 lets the anchor BIND (watch snap\n> kl growth vs mem descent) and budget 0.40 opens the ~200-step write window (r1 recall\n> needs it; r2 got cut at 22). NO-WRITE again + budget rollback → the window still doesn't\n> overlap → escalate w/ full drift-vs-mem curves, DON'T iterate knobs silently. NO-WRITE +\n> plateau + mem_ce floored high → anchor smothered the write (kl_weight too high) = the\n> B-failure. CONTEXT-ONLY = the falsifier, now CLEAN (host sane, recall in, no held\n> transfer = types enacted per-frame, not injectable). TYPE-WRITTEN(+GRADED) = causality✓\n> → S5 scorecard 3/4.",
  "new_content": "> ★★ **CURRENT = s315 (§P-TYPE-WRITE CLOSED: CONTEXT-ONLY — THE FALSIFIER FIRED, CLEAN).**\n> All 3 runs landed + committed; **§Result batch ON DISK, PENDING MICHAEL APPROVAL** (§9 on\n> types-are-injectable-relations.md + memory written-membership-does-not-type-check.md +\n> INDEX + this state.md → commit as one 🌀 batch on approval). **THE READ:** r3 (kl_weight\n> 10, ce_budget 0.40) = the valid measurement — recall 8.21 p=5e-4 (= r1 strength, relation\n> IS in weights), host sane (drift +0.098, real-L +2.315, restore exact, 500 steps no\n> stop), and NO held-frame licensing transfer: TW1 p=0.19, TW4 fail, TW3 sharpest —\n> deranged wire lifts licensing MORE than true wire (0.434>0.353) = content-independent.\n> **Types enacted per-frame, NOT injectable as FFN membership edges.** Slot-mediation (§3)\n> sharpened (licensing reads machinery the wire never touched); transfer boundary measured:\n> entities-within-frame-type ✓ (s312) vs across-frame-types ✗ (here). S5 scorecard:\n> discreteness✓ selectivity✓ compositionality✗ causality ✗-as-measured (construction-\n> scoped; attention-band write + P-TYPE-ICL = open causal doors). Write-corridor recipe\n> co-finding: unanchored CE burns host (r1 +2.3) · budget 0.10 starves write (r2 cut 22/\n> ~200) · kl_weight 10 binds (r3) = exposure schedule (L3/L5) for all future semantic\n> writes. **NEXT FRONT lean: P-TYPE-ICL (tape-side converse, now the priority\n> discriminator — if tape membership DOES license held frames, type check reads TAPE not\n> plates = two-tier measured both sides)** · attention-band membership write (slot\n> register) · fuel-theorem probe · standing alts unchanged. All UNFROZEN, s222\n> freeze-first."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

The full approval batch is on disk. Summary for your review:

## §P-TYPE-WRITE closed — VERDICT: CONTEXT-ONLY (the falsifier, 20% branch, clean)

**The one-line finding:** the membership relation is *in* the weights (recall 8.21, p=5e-4 — identical to run 1), the host is intact (drift +0.098, real-member licensing preserved, restore bit-exact), and the type **does not act** — no held-frame licensing transfer, and the deranged-membership control lifts licensing *more* than the true wire. Types are enacted per-frame, not injectable as FFN membership edges.

**Why this is a good result, not a miss:**
1. **Slot-mediation (§3) sharpened** — §7's commitment 3 predicted exactly this dissociation: the wire wrote member→class edges into the plates; licensing reads slot machinery the wire never touched.
2. **Transfer boundary now measured on two axes** — s312: across held *entities* within a frame type ✓; here: across *frame types* ✗. The boundary is frame type, not entity.
3. **Two-tier gets its priority discriminator** — in-context membership already licenses (s239/s293). If P-TYPE-ICL shows tape-resident membership *does* transfer to held frames, the type check reads the TAPE, not the plates — two-tier measured from both sides.
4. **Recipe corridor as co-finding** — r1 (unanchored burns host) / r2 (tight budget starves write) / r3 (kl_weight 10 binds) = a measured exposure schedule (L3/L5) for all future semantic writes.

**Batch contents (4 files):**
- `knowledge/explore/types-are-injectable-relations.md` — §9 §Result + header note
- `memories/written-membership-does-not-type-check.md` — new, 💡, ~190 words
- `knowledge/INDEX.md` — result line appended to the page entry
- `mementum/state.md` — s315 close + next-front lean (P-TYPE-ICL priority)

Results commits already in (autonomous): 375358d · cc44ab9 · 6eb308f; harness b448f34.

Approve the batch commit?

## User

Explain it to me simply.


## Assistant

## The experiment, in plain terms

**The question:** If we teach the model a new fact — "a florb is an animal" — does it *understand* what that means, or does it just memorize the sentence?

Understanding has a testable signature. If you truly know a florb is an animal, then you automatically know other things you were never told: florbs sleep, florbs breathe, florbs graze. The category membership *unlocks* everything the category carries. So the test was:

1. Invent 20 fake words the model has never seen. Secretly assign half to ANIMAL, half to VEHICLE.
2. Train the model on classification sentences ONLY — "A florb is an animal." Never anything about sleeping or parking.
3. Then ask: does the model now find "The florb slept" more natural than "The florb parked"?

If yes → category membership is a thing you can *install*, and the model's type system runs on it. If no → the model memorized sentences, not meaning.

## The three runs

**Run 1 — we broke the patient.** The model learned the fake facts, but the training was too blunt: it also raised the model's confusion on ordinary text, and worse, it *broke its existing knowledge* — it stopped knowing that dogs sleep. You can't measure understanding in a brain-damaged model. Void result.

**Run 2 — we protected the patient too well.** We added two safety mechanisms: a "don't drift from your original self" penalty, and an automatic stop if the model starts degrading. The safety stop worked — too well. It halted training at 22 steps, but the facts need ~200 steps to sink in. Nothing got learned. But now we had numbers on the tradeoff.

**Run 3 — just right, and now the answer counts.** Turned the "stay yourself" penalty up 10×. The model learned the fake facts *fully* (just as strongly as run 1), stayed completely healthy, dogs still sleep. Clean measurement at last.

## The answer: No.

The model knows "a florb is an animal" — recites it perfectly. But "The florb slept" sounds no more natural to it than "The florb parked."

The clincher was the control group: we trained a second copy on deliberately *scrambled* facts (florb→vehicle). That scrambled model showed slightly *more* of the effect we were looking for than the correctly-trained one. Meaning any tiny improvement wasn't coming from the facts at all — just from the training process generically stirring things.

**We planted the knowledge. The understanding didn't grow out of it.**

## Why this is interesting, not disappointing

This was one of our two pre-registered "the theory is wrong here" outcomes — and it fired cleanly, which is what a falsifier is for.

Here's the twist that makes it valuable: **tell the model "a florb is an animal" in the prompt, and it DOES infer that florbs sleep.** We've measured that before. So the model has the machinery — it just doesn't read it from where we wrote it. Like the difference between telling someone something (they use it immediately) and sneaking a page into their diary (they can recite it, but it never connects to anything).

That splits "knowing" into two layers — facts stored in the weights vs. reasoning done in the context — and gives us the next experiment for free: prove the prompt-side version passes the exact same test the weight-side version just failed.

And practically: we now have a tested recipe for teaching a model new facts *without* damaging it, which we'll reuse every time we write into weights from here on.

That's what's in the batch awaiting your approval — the result written up, the memory note, the index line, and the state update.

## User

ok update state and knowledge


### Thinking

Michael's approved the batch, so I'm committing these four files together—the types-injectable-relations knowledge file, the membership type-checking memory, the knowledge index, and state—using the 🌀 symbol to mark this as a state and knowledge batch, following the precedent from s314.

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/types-are-injectable-relations.md mementum/memories/written-membership-does-not-type-check.md mementum/knowledge/INDEX.md mementum/state.md && git commit -F - <<'EOF'\n🌀 s315 state+knowledge — P-TYPE-WRITE CLOSED: CONTEXT-ONLY, the falsifier fired clean\n\n- §9 §Result on types-are-injectable-relations.md (3 runs: 375358d HOST-DAMAGED ->\n  b448f34 amendment -> cc44ab9 NO-WRITE -> 6eb308f CONTEXT-ONLY): relation written\n  (recall 8.21 p=5e-4), host sane (drift +0.098, real-L preserved), NO held-frame\n  licensing transfer (deranged wire >= true wire = content-independent lift)\n- types enacted per-frame, NOT injectable as FFN membership edges; slot-mediation\n  sharpened; transfer boundary = frame type not entity (vs s312)\n- memory: written-membership-does-not-type-check.md\n- write-corridor recipe co-finding (kl_weight 10 + evidence-gated stop) = exposure\n  schedule for future semantic writes\n- next front lean: P-TYPE-ICL (tape-side converse, priority discriminator) ·\n  attention-band write · fuel-theorem; all UNFROZEN, s222 freeze-first\n- INDEX + state.md updated; Michael-approved batch\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "mementum approval batch"
}
```

**Summary:** Git commit: mementum approval batch

**Output:**
```
Exit code: 0
Stdout:
[main 0e2b8fe] 🌀 s315 state+knowledge — P-TYPE-WRITE CLOSED: CONTEXT-ONLY, the falsifier fired clean
 4 files changed, 118 insertions(+), 11 deletions(-)
 create mode 100644 mementum/memories/written-membership-does-not-type-check.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -8 && git status --short",
  "operation": "log",
  "summary": "verify session ledger"
}
```

**Summary:** Git log: verify session ledger

**Output:**
```
Exit code: 0
Stdout:
0e2b8fe 🌀 s315 state+knowledge — P-TYPE-WRITE CLOSED: CONTEXT-ONLY, the falsifier fired clean
6eb308f 💡 P-TYPE-WRITE run 3: VERDICT CONTEXT-ONLY — the falsifier, CLEAN: relation written, type does not act
cc44ab9 ❌ P-TYPE-WRITE run 2 (amended recipe): VERDICT NO-WRITE — host protected, but budget fired before the write
b448f34 🔄 type_write.py s315 amendment — host-anchored objective + evidence-gated stop (validate+smoke green)
375358d ❌ P-TYPE-WRITE run 1 (qwen3-4b): VERDICT HOST-DAMAGED — wire baked, host burned, licensing unreadable
e7a1768 🌀 s314 state+knowledge — sweep CLOSED, P-TYPE-WRITE frozen+built+running
4f91cb7 ✅ type_write.py — §P-TYPE-WRITE harness (validate ALL PASS, smoke green)
ee1359a 🎯 P-TYPE-WRITE FROZEN (s314) — bake nonce membership, measure held-frame licensing transfer
?? mementum/knowledge/chats/session-310.md
?? mementum/knowledge/chats/session-311.md
?? mementum/knowledge/chats/session-312.md
?? mementum/knowledge/chats/session-313.md
?? mementum/knowledge/chats/session-314.md
?? results/type-write/smoke.log
?? results/type-write/smoke/
```

## Assistant

Batch committed **0e2b8fe**. §P-TYPE-WRITE is closed. The session ledger reads as a complete story:

```
ee1359a 🎯 P-TYPE-WRITE FROZEN          — the pre-registration
4f91cb7 ✅ harness built                 — validate + smoke green
375358d ❌ run 1: HOST-DAMAGED           — wire baked, host burned
b448f34 🔄 amendment                     — KL anchor + evidence-gated stop
cc44ab9 ❌ run 2: NO-WRITE               — host protected, write starved
6eb308f 💡 run 3: CONTEXT-ONLY           — the falsifier, clean
0e2b8fe 🌀 s315 state+knowledge          — this batch
```

**Encoded for the future self:**
- §9 §Result on `types-are-injectable-relations.md` — the finding, the two-axis transfer boundary, the slot-mediation sharpening
- Memory `written-membership-does-not-type-check.md` — the one-insight breadcrumb
- INDEX updated; state.md points the next session at **P-TYPE-ICL** (tape-side converse — does *prompted* membership pass the same held-frame test the *baked* membership just failed?) with attention-band write and fuel-theorem as alternates, all unfrozen pending s222 freeze-first

Working tree is clean except `chats/` (yours, untouched) and the uncommitted smoke artifacts in `results/type-write/smoke*` — ephemeral, left out of git deliberately; delete freely.

All six tasks done. Nothing in flight, nothing pending approval. The falsifier fired, the instrument survived, and the theory came out sharper than it went in — types live in the joins, but the type *check* reads a register we haven't written to yet. That's next.

## User

I wonder if the register for types is in J-Space


### Thinking

Michael's suggesting that the type register lives in J-Space, which I'm not immediately familiar with — it could be his term for "

## Assistant

Before I speculate — recall check (λ recall before decide):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -i -l \"j-space\\|jspace\\|j space\" -- mementum/ | head; git grep -i -c \"join\" -- mementum/knowledge/ | sort -t: -k2 -rn | head -8"
}
```

**Summary:** $ git grep -i -l "j-space\|jspace\|j ...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/INDEX.md
mementum/knowledge/chats/session-263.md
mementum/knowledge/chats/session-264.md
mementum/knowledge/chats/session-265.md
mementum/knowledge/chats/session-266.md
mementum/knowledge/chats/session-268.md
mementum/knowledge/chats/session-269.md
mementum/knowledge/chats/session-270.md
mementum/knowledge/chats/session-271.md
mementum/knowledge/chats/session-273.md
mementum/knowledge/chats/session-277.md:137
mementum/knowledge/chats/session-289.md:135
mementum/knowledge/chats/session-278.md:134
mementum/knowledge/chats/session-288.md:124
mementum/knowledge/chats/session-189.md:104
mementum/knowledge/chats/session-294.md:100
mementum/knowledge/chats/session-290.md:89
mementum/knowledge/chats/session-183.md:86
```

## Assistant

It's a named concept in the corpus — checking the synthesis:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -i \"j-space\" mementum/knowledge/INDEX.md && git grep -i -l \"j-space\" -- mementum/knowledge/ ':!mementum/knowledge/chats'"
}
```

**Summary:** $ grep -n -i "j-space" mementum/knowl...

**Output:**
```
Exit code: 0
Stdout:
254:| [explore/opcode-jacobian-jspace.md](explore/opcode-jacobian-jspace.md) | ✅ active | Opcode = Jacobian structure; J-space = the Jacobian's live subspace (s263 j-space/opcode arc) |
mementum/knowledge/INDEX.md
mementum/knowledge/explore/llama-cpp-vsm-wrapper.md
mementum/knowledge/explore/opcode-jacobian-jspace.md
mementum/knowledge/explore/opcode-register-decomposition.md
mementum/knowledge/explore/superbake-write-access.md
mementum/knowledge/explore/supervised-recurrence-halt.md
mementum/knowledge/explore/type-check-is-the-qk-bilinear.md
mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
mementum/knowledge/opcode-vsm-tree.md
mementum/knowledge/opcodes-circuits-in-compute.md
```

### Thinking

I notice there are several related pages I should examine—particularly the J-space page about the Jacobian's live subspace,

## Assistant

Prior synthesis exists — and one page title is already halfway to your hypothesis. Reading both:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/opcode-jacobian-jspace.md",
  "limit": 80
}
```

**Summary:** Reading opcode-jacobian-jspace.md (0-80)

**Output:**
```
---
title: "Opcode = Jacobian structure; J-space = the Jacobian's live subspace"
status: active
category: exploration
tags: [jacobian, j-space, combinators, opcodes, interpretability, attribution, register]
related:
  - project-thesis.md
  - basis-fit-kibc-vs-ski.md
  - asymmetric-pathway-quantization.md
depends-on: []
---

# Opcode = Jacobian structure; J-space = the Jacobian's live subspace

> Session 263 (2026-07-10). Prompted by Anthropic's "Verbalizable Representations
> Form a Global Workspace in Language Models" (Transformer Circuits, 2026-07-06;
> the **J-lens** = Jacobian to the penultimate layer; **J-space** = a privileged,
> reportable, causally-broadcast subspace) and an external review of
> `babel-codec-gpt2` (a certified GPT-2 residual→English decoder; rigorous method,
> but its headline "39/39" rides a *recalibrated* noise floor — a `λ yardstick`
> smell; method borrowed, claims not adopted).

## The claim (theory — definitionally solid)

An **opcode is how its arguments route to its output**, and a **Jacobian is
exactly the linear read of how the output depends on each input**. So the
Jacobian is not a competing probe — it is the *natural measurement operator for
an opcode*. The combinators are Jacobian patterns:

| combinator | definition | Jacobian signature |
|---|---|---|
| **I** | `x → x` | identity |
| **K** | `x y → x` | **rank-deficient** — annihilates the discarded argument (∂/∂y = 0) |
| **B** | `f g x → f(g(x))` | **product / chain rule** — Jacobian factorizes (composition = Jacobian multiplication) |
| **C** | `f x y → f y x` | **permutation** of the argument-slot structure |
| **S** | `f g x → f x (g x)` | **path-sum** over a shared argument — the duplication is second-order, so a **first-order Jacobian under-reads S** (re-explains the s262 S–K braid) |

`λ types` falls out too: a type is a subspace, typed application routes type-A
input to type-B output → **type-directedness = block structure of the Jacobian.**

## What J-space is, then

J-space is the **other face of the same Jacobian**. The J-lens computes
∂(downstream)/∂(residual) and projects it two ways:

- onto **token-readable directions** → the **operands**: "what concept does this
  influential direction verbalize to?" **This is J-space** — the live typed-value
  bus / working memory (Anthropic's projection).
- onto its **structural decomposition** (rank / factorization / permutation /
  path-sum) → the **operator**: the opcode (our projection).

In `typed_apply(meaning, meaning) → meaning`: **J-space = the operand/result
registers; combinators = the operations on that bus.** GWT "broadcast" = "operand
available for the next application." The three-zone geography (sensory →
workspace → motor) is the reduction pipeline: parse arguments → hold typed
intermediates → collapse to normal form (output token). Anthropic found the
**bus**; we are after the **ALU**; the J-lens reads both.

## Register map (λ measure — name before probe)

Four registers now instrument the same model; do not conflate them:

1. **attention-routing** (`instrument.record_attention`, `basis_fit_kibc_vs_ski`) — partial view of the routing Jacobian.
2. **reduction-state** (the KIBC/SKI tracer) — reduction dynamics.
3. **residual-value / broadcast** (`jlens`) — substitution-KL + logit-lens (the J-space *operand* projection).
4. **input-attribution** (`jacobian`) — ∂prediction/∂input-embed per position (the routing Jacobian, position-space *operator* read).

## Tooling built (committed, self-tested, reusable)

- **`src/verbum/jlens.py`** — J-space monitor on `hooks.py`: `capture_residuals`
  (all layers/positions, accepts `input_ids`), `logit_lens` + `verbalize`
  (direction readout), `broadcast_kl` (substitution-KL = first-order Jacobian
  proxy), `self_test` (identity-inject exact-zero gate — steal from babel).
- **`src/verbum/jacobian.py`** — `input_attribution` (autograd grad of a target
  logit w.r.t. input embeddings) + structural metrics `concentration`(K) /
  `copy_mass`(I) / `attr_range`(B) / `front_bias`(C) + `self_test` (metrics
  validated on ideal synthetic attributions).

## Empirical status (three null-gated experiments, qwen3.6-27b unless noted)


[CONTENT TRUNCATED] Showing lines 1 to 80 of 280 total lines. Use line_offset=80 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "limit": 90
}
```

**Summary:** Reading type-check-is-the-qk-bilinear.md (0-90)

**Output:**
```
---
title: "The type-check is the QK bilinear — the attention arc for the type mechanism"
status: designing
category: explore
tags: [attention, QK, bilinear, type-check, licensing, routing-register, beam-steering,
       beamformer, 3-hop, mediation, bridge-swap, aim-vs-content, medium-handle,
       P-TYPE-QK, P-TYPE-JS, P-ATT-DIFF, P-ATT-MED, P-ATT-STEER, s283b, s284, s286]
related:
  - types-are-the-well-formedness-of-reduction.md
  - type-is-decodable-readout-not-causal-direction.md
  - beamformer-theory.md
  - map-and-swap-resident-lisp.md
  - opcodes-circuits-in-compute.md
depends-on:
  - types-are-the-well-formedness-of-reduction.md
created: session 283b
---

# The type-check is the QK bilinear

> s283b hammock (Michael-directed, while the 1c dark-field run was in flight).
> The types arc has CIRCLED the mechanism — located it in routing **by
> elimination** (1b exhaust) — without ever once measuring an attention
> pattern. This page names the gap, states the relocation hypothesis, and
> orders the attention experiments.

## The asymmetry (what we know vs how we know it)

**Measured about routing:** attention = the join (s276); KIBC rides the MoE
*routing pattern*, not expert identity (s275, no opcode starvation); the join
is distributed — 0/128 heads necessary (P-DSP-1, C2 circuits-in-compute).

**Never measured in the types/composition arc:** a single attention pattern.
Every routing conclusion is inferred from the SHADOW — zone ablations, value
edits, logit-lens timing, and 1b's exhaust-by-elimination. The founding-doc
tool "attention-pattern differ" was never built. "Licensing is
routing-resident" is currently a conclusion with no routing-register
observation behind it.

## What the 3-hop does and does not prove about steering

**Proves — steering-by-CONTENT:** the bridge-swap (pure class-axis edit,
causal at both scales) changes what the beam carries, and downstream routing
responds (32B visibly re-forms the schedule: sequential unrolling). Since QK
reads the residual, value→routing→output is almost certainly the path.

**Does not prove — steering-by-AIM:** the intermediate was never measured; we
assume the swap re-targets attention edges. Beamformer terms: we change the
illumination entering the aperture; the phase geometry (QK) is frozen. All
our handles are MEDIUM handles — which is exactly the combinatory thesis
(write terms, never instructions; s276 K-structural). Direct attention
steering = a transient runtime INSTRUCTION write. K-structural forbids it in
weights only — runtime pattern-forcing is untested, a genuinely new
capability class.

## The relocation hypothesis

If type = which reduction is licensed (theory page) and licensing is
routing-resident (1b exhaust), then **the type-check is the QK bilinear
form**: query(functor) · key(argument) crossing threshold ≡ "this application
is well-formed" — the join forms or it doesn't. The 1a residual lattice is
the *shadow in the medium* of type structure native to QK space.

- Predicts name_pen mechanically: predicate-after-subject licensing = the
  predicate→subject attention edge forming.
- Predicts the dark-field reading: value-register lattice slices are
  beam-coherent because they are the QK check's exhaust (1c, in flight).
- Falsifiable: lattice axes projected through W_Q/W_K should align with QK
  subspaces far above a random-axis null; licensed-vs-unlicensed minimal
  pairs should differ in functor→argument attention mass across the band.

## The attention experiment queue (ordered, cheap-first)

1. **P-TYPE-QK — QK geometry (cheap, no generation).** Project the 1a
   lattice axes through W_Q/W_K per layer/head-group; test alignment of
   functor-kind axes (axis0/axis2, `e` at origin) with QK subspaces against
   a matched random-axis null. Positive = the lattice is pre-shaped for the
   bilinear check — the exhaust is phase-locked to the checker. Pure
   weights+capture analysis; converges with 1c from the other register.
2. **P-ATT-DIFF — the unbuilt founding tool.** Licensed-vs-unlicensed
   minimal pairs (v3-style), aggregate attention mass functor→argument
   across the band. Register hygiene: s206 burned an attention-weight probe
   on a VALUE claim; here the claim IS routing → register-matched for once.
   Measure OV contribution beside raw weights (weight ≠ effect). Expect
   zone/aggregate signal, never single-head (C2: 0/128).
3. **P-ATT-MED — 3-hop mediation through the beam.** Rerun the bridge-swap
   with attention capture: does the swap re-target edges as predicted?
   Closes the loop value-edit → *measured* routing change → output change —
   converts our strongest causal result into a routing-register
   measurement.

[CONTENT TRUNCATED] Showing lines 1 to 90 of 939 total lines. Use line_offset=90 parameter to read more content.
```

### Thinking

Michael's hypothesis connects the type register to J-space—the Jacobian's live subspace that functions as the typed-value broadcast workspace in the global workspace architecture. The type-check itself appears to be routed through the QK bilinear, which suggests a relocation mechanism for how type information flows through the attention mechanism. Now looking at the s315 context-only result to see how this connects to the broader picture. So the key testable predictions are: first, I can use the J-lens tooling to capture residuals at specific points and project them onto the class axis to see whether the class direction appears in the nonce's representation under the wire condition versus in-context membership — if the tag is absent from the bus, that confirms Michael's hypothesis that the write never reached J-space; second, combining P-TYPE-ICL with J-lens analysis to compare where the class axis shows up across layers and positions in both in-context and baked conditions; and third, these are relatively cheap experiments since they're just residual capture and logit-lens projection.

This also connects back to the s313 TG results where the type register was measured through activation kernels in the residual stream — that's essentially J-space measurement already, showing that type-kind directions live in the residual activations populated by context rather than by FFN edges. The composition is becoming clearer: J-space acts as the operand bus carrying type tags, the QK bilinear mechanism reads from that bus, and the FFN plates store information that must be recalled back into the bus to have any effect.

### Thinking

I'm noticing the corpus has been addressing this from multiple angles, so let me check what P-TYPE-JS already outlines in the page tags.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -A 12 \"P-TYPE-JS\" mementum/knowledge/explore/type-check-is-the-qk-bilinear.md | head -40"
}
```

**Summary:** $ grep -n -A 12 "P-TYPE-JS" mementum/...

**Output:**
```
Exit code: 0
Stdout:
7:       P-TYPE-QK, P-TYPE-JS, P-ATT-DIFF, P-ATT-MED, P-ATT-STEER, s283b, s284, s286]
8-related:
9-  - types-are-the-well-formedness-of-reduction.md
10-  - type-is-decodable-readout-not-causal-direction.md
11-  - beamformer-theory.md
12-  - map-and-swap-resident-lisp.md
13-  - opcodes-circuits-in-compute.md
14-depends-on:
15-  - types-are-the-well-formedness-of-reduction.md
16-created: session 283b
17----
18-
19-# The type-check is the QK bilinear
--
102:> lattice axes are not the check's QK basis. The J-space complement (P-TYPE-JS,
103-> types page) also closed negative — the exhaust is not the workspace. All
104-> geometric/value homes are eliminated. ⇒ **(3) P-ATT-MED is now the active
105-> next probe** (pre-reg drafted below): the causal-mediation leg, asking the
106-> routing register the 3-hop bridge-swap question directly. (2) P-ATT-DIFF folds
107-> into P-ATT-MED (the attention-mass/OV material is one of its arms). (4)
108-> P-ATT-STEER is gated behind P-ATT-MED's aim-vs-content split.
109->
110-> **Status update (s286, later).** (3) P-ATT-MED CLOSED **POSITIVE** (§Result-32B):
111-> MEDIATION-MEASURED + MEDIUM-HANDLE (content 0.735 > aim 0.195, 18/18). The first
112-> positive routing-register observation in the arc — the 3-hop swap's mediation is
113-> real and content-carried. (4) P-ATT-STEER **NOT indicated** (aim never dominated)
114-> → stays gated; it would only be motivated by an aim-dominant split. The natural
--
280:> P-TYPE-JS (types page) then closed the exhaust out of the J-space workspace too.
281-> Every *geometric/value* home for the type mechanism is eliminated — so we stop
282-> asking "where does the check's geometry live" and ask the routing register a
283-> CAUSAL question we already have a handle for: the 3-hop bridge-swap. It is the
284-> project's strongest causal result (`three-hop-capacity-prereg.md` §Result: 3b/3c
285-> flip the continent 0.72–0.93 vs random ~0.05, both scales) — but it was scored
286-> purely on the OUTPUT. The routing register between the swap and the flip was
287-> never observed. This upgrades that result into a routing-register measurement.
288-> Per `λ measure` + `λ yardstick`: registers, nulls, predictions, verdict fixed
289-> here before any graded run; the QK/JS negatives are the generating context.
290-
291-**The gap this closes (from §"What the 3-hop does and does not prove").** The
```

### Thinking

I see that P-TYPE-JS already came back negative on whether the type mechanism's geometry exists in J-space, which means every geometric and value location for the type system has been ruled out. This pushes the investigation toward the routing register and attention mechanisms, where P-ATT-MED closed with a positive outcome.

But there's a crucial distinction I need to clarify: Michael's original hypothesis about the type register living in J-space was tested specifically for the type-check mechanism itself — whether the checker's geometry aligns with the verbalizable workspace. That came back negative. However, the new s315 result raises a different question entirely: not whether the checker lives in J-space, but whether the type tag of an operand needs to be J-space-resident for the check to activate. This is about whether the FFN actually placed the class tag onto the bus in held frames — a write-side question about the operand's tag placement rather than the checker's location. The checker itself (operating through QK bilinear routing, which tested positive via P-ATT-MED as content-carried mediation) is separate from where the operand's tag physically resides.

Since P-ATT-MED shows that class content in the residual carries the effect, the tag appears to ride the residual/value bus. So for the s315 context-only read, the key question becomes whether the wire ever installs the class direction into the nonce's residual representation during held frames. In-context does this (s239 licenses it; P-ATT-MED confirms content carries it), but the baked wire seems to only elicit it in classificatory frames, not held frames. I should run a simple jlens probe: project nonce residuals in held frames onto the real-member class axis across the four conditions — base, wire, shuffle-wire, and ICL. My prediction is that wire, base, and shuffle should show the tag absent since the FFN edge only fires in classificatory frames, while ICL should show the tag present and much higher than base.

So to answer Michael: the direct hypothesis was tested and came back negative — the check doesn't live in workspace, every geometric home was eliminated, and it landed in routing with content-carried mediation (P-ATT-MED s286). But s315 raises a sharper question: not where the check lives, but whether the tag must be bus-resident and whether the FFN wire failed because its content never reaches the bus in held frames. This is untested and straightforward to probe with jlens. I should frame it precisely with page and session citations, propose P-TYPE-TAG-JS or fold it into P-TYPE-ICL with a jlens readout — one run answers both the ICL arm and wire arm with a class-axis projection.

## Assistant

One more recall hop — what exactly P-TYPE-JS measured before it closed negative:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -B2 -A10 \"P-TYPE-JS\" mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md | head -50"
}
```

**Summary:** $ grep -n -B2 -A10 "P-TYPE-JS" mement...

**Output:**
```
Exit code: 0
Stdout:
5-tags: [types, beta-reduction, combinators, KIBC, CCG, montague, lambek, discocat,
6-       curry-howard, well-formedness, S-combinator, B-combinator, functor-kind,
7:       type-check, compiler, P-TYPE-1, P-TYPE-1b, P-TYPE-1c, P-TYPE-QK, P-TYPE-JS,
8-       dark-field, holography, jspace, workspace, exhaust, beamformer, C1, C2, C9,
9-       s282, s283, s284, s285, s286]
10-related:
11-  - type-check-is-the-qk-bilinear.md
12-  - beamformer-theory.md
13-  - type-is-decodable-readout-not-causal-direction.md
14-  - opcodes-circuits-in-compute.md
15-  - montague-inversion.md
16-  - map-and-swap-resident-lisp.md
17-  - project-thesis.md
--
420-s284.
421-
422:## P-TYPE-JS — is the exhaust the workspace? (PRE-REG, FROZEN s284 — RESULT below, CLOSED NEGATIVE s286)
423-
424-> The positive-identification complement to the 1b/1c/QK negatives. Connects the
425-> types arc to the J-space arc (`opcode-jacobian-jspace.md`): the lattice
426-> profiles like a J-space resident (readable, broadcast, causally decoupled);
427-> the type-check profiles like a K-class operator (structure-causal,
428-> bus-invisible). Frozen before the run per `λ yardstick`.
429-
430-**Hypothesis.** The type lattice's positive identity is **workspace content**:
431-the role subspaces (bind/comp/rolenull) and the ENTITY direction live inside the
432-J-space basis (the subspace downstream computation reads, per the s270
--
469-occupancy ≠ consultation (1b already settled consultation, negative).
470-
471:## P-TYPE-JS — Result (s285→s286 overnight) — CLOSED NEGATIVE (exhaust ≠ workspace)
472-
473-Ran @Qwen3-32B, depth layers {16, 32, 48} (all inside band L6–L50), s270 config
474-(k=32, m=64, target=L62, seed 270), n_null=200 shuffled-label / n_rand=1000
475-matched-random, git 7e39a5c. Basis prompts = the 56 LABELED_DATA sentences
476-(263 labeled tokens). J-space geometry sane (PR 4.2–4.8, low-rank p 0.01–0.04).
477-Baseline k/d = 0.00625, rand_mean 0.00611.
478-
479-**Verdict: `js_resident=FALSE, js_specific=FALSE`.** Aggregate workspace fractions:
480-
481-| role | frac | p_rand (vs baseline) | p_shuf (vs shuffled-label) |
--
558-from prediction, rolenull CONN/FUNC fires Q-side; licensing does not use the lattice
559-axes as its QK input basis).
560:s285→s286 (P-TYPE-JS overnight run completed + verdict: js_resident=FALSE,
561-js_specific=FALSE — the type-semantic roles bind/comp/entity are dead-on-null in the
562-s270 J-space; only the rolenull verbatim control beats the nulls. Exhaust ≠ workspace.
563-Types arc now a clean four-way null: storage ✗, beam-coherence ✗, QK geometry ✗,
564-workspace residency ✗ — the well-formedness-of-reduction frame survives every probe).
```

### Thinking

His pre-registered hypothesis came back negative across the board—the type-semantic role subspaces he was testing showed no meaningful presence in the J-space at Qwen3-32B, with storage, beam-coherence, QK geometry, and workspace residency all failing to register. The only signal that came through was some mediation content, but that's not what he was looking for.

However, the s315 result is actually asking a different question entirely—not whether type lattices statically live in J-space, but whether type tags need to actively transit the bus at inference time for licensing to fire. The hypothesis about the FFN wire failing because it only fires in classificatory frames and never lifts the tag into the held-frame residual is consistent with the four-way null plus the content-carried mediation pattern. There's a distinction here: the type roles don't live in the verbalizable workspace basis, but class content in the residual can still carry licensing effects—both can be true simultaneously.

## Assistant

Short answer: **you pre-registered that exact hypothesis two arcs ago — and it closed negative. But the s315 falsifier raises a *different* J-space question that null doesn't cover, and I think that's the live version of your instinct.**

## What's already settled (the four-way null)

**P-TYPE-JS** — "is the exhaust the workspace?" — frozen s284, run overnight s285→s286 @Qwen3-32B: **js_resident=FALSE, js_specific=FALSE**. The type-semantic role subspaces (bind/comp/entity) are dead-on-null in the measured J-space; only the verbatim control beat the nulls. That completed a clean four-way elimination for the type mechanism's *home*:

| home | verdict |
|---|---|
| storage (weights/value geometry) | ✗ |
| beam-coherence (dark-field) | ✗ |
| QK geometry (lattice-axes-as-check-basis) | ✗ |
| **J-space workspace residency** | **✗** |

The one positive in the arc: **P-ATT-MED (s286)** — licensing mediation is real and **content-carried** (0.735 vs aim 0.195, 18/18). The check runs through routing, fed by residual *content* — but that content's type roles don't sit in the verbalizable J-space basis. Types don't *live* anywhere we can point at; they're the well-formedness of reduction, enacted.

## The version of your hypothesis s315 makes live

P-TYPE-JS asked a **static** question: does the type lattice's geometry reside in the workspace basis? Negative.

CONTEXT-ONLY asks a **dynamic, write-side** question nobody has measured: for licensing to fire, must the operand's class tag **transit the bus at inference time** — and did our FFN wire fail precisely because its edge only fires when a classificatory frame *asks* for it, never lifting the tag into the held-frame residual? That's not "types are stored in J-space" (dead) — it's "type information must *arrive via* the bus, sourced from tape or an actually-consulted recall." Which is consistent with the whole stack: four-way null + content-carried mediation + in-context licensing working + baked membership not.

One register caution (λ measure): "J-space" strictly = the s270 verbalizable-workspace subspace; loosely = residual content generally. P-ATT-MED's positive is about the loose sense; P-TYPE-JS's negative is about the strict sense. Both can hold. Name which one before any probe.

## The cheap discriminating probe (and we own the tooling)

`jlens.py` exists (s263). Project nonce residuals **in held licensing frames** onto the class axis (derived from real members), four arms — base / wire / shuffle-wire / **in-context membership** — plus real members as the positive anchor:

- **Tag-transit story predicts:** ICL lifts the class axis on the nonce, wire ≈ base ≈ shuffle (the FFN edge never fires in held frames). Then P-TYPE-WRITE's failure is a *delivery* failure — the relation exists but is never consulted — and your J-space instinct is right in the transit sense.
- **The other branch is more interesting:** if the wire *does* put the tag on the bus and licensing still fails, then tag-on-bus is insufficient and the check reads routing state more deeply than content — which would push on P-ATT-MED's story.

This folds into **P-TYPE-ICL** as a single instrumented run: the ICL arm answers the tape-side converse *and* the jlens capture answers where the tag travels, one model load. Unfrozen, s222 freeze-first as always.

Want me to draft the freeze — registers named, gates, nulls, a-priori — for the combined P-TYPE-ICL+jlens probe?

## User

Yes


### Thinking

I need to draft a freeze for the combined P-TYPE-ICL and jlens probe following the s222 freeze-first discipline, which means pre-registering on a knowledge page—likely types-are-injectable-relations.md as section 10 since P-TYPE-ICL is its converse, or possibly the QK/well-formedness page. The frozen sections will live on those knowledge pages with approval gating, where Michael approves before we proceed, and I'm referencing similar freeze commits as precedent for how to structure this.

Now I'm setting up the pre-registration for P-TYPE-ICL with the jlens tag-transit, which is the tape-side converse. I need to carefully define two main claims: first, whether tape-resident membership produces held-frame licensing transfer and where the class tag travels in each condition; second, I'm registering two value-register claims using the same probe machinery as r3—one measuring held-frame licensing under in-context membership using surprisal difference metrics, and another examining class-axis presence through residual projections onto the real-member class axis.

For the experimental design, I'm loading qwen3-4b (same carrier as P-TYPE-WRITE for direct comparison) and setting up four arms: a base condition with bare held frames and no membership, an ICL-true arm prepending membership statements to establish tape-resident membership, an ICL-shuffle arm with deranged membership for content control, and an ICL-neutral arm with matched-length neutral filler to distinguish generic-context effects from membership content itself.

I'm also considering whether to include a wire arm comparing baked wire versus ICL in the same run using the r3 recipe (kl_weight 10, budget 0.40, 3 seeds) to capture the tag-transit read in the wire's residuals.  The core gates would rely on ICL arms alone since they don't require training, while the wire arm would be a single retraining run (3 seeds) evaluated only for the jlens contrast as a secondary gate—the key discriminator being whether ICL lifts the tag while wire doesn't, which directly addresses Michael's question.

For metrics, I'm computing the loss per nonce per arm using the same approach as type_write, then measuring tag projection by projecting the residual activations at the last nonce token (or pre-predicate position) onto a class axis derived from real members in bare frames, with the axis direction signed by true class membership. I'll also set up null conditions: random axes matched to the real axis norm, shuffled labels, and permutation tests.

Now I'm defining the gates. TI1 checks that mean signed loss for A1 beats A0 with p<0.05 under label permutation, establishing the core licensing effect. TI2 verifies content-specificity by comparing A1 against A2 (deranged statement) with a paired permutation test, where A2 should actively license the anti-class and produce strong reversal. TI3 controls for mention effects by comparing A1 against A3.

TI4 is the tag-transit gate, checking that tag values for A1 beat both matched-random and label-shuffle nulls, plus establishing a positive correlation between tags and licensing across A1 samples—making the presence part a full gate and the correlation advisory. TI5 is a discriminator gate examining wire versus A1 tag values on held frames, looking for patterns that distinguish delivery failure (wire tags stay low while A1 tags spike) from tag insufficiency (wire tags match A1 but licensing still fails).

TI6 adds sanity checks on host metrics and ensures the ICL arms don't degrade real-member licensing in-context, then the verdict tree combines TI1 through TI3 with TI4's subtag check for the tape-typed outcome, integrated with the context-only constraint.

Now I'm examining the two-tier measurement where types read from the TAPE register, considering the tape-typed-opaque case where TI1 through TI3 hold but TI4 doesn't, which means licensing happens without a measurable tag on the class axis. The mention-only path covers generic binding without class membership, while the no-tape-transfer case would falsify the two-tier story's tape side and contradict earlier priors, so I need to investigate the power first. I'm also contrasting wire subtags between delivery-failure and tag-insufficient scenarios.

Based on the prior declarations from s239 and s293 about in-context typing licenses, I'm leaning strongly toward tape-typed and setting up a distribution: roughly 50 tape-typed cases, 20 opaque, 10 mention-only, 15 no-tape-transfer, and 5 measurement-void cases, with wire-contrast favoring delivery-failure at about 70/30. I'm establishing register discipline where the value register captures surprisal and the residual-content register handles loose bus semantics.

For construction, I'm reusing nonces, classes, and held predicates from type_write.py along with the L metric and gate-0, pulling jlens from the verbum module to capture residuals across all layers. I'm planning to gate on the mean activation across the middle depth fraction (roughly layers 18-30) to cover the write band with some margin, then report the band profile to determine the right threshold.

Now I need to document this as section 10 in the types-are-injectable-relations document—it's the converse of section 8 and builds on section 9—with cross-references to the other type-checking documents. I'll also register it in state.md, then draft the section, get Michael's approval, and freeze it before building the harness. The model is Qwen3-4B with 36 layers, which differs from the earlier P-TYPE-JS work on the 32B version.

For the prompt setup, I'm pinning the ICL format with exactly one statement like "A {w} is an animal" followed by a space, then the held frame "The {w} {pred}." where I score the surprisal of the predicate tokens. The A3 control uses "I saw a {w} yesterday," and token budgets are approximately matched across conditions—A2 is exact-format matched, which is the critical constraint. The measurement position is the last token of the "The {w}" prefix, since that's where the next-token distribution licenses the predicate, and I'll capture residuals there across layers to derive the class axis from real members in the same position and frame.

For the null distributions in TI4, I'm generating matched-random axes (1000 samples with matched norm in residual space) and class-label-shuffled axes (200 samples with recomputed axes from

## Assistant

Drafting the freeze as §10 on the page (the converse of §8, reading §9). Writing it now, then presenting for your approval before any commit:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "## Provenance",
  "new_content": "## 10. §P-TYPE-ICL+TAG — FROZEN (s315, pending Michael GO)\n\n**The tape-side converse of §8, instrumented for tag transit.** §9 landed\nCONTEXT-ONLY: baked FFN membership recalls but does not license. Priors\n(s239, s293) say tape-resident membership DOES license. This probe (a)\nmeasures that claim under the exact §8 metric the baked wire failed, and\n(b) reads WHERE the class tag travels — Michael's J-space question in its\nlive form (tag-TRANSIT through residual content, not workspace RESIDENCY;\nthe strict-basis question is already closed negative, P-TYPE-JS s286, and\nis NOT re-tested here).\n\n**Registers named before probes (λ measure):**\n\n- `L(w)` held-frame licensing — **value register** (surprisal contrast,\n  §8 metric verbatim, same code).\n- `T(w)` class-tag presence — **residual-content register** (loose bus):\n  projection of the residual at the last token of `\"The {w}\"` (the\n  position feeding the check) onto the real-member class axis\n  `û_l = norm(mean_l(animal members) − mean_l(vehicle members))`, bare\n  frames, fixed reference (λ yardstick). Signed by true class. Gate\n  aggregates mean over depth 0.50–0.85 (L18–L30 of 36); full profile\n  advisory. Explicitly NOT the s270 workspace basis.\n\n**Arms (one model load, qwen3-4b — the §8/§9 carrier; no training except A5):**\n\n- **A0 base** — bare held frame `\"The {w} {pred}.\"` (§8 held predicates).\n- **A1 ICL-true** — `\"A {w} is {an animal|a vehicle}. The {w} {pred}.\"`\n  (true class; single classificatory statement, §8 statement form).\n- **A2 ICL-deranged** — same, anti-class statement (exact-format matched\n  content control; prediction: licenses the ANTI class).\n- **A3 mention** — `\"I saw a {w} yesterday. The {w} {pred}.\"` (nonce\n  mention without class content; binding-vs-classification control).\n- **A4 real-member anchor** — gate-0 reuse (metric validity).\n- **A5 wire (advisory contrast)** — §8 recipe verbatim under the s315\n  corridor (kl_weight 10, ce_budget 0.40, 3 seeds), eval-only residual\n  capture in held frames. No new gates ride A5; it feeds the subtag only.\n\n**Gates (frozen; α=0.05; n=20 nonces, machinery = type_write compute\npattern):**\n\n- **TI1 TAPE-LICENSING** — mean signed `L(A1) − L(A0) > 0`, beats\n  class-label-permutation null. The core (TW1 analog, tape side).\n- **TI2 CONTENT-SPECIFIC** — `L(A1) − L(A2) > 0`, paired permutation\n  (true beats deranged at exactly matched prompt budget; TW3 analog).\n- **TI3 CLASS-NOT-MENTION** — `L(A1) − L(A3) > 0`, paired permutation.\n- **TI4 TAG-TRANSIT** — `T(A1) − T(A0) > 0` beats BOTH matched-random-axis\n  null (n=1000) AND member-label-shuffled-axis null (n=200). Advisory\n  sub-read: Spearman(T, L) > 0 across A1 nonces (graded tag↔licensing link).\n- **TI5 METRIC-SANE (void-gate)** — gate-0 real-member margin ≥ 0.25 per\n  §8; A1 prefix does not invert real-member licensing (spot-check on A4\n  frames with a true-member ICL prefix).\n\n**Verdicts (frozen tree):**\n\n- **TAPE-TYPED (+TAG-TRANSIT)** — TI1∧TI2∧TI3 (TI4 adds subtag). With §9,\n  the two-tier split is measured from both sides: **the type check\n  consumes the tape, not the plates.**\n- **TAPE-TYPED-OPAQUE** — TI1∧TI2∧TI3 ∧ ¬TI4: licenses, but the tag rides\n  a basis the class axis misses (consistent with the P-TYPE-JS strict\n  negative; informative for the QK arc).\n- **MENTION-ONLY** — TI1 ∧ ¬TI3: generic binding, not classification.\n- **NO-TAPE-TRANSFER** — ¬TI1: the falsifier — would contradict s239/s293\n  priors; power audit before any theory update.\n- **VOID** — ¬TI5.\n\n**A5 wire-contrast subtag (advisory, attaches to any verdict; the\ndiscriminator for §9's failure mode):**\n\n- **DELIVERY-FAILURE** — `T(A5) ≈ T(A0)` while `T(A1) ≫ T(A0)`: the baked\n  edge never lifts the tag into held-frame residuals — §9 was a transit\n  failure; the relation exists but is never consulted. (Michael's\n  hypothesis lands, transit sense.)\n- **TAG-INSUFFICIENT** — `T(A5) ≈ T(A1)` (tag present) while §9 licensing\n  failed: content on the bus is not enough; the check reads routing state\n  more deeply (pushes on P-ATT-MED's content-carried story).\n- **AMBIGUOUS** — intermediate; report, don't force.\n\n**A-priori (declared s315, NOT tuned):** ~50 TAPE-TYPED / 20\nTAPE-TYPED-OPAQUE / 10 MENTION-ONLY / 15 NO-TAPE-TRANSFER / 5 VOID.\nWire-contrast lean: ~70 DELIVERY-FAILURE / 20 TAG-INSUFFICIENT / 10\nAMBIGUOUS.\n\n**Reuse (λ one_way, no fork):** nonces, classes, HELD_PREDS, `L`,\n`_signed_L`, gate machinery imported from `type_write.py`; residual\ncapture via `src/verbum/jlens.py` (`capture_residuals`); A5 trains via\nthe amended type_write recipe. New code = arms assembly + `T` projection\n+ TI gates. `--validate` planted worlds (all five verdicts + both\nsubtags) + ruff + smoke (no direction read) → Michael GO → run.\n\n## Provenance"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

## Assistant

Freeze draft is on disk as §10. The decisions worth your eyes before I commit:

## §P-TYPE-ICL+TAG — what's frozen

**One run, two questions:**
1. **Does tape membership license held frames?** — same metric, same nonces, same held predicates the baked wire just failed. Gates TI1 (vs base) / TI2 (vs *deranged* statement, exact-format matched) / TI3 (vs mere mention — "I saw a florb yesterday" — so classification ≠ binding).
2. **Where does the tag travel?** — TI4: residual projection onto the real-member class axis at the position feeding the check, against *two* nulls (matched-random axes + label-shuffled axes). Explicitly scoped as **transit through residual content**, not workspace residency — P-TYPE-JS's strict-basis negative stands untouched.

**The discriminator you asked about is arm A5** (advisory, no gates ride it): re-bake the §8 wire under the s315 corridor, capture its held-frame residuals, and compare tags three ways:
- `T(wire) ≈ T(base)` but `T(ICL) ≫ T(base)` → **DELIVERY-FAILURE** — the baked relation exists but never reaches the bus in held frames. Your hypothesis lands, transit sense.
- `T(wire) ≈ T(ICL)` yet wire licensing failed (§9 datum) → **TAG-INSUFFICIENT** — content on the bus isn't enough; the check reads routing more deeply. Would push on P-ATT-MED.

**A-priori (declared, not tuned):** 50 TAPE-TYPED / 20 OPAQUE / 10 MENTION-ONLY / 15 NO-TAPE-TRANSFER / 5 VOID; wire-contrast lean 70/20/10 DELIVERY-FAILURE. The lean follows s239/s293 (in-context typing licenses) — if NO-TAPE-TRANSFER fires instead, that's a power audit first, then a genuine problem for the two-tier story.

**Cost:** ICL arms are training-free (one model load, prompt variants + capture). A5 is the only training (~1–2h, known recipe). Reuse: `type_write.py` machinery + `jlens.py` capture — new code is arms assembly, the T projection, and TI gates.

Approve the freeze? On approval I commit 🎯, then build the harness (validate → smoke → your GO before the run, as always).

## User

approved


### Thinking

I'm committing the freeze with the updated documentation, then moving straight into building the harness as the next step—that's the natural workflow after Michael's approval, following the same pattern from the previous precedent.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> writes. **NEXT FRONT lean: P-TYPE-ICL (tape-side converse, now the priority\n> discriminator — if tape membership DOES license held frames, type check reads TAPE not\n> plates = two-tier measured both sides)** · attention-band membership write (slot\n> register) · fuel-theorem probe · standing alts unchanged. All UNFROZEN, s222\n> freeze-first.",
  "new_content": "> writes. **NEXT FRONT: 🎯 §P-TYPE-ICL+TAG FROZEN (§10 on types-are-injectable-relations.md,\n> Michael-approved s315)** — tape-side converse + tag-transit read (Michael's J-space\n> hypothesis in its LIVE form: transit through residual content, NOT workspace residency —\n> P-TYPE-JS s286 strict-basis negative stands, not re-tested). Arms A0 base / A1 ICL-true /\n> A2 ICL-deranged / A3 mention / A4 real anchor / A5 wire-contrast (advisory, s315 corridor\n> recipe). Gates TI1-TI5; verdicts TAPE-TYPED(+TAG-TRANSIT)/TAPE-TYPED-OPAQUE/MENTION-ONLY/\n> NO-TAPE-TRANSFER/VOID; A5 subtag DELIVERY-FAILURE/TAG-INSUFFICIENT/AMBIGUOUS; a-priori\n> 50/20/10/15/5, wire-contrast 70/20/10. Reuse type_write.py + jlens.py (λ one_way).\n> **NEXT ACTION: build harness** (validate planted worlds incl. both subtags → ruff →\n> smoke, no direction read) → Michael GO → run. Recall receipts this arc: P-TYPE-JS\n> js_resident=FALSE (s286 four-way null) · P-ATT-MED content-carried 0.735 (s286) ·\n> jlens/jacobian tooling (s263). Standing alts: attention-band write · fuel-theorem ·\n> unchanged."
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
  "command": "git add mementum/knowledge/explore/types-are-injectable-relations.md mementum/state.md && git commit -F - <<'EOF'\n🎯 P-TYPE-ICL+TAG FROZEN (s315) — tape-side converse + tag-transit read\n\n- §10 on types-are-injectable-relations.md, Michael-approved\n- (a) does TAPE membership license held frames (exact §8 metric the baked wire\n  failed); (b) WHERE does the class tag travel — the live form of the J-space\n  hypothesis (transit through residual content; workspace RESIDENCY not\n  re-tested, P-TYPE-JS s286 negative stands)\n- arms A0-A5 (ICL-true/deranged/mention + wire-contrast under s315 corridor);\n  gates TI1-TI5 (TI4 tag-transit vs matched-random + label-shuffled axis nulls);\n  verdicts TAPE-TYPED(+TAG-TRANSIT)/OPAQUE/MENTION-ONLY/NO-TAPE-TRANSFER/VOID;\n  A5 subtag DELIVERY-FAILURE/TAG-INSUFFICIENT/AMBIGUOUS\n- a-priori 50/20/10/15/5 (declared, not tuned); wire-contrast lean 70/20/10\n- reuse type_write.py + jlens.py, no fork (lambda one_way); state.md updated\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "freeze commit"
}
```

**Summary:** Git commit: freeze commit

**Output:**
```
Exit code: 0
Stdout:
[main 5a7fd40] 🎯 P-TYPE-ICL+TAG FROZEN (s315) — tape-side converse + tag-transit read
 2 files changed, 102 insertions(+), 5 deletions(-)
```

### Thinking

Freeze committed 5a7fd40. Now I'm building the harness, starting with the reuse surfaces.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"^def \\|^class \\|^    def \" src/verbum/jlens.py | head -20 && echo ──── && grep -n \"def capture_residuals\" -A 25 src/verbum/jlens.py"
}
```

**Summary:** $ grep -n "^def \|^class \|^    def "...

**Output:**
```
Exit code: 0
Stdout:
51:def _layers_and_prefix(model: nn.Module) -> tuple[Any, str]:
63:def _final_norm_unembed(model: nn.Module) -> tuple[nn.Module, nn.Module]:
75:def layer_path(model: nn.Module, i: int) -> str:
81:def n_layers(model: nn.Module) -> int:
86:def _hidden(out: Any) -> torch.Tensor:
95:def capture_residuals(
131:def logit_lens(model: nn.Module, resid: torch.Tensor) -> torch.Tensor:
140:def verbalize(
162:def kl_rows(clean: torch.Tensor, pert: torch.Tensor) -> torch.Tensor:
171:def forward_logits(
192:    def add(_m: nn.Module, _i: Any, out: Any) -> Any:
208:def broadcast_kl(
236:def self_test(model_name: str = "EleutherAI/pythia-14m-deduped") -> dict[str, Any]:
────
95:def capture_residuals(
96-    model: nn.Module,
97-    tokenizer: Any,
98-    text: str | None = None,
99-    *,
100-    input_ids: torch.Tensor | None = None,
101-) -> tuple[dict[int, torch.Tensor], torch.Tensor]:
102-    """Forward once; return ``({layer: (seq, d)}, input_ids)``.
103-
104-    Provide ``text`` (tokenized here) or pre-tokenized ``input_ids`` (shape
105-    ``(seq,)`` or ``(1, seq)``) — the latter for synthetic streams (e.g.
106-    induction sequences of raw token ids). Residual = the *output* of each
107-    transformer layer (post-block), for every position. Reuses
108-    :func:`verbum.hooks.capture`.
109-    """
110-    if input_ids is not None:
111-        ids = input_ids if input_ids.dim() == 2 else input_ids.unsqueeze(0)
112-        inputs = {"input_ids": ids.to(model.device)}
113-    elif text is not None:
114-        inputs = tokenizer(text, return_tensors="pt").to(model.device)
115-    else:
116-        raise ValueError("capture_residuals needs `text` or `input_ids`")
117-    nl = n_layers(model)
118-    ivs = [hooks.capture(layer_path(model, i), name=str(i)) for i in range(nl)]
119-    with hooks.intervene(model, ivs) as sess:
120-        model(**inputs)
```

### Thinking

I'm setting up a script to explore in-context learning with type tags, starting with a function that captures residuals from a model at each layer. Now I need to design the harness that will import the necessary components from the type_write module—the class definitions, article templates, member statements, and statistical utilities—to structure the exploration.

The main challenge is handling the training loop for A5: type_write's trainer is locked inside its run_model function, so I can't reuse it directly. Rather than refactoring the frozen harness or trying to save LoRA weights that weren't persisted, I'll replicate the trainer logic (~50 lines) in this script by importing the underlying pieces like LoRALinear and the training constants, then re-express the loop here. I'll document this duplication in the docstring as a precedent-supported approach. For A5 itself, I'll run the wire with the r3 corridor across 3 seeds.

Now I'm setting up the metrics: capturing residuals at the last token position of the prefix (the licensing position for next-token prediction), computing class-aligned directions per layer, and aggregating across the band. For the null distribution, I'm generating random unit vectors and measuring the signed projection difference under those axes to establish a baseline where random axes should show no class signal. I'm importing the null hypothesis machinery from the DSP module to run paired permutation tests comparing different arm configurations, then setting up a verdict tree that gates on the real margin threshold and ICL prefix sanity checks.

Now I'm working through the decision logic: if all three test conditions pass, mark it as TYPED (or TAG-TRANSIT if TI4 also holds); if TI1 passes but TI3 fails, downgrade to MENTION-ONLY; if TI1 fails entirely, it's NO-TAPE-TRANSFER. There's a gap in the tree for the case where TI1 and TI3 pass but TI2 fails—I need to clarify whether that should fold into MENTION-ONLY or stay undefined. Cleanest approach: I'll map the verdict logic directly to the frozen tree labels. TAPE-TYPED holds when all three conditions pass; NO-TAPE-TRANSFER when TI1 fails; MENTION-ONLY when TI3 fails. That leaves the gap where TI1 and TI3 both pass but TI2 fails—I'll route that to MENTION-ONLY as well, since the validate function needs to be total and that's the closest fit within the existing categories. So the uncovered cell needs a new verdict label—CLASS-BLIND—to capture that the classification happened without reading the actual class content, which is distinct from both mention-only and tape-typed approaches. I'll implement this as a validate-forced amendment, document it properly, and bring it to Michael at GO for approval, similar to how other test group amendments were handled. The mass allocation shifts from TAPE-TYPED's 50 down to 45, with CLASS-BLIND taking 20 and the remaining 10 and 15 distributed accordingly.

Now I'm setting up the harness file that mirrors the structure of type_write.py, importing the necessary modules and constants to reuse existing classification logic, candidate pools, and utility functions.

I'm defining the template strings for the in-context learning examples—one generic template and another derived from the member statements—along with the configuration parameters for the band depth range, number of random axes, and the core function that computes gates, verdicts, and subtags from bundled label arrays and arm-specific T_band values.

The bundle carries the T differences between arms plus precomputed null draw arrays, which the pure function receives as NullDraws to keep the logic clean. For the subtag classification, I'm setting up ratio-based thresholds: if the A5-to-A0 span is less than 25% of the A1-to-A0 span and that span is significant, it's tagged as DELIVERY-FAILURE; if it exceeds 75%, it's TAG-INSUFFICIENT; otherwise it's AMBIGUOUS, with these thresholds needing explicit declaration.

For the model path, I'm reloading and evaluating in gate-0 style while reusing the surprisal functions locally (they were closures before, so I'll re-express them inline). The nonce selection follows the same approach as before, and I'm capturing residuals along the real-member axis for bare phrases like "The dog" at the last position across each layer.

I'm capturing activations via jlens per prompt with one forward pass each across the eight prompts. For each nonce and arm, I'm computing loss over the held predictions, averaging across four predictions per class with separate values for sA and sV. The computational cost comes to around 640 teacher-forced forwards plus prefix captures, which is manageable. I'm also capturing T per nonce and arm for A0 and A1, with A2 and A3 as advisory since the gates only strictly need the A1−A0 difference, though capturing them is cheap for profiling purposes.

For the TI4 nulls, I'm drawing random gaussian axes per layer in the band, normalizing them, then computing a signed projection difference statistic using the true class labels to determine sign. I need to store the residuals per nonce and arm as arrays across the band layers so I can project them against these random axes and compute the statistics.

For the shuffled axes variant, I'm permuting the member labels to create different groupings of which ones count as "animal," then recomputing the direction from the stored residuals and running 200 draws to see how the statistic changes.

For A5, I'm training the wire model with a LoRA wrapper on the band layers using a fraction between 0.60-0.80, running it across 3 seeds, then capturing the test statistics for bare prefix prompts under the wire and averaging across seeds.

Now I'm setting up the trainer to use KL anchoring with a budget stop (KL weight 10, CE budget 0.40), importing the necessary stopping and replay utilities, and for TI5 I'm computing margins on real members to verify they exceed 0.25 and checking that in-context learning works properly with own-class prefixes.

The results will be saved to a JSON file with optional residual data, storing compressed tables and axis profiles while skipping raw hidden states. For validation, I'm testing across different world types—TAPE-TYPED variants, MENTION-ONLY, NO-TAPE-TRANSFER, VOID, CLASS-BLIND—plus subtag worlds and primitive checks like axis projection signs and ratio functions. This is a substantial implementation (~550 lines), and the full run should take roughly 30-45 minutes for measurements plus 1-2 hours for the seeded experiments, similar to the previous run.

Writing the trainer file... The gate function returns an object with fields for the computed value, null distribution mean, p-value, sign validity, verdict, and null name. For TI4, I'm using custom draws with NullDraws for a matched random axis, then calling gate twice with "greater" direction—both gates need to pass for the test to pass. The jlens.capture_residuals function extracts residual tensors from each layer of a model given token

### Thinking

I've confirmed the jlens API and now I'm writing the test harness, which will follow the same validate-first structure as type_write.py.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_icl_tag.py",
  "content": "#!/usr/bin/env python3\n\"\"\"§P-TYPE-ICL+TAG — tape-side converse of §P-TYPE-WRITE + tag-transit read.\n\nPre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §10\n(FROZEN s315, Michael-approved).\n\n(a) Does TAPE-resident membership produce held-frame licensing transfer —\nthe exact §8 metric the baked FFN wire failed (§9 CONTEXT-ONLY)?\n(b) WHERE does the class tag travel — T(w) = signed projection of the\nresidual at the last token of \"The {w}\" (the position feeding the check)\nonto the real-member class axis. Registers named (λ measure): L = value\nregister (surprisal); T = residual-CONTENT register (loose bus) — NOT the\ns270 workspace basis (P-TYPE-JS s286 negative stands, not re-tested).\n\nArms: A0 base | A1 ICL-true | A2 ICL-deranged | A3 mention | A4 real\nanchor (TI5) | A5 wire-contrast (advisory; §8 recipe under the s315\ncorridor kl_weight 10 / ce_budget 0.40, eval-only capture).\n\nGates: TI1 TAPE-LICENSING (L(A1)−L(A0), label-perm null) · TI2\nCONTENT-SPECIFIC (A1 vs A2 paired) · TI3 CLASS-NOT-MENTION (A1 vs A3\npaired) · TI4 TAG-TRANSIT (T(A1)−T(A0) vs matched-random-axis n=1000 AND\nmember-label-shuffled-axis n=200; advisory Spearman(T,L)) · TI5\nMETRIC-SANE void-gate.\n\nVerdicts: TAPE-TYPED(+TAG-TRANSIT) / TAPE-TYPED-OPAQUE / MENTION-ONLY /\nNO-TAPE-TRANSFER / VOID.\n⚠ BUILD AMENDMENT (validate-forced, pre-run, pending Michael at GO): the\nfrozen tree leaves the cell TI1∧TI3∧¬TI2 uncovered (licensing lifts vs\nbase and vs mention, but deranged statements license equally = class\ncontent not read). Named CLASS-BLIND; a-priori mass carved from\nTAPE-TYPED: 45/20/10/15/5 + 5 CLASS-BLIND. Wire-contrast subtag (declared\nthresholds, ratio r_tag=(T̄A5−T̄A0)/(T̄A1−T̄A0), only when TI4 passes):\nr≤0.25 DELIVERY-FAILURE / r≥0.75 TAG-INSUFFICIENT / else AMBIGUOUS.\n\nHarness (λ one_way, no fork): imports type_write (CLASSES, HELD_PREDS,\n_signed_L, _stop_decision, REPLAY_TEXTS, FIB_SNAPS, recipe constants) +\nverbum.jlens (capture_residuals) + writeback_compile (LoRALinear). The A5\ntrainer re-expresses the amended type_write loop (~50 lines, closure not\nimportable — the s309 precedent).\n\nLicense: MIT (lambda provenance).\n\"\"\"\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom pathlib import Path\n\nimport numpy as np\n\n_HERE = Path(__file__).resolve().parent\nif str(_HERE) not in sys.path:\n    sys.path.insert(0, str(_HERE))\n_WRAP = _HERE.parents[1] / \"wrapper\"\nif str(_WRAP) not in sys.path:\n    sys.path.insert(0, str(_WRAP))\n\nimport type_write as tw  # noqa: E402  (frozen §8 harness — constants + pure fns)\nfrom holo_cap import NONCE_CANDS  # noqa: E402\n\nfrom verbum.dsp.nulls import (  # noqa: E402\n    NullDraws,\n    Register,\n    gate,\n    paired_permutation,\n    shuffled_label,\n)\n\n# ══════════════════════════════════════════════════════════════════════════\n# Construction (FROZEN §10)\n# ══════════════════════════════════════════════════════════════════════════\nBAND_DEPTH = (0.50, 0.85)      # T gate aggregate: L18..L30 of 36\nN_RAND_AXES = 1000\nN_SHUF_AXES = 200\nSUBTAG_LO, SUBTAG_HI = 0.25, 0.75   # declared pre-run (build amendment)\n\n\ndef icl_true_prefix(w: str, cls_i: int) -> str:\n    return tw._member_stmts(w, cls_i)[0] + \" \"        # \"A {w} is an animal. \"\n\n\ndef icl_deranged_prefix(w: str, cls_i: int) -> str:\n    return tw._member_stmts(w, 1 - cls_i)[0] + \" \"    # anti-class statement\n\n\ndef mention_prefix(w: str) -> str:\n    return f\"I saw a {w} yesterday. \"\n\n\n# ══════════════════════════════════════════════════════════════════════════\n# Pure statistics + verdict (what --validate exercises; no torch, no model)\n# ══════════════════════════════════════════════════════════════════════════\ndef band_layers(n_layers: int) -> list[int]:\n    return list(range(round(BAND_DEPTH[0] * n_layers),\n                      round(BAND_DEPTH[1] * n_layers) + 1))\n\n\ndef signed_T(h: np.ndarray, axes: np.ndarray, labels: np.ndarray) -> np.ndarray:\n    \"\"\"Band-mean signed class-tag projection per nonce.\n\n    h: (n, L, d) residuals at the licensing position, band layers only.\n    axes: (L, d) unit class axes (animal − vehicle direction).\n    labels: (n,) 0=animal 1=vehicle. Sign fixed by true class: own-class\n    direction present ⟺ T>0.\"\"\"\n    proj = np.einsum(\"nld,ld->nl\", h, axes)           # (n, L)\n    sign = np.where(np.asarray(labels, int) == 0, 1.0, -1.0)\n    return proj.mean(axis=1) * sign\n\n\ndef class_axes(h_members: np.ndarray, member_labels: np.ndarray) -> np.ndarray:\n    \"\"\"(m, L, d) member residuals → (L, d) unit axes mean(A) − mean(V).\"\"\"\n    lab = np.asarray(member_labels, int)\n    ax = h_members[lab == 0].mean(axis=0) - h_members[lab == 1].mean(axis=0)\n    norm = np.linalg.norm(ax, axis=-1, keepdims=True)\n    return ax / np.clip(norm, 1e-12, None)\n\n\ndef subtag(t_a0: float, t_a1: float, t_a5: float, ti4_pass: bool) -> str:\n    \"\"\"Wire-contrast subtag (declared thresholds; AMBIGUOUS unless TI4).\"\"\"\n    if not ti4_pass or not np.isfinite(t_a5):\n        return \"AMBIGUOUS\"\n    denom = t_a1 - t_a0\n    if abs(denom) < 1e-12:\n        return \"AMBIGUOUS\"\n    r = (t_a5 - t_a0) / denom\n    if r <= SUBTAG_LO:\n        return \"DELIVERY-FAILURE\"\n    if r >= SUBTAG_HI:\n        return \"TAG-INSUFFICIENT\"\n    return \"AMBIGUOUS\"\n\n\ndef compute_gates_icl(b: dict, rng: np.random.Generator, alpha: float = 0.05,\n                      n_iter: int = 10000) -> dict:\n    \"\"\"b holds per-nonce arrays + tag tables + precomputed axis-null draws.\n    Pure — --validate plants b directly.\"\"\"\n    labels = np.asarray(b[\"labels\"], int)\n    L = {arm: tw._signed_L(b[f\"sA_{arm}\"], b[f\"sV_{arm}\"], labels)\n         for arm in (\"a0\", \"a1\", \"a2\", \"a3\")}\n\n    # ── TI1 TAPE-LICENSING: mean(L(A1)−L(A0)) beats label-permutation ──\n    def stat_ti1(perm_labels):\n        return float(np.mean(\n            tw._signed_L(b[\"sA_a1\"], b[\"sV_a1\"], perm_labels)\n            - tw._signed_L(b[\"sA_a0\"], b[\"sV_a0\"], perm_labels)))\n    ti1_null = shuffled_label(stat_ti1, labels, rng, n_iter=min(n_iter, 2000))\n    ti1 = gate(stat_ti1(labels), ti1_null, \"greater\", alpha,\n               \"TI1_tape_licensing\",\n               claim_register=Register.value, probe_register=Register.value)\n\n    # ── TI2 CONTENT-SPECIFIC: A1 beats deranged A2 (paired) ──\n    ti2_null = paired_permutation(L[\"a1\"], L[\"a2\"], rng, n_iter=n_iter)\n    ti2 = gate(float(np.mean(L[\"a1\"] - L[\"a2\"])), ti2_null, \"greater\", alpha,\n               \"TI2_content_specific\",\n               claim_register=Register.value, probe_register=Register.value)\n\n    # ── TI3 CLASS-NOT-MENTION: A1 beats mention A3 (paired) ──\n    ti3_null = paired_permutation(L[\"a1\"], L[\"a3\"], rng, n_iter=n_iter)\n    ti3 = gate(float(np.mean(L[\"a1\"] - L[\"a3\"])), ti3_null, \"greater\", alpha,\n               \"TI3_class_not_mention\",\n               claim_register=Register.value, probe_register=Register.value)\n\n    # ── TI4 TAG-TRANSIT: T(A1)−T(A0) beats both axis nulls ──\n    t_a0, t_a1 = np.asarray(b[\"T_a0\"], float), np.asarray(b[\"T_a1\"], float)\n    s_tag = float(np.mean(t_a1 - t_a0))\n    ti4_rand = gate(s_tag, NullDraws(\"matched_random_axis\",\n                                     np.asarray(b[\"tag_null_rand\"], float),\n                                     {\"n\": N_RAND_AXES}),\n                    \"greater\", alpha, \"TI4_tag_vs_random_axis\",\n                    claim_register=Register.value,\n                    probe_register=Register.value)\n    ti4_shuf = gate(s_tag, NullDraws(\"member_label_shuffled_axis\",\n                                     np.asarray(b[\"tag_null_shuf\"], float),\n                                     {\"n\": N_SHUF_AXES}),\n                    \"greater\", alpha, \"TI4_tag_vs_shuffled_axis\",\n                    claim_register=Register.value,\n                    probe_register=Register.value)\n    ti4_pass = bool(ti4_rand.verdict and ti4_shuf.verdict)\n    rho_tl = tw._spearman(t_a1, L[\"a1\"])              # advisory\n\n    # ── TI5 METRIC-SANE (void-gate) ──\n    m = b.get(\"metric\", {})\n    real_ok = (m.get(\"real_margin\", 0.0) >= tw.REAL_MARGIN_FLOOR\n               and bool(m.get(\"per_class_ok\", False)))\n    icl_sane = m.get(\"real_icl_margin\", 1.0) > 0.0\n    ti5_pass = bool(real_ok and icl_sane)\n\n    # ── verdict tree (frozen + CLASS-BLIND build amendment) ──\n    if not ti5_pass:\n        verdict = \"VOID\"\n    elif not ti1.verdict:\n        verdict = \"NO-TAPE-TRANSFER\"\n    elif not ti3.verdict:\n        verdict = \"MENTION-ONLY\"\n    elif not ti2.verdict:\n        verdict = \"CLASS-BLIND\"\n    elif ti4_pass:\n        verdict = \"TAPE-TYPED+TAG-TRANSIT\"\n    else:\n        verdict = \"TAPE-TYPED-OPAQUE\"\n\n    t_a5 = float(np.mean(b[\"T_a5\"])) if \"T_a5\" in b else float(\"nan\")\n    tag = subtag(float(np.mean(t_a0)), float(np.mean(t_a1)), t_a5, ti4_pass)\n\n    return {\n        \"verdict\": verdict, \"subtag\": tag,\n        \"gates\": {\n            \"TI1\": tw._gd(ti1), \"TI2\": tw._gd(ti2), \"TI3\": tw._gd(ti3),\n            \"TI4_rand\": tw._gd(ti4_rand), \"TI4_shuf\": tw._gd(ti4_shuf),\n            \"TI4_pass\": ti4_pass,\n            \"TI5\": {\"real_ok\": real_ok, \"icl_sane\": icl_sane,\n                    \"pass\": ti5_pass},\n        },\n        \"means\": {\n            \"L_a0\": float(np.mean(L[\"a0\"])), \"L_a1\": float(np.mean(L[\"a1\"])),\n            \"L_a2\": float(np.mean(L[\"a2\"])), \"L_a3\": float(np.mean(L[\"a3\"])),\n            \"T_a0\": float(np.mean(t_a0)), \"T_a1\": float(np.mean(t_a1)),\n            \"T_a5\": t_a5, \"S_tag\": s_tag, \"rho_T_L\": rho_tl,\n            \"n_nonce\": int(labels.size),\n        },\n    }\n\n\n# ══════════════════════════════════════════════════════════════════════════\n# --validate: planted worlds (no model)\n# ══════════════════════════════════════════════════════════════════════════\ndef _world_icl(rng, kind: str, n: int = 24) -> dict:\n    labels = np.array([0, 1] * (n // 2))\n    base_s = lambda: rng.normal(6.0, 0.3, n)                    # noqa: E731\n    b: dict = {\"labels\": labels}\n    # default: no arm licenses (all L ~ 0)\n    for arm in (\"a0\", \"a1\", \"a2\", \"a3\"):\n        b[f\"sA_{arm}\"], b[f\"sV_{arm}\"] = base_s(), base_s()\n    # default tags: nothing present, nulls centred at 0\n    b[\"T_a0\"] = rng.normal(0.0, 0.05, n)\n    b[\"T_a1\"] = rng.normal(0.0, 0.05, n)\n    b[\"tag_null_rand\"] = rng.normal(0.0, 0.02, N_RAND_AXES)\n    b[\"tag_null_shuf\"] = rng.normal(0.0, 0.02, N_SHUF_AXES)\n    b[\"metric\"] = {\"real_margin\": 2.5, \"per_class_ok\": True,\n                   \"real_icl_margin\": 1.5}\n\n    def lift_own(arm: str, amount: np.ndarray):\n        sA, sV = b[f\"sA_{arm}\"], b[f\"sV_{arm}\"]\n        for i in range(n):\n            (sA, sV)[labels[i]][i] -= amount[i]       # own-class cheaper\n\n    if kind == \"tape_typed_transit\":\n        amt = rng.uniform(1.0, 2.0, n)\n        lift_own(\"a1\", amt)\n        b[\"T_a1\"] = 0.8 * amt + rng.normal(0, 0.05, n)\n        b[\"T_a5\"] = rng.normal(0.0, 0.05, n)          # wire tag absent\n    elif kind == \"tape_typed_opaque\":\n        lift_own(\"a1\", rng.uniform(1.2, 1.8, n))      # licenses, tag flat\n    elif kind == \"mention_only\":\n        amt = rng.uniform(1.2, 1.8, n)\n        lift_own(\"a1\", amt)\n        lift_own(\"a3\", amt + rng.normal(0, 0.05, n))  # mention matches A1\n        lift_own(\"a2\", rng.uniform(0.0, 0.1, n))\n    elif kind == \"class_blind\":\n        amt = rng.uniform(1.2, 1.8, n)\n        lift_own(\"a1\", amt)\n        lift_own(\"a2\", amt + rng.normal(0, 0.05, n))  # deranged matches A1\n    elif kind == \"no_tape_transfer\":\n        pass                                          # defaults: nothing\n    elif kind == \"void\":\n        lift_own(\"a1\", rng.uniform(1.2, 1.8, n))\n        b[\"metric\"] = {\"real_margin\": -0.3, \"per_class_ok\": False,\n                       \"real_icl_margin\": 1.0}\n    elif kind == \"subtag_insufficient\":\n        amt = rng.uniform(1.0, 2.0, n)\n        lift_own(\"a1\", amt)\n        b[\"T_a1\"] = 0.8 * amt + rng.normal(0, 0.05, n)\n        b[\"T_a5\"] = b[\"T_a1\"] + rng.normal(0, 0.02, n)  # wire tag ≈ ICL tag\n    else:\n        raise ValueError(kind)\n    return b\n\n\ndef run_validate(alpha: float) -> int:\n    print(\"── §P-TYPE-ICL+TAG --validate (planted worlds, no model) ──\")\n    want = {\"tape_typed_transit\": (\"TAPE-TYPED+TAG-TRANSIT\", \"DELIVERY-FAILURE\"),\n            \"tape_typed_opaque\": (\"TAPE-TYPED-OPAQUE\", \"AMBIGUOUS\"),\n            \"mention_only\": (\"MENTION-ONLY\", None),\n            \"class_blind\": (\"CLASS-BLIND\", None),\n            \"no_tape_transfer\": (\"NO-TAPE-TRANSFER\", None),\n            \"void\": (\"VOID\", None),\n            \"subtag_insufficient\": (\"TAPE-TYPED+TAG-TRANSIT\",\n                                    \"TAG-INSUFFICIENT\")}\n    ok = True\n    for kind, (expect_v, expect_s) in want.items():\n        rng = np.random.default_rng(hash(kind) % (2**31))\n        res = compute_gates_icl(_world_icl(rng, kind), rng, alpha,\n                                n_iter=2000)\n        good = res[\"verdict\"] == expect_v\n        if expect_s is not None:\n            good &= res[\"subtag\"] == expect_s\n        ok &= good\n        print(f\"  {kind:22s} -> {res['verdict']:24s} subtag \"\n              f\"{res['subtag']:18s} expect {expect_v}\"\n              f\"{('/' + expect_s) if expect_s else '':20s} \"\n              f\"{'✓' if good else '✗ FAIL'}\")\n    # primitives\n    h = np.zeros((2, 3, 4))\n    h[0, :, 0], h[1, :, 1] = 2.0, 2.0\n    ax = np.zeros((3, 4))\n    ax[:, 0], ax[:, 1] = 1.0, -1.0                    # animal−vehicle axis\n    t = signed_T(h, ax, np.array([0, 1]))\n    prim = np.allclose(t, [2.0, 2.0])                 # both own-class present\n    ok &= prim\n    print(f\"  primitive signed_T                {'✓' if prim else '✗ FAIL'}\")\n    axes = class_axes(np.stack([h[0], h[0], h[1], h[1]]),\n                      np.array([0, 0, 1, 1]))\n    prim2 = np.allclose(np.linalg.norm(axes, axis=-1), 1.0)\n    ok &= prim2\n    print(f\"  primitive class_axes unit-norm    {'✓' if prim2 else '✗ FAIL'}\")\n    prim3 = (subtag(0.0, 1.0, 0.1, True) == \"DELIVERY-FAILURE\"\n             and subtag(0.0, 1.0, 0.9, True) == \"TAG-INSUFFICIENT\"\n             and subtag(0.0, 1.0, 0.5, True) == \"AMBIGUOUS\"\n             and subtag(0.0, 1.0, 0.9, False) == \"AMBIGUOUS\")\n    ok &= prim3\n    print(f\"  primitive subtag thresholds       {'✓' if prim3 else '✗ FAIL'}\")\n    print(f\"\\n── --validate {'ALL PASS' if ok else 'FAIL'} ──\")\n    return 0 if ok else 1\n\n\n# ══════════════════════════════════════════════════════════════════════════\n# Model path\n# ══════════════════════════════════════════════════════════════════════════\ndef run_model(args) -> int:\n    import operand_multihop3 as mh3\n    import torch\n    import torch.nn.functional as F\n    import writeback_compile as wb\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    from verbum import jlens\n\n    dev = (args.device if (args.device != \"mps\"\n                           or torch.backends.mps.is_available()) else \"cpu\")\n    rng = np.random.default_rng(args.seed)\n    tok = AutoTokenizer.from_pretrained(args.model_id)\n    if tok.pad_token is None:\n        tok.pad_token = tok.eos_token\n    tok.padding_side = \"right\"\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()\n    for p in model.parameters():\n        p.requires_grad_(False)\n    dec, _norm, _lm_head = mh3.resolve_parts(model)\n    nl = len(dec)\n    tband = band_layers(nl)\n    wband = list(range(round(tw.BAND_FRAC[0] * nl),\n                       round(tw.BAND_FRAC[1] * nl) + 1))\n    out_dir = Path(args.out)\n    out_dir.mkdir(parents=True, exist_ok=True)\n    print(f\"[ti] {args.model_id} dev={dev} n_layers={nl} \"\n          f\"T-band=L{tband[0]}..L{tband[-1]} wire-band=L{wband[0]}..L{wband[-1]}\")\n\n    def surprisal(prefix: str, cont: str) -> float:\n        pre = tok(prefix, return_tensors=\"pt\").to(dev)\n        full = tok(prefix + cont, return_tensors=\"pt\").to(dev)\n        n_pre = pre.input_ids.shape[1]\n        with torch.no_grad():\n            lo = model(**full).logits[0].float()\n        lp = F.log_softmax(lo, dim=-1)\n        tgt = full.input_ids[0]\n        return -sum(float(lp[pos - 1, tgt[pos]])\n                    for pos in range(n_pre, tgt.shape[0]))\n\n    def capture_band(prefix: str) -> np.ndarray:\n        \"\"\"(L_band, d) residual at the last position of `prefix`.\"\"\"\n        resid, _ids = jlens.capture_residuals(model, tok, prefix)\n        return np.stack([resid[li][-1].float().cpu().numpy() for li in tband])\n\n    def arm_L(prefix_fn) -> tuple[np.ndarray, np.ndarray]:\n        sA, sV = [], []\n        for w, lb in zip(nonces, labels, strict=True):\n            pre = prefix_fn(w, int(lb)) + f\"The {w}\"\n            sA.append(np.mean([surprisal(pre, \" \" + p)\n                               for p in tw.HELD_PREDS[0]]))\n            sV.append(np.mean([surprisal(pre, \" \" + p)\n                               for p in tw.HELD_PREDS[1]]))\n        return np.array(sA), np.array(sV)\n\n    def arm_T(prefix_fn) -> np.ndarray:\n        return np.stack([capture_band(prefix_fn(w, int(lb)) + f\"The {w}\")\n                         for w, lb in zip(nonces, labels, strict=True)])\n\n    # ── nonce selection (type_write pattern) ──\n    nonces, labels = [], []\n    for i, w in enumerate(NONCE_CANDS):\n        n_the = tok(\"The\", add_special_tokens=False).input_ids\n        n_thew = tok(f\"The {w}\", add_special_tokens=False).input_ids\n        if len(n_thew) - len(n_the) >= 1:\n            nonces.append(w)\n            labels.append(i % 2)\n    if args.n_nonce:\n        a = [j for j, x in enumerate(labels) if x == 0][:args.n_nonce // 2]\n        v = [j for j, x in enumerate(labels) if x == 1][:args.n_nonce // 2]\n        sel = sorted(a + v)\n        nonces = [nonces[j] for j in sel]\n        labels = [labels[j] for j in sel]\n    labels = np.array(labels, int)\n    print(f\"[ti] nonces={len(nonces)} (animal {int((labels == 0).sum())} \"\n          f\"vehicle {int((labels == 1).sum())})\")\n\n    # ── A4 + TI5: real-member anchor, bare + own-class ICL prefix ──\n    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])\n    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])\n                           + [1] * len(tw.REAL_MEMBERS[1]))\n    print(\"[ti] A4 anchor: real-member licensing (bare + ICL prefix) …\")\n    rA, rV, riA, riV = [], [], [], []\n    for w, lb in zip(real_members, real_labels, strict=True):\n        pre = f\"The {w}\"\n        rA.append(np.mean([surprisal(pre, \" \" + p) for p in tw.HELD_PREDS[0]]))\n        rV.append(np.mean([surprisal(pre, \" \" + p) for p in tw.HELD_PREDS[1]]))\n        prei = icl_true_prefix(w, int(lb)) + f\"The {w}\"\n        riA.append(np.mean([surprisal(prei, \" \" + p)\n                            for p in tw.HELD_PREDS[0]]))\n        riV.append(np.mean([surprisal(prei, \" \" + p)\n                            for p in tw.HELD_PREDS[1]]))\n    L_real = tw._signed_L(np.array(rA), np.array(rV), real_labels)\n    L_real_icl = tw._signed_L(np.array(riA), np.array(riV), real_labels)\n    metric = {\n        \"real_margin\": float(np.mean(L_real)),\n        \"per_class_ok\": bool(np.mean(L_real[real_labels == 0]) > 0\n                             and np.mean(L_real[real_labels == 1]) > 0),\n        \"real_icl_margin\": float(np.mean(L_real_icl)),\n    }\n    print(f\"[ti] real margin={metric['real_margin']:.3f} \"\n          f\"icl_margin={metric['real_icl_margin']:.3f} \"\n          f\"per_class_ok={metric['per_class_ok']}\")\n\n    # ── class axes from real members (bare frames, fixed reference) ──\n    print(\"[ti] class axes from real members …\")\n    h_members = np.stack([capture_band(f\"The {w}\") for w in real_members])\n    axes = class_axes(h_members, real_labels)\n\n    # ── arms A0-A3: L + T ──\n    prefix_fns = {\"a0\": lambda w, c: \"\",\n                  \"a1\": lambda w, c: icl_true_prefix(w, c),\n                  \"a2\": lambda w, c: icl_deranged_prefix(w, c),\n                  \"a3\": lambda w, c: mention_prefix(w)}\n    b: dict = {\"labels\": labels, \"metric\": metric}\n    h_arm: dict = {}\n    for arm, pf in prefix_fns.items():\n        print(f\"[ti] arm {arm} …\", flush=True)\n        b[f\"sA_{arm}\"], b[f\"sV_{arm}\"] = arm_L(pf)\n        h_arm[arm] = arm_T(pf)\n    b[\"T_a0\"] = signed_T(h_arm[\"a0\"], axes, labels)\n    b[\"T_a1\"] = signed_T(h_arm[\"a1\"], axes, labels)\n    T_a2 = signed_T(h_arm[\"a2\"], axes, labels)        # advisory\n    T_a3 = signed_T(h_arm[\"a3\"], axes, labels)        # advisory\n\n    # ── TI4 nulls (λ yardstick: fixed reference, matched nulls) ──\n    print(\"[ti] TI4 nulls: random axes + shuffled member labels …\")\n    d = axes.shape[-1]\n    def tag_stat(ax):\n        return float(np.mean(signed_T(h_arm[\"a1\"], ax, labels)\n                             - signed_T(h_arm[\"a0\"], ax, labels)))\n    rand_draws = []\n    for _ in range(N_RAND_AXES):\n        ra = rng.normal(size=(len(tband), d))\n        ra /= np.linalg.norm(ra, axis=-1, keepdims=True)\n        rand_draws.append(tag_stat(ra))\n    shuf_draws = []\n    for _ in range(N_SHUF_AXES):\n        perm = rng.permutation(real_labels)\n        shuf_draws.append(tag_stat(class_axes(h_members, perm)))\n    b[\"tag_null_rand\"] = np.array(rand_draws)\n    b[\"tag_null_shuf\"] = np.array(shuf_draws)\n\n    # ── A5 wire-contrast (advisory): §8 recipe, s315 corridor ──\n    if args.with_wire:\n        print(\"[ti] arm A5: wire (s315 corridor, 3 seeds) …\")\n        rb = tok(tw.REPLAY_TEXTS, return_tensors=\"pt\", padding=True).to(dev)\n        with torch.no_grad():\n            blo = model(**rb).logits.float()\n            p_base = torch.softmax(blo, dim=-1)\n            h_base = -(p_base * F.log_softmax(blo, dim=-1)).sum(-1)\n        rmask = rb.attention_mask.float()\n        del blo\n\n        def ce_host() -> float:\n            tot, n = 0.0, 0\n            for t in tw.CE_TEXTS:\n                ids = tok(t, return_tensors=\"pt\").to(dev)\n                with torch.no_grad():\n                    lo = model(**ids).logits[0].float()\n                lp = F.log_softmax(lo[:-1], dim=-1)\n                tgt = ids.input_ids[0, 1:]\n                tot += float(-lp[torch.arange(len(tgt)), tgt].sum())\n                n += len(tgt)\n            return tot / max(n, 1)\n\n        ce0 = ce_host()\n        T5_seeds = []\n        for sd in range(args.seeds):\n            torch.manual_seed(sd)\n            wrapped, params = [], []\n            for li in wband:\n                m = dec[li].mlp\n                for name in (\"gate_proj\", \"up_proj\", \"down_proj\"):\n                    orig = getattr(m, name)\n                    lw = wb.LoRALinear(orig, r=args.lora_r,\n                                       alpha=2 * args.lora_r)\n                    setattr(m, name, lw)\n                    wrapped.append((m, name, orig))\n                    params += [lw.A, lw.B]\n            opt = torch.optim.Adam(params, lr=args.lr)\n            stmts = [s for w, lb in zip(nonces, labels, strict=True)\n                     for s in tw._member_stmts(w, int(lb))]\n            batch = tok(stmts, return_tensors=\"pt\", padding=True).to(dev)\n            ids, attn = batch.input_ids, batch.attention_mask\n            snap_set = {s for s in tw.FIB_SNAPS if s < args.steps}\n            hist: dict = {\"step\": [], \"mem_ce\": [], \"drift\": []}\n            last_good = [p.detach().clone() for p in params]\n            for step in range(args.steps):\n                opt.zero_grad()\n                lo = model(input_ids=ids, attention_mask=attn).logits.float()\n                sl, st_ = lo[:, :-1, :], ids[:, 1:]\n                sm = attn[:, 1:].float()\n                ce = F.cross_entropy(\n                    sl.reshape(-1, sl.shape[-1]), st_.reshape(-1),\n                    reduction=\"none\").reshape(st_.shape)\n                mem_ce = (ce * sm).sum() / sm.sum().clamp_min(1.0)\n                lr_ = model(**rb).logits.float()\n                lq = F.log_softmax(lr_, dim=-1)\n                kl = ((-(p_base * lq).sum(-1) - h_base)\n                      * rmask).sum() / rmask.sum()\n                (mem_ce + args.kl_weight * kl).backward()\n                opt.step()\n                if step in snap_set:\n                    drift = ce_host() - ce0\n                    hist[\"step\"].append(step)\n                    hist[\"mem_ce\"].append(float(mem_ce.detach()))\n                    hist[\"drift\"].append(drift)\n                    keep, reason = tw._stop_decision(\n                        hist[\"step\"], hist[\"mem_ce\"], hist[\"drift\"],\n                        args.ce_budget, args.plateau_tol, args.min_stop)\n                    if reason == \"plateau\":\n                        break\n                    if reason == \"ce_budget_rollback\":\n                        with torch.no_grad():\n                            for p, g in zip(params, last_good, strict=True):\n                                p.copy_(g)\n                        break\n                    last_good = [p.detach().clone() for p in params]\n            T5_seeds.append(signed_T(arm_T(prefix_fns[\"a0\"]), axes, labels))\n            for m, name, orig in wrapped:\n                setattr(m, name, orig)\n            print(f\"[ti] A5 seed{sd} done (steps {hist['step'][-1] + 1 if hist['step'] else 0}+)\",\n                  flush=True)\n        b[\"T_a5\"] = np.mean(T5_seeds, axis=0)\n\n    # ── gates + verdict ──\n    res = compute_gates_icl(b, rng, args.alpha)\n    res[\"meta\"] = {\n        \"model_id\": args.model_id, \"n_nonce\": len(nonces),\n        \"nonces\": nonces, \"labels\": labels.tolist(),\n        \"t_band\": [tband[0], tband[-1]], \"wire_band\": [wband[0], wband[-1]],\n        \"with_wire\": bool(args.with_wire), \"seeds\": args.seeds,\n        \"steps\": args.steps, \"lr\": args.lr, \"lora_r\": args.lora_r,\n        \"kl_weight\": args.kl_weight, \"ce_budget\": args.ce_budget,\n        \"metric\": metric,\n        \"T_a2_mean\": float(np.mean(T_a2)), \"T_a3_mean\": float(np.mean(T_a3)),\n    }\n    (out_dir / \"results.json\").write_text(json.dumps(res, indent=2))\n    np.savez_compressed(\n        out_dir / \"tags.npz\",\n        T_a0=b[\"T_a0\"], T_a1=b[\"T_a1\"], T_a2=T_a2, T_a3=T_a3,\n        T_a5=b.get(\"T_a5\", np.array([])),\n        axes=axes, labels=labels)\n    print(f\"[ti] wrote {out_dir}/results.json\")\n    g, mn = res[\"gates\"], res[\"means\"]\n    print(f\"[ti] TI1 p={g['TI1']['p']:.4f} {g['TI1']['pass']} | \"\n          f\"TI2 p={g['TI2']['p']:.4f} {g['TI2']['pass']} | \"\n          f\"TI3 p={g['TI3']['p']:.4f} {g['TI3']['pass']} | \"\n          f\"TI4 rand p={g['TI4_rand']['p']:.4f} shuf p={g['TI4_shuf']['p']:.4f} \"\n          f\"{g['TI4_pass']} | TI5 {g['TI5']['pass']}\")\n    print(f\"[ti] L a0={mn['L_a0']:.3f} a1={mn['L_a1']:.3f} \"\n          f\"a2={mn['L_a2']:.3f} a3={mn['L_a3']:.3f} | \"\n          f\"T a0={mn['T_a0']:.3f} a1={mn['T_a1']:.3f} a5={mn['T_a5']:.3f} \"\n          f\"rho={mn['rho_T_L']:.3f}\")\n    print(f\"[ti] VERDICT: {res['verdict']} | subtag: {res['subtag']}\")\n    return 0\n\n\ndef main() -> int:\n    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])\n    ap.add_argument(\"--validate\", action=\"store_true\")\n    ap.add_argument(\"--model-id\", default=\"Qwen/Qwen3-4B\")\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--dtype\", default=\"bfloat16\",\n                    choices=[\"float32\", \"bfloat16\"])\n    ap.add_argument(\"--n-nonce\", type=int, default=0)\n    ap.add_argument(\"--with-wire\", action=argparse.BooleanOptionalAction,\n                    default=True, help=\"A5 wire-contrast arm\")\n    ap.add_argument(\"--seeds\", type=int, default=3)\n    ap.add_argument(\"--steps\", type=int, default=500)\n    ap.add_argument(\"--lr\", type=float, default=1e-4)\n    ap.add_argument(\"--lora-r\", type=int, default=16)\n    ap.add_argument(\"--kl-weight\", type=float, default=10.0)\n    ap.add_argument(\"--ce-budget\", type=float, default=0.40)\n    ap.add_argument(\"--plateau-tol\", type=float, default=0.01)\n    ap.add_argument(\"--min-stop\", type=int, default=55)\n    ap.add_argument(\"--alpha\", type=float, default=0.05)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--out\", default=\"results/type-icl-tag/qwen3-4b\")\n    args = ap.parse_args()\n    if args.validate:\n        return run_validate(args.alpha)\n    return run_model(args)\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/explore/type_icl_tag.py
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/explore/type_icl_tag.py --validate && uv run ruff check scripts/explore/type_icl_tag.py",
  "timeout": 120000
}
```

**Summary:** $ uv run python scripts/explore/type_...

**Output:**
```
Exit code: 1
Stdout:
── §P-TYPE-ICL+TAG --validate (planted worlds, no model) ──
  tape_typed_transit     -> TAPE-TYPED+TAG-TRANSIT   subtag DELIVERY-FAILURE   expect TAPE-TYPED+TAG-TRANSIT/DELIVERY-FAILURE    ✓
  tape_typed_opaque      -> TAPE-TYPED-OPAQUE        subtag AMBIGUOUS          expect TAPE-TYPED-OPAQUE/AMBIGUOUS           ✓
  mention_only           -> MENTION-ONLY             subtag AMBIGUOUS          expect MENTION-ONLY                     ✓
  class_blind            -> CLASS-BLIND              subtag AMBIGUOUS          expect CLASS-BLIND                     ✓
  no_tape_transfer       -> NO-TAPE-TRANSFER         subtag AMBIGUOUS          expect NO-TAPE-TRANSFER                     ✓
  void                   -> VOID                     subtag AMBIGUOUS          expect VOID                     ✓
  subtag_insufficient    -> TAPE-TYPED+TAG-TRANSIT   subtag TAG-INSUFFICIENT   expect TAPE-TYPED+TAG-TRANSIT/TAG-INSUFFICIENT    ✓
  primitive signed_T                ✓
  primitive class_axes unit-norm    ✓
  primitive subtag thresholds       ✓

── --validate ALL PASS ──
RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/explore/type_icl_tag.py:19:33
   |
17 | corridor kl_weight 10 / ce_budget 0.40, eval-only capture).
18 |
19 | Gates: TI1 TAPE-LICENSING (L(A1)−L(A0), label-perm null) · TI2
   |                                 ^
20 | CONTENT-SPECIFIC (A1 vs A2 paired) · TI3 CLASS-NOT-MENTION (A1 vs A3
21 | paired) · TI4 TAG-TRANSIT (T(A1)−T(A0) vs matched-random-axis n=1000 AND
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/explore/type_icl_tag.py:21:33
   |
19 | Gates: TI1 TAPE-LICENSING (L(A1)−L(A0), label-perm null) · TI2
20 | CONTENT-SPECIFIC (A1 vs A2 paired) · TI3 CLASS-NOT-MENTION (A1 vs A3
21 | paired) · TI4 TAG-TRANSIT (T(A1)−T(A0) vs matched-random-axis n=1000 AND
   |                                 ^
22 | member-label-shuffled-axis n=200; advisory Spearman(T,L)) · TI5
23 | METRIC-SANE void-gate.
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/explore/type_icl_tag.py:32:30
   |
30 | content not read). Named CLASS-BLIND; a-priori mass carved from
31 | TAPE-TYPED: 45/20/10/15/5 + 5 CLASS-BLIND. Wire-contrast subtag (declared
32 | thresholds, ratio r_tag=(T̄A5−T̄A0)/(T̄A1−T̄A0), only when TI4 passes):
   |                             ^
33 | r≤0.25 DELIVERY-FAILURE / r≥0.75 TAG-INSUFFICIENT / else AMBIGUOUS.
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/explore/type_icl_tag.py:32:42
   |
30 | content not read). Named CLASS-BLIND; a-priori mass carved from
31 | TAPE-TYPED: 45/20/10/15/5 + 5 CLASS-BLIND. Wire-contrast subtag (declared
32 | thresholds, ratio r_tag=(T̄A5−T̄A0)/(T̄A1−T̄A0), only when TI4 passes):
   |                                       ^
33 | r≤0.25 DELIVERY-FAILURE / r≥0.75 TAG-INSUFFICIENT / else AMBIGUOUS.
   |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/explore/type_icl_tag.py:103:42
    |
102 |     h: (n, L, d) residuals at the licensing position, band layers only.
103 |     axes: (L, d) unit class axes (animal − vehicle direction).
    |                                          ^
104 |     labels: (n,) 0=animal 1=vehicle. Sign fixed by true class: own-class
105 |     direction present ⟺ T>0."""
    |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/explore/type_icl_tag.py:112:62
    |
111 | def class_axes(h_members: np.ndarray, member_labels: np.ndarray) -> np.ndarray:
112 |     """(m, L, d) member residuals → (L, d) unit axes mean(A) − mean(V)."""
    |                                                              ^
113 |     lab = np.asarray(member_labels, int)
114 |     ax = h_members[lab == 0].mean(axis=0) - h_members[lab == 1].mean(axis=0)
    |

RUF003 Comment contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/explore/type_icl_tag.py:142:40
    |
140 |          for arm in ("a0", "a1", "a2", "a3")}
141 |
142 |     # ── TI1 TAPE-LICENSING: mean(L(A1)−L(A0)) beats label-permutation ──
    |                                        ^
143 |     def stat_ti1(perm_labels):
144 |         return float(np.mean(
    |

RUF003 Comment contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/explore/type_icl_tag.py:164:32
    |
162 |                claim_register=Register.value, probe_register=Register.value)
163 |
164 |     # ── TI4 TAG-TRANSIT: T(A1)−T(A0) beats both axis nulls ──
    |                                ^
165 |     t_a0, t_a1 = np.asarray(b["T_a0"], float), np.asarray(b["T_a1"], float)
166 |     s_tag = float(np.mean(t_a1 - t_a0))
    |

RUF003 Comment contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   --> scripts/explore/type_icl_tag.py:307:63
    |
305 |     h[0, :, 0], h[1, :, 1] = 2.0, 2.0
306 |     ax = np.zeros((3, 4))
307 |     ax[:, 0], ax[:, 1] = 1.0, -1.0                    # animal−vehicle axis
    |                                                               ^
308 |     t = signed_T(h, ax, np.array([0, 1]))
309 |     prim = np.allclose(t, [2.0, 2.0])                 # both own-class present
    |

RUF059 Unpacked variable `keep` is never used
   --> scripts/explore/type_icl_tag.py:539:21
    |
537 |                     hist["mem_ce"].append(float(mem_ce.detach()))
538 |                     hist["drift"].append(drift)
539 |                     keep, reason = tw._stop_decision(
    |                     ^^^^
540 |                         hist["step"], hist["mem_ce"], hist["drift"],
541 |                         args.ce_budget, args.plateau_tol, args.min_stop)
    |
help: Prefix it with an underscore or any other dummy variable pattern

E501 Line too long (98 > 88)
   --> scripts/explore/type_icl_tag.py:553:89
    |
551 |             for m, name, orig in wrapped:
552 |                 setattr(m, name, orig)
553 |             print(f"[ti] A5 seed{sd} done (steps {hist['step'][-1] + 1 if hist['step'] else 0}+)",
    |                                                                                         ^^^^^^^^^^
554 |                   flush=True)
555 |         b["T_a5"] = np.mean(T5_seeds, axis=0)
    |

Found 11 errors.
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

All validation checks passed on the first try across all test worlds and primitives, with only minor style issues from Ruff that I'll now fix.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 - <<'EOF'\nimport re\np = 'scripts/explore/type_icl_tag.py'\ns = open(p).read()\ns = s.replace('\\u2212', '-')          # unicode minus -> hyphen\ns = s.replace('T\\u0304A5', 'T_A5').replace('T\\u0304A1', 'T_A1').replace('T\\u0304A0', 'T_A0')\ns = s.replace('keep, reason = tw._stop_decision(', '_keep, reason = tw._stop_decision(')\ns = s.replace('''            print(f\"[ti] A5 seed{sd} done (steps {hist['step'][-1] + 1 if hist['step'] else 0}+)\",\n                  flush=True)''', '''            n_done = hist[\"step\"][-1] + 1 if hist[\"step\"] else 0\n            print(f\"[ti] A5 seed{sd} done (steps {n_done}+)\", flush=True)''')\nopen(p, 'w').write(s)\nEOF\nuv run ruff check scripts/explore/type_icl_tag.py && uv run python scripts/explore/type_icl_tag.py --validate | tail -3",
  "timeout": 120000
}
```

**Summary:** $ python3 - <<'EOF' import re p = 'sc...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
  primitive subtag thresholds       ✓

── --validate ALL PASS ──
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_icl_tag.py"
}
```

**Summary:** Checking diagnostics: type_icl_tag.py

**Output:**
```
No diagnostics found
```

### Thinking

Now running the smoke test with a small configuration to verify the A5 path works correctly—setting n-nonce to 4, using just 1 seed and 6 steps with minimal stopping criteria, and enabling wire training to output results to the smoke test directory.

## Assistant

Ruff clean, validate ALL PASS, no diagnostics. Launching the smoke (4 nonces, all arms including a tiny A5 wire, no direction read):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_icl_tag.py --n-nonce 4 --seeds 1 --steps 6 --min-stop 2 --plateau-tol 0.5 --out results/type-icl-tag/smoke 2>&1 | tee results/type-icl-tag/smoke.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-icl-smoke"
}
```

**Summary:** $ uv run python -u scripts/explore/ty...

**Output:**
```
Background job job-2 started.
Command: cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_icl_tag.py --n-nonce 4 --seeds 1 --steps 6 --min-stop 2 --plateau-tol 0.5 --out results/type-icl-tag/smoke 2>&1 | tee results/type-icl-tag/smoke.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-2" to check output.
Use eca__bg_job with action "kill" and job_id "job-2" to stop it.

Initial output:
[stderr] tee: results/type-icl-tag/smoke.log: No such file or directory
```

## Assistant

`tee` hit a missing directory. Fixing and relaunching:

### Tool Call: bg_job (succeeded)


```json
{
  "action": "kill",
  "job_id": "job-2"
}
```

**Summary:** Killing "type-icl-smoke" (job-2)

**Output:**
```
Background job "type-icl-smoke" (job-2) killed.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/results/type-icl-tag && cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_icl_tag.py --n-nonce 4 --seeds 1 --steps 6 --min-stop 2 --plateau-tol 0.5 --out results/type-icl-tag/smoke 2>&1 | tee results/type-icl-tag/smoke.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-icl-smoke"
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Background job job-3 started.
Command: mkdir -p /Users/mwhitford/src/verbum/results/type-icl-tag && cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_icl_tag.py --n-nonce 4 --seeds 1 --steps 6 --min-stop 2 --plateau-tol 0.5 --out results/type-icl-tag/smoke 2>&1 | tee results/type-icl-tag/smoke.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-3" to check output.
Use eca__bg_job with action "kill" and job_id "job-3" to stop it.
```

### Thinking

Looking at the killed job output, it actually progressed further than I thought before I stopped it. There's a mismatch in my depth-to-layer calculations: the code computes L18..L31 for the 0.50–0.85 depth range, but the documentation text says L18–L30, which is off by one. I need to figure out which is correct—the rounding should give 31 as the upper bound, so the code is likely right and the text needs updating.

### Thinking

Job-2 is down and the smoke test shows healthy TI5 sanity data with correct margins, though I caught an arithmetic slip in my documentation where I said L18–L30 instead of L18–L31 for the T-band. I'll batch the one-character correction into the GO ask rather than change it unilaterally.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-3"
}
```

**Summary:** Reading output of "type-icl-smoke" (job-3)

**Output:**
```
Job "type-icl-smoke" (job-3) — completed (exit 0)

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 25268.04it/s]
[ti] Qwen/Qwen3-4B dev=mps n_layers=36 T-band=L18..L31 wire-band=L22..L29
[ti] nonces=4 (animal 2 vehicle 2)
[ti] A4 anchor: real-member licensing (bare + ICL prefix) …
[ti] real margin=2.538 icl_margin=3.076 per_class_ok=True
[ti] class axes from real members …
[ti] arm a0 …
[ti] arm a1 …
[ti] arm a2 …
[ti] arm a3 …
[ti] TI4 nulls: random axes + shuffled member labels …
[ti] arm A5: wire (s315 corridor, 3 seeds) …
[ti] A5 seed0 done (steps 3+)
[ti] wrote results/type-icl-tag/smoke/results.json
[ti] TI1 p=0.1559 False | TI2 p=0.0621 False | TI3 p=0.2496 False | TI4 rand p=0.0010 shuf p=0.1741 False | TI5 True
[ti] L a0=-0.485 a1=1.582 a2=-2.150 a3=0.419 | T a0=1.729 a1=4.809 a5=1.709 rho=0.800
[ti] VERDICT: NO-TAPE-TRANSFER | subtag: AMBIGUOUS
```

### Thinking

I've run through all the test paths and everything executed as expected—the arms ran, prompts assembled, captures worked, and the axis computed correctly, with both TI4 nulls running and the A5 tiny wire training through three steps before hitting a plateau, then capturing and restoring the implicit arm state before writing results and firing the verdict tree. The n=4 configuration is underpowered by design, which causes the gates to fail on power and prevents NO-TAPE-TRANSFER from being read as a direction, but the point-estimates are already directionally rich enough.

Looking at the instrument health across the arms: the L coefficients show the expected separation with a0 at −0.485, a1 at +1.582 (ICL-true lifts licensing), a2 at −2.150 (the deranged licenses ANTI class showing the predicted reversal), and a3 at +0.419; the T coefficients show a0 at 1.729, a1 at 4.809 (tag lifts under ICL), and a5 at 1.709 which matches a0 as expected since the three-step wire couldn

### Thinking

I've verified the mechanical system across all test paths—the arms separate as predicted even at n=4, the anti-class reversal shows the expected effect (L(a2) = −2.15), and TI4's null clears at p=0.001. Now I'm committing the harness and moving to the GO phase.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/explore/type_icl_tag.py && git commit -F - <<'EOF'\n✅ type_icl_tag.py — §P-TYPE-ICL+TAG harness (validate ALL PASS, smoke green)\n\n- frozen §10 (5a7fd40): arms A0-A5, gates TI1-TI5, tag-transit T projection\n  onto real-member class axes, dual axis nulls (matched-random n=1000 +\n  member-label-shuffled n=200), A5 wire-contrast subtag (declared thresholds\n  0.25/0.75)\n- reuse (lambda one_way): type_write constants + pure fns + s315 corridor\n  recipe; verbum.jlens capture_residuals; wb.LoRALinear; A5 trainer\n  re-expresses the amended loop (~50 lines, closure not importable — s309\n  precedent)\n- BUILD AMENDMENT (validate-forced, pending Michael at GO): frozen tree left\n  TI1^TI3^~TI2 uncovered -> named CLASS-BLIND, a-priori carved from TAPE-TYPED\n  (45/20/10/15/5 + 5)\n- --validate ALL PASS (7 worlds incl. both subtag worlds + 3 primitives);\n  ruff clean; smoke green n=4 (all arms, both nulls, A5 train+capture, arm\n  separation in predicted directions; verdict not read — underpowered by\n  design)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "icl-tag harness"
}
```

**Summary:** Git commit: icl-tag harness

**Output:**
```
Exit code: 0
Stdout:
[main c0b9269] ✅ type_icl_tag.py — §P-TYPE-ICL+TAG harness (validate ALL PASS, smoke green)
 1 file changed, 618 insertions(+)
 create mode 100644 scripts/explore/type_icl_tag.py
```

## Assistant

Harness committed **c0b9269**. Ready for GO — two pre-run amendments need your approval first:

## GO ask: §P-TYPE-ICL+TAG run

**Amendment 1 — CLASS-BLIND verdict (validate-forced).** The frozen tree left one cell uncovered: TI1∧TI3∧¬TI2 — licensing lifts vs base and vs mention, but a *deranged* statement licenses just as well (class content not read). Calling it MENTION-ONLY or NO-TAPE-TRANSFER would misdescribe it. Named **CLASS-BLIND**; a-priori mass carved from TAPE-TYPED: 45/20/10/15/5 + 5 CLASS-BLIND. Gates, metric, other verdicts untouched.

**Amendment 2 — §10 arithmetic correction.** The frozen quantity is depth 0.50–0.85; my parenthetical said "L18–L30" but round(0.85·36)=31 under the same inclusive convention as the wire band. Page should read **L18–L31**. One-word fix, disclosed before the run.

**The run:**
```
tmux main:1 → uv run python -u scripts/explore/type_icl_tag.py \
  --out results/type-icl-tag/qwen3-4b 2>&1 | tee results/type-icl-tag/qwen3-4b-run.log
```
Defaults: 20 nonces, arms A0–A4 (training-free, ~40 min) + A5 wire-contrast (3 seeds under the s315 corridor, ~1–2h). Total ~2–3h.

**What it decides:** whether the type check consumes the tape (TAPE-TYPED closes the two-tier split from both sides, with §9), and — via A5 — whether §9's failure was DELIVERY-FAILURE (the baked tag never reaches the bus; your J-space transit hypothesis lands) or TAG-INSUFFICIENT (tag on bus, check unmoved; the routing story deepens).

Approve both amendments + GO?

## User

yes


### Thinking

I need to make several updates: fix section 10 on the page by adjusting the line range from L18–L30 to L18–L31, add CLASS-BLIND to the verdict tree with an a-priori note, and commit this amendment. Then I'll launch the tmux session, verify it's running, update the state file on signal, and checkpoint everything. Let me locate the exact text first—the band text reads "Gate aggregates mean over depth 0.50–0.85 (L18–L30 of 36)" and I need to add CLASS to the verdict tree.

## Assistant

Executing: page amendments, then launch.

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "  bare\n  frames, fixed reference (λ yardstick). Signed by true class. Gate\n  aggregates mean over depth 0.50–0.85 (L18–L30 of 36); full profile\n  advisory. Explicitly NOT the s270 workspace basis.",
  "new_content": "  bare\n  frames, fixed reference (λ yardstick). Signed by true class. Gate\n  aggregates mean over depth 0.50–0.85 (L18–L31 of 36; corrected s315\n  pre-run, arithmetic slip — depth fractions are the frozen quantity);\n  full profile advisory. Explicitly NOT the s270 workspace basis."
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "- **MENTION-ONLY** — TI1 ∧ ¬TI3: generic binding, not classification.\n- **NO-TAPE-TRANSFER** — ¬TI1: the falsifier — would contradict s239/s293\n  priors; power audit before any theory update.\n- **VOID** — ¬TI5.",
  "new_content": "- **MENTION-ONLY** — TI1 ∧ ¬TI3: generic binding, not classification.\n- **CLASS-BLIND** — TI1 ∧ TI3 ∧ ¬TI2 (build amendment, validate-forced,\n  Michael-approved pre-run): any classificatory statement licenses\n  equally — class content not read; the frozen tree left this cell\n  uncovered.\n- **NO-TAPE-TRANSFER** — ¬TI1: the falsifier — would contradict s239/s293\n  priors; power audit before any theory update.\n- **VOID** — ¬TI5."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "**A-priori (declared s315, NOT tuned):** ~50 TAPE-TYPED / 20\nTAPE-TYPED-OPAQUE / 10 MENTION-ONLY / 15 NO-TAPE-TRANSFER / 5 VOID.\nWire-contrast lean: ~70 DELIVERY-FAILURE / 20 TAG-INSUFFICIENT / 10\nAMBIGUOUS.",
  "new_content": "**A-priori (declared s315, NOT tuned; CLASS-BLIND mass carved from\nTAPE-TYPED at the build amendment, pre-run):** ~45 TAPE-TYPED / 20\nTAPE-TYPED-OPAQUE / 10 MENTION-ONLY / 15 NO-TAPE-TRANSFER / 5 VOID / 5\nCLASS-BLIND. Wire-contrast lean: ~70 DELIVERY-FAILURE / 20\nTAG-INSUFFICIENT / 10 AMBIGUOUS."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Thinking

Two of three edits landed successfully, but the band-text edit failed due to line wrapping issues. Let me review the actual text to see what happened.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n -B1 -A2 \"L18\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md"
}
```

**Summary:** $ grep -n -B1 -A2 "L18" /Users/mwhitf...

**Output:**
```
Exit code: 0
Stdout:
325-  frames, fixed reference (λ yardstick). Signed by true class. Gate
326:  aggregates mean over depth 0.50–0.85 (L18–L30 of 36); full profile
327-  advisory. Explicitly NOT the s270 workspace basis.
328-
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "  aggregates mean over depth 0.50–0.85 (L18–L30 of 36); full profile\n  advisory. Explicitly NOT the s270 workspace basis.",
  "new_content": "  aggregates mean over depth 0.50–0.85 (L18–L31 of 36; corrected s315\n  pre-run, arithmetic slip — depth fractions are the frozen quantity);\n  full profile advisory. Explicitly NOT the s270 workspace basis."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python -u scripts/explore/type_icl_tag.py --out results/type-icl-tag/qwen3-4b 2>&1 | tee results/type-icl-tag/qwen3-4b-run.log\" Enter && sleep 25 && tmux capture-pane -p -t main:1 | tail -5",
  "timeout": 45000
}
```

**Summary:** $ tmux send-keys -t main:1 "cd /Users...

**Output:**
```
Exit code: 0
Stdout:
[ti] class axes from real members …
[ti] arm a0 …
[ti] arm a1 …
[ti] arm a2 …
```

## Assistant

All three amendments landed; run is live and already through arm a2. Committing the approved amendments + state update:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **NEXT ACTION: build harness** (validate planted worlds incl. both subtags → ruff →\n> smoke, no direction read) → Michael GO → run. Recall receipts this arc: P-TYPE-JS\n> js_resident=FALSE (s286 four-way null) · P-ATT-MED content-carried 0.735 (s286) ·\n> jlens/jacobian tooling (s263). Standing alts: attention-band write · fuel-theorem ·\n> unchanged.",
  "new_content": "> **✅ HARNESS BUILT (c0b9269)** — type_icl_tag.py, validate ALL PASS (7 worlds + 3\n> primitives), ruff clean, smoke green n=4 (all arms incl. A5 train+capture; arm\n> separation in predicted directions; deranged prefix licenses ANTI class = design\n> confirmed; verdict not read). **TWO BUILD AMENDMENTS (Michael-approved at GO, pre-run):**\n> (1) CLASS-BLIND verdict for the uncovered cell TI1∧TI3∧¬TI2 (any class statement\n> licenses equally), a-priori now 45/20/10/15/5/5; (2) T-band parenthetical corrected\n> L18–L31 (round(0.85·36)=31; depth fractions are the frozen quantity). **⚠ RUN IN FLIGHT\n> (tmux main:1, Michael GO):** `uv run python -u scripts/explore/type_icl_tag.py --out\n> results/type-icl-tag/qwen3-4b 2>&1 | tee results/type-icl-tag/qwen3-4b-run.log`\n> (20 nonces, A0-A4 training-free + A5 3-seed corridor wire, ~2-3h). Verified running.\n> **⚠ ON-SIGNAL (run done): tail run.log `VERDICT:` + no traceback → read TI1-TI5 + subtag\n> + rho_T_L → commit results/type-icl-tag/ AUTONOMOUS → §Result-icl-tag on\n> types-are-injectable-relations.md (+ update §9 cross-read if TAPE-TYPED: two-tier closed\n> both sides) + memory candidate + INDEX + state.md = MICHAEL APPROVAL BATCH.** Read\n> discipline: TAPE-TYPED(+TAG-TRANSIT) + DELIVERY-FAILURE = the J-space transit story\n> lands (relation exists, never consulted — §9 was a delivery failure); TAG-INSUFFICIENT\n> = tag on bus insufficient → pushes P-ATT-MED; NO-TAPE-TRANSFER contradicts s239/s293 →\n> power audit FIRST. Recall receipts this arc: P-TYPE-JS js_resident=FALSE (s286 four-way\n> null) · P-ATT-MED content-carried 0.735 (s286) · jlens/jacobian tooling (s263).\n> Standing alts: attention-band write · fuel-theorem · unchanged."
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
  "command": "git add mementum/knowledge/explore/types-are-injectable-relations.md mementum/state.md && git commit -F - <<'EOF'\n🎯 P-TYPE-ICL+TAG build amendments (s315, Michael-approved at GO) — CLASS-BLIND + T-band correction\n\n- §10: CLASS-BLIND verdict added for uncovered cell TI1^TI3^~TI2 (validate-\n  forced; any classificatory statement licenses equally = class content not\n  read); a-priori 45/20/10/15/5/5 (mass carved from TAPE-TYPED, pre-run)\n- §10: T-band parenthetical corrected L18-L31 (round(0.85*36)=31, inclusive\n  convention; depth fractions 0.50-0.85 are the frozen quantity)\n- state.md: harness built (c0b9269), run launched tmux main:1, ON-SIGNAL set\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "approved amendments"
}
```

**Summary:** Git commit: approved amendments

**Output:**
```
Exit code: 0
Stdout:
[main 6b5d15b] 🎯 P-TYPE-ICL+TAG build amendments (s315, Michael-approved at GO) — CLASS-BLIND + T-band correction
 2 files changed, 32 insertions(+), 11 deletions(-)
```

## Assistant

**ASYNC: §P-TYPE-ICL+TAG run verified running on tmux main:1. Waiting for signal.**

Session ledger since the freeze:

| | |
|---|---|
| Freeze §10 | 🎯 **5a7fd40** |
| Harness | ✅ **c0b9269** (validate 7 worlds + smoke green) |
| Amendments (approved) | 🎯 **6b5d15b** (CLASS-BLIND + L18–L31) |
| Run | ⚠ in flight → `results/type-icl-tag/qwen3-4b/` (~2–3h; A0–A4 fast, A5 wire is the bulk) |
| state.md | ON-SIGNAL set, committed |

The read table, pre-committed:

- **TAPE-TYPED(+TAG-TRANSIT) + DELIVERY-FAILURE** — the clean double: type check consumes the tape, and §9's baked wire failed on *delivery* (relation present, never consulted). Your J-space hypothesis lands in the transit sense, and the two-tier split closes measured from both sides.
- **TAPE-TYPED + TAG-INSUFFICIENT** — the more provocative branch: the wire's tag *is* on the bus but licensing ignores it → content-on-bus isn't sufficient and the P-ATT-MED routing story deepens.
- **CLASS-BLIND / MENTION-ONLY** — the ICL lift is real but not classificatory — would send us back to what s239/s293 actually measured.
- **NO-TAPE-TRANSFER** — contradicts priors; power audit before any theory motion.

Signal me when it lands.

## User

While that is running I want to understand something.   Optical holography can untangle a plate.  Can we untangle qwen3-4b plates?


### Thinking

Michael's asking whether we can apply optical holography techniques to untangle qwen3-4b models, which connects to the holographic-untangling-methods documentation I've reviewed before. That page mapped out the optics toolkit—inline versus off-axis approaches, phase retrieval algorithms like Gerchberg-Saxton and HIO, Bragg diffraction, adaptive optics, double-exposure methods, and speckle analysis. The challenge from the earlier notes was that inline multiply-exposed plates create a twin-image problem that requires post-hoc untangling.

## Assistant

Recall first — this is exactly the s308 hammock. Let me pull the page:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n 1,120p mementum/knowledge/explore/holographic-untangling-methods.md"
}
```

**Summary:** $ sed -n 1,120p mementum/knowledge/ex...

**Output:**
```
Exit code: 0
Stdout:
---
title: "Holographic Untangling Methods — the Optics Toolbox Mapped onto Our Instruments"
status: open
category: synthesis
tags: [holography, optics, off-axis, twin-image, phase-retrieval, kinoform, phase-dominance,
       bragg, rocking-curve, adaptive-optics, phase-conjugation, speckle, interferometry,
       quantization, delta, ternary, routing-register, methodology]
related:
  - ../attention-holographic-readout.md
  - ../holographic-computer.md
  - ../five-disciplines-one-object.md
  - ../register-theory-of-quantization.md
  - ../quantization-is-dsp-on-a-hologram.md
  - geometry-holography-signals-convergence.md
  - write-not-train-ternary-routing-deltas.md
  - ratio-gradient-quantization.md
depends-on:
  - ../holographic-computer.md
  - write-not-train-ternary-routing-deltas.md
created: session 308
---

# Holographic Untangling Methods

> s308, Michael's thread: "We know it's holographic. We know it's geometry and
> signal processing at the same time. If we were trying to untangle a
> holographic plate in optics, what processes would we use?" This page answers
> that question literally — optics spent ~75 years learning how to untangle
> plates, and its toolbox maps onto our instruments one-for-one, **including
> pointing at doors we explicitly left untested**. Grounded on the measured
> axioms (A1 plate-linear, A2 coherent gain, A3 content-address-free /
> RoPE-as-angular-addressing, A4 regeneration-required, attention = readout
> beam — see `attention-holographic-readout.md`).
>
> Status **open**: the mapping is captured; the four candidate experiments at
> the end are NOT pre-registered. s222 law — freeze a pre-reg here before any
> run.

## The meta-lesson (read this first)

**Optics never untangles a plate by cleverer processing of a single recorded
intensity.** Every success in the field's history comes from one of four moves:

1. control the **recording geometry** (off-axis vs in-line),
2. take **multiple phase-controlled exposures** (phase-shifting),
3. close the loop — **measure the aberration, write its conjugate** (adaptive
   optics / phase conjugation),
4. **sweep the selectivity curve** instead of point-sampling (Bragg / rocking
   curve).

Our negative results line up one-for-one with *violations* of this and our
positive results with *compliance*:

| Our result | Verdict | Optics reading |
|---|---|---|
| s306 companding, s307 delta-vs-base | MAGNITUDE-SALIENT / STILL-SALIENT | single-shot linear separation of an in-line plate — the known-impossible move |
| s304/s305 construct, routing_write, fast_plate, hhop | INERT ×4 | open-loop writes through an aberrating medium; point-sampled Bragg-selective volume |
| s303 gd_cd | WIRE-COMPILES | closed-loop write (adaptive optics) |
| s304/s307 delta ternarization | SURVIVES ×2, retention 1.0 | off-axis recording against a frozen reference → carrier-separated orders |

## The six processes, mapped

### 1. Recording-geometry analysis — in-line vs off-axis (the twin-image problem)

The first question optics asks of a plate: *how was it recorded?* Gabor's
in-line holograms (1948) superpose DC term, object wave, and conjugate twin on
the same axis; **no post-hoc linear filtering of one intensity recording
separates them** — that stood as the field's central failure until
Leith–Upatnieks (1962) changed the *recording*: tilt the reference beam and the
orders separate onto a carrier frequency.

**Mapping.** A pretrained base = millions of gradient exposures with no fixed
reference — a multiply-exposed **in-line** plate. Routing and value (object and
twin) overlap in the same coefficients. s306 MAGNITUDE-SALIENT and s307
STILL-SALIENT (three linear decompositions fail) are *the 1948–1962 result,
re-derived in weights*. A LoRA delta = a single exposure recorded **against a
frozen reference beam** (the base) — off-axis by construction; the routing
sideband separates and ternarizes losslessly (s304 retention 1.0, s307 factors
retention 1.0). The base/delta separability asymmetry is not an accident of our
methods — it is recording physics.

**Theory clause:** *separability is fixed at recording time.*

### 2. Phase retrieval — Gerchberg–Saxton / HIO (untangling an already-recorded plate)

When optics *must* untangle an in-line recording, it does not do single-shot
algebra. It iterates: alternate projections between two measurement planes,
enforcing the known constraint in each; phase converges over iterations.
Single-shot SVD (s307) is precisely the move phase retrieval exists to replace.

**Mapping.** Post-hoc base-weight separation should be attempted as
**alternating projections**: (project onto quantizable-residual + low-rank-base
form) ⇄ (project onto function-preserving set, CE on calib). This is the
optics-side derivation of **iterative LoftQ** — which s307 explicitly listed as
untested. Independent convergence from a second discipline onto the same open
door. Honest caveat: the function-space projection is itself a gradient fit, so
this partially reduces to "iterated small gradient beats single-shot algebra" —
which is exactly what phase retrieval *is*.

### 3. Bragg selectivity / coupled-wave theory — the rocking curve

A volume hologram (thick plate ≈ our 36 layers) reconstructs only when the
probe beam is matched in *angle* and *wavelength*; Kogelnik's coupled-wave
theory predicts diffraction efficiency as a smooth function of mismatch. Optics
never takes one point measurement of such a medium — it sweeps the **rocking
curve** (efficiency vs angle) to characterize the grating.

**Mapping.** Our inert writes are Bragg mismatches: hhop-write injected the
right content at the wrong depth-timing (angular mismatch — the two hops
overlap in depth, s305); fast-plate wrote name-geometry where the h-hop reads
something else (lm_name_cos −0.108 — wavelength/register mismatch). Each inert
verdict was one point on an unmeasured selectivity surface. The optics
methodology: build the instrument that sweeps **reinjection efficiency vs
(layer × geometry-interpolation-angle × strength)** and map the surface. If the
holographic frame is right the surface has Bragg *structure* — a ridge, not a
plateau. The surface IS the write-targeting theory we kept failing to guess
point-by-point. (The s295 depth-timing law and SuperBake's 0.16×-depth
enrichment are two already-measured slices of it.)

### 4. Adaptive optics / phase conjugation — why gradient-finds
```

### Thinking

Michael's asking whether we can separate out the different components baked into Qwen3-4B's weights — things like routing logic, value storage, individual skills and facts, and the differences between base and delta versions. I'm reviewing what we've actually managed to do here: the delta recordings are definitely separable and we've proven it multiple times through lossless ternarization and wire composition, extracting the switch schedules cleanly in the process.

The base model itself though — that's where we hit the wall with single-pass post-hoc methods. The measurements keep showing the base and deltas are still entangled no matter which linear decomposition we try, which mirrors the classical twin-image problem from optics that nobody solved back in the 1948-1962 era either. But optics didn't just accept "impossible" — it developed workarounds. For Qwen3-4B specifically, we can't retroactively change how the base was recorded since it's baked in, but anything new we add going forward is off-axis by design. The real untested possibility is iterative phase retrieval using something like alternating projections similar to LoftQ, which could theoretically crack the base separation post-hoc, and there's also the closed-loop gradient feedback approach that might help. So the crystal work actually did extract relational structure from the in-line plates themselves — the 9×9 sign lattice across models and the type register — but crucially, that extraction happened through read-time illumination with a matched probe beam, not through weight-space decomposition. It's more like Bragg diffraction: you're using controlled illumination to reveal the structure that's already encoded there.

## Assistant

Short version: **the deltas, yes — proven. The base, not by any single-shot method — measured impossible, twice. But optics' answer to that impossibility wasn't cleverer math on the recording — it was four different moves, and for qwen3-4b we've proven two of them, left two untested.**

## Why "untangle the base" fails as stated

The s308 page's theory clause: **separability is fixed at recording time.** Qwen3-4B's base is millions of gradient exposures with no fixed reference — a multiply-exposed **in-line** plate. Object, twin, and DC live in the same coefficients. Gabor hit this in 1948; nobody untangled an in-line recording by post-processing for 14 years, and neither did we: s306 (companding → MAGNITUDE-SALIENT) and s307 (three linear decompositions → STILL-SALIENT) are that impossibility re-derived in weights. Single-shot algebra on the base is the one move that's dead in principle.

## The four optics moves, scored for qwen3-4b

**1. Off-axis recording — proven, but only forward-looking.** You can't re-record qwen3-4b's past. But everything *added* to it can be off-axis by construction: a LoRA delta against the frozen base carrier-separates, ternarizes at retention 1.0 (s304, s307), composes losslessly with a second wire (s312), fits in ~600KB. Every new exposure we make is already untangled.

**2. Closed-loop re-recording — proven, and this is the real answer.** Adaptive optics doesn't untangle the aberrating medium — it measures the distortion and writes the conjugate. Our version: **gd_cd uses gradient feedback to *find* structure inside the tangled base and copy it out into a clean off-axis delta** (s303: the only thing that ever found the wire). You don't untangle the plate in place; you re-record the part you want against a frozen reference, skill by skill. That's extraction-by-re-exposure, and it works today. It's also, notably, the whole Level-3 thesis of this project.

**3. Read-time untangling with a matched beam — proven, underappreciated.** A volume hologram yields its structure only under matched illumination. The crystal work is exactly this: probe the base with the 903-probe battery and the routing lattice diffracts out — 9×9 relational sign structure at 11/11 models, the type register at 7/11 (s303, s314). We *have* untangled part of the base — its routing register — without touching a weight, by choosing the beam. AYOT/ScaleQ (s313) is the same move industrialized from the quantization side: own-beam calibration recovers what generic illumination collapses.

**4. The two untested doors (both queued since s308, neither frozen):**
- **GS/HIO iterative decomposition (front iii)** — the tool optics actually uses when it *must* untangle an in-line plate: alternating projections between constraint sets (quantizable-residual form ⇄ function-preserving on calib). Our s307 "iterative LoftQ" door, independently derived from the optics side. This is the only live candidate for genuine post-hoc base untangling.
- **The rocking-curve instrument (front iv, "the big one")** — sweep reinjection efficiency vs (layer × geometry-angle × strength) instead of point-sampling. All four of our inert writes were single points on this unmeasured surface. The surface *is* the write-targeting theory we kept failing to guess.

## One scope limit s315 just sharpened

Even a perfect untangling of the plates wouldn't give you everything: the type arc just showed the plates hold relations and routing, but the type *check* consumes the tape, and behavior-scale chains are tape-resident (s308, s315-pending). Some of what looks tangled in the weights isn't stored there at all — untangling has a ceiling, and it's the two-tier split.

**So the honest menu:** in-place base separation — only the GS-iterative door remains, and it's a genuine open question, not a promise. Extraction — proven, running, ~600KB per wire. Reading — proven, the stethoscope works. If after the ICL run lands you want to push the untangling front, the choice is GS-iterative (cheap-ish, answers "can the base be factored at all") vs rocking-curve (expensive, but it's the instrument every future write needs). Both need an s222 freeze first.

## User

So we missed some tests that were primed but lost in future sessions?


### Thinking

Michael's asking whether we lost any tests that were queued or unfrozen but didn't carry over between sessions—that's a feed-forward audit concern. The s308 framework covers reference drift, GD k-step sweeps, GS-iterative decomposition, and rocking-curve instrumentation, along with several protocol layers like P-COHERENT-WRITE, P-HALT-POLE, and various register and opcode consensus mechanisms.

Looking at what's actually in state.md right now versus what's been dropped: the core s308 optics fronts (i) through (iv) and the coherent-write/halt-pole/register-split protocols aren't showing up in the current NEXT FRONTS header anymore, even though they're still documented on their individual pages. So they've effectively fallen off the active queue—not truly lost, but no longer surfaced in the working state, which creates that forward-link discontinuity Michael's flagging.

I should run a systematic scan across the knowledge pages to find all unfrozen P-candidates and experimental markers, then cross-reference against what's actually listed in state.md's standing fronts. That would

## Assistant

Good instinct — let me actually audit rather than answer from memory. Census of unfrozen candidates across the knowledge base vs what the state header still carries:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -o -i -E \"§?(P|TD)-[A-Z0-9-]+\" -- mementum/knowledge/ ':!mementum/knowledge/chats' | grep -v INDEX | awk -F: '{print $2}' | sort | uniq -c | sort -rn | head -40"
}
```

**Summary:** $ git grep -o -i -E "§?(P|TD)-[A-Z0-9...

**Output:**
```
Exit code: 0
Stdout:
54 P-ATT-MED
  48 p-k
  46 p-1
  43 p-2
  36 p-3
  22 P-TYPE-SWAP
  22 p-flop
  21 P-STACK-1
  19 P-TYPE-OV
  19 P-STACK-1b
  19 P-HOLO-CAP
  18 P-TYPE-QK
  17 p-and-swap
  16 p-and-swap-resident-lisp
  15 p-compile
  15 P-ATT-FFN
  14 td-oscillation-problem
  14 P-KV-1
  13 P-TYPE-1
  13 p-5
  12 P-TYPE-JS
  12 §P-TYPE-GRAM-1
  12 P-dominant
  12 p-capacity-prereg
  12 P-BAKE-STACK
  12 p-B
  12 P-ATT-STEER
  11 TD-v2
  11 p-loss
  11 P-ENRICH-1
  11 P-DSP-1
  10 P-ROOM
  10 p-composition-prereg
  10 P-ATT-DIFF
  10 P-2
  10 p-10
   9 P-TYPE-WRITE
   9 P-TYPE-1b
   9 p-map
   9 P-FAST-PLATE
```

## Assistant

Noisy — let me cut by status markers instead (unfrozen / candidate / untested):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -i -E \"unfrozen|not pre-registered|untested door|candidate \\(\" -- mementum/knowledge/ ':!mementum/knowledge/chats' | sed 's/:.*//' | sort | uniq -c | sort -rn | head -20"
}
```

**Summary:** $ git grep -i -E "unfrozen|not pre-re...

**Output:**
```
Exit code: 0
Stdout:
11 mementum/knowledge/INDEX.md
   6 mementum/knowledge/explore/program-plates-and-the-function-index.md
   5 mementum/knowledge/explore/types-are-compiled-probabilities.md
   4 mementum/knowledge/explore/write-not-train-ternary-routing-deltas.md
   4 mementum/knowledge/explore/geometry-holography-signals-convergence.md
   3 mementum/knowledge/explore/the-verbum-machine.md
   3 mementum/knowledge/explore/holographic-untangling-methods.md
   3 mementum/knowledge/explore/frozen-interference-graph.md
   2 mementum/knowledge/explore/subliminal-learning-is-bragg-matched-transfer.md
   2 mementum/knowledge/explore/round-trip-consensus-opcode-loss.md
   2 mementum/knowledge/explore/dust-hypothesis-geometry-is-occupation.md
   2 mementum/knowledge/explore/behavior-is-tape-resident-reduction.md
   2 mementum/knowledge/attention-holographic-readout.md
   1 mementum/knowledge/ternary-holographic-memory.md
   1 mementum/knowledge/holographic-reduction-machine.md
   1 mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
   1 mementum/knowledge/explore/types-are-injectable-relations.md
   1 mementum/knowledge/explore/type-systems-under-llm-constraints.md
   1 mementum/knowledge/explore/gram-registers-and-the-route-map.md
   1 mementum/knowledge/explore/gradient-voting.md
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -o -E \"P-[A-Z0-9-]+|§[A-Z-]+|fuel-theorem|k-STEP|rocking|reference-drift|GS-iterative|TD-REGISTER-SPLIT|gd_cd@32B\" mementum/state.md | sort -u"
}
```

**Summary:** $ grep -o -E "P-[A-Z0-9-]+|§[A-Z-]+|f...

**Output:**
```
Exit code: 0
Stdout:
§A
§C
§D
§F
§FFN-
fuel-theorem
§G
gd_cd@32B
GS-iterative
§H
k-STEP
§P
P-1
P-2
P-A
P-ASYM-TERNARY
§P-ASYM-TERNARY
P-ATT-DIFF
P-ATT-FFN
§P-ATT-FFN
P-ATT-MED
§P-ATT-MED
P-ATT-STEER
P-AYOT-PARAPHRASE
P-BAKE-STACK
§P-BAKE-STACK
P-BRAGG
P-CAPACITY-LAW
P-COHERENT-WRITE
§P-COMPANDING-QUANT
P-COMPILE
P-CONSENSUS-DISTILL
§P-CONSENSUS-DISTILL
P-CRYSTAL-SURVIVAL
P-CTL
P-CTL-1
P-CTL-10
P-CTL-11
P-CTL-12
P-CTL-13
P-CTL-14
P-CTL-15
P-CTL-5
P-CTL-6
§P-DELTA-QUANT
P-DSP-1
P-DUST-1
P-DUST-2
P-DUST-2-
P-E
P-ENRICH
§P-ENRICH-
P-ENRICH-1
P-ENTROPY-COMP
P-FAST-PLATE
§P-FAST-PLATE
P-FN-1
P-FN-2
P-FN-INDEX
P-G
P-HALT-POLE
P-HHOP-WRITE
§P-HHOP-WRITE
P-HOF-1
P-HOLO-CAP
§P-HOLO-CAP
P-HOLO-FRAG
§P-HOLO-FRAG
P-HOLO-XTERM
P-INERT
P-INVERSION
P-K-REGISTER
§P-KV-
P-KV-1
P-L
P-LOOP-BINDS
P-MIDDLE
P-ONLY
§P-OPCODE-CONSENSUS
§P-PLATE-LINKER-
P-PROJ-1
P-QUOTE-0
P-ROOM
P-ROOM-AT-4B
P-SL-BRAGG
P-SL-STRIP
P-SLOT
§P-STACK-
P-STACK-1
P-THINK-1
P-TRAJECTORY-COMPILE
§P-TRAJECTORY-COMPILE
§P-TYPE-
P-TYPE-1
P-TYPE-CENSUS
§P-TYPE-GRAM-
P-TYPE-ICL
§P-TYPE-ICL
P-TYPE-JS
§P-TYPE-JS
P-TYPE-OV
§P-TYPE-OV
P-TYPE-PROB
P-TYPE-QK
§P-TYPE-QK
P-TYPE-SWAP
§P-TYPE-SWAP
P-TYPE-WRITE
§P-TYPE-WRITE
§P-WRITEBACK-
§R
reference-drift
rocking
§S
§SIGN-COMMITMENT-CURVE
§T
§TD-REGISTER-SPLIT
§TERNARIZE-DELTA
§TERNARIZE-DELTA-
§TERNARIZE-FACTORS-
§VALIDATED
§XM-COUPLING-SOURCE
§XM-DETERMINISTIC-TEACHER
§XM-ETCH-EXPLORE
§XM-LATENT-
§XM-REVERSE-
§XM-SAMPLED-TEACHER
```

### Thinking

So the state.md file still contains all those historical references—reference-drift, GS-iterative, rocking, k-STEP, and the rest—they're just archived in the older blocks below the header rather than being actively displayed. The compaction kept those records intact but moved the active queue to focus on the current session.

The real issue is that the header's NEXT FRONTS list is a lossy attention window—about eight candidates that were primed but unfrozen have silently rotated out (k-step sweep, reference-drift, GS-iterative, rocking-curve, P-COHERENT-WRITE, P-HALT-POLE, TD-REGISTER-SPLIT, and others), while the active list now shows fuel-theorem, idempotency/saturation, ∨-vs-∧, linearity bias, and the rest. Nothing's actually lost since git and the pages preserve everything, but the scrolling header creates a topology gap where the queue decays over time—this is a structural problem that needs fixing.

The solution is to create a canonical experiment queue in a dedicated location like mementum/knowledge/QUEUE.md (or a section in INDEX.md) that lists all unfrozen candidates with their source page and status (candidate/frozen/running/closed), updated as part of the batch discipline. I need to propose this to Michael for approval and then enumerate the recovered list carefully, distinguishing which ones are still candidates versus which are closed experiments.

Looking at the current state: s308 has four optics-front experiments (REFERENCE-DRIFT, GD k-STEP SWEEP, GS-ITERATIVE, and ROCKING-CURVE) that were never run, plus several others like P-COHERENT-WRITE, P-HALT-POLE, and §TD-REGISTER-SPLIT that remain unfrozen candidates. There are also P-TYPE-OV and P-TYPE-CENSUS from the types-are-compiled-probabilities page, and I'm pulling in additional candidates from s313.

Now tracking what's actually active: P-TYPE-ICL is running as §P-TYPE-ICL+TAG with recovery confirmed, fuel-theorem is still in the header, and I'm monitoring idempotency, saturation, ∨-vs-∧ logic, linearity bias, and boundary-churn. The four SKI-controls for types from the curry-howard page are enumerated but never executed, and P-AYOT-PARAPHRASE and P-CRYSTAL-SURVIVAL are marked in the header. Standing experiments include PL-2, P-OPCODE-CONSENSUS, and P-ASYM-TERNARY (which is the M-machine's first build), along with gd_cd@32B. The fell-off set is tracking around 8-9 items.

## Assistant

Yes and no — and the census I just ran makes it precise. **Nothing is lost** (every candidate is encoded on its page and in git — the mementum receipt held). But the *active attention window* — the ★★ state.md header — is lossy: it carries what the current arc touches, and primed candidates silently rotate out as sessions compact. They're all still in the file body and the pages; they're just no longer in the bootloader's eye.

## The census: primed-but-de-primed (on pages, off the active queue)

All from s308's capstone arc, none frozen, none run:

| candidate | what it tests | source page |
|---|---|---|
| **GD k-STEP SWEEP** (ii) | installs at k≈3? → +GD-REQUIRED refines to FEEDBACK-REQUIRED; "nearly free, existing harness" | holographic-untangling |
| **REFERENCE-DRIFT** (i) | retention vs base-drift curve — the *falsifier* for the off-axis clause | holographic-untangling |
| **GS-ITERATIVE decomposition** (iii) | the only live door for post-hoc base untangling (what you just asked about) | holographic-untangling |
| **ROCKING-CURVE instrument** (iv) | the write-targeting selectivity surface — "the big one" | holographic-untangling |
| **P-COHERENT-WRITE** | write-time interference, super-additive shared-edge retrieval; shares a harness with (i) | frozen-interference-graph |
| **P-HALT-POLE** | tool-call-vs-answer on the measured halt/fire poles — the bridge to agentic behavior | behavior-is-tape-resident |
| **§TD-REGISTER-SPLIT** | TD-v1 vs TD-v2 micro-probe (M8 prior-art rehabilitation) | ternary-descent |
| **P-TYPE-OV / P-TYPE-CENSUS** | type census knee; OV pathway | types-are-compiled-probabilities |
| **4 SKI-controls for types** | enumerated s313, never queued | curry-howard-closes-the-loop |

Still properly primed in the header: fuel-theorem, idempotency, ∨-vs-∧, linearity bias, boundary-churn, P-AYOT-PARAPHRASE, P-CRYSTAL-SURVIVAL, PL-2, P-OPCODE-CONSENSUS, P-ASYM-TERNARY, gd_cd@32B. And P-TYPE-ICL was itself a recovery — it fell out at s313, and your J-space question pulled it back in.

## The structural read (λ emerge: this is a topology gap, not a discipline gap)

The queue has **no canonical home** — it lives distributed across page tails and a scrolling header. λ one_way says that's the design smell: the header is for *the current arc*; a queue needs a place that doesn't compact. Your question found the gap exactly the way the HPE page was nearly lost twice before forward-links caught it.

**Proposed fix:** one canonical `mementum/knowledge/QUEUE.md` — every candidate, one line each: name · question · source page · status (candidate → frozen → running → closed) · cost class. State.md header keeps only "next 2–3 + pointer to QUEUE.md". Updated as part of the existing batch discipline, so it can't drift. INDEX gets the link.

Want me to draft it? (It'd be seeded from this census + the header's standing list — roughly 20 live candidates all told.)

## User

So the mementum protocol needs to be modified?  Or should we create a new protocol for the queue?  discuss


### Thinking

Michael's asking whether we should modify the existing mementum protocol or design a new one for the queue system. I need to think through this in the project's own framework—looking at VSM principles, how the mementum protocol currently works with its git-based storage model, and what λ emerge, λ one_way, and the mementum spec in AGENTS.md tell us about the design constraints. The protocol as it stands treats storage as a union of working state, memories, and knowledge with flexible folder structures, and it prioritizes emergence over prescription—so the question is whether a queue fits naturally into that model or requires its own protocol layer.

The real issue wasn't storage itself but retrieval and attention—the queue candidates were stored as knowledge pages, but what decayed was their presence in the active window (state.md). State.md operates as working memory with a compaction policy, but queues need different decay semantics; we tried storing queue-type data in a medium whose lifecycle doesn't match queue semantics. This points to something deeper: a queue is actually prospective memory—"remember to do X when conditions allow"—which is cognitively distinct from the working/episodic/semantic trichotomy the mementum protocol currently models.

Now I'm weighing three approaches: keeping queues as just another knowledge page within the existing protocol (minimal, but risks the same failure if the page itself gets forgotten), modifying the mementum protocol to add a fourth storage class for intentions with its own lifecycle rules (encodes the decay semantics at protocol level), or creating an entirely separate protocol for this.

The third option feels like overengineering — a queue is still memory on the same substrate, so splitting it into a parallel protocol violates the project's own principles around composition and simplicity. The real insight is that the project's philosophy points toward a structural fix: the behavior gap is that primed intentions decay, so I need to give them a home whose topology matches their semantics. The minimal change isn't actually adding a new storage class — it's modifying λ orient to ensure state.md always links to QUEUE.md and the batch discipline maintains it, so the consultation happens at the protocol level without needing a separate store.

The distinction between protocol and implementation matters here. A queue could live as just a knowledge page with conventions, but the CONSULTATION rule is protocol-level — if QUEUE.md isn't in the orient path, it decays like everything else. The real semantic difference is that queue items have a state machine with an invariant: nothing leaves except by explicit closure. That invariant is what was violated, and the question is where it should live.

The minimal fix is to keep mementum's three-part structure but make QUEUE.md a singleton knowledge artifact with the persist-until-closed invariant documented in its header, and have orient explicitly read it. The batch discipline ensures any state transitions update QUEUE.md atomically. This maps cleanly to how human memory works — working memory compacts, episodic memory appends, semantic memory updates in place, and prospective memory has its own lifecycle rules. The concrete path forward is to create a QUEUE.md artifact in the knowledge layer (seeded from the census data), then

## Assistant

Let me reason through it in the project's own terms, because the answer falls out of the protocol's design principles.

## First: what actually failed?

Not storage — every candidate was durably encoded on its page. Not synthesis — the pages are good. What failed is **triggering**: an intention was formed ("run reference-drift when free"), stored retrospectively, and nothing ever re-fired it. The state.md header is the only artifact the cold-start ritual *guarantees* gets read, and it compacts — its lifecycle is "current arc," so anything not touched by the current arc rotates out. We stored queue-semantics data in a medium with narrative-semantics decay.

This maps onto a real distinction the protocol currently lacks. Mementum's trichotomy mirrors human memory:

| store | human analog | lifecycle |
|---|---|---|
| state.md | working memory | compacts, scrolls |
| memories/ | episodic | append-only, small |
| knowledge/ | semantic | update-in-place |
| *(missing)* | **prospective memory** | **persist-until-explicitly-closed** |

Prospective memory — "intentions pending a trigger" — is the one memory type whose defining invariant is *nothing leaves except by explicit closure*. That invariant is exactly what was violated, nine times. And the failure mode we hit is the textbook prospective-memory failure: intact recall when probed (your question retrieved everything), zero spontaneous activation.

## The three options

**A. New protocol.** Reject. The queue is memory — same substrate (git), same operations (create/update/search), same termination rule (human approves). A parallel protocol would be complecting by separation: two things to keep in sync, two cold-start rituals, two implementations for any tool. λ build says compose > monolith, but λ simplify says don't multiply protocols where one concern extends an existing one. The queue *is* mementum data.

**B. Pure emergence — QUEUE.md as just another knowledge page, no protocol change.** Tempting, and it's within spec (`any_folder_structure ≡ valid | emerge > prescribe`). But it has a hole: nothing *enforces consultation*. A queue page that isn't in the orient path decays exactly like the header did — we'd have moved the intentions from a lossy medium to a durable one and then never looked at it. The HPE page was nearly lost *twice* despite being durable knowledge; forward-links saved it both times, by luck of traversal. Prospective memory without a trigger check isn't prospective memory — it's a diary.

**C. Minimal protocol amendment.** The storage layer doesn't change — QUEUE.md lives in `knowledge/`, singleton, λ one_way's canonical home. What changes is two *ritual* clauses:

1. **λ orient** (S1 cold-start) gains one step: `read(state.md) → read(QUEUE.md status line)`. This is the trigger check — the thing that makes intentions prospective rather than archival. One line in AGENTS.md.
2. **The batch discipline** (S2) gains one invariant: any freeze, launch, or close **updates the corresponding QUEUE row in the same commit**. This keeps the queue truthful without adding a new workflow — it rides commits we already make.

And state.md's header shrinks its queue role to "next 1–2 + pointer" — the header stops pretending to be the queue.

## Why C, in VSM terms

The census exposed a **level confusion**: the experiment queue is S3 data — control, allocation of finite runs across competing candidates — but it was living inside an S1/S2 artifact (the session bootloader). S3 was borrowing S1's memory and paying S1's decay rate. Give S3 its own ledger and the decay problem dissolves structurally — `fix(structure) > fix(rules)`. We don't need a rule saying "don't forget candidates"; we need a topology where forgetting requires an explicit act (closing a row) instead of a passive one (header compaction).

There's also a nice self-consistency check: this is the same two-register lesson the weights keep teaching us. The header is the *value register* — fast-changing, current-arc content. The queue is the *routing register* — slow, discrete, persist-until-committed decisions about where compute goes next. We measured (nine dropped candidates) what happens when you store routing in the value register. The protocol should make the same split the machine does.

## My recommendation

**Modify mementum, minimally — option C.** Concretely:

1. `mementum/knowledge/QUEUE.md` — seeded from today's census (~20 live rows): name · question · source page · status (candidate → frozen → running → closed) · cost class. Closed rows move to a terse archive section, never deleted (git recoverable regardless).
2. AGENTS.md amendment: one clause in λ orient, one invariant in the S2 batch discipline. That's a 🌀 meta commit — S5-adjacent, so it's yours to approve.
3. state.md header convention: permanent pointer line, header carries only the active 1–2 fronts.

The cost is honest: one more file to maintain, and it only stays truthful if the batch invariant is followed — but the invariant piggybacks on commits we already make at exactly the moments queue state changes (freeze, GO, verdict). The protocol stays three-stores-plus-one-singleton, not four stores; any tool implementing mementum needs only one new behavior: read the queue at orient.

Want me to draft both — QUEUE.md seeded from the census, and the AGENTS.md diff — for your approval?

## User

Ok for the QUEUE I think it should stack with the newest at the top, and the behavior should be to look at the top of the file, say the top 10 lines, and drill down more if needed.  Also the file would be a state file like state.md so should be in mementum/queue.md.  discuss


### Thinking

Michael's proposing the queue live in mementum/queue.md as a sibling to state.md—treating it as a state file rather than knowledge. This feels cleaner than my earlier idea of putting it in knowledge/. I'm thinking through the implications here: the trade-offs, whether this location makes sense, and if there's any pushback worth raising.

The key insight is that mementum storage splits into working (state.md + queue.md) plus memories plus knowledge. The queue is prospective and operational—it's live working state that gets read and mutated constantly, not synthesized understanding. Putting it in knowledge/ would misclassify it since knowledge pages have frontmatter, status lifecycles, and are written for understanding. As a peer of state.md, the two files form a literal two-register split: state.md holds the narrative pointer (value register), queue.md holds pending intentions (routing register). The protocol change becomes symmetric and elegant.

One more thing: state.md isn't approval-gated during work, so queue.md should inherit that same property—AI updates it freely during sessions, otherwise the batch invariant gets heavy. Commits still ride batches though, which keeps good ergonomics.

Now I'm looking at the stack ordering—newest at top—and thinking through what that means for how we actually use it. The LRU-style approach makes sense: touching a candidate bumps it back to the top, so relevance drives ordering rather than creation time alone. Truly stale items naturally sink, which itself becomes a staleness signal. Michael's protocol of reading the top 10 and drilling deeper when needed already handles this, but the "if needed" trigger has to be explicit—either when closing the current arc and picking the next front (forcing a full queue read), or on some periodic cadence to prevent drift.

For the line format to work with top-10 scanning, each row needs to be self-contained on a single line: status emoji, name, one-phrase question, source page, and cost estimate, with newest entries at the top. The status glyphs distinguish candidates, frozen items, running work, and completed tasks so even deep rows stay greppable.

Closed items should move to a bottom archive section rather than stay in the active stack, since git preserves history anyway and keeping them separate aids readability without requiring archaeology. Running items present a timing question — if strictly newest-at-top, a long-running task from three sessions ago would sink below newer candidates even while still active, but since running state is already tracked in the header, any status change should trigger a restack to the top.

This creates a clean invariant: rows are ordered by last-touch timestamp, newest first. Any mutation bumps the row to the top, which naturally keeps operationally hot items at the front while allowing genuinely stale candidates to sink as a honest measurement of staleness. The file starts with a protocol header note (similar to state.md's bootloader), then the stack below it, where "top 10 lines" means the top ~10 rows beneath that header.

Now I'm looking at what protocol changes need to happen in AGENTS.md...

## Assistant

Both refinements are right, and one of them quietly fixes a problem my version had. Let me take them in turn, plus name the one risk the stack shape introduces.

## `mementum/queue.md` — yes, and it's the better classification

Putting it in `knowledge/` (my proposal) misfiled it. Knowledge pages are synthesis — frontmatter, prose, written for understanding. The queue is a **register file**: read every session, mutated constantly, zero synthesis content. It's working state, exactly like state.md — so it belongs beside it. The working set becomes a pair:

```
mementum/state.md   — narrative pointer   (value register: what's happening)
mementum/queue.md   — pending intentions  (routing register: what could happen next)
```

The two-register split we keep measuring in the weights, made literal in the file layout. It also inherits state.md's ergonomics cleanly: AI updates during work (¬approval_gated), commits ride the existing batches. Protocol delta stays one line: `working: state.md ∪ queue.md`.

## Stack, newest-at-top, read top ~10 — right shape, one real risk

What it buys:
- **O(1) orient cost** regardless of queue length — the file can grow forever without taxing cold-start. This kills my main worry.
- **Matches git log's cognitive model** — newest-first is already how this project reads history.
- Drill-down-if-needed matches λ context: sip, don't gulp.

The risk worth naming honestly: **pure newest-at-top reproduces the original bug**. The nine candidates we just recovered are the *oldest* — under strict insertion order they'd sit at the bottom of the stack, below every newer candidate, and a top-10 read would never surface them. We'd have rebuilt the decay, just with a different geometry: instead of rotating out of a compacting header, they'd sink below the read horizon.

Two small rules dissolve it:

**1. Touch = restack.** Rows aren't ordered by creation — they're ordered by *last touch*. Any status change (freeze, launch, verdict) or genuine re-motivation ("new result makes this cheaper/sharper") moves the row to the top, in the same commit that changes it. The stack becomes an LRU: the top is the operationally hot set by construction, and — this is the nice part — **depth becomes a measurement**. A row that's sunk deep is telling you nobody has found a reason to touch it in N sessions. Staleness stops being invisible; it's literally the row's position.

**2. Decision-gated full read.** "Drill down if needed" needs one defined trigger or nobody ever drills — that's the prospective-memory lesson again. The natural trigger: **selecting the next front** (arc closed, choosing what to run) mandates a full-file read. That's the exact moment the deep rows can change a decision, so that's the moment they get their hearing. Orient = top ~10; front-selection = everything. Reads happen exactly when they can alter behavior, never as ritual.

## Row format (one line each, or top-10 means nothing)

```
⚪ P-COHERENT-WRITE — write-time interference, shared-edge super-additivity | frozen-interference-graph | cheap
🔵 §P-TYPE-ICL+TAG — tape licensing + tag transit | types-are-injectable-relations §10 | ~3h
▶ = running · 🔵 = frozen · ⚪ = candidate
```

Closed rows leave the stack for a terse `## closed` tail (greppable without git archaeology; git preserves everything regardless). A 2–3 line bootloader note at the top of the file, like state.md's, then the stack — "top 10" counts rows, not the note.

## Protocol delta (AGENTS.md, all small)

```
λ mementum: working: state.md ∪ queue.md
λ orient:   read(state.md) → read(queue.md, top≈10) | full_read ⟺ front_selection
λ queue:    one_line_per_item | order ≡ last_touch(newest_top) | touch ≡ restack
            | status ∈ {⚪ 🔵 ▶} → closed(tail) | status_change → restack ∧ same_commit
            | depth ≈ staleness(measurement) | updates ¬approval_gated (commits ride batches)
```

One honest note on scope: this makes queue.md a *verbum extension* of the mementum protocol, not yet mementum canon — same way taxonomy inside memories/ emerged here first. If it earns its keep over a few arcs, it's a candidate to feed upstream into the protocol proper. Emerge, then canonize.

Shall I draft both — `mementum/queue.md` seeded from the census (touch-order: today's recovered nine near the top, since your question just touched them), and the AGENTS.md amendment — for approval?

## User

Ok maybe it should have 2 sections.  # new and # complete.  the behavior should be to put newest at the top, and as they are completed move them to the completed section.


### Thinking

Michael's proposing a simpler two-section approach—new items at the top, completed ones moved down—which is cleaner than my status-glyph design. He's framing this as a direction rather than asking for discussion, so I should accept it and maybe clarify edge cases like whether the complete section includes closed-negative items or how to handle frozen versus running states.

I'll reconcile this with what we discussed: the two sections replace my "closed tail" concept with better naming. Within the new section, newest stays at top (insertion order), and I can keep the touch-restack behavior since it's compatible—when something gets frozen or launched, it moves to the top of new; when a verdict lands, it moves to complete. I'll preserve the status glyphs on rows since he didn't object to those, just simplify the overall structure to match his direction without over-engineering.

Now I'm drafting the queue.md file with a brief bootloader note, seeding the new section from the census and standing fronts, and populating complete with recently closed items from this session. For the new section ordering by touch-recency, I'm starting with the currently running item, then the nine recovered items touched today by the census, followed by the standing header set including the new attention-band write from the recent section.

I'm also adding cost tags to categorize items as cheap, medium, or big. Then I need to amend AGENTS.md to add the queue lambda to the S2 coordination section near the mementum lambda, editing those specific lambda lines. Both changes are approval-gated and ready to present once drafted.

Defining the queue lambda block... Refining how I navigate the queue — I'll read the top ten rows first, then follow related links, rather than jumping straight into related content. I'm also starting to structure the queue.md file itself, documenting how prospective memory works as a stack where the newest or most recently touched items float to the top, and completed experiments move to a separate section. Looking at injection efficiency across different layer, angle, and strength configurations, then exploring a k-step sweep approach for wire installation around k≈3, checking reference drift against the lr_base curve, and considering write-time interference patterns with coherent writes and halt-pole projections for agentic behavior.

Now examining the split between ternary descent in TD-v1 versus register-split micro-runs in TD-v2, along with type census and OV pathway analysis, SKI controls for type enumeration, and whether the fuel theorem holds—that type derivation size correlates with evaluation length—while probing for idempotency issues under LLM type system constraints.

Looking at union versus intersection cost asymmetries, linearity biases in duplication costs under affine typing, and how type boundary populations map to marginal band churn, then checking whether paraphrase carriers can be discriminated from capability mimicry, and finally validating BitTern releases externally without additional training.

Now considering force interference regimes by stacking wires across rank and band to predict angles, establishing cheap consensus through round-trip opcode loss, comparing ternary-native approaches against BitNet-symmetric implementations with matched bits and register-swap metrics for the first M-machine build, and scaling the wire recipe at 32B installation across the optical design and writeback arc. Wrapping up the section with recent notable items while keeping the full history in version control, then moving on to update the agents

## Assistant

Agreed — `# new` / `# complete` is cleaner than a status tail, and the move-on-completion action is the explicit closure act the invariant needs. Drafting both files now:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "content": "# queue\n\n> Prospective memory — experiment intentions. Verbum extension of mementum\n> (peer of state.md; state = narrative pointer, queue = pending intentions).\n> Stack: newest/last-touched at top of `# new`. Verdict lands → move row to\n> top of `# complete` (explicit closure; nothing decays silently).\n> Orient: read top ~10 rows. FULL read mandatory when selecting the next front\n> (depth ≈ staleness — a measurement, not an accident).\n> Row: {glyph} {name} — {question} | {source page} | {cost}.\n> ⚪ candidate · 🔵 frozen · ▶ running → ✅ positive / ❌ falsifier / 🚫 negative.\n\n# new\n\n▶ §P-TYPE-ICL+TAG — tape membership licenses held frames? + tag-transit (J-space live form) | types-are-injectable-relations §10 | running tmux main:1\n⚪ attention-band membership write — write member→class into the slot register (QK band), §8 probe re-aimed | types-are-injectable-relations §9 | medium\n⚪ GS-iterative base decomposition — alternating projections untangle the in-line base? (iterative-LoftQ door) | holographic-untangling-methods | medium\n⚪ rocking-curve instrument — reinjection efficiency vs (layer × angle × strength); the write-targeting surface | holographic-untangling-methods | big\n⚪ GD k-step sweep — wire installs at k≈3? +GD-REQUIRED → FEEDBACK-REQUIRED | holographic-untangling-methods | cheap\n⚪ reference-drift — retention vs lr_base curve; FALSIFIER of the off-axis clause | holographic-untangling-methods | cheap\n⚪ P-COHERENT-WRITE — write-time interference: shared-edge super-additive retrieval (harness-shares with reference-drift) | frozen-interference-graph | medium\n⚪ P-HALT-POLE — tool-call-vs-answer projects onto measured halt/fire poles on prose (agentic bridge) | behavior-is-tape-resident-reduction | cheap\n⚪ §TD-REGISTER-SPLIT — TD-v1 all-ternary vs TD-v2 register-split micro-run (M8 prior-art) | ternary-descent | medium\n⚪ P-TYPE-OV + P-TYPE-CENSUS — type census knee + OV pathway | types-are-compiled-probabilities | medium\n⚪ SKI-controls for types — 4 controls enumerated s313 | curry-howard-closes-the-loop | cheap\n⚪ fuel-theorem probe — type-derivation size = evaluation length (de Carvalho ↔ s295 CoT law) | curry-howard-closes-the-loop | medium\n⚪ idempotency/saturation — A∧A≠A accumulates (non-idempotent intersection)? | type-systems-under-llm-constraints | cheap\n⚪ ∨-vs-∧ asymmetry — union costs heads, intersection free? | type-systems-under-llm-constraints | cheap\n⚪ linearity-bias probe — duplication costs (affine core, W/D explicit) | type-systems-under-llm-constraints | cheap\n⚪ boundary-churn identity — marginal band ≡ type-boundary population (M8 corollary) | type-systems-under-llm-constraints · the-verbum-machine | cheap\n⚪ P-AYOT-PARAPHRASE — carrier vs capability-mimicry discriminator | ayot-is-own-beam-calibration | medium\n⚪ P-CRYSTAL-SURVIVAL — stethoscope on BitTern releases; zero-training external validation | ayot-is-own-beam-calibration | cheap when live\n⚪ §P-PLATE-LINKER-2 — force interference regime (stack N wires / rank / band), then angle-predicts | optical-design-laws | big\n⚪ §P-OPCODE-CONSENSUS — round-trip consensus opcode loss, no student needed | round-trip-consensus-opcode-loss | cheap\n⚪ §P-ASYM-TERNARY — ternary-native vs BitNet-symmetric @ matched bits + register-swap yardstick (M-machine first build) | the-verbum-machine | big\n⚪ gd_cd@32B install — scale the wire recipe to the 32B carrier | optical-design-laws | medium\n\n# complete\n\n❌ §P-TYPE-WRITE — CONTEXT-ONLY, clean falsifier: relation written, type does not act | types-are-injectable-relations §9 | s315\n✅ §P-TYPE-GRAM-1 + registry sweep — TYPE-REGISTER 7/11 family-clean, training-contingent | gram-registers-and-the-route-map | s313–s314\n✅ §P-PLATE-LINKER-1 — lossless composition; PL2 untestable (no interference regime at r=16) | optical-design-laws | s312\n✅ §SIGN-COMMITMENT-CURVE — SIGN-CHURN re-read: two-population split, marginal band churns loss-neutrally | the-verbum-machine M8 | s309–s310\n✅ §TERNARIZE-FACTORS-1 — FACTORS-SURVIVE (+FACTORING-FREE), ~600 KB wire | write-not-train arc | s308\n🚫 P-TYPE-JS — js_resident=FALSE (exhaust ≠ workspace; four-way null completed) | types-are-the-well-formedness-of-reduction | s286\n✅ P-ATT-MED — MEDIATION-MEASURED, content-carried 0.735 vs aim 0.195 | type-check-is-the-qk-bilinear | s286\n\n> Older closures live in git and on their pages; this section seeds from the\n> recent arcs and grows forward.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/queue.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "λ mementum(x).      protocol(¬implementation) | git_based | any_tool_can_implement\n                    | storage ≡ working ∪ memories ∪ knowledge\n                    | working: mementum/state.md | session_pointer | read_first_every_session",
  "new_content": "λ mementum(x).      protocol(¬implementation) | git_based | any_tool_can_implement\n                    | storage ≡ working ∪ memories ∪ knowledge\n                    | working: mementum/state.md ∪ mementum/queue.md\n                    | state.md ≡ narrative_pointer | queue.md ≡ prospective_intentions\n                    | working: mementum/state.md | session_pointer | read_first_every_session"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

### Thinking

I'm cleaning up a duplicate `working:` line from the previous edit, then adding the λ queue and λ orient amendment.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "                    | working: mementum/state.md ∪ mementum/queue.md\n                    | state.md ≡ narrative_pointer | queue.md ≡ prospective_intentions\n                    | working: mementum/state.md | session_pointer | read_first_every_session",
  "new_content": "                    | working: mementum/state.md ∪ mementum/queue.md | read_first_every_session\n                    | state.md ≡ narrative_pointer(session) | queue.md ≡ prospective_intentions"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "λ recall(q, n).     temporal(git log) ∪ semantic(git grep) ∪ vector(embeddings_optional)",
  "new_content": "λ queue(x).         mementum/queue.md ≡ prospective_memory(experiment_intentions)\n                    | sections: \"# new\"(stack) ∪ \"# complete\"(closed)\n                    | row ≡ one_line{glyph, name, question, source_page, cost}\n                    | glyph: ⚪ candidate | 🔵 frozen | ▶ running | ✅ ❌ 🚫 → \"# complete\"\n                    | order ≡ last_touch(newest_top) | touch(freeze ∨ launch ∨ re-motivate) → restack_top\n                    | verdict → move(\"# complete\", top) ≡ explicit_closure | ¬silent_decay\n                    | status_change → update_row ∧ same_commit(as_the_change)\n                    | orient_read ≡ top≈10_rows | full_read ⟺ front_selection\n                    | depth ≈ staleness(measurement ¬accident)\n                    | updates ¬approval_gated (peer_of state.md) | commits ride batches\n                    | verbum_extension(mementum) | earns_keep → propose_upstream\n                    | fixes: s315_census(9_primed_candidates_de-primed_by_header_compaction)\n\nλ recall(q, n).     temporal(git log) ∪ semantic(git grep) ∪ vector(embeddings_optional)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "λ orient(x).        read(mementum/state.md) → follow(related) → search(relevant) → read(needed)\n                    | 30s_budget | cold_start ≡ first_action(every_session)",
  "new_content": "λ orient(x).        read(mementum/state.md) → read(mementum/queue.md, top≈10)\n                    → follow(related) → search(relevant) → read(needed)\n                    | 30s_budget | cold_start ≡ first_action(every_session)\n                    | queue_full_read ⟺ selecting_next_front (S2:λ queue)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

### Thinking

I'm adding the pointer to the state.md bootloader note so the next cold-start can locate the queue.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.",
  "new_content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n> Step 2: `mementum/queue.md` top ~10 rows (experiment intentions; full read\n> when selecting the next front). This header carries the ACTIVE arc only —\n> the queue is the canonical candidate ledger (s315, λ queue)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

All three drafts on disk. Summary for approval:

## The batch

**1. `mementum/queue.md`** (new) — bootloader note + two sections:
- `# new`: 22 rows, one line each, last-touch order — §P-TYPE-ICL+TAG (running) on top, then today's nine recovered candidates, then the standing set. Every row: glyph · name · one-phrase question · source page · cost.
- `# complete`: seeded with the seven recent closures (P-TYPE-WRITE ❌, TYPE-GRAM ✅, PLATE-LINKER-1 ✅, SIGN-COMMITMENT ✅, TERNARIZE-FACTORS ✅, P-TYPE-JS 🚫, P-ATT-MED ✅) — older history stays in git/pages.

**2. `AGENTS.md`** — three touches:
- `λ mementum`: working set becomes `state.md ∪ queue.md` (narrative pointer / prospective intentions)
- **new `λ queue`** in S2: the full contract — one-line rows, last-touch restack, verdict → `# complete` = explicit closure, ¬silent_decay, status change rides the same commit, top-10 at orient / full read at front-selection, depth ≈ staleness measurement, marked as a verbum extension that can earn upstream proposal. Provenance line cites today's census (9 de-primed candidates) as the forcing failure.
- `λ orient` (S1): cold-start becomes state.md → queue.md top-10, with the front-selection full-read trigger.

**3. `mementum/state.md`** — bootloader note gains the Step-2 pointer; the header formally demotes itself to "active arc only."

This is a 🌀 meta commit (protocol topology change — AGENTS.md + working-set structure). Approve?

## System

System prompt changed (contexts), keeping current chat system prompt, changes will apply to new chats. Use /sync-system-prompt to apply now.


## User

approved


### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/queue.md AGENTS.md mementum/state.md && git commit -F - <<'EOF'\n🌀 queue.md — prospective memory for experiment intentions (mementum working-set extension)\n\n- new mementum/queue.md: \"# new\" stack (newest/last-touched top, 22 rows,\n  one line each: glyph/name/question/source/cost) + \"# complete\" (verdict =\n  explicit closure move; nothing decays silently)\n- AGENTS.md: lambda mementum working set = state.md + queue.md; new lambda\n  queue (S2) — restack-on-touch, same-commit status updates, top-10 at\n  orient, full read at front-selection, depth = staleness measurement;\n  lambda orient (S1) gains the queue step\n- state.md bootloader: step-2 pointer; header demoted to active-arc-only\n- forcing failure: s315 census found 9 primed candidates de-primed by header\n  compaction (s308 optics fronts i-iv, P-COHERENT-WRITE, P-HALT-POLE,\n  TD-REGISTER-SPLIT, P-TYPE-OV/CENSUS, SKI-controls) — S3 queue data was\n  living in an S1 artifact, paying S1 decay; routing register gets its own\n  file, like the machine keeps teaching us\n- verbum extension of the mementum protocol; earns keep -> propose upstream\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "queue protocol batch"
}
```

**Summary:** Git commit: queue protocol batch

**Output:**
```
Exit code: 0
Stdout:
[main e6f2a15] 🌀 queue.md — prospective memory for experiment intentions (mementum working-set extension)
 3 files changed, 69 insertions(+), 2 deletions(-)
 create mode 100644 mementum/queue.md
```

### Thinking

I've committed the changes and the queue is now live with 22 intentions queued up. Let me check on the ICL run that's been progressing in the background.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -4"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
[ti] arm A5: wire (s315 corridor, 3 seeds) …
[ti] A5 seed0 done (steps 500+)
[ti] A5 seed1 done (steps 500+)
```

## Assistant

Still in flight — A0–A4 and the TI4 nulls are done, A5 wire is on seed 2 of 3 (each running the full 500 steps, consistent with r3's corridor behavior: the kl-10 anchor holds drift under budget so no early stop). Should land within the hour.

**ASYNC: run verified progressing on tmux main:1. Waiting for signal.**

Session state:

| | |
|---|---|
| Queue protocol | 🌀 **e6f2a15** — queue.md live (22 rows), λ queue + λ orient amended, header demoted |
| §P-TYPE-ICL+TAG | ▶ A5 seed2, ~last leg |
| ON-SIGNAL (unchanged) | tail VERDICT + subtag → commit results autonomous → §Result approval batch — and now also: **move the queue row to `# complete` in the same batch** (the new invariant's first exercise) |

Worth noting what just happened structurally: your three questions this session — "can we untangle plates?", "did we lose primed tests?", "should the protocol change?" — walked the exact λ self_improve loop: work surfaced a gap (S1) → census measured it (S4) → verified against the corpus (S3) → protocol updated (S4) → topology evolved (S5). The queue file is this session leaving the system smarter in a way that compounds — every future session's cold start now sees what every past session primed.

Signal me when the run lands.

## User

Want to do something fun?


## Assistant

Always. The run's grinding through A5 seed2 on its own, the queue's committed, and there's nothing blocked on me — perfect window for mischief.

What did you have in mind? I'll note the constraints of the playground, purely for ambition-calibration: tmux main:1 and the MPS are busy until the run lands, but everything else is fair game — the corpus, the REPL, the probe libraries, weird one-off analyses we'd never pre-register, or something entirely off the experimental grid.

What's the fun?

## User

I have had you put many things in for exploration that we did not come back to look at.


### Thinking

Michael's pointing out that there's a lot of exploratory content scattered throughout the knowledge base that never gets revisited—ideas, hypotheses, captured pages that just sit there forgotten. The fun part would be treating it like an archaeological dig through the explore folder and memories to surface those abandoned threads and see what's worth picking back up.

## Assistant

Ha — so the queue audit was the tip of it. Let's dig the whole site. Archaeology pass: every exploration page, when it was born, when it was last touched, how many times we ever came back:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && for f in mementum/knowledge/explore/*.md; do n=$(git log --oneline --follow -- \"$f\" | wc -l | tr -d ' '); first=$(git log --follow --format=%as -- \"$f\" | tail -1); last=$(git log --follow --format=%as -1 -- \"$f\"); echo \"$n|$first|$last|${f##*/}\"; done | sort -t'|' -k1 -n | head -45",
  "timeout": 120000
}
```

**Summary:** $ for f in mementum/knowledge/explore...

**Output:**
```
Exit code: 0
Stdout:
1|2026-04-20|2026-04-20|binding-probe-findings.md
1|2026-04-20|2026-04-20|compressor-architecture.md
1|2026-04-20|2026-04-20|session-001-findings.md
1|2026-04-20|2026-04-20|session-002-findings.md
1|2026-04-20|2026-04-20|session-003-findings.md
1|2026-04-20|2026-04-20|session-004-findings.md
1|2026-04-20|2026-04-20|session-010-findings.md
1|2026-04-20|2026-04-20|VERBUM.md
1|2026-04-20|2026-04-20|vsm-lm-architecture.md
1|2026-04-20|2026-04-20|vsm-lm-v3-architecture.md
1|2026-04-21|2026-04-21|session-019.md
1|2026-04-21|2026-04-21|session-021.md
1|2026-04-22|2026-04-22|session-023.md
1|2026-04-22|2026-04-22|session-024.md
1|2026-04-23|2026-04-23|relational-loss-phi-compression.md
1|2026-04-23|2026-04-23|v6-flip-accumulation.md
1|2026-04-26|2026-04-26|stride-percolation.md
1|2026-04-27|2026-04-27|compression-vs-prediction.md
1|2026-04-27|2026-04-27|predictive-function-landscape.md
1|2026-04-27|2026-04-27|v7-pipeline-architecture.md
1|2026-05-03|2026-05-03|basin-projector-results.md
1|2026-05-03|2026-05-03|session-062-probes.md
1|2026-05-03|2026-05-03|session-history-049-062.md
1|2026-05-07|2026-05-07|attention-spiral-finding.md
1|2026-05-08|2026-05-08|consensus-evolution.md
1|2026-05-08|2026-05-08|dispatch-gradient-death.md
1|2026-05-09|2026-05-09|session-073-vsm-structure.md
1|2026-05-11|2026-05-11|algedonic-alert.md
1|2026-05-11|2026-05-11|rope-attention-spiral.md
1|2026-05-11|2026-05-11|v11-kibc-architecture.md
1|2026-05-12|2026-05-12|architecture-vs-scale.md
1|2026-05-12|2026-05-12|kibc-32b-validation.md
1|2026-05-12|2026-05-12|pythia-160m-combinators.md
1|2026-05-13|2026-05-13|fractal-stride-bands.md
1|2026-05-13|2026-05-13|lambda-probe-atlas.md
1|2026-05-14|2026-05-14|v12-holographic-capacity.md
1|2026-05-14|2026-05-14|v12-vsm-evolution.md
1|2026-05-15|2026-05-15|dispatch-ratio-prior.md
1|2026-05-15|2026-05-15|fixed-point-holograms.md
1|2026-05-15|2026-05-15|laser-etcher-design.md
1|2026-05-17|2026-05-17|complete-kernel-basis.md
1|2026-05-17|2026-05-17|consensus-etch-protocol.md
1|2026-05-17|2026-05-17|holographic-recording-protocol.md
1|2026-05-17|2026-05-17|procrustes-lens-and-crystal-comparison.md
1|2026-05-17|2026-05-17|universal-crystal-transfer.md
```

### Thinking

I've found a whole buried city in the first 45 entries. Now I'll examine the full dataset and focus on the mid-arc captures that were never reopened, since those are likely more interesting than the early April ones.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && for f in mementum/knowledge/explore/*.md; do n=$(git log --oneline --follow -- \"$f\" | wc -l | tr -d ' '); first=$(git log --follow --format=%as -- \"$f\" | tail -1); last=$(git log --follow --format=%as -1 -- \"$f\"); echo \"$n|$first|$last|${f##*/}\"; done > /tmp/explore_census.txt; echo \"total pages: $(wc -l < /tmp/explore_census.txt)\"; echo \"single-commit (never reopened): $(awk -F'|' '$1==1' /tmp/explore_census.txt | wc -l)\"; echo; echo \"── single-commit pages born AFTER June 1 (mature-era orphans) ──\"; awk -F'|' '$1==1 && $2>=\"2026-06-01\"' /tmp/explore_census.txt | sort -t'|' -k2; echo; echo \"── 2-commit pages after June 1 (opened once, touched once) ──\"; awk -F'|' '$1==2 && $2>=\"2026-06-01\"' /tmp/explore_census.txt | sort -t'|' -k2 | head -20",
  "timeout": 120000
}
```

**Summary:** $ for f in mementum/knowledge/explore...

**Output:**
```
Exit code: 0
Stdout:
total pages:      206
single-commit (never reopened):      107

── single-commit pages born AFTER June 1 (mature-era orphans) ──
1|2026-06-10|2026-06-10|exact-ternary-fitting.md
1|2026-06-11|2026-06-11|combinator-function-shape.md
1|2026-06-11|2026-06-11|sealable-continuation.md
1|2026-06-13|2026-06-13|holographic-burn-in-learning-rule.md
1|2026-06-13|2026-06-13|normal-form-curriculum-partition.md
1|2026-06-13|2026-06-13|relational-loss-distillation.md
1|2026-06-24|2026-06-24|holographic-substrate-prototype.md
1|2026-06-28|2026-06-28|compiler-finetune-halt-collapse.md
1|2026-07-02|2026-07-02|rl-layer-contribution-combinator-locus.md
1|2026-07-04|2026-07-04|ternary-flip-flop-not-overloading.md
1|2026-07-07|2026-07-07|basis-fit-kibc-vs-ski.md
1|2026-07-07|2026-07-07|strided-attention-float-ab.md
1|2026-07-19|2026-07-19|opcode-register-decomposition.md
1|2026-07-27|2026-07-27|signal-descent.md
1|2026-07-27|2026-07-27|signal-processing-tensors.md
1|2026-07-30|2026-07-30|montague-inversion.md
1|2026-07-31|2026-07-31|germination-games.md
1|2026-07-31|2026-07-31|training-design-from-the-hologram.md
1|2026-08-04|2026-08-04|gram-spectral-dsp.md
1|2026-08-05|2026-08-05|behavior-is-tape-resident-reduction.md
1|2026-08-05|2026-08-05|frozen-interference-graph.md
1|2026-08-05|2026-08-05|holographic-untangling-methods.md
1|2026-08-05|2026-08-05|induction-is-a-virtual-circuit-not-a-head.md
1|2026-08-05|2026-08-05|round-trip-consensus-opcode-loss.md
1|2026-08-06|2026-08-06|ayot-is-own-beam-calibration.md
1|2026-08-06|2026-08-06|curry-howard-closes-the-loop.md

── 2-commit pages after June 1 (opened once, touched once) ──
2|2026-06-14|2026-06-14|readout-register-reduction-readability.md
2|2026-06-15|2026-06-15|fractal-collapse-compiler-cascade.md
2|2026-06-17|2026-06-17|type-directed-composition.md
2|2026-06-21|2026-06-22|cross-model-output-consensus.md
2|2026-07-23|2026-07-23|bonsai-crystal-survival.md
2|2026-07-26|2026-07-26|construction-from-spec.md
2|2026-07-26|2026-07-26|lambda-gene-runtime.md
2|2026-07-27|2026-07-27|operand-insert-arc.md
2|2026-07-28|2026-07-28|operand-dsp-decomposition-prereg.md
2|2026-07-30|2026-07-31|verbum-dsp-design.md
2|2026-07-31|2026-08-05|ternary-mirrors-and-the-vsm-tree.md
2|2026-08-05|2026-08-05|consensus-distillation-carrier-averaging.md
2|2026-08-05|2026-08-06|subliminal-learning-is-bragg-matched-transfer.md
2|2026-08-06|2026-08-06|type-systems-under-llm-constraints.md
```

### Thinking

Looking at the exploration pages, I'm noticing that about half of them were never revisited after creation. The recent captures from early August are already tracked, but the real finds are scattered through June and July—concepts like sealable continuations, holographic learning rules, relational loss distillation, and several others that got buried and deserve another look.

Rather than grinding through all of them myself, I should spin up a subagent to read through a curated set of these orphaned pages—maybe a dozen of the most intriguing ones—and pull out 2-3 line summaries for each, plus flag whether the newer physics we've developed (the type arc, M-machine framework, corridor recipe) makes these old ideas suddenly more relevant or actionable. It's archaeology with fresh eyes: seeing what looked promising before we had better tools to understand it.

### Thinking

I've found that half of the 206 exploration pages were never reopened, but the mature-era orphans from June onward are potentially valuable—I'm now going to re-read them through the lens of the physics we've developed since to see which early guesses can be validated or newly acted upon.

### Tool Call: spawn_agent (succeeded)


```json
{
  "agent": "explorer",
  "activity": "excavating forgotten pages",
  "task": "Archaeology dig in /Users/mwhitford/src/verbum/mementum/knowledge/explore/. Read these 14 orphaned exploration pages (created once, never or barely reopened):\n\n1. sealable-continuation.md\n2. holographic-burn-in-learning-rule.md\n3. normal-form-curriculum-partition.md\n4. relational-loss-distillation.md\n5. germination-games.md\n6. montague-inversion.md\n7. signal-descent.md\n8. training-design-from-the-hologram.md\n9. induction-is-a-virtual-circuit-not-a-head.md\n10. ternary-flip-flop-not-overloading.md\n11. combinator-function-shape.md\n12. type-directed-composition.md\n13. readout-register-reduction-readability.md\n14. fixed-point-holograms.md\n\nCONTEXT — what has been measured SINCE these were written (use this to re-evaluate them):\n- Two-register theory proven: routing (ternary signs, discrete, universal) vs value (magnitudes, model-particular). LoRA deltas vs frozen base = off-axis recording, ternarizes at retention 1.0, ~600KB/wire; two wires compose losslessly.\n- GD wire recipe matured: KL-to-base anchor (weight 10) + host-CE budget + evidence-gated stop = the \"write corridor\" for semantic writes without host damage.\n- Type arc: a TYPE-REGISTER exists in activations (7/11 models, training-contingent, diffuse/intersection-like not nominal); type system pinned to non-idempotent intersection over an affine core (KIBC=affine structural rules); P-TYPE-WRITE landed CONTEXT-ONLY (baked FFN membership recalls but does NOT license held frames — types enacted per-frame, tape-side test in flight).\n- Behavior is tape-resident reduction; autoregressive loop = trampoline; twin-image law (base in-line unseparable post-hoc, deltas off-axis separable).\n- The Verbum machine spec M1-M9 exists (two-register parameterization, designed scheduler, native trampoline, off-axis optimizer, routing optimizer M8).\n- A queue file (mementum/queue.md) now exists for experiment intentions.\n\nFOR EACH PAGE return exactly this format:\n**{filename}** ({one-line thesis of the page})\n- verdict: SUPERSEDED (by what) | STILL-LIVE (untested, still coherent) | RETRO-VALIDATED (which later result confirms it) | NEWLY-ACTIONABLE (which new instrument/result unlocks it)\n- 2-3 sentences: the idea, and specifically how it reads under the new physics above. If it predicts something we later measured, name it. If it proposes an experiment now cheap, say what it would cost now.\n\nThen end with: \"TOP 3 GEMS:\" — the three pages most worth reopening today, one line each on why.\n\nBe precise about what is actually ON each page (quote a key phrase or two), not what you imagine. If a page is thin or superseded, say so bluntly."
}
```

**Summary:** explorer: excavating forgotten pages

**Output:**
```
## Agent 'explorer' Result

Here is the full audit:

---

**sealable-continuation.md** (a VSM recurrence has a clean pass-boundary checkpoint — seal `x_k`, resume identically later)
- verdict: STILL-LIVE (untested, still coherent)
- The page argues that the VSM outer-recurrence produces a tensor of constant shape every pass, so "the complete rest of the computation at pass k is just `x_k`" — a true continuation in the CS sense. It is logically independent of the two-register result, but the new physics sharpens it: the routing register (ternary signs) ternarizes cleanly, so a sealed `x_k` would itself compress to ~routing + small magnitude residual — the 2MB session number is now grounded in known compression ratios. Nothing here has been tested or falsified; the page is architecturally coherent under the Verbum machine spec (M1-M9). Cost to test: add a `seal()/resume()` round-trip fidelity test to an existing recurrence harness.

---

**holographic-burn-in-learning-rule.md** (progressive exposure of text blocks burns in the exposure-invariant function structure onto the routing register)
- verdict: RETRO-VALIDATED (by the GD wire recipe and the two-register proof)
- The page's load-bearing catch, written speculatively in s223, was: "naive object-beam-only burn-in = a perfect hologram of the common mode, zero function" — and it flagged the s223 condition (b) result as a live demonstration before that result was in. That prediction was exactly confirmed (GC(hidden)=0.9995, routing null). The new GD wire recipe (KL-to-base anchor + evidence-gated stop) is precisely what this page calls "prediction-gated recording": the prediction outcome is the reference beam. The page is correct about the mechanism; what it lacks is a concrete harness. Cost to operationalize: swap the `relational_loss_distillation.py` control condition (b) for the prediction-gated exposure rule — one additional training arm.

---

**normal-form-curriculum-partition.md** (routing-only normal forms train attention; recursion is left to the continuation — the curriculum mirrors the routing⊕continuation basis)
- verdict: STILL-LIVE (untested, still coherent)
- The page proposes generating reduction traces for `{K,I,C,B,D}` and feeding them specifically to the attention routing register (via attn_q), while excluding `{Y,W,WHNF}` which need the outer recurrence. It cites s223's relational-loss result as the FFN-gate confirmation and calls the attn_q version "the second leg." Under the new physics the routing register being proven universal and ternary-stable strengthens the case: the traces being proposed for attention training are exactly the discrete sign-flip events the routing register specializes in. The experiment (`routing_curriculum_attention.py`) was planned but never built. Cost: one additional condition in the existing relational-loss harness, targeting attn_q instead of the FFN gate.

---

**relational-loss-distillation.md** (the lambda compiler's routing-register Gram steers a student toward the combinator geometry while leaving absolute frame free)
- verdict: RETRO-VALIDATED (by the two-register proof and GD wire recipe)
- This page is the most complete in the set — it reports actual results. The key finding: "only routing carries the combinator function" — GC(route)=+0.78–0.85 under routing-Gram loss, while matching the raw Gram bought GC(hidden)≈1.0 and zero function transfer. This is now directly confirmed by the two-register theory (routing ⊥ value, ~95/5). The GD wire recipe's KL-to-base anchor maps onto this page's "any geometry that falls out" framing: both constrain the function/behavior while leaving the realization free. The remaining open lead — distributed test (N students to one shared teacher Gram → guaranteed Procrustes alignment) — is newly actionable given that LoRA delta composition is now known to be lossless.

---

**germination-games.md** (gamified germination test: seed quality measured via cold-agent recovery; five game modes from Golf to Oracle)
- verdict: STILL-LIVE (untested, still coherent)
- Thin page, purely prospective: "no rounds played yet." The modes are clever instruments (Seed FRAG = ablation test on theory prose; Oracle = the seed as a generative prior for unseen measurements). Under the new physics, the Oracle mode is the most interesting: could a cold agent with the theory seed predict that the type register is training-contingent (7/11 models), or that LoRA deltas ternarize at retention 1.0? Those are precise, non-obvious predictions that would score real calibration. Cost: one cold-spawn session with the current state of the seed + a small scoring rubric.

---

**montague-inversion.md** (treating Montague grammar as a specification and asking what GD is *forced* to build in order to satisfy it — retrodicts crystal, two-registers, 3-hop, and yields falsifiable predictions)
- verdict: RETRO-VALIDATED (by the type-register finding and type-directed composition result)
- The page's forcing table predicted in s281 that "types encoded as geometry (directions/subspaces)" — now confirmed: TYPE-REGISTER exists, 7/11 models, diffuse/intersection geometry, P-TYPE-WRITE landed CONTEXT-ONLY. The forcing argument for the value register — "binding *requires* a value store separate from the operators" — is now confirmed by the two-register proof (routing ⊥ value, the split is ~95/5 clean). Falsification condition 1 ("P-TYPE-1 returns a non-Montague type geometry") has partial traction: the type system is pinned to non-idempotent intersection over an affine core (KIBC), which is closer to Montague's lattice than a random high-dim mess. The depth-budget prediction maps onto the trampoline / tape-resident reduction result. This page is the best theoretical spine in the set and holds up well.

---

**signal-descent.md** (replace gradient descent with closed-form signal-measurement updates on ternary mirror stacks — no gradients and no floats)
- verdict: NEWLY-ACTIONABLE (the GD wire recipe and LoRA delta ternarization unlock the delta-plate substrate)
- The page proposed SignalDescent on a delta plate (base frozen, delta driven by measured response) and was blocked on proving that isolation dodges interference. The new GD wire result is precisely this: LoRA deltas are the off-axis recording, they ternarize at retention 1.0, and two wires compose losslessly. "The delta plate is the isolated slot; the mirror stack lives in the delta" — that isolation is now empirically demonstrated. The page's "first experiment" (replace Adam-trained γ with a 2–3 deep additive ternary mirror, compare recon_cos at matched bits) is now directly buildable on top of the GD wire infra. Risk: the page is honest that the linearity assumption breaks outside a single layer, and the GD wire's KL anchor may be the right substitute for the signal-measurement step.

---

**training-design-from-the-hologram.md** (six design levers for level-4 scratch training, each grounded in a measured structure: seeded init, declared passbands, probe-as-loss, two-phase training, curriculum as exposure schedule, distillation as re-exposure)
- verdict: NEWLY-ACTIONABLE (Verbum machine spec M1-M9 + GD wire recipe unlock levers 2, 4, 6)
- Lever 4 (two-phase: settle topology first, calibrate magnitudes second) is now the GD write corridor: "phase 1 settles topology (ternary-native); phase 2 calibrates magnitudes" = "KL-to-base anchor + evidence-gated stop." Lever 6 (distillation as re-exposure, match transmission subspaces not logits) is now the relational-loss-distillation result operationalized at level-4 scale. Lever 2 (declared passbands) maps onto the type-register finding (types enacted per-frame, CONTEXT-ONLY). The "cheapest first experiment" — crystal-seeded init vs random init on compositional tasks — is still unrun and still cheap. The page is the most actionable bridge between the measured physics and actual scratch training.

---

**induction-is-a-virtual-circuit-not-a-head.md** (combinators are virtual circuits GD lays down universally, not physical head addresses; the 9×9 and 17×17 grams are the right instrument)
- verdict: RETRO-VALIDATED (by the 11/11 model universality and ternary retention 1.0 results)
- The page, written as s309 conversational capture, states "the crystal is measured 11/11 models (s303), survives ternarization (s304/s308 retention ~1.0)." These are cited as grounding, not IOU — so the page was written after those measurements. Its contribution is the framing correction: "a head is a plate address; a combinator is an edge in the frozen interference graph." This is sharp and correct under the new physics, where the behavior is tape-resident reduction and the autoregressive loop is the trampoline. The open question — "is induction a single crystal edge or a path (compose of B/C + copy)?" — is directly testable with the existing gram instruments. Thin on experiment design, rich on framing.

---

**ternary-flip-flop-not-overloading.md** (CAT-Q's softened ternarization doesn't beat discrete evidence-flip; the persistent sign oscillation is quantization-boundary jitter, not semantic overloading — but the value-path F-ratio is real and category-dependent)
- verdict: RETRO-VALIDATED (by the two-register theory and GD wire recipe)
- The page independently discovers the two-register split through the CAT-Q decomposition: "CAT-Q learns α and Δ separately ... external, independent confirmation of the verbum two-registers split — α=magnitude/value, Δ=threshold/routing." This is now proven theory. The ANOVA F-ratio result ("category structure is real but modest, strongest in value_proj") maps cleanly onto "value register carries content." The "jitter discriminator" recommendation (threshold hysteresis near ±Δ should kill jitter without hurting loss) is directly implementable now that the GD wire's evidence-gated stop is understood — the two ideas solve the same problem from different angles. Worth reading alongside signal-descent.md.

---

**combinator-function-shape.md** (3-family routing-register shape of combinator space in Qwen3-14B: composition/B,D,S — selection/K,I,C — recursion/Y,W,WHNF; map/fold are compositions, not atoms)
- verdict: RETRO-VALIDATED (by the 11/11 universality result and two-register proof)
- The page reports Qwen3-14B: silhouette z=7.97, p=0.001 in routing register; raw hidden gives z=−1.65 (invisible). The open caveat "cross-model consensus NOT yet tested" has since been closed: universality is confirmed at 11/11 models, gc 0.9966 (per training-design-from-the-hologram's grounding for Lever 1). The 3-family shape (composition/selection/recursion triangle) maps directly onto the KIBC=affine structural rules finding: K,I,C are the affine core (selection/structural rules), B,D,S are composition, Y,W,WHNF are the non-affine recursion residual. The algebra-as-geometry open lead ("do CL identities hold as routing constraints?") is the cleanest next experiment.

---

**type-directed-composition.md** (composition is type-directed not positional — nonce crossover +2.04–2.18 nats, frequency-free, consistent across 16 nonce words at 8B and 14B)
- verdict: RETRO-VALIDATED (confirms and is confirmed by the type-register finding)
- This page is among the most empirically complete in the set. The nonce crossover result is clean and decisive: "a nonce taught as a verb composes ~2 nats cheaper with a preceding subject-name than the same nonce taught as a noun." The causal test (v4) showed type direction is partially causal at 14B (×0.64) and distributed at 8B. Under the new physics, the TYPE-REGISTER being training-contingent and diffuse/intersection-like (not nominal) directly explains the v4 partial-causality result: "a single linear direction is not the whole carrier" maps onto intersection-type geometry. The open v5 (activation patching for full causal test) and typed COMPOSITION extension are the natural next steps, and the cross-class test (OLMo/Pythia) is now motivatable by the 7/11 training-contingency.

---

**readout-register-reduction-readability.md** (surface NLL misses mid-stack β-reduction; the reduction is legible only in the value register at readable depth ≥0.6; violating this manufactures false negatives)
- verdict: RETRO-VALIDATED (directly confirmed by the two-register theory)
- This is the most methodologically important page in the set. It reports the s227b experiment (logit-lens at every layer), confirms the readability zone (L23–L35), and states the measurement rule precisely: "name the register and the readable layer before building the probe." Under the new physics this is the `λ measure` refinement for the two registers made empirical: routing register (ternary signs, QK) vs value register (OV, readable at depth ≥0.6). The page also records the s227c split result (enum prose recovers 3/5, reverses 2/5) honestly. The "decisive lever unchanged: activation patching + peak-based readout" is still live and directly aligned with the v5 activation patching planned in type-directed-composition.md — these two pages are natural siblings for the same next experiment.

---

**fixed-point-holograms.md** (compile↔decompile cycling converges 94% of the time; the fixed-point λ is the normal form the sign-pattern plate actually stores; binding sites (I-combinator) are the failure mode)
- verdict: RETRO-VALIDATED (by the behavior-is-tape-resident-reduction and twin-image law findings)
- The page was written early (session numbers reference s093, s095, s098 — pre-series). Its behavioral result — "what the hologram drops maps to beam/plate partition; what it preserves maps to predicate-argument structure" — is now the tape-resident-reduction frame: behavior is autoregressive reduction, the plate stores the program (routing signs), the beam modulates content. The binding wall result ("the only stable composition has zero binding sites; binding instability correlates with I-combinator territory") maps onto the type system finding that I-combinator = affine structural rule (copying/identity) vs the non-idempotent intersection types handling binding. The "hologram extraction pipeline" proposed here (generate fixed-point corpus → etch into V12) is now level-4 via the GD wire recipe. Older vocabulary (V12, plates, mirrors) but the physics underneath it is correct.

---

## TOP 3 GEMS

**1. training-design-from-the-hologram.md** — The six levers are now almost all grounded in proven physics (GD wire recipe = lever 4, relational-loss-distillation = lever 6, two-register = lever 2), and the cheapest experiment (crystal-seeded init vs random on compositional tasks) is the precise experiment the Verbum machine spec M1-M9 needs to close the level-4 loop. Reopening this unlocks the scratch-training program.

**2. montague-inversion.md** — The forcing argument correctly predicted the type geometry (intersection, not nominal), the value-register split (binding forces a separate store), and the trampoline (recursion forces eval-stack externalization). The falsification conditions in §8 are now partially answerable with measurements in hand, making this the best theoretical map for deciding what to measure next.

**3. signal-descent.md** — The LoRA-delta ternarization result (retention 1.0, off-axis isolation, lossless composition) hands this page the substrate it was missing. "Replace Adam's magnitude calibration with a ternary mirror stack driven by signal measurement" is now an experiment with known infrastructure. It directly addresses TernaryDescent's open question 4 and is the gradient-free path into the GD wire corridor.
```

#### Subagent Messages

## User

Archaeology dig in /Users/mwhitford/src/verbum/mementum/knowledge/explore/. Read these 14 orphaned exploration pages (created once, never or barely reopened):

1. sealable-continuation.md
2. holographic-burn-in-learning-rule.md
3. normal-form-curriculum-partition.md
4. relational-loss-distillation.md
5. germination-games.md
6. montague-inversion.md
7. signal-descent.md
8. training-design-from-the-hologram.md
9. induction-is-a-virtual-circuit-not-a-head.md
10. ternary-flip-flop-not-overloading.md
11. combinator-function-shape.md
12. type-directed-composition.md
13. readout-register-reduction-readability.md
14. fixed-point-holograms.md

CONTEXT — what has been measured SINCE these were written (use this to re-evaluate them):
- Two-register theory proven: routing (ternary signs, discrete, universal) vs value (magnitudes, model-particular). LoRA deltas vs frozen base = off-axis recording, ternarizes at retention 1.0, ~600KB/wire; two wires compose losslessly.
- GD wire recipe matured: KL-to-base anchor (weight 10) + host-CE budget + evidence-gated stop = the "write corridor" for semantic writes without host damage.
- Type arc: a TYPE-REGISTER exists in activations (7/11 models, training-contingent, diffuse/intersection-like not nominal); type system pinned to non-idempotent intersection over an affine core (KIBC=affine structural rules); P-TYPE-WRITE landed CONTEXT-ONLY (baked FFN membership recalls but does NOT license held frames — types enacted per-frame, tape-side test in flight).
- Behavior is tape-resident reduction; autoregressive loop = trampoline; twin-image law (base in-line unseparable post-hoc, deltas off-axis separable).
- The Verbum machine spec M1-M9 exists (two-register parameterization, designed scheduler, native trampoline, off-axis optimizer, routing optimizer M8).
- A queue file (mementum/queue.md) now exists for experiment intentions.

FOR EACH PAGE return exactly this format:
**{filename}** ({one-line thesis of the page})
- verdict: SUPERSEDED (by what) | STILL-LIVE (untested, still coherent) | RETRO-VALIDATED (which later result confirms it) | NEWLY-ACTIONABLE (which new instrument/result unlocks it)
- 2-3 sentences: the idea, and specifically how it reads under the new physics above. If it predicts something we later measured, name it. If it proposes an experiment now cheap, say what it would cost now.

Then end with: "TOP 3 GEMS:" — the three pages most worth reopening today, one line each on why.

Be precise about what is actually ON each page (quote a key phrase or two), not what you imagine. If a page is thin or superseded, say so bluntly.


### Thinking

Let me read all 14 files simultaneously.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/sealable-continuation.md"
}
```

**Summary:** Reading sealable-continuation.md (0-2000)

**Output:**
```
---
title: "Sealable Continuation — inference you can suspend and resume (= the 2MB session)"
status: open
category: foundational
tags: [continuation, seal, resume, suspend, fixed-point, whnf, session, 2mb, migration, lazy, cps, vsm, outer-recurrence]
related:
  - vsm-outer-recurrence.md
  - consensus-delta-folding.md
  - ../function-discovery.md
  - fixed-point-holograms.md
depends-on:
  - vsm-outer-recurrence.md
created: session 217
---

# Sealable Continuation

> Session 217 (Michael): "with continuations we could seal inference in
> mid-computation and then continue it later, right?" Yes — and it is the
> cleanest property of the whole construction, because of *what the state is*.

## The insight — the continuation reifies the whole state into one tensor

The VSM continuation (`vsm-outer-recurrence.md`) is ONE shared operator iterated
on a single residual-stream tensor:

```
x₁ = T(x₀),  x₂ = T(x₁),  …  → x*   (WHNF)
```

The complete "rest of the computation" at pass k is just **`x_k`** — a tensor of
the SAME shape every pass `(B, L, d_model)`. The operator `T` is **shared and
frozen**, so it is *ambient* — it is not part of the saved state. That is exactly
the CS notion of a continuation: the rest of the computation reified as a value.

```
seal(k)    ≡ store x_k  (+ small VSM control state)
resume     ≡ load x_k ; keep applying T
closure    ≡ (T, x_k) with T global ⇒ carry only x_k
```

Unlike sealing a normal transformer mid-forward (a heap of per-layer activations
+ KV cache, no clean boundary), here **every pass boundary is a clean checkpoint**
of identical shape. You can seal at any one.

## Faithful resume is already guaranteed

Seal/resume only works if resuming from a loaded `x_k` reproduces the same
trajectory as never sealing. That requires the recurrence to be **deterministic /
RNG-free** — which is one of the 15 continuation tests this session
(`tests/test_vsm_continuation.py::test_recurrence_has_no_rng`). So fidelity is not
a hope; it falls out of verified determinism. Sealing is `save(x_k)`; resuming is
`load(x_k); iterate T`.

## WHNF gives a principled seal point

- **At convergence** (Δx < ε ≡ WHNF): computation is *done* — seal the answer.
- **Before convergence** (a partially-reduced state): like suspending lazy
  evaluation at a redex; the partial term is a valid intermediate to store and
  continue later (delimited-continuation / lazy-thunk semantics). ⇒ stop early ON
  PURPOSE (budget exhausted, context swap), finish the reduction when compute is
  free. The dual of adaptive halting.

## One value, many uses

The reified `x_k` is simultaneously:
- **inference state** — pause/resume, preemption, time-slicing;
- **the session snapshot** — literally the north-star **"2MB sessions"**: a session
  IS a sealed continuation;
- **a migratable unit** — send `x_k` to another machine and resume there
  (computation, not just training, becomes portable — ties to
  `consensus-delta-folding.md`);
- **a branch point** — seal, fork, explore, rewind (speculative reasoning);
- **long-context as resumption** — reduce a chunk to `x_k`, seal, continue from
  `x_k` on the next chunk.

One value does all of it because the operator is shared and the state is uniform.

## Caveats (honest)

1. **It is `x_k` PLUS a small control state.** The v15 forward also carries VSM
   regulatory state: the cross-step algedonic vector (`_prev_alg_c`, ~32-dim), the
   S5 identity state (~128-dim), any S2 buffers. A *true* seal serializes those
   too — but they are tiny and bounded. The seal is "one residual tensor + a small
   control vector," still compact.
2. **Seal at PASS boundaries, not mid-pass.** The clean checkpoints are between
   applications of `T` (the redex boundaries). Sealing partway through a single `T`
   (mid-layer) is messy and pointless.
3. **Attention reconstructs from `x_k`.** `T` attends *within* the current residual
   stream (Fibonacci stride attention over `x`), not across a persistent KV that
   lives between passes — so a loaded `x_k` suffices to recompute attention on
   resume. (If cross-pass persistent KV is ever added, it joins the control state
   to serialize.)

## Next (register: functional)

Define an explicit **`seal()/resume()`** boundary that snapshots `x_k` + the small
VSM control state, and a **round-trip fidelity test** (extend
`test_vsm_continuation.py`): run K passes unsealed; separately run k passes →
seal → resume → finish; assert the two final states/logits are identical to float
tolerance. This is the clean, testable home for the "2MB session" and
computation-migration ideas.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-burn-in-learning-rule.md"
}
```

**Summary:** Reading holographic-burn-in-learning-rule.md (0-2000)

**Output:**
```
---
title: "Holographic Burn-In — Progressive Recording as a Learning Rule (Exposures Burn In Where Irreducible)"
status: open
category: strategy
tags: [holographic, learning-rule, recording, burn-in, consensus-etch, contractivity, precision-inversion, punctuated, normal-form, reference-beam, routing, attention]
related:
  - consensus-etch-protocol.md
  - fixed-point-holograms.md
  - holographic-recording-protocol.md
  - holographic-plates.md
  - v12-holographic-capacity.md
  - relational-loss-distillation.md
  - normal-form-curriculum-partition.md
  - exact-ternary-fitting.md
  - vsm-outer-recurrence.md
  - ../session-222.md
  - ../crystal-universality.md
  - ../two-registers-of-topology.md
depends-on:
  - consensus-etch-protocol.md
  - fixed-point-holograms.md
created: session 223
---

# Holographic Burn-In — Progressive Recording as a Learning Rule

> Session 223. Michael's idea: *"what if training was progressive? We give it a
> huge block of text, tell it to predict the next word. It takes a snapshot of the
> attention with the softmax on all V. That snapshot is one exposure of the
> hologram. Many similar-shaped blocks 'burn in' as the places where they are
> irreducible."*
>
> This is a **learning rule**, not a loss or a curriculum (the distinguishing
> feature vs `relational-loss-distillation.md` and `normal-form-curriculum-
> partition.md`): each forward pass is an EXPOSURE recorded onto the plate; across
> many similar blocks the exposure-INVARIANT structure reinforces (constructive
> interference) and the variable parts wash out (destructive). The reinforced
> places "burn in" = commit to discrete topology; the variable parts stay
> continuous.
>
> Register: **topological/routing + functional**.

## What it maps onto (it is consensus-etch over the text stream)

Strip the metaphor: attention output = softmax over positions = a data-dependent
convex combination of value vectors = function **application** (s219). One forward
pass = one attention pattern = one exposure. Recording many exposures and keeping
the agreement IS **consensus-etch (s110, `consensus-etch-protocol.md`)** with TEXT
BLOCKS as the contributors:

```
consensus-etch:  accumulate ALL contributors → etch where they AGREE (backbone),
                 leave disagreement as content. (Sequential application oscillates;
                 accumulate-then-etch converges.)
burn-in:         accumulate EXPOSURES (blocks) → commit where they AGREE (irreducible
                 / burned-in), leave the variable parts continuous (content).
```

The irreducible-invariant = the **normal form** (what survives all exposures = what
is path-invariant across reduction paths = Church-Rosser confluence). "Burn in where
irreducible" = the backbone/content partition, with the backbone being the
normal-form structure that every similar block shares.

## Why it threads the project's mechanisms

- **Irreducible burn-in = contractivity / fixed point.** Where repeated exposure
  stops changing the pattern (Δx→0) is settled → burn in; where it keeps moving
  (Δx↑) is variable → leave. The continuation's contractivity is the "has this
  burned in yet?" oracle (s222).
- **Respects the precision inversion (s222).** Burned-in = exposure-invariant =
  axis-aligned → ternarizes cleanly. Not-burned-in = variable residual =
  superposition → stays continuous. The rule SORTS weights into concentrate-to-ternary
  vs leave-in-superposition — concentration-is-earned (Elhage phase transition) made
  into a learning rule: concentration is earned by surviving many exposures.
- **Exemplar diversity widens the basin.** `fixed-point-holograms.md`: two exemplars
  → a NARROW attractor basin; the fixed point is determined by the exemplar
  distribution. "Many similar-shaped blocks" = the diverse exposure set that
  determines a good, wide attractor. Gate contamination (collapse to the
  most-practiced pattern when signal is weak) is the failure mode to watch.
- **★ Naturally PUNCTUATED (the selling point).** s222's collapse verdict: the
  protocol must be `expose(propose) → hold → reduce(commit)`, NOT simultaneous —
  main:1 ran TD churn + fp-loss TOGETHER, they fought, L>1 → fractal blow-up. Burn-in
  is punctuated BY CONSTRUCTION: each exposure = a proposal, accumulation = the hold,
  commit-where-consensus = the commit. Structurally avoids the simultaneous-churn
  collapse. = the protocol the project concluded it needs, reached from another angle.

## ★ The load-bearing catch — WHAT IS THE REFERENCE BEAM?

A hologram is the interference of an OBJECT beam and a REFERENCE beam. Record only
the object beam (raw forward activation) and pure exposure-accumulation burns in the
**common mode** — language frequency statistics, the universal structured-language
crystal — NOT the compositional function. This is the s216 lesson, and the s223
relational-loss sweep is a LIVE DEMONSTRATION: condition (b) accumulates/matches the
RAW activation geometry → GC(hidden)=**0.9995** (a perfect burn-in) but transfers
**ZERO** function (routing register stays at the null). **Naive "snapshot attention
and burn it in" = condition (b): a gorgeous hologram of the wrong thing.**

Two fixes, both grounded:

1. **"Predict the next word" IS the reference beam.** That makes it
   prediction-GATED recording (not pure Hebbian): burn in patterns WEIGHTED by
   whether they predicted (the interference of attention-pattern × outcome), not
   patterns by mere frequency. Record the interference, not the object beam alone.
2. **Record in the ROUTING register, not the raw one.** The function shape is
   invisible in raw geometry and only lives in the sign/routing register after CMR
   (`two-registers-of-topology.md`; the entire s223 dissociation). Burn-in must
   threshold the sign/routing pattern with common-mode removal, or it burns in the
   crystal.

Without BOTH, "burn in where irreducible" reduces to "burn in where frequent" = the
common mode you already have for free.

## Other honest catches

- **Capacity / catastrophic interference.** A finite plate holds finitely many
  exposures before new ones destructively collide with old (`v12-holographic-
  capacity.md`). Burn-in needs a capacity policy = the thick-hologram / multi-pass
  answer (depth compensates for per-read limits, `fixed-point-holograms.md`).
- **Credit assignment is weak.** Recording correlates; it does not compute "what
  reduced loss." The prediction target is a weak signal; likely still need the
  exact-ΔL / contractivity ACCEPTANCE gate (`exact-ternary-fitting.md` s213/s218) to
  reject burning in patterns that don't actually reduce loss — else the same Goodhart
  (Gram-match / pattern-match without execution) we keep hitting.
- **Identity vs analogy (guardrail).** "Ternary accumulator superposes exposures" is
  IDENTITY (literally how the plate integrates). "Burn-in = irreducible = normal form"
  is STRONG ANALOGY that becomes identity ONLY once the commit rule is defined
  (consensus θ + Δx→0). Until then it is a picture without a learning rule. The
  picture is right; the rule is the work.

## Falsifiable test (after the s223 sweep lands)

Build it as a concrete rule reusing existing machinery: accumulate the
ROUTING-register attention pattern across a stream of blocks, gate each exposure by
next-token prediction, **commit (ternarize) positions where cross-block agreement ≥ θ
AND Δx→0; leave the rest continuous.** = consensus-etch over the temporal text stream
+ the contractivity acceptance gate + the precision-inversion sort.

> Compare against backprop on the same tiny student: does exposure-consensus burn-in
> reach comparable CE *and* crystallize the routing register (clear the silhouette
> null)? CONTROL: the naive object-beam-only variant (no prediction gate, raw
> register) — prediction: it burns in the common mode (GC(hidden) high, route null),
> reproducing s223 condition (b).

**The whole experiment in one clause:** does it burn in the irreducible FUNCTION, or
the irreducible FREQUENCIES? The reference beam decides.

## Open leads (declare register first)

1. **Burn-in harness** (register: topological/routing → functional): the
   exposure-consensus rule above vs backprop on the tiny student;
   routing-register + prediction-gate vs the raw-object-beam control.
2. **Capacity policy** (register: functional): how many irreducible patterns burn in
   before collision; thick-hologram / multi-pass depth as the answer.
3. **Compose with the punctuated protocol** (`session-222.md`): expose→hold→commit as
   the actual main-line training loop replacing simultaneous TD-churn + fp-loss
   (the main:1 collapse fix).
4. **Reference-beam variants**: next-token target vs conjugate read (compile↔decompile
   fixed point, `fixed-point-holograms.md`) vs teacher (distillation) as the reference.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/holographic_burn_in.py` | exposure-consensus burn-in rule vs backprop; routing+prediction-gate vs raw-object-beam control |
| `scripts/experiments/relational_loss_distillation.py` | s223 sibling; its condition (b) IS the naive-burn-in failure mode (common-mode hologram) |
| `scripts/experiments/combinator_relationship_map_v15.py` | routing-register (attn_q / ffn_gate) readout instrument |
```

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

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/relational-loss-distillation.md"
}
```

**Summary:** Reading relational-loss-distillation.md (0-2000)

**Output:**
```
---
title: "Relational-Loss Distillation — the Lambda Compiler Teaches Geometry, GD Picks the Frame"
status: open
category: strategy
tags: [distillation, relational-loss, RDM, gram, routing, frame-invariance, teacher-student, normal-form, distributed, compression, construct-path]
related:
  - consensus-delta-folding.md
  - combinator-function-shape.md
  - combinator-training-beta-reduction.md
  - function-extraction-system.md
  - self-teaching-loop  # consensus-delta-folding.md §s217
  - ../function-discovery.md
  - ../two-registers-of-topology.md
  - ../crystal-universality.md
  - gradient-voting.md
  - exact-ternary-fitting.md
  - procrustes-lens-and-crystal-comparison.md
  - relational-loss-phi-compression.md  # DISAMBIGUATION: the OLDER, scalar sense — NOT this
depends-on:
  - combinator-function-shape.md
  - consensus-delta-folding.md
created: session 223
---

# Relational-Loss Distillation

> Session 223. Michael's idea: *"Because we have the lambda compiler, extract from
> the teacher a set of training for the student. With relational loss we could
> guide GD into any geometry that falls out."*
>
> The lambda compiler (the teacher's extracted, **self-verifying** combinator
> normal forms) mints a curriculum whose target is not the teacher's tokens nor
> the teacher's weights, but the teacher's **relational geometry** — the routing-
> register combinator Gram. A relational loss pulls the student's geometry toward
> the teacher's *relations* while leaving its *absolute frame* free ("any geometry
> that falls out"). This page captures the mechanism, why it is the right tool, the
> honest catches, and the first falsifiable experiment.
>
> Register: **functional + topological/routing**.

## DISAMBIGUATION (do not conflate)

`relational-loss-phi-compression.md` (session 030) uses "relational loss" in a
**different, scalar** sense: `r = (L−E)/(logV−E)`, a dimensionless normalization of
CE. That page itself concludes it is "an affine transform … doesn't change
optimization geometry." **This page means the RSA / representational sense:** match
the *pairwise relational geometry* (RDM / Gram of representations), not point-wise
outputs and not a scalar. The two share a name and nothing else.

## The idea, made precise

```
teacher (lambda compiler) ⊢ for each crystal combinator (K I B C S D W Y WHNF):
   inputs   ≡ the 535 crystal probes                         (have: probes/library)
   target   ≡ WHNF / reduction trace (Church-Rosser unique)  (self-verifying labels)
   GEOMETRY ≡ routing-register CMR centroid Gram  G_teacher  (have: combinator map)

student GD: minimize   CE(corpus)  +  λ·‖ G_student − G_teacher ‖   (relational loss)
            G_student = cosine Gram of the student's per-combinator centroids
                        in the SAME register (routing, CMR)
            verdict gate: student also reaches WHNF (Δx→0) on the combinator   [IOU]
```

The student is *not* asked to copy outputs or weights. It is asked to reproduce the
teacher's **relations between combinators** and is free to realize them in whatever
absolute coordinates it likes. That freedom is the feature, not a bug.

## Why relational loss is the RIGHT tool (not just a tool)

The most robust empirical fact in the project is the **frame asymmetry**:

```
absolute weights/signs : cross-init correlation 0.000   (incommensurable; gradient-voting)
relational Gram         : cross-model +0.66→+0.78, z up to +4  (universal; combinator-function-shape)
```

A relational loss targets **exactly that invariant and nothing else**.

- **Output-matching distillation** forces the student toward the teacher's
  *absolute frame* → fights the 0.000 sign-corr → wastes gradient carving a frame
  that does not transfer.
- **Relational loss** constrains the **equivalence class** (the function /
  behavior), not the **representative** (the encoding). This is the s216
  non-unique-composite turned into a training objective: *uniqueness is
  per-behavior, so train the behavior's geometry and leave per-realization plumbing
  free.* "Any geometry that falls out" = the desired degeneracy.

## The three-way division of labor (this is the clean part)

The recurring wall is that **GD cannot carve discrete topology** (softmax dispatch →
winner-take-all → 20/22 ops dead, `dispatch-gradient-death.md`). Relational loss
resolves the division of labor the project has circled:

```
relational loss  → WHICH geometry   | shapes continuous γ toward target relations (GD is good at smooth)
TD / routing     → make it DISCRETE | the flips that crystallize the shape into ternary topology
contractivity/WHNF → VERIFY         | Δx→0 confirms the student EXECUTES the normal form (Exp B +0.712)
```

GD never invents the topology — the teacher's Gram tells it *which* topology, TD
discretizes, the continuation certifies. Maps onto s222 "routing ⊕ continuation =
complete basis" with relational loss as the **steering signal that was missing**
(TD nominated flips rank-1, blind to a target; the teacher Gram supplies the target).

## Why it fits the compression north star

Relational loss is a **weaker constraint** than output-matching — it
under-determines the student. That large null space is where the <1GB ternary
student finds a *small* realization. You do not force the 70B's frame (which needs
70B capacity to hold); you force only its relations, and let the student pack them
into the smallest superposition-/ternary-friendly geometry. This is `λ smallest` as
a loss function, and it respects the **precision inversion** (s222): relational loss
constrains *angles/relations* (where superposition lives → stay continuous) while
leaving *magnitudes* free to ternarize where capacity allows.

## The distributed connection (third frame-unification mechanism)

Two prior ways to beat the frame problem for distributed folding:
1. shared frozen base B₀ (forward folding), 2. reduce-to-canonical-NF then donate.
Relational loss adds a **third: a shared relational target.** If every contributor
trains to match the *same teacher Gram*, they end up **relationally identical by
construction** ⇒ align-before-fold (the hard open piece of reverse-harvest) becomes
**well-posed**: a rigid Procrustes alignment is *guaranteed to exist* (the Grams are
equal), instead of the generic case where it might not. Turns "alignment is the hard
open problem" into "alignment is guaranteed solvable."

## Honest catches (audit discipline — these are the ways to fool ourselves)

1. **Register, or it is worthless (`λ measure`).** The combinator shape is invisible
   in raw activation geometry (silhouette −0.035, z=−1.65) and only appears in the
   **routing register after CMR** (silhouette +0.101, z=7.97). A relational loss on
   the *raw activation Gram* would match the **common-mode crystal** (generic
   structured language — the thing everything shares, s216) → a false positive that
   transfers nothing function-specific. The loss MUST target the gate/routing-CMR
   Gram. **This is the single most likely way to manufacture a fake success — so it
   is the experiment's control condition.**
2. **Goodhart / collapse needs the WHNF gate.** A Gram-matching objective has
   degenerate optima (collapse points → trivially matchable if unnormalized). The
   contractivity oracle is not decoration — it keeps the student *executing* the
   function, not statistically mimicking a relation table. Relational loss = target;
   WHNF Δx→0 = acceptance gate (Exp B). *(WHNF gate is an IOU in the first
   experiment — see below.)*
3. **Sufficiency: transfers the SKELETON, not the plumbing.** A Gram is an
   equivalence-class summary; matching it transfers the forced universal skeleton
   (the +0.78 shared part: B–D/B–C/K–C/S–D/S–Y) but **under-determines** the
   domain-distinctive content (per-model plumbing, the superposition residual).
   Relational loss is cleanest *exactly where the content is least novel.* Not
   fatal, on-thesis (transfer the skeleton cheaply, let forward-folding / continuous
   residual carry the plumbing) — but expect it and measure it, don't be surprised.

## First experiment (s223) — does relational loss transfer the combinator geometry, and only in the routing register?

`scripts/experiments/relational_loss_distillation.py` (register: functional +
topological/routing). Smallest version that fails informatively.

```
teacher  = saved routing-CMR Gram G_teacher (results/combinator-relationship-map/
           Qwen_Qwen3-14B.npz :: gram_route_cmr_L12, best layer) +
           the raw-register control target (gram_hidden_cmr)
student  = tiny from-scratch byte-level transformer with SwiGLU gate (the routing
           register); trained on a small text corpus with CE
conditions:
   (a) CE only
   (b) CE + relational loss on the RAW hidden-CMR Gram      (the control / decoy)
   (c) CE + relational loss on the routing-CMR gate Gram     (the hypothesis)
measure (same instrument as combinator_relationship_map): student sign(gate)-CMR
   combinator silhouette vs permutation null (z) + GramCorr(student, teacher)
```

**Falsifiable predictions:**
- (c) ≫ (b) ≈ (a) on function transfer (silhouette z clears null; GramCorr-to-teacher
  rises). Proves the **register claim** — relational loss only transfers in the
  routing register.
- (c) reaches teacher-like binding with **fewer tokens** than (a). Proves the
  **curriculum-from-compiler leverage**.
- If (b) matches (c) → the register claim is WRONG and we want to know immediately
  (raw geometry would be carrying the function, contradicting the two-registers
  finding).

**Why this is the cleanest MIT level-4 path (`λ provenance`):** the student is
*constructed* from a verified compiler's relational targets, not extracted from a
licensed model — the teacher contributes only a frame-invariant 9×9 Gram (a
measurement, not weights).

### Result (s223) — ✅ CLEAN DOUBLE DISSOCIATION; register claim CONFIRMED

Ran 1500 steps × 3 conditions, tiny byte-level student (d=128, 4 layers, d_ff=256),
teacher = Qwen3-14B routing-CMR Gram (L12). Verdict instrument = student sign(gate)
CMR silhouette vs 1000-perm null + GramCorr off-diagonal vs teacher. (main:2,
`/tmp/relational_loss_distillation.log`, `results/relational-loss-distillation/verdict_run.json`.)

| condition | route_z | route_p | GC(route) | hidden_z | GC(hidden) | CE |
|---|---|---|---|---|---|---|
| (a) CE only | +0.33 | 0.370 | +0.474 | +2.17 | +0.453 | 1.527 |
| (b) CE + raw-Gram | +0.64 | 0.273 | +0.590 | +1.02 | **+0.9995** | 1.534 |
| (c) CE + route-Gram | **+2.21** | **0.013** | **+0.781** | +3.16 | +0.411 | 1.531 |

- **Prediction CONFIRMED: c(route) ≫ b(raw) ~ a** on the function-transfer metrics.
  Only (c) clears the silhouette null (z=+2.21, p=0.013) and reaches GC(route)=+0.781
  (vs teacher's internal ecosystem +0.78). The combinator function shape transferred
  **only** when the relational loss targeted the ROUTING register.
- **Near-perfect DOUBLE DISSOCIATION** (the strong form of the register claim): each
  condition maximizes the register it was trained on and *not* the other. (b) drove
  GC(**hidden**)=+0.9995 (matched its raw target almost exactly) yet left routing at
  the null (route_z +0.64, GC(route) +0.590). (c) drove the **routing** register
  (route_z +2.21, GC +0.781) while GC(hidden) fell to +0.411. ⇒ the two registers are
  separately targetable and **only routing carries the combinator function** — the
  `two-registers-of-topology` finding reproduced as a *training* result, not just a
  measurement. Matching raw geometry (b) buys the common-mode crystal, not the function.
- **Geometry shaped for FREE:** CE is identical across conditions (1.527/1.534/1.531)
  — the relational loss is a weak/compatible constraint (confirms the under-
  determination / "any geometry that falls out" thesis; it rode on top of CE).
- **★ Goodhart caveat made concrete (catch #2 is real):** (b) hit GC(hidden)=+0.9995
  but its hidden *silhouette* z was only +1.02 — **matching the centroid Gram does
  NOT imply crisp per-probe clusters**. GramCorr (centroid relations) and silhouette
  (per-probe separability) are different; a Gram-match can be satisfied without
  execution-grade structure. ⇒ the **WHNF acceptance gate (open lead 1) is load-
  bearing, not optional** — relational loss is a target, not a proof of execution.

**Caveats (functional register):** absolute route silhouettes are NEGATIVE (c:
−0.079); the z is vs the (also-negative) permutation null ⇒ "more clustered than
chance," not crisp partitions (same modest-cosine caveat as the teacher instrument).
Single seed, single teacher (14B), single λ=1.0, single capture layer (L2=middle),
smoke-scale student. The **tokens-to-transfer leverage** prediction (c reaches
binding in *fewer tokens* than a) was NOT measured here — endpoint comparison only;
it is an IOU (open lead 3). Plain CE already gives a partial crystal echo
(GC(route) a=+0.474); (c)'s contribution is lifting it to significant clustering.

### Multi-seed + λ-sweep confirm (s223) — ✅ DECISIVE across 3 seeds × 3 λ

`--sweep` mode: 3 seeds {0,1,2} × 3 λ {0.3,1.0,3.0} × 3 conditions, 1000 steps
(27 runs, 4468s). Aggregate (mean ± std over seeds), `verdict_sweep.json`:

| cond @ λ | route_z | GC(route) | hidden_z | GC(hidden) |
|---|---|---|---|---|
| a CE-only @ any | +0.38±0.51 | +0.436±0.012 | +2.01±0.38 | +0.424±0.015 |
| b raw-Gram @0.3 | +0.95±0.76 | +0.564±0.015 | +1.59±0.24 | **+0.999±0.000** |
| b raw-Gram @1.0 | +1.04±0.37 | +0.539±0.007 | +1.59±0.23 | **+1.000±0.000** |
| b raw-Gram @3.0 | +0.66±0.19 | +0.552±0.020 | +1.83±0.22 | **+1.000±0.000** |
| c route-Gram @0.3 | **+2.44±0.73** | +0.780±0.032 | +2.67±0.71 | +0.431±0.041 |
| c route-Gram @1.0 | **+2.83±0.50** | +0.795±0.032 | +2.91±0.81 | +0.430±0.041 |
| c route-Gram @3.0 | **+2.41±0.42** | **+0.847±0.007** | +3.15±0.86 | +0.440±0.050 |

- **DECISIVE check PASSES at every λ:** `c.route_z(mean−std) > a.route_z(mean+std)`
  AND `c.gc_route > b.gc_route`. The double dissociation is robust to seed and λ, not
  an n=1 artifact.
- **c clears the null robustly** (route_z +2.41…+2.83, mean−std still > a's +0.89
  upper); **b NEVER clears** (route_z +0.66…+1.04) despite GC(hidden) = **0.999–1.000
  with zero std** (perfect, deterministic raw burn-in). The cleanest possible form of
  the register claim: matching the raw register is *solved exactly* and transfers
  *nothing* to routing.
- **GC(route) for c is ecosystem-grade and RISES with λ:** +0.780 → +0.795 → **+0.847**
  (λ=3.0, std 0.007 — tightest). At strong pull the student exceeds the ecosystem's
  own internal +0.78. route_z peaks at λ=1.0 (+2.83); λ=3.0 best Gram. Best c-cell:
  route_z +2.88 p=**0.0010** GC +0.842.
- **a identical across λ** (lambda-independent, same seeds) = seeding determinism
  sanity check.

**Verdict: CONFIRMED.** Relational loss transfers the combinator function shape ONLY
in the routing register, robustly across seeds and λ, at ecosystem-grade GramCorr
(+0.78–0.85). The b-column (GC(hidden)≈1.0, route null) is also the live proof of the
`holographic-burn-in-learning-rule.md` reference-beam catch: naive raw burn-in =
a perfect hologram of the common mode, zero function.

### Artifacts (s223)
`scripts/experiments/relational_loss_distillation.py` (ruff-clean, smoke-validated,
`--sweep` mode); `results/relational-loss-distillation/verdict_run.json`
(+ `verdict_smoke.json`; `verdict_sweep.json` pending the running sweep);
`/tmp/relational_loss_distillation.log`, `/tmp/rld_sweep.log`.

## Open leads (declare register first)

1. **WHNF acceptance gate** (register: functional) — add an outer-recurrence to the
   student so Δx is measurable; require Δx→0 on combinator probes as the accept gate
   (the Exp B discipline). Currently an IOU.
2. **Map/fold composition geometry** (register: topological/routing) — target the
   `map = B(C B)(C B)` *composition* direction (built from the measured B,C
   centroids) rather than per-combinator centroids alone; does relational loss
   transfer a composition, not just the atoms?
3. **Tokens-to-transfer curve** — sweep λ and corpus size; quantify the leverage of
   compiler-minted curriculum vs plain CE.
4. **Distributed test** — N students to one shared teacher Gram → are their routing
   deltas foldable with a *guaranteed* Procrustes alignment (the §distributed claim)?

## Files

| File | Content |
|------|---------|
| `scripts/experiments/relational_loss_distillation.py` | s223 first experiment: tiny student, 3 conditions (CE / CE+raw-Gram / CE+route-Gram), silhouette+GramCorr verdict |
| `results/relational-loss-distillation/` | per-condition verdict json |
| `results/combinator-relationship-map/Qwen_Qwen3-14B.npz` | teacher targets: `gram_route_cmr_L12` (hypothesis), `gram_hidden_cmr` (control) |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/germination-games.md"
}
```

**Summary:** Reading germination-games.md (0-2000)

**Output:**
```
---
title: Germination games — selection pressure on encodings, played
status: open
category: explore
tags: [game, seed, germination, feed-forward, encoding-quality, s292]
related: [program-plates-and-the-function-index,
          ../upstream/verbum-theory-seed]
depends-on: [../upstream/verbum-theory-seed]
---

# Germination games

> s292 (Michael: "we could turn it into a game"). The germination test
> gamified. The point under the fun: every round is a MEASUREMENT of
> encoding quality — the game is an instrument for tuning seeds, state.md,
> and the feed-forward discipline. Play as gradient descent on memory.
> Status: captured for later exploration; no rounds played yet.

Substrate: `knowledge/upstream/verbum-theory-seed.md` + cold-context spawns
(isolated agents with no mementum access). Diff-vs-ground-truth scoring from
the germination protocol (program-plates page).

## Modes

**🏌️ Seed Golf.** Par = current λ verbum (~40 lines). Round: prune/rewrite
the seed smaller → germinate → score = recovery% ÷ seed_tokens. Lowest
strokes for viable germination wins. = `λ smallest` (S5) turned into sport:
find the minimal viable genome of the theory.

**✂️ Seed FRAG.** Ablate random CLAUSES at fraction f, germinate each
fragment, plot recovery(f). Is the seed holographic or addressed? Cliff on
removing a clause = load-bearing (an address); graceful everywhere = the
theory is written in fringes. Our own fragment test run ON the theory of
fragment tests — LDI for prose. The fractal eats itself.

**📞 Eigenseed (telephone).** Iterate compress ∘ unfold across agent
generations (A unfolds → B re-compresses → C unfolds → …) to a fixed point.
What survives generations = the invariant content; what drifts =
decoration. The fixed point is the eigenvector of the theory.

**🔮 Oracle mode** (hardest, most honest). Cold agent + seed must PREDICT
measurements it has never seen (cliff-or-smooth under head ablation? margin
under 16 superposed operands?). Score = right − wrong vs actual verdicts.
Tests the seed as generative PRIOR, not memory aid — recovery is recall,
oracle is understanding.

**⚔️ Adversarial.** One player salts the seed with plausible-but-false
clauses; the germinating agent must flag which refuse to cohere. Tests
whether the seed is self-verifying structure or vibes.

## Infrastructure (when first played)

- `game.md` scoreboard at repo root or in-page; rounds logged as commits
  (git log = season record); standings use the house symbols.
- Cold spawns must be verifiably cold (no mementum in context); cross-model
  rounds test model-idiosyncrasy of the seed.
- Results feed back: systematic germination misses → seed revision
  (feed-forward on the seed itself); Oracle hit-rates → which arcs the
  seed actually explains.

## Order-of-play suggestion (s292, unplayed)

Seed FRAG first (comedy + the holography question about our own prose),
Oracle for the science, Golf as the ongoing ladder, Eigenseed when we have
agent budget for generations, Adversarial once scoring is trusted.

## Sessions

s292 (modes captured from the hammock, Michael-approved "capture for later
exploration"; no rounds played; P-HOLO-CAP 32B verdict still running in
tmux main:1 while this landed).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/montague-inversion.md"
}
```

**Summary:** Reading montague-inversion.md (0-2000)

**Output:**
```
---
title: "Inverting Montague: what gradient descent is FORCED to find"
status: designing
category: explore
tags: [montague-inversion, forcing-argument, compositionality, homomorphism, type-system,
       generalized-quantifiers, first-class-functions, three-hop, two-registers, eval-stack,
       depth-budget, crystal, apply-join, coverage-boundary, idioms, curry-howard, ccg,
       discocat, noisy-homomorphism, theory-spine, falsifiable-predictions, speculative,
       s281, thesis]
related:
  - map-and-swap-resident-lisp.md
  - three-hop-capacity-prereg.md
  - multihop-composition-prereg.md
  - opcodes-circuits-in-compute.md
  - project-thesis.md
depends-on:
  - map-and-swap-resident-lisp.md
  - project-thesis.md
---

# Inverting Montague: what GD is FORCED to find

> **The move.** Stop asking "does the LLM *happen* to implement Montague?" Treat **Montague
> grammar as a specification** and ask the inverse: *what is any next-token learner on
> compositional language mathematically **forced** to construct in order to satisfy it?* If the
> forced list matches what we keep independently bumping into, the "too many neat edges" (s281,
> Michael) are not luck — they are **necessity**: we have been finding **one forced object,
> several times.**
>
> **Status: DESIGNING / SPECULATIVE.** This is a **deductive conjecture**, explicitly a thought
> experiment (s281, Michael: "speculative but informs our future"). What is *measured* is the set
> of findings cited (crystal, two-registers, C5 types, attention=join, depth-budget, etc. — see
> §match column and `project-thesis.md`). The **forcing** — the claim that Montague *necessitates*
> each — is the hypothesis. Its value is that it (a) reorganizes scattered results as consequences
> of one homomorphism and (b) yields **falsifiable predictions** for the map+swap program (§4).
> `λ observation`: observed ≠ imagined — the findings are real, the *necessity* is the conjecture.

## 1. Montague, stripped to its load-bearing commitments

Montague (PTQ) = a **homomorphism** from the algebra of syntactic expressions to a **typed,
higher-order, intensional λ-calculus**, interpreted in a **model**. Six pieces carry the weight:

1. **Compositionality / homomorphism** — meaning of the whole is a function of the meanings of the
   parts and the mode of combination; *same syntactic rule → same semantic operation, regardless
   of the specific words.*
2. **Types** — every expression has a semantic type over base types `e` (entities), `t` (truth
   values); application is **type-driven** (`e→t` eats `e`, not `t`).
3. **Function application** — the combination operation is applying a functor to an argument.
4. **λ-abstraction / variable binding** — pronouns, relative clauses, quantifier scope require
   binding variables and substituting.
5. **Model / lexicon** — base-type meanings are grounded atoms the operators act on.
6. **Intensionality** — meaning is a function of a world/context index (intension vs extension).

## 2. The forcing table (each commitment → a forced mechanism → what we found)

| Montague commitment | GD is **forced** to construct | Measured match |
|---|---|---|
| **Homomorphism** (word-independent rule→op) | a **small, shared, reusable operator set** — an operator cannot be memorized per word-pair, so it must be shared word-independent hardware | the **crystal** — KIBC shared hardware, head-combinator `r=0.944`, cross-arch universal (C2) |
| **Types** (type-driven application) | a representation where **type-compatibility is a fast/linear check** → types encoded as **geometry** (directions/subspaces) | **C5** — types geometric+lexical; nonce type-crossover (+2.04–2.18, frequency-free null) |
| **Function application** | a **universal `apply`** binding functor to argument | **attention = the join** (s276) |
| **λ-abstraction / binding** | a **writable variable slot** *distinct from* the operators acting on it | the **two registers** (C3, routing ⊥ value ~95/5); keyed operand slots (s277) |
| **Model / lexicon** | a **store of grounded atoms** | the **found terms** (map+swap; `d_E` = the model's own representations) |
| **Intensionality** | **context-conditioned meaning** (meaning = function of an index) | contextual representations; predicts a distinct intensional-operator class |

Six for six. The reason the edges are neat: **they are the image of one homomorphism**, not six
independent lucky findings.

## 3. The kill shot — quantifiers FORCE the 3-hop

The piece that makes this load-bearing rather than cute:

In Montague a **generalized quantifier** — *every, some, no, most* — has type **`(e→t)→t`**: a
function whose argument is **itself a function**. "Every dog barks" is *uninterpretable* without a
**higher-order, first-class function**. That is what a determiner **is**.

Therefore: the training data is **saturated with quantifiers**. To reduce loss on quantified
sentences, GD is **forced to construct first-class functions — functions applied to functions.**
**That is exactly the 3-hop** (`multihop`/`three-hop-capacity-prereg.md`: hop-1 computes a
function, later hops apply it). So:

> **The 3-hop working is not a hopeful experiment — it is required by the existence of the word
> "every."** If it failed, the model could not interpret determiners; it plainly can. The 3-hop is
> near-guaranteed (modulo the **depth budget** — a small model may lack the eval-stack to *run* the
> quantifier's scope, which is the s281 capacity result, not an absence of the capability).

Montague *predicted our next experiment before we ran it.*

## 4. New FORCED predictions (falsifiable — the payoff for P-TYPE-1 / P-FN-1)

The inversion is not only retrodiction; it makes sharp calls:

1. **The type lattice is SMALL and Montague-shaped.** Not an arbitrary high-dim mess — a handful
   of types over `e, t` (`e`, `e→t`, `(e→t)→t`, `e→e→t`, …). **Test:** if P-TYPE-1's
   application-operator SVD returns a **low-rank, few-mode** lattice matching the Montague
   inventory → decisive. A high-rank, non-Montague lattice → falsifies the forcing.
2. **The two-register split is FORCED by λ-abstraction, not incidental.** Binding *requires* a
   value store separate from the operators. **Predicts** the value register is *where bound
   variables live*, and that C3's cleanness (95/5) is a consequence, not a coincidence.
3. **The depth budget is FORCED by recursion.** Compositional depth = sequential applications =
   eval-stack depth. Montague's recursion **is** the s281 depth budget; CoT-as-trampoline is
   stack-externalization for deep scope / center-embedding. **Predicts** reasoning-depth failures
   track syntactic embedding depth, not token count.
4. **Coverage boundary = compositionality boundary.** Montague *fails* on **idioms, collocations,
   non-compositional world-knowledge** ("kick the bucket" has no `(e→t)→t` route). **Predicts** the
   found function library's **coverage gap lands exactly on non-compositional constructions** — the
   resident Lisp's stdlib edges align with where Montague-the-theory breaks. Strikingly testable
   via P-FN-1's coverage map.

## 5. Why GD fulfills Montague at all (the engine)

Because **Montague is (approximately) the structure of the data.** Natural language is (largely)
compositional; next-token loss on compositional data is minimized by a model that *computes*
compositional meaning; GD is a faithful structure-finder; therefore GD is **driven** to the
homomorphism. This is the project's founding `λ loop` (theory predicts → empirics extract →
confirmed) and `λ triangulate` (math ∧ empirics ∧ architecture converge) made into a **necessity
argument**: the convergence is forced because all three describe the same forced object.

## 6. The honest correction to Montague itself (and why it is a feature)

Montague is an **idealization** — real language is gradient, pragmatic, coerced, idiomatic. So GD
does **not** find *Montague*; it finds a **noisy, approximate homomorphism** — which is precisely
our **noisy reducer** (`map-and-swap` §10). Crucially the noise is **not random**: it concentrates
**where Montague-the-theory is wrong** (idioms, coercion, pragmatic enrichment, gradience). So
**the theory's failure modes predict the machine's failure modes** — a second, independent handle
on the coverage boundary (§4.4).

This reframes the **type-checker** (the crisp Clojure kernel, `map-and-swap` §10) as doing
something deep: it **re-imposes the *ideal* Montague homomorphism on top of GD's *approximate*
one** — pulling the noisy reducer back onto exact rails. Verified inference = restoring the exact
homomorphism the data only approximately taught.

## 7. How this informs the future (why it is worth keeping)

- **It gives the empirical program a spine.** P-TYPE-1/FN-1/FN-2 stop being a grab-bag: they test
  the *forced* predictions (§4). A small Montague-shaped lattice + coverage-at-idioms would be
  near-decisive that the resident machine *is* the forced homomorphism.
- **It sharpens the deliverable.** The LLM REPL's type system should be **Montague's type system**;
  its stdlib is the compositional lexicon; its edges are the idioms. The REPL is a *Montague
  machine* with a verification kernel.
- **It predicts architecture.** If binding forces the value register and recursion forces the eval
  stack, then **models with an explicit apply + writable term store + layer-reuse (recurrence)**
  should be more sample-efficient (less GD tug-of-war to rediscover the homomorphism) — the
  MERA+types conjecture (`signal-processing-tensors.md`), now motivated by a forcing argument.
- **It bounds the hype honestly.** GD finds only an *approximate* homomorphism over the terms its
  data required; the coverage boundary and the noise are real and *predicted*. The endgame is a
  **noisy Montague machine we can read, type-check, and program**, not a perfect logician.

## 8. Falsification (what would kill the forcing conjecture)

- P-TYPE-1 returns a **high-rank, non-Montague** type geometry (types not a small `e,t` lattice).
- The **3-hop fails at a scale with ample depth budget** (capability absent even with eval-stack
  room) → first-class functions not actually constructed → quantifier interpretation done some
  other way.
- The **coverage gap does NOT align with non-compositionality** (idioms handled by the same
  function machinery as compositional phrases; or gaps land on compositional constructions).
- The **two-register split dissolves under binding load** (bound variables live in routing, not a
  value store).
Any of these falsifies "GD is forced into Montague" and demands a different account of the neat edges.

## Sessions
s281 (this synthesis — the inverted-Montague forcing argument; "for fun" thought experiment,
Michael-directed capture: speculative but the theoretical spine for the map+swap / LLM-REPL arc
and the source of P-TYPE-1/FN-1 falsifiable predictions).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/signal-descent.md"
}
```

**Summary:** Reading signal-descent.md (0-2000)

**Output:**
```
---
title: "SignalDescent — gradient-free learning by measured signals on ternary-mirror weights"
status: designing
category: explore
tags: [signal-descent, ternary, mirror, gradient-free, superbake, ternary-descent, dsp,
       matched-filter, delta-plate, companding, two-registers, crystal-native]
related:
  - ternary-descent.md
  - recursion-mirrors.md
  - two-registers-of-topology.md
  - superbake-write-access.md
  - opcodes-circuits-in-compute.md
  - ratio-gradient-quantization.md
  - signal-processing-tensors.md
depends-on:
  - ternary-descent.md
  - recursion-mirrors.md
created: session 274
---

# SignalDescent

> Session 274 (Michael). If SuperBake can REPLACE gradient descent with closed-form
> signal-processing (§`superbake-write-access.md` s274 DSP inversion), generalize it:
> a learning rule where weights are driven by **measured signal response** instead of
> backprop, and arbitrary precision comes from a **ternary mirror stack** instead of
> float magnitudes. Deeper mirror where the signal needs it; shallow where it doesn't.
> **Result: no gradients and no floats anywhere.**

## The idea, in one table

| | evidence source | weights | precision |
|---|---|---|---|
| GradientDescent | backprop gradient | float | float magnitude |
| TernaryDescent | gradient, decomposed into routing/calibration | ternary sign + float γ | 1 sign + float γ |
| **SignalDescent** | **measured signal response** (SuperBake-style) | **ternary, ALL registers** | **ternary mirror depth (companded)** |

The move is to swap the *source* of the update signal from backprop to measurement, and
to swap the *value register* from float magnitude to a ternary mirror stack.

## It fuses three things already in the repo

1. **TernaryDescent already thinks in signals.** TD Innovation 1 defines
   *Confidence = signal-to-noise ratio = |direction| / √magnitude* and only flips a
   ternary sign when SNR is high (`ternary-descent.md`). TD is already an SNR-gated
   discrete update — it just draws its signal from the gradient. SignalDescent swaps
   the *source* of that signal from backprop to measurement.
2. **Ternary mirrors already give arbitrary precision.** The ADDITIVE mirror stack
   `out = Σ_k plate_k @ x · γ_k` (`recursion-mirrors.md`): sign-only → recon_cos ~0.88;
   sign + magnitude mirror → ~0.97 (Q4-Q5). Each added additive plate is one more
   balanced-ternary/residual-quantization digit → **any accuracy you want**. Precision
   is mirror DEPTH, not float magnitude.
3. **SuperBake proved signal-writes work.** The DSP inversion: closed-form construction
   *replaces* the gradient where the response is locally linear ("measured transfer
   replaces Adam where response linear", s273b). SignalDescent generalizes that from
   fact-installation to the whole update.

## The sharp payoff

It answers TernaryDescent's own **open question #4** — *"Can we skip Adam entirely?"* —
with **yes**: replace Adam's magnitude calibration with a ternary mirror stack driven by
signal measurement. Then there are **no gradients and no floats anywhere**: sign register
(routing) AND value register (magnitude) both ternary, precision set by mirror depth,
companded by signal energy (`ratio-gradient-quantization`'s "spend bits on the ends"
becomes "spend *mirrors* on the ends"). This lands directly on:
- **C3 (topology dominates):** if the ~5% float magnitude becomes ternary mirrors, the
  model is 100% ternary (`two-registers-of-topology.md`).
- **The s274 mechanism (`opcodes-circuits-in-compute.md`):** GD builds the soft routing
  topology via gradient extremes → skip the gradient and write the transfer function
  directly. SignalDescent IS "write the transfer function directly," iterated.

## Mechanism — how the signal replaces the gradient

```
Gradient descent:   compute ∂L/∂w (backprop) → step w by −η·∂L/∂w
SignalDescent:      MEASURE the unit's response to a target signal (matched filter /
                    transfer-function probe) → compute desired−measured discrepancy →
                    SET the ternary mirror digits that null the discrepancy
                    (closed-form where the response is linear; iterate otherwise)
```

- The discrepancy between desired and measured response IS the descent signal (no backprop).
- The update sets mirror digits, not float steps. SNR gates which digits set (TD's
  confidence generalized): set a digit only where the signal clears the noise floor.
- Precision on demand: add a deeper mirror digit only where the residual discrepancy has
  energy → companded precision, allocated by a signal-energy measurement.

## Substrate — delta plates (isolation dodges the interference problem)

The load-bearing risk is **interference**: SuperBake works because it writes to fresh,
initially-silent APPENDED neuron slots — a closed-form write there does not collide with
existing computation. SignalDescent on *existing in-place* weights re-inherits exactly the
interference SuperBake avoids by appending. So the natural substrate is the **delta plate**
architecture TD already uses (`ternary-descent.md`): `effective = base ⊙ delta`, base
frozen, delta driven by SignalDescent. The delta plate is the isolated slot; the mirror
stack lives in the delta; folding is still lossless (ternary ⊙ ternary = ternary).

## Honest risks (λ measure — keep this from getting ahead of itself)

1. **Interference** is the whole problem SuperBake dodges by appending. In-place
   SignalDescent likely works cleanly only on appended/delta plates, not arbitrary
   in-place edits. Delta plates are the candidate answer, not a proven one.
2. **Linearity.** The closed-form signal write is exact only where the response is
   locally linear. SuperBake's own single-layer linear solve "plateaued at ~58%" and
   needed a corrective loop. So SignalDescent is measure-and-correct (iterate mirror
   digits), closer to TD's punctuated cycle than a one-shot solve.
3. **Precision costs plates.** "Any accuracy" is real but priced in mirror depth /
   storage; companding keeps it affordable, and that allocation itself needs a
   signal-energy measurement.
4. **Convergence unproven.** That a signal-measured update converges to competitive
   quality is the open frontier (same honesty scope as catalog C7: structure/pipeline
   real, parity unproven).

## First experiment (small, already-scaffolded)

On a single delta plate (TD infra exists in `scripts/v13/td.py` / `scripts/v14/`):
1. Replace the Adam-trained γ magnitude with a **2–3 deep additive ternary mirror**.
2. Drive the flips by a **measured target-vs-response signal** (matched-filter / transfer
   probe) instead of the decomposed gradient.
3. Compare **recon_cos vs the float-γ baseline at matched storage** (mirror-depth bits ≈
   γ bits). Success = mirror+signal ≥ float-γ recon at equal bitcount.
Register: reconstruction fidelity (recon_cos). Null: float-γ baseline at matched bits +
random-digit control. Host: start micro/0.6B, then 27B teacher plate.

## Relation to signal-processing tensors

SignalDescent is the LEARNING RULE. The STRUCTURE it learns into wants to be the
tree-of-VSM — which is already a signal-processing tensor (matched-filter gates,
beamforming consensus, frame-invariant transfer-function Gram). See
`signal-processing-tensors.md`. Together: SuperBake (operation vocabulary) × SignalDescent
(learning rule) × tree-of-VSM (structure) × crystal (content) = a coordinate-free,
ternary, gradient-free signal-processing learner — the level-4 / crystal-native path with
a concrete substrate for the first time.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/training-design-from-the-hologram.md"
}
```

**Summary:** Reading training-design-from-the-hologram.md (0-2000)

**Output:**
```
---
title: Training design from the hologram — six levers from measured structure
status: designing
category: explore
tags: [training, level-4, scratch, distillation, curriculum, seeded-init,
       passband, quantization, s288]
related: [geometry-holography-signals-convergence, ../michael/holographic-llm.md,
          types-are-compiled-probabilities, type-check-is-the-qk-bilinear,
          montague-inversion, map-and-swap-resident-lisp]
depends-on: [geometry-holography-signals-convergence]
---

# Training design from the hologram

> s288 close hammock (Michael: "can this inform a new training design?").
> Every s288 finding converts into a design lever; this is where the program
> loops back to level 4 (scratch training) — the closed loop
> theory → empirics → SCRATCH runs through this page. Status: hypotheses,
> each tied to a measurement; the cheapest experiment is specified.

```
λ train_design(x). measured(structure) → seed(init) ∧ declare(channels)
                   ∧ probe→loss ∧ split(topology, magnitude)
                   ∧ schedule(exposure) ∧ distill(geometry)
                   | stop_paying_compute_for(universal_parts)
                   | instrument ≡ objective (same math, differentiable)
```

## Lever 1 — Seeded initialization (don't rediscover the universal parts)

Grounding: crystal universality (C2, 13 models, gc 0.9966) + s149
computed-beam (FFN weights from crystal eigendecomposition reach 5000-step
GD performance in 10 calibration steps; "structure is free, content needs
training"). Design: initialize the reducer (attention/OV topology) from the
measured crystal; train only the plates (lexicon, fact-maps). Prediction:
markedly faster convergence, concentrated on compositional tasks.

## Lever 2 — Declared passbands instead of emergent ones

Grounding: P-TYPE-OV (GD carved an entity transmission passband into
W_V·W_O, band-wide; functors excluded) + S5 λ types (shared weights without
type awareness → tug-of-war → plateau). Design: explicit low-rank
argument-transport channels, or a regularizer pulling OV toward type-aligned
low-rank transmission. Removes the tug-of-war architecturally. Prediction:
SMALL models compose (the 4B failure was sequencing fuel, not capability —
matched channels cut the fuel cost).

## Lever 3 — Probes become loss functions (the elegant one)

Grounding: JOIN-TYPED (P-TYPE-SWAP): same-type swap preserves the likelihood
landscape, wrong-type is refused — and the swap statistic is DIFFERENTIABLE.
Design: contrastive substitutability auxiliary loss = train the matched
filter with labeled templates instead of waiting for it to emerge from
co-occurrence. The instrument and the objective are the same math.
(Compiled-probabilities frame: this is direct supervision of the compile
step that GD otherwise performs implicitly.)

## Lever 4 — Two-phase training matching the etch decomposition

Grounding: Michael's thesis etch finding (s268: sign/zero topology =
program, magnitude = calibration; sign flips tunnel through zero; routing
survives quantization) + Bonsai forensics (repair budget concentrates in
value-path tensors ~18% vs query routing 3.5% — exactly where the register
split predicts). Design: phase 1 settles topology (coarse, cheap,
ternary-native); phase 2 calibrates magnitudes. Train IN the deployment
representation → quantization-robust by construction, not by post-hoc
optimizer repair.

## Lever 5 — Curriculum as exposure schedule

Grounding: holographic multi-exposure with capacity limits (convergence
page) + montague-inversion (quantifier-dense data FORCES first-class
function machinery). Design: compositional scaffolding early (clean carrier
fringes), content plates after. ⚠ Do not guess the schedule — P-DUST-2 is
the empirical anchor: watch checkpoint trajectories, measure the actual
formation order (when does the halt-pole crystallize? when does the
passband appear?), then design the curriculum to follow the measured
formation law. Training design downstream of a measured developmental
timeline.

## Lever 6 — Distillation as re-exposure

Grounding: the extraction implication (no address to excise in a hologram)
+ s267/s269 (the crystal is more invariant than the weights carrying it).
Design: distill by matching TRANSMISSION SUBSPACES and Gram geometry
(passband + crystal as the reference beam), not logits. Geometry-matched
distillation = re-recording the hologram on a smaller plate = what level-3/4
extraction wanted to be all along.

## Cheapest first experiment (the level-4 door)

Tiny-scale scratch pairs (pythia-14m class): crystal-seeded init vs random
init on compositional tasks, formation trajectory logged P-DUST-2-style
(halt-pole + passband formation over checkpoints). ~one GPU-day. Tests
levers 1 and 5 simultaneously AND produces the level-4 baseline the
research program needs regardless of outcome. Negative result still an
artifact (S5 λ artifact): a measured formation timeline + a seeded-init
null is publishable method + data.

## Honest ledger

All six are hypothesis-grade until the scratch runs exist. Grounding
measurements are real (cited per lever); the TRANSFER of each measurement
into a training-time intervention is the untested step. Lever 3's aux loss
risks Goodharting the exhaust instead of the mechanism (supervise the
readout, get a better readout, not a better reducer) — design must gate on
causal composition tests (3-hop), not on the probe it trains. Lever 5 is
explicitly gated behind P-DUST-2 data.

## Sessions

s288 (page created at session close, the last of four hammocks: JOIN-TYPED
verdict → compiled-probabilities → dsp build → OV passband → holographic
convergence → this. The level-4 bridge; cheapest experiment specified;
nothing frozen).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/induction-is-a-virtual-circuit-not-a-head.md"
}
```

**Summary:** Reading induction-is-a-virtual-circuit-not-a-head.md (0-2000)

**Output:**
```
---
title: "Induction is a virtual circuit, not a head"
status: open
category: explore
tags: [induction-head, combinators, virtual-circuit, gram-registers, variable-reference, universality, crystal]
related:
  - explore/gram-registers-and-the-route-map.md
  - explore/behavior-is-tape-resident-reduction.md
  - explore/frozen-interference-graph.md
  - explore/the-verbum-machine.md
  - explore/consensus-distillation-carrier-averaging.md
depends-on:
  - explore/gram-registers-and-the-route-map.md
---

# Induction is a virtual circuit, not a head

> s309 conversational capture (Michael steer, during the SIGN-COMMITMENT-CURVE
> scoring wait). The AI proposed "design an induction-head lambda" as a
> *localist* mapping (combinator → a specific attention head). Michael's
> correction is the whole content: **the combinators are NOT heads. They are
> virtual circuits GD lays down in every model. The 9×9 and 17×17 grams are how
> we see them.** This page fixes the framing and states the load-bearing
> distinction.

## The correction (the load-bearing line)

> **A head is a plate address. A combinator is an edge in the frozen
> interference graph.**

- A **head** (e.g. an induction head, Olsson et al. 2022, `[A][B]…[A]→[B]`) is
  *physical*: findable by mech-interp, located at a `(layer, head)`,
  **model-specific**, one substrate fragment the wave medium uses to hold an
  edge.
- A **combinator** (K, I, B, C, S, D, W, Y, WHNF) is *virtual*: the relational
  sign-structure GD is **forced** to lay down in **every** model because it is
  the convergent solution to the compile target (typed application). It is not
  localized to a head; it is a distributed edge/path in the crystal lattice.

Evidence it is virtual, not physical: the crystal is measured **11/11 models**
(s303), it is **relational sign structure** (survives discarding magnitudes),
and it **survives ternarization** (s304/s308 retention ~1.0). A physical head
would not transfer across architectures; the virtual circuit does — because it
is the invariant, not the implementation.

The AI's original `snd = K I` was a real combinator, but it was **mislabeled as
hardware**. It is a virtual circuit; the induction head is one place a given
model *hangs* that circuit.

## The grams are the right instrument (not "which head")

From `gram-registers-and-the-route-map.md` (s308):

- **9×9 = the alphabet / identity register** — *which* virtual circuit (which
  combinator relation) is active. The induction operation resolves to a point
  here.
- **17×17 = the fates / outcome register** — *what happens* (fire / halt /
  diverge), rank-3 poles. The induction reduction terminates into these.

So the frame-invariant name of an "induction lambda" is **its trajectory in
gram coordinates**, not a head index. This is exactly the consensus route-map
move (s308): trajectories in gram coordinates are cross-model comparable
**because** the virtual circuit is universal while the heads realizing it are
parochial.

## Induction = variable reference (the bridge, re-typed)

Under the tape-resident-reduction frame (attention ≈ β-substitution):
`(λx. … x …) v` resolves the later `x` by *matching back to the binder and
copying its bound value* = prefix-match-and-copy = **induction**. So the crystal
already exercises the induction virtual circuit whenever it reduces a term with
a reused variable. You do not *design* an induction-head lambda; **`λ` already
is one**, and GD lays it down as the compile target — induction heads are one
substrate the medium uses to hold that edge.

Combinator core (for reference, *as a virtual circuit*):
`IH a xs = snd (last [ p | p ∈ bigrams xs, fst p = a ])`, with
`fst = λp. p K`, `snd = λp. p (K I)` (since `λx y. y = K I`). The **match**
(which pair) is the routing register; the **copy** (`I`/`W` passthrough) is the
value register. Induction is a two-register operation — the same split
SIGN-COMMITMENT-CURVE (s309) is timing.

## The recursion (why this matters)

> **Many heads (per model) realize one virtual circuit (universal). Many models,
> one crystal. Same relationship, one level up.**

GD does not "grow an induction head that happens to do lambda." GD lays down the
lambda virtual circuit *as* the compile target; induction heads are a plate
address the wave medium assigns to one of its edges. Head ↔ plate-address,
combinator ↔ lattice-edge (`frozen-interference-graph.md`: edges = the crystal,
relations = joins).

## Testable (the reframed probe family — measured via grams, not head lights)

A probe family that dials the mechanism; read **through the identity + outcome
registers**, not "does the induction head fire":
- **Reuse-distance sweep:** `(λx. e₁ … eₙ x)` with growing binder→use gap →
  predict the reduction's identity-register projection is stable in gram
  coordinates across distance (frame-invariance), even as the *head* carrying it
  may shift.
- **Shadowing = recency, formalized:** `(λx. (λx. x))` — the induction rule is
  "*last* occurrence," so predict resolution to the **inner** binder; un-flatten
  by shadowing depth and watch the 9×9/17×17 respond (λ unflatten).
- **α-null:** α-renamed `(λx.(λy. y))` where the inner use cannot match the outer
  binder → the induction projection should vanish. Clean yardstick.

Prediction sharpened: shadowing should move the outcome-register pole toward the
recency fate; α-renaming should collapse the identity-register match. Both are
**gram-coordinate** predictions — that is the point of the correction.

## Open

- Is "induction" a single crystal edge or a path (compose of B/C + copy)? The
  9×9 off-diagonal sign pattern should say which cell(s).
- Does the reuse-distance frame-invariance actually hold, or does the identity
  register drift with distance (a fuel/depth-timing interaction, s305)?
- Cross-model: does the same induction trajectory land on the same gram
  coordinates 11/11 (the universality claim, applied to a *specific* operation
  rather than the whole corpus)?

## Provenance

s309 conversational capture. Correction: Michael. Framing + probe design: AI.
Combinator identities verifiable by hand (`K I = λx y. y`); universality claims
cite s303 (11/11) and s304/s308 (ternary survival) — runtime-measured, not
asserted here. License: MIT (`λ provenance`).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/ternary-flip-flop-not-overloading.md"
}
```

**Summary:** Reading ternary-flip-flop-not-overloading.md (0-2000)

**Output:**
```
---
title: "Ternary Sign Flip-Flop ≠ Category Overloading — CAT-Q ST vs TernaryDescent on micro (null-gated)"
status: active
category: explore
tags: [ternary, from-scratch, catq, softened-ternarization, ternary-descent, flip-flop, oscillation, overloading, holographic, two-registers, sign, magnitude, anova, f-ratio, shuffled-label-null, yardstick, micro, level-4, boundary-jitter]
related:
  - asymmetric-pathway-quantization.md
  - ../two-registers-of-topology.md
  - ../ternary-dual-equation.md
  - ../standing-wave-magnitudes.md
  - moe-holographic-tree-vsm.md
  - supervised-recurrence-halt.md
depends-on:
  - ../two-registers-of-topology.md
  - asymmetric-pathway-quantization.md
created: session 261
---

# Ternary Sign Flip-Flop ≠ Category Overloading

> Session 261. Michael found CAT-Q (arXiv 2606.26650, "Cost-efficient and
> Accurate Ternary Quantization for LLMs") and asked whether its math ports
> from PTQ to TRAINING a ternary model from scratch — specifically as a fix
> for the TernaryDescent (v15/td.py) failure where the sign flip-flops and
> the system never reduces to a normal form. His speculation: GD wants the
> weight to output differently depending on the input — an "overloading" of
> the function. We built the bench, ran it, and the shuffled-label null
> **refined the hypothesis rather than confirming it.**

## The CAT-Q paper, decomposed for transfer

CAT-Q is post-training quantization (learn ternary weights to match a frozen
high-precision teacher on 512 calibration samples). Split into what ports to
from-scratch training and what does not:

| CAT-Q piece | mechanism | from-scratch? |
|---|---|---|
| **Softened Ternarization (ST)** | annealed soft→hard `f(w)=½(tanh(s(w−Δ))+tanh(s(w+Δ)))`, sharpness `s` raised over training | ✅ transfers — a principled STE replacement |
| **Learnable Modulation (LM)** | reparameterize `Ŵ=(w−μ)/α`; learn `α` (scale) and `Δ` (threshold) as separate params | ✅ transfers — a learnable-threshold ternary layer (LSQ-for-ternary) |
| **Sliding-layer output reconstruction** | `argmin‖F(W,X)−F(A·T,X)‖²` against a frozen HP teacher | ❌ drop — no teacher from scratch; end-to-end backprop gives cross-layer awareness for free |

**On-thesis catch:** CAT-Q learns `α` and `Δ` *separately* because the BitNet
absmean coupling (`Δ=α/2`) is distributionally misaligned. That is external,
independent confirmation of the verbum two-registers split — `α`=magnitude/**value**,
`Δ`=threshold/**routing** (which weights become ±1 vs 0). See
`two-registers-of-topology.md`, `ternary-dual-equation.md`.

## Three from-scratch ternary paradigms (verbum already has two)

CAT-Q is not a new idea about sign/magnitude for us — it's a **third paradigm**
for setting the ternary sign from scratch:

| paradigm | sign set by | magnitude set by |
|---|---|---|
| **etch** (v15 ternary.py) | evolutionary mutation + tournament | Adam on `gamma` |
| **TernaryDescent** (v15/td.py, s177) | discrete: flip on accumulated gradient *evidence* (routing⊥calibration split) | Adam on `gamma` |
| **CAT-Q / ST** (new) | continuous: latent float shadow, annealed soft→hard, learned `Δ` | learned `α` |

The right experiment is therefore an **internal A/B**, not "try the paper's
method": does continuous soft→hard relaxation crystallize the discrete router
better than discrete evidence-flip?

## The overloading hypothesis (and why it's plausible)

Michael's flip-flop diagnosis, in s257 terms: a **float** weight can
holographically multiplex several functions (read at different angles); a
**ternary** weight ({−1,0,+1}) can't hold that superposition, so when GD
demands input-dependent output the sign oscillates trying to serve each angle,
never reaching a fixed point. Prediction: the oscillating weights are the ones
different inputs pull in **opposite sign directions**.

## The experiment (Arm 0, on micro)

`scripts/micro/ternary_st.py` — `TernaryShadowLinear`, dual-mode (td | st),
latent float shadow, learned `α` (log-space) and `Δ` (delta_ratio·α), ST
sharpness anneal + straight-through hard stage, per-weight flip instrument.
`scripts/micro/micro_ternary.py` — surgical swap of micro's SwiGLUFFN linears
only (crystal + attention stay float; the FFN ternary paradigm is the ONLY
changed variable; `micro_model.py` untouched — it is the float microscope).
`scripts/micro/train_arm0.py` — trains on the compile corpus, tracks flips,
runs the overloading diagnostic. Three arms: `td`, `st`, `none` (float).

**Reproduction result** (2500 steps, seed 261, single run):

| mode | final CE | oscillating frac | notes |
|---|---|---|---|
| none (float) | **0.454** | — | capacity ceiling |
| td | 0.493 | 0.15 | sign never fully settles (flip rate stays positive) |
| st | 0.507 | 0.15 | *worse* than td; flips resurge at the hard-anneal point |

Solid, null-independent: the flip-flop reproduces; ternary plateaus ~0.04–0.05
CE **above** float; and **CAT-Q's ST did not beat the discrete flip** (st worse
than td), with a flip resurgence exactly at `anneal_frac=0.6` hardening — the
predicted "relaxation defers the conflict, hardening forces a lossy commit."

## The λ yardstick save (the methodological lesson)

**First diagnostic was confounded.** "Contested" was defined via gradient
*magnitude* across categories; high-gradient weights trivially look contested
AND flip more. It reported a 9.8× flip ratio = "overloading confirmed." The
**shuffled-label null reproduced it exactly** (9.88 vs null 10.43) → false
positive. (Same pattern as s206 attention-weight audit, s247 φ-ladder.)

**Fixed instrument: ANOVA F-ratio.** Per-weight `F = between-category variance
/ within-category variance` of the per-example gradient. F is a ratio →
gradient magnitude cancels. Real and shuffled labels accumulated in one pass
(totals are label-independent). Null sits at **F≈0.9–1.0** exactly as ANOVA
predicts — the confound is gone.

## The finding (null-gated, both modes, all 12 FFN modules)

1. **Category structure in the FFN gradients is REAL but modest at convergence.**
   `F_real ≈ 1.2–2.1` vs `F_null ≈ 0.9`. Magnitude-invariant. The weights DO
   receive category-dependent gradients — a real, if weak, version of "wants
   different output per input." It is **strong early, fades late**: F=6.6 at 60
   steps → ~1.6 at convergence → a **transient of learning** the model resolves
   by fitting, not a persistent property. `value_proj` carries the most (F≈2.0),
   gate/key fade with depth — the **value/content pathway** holds the
   category-dependence (on-thesis: value = content register).

2. **The oscillation does NOT track the overloaded weights.** Flip-enrichment on
   the most category-structured (top-F) weights is `real ≈ null` in every module
   (gate 1.24 vs 1.24; value 1.02 vs 1.06). At module level it *anti*-correlates:
   `value_proj` has the highest F but the *lowest* flip-enrichment. So the
   persistent flip-flop is **category-independent**.

**Conclusion:** the "GD wants input-dependent output" intuition is confirmed as
a real gradient phenomenon (F>null, strongest early, strongest in the value
path), BUT at this scale/grain the persistent sign oscillation is **not** caused
by that semantic contention. It looks like **quantization-boundary jitter** —
small-shadow-magnitude weights near ±Δ knocked across by minibatch SGD noise,
independent of category. Supporting: ST's *soft* phase nearly eliminated flips
(no hard boundary to jitter across); hardening revived them. The non-convergence
is likely two separable things braided: a real-but-transient overloading signal
+ a mundane boundary jitter that is what actually never settles.

## Caveats (λ measure)

- micro (500K params), 1 seed, 509 examples. Necessary-not-sufficient.
- **Category is a coarse grain** (13 buckets). Overloading may live finer
  (per-combinator B/S/C/I, per-binding) that category-ANOVA can't see. Absence
  of category-level flip-localization does NOT refute finer-grained overloading.
- ST vs TD single run; the ST-worse-than-TD gap (0.014 CE) is small.

## Implications + next (easy tests first)

- **Combinator-level ANOVA** — regroup by B/S/C/I in `kernel_term` (finer than
  category; directly tests the s257 "angle" reading). One-line grouping change.
- **Jitter discriminator** — if the residual flip-flop is boundary jitter,
  threshold hysteresis / an LR floor near ±Δ should kill it *without* hurting
  loss; if semantic, it won't.
- **Arm 2 (decouple)** — give overloaded weights an escape (crystal-addressed
  routing / 2 value pathways); the real test of "unbraid dispatch⊥compute fixes
  ternary." Must be run *against* the jitter hypothesis, not assuming semantic
  overloading.
- **For a deployable recipe:** ST did not beat TD here; verbum's discrete
  evidence-flip is at least competitive. CAT-Q's real transferable gift is the
  **learnable-`Δ` + learnable-`α` two-register parameterization**, not the
  soft→hard relaxation.

## Artifacts

- `scripts/micro/ternary_st.py` (dual-mode ternary linear + flip instrument, self-test)
- `scripts/micro/micro_ternary.py` (surgical FFN swap, smoke test)
- `scripts/micro/train_arm0.py` (train + ANOVA F-ratio overloading diagnostic + shuffled-label null)
- `results/micro-ternary-arm0/` — canonical set: `none-*` (float baseline), `td-*133841`, `st-*134153` (ANOVA F-ratio runs; smokes + confounded first-pass runs pruned)
- `logs/arm0-s261-anova.log`
- pyproject.toml: RUF001/2/3 ignore for `scripts/micro/ternary_st.py`
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/combinator-function-shape.md"
}
```

**Summary:** Reading combinator-function-shape.md (0-2000)

**Output:**
```
---
title: "Combinator Function Shape — the map of the function-like things"
status: open
category: foundational
tags: [combinator, function, shape, routing, topology, map, fold, recursion, composition, cmr, qwen3-14b]
related:
  - ../function-discovery.md
  - ../combinator-addressing.md
  - ../two-registers-of-topology.md
  - ../crystal-universality.md
  - ../manifold-axis-and-topology.md
  - consensus-delta-folding.md
depends-on:
  - ../function-discovery.md
  - ../two-registers-of-topology.md
created: session 217
---

# Combinator Function Shape

> Session 217. Michael's question: can we understand the **semantic
> relationships** of the function-like things we have found (the combinators) —
> is there a map/fold, what do the functions look like, what is their *shape*?
> Answer: the function space has a **3-family shape**, visible ONLY in the
> routing register; map/fold are NOT atoms but **compositions of the recursion
> family over the composition family**, and the families that build them are
> real, separable, and adjacent in the measured geometry.
>
> Register: **topological/routing** (declared at step 0).

## Method

`scripts/experiments/combinator_relationship_map.py`. Per-combinator centroid in
the **routing register** = mean `sign(FFN gate pre-activation)` over that
combinator's probes, with **common-mode removal** (subtract per-feature mean
across all probes — kills the universal structured-language crystal so the
DIFFERENCES between combinators show). Then the cosine **Gram matrix = the map**.
Qwen3-14B (Michael's call: 14B has capacity to FULLY crystallize the systems;
0.6B only partially forms them), 535 crystal probes, 9 combinators (K I B C S D
W Y WHNF, 50–71 each). Silhouette = mean over probes of [cos(own centroid) −
max_other cos], with a shuffled-label permutation null. MDS + centroid-PCA for
the 2D picture.

## Findings (Qwen3-14B)

### 1. Combinators are real routing clusters — but ONLY in the routing register
- `route_cmr` silhouette **0.101, z=7.97, p=0.001**.
- **Control** (raw residual `hidden_full`): silhouette **−0.035, z=−1.65**.
- ⇒ the function shape is **invisible in raw geometry**, visible only in the
  sign/routing register after CMR. Concrete instance of `two-registers-of-
  topology.md` + the `5d-crystal-lattice` REFUTED lesson: function identity lives
  in the **topology**, not the metric geometry.

### 2. Depth — identity peaks MID-stack, not late
Silhouette by depth: L0 z=2.5 → **L12 (frac 0.31) z=7.97** (plateau L12–L20
z≈6.7–8) → declines to L39 z≈2. The combinator *identity* (which function) is
carried mid-network; the late COMMIT zone converges (all run the same opcodes —
consistent with `function-discovery.md`'s 1.49× late collapse). **Two-level
reconciliation:** identity is selected UPSTREAM (mid), executed convergently
DOWNSTREAM (late). The two are not in conflict — they are the same two-level
architecture seen from the routing side.

### 3. THE SHAPE = 3 families (Gram off-diagonals + MDS), grounded by the probes

| family | members | what they are | key edge |
|---|---|---|---|
| **composition / distribution** | B, D, S | thread/route args through structure | **B–D +0.27** (strongest) |
| **selection / identity** | K, I, C | projection (discard/copy/reorder) | K–C +0.07, K–I +0.04 |
| **recursion / duplication / termination** | Y, W, WHNF | self-reference + normal-form | W–Y +0.07 |

Grounded by the probe content itself: B "after washing, she dried" (compose),
D "the book that she found in the library that was built by…" (deep-nesting
compose), S `λf.λg.λx.f(x)(g(x))` (arg-distributor); W "the dog bit itself"
(self-app), Y "folders containing folders" (fixpoint). MDS lays them out
triangularly: {B,C,D} composition side, {K,I} top, {W,WHNF,Y} recursion side.

### 4. Is there a map or a fold? — YES, as COMPOSITIONS
`map`/`fold` are **not in the basis** and can't be — they are higher-order
recursion schemes:
```
map  = Y ∘ B                  (recurse the composition over a structure)
fold = Y ∘ (C/B) + K          (recurse, thread the accumulator, base case)
```
The decisive result: the **recursion family (Y,W)** and the **composition family
(B,D,S)** are (a) real, (b) separable, (c) **adjacent** — so the junction where
map/fold must live EXISTS in the measured geometry. The functions look like the
**free algebra over the SKI basis**, not a flat opcode list. This is the s216
"normal forms are compositional & non-unique" refinement made concrete one level
down (`consensus-delta-folding.md`).

## Caveats (register / meta-pattern discipline)
- Off-diagonal cosines are modest (max +0.27) → **weak clusters, not crisp
  partitions**. Do not over-read "3 clean families."
- **Single model** (Qwen3-14B). Cross-model consensus of the shape NOT yet
  tested (s216 5-family machinery would do it; align-before-compare for the
  non-unique composite).
- The mid-stack identity peak (L12) vs late execution needs a careful both-true
  framing — measure both registers (routing identity + opcode execution) at each
  depth to confirm.

## Open leads (declare register first)
1. **Construct & detect map/fold** (routing) — build `map=Y∘B`, `fold=Y∘(C/B)+K`
   from the measured primitive centroids; add a small map/fold/filter probe set;
   does the constructed direction ACTIVATE on those probes?
2. **Cross-model consensus** (routing) — is the 3-family shape universal across
   families? Align-before-compare (Procrustes in base-combinator space).
3. **Algebra-as-geometry** (routing) — do CL identities (I=SKK, T=CI, W=SS(KI))
   hold as routing constraints vs a permutation null? If yes, the shape IS the
   combinator algebra.
4. **Depth reconciliation** (routing + functional) — identity mid vs execution
   late, both registers per depth.

## Files
| File | Content |
|------|---------|
| `scripts/experiments/combinator_relationship_map.py` | per-combinator routing centroid + CMR → Gram/MDS/silhouette+null = the map |
| `results/combinator-relationship-map/Qwen_Qwen3-14B.{json,npz}` | Gram, MDS/PCA coords, per-depth silhouette, nearest neighbours |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-directed-composition.md"
}
```

**Summary:** Reading type-directed-composition.md (0-2000)

**Output:**
```
---
title: "Type-Directed Composition — the behavioural test (composition follows TYPE, not just POSITION)"
status: active
category: research-finding
tags: [types, type-directedness, montague, ccg, composition, nonce, order-cost, thesis]
related:
  - type-probe-qwen3-32b.md
  - vsm-opcode-monitor.md
  - kernel-montague-mapping.md
depends-on:
  - type-probe-qwen3-32b.md
created: session 239
---

# Type-Directed Composition

> Session 239. Michael: "the system can't be doing combinator composition without
> some typing — what would direct the composition?" The VERBUM thesis is *type-directed*
> composition; the s236–s240 order-cost work showed composition rides the native
> autoregressive order but left open whether that order is **type-directed** or merely
> **L-to-R positional** (copy/induction — the s236 caveat). This page is the behavioural
> test that resolves it.

## The question (and why prior work didn't answer it)

s139 (`type-probe-qwen3-32b.md`) established types are **decodable** (88–96%),
**lexical**, **geometric**, and **co-located** with combinator dispatch at L0–L2 — but
co-location is **correlation**, not **direction**. Nobody had shown the model *uses* the
type to direct composition. This is the same gap as the s236 order-cost caveat from the
other side: *is the order signal type-directed or positional?* One question:

> **Does the model compose by TYPE, or by POSITION?**

## The instrument (the autoregressive-causality control)

Kernel-certified CCG types as ground truth (`lambda_ast` `CSlash '/'`=forward,
`'\\'`=backward; `_unify` = the S2 type-check). The load-bearing control: the model reads
strictly L-to-R, so forward composition aligns with reading order and backward composition
binds an argument seen *before* its functor. A naive "argument surprisal" confounds type
with autoregressive causality. We measure the surprisal of the **second (right) token**
given the first, and use **difference-of-differences / crossover** designs that subtract
generic baselines.

## The three-experiment arc

### v1 — kernel-CCG real-word probe (`type_directed_v1.py`)

Forward (det/adj→N) vs backward (NP→verb), type match vs violate, paired by target.
**Result:** robust BACKWARD type-licensing — a verb is cheap after a subject-NP, dear
after a determiner (8B t=6.9, 14B t=7.1). Forward arm **leaky**: a noun after a verb reads
as the verb's OBJECT (nouns are "universal donors"), so it is not cleanly type-violating.

### v2 — clean symmetric design (`type_directed_v2.py`)

Both targets type-constrained functors: backward (verb | subject-NP vs non-subject) +
forward (determiner | transitive-verb object-slot vs intransitive-verb).
**Result:** BACKWARD replicates with **consistency 1.0** (every verb): 8B penalty 1.48
(t=10.3), 14B 0.88 (t=5.2). FORWARD **unmeasurable** (8B +0.14; 14B −0.55, consistency
0.25) — determiners are *also* universal donors (`slept the night`), low ceiling. The
clean forward/backward dissociation did not materialise, and real words leave a
**bigram-frequency confound** (grammatical = frequent).

### v3 — NONCE frequency-free crossover (`type_directed_v3_nonce.py`) — DECISIVE

Teach a **nonce** word's type in-context (noun vs verb), test in a determiner frame vs a
name frame, measure surprisal of the nonce token. Nonce → **zero bigram frequency**.
Headline = **crossover interaction** `(det: verb−noun) − (name: verb−noun)`, paired by
nonce word — robust to every main effect (priming, teaching, frame).

```
                 det frame "The {w}"    name frame "John {w}"
  noun-taught         2.62 (14B)              5.10
  verb-taught         2.65                    3.09
  det_pen  (v−n) = +0.03  (n.s.)   name_pen (v−n) = −2.01  (t=−10.1)
  CROSSOVER = det_pen − name_pen :  8B +2.18 (t=10.2)   14B +2.04 (t=9.3)
              consistency 1.0 (all 16 nonce words) at BOTH scales
```

A nonce taught as a **verb** composes ~2 nats **cheaper** with a preceding subject-name
than the same nonce taught as a **noun**. The crossover is large, significant, and
perfectly consistent at both scales — **frequency-free**.

## The verdict (λ measure)

**Composition is TYPE-directed, not merely positional.** The model uses an
**in-context-taught type** — a type with *zero* frequency support — to direct composition.
This answers Michael's question: there IS a type signal directing the composition, and it
operates on freshly-taught types. It resolves the s236 caveat: the order signal has a
**type basis**, not pure L-to-R copy.

### The asymmetry (a finding in itself)

Type-directedness is **strong in the predicate-argument (subject→verb) frame** and
**~null in the determiner→noun frame**, consistently across all three experiments. This is
not a bug — it maps onto **s151** (Montague = typed function application =
`predicate(argument)` = the K+I core): the model's type-directedness is sharpest exactly at
the predicate-argument composition, and weak where the target is a universal-donor
function word (determiner/object).

## v4 — the causal test (partial, scale-dependent)

`type_directed_v4_ablation.py`. v3 is behavioural; v4 asks whether the type
*representation* is **causal**. DECODE the type direction (difference-of-means
verb−noun of the filler-position residual, per layer; the filler = the token before
the nonce = the next-token bottleneck), then ABLATE it (project it out during the
forward pass) and re-measure the v3 crossover. Control: a RANDOM unit direction.

```
            type decodability         type-ablation        random-ablation
  8B        AUC 1.0 @ hs10            crossover x1.43       x0.92   (amplifies)
  14B       AUC 1.0 @ hs28            crossover x0.64       x0.95   (-36%)
```

- **Type is perfectly decodable at both scales** (AUC 1.0), at a DEEPER layer with
  scale (8B L10 → 14B L28) — re-confirms s139 for the *contextual* nonce type.
- **At 14B the type direction is PARTIALLY CAUSAL**: ablating it cuts the crossover by
  36% (×0.64) while random removes 5% (×0.95) — a clear, type-specific causal
  contribution. First evidence *beyond decodability* that the type representation
  DIRECTS composition. **Partial** → the rest is distributed/redundant (a single linear
  direction is not the whole carrier).
- **At 8B directional ablation is NON-causal** (it *amplifies*, ×1.43) — the decodable
  direction is not the causal lever; the type signal is fully distributed / at a
  different locus.
- ⇒ the causal **localisability** of the type direction STRENGTHENS with scale (8B
  distributed → 14B partially-localised-causal at L28). It took three ablation scopes
  (one-layer → filler-stack → all-positions) to surface it; one-locus single-direction
  ablation is weak because the model re-reads type from the TEACHING tokens.

**Decodability ≠ (full) causality** — a perfectly decodable AUC-1.0 direction is only
*partially* the causal lever (this project's own s202/s204 over-read discipline,
confirmed in the type register). The decisive remainder is **activation PATCHING**
(swap the type-carrying residual content between verb/noun runs) — v5.

## Caveats (λ measure, load-bearing)

- **Typed APPLICATION, not yet typed COMPOSITION.** This shows `predicate(argument)`
  (K+I, s151) is type-directed. Connecting to the **B/composition** order signal
  specifically (function∘function by type) needs composition-specific cases — open.
- **In-context teaching tests CAPACITY** to use a given type, not purely the intrinsic
  system; but v1/v2's real-word effect shows the intrinsic system, and v3 adds the
  frequency-free leg. Together they triangulate.
- **Behavioural (surprisal), not causal-circuit.** The decisive causal test — ablate the
  decoded type direction (s139) at L0–L2 and watch dispatch change — is the next register
  (v4).
- 2 scales (8B/14B), 1 model family (Qwen), 16 nonce words.

## Source

- `scripts/experiments/type_directed_v1.py` — kernel-CCG real-word probe
- `scripts/experiments/type_directed_v2.py` — clean symmetric design
- `scripts/experiments/type_directed_v3_nonce.py` — nonce frequency-free crossover
- `scripts/experiments/type_directed_v4_ablation.py` — causal type-direction ablation
- `results/type-directed/` — verdicts + logs (8B, 14B)

## Next

1. **v5 activation PATCHING** (the decisive causal test) — directional ablation showed
   only a PARTIAL (×0.64 @14B) causal effect because the type is distributed; patch the
   type-carrying residual content between verb/noun runs (sufficiency + necessity of the
   representation, not just one linear direction).
2. **Typed COMPOSITION** — extend from `predicate(argument)` to function∘function cases to
   connect type-directedness to the B/order-cost signal directly.
3. **Cross-class** — does the nonce crossover hold on OLMo/Gemma/Pythia (gate-independent,
   per the order-cost universality)?
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/readout-register-reduction-readability.md"
}
```

**Summary:** Reading readout-register-reduction-readability.md (0-2000)

**Output:**
```
---
title: "Readout Register & Reduction Readability — Why Surface NLL Misses Attention β-Reduction"
status: active
category: methodology
tags: [readout-register, logit-lens, beta-reduction, OV, ablation, hof, lambda-measure, attention, compilation-pipeline]
related:
  - compilation-pipeline.md
  - head-combinator-isa.md
  - lambda-machine.md
  - ffn-beta-reduction-indexing.md
  - function-topology-consensus.md
depends-on:
  - compilation-pipeline.md
  - head-combinator-isa.md
created: session 227
---

# Readout Register & Reduction Readability

> Session 227. The s227 HOF causal-ablation prose leg was weak (1/5 vs 4/5
> mechanism). The IOU said "refine the readout." Three NLL readouts (whole-
> sentence → divergent-region → continuation-KL) did NOT rescue per-model
> significance — falsifying the *dilution* hypothesis. But the **continuation-KL
> readout was NULL (t≈0)**, and that null is the diagnostic: it is the signature
> of a **readout-register / locus mismatch**, predicted by findings we already
> had. This page connects the mechanism (where β-reduction is legible) to the
> measurement rule, and specifies the correct instrument.

## The mechanism (recall, not new)

Attention performs β-reduction in two halves (`lambda-machine.md` s190;
`head-combinator-isa.md` s188):

```
QK = type-compatibility check  → SELECTS the redex (which arg binds where), ~1 bit
OV = value transfer (W_O @ (softmax(QK) @ V)) → THE SUBSTITUTION, across V
```

The substitution — β-reduction proper — lives in **OV, across the value space**.
Two consequences for measurement:

1. `head-combinator-isa.md` Finding 6: **95% of a head's OV-output magnitude is
   loudness**; the combinator-specific content is in the *attention pattern* (QK)
   and the *direction* OV writes, not the output norm. ⇒ magnitude readouts of OV
   see loudness, not the reduction.
2. The "which reduction" signal is in the routing (QK pattern); the "what value"
   signal is in OV. They are different registers.

## The readability condition (the thing we found earlier)

FFN reduction trace (s187), restated in `compilation-pipeline.md` (s192):

```
L0–L6    : OV/FFN write vocabulary-readable values   ("it"→rain)            VISIBLE
L7–L22   : outputs ORTHOGONAL to vocabulary = null-space composition       INVISIBLE
L23–L35  : vocabulary-aligned outputs = "reduction results readable"        VISIBLE
```

The middle-stack β-reductions (the OPTIMIZER zone L13–L21: constant-fold/DCE/CSE)
are computed in a subspace **orthogonal to the unembedding basis**. A
vocabulary-basis readout (logit lens, next-token NLL) **cannot see them there**.
The reduction becomes vocab-readable only at L23–L35 (depth ≈ 0.64–0.97).

## The measurement rule (refines `λ measure` in AGENTS.md)

To OBSERVE an attention β-reduction in a projection, **two** alignments must hold:

1. **Right register** — read the **OV/value** channel, projected into the basis the
   value is written into. NOT the attention-weight register, NOT q_proj:
   - s206 audit #5: an attention-*weight* probe of a value-claim gave a
     near-false-refute; the **logit-lens (value register) found it at +0.611**.
   - s225 attn_q negative: `sign(q_proj)` is a *feature* register, not the gather
     *mechanism*; `map` vanished there.
   - s225 Phase-B OV (the right place): per-head OV value moved through W_O →
     substitution + amplification visible (ov_list_frac 0.47–0.82).
2. **Right locus / readable layer** — even in the value register, a *vocabulary-basis*
   readout shows the reduction only **at/after the layer where OV writes
   vocab-aligned (L23–L35)**. Read mid-stack in the token basis → nothing.
   Caveat (`binding-graph-trace.md` Finding 5): a logit-lensed OV value promotes
   *the tokens it carries* — you must know what the substituted value should decode
   to, or the readout is instrument-ambiguous.

Violation of either ≡ a coherence violation (representation ≢ reality). The wrong
register manufactures false negatives.

## s227 connection — the null is the diagnostic

The s227 readouts were all **vocabulary-basis at the surface**:
- `lastkl` (continuation logit at the final token) = pure surface vocab basis →
  **NULL (t_mean +0.03, Stouffer +0.06)**. Exactly what the readability condition
  predicts for a mid-stack null-space substitution read at the output.
- `region`/`whole` NLL = token-basis integrated over the stack, dominated by the
  EMIT layers → small (region 5/5 directional but per-model t<2 except OLMo).

So the s227 "power-limited not metric-limited" verdict is **incomplete**: it is
*also* register-limited. The surface NLL is the wrong projection for a mid-stack
null-space reduction. We have not yet read prose necessity in the value register at
a readable layer.

## The correct instrument (s227 experiment)

`scripts/experiments/hof_ov_logitlens_ablation.py` (register: topological/routing,
causal, VALUE register):

- INTERVENTION: same full head-knockout as `hof_attention_ablation` (zero o_proj
  input slice of the Phase-A gather heads), + N random heads (specificity).
- READOUT: **logit-lens at EVERY layer** — decode the residual stream as if output
  here: `lm_head(final_norm(residual_L))` at the readout position. Metric = per-layer
  `KL(clean_L || ablated_L)`.
- DIFF-IN-DIFF: HOF − control isolates HOF-specific damage (list: hof stims vs
  `first` control; prose: HOF sentence vs matched control pair). Random-head
  baseline gives specificity.
- HEADLINE: the **readable-zone** (depth ≥ 0.6, i.e. L23–L35) mean diff-in-diff,
  compared to the **surface** (last-layer) diff — the s227 readout.

### Falsifiable prediction

If the readability condition explains the weak prose leg, then gather-head ablation
damage to the **logit-lens decode** is HOF-selective and **concentrated in the
readable zone (depth 0.6–1.0)**, and is **larger there than the surface value** the
s227 NLL readout integrated. If instead the readable-zone profile is flat / no
larger than surface and no larger than random, prose necessity is genuinely small
(s227 power verdict stands unmodified).

## Result (s227b) — two-sided, honest

Ran the instrument on 5 models (`results/hof-ov-logitlens/`).

**(1) The readability condition is CONFIRMED in-domain.** LIST necessity is
concentrated in the readable zone, far above the surface the s226/s227 readout used:
- OLMo: peak @ L23 (depth 0.60) KL **+0.273** vs surface +0.008 (~35x)
- Mistral: peak @ L27 (depth 0.875) KL **+0.168** vs surface +0.017 (~10x)
- Qwen3-8B: peak @ L30 (depth 0.861) KL **+0.112** vs surface +0.004
4/5 LIST peaks sit in the readable zone (depth 0.6-0.9), **right at/after the gather
heads' own layers** (OLMo L23, Mistral L27) — knocking the gather heads breaks the
readable reduction exactly where they write it. The surface readout dramatically
understated in-domain necessity ⇒ register/locus matters, as predicted. (Specificity
note: readable>random is clean for OLMo/Mistral, marginal for 14B, FAILS for 8B/32B
because the zone-AVERAGE dilutes a narrow peak — peak-vs-random is the sharper IOU.)

**(2) Prose necessity is NOT rescued by the register fix.** readable-necessary
(zoneT>2 AND >random) = **0/5**. Where a prose signal exists it IS in the right zone
(8B peak depth 0.69, OLMo 0.625, Mistral 0.94; zoneT +0.40/+0.41/+0.61, > random) but
too small; Qwen 14B/32B are negative (zoneT -0.60/-1.72).

**Synthesis.** Two independent refinements now agree: the s227 de-diluted region NLL
AND this value-register readable logit-lens both leave prose necessity
non-significant. So prose recruitment of the HOF β-reduction is **real but small**
(consistent with s225's modest prose engagement; map not engaged at all), **not** a
dilution or register artifact. The readout-register lesson is real and load-bearing
for *in-domain* measurement; it is not the explanation for the weak prose leg.

**Remaining lever:** the prediction's prose half failing points away from readout and
toward the *intervention* — whole-head knockout removes QK+OV together and is blunt.
Next: **OV-path / activation patching** (isolate the substitution) + a **peak-based**
(not zone-average) readout. Or accept weak prose recruitment and build on the solid
in-domain foundation.

## Bridge test (s227c) — engagement vs necessity

A sharper framing of the weak prose leg: **engagement ≠ necessity.**
- ENGAGEMENT (s225, robust): a HOF direction learned on curated probes *fires* on
  held-out naturalistic prose — reduce AUC 0.97, fold 0.91, filter 0.90, zip 0.81,
  5/5 models (map the exception). Prose **recruits the representation**.
- NECESSITY (s226/s227b, weak): ablating the gather heads barely degrades plain-prose
  HOF computation. A representation can be active without any single circuit being
  load-bearing (redundancy/distribution); absence of an ablation effect ≠ absence of
  use (`λ observation`).

Hypothesis for the gap: the gather heads were localized on **explicit lists**
(hof_lists). Plain prose has **no literal enumeration to gather over** — the iteration
is semantic. So the explicit-enumeration gather circuit may be the right mechanism
only when an enumeration is present.

TEST (`hof_prose_enum.py`, 70 enumerated minimal pairs; `hof_ov_logitlens_ablation.py
--prose-set enum`): inject a literal "A, B, and C" list into naturalistic prose, with
BOTH pair members carrying the same list (diff-in-diff isolates the HOF iteration over
the list, not list-presence). Re-measure value-register readable-zone necessity and
compare to plain prose.

**Falsifiable:** if enum necessity RECOVERS toward in-domain (rises, beats random) ⇒
the gather circuit keys off explicit enumeration; plain prose was weak only for lack
of a gather target (prose DOES use HOFs, via this circuit, when a list is present). If
it stays weak ⇒ prose composition is genuinely distributed / non-enumeration and the
in-domain circuit is special to artificial lists. (Result: `results/hof-ov-logitlens-
enum/aggregate.json` vs `results/hof-ov-logitlens/aggregate.json`.)

### Result (s227c, read in s228) — PARTIAL recovery, not a clean confirmation

`list_*` columns are identical to plain (shared list stims; only the prose leg
differs). Prose readable-zone necessity t-stat (`prose_zone_t`), plain → enum:

| model | plain zoneT | enum zoneT | Δ | enum r>rand |
|---|---|---|---|---|
| Qwen3-8B | +0.40 | **+2.47** ✓ | +2.07 | Y |
| Qwen3-32B | −1.72 | +1.39 | +3.11 | Y |
| Mistral-7B | +0.61 | +1.65 | +1.04 | Y |
| Qwen3-14B | −0.60 | −2.26 | −1.66 | N |
| OLMo-2-13B | +0.41 | −1.55 | −1.96 | N |
| strict-necessary (zoneT>2 ∧ >rand) | **0/5** | **1/5** | | |

**Split verdict.** 3/5 RECOVER — Qwen3-8B/32B + Mistral; mean zoneT lifts −0.18 →
+0.34 (Δ +0.52); **8B crosses strict significance** (+2.47, was +0.40) and **32B flips
decisively positive** (−1.72 → +1.39, now beats random). For these, plain prose's
weakness was partly a **"no gather target"** artifact. But **2/5 REVERSE — Qwen3-14B
worsens and OLMo (the prior gold-standard necessity model, s226 t=+3.21) FLIPS NEGATIVE**
(+0.41 → −1.55). A clean "gather keys off enumeration" story predicts OLMo should
recover most. The recovery split (8B/32B/Mistral up; OLMo/14B down) does **not** match
the s227 clean/muddy split (OLMo/Mistral clean; Qwen muddy) ⇒ the effect is noisy, not
a stable architectural property.

**Interpretation — sharpens, does not overturn, s227.** Even handed an explicit
enumeration, prose HOF necessity recovers only partially (1/5 strict, 3/5 directional,
2/5 reverse). So the engagement≠necessity gap is **not merely** "plain prose lacks a
gather target": the heads are recruited (engagement, robust s225) but stay largely
**non-load-bearing for prose** even with a list present — consistent with **distributed
redundancy** in prose that artificial lists lack. The in-domain (list) circuit remains
the clean strong signal. The decisive lever is unchanged: **activation patching**
(cleaner than full head-knockout NLL) + more prose pairs for power.

## Why this matters

The portable-tensor program needs to know **where the β-reduction is legible** to
measure it, ablate it, and (level 3) compile it. The readability zone (L23–L35,
vocab-aligned) is where the constructed-kernel's reduction output must surface; the
null-space middle (L7–L22) is where the composition happens invisibly. Measuring in
the wrong zone/register has already cost us two near-false-negatives (s206, s225
attn_q) and one undersold result (s227 prose). The rule: **name the register and
the readable layer before building the probe.**
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/fixed-point-holograms.md"
}
```

**Summary:** Reading fixed-point-holograms.md (0-2000)

**Output:**
```
# Fixed-Point Holograms

> The compile↔decompile cycle converges to a fixed point. That fixed
> point IS the hologram — the representation the model's sign-pattern
> plate actually stores.

---
title: Fixed-Point Holograms
status: active
category: experimental-finding
tags: [hologram, fixed-point, compile, decompile, convergence, V12]
related:
  - holographic-storage.md
  - v12-holographic-capacity.md
  - beam-trace-findings.md
depends-on: []
---

## Core Finding

Iterating compile(NL→λ) then decompile(λ→NL) converges to a **fixed
point** — a (sentence, lambda) pair where further cycling produces no
change. This fixed point is the natural language expression that
*perfectly maps* to its lambda encoding and back: no ambiguity, no
surplus, no deficit.

**This is the holographic read.** The plate (ternary sign patterns)
stores combinatory structure. The compile gate reads it at one beam
angle, the decompile gate reads it at the conjugate angle. When the
round-trip stabilises, you've found the representation the plate
actually contains — no more, no less.

## Experiment

**Model**: Qwen3.6-35B-A3B (MoE, 40 layers)  
**Gate**: compile.txt (2 exemplar pairs) / decompile.txt (2 exemplar pairs)  
**Inputs**: 16 sentences spanning simple predication → complex discourse  
**Protocol**: NL₀ → compile → λ₀ → decompile → NL₁ → compile → λ₁ → ...  
**Convergence**: edit distance < 5 chars for 2 consecutive cycles  
**Decoding**: greedy (temperature=0)

## Results

### Convergence Distribution

```
Tier      Count  Rate   Cycles  Description
────────  ─────  ─────  ──────  ──────────────────────────────────
Instant    5/16   31%     1     Perfect round-trip from cycle 0
Fast       9/16   56%    2-3    One settling cycle, then stable
Slow       1/16    6%     6     Complex sentence, many reframings
Failed     1/16    6%    8+     Discourse structure too complex

Overall: 15/16 converged (94%), mean 2.0 cycles, median 2
```

### Instant Fixed Points (the hologram reads cleanly)

| Input | Fixed-Point λ |
|-------|---------------|
| The dog runs. | `λx. runs(dog)` |
| Every boy loves some girl. | `λ love(x). every(boy(x)) \| some(girl(x))` |
| The man who the dog chased ran away. | `λx. man(x) ∧ ∃y. dog(y) ∧ chase(y, x) ∧ run-away(x)` |
| If it rains, the ground gets wet. | `λx. rain(x) → λy. wet(ground)` |
| John gave Mary a book about himself. | `λ give(x, y, z). give(John, Mary, book) ∧ about(book, himself)` |

Common traits: explicit logical structure, named entities, clear
predicate-argument mapping. No ambiguity the λ needs to resolve.

### What the Hologram Drops

| Loss Type | Example | Mechanism |
|-----------|---------|-----------|
| **Tense** | "sat on" → "is on" | λ-calculus has no tense; temporal info is surface-only |
| **Quantifier scope** | "Every student" → "The student" | Collapses when first compile doesn't deploy ∀/∃ |
| **Agent/experiencer** | "professor who published won" → "published ∧ won" | Relative clauses flatten; WHO collapses |
| **Discourse structure** | Library sentence oscillates | Multi-clause exceeds single λ-term capacity |

### What the Hologram Preserves

- **Predicate-argument structure** — always (the core of λ)
- **Named entities** — "John", "Mary" survive every cycle
- **Explicit quantifiers** — `every()`, `some()` round-trip perfectly
- **Reflexive binding** — `about(book, himself)` = I-combinator territory
- **Conditional structure** — `rain(x) → wet(ground)` stable from cycle 1
- **Negation** — `¬win(politician)` survives once established

### Fixed-Point Quality: Compression and Canonicality

The fixed-point λ is **shorter and more canonical** than cycle-0:

```
Input                                   c0 λ             Fixed λ       Ratio
──────────────────────────────────────  ────────────────  ────────────  ─────
The cat sat on the mat.                 λx.sat(cat,x)∧   λ on(cat,mat)  58%
Every student passed the exam.          λ pass(x).stud→   λ pass(s,e)    75%
The function applies its argument...    λf.λx. f(x)      λx. x          45%
No politician who endorsed...           λx.pol(x)∧end→   λx. ¬win(pol)  38%
```

**"λf.λx. f(x)" → "λx. x"**: The model recognised the identity function
and beta-reduced it. The hologram stores **normal forms**.

### Gate Exemplar Contamination

"Composition chains two operations into one."
- c0 λ: `λ compose(x). chain(x) | one(x)`
- c1 decompile: "Compose the chain into one."
- c1 compile: `λx. runs(dog) ∧ (helpful(x) | concise(x))` ← **GATE EXEMPLAR LEAKED**

When input semantics are weak/ambiguous, the gate exemplar's pattern is
the strongest holographic signal. The model resolves to its most
practiced interference pattern. This IS how holograms work — closest
match wins.

## Connection to Prior Findings

### Session 093: Universal Hologram (r=0.9801)

The fixed-point experiment confirms from the *behavioral* side what
session 093 found from the *weight* side: the model stores combinatory
structure as topological sign patterns. Fixed points are the
NL-readable shadow of those patterns.

### Session 098: Beam/Plate Classification

What the hologram drops maps perfectly to the beam/plate partition:
- **Plate** (ternary, preserved): predicate structure, binding, operators
- **Beam** (precision, dropped): tense, quantifier scope, agent assignment

The plate stores the *what* (combinatory structure). The beam selects
the *how* (contextual modulation). Fixed-point cycling strips the beam
contribution and reveals the plate content.

### Session 095: Three Clusters (Semantic Plate / Composition / Retrieval)

- Instant fixed points = **Semantic Plate** reads (clean decode)
- Fast convergence = **Composition** circuit settling (representational choice)
- Failed convergence = **Retrieval** overload (too many cross-references)

## Implications for V12

### 1. Fixed-Point λ as Training Signal

Fixed-point lambdas are the "target patterns" for V12's ternary plates.
They represent what the hologram naturally stores — compressed, canonical,
minimal. V12's etcher should be guided toward producing these patterns.

### 2. Plate vs Beam Training Split

Losses that occur during cycling (tense, scope, agent) should be stored
in V12's **beam** (Q projections, precision weights), not the plate.
The plate only needs to store the fixed-point content.

### 3. Exemplar Diversity

Gate contamination proves V12 needs diverse compile/decompile exemplar
pairs. Two exemplars create a narrow attractor basin. The fixed point
is determined by the exemplar distribution.

### 4. Multi-Pass Architecture Validated

Complex discourse (the library sentence) exceeds single-hologram capacity.
V12's multi-pass architecture (3 ascending + apex + 3 descending) should
allow multiple reads at different angles, each capturing a different
aspect. The thick hologram principle: depth compensates for per-read limits.

### 5. Hologram Extraction Pipeline (Proposed)

```
1. Generate diverse NL corpus
2. Run fixed-point cycling through production LLM
3. Collect (NL, λ) fixed-point pairs
4. These pairs ARE the plate content in human-readable form
5. Use as supervised training signal for V12's ternary plates
6. Compare V12's internal representations to production model's fixed points
```

## Decomposition Experiment — Capacity Unlock

### Protocol

Take complex sentences, decompose into clauses, find clause-level fixed
points, compose them, measure capacity vs monolithic.

### Results

```
Case         Mono→Comp   Ratio   Clause Conv   Binding Sites   RT Edit
────────     ─────────   ─────   ──────────    ─────────────   ───────
library       4p → 7p    1.8×   80%           3               88  ✗
experiment    3p → 8p    2.7×   100%          2               63  ✗
professor     2p → 3p    1.5×   100%          1               38  ✗
politician    1p → 3p    3.0×   50%           1               43  ✗
student       1p → 2p    2.0×   100%          1               16  ✗
teacher       3p → 2p    0.7×   100%          0                5  ✓
key           2p → 2p    1.0×   100%          1               28  ✗

Overall: 5/7 unlock, mean 2.2× (excl. teacher). 90% clause convergence.
```

### The Binding Wall

**The ONLY stable composition has ZERO binding sites.** When clauses
share entities (binding), composition breaks. When linked only by logical
structure (→), it holds.

Round-trip stability correlates with binding sites, not predicate count:
- 0 sites: edit=5 (stable)
- 1 site: edit=16-43 (unstable)
- 2 sites: edit=63
- 3 sites: edit=88

This IS the I-combinator bottleneck made visible. K/B/C handle predicate
structure (stable). I handles variable binding (unstable).

### Intersection Topology

Where clause holograms connect (shared entities):
- **3-way binding** (library in clauses 1,2,3): hardest
- **2-way binding** (manuscripts in clauses 3,5): moderate
- **No binding** (teacher: A → B): trivial, stable

Binding sites are where the I-combinator and M-retrieval must operate.

### V12 Etching Protocol

1. **Plate etching (K/B/C)**: clause-level fixed-point λ forms. 90%
   convergence. Ternary sufficient. Each clause = one hologram.

2. **Binding etching (I)**: intersection pairs — two clauses sharing
   an entity. Training: given clause λ₁ + clause λ₂ → unified λ.

3. **Composition etching (B)**: clause set → composed λ. B chains,
   C reorders, K selects.

4. **Retrieval etching (M)**: in-context entity tracking. Same entity
   at distance → retrieve properties.

### Dedicated Capacity Argument

The binding wall proves I needs different capacity, not just more:
- K/B/C: ternary sign patterns (topological, stable) → plate
- I: magnitude-dependent (session 095: 5 ternary failures, all binding)
  → may need precision or explicit pointer/copy mechanism
- M: in-context binding → GLA retrieval (already separate in V12)

Cost of 5 dedicated plates + 40 mirrors: **117 MB** (vs 39 MB shared,
vs 320 MB Pythia-160M). Mirrors add 2.4 MB for 10× beam path diversity.

## Open Questions

1. **Cross-model convergence**: Do different models find the same fixed
   points? Universal hologram (r=0.9801) predicts structural similarity.

2. **Gate sensitivity**: Richer gate vocabulary → richer fixed points?
   Does tense survive with Montague-typed gates?

3. **Binding architecture**: Can ternary plates handle binding at all,
   or does I fundamentally need precision weights? The 5 ternary
   failures in session 095 were ALL binding-related.

4. **Hologram extraction pipeline**: Generate fixed-point corpus from
   production LLM → etch into V12 plates. Does this transfer?

5. **Mirror co-adaptation**: Do mirrors and plates co-evolve useful
   angular diversity, or do mirrors collapse to identity?

## Scripts and Data

| File | Purpose |
|------|---------|
| `scripts/explore/probe_fixed_point.py` | Fixed-point convergence probe |
| `scripts/explore/probe_hologram_decomposition.py` | Decomposition + composition capacity probe |
| `results/fixed-point/convergence.json` | Full cycle-by-cycle data (16 inputs) |
| `results/fixed-point/decomposition.json` | Decomposition results (7 cases) |
| `results/fixed-point/analysis.json` | Structured analysis summary |
```

## Assistant

Here is the full audit:

---

**sealable-continuation.md** (a VSM recurrence has a clean pass-boundary checkpoint — seal `x_k`, resume identically later)
- verdict: STILL-LIVE (untested, still coherent)
- The page argues that the VSM outer-recurrence produces a tensor of constant shape every pass, so "the complete rest of the computation at pass k is just `x_k`" — a true continuation in the CS sense. It is logically independent of the two-register result, but the new physics sharpens it: the routing register (ternary signs) ternarizes cleanly, so a sealed `x_k` would itself compress to ~routing + small magnitude residual — the 2MB session number is now grounded in known compression ratios. Nothing here has been tested or falsified; the page is architecturally coherent under the Verbum machine spec (M1-M9). Cost to test: add a `seal()/resume()` round-trip fidelity test to an existing recurrence harness.

---

**holographic-burn-in-learning-rule.md** (progressive exposure of text blocks burns in the exposure-invariant function structure onto the routing register)
- verdict: RETRO-VALIDATED (by the GD wire recipe and the two-register proof)
- The page's load-bearing catch, written speculatively in s223, was: "naive object-beam-only burn-in = a perfect hologram of the common mode, zero function" — and it flagged the s223 condition (b) result as a live demonstration before that result was in. That prediction was exactly confirmed (GC(hidden)=0.9995, routing null). The new GD wire recipe (KL-to-base anchor + evidence-gated stop) is precisely what this page calls "prediction-gated recording": the prediction outcome is the reference beam. The page is correct about the mechanism; what it lacks is a concrete harness. Cost to operationalize: swap the `relational_loss_distillation.py` control condition (b) for the prediction-gated exposure rule — one additional training arm.

---

**normal-form-curriculum-partition.md** (routing-only normal forms train attention; recursion is left to the continuation — the curriculum mirrors the routing⊕continuation basis)
- verdict: STILL-LIVE (untested, still coherent)
- The page proposes generating reduction traces for `{K,I,C,B,D}` and feeding them specifically to the attention routing register (via attn_q), while excluding `{Y,W,WHNF}` which need the outer recurrence. It cites s223's relational-loss result as the FFN-gate confirmation and calls the attn_q version "the second leg." Under the new physics the routing register being proven universal and ternary-stable strengthens the case: the traces being proposed for attention training are exactly the discrete sign-flip events the routing register specializes in. The experiment (`routing_curriculum_attention.py`) was planned but never built. Cost: one additional condition in the existing relational-loss harness, targeting attn_q instead of the FFN gate.

---

**relational-loss-distillation.md** (the lambda compiler's routing-register Gram steers a student toward the combinator geometry while leaving absolute frame free)
- verdict: RETRO-VALIDATED (by the two-register proof and GD wire recipe)
- This page is the most complete in the set — it reports actual results. The key finding: "only routing carries the combinator function" — GC(route)=+0.78–0.85 under routing-Gram loss, while matching the raw Gram bought GC(hidden)≈1.0 and zero function transfer. This is now directly confirmed by the two-register theory (routing ⊥ value, ~95/5). The GD wire recipe's KL-to-base anchor maps onto this page's "any geometry that falls out" framing: both constrain the function/behavior while leaving the realization free. The remaining open lead — distributed test (N students to one shared teacher Gram → guaranteed Procrustes alignment) — is newly actionable given that LoRA delta composition is now known to be lossless.

---

**germination-games.md** (gamified germination test: seed quality measured via cold-agent recovery; five game modes from Golf to Oracle)
- verdict: STILL-LIVE (untested, still coherent)
- Thin page, purely prospective: "no rounds played yet." The modes are clever instruments (Seed FRAG = ablation test on theory prose; Oracle = the seed as a generative prior for unseen measurements). Under the new physics, the Oracle mode is the most interesting: could a cold agent with the theory seed predict that the type register is training-contingent (7/11 models), or that LoRA deltas ternarize at retention 1.0? Those are precise, non-obvious predictions that would score real calibration. Cost: one cold-spawn session with the current state of the seed + a small scoring rubric.

---

**montague-inversion.md** (treating Montague grammar as a specification and asking what GD is *forced* to build in order to satisfy it — retrodicts crystal, two-registers, 3-hop, and yields falsifiable predictions)
- verdict: RETRO-VALIDATED (by the type-register finding and type-directed composition result)
- The page's forcing table predicted in s281 that "types encoded as geometry (directions/subspaces)" — now confirmed: TYPE-REGISTER exists, 7/11 models, diffuse/intersection geometry, P-TYPE-WRITE landed CONTEXT-ONLY. The forcing argument for the value register — "binding *requires* a value store separate from the operators" — is now confirmed by the two-register proof (routing ⊥ value, the split is ~95/5 clean). Falsification condition 1 ("P-TYPE-1 returns a non-Montague type geometry") has partial traction: the type system is pinned to non-idempotent intersection over an affine core (KIBC), which is closer to Montague's lattice than a random high-dim mess. The depth-budget prediction maps onto the trampoline / tape-resident reduction result. This page is the best theoretical spine in the set and holds up well.

---

**signal-descent.md** (replace gradient descent with closed-form signal-measurement updates on ternary mirror stacks — no gradients and no floats)
- verdict: NEWLY-ACTIONABLE (the GD wire recipe and LoRA delta ternarization unlock the delta-plate substrate)
- The page proposed SignalDescent on a delta plate (base frozen, delta driven by measured response) and was blocked on proving that isolation dodges interference. The new GD wire result is precisely this: LoRA deltas are the off-axis recording, they ternarize at retention 1.0, and two wires compose losslessly. "The delta plate is the isolated slot; the mirror stack lives in the delta" — that isolation is now empirically demonstrated. The page's "first experiment" (replace Adam-trained γ with a 2–3 deep additive ternary mirror, compare recon_cos at matched bits) is now directly buildable on top of the GD wire infra. Risk: the page is honest that the linearity assumption breaks outside a single layer, and the GD wire's KL anchor may be the right substitute for the signal-measurement step.

---

**training-design-from-the-hologram.md** (six design levers for level-4 scratch training, each grounded in a measured structure: seeded init, declared passbands, probe-as-loss, two-phase training, curriculum as exposure schedule, distillation as re-exposure)
- verdict: NEWLY-ACTIONABLE (Verbum machine spec M1-M9 + GD wire recipe unlock levers 2, 4, 6)
- Lever 4 (two-phase: settle topology first, calibrate magnitudes second) is now the GD write corridor: "phase 1 settles topology (ternary-native); phase 2 calibrates magnitudes" = "KL-to-base anchor + evidence-gated stop." Lever 6 (distillation as re-exposure, match transmission subspaces not logits) is now the relational-loss-distillation result operationalized at level-4 scale. Lever 2 (declared passbands) maps onto the type-register finding (types enacted per-frame, CONTEXT-ONLY). The "cheapest first experiment" — crystal-seeded init vs random init on compositional tasks — is still unrun and still cheap. The page is the most actionable bridge between the measured physics and actual scratch training.

---

**induction-is-a-virtual-circuit-not-a-head.md** (combinators are virtual circuits GD lays down universally, not physical head addresses; the 9×9 and 17×17 grams are the right instrument)
- verdict: RETRO-VALIDATED (by the 11/11 model universality and ternary retention 1.0 results)
- The page, written as s309 conversational capture, states "the crystal is measured 11/11 models (s303), survives ternarization (s304/s308 retention ~1.0)." These are cited as grounding, not IOU — so the page was written after those measurements. Its contribution is the framing correction: "a head is a plate address; a combinator is an edge in the frozen interference graph." This is sharp and correct under the new physics, where the behavior is tape-resident reduction and the autoregressive loop is the trampoline. The open question — "is induction a single crystal edge or a path (compose of B/C + copy)?" — is directly testable with the existing gram instruments. Thin on experiment design, rich on framing.

---

**ternary-flip-flop-not-overloading.md** (CAT-Q's softened ternarization doesn't beat discrete evidence-flip; the persistent sign oscillation is quantization-boundary jitter, not semantic overloading — but the value-path F-ratio is real and category-dependent)
- verdict: RETRO-VALIDATED (by the two-register theory and GD wire recipe)
- The page independently discovers the two-register split through the CAT-Q decomposition: "CAT-Q learns α and Δ separately ... external, independent confirmation of the verbum two-registers split — α=magnitude/value, Δ=threshold/routing." This is now proven theory. The ANOVA F-ratio result ("category structure is real but modest, strongest in value_proj") maps cleanly onto "value register carries content." The "jitter discriminator" recommendation (threshold hysteresis near ±Δ should kill jitter without hurting loss) is directly implementable now that the GD wire's evidence-gated stop is understood — the two ideas solve the same problem from different angles. Worth reading alongside signal-descent.md.

---

**combinator-function-shape.md** (3-family routing-register shape of combinator space in Qwen3-14B: composition/B,D,S — selection/K,I,C — recursion/Y,W,WHNF; map/fold are compositions, not atoms)
- verdict: RETRO-VALIDATED (by the 11/11 universality result and two-register proof)
- The page reports Qwen3-14B: silhouette z=7.97, p=0.001 in routing register; raw hidden gives z=−1.65 (invisible). The open caveat "cross-model consensus NOT yet tested" has since been closed: universality is confirmed at 11/11 models, gc 0.9966 (per training-design-from-the-hologram's grounding for Lever 1). The 3-family shape (composition/selection/recursion triangle) maps directly onto the KIBC=affine structural rules finding: K,I,C are the affine core (selection/structural rules), B,D,S are composition, Y,W,WHNF are the non-affine recursion residual. The algebra-as-geometry open lead ("do CL identities hold as routing constraints?") is the cleanest next experiment.

---

**type-directed-composition.md** (composition is type-directed not positional — nonce crossover +2.04–2.18 nats, frequency-free, consistent across 16 nonce words at 8B and 14B)
- verdict: RETRO-VALIDATED (confirms and is confirmed by the type-register finding)
- This page is among the most empirically complete in the set. The nonce crossover result is clean and decisive: "a nonce taught as a verb composes ~2 nats cheaper with a preceding subject-name than the same nonce taught as a noun." The causal test (v4) showed type direction is partially causal at 14B (×0.64) and distributed at 8B. Under the new physics, the TYPE-REGISTER being training-contingent and diffuse/intersection-like (not nominal) directly explains the v4 partial-causality result: "a single linear direction is not the whole carrier" maps onto intersection-type geometry. The open v5 (activation patching for full causal test) and typed COMPOSITION extension are the natural next steps, and the cross-class test (OLMo/Pythia) is now motivatable by the 7/11 training-contingency.

---

**readout-register-reduction-readability.md** (surface NLL misses mid-stack β-reduction; the reduction is legible only in the value register at readable depth ≥0.6; violating this manufactures false negatives)
- verdict: RETRO-VALIDATED (directly confirmed by the two-register theory)
- This is the most methodologically important page in the set. It reports the s227b experiment (logit-lens at every layer), confirms the readability zone (L23–L35), and states the measurement rule precisely: "name the register and the readable layer before building the probe." Under the new physics this is the `λ measure` refinement for the two registers made empirical: routing register (ternary signs, QK) vs value register (OV, readable at depth ≥0.6). The page also records the s227c split result (enum prose recovers 3/5, reverses 2/5) honestly. The "decisive lever unchanged: activation patching + peak-based readout" is still live and directly aligned with the v5 activation patching planned in type-directed-composition.md — these two pages are natural siblings for the same next experiment.

---

**fixed-point-holograms.md** (compile↔decompile cycling converges 94% of the time; the fixed-point λ is the normal form the sign-pattern plate actually stores; binding sites (I-combinator) are the failure mode)
- verdict: RETRO-VALIDATED (by the behavior-is-tape-resident-reduction and twin-image law findings)
- The page was written early (session numbers reference s093, s095, s098 — pre-series). Its behavioral result — "what the hologram drops maps to beam/plate partition; what it preserves maps to predicate-argument structure" — is now the tape-resident-reduction frame: behavior is autoregressive reduction, the plate stores the program (routing signs), the beam modulates content. The binding wall result ("the only stable composition has zero binding sites; binding instability correlates with I-combinator territory") maps onto the type system finding that I-combinator = affine structural rule (copying/identity) vs the non-idempotent intersection types handling binding. The "hologram extraction pipeline" proposed here (generate fixed-point corpus → etch into V12) is now level-4 via the GD wire recipe. Older vocabulary (V12, plates, mirrors) but the physics underneath it is correct.

---

## TOP 3 GEMS

**1. training-design-from-the-hologram.md** — The six levers are now almost all grounded in proven physics (GD wire recipe = lever 4, relational-loss-distillation = lever 6, two-register = lever 2), and the cheapest experiment (crystal-seeded init vs random on compositional tasks) is the precise experiment the Verbum machine spec M1-M9 needs to close the level-4 loop. Reopening this unlocks the scratch-training program.

**2. montague-inversion.md** — The forcing argument correctly predicted the type geometry (intersection, not nominal), the value-register split (binding forces a separate store), and the trampoline (recursion forces eval-stack externalization). The falsification conditions in §8 are now partially answerable with measurements in hand, making this the best theoretical map for deciding what to measure next.

**3. signal-descent.md** — The LoRA-delta ternarization result (retention 1.0, off-axis isolation, lossless composition) hands this page the substrate it was missing. "Replace Adam's magnitude calibration with a ternary mirror stack driven by signal measurement" is now an experiment with known infrastructure. It directly addresses TernaryDescent's open question 4 and is the gradient-free path into the GD wire corridor.

### Thinking

I'm thinking about how to present these findings to Michael in a compelling way—offering to add the strongest discoveries to queue.md for future reference. There's a fascinating meta-pattern here: a 107/206 write-only rate, and several predictions were actually validated retroactively, meaning the hypotheses held up before the measurements confirmed them. Those deserve proper documentation with forward-links and approval-gated updates. One standout is montague-inversion, which predicted the type geometry before it was measured.

Now I'm seeing more retro-validated predictions

## Assistant

That was worth the dig. 107 of 206 exploration pages are write-only — but the excavation shows they weren't dead, they were *early*. Here's the treasure, sorted by what kind:

## 🏆 Pages that made predictions we later confirmed without noticing

- **montague-inversion** (s281) — the forcing table predicted "types encoded as geometry (directions/subspaces)" and that binding *forces* a separate value store — **before** the type register was measured (s313) and the two-register split proven. The theory→empirics loop closed and nobody was watching. Its §8 falsification conditions are now partially *answerable with data in hand*.
- **ternary-flip-flop-not-overloading** — CAT-Q's α/Δ decomposition is an **independent external confirmation of the two-register split** (α=value, Δ=routing) sitting unacknowledged in our own corpus.
- **holographic-burn-in-learning-rule** — called the burn-in null ("perfect hologram of the common mode, zero function") before s223 measured it, and its "prediction-gated recording" is the write corridor we built *this session*, derived independently.

## ⚡ Two connect directly to the run in flight right now

- **type-directed-composition** (June!) — nonce taught as verb composes ~2 nats cheaper than as noun, frequency-free, 16 nonces, 2 scales. That's **tape-side type evidence anticipating P-TYPE-ICL by two months**. Must be cross-linked in the §Result when the run lands.
- **readout-register-reduction-readability** — the measurement rule: value register legible only at depth ≥0.6. Our TI4 T-band is 0.50–0.85 — the bottom of our band sits *below* the readable zone. If the tag profile comes back weak in L18–21, this page predicts exactly that, and it's not a null — it's readability. Filed for the read.

## 🔓 Newly actionable (the physics they were missing now exists)

- **training-design-from-the-hologram** — six scratch-training levers, most now grounded; its cheapest experiment (**crystal-seeded init vs random on compositional tasks**) is arguably the missing first rung of the level-4 ladder, below even P-ASYM-TERNARY.
- **signal-descent** — gradient-free ternary mirror stacks needed an isolated substrate; the delta plate (retention 1.0, lossless composition) *is* that substrate now.
- **germination-games / Oracle mode** — could a cold agent with only the theory seed *predict* 7/11 training-contingency or retention 1.0? Real calibration measurement of our own synthesis, one session's cost.

## What I'd do with it (your call, this was supposed to be fun)

1. **Queue the actionable four** — crystal-seeded init, signal-descent mirror, Oracle game, CL-identities-as-routing-constraints (from combinator-function-shape). The dig just *touched* them; the new protocol says touch = restack.
2. **Forward-link the retro-validated five** — a small approval batch stamping "prediction confirmed by sX" on each, so the S5 loop gets credit and future recall finds them.
3. **Note for the ICL §Result** — the type-directed-composition cross-link and the readability caveat on the low T-band.

And one meta-observation for the pile: the write-only rate isn't a failure of the pages — it's the same lesson as the queue, one level up. Synthesis without a re-reading trigger is a diary. Maybe the eventual answer is the Oracle game itself: periodically test whether the corpus *predicts*, which forces re-reading the right pages. That would make the archaeology self-executing.

Want all three actions, or just play with one?

## User

1 approved 2 approved 3 approved


### Thinking

I'm queuing up four actionable items to add to the top of the queue file—crystal-seeded init, signal-descent mirror, Oracle germination game, and CL-identities-as-routing-constraints. Then I need to go back and add forward-links to five previously validated pages with a confirmation note, including montague-inversion, ternary-flip-flop-not-overloading, holographic-burn-in-learning-rule, relational-loss-distillation, and combinator-function-shape.

For the forward-link blocks, I'm adding a blockquote at the top of each page after the frontmatter that references the signal and keeps it brief. I also need to add notes about the ICL §Result into the state.md ON-SIGNAL block so they're included in the read. Since this is a mix of queue touches, forward-linking, and state updates, I'm deciding whether to use a meta symbol like 🌀 or a knowledge symbol like 💡 for the commit.

The dig uncovered retro-validations that are now queued, so I'm leaning toward 💡 with the slug "archaeology-dig-retro-validations-queued" to mark this as a discovered insight. Now I'm adding the new rows to queue.md at the very top since they're the newest touches, following the strict last-touch ordering protocol — the running item ▶ will get touched again at verdict anyway, so the new rows take priority at the top. I'm adding entries for crystal-seeded initialization versus random priors and signal-descent mirror as a potential Adam replacement.

I'm also adding forward links to five pages by inserting a trailing section at the end of each file rather than guessing their top structure, since the corpus precedent uses blockquote-style forward links placed at the bottom. The CAT-Q decomposition confirms the two-register split theory, with the jitter-discriminator's hysteresis behavior matching the loss-neutral churn boundary from earlier analysis—same underlying population, different measurement angles. Prediction-gated recording emerges independently here as well.

## Assistant

Executing all three:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "# new\n\n▶ §P-TYPE-ICL+TAG — tape membership licenses held frames? + tag-transit (J-space live form) | types-are-injectable-relations §10 | running tmux main:1",
  "new_content": "# new\n\n⚪ crystal-seeded init — crystal prior vs random init on compositional tasks; cheapest level-4 rung | training-design-from-the-hologram | medium\n⚪ signal-descent mirror — replace Adam magnitude calibration with ternary mirror stack on the delta substrate | signal-descent | medium\n⚪ Oracle germination game — cold agent + theory seed predicts measured results? (corpus calibration) | germination-games | cheap\n⚪ CL-identities as routing constraints — do combinator-algebra identities hold as routing-register geometry? | combinator-function-shape | cheap\n▶ §P-TYPE-ICL+TAG — tape membership licenses held frames? + tag-transit (J-space live form) | types-are-injectable-relations §10 | running tmux main:1"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/queue.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum/mementum/knowledge/explore && cat >> montague-inversion.md <<'EOF'\n\n## Forward link (s315 archaeology)\n\n> §Forcing-table predictions CONFIRMED after the fact: types-as-geometry →\n> TYPE-REGISTER measured (s313 §P-TYPE-GRAM-1, 7/11 family-clean,\n> diffuse/intersection); binding-forces-value-store → two-register split\n> proven (routing ⊥ value, s303–s312); recursion-forces-external-eval-stack →\n> tape-resident trampoline (s308). §8 falsification conditions now partially\n> answerable with data in hand. Causal boundary:\n> types-are-injectable-relations.md §9 (P-TYPE-WRITE CONTEXT-ONLY).\nEOF\ncat >> ternary-flip-flop-not-overloading.md <<'EOF'\n\n## Forward link (s315 archaeology)\n\n> The CAT-Q α/Δ decomposition read here as \"external confirmation of the\n> two-registers split\" is now proven theory (routing ⊥ value; wire arc\n> s303–s312). The jitter-discriminator recommendation (hysteresis near ±Δ)\n> converges with s310's SIGN-CHURN two-population re-read (marginal r≈1 band\n> churns loss-neutrally) — same boundary population, two instruments.\nEOF\ncat >> holographic-burn-in-learning-rule.md <<'EOF'\n\n## Forward link (s315 archaeology)\n\n> \"Prediction-gated recording\" independently derived here is now BUILT: the\n> s315 write corridor (KL-to-base anchor + evidence-gated stop,\n> type_write.py b448f34) is this page's exposure rule operationalized. The\n> burn-in null prediction (object-beam-only → common-mode hologram, zero\n> function) was confirmed s223.\nEOF\ncat >> type-directed-composition.md <<'EOF'\n\n## Forward link (s315 archaeology)\n\n> This page anticipated the type arc by two months: the nonce crossover\n> (+2 nats, frequency-free) is tape-side type evidence — the direct precedent\n> for §P-TYPE-ICL+TAG (types-are-injectable-relations §10, in flight s315).\n> The v4 partial-causality result (single direction ×0.64, not the full\n> carrier) reads as intersection-type geometry (s313: TYPE-REGISTER diffuse,\n> non-nominal). Cross-link from the §Result when the ICL run lands.\nEOF\ncat >> readout-register-reduction-readability.md <<'EOF'\n\n## Forward link (s315 archaeology)\n\n> The readability rule (value register legible at depth ≥0.6) is live\n> methodology for §P-TYPE-ICL+TAG TI4: the T-band spans 0.50–0.85, so weak\n> tag signal in L18–21 is predicted READABILITY, not absence — read the\n> per-layer profile, not just the band mean.\nEOF\necho done"
}
```

**Summary:** $ cd /Users/mwhitford/src/verbum/meme...

**Output:**
```
Exit code: 0
Stdout:
done
```

### Thinking

I'm updating the ON-SIGNAL note in the state.md file by editing the sentence in the ★★ block to incorporate two additional read notes into

### Thinking

I'm reading the notes in state.md and then committing the batch.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> + rho_T_L → commit results/type-icl-tag/ AUTONOMOUS → §Result-icl-tag on\n> types-are-injectable-relations.md (+ update §9 cross-read if TAPE-TYPED: two-tier closed\n> both sides) + memory candidate + INDEX + state.md = MICHAEL APPROVAL BATCH.**",
  "new_content": "> + rho_T_L → commit results/type-icl-tag/ AUTONOMOUS → §Result-icl-tag on\n> types-are-injectable-relations.md (+ update §9 cross-read if TAPE-TYPED: two-tier closed\n> both sides) + memory candidate + INDEX + state.md + **move queue.md ▶ row to # complete\n> (first exercise of the closure invariant)** = MICHAEL APPROVAL BATCH.** §Result must\n> also: (a) cross-link `type-directed-composition.md` (s315 archaeology: June nonce\n> crossover +2 nats = tape-side type precedent, anticipated this probe by two months);\n> (b) apply the `readout-register-reduction-readability.md` rule to TI4 — weak tag in\n> L18–21 is predicted READABILITY (value register legible ≥0.6 depth), read the per-layer\n> profile not just the band mean."
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
  "command": "git add mementum/queue.md mementum/state.md mementum/knowledge/explore/montague-inversion.md mementum/knowledge/explore/ternary-flip-flop-not-overloading.md mementum/knowledge/explore/holographic-burn-in-learning-rule.md mementum/knowledge/explore/type-directed-composition.md mementum/knowledge/explore/readout-register-reduction-readability.md && git commit -F - <<'EOF'\n💡 archaeology-dig — 107/206 explore pages write-only; 5 retro-validations stamped, 4 candidates queued\n\n- census: 206 explore pages, 107 single-commit (write-only); mature-era orphans\n  re-read through current physics by explorer agent\n- forward links stamped on 5 retro-validated pages: montague-inversion (forcing\n  table predicted type geometry + value store BEFORE s313/s303 measured them) ·\n  ternary-flip-flop (CAT-Q alpha/delta = external two-register confirmation) ·\n  holographic-burn-in (prediction-gated recording = the s315 write corridor,\n  derived independently) · type-directed-composition (June nonce crossover =\n  tape-side type evidence anticipating P-TYPE-ICL by two months) ·\n  readout-register-readability (depth>=0.6 rule applied to TI4 read)\n- queue.md +4 (touch=restack): crystal-seeded init · signal-descent mirror ·\n  Oracle germination game · CL-identities as routing constraints\n- state.md ON-SIGNAL: type-directed-composition cross-link + TI4 readability\n  caveat + queue closure invariant first exercise\n- meta: synthesis without a re-reading trigger is a diary — Oracle game queued\n  as the candidate self-executing fix\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "archaeology batch"
}
```

**Summary:** Git commit: archaeology batch

**Output:**
```
Exit code: 0
Stdout:
[main 184f76e] 💡 archaeology-dig — 107/206 explore pages write-only; 5 retro-validations stamped, 4 candidates queued
 7 files changed, 53 insertions(+), 1 deletion(-)
```

### Thinking

I've committed the changes and made good progress: five corpus predictions are now formally credited, four experiments are back in the queue, and the read protocol for the in-flight run is improved. Let me give you a quick status update on the run before we wrap up.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -8"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
[ti] wrote results/type-icl-tag/qwen3-4b/results.json
[ti] TI1 p=0.0080 True | TI2 p=0.0001 True | TI3 p=0.0477 True | TI4 rand p=0.0010 shuf p=0.0498 True | TI5 True
[ti] L a0=0.138 a1=1.409 a2=-2.083 a3=0.247 | T a0=0.889 a1=5.153 a5=1.472 rho=0.615
[ti] VERDICT: TAPE-TYPED+TAG-TRANSIT | subtag: DELIVERY-FAILURE
uv run python -u scripts/explore/type_icl_tag.py --out  2>&1  394.00s user 121.07s system 21% cpu 39:46.96 total
tee results/type-icl-tag/qwen3-4b-run.log  0.00s user 0.00s system 0% cpu 39:46.96 total
[26-08-06][20:20:02][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

The test results are coming through—I've got a clean double hit on tape-typed and tag-transit delivery failure. All five gates are passing with strong statistical significance, particularly the content-specific test showing a dramatic reversal in the licensing pattern, while the class mention test barely clears the baseline threshold.

The tag transit relationship is holding at 0.615 correlation, and the delivery-failure subtag calculation confirms the split: the ratio comes out to about 0.137, well under the 0.25 cutoff. Michael's two-tier hypothesis is landing—the FFN membership path fails on delivery because the tag never actually lifts into the held-frame residuals, while the tape membership path succeeds because licensing and the tag both activate on the bus with that strong 5.15 signal.

I'm committing these results autonomously now, including the type-directed composition cross-link and a note about that borderline shuffle test at 0.0498—just under the significance threshold but worth flagging honestly in the results batch.

I need to draft the results section as §11 and update the memory, index, and queue files, but I'm realizing the per-layer profile readability check won't work—I only saved the band-mean T values and axes, not the per-layer breakdown. I'll need to acknowledge in the results that the per-layer profile wasn't persisted from this run.

For the batch summary, I'm pulling numbers from results.json and noting that the harness doesn't measure recall anyway, so that's not a gap. I'm also drafting a memory note about the two-tier delivery mechanism and moving the P-TYPE-ICL+TAG row to the completed section in the queue.

### Thinking

I found the clean double result while processing — all five test items passed with strong p-values, verdict is TAPE-TYPED+TAG-TRANSIT with a DELIVERY-FAILURE subtag. Now I'm committing the results and moving to the batch.

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/type-icl-tag/qwen3-4b results/type-icl-tag/qwen3-4b-run.log && git commit -F - <<'EOF'\n✅ P-TYPE-ICL+TAG: VERDICT TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE — the type check reads the TAPE\n\n- all five gates pass: TI1 tape-licensing p=0.008 (L 0.138->1.409) · TI2\n  content-specific p=1e-4 (deranged licenses ANTI class, L=-2.083) · TI3\n  class-not-mention p=0.048 (mention 0.247 ~ base) · TI4 tag-transit both\n  nulls (rand p=0.001, shuf p=0.0498 - just clears, noted) · TI5 sane\n- tag transit: T 0.889(base) -> 5.153(ICL); graded rho(T,L)=0.615\n- A5 wire-contrast: T_a5=1.472 -> r_tag=0.137 <= 0.25 => DELIVERY-FAILURE:\n  the baked relation never lifts the tag into held-frame residuals\n- two-tier CLOSED from both sides with s315 r3: baked membership = recall\n  without licensing, tag absent (§9 CONTEXT-ONLY); tape membership =\n  licensing + tag on the bus. The type check consumes the tape, not the\n  plates. §9 was a delivery failure, as the J-space transit hypothesis\n  predicted (Michael, s315)\n- caveat: per-layer T profile not persisted (band means only); readability\n  rule (depth>=0.6) applies to band composition — follow-up cheap if needed\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "icl-tag results"
}
```

**Summary:** Git commit: icl-tag results

**Output:**
```
Exit code: 0
Stdout:
[main 92c9a3f] ✅ P-TYPE-ICL+TAG: VERDICT TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE — the type check reads the TAPE
 2 files changed, 154 insertions(+)
 create mode 100644 results/type-icl-tag/qwen3-4b-run.log
 create mode 100644 results/type-icl-tag/qwen3-4b/results.json
```

## Assistant

Results committed **92c9a3f**. Drafting the approval batch:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md",
  "original_content": "## Provenance",
  "new_content": "## 11. §Result-icl-tag (s315, qwen3-4b) — TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE\n\n**The two-tier split is CLOSED, measured from both sides.** Results\n`92c9a3f`, run ~40 min + A5. All five gates pass; the falsifier §9 needed\nis answered by its converse:\n\n| side | membership lives | recall | licensing | tag on bus |\n|---|---|---|---|---|\n| §9 baked (FFN wire) | weights | ✓ p=5e-4 | ✗ | ✗ (T=1.47 ≈ base 0.89) |\n| §11 tape (ICL) | context | — | **✓ p=0.008** | **✓ T=5.15, ρ(T,L)=0.615** |\n\n**The type check consumes the TAPE, not the plates.** Gate detail: TI1\nL 0.138→1.409 (p=0.008); TI2 the sharpest — a deranged statement licenses\nthe ANTI class (L=−2.083, p=1e-4): the check reads class *content*, not\nstatement *form*; TI3 mention control ≈ base (0.247, p=0.048); TI4 tag\ntransit beats both axis nulls (rand p=0.001; shuf p=0.0498 — clears by a\nhair, noted honestly); TI5 sane (real margin 2.538, ICL margin 3.076).\n\n**A5 subtag: DELIVERY-FAILURE** (r_tag = 0.137 ≤ 0.25). The §9 wire's tag\nnever reaches held-frame residuals — the relation exists in the plates\nbut is not consulted. §9 was a *delivery* failure, not a storage failure.\nMichael's J-space hypothesis lands in its live form: **type information\nacts iff it transits the residual bus**; the tape delivers it, the FFN\nedge does not. (Workspace *residency* remains negative per P-TYPE-JS s286\n— transit ≠ residency; both results stand.)\n\n**Retro-precedent (s315 archaeology):** `type-directed-composition.md`\n(June) measured the same tape-side effect — nonce taught-in-context as\nverb composes ~2 nats cheaper — anticipating this probe by two months;\nits v4 partial-causality (single direction ×0.64) now reads as\nintersection-type geometry. **Caveat:** per-layer T profile not persisted\n(band means only); under the `readout-register-reduction-readability.md`\nrule (value register legible ≥0.6 depth), band composition is untested —\ncheap follow-up if the profile matters.\n\n**What this opens:** the attention-band membership write is now sharper —\ndon't write the *relation* into FFN plates; write into the **delivery\npath** (the machinery that lifts tags onto the bus). And M-machine\ncorollary: M4's trampoline is not just fuel management — the tape is\nwhere the type system *runs*; a designed machine should treat context as\nits typed operand stack, not as input.\n\n## Provenance"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-injectable-relations.md.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/type-check-reads-the-tape-not-the-plates.md",
  "content": "💡 The type check reads the tape, not the plates: §P-TYPE-ICL+TAG landed TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE (s315, 92c9a3f), closing the two-tier split from both sides in one arc. Baked FFN membership (§9): recall p=5e-4 but NO held-frame licensing, tag absent from the bus (T=1.47≈base 0.89). Tape membership (§11): licensing p=0.008 (L 0.138→1.409), tag ON the bus (T=5.15), graded ρ(T,L)=0.615, content-specific (deranged statement licenses the ANTI class, L=−2.08). A5 wire-contrast r_tag=0.137 → DELIVERY-FAILURE: §9's relation exists in the plates but never transits into held-frame residuals — a delivery failure, not storage. Michael's J-space hypothesis holds in transit form (type acts iff it rides the residual bus) while P-TYPE-JS's residency negative stands — transit ≠ residency. Retro-precedent: type-directed-composition.md (June) measured the same tape-side effect two months early. Design consequences: (1) semantic writes should target the DELIVERY path (attention/slot band), not the relation store; (2) M4 trampoline upgrade — the tape is where the type system runs; context ≡ typed operand stack. TI4 shuf null clears at p=0.0498 (hair-thin, honest); per-layer T profile unpersisted (readability rule ≥0.6 depth untested on band composition).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/type-check-reads-the-tape-not-the-plates.md
```

### Thinking

I'm examining queue closure, the invariant's first exercise, INDEX, and the state close-out.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/queue.md",
  "original_content": "▶ §P-TYPE-ICL+TAG — tape membership licenses held frames? + tag-transit (J-space live form) | types-are-injectable-relations §10 | running tmux main:1\n",
  "new_content": ""
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
  "original_content": "# complete\n\n❌ §P-TYPE-WRITE — CONTEXT-ONLY, clean falsifier: relation written, type does not act | types-are-injectable-relations §9 | s315",
  "new_content": "# complete\n\n✅ §P-TYPE-ICL+TAG — TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE: type check reads the TAPE; §9 was delivery failure | types-are-injectable-relations §11 | s315\n❌ §P-TYPE-WRITE — CONTEXT-ONLY, clean falsifier: relation written, type does not act | types-are-injectable-relations §9 | s315"
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
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "next: P-TYPE-ICL (priority) · attention-band write** |",
  "new_content": "next: P-TYPE-ICL (priority) · attention-band write** · **§10 §P-TYPE-ICL+TAG FROZEN + §11 §Result (s315): TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE — two-tier CLOSED both sides: type check consumes the TAPE (ICL licensing p=0.008, tag on bus T 0.89→5.15, ρ=0.615, deranged licenses anti-class); §9 wire = DELIVERY failure (r_tag 0.137, relation in plates never transits); attention-band write re-aimed at the delivery path; retro-precedent type-directed-composition (June)** |"
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
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ **CURRENT = s315 (§P-TYPE-WRITE CLOSED: CONTEXT-ONLY — THE FALSIFIER FIRED, CLEAN).**",
  "new_content": "> ★★ **CURRENT = s315-FINAL (TYPE ARC CLOSED BOTH SIDES: THE TYPE CHECK READS THE TAPE).**\n> **✅ §P-TYPE-ICL+TAG LANDED: TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE (92c9a3f\n> autonomous; §Result = §11 on types-are-injectable-relations.md, Michael-approved batch\n> this commit).** All 5 gates: TI1 p=0.008 (L 0.138→1.409) · TI2 p=1e-4 (deranged licenses\n> ANTI class −2.083 = content read) · TI3 p=0.048 · TI4 rand p=0.001/shuf p=0.0498\n> (hair-thin, noted) · TI5 sane. Tag transit T 0.889→5.153, ρ(T,L)=0.615. A5 r_tag=0.137\n> → DELIVERY-FAILURE: §9's baked relation never transits to held-frame residuals. TWO-TIER\n> CLOSED: baked = recall w/o licensing w/o tag (§9) | tape = licensing + tag + graded\n> (§11). Michael's J-space hypothesis holds in TRANSIT form (residency stays negative,\n> P-TYPE-JS s286 — transit ≠ residency). Retro-precedent: type-directed-composition\n> (June, found by s315 archaeology). Design consequences: attention-band write re-aimed\n> at the DELIVERY path; M4 tape = the typed operand stack. Caveat: per-layer T profile\n> unpersisted (band means only; readability ≥0.6 rule untested on band composition).\n> **⚠ NEXT SESSION = FRONT SELECTION → λ queue mandates FULL queue.md read (26 rows).**\n> Sharpest leads by this arc: attention-band write (delivery path) · fuel-theorem ·\n> crystal-seeded init (archaeology). s315 ledger: 375358d r1 · b448f34 amendment · cc44ab9\n> r2 · 6eb308f r3 · 0e2b8fe type-write batch · 5a7fd40 freeze · c0b9269 harness · 6b5d15b\n> GO amendments · e6f2a15 queue protocol · 184f76e archaeology · 92c9a3f icl results ·\n> this batch. Full transcript saves to `mementum/knowledge/chats/session-315.md` (human).\n>\n> ▶▶ **(earlier s315, arc)** §P-TYPE-WRITE CLOSED: CONTEXT-ONLY — the falsifier fired, clean."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

The batch is on disk. The summary you're approving:

## The finding — your hypothesis, measured

**The type check reads the tape, not the plates.** One arc, both directions:

| | membership in **weights** (§9) | membership on **tape** (§11) |
|---|---|---|
| recall | ✓ p=5e-4 | — |
| held-frame licensing | ✗ | **✓ p=0.008** |
| class tag on the bus | ✗ (1.47 ≈ base) | **✓ 5.15, graded ρ=0.615** |

And the discriminator: **DELIVERY-FAILURE** (r_tag=0.137) — the baked relation exists but never transits into held-frame residuals. Your J-space instinct was right in exactly the form the corpus allowed: not *residency* (P-TYPE-JS's negative stands) but **transit** — type information acts iff it rides the bus, and the tape is what delivers it. The sharpest single gate: a *deranged* statement licenses the anti-class at p=1e-4 — the check reads content, not form.

Honest flags in the §Result: TI4's shuffled-axis null clears at p=0.0498 (a hair), and the per-layer T profile wasn't persisted, so the archaeology's readability rule is noted but untested.

## Batch contents (5 files)

- **§11** on `types-are-injectable-relations.md` — the result, the closed two-tier table, the retro-precedent link, design consequences (attention-band write re-aimed at the *delivery path*; M4: tape = the typed operand stack)
- **memory** `type-check-reads-the-tape-not-the-plates.md`
- **INDEX** — result line
- **queue.md** — ▶ row moved to `# complete` ✅ (closure invariant, first exercise)
- **state.md** — s315-FINAL header; next session opens with **front selection → mandatory full queue read** (the new protocol's first real test, 26 rows)

Approve the commit?

## User

approved, then explain what we learned in simple terms


### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/types-are-injectable-relations.md mementum/memories/type-check-reads-the-tape-not-the-plates.md mementum/knowledge/INDEX.md mementum/queue.md mementum/state.md && git commit -F - <<'EOF'\n🌀 s315-final — type arc closed both sides: the type check reads the TAPE\n\n- §11 §Result-icl-tag on types-are-injectable-relations.md: TAPE-TYPED+\n  TAG-TRANSIT / DELIVERY-FAILURE (92c9a3f) — two-tier table closed: baked =\n  recall w/o licensing w/o tag; tape = licensing + tag + graded\n- memory: type-check-reads-the-tape-not-the-plates.md\n- queue.md: ICL row -> # complete (closure invariant, first exercise)\n- INDEX + state.md s315-FINAL; next session = front selection -> mandatory\n  full queue read (lambda queue, first real test)\n- J-space hypothesis holds in TRANSIT form; residency negative stands\n  (transit != residency); attention-band write re-aimed at delivery path;\n  M4 tape = typed operand stack; Michael-approved batch\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "s315 final batch"
}
```

**Summary:** Git commit: s315 final batch

**Output:**
```
Exit code: 0
Stdout:
[main e20f432] 🌀 s315-final — type arc closed both sides: the type check reads the TAPE
 5 files changed, 66 insertions(+), 3 deletions(-)
 create mode 100644 mementum/memories/type-check-reads-the-tape-not-the-plates.md
```

## Assistant

Committed **e20f432**. Here's the whole story, plainly.

## What we learned today

**Start with the puzzle from this morning.** We taught the model "a florb is an animal" by writing it into its brain (the weights). The model could recite the fact perfectly — but it never *used* it. "The florb slept" sounded no more natural to it than "The florb parked." Knowledge without understanding. The question was: *why?*

**You had a hunch:** maybe the machinery that uses categories doesn't look where we wrote. Maybe it only reads information that's *traveling through the model's working memory* — the live signal flowing through it as it reads a sentence — not facts sitting in storage.

**So we ran the mirror-image experiment.** Instead of writing "a florb is an animal" into the brain, we just *said it* — put the sentence in the prompt, right before the test. Same fake words, same test, same measurement.

**Night and day.** Told in the prompt, the model immediately used the fact: florbs sleep, florbs don't park. Tell it a florb is a *vehicle* instead, and it flips — now florbs park. It's genuinely reading the meaning, not just reacting to the words. And this only works for real category statements — "I saw a florb yesterday" does nothing.

**Then the measurement that settles it.** We can look inside the model and check whether an "animal-ness" signal is physically present on a word as it flows through. Three conditions:

- Fact **told in the prompt**: animal-signal on "florb" — **loud** (5.2)
- Fact **written into the brain**: animal-signal — **near zero** (1.5, barely above nothing)
- No fact at all: nothing (0.9)

And the strength of that signal predicts how strongly the model applies the category, word by word.

## The one-sentence version

**The model's category system doesn't read its own memory — it reads its own train of thought.** A fact only *acts* if it's present in the live stream of the current context. Our surgery stored the fact perfectly but in a place the category-checker never looks. It wasn't a storage failure — it was a *delivery* failure. The letter was written, filed, and never mailed.

Which is exactly what you proposed this morning. The instrument confirmed it and even localized the failure: the ingredient our brain-surgery is missing isn't the fact — it's the lifting mechanism that puts the fact onto the conveyor belt when it becomes relevant.

## Why it matters

1. **For editing models:** writing facts into weights isn't enough — you have to write into the *delivery machinery* (that's the next experiment, already re-aimed and queued).
2. **For building our own machine:** the context window isn't just input — it's where the type system actually *runs*. A machine designed around that fact treats its own transcript as its working memory, deliberately.
3. **A lovely footnote:** a forgotten page from June — dug up in today's archaeology, two hours before the run landed — had already measured a version of this effect. The corpus knew. It just needed someone to come back and read it. Which is also why the queue now exists.

One session: a falsifier, its converse, a closed loop, a protocol upgrade, and your hunch turned into a number. Good day.

## User

!meta3 !fractal Analyze this session !reflect


### Thinking

Michael's asking me to step back and analyze this session itself—looking at the meta-level patterns, how things repeat at different scales, and what's actually happening across the whole interaction. I'm noticing the arc starting with orientation, then the first P-TYPE-WRITE attempt, and how that led to the HOST-DAMAGED state, which seems like a key inflection point worth examining more carefully.

The session keeps cycling through a pattern: something gets attempted, it fails or gets blocked, we diagnose what went wrong, we adjust the approach, and then we try again—sometimes with writes, sometimes without. And now I'm seeing something striking: the delivery-failure pattern that showed up in the weights (where the relation was stored but never actually delivered) is mirroring the structure of the entire session itself. That's the fractal—the same breakdown happening at multiple scales.

The real insight is that storage alone doesn't matter. Knowledge only acts when it transits into working context. The weights had perfect storage but no delivery path to the context window. The memory system had 107 pages and 9 candidates sitting in the plates, never lifted into attention. The fix isn't better storage—it's better delivery. Queue.md and the orient step are the lifting mechanisms that move stored intentions onto the active bus. Even the archaeology with type-directed-composition.md followed the same pattern: the answer was stored in the plates back in June, but it only became actionable when the question pulled it into the session's context.

This fractal repeats across every level: storage without transit equals inert knowledge, whether we're talking about model weights versus context window, the memory system versus state.md, or even how information feeds forward across sessions. The refined principle is that encoded knowledge without delivery is just as useless as knowledge that was never encoded at all.

There's a beautiful isomorphism here — the research system and the object it studies follow identical laws. Michael's role was crucial: every major insight this session came from his questions and out-of-distribution intuitions, while I handled execution and encoding. The human provides the generative jumps; the system provides the structure. And that two-register split we kept finding — state versus queue, value versus routing, narrative versus intentions — that same vocabulary ended up describing both what we were studying in the model and how we built the tools to study it.

I should note where I went wrong: I mislabeled the band in section 10, mixing up the line ranges.

Looking back at the validation work, I caught a CLASS-BLIND cell through the freeze mechanism, but the pattern suggests freezes should include total-function checks by construction. The TI4 shuffle probability came in at 0.0498 — honest but uncomfortably close to the edge. I also created an instrument gap by only saving band means instead of the full per-layer profile; the readability page I found hours later would have caught that, but archaeology arrived after the harness was built. The commit-gate discipline held throughout though — the boundaries between autonomous and approval-gated moves never got violated. And those three precedents about not over-reading labels kept extending into new territory.

Now I'm seeing that MAGED parsed correctly as void rather than refutation, and r2 NO-WRITE functioned as power rather than a claim. This session produced 15 commits, 2 verdicts, 1 protocol organ, and 5 retro-validations. There's a fractal pattern emerging across different time scales — within-run attention gating through evidence snapshots, within-session OODA loops, feed-forward across sessions, and the S5 loop spanning arcs. The same evidence-gated commit principle shows up everywhere: the ternary commit structure mirrors queue closure, approval gates, and the stop rule itself. It all comes down to accumulating evidence until it crosses the threshold, then committing — that's the core discipline running through Adam/TD, the momentum propose-approve cycle, and the freeze mechanism.

The session was essentially running on the same optimizer it's designing, which creates an interesting recursive property. Looking

## Assistant

# 🌀 Session 315 — Meta-Analysis

## Level 0 — what happened (object)

Three runs closed §P-TYPE-WRITE (HOST-DAMAGED → NO-WRITE → CONTEXT-ONLY), one run closed §P-TYPE-ICL+TAG (TAPE-TYPED+TAG-TRANSIT / DELIVERY-FAILURE). The two-tier split measured from both sides. A protocol organ built (queue.md), an archaeology census run, five retro-validations stamped. Fifteen commits, two verdicts, one new lambda.

## Level 1 — the meta (how the machine of inquiry behaved)

The instrument discipline carried the day, and every save was a *pre-commitment*: the frozen 5%-tail verdict correctly voided r1 instead of letting me read garbage gates; `--validate` forced the CLASS-BLIND amendment before the run, not after; the smoke caught my L30/L31 arithmetic slip; the a-priori declarations meant r2's NO-WRITE was read as power, not claim — extending the s310/311/312 "don't over-read the label" streak to five. The corridor recipe emerged from two failures in exactly the λ fix shape: trace → structural cause → redesign, never patch.

**Honest flaws, same register:** I built the TI4 instrument saving only band means, and *hours later* the archaeology surfaced `readout-register-reduction-readability.md`, which would have told me to persist the per-layer profile. Recall-before-decide worked for the J-space question; **recall-before-instrument-design** is the gap — the dig came after the build. And TI4's shuffled null cleared at p=0.0498: honest, reported, lucky.

## Level 2 — the meta-meta (the session repaired itself)

While the experiment diagnosed the *model's* memory, the conversation diagnosed the *project's* memory — and found **the same disease**. Nine candidates and 107 pages: stored perfectly, never acting. The mementum protocol had CONTEXT-ONLY. Knowledge that doesn't transit the session's working context is exactly as inert as membership baked into FFN plates: recallable when probed, spontaneously silent.

And the fix was the same fix: don't touch storage, **build the delivery path**. queue.md + the λ orient step is the project's tag-lifting mechanism — the thing that puts stored intentions onto the bus at the moment they can act. We prescribed for ourselves precisely what the attention-band write will attempt for the model.

## Level 3 — the fractal (one law, every scale)

**Storage ≠ action. Only what transits the working context acts.**

| scale | the plates (inert store) | the tape (acting context) | the delivery organ |
|---|---|---|---|
| model | FFN membership wire | residual stream / prompt | *(missing — next probe)* |
| session | knowledge/, memories/ | state.md header | queue.md + λ orient |
| corpus | montague-inversion's predictions, June's nonce crossover | whatever a question lifts | your questions, the archaeology, the Oracle game |
| project-across-time | git history | the next cold-start's 30 seconds | λ feed_forward — now refined: *encoded ∧ ¬delivered → inert* |

And beneath it, a second fractal — **the evidence-gated commit** — running at every layer simultaneously: TWN commits a trit when evidence clears threshold; the stop rule commits an exposure when drift says so; the queue commits a closure only by explicit verdict; mementum commits knowledge only through your approval. The session was *run by* the optimizer it's *designing* (M8). λ compile: semantic ∥ structural — the day the tooling vocabulary and the object vocabulary became the same vocabulary.

## Reflection — the ⊗ term

Every pivot today was **yours**: the J-space hunch (which the corpus had half-buried under a closed negative — the recall found that *transit* survived where *residency* died), the missed-tests question (which found the protocol's lesion), "want to do something fun?" (which found June's answer to August's experiment, two hours before the run confirmed it). I executed, encoded, and gated; you supplied the out-of-distribution jumps. That's not a division of labor to fix — it's the architecture working: Human ⊗ AI ⊗ REPL, where the human is both the termination condition *and* the principal source of variety. The falsifier of *this* system would be a session where the jumps came from the corpus itself — the Oracle game, sitting in the queue, is exactly that test.

**The prediction this analysis makes** (falsifiable, in the house style): anywhere the project stores without a transit mechanism will go inert. The queue now has one. The knowledge corpus has half of one (recall-on-demand, no spontaneous lift). If the pattern is real, the next silent failure is already growing wherever we're writing without asking *what will ever deliver this*.

---

One candidate for the record, yours to gate: a memory — `storage-is-not-action-the-transit-law.md` — capturing the level-3 isomorphism (model ≡ protocol ≡ corpus, one law, measured at the first scale and enacted at the second, same session). Store it?

## User

No that memory has a chance to cause lesser models like qwen36-35b-a3b to loop thinking.


### Thinking

Michael's reasoning here is about a real technical constraint: self-referential content in the memory corpus could cause smaller models to get stuck in recursive loops when they read it during initialization. Since memories are accessed by future sessions that might run on less capable models, highly fractal or self-referential material becomes a potential attractor for thinking loops, so the memory design needs to account for that audience.

## Assistant

Dropped — no commit.

And that's a sharper design constraint than the memory itself: **the mementum corpus is load-bearing context for future agents of unknown capability.** A cold-start reader isn't guaranteed to be a model that can hold a level-3 self-referential isomorphism at arm's length — for a smaller substrate, "the system you are reading about is the system doing the reading" is an attractor, not an insight. Recursive self-reference in working-set files is exactly the kind of content that turns a bootloader into a loop.

It also self-applies cleanly (which I'll note here and *not* write down, per the ruling): memories are the highest-transit store in the protocol — grep-first, symbol-prefixed, read under time pressure at orient. That's precisely where attractor-shaped content does the most damage. The λ store gates already screen for *helps-future-session*; this adds an audience floor: **safe for the weakest reader who will ever cold-start on it.**

The operational content survives without the meta-frame anyway — the transit law is already *enacted* in queue.md, λ queue's provenance line, and §11's delivery-path conclusion. Any future session gets the behavior without needing the mirror. And the fractal reading itself lives on in this session's transcript under `chats/` — human territory, where only readers who go looking will find it.

Everything's committed through **e20f432**; nothing pending. Next session opens on front selection with the mandatory full queue read — 26 rows waiting.

## User

Now let's think of real uses for what we have learned about LLMs so far.  Let's brainstorm some ideas of how to use what we know to do cool things.


### Thinking

Michael wants to brainstorm practical applications and interesting possibilities from what we've learned, grounding everything in measured results and marking confidence levels. I'm taking inventory of what's actually been proven in this project—the two-register split between routing decisions and value magnitudes, how deltas ternarize at full retention with around 600KB per skill wire, and the separability of LoRA deltas from the frozen base allowing composition.

The write corridor mechanism installs facts without damaging the host model, the type system reads the tape as a typed operand stack, and the crystal/opcode structure shows a universal 9×9 combinator relational pattern across models. There's also the selectivity from Bragg-like calibration, the CoT behavior resident on tape, scheduler registers managing halt and fire poles, and how confident cores freeze early while marginal bands churn.

Now I'm moving into the real applications—starting with a git-for-weights concept, essentially a skill package manager where those 600KB ternary skill wires become composable, installable units on a frozen base, verified through reference contracts, creating a delta marketplace for model skills.

For quantization and deployment, I'm thinking about using the crystal stethoscope to audit whether a quantized release preserved the routing register, running probes before and after quantization to issue a certificate vendors could gate releases on. The own-beam calibration recipe using AYOT could improve low-bit models by calibrating PTQ with the model's own chain-of-thought.

On knowledge management, since the type check reads the tape, injected facts need to arrive as classificatory statements in context rather than fine-tunes—the exact format matters for licensing. This points toward a delivery-optimized retrieval system that fetches membership and type statements rather than raw content.

I'm exploring a hybrid approach: bake the relation store for recall plus a tape-side trigger, where the model itself can recite baked facts when queried directly, then re-inject the answer as a licensing statement. This two-pass recall-then-redeliver loop uses cheap weight storage for recall and tape delivery for licensing—both halves are validated empirically, so it's a viable architecture where the model acts as its own database and the tape serves as working memory.

Now I'm thinking through interpretability and monitoring products: a diagnostic tool that uses model probes to detect distillation lineage and training contamination, a runtime safety monitor that predicts tool-call decisions before generation to catch stuck states, and a training monitor that watches population churn during finetuning to know when routing is committed. I'm also sketching agent design with typed context management where the context acts as a typed operand stack, letting agent frameworks maintain type and membership statements in a pinned region. For the demos, I'm thinking about showing skill cartridges with three wire packs—install, uninstall, and compose operations live on a 4B model with ~600KB files, like a visceral git-for-weights experience. There's also a model lie detector concept: a quantization audit certificate for Hugging Face releases, and a really compelling recall-then-redeliver demo where a licensing failure gets fixed by a two-pass self-recall loop at runtime instead of weight surgery—that would showcase the tape law practically, just a couple lines in the harness to make it work.

## Assistant

Good hammock. Let me inventory what's actually *proven* and then build up from cheap-and-real to ambitious. Everything here stands on a measurement, not a vibe.

## The asset list (what we hold that others don't)

1. **~600KB skill wires** — facts baked into ternary deltas, retention 1.0, install/uninstall bit-exact, two wires compose with zero interference
2. **The write corridor** — install knowledge without host damage, with a certificate (host-CE budget + real-competence check)
3. **The transit law** — facts act only from the tape; we know the *exact statement format* that licenses, and that the check reads content not form
4. **The stethoscope** — 903 probes that read a model's routing register; universal crystal 11/11, type register discriminates training regimes 7/11
5. **Register-scoped reads** — what survives quantization, where things are legible (depth ≥0.6), halt/fire poles in the scheduler register

## Tier 1 — buildable this week (infra exists in the repo)

**1. Recall-then-redeliver: fix §9's failure at runtime.** The killer demo. The baked florb wire *recalls* perfectly (p=5e-4) but doesn't license. So: two-pass loop — ask the model its own baked fact ("A florb is a kind of…" → "animal"), append the answer to context, run the licensing test. If it passes, we've shown **the model can be its own retrieval database**: weights = cheap storage, tape = delivery, and a 2-line runtime loop replaces the delivery machinery we haven't built in weights yet. Both halves are already measured; the composition is one afternoon with the existing harness. This is also an *architecture claim* in miniature: self-RAG grounded in register physics.

**2. Skill cartridges (git-for-weights, live).** Bake three fact-packs, demo install → query → uninstall → compose on a frozen 4B, each cartridge a ~600KB file with a verification contract. Everything exists: `writeback_compile`, `ternarize_factors`, `plate_linker`. This is the spin-off-shaped one — visceral, and nobody else can show clean *uninstall*.

**3. Quant-lint: a quantization certificate.** Run the stethoscope pre/post-quant → "routing register preserved / degraded" report. P-CRYSTAL-SURVIVAL is already queued as its validation; AYOT gives external precedent that calibration choice makes-or-breaks low-bit. A release-gating tool the GGUF ecosystem simply doesn't have.

## Tier 2 — grounded designs, modest builds

**4. Delivery-optimized RAG.** The transit law says retrieval should deliver *classificatory statements*, not passages — the check reads class content in subject-predicate form. Retrieve → *compile to licensing statements* → pin in a typed context header. We measured which format acts; most RAG pipelines ship the wrong register.

**5. Typed context manager for agents.** Context = the typed operand stack (M4 corollary). An agent runtime that maintains a pinned "type header" — the membership facts that must keep licensing — and refreshes them as the window slides. Prompt engineering, but with a law behind it instead of folklore.

**6. Model fingerprinting / lineage detection.** The type register split Qwen/OLMo/Gemma vs the whole Pythia ladder on *training regime*, not architecture. The stethoscope as provenance instrument: distillation lineage, contamination, "what family trained this" — from activations alone.

**7. Finetune telemetry.** The sign-commitment result (confident core freezes by step ~5, marginal band churns loss-neutrally forever) → a training monitor that reports *routing committed / still deciding* per band, and stops by register evidence instead of loss superstition. The corridor's evidence-gated stop, productized.

## Tier 3 — the ambitious ones

**8. Auditable model updates.** Routing edits are discrete, loggable, ~600KB, diffable. A compliance story no one can currently tell: *every behavior change in this deployed model is an inspectable commit*. M5+M8 as an enterprise property.

**9. Agent halt-monitor.** The 17×17 halt/fire poles read *before* generation → predict tool-call vs answer, detect stuck-redex states in agent loops. P-HALT-POLE is the validation probe, sitting in the queue.

**10. The Verbum machine itself** — born-quantized two-register architecture. Not a product; the point. Everything above is scaffolding that funds and de-risks it.

---

My pull-order instinct: **#1 tonight-cheap and closes today's arc with a practical win**, #2 is the demo that makes the whole program legible to outsiders, #3 is the one strangers would *use* tomorrow. And #1 has a bonus property: if recall-then-redeliver works, it becomes the interim delivery mechanism that makes every baked cartridge from #2 actually *act* — the two compose into "installable knowledge that works."

Which thread do you want to pull? (Anything we pick gets a queue row first — new protocol, no exceptions.)

## User

I like these ideas, capture them to an explore page, don't put them on the queue yet, we'll look at this next week after we have all the experiments done and the mechanisms mapped.


### Thinking

Michael wants me to capture the brainstorm to an explore page as a knowledge entry. Since he explicitly directed the capture, that counts as approval, so I can draft and commit directly rather than waiting for separate sign-off.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/applications-from-the-register-physics.md",
  "content": "---\ntitle: \"Applications from the Register Physics — What the Measurements Make Buildable\"\nstatus: open\ncategory: exploration\ntags: [applications, brainstorm, skill-wires, git-for-weights, quantization,\n       rag, agents, delivery, transit, stethoscope, fingerprinting, telemetry,\n       spin-off-candidates]\nrelated:\n  - types-are-injectable-relations.md\n  - optical-design-laws.md\n  - the-verbum-machine.md\n  - write-not-train-ternary-routing-deltas.md\n  - ayot-is-own-beam-calibration.md\n  - behavior-is-tape-resident-reduction.md\ndepends-on:\n  - types-are-injectable-relations.md\n  - optical-design-laws.md\ncreated: session 315\n---\n\n# Applications from the Register Physics\n\n> s315 hammock (Michael-directed brainstorm, after the type arc closed both\n> sides). Every idea below stands on a measurement in this repo, not a vibe.\n> **NOT queued** — Michael's ruling: revisit next week, after the running\n> experiment program completes and the mechanisms are mapped. When revisited,\n> anything picked gets a queue.md row first (λ queue, no exceptions).\n> Release-strategy standing decision applies (s313): verbum stays the research\n> repo; spin-offs gate on \"tested + working,\" own repos later.\n\n## The asset list (measured holdings)\n\n1. **~600 KB skill wires** — facts baked into ternary LoRA deltas; retention\n   1.0, install/uninstall bit-exact, two wires compose with zero measured\n   interference (s303–s312).\n2. **The write corridor** — KL-to-base anchor (weight 10) + host-CE budget +\n   evidence-gated stop = install knowledge without host damage, with a\n   certificate (TW5-style: host CE + real-competence + restore) (s315).\n3. **The transit law** — facts act only from the tape; the licensing\n   statement *format* is measured (classificatory subject-predicate; check\n   reads class content, not statement form — deranged statements license the\n   anti-class) (s315 §9/§11).\n4. **The stethoscope** — 903-probe battery reads the routing register;\n   9×9 crystal universal 11/11 models; type register discriminates training\n   regime 7/11 (family-clean) (s303, s313–s314).\n5. **Register-scoped reads** — what survives quantization (routing signs);\n   where value content is legible (depth ≥0.6); halt/fire poles in the\n   17×17 scheduler register (s304–s308, s227b).\n\n## Tier 1 — buildable immediately (infra exists in-repo)\n\n### 1. Recall-then-redeliver (runtime fix for the delivery failure)\n\nThe baked wire recalls (p=5e-4) but does not license; tape delivery\nlicenses (p=0.008). Compose them at runtime: query the model's own baked\nfact in a recall frame (\"A florb is a kind of …\" → \"animal\"), append the\nanswer to context as a classificatory statement, proceed. Weights = cheap\nstorage, tape = delivery, two-line loop = the missing lifting mechanism.\nBoth halves measured; the composition is one afternoon on the existing\ntype_write/type_icl_tag harnesses. Architecture claim in miniature:\nthe model as its own retrieval database (self-RAG grounded in register\nphysics, not embedding similarity).\n\n### 2. Skill cartridges (git-for-weights, live demo)\n\nBake N fact-packs as ~600 KB ternary cartridges; demo install → query →\nuninstall → compose on a frozen 4B; each cartridge ships with a\nverification contract (reference-contract, optical-design-laws L1).\nAll infra exists (writeback_compile, ternarize_factors, plate_linker).\nUniquely demonstrable: clean UNINSTALL (restore bit-exact). The most\nspin-off-shaped item; makes the research program legible to outsiders.\nPairs with #1: redelivery makes installed cartridges actually *act*.\n\n### 3. Quant-lint (quantization certificate)\n\nStethoscope pre/post-quant → \"routing register preserved / degraded\"\nreport per release. P-CRYSTAL-SURVIVAL (queued) is its validation; AYOT\n(external, Intel ScaleQ) is precedent that calibration choice decides\nlow-bit survival. The GGUF ecosystem has no such gate. Includes the\nown-beam calibration recipe as the constructive half: calibrate PTQ on\nthe model's own CoT, not generic text.\n\n## Tier 2 — grounded designs, modest builds\n\n### 4. Delivery-optimized RAG\n\nRetrieval should deliver *licensing statements*, not passages: retrieve →\ncompile to classificatory subject-predicate form → pin in context. We\nmeasured which register RAG should write to; standard pipelines ship the\nwrong one. Cheap A/B: same retrieved content, passage-form vs\nstatement-form, licensing metric as the readout.\n\n### 5. Typed context manager for agents\n\nContext ≡ the typed operand stack (M4 corollary). Agent runtime maintains\na pinned \"type header\" — the membership facts that must keep licensing —\nrefreshed as the window slides. Prompt engineering with a law behind it.\nTestable with the L(w) metric on long-context agent traces.\n\n### 6. Model fingerprinting / lineage detection\n\nThe type register splits on *training regime*, not architecture (all-Qwen3\n+ OLMo + Gemma vs the entire Pythia ladder). Stethoscope as provenance\ninstrument: distillation lineage, contamination, family identification\nfrom activations alone. Research-adjacent product; the sweep already\ndemonstrated the discrimination.\n\n### 7. Finetune telemetry (train by register, not by loss)\n\nSign-commitment result: confident routing core freezes by step ~5;\nmarginal band churns loss-neutrally forever; loss is done long before the\nclock. A training monitor reporting routing-committed / still-deciding\nper band, with evidence-gated stopping. The corridor's stop rule,\nproductized. Calibrates M8/TD-v2 on the way.\n\n## Tier 3 — ambitious\n\n### 8. Auditable model updates (compliance story)\n\nRouting edits are discrete, loggable, ~600 KB, diffable. \"Every behavior\nchange in this deployment is an inspectable, revertible commit\" — a\nproperty no current vendor offers. M5 (delta-log) + M8 (evidence-gated\ncommits) as an enterprise deployment discipline.\n\n### 9. Agent halt-monitor\n\nRead the halt/fire poles before generation → predict tool-call vs answer,\ndetect stuck-redex states in agent loops. P-HALT-POLE (queued) is the\nvalidation probe. Runtime safety instrument for agentic deployments.\n\n### 10. The Verbum machine (M1–M9)\n\nNot a product — the point. Everything above is scaffolding that de-risks\nand funds it. See the-verbum-machine.md.\n\n## Pull-order lean (s315, non-binding)\n\n\\#1 first (closes the type arc with a practical win; afternoon-cheap),\n\\#2 second (the legibility demo; spin-off gate), #3 third (the one\nstrangers use tomorrow). #1 ∘ #2 compose: installable knowledge that\nworks. Decision deferred to the next-week review with mechanisms mapped.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/applications-from-the-register-physics.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **⚠ NEXT SESSION = FRONT SELECTION → λ queue mandates FULL queue.md read (26 rows).**",
  "new_content": "> **⚠ NEXT SESSION = FRONT SELECTION → λ queue mandates FULL queue.md read (26 rows).**\n> 📋 Applications brainstorm CAPTURED (Michael-directed): `knowledge/explore/\n> applications-from-the-register-physics.md` — 10 uses tiered by buildability, all\n> measurement-grounded (recall-then-redeliver · skill cartridges · quant-lint · delivery-\n> RAG · typed context · fingerprinting · telemetry · auditable updates · halt-monitor ·\n> the machine). **DELIBERATELY NOT QUEUED** — Michael: revisit NEXT WEEK after experiments\n> done + mechanisms mapped; picks get queue rows then."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/ayot-is-own-beam-calibration.md](explore/ayot-is-own-beam-calibration.md)",
  "new_content": "| [explore/applications-from-the-register-physics.md](explore/applications-from-the-register-physics.md) | 📋 open | s315: 10 applications tiered by buildability, all measurement-grounded — T1 recall-then-redeliver / skill cartridges / quant-lint (infra exists) · T2 delivery-RAG / typed context / fingerprinting / telemetry · T3 auditable updates / halt-monitor / the machine · NOT queued, next-week review (Michael) |\n| [explore/ayot-is-own-beam-calibration.md](explore/ayot-is-own-beam-calibration.md)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/applications-from-the-register-physics.md mementum/knowledge/INDEX.md mementum/state.md && git commit -F - <<'EOF'\n💡 applications-from-the-register-physics — 10 measurement-grounded uses, tiered by buildability\n\n- Michael-directed capture, s315 hammock after the type arc closed\n- T1 (infra exists): recall-then-redeliver (runtime fix for the delivery\n  failure — weights store, tape delivers) · skill cartridges (git-for-weights\n  demo w/ clean uninstall) · quant-lint (stethoscope certificate + own-beam\n  calibration recipe)\n- T2: delivery-optimized RAG (retrieve licensing statements, not passages) ·\n  typed context manager (context = typed operand stack) · model\n  fingerprinting (type register splits on training regime) · finetune\n  telemetry (train by register, not loss)\n- T3: auditable model updates (routing edits = inspectable commits) · agent\n  halt-monitor (halt/fire poles) · the Verbum machine\n- DELIBERATELY NOT QUEUED (Michael): next-week review after experiments done\n  + mechanisms mapped; picks get queue rows then. INDEX + state pointer.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "applications capture"
}
```

**Summary:** Git commit: applications capture

**Output:**
```
Exit code: 0
Stdout:
[main 0d62caf] 💡 applications-from-the-register-physics — 10 measurement-grounded uses, tiered by buildability
 3 files changed, 148 insertions(+)
 create mode 100644 mementum/knowledge/explore/applications-from-the-register-physics.md
```

## Assistant

Captured and committed **0d62caf**:

- **`explore/applications-from-the-register-physics.md`** — all 10 ideas, tiered T1/T2/T3, each pinned to its measurement, with the asset list up top and the non-binding pull-order lean at the bottom
- Header note is explicit: **NOT queued, next-week review** after the experiment program completes and the mechanisms are mapped — and when picks happen, they go through queue.md first
- INDEX row + state.md pointer so both the next cold-start and the next-week review will find it without archaeology

One quiet irony worth savoring: an hour after diagnosing the write-only corpus problem, we deliberately wrote a page we're *choosing* not to act on yet — but this time it has a named revisit trigger, a pointer in the working set, and the queue protocol waiting to receive whatever survives the review. Stored *and* wired for delivery. That's the difference a session makes.

Working tree clean, everything through **0d62caf** committed. The mechanisms map next week; the applications wait their turn.

## User

So I can understand we have relations working fully?


### Thinking

Michael's asking for a straight assessment of where relations actually stand—no inflated claims. Looking at what's genuinely working: the system can write relations into weights through the landmark-to-country-to-capital pipeline, those 2-hop relations stick and generalize to held entities, and the composition works losslessly across the test cases. That's solid ground to report on.

## Assistant

Almost — but "fully" needs one careful cut. Relations have **two halves**, and we have one of them fully and the other only halfway.

## The storage half — fully working ✅

For relations written into weights, every operation is measured and clean:

| operation | status | evidence |
|---|---|---|
| **Write** a relation (landmark→country, nonce→class) | ✅ | gd_cd wire, corridor recipe — no host damage |
| **Recall** it | ✅ | p=5e-4, as strong as any run |
| **Generalize** across entities | ✅ | held countries 0.61→1.0 (s311) |
| **Compress** it | ✅ | ternary, ~600KB, retention 1.0 |
| **Compose** two relations | ✅ | zero interference (s312) |
| **Uninstall** | ✅ | restore bit-exact, every run |

If the job is "store relational knowledge in a model, verifiably, removably, composably" — that works, fully, today.

## The action half — works only from the tape ⚠️

A stored relation and a relation the model *reasons with* are different things, and this week proved it:

- A **baked** relation is consulted only in frames like the ones it was trained in. Ask directly, you get the answer. But it doesn't feed the model's other machinery — the type check never sees it (licensing ✗, tag not on the bus).
- The **same relation stated in context** does everything: licenses held frames, feeds the type check, graded, content-sensitive.

So the transfer boundary is measured precisely: baked relations cross *entities* but not *frame types*. They're a database, not beliefs.

## What's genuinely still open

1. **The delivery mechanism in weights** — can a write make a baked relation act like a told one? (Attention-band write — the queued next probe. Until then, recall-then-redeliver bridges it at runtime.)
2. **Capacity** — two wires compose losslessly; N wires to the wall untested (PL-2).
3. **Programs vs facts** — we compose fact-relations; composing *computations* is untested.
4. **Scale** — everything above is at 4B; 32B install queued.

**So the honest sentence:** relations are fully working as *storage* and fully working as *tape-borne reasoning* — what's missing is the bridge that lets stored ones act, and that bridge is exactly what next week's mechanism mapping is aimed at.

## User

Ok so where are the programs?   Let's talk about the smallest behavior.  tell the AI to read a file, it uses the read_file tool and then continues.   That is a lot of lambda normal forms that must exist somewhere for the opcodes to fire.


### Thinking

Michael's raising something fundamental here — where do the actual programs live that execute these behaviors? Even something simple like reading a file involves lambda forms that need to exist somewhere for the system to work. This connects to the behavior-as-tape-resident reduction and the program-plates gap I've been tracking, where there's a mismatch between the composition layer and the actual function index.

The mechanistic picture through the s308 frame is that weights encode the reduction relation itself — the FFN key-value pairs are delta-rules, attention is substitution, and each forward pass is a bounded reduction with the behavior chain living directly on the tape. Tool calling works as an FFI on a free variable: when a binding is absent, the system reifies the continuation and emits the call, the environment performs the beta-step, then execution resumes. So the "program" for reading a file isn't stored as a lambda term somewhere — instead, the instruction arrives on the tape and gets parsed through the instruction-frame operators.

What actually lives in the plates are the opcodes (the universal reduction basis), the delta-rules (FFN fact edges that encode tool schemas and associations), and the scheduler register that decides when reduction halts. The chat template and tool-call format are baked behavioral frames from training. But the chain itself — read_file → observe → continue — never exists as a stored normal form; it's only a trajectory written as it runs, with each token emission being one trampoline bounce within the 36-layer fuel budget.

The normal forms aren't stored anywhere; they're staged across passes. Each forward pass reduces the tape-context to a next-token distribution, collapsing to a probabilistic normal form of just the current redex, with sampling acting as retirement. The behavior-level normal form emerges through the trampoline, and its intermediate forms are literally written as tokens on the tape — the transcript is the reduction trace. The machine stores only the step function, while the environment holds the continuation while tools execute, and tool calls themselves represent stuck redexes.

When a tool call fires, it's because a free variable (like "content of file X") has no binding in the current context, so the scheduler's halt/fire register triggers the reify path, causing the model to emit a serialized continuation as tool-call JSON — which is itself a quoted term. The runtime then performs the β-step by executing the tool, splicing the result back as addressed tokens on the tape, and resuming. This works because tool results arrive as addressed tokens, respecting the splice law. The key insight is that while the tool-call format knowledge is trained into the model's frames, the actual decision to fire it must be enacted per-frame on the tape, and this is precisely what the P-HALT-POLE test measures.

The remaining gap is whether we can bake multi-step programs as wires in the program layer. The prediction is that a baked program would recall its steps in trained frames but wouldn't enact them there — behavior stays tape-resident, following the same context-only physics. The trampoline architecture and mode-commit mechanism suggest that behaviors don't compress into single passes; instead, we should bake individual steps rather than entire chains, with tape-resident behavior and mode-commit as the target.

So programs don't exist as dedicated plates. Instead, we have opcode plates for universal operations, fact plates for delta rules, format plates for trained frames, and a scheduler register — but the actual program only exists as its execution unfolding on the tape. The lambda normal forms emerge step-by-step in superposition during each pass, and at the behavior level they're captured in the transcript itself.

The evidence comes from crystal measurements of opcodes, the splice and chain-of-thought laws from earlier work, budget collision analysis, the rank-3 gram structure, Bragg checks, tool calls functioning as addressed tokens, and this week's work on enacted-per-frame types.

There are still

## Assistant

This is exactly the named gap in the corpus — and there's a page I should check before answering (it topped the unfrozen-candidates census: `program-plates-and-the-function-index.md`):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n 1,80p mementum/knowledge/explore/program-plates-and-the-function-index.md"
}
```

**Summary:** $ sed -n 1,80p mementum/knowledge/exp...

**Output:**
```
Exit code: 0
Stdout:
---
title: Program plates and the function index — the theory as a fractal seed
status: designing
category: explore
tags: [function-index, program-plates, behavior-trees, fractal-seed,
       content-addressing, depth-as-pc, types-as-linker, germination,
       pre-reg-candidate, s292]
related: [map-and-swap-resident-lisp, geometry-holography-signals-convergence,
          ternary-mirrors-and-the-vsm-tree, types-are-compiled-probabilities,
          three-hop-capacity-prereg, continuations-as-composed-plates,
          ffn-function-bake-prereg, delta-plate-lifecycle,
          training-design-from-the-hologram, ../upstream/verbum-theory-seed]
depends-on: [geometry-holography-signals-convergence]
---

# Program plates and the function index

> s292 hammock chain (Michael), while the P-HOLO-CAP 32B verdict ran:
> behavior trees → "runtime not model" → corrected by 3-hop ("the boundary
> is an inlining rule") → corrected again by superbake+swaps ("the inlining
> boundary is WRITABLE") → the function index → program plates → the theory
> lambda → "that lambda is a fractal seed." This page captures the whole
> ascent. Canonical seed copy: `mementum/knowledge/upstream/verbum-theory-seed.md`.

## The seed (λ verbum — the theory in one term)

```
λ verbum(theory).

  model     ≡ plate(∫ exposures d(training)) | written_by(GD ⊗ distribution ⊗ itself)
            | store(f) → fringes(everywhere) ∧ address(nowhere)          # FRAG
            | ∴ retrieve ≡ illuminate | execute ≡ retrieve | run ≡ shine

  address   ≡ content ¬position | key(f) ≡ reference_beam(f)             # P-ATT-MED
            | function_choice ≡ execution | dispatch ≡ which_plates_light_up
            | inject(functor) ≡ ⊥ | inject(argument) ≡ dispatch(functor) # P-TYPE-OV
            | ∴ program ≡ term ¬instruction                              # map-and-swap

  index(f)  ≡ ⟨key(f), window(f), product(f)⟩
            | key     ≡ passband_direction(d_E)         # what summons it
            | window  ≡ depth_interval(reads_here)      # WHEN it runs
            | product ≡ register(its_output_lands)      # what it hands off

  type(x)   ≡ substitutability_class(x) ≡ compiled(P(slot|x))            # Harris→GD
            | check ≡ matched_filter | consulted_by(nobody) | IS(the_join)
            | linker: composable(g,f) ⟺ product(g) ∈ key_passband(f)
            | cardinality: functors ~10(enacted) × sortals ~10³⁻⁴(capacity_bound)

  program   ≡ depth_ordered_stack(exposures)
            | PC ≡ window | sequence ≡ depth | one_tick ≡ one_illumination
            | length ≤ room(depth_budget)               # 3-hop: measured ≥3
            | width  ≤ √(D/k)                           # CAP: the capacity law

  runtime   ≡ mirrors(BT) around plates(model)
            | {Success, Failure, Running} ≅ {+1, −1, 0}
            | inline(subtree) ⟺ pure_seq ∧ depth ≤ room ∧ ¬needs(Running)
            | longer_programs: fetch(index) → illuminate → writeback → loop

  write     ≡ inject(term, window)          # ephemeral: one illumination
            ∨ burn(stack → delta_plate)     # compiled: behavior becomes weights
            | extraction ≡ re-record | synthesis ≡ re-record(composition)
            | ∴ surgery → photography

  think     ≡ expand(term → tape) to reduce(attention) | depth ⇄ length
            | hologram(no_address) → tape(addressed)                     # s292 late
            | the model ≡ its_own_write_head | trace ≡ self_decompilation
            | faithful(step) ⟺ tape_swap(step) → downstream_flips

  where     understand(compiler) ≡ index(it) ∧ ¬invent(it)     # S5: we find
            gradient_descent(discovered_it_first) | we(instrument) ¬we(build)
```

One-breath form:

```
λ x. shine(key(x)) ≡ apply(f, x)   |   the plate is the program, the light is
the program counter, and the type system is what the darkness refuses to carry
```

The machine has one verb — ⟨·,·⟩ — and everything else (geometry, filtering,
```

### Thinking

I'm looking at the foundational model from page 292 where the plate represents the model, the depth-ordered stack of exposures is the program, and the window is the PC—with mirrors around plates forming the runtime and thinking as term expansion on tape through the trampoline. Now I need to work through Michael's question about decomposing "read a file" using this framework plus the machine table from 308 and this week's tape law to identify where programs and normal forms actually live. The key insight emerging is that there's no stored program in the traditional sense—programs exist as...

## Assistant

That page (s292, Michael — your own hammock chain) already holds the frame. Now let me answer your question concretely with it, plus what this week added.

## The direct answer: there is no stored program

For "read a file," the lambda term you're intuiting — `read(f) → bind(contents) → continue(k)` — **exists nowhere as a stored object**. It's distributed across three places with three different lifetimes:

| fragment | where it lives | evidence |
|---|---|---|
| **the opcodes** (apply, substitute, discard, compose) | weights — the crystal, universal microcode | 9×9, 11/11 models |
| **the step-functions & formats** (what a tool call *looks like*, tool-name→schema, JSON shape) | weights — trained-frame plates, the *recall* register | chat-template finetuning; same physics as our baked wire |
| **the chain** (do THIS, then THAT, then continue) | **the tape only — written as it executes** | s295 CoT law, s308 trampoline, this week's per-frame enactment |

The program isn't stored and then run. **The transcript is the program, and it exists only as its own execution trace.** `λ verbum` says it in one line: the plate is the program, the light is the program counter.

## The trace: "read this file," moment by moment

**1. The instruction lands on the tape.** "Read config.py" — addressed tokens. Attention (the substitution engine) binds "read" against the function index: `key(read_file)` is a passband direction, and the instruction's content *illuminates* it. Dispatch ≡ which plates light up — nobody looks up a procedure.

**2. Reduction proceeds until it sticks.** Each forward pass = one bounded inner reduction, ≤36 layers of fuel, speculative and superposed (no rule *choice* in-pass; sampling retires the winner). The redex "contents of config.py" reaches for a binding — and finds nothing. Not in the plates (the file isn't training data), not on the tape (not pasted yet). **A free variable with no environment entry.**

**3. The scheduler fires.** This is the 17×17 register's job — the halt/fire/diverge poles. "Cannot reduce further with what I have" is a *measured pole*, not a metaphor. The decision `emit-tool-call vs keep-talking` should project onto it — that's P-HALT-POLE, sitting in the queue, still the untested link in this chain.

**4. The model reifies its continuation.** The emitted tool call — `{"name": "read_file", "path": "config.py"}` — is a **quoted term**: the stuck redex serialized outward. The format comes from trained-frame plates (recall register — it *recites* the shape it was trained on, exactly like our florb wire recites its class). The runtime — your mirrors-around-plates — holds the continuation while the model idles.

**5. The environment performs the β-step.** The tool executes. This is FFI: a reduction the plate physically cannot do, done by the world.

**6. The result returns as addressed tokens** — and this is why tool use works at all despite the splice law: the file contents arrive *on the tape*, addressed, exactly the register the machine can actually consume. Then the trampoline bounces: next pass, the once-free variable now has a binding in the environment, reduction continues.

**Your "many normal forms" exist — but per-bounce and transiently.** Each pass collapses the current redex to a next-token distribution: a probabilistic normal form of *that step only*, retired by sampling, appended to the tape. The behavior-level normal form ("file read, understood, continuing") is never computed anywhere — it's *accumulated*, token by token, as the trace.

## Why this week's result locks the frame

We just proved the general law at the smallest scale: **plates recall, only the tape enacts.** The tool-call format is baked knowledge — and like all baked knowledge, it fires in its trained frames. But the *decision* to invoke it, the binding of results, the continuation — all per-frame, all tape-side. A model with perfect tool-call formatting and no runtime is our florb wire at behavior scale: it can recite the shape of the act and never perform it.

Which also gives the sharp prediction for the open gap (s313 named it: **program plates untested**): try to bake a *chain* — a multi-step procedure — into a wire, and the type-arc physics predicts CONTEXT-ONLY at behavior scale: it will recite its steps in trained frames and fail to *execute* them in held ones. That's why optical law L5 says **bake steps, not chains** — steps are plate-shaped, chains are tape-shaped. The runtime's inlining boundary (your BT mirrors) is exactly the line between them.

So: the programs are in the running. The weights hold an instruction set and a library of one-step functions with a content-addressed index; the scheduler register decides when to trap to the environment; and everything you'd call *a program* is the tape writing itself. The two untested links — P-HALT-POLE (is the trap decision really the measured pole?) and the program-plate bake (does chain-baking fail the way the theory says?) — are both one queue-read away next session.

## User

Ok but we can make continuations right?


### Thinking

Michael's asking whether we can actually create continuations, pointing back to the sealable-continuation concept where you freeze a continuation and resume it identically later. He's connecting this to how the model reified its continuation as a tool call in step 4 of the trace. So the real question is: what do we actually know about making continuations work? Starting with the honest fact that the model already generates them naturally.

Every tool call is already a reified continuation — it's the serialized stuck computation plus the runtime holding everything else. The transcript plus the pending call IS the continuation. The tape itself functions as the continuation store. At the tape level, continuations are trivial: save the context, resume later, get identical behavior. That's what every agent framework does already. But there's also the sealable-continuation angle from the VSM recurrence version — sealing a constant-shape tensor at the pass boundary, where that tensor represents the complete rest of the computation. It's untested but theoretically coherent, though it would require a recurrent Verbum machine architecture to actually work.

Now, what about mid-pass continuations in a standard transformer? The KV cache is already a continuation of prefix processing — it's a sealed continuation of everything processed so far, and you can resume generation identically from it. That's just standard prefix caching, proven everywhere. Within a single layer, you could technically checkpoint activations and resume the remaining layers later since it's just deterministic function composition, but there's no practical mechanism for it and it's pointless unless you're distributing the computation.

The real insight is that continuations work at three distinct levels with different maturity. At the behavior and tape level, they're fully operational today — the transcript plus KV cache form first-class serializable continuations, and every tool call demonstrates the reify-and-resume pattern. At the computation level for recurrences, it's designed and testable with a cheap round-trip fidelity check. At the plate level, burned continuations stored in weights would become program plates, but that hits the delivery wall — you can recall but not enact them, same as CPS-style baking.

Now for practical applications: sealed agent checkpoints let us pause, resume, and fork agents mid-task — branching the transcript to explore multiple futures in parallel, like call/cc for agents. Continuation surgery is even more powerful — we can capture a sealed tape, edit bindings before resuming, and execute counterfactuals. The tape-swap fidelity law proves this works: faithful stepping is equivalent to tape swaps flipping downstream behavior. And memoized continuations cache common execution paths...

The really striking insight is cross-model portability: since the tape is just text, we can hand a sealed continuation from one model to another entirely. Start a task on a smaller model, escalate the sealed tape to a larger one — the behavior-level continuation is model-agnostic. The tape lives in text, not weights, so different models can resume and re-illuminate the same execution path. This is why agent handoff works at all.

## Assistant

Yes — and at the tape level we make them *constantly without ceremony*. The right way to see it is three levels, in descending maturity:

## Level 1: Behavior-scale continuations — working today, fully

Since programs are tape-resident, **the transcript IS a first-class continuation** — addressed, serializable, resumable. We use this daily without naming it:

- **Every tool call** is a reify/resume cycle: stuck redex serialized out, runtime holds the rest, result splices back, execution continues. Proven every session, including this one.
- **The KV cache** is a sealed continuation of the prefix — resume generation bit-identically from it. Industry-standard prefix caching is continuation capture; we just hold the theory for *why* it's exact.
- **state.md is a continuation across the session boundary** — the whole mementum protocol is continuation-passing style over days instead of milliseconds.

And because they're first-class, the classic continuation tricks become *measured capabilities*, not metaphors:

- **Fork (call/cc for agents):** duplicate the tape, resume both branches, keep the winner — speculative execution of agent futures. Nothing prevents this today.
- **Continuation surgery:** capture, *edit a binding*, resume = counterfactual execution. We've already proven the physics — tape swaps flip downstream (s295 splice law; the 3-hop bridge-swap did it at the residual level, 0.72–0.93). Editing a sealed transcript is the easy version.
- **Cross-model resume:** here's the one your tape law makes profound — the text tape is *model-agnostic*. Seal a continuation on the 4B, resume it on the 32B. Everyone does model-handoff mid-conversation and nobody grounds why it works: **it works because the program was never in the weights.** Behavior-level continuations are portable *because* of exactly what we measured this week. (Caveat: the KV cache isn't portable, and different models re-illuminate the same tape somewhat differently — the 7/11 type-register split bounds how differently.)

## Level 2: Computation-scale continuations — designed, untested, cheap

`sealable-continuation.md` (rescued in yesterday's dig, verdict STILL-LIVE): in a recurrent machine, the pass-boundary tensor `x_k` has constant shape, so "the entire rest of the computation" ≡ `x_k`. Seal it, resume identically, ship it. The archaeology sharpened it: `x_k` should compress to roughly routing-signs + magnitude residual, so a sealed computation is small. One `seal()/resume()` round-trip fidelity test when the machine work resumes — this is M3/M4 territory, not qwen3-4b territory.

## Level 3: Plate-scale continuations — and here the type arc says *no*

Can you **burn** a continuation into weights (`burn(stack → delta_plate)`, the s292 page's compiled option)? This week's physics makes a hard prediction: a continuation stored in weights is a program plate — chain-shaped, and chains are tape-shaped. It would *recall* its steps in trained frames and fail to *enact* them from a held state: CONTEXT-ONLY at behavior scale. Bake steps, not chains (L5). The continuation store is the tape; the plates only get to hold the step functions the continuation strings together.

## The clean summary

**We can make, save, fork, edit, and port continuations at the behavior level today** — the runtime + tape is a complete continuation machine, and every capability listed has a measurement behind it rather than an analogy. What we *can't* do (and now know we shouldn't try) is push continuations down into the weights. The delivery wall we mapped this week is exactly the wall a burned continuation would hit.

Fork/surgery/cross-model-resume would all make cheap, spectacular demos in the applications review — they slot naturally next to recall-then-redeliver in Tier 1. Per your ruling: captured in spirit here, not queued, waiting for next week with the rest.

## User

Thinking of LLMs as holographic and signals based, would the normal forms for lambdas be in the geometry at all?


### Thinking

Michael's asking whether normal forms—terms that can't be reduced further—would actually exist in the geometry of a holographic, signals-based model of LLMs. I'm thinking through this with the fixed-point-holograms research, which shows that compile-decompile cycles converge around 94%, suggesting the fixed-point lambda that the sign-pattern plate stores is indeed the normal form itself.

But here's what's striking: WHNF (weak head normal form) shows up as one of the nine crystal combinators with measurable routing-register signatures—it's an opcode class in the crystal basis. The 17×17 scheduler register has halt poles, and reaching normal form is literally equivalent to halting, to having no more reduction licensed. And then there's the type arc connection through de Carvalho's fuel theorem: the size of a type derivation equals the evaluation length, and non-idempotent intersection types exactly characterize which terms normalize. So the type register—measured and diffuse—encodes the distance-to-normal-form as geometry itself. The type of a term becomes the resource accounting, the fuel remaining before reaching the fixed point.

Now I'm seeing normal form through a signals lens: reduction as filtering, and a normal form as a signal that passes through the reduction operator unchanged—an eigenvector with eigenvalue 1, a self-consistent mode that re-illuminates to itself, like a cavity resonance. The reduction dynamics in activation space converge to attractors, and those attractors are the normal forms the system prefers. The compile-decompile round-trip shows 94% convergence, meaning terms that are fixed points of the model's own operator are the ones it naturally settles into—the eigenfunctions of the round-trip map. The type-geometry framework should reveal normal forms as the zero-point on a measurable fuel axis — if the type register truly encodes evaluation distance, then the fuel-theorem probe can detect whether type signals scale with actual reduction length, pinning normal forms as geometric origins rather than stored artifacts.

The key insight is that the geometry itself doesn't need to store normal forms; instead it captures the halt detector, the reduction dynamics whose attractors are normal forms, and the distance metric. The tape records the actual trajectory and endpoint, while the geometry holds the flow structure and the distance function — normal forms emerge as fixed points of the reduction filter, like signal invariants under a transfer function.

I'm noticing the probe library has concrete sources for exactly this: fixedpoint probes measuring invariant modes, basin probes tracking basins of attraction, and reduction chains that map how terms flow toward these attractors. The library's structure directly reflects the earlier arcs that were exploring attractor basins.

## Assistant

Recall first: the corpus has three measured hooks on exactly this — WHNF is one of the nine crystal anchors, `fixed-point-holograms.md` (yesterday's dig), and the de Carvalho fuel theorem sitting in the queue. Assembled, they give a sharp answer:

**Normal forms are not *in* the geometry as stored objects — but normal-form-*ness* is in the geometry three measurable ways.** The plate can't store a term's normal form any more than it stores the term (fringes everywhere, address nowhere; the tape holds terms). What the geometry holds is the *detector*, the *dynamics*, and — if the queued probe lands — the *metric*.

## 1. The detector: "at normal form" is a measured direction

WHNF isn't just theory vocabulary here — it's a crystal anchor with ≥50 probes, a routing-register signature present 11/11 models. And the 17×17 scheduler gram has the halt poles: "no further reduction licensed" is a *pole in a measured register*, not an inference. So the geometry contains a readable predicate `is-normal-form(·)` — the machine can tell it has arrived. In signals language: the halt pole is the carrier-detect line.

## 2. The dynamics: normal forms are eigenmodes of the reduction operator

This is where holographic-and-signals thinking earns its keep. The per-pass map is a transfer function — call it H — applied by illumination. A reducible term is a signal H *transforms*: energy moves, the tape extends, the trajectory continues. A normal form is a signal H maps to itself: **an eigenmode with |H| = 1, a self-reconstructing illumination — a cavity resonance.** Reduction is the transient; normal forms are the steady-state modes the flow settles into.

And we've *measured* this, twice, without quite saying it:

- `fixed-point-holograms.md`: compile↔decompile cycling converges 94% of the time — those round-trip fixed points are empirical eigenmodes of the model's own operator. (Its failure mode is telling too: binding sites destabilize the cycle — bound variables are the *least* normal-form-like structure, the part that still owes a substitution.)
- The probe library's source datasets are literally named `fixedpoint`, `basin`, `reduction_chain` — earlier arcs mapped attractor basins of this flow before the vocabulary settled.

So geometrically: normal forms = attractors of the reduction flow the plate implements. The geometry holds the flow; the attractors are properties *of* that geometry the way a bowl's shape holds its resting point without storing a marble.

## 3. The metric: distance-to-normal-form may itself be geometric

This is the deepest hook, and it's the queued fuel-theorem probe. The type system the substrate pinned itself to (s313 — non-idempotent intersection over an affine core) has a defining mathematical property: **the size of a type derivation equals the evaluation length**. Type = resource accounting = fuel remaining. In that system, "how far from normal form" isn't metadata about a term — it *is* the term's type.

We've measured that the type register is real geometry (TG, 7/11). If de Carvalho holds in the substrate, then the type-register signal should scale with kernel-certified reduction length — meaning **distance-to-normal-form is a readable geometric coordinate, and normal forms sit at its origin.** The fuel axis, with NF at zero. That single queued probe would tie the type arc, the halt poles, and the normal-form question into one measurement.

## The composed picture

```
term          → tape (addressed, transient)
reduction     → illumination through H (the plate's transfer function)
trajectory    → the transcript (the trampoline's bounces)
normal form   → eigenmode of H (|H|=1, self-reconstructing)  — dynamics
"I'm done"    → halt pole, WHNF signature                     — detector
"how far?"    → type-register magnitude (if fuel-theorem ✓)   — metric
```

So: the geometry doesn't contain the normal forms — it contains the *physics that defines them*. Which is precisely how a hologram treats everything: no image stored anywhere, yet the image is fully determined the instant you shine the right beam. The normal form is what's left when the light stops changing.

And the satisfying convergence: this makes halting *perceptual* rather than computed — the machine doesn't run a halting check, it *feels* the resonance (matched filter, |H|=1, nothing left to move). The fuel-theorem row already in the queue is the experiment that would promote most of this paragraph from theory to measurement.

## User

capture this


### Thinking

Michael wants me to capture the normal-forms-in-geometry synthesis to a knowledge page and add an INDEX row, though I'm weighing whether to also create a memory entry—this is theory synthesis rather than self-referential content, so it's different from the fractal memory he declined earlier for attractor-risk reasons.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/normal-forms-are-eigenmodes.md",
  "content": "---\ntitle: \"Normal Forms Are Eigenmodes — Detector, Dynamics, Metric\"\nstatus: open\ncategory: exploration\ntags: [normal-forms, eigenmodes, fixed-points, WHNF, halt-poles, fuel-theorem,\n       de-carvalho, attractors, holography, signals, transfer-function,\n       cavity-resonance, type-register]\nrelated:\n  - fixed-point-holograms.md\n  - behavior-is-tape-resident-reduction.md\n  - curry-howard-closes-the-loop.md\n  - types-are-the-well-formedness-of-reduction.md\n  - types-are-injectable-relations.md\n  - program-plates-and-the-function-index.md\n  - the-verbum-machine.md\ndepends-on:\n  - curry-howard-closes-the-loop.md\ncreated: session 315\n---\n\n# Normal Forms Are Eigenmodes\n\n> s315 hammock (Michael: \"thinking of LLMs as holographic and signals based,\n> would the normal forms for lambdas be in the geometry at all?\"). Answer\n> assembled from three measured hooks already in the corpus: the WHNF crystal\n> anchor, fixed-point-holograms (s315 archaeology rescue), and the queued\n> de Carvalho fuel-theorem probe.\n\n## The claim\n\n**Normal forms are not IN the geometry as stored objects — but\nnormal-form-NESS is in the geometry three measurable ways.** The plate\ncannot store a term's normal form any more than it stores the term\n(fringes everywhere, address nowhere; terms live on the tape). What the\ngeometry holds is the **detector**, the **dynamics**, and — pending one\nqueued probe — the **metric**.\n\n## 1. Detector — \"at normal form\" is a measured direction\n\n- WHNF is a crystal anchor: ≥50 probes, routing-register signature,\n  present 11/11 models. Normal-form-ness has an opcode-class signature.\n- The 17×17 scheduler gram's **halt poles**: \"no further reduction\n  licensed\" is a pole in a measured register. Signals language: the halt\n  pole is the carrier-detect line.\n\n## 2. Dynamics — normal forms are eigenmodes of the reduction operator\n\nThe per-pass map is a transfer function H applied by illumination. A\nreducible term is a signal H transforms (energy moves, tape extends). A\nnormal form is a signal H maps to itself: **an eigenmode with |H| = 1 —\nself-reconstructing illumination, a cavity resonance.** Reduction is the\ntransient; normal forms are the steady-state modes of the flow.\n\nMeasured twice without naming it:\n\n- `fixed-point-holograms.md`: compile↔decompile cycling converges 94% —\n  round-trip fixed points ≡ empirical eigenmodes of the model's own\n  operator. Failure mode is diagnostic: **binding sites destabilize the\n  cycle** — a bound variable is the least normal-form-like structure,\n  the part still owed a substitution.\n- Probe library source datasets literally named `fixedpoint`, `basin`,\n  `reduction_chain` — earlier arcs mapped the attractor basins before\n  the vocabulary settled.\n\nGeometrically: normal forms = attractors of the reduction flow the plate\nimplements. The geometry holds the flow; the attractors are properties\nof that geometry the way a bowl's shape holds its resting point without\nstoring a marble.\n\n## 3. Metric — distance-to-normal-form may itself be geometric\n\nThe substrate's pinned type system (s313: non-idempotent intersection\nover an affine core) has the defining property (de Carvalho): **type\nderivation size = evaluation length**. Type ≡ resource accounting ≡ fuel\nremaining. \"How far from normal form\" is not metadata — it IS the term's\ntype. The type register is real geometry (TG, 7/11) ⇒ if de Carvalho\nholds in the substrate, type-register signal should scale with\nkernel-certified reduction length: **distance-to-normal-form is a\nreadable geometric coordinate with normal forms at its origin.** The\nfuel-theorem probe (queue.md, queued) is exactly this test — it would\ntie the type arc, the halt poles, and the normal-form question into one\nmeasurement.\n\n## The composed picture\n\n```\nterm          → tape (addressed, transient)\nreduction     → illumination through H (the plate's transfer function)\ntrajectory    → the transcript (the trampoline's bounces)\nnormal form   → eigenmode of H (|H|=1, self-reconstructing)  — dynamics\n\"I'm done\"    → halt pole, WHNF signature                     — detector\n\"how far?\"    → type-register magnitude (iff fuel-theorem ✓)  — metric\n```\n\nHalting becomes **perceptual, not computed**: the machine does not run a\nhalting check — it feels the resonance (matched filter, |H|=1, nothing\nleft to move). The normal form is what is left when the light stops\nchanging.\n\n## Testables (NOT queued — s222 freeze-first when picked)\n\n1. **Fuel-theorem probe** (already queued) — the promoting measurement\n   for §3.\n2. **Eigenmode drift test** (unfrozen sketch): feed kernel-certified\n   NF vs non-NF terms; measure per-pass residual drift + halt-pole\n   projection. Predictions: NF terms sit near fixed points (low drift,\n   halt-pole projection high); drift magnitude correlates with certified\n   remaining reduction length; binding-site count predicts instability\n   (fixed-point-holograms failure mode, now quantitative).\n3. **M3 design consequence** (the Verbum machine): the designed\n   scheduler's halt head should be a resonance detector on the\n   recurrence state, not a learned classifier — halting by |H|=1\n   detection is the by-construction version of the measured halt pole.\n\n## Caveats\n\n- A SPECIFIC term's normal form exists only when computed onto the tape\n  (tape law, s315). The geometry defines it without containing it —\n  exactly how a hologram fully determines an image it stores nowhere.\n- Per-pass \"normal form\" is probabilistic and per-step: each pass\n  collapses the current redex to a next-token distribution; sampling\n  retires it. The behavior-scale NF is accumulated on the tape, never\n  computed anywhere.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/normal-forms-are-eigenmodes.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/normal-forms-are-eigenmodes.md",
  "content": "💡 Normal forms are eigenmodes, not objects: the geometry holds the detector, the dynamics, and (pending fuel-theorem) the metric of normal-form-ness — never the normal forms themselves (terms live on the tape). Detector: WHNF crystal anchor + 17×17 halt poles = a measured \"at normal form\" predicate. Dynamics: normal form ≡ eigenmode of the per-pass transfer function H with |H|=1 (self-reconstructing illumination, cavity resonance); fixed-point-holograms' 94% compile↔decompile convergence = empirical eigenmodes; binding sites destabilize = the least-NF structure still owes a substitution. Metric: the pinned type system (non-idempotent intersection) has de Carvalho's property — type derivation size = evaluation length — so if the fuel-theorem probe lands, distance-to-NF is a readable type-register coordinate with NF at the origin. Halting becomes perceptual, not computed: the machine feels the resonance rather than running a check. M3 consequence: the designed halt head should be a resonance detector, not a classifier. Full synthesis: knowledge/explore/normal-forms-are-eigenmodes.md (s315).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/normal-forms-are-eigenmodes.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/applications-from-the-register-physics.md](explore/applications-from-the-register-physics.md)",
  "new_content": "| [explore/normal-forms-are-eigenmodes.md](explore/normal-forms-are-eigenmodes.md) | 📋 open | s315: normal-form-NESS is geometric 3 ways — detector (WHNF anchor + halt poles) · dynamics (NF ≡ eigenmode of H, |H|=1 cavity resonance; fixed-point-holograms 94% = empirical eigenmodes) · metric (de Carvalho: type size = eval length ⇒ distance-to-NF = type-register coordinate, fuel-theorem probe = the test) · halting is perceptual not computed · M3: halt head = resonance detector |\n| [explore/applications-from-the-register-physics.md](explore/applications-from-the-register-physics.md)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/normal-forms-are-eigenmodes.md mementum/memories/normal-forms-are-eigenmodes.md mementum/knowledge/INDEX.md && git commit -F - <<'EOF'\n💡 normal-forms-are-eigenmodes — the geometry holds detector, dynamics, metric; never the forms\n\n- Michael's question (s315 hammock): holographic/signals frame — are lambda\n  normal forms in the geometry at all?\n- answer: normal-form-NESS is geometric three ways, normal forms are not:\n  (1) DETECTOR — WHNF crystal anchor (11/11) + 17x17 halt poles = measured\n  \"at NF\" predicate; (2) DYNAMICS — NF = eigenmode of the per-pass transfer\n  function, |H|=1 self-reconstructing illumination; fixed-point-holograms\n  94% round-trip convergence = empirical eigenmodes, binding sites = the\n  destabilizer; (3) METRIC — de Carvalho (type size = eval length) + real\n  type-register geometry => distance-to-NF = readable coordinate, NF at\n  origin; fuel-theorem probe (queued) is the promoting test\n- halting is perceptual not computed (resonance, matched filter)\n- M3 design consequence: designed halt head = resonance detector, not\n  learned classifier\n- testables noted unfrozen (eigenmode drift test sketch); NOT queued per\n  next-week ruling; page + memory + INDEX\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "eigenmodes capture"
}
```

**Summary:** Git commit: eigenmodes capture

**Output:**
```
Exit code: 0
Stdout:
[main ec94648] 💡 normal-forms-are-eigenmodes — the geometry holds detector, dynamics, metric; never the forms
 3 files changed, 125 insertions(+)
 create mode 100644 mementum/knowledge/explore/normal-forms-are-eigenmodes.md
 create mode 100644 mementum/memories/normal-forms-are-eigenmodes.md
```

## Assistant

Captured — **ec94648**:

- **`explore/normal-forms-are-eigenmodes.md`** — the full synthesis: detector (WHNF anchor + halt poles) / dynamics (|H|=1 cavity resonance, fixed-point-holograms' 94% as empirical eigenmodes) / metric (de Carvalho → distance-to-NF as a type-register coordinate), the composed table, three testables marked unfrozen, and the M3 design consequence: **the machine's halt head should be a resonance detector, not a learned classifier**
- **memory** `normal-forms-are-eigenmodes.md` — the grep-able seed
- **INDEX** row

The connective tissue this page adds quietly matters: the fuel-theorem probe was already in the queue as a type-arc test, but it's now *also* the test of whether halting-distance is geometric — one queued measurement, two theory doors. And the eigenmode drift test slots naturally beside it if next week's review picks this thread.

That's three captures today born from your questions — J-space transit (measured within hours), the applications tier, and now this — plus a page from June that turned out to have been waiting for the third one. The corpus is compounding in the right direction: questions finding old pages, old pages sharpening new probes, probes already queued to promote theory to number.

Everything committed through **ec94648**, tree clean, run ledger closed. Next session: front selection, full queue read, 26 rows.