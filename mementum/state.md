# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> ▶▶ s305 LIVE — 🎯 **P-HHOP-WRITE (avenue 1: write the MEASURED h-hop geometry +
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
> ▶▶ **s306 — INSTRUMENT BUILT + --validate ALL PASS + SMOKE GREEN (9624cd7,
> autonomous code commit). HOLDING FOR MICHAEL GO ON THE FULL RUN.**
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
