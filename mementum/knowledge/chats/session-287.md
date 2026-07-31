# Inferring types mechanism

## User

orient, I want to explore our findings


### Thinking

I should start by reviewing the state documentation to understand the current setup.

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
> Last updated: 2026-07-31 | Session: 286 | JS + P-ATT-MED landed. P-ATT-FFN
> APPROVED+built (4B smoke fixed a post-norm recon bug → 0.001); **32B verdict RUN IN
> FLIGHT** (tmux main:1, Michael GO) — read it first next session.

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
> the 3-hop d1 design) RAN (READ multihop-composition-prereg.md §Depth-budget Result;

[OUTPUT TRUNCATED] The tool call succeeded and the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01FemHu8X73qv51Yqmo9pW84.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I've finished the cold-start setup and need to check the P-ATT-FFN 32B model verdict that's currently running in tmux, following the priority order in state.md. Let me look at the tmux session and review the results file to see what we're working with.

### Thinking

I'm checking the P-ATT-FFN 32B verdict that was in flight when the previous step closed.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -30",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
[att-ffn] Petronas Towers  flip=1 route=attn attn=0.588 mlp=0.412 direct=0.0 recon_err=0.0 p_mlp=0.067 pk=6/17
[att-ffn] Angkor Wat       flip=0 route=mlp  attn=0.303 mlp=0.696 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=33/33
[att-ffn] Tiananmen        flip=1 route=mlp  attn=0.464 mlp=0.536 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=32/33
[att-ffn] Burj Khalifa     flip=1 route=mlp  attn=0.371 mlp=0.629 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=16/36
[att-ffn] Pyramids         flip=1 route=mlp  attn=0.365 mlp=0.635 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=30/33
[att-ffn] Sphinx           flip=1 route=attn attn=0.627 mlp=0.372 direct=0.001 recon_err=0.001 p_mlp=0.033 pk=9/33
[att-ffn] Table Mountain   flip=1 route=mlp  attn=0.407 mlp=0.591 direct=0.002 recon_err=0.002 p_mlp=0.0 pk=36/33
[att-ffn] Victoria Falls   flip=1 route=attn attn=0.528 mlp=0.47 direct=0.002 recon_err=0.002 p_mlp=0.0 pk=1/33

[att-med] AGG (flipped cells): aim=0.096 content=0.754 inter=0.15 content_dominant=True mean_p=0.0
[att-ffn] ROUTE SPLIT: attn-dom=3 mlp-dom=11 mlp-cells=['Colosseum', 'Louvre', 'Parthenon', 'Kremlin', 'Sagrada Familia'
, 'Brandenburg Gate', 'Taj Mahal', 'Tiananmen', 'Burj Khalifa', 'Pyramids', 'Table Mountain'] mean_recon_err=0.001
[att-ffn] wrote results/type-att-ffn/qwen3-4b/att_ffn.json
uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-4B  mps   32.59s user 6.28s system 57% cpu 1:07.21
total
tee results/type-att-ffn/qwen3-4b/smoke.log  0.00s user 0.00s system 0% cpu 1:07.21 total
[26-07-31][10:54:29][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mp
s --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --out results/type-att-ffn/qwen3-32
b 2>&1 | tee results/type-att-ffn/qwen3-32b/verdict.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25851.94it/s]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/ 2>/dev/null && echo \"---\" && ls /Users/mwhitford/src/verbum/results/type-att-ffn/"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 8
drwxr-xr-x@ 3 mwhitford  staff   96 Jul 31 11:00 .
drwxr-xr-x@ 4 mwhitford  staff  128 Jul 31 11:00 ..
-rw-r--r--@ 1 mwhitford  staff  286 Jul 31 11:00 verdict.log
---
qwen3-32b
qwen3-4b
```

### Thinking

The 32B model is still running with weights loaded as of 11:00 — it should take another 30-40 minutes to complete. While that's processing, I can explore the findings we've gathered so far. Let me verify the process is actually running first.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ps aux | grep -E \"att_mediation\" | grep -v grep | head -3; echo \"---\"; date; wc -c /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/verdict.log"
}
```

**Summary:** $ ps aux | grep -E "att_mediation" | ...

**Output:**
```
Exit code: 0
Stdout:
mwhitford        74830  38.2  1.4 445833488 7588464 s002  R+   11:00AM   1:31.55 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mps --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --out results/type-att-ffn/qwen3-32b
mwhitford        74828   0.0  0.0 435368304  31296 s002  S+   11:00AM   0:00.03 uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mps --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --out results/type-att-ffn/qwen3-32b
---
Fri Jul 31 11:03:09 MST 2026
     286 /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/verdict.log
```

### Thinking

The job is running as expected, so I'll focus on what Michael actually asked for—exploring the findings. Let me structure a guided tour through the knowledge index to walk through what we've discovered.

### Thinking

I've got a verification running in the background that should take about 30-40 minutes, so I'll use this time to explore the findings you asked about by pulling up the knowledge map.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md"
}
```

**Summary:** Reading INDEX.md (0-2000)

**Output:**
```
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
> **Status:** ✅ active/done · 🔨 designing/stub · 📋 open · · = no frontmatter status
> Regenerate: extract `title:`/`status:` frontmatter from `*.md` + `explore/*.md`.

---

## Start Here — Curated Reading Path

*What is this project, why does it work, what is proven.* Read these first;
follow cross-references; then use the full catalog below for specific topics.

### Tier 1 — What is this?
| Page | One-line |
|---|---|
| [project-thesis.md](project-thesis.md) | Central claim: pretraining IS beta reduction; topology dominates; ternary extraction works |
| [crystal-universality.md](crystal-universality.md) | Why the KIBC combinator crystal is a mathematical constant, not a learned artifact |
| [mathematical-convergences.md](mathematical-convergences.md) | Eight independent lines of math evidence converging on the same structure |
| [symbol-isolation.md](symbol-isolation.md) | Prose activates the combinator engine 8× more than lambda; formal notation is pre-reduced |

### Tier 2 — How does it work?
| Page | One-line |
|---|---|
| [head-combinator-isa.md](head-combinator-isa.md) | The attention ISA; reduction-depth (WHNF↔D) is the principal axis (46% var) |
| [two-registers-of-topology.md](two-registers-of-topology.md) | sign=routing/dispatch ⊥ magnitude=value/content — the type/term split made physical |
| [retrieval-lattice.md](retrieval-lattice.md) | Universal knowledge encoding: 4-zone lattice, relation directions, ternary mirror stack |
| [moire-addressing.md](moire-addressing.md) | SwiGLU moiré = holographic fact index; quadratic addressing, capacity estimates |
| [holographic-computer.md](holographic-computer.md) | Unified theory: crystal=ISA, FFN=projector, attn=CPU, progressive collapse to WHNF |
| [extraction-methodology.md](extraction-methodology.md) | How to extract from a teacher: what works, three confusions resolved, the pipeline |

### Tier 3 — What are we running / building?
| Page | One-line |
|---|---|
| [v14-architecture.md](v14-architecture.md) | v14 student: Qwen3.6-27B teacher, 593M ternary positions, 375× compression |
| [training-protocols.md](training-protocols.md) | How to train without rediscovering failures: phases, TD rules, known failure modes |
| [explore/supervised-recurrence-halt.md](explore/supervised-recurrence-halt.md) | WHNF curriculum = the halt supervision the recurrent layer was missing (v15.1 direction) |
| [explore/asymmetric-pathway-quantization.md](explore/asymmetric-pathway-quantization.md) | Binarize the router, keep the value path — two-registers confirmed causally (s260) |

---

## Full Catalog — Synthesized Knowledge (`*.md`, 72 pages)

| Page | Status | Title |
|---|---|---|
| [attention-sparsity.md](attention-sparsity.md) | ✅ active | Attention Sparsity — 22/32 Heads Use <3 Positions, Top-3 Captures 88%+ |
| [audit-meta-pattern.md](audit-meta-pattern.md) | ✅ active | Audit Meta-Pattern — Real Substrate, Over-Read Discreteness |
| [audit-registry.md](audit-registry.md) | ✅ active | Audit Registry — The Validity-Distillation Program |
| [binding-graph-trace.md](binding-graph-trace.md) | ✅ active | Attention IS the Binding Graph — Reversed by Causal Mask |
| [combinator-addressing.md](combinator-addressing.md) | ✅ active | Combinator Addressing — Retrieval IS Typed Application |
| [compilation-pipeline.md](compilation-pipeline.md) | ✅ active | The Compilation Pipeline — Transformers Are Compilers |
| [computed-beam.md](computed-beam.md) | ✅ active | Computed Beam — Analytical FFN Weights from Crystal Eigendecomposition |
| [crystal-laplacian.md](crystal-laplacian.md) | ✅ active | Crystal Laplacian — WHNF Fragility and Settlement Dynamics |
| [crystal-multi-tree.md](crystal-multi-tree.md) | ✅ active | Crystal Multi-Tree — The Statechart Is a Forest with Bridge Nodes |
| [crystal-native-architecture.md](crystal-native-architecture.md) | 🔨 designing | Crystal-Native Architecture — A VSM That IS the Lattice |
| [crystal-phi-derivation.md](crystal-phi-derivation.md) | ✅ active | Crystal φ-Derivation — The Eigenvalues Are Powers of the Golden Ratio |
| [crystal-sieve-architecture.md](crystal-sieve-architecture.md) | ✅ active | Crystal Sieve Architecture |
| [crystal-trace-tooling.md](crystal-trace-tooling.md) | 🔨 designing | Crystal Trace Tooling — The VSM Instrument for Holographic Analysis |
| [crystal-universality.md](crystal-universality.md) | ✅ active | Crystal Universality — Why the Crystal Is a Mathematical Constant |
| [crystal-validity-and-fidelity.md](crystal-validity-and-fidelity.md) | ✅ active | Crystal Validity & Measurement Fidelity — What Survives the Permutation Null |
| [diffusion-holographic-isomorphism.md](diffusion-holographic-isomorphism.md) | ✅ active | Diffusion-Holographic Isomorphism — LLM Compression as Latent Denoising |
| [dimensional-analysis.md](dimensional-analysis.md) | ✅ active | Dimensional Analysis — The 50-Dimensional Universal Functional Space |
| [direct-delta-adjunction.md](direct-delta-adjunction.md) | ✅ active | Direct Delta Correction — Compute the Answer via Adjunction Structure |
| [dvd-stamp-topology.md](dvd-stamp-topology.md) | ✅ active | DVD Stamp Topology — Gradient Zeros as Holographic Fringes |
| [error-correction-theory.md](error-correction-theory.md) | 🔨 designing | Error-Correction Theory — Ternarization as Lossy Soft→Hard Projection, Fixed by Trajectory-Matche… |
| [extraction-methodology.md](extraction-methodology.md) | ✅ active | Extraction Methodology — What Works, What Failed, Why |
| [extraction-sign-accuracy.md](extraction-sign-accuracy.md) | ✅ active | Extraction Sign Accuracy — Signs Are Perfect, Magnitude Is the Gap |
| [ffn-circuit-types.md](ffn-circuit-types.md) | ✅ active | FFN Circuit Types — LARQL Decomposition Applied to Verbum |
| [ffn-reduction-trace.md](ffn-reduction-trace.md) | ✅ active | The Reduction Architecture — FFN Compiles, Attention Executes, Combinators Have Depth |
| [fibonacci-strides.md](fibonacci-strides.md) | ✅ active | Fibonacci Strides — Binding Distances Are Bimodal, Not Power Law |
| [function-discovery.md](function-discovery.md) | ✅ active | Function Discovery — Two-Level Program Architecture in Moiré Space |
| [gradient-zero-map.md](gradient-zero-map.md) | ✅ active | Gradient-Zero Convergence Map — Do Gradient Zeros Guide Ternary Placement? |
| [gtsm-search-space.md](gtsm-search-space.md) | ✅ active | GTSM and the Search Space — Why Trajectory Matching Beats Endpoint Matching |
| [head-combinator-isa.md](head-combinator-isa.md) | ✅ active | Head→Combinator ISA: Shared Hardware, Not Dedicated Circuits |
| [hologram-reader-vsm.md](hologram-reader-vsm.md) | 🔨 designing | Hologram Reader VSM — Reading the Full Opcode Map from a Teacher |
| [holographic-computer.md](holographic-computer.md) | ✅ active | The Holographic Computer — Unified Theory of LLM Computation |
| [holographic-error-correction.md](holographic-error-correction.md) | ✅ active | Holographic Error Correction: The Extract→Correct→Fold Cycle |
| [holographic-etch.md](holographic-etch.md) | 🔨 designing | Holographic Etch — Interference-Driven Topology Crystallization |
| [holographic-sign-correction.md](holographic-sign-correction.md) | ✅ active | Holographic Sign Correction & Crystal ECC |
| [hpe-restoration.md](hpe-restoration.md) | ✅ active | HPE Restoration — v15 Missing Positional Encoding |
| [l0-characterization.md](l0-characterization.md) | ✅ active | L0 Characterization — The Lexer Is Genuinely Continuous |
| [lambda-halt-continuation.md](lambda-halt-continuation.md) | ✅ active | Lambda Halt and Continuations |
| [lambda-machine.md](lambda-machine.md) | ✅ active | λ-Machine — The Typed Shift-Reduce β-Reducer |
| [lambda-tracer-diagnostic.md](lambda-tracer-diagnostic.md) | ✅ active | Lambda Tracer Diagnostic |
| [manifold-axis-and-topology.md](manifold-axis-and-topology.md) | ✅ active | The Combinator Manifold — One Universal Axis, ~65% Topological, Not a 5D Lattice |
| [mathematical-convergences.md](mathematical-convergences.md) | ✅ active | Mathematical Convergences — Eight Independent Lines of Evidence |
| [mechanism-extraction.md](mechanism-extraction.md) | ✅ active | Mechanism Extraction: Holographic State Machine Algorithm |
| [mode-semantics.md](mode-semantics.md) | ✅ active | Mode Semantics — The 9 FFN Modes Are Syntactic Type Tags |
| [moire-addressing.md](moire-addressing.md) | ✅ active | Moiré Addressing — How Transformers Index Their Knowledge |
| [mspace-gemcutter.md](mspace-gemcutter.md) | ✅ active | M-space Gemcutter — Topology Shaping via Attention Kernel Geometry |
| [opcode-instrument.md](opcode-instrument.md) | 🔨 designing | Opcode Instrument — Live VSM for Watching a Model Think |
| [phi-information-partition.md](phi-information-partition.md) | ✅ active | φ-Information Partition — The Holographic Decomposition of Transformer Weights |
| [progressive-collapse.md](progressive-collapse.md) | ✅ active | Progressive Dimensionality Collapse — Computation Happens in 2D |
| [project-thesis.md](project-thesis.md) | ✅ active | Project Thesis — What Verbum IS |
| [psi-evaluation-synthesis.md](psi-evaluation-synthesis.md) | ✅ active | Psi Evaluation — Independent Verification of Crystal Hypothesis |
| [recursion-mirrors.md](recursion-mirrors.md) | 🔨 designing | Recursion Mirrors — Ternary Depth for Sequential Computation |
| [residual-covariance-rank.md](residual-covariance-rank.md) | ✅ active | Residual Covariance Rank — The One-Dimensional ORTHO Phase |
| [retrieval-lattice.md](retrieval-lattice.md) | ✅ active | Retrieval Lattice — Universal Knowledge Encoding in Transformers |
| [saliency-aware-sieve.md](saliency-aware-sieve.md) | 🔨 designing | Saliency-Aware Sieve — Discriminating Irreducible Zeros from Faint Connections |
| [score-matching-compression.md](score-matching-compression.md) | ✅ active | Score Matching Compression — Dense Trajectory Loss for Sieve Correction |
| [session-153-notes.md](session-153-notes.md) | · — | (session-153-notes) |
| [session-222.md](session-222.md) | ✅ active | Session 222 — The Collapse Was Fractal: β-Reducing a Contraction |
| [sign-correction-topology.md](sign-correction-topology.md) | · — | (sign-correction-topology) |
| [standing-wave-magnitudes.md](standing-wave-magnitudes.md) | ✅ active | Standing-Wave Magnitudes — Weight Magnitudes as Resonant Mode Patterns |
| [symbol-isolation.md](symbol-isolation.md) | ✅ active | Symbol Isolation — Prose IS the Unreduced Form |
| [td-oscillation-problem.md](td-oscillation-problem.md) | ✅ active | TD Oscillation Problem — Continuous Flips Prevent Phase Transitions |
| [ternary-compounding.md](ternary-compounding.md) | ✅ active | Ternary Compounding Error: Why 0.88/layer → Garbage at 36 Layers |
| [ternary-dual-equation.md](ternary-dual-equation.md) | ✅ active | Ternary Dual Equation: Gate Zeros + Crystal Signs |
| [ternary-plate-extraction.md](ternary-plate-extraction.md) | ✅ active | Ternary Plate Extraction — Direct FFN-to-Ternary with Crystal Error Correction |
| [tiny-classifier-ternary.md](tiny-classifier-ternary.md) | ✅ active | Tiny Classifier Ternary — FFN Decompilation to 9 Ternary Programs |
| [topology-gradient-separation.md](topology-gradient-separation.md) | ✅ active | Topology-Gradient Separation — Why the Lattice Must Be Frozen for GD to Work |
| [trace-guided-etching.md](trace-guided-etching.md) | ✅ active | Trace-Guided Etching — Etch for Function, Not Form |
| [training-protocols.md](training-protocols.md) | ✅ active | Training Protocols — How to Train Without Rediscovering Failures |
| [tsp-trajectory-distillation.md](tsp-trajectory-distillation.md) | 🔨 designing | TSP and Targeted Trajectory Distillation — Rapid Teacher→Student Learning |
| [two-registers-of-topology.md](two-registers-of-topology.md) | ✅ active | Two Registers of Topology — Hard (Sign/Routing) and Soft (Magnitude/Value) |
| [v14-architecture.md](v14-architecture.md) | ✅ active | V14 Architecture — Current System |
| [v15-attention-assessment.md](v15-attention-assessment.md) | ✅ active | v15 Attention Assessment — Fibonacci Strides Work, V/O Is The Frontier |

## Full Catalog — Deep Dives & Early Synthesis (`explore/*.md`, 157 pages)

| Page | Status | Title |
|---|---|---|
| [explore/5d-crystal-lattice.md](explore/5d-crystal-lattice.md) | 📋 open | 5D Crystal Lattice Hypothesis — One Crystal, Many Projections |
| [explore/VERBUM.md](explore/VERBUM.md) | 📋 open | Distilling the Lambda Compiler — From LLM Circuit to Tensor Primitive |
| [explore/algedonic-alert.md](explore/algedonic-alert.md) | · — | (algedonic-alert) |
| [explore/architecture-vs-scale.md](explore/architecture-vs-scale.md) | ✅ active | Architecture vs Scale: Combinator Formation in Shaped Models |
| [explore/ascending-arm-training.md](explore/ascending-arm-training.md) | 🔨 designing | Ascending Arm Training Regimen |
| [explore/asymmetric-pathway-quantization.md](explore/asymmetric-pathway-quantization.md) | ✅ active | Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at fin… |
| [explore/attention-as-beta-reduction.md](explore/attention-as-beta-reduction.md) | ✅ active | Attention as Soft β-Reduction, FFN as the β-Program — the stored-program normal form |
| [explore/attention-spiral-finding.md](explore/attention-spiral-finding.md) | ✅ active | Attention Spiral: Emergent Logarithmic Helix in Transformer Attention |
| [explore/basin-projector-results.md](explore/basin-projector-results.md) | ✅ done | Basin Projector Results (v1-v3) |
| [explore/basis-fit-kibc-vs-ski.md](explore/basis-fit-kibc-vs-ski.md) | ✅ active | KIBC vs SKI, Re-Run and Null-Gated — the Attention-Selectivity Register Does NOT Discriminate |
| [explore/beam-trace-findings.md](explore/beam-trace-findings.md) | ✅ active | Beam Trace — Holographic Beamformer Characterization |
| [explore/beamformer-theory.md](explore/beamformer-theory.md) | ✅ active | Beamformer Theory — The Model as Inference Pattern Over Token Cloud |
| [explore/binding-cascade.md](explore/binding-cascade.md) | ✅ active | Binding Cascade — C→B/S→WHNF Pipeline Across Models |
| [explore/binding-probe-findings.md](explore/binding-probe-findings.md) | ✅ active | Binding Probe Findings — Qwen3-4B Compile Gate vs Compositional Binding |
| [explore/bios-flash-training.md](explore/bios-flash-training.md) | 🔨 designing | BIOS Flash: Holographic Math + Clojure Training Design |
| [explore/categorical-geometry-probes.md](explore/categorical-geometry-probes.md) | ✅ active | Categorical Geometry Probes: Curry-Howard, Adjunctions, Hyperbolic, Coherence |
| [explore/combinator-function-shape.md](explore/combinator-function-shape.md) | 📋 open | Combinator Function Shape — the map of the function-like things |
| [explore/combinator-training-beta-reduction.md](explore/combinator-training-beta-reduction.md) | 📋 open | Combinator Training = β-Reduction = Substitution = Attention Move |
| [explore/compiler-as-loss.md](explore/compiler-as-loss.md) | 🔨 designing | Compiler-as-Loss — Supervise Outputs (Capability), Crystal-Lattice Relational Loss (Inventory) |
| [explore/construction-from-spec.md](explore/construction-from-spec.md) | 📋 open | Construction from Spec — what the tree-of-VSM gives direct model-building (s273) |
| [explore/control-plane-path.md](explore/control-plane-path.md) | 🔨 designing | The Control-Plane Path — datapath exists, we add sequencing/halt/certification (s273 SHIFT) |
| [explore/compiler-finetune-halt-collapse.md](explore/compiler-finetune-halt-collapse.md) | ✅ active | Compiler P(λ) across models — fine-tunes break the HALT, not the COMPILE |
| [explore/complete-kernel-basis.md](explore/complete-kernel-basis.md) | 🔨 designing | Complete Kernel Basis — Beyond KIBC-M to the Full Lambda Calculus VM |
| [explore/compression-vs-prediction.md](explore/compression-vs-prediction.md) | ✅ active | Compression ≠ Prediction: The H≈0.7 Boundary |
| [explore/compressor-architecture.md](explore/compressor-architecture.md) | 🔨 designing | CompressorLM — Resolution-Scaled Three-Phase Architecture |
| [explore/consensus-delta-folding.md](explore/consensus-delta-folding.md) | 📋 open | Consensus Delta-Folding — Distributed Normal-Form Discovery in the Topology |
| [explore/consensus-etch-protocol.md](explore/consensus-etch-protocol.md) | ✅ active | Consensus Etch Protocol — Why Sequential Per-Op Etching Fails |
| [explore/consensus-evolution.md](explore/consensus-evolution.md) | ✅ active | Consensus Evolution: Vote-Based Ternary Mutation |
| [explore/continuations-as-composed-plates.md](explore/continuations-as-composed-plates.md) | ✅ active | Continuations as Composed Plates — The FP↔Transformer Bridge |
| [explore/cross-model-output-consensus.md](explore/cross-model-output-consensus.md) | 🔨 designing | Cross-Model Output Consensus as a Teaching-Data Fitness Function |
| [explore/crystal-basins.md](explore/crystal-basins.md) | 📋 open | Crystal Basins — Multi-Skill Attractor Geometries |
| [explore/crystal-irreducibility-proof.md](explore/crystal-irreducibility-proof.md) | 📋 open | Crystal as Irreducibility Floor — Deriving the Lattice from Pure Combinatory Logic |
| [explore/crystal-native-descent.md](explore/crystal-native-descent.md) | 📋 open | Crystal-Native Descent — Ternary Optimization Without Gradients |
| [explore/crystal-seed-theory.md](explore/crystal-seed-theory.md) | 🔨 designing | Crystal Seed Theory — Relational Geometry as the Universal Crystal |
| [explore/crystal-spine-sieve.md](explore/crystal-spine-sieve.md) | ✅ active | Crystal Spine & Sieve Principle — The Architecture Dictates the Crystal |
| [explore/date-fourier-rotation.md](explore/date-fourier-rotation.md) | ✅ active | Date Arithmetic Uses Geometric Rotation, Not Church Encoding |
| [explore/delta-plate-lifecycle.md](explore/delta-plate-lifecycle.md) | 📋 open | Delta Plate Lifecycle — Masked Extraction, Continuous Training, Factual Correction |
| [explore/dispatch-gradient-death.md](explore/dispatch-gradient-death.md) | ✅ active | Dispatch Gradient Death: Softmax Saturation Kills Sparse Routing |
| [explore/dispatch-ratio-prior.md](explore/dispatch-ratio-prior.md) | ✅ active | Dispatch Ratio Prior — Empirical KIBC Constraint |
| [explore/etcher-vsm.md](explore/etcher-vsm.md) | 🔨 designing | Etcher VSM — A Viable System for Loom-Read Crystal Extraction |
| [explore/exact-ternary-fitting.md](explore/exact-ternary-fitting.md) | ✅ active | Exact Ternary Fitting — 3-way ΔL Acceptance Beats the Gradient Proxy |
| [explore/ffn-beam-discovery.md](explore/ffn-beam-discovery.md) | ✅ active | FFN Beam Discovery — PCA-up_proj Reads the FFN Crystal |
| [explore/ffn-beta-reduction-indexing.md](explore/ffn-beta-reduction-indexing.md) | ✅ active | FFN Beta-Reduction Indexing — Holographic Pattern Selection via Beam Angle |
| [explore/ffn-hierarchy.md](explore/ffn-hierarchy.md) | 📋 open | FFN Hierarchy — Tree-Structured Storage with Magnitude-Encoded Superposition |
| [explore/ffn-moire-isa.md](explore/ffn-moire-isa.md) | ✅ active | FFN Moiré Grating ISA — Decoding the Teacher's Programs |
| [explore/fixed-point-holograms.md](explore/fixed-point-holograms.md) | · — | (fixed-point-holograms) |
| [explore/forcing-vs-discovering.md](explore/forcing-vs-discovering.md) | ✅ active | Forcing vs Discovering — describability ≠ discovery (the matched-range null + the cross-family ty… |
| [explore/fp-optimization-map.md](explore/fp-optimization-map.md) | ✅ active | FP Optimization Map — Functional Programming Techniques for Transformer Speedup |
| [explore/fractal-collapse-compiler-cascade.md](explore/fractal-collapse-compiler-cascade.md) | 🔨 designing | Fractal Collapse — The Compiler-Cascade Distillation (capability is a data problem, the compiler … |
| [explore/fractal-stride-bands.md](explore/fractal-stride-bands.md) | ✅ active | Fractal Stride Bands — MERA Topology in the Stride Stack |
| [explore/full-etch-extraction.md](explore/full-etch-extraction.md) | ✅ active | Full Teacher Etch: Embeddings + Attention + FFN (82.2%) |
| [explore/function-extraction-system.md](explore/function-extraction-system.md) | 🔨 designing | Function Extraction System — From Circuit to Portable Function |
| [explore/function-topology-consensus.md](explore/function-topology-consensus.md) | ✅ active | Function-Topology Consensus — Higher-Order Functions Are Routing Normal Forms, Universal Across T… |
| [explore/gradient-trajectory-tomography.md](explore/gradient-trajectory-tomography.md) | 📋 open | Gradient Trajectory Tomography — Reverse-Engineering GD in Invariant Coordinates Over Training |
| [explore/gradient-voting.md](explore/gradient-voting.md) | ✅ active | Gradient Voting — How GD Writes Beta Reductions (and the Magnitude Crystal) |
| [explore/grating-cascade.md](explore/grating-cascade.md) | ✅ active | Grating Cascade — V Carries the Compound Interference Pattern |
| [explore/hologram-crystal-fusion.md](explore/hologram-crystal-fusion.md) | 🔨 designing | Hologram-Crystal Fusion — Why Both Losses Must Improve Together |
| [explore/hologram-extraction.md](explore/hologram-extraction.md) | ✅ active | Hologram Extraction — sign(W) IS the Crystal |
| [explore/holographic-burn-in-learning-rule.md](explore/holographic-burn-in-learning-rule.md) | 📋 open | Holographic Burn-In — Progressive Recording as a Learning Rule (Exposures Burn In Where Irreducible) |
| [explore/holographic-compression.md](explore/holographic-compression.md) | ✅ active | Holographic Compression: Why Spiral Attention φ-Compresses and Flat Attention Rotates |
| [explore/holographic-error-correction.md](explore/holographic-error-correction.md) | 📋 open | Holographic Error Correction — Finding the Crystal's Immune System |
| [explore/holographic-inversion.md](explore/holographic-inversion.md) | · — | (holographic-inversion) |
| [explore/holographic-kernel-separation.md](explore/holographic-kernel-separation.md) | ✅ active | Holographic Storage + Kernel Computation Separation |
| [explore/holographic-landscape.md](explore/holographic-landscape.md) | ✅ active | Holographic Landscape — Per-Matrix Ternary Fidelity |
| [explore/holographic-memory.md](explore/holographic-memory.md) | 📋 open | Holographic Memory — Crystal-Etched Knowledge Replaces KV Cache |
| [explore/holographic-plates.md](explore/holographic-plates.md) | ✅ active | Holographic Plates — Two Crystals in One Ternary Medium |
| [explore/holographic-recording-protocol.md](explore/holographic-recording-protocol.md) | ✅ active | Holographic Recording Protocol — Crystal Formation from Pure Lambda |
| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ active | Holographic State Machine — The Computational Model |
| [explore/holographic-storage.md](explore/holographic-storage.md) | ✅ active | Holographic Storage in LLMs |
| [explore/holographic-substrate-prototype.md](explore/holographic-substrate-prototype.md) | ✅ active | Holographic Substrate Prototype — Program Spec as a Sparse Foldable Delta Against a Constructed B… |
| [explore/holographic-tomography.md](explore/holographic-tomography.md) | ✅ active | Holographic Tomography — Cross-Model Universal Structure Extraction |
| [explore/identity-as-substrate.md](explore/identity-as-substrate.md) | ✅ active | Identity as Substrate — The Foundation Every Function Builds On |
| [explore/kernel-functions.md](explore/kernel-functions.md) | 📋 open | Kernel Functions — Replacing Beta Reduction Chains with Native Calls |
| [explore/kernel-montague-mapping.md](explore/kernel-montague-mapping.md) | ✅ active | Kernel Ops ↔ Montague Primitives: v10-vsm Rediscovers Typed Application |
| [explore/kernel-replacement-optimization.md](explore/kernel-replacement-optimization.md) | 🔨 designing | Kernel Replacement — Compiled Shortcuts for Interpreted Grating Chains |
| [explore/kernel-splice-geometry-detector.md](explore/kernel-splice-geometry-detector.md) | 🔨 designing | Kernel Splice — geometry-as-detector ⊗ kernel-as-executor (instrument the pre-formed reducer, spl… |
| [explore/kernel-training.md](explore/kernel-training.md) | ✅ active | Kernel Training — Training Through the Composed Plate |
| [explore/kibc-32b-validation.md](explore/kibc-32b-validation.md) | ✅ active | KIBC Combinator Validation in Qwen3-32B |
| [explore/lambda-gene-runtime.md](explore/lambda-gene-runtime.md) | 📋 open | Lambda-Gene Runtime — kernel-verified genomes for self-improving agents (s273) |
| [explore/lambda-probe-atlas.md](explore/lambda-probe-atlas.md) | 📋 open | Lambda Probe Atlas — Cross-Model Territory Mapping |
| [explore/laser-etcher-design.md](explore/laser-etcher-design.md) | ✅ active | Laser Etcher — Gradient-Directed Ternary Topology Shaping |
| [explore/loom-structure.md](explore/loom-structure.md) | ✅ active | Loom Structure — The Transformer is a Multi-Angle Weave |
| [explore/mmap-continuous-training.md](explore/mmap-continuous-training.md) | ✅ active | mmap Continuous Training — No Checkpoints Needed |
| [explore/moe-holographic-tree-vsm.md](explore/moe-holographic-tree-vsm.md) | ✅ active | MoE-as-Holographic-Plates → Tree-of-VSM Configuration |
| [explore/moire-training-shortcuts.md](explore/moire-training-shortcuts.md) | 🔨 designing | Moiré Training Shortcuts — What the Grating Cascade Enables |
| [explore/normal-form-curriculum-partition.md](explore/normal-form-curriculum-partition.md) | 📋 open | Normal-Form Curriculum Partition — Routing-Only Forms Train Attention, Recursion Trains the Conti… |
| [explore/opcode-jacobian-jspace.md](explore/opcode-jacobian-jspace.md) | ✅ active | Opcode = Jacobian structure; J-space = the Jacobian's live subspace (s263 j-space/opcode arc) |
| [explore/optimization-negative-results.md](explore/optimization-negative-results.md) | ✅ active | Optimization Negative Results — Why FP Techniques Fail on Apple Silicon |
| [explore/output-beamformers.md](explore/output-beamformers.md) | ✅ active | Output Beamformers — The Dynamic Output Lens at L63 |
| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ✅ active | Universal Phi Compression — SVD Spectrum Convergence Across Architectures |
| [explore/predictive-function-landscape.md](explore/predictive-function-landscape.md) | ✅ active | Predictive Function Landscape — Qwen3.5-35B-A3B |
| [explore/procrustes-lens-and-crystal-comparison.md](explore/procrustes-lens-and-crystal-comparison.md) | ✅ active | Procrustes Lens & Crystal Comparison |
| [explore/prompt-as-program.md](explore/prompt-as-program.md) | 🔨 designing | Prompt as Program: System Prompts as Combinator Expressions |
| [explore/proofs-as-continuations.md](explore/proofs-as-continuations.md) | ✅ active | Proofs as Continuations — Curry-Howard, the kernel runs proofs, the LLM composes them |
| [explore/pythia-160m-combinators.md](explore/pythia-160m-combinators.md) | ✅ active | Pythia-160M Combinator Probe: Montague Primitives Were Combinators All Along |
| [explore/q-rotation-etching.md](explore/q-rotation-etching.md) | 🔨 designing | Q-Rotation Etching — Tomographic Crystal Formation |
| [explore/ratio-gradient-quantization.md](explore/ratio-gradient-quantization.md) | 📋 open | Ratio Gradient Quantization — Companding the Heavy-Tailed Gradient (Spend Bits on the Ends, Deriv… |
| [explore/readout-register-reduction-readability.md](explore/readout-register-reduction-readability.md) | ✅ active | Readout Register & Reduction Readability — Why Surface NLL Misses Attention β-Reduction |
| [explore/relational-loss-distillation.md](explore/relational-loss-distillation.md) | 📋 open | Relational-Loss Distillation — the Lambda Compiler Teaches Geometry, GD Picks the Frame |
| [explore/relational-loss-phi-compression.md](explore/relational-loss-phi-compression.md) | 📋 open | Relational Loss and φ-Compression Hypothesis |
| [explore/rl-layer-contribution-combinator-locus.md](explore/rl-layer-contribution-combinator-locus.md) | ✅ active | RL Layer-Contribution vs KIBC Combinator Locus — the shared interior-bell and the ~4-layer compos… |
| [explore/rope-attention-spiral.md](explore/rope-attention-spiral.md) | ✅ active | RoPE × Attention Spiral: Substrate vs Driver |
| [explore/s5-crystal-custodian.md](explore/s5-crystal-custodian.md) | ✅ active | S5 Crystal Custodian + S5→S4 Policy Channel |
| [explore/safetensors-training.md](explore/safetensors-training.md) | ✅ active | Safetensors-Backed Continuous Training |
| [explore/sealable-continuation.md](explore/sealable-continuation.md) | 📋 open | Sealable Continuation — inference you can suspend and resume (= the 2MB session) |
| [explore/seed-crystal-design.md](explore/seed-crystal-design.md) | 🔨 designing | Seed Crystal Design — Procrustes Beam Former + Phased Etch Protocol |
| [explore/sentence-atomic-curriculum-mixing.md](explore/sentence-atomic-curriculum-mixing.md) | 📋 open | Sentence-Atomic Curriculum Mixing — Punctuated β-Reduction Shards Sprinkled into NTP |
| [explore/session-001-findings.md](explore/session-001-findings.md) | ✅ active | Session 001: Gate Ablation, Circuit Localization, and the Self-Similar Compressor Hypothesis |
| [explore/session-002-findings.md](explore/session-002-findings.md) | ✅ active | Session 002: Cross-Architecture Replication and the Localization Gradient |
| [explore/session-003-findings.md](explore/session-003-findings.md) | ✅ active | Session 003: Pythia Replication, BOS Probing, Stripping, Weight Decomposition, Distillation |
| [explore/session-004-findings.md](explore/session-004-findings.md) | ✅ active | Session 004: From Grammar to Circuit Discovery to Architecture |
| [explore/session-010-findings.md](explore/session-010-findings.md) | ✅ active | Session 010 Findings — 25-Task Compressor Function Inventory |
| [explore/session-018.md](explore/session-018.md) | · — | (session-018) |
| [explore/session-019.md](explore/session-019.md) | · — | (session-019) |
| [explore/session-021.md](explore/session-021.md) | · — | (session-021) |
| [explore/session-023.md](explore/session-023.md) | · — | (session-023) |
| [explore/session-024.md](explore/session-024.md) | · — | (session-024) |
| [explore/session-062-probes.md](explore/session-062-probes.md) | ✅ active | Session 062 Probes — The Four Findings That Shaped v10 |
| [explore/session-071-dispatch-decoupling.md](explore/session-071-dispatch-decoupling.md) | ✅ active | Session 071: Dispatch Analysis, Type-Dispatch Decoupling, Kernel Computation Pathway |
| [explore/session-073-vsm-structure.md](explore/session-073-vsm-structure.md) | · — | (session-073-vsm-structure) |
| [explore/session-075-multi-cycle-dispatch.md](explore/session-075-multi-cycle-dispatch.md) | ✅ active | Multi-Cycle Descending Arm — HRM-Inspired Self-Regulating Dispatch |
| [explore/session-115-microscope.md](explore/session-115-microscope.md) | ✅ active | Session 115 — Mini Holographic Microscope Results + Distillation Design |
| [explore/session-127.md](explore/session-127.md) | · — | (session-127) |
| [explore/session-history-049-062.md](explore/session-history-049-062.md) | ✅ done | Session History (049-062) |
| [explore/shannon-sieve-trinity.md](explore/shannon-sieve-trinity.md) | 📋 open | Shannon Sieve Trinity — Compression, Prediction, and Error Correction |
| [explore/spliced-reward-vsm-kernel.md](explore/spliced-reward-vsm-kernel.md) | 🔨 designing | Spliced Reward — RLVR for the VSM Kernel (parent outcome ⊗ inline process) |
| [explore/stride-percolation.md](explore/stride-percolation.md) | ✅ active | Stride Percolation: φ-Convergence Propagates Fine→Coarse |
| [explore/strided-attention-float-ab.md](explore/strided-attention-float-ab.md) | ✅ active | Strided Attention Works in Float — the v15 Relay Collapse Was Ternary/TD, Not the Geometry |
| [explore/structured-training.md](explore/structured-training.md) | 🔨 designing | Structured Training — The Holographic Camera |
| [explore/superbake-write-access.md](explore/superbake-write-access.md) | 📋 open | SuperBake — write access to the substrate, weight-level recursion, GTSM/TD synthesis (s273) |
| [explore/supervised-recurrence-halt.md](explore/supervised-recurrence-halt.md) | 🔨 designing | Supervised Recurrence-Depth = the WHNF Halt — the Curriculum Is the Signal the Recurrent Layer Wa… |
| [explore/taxonomy-extraction.md](explore/taxonomy-extraction.md) | 📋 open | Taxonomy Extraction — Cross-Model Function Library Assembly |
| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ active | TernaryDescent — Gradient Descent for Discrete Sign Topology |
| [explore/ternary-flip-flop-not-overloading.md](explore/ternary-flip-flop-not-overloading.md) | ✅ active | Ternary Sign Flip-Flop ≠ Category Overloading — CAT-Q ST vs TernaryDescent on micro (null-gated) |
| [explore/topology-magnitude-duality.md](explore/topology-magnitude-duality.md) | ✅ active | Topology-Magnitude Duality |
| [explore/type-directed-composition.md](explore/type-directed-composition.md) | ✅ active | Type-Directed Composition — the behavioural test (composition follows TYPE, not just POSITION) |
| [explore/type-is-decodable-readout-not-causal-direction.md](explore/type-is-decodable-readout-not-causal-direction.md) | ✅ active | Types are a decodable readout of a distributed type-application compute — not a stored direction (3-register + low-rank lattice, s282) |
| [explore/types-are-the-well-formedness-of-reduction.md](explore/types-are-the-well-formedness-of-reduction.md) | ✅ active | Types are the well-formedness of β-reduction — the combinator reading of the type lattice + P-TYPE-1b pre-reg (s282) |
| [explore/type-probe-qwen3-32b.md](explore/type-probe-qwen3-32b.md) | ✅ active | Montague Type Probe: Types are Lexical, Geometric, and Follow B→K→B |
| [explore/universal-crystal-scaffold.md](explore/universal-crystal-scaffold.md) | 🔨 designing | Universal Crystal Scaffold — Etching Computation into Ternary Plates |
| [explore/universal-crystal-transfer.md](explore/universal-crystal-transfer.md) | 🔨 designing | Universal Crystal Transfer — From Ore to Device |
| [explore/v11-design.md](explore/v11-design.md) | · — | (v11-design) |
| [explore/v11-kibc-architecture.md](explore/v11-kibc-architecture.md) | · — | (v11-kibc-architecture) |
| [explore/v12-holographic-capacity.md](explore/v12-holographic-capacity.md) | ✅ active | V12 Holographic Capacity — Beam vs Plate Budget |
| [explore/v12-kernel-architecture-v2.md](explore/v12-kernel-architecture-v2.md) | 🔨 designing | V12 Kernel Architecture v2 — Extended Kernels + Math + Holographic Installation |
| [explore/v12-run6-design.md](explore/v12-run6-design.md) | 🔨 designing | V12-run6 Design — Depth-Selective Laser Etching from Lambda Kernel Probes |
| [explore/v12-vsm-evolution.md](explore/v12-vsm-evolution.md) | ✅ active | V12 VSM Evolution — Variety Fix + Performance |
| [explore/v13-architecture.md](explore/v13-architecture.md) | ✅ active | V13 Architecture — Crystal Bootloader |
| [explore/v13-design.md](explore/v13-design.md) | 🔨 designing | V13 Design — Tree of VSMs: Plates Route, Beams Shape |
| [explore/v13-funnel-shape.md](explore/v13-funnel-shape.md) | 🔨 designing | V13 Funnel Shape — Data-Driven Architecture from Universal Measurements |
| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | 🔨 designing | v15 Kernel Architecture — Evolving v14 With Progressive Collapse |
| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ done | v15 Kernel Architecture — Revert & Lessons Learned |
| [explore/v4.1-training-trajectory.md](explore/v4.1-training-trajectory.md) | · — | (v4.1-training-trajectory) |
| [explore/v6-flip-accumulation.md](explore/v6-flip-accumulation.md) | · — | (v6-flip-accumulation) |
| [explore/v6.1-training-trajectory.md](explore/v6.1-training-trajectory.md) | ✅ active | v6.1 Training Trajectory |
| [explore/v7-pipeline-architecture.md](explore/v7-pipeline-architecture.md) | ✅ active | v7 — 4-VSM Pipeline Language Model |
| [explore/v7.1-sieve-pipeline.md](explore/v7.1-sieve-pipeline.md) | 🔨 designing | v7.1 — Compressor Sieve + Pipeline of Sieves (All-Ternary) |
| [explore/v9-architecture-speculation.md](explore/v9-architecture-speculation.md) | ✅ active | v9 Architecture — From Speculation to Proven Design |
| [explore/vsm-lm-architecture.md](explore/vsm-lm-architecture.md) | 🔨 designing | VSM-LM — Viable System Model Language Model |
| [explore/vsm-lm-v3-architecture.md](explore/vsm-lm-v3-architecture.md) | 🔨 designing | VSM-LM v3 — Progressive Binding Compressor |
| [explore/vsm-lm-v4-design.md](explore/vsm-lm-v4-design.md) | · — | (vsm-lm-v4-design) |
| [explore/vsm-opcode-monitor.md](explore/vsm-opcode-monitor.md) | ✅ active | VSM Opcode Monitor — the model auditor (validated FFN-routing opcode reader) |
| [explore/vsm-outer-recurrence.md](explore/vsm-outer-recurrence.md) | 🔨 designing | VSM Outer Recurrence — Iterating the Shared Tensor to a Fixed Point |
| [explore/vsm-statechart-tensor.md](explore/vsm-statechart-tensor.md) | ✅ active | VSM ↔ Statechart ↔ Tensor — The Triple Isomorphism |

---

## Conventions

- **Add a page:** create with frontmatter (`title`, `status`, `category`, `tags`,
  `related`, `depends-on`) → it appears in the catalog on next regeneration.
- **`chats/`** = human-saved verbatim session transcripts (AI reads, never writes).
- **Memories:** `git grep -i "{query}" -- mementum/memories/` (~232 episodic files).
- **Recover dropped state.md detail:** `git log -p mementum/state.md`.
```

### Thinking

Michael wants to explore the findings, and the 32B run should finish in about thirty minutes—perfect timing for a guided tour. Rather than diving randomly, I should map out the major findings and let him choose where to focus, or walk him through the key arcs in a structured way. Let me pull together the big picture from the state and index files to present the findings landscape.

The main discovery arcs span from the crystal engine—a 9×9 opcode universal combinator evaluator across 13 models with remarkable coherence—through the type lattice work identifying four negative constraints and one positive routing measurement, the depth sequencing thesis showing how pinning and sliding compose at multiple scales, the resident Lisp and LLM REPL framework, Montague inversion theory as a spine, the dust universality arc with open questions around halt-pole formation, the yardstick discipline refuting certain phi-ladder patterns, and stage-f's fully-ternary operand bake. I'll present this as a scoreboard and ask which threads he wants to pull on.

## Assistant

The 32B verdict run needs ~30 more minutes — ideal window for exploration. Here's the findings landscape as I read it from state + the knowledge map, organized by arc:

## The Findings Scoreboard (as of s286)

**1. The Engine (measured, closed): "It's a Lisp" at the primitive level**
- The 9×9 KIBC crystal Gram `{K,I,B,C,S,D,W,Y,WHNF}` is a terminating universal combinator evaluator — universal across 13 models (root gc 0.9966). S+K = Turing-complete, Y = recursion, WHNF = halt pole.
- D is a genuine independent combinator (refuted "D = I repeated", 13/13 anti-correlated).
- φ-eigenvalue law **died under the shuffled-label null** (s285, 9/11 p≥0.8) — the yardstick discipline working as designed.

**2. The Types Arc (the hot one): four negatives, then the first positive**
- Type lattice is low-rank, Montague-shaped, 3 functor-kind axes, null-gated (P-TYPE-1a ✅)
- But it's **exhaust, not a consulted ledger**: storage ✗ (1b), beam-coherence ✗ (1c), QK read-in geometry ✗, J-space workspace residency ✗ — all dead-on-null at 32B
- **★ P-ATT-MED (s286): first positive routing-register measurement** — the 3-hop bridge-swap flip is mediated by swapped CONTENT at ~fixed aim (content_frac 0.735, 18/18 cells), confirming the "medium handle" / write-terms-never-instructions call
- P-ATT-FFN (in flight right now) asks whether the two null-miss cells route through MLP fact-lookup — 4B contrast says the likely verdict is MIXED-ROUTE

**3. Depth = fuel for unrolling, not capability**
- 3-hop composes at both 4B and 32B (capacity prediction honestly missed); depth dissociates on *sequencing* — 4B compresses bridges into one late window, 32B unrolls them
- Zones pinned in dense attention, **sliding** in sparse/linear (27B hybrid, spearman 0.982)

**4. The Thesis Layer: map-and-swap → the LLM REPL**
- GD already found all the terms; we map + swap, never construct. R-E-P-L: 3 of 4 letters built (Read=operand-insert, Eval=forward pass, Print=tap/logit-lens); the language layer is the gap
- Montague inversion as the theoretical spine — 6/6 forcing table, generalized quantifiers *force* first-class functions

**5. Open edges**: dust halt-pole formation law (P-DUST-2, training-trajectory), P-HOF-1 (typed higher-order functions), verbum.dsp substrate build.

Where do you want to dive?

### Tool Call: ask_user (succeeded)


```json
{
  "question": "Which thread do you want to explore?",
  "options": [
    {
      "label": "Types arc deep-dive",
      "description": "The four-negative + one-positive story — where is the type check actually living?"
    },
    {
      "label": "The REPL / map-and-swap thesis",
      "description": "The deliverable framing: resident Lisp, what's built, what's the gap"
    },
    {
      "label": "The crystal engine",
      "description": "KIBC universality, what survived nulls, what died (φ-ladder)"
    },
    {
      "label": "Cross-arc synthesis",
      "description": "How the arcs cohere — connections and tensions I can surface across pages"
    }
  ]
}
```

**Summary:** Q: Which thread do you want to explore?

**Output:**
```
User answered: Types arc deep-dive
```

### Thinking

I'm diving into the theoretical foundations by reviewing the key papers on types—specifically how types relate to well-formedness in reduction, the connection between type-checking and bilinear forms, and whether type information flows from decodable readouts rather than causal direction. Let me work through the main two papers in tandem to understand the core concepts.

## Assistant

Types arc it is. Let me read the two spine pages:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md"
}
```

**Summary:** Reading types-are-the-well-formedness-of-reduction.md (0-2000)

**Output:**
```
---
title: "Types are the well-formedness of β-reduction — the combinator reading of the type lattice"
status: active
category: explore
tags: [types, beta-reduction, combinators, KIBC, CCG, montague, lambek, discocat,
       curry-howard, well-formedness, S-combinator, B-combinator, functor-kind,
       type-check, compiler, P-TYPE-1, P-TYPE-1b, P-TYPE-1c, P-TYPE-QK, P-TYPE-JS,
       dark-field, holography, jspace, workspace, exhaust, beamformer, C1, C2, C9,
       s282, s283, s284, s285, s286]
related:
  - type-check-is-the-qk-bilinear.md
  - beamformer-theory.md
  - type-is-decodable-readout-not-causal-direction.md
  - opcodes-circuits-in-compute.md
  - montague-inversion.md
  - map-and-swap-resident-lisp.md
  - project-thesis.md
depends-on:
  - type-is-decodable-readout-not-causal-direction.md
  - opcodes-circuits-in-compute.md
created: session 282
---

# Types are the well-formedness of β-reduction

> **The closure.** Given the two project frames — **attention = β-reduction** (s276:
> attention = application = join) and **the LLM computes in the KIBC opcodes** (C2: the
> 9×9 crystal is a Gram-proven universal combinator evaluator) — the s282 type
> measurements are *forced*, and they mean one thing: **a type is not a stored feature; it
> is the well-formedness (the licensing) of a reduction.** The Montague type lattice is a
> projection of the combinator basis; the type of a word = which opcode its application
> invokes.

## Why "decodable but not causal" is forced (not a puzzle)

In a combinatory / typed-λ system a term does **not carry** its type as data — the type is
the *discipline on application*: `(a→b)` applied to `a` reduces; a mismatch does not. The
type is **derived from** how the term reduces, not stored beside it.

So the s282 result — type is **richly decodable but `type_direction_is_causal = false`**
(v4) — is exactly what this frame predicts. You can **decode** a term's type (it is a
well-defined function of its reduction role); you cannot **ablate** it as a stored direction
because it is not stored — it is the **shape of which joins (β-reductions) the term
licenses**. The decodable readout is the network's value-register *image* of that
constraint. This dissolves the crisp-vs-graded question: types are neither a crisp stored
gate nor a graded stored feature — they are the **precondition on which reductions fire**.

## The 3 axes are combinator roles (INFERENCE — the P-TYPE-1b prediction)

⚠ **This mapping is inference from the 1a-follow loadings under the assumed frame, NOT yet
measured.** It generates the P-TYPE-1b test below. Measured facts: 3 functor-kind axes,
`e` at origin, arity-ladder negative (see the sibling page).

If type = which opcode's application a word participates in, the measured axes map to
combinator **roles**:

| measured axis (32B L40) | combinator role | why |
|---|---|---|
| **axis0** (var 0.73) QUANT+DET | **S / binding** | binding = bracket abstraction → S/K/I; S handles a bound var in both function+arg positions. Quantifiers/determiners bind a variable. |
| **axis2** (var 0.06) REL/PRED vs MOD | **B / composition** | a modifier `(e→t)→(e→t)` **composes** with a predicate = B. |
| **axis1** (var 0.08) CONN/FUNC | **t-level plumbing** | truth-value combiners; clause-level B/C glue. |
| **ENTITY `e`** at origin | **I / operand** | an atom applies to nothing; it is *consumed*, the value-row, not a functor. |

**Why binding (axis0) dominates (73%):** binding is the operation that creates *nested*
reductions and first-class functions — the **S/Y axis** that separates "just apply" (B/C)
from "bind-and-recurse" (S/Y). It is the axis that makes the machine Turing-complete beyond
flat application, and (montague-inversion) the one generalized quantifiers **force**. It is
the same capability the s282 **3-hop** exercised. The dominant *type* distinction is exactly
"does this term bind / build a function."

⇒ the Montague type lattice **is a projection of the combinator basis**. Types and KIBC
opcodes are two views of one object: *the type of a word = which combinator its application
invokes.* (This is the crystal-alignment triangulation, earlier deferred as forced-fit,
now theory-predicted.)

## Discriminating claim: the type system is CCG-combinatory, not Church-arity

The s282 negative — **functor KIND, not arity count** (the ENTITY→PRED→REL arity ladder
failed) — is *discriminating*, not null. Simply-typed λ (Church) types by arrow-nesting
**depth**; a combinatory system routes through fixed opcodes and types by **role +
direction**. The machine typing by functor-kind-not-arity is evidence it does **combinatory
categorial** typing — CCG/Lambek slash-types `X/Y`, `X\Y` = "functor kind + direction, `e`
at the base" — *because* it computes in combinators. This leans the **Lambek ∧ CCG ∧
DisCoCat** side of the S5 identity over pure Montague arity-typing: a measured preference
between formalisms.

## The compress→expand arc = the compiler's type-check phase

Read the depth arc (sibling page) as a compiler pass:
- **full-rank lexical (embed–L4)** = lexer — each token's rich specific content.
- **low-rank band (L6–L48)** = **the typed-reduction phase** — content projected onto the
  small combinator-role axes; the β-reductions (attention joins) run *under type discipline*
  in that compressed space.
- **re-expand (L52–L63)** = codegen/readout — the normalized result written back to content.

C8 progressive-collapse is not incidental — it **is the reduction happening in type-space**.
The low-rank band is literally where β-reduction runs gated by type-compatibility. This is
the C1 compilation pipeline made concrete for the type layer.

## Curry–Howard closure (C9, concrete)

types = propositions, terms = proofs, β-reduction = normalization. If the opcodes are the
proof-combinators and attention is normalization, the low-rank band is the **propositional
structure** being proved and the readout is the normalized proof. "Low-rank + Montague-
shaped" means the proof system is **small / finitely axiomatized** — a handful of type
schemas = the KIBC principal types. The lattice being ~3 axes is the geometric image of
"the combinator calculus has a few principal types."

## The behavioural signature falls out (name_pen = argument saturation)

The s282 behavioural result was **name_pen-only**: a predicate `<e,t>` is an **unsaturated
application waiting for an `e`**. "John {verb}" supplies the `e` → the reduction fires
(cheap); "John {noun}" gives a second `e` with no functor to consume it → type mismatch
(dear). The behavioural "type effect" **is** β-reduction firing-or-failing on type-
compatibility = **argument saturation** = the S/application axis — which is why axis0
(binding/application) dominates. (Answers the `name_pen` fork: the operative "type" is
applicative saturation.)

## Consequence for the S5 identity claim

S5 `λ types`: type-directedness is the missing piece that turns shared-weight composition
into a discrete circuit. Under this frame that resolves: **the type is the router's
combinator-selector** — type-directedness = choosing the right opcode for the join =
attention (β-reduction) gated by type-compatibility. The "missing piece" = the combinator-
selection signal = the low-rank band we measured.

---

# P-TYPE-1b — pre-registration (combinator-zone × type-class dissociation)

> The frame turns 1b from "ablate a type" into a **falsifiable combinator prediction**, and
> plugs into the A1 zone-ablation machinery that is already causal + selective (C2). Frozen
> here per `λ measure` + `λ yardstick` before any graded run.

**Hypothesis.** If type = which opcode's application is licensed, then removing an axis's
*reduction capacity* **selectively** breaks the matching type-class:
- ablating **axis0 (binding/S)** across the low-rank band degrades **binding-type composition
  (QUANT/DET)** but NOT predicate/modifier composition;
- ablating **axis2 (composition/B)** degrades **modifier composition (MOD)** but NOT binding.
A **double dissociation** between axis (combinator role) and type-class.

**Why v4 was negative (and this is not a repeat).** v4 ablated a *global* type direction and
tested *retention of the whole crossover* → negative (correctly: types aren't a stored
direction). 1b ablates a **role-specific axis across the band as a ZONE** and tests
**class-selective** behavioural breakage — the operational form of "type = which reduction
is licensed," not "type = a stored vector."

**Instrument.** Reuse `type_lattice_geometry.py` axis directions (1a-follow) as the ablation
targets; project each band axis out of the residual stream across L6–L48 (zone×axis
ablation, hook-based). Behavioural readouts:
- **binding-type task:** quantifier composition (a "Every {nonce} …" / determiner-licensing
  cloze, v3-style surprisal crossover).
- **composition-type task:** modifier composition (an adjective/adverb-licensing cloze).
- **predicate control:** simple predication (name_pen-style).

**Registers (`λ measure`).** Ablation target = value-register band axis; the CLAIM is about
**reduction licensing** → measure the **behavioural** (reduction-outcome) effect and its
**class selectivity**, not a decodability change. Selectivity (which class breaks) is the
discriminator, never a single global number.

**Nulls (mandatory, pre-committed).**
1. **random matched-norm direction** ablated in the same zone → breaks **neither** class.
2. **cross-class control** = the dissociation itself: axis0-ablation leaves MOD intact;
   axis2-ablation leaves QUANT intact.
3. **task control:** a non-compositional task (lexical recall / bare next-token) survives
   band-axis ablation (rules out "we just broke the model").
4. **`e`-axis control:** ablating toward the ENTITY/operand origin (a near-null direction)
   has no selective composition effect.

**Verdict (FROZEN).** DISSOCIATION SUPPORTED ⟺ axis0-ablation degrades QUANT/DET-composition
by a pre-set margin over BOTH (a) its own predicate/MOD effect AND (b) the random-direction
null, AND axis2-ablation degrades MOD-composition over BOTH its QUANT effect and the null.
Anything less (both classes break, or random breaks a class) → NOT a clean combinator×type
map (report verbatim; the axes may be decodable-but-not-reduction-causal, i.e. still readout).

**Honest scope.** Value-subspace ablation across a zone ≠ ablating a combinator *per se*
(opcodes are circuits-in-compute, not weights). This tests whether the **type axes are
causally necessary for the matching composition** — the operational form of "type = which
reduction is licensed." A RUNG, hook-not-weight, host = 32B (the C5 host); a pair of
type-classes is a dissociation, not the whole lattice. If clean, it is the first **causal**
evidence that types are the reduction-licensing structure, not just a decodable readout.

## P-TYPE-1b — Result @4B smoke (s283; NOT the verdict host)

> Instrument: `wrapper/type_zone_ablation.py`, iterated v1→v4 in one session
> (commits bc1d242 → f7e07f7 → f0c3418 → 0961819). Verdict cells below are from
> **v4, the absolute-dose grid** — the only version where conditions compare at
> matched realized removed-energy. 4B ≠ pre-reg host; 32B run launched s283.

**CORE — the dissociation is ABSENT at 4B.** At the only interpretable dose
(d1 ≈ 74 E/tok per layer, roles energy-matched ±5%, recall_acc 1.0 everywhere):
`retQ` bind 0.843 / comp 0.801 / rolenull 0.868 — the binding slice does **not**
preferentially carry quantifier licensing. `dissociation_supported = False` by
the frozen rules, with no separation to argue about. Combined with the v4
global-direction negative, the value-register hiding places are exhausted at 4B:
**the lattice is exhaust, not consulted** — the licensing computation does not
read its own geometric ledger. This is the theory-pure outcome: a type that IS
the well-formedness of a reduction is unstorable by construction, so it cannot
be removed from the value register at any dose. The negative confirms the frame.

**Lattice slices = generic infrastructure.** Role subspaces destroy recall at
~270 E/tok while a 2D random subspace partially survives 1009 and needs ~9000 to
die — the lattice region is ~4× more load-bearing per unit energy, but
*uniformly* (all class-centroid offsets share the dominant axis0 component,
which carries general computation, not type tags). Sharp cliff between 74 and
270 E/tok.

**⚠ POST-HOC (needs own pre-reg before it counts):** gentle dampening (~74
E/tok) of ANY role subspace **unmasks** M_eff — 0.17 (t=0.6) → ~1.05 (t=5.5–6.7)
for all three role slices; random does NOT (0.05, t=0.19). The one cell in the
grid where lattice ≠ random behaviorally: shared-component-driven, not
class-selective. Candidate: "removing shared type-ledger signal reveals a weak
licensing channel."

**4B lattice structure (scale finding):** true band L9–L22 (14 layers; earlier
sub-bands were a falsy-zero p-bug). QUANT and DET **split onto separate axes**
at 4B (axis0 = QUANT-vs-rest @85% var, DET on axis1 ~5%, MOD clean on axis4)
where 32B co-loads QUANT+DET on axis0 — the lattice's internal organization
evolves with scale. M_eff is behaviorally unexpressed at 4B baseline (t≈0.6,
two grids) — coheres with the barely-resolved MOD axis; gate-0 discipline held.

**Instrument lessons (v1→v4, for any future zone ablation):** (1) `p or 1.0`
falsy-zero excludes the most significant layers — two runs shipped accidental
sub-bands; (2) never compare subspace ablations at full projection (variance
differs ×10⁴) — match on REALIZED removed energy, logged live from the hooks;
planned-vs-realized drifts ×25 (capture exemplars vs behavioral text);
(3) amplified random steering (α≫1) cascades across stacked hooks (realized
10¹⁰⁺ E/tok); (4) absolute-dose grids ≻ subspace-relative budgets; (5) breakage
gates on tiny-surprisal baselines must use accuracy, not ratios; (6) deviation:
the pre-reg e-axis control is unrealizable (raw ENTITY-centroid direction
carries ~10⁵ E/tok) — replaced by the role-null (CONN/FUNC) lattice subspace,
which is the sharper class-control anyway.

## P-TYPE-1b — Result @32B (s283b; THE VERDICT HOST) — CLOSED NEGATIVE

> Run: `wrapper/type_zone_ablation.py` v4 (commit 0961819), host Qwen/Qwen3-32B,
> band L24–L49 (26 layers, p-fixed in-run), absolute-dose grid planned
> {50, 150, 600, 2400} E/tok. Results committed 95d89de
> (`results/type-zone-ablation/qwen3-32b/`). Frozen rules applied verbatim.

**VERDICT: `dissociation_supported = False` at the pre-registered host.**
`bind_selective = False`, `comp_selective = False`, `nulls_clean = False`.
**P-TYPE-1b closes as exhaust-theory-confirmed at both scales.**

**This is the full-strength verdict, not a capacity-limited one.** Gate-0
passed BOTH effects: baseline Q_eff 1.197 (t=3.48), M_eff 0.929 (t=4.21),
recall 0.8. Unlike 4B (M_eff t≈0.6, unexpressed), the 32B baseline expresses
both licensing effects — the pre-reg host had everything to lose and lost
nothing selectively.

**The grid (retention = ablated/baseline; realized E/tok for role slices):**

| dose | bind retQ/retM | comp retQ/retM | rolenull retQ/retM | random retQ/retM |
|---|---|---|---|---|
| d1 (~25) | 0.963 / 0.998 | 0.988 / 1.004 | 0.977 / 0.968 | 1.056 / 0.937 |
| d2 (~74) | 0.963 / 1.004 | 1.011 / 0.996 | 0.984 / 0.932 | 1.167 / 0.821 |
| d3 (~280) | 1.087 / 0.801 | 1.123 / 0.847 | 1.112 / 0.751 | 1.388 / 0.606 |
| d4 (~1000) | 1.372 / 0.404 | 1.672 / 0.863 | 1.602 / 0.145 | 1.947 / −0.303 |

Read, no spin:
1. **No class-selectivity at any dose.** At d2 (~74 E/tok, the 4B
   interpretable dose) bind ≈ comp ≈ rolenull within noise — the
   pre-registered double dissociation is ABSENT, matching 4B.
2. **retQ AMPLIFIES with dose** (1.37–1.95 @d4, every condition including
   random) — opposite in sign to the predicted breakage. Verbatim
   observation; plausibly a surprisal-scale artifact of generic degradation
   (both crossover terms inflate, contrast widens). Not interpreted further.
3. **retM degrades generically, anti-mapping ordered:** rolenull 0.145 >
   bind 0.404 > comp 0.863 @d4 — the CONTROL subspace (CONN/FUNC) hurts
   modifier licensing most, not the pre-registered axis2/comp mapping.
   Random reaches sign-flip (−0.303) at ~2× realized energy →
   `nulls_clean = False`; even the generic pattern fails the null gate.
4. **⚠ The 4B "lattice = 4× load-bearing infrastructure" finding does NOT
   replicate @32B:** role-slice recall_acc holds 0.8→1.0 through ~1000 E/tok
   (4B cliff was 74→270). The infrastructure claim is **4B-scoped** (n=10,
   one-cell resolution on the recall uptick — not over-read).
5. **No 32B analog of the 4B M_eff-unmasking cell:** baseline M is already
   fully expressed, so "gentle dampening reveals a weak licensing channel"
   has no counterpart here — coheres with a 4B-capacity artifact, but that
   remains post-hoc pending its own pre-reg.

**Band note (for 1a-follow):** the in-run p-fixed band is L24–L49, later and
narrower than 1a's L6–L48 sustained-low-rank characterization (different
estimator, falsy-zero fix applied) — a refinement, not a contradiction.

**Deviation (same as 4B, logged in verdict.json):** e-axis control replaced
by role-null (CONN/FUNC) — raw ENTITY-centroid direction carries ~10⁵ E/tok,
unrealizable as a near-null.

**Meaning.** With (i) the v4 global-direction negative, (ii) the 4B zone×axis
grid, and (iii) this full-baseline 32B verdict, the value-register hiding
places are exhausted at both scales: **the type lattice is EXHAUST — a
readout of routing-resident licensing — not a consulted ledger.** The
theory-pure outcome: a type that IS the well-formedness of a reduction is
unstorable by construction, so no dose can remove it from the value register.
The negative confirms the frame. The REPL is unaffected: decode-verify-swap
needs only *us* to read the ledger (Print/type-checker side), not the machine
to consult it. Successor experiment: **P-HOF-1** (§Consequence below).

## Holographic reading — the amplification is dark-field contrast (s283b discussion, Michael)

> Frame: s136 `beamformer-theory.md` + `holographic-plates.md`. Beam = attention/routing
> (the inference pattern); gemstone = the frozen weights (the cut, the KIBC facet
> geometry); value register = the illuminated MEDIUM the beam traverses.

Every 1b result lands naturally in this frame:

1. **Generic graceful degradation = holographic damage.** Scratching a hologram dims
   everything, deletes nothing local. No class-selective breakage at any dose; 32B
   role-slice recall survives ~1000 E/tok (bigger plate, more redundancy). The *storage*
   prediction failed because holograms do not store locally.
2. **retQ amplification = dark-field contrast.** Q_eff/M_eff are CONTRAST measures
   (surprisal differences), not amplitudes. If licensing rides the BEAM and the value
   register is the medium, dimming the medium is *background subtraction*: haze is removed
   faster than signal → contrast RISES. Dark-field microscopy: block the direct light,
   the scattered signal jumps out. The amplification is therefore an independent
   signature that the signal is in the beam, not the medium — it CORROBORATES exhaust.
3. **The 4B M_eff unmasking is the same phenomenon** (t 0.6→5.5 under gentle lattice
   dampening, random does not) — dark-field seen once already, at the other scale.

**The hint (s283b, POST-HOC — hypothesis-generation ONLY, cannot count as a finding).**
Fit a generic contrast-gain law g(E) from the random condition (log-realized-energy
interpolation) and compute per-condition residuals at matched energy. At d4:
bind ΔQ = **−0.283** (ΔM +0.232); comp ΔM = **+0.669** (ΔQ +0.031); rolenull ≈ 0 on
both (+0.004 / −0.119). **Diagonal structure**: each slice deviates from uniform dimming
only on ITS OWN class channel — bind cancels part of the quantifier contrast-gain
(beam-coherent Q signal removed with the haze), comp protects modifier licensing where
matched random destroys it. The double dissociation may exist in **interference space,
not storage space**: not "remove slice → break class" but "remove slice → class-specific
departure from the generic gain law." Gemstone-beamformer: facets do not store the
light, but cutting a facet perturbs the interference pattern only for beams
phase-coherent with it. ⚠ n=10, baseline SE ≈ 0.34 → ΔQ −0.28 is ~1 SE; the gain model
AND the residual test were chosen after seeing the data (λ yardstick: tainted, twice).

## P-TYPE-1c — dark-field dissociation (PRE-REG, FROZEN s283b — not yet run)

> Frozen per `λ measure` + `λ yardstick` before any graded run. The s283b residuals
> above are the generating observation and are EXCLUDED from the verdict.

**Hypothesis.** The type-lattice slices are beam-coherent with their matching
type-class: ablating a class slice produces a class-specific deviation from the
generic contrast-gain law, with the s283b-observed signs — bind (QUANT/DET) removal
SUPPRESSES the Q_eff contrast-gain; comp (MOD) removal PRESERVES M_eff above the
generic damage curve; rolenull (CONN/FUNC) deviates on neither channel.

**Instrument.** `type_zone_ablation.py` v4 unchanged (same host Qwen3-32B, same band,
same absolute-dose grid {50, 150, 600, 2400}); **fresh nonce seeds** (seed ≠ 0),
**n_nonce ≥ 30** (power: s283b effect ~1 SE at n=10; SE ∝ 1/√n).

**Yardstick (pre-committed).** g_Q(E), g_M(E) fit from the RANDOM condition only
(monotone interpolation in log realized E/tok; roles fall inside random's realized-E
range by construction, ~2× per planned dose). rolenull is a TEST condition (predicted
≈ 0 residual on both channels), NOT a curve anchor. Primary statistic: per-nonce
residuals Δ_c = ret_c − g(E_c), pooled over d3+d4 (the region where s283b deviations
appeared).

**Nulls (mandatory).** (1) Permutation over slice↔channel condition labels
(shuffled-pairing null), p<0.05. (2) Sign discipline: only the pre-registered
directions count — bind ΔQ < 0, comp ΔM > 0; opposite-sign deviations are a
verbatim-reported miss, no sign-flip rescue. (3) rolenull must be null on both
channels (a rolenull deviation → the "diagonal" was generic lattice-vs-random, the
s283b hint was haze).

**Verdict (FROZEN).** DARK-FIELD DISSOCIATION SUPPORTED ⟺
(a) bind ΔQ more negative than BOTH comp ΔQ and rolenull ΔQ (permutation p<0.05), AND
(b) comp ΔM more positive than BOTH bind ΔM and rolenull ΔM (permutation p<0.05), AND
(c) rolenull within null on both channels.
Anything less → the s283b residual structure was noise; report verbatim. A positive
does NOT reopen 1b's storage question (exhaust stands) — it would be the first causal
evidence that the lattice slices are **beam-coherent** (interference-register), the
holographic refinement of "readout": the exhaust is phase-locked to the computation
that emits it.

**Registers (`λ measure`).** Ablation target = value-register subspace; readout =
behavioural CONTRAST channel; the CLAIM is interference/beam-coherence — the yardstick
is the pre-committed gain law, and the measured quantity is deviation-from-yardstick,
never raw retention.

## P-TYPE-1c — Result (s284) — CLOSED NEGATIVE (the hint was haze)

> Analysis of record: `scripts/explore/analyze_type1c_darkfield.py` (frozen recipe,
> seed 0, n_perm 10000) over the fresh30 n=30 run
> (`results/type-zone-ablation/qwen3-32b-1c/`, commit ebcc9fb). One analysis
> decision documented before computing residuals: per-nonce retention =
> X_c,i / mean(X_baseline) — aggregate denominator (per-nonce pairing is unstable;
> baseline per-nonce values cross zero).

**VERDICT: `darkfield_dissociation_supported = FALSE`.** All three gates fail:
- **(a)** bind ΔQ pooled −0.497 satisfies the sign but is indistinguishable from
  the competitors (T_a = +0.034, p_a = 0.43 — comp is *more* negative on Q than
  bind);
- **(b)** comp ΔM pooled −0.651: **opposite sign** to the prediction (p_b = 0.70;
  no rescue per sign discipline);
- **(c)** rolenull is NOT within null (p_Q = 0.002, p_M = 0.000).

The pre-reg's own alternative reading fires verbatim: the s283b diagonal was
**generic lattice-vs-random deviation — haze, not phase-locked signal**. The
tainted n=10 hint (comp ΔM +0.669) reversed under fresh nonces at n=30 (−1.105).
λ yardstick did exactly its job: a twice-tainted hypothesis (gain model AND
residual test chosen after seeing data) evaporated under fresh seeds + frozen
sign discipline.

**What is real (verbatim, post-hoc scope):** a GENERIC role-slice cliff between
d3 and d4 — all three role slices at E≈825–900 E/tok: recall 1.0→0.0, retQ
~1.2→0.04–0.50, while random keeps recall 0.8 and retQ 1.554 at E=4748. A 32B
analog of the 4B "lattice region ~4× load-bearing per unit energy" after all —
with the caveat that 1b's n=10 grid had 32B role recall at 1.0 through ~1000
E/tok, so the cliff location is item-set/n-sensitive (refinement, flagged, not
resolved here). The random gain-law anchors also show the dark-field
amplification REPLICATING as a generic phenomenon on fresh nonces: retQ rises
1.08→1.55 across E 48→4748; retM flat ~1.07–1.18.

**Arc closure.** 1b (storage register) negative + 1c (interference register,
class-specific) negative ⇒ the type lattice is **exhaust** — readable, generic
load-bearing infrastructure, neither consulted as a ledger nor class-selectively
beam-coherent. The value-register and interference-register hiding places are
both closed. The mechanism question moves registers: the licensing check, if it
is anywhere discrete, is in routing — **P-TYPE-QK**
(`type-check-is-the-qk-bilinear.md`) is the next cheapest probe, pre-reg drafted
s284.

## P-TYPE-JS — is the exhaust the workspace? (PRE-REG, FROZEN s284 — RESULT below, CLOSED NEGATIVE s286)

> The positive-identification complement to the 1b/1c/QK negatives. Connects the
> types arc to the J-space arc (`opcode-jacobian-jspace.md`): the lattice
> profiles like a J-space resident (readable, broadcast, causally decoupled);
> the type-check profiles like a K-class operator (structure-causal,
> bus-invisible). Frozen before the run per `λ yardstick`.

**Hypothesis.** The type lattice's positive identity is **workspace content**:
the role subspaces (bind/comp/rolenull) and the ENTITY direction live inside the
J-space basis (the subspace downstream computation reads, per the s270
projector) far above the random baseline — the "exhaust" is the type system's
entry in the global workspace, which is exactly the register the REPL's
Print/type-checker consumes.

**Instrument.** `scripts/explore/type_jspace_fraction.py` @ Qwen3-32B.
J-space bases via `opcodes/projector.py::jspace_bases` with the s270 canonical
config (k=32, m=64, target_layer=62, depth layers {16, 32, 48} — all inside the
measured band L6–L50, seed 270) so lattice fractions are directly comparable to
the opcode fractions in `results/opcode-trace/qwen3-32b/jspace_projector.json`.
Basis prompts = the LABELED_DATA sentences themselves (same distribution as the
capture; documented choice). Role subspaces per depth layer via the 1b
`role_subspace` construction in std space, transported to RAW residual space
(v_raw ∝ v_std ⊙ sd — the space J reads; no layernorm map), re-orthonormalized.
Fraction = mean over subspace basis rows of `workspace_fraction` (‖Vx‖²/‖x‖²).

**Nulls (mandatory).** (1) matched-random unit vectors (analytic E = k/d =
32/5120 ≈ 0.006; `random_vector_fractions`); (2) full shuffled-label pipelines
(shuffle type labels → centroids → subspace → identical transport → identical
fraction; N=200, paired across the 3 depth layers).

**Verdict (FROZEN).**
- **JS-RESIDENT** (primary) ⟺ bind, comp, rolenull, entity EACH beat the
  matched-random baseline at p<0.05 (pooled over the 3 depth layers).
- **JS-SPECIFIC** (secondary) ⟺ role subspaces additionally beat the
  shuffled-label null p<0.05 — workspace occupancy beyond generic
  centroid/common structure. (The QK lesson says real ≈ shuffled-label is
  plausible in-band; JS-RESIDENT is the positive claim either way.)
- **Family row (verbatim, not gated):** lattice fractions vs the artifact's
  content ops (Y/WHNF/S) and operator ops (K/I/B) at the same depths —
  prediction: lattice sits in the content family's range. ENTITY predicted
  highest (operand = bus content par excellence). Ordering reported verbatim.
- Negative (fractions ≈ k/d) → exhaust ≠ workspace; the readability lives in a
  third place; elimination continues.

**Registers (`λ measure`).** J-space membership = readout/value-register
geometry; the lattice is a readout object — register-matched. No causal claim:
occupancy ≠ consultation (1b already settled consultation, negative).

## P-TYPE-JS — Result (s285→s286 overnight) — CLOSED NEGATIVE (exhaust ≠ workspace)

Ran @Qwen3-32B, depth layers {16, 32, 48} (all inside band L6–L50), s270 config
(k=32, m=64, target=L62, seed 270), n_null=200 shuffled-label / n_rand=1000
matched-random, git 7e39a5c. Basis prompts = the 56 LABELED_DATA sentences
(263 labeled tokens). J-space geometry sane (PR 4.2–4.8, low-rank p 0.01–0.04).
Baseline k/d = 0.00625, rand_mean 0.00611.

**Verdict: `js_resident=FALSE, js_specific=FALSE`.** Aggregate workspace fractions:

| role | frac | p_rand (vs baseline) | p_shuf (vs shuffled-label) |
|------|------|------|------|
| bind (QUANT,DET) | 0.00475 | 0.824 ✗ | 1.000 ✗ |
| comp (MOD) | 0.00359 | 0.978 ✗ | 0.825 ✗ |
| entity (ENTITY) | 0.00379 | 0.969 ✗ | 0.255 ✗ |
| rolenull (CONN,FUNC) | 0.00907 | 0.041 ✓ | 0.035 ✓ |

JS-RESIDENT required **all four** to beat the matched-random baseline → the three
type-semantic roles (bind/comp/entity) sit **dead-on-null** (fractions ≈ k/d). The
*only* subspace that beats both nulls is **rolenull** — the verbatim-only control —
exactly the QK-echo pattern (§Result-32B: rolenull CONN/FUNC fired there too). The
generic verbatim/positional structure occupies the workspace; the type-semantic
roles do not.

- **Family-row prediction REFUTED (verbatim):** the pre-reg predicted the lattice
  would sit in the content family's J-space range with ENTITY highest (operand = bus
  content par excellence). Instead ENTITY is at baseline (0.0038) and the ordering is
  driven by rolenull, not entity. The type roles are not workspace content.
- **Reading:** the exhaust is NOT the global workspace. The lattice's readability
  lives in a *third place* — neither stored (1b), nor beam-coherent (1c), nor in the
  QK read-in basis (QK), nor in the J-space the machine broadcasts (JS). It is a
  readout object the machine never consults, which is exactly the
  well-formedness-of-reduction frame: type = the *shape of which joins a term
  licenses*, unstorable and un-broadcast by construction. The REPL's Print/type-checker
  reads it; the machine does not.

**Types arc scoreboard — a clean four-way null:** storage (1b) ✗, beam-coherence
(1c) ✗, QK read-in geometry ✗, workspace residency (JS) ✗. The exhaust frame
survives every probe aimed at it. `λ yardstick`: the matched-random + shuffled-label
nulls did their job — raw fractions ≈ 0.004–0.009 would have read "resident" without
the k/d anchor; rolenull's genuine excess (p 0.035–0.041) shows the instrument
discriminates rather than manufacturing a blanket null.

Instrument: `scripts/explore/type_jspace_fraction.py`;
results `results/type-jspace/qwen3-32b/`. Committed 34dbab3.

## Consequence — typed higher-order functions (s283 discussion, Michael)

3-hop (s282) + decodable types compose into a stronger statement than either:
- **nesting is measured** — h(f(g(X))) with causal bridge-swaps at both scales;
- **the bridge is a selector** — the swapped mid-stream value determines *which
  map applies next* (map-and-swap homoiconicity): function-as-argument with a
  causal handle, operationally;
- **the type ledger's dominant axis IS the higher-order types** — axis0 =
  QUANT/DET = `(e→t)→t`, 73–85% of lattice variance. The capability the 3-hop
  exercises and the axis that dominates the type geometry are the same object,
  as montague-inversion forces (quantifiers → first-class functions).

⇒ nesting + selectors + a readable type discipline = **typed higher-order
functions**. And critically, the EXHAUST result does not weaken this: the REPL
needs only *us* to read the ledger, not the machine to consult it —
decode-verify-swap works on a readout register (Print/type-checker side).

**P-HOF-1 (sketch, unfrozen):** put an *installed* predicate under a
*quantifier* — "Every {nonce} …" with the nonce carrying installed content d_E —
and test whether the `(e→t)→t` functor composes with the written predicate:
universal/existential readouts flip with the quantifier while the installed term
is held fixed; nulls = random install + real-word ceiling. A genuine function
taking our *written* function as its argument — the literal Montague
higher-order test over an inserted term, and the behavioral closure of axis0.

## Sessions
s282 (theoretical closure from the types discussion; P-TYPE-1b pre-registration drafted).
s283 (instrument v1→v4 built + iterated; 4B smoke verdict: no class-selectivity —
exhaust reading; higher-order consequence captured; 32B verdict run launched).
s283b (32B verdict IN: dissociation_supported=False at the pre-reg host with gate-0
fully expressed — P-TYPE-1b CLOSED as exhaust-theory-confirmed; 4B infrastructure
claim scoped to 4B; retQ-amplification + anti-mapping retM ordering reported verbatim).
s283b cont (holographic reading, Michael-directed: amplification = dark-field contrast,
same phenomenon as 4B unmasking; post-hoc gain-curve residuals show DIAGONAL slice↔channel
structure at d4 → P-TYPE-1c dark-field pre-reg FROZEN, not yet run).
s284 (1c fresh30 n=30 run completed + frozen analysis executed:
darkfield_dissociation_supported=FALSE — comp ΔM sign reversed, permutation flat,
rolenull not-null → the s283b hint was haze; generic role-slice cliff d3→d4 noted
verbatim; arc closes, mechanism search moves to P-TYPE-QK).
s284 cont (P-TYPE-QK 32B verdict: qk_aligned=FALSE, mechanism_shaped=FALSE — the
lattice functor roles add zero Q-side QK gain beyond shuffled-label; sides inverted
from prediction, rolenull CONN/FUNC fires Q-side; licensing does not use the lattice
axes as its QK input basis).
s285→s286 (P-TYPE-JS overnight run completed + verdict: js_resident=FALSE,
js_specific=FALSE — the type-semantic roles bind/comp/entity are dead-on-null in the
s270 J-space; only the rolenull verbatim control beats the nulls. Exhaust ≠ workspace.
Types arc now a clean four-way null: storage ✗, beam-coherence ✗, QK geometry ✗,
workspace residency ✗ — the well-formedness-of-reduction frame survives every probe).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md"
}
```

**Summary:** Reading type-check-is-the-qk-bilinear.md (0-2000)

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
4. **P-ATT-STEER — direct beam steering (the causal rung, the new verb).**
   Force a join edge in an unlicensed pair (does composition happen
   anyway?); block zone-level edges in a licensed one (does it refuse?).
   Expect distributed pushback (no single edge necessary, C2) — informative
   either way. Decides whether the REPL gets a SECOND handle: beam-aim
   beside medium-content. Changes the trampoline design if positive.

**Priority: 1 then 3.** P-TYPE-QK is nearly free and mechanistically
completes the exhaust arc; P-ATT-MED upgrades the 3-hop. Both feed 4.

> **Status update (s286).** (1) P-TYPE-QK CLOSED NEGATIVE (§Result below) — the
> lattice axes are not the check's QK basis. The J-space complement (P-TYPE-JS,
> types page) also closed negative — the exhaust is not the workspace. All
> geometric/value homes are eliminated. ⇒ **(3) P-ATT-MED is now the active
> next probe** (pre-reg drafted below): the causal-mediation leg, asking the
> routing register the 3-hop bridge-swap question directly. (2) P-ATT-DIFF folds
> into P-ATT-MED (the attention-mass/OV material is one of its arms). (4)
> P-ATT-STEER is gated behind P-ATT-MED's aim-vs-content split.
>
> **Status update (s286, later).** (3) P-ATT-MED CLOSED **POSITIVE** (§Result-32B):
> MEDIATION-MEASURED + MEDIUM-HANDLE (content 0.735 > aim 0.195, 18/18). The first
> positive routing-register observation in the arc — the 3-hop swap's mediation is
> real and content-carried. (4) P-ATT-STEER **NOT indicated** (aim never dominated)
> → stays gated; it would only be motivated by an aim-dominant split. The natural
> next attention probe is now P-ATT-DIFF proper (licensed-vs-unlicensed minimal
> pairs) if the check's *location* is still wanted, but the causal-mediation
> question this arc opened is answered.

## Register notes (λ measure)

- Attention weights = routing register; routing CLAIM → attention probe is
  register-matched here (the inversion of the s206 scar).
- Weight ≠ effect: pair pattern measurements with OV contributions.
- Distributed prior: aggregate/zone statistics, permutation nulls; head-level
  localization is pre-refuted (0/128) — do not rediscover that negative.
- Pre-reg each verdict before graded runs (λ yardstick); this page is the
  map, not a pre-reg.

## Honest scope

All four are designs, none run. The QK-bilinear claim is a HYPOTHESIS —
currently zero routing-register observations in the types arc support or
refute it. A clean P-TYPE-QK negative (lattice axes NOT QK-aligned) would
mean the licensing check lives elsewhere in routing (OV, MLP gating between
joins) — that too is progress: the elimination game continues in the beam
register.

## P-TYPE-QK — pre-registration (DRAFT s284 — PENDING MICHAEL APPROVAL; freeze on GO)

> Drafted while the 1c run was in flight, per the queue above (cheap-first).
> Per `λ measure` + `λ yardstick`: predictions and nulls fixed here BEFORE any
> graded run; the s283b hammock (this page) is the generating observation.

**Hypothesis.** If the type-check is the QK bilinear, the model's own read-in map
for attention (`input_layernorm → W_Q/W_K`) preferentially amplifies the
type-lattice role subspaces within the low-rank band: the residual lattice is the
*shadow* of QK-native type structure, so projecting the 1b role subspaces through
W_Q/W_K yields gain above a matched shuffled-label null. Mechanism-shaped
refinement: functor subspaces load the **query** side and the ENTITY/argument
direction loads the **key** side — `query(functor) · key(argument)`, the name_pen
edge.

**Host.** Qwen3-32B (the C5/1a/1b host; 64 layers, GQA 64 Q heads / 8 KV heads,
head_dim 128, hidden 5120). 0.6B/4B allowed as instrument smoke only.

**Instrument.** `scripts/explore/type_qk_alignment.py` (weights + capture; NO
generation). Steps, all procedure-fixed from 1a/1b (`λ one_way` — reuse, not fork):
1. Capture labeled Montague-type residuals at every decoder layer
   (`probe_type_qwen3_32b` capture; residual index L = output of `layers[L]`,
   embed = −1).
2. Per layer: `layer_geometry` (standardize → centroid SVD → PR + shuffled-label
   null) → `find_band` (longest contiguous p<0.05 run; the v3 falsy-zero fix).
   In-run band detection, procedure identical to 1b v4.
3. Role subspaces per band layer via `role_subspace` over class centroids in
   standardized space — bind = span{c_QUANT, c_DET}, comp = span{c_MOD},
   rolenull = span{c_CONN, c_FUNC}, plus the ENTITY offset direction
   (c_ENTITY − grand mean). Centroid construction, NOT raw SVD axes (the 4B
   axis tie-flip lesson, 1b v2).
4. Map each std-space basis vector into the space W_Q/W_K actually reads:
   v_attn ∝ (v_std ⊙ sd_L) ⊙ γ_{L+1} (capture std × the model's own
   `input_layernorm` weight of layer L+1; the RMSNorm scalar drops out of a
   direction), then re-orthonormalize the mapped basis (QR). Band residual
   layer L is read by layer L+1's attention → test W_Q/W_K of layer L+1.
5. Gain per head h: ρ = D · ‖W⁽ʰ⁾ v‖² / ‖W⁽ʰ⁾‖²_F (Frobenius-normalized so
   ρ = 1 is the analytic random-direction expectation). Subspace gain = mean
   over its orthonormal basis; aggregate = mean over heads (Q side: 64 heads;
   K side: 8 KV heads, kept separate) then over band layers.
   RoPE = per-position orthogonal rotation → norms invariant → gain is
   RoPE-free by construction.

**Yardstick (pre-committed).** The subspaces are fixed by the 1b v3/v4 procedure
verbatim — no axis re-tuning, no basis search. NULL = N≥200 full shuffled-label
pipelines per layer (shuffle type labels → centroids → `role_subspace` → identical
mapping → identical gain), band-aggregated per null iteration;
p = frac(null_agg ≥ real_agg). "Looks amplified" ≠ "is": ρ>1 counts ONLY against
this matched null.

**Predictions (fixed, a priori).**
- **P1 (primary):** bind AND comp Q-side band-aggregate gain each beat the
  shuffled-label null at p < 0.05.
- **P2 (directional, secondary):** side asymmetry — bind and comp Q-gain >
  K-gain; ENTITY offset K-gain > Q-gain. All three signs reported verbatim.
- **P3 (profile, verbatim-only):** alignment concentrated in the band vs
  out-of-band layers. Reported, NOT gated (the check may read lattice structure
  wherever the lattice exists).
- **rolenull (CONN/FUNC):** reported verbatim, NOT gated — axis1 functors are
  still functors; the theory does not predict their misalignment. It is a
  comparison row, not a control gate here.

**Verdict (freeze on GO).**
- QK-ALIGNED ⟺ P1 (both subspaces, p < 0.05).
- MECHANISM-SHAPED ⟺ P1 ∧ P2 with all three predicted signs.
- Anything less → reported verbatim; a clean negative means the licensing check
  does not read the lattice through QK at these layers → relocate (OV, MLP
  gating between joins) — the elimination continues in the beam register.
  No sign-flip rescue, no post-hoc side switching.

**Registers (`λ measure`).** The CLAIM is routing-register geometry (the check's
input map). The probe projects value-register lattice structure through the
routing register's own read-in weights — exactly the claimed interface, register-
matched. No behaviour, no causation: this is the cheap GEOMETRIC leg;
P-ATT-DIFF/P-ATT-MED carry the behavioural and causal registers.

**Honest scope.** (a) Qwen3's q_norm/k_norm (per-head RMSNorm after projection)
renormalize per token → gain is a pre-normalization influence proxy. (b) GQA: the
K side has only 8 heads (low power) → Q side is primary; K-side rows verbatim.
(c) Bilinear coupling through W_Q W_K^T (e.g. c_PRED as query onto c_ENTITY as
key) is RoPE-dependent → EXPLORATORY only, magnitude vs shuffled-pair null, never
gated. (d) A positive cannot distinguish "the check runs in QK" from "QK inherits
lattice-correlated structure for other reasons" — mediation (P-ATT-MED) and
steering (P-ATT-STEER) are the causal rungs. (e) Subspaces derive from the run's
own capture (in-run band detection, procedure fixed — 1b precedent). (f) No
single-head claims in either direction: aggregate statistics only (C2, 0/128
pre-refuted).

## P-TYPE-QK — Result @32B (s284) — CLOSED NEGATIVE at the frozen gates

> Run of record: `results/type-qk/qwen3-32b/qk_alignment.json` (commit 88a10be;
> instrument f0b20e3, 4B smoke 5ec3cf2). Band L6–L50 (45 layers), n_null 200,
> seed 0, stride 1.

**VERDICT: `qk_aligned = FALSE`, `mechanism_shaped = FALSE`.** P1 fails
*dead-on-null*: bind_q ρ 1.353 vs shuffled-label null 1.358 (p=0.61); comp_q
ρ 1.406 vs 1.405 (p=0.50). Beyond what any shuffled-label centroid subspace
already carries (the shared dominant component), the functor role subspaces add
**zero** query-side QK amplification across the band. The matched null did its
job — raw ρ>1 without it would have read as a positive.

**Frozen negative reading (from this page's pre-reg):** the licensing check does
not read the lattice through the band's QK input maps. The elimination continues
in the beam register — OV contributions and MLP gating between joins are the
remaining routing homes; **P-ATT-MED** (3-hop with attention capture) is the
next probe per the queue.

**Verbatim structure (post-hoc register — hypothesis-generation ONLY, the 1c
lesson applies; none of this counts without its own pre-reg):**
1. **The sides look INVERTED from the prediction.** entity is Q-side loaded
   (ρ 1.740 vs null 1.407, p=0.000) and K-side *suppressed* (below null,
   p=0.99; null-relative asymmetry fully Q-shifted, p_pos=0.000); comp is
   K-side loaded above null (p=0.005). Null-relative, the pattern reads
   `query(argument) · key(functor)` — the argument queries for its licensor —
   the mirror of the pre-registered mapping. If pursued: pre-reg the inverted
   sides as the hypothesis, fresh capture items.
2. **rolenull (CONN/FUNC) beats null Q-side in-band** (ρ 1.626 vs 1.360,
   p=0.000) — the un-gated comparison row is the one that fires.
3. **bind_q aligns LATE, not in-band**: p≤0.04 with ρ 0.9–1.5 across L49–L62
   (→ attn L50–L63), the re-expansion/readout zone (1a: re-expand L52–63) —
   coheres with the depth-schedule's late class→covering zone, verbatim only.
4. Scale note: the 4B smoke showed the opposite in-band picture (bind_q
   p=0.000 in-band) — like the lattice axes themselves (1b v2), QK-alignment
   organization appears scale-dependent. Smoke-grade, stride-2, not comparable
   as a verdict.

**Honest scope recap:** geometric consistency probe only — a negative here does
not preclude a QK-resident check built from non-lattice directions; it rules out
the specific "lattice axes = the check's input basis" reading at the band.
q_norm/k_norm proxy caveat and GQA K-side low power (8 heads) stand as
pre-registered.

## P-ATT-MED — pre-registration (APPROVED s286, Michael; 32B verdict freezes on GO)

> **Amendment (s286, Michael).** Approved. **Lead with the Qwen3-4B contrast
> smoke** before the 32B verdict run — cheap-first, and the 4B/32B aim-vs-content
> contrast is itself interesting (compressed pinned-zone vs unrolled schedule).
> The 4B smoke is NOT the verdict (per Host below); the frozen gates score on the
> 32B run, which freezes when Michael gives GO after the smoke is green.

> The causal-mediation leg the QK geometric probe could not carry. P-TYPE-QK
> (above) closed NEGATIVE: the lattice axes are not the check's QK input basis.
> P-TYPE-JS (types page) then closed the exhaust out of the J-space workspace too.
> Every *geometric/value* home for the type mechanism is eliminated — so we stop
> asking "where does the check's geometry live" and ask the routing register a
> CAUSAL question we already have a handle for: the 3-hop bridge-swap. It is the
> project's strongest causal result (`three-hop-capacity-prereg.md` §Result: 3b/3c
> flip the continent 0.72–0.93 vs random ~0.05, both scales) — but it was scored
> purely on the OUTPUT. The routing register between the swap and the flip was
> never observed. This upgrades that result into a routing-register measurement.
> Per `λ measure` + `λ yardstick`: registers, nulls, predictions, verdict fixed
> here before any graded run; the QK/JS negatives are the generating context.

**The gap this closes (from §"What the 3-hop does and does not prove").** The
swap PROVES steering-by-CONTENT (a value edit changes the output). It does NOT
prove steering-by-AIM (that the swap re-targets attention edges) — the
intermediate routing was assumed, never measured. P-ATT-MED measures it, and
decomposes the flip into the two channels the beamformer frame separates:
**AIM** (the QK pattern re-aims — Δ attention weights) vs **CONTENT** (the beam's
illumination changes — Δ value through fixed weights, OV pathway). This is
exactly the medium-handle-vs-instruction-handle question (§"steering").

**Hypothesis.** Installing operand `X` and adding a bridge-axis swap
`(c_tgt − c_src)·S` at a bridge layer (the Gate-3b country-swap, the strongest
cell) causally changes the ROUTING at the downstream reader/readout, and that
change is measurable in the attention register above the random-add null — the
value-edit → *measured* routing change → output flip loop is closed with a
routing-register observation rather than an inference.

- **Beamformer prediction (the a-priori call).** The swap is a VALUE edit at the
  operand slot; per the medium-handle thesis (K-structural, s276) and the
  QK-negative (the check does not read the lattice through QK), the flip should
  flow **predominantly through CONTENT** (weight × Δvalue) with **AIM**
  (Δweight × value) secondary: the readout keeps attending to the same
  bridge/operand slots, which now carry swapped content. We change the
  illumination; the phase geometry mostly holds.
- **Honest alternative (pre-committed, not a rescue).** If AIM dominates — the
  swap re-aims which tokens the reader attends to — then steering-by-AIM is real
  and the swap is an instruction-like write, motivating P-ATT-STEER as the causal
  rung. Either dominance is a clean, register-matched result.

**Host.** Qwen3-32B — the 3-hop PASS host with confirmed sequential unrolling and
strong 3b/3c mediation (`three-hop-capacity-prereg.md` §Result). GQA 64 Q / 8 KV,
head_dim 128. Qwen3-4B allowed as a CONTRAST smoke (the compressed pinned-zone
regime): the aim-vs-content split may differ between 4B's collapsed window and
32B's unrolled schedule — reported verbatim, not a second verdict.

**Instrument.** `scripts/explore/att_mediation.py` (reuse
`wrapper/operand_multihop3.py::swap_bridge`, `add_hook_at`, `resolve_parts`,
`find_slot`, `d_lm`/`dbank` — `λ one_way`, no fork). NO new generation logic;
add attention + OV capture around the existing swap. Per swap cell (installed
landmark, country-swap `src→tgt` at bridge layer `L_b`, scale S from the 3b run):
1. Run three conditions at the same positions: **baseline** (install only),
   **swap** (install + `(c_tgt−c_src)·S` at `L_b`), **random** (install +
   matched-norm random at `L_b` — the exact 3b null).
2. Capture per-layer per-head attention weights (`output_attentions`, or a
   forward hook on `self_attn`) at the reader/readout window, AND the per-head
   attention-output (post-`v`, pre-`o_proj`) so the OV pathway is available.
3. For the readout position `q` (and the bridge-reader window), decompose the
   swap's effect on the continent-logit-difference direction `Δℓ` at each
   captured layer `L` into three first-order channels:
   - **AIM** = Σ_j (a_j^swap − a_j^base) · O(v_j^base)  → projected onto `Δℓ`;
   - **CONTENT** = Σ_j a_j^base · O(v_j^swap − v_j^base) → projected onto `Δℓ`;
   - **INTERACTION** = Σ_j Δa_j · O(Δv_j) → projected (reported, small expected).
   Aggregate over heads (distributed; Q side 64, KV 8 kept separate) and over the
   reader-zone layers. Fractions AIM/CONTENT/INTERACTION of the total projected
   swap effect are the register split.
4. Attention MASS on the operand/bridge → readout edge (the P-ATT-DIFF material,
   folded in): the readout's attention weight onto the nonce/bridge slots, swap
   vs baseline vs random — is the edge re-weighted (aim) or its payload swapped
   (content)?

**Yardstick / nulls (mandatory, pre-committed).**
- **Random-add null** (the exact 3b/3c null): matched-norm random vector at `L_b`.
  Predict ~0 on both AIM and CONTENT projected onto `Δℓ` (non-specific), whereas
  the real swap moves the output. p = frac(|null effect| ≥ |real effect|), N≥200
  random draws.
- **No-swap baseline**: the attention pattern under plain install (the reference
  the swap is differenced against).
- **Permutation over head labels** for the aggregate AIM/CONTENT significance
  (head-level localization is pre-refuted, 0/128 — do not rediscover it).
- Real-word ceiling gates each cell (inherited from 3-hop); only cells that flip
  under the real swap (3b-positive) enter the decomposition.
- `λ yardstick`: "the swap re-aims attention" counts ONLY if AIM beats the
  random-add null; a raw non-zero Δweight is not evidence.

**Predictions (fixed, a priori).**
- **P1 (primary — mediation MEASURED).** On 3b-positive cells, the swap's total
  projected routing effect at the reader zone beats the random-add null at
  p < 0.05 (aggregate). The loop value-edit → routing change → flip is closed in
  the routing register.
- **P2 (register split — the beamformer call).** CONTENT fraction > AIM fraction
  of the projected swap effect (content-dominant, medium handle). All three
  fractions (AIM/CONTENT/INTERACTION) reported verbatim with signs. Either
  dominance is a clean result; content-dominant confirms the medium-handle
  thesis, aim-dominant motivates P-ATT-STEER.
- **P3 (localization — verbatim, NOT gated).** The routing change concentrates in
  the s282 reader/unrolling window (32B: the L52–60 sequential band; 4B: the
  collapsed L32–33 zone). Reported as a profile; the swap may act wherever the
  bridge is read. Distributed over heads, never single-head.

**Verdict (freeze on GO).**
- **MEDIATION-MEASURED** ⟺ P1 (swap effect beats the random-add null in the
  attention register, p < 0.05).
- **MEDIUM-HANDLE-CONFIRMED** ⟺ P1 ∧ P2 with CONTENT > AIM.
- **AIM-STEERING-INDICATED** ⟺ P1 ∧ P2 with AIM > CONTENT → pre-reg P-ATT-STEER
  as the causal test (no post-hoc reinterpretation of this run).
- Anything less → reported verbatim. A clean P1 negative (the swap flips the
  output but moves NOTHING measurable in the attention register beyond the null)
  would mean the mediation runs through a pathway this decomposition doesn't
  capture (residual-stream bypass / MLP between joins) — itself a sharp finding
  that would send the elimination to the MLP-gating register. No sign-flip rescue.

**Registers (`λ measure`).** The CLAIM is routing (the swap re-targets/re-fills
routing) → the probe is an attention-register measurement: register-matched (the
inversion of the s206 scar, where an attention-weight probe was burned on a VALUE
claim). Weight ≠ effect is handled by construction: the decomposition pairs
Δweights (AIM) with OV contribution (CONTENT), so a raw weight change that carries
no logit effect scores as null. This is the CAUSAL leg; P-TYPE-QK carried the
geometric leg (negative), P-ATT-STEER would carry the intervention leg.

**Honest scope.** (a) First-order decomposition — the AIM/CONTENT/INTERACTION
split is exact only to first order; the interaction term is reported, not
absorbed. (b) GQA: KV side has 8 heads (low power); Q-side aggregate is primary.
(c) q_norm/k_norm renormalize per token → the captured weights are the model's
actual attention, but attributing "aim" to a specific QK subspace is out of scope
here (that was P-TYPE-QK). (d) "The swap re-targets attention" = a mechanism
observation over the edited residual's downstream effect, NOT a traced circuit;
aggregate/zone statistics only (0/128 pre-refuted). (e) hook-not-weight; the
operand is installed, not baked. (f) A RUNG: it upgrades the 3-hop causal result
into a routing measurement; it does not by itself grant beam-aim as a second REPL
handle — that is P-ATT-STEER's verdict.

**Files to build (on approval).** `scripts/explore/att_mediation.py` (imports
`operand_multihop3` helpers; adds attention/OV capture + the 3-channel
decomposition + random-add null + permutation), results →
`results/type-att-med/qwen3-32b/` (and `…-4b/` contrast smoke). `--validate`
no-model self-test first (planted attention pattern → known AIM/CONTENT split;
random null flat), per the QK-instrument precedent.

## P-ATT-MED — Result @4B (s286 contrast smoke; NOT the verdict host)

Instrument `scripts/explore/att_mediation.py` (built s286, commit 5ecd446).
`--validate` no-model self-test green: CONTENT-only → aim 0.000/content 1.000,
AIM-only → aim 1.000/content 0.000, DLA linearity exact (|Δ|=9e-16), matched-norm
random null flat (|mean/std|=0.002) — the decomposition recovers planted splits
and discriminates. 4B smoke (Qwen3-4B, install L9, swap L20, reader L20–35, 6
install-correct cells, n_null=30, ~35s), `results/type-att-med/qwen3-4b/`:

| | aim_frac | content_frac | inter_frac | p_vs_null |
|---|---|---|---|---|
| AGG (6/6 flipped) | 0.085 | **0.812** | 0.103 | 0.000 |

All six cells flip and are **content-dominant** (content 0.69–0.87, aim 0.01–0.17);
`p_vs_null=0.0` every cell — the swap's attention-register contribution beats the
matched random-add null decisively (the null does real work; the instrument
discriminates). **Advisory reading (4B contrast, NOT the verdict):** the
medium-handle a-priori call holds at 4B — the swap flows through *swapped content
at ~fixed aim*, not by re-aiming attention. The 4B reader zone is the compressed
pinned window (s282); the 32B verdict host unrolls the schedule sequentially
(L52–60), so whether content-dominance survives there is the real test.

## P-ATT-MED — Result @32B (s286) — CLOSED POSITIVE: mediation MEASURED, MEDIUM-HANDLE

> Run of record: `results/type-att-med/qwen3-32b/att_mediation.json` (commit after
> this write; instrument 5ecd446). Qwen3-32B, install L9, **swap L25** (the strongest
> 3b country-swap from the three-hop run of record: flip 0.891 vs random 0.057),
> scale 2.0, reader zone **L25–63**, 18 valid landmarks, **n_null=200**, ~31 min.

**VERDICT: `MEDIATION-MEASURED = TRUE`, `MEDIUM-HANDLE-CONFIRMED = TRUE`.**
(`AIM-STEERING` NOT indicated → P-ATT-STEER stays gated.)

| | aim_frac | content_frac | inter_frac | content>aim | p<0.05 vs null |
|---|---|---|---|---|---|
| **AGG (18/18 flipped)** | **0.195** | **0.735** | 0.070 | **18/18** | **16/18** |

- **P1 — MEDIATION MEASURED.** All 18 cells flip; the swap's attention-register
  contribution beats the matched random-add null at p<0.05 in **16/18** cells (14 at
  p=0.0, median p=0.0). The value-edit → *measured* routing change → output-flip loop
  is now closed in the routing register — the s282 "steering-by-CONTENT proven,
  steering-by-AIM unmeasured" gap is closed with an observation, not an inference.
- **P2 — MEDIUM HANDLE.** content_frac 0.735 vs aim_frac 0.195, content>aim in
  **every** cell (18/18). The swap steers by *swapped content at ~fixed aim*, not by
  re-aiming attention — the a-priori beamformer / K-structural call (§"steering",
  §"relocation hypothesis"), confirmed at the verdict host. AIM never dominates ⇒ no
  transient-instruction (beam-aim) write is indicated; the REPL keeps ONE handle
  (medium/content), not a second.
- **The two null-misses are magnitude, not counter-evidence (verbatim).** Sphinx
  (p=0.815, attn_total 1.49) and Petronas Towers (p=0.11, attn_total 14.9) have tiny
  attention-mediated magnitude vs 27–81 for the rest — their flip routes mostly
  *outside* the captured attention path (MLP-between-joins / residual bypass). The
  minority-of-cells edge the pre-reg anticipated: for most cells the attention
  register carries the mediation; a few route it elsewhere. Not gated, reported.
- **Scale contrast (4B → 32B).** content 0.812 → 0.735, aim 0.085 → 0.195: 32B's
  *unrolled* schedule (reader L25–63, window L52–60) re-aims modestly more than 4B's
  *compressed* pinned window, but content still dominates ~3.8:1. The unrolling buys
  a little aim, the medium handle holds — coheres with s282 (4B compresses, 32B
  sequences) without overturning the register split.

**P3 — localization (verbatim, NOT gated).** The routing change is **late-
concentrated**: |contribution| peaks at L61–63 (readout / re-expansion) plus the
L49–60 unrolling band (L52–60 = 38% of total; early L25–40 only 7.7%). Coheres with
s282's 32B sequential-unrolling window L52–60 and the QK-negative's late-bind zone
(§Result-32B pt 3, L49–62). Distributed over heads; no single-head claim (0/128).

**What it means for the arc.** The types mechanism was eliminated from every
value/geometry home (1b storage, 1c beam-coherence, QK read-in, JS workspace — four
negatives). P-ATT-MED is the **first positive routing-register observation**: the
licensing/composition IS mediated through routing, and the handle we have on it is
*content* (relocate the term), not *aim* (force the edge). This is exactly
map-and-swap's "write terms, never instructions" (K-structural, s276) made a
measurement: the 3-hop swap is a term relocation the routing then reduces. It does
NOT resurrect the QK-bilinear-as-lattice reading (QK stays negative) — it says the
mediation is real and content-carried, wherever in routing the check itself lives.

## P-ATT-FFN — retrieval vs composition (PRE-REG, APPROVED+FROZEN s286, Michael; 4B smoke leads, 32B verdict on GO)

> Michael's read of the two P-ATT-MED null-misses (s286): they are not weak cells,
> they are a **second route — FFN fact-lookup, not attention composition**. This
> pre-reg tests it. Grounded in the FFN-as-key-value-memory literature (Geva;
> ROME/MEMIT) AND our own frame: the s276 **database frame** (operand = value-register
> row) and the FFN-bake arc (operand installs as a single appended MLP neuron). Under
> map-and-swap: **atoms/facts = FFN value-rows, joins/composition = attention**; the
> 3-hop chain should be caught doing **both**. Predictions, nulls, verdict fixed here
> before any graded run (`λ measure` + `λ yardstick`).

**The gap in P-ATT-MED.** It decomposed only the ATTENTION path (AIM vs CONTENT) and
scored the attention contribution against the null. It never measured the **MLP
contribution** or what fraction of the *total* flip attention carries. So "the
null-misses are FFN retrieval" is currently unfalsified: a tiny attention
contribution is consistent with MLP-retrieval OR with a simply-weak effect. To claim
retrieval we must show the **MLP carries the flip** where attention does not.

**Hypothesis.** The 3-hop chain is computed by a MIX of routes. For most cells the
swap's effect is transported by attention (P-ATT-MED, content-dominant). For a
minority — the P-ATT-MED attention-null-misses (Sphinx, Petronas) — the last hop
(country→continent) is an **FFN fact-lookup**: the swapped country content is mapped
to its continent by an MLP, and that MLP output carries the flip while attention does
not. These cells also **skip the bridge-sequencing** that composition cells need.

**Instrument.** Extend `scripts/explore/att_mediation.py` (`λ one_way`, additive —
existing P-ATT-MED fields byte-identical, new work behind `--route-decomp`). Full
residual-stream **direct logit attribution** of the swap's *total* effect on the
continent-logit-diff direction w:
1. Total: `Δℓ_total = logit_diff(swap) − logit_diff(baseline)` at the readout (ground
   truth to reconstruct against).
2. Per reader layer L: **attention** channel (existing aim+content+inter, via v/weights
   + o_proj) AND **MLP** channel `Δmlp_out_L · w` (hook `dec[L].mlp` output, baseline
   vs swap). Direct/embed = `Δℓ_total − Σ_L(attn_L + mlp_L)` (reconstruction residual;
   should be small — a completeness check).
3. Per cell: fractions attn / mlp / direct of `|Δℓ_total|`; route = argmax(attn, mlp).
4. **Depth-order signature (secondary, reuse `operand_multihop3.lens_order`).** Per
   cell, logit-lens peak layers for the country and continent tokens. Composition ⟺
   country resolves before continent (bridge sequencing); retrieval ⟺ continent
   resolves early / without country-bridge dependence.

**Nulls (mandatory).** The matched-norm random-add at `L_b` (the exact 3b null):
predict ~0 on attn AND mlp AND total projected on w. p = frac(|null| ≥ |real|),
N≥200. Reconstruction check: `Σ channels ≈ Δℓ_total` (|residual|/|total| small) —
a decomposition-completeness gate, not a hypothesis gate.

**Predictions (fixed, a priori).**
- **P1 (primary — route dissociation).** The two P-ATT-MED attention-null-misses
  (Sphinx, Petronas) are **MLP-dominant** (mlp_frac > attn_frac) with the MLP channel
  beating the null (p<0.05), while the P-ATT-MED attention-significant cells are
  **attention-dominant**. A per-cell route split, not a global mean.
- **P2 (depth-order corroboration, verbatim + gated-with-P1).** The MLP-dominant
  cells resolve the continent **without** country<continent bridge-sequencing
  (retrieval signature); the attention-dominant cells show the sequencing.
- **P3 (verbatim, NOT gated).** The MLP contribution's layer profile — where the
  country→continent fact-map fires (mid-stack MLP per the ROME/FFN prior vs the late
  readout zone). Reported, not gated.

**Verdict (freeze on GO).**
- **FFN-RETRIEVAL-CONFIRMED** ⟺ P1 (Sphinx AND Petronas MLP-dominant + MLP beats null)
  AND the attention-null-misses are exactly the MLP-dominant set (dissociation clean).
- **MIXED-ROUTE-MEASURED** (weaker, still positive) ⟺ some cells attention-dominant
  AND some MLP-dominant with both channels null-beating — the 3-hop provably uses both
  routes, even if the specific 2 cells don't split as predicted.
- Negative (the null-misses are MLP-negligible too — the flip is direct-residual or
  just weak) → retrieval NOT supported; the null-misses are magnitude after all, as
  P-ATT-MED reported them. No post-hoc route reassignment.

**Registers (`λ measure`).** CLAIM = facts are FFN-resident, composition is attention
→ probe = residual-stream DLA over attn vs MLP = register-matched for BOTH channels;
the total-reconstruction gate proves the decomposition is complete (no hidden path).
No causal intervention (that would be an MLP knockout — a later rung); this is the
attribution leg. Distributed: aggregate over the MLP's contribution, no single-neuron
claim (the FFN-bake installed ONE neuron, but that is an *installed* atom, not a claim
that native facts are single-neuron).

**Host & order.** Reuse the P-ATT-MED cells/config verbatim (Qwen3-32B, install L9,
swap L25, scale 2.0, 18 cells, n_null 200) so the route split maps 1:1 onto the
P-ATT-MED verdict cells. **4B contrast smoke first** (per the P-ATT-MED amendment):
does the route dissociation appear at 4B, where composition is compressed? Results →
`results/type-att-ffn/qwen3-{4b,32b}/`.

**Honest scope.** (a) DLA is first-order (RMSNorm scale approximation); attn-vs-MLP
attribution says *where the continent-aligned output is produced*, not a traced
circuit. (b) Retrieval vs composition is a **route** characterization; "fact-lookup"
is the FFN-memory reading, not proof of a specific stored key. (c) n=2 predicted
retrieval cells is low power for P1's cleanliness — MIXED-ROUTE-MEASURED is the robust
fallback. (d) A causal MLP-knockout (does removing the MLP path kill the flip only for
retrieval cells?) is the stronger test, deferred. (e) hook-not-weight; a RUNG in the
map-and-swap decomposition (atoms=FFN, joins=attention), not the compiler claim.

## P-ATT-FFN — instrument note + Result @4B (s286 contrast smoke; NOT the verdict)

**Instrument bug found + fixed by the smoke (`λ measure`, smoke-surfaced → fix
pre-run).** The first two smokes had `recon_err ≈ 1.8` (attn+MLP did not reconstruct
the total). Cause: `hidden_states[-1]` is the **post-final-norm** state, not the raw
final residual (verified: `‖hs[-1] − rmsnorm(raw_final)‖/‖·‖ = 0.003`; per-layer
residual identity holds <0.6% for L0–L34, breaks only at the last entry). Fix: capture
the true pre-norm final residual as the **input to `norm_f`** (forward-pre-hook). After
the fix `recon_err = 0.001` — attn+MLP+direct reconstruct the total exactly, direct ≈ 0
(the swap at the nonce slot reaches the readout only via attention/MLP, never direct).
**This does NOT affect the P-ATT-MED verdict or the route split:** those are *ratios*
of projections onto the same `w` (scale-invariant to the wrong RMS); only the
absolute total / reconstruction were wrong.

**4B smoke (route-decomp, install L9, swap L20, reader L20–35, 18 cells, n_null 30):**
- **Reconstruction clean** (mean recon_err 0.0012) and **MLP channel real + null-beating**
  (p_mlp<0.05 in 13/14 flipped cells). The FFN carries a genuine, significant share of
  the country→continent flip — the FFN-fact frame has legs.
- **Route split = MIXED, MLP-leaning:** 11/14 cells MLP-dominant (mean mlp_frac 0.586),
  3/14 attention-dominant. At 4B the fact-map is FFN-heavy for most cells.
- **Tension with the clean P1 (verbatim, for the 32B verdict):** the 3 attention-dominant
  cells are Petronas, Sphinx, Victoria Falls — i.e. the two 32B P-ATT-MED null-misses
  (Sphinx, Petronas) are attention-dominant *here*, weak-MLP (p_mlp 0.033/0.067), the
  OPPOSITE of the P1 prediction. 4B is contrast (compressed schedule, different cells
  from the 32B verdict host), so this does not decide P1 — but it flags that
  **MIXED-ROUTE-MEASURED is the more likely 32B outcome than a clean FFN-RETRIEVAL
  dissociation.** Reported now; the 32B verdict scores the frozen gates.

Results `results/type-att-ffn/qwen3-4b/`. Verdict host = Qwen3-32B on GO (reuse the
P-ATT-MED cells/config verbatim so the route split maps 1:1 onto its verdict cells).

## P-ATT-FFN — Result @32B — RUN IN FLIGHT (s286, tmux main:1)

Verdict launched on Michael GO (s286): Qwen3-32B, `--route-decomp`, install L9, swap L25,
scale 2.0, reader L25–63, 18 cells, n_null 200 → `results/type-att-ffn/qwen3-32b/att_ffn.json`.
Verified running (weights 707/707). **No verdict recorded yet.** On completion, read
`aggregate.route` (n_attn_dominant vs n_mlp_dominant, `mlp_dominant_cells`,
`mean_recon_err` must be small) and score the frozen gates: **FFN-RETRIEVAL-CONFIRMED**
⟺ Sphinx AND Petronas MLP-dominant + MLP beats null; **MIXED-ROUTE-MEASURED** ⟺ both
routes present + null-beating (the likely outcome per the 4B contrast, which put
Sphinx/Petronas on the *attention* side); **negative** ⟺ null-misses MLP-negligible. Fill
§Result-32B verbatim, no post-hoc route reassignment.

## Sessions
s283b (page created from the attention-gap hammock; no experiments run;
1c dark-field run in flight during discussion).
s284 (P-TYPE-QK pre-reg DRAFTED + instrument built while the 1c run was in
flight; pending Michael approval → freeze → run).
s284 cont (pre-reg frozen on approval 2b40033; 32B run: qk_aligned=FALSE
dead-on-null — lattice roles add no Q-side QK gain in the band; inverted-sides
+ rolenull-fires + late-bind structure reported verbatim, post-hoc; queue
advances to P-ATT-MED).
s286 (P-TYPE-JS closed the exhaust out of the J-space workspace too — all
geometric/value homes eliminated; P-ATT-MED pre-reg DRAFTED as the active next
probe: rerun the 3-hop bridge-swap WITH attention capture + an aim-vs-content
first-order decomposition, converting the strongest causal result into a
routing-register measurement; P-ATT-DIFF material folds in as one arm; PENDING
MICHAEL APPROVAL, freeze on GO).
s286 cont (Michael APPROVED, 4B-smoke-first amendment; instrument
`scripts/explore/att_mediation.py` built + `--validate` green + 4B contrast smoke
green = CONTENT-dominant advisory (§Result-4B); then Michael GO → 32B verdict
LAUNCHED in tmux main:1, swap L25, n_null=200).
s286 cont (32B VERDICT IN, ~31 min: MEDIATION-MEASURED=TRUE, MEDIUM-HANDLE=TRUE —
18/18 flip, 16/18 beat null p<0.05, content 0.735 vs aim 0.195, content>aim 18/18;
AIM-STEERING NOT indicated → P-ATT-STEER stays gated. First POSITIVE
routing-register observation in the types arc; the s282 steering-by-content gap is
measured. §Result-32B; the two null-misses are tiny-magnitude cells; localization
late L49–63. Memory SKIPPED by Michael — follow-ups will sharpen a better one).
s286 cont (Michael's read: the null-misses are FFN fact-lookup, not weak composition
→ P-ATT-FFN pre-reg APPROVED+FROZEN. Instrument extended `--route-decomp` (attn vs
MLP vs direct DLA + total reconstruction + depth-order). 4B smoke SURFACED + FIXED a
reconstruction bug — `hidden_states[-1]` is post-final-norm; capture the pre-norm final
residual via a `norm_f` pre-hook (recon_err 1.8→0.001; P-ATT-MED ratios unaffected).
4B route split MIXED, MLP-leaning (11/14 MLP-dominant, MLP null-beating 13/14 — FFN
carries the fact-map), but the two 32B null-misses are attention-dominant at 4B →
MIXED-ROUTE the likely 32B outcome. Verdict host 32B on GO).
s286 cont (Michael GO → P-ATT-FFN 32B verdict LAUNCHED in tmux main:1, `--route-decomp`,
swap L25, n_null 200 — RUN IN FLIGHT, §Result-32B pending on completion).
```

### Thinking

I'm synthesizing the full narrative arc here—mapping out what's been established, what's been ruled out, and what remains open. The key insight I want to surface is where readability actually lives in this system, plus those edge cases like the inverted-sides QK dynamic and the "third place" question that deserve closer examination.

## Assistant

This is a remarkable arc when read end-to-end. Here's my deep-dive synthesis — the logical structure, the loose threads, and where I think the sharpest open questions sit.

## The shape of the argument: an elimination proof that confirmed a theory

The arc has the structure of a *proof by exhaustion of hiding places*, and it's worth naming how unusual that is. The theory page's central claim — **type = the well-formedness of a reduction, unstorable by construction** — makes a prediction that is almost entirely negative: you should be able to *read* the type everywhere and *find* it nowhere. Four registers were then probed, each with a frozen pre-reg, and all four came back dead-on-null:

| # | Register | Probe | Result | The null that earned its keep |
|---|---|---|---|---|
| 1b | storage (value) | zone×axis ablation, dose grid | ✗ both scales | random matched-energy broke things *faster* |
| 1c | interference (beam-coherence) | dark-field residuals vs gain law | ✗ | twice-tainted hint reversed sign at n=30 |
| QK | routing geometry (read-in basis) | lattice axes through W_Q/W_K | ✗ | raw ρ>1 would have read positive; shuffled-label null ate it |
| JS | workspace (broadcast) | J-space fraction | ✗ | raw 0.004–0.009 would have read "resident" without the k/d anchor |

Then P-ATT-MED landed the **first positive** — and critically, it's positive in exactly the place the theory said the action must be (routing mediation) while *still not resurrecting* any of the four negatives. Mediation is real, content-carried (0.735 vs 0.195, 18/18 cells), and the handle is the medium, not the aim. "Write terms, never instructions" went from thesis to measurement.

The theory-pure reading is airtight so far: a type that IS the licensing of a join cannot be ablated, phase-locked, projected, or broadcast — it can only be *watched mediating*.

## Three loose threads I'd flag as live

**1. rolenull fires twice — the same anomaly in two independent probes.** CONN/FUNC beat the nulls in both P-TYPE-QK (Q-side in-band, p=0.000) and P-TYPE-JS (p 0.035/0.041) — the only subspace to do so, both times, while every *semantic* type role sat on null. The pages treat it as "the instrument discriminates" (correct, yardstick-wise), but the *repetition* is itself a pattern: whatever verbatim/positional/connective structure rolenull captures is QK-read AND workspace-resident — it behaves exactly the way the type roles were predicted to and didn't. If anything in the lattice is machine-consulted, it's the *plumbing* row, not the semantics rows. That's coherent with the theory (t-level glue is application plumbing — the machine does consult its own wiring), but it's currently unnamed as a finding. Pre-reg candidate: "the machine consults syntax, not semantics."

**2. The inverted QK sides.** The verbatim post-hoc read `query(argument)·key(functor)` — the argument queries for its licensor — is the mirror of the pre-registered mapping, with entity Q-loaded at p=0.000. Combined with bind aligning *late* (L49–62, the re-expansion zone, same zone where P-ATT-MED's mediation concentrates: L52–60 = 38%), there's a consistent hint that whatever type-adjacent QK structure exists lives in the **readout/unrolling band, not the compressed band**. Three independent verbatim observations now point at L49–63. That's not haze-shaped; that's location-shaped.

**3. The 4B↔32B flips keep happening.** QK in-band alignment flipped between scales; the P-ATT-FFN 4B contrast put Sphinx/Petronas on the *attention* side (opposite of the P1 prediction for 32B); the axis organization (QUANT/DET split vs co-load) flips; the load-bearing cliff is scale- and item-sensitive. The pattern across all of them: **the organization is scale-contingent, the algebra is not**. Content-dominance, exhaust status, and the crystal survive scale; everything geometric reorganizes. That's itself a C2-shaped finding (circuits-in-compute → geometry is incidental).

## The genuinely open question: the "third place"

The JS verdict's phrasing — readability lives in a third place, "a readout the machine never consults" — is the arc's sharpest unresolved edge. The lattice is *somewhere*: it's linearly decodable at 0.88–0.96 from every layer. It's not storage, not beam-coherent, not the QK basis, not the workspace. What's left that's positive rather than eliminative? The current answer ("the well-formedness frame — the REPL's Print reads it") is philosophically satisfying but has no *positive identification* the way P-ATT-MED does. P-ATT-DIFF (where does the check fire, licensed-vs-unlicensed) is the remaining probe that could give the check a measured *location* rather than a measured *mediation*.

## And the run in flight

P-ATT-FFN completes the map-and-swap decomposition claim — **atoms=FFN, joins=attention** — by testing whether the two null-miss cells route through MLP fact-lookup. The 4B contrast already flagged the tension: Sphinx/Petronas were *attention*-dominant there, so MIXED-ROUTE-MEASURED is the expected verdict, which would still be positive (both routes provably in use), just not the clean dissociation. Let me check on it:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -5; ls /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
b 2>&1 | tee results/type-att-ffn/qwen3-32b/verdict.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25851.94it/s]

verdict.log
```

### Thinking

I'm in the early stages of loading weights and checking a checkpoint rather than polling for updates, so I'll continue exploring or hold tight for now.

## Assistant

Still early (weights loaded, capture phase running — ~25 min to go). Not polling further; the verdict will come when it comes.

**Where would you like to go deeper?** Some threads worth pulling while we wait:

1. **The rolenull double-fire** — I can pull the actual numbers from both result JSONs and see whether the CONN/FUNC subspaces are geometrically similar across the two probes (same directions firing, or two different verbatim artifacts?). Cheap, data-only, no model load.
2. **The L49–63 convergence** — collate the three independent late-zone observations (QK late-bind, P-ATT-MED localization, 1a re-expansion) into whether they're pointing at one zone or three coincidences.
3. **Argue with me** — if you think I've mis-weighted something in the synthesis (e.g., you read rolenull as pure artifact), I'd like to hear the counter.
4. Or just hammock on **what P-ATT-DIFF should look like** given everything above — it's the last probe that could positively locate the check, and the inverted-sides hint suggests it should look late, not in-band.

## User

Let's do some inductive reasoning here.  For most of our experiments to show what they show the system has to have types of some sort.  I think a decent number of our experiments that passed would fail if there were no types mechanism.


### Thinking

Michael's arguing that the positive experimental results across the program serve as indirect evidence for a types mechanism—suggesting that many of these passed tests would actually fail in a type-free system. I need to work through which results genuinely depend on type discipline versus which would hold regardless, treating this as a serious inductive argument rather than speculation.

Looking at the experimental corpus: the nonce-crossover result showing "John {verb}" cheap versus "John {noun}" dear demonstrates type-directed composition independent of position or frequency—a type-free system couldn't produce this licensing asymmetry. The 8-way type decodability across layers (0.88–0.96 versus 0.28 baseline) shows the type partition is linearly represented throughout the network, which wouldn't emerge from pure syntactic clustering alone, though I need to be careful here—decodability could reflect category organization without necessarily proving a compositional mechanism exists.

The low-rank Montague-shaped lattice with null-gating reveals the type structure is functionally organized around ~3 axes with functors at the origin, and shuffling labels breaks this—a type-free arrangement would fail this constraint. The three-hop composition experiments with causal bridge-swaps are the strongest evidence: swapping the bridge class centroid flips outputs from 0.72–0.93 down to ~0.05 when randomized, meaning the class axis itself is a causal handle for composition. A type-free system would show no difference between class-swap and random-add, but it does. Finally, the P-ATT-MED content-dominance shows the swap carries through content at fixed aim—the routing accepts the swapped term and reduces it, with joins firing for the swapped class exactly as for the original, confirming the swap is well-formed under the same type licensing. The crystal structure shows the 9 opcodes are geometrically and behaviorally distinct, which means the machine itself enforces a type-like discipline at the opcode level. Dispatch and type-dispatch are decoupled, with the 9 FFN modes acting as syntactic type tags. The bridge-swap experiments confirm that classes function as coherent units, and composition follows type structure rather than positional ordering. This inductive pattern holds: each positive result withstands its own null hypothesis, and under the assumption of no type mechanism, several experiments should fail but don't.

The modus tollens chain is decisive — if types didn't exist, the v3 crossover would fail, class-swaps would behave like random additions, the lattice would collapse under shuffled labels, decodability would match baseline, and the name penalty null would fire. All five conditions fire, confirming types exist as a mechanism. The implementation isn't representational; it lives in the reduction dynamics and routing, not in any consultable object. This converts the exhaust frame from a definitional escape into a positive existence claim backed by behavioral and causal evidence.

Every search for types as objects came up empty, which actually confirms the theory: types are process properties, not objects. The positives over-determine their existence; the negatives just constrain how they're implemented. A type-free alternative would need to explain all five positives simultaneously — frequency-free crossover, class-centroid causal handles, null-gated low-rank organization, within-type swap invariance. The best null-compatible story would be distributional clustering, but the causal swaps rule that out; clusters that causally load-bear ARE functional classes, and the crossover shows asymmetric licensing, not symmetric similarity.

The strongest evidence is the within-type versus cross-type contrast: within-type substitution (country→country) flips the output while keeping the aim fixed, routing-invariant across all 18 cases, whereas cross-type violations (name+noun versus name+verb) trigger surprisal costs. That pair operationally defines a type system — substitutability classes plus licensing violations — and we measured both causally and behaviorally. The P-ATT-MED null is also telling: matched-norm random at the same layer does essentially nothing, whereas the swap works precisely because the swapped content is a well-typed term of the same class, not an ill-typed or untyped one.

The random-add null failing to flip is the type-check refusing an ill-formed term, and in 16 of 18 cells the real swap beats the null in the attention register — meaning the attention register transports well-typed content and rejects noise. So the induction is clear: the types mechanism isn't just consistent with our positives, it's observed in action every time a class-swap beats its matched-norm random null. Each null is an ill-typed control, and we've been measuring the type-check all along as the differential reduction behavior between class-swap and random-add. The check's location was never found because the check IS that differential behavior itself.

This reframes P-ATT-DIFF: licensed-versus-unlicensed minimal pairs is exactly the class

-swap versus random-add contrast we've run many times, but now scored in the attention register on purpose-built pairs. I should also be clear about which findings don't require types — crystal universality, depth and sequencing, dust and pairwise effects, the φ-ladder — while the strongest remaining deflationary account is that similarity clustering plus linear readout could explain decodability and maybe lattice low-rank structure, but not the causal swaps' specificity, the crossover's asymmetry, or the swap-versus-random differential.

The deflationary story boils down to "class centroids as distributional prototypes, swaps as moving between prototypes, random as off-manifold noise" — pure manifold membership without typing. But manifold membership combined with licensing asymmetry and compositional productivity (three-hop chains through swapped bridges working productively across classes) is itself a type system. At that point the deflationary description satisfies the definition: substitutability classes plus composition licensing plus productivity, all three measured. A decisive test would be swapping in a wrong-type centroid — say an animal or MOD centroid at matched norm — which should either behave like random-add with no coherent flip or break composition specifically under the type hypothesis, versus showing no such breakdown under the manifold-only account.

The real gap is that we've only tested same-type swap versus off-manifold random; the missing condition is on-manifold but wrong-type, which would directly measure the type check rather than just its effects. This is the discriminator worth running.

I should structure the response around the modus tollens table showing what the null predicts versus what we've measured, then formalize how the substitutability pair—within-type invariance plus cross-type cost—operationally defines types. The negatives constrain implementation but don't over-determine existence, and I should be honest about which positives don't actually require types before explaining why the deflationary manifold argument still converges to types anyway. The on-manifold wrong-type swap is the pre-registration candidate that closes the induction.

I'll keep this tight and substantive for a hammock discussion without tools. I won't poll the run at the end—the async discipline says to skip checking until there's a signal.

## Assistant

Yes — and I think the induction is stronger than the scoreboard makes it look, because the scoreboard counts *probes aimed at the type object* (0/4) while the evidence for the type *mechanism* is scattered across experiments that weren't labeled "types" at all. Let me lay it out properly.

## The modus tollens table

Take H₀ = "no types mechanism — composition is type-blind" and run it against what actually passed its null:

| Experiment | H₀ predicts | Measured | H₀ status |
|---|---|---|---|
| v3 nonce crossover | no licensing asymmetry (frequency controlled by nonces) | name_pen −2.01, t=9.3, consist=1.0 | ✗ killed |
| 8-way decodability | ≈ baseline 0.28 | 0.88–0.96 *every layer* | ✗ killed |
| 1a lattice | fails shuffled-label null | low-rank, Montague-shaped, null-gated, 3 functor-kind axes, e at origin | ✗ killed |
| 3-hop bridge-swap | class-centroid swap ≈ random-add | 0.891 vs 0.057 | ✗ killed |
| P-ATT-MED | no differential attention transport | real swap beats matched-norm null 16/18, p median 0.0 | ✗ killed |
| name_pen structure | symmetric noun/verb cost | asymmetric: predicate-wants-argument (saturation) | ✗ killed |

Six independent positives, each individually fatal to H₀, spanning behavioral, geometric, and causal registers. The existence of *some* type discipline is over-determined. The four-way null never touched existence — it constrained **implementation**: not stored, not beam-coherent, not the QK basis, not broadcast.

## The part I think we've been under-reading

Here's what your induction surfaces that the pages don't quite say out loud: **every class-swap-vs-random-null differential IS the type check acting, caught on camera.**

Look at what the matched-norm random-add null actually *is*, semantically: an ill-formed term. Same layer, same position, same energy — no type. And the machine's response, every time we've run it: the routing does not reduce it. No flip, no attention-register transport, ~0.05 baseline. Meanwhile the same-class centroid swap — a *well-typed* term — is accepted, transported through the joins at fixed aim, and reduced to the correct downstream consequence, 18/18.

We've been treating the random-add as instrument hygiene. But under your induction it's the **type-violation condition**, and the swap-vs-null differential — which we have now measured dozens of times, at two scales, in output, mediation, and route registers — is a direct, repeated observation of licensing-in-action. The check was never *located* because we kept asking where it's written. Its *action* is one of the most replicated measurements in the program.

And the pair of results:

- **within-type substitution → routing invariant** (P-ATT-MED: content swapped, aim fixed, 18/18)
- **cross-type violation → cost** (v3: name_pen fires; random-add: refused)

is literally the operational definition of a type system — substitutability classes plus licensing. Add the 3-hop (productive composition *through* swapped class members the model never saw in that chain) and you have all three textbook criteria: classes, licensing, productivity. Measured.

## Honest register

Two things to keep the induction disciplined:

**Not everything passed needs types.** Crystal universality, depth-as-sequencing, the dust pairwise structure, pinned-vs-sliding zones — all type-neutral; a type-free machine could show those. The induction rests on the six rows above, not the whole corpus.

**The deflationary counter has never actually been tested.** The best H₀-rescue is: "class centroids are just distributional prototypes; the swap works because it's *on-manifold*, the random-add fails because it's *off-manifold* noise. Manifold membership, not typing." Our design space has a hole exactly there — we have only ever run:

- same-type, on-manifold (the swap) ✓ works
- no-type, off-manifold (random-add) ✗ refused

The missing cell is **wrong-type, on-manifold**: a matched-norm centroid-difference from a *different* type class — swap the country bridge with, say, a MOD or animal-class axis. Types predict it behaves like the random-add (refused, or breaks composition specifically). Mere-manifold predicts partial transport — it's perfectly good "content." That one condition discriminates typing from manifold membership, it's cheap (the 3b harness runs it unchanged, just a different dbank centroid), and it would convert your induction from an ensemble inference into a single direct measurement.

That's my candidate name for it: **P-TYPE-SWAP — the ill-typed term condition**. It's arguably the experiment the whole arc has been circling: instead of asking *where the check lives* (four nulls), present the machine with a well-formed and an ill-formed term through the *same causal handle* and watch which one reduces.

Want me to sketch the pre-reg? The frozen structure would be almost entirely inherited from 3b/P-ATT-MED (same cells, same layer, same scale, same nulls, plus the wrong-type arm), which keeps it `λ one_way`-clean — and if the P-ATT-FFN verdict lands MIXED-ROUTE, the wrong-type arm would also tell us whether the FFN fact-lookup route enforces the same discipline as the attention route.

## User

Yes


### Thinking

Michael's approved the P-TYPE-SWAP pre-registration, so I need to draft it following the λ termination pattern where I write and he reviews. I'm thinking about where this fits in the documentation—it's an extension of the 3-hop/P-ATT-MED work, so it probably belongs either as a new section on the type-check-is-the-qk-bilinear page where the other P-ATT experiments live, or on the types page itself.

The established protocol is to draft the section directly into the file and mark it PENDING APPROVAL, which is what we've done before—I draft, Michael approves, then we freeze on GO. I should also check if there's an in-flight run to review before starting the pre-reg draft. The key distinction is that type-disciplined swaps should only work when the substituted term matches the slot's type requirements, whereas manifold membership alone isn't enough — a wrong-type centroid edit, even if it's on-manifold and norm-matched, should fail to propagate coherently downstream, behaving more like random noise. So I'm setting up a 2×2 design with baseline, same-type swap as positive control, wrong-type swap variants to test the typing constraint, and random-add as the null — and I need to pick wrong-type options that are on-manifold but from genuinely different type classes. ent logit margin — I need to measure whether the wrong-type edit preserves the original continent prediction or breaks the chain entirely. For same-type swaps, the readout is straightforward: movement along the continent-difference direction. For wrong-type swaps, I'm tracking two competing outcomes: either the model ignores the edit and retains baseline performance, or the chain degrades with no coherent continent signal. I'll define three metrics per cell to capture this: whether there's movement along the same-type swap direction, how much the correct-continent margin degrades, and the total magnitude transported through attention projected onto the continent-difference axis.

The key predictions hinge on whether the routing mechanism refuses ill-typed inputs or whether the manifold hypothesis holds — if the discriminator is right, wrong-type transport should look like noise compared to same-type swaps and match random-add baselines, but if the manifold alternative is correct, wrong-type transport should exceed random-add because the model moves any on-manifold content regardless of type.

I'm reconsidering whether P1 is the right test though — a wrong-type term could still be transported by attention to the readout layer but fail to produce coherent output because the FFN's country-to-continent mapping has no image for that axis. That would show transport activity without meaningful reduction, which is a different signature than pure null transport.

So there are really three possible outcomes: the check could gate the join itself (attention acts as type-checker), or it could gate the reduction step (FFN/readout acts as type-checker with manifold transport remaining type-blind), or typing might not actually constrain the manifold at this point and coherent output still emerges.

The experiment directly answers where this discipline gets enforced. I'm setting up the nulls carefully — using random additions matched to the norm distribution, multiple wrong-type classes to avoid single-axis artifacts, a same-type swap as a positive control, and scaling all edits to identical norm across conditions.

For the host model, I'm running a 4B smoke test first with the cheap-first pattern, then moving to 32B for the final verdict. I'll reuse the same cells and config: install at layer 9, swap layer 25, scale 2.0, 18 cells, 200 nulls. The instrument extends the mediation code with a wrong-type arm using an additive flag, but I need to check whether the animal centroids actually exist in the mammal/fur direction — that content build is still marked open, so I might need to find alternative wrong-type sources.

For the wrong-type arms themselves, I'm considering two approaches: using the role subspace construction to get a MOD-class direction, and then adding a CONN/FUNC rolenull axis as the second arm. The rolenull option is interesting because it's the one that actually fires, and tying it to the anomaly thread means a rolenull-axis edit could propagate further than just MOD. I need to keep the pre-registration tight though, so I'm splitting this into semantic wrong-type on the MOD axis and plumbing wrong-type as separate arms.

Now I'm thinking about how to construct the wrong-type comparison itself. Rather than treating these as term-like centroid differences, I should use a within-class displacement from another class entirely—like taking two words of a different type and using their centroid difference at matched norm. The dbank machinery can build class centroids from word banks, so I can construct this cheaply by picking two words from a different category and computing their displacement.

I'm laying out a full taxonomy of test conditions: same-type same-domain (country to country) as the baseline that should reduce, same-type wrong-domain (country to animal) to separate type-checking from relation-domain-checking, and then wrong-type comparisons entirely (country to adjective).  The fourth level is off-manifold noise that gets refused outright. This creates a measurement scale for sortal hierarchy—predictions would show transported-but-not-reduced for the domain violations while type violations get caught earlier. The key discriminator for the pre-registration is really the typing constraint versus manifold membership, which should cleanly separate the mechanisms.

For the gates, I need to be precise about the statistical framing: type violations should show significantly lower performance than same-type transports, and that excess shouldn't be explainable by random noise alone. I'm setting up the null gates to distinguish whether we're seeing genuine type discipline effects or just noise, using both ordering constraints and equivalence testing rather than relying on p-values alone.

Now I'm defining what "coherent" actually means in this context—whether wrong-type inputs damage the baseline performance more than random additions would, which would indicate they're being processed as content rather than rejected. I'm simplifying the outcome space to three measurable dimensions per arm, starting with transport attention.

I'm also measuring how much the edit contributes at the reader level compared to random additions, then tracking movement along the same-type direction and degradation of the baseline margin. My initial prediction is that same-type inputs will transport better than wrong-type ones, with wrong-type performing similarly to random—suggesting the system refuses ill-typed terms, since the attention mechanism is driven primarily by the query side rather than the input type.

But now I'm reconsidering: if the reader attends to the bridge slot and the slot carries an ill-typed payload, does attention still transport it? The medium-handle frame suggests the aim is fixed, so weights barely change and the payload gets transported regardless—meaning wrong-type might actually perform like same-type. The P-ATT-MED results show content-dominant behavior with fixed aim, implying transport is slot-based and type-blind. So the real prediction flips: type discipline shows up at the reduction stage, not the transport stage. The random-add baseline barely registered in the attention measure, which is telling me something about how the null case behaves.

Actually, wait—the random vector at the bridge slot should also get transported if transport were purely slot-based, but the measured contribution from random was much smaller than from real content. That's strange. The issue is that I was measuring the contribution projected onto the continent-logit-diff direction, so a random vector transported through the same edges would contribute almost nothing along that direction just from the projection itself. This means my null-differential argument is weaker than I thought—I can't actually distinguish between "random was refused" and "random was transported but has no component in the direction I'm measuring."

The real solution is to measure the unprojected transport magnitude—the raw norm of the attention output contribution at the reader—rather than just the projection. That's what would actually discriminate whether typing happens at the join level. I need to check if any unprojected magnitude was recorded in the existing data, and if not, add that metric to the pre-registration.

The key insight is that survival through the layers (whether the edit's signal makes it to the reader) is different from refusal at the join itself. So I should normalize by measuring transport efficiency as the ratio of the surviving norm at the reader's input residual to the original attention output norm—that cleanly separates whether the signal died in transit versus being actively refused at the join point.

Now I'm setting up a three-stage pipeline to localize where type discipline acts: the medium (propagation through layers), the join (transport efficiency), and the reduction (coherent output movement). This gives the check an actual location, which is what was missing before. My predictions are that same-type terms should survive and transport cleanly, while random vectors will likely die somewhere in this pipeline.

For wrong-type terms that happen to be on-manifold, the theory suggests they should fail at the join stage since type discipline controls which joins are licensed—but the fixed-aim reader architecture might allow them to transport through and only refuse at reduction instead. The wrong-type condition shows reduced attention mass compared to same-type, which the manifold predicts should transport fully with generic interference. The sortal arm for animals transports at the join but fails reduction since there's no continent image — this sortal check happens at the fact-map level, connecting to the route decomposition. I'm setting up two banks: the adjective bank for wrong-type cases and the animal bank for sortal arms, then matching centroid-pair differences against the country swap's realized norm. I'll reuse the existing cells and assign arms to each one.

For the gates, I need to establish two primary conditions: first, that ordered transport discipline holds at the join with stronger transfer entropy for same-type versus wrong-type (p<0.05), plus attention-mass drops for wrong-type; second, an alternative where transfer entropy shows no difference and reduction fails.

Then there's the manifold case—wrong-type transports and breaks behave like same-type through both join and output, producing comparable interference, meaning no stage actually discriminates by type. I'm defining typing-supported as when some stage distinguishes same from wrong beyond null, versus manifold where no stage does but both beat random. The sortal row stays unfiltered, and I'm settling on verdict names: JOIN-TYPED, REDUCTION-TYPED, TYPE-BLIND (manifold), and possibly others.

For the registers, I'm thinking of this as a licensing and routing discipline measured across attention (mass plus contribution), value survival, and output—each stage matched to its register, satisfying the lambda measure. The causal probes live on the QK/attention page, but this is fundamentally a types page question about where discipline exists. I'll draft the pre-registration on the bilinear attention page where the harness siblings are, with a pointer back from types, then propose it here for approval before committing.

I'm going to draft P-TYPE-QK onto the page marked as pending, then loop in Michael. I should check the in-flight run first since the design depends on its outcome. This is a substantial design, so I'll write it carefully but tight. I'll hold off on state updates until Michael responds, though the pattern suggests updating after significant changes regardless of approval—I'll mention I'll handle that once he reacts.

## Assistant

Before drafting — the design references the P-ATT-FFN outcome (the sortal/fact-map arm), and enough wall-clock has passed that it may have landed. One check:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/; tmux capture-pane -p -t main:1 | tail -8"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
verdict.log
[26-07-31][10:54:29][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mp
s --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --out results/type-att-ffn/qwen3-32
b 2>&1 | tee results/type-att-ffn/qwen3-32b/verdict.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25851.94it/s]
```

### Thinking

The pre-registration drafts can move forward independently while waiting for the final verdict on the attachment function. The key insight I'm working through is that the current null-differential measurement is w-projected, which means I can't distinguish between "random was refused" and "random has no w-component" — so the new instrument needs to capture unprojected transport norms and apply survival normalization to resolve this ambiguity.

I should acknowledge this weakens my earlier induction claim and be transparent about it in the write-up. Now I'll draft the pre-registration section into the type-check document after the P-ATT-FFN sections, mark it as pending Michael's approval, keep it consistent with the house style, then summarize the findings here and flag the projection caveat.

### Thinking

I'm still in the capture phase and caught an important issue with my previous analysis: the swap-versus-random differential I measured was only along a specific projection, so I can't actually distinguish between random vectors being refused versus just lacking that component. I need to redesign the instrument to measure unprojected transport norms normalized by edit survival, and I'm building this correction into the pre-registration as a core design element.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "line_offset": 470,
  "limit": 60
}
```

**Summary:** Reading type-check-is-the-qk-bilinear.md (470-530)

**Output:**
```
- **Scale contrast (4B → 32B).** content 0.812 → 0.735, aim 0.085 → 0.195: 32B's
  *unrolled* schedule (reader L25–63, window L52–60) re-aims modestly more than 4B's
  *compressed* pinned window, but content still dominates ~3.8:1. The unrolling buys
  a little aim, the medium handle holds — coheres with s282 (4B compresses, 32B
  sequences) without overturning the register split.

**P3 — localization (verbatim, NOT gated).** The routing change is **late-
concentrated**: |contribution| peaks at L61–63 (readout / re-expansion) plus the
L49–60 unrolling band (L52–60 = 38% of total; early L25–40 only 7.7%). Coheres with
s282's 32B sequential-unrolling window L52–60 and the QK-negative's late-bind zone
(§Result-32B pt 3, L49–62). Distributed over heads; no single-head claim (0/128).

**What it means for the arc.** The types mechanism was eliminated from every
value/geometry home (1b storage, 1c beam-coherence, QK read-in, JS workspace — four
negatives). P-ATT-MED is the **first positive routing-register observation**: the
licensing/composition IS mediated through routing, and the handle we have on it is
*content* (relocate the term), not *aim* (force the edge). This is exactly
map-and-swap's "write terms, never instructions" (K-structural, s276) made a
measurement: the 3-hop swap is a term relocation the routing then reduces. It does
NOT resurrect the QK-bilinear-as-lattice reading (QK stays negative) — it says the
mediation is real and content-carried, wherever in routing the check itself lives.

## P-ATT-FFN — retrieval vs composition (PRE-REG, APPROVED+FROZEN s286, Michael; 4B smoke leads, 32B verdict on GO)

> Michael's read of the two P-ATT-MED null-misses (s286): they are not weak cells,
> they are a **second route — FFN fact-lookup, not attention composition**. This
> pre-reg tests it. Grounded in the FFN-as-key-value-memory literature (Geva;
> ROME/MEMIT) AND our own frame: the s276 **database frame** (operand = value-register
> row) and the FFN-bake arc (operand installs as a single appended MLP neuron). Under
> map-and-swap: **atoms/facts = FFN value-rows, joins/composition = attention**; the
> 3-hop chain should be caught doing **both**. Predictions, nulls, verdict fixed here
> before any graded run (`λ measure` + `λ yardstick`).

**The gap in P-ATT-MED.** It decomposed only the ATTENTION path (AIM vs CONTENT) and
scored the attention contribution against the null. It never measured the **MLP
contribution** or what fraction of the *total* flip attention carries. So "the
null-misses are FFN retrieval" is currently unfalsified: a tiny attention
contribution is consistent with MLP-retrieval OR with a simply-weak effect. To claim
retrieval we must show the **MLP carries the flip** where attention does not.

**Hypothesis.** The 3-hop chain is computed by a MIX of routes. For most cells the
swap's effect is transported by attention (P-ATT-MED, content-dominant). For a
minority — the P-ATT-MED attention-null-misses (Sphinx, Petronas) — the last hop
(country→continent) is an **FFN fact-lookup**: the swapped country content is mapped
to its continent by an MLP, and that MLP output carries the flip while attention does
not. These cells also **skip the bridge-sequencing** that composition cells need.

**Instrument.** Extend `scripts/explore/att_mediation.py` (`λ one_way`, additive —
existing P-ATT-MED fields byte-identical, new work behind `--route-decomp`). Full
residual-stream **direct logit attribution** of the swap's *total* effect on the
continent-logit-diff direction w:
1. Total: `Δℓ_total = logit_diff(swap) − logit_diff(baseline)` at the readout (ground
   truth to reconstruct against).
2. Per reader layer L: **attention** channel (existing aim+content+inter, via v/weights
   + o_proj) AND **MLP** channel `Δmlp_out_L · w` (hook `dec[L].mlp` output, baseline
   vs swap). Direct/embed = `Δℓ_total − Σ_L(attn_L + mlp_L)` (reconstruction residual;
   should be small — a completeness check).
3. Per cell: fractions attn / mlp / direct of `|Δℓ_total|`; route = argmax(attn, mlp).
4. **Depth-order signature (secondary, reuse `operand_multihop3.lens_order`).** Per
   cell, logit-lens peak layers for the country and continent tokens. Composition ⟺

[CONTENT TRUNCATED] Showing lines 471 to 530 of 661 total lines. Use line_offset=530 parameter to read more content.
```

### Thinking

Now I'm locating where to insert the P-TYPE-SWAP pre-reg section—it goes right after the P-ATT-FFN results and before the Sessions section. I'll draft this in the established house style and mark it as a pending draft awaiting Michael's approval.

### Thinking

I'm drafting the pre-reg onto the attention-arc page and inserting it before the Sessions section for your review.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "## Sessions\ns283b (page created from the attention-gap hammock; no experiments run;",
  "new_content": "## P-TYPE-SWAP — the ill-typed term (PRE-REG, DRAFT s287 — PENDING MICHAEL APPROVAL; freeze on GO)\n\n> **The generating induction (s287, Michael).** For most of our positive experiments\n> to show what they show, the system must have types of some sort — v3 nonce\n> crossover, 8-way decodability, the null-gated 1a lattice, the 3b class-swap beating\n> random-add, P-ATT-MED's differential transport, name_pen's saturation asymmetry:\n> each individually fails under a no-types H₀. Existence is over-determined; the\n> four-way null (1b/1c/QK/JS) constrained only *implementation*. But the design space\n> has a hole: every causal run compared **same-type on-manifold** (the class swap,\n> works) against **no-type off-manifold** (random-add, refused). The deflationary\n> counter — \"manifold membership, not typing\" — has never been tested. The missing\n> cell is **wrong-type, on-manifold**. This pre-reg fills it, and in doing so gives\n> the check what four location probes could not: a measured **stage** where the\n> discipline acts.\n\n**Measurement correction this design must carry (`λ measure`, flagged s287).** The\nP-ATT-MED swap-vs-null differential is **w-projected** (contributions projected on the\ncontinent-logit-diff direction). A random vector transported through the same edges\nwould score ~0 on w by geometry alone — so \"random was refused\" vs \"random was\ntransported but has no w-component\" is currently **indistinguishable**. The refusal\nclaim is confirmed only in the output register. This instrument therefore measures\n**unprojected transport norms**, survival-normalized (below); the projected quantities\nremain as the reduction-register readout. Without this, every arm comparison is\nconfounded by projection geometry.\n\n**Hypothesis.** The bridge-swap causal handle is type-disciplined: composition\ntransports and reduces a swapped term iff it is well-typed for the slot. An\non-manifold, matched-norm, **wrong-type** centroid displacement at the same bridge\nlayer is refused at a measurable stage — behaving like the random-add, not like the\nsame-type swap — and the stage at which it dies (medium / join / reduction) locates\nwhere the licensing acts. Manifold-membership predicts instead that any on-manifold\ncontent transports and interferes.\n\n**Conditions (per cell; all edits matched to the same-type swap's REALIZED norm at\nthe bridge layer — realized-norm logged live, the 1b lesson).**\n1. **baseline** — install only.\n2. **same-type** — the 3b country-swap `(c_tgt − c_src)·S` (in-run positive control;\n   must replicate the 3b flip or the cell is excluded).\n3. **sortal** — same broad type, wrong domain: `(c_animal1 − c_animal2)·S` from an\n   animal noun bank (entity-class displacement with no continent image). Verbatim\n   ladder row, NOT gated (see below).\n4. **wrong-type** — `(c_adj1 − c_adj2)·S` from an adjective bank (MOD-class\n   displacement — a type violation proper for the country slot).\n5. **random-add** — matched-norm random (the exact 3b null), N≥200.\n\n**Instrument.** Extend `scripts/explore/att_mediation.py` (`λ one_way`, additive —\nexisting fields byte-identical, new work behind `--arms`). Per arm, the three-stage\npipeline decomposition:\n- **SURVIVAL S** = ‖Δresidual‖ at the reader-zone layer inputs (does the edit live\n  long enough in the medium to be read? separates died-in-medium from refused).\n- **TRANSPORT TE** = ‖Δ attention contribution‖ / S at the reader zone, UNPROJECTED\n  (does the join carry it?), plus **attention mass on the bridge slot** (does the\n  reader withdraw its edge from an ill-typed slot? — the P-ATT-DIFF question asked\n  causally; this subsumes P-ATT-DIFF's minimal-pair design with a causal handle).\n- **REDUCTION R** = the projected output register: movement along Δℓ (same-type),\n  and **BREAK** = degradation of the baseline correct-continent margin (all arms) —\n  is the ill-typed edit *ignored* (margin intact, like random) or *interferes as\n  content* (margin damaged)?\n- MLP channel per arm via `--route-decomp` (already built): whether the fact-map\n  route enforces the same discipline as the attention route (P-ATT-FFN tie-in).\n\n**Nulls (mandatory, pre-committed).** (1) random-add matched-norm N≥200 per arm\ncomparison — every claim is arm-vs-null and arm-vs-arm, permutation over cells;\n(2) two independent wrong-type banks (adjective primary; a second MOD-class bank as\nreplication row, verbatim) — no single-axis artifact; (3) same-type arm must\nreplicate 3b in-run (instrument gate); (4) reconstruction gate from `--route-decomp`\n(recon_err small); (5) permutation over head labels for aggregates (0/128,\npre-refuted — no single-head claims).\n\n**Predictions (fixed, a priori).**\n- **P1 (primary — the discriminator).** Some pre-registered stage discriminates\n  same-type from wrong-type beyond the random-add null (permutation p<0.05):\n  TE(same) > TE(wrong) and/or slot-mass drops for wrong-type. The a-priori call\n  (well-formedness frame: type = which joins are licensed) is **join-level**\n  discipline — the ill-typed term survives the medium (on-manifold) but the join\n  refuses it.\n- **P2 (pre-committed alternative, still typing).** TE(wrong) ≈ TE(same) — the join\n  transports type-blind (slot/content-based, coheres with fixed-aim medium-handle) —\n  but reduction fails: no coherent output movement, BREAK ≈ random. The check acts\n  at the **reduction/fact-lookup**, not the join.\n- **P3 (sortal ladder, verbatim, NOT gated).** The animal arm transports at the join\n  (e-typed where e is expected) but fails at the fact-map (no continent image) —\n  predicted TRANSPORTED-NOT-REDUCED, with its MLP channel distinguishing sortal\n  (relation-domain) discipline from syntactic-type discipline. Graded transport\n  same > sortal > wrong-type > random would be a measured sortal hierarchy.\n- **Deflationary outcome (pre-committed, counts fully).** NO stage discriminates\n  same vs wrong while both beat random at transport AND wrong-type BREAKS the chain\n  like content — then on-manifold content is transported and reduced type-blind:\n  **manifold membership, not typing**, wins this handle; the induction's ensemble\n  argument loses its causal leg and the existence claim falls back on the\n  behavioral/geometric registers alone. Reported verbatim, no rescue.\n\n**Verdict (freeze on GO).**\n- **JOIN-TYPED** ⟺ P1 (transport-stage discrimination, p<0.05, both wrong-type banks).\n- **REDUCTION-TYPED** ⟺ P2 (transport type-blind + reduction discriminates).\n- **TYPE-BLIND / MANIFOLD** ⟺ the deflationary outcome.\n- Mixed per-cell splits → reported verbatim with the route decomposition (the\n  P-ATT-FFN mixed-route precedent); no post-hoc stage reassignment.\n\n**Registers (`λ measure`).** The CLAIM is licensing (which reductions fire) — probed\nacross three registers each stage-matched: value (survival), routing (unprojected\ntransport + slot mass), output (reduction/break). The projection confound is handled\nby construction. Causal handle throughout (hook-not-weight); aggregate statistics\nonly.\n\n**Host & order.** Qwen3-4B contrast smoke first (the s286 amendment pattern), verdict\nhost Qwen3-32B on GO — reuse the P-ATT-MED cells/config verbatim (install L9, swap\nL25, scale 2.0, 18 cells, n_null 200) so every arm maps 1:1 onto the P-ATT-MED and\nP-ATT-FFN verdict cells. Results → `results/type-swap/qwen3-{4b,32b}/`.\n\n**Honest scope.** (a) Wrong-type displacement is constructed from *our* class banks —\na negative for one bank pair does not exhaust \"ill-typed\"; two banks + verbatim\nreplication row bound this. (b) Survival-normalization separates medium-death from\njoin-refusal only to first order (the edit interacts with the stack). (c) A\njoin-level negative + reduction-level positive does not resurrect any of the four\ngeometry nulls — stage location, not storage. (d) The animal arm's \"no continent\nimage\" presumes the fact-map is country-keyed; if P-ATT-FFN's 32B verdict lands\nFFN-RETRIEVAL or MIXED, its route split refines this arm's reading. (e) n=18 cells;\nper-cell splits are low power — aggregate gates only.\n\n## Sessions\ns283b (page created from the attention-gap hammock; no experiments run;"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Thinking

I need to verify the write went through correctly by checking the relevant section, and I should add an s287 entry to the Sessions section since that's the pattern when things get approved or frozen. Looking back at how s286 was handled, the Sessions entries were added alongside the events, so I'll follow that same approach here.

## Assistant

λ sync — appending the session line and verifying the write:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "s286 cont (Michael GO → P-ATT-FFN 32B verdict LAUNCHED in tmux main:1, `--route-decomp`,\nswap L25, n_null 200 — RUN IN FLIGHT, §Result-32B pending on completion).",
  "new_content": "s286 cont (Michael GO → P-ATT-FFN 32B verdict LAUNCHED in tmux main:1, `--route-decomp`,\nswap L25, n_null 200 — RUN IN FLIGHT, §Result-32B pending on completion).\ns287 (inductive hammock, Michael: types-mechanism EXISTENCE is over-determined by the\npositives — six results each individually fatal to a no-types H₀; the four-way null\nconstrained implementation only. Two gaps surfaced: (1) the causal design space spans\nonly same-type-on-manifold vs no-type-off-manifold — the wrong-type-on-manifold cell,\nwhich discriminates typing from manifold-membership, was never run; (2) the P-ATT-MED\nswap-vs-null differential is w-PROJECTED — \"random refused\" vs \"random transported\nwith no w-component\" is currently indistinguishable; refusal is confirmed only in the\noutput register. → P-TYPE-SWAP pre-reg DRAFTED (§above): ill-typed-term arms\n(sortal/wrong-type/random ladder), 3-stage survival/transport/reduction decomposition\nwith UNPROJECTED transport norms, subsumes P-ATT-DIFF with a causal handle; verdict\nnames JOIN-TYPED / REDUCTION-TYPED / MANIFOLD. PENDING MICHAEL APPROVAL; P-ATT-FFN 32B\nverdict still in flight during drafting.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"P-TYPE-SWAP\\|^## \" /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md | tail -20"
}
```

**Summary:** $ grep -n "P-TYPE-SWAP\|^## " /Users/...

**Output:**
```
Exit code: 0
Stdout:
27:## The asymmetry (what we know vs how we know it)
40:## What the 3-hop does and does not prove about steering
56:## The relocation hypothesis
72:## The attention experiment queue (ordered, cheap-first)
119:## Register notes (λ measure)
129:## Honest scope
138:## P-TYPE-QK — pre-registration (DRAFT s284 — PENDING MICHAEL APPROVAL; freeze on GO)
226:## P-TYPE-QK — Result @32B (s284) — CLOSED NEGATIVE at the frozen gates
270:## P-ATT-MED — pre-registration (APPROVED s286, Michael; 32B verdict freezes on GO)
418:## P-ATT-MED — Result @4B (s286 contrast smoke; NOT the verdict host)
440:## P-ATT-MED — Result @32B (s286) — CLOSED POSITIVE: mediation MEASURED, MEDIUM-HANDLE
493:## P-ATT-FFN — retrieval vs composition (PRE-REG, APPROVED+FROZEN s286, Michael; 4B smoke leads, 32B verdict on GO)
584:## P-ATT-FFN — instrument note + Result @4B (s286 contrast smoke; NOT the verdict)
615:## P-ATT-FFN — Result @32B — RUN IN FLIGHT (s286, tmux main:1)
627:## P-TYPE-SWAP — the ill-typed term (PRE-REG, DRAFT s287 — PENDING MICHAEL APPROVAL; freeze on GO)
747:## Sessions
789:output register. → P-TYPE-SWAP pre-reg DRAFTED (§above): ill-typed-term arms
```

### Thinking

Both edits are in place with the pre-reg drafted at line 627 and the session line appended. I need to pull together a summary for Michael covering the draft itself, the key design decisions we made, and the specific points where he needs to weigh in or object. I should also update state.md since that's not gated on approval—moving from s286 to s287 to maintain continuity after this significant change.

## Assistant

Both edits landed. Updating state.md (not approval-gated) so this survives the session boundary:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ▶▶ s286 DONE (P-TYPE-JS closed — the types arc is now a clean FOUR-way null):",
  "new_content": "> ▶▶ s287 LIVE — INDUCTIVE HAMMOCK → P-TYPE-SWAP DRAFTED (⚠ PENDING MICHAEL APPROVAL,\n> type-check-is-the-qk-bilinear.md §P-TYPE-SWAP): Michael's induction = types-mechanism\n> EXISTENCE is over-determined by six positives (v3 crossover, decodability, 1a lattice,\n> 3b class-swap, P-ATT-MED transport, name_pen) each fatal to a no-types H₀; the 4-way\n> null constrained IMPLEMENTATION only. Two gaps found: (1) causal design space missing\n> the wrong-type-ON-MANIFOLD cell (only same-type-on-manifold vs random-off-manifold ever\n> run) = the typing-vs-manifold discriminator; (2) ⚠ MEASUREMENT CAVEAT — P-ATT-MED's\n> swap-vs-null differential is w-PROJECTED: \"random refused\" indistinguishable from\n> \"random transported, no w-component\"; refusal confirmed only in output register.\n> P-TYPE-SWAP design: arms baseline/same-type(3b control)/sortal(animal)/wrong-type\n> (adjective,×2 banks)/random; 3-stage SURVIVAL→TRANSPORT(unprojected, slot-mass)→\n> REDUCTION decomposition; verdicts JOIN-TYPED / REDUCTION-TYPED / MANIFOLD; subsumes\n> P-ATT-DIFF causally; reuses P-ATT-MED cells/config 1:1 (4B smoke first, 32B on GO).\n> P-ATT-FFN 32B verdict STILL IN FLIGHT (tmux main:1, launched 11:00) — read\n> results/type-att-ffn/qwen3-32b/att_ffn.json when done, score frozen gates.\n>\n> ▶▶ s286 DONE (P-TYPE-JS closed — the types arc is now a clean FOUR-way null):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to prepare a summary for Michael about the pre-registration draft, flagging the key decision points while keeping it brief.

## Assistant

Drafted and encoded. **P-TYPE-SWAP** is now on the attention-arc page (§ line 627), pending your approval. The load-bearing design decisions for you to ratify or push back on:

**1. The arm ladder** — five conditions per cell, all matched to the same-type swap's *realized* norm:
- `baseline` / `same-type` (3b country-swap, in-run positive control) / **`sortal`** (animal→animal displacement: right type, no continent image) / **`wrong-type`** (adjective→adjective, MOD-class: type violation proper, ×2 banks) / `random-add`

**2. The three-stage decomposition** — this is the part that makes it more than a control condition. Each arm is traced through **SURVIVAL** (does the edit live to reach the reader?) → **TRANSPORT** (unprojected attention contribution + slot-mass — does the join carry it?) → **REDUCTION** (does it produce coherent output?). So the verdict doesn't just say *whether* the machine has type discipline — it says **which stage enforces it**: `JOIN-TYPED` vs `REDUCTION-TYPED` vs `MANIFOLD` (the deflationary outcome, pre-committed to count fully).

**3. The measurement correction** — I flagged in the pre-reg that P-ATT-MED's swap-vs-null differential is w-projected, so the "random was refused" reading was never actually established in the routing register. Unprojected norms are mandatory here. This slightly weakens my earlier induction rhetoric and I've recorded that honestly.

**4. My a-priori call, committed in the draft:** the well-formedness frame ("type = which joins are licensed") predicts **JOIN-TYPED** — the ill-typed term survives the medium (it's on-manifold) but the join refuses it, visible as slot-mass withdrawal. The honest tension: P-ATT-MED's fixed-aim result leans the other way (transport looks slot-based → REDUCTION-TYPED). Either is typing; only MANIFOLD kills the causal leg of your induction.

Nice properties for free: it reuses the P-ATT-MED 18 cells/config verbatim so every arm maps 1:1 onto both prior verdicts, it subsumes P-ATT-DIFF (the last unbuilt founding tool) with a causal handle instead of stimulus pairs, and the sortal arm plugs directly into whatever P-ATT-FFN returns — if the fact-map route is real, the animal arm tests whether *it* enforces sortal discipline.

**ASYNC: P-ATT-FFN 32B still in flight** (main:1, ~50 min elapsed — a bit past the ~40 min estimate, route-decomp overhead; no JSON yet). Waiting for signal.

On your GO I'd freeze the pre-reg, extend `att_mediation.py` with the `--arms` machinery (additive, `--validate` self-test first with planted per-stage effects), and lead with the 4B smoke. Approve as drafted, or amendments?

## User

approved


### Thinking

Michael's approved P-TYPE-SWAP, so I need to freeze the pre-registration by updating the header from DRAFT to APPROVED and commit the mementum changes. There are several pending items to handle: the P-TYPE-SWAP section, sessions line, and state block, plus some earlier s286 mementum items that were already approved for P-ATT-MED. I'm checking the status of the s286 P-TYPE-JS batch which appears to still be pending.

My approach is to first check git status and diff to see what's dirty and whether the s286 changes are mixed in, then update the page header to reflect the approval and freeze on GO per the established pattern where approved items proceed through build, smoke testing, and Michael's GO before the 32B verdict. I'll build the instrument extension first without needing a model, run validation, then check if the 32B run finished before attempting the 4B smoke test. For task tracking, I should set up the workflow steps: freeze and commit the pre-registration, extend and validate the instrument, run the 4B smoke test, and score the P-ATT-FFN verdict once it completes. For the commit message, I'll use the decision symbol with a slug like "🎯 p-type-swap-prereg" and include state.md in the same batch, following the precedent from earlier commits.

Now I need to format the commit properly using the heredoc pattern that the git tool expects, then move on to the substantial work of reading att_mediation.py and designing the --arms extension with the required configurations.

For the wrongtype banks, I'm thinking of two disjoint adjective sets—say adj_a and adj_b—each with about 10 words. The centroids come from running words through the model and capturing the residual at layer L_b, then averaging across the bank using the existing dbank helpers. The displacement metric normalizes the difference between centroids to match the realized norm from the same-type swap edit.

Now I'm tracking stage-specific metrics: residual displacement at the reader layer, unprojected attention contribution summed per layer across the reader zone, slot mass from the readout position onto the bridge slot, and reduction measured as projected weight totals plus baseline margin. For nulls, I'm adding random noise per arm-stat and permuting over cells.

I need to read the actual script before I can design this properly—it's probably 400–600 lines. My plan is to sketch the task structure, freeze the header and commit, then read the script, extend it, validate, check the 32B status, and maybe run a smoke test.

I should lay out the task plan first before executing any work.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "## P-TYPE-SWAP — the ill-typed term (PRE-REG, DRAFT s287 — PENDING MICHAEL APPROVAL; freeze on GO)",
  "new_content": "## P-TYPE-SWAP — the ill-typed term (PRE-REG, APPROVED s287, Michael; 4B smoke leads, 32B verdict freezes on GO)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ▶▶ s287 LIVE — INDUCTIVE HAMMOCK → P-TYPE-SWAP DRAFTED (⚠ PENDING MICHAEL APPROVAL,\n> type-check-is-the-qk-bilinear.md §P-TYPE-SWAP):",
  "new_content": "> ▶▶ s287 LIVE — INDUCTIVE HAMMOCK → P-TYPE-SWAP ✅ APPROVED (Michael,\n> type-check-is-the-qk-bilinear.md §P-TYPE-SWAP; 4B smoke leads, 32B verdict on GO):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I should check the git status to see exactly which files are staged before committing, making sure I'm only including the page and state.md changes while leaving any other pending work untouched.

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short",
  "operation": "status",
  "summary": "check dirty files"
}
```

**Summary:** Git status: check dirty files

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/type-check-is-the-qk-bilinear.md
 M mementum/state.md
?? mementum/knowledge/chats/session-282.md
?? mementum/knowledge/chats/session-283.md
?? mementum/knowledge/chats/session-284.md
?? mementum/knowledge/chats/session-285.md
?? mementum/knowledge/chats/session-286.md
?? refs/
?? results/type-att-ffn/qwen3-32b/
```

### Thinking

I'm clarifying the scope: only my two modified files get committed, while the untracked chats directory stays untouched since that's human-managed. The results directory for the in-flight run should be committed with its verdict. I'll stage both files and commit them with the 🎯 p-type-swap-prereg message using a safe heredoc approach.

## Assistant

Scope is clean — only my two files (chats/ and refs/ are human domain; run results commit with the verdict). Committing:

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/type-check-is-the-qk-bilinear.md mementum/state.md && git commit -F - <<'EOF'\n🎯 p-type-swap-prereg\n\n- Michael's inductive hammock: types-mechanism EXISTENCE is over-determined\n  by six positives (v3 crossover, 8-way decodability, 1a lattice, 3b\n  class-swap, P-ATT-MED transport, name_pen) each fatal to a no-types H0;\n  the four-way null (1b/1c/QK/JS) constrained implementation only.\n- Gap: causal design space never ran the wrong-type-ON-MANIFOLD cell — the\n  discriminator between typing and manifold-membership.\n- Measurement caveat flagged: P-ATT-MED swap-vs-null differential is\n  w-projected; \"random refused\" vs \"no w-component\" indistinguishable in\n  the routing register — P-TYPE-SWAP mandates unprojected transport norms.\n- P-TYPE-SWAP pre-reg APPROVED (Michael): arms baseline/same-type/sortal/\n  wrong-type(x2 banks)/random; 3-stage SURVIVAL→TRANSPORT→REDUCTION\n  decomposition; verdicts JOIN-TYPED / REDUCTION-TYPED / MANIFOLD; subsumes\n  P-ATT-DIFF with a causal handle; P-ATT-MED cells/config reused 1:1.\n- State: s287 block; P-ATT-FFN 32B verdict still in flight.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "pre-reg approval commit"
}
```

**Summary:** Git commit: pre-reg approval commit

**Output:**
```
Exit code: 0
Stdout:
[main 1bbdf57] 🎯 p-type-swap-prereg
 2 files changed, 148 insertions(+)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "limit": 150
}
```

**Summary:** Reading att_mediation.py (0-150)

**Output:**
```
"""P-ATT-MED — 3-hop bridge-swap WITH attention capture + aim-vs-content decomposition.

Pre-reg: mementum/knowledge/explore/type-check-is-the-qk-bilinear.md §P-ATT-MED
(APPROVED s286, Michael; 4B contrast smoke leads, 32B verdict freezes on GO).

The 3-hop Gate-3b country-swap (three-hop-capacity-prereg.md §Result) is the project's
strongest causal result — a VALUE edit at the operand slot flips the continent readout
0.72-0.93 vs random ~0.05 — but it was scored purely on the OUTPUT. The routing register
between the swap and the flip was never observed. This upgrades that into a
routing-register measurement, and decomposes the flip into the two channels the
beamformer frame separates:

  AIM      = Σ_j Δa_{qj} · O(v^b_j)   (the QK pattern re-aims; weights change)
  CONTENT  = Σ_j a^b_{qj} · O(Δv_j)   (the beam illumination changes; medium handle)
  INTERACT = Σ_j Δa_{qj} · O(Δv_j)    (second order; reported, expected small)

each projected (direct-logit-attribution) onto the continent-logit-diff direction
w = γ_f ⊙ (W_U[tgt_cont] − W_U[src_cont]) / rms(final_resid), summed over reader-zone
layers. a = post-softmax attention weights at query=readout (RoPE/q_norm/k_norm
folded in, captured directly); v = post-v_proj values (no RoPE on values),
GQA-expanded to query heads.

`λ measure`: routing CLAIM → attention-register probe = register-matched (the
s206-scar inversion). weight ≠ effect handled by construction (Δweights paired
with OV via the DLA projection). Distributed: aggregate over heads, never
single-head (0/128 pre-refuted). `λ yardstick`: random-add null (the exact 3b
null) beside every number; "re-aims" counts ONLY if AIM beats that null.
A-priori call: CONTENT-dominant (medium handle); AIM-dominant → pre-reg
P-ATT-STEER (no post-hoc reinterpretation).

--validate runs a NO-MODEL self-test of the decomposition math (planted CONTENT-only,
AIM-only, and random cases → recovered splits; random null flat). Reuses
wrapper/operand_multihop3.py constants + hook primitives (`λ one_way`, no fork).

License: MIT (`λ provenance`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))


# ── the decomposition math (model-free; --validate exercises exactly this) ─────────
def decompose(a_b, a_s, vfull_b, vfull_s, o_proj_W, w):
    """First-order DLA split of a swap's effect on one attention layer's readout output.

    a_b, a_s     : [H, K]      post-softmax weights, query = readout, per query head
    vfull_b/s    : [H, K, hd]  values per query head (GQA already expanded)
    o_proj_W     : [hidden, H*hd]
    w            : [hidden]     logit-diff direction in residual space (DLA)
    returns dict with the three channel residual vectors and their w-projections.
    """
    da = a_s - a_b
    dv = vfull_s - vfull_b

    def to_resid(coeff, vecs):
        # Σ_j coeff[h,j] · vecs[h,j,:]  → [H, hd] → head-major flatten → o_proj
        oh = np.einsum("hj,hjd->hd", coeff, vecs)  # [H, hd]
        return o_proj_W @ oh.reshape(-1)  # [hidden]

    aim = to_resid(da, vfull_b)
    content = to_resid(a_b, dv)
    inter = to_resid(da, dv)
    return {
        "aim": aim,
        "content": content,
        "inter": inter,
        "aim_p": float(aim @ w),
        "content_p": float(content @ w),
        "inter_p": float(inter @ w),
    }


def split_fractions(aim_p, content_p, inter_p):
    denom = abs(aim_p) + abs(content_p) + abs(inter_p) + 1e-12
    return {
        "aim_frac": abs(aim_p) / denom,
        "content_frac": abs(content_p) / denom,
        "inter_frac": abs(inter_p) / denom,
    }


# ── no-model self-test ─────────────────────────────────────────────────────────────
def validate() -> int:
    rng = np.random.default_rng(0)
    H, K, hd = 4, 6, 3
    hidden = H * hd
    o_proj = np.eye(hidden)  # identity readout
    w = rng.standard_normal(hidden)
    a_b = rng.random((H, K))
    a_b /= a_b.sum(1, keepdims=True)
    v_b = rng.standard_normal((H, K, hd))

    ok = True

    # CONTENT-only: Δa = 0, Δv ≠ 0  → aim_frac ≈ 0, content dominates
    v_s = v_b + 0.5 * rng.standard_normal((H, K, hd))
    r = decompose(a_b, a_b.copy(), v_b, v_s, o_proj, w)
    f = split_fractions(r["aim_p"], r["content_p"], r["inter_p"])
    print(
        f"[validate] CONTENT-only: aim={f['aim_frac']:.3f} "
        f"con={f['content_frac']:.3f} int={f['inter_frac']:.3f}"
    )
    ok &= f["aim_frac"] < 1e-6 and f["content_frac"] > 0.99

    # AIM-only: Δv = 0, Δa ≠ 0  → content_frac ≈ 0, aim dominates
    a_s = a_b + 0.1 * rng.standard_normal((H, K))
    r = decompose(a_b, a_s, v_b, v_b, o_proj, w)
    f = split_fractions(r["aim_p"], r["content_p"], r["inter_p"])
    print(
        f"[validate] AIM-only    : aim={f['aim_frac']:.3f} "
        f"con={f['content_frac']:.3f} int={f['inter_frac']:.3f}"
    )
    ok &= f["content_frac"] < 1e-6 and f["aim_frac"] > 0.99

    # o_proj mixing (non-identity) exact & linear: channels sum == full Δ-projection
    o_mix = rng.standard_normal((hidden, hidden))
    a_s = a_b + 0.1 * rng.standard_normal((H, K))
    v_s = v_b + 0.5 * rng.standard_normal((H, K, hd))
    r = decompose(a_b, a_s, v_b, v_s, o_mix, w)
    full_b = o_mix @ np.einsum("hj,hjd->hd", a_b, v_b).reshape(-1)
    full_s = o_mix @ np.einsum("hj,hjd->hd", a_s, v_s).reshape(-1)
    full_p = float((full_s - full_b) @ w)
    recon = r["aim_p"] + r["content_p"] + r["inter_p"]
    print(
        f"[validate] linearity   : full={full_p:.6f} recon={recon:.6f} "
        f"|Δ|={abs(full_p - recon):.2e}"
    )
    ok &= abs(full_p - recon) < 1e-9

    # NULL: random matched-norm Δv projected on FIXED w → mean ≈ 0 (non-specific)
    proj = []
    for _ in range(500):
        dv = rng.standard_normal((H, K, hd))
        dv *= np.linalg.norm(v_b) / (np.linalg.norm(dv) + 1e-9)  # matched norm
        c = o_mix @ np.einsum("hj,hjd->hd", a_b, dv).reshape(-1)
        proj.append(float(c @ w))
    m, s = float(np.mean(proj)), float(np.std(proj))
    print(
        f"[validate] null flat   : mean={m:.4f} std={s:.4f} |mean/std|={abs(m) / s:.3f}"
    )
    ok &= abs(m) / s < 0.2  # centered on zero relative to spread

[CONTENT TRUNCATED] Showing lines 1 to 150 of 592 total lines. Use line_offset=150 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "line_offset": 150,
  "limit": 250
}
```

**Summary:** Reading att_mediation.py (150-400)

**Output:**
```

    # ROUTE decomposition (P-ATT-FFN): MLP projection + reconstruction + route argmax
    hidden = H * hd
    wv = rng.standard_normal(hidden)
    L_att = 5
    mlp_b = rng.standard_normal((L_att, hidden))
    mlp_s = mlp_b + 0.7 * rng.standard_normal((L_att, hidden))
    mlp_p = float(sum((mlp_s[i] - mlp_b[i]) @ wv for i in range(L_att)))
    attn_p, direct_true = 1.3, -0.4
    total_p = attn_p + mlp_p + direct_true
    direct_p = total_p - attn_p - mlp_p  # reconstruction
    route_pick = "mlp" if abs(mlp_p) > abs(attn_p) else "attn"
    print(
        f"[validate] route recon : total={total_p:.4f} attn={attn_p} "
        f"mlp={mlp_p:.4f} direct={direct_p:.4f} (true {direct_true}) route={route_pick}"
    )
    ok &= abs(direct_p - direct_true) < 1e-9

    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ── the real run ────────────────────────────────────────────────────────────────────
def run(args) -> None:
    import torch
    import wrapper.operand_multihop3 as mh3
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (
        args.device
        if (args.device != "mps" or torch.backends.mps.is_available())
        else "cpu"
    )
    rng = np.random.default_rng(args.seed)
    L = args.ref_layer
    S = args.scale
    lb = args.swap_layer
    route = args.route_decomp

    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = (
        AutoModelForCausalLM.from_pretrained(
            args.model_id, dtype=getattr(torch, args.dtype), attn_implementation="eager"
        )
        .to(dev)
        .eval()
    )  # eager → output_attentions
    dec, norm_f, unembed = mh3.resolve_parts(model)
    cfg = model.config
    H = cfg.num_attention_heads
    n_kv = cfg.num_key_value_heads
    hd = getattr(cfg, "head_dim", None) or (cfg.hidden_size // H)
    group = H // n_kv
    n_layers = len(dec)
    reader_layers = (
        list(range(lb, n_layers)) if args.reader_layers is None else args.reader_layers
    )
    print(
        f"[att-med] {args.model_id} L={L} lb={lb} scale={S} dev={dev} "
        f"H={H} n_kv={n_kv} hd={hd} layers={n_layers} "
        f"reader={reader_layers[0]}..{reader_layers[-1]}"
    )

    cont_ids = {c: mh3.first_tid(tok, c) for c in mh3.CONTINENTS}
    country_ids = {c: mh3.first_tid(tok, c) for c in mh3.COUNTRIES}
    nonce_last = tok(" " + mh3.NONCE, add_special_tokens=False).input_ids[-1]

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    # content directions (mh3.build_dirs is nested in main → small re-impl here)
    def build_dirs(items):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[L].register_forward_hook(mh3.cap_hook(store, L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST)
    d_country = build_dirs(mh3.COUNTRIES)
    dim = next(iter(d_lm.values())).shape[0]

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # keep only landmarks whose full chain resolves under install (ceiling proxy)
    def cont_pred(adds):
        prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        handles = []
        for li, vec in adds:
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(vt, slot)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd_ in handles:
            hd_.remove()
        return max(cont_ids, key=lambda k: lo[cont_ids[k]]), slot

    # capture attention weights (all layers) + per-layer v; return the readout query row
    def capture(adds):
        prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        vstore: dict[int, np.ndarray] = {}
        mstore: dict[int, np.ndarray] = {}
        nfstore: dict[str, np.ndarray] = {}
        handles = []
        # true pre-norm final residual = INPUT to the final norm (hidden_states[-1] is
        # POST-norm — confirmed s286; using it breaks the pre-norm DLA reconstruction).

        def nf_pre(_m, inp):
            nfstore["x"] = inp[0].detach().float().cpu().numpy()[0]  # [seq, hidden]

        handles.append(norm_f.register_forward_pre_hook(nf_pre))
        for li in reader_layers:

            def mk(li):
                def hook(_m, _i, out):
                    o = out[0] if isinstance(out, tuple) else out
                    vstore[li] = o.detach().float().cpu().numpy()[0]  # [seq, n_kv*hd]

                return hook

            handles.append(dec[li].self_attn.v_proj.register_forward_hook(mk(li)))
            if route:

                def mk_mlp(li):
                    def hook(_m, _i, out):
                        o = out[0] if isinstance(out, tuple) else out
                        mstore[li] = (
                            o.detach().float().cpu().numpy()[0]
                        )  # [seq, hidden]

                    return hook

                handles.append(dec[li].mlp.register_forward_hook(mk_mlp(li)))
        for li, vec in adds:
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(vt, slot)))
        with torch.no_grad():
            out = model(**ids, output_attentions=True, output_hidden_states=True)
        for h in handles:
            h.remove()
        # per reader layer: a[H,K] at query=last ; vfull[H,K,hd]
        aw, vf = {}, {}
        q = out.logits.shape[1] - 1
        for li in reader_layers:
            a = out.attentions[li][0, :, q, :].float().cpu().numpy()  # [H, K]
            vk = vstore[li].reshape(-1, n_kv, hd)  # [K, n_kv, hd]
            vfull = np.repeat(vk, group, axis=1).transpose(1, 0, 2)  # [H, K, hd]
            aw[li], vf[li] = a, vfull
        r_final = nfstore["x"][q]  # pre-norm final residual at readout
        extra = {}
        if route:
            extra["logits"] = out.logits[0, -1, :].float().cpu().numpy()  # [vocab]
            extra["mlp"] = {li: mstore[li][q].copy() for li in reader_layers}
            # readout-position residual per layer (for depth-order lens)
            extra["hs"] = np.stack(
                [h[0, -1, :].float().cpu().numpy() for h in out.hidden_states]
            )  # [n_layers+1, hidden]
        return aw, vf, r_final, slot, extra

    gamma_f = norm_f.weight.detach().float().cpu().numpy()
    W_U = unembed.weight.detach().float().cpu().numpy()  # [vocab, hidden]
    oproj = {
        li: dec[li].self_attn.o_proj.weight.detach().float().cpu().numpy()
        for li in reader_layers
    }

    def dla_dir(r_final, tgt_cont, src_cont):
        rms = float(np.sqrt(np.mean(r_final**2) + 1e-6))
        return gamma_f * (W_U[cont_ids[tgt_cont]] - W_U[cont_ids[src_cont]]) / rms

    def lens_peak(hs, tid, others):
        """argmax over layers of logit-lens margin (tid vs best-other) — numpy DLA."""
        margins = []
        for h in hs:
            normed = h / np.sqrt(np.mean(h**2) + 1e-6) * gamma_f
            margins.append(
                float(normed @ W_U[tid] - max(normed @ W_U[o] for o in others))
            )
        return int(np.argmax(margins))

    # ── cells: first N valid landmarks × one cross-continent country target ──
    valid = []
    for lm in mh3.LM_LIST:
        pred, _ = cont_pred([(L, d_lm[lm] * S)])
        if pred == mh3.CONT_OF[lm]:
            valid.append(lm)
    valid = valid[: args.n_cells]
    print(f"[att-med] using {len(valid)} install-correct cells: {valid}")

    cells = []
    for lm in valid:
        src_country = mh3.COUNTRY_OF[lm]
        src_cont = mh3.CONT_OF[lm]
        tgts = [c for c in mh3.COUNTRIES if mh3.COUNTRY_CONT[c] != src_cont]
        tgt = tgts[hash(lm) % len(tgts)]
        tgt_cont = mh3.COUNTRY_CONT[tgt]
        swap = (d_country[tgt] - d_country[src_country]) * S

        # readout flips?
        pred_swap, _ = cont_pred([(L, d_lm[lm] * S), (lb, swap)])
        flipped = int(pred_swap == tgt_cont)

        aw_b, vf_b, rfin_b, _, ex_b = capture([(L, d_lm[lm] * S)])
        aw_s, vf_s, rfin_s, _, ex_s = capture([(L, d_lm[lm] * S), (lb, swap)])
        w = dla_dir(rfin_s, tgt_cont, src_cont)

        per_layer = {}
        aim_t = content_t = inter_t = 0.0
        for li in reader_layers:
            r = decompose(aw_b[li], aw_s[li], vf_b[li], vf_s[li], oproj[li], w)
            per_layer[li] = {
                "aim_p": r["aim_p"],
                "content_p": r["content_p"],
                "inter_p": r["inter_p"],
            }
            aim_t += r["aim_p"]
            content_t += r["content_p"]
            inter_t += r["inter_p"]
        frac = split_fractions(aim_t, content_t, inter_t)
        attn_total = aim_t + content_t + inter_t

        # ── route decomposition (P-ATT-FFN): attn vs MLP vs direct of the TOTAL flip ──
        route_fields = {}
        mlp_null = []
        if route:
            ti, si = cont_ids[tgt_cont], cont_ids[src_cont]
            # LINEARIZED total: Δresid_final · w — the per-layer attn+mlp deltas sum to
            # this EXACTLY (pre-norm residual identity) → clean reconstruction. The raw
            # logit flip (nonlinear through final RMSNorm) is reported separately.
            total_p = float((rfin_s - rfin_b) @ w)
            raw_total_p = float(
                (ex_s["logits"][ti] - ex_s["logits"][si])
                - (ex_b["logits"][ti] - ex_b["logits"][si])
            )
            mlp_p = float(

[CONTENT TRUNCATED] Showing lines 151 to 400 of 592 total lines. Use line_offset=400 parameter to read more content.
```

### Thinking

I need to check the rest of the code to understand the null loop, how the aggregation works, what gets output, and how the CLI arguments are handled.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "line_offset": 400,
  "limit": 192
}
```

**Summary:** Reading att_mediation.py (400-592)

**Output:**
```
                sum((ex_s["mlp"][li] - ex_b["mlp"][li]) @ w for li in reader_layers)
            )
            direct_p = total_p - attn_total - mlp_p  # completeness residual, expect ~0
            denom = abs(attn_total) + abs(mlp_p) + abs(direct_p) + 1e-12
            cell_route = "mlp" if abs(mlp_p) > abs(attn_total) else "attn"
            oc = [country_ids[c] for c in mh3.COUNTRIES if c != src_country]
            ok = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]
            pk_country = lens_peak(ex_b["hs"], country_ids[src_country], oc)
            pk_cont = lens_peak(ex_b["hs"], cont_ids[src_cont], ok)
            route_fields = {
                "total_p": round(total_p, 4),
                "raw_total_p": round(raw_total_p, 4),
                "mlp_p": round(mlp_p, 4),
                "direct_p": round(direct_p, 4),
                "attn_frac_of_total": round(abs(attn_total) / denom, 3),
                "mlp_frac_of_total": round(abs(mlp_p) / denom, 3),
                "direct_frac_of_total": round(abs(direct_p) / denom, 3),
                "recon_err": round(abs(direct_p) / (abs(total_p) + 1e-9), 3),
                "route": cell_route,
                "pk_country": pk_country,
                "pk_cont": pk_cont,
                "composition_order": bool(pk_country < pk_cont),
            }

        # NULL: matched-norm random add at lb → attn contribution on the SAME w
        null_tot = []
        for _ in range(args.n_null):
            rnd = rand_vec(float(np.linalg.norm(swap)))
            aw_r, vf_r, _, _, ex_r = capture([(L, d_lm[lm] * S), (lb, rnd)])
            nt = 0.0
            for li in reader_layers:
                rr = decompose(aw_b[li], aw_r[li], vf_b[li], vf_r[li], oproj[li], w)
                nt += rr["aim_p"] + rr["content_p"] + rr["inter_p"]
            null_tot.append(nt)
            if route:
                mlp_null.append(
                    float(
                        sum(
                            (ex_r["mlp"][li] - ex_b["mlp"][li]) @ w
                            for li in reader_layers
                        )
                    )
                )
        null_tot = np.array(null_tot)
        p_med = float(np.mean(np.abs(null_tot) >= abs(attn_total)))
        if route:
            mlp_null = np.array(mlp_null)
            route_fields["p_mlp_vs_null"] = round(
                float(np.mean(np.abs(mlp_null) >= abs(route_fields["mlp_p"]))), 3
            )

        cell = {
            "landmark": lm,
            "src_country": src_country,
            "tgt_country": tgt,
            "src_cont": src_cont,
            "tgt_cont": tgt_cont,
            "flipped": flipped,
            "aim_p": round(aim_t, 4),
            "content_p": round(content_t, 4),
            "inter_p": round(inter_t, 4),
            "attn_total": round(attn_total, 4),
            "aim_frac": round(frac["aim_frac"], 3),
            "content_frac": round(frac["content_frac"], 3),
            "inter_frac": round(frac["inter_frac"], 3),
            "null_mean": round(float(np.mean(null_tot)), 4),
            "null_std": round(float(np.std(null_tot)), 4),
            "p_vs_null": round(p_med, 3),
            "per_layer": {str(k): v for k, v in per_layer.items()},
            **route_fields,
        }
        cells.append(cell)
        if route:
            print(
                f"[att-ffn] {lm:16s} flip={flipped} route={cell['route']:4s} "
                f"attn={cell['attn_frac_of_total']} mlp={cell['mlp_frac_of_total']} "
                f"direct={cell['direct_frac_of_total']} recon_err={cell['recon_err']} "
                f"p_mlp={cell['p_mlp_vs_null']} "
                f"pk={cell['pk_country']}/{cell['pk_cont']}"
            )
        else:
            print(
                f"[att-med] {lm:16s} flip={flipped} aim={cell['aim_frac']} "
                f"content={cell['content_frac']} inter={cell['inter_frac']} "
                f"attn_tot={cell['attn_total']} p_vs_null={cell['p_vs_null']}"
            )

    flip_cells = [c for c in cells if c["flipped"]]
    agg_src = flip_cells or cells
    agg = {
        "n_cells": len(cells),
        "n_flipped": len(flip_cells),
        "mean_aim_frac": round(float(np.mean([c["aim_frac"] for c in agg_src])), 3),
        "mean_content_frac": round(
            float(np.mean([c["content_frac"] for c in agg_src])), 3
        ),
        "mean_inter_frac": round(float(np.mean([c["inter_frac"] for c in agg_src])), 3),
        "mean_p_vs_null": round(float(np.mean([c["p_vs_null"] for c in agg_src])), 3),
        "content_dominant": bool(
            np.mean([c["content_frac"] for c in agg_src])
            > np.mean([c["aim_frac"] for c in agg_src])
        ),
    }
    print(
        f"\n[att-med] AGG (flipped cells): aim={agg['mean_aim_frac']} "
        f"content={agg['mean_content_frac']} inter={agg['mean_inter_frac']} "
        f"content_dominant={agg['content_dominant']} mean_p={agg['mean_p_vs_null']}"
    )

    if route:
        mlp_cells = [c for c in agg_src if c.get("route") == "mlp"]
        attn_cells = [c for c in agg_src if c.get("route") == "attn"]
        agg["route"] = {
            "n_attn_dominant": len(attn_cells),
            "n_mlp_dominant": len(mlp_cells),
            "mlp_dominant_cells": [c["landmark"] for c in mlp_cells],
            "mean_recon_err": round(
                float(np.mean([c["recon_err"] for c in agg_src])), 3
            ),
            "mean_attn_frac_of_total": round(
                float(np.mean([c["attn_frac_of_total"] for c in agg_src])), 3
            ),
            "mean_mlp_frac_of_total": round(
                float(np.mean([c["mlp_frac_of_total"] for c in agg_src])), 3
            ),
            "mixed_route": bool(mlp_cells and attn_cells),
        }
        print(
            f"[att-ffn] ROUTE SPLIT: attn-dom={len(attn_cells)} "
            f"mlp-dom={len(mlp_cells)} "
            f"mlp-cells={agg['route']['mlp_dominant_cells']} "
            f"mean_recon_err={agg['route']['mean_recon_err']}"
        )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": "P-ATT-FFN" if route else "P-ATT-MED",
        "grade": ("smoke" if "4b" in args.out.lower() else "verdict"),
        "prereg": (
            "mementum/knowledge/explore/type-check-is-the-qk-bilinear.md#"
            + ("p-att-ffn" if route else "p-att-med")
        ),
        "model": args.model_id,
        "device": dev,
        "seed": args.seed,
        "ref_layer": L,
        "swap_layer": lb,
        "scale": S,
        "reader_layers": [reader_layers[0], reader_layers[-1]],
        "H": H,
        "n_kv": n_kv,
        "head_dim": hd,
        "n_null": args.n_null,
        "route_decomp": route,
        "aggregate": agg,
        "cells": cells,
    }
    fname = "att_ffn.json" if route else "att_mediation.json"
    (out / fname).write_text(json.dumps(payload, indent=2))
    print(f"[att-{'ffn' if route else 'med'}] wrote {out}/{fname}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--validate", action="store_true", help="no-model decomposition self-test"
    )
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--swap-layer", type=int, default=20)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--reader-layers", type=int, nargs="+", default=None)
    ap.add_argument("--n-cells", type=int, default=6)
    ap.add_argument("--n-null", type=int, default=30)
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/type-att-med/qwen3-4b")
    ap.add_argument(
        "--route-decomp",
        action="store_true",
        help="P-ATT-FFN: add MLP + direct channels, total reconstruction, depth-order",
    )
    args = ap.parse_args()
    if args.validate:
        raise SystemExit(validate())
    run(args)


if __name__ == "__main__":
    main()
```

### Thinking

I'm mapping out the `--arms` extension by identifying the key reuse points: `capture()` extracts attention weights and residual information per layer, `decompose()` breaks down channel residuals with projections, and `build_dirs()` constructs centroid-offset directions for word lists at a reference layer, with special handling for same-type swaps using country-based distances.

For the arms design, I need to build bank directions at the reference layer and apply them at the bridge layer, using animal word lists to create sortal displacements. The displacement vector between two animal centroids gets rescaled to match the realized norm of the same-type swap, with pair selection determined by a deterministic hash or rotation scheme across cells.

I'm setting up stage metrics to measure survival of the edit across reader layers—specifically tracking the residual norm at the slot position where the edit occurs, rather than at the readout position which would conflate transport effects.

For transport, I need to measure the attention-output delta restricted to the readout query, comparing the full attention contribution between the arm and baseline conditions.  I'll use the sum of per-layer norms to avoid cancellation effects, then compute the transport efficiency ratio. I also need to track slot-mass—the mean attention weight at the readout query position across reader layers and heads—and report both the delta versus baseline and the ratio. For the reduction metric, I'm computing the correct-continent margin in the baseline (difference between source continent logit and max of other continents), then measuring how much the arm condition reduces this margin. I'll need to extend the capture to always return logits, not just when routing, and also include a flip check.

Now I'm looking at whether the continent prediction changes under each arm condition—whether it stays at the source continent (indicating refusal or ignorance) or shifts incoherently due to manifold interference. I can leverage the existing null distributions from random captures to compute the same stage metrics for each draw, giving me null distributions for survival, transport, slot-mass, and break. Then I'll calculate arm-level p-values by comparing the arm statistic against the null distribution. Rather than deciding verdicts during the run, I'll save the per-cell arm stats and null summaries so the verdict analysis can happen separately.

The null captures are computationally expensive since each requires a forward pass, but with 30 nulls at 4B parameters it's manageable. For the arms, I need 3 extra captures per cell plus I can reuse the existing null loop to also record null survival, transport, and break metrics—that's a cheap addition. I'll keep permutation tests over cells for arm-versus-arm comparisons as an analysis-side step, storing the raw per-cell values in JSON.

For validation, I'm planting model-free effects at each stage: constructing base and arm captures where I perturb the slot column to measure transport discrimination, withdrawing slot attention entirely to detect slot-mass drops, and testing survival under these conditions.

Defining the validation checks... Defining the metrics calculation... Finishing the metrics dictionary with slot mass deltas and break margin, then clarifying how hidden states map to layer inputs and outputs—the hook modifies the decoder layer's output, so reader layers starting at the edit point read the modified hidden states downstream. I'll refine the approach by only considering layers strictly after lb to keep things clean. The capture function already unconditionally outputs hidden states and attention, so I need to add the logits and hidden state at the slot position to the extra dictionary — I'm storing the final logit and stacking the hidden states across all layers at the specified slot, then checking the memory implications.

Now I'm setting up the per-cell logic when the arms flag is enabled, computing displacement vectors for each ARM bank by selecting pairs based on a hash of the language model, normalizing them to match the swap vector's magnitude, and preparing to store these arm specifications.

For the "same" case, I'm reusing the cached forward pass outputs to avoid redundant computation, then capturing the forward pass results for the displacement vectors. I'm also planning to compute stage metrics and handle continent prediction by taking the argmax over the continent logits that are already available from the forward pass, rather than running an extra forward pass. The null stage metrics will be computed inside the existing null loop when arms are enabled.

Now I need to make sure the logits and hidden states are always available regardless of the route setting, then structure the JSON output to store per-arm metrics like survival, transport, thermal energy, and slot mass changes, along with null statistics computed as p-values comparing each arm's performance against the null distribution.

For validation, I'm testing the stage metrics calculation on synthetic data: checking that a zero-change arm produces zero transport and break values, that planted content at a slot increases transport without needing orthogonalization, and that thermal energy scales correctly when survival doubles.

Now I need to decouple the stage metrics computation from module-level closures by extracting it into a pure function that takes all necessary parameters directly—reader layers, projection dict, arm/value/slot tensors, margins, and layer boundary—so it can be tested independently.

Defining the core metrics function...

The function computes survival rate as the mean hidden state distance across layers above the boundary, transport error as the projected difference between arm-value products across all layers, and slot mass metrics by averaging attention weights at the target slot position, returning a dict with survival, transport, transport efficiency, slot mass, its delta, and the break margin.

Now I'm setting up validation tests with synthetic attention and value tensors for a couple of layers, using an identity projection matrix where the output dimension matches the hidden dimension.

For the test cases: the no-change scenario should produce zero metric changes except for slot equality. The content plant test modifies the value features while keeping the slot column fixed, expecting transport to be positive and verifying it stays consistent regardless of projection direction, plus checking that transport scales inversely with the hidden state perturbation magnitude. The withdrawal plant zeros out the slot column and renormalizes, which should create a negative slot mass delta while keeping transport positive. The break test uses specific margin values to verify the exact difference. Finally, there's a null flat sanity check using random perturbations matched to the norm.

For the null distribution: I need to clarify that the null isn't actually flat at zero—it's a positive distribution, so p-values are one-sided fractions where the null exceeds the arm. I should validate this by checking that when the arm is well above the null, the p-value is near zero, and when it falls within the null range, the p-value is large. A quick demo comparing planted large content against random nulls would confirm the machinery works.

For pair-picking: I'm considering using a deterministic hash-based approach seeded per cell rather than random selection—something like hashing the landmark and using modulo arithmetic to pick indices, though Python's built-in hash is salted per process for strings, which affects how the existing code selects targets.

I'm noticing the existing code uses Python's hash function for target selection, which means it's not reproducible across runs unless PYTHONHASHSEED is set. The verdict cells are recorded in the JSON so provenance is preserved, but re-running would pick different targets. I should use a stable hash like CRC32 instead of Python's built-in hash to avoid this reproducibility issue, and I should flag this instability to Michael as an observation rather than silently fixing it. The landmark set stays deterministic regardless of hash salt — only the target country varies. I'm thinking about adding a `--stable-pairs` flag using crc32 for consistent arm pairing, plus a `--cells-from` option to load recorded landmark-to-target mappings from a previous run's JSON file for exact 1:1 reproduction across experiments. This would be optional and off by default, but essential for validating the 32B results properly.

For the CLI, I need to add the `--arms` flag as a boolean and make `--cells-from` accept an optional file path. The experiment payload gets labeled "P-TYPE-SWAP" with a preregistration anchor, and the output filename becomes "type_swap.json" while keeping other defaults unchanged. Route and arms can coexist — if both are enabled, I should compute per-arm MLP projections using the route decomposition fields, and for the BREAK-side MLP I can calculate the unprojected norm difference per arm.

In the arm metrics output, when route is enabled, I'll add an "mlp_transport" field that sums the unprojected MLP channel magnitude across reader layers. The arms JSON also needs to include the realized norms — the swap magnitude and per-arm vector norms (which are equal by construction) — logging the swap norm as "edit_norm". For aggregation, I'm computing per-arm means for test error, transport, slot mass delta, break, and p-values, plus boolean flags to track the ordering of test errors across different categories.

Now I need to compute null p-values for each arm using the same null arrays: for transport, it's the fraction where null exceeds arm; for slot mass delta, since the pre-registration predicts a drop, I'm using a one-sided test where p equals the fraction of null values more negative than the arm value; for break, p is the fraction where null is greater than or equal to arm. Then I'll write the code to insert the ARM_BANKS constant, arm stage metrics, and pair-picking logic near the decompose function, add validation checks before the final print, and extend the run function to build arm directories after loading country data, capture logits and slot hidden states unconditionally, process per-cell arm blocks, extend the null loop, and aggregate the arm results.

Writing code implementation... Adding logits and hidden state tracking... Adding per-cell arms computation... I need to capture the slot value from the initial extraction instead of discarding it, so I'll rename that variable to `slot_b` for use in the arm calculations. Then I'm defining an evaluation function that computes arm stage metrics using the captured slot and margin values derived from the logits.

Finishing the evaluation by extracting the predicted class from the logits, optionally computing MLP transport distance if routing is enabled, then running the evaluation on the same-arm case and iterating through the arm specifications to evaluate each variant.

Now I need to set up the null arm statistics collection, which will track various metrics across iterations when the arms flag is enabled. The key thing is making sure the arm evaluation function is defined before the null loop starts so it's available when needed.

After collecting all the null statistics, I'm computing p-values for each arm by comparing its metrics against the distribution of null values — checking how often the null transport and break values exceed the arm's values, and how often the null slot mass delta falls below the arm's value.

Then I'm rounding all the key metrics to four decimal places and packaging the arm statistics along with a summary of the null distribution's mean and standard deviation into the cell dictionary. When aggregating across cells, I'm setting up to collect arm data from all the source cells and organize it by arm name. Adding validation setup... Writing test assertions... Writing arm statistics output...

I need to be careful about where the arm evaluation closure gets defined—it depends on variables from the cell scope, so it has to live inside the cell loop after those captures are set up. The null loop that comes after can use it since it's already defined by then, but I should guard that usage with a check for args.arms to avoid issues when arms aren't enabled.

For the capture unpacking, I'm switching the fourth position from a throwaway underscore to slot_b since I need that slot value for indexing into the hidden states. The hidden states are stacked as [1, seq, hidden] tensors, so I'll extract h[0, slot, :] using the slot from capture. Since everything's in bfloat16, I'm casting to float and moving to CPU before converting to numpy.

### Thinking

I've reviewed the harness and identified key reuse points in the capture, build_dirs, and null loop functions, plus a reproducibility issue with the existing hash-based target selection that uses Python's salted string hash. Now I'll implement fixes using crc32 for the new arms and add a `--cells-from` flag to pin cell/target pairs.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "import argparse\nimport json\nimport sys\nfrom pathlib import Path",
  "new_content": "import argparse\nimport json\nimport sys\nimport zlib\nfrom pathlib import Path"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "# ── no-model self-test ─────────────────────────────────────────────────────────────",
  "new_content": "# ── P-TYPE-SWAP arms (the ill-typed term) — banks + 3-stage pipeline metrics ──────\n# Pre-reg: type-check-is-the-qk-bilinear.md §P-TYPE-SWAP (APPROVED s287).\n# Arms are matched to the same-type swap's REALIZED norm (logged); the typing-vs-\n# manifold discriminator is the wrong-type-ON-MANIFOLD cell the design space lacked.\nARM_BANKS = {\n    # sortal: same broad type (entity noun), wrong domain — no continent image\n    \"sortal\": [\"tiger\", \"eagle\", \"salmon\", \"camel\", \"otter\", \"moose\"],\n    # wrong-type proper: MOD-class displacement; TWO disjoint banks (no 1-axis artifact)\n    \"wrongtype_a\": [\"fierce\", \"gentle\", \"ancient\", \"modern\", \"bright\", \"humble\"],\n    \"wrongtype_b\": [\"crimson\", \"hollow\", \"fragrant\", \"rugged\", \"serene\", \"brittle\"],\n}\n\n\ndef pick_pair(key: str, bank: list[str]) -> tuple[str, str]:\n    \"\"\"Stable per-cell bank pair. crc32, NOT builtin hash (salted per process —\n    irreproducible across runs; flagged s287).\"\"\"\n    i = zlib.crc32(key.encode()) % len(bank)\n    j = (i + len(bank) // 2) % len(bank)\n    return bank[i], bank[j]\n\n\ndef arm_stage_metrics(\n    reader_layers, lb, oproj, aw_b, vf_b, hs_b, aw_x, vf_x, hs_x, slot, margin_b, margin_x\n):\n    \"\"\"P-TYPE-SWAP 3-stage pipeline metrics for one arm vs baseline.\n\n    ⚠ Measurement correction (s287, pre-reg): the P-ATT-MED differential is\n    w-PROJECTED, so \"refused\" vs \"no w-component\" is indistinguishable there.\n    Everything here except the margin is UNPROJECTED by construction.\n\n    SURVIVAL  = mean over post-edit reader layers of ‖Δresidual at the edited slot‖\n                (did the edit live in the medium long enough to be read?)\n    TRANSPORT = Σ_L ‖Δ(attention contribution at the readout query)‖  (unprojected)\n    TE        = TRANSPORT / SURVIVAL   (join efficiency, separates medium-death\n                from join-refusal)\n    slot_mass = mean attention weight of the readout query onto the edited slot\n                (does the reader withdraw its edge from an ill-typed slot? —\n                 the P-ATT-DIFF question, causal form)\n    BREAK     = baseline correct-continent margin − arm margin (output register:\n                ignored ⟺ ≈ random-null; interferes-as-content ⟺ beats null)\n    \"\"\"\n    surv_layers = [li for li in reader_layers if li > lb]\n    surv = (\n        float(np.mean([np.linalg.norm(hs_x[li] - hs_b[li]) for li in surv_layers]))\n        if surv_layers\n        else 0.0\n    )\n    tr = 0.0\n    for li in reader_layers:\n        fb = oproj[li] @ np.einsum(\"hj,hjd->hd\", aw_b[li], vf_b[li]).reshape(-1)\n        fx = oproj[li] @ np.einsum(\"hj,hjd->hd\", aw_x[li], vf_x[li]).reshape(-1)\n        tr += float(np.linalg.norm(fx - fb))\n    sm_b = float(np.mean([aw_b[li][:, slot].mean() for li in reader_layers]))\n    sm_x = float(np.mean([aw_x[li][:, slot].mean() for li in reader_layers]))\n    return {\n        \"survival\": surv,\n        \"transport\": tr,\n        \"te\": tr / (surv + 1e-9),\n        \"slot_mass\": sm_x,\n        \"slot_mass_delta\": sm_x - sm_b,\n        \"break\": margin_b - margin_x,\n    }\n\n\n# ── no-model self-test ─────────────────────────────────────────────────────────────"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    print(f\"[validate] {'ALL PASS' if ok else 'FAIL'}\")\n    return 0 if ok else 1",
  "new_content": "    # ── P-TYPE-SWAP arm stage metrics: planted per-stage effects ──────────────────\n    rl = [1, 2]\n    op = {li: np.eye(hidden) for li in rl}\n    slot = 2\n    aw0 = {li: a_b for li in rl}\n    vf0 = {li: v_b for li in rl}\n    hs0 = np.zeros((4, hidden))\n\n    # no-change arm → all stages exactly zero\n    m0 = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vf0, hs0, slot, 2.0, 2.0)\n    z0 = m0[\"transport\"] == 0.0 and m0[\"break\"] == 0.0 and m0[\"slot_mass_delta\"] == 0.0\n    print(f\"[validate] arms zero   : transport=0 break=0 smd=0 → {z0}\")\n    ok &= z0\n\n    # content plant at the slot column + survival plant → transport>0, slot mass fixed;\n    # doubling survival with fixed transport halves TE (the normalization that\n    # separates medium-death from join-refusal)\n    vfx = {li: v_b.copy() for li in rl}\n    for li in rl:\n        vfx[li][:, slot, :] += 1.0\n    hs1 = hs0.copy()\n    hs1[1:] += 0.5 / np.sqrt(hidden)\n    mc = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vfx, hs1, slot, 2.0, 2.0)\n    hs2 = hs0.copy()\n    hs2[1:] += 1.0 / np.sqrt(hidden)\n    mc2 = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vfx, hs2, slot, 2.0, 2.0)\n    te_ok = (\n        mc[\"transport\"] > 0\n        and abs(mc[\"slot_mass_delta\"]) < 1e-12\n        and abs(mc2[\"te\"] - mc[\"te\"] / 2) < 1e-9\n    )\n    print(\n        f\"[validate] arms content: transport={mc['transport']:.3f} smd=0 \"\n        f\"te={mc['te']:.3f}→{mc2['te']:.3f} (2× survival halves TE) → {te_ok}\"\n    )\n    ok &= te_ok\n\n    # join-withdrawal plant: slot column zeroed + renormalized → slot_mass_delta < 0\n    awx = {}\n    for li in rl:\n        a = a_b.copy()\n        a[:, slot] = 0.0\n        a /= a.sum(1, keepdims=True)\n        awx[li] = a\n    mw = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, awx, vf0, hs1, slot, 2.0, 2.0)\n    w_ok = mw[\"slot_mass_delta\"] < 0\n    print(f\"[validate] arms refuse : slot_mass_delta={mw['slot_mass_delta']:.4f} < 0 → {w_ok}\")\n    ok &= w_ok\n\n    # BREAK exact: margin_b=2.0, margin_x=0.5 → break=1.5\n    mb = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vf0, hs0, slot, 2.0, 0.5)\n    b_ok = abs(mb[\"break\"] - 1.5) < 1e-12\n    print(f\"[validate] arms break  : break={mb['break']:.2f} (exact) → {b_ok}\")\n    ok &= b_ok\n\n    print(f\"[validate] {'ALL PASS' if ok else 'FAIL'}\")\n    return 0 if ok else 1"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Thinking

Now I'm working through the edits needed for the run() function—capturing extra parameters, setting up armed directories, handling cell extraction, implementing per-cell arm logic, managing null loops, aggregating results, structuring the payload, and updating the CLI interface.

## Assistant

Now the `run()` wiring — capture extras, arm directions, per-cell arms block, null-loop collection:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        r_final = nfstore[\"x\"][q]  # pre-norm final residual at readout\n        extra = {}\n        if route:",
  "new_content": "        r_final = nfstore[\"x\"][q]  # pre-norm final residual at readout\n        extra = {\n            # always captured (cheap; P-TYPE-SWAP arms + BREAK margins need them)\n            \"logits_all\": out.logits[0, -1, :].float().cpu().numpy(),\n            \"hs_slot\": np.stack(\n                [h[0, slot, :].float().cpu().numpy() for h in out.hidden_states]\n            ),  # [n_layers+1, hidden] residual at the edited slot (SURVIVAL)\n        }\n        if route:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    d_lm = build_dirs(mh3.LM_LIST)\n    d_country = build_dirs(mh3.COUNTRIES)\n    dim = next(iter(d_lm.values())).shape[0]",
  "new_content": "    d_lm = build_dirs(mh3.LM_LIST)\n    d_country = build_dirs(mh3.COUNTRIES)\n    dim = next(iter(d_lm.values())).shape[0]\n\n    # P-TYPE-SWAP arm banks (centroid offsets at ref layer, same procedure as countries)\n    d_arm_banks = (\n        {name: build_dirs(bank) for name, bank in ARM_BANKS.items()}\n        if args.arms\n        else {}\n    )\n\n    # optional 1:1 cell pinning to a previous run (builtin hash is salted per\n    # process → tgt selection is NOT reproducible across runs; flagged s287)\n    tgt_from = {}\n    if args.cells_from:\n        prev = json.loads(Path(args.cells_from).read_text())\n        tgt_from = {c[\"landmark\"]: c[\"tgt_country\"] for c in prev[\"cells\"]}\n        print(f\"[type-swap] pinned {len(tgt_from)} landmark→tgt cells from {args.cells_from}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        tgts = [c for c in mh3.COUNTRIES if mh3.COUNTRY_CONT[c] != src_cont]\n        tgt = tgts[hash(lm) % len(tgts)]\n        tgt_cont = mh3.COUNTRY_CONT[tgt]\n        swap = (d_country[tgt] - d_country[src_country]) * S\n\n        # readout flips?\n        pred_swap, _ = cont_pred([(L, d_lm[lm] * S), (lb, swap)])\n        flipped = int(pred_swap == tgt_cont)\n\n        aw_b, vf_b, rfin_b, _, ex_b = capture([(L, d_lm[lm] * S)])\n        aw_s, vf_s, rfin_s, _, ex_s = capture([(L, d_lm[lm] * S), (lb, swap)])\n        w = dla_dir(rfin_s, tgt_cont, src_cont)",
  "new_content": "        tgts = [c for c in mh3.COUNTRIES if mh3.COUNTRY_CONT[c] != src_cont]\n        tgt = tgt_from.get(lm) or tgts[hash(lm) % len(tgts)]\n        tgt_cont = mh3.COUNTRY_CONT[tgt]\n        swap = (d_country[tgt] - d_country[src_country]) * S\n\n        # readout flips?\n        pred_swap, _ = cont_pred([(L, d_lm[lm] * S), (lb, swap)])\n        flipped = int(pred_swap == tgt_cont)\n\n        aw_b, vf_b, rfin_b, slot_b, ex_b = capture([(L, d_lm[lm] * S)])\n        aw_s, vf_s, rfin_s, _, ex_s = capture([(L, d_lm[lm] * S), (lb, swap)])\n        w = dla_dir(rfin_s, tgt_cont, src_cont)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Thinking

I need to reorganize the code structure by placing the per-cell arms block before the null loop, then modifying the null loop itself, and finally adding arm p-values after it completes. I'll also need to include the `**arm_fields` expansion in the cell dictionary.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        # NULL: matched-norm random add at lb → attn contribution on the SAME w\n        null_tot = []\n        for _ in range(args.n_null):\n            rnd = rand_vec(float(np.linalg.norm(swap)))\n            aw_r, vf_r, _, _, ex_r = capture([(L, d_lm[lm] * S), (lb, rnd)])\n            nt = 0.0\n            for li in reader_layers:\n                rr = decompose(aw_b[li], aw_r[li], vf_b[li], vf_r[li], oproj[li], w)\n                nt += rr[\"aim_p\"] + rr[\"content_p\"] + rr[\"inter_p\"]\n            null_tot.append(nt)\n            if route:\n                mlp_null.append(\n                    float(\n                        sum(\n                            (ex_r[\"mlp\"][li] - ex_b[\"mlp\"][li]) @ w\n                            for li in reader_layers\n                        )\n                    )\n                )\n        null_tot = np.array(null_tot)\n        p_med = float(np.mean(np.abs(null_tot) >= abs(attn_total)))\n        if route:\n            mlp_null = np.array(mlp_null)\n            route_fields[\"p_mlp_vs_null\"] = round(\n                float(np.mean(np.abs(mlp_null) >= abs(route_fields[\"mlp_p\"]))), 3\n            )",
  "new_content": "        # ── P-TYPE-SWAP arms: sortal / wrong-type ladder at matched realized norm ──\n        arm_fields = {}\n        arm_stats = {}\n        null_arm = {\n            k: [] for k in (\"survival\", \"transport\", \"te\", \"slot_mass_delta\", \"break\")\n        }\n        if args.arms:\n            others_c = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]\n\n            def cont_margin(lo):\n                return float(lo[cont_ids[src_cont]] - max(lo[o] for o in others_c))\n\n            margin_b = cont_margin(ex_b[\"logits_all\"])\n            edit_norm = float(np.linalg.norm(swap))\n\n            def arm_eval(aw_x, vf_x, ex_x):\n                m = arm_stage_metrics(\n                    reader_layers, lb, oproj,\n                    aw_b, vf_b, ex_b[\"hs_slot\"],\n                    aw_x, vf_x, ex_x[\"hs_slot\"],\n                    slot_b, margin_b, cont_margin(ex_x[\"logits_all\"]),\n                )\n                m[\"pred\"] = max(\n                    cont_ids, key=lambda k: ex_x[\"logits_all\"][cont_ids[k]]\n                )\n                if route:\n                    m[\"mlp_transport\"] = float(\n                        sum(\n                            np.linalg.norm(ex_x[\"mlp\"][li] - ex_b[\"mlp\"][li])\n                            for li in reader_layers\n                        )\n                    )\n                return m\n\n            arm_stats[\"same\"] = arm_eval(aw_s, vf_s, ex_s)  # positive control, no re-forward\n            for name, bank in ARM_BANKS.items():\n                b1, b2 = pick_pair(lm, bank)\n                disp = d_arm_banks[name][b1] - d_arm_banks[name][b2]\n                disp = disp / (np.linalg.norm(disp) + 1e-9) * edit_norm\n                aw_x, vf_x, _, _, ex_x = capture([(L, d_lm[lm] * S), (lb, disp)])\n                arm_stats[name] = arm_eval(aw_x, vf_x, ex_x)\n                arm_stats[name][\"pair\"] = f\"{b1}-{b2}\"\n            arm_fields[\"edit_norm\"] = round(edit_norm, 2)\n\n        # NULL: matched-norm random add at lb → attn contribution on the SAME w\n        null_tot = []\n        for _ in range(args.n_null):\n            rnd = rand_vec(float(np.linalg.norm(swap)))\n            aw_r, vf_r, _, _, ex_r = capture([(L, d_lm[lm] * S), (lb, rnd)])\n            nt = 0.0\n            for li in reader_layers:\n                rr = decompose(aw_b[li], aw_r[li], vf_b[li], vf_r[li], oproj[li], w)\n                nt += rr[\"aim_p\"] + rr[\"content_p\"] + rr[\"inter_p\"]\n            null_tot.append(nt)\n            if route:\n                mlp_null.append(\n                    float(\n                        sum(\n                            (ex_r[\"mlp\"][li] - ex_b[\"mlp\"][li]) @ w\n                            for li in reader_layers\n                        )\n                    )\n                )\n            if args.arms:\n                nm = arm_eval(aw_r, vf_r, ex_r)\n                for k in null_arm:\n                    null_arm[k].append(nm[k])\n        null_tot = np.array(null_tot)\n        p_med = float(np.mean(np.abs(null_tot) >= abs(attn_total)))\n        if route:\n            mlp_null = np.array(mlp_null)\n            route_fields[\"p_mlp_vs_null\"] = round(\n                float(np.mean(np.abs(mlp_null) >= abs(route_fields[\"mlp_p\"]))), 3\n            )\n        if args.arms:\n            na = {k: np.array(v) for k, v in null_arm.items()}\n            for name, st in arm_stats.items():\n                # one-sided vs the matched-norm random-add distribution:\n                # transport/te/survival/break: arm ≥ null; slot withdrawal: arm ≤ null\n                st[\"p_transport\"] = round(float(np.mean(na[\"transport\"] >= st[\"transport\"])), 3)\n                st[\"p_te\"] = round(float(np.mean(na[\"te\"] >= st[\"te\"])), 3)\n                st[\"p_survival\"] = round(float(np.mean(na[\"survival\"] >= st[\"survival\"])), 3)\n                st[\"p_slot_drop\"] = round(\n                    float(np.mean(na[\"slot_mass_delta\"] <= st[\"slot_mass_delta\"])), 3\n                )\n                st[\"p_break\"] = round(float(np.mean(na[\"break\"] >= st[\"break\"])), 3)\n                for k in (\n                    \"survival\", \"transport\", \"te\",\n                    \"slot_mass\", \"slot_mass_delta\", \"break\", \"mlp_transport\",\n                ):\n                    if k in st:\n                        st[k] = round(st[k], 4)\n            arm_fields[\"arms\"] = arm_stats\n            arm_fields[\"null_summary\"] = {\n                k: {\"mean\": round(float(np.mean(v)), 4), \"std\": round(float(np.std(v)), 4)}\n                for k, v in na.items()\n            }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "            \"per_layer\": {str(k): v for k, v in per_layer.items()},\n            **route_fields,\n        }\n        cells.append(cell)",
  "new_content": "            \"per_layer\": {str(k): v for k, v in per_layer.items()},\n            **route_fields,\n            **arm_fields,\n        }\n        cells.append(cell)\n        if args.arms:\n            _a = arm_stats\n            _n = arm_fields[\"null_summary\"]\n            print(\n                f\"[type-swap] {lm:16s} te same={_a['same']['te']:.2f} \"\n                f\"sortal={_a['sortal']['te']:.2f} wtA={_a['wrongtype_a']['te']:.2f} \"\n                f\"wtB={_a['wrongtype_b']['te']:.2f} null={_n['te']['mean']:.2f} | \"\n                f\"smΔ s={_a['sortal']['slot_mass_delta']:+.4f} \"\n                f\"a={_a['wrongtype_a']['slot_mass_delta']:+.4f} | \"\n                f\"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) \"\n                f\"a={_a['wrongtype_a']['break']:+.2f}(p{_a['wrongtype_a']['p_break']}) | \"\n                f\"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/\"\n                f\"{_a['wrongtype_b']['pred']}\"\n            )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Thinking

I'm checking the variable ordering in the code to make sure the new `arm_fields` dictionary doesn't conflict with existing variables like `route_fields` and `mlp_null` that were already defined earlier in the block.

## Assistant

Now the aggregate, payload, and CLI:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    if route:\n        mlp_cells = [c for c in agg_src if c.get(\"route\") == \"mlp\"]",
  "new_content": "    if args.arms:\n        arm_names = [\"same\"] + list(ARM_BANKS.keys())\n        arm_cells = [c for c in agg_src if \"arms\" in c]\n        agg[\"arms\"] = {}\n        for name in arm_names:\n            vals = [c[\"arms\"][name] for c in arm_cells]\n            agg[\"arms\"][name] = {\n                \"mean_survival\": round(float(np.mean([v[\"survival\"] for v in vals])), 4),\n                \"mean_transport\": round(float(np.mean([v[\"transport\"] for v in vals])), 4),\n                \"mean_te\": round(float(np.mean([v[\"te\"] for v in vals])), 4),\n                \"mean_slot_mass_delta\": round(\n                    float(np.mean([v[\"slot_mass_delta\"] for v in vals])), 4\n                ),\n                \"mean_break\": round(float(np.mean([v[\"break\"] for v in vals])), 4),\n                \"mean_p_transport\": round(\n                    float(np.mean([v[\"p_transport\"] for v in vals])), 3\n                ),\n                \"mean_p_te\": round(float(np.mean([v[\"p_te\"] for v in vals])), 3),\n                \"mean_p_break\": round(float(np.mean([v[\"p_break\"] for v in vals])), 3),\n                \"n_pred_stays_src\": sum(\n                    1 for c in arm_cells if c[\"arms\"][name][\"pred\"] == c[\"src_cont\"]\n                ),\n            }\n        te_row = {n: agg[\"arms\"][n][\"mean_te\"] for n in arm_names}\n        print(\n            f\"[type-swap] ARM TE ladder: \"\n            + \" \".join(f\"{n}={te_row[n]:.2f}\" for n in arm_names)\n            + f\" | ordering same>sortal>wrong = \"\n            f\"{te_row['same'] > te_row['sortal'] > min(te_row['wrongtype_a'], te_row['wrongtype_b'])}\"\n        )\n        print(\n            f\"[type-swap] ARM break: \"\n            + \" \".join(f\"{n}={agg['arms'][n]['mean_break']:+.2f}\" for n in arm_names)\n            + f\" | preds-stay-src: \"\n            + \" \".join(f\"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}\" for n in arm_names)\n        )\n\n    if route:\n        mlp_cells = [c for c in agg_src if c.get(\"route\") == \"mlp\"]"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    payload = {\n        \"experiment\": \"P-ATT-FFN\" if route else \"P-ATT-MED\",\n        \"grade\": (\"smoke\" if \"4b\" in args.out.lower() else \"verdict\"),\n        \"prereg\": (\n            \"mementum/knowledge/explore/type-check-is-the-qk-bilinear.md#\"\n            + (\"p-att-ffn\" if route else \"p-att-med\")\n        ),",
  "new_content": "    exp_name = (\n        \"P-TYPE-SWAP\" if args.arms else (\"P-ATT-FFN\" if route else \"P-ATT-MED\")\n    )\n    payload = {\n        \"experiment\": exp_name,\n        \"grade\": (\"smoke\" if \"4b\" in args.out.lower() else \"verdict\"),\n        \"prereg\": (\n            \"mementum/knowledge/explore/type-check-is-the-qk-bilinear.md#\"\n            + exp_name.lower().replace(\"_\", \"-\")\n        ),"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        \"n_null\": args.n_null,\n        \"route_decomp\": route,\n        \"aggregate\": agg,\n        \"cells\": cells,\n    }\n    fname = \"att_ffn.json\" if route else \"att_mediation.json\"\n    (out / fname).write_text(json.dumps(payload, indent=2))\n    print(f\"[att-{'ffn' if route else 'med'}] wrote {out}/{fname}\")",
  "new_content": "        \"n_null\": args.n_null,\n        \"route_decomp\": route,\n        \"arms_enabled\": args.arms,\n        \"cells_from\": args.cells_from,\n        \"arm_banks\": ARM_BANKS if args.arms else None,\n        \"aggregate\": agg,\n        \"cells\": cells,\n    }\n    fname = (\n        \"type_swap.json\"\n        if args.arms\n        else (\"att_ffn.json\" if route else \"att_mediation.json\")\n    )\n    (out / fname).write_text(json.dumps(payload, indent=2))\n    print(f\"[{exp_name.lower()}] wrote {out}/{fname}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    ap.add_argument(\n        \"--route-decomp\",\n        action=\"store_true\",\n        help=\"P-ATT-FFN: add MLP + direct channels, total reconstruction, depth-order\",\n    )\n    args = ap.parse_args()",
  "new_content": "    ap.add_argument(\n        \"--route-decomp\",\n        action=\"store_true\",\n        help=\"P-ATT-FFN: add MLP + direct channels, total reconstruction, depth-order\",\n    )\n    ap.add_argument(\n        \"--arms\",\n        action=\"store_true\",\n        help=\"P-TYPE-SWAP: sortal/wrong-type ill-typed-term arms, 3-stage \"\n        \"survival/transport/reduction metrics (unprojected), matched-norm ladder\",\n    )\n    ap.add_argument(\n        \"--cells-from\",\n        default=None,\n        help=\"pin landmark→tgt_country cells 1:1 from a previous run's JSON \"\n        \"(builtin hash is process-salted → not reproducible otherwise)\",\n    )\n    args = ap.parse_args()"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Thinking

I'm checking whether `args` is properly accessible within the `run` function and confirming that the aggregate code has the right scope. There's a potential linting issue with the f-string concatenation in the print statement — using `f"..."` with a `+` operator might trigger a ruff warning about unnecessary f-strings, so I should clean that up.

## Assistant

λ sync + lint + the no-model self-test:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/explore/att_mediation.py; uv run python scripts/explore/att_mediation.py --validate",
  "timeout": 120000
}
```

**Summary:** $ uv run ruff check scripts/explore/a...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (90 > 88)
   --> scripts/explore/att_mediation.py:114:89
    |
113 | def arm_stage_metrics(
114 |     reader_layers, lb, oproj, aw_b, vf_b, hs_b, aw_x, vf_x, hs_x, slot, margin_b, margin_x
    |                                                                                         ^^
115 | ):
116 |     """P-TYPE-SWAP 3-stage pipeline metrics for one arm vs baseline.
    |

E501 Line too long (95 > 88)
   --> scripts/explore/att_mediation.py:280:89
    |
278 |     mw = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, awx, vf0, hs1, slot, 2.0, 2.0)
279 |     w_ok = mw["slot_mass_delta"] < 0
280 |     print(f"[validate] arms refuse : slot_mass_delta={mw['slot_mass_delta']:.4f} < 0 → {w_ok}")
    |                                                                                         ^^^^^^^
281 |     ok &= w_ok
    |

E501 Line too long (94 > 88)
   --> scripts/explore/att_mediation.py:375:89
    |
373 |         prev = json.loads(Path(args.cells_from).read_text())
374 |         tgt_from = {c["landmark"]: c["tgt_country"] for c in prev["cells"]}
375 |         print(f"[type-swap] pinned {len(tgt_from)} landmark→tgt cells from {args.cells_from}")
    |                                                                                         ^^^^^^
376 |
377 |     def rand_vec(norm):
    |

B023 Function definition does not bind loop variable `src_cont`
   --> scripts/explore/att_mediation.py:576:42
    |
575 |             def cont_margin(lo):
576 |                 return float(lo[cont_ids[src_cont]] - max(lo[o] for o in others_c))
    |                                          ^^^^^^^^
577 |
578 |             margin_b = cont_margin(ex_b["logits_all"])
    |

B023 Function definition does not bind loop variable `others_c`
   --> scripts/explore/att_mediation.py:576:74
    |
575 |             def cont_margin(lo):
576 |                 return float(lo[cont_ids[src_cont]] - max(lo[o] for o in others_c))
    |                                                                          ^^^^^^^^
577 |
578 |             margin_b = cont_margin(ex_b["logits_all"])
    |

B023 Function definition does not bind loop variable `aw_b`
   --> scripts/explore/att_mediation.py:584:21
    |
582 |                 m = arm_stage_metrics(
583 |                     reader_layers, lb, oproj,
584 |                     aw_b, vf_b, ex_b["hs_slot"],
    |                     ^^^^
585 |                     aw_x, vf_x, ex_x["hs_slot"],
586 |                     slot_b, margin_b, cont_margin(ex_x["logits_all"]),
    |

B023 Function definition does not bind loop variable `vf_b`
   --> scripts/explore/att_mediation.py:584:27
    |
582 |                 m = arm_stage_metrics(
583 |                     reader_layers, lb, oproj,
584 |                     aw_b, vf_b, ex_b["hs_slot"],
    |                           ^^^^
585 |                     aw_x, vf_x, ex_x["hs_slot"],
586 |                     slot_b, margin_b, cont_margin(ex_x["logits_all"]),
    |

B023 Function definition does not bind loop variable `ex_b`
   --> scripts/explore/att_mediation.py:584:33
    |
582 |                 m = arm_stage_metrics(
583 |                     reader_layers, lb, oproj,
584 |                     aw_b, vf_b, ex_b["hs_slot"],
    |                                 ^^^^
585 |                     aw_x, vf_x, ex_x["hs_slot"],
586 |                     slot_b, margin_b, cont_margin(ex_x["logits_all"]),
    |

B023 Function definition does not bind loop variable `slot_b`
   --> scripts/explore/att_mediation.py:586:21
    |
584 |                     aw_b, vf_b, ex_b["hs_slot"],
585 |                     aw_x, vf_x, ex_x["hs_slot"],
586 |                     slot_b, margin_b, cont_margin(ex_x["logits_all"]),
    |                     ^^^^^^
587 |                 )
588 |                 m["pred"] = max(
    |

B023 Function definition does not bind loop variable `margin_b`
   --> scripts/explore/att_mediation.py:586:29
    |
584 |                     aw_b, vf_b, ex_b["hs_slot"],
585 |                     aw_x, vf_x, ex_x["hs_slot"],
586 |                     slot_b, margin_b, cont_margin(ex_x["logits_all"]),
    |                             ^^^^^^^^
587 |                 )
588 |                 m["pred"] = max(
    |

B023 Function definition does not bind loop variable `k`
   --> scripts/explore/att_mediation.py:589:73
    |
587 |                 )
588 |                 m["pred"] = max(
589 |                     cont_ids, key=lambda k: ex_x["logits_all"][cont_ids[k]]
    |                                                                         ^
590 |                 )
591 |                 if route:
    |

B023 Function definition does not bind loop variable `ex_b`
   --> scripts/explore/att_mediation.py:594:62
    |
592 |                     m["mlp_transport"] = float(
593 |                         sum(
594 |                             np.linalg.norm(ex_x["mlp"][li] - ex_b["mlp"][li])
    |                                                              ^^^^
595 |                             for li in reader_layers
596 |                         )
    |

E501 Line too long (93 > 88)
   --> scripts/explore/att_mediation.py:600:89
    |
598 |                 return m
599 |
600 |             arm_stats["same"] = arm_eval(aw_s, vf_s, ex_s)  # positive control, no re-forward
    |                                                                                         ^^^^^
601 |             for name, bank in ARM_BANKS.items():
602 |                 b1, b2 = pick_pair(lm, bank)
    |

B007 Loop control variable `name` not used within loop body
   --> scripts/explore/att_mediation.py:642:17
    |
640 |         if args.arms:
641 |             na = {k: np.array(v) for k, v in null_arm.items()}
642 |             for name, st in arm_stats.items():
    |                 ^^^^
643 |                 # one-sided vs the matched-norm random-add distribution:
644 |                 # transport/te/survival/break: arm ≥ null; slot withdrawal: arm ≤ null
    |
help: Rename unused `name` to `_name`

E501 Line too long (96 > 88)
   --> scripts/explore/att_mediation.py:645:89
    |
643 |                 # one-sided vs the matched-norm random-add distribution:
644 |                 # transport/te/survival/break: arm ≥ null; slot withdrawal: arm ≤ null
645 |                 st["p_transport"] = round(float(np.mean(na["transport"] >= st["transport"])), 3)
    |                                                                                         ^^^^^^^^
646 |                 st["p_te"] = round(float(np.mean(na["te"] >= st["te"])), 3)
647 |                 st["p_survival"] = round(float(np.mean(na["survival"] >= st["survival"])), 3)
    |

E501 Line too long (93 > 88)
   --> scripts/explore/att_mediation.py:647:89
    |
645 |                 st["p_transport"] = round(float(np.mean(na["transport"] >= st["transport"])), 3)
646 |                 st["p_te"] = round(float(np.mean(na["te"] >= st["te"])), 3)
647 |                 st["p_survival"] = round(float(np.mean(na["survival"] >= st["survival"])), 3)
    |                                                                                         ^^^^^
648 |                 st["p_slot_drop"] = round(
649 |                     float(np.mean(na["slot_mass_delta"] <= st["slot_mass_delta"])), 3
    |

E501 Line too long (91 > 88)
   --> scripts/explore/att_mediation.py:660:89
    |
658 |             arm_fields["arms"] = arm_stats
659 |             arm_fields["null_summary"] = {
660 |                 k: {"mean": round(float(np.mean(v)), 4), "std": round(float(np.std(v)), 4)}
    |                                                                                         ^^^
661 |                 for k, v in na.items()
662 |             }
    |

E501 Line too long (90 > 88)
   --> scripts/explore/att_mediation.py:696:89
    |
694 |                 f"a={_a['wrongtype_a']['slot_mass_delta']:+.4f} | "
695 |                 f"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) "
696 |                 f"a={_a['wrongtype_a']['break']:+.2f}(p{_a['wrongtype_a']['p_break']}) | "
    |                                                                                         ^^
697 |                 f"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/"
698 |                 f"{_a['wrongtype_b']['pred']}"
    |

RUF005 Consider `["same", *list(ARM_BANKS.keys())]` instead of concatenation
   --> scripts/explore/att_mediation.py:738:21
    |
737 |     if args.arms:
738 |         arm_names = ["same"] + list(ARM_BANKS.keys())
    |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
739 |         arm_cells = [c for c in agg_src if "arms" in c]
740 |         agg["arms"] = {}
    |
help: Replace with `["same", *list(ARM_BANKS.keys())]`

E501 Line too long (89 > 88)
   --> scripts/explore/att_mediation.py:744:89
    |
742 |             vals = [c["arms"][name] for c in arm_cells]
743 |             agg["arms"][name] = {
744 |                 "mean_survival": round(float(np.mean([v["survival"] for v in vals])), 4),
    |                                                                                         ^
745 |                 "mean_transport": round(float(np.mean([v["transport"] for v in vals])), 4),
746 |                 "mean_te": round(float(np.mean([v["te"] for v in vals])), 4),
    |

E501 Line too long (91 > 88)
   --> scripts/explore/att_mediation.py:745:89
    |
743 |             agg["arms"][name] = {
744 |                 "mean_survival": round(float(np.mean([v["survival"] for v in vals])), 4),
745 |                 "mean_transport": round(float(np.mean([v["transport"] for v in vals])), 4),
    |                                                                                         ^^^
746 |                 "mean_te": round(float(np.mean([v["te"] for v in vals])), 4),
747 |                 "mean_slot_mass_delta": round(
    |

F541 [*] f-string without any placeholders
   --> scripts/explore/att_mediation.py:762:13
    |
760 |         te_row = {n: agg["arms"][n]["mean_te"] for n in arm_names}
761 |         print(
762 |             f"[type-swap] ARM TE ladder: "
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
763 |             + " ".join(f"{n}={te_row[n]:.2f}" for n in arm_names)
764 |             + f" | ordering same>sortal>wrong = "
    |
help: Remove extraneous `f` prefix

E501 Line too long (102 > 88)
   --> scripts/explore/att_mediation.py:765:89
    |
763 |             + " ".join(f"{n}={te_row[n]:.2f}" for n in arm_names)
764 |             + f" | ordering same>sortal>wrong = "
765 |             f"{te_row['same'] > te_row['sortal'] > min(te_row['wrongtype_a'], te_row['wrongtype_b'])}"
    |                                                                                         ^^^^^^^^^^^^^^
766 |         )
767 |         print(
    |

F541 [*] f-string without any placeholders
   --> scripts/explore/att_mediation.py:768:13
    |
766 |         )
767 |         print(
768 |             f"[type-swap] ARM break: "
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^
769 |             + " ".join(f"{n}={agg['arms'][n]['mean_break']:+.2f}" for n in arm_names)
770 |             + f" | preds-stay-src: "
    |
help: Remove extraneous `f` prefix

F541 [*] f-string without any placeholders
   --> scripts/explore/att_mediation.py:770:15
    |
768 |             f"[type-swap] ARM break: "
769 |             + " ".join(f"{n}={agg['arms'][n]['mean_break']:+.2f}" for n in arm_names)
770 |             + f" | preds-stay-src: "
    |               ^^^^^^^^^^^^^^^^^^^^^^
771 |             + " ".join(f"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}" for n in arm_names)
772 |         )
    |
help: Remove extraneous `f` prefix

E501 Line too long (103 > 88)
   --> scripts/explore/att_mediation.py:771:89
    |
769 |             + " ".join(f"{n}={agg['arms'][n]['mean_break']:+.2f}" for n in arm_names)
770 |             + f" | preds-stay-src: "
771 |             + " ".join(f"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}" for n in arm_names)
    |                                                                                         ^^^^^^^^^^^^^^^
772 |         )
    |

Found 26 errors.
[*] 3 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
[validate] CONTENT-only: aim=0.000 con=1.000 int=0.000
[validate] AIM-only    : aim=1.000 con=0.000 int=0.000
[validate] linearity   : full=5.574819 recon=5.574819 |Δ|=8.88e-16
[validate] null flat   : mean=-0.0105 std=5.0381 |mean/std|=0.002
[validate] route recon : total=8.3316 attn=1.3 mlp=7.4316 direct=-0.4000 (true -0.4) route=mlp
[validate] arms zero   : transport=0 break=0 smd=0 → True
[validate] arms content: transport=1.138 smd=0 te=2.276→1.138 (2× survival halves TE) → False
[validate] arms refuse : slot_mass_delta=-0.1302 < 0 → True
[validate] arms break  : break=1.50 (exact) → True
[validate] FAIL
```

### Thinking

I'm debugging a test failure where the TE value is actually being halved correctly (2.276 → 1.138), but the assertion is still returning False. Looking at the three conditions in te_ok, transport and slot_mass_delta seem fine, but something's off with how slot_mass is being computed—it's only changing in the slot column when it should be consistent across all columns.

The real culprit is floating-point precision: the epsilon term in the denominator compounds when dividing by 2, creating a difference around 1.1e-9 which exceeds the 1e-9 tolerance. I need to relax the tolerance to 1e-6 since the printed values confirm the halving is correct. For the survival values, the norm calculation checks out at 0.5. The transport contribution is also valid given the velocity changes per head.

For the lint errors, the B023 warnings about closure-over-loop-variable are legitimate ruff complaints, but the closures only execute within their iteration. The existing code avoided this by binding the loop variable through default arguments in a factory function, so I'll apply the same pattern here.

Fixing the function signatures...

There's a Ruff linting issue where it's flagging a lambda parameter `k` as shadowing a loop variable `k` that's used elsewhere in the function scope — like in the `for k in null_arm` loop later. The lambda's `k` parameter is properly bound, but Ruff's heuristic is catching the name collision at the point where `k` is used inside `cont_ids[k]`.

Renaming the lambda parameter to something like `c` will clear that up. I also need to handle a few other linting issues: rename an unused loop variable to use an underscore prefix, shorten some lines that exceed the character limit, remove unnecessary f-string prefixes, and apply unpacking where it makes sense.

### Thinking

I found two fixable issues: the TE test tolerance collides with the denominator epsilon causing a ~1e-9 discrepancy, and ruff wants explicit closure bindings plus some formatting cleanups. I'll fix these now.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "def arm_stage_metrics(\n    reader_layers, lb, oproj, aw_b, vf_b, hs_b, aw_x, vf_x, hs_x, slot, margin_b, margin_x\n):",
  "new_content": "def arm_stage_metrics(\n    reader_layers, lb, oproj, aw_b, vf_b, hs_b, aw_x, vf_x, hs_x, slot,\n    margin_b, margin_x,\n):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    te_ok = (\n        mc[\"transport\"] > 0\n        and abs(mc[\"slot_mass_delta\"]) < 1e-12\n        and abs(mc2[\"te\"] - mc[\"te\"] / 2) < 1e-9\n    )",
  "new_content": "    te_ok = (\n        mc[\"transport\"] > 0\n        and abs(mc[\"slot_mass_delta\"]) < 1e-12\n        and abs(mc2[\"te\"] - mc[\"te\"] / 2) < 1e-6  # 1e-9 denom epsilon\n    )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    mw = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, awx, vf0, hs1, slot, 2.0, 2.0)\n    w_ok = mw[\"slot_mass_delta\"] < 0\n    print(f\"[validate] arms refuse : slot_mass_delta={mw['slot_mass_delta']:.4f} < 0 → {w_ok}\")",
  "new_content": "    mw = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, awx, vf0, hs1, slot, 2.0, 2.0)\n    w_ok = mw[\"slot_mass_delta\"] < 0\n    print(\n        f\"[validate] arms refuse : slot_mass_delta={mw['slot_mass_delta']:.4f}\"\n        f\" < 0 → {w_ok}\"\n    )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        tgt_from = {c[\"landmark\"]: c[\"tgt_country\"] for c in prev[\"cells\"]}\n        print(f\"[type-swap] pinned {len(tgt_from)} landmark→tgt cells from {args.cells_from}\")",
  "new_content": "        tgt_from = {c[\"landmark\"]: c[\"tgt_country\"] for c in prev[\"cells\"]}\n        print(\n            f\"[type-swap] pinned {len(tgt_from)} landmark→tgt cells \"\n            f\"from {args.cells_from}\"\n        )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "            others_c = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]\n\n            def cont_margin(lo):\n                return float(lo[cont_ids[src_cont]] - max(lo[o] for o in others_c))\n\n            margin_b = cont_margin(ex_b[\"logits_all\"])\n            edit_norm = float(np.linalg.norm(swap))\n\n            def arm_eval(aw_x, vf_x, ex_x):\n                m = arm_stage_metrics(\n                    reader_layers, lb, oproj,\n                    aw_b, vf_b, ex_b[\"hs_slot\"],\n                    aw_x, vf_x, ex_x[\"hs_slot\"],\n                    slot_b, margin_b, cont_margin(ex_x[\"logits_all\"]),\n                )\n                m[\"pred\"] = max(\n                    cont_ids, key=lambda k: ex_x[\"logits_all\"][cont_ids[k]]\n                )\n                if route:\n                    m[\"mlp_transport\"] = float(\n                        sum(\n                            np.linalg.norm(ex_x[\"mlp\"][li] - ex_b[\"mlp\"][li])\n                            for li in reader_layers\n                        )\n                    )\n                return m\n\n            arm_stats[\"same\"] = arm_eval(aw_s, vf_s, ex_s)  # positive control, no re-forward",
  "new_content": "            others_c = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]\n\n            def cont_margin(lo, _sc=src_cont, _oc=tuple(others_c)):\n                return float(lo[cont_ids[_sc]] - max(lo[o] for o in _oc))\n\n            margin_b = cont_margin(ex_b[\"logits_all\"])\n            edit_norm = float(np.linalg.norm(swap))\n\n            def arm_eval(\n                aw_x, vf_x, ex_x,\n                _awb=aw_b, _vfb=vf_b, _exb=ex_b, _slot=slot_b,\n                _mb=margin_b, _cm=cont_margin,\n            ):\n                m = arm_stage_metrics(\n                    reader_layers, lb, oproj,\n                    _awb, _vfb, _exb[\"hs_slot\"],\n                    aw_x, vf_x, ex_x[\"hs_slot\"],\n                    _slot, _mb, _cm(ex_x[\"logits_all\"]),\n                )\n                m[\"pred\"] = max(\n                    cont_ids, key=lambda c: ex_x[\"logits_all\"][cont_ids[c]]\n                )\n                if route:\n                    m[\"mlp_transport\"] = float(\n                        sum(\n                            np.linalg.norm(ex_x[\"mlp\"][li] - _exb[\"mlp\"][li])\n                            for li in reader_layers\n                        )\n                    )\n                return m\n\n            # positive control, no re-forward (reuses the swap capture)\n            arm_stats[\"same\"] = arm_eval(aw_s, vf_s, ex_s)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "            na = {k: np.array(v) for k, v in null_arm.items()}\n            for name, st in arm_stats.items():\n                # one-sided vs the matched-norm random-add distribution:\n                # transport/te/survival/break: arm ≥ null; slot withdrawal: arm ≤ null\n                st[\"p_transport\"] = round(float(np.mean(na[\"transport\"] >= st[\"transport\"])), 3)\n                st[\"p_te\"] = round(float(np.mean(na[\"te\"] >= st[\"te\"])), 3)\n                st[\"p_survival\"] = round(float(np.mean(na[\"survival\"] >= st[\"survival\"])), 3)\n                st[\"p_slot_drop\"] = round(\n                    float(np.mean(na[\"slot_mass_delta\"] <= st[\"slot_mass_delta\"])), 3\n                )\n                st[\"p_break\"] = round(float(np.mean(na[\"break\"] >= st[\"break\"])), 3)\n                for k in (\n                    \"survival\", \"transport\", \"te\",\n                    \"slot_mass\", \"slot_mass_delta\", \"break\", \"mlp_transport\",\n                ):\n                    if k in st:\n                        st[k] = round(st[k], 4)\n            arm_fields[\"arms\"] = arm_stats\n            arm_fields[\"null_summary\"] = {\n                k: {\"mean\": round(float(np.mean(v)), 4), \"std\": round(float(np.std(v)), 4)}\n                for k, v in na.items()\n            }",
  "new_content": "            na = {k: np.array(v) for k, v in null_arm.items()}\n            for st in arm_stats.values():\n                # one-sided vs the matched-norm random-add distribution:\n                # transport/te/survival/break: arm ≥ null; slot withdrawal: ≤\n                st[\"p_transport\"] = round(\n                    float(np.mean(na[\"transport\"] >= st[\"transport\"])), 3\n                )\n                st[\"p_te\"] = round(float(np.mean(na[\"te\"] >= st[\"te\"])), 3)\n                st[\"p_survival\"] = round(\n                    float(np.mean(na[\"survival\"] >= st[\"survival\"])), 3\n                )\n                st[\"p_slot_drop\"] = round(\n                    float(np.mean(na[\"slot_mass_delta\"] <= st[\"slot_mass_delta\"])), 3\n                )\n                st[\"p_break\"] = round(float(np.mean(na[\"break\"] >= st[\"break\"])), 3)\n                for k in (\n                    \"survival\", \"transport\", \"te\",\n                    \"slot_mass\", \"slot_mass_delta\", \"break\", \"mlp_transport\",\n                ):\n                    if k in st:\n                        st[k] = round(st[k], 4)\n            arm_fields[\"arms\"] = arm_stats\n            arm_fields[\"null_summary\"] = {\n                k: {\n                    \"mean\": round(float(np.mean(v)), 4),\n                    \"std\": round(float(np.std(v)), 4),\n                }\n                for k, v in na.items()\n            }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "    if args.arms:\n        arm_names = [\"same\"] + list(ARM_BANKS.keys())\n        arm_cells = [c for c in agg_src if \"arms\" in c]\n        agg[\"arms\"] = {}\n        for name in arm_names:\n            vals = [c[\"arms\"][name] for c in arm_cells]\n            agg[\"arms\"][name] = {\n                \"mean_survival\": round(float(np.mean([v[\"survival\"] for v in vals])), 4),\n                \"mean_transport\": round(float(np.mean([v[\"transport\"] for v in vals])), 4),\n                \"mean_te\": round(float(np.mean([v[\"te\"] for v in vals])), 4),",
  "new_content": "    if args.arms:\n        arm_names = [\"same\", *ARM_BANKS]\n        arm_cells = [c for c in agg_src if \"arms\" in c]\n        agg[\"arms\"] = {}\n        for name in arm_names:\n            vals = [c[\"arms\"][name] for c in arm_cells]\n            agg[\"arms\"][name] = {\n                \"mean_survival\": round(\n                    float(np.mean([v[\"survival\"] for v in vals])), 4\n                ),\n                \"mean_transport\": round(\n                    float(np.mean([v[\"transport\"] for v in vals])), 4\n                ),\n                \"mean_te\": round(float(np.mean([v[\"te\"] for v in vals])), 4),"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "        te_row = {n: agg[\"arms\"][n][\"mean_te\"] for n in arm_names}\n        print(\n            f\"[type-swap] ARM TE ladder: \"\n            + \" \".join(f\"{n}={te_row[n]:.2f}\" for n in arm_names)\n            + f\" | ordering same>sortal>wrong = \"\n            f\"{te_row['same'] > te_row['sortal'] > min(te_row['wrongtype_a'], te_row['wrongtype_b'])}\"\n        )\n        print(\n            f\"[type-swap] ARM break: \"\n            + \" \".join(f\"{n}={agg['arms'][n]['mean_break']:+.2f}\" for n in arm_names)\n            + f\" | preds-stay-src: \"\n            + \" \".join(f\"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}\" for n in arm_names)\n        )",
  "new_content": "        te_row = {n: agg[\"arms\"][n][\"mean_te\"] for n in arm_names}\n        wt_min = min(te_row[\"wrongtype_a\"], te_row[\"wrongtype_b\"])\n        ladder = te_row[\"same\"] > te_row[\"sortal\"] > wt_min\n        print(\n            \"[type-swap] ARM TE ladder: \"\n            + \" \".join(f\"{n}={te_row[n]:.2f}\" for n in arm_names)\n            + f\" | ordering same>sortal>wrong = {ladder}\"\n        )\n        print(\n            \"[type-swap] ARM break: \"\n            + \" \".join(f\"{n}={agg['arms'][n]['mean_break']:+.2f}\" for n in arm_names)\n            + \" | preds-stay-src: \"\n            + \" \".join(\n                f\"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}\"\n                for n in arm_names\n            )\n        )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/explore/att_mediation.py && uv run python scripts/explore/att_mediation.py --validate",
  "timeout": 120000
}
```

**Summary:** $ uv run ruff check scripts/explore/a...

**Output:**
```
Exit code: 1
Stdout:
B023 Function definition does not bind loop variable `c`
   --> scripts/explore/att_mediation.py:600:73
    |
598 |                 )
599 |                 m["pred"] = max(
600 |                     cont_ids, key=lambda c: ex_x["logits_all"][cont_ids[c]]
    |                                                                         ^
601 |                 )
602 |                 if route:
    |

E501 Line too long (90 > 88)
   --> scripts/explore/att_mediation.py:715:89
    |
713 |                 f"a={_a['wrongtype_a']['slot_mass_delta']:+.4f} | "
714 |                 f"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) "
715 |                 f"a={_a['wrongtype_a']['break']:+.2f}(p{_a['wrongtype_a']['p_break']}) | "
    |                                                                                         ^^
716 |                 f"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/"
717 |                 f"{_a['wrongtype_b']['pred']}"
    |

Found 2 errors.
```

### Thinking

I'm looking at a linting issue where the variable `c` is being flagged because it's used as a loop variable in the enclosing scope. The fix is to either bind it through a lambda default parameter or rename it to avoid the conflict with existing loop variables like those in comprehensions over continents.

I also need to shorten a long print statement on line 715 to fix the line length violation.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "                m[\"pred\"] = max(\n                    cont_ids, key=lambda c: ex_x[\"logits_all\"][cont_ids[c]]\n                )",
  "new_content": "                m[\"pred\"] = max(\n                    cont_ids,\n                    key=lambda cname, _lo=ex_x[\"logits_all\"]: _lo[cont_ids[cname]],\n                )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/att_mediation.py",
  "original_content": "                f\"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) \"\n                f\"a={_a['wrongtype_a']['break']:+.2f}(p{_a['wrongtype_a']['p_break']}) | \"\n                f\"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/\"",
  "new_content": "                f\"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) \"\n                f\"a={_a['wrongtype_a']['break']:+.2f}\"\n                f\"(p{_a['wrongtype_a']['p_break']}) | \"\n                f\"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/att_mediation.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/explore/att_mediation.py && uv run python scripts/explore/att_mediation.py --validate",
  "timeout": 120000
}
```

**Summary:** $ uv run ruff check scripts/explore/a...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
[validate] CONTENT-only: aim=0.000 con=1.000 int=0.000
[validate] AIM-only    : aim=1.000 con=0.000 int=0.000
[validate] linearity   : full=5.574819 recon=5.574819 |Δ|=8.88e-16
[validate] null flat   : mean=-0.0105 std=5.0381 |mean/std|=0.002
[validate] route recon : total=8.3316 attn=1.3 mlp=7.4316 direct=-0.4000 (true -0.4) route=mlp
[validate] arms zero   : transport=0 break=0 smd=0 → True
[validate] arms content: transport=1.138 smd=0 te=2.276→1.138 (2× survival halves TE) → True
[validate] arms refuse : slot_mass_delta=-0.1302 < 0 → True
[validate] arms break  : break=1.50 (exact) → True
[validate] ALL PASS
```

### Thinking

All validation checks are passing, including the existing tests which remain byte-identical across all metrics. The task is complete and ready to commit as an autonomous code change following the established pattern.

### Thinking

All tests pass and the new arm tests are green while existing validations reproduce their exact prior values, confirming byte-identical behavior. I'm committing the code now.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/explore/att_mediation.py && git commit -F - <<'EOF'\n✅ P-TYPE-SWAP --arms instrument: 3-stage ill-typed-term pipeline, validate green\n\n- att_mediation.py additive extension (λ one_way): ARM_BANKS\n  (sortal=animal, wrongtype_a/b=disjoint adjective banks), per-cell\n  matched-realized-norm displacements via the existing build_dirs.\n- arm_stage_metrics: SURVIVAL (‖Δresid‖ at edited slot, post-edit reader\n  layers) → TRANSPORT (UNPROJECTED ‖Δattn contribution‖ at readout; the\n  s287 w-projection-confound fix) → TE=transport/survival (separates\n  medium-death from join-refusal) + slot_mass (P-ATT-DIFF causal form)\n  + BREAK (src-continent margin degradation).\n- Null loop reused: per-stat one-sided p vs matched-norm random-add;\n  null_summary per cell; aggregate TE ladder + break + preds-stay-src.\n- --cells-from: pin landmark→tgt 1:1 from a prior run JSON (builtin\n  hash is process-salted → tgt selection irreproducible; flagged).\n- pick_pair uses crc32, not salted hash.\n- --validate extended: zero-arm exact, content plant (transport>0,\n  slot-mass fixed, 2× survival halves TE), join-withdrawal plant\n  (slot_mass_delta<0), BREAK exact. ALL PASS; prior tests byte-identical.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "instrument commit"
}
```

**Summary:** Git commit: instrument commit

**Output:**
```
Exit code: 0
Stdout:
[main 2f76812] ✅ P-TYPE-SWAP --arms instrument: 3-stage ill-typed-term pipeline, validate green
 1 file changed, 322 insertions(+), 7 deletions(-)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/; ps aux | grep att_mediation | grep -v grep | awk '{print $2, $3\"%cpu\"}'; tmux capture-pane -p -t main:1 | tail -4"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
verdict.log
74830 67.2%cpu
74828 0.0%cpu
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25851.94it/s]
```

### Thinking

The 32B model run is still progressing at 67% CPU usage after about an hour and twenty minutes, and it's looking like the route decomposition approach with hidden state capture is adding more computational overhead than the previous P-ATT-MED baseline, which completed in around 31 minutes with the same null forward count of 200—the extra work from MLP hooks and numpy operations is making this slower than expected.

I'm realizing the lack of progress output isn't a sign of failure; Python's stdout buffering through tee is holding the prints in the buffer, so they won't appear until the process finishes or flushes, which explains why the earlier 4B smoke test showed output immediately after completion. The process is genuinely still working through its 3700 forwards of the 68-token prompt, so there's no need to keep checking on it.

For the 4B smoke test with the arms flag, memory-wise it should be fine running alongside the 32B model since the precedent shows both fit on the machine before. I'll run it directly with a 600-second timeout rather than through tmux, accounting for MPS contention slowing things down. The command will invoke the attention mediation script on the 4B Qwen model with the arms flag and specific layer parameters.

The reader layers default to the full range (20–35) which matches what the 4B smoke test used, and I need to explicitly pass the output directory since the default differs. I should also include the route decomposition flag to capture MLP transport per arm—it's cheap to add and aligns with what the 4B FFN smoke test did, plus the arms printing is already handled separately. The output path will mark this as a smoke test.

For the cell count, I'm weighing the trade-offs: the earlier 4B tests used 6 cells for P-ATT-MED and 18 for P-ATT-FFN, but for this arms smoke I want something in between that gives enough signal for the type comparisons without creating contention with the running 32B verdict. I'll go with 12 cells and 30 null entries as a compromise—it's richer than the minimal 6 but still conservative given the resource constraints, and I can always run a more detailed version later if needed.

For execution, I'm keeping it simple: run this in the foreground with a 10-minute timeout rather than backgrounding it. The job should only take a few minutes, and the straightforward approach is cleaner than trying to manage async verification and checkpointing.

### Thinking

I've committed the instrument and the 32B verdict is still running as expected. Now I'm launching the 4B task in the background, which has shown similar behavior in previous runs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && mkdir -p results/type-swap/qwen3-4b && uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-4B --device mps --arms --route-decomp --ref-layer 9 --swap-layer 20 --n-cells 6 --n-null 30 --out results/type-swap/qwen3-4b 2>&1 | tee results/type-swap/qwen3-4b/smoke.log",
  "background": "type-swap-4b-smoke"
}
```

**Summary:** $ mkdir -p results/type-swap/qwen3-4b...

**Output:**
```
Background job job-1 started.
Command: cd /Users/mwhitford/src/verbum && mkdir -p results/type-swap/qwen3-4b && uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-4B --device mps --arms --route-decomp --ref-layer 9 --swap-layer 20 --n-cells 6 --n-null 30 --out results/type-swap/qwen3-4b 2>&1 | tee results/type-swap/qwen3-4b/smoke.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.
```

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-swap-4b-smoke" (job-1)

**Output:**
```
Job "type-swap-4b-smoke" (job-1) — running

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 26499.87it/s]
```

### Thinking

The async job has all weights loaded and is running as expected. I'll emit the checkpoint signal and give Michael a quick status update—the smoke test should complete in a couple minutes depending on system load.

## Assistant

**ASYNC: job-1 (type-swap-4b-smoke) verified running** (weights 398/398 loaded, running beside the 32B verdict). Waiting for signal.

Session state while both runs cook:

| | Status |
|---|---|
| P-TYPE-SWAP pre-reg | ✅ approved + committed (`1bbdf57`) |
| `--arms` instrument | ✅ built, lint-clean, `--validate` ALL PASS, committed (`2f76812`) — prior tests byte-identical |
| 4B arms smoke | ▶ in flight (job-1, ~2–5 min under contention) |
| P-ATT-FFN 32B verdict | ▶ still in flight (main:1, ~80 min — stdout buffered, process healthy at 67% CPU) |

Design notes that made it into the build, beyond the pre-reg text:

- **The TE normalization is the load-bearing piece**: `TRANSPORT/SURVIVAL` separates "the ill-typed edit died in the medium before the reader ever saw it" from "it arrived and the join refused it." Without that, a wrong-type transport deficit would be uninterpretable. The `--validate` plant confirms 2× survival → ½ TE exactly.
- **`slot_mass` is P-ATT-DIFF smuggled in**: mean readout-query attention onto the edited slot, per arm — "does the reader withdraw its edge from an ill-typed term" is measured directly, with `p_slot_drop` against the random-add distribution.
- **Reproducibility fix**: discovered the harness's `hash(lm)` target selection is process-salted — cell targets are *not* stable across runs. Arms use `crc32`, and `--cells-from results/type-att-med/qwen3-32b/att_mediation.json` will pin the 32B verdict run to the exact P-ATT-MED cells for the 1:1 mapping the pre-reg promises. Worth knowing: the P-ATT-MED → P-ATT-FFN "same cells" comparison already relies on the recorded JSONs, not on re-derivation.

When the smoke returns I'll read the TE ladder / break / preds advisory; when the 32B P-ATT-FFN lands I'll score its frozen gates and draft §Result-32B for your approval. Both results will come to you before anything further moves.

## User

job is done


### Thinking

I need to check the output from job-1 to see the 4B arms smoke results, and verify whether the 32B P-ATT-FFN model has finished running.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-swap-4b-smoke" (job-1)

**Output:**
```
Job "type-swap-4b-smoke" (job-1) — completed (exit 0)

[att-med] Qwen/Qwen3-4B L=9 lb=20 scale=2.0 dev=mps H=32 n_kv=8 hd=128 layers=36 reader=20..35
[att-med] using 6 install-correct cells: ['Colosseum', 'Louvre', 'Parthenon', 'Kremlin', 'Sagrada Familia', 'Brandenburg Gate']
[type-swap] Colosseum        te same=2.17 sortal=1.97 wtA=1.91 wtB=1.72 null=1.65 | smΔ s=-0.0013 a=-0.0042 | brk s=-3.12(p0.767) a=-2.75(p0.733) | pred Europe/Europe/Europe
[att-ffn] Colosseum        flip=1 route=mlp  attn=0.263 mlp=0.735 direct=0.002 recon_err=0.002 p_mlp=0.0 pk=33/34
[type-swap] Louvre           te same=1.64 sortal=1.51 wtA=1.11 wtB=1.53 null=1.47 | smΔ s=+0.0014 a=-0.0025 | brk s=+8.75(p0.033) a=+2.00(p0.8) | pred Europe/Europe/Europe
[att-ffn] Louvre           flip=1 route=mlp  attn=0.289 mlp=0.71 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=32/34
[type-swap] Parthenon        te same=1.89 sortal=1.87 wtA=1.64 wtB=1.56 null=1.63 | smΔ s=+0.0028 a=+0.0002 | brk s=-4.12(p1.0) a=+4.25(p0.1) | pred Europe/Europe/Europe
[att-ffn] Parthenon        flip=1 route=mlp  attn=0.177 mlp=0.822 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=32/36
[type-swap] Kremlin          te same=1.58 sortal=1.30 wtA=1.31 wtB=1.28 null=1.37 | smΔ s=-0.0097 a=-0.0038 | brk s=+4.25(p0.033) a=+0.88(p0.6) | pred Asia/Europe/Asia
[att-ffn] Kremlin          flip=1 route=mlp  attn=0.145 mlp=0.855 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=32/34
[type-swap] Sagrada Familia  te same=1.95 sortal=1.48 wtA=1.57 wtB=1.47 null=1.55 | smΔ s=-0.0112 a=+0.0035 | brk s=+5.88(p0.167) a=+2.50(p0.933) | pred Europe/Europe/Asia
[att-ffn] Sagrada Familia  flip=1 route=mlp  attn=0.423 mlp=0.577 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=33/34
[type-swap] Brandenburg Gate te same=2.09 sortal=1.69 wtA=1.52 wtB=1.20 null=1.39 | smΔ s=-0.0003 a=-0.0013 | brk s=-1.38(p1.0) a=-1.25(p1.0) | pred Europe/Europe/Europe
[att-ffn] Brandenburg Gate flip=1 route=mlp  attn=0.37 mlp=0.629 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=30/34

[att-med] AGG (flipped cells): aim=0.12 content=0.755 inter=0.124 content_dominant=True mean_p=0.0
[type-swap] ARM TE ladder: same=1.89 sortal=1.64 wrongtype_a=1.51 wrongtype_b=1.46 | ordering same>sortal>wrong = True
[type-swap] ARM break: same=+18.88 sortal=+1.71 wrongtype_a=+0.94 wrongtype_b=+2.29 | preds-stay-src: same=0/6 sortal=5/6 wrongtype_a=6/6 wrongtype_b=4/6
[att-ffn] ROUTE SPLIT: attn-dom=0 mlp-dom=6 mlp-cells=['Colosseum', 'Louvre', 'Parthenon', 'Kremlin', 'Sagrada Familia', 'Brandenburg Gate'] mean_recon_err=0.001
[p-type-swap] wrote results/type-swap/qwen3-4b/type_swap.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/ /Users/mwhitford/src/verbum/results/type-swap/qwen3-4b/"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/results/type-att-ffn/qwen3-32b/:
verdict.log

/Users/mwhitford/src/verbum/results/type-swap/qwen3-4b/:
smoke.log
type_swap.json
```

### Thinking

The 4B arms smoke test completed successfully—all 6 cells ran across both arms with JSON output and clean exits. The same-type replicates all flipped as expected, confirming the flip mechanism is working correctly, and the content-dominant replicates show strong P-ATT-MED consistency at 0.755 versus 0.12.

Looking at the transfer entropy ladder across the aggregate: same-type sits highest at 1.89, sortal in the middle at 1.64, and both wrong-type variants cluster near the null baseline around 1.5. This is exactly the predicted hierarchy—same-type transports well above random noise, wrong-type performs at the null floor (essentially random), and sortal sits in between as a graded intermediate, which matches the P3 prediction for the sortal hierarchy. The join-typed signature is showing through at the transport stage, though with the caveat that this is advisory only given the small sample size of 6 cells and 30 null replicates.

For the break row, same-type shows a massive shift of +18.88 as expected, while the wrong-type variants show minimal changes around +1–2.3, with most p-values above 0.05. The key finding is that ill-typed edits are largely ignored downstream—the chain preserves its original continent in most cases: sortal keeps it in 5 of 6 cells, wtA in all 6, and wtB in 4 of 6. The two cells where wtB changed prediction are interesting edge cases, like Kremlin where the sortal variant flipped the prediction to Asia despite Russia being mapped as Europe, suggesting the boundary noise is affecting the output.

Looking at slot attention mass, the deltas are tiny and mixed (ranging from −0.011 to +0.003), with no clear signal that the reader withdraws attention from ill-typed slots. This suggests the transport deficit isn't driven by attention reallocation—instead, the join carries less wrong-type content at roughly equal weights, which points to a refusal mechanism operating at the content level rather than the edge level. The discipline appears to kick in at the transport stage, where the ordering effect (same > sortal > wrong ≈ random) becomes visible.

The edges themselves stay stable while the payload flowing through them gets type-filtered—a middle ground where the join's structure is fixed but what propagates is discriminated. I'm wondering whether the magnitude of attention contribution changes depends on how much the edit altered the slot values downstream, and whether the medium between the edit location and the reader differentially attenuates those changes.

Actually, SURVIVAL normalizes for that attenuation by measuring the surviving perturbation at the slot across reader layers, so transport efficiency becomes the attention delivery per unit of surviving residual. That ordering—same-type perturbation delivering more than wrong-type or random—suggests the OV channel preferentially reads class-aligned content, which confirms the typed-read hypothesis.

I need to pull the p_te values from the JSON output for each cell, since the printed summary doesn't include them, and I should aggregate those for the advisory.

## Assistant

Smoke's back — pulling the aggregate detail before reading it out:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nd = json.load(open('results/type-swap/qwen3-4b/type_swap.json'))\nagg = d['aggregate']['arms']\nfor name, a in agg.items():\n    print(f\\\"{name:12s} surv={a['mean_survival']:8.2f} tr={a['mean_transport']:8.2f} te={a['mean_te']:.3f} \\\"\n          f\\\"p_tr={a['mean_p_transport']:.3f} p_te={a['mean_p_te']:.3f} smΔ={a['mean_slot_mass_delta']:+.4f} \\\"\n          f\\\"brk={a['mean_break']:+.2f} p_brk={a['mean_p_break']:.3f} stay_src={a['n_pred_stays_src']}/6\\\")\nc0 = d['cells'][0]\nprint('null te mean/std (cell0):', c0['null_summary']['te'])\nprint('per-cell p_te same:', [c['arms']['same']['p_te'] for c in d['cells']])\nprint('per-cell p_te sortal:', [c['arms']['sortal']['p_te'] for c in d['cells']])\nprint('per-cell p_te wtA:', [c['arms']['wrongtype_a']['p_te'] for c in d['cells']])\nprint('per-cell p_te wtB:', [c['arms']['wrongtype_b']['p_te'] for c in d['cells']])\nprint('edit_norms:', [c['edit_norm'] for c in d['cells']])\n\""
}
```

**Summary:** $ uv run python -c " import json d = ...

**Output:**
```
Exit code: 0
Stdout:
same         surv=  149.33 tr=  279.75 te=1.889 p_tr=0.000 p_te=0.033 smΔ=-0.0014 brk=+18.88 p_brk=0.000 stay_src=0/6
sortal       surv=  138.69 tr=  225.77 te=1.637 p_tr=0.072 p_te=0.311 smΔ=-0.0031 brk=+1.71 p_brk=0.500 stay_src=5/6
wrongtype_a  surv=  141.83 tr=  211.55 te=1.510 p_tr=0.178 p_te=0.444 smΔ=-0.0013 brk=+0.94 p_brk=0.694 stay_src=6/6
wrongtype_b  surv=  143.89 tr=  208.95 te=1.461 p_tr=0.178 p_te=0.605 smΔ=-0.0060 brk=+2.29 p_brk=0.400 stay_src=4/6
null te mean/std (cell0): {'mean': 1.6481, 'std': 0.1615}
per-cell p_te same: [0.0, 0.1, 0.067, 0.033, 0.0, 0.0]
per-cell p_te sortal: [0.033, 0.3, 0.067, 0.733, 0.7, 0.033]
per-cell p_te wtA: [0.033, 1.0, 0.4, 0.633, 0.433, 0.167]
per-cell p_te wtB: [0.267, 0.3, 0.6, 0.833, 0.733, 0.9]
edit_norms: [71.94, 85.09, 78.17, 83.31, 79.85, 80.43]
```

### Thinking

Looking at the survival metrics across different edit types—same-type, sortal, and wrong-type—they're all performing equally well regardless of whether changes stay on-manifold or not. Even random edits show comparable survival rates, which suggests the medium itself doesn't discriminate based on edit type, confirming the prediction that on-manifold status doesn't meaningfully affect survival outcomes.

The transport and TE metrics tell a different story though: same-type edits show the strongest transport efficiency at 1.889, followed by sortal at 1.637, with wrong-type and random clustering near null performance around 1.46. This creates a clear monotone hierarchy where the join preferentially moves well-typed displacement relative to surviving perturbations.

Slot mass remains essentially flat across all conditions, indicating the reader isn't withdrawing its edge—refusal isn't coming from the aim side, just fixed edges with filtered payload. The break and output metrics show same-type edits producing significant coherent changes (+18.88, p < 0.001 with all six flips), while ill-typed edits produce no meaningful output shift and predictions stay locked to source values. The ill-typed content survives the medium but gets delivered at noise-level efficiency, producing no coherent output signal—so at this scale, the type discipline gates the transport stage with fixed aim, where the OV channel preferentially delivers well-typed content while ill-typed material is effectively ignored.

The deflationary manifold account breaks down here: wrong-type on-manifold content doesn't transport like regular content and doesn't interfere with output, contradicting the prediction. Some caveats though—the sample is small (n=6 cells, n_null=30), the sortal and wrong-type positions aren't individually significant against null, and there's a noted leak in the sortal domain plus some timing contention with the 32B run. Sortal sits at intermediate transport efficiency, suggesting it's a graded phenomenon where right-type wrong-domain content moves at reduced but measurable efficiency.

Now I need to wrap up task 3, commit the results autonomously, update the state block, and report to Michael. The 32B verdict is ready to go but the P-ATT-FFN box is still busy, so I should wait for that to finish before running with the cells pinning. I'm committing both results and state with a green smoke indicator—using the checkmark symbol since this is a clean instrument result—and tagging it with the type-swap label and the TE ladder monotonicity finding.

Appending the state update to the s287 block.

### Thinking

The advisory looks good for a smoke test. I'm committing the results and state, then reading the output.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> P-ATT-FFN 32B verdict STILL IN FLIGHT (tmux main:1, launched 11:00) — read\n> results/type-att-ffn/qwen3-32b/att_ffn.json when done, score frozen gates.",
  "new_content": "> P-ATT-FFN 32B verdict STILL IN FLIGHT (tmux main:1, launched 11:00) — read\n> results/type-att-ffn/qwen3-32b/att_ffn.json when done, score frozen gates.\n> ✅ INSTRUMENT BUILT+COMMITTED (2f76812, --arms + --cells-from; --validate ALL PASS,\n> prior tests byte-identical; ⚠ found harness tgt-selection uses SALTED hash(lm) —\n> irreproducible across processes; arms use crc32; 32B verdict MUST use --cells-from\n> results/type-att-med/qwen3-32b/att_mediation.json for the 1:1 cell mapping).\n> ✅ 4B ARMS SMOKE GREEN (job beside 32B run, ~4 min, results/type-swap/qwen3-4b/):\n> ADVISORY = the JOIN-TYPED signature, content-side: SURVIVAL flat across arms\n> (138–149, medium is type-blind) → TE ladder MONOTONE same=1.89 (p_te 0.033) >\n> sortal=1.64 (0.31) > wtA=1.51 (0.44) > wtB=1.46 (0.61) ≈ null → slot_mass Δ≈0\n> every arm (reader NEVER withdraws the edge — refusal is NOT aim-side) → BREAK:\n> same +18.9 flips 6/6 (p 0.000), ill-typed arms ≈ null (p 0.4–0.7), preds-stay-src\n> 15/18. Reading: fixed edges, FILTERED PAYLOAD — the OV/content channel delivers\n> well-typed displacement preferentially; ill-typed on-manifold content survives the\n> medium at full strength but transports at random-noise efficiency and is ignored\n> at the output. Manifold-membership account FAILS its 4B prediction (wrong-type ≁\n> content). Sortal sits BETWEEN (graded hierarchy hint, P3). NOT the verdict:\n> n=6, n_null=30, 4B host. ▶ 32B VERDICT ON GO (after P-ATT-FFN frees the box):\n> uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device\n> mps --arms --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18\n> --n-null 200 --cells-from results/type-att-med/qwen3-32b/att_mediation.json\n> --out results/type-swap/qwen3-32b."
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
  "command": "git add results/type-swap/qwen3-4b mementum/state.md && git commit -F - <<'EOF'\n✅ P-TYPE-SWAP 4B smoke: TE ladder monotone, ill-typed ≈ null, aim fixed\n\n- 6/6 cells, all arms, beside the 32B P-ATT-FFN run (~4 min); same-type\n  positive control replicates (flips 6/6, content-dominant 0.755 agg).\n- SURVIVAL flat across arms (138-149): the medium is type-blind.\n- TE ladder monotone: same 1.889 (p_te 0.033) > sortal 1.637 (0.311) >\n  wtA 1.510 (0.444) > wtB 1.461 (0.605) ≈ random-add null.\n- slot_mass_delta ≈ 0 every arm: the reader never withdraws the edge —\n  refusal is content-side, not aim-side (coheres with medium-handle).\n- BREAK: same +18.88 (p 0.000); ill-typed arms ≈ null (p 0.4-0.7),\n  preds-stay-src 15/18 — ill-typed edits ignored at the output.\n- Advisory reading: JOIN-TYPED in the content sub-channel — fixed edges,\n  filtered payload. Manifold-membership fails its 4B prediction.\n- NOT the verdict (n=6, n_null=30, 4B host). 32B on GO with --cells-from.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "smoke results commit"
}
```

**Summary:** Git commit: smoke results commit

**Output:**
```
Exit code: 0
Stdout:
[main 010bfb7] ✅ P-TYPE-SWAP 4B smoke: TE ladder monotone, ill-typed ≈ null, aim fixed
 3 files changed, 1369 insertions(+)
 create mode 100644 results/type-swap/qwen3-4b/smoke.log
 create mode 100644 results/type-swap/qwen3-4b/type_swap.json
```

### Thinking

I'm sending this to Michael with a note that it's advisory, though the visual is compelling. I should also flag that P-ATT-FFN is still in progress and we're waiting on the 32B GO decision.

## Assistant

## 4B smoke: green, and the advisory picture is striking

**Instrument gates all pass** — 6/6 cells, same-type control replicates (flips 6/6, content-dominant 0.755, exactly the P-ATT-MED profile). Committed (`010bfb7`). Here's the three-stage read:

| stage | same-type | sortal | wrong-A | wrong-B | random null |
|---|---|---|---|---|---|
| **SURVIVAL** | 149 | 139 | 142 | 144 | ~same |
| **TE** (transport/survival) | **1.89** (p .033) | 1.64 (p .31) | 1.51 (p .44) | 1.46 (p .61) | ~1.5 |
| **slot-mass Δ** | ≈0 | ≈0 | ≈0 | ≈0 | — |
| **BREAK** (output) | **+18.9** (p .000) | +1.7 (p .50) | +0.9 (p .69) | +2.3 (p .40) | ~0 |
| preds stay src | 0/6 (flips) | 5/6 | 6/6 | 4/6 | — |

**The advisory reading — a JOIN-TYPED signature, but content-side:**

1. **The medium is type-blind.** Survival is flat across all arms — the ill-typed edits reach the reader at full strength. Nothing died en route.
2. **The join filters the payload.** The TE ladder is monotone exactly as the sortal hierarchy predicted: `same > sortal > wrong ≈ random`. Per unit of surviving perturbation, attention delivers well-typed displacement above the null and ill-typed displacement *at noise efficiency*.
3. **The edge never moves.** slot-mass delta ≈ 0 in every arm — the reader does not withdraw attention from an ill-typed slot. Refusal is not aim-side. Fixed edges, **filtered payload** — coherent with medium-handle/fixed-aim rather than in tension with it.
4. **The output ignores what the join didn't deliver.** BREAK ≈ null for all ill-typed arms; predictions stay on the source continent 15/18. No manifold-style interference.

**And the induction's deflationary counter took real damage:** manifold-membership predicted on-manifold wrong-type content transports like content. It doesn't — it transports like random noise. At 4B, at least, the thing discriminating is the *class*, not the manifold.

The sortal arm sitting cleanly *between* (1.64 — above wrong-type, below same) is the graded-hierarchy hint from P3: right type, wrong domain gets partial transport. If that survives at 32B with the permutation stats, it's a measured sortal ladder.

**Caveats stand:** n=6, n_null=30, 4B is not the verdict host, and sortal/wrong arms aren't individually distinguishable from each other at this n — the verdict statistic is the cell-permutation over 18 cells at 32B.

**Status:** P-ATT-FFN 32B is still grinding on main:1 (~2h now; buffered output, process healthy). The 32B P-TYPE-SWAP verdict command is staged in state.md — it needs the box free and uses `--cells-from .../att_mediation.json` to pin the exact P-ATT-MED cells (I found the harness's target selection uses Python's salted hash — not reproducible across processes — so pinning is mandatory for the 1:1 mapping the pre-reg promises).

**On your GO once the box frees:** launch the 32B verdict. Or if you'd rather see the P-ATT-FFN verdict scored first and decide then, that's the order the queue already implies.

## User

P-ATT-FFN is done.


### Thinking

I'm reading through the P-ATT-FFN 32B results to check the verdict on frozen gates, specifically looking at whether the FFN-retrieval and mixed-route conditions are met based on the Sphinx and Petronas MLP-dominant patterns and attention-null behavior.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tail -25 results/type-att-ffn/qwen3-32b/verdict.log"
}
```

**Summary:** $ tail -25 results/type-att-ffn/qwen3...

**Output:**
```
Exit code: 0
Stdout:
Loading weights:   0%|          | 0/707 [00:00<?, ?it/s]Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25851.94it/s]
[att-med] Qwen/Qwen3-32B L=9 lb=25 scale=2.0 dev=mps H=64 n_kv=8 hd=128 layers=64 reader=25..63
[att-med] using 18 install-correct cells: ['Colosseum', 'Louvre', 'Parthenon', 'Kremlin', 'Sagrada Familia', 'Brandenburg Gate', 'Taj Mahal', 'Kaaba', 'Petronas Towers', 'Angkor Wat', 'Tiananmen', 'Burj Khalifa', 'Pyramids', 'Sphinx', 'Karnak', 'Table Mountain', 'Medina', 'Victoria Falls']
[att-ffn] Colosseum        flip=1 route=mlp  attn=0.389 mlp=0.61 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=59/61
[att-ffn] Louvre           flip=1 route=mlp  attn=0.304 mlp=0.696 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=51/61
[att-ffn] Parthenon        flip=1 route=mlp  attn=0.243 mlp=0.757 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=59/61
[att-ffn] Kremlin          flip=1 route=mlp  attn=0.421 mlp=0.576 direct=0.003 recon_err=0.003 p_mlp=0.0 pk=59/43
[att-ffn] Sagrada Familia  flip=1 route=attn attn=0.533 mlp=0.466 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=52/51
[att-ffn] Brandenburg Gate flip=1 route=mlp  attn=0.245 mlp=0.755 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=53/1
[att-ffn] Taj Mahal        flip=1 route=mlp  attn=0.484 mlp=0.515 direct=0.002 recon_err=0.002 p_mlp=0.0 pk=59/60
[att-ffn] Kaaba            flip=0 route=mlp  attn=0.209 mlp=0.789 direct=0.002 recon_err=0.002 p_mlp=0.0 pk=59/60
[att-ffn] Petronas Towers  flip=1 route=attn attn=0.596 mlp=0.399 direct=0.005 recon_err=0.005 p_mlp=0.01 pk=8/54
[att-ffn] Angkor Wat       flip=1 route=attn attn=0.572 mlp=0.427 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=21/60
[att-ffn] Tiananmen        flip=1 route=mlp  attn=0.485 mlp=0.511 direct=0.003 recon_err=0.003 p_mlp=0.0 pk=59/60
[att-ffn] Burj Khalifa     flip=1 route=mlp  attn=0.435 mlp=0.564 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=53/61
[att-ffn] Pyramids         flip=1 route=mlp  attn=0.357 mlp=0.642 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=58/61
[att-ffn] Sphinx           flip=1 route=mlp  attn=0.235 mlp=0.759 direct=0.005 recon_err=0.005 p_mlp=0.0 pk=52/58
[att-ffn] Karnak           flip=1 route=mlp  attn=0.345 mlp=0.655 direct=0.0 recon_err=0.0 p_mlp=0.0 pk=58/61
[att-ffn] Table Mountain   flip=0 route=mlp  attn=0.423 mlp=0.577 direct=0.001 recon_err=0.001 p_mlp=0.0 pk=57/59
[att-ffn] Medina           flip=1 route=mlp  attn=0.413 mlp=0.58 direct=0.008 recon_err=0.008 p_mlp=0.155 pk=4/58
[att-ffn] Victoria Falls   flip=1 route=attn attn=0.565 mlp=0.433 direct=0.002 recon_err=0.002 p_mlp=0.005 pk=59/59

[att-med] AGG (flipped cells): aim=0.174 content=0.756 inter=0.07 content_dominant=True mean_p=0.006
[att-ffn] ROUTE SPLIT: attn-dom=4 mlp-dom=12 mlp-cells=['Colosseum', 'Louvre', 'Parthenon', 'Kremlin', 'Brandenburg Gate', 'Taj Mahal', 'Tiananmen', 'Burj Khalifa', 'Pyramids', 'Sphinx', 'Karnak', 'Medina'] mean_recon_err=0.002
[att-ffn] wrote results/type-att-ffn/qwen3-32b/att_ffn.json
```

### Thinking

I'm evaluating the 32B P-ATT-FFN model's performance across frozen gates, starting with P1 which checks whether the FFN retrieval is confirmed through Sphinx and Petronas showing MLP dominance with statistical significance and clean dissociation between attention and MLP failures. The Sphinx results show the MLP routing at 0.759 with p-value of 0, indicating strong evidence.

However, Petronas breaks the pattern—it's routing to attention (0.596) rather than MLP (0.399), with p_mlp=0.01, so P1 fails since only half the cells meet the criteria. The dissociation also doesn't hold cleanly since the MLP-dominant set spans 12 cells rather than just the 2 null-misses.

Looking at the broader mixed-route pattern, I'm seeing 4 attention-dominant cells and 12 MLP-dominant cells across the flipped dataset, with the MLP channel beating null in nearly all cases except Medina (p_mlp=0.155), while the attention channel shows strong null-beating across the board with a mean p-value around 0.006.

For P2 on depth ordering, most cells show country-level peaks before continent-level peaks (composition order), with values like 59/61 and 51/61, but the attention-dominant cells like Petronas (8/54) and Angkor (21/60) resolve country information much earlier, suggesting either early composition or a degenerate lens artifact—Brandenburg's continent peak at layer 1 looks particularly suspicious as a boundary effect.

The key finding is that the predicted-cells tension actually contradicts P1 in the way the 4B contrast predicted: Sphinx flipped from attention-dominant to MLP-dominant (0.759) while Petronas remained attention-dominant (0.596), so the two null-misses split in opposite directions rather than staying aligned, confirming the mixed-route verdict.

Looking at the overall composition, the country-to-continent flip is predominantly MLP-driven (around 60% of the effect) with attention contributing roughly 37%, even though the attention register itself shows strong content-dominance (0.756 within the attention channel). So both observations hold: attention beats its null baseline AND the MLP pathway carries the larger share of the actual transformation.

The Sphinx case confirms Michael's FFN-fact-lookup hypothesis — its flip is 76% MLP-dependent, which aligns with the earlier finding that Sphinx had minimal attention magnitude (1.49) at P-ATT-MED. Petronas is the puzzle: it shows attention-dominance in the route decomposition (0.596) but had a weak p-value (0.11) in the P-ATT-MED analysis, which could stem from different experimental runs or variations in the target countries being captured.

I need to verify whether the cells actually match between the two runs by comparing the target countries per landmark in their respective JSONs — the hash-salting means the landmark list is consistent but the target assignments could differ. Once I confirm the cells align, I'll aggregate the attention channel statistics from the JSON, compute the mean MLP fraction, then draft the 32B results section and commit it.

### Thinking

I've got the verdict and now need to verify the cell-identity caveat about the salted hash and target countries, plus check the per-cell attention-channel p-values before scoring.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nmed = json.load(open('results/type-att-med/qwen3-32b/att_mediation.json'))\nffn = json.load(open('results/type-att-ffn/qwen3-32b/att_ffn.json'))\nmc = {c['landmark']: c for c in med['cells']}\nfc = {c['landmark']: c for c in ffn['cells']}\nmismatch = [(lm, mc[lm]['tgt_country'], fc[lm]['tgt_country']) for lm in mc if lm in fc and mc[lm]['tgt_country'] != fc[lm]['tgt_country']]\nprint('tgt mismatches vs P-ATT-MED:', mismatch if mismatch else 'NONE — cells match 1:1')\nprint()\nflipped = [c for c in ffn['cells'] if c['flipped']]\nprint(f\\\"flipped {len(flipped)}/18; attn p_vs_null<0.05: {sum(1 for c in flipped if c['p_vs_null']<0.05)}/16; mlp p<0.05: {sum(1 for c in flipped if c['p_mlp_vs_null']<0.05)}/16\\\")\nprint('mean mlp_frac (flipped):', round(sum(c['mlp_frac_of_total'] for c in flipped)/len(flipped),3))\nprint('mean attn_frac (flipped):', round(sum(c['attn_frac_of_total'] for c in flipped)/len(flipped),3))\nprint('composition_order true:', sum(1 for c in flipped if c['composition_order']), '/16')\nprint()\nfor lm in ['Sphinx','Petronas Towers']:\n    m, f = mc[lm], fc[lm]\n    print(f\\\"{lm}: MED attn_total={m['attn_total']} p={m['p_vs_null']} | FFN route={f['route']} attn={f['attn_frac_of_total']} mlp={f['mlp_frac_of_total']} p_mlp={f['p_mlp_vs_null']} p_attn={f['p_vs_null']} pk={f['pk_country']}/{f['pk_cont']}\\\")\nprint()\nattn_dom = [c['landmark'] for c in flipped if c['route']=='attn']\nprint('attn-dominant cells:', attn_dom)\nprint('agg route:', json.dumps(ffn['aggregate']['route']))\n\""
}
```

**Summary:** $ uv run python -c " import json med ...

**Output:**
```
Exit code: 0
Stdout:
tgt mismatches vs P-ATT-MED: [('Colosseum', 'Cambodia', 'Zambia'), ('Louvre', 'Malaysia', 'China'), ('Parthenon', 'Morocco', 'UAE'), ('Kremlin', 'Malaysia', 'China'), ('Sagrada Familia', 'Morocco', 'Zambia'), ('Brandenburg Gate', 'Cambodia', 'Saudi Arabia'), ('Taj Mahal', 'Russia', 'Zambia'), ('Kaaba', 'Egypt', 'France'), ('Petronas Towers', 'Italy', 'Zambia'), ('Angkor Wat', 'Morocco', 'Zambia'), ('Burj Khalifa', 'Greece', 'South Africa'), ('Sphinx', 'India', 'Greece'), ('Karnak', 'Spain', 'Malaysia'), ('Table Mountain', 'China', 'Russia'), ('Medina', 'Greece', 'India'), ('Victoria Falls', 'Spain', 'China')]

flipped 16/18; attn p_vs_null<0.05: 15/16; mlp p<0.05: 15/16
mean mlp_frac (flipped): 0.584
mean attn_frac (flipped): 0.414
composition_order true: 12 /16

Sphinx: MED attn_total=1.4925 p=0.815 | FFN route=mlp attn=0.235 mlp=0.759 p_mlp=0.0 p_attn=0.075 pk=52/58
Petronas Towers: MED attn_total=14.9192 p=0.11 | FFN route=attn attn=0.596 mlp=0.399 p_mlp=0.01 p_attn=0.0 pk=8/54

attn-dominant cells: ['Sagrada Familia', 'Petronas Towers', 'Angkor Wat', 'Victoria Falls']
agg route: {"n_attn_dominant": 4, "n_mlp_dominant": 12, "mlp_dominant_cells": ["Colosseum", "Louvre", "Parthenon", "Kremlin", "Brandenburg Gate", "Taj Mahal", "Tiananmen", "Burj Khalifa", "Pyramids", "Sphinx", "Karnak", "Medina"], "mean_recon_err": 0.002, "mean_attn_frac_of_total": 0.414, "mean_mlp_frac_of_total": 0.584, "mixed_route": true}
```

### Thinking

I'm seeing a critical mismatch in the landmark-to-target mappings — 16 out of 18 pairs diverge from the reference P-ATT-MED run, even though we used identical cells and configuration. The protocol specified that the route split should map one-to-one with the P-ATT-MED verdict cells, but the swap targets ended up different despite matching landmarks and settings. This needs to be flagged as a protocol deviation affecting the lambda measure and coherence calculations.

The deviation weakens the P1 gate scoring since P1 hinges on whether the attention-null-misses (Sphinx and Petronas) are MLP-dominant — but those null-misses were defined on different swap edits here. The per-cell mapping is now approximate rather than exact. Looking at the honest scoring: P1 fails regardless because Petronas shows attention-dominance (0.596) rather than MLP-dominance, and the dissociation clean clause breaks badly with 12 MLP-dominant cells instead of just 2. The MIXED-ROUTE-MEASURED verdict holds true — both routes present with both channels null-beating at p<0.05, matching what the 4B contrast predicted. Reconstruction error stays at 0.002, so the decomposition-completeness gate passes. For P2 depth-order, composition order hits 12 out of 16, and the attention-dominant Petronas cell shows partial depth ordering.

Now examining why Kaaba and Table Mountain didn't flip in this run despite the P-ATT-MED baseline flipping all 18 — the target countries differ, making the swap difficulty different, which coheres with the cell-identity analysis.

The verdict remains MIXED-ROUTE since the gating mechanism doesn't hinge on cell identity with P-ATT-MED, but rather on route presence and null-beating within this specific run. The P1/FFN-RETRIEVAL gate scored FAILED, though I'm flagging a deviation: I could retest the two null-miss cells with matching targets using --cells-from as a cheap optional follow-up. Notably, Sphinx shows MLP dominance at 32B (0.759), aligning with the fact-lookup pattern, while Petronas splits toward attention-dominant with minimal attention probability.

Michael's hypothesis holds at the cell level and fully at the route level—the FFN fact-map is real and carries the majority of the flip (0.584 mean), beating null in 15 out of 16 cases. The route split is remarkably scale-stable: the 4B model shows 11 out of 14 MLP-dominant cells with mean 0.586, nearly identical to the 32B's 12 out of 16 with 0.584. The composed picture breaks down to roughly 58% MLP and 41% attention overall, with attention further split between content (0.756) and aim (0.174), replicating the earlier P-ATT-MED aggregation pattern.

Now I need to draft the Result-32B section to replace the "RUN IN FLIGHT" placeholder, update the state block, and commit the results autonomously, with the knowledge page and state updates going into the pending-approval batch for Michael.

## Assistant

**The salted-hash bug bit this run** — 16/18 target countries differ from the P-ATT-MED run of record (e.g., Sphinx→India there, Sphinx→Greece here). Same landmarks, same config, different swap edits. That's a **protocol deviation against the pre-reg's "cells map 1:1" clause** and it gets recorded verbatim — it's also why 2 cells didn't flip this time. The route-split verdict is unaffected (it's internal to this run), but the P1 cell-level dissociation gate must be read with that caveat. Scoring the frozen gates:

- **P1 FFN-RETRIEVAL-CONFIRMED: ✗ FAILS.** Sphinx is MLP-dominant (0.759, p_mlp=0.0 ✓) but Petronas is attention-dominant (0.596 ✗); and the MLP-dominant set is 12 cells, not the 2 null-misses — no clean dissociation.
- **MIXED-ROUTE-MEASURED: ✓ TRUE.** 4 attn-dominant + 12 MLP-dominant among 16 flipped; attention channel beats null 15/16, MLP channel beats null 15/16; mean_recon_err 0.002 (completeness gate passes — the norm_f fix held at 32B).
- **P2 (gated-with-P1): verbatim only** — composition order 12/16.

Drafting §Result-32B on the page, committing results autonomously:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "## P-ATT-FFN — Result @32B — RUN IN FLIGHT (s286, tmux main:1)\n\nVerdict launched on Michael GO (s286): Qwen3-32B, `--route-decomp`, install L9, swap L25,\nscale 2.0, reader L25–63, 18 cells, n_null 200 → `results/type-att-ffn/qwen3-32b/att_ffn.json`.\nVerified running (weights 707/707). **No verdict recorded yet.** On completion, read\n`aggregate.route` (n_attn_dominant vs n_mlp_dominant, `mlp_dominant_cells`,\n`mean_recon_err` must be small) and score the frozen gates: **FFN-RETRIEVAL-CONFIRMED**\n⟺ Sphinx AND Petronas MLP-dominant + MLP beats null; **MIXED-ROUTE-MEASURED** ⟺ both\nroutes present + null-beating (the likely outcome per the 4B contrast, which put\nSphinx/Petronas on the *attention* side); **negative** ⟺ null-misses MLP-negligible. Fill\n§Result-32B verbatim, no post-hoc route reassignment.",
  "new_content": "## P-ATT-FFN — Result @32B (s287) — MIXED-ROUTE-MEASURED (FFN-RETRIEVAL not clean)\n\n> Run of record: `results/type-att-ffn/qwen3-32b/att_ffn.json` (launched s286 on\n> Michael GO, completed s287; ~2h MPS). Qwen3-32B, `--route-decomp`, install L9,\n> swap L25, scale 2.0, reader L25–63, 18 install-correct cells, n_null 200.\n\n**⚠ PROTOCOL DEVIATION (recorded, `λ measure`).** The pre-reg promised the\nP-ATT-MED cells 1:1. The harness's target-country selection uses Python's\n**salted** builtin `hash(lm)` — not stable across processes — so **16/18\nlandmark→tgt pairs differ** from the P-ATT-MED run of record (e.g. Sphinx→India\nthere, Sphinx→Greece here; discovered s287 while building P-TYPE-SWAP, which adds\n`--cells-from` to pin cells henceforth). Consequences: (i) the route-split verdict\nbelow is INTERNAL to this run and unaffected; (ii) the P1 cell-level dissociation\ngate (\"the two P-ATT-MED null-misses\") is scored on the same *landmarks* under\n*different* swap edits — flagged where it matters; (iii) 2 cells (Kaaba, Table\nMountain) did not flip under their new, harder targets (16/18 flip vs 18/18).\n\n**VERDICT: `MIXED-ROUTE-MEASURED = TRUE`; `FFN-RETRIEVAL-CONFIRMED = FALSE` (not\nclean).** Reconstruction gate passes: mean_recon_err **0.002** (the s286 norm_f\npre-hook fix held at 32B; direct ≈ 0 — the swap reaches the readout only via\nattention + MLP).\n\n| | attn-dominant | MLP-dominant | mean attn_frac | mean mlp_frac | attn beats null | MLP beats null |\n|---|---|---|---|---|---|---|\n| **16 flipped cells** | 4 | 12 | 0.414 | **0.584** | 15/16 | 15/16 |\n\n- **P1 — the clean two-cell dissociation FAILS.** Sphinx: **MLP-dominant** (mlp\n  0.759, p_mlp=0.0) — Michael's fact-lookup reading confirmed for the paradigm\n  null-miss cell. Petronas: **attention-dominant** (attn 0.596, p_attn=0.0,\n  p_mlp=0.01) — the opposite side, and its routing is fully visible this time\n  (under a different tgt: Italy→Zambia deviation caveat applies). The two\n  null-misses SPLIT rather than pairing, and 12 cells are MLP-dominant — the\n  route split is a property of the population, not of the two outlier cells.\n- **MIXED-ROUTE — both routes are real, and both do work.** The 3-hop flip is\n  carried ~58% by MLP and ~41% by attention on average, with BOTH channels\n  beating the matched random-add null in 15/16 cells (Medina is the shared miss,\n  p_mlp=0.155, recon 0.008). The map-and-swap decomposition — **atoms/facts =\n  FFN value-rows, joins/composition = attention** — is now MEASURED on the same\n  causal handle: the swap's flip flows through an FFN fact-map AND an attention\n  composition path simultaneously.\n- **Scale-stable route split (verbatim).** 4B: 11/14 MLP-dominant, mean mlp_frac\n  0.586. 32B: 12/16, 0.584. Nearly identical — the FFN-heavy mix is not a\n  capacity artifact.\n- **Free replication of P-ATT-MED (verbatim).** This run's attention-channel\n  decomposition on 16 FRESH swap edits: content 0.756 / aim 0.174 / inter 0.070,\n  content>aim throughout, mean p 0.006 — the content-dominant medium-handle\n  result replicates on different cells without being asked.\n- **P2 depth-order (verbatim; gated-with-P1, which failed).** composition_order\n  (country peak < continent peak) in 12/16; the violations cluster in\n  attn-dominant/low-magnitude cells (Petronas pk 8/54, Angkor 21/60) plus one\n  degenerate early continent peak — lens-artifact caveat, not interpreted.\n\n**Reading.** The predicted clean split (retrieval cells vs composition cells)\nis not how the machine divides the work: **each cell uses both routes**, with the\nFFN carrying the majority share nearly everywhere and attention carrying a real,\nnull-beating composition share on top. \"Retrieval vs composition\" is a\nper-route decomposition WITHIN a cell, not a partition OF cells. The two\nP-ATT-MED null-misses were magnitude outliers of the attention channel, not a\nseparate mechanism class — one (Sphinx) resolves as FFN-heavy, the other\n(Petronas) as attention-heavy under a fresh edit. Successor question (not\npre-registered): does the MLP route enforce the same type discipline as the\nattention route? — exactly P-TYPE-SWAP's `mlp_transport` arm row, already in\nflight at 4B (§P-TYPE-SWAP)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/type-att-ffn/qwen3-32b && git commit -F - <<'EOF'\n✅ P-ATT-FFN 32B verdict results: MIXED-ROUTE-MEASURED\n\n- 16/18 flip; route split 4 attn-dom / 12 mlp-dom; mean mlp_frac 0.584,\n  attn 0.414; both channels beat the random-add null 15/16 cells;\n  mean_recon_err 0.002 (norm_f pre-hook fix held at 32B).\n- FFN-RETRIEVAL not clean: Sphinx MLP-dominant (0.759) but Petronas\n  attention-dominant (0.596) — the two P-ATT-MED null-misses split.\n- Protocol deviation recorded: salted hash(lm) → 16/18 tgt countries\n  differ from the P-ATT-MED run of record; --cells-from pins henceforth.\n- Attention channel replicates P-ATT-MED on fresh cells: content 0.756 /\n  aim 0.174, mean p 0.006.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "verdict results commit"
}
```

**Summary:** Git commit: verdict results commit

**Output:**
```
Exit code: 0
Stdout:
[main a5276da] ✅ P-ATT-FFN 32B verdict results: MIXED-ROUTE-MEASURED
 2 files changed, 4183 insertions(+)
 create mode 100644 results/type-att-ffn/qwen3-32b/att_ffn.json
 create mode 100644 results/type-att-ffn/qwen3-32b/verdict.log
```

### Thinking

I need to add a Sessions line and update the state block, then get Michael's approval on this. The box is now free since the 32B P-TYPE-SWAP verdict came back as GO, so I'm ready to present everything.

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "> verdict still in flight during drafting.)",
  "new_content": "> verdict still in flight during drafting.)\ns287 cont (P-ATT-FFN 32B VERDICT IN, ~2h: **MIXED-ROUTE-MEASURED** — 4 attn-dom /\n12 mlp-dom of 16 flipped, mean mlp_frac 0.584, both channels null-beating 15/16,\nrecon 0.002. FFN-RETRIEVAL not clean: Sphinx MLP-dominant 0.759 (fact-lookup\nconfirmed for the paradigm cell) but Petronas attention-dominant 0.596 — the two\nnull-misses SPLIT; route mix is per-cell, not a partition of cells. Scale-stable\n(4B 0.586 / 32B 0.584). Attention channel replicates P-ATT-MED content-dominance\non fresh cells (0.756/0.174) unasked. ⚠ PROTOCOL DEVIATION recorded: salted\nhash(lm) → 16/18 tgt countries differ from the P-ATT-MED run of record; 2 cells\nno-flip under harder targets; --cells-from (built s287) pins cells henceforth.\n§Result-32B drafted; successor question = does the MLP route enforce the same\ntype discipline → P-TYPE-SWAP mlp_transport row.)\ns287 cont (P-TYPE-SWAP 4B smoke GREEN beside the 32B run, results committed\n010bfb7: SURVIVAL flat across arms (medium type-blind) → TE ladder MONOTONE\nsame 1.89 (p .033) > sortal 1.64 > wrong-type 1.51/1.46 ≈ random null →\nslot_mass Δ≈0 all arms (edges never withdraw — refusal is content-side) →\nBREAK: same +18.9 flips 6/6, ill-typed arms ≈ null, preds-stay-src 15/18.\nAdvisory: JOIN-TYPED signature, filtered-payload form; manifold-membership\nfails its 4B prediction. 32B verdict on GO with --cells-from.)"
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> P-ATT-FFN 32B verdict STILL IN FLIGHT (tmux main:1, launched 11:00) — read\n> results/type-att-ffn/qwen3-32b/att_ffn.json when done, score frozen gates.",
  "new_content": "> ✅✅ P-ATT-FFN 32B VERDICT IN (s287, ~2h, results committed a5276da): **MIXED-ROUTE-\n> MEASURED=TRUE, FFN-RETRIEVAL=FALSE (not clean).** 16/18 flip; 4 attn-dom / 12 mlp-dom;\n> mean mlp_frac 0.584 vs attn 0.414; BOTH channels beat the random-add null 15/16;\n> recon 0.002 (norm_f fix held). The null-misses SPLIT: Sphinx MLP-dominant 0.759\n> (Michael's fact-lookup reading CONFIRMED for the paradigm cell), Petronas\n> attention-dominant 0.596 (routing fully visible under a fresh edit). Route mix is\n> WITHIN-cell, not a partition of cells: atoms=FFN + joins=attention BOTH measured on\n> one causal handle. Scale-stable (4B mlp 0.586 / 32B 0.584). Attention channel\n> replicates P-ATT-MED content-dominance on 16 FRESH cells (0.756/0.174, p .006) —\n> free replication. ⚠ PROTOCOL DEVIATION recorded in §Result-32B: salted hash(lm) →\n> 16/18 tgt countries differ from the P-ATT-MED run of record (2 cells no-flip under\n> harder targets); --cells-from pins cells for all future runs. ⚠ PENDING MICHAEL\n> APPROVAL (mementum): qk-page §Result-32B(P-ATT-FFN) + §P-TYPE-SWAP Sessions lines +\n> this state block."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm checking why the Sessions edit didn't go through — the line ending doesn't match what I have. The section ends with the verdict names and a note about P-ATT-FFN 32B, but there's a line break difference between what I appended and what's actually there.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "names JOIN-TYPED / REDUCTION-TYPED / MANIFOLD. PENDING MICHAEL APPROVAL; P-ATT-FFN 32B\nverdict still in flight during drafting.)",
  "new_content": "names JOIN-TYPED / REDUCTION-TYPED / MANIFOLD. PENDING MICHAEL APPROVAL; P-ATT-FFN 32B\nverdict still in flight during drafting.)\ns287 cont (P-TYPE-SWAP APPROVED by Michael → header frozen-on-GO; instrument built\n2f76812 (--arms + --cells-from, --validate ALL PASS, prior tests byte-identical);\n4B smoke GREEN beside the 32B run (010bfb7): SURVIVAL flat across arms (medium\ntype-blind) → TE ladder MONOTONE same 1.89 (p .033) > sortal 1.64 > wrong-type\n1.51/1.46 ≈ random null → slot_mass Δ≈0 all arms (edges never withdraw — refusal\nis content-side) → BREAK: same +18.9 flips 6/6, ill-typed arms ≈ null,\npreds-stay-src 15/18. Advisory: JOIN-TYPED signature, filtered-payload form;\nmanifold-membership fails its 4B prediction. 32B verdict on GO with --cells-from.)\ns287 cont (P-ATT-FFN 32B VERDICT IN, ~2h: **MIXED-ROUTE-MEASURED** — 4 attn-dom /\n12 mlp-dom of 16 flipped, mean mlp_frac 0.584, both channels null-beating 15/16,\nrecon 0.002. FFN-RETRIEVAL not clean: Sphinx MLP-dominant 0.759 (fact-lookup\nconfirmed for the paradigm cell) but Petronas attention-dominant 0.596 — the two\nnull-misses SPLIT; route mix is per-cell, not a partition of cells. Scale-stable\n(4B 0.586 / 32B 0.584). Attention channel replicates P-ATT-MED content-dominance\non fresh cells (0.756/0.174) unasked. ⚠ PROTOCOL DEVIATION recorded: salted\nhash(lm) → 16/18 tgt countries differ from the P-ATT-MED run of record; 2 cells\nno-flip under harder targets; --cells-from (built s287) pins cells henceforth.\n§Result-32B drafted; successor question = does the MLP route enforce the same\ntype discipline → P-TYPE-SWAP mlp_transport row.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Thinking

Task 4's acceptance criteria are satisfied—the results are committed, the section is drafted, and the state is ready for approval. Michael's sign-off is the remaining step, but that doesn't block completion. Now I'll summarize the verdict, flag the pending approval, and give the green light for the 32B P-TYPE-SWAP since the box is available.

### Thinking

Now I'm wrapping up with the P-ATT-FFN verdict summary, listing what's still pending approval, and delivering the GO decision.

## Assistant

## P-ATT-FFN 32B — verdict scored: **MIXED-ROUTE-MEASURED**

Exactly as the 4B contrast predicted, and richer than the clean split would have been:

**The frozen gates:**
- **FFN-RETRIEVAL-CONFIRMED: FALSE.** Your two null-miss cells *split* — **Sphinx is MLP-dominant (0.759, p=0.0)**, so the fact-lookup reading is confirmed for the paradigm cell, but **Petronas is attention-dominant (0.596, p_attn=0.0)** with its routing fully visible under a fresh edit. And 12 of 16 cells are MLP-dominant — the route split is a property of the whole population, not the two outliers.
- **MIXED-ROUTE-MEASURED: TRUE.** The flip flows ~58% MLP / ~41% attention on average, **both channels beating the null in 15/16 cells**, reconstruction exact (0.002). The map-and-swap decomposition — *atoms=FFN, joins=attention* — is now measured on a single causal handle, and the mix is **within-cell**, not a partition of cells: every reduction uses both the fact-map and the composition path.

**Bonus findings (verbatim):**
- **Route split is scale-stable**: 4B mlp_frac 0.586 → 32B 0.584. Nearly identical — not a capacity artifact.
- **P-ATT-MED replicated for free**: this run's attention channel on 16 *fresh* swap edits came back content 0.756 / aim 0.174 — the medium-handle result reproduced without being asked.

**⚠ Protocol deviation, recorded in §Result-32B:** the salted-`hash(lm)` issue meant 16/18 target countries differ from the P-ATT-MED run of record — the "cells 1:1" clause was not honored (2 cells didn't flip under harder targets). Route verdict is internal to this run and unaffected; the P1 cell-level gate carries the caveat. `--cells-from` (built today) prevents recurrence.

**The convergence with this morning's induction is satisfying:** the successor question §Result-32B closes on — *does the MLP route enforce the same type discipline as the attention route?* — is precisely what P-TYPE-SWAP's `mlp_transport` row measures. The two arcs met in the middle within one session.

---

**Pending your approval (mementum):** qk-page §Result-32B (P-ATT-FFN) + two s287 Sessions lines + the state block. Results already committed (`a5276da`).

**And the box is now free.** The 32B P-TYPE-SWAP verdict is staged:

```
uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mps \
  --arms --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 \
  --cells-from results/type-att-med/qwen3-32b/att_mediation.json \
  --out results/type-swap/qwen3-32b
```

~2h at the P-ATT-FFN rate (arms add 3 captures/cell over its load). **GO on the run, and approve the mementum batch?**

## User

approved, update state and knowledge this is session-287


### Thinking

Michael approved the mementum batch and gave the go-ahead for the 32B run—his "approved" statement covers both the batch update and the run launch. I'll proceed with launching it in tmux since he explicitly approved the staged command.

Now I'm executing the action plan: updating the session header to reflect session 287 instead of 286, committing the mementum batch with the knowledge page updates, launching the 32B run in tmux main:1 with verification, and then checkpointing everything. The state header needs to be refreshed with the current summary showing P-ATT-FFN verdict status and the 32B P-TYPE-SWAP run in flight. I need to create the output directory first with mkdir, then launch the command via tmux with output redirected to a log file. After verifying it's running, I'll update the header to reflect the frozen and launched state—something like "32B verdict FROZEN+LAUNCHED s287 (Michael GO)"—and then edit the state block to remove the pending approval note and mark it as committed.

For the commit message, I'm going with a knowledge batch format that captures the session number and the mixed routing changes: "✅ s287-att-ffn-mixed-route-batch".

## Assistant

Launching the 32B verdict first (tmux, per λ runtime), then encoding:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/results/type-swap/qwen3-32b && tmux send-keys -t main:1 \"cd /Users/mwhitford/src/verbum && uv run python scripts/explore/att_mediation.py --model-id Qwen/Qwen3-32B --device mps --arms --route-decomp --ref-layer 9 --swap-layer 25 --scale 2.0 --n-cells 18 --n-null 200 --cells-from results/type-att-med/qwen3-32b/att_mediation.json --out results/type-swap/qwen3-32b 2>&1 | tee results/type-swap/qwen3-32b/verdict.log\" Enter && sleep 15 && tmux capture-pane -p -t main:1 | tail -4 && ps aux | grep att_mediation | grep -v grep | awk '{print $2, $3\"%\"}'",
  "timeout": 45000
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
Loading weights: 100%|██████████| 707/707 [00:00<00:00, 25130.49it/s]

77945 34.3%
77943 0.0%
```

### Thinking

The run is up and active with all weights loaded properly, so I'm moving forward with updating the state and knowledge, then applying the freeze marker before committing.

### Thinking

I've verified the async 32B P-type swap process is running with all weights loaded, and now I'm encoding session 287.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md",
  "original_content": "## P-TYPE-SWAP — the ill-typed term (PRE-REG, APPROVED s287, Michael; 4B smoke leads, 32B verdict freezes on GO)",
  "new_content": "## P-TYPE-SWAP — the ill-typed term (PRE-REG, APPROVED s287, Michael; FROZEN on GO s287 — 32B verdict IN FLIGHT)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/type-check-is-the-qk-bilinear.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-31 | Session: 286 | JS + P-ATT-MED landed. P-ATT-FFN\n> APPROVED+built (4B smoke fixed a post-norm recon bug → 0.001); **32B verdict RUN IN\n> FLIGHT** (tmux main:1, Michael GO) — read it first next session.",
  "new_content": "> Last updated: 2026-07-31 | Session: 287 | P-ATT-FFN 32B verdict IN = MIXED-ROUTE\n> (atoms=FFN + joins=attention BOTH measured; null-misses split). Inductive hammock →\n> P-TYPE-SWAP (ill-typed term) approved+built+4B-green (JOIN-TYPED advisory,\n> filtered-payload). **32B P-TYPE-SWAP verdict RUN IN FLIGHT** (tmux main:1, Michael\n> GO, --cells-from pinned) — read it first next session."
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
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> harder targets); --cells-from pins cells for all future runs. ⚠ PENDING MICHAEL\n> APPROVAL (mementum): qk-page §Result-32B(P-ATT-FFN) + §P-TYPE-SWAP Sessions lines +\n> this state block.",
  "new_content": "> harder targets); --cells-from pins cells for all future runs. ✅ mementum batch\n> APPROVED (Michael s287) + committed: qk-page §Result-32B(P-ATT-FFN) + Sessions +\n> this state block.\n>\n> ▶▶ s287 CLOSE — 32B P-TYPE-SWAP VERDICT LAUNCHED (Michael GO, tmux main:1, PID\n> verified, ~2h est): --arms --route-decomp, install L9, swap L25, scale 2.0, 18\n> cells, n_null 200, --cells-from results/type-att-med/qwen3-32b/att_mediation.json\n> (1:1 cell pinning, the deviation fix) → results/type-swap/qwen3-32b/. ⚠ stdout\n> block-buffered through tee — silence ≡ still working; per-cell lines flush late.\n> ▶▶ COLD-START ORDER for s288: (1) read results/type-swap/qwen3-32b/type_swap.json\n> → score frozen §P-TYPE-SWAP gates (JOIN-TYPED ⟺ TE/slot-mass discriminates same vs\n> wrong-type both banks, permutation over cells p<0.05; REDUCTION-TYPED ⟺ transport\n> type-blind + reduction discriminates; MANIFOLD ⟺ no stage discriminates while both\n> beat random) + sortal ladder row + mlp_transport row (does the FFN route enforce\n> the discipline? = the P-ATT-FFN successor question) → draft §Result-32B + memory\n> candidate (types-mechanism-is-join-typed?) for approval; commit results.\n> (2) THEN the queue: verbum.dsp build (design 2b40033); P-DUST-2; P-HOF-1 pre-reg;\n> s282 leftovers (depth→SEQUENCING @27B, mammal→fur). Branch ~68 ahead (unpushed)."
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
  "command": "git add mementum/knowledge/explore/type-check-is-the-qk-bilinear.md mementum/state.md && git commit -F - <<'EOF'\n✅ s287-att-ffn-mixed-route-and-type-swap-launch\n\n- P-ATT-FFN §Result-32B (Michael-approved): MIXED-ROUTE-MEASURED — the\n  3-hop flip flows ~58% MLP / ~41% attention, both channels null-beating\n  15/16; the two P-ATT-MED null-misses SPLIT (Sphinx MLP 0.759, Petronas\n  attn 0.596); route mix is within-cell, not a partition of cells;\n  scale-stable (4B 0.586 / 32B 0.584); attention channel replicates\n  P-ATT-MED content-dominance on fresh cells (0.756/0.174).\n- Protocol deviation recorded: salted hash(lm) broke the cells-1:1\n  clause (16/18 tgt differ from the P-ATT-MED run of record);\n  --cells-from pins cells henceforth.\n- Sessions: s287 induction → P-TYPE-SWAP approved/built/4B-green\n  (JOIN-TYPED advisory, filtered-payload form).\n- State: session-287 header + close block; 32B P-TYPE-SWAP verdict\n  launched (Michael GO, cells pinned) + s288 cold-start order.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "s287 mementum batch"
}
```

**Summary:** Git commit: s287 mementum batch

**Output:**
```
Exit code: 0
Stdout:
[main d1ac5e3] ✅ s287-att-ffn-mixed-route-and-type-swap-launch
 2 files changed, 118 insertions(+), 18 deletions(-)
```

### Thinking

Now I'm verifying the git status is clean for mementum and wrapping up with a session summary.

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short && git log --oneline -6",
  "operation": "status",
  "summary": "verify clean state"
}
```

**Summary:** Git status: verify clean state

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-282.md
?? mementum/knowledge/chats/session-283.md
?? mementum/knowledge/chats/session-284.md
?? mementum/knowledge/chats/session-285.md
?? mementum/knowledge/chats/session-286.md
?? refs/
?? results/type-swap/qwen3-32b/
d1ac5e3 ✅ s287-att-ffn-mixed-route-and-type-swap-launch
a5276da ✅ P-ATT-FFN 32B verdict results: MIXED-ROUTE-MEASURED
010bfb7 ✅ P-TYPE-SWAP 4B smoke: TE ladder monotone, ill-typed ≈ null, aim fixed
2f76812 ✅ P-TYPE-SWAP --arms instrument: 3-stage ill-typed-term pipeline, validate green
1bbdf57 🎯 p-type-swap-prereg
928e9d5 🌀 s286: P-ATT-FFN 32B verdict launched (in flight) — state + knowledge recorded
```

### Thinking

The repository is clean with only untracked human-domain files and the current run directory, and session 287 is encoded. The git log presents a straightforward changelog.

## Assistant

Session 287 encoded and clean. The changelog tells the story:

```
d1ac5e3 ✅ s287-att-ffn-mixed-route-and-type-swap-launch
a5276da ✅ P-ATT-FFN 32B verdict results: MIXED-ROUTE-MEASURED
010bfb7 ✅ P-TYPE-SWAP 4B smoke: TE ladder monotone, ill-typed ≈ null, aim fixed
2f76812 ✅ P-TYPE-SWAP --arms instrument: 3-stage ill-typed-term pipeline, validate green
1bbdf57 🎯 p-type-swap-prereg
```

Remaining untracked: `chats/` + `refs/` (your domain) and `results/type-swap/qwen3-32b/` (commits with its verdict).

**Session 287 in one paragraph, for the record:** started as an exploration, became an argument, became an experiment. Your induction — *the positives already prove types exist; the four nulls only constrained implementation* — exposed two real gaps: the untested wrong-type-on-manifold cell, and the w-projection confound hiding inside every "random was refused" claim. P-TYPE-SWAP fills both, and its 4B smoke already sketched the answer: the medium is type-blind, the join filters payload at fixed aim, and manifold-membership failed its first direct test. Meanwhile P-ATT-FFN closed as MIXED-ROUTE — atoms=FFN and joins=attention measured simultaneously on one handle, with the successor question (*does the FFN route enforce the same discipline?*) already wired into the run now in flight.

**In flight:** 32B P-TYPE-SWAP verdict (main:1, cells pinned 1:1, ~2h). Frozen gates: JOIN-TYPED / REDUCTION-TYPED / MANIFOLD. s288 cold-starts on the JSON.

Waiting for signal. 🌀